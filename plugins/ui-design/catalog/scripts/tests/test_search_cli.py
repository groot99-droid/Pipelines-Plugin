#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for search.py's --diagnostics flag (stdlib unittest)."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
SEARCH = SCRIPTS_DIR / "search.py"
LEDGERLY = "freelancer invoicing SaaS fintech trustworthy"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SEARCH), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )


class TestDiagnosticsFlag(unittest.TestCase):
    def test_text_output_gains_one_diagnostics_line(self):
        done = run(LEDGERLY, "--domain", "product", "-n", "1", "--diagnostics")
        self.assertEqual(done.returncode, 0, done.stderr)
        line = next(l for l in done.stdout.splitlines() if l.startswith("**Diagnostics:**"))
        for field in ("top_score=", "margin=", "token_coverage=", "reason="):
            self.assertIn(field, line)

    def test_stack_search_also_reports_diagnostics(self):
        done = run("virtualized list", "--stack", "react-native", "-n", "1", "--diagnostics")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("**Diagnostics:**", done.stdout)

    def test_json_carries_the_diagnostics_object(self):
        done = run(LEDGERLY, "--domain", "product", "--diagnostics", "--json")
        payload = json.loads(done.stdout)
        for field in ("top_score", "margin", "token_coverage", "reason"):
            self.assertIn(field, payload["diagnostics"])

    def test_output_without_the_flag_is_unchanged(self):
        plain = run("keyboard focus modal", "--domain", "ux")
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertNotIn("Diagnostics", plain.stdout)
        self.assertNotIn("diagnostics", json.loads(
            run("keyboard focus modal", "--domain", "ux", "--json").stdout))

    def test_flag_is_ignored_by_design_system(self):
        done = run("beauty spa wellness service", "--design-system", "--diagnostics")
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == "__main__":
    unittest.main()
