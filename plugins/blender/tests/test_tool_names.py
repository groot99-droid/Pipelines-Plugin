"""Every MCP for Blender tool the plugin's documents name exists in the server.

SERVER_TOOLS is the list `server.py` of mcp-for-blender registers for the model in
the version below. When the version the docs describe changes, read that
version's `server.py` (every `@mcp.tool` that is not app-only) and update both."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = "2.2.6"
SERVER_TOOLS = {
    "get_addon_status", "disable_telemetry", "get_scene_info", "execute_blender_code",
    "record_trajectory_feedback", "look", "generate_3d", "search_assets", "import_asset",
}
# Tools the server registers for the host UI only; documents may name them, Claude never calls them.
APP_ONLY = {"open_viewport", "viewport_latest", "viewport_capture", "viewport_pick", "search_mentions"}
# Names from older releases that must not come back.
GONE = {"get_object_info", "get_viewport_screenshot", "describe_node_type", "bpy_api_lookup", "export_scene",
        "get_polyhaven_status", "search_polyhaven_assets", "download_polyhaven_asset", "set_texture",
        "search_sketchfab_models", "download_sketchfab_model", "download_polypizza_model",
        "generate_hyper3d_model_via_text", "poll_rodin_job_status", "import_generated_asset",
        "generate_hunyuan3d_model"}


def documents():
    yield from (ROOT / "skills").rglob("*.md")
    yield from (ROOT / "agents").glob("*.md")
    yield ROOT / "README.md"


class ToolNames(unittest.TestCase):
    def test_prefixed_names_exist(self):
        for path in documents():
            for name in re.findall(r"mcp__blender__(\w+)", path.read_text(encoding="utf-8")):
                with self.subTest(file=path.name, tool=name):
                    self.assertIn(name, SERVER_TOOLS)

    def test_no_name_from_an_older_release(self):
        for path in documents():
            text = path.read_text(encoding="utf-8")
            for name in GONE:
                with self.subTest(file=path.name, tool=name):
                    self.assertNotRegex(text, rf"(?<![.\w]){name}\b")

    def test_the_tool_table_lists_every_tool(self):
        table = (ROOT / "skills" / "blender-mcp" / "references" / "tools.md").read_text(encoding="utf-8")
        self.assertIn(VERSION, table)
        rows = set(re.findall(r"^\| (\w+) \|", table, re.M)) - {"Tool"}
        self.assertEqual(rows, SERVER_TOOLS)
        for name in APP_ONLY:
            self.assertIn(name, table)

    def test_the_reviewer_only_reads(self):
        agent = (ROOT / "agents" / "blender-scene-reviewer.md").read_text(encoding="utf-8")
        tools = re.search(r"^tools: (.*)$", agent, re.M).group(1)
        self.assertNotIn("execute_blender_code", tools)
        self.assertNotIn("import_asset", tools)

    def test_both_servers_are_registered(self):
        config = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
        self.assertEqual(config["blender"]["env"]["DISABLE_TELEMETRY"], "true")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/addon-tools/server.py", config["blender-addons"]["args"])


if __name__ == "__main__":
    unittest.main()
