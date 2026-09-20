#!/usr/bin/env python3
"""Tests for generate-index.py: the indexes are current, complete and gated."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

MAINTENANCE = Path(__file__).resolve().parents[1]
REPO_ROOT = MAINTENANCE.parents[1]
SCRIPT = MAINTENANCE / "generate-index.py"

spec = importlib.util.spec_from_file_location("generate_index", SCRIPT)
gi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gi)


def run_check():
    return subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=REPO_ROOT,
                          capture_output=True, text=True, encoding="utf-8", check=False)


class TestGenerateIndex(unittest.TestCase):
    def test_committed_indexes_are_current(self):
        done = run_check()
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_every_skill_and_agent_is_in_the_root_index(self):
        text = gi.build_root_index()
        skills, agents = gi.collect_entries()
        self.assertGreaterEqual(len(skills), 4)
        self.assertEqual(gi.missing_from_root(text), [])
        for fm, _ in skills + agents:
            self.assertIn(f"[{fm['name']}]", text)

    def test_a_dropped_entry_is_reported_by_name(self):
        text = gi.build_root_index().replace("[ui-design-catalog-reviewer]", "[dropped]")
        self.assertEqual(gi.missing_from_root(text), ["ui-design-catalog-reviewer"])

    def test_vocabulary_contains_the_row_the_router_needs(self):
        text = gi.build_tool_index()
        self.assertIn("Invoice & Billing Tool", text)
        self.assertIn("minimalism-and-swiss-style", text)

    def test_first_sentence_stops_at_the_period(self):
        self.assertEqual(gi.first_sentence("Does a thing. Use when x."), "Does a thing.")
        self.assertEqual(gi.first_sentence("No period here"), "No period here")

    def test_generation_is_deterministic(self):
        self.assertEqual(gi.build_tool_index(), gi.build_tool_index())


if __name__ == "__main__":
    unittest.main()
