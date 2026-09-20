#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for merge_parts.py, the multipart fan-out merger (stdlib unittest)."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import merge_parts

MANIFEST = [
    {"part_id": "ux-a11y", "kind": "domain", "target": "ux", "query": "keyboard focus", "n": 3},
    {"part_id": "ux-forms", "kind": "domain", "target": "ux", "query": "form validation", "n": 3},
]


def search_block(part_id, query, verdict="match", rows=("row one",), retried="no"):
    lines = [f"PART: {part_id}", f"QUERY: {query}", f"RETRIED: {retried}", f"VERDICT: {verdict}", "ROWS:"]
    lines += [f"- {r}" for r in rows] or ["(none)"]
    return "\n".join(lines)


GOOD = "\n\n".join([search_block("ux-a11y", "keyboard focus"),
                    search_block("ux-forms", "form validation")])


class TestSearchMerge(unittest.TestCase):
    def test_complete_run_passes(self):
        merged = merge_parts.merge_search(MANIFEST, GOOD)
        self.assertEqual(merged["errors"], [])
        self.assertEqual((merged["expected"], merged["returned"]), (2, 2))
        self.assertEqual(merged["verdicts"]["match"], 2)

    def test_missing_part_fails(self):
        merged = merge_parts.merge_search(MANIFEST, search_block("ux-a11y", "keyboard focus"))
        self.assertTrue(any("ux-forms" in e and "missing" in e for e in merged["errors"]))

    def test_duplicate_and_unknown_parts_fail(self):
        text = GOOD + "\n\n" + search_block("ux-a11y", "keyboard focus") + "\n\n" + \
            search_block("ux-bogus", "x")
        errors = merge_parts.merge_search(MANIFEST, text)["errors"]
        self.assertTrue(any("more than once" in e for e in errors))
        self.assertTrue(any("unknown part" in e for e in errors))

    def test_changed_query_needs_a_declared_retry(self):
        bad = search_block("ux-a11y", "something else") + "\n\n" + search_block("ux-forms", "form validation")
        self.assertTrue(merge_parts.merge_search(MANIFEST, bad)["errors"])
        ok = search_block("ux-a11y", "something else", retried="yes") + "\n\n" + \
            search_block("ux-forms", "form validation")
        self.assertEqual(merge_parts.merge_search(MANIFEST, ok)["errors"], [])

    def test_match_without_rows_fails(self):
        text = search_block("ux-a11y", "keyboard focus", rows=()) + "\n\n" + \
            search_block("ux-forms", "form validation")
        self.assertTrue(any("ROWS is empty" in e for e in merge_parts.merge_search(MANIFEST, text)["errors"]))

    def test_empty_and_low_confidence_are_warnings_not_errors(self):
        text = search_block("ux-a11y", "keyboard focus", verdict="empty", rows=()) + "\n\n" + \
            search_block("ux-forms", "form validation", verdict="low-confidence")
        merged = merge_parts.merge_search(MANIFEST, text)
        self.assertEqual(merged["errors"], [])
        self.assertEqual(len(merged["warnings"]), 2)

    def test_code_fences_and_prose_are_ignored(self):
        merged = merge_parts.merge_search(MANIFEST, "Here you go:\n```\n" + GOOD + "\n```\n")
        self.assertEqual(merged["errors"], [])


REVIEW_AREAS = {a: s for a, s in merge_parts.AREA_SECTIONS.items()}
RULES = merge_parts.load_rule_ids()


def review_block(area, findings=("(none)",), not_checked="nothing"):
    return "\n".join([f"AREA: {area}", "FINDINGS:", *findings, f"NOT-CHECKED: {not_checked}"])


class TestReviewMerge(unittest.TestCase):
    def all_areas(self, **overrides):
        blocks = []
        for area in merge_parts.AREA_SECTIONS:
            blocks.append(overrides.get(area) or review_block(area))
        return "\n\n".join(blocks)

    def test_rule_ids_load_from_quick_reference(self):
        self.assertIn("color-contrast", RULES)
        self.assertEqual(RULES["color-contrast"], 1)
        self.assertGreater(len(RULES), 200)

    def test_clean_review_passes(self):
        merged = merge_parts.merge_review(REVIEW_AREAS, self.all_areas(), RULES)
        self.assertEqual(merged["errors"], [])
        self.assertEqual(merged["findings"], [])

    def test_fabricated_rule_id_is_rejected(self):
        block = review_block("a11y+touch", ["- totally-made-up-rule | high | line 3 | fix it"])
        merged = merge_parts.merge_review(REVIEW_AREAS, self.all_areas(**{"a11y+touch": block}), RULES)
        self.assertTrue(any("totally-made-up-rule" in e for e in merged["errors"]))
        self.assertEqual(merged["findings"], [])

    def test_real_finding_is_kept_and_sorted_by_severity(self):
        a11y = review_block("a11y+touch", ["- color-contrast | low | line 9: #999 | darken",
                                           "- alt-text | critical | line 4: <img> | add alt"])
        merged = merge_parts.merge_review(REVIEW_AREAS, self.all_areas(**{"a11y+touch": a11y}), RULES)
        self.assertEqual(merged["errors"], [])
        self.assertEqual([f["rule_id"] for f in merged["findings"]], ["alt-text", "color-contrast"])

    def test_out_of_area_rule_is_a_warning(self):
        block = review_block("layout", ["- color-contrast | high | line 2 | x"])
        merged = merge_parts.merge_review(REVIEW_AREAS, self.all_areas(layout=block), RULES)
        self.assertEqual(merged["errors"], [])
        self.assertTrue(any("outside this area" in w for w in merged["warnings"]))

    def test_missing_area_and_bad_severity_fail(self):
        text = review_block("layout", ["- mobile-first | urgent | line 1 | x"])
        errors = merge_parts.merge_review(REVIEW_AREAS, text, RULES)["errors"]
        self.assertTrue(any("severity" in e for e in errors))
        self.assertTrue(any("'motion' is missing" in e for e in errors))

    def test_missing_findings_key_fails(self):
        text = "AREA: layout\nNOT-CHECKED: x"
        errors = merge_parts.merge_review({"layout": (5,)}, text, RULES)["errors"]
        self.assertTrue(any("FINDINGS is missing" in e for e in errors))


class TestCli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "merge_parts.py"), *args],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
            check=False)

    def test_exit_codes_follow_the_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp, "m.json")
            manifest.write_text(json.dumps({"manifest": MANIFEST}), encoding="utf-8")
            good, bad = Path(tmp, "good.txt"), Path(tmp, "bad.txt")
            good.write_text(GOOD, encoding="utf-8")
            bad.write_text(search_block("ux-a11y", "keyboard focus"), encoding="utf-8")
            self.assertEqual(self.run_cli("--mode", "search", "--manifest", str(manifest),
                                          "--results", str(good)).returncode, 0)
            failed = self.run_cli("--mode", "search", "--manifest", str(manifest), "--results", str(bad))
            self.assertEqual(failed.returncode, 1)
            self.assertIn("RESULT: FAIL", failed.stdout)


if __name__ == "__main__":
    unittest.main()
