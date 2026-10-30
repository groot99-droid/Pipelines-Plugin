"""pipeline/app_server.py: the loopback HTTP API and the allow-listed files of
the designer app (docs/CONTRACTS.md, F10 "HTTP").

The server runs in this process on an ephemeral port (`make_server(...,
port=0)`, the way the contract has tests override the port; the command line
never falls back to another port) and is called with http.client and raw
sockets. Its data is a library built in a temporary folder (test_service.World)
and its app folder is a temporary one, so nothing reads the real library,
catalog, vault or app. A last class starts the script as a program under
`python -I` and drives it from another directory.

    python -m unittest discover -s brushes/pipeline/tests -p "test_app_server.py"
"""

import ast
import base64
import http.client
import io
import json
import mimetypes
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path
from unittest import mock
from urllib.parse import quote, unquote

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import app_server  # noqa: E402
import brush_common as bc  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import fixtures  # noqa: E402
import mcp_server as ms  # noqa: E402
import service  # noqa: E402
import test_service as ts  # noqa: E402

BRUSHES = PIPELINE.parent
SCRIPT = PIPELINE / "app_server.py"
TOKEN = "test-token-0123456789abcdefghij"
SECRET = b"SECRET-OUTSIDE-THE-APP-FOLDER"
NAME = "Cont\u00e9 \U0001f4a7 6B \u6d53\u58a8"
REQUIRED_HEADERS = ("Content-Length", "Cache-Control", "X-Content-Type-Options", "Referrer-Policy",
                    "Cross-Origin-Resource-Policy")


class Raw(str):
    """A Host value sent exactly as given (a plain string names a kind)."""


class Response:
    def __init__(self, status, headers, body):
        self.status, self.headers, self.body = status, headers, body

    def json(self):
        return json.loads(self.body.decode("utf-8"))

    def error(self):
        return self.json()["error"]


def raw_exchange(port, data, *, shutdown=False, timeout=10):
    """Send bytes, read until the server closes: Response."""
    with socket.create_connection(("127.0.0.1", port), timeout=timeout) as sock:
        sock.sendall(data)
        if shutdown:
            sock.shutdown(socket.SHUT_WR)
        chunks = []
        while True:
            try:
                chunk = sock.recv(65536)
            except (ConnectionResetError, TimeoutError, socket.timeout):
                break
            if not chunk:
                break
            chunks.append(chunk)
    blob = b"".join(chunks)
    head, _, body = blob.partition(b"\r\n\r\n")
    lines = head.decode("iso-8859-1").split("\r\n")
    status = int(lines[0].split()[1]) if lines and lines[0].startswith("HTTP/") else 0
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    return Response(status, headers, body)


class ServerCase(ts.WorldCase):
    """One server on the shared synthetic world and a temporary app folder."""

    max_upload = service.MAX_UPLOAD

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.app = cls.tmp / "app"
        cls.outside = cls.tmp / "outside.txt"
        cls.outside.write_bytes(SECRET)
        cls.make_app(cls.app)
        paths = cls.world.paths._replace(app=cls.app)
        cls.errors = []
        cls.service = service.BrushService(paths)
        cls.server = app_server.make_server(cls.service, TOKEN, 0, max_upload=cls.max_upload, paths=paths,
                                            log=cls.errors.append)
        cls.port = cls.server.port
        cls.thread = threading.Thread(target=cls.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        cls.thread.start()
        cls.addClassCleanup(cls.stop_server)
        cls.before = ts.snapshot(cls.tmp)       # the app folder and the secret are part of the baseline

    @classmethod
    def stop_server(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(5)

    @staticmethod
    def make_app(app):
        (app / "sub").mkdir(parents=True)
        (app / ".hidden").mkdir()
        files = {
            "index.html": b"<!doctype html><title>t</title><script src=app.js></script>",
            "app.js": b"console.log(1)", "styles.css": b"body{}", "data.json": b"{}",
            "icon.svg": b"<svg xmlns='http://www.w3.org/2000/svg'/>", "pic.png": fixtures.make_png(),
            "font.woff2": b"wOF2....", "sub/deep.js": b"export default 1", "sub/page.html": b"<p>sub</p>",
            ".secret.js": b"hidden", ".hidden/inner.js": b"hidden", "notes.exe": b"MZ", "tool.py": b"print(1)",
            "no_extension": b"x", "with space.js": b"x", "caf\u00e9.js": b"x", "ro.bak": b"x",
        }
        for name, data in files.items():
            (app / name).write_bytes(data)
        with open(app / "big.js", "wb") as handle:                 # one byte over the 8 MiB cap
            handle.truncate(app_server.MAX_STATIC + 1)

    # ── calls ──
    def host(self, kind="localhost"):
        return {"localhost": f"localhost:{self.port}", "ip": f"127.0.0.1:{self.port}"}[kind]

    def call(self, method, path, *, token=True, host="localhost", headers=None, body=None, port=None,
             content_type=None, length=True):
        """A request with full control: `host` is a kind, a string, or None for no Host;
        `token` True sends the right one, a string sends that, False none."""
        port = port or self.port
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=15)
        try:
            connection.putrequest(method, path, skip_host=True, skip_accept_encoding=True)
            if host is not None:
                connection.putheader("Host", str(host) if isinstance(host, Raw) else
                                     self.host(host) if host in ("localhost", "ip") else host)
            if token is True:
                connection.putheader("X-ROSW-Token", TOKEN)
            elif token:
                connection.putheader("X-ROSW-Token", token)
            for name, value in (headers or {}).items():
                connection.putheader(name, value)
            if body is not None:
                if content_type:
                    connection.putheader("Content-Type", content_type)
                if length:
                    connection.putheader("Content-Length", str(len(body)))
            connection.endheaders(body if body is not None else None)
            response = connection.getresponse()
            return Response(response.status, {k.lower(): v for k, v in response.getheaders()}, response.read())
        finally:
            connection.close()

    def get(self, path, **kwargs):
        return self.call("GET", path, **kwargs)

    def post_json(self, path, payload, **kwargs):
        return self.call("POST", path, body=json.dumps(payload).encode("utf-8"),
                         content_type="application/json", **kwargs)

    def ident(self, name):
        return self.world.ids[name]

    def assertError(self, response, status, code):
        self.assertEqual(response.status, status, response.body[:300])
        self.assertEqual(response.headers["content-type"], "application/json")
        error = response.error()
        self.assertEqual(set(error), {"code", "message", "hint", "data"})
        self.assertEqual(error["code"], code)
        self.assertNotIn(TOKEN.encode(), response.body)
        self.assertTrue(response.body.isascii())
        return error

    def assertHeaders(self, response):
        for name in REQUIRED_HEADERS:
            self.assertIn(name.lower(), response.headers, name)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["referrer-policy"], "no-referrer")
        self.assertEqual(response.headers["cross-origin-resource-policy"], "same-origin")
        self.assertEqual(int(response.headers["content-length"]), len(response.body))
        for name, value in response.headers.items():
            self.assertTrue(value.isascii(), name)


# ── static files ─────────────────────────────────────────────────────────────

class Static(ServerCase):
    def test_the_page_needs_no_token_and_carries_the_policy(self):
        for path in ("/", "/index.html"):
            response = self.get(path, token=False)
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["content-type"], "text/html; charset=utf-8")
            self.assertEqual(response.body, (self.app / "index.html").read_bytes())
            self.assertHeaders(response)
            policy = response.headers["content-security-policy"]
            for part in ("default-src 'self'", "script-src 'self'", "style-src 'self'", "object-src 'none'",
                         "base-uri 'none'", "frame-ancestors 'none'", "form-action 'none'",
                         "connect-src 'self' http://localhost:* http://127.0.0.1:*", "worker-src 'self' blob:",
                         "img-src 'self' blob: data:"):
                self.assertIn(part, policy)
            self.assertNotIn("unsafe", policy)

    def test_only_html_gets_the_policy(self):
        self.assertNotIn("content-security-policy", self.get("/app.js", token=False).headers)

    def test_the_content_types_come_from_the_table_not_the_registry(self):
        expected = {"/app.js": "text/javascript; charset=utf-8", "/styles.css": "text/css; charset=utf-8",
                    "/data.json": "application/json; charset=utf-8", "/icon.svg": "image/svg+xml",
                    "/pic.png": "image/png", "/font.woff2": "font/woff2", "/sub/deep.js": "text/javascript; charset=utf-8",
                    "/sub/page.html": "text/html; charset=utf-8"}
        with mock.patch.dict(mimetypes.types_map, {".js": "text/plain", ".css": "text/plain"}):
            for path, content_type in expected.items():
                response = self.get(path, token=False)
                self.assertEqual((response.status, response.headers["content-type"]), (200, content_type), path)
                self.assertHeaders(response)

    def test_the_four_schema_files_are_served_and_no_others(self):
        for name in ("silica_keys.json", "facets.json"):
            response = self.get(f"/schema/{name}", token=False)
            self.assertEqual(response.status, 200, name)
            self.assertEqual(response.body, (BRUSHES / "schema" / name).read_bytes())
        for name in ("bundled_textures.json", "preview_calibration.json"):
            expected = (BRUSHES / "schema" / name).is_file()
            self.assertEqual(self.get(f"/schema/{name}", token=False).status, 200 if expected else 404, name)
        for path in ("/schema/patch_cases.json", "/schema/", "/schema", "/schema/../schema/silica_keys.json",
                     "/schema/nope.json", "/schema/SILICA_KEYS.JSON"):
            self.assertEqual(self.get(path, token=False).status, 404, path)

    def test_what_is_not_on_the_list_is_not_served(self):
        for path in ("/.secret.js", "/.hidden/inner.js", "/notes.exe", "/tool.py", "/no_extension", "/with%20space.js",
                     "/caf%C3%A9.js", "/ro.bak", "/big.js", "/sub/", "/sub", "/missing.js",
                     "/index.html/", "/INDEX.HTML", "/api", "/api/", "/favicon.ico"):
            response = self.get(path, token=False)
            self.assertIn(response.status, (404, 400), path)
            self.assertEqual(response.headers["content-type"], "application/json", path)
            self.assertNotIn(b"hidden", response.body, path)

    def test_a_file_added_after_the_start_is_not_served(self):
        late = self.app / "late.js"
        late.write_bytes(b"late")
        self.addCleanup(late.unlink)
        self.assertEqual(self.get("/late.js", token=False).status, 404)

    def test_no_directory_is_listed(self):
        for path in ("/sub/", "/sub", "/", "/schema/", "/.hidden/"):
            response = self.get(path, token=False)
            self.assertNotIn(b"Directory listing", response.body)
            self.assertNotIn(b"deep.js", response.body)

    def test_no_traversal_reaches_a_file_outside_the_list(self):
        paths = ["/../outside.txt", "/%2e%2e/outside.txt", "/%2E%2E%2Foutside.txt", "/..%2foutside.txt",
                 "/sub/../../outside.txt", "/sub/..%2f..%2foutside.txt", "/..\\outside.txt", "/%5c..%5coutside.txt",
                 "/sub%5c..%5c..%5coutside.txt", "//outside.txt", "///outside.txt", "/./outside.txt",
                 "/%2e/index.html", "/%2e%2e", "/..", "/sub/..", "/C:/Windows/win.ini", "/c%3a/windows/win.ini",
                 "/C%3A%5CWindows%5Cwin.ini", "/%00", "/index.html%00.png", "/index.html%00", "/app.js%00.json",
                 "/app_server.py", "/../pipeline/app_server.py", "/../spec.yaml", "/../../.mcp.json", "/.git/config",
                 "/app/../../outside.txt", "/%252e%252e/outside.txt", "/%2e%2e%5coutside.txt", "/sub/%2e%2e/index.html",
                 "/index.html/..%2f..%2foutside.txt", "/schema/..%2foutside.txt", "/schema/%2e%2e/outside.txt",
                 "/" + "a" * 3000]
        for path in paths:
            response = self.get(path, token=False)
            self.assertIn(response.status, (400, 404), path)
            self.assertNotIn(SECRET, response.body, path)
            self.assertNotIn(b"def main", response.body, path)
            self.assertEqual(response.headers["content-type"], "application/json", path)

    def test_raw_targets_a_client_would_not_send(self):
        for target in (b"/\x00", b"/index.html\x00.png", b"http://localhost/index.html",
                       b"*", b"index.html", b"/" + b"a" * 2100):
            response = raw_exchange(self.port, b"GET " + target + b" HTTP/1.0\r\nHost: localhost:%d\r\n\r\n" % self.port)
            self.assertIn(response.status, (400, 404, 414), target[:30])
            self.assertNotIn(b"<title>", response.body, target[:30])

    def test_a_link_or_junction_out_of_the_app_folder_is_not_followed(self):
        outside_dir = self.tmp / "outside-dir"
        outside_dir.mkdir()
        (outside_dir / "secret.js").write_bytes(SECRET)
        made = []
        link_dir, link_file = self.app / "linked-dir", self.app / "linked-file.js"
        if ts.make_link(link_dir, outside_dir, directory=True):
            made.append(link_dir)
        if ts.make_link(link_file, self.outside, directory=False):
            made.append(link_file)
        if not made:
            self.skipTest("this account can make neither a symbolic link nor a junction")
        server_paths = self.world.paths._replace(app=self.app)
        fresh = app_server.static_table(server_paths)
        try:
            self.assertNotIn("/linked-dir/secret.js", fresh)
            self.assertNotIn("/linked-file.js", fresh)
            self.assertIn("/app.js", fresh)
        finally:
            for link in made:
                try:
                    if link.is_dir() and not link.is_symlink():
                        os.rmdir(link)
                    else:
                        link.unlink()
                except OSError:
                    pass
            shutil.rmtree(outside_dir, ignore_errors=True)

    def test_the_table_is_walked_once_and_dev_walks_again(self):
        self.assertIn("/sub/deep.js", self.server.static)
        self.assertNotIn("/big.js", self.server.static)
        paths = self.world.paths._replace(app=self.app)
        dev = app_server.make_server(self.service, TOKEN, 0, dev=True, paths=paths)
        thread = threading.Thread(target=dev.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        late = self.app / "dev-late.js"
        try:
            self.assertEqual(self.get("/dev-late.js", token=False, port=dev.port, host=f"localhost:{dev.port}").status, 404)
            late.write_bytes(b"late")
            response = self.get("/dev-late.js", token=False, port=dev.port, host=f"localhost:{dev.port}")
            self.assertEqual((response.status, response.body), (200, b"late"))
        finally:
            late.unlink(missing_ok=True)
            dev.shutdown()
            dev.server_close()
            thread.join(5)

    def test_the_table_has_no_dot_file_and_every_name_is_plain_ascii(self):
        for url in self.server.static:
            self.assertTrue(url.isascii())
            self.assertFalse(any(part.startswith(".") for part in url.split("/")), url)
            self.assertNotIn(" ", url)
        self.assertTrue(all(Path(file).is_file() for file, _ in self.server.static.values()))


# ── the gate ─────────────────────────────────────────────────────────────────

class Gate(ServerCase):
    def test_only_get_and_post(self):
        for method in ("PUT", "DELETE", "PATCH", "OPTIONS", "HEAD", "TRACE", "FOO"):
            response = self.call(method, "/api/status")
            self.assertEqual(response.status, 405, method)
            if method != "HEAD":
                self.assertEqual(response.error()["code"], "method_not_allowed")
            self.assertEqual(response.headers["allow"], "GET, POST")
        self.assertEqual(self.call("PUT", "/index.html", token=False).status, 405)

    def test_the_host_must_be_localhost_or_127_0_0_1_on_this_port(self):
        for host in (None, "evil.example", "evil.example:%d" % self.port, "localhost", "127.0.0.1",
                     f"localhost:{self.port + 1}", f"127.0.0.1:{self.port + 1}", "[::1]:%d" % self.port,
                     f"localhost:{self.port}.evil.example", f"evil.localhost:{self.port}", "localhost:0",
                     f"localhost:{self.port}, evil.example", f"0.0.0.0:{self.port}", " ", "1.2.3.4:%d" % self.port):
            for path in ("/", "/api/status", "/api/nope", "/index.html", "/app.js"):
                response = self.get(path, host=None if host is None else Raw(host))
                self.assertError(response, 403, "bad_host")
        both = raw_exchange(self.port, (f"GET /api/status HTTP/1.0\r\nHost: localhost:{self.port}\r\n"
                                       f"Host: evil.example\r\nX-ROSW-Token: {TOKEN}\r\n\r\n").encode())
        self.assertEqual((both.status, both.json()["error"]["code"]), (403, "bad_host"))

    def test_both_allowed_hosts_are_served_whatever_their_case(self):
        for host in (f"localhost:{self.port}", f"127.0.0.1:{self.port}", f"LOCALHOST:{self.port}"):
            self.assertEqual(self.get("/api/status", host=host).status, 200, host)
            self.assertEqual(self.get("/", host=host, token=False).status, 200, host)

    def test_the_origin_when_sent_must_be_the_page_itself(self):
        for origin in ("http://evil.example", "null", "https://localhost:%d" % self.port,
                       f"http://localhost:{self.port + 1}", f"http://localhost.evil.example:{self.port}",
                       f"http://evil.example:{self.port}", "", f"http://localhost:{self.port}/", "*"):
            self.assertError(self.get("/api/status", headers={"Origin": origin}), 403, "bad_origin")
            self.assertError(self.get("/", token=False, headers={"Origin": origin}), 403, "bad_origin")
        for origin in (f"http://localhost:{self.port}", f"http://127.0.0.1:{self.port}"):
            self.assertEqual(self.get("/api/status", headers={"Origin": origin}).status, 200)
        self.assertEqual(self.get("/api/status").status, 200, "no Origin is fine: a same-origin GET sends none")

    def test_sec_fetch_site_when_sent_is_same_origin_or_none(self):
        for site in ("cross-site", "same-site", "", "Cross-Site", "bogus"):
            self.assertError(self.get("/api/status", headers={"Sec-Fetch-Site": site}), 403, "cross_site")
        for site in ("same-origin", "none"):
            self.assertEqual(self.get("/api/status", headers={"Sec-Fetch-Site": site}).status, 200)

    def test_the_gate_runs_in_the_documented_order(self):
        evil = {"Origin": "http://evil.example", "Sec-Fetch-Site": "cross-site"}
        self.assertEqual(self.get("/api/nope", host="evil.example", headers=evil, token="bad").error()["code"], "bad_host")
        self.assertEqual(self.get("/api/nope", headers=evil, token="bad").error()["code"], "bad_origin")
        self.assertEqual(self.get("/api/nope", headers={"Sec-Fetch-Site": "cross-site"}, token="bad")
                         .error()["code"], "cross_site")
        self.assertEqual(self.get("/api/nope", token="bad").error()["code"], "not_found", "the route is looked up first")
        self.assertEqual(self.get("/api/status", token="bad").error()["code"], "bad_token")
        self.assertEqual(self.call("DELETE", "/api/status", host="evil.example").status, 405,
                         "the method is the first check")

    def test_the_token_is_needed_for_every_api_route(self):
        examples = {
            "/api/status": None, "/api/search": None, "/api/facets": None, "/api/vocabulary": None,
            "/api/sets": None, f"/api/sets/demo-set": None, f"/api/brush/{self.ident('inker')}": None,
            f"/api/brush/{self.ident('inker')}/similar": None, f"/api/brush/{self.ident('inker')}/open": None,
            f"/api/preview/{self.ident('inker')}/stroke.png": None, "/api/app-source.zip": None,
            "/api/similar": b"{}", "/api/import": b"x", "/api/validate-patch": b"{}", "/api/export": b"{}",
            "/api/quit": b"{}"}
        self.assertEqual(len(app_server.ROUTES), len(examples))
        for path, body in examples.items():
            for token in (False, "", "wrong", TOKEN[:-1], TOKEN + "x", TOKEN.upper(), "\u00e9\u00e8" * 8):
                if body is None:
                    response = self.get(path, token=token)
                else:
                    ctype = "application/octet-stream" if path == "/api/import" else "application/json"
                    response = self.call("POST", path, token=token, body=body, content_type=ctype)
                self.assertError(response, 403, "bad_token")
        self.assertEqual(self.get("/api/status?token=" + TOKEN, token=False).error()["code"], "bad_token",
                         "a token in the URL is not a token")
        self.assertEqual(self.get("/api/status?token=" + TOKEN).error()["code"], "bad_argument",
                         "and it is not a parameter either")
        self.assertEqual(self.get("/api/status", token=False, headers={"Authorization": TOKEN}).status, 403)

    def test_a_refused_post_is_answered_after_its_body_is_read_so_the_client_sees_the_reply(self):
        """Answering and closing with the body unread can reset the connection
        before the client reads the 403; the server reads the body first."""
        body = bytes(300 * 1024)
        for number in range(25):
            response = self.call("POST", "/api/import", token="wrong", body=body,
                                 content_type="application/octet-stream")
            self.assertError(response, 403, "bad_token")
            wrong_host = self.call("POST", "/api/export", host="evil.example", body=body,
                                   content_type="application/json")
            self.assertError(wrong_host, 403, "bad_host")
            unknown = self.call("POST", "/api/nope", body=body, content_type="application/json")
            self.assertError(unknown, 404, "not_found")

    def test_a_non_ascii_token_header_is_refused_without_a_crash(self):
        response = raw_exchange(self.port, (f"GET /api/status HTTP/1.0\r\nHost: localhost:{self.port}\r\n"
                                           "X-ROSW-Token: ").encode() + "\u00e9\u4e2d".encode("utf-8") + b"\r\n\r\n")
        self.assertEqual((response.status, response.json()["error"]["code"]), (403, "bad_token"))
        self.assertEqual(self.get("/api/status").status, 200, "the server is still up")

    def test_the_token_is_never_in_a_static_file_or_an_error(self):
        for path in ("/", "/app.js", "/index.html", "/data.json"):
            self.assertNotIn(TOKEN.encode(), self.get(path, token=False).body)
        for path in ("/api/nope", "/api/status?bogus=1"):
            self.assertNotIn(TOKEN.encode(), self.get(path).body)

    def test_unknown_routes_and_wrong_methods(self):
        self.assertError(self.get("/api/nope"), 404, "not_found")
        self.assertError(self.get("/api/brush/b_0123456789a"), 404, "not_found")
        self.assertError(self.get("/api/brush/B_0123456789AB"), 404, "not_found")
        self.assertError(self.get("/api/brush/b_0123456789ab/extra"), 404, "not_found")
        self.assertError(self.get("/api/brush/..%2fb_0123456789ab"), 404, "not_found")
        self.assertError(self.get("/api/sets/Demo%20Set"), 404, "not_found")
        self.assertError(self.get(f"/api/preview/{self.ident('inker')}/thumbnail.png"), 404, "not_found")
        self.assertError(self.get(f"/api/preview/{self.ident('inker')}/stroke"), 404, "not_found")
        self.assertError(self.call("POST", "/api/status", body=b"{}", content_type="application/json"),
                         405, "method_not_allowed")
        self.assertError(self.get("/api/export"), 405, "method_not_allowed")
        self.assertError(self.get("/api/quit"), 405, "method_not_allowed")
        self.assertEqual(self.get("/api/status").status, 200, "a GET /api/quit did not stop the server")

    def test_the_target_is_checked(self):
        self.assertError(self.get("/api/status?" + "a=1&" * 600), 400, "bad_request")
        self.assertError(self.get("/api/search?q=" + "x" * 2100), 400, "bad_request")

    def test_a_dropped_connection_does_not_stop_the_server(self):
        for data in (b"GET /api/status HT", b"", b"\x16\x03\x01\x02\x00\x01\x00\x01\xfc\x03\x03", b"GET"):
            with socket.create_connection(("127.0.0.1", self.port), timeout=5) as sock:
                sock.sendall(data)
        self.assertEqual(self.get("/api/status").status, 200)


# ── bodies ───────────────────────────────────────────────────────────────────

class Bodies(ServerCase):
    def test_a_post_needs_a_content_length(self):
        head = f"POST /api/validate-patch HTTP/1.0\r\nHost: localhost:{self.port}\r\nX-ROSW-Token: {TOKEN}\r\n"
        response = raw_exchange(self.port, (head + "Content-Type: application/json\r\n\r\n{}").encode(), shutdown=True)
        self.assertEqual((response.status, response.json()["error"]["code"]), (411, "length_required"))
        chunked = raw_exchange(self.port, (head + "Content-Type: application/json\r\nTransfer-Encoding: chunked\r\n\r\n"
                                           "2\r\n{}\r\n0\r\n\r\n").encode(), shutdown=True)
        self.assertEqual((chunked.status, chunked.json()["error"]["code"]), (411, "length_required"))
        for length in ("abc", "-1", "1e3", " ", "99999999999999999"):
            odd = raw_exchange(self.port, (head + f"Content-Type: application/json\r\nContent-Length: {length}\r\n\r\n{{}}")
                               .encode(), shutdown=True)
            self.assertIn(odd.status, (411, 413, 400), length)

    def test_a_body_over_the_routes_cap_is_413(self):
        patch_cap = service.MAX_PATCH_JSON
        body = b" " * (patch_cap + 1)
        for path in ("/api/validate-patch", "/api/similar"):
            response = self.call("POST", path, body=body, content_type="application/json")
            self.assertError(response, 413, "too_large")
        quit_body = b" " * 2000
        self.assertError(self.call("POST", "/api/quit", body=quit_body, content_type="application/json"),
                         413, "too_large")
        self.assertEqual(self.get("/api/status").status, 200, "and the server is still there")

    def test_a_short_body_is_a_bad_request_not_a_hang(self):
        head = (f"POST /api/validate-patch HTTP/1.0\r\nHost: localhost:{self.port}\r\nX-ROSW-Token: {TOKEN}\r\n"
                "Content-Type: application/json\r\nContent-Length: 500\r\n\r\n{}")
        response = raw_exchange(self.port, head.encode(), shutdown=True)
        self.assertEqual(response.status, 400)

    def test_the_content_type_is_checked(self):
        for path, wrong, right in (("/api/validate-patch", "text/plain", "application/json"),
                                   ("/api/validate-patch", "application/octet-stream", "application/json"),
                                   ("/api/validate-patch", "", "application/json"),
                                   ("/api/import", "application/json", "application/octet-stream"),
                                   ("/api/export", "multipart/form-data", "application/json")):
            response = self.call("POST", path, body=b"{}", content_type=wrong or None)
            self.assertError(response, 415, "unsupported_file")
        ok = self.call("POST", "/api/validate-patch", body=b'{"changes": {}}', content_type="Application/JSON; charset=utf-8")
        self.assertEqual(ok.status, 200)

    def test_json_bodies_are_checked(self):
        for body in (b"{", b"", b"not json", b"[]", b'"x"', b"null", b"1", b'{"changes": NaN}', b"\xff\xfe{}",
                     b'{"changes": {}} trailing', b"[" * 100000):
            response = self.call("POST", "/api/validate-patch", body=body, content_type="application/json")
            self.assertError(response, 400, "bad_json")
        for path in ("/api/export", "/api/similar"):
            self.assertError(self.call("POST", path, body=b"{broken", content_type="application/json"), 400, "bad_json")

    def test_a_field_a_route_does_not_take_is_refused(self):
        self.assertError(self.post_json("/api/validate-patch", {"changes": {}, "mode": "x"}), 400, "bad_argument")
        self.assertError(self.post_json("/api/similar", {"settings": {"a": 1}, "evil": 1}), 400, "bad_argument")

    def test_an_upload_over_the_cap_is_413(self):
        small = app_server.make_server(self.service, TOKEN, 0, max_upload=1024, paths=self.server.paths)
        thread = threading.Thread(target=small.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        try:
            host = f"localhost:{small.port}"
            ok = self.call("POST", "/api/import", port=small.port, host=host, body=b"x" * 1024,
                           content_type="application/octet-stream")
            self.assertEqual(ok.status, 415, "1024 bytes are within the cap; the file is not a brush")
            over = self.call("POST", "/api/import", port=small.port, host=host, body=b"x" * 1025,
                             content_type="application/octet-stream")
            self.assertError(over, 413, "too_large")
            status = self.call("GET", "/api/status", port=small.port, host=host).json()
            self.assertEqual(status["caps"]["max_upload_bytes"], 1024)
        finally:
            small.shutdown()
            small.server_close()
            thread.join(5)


# ── the routes ───────────────────────────────────────────────────────────────

class Routes(ServerCase):
    def test_status_is_the_library_status_plus_caps_and_the_new_brush_era(self):
        response = self.get("/api/status")
        self.assertHeaders(response)
        status = response.json()
        expected = self.service.status()
        for key in expected:
            self.assertEqual(status[key], expected[key], key)
        self.assertEqual(set(status) - set(expected), {"caps", "new_brush_era", "new_brush_eras"})
        self.assertEqual(status["new_brush_era"], brush_model.NEW_BRUSH_ERA)
        self.assertEqual(status["caps"]["max_upload_bytes"], service.MAX_UPLOAD)
        self.assertEqual(status["caps"]["container"]["zip_entries"], 5000)
        self.assertEqual(status["counts"]["brushes"], 8)
        self.assertNotIn("stub", status)
        self.assertEqual(response.headers["content-type"], "application/json")

    def test_search(self):
        envelope = self.get("/api/search?q=conte").json()
        self.assertEqual(envelope["results"][0]["brush_id"], self.ident("conte"))
        browse = self.get("/api/search").json()
        self.assertEqual((browse["ranking"], browse["total"], len(browse["results"])), ("filter-order", 8, 8))
        self.assertEqual(len(self.get("/api/search?top=3&offset=2").json()["results"]), 3)
        by_filter = self.get("/api/search?where=kind%3Dstamp&where_not=library%3Dofficial").json()
        self.assertEqual([r["brush_id"] for r in by_filter["results"]], [self.ident("inker2")])
        self.assertEqual(self.get("/api/search?where=kind%3Dstroke&where=library%3Dofficial").json()["total"], 3,
                         "repeated filters are ANDed")

    def test_search_arguments_are_checked(self):
        for query in ("top=9999", "top=0", "top=abc", "top=-1", "top=1.5", "top=%2B5", "top=1&top=2", "offset=-1",
                      "offset=x", "offset=99999999999", "q=a&q=b", "bogus=1", "tag=medium", "tag=colour%3Dred",
                      "tag=texture%3Dnope", "where=nope%3D1", "where=" + "x" * 130, "q=" + "x" * 501, "q=a%00b"):
            response = self.get("/api/search?" + query)
            self.assertError(response, 400, "bad_argument")
        self.assertEqual(self.get("/api/search?top=200").status, 200)

    def test_facets_vocabulary_and_sets(self):
        facets = self.get("/api/facets").json()
        self.assertEqual(facets["brushes"], 8)
        self.assertEqual(self.get("/api/facets?where=kind%3Dstamp").json()["brushes"], 1)
        self.assertEqual(self.get("/api/vocabulary").json(), self.service.vocabulary())
        sets = self.get("/api/sets").json()["sets"]
        self.assertEqual({s["set_slug"] for s in sets}, {"demo-set", "demo-modern", "demo-pack-loose"})
        self.assertEqual([s["set_slug"] for s in self.get("/api/sets?library=official").json()["sets"]], ["demo-modern"])
        self.assertError(self.get("/api/sets?library=both"), 400, "bad_argument")
        one = self.get("/api/sets/demo-set").json()
        self.assertEqual([r["brush_id"] for r in one["brushes"]],
                         [self.ident(n) for n in ("inker", "pencil", "conte", "inker2")])
        self.assertError(self.get("/api/sets/no-such-set"), 404, "unknown_id")

    def test_the_names_in_a_reply_travel_as_ascii(self):
        response = self.get("/api/sets?library=official")
        self.assertTrue(response.body.isascii())
        self.assertEqual(response.json()["sets"][0]["name"], "\u6d53\u58a8 Modern 1")

    def test_one_brush(self):
        brush = self.get(f"/api/brush/{self.ident('dual')}").json()
        self.assertEqual((brush["name"], brush["dual"]["name"]), ("Modern Dual", "Modern Dual Secondary"))
        self.assertNotIn("settings", brush)
        self.assertIn("settings", self.get(f"/api/brush/{self.ident('dual')}?include=settings,note").json())
        self.assertNotIn("facets", self.get(f"/api/brush/{self.ident('dual')}?include=settings").json())
        self.assertError(self.get(f"/api/brush/{self.ident('dual')}?include=everything"), 400, "bad_argument")
        self.assertError(self.get("/api/brush/b_000000000000"), 404, "unknown_id")

    def test_similar(self):
        found = self.get(f"/api/brush/{self.ident('inker')}/similar?top=3").json()
        self.assertEqual((found["method"], len(found["results"])), ("gower-v1", 3))
        self.assertError(self.get(f"/api/brush/{self.ident('inker')}/similar?top=0"), 400, "bad_argument")
        self.assertError(self.get("/api/brush/b_000000000000/similar"), 404, "unknown_id")
        by_settings = self.post_json("/api/similar", {"settings": {"plotSpacing": 0.1}, "top": 2})
        self.assertEqual((by_settings.status, len(by_settings.json()["results"])), (200, 2))
        self.assertEqual(by_settings.json()["query"]["brush_id"], None)
        for payload in ({}, {"settings": {}}, {"settings": []}, {"settings": {"a": 1}, "top": 0},
                        {"settings": {"a": 1}, "where": ["nope=1"]}):
            self.assertError(self.post_json("/api/similar", payload), 400, "bad_argument")

    def test_open_gives_the_library_original(self):
        response = self.get(f"/api/brush/{self.ident('inker')}/open")
        brush = response.json()
        original = self.world.brushes["inker"]
        self.assertEqual((brush["kind"], brush["name"], brush["library_id"]), ("brush", "Demo Inker", self.ident("inker")))
        self.assertEqual(base64.b64decode(brush["textures"]["shape"]["png_b64"]), original.shape)
        self.assertEqual({m["path"]: base64.b64decode(m["b64"]) for m in brush["base"]["members"]},
                         dict(original.members))
        light = self.get(f"/api/brush/{self.ident('inker')}/open?textures=none").json()
        self.assertEqual(light["base"], {"library_id": self.ident("inker")})
        self.assertError(self.get(f"/api/brush/{self.ident('inker')}/open?textures=huge"), 400, "bad_argument")
        self.assertError(self.get("/api/brush/b_000000000000/open"), 404, "unknown_id")

    def test_a_missing_library_is_409_on_open(self):
        world = self.copy_world(library=False)
        server = app_server.make_server(world.service(), TOKEN, 0, paths=world.paths)
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        try:
            response = self.get(f"/api/brush/{world.ids['inker']}/open", port=server.port,
                                host=f"localhost:{server.port}")
            self.assertError(response, 409, "library_missing")
            self.assertEqual(self.get("/api/search?q=conte", port=server.port, host=f"localhost:{server.port}").status, 200)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(5)

    def test_previews_are_the_stored_files(self):
        response = self.get(f"/api/preview/{self.ident('inker')}/stroke.png")
        path = self.world.paths.previews / "demo-set" / f"{self.ident('inker')}.stroke.png"
        self.assertEqual((response.status, response.headers["content-type"], response.body),
                         (200, "image/png", path.read_bytes()))
        self.assertHeaders(response)
        self.assertEqual(self.get(f"/api/preview/{self.ident('inker')}/shape.png").status, 200)
        self.assertError(self.get(f"/api/preview/{self.ident('pencil')}/shape.png"), 404, "no_preview")
        self.assertError(self.get("/api/preview/b_000000000000/stroke.png"), 404, "unknown_id")

    def test_a_preview_path_in_the_catalog_that_leaves_the_previews_folder_is_no_preview(self):
        world = self.copy_world()
        record_path = world.paths.catalog / "brushes" / f"{world.ids['inker']}.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["preview"]["stroke"] = "../../outside.txt"
        record_path.write_text(json.dumps(record), encoding="utf-8", newline="\n")
        (world.root.parent / "outside.txt").write_bytes(SECRET)
        server = app_server.make_server(world.service(), TOKEN, 0, paths=world.paths)
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        try:
            response = self.get(f"/api/preview/{world.ids['inker']}/stroke.png", port=server.port,
                                host=f"localhost:{server.port}")
            self.assertError(response, 404, "no_preview")
            self.assertNotIn(SECRET, response.body)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(5)

    def test_the_service_is_not_called_for_an_id_the_route_refuses(self):
        with mock.patch.object(service.BrushService, "get_brush") as get_brush, \
                mock.patch.object(service.BrushService, "preview") as preview:
            for path in ("/api/brush/..%2f..%2fetc%2fpasswd", "/api/brush/b_xyz", "/api/preview/..%2fx/stroke.png",
                         "/api/preview/b_0123456789ab/..%2fstroke.png", "/api/brush/b_0123456789ab%00"):
                self.assertIn(self.get(path).status, (400, 404), path)
            get_brush.assert_not_called()
            preview.assert_not_called()

    def test_the_app_source_is_the_allow_listed_files_in_a_zip(self):
        response = self.get("/api/app-source.zip")
        self.assertEqual((response.status, response.headers["content-type"]), (200, "application/zip"))
        self.assertIn("attachment", response.headers["content-disposition"])
        with zipfile.ZipFile(io.BytesIO(response.body)) as archive:
            names = sorted(archive.namelist())
            self.assertEqual(names, sorted(url.lstrip("/") for url in self.server.static))
            for url, (file, _) in self.server.static.items():
                self.assertEqual(archive.read(url.lstrip("/")), file.read_bytes(), url)
        self.assertNotIn(".secret.js", names)
        self.assertIn("schema/silica_keys.json", names)

    def test_validate_patch_is_the_same_function_over_http_and_mcp(self):
        arguments = {"changes": {"plotSpacing": 0.25, "stamp": True, "nope": 1}, "base_id": self.ident("inker")}
        over_http = self.post_json("/api/validate-patch", arguments)
        self.assertEqual(over_http.status, 200)
        context = ms.make_context(self.world.paths)
        via_mcp = ms.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "validate_settings_patch", "arguments": arguments}}, context)
        self.assertEqual(over_http.json(), json.loads(via_mcp["result"]["content"][0]["text"]))
        self.assertFalse(over_http.json()["ok"])
        self.assertError(self.post_json("/api/validate-patch", {}), 400, "bad_argument")
        self.assertError(self.post_json("/api/validate-patch", {"changes": {}, "base_id": "b_000000000000"}),
                         404, "unknown_id")

    def test_search_is_the_same_envelope_over_http_and_mcp(self):
        context = ms.make_context(self.world.paths)
        via_mcp = ms.dispatch({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "search_brushes", "arguments": {"query": "inker", "top": 8}}}, context)
        over_http = self.get("/api/search?q=inker&top=8").json()
        self.assertEqual(over_http, json.loads(via_mcp["result"]["content"][0]["text"]))

    def test_nothing_is_written_by_any_route(self):
        before = ts.snapshot(self.tmp)
        i = self.ident
        for path in ("/api/status", "/api/search?q=ink", "/api/facets", "/api/vocabulary", "/api/sets",
                     "/api/sets/demo-set", f"/api/brush/{i('dual')}", f"/api/brush/{i('dual')}/similar",
                     f"/api/brush/{i('dual')}/open", f"/api/preview/{i('dual')}/stroke.png", "/api/app-source.zip"):
            self.assertEqual(self.get(path).status, 200, path)
        self.post_json("/api/export", {"format": "brush", "brushes": [{"base": {"library_id": i("dual")}}]})
        self.assertEqual(ts.snapshot(self.tmp), before)

    def test_parallel_requests(self):
        results = []

        def work():
            results.append(self.get("/api/search?q=inker").status)

        threads = [threading.Thread(target=work) for _ in range(12)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(30)
        self.assertEqual(results, [200] * 12)

    def test_an_unexpected_error_is_500_internal_with_no_detail_and_is_logged(self):
        with mock.patch.object(service.BrushService, "list_sets", side_effect=RuntimeError("secret detail")):
            response = self.get("/api/sets")
        error = self.assertError(response, 500, "internal")
        self.assertNotIn("secret", json.dumps(error))
        self.assertIn("secret detail", "".join(self.errors))
        self.assertEqual(self.get("/api/status").status, 200)


# ── import and export ────────────────────────────────────────────────────────

class ImportExport(ServerCase):
    def setUp(self):
        super().setUp()
        self.set_bytes = (self.world.paths.library / "user" / "demo-pack" / "Demo_Set.brushset").read_bytes()

    def upload(self, data, query="", headers=None):
        return self.call("POST", "/api/import" + query, body=data, content_type="application/octet-stream",
                         headers=headers)

    def test_a_set_gives_a_manifest_and_a_member_gives_a_brush(self):
        manifest = self.upload(self.set_bytes, headers={"X-ROSW-Filename": quote("Demo \U0001f4a7 Set.brushset")}).json()
        self.assertEqual((manifest["kind"], manifest["brush_count"]), ("brushset", 4))
        member = manifest["brushes"][1]["member"]
        brush = self.upload(self.set_bytes, "?member=" + quote(member, safe="")).json()
        self.assertEqual((brush["kind"], brush["name"]), ("brush", "Demo  Pencil"))
        self.assertEqual(self.upload(self.set_bytes, "?member=" + quote(member, safe="") + "&textures=none")
                         .json()["textures"]["thumbnail"], {"present": True})
        self.assertError(self.upload(self.set_bytes, "?member=nope"), 400, "bad_argument")
        self.assertError(self.upload(self.set_bytes, "?textures=big"), 400, "bad_argument")

    def test_garbage_and_hostile_files(self):
        self.assertError(self.upload(b"not a brush file at all"), 415, "unsupported_file")
        self.assertError(self.upload(fixtures.make_zip([("a.txt", b"x")])), 415, "unsupported_file")
        self.assertEqual(self.upload(fixtures.LFS_POINTER).status, 409)
        before = ts.snapshot(self.tmp)
        for name, data in fixtures.hostile_files().items():
            response = self.upload(data, headers={"X-ROSW-Filename": quote(name)})
            self.assertIn(response.status, (200, 415, 422, 409), name)
            self.assertTrue(response.body.isascii())
        bomb = self.upload(fixtures.ratio_bomb(20))
        self.assertError(bomb, 422, "corrupt_file")
        self.assertEqual(ts.snapshot(self.tmp), before, "an import creates nothing")
        self.assertFalse((self.tmp / "outside.txt").read_bytes() != SECRET)

    def test_an_unedited_import_exports_an_archive_byte_equal_to_the_original(self):
        original = self.world.brushes["marker"]
        brush = self.upload((self.world.paths.library / "user" / "demo-pack" / "Loose_Marker.brush").read_bytes()).json()
        self.assertEqual(brush["kind"], "brush")
        response = self.post_json("/api/export", {"format": "brush", "brushes": [{
            "base": {"members": brush["base"]["members"]}, "changes": {},
            "textures": {"shape": {"keep": True}, "grain": {"keep": True}}, "thumbnail": {"keep": True}}]})
        self.assertEqual(response.status, 200, response.body[:300])
        members = dict(fixtures.zip_entries(response.body))
        self.assertEqual(members[container.ARCHIVE], original.archive)
        self.assertEqual(members, dict(original.members))

    def test_export_returns_the_file_with_ascii_headers(self):
        response = self.post_json("/api/export", {"format": "brush", "brushes": [{
            "base": {"library_id": self.ident("inker")}, "changes": {"name": NAME, "plotSpacing": 0.25}}]})
        self.assertEqual((response.status, response.headers["content-type"]), (200, "application/octet-stream"))
        self.assertHeaders(response)
        disposition = response.headers["content-disposition"]
        self.assertEqual(disposition, 'attachment; filename="conte-6b.brush"; filename*=UTF-8\'\'' + quote(NAME + ".brush", safe=""))
        self.assertEqual(unquote(disposition.split("filename*=UTF-8''")[1]), NAME + ".brush")
        info = json.loads(unquote(response.headers["x-rosw-export"]))
        self.assertEqual(set(info), {"filename", "size", "sha256", "brushes", "warnings"})
        self.assertEqual((info["filename"], info["size"]), ("conte-6b.brush", len(response.body)))
        import hashlib
        self.assertEqual(info["sha256"], hashlib.sha256(response.body).hexdigest())
        folder = container.read_brush(response.body)
        self.assertEqual(brush_model.decode(folder.archive).name, NAME)

    def test_dry_run_is_json_and_builds_no_download(self):
        response = self.post_json("/api/export", {"format": "brush", "dry_run": True, "brushes": [{
            "base": {"library_id": self.ident("dual")}, "changes": {"plotSpacing": 0.25}}]})
        self.assertEqual((response.status, response.headers["content-type"]), (200, "application/json"))
        report = response.json()
        self.assertEqual(list(report), ["filename", "size", "sha256", "members", "brushes", "warnings"])
        self.assertEqual({m["state"] for m in report["members"]}, {"verbatim", "re-encoded"})
        self.assertNotIn("content-disposition", response.headers)

    def test_rejected_settings_are_422_with_the_list(self):
        for mode in ("strict", "clamp"):
            response = self.post_json("/api/export", {"format": "brush", "brushes": [{
                "base": {"library_id": self.ident("inker")}, "mode": mode, "changes": {"nope": 1}}]})
            error = self.assertError(response, 422, "invalid_settings")
            self.assertEqual(error["data"]["rejected"][0]["code"], "unknown_key")

    def test_every_format(self):
        brushset = self.post_json("/api/export", {"format": "brushset", "name": "\U0001f4a7", "brushes": [
            {"base": {"library_id": self.ident("inker")}}, {"base": {"library_id": self.ident("dual")}}]})
        self.assertEqual(brushset.status, 200)
        self.assertEqual(container.read_brushset(brushset.body).name, "\U0001f4a7")
        self.assertIn('filename="untitled.brushset"', brushset.headers["content-disposition"])
        self.assertIn("filename*=UTF-8''%F0%9F%92%A7.brushset", brushset.headers["content-disposition"])
        gbr_file = self.post_json("/api/export", {"format": "gbr", "brushes": [{"base": {"library_id": self.ident("inker")}}]})
        self.assertEqual((gbr_file.status, gbr_file.body[28:32] == b"GIMP" or gbr_file.body[20:24] == b"GIMP"), (200, True))
        kit = self.post_json("/api/export", {"format": "kit", "name": "k", "files": [
            {"path": "brush-recipe.md", "b64": base64.b64encode(b"# r").decode()}]})
        self.assertEqual((kit.status, zipfile.ZipFile(io.BytesIO(kit.body)).namelist()), (200, ["brush-recipe.md"]))
        self.assertEqual(kit.headers["content-type"], "application/octet-stream")

    def test_a_bad_export_request_is_400(self):
        for payload in ({}, {"format": "zip"}, {"format": "brush", "brushes": []},
                        {"format": "brush", "brushes": [{"base": {"library_id": "nope"}}]},
                        {"format": "brush", "brushes": [{"base": {"library_id": self.ident("inker")}, "uuid": "x"}]},
                        {"format": "kit", "files": [{"path": "../x.png", "b64": "QQ=="}]}):
            self.assertError(self.post_json("/api/export", payload), 400, "bad_argument")
        self.assertError(self.post_json("/api/export", {"format": "brush", "brushes": [
            {"base": {"library_id": "b_000000000000"}}]}), 404, "unknown_id")

    def test_the_new_brush_template_needs_the_library_donor(self):
        self.assertError(self.post_json("/api/export", {"format": "brush", "brushes": [{"base": None}]}),
                         409, "library_missing")


# ── quit and the start ───────────────────────────────────────────────────────

class Quit(ts.WorldCase):
    def test_quit_stops_the_server_after_answering(self):
        server = app_server.make_server(self.world.service(), TOKEN, 0, paths=self.world.paths._replace(app=self.tmp))
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        host = {"Host": f"localhost:{server.port}", "X-ROSW-Token": TOKEN, "Content-Type": "application/json"}
        connection = http.client.HTTPConnection("127.0.0.1", server.port, timeout=10)
        connection.request("POST", "/api/quit", body=b"{}", headers=host)
        response = connection.getresponse()
        self.assertEqual((response.status, json.loads(response.read())), (200, {"ok": True}))
        thread.join(10)
        self.assertFalse(thread.is_alive())
        self.assertTrue(server.quit_requested)
        server.server_close()
        with self.assertRaises(OSError):
            socket.create_connection(("127.0.0.1", server.port), timeout=2).close()


class Starting(ts.WorldCase):
    def test_the_defaults_are_the_documented_ones(self):
        self.assertEqual(bc.APP_PORT, 8719)
        args = app_server.build_parser().parse_args([])
        self.assertEqual((args.port, args.no_browser, args.dev), (8719, False, False))
        self.assertEqual(app_server.BIND, "127.0.0.1")
        server = app_server.make_server(self.world.service(), TOKEN, 0, paths=self.world.paths)
        try:
            self.assertEqual(server.server_address[0], "127.0.0.1")
            self.assertEqual(server.url(), f"http://localhost:{server.port}/#t={TOKEN}")
        finally:
            server.server_close()

    def test_a_busy_port_is_exit_2_and_never_another_port(self):
        holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(holder.close)
        if sys.platform == "win32" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            holder.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        holder.bind(("127.0.0.1", 0))
        holder.listen(1)
        port = holder.getsockname()[1]
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", err), \
                mock.patch.object(app_server.webbrowser, "open") as browser:
            code = app_server.main(["--port", str(port), "--no-browser", "--root", str(self.world.root)])
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertEqual(out.getvalue(), "")
        self.assertIn(str(port), err.getvalue())
        self.assertIn("never falls back", err.getvalue())
        browser.assert_not_called()
        with self.assertRaises(OSError):
            app_server.make_server(self.world.service(), TOKEN, port, paths=self.world.paths)

    def test_bad_ports_are_usage_errors(self):
        for argv in (["--port", "70000"], ["--port", "-1"]):
            with mock.patch.object(sys, "stderr", io.StringIO()):
                self.assertEqual(app_server.main(argv + ["--root", str(self.world.root)]), bc.EXIT_USAGE)
        with mock.patch.object(sys, "stderr", io.StringIO()):
            with self.assertRaises(SystemExit) as stopped:
                app_server.main(["--port", "abc"])
        self.assertEqual(stopped.exception.code, 2)

    def test_the_flags_are_the_specs(self):
        options = {flag for action in app_server.build_parser()._actions for flag in action.option_strings}
        self.assertEqual(options - set(bc.FLAGS.values()), {"-h", "--help", "--port", "--no-browser", "--dev"})

    def test_a_second_server_cannot_share_the_port(self):
        first = app_server.make_server(self.world.service(), TOKEN, 0, paths=self.world.paths)
        try:
            with self.assertRaises(OSError):
                app_server.make_server(self.world.service(), TOKEN, first.port, paths=self.world.paths)
        finally:
            first.server_close()


class AsAProgram(ts.WorldCase):
    """The script as `python -I` runs it, from another directory."""

    def start(self, *args, script=SCRIPT):
        self.cwd = Path(tempfile.mkdtemp(prefix="brushes-app-cwd-")).resolve()
        self.addCleanup(shutil.rmtree, self.cwd, ignore_errors=True)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith(fixtures.ENV_PREFIX)}
        process = subprocess.Popen([sys.executable, "-I", str(script), "--port", "0", "--no-browser",
                                    "--root", str(self.world.root), *args], cwd=str(self.cwd), env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(self.reap, process)
        line = process.stdout.readline().decode("utf-8").rstrip("\r\n")
        match = re.fullmatch(r"Open http://localhost:(\d+)/#t=([A-Za-z0-9_-]{32})", line)
        self.assertIsNotNone(match, line)
        return process, int(match.group(1)), match.group(2)

    @staticmethod
    def reap(process):
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=20)

    def request(self, port, token, method, path, body=None, content_type=None):
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
        headers = {"Host": f"localhost:{port}", "X-ROSW-Token": token}
        if content_type:
            headers["Content-Type"] = content_type
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        data = response.read()
        connection.close()
        return response.status, data

    def test_the_first_line_is_the_open_line_and_quit_ends_it_with_exit_0(self):
        before = ts.snapshot(self.tmp)
        process, port, token = self.start()
        status, data = self.request(port, token, "GET", "/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data)["counts"]["brushes"], 8)
        self.assertEqual(self.request(port, "wrong", "GET", "/api/status")[0], 403)
        status, data = self.request(port, token, "GET", "/api/search?q=conte")
        self.assertEqual(json.loads(data)["results"][0]["brush_id"], self.world.ids["conte"])
        status, data = self.request(port, token, "POST", "/api/quit", b"{}", "application/json")
        self.assertEqual((status, json.loads(data)), (200, {"ok": True}))
        process.wait(timeout=20)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(ts.snapshot(self.tmp), before)
        self.assertEqual(list(self.cwd.iterdir()), [], "nothing is written where it was started")

    def test_the_token_is_new_each_run(self):
        first, _, token_one = self.start()
        second, _, token_two = self.start()
        self.assertNotEqual(token_one, token_two)

    def test_a_busy_port_under_the_script_is_exit_2(self):
        holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(holder.close)
        if sys.platform == "win32" and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            holder.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        holder.bind(("127.0.0.1", 0))
        holder.listen(1)
        port = holder.getsockname()[1]
        done = subprocess.run([sys.executable, "-I", str(SCRIPT), "--port", str(port), "--no-browser",
                               "--root", str(self.world.root)], capture_output=True, timeout=60,
                              cwd=tempfile.gettempdir())
        self.assertEqual(done.returncode, 2)
        self.assertEqual(done.stdout, b"")

    def test_a_copy_of_the_code_serves_and_leaves_no_bytecode(self):
        copy = Path(tempfile.mkdtemp(prefix="brushes-app-copy-")).resolve() / "brushes"
        self.addCleanup(shutil.rmtree, copy.parent, ignore_errors=True)
        (copy / "pipeline").mkdir(parents=True)
        for path in PIPELINE.glob("*.py"):
            shutil.copy2(path, copy / "pipeline" / path.name)
        shutil.copytree(BRUSHES / "schema", copy / "schema")
        (copy / "app").mkdir()
        (copy / "app" / "index.html").write_bytes(b"<!doctype html><title>copy</title>")
        (copy / "vault" / "tools").mkdir(parents=True)
        shutil.copy2(BRUSHES / "vault" / "tools" / "brush_search.py", copy / "vault" / "tools" / "brush_search.py")
        process, port, token = self.start(script=copy / "pipeline" / "app_server.py")
        self.assertEqual(self.request(port, token, "GET", "/api/search?q=conte")[0], 200)
        self.assertEqual(self.request(port, "x", "GET", "/")[1], b"<!doctype html><title>copy</title>")
        self.request(port, token, "POST", "/api/quit", b"{}", "application/json")
        process.wait(timeout=20)
        self.assertEqual([str(p) for p in copy.rglob("__pycache__")], [])


class TheSource(unittest.TestCase):
    def test_it_writes_no_file(self):
        tree = ast.parse((PIPELINE / "app_server.py").read_text(encoding="utf-8"))
        offenders = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if name in {"write_text", "write_bytes", "write_json", "mkdir", "unlink", "rmdir", "rename", "symlink",
                        "touch", "truncate", "copyfile", "move", "rmtree", "makedirs", "write_export"}:
                offenders.append(name)
            if name == "open" and any(isinstance(a, ast.Constant) and isinstance(a.value, str)
                                      and set(a.value) & set("wxa+") for a in node.args[1:2]):
                offenders.append("open for writing")
        self.assertEqual(offenders, [])

    def test_it_imports_the_standard_library_and_its_siblings_only(self):
        tree = ast.parse((PIPELINE / "app_server.py").read_text(encoding="utf-8"))
        siblings = {path.stem for path in PIPELINE.glob("*.py")}
        for node in ast.walk(tree):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else [node.module] if isinstance(node, ast.ImportFrom) and node.level == 0 else [])
            for name in names:
                top = name.split(".")[0]
                self.assertTrue(top in siblings or top in sys.stdlib_module_names or top == "__future__", name)

    def test_it_is_a_script_in_the_house_style(self):
        source = (PIPELINE / "app_server.py").read_text(encoding="utf-8")
        self.assertTrue(source.rstrip().endswith("raise SystemExit(main())"))
        self.assertIn("sys.path.insert(0, str(Path(__file__).resolve().parent))", source)
        self.assertIn("def main(argv=None):", source)
        self.assertIn("bc.open_console()", source)
        self.assertNotIn("\r", source)
        self.assertIsNone(ts.MACHINE_PATH.search(source))

    def test_the_declared_routes_are_the_registered_ones(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("pyyaml is not installed")
        spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        declared = spec["surfaces"]["app"]
        registered = []
        for route in app_server.ROUTES:
            registered.append(route.method + " " + route.pattern.pattern)
        self.assertEqual(len(declared["routes"]), len(app_server.ROUTES))
        for text in declared["routes"]:
            method, path = text.split(" ", 1)
            probe = (path.replace("<id>", "b_0123456789ab").replace("<set_slug>", "demo-set")
                     .replace("<kind>", "stroke"))
            probe = probe.split("  #")[0].strip()
            self.assertTrue(any(r.method == method and r.pattern.fullmatch(probe) for r in app_server.ROUTES), text)
        self.assertEqual(declared["port"], bc.APP_PORT)
        self.assertEqual(declared["token"]["header"], "X-ROSW-Token")
        self.assertEqual(declared["bind"], app_server.BIND)
        self.assertEqual(sorted(declared["export_formats"]), sorted(service.EXPORT_FORMATS))
        self.assertEqual(["/schema/" + name for name in app_server.SCHEMA_FILES], declared["static"]["schema"])


if __name__ == "__main__":
    unittest.main()
