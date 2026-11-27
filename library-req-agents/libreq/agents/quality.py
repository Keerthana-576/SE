"""Agent 2 - Quality & Clarification Agent.

Checks every requirement for ambiguity, incompleteness, missing controls,
duplication and conflicts, scores confidence, and produces the clarification
questions that go back to stakeholders. Also reports missing requirement areas.
"""
from __future__ import annotations

import itertools
import re
from typing import Any, Dict, FrozenSet, List, Set, Tuple

from ..kb import kw_match, tokenize
from ..models import Requirement
from .base import Agent

VAGUE = [
    "fast", "quick", "quickly", "user-friendly", "user friendly", "easy", "easily", "secure",
    "appropriate", "flexible", "robust", "efficient", "seamless", "modern", "intuitive", "adequate",
    "reasonable", "as needed", "when needed", "etc", "and/or", "some", "several", "many", "good",
    "better", "minimal", "soon", "scalable", "properly",
]

PARAM = re.compile(
    r"\b(limit|period|threshold|fine|retention|maximum|minimum|timeout|quota|fee|penalty|duration|interval)\b", re.I
)

NUM = re.compile(
    r"(?:(?:rs|inr|\u20b9)\.?\s*(\d+(?:\.\d+)?))"
    r"|(?:(\d+(?:\.\d+)?)\s*(days?|hours?|minutes?|seconds?|months?|years?|books?|items?|copies|times|renewals?|%|percent))",
    re.I,
)

TOPICS = {
    "loan period": ["loan period", "loan duration", "borrowing period"],
    "fine rate": ["fine", "penalty", "late fee"],
    "renewals": ["renew"],
    "borrowing limit": ["borrowing limit", "borrow limit", "maximum books", "books per member"],
    "retention": ["retention", "retain", "retained"],
    "response time": ["response time"],
}

NEGATIVE = re.compile(r"\b(shall not|must not|should not|not allow|never|prohibit|no one)\b", re.I)

AREAS = {
    "Security": "Who can log in and what may each role do (authentication, SSO, roles)?",
    "Privacy": "What member personal data is collected, for what purpose, and how long is it kept?",
    "Audit & Reporting": "Which actions must be logged, and which reports are required (including accreditation)?",
    "Accessibility": "Which accessibility needs (screen readers, keyboard use, accessible formats) must be supported?",
    "Performance": "What response-time and concurrent-user targets apply, for example during exam periods?",
    "Availability": "What uptime, backup and recovery expectations apply?",
    "Integration": "Which existing systems must be integrated (Koha, ERP, LMS, RFID, SSO)?",
}


def _values(text: str) -> Set[Tuple[str, str]]:
    vals = set()
    for m in NUM.finditer(text):
        if m.group(1):
            vals.add((m.group(1), "rs"))
        else:
            unit = m.group(3).lower().rstrip("s")
            vals.add((m.group(2), unit))
    return vals


def _content_tokens(text: str) -> Set[str]:
    t = NEGATIVE.sub(" ", text)
    return set(tokenize(t))


def _jaccard(a: Set[str], b: Set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


class QualityAgent(Agent):
    name = "QualityClarificationAgent"

    def run(self, reqs: List[Requirement], resolved: Set[FrozenSet[str]] = None) -> List[Dict[str, Any]]:
        resolved = resolved or set()
        active = [r for r in reqs if r.status != "Rejected"]
        for r in active:
            r.issues = []
            self._single_checks(r)
        self._pair_checks(active, resolved)
        for r in active:
            penalty = sum({"Ambiguity": 0.15, "Conflict": 0.2}.get(i["type"], 0.1) for i in r.issues)
            r.confidence = round(max(0.2, min(0.95, 0.9 - penalty)), 2)
            if r.status not in ("Approved", "Pending Approval"):
                r.status = "Needs Clarification" if r.issues else "Validated"
        gaps = self._area_gaps(active)
        self.log(
            "quality_checked",
            requirements=len(active),
            with_issues=sum(1 for r in active if r.issues),
            missing_areas=[g["area"] for g in gaps],
        )
        return gaps

    # -- single requirement checks -----------------------------------------
    def _single_checks(self, r: Requirement) -> None:
        text = r.statement
        terms = [v for v in VAGUE if kw_match(v + "!", text)]
        for term in terms:
            self._add(r, "Ambiguity", "Medium", f"Vague term '{term}'.",
                      f"{r.id}: you used '{term}'. What measurable target applies (a number, time, standard or list)?")
        if PARAM.search(text) and not re.search(r"\d", text) and not re.search(
            r"approved|configurable|per member category", text, re.I
        ):
            self._add(r, "Incomplete", "High", "A limit/period/rate is mentioned but no value is given.",
                      f"{r.id}: what is the exact value (or who approves it) for the limit, period or rate mentioned?")
        if re.search(r"\b(overrid|waiv|bypass|exempt)", text, re.I) and not re.search(
            r"\b(log|audit|record|reason|approv)", text, re.I
        ):
            self._add(r, "Missing control", "High", "Override/waiver without logging or authorisation.",
                      f"{r.id}: who may override, and should every override be logged with the user ID and a reason?")
        if r.source in ("Unknown", ""):
            self._add(r, "Missing source", "Medium", "No stakeholder is linked to this requirement.",
                      f"{r.id}: which stakeholder asked for this?")
        if len(text.split()) < 6:
            self._add(r, "Incomplete", "Medium", "Statement is too short to test.",
                      f"{r.id}: can you describe the expected behaviour in more detail?")

    # -- cross-requirement checks ------------------------------------------
    def _pair_checks(self, active: List[Requirement], resolved: Set[FrozenSet[str]]) -> None:
        vals = {r.id: _values(r.statement) for r in active}
        seen_pairs: Set[FrozenSet[str]] = set()
        for topic, kws in TOPICS.items():
            members = [r for r in active if any(kw_match(k, r.statement) for k in kws) and vals[r.id]]
            for a, b in itertools.combinations(members, 2):
                pair = frozenset((a.id, b.id))
                if pair in resolved or pair in seen_pairs:
                    continue
                if self._numeric_conflict(vals[a.id], vals[b.id]):
                    seen_pairs.add(pair)
                    self._conflict(a, b, f"differ on {topic}",
                                   f"{a.id} and {b.id} give different values for {topic}. "
                                   f"Which applies, or does it vary by member category?")
        for a, b in itertools.combinations(active, 2):
            pair = frozenset((a.id, b.id))
            if pair in resolved or pair in seen_pairs:
                continue
            ta, tb = _content_tokens(a.statement), _content_tokens(b.statement)
            sim = _jaccard(ta, tb)
            neg_a, neg_b = bool(NEGATIVE.search(a.statement)), bool(NEGATIVE.search(b.statement))
            if neg_a != neg_b and sim >= 0.5:
                seen_pairs.add(pair)
                self._conflict(a, b, "contradict each other",
                               f"{a.id} and {b.id} appear to contradict each other. Which one is correct?")
            elif neg_a == neg_b and sim >= 0.75:
                seen_pairs.add(pair)
                self._add(b, "Duplication", "Low", f"Near-duplicate of {a.id}.",
                          f"{b.id} looks like a duplicate of {a.id}. Can they be merged?", pair=[a.id, b.id])

    @staticmethod
    def _numeric_conflict(a: Set[Tuple[str, str]], b: Set[Tuple[str, str]]) -> bool:
        for unit in {u for _, u in a} & {u for _, u in b}:
            va = {v for v, u in a if u == unit}
            vb = {v for v, u in b if u == unit}
            if va.isdisjoint(vb):
                return True
        return False

    def _conflict(self, a: Requirement, b: Requirement, what: str, question: str) -> None:
        for r, other in ((a, b), (b, a)):
            self._add(r, "Conflict", "High", f"Conflicts with {other.id} ({what}).", question,
                      pair=[a.id, b.id])

    @staticmethod
    def _add(r: Requirement, kind: str, severity: str, detail: str, question: str, **extra: Any) -> None:
        r.issues.append({"type": kind, "severity": severity, "detail": detail, "question": question, **extra})

    # -- completeness --------------------------------------------------------
    @staticmethod
    def _area_gaps(active: List[Requirement]) -> List[Dict[str, Any]]:
        present = {c for r in active for c in r.categories}
        return [{"area": a, "question": q} for a, q in AREAS.items() if a not in present]
