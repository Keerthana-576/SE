"""Optional LLM access.

The prototype runs fully offline (rule-based agents). If `--llm` is passed, the
`anthropic` package is installed and ANTHROPIC_API_KEY is set, the extraction and
SDLC-justification steps additionally use Claude. Any failure falls back to the
offline path, so the pipeline never depends on the network.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")


class LLM:
    def __init__(self, enabled: bool = False):
        self.client = None
        self.model = DEFAULT_MODEL
        if enabled and os.environ.get("ANTHROPIC_API_KEY"):
            try:
                import anthropic  # type: ignore

                self.client = anthropic.Anthropic()
            except Exception:
                self.client = None

    @property
    def available(self) -> bool:
        return self.client is not None

    def complete(self, system: str, user: str, max_tokens: int = 1500) -> Optional[str]:
        if not self.available:
            return None
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        except Exception:
            return None

    def complete_json(self, system: str, user: str, max_tokens: int = 2000) -> Optional[Any]:
        raw = self.complete(system, user, max_tokens)
        if not raw:
            return None
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
        try:
            return json.loads(raw)
        except Exception:
            return None
