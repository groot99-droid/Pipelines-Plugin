"""The hub's server. Standard library only.

    python studio/hub/serve.py [--port 8765]

Binds 127.0.0.1 and serves two things: the static files in this folder (the
hub page, and the brush designer under brush/), and a few JSON routes over the
studio's own files. It never serves the repo root, and it reads the vault and
the runs through studio_common, so it counts exactly the notes and runs the
pipeline does.

    GET  /api/notes         one row per Content MD (vault_index.note_rows)
    GET  /api/search?q=     the index, when it has been built
    GET  /api/runs          every run, as studio_run.py status --json prints it
    GET  /api/gates         each gate in the spec: authored, answers, unresolved
    GET  /api/pipelines     each pipeline: status, kind, what it makes
    GET  /api/writing       the creative-writing index's files and kinds, titles only
    GET  /api/museum        where the Writing Museum's own server is expected (--museum-port,
                            default 8768): its url, the command that starts it, and whether
                            its library has been built. The hub never serves the museum.
    GET  /api/tokens        tokens.json, so the page's stylesheet can take its values
    POST /api/runs          {"pipeline": ..., "title": ...} -> a new run, through the bookkeeper

The one write is POST /api/runs, and it writes only under the run folder. The
hub never writes a note, a gate or tokens.json.

Exit codes: 0, or 2 when the port cannot be bound.
"""

import argparse
import json
import sys
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
STUDIO = HERE.parent
REPO = STUDIO.parent
sys.path.insert(0, str(STUDIO / "pipeline"))
sys.path.insert(0, str(STUDIO / "vault" / "tools"))

import studio_common  # noqa: E402
import studio_run  # noqa: E402
import vault_index  # noqa: E402
from studio_common import Env, Refused, Usage, read_text  # noqa: E402

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_MUSEUM_PORT = 8768   # python -m http.server 8768 --directory writing-museum
MARK = "ROSW studio hub"  # the launcher looks for this in / to recognise a running hub


def gates_view(env):
    rows = []
    for name, cfg in env.spec["gates"].items():
        found = studio_common.gate_sections(env, name)
        rows.append({
            "gate": name,
            "file": cfg["file"],
            "must_answer": cfg.get("must_answer", ""),
            "authored": found is not None,
            "answers": found["answers"] if found else [],
            "unresolved": found["unresolved"] if found else [],
            "needed_by": sorted(p for p, pcfg in env.spec["pipelines"].items()
                                if any(need["gate"] == name for need in pcfg.get("requires_context", []))),
        })
    return rows


def pipelines_view(env):
    return [{"pipeline": name, "status": cfg.get("status"), "kind": cfg.get("kind"),
             "makes": cfg.get("makes", ""), "class": cfg.get("class", "none"),
             "requires": [need["gate"] for need in cfg.get("requires_context", [])]}
            for name, cfg in env.spec["pipelines"].items()]


def runs_view(env):
    broken = []
    runs = [studio_run.summary(env, state) for state in studio_common.all_states(env, broken)]
    runs.sort(key=lambda r: r.get("updated") or "", reverse=True)
    return runs + [{"run_id": run_id, "status": "broken", "problem": problem} for run_id, problem in broken]


def writing_view(repo):
    """Titles and kinds from the creative-writing vault's own index, if it has
    been built. Never a body: that vault is read only through its own tool."""
    path = repo / "creative-writing" / "vault" / "tools" / "rag_index" / "index.json"
    if not path.is_file():
        return {"built": None, "files": []}
    try:
        index = json.loads(read_text(path))
    except (Usage, json.JSONDecodeError):
        return {"built": None, "files": []}
    seen = {}
    for chunk in index.get("chunks", []):
        file = chunk.get("file")
        if not file or file in seen:
            continue
        seen[file] = {"file": file, "source_type": chunk.get("source_type", ""),
                      "kind": Path(file).parts[0] if "/" in file else ""}
    return {"built": index.get("built"), "files": sorted(seen.values(), key=lambda f: f["file"])}


def museum_view(repo, museum_port):
    """Where the Writing Museum is served from, when it is: a link, never a proxy. The
    museum has its own server over its own folder, and the library page beside its
    viewer reads the vault's works; the hub only points at it and says whether the
    library file exists. Nothing under writing-museum/ is read here."""
    url = f"http://{HOST}:{museum_port}/"
    return {
        "url": url,
        "library": url + "web/explore.html",
        "viewer": url + "web/index.html",
        "command": f"python -m http.server {museum_port} --bind {HOST} --directory writing-museum",
        "built": (repo / "writing-museum" / "data" / "library.json").is_file(),
        "build": "python writing-museum/build/build_museum.py build",
    }


def new_run(env, body):
    """A run through the bookkeeper's own command. Returns the summary and the
    skill invocation to paste into a Claude Code session."""
    pipeline = str(body.get("pipeline", "")).strip()
    title = " ".join(str(body.get("title", "")).split())
    if not pipeline or not title:
        raise Usage("a run needs a pipeline and a title")
    env.pipeline(pipeline)
    args = argparse.Namespace(pipeline=pipeline, title=title, run_id=None, note=None)
    import contextlib
    import io
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        studio_run.cmd_new(env, args)
    run_id = next(line.split()[1] for line in out.getvalue().splitlines() if line.startswith("run "))
    state = studio_common.load_state(env, run_id)
    return {
        "run": studio_run.summary(env, state),
        "command": f"/studio-pipeline resume run {run_id}",
        "note": "Paste the command into a Claude Code session opened on the repo. "
                "The hub keeps the books; the session does the work.",
    }


class Handler(SimpleHTTPRequestHandler):
    server_version = "rosw-hub/1"

    def __init__(self, *args, env=None, repo=None, index_path=None, museum_port=DEFAULT_MUSEUM_PORT, **kwargs):
        self.env = env
        self.repo = repo
        self.index_path = index_path
        self.museum_port = museum_port
        super().__init__(*args, directory=str(HERE), **kwargs)

    # ── static files: this folder only ───────────────────────────────────
    def translate_path(self, path):
        translated = Path(super().translate_path(path)).resolve()
        try:
            translated.relative_to(HERE)
        except ValueError:
            return str(HERE / "index.html") + ".refused"  # a path that cannot exist
        return str(translated)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def log_message(self, format, *args):
        if self.server.quiet:
            return
        super().log_message(format, *args)

    # ── JSON ─────────────────────────────────────────────────────────────
    def send_json(self, payload, status=HTTPStatus.OK):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parts = urlsplit(self.path)
        if not parts.path.startswith("/api/"):
            return super().do_GET()
        query = parse_qs(parts.query)
        try:
            route = parts.path[len("/api/"):]
            if route == "notes":
                return self.send_json(vault_index.note_rows(self.env))
            if route == "search":
                q = (query.get("q") or [""])[0]
                index = vault_index.load_index(self.index_path)
                hits = vault_index.search_index(index, q, top=int((query.get("top") or ["8"])[0]),
                                                kind=(query.get("kind") or [None])[0],
                                                status=(query.get("status") or [None])[0])
                return self.send_json([{"score": round(score, 4), **vault_index.chunk_public(chunk)}
                                       for score, chunk in hits])
            if route == "runs":
                return self.send_json(runs_view(self.env))
            if route == "gates":
                return self.send_json(gates_view(self.env))
            if route == "pipelines":
                return self.send_json(pipelines_view(self.env))
            if route == "writing":
                return self.send_json(writing_view(self.repo))
            if route == "museum":
                return self.send_json(museum_view(self.repo, self.museum_port))
            if route == "tokens":
                return self.send_json(json.loads(read_text(self.env.context / self.env.spec["tokens"]["file"])))
            if route == "mark":
                return self.send_json({"mark": MARK})
        except (Usage, Refused, ValueError) as problem:
            return self.send_json({"error": str(problem)}, HTTPStatus.BAD_REQUEST)
        return self.send_json({"error": "no such route"}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parts = urlsplit(self.path)
        if parts.path != "/api/runs":
            return self.send_json({"error": "no such route"}, HTTPStatus.NOT_FOUND)
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(body, dict):
                raise Usage("the body is a JSON object")
            return self.send_json(new_run(self.env, body), HTTPStatus.CREATED)
        except json.JSONDecodeError:
            return self.send_json({"error": "the body is not JSON"}, HTTPStatus.BAD_REQUEST)
        except (Usage, Refused) as problem:
            return self.send_json({"error": str(problem)}, HTTPStatus.BAD_REQUEST)


def make_server(port=DEFAULT_PORT, env=None, repo=REPO, index_path=None, quiet=False, museum_port=DEFAULT_MUSEUM_PORT):
    env = env or Env()
    index_path = Path(index_path) if index_path else vault_index.DEFAULT_INDEX
    handler = partial(Handler, env=env, repo=Path(repo), index_path=index_path, museum_port=int(museum_port))
    server = ThreadingHTTPServer((HOST, port), handler)
    server.quiet = quiet
    return server


def main(argv=None):
    parser = argparse.ArgumentParser(prog="serve.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--museum-port", type=int, default=DEFAULT_MUSEUM_PORT,
                        help="where the Writing Museum's own server is expected (the hub links to it, never serves it)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    try:
        server = make_server(args.port, quiet=args.quiet, museum_port=args.museum_port)
    except OSError as problem:
        print(f"error     cannot bind {HOST}:{args.port}: {problem}", file=sys.stderr)
        return 2
    print(f"{MARK} at http://{HOST}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
