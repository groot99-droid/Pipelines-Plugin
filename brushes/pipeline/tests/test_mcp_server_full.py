"""pipeline/mcp_server.py with its nine read-only tools and the gated
export_brush, over a synthetic library (docs/CONTRACTS.md, F10 "MCP").

test_mcp_server.py pins the protocol with the library_status tool alone; this
file calls every tool through `dispatch`, `handle_line` and `serve`, checks that
a failure is an `isError` result and never a protocol error, that the wire
carries nothing but protocol, and starts the server as a program under
`python -I` from another directory. It reads only a library built in a
temporary folder (test_service.World); the real library, catalog and vault are
never touched.

    python -m unittest discover -s brushes/pipeline/tests -p "test_mcp_server_full.py"
"""

import base64
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import brush_common as bc  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import fixtures  # noqa: E402
import mcp_server as ms  # noqa: E402
import png_io  # noqa: E402
import service  # noqa: E402
import test_service as ts  # noqa: E402

BRUSHES = PIPELINE.parent
SCRIPT = PIPELINE / "mcp_server.py"
NAME = "Conté \U0001f4a7 6B 浓墨"

READ_ONLY = ["library_status", "search_brushes", "get_brush", "similar_brushes", "list_sets",
             "list_vocabulary", "get_preview", "get_brush_settings_schema", "validate_settings_patch"]

try:
    import yaml
except ImportError:
    yaml = None


def request(method, params=None, request_id=1):
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    return message


def payload_of(reply):
    block = reply["result"]["content"][0]
    assert block["type"] == "text", block
    return json.loads(block["text"])


class FakeStream:
    def __init__(self, data=b""):
        self.buffer = io.BytesIO(data)


class ServerCase(ts.WorldCase):
    """A context over the shared synthetic world."""

    def context(self, **options):
        options.setdefault("log", self.logged.append)
        return ms.make_context(self.world.paths, **options)

    def setUp(self):
        super().setUp()
        self.logged = []

    def call(self, name, arguments=None, **options):
        params = {"name": name}
        if arguments is not None:
            params["arguments"] = arguments
        return ms.dispatch(request("tools/call", params), self.context(**options))

    def ok(self, name, arguments=None, **options):
        reply = self.call(name, arguments, **options)
        self.assertIs(reply["result"]["isError"], False, reply["result"]["content"][0]["text"][:300])
        return payload_of(reply)

    def refused(self, name, arguments=None, code=None, **options):
        reply = self.call(name, arguments, **options)
        self.assertNotIn("error", reply, "a tool failure is a result, not a protocol error")
        self.assertIs(reply["result"]["isError"], True, name)
        self.assertEqual(len(reply["result"]["content"]), 1)
        error = payload_of(reply)["error"]
        self.assertEqual(set(error), {"code", "message", "hint"})
        self.assertNotIn("Traceback", reply["result"]["content"][0]["text"])
        if code is not None:
            self.assertEqual(error["code"], code, error["message"])
        return error

    def ident(self, name):
        return self.world.ids[name]


# ── the list ─────────────────────────────────────────────────────────────────

class Listing(ServerCase):
    def tools(self, **options):
        return ms.dispatch(request("tools/list"), self.context(**options))["result"]["tools"]

    def test_the_nine_tools_in_the_declared_order_and_export_only_with_a_folder(self):
        self.assertEqual([t["name"] for t in self.tools()], READ_ONLY)
        listed = self.tools(export_dir=self.tmp / "exports")
        self.assertEqual([t["name"] for t in listed], READ_ONLY + ["export_brush"])
        self.assertFalse((self.tmp / "exports").exists())

    def test_every_entry_is_a_well_formed_read_only_tool(self):
        for tool in self.tools(export_dir=self.tmp / "exports"):
            schema = tool["inputSchema"]
            self.assertEqual(schema["type"], "object")
            self.assertIs(schema["additionalProperties"], False, tool["name"])
            self.assertTrue(set(schema.get("required", [])) <= set(schema["properties"]))
            self.assertGreater(len(tool["description"]), 80, tool["name"])
            self.assertLessEqual(len(tool["description"]), 1800)
            json.dumps(tool, allow_nan=False)
            self.assertTrue(tool["title"].strip())
            if tool["name"] == "export_brush":
                self.assertEqual(tool["annotations"], {"readOnlyHint": False, "destructiveHint": False,
                                                       "idempotentHint": False, "openWorldHint": False})
            else:
                self.assertEqual(tool["annotations"], {"readOnlyHint": True, "openWorldHint": False}, tool["name"])

    def test_the_argument_limits_are_the_contracts(self):
        tools = {t["name"]: t["inputSchema"]["properties"] for t in self.tools()}
        search = tools["search_brushes"]
        self.assertEqual((search["query"]["maxLength"], search["tags"]["maxItems"], search["where"]["maxItems"],
                          search["where_not"]["maxItems"]), (500, 12, 12, 12))
        self.assertEqual((search["top"]["minimum"], search["top"]["maximum"], search["top"]["default"]), (1, 25, 8))
        self.assertEqual(tools["similar_brushes"]["top"]["maximum"], 25)
        self.assertEqual(tools["get_preview"]["kinds"]["items"]["enum"], ["stroke", "shape", "grain"])
        self.assertEqual(tools["get_preview"]["kinds"]["maxItems"], 3)
        self.assertEqual(tools["get_brush_settings_schema"]["keys"]["maxItems"], 60)
        self.assertEqual(tools["get_brush_settings_schema"]["detail"]["enum"], ["compact", "full"])
        self.assertEqual(tools["list_sets"]["library"]["enum"], ["user", "official"])
        self.assertEqual(tools["get_brush"]["include"]["items"]["enum"],
                         ["settings", "tags", "facets", "visual", "textures", "note"])
        for name in ("get_brush", "similar_brushes", "get_preview"):
            self.assertEqual(tools[name]["id"]["pattern"], "^b_[0-9a-f]{12}$")
        self.assertEqual(set(tools["validate_settings_patch"]), {"changes", "base_id", "base", "era"})
        self.assertEqual(set(tools["export_brush"] if "export_brush" in tools else {"base_id", "changes", "name",
                                                                                    "confirm"}),
                         {"base_id", "changes", "name", "confirm"})

    def test_the_instructions_name_export_brush_only_when_it_is_listed(self):
        plain = ms.dispatch(request("initialize"), self.context())["result"]["instructions"]
        gated = ms.dispatch(request("initialize"), self.context(export_dir=self.tmp / "x"))["result"]["instructions"]
        self.assertNotIn("export_brush", plain)
        self.assertIn("export_brush", gated)
        self.assertTrue(gated.startswith(plain))
        stood = ms.dispatch(request("initialize"), self.context(export_dir=self.tmp / "x", stand_down=True))
        self.assertNotIn("export_brush", stood["result"]["instructions"])

    def test_the_selftest_checks_a_refusing_tool(self):
        lines = []
        self.assertEqual(ms.selftest(self.context(), lines.append), 0)
        self.assertTrue(any("isError result, not a protocol error" in line for line in lines), lines)

    def test_the_two_large_results_ask_for_room(self):
        by_name = {t["name"]: t for t in self.tools()}
        for name in ("get_brush", "get_brush_settings_schema"):
            self.assertEqual(by_name[name]["_meta"], {"anthropic/maxResultSizeChars": 120000})
        self.assertNotIn("_meta", by_name["library_status"])

    @unittest.skipIf(yaml is None, "pyyaml is not installed")
    def test_the_registry_is_the_specs(self):
        spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        self.assertEqual(spec["surfaces"]["mcp"]["tools"], READ_ONLY)
        self.assertEqual(list(spec["surfaces"]["mcp"]["gated_tools"]), ["export_brush"])


# ── each tool ────────────────────────────────────────────────────────────────

class Tools(ServerCase):
    def test_library_status_reads_the_world(self):
        status = self.ok("library_status")
        self.assertEqual((status["server"], status["index"]["state"], status["counts"]["brushes"]),
                         ("rosw-brushes", "memory", 8))
        self.assertEqual(status["export"], {"enabled": False, "dir": None})
        self.assertEqual(self.ok("library_status", export_dir=self.tmp / "e")["export"],
                         {"enabled": True, "dir": "e"})

    def test_search_brushes(self):
        found = self.ok("search_brushes", {"query": "conte"})
        self.assertEqual(found["results"][0]["brush_id"], self.ident("conte"))
        self.assertEqual((found["index"], found["ranking"]), ("memory", "cosine"))
        by_where = self.ok("search_brushes", {"where": ["kind=stamp"], "top": 25})
        self.assertEqual([r["brush_id"] for r in by_where["results"]], [self.ident("inker2")])
        self.assertEqual(self.ok("search_brushes", {"query": "inker", "where_not": ["kind=stamp"]})["total"], 1)
        self.assertEqual(self.ok("search_brushes", {"query": "zzzzz qqqqq"})["results"], [])

    def test_search_needs_a_query_a_tag_or_a_filter(self):
        error = self.refused("search_brushes", {}, "bad_argument")
        self.assertIn("at least one", error["message"])
        self.refused("search_brushes", {"top": 5}, "bad_argument")
        self.refused("search_brushes", {"query": "  "}, "bad_argument")
        self.refused("search_brushes", {"where_not": ["kind=stamp"]}, "bad_argument")

    def test_search_arguments_the_schema_refuses(self):
        for arguments in ({"query": "x", "top": 26}, {"query": "x", "top": 0}, {"query": "x", "top": "8"},
                          {"query": "x" * 501}, {"query": 5}, {"tags": ["medium=x"] * 13},
                          {"tags": ["Medium=x"]}, {"tags": ["medium"]}, {"tags": "medium=x"},
                          {"where": ["a=b"] * 13}, {"where": [5]}, {"query": "x", "offset": 3},
                          {"query": "x", "settings": True}):
            self.refused("search_brushes", arguments, "bad_argument")

    def test_an_unknown_axis_tag_or_facet_is_bad_argument_and_never_an_empty_result(self):
        self.refused("search_brushes", {"tags": ["colour=red"]}, "bad_argument")
        error = self.refused("search_brushes", {"tags": ["medium=nope"]}, "bad_argument")
        self.assertTrue(error["message"])
        self.refused("search_brushes", {"where": ["no_such_facet=1"]}, "bad_argument")

    def test_get_brush(self):
        brush = self.ok("get_brush", {"id": self.ident("dual")})
        self.assertEqual((brush["name"], brush["family"], brush["dual"]["name"]),
                         ("Modern Dual", "modern", "Modern Dual Secondary"))
        self.assertNotIn("settings", brush)
        full = self.ok("get_brush", {"id": self.ident("dual"), "include": ["settings"]})
        self.assertEqual(full["settings"]["name"], "Modern Dual")
        self.assertEqual(self.ok("get_brush", {"id": self.ident("dual"), "include": []}).get("facets"), None)

    def test_get_brush_refusals(self):
        error = self.refused("get_brush", {"id": "b_000000000000"}, "unknown_id")
        self.assertIn("search_brushes", error["hint"])
        for arguments in ({}, {"id": "nope"}, {"id": "B_0123456789AB"}, {"id": "../../x"}, {"id": 5},
                          {"id": self.ident("dual"), "include": ["everything"]},
                          {"id": self.ident("dual"), "include": ["settings"] * 7},
                          {"id": self.ident("dual"), "extra": 1}):
            self.refused("get_brush", arguments, "bad_argument")

    def test_similar_brushes(self):
        found = self.ok("similar_brushes", {"id": self.ident("inker"), "top": 3})
        self.assertEqual((found["method"], len(found["results"])), ("gower-v1", 3))
        self.assertNotIn(self.ident("inker"), [r["brush_id"] for r in found["results"]])
        narrowed = self.ok("similar_brushes", {"id": self.ident("inker"), "where": ["library=official"]})
        self.assertTrue(all(r["library"] == "official" for r in narrowed["results"]))
        self.refused("similar_brushes", {"id": "b_000000000000"}, "unknown_id")
        self.refused("similar_brushes", {"id": self.ident("inker"), "top": 26}, "bad_argument")

    def test_list_sets(self):
        sets = self.ok("list_sets")["sets"]
        self.assertEqual({s["set_slug"] for s in sets}, {"demo-set", "demo-modern", "demo-pack-loose"})
        self.assertEqual([s["set_slug"] for s in self.ok("list_sets", {"library": "official"})["sets"]],
                         ["demo-modern"])
        self.refused("list_sets", {"library": "mine"}, "bad_argument")
        self.refused("list_sets", {"source": "user"}, "bad_argument")

    def test_list_vocabulary(self):
        listed = self.ok("list_vocabulary")
        self.assertEqual(set(listed), {"axes", "facets"})
        self.assertTrue(any(f["name"] == "kind" for f in listed["facets"]))
        self.refused("list_vocabulary", {"axis": "colour"}, "bad_argument")

    def test_get_preview_returns_png_blocks_after_a_text_block(self):
        reply = self.call("get_preview", {"id": self.ident("inker"), "kinds": ["stroke", "shape", "grain"]})
        content = reply["result"]["content"]
        self.assertIs(reply["result"]["isError"], False)
        self.assertEqual([block["type"] for block in content], ["text", "image", "image", "image"])
        text = json.loads(content[0]["text"])
        self.assertEqual([i["kind"] for i in text["images"]], ["stroke", "shape", "grain"])
        self.assertEqual(text["missing"], [])
        for block in content[1:]:
            self.assertEqual(block["mimeType"], "image/png")
            self.assertTrue(base64.b64decode(block["data"], validate=True).startswith(png_io.SIGNATURE))
        stroke = png_io.read_png(base64.b64decode(content[1]["data"]))
        self.assertEqual((stroke.width, stroke.height), (530, 162))
        default = self.call("get_preview", {"id": self.ident("inker")})
        self.assertEqual(len(default["result"]["content"]), 2, "stroke is the default kind")

    def test_get_preview_names_what_is_missing_and_errors_only_when_nothing_exists(self):
        partial = self.call("get_preview", {"id": self.ident("pencil"), "kinds": ["stroke", "shape"]})
        text = json.loads(partial["result"]["content"][0]["text"])
        self.assertEqual([m["kind"] for m in text["missing"]], ["shape"])
        self.assertEqual(len(partial["result"]["content"]), 2)
        error = self.refused("get_preview", {"id": self.ident("pencil"), "kinds": ["shape", "grain"]}, "no_preview")
        self.assertIn("previews.py", error["hint"])
        self.refused("get_preview", {"id": self.ident("pencil"), "kinds": []}, "bad_argument")
        self.refused("get_preview", {"id": self.ident("pencil"), "kinds": ["thumbnail"]}, "bad_argument")
        self.refused("get_preview", {"id": self.ident("pencil"), "kinds": ["stroke"] * 4}, "bad_argument")
        self.refused("get_preview", {"id": "b_000000000000"}, "unknown_id")

    def test_get_brush_settings_schema(self):
        compact = self.ok("get_brush_settings_schema")
        self.assertEqual(len(compact["keys"]), 260)
        group = self.ok("get_brush_settings_schema", {"group": "taper", "detail": "full"})
        self.assertTrue(all(row["group"] == "taper" for row in group["keys"].values()))
        self.assertIn("label", next(iter(group["keys"].values())))
        self.refused("get_brush_settings_schema", {"group": "nope"}, "bad_argument")
        self.refused("get_brush_settings_schema", {"detail": "huge"}, "bad_argument")
        self.refused("get_brush_settings_schema", {"keys": ["a"] * 61}, "bad_argument")

    def test_validate_settings_patch(self):
        report = self.ok("validate_settings_patch", {"changes": {"plotSpacing": 0.25}, "base_id": self.ident("inker")})
        self.assertTrue(report["ok"])
        self.assertEqual(json.loads(report["patch_text"])["changes"], {"plotSpacing": 0.25})
        widened = self.ok("validate_settings_patch", {"changes": {"plotSpacing": 0.2}, "base_id": self.ident("inker")})
        self.assertEqual(widened["applied"]["plotSpacing"], 0.20000000298023224, "the 32-bit float, widened")
        rejected = self.ok("validate_settings_patch", {"changes": {"nope": 1}, "base_id": self.ident("inker")})
        self.assertFalse(rejected["ok"], "a rejected key is a finding, not a tool error")
        self.assertEqual(rejected["rejected"][0]["code"], "unknown_key")
        self.refused("validate_settings_patch", {}, "bad_argument")
        self.refused("validate_settings_patch", {"changes": []}, "bad_argument")
        self.refused("validate_settings_patch", {"changes": {}, "base_id": self.ident("inker"),
                                                 "base": {"members": []}}, "bad_argument")
        self.refused("validate_settings_patch", {"changes": {}, "base_id": "nope"}, "bad_argument")

    def test_the_patch_text_carries_a_non_ascii_name_through_one_ascii_line(self):
        context = self.context()
        line = json.dumps(request("tools/call", {"name": "validate_settings_patch", "arguments": {
            "changes": {"name": NAME}, "base_id": self.ident("inker")}}), ensure_ascii=False).encode("utf-8")
        raw = ms.handle_line(line + b"\n", context)
        self.assertTrue(raw.isascii())
        self.assertEqual((raw.count(b"\n"), b"\r" in raw), (1, False))
        reply = json.loads(raw)
        self.assertEqual(json.loads(payload_of(reply)["patch_text"])["changes"]["name"], NAME)

    def test_a_tool_that_raises_something_unexpected_is_internal_and_the_server_goes_on(self):
        with mock.patch.object(service.BrushService, "list_sets", side_effect=RuntimeError("secret /private/path")):
            error = self.refused("list_sets", {}, "internal")
        self.assertNotIn("secret", json.dumps(error))
        self.assertIn("secret /private/path", "".join(self.logged))
        self.assertTrue(self.ok("list_sets")["sets"])

    def test_an_api_error_keeps_its_code_message_and_hint(self):
        empty = Path(tempfile.mkdtemp(prefix="brushes-empty-")).resolve()
        self.addCleanup(shutil.rmtree, empty, ignore_errors=True)
        context = ms.make_context(bc.resolve_paths(root=empty / "brushes"))
        for name, arguments in (("search_brushes", {"query": "ink"}), ("list_sets", {}),
                                ("get_brush", {"id": "b_0123456789ab"}), ("list_vocabulary", {})):
            reply = ms.dispatch(request("tools/call", {"name": name, "arguments": arguments}), context)
            if name == "list_vocabulary":
                self.assertIs(reply["result"]["isError"], False, "it works with no catalog")
                continue
            error = payload_of(reply)["error"]
            self.assertIs(reply["result"]["isError"], True)
            self.assertEqual(error["code"], "not_ingested", name)
            self.assertIn("ingest.py build", error["hint"])
        status = payload_of(ms.dispatch(request("tools/call", {"name": "library_status"}), context))
        self.assertEqual(status["index"]["state"], "not_ingested")
        self.assertTrue(status["next_steps"])

    def test_the_protocol_errors_are_only_for_a_call_that_is_not_a_call(self):
        context = self.context()
        for params in (None, {}, {"name": 5}, {"name": "no_such_tool"}, {"name": "library_status", "arguments": []},
                       {"name": "export_brush", "arguments": {"base_id": self.ident("inker")}}):
            reply = ms.dispatch(request("tools/call", params), context)
            self.assertEqual(reply["error"]["code"], ms.INVALID_PARAMS, params)


# ── export_brush ─────────────────────────────────────────────────────────────

class ExportBrush(ServerCase):
    def setUp(self):
        super().setUp()
        self.out = Path(tempfile.mkdtemp(prefix="brushes-mcp-out-")).resolve()
        self.addCleanup(shutil.rmtree, self.out, ignore_errors=True)
        self.dir = self.out / "exports"

    def test_a_dry_run_is_the_default_and_writes_nothing(self):
        before = ts.snapshot(self.tmp)
        result = self.ok("export_brush", {"base_id": self.ident("inker"), "changes": {"plotSpacing": 0.25}},
                         export_dir=self.dir)
        self.assertIs(result["dry_run"], True)
        self.assertEqual(result["would_write"], f"demo-inker-{self.ident('inker')[2:10]}.brush")
        self.assertFalse(self.dir.exists())
        self.assertEqual(ts.snapshot(self.tmp), before)

    def test_confirm_writes_one_file_inside_the_folder_and_never_over_another(self):
        arguments = {"base_id": self.ident("inker"), "name": NAME, "changes": {"plotSpacing": 0.25}, "confirm": True}
        result = self.ok("export_brush", arguments, export_dir=self.dir)
        written = sorted(self.dir.iterdir())
        self.assertEqual([p.name for p in written], [result["written"]])
        self.assertTrue(result["written"].isascii())
        self.assertTrue(result["written"].endswith(f"-{self.ident('inker')[2:10]}.brush"))
        folder = container.read_brush(written[0].read_bytes())
        self.assertEqual(brush_model.decode(folder.archive).name, NAME)
        self.assertEqual(self.refused("export_brush", arguments, "exists", export_dir=self.dir)["code"], "exists")
        self.assertEqual([p.name for p in self.dir.iterdir()], [result["written"]])

    def test_no_path_component_can_be_supplied(self):
        for arguments in ({"base_id": self.ident("inker"), "name": "../../evil", "confirm": True},
                          {"base_id": self.ident("inker"), "name": "a/b\\c", "confirm": True}):
            result = self.ok("export_brush", arguments, export_dir=self.dir)
            self.assertNotIn("/", result["written"])
            self.assertNotIn("\\", result["written"])
            self.assertEqual({p.parent for p in self.dir.iterdir()}, {self.dir})
        self.refused("export_brush", {"base_id": "../../x", "confirm": True}, "bad_argument", export_dir=self.dir)
        self.refused("export_brush", {"base_id": self.ident("inker"), "path": "/tmp/x"}, "bad_argument",
                     export_dir=self.dir)
        self.refused("export_brush", {"base_id": self.ident("inker"), "confirm": "yes"}, "bad_argument",
                     export_dir=self.dir)
        self.refused("export_brush", {"base_id": self.ident("inker"), "name": ""}, "bad_argument", export_dir=self.dir)

    def test_a_rejected_change_writes_nothing(self):
        error = self.refused("export_brush", {"base_id": self.ident("inker"), "changes": {"nope": 1},
                                              "confirm": True}, "invalid_settings", export_dir=self.dir)
        self.assertTrue(error["message"])
        self.assertFalse(self.dir.exists())

    def test_the_data_roots_are_untouched(self):
        before = ts.snapshot(self.tmp)
        self.ok("export_brush", {"base_id": self.ident("dual"), "confirm": True}, export_dir=self.dir)
        self.assertEqual(ts.snapshot(self.tmp), before)


# ── the wire ─────────────────────────────────────────────────────────────────

class Wire(ServerCase):
    def test_a_whole_session_over_the_loop(self):
        lines = [request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                        "clientInfo": {"name": "t", "version": "1"}}, 0),
                 {"jsonrpc": "2.0", "method": "notifications/initialized"},
                 request("ping", request_id=1),
                 request("tools/list", request_id=2),
                 request("tools/call", {"name": "library_status"}, 3),
                 request("tools/call", {"name": "search_brushes", "arguments": {"query": NAME}}, 4),
                 request("tools/call", {"name": "get_preview", "arguments": {"id": self.ident("inker")}}, 5),
                 request("resources/list", request_id=6),
                 request("server/discover", request_id=7),
                 request("tools/call", {"name": "get_brush", "arguments": {"id": "bad"}}, 8)]
        data = b"".join(json.dumps(line, ensure_ascii=False).encode("utf-8") + b"\n" for line in lines)
        out = io.BytesIO()
        self.assertEqual(ms.serve(io.BytesIO(data), out, self.context()), 0)
        raw = out.getvalue()
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.isascii())
        replies = [json.loads(line) for line in raw.split(b"\n") if line]
        self.assertEqual([r["id"] for r in replies], [0, 1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual(replies[0]["result"]["serverInfo"]["name"], "rosw-brushes")
        self.assertEqual(replies[5]["result"]["content"][1]["mimeType"], "image/png")
        for position in (6, 7):
            self.assertEqual(replies[position]["error"]["code"], ms.METHOD_NOT_FOUND)
        self.assertEqual(replies[6]["error"]["data"], "resources/list")
        self.assertIs(replies[8]["result"]["isError"], True)

    def test_a_batch_of_calls(self):
        batch = [request("tools/call", {"name": "list_sets"}, 1), request("ping", request_id=2),
                 {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 9}},
                 request("tools/call", {"name": "nope"}, 3)]
        replies = ms.dispatch(batch, self.context())
        self.assertEqual([r["id"] for r in replies], [1, 2, 3])
        self.assertIn("result", replies[0])
        self.assertEqual(replies[2]["error"]["code"], ms.INVALID_PARAMS)

    def test_a_print_in_a_tool_cannot_reach_the_client(self):
        data = b"".join(json.dumps(m).encode("utf-8") + b"\n" for m in (
            request("tools/call", {"name": "list_sets"}, 1), request("ping", request_id=2)))
        noisy = ms.tool_table(ms.Tool(name="list_sets", title="Noisy", description="prints before it answers " * 3,
                                      input_schema=ms.NO_ARGUMENTS,
                                      handler=lambda a, c: print("NOISE") or {"sets": []}))
        out, err = FakeStream(), io.StringIO()
        with mock.patch.object(sys, "stdin", FakeStream(data)), mock.patch.object(sys, "stdout", out), \
                mock.patch.object(sys, "stderr", err), mock.patch.object(ms, "TOOLS", noisy):
            code = ms.main(["--root", str(self.world.root)])
        self.assertEqual(code, 0)
        wire = out.buffer.getvalue()
        self.assertNotIn(b"NOISE", wire)
        self.assertEqual([json.loads(line)["id"] for line in wire.splitlines()], [1, 2])
        self.assertIn("NOISE", err.getvalue())

    def test_a_long_result_is_still_one_line(self):
        reply = ms.handle_line(json.dumps(request("tools/call", {"name": "get_brush", "arguments": {
            "id": self.ident("dual"), "include": ["settings", "tags", "facets", "visual", "textures", "note"]}}
        )).encode("utf-8") + b"\n", self.context())
        self.assertGreater(len(reply), 8000)
        self.assertEqual(reply.count(b"\n"), 1)

    def test_nothing_is_written_by_serving_every_tool(self):
        before = ts.snapshot(self.tmp)
        calls = [("library_status", {}), ("search_brushes", {"query": "ink"}), ("get_brush", {"id": self.ident("inker")}),
                 ("similar_brushes", {"id": self.ident("inker")}), ("list_sets", {}), ("list_vocabulary", {}),
                 ("get_preview", {"id": self.ident("inker"), "kinds": ["stroke", "shape", "grain"]}),
                 ("get_brush_settings_schema", {"detail": "full"}),
                 ("validate_settings_patch", {"changes": {"stamp": True}, "base_id": self.ident("inker")})]
        context = self.context()
        for name, arguments in calls:
            reply = ms.dispatch(request("tools/call", {"name": name, "arguments": arguments}), context)
            self.assertIs(reply["result"]["isError"], False, name)
        self.assertEqual(ts.snapshot(self.tmp), before)


# ── started as a program ─────────────────────────────────────────────────────

class AsAProgram(ts.WorldCase):
    """The registration as an MCP client runs it: `python -I`, another working
    directory, a data root that is not the script's own."""

    def setUp(self):
        super().setUp()
        self.env = {k: v for k, v in os.environ.items() if not k.upper().startswith(fixtures.ENV_PREFIX)}
        self.cwd = Path(tempfile.mkdtemp(prefix="brushes-cwd-")).resolve()
        self.addCleanup(shutil.rmtree, self.cwd, ignore_errors=True)

    def run_server(self, messages, *args, script=SCRIPT, timeout=120):
        data = b"".join(json.dumps(m, ensure_ascii=False).encode("utf-8") + b"\n" for m in messages)
        return subprocess.run([sys.executable, "-I", str(script), "--root", str(self.world.root), *args],
                              input=data, capture_output=True, cwd=str(self.cwd), env=self.env, timeout=timeout)

    def test_the_whole_conversation_under_python_dash_I(self):
        before = ts.snapshot(self.tmp)
        done = self.run_server([
            request("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                                   "clientInfo": {"name": "t", "version": "1"}}, 1),
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            request("tools/list", request_id=2),
            request("tools/call", {"name": "library_status"}, 3),
            request("tools/call", {"name": "search_brushes", "arguments": {"query": "conte"}}, 4),
            request("tools/call", {"name": "get_preview", "arguments": {"id": self.world.ids["inker"]}}, 5),
            request("tools/call", {"name": "validate_settings_patch", "arguments": {
                "changes": {"plotSpacing": 0.2}, "base_id": self.world.ids["inker"]}}, 6)])
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        replies = [json.loads(line) for line in done.stdout.split(b"\n") if line]
        self.assertEqual([r["id"] for r in replies], [1, 2, 3, 4, 5, 6])
        self.assertTrue(done.stdout.isascii())
        self.assertEqual([t["name"] for t in replies[1]["result"]["tools"]], READ_ONLY)
        self.assertEqual(payload_of(replies[2])["counts"]["brushes"], 8)
        self.assertEqual(payload_of(replies[3])["results"][0]["brush_id"], self.world.ids["conte"])
        self.assertEqual(replies[4]["result"]["content"][1]["type"], "image")
        self.assertTrue(payload_of(replies[5])["ok"])
        self.assertEqual(len(done.stderr.decode("utf-8").splitlines()), 1, "one log line, at start")
        self.assertEqual(ts.snapshot(self.tmp), before)
        self.assertEqual(list(self.cwd.iterdir()), [], "nothing is written where it was started")

    def test_a_server_with_an_export_folder_writes_only_there(self):
        target = self.cwd / "out"
        done = self.run_server([
            request("tools/call", {"name": "export_brush", "arguments": {
                "base_id": self.world.ids["inker"], "changes": {"plotSpacing": 0.25}, "confirm": True}}, 1)],
            "--export-dir", str(target))
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        result = payload_of(json.loads(done.stdout.splitlines()[0]))
        self.assertEqual([p.name for p in target.iterdir()], [result["written"]])
        self.assertEqual([p.name for p in self.cwd.iterdir()], ["out"])

    def test_a_bad_export_folder_is_exit_2(self):
        done = self.run_server([], "--export-dir", str(self.world.root / "library" / "x"))
        self.assertEqual(done.returncode, 2)
        self.assertEqual(done.stdout, b"")
        self.assertIn(b"--export-dir", done.stderr)

    def test_the_selftest_passes_from_another_directory(self):
        done = subprocess.run([sys.executable, "-I", str(SCRIPT), "--selftest", "--root", str(self.world.root)],
                              capture_output=True, cwd=str(self.cwd), env=self.env, timeout=120)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        self.assertEqual(done.stdout.decode("utf-8").rstrip().splitlines()[-1], "PASS")

    def test_a_copy_of_the_code_runs_and_leaves_no_bytecode_behind(self):
        """What a plugin snapshot is: the scripts, the schema and the search
        tool, in a folder of their own."""
        copy = self.cwd / "brushes"
        (copy / "pipeline").mkdir(parents=True)
        for path in PIPELINE.glob("*.py"):
            shutil.copy2(path, copy / "pipeline" / path.name)
        shutil.copytree(BRUSHES / "schema", copy / "schema")
        (copy / "vault" / "tools").mkdir(parents=True)
        shutil.copy2(BRUSHES / "vault" / "tools" / "brush_search.py", copy / "vault" / "tools" / "brush_search.py")
        done = self.run_server([request("tools/call", {"name": "search_brushes", "arguments": {"query": "conte"}}, 1),
                                request("tools/call", {"name": "get_brush_settings_schema", "arguments": {}}, 2)],
                               script=copy / "pipeline" / "mcp_server.py")
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        replies = [json.loads(line) for line in done.stdout.split(b"\n") if line]
        self.assertEqual(payload_of(replies[0])["results"][0]["brush_id"], self.world.ids["conte"])
        self.assertEqual(len(payload_of(replies[1])["keys"]), 260)
        self.assertEqual([str(p) for p in copy.rglob("__pycache__")], [])

    def test_a_dead_pipe_and_an_empty_input_end_cleanly(self):
        self.assertEqual(self.run_server([]).returncode, 0)


class TheSource(unittest.TestCase):
    def test_it_reaches_the_disk_only_through_the_service(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for word in ("open(", "write_text", "write_bytes", "mkdir", "os.replace", "unlink", "shutil", "tempfile",
                     "subprocess", "socket", "urllib", "pathlib.Path(", "json.load("):
            self.assertNotIn(word, source.split('"""', 2)[2], word)
        self.assertNotIn("import yaml", source)

    def test_the_names_the_tests_and_the_spec_read_are_still_here(self):
        for name in ("library_status", "NEXT_STEPS", "next_steps", "repo_relative", "count_files", "INDEX_STATES",
                     "MODES", "make_context", "dispatch", "handle_line", "serve", "selftest", "TOOLS", "Tool",
                     "ToolOutput", "ToolError"):
            self.assertTrue(hasattr(ms, name), name)
        self.assertIs(ms.NEXT_STEPS, service.NEXT_STEPS)
        self.assertEqual(ms.SERVER_VERSION, service.SERVER_VERSION)


if __name__ == "__main__":
    unittest.main()
