#!/usr/bin/env python3
"""Tests for validate-contract.py's portability rule.

A skill or agent that names a monorepo path works in the Pipelines repo and breaks
the moment the plugin is installed, because none of those paths exist there. These
pin what the rule catches, and that the current plugin passes it.
"""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "validate-contract.py"
spec = importlib.util.spec_from_file_location("validate_contract", SCRIPT)
vc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vc)


class TestPortability(unittest.TestCase):
    def test_a_plugin_root_path_is_portable(self):
        text = 'Run python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "q" --domain ux.'
        self.assertEqual(vc.portability_errors("skill", text), [])

    def test_a_monorepo_path_is_not(self):
        problems = vc.portability_errors("skill", "Run python ui-design/catalog/scripts/search.py")
        self.assertEqual(len(problems), 1)
        self.assertIn("ui-design/", problems[0])

    def test_a_dot_claude_path_is_not(self):
        self.assertTrue(vc.portability_errors("skill", "see .claude/agents/x.md"))

    def test_naming_the_pipelines_repo_or_its_root_is_not(self):
        self.assertTrue(vc.portability_errors("skill", "relative to the Pipelines root"))
        self.assertTrue(vc.portability_errors("skill", "the ROSW repo holds the vault"))
        self.assertEqual(vc.portability_errors("skill", "CROSWALK is one word, not a name"), [])
        self.assertTrue(vc.portability_errors("skill", "run it from the repo root"))
        self.assertTrue(vc.portability_errors("skill", "run it from the repo-root"))

    def test_the_skill_and_agent_names_themselves_are_portable(self):
        text = "Use ui-design-catalog and the ui-design:ui-design-search-part agent."
        self.assertEqual(vc.portability_errors("skill", text), [])

    def test_the_line_number_is_reported(self):
        text = "\n".join(["fine", "fine", "see ui-design/INDEX.md", ""])
        problems = vc.portability_errors("skill", text)
        self.assertIn("skill:3:", problems[0])

    def test_plugin_root_references_are_extracted_with_their_relative_path(self):
        found = vc.PATH_REFERENCE.findall("Read ${CLAUDE_PLUGIN_ROOT}/references/quick-reference.md now")
        self.assertEqual(found, ["references/quick-reference.md"])

    def test_a_variable_in_frontmatter_is_reported(self):
        errors = []
        vc.check_frontmatter_portable(vc.TOOL_ROOT / "skills" / "x" / "SKILL.md",
                                      {"name": "x", "description": "see ${CLAUDE_PLUGIN_ROOT}/a"}, errors)
        self.assertEqual(len(errors), 1)
        self.assertIn("frontmatter 'description'", errors[0])

    def test_the_real_skills_agents_and_docs_are_portable(self):
        errors = []
        for path in [*(vc.SKILLS_DIR.glob("*/SKILL.md")), *(vc.AGENTS_DIR.glob("*.md")),
                     vc.TOOL_ROOT / "ROUTER.md", *(vc.TOOL_ROOT / "references").glob("*.md")]:
            vc.check_portable(path, errors)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
