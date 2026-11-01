import csv
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
SCRIPTS = PLUGIN / "catalog" / "scripts"
DATA = PLUGIN / "catalog" / "data"
sys.path.insert(0, str(SCRIPTS))

import _build_data  # noqa: E402
import preflight  # noqa: E402
import search  # noqa: E402
import svg_lint  # noqa: E402


class Data(unittest.TestCase):
    def test_every_table_matches_its_generator(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = _build_data.DATA
            _build_data.DATA = Path(tmp)
            try:
                _build_data.write("print-specs.csv", ["ID", "Name", "Trim", "Bleed", "Safe margin", "Resolution", "Colour", "Keywords", "Notes"], _build_data.PRINT)
                fresh = (Path(tmp) / "print-specs.csv").read_bytes()
            finally:
                _build_data.DATA = original
        self.assertEqual(fresh, (DATA / "print-specs.csv").read_bytes(), "run catalog/scripts/_build_data.py and commit the CSVs")

    def test_tables_are_well_formed(self):
        for domain, (name, columns) in search.DOMAINS.items():
            with open(DATA / name, newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertGreaterEqual(len(rows), 10, name)
            ids = [r["ID"] for r in rows]
            self.assertEqual(len(ids), len(set(ids)), f"{name}: duplicate id")
            for row in rows:
                self.assertTrue(all(row[c] for c in columns[:2]), f"{name}: {row['ID']} has an empty key cell")
                self.assertNotIn(None, row, f"{name}: {row['ID']} has extra cells")

    def test_catalog_holds_no_link_or_local_path(self):
        for path in DATA.glob("*.csv"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"https?://", path.name)
            self.assertNotRegex(text, r"[A-Za-z]:\\|/Users/|/home/", path.name)


class Search(unittest.TestCase):
    def test_known_queries_find_the_right_row(self):
        self.assertEqual(search.rank("print", "business card")[0][1]["ID"][:13], "business-card")
        self.assertEqual(search.rank("social", "instagram story")[0][1]["ID"], "ig-story")
        self.assertEqual(search.rank("color", "hairline stroke")[0][1]["ID"], "hairline")
        self.assertEqual(search.rank("tool", "remove background")[0][1]["ID"], "bg-remove")

    def test_guessed_domain(self):
        self.assertEqual(search.guess_domain("instagram story"), "social")

    def test_exit_codes(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(search.main(["zzzzqqq", "--domain", "print"]), 1)
            self.assertEqual(search.main(["   ", "--domain", "print"]), 2)
            self.assertEqual(search.main(["poster", "--domain", "print"]), 0)


class Preflight(unittest.TestCase):
    def codes(self, spec, level=None):
        return {f["code"] for f in preflight.check(spec) if level in (None, f["level"])}

    def test_a_clean_layout_has_no_errors_or_warnings(self):
        spec = {"trim_mm": [210, 297], "bleed_mm": 3, "safe_mm": 5, "colour_mode": "CMYK", "total_ink_pct": 280,
                "min_text_pt": 8, "min_stroke_pt": 0.5, "fonts": [{"name": "A", "embedded": True}],
                "images": [{"name": "h.jpg", "px": [2480, 3508], "placed_mm": [210, 297]}], "pdf_standard": "PDF/X-4"}
        levels = {f["level"] for f in preflight.check(spec)}
        self.assertFalse(levels & {"error", "warn"})

    def test_each_rule_fires(self):
        spec = {"bleed_mm": 0, "safe_mm": 1, "colour_mode": "RGB", "total_ink_pct": 340, "min_text_pt": 4,
                "min_stroke_pt": 0.1, "fonts": [{"name": "X", "embedded": False}],
                "images": [{"name": "low.jpg", "px": [600, 400], "placed_mm": [210, 140]}], "pdf_standard": "PDF/A"}
        self.assertEqual(self.codes(spec, "error"), {"bleed", "hairline", "fonts", "image-resolution"})
        self.assertEqual(self.codes(spec, "warn"), {"safe-zone", "colour-mode", "ink-limit", "text-size", "pdf-standard"})

    def test_missing_keys_are_not_checked_not_passed(self):
        findings = preflight.check({})
        self.assertTrue(findings and all(f["level"] == "info" for f in findings))

    def test_image_resolution_is_measured_at_placed_size(self):
        low = {"images": [{"name": "a", "px": [1000, 1000], "placed_mm": [254, 254]}]}  # 100 ppi
        self.assertIn("image-resolution", self.codes(low, "error"))
        ok = {"images": [{"name": "a", "px": [3000, 3000], "placed_mm": [254, 254]}]}  # about 300 ppi
        self.assertNotIn("image-resolution", self.codes(ok))

    def test_large_format_accepts_lower_ppi(self):
        spec = {"target": "large-format", "images": [{"name": "a", "px": [1500, 1500], "placed_mm": [254, 254]}]}  # 150 ppi
        self.assertNotIn("image-resolution", self.codes(spec, "error"))

    def test_bad_target_is_an_input_error(self):
        with self.assertRaises(ValueError):
            preflight.check({"target": "web"})

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad, good = Path(tmp, "bad.json"), Path(tmp, "good.json")
            bad.write_text(json.dumps({"bleed_mm": 0}))
            good.write_text(json.dumps({"bleed_mm": 3}))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(preflight.main([str(bad)]), 1)
                self.assertEqual(preflight.main([str(good)]), 0)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(preflight.main([str(Path(tmp, "missing.json"))]), 2)


class SvgLint(unittest.TestCase):
    GOOD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><title>Mark</title><circle cx="32" cy="32" r="30" fill="currentColor"/></svg>'

    def codes(self, text, level=None):
        return {f["code"] for f in svg_lint.lint(text) if level in (None, f["level"])}

    def test_good_mark_has_no_errors_or_warnings(self):
        self.assertEqual({f["level"] for f in svg_lint.lint(self.GOOD)} & {"error", "warn"}, set())

    def test_errors(self):
        self.assertEqual(self.codes("<svg", "error"), {"xml"})
        self.assertEqual(self.codes("<html/>", "error"), {"root"})
        self.assertIn("viewbox", self.codes('<svg xmlns="http://www.w3.org/2000/svg"><title>t</title></svg>', "error"))
        self.assertIn("script", self.codes(self.GOOD.replace("<circle", "<script>1</script><circle"), "error"))
        self.assertIn("external", self.codes(self.GOOD.replace("<circle", '<use href="https://example.com/a.svg#x"/><circle'), "error"))

    def test_warnings(self):
        self.assertIn("text", self.codes(self.GOOD.replace("<circle", "<text>Hi</text><circle"), "warn"))
        self.assertIn("raster", self.codes(self.GOOD.replace("<circle", '<image href="data:image/png;base64,AAAA"/><circle'), "warn"))
        self.assertIn("hairline", self.codes(self.GOOD.replace("<circle", '<path d="M0 0L5 5" stroke="#000" stroke-width="0.05"/><circle'), "warn"))

    def test_internal_reference_is_allowed(self):
        self.assertNotIn("external", self.codes(self.GOOD.replace("<circle", '<use href="#c"/><circle')))

    def test_size_warning(self):
        self.assertIn("size", {f["code"] for f in svg_lint.lint(self.GOOD, max_bytes=10)})


class Render(unittest.TestCase):
    def run_render(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "render.py"), *args], capture_output=True, text=True)

    def test_bad_usage_is_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.run_render(str(Path(tmp, "nope.html")), str(Path(tmp, "o.png"))).returncode, 2)
            Path(tmp, "a.html").write_text("<p>hi</p>")
            self.assertEqual(self.run_render(str(Path(tmp, "a.html")), str(Path(tmp, "o.gif"))).returncode, 2)


class SelfContained(unittest.TestCase):
    def test_nothing_names_the_repo_or_dot_claude(self):
        for path in PLUGIN.rglob("*"):
            if path.suffix not in (".md", ".py", ".json", ".csv") or "tests" in path.parts or path.name in ("plugin.json", "README.md"):  # the README must say where to install from
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\.claude/|Pipelines-Plugin|\bROSW\b|\bstudio/", str(path.relative_to(PLUGIN)))

    def test_skills_and_agents_have_the_required_frontmatter(self):
        for path in list((PLUGIN / "skills").glob("*/SKILL.md")) + list((PLUGIN / "agents").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            front = text.split("---", 2)[1]
            self.assertIn("name:", front, path.name)
            description = re.search(r"^description:\s*(.+)$", front, re.M).group(1)
            self.assertLess(len(description), 1024, path.name)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", front, path.name)
            if path.parent.name == "agents":
                self.assertRegex(front, r"(?m)^model:\s*\S+", path.name)
                self.assertNotIn("Bash", front, path.name)
            else:
                self.assertNotRegex(front, r"allowed-tools:.*\b(Write|Edit)\b", path.name)

    def test_skills_name_only_scripts_that_exist(self):
        for path in (PLUGIN / "skills").glob("*/SKILL.md"):
            for script in re.findall(r"catalog/scripts/(\w+\.py)", path.read_text(encoding="utf-8")):
                self.assertTrue((SCRIPTS / script).is_file(), f"{path.parent.name}: {script}")


if __name__ == "__main__":
    unittest.main()
