"""The one download helper: kept whole or not at all, never a stray .part."""

import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile

from download import DownloadError, download

BODY = b"x" * 70000


class Serve(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/short":
            self.send_response(200)
            self.send_header("Content-Length", str(len(BODY) + 10))
            self.end_headers()
            self.wfile.write(BODY)
        elif self.path == "/ok":
            self.send_response(200)
            self.send_header("Content-Length", str(len(BODY)))
            self.end_headers()
            self.wfile.write(BODY)
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


class Download(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Serve)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def test_a_whole_file_is_kept_with_its_hash(self):
        target = Path(self.dir.name) / "sub" / "a.bin"
        found = download(self.base + "/ok", target)
        self.assertEqual(found["bytes"], len(BODY))
        self.assertEqual(target.read_bytes(), BODY)
        self.assertEqual(list(target.parent.glob("*.part")), [])

    def test_a_short_read_and_an_error_keep_nothing_and_leave_no_part(self):
        for path in ("/short", "/missing"):
            target = Path(self.dir.name) / "b.bin"
            with self.subTest(path=path):
                with self.assertRaises(DownloadError):
                    download(self.base + path, target)
                self.assertFalse(target.exists())
                self.assertEqual(list(Path(self.dir.name).glob("*.part")), [])


if __name__ == "__main__":
    unittest.main()
