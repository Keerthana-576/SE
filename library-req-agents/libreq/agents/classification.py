"""Agent 3 - Classification Agent.

Multi-label classification across 14 categories, assigns the library module and
final requirement ID (e.g. FR-CIR-001), and drafts acceptance criteria.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List

from ..kb import kw_match
from ..models import Requirement
from .base import Agent

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Functional": [
        "issue", "return", "renew", "reserve", "search", "register", "deposit", "upload", "download",
        "notif", "generate", "calculate", "block", "allow", "borrow", "catalogue", "add", "edit",
        "delete", "view", "display", "pay", "send", "request", "recommend", "import", "export",
        "store", "record", "provide", "support", "enable",
    ],
    "Security": [
        "authenticat", "login", "log in", "password", "sso", "single sign", "role", "permission",
        "access control", "encrypt", "secure", "mfa", "multi-factor", "unauthori", "authoris",
        "authoriz", "session",
    ],
    "Privacy": [
        "personal", "privacy", "consent", "reading history", "borrower", "member data",
        "member record", "anonymi", "mask", "retention", "retain", "email", "phone", "address",
        "profile",
    ],
    "Regulatory": ["naac", "nba!", "nirf", "ugc", "act!", "regulation", "mandatory", "compliance", "accreditation", "statutory"],
    "Copyright/Licence": ["licen", "copyright", "subscription", "publisher", "simultaneous", "concurrent user", "download limit"],
    "Performance": ["fast", "quick", "response", "seconds", "latency", "throughput", "performance", "peak", "concurrent", "scal", "load"],
    "Availability": ["24x7", "24/7", "uptime", "availability", "downtime", "backup", "recovery", "disaster", "failover", "reliab"],
    "Usability": ["user-friendly", "user friendly", "easy", "easily", "intuitive", "usab", "simple", "mobile", "ui!", "ux!", "multilingual", "language"],
    "Accessibility": ["accessib", "screen reader", "wcag", "visually", "disab", "dyslex", "keyboard navigation", "alt text", "daisy"],
    "Data Management": ["data", "database", "metadata", "retention", "retain", "archive", "backup", "migrat", "import", "export", "history", "stored"],
    "Integration": ["integrat", "koha", "erp!", "lms!", "sip2", "ncip", "rfid", "api!", "oai", "sync", "interoperab", "sso", "dspace", "marc"],
    "Audit & Reporting": ["audit", "log!", "logged", "logging", "logs!", "report", "statistic", "analytics", "dashboard", "accreditation", "trail", "traceab"],
    "Operational": ["maintenance", "monitor", "deploy", "helpdesk", "configur", "patch", "schedule"],
    "Business": ["policy", "fine", "loan period", "budget", "cost", "vendor", "acquisition", "procure", "membership", "member categor", "footfall"],
}

MODULE_KEYWORDS: List = [
    ("CIR", ["issue", "return", "renew", "loan", "borrow", "fine", "reserv", "overdue", "circulation", "due date"]),
    ("MEM", ["member", "registration", "onboard", "enrol", "membership"]),
    ("CAT", ["catalog", "opac", "search", "metadata", "marc", "dublin", "isbn"]),
    ("DIG", ["e-journal", "e-book", "e-resource", "remote access", "licen", "subscription", "proxy"]),
    ("REP", ["repository", "thesis", "theses", "dspace", "open access", "embargo", "deposit"]),
    ("ACQ", ["acqui", "vendor", "purchase", "budget", "procure", "serial", "order"]),
    ("RPT", ["report", "statistic", "analytics", "accreditation", "naac", "nirf", "dashboard", "reading history"]),
    ("SEC", ["login", "authenticat", "sso", "password", "role", "access control"]),
    ("INT", ["integrat", "koha", "erp!", "lms!", "sip2", "ncip", "rfid", "api!", "oai"]),
]

CRITERIA: Dict[str, str] = {
    "Security": "Attempts by unauthorised roles are rejected and the attempt is logged.",
    "Privacy": "Personal data is masked in logs and exports; consent and purpose are recorded where data is collected.",
    "Audit & Reporting": "Each relevant action records user ID, timestamp, action and outcome in the audit log.",
    "Performance": "The agreed response-time target (value to be confirmed with stakeholders) is met under peak load.",
    "Availability": "The agreed availability target (value to be confirmed) is met over a monthly measurement window.",
    "Accessibility": "Affected screens pass a WCAG 2.1 AA check and work with a screen reader and keyboard only.",
    "Integration": "The interface passes a conformance test against the agreed standard (e.g. SIP2, NCIP, OAI-PMH) in the test environment.",
    "Copyright/Licence": "Licence limits (simultaneous users, download caps) are enforced as written in the publisher agreement.",
    "Regulatory": "Compliance evidence is attached and the compliance officer has signed off the mapped policy.",
}


class ClassificationAgent(Agent):
    name = "ClassificationAgent"

    def run(self, reqs: List[Requirement]) -> None:
        counters: Counter = Counter()
        for r in reqs:
            if r.status == "Rejected":
                continue
            text = f"{r.statement}"
            cats = [c for c, kws in CATEGORY_KEYWORDS.items() if any(kw_match(k, text) for k in kws)]
            if not cats:
                cats = ["Functional"]
            r.categories = sorted(set(r.categories) | set(cats), key=list(CATEGORY_KEYWORDS).index)
            r.module = self._module(text)
            if r.id.startswith("TMP-"):
                if "Functional" in r.categories:
                    prefix = "FR"
                elif set(r.categories) <= {"Business", "Data Management"}:
                    prefix = "BR"   # business rule
                else:
                    prefix = "NFR"
                counters[(prefix, r.module)] += 1
                r.id = f"{prefix}-{r.module}-{counters[(prefix, r.module)]:03d}"
            r.acceptance_criteria = self._criteria(r)
        self.log("classified", count=len([r for r in reqs if r.status != "Rejected"]))

    @staticmethod
    def _module(text: str) -> str:
        best, best_hits = "GEN", 0
        for mod, kws in MODULE_KEYWORDS:
            hits = sum(1 for k in kws if kw_match(k, text))
            if hits > best_hits:
                best, best_hits = mod, hits
        return best

    @staticmethod
    def _criteria(r: Requirement) -> List[str]:
        out = [f"Verified by at least one positive and one negative test case for: {r.statement}."]
        for cat in r.categories:
            if cat in CRITERIA:
                out.append(CRITERIA[cat])
        return out
