"""The brushes MCP server: JSON-RPC 2.0 over stdio (brushes/docs/CONTRACTS.md,
F10 "MCP").

    python -I brushes/pipeline/mcp_server.py [--export-dir D] [--defer-to-project D] [--selftest]

Nine read-only tools, one row each of the TOOLS table, over pipeline/service.py:
library_status, search_brushes, get_brush, similar_brushes, list_sets,
list_vocabulary, get_preview, get_brush_settings_schema and
validate_settings_patch. A tenth, export_brush, is listed only when the server
is started with --export-dir DIR, and then it is the one way this server
writes: `confirm: false` is a dry run, `confirm: true` writes
`<ascii-slug>-<id8>.brush` inside DIR and never over a file (service.write_export,
F12). Without --export-dir the server writes nothing.

Run it with `python -I`: it opens library originals, and a brush file is data
from a stranger (docs/CONTRACTS.md, section 0).

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

This file opens no file and writes none: everything that touches the disk is in
service.py. It never exits because data is missing: library_status says what is
absent and which commands would make it.

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
import service  # noqa: E402
from service import (  # noqa: E402,F401  (re-exported: the tests and the spec test read them here)
    INDEX_STATES, LIBRARY_HALVES, MCP_TOP_MAX, MODES, NEXT_STEPS, ApiError, count_files, next_steps,
    repo_relative)

SERVER_NAME = service.SERVER_NAME
SERVER_TITLE = "ROSW Brushes"
SERVER_VERSION = service.SERVER_VERSION

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
    "repository, with a catalog, a note per set, previews and a search index. Start with "
    "library_status: it says whether the library, the catalog and the index exist and which "
    "commands would make what is missing. search_brushes finds brushes by words, tags "
    "(axis=value) and facet filters (key=value); similar_brushes finds brushes with alike "
    "settings; get_brush, list_sets, list_vocabulary and get_preview read what is stored; "
    "get_brush_settings_schema describes every setting; validate_settings_patch checks a "
    "change and returns a patch to paste into the designer app. These tools are read-only. "
    "Tag words and `visual` sentences are descriptions of previews, not measurements."
)
EXPORT_INSTRUCTIONS = (
    " This server was started with an export folder, so export_brush is listed too: it writes a "
    "changed library brush as a .brush file into that folder (a dry run unless confirm is true) and "
    "never over an existing file. It is the only tool that writes. Nothing it writes is known to "
    "open in Procreate."
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
    export_dir: object = None           # the one folder export_brush writes into, or None
    stand_down: bool = False
    mode: str = "project"               # "project" | "snapshot"
    log: object = None                  # log(text) for diagnostics, or None
    service: object = None              # the BrushService the tools read through


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
    paths = paths if paths is not None else bc.resolve_paths()
    return Context(paths=paths, tools=TOOLS if tools is None else tools, export_dir=export_dir,
                   stand_down=stand_down, mode=mode, log=log,
                   service=service.BrushService(paths, mode=mode, export_dir=export_dir, log=log))


def service_of(context):
    """The context's service; one is made when a context was built by hand."""
    if context.service is not None:
        return context.service
    return service.BrushService(context.paths, mode=context.mode, export_dir=context.export_dir,
                                log=context.log)


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


# ── the tools ────────────────────────────────────────────────────────────────
# Each handler is a few lines over service.py; the payloads are the service's.

NO_ARGUMENTS = {"type": "object", "properties": {}, "additionalProperties": False}
BRUSH_ID = {"type": "string", "pattern": "^b_[0-9a-f]{12}$"}
TAG_ITEM = {"type": "string", "maxLength": 80, "pattern": "^[a-z][a-z_]*=[a-z0-9][a-z0-9,-]*$"}
FILTER_ITEM = {"type": "string", "maxLength": 120}
RESULT_SIZE = {"anthropic/maxResultSizeChars": 120000}


def library_status(arguments, context):
    """Where the server reads from and what is there: the payload of F10, from
    service.BrushService.status. It reads folder listings, the catalog's counts,
    the vocabulary and the index state, and opens no brush file."""
    return service_of(context).status()


def search_brushes(arguments, context):
    return service_of(context).search(
        arguments.get("query", ""), arguments.get("tags"), arguments.get("where"),
        arguments.get("where_not"), arguments.get("top", 8), 0, top_max=MCP_TOP_MAX, require_filter=True)


def get_brush(arguments, context):
    return service_of(context).get_brush(arguments["id"], arguments.get("include"))


def similar_brushes(arguments, context):
    return service_of(context).similar(arguments["id"], arguments.get("top", 8), arguments.get("where"),
                                       arguments.get("where_not"), top_max=MCP_TOP_MAX)


def list_sets(arguments, context):
    return service_of(context).list_sets(arguments.get("library"))


def list_vocabulary(arguments, context):
    return service_of(context).vocabulary(arguments.get("axis"))


def get_preview(arguments, context):
    payload, files = service_of(context).preview_set(arguments["id"], arguments.get("kinds") or ["stroke"])
    blocks = tuple({"type": "image", "data": service.b64(data), "mimeType": "image/png"}
                   for _, data in files)
    return ToolOutput(payload, blocks)


def get_brush_settings_schema(arguments, context):
    return service_of(context).settings_schema(arguments.get("group"), arguments.get("keys"),
                                               arguments.get("detail", "compact"))


def validate_settings_patch(arguments, context):
    return service_of(context).validate_patch(arguments["changes"], arguments.get("base_id"),
                                               arguments.get("base"), arguments.get("era"))


def export_brush(arguments, context):
    return service_of(context).export_brush(arguments["base_id"], arguments.get("changes"),
                                            arguments.get("name"), arguments.get("confirm", False))


TOOLS = tool_table(
    Tool(
        name="library_status",
        title="Brush library status",
        description=(
            "Where this server reads the brush library from, and what is there. Returns the "
            "data root as a path relative to the repository root, the state of the search index "
            "(fresh, stale, memory when it is built in RAM, or not_ingested when there is no "
            "catalog), the catalog's own counts, how many files sit under library/user and "
            "library/official (counted by name), the tag axes of the vocabulary, whether export "
            "is enabled, and the commands that would make what is missing. Call it first. Takes "
            "no arguments and opens no brush file."),
        input_schema=NO_ARGUMENTS,
        handler=library_status,
    ),
    Tool(
        name="search_brushes",
        title="Search brushes",
        description=(
            "Find brushes by words, tags and facet filters. `query` is free words, ranked by TF-IDF "
            "cosine over each brush's name, set, tags, visual sentence and facet words. `tags` are "
            "axis=value filters (axes medium, mark, texture, edge, motif, use; a comma list is OR; "
            "several filters are AND), for example medium=charcoal,graphite-pencil. `where` and "
            "`where_not` are facet or setting filters: key=value, key=v1,v2 or key=MIN..MAX, for "
            "example kind=stamp or spacing=..0.05. Give at least one of query, tags, where. Returns "
            "ranked rows with brush id, set, tags, the visual sentence and where its note is; no match "
            "is an empty list, not an error. Tags and `visual` describe previews, they are not "
            "measurements; the numbers are in the settings."),
        input_schema={"type": "object", "additionalProperties": False, "properties": {
            "query": {"type": "string", "maxLength": 500},
            "tags": {"type": "array", "maxItems": 12, "items": TAG_ITEM},
            "where": {"type": "array", "maxItems": 12, "items": FILTER_ITEM},
            "where_not": {"type": "array", "maxItems": 12, "items": FILTER_ITEM},
            "top": {"type": "integer", "minimum": 1, "maximum": MCP_TOP_MAX, "default": 8}}},
        handler=search_brushes,
    ),
    Tool(
        name="get_brush",
        title="Get one brush",
        description=(
            "One brush by id: its names, the sets it is in, library, era and family, its dual (second) "
            "brush if any, the preview paths, and the other places it occurs. `include` adds parts: "
            "facets (the computed facts and facet words), tags (the six tag lists and their state), "
            "visual (the sentence describing its preview), textures (where its shape and grain come "
            "from), note (the note path, heading and line range) and settings (every archive key, "
            "read-only; large). The default is every part but settings."),
        input_schema={"type": "object", "additionalProperties": False, "required": ["id"], "properties": {
            "id": BRUSH_ID,
            "include": {"type": "array", "maxItems": 6,
                        "items": {"type": "string", "enum": ["settings", "tags", "facets", "visual",
                                                             "textures", "note"]}}}},
        handler=get_brush,
        meta=RESULT_SIZE,
    ),
    Tool(
        name="similar_brushes",
        title="Brushes with alike settings",
        description=(
            "Brushes whose settings are close to those of the brush `id` (method gower-v1: numbers "
            "scaled by the library's own spread, booleans and enums equal or not, the shape and grain "
            "images weighted most). Each result lists how many keys were compared and the keys that "
            "differ most, with both values. It compares settings, not how a stroke looks. `where` and "
            "`where_not` narrow the candidates as in search_brushes."),
        input_schema={"type": "object", "additionalProperties": False, "required": ["id"], "properties": {
            "id": BRUSH_ID,
            "top": {"type": "integer", "minimum": 1, "maximum": MCP_TOP_MAX, "default": 8},
            "where": {"type": "array", "maxItems": 12, "items": FILTER_ITEM},
            "where_not": {"type": "array", "maxItems": 12, "items": FILTER_ITEM}}},
        handler=similar_brushes,
    ),
    Tool(
        name="list_sets",
        title="List brush sets",
        description=(
            "Every brush set in the catalog: slug, id, name (verbatim), library (user or official), "
            "vendor, brush count, how many of its brushes carry tags, and where its note is. `library` "
            "narrows to one half of the library."),
        input_schema={"type": "object", "additionalProperties": False, "properties": {
            "library": {"type": "string", "enum": ["user", "official"]}}},
        handler=list_sets,
    ),
    Tool(
        name="list_vocabulary",
        title="Tag vocabulary and facets",
        description=(
            "The closed tag vocabulary (six axes, each tag with its definition) that the tags filter of "
            "search_brushes accepts, and the facets that where filters accept, with their value ranges "
            "from the catalog. `axis` limits it to one axis."),
        input_schema={"type": "object", "additionalProperties": False, "properties": {
            "axis": {"type": "string", "maxLength": 40}}},
        handler=list_vocabulary,
    ),
    Tool(
        name="get_preview",
        title="Get brush previews",
        description=(
            "The stored preview images of a brush as PNG: `stroke` (a drawn stroke, 530x162, the "
            "drawing app's own thumbnail when it has one), `shape` and `grain` (256x256 tiles). It "
            "serves the files previews.py wrote and renders nothing; a brush whose shape or grain is "
            "an image inside the drawing app has no tile for it. The text block names the images and "
            "says what is missing."),
        input_schema={"type": "object", "additionalProperties": False, "required": ["id"], "properties": {
            "id": BRUSH_ID,
            "kinds": {"type": "array", "minItems": 1, "maxItems": 3, "default": ["stroke"],
                      "items": {"type": "string", "enum": ["stroke", "shape", "grain"]}}}},
        handler=get_preview,
    ),
    Tool(
        name="get_brush_settings_schema",
        title="Brush settings schema",
        description=(
            "What each brush setting (archive key) is: type, range, default, the eras that have it, and "
            "its tab. `group` limits it to one tab, `keys` to named settings (up to 60). `detail` full "
            "adds labels, descriptions, enums and the values the library holds. Labels and ranges are "
            "inferred from key names and observed values; only a few rows are verified."),
        input_schema={"type": "object", "additionalProperties": False, "properties": {
            "group": {"type": "string", "maxLength": 40},
            "keys": {"type": "array", "maxItems": 60, "items": {"type": "string", "maxLength": 64}},
            "detail": {"type": "string", "enum": ["compact", "full"], "default": "compact"}}},
        handler=get_brush_settings_schema,
        meta=RESULT_SIZE,
    ),
    Tool(
        name="validate_settings_patch",
        title="Validate a settings patch",
        description=(
            "Check a change to a brush's settings without making any file. `changes` is {setting: "
            "value}. The base is `base_id` (a library brush), `base` ({members: [{path, b64}]}; only "
            "Brush.archive is read) or neither (the new-brush template of `era`). Returns what would "
            "apply, what is clamped or rejected and why, and `patch_text`: a JSON patch the designer "
            "app's paste box accepts. Python is the authority; the app's own check is advisory."),
        input_schema={"type": "object", "additionalProperties": False, "required": ["changes"], "properties": {
            "changes": {"type": "object"},
            "base_id": BRUSH_ID,
            "base": {"type": "object"},
            "era": {"type": "string", "maxLength": 16}}},
        handler=validate_settings_patch,
    ),
    Tool(
        name="export_brush",
        title="Export a changed brush",
        description=(
            "Write a library brush, with `changes` applied, as a .brush file into the server's export "
            "folder (it was started with --export-dir). `name` renames the brush. With confirm false "
            "(the default) nothing is written and the result says what would be; with confirm true the "
            "file `<name-slug>-<id8>.brush` is written, never over an existing file. The original "
            "archive's bytes are kept for an unchanged brush; the thumbnail is the old one (stale). "
            "Nothing it writes is known to open in Procreate."),
        input_schema={"type": "object", "additionalProperties": False, "required": ["base_id"], "properties": {
            "base_id": BRUSH_ID,
            "changes": {"type": "object"},
            "name": {"type": "string", "minLength": 1, "maxLength": 120},
            "confirm": {"type": "boolean", "default": False}}},
        handler=export_brush,
        read_only=False,
        needs_export_dir=True,
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
        "instructions": (STAND_DOWN_INSTRUCTIONS if context.stand_down else
                         INSTRUCTIONS + (EXPORT_INSTRUCTIONS if context.export_dir is not None else "")),
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
        if "search_brushes" in names:
            _, reply = ask({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                            "params": {"name": "search_brushes", "arguments": {}}})
            result = reply.get("result", {})
            error = json.loads(result["content"][0]["text"]).get("error", {})
            check("a tool that refuses answers with an isError result, not a protocol error",
                  result.get("isError") is True and error.get("code") == "bad_argument", str(error.get("code")))
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
                        help="the one folder export_brush may write into; the tool is listed only "
                             "with this flag. Never a folder inside the tool, the library, the "
                             "catalog or the vault")
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
    if args.export_dir:
        problem = service.check_export_dir(args.export_dir, paths)
        if problem:
            _stderr_log(f"--export-dir {args.export_dir}: {problem}")
            return bc.EXIT_USAGE
    stand_down = should_stand_down(args.defer_to_project)
    context = make_context(paths, export_dir=Path(args.export_dir).resolve() if args.export_dir else None,
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
    _stderr_log(f"{SERVER_VERSION} serving {paths.root} over stdio, mode {context.mode}"
                + (", standing down: the project has its own server" if stand_down else "")
                + (f", export_brush writes into {args.export_dir}" if args.export_dir and not stand_down else ""))
    try:
        return serve(wire_in, wire_out, context)
    except KeyboardInterrupt:
        return bc.EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
