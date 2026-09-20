#!/usr/bin/env python3
"""Tests for validate-contract.py's agent tool rule and its Bash exception."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "validate-contract.py"
spec = importlib.util.spec_from_file_location("validate_contract", SCRIPT)
vc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vc)

BODY = ("Never pass `--persist`. You never write any file. "
        "Run only python ui-design/catalog/scripts/search.py.")
EXCEPTIONS = {"ui-design-search-part": ["Bash"]}


class TestAgentToolErrors(unittest.TestCase):
    def test_read_only_agent_passes(self):
        self.assertEqual(vc.agent_tool_errors("ui-design-page-reviewer", ["Read", "Grep", "Glob"], "", EXCEPTIONS), [])

    def test_bash_is_forbidden_without_an_exception(self):
        errors = vc.agent_tool_errors("ui-design-other", ["Read", "Bash"], BODY, EXCEPTIONS)
        self.assertTrue(any("Bash" in e for e in errors))

    def test_declared_agent_may_hold_bash_with_a_stated_boundary(self):
        self.assertEqual(vc.agent_tool_errors(
            "ui-design-search-part", ["Read", "Grep", "Glob", "Bash"], BODY, EXCEPTIONS), [])

    def test_bash_agent_without_the_boundary_in_its_body_fails(self):
        errors = vc.agent_tool_errors("ui-design-search-part", ["Read", "Bash"], "Search things.", EXCEPTIONS)
        self.assertEqual(len(errors), 1)
        self.assertIn("never pass `--persist`", errors[0])

    def test_the_exception_never_lifts_write_edit_agent_or_notebookedit(self):
        for tool in ("Write", "Edit", "Agent", "NotebookEdit"):
            errors = vc.agent_tool_errors("ui-design-search-part", ["Read", "Bash", tool], BODY, EXCEPTIONS)
            self.assertTrue(any(tool in e for e in errors), tool)

    def test_an_exception_for_a_non_bash_tool_grants_nothing(self):
        errors = vc.agent_tool_errors("ui-design-x", ["Write"], BODY, {"ui-design-x": ["Write"]})
        self.assertTrue(errors)


class TestExceptionDeclarations(unittest.TestCase):
    AGENTS = {"ui-design-search-part", "ui-design-page-reviewer"}

    def test_valid_block_passes(self):
        self.assertEqual(vc.exception_declaration_errors(EXCEPTIONS, self.AGENTS), [])

    def test_unknown_agent_fails(self):
        errors = vc.exception_declaration_errors({"ui-design-ghost": ["Bash"]}, self.AGENTS)
        self.assertTrue(any("not an existing" in e for e in errors))

    def test_only_bash_can_be_excepted(self):
        errors = vc.exception_declaration_errors({"ui-design-search-part": ["Write"]}, self.AGENTS)
        self.assertTrue(any("only" in e for e in errors))

    def test_empty_tool_list_and_wrong_shape_fail(self):
        self.assertTrue(vc.exception_declaration_errors({"ui-design-search-part": []}, self.AGENTS))
        self.assertTrue(vc.exception_declaration_errors(["Bash"], self.AGENTS))


class TestRealRepo(unittest.TestCase):
    def test_only_the_search_part_agent_holds_bash(self):
        yaml = vc.load_yaml()
        holders = []
        for path in vc.AGENTS_DIR.glob(f"{vc.OWNED_PREFIX}*.md"):
            errors = []
            tools = vc.parse_frontmatter(yaml, path, errors)["tools"]
            if "Bash" in [t.strip() for t in str(tools).split(",")]:
                holders.append(path.stem)
        self.assertEqual(holders, ["ui-design-search-part"])


if __name__ == "__main__":
    unittest.main()
