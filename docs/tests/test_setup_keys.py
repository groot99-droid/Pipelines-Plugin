"""Tests for docs/setup_keys.py. stdlib unittest; run from the repo root:

    python -m unittest discover -s docs/tests -v
"""
import http.client
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

DOCS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DOCS))

import setup_keys as sk  # noqa: E402

TOKEN = "test-token-123"
SECRET = "AIzaTESTVALUEnotarealkey0123456789abcd"


class ServerTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "sub" / "keys.env"
        self.server = sk.make_server(self.path, TOKEN)
        self.port = self.server.server_address[1]
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def request(self, method, route, body=None, token=TOKEN, host=None, origin=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {"Host": host or f"127.0.0.1:{self.port}"}
        if token is not None:
            headers["X-ROSW-Token"] = token
        if origin:
            headers["Origin"] = origin
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        conn.request(method, route, body=data, headers=headers)
        resp = conn.getresponse()
        raw = resp.read()
        conn.close()
        return resp.status, raw

    def test_status_needs_the_token(self):
        self.assertEqual(self.request("GET", "/status", token=None)[0], 403)
        self.assertEqual(self.request("GET", "/status", token="wrong")[0], 403)
        code, raw = self.request("GET", "/status")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)["keys"],
                         {"GEMINI_API_KEY": False, "ANTHROPIC_API_KEY": False,
                          "GOOGLE_FONTS_API_KEY": False})

    def test_save_needs_the_token(self):
        body = {"set": {"GEMINI_API_KEY": SECRET}}
        self.assertEqual(self.request("POST", "/save", body, token=None)[0], 403)
        self.assertEqual(self.request("POST", "/quit", token="wrong")[0], 403)
        self.assertFalse(self.path.exists())

    def test_bad_host_or_origin_is_refused(self):
        self.assertEqual(self.request("GET", "/status", host="evil.example")[0], 403)
        self.assertEqual(self.request("GET", "/keys.html", host=f"localhost:{self.port}")[0], 403)
        code, _ = self.request("POST", "/save", {"set": {}}, origin="http://evil.example")
        self.assertEqual(code, 403)

    def test_static_page_is_served(self):
        code, raw = self.request("GET", "/keys.html", token=None)
        self.assertEqual(code, 200)
        self.assertIn(b"<html", raw.lower())
        self.assertEqual(self.request("GET", "/setup_keys.py", token=None)[0], 404)
        self.assertEqual(self.request("GET", "/../README.md", token=None)[0], 404)

    def test_unknown_or_malformed_keys_are_refused(self):
        for body in ({"set": {"PATH": "x"}}, {"remove": ["HOME"]},
                     {"set": {"GEMINI_API_KEY": "a\nEVIL=1"}}, {"other": 1}):
            self.assertEqual(self.request("POST", "/save", body)[0], 400, body)
        self.assertFalse(self.path.exists())

    def test_save_merges_and_never_echoes_the_value(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("# mine\nGEMINI_MODEL=m\nANTHROPIC_API_KEY=old\n", encoding="utf-8")
        code, raw = self.request("POST", "/save",
                                 {"set": {"GEMINI_API_KEY": SECRET, "ANTHROPIC_API_KEY": ""}})
        self.assertEqual(code, 200)
        self.assertNotIn(SECRET.encode(), raw)
        self.assertTrue(json.loads(raw)["keys"]["GEMINI_API_KEY"])
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("# mine\nGEMINI_MODEL=m\nANTHROPIC_API_KEY=old\n", text)
        self.assertIn(f"GEMINI_API_KEY={SECRET}\n", text)
        _, raw = self.request("GET", "/status")
        self.assertNotIn(SECRET.encode(), raw)

    def test_remove(self):
        self.request("POST", "/save", {"set": {"GEMINI_API_KEY": SECRET}})
        code, raw = self.request("POST", "/save", {"remove": ["GEMINI_API_KEY"]})
        self.assertEqual(code, 200)
        self.assertFalse(json.loads(raw)["keys"]["GEMINI_API_KEY"])
        self.assertNotIn(SECRET, self.path.read_text(encoding="utf-8"))


def no_override():
    return {k: v for k, v in os.environ.items() if k != "ROSW_KEYS_FILE"}


class LocationTests(unittest.TestCase):
    def test_default_is_in_the_user_profile(self):
        with mock.patch.dict(os.environ, no_override(), clear=True):
            path = sk.keys_file()
        self.assertTrue(path.is_absolute())
        self.assertEqual(path.parent.name, ".rosw")
        self.assertNotIn(sk.REPO, path.resolve().parents)

    def test_override(self):
        with mock.patch.dict(os.environ, {"ROSW_KEYS_FILE": "x/k.env"}):
            self.assertEqual(sk.keys_file(), Path("x/k.env"))

    def test_llm_reads_the_same_file(self):
        sys.path.insert(0, str(sk.REPO / "creative-writing" / "pipeline"))
        import llm
        for env in (no_override(), {**no_override(), "ROSW_KEYS_FILE": "x/k.env"}):
            with mock.patch.dict(os.environ, env, clear=True):
                self.assertEqual(Path(llm.user_keys_file()), sk.keys_file())


class MigrateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.legacy = Path(tmp.name) / ".env"
        self.target = Path(tmp.name) / "user" / "keys.env"
        patcher = mock.patch.object(sk, "LEGACY_ENV", self.legacy)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_moves_and_deletes(self):
        self.legacy.write_text(f"GEMINI_API_KEY={SECRET}\n", encoding="utf-8")
        with mock.patch("builtins.print"):
            self.assertEqual(sk.migrate(self.target), 0)
        self.assertFalse(self.legacy.exists())
        self.assertEqual(sk.parse(sk.read_env(self.target))["GEMINI_API_KEY"], SECRET)

    def test_refuses_unknown_names_and_keeps_the_file(self):
        self.legacy.write_text("GEMINI_API_KEY=a\nOTHER_SECRET=b\n", encoding="utf-8")
        with mock.patch("builtins.print"):
            self.assertEqual(sk.migrate(self.target), 1)
        self.assertTrue(self.legacy.exists())
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
