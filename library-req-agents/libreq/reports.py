"""Generates all output artefacts from a finished Project."""
from __future__ import annotations

import csv
import json
import os
import time
from typing import List

from .models import Project, Requirement


def _active(p: Project) -> List[Requirement]:
    return [r for r in p.requirements if r.status != "Rejected"]


def _md_row(cells) -> str:
    return "| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in cells) + " |"


def write_all(p: Project, out_dir: str) -> List[str]:
    os.makedirs(out_dir, exist_ok=True)
    files = {
        "requirements.json": _json(p),
        "SRS.md": _srs(p),
        "sdlc_plan.md": _sdlc_md(p),
    }
    paths = []
    for name, content in files.items():
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        paths.append(path)
    paths += [_rtm(p, out_dir), _compliance_csv(p, out_dir), _risk_csv(p, out_dir)]
    return paths


def _json(p: Project) -> str:
    return json.dumps(
        {
            "project": p.name,
            "requirements": [r.to_dict() for r in p.requirements],
            "open_questions": p.open_questions,
            "compliance_gaps": p.compliance_gaps,
            "sdlc": p.sdlc,
            "approvals": p.approvals,
            "stats": p.stats,
        },
        indent=2,
        ensure_ascii=False,
    )


def _rtm(p: Project, out_dir: str) -> str:
    path = os.path.join(out_dir, "traceability_matrix.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Requirement ID", "Stakeholder", "Original statement (masked)", "Policy IDs", "Acceptance criteria", "Test case IDs", "Status"])
        for r in _active(p):
            tcs = "; ".join(f"TC-{r.id}-{i:02d}" for i in range(1, len(r.acceptance_criteria) + 1))
            w.writerow([r.id, r.source, r.source_text, "; ".join(x["id"] for x in r.policies), len(r.acceptance_criteria), tcs, r.status])
    return path


def _compliance_csv(p: Project, out_dir: str) -> str:
    path = os.path.join(out_dir, "compliance_matrix.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Requirement ID", "Policy ID", "Policy", "Source", "Jurisdiction", "Version", "Retrieval score", "Required control", "Needs human approval"])
        for r in _active(p):
            for x in r.policies:
                w.writerow([r.id, x["id"], x["title"], x["source"], x["jurisdiction"], x["version"], x["score"], x["control"], "Yes" if r.escalations else "No"])
    return path


def _risk_csv(p: Project, out_dir: str) -> str:
    path = os.path.join(out_dir, "risk_register.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Risk ID", "Source", "Level", "Description", "Mitigation / control"])
        n = 0
        for r in _active(p):
            if r.risk in ("High", "Medium"):
                n += 1
                ctrl = "; ".join(x["control"] for x in r.policies[:2]) or "Review by security/compliance"
                w.writerow([f"RK-{n:03d}", r.id, r.risk, f"{', '.join(r.categories)}: {r.statement}", ctrl])
        for g in p.compliance_gaps:
            n += 1
            w.writerow([f"RK-{n:03d}", g["policy_id"], "High", g["message"], g["suggested_requirement"]])
        for r in _active(p):
            for i in r.issues:
                if i["type"] == "Conflict" and r.id == i["pair"][0]:
                    n += 1
                    w.writerow([f"RK-{n:03d}", "/".join(i["pair"]), "High", i["detail"], "Stakeholder decision required"])
    return path


def _srs(p: Project) -> str:
    act = _active(p)
    L: List[str] = []
    L += [f"# Software Requirements Specification - {p.name}", "",
          f"*Generated {time.strftime('%Y-%m-%d %H:%M')} by the Library Requirements Multi-Agent Prototype. "
          "Advisory draft: nothing here is baselined until approved by authorised stakeholders.*", ""]
    L += ["## 1. Summary", "",
          f"- Requirements extracted: **{len(act)}** ({sum(1 for r in p.requirements if r.status == 'Rejected')} rejected)",
          f"- Need clarification: **{sum(1 for r in act if r.issues)}**",
          f"- High-risk: **{sum(1 for r in act if r.risk == 'High')}**",
          f"- Compliance gaps found: **{len(p.compliance_gaps)}**",
          f"- Recommended SDLC: **{p.sdlc['recommended']}** (pending approval)",
          f"- Personal data masked before processing: {p.stats.get('masked', {}) or 'none found'}",
          f"- Lines blocked as possible prompt injection: {len(p.stats.get('injection_lines', []))}", ""]
    L += ["## 2. Requirements", "",
          _md_row(["ID", "Requirement", "Source", "Priority", "Categories", "Risk", "Conf.", "Status"]),
          _md_row(["---"] * 8)]
    for r in act:
        L.append(_md_row([r.id, r.statement, r.source, r.priority, ", ".join(r.categories), r.risk, r.confidence, r.status]))
    L += ["", "## 3. Requirement details", ""]
    for r in act:
        L += [f"### {r.id}", "", f"**Statement:** {r.statement}", "",
              f"**Source:** {r.source} - original: \"{r.source_text}\"", "",
              f"**Categories:** {', '.join(r.categories)} | **Priority:** {r.priority} | **Risk:** {r.risk} | "
              f"**Confidence:** {r.confidence} | **Status:** {r.status}", ""]
        L.append("**Acceptance criteria:**")
        L += [f"{i}. {c}" for i, c in enumerate(r.acceptance_criteria, 1)]
        if r.policies:
            L += ["", "**Evidence (citations):**"]
            L += [f"- [{x['id']}] {x['title']} ({x['jurisdiction']}, {x['version']}), retrieval score {x['score']}" for x in r.policies]
        if r.issues:
            L += ["", "**Quality issues:**"]
            L += [f"- {i['type']} ({i['severity']}): {i['detail']}" for i in r.issues]
        if r.escalations:
            L += ["", "**Human review required:**"]
            L += [f"- {e}" for e in r.escalations]
        if r.notes:
            L += ["", "**Notes:** " + " ".join(r.notes)]
        L.append("")
    L += ["## 4. Open questions for stakeholders", ""]
    qs = [(r.id, i["question"]) for r in act for i in r.issues]
    seen = set()
    for rid, q in qs:
        if q not in seen:
            seen.add(q)
            L.append(f"- {q}")
    for g in p.open_questions:
        L.append(f"- **Missing area - {g['area']}:** {g['question']}")
    if not seen and not p.open_questions:
        L.append("- None")
    L += ["", "## 5. Compliance gaps and suggested additions (not baselined)", ""]
    if p.compliance_gaps:
        L += [_md_row(["Policy", "Missing control", "Suggested requirement"]), _md_row(["---"] * 3)]
        L += [_md_row([g["policy_id"], g["control"], g["suggested_requirement"]]) for g in p.compliance_gaps]
    else:
        L.append("None found.")
    L += ["", "## 6. Approvals", ""]
    if p.approvals:
        L += [_md_row(["Item", "Decision", "By", "Note"]), _md_row(["---"] * 4)]
        L += [_md_row([a["item"], a["decision"], a["by"], a.get("note", "")]) for a in p.approvals]
    else:
        L.append("No approvals recorded (advisory mode). All items are pending human approval.")
    L += ["", "## 7. SDLC recommendation", "", _sdlc_body(p), ""]
    L += ["## 8. Disclaimer", "",
          "Policy mappings come from an illustrative knowledge base and are not legal determinations. "
          "A compliance or legal officer must verify and approve every mapping."]
    return "\n".join(L)


def _sdlc_body(p: Project) -> str:
    s = p.sdlc
    L = [f"**Recommended:** {s['recommended']}", "", s["justification"], "",
         "**Ranking (heuristic suitability, not probability):**"]
    L += [f"{i}. {r['model']}: {r['score']}%" for i, r in enumerate(s["ranking"], 1)]
    L += ["", "**Decision factors (0-1):** " + ", ".join(f"{k}={v}" for k, v in s["factors"].items()), "",
          f"**Approval:** {s['approval']}"]
    return "\n".join(L)


def _sdlc_md(p: Project) -> str:
    s = p.sdlc
    L = [f"# Project-specific SDLC workflow - {s['recommended']}", "", _sdlc_body(p), "", "## Workflow", ""]
    for i, ph in enumerate(s["workflow"], 1):
        L += [f"### Phase {i}: {ph['phase']}", "",
              f"- **Activities:** {'; '.join(ph['activities'])}",
              f"- **Roles:** {', '.join(ph['roles'])}",
              f"- **Deliverables:** {', '.join(ph['deliverables'])}",
              f"- **Security controls:** {', '.join(ph['security']) or 'None specific'}",
              f"- **Compliance checkpoints:** {', '.join(ph['compliance']) or 'None specific'}",
              f"- **Entry criteria:** {ph['entry_criteria']}",
              f"- **Exit criteria:** {ph['exit_criteria']}",
              f"- **Human-approval gate:** {ph['gate']}", ""]
    return "\n".join(L)
