"""pipeline/mcp_server.py: the JSON-RPC dispatcher, the line codec, the tool
table and the one tool of this build (docs/CONTRACTS.md, F10 "MCP").

Everything runs in this process. `dispatch` is called with decoded messages,
`handle_line` with bytes, `serve` and `main` with in-memory streams; no test
starts the server as a program. The one tool is pointed at a temporary data
root, so nothing here reads the real library, catalog or vault.

    python -m unittest discover -s brushes/pipeline/tests
"""

import io
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))         # for `fixtures`, when one file is run by path

import brush_common as bc  # noqa: E402
import fixtures  # noqa: E402
import mcp_server as ms  # noqa: E402

try:
    import yaml
except ImportError:                                 # the agreement checks need it; nothing else does
    yaml = None

BRUSHES = PIPELINE.parent
REPO = BRUSHES.parent

# The tools this build registers. A later build that adds a row extends this.
REGISTERED = ["library_status"]

NAME = "Cont\u00e9 \U0001f4a7 6B \u6d53\u58a8"      # accents, an astral character, CJK
MACHINE_PATH = re.compile(r"[A-Za-z]:[\\/](?:Users|Windows|Program)|/Users/|/home/")


def request(method, params=None, request_id=1):
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    return message


def notification(method, params=None):
    message = request(method, params)
    del message["id"]
    return message


def payload_of(reply):
    """The JSON a tool result carries in its first text block."""
    block = reply["result"]["content"][0]
    assert block["type"] == "text", block
    return json.loads(block["text"])


def echo_tool(**changes):
    """A registry row for the tests: it returns its arguments."""
    row = dict(name="echo", title="Echo", description="Returns what it was given.",
               input_schema={"type": "object", "properties": {"text": {"type": "string", "maxLength": 80}},
                             "additionalProperties": False},
               handler=lambda arguments, context: {"echo": arguments})
    row.update(changes)
    return ms.Tool(**row)


class ServerCase(fixtures.BrushCase):
    """A context over a temporary data root named brushes/, as in a checkout."""

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "brushes"
        self.logged = []

    def context(self, **options):
        options.setdefault("log", self.logged.append)
        return ms.make_context(bc.resolve_paths(root=self.root), **options)

    def ask(self, message, **options):
        return ms.dispatch(message, self.context(**options))

    def assertError(self, reply, code, request_id=None):
        self.assertEqual(set(reply), {"jsonrpc", "id", "error"}, reply)
        self.assertEqual(reply["jsonrpc"], "2.0")
        self.assertEqual(reply["id"], request_id)
        self.assertEqual(reply["error"]["code"], code, reply)
        self.assertIsInstance(reply["error"]["message"], str)
        self.assertTrue(reply["error"]["message"])


# ── the handshake ────────────────────────────────────────────────────────────

class Handshake(ServerCase):
    def initialize(self, version, **options):
        return self.ask(request("initialize", {
            "protocolVersion": version, "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1"}}), **options)

    def test_it_answers_with_the_clients_version_when_it_knows_it(self):
        self.assertEqual(ms.PROTOCOL_VERSIONS, ("2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"))
        for version in ms.PROTOCOL_VERSIONS:
            reply = self.initialize(version)
            self.assertEqual(reply["result"]["protocolVersion"], version)
            self.assertEqual((reply["jsonrpc"], reply["id"]), ("2.0", 1))

    def test_it_offers_its_default_for_any_other_version(self):
        self.assertEqual(ms.DEFAULT_PROTOCOL_VERSION, "2025-11-25")
        self.assertIn(ms.DEFAULT_PROTOCOL_VERSION, ms.PROTOCOL_VERSIONS)
        for version in ("2026-07-28", "1999-01-01", "", "latest", 20251125, None, ["2025-06-18"]):
            self.assertEqual(self.initialize(version)["result"]["protocolVersion"],
                             ms.DEFAULT_PROTOCOL_VERSION, version)
        bare = self.ask(request("initialize"))
        self.assertEqual(bare["result"]["protocolVersion"], ms.DEFAULT_PROTOCOL_VERSION)

    def test_the_result_has_the_fields_a_client_reads(self):
        result = self.initialize("2025-06-18")["result"]
        self.assertEqual(set(result), {"protocolVersion", "capabilities", "serverInfo", "instructions"})
        self.assertEqual(result["capabilities"], {"tools": {"listChanged": False}})
        self.assertEqual(result["serverInfo"], {"name": "rosw-brushes", "title": "ROSW Brushes",
                                                "version": ms.SERVER_VERSION})
        self.assertRegex(ms.SERVER_VERSION, r"^\d+\.\d+\.\d+$")
        self.assertIn("library_status", result["instructions"])
        self.assertIn("stub", result["instructions"])

    def test_ping(self):
        self.assertEqual(self.ask(request("ping", request_id="p-1")),
                         {"jsonrpc": "2.0", "id": "p-1", "result": {}})

    def test_a_whole_session_over_bytes(self):
        context = self.context()
        lines = [request("initialize", {"protocolVersion": "2025-03-26"}, 0),
                 notification("notifications/initialized"),
                 request("ping", request_id=1),
                 request("tools/list", request_id=2),
                 request("tools/call", {"name": "library_status", "arguments": {}}, 3)]
        replies = [ms.handle_line(json.dumps(line).encode("utf-8") + b"\n", context) for line in lines]
        self.assertIsNone(replies[1])
        decoded = [json.loads(raw) for raw in replies if raw is not None]
        self.assertEqual([reply["id"] for reply in decoded], [0, 1, 2, 3])
        self.assertEqual(decoded[0]["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(decoded[1]["result"], {})
        self.assertEqual([tool["name"] for tool in decoded[2]["result"]["tools"]], REGISTERED)
        self.assertIs(decoded[3]["result"]["isError"], False)

    def test_requests_are_served_before_initialize(self):
        self.assertEqual(self.ask(request("tools/list"))["result"]["tools"][0]["name"], "library_status")


# ── the envelope ─────────────────────────────────────────────────────────────

class Envelope(ServerCase):
    def test_an_unknown_method_is_method_not_found(self):
        for method in ("server/discover", "resources/list", "prompts/list", "logging/setLevel",
                       "tools/run", "Initialize", ""):
            reply = self.ask(request(method, request_id=7))
            self.assertError(reply, ms.METHOD_NOT_FOUND, 7)
            self.assertEqual(reply["error"]["data"], method)

    def test_a_notification_gets_no_reply(self):
        for message in (notification("notifications/initialized"),
                        notification("notifications/cancelled", {"requestId": 3, "reason": "x"}),
                        notification("notifications/unheard-of"),
                        notification("ping"),
                        notification("tools/call", {"name": "library_status"}),
                        notification("tools/call", {"name": "no-such-tool"}),
                        notification("initialize", ["not", "an", "object"])):
            self.assertIsNone(self.ask(message), message)

    def test_a_response_from_the_client_is_ignored(self):
        self.assertIsNone(self.ask({"jsonrpc": "2.0", "id": 4, "result": {}}))
        self.assertIsNone(self.ask({"jsonrpc": "2.0", "id": 4, "error": {"code": -1, "message": "x"}}))

    def test_what_is_not_a_request_is_invalid(self):
        for message in ("ping", 7, None, True, 1.5):
            self.assertError(self.ask(message), ms.INVALID_REQUEST)
        self.assertError(self.ask({}), ms.INVALID_REQUEST)
        self.assertError(self.ask({"jsonrpc": "2.0", "id": 5}), ms.INVALID_REQUEST, 5)
        self.assertError(self.ask({"jsonrpc": "2.0", "id": 5, "method": 12}), ms.INVALID_REQUEST, 5)
        self.assertError(self.ask({"id": 6, "method": "ping"}), ms.INVALID_REQUEST, 6)
        self.assertError(self.ask({"jsonrpc": "1.0", "id": 6, "method": "ping"}), ms.INVALID_REQUEST, 6)
        self.assertError(self.ask({"jsonrpc": 2.0, "id": 6, "method": "ping"}), ms.INVALID_REQUEST, 6)
        self.assertError(self.ask({"method": "ping"}), ms.INVALID_REQUEST)

    def test_an_id_is_a_string_or_an_integer(self):
        for good in (0, -1, 2 ** 40, "", "abc", NAME):
            self.assertEqual(self.ask(request("ping", request_id=good))["id"], good)
        for bad in (None, True, 1.5, [1], {"a": 1}):
            self.assertError(self.ask(request("ping", request_id=bad)), ms.INVALID_REQUEST)

    def test_params_must_be_an_object(self):
        for bad in ([], [1, 2], "x", 3, True):
            self.assertError(self.ask(request("ping", bad, 8)), ms.INVALID_PARAMS, 8)
            self.assertError(self.ask(request("tools/call", bad, 8)), ms.INVALID_PARAMS, 8)
        self.assertEqual(self.ask({"jsonrpc": "2.0", "id": 8, "method": "ping", "params": None})["result"], {})

    def test_a_batch_answers_each_request_and_no_notification(self):
        replies = self.ask([request("ping", request_id="a"), notification("notifications/initialized"),
                            request("nope", request_id="b"), 17, request("tools/list", request_id="c")])
        self.assertEqual([reply["id"] for reply in replies], ["a", "b", None, "c"])
        self.assertEqual(replies[0]["result"], {})
        self.assertError(replies[1], ms.METHOD_NOT_FOUND, "b")
        self.assertError(replies[2], ms.INVALID_REQUEST)
        self.assertEqual(len(replies[3]["result"]["tools"]), len(REGISTERED))

    def test_an_empty_batch_is_invalid_and_a_silent_one_is_silent(self):
        self.assertError(self.ask([]), ms.INVALID_REQUEST)
        self.assertIsNone(self.ask([notification("a"), notification("b")]))

    def test_a_mistake_inside_a_method_is_an_internal_error_not_a_crash(self):
        def broken(params, context):
            raise RuntimeError("secret detail")

        with mock.patch.dict(ms.METHODS, {"ping": broken}):
            reply = self.ask(request("ping", request_id=9))
        self.assertError(reply, ms.INTERNAL_ERROR, 9)
        self.assertNotIn("secret", json.dumps(reply))
        self.assertIn("secret detail", "".join(self.logged))

    def test_the_dispatcher_keeps_nothing_between_calls(self):
        context = self.context()
        first = ms.dispatch(request("tools/list"), context)
        ms.dispatch(request("initialize", {"protocolVersion": "2024-11-05"}), context)
        ms.dispatch(request("tools/call", {"name": "library_status"}), context)
        self.assertEqual(ms.dispatch(request("tools/list"), context), first)

    def test_the_error_codes_are_the_json_rpc_ones(self):
        self.assertEqual((ms.PARSE_ERROR, ms.INVALID_REQUEST, ms.METHOD_NOT_FOUND, ms.INVALID_PARAMS,
                          ms.INTERNAL_ERROR), (-32700, -32600, -32601, -32602, -32603))


# ── lines ────────────────────────────────────────────────────────────────────

class Lines(ServerCase):
    def line(self, raw):
        reply = ms.handle_line(raw, self.context())
        return reply, (None if reply is None else json.loads(reply.decode("ascii")))

    def test_malformed_json_is_a_parse_error_with_a_null_id(self):
        for raw in (b"{not json\n", b'{"jsonrpc":"2.0","id":1,"method":"ping"\n', b"}\n", b"ping\n",
                    b'{"jsonrpc":"2.0","id":1,"method":"ping"} trailing\n',
                    b'{"jsonrpc":"2.0","id":1,"method":"ping"}{"jsonrpc":"2.0","id":2,"method":"ping"}\n',
                    b"{'jsonrpc': '2.0'}\n"):
            _, reply = self.line(raw)
            self.assertError(reply, ms.PARSE_ERROR)

    def test_bytes_that_are_not_utf8_are_a_parse_error(self):
        for raw in (b'{"jsonrpc":"2.0","id":1,"method":"\xff\xfe"}\n',
                    '{"jsonrpc":"2.0","id":1,"method":"ping"}\n'.encode("utf-16"),
                    b'{"jsonrpc":"2.0","id":"\xc3","method":"ping"}\n'):
            _, reply = self.line(raw)
            self.assertError(reply, ms.PARSE_ERROR)

    def test_nan_and_infinity_are_not_json(self):
        for word in (b"NaN", b"Infinity", b"-Infinity"):
            _, reply = self.line(b'{"jsonrpc":"2.0","id":1,"method":"ping","params":{"x":' + word + b"}}\n")
            self.assertError(reply, ms.PARSE_ERROR)

    def test_a_value_nested_too_deep_is_a_parse_error_not_a_crash(self):
        _, reply = self.line(b"[" * 200000 + b"\n")
        self.assertError(reply, ms.PARSE_ERROR)

    def test_a_blank_line_is_skipped(self):
        for raw in (b"", b"\n", b"\r\n", b"   \t \n"):
            self.assertEqual(self.line(raw), (None, None))

    def test_a_carriage_return_before_the_newline_is_accepted(self):
        raw, reply = self.line(b'{"jsonrpc":"2.0","id":1,"method":"ping"}\r\n')
        self.assertEqual(reply, {"jsonrpc": "2.0", "id": 1, "result": {}})
        self.assertEqual(raw, b'{"jsonrpc":"2.0","id":1,"result":{}}\n')

    def test_a_reply_is_one_compact_ascii_line(self):
        context = self.context(tools=ms.tool_table(echo_tool()))
        messages = [request("initialize", {"protocolVersion": "2025-06-18"}), request("tools/list"),
                    request("tools/call", {"name": "echo", "arguments": {"text": "a\r\nb\tc " + NAME}}),
                    request("no/such\r\nmethod", request_id="id\nwith\rbreaks")]
        for message in messages:
            raw = ms.handle_line(json.dumps(message).encode("utf-8"), context)
            self.assertTrue(raw.isascii())
            self.assertTrue(raw.endswith(b"\n"))
            self.assertEqual(raw.count(b"\n"), 1)
            self.assertNotIn(b"\r", raw)
            self.assertTrue(raw.startswith(b'{"jsonrpc":"2.0","id":'), "no space after a separator")
            self.assertEqual(json.loads(raw)["id"], message["id"])

    def test_non_ascii_goes_in_as_utf8_and_comes_back_whole(self):
        context = self.context(tools=ms.tool_table(echo_tool()))
        message = request("tools/call", {"name": "echo", "arguments": {"text": NAME}}, request_id=NAME)
        for raw_in in (json.dumps(message, ensure_ascii=False).encode("utf-8"),      # real characters
                       json.dumps(message, ensure_ascii=True).encode("ascii")):      # \u escapes
            raw_out = ms.handle_line(raw_in + b"\n", context)
            self.assertTrue(raw_out.isascii(), "the line itself is ASCII")
            self.assertNotIn(NAME.encode("utf-8"), raw_out)
            reply = json.loads(raw_out.decode("ascii"))
            self.assertEqual(reply["id"], NAME)
            text = reply["result"]["content"][0]["text"]
            self.assertIn(NAME, text, "inside the text block the characters are real, not escaped")
            self.assertNotIn("\\u", text)
            self.assertEqual(json.loads(text), {"echo": {"text": NAME}})

    def test_a_non_ascii_method_name_comes_back_in_the_error(self):
        raw = ms.handle_line(json.dumps(request(NAME), ensure_ascii=False).encode("utf-8"), self.context())
        self.assertTrue(raw.isascii())
        reply = json.loads(raw)
        self.assertError(reply, ms.METHOD_NOT_FOUND, 1)
        self.assertEqual(reply["error"]["data"], NAME)

    def test_a_lone_surrogate_cannot_break_the_line(self):
        context = self.context(tools=ms.tool_table(echo_tool()))
        raw = ms.handle_line(b'{"jsonrpc":"2.0","id":"\\ud83d","method":"tools/call",'
                             b'"params":{"name":"echo","arguments":{"text":"half \\ud83d"}}}\n', context)
        self.assertTrue(raw.isascii())
        reply = json.loads(raw)
        self.assertEqual(reply["id"], "\ud83d")
        reply["result"]["content"][0]["text"].encode("utf-8")       # no lone surrogate left in the text
        self.assertEqual(json.loads(reply["result"]["content"][0]["text"]), {"echo": {"text": "half ?"}})

    def test_a_reply_that_cannot_be_encoded_is_an_internal_error(self):
        with mock.patch.object(ms, "dispatch", return_value={"jsonrpc": "2.0", "id": 1, "result": float("nan")}):
            _, reply = self.line(b'{"jsonrpc":"2.0","id":1,"method":"ping"}\n')
        self.assertError(reply, ms.INTERNAL_ERROR)


# ── tools/list ───────────────────────────────────────────────────────────────

class ToolsList(ServerCase):
    def tools(self, **options):
        reply = self.ask(request("tools/list"), **options)
        self.assertEqual(set(reply["result"]), {"tools"})
        return reply["result"]["tools"]

    def test_this_build_registers_exactly_one_tool(self):
        self.assertEqual(list(ms.TOOLS), REGISTERED)
        self.assertEqual([tool["name"] for tool in self.tools()], REGISTERED)

    def test_the_shape_of_an_entry(self):
        for tool in self.tools():
            self.assertEqual(set(tool), {"name", "title", "description", "inputSchema", "annotations"})
            self.assertRegex(tool["name"], r"^[a-z][a-z0-9_]{0,63}$")
            self.assertTrue(tool["title"].strip())
            self.assertGreater(len(tool["description"]), 40)
            schema = tool["inputSchema"]
            self.assertEqual(schema["type"], "object")
            self.assertIsInstance(schema["properties"], dict)
            self.assertIs(schema["additionalProperties"], False)
            self.assertEqual(tool["annotations"], {"readOnlyHint": True, "openWorldHint": False})
            json.dumps(tool, allow_nan=False)

    def test_library_status_takes_no_arguments(self):
        (tool,) = [tool for tool in self.tools() if tool["name"] == "library_status"]
        self.assertEqual(tool["inputSchema"], {"type": "object", "properties": {}, "additionalProperties": False})

    def test_a_cursor_is_ignored(self):
        self.assertEqual(self.ask(request("tools/list", {"cursor": "page-2"}))["result"]["tools"], self.tools())

    def test_a_table_row_is_all_a_new_tool_needs(self):
        table = ms.tool_table(*ms.TOOLS.values(), echo_tool(meta={"anthropic/maxResultSizeChars": 120000}))
        listed = self.tools(tools=table)
        self.assertEqual([tool["name"] for tool in listed], REGISTERED + ["echo"])
        self.assertEqual(listed[-1]["_meta"], {"anthropic/maxResultSizeChars": 120000})
        reply = self.ask(request("tools/call", {"name": "echo", "arguments": {"text": "hi"}}), tools=table)
        self.assertEqual(payload_of(reply), {"echo": {"text": "hi"}})

    def test_a_name_registered_twice_is_refused(self):
        with self.assertRaises(ValueError):
            ms.tool_table(echo_tool(), echo_tool())

    def test_a_writing_tool_is_listed_only_with_an_export_folder(self):
        writer = echo_tool(name="export_brush", read_only=False, needs_export_dir=True)
        table = ms.tool_table(*ms.TOOLS.values(), writer)
        self.assertEqual([tool["name"] for tool in self.tools(tools=table)], REGISTERED)
        self.assertError(self.ask(request("tools/call", {"name": "export_brush"}), tools=table),
                         ms.INVALID_PARAMS, 1)
        listed = self.tools(tools=table, export_dir=self.tmp / "out")
        self.assertEqual([tool["name"] for tool in listed], REGISTERED + ["export_brush"])
        self.assertEqual(listed[-1]["annotations"], {"readOnlyHint": False, "destructiveHint": False,
                                                     "idempotentHint": False, "openWorldHint": False})
        self.assertFalse((self.tmp / "out").exists(), "listing a tool creates nothing")

    def test_the_export_folder_changes_nothing_in_this_build(self):
        self.assertEqual(self.tools(export_dir=self.tmp / "out"), self.tools())
        self.assertFalse(any(tool.needs_export_dir for tool in ms.TOOLS.values()))
        self.assertTrue(all(tool.read_only for tool in ms.TOOLS.values()))

    def test_a_server_that_stood_down_lists_nothing(self):
        self.assertEqual(self.tools(stand_down=True), [])
        self.assertError(self.ask(request("tools/call", {"name": "library_status"}), stand_down=True),
                         ms.INVALID_PARAMS, 1)
        result = self.ask(request("initialize", {"protocolVersion": "2025-06-18"}), stand_down=True)["result"]
        self.assertIn("stood down", result["instructions"])
        self.assertEqual(self.ask(request("ping"), stand_down=True)["result"], {})


# ── tools/call ───────────────────────────────────────────────────────────────

class LibraryStatus(ServerCase):
    def status(self, **options):
        reply = self.ask(request("tools/call", {"name": "library_status", "arguments": {}}), **options)
        self.assertEqual(set(reply["result"]), {"content", "isError"})
        self.assertIs(reply["result"]["isError"], False)
        self.assertEqual(len(reply["result"]["content"]), 1)
        return payload_of(reply)

    # The payload frozen in docs/CONTRACTS.md, F10, in its order.
    FROZEN = ["server", "version", "mode", "root", "index", "counts", "library_present",
              "library_files", "vocabulary_axes", "export", "next_steps"]

    def test_an_empty_root(self):
        status = self.status()
        self.assertEqual(list(status), self.FROZEN + ["stub"],
                         "the frozen keys, and one more that holds everything only the stub says")
        self.assertEqual((status["server"], status["version"], status["mode"]),
                         ("rosw-brushes", ms.SERVER_VERSION, "project"))
        self.assertEqual(status["root"], "brushes")
        stub = status["stub"]
        self.assertEqual(set(stub), {"stage", "roots", "exists", "not_read"})
        self.assertEqual(stub["stage"], "stub")
        self.assertEqual(stub["roots"], {
            "root": "brushes", "library": "brushes/library", "catalog": "brushes/catalog",
            "vault": "brushes/vault", "index": "brushes/vault/tools/rag_index/index.json"})
        self.assertEqual(stub["exists"], {"root": False, "library": False, "catalog": False,
                                          "vault": False, "index": False})
        self.assertEqual(stub["not_read"], ["counts", "vocabulary_axes"])
        empty = {"files": 0, "brushset": 0, "brush": 0}
        self.assertEqual(status["library_files"], {"user": empty, "official": empty})
        self.assertIsNone(status["counts"], "the catalog's counts; there is no catalog")
        self.assertEqual(status["vocabulary_axes"], [])
        self.assertIs(status["library_present"], False)
        self.assertEqual(status["index"]["state"], "not_ingested")
        self.assertIn("brushes/catalog/catalog.json", status["index"]["reason"])
        self.assertEqual(status["export"], {"enabled": False, "dir": None})
        self.assertIsInstance(status["next_steps"], list)

    @unittest.skipIf(yaml is None, "pyyaml is not installed")
    def test_the_payload_is_the_documents(self):
        contracts = (BRUSHES / "docs" / "CONTRACTS.md").read_text(encoding="utf-8")
        row = next(line for line in contracts.splitlines() if line.startswith("| `library_status` |"))
        self.assertEqual(re.findall(r'"([a-z_]+)"', row.split("|")[3].split("stub")[0]),
                         ["server", "version", "mode", "root", "index", "state", "reason", "counts",
                          "library_present", "library_files", "vocabulary_axes", "export", "enabled", "dir",
                          "next_steps"])
        for state in ms.INDEX_STATES:
            self.assertIn(f"`{state}`", contracts)
        self.assertIn('`mode` is `"project"`', " ".join(contracts.split()))
        self.assertEqual(ms.MODES, ("project", "snapshot"))
        self.assertEqual(ms.INDEX_STATES, ("fresh", "stale", "memory", "not_ingested"))

    def test_a_library_on_disk_is_counted(self):
        library = fixtures.write_library(self.root / "library")
        (self.root / "library" / "user" / "demo-pack" / "_docs").mkdir()
        (self.root / "library" / "user" / "demo-pack" / "_docs" / "Guide.txt").write_bytes(b"read me")
        (self.root / "library" / "official" / "fetch_log.jsonl").write_bytes(b"{}\n")
        (self.root / "library" / "user" / "demo-pack" / "UPPER.BRUSHSET").write_bytes(b"by name only")
        self.assertEqual(len(library["files"]), 4)
        status = self.status()
        self.assertEqual(status["library_files"], {
            "user": {"files": 5, "brushset": 2, "brush": 2},
            "official": {"files": 2, "brushset": 1, "brush": 0}})
        self.assertIsNone(status["counts"], "file counts are not the catalog's counts")
        self.assertIs(status["library_present"], True)
        self.assertEqual(status["stub"]["exists"], {"root": True, "library": True, "catalog": False,
                                                    "vault": False, "index": False})
        self.assertEqual(status["index"]["state"], "not_ingested")

    def test_a_catalog_and_an_index_on_disk_are_seen(self):
        (self.root / "catalog").mkdir(parents=True)
        self.assertIs(self.status()["stub"]["exists"]["catalog"], False, "a folder is not a catalog")
        (self.root / "catalog" / "catalog.json").write_bytes(b'{"counts": {"brushes": 3}}\n')
        status = self.status()
        self.assertEqual(status["stub"]["exists"], {"root": True, "library": False, "catalog": True,
                                                    "vault": False, "index": False})
        self.assertEqual(status["index"]["state"], "memory", "a catalog and no index file")
        self.assertIn("is missing", status["index"]["reason"])
        self.assertIsNone(status["counts"], "this build opens no file, the catalog included")
        index = self.root / "vault" / "tools" / "rag_index" / "index.json"
        index.parent.mkdir(parents=True)
        index.write_bytes(b"{}\n")
        status = self.status()
        self.assertEqual(status["stub"]["exists"], {"root": True, "library": False, "catalog": True,
                                                    "vault": True, "index": True})
        self.assertEqual(status["index"]["state"], "stale",
                         "this build cannot tell fresh from stale, and never says fresh")
        self.assertIn("brushes/vault/tools/rag_index/index.json is on disk", status["index"]["reason"])

    def test_the_index_state_is_always_one_of_the_four(self):
        seen = set()
        catalog = self.root / "catalog" / "catalog.json"
        index = self.root / "vault" / "tools" / "rag_index" / "index.json"
        for make_catalog, make_index in ((False, False), (False, True), (True, False), (True, True)):
            for path, wanted in ((catalog, make_catalog), (index, make_index)):
                if wanted and not path.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b"{}\n")
                elif not wanted and path.exists():
                    path.unlink()
            state = self.status()["index"]["state"]
            self.assertIn(state, ms.INDEX_STATES, (make_catalog, make_index))
            self.assertIsInstance(self.status()["index"]["reason"], str)
            seen.add(state)
        self.assertEqual(seen, {"not_ingested", "memory", "stale"})

    def test_it_reads_listings_and_writes_nothing(self):
        fixtures.write_library(self.root / "library")
        before = fixtures.tree_digest(self.tmp)
        opened = []
        real_open = open

        def spy(file, *args, **kwargs):
            opened.append(str(file))
            return real_open(file, *args, **kwargs)

        with mock.patch("builtins.open", spy), mock.patch("io.open", spy):
            self.status()
            self.status(export_dir=self.tmp / "out")
        self.assertEqual(opened, [], "no file is opened, a brush file least of all")
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertFalse((self.tmp / "out").exists())
        self.assertFalse((self.root / "catalog").exists())
        self.assertFalse((self.root / "vault").exists())

    def test_no_machine_path_is_reported(self):
        fixtures.write_library(self.root / "library")
        reply = self.ask(request("tools/call", {"name": "library_status"}))
        text = reply["result"]["content"][0]["text"]
        self.assertNotIn(str(self.tmp), text)
        self.assertNotIn(self.tmp.as_posix(), text)
        self.assertNotIn("\\\\", text)
        self.assertIsNone(MACHINE_PATH.search(text))

    def test_a_folder_moved_by_a_flag_is_still_shown_relative(self):
        paths = bc.resolve_paths(root=self.root, library=self.tmp / "elsewhere" / "originals",
                                 vault=self.root / "data" / "vault")
        (self.tmp / "elsewhere" / "originals" / "user" / "p").mkdir(parents=True)
        (self.tmp / "elsewhere" / "originals" / "user" / "p" / "One.brush").write_bytes(b"x")
        reply = ms.dispatch(request("tools/call", {"name": "library_status"}), ms.make_context(paths))
        status = payload_of(reply)
        self.assertEqual(status["stub"]["roots"], {
            "root": "brushes", "library": "elsewhere/originals", "catalog": "brushes/catalog",
            "vault": "brushes/data/vault", "index": "brushes/data/vault/tools/rag_index/index.json"})
        self.assertEqual(status["library_files"]["user"], {"files": 1, "brushset": 0, "brush": 1})

    def test_a_path_outside_the_base_gets_dot_dot_segments(self):
        base = self.tmp / "repo"
        self.assertEqual(ms.repo_relative(base / "brushes" / "library", base), "brushes/library")
        self.assertEqual(ms.repo_relative(base, base), ".")
        self.assertEqual(ms.repo_relative(self.tmp / "other" / "lib", base), "../other/lib")

    def test_the_mode_is_reported(self):
        self.assertEqual(self.status(mode="snapshot")["mode"], "snapshot")

    def test_arguments_may_be_absent_or_null(self):
        for params in ({"name": "library_status"}, {"name": "library_status", "arguments": None},
                       {"name": "library_status", "arguments": {}}):
            self.assertIs(self.ask(request("tools/call", params))["result"]["isError"], False)

    def test_an_argument_it_does_not_take_is_a_tool_error(self):
        reply = self.ask(request("tools/call", {"name": "library_status", "arguments": {"verbose": True}}))
        self.assertIs(reply["result"]["isError"], True)
        error = payload_of(reply)["error"]
        self.assertEqual(set(error), {"code", "message", "hint"})
        self.assertEqual(error["code"], "bad_argument")
        self.assertIn("verbose", error["message"])

    EVERYTHING = ["official", "catalog", "index"]

    def test_next_steps_name_only_scripts_that_are_on_disk(self):
        tool_root = self.tmp / "brushes"
        built = tuple((what, script, verb, True) for what, script, verb, _ in ms.NEXT_STEPS)
        self.assertEqual(ms.next_steps(self.EVERYTHING, tool_root, built), [])
        (tool_root / "pipeline").mkdir(parents=True)
        (tool_root / "pipeline" / "ingest.py").write_bytes(b"")
        self.assertEqual(ms.next_steps(self.EVERYTHING, tool_root, built),
                         ["python brushes/pipeline/ingest.py build"])
        (tool_root / "pipeline" / "fetch_base_library.py").write_bytes(b"")
        (tool_root / "vault" / "tools").mkdir(parents=True)
        (tool_root / "vault" / "tools" / "brush_search.py").write_bytes(b"")
        self.assertEqual(ms.next_steps(self.EVERYTHING, tool_root, built), [
            "python brushes/pipeline/fetch_base_library.py fetch",
            "python brushes/pipeline/ingest.py build",
            "python brushes/vault/tools/brush_search.py index"])
        self.assertEqual(ms.next_steps(["index"], tool_root, built),
                         ["python brushes/vault/tools/brush_search.py index"])
        self.assertEqual(ms.next_steps([], tool_root, built), [])

    def test_next_steps_name_only_verbs_that_are_built(self):
        """A script on disk is not enough: `ingest.py` was there, without `build`,
        and the status sent its reader to a command that exits 2."""
        tool_root = self.tmp / "brushes"
        for _, script, _, _ in ms.NEXT_STEPS:
            (tool_root / script).parent.mkdir(parents=True, exist_ok=True)
            (tool_root / script).write_bytes(b"")
        none_built = tuple((what, script, verb, False) for what, script, verb, _ in ms.NEXT_STEPS)
        self.assertEqual(ms.next_steps(self.EVERYTHING, tool_root, none_built), [])
        one = (("catalog", "pipeline/ingest.py", "build", False),
               ("index", "vault/tools/brush_search.py", "index", True))
        self.assertEqual(ms.next_steps(self.EVERYTHING, tool_root, one),
                         ["python brushes/vault/tools/brush_search.py index"])
        with_table = ms.next_steps(self.EVERYTHING, tool_root)
        self.assertEqual(with_table, [f"python brushes/{script} {verb}"
                                      for _, script, verb, built in ms.NEXT_STEPS if built])

    def test_the_built_column_is_what_each_script_really_accepts(self):
        """Every row of NEXT_STEPS, run as `python -I <script> <verb> --help`.
        Exit 0 means the verb exists. The column must say so, both ways: a verb
        that lands without the row being switched on fails here too."""
        self.assertEqual([row[0] for row in ms.NEXT_STEPS], self.EVERYTHING)
        elsewhere = fixtures.temp_dir(self)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith(fixtures.ENV_PREFIX)}
        for what, script, verb, built in ms.NEXT_STEPS:
            path = BRUSHES / script
            if not path.is_file():
                self.assertFalse(built, f"{script} is not on disk, so `{verb}` cannot be built")
                continue
            done = subprocess.run([sys.executable, "-I", str(path), verb, "--help"], cwd=str(elsewhere),
                                  env=env, capture_output=True, timeout=120)
            self.assertEqual(done.returncode == 0, built,
                             f"`{script} {verb} --help` exits {done.returncode}, but NEXT_STEPS says "
                             f"built={built}: {done.stderr.decode('utf-8', 'replace')[-300:]}")
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_every_step_the_real_status_advertises_can_be_run(self):
        for step in ms.next_steps(self.EVERYTHING):
            self.assertNotIn("--confirm", step, "a status never tells anyone to confirm a write")
            command, script, verb = step.split()
            self.assertEqual(command, "python")
            self.assertTrue((REPO / script).is_file(), step)
            done = subprocess.run([sys.executable, "-I", str(REPO / script), verb, "--help"],
                                  capture_output=True, timeout=120)
            self.assertEqual(done.returncode, 0, step)


class ToolsCall(ServerCase):
    def call(self, params, tool=None, **options):
        if tool is not None:
            options["tools"] = ms.tool_table(tool)
        return self.ask(request("tools/call", params), **options)

    def test_what_is_wrong_with_the_call_itself_is_invalid_params(self):
        for params in (None, {}, {"arguments": {}}, {"name": 7}, {"name": ""}, {"name": ["library_status"]},
                       {"name": "library_status", "arguments": []},
                       {"name": "library_status", "arguments": "none"},
                       {"name": "library_status", "arguments": 0},
                       {"name": "no_such_tool"}, {"name": "Library_Status"}, {"name": NAME}):
            self.assertError(self.call(params), ms.INVALID_PARAMS, 1)
        self.assertEqual(self.call({"name": "no_such_tool"})["error"]["data"], "no_such_tool")

    def test_a_bad_argument_value_is_a_tool_error_not_a_protocol_error(self):
        reply = self.call({"name": "echo", "arguments": {"text": 5}}, echo_tool())
        self.assertIs(reply["result"]["isError"], True)
        self.assertEqual(payload_of(reply)["error"]["code"], "bad_argument")
        self.assertIn("arguments.text", payload_of(reply)["error"]["message"])

    def test_a_tools_own_refusal_is_a_tool_error(self):
        def refuse(arguments, context):
            raise ms.ToolError("not_ingested", "there is no catalog yet", "python brushes/pipeline/ingest.py build")

        reply = self.call({"name": "echo"}, echo_tool(handler=refuse))
        self.assertEqual(set(reply["result"]), {"content", "isError"})
        self.assertIs(reply["result"]["isError"], True)
        self.assertEqual(payload_of(reply), {"error": {
            "code": "not_ingested", "message": "there is no catalog yet",
            "hint": "python brushes/pipeline/ingest.py build"}})
        self.assertEqual(self.logged, [])

    def test_any_error_that_carries_a_code_and_a_message_is_reported_the_same_way(self):
        class ApiError(Exception):
            def __init__(self):
                super().__init__("unknown id")
                self.code, self.message, self.status, self.hint, self.data = "unknown_id", "unknown id", 404, None, None

        def refuse(arguments, context):
            raise ApiError()

        reply = self.call({"name": "echo"}, echo_tool(handler=refuse))
        self.assertEqual(payload_of(reply), {"error": {"code": "unknown_id", "message": "unknown id", "hint": None}})

    def test_an_unexpected_exception_is_internal_and_shows_no_traceback(self):
        def crash(arguments, context):
            raise OSError(13, "secret path D:/vault/private")

        reply = self.call({"name": "echo"}, echo_tool(handler=crash))
        self.assertIs(reply["result"]["isError"], True)
        text = reply["result"]["content"][0]["text"]
        self.assertEqual(payload_of(reply)["error"]["code"], "internal")
        for leaked in ("Traceback", "secret", "OSError", "private"):
            self.assertNotIn(leaked, text)
        self.assertIn("secret path", "".join(self.logged), "the detail goes to the log")
        self.assertIn("Traceback", "".join(self.logged))

    def test_a_payload_that_is_not_json_is_internal(self):
        for bad in (float("nan"), {"x": float("inf")}, {"x": {1, 2}}, object()):
            reply = self.call({"name": "echo"}, echo_tool(handler=lambda arguments, context, bad=bad: bad))
            self.assertIs(reply["result"]["isError"], True)
            self.assertEqual(payload_of(reply)["error"]["code"], "internal")

    def test_a_tool_may_add_image_blocks(self):
        png = {"type": "image", "data": "iVBORw0KGgo=", "mimeType": "image/png"}

        def picture(arguments, context):
            return ms.ToolOutput({"images": [{"kind": "stroke"}]}, (png,))

        reply = self.call({"name": "echo"}, echo_tool(handler=picture))
        self.assertIs(reply["result"]["isError"], False)
        self.assertEqual(reply["result"]["content"],
                         [{"type": "text", "text": '{"images":[{"kind":"stroke"}]}'}, png])

    def test_the_text_block_is_compact_json_with_real_characters(self):
        reply = self.call({"name": "echo", "arguments": {"text": NAME}}, echo_tool())
        self.assertEqual(reply["result"]["content"][0]["text"], '{"echo":{"text":"' + NAME + '"}}')

    def test_the_handler_gets_the_arguments_and_the_context(self):
        seen = []
        tool = echo_tool(handler=lambda arguments, context: seen.append((arguments, context)) or {})
        context = self.context(tools=ms.tool_table(tool))
        ms.dispatch(request("tools/call", {"name": "echo", "arguments": {"text": "x"}}), context)
        self.assertEqual(seen, [({"text": "x"}, context)])
        self.assertEqual(context.paths.root, self.root)


class ArgumentCheck(unittest.TestCase):
    """The part of JSON Schema the later tools use, so that adding one is a
    table row and not a change to the dispatcher."""

    SCHEMA = {"type": "object", "additionalProperties": False, "required": ["id"], "properties": {
        "id": {"type": "string", "pattern": "^b_[0-9a-f]{12}$"},
        "top": {"type": "integer", "minimum": 1, "maximum": 25},
        "ratio": {"type": "number"},
        "query": {"type": "string", "minLength": 1, "maxLength": 10},
        "kinds": {"type": "array", "minItems": 1, "maxItems": 3,
                  "items": {"type": "string", "enum": ["stroke", "shape", "grain"]}},
        "detail": {"type": "string", "enum": ["compact", "full"]},
        "confirm": {"type": "boolean"},
        "changes": {"type": "object"}}}
    GOOD = "b_0123456789ab"

    def problem(self, **arguments):
        arguments.setdefault("id", self.GOOD)
        return ms.check_arguments(arguments, self.SCHEMA)

    def test_what_passes(self):
        self.assertIsNone(self.problem())
        self.assertIsNone(self.problem(top=1, ratio=0.5, query="ink", kinds=["stroke", "grain"],
                                       detail="full", confirm=False, changes={"any": [1, {"thing": None}]}))
        self.assertIsNone(self.problem(top=25.0), "a whole float passes for an integer")
        self.assertIsNone(self.problem(ratio=3))
        self.assertIsNone(ms.check_arguments({}, {"type": "object", "properties": {}, "additionalProperties": False}))
        self.assertIsNone(ms.check_arguments({"free": 1}, {"type": "object"}))

    def test_what_is_refused(self):
        refused = {
            "arguments needs `id`": ms.check_arguments({}, self.SCHEMA),
            "arguments.id must match": self.problem(id="b_XYZ"),
            "arguments.id must be of type string": self.problem(id=12),
            "arguments.top must be of type integer": self.problem(top=2.5),
            "arguments.top must be of type integer ": self.problem(top=True),
            "arguments.top must be of type integer  ": self.problem(top="3"),
            "arguments.top must be of type integer   ": self.problem(top=float("inf")),
            "arguments.top must be at least 1": self.problem(top=0),
            "arguments.top must be at most 25": self.problem(top=26),
            "arguments.ratio must be of type number": self.problem(ratio=float("nan")),
            "arguments.ratio must be of type number ": self.problem(ratio=float("inf")),
            "arguments.ratio must be of type number  ": self.problem(ratio=False),
            "arguments.query must have at least 1": self.problem(query=""),
            "arguments.query must have at most 10": self.problem(query="x" * 11),
            "arguments.kinds must have at least 1": self.problem(kinds=[]),
            "arguments.kinds must have at most 3": self.problem(kinds=["stroke"] * 4),
            "arguments.kinds[1] must be one of: stroke, shape, grain": self.problem(kinds=["stroke", "card"]),
            "arguments.kinds[0] must be of type string": self.problem(kinds=[1]),
            "arguments.kinds must be of type array": self.problem(kinds="stroke"),
            "arguments.detail must be one of: compact, full": self.problem(detail="long"),
            "arguments.confirm must be of type boolean": self.problem(confirm=1),
            "arguments.changes must be of type object": self.problem(changes=[]),
            "arguments has no `extra`": self.problem(extra=1),
            "arguments must be of type object": ms.check_arguments([], self.SCHEMA),
        }
        for expected, found in refused.items():
            self.assertIsNotNone(found, expected)
            self.assertTrue(found.startswith(expected.strip()), (expected, found))

    def test_a_long_unknown_name_is_cut_in_the_message(self):
        found = ms.check_arguments({"x" * 5000: 1}, {"type": "object", "properties": {}, "additionalProperties": False})
        self.assertLess(len(found), 400)


# ── the loop ─────────────────────────────────────────────────────────────────

class Serve(ServerCase):
    def run_lines(self, data, **options):
        out = io.BytesIO()
        code = ms.serve(io.BytesIO(data), out, self.context(), **options)
        return code, out.getvalue()

    def test_it_answers_each_request_and_ends_with_the_input(self):
        data = b"".join(json.dumps(m).encode("utf-8") + b"\n" for m in (
            request("initialize", {"protocolVersion": "2025-06-18"}, 1),
            notification("notifications/initialized"),
            request("tools/list", request_id=2)))
        code, out = self.run_lines(data + b"\n" + b"{broken\r\n")
        self.assertEqual(code, 0)
        lines = out.split(b"\n")
        self.assertEqual(lines[-1], b"")
        replies = [json.loads(line) for line in lines[:-1]]
        self.assertEqual([reply["id"] for reply in replies], [1, 2, None])
        self.assertEqual(replies[2]["error"]["code"], ms.PARSE_ERROR)
        self.assertNotIn(b"\r", out)

    def test_no_input_is_a_clean_end(self):
        self.assertEqual(self.run_lines(b""), (0, b""))

    def test_a_last_line_without_a_newline_is_still_answered(self):
        code, out = self.run_lines(b'{"jsonrpc":"2.0","id":1,"method":"ping"}')
        self.assertEqual((code, out), (0, b'{"jsonrpc":"2.0","id":1,"result":{}}\n'))

    def test_a_line_over_the_limit_is_refused_and_the_next_one_is_served(self):
        ping = b'{"jsonrpc":"2.0","id":2,"method":"ping"}\n'
        long_line = b'{"jsonrpc":"2.0","id":1,"method":"ping","params":{"pad":"' + b"x" * 5000 + b'"}}\n'
        code, out = self.run_lines(long_line + ping, max_line=256)
        self.assertEqual(code, 0)
        first, second = [json.loads(line) for line in out.splitlines()]
        self.assertError(first, ms.INVALID_REQUEST)
        self.assertIn("256", first["error"]["message"])
        self.assertEqual(second, {"jsonrpc": "2.0", "id": 2, "result": {}})
        code, out = self.run_lines(long_line, max_line=len(long_line))
        self.assertEqual(json.loads(out), {"jsonrpc": "2.0", "id": 1, "result": {}})
        self.assertGreaterEqual(ms.MAX_LINE, 1024 * 1024)

    def test_a_client_that_went_away_ends_the_server_quietly(self):
        class Gone(io.BytesIO):
            def write(self, data):
                raise BrokenPipeError("the pipe is closed")

        code = ms.serve(io.BytesIO(b'{"jsonrpc":"2.0","id":1,"method":"ping"}\n' * 3), Gone(), self.context())
        self.assertEqual(code, 0)
        self.assertEqual(len(self.logged), 1)


# ── starting ─────────────────────────────────────────────────────────────────

class FakeStream:
    """What main() needs of sys.stdin and sys.stdout: a byte stream under it."""

    def __init__(self, data=b""):
        self.buffer = io.BytesIO(data)


class Starting(ServerCase):
    def run_main(self, argv, stdin=b""):
        out, err = FakeStream(), io.StringIO()
        with mock.patch.object(sys, "stdin", FakeStream(stdin)), mock.patch.object(sys, "stdout", out), \
                mock.patch.object(sys, "stderr", err):
            code = ms.main(argv)
            stdout_now = sys.stdout
        return code, out.buffer.getvalue(), err.getvalue(), stdout_now is err

    def test_it_serves_stdin_to_stdout_and_logs_to_stderr(self):
        data = b"".join(json.dumps(m).encode("utf-8") + b"\n" for m in (
            request("initialize", {"protocolVersion": "2025-11-25"}, 1), request("tools/list", request_id=2),
            request("tools/call", {"name": "library_status"}, 3)))
        code, out, err, redirected = self.run_main(["--root", str(self.root)], data)
        self.assertEqual(code, 0)
        self.assertTrue(redirected, "after the wire is taken, sys.stdout is stderr")
        replies = [json.loads(line) for line in out.splitlines()]
        self.assertEqual([reply["id"] for reply in replies], [1, 2, 3])
        self.assertEqual(payload_of(replies[2])["stub"]["roots"]["library"], "brushes/library")
        self.assertIn("rosw-brushes", err)
        self.assertEqual(len(err.splitlines()), 1, "one line at start, nothing per request")
        self.assertEqual(list(self.tmp.iterdir()), [], "serving created nothing")

    def test_the_export_folder_is_parsed_and_not_used(self):
        target = self.tmp / "exports"
        data = json.dumps(request("tools/list")).encode("utf-8") + b"\n"
        code, out, err, _ = self.run_main(["--root", str(self.root), "--export-dir", str(target)], data)
        self.assertEqual(code, 0)
        self.assertEqual([tool["name"] for tool in json.loads(out)["result"]["tools"]], REGISTERED)
        self.assertFalse(target.exists())
        self.assertIn("--export-dir is accepted and not used", err)

    def test_the_flags_of_the_contract_are_accepted(self):
        args = ms.build_parser().parse_args(["--export-dir", "out", "--defer-to-project", "proj", "--selftest",
                                             "--root", "r", "--library", "l", "--catalog", "c", "--vault", "v"])
        self.assertEqual((args.export_dir, args.defer_to_project, args.selftest), ("out", "proj", True))
        args = ms.build_parser().parse_args([])
        self.assertEqual((args.export_dir, args.defer_to_project, args.selftest), (None, None, False))

    def test_a_bad_flag_is_exit_2_and_prints_nothing_on_stdout(self):
        for argv in (["--no-such-flag"], ["--export"], ["--export-dir"], ["stray"]):
            out, err = FakeStream(), io.StringIO()
            with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", err):
                with self.assertRaises(SystemExit) as stopped:
                    ms.main(argv)
            self.assertEqual(stopped.exception.code, bc.EXIT_USAGE, argv)
            self.assertEqual(out.buffer.getvalue(), b"")

    def test_selftest_passes_and_says_so(self):
        fixtures.write_library(self.root / "library")
        before = fixtures.tree_digest(self.tmp)
        out = io.StringIO()
        with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", io.StringIO()):
            code = ms.main(["--selftest", "--root", str(self.root)])
        lines = out.getvalue().splitlines()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(lines[-1], "PASS")
        self.assertTrue(all(line.startswith("ok    ") for line in lines[:-1]), lines)
        self.assertGreaterEqual(len(lines), 9)
        self.assertIn("library/user 3 files, library/official 1 files, index not_ingested", out.getvalue())
        self.assertNotIn(str(self.tmp), out.getvalue())
        self.assertEqual(fixtures.tree_digest(self.tmp), before)

    def test_selftest_fails_when_a_reply_is_wrong(self):
        for broken in ({"ping": lambda params, context: {"pong": True}},
                       {"tools/list": lambda params, context: {"tools": []}},
                       {"initialize": lambda params, context: {}},
                       {"tools/call": lambda params, context: {"content": []}}):
            lines = []
            with mock.patch.dict(ms.METHODS, broken):
                code = ms.selftest(self.context(), lines.append)
            self.assertEqual(code, bc.EXIT_REFUSED, list(broken))
            self.assertEqual(lines[-1], "FAIL")
            self.assertTrue(any(line.startswith("FAIL  ") for line in lines[:-1]))

    def test_selftest_of_a_server_that_stood_down(self):
        lines = []
        self.assertEqual(ms.selftest(self.context(stand_down=True), lines.append), bc.EXIT_OK)
        self.assertIn("ok    tools/list: no tools", lines)

    def test_when_the_plugin_copy_stands_down(self):
        own = Path(ms.__file__).resolve()
        project = self.tmp / "project"
        self.assertFalse(ms.should_stand_down(None))
        self.assertFalse(ms.should_stand_down(""))
        self.assertFalse(ms.should_stand_down(str(project)), "a missing folder")
        self.assertFalse(ms.should_stand_down("${CLAUDE_PROJECT_DIR}"), "a variable nobody expanded")
        project.mkdir()
        self.assertFalse(ms.should_stand_down(str(project)), "a project with no copy")
        theirs = project / "brushes" / "pipeline" / "mcp_server.py"
        theirs.parent.mkdir(parents=True)
        theirs.write_bytes(b"")
        self.assertTrue(ms.should_stand_down(str(project)), "a project with its own copy")
        self.assertTrue(ms.should_stand_down(project))
        self.assertFalse(ms.should_stand_down(str(project), own_file=theirs), "the copy is this file")
        self.assertFalse(ms.should_stand_down(str(own.parents[2])), "started inside its own checkout")

    def test_main_stands_down_only_then(self):
        project = self.tmp / "project"
        (project / "brushes" / "pipeline").mkdir(parents=True)
        (project / "brushes" / "pipeline" / "mcp_server.py").write_bytes(b"")
        data = json.dumps(request("tools/list")).encode("utf-8") + b"\n"
        code, out, err, _ = self.run_main(["--root", str(self.root), "--defer-to-project", str(project)], data)
        self.assertEqual((code, json.loads(out)["result"]["tools"]), (0, []))
        self.assertIn("standing down", err)
        code, out, err, _ = self.run_main(
            ["--root", str(self.root), "--defer-to-project", "${CLAUDE_PROJECT_DIR}"], data)
        self.assertEqual([tool["name"] for tool in json.loads(out)["result"]["tools"]], REGISTERED)
        self.assertNotIn("standing down", err)

    def test_the_mode(self):
        own = self.tmp / "plugins" / "rosw" / "brushes" / "pipeline" / "mcp_server.py"
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
            self.assertEqual(ms.running_mode(None), "project")
            self.assertEqual(ms.running_mode("anything"), "snapshot")
            os.environ["CLAUDE_PLUGIN_ROOT"] = str(self.tmp / "plugins" / "rosw")
            self.assertEqual(ms.running_mode(None, own_file=own), "snapshot")
            self.assertEqual(ms.running_mode(None), "project", "this file is not under that plugin")
            os.environ["CLAUDE_PLUGIN_ROOT"] = "${CLAUDE_PLUGIN_ROOT}"
            self.assertEqual(ms.running_mode(None, own_file=own), "project")
            installed = (self.tmp / ".claude" / "plugins" / "marketplaces" / "m" / "rosw" / "brushes"
                         / "pipeline" / "mcp_server.py")
            self.assertEqual(ms.running_mode(None, own_file=installed), "snapshot")
            self.assertEqual(ms.running_mode(None, own_file=self.tmp / ".claude" / "x" / "mcp_server.py"),
                             "project")

    def test_without_byte_streams_it_is_a_usage_error(self):
        with mock.patch.object(sys, "stdin", None), mock.patch.object(sys, "stdout", io.StringIO()), \
                mock.patch.object(sys, "stderr", io.StringIO()):
            self.assertEqual(ms.main(["--root", str(self.root)]), bc.EXIT_USAGE)

    def test_ctrl_c_is_a_clean_end(self):
        with mock.patch.object(ms, "serve", side_effect=KeyboardInterrupt):
            code, out, _, _ = self.run_main(["--root", str(self.root)])
        self.assertEqual((code, out), (0, b""))


# ── the module, the registration file and the declared contract ──────────────

class TheModule(unittest.TestCase):
    def test_it_is_a_script_with_a_main(self):
        source = (PIPELINE / "mcp_server.py").read_text(encoding="utf-8")
        self.assertTrue(source.rstrip().endswith("raise SystemExit(main())"))
        self.assertIn("sys.path.insert(0, str(Path(__file__).resolve().parent))", source)
        self.assertIn("def main(argv=None):", source)

    def test_it_is_lf_and_names_no_machine_path(self):
        for path in (PIPELINE / "mcp_server.py", Path(__file__)):
            raw = path.read_bytes()
            self.assertNotIn(b"\r", raw, path.name)
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), path.name)
        # This file is not scanned for a path: it spells the pattern itself.
        self.assertIsNone(MACHINE_PATH.search((PIPELINE / "mcp_server.py").read_text(encoding="utf-8")))

    def test_only_the_wire_writes_and_nothing_opens_a_file(self):
        """The server writes nothing: its source calls no file-writing helper,
        opens no file, and prints only to stderr or through `write`."""
        source = (PIPELINE / "mcp_server.py").read_text(encoding="utf-8")
        code = source.split('"""', 2)[2]
        for word in ("open(", "write_text", "write_bytes", "write_json", "mkdir", "os.replace",
                     "os.remove", "unlink", "shutil", "tempfile", "subprocess", "socket", "urllib"):
            self.assertNotIn(word, code, word)
        self.assertEqual(code.count("print("), 1)
        self.assertIn("file=sys.stderr", code)


class Registration(unittest.TestCase):
    """The repository's .mcp.json. Skipped for a copy of brushes/ taken out of
    its repository."""

    @classmethod
    def setUpClass(cls):
        cls.path = REPO / ".mcp.json"
        if not cls.path.is_file():
            raise unittest.SkipTest("brushes/ is not inside its repository: no .mcp.json")
        cls.raw = cls.path.read_bytes()
        cls.declared = json.loads(cls.raw.decode("utf-8"))

    def test_it_declares_a_server_named_brushes(self):
        """The root .mcp.json is shared with other tools (blender-gemini declares
        `gemini` there), so this checks only that `brushes` is one of its servers."""
        self.assertEqual(list(self.declared), ["mcpServers"])
        self.assertIn("brushes", self.declared["mcpServers"])

    def test_the_command_is_python_isolated_and_the_argument_is_the_script(self):
        """`-I` comes first: the full server opens library originals, and a brush
        file is read only by an isolated interpreter (CONTRACTS, section 0)."""
        server = self.declared["mcpServers"]["brushes"]
        self.assertEqual(server, {"command": "python", "args": ["-I", "brushes/pipeline/mcp_server.py"]})
        self.assertEqual(server["args"][0], "-I")
        (script,) = [arg for arg in server["args"] if not arg.startswith("-")]
        self.assertFalse(Path(script).is_absolute())
        self.assertNotIn("\\", script)
        self.assertNotIn("..", script)
        self.assertEqual((REPO / script).resolve(), Path(ms.__file__).resolve())

    def test_the_declared_command_starts_and_passes_its_selftest(self):
        """The registration as an MCP client runs it: from the repository root,
        with the declared command and arguments, plus --selftest."""
        server = self.declared["mcpServers"]["brushes"]
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith(fixtures.ENV_PREFIX)}
        done = subprocess.run([sys.executable, *server["args"], "--selftest"], cwd=str(REPO), env=env,
                              capture_output=True, timeout=120)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        self.assertEqual(done.stdout.decode("utf-8").rstrip().splitlines()[-1], "PASS")

    def test_it_gives_the_server_no_way_to_write(self):
        server = self.declared["mcpServers"]["brushes"]
        self.assertNotIn("--export-dir", server["args"])
        self.assertNotIn("env", server)

    def test_the_file_is_plain_json_with_no_machine_path(self):
        # No line-ending check: the file is outside brushes/, so on a Windows
        # checkout git may hand it out with CRLF. A JSON reader takes either.
        self.assertFalse(self.raw.startswith(b"\xef\xbb\xbf"))
        self.assertTrue(self.raw.rstrip().endswith(b"}"))
        self.assertTrue(self.raw.isascii())
        self.assertIsNone(MACHINE_PATH.search(self.raw.decode("utf-8")))


@unittest.skipIf(yaml is None, "pyyaml is not installed")
class ThePluginEntry(unittest.TestCase):
    """The second registration, for the copy an installed plugin starts
    (docs/CONTRACTS.md, "Registration"). It lives in a file outside brushes/.
    Whichever state that file is in, the spec and the document must say the
    same: `pending` while the entry is not there, `present` once it is, and
    then its shape is checked. Skipped for a copy of brushes/ taken out of its
    repository."""

    @classmethod
    def setUpClass(cls):
        cls.path = REPO / ".claude-plugin" / "plugin.json"
        if not cls.path.is_file():
            raise unittest.SkipTest("brushes/ is not inside its repository: no .claude-plugin/plugin.json")
        cls.plugin = json.loads(cls.path.read_text(encoding="utf-8"))
        cls.spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        cls.declared = cls.spec["surfaces"]["mcp"]["plugin_entry"]
        contracts = (BRUSHES / "docs" / "CONTRACTS.md").read_text(encoding="utf-8")
        start = contracts.index("**Registration.**")
        cls.paragraph = " ".join(contracts[start:contracts.index("\n## F11.", start)].split())

    def entry(self):
        servers = self.plugin.get("mcpServers")
        return servers.get("brushes") if isinstance(servers, dict) else None

    def test_the_declared_entry_has_the_frozen_shape(self):
        self.assertEqual(self.declared["file"], "repo:.claude-plugin/plugin.json")
        self.assertIn(self.declared["state"], ("pending", "present"))
        args = self.declared["args"]
        self.assertEqual(self.declared["command"], "python")
        self.assertEqual(args[0], "-I")
        (script,) = [arg for arg in args if not arg.startswith("-") and not arg.startswith("${CLAUDE_PROJECT")]
        self.assertTrue(script.startswith("${CLAUDE_PLUGIN_ROOT}/"), script)
        self.assertEqual(script, "${CLAUDE_PLUGIN_ROOT}/brushes/pipeline/mcp_server.py")
        self.assertEqual(args[args.index("--defer-to-project") + 1], "${CLAUDE_PROJECT_DIR}")
        self.assertNotIn("--export-dir", args)
        for word in ("`${CLAUDE_PLUGIN_ROOT}/`", "`--defer-to-project ${CLAUDE_PROJECT_DIR}`", "`-I`"):
            self.assertIn(word, self.paragraph)

    def test_the_spec_and_the_document_say_what_the_file_holds(self):
        entry = self.entry()
        if entry is None:
            self.assertEqual(self.declared["state"], "pending",
                             "plugin.json has no mcpServers.brushes: the spec may not call it present")
            self.assertIn("is not there yet", self.paragraph)
            self.assertNotIn("repo:.claude-plugin/plugin.json", self.spec["surfaces"]["mcp"]["declared_in"])
            self.assertIn("must not reach", self.paragraph,
                          "until the entry lands, the root .mcp.json is not to be published")
        else:
            self.assertEqual(self.declared["state"], "present",
                             "plugin.json now has the entry: say so in spec.yaml and CONTRACTS.md")
            self.assertEqual(entry, {"command": self.declared["command"], "args": self.declared["args"]})
            self.assertNotIn("is not there yet", self.paragraph)
            self.assertIn("repo:.claude-plugin/plugin.json", self.spec["surfaces"]["mcp"]["declared_in"])

    def test_the_stand_down_the_entry_relies_on_is_built(self):
        options = {flag for action in ms.build_parser()._actions for flag in action.option_strings}
        self.assertIn("--defer-to-project", options)
        self.assertFalse(ms.should_stand_down("${CLAUDE_PROJECT_DIR}"))


@unittest.skipIf(yaml is None, "pyyaml is not installed")
class TheDeclaredContract(unittest.TestCase):
    """spec.yaml declares the server; this binds the code to that block."""

    @classmethod
    def setUpClass(cls):
        cls.spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        cls.mcp = cls.spec["surfaces"]["mcp"]
        contracts = (BRUSHES / "docs" / "CONTRACTS.md").read_text(encoding="utf-8")
        start = contracts.index("### MCP: `pipeline/mcp_server.py`")
        cls.section = contracts[start:contracts.index("\n## F11.", start)]

    def test_the_script_and_the_server_name(self):
        self.assertEqual(BRUSHES / self.mcp["script"], Path(ms.__file__).resolve())
        self.assertEqual(self.mcp["server"], "brushes")
        self.assertIn("repo:.mcp.json", self.mcp["declared_in"])
        self.assertIn(f'`name: "{ms.SERVER_NAME}"`', self.section)

    def test_every_registered_tool_is_a_declared_one_in_the_declared_order(self):
        declared = self.mcp["tools"]
        registered = [name for name, tool in ms.TOOLS.items() if not tool.needs_export_dir]
        self.assertEqual(registered, [name for name in declared if name in registered])
        self.assertEqual(set(registered) - set(declared), set())
        gated = {name for name, tool in ms.TOOLS.items() if tool.needs_export_dir}
        self.assertTrue(gated <= set(self.mcp["gated_tools"]))
        self.assertEqual(declared[0], "library_status")

    def test_the_declared_flags_are_the_parsers(self):
        declared = self.spec["cli"]["scripts"]["pipeline/mcp_server.py"]
        self.assertEqual(declared["verbs"], [])
        options = {flag for action in ms.build_parser()._actions for flag in action.option_strings}
        for flag in declared["flags"][""]:
            self.assertIn(flag, options)
        self.assertEqual(options - set(declared["flags"][""]) - set(bc.FLAGS.values()), {"-h", "--help"})

    def test_the_protocol_versions_are_the_documents(self):
        for version in ms.PROTOCOL_VERSIONS:
            self.assertIn(f"`{version}`", self.section)
        self.assertIn(f"else `{ms.DEFAULT_PROTOCOL_VERSION}`", self.section)
        for code in (ms.PARSE_ERROR, ms.INVALID_REQUEST, ms.METHOD_NOT_FOUND, ms.INVALID_PARAMS):
            self.assertIn(f"`{code}`", self.section)

    def test_the_line_format_is_the_declared_one(self):
        self.assertEqual(self.mcp["transport"], "stdio; one ASCII JSON object per line")
        self.assertTrue(ms.encode({"name": NAME}).isascii())

    def test_it_writes_nothing_without_an_export_folder(self):
        self.assertEqual(self.mcp["writes"], "nothing unless started with --export-dir")
        self.assertEqual(self.mcp["gated_tools"], {"export_brush": "--export-dir"})


if __name__ == "__main__":
    unittest.main()
