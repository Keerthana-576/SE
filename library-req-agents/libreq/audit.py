"""Hash-chained, append-only audit log (JSON Lines).

Every record stores the hash of the previous record, so editing or deleting a
line afterwards breaks the chain and `AuditLog.verify` reports it.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional

GENESIS = "0" * 64


class AuditLog:
    def __init__(self, path: str):
        self.path = path
        self.prev = GENESIS
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        open(path, "w", encoding="utf-8").close()

    def log(self, agent: str, event: str, details: Optional[Dict[str, Any]] = None) -> None:
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "agent": agent,
            "event": event,
            "details": details or {},
            "prev": self.prev,
        }
        rec["hash"] = hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
        self.prev = rec["hash"]

    @staticmethod
    def verify(path: str) -> bool:
        prev = GENESIS
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                claimed = rec.pop("hash", None)
                if rec.get("prev") != prev:
                    return False
                if hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest() != claimed:
                    return False
                prev = claimed
        return True
