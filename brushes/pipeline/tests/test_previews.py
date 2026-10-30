"""pipeline/previews.py: the stroke, shape and grain previews, the contact sheets
and the way the measurements come back into the catalog (docs/CONTRACTS.md F5,
F6, F11, F12).

Every test builds a small synthetic library in a temporary folder with
fixtures.py, builds its catalog with ingest.py and renders previews there. None
reads the real library, catalog or vault. The real decoder is png_io's; the
images here are tiny, so the standard-library path is fast.

    python -m unittest discover -s brushes/pipeline/tests -p "test_previews.py"
"""

import contextlib
import hashlib
import io
import json
import re
import struct
import subprocess
import sys
import unittest
import zlib
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import brush_common as bc  # noqa: E402
import fixtures  # noqa: E402
import ingest  # noqa: E402
import png_io  # noqa: E402
import previews  # noqa: E402

SCRIPT = PIPELINE / "previews.py"
PNG = fixtures.PNG_SIGNATURE
TEXTURE_FACETS = ("shape_coverage", "shape_aspect", "shape_midtone", "shape_edge_touch", "grain_mean",
                  "grain_contrast")


def raw_png(width, height, depth, colour, rows):
    """A PNG with the given header and the given raw sample bytes per row
    (filter 0 is added), whatever the header says."""
    body = b"".join(b"\x00" + row for row in rows)
    header = struct.pack(">IIBBBBB", width, height, depth, colour, 0, 0, 0)
    return (PNG + fixtures._chunk(b"IHDR", header) + fixtures._chunk(b"IDAT", zlib.compress(body))
            + fixtures._chunk(b"IEND", b""))


def png16(width, height, paint, colour):
    """A 16-bit grey+alpha (colour 4) or RGBA (colour 6) PNG; paint(x, y) gives
    the 8-bit samples, each written as value * 257."""
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            for value in paint(x, y):
                row += struct.pack(">H", value * 257)
        rows.append(bytes(row))
    return raw_png(width, height, 16, colour, rows)


def ink_png(alpha_value, width=53, height=16, mode="RGBA"):
    """A thumbnail whose alpha is `alpha_value` everywhere (0: no ink at all)."""
    if mode == "RGBA":
        return fixtures.make_png(width, height, "RGBA", lambda x, y: (255, 255, 255, alpha_value))
    return fixtures.make_png(width, height, "LA", lambda x, y: (255, alpha_value))


class PreviewCase(fixtures.BrushCase):
    """A temporary data root with the standard synthetic library and its catalog."""

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "brushes"
        self.library = self.root / "library"
        self.lib = fixtures.write_library(self.library)
        self.catalog = self.root / "catalog"
        self.vault = self.root / "vault"
        self.pre = self.vault / "_Previews"

    # ── commands ──
    def ingest(self, root=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ingest.main(["build", "--root", str(root or self.root)])
        self.assertEqual(code, 0, out.getvalue() + err.getvalue())

    def render(self, *argv, root=None, expect=0):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = previews.main(["render", "--root", str(root or self.root), *argv])
            except SystemExit as exc:
                code = exc.code
        self.assertEqual(code, expect, out.getvalue() + err.getvalue())
        return out.getvalue() + err.getvalue()

    def built(self, *argv):
        """Build the catalog, render with --confirm, return the output."""
        self.ingest()
        return self.render(*argv, "--confirm")

    # ── reading results ──
    def read(self, relative):
        return json.loads((self.catalog / relative).read_text(encoding="utf-8"))

    def records(self):
        return {path.stem: json.loads(path.read_text(encoding="utf-8"))
                for path in sorted((self.catalog / "brushes").glob("b_*.json"))}

    def by_name(self, name, nth=0):
        found = [record for record in self.records().values() if record["name"] == name]
        found.sort(key=lambda record: record["home"]["position"])
        return found[nth]

    def image(self, relative):
        return png_io.read_png((self.vault / relative).read_bytes())

    def previews_digest(self):
        return fixtures.tree_digest(self.pre)

    def written(self, output):
        return int(re.search(r"WROTE\s+(\d+) files changed", output).group(1))

    def set_library_set(self, brushes, *, relative=None, name=None):
        """Replace a container of the library with a set made of `brushes`."""
        relative = relative or self.lib["user_set"]["file"]
        data = fixtures.brushset_file(name or fixtures.USER_SET_NAME, brushes)
        (self.library / relative).write_bytes(data)


# ── pixels ───────────────────────────────────────────────────────────────────

class StrokeMaths(unittest.TestCase):
    def ink(self, width, height, value, box=None):
        left, top, right, bottom = box or (0, 0, width, height)
        pixels = bytearray(width * height)
        for y in range(top, bottom):
            pixels[y * width + left:y * width + right] = bytes((value,)) * (right - left)
        return png_io.Image(width, height, "L", bytes(pixels))

    def test_a_full_size_thumbnail_is_halved_and_stretched(self):
        ink = self.ink(1060, 324, 100, (200, 100, 400, 200))
        pixels, measures = previews.stroke_from_ink(ink)
        self.assertEqual(len(pixels), 530 * 162)
        # hi is the 99.5th percentile of the non-zero ink: all of it is 100
        self.assertEqual((measures["alpha_max"], measures["alpha_hi"]), (100, 100))
        self.assertEqual(measures["gain"], 2.55)
        self.assertEqual(pixels[60 * 530 + 150], 26 + (229 * 255 + 127) // 255)     # ink: 255 on 26
        self.assertEqual(pixels[5 * 530 + 5], 26)                                   # ground
        self.assertEqual(measures["bbox"], [100, 50, 200, 100])
        self.assertEqual(measures["ink_fraction"], round(100 * 50 / (530 * 162), 4))

    def test_a_faint_stroke_is_stretched_from_the_floor(self):
        pixels, measures = previews.stroke_from_ink(self.ink(530, 162, 7, (10, 10, 200, 100)))
        self.assertEqual(measures["alpha_hi"], 16, "the floor of the percentile")
        spread = min(255, (7 * 255 + 8) // 16)
        self.assertEqual(pixels[50 * 530 + 50], 26 + (229 * spread + 127) // 255)
        self.assertEqual(measures["ink_fraction"], 0.0, "no ink over 8")
        self.assertIsNotNone(measures["bbox"], "the box holds any ink")

    def test_a_smaller_image_is_centred_not_scaled(self):
        pixels, measures = previews.stroke_from_ink(self.ink(100, 40, 255))
        self.assertEqual(measures["bbox"], [215, 61, 315, 101])
        self.assertEqual(pixels[81 * 530 + 265], 255)

    def test_the_reduction_is_an_integer_box_mean(self):
        # 3x3 blocks: one of nine is 255, so the mean is (255 + 4) // 9 = 28
        pixels = bytearray(1590 * 486)
        pixels[0] = 255
        _, measures = previews.stroke_from_ink(png_io.Image(1590, 486, "L", bytes(pixels)))
        self.assertEqual(measures["alpha_hi"], 28)
        self.assertEqual(measures["bbox"], [0, 0, 1, 1])

    def test_no_ink_is_none(self):
        self.assertIsNone(previews.stroke_from_ink(self.ink(20, 20, 0)))

    def test_ink_of_an_image_without_alpha_follows_the_border(self):
        light_on_dark = fixtures.make_png(20, 10, "L", lambda x, y: 255 if 5 <= x < 15 and 3 <= y < 7 else 0)
        dark_on_light = fixtures.make_png(20, 10, "L", lambda x, y: 0 if 5 <= x < 15 and 3 <= y < 7 else 255)
        for data in (light_on_dark, dark_on_light):
            ink = previews.ink_of(data)
            self.assertEqual(ink.pixels[5 * 20 + 10], 255)
            self.assertEqual(ink.pixels[0], 0)

    def test_ink_of_alpha_is_the_alpha_channel(self):
        ink = previews.ink_of(ink_png(77, mode="LA"))
        self.assertEqual(set(ink.pixels), {77})
        ink = previews.ink_of(ink_png(0))
        self.assertEqual(set(ink.pixels), {0})

    def test_a_16_bit_thumbnail_is_read(self):
        data = png16(12, 6, lambda x, y: (255, 200 if x > 5 else 0), 4)
        ink = previews.ink_of(data)
        self.assertEqual((ink.width, ink.pixels[5], ink.pixels[6]), (12, 0, 200))


class TileMaths(unittest.TestCase):
    def grey(self, width, height, paint):
        return png_io.Image(width, height, "L", bytes(paint(x, y) for y in range(height) for x in range(width)))

    def test_a_shape_is_reduced_to_fit_and_centred_on_black(self):
        tile = previews.shape_tile(self.grey(512, 512, lambda x, y: 200), False)
        self.assertEqual((tile.width, tile.height, set(tile.pixels)), (256, 256, {200}))
        small = previews.shape_tile(self.grey(100, 60, lambda x, y: 255), False)
        self.assertEqual(small.pixels[128 * 256 + 128], 255)
        self.assertEqual(small.pixels[0], 0)
        self.assertEqual(png_io.bbox(small, 0), (78, 98, 178, 158))

    def test_an_inverted_shape_has_white_for_paint(self):
        # dark mark on white: inverted, the mark is white on black
        shape = self.grey(64, 64, lambda x, y: 20 if 16 <= x < 48 and 16 <= y < 48 else 255)
        plain, inverted = previews.shape_tile(shape, False), previews.shape_tile(shape, True)
        self.assertEqual(inverted.pixels[128 * 256 + 128], 235)
        self.assertEqual(inverted.pixels[0], 0, "the padding stays black")
        self.assertEqual(plain.pixels[128 * 256 + 128], 20)

    def test_shape_stats(self):
        tile = png_io.Image(256, 256, "L", bytes(256 * 256))
        self.assertEqual(previews.shape_stats(tile), {"coverage": 0.0, "aspect": None, "midtone": None,
                                                      "edge_touch": 0.0})
        # a 100 wide, 50 tall block: half hard white, half mid grey
        pixels = bytearray(256 * 256)
        for y in range(100, 150):
            for x in range(78, 178):
                pixels[y * 256 + x] = 255 if x < 128 else 128
        stats = previews.shape_stats(png_io.Image(256, 256, "L", bytes(pixels)))
        self.assertEqual(stats["aspect"], 2.0)
        self.assertEqual(stats["midtone"], 0.5)
        self.assertEqual(stats["coverage"], round((2500 * 255 + 2500 * 128) / (65536 * 255), 6))
        self.assertEqual(stats["edge_touch"], 0.0)
        edge = bytes([255] * 256 + [0] * (256 * 255))
        self.assertGreater(previews.shape_stats(png_io.Image(256, 256, "L", edge))["edge_touch"], 0.05)

    def test_grain_tile_is_the_centre_at_one_to_one_and_tiles_when_small(self):
        big = self.grey(400, 300, lambda x, y: (x + y) % 256)
        tile = previews.grain_tile(big)
        self.assertEqual(tile.pixels[0], (72 + 22) % 256)
        small = previews.grain_tile(self.grey(8, 8, lambda x, y: 255 if x < 4 else 0))
        self.assertEqual((small.width, small.height), (256, 256))
        self.assertIn(small.pixels[0:8], (bytes([255] * 4 + [0] * 4), bytes([0] * 4 + [255] * 4)))

    def test_grain_stats(self):
        flat = png_io.Image(256, 256, "L", bytes([128]) * 65536)
        self.assertEqual(previews.grain_stats(flat), {"mean": round(128 / 255, 6), "contrast": 0.0})
        halves = png_io.Image(256, 256, "L", bytes([0, 255]) * 32768)
        stats = previews.grain_stats(halves)
        self.assertEqual(stats["mean"], 0.5)
        self.assertEqual(stats["contrast"], 0.5)


class FontAndSheetMaths(unittest.TestCase):
    def test_the_font_has_every_printable_ascii_character(self):
        self.assertEqual(len(previews.FONT), 95)
        self.assertEqual(previews.FONT[ord("A") - 32].hex(), "7e1111117e")
        self.assertEqual(previews.FONT[0], bytes(5))
        self.assertEqual(len(set(previews.FONT)), 95, "no two characters look the same")

    def test_ascii_fold_keeps_position_and_id_readable(self):
        self.assertEqual(previews.ascii_fold("Broken Conté"), "Broken Conte")
        self.assertEqual(previews.ascii_fold("浓墨 Modern\t1"), " Modern 1")

    def test_draw_text_is_clipped(self):
        canvas = bytearray(20 * 9)
        previews.draw_text(canvas, 20, 15, 4, "WWWW", scale=2, limit=19)
        self.assertEqual(len(canvas), 180)
        self.assertEqual(max(canvas), 255)
        for y in range(9):
            self.assertEqual(canvas[y * 20 + 19], 0, "nothing at or past the limit")

    def test_a_sheet_has_the_size_of_f6(self):
        record = {"id": "b_0123456789ab", "display_name": "N" * 50, "preview": {}, "shape": {}, "grain": {}}
        pixels = previews.compose_sheet([(1, record)], previews.Tiles(Path("nowhere")))
        self.assertEqual(len(pixels), 802 * 1496)
        self.assertEqual(pixels[-1], 16, "background 16")
        self.assertEqual(pixels[4 * 802 + 4], 64, "the label bar")

    def test_the_placeholder_is_a_stroke_tile(self):
        tile = previews.placeholder_stroke("Brush-Preset-Hard.png")
        self.assertEqual(len(tile), 530 * 162)
        self.assertGreater(len(set(tile)), 2)


# ── what render writes ───────────────────────────────────────────────────────

class DryRun(PreviewCase):
    def test_a_dry_run_writes_nothing(self):
        self.ingest()
        before = fixtures.tree_digest(self.root)
        out = self.render()
        self.assertEqual(fixtures.tree_digest(self.root), before)
        self.assertFalse(self.pre.exists())
        self.assertIn("DRY RUN   nothing is written without --confirm.", out)
        self.assertIn("STROKES   8 of 8 to make", out)
        self.assertIn("bundled textures get no tile", out)

    def test_a_dry_run_needs_no_library(self):
        self.ingest()
        out = self.render("--library", str(self.tmp / "no-library"))
        self.assertIn("DRY RUN", out)

    def test_a_dry_run_of_sheets_only_reads_the_vault_and_writes_nothing(self):
        self.built("--no-sheets")
        before = fixtures.tree_digest(self.root)
        out = self.render("--sheets-only")
        self.assertEqual(fixtures.tree_digest(self.root), before)
        self.assertIn("3 of them would be written", out)


class WhatIsWritten(PreviewCase):
    def setUp(self):
        super().setUp()
        self.out = self.built()
        self.records_after = self.records()

    def test_the_files_of_f6(self):
        for brush_id, record in self.records_after.items():
            home = record["home"]["set_slug"]
            self.assertEqual(record["preview"]["stroke"], f"_Previews/{home}/{brush_id}.stroke.png")
            img = self.image(record["preview"]["stroke"])
            self.assertEqual((img.width, img.height, img.mode), (530, 162, "L"), brush_id)
            self.assertEqual(img.chunks, ("IHDR", "IDAT", "IEND"), "no alpha, no extras")
        shapes = list((self.pre / "_textures").glob("*.shape.png"))
        grains = list((self.pre / "_textures").glob("*.grain.png"))
        self.assertTrue(shapes and grains)
        for path in shapes + grains:
            img = png_io.read_png(path.read_bytes())
            self.assertEqual((img.width, img.height, img.mode), (256, 256, "L"), path.name)
        for path in shapes:
            self.assertRegex(path.name, r"^t_[0-9a-f]{12}\.[ni]\.shape\.png$")
        for path in grains:
            self.assertRegex(path.name, r"^t_[0-9a-f]{12}\.grain\.png$")
        self.assertTrue((self.pre / "manifest.json").is_file())
        sheets = sorted(path.relative_to(self.pre).as_posix() for path in (self.pre / "_sheets").rglob("*"))
        self.assertIn("_sheets/demo-set/sheet-01.png", sheets)
        self.assertIn("_sheets/demo-set/sheets.json", sheets)
        self.assertFalse(list(self.pre.rglob("*.tmp")))

    def test_a_shape_is_made_for_the_polarity_a_brush_uses(self):
        for record in self.records_after.values():
            tile = record["preview"]["shape"]
            if record["shape"]["texture_id"] is None:
                self.assertIsNone(tile)
            else:
                side = "i" if record["shape"]["inverted"] else "n"
                self.assertTrue(tile.endswith(f".{side}.shape.png"), tile)

    def test_the_manifest_records_source_version_and_pixels(self):
        manifest = json.loads((self.pre / "manifest.json").read_text(encoding="utf-8"))
        textures = self.read("textures.json")
        thumbnails = self.read("thumbnails.json")
        self.assertEqual(set(manifest), {entry["stroke"] for entry in thumbnails.values()}
                         | {path for held in textures.values() for path in (held["shape_tiles"] or {}).values() if path}
                         | {held["grain_tile"] for held in textures.values() if held["grain_tile"]})
        for rel, entry in manifest.items():
            self.assertEqual(set(entry), {"source_sha256", "preview_version", "pixel_sha256"}, rel)
            self.assertEqual(entry["preview_version"], previews.PREVIEW_VERSION)
            pixels = self.image(rel).pixels
            self.assertEqual(entry["pixel_sha256"], hashlib.sha256(pixels).hexdigest(), rel)
        for brush_id, entry in thumbnails.items():
            record = self.records_after[brush_id]
            if entry["stroke_source"] == "thumbnail":
                self.assertEqual(manifest[entry["stroke"]]["source_sha256"], record["thumbnail"]["sha256"])
        for texture_id, held in textures.items():
            for path in [p for p in (held["shape_tiles"] or {}).values() if p] + [held["grain_tile"]]:
                if path:
                    self.assertEqual(manifest[path]["source_sha256"], held["sha256"], path)

    def test_thumbnails_json(self):
        thumbnails = self.read("thumbnails.json")
        self.assertEqual(set(thumbnails), set(self.records_after))
        keys = {"source_sha256", "stroke", "stroke_source", "alpha_max", "alpha_hi", "gain", "ink_fraction", "bbox"}
        for brush_id, entry in thumbnails.items():
            self.assertEqual(set(entry), keys, brush_id)
            self.assertIn(entry["stroke_source"], ("thumbnail", "reset-thumbnail", "none"))
        made = thumbnails[self.by_name("Demo Inker")["id"]]
        self.assertEqual(made["stroke_source"], "thumbnail")
        self.assertEqual(made["alpha_hi"], made["alpha_max"])
        self.assertEqual(made["gain"], round(255 / made["alpha_hi"], 4))
        self.assertEqual(len(made["bbox"]), 4)

    def test_textures_json_has_tiles_and_statistics(self):
        textures = self.read("textures.json")
        record = self.by_name("Demo Inker")
        shape = textures[record["shape"]["texture_id"]]
        grain = textures[record["grain"]["texture_id"]]
        self.assertEqual(set(shape["stats"]["shape"]["n"]), {"coverage", "aspect", "midtone", "edge_touch"})
        self.assertEqual(set(grain["stats"]["grain"]), {"mean", "contrast"})
        self.assertIsNone(shape["stats"]["grain"])
        self.assertEqual(shape["shape_tiles"]["i"], None)
        self.assertEqual(grain["grain_tile"], record["preview"]["grain"])
        for held in textures.values():
            if held["used_as"] == ["grain"]:
                self.assertEqual(held["shape_tiles"], {"n": None, "i": None})

    def test_a_texture_the_archive_only_names_gets_no_tile(self):
        pencil = self.by_name("Demo  Pencil")
        self.assertEqual(pencil["shape"]["source"], "bundled")
        self.assertIsNone(pencil["shape"]["texture_id"])
        self.assertIsNone(pencil["preview"]["shape"])
        self.assertEqual(pencil["preview"]["shape_source"], "bundled")
        self.assertIsNone(pencil["preview"]["grain"])
        self.assertEqual(pencil["preview"]["grain_source"], "blank")
        for name in ("shape_coverage", "shape_aspect", "shape_midtone", "shape_edge_touch",
                     "grain_mean", "grain_contrast"):
            self.assertIsNone(pencil["facets"][name], name)
        # no tile was made for a name: only ids of real texture bytes are in _textures
        ids = {path.name.split(".")[0] for path in (self.pre / "_textures").iterdir()}
        self.assertEqual(ids, {tid for tid, held in self.read("textures.json").items()
                               if any((held["shape_tiles"] or {}).values()) or held["grain_tile"]})

    def test_the_facets_of_a_measured_brush(self):
        record = self.by_name("Demo Inker")
        textures = self.read("textures.json")
        shape = textures[record["shape"]["texture_id"]]["stats"]["shape"]["n"]
        grain = textures[record["grain"]["texture_id"]]["stats"]["grain"]
        facets = record["facets"]
        self.assertEqual(facets["shape_coverage"], round(shape["coverage"], 4))
        self.assertEqual(facets["shape_aspect"], round(shape["aspect"], 4))
        self.assertEqual(facets["shape_midtone"], round(shape["midtone"], 4))
        self.assertEqual(facets["shape_edge_touch"], round(shape["edge_touch"], 4))
        self.assertEqual(facets["grain_mean"], round(grain["mean"], 4))
        self.assertEqual(facets["grain_contrast"], round(grain["contrast"], 4))
        rules = ingest.load_facet_rules()
        self.assertIn("grain-" + ingest.class_of(grain["contrast"], rules["facets"]["grain_contrast"]["classes"]),
                      record["facet_words"])
        self.assertIn("shape-" + ingest.class_of(shape["aspect"], rules["facets"]["shape_aspect"]["classes"]),
                      record["facet_words"])
        self.assertTrue(facets["has_grain"])

    def test_a_brush_with_no_grain_has_no_grain_measures(self):
        record = self.by_name("Broken Conté")
        self.assertEqual(record["grain"]["source"], "none")
        self.assertFalse(record["facets"]["has_grain"])
        self.assertIsNone(record["facets"]["grain_contrast"])

    def test_the_catalog_rows_are_copies_of_the_records(self):
        catalog = self.read("catalog.json")
        for row in catalog["brushes"]:
            record = self.records_after[row["id"]]
            for key in ("facets", "facet_words", "preview"):
                self.assertEqual(row[key], record[key], (row["id"], key))
        self.assertEqual(catalog["counts"]["textures"], len(self.read("textures.json")))

    def test_only_the_three_fields_of_a_record_changed(self):
        # a second catalog built without previews, against the one after them
        other = self.tmp / "other"
        fixtures.write_library(other / "library")
        self.ingest(other)
        for brush_id, record in self.records_after.items():
            plain = json.loads((other / "catalog" / "brushes" / f"{brush_id}.json").read_text(encoding="utf-8"))
            for key in record:
                if key not in ("facets", "facet_words", "preview"):
                    self.assertEqual(record[key], plain[key], (brush_id, key))

    def test_the_secondary_texture_of_a_dual_brush_has_a_tile(self):
        dual = self.by_name("Modern Dual")
        texture_id = dual["secondary"]["shape"]["texture_id"]
        self.assertIsNotNone(texture_id)
        tile = self.read("textures.json")[texture_id]["shape_tiles"]
        self.assertTrue(any(tile.values()))

    def test_the_report(self):
        self.assertRegex(self.out, r"WROTE\s+\d+ files changed")
        self.assertIn("PREVIEWS", self.out)
        for kind in ("stroke", "shape", "grain"):
            self.assertRegex(self.out, rf"\n\s+{kind}\s+\d+ files\s+[\d,]+ bytes")
        self.assertIn("tracked", self.out)
        self.assertNotIn("WARNING", self.out)
        self.assertNotIn("ORPHANS", self.out)

    def test_every_tracked_file_is_within_the_limits_of_f6(self):
        kinds, files = previews.inventory(self.vault)
        for rel in files:
            if previews.kind_of(rel) in ("stroke", "shape", "grain"):
                self.assertLessEqual((self.vault / rel).stat().st_size, previews.PREVIEW_KB * 1024, rel)
        tracked = sum(kinds[k][1] for k in ("stroke", "shape", "grain", "manifest"))
        self.assertLess(tracked, previews.PREVIEWS_TOTAL_MB * 1024 * 1024)


class Strokes(PreviewCase):
    def test_a_brush_without_a_thumbnail_gets_a_placeholder(self):
        self.built()
        record = self.by_name("Modern Plain")
        self.assertFalse(record["thumbnail"]["present"])
        entry = self.read("thumbnails.json")[record["id"]]
        self.assertEqual(entry["stroke_source"], "none")
        self.assertIsNone(entry["source_sha256"])
        self.assertIsNone(entry["gain"])
        self.assertEqual(record["preview"]["stroke_source"], "none")
        self.assertIn("no-thumbnail", record["facet_words"])
        self.assertEqual(self.image(record["preview"]["stroke"]).width, 530)

    def test_a_thumbnail_without_ink_falls_back_to_the_reset_thumbnail(self):
        dead = fixtures.make_brush("Blank Both", "modern", number=22, reset=True, thumbnail=ink_png(0))
        dead.members = [(path, ink_png(0) if path.endswith("QuickLook/Thumbnail.png") else data)
                        for path, data in dead.members]
        (self.library / "user" / "demo-pack" / "Extra.brushset").write_bytes(
            fixtures.brushset_file("Extra Set", [dead]))
        self.built()
        record = self.by_name("Blank Both")
        entry = self.read("thumbnails.json")[record["id"]]
        self.assertEqual(entry["stroke_source"], "none", "no ink in either thumbnail")
        self.assertEqual(entry["source_sha256"], record["thumbnail"]["sha256"])
        self.assertEqual(record["preview"]["stroke_source"], "none")
        self.assertIn("no-thumbnail", record["facet_words"])

    def test_reset_thumbnail_is_used_when_the_live_one_has_no_ink(self):
        live = fixtures.make_brush("Live Blank", "modern", number=31, reset=True)
        live.members = [(path, ink_png(0) if path == fixtures.THUMBNAIL else data) for path, data in live.members]
        (self.library / "user" / "demo-pack" / "Extra.brushset").write_bytes(
            fixtures.brushset_file("Extra Set", [live]))
        self.built()
        record = self.by_name("Live Blank")
        entry = self.read("thumbnails.json")[record["id"]]
        self.assertEqual(entry["stroke_source"], "reset-thumbnail")
        self.assertEqual(entry["source_sha256"], record["reset"]["thumbnail_sha256"])
        self.assertEqual(record["preview"]["stroke_source"], "reset-thumbnail")
        self.assertNotIn("no-thumbnail", record["facet_words"])
        self.assertIsNotNone(entry["gain"])

    def test_a_16_bit_and_an_unreadable_thumbnail(self):
        sixteen = fixtures.make_brush("Sixteen", "modern", number=41,
                                      thumbnail=png16(40, 12, lambda x, y: (255, 150), 4))
        broken = fixtures.make_brush("Broken Png", "modern", number=42, thumbnail=b"not a png at all")
        (self.library / "user" / "demo-pack" / "Extra.brushset").write_bytes(
            fixtures.brushset_file("Extra Set", [sixteen, broken]))
        out = self.built()
        entries = self.read("thumbnails.json")
        self.assertEqual(entries[self.by_name("Sixteen")["id"]]["stroke_source"], "thumbnail")
        self.assertEqual(entries[self.by_name("Sixteen")["id"]]["alpha_max"], 150)
        record = self.by_name("Broken Png")
        self.assertEqual(entries[record["id"]]["stroke_source"], "none")
        self.assertEqual(entries[record["id"]]["source_sha256"], record["thumbnail"]["sha256"],
                         "the file it was tried from")
        self.assertIn("is not a usable PNG", out)
        self.assertEqual(record["preview"]["stroke_source"], "none")

    def test_a_grey_alpha_thumbnail_is_read(self):
        self.built()
        earth = self.by_name("Modern Earth")
        entry = self.read("thumbnails.json")[earth["id"]]
        self.assertEqual((entry["stroke_source"], earth["thumbnail"]["color_type"]), ("thumbnail", 4))


class Hostile(PreviewCase):
    def extra(self, *brushes):
        (self.library / "user" / "demo-pack" / "Extra.brushset").write_bytes(
            fixtures.brushset_file("Extra Set", list(brushes)))

    def test_zero_size_images_make_no_tile_and_no_failure(self):
        zero = raw_png(0, 0, 8, 0, [])
        self.extra(fixtures.make_brush("Zero Shape", "modern", number=51, shape=zero, grain=zero))
        out = self.built()
        record = self.by_name("Zero Shape")
        self.assertIsNone(record["preview"]["shape"])
        self.assertIsNone(record["preview"]["grain"])
        self.assertIsNone(record["facets"]["shape_coverage"])
        self.assertIsNotNone(record["preview"]["stroke"], "its stroke is still made")
        self.assertIn("is not usable", out)
        self.assertNotIn("REFUSED", out)

    def test_a_pixel_bomb_is_refused_from_the_header_and_not_inflated(self):
        bomb = raw_png(30000, 30000, 8, 0, [b"\x00"])
        self.extra(fixtures.make_brush("Bomb", "modern", number=52, shape=bomb))
        out = self.built()
        self.assertIsNone(self.by_name("Bomb")["preview"]["shape"])
        self.assertIn("png_pixels", out)

    def test_colour_images_are_taken_by_luminance(self):
        rgb = fixtures.make_png(40, 40, "RGB", lambda x, y: (200, 200, 200) if 10 <= x < 30 else (0, 0, 0))
        rgba = fixtures.make_png(40, 40, "RGBA", lambda x, y: (255, 255, 255, 128))
        self.extra(fixtures.make_brush("Colour Mix", "modern", number=53, shape=rgb, grain=rgba))
        self.built()
        record = self.by_name("Colour Mix")
        shape = self.image(record["preview"]["shape"])
        grain = self.image(record["preview"]["grain"])
        self.assertEqual((shape.mode, grain.mode), ("L", "L"))
        self.assertEqual(shape.pixels[128 * 256 + 128], 200)
        self.assertEqual(set(grain.pixels), {128}, "luminance times alpha over black")
        self.assertEqual(record["facets"]["grain_contrast"], 0.0)

    def test_a_16_bit_texture_is_read(self):
        sixteen = png16(24, 24, lambda x, y: (255 if x < 12 else 0, 255), 4)
        self.extra(fixtures.make_brush("Deep Shape", "modern", number=54, shape=sixteen))
        self.built()
        record = self.by_name("Deep Shape")
        self.assertIsNotNone(record["preview"]["shape"])
        self.assertEqual(self.read("textures.json")[record["shape"]["texture_id"]]["stats"]["shape"]["n"]["aspect"], 0.5)

    def test_a_catalog_older_than_the_library_is_exit_1_and_nothing_wrong_is_written(self):
        self.ingest()
        other = [fixtures.make_brush("Someone Else", number=61)]
        self.set_library_set(other)
        out = self.render("--confirm", "--no-sheets", expect=1)
        self.assertIn("FAILED", out)
        self.assertIn("is no longer in its container", out)
        self.assertIn("REFUSED", out)
        self.assertFalse((self.pre / "demo-set").exists(), "no preview for a brush that is no longer there")

    def test_a_container_that_is_not_a_zip_is_exit_1(self):
        self.ingest()
        (self.library / self.lib["user_set"]["file"]).write_bytes(b"this is not a zip")
        out = self.render("--confirm", expect=1)
        self.assertIn("it cannot be read", out)

    def test_a_git_lfs_pointer_is_exit_2(self):
        self.ingest()
        (self.library / self.lib["user_set"]["file"]).write_bytes(fixtures.LFS_POINTER)
        out = self.render("--confirm", expect=2)
        self.assertIn("git lfs pull", out)


class Idempotence(PreviewCase):
    def test_a_second_run_writes_nothing(self):
        self.built()
        digest = fixtures.tree_digest(self.root)
        out = self.render("--confirm")
        self.assertEqual(self.written(out), 0)
        self.assertIn("STROKES   0 of 8 to make", out)
        self.assertIn("LIBRARY   0 containers to read", out)
        self.assertEqual(fixtures.tree_digest(self.root), digest)

    def test_two_roots_give_the_same_bytes(self):
        self.built()
        other = self.tmp / "other"
        fixtures.write_library(other / "library")
        self.ingest(other)
        self.render("--confirm", root=other)
        for part in ("catalog", "vault"):
            self.assertEqual(fixtures.tree_digest(self.root / part), fixtures.tree_digest(other / part), part)

    def test_no_clock_and_no_absolute_path_in_what_is_written(self):
        self.built()
        text = ""
        for path in [self.catalog / "thumbnails.json", self.catalog / "textures.json"] + sorted(self.pre.rglob("*.json")):
            text += path.read_text(encoding="utf-8")
        self.assertIn("_Previews/", text)
        self.assertNotIn(str(self.root), text)
        self.assertNotIn(str(self.tmp), text)
        self.assertNotIn("\\\\", text)
        self.assertNotRegex(text, r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

    def test_ingest_build_keeps_what_was_measured(self):
        self.built()
        before = fixtures.tree_digest(self.catalog)
        self.ingest()
        self.assertEqual(fixtures.tree_digest(self.catalog), before)

    def test_a_missing_manifest_is_rebuilt_without_rewriting_an_image(self):
        self.built()
        (self.pre / "manifest.json").unlink()
        out = self.render("--confirm")
        wrote = next(line for line in out.splitlines() if line.startswith("WROTE"))
        self.assertIn("1 manifest", wrote)
        self.assertNotRegex(wrote, r"\d+ (stroke|shape|grain)\b")
        self.assertEqual(self.written(out), 1)

    def test_a_missing_file_is_made_again(self):
        self.built()
        victim = next(self.pre.glob("demo-set/*.stroke.png"))
        original = victim.read_bytes()
        victim.unlink()
        out = self.render("--confirm")
        self.assertIn("1 missing", out)
        self.assertEqual(victim.read_bytes(), original)

    def test_a_changed_thumbnail_is_made_again_and_nothing_else(self):
        self.built()
        brushes = fixtures.standard_user_brushes()
        brushes[0] = fixtures.make_brush("Demo Inker", number=1, thumbnail=ink_png(90, 80, 20))
        self.set_library_set(brushes)
        brushes_loose = (self.library / self.lib["loose"][0]["file"])
        brushes_loose.write_bytes(fixtures.brush_file(brushes[0]))
        self.ingest()
        out = self.render("--confirm")
        self.assertIn("STROKES   1 of 8 to make (1 changed)", out)
        record = self.by_name("Demo Inker")
        self.assertEqual(self.read("thumbnails.json")[record["id"]]["source_sha256"], record["thumbnail"]["sha256"])

    def test_a_version_bump_changes_the_manifest_not_the_bytes(self):
        self.built()
        images = fixtures.tree_digest(self.pre / "_textures")
        with mock.patch.object(previews, "PREVIEW_VERSION", 2):
            out = self.render("--confirm")
        self.assertIn("(8 changed)", out)
        manifest = json.loads((self.pre / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual({entry["preview_version"] for entry in manifest.values()}, {2})
        self.assertEqual(fixtures.tree_digest(self.pre / "_textures"), images)


class Selection(PreviewCase):
    def test_only_a_set_slug(self):
        self.ingest()
        out = self.render("--only", "demo-set", "--confirm")
        self.assertIn("STROKES   4 of 4 to make", out)
        self.assertTrue(list(self.pre.glob("demo-set/*.stroke.png")))
        self.assertFalse((self.pre / "demo-modern").exists())
        self.assertEqual(len(self.read("thumbnails.json")), 4)
        records = self.records()
        for record in records.values():
            home = record["home"]["set_slug"]
            self.assertEqual(record["preview"]["stroke"] is not None, home == "demo-set", record["name"])
        self.assertFalse((self.pre / "_sheets" / "demo-modern").exists())
        self.assertTrue((self.pre / "_sheets" / "demo-set" / "sheets.json").is_file())

    def test_only_a_pack_id_then_the_rest_adds_up_to_a_full_run(self):
        self.ingest()
        self.render("--only", fixtures.OFFICIAL_PACK, "--confirm")
        self.assertTrue(list(self.pre.glob("demo-modern/*.stroke.png")))
        self.assertFalse((self.pre / "demo-set").exists())
        self.render("--confirm")
        other = self.tmp / "other"
        fixtures.write_library(other / "library")
        self.ingest(other)
        self.render("--confirm", root=other)
        for part in ("catalog", "vault"):
            self.assertEqual(fixtures.tree_digest(self.root / part), fixtures.tree_digest(other / part), part)

    def test_an_unknown_only_is_exit_2(self):
        self.ingest()
        out = self.render("--only", "no-such-set", expect=2)
        self.assertIn("no set slug or pack id", out)
        self.assertFalse(self.pre.exists())


class Force(PreviewCase):
    def test_force_restores_a_file_the_manifest_vouches_for(self):
        self.built()
        victim = next(self.pre.glob("demo-set/*.stroke.png"))
        original = victim.read_bytes()
        victim.write_bytes(b"damaged")
        out = self.render("--confirm", "--no-sheets")
        self.assertEqual(victim.read_bytes(), b"damaged", "no churn: the manifest says it is current")
        self.assertEqual(self.written(out), 0)
        out = self.render("--force", "--confirm", "--no-sheets")
        self.assertEqual(victim.read_bytes(), original)
        self.assertIn("forced", out)
        self.assertEqual(self.written(out), 1)

    def test_force_with_nothing_damaged_writes_nothing(self):
        self.built()
        digest = fixtures.tree_digest(self.root)
        out = self.render("--force", "--confirm")
        self.assertEqual(self.written(out), 0)
        self.assertEqual(fixtures.tree_digest(self.root), digest)

    def test_a_dry_run_with_force_plans_everything(self):
        self.built()
        out = self.render("--force")
        self.assertIn("STROKES   8 of 8 to make (8 forced)", out)


class Sheets(PreviewCase):
    def test_no_sheets(self):
        self.built("--no-sheets")
        self.assertFalse((self.pre / "_sheets").exists())
        self.assertTrue(list(self.pre.glob("demo-set/*.stroke.png")))

    def test_sheets_only_needs_no_library_and_touches_no_catalog(self):
        self.built("--no-sheets")
        catalog = fixtures.tree_digest(self.catalog)
        tracked = fixtures.tree_digest(self.pre / "_textures")
        out = self.render("--sheets-only", "--confirm", "--library", str(self.tmp / "no-library"))
        self.assertEqual(fixtures.tree_digest(self.catalog), catalog)
        self.assertEqual(fixtures.tree_digest(self.pre / "_textures"), tracked)
        self.assertIn("6 files changed", out)
        again = self.render("--sheets-only", "--confirm", "--library", str(self.tmp / "no-library"))
        self.assertEqual(self.written(again), 0)

    def test_the_two_flags_exclude_each_other(self):
        self.ingest()
        out = self.render("--sheets-only", "--no-sheets", expect=2)
        self.assertIn("cancel each other out", out)

    def test_a_sheet_and_its_list(self):
        self.built()
        sheet = self.image("_Previews/_sheets/demo-set/sheet-01.png")
        self.assertEqual((sheet.width, sheet.height, sheet.mode), (802, 1496, "L"))
        listing = json.loads((self.pre / "_sheets" / "demo-set" / "sheets.json").read_text(encoding="utf-8"))
        self.assertEqual(listing["schema"], "rosw-brushes-sheets/1")
        self.assertEqual(listing["set_slug"], "demo-set")
        cells = listing["sheets"][0]["cells"]
        self.assertEqual([cell["n"] for cell in cells], [1, 2, 3, 4])
        self.assertEqual(set(cells[0]), {"n", "id", "name", "stroke_source", "shape_source", "grain_source"})
        self.assertEqual((cells[1]["shape_source"], cells[1]["grain_source"]), ("bundled", "blank"))
        self.assertEqual(cells[0]["id"], self.records()[cells[0]["id"]]["id"])

    def test_a_pseudo_set_without_a_home_brush_has_no_sheet(self):
        (self.library / self.lib["loose"][1]["file"]).unlink()      # only the repeat of a set member is left
        self.built()
        catalog = self.read("catalog.json")
        rows = {row["set_slug"]: row for row in catalog["sets"]}
        self.assertIsNone(rows["demo-pack-loose"]["note"])
        for slug, row in rows.items():
            self.assertEqual((self.pre / "_sheets" / slug / "sheets.json").is_file(), bool(row["note"]), slug)

    def test_a_set_of_more_than_eight_has_more_sheets(self):
        many = [fixtures.make_brush(f"Many {n:02d}", "modern", number=100 + n) for n in range(11)]
        (self.library / "user" / "demo-pack" / "Many.brushset").write_bytes(fixtures.brushset_file("Many", many))
        self.built()
        slug = ingest.identity.slugify("Many")
        listing = json.loads((self.pre / "_sheets" / slug / "sheets.json").read_text(encoding="utf-8"))
        self.assertEqual([len(sheet["cells"]) for sheet in listing["sheets"]], [8, 3])
        self.assertEqual([sheet["file"] for sheet in listing["sheets"]], ["sheet-01.png", "sheet-02.png"])
        self.assertEqual(listing["sheets"][1]["cells"][0]["n"], 9)


class LocalPacks(PreviewCase):
    def test_a_pack_that_does_not_publish_previews_goes_to_local(self):
        sources = json.loads((self.library / "sources.json").read_text(encoding="utf-8"))
        sources["packs"][0]["publish_previews"] = False
        self.library.joinpath("sources.json").write_text(json.dumps(sources), encoding="utf-8")
        self.built()
        record = self.by_name("Demo Inker")
        self.assertTrue(record["preview"]["stroke"].startswith("_Previews/_local/demo-set/"), record["preview"])
        self.assertTrue((self.vault / record["preview"]["stroke"]).is_file())
        self.assertTrue(record["preview"]["grain"].startswith("_Previews/_local/_textures/"))
        official = self.by_name("Modern Plain")
        self.assertFalse(official["preview"]["stroke"].startswith("_Previews/_local"))
        public = json.loads((self.pre / "manifest.json").read_text(encoding="utf-8"))
        local = json.loads((self.pre / "_local" / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(local and all(key.startswith("_Previews/_local/") for key in local))
        self.assertFalse(any(key.startswith("_Previews/_local/") for key in public))
        self.assertFalse(list((self.pre / "demo-set").glob("*")) if (self.pre / "demo-set").exists() else [])

    def test_a_second_run_of_a_local_pack_writes_nothing(self):
        sources = json.loads((self.library / "sources.json").read_text(encoding="utf-8"))
        sources["packs"][0]["publish_previews"] = False
        self.library.joinpath("sources.json").write_text(json.dumps(sources), encoding="utf-8")
        self.built()
        self.assertEqual(self.written(self.render("--confirm")), 0)


class Pillow(PreviewCase):
    @unittest.skipUnless(png_io.HAVE_PIL, "PIL is not installed")
    def test_the_standard_library_path_writes_the_same_bytes(self):
        self.built()
        other = self.tmp / "stdlib"
        fixtures.write_library(other / "library")
        self.ingest(other)
        self.render("--stdlib", "--confirm", root=other)
        self.assertTrue(png_io.HAVE_PIL, "--stdlib is for one run only")
        for part in ("catalog", "vault"):
            self.assertEqual(fixtures.tree_digest(self.root / part), fixtures.tree_digest(other / part), part)

    def test_stdlib_switches_pil_off_for_the_run_only(self):
        self.ingest()
        seen = []
        real = previews.run_render

        def spy(*args, **kwargs):
            seen.append(png_io.HAVE_PIL)
            return real(*args, **kwargs)

        held = png_io.HAVE_PIL
        with mock.patch.object(previews, "run_render", spy):
            self.render("--stdlib")
        self.assertEqual(seen, [False])
        self.assertEqual(png_io.HAVE_PIL, held)


class CommandLine(PreviewCase):
    def run_script(self, *argv):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *argv], capture_output=True, text=True,
                              encoding="utf-8", cwd=str(self.tmp))

    def test_the_parser_has_the_flags_of_f11(self):
        parser = previews.build_parser()
        verbs = next(action for action in parser._actions if isinstance(action.choices, dict))
        self.assertEqual(list(verbs.choices), ["render"])
        flags = {flag for action in verbs.choices["render"]._actions for flag in action.option_strings}
        for flag in ("--only", "--force", "--no-sheets", "--sheets-only", "--stdlib", "--confirm"):
            self.assertIn(flag, flags)
        args = parser.parse_args(["render", "--only", "x", "--force", "--no-sheets", "--stdlib", "--confirm"])
        self.assertEqual((args.only, args.force, args.no_sheets, args.stdlib, args.confirm),
                         ("x", True, True, True, True))
        for flag in bc.FLAGS.values():
            self.assertIn(flag, flags)

    def test_a_dry_run_through_the_script(self):
        self.ingest()
        result = self.run_script("render", "--root", str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN   nothing is written without --confirm.", result.stdout)
        self.assertFalse(self.pre.exists())

    def test_confirm_through_the_script_then_nothing(self):
        self.ingest()
        first = self.run_script("render", "--root", str(self.root), "--confirm")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        second = self.run_script("render", "--root", str(self.root), "--confirm")
        self.assertEqual(second.returncode, 0)
        self.assertEqual(self.written(second.stdout), 0)

    def test_no_verb_and_a_bad_flag_are_exit_2(self):
        self.assertEqual(self.run_script().returncode, 2)
        self.assertEqual(self.run_script("render", "--nonsense").returncode, 2)

    def test_no_catalog_is_exit_2(self):
        result = self.run_script("render", "--root", str(self.tmp / "empty"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("ingest.py build", result.stderr)

    def test_an_empty_catalog_is_exit_2(self):
        self.ingest()
        for path in (self.catalog / "brushes").glob("*.json"):
            path.unlink()
        self.render(expect=2)

    def test_a_catalog_that_is_not_json_is_exit_2(self):
        self.ingest()
        (self.catalog / "catalog.json").write_text("{not json", encoding="utf-8")
        out = self.render(expect=2)
        self.assertIn("cannot be read as JSON", out)

    def test_a_confirm_that_needs_the_library_and_has_none_is_exit_2(self):
        self.ingest()
        out = self.render("--confirm", "--library", str(self.tmp / "no-library"), expect=2)
        self.assertIn("there is no library folder", out)
        self.assertFalse((self.pre / "demo-set").exists())

    def test_the_script_starts_with_its_own_folder_on_the_path(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("sys.path.insert(0, str(Path(__file__).resolve().parent))", text)
        self.assertTrue(text.rstrip().endswith("raise SystemExit(main())"))

    def test_no_text_is_written_with_the_platform_newline(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for match in re.finditer(r"\bopen\(", text):
            self.assertIn("encoding", text[match.start():match.start() + 200])


if __name__ == "__main__":
    unittest.main()
