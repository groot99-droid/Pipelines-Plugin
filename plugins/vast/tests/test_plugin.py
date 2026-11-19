"""The plugin's files agree with each other and name nothing outside the plugin."""

import json
import re
import sys
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN / "server"))

import server  # noqa: E402


class PluginTests(unittest.TestCase):
    def test_skill_names_every_tool_and_no_other(self):
        text = (PLUGIN / "skills" / "vast-gpu" / "SKILL.md").read_text(encoding="utf-8")
        listed = re.search(r"Its tools are (.+?)\.\n", text, re.S).group(1)
        named = set(re.findall(r"`([a-z_]+)`", listed))
        self.assertEqual(named, set(server.TOOLS))

    def test_names_nothing_outside_the_plugin(self):
        for path in PLUGIN.rglob("*"):
            if path.is_dir() or "__pycache__" in path.parts or path.name in ("README.md", "LICENSE", "plugin.json", "test_plugin.py"):
                continue
            if path.suffix not in (".py", ".md", ".json"):
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\.claude/|Pipelines-Plugin|\bROSW\b|\brosw\b|\bstudio/",
                                str(path.relative_to(PLUGIN)))

    def test_manifests(self):
        manifest = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "vast")
        self.assertEqual(manifest["version"], server.SERVER_VERSION)
        changelog = (PLUGIN / "CHANGELOG.md").read_text()
        self.assertIn("## " + manifest["version"], changelog)
        mcp = json.loads((PLUGIN / ".mcp.json").read_text())
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/server/server.py", mcp["mcpServers"]["vast"]["args"])

    def test_skill_paths_start_from_plugin_root(self):
        text = (PLUGIN / "skills" / "vast-gpu" / "SKILL.md").read_text(encoding="utf-8")
        front = text.split("---")[1]
        self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", front)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", text)


if __name__ == "__main__":
    unittest.main()
