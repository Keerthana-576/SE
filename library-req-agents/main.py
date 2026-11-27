#!/usr/bin/env python3
"""CLI entry point.

Examples
  python main.py                              # run on the bundled sample, advisory mode
  python main.py --interactive                # clarification questions + approval gates
  python main.py --input my_notes.txt --llm   # use Claude (needs ANTHROPIC_API_KEY)
"""
import argparse
import json
import os
import sys

from libreq.audit import AuditLog
from libreq.orchestrator import Orchestrator

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    ap = argparse.ArgumentParser(description="Library requirements multi-agent prototype")
    ap.add_argument("--input", default=os.path.join(HERE, "data", "sample_transcript.txt"))
    ap.add_argument("--kb", default=os.path.join(HERE, "data", "knowledge_base.json"))
    ap.add_argument("--profile", default=os.path.join(HERE, "data", "project_profile.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "output"))
    ap.add_argument("--name", default="College Library Management System")
    ap.add_argument("--interactive", action="store_true", help="ask clarification questions and approval gates")
    ap.add_argument("--llm", action="store_true", help="use Claude for extraction/explanations if available")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        raw = f.read()
    profile = {}
    if os.path.exists(args.profile):
        with open(args.profile, encoding="utf-8") as f:
            profile = json.load(f)

    orch = Orchestrator(args.kb, args.out, profile=profile, interactive=args.interactive,
                        use_llm=args.llm, project_name=args.name)
    if args.llm and not orch.llm.available:
        print("Note: --llm requested but the anthropic package or ANTHROPIC_API_KEY is missing; running offline.")
    p = orch.run(raw)

    act = [r for r in p.requirements if r.status != "Rejected"]
    print(f"\nRequirements: {len(act)} | need clarification: {sum(1 for r in act if r.issues)} | "
          f"high risk: {sum(1 for r in act if r.risk == 'High')} | compliance gaps: {len(p.compliance_gaps)}")
    print(f"Masked personal data: {p.stats['masked'] or 'none'} | injection lines blocked: {len(p.stats['injection_lines'])}")
    print(f"Recommended SDLC: {p.sdlc['recommended']}")
    for r in p.sdlc["ranking"][:3]:
        print(f"   {r['model']}: {r['score']}%")
    ok = AuditLog.verify(os.path.join(args.out, "audit_log.jsonl"))
    print(f"Audit log integrity: {'OK' if ok else 'BROKEN'}")
    print(f"Outputs written to: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
