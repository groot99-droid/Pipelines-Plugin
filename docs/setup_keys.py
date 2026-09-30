"""Put your API keys in one place, outside the repo, from a page in your browser.

    python docs/setup_keys.py              # opens the keys page
    python docs/setup_keys.py --migrate    # move keys out of creative-writing/pipeline/.env

Keys are saved to ~/.rosw/keys.env (on Windows %USERPROFILE%\\.rosw\\keys.env), or to
ROSW_KEYS_FILE if that is set. creative-writing/pipeline/llm.py reads that file, so
nothing secret needs to live in the repo folder.

The page is served on 127.0.0.1 only, on a random port, and every request that reads
or changes anything must carry a random token made for this run. The page learns only
whether each key is set; a saved value is never sent back, printed or logged.
Stdlib only.
"""
import argparse
import http.server
import json
import os
import secrets
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path

DOCS = Path(__file__).resolve().parent
REPO = DOCS.parent
LEGACY_ENV = REPO / "creative-writing" / "pipeline" / ".env"

# The only names the page may set. Each is read by a tool in this repo.
KEYS = {
    "GEMINI_API_KEY": "creative-writing: the gemini_mcp drafting / librarian backend",
    "ANTHROPIC_API_KEY": "creative-writing: the anthropic drafting backend",
    "GOOGLE_FONTS_API_KEY": "ui-design: a live Google Fonts catalog refresh (maintainers only)",
}
_HTML = "text/html; charset=utf-8"
STATIC = {"/keys.html": _HTML, "/index.html": _HTML, "/creative-writing.html": _HTML,
          "/studio.html": _HTML, "/ui-design.html": _HTML, "/style.css": "text/css; charset=utf-8"}
MAX_VALUE = 512
PLACEHOLDERS = {"your-key-here", "Add_Key"}  # "no key yet"


def keys_file() -> Path:
    override = os.environ.get("ROSW_KEYS_FILE")
    return Path(override) if override else Path.home() / ".rosw" / "keys.env"


def read_env(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []


def parse(lines: list[str]) -> dict[str, str]:
    out = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        if value and value not in PLACEHOLDERS:
            out[key.strip()] = value
    return out


def status(path: Path) -> dict[str, bool]:
    present = parse(read_env(path))
    return {name: name in present for name in KEYS}


def write_keys(path: Path, changes: dict[str, str | None]) -> None:
    """Set (str) or remove (None) keys, keeping every other line of the file."""
    lines = read_env(path)
    if not lines:
        lines = ["# ROSW keys, written by docs/setup_keys.py. Never commit this file."]
    done = set()
    out = []
    for line in lines:
        name = line.split("=", 1)[0].strip() if "=" in line and not line.lstrip().startswith("#") else None
        if name in changes:
            if changes[name] is not None and name not in done:
                out.append(f"{name}={changes[name]}")
            done.add(name)
            continue
        out.append(line)
    for name, value in changes.items():
        if name not in done and value is not None:
            out.append(f"{name}={value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        os.chmod(path.parent, 0o700)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".keys.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out) + "\n")
        if os.name != "nt":
            os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def validate(body: object) -> dict[str, str | None]:
    """{"set": {NAME: value}, "remove": [NAME]} -> changes. Raises ValueError."""
    if not isinstance(body, dict) or set(body) - {"set", "remove"}:
        raise ValueError("expected {\"set\": {...}, \"remove\": [...]}")
    changes: dict[str, str | None] = {}
    for name, value in (body.get("set") or {}).items():
        if name not in KEYS:
            raise ValueError(f"unknown key {name!r}")
        if not isinstance(value, str):
            raise ValueError(f"{name}: value must be text")
        value = value.strip()
        if not value:
            continue  # an empty field leaves the saved value alone
        if len(value) > MAX_VALUE or any(c in value for c in "\r\n\0\"'") or value in PLACEHOLDERS:
            raise ValueError(f"{name}: that does not look like a key")
        changes[name] = value
    for name in body.get("remove") or []:
        if name not in KEYS:
            raise ValueError(f"unknown key {name!r}")
        changes[name] = None
    return changes


def make_server(path: Path, token: str, port: int = 0) -> http.server.HTTPServer:
    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "rosw-keys"
        sys_version = ""

        def log_message(self, *args):  # never log: a query string carries the token
            pass

        def _host_ok(self) -> bool:
            expected = f"127.0.0.1:{self.server.server_address[1]}"
            if self.headers.get("Host") != expected:
                return False
            origin = self.headers.get("Origin")
            return origin in (None, f"http://{expected}")

        def _authorised(self) -> bool:
            return secrets.compare_digest(self.headers.get("X-ROSW-Token", ""), token)

        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, obj: object) -> None:
            self._send(code, json.dumps(obj).encode(), "application/json")

        def do_GET(self):
            if not self._host_ok():
                return self._json(403, {"error": "bad host"})
            route = self.path.split("?", 1)[0]
            if route in STATIC:
                return self._send(200, (DOCS / route.lstrip("/")).read_bytes(), STATIC[route])
            if route == "/status":
                if not self._authorised():
                    return self._json(403, {"error": "bad token"})
                return self._json(200, {"file": str(path), "keys": status(path),
                                        "about": KEYS})
            self._json(404, {"error": "not found"})

        def do_POST(self):
            # Read the body before any reply: closing a socket with unread data
            # resets the connection on Windows, and the client sees an error
            # instead of the refusal.
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = -1
            if not 0 <= length <= 16384:
                self.close_connection = True
                return self._json(413, {"error": "request too large"})
            raw = self.rfile.read(length)
            if not self._host_ok():
                return self._json(403, {"error": "bad host"})
            if not self._authorised():
                return self._json(403, {"error": "bad token"})
            route = self.path.split("?", 1)[0]
            if route == "/quit":
                self._json(200, {"ok": True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            if route != "/save":
                return self._json(404, {"error": "not found"})
            try:
                changes = validate(json.loads(raw or b"{}"))
            except (ValueError, json.JSONDecodeError) as exc:
                return self._json(400, {"error": str(exc)})
            if changes:
                write_keys(path, changes)
            self._json(200, {"keys": status(path)})

    return http.server.HTTPServer(("127.0.0.1", port), Handler)


def migrate(path: Path) -> int:
    """Move known keys out of the legacy repo .env into the user file, then delete it."""
    legacy = parse(read_env(LEGACY_ENV))
    if not LEGACY_ENV.exists():
        print("Nothing to move: there is no creative-writing/pipeline/.env.")
        return 0
    moved = {k: v for k, v in legacy.items() if k in KEYS}
    others = sorted(set(legacy) - set(moved))
    if others:
        print(f"Not moving {', '.join(others)}: setup_keys.py only handles {', '.join(KEYS)}.")
        print("Leaving creative-writing/pipeline/.env in place. Move those by hand.")
        return 1
    if moved:
        write_keys(path, moved)
        if not all(status(path)[k] for k in moved):
            print("The key file did not read back as expected; nothing deleted.")
            return 1
    LEGACY_ENV.unlink()
    print(f"Moved {', '.join(moved) or 'nothing'} to {path}")
    print("Deleted creative-writing/pipeline/.env.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--migrate", action="store_true",
                    help="move keys from creative-writing/pipeline/.env to the user key file")
    ap.add_argument("--no-browser", action="store_true", help="print the address, do not open it")
    args = ap.parse_args(argv)
    path = keys_file()
    if args.migrate:
        return migrate(path)
    token = secrets.token_urlsafe(24)
    server = make_server(path, token)
    url = f"http://127.0.0.1:{server.server_address[1]}/keys.html#t={token}"
    print(f"Keys are saved to {path}")
    print(f"Open {url}")
    print("Press Ctrl+C here, or Done on the page, to stop.")
    if LEGACY_ENV.exists():
        print("Note: creative-writing/pipeline/.env still exists. "
              "`python docs/setup_keys.py --migrate` moves it out of the repo.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    print("Stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
