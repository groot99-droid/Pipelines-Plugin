"""pipeline/notes.py: the notes writer (docs/CONTRACTS.md F7, F11 and F12).

Every test builds a small synthetic catalog in a temporary folder (a builder
below writes the files `ingest.py build` would, so odd names and every folder of
F7 can be had on demand), or builds one for real from the fixtures library with
`ingest.py build`. None reads the real library, catalog or vault. One class
reads vault/CLAUDE.md, which is an authored document and a code asset like
spec.yaml, to keep its glossary equal to schema/facets.json.

    python -m unittest discover -s brushes/pipeline/tests -p "test_notes.py"
"""

import contextlib
import copy
import io
import json
import os
import random
import re
import subprocess
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import brush_common as bc  # noqa: E402
import fixtures  # noqa: E402
import ingest  # noqa: E402
import notes  # noqa: E402

try:
    import yaml
except ImportError:  # the tests that parse YAML skip
    yaml = None

BRUSHES = PIPELINE.parent
SCRIPT = PIPELINE / "notes.py"
ID_LINE = re.compile(r"^- id: `(b_[0-9a-f]{12})`")
FRONT_KEYS = ["title", "type", "set_name", "set_slug", "set_id", "library", "pack", "pack_kind", "vendor",
              "redistribute", "brush_count", "eras", "kinds", "template", "generated_fingerprint", "tags"]
LINE_PREFIXES = ["id", "kind", "shape", "grain", "size", "pressure", "tilt", "speed", "taper", "render",
                 "facets", "preview"]

DEFAULT_FACETS = {
    "kind": "stroke", "is_stamp": False, "spacing": 0.026, "spacing_class": "tight",
    "shape_source": "embedded", "uses_bundled_shape": False, "grain_source": "blank", "has_grain": False,
    "uses_bundled_grain": True, "grain_movement": "rolling", "grain_application_code": None,
    "wet_mix": False, "render_code": "render-type-0", "taper": "both", "taper_start": True,
    "taper_end": True, "pressure_size": 1.0, "pressure_size_class": "high", "pressure_opacity": 0.0,
    "pressure_opacity_class": "none", "tilt": False, "speed": True, "size_min": 0.003, "size_max": 0.198,
    "size_class": "fine", "opacity_min": 0.01, "opacity_max": 1.0, "translucent": False, "dual": False,
    "dual_blend_code": None, "blend_code": 0, "blend_extended_code": None, "scatter": True,
    "shape_rotation": True, "randomised": True, "azimuth": False, "jitter_size": False,
    "jitter_opacity": False, "jitter_position": False, "streamline": False, "color_dynamics": False,
    "wet_edges": False, "burnt_edges": False, "era": "E3", "family": "legacy", "stroke_source": "thumbnail",
    "shape_coverage": None, "shape_aspect": None, "shape_midtone": None, "shape_edge_touch": None,
    "grain_mean": None, "grain_contrast": None,
}
DEFAULT_SETTINGS = {
    "plotSpacing": 0.026, "minSize": 0.003, "maxSize": 0.198, "minOpacity": 0.01, "maxOpacity": 1.0,
    "shapeScatter": 0.18, "shapeRotation": 1.0, "shapeRandomise": True, "shapeAzimuth": False,
    "textureScale": 16.0, "textureMovement": 1.0, "textureZoom": 1.0, "dynamicsTiltSize": 0.0,
    "dynamicsTiltOpacity": 0.0, "dynamicsSpeedSize": 0.63, "dynamicsSpeedOpacity": 0.0,
    "pencilTaperStartLength": 0.11, "pencilTaperEndLength": 0.11, "taperStartLength": 0.21,
    "taperEndLength": 0.24, "dynamicsGlazedFlow": 0.91, "blendMode": 0,
}


class Builder:
    """Writes a catalog/ folder in the shape of F5, from a few calls."""

    def __init__(self, root):
        self.root = Path(root)
        self.packs, self.sets, self.brushes, self.textures, self.containers = {}, [], {}, {}, {}
        self.order = []
        self.pack("demo-pack")

    def pack(self, pack_id, *, kind="vendor", vendor="Demo Vendor", redistribute="unknown",
             licence="none in pack; store terms apply", library="user", publish_previews=True):
        self.packs[pack_id] = {"id": pack_id, "kind": kind, "library": library, "vendor": vendor,
                               "product": pack_id.title(), "redistribute": redistribute,
                               "licence_note": licence, "publish_previews": publish_previews,
                               "source_url": None, "evidence": None, "counts": {}}

    def brush(self, name, *, era="E3", settings=None, facets=None, words=None, shape=None, grain=None,
              preview=None, extra=None, key_count=88):
        number = len(self.brushes) + 1
        brush_id = f"b_{number:012x}"
        display = name.strip() or "Untitled"
        merged_settings = dict(DEFAULT_SETTINGS)
        merged_settings.update(settings or {})
        merged_facets = dict(DEFAULT_FACETS, era=era)
        merged_facets.update(facets or {})
        shape_record = {"source": "embedded", "bundled_name": None, "texture_id": f"t_{number:012x}",
                        "inverted": True}
        shape_record.update(shape or {})
        grain_record = {"source": "blank", "bundled_name": "Brush-Preset-Blank.png", "texture_id": None,
                        "inverted": False}
        grain_record.update(grain or {})
        preview_record = {"stroke": None, "stroke_source": "thumbnail", "shape": None,
                          "shape_source": shape_record["source"], "grain": None,
                          "grain_source": grain_record["source"]}
        preview_record.update(preview or {})
        record = {
            "schema": "rosw-brushes-brush/1", "id": brush_id, "content_sha256": f"{number:064x}",
            "name": name, "display_name": display, "slug": "x", "library": "user", "pack": "demo-pack",
            "family": "legacy", "era": era,
            "format": {"key_count": key_count, "version": 2, "ref_size": 1, "archive_bytes": 100,
                       "archive_sha256": "0" * 64, "classes": []},
            "home": None, "occurrences": [], "shape": shape_record, "grain": grain_record,
            "thumbnail": {"present": True}, "secondary": None, "reset": None,
            "author": {"name": None, "has_picture": False, "has_signature": False, "creation_date": None},
            "settings": merged_settings, "facets": merged_facets,
            "facet_words": words if words is not None else ["stroke", "spacing-tight", f"era-{era.lower()}"],
            "preview": preview_record, "warnings": [],
        }
        record.update(extra or {})
        self.brushes[brush_id] = record
        if shape_record["texture_id"]:
            self.textures[shape_record["texture_id"]] = {"width": 64, "height": 32, "sha256": "0" * 64}
        return brush_id

    def set(self, slug, members, *, name=None, title=None, pack="demo-pack", library=None, kind="set",
            note="auto", container="user/demo-pack/Demo_Set.brushset"):
        pack_row = self.packs[pack]
        library = library or pack_row["library"]
        row = {"set_slug": slug, "set_id": "s_" + f"{len(self.sets) + 1:012x}",
               "name": slug if name is None else name, "title": title if title is not None else (name or slug),
               "kind": kind, "library": library, "pack": pack, "pack_kind": pack_row["kind"],
               "brush_count": len(members), "note": None, "brushes": list(members),
               "_note": note, "_container": container}
        self.sets.append(row)
        return row

    def build(self):
        for brush_id, record in self.brushes.items():
            places = [(row, index) for row in self.sets for index, member in enumerate(row["brushes"], 1)
                      if member == brush_id]
            places.sort(key=lambda p: (p[0]["kind"] == "loose", p[0]["pack"], p[0]["set_slug"], p[1]))
            home_row, position = places[0] if places else (None, None)
            if home_row is not None:
                record["home"] = {"set_slug": home_row["set_slug"], "position": position}
                record["pack"] = home_row["pack"]
                record["library"] = home_row["library"]
            record["occurrences"] = [
                {"set_slug": row["set_slug"], "set_id": row["set_id"], "position": index, "pack": row["pack"],
                 "container": row["_container"], "container_sha256": f"{abs(hash(row['_container'])) % 10**8:064x}",
                 "entry_prefix": ""} for row, index in places]
        homed = {record["home"]["set_slug"] for record in self.brushes.values() if record["home"]}
        rows = []
        for row in self.sets:
            row = dict(row)
            note = row.pop("_note")
            row.pop("_container")
            if note == "auto":
                if row["set_slug"] in homed:
                    folder = ("01_Procreate_Defaults" if row["library"] == "official"
                              else "04_My_Brushes" if row["pack_kind"] == "mine"
                              else "03_Loose" if row["kind"] == "loose" else "02_Vendor_Packs")
                    note = f"{folder}/{row['set_slug']}.md"
                else:
                    note = None
            row["note"] = note
            rows.append(row)
        for row in self.sets:
            row["brush_count"] = len(row["brushes"])
        catalog = self.root / "catalog"
        (catalog / "brushes").mkdir(parents=True, exist_ok=True)
        (catalog / "sets").mkdir(parents=True, exist_ok=True)
        for brush_id, record in self.brushes.items():
            self._write(catalog / "brushes" / f"{brush_id}.json", record)
        for row in rows:
            self._write(catalog / "sets" / f"{row['set_slug']}.json", row)
        brush_rows = [{"id": i, "name": r["name"], "display_name": r["display_name"],
                       "home_set": (r["home"] or {}).get("set_slug"), "era": r["era"],
                       "facet_words": r["facet_words"]} for i, r in self.brushes.items()]
        catalog_json = {
            "schema": "rosw-brushes-catalog/1", "ingest_version": 1, "facet_rules_version": 1,
            "library_fingerprint": "sha256:16:0123456789abcdef",
            "counts": {"brushes": len(self.brushes), "occurrences": sum(len(r["occurrences"]) for r in self.brushes.values()),
                       "sets": len(rows), "notes": sum(1 for r in rows if r["note"]), "packs": len(self.packs),
                       "textures": len(self.textures), "by_library": {"user": len(self.brushes), "official": 0}},
            "packs": list(self.packs.values()), "sets": rows, "brushes": brush_rows}
        self._write(catalog / "catalog.json", catalog_json)
        self._write(catalog / "textures.json", self.textures)
        containers = {}
        for record in self.brushes.values():
            for occurrence in record["occurrences"]:
                containers[occurrence["container_sha256"]] = {"bytes": 517781, "paths": [occurrence["container"]]}
        self._write(catalog / "containers.json", containers)
        return catalog_json

    @staticmethod
    def _write(path, value):
        bc.write_json(path, value)


class NotesCase(fixtures.BrushCase):
    def setUp(self):
        super().setUp()
        self.root = self.tmp / "brushes"
        self.root.mkdir()
        self.vault = self.root / "vault"
        self.cat = Builder(self.root)

    def run_notes(self, *argv, root=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = notes.main([*argv, "--root", str(root or self.root)])
        return code, out.getvalue(), err.getvalue()

    def write(self, *flags):
        code, out, err = self.run_notes("write", "--confirm", *flags)
        return code, out, err

    def note(self, rel):
        return (self.vault / rel).read_bytes().decode("utf-8")

    def two_sets(self):
        """A vendor set of three and a loose set repeating one of them plus one of its own."""
        a = self.cat.brush("Inker")
        b = self.cat.brush("Pencil", era="E4", key_count=101, facets={"kind": "stamp"},
                           grain={"source": "bundled", "bundled_name": "Brush-Preset-Stained-Paper-1.jpg"},
                           shape={"source": "bundled", "bundled_name": "Brush-Preset-Hard.png", "texture_id": None})
        c = self.cat.brush("Marker")
        d = self.cat.brush("Loose One", settings={"dynamicsTiltSize": 1.0, "dynamicsTiltOpacity": 0.8},
                           facets={"tilt": True})
        self.cat.set("demo-set", [a, b, c], name="Demo Set ", title="Demo Set")
        self.cat.set("demo-pack-loose", [a, d], name="demo-pack-loose", title="Demo Pack (loose brushes)",
                     kind="loose", container="user/demo-pack/Loose.brush")
        self.cat.build()
        return a, b, c, d

    def sections(self, text):
        """{heading: [lines]} for every H2 of a note."""
        out, current = {}, None
        for line in text.split("\n"):
            if line.startswith("## "):
                current = line[3:]
                out[current] = []
            elif current is not None:
                out[current].append(line)
        return out

    def hand_edit(self, rel, old, new):
        path = self.vault / rel
        text = path.read_bytes().decode("utf-8")
        self.assertIn(old, text)
        path.write_bytes(text.replace(old, new, 1).encode("utf-8"))


# ── the command line ─────────────────────────────────────────────────────────

class CommandLine(NotesCase):
    def test_the_parser_is_f11(self):
        parser = notes.build_parser()
        verbs = next(action for action in parser._actions if isinstance(action.choices, dict))
        self.assertEqual(list(verbs.choices), ["write", "check"])
        flags = lambda p: {s for a in p._actions for s in a.option_strings if s.startswith("--")} - {"--help"}
        roots = {"--root", "--catalog", "--vault"}
        self.assertEqual(flags(verbs.choices["write"]), roots | {"--only", "--diff", "--overwrite-generated", "--confirm"})
        self.assertEqual(flags(verbs.choices["check"]), roots)

    def test_main_returns_codes_and_the_script_ends_with_systemexit(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertTrue(source.rstrip().endswith("raise SystemExit(main())"))
        self.assertIn("sys.path.insert(0, str(Path(__file__).resolve().parent))", source)

    def test_no_catalog_is_exit_2_and_names_the_fix(self):
        code, out, err = self.run_notes("write")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("ingest.py build", err)
        self.assertEqual(self.run_notes("check")[0], bc.EXIT_USAGE)

    def test_a_catalog_of_another_schema_is_exit_2(self):
        self.two_sets()
        path = self.root / "catalog" / "catalog.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["schema"] = "something-else/9"
        bc.write_json(path, data)
        self.assertEqual(self.run_notes("write")[0], bc.EXIT_USAGE)

    def test_a_catalog_that_is_not_shaped_as_f5_says_is_exit_2_not_a_traceback(self):
        self.two_sets()
        path = self.root / "catalog" / "catalog.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["sets"] = [{"set_slug": "ok-slug", "note": "02_Vendor_Packs/ok-slug.md", "brushes": 7}]
        bc.write_json(path, data)
        code, _, err = self.run_notes("write")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("ingest.py build", err)

    def test_a_missing_brush_record_is_exit_2(self):
        a, *_ = self.two_sets()
        (self.root / "catalog" / "brushes" / f"{a}.json").unlink()
        code, _, err = self.run_notes("write")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn(a, err)

    def test_an_unknown_only_is_exit_2(self):
        self.two_sets()
        code, _, err = self.run_notes("write", "--only", "no-such-set")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("no-such-set", err)

    def test_a_bad_flag_is_exit_2(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            notes.main(["write", "--nonsense"])
        self.assertEqual(caught.exception.code, 2)


# ── dry run and confirm ──────────────────────────────────────────────────────

class DryRunAndConfirm(NotesCase):
    def test_a_dry_run_writes_nothing_and_says_so(self):
        self.two_sets()
        before = fixtures.tree_digest(self.root)
        code, out, _ = self.run_notes("write")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(out.rstrip("\n").splitlines()[-1], "DRY RUN   nothing is written without --confirm.")
        self.assertEqual(fixtures.tree_digest(self.root), before)
        self.assertFalse(self.vault.exists(), "a dry run does not even make the folder")
        self.assertIn("new       02_Vendor_Packs/demo-set.md", out)

    def test_confirm_writes_every_expected_file(self):
        self.two_sets()
        code, out, _ = self.write()
        self.assertEqual(code, bc.EXIT_OK)
        written = sorted(p.relative_to(self.vault).as_posix() for p in self.vault.rglob("*") if p.is_file())
        self.assertEqual(written, ["00_INDEX.md", "01_Procreate_Defaults/_index.md", "02_Vendor_Packs/_index.md",
                                   "02_Vendor_Packs/demo-set.md", "03_Loose/_index.md",
                                   "03_Loose/demo-pack-loose.md", "04_My_Brushes/_index.md"])
        self.assertIn("WROTE     7 files", out)
        self.assertFalse(list(self.vault.rglob("*.tmp")), "writes go through a temporary name and leave none")

    def test_the_frontmatter_has_the_f7_keys_in_order(self):
        self.two_sets()
        self.write()
        head = self.note("02_Vendor_Packs/demo-set.md").split("\n---\n", 1)[0].split("\n")
        self.assertEqual(head[0], "---")
        self.assertEqual([line.split(":", 1)[0] for line in head[1:]], FRONT_KEYS)
        values = dict(line.split(": ", 1) for line in head[1:])
        self.assertEqual(values["title"], '"Demo Set"')
        self.assertEqual(values["set_name"], '"Demo Set "', "the trailing space is kept")
        self.assertEqual((values["type"], values["library"], values["pack_kind"], values["redistribute"]),
                         ("brushset", "user", "vendor", "unknown"))
        self.assertEqual(values["vendor"], '"Demo Vendor"')
        self.assertEqual(values["brush_count"], "3")
        self.assertEqual(values["eras"], "[E3, E4]")
        self.assertEqual(values["kinds"], "[stamp, stroke]")
        self.assertEqual(values["template"], "brushset-note/1")
        self.assertEqual(values["tags"], "[brushset, library/user, era/E3, era/E4]")
        self.assertRegex(values["generated_fingerprint"], r'^"sha256:16:[0-9a-f]{16}"$')

    def test_every_brush_section_has_the_twelve_lines_in_order(self):
        a, b, c, d = self.two_sets()
        self.write()
        text = self.note("02_Vendor_Packs/demo-set.md")
        sections = self.sections(text)
        self.assertEqual(list(sections), ["Overview", "Inker", "Pencil", "Marker", "Notes"])
        for heading, brush_id in (("Inker", a), ("Pencil", b), ("Marker", c)):
            body = [line for line in sections[heading] if line.startswith("- ")]
            self.assertEqual(len(body), 12, heading)
            self.assertEqual([line[2:].split(":", 1)[0] for line in body], LINE_PREFIXES)
            self.assertEqual(ID_LINE.match(body[0]).group(1), brush_id)
            self.assertIn(f"![[_Previews/demo-set/{brush_id}.stroke.png]]", sections[heading])
        self.assertTrue(text.endswith("## Notes\n"))
        self.assertIn("\n\n## Notes\n", text, "a blank line before the author's heading")

    def test_the_lines_quote_the_catalog(self):
        a, b, c, d = self.two_sets()
        self.write()
        sections = self.sections(self.note("02_Vendor_Packs/demo-set.md"))
        inker = [line for line in sections["Inker"] if line.startswith("- ")]
        self.assertEqual(inker[0], f"- id: `{a}` · 1 of 3 · era E3 · 88 keys")
        self.assertEqual(inker[1], "- kind: stroke · spacing tight (0.026)")
        self.assertEqual(inker[2], "- shape: embedded 64x32, inverted yes · scatter 0.18 · rotation 1.00 · "
                                   "randomised yes · azimuth no")
        self.assertEqual(inker[3], "- grain: blank (`Brush-Preset-Blank.png`) · scale 16.00 · movement 1.00 · zoom 1.00")
        self.assertEqual(inker[4], "- size: 0.003 to 0.198 (fine) · opacity 0.01 to 1.00")
        self.assertEqual(inker[5], "- pressure: size high (1.00) · opacity none (0.00)")
        self.assertEqual(inker[6], "- tilt: none")
        self.assertEqual(inker[7], "- speed: size 0.63 · opacity 0.00")
        self.assertEqual(inker[8], "- taper: both · pencil 0.11/0.11 · touch 0.21/0.24")
        self.assertEqual(inker[9], "- render: render-type-0 · blend 0 · flow 0.91 · wet mix no")
        self.assertEqual(inker[10], "- facets: stroke spacing-tight era-e3")
        self.assertEqual(inker[11], "- preview: Procreate's own thumbnail")
        pencil = [line for line in sections["Pencil"] if line.startswith("- ")]
        self.assertEqual(pencil[2], "- shape: bundled `Brush-Preset-Hard.png` (inside Procreate, not in this library)"
                                    " · scatter 0.18 · rotation 1.00 · randomised yes · azimuth no")
        self.assertIn("bundled `Brush-Preset-Stained-Paper-1.jpg`", pencil[3])
        self.assertEqual(pencil[11], "- preview: Procreate's own thumbnail; shape and grain images are not in the file")
        loose = [line for line in self.sections(self.note("03_Loose/demo-pack-loose.md"))["Loose One"]
                 if line.startswith("- ")]
        self.assertEqual(loose[6], "- tilt: size 1.00 · opacity 0.80")

    def test_the_overview_counts_what_the_catalog_holds(self):
        self.two_sets()
        self.write()
        overview = "\n".join(self.sections(self.note("02_Vendor_Packs/demo-set.md"))["Overview"]).strip()
        paragraph = overview.split("\n\n")[0]
        self.assertTrue(paragraph.startswith("Three brushes from the pack `demo-pack` (Demo Vendor), read from "
                                             "`Demo_Set.brushset` (517,781 bytes)."), paragraph)
        self.assertIn("Two are stroke brushes and one is a stamp. Their format eras are E3 (2) and E4 (1).", paragraph)
        self.assertTrue(paragraph.endswith("licence note: none in pack; store terms apply."), paragraph)
        self.assertTrue(overview.endswith("Write only below it."))

    def test_the_overview_wording_for_all_both_and_one(self):
        words = notes._phrase_sentence
        phrases = notes.KIND_PHRASES
        self.assertEqual(words({"stroke": 6}, 6, phrases), "All six are stroke brushes.")
        self.assertEqual(words({"stroke": 2}, 2, phrases), "Both are stroke brushes.")
        self.assertEqual(words({"stroke": 1}, 1, phrases), "It is a stroke brush.")
        self.assertEqual(words({"stroke": 3, "stamp": 1}, 4, phrases), "Three are stroke brushes and one is a stamp.")
        self.assertEqual(words({"stroke": 3}, 4, phrases), "Three are stroke brushes and one has no recorded value.")
        self.assertIsNone(words({}, 0, phrases))

    def test_a_pack_without_a_vendor_or_a_licence_note(self):
        self.cat.pack("anon", vendor=None, licence=None, redistribute="yes")
        a = self.cat.brush("Solo")
        self.cat.set("anon-set", [a], pack="anon")
        self.cat.build()
        self.write()
        text = self.note("02_Vendor_Packs/anon-set.md")
        self.assertIn('vendor: ""', text)
        self.assertIn('redistribute: "yes"', text, "a bare yes would read as a YAML boolean")
        self.assertIn("One brush from the pack `anon`, read from", text)
        self.assertIn("Redistribution is recorded as yes.", text)

    def test_the_generated_part_of_a_new_note_is_followed_by_an_empty_notes_section(self):
        self.two_sets()
        self.write()
        text = self.note("02_Vendor_Packs/demo-set.md")
        generated, tail = notes.split_at_notes(text)
        self.assertEqual(tail, "## Notes\n")
        self.assertTrue(notes.fingerprint_holds(generated))

    def test_files_are_utf8_lf_without_a_bom_and_end_with_a_newline(self):
        self.two_sets()
        self.write()
        for path in self.vault.rglob("*.md"):
            data = path.read_bytes()
            self.assertFalse(data.startswith(b"\xef\xbb\xbf"), path.name)
            self.assertNotIn(b"\r", data, path.name)
            self.assertTrue(data.endswith(b"\n"), path.name)
            data.decode("utf-8")


# ── regeneration ─────────────────────────────────────────────────────────────

class Regeneration(NotesCase):
    AUTHOR = ("## Notes\r\n\r\nMy own thoughts: the \"Inker\" is my go-to.\r\n- bullet \u2603\r\n\r\n"
              "## Notes (old)\r\ntext with no final newline")

    def setUp(self):
        super().setUp()
        self.ids = self.two_sets()
        self.write()
        self.rel = "02_Vendor_Packs/demo-set.md"

    def author_in(self, rel=None, tail=None):
        rel = rel or self.rel
        generated, _ = notes.split_at_notes(self.note(rel))
        (self.vault / rel).write_bytes((generated + (tail or self.AUTHOR)).encode("utf-8"))

    def test_a_second_run_writes_nothing_and_touches_no_file(self):
        stamps = {p: p.stat().st_mtime_ns for p in self.vault.rglob("*") if p.is_file()}
        digest = fixtures.tree_digest(self.vault)
        code, out, _ = self.write()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("WROTE     0 files", out)
        self.assertIn("SUMMARY   7 files: 0 new, 0 changed, 7 unchanged, 0 refused, 0 orphan", out)
        self.assertEqual(fixtures.tree_digest(self.vault), digest)
        self.assertEqual({p: p.stat().st_mtime_ns for p in self.vault.rglob("*") if p.is_file()}, stamps)

    def test_the_authors_notes_section_survives_a_change_byte_for_byte(self):
        self.author_in()
        before = (self.vault / self.rel).read_bytes()
        tail = notes.split_at_notes(before.decode("utf-8"))[1].encode("utf-8")
        record = self.cat.root / "catalog" / "brushes" / f"{self.ids[0]}.json"
        data = json.loads(record.read_text(encoding="utf-8"))
        data["settings"]["maxSize"] = 0.5
        data["facets"]["size_max"] = 0.5
        data["facets"]["size_class"] = "fine"
        bc.write_json(record, data)
        code, out, _ = self.write()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertRegex(out, r"changed   02_Vendor_Packs/demo-set\.md  \(\+2 -2\)")
        after = (self.vault / self.rel).read_bytes()
        self.assertEqual(notes.split_at_notes(after.decode("utf-8"))[1].encode("utf-8"), tail,
                         "the tail is the author's, CRLF included")
        self.assertEqual(tail, self.AUTHOR.encode("utf-8"))
        self.assertIn(b"size: 0.003 to 0.500 (fine)", after)
        self.assertNotEqual(after, before)
        self.assertFalse(b"\r" in after[:after.index(b"## Notes")], "the generated part is LF")

    def test_a_catalog_change_in_one_note_leaves_the_others_alone(self):
        names = ("demo-pack-loose.md", "01_Procreate_Defaults")
        stamps = {p: p.stat().st_mtime_ns for p in self.vault.rglob("*.md")}
        record = self.cat.root / "catalog" / "brushes" / f"{self.ids[2]}.json"     # Marker, only in demo-set
        data = json.loads(record.read_text(encoding="utf-8"))
        data["facets"]["spacing"] = 0.5
        bc.write_json(record, data)
        code, out, _ = self.write()
        self.assertEqual(code, bc.EXIT_OK)
        changed = sorted(l.split()[1] for l in out.splitlines() if l.startswith("changed"))
        self.assertEqual(changed, ["02_Vendor_Packs/demo-set.md"])
        for path, stamp in stamps.items():
            if path.name != "demo-set.md":
                self.assertEqual(path.stat().st_mtime_ns, stamp, path.name)

    def test_a_crlf_converted_generated_part_is_not_a_hand_edit(self):
        path = self.vault / self.rel
        text = path.read_bytes().decode("utf-8")
        path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
        code, out, _ = self.run_notes("check")
        self.assertEqual(code, bc.EXIT_OK, out)

    def test_a_hand_edited_generated_part_is_refused_and_nothing_is_written_for_it(self):
        self.author_in()
        self.hand_edit(self.rel, "spacing tight (0.026)", "spacing LOOSE (0.026)")
        edited = (self.vault / self.rel).read_bytes()
        # another note changes at the same time: it must still be written
        record = self.cat.root / "catalog" / "brushes" / f"{self.ids[3]}.json"      # Loose One, in the loose note
        data = json.loads(record.read_text(encoding="utf-8"))
        data["facets"]["opacity_max"] = 0.5
        bc.write_json(record, data)
        code, out, _ = self.write()
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertRegex(out, r"REFUSED   02_Vendor_Packs/demo-set\.md  the generated part was edited by hand")
        self.assertEqual((self.vault / self.rel).read_bytes(), edited, "untouched")
        self.assertIn("to 0.50", self.note("03_Loose/demo-pack-loose.md"), "the other note was written")
        self.assertIn("1 refused", out)

    def test_a_dry_run_with_a_refused_note_is_exit_1(self):
        self.hand_edit(self.rel, "spacing tight (0.026)", "spacing LOOSE (0.026)")
        code, out, _ = self.run_notes("write")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("DRY RUN", out)

    def test_overwrite_generated_shows_the_lost_lines_and_needs_confirm(self):
        self.author_in()
        self.hand_edit(self.rel, "spacing tight (0.026)", "spacing LOOSE (0.026)")
        edited = (self.vault / self.rel).read_bytes()
        code, out, _ = self.run_notes("write", "--overwrite-generated")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("overwrites hand edits", out)
        self.assertIn("- kind: stroke · spacing LOOSE (0.026)", out, "the lines that would be lost")
        self.assertEqual((self.vault / self.rel).read_bytes(), edited, "no --confirm, no write")
        code, out, _ = self.write("--overwrite-generated")
        self.assertEqual(code, bc.EXIT_OK)
        after = (self.vault / self.rel).read_bytes()
        self.assertIn(b"spacing tight (0.026)", after)
        self.assertNotIn(b"LOOSE", after)
        self.assertEqual(notes.split_at_notes(after.decode("utf-8"))[1], self.AUTHOR, "the tail still survives")
        self.assertEqual(self.run_notes("check")[0], bc.EXIT_OK)

    def test_overwrite_generated_does_not_touch_a_note_that_was_not_edited(self):
        self.author_in()
        digest = fixtures.tree_digest(self.vault)
        code, out, _ = self.write("--overwrite-generated")
        self.assertEqual((code, fixtures.tree_digest(self.vault)), (bc.EXIT_OK, digest))

    def test_a_file_with_no_notes_line_is_refused_even_with_overwrite(self):
        path = self.vault / self.rel
        path.write_bytes(b"# my own file\n\nno notes heading here\n")
        before = path.read_bytes()
        for flags in ((), ("--overwrite-generated",)):
            code, out, _ = self.write(*flags)
            self.assertEqual(code, bc.EXIT_REFUSED)
            self.assertIn("no `## Notes` line", out)
            self.assertEqual(path.read_bytes(), before)

    def test_a_file_that_is_not_utf8_is_refused_untouched(self):
        path = self.vault / self.rel
        path.write_bytes(b"\xff\xfe not text")
        code, out, _ = self.write()
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(path.read_bytes(), b"\xff\xfe not text")

    def test_the_split_is_at_the_last_notes_line(self):
        """F7: the last line exactly equal to `## Notes`. An author who writes a second
        `## Notes` line pulls their first section into the generated part, which then
        fails its fingerprint: refused, never silently overwritten."""
        self.author_in(tail="## Notes\nfirst\n\n## Notes\nsecond\n")
        text = self.note(self.rel)
        generated, tail = notes.split_at_notes(text)
        self.assertEqual(tail, "## Notes\nsecond\n")
        code, out, _ = self.write()
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(self.note(self.rel), text)

    def test_a_heading_that_only_looks_like_notes_is_not_the_split(self):
        text = "x\n## Notes (old)\n## Notes \n### Notes\n"
        self.assertIsNone(notes.split_at_notes(text))

    def test_author_text_between_the_title_and_the_overview_is_a_hand_edit(self):
        self.hand_edit(self.rel, "## Overview\n", "my aside\n\n## Overview\n")
        self.assertEqual(self.run_notes("check")[0], bc.EXIT_REFUSED)

    def test_diff_prints_the_change_and_still_writes_nothing(self):
        record = self.cat.root / "catalog" / "brushes" / f"{self.ids[0]}.json"
        data = json.loads(record.read_text(encoding="utf-8"))
        data["facets"]["opacity_min"] = 0.25
        bc.write_json(record, data)
        digest = fixtures.tree_digest(self.vault)
        code, out, _ = self.run_notes("write", "--diff")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("--- a/02_Vendor_Packs/demo-set.md", out)
        self.assertIn("+++ b/02_Vendor_Packs/demo-set.md", out)
        self.assertIn("-- size: 0.003 to 0.198 (fine) · opacity 0.01 to 1.00", out)
        self.assertIn("+- size: 0.003 to 0.198 (fine) · opacity 0.25 to 1.00", out)
        self.assertEqual(fixtures.tree_digest(self.vault), digest)
        quiet = self.run_notes("write")[1]
        self.assertNotIn("--- a/", quiet, "no --diff, no diff")

    def test_only_limits_the_run_to_one_note_and_skips_the_indexes(self):
        record = self.cat.root / "catalog" / "brushes" / f"{self.ids[2]}.json"
        data = json.loads(record.read_text(encoding="utf-8"))
        data["facets"]["size_max"] = 0.4
        bc.write_json(record, data)
        code, out, _ = self.write("--only", "demo-set")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("SUMMARY   1 files: 0 new, 1 changed", out)
        self.assertNotIn("_index", out)
        by_pack = self.run_notes("write", "--only", "demo-pack")[1]
        self.assertIn("demo-pack-loose.md", by_pack, "a pack id selects all its sets")

    def test_orphans_are_reported_never_deleted(self):
        path = self.vault / "02_Vendor_Packs" / "gone-set.md"
        generated, _ = notes.split_at_notes(self.note(self.rel))
        path.write_bytes((generated + "## Notes\nkeep me\n").encode("utf-8"))
        code, out, _ = self.write()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("orphan    02_Vendor_Packs/gone-set.md", out)
        self.assertTrue(path.is_file())
        self.assertIn("keep me", self.note("02_Vendor_Packs/gone-set.md"))
        code, out, _ = self.run_notes("check")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("orphan", out)

    def test_an_authored_file_in_a_note_folder_is_not_an_orphan(self):
        (self.vault / "04_My_Brushes" / "my-ideas.md").write_bytes(b"# Ideas\n\nnot generated\n")
        code, out, _ = self.run_notes("check")
        self.assertEqual(code, bc.EXIT_OK, out)

    def test_an_index_keeps_the_authors_section_too(self):
        rel = "02_Vendor_Packs/_index.md"
        generated, _ = notes.split_at_notes(self.note(rel))
        (self.vault / rel).write_bytes((generated + "## Notes\nmy reading list\n").encode("utf-8"))
        record = self.cat.root / "catalog" / "catalog.json"
        data = json.loads(record.read_text(encoding="utf-8"))
        data["sets"][0]["title"] = "Renamed Set"
        bc.write_json(record, data)
        self.write()
        text = self.note(rel)
        self.assertIn("Renamed Set", text)
        self.assertTrue(text.endswith("## Notes\nmy reading list\n"))


# ── check ────────────────────────────────────────────────────────────────────

class Check(NotesCase):
    def setUp(self):
        super().setUp()
        self.ids = self.two_sets()
        self.write()

    def test_a_vault_that_matches_is_exit_0_and_check_writes_nothing(self):
        digest = fixtures.tree_digest(self.root)
        code, out, _ = self.run_notes("check")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("OK        7 files match the catalog", out)
        self.assertEqual(fixtures.tree_digest(self.root), digest)

    def test_a_stale_value_is_drift(self):
        record = self.cat.root / "catalog" / "brushes" / f"{self.ids[0]}.json"
        data = json.loads(record.read_text(encoding="utf-8"))
        data["settings"]["shapeScatter"] = 0.75
        bc.write_json(record, data)
        code, out, _ = self.run_notes("check")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("changed", out)
        self.assertIn("DRIFT", out)
        self.assertEqual(self.write()[0], bc.EXIT_OK)
        self.assertEqual(self.run_notes("check")[0], bc.EXIT_OK, "write fixes what check found")

    def test_a_missing_note_is_drift(self):
        (self.vault / "02_Vendor_Packs" / "demo-set.md").unlink()
        code, out, _ = self.run_notes("check")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("missing   02_Vendor_Packs/demo-set.md", out)

    def test_an_empty_vault_is_all_missing(self):
        code, out, _ = self.run_notes("check", root=self.root)
        self.assertEqual(code, bc.EXIT_OK)
        for path in sorted(self.vault.rglob("*.md")):
            path.unlink()
        code, out, _ = self.run_notes("check")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(out.count("missing"), 7)

    def test_an_extra_section_in_the_generated_part_is_drift(self):
        self.hand_edit("03_Loose/demo-pack-loose.md", "\n## Notes\n", "\n## An extra section\n\nx\n\n## Notes\n")
        code, out, _ = self.run_notes("check")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("REFUSED   03_Loose/demo-pack-loose.md", out)

    def test_a_note_whose_set_left_the_catalog_is_an_orphan(self):
        self.cat.sets.pop()
        self.cat.build()
        (self.root / "catalog" / "sets" / "demo-pack-loose.json").unlink()
        code, out, _ = self.run_notes("check")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("orphan    03_Loose/demo-pack-loose.md", out)

    def test_previews_arriving_in_the_catalog_make_the_note_stale(self):
        record = self.cat.root / "catalog" / "brushes" / f"{self.ids[0]}.json"
        data = json.loads(record.read_text(encoding="utf-8"))
        data["facets"].update({"shape_coverage": 0.61, "shape_aspect": 1.0, "shape_midtone": 0.1,
                               "shape_edge_touch": 0.07})
        data["facet_words"] += ["shape-even", "shape-hard"]
        data["preview"]["stroke"] = f"_Previews/demo-set/{self.ids[0]}.stroke.png"
        bc.write_json(record, data)
        self.assertEqual(self.run_notes("check")[0], bc.EXIT_REFUSED)
        self.write()
        line = [l for l in self.note("02_Vendor_Packs/demo-set.md").split("\n") if l.startswith("- shape:")][0]
        self.assertEqual(line, "- shape: embedded 64x32, inverted yes · coverage 0.61 · aspect even (1.00) · "
                               "edges hard (0.10) · edge touch 0.07 · scatter 0.18 · rotation 1.00 · "
                               "randomised yes · azimuth no")


# ── routing ──────────────────────────────────────────────────────────────────

class Routing(NotesCase):
    def test_route_folder_is_the_table_of_f7(self):
        route = notes.route_folder
        self.assertEqual(route({"library": "official", "pack_kind": "official", "kind": "set"}), "01_Procreate_Defaults")
        self.assertEqual(route({"library": "user", "pack_kind": "mine", "kind": "set"}), "04_My_Brushes")
        self.assertEqual(route({"library": "user", "pack_kind": "mine", "kind": "loose"}), "04_My_Brushes")
        self.assertEqual(route({"library": "user", "pack_kind": "vendor", "kind": "loose"}), "03_Loose")
        self.assertEqual(route({"library": "user", "pack_kind": "vendor", "kind": "set"}), "02_Vendor_Packs")
        self.assertEqual(route({"library": "user", "pack_kind": "vendor", "kind": "set", "pack": "unsorted"}),
                         "02_Vendor_Packs")
        self.assertEqual(route({"library": "official", "pack_kind": "official", "kind": "loose"}),
                         "01_Procreate_Defaults", "official wins over loose")

    def test_each_kind_of_set_lands_in_its_folder(self):
        self.cat.pack("procreate-5", kind="official", vendor="Savage Interactive (Procreate)", library="official")
        self.cat.pack("mine", kind="mine", vendor="Me")
        self.cat.pack("unsorted", kind="vendor", vendor=None)
        ids = [self.cat.brush(n) for n in ("O", "V", "L", "M", "U", "ML")]
        self.cat.set("p5-test", [ids[0]], pack="procreate-5", name="Test 1", title="Test (Procreate 5)")
        self.cat.set("vend", [ids[1]])
        self.cat.set("vend-loose", [ids[2]], kind="loose", container="user/demo-pack/a.brush")
        self.cat.set("mine-set", [ids[3]], pack="mine")
        self.cat.set("mine-loose", [ids[5]], pack="mine", kind="loose", container="user/mine/a.brush")
        self.cat.set("odd", [ids[4]], pack="unsorted")
        self.cat.build()
        self.write()
        found = sorted(p.relative_to(self.vault).as_posix() for p in self.vault.rglob("*.md") if p.name != "_index.md")
        self.assertEqual(found, ["00_INDEX.md", "01_Procreate_Defaults/p5-test.md", "02_Vendor_Packs/odd.md",
                                 "02_Vendor_Packs/vend.md", "03_Loose/vend-loose.md",
                                 "04_My_Brushes/mine-loose.md", "04_My_Brushes/mine-set.md"])
        self.assertIn("library: official", self.note("01_Procreate_Defaults/p5-test.md"))
        self.assertIn("pack_kind: mine", self.note("04_My_Brushes/mine-set.md"))
        self.assertIn("[[04_My_Brushes/mine-set|", self.note("04_My_Brushes/_index.md"))
        self.assertNotIn("mine-set", self.note("02_Vendor_Packs/_index.md"))
        self.assertEqual(self.run_notes("check")[0], bc.EXIT_OK)

    def test_a_catalog_that_routes_a_set_elsewhere_is_refused(self):
        self.two_sets()
        path = self.root / "catalog" / "catalog.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["sets"][0]["note"] = "04_My_Brushes/demo-set.md"
        bc.write_json(path, data)
        code, out, err = self.run_notes("write", "--confirm")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("02_Vendor_Packs/demo-set.md", err)
        self.assertFalse(self.vault.exists())

    def test_the_set_with_no_note_gets_no_file_and_is_named_in_the_index(self):
        a = self.cat.brush("Alpha")
        b = self.cat.brush("Beta")
        self.cat.set("rsco", [a, b])
        self.cat.set("rsco-loose", [b, a], kind="loose", container="user/demo-pack/x.brush")
        self.cat.build()
        rows = {r["set_slug"]: r for r in json.loads((self.root / "catalog" / "catalog.json").read_text(encoding="utf-8"))["sets"]}
        self.assertIsNone(rows["rsco-loose"]["note"])
        code, out, _ = self.write()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertFalse(list(self.vault.rglob("rsco-loose*")))
        self.assertNotIn("rsco-loose", self.note("03_Loose/_index.md"))
        self.assertIn("`rsco-loose`", self.note("00_INDEX.md"))
        self.assertIn("1 set has no note", self.note("00_INDEX.md"))
        code, out, _ = self.run_notes("write", "--only", "rsco-loose")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("rsco-loose has no note", out)

    def test_shared_brushes_are_stubs_that_point_at_the_home_heading(self):
        a, b, c, d = self.two_sets()
        self.write()
        loose = self.note("03_Loose/demo-pack-loose.md")
        sections = self.sections(loose)
        self.assertEqual(list(sections), ["Overview", "Loose One", "Shared brushes", "Notes"])
        stubs = [l for l in sections["Shared brushes"] if l.startswith("- ")]
        self.assertEqual(stubs, [f"- `{a}` Inker: see [[02_Vendor_Packs/demo-set#Inker]]"])
        self.assertEqual(sum(1 for l in loose.split("\n") if ID_LINE.match(l)), 1, "no section for a shared brush")
        paragraph = "\n".join(sections["Overview"]).split("\n\n")[0]
        self.assertIn("Two loose brush files from the pack `demo-pack` (Demo Vendor)", paragraph)
        self.assertIn("One has its section in this note; the other one is homed in another set", paragraph)

    def test_a_brush_homed_in_a_set_without_a_note_is_a_catalog_error(self):
        a, b, c, d = self.two_sets()
        path = self.root / "catalog" / "catalog.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data["sets"]:
            if row["set_slug"] == "demo-set":
                row["note"] = None
        bc.write_json(path, data)
        code, _, err = self.run_notes("write", "--confirm")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("has no note", err)


# ── odd names ────────────────────────────────────────────────────────────────

ODD_NAMES = ["Ink: Fine #1", 'Quote "Pen"', "Back\\slash", "Caf\u00e9 \u58a8 \U0001f4a7", "Line\nBreak",
             "# Hash first", "[[Link]] | pipe", "Overview", "Notes", "Shared brushes", "Twin", "Twin", "Twin",
             "Twin (2)", "  Spaced  name ", "", "Overview", "tab\there", "bom\ufeffname"]


class OddNames(NotesCase):
    def setUp(self):
        super().setUp()
        self.ids = [self.cat.brush(name) for name in ODD_NAMES]
        self.cat.set("odd-set", self.ids, name='Odd: "Set" #1 \\ \u6d53\u58a8 ', title='Odd: "Set" #1 \\ \u6d53\u58a8 ')
        self.cat.set("odd-loose", [self.ids[0], self.ids[4]], kind="loose", name="odd-loose",
                     title="Odd (loose)", container="user/demo-pack/o.brush")
        self.cat.build()
        self.write()
        self.text = self.note("02_Vendor_Packs/odd-set.md")

    def headings(self):
        return [line[3:] for line in self.text.split("\n") if line.startswith("## ")]

    def test_headings_are_one_line_unique_and_never_reserved(self):
        headings = self.headings()
        self.assertEqual(headings, [
            "Overview", "Ink: Fine #1", 'Quote "Pen"', "Back\\slash", "Caf\u00e9 \u58a8 \U0001f4a7", "Line Break",
            "# Hash first", "[[Link]] | pipe", "Overview (brush)", "Notes (brush)", "Shared brushes (brush)",
            "Twin", "Twin (2)", "Twin (3)", "Twin (2) (2)", "Spaced  name", "Untitled", "Overview (brush) (2)",
            "tab here", "bom name", "Notes"])
        self.assertEqual(len(set(headings)), len(headings))
        self.assertEqual(sum(1 for l in self.text.split("\n") if ID_LINE.match(l)), len(ODD_NAMES))

    def test_every_chunk_is_one_id_line_and_twelve_lines(self):
        for heading, body in self.sections(self.text).items():
            if heading in ("Overview", "Notes"):
                continue
            lines = [l for l in body if l.startswith("- ")]
            self.assertEqual([l[2:].split(":", 1)[0] for l in lines], LINE_PREFIXES, heading)
            self.assertRegex(lines[0], r"^- id: `b_[0-9a-f]{12}`")

    def test_the_notes_line_appears_once(self):
        self.assertEqual(len(notes.NOTES_LINE.findall(self.text)), 1)

    def test_the_frontmatter_is_flat_and_safe(self):
        head = self.text.split("\n---\n", 1)[0]
        lines = head.split("\n")[1:]
        self.assertEqual([l.split(":", 1)[0] for l in lines], FRONT_KEYS)
        title = dict(l.split(": ", 1) for l in lines)["title"]
        self.assertEqual(title, '"Odd: \'Set\' #1 \\\\ \u6d53\u58a8"', "a double quote becomes a single one")
        self.assertEqual(dict(l.split(": ", 1) for l in lines)["set_name"], '"Odd: \'Set\' #1 \\\\ \u6d53\u58a8 "')

    @unittest.skipIf(yaml is None, "pyyaml is not installed")
    def test_the_frontmatter_parses_as_yaml(self):
        data = yaml.safe_load(self.text.split("\n---\n", 1)[0][4:])
        self.assertEqual(data["title"], "Odd: 'Set' #1 \\ \u6d53\u58a8")
        self.assertEqual(data["set_name"], "Odd: 'Set' #1 \\ \u6d53\u58a8 ")
        self.assertEqual(data["brush_count"], len(ODD_NAMES))
        self.assertEqual(data["tags"], ["brushset", "library/user", "era/E3"])
        self.assertEqual(data["redistribute"], "unknown")
        for path in self.vault.rglob("*.md"):
            front = yaml.safe_load(path.read_bytes().decode("utf-8").split("\n---\n", 1)[0][4:])
            self.assertIn("type", front, path.name)

    def test_the_index_survives_odd_titles(self):
        index = self.note("02_Vendor_Packs/_index.md")
        self.assertIn("[[02_Vendor_Packs/odd-set|Odd: 'Set' #1 \\ \u6d53\u58a8]]".replace("'", '"'), index)
        self.assertNotIn("\n[[", index)


class SharedWithOddHeading(NotesCase):
    def test_the_stub_target_drops_characters_a_link_cannot_hold(self):
        a = self.cat.brush("Ink: Fine #1 [x] | y^z")
        b = self.cat.brush("Own")
        self.cat.set("home", [a])
        self.cat.set("lo", [b, a], kind="loose", container="user/demo-pack/o.brush")
        self.cat.build()
        self.write()
        loose = self.note("03_Loose/lo.md")
        self.assertIn(f"- `{a}` Ink: Fine #1 [x] | y^z: see [[02_Vendor_Packs/home#Ink Fine 1 x y z]]", loose)


class Numbers(unittest.TestCase):
    def test_fnum(self):
        self.assertEqual(notes.fnum(0.0254, 3), "0.025")
        self.assertEqual(notes.fnum(0.026, 3), "0.026")
        self.assertEqual(notes.fnum(1, 2), "1.00")
        self.assertEqual(notes.fnum(-0.001, 2), "0.00", "no negative zero")
        self.assertEqual(notes.fnum(-0.5, 2), "-0.50")
        self.assertEqual(notes.fnum(None), "n/a")
        self.assertEqual(notes.fnum("x"), "n/a")
        self.assertEqual(notes.fnum(True), "n/a", "a bool is not a number")
        self.assertEqual(notes.fnum(float("nan")), "n/a")
        self.assertEqual(notes.fnum(1.0, 0), "1")

    def test_scalar_opens_a_tag(self):
        self.assertEqual(notes.scalar({"$real32": "3f800000"}), 1.0)
        self.assertEqual(notes.scalar({"$real64": "bff0000000000000"}), -1.0)
        self.assertEqual(notes.scalar({"$real32": 0.5}), 0.5)
        self.assertEqual(notes.scalar({"$int": 3}), 3.0)
        self.assertEqual(notes.fnum({"$real32": "80000000"}), "0.00", "the library's negative-zero tilt angle")
        self.assertIsNone(notes.scalar({"$real32": "zz"}))
        self.assertIsNone(notes.scalar({"points": []}))
        self.assertIsNone(notes.scalar(None))

    def test_yesno(self):
        self.assertEqual((notes.yesno(True), notes.yesno(False), notes.yesno(None), notes.yesno(1)),
                         ("yes", "no", "n/a", "n/a"))

    def test_words_and_lists(self):
        self.assertEqual(notes.count_word(6), "six")
        self.assertEqual(notes.count_word(13), "13")
        self.assertEqual(notes.count_word(1234), "1,234")
        self.assertEqual(notes.join_and(["a"]), "a")
        self.assertEqual(notes.join_and(["a", "b"]), "a and b")
        self.assertEqual(notes.join_and(["a", "b", "c"]), "a, b and c")

    def test_yaml_scalars(self):
        self.assertEqual(notes.yaml_plain("demo-set"), "demo-set")
        self.assertEqual(notes.yaml_plain("s_0123456789ab"), "s_0123456789ab")
        for risky in ("yes", "No", "null", "true", "123", "1e3", "", "a b", "a: b", "#x", "-x"):
            self.assertTrue(notes.yaml_plain(risky).startswith('"'), risky)
        self.assertEqual(notes.yaml_quoted('a"b\\c\nd'), '"a\'b\\\\c d"')

    def test_missing_settings_read_n_a_and_never_crash(self):
        builder = {"id": "b_000000000001", "settings": {}, "facets": {}, "shape": {}, "grain": {},
                   "preview": {}, "format": {}, "home": {}}
        cat = type("C", (), {"texture_size": staticmethod(lambda _t: None), "pack": staticmethod(lambda _p: {})})()
        lines = notes.brush_section(cat, builder, "X", {"brush_count": 1})
        body = [l for l in lines if l.startswith("- ")]
        self.assertEqual(len(body), 12)
        self.assertIn("scatter n/a", body[2])
        self.assertIn("pencil n/a · touch n/a", body[8])
        self.assertIn("flow n/a", body[9])


# ── previews ─────────────────────────────────────────────────────────────────

class PreviewLinks(NotesCase):
    def test_links_follow_the_record_else_the_f6_path_and_no_image_is_created(self):
        a = self.cat.brush("Has path", preview={"stroke": "_Previews/set-x/custom.stroke.png"})
        b = self.cat.brush("No path yet")
        c = self.cat.brush("None source", preview={"stroke_source": "none"}, facets={"stroke_source": "none"})
        d = self.cat.brush("From reset", preview={"stroke_source": "reset-thumbnail"})
        self.cat.set("set-x", [a, b, c, d])
        self.cat.pack("private", publish_previews=False)
        e = self.cat.brush("Private one")
        self.cat.set("priv", [e], pack="private")
        self.cat.build()
        self.write()
        text = self.note("02_Vendor_Packs/set-x.md")
        self.assertIn("![[_Previews/set-x/custom.stroke.png]]", text)
        self.assertIn(f"![[_Previews/set-x/{b}.stroke.png]]", text)
        self.assertIn("- preview: no thumbnail in the file (the preview is a placeholder)", text)
        self.assertIn("- preview: the thumbnail inside the Reset folder", text)
        self.assertIn(f"![[_Previews/_local/priv/{e}.stroke.png]]", self.note("02_Vendor_Packs/priv.md"))
        self.assertFalse((self.vault / "_Previews").exists(), "notes.py never creates an image or its folder")


# ── determinism ──────────────────────────────────────────────────────────────

class Determinism(NotesCase):
    def tree(self, vault):
        return {p.relative_to(vault).as_posix(): p.read_bytes() for p in sorted(Path(vault).rglob("*")) if p.is_file()}

    def test_the_same_catalog_gives_the_same_bytes_in_any_directory(self):
        self.two_sets()
        self.write()
        other = self.tmp / "elsewhere" / "deeper"
        (other / "catalog").parent.mkdir(parents=True)
        import shutil
        shutil.copytree(self.root / "catalog", other / "catalog")
        self.assertEqual(self.run_notes("write", "--confirm", root=other)[0], bc.EXIT_OK)
        first, second = self.tree(self.vault), self.tree(other / "vault")
        self.assertEqual(first, second)
        blob = b"\n".join(first.values()).decode("utf-8")
        self.assertNotIn(str(self.root), blob)
        self.assertNotIn(str(other), blob)
        self.assertNotIn(os.sep + "Users" + os.sep, blob)
        self.assertIsNone(re.search(r"\b20\d\d-\d\d-\d\dT", blob), "no timestamp")

    def test_the_order_of_catalog_rows_does_not_matter(self):
        self.two_sets()
        self.write()
        path = self.root / "catalog" / "catalog.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        shuffled = copy.deepcopy(data)
        random.Random(7).shuffle(shuffled["sets"])
        random.Random(8).shuffle(shuffled["brushes"])
        random.Random(9).shuffle(shuffled["packs"])
        other = self.tmp / "shuffled"
        (other / "catalog").mkdir(parents=True)
        import shutil
        for item in (self.root / "catalog").iterdir():
            if item.is_dir():
                shutil.copytree(item, other / "catalog" / item.name)
        bc.write_json(other / "catalog" / "catalog.json", shuffled)
        for name in ("textures.json", "containers.json"):
            shutil.copy(self.root / "catalog" / name, other / "catalog" / name)
        self.assertEqual(self.run_notes("write", "--confirm", root=other)[0], bc.EXIT_OK)
        self.assertEqual(self.tree(self.vault), self.tree(other / "vault"))

    def test_render_all_is_a_pure_function_of_the_catalog(self):
        self.two_sets()
        one = notes.render_all(notes.Catalog(self.root / "catalog"))
        two = notes.render_all(notes.Catalog(self.root / "catalog"))
        self.assertEqual(one, two)
        self.assertEqual(list(one), sorted(one))


# ── path safety ──────────────────────────────────────────────────────────────

class PathSafety(NotesCase):
    def test_the_only_files_written_are_under_the_vault(self):
        self.two_sets()
        before = {p.relative_to(self.tmp).as_posix(): p.read_bytes() for p in self.tmp.rglob("*") if p.is_file()}
        self.write()
        after = {p.relative_to(self.tmp).as_posix(): p.read_bytes() for p in self.tmp.rglob("*") if p.is_file()}
        added = set(after) - set(before)
        self.assertTrue(added)
        self.assertTrue(all(name.startswith("brushes/vault/") for name in added), sorted(added))
        self.assertEqual({k: v for k, v in after.items() if k in before}, before, "no existing file changed")

    def test_unsafe_note_paths_in_the_catalog_are_refused_before_anything_is_written(self):
        for bad in ("../escape.md", "02_Vendor_Packs/../../escape.md", "/abs/x.md", "C:/x.md",
                    "02_Vendor_Packs\\demo-set.md", "99_Other/demo-set.md", "02_Vendor_Packs/sub/demo-set.md",
                    "02_Vendor_Packs/Demo Set.md", "02_Vendor_Packs/demo-set.txt", "00_INDEX.md", ""):
            builder = Builder(self.root)
            a = builder.brush("A")
            builder.set("demo-set", [a])
            builder.build()
            path = self.root / "catalog" / "catalog.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["sets"][0]["note"] = bad
            bc.write_json(path, data)
            before = fixtures.tree_digest(self.tmp)
            code, _, err = self.run_notes("write", "--confirm")
            self.assertEqual(code, bc.EXIT_REFUSED, bad)
            self.assertIn("note path", err, bad)
            self.assertEqual(fixtures.tree_digest(self.tmp), before, bad)

    def test_a_bad_set_slug_is_exit_2(self):
        self.two_sets()
        path = self.root / "catalog" / "catalog.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["sets"][0]["set_slug"] = "../evil"
        bc.write_json(path, data)
        self.assertEqual(self.run_notes("write", "--confirm")[0], bc.EXIT_USAGE)

    def test_target_path_refuses_to_leave_the_vault(self):
        self.vault.mkdir()
        with self.assertRaises(notes.NotesError):
            notes.target_path(self.vault, "../outside.md")
        with self.assertRaises(notes.NotesError):
            notes.target_path(self.vault, "02_Vendor_Packs/../../outside.md")
        self.assertEqual(notes.target_path(self.vault, "02_Vendor_Packs/x.md"),
                         (self.vault / "02_Vendor_Packs" / "x.md").resolve())

    def test_a_folder_that_is_a_link_out_of_the_vault_is_refused(self):
        self.two_sets()
        outside = self.tmp / "outside"
        outside.mkdir()
        self.vault.mkdir()
        link = self.vault / "02_Vendor_Packs"
        try:
            os.symlink(outside, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            made = False
            if os.name == "nt":      # a directory junction needs no privilege
                made = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)],
                                      capture_output=True).returncode == 0
            if not made:
                self.skipTest("this account cannot make a symbolic link or a junction")
        code, _, err = self.run_notes("write", "--confirm")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertIn("outside the vault", err)


# ── a catalog built by ingest.py ─────────────────────────────────────────────

class WithARealBuild(fixtures.BrushCase):
    """The standard fixtures library, ingested for real, then noted."""

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "brushes"
        self.lib = fixtures.write_library(self.root / "library")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ingest.main(["build", "--root", str(self.root)]), bc.EXIT_OK)
        self.vault = self.root / "vault"

    def run_notes(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = notes.main([*argv, "--root", str(self.root)])
        return code, out.getvalue(), err.getvalue()

    def test_notes_for_an_ingested_library(self):
        catalog = json.loads((self.root / "catalog" / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["counts"]["notes"], 3)
        code, out, _ = self.run_notes("write")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertFalse(self.vault.exists())
        code, out, _ = self.run_notes("write", "--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("WROTE     8 files", out)
        self.assertEqual(sorted(p.relative_to(self.vault).as_posix() for p in self.vault.rglob("*.md")
                                if p.name != "_index.md"),
                         ["00_INDEX.md", "01_Procreate_Defaults/demo-modern.md", "02_Vendor_Packs/demo-set.md",
                          "03_Loose/demo-pack-loose.md"])
        self.assertIn("WROTE     0 files", self.run_notes("write", "--confirm")[1])
        self.assertEqual(self.run_notes("check")[0], bc.EXIT_OK)
        for row in catalog["sets"]:
            if row["note"]:
                text = (self.vault / row["note"]).read_bytes().decode("utf-8")
                ids = [m.group(1) for m in (ID_LINE.match(l) for l in text.split("\n")) if m]
                homed = [i for i in row["brushes"]
                         if json.loads((self.root / "catalog" / "brushes" / f"{i}.json").read_text(encoding="utf-8"))
                         ["home"]["set_slug"] == row["set_slug"]]
                self.assertEqual(ids, homed, row["set_slug"])
        loose = (self.vault / "03_Loose" / "demo-pack-loose.md").read_bytes().decode("utf-8")
        self.assertIn("## Shared brushes", loose, "the loose copy of Demo Inker is a stub")
        demo = (self.vault / "02_Vendor_Packs" / "demo-set.md").read_bytes().decode("utf-8")
        self.assertIn("## Demo  Pencil", demo, "a doubled space in a name is kept")
        self.assertIn('set_name: "Demo Set "', demo)
        self.assertIn('redistribute: "yes"', demo)
        modern = (self.vault / "01_Procreate_Defaults" / "demo-modern.md").read_bytes().decode("utf-8")
        self.assertIn("library: official", modern)
        self.assertIn("pack_kind: official", modern)

    def test_the_four_name_collision_headings_of_the_fixtures_are_numbered(self):
        self.run_notes("write", "--confirm")
        demo = (self.vault / "02_Vendor_Packs" / "demo-set.md").read_bytes().decode("utf-8")
        headings = [l[3:] for l in demo.split("\n") if l.startswith("## ")]
        self.assertEqual(len(headings), len(set(headings)))
        self.assertTrue(any(h.endswith(" (2)") for h in headings), headings)


# ── the vault's rulebook ─────────────────────────────────────────────────────

class RulebookAgreesWithTheCode(unittest.TestCase):
    """vault/CLAUDE.md is authored. Its facet glossary and its description of a
    brush section must match schema/facets.json and notes.py."""

    @classmethod
    def setUpClass(cls):
        path = BRUSHES / "vault" / "CLAUDE.md"
        cls.text = path.read_text(encoding="utf-8") if path.is_file() else None

    def setUp(self):
        if self.text is None:
            self.skipTest("brushes/vault/CLAUDE.md is not present")

    def test_every_facet_is_in_the_glossary(self):
        facets = json.loads((BRUSHES / "schema" / "facets.json").read_text(encoding="utf-8"))["facets"]
        for name in facets:
            self.assertIn(f"`{name}`", self.text, name)

    def test_the_line_prefixes_and_verbs_are_described(self):
        for prefix in notes.BRUSH_LINES:
            self.assertIn(f"`{prefix}`", self.text, prefix)
        for verb in ("notes.py write", "notes.py check", "--overwrite-generated", "--confirm",
                     "brush_search.py", "brush_tags.py"):
            self.assertIn(verb, self.text, verb)
        for word in ("index", "search", "ask", "similar", "facets", "files", "chunks", "verify", "brush"):
            self.assertIn(f"brush_search.py {word}", self.text, word)

    def test_the_reserved_headings_and_template_names_are_the_codes(self):
        for heading in notes.RESERVED_HEADINGS:
            self.assertIn(heading, self.text)
        self.assertIn(notes.TEMPLATE_NOTE, self.text)
        self.assertIn(notes.CHUNKER_VERSION, self.text)


if __name__ == "__main__":
    unittest.main()
