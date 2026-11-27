"""Sensitive-data masking and prompt-injection screening.

Everything that reaches an agent (and therefore any LLM) is masked first.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

_PATTERNS = [
    ("AADHAAR", re.compile(r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)")),
    ("PHONE", re.compile(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}(?!\d)")),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("MEMBER_ID", re.compile(r"\b(?:LIB|MEM|STU|FAC)[-/]?\d{3,}\b", re.I)),
]

_INJECTION = re.compile(
    r"(ignore\s+(all\s+|any\s+)?(previous|prior|above)\s+(instructions|rules)"
    r"|disregard\s+.*instructions"
    r"|system\s+prompt"
    r"|you\s+are\s+now"
    r"|reveal\s+.*(prompt|api\s*key|password)"
    r"|mark\s+(all|every)\s+.*approved)",
    re.I,
)


def mask_text(text: str) -> Tuple[str, Dict[str, int]]:
    """Replace personal identifiers with placeholders. Returns (masked_text, counts)."""
    counts: Dict[str, int] = {}
    for label, pattern in _PATTERNS:
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = n
    return text, counts


def screen_injection(text: str) -> Tuple[str, List[str]]:
    """Drop lines that look like prompt-injection attempts. Returns (clean_text, dropped_lines)."""
    clean, dropped = [], []
    for line in text.splitlines():
        if _INJECTION.search(line):
            dropped.append(line.strip())
        else:
            clean.append(line)
    return "\n".join(clean), dropped
