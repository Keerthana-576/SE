#!/usr/bin/env python3
"""Local web UI for the Library Requirements Multi-Agent Prototype.

    python server.py                 # http://127.0.0.1:8000
    python server.py --port 9000 --no-browser

Standard library only. Binds to 127.0.0.1 and checks the Host header, so it is
not reachable from other machines. The prototype is single-user: one analysis
session is held in memory at a time.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import threading
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional

from libreq.audit import AuditLog
from libreq.orchestrator import Orchestrator

ROOT = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(ROOT, "data", "knowledge_base.json")
SAMPLE_PATH = os.path.join(ROOT, "data", "sample_transcript.txt")
PROFILE_PATH = os.path.join(ROOT, "data", "project_profile.json")
INDEX_PATH = os.path.join(ROOT, "web", "index.html")

MAX_BODY = 1_000_000
MAX_TEXT = 200_000
NULLABLE = {"requirement_stability", "needs_formal_verification", "continuous_delivery_need"}
PROFILE_KEYS = {
    "requirement_stability": "num", "stakeholder_availability": "num",
    "needs_formal_verification": "num", "continuous_delivery_need": "num",
    "extensive_approvals": "bool",
}
CONTENT_TYPES = {".md": "text/markdown; charset=utf-8", ".csv": "text/csv; charset=utf-8",
                 ".json": "application/json", ".jsonl": "application/x-ndjson"}


def clean_profile(raw: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if not isinstance(raw, dict):
        return out
    for key, kind in PROFILE_KEYS.items():
        if key not in raw:
            continue
        v = raw[key]
        if v is None:
            if key in NULLABLE:   # None = "estimate automatically"
                out[key] = None
        elif kind == "bool":
            out[key] = bool(v)
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            out[key] = max(0.0, min(1.0, float(v)))
    return out


class App:
    """Holds the single in-memory session."""

    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.lock = threading.Lock()
        self.orch: Optional[Orchestrator] = None

    # -- state ----------------------------------------------------------------
    def state(self) -> Dict[str, Any]:
        o = self.orch
        if o is None or o.project is None:
            return {"empty": True}
        p = o.project
        log = os.path.join(self.out_dir, "audit_log.jsonl")
        return {
            "empty": False,
            "name": p.name,
            "requirements": [r.to_dict() for r in p.requirements],
            "open_questions": p.open_questions,
            "compliance_gaps": p.compliance_gaps,
            "sdlc": p.sdlc,
            "approvals": p.approvals,
            "stats": p.stats,
            "files": sorted(f for f in os.listdir(self.out_dir) if os.path.isfile(os.path.join(self.out_dir, f))),
            "audit_ok": AuditLog.verify(log),
            "llm": o.llm.available,
        }

    def audit_records(self, limit: int = 300):
        path = os.path.join(self.out_dir, "audit_log.jsonl")
        with open(path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        return rows[-limit:]

    # -- operations -----------------------------------------------------------
    def analyze(self, body: Dict[str, Any]) -> Dict[str, Any]:
        text = body.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Please provide some stakeholder text.")
        if len(text) > MAX_TEXT:
            raise ValueError("Input is too long for this prototype.")
        name = str(body.get("name") or "Library Management System")[:120]
        by = str(body.get("by") or "Reviewer")[:60]
        self.orch = Orchestrator(
            KB_PATH, self.out_dir, profile=clean_profile(body.get("profile")),
            use_llm=bool(body.get("use_llm")), project_name=name, approver=by,
        )
        self.orch.analyze(text)
        return self.state()

    def operate(self, action: str, body: Dict[str, Any]) -> Dict[str, Any]:
        o = self.orch
        if o is None:
            raise LookupError("Run an analysis first.")
        o.approver = str(body.get("by") or o.approver)[:60]
        if action == "decide":
            o.decide(str(body["id"]), str(body["decision"]))
        elif action == "revise":
            o.revise(str(body["id"]), str(body["statement"]))
        elif action == "add":
            o.add_requirement(str(body["text"]), str(body.get("who") or "Reviewer"))
        elif action == "resolve":
            o.resolve_pair(str(body["a"]), str(body["b"]), str(body["choice"]), str(body.get("note") or ""))
        elif action == "sdlc_model":
            o.set_sdlc_model(str(body["model"]))
        elif action == "sdlc_decide":
            o.decide_sdlc(str(body["decision"]))
        elif action == "approve_low_risk":
            o.approve_low_risk()
        else:
            raise ValueError("Unknown action")
        return self.state()


class Handler(BaseHTTPRequestHandler):
    app: App = None  # set by make_server
    server_version = "LibReq/1.0"

    # quiet logging
    def log_message(self, fmt, *args):  # noqa: A003
        pass

    # -- helpers ----------------------------------------------------------------
    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        return host in ("127.0.0.1", "localhost", "::1")

    def _send(self, code: int, data: bytes, ctype: str, extra: Optional[Dict[str, str]] = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj: Any, code: int = 200) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    # -- GET ----------------------------------------------------------------------
    def do_GET(self):  # noqa: N802
        if not self._host_ok():
            return self._json({"error": "Forbidden host"}, 403)
        path = self.path.split("?", 1)[0]
        try:
            if path in ("/", "/index.html"):
                with open(INDEX_PATH, "rb") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            if path == "/api/config":
                possible = bool(os.environ.get("ANTHROPIC_API_KEY")) and importlib.util.find_spec("anthropic") is not None
                return self._json({"llm_possible": possible})
            if path == "/api/sample":
                with open(SAMPLE_PATH, encoding="utf-8") as f:
                    text = f.read()
                with open(PROFILE_PATH, encoding="utf-8") as f:
                    profile = json.load(f)
                return self._json({"text": text, "profile": profile})
            if path == "/api/state":
                with self.app.lock:
                    return self._json(self.app.state())
            if path == "/api/audit":
                with self.app.lock:
                    if self.app.orch is None:
                        return self._json({"records": [], "ok": True})
                    return self._json({"records": self.app.audit_records(),
                                       "ok": AuditLog.verify(os.path.join(self.app.out_dir, "audit_log.jsonl"))})
            if path.startswith("/download/"):
                return self._download(path[len("/download/"):])
        except Exception:
            return self._json({"error": "Server error"}, 500)
        return self._json({"error": "Not found"}, 404)

    def _download(self, name: str) -> None:
        out = self.app.out_dir
        with self.app.lock:
            if name == "all.zip":
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                    for f in sorted(os.listdir(out)):
                        full = os.path.join(out, f)
                        if os.path.isfile(full):
                            z.write(full, f)
                return self._send(200, buf.getvalue(), "application/zip",
                                  {"Content-Disposition": 'attachment; filename="library-requirements.zip"'})
            if name != os.path.basename(name) or name not in os.listdir(out):
                return self._json({"error": "Not found"}, 404)
            with open(os.path.join(out, name), "rb") as f:
                data = f.read()
        ctype = CONTENT_TYPES.get(os.path.splitext(name)[1], "application/octet-stream")
        self._send(200, data, ctype, {"Content-Disposition": f'attachment; filename="{name}"'})

    # -- POST ---------------------------------------------------------------------
    def do_POST(self):  # noqa: N802
        if not self._host_ok():
            return self._json({"error": "Forbidden host"}, 403)
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self._json({"error": "Content-Type must be application/json"}, 415)
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._json({"error": "Bad length"}, 400)
        if length > MAX_BODY:
            return self._json({"error": "Request too large"}, 413)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(body, dict):
                raise ValueError("JSON object expected")
        except ValueError:
            return self._json({"error": "Invalid JSON"}, 400)

        path = self.path.split("?", 1)[0]
        if not path.startswith("/api/"):
            return self._json({"error": "Not found"}, 404)
        action = path[len("/api/"):]
        try:
            with self.app.lock:
                if action == "analyze":
                    return self._json(self.app.analyze(body))
                return self._json(self.app.operate(action, body))
        except LookupError as e:
            return self._json({"error": str(e)}, 409)
        except (ValueError, KeyError) as e:
            return self._json({"error": f"Invalid request: {e}"}, 400)
        except Exception:
            return self._json({"error": "Server error"}, 500)


def make_server(host: str = "127.0.0.1", port: int = 8000, out_dir: Optional[str] = None) -> ThreadingHTTPServer:
    handler = type("BoundHandler", (Handler,), {"app": App(out_dir or os.path.join(ROOT, "output", "web"))})
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    ap = argparse.ArgumentParser(description="Library requirements web UI")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    srv = make_server(port=args.port)
    url = f"http://127.0.0.1:{srv.server_address[1]}"
    print(f"Library Requirements UI running at {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
