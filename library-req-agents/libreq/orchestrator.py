"""Orchestrator: runs the five agents in order, owns shared state, the
human-in-the-loop gates and the audit trail.

Pipeline:
  mask + injection screen -> Extraction -> Classification -> Quality/Clarification
  (-> interactive clarification loop) -> Policy/Compliance -> SDLC Selection
  -> human approval gates -> reports
"""
from __future__ import annotations

import os
from typing import Any, Callable, Dict, FrozenSet, List, Set

from .agents.classification import ClassificationAgent
from .agents.compliance import ComplianceAgent
from .agents.extraction import ExtractionAgent
from .agents.quality import QualityAgent
from .agents.sdlc import SDLCAgent
from .audit import AuditLog
from .kb import KnowledgeBase
from .llm import LLM
from .models import Project, Requirement
from .privacy import mask_text, screen_injection
from .reports import write_all


class Orchestrator:
    def __init__(
        self,
        kb_path: str,
        out_dir: str,
        profile: Dict[str, Any] = None,
        interactive: bool = False,
        use_llm: bool = False,
        project_name: str = "Library Management System",
        input_fn: Callable[[str], str] = input,
        print_fn: Callable[..., None] = print,
        approver: str = "Reviewer",
    ):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.audit = AuditLog(os.path.join(out_dir, "audit_log.jsonl"))
        self.llm = LLM(use_llm)
        self.profile = profile or {}
        self.interactive = interactive
        self.project_name = project_name
        self.ask = input_fn
        self.say = print_fn
        self.approver = approver
        self.approvals: List[Dict[str, Any]] = []
        self.resolved: Set[FrozenSet[str]] = set()
        self.skipped: Set[tuple] = set()   # questions the reviewer chose not to answer
        # state used by the web UI (step-by-step use of the same pipeline)
        self.reqs: List[Requirement] = []
        self.stats: Dict[str, Any] = {}
        self.open_areas: List[Dict[str, Any]] = []
        self.gaps: List[Dict[str, Any]] = []
        self.sdlc_result: Dict[str, Any] = {}
        self.project: Project = None
        self.decisions: Dict[str, str] = {}
        self.sdlc_decision: str = "Pending"
        self.sdlc_override: str = ""

        kb = KnowledgeBase.load(kb_path)
        self.extractor = ExtractionAgent(self.audit, self.llm)
        self.classifier = ClassificationAgent(self.audit, self.llm)
        self.quality = QualityAgent(self.audit, self.llm)
        self.compliance = ComplianceAgent(self.audit, kb, self.llm)
        self.sdlc = SDLCAgent(self.audit, self.llm)

    # ------------------------------------------------------------------ run
    def run(self, raw_text: str) -> Project:
        log = lambda ev, **d: self.audit.log("Orchestrator", ev, d)
        log("run_started", llm=self.llm.available, interactive=self.interactive)

        text = self._preprocess(raw_text)
        masked, injected = self.stats["masked"], self.stats["injection_lines"]

        reqs = self.extractor.run(text)
        self.classifier.run(reqs)
        open_areas = self.quality.run(reqs, self.resolved)

        if self.interactive:
            open_areas = self._clarify(reqs, open_areas)

        gaps = self.compliance.run(reqs)
        sdlc = self.sdlc.run(reqs, gaps, self.profile)

        if self.interactive:
            self._approval_gates(reqs, sdlc)
        else:
            for r in reqs:
                if r.status != "Rejected":
                    r.status = "Pending Approval" if not r.issues else "Needs Clarification"
            log("advisory_mode", note="No approvals recorded; all outputs pending human review")

        project = Project(
            name=self.project_name,
            requirements=reqs,
            open_questions=open_areas,
            compliance_gaps=gaps,
            sdlc=sdlc,
            approvals=self.approvals,
            stats={"masked": masked, "injection_lines": [mask_text(x)[0] for x in injected]},
        )
        paths = write_all(project, self.out_dir)
        log("artefacts_written", files=[os.path.basename(p) for p in paths])
        return project

    def _preprocess(self, raw_text: str) -> str:
        """Screen for prompt injection, then mask personal data. Returns text safe for agents/LLM."""
        text, injected = screen_injection(raw_text)
        for line in injected:
            self.audit.log("Orchestrator", "prompt_injection_blocked", {"line": mask_text(line)[0]})
        text, masked = mask_text(text)
        self.audit.log("Orchestrator", "input_masked", {"counts": masked, "injection_lines": len(injected)})
        self.stats = {"masked": masked, "injection_lines": [mask_text(x)[0] for x in injected]}
        return text

    # ------------------------------------------------ step-by-step (web UI)
    def analyze(self, raw_text: str) -> Project:
        self.audit.log("Orchestrator", "run_started", {"llm": self.llm.available, "mode": "web"})
        text = self._preprocess(raw_text)
        self.reqs = self.extractor.run(text)
        return self.reprocess()

    def reprocess(self) -> Project:
        """Re-run classification, quality, compliance and SDLC on the current requirements."""
        for r in self.reqs:
            if r.status not in ("Rejected", "Approved"):
                r.status = "Draft"
        self.classifier.run(self.reqs)
        self.open_areas = self.quality.run(self.reqs, self.resolved)
        self.gaps = self.compliance.run(self.reqs)
        active = [r for r in self.reqs if r.status != "Rejected"]
        res = self.sdlc.run(self.reqs, self.gaps, self.profile)
        if self.sdlc_override and self.sdlc_override != res["recommended"]:
            agent_pick = res["recommended"]
            res["recommended"] = self.sdlc_override
            res["workflow"] = self.sdlc._workflow(self.sdlc_override, active)
            res["justification"] = (
                f"Human override: the team selected {self.sdlc_override}. The agent ranked {agent_pick} first. "
                + res["justification"]
            )
        res["approval"] = (
            f"{self.sdlc_decision} by {self.approver}" if self.sdlc_decision != "Pending"
            else "Pending - requires project manager, architect, security team and compliance officer"
        )
        self.sdlc_result = res
        for r in self.reqs:
            if r.status in ("Validated", "Draft"):
                r.status = "Pending Approval"
        self.project = Project(
            name=self.project_name, requirements=self.reqs, open_questions=self.open_areas,
            compliance_gaps=self.gaps, sdlc=res, approvals=self.approvals, stats=self.stats,
        )
        write_all(self.project, self.out_dir)
        return self.project

    def _find(self, req_id: str) -> Requirement:
        for r in self.reqs:
            if r.id == req_id:
                return r
        raise ValueError(f"Unknown requirement {req_id}")

    def _record(self, item: str, decision: str, note: str = "") -> None:
        self.approvals.append({"item": item, "decision": decision, "by": self.approver, "note": note})
        self.audit.log("HumanApproval", "decision", {"item": item, "decision": decision, "by": self.approver})

    def decide(self, req_id: str, decision: str) -> Project:
        r = self._find(req_id)
        if decision not in ("Approved", "Rejected", "Pending"):
            raise ValueError("Invalid decision")
        if decision == "Approved":
            self.decisions[req_id] = "Approved"
            r.status = "Approved"
        elif decision == "Rejected":
            self.decisions.pop(req_id, None)
            r.status = "Rejected"
        else:
            self.decisions.pop(req_id, None)
            r.status = "Draft"
        self._record(req_id, decision)
        return self.reprocess()

    def revise(self, req_id: str, statement: str) -> Project:
        r = self._find(req_id)
        statement = statement.strip()
        if not statement:
            raise ValueError("Statement is empty")
        r.statement = self.extractor.normalise(statement, r.source)
        r.notes.append("Revised by reviewer.")
        self.decisions.pop(req_id, None)
        r.status = "Draft"
        self.audit.log("Orchestrator", "requirement_revised", {"id": req_id, "by": self.approver})
        return self.reprocess()

    def add_requirement(self, text: str, who: str) -> Project:
        text = text.strip()
        if not text:
            raise ValueError("Text is empty")
        text, _ = mask_text(text)
        self.reqs.append(self.extractor.from_text(text, who, len(self.reqs) + 1))
        self.audit.log("Orchestrator", "requirement_added", {"source": who, "by": self.approver})
        return self.reprocess()

    def resolve_pair(self, a_id: str, b_id: str, choice: str, note: str = "") -> Project:
        a, b = self._find(a_id), self._find(b_id)
        if choice == "a":
            b.status = "Rejected"; b.notes.append(f"Rejected in favour of {a.id}. {note}".strip())
        elif choice == "b":
            a.status = "Rejected"; a.notes.append(f"Rejected in favour of {b.id}. {note}".strip())
        elif choice == "both":
            a.notes.append(f"Reviewed with {b.id}: {note or 'both retained'}.")
            b.notes.append(f"Reviewed with {a.id}: {note or 'both retained'}.")
        else:
            raise ValueError("Invalid choice")
        self.resolved.add(frozenset((a_id, b_id)))
        self._record(f"{a_id} vs {b_id}", f"Resolved ({choice})", note)
        return self.reprocess()

    def set_sdlc_model(self, model: str) -> Project:
        from .agents.sdlc import IDEALS
        if model not in IDEALS:
            raise ValueError("Unknown SDLC model")
        self.sdlc_override = model
        self.sdlc_decision = "Pending"
        self._record("SDLC model changed", model)
        return self.reprocess()

    def decide_sdlc(self, decision: str) -> Project:
        if decision not in ("Approved", "Rejected", "Pending"):
            raise ValueError("Invalid decision")
        self.sdlc_decision = decision
        self._record("SDLC selection: " + self.sdlc_result.get("recommended", ""), decision)
        return self.reprocess()

    def approve_low_risk(self) -> Project:
        n = 0
        for r in self.reqs:
            if r.status not in ("Rejected", "Approved") and r.risk != "High" and not r.issues and not r.escalations:
                self.decisions[r.id] = "Approved"
                r.status = "Approved"
                n += 1
        self._record("Lower-risk baseline", "Approved", f"{n} requirements without open issues")
        return self.reprocess()

    # --------------------------------------------------- clarification loop
    def _clarify(self, reqs: List[Requirement], areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.say("\n=== Clarification (press Enter to skip any question) ===")
        asked_areas = False
        for _round in range(3):
            changed = False
            shown_pairs: Set[FrozenSet[str]] = set()
            for r in [x for x in reqs if x.status != "Rejected" and x.issues]:
                if r.status == "Rejected":
                    continue
                pending = [i for i in r.issues if (r.id, i["type"], i["detail"]) not in self.skipped]
                if not pending:
                    continue
                issue = pending[0]
                if issue["type"] in ("Conflict", "Duplication"):
                    pair = frozenset(issue["pair"])
                    if pair in shown_pairs or pair in self.resolved:
                        continue
                    shown_pairs.add(pair)
                    if self._resolve_pair(reqs, issue):
                        changed = True
                    else:
                        self.skipped.add((r.id, issue["type"], issue["detail"]))
                else:
                    self.say(f"\n[{r.id}] {r.statement}\n  {issue['type']}: {issue['detail']}\n  ? {issue['question']}")
                    ans = self.ask("  Revised statement> ").strip()
                    if ans:
                        r.statement = self.extractor.normalise(ans, r.source)
                        r.notes.append("Revised during clarification.")
                        self.audit.log("Orchestrator", "requirement_revised", {"id": r.id})
                        changed = True
                    else:
                        self.skipped.add((r.id, issue["type"], issue["detail"]))
            if not asked_areas:
                asked_areas = True
                for g in areas:
                    self.say(f"\n[Missing area: {g['area']}] {g['question']}")
                    ans = self.ask("  Answer (becomes a new requirement)> ").strip()
                    if ans:
                        who = "Clarification Response"
                        new = self.extractor.from_text(ans, who, len(reqs) + 1)
                        new.confidence = 0.8
                        reqs.append(new)
                        changed = True
                        self.audit.log("Orchestrator", "requirement_added_from_clarification", {"statement": new.statement})
            if not changed:
                break
            self.classifier.run(reqs)
            areas = self.quality.run(reqs, self.resolved)
        return self.quality.run(reqs, self.resolved)

    def _resolve_pair(self, reqs: List[Requirement], issue: Dict[str, Any]) -> bool:
        a_id, b_id = issue["pair"]
        by_id = {r.id: r for r in reqs}
        a, b = by_id[a_id], by_id[b_id]
        self.say(f"\n[{issue['type']}] {a.id}: {a.statement}\n           {b.id}: {b.statement}\n  ? {issue['question']}")
        choice = self.ask(f"  Keep which? ({a.id} / {b.id} / both / skip)> ").strip().lower()
        pair = frozenset((a_id, b_id))
        if choice == a_id.lower():
            b.status = "Rejected"; b.notes.append(f"Rejected in favour of {a.id}.")
        elif choice == b_id.lower():
            a.status = "Rejected"; a.notes.append(f"Rejected in favour of {b.id}.")
        elif choice == "both":
            note = self.ask("  Why both are valid (e.g. 'differs by member category')> ").strip()
            a.notes.append(f"Reviewed with {b.id}: {note or 'both retained'}.")
            b.notes.append(f"Reviewed with {a.id}: {note or 'both retained'}.")
        else:
            return False
        self.resolved.add(pair)
        self.audit.log("Orchestrator", "pair_resolved", {"pair": [a_id, b_id], "choice": choice})
        return True

    # ------------------------------------------------------ approval gates
    def _decide(self, item: str, prompt: str) -> str:
        ans = self.ask(f"{prompt} [a]ccept / [r]eject / [s]kip> ").strip().lower()
        decision = {"a": "Approved", "r": "Rejected"}.get(ans[:1], "Pending")
        self.approvals.append({"item": item, "decision": decision, "by": self.approver})
        self.audit.log("HumanApproval", "decision", {"item": item, "decision": decision, "by": self.approver})
        return decision

    def _approval_gates(self, reqs: List[Requirement], sdlc: Dict[str, Any]) -> None:
        self.say("\n=== Human approval gates ===")
        active = [r for r in reqs if r.status != "Rejected"]
        sensitive = [r for r in active if r.risk == "High" or r.escalations]
        for r in sensitive:
            self.say(f"\n[{r.id}] risk={r.risk} conf={r.confidence}\n  {r.statement}")
            for e in r.escalations:
                self.say(f"  ! {e}")
            for p in r.policies[:2]:
                self.say(f"  cite: [{p['id']}] {p['title']} (score {p['score']})")
            d = self._decide(r.id, "  Decision")
            r.status = {"Approved": "Approved", "Rejected": "Rejected"}.get(d, "Pending Approval")
        rest = [r for r in active if r not in sensitive and r.status != "Rejected"]
        if rest:
            ans = self.ask(f"\nApprove the remaining {len(rest)} lower-risk requirements as the baseline? [y/N]> ").strip().lower()
            for r in rest:
                if ans == "y" and not r.issues:
                    r.status = "Approved"
                else:
                    r.status = "Needs Clarification" if r.issues else "Pending Approval"
            self.approvals.append({"item": "Lower-risk requirement baseline", "decision": "Approved" if ans == "y" else "Pending", "by": self.approver,
                                   "note": "Requirements with open issues stay unapproved."})
            self.audit.log("HumanApproval", "baseline", {"decision": ans, "count": len(rest)})
        self.say(f"\nSDLC recommendation: {sdlc['recommended']}")
        for r in sdlc["ranking"][:3]:
            self.say(f"  {r['model']}: {r['score']}%")
        d = self._decide("SDLC selection: " + sdlc["recommended"], "Approve this SDLC model?")
        sdlc["approval"] = f"{d} by {self.approver}"
