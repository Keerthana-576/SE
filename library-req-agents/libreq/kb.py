"""Version-controlled knowledge base with a small dependency-free retriever.

Retrieval = TF-IDF cosine similarity blended with trigger-phrase matches.
In a production system, replace `search` with a vector database; the interface
(`search(text, k) -> [(entry, score)]`) stays the same.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Any, Dict, List, Tuple

STOPWORDS = set(
    "a an the of to and or in on for with by is are be shall should must can may will "
    "that this these those it its as at from into per all any each".split()
)


def tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS and len(t) > 1]


def kw_match(keyword: str, text: str) -> bool:
    """Prefix-boundary match: 'log' matches 'logged' and 'login' but not 'catalogue'.
    A trailing '!' means exact word (e.g. 'act!')."""
    exact = keyword.endswith("!")
    pat = r"\b" + re.escape(keyword.rstrip("!")) + (r"\b" if exact else "")
    return re.search(pat, text.lower()) is not None


class KnowledgeBase:
    def __init__(self, entries: List[Dict[str, Any]]):
        self.entries = entries
        self._docs = [Counter(tokenize(self._doc_text(e))) for e in entries]
        n = len(entries)
        df: Counter = Counter()
        for d in self._docs:
            df.update(d.keys())
        self._idf = {t: math.log((1 + n) / (1 + c)) + 1.0 for t, c in df.items()}
        self._norms = [self._norm(d) for d in self._docs]

    @classmethod
    def load(cls, path: str) -> "KnowledgeBase":
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f)["entries"])

    @staticmethod
    def _doc_text(e: Dict[str, Any]) -> str:
        return " ".join([e["title"], e["text"], " ".join(e.get("triggers", []))])

    def _vec(self, tf: Counter) -> Dict[str, float]:
        return {t: (1 + math.log(c)) * self._idf.get(t, 0.0) for t, c in tf.items()}

    def _norm(self, tf: Counter) -> float:
        return math.sqrt(sum(v * v for v in self._vec(tf).values())) or 1.0

    def search(self, text: str, k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        q = Counter(tokenize(text))
        qv = self._vec(q)
        qn = math.sqrt(sum(v * v for v in qv.values())) or 1.0
        results = []
        for entry, doc, dn in zip(self.entries, self._docs, self._norms):
            dv = self._vec(doc)
            cos = sum(qv[t] * dv.get(t, 0.0) for t in qv) / (qn * dn)
            hits = sum(1 for trig in entry.get("triggers", []) if kw_match(trig, text))
            trig_score = min(1.0, hits / 2.0)
            score = 0.6 * trig_score + 0.4 * min(1.0, cos * 2.5)
            results.append((entry, round(score, 3)))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
