"""The brushes app server: a loopback HTTP API and the files of the designer app
(brushes/docs/CONTRACTS.md, F10 "HTTP").

    python -I brushes/pipeline/app_server.py [--port 8719] [--no-browser] [--dev]

It binds 127.0.0.1:8719 and nothing else. The one origin is
http://localhost:8719; a busy port is exit 2, never a different port, because
the browser keeps the author's presets per origin. The first line on stdout is

    Open http://localhost:<port>/#t=<token>

The token is made per run (secrets.token_urlsafe(24)), reaches the page only in
the URL fragment, and every /api/* call must send it as `X-ROSW-Token`. The
Browser pane or any browser is then pointed at that line.

The request gate, in this order: the method is GET or POST (405); the target
starts with `/`, is at most 2048 characters and holds no NUL (400); `Host` is
`localhost:<port>` or `127.0.0.1:<port>` (403 bad_host: this is what stops a
DNS-rebinding page); `Origin`, when sent, is `http://<that host>` (403
bad_origin); `Sec-Fetch-Site`, when sent, is `same-origin` or `none` (403
cross_site); the route exists (404); the token is right (403 bad_token); a POST
has a Content-Length (411) within its route's cap (413) and the right content
type (415).

Static files need no token: every regular file under brushes/app/ found by
walking it when the server starts (no dot-file, none over 8 MiB, no link that
leaves the folder, one of the extensions of CONTENT_TYPES), plus exactly four
files of brushes/schema/. A name is looked up in that table by exact match; no
path is ever built from a request. `--dev` walks again on every request and
logs each request to stderr.

The server writes nothing: not to library/, catalog/ or vault/, not to disk at
all. An export is built in memory and returned to the browser, which saves it.
Everything behind a route is pipeline/service.py, the layer the MCP server
shares.

Exit codes: 0 stopped, 2 a bad argument or a busy port.

Standard library only.
"""

from __future__ import annotations

import sys

if __name__ == "__main__":
    # The server writes nothing, not even a __pycache__. Set before the sibling
    # imports below, and only when this file is the program.
    sys.dont_write_bytecode = True

import argparse
import http.server
import json
import os
import re
import secrets
import socket
import socketserver
import threading
import traceback
import webbrowser
from pathlib import Path
from urllib.parse import parse_qsl, quote, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import service  # noqa: E402
import zip_writer  # noqa: E402
from service import ApiError  # noqa: E402

BIND = "127.0.0.1"
MAX_TARGET = 2048
MAX_STATIC = 8 * service.MIB
MAX_SOURCE_ZIP = 64 * service.MIB
DRAIN_LIMIT = 4 * service.MIB
SEARCH_TOP_DEFAULT = 48
JSON_TYPE = "application/json"
STREAM_TYPE = "application/octet-stream"

# An explicit table, never `mimetypes`: the Windows registry can map `.js` to
# text/plain. A file whose extension is not here is not served.
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".txt": "text/plain; charset=utf-8",
    ".map": "application/json; charset=utf-8",
}
SCHEMA_FILES = ("silica_keys.json", "facets.json", "bundled_textures.json", "preview_calibration.json")
STATIC_NAME = re.compile(r"^/[A-Za-z0-9._~@+=,-]+(?:/[A-Za-z0-9._~@+=,-]+)*$")

CSP = ("default-src 'self'; img-src 'self' blob: data:; style-src 'self'; script-src 'self'; "
       "connect-src 'self' http://localhost:* http://127.0.0.1:*; worker-src 'self' blob:; "
       "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")

# status -> error code for a request the stdlib handler refused before routing
_PARSE_ERRORS = {400: "bad_request", 405: "method_not_allowed", 411: "length_required", 413: "too_large",
                 414: "bad_request", 431: "bad_request", 501: "method_not_allowed"}


def static_table(paths):
    """{url path: (file, content type)}: the allow-list. Walked, never built
    from a request. Files only; no dot-file or dot-folder; no link, junction or
    file that resolves outside its root; at most MAX_STATIC bytes."""
    table = {}
    try:
        app_root = paths.app.resolve()
    except OSError:
        app_root = None
    if app_root is not None and app_root.is_dir():
        for folder, folders, names in os.walk(app_root, followlinks=False):
            keep = []
            for name in sorted(folders):
                path = Path(folder) / name
                is_junction = getattr(path, "is_junction", lambda: False)()
                if not name.startswith(".") and not path.is_symlink() and not is_junction:
                    keep.append(name)
            folders[:] = keep
            for name in sorted(names):
                _add_static(table, app_root, Path(folder) / name, "/" + (Path(folder) / name).relative_to(app_root).as_posix())
    try:
        schema_root = paths.schema.resolve()
    except OSError:
        schema_root = None
    if schema_root is not None:
        for name in SCHEMA_FILES:
            _add_static(table, schema_root, schema_root / name, "/schema/" + name)
    return table


def _add_static(table, root, path, url):
    if any(part.startswith(".") for part in url.split("/")) or STATIC_NAME.match(url) is None:
        return
    content_type = CONTENT_TYPES.get(Path(url).suffix.lower())
    if content_type is None:
        return
    try:
        if path.is_symlink() or not path.is_file():
            return
        resolved = path.resolve()
        if root not in resolved.parents or resolved.stat().st_size > MAX_STATIC:
            return
    except OSError:
        return
    table[url] = (resolved, content_type)


def ascii_header(value):
    """A header value that is plain ASCII with no control character, or a bug."""
    value = str(value)
    if not value.isascii() or any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("a header value must be printable ASCII")
    return value


class Route:
    def __init__(self, method, pattern, handler, *, query=(), many=(), cap=0, types=()):
        self.method = method
        self.pattern = re.compile(pattern)
        self.handler = handler
        self.query = set(query) | set(many)       # parameter names the route takes
        self.many = set(many)                     # the ones that may repeat
        self.cap = cap                            # a POST's largest body
        self.types = tuple(types)                 # a POST's content types


ID = r"b_[0-9a-f]{12}"
SLUG = r"[a-z0-9][a-z0-9-]{0,47}"


class AppServer(http.server.ThreadingHTTPServer):
    """The HTTP server: loopback only, one token, one allow-list of files."""

    daemon_threads = True
    # On Windows SO_REUSEADDR lets a second process bind a port that is in use,
    # which would turn "busy port is exit 2" into two servers on one port.
    allow_reuse_address = sys.platform != "win32"

    def __init__(self, address, service_, token, *, max_upload, dev, paths, log):
        self.service = service_
        self.token = token
        self.token_bytes = token.encode("utf-8")
        self.max_upload = max_upload
        self.dev = dev
        self.paths = paths
        self.log = log
        self.work_lock = threading.Lock()
        self.static = static_table(paths)
        self.quit_requested = False
        super().__init__(address, Handler)
        port = self.server_address[1]
        self.allowed_hosts = frozenset({f"localhost:{port}", f"127.0.0.1:{port}"})

    def server_bind(self):
        exclusive = getattr(socket, "SO_EXCLUSIVEADDRUSE", None)
        if sys.platform == "win32" and exclusive is not None:
            self.socket.setsockopt(socket.SOL_SOCKET, exclusive, 1)
        # HTTPServer.server_bind would ask the resolver for this host's name.
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = "localhost", self.server_address[1]

    def handle_error(self, request, client_address):           # a dropped connection is not news
        error = sys.exc_info()[1]
        if not isinstance(error, (ConnectionError, TimeoutError, BrokenPipeError)) and self.log:
            self.log("an error in a request:\n" + traceback.format_exc())

    @property
    def port(self):
        return self.server_address[1]

    def url(self):
        return f"http://localhost:{self.port}/#t={self.token}"


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    timeout = 30
    server_version = "rosw-brushes"
    sys_version = ""
    _body_taken = False                 # the POST body has been read, or drained

    # ── the stdlib hooks ──
    def log_message(self, format, *args):                      # noqa: A002
        if self.server.dev and self.server.log:
            self.server.log("%s %s" % (self.address_string(), format % args))

    def send_error(self, code, message=None, explain=None):
        """The stdlib calls this for a request it cannot parse; the answer is
        JSON like every other."""
        self._send_error_json(ApiError(_PARSE_ERRORS.get(code, "bad_request"), message or "bad request",
                                       405 if code == 501 else code))

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def _other_method(self):
        self._send_error_json(ApiError("method_not_allowed", "only GET and POST are served", 405))

    do_HEAD = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_TRACE = do_CONNECT = _other_method

    # ── sending ──
    def _headers(self, content_type, length, extra=()):
        self.send_header("Content-Type", ascii_header(content_type))
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        for name, value in extra:
            self.send_header(name, ascii_header(value))
        self.end_headers()

    def _send(self, status, body, content_type, extra=()):
        self.send_response(status)
        self._headers(content_type, len(body), extra)
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, payload, status=200):
        try:
            body = json.dumps(payload, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode("ascii")
        except (TypeError, ValueError):
            raise ApiError("internal", "a reply could not be written as JSON", 500) from None
        self._send(status, body, JSON_TYPE)

    def _send_error_json(self, error):
        body = {"error": {"code": error.code, "message": error.message, "hint": error.hint,
                          "data": error.data}}
        extra = (("Allow", "GET, POST"),) if error.status == 405 else ()
        try:
            data = json.dumps(body, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode("ascii")
        except (TypeError, ValueError):
            data = b'{"error":{"code":"internal","message":"internal error","hint":null,"data":null}}'
        try:
            self.send_response(error.status)
            self.close_connection = True
            self._headers(JSON_TYPE, len(data), extra)
            if self.command != "HEAD":
                self.wfile.write(data)
        except (OSError, ValueError):
            pass

    # ── the gate and the dispatch ──
    def _handle(self, method):
        try:
            self._serve(method)
        except ApiError as exc:
            self._drain_unread()
            self._send_error_json(exc)
        except (ConnectionError, TimeoutError):
            self.close_connection = True
        except Exception:                                      # a mistake here, not in the request
            if self.server.log:
                self.server.log(f"{method} {self.path[:200]} failed:\n" + traceback.format_exc())
            self._drain_unread()
            self._send_error_json(ApiError("internal", "internal error", 500,
                                           hint="the server's stderr log has the details"))

    def _serve(self, method):
        server = self.server
        target = self.path
        if (not target.startswith("/") or len(target) > MAX_TARGET or "\x00" in target):
            raise ApiError("bad_request", "the request target must start with / and be at most "
                                          f"{MAX_TARGET} characters with no NUL", 400)
        hosts = self.headers.get_all("Host") or []
        if len(hosts) != 1 or hosts[0].strip().lower() not in server.allowed_hosts:
            raise ApiError("bad_host", "this server answers only to localhost and 127.0.0.1 on its own port", 403)
        origin = self.headers.get("Origin")
        if origin is not None and origin.strip().lower() not in {f"http://{h}" for h in server.allowed_hosts}:
            raise ApiError("bad_origin", "this server answers only to its own page", 403)
        fetch_site = self.headers.get("Sec-Fetch-Site")
        if fetch_site is not None and fetch_site.strip().lower() not in ("same-origin", "none"):
            raise ApiError("cross_site", "a cross-site request is refused", 403)
        raw_path, _, query = target.partition("?")
        raw_path = raw_path.split("#", 1)[0]
        path = unquote(raw_path, errors="replace")
        if "\x00" in path:
            raise ApiError("bad_request", "the request target holds a NUL", 400)
        if path.startswith("/api/") or path == "/api":
            route, groups = self._route(method, path)
            self._check_token()
            params = self._query(route, query)
            if method == "POST":
                self._post(route, groups, params)
            else:
                route.handler(self, groups, params)
            return
        if method != "GET":
            raise ApiError("method_not_allowed", "static files are served with GET", 405)
        self._static(path)

    def _route(self, method, path):
        known = False
        for route in ROUTES:
            found = route.pattern.fullmatch(path)
            if found is None:
                continue
            known = True
            if route.method == method:
                return route, found.groups()
        if known:
            raise ApiError("method_not_allowed", f"{method} is not what that route takes", 405)
        raise ApiError("not_found", "no such route", 404)

    def _check_token(self):
        given = self.headers.get("X-ROSW-Token")
        if given is None or not secrets.compare_digest(given.encode("utf-8", "replace"),
                                                       self.server.token_bytes):
            raise ApiError("bad_token", "this call needs the X-ROSW-Token of this run", 403,
                           hint="open the page at the Open line the server printed when it started")

    @staticmethod
    def _query(route, query):
        """{name: [values]} of a query string, only the names the route takes."""
        try:
            pairs = parse_qsl(query, keep_blank_values=True, max_num_fields=40, errors="replace")
        except ValueError:
            raise ApiError("bad_request", "too many query parameters", 400) from None
        params = {}
        for name, value in pairs:
            if name not in route.query:
                raise ApiError("bad_argument", f"this route takes no `{name[:40]}` parameter", 400)
            if "\x00" in value or len(value) > 600:
                raise ApiError("bad_argument", f"`{name}` is too long or holds a NUL", 400)
            params.setdefault(name, []).append(value)
        for name, values in params.items():
            if name not in route.many and len(values) > 1:
                raise ApiError("bad_argument", f"`{name}` is given once", 400)
        return params

    # ── bodies ──
    def _drain(self, length):
        left = min(length, DRAIN_LIMIT)
        while left > 0:
            chunk = self.rfile.read(min(left, 65536))
            if not chunk:
                break
            left -= len(chunk)

    def _drain_unread(self):
        """Read what a POST sent that no route took before answering it: a
        reply sent while the client is still writing, and a socket closed with
        unread bytes, can reset the connection before the client has read the
        reply (it then sees a network error, not the 403)."""
        if self.command != "POST" or self._body_taken:
            return
        self._body_taken = True
        text = (self.headers.get("Content-Length") or "").strip()
        if not text.isdigit() or len(text) > 12 or "Transfer-Encoding" in self.headers:
            return
        try:
            self.connection.settimeout(2)
            self._drain(int(text))
        except OSError:
            pass

    def _body(self, route):
        self._body_taken = True
        if "Transfer-Encoding" in self.headers:
            raise ApiError("length_required", "chunked bodies are not accepted; send Content-Length", 411)
        text = self.headers.get("Content-Length")
        if text is None or not text.strip().isdigit() or len(text.strip()) > 12:
            raise ApiError("length_required", "a POST needs a Content-Length", 411)
        length = int(text.strip())
        cap = self.server.max_upload if route.cap == service.MAX_UPLOAD else route.cap
        if length > cap:
            self._drain(length)
            raise ApiError("too_large", f"the body may be at most {cap:,} bytes", 413)
        media = (self.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
        if media not in route.types:
            self._drain(length)
            raise ApiError("unsupported_file", f"this route takes {' or '.join(route.types)}", 415)
        chunks, left = [], length
        while left > 0:
            chunk = self.rfile.read(min(left, 1 << 20))
            if not chunk:
                raise ApiError("bad_request", "the body ended before Content-Length", 400)
            chunks.append(chunk)
            left -= len(chunk)
        return b"".join(chunks)

    def _json_body(self, body):
        def refuse(name):
            raise ValueError(name)

        try:
            value = json.loads(body.decode("utf-8"), parse_constant=refuse)
        except (ValueError, RecursionError):
            raise ApiError("bad_json", "the body is not valid JSON", 400) from None
        if not isinstance(value, dict):
            raise ApiError("bad_json", "the body must be a JSON object", 400)
        return value

    def _post(self, route, groups, params):
        body = self._body(route)
        route.handler(self, groups, params, body)

    # ── static files ──
    def _static(self, path):
        server = self.server
        if path == "/":
            path = "/index.html"
        table = static_table(server.paths) if server.dev else server.static
        entry = table.get(path)
        if entry is None:
            raise ApiError("not_found", "no such file", 404)
        file, content_type = entry
        try:
            if file.stat().st_size > MAX_STATIC:
                raise ApiError("not_found", "no such file", 404)
            data = file.read_bytes()
        except OSError:
            raise ApiError("not_found", "no such file", 404) from None
        extra = (("Content-Security-Policy", CSP),) if content_type.startswith("text/html") else ()
        self._send(200, data, content_type, extra)


# ── the routes ───────────────────────────────────────────────────────────────

def _one(params, name, default=None):
    values = params.get(name)
    return values[0] if values else default


def _number(params, name, default, low, high):
    text = _one(params, name)
    if text is None:
        return default
    if not text.isascii() or not text.isdigit() or len(text) > 9:
        raise ApiError("bad_argument", f"`{name}` is a whole number from {low} to {high}", 400)
    value = int(text)
    if not low <= value <= high:
        raise ApiError("bad_argument", f"`{name}` is a whole number from {low} to {high}", 400)
    return value


def _status(handler, groups, params):
    payload = handler.server.service.status()
    payload["caps"] = {
        "max_upload_bytes": handler.server.max_upload,
        "max_export_json_bytes": service.MAX_EXPORT_JSON,
        "max_patch_json_bytes": service.MAX_PATCH_JSON,
        "search_top_max": service.HTTP_TOP_MAX,
        "export_formats": list(service.EXPORT_FORMATS),
        "container": dict(container.CAPS),
    }
    payload["new_brush_era"] = brush_model.NEW_BRUSH_ERA
    payload["new_brush_eras"] = list(brush_model.NEW_BRUSH_ERAS)
    handler._send_json(payload)


def _search(handler, groups, params):
    handler._send_json(handler.server.service.search(
        _one(params, "q", ""), params.get("tag"), params.get("where"), params.get("where_not"),
        _number(params, "top", SEARCH_TOP_DEFAULT, 1, service.HTTP_TOP_MAX),
        _number(params, "offset", 0, 0, service.MAX_OFFSET)))


def _facets(handler, groups, params):
    handler._send_json(handler.server.service.facets(params.get("tag"), params.get("where"),
                                                     params.get("where_not")))


def _vocabulary(handler, groups, params):
    handler._send_json(handler.server.service.vocabulary())


def _sets(handler, groups, params):
    handler._send_json(handler.server.service.list_sets(_one(params, "library")))


def _one_set(handler, groups, params):
    handler._send_json(handler.server.service.get_set(groups[0]))


def _brush(handler, groups, params):
    include = _one(params, "include")
    handler._send_json(handler.server.service.get_brush(
        groups[0], include.split(",") if include else None))


def _similar(handler, groups, params):
    handler._send_json(handler.server.service.similar(
        groups[0], _number(params, "top", 10, 1, service.HTTP_TOP_MAX)))


def _open(handler, groups, params):
    with handler.server.work_lock:
        handler._send_json(handler.server.service.open_library_brush(
            groups[0], _one(params, "textures", "full")))


def _preview(handler, groups, params):
    data, _ = handler.server.service.preview(groups[0], groups[1])
    handler._send(200, data, "image/png")


def _source_zip(handler, groups, params):
    table = handler.server.static if not handler.server.dev else static_table(handler.server.paths)
    entries, total = [], 0
    for url in sorted(table):
        file, _ = table[url]
        data = file.read_bytes()
        total += len(data)
        if total > MAX_SOURCE_ZIP:
            raise ApiError("too_large", "the app files are too large to zip", 413)
        entries.append((url.lstrip("/"), data))
    try:
        body = zip_writer.write_zip(entries)
    except zip_writer.ZipWriteError as exc:
        raise ApiError("internal", str(exc), 500) from None
    handler._send(200, body, "application/zip",
                  (("Content-Disposition", 'attachment; filename="rosw-brushes-app-source.zip"'),))


def _similar_settings(handler, groups, params, body):
    request = handler._json_body(body)
    unknown = set(request) - {"settings", "tags", "where", "where_not", "top", "other_sets"}
    if unknown:
        raise ApiError("bad_argument", f"the request has no `{sorted(unknown)[0][:30]}`", 400)
    top = request.get("top", 10)
    handler._send_json(handler.server.service.similar_settings(
        request.get("settings"), request.get("tags"), request.get("where"), request.get("where_not"), top,
        other_sets=request.get("other_sets", False)))


def _import(handler, groups, params, body):
    filename = unquote(handler.headers.get("X-ROSW-Filename") or "", errors="replace")[:255]
    with handler.server.work_lock:
        handler._send_json(handler.server.service.decode_upload(
            body, filename, _one(params, "member"), _one(params, "textures", "full")))


def _validate_patch(handler, groups, params, body):
    request = handler._json_body(body)
    unknown = set(request) - {"changes", "base", "base_id", "era"}
    if unknown:
        raise ApiError("bad_argument", f"the request has no `{sorted(unknown)[0][:30]}`", 400)
    handler._send_json(handler.server.service.validate_patch(
        request.get("changes"), request.get("base_id"), request.get("base"), request.get("era")))


def _export(handler, groups, params, body):
    request = handler._json_body(body)
    with handler.server.work_lock:
        export = handler.server.service.build_export(request)
    if export.dry_run:
        handler._send_json(export.report)
        return
    extension = export.filename.rsplit(".", 1)[-1]
    shown = request.get("name") if isinstance(request.get("name"), str) else None
    if shown is None and export.report["brushes"]:
        shown = export.report["brushes"][0].get("name")
    shown = "".join(ch for ch in (shown or export.filename.rsplit(".", 1)[0]) if ch.isprintable())
    header = {"filename": export.filename, "size": export.report["size"], "sha256": export.report["sha256"],
              "brushes": len(export.report["brushes"]), "warnings": len(export.report["warnings"])}
    handler._send(200, export.data, STREAM_TYPE, (
        ("Content-Disposition", f'attachment; filename="{export.filename}"; '
                                f"filename*=UTF-8''{quote(shown + '.' + extension, safe='')}"),
        ("X-ROSW-Export", quote(json.dumps(header, separators=(",", ":")), safe=""))))


def _quit(handler, groups, params, body):
    handler.server.quit_requested = True
    handler._send_json({"ok": True})
    threading.Thread(target=handler.server.shutdown, daemon=True).start()


ROUTES = (
    Route("GET", r"/api/status", _status),
    Route("GET", r"/api/search", _search, query=("q", "top", "offset"), many=("tag", "where", "where_not")),
    Route("GET", r"/api/facets", _facets, many=("tag", "where", "where_not")),
    Route("GET", r"/api/vocabulary", _vocabulary),
    Route("GET", r"/api/sets", _sets, query=("library",)),
    Route("GET", rf"/api/sets/({SLUG})", _one_set),
    Route("GET", rf"/api/brush/({ID})", _brush, query=("include",)),
    Route("GET", rf"/api/brush/({ID})/similar", _similar, query=("top",)),
    Route("GET", rf"/api/brush/({ID})/open", _open, query=("textures",)),
    Route("GET", rf"/api/preview/({ID})/(stroke|shape|grain)\.png", _preview),
    Route("GET", r"/api/app-source\.zip", _source_zip),
    Route("POST", r"/api/similar", _similar_settings, cap=service.MAX_PATCH_JSON, types=(JSON_TYPE,)),
    Route("POST", r"/api/import", _import, query=("member", "textures"), cap=service.MAX_UPLOAD,
          types=(STREAM_TYPE,)),
    Route("POST", r"/api/validate-patch", _validate_patch, cap=service.MAX_PATCH_JSON, types=(JSON_TYPE,)),
    Route("POST", r"/api/export", _export, cap=service.MAX_EXPORT_JSON, types=(JSON_TYPE,)),
    Route("POST", r"/api/quit", _quit, cap=1024, types=(JSON_TYPE,)),
)


# ── starting ─────────────────────────────────────────────────────────────────

def make_server(service_, token, port=bc.APP_PORT, *, max_upload=service.MAX_UPLOAD, dev=False,
                paths=None, log=None):
    """An AppServer bound to 127.0.0.1:`port`. `port=0` picks a free port (the
    tests use it; the command line never falls back to one). Raises OSError
    when the port is busy."""
    return AppServer((BIND, port), service_, token, max_upload=max_upload, dev=dev,
                     paths=paths if paths is not None else service_.paths, log=log)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="app_server.py", allow_abbrev=False,
        description="The brushes app server: the designer app and its JSON API on 127.0.0.1, "
                    "one token per run. It writes nothing.")
    bc.add_path_arguments(parser)
    parser.add_argument("--port", type=int, default=bc.APP_PORT, metavar="N",
                        help=f"the port (default {bc.APP_PORT}); a busy port is exit 2, never another port")
    parser.add_argument("--no-browser", action="store_true",
                        help="print the Open line and do not start a browser")
    parser.add_argument("--dev", action="store_true",
                        help="walk app/ again on every request and log each request to stderr")
    return parser


def _stderr_log(text):
    try:
        print(f"[app_server] {text}", file=sys.stderr, flush=True)
    except (OSError, ValueError):
        pass


def main(argv=None):
    bc.open_console()
    args = build_parser().parse_args(argv)
    if not 0 <= args.port <= 65535:
        print("--port is 0 to 65535", file=sys.stderr)
        return bc.EXIT_USAGE
    paths = bc.paths_from_args(args)
    token = secrets.token_urlsafe(24)
    brush_service = service.BrushService(paths, mode="project", log=_stderr_log)
    try:
        server = make_server(brush_service, token, args.port, dev=args.dev, paths=paths, log=_stderr_log)
    except OSError as exc:
        print(f"port {args.port} on {BIND} cannot be used ({exc.strerror or exc}); another copy may be "
              "running. The server never falls back to another port.", file=sys.stderr)
        return bc.EXIT_USAGE
    if not (paths.app / "index.html").is_file():
        _stderr_log("brushes/app/index.html is not there: only the API will answer")
    url = server.url()
    print(f"Open {url}", flush=True)
    _stderr_log(f"serving {paths.root} on {BIND}:{server.port}; Ctrl-C or POST /api/quit stops it")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:                                      # no browser is not a reason to stop
            pass
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return bc.EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
