from __future__ import annotations

from typing import Any, Optional

from ..audit import AuditLog
from ..llm import LLM


class Agent:
    name = "Agent"

    def __init__(self, audit: AuditLog, llm: Optional[LLM] = None):
        self.audit = audit
        self.llm = llm or LLM(False)

    def log(self, event: str, **details: Any) -> None:
        self.audit.log(self.name, event, details)
