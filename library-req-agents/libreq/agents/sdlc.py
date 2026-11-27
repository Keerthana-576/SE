"""Agent 5 - SDLC Selection Agent.

Hybrid engine: (1) derive decision factors from the analysed requirements and a
project profile, (2) score every SDLC model by weighted similarity to its ideal
factor profile, (3) apply deterministic rules from the selection table,
(4) return a ranked list and a project-specific workflow, (5) explain the choice
(offline template, or Claude when available).

Scores are heuristic suitability scores, not probabilities.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..kb import kw_match
from ..models import Requirement
from .base import Agent

FACTORS = [
    "volatility", "regulatory", "security", "uncertainty", "integration",
    "continuous_delivery", "stakeholder_availability", "verification",
]
WEIGHTS = [1.0, 1.2, 1.0, 1.0, 0.8, 0.8, 0.6, 1.0]

IDEALS: Dict[str, List[float]] = {
    "Waterfall":              [0.10, 0.60, 0.50, 0.10, 0.40, 0.10, 0.40, 0.60],
    "V-Model":                [0.20, 0.90, 0.80, 0.20, 0.80, 0.20, 0.50, 0.95],
    "Spiral":                 [0.60, 0.60, 0.70, 0.95, 0.60, 0.30, 0.70, 0.50],
    "Agile":                  [0.90, 0.20, 0.30, 0.60, 0.30, 0.60, 0.90, 0.20],
    "DevSecOps":              [0.70, 0.60, 0.90, 0.40, 0.50, 0.95, 0.60, 0.50],
    "Agile-V-Model hybrid":   [0.60, 0.85, 0.70, 0.50, 0.70, 0.40, 0.70, 0.80],
    "Agile-DevSecOps hybrid": [0.80, 0.60, 0.85, 0.50, 0.50, 0.85, 0.80, 0.50],
}

DEFAULT_PROFILE = {
    "requirement_stability": None,      # 0..1, None = estimate from analysis
    "stakeholder_availability": 0.6,    # 0..1
    "needs_formal_verification": None,  # 0..1, None = estimate
    "extensive_approvals": False,
    "continuous_delivery_need": None,   # 0..1, None = estimate
}

ONLINE = ["online", "remote", "portal", "24x7", "24/7", "mobile", "web", "self-service", "self service"]


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def _ph(name, activities, roles, deliverables, security, compliance, gate):
    return {
        "phase": name, "activities": activities, "roles": roles, "deliverables": deliverables,
        "security": security, "compliance": compliance, "gate": gate,
    }


BASE_PHASES: Dict[str, List[Dict[str, Any]]] = {
    "Waterfall": [
        _ph("Requirements and Policy Baseline", ["Finalise SRS", "Review compliance matrix"], ["Business Analyst", "Head Librarian", "Compliance Officer"], ["Approved SRS", "Compliance matrix"], ["Data classification"], ["Policy mapping reviewed"], "Requirements baseline approval"),
        _ph("System Design", ["Architecture and database design", "Interface design"], ["Architect"], ["Design document"], ["Threat modelling"], ["Privacy impact assessment"], "Design review"),
        _ph("Implementation", ["Coding", "Code review"], ["Developers"], ["Source code", "Unit tests"], ["Static analysis"], ["Requirement-ID traceability in commits"], "Code complete"),
        _ph("Verification and Testing", ["System and integration testing", "Security testing"], ["QA", "Security"], ["Test reports"], ["Penetration test"], ["Test evidence mapped to requirements"], "Test exit approval"),
        _ph("Deployment and Maintenance", ["Release", "Training", "Support"], ["IT Operations", "Librarians"], ["Release notes", "User manual"], ["Hardening"], ["Compliance sign-off"], "Production-readiness approval"),
    ],
    "V-Model": [
        _ph("Requirements and Acceptance Test Planning", ["Baseline requirements", "Write acceptance tests per requirement"], ["Business Analyst", "QA"], ["SRS", "Acceptance test plan"], ["Data classification"], ["Policy mapping reviewed"], "Requirements baseline approval"),
        _ph("System Design and System Test Planning", ["Architecture", "System test design"], ["Architect", "QA"], ["Design", "System test plan"], ["Threat modelling"], ["Privacy impact assessment"], "Design review"),
        _ph("Module Design and Implementation", ["Detailed design", "Coding", "Unit tests"], ["Developers"], ["Code", "Unit test results"], ["Static analysis"], ["Traceability to requirement IDs"], "Code review gate"),
        _ph("Integration and System Verification", ["Integration test", "System test", "Interface conformance"], ["QA", "Integrator"], ["Verification reports"], ["Security testing"], ["Evidence mapped to controls"], "Verification gate"),
        _ph("Acceptance and Release", ["User acceptance testing", "Deployment"], ["Librarians", "Compliance Officer"], ["UAT sign-off"], ["Hardening"], ["Compliance sign-off"], "Production-readiness approval"),
    ],
    "Spiral": [
        _ph("Objectives, Alternatives and Constraints", ["Define goals for this loop", "List options and constraints"], ["Product Owner", "Architect"], ["Loop objectives"], [], ["Policy constraints listed"], "Loop plan approval"),
        _ph("Risk Analysis and Prototyping", ["Risk assessment", "Build prototype of riskiest part"], ["Architect", "Security"], ["Risk register", "Prototype"], ["Threat modelling"], ["Privacy impact check"], "Risk review"),
        _ph("Development and Testing", ["Build and test the increment"], ["Developers", "QA"], ["Increment", "Test results"], ["Static analysis"], ["Traceability update"], "Increment review"),
        _ph("Evaluation and Next-Loop Planning", ["Stakeholder review", "Plan next loop"], ["Stakeholders", "Project Manager"], ["Review notes", "Updated plan"], [], ["Compliance review of changes"], "Go / no-go for next loop"),
    ],
    "Agile": [
        _ph("Backlog Creation", ["Create and prioritise backlog"], ["Product Owner", "Business Analyst"], ["Product backlog"], ["Data classification"], ["Policy tags on stories"], "Backlog approval"),
        _ph("Sprint Planning", ["Refine stories", "Select sprint scope"], ["Product Owner", "Scrum Master", "Developers"], ["Sprint backlog"], [], ["Story-level policy check"], "Sprint scope accepted"),
        _ph("Sprint Development and Testing", ["Build", "Test", "Demo"], ["Developers", "QA"], ["Working increment"], ["Dependency scan"], ["Traceability to story IDs"], "Definition of done"),
        _ph("Review, Retrospective and Release", ["Sprint review", "Retrospective", "Release"], ["Whole team", "Librarians"], ["Release", "Retro actions"], [], ["Compliance check before release"], "Release approval"),
    ],
    "DevSecOps": [
        _ph("Plan and Threat Model", ["Backlog", "Threat modelling"], ["Product Owner", "Security"], ["Backlog", "Threat model"], ["Threat modelling"], ["Policy tags"], "Plan approval"),
        _ph("Build with Security Gates", ["Code", "CI build", "SAST, SCA, secrets scan"], ["Developers", "DevOps"], ["Pipeline reports"], ["SAST", "Dependency scan", "Secrets scan"], ["Commit-to-requirement traceability"], "Pipeline gate"),
        _ph("Test and Verify", ["Automated tests", "DAST", "Accessibility tests"], ["QA", "Security"], ["Test reports"], ["DAST"], ["Evidence automatically attached"], "Quality gate"),
        _ph("Release and Operate", ["Continuous deployment", "Monitoring", "Audit-log review"], ["DevOps", "IT Operations"], ["Release record", "Dashboards"], ["Runtime monitoring"], ["Compliance approval for each release"], "Production-readiness approval"),
    ],
    "Agile-V-Model hybrid": [
        _ph("Baseline Requirements and Acceptance Tests", ["Baseline high-risk and regulated requirements", "Write acceptance tests"], ["Business Analyst", "Compliance Officer", "QA"], ["Baselined SRS", "Acceptance test plan"], ["Data classification"], ["Policy mapping approved"], "Requirements baseline approval"),
        _ph("Iteration Planning", ["Refine backlog", "Select iteration scope"], ["Product Owner", "Developers"], ["Iteration backlog"], [], ["Story-level policy tags"], "Iteration scope accepted"),
        _ph("Iterative Design and Build", ["Design per epic", "Build and unit test"], ["Architect", "Developers"], ["Increment"], ["Threat modelling", "Static analysis"], ["Privacy impact assessment for personal-data epics"], "Design review"),
        _ph("Integration and System Verification (V-leg)", ["Integration test", "System test", "Interface conformance"], ["QA", "Integrator"], ["Verification reports"], ["Security testing"], ["Evidence mapped to controls"], "Verification gate"),
        _ph("Acceptance and Release", ["UAT", "Compliance review", "Release"], ["Librarians", "Compliance Officer"], ["UAT sign-off"], ["Hardening"], ["Compliance sign-off"], "Production-readiness approval"),
    ],
    "Agile-DevSecOps hybrid": [
        _ph("Inception and Compliance Baseline", ["Confirm scope", "Approve high-risk requirements and policy mapping", "Define definition of done incl. security and accessibility"], ["Product Owner (Head Librarian)", "Business Analyst", "Compliance Officer", "Security"], ["Product backlog", "Compliance-control matrix", "Risk register"], ["Data classification"], ["Baseline approval"], "Backlog and policy baseline approval"),
        _ph("Sprint Planning and Refinement", ["Refine stories with acceptance criteria", "Resolve open clarification questions"], ["Product Owner", "Scrum Master", "Developers"], ["Sprint backlog"], [], ["Story-level policy tags"], "Sprint scope accepted"),
        _ph("Secure Design and Threat Modelling", ["Design per epic", "STRIDE threat model", "API design"], ["Architect", "Security"], ["Threat model", "Design notes"], ["Threat modelling"], ["Privacy impact assessment"], "Architect and Security approval for high-risk stories"),
        _ph("Build with CI Security Gates", ["Code and review", "CI build", "SAST, dependency and secrets scans"], ["Developers", "DevOps"], ["Tested increment", "Pipeline reports"], ["SAST", "Dependency scan", "Secrets scan"], ["Commit-to-requirement traceability"], "Pipeline gate"),
        _ph("Verify", ["Automated unit and integration tests", "DAST", "Accessibility and interface tests"], ["QA", "Security"], ["Test reports"], ["DAST"], ["Evidence mapped to controls"], "Definition of done"),
        _ph("Compliance Gate and Release", ["Compliance review of evidence", "UAT by librarians", "Release"], ["Compliance Officer", "Librarians", "DevOps"], ["Signed release checklist"], ["Hardening"], ["Compliance sign-off"], "Compliance and production-readiness approval"),
        _ph("Operate and Improve", ["Monitoring", "Audit-log review", "Retrospective"], ["IT Operations", "Whole team"], ["Dashboards", "Retro actions"], ["Runtime monitoring"], ["Periodic access review"], "None (continuous)"),
    ],
}


class SDLCAgent(Agent):
    name = "SDLCSelectionAgent"

    def run(self, reqs: List[Requirement], gaps: List[Dict[str, Any]], profile: Dict[str, Any] = None) -> Dict[str, Any]:
        active = [r for r in reqs if r.status != "Rejected"]
        prof = {**DEFAULT_PROFILE, **(profile or {})}
        factors = self._factors(active, gaps, prof)
        ranking = self._rank(factors, prof)
        top = ranking[0]["model"]
        workflow = self._workflow(top, active)
        result = {
            "factors": factors,
            "ranking": ranking,
            "recommended": top,
            "justification": self._explain(top, ranking, factors),
            "workflow": workflow,
            "approval": "Pending - requires project manager, architect, security team and compliance officer",
        }
        self.log("sdlc_recommended", recommended=top, ranking=[(r["model"], r["score"]) for r in ranking])
        return result

    # -- factors ----------------------------------------------------------------
    @staticmethod
    def _factors(active: List[Requirement], gaps: List[Dict[str, Any]], prof: Dict[str, Any]) -> Dict[str, float]:
        n = max(1, len(active))
        reg = sum(1 for r in active if r.policies or {"Regulatory", "Privacy", "Copyright/Licence"} & set(r.categories)) / n
        sec = sum(1 for r in active if r.risk == "High") / n
        integ = sum(1 for r in active if "Integration" in r.categories) / n
        issues = sum(len(r.issues) for r in active) / n
        conflicts = sum(1 for r in active for i in r.issues if i["type"] == "Conflict") / 2
        # Wording problems are fixed by clarification, so they count only partly as project uncertainty.
        uncertainty = _clamp(0.35 * issues + 0.05 * conflicts + 0.01 * len(gaps))
        online = sum(1 for r in active if any(kw_match(k, r.statement) for k in ONLINE)) / n

        stability = prof["requirement_stability"]
        volatility = _clamp(1 - stability) if stability is not None else _clamp(0.3 + 0.5 * uncertainty)
        verification = prof["needs_formal_verification"]
        if verification is None:
            verification = max(_clamp(reg * 1.5), _clamp(integ * 2.5) * 0.8, _clamp(sec * 1.5))
        cd = prof["continuous_delivery_need"]
        if cd is None:
            cd = _clamp(online * 2)
        factors = {
            "volatility": volatility,
            "regulatory": _clamp(reg * 1.5 + 0.01 * len(gaps)),
            "security": _clamp(sec * 1.5),
            "uncertainty": uncertainty,
            "integration": _clamp(integ * 2.5),
            "continuous_delivery": _clamp(cd),
            "stakeholder_availability": _clamp(prof["stakeholder_availability"]),
            "verification": _clamp(verification),
        }
        return {k: round(v, 2) for k, v in factors.items()}

    # -- ranking ----------------------------------------------------------------
    @staticmethod
    def _rank(f: Dict[str, float], prof: Dict[str, Any]) -> List[Dict[str, Any]]:
        x = [f[k] for k in FACTORS]
        total_w = sum(WEIGHTS)
        scores: Dict[str, float] = {}
        for model, ideal in IDEALS.items():
            dist = sum(w * abs(a - b) for w, a, b in zip(WEIGHTS, x, ideal)) / total_w
            scores[model] = 1 - dist
        rules: List[str] = []

        def boost(models, amount, why):
            for m in models:
                scores[m] += amount
            rules.append(why)

        if f["volatility"] >= 0.7 and f["regulatory"] >= 0.6:
            boost(["Agile-V-Model hybrid", "Agile-DevSecOps hybrid"], 0.05, "High regulation with evolving requirements -> hybrid models")
        if f["verification"] >= 0.8:
            boost(["V-Model", "Agile-V-Model hybrid"], 0.05, "Strict verification needed -> V-Model family")
        if f["uncertainty"] >= 0.75:
            boost(["Spiral"], 0.05, "High uncertainty -> Spiral")
        if f["volatility"] <= 0.25 and prof.get("extensive_approvals"):
            boost(["Waterfall"], 0.05, "Stable requirements with extensive approvals -> Waterfall")
        if f["continuous_delivery"] >= 0.8:
            boost(["DevSecOps", "Agile-DevSecOps hybrid"], 0.05, "Continuous secure deployment -> DevSecOps family")
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        return [
            {"model": m, "score": round(100 * max(0.0, min(1.0, s)) ** 2), "rules_applied": rules}
            for m, s in ranked
        ]

    # -- workflow ---------------------------------------------------------------
    @staticmethod
    def _workflow(model: str, active: List[Requirement]) -> List[Dict[str, Any]]:
        cats = {c for r in active for c in r.categories}
        extras = {"design": [], "verify": [], "release": []}
        if "Privacy" in cats:
            extras["design"].append("Privacy impact assessment (DPDP Act)")
            extras["release"].append("Data-retention and deletion schedule verified")
        if "Security" in cats:
            extras["design"].append("Role and permission matrix reviewed")
        if "Integration" in cats:
            extras["verify"].append("Interface conformance tests (SIP2 / NCIP / OAI-PMH / SSO)")
        if "Accessibility" in cats or "Usability" in cats:
            extras["verify"].append("WCAG 2.1 AA audit with screen reader")
        if "Copyright/Licence" in cats:
            extras["verify"].append("Licence-limit tests (simultaneous users, download caps)")
        if "Audit & Reporting" in cats:
            extras["verify"].append("Audit-log completeness and report-accuracy checks")
            extras["release"].append("Accreditation report sample reviewed by librarian")
        phases = []
        for i, p in enumerate(BASE_PHASES[model]):
            p = {k: (list(v) if isinstance(v, list) else v) for k, v in p.items()}
            name = p["phase"].lower()
            if "design" in name or "threat" in name:
                p["compliance"] += extras["design"]
            if "verif" in name or "test" in name:
                p["compliance"] += extras["verify"]
            if "release" in name or "deploy" in name or "acceptance" in name or "compliance gate" in name:
                p["compliance"] += extras["release"]
            p["entry_criteria"] = "Previous gate approved" if i else "Approved scope and stakeholder list"
            p["exit_criteria"] = f"{p['gate']} recorded in the audit log"
            phases.append(p)
        return phases

    # -- explanation -----------------------------------------------------------
    def _explain(self, top: str, ranking: List[Dict[str, Any]], f: Dict[str, float]) -> str:
        high = [k for k, v in f.items() if v >= 0.6]
        low = [k for k, v in f.items() if v <= 0.3]
        offline = (
            f"{top} scores highest ({ranking[0]['score']}) against {ranking[1]['model']} ({ranking[1]['score']}) "
            f"and {ranking[2]['model']} ({ranking[2]['score']}). "
            f"High factors: {', '.join(high) or 'none'}. Low factors: {', '.join(low) or 'none'}. "
            + (f"Rules applied: {'; '.join(ranking[0]['rules_applied'])}. " if ranking[0]["rules_applied"] else "")
            + "This is a heuristic recommendation; the project manager, architect, security team and compliance officer must approve it."
        )
        if not self.llm.available:
            return offline
        text = self.llm.complete(
            "You explain SDLC recommendations to a library project team in 4-5 sentences. Use ONLY the supplied scores and factors; do not invent facts.",
            f"Recommended: {top}\nRanking: {[(r['model'], r['score']) for r in ranking[:3]]}\nFactors: {f}",
            max_tokens=400,
        )
        return text or offline
