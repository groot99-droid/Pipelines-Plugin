"""The brushes MCP server: JSON-RPC 2.0 over stdio (brushes/docs/CONTRACTS.md,
F10 "MCP").

    python brushes/pipeline/mcp_server.py [--export-dir D] [--defer-to-project D] [--selftest]

This build is a stub. It speaks the protocol and registers one tool,
library_status, so that the wiring (the repository's .mcp.json, the client's
spawn directory, the `python` command) can be checked by hand before anything
is built behind it. Search, previews and the settings tools arrive as rows of
the TOOLS table; the dispatcher does not change when they do.

The wire
    One JSON value per line in each direction, both streams used in binary.
    Input is UTF-8. Output is one compact JSON object, written in ASCII (any
    other character is a \\uXXXX escape, so it is still UTF-8), ended by one
    "\\n", and it never holds a "\\r".
    Nothing but protocol messages goes to stdout: once the wire handle is
    taken, sys.stdout points at stderr, so a stray print cannot corrupt a
    reply. Diagnostics go to stderr.
    End of input, a client that went away and Ctrl-C all end the server with
    exit code 0.

What is answered
    invalid JSON, or bytes that are not UTF-8      error -32700, id null
    not an object, wrong `jsonrpc`, no `method`    error -32600
    an array                                       each element; empty is -32600
    no `id` (a notification)                       nothing
    initialize                                     the client's protocol version
                                                   when it is one of
                                                   PROTOCOL_VERSIONS, else
                                                   DEFAULT_PROTOCOL_VERSION
    ping                                           {}
    tools/list                                     {"tools": [...]}
    tools/call                                     a result; -32602 when `name`
                                                   is missing, `arguments` is
                                                   not an object, or the tool is
                                                   unknown
    anything else                                  error -32601

A tool that fails (a bad argument value, a refusal of its own, an unexpected
exception) still answers with a result: `isError` true and one text block
{"error": {"code", "message", "hint"}}, never a traceback. That is what lets
the model on the other end correct itself.

`dispatch(message, context)` is the whole protocol as a function of its two
arguments: it reads no stream and keeps no state, so the tests call it
directly. `handle_line` adds the bytes on either side, `serve` the loop.

The server writes nothing. --export-dir is accepted and not used: no export
tool is registered in this build. It never exits because data is missing.

Standard library only.
"""

from __future__ import annotations

import sys

if __name__ == "__main__":
    # A server that writes nothing leaves no __pycache__ behind either. Set
    # before the sibling import below, and only when this file is the program:
    # a test that imports the module keeps its own setting.
    sys.dont_write_bytecode = True

import argparse
import json
import math
import os
import re
import traceback
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402

SERVER_NAME = "rosw-brushes"
SERVER_TITLE = "ROSW Brushes"
SERVER_VERSION = "0.1.0"
# What stands behind the protocol today. A later build drops the word.
STAGE = "stub"

# The revisions the initialize handshake can settle on, oldest first, and the
# one offered to a client that asks for anything else. These are the handshake
# revisions of the MCP Python SDK 2.2.0 (mcp_types.version); the newer
# per-request revision is reached through `server/discover`, which this server
# answers with -32601, and a client then falls back to initialize.
PROTOCOL_VERSIONS = ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25")
DEFAULT_PROTOCOL_VERSION = "2025-11-25"

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# The longest line read. A longer one is drained and answered with -32600.
MAX_LINE = 64 * 1024 * 1024

INSTRUCTIONS = (
    "The ROSW brush library: Procreate brush sets kept under brushes/ in the ROSW "
    "repository. This build of the server is a stub with one read-only tool, "
    "library_status, which reports where the data folders are, whether the library of "
    "original files, the catalog and the search index exist, how many files the "
    "library holds, and which commands would make what is missing. Search, previews and "
    "the settings tools are not built yet."
)
STAND_DOWN_INSTRUCTIONS = (
    "This copy of the brushes server was started by an installed plugin and has stood "
    "down: the open project has its own brushes server (brushes/pipeline/mcp_server.py, "
    "declared in the project's .mcp.json), and that one is the authority. This copy "
    "lists no tools."
)


# ── the tool table ───────────────────────────────────────────────────────────

class Tool(NamedTuple):
    """One row of the registry. A later build adds rows; nothing else changes.

    handler(arguments, context) returns the payload, a JSON value that becomes
    the result's one text block, or a ToolOutput when it also has image blocks.
    It refuses by raising ToolError.
    """

    name: str
    title: str
    description: str
    input_schema: dict
    handler: object
    read_only: bool = True
    needs_export_dir: bool = False      # listed only when started with --export-dir
    meta: object = None                 # the tool's `_meta`, when it has one


class ToolOutput(NamedTuple):
    """A payload plus further content blocks, for a tool that returns images."""

    payload: object
    blocks: tuple = ()


class ToolError(Exception):
    """A tool's own refusal. It becomes a result with `isError` true, never a
    protocol error. Any exception that carries a string `code` and a string
    `message` (and optionally `hint`) is reported the same way."""

    def __init__(self, code, message, hint=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint


class Context(NamedTuple):
    """Everything a reply may depend on besides the message itself."""

    paths: bc.Paths
    tools: dict
    export_dir: object = None           # parsed and carried; nothing reads it yet
    stand_down: bool = False
    mode: str = "project"               # "project" | "snapshot"
    log: object = None                  # log(text) for diagnostics, or None


def tool_table(*tools):
    """{name: Tool} in the order given. A name used twice is a mistake."""
    table = {}
    for tool in tools:
        if tool.name in table:
            raise ValueError(f"the tool {tool.name} is registered twice")
        table[tool.name] = tool
    return table


def make_context(paths=None, *, tools=None, export_dir=None, stand_down=False, mode="project",
                 log=None):
    return Context(paths=paths if paths is not None else bc.resolve_paths(),
                   tools=TOOLS if tools is None else tools, export_dir=export_dir,
                   stand_down=stand_down, mode=mode, log=log)


def listed_tools(context):
    """The rows this server offers now, in table order."""
    if context.stand_down:
        return {}
    return {name: tool for name, tool in context.tools.items()
            if context.export_dir is not None or not tool.needs_export_dir}


def describe_tool(tool):
    """A registry row as tools/list shows it."""
    if tool.read_only:
        annotations = {"readOnlyHint": True, "openWorldHint": False}
    else:
        annotations = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False,
                       "openWorldHint": False}
    entry = {"name": tool.name, "title": tool.title, "description": tool.description,
             "inputSchema": tool.input_schema, "annotations": annotations}
    if tool.meta:
        entry["_meta"] = dict(tool.meta)
    return entry


# ── library_status ───────────────────────────────────────────────────────────

LIBRARY_HALVES = ("user", "official")
STATUS_ROOTS = ("root", "library", "catalog", "vault", "index")
INDEX_STATES = ("fresh", "stale", "memory", "not_ingested")     # docs/CONTRACTS.md, F10
MODES = ("project", "snapshot")
NO_ARGUMENTS = {"type": "object", "properties": {}, "additionalProperties": False}
# (what is missing, the script that makes it, the verb, whether that verb is
# built). The path is under the brushes/ folder that holds this code. A writer
# is named in its dry-run form: the status never tells anyone to pass --confirm.
#
# A command is advertised only when the last column says its verb exists: a
# status that names a command which then exits 2 sends its reader nowhere. The
# column is not looked up at run time, because this server opens no file and
# imports no other script; test_mcp_server.py runs every row's `<verb> --help`
# and fails when the column and the script disagree, in either direction.
NEXT_STEPS = (
    ("official", "pipeline/fetch_base_library.py", "fetch", True),
    ("catalog", "pipeline/ingest.py", "build", False),          # ingest.py has `where` and `adopt` today
    ("index", "vault/tools/brush_search.py", "index", False),   # the search tool is not written yet
)


def repo_relative(path, base):
    """A path as the status reports it: POSIX and relative to `base`, the folder
    that holds the data root (in a checkout, the repository root).

    A folder that a flag or a variable moved outside `base` is shown with
    leading `..` segments. On another drive there is no relative form, and only
    then is the absolute path given.
    """
    path, base = Path(path), Path(base)
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        pass
    try:
        return Path(os.path.relpath(path, base)).as_posix()
    except ValueError:
        return path.as_posix()


def count_files(folder):
    """How many files sit under a folder, at any depth, and how many of them are
    named as brush sets and as single brushes. By name only: no file is opened,
    so a Git LFS pointer counts like the file it stands for. A missing folder
    counts as empty."""
    counts = {"files": 0, "brushset": 0, "brush": 0}
    for _folder, _subfolders, names in os.walk(folder):
        for name in names:
            counts["files"] += 1
            lowered = name.lower()
            if lowered.endswith(".brushset"):
                counts["brushset"] += 1
            elif lowered.endswith(".brush"):
                counts["brush"] += 1
    return counts


def next_steps(missing, tool_root=None, steps=NEXT_STEPS):
    """The commands that would make what is missing, in the order to run them.
    A command is listed only when its verb is built and its script is on disk:
    a status never points at a file that is not there, nor at a verb the script
    does not have."""
    tool_root = Path(tool_root) if tool_root is not None else bc.TOOL_ROOT
    listed = []
    for what, script, verb, built in steps:
        if built and what in missing and (tool_root / script).is_file():
            listed.append(f"python {tool_root.name}/{script} {verb}")
    return listed


def library_status(arguments, context):
    """Where the server reads from and what is there. Reads folder listings and
    nothing else.

    The keys are the frozen ones of docs/CONTRACTS.md, F10. What only this stub
    build reports (its stage, every resolved folder, what exists) sits under
    the one extra key `stub`, which goes when the stub does. Two frozen values
    are placeholders here, because this build opens no file: `counts` (the
    catalog's own counts) is null, and `vocabulary_axes` is empty.
    """
    paths = context.paths
    base = paths.root.parent

    def shown(path):
        return repo_relative(path, base)

    catalog_file = paths.catalog / "catalog.json"
    exists = {"root": paths.root.is_dir(), "library": paths.library.is_dir(),
              "catalog": catalog_file.is_file(), "vault": paths.vault.is_dir(),
              "index": paths.index.is_file()}
    library_files = {half: count_files(paths.library / half) for half in LIBRARY_HALVES}
    brush_files = {half: library_files[half]["brushset"] + library_files[half]["brush"]
                   for half in LIBRARY_HALVES}
    # One of INDEX_STATES, always. This build cannot tell fresh from stale, so
    # an index file it has not checked is reported as stale, never as fresh.
    if not exists["catalog"]:
        index = {"state": "not_ingested", "reason": f"no catalog: {shown(catalog_file)} is missing"}
    elif not exists["index"]:
        index = {"state": "memory", "reason": f"no index file: {shown(paths.index)} is missing"}
    else:
        index = {"state": "stale",
                 "reason": f"not checked: this build does not load the index ({shown(paths.index)} "
                           "is on disk); it is reported stale until a build can check it"}
    missing = [what for what, absent in (("official", not brush_files["official"]),
                                         ("catalog", not exists["catalog"]),
                                         ("index", not exists["index"])) if absent]
    return {
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "mode": context.mode,
        "root": shown(paths.root),
        "index": index,
        "counts": None,
        "library_present": sum(brush_files.values()) > 0,
        "library_files": library_files,
        "vocabulary_axes": [],
        "export": {"enabled": False, "dir": None},
        "next_steps": next_steps(missing),
        "stub": {
            "stage": STAGE,
            "roots": {name: shown(getattr(paths, name)) for name in STATUS_ROOTS},
            "exists": exists,
            "not_read": ["counts", "vocabulary_axes"],
        },
    }


TOOLS = tool_table(
    Tool(
        name="library_status",
        title="Brush library status",
        description=(
            "Where this server reads the brush library from, and what is there. Returns the "
            "data root as a path relative to the repository root (the folder that holds "
            "brushes/), the state of the search index (not_ingested when there is no catalog), "
            "how many files sit under library/user and library/official, counted by name "
            "(`library_files`), and the commands that would make what is missing. This stub "
            "build also reports, under `stub`, every data folder and whether the library, the "
            "generated catalog (catalog/catalog.json), the vault and the index exist; it does "
            "not read the catalog, so `counts` is null. Takes no arguments and reads folder "
            "listings only."),
        input_schema=NO_ARGUMENTS,
        handler=library_status,
    ),
)


# ── argument checking ────────────────────────────────────────────────────────

_PLAIN_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool}


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_arguments(value, schema, where="arguments"):
    """The first way `value` breaks `schema`, as a sentence, or None.

    The part of JSON Schema the tool table uses: type, enum, minimum, maximum,
    minLength, maxLength, pattern (searched), minItems, maxItems, items,
    properties, required, additionalProperties false. A whole float passes for
    an integer; a number must be finite.
    """
    kind = schema.get("type")
    if kind == "integer":
        fits = _is_number(value) and (isinstance(value, int) or value.is_integer())
    elif kind == "number":
        fits = _is_number(value) and math.isfinite(value)
    elif kind in _PLAIN_TYPES:
        fits = isinstance(value, _PLAIN_TYPES[kind])
    else:
        fits = True
    if not fits:
        return f"{where} must be of type {kind}"
    if "enum" in schema and value not in schema["enum"]:
        return f"{where} must be one of: {', '.join(str(choice) for choice in schema['enum'])}"
    if _is_number(value):
        if "minimum" in schema and value < schema["minimum"]:
            return f"{where} must be at least {schema['minimum']}"
        if "maximum" in schema and value > schema["maximum"]:
            return f"{where} must be at most {schema['maximum']}"
    elif isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            return f"{where} must have at least {schema['minLength']} characters"
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            return f"{where} must have at most {schema['maxLength']} characters"
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            return f"{where} must match {schema['pattern']}"
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            return f"{where} must have at least {schema['minItems']} items"
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            return f"{where} must have at most {schema['maxItems']} items"
        if isinstance(schema.get("items"), dict):
            for position, item in enumerate(value):
                problem = check_arguments(item, schema["items"], f"{where}[{position}]")
                if problem:
                    return problem
    elif isinstance(value, dict):
        properties = schema.get("properties") or {}
        for name in schema.get("required", ()):
            if name not in value:
                return f"{where} needs `{name}`"
        for name, item in value.items():
            if name in properties:
                problem = check_arguments(item, properties[name], f"{where}.{name}")
                if problem:
                    return problem
            elif schema.get("additionalProperties") is False:
                known = ", ".join(properties) or "none"
                return f"{where} has no `{_clip(name)}` (it takes: {known})"
    return None


# ── the dispatcher ───────────────────────────────────────────────────────────

class _Refused(Exception):
    """A request the protocol refuses: it becomes a JSON-RPC error."""

    def __init__(self, code, message, data=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


def _clip(text, limit=200):
    text = str(text)
    return text if len(text) <= limit else text[:limit] + "..."


def _error(request_id, code, message, data=None):
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def _log(context, text):
    if context.log is not None:
        context.log(text)


def _text_block(payload):
    """A payload as the one text block of a result: compact JSON with real
    characters. A lone surrogate, which no UTF-8 reader accepts, becomes `?`."""
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return {"type": "text", "text": text.encode("utf-8", "replace").decode("utf-8")}


def _tool_failure(code, message, hint=None):
    return {"content": [_text_block({"error": {"code": code, "message": message, "hint": hint}})],
            "isError": True}


def _initialize(params, context):
    asked = params.get("protocolVersion")
    known = isinstance(asked, str) and asked in PROTOCOL_VERSIONS
    return {
        "protocolVersion": asked if known else DEFAULT_PROTOCOL_VERSION,
        "capabilities": {"tools": {"listChanged": False}},
        "serverInfo": {"name": SERVER_NAME, "title": SERVER_TITLE, "version": SERVER_VERSION},
        "instructions": STAND_DOWN_INSTRUCTIONS if context.stand_down else INSTRUCTIONS,
    }


def _ping(params, context):
    return {}


def _tools_list(params, context):
    # No pagination: the whole table is one page, and a `cursor` is ignored.
    return {"tools": [describe_tool(tool) for tool in listed_tools(context).values()]}


def _tools_call(params, context):
    name = params.get("name")
    if not isinstance(name, str) or not name:
        raise _Refused(INVALID_PARAMS, "tools/call needs the tool's `name`, a string")
    arguments = params.get("arguments")
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        raise _Refused(INVALID_PARAMS, "`arguments` must be an object")
    tool = listed_tools(context).get(name)
    if tool is None:
        raise _Refused(INVALID_PARAMS, f"unknown tool: {_clip(name)}", _clip(name))
    problem = check_arguments(arguments, tool.input_schema)
    if problem:
        return _tool_failure("bad_argument", problem,
                             f"tools/list shows the arguments {name} takes")
    try:
        output = tool.handler(arguments, context)
        payload, blocks = output if isinstance(output, ToolOutput) else (output, ())
        return {"content": [_text_block(payload), *blocks], "isError": False}
    except Exception as exc:                    # a tool never takes the server down
        code, message = getattr(exc, "code", None), getattr(exc, "message", None)
        if isinstance(code, str) and isinstance(message, str):
            return _tool_failure(code, message, getattr(exc, "hint", None))
        _log(context, f"{name} failed:\n"
                      + "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        return _tool_failure("internal", f"{name} failed unexpectedly",
                             "the server's stderr log has the details")


METHODS = {
    "initialize": _initialize,
    "ping": _ping,
    "tools/list": _tools_list,
    "tools/call": _tools_call,
}


def _dispatch_one(message, context):
    if not isinstance(message, dict):
        return _error(None, INVALID_REQUEST, "a message must be a JSON object")
    request_id = message.get("id")
    id_fits = isinstance(request_id, (str, int)) and not isinstance(request_id, bool)
    echo = request_id if id_fits else None
    method = message.get("method")
    if not isinstance(method, str):
        if "result" in message or "error" in message:
            return None                         # a response; this server asks nothing
        return _error(echo, INVALID_REQUEST, "a request needs a `method`, a string")
    if message.get("jsonrpc") != "2.0":
        return _error(echo, INVALID_REQUEST, '`jsonrpc` must be "2.0"')
    if "id" not in message:
        return None                             # a notification is never answered
    if not id_fits:
        return _error(None, INVALID_REQUEST, "`id` must be a string or an integer")
    params = message.get("params")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return _error(request_id, INVALID_PARAMS, "`params` must be an object")
    handler = METHODS.get(method)
    if handler is None:
        return _error(request_id, METHOD_NOT_FOUND, f"method not found: {_clip(method)}",
                      _clip(method))
    try:
        result = handler(params, context)
    except _Refused as refusal:
        return _error(request_id, refusal.code, refusal.message, refusal.data)
    except Exception as exc:                    # a mistake in this file, not in the request
        _log(context, f"{method} failed:\n"
                      + "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        return _error(request_id, INTERNAL_ERROR, "internal error")
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def dispatch(message, context):
    """One decoded JSON-RPC message in; the reply out.

    Returns a dict, a list (the replies to a batch), or None when nothing is to
    be sent. It reads no stream and keeps nothing between calls: the reply
    depends on the message, the context, and what a tool finds on disk.
    """
    if isinstance(message, list):
        if not message:
            return _error(None, INVALID_REQUEST, "an empty batch")
        replies = [reply for reply in (_dispatch_one(item, context) for item in message)
                   if reply is not None]
        return replies or None
    return _dispatch_one(message, context)


# ── the wire ─────────────────────────────────────────────────────────────────

def _refuse_constant(name):
    raise ValueError(f"{name} is not JSON")


def encode(message):
    """A protocol message as one line: compact, ASCII, ended by one newline."""
    return json.dumps(message, ensure_ascii=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii") + b"\n"


def handle_line(line, context):
    """One line of input, as bytes, to one line of output, or None for no reply."""
    line = line.strip(b" \t\r\n")
    if not line:
        return None
    try:
        message = json.loads(line.decode("utf-8"), parse_constant=_refuse_constant)
    except (ValueError, RecursionError):        # bad UTF-8 and bad JSON are both ValueError
        return encode(_error(None, PARSE_ERROR, "parse error: a line must be one JSON value in UTF-8"))
    reply = dispatch(message, context)
    if reply is None:
        return None
    try:
        return encode(reply)
    except (TypeError, ValueError):
        _log(context, "a reply could not be written as JSON")
        return encode(_error(None, INTERNAL_ERROR, "internal error: the reply could not be encoded"))


def serve(rfile, wfile, context, *, max_line=MAX_LINE):
    """Answer lines from `rfile` on `wfile` until the input ends. Returns 0:
    end of input and a client that stopped reading are both a normal end."""
    while True:
        line = rfile.readline(max_line + 1)
        if not line:
            return bc.EXIT_OK
        if len(line) > max_line and not line.endswith(b"\n"):
            while line and not line.endswith(b"\n"):
                line = rfile.readline(65536)
            reply = encode(_error(None, INVALID_REQUEST, f"a message may be at most {max_line} bytes"))
        else:
            reply = handle_line(line, context)
        if reply is None:
            continue
        try:
            wfile.write(reply)
            wfile.flush()
        except OSError:                         # BrokenPipeError among them
            _log(context, "the client stopped reading; ending")
            return bc.EXIT_OK


# ── starting ─────────────────────────────────────────────────────────────────

def should_stand_down(defer_to, own_file=None):
    """Whether --defer-to-project names a project that has its own copy of this
    server. A missing folder, or a `${...}` the client did not expand, means
    serve normally; so does a project whose copy is this very file."""
    if not defer_to or "${" in str(defer_to):
        return False
    try:
        theirs = (Path(defer_to) / "brushes" / "pipeline" / "mcp_server.py").resolve()
        return theirs.is_file() and theirs != Path(own_file or __file__).resolve()
    except OSError:
        return False


def running_mode(defer_to, own_file=None):
    """`snapshot` for the copy an installed plugin starts, `project` for a
    checkout's own. Three signs of the plugin's copy: its entry is the one that
    passes --defer-to-project; it sits under CLAUDE_PLUGIN_ROOT; or it sits
    under a `.claude/plugins/` folder, where installed plugins are kept."""
    if defer_to is not None:
        return "snapshot"
    try:
        own = Path(own_file or __file__).resolve()
    except OSError:
        return "project"
    parts = [part.lower() for part in own.parts]
    if (".claude", "plugins") in zip(parts, parts[1:]):
        return "snapshot"
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "").strip()
    if plugin_root and "${" not in plugin_root:
        try:
            own.relative_to(Path(plugin_root).resolve())
            return "snapshot"
        except (OSError, ValueError):
            pass
    return "project"


def selftest(context, write=print):
    """A handshake run in this process, through the same bytes-in, bytes-out
    path the pipes use. Prints one line per step, then PASS or FAIL."""
    failed = []

    def ask(message):
        raw = handle_line(json.dumps(message, ensure_ascii=False).encode("utf-8") + b"\n", context)
        return raw, (None if raw is None else json.loads(raw.decode("ascii")))

    def check(label, passed, detail=""):
        write(("ok    " if passed else "FAIL  ") + label + (f": {detail}" if detail else ""))
        if not passed:
            failed.append(label)

    try:
        _, reply = ask({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": PROTOCOL_VERSIONS[-2], "capabilities": {},
            "clientInfo": {"name": "sélftest \U0001f4a7", "version": "0"}}})
        result = reply.get("result", {})
        check("initialize answers with the client's protocol version",
              result.get("protocolVersion") == PROTOCOL_VERSIONS[-2]
              and result.get("serverInfo", {}).get("name") == SERVER_NAME
              and "tools" in result.get("capabilities", {}), str(result.get("protocolVersion")))
        _, reply = ask({"jsonrpc": "2.0", "id": 2, "method": "initialize",
                        "params": {"protocolVersion": "1999-01-01"}})
        check("initialize offers its default for a version it does not know",
              reply.get("result", {}).get("protocolVersion") == DEFAULT_PROTOCOL_VERSION,
              DEFAULT_PROTOCOL_VERSION)
        raw, _ = ask({"jsonrpc": "2.0", "method": "notifications/initialized"})
        check("a notification gets no reply", raw is None)
        _, reply = ask({"jsonrpc": "2.0", "id": 3, "method": "ping"})
        check("ping", reply.get("result") == {})
        _, reply = ask({"jsonrpc": "2.0", "id": 4, "method": "tools/list"})
        names = [tool.get("name") for tool in reply.get("result", {}).get("tools", [])]
        check("tools/list", names == list(listed_tools(context)), ", ".join(names) or "no tools")
        if "library_status" in names:
            _, reply = ask({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                            "params": {"name": "library_status", "arguments": {}}})
            result = reply.get("result", {})
            status = json.loads(result["content"][0]["text"])
            files = status["library_files"]
            check("tools/call library_status",
                  result.get("isError") is False and status["server"] == SERVER_NAME
                  and status["index"]["state"] in INDEX_STATES and status["mode"] in MODES,
                  f"mode {status['mode']}, root {status['root']}, "
                  f"library/user {files['user']['files']} files, "
                  f"library/official {files['official']['files']} files, "
                  f"index {status['index']['state']}, "
                  f"next steps {len(status['next_steps'])}")
        _, reply = ask({"jsonrpc": "2.0", "id": 6, "method": "resources/list"})
        check("an unknown method is -32601", reply.get("error", {}).get("code") == METHOD_NOT_FOUND)
        reply = json.loads(handle_line(b"{not json\n", context).decode("ascii"))
        check("malformed JSON is -32700",
              reply.get("error", {}).get("code") == PARSE_ERROR and reply.get("id") is None)
        raw, reply = ask({"jsonrpc": "2.0", "id": "é\U0001f4a7", "method": "ping"})
        check("a non-ASCII id comes back intact on one ASCII line",
              reply.get("id") == "é\U0001f4a7" and raw.isascii()
              and raw.endswith(b"\n") and raw.count(b"\n") == 1 and b"\r" not in raw)
    except Exception as exc:                    # a broken reply shape must read FAIL, not a traceback
        check("the selftest ran to its end", False, f"{type(exc).__name__}: {exc}")
    write("PASS" if not failed else "FAIL")
    return bc.EXIT_OK if not failed else bc.EXIT_REFUSED


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mcp_server.py", allow_abbrev=False,
        description="The brushes MCP server: JSON-RPC 2.0 over stdio, read-only. "
                    "Started by an MCP client; see the repository's .mcp.json.")
    bc.add_path_arguments(parser)
    parser.add_argument("--export-dir", metavar="DIR", default=None,
                        help="the one folder an export tool may write into. Accepted and not "
                             "used by this build: no export tool is registered")
    parser.add_argument("--defer-to-project", metavar="DIR", default=None,
                        help="stand down (list no tools) when DIR is a project with its own "
                             "brushes/pipeline/mcp_server.py; for the copy a plugin starts")
    parser.add_argument("--selftest", action="store_true",
                        help="run a handshake in this process, print PASS or FAIL, and exit 0 or 1")
    return parser


def _stderr_log(text):
    try:
        print(f"[{SERVER_NAME}] {text}", file=sys.stderr, flush=True)
    except (OSError, ValueError):
        pass


def main(argv=None):
    bc.open_console()
    args = build_parser().parse_args(argv)
    paths = bc.paths_from_args(args)
    stand_down = should_stand_down(args.defer_to_project)
    context = make_context(paths, export_dir=Path(args.export_dir) if args.export_dir else None,
                           stand_down=stand_down, mode=running_mode(args.defer_to_project),
                           log=_stderr_log)
    if args.selftest:
        return selftest(context)

    wire_in = getattr(sys.stdin, "buffer", None)
    wire_out = getattr(sys.stdout, "buffer", None)
    if wire_in is None or wire_out is None:
        _stderr_log("stdin and stdout must be byte streams; this server is started by an MCP client")
        return bc.EXIT_USAGE
    # From here on the wire is the only way to the client's stdout.
    sys.stdout = sys.stderr
    reconfigure = getattr(sys.stderr, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(errors="backslashreplace")
    _stderr_log(f"{SERVER_VERSION} ({STAGE}) serving {paths.root} over stdio, mode {context.mode}"
                + (", standing down: the project has its own server" if stand_down else ""))
    if args.export_dir:
        _stderr_log("--export-dir is accepted and not used: no export tool is registered in this build")
    try:
        return serve(wire_in, wire_out, context)
    except KeyboardInterrupt:
        return bc.EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
