"""The add-on manifests load, name operators their add-on's source registers, and
make code that compiles. No Blender: the server's own loader and code builder."""

import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE.parent / "plugins" / "blender" / "addon-tools"))
import server  # noqa: E402

MANIFESTS = HERE / "manifests"
SOURCES = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))


def sample(spec):
    """A value of the declared type, for a required parameter."""
    if "enum" in spec:
        return spec["enum"][0]
    kind = spec["type"]
    if kind == "array":
        item = sample(spec["items"])
        return [item] * spec.get("minItems", 1)
    if kind in ("number", "integer"):
        low = spec.get("minimum", 0)
        return float(low) if kind == "number" else int(low)
    return {"boolean": True, "string": "/tmp/model.file"}[kind]


class Manifests(unittest.TestCase):
    def test_the_folder_loads_without_problems(self):
        tools, problems = server.load_tools(MANIFESTS, include_disabled=True)
        self.assertEqual(problems, [])
        self.assertTrue(tools)

    def test_each_manifest_matches_its_source(self):
        listed = {entry["manifest"]: (ident, entry) for ident, entry in SOURCES.items()}
        self.assertEqual(set(listed), {p.name for p in MANIFESTS.glob("*.json")})
        for path in sorted(MANIFESTS.glob("*.json")):
            ident, entry = listed[path.name]
            raw = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(manifest=path.name):
                self.assertEqual(raw["addon"], f"bl_ext.blender_org.{ident}")
                self.assertEqual(raw["seen_version"], entry["version"])
                self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(entry["license"])
                for tool in raw["tools"]:
                    self.assertIn(tool["op"], entry["operators"], tool["name"])

    def test_every_tool_builds_code_that_compiles(self):
        tools, _ = server.load_tools(MANIFESTS, include_disabled=True)
        for name, tool in tools.items():
            with self.subTest(tool=name):
                given = {k: sample(s) for k, s in tool["params"].items() if s.get("required")}
                code = server.tool_code(tool, server.validate_args(tool, given))
                compile(code, name, "exec")
                self.assertIn(f"bpy.ops.{tool['op']}('EXEC_DEFAULT'", code)

    def test_no_secret_shaped_value(self):
        for path in [*MANIFESTS.glob("*.json"), HERE / "sources.json"]:
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                self.assertNotRegex(text, r"(?i)\b(api[_-]?key|token|password|secret)\b\s*[\"']?\s*[:=]")
                self.assertNotRegex(text, r"(?i)https?://(?!extensions\.blender\.org/)")

    def test_a_file_parameter_is_required(self):
        tools, _ = server.load_tools(MANIFESTS, include_disabled=True)
        for name, tool in tools.items():
            if "filepath" in tool["params"]:
                with self.subTest(tool=name):
                    self.assertTrue(tool["params"]["filepath"].get("required"))

    def test_tool_names_are_short_and_plain(self):
        tools, _ = server.load_tools(MANIFESTS, include_disabled=True)
        for name in tools:
            self.assertRegex(name, server.TOOL_NAME)
            self.assertFalse(re.search(r"__", name), name)


if __name__ == "__main__":
    unittest.main()
