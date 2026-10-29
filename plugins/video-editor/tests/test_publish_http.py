"""The mocked tests prove what we ask for; these prove `requests` really sends it that way.
A local HTTP server records raw requests (multipart bodies, streamed files, Content-Range, basic auth)."""
import _paths  # noqa: F401  (puts src/ on sys.path)

import json
import os
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from videoeditor.publish import oauth, package, secrets, service
from videoeditor.publish.platforms import bluesky, instagram, tiktok, x, youtube

TOKEN = json.dumps({"access_token": "ACCESS", "refresh_token": None, "expires_at": None, "scope": None, "extra": {}})


class Server:
    """routes: list of (method, path-prefix, fn(req) -> (status, headers, json-or-None))."""

    def __init__(self, routes):
        self.routes, self.requests = routes, []
        outer = self

        class H(BaseHTTPRequestHandler):
            def _handle(self):
                n = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(n) if n else b""
                path = self.path.split("?")[0]
                req = {"method": self.command, "path": path, "query": self.path.partition("?")[2], "headers": dict(self.headers),
                       "body": body}
                outer.requests.append(req)
                for m, prefix, fn in outer.routes:
                    if m == self.command and path.startswith(prefix):
                        status, headers, payload = fn(req)
                        data = json.dumps(payload).encode() if payload is not None else b""
                        self.send_response(status)
                        for k, v in (headers or {}).items():
                            self.send_header(k, v)
                        self.send_header("Content-Length", str(len(data)))
                        self.end_headers()
                        self.wfile.write(data)
                        return
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

            do_GET = do_POST = do_PUT = _handle

            def log_message(self, *a):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    def find(self, method, prefix):
        return [r for r in self.requests if r["method"] == method and r["path"].startswith(prefix)]


class RealHttp(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.dir = Path(self.td.name)
        clean = {k: v for k, v in os.environ.items() if not k.startswith("VE_")}
        self.env = mock.patch.dict(os.environ, clean, clear=True)
        self.env.start()
        self.nokr = mock.patch.object(secrets, "_keyring", return_value=None)
        self.nokr.start()
        video = self.dir / "v.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=s=1080x1920:r=25:d=2", "-f", "lavfi",
                        "-i", "sine=d=2", "-shortest", "-pix_fmt", "yuv420p", str(video)], check=True)
        with open(video, "ab") as f:
            f.write(os.urandom(300_000))            # a few chunks' worth
        self.pkg = package.build(video, "Real http caption", made_for_kids=False)
        self.bytes = video.read_bytes()
        self.servers = []

    def tearDown(self):
        for s in self.servers:
            s.close()
        self.nokr.stop(); self.env.stop(); self.td.cleanup()

    def serve(self, routes):
        s = Server(routes)
        self.servers.append(s)
        return s

    def test_mastodon_multipart_and_idempotency_header(self):
        inst = {"configuration": {"statuses": {"max_characters": 500}, "media_attachments": {}}}
        srv = self.serve([("GET", "/api/v2/instance", lambda r: (200, {}, inst)),
                          ("POST", "/api/v2/media", lambda r: (200, {}, {"id": "M1", "url": "u"})),
                          ("POST", "/api/v1/statuses", lambda r: (200, {}, {"id": "S1", "url": "https://x/1"}))])
        os.environ.update(VE_MASTODON_INSTANCE=srv.url, VE_MASTODON_TOKEN="TOK")
        service.send(self.pkg, "mastodon", edit_dir=self.dir / "e", confirm=True)
        media = srv.find("POST", "/api/v2/media")[0]
        self.assertIn("multipart/form-data", media["headers"]["Content-Type"])
        self.assertIn(b'name="file"', media["body"])
        self.assertIn(self.bytes[:2000], media["body"])                          # the real file went over the wire
        self.assertEqual(media["headers"]["Authorization"], "Bearer TOK")
        st = srv.find("POST", "/api/v1/statuses")[0]
        self.assertEqual(json.loads(st["body"])["visibility"], "private")
        self.assertEqual(len(st["headers"]["Idempotency-Key"]), 24)

    def test_x_multipart_segments_with_form_field(self):
        srv = self.serve([("POST", "/2/media/upload/initialize", lambda r: (200, {}, {"data": {"id": "MID"}})),
                          ("POST", "/2/media/upload/MID/append", lambda r: (204, {}, None)),
                          ("POST", "/2/media/upload/MID/finalize", lambda r: (200, {}, {"data": {"id": "MID"}})),
                          ("POST", "/2/tweets", lambda r: (201, {}, {"data": {"id": "T1"}}))])
        os.environ.update(VE_X_CLIENT_ID="CID", VE_X_TOKEN=TOKEN)
        with mock.patch.object(x, "API", srv.url), mock.patch.object(x, "SEGMENT", 131072):
            service.send(self.pkg, "x", edit_dir=self.dir / "e", confirm=True, public=True, accept_cost=True)
        apps = srv.find("POST", "/2/media/upload/MID/append")
        self.assertGreaterEqual(len(apps), 3)
        for i, a in enumerate(apps):
            self.assertIn(b'name="segment_index"', a["body"])
            self.assertIn(f'\r\n\r\n{i}\r\n'.encode(), a["body"])
            self.assertIn(b'name="media"', a["body"])
        self.assertEqual(srv.find("POST", "/2/tweets")[0]["headers"]["Authorization"], "Bearer ACCESS")
        self.assertEqual(json.loads(srv.find("POST", "/2/media/upload/initialize")[0]["body"])["total_bytes"], len(self.bytes))

    def test_bluesky_streams_the_file_with_query_params(self):
        sess = {"did": "did:plc:abc", "accessJwt": "JWT", "didDoc": None}
        srv = self.serve([("POST", "/xrpc/com.atproto.server.createSession", lambda r: (200, {}, sess)),
                          ("GET", "/xrpc/com.atproto.server.getServiceAuth", lambda r: (200, {}, {"token": "SVC"})),
                          ("GET", "/xrpc/app.bsky.video.getUploadLimits", lambda r: (200, {}, {"canUpload": True})),
                          ("POST", "/xrpc/app.bsky.video.uploadVideo", lambda r: (200, {}, {"jobStatus": {"jobId": "J", "did": "d", "state": "JOB_STATE_CREATED"}})),
                          ("GET", "/xrpc/app.bsky.video.getJobStatus", lambda r: (200, {}, {"jobStatus": {"jobId": "J", "did": "d", "state": "JOB_STATE_COMPLETED", "blob": {"$type": "blob"}}})),
                          ("POST", "/xrpc/com.atproto.repo.createRecord", lambda r: (200, {}, {"uri": "at://did:plc:abc/app.bsky.feed.post/k1", "cid": "c"}))])
        os.environ.update(VE_BLUESKY_IDENTIFIER="me", VE_BLUESKY_APP_PASSWORD="pw", VE_BLUESKY_SERVICE=srv.url)
        with mock.patch.object(bluesky, "VIDEO_HOST", srv.url):
            service.send(self.pkg, "bluesky", edit_dir=self.dir / "e", confirm=True, public=True)
        up = srv.find("POST", "/xrpc/app.bsky.video.uploadVideo")[0]
        self.assertEqual(up["body"], self.bytes)                                 # byte-identical stream
        self.assertEqual(up["headers"]["Content-Type"], "video/mp4")
        self.assertIn("did=did%3Aplc%3Aabc", up["query"])
        self.assertIn("name=v.mp4", up["query"])
        self.assertEqual(up["headers"]["Authorization"], "Bearer SVC")

    def test_youtube_resumable_content_range_over_http(self):
        holder = {}
        srv = self.serve([("POST", "/upload/youtube/v3/videos", lambda r: (200, {"Location": holder["url"] + "/session/1"}, None)),
                          ("PUT", "/session/1", lambda r: (308, {}, None) if not r["headers"]["Content-Range"].endswith(f"-{len(self.bytes) - 1}/{len(self.bytes)}") else (201, {}, {"id": "VID"}))])
        holder["url"] = srv.url
        os.environ.update(VE_YOUTUBE_CLIENT_ID="CID", VE_YOUTUBE_TOKEN=TOKEN)
        with mock.patch.object(youtube, "UPLOAD_URL", srv.url + "/upload/youtube/v3/videos"), mock.patch.object(youtube, "CHUNK", 131072):
            res = service.send(self.pkg, "youtube", edit_dir=self.dir / "e", confirm=True)
        puts = srv.find("PUT", "/session/1")
        self.assertGreaterEqual(len(puts), 3)
        self.assertEqual(b"".join(p["body"] for p in puts), self.bytes)          # all chunks, in order, no gaps
        self.assertEqual(res.id, "VID")
        init = srv.find("POST", "/upload/youtube/v3/videos")[0]
        self.assertIn("uploadType=resumable", init["query"])
        self.assertEqual(init["headers"]["X-Upload-Content-Length"], str(len(self.bytes)))

    def test_instagram_rupload_headers_and_body(self):
        holder = {}
        srv = self.serve([("POST", "/1789/media_publish", lambda r: (200, {}, {"id": "M"})),
                          ("POST", "/1789/media", lambda r: (200, {}, {"id": "C1", "uri": holder["url"] + "/rupload/C1"})),
                          ("POST", "/rupload/C1", lambda r: (200, {}, {"success": True})),
                          ("GET", "/C1", lambda r: (200, {}, {"status_code": "FINISHED"}))])
        holder["url"] = srv.url
        os.environ.update(VE_INSTAGRAM_TOKEN="IGT", VE_INSTAGRAM_USER_ID="1789", VE_INSTAGRAM_GRAPH=srv.url)
        res = instagram.Instagram().send(self.pkg, "draft", interval=0)
        up = srv.find("POST", "/rupload/C1")[0]
        self.assertEqual(up["body"], self.bytes)
        self.assertEqual((up["headers"]["offset"], up["headers"]["file_size"], up["headers"]["Authorization"]),
                         ("0", str(len(self.bytes)), "OAuth IGT"))
        create = srv.find("POST", "/1789/media")[0]
        self.assertIn(b"media_type=REELS", create["body"])                       # form-encoded, token not in the URL
        self.assertNotIn("IGT", create["query"])
        self.assertEqual(srv.find("POST", "/1789/media_publish"), [])
        self.assertEqual(res.status, "draft")

    def test_tiktok_chunk_put_headers(self):
        holder = {}
        srv = self.serve([("POST", "/v2/post/publish/inbox/video/init/", lambda r: (200, {}, {"data": {"publish_id": "P", "upload_url": holder["url"] + "/up/1"}})),
                          ("PUT", "/up/1", lambda r: (201, {}, None)),
                          ("POST", "/v2/post/publish/status/fetch/", lambda r: (200, {}, {"data": {"status": "SEND_TO_USER_INBOX"}}))])
        holder["url"] = srv.url
        os.environ.update(VE_TIKTOK_CLIENT_ID="K", VE_TIKTOK_TOKEN=TOKEN)
        with mock.patch.object(tiktok, "API", srv.url):
            service.send(self.pkg, "tiktok", edit_dir=self.dir / "e", confirm=True)
        put = srv.find("PUT", "/up/1")[0]
        n = len(self.bytes)
        self.assertEqual((put["headers"]["Content-Range"], put["headers"]["Content-Length"]), (f"bytes 0-{n - 1}/{n}", str(n)))
        self.assertEqual(put["body"], self.bytes)

    def test_token_exchange_basic_auth_over_http(self):
        srv = self.serve([("POST", "/token", lambda r: (200, {}, {"access_token": "T", "expires_in": 60}))])
        cfg = oauth.OAuthConfig(platform="p", auth_url="x", token_url=srv.url + "/token", client_id="CID", scopes=[],
                                client_secret="SEC", token_auth="basic")
        oauth.exchange_code(cfg, "CODE", "http://127.0.0.1/cb", "VER")
        req = srv.find("POST", "/token")[0]
        self.assertTrue(req["headers"]["Authorization"].startswith("Basic "))
        self.assertIn(b"code_verifier=VER", req["body"])
        self.assertNotIn(b"client_secret", req["body"])

    def test_http_errors_surface_without_leaking_tokens(self):
        srv = self.serve([("POST", "/api/v2/media", lambda r: (422, {}, {"error": "Unsupported file"})),
                          ("GET", "/api/v2/instance", lambda r: (200, {}, {"configuration": {}}))])
        os.environ.update(VE_MASTODON_INSTANCE=srv.url, VE_MASTODON_TOKEN="SECRETTOKEN")
        with self.assertRaises(Exception) as cm:
            service.send(self.pkg, "mastodon", edit_dir=self.dir / "e", confirm=True)
        self.assertIn("422", str(cm.exception))
        self.assertNotIn("SECRETTOKEN", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
