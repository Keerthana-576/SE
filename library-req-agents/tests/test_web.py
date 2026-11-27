"""Web API tests (real HTTP server on an ephemeral port)."""
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request as ur

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from server import make_server  # noqa: E402


class TestWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.srv = make_server("127.0.0.1", 0, cls.tmp)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def get(self, path, headers=None):
        return ur.urlopen(ur.Request(self.base + path, headers=headers or {}))

    def post(self, path, body, ctype="application/json"):
        req = ur.Request(self.base + path, json.dumps(body).encode(), {"Content-Type": ctype})
        try:
            with ur.urlopen(req) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def test_01_page_and_sample(self):
        self.assertIn(b"Library Requirements Agents", self.get("/").read())
        self.assertIn("[Librarian]", json.load(self.get("/api/sample"))["text"])

    def test_02_actions_need_session(self):
        # state is empty until an analysis runs (order-dependent: runs before analyze)
        self.assertTrue(json.load(self.get("/api/state"))["empty"])
        code, _ = self.post("/api/decide", {"id": "X", "decision": "Approved"})
        self.assertEqual(code, 409)

    def test_03_full_flow(self):
        sample = json.load(self.get("/api/sample"))
        code, st = self.post("/api/analyze", {"text": sample["text"], "profile": sample["profile"]})
        self.assertEqual(code, 200)
        self.assertTrue(st["audit_ok"])
        ids = [r["id"] for r in st["requirements"]]
        # approve one, resolve a conflict, add a suggested requirement, change SDLC model
        code, st = self.post("/api/decide", {"id": ids[0], "decision": "Approved"})
        self.assertEqual(next(r for r in st["requirements"] if r["id"] == ids[0])["status"], "Approved")
        pair = next(i["pair"] for r in st["requirements"] for i in r["issues"] if i["type"] == "Conflict")
        code, st = self.post("/api/resolve", {"a": pair[0], "b": pair[1], "choice": "a"})
        self.assertEqual(next(r for r in st["requirements"] if r["id"] == pair[1])["status"], "Rejected")
        n_gaps = len(st["compliance_gaps"])
        code, st = self.post("/api/add", {"text": st["compliance_gaps"][0]["suggested_requirement"], "who": "Compliance Agent (suggested)"})
        self.assertLess(len(st["compliance_gaps"]), n_gaps)
        code, st = self.post("/api/sdlc_model", {"model": "V-Model"})
        self.assertEqual(st["sdlc"]["recommended"], "V-Model")
        self.assertIn("Human override", st["sdlc"]["justification"])
        code, st = self.post("/api/sdlc_decide", {"decision": "Approved"})
        self.assertTrue(st["sdlc"]["approval"].startswith("Approved"))
        self.assertTrue(st["audit_ok"])
        self.assertTrue(any(a["item"] == "SDLC model changed" for a in st["approvals"]))

    def test_04_validation_and_security(self):
        self.assertEqual(self.post("/api/analyze", {"text": ""})[0], 400)
        self.assertEqual(self.post("/api/decide", {"id": "NOPE", "decision": "Approved"})[0], 400)
        self.assertEqual(self.post("/api/analyze", {"text": "x"}, ctype="text/plain")[0], 415)
        with self.assertRaises(urllib.error.HTTPError) as c:
            self.get("/api/state", headers={"Host": "evil.example.com"})
        self.assertEqual(c.exception.code, 403)
        with self.assertRaises(urllib.error.HTTPError) as c:
            self.get("/download/..%2Fserver.py")
        self.assertEqual(c.exception.code, 404)

    def test_05_downloads_and_no_pii(self):
        sample = json.load(self.get("/api/sample"))
        self.post("/api/analyze", {"text": sample["text"]})
        self.assertGreater(len(self.get("/download/all.zip").read()), 1000)
        srs = self.get("/download/SRS.md").read().decode()
        for secret in ("librarian@college.edu", "9876543210", "LIB-20457"):
            self.assertNotIn(secret, srs)


if __name__ == "__main__":
    unittest.main()
