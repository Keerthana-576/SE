"""Shared data structures used by all agents."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class Requirement:
    id: str
    statement: str
    source: str                      # stakeholder role
    source_text: str                 # original (already masked) stakeholder wording
    priority: str = "Medium"         # High / Medium / Low
    categories: List[str] = field(default_factory=list)
    module: str = "GEN"
    acceptance_criteria: List[str] = field(default_factory=list)
    policies: List[Dict[str, Any]] = field(default_factory=list)   # retrieved evidence
    issues: List[Dict[str, Any]] = field(default_factory=list)     # quality problems
    escalations: List[str] = field(default_factory=list)           # reasons for human review
    risk: str = "Low"
    confidence: float = 0.0
    status: str = "Draft"            # Draft / Needs Clarification / Validated / Approved / Rejected / Pending Approval
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Project:
    name: str
    requirements: List[Requirement]
    open_questions: List[Dict[str, Any]]
    compliance_gaps: List[Dict[str, Any]]
    sdlc: Dict[str, Any]
    approvals: List[Dict[str, Any]]
    stats: Dict[str, Any]
