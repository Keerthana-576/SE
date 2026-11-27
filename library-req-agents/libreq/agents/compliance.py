"""Agent 4 - Policy & Compliance Agent.

Retrieval-grounded mapping of each requirement to approved knowledge-base
entries, with citations and confidence. A deterministic rule check then finds
controls the project is missing. The agent never makes legal determinations:
policy mappings are escalated for a compliance/legal officer.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..kb import KnowledgeBase, kw_match
from ..models import Requirement
from .base import Agent

MAP_THRESHOLD = 0.30     # minimum score to attach a policy to a requirement
IMPLY_THRESHOLD = 0.45   # minimum score to add the entry's implied categories
SENSITIVE = {"Privacy", "Security", "Regulatory", "Copyright/Licence", "Accessibility"}
HIGH_RISK = {"Privacy", "Security", "Regulatory", "Copyright/Licence"}
MEDIUM_RISK = {"Integration", "Availability", "Audit & Reporting", "Accessibility"}


class ComplianceAgent(Agent):
    name = "PolicyComplianceAgent"

    def __init__(self, audit, kb: KnowledgeBase, llm=None):
        super().__init__(audit, llm)
        self.kb = kb

    def run(self, reqs: List[Requirement]) -> List[Dict[str, Any]]:
        active = [r for r in reqs if r.status != "Rejected"]
        for r in active:
            r.policies, r.escalations = [], []
            hits = [(e, s) for e, s in self.kb.search(r.statement, k=3) if s >= MAP_THRESHOLD]
            for entry, score in hits:
                r.policies.append(
                    {
                        "id": entry["id"],
                        "title": entry["title"],
                        "source": entry["source"],
                        "jurisdiction": entry["jurisdiction"],
                        "version": entry["version"],
                        "effective_date": entry["effective_date"],
                        "score": score,
                        "obligation": entry["text"],
                        "control": entry["control"],
                    }
                )
                if score >= IMPLY_THRESHOLD:
                    for c in entry.get("implies", []):
                        if c not in r.categories:
                            r.categories.append(c)
            self._confidence_and_escalation(r, hits)
            r.risk = self._risk(r)
        gaps = self._gap_rules(active)
        self.log(
            "compliance_mapped",
            requirements=len(active),
            with_policy=sum(1 for r in active if r.policies),
            gaps=len(gaps),
        )
        return gaps

    # -- helpers --------------------------------------------------------------
    @staticmethod
    def _confidence_and_escalation(r: Requirement, hits) -> None:
        if hits:
            top = hits[0][1]
            r.confidence = round(0.75 * r.confidence + 0.25 * top, 2)
            strong = any("Regulatory" in e.get("implies", []) and sc >= IMPLY_THRESHOLD for e, sc in hits)
            own_sensitive = bool({"Privacy", "Regulatory", "Copyright/Licence"} & set(r.categories))
            if strong or own_sensitive:
                r.escalations.append("Policy/regulatory interpretation must be approved by the compliance or legal officer.")
        elif set(r.categories) & SENSITIVE:
            r.confidence = round(r.confidence * 0.85, 2)
            r.escalations.append("Sensitive requirement with no supporting source found in the knowledge base: human review.")
        if r.confidence < 0.6:
            r.escalations.append(f"Low confidence ({r.confidence}): human review.")

    @staticmethod
    def _risk(r: Requirement) -> str:
        cats = set(r.categories)
        if cats & HIGH_RISK:
            return "High" if (r.policies or r.priority == "High") else "Medium"
        if cats & MEDIUM_RISK:
            return "Medium"
        return "Low"

    def _gap_rules(self, active: List[Requirement]) -> List[Dict[str, Any]]:
        """Deterministic check: if a policy applies to the project, are its required controls covered?"""
        all_text = " ".join(r.statement for r in active)
        triggered = {p["id"] for r in active for p in r.policies}
        gaps: List[Dict[str, Any]] = []
        for entry in self.kb.entries:
            if entry["id"] not in triggered:
                continue
            for ctrl in entry.get("required_controls", []):
                if not any(kw_match(k, all_text) for k in ctrl["keywords"]):
                    gaps.append(
                        {
                            "policy_id": entry["id"],
                            "policy_title": entry["title"],
                            "control": ctrl["name"],
                            "message": f"No requirement covers '{ctrl['name']}' required by {entry['title']}.",
                            "suggested_requirement": ctrl["suggested"],
                            "status": "Suggested - needs approval",
                        }
                    )
        return gaps
