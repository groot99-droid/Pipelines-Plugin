"""The add-on tools server, against a fake MCP for Blender socket.

The fake records the code it is sent and answers with a canned reply, so these
tests need no Blender. What the generated code does inside a real Blender is
checked by hand (see the blender-addon-tools skill)."""

import ast
import io
import json
import os
import shutil
import socket
import sys
import tempfile
import threading
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "addon-tools"))
import server  # noqa: E402

MANIFEST = {
    "addon": "demo_addon",
    "tools": [
        {"name": "demo_make_cube", "enabled": True, "description": "Add a cube", "op": "demo.make_cube", "context": "VIEW_3D",
         "params": {"size": {"type": "number", "minimum": 0.01, "default": 1.0},
                    "label": {"type": "string", "required": True},
                    "style": {"type": "string", "enum": ["PLAIN", "FANCY"], "default": "PLAIN"},
                    "offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}}},
        {"name": "demo_count", "enabled": True, "read_only": True, "code": ["report(count=len(bpy.data.objects))"]},
        {"name": "demo_hidden", "enabled": False, "op": "demo.secret"},
    ],
}

INSPECTED = {
    "module": "bl_ext.user_default.demo_addon", "name": "Demo", "version": "1.2.3",
    "panels": [{"label": "Demo", "space": "VIEW_3D", "region": "UI", "category": "Demo"}],
    "operators": [{
        "idname": "demo.make_cube", "label": "Make Cube", "description": "Add a cube", "options": ["REGISTER"],
        "properties": [
            {"identifier": "size", "type": "FLOAT", "name": "Size", "description": "", "default": 1,
             "min": 0.009999999776, "max": 3.4e38},
            {"identifier": "count", "type": "INT", "name": "Count", "description": "How many", "default": 1,
             "min": 1, "max": 2147483647},
            {"identifier": "style", "type": "ENUM", "name": "Style", "description": "", "flag": False,
             "items": ["PLAIN", "FANCY"], "default": "PLAIN"},
            {"identifier": "layers", "type": "ENUM", "name": "Layers", "description": "", "flag": True,
             "items": ["A", "B"], "default": ["A"]},
            {"identifier": "preset", "type": "ENUM", "name": "Preset", "description": "", "flag": False,
             "items": [], "default": ""},
            {"identifier": "offset", "type": "FLOAT", "name": "Offset", "description": "", "array_length": 3,
             "default": [0, 0, 0], "min": -1e9, "max": 1e9},
            {"identifier": "target", "type": "POINTER", "name": "Target", "description": ""},
            {"identifier": "secret", "type": "STRING", "name": "", "description": "", "hidden": True,
             "default": ""},
        ]}],
}


class FakeBlender:
    """Answers one JSON command per connection, like the add-on's socket."""

    def __init__(self, reply):
        self.reply = reply
        self.received = []
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen()
        self.port = self.sock.getsockname()[1]
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def loop(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            with conn:
                buffer = b""
                while True:
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    buffer += chunk
                    try:
                        command = json.loads(buffer)
                        break
                    except ValueError:
                        continue
                self.received.append(command)
                conn.sendall(json.dumps(self.reply(command)).encode("utf-8"))

    def close(self):
        self.sock.close()


def printed(found, extra=""):
    return {"status": "success",
            "result": {"executed": True, "result": extra + server.MARKER + json.dumps(found) + "\n"}}


class Case(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="addon-tools-test-"))
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        (self.dir / "demo.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
        self.fake = None
        self.saved = {k: os.environ.get(k) for k in ("BLENDER_PORT", "BLENDER_HOST", "BLENDER_ADDON_TOOLS_DIR")}
        os.environ["BLENDER_HOST"] = "127.0.0.1"
        os.environ["BLENDER_ADDON_TOOLS_DIR"] = str(self.dir)
        self.addCleanup(self.restore)

    def restore(self):
        for key, value in self.saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        if self.fake:
            self.fake.close()

    def blender(self, reply=lambda command: printed({"ok": True})):
        self.fake = FakeBlender(reply)
        os.environ["BLENDER_PORT"] = str(self.fake.port)
        return self.fake

    def call(self, name, arguments=None):
        reply = server.handle({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                               "params": {"name": name, "arguments": arguments or {}}}, self.dir)
        return reply["result"]


class Manifests(Case):
    def test_listing_comes_from_the_manifests(self):
        (self.dir / "demo.draft.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
        (self.dir / "broken.json").write_text("{not json", encoding="utf-8")
        with contextlib_quiet():
            reply = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, self.dir)
        names = [t["name"] for t in reply["result"]["tools"]]
        self.assertEqual(names, [*server.BUILTINS, "demo_make_cube", "demo_count"])
        count = next(t for t in reply["result"]["tools"] if t["name"] == "demo_count")
        self.assertTrue(count["annotations"]["readOnlyHint"])
        cube = next(t for t in reply["result"]["tools"] if t["name"] == "demo_make_cube")
        self.assertEqual(cube["inputSchema"]["required"], ["label"])
        self.assertFalse(cube["inputSchema"]["additionalProperties"])
        self.assertNotIn("required", cube["inputSchema"]["properties"]["label"])

    def test_a_tool_without_enabled_is_off(self):
        doc = {"addon": "demo_addon", "tools": [{"name": "demo_silent", "op": "demo.silent"}]}
        (self.dir / "silent.json").write_text(json.dumps(doc), encoding="utf-8")
        path = self.dir / "silent.json"
        _, (tool,) = server.load_manifest(path)
        self.assertIs(tool["enabled"], False)
        tools, _ = server.load_tools(self.dir)
        self.assertNotIn("demo_silent", tools)
        tools, _ = server.load_tools(self.dir, include_disabled=True)
        self.assertIn("demo_silent", tools)

    def test_what_a_manifest_may_not_say(self):
        bad = {
            "both": {"name": "x", "op": "a.b", "code": "pass"},
            "neither": {"name": "x"},
            "op shape": {"name": "x", "op": "import os"},
            "name": {"name": "Has Spaces", "op": "a.b"},
            "context": {"name": "x", "op": "a.b", "context": "TEXT_EDITOR"},
            "param type": {"name": "x", "op": "a.b", "params": {"p": {"type": "object"}}},
            "bad default": {"name": "x", "op": "a.b", "params": {"p": {"type": "integer", "default": "1"}}},
            "array items": {"name": "x", "op": "a.b", "params": {"p": {"type": "array"}}},
            "unknown key": {"name": "x", "op": "a.b", "colour": "red"},
            "code syntax": {"name": "x", "code": "def ("},
        }
        for label, tool in bad.items():
            with self.subTest(case=label):
                path = self.dir / "bad.json"
                path.write_text(json.dumps({"addon": "demo", "tools": [tool]}), encoding="utf-8")
                with self.assertRaises((server.Invalid, SyntaxError)):
                    server.load_manifest(path)
        (self.dir / "bad.json").unlink()

    def test_a_name_defined_twice_is_reported(self):
        (self.dir / "again.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
        tools, problems = server.load_tools(self.dir)
        self.assertIn("demo_make_cube", tools)
        self.assertTrue(any("defined twice" in p for p in problems))


class Calls(Case):
    def test_an_operator_call(self):
        fake = self.blender(lambda c: printed({"result": ["FINISHED"], "new_objects": ["cube"]}, "log line\n"))
        result = self.call("demo_make_cube", {"label": "cube", "size": 2, "offset": [1, 2, 3]})
        self.assertFalse(result["isError"], result)
        out = json.loads(result["content"][0]["text"])
        self.assertEqual(out["new_objects"], ["cube"])
        self.assertEqual(out["printed"], "log line")
        code = fake.received[0]["params"]["code"]
        self.assertEqual(fake.received[0]["type"], "execute_code")
        self.assertIn("bpy.ops.demo.make_cube('EXEC_DEFAULT', **_kwargs)", code)
        self.assertIn("temp_override(**area_override('VIEW_3D'))", code)
        self.assertIn("addon_enabled('demo_addon')", code)

    def test_arguments_travel_as_data(self):
        fake = self.blender()
        hostile = '"); import os; os.system("echo pwned"); ("'
        self.call("demo_make_cube", {"label": hostile})
        code = fake.received[0]["params"]["code"]
        tree = ast.parse(code)
        imported = {a.name for node in ast.walk(tree) if isinstance(node, ast.Import) for a in node.names}
        self.assertEqual(imported, {"json", "bpy", "addon_utils"})
        literal = next(node.value.args[0] for node in tree.body
                       if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ARGS")
        self.assertEqual(json.loads(ast.literal_eval(literal)),
                         {"label": hostile, "size": 1.0, "style": "PLAIN"})

    def test_bad_arguments_never_reach_blender(self):
        fake = self.blender()
        cases = {
            "type": {"label": "a", "size": "big"},
            "bool is not a number": {"label": "a", "size": True},
            "enum": {"label": "a", "style": "LOUD"},
            "minimum": {"label": "a", "size": 0},
            "array length": {"label": "a", "offset": [1, 2]},
            "array item": {"label": "a", "offset": [1, "2", 3]},
            "missing": {},
            "unknown": {"label": "a", "colour": "red"},
        }
        for label, arguments in cases.items():
            with self.subTest(case=label):
                result = self.call("demo_make_cube", arguments)
                self.assertTrue(result["isError"])
                self.assertTrue(result["content"][0]["text"].startswith("Error: "))
        self.assertEqual(fake.received, [])
        self.assertTrue(self.call("demo_hidden")["isError"], "a disabled tool cannot be called")
        self.assertEqual(fake.received, [])

    def test_a_code_tool_and_the_builtins_send_code_that_compiles(self):
        fake = self.blender()
        self.call("demo_count")
        self.call("addons_list")
        self.call("addon_inspect", {"module": "demo_addon"})
        self.call("library_list", {"library": "Poly Haven"})
        self.call("library_import", {"library": "Poly Haven", "file": "a/a.blend", "name": "a", "kind": "objects"})
        self.assertEqual(len(fake.received), 5)
        for command in fake.received:
            compile(command["params"]["code"], "sent", "exec")
        self.assertIn("report(count=len(bpy.data.objects))", fake.received[0]["params"]["code"])

    def test_a_failure_in_blender(self):
        detail = {"exception_type": "RuntimeError", "message": "the add-on `demo_addon` is not enabled",
                  "traceback": 'Traceback:\n  File "addon.py", line 9, in run\n  File "<string>", line 31, '
                               'in <module>\nRuntimeError: ...'}
        self.blender(lambda c: {"status": "error", "message": json.dumps(detail)})
        result = self.call("demo_count")
        self.assertTrue(result["isError"])
        self.assertEqual(result["content"][0]["text"],
                         "Error: RuntimeError: the add-on `demo_addon` is not enabled "
                         "(line 31, in <module> of the sent code)")

    def test_no_blender(self):
        free = socket.socket()
        free.bind(("127.0.0.1", 0))
        port = free.getsockname()[1]
        free.close()
        os.environ["BLENDER_PORT"] = str(port)
        result = self.call("demo_count")
        self.assertTrue(result["isError"])
        self.assertIn("Connect to MCP server", result["content"][0]["text"])


class Discover(Case):
    def test_a_draft_from_an_inspection(self):
        draft = server.draft_manifest(INSPECTED)
        self.assertEqual(draft["addon"], "bl_ext.user_default.demo_addon")
        (tool,) = draft["tools"]
        self.assertEqual(tool["name"], "demo_addon_make_cube")
        self.assertFalse(tool["enabled"])
        self.assertEqual(tool["context"], "VIEW_3D")
        params = tool["params"]
        self.assertEqual(params["size"], {"description": "Size", "type": "number", "minimum": 0.01, "default": 1.0})
        self.assertEqual(params["count"]["minimum"], 1)
        self.assertNotIn("maximum", params["count"])
        self.assertEqual(params["style"]["enum"], ["PLAIN", "FANCY"])
        self.assertEqual(params["layers"], {"description": "Layers", "type": "array", "items": {"type": "string", "enum": ["A", "B"]},
                                            "default": ["A"]})
        self.assertEqual(params["preset"]["type"], "string")
        self.assertEqual(params["offset"]["minItems"], 3)
        self.assertNotIn("target", params)
        self.assertNotIn("secret", params)
        path = self.dir / "draft.json"
        path.write_text(json.dumps(draft), encoding="utf-8")
        server.load_manifest(path)

    def test_discover_never_overwrites(self):
        out = self.dir / "drafts"
        self.blender(lambda c: printed(INSPECTED))
        for expected in ("demo_addon.json", "demo_addon.draft.json"):
            with self.subTest(file=expected), contextlib_quiet():
                self.assertEqual(server.main(["discover", "bl_ext.user_default.demo_addon", "--out", str(out)]), 0)
            self.assertTrue((out / expected).is_file())
        with contextlib_quiet():
            self.assertEqual(server.main(["discover", "bl_ext.user_default.demo_addon", "--out", str(out)]), 2)
        with contextlib_quiet():
            self.assertEqual(server.main(["discover", "not a module"]), 2)


class Stdio(Case):
    def test_the_handshake(self):
        lines = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "resources/list"},
        ]
        stdin = io.StringIO("\n".join(json.dumps(line) for line in lines) + "\nnot json\n")
        stdout = io.StringIO()
        server.serve(stdin, stdout, self.dir)
        replies = [json.loads(line) for line in stdout.getvalue().splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2, 3, None])
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2024-11-05")
        self.assertEqual(replies[0]["result"]["serverInfo"]["name"], "blender-addons")
        self.assertIn("tools", replies[1]["result"])
        self.assertEqual(replies[2]["error"]["code"], -32601)
        self.assertEqual(replies[3]["error"]["code"], -32700)


class AddonEnabled(unittest.TestCase):
    """The prelude's check, run against stand-ins for bpy and addon_utils."""

    def enabled(self, module, installed):
        import types
        bpy = types.SimpleNamespace(context=types.SimpleNamespace(
            preferences=types.SimpleNamespace(addons={name: None for name in installed})))
        addon_utils = types.SimpleNamespace(check=lambda name: (False, False))
        saved = {k: sys.modules.get(k) for k in ("bpy", "addon_utils")}
        sys.modules.update(bpy=bpy, addon_utils=addon_utils)
        try:
            scope = {}
            exec(server.PRELUDE.format(args="{}"), scope)
            return scope["addon_enabled"](module)
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v

    def test_an_extension_from_any_repository(self):
        self.assertTrue(self.enabled("bl_ext.blender_org.easy_pivot", ["bl_ext.user_default.easy_pivot"]))
        self.assertTrue(self.enabled("bl_ext.blender_org.easy_pivot", ["bl_ext.blender_org.easy_pivot"]))

    def test_only_the_same_extension(self):
        self.assertFalse(self.enabled("bl_ext.blender_org.easy_pivot", ["bl_ext.user_default.easy_tree"]))
        self.assertFalse(self.enabled("bl_ext.blender_org.easy_pivot", ["easy_pivot"]))
        self.assertFalse(self.enabled("legacy_addon", ["bl_ext.user_default.legacy_addon"]))


class contextlib_quiet:
    """Swallow what main() prints."""

    def __enter__(self):
        self.saved = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = io.StringIO()

    def __exit__(self, *exc):
        sys.stdout, sys.stderr = self.saved


if __name__ == "__main__":
    unittest.main()
