"""pipeline/device_tests.py: the files for a sitting with the iPad.

Every test builds its own small library in a temporary folder from the
synthetic brushes in fixtures.py, and points the command at it with --root. None
reads the real library, the author's downloads folder or a real brush file.

fixtures.py is the second implementation: it wrote each brush's files, so "the
set holds the source's bytes" is checked against what the fixture put in, not
against what the builder read. The plist is checked against plistlib, the zip
against zipfile.

    python -m unittest discover -s brushes/pipeline/tests
"""

import ast
import contextlib
import hashlib
import io
import json
import plistlib
import re
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import yaml

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import brush_common as bc  # noqa: E402
import device_tests as dt  # noqa: E402
import fixtures  # noqa: E402
import zip_writer  # noqa: E402

BRUSHES = PIPELINE.parent
SCRIPT = PIPELINE / "device_tests.py"
DRY_RUN = "DRY RUN   nothing is written without --confirm."
WHEN = (2026, 10, 8, 12, 30, 44)
PNG = fixtures.make_png(4, 4)
# What the old designer's broken file is like: the archive's top object is a string.
BAD_BRUSH = fixtures.make_zip([(fixtures.ARCHIVE, plistlib.dumps("only a string", fmt=plistlib.FMT_BINARY))])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def uuids(start=900):
    """A callable giving repeatable folder names in the app's form."""
    numbers = iter(range(start, start + 500))
    return lambda: fixtures.brush_uuid(next(numbers))


def modern(name, number, **options):
    return fixtures.make_brush(name, "modern", number=number, **options)


def shrunk(count):
    """Root keys to leave out of a modern fixture so that `count` remain."""
    plain = [key for key in fixtures.modern_keys() if fixtures.kind_of(key) == "real"]
    return tuple(plain[-(fixtures.MODERN_KEY_COUNT - count):])


def grown(count):
    """Root keys to add to a modern fixture so that `count` are there."""
    return {f"futureSetting{n:02d}": 0.0 for n in range(count - fixtures.MODERN_KEY_COUNT)}


def set_with_junk(name, brushes):
    """A set as a careless zip tool leaves it: a folder entry before each brush,
    a .DS_Store inside each, and a __MACOSX fork beside the plist."""
    entries = []
    for brush in brushes:
        entries.append((f"{brush.uuid}/", b""))
        entries += [(f"{brush.uuid}/{path}", data) for path, data in brush.members]
        entries.append((f"{brush.uuid}/.DS_Store", b"\x00\x00\x00\x01Bud1"))
    entries.append(("__MACOSX/._brushset.plist", b"\x00\x05\x16\x07resource fork"))
    entries.append((fixtures.PLIST, fixtures.brushset_plist(name, [b.uuid for b in brushes])))
    return fixtures.make_zip(entries)


class Brushes:
    """The synthetic brushes of the full library, by the job each has."""

    def __init__(self):
        self.conte = fixtures.make_brush("Broken Cont\u00e9", era="E0", number=31)
        self.bar = fixtures.make_brush("Charcoal Bar", era="E0", number=32)
        self.jittery = fixtures.make_brush("Jittery", number=33, overrides={"plotJitter": 0.4})
        self.steady_big = fixtures.make_brush("Steady Big", number=34, size=16)
        self.steady = fixtures.make_brush("Steady", number=35)
        self.stamp = fixtures.make_brush("Steady Stamp", number=36, overrides={"stamp": True})
        self.scatter = fixtures.make_brush("Scatter", number=37, overrides={"shapeScatter": 0.2})
        self.hue = fixtures.make_brush("Hue Jitter", number=38, overrides={"dynamicsJitterHue": 0.3})
        self.inker = fixtures.make_brush("IGB Inker", era="E3", number=39)
        self.pencil = fixtures.make_brush("IGB 6B Pencil", era="E3", number=40, shape="bundled",
                                          grain="bundled")
        self.other_pencil = fixtures.make_brush("IGB HB Pencil", era="E3", number=41,
                                                shape="bundled", grain="bundled")
        self.dual = modern("Oil Dual", 42, dual=True)
        self.round = modern("Round", 43, shape="bundled", grain="bundled")
        self.painting_bare = modern("Painting Bare", 44, shape="bundled", grain="none", thumbnail=False)
        self.pen = modern("Studio Pen", 45, shape="bundled", grain="none")
        self.dry_ink = modern("Dry Ink", 46, shape="bundled", grain="bundled", thumbnail=False)
        self.heavy_ink = modern("Heavy Ink", 47, shape="bundled", grain="none", thumbnail=False,
                                dual=True)
        self.signed = modern("Signed", 48, shape="bundled", grain="bundled", author=True)
        self.candy = modern("Candy Floss", 49, dual=True, reset=True, drop_keys=shrunk(173))
        self.limestone = modern("Limestone", 50, shape="named", grain="named", thumbnail="LA",
                                empty=("", "Reset"), overrides={"version": 4},
                                extras=[("Extra/unknown.bin", b"\x00\x01unknown\xff")],
                                extra_keys=grown(242))
        self.clay = modern("Clay", 51, shape="bundled", grain="none", overrides={"version": 4},
                           extra_keys=grown(242))

        self._files = {}

    @classmethod
    def shared(cls):
        """One set of brushes for the whole run: they are bytes, and nothing changes them."""
        if cls._shared is None:
            cls._shared = cls()
        return cls._shared

    _shared = None

    def user_files(self):
        if "user" not in self._files:
            self._files["user"] = self._user_files()
        return dict(self._files["user"])

    def official_files(self):
        if "official" not in self._files:
            self._files["official"] = self._official_files()
        return dict(self._files["official"])

    def _user_files(self):
        return {
            "user/insecto-charcoal/Broken_Conte.brush": fixtures.brush_file(self.conte),
            "user/insecto-charcoal/Charcoal_Bar.brush": fixtures.brush_file(self.bar),
            "user/demo-pack/Demo_Set.brushset": fixtures.brushset_file(
                "Demo Set ", [self.jittery, self.steady_big, self.steady, self.stamp, self.scatter,
                              self.hue]),
            "user/demo-pack/Steady.brush": fixtures.brush_file(self.steady),
            "user/igb-vintage-ink-kit/IGB_Vintage_Ink_Kit.brushset": set_with_junk(
                "IGB Vintage Ink Kit", [self.inker, self.pencil, self.other_pencil]),
        }

    def _official_files(self):
        return {
            "official/procreate-5/p5-painting.brushset": fixtures.brushset_file(
                "Painting", [self.dual, self.round, self.painting_bare]),
            "official/procreate-5/p5-inking.brushset": fixtures.brushset_file(
                "Inking", [self.pen, self.heavy_ink, self.dry_ink]),
            "official/procreate-5/p5-artistic.brushset": fixtures.brushset_file(
                "Artistic", [self.signed]),
            "official/sweet-treats/sweet-treats.brushset": fixtures.brushset_file(
                "Sweet Treats", [self.candy]),
            "official/earth/earth.brushset": fixtures.brushset_file(
                "Earth", [self.clay, self.limestone], plist_extra={"iconName": "earth-icon"},
                double_empty=True, stored=(f"{self.limestone.uuid}/Brush.archive",
                                           f"{self.limestone.uuid}/.empty")),
        }

    def expected(self):
        """The brush each slot must take from the full library, in slot order."""
        return [self.conte, self.steady, self.pencil, self.dual, self.dry_ink, self.signed,
                self.candy, self.limestone]


class LibraryCase(fixtures.BrushCase):
    """A temporary brushes/ root with a library, and a place for a known-bad file."""

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "brushes"
        self.library = self.root / "library"
        self.library.mkdir(parents=True)
        self.out = self.root / "device-tests" / "sitting-1"
        self.brushes = Brushes.shared()
        self.bad = self.tmp / "downloads" / "Untitled_Brush.brush"
        self.bad.parent.mkdir()
        self.bad_bytes = BAD_BRUSH
        self.bad.write_bytes(self.bad_bytes)

    def put(self, relative, data):
        target = self.library.joinpath(*relative.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target

    def fill(self, user=True, official=True):
        files = {}
        if user:
            files.update(self.brushes.user_files())
        if official:
            files.update(self.brushes.official_files())
        for relative, data in files.items():
            self.put(relative, data)
        return files

    def build(self, **options):
        options.setdefault("known_bad", self.bad)
        options.setdefault("date_time", WHEN)
        options.setdefault("new_uuid", uuids())
        return dt.build_sitting(self.library, **options)

    def main(self, *argv, known_bad=True):
        argv = list(argv) + ["--root", str(self.root)]
        if known_bad and argv[0] == "build" and "--known-bad" not in argv:
            argv += ["--known-bad", str(self.bad)]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = dt.main(argv)
        return code, out.getvalue(), err.getvalue()

    def names(self, picks):
        return [pick.candidate.name for pick in picks]


def entries_of(data):
    return fixtures.zip_entries(data)


def folder_of(data, folder):
    """[(path, bytes)] of the entries of a built set under one folder name."""
    return [(name[len(folder) + 1:], content) for name, content in entries_of(data)
            if name.startswith(folder + "/")]


# ── the plist ────────────────────────────────────────────────────────────────

class ThePlist(unittest.TestCase):
    def test_the_exact_bytes(self):
        made = dt.brushset_plist("ROSW 1 Control", ["AAAA", "BBBB"])
        self.assertEqual(made, (
            b'<?xml version="1.0" encoding="UTF-8"?>\n'
            b'<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
            b'"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
            b'<plist version="1.0">\n<dict>\n\t<key>brushes</key>\n\t<array>\n'
            b"\t\t<string>AAAA</string>\n\t\t<string>BBBB</string>\n"
            b"\t</array>\n\t<key>name</key>\n\t<string>ROSW 1 Control</string>\n</dict>\n</plist>\n"))

    def test_it_is_what_plistlib_writes_and_reads(self):
        folders = [fixtures.brush_uuid(n) for n in range(1, 9)]
        for name in ("ROSW 1 Control", "Demo Set ", "Scratch & \u00dcn\u00ef \U0001f4a7", "a < b > c",
                     "\u6d53\u58a8\u6de1\u5f69"):
            made = dt.brushset_plist(name, folders)
            self.assertEqual(made, plistlib.dumps({"brushes": folders, "name": name},
                                                  fmt=plistlib.FMT_XML, sort_keys=False), name)
            read = plistlib.loads(made)
            self.assertEqual((list(read), read["name"], read["brushes"]),
                             (["brushes", "name"], name, folders))
            self.assertNotIn(b"\r", made)
            self.assertTrue(made.endswith(b"</plist>\n"))

    def test_a_set_with_no_brush_is_refused(self):
        with self.assertRaises(dt.DeviceTestError):
            dt.brushset_plist("Empty", [])


# ── scanning ─────────────────────────────────────────────────────────────────

class Scanning(LibraryCase):
    def scan(self):
        return dt.scan_library(self.library)

    def one(self, scan, name):
        found = [c for c in scan.candidates if c.name == name]
        self.assertTrue(found, name)
        return found[0]

    def test_it_finds_every_brush_and_only_brush_files(self):
        self.fill()
        self.put("user/demo-pack/_docs/Old_Copy.brush", fixtures.brush_file(self.brushes.bar))
        self.put("user/demo-pack/Half.brushset.part", b"PK\x03\x04half a download")
        self.put("user/demo-pack/notes.txt", b"not a brush")
        self.put("bundled/Brush-Preset-Hard.brush", fixtures.brush_file(self.brushes.bar))
        self.put("sources.json", b"{}")
        scan = self.scan()
        self.assertEqual(scan.files, {"user": 5, "official": 5})
        self.assertEqual(scan.brushes, {"user": 12, "official": 10})
        self.assertEqual(len(scan.candidates), 22)
        self.assertEqual(scan.skipped, [])
        self.assertEqual({c.library for c in scan.candidates}, {"user", "official"})

    def test_a_sets_brushes_come_in_plist_order_with_their_place(self):
        b = self.brushes
        self.put("user/demo-pack/Demo.brushset", fixtures.brushset_file(
            "Demo", [b.jittery, b.steady, b.hue], zip_order=[b.hue, b.jittery, b.steady], plist_first=True))
        found = self.scan().candidates
        self.assertEqual([(c.name, c.position, c.folder) for c in found],
                         [("Jittery", 0, b.jittery.uuid), ("Steady", 1, b.steady.uuid),
                          ("Hue Jitter", 2, b.hue.uuid)])
        self.assertEqual({c.set_name for c in found}, {"Demo"})
        self.assertEqual({c.container for c in found}, {"user/demo-pack/Demo.brushset"})
        self.assertEqual({(c.library, c.pack, c.stem) for c in found}, {("user", "demo-pack", "Demo")})

    def test_what_it_knows_of_a_legacy_brush(self):
        self.fill(official=False)
        scan = self.scan()
        conte = self.one(scan, "Broken Cont\u00e9")
        self.assertEqual((conte.era, conte.keys, conte.family), ("E0", 52, "legacy"))
        self.assertEqual((conte.set_name, conte.folder, conte.prefix, conte.position), (None, "", "", 0))
        self.assertEqual(conte.paths, tuple(self.brushes.conte.paths()))
        self.assertEqual(conte.total, sum(len(data) for _, data in self.brushes.conte.members))
        self.assertEqual(conte.archive_sha256, sha(self.brushes.conte.archive))
        self.assertTrue(conte.has_shape and conte.has_grain and conte.has_thumbnail)
        self.assertFalse(conte.dual or conte.reset or conte.reset_dual or conte.author_picture
                         or conte.signature or conte.names_only or conte.empties)
        pencil = self.one(scan, "IGB 6B Pencil")
        self.assertEqual((pencil.era, pencil.keys), ("E3", 88))
        self.assertEqual((pencil.bundled_shape, pencil.bundled_grain),
                         (fixtures.BUNDLED_SHAPE, fixtures.BUNDLED_GRAIN))
        self.assertTrue(pencil.names_only)
        self.assertFalse(pencil.has_shape or pencil.has_grain)
        self.assertEqual(pencil.where, f"user/igb-vintage-ink-kit/IGB_Vintage_Ink_Kit.brushset!/"
                                       f"{self.brushes.pencil.uuid}")

    def test_jitter_and_scatter(self):
        self.fill(official=False)
        scan = self.scan()
        facts = {c.name: (c.steady, c.calm, c.stamp) for c in scan.candidates if c.era == "E4"}
        self.assertEqual(facts, {
            "Jittery": (False, False, False), "Steady Big": (True, True, False),
            "Steady": (True, True, False), "Steady Stamp": (True, True, True),
            "Scatter": (False, False, False), "Hue Jitter": (False, True, False)})

    def test_what_it_knows_of_a_modern_brush(self):
        self.fill(user=False)
        scan = self.scan()
        dual = self.one(scan, "Oil Dual")
        self.assertEqual((dual.era, dual.keys, dual.family), ("M220", 220, "modern"))
        self.assertTrue(dual.dual)
        self.assertFalse(dual.reset or dual.reset_dual)
        candy = self.one(scan, "Candy Floss")
        self.assertEqual((candy.era, candy.keys, candy.family), ("M173", 173, "modern"))
        self.assertTrue(candy.dual and candy.reset and candy.reset_dual)
        self.assertEqual((candy.library, candy.pack, candy.stem), ("official", "sweet-treats", "sweet-treats"))
        signed = self.one(scan, "Signed")
        self.assertTrue(signed.author_picture and signed.signature)
        self.assertEqual(signed.author_name, "Fixture Author")
        bare = self.one(scan, "Dry Ink")
        self.assertFalse(bare.has_thumbnail)
        self.assertEqual(bare.stem, "p5-inking")
        stone = self.one(scan, "Limestone")
        self.assertEqual((stone.era, stone.keys, stone.version), ("M242", 242, 4))
        self.assertEqual(stone.named_textures, [self.brushes.limestone.bundled_shape,
                                                self.brushes.limestone.bundled_grain])
        self.assertFalse(stone.names_only, "its textures are in the folder, under their own names")
        self.assertEqual(stone.empties, 2)
        self.assertEqual(stone.stored, 2)
        self.assertIn("Extra/unknown.bin", stone.paths)

    def test_an_unknown_key_count_is_an_era_of_its_own(self):
        self.put("official/x/odd.brushset", fixtures.brushset_file(
            "Odd", [modern("Odd", 60, extra_keys=grown(230)),
                    fixtures.make_brush("Short", number=61, drop_keys=("plotSmoothing",))]))
        found = {c.name: (c.era, c.family) for c in self.scan().candidates}
        self.assertEqual(found, {"Odd": ("X230", "modern"), "Short": ("X100", "legacy")})

    def test_folders_junk_and_repeated_names_are_left_out_and_empty_files_kept(self):
        self.fill()
        scan = self.scan()
        pencil = self.one(scan, "IGB 6B Pencil")
        self.assertEqual(pencil.paths, tuple(self.brushes.pencil.paths()))
        stone = self.one(scan, "Limestone")
        self.assertEqual(stone.paths, tuple(self.brushes.limestone.paths()),
                         "each .empty once, though the source zip holds it twice")
        self.assertEqual([p for p in stone.paths if p.endswith(".empty")], [".empty", "Reset/.empty"])

    def test_a_set_zipped_with_one_folder_around_it(self):
        self.put("user/demo-pack/Wrapped.brushset", fixtures.brushset_file(
            "Wrapped", [self.brushes.steady], prefix="Wrapped Set/"))
        (found,) = self.scan().candidates
        self.assertEqual((found.name, found.prefix), ("Steady", f"Wrapped Set/{self.brushes.steady.uuid}/"))
        self.assertEqual(found.paths, tuple(self.brushes.steady.paths()))

    def test_a_folder_the_plist_does_not_list_is_not_a_member(self):
        b = self.brushes
        entries = [(f"{brush.uuid}/{path}", data) for brush in (b.steady, b.hue)
                   for path, data in brush.members]
        entries.append((fixtures.PLIST, fixtures.brushset_plist("Partial", [b.hue.uuid, fixtures.brush_uuid(77)])))
        self.put("user/demo-pack/Partial.brushset", fixtures.make_zip(entries))
        scan = self.scan()
        self.assertEqual([c.name for c in scan.candidates], ["Hue Jitter"])
        self.assertEqual(len(scan.skipped), 1)
        self.assertIn(fixtures.brush_uuid(77), scan.skipped[0][0])
        self.assertIn("Brush.archive", scan.skipped[0][1])

    def test_files_no_reader_may_trust_are_passed_over_and_the_scan_goes_on(self):
        self.fill(official=False)
        hostile = fixtures.hostile_files()
        del hostile["lfs-pointer.brushset"]         # stops the run: its own test
        del hostile["missing-folder.brushset"]      # costs one brush only: its own test
        for name, data in hostile.items():
            self.put(f"user/hostile/{name}", data)
        scan = self.scan()
        self.assertEqual(scan.brushes["user"], 12, "none of the hostile files gave a candidate")
        skipped = dict(scan.skipped)
        self.assertEqual(set(skipped), {f"user/hostile/{name}" for name in hostile})
        self.assertIn("..", skipped["user/hostile/traversal.brushset"])
        self.assertIn("brushset.plist", skipped["user/hostile/bare-array-plist.brushset"])
        self.assertIn("piece of text", skipped["user/hostile/string-top-archive.brush"])
        self.assertIn("binary property list", skipped["user/hostile/wrong-magic.brush"])
        self.assertIn("Brush.archive", skipped["user/hostile/no-archive.brush"])
        self.assertIn("zip", skipped["user/hostile/not-a-zip.brush"])
        self.assertTrue(skipped["user/hostile/truncated-archive.brush"])
        self.assertTrue(skipped["user/hostile/empty.brushset"])

    def test_a_listed_folder_that_is_missing_costs_only_that_brush(self):
        self.put("user/hostile/missing-folder.brushset", fixtures.hostile_files()["missing-folder.brushset"])
        scan = self.scan()
        self.assertEqual([c.name for c in scan.candidates], ["Hostile Host"])
        self.assertEqual(len(scan.skipped), 1)

    def test_a_git_lfs_pointer_stops_the_run(self):
        self.fill(official=False)
        self.put("official/earth/earth.brushset", fixtures.LFS_POINTER)
        with self.assertRaises(dt.EnvironmentProblem) as caught:
            self.scan()
        self.assertIn("git lfs pull", str(caught.exception))
        self.assertEqual(caught.exception.exit_code, 2)

    def test_the_caps(self):
        b = self.brushes
        self.put("user/demo-pack/One.brush", fixtures.brush_file(b.steady))
        size = (self.library / "user/demo-pack/One.brush").stat().st_size
        biggest = max(len(data) for _, data in b.steady.members)
        cases = {
            "zip_entries": (len(b.steady.members) - 1, "entries"),
            "archive_bytes": (len(b.steady.archive) - 1, "Brush.archive"),
            "entry_bytes": (biggest - 1, "an entry of"),
            "total_bytes": (sum(len(data) for _, data in b.steady.members) - 1, "inflated"),
            "upload_bytes": (size - 1, "the cap is"),
        }
        self.assertEqual(len(self.scan().candidates), 1)
        for cap, (value, words) in cases.items():
            with mock.patch.dict(dt.CAPS, {cap: value}):
                scan = self.scan()
            self.assertEqual(scan.candidates, [], cap)
            self.assertEqual(len(scan.skipped), 1, cap)
            self.assertIn(words, scan.skipped[0][1], cap)

    def test_an_entry_that_inflates_out_of_all_proportion(self):
        self.put("user/demo-pack/Bomb.brush", fixtures.ratio_bomb(megabytes=1))
        with mock.patch.dict(dt.CAPS, {"ratio_min_bytes": 64 * 1024}):
            scan = self.scan()
        self.assertEqual(scan.candidates, [])
        self.assertIn("200:1", scan.skipped[0][1])

    def test_an_encrypted_entry(self):
        data = bytearray(fixtures.brush_file(self.brushes.steady))
        at = data.rfind(b"PK\x01\x02")
        data[at + 8] |= 0x01
        self.put("user/demo-pack/Locked.brush", bytes(data))
        scan = self.scan()
        self.assertEqual(scan.candidates, [])
        self.assertIn("encrypted", scan.skipped[0][1])

    def test_a_member_name_this_tool_does_not_write(self):
        brush = fixtures.make_brush("Accent", number=62, extras=[("Notes/caf\u00e9.txt", b"x")])
        self.put("user/demo-pack/Accent.brush", fixtures.brush_file(brush))
        scan = self.scan()
        self.assertEqual(scan.candidates, [])
        self.assertIn("entry name", scan.skipped[0][1])

    def test_scanning_writes_nothing(self):
        self.fill()
        before = fixtures.tree_digest(self.tmp)
        self.scan()
        self.assertEqual(fixtures.tree_digest(self.tmp), before)


# ── choosing ─────────────────────────────────────────────────────────────────

class Choosing(LibraryCase):
    def choose(self):
        return dt.choose(dt.scan_library(self.library).candidates)

    def test_eight_slots_in_the_plans_order(self):
        self.assertEqual([slot.number for slot in dt.SLOTS], list(range(1, 9)))
        self.assertEqual([slot.key for slot in dt.SLOTS],
                         ["e0", "e4", "e3", "dual", "no-thumbnail", "author", "reset", "earth"])
        for slot in dt.SLOTS:
            self.assertEqual(slot.tiers[0].lost, "", slot.key)
            self.assertTrue(all(tier.lost for tier in slot.tiers[1:]), slot.key)
            self.assertTrue(slot.wanted and slot.shows and slot.absent, slot.key)

    def test_the_full_library_gives_every_slot_the_brush_it_asks_for(self):
        self.fill()
        picks, unfilled = self.choose()
        self.assertEqual(unfilled, [])
        self.assertEqual(self.names(picks), [brush.name for brush in self.brushes.expected()])
        self.assertEqual([pick.slot.number for pick in picks], list(range(1, 9)))
        self.assertTrue(all(pick.as_specified and pick.note == "" for pick in picks))
        self.assertEqual([pick.candidate.archive_sha256 for pick in picks],
                         [sha(brush.archive) for brush in self.brushes.expected()])

    def test_where_each_came_from(self):
        self.fill()
        picks, _ = self.choose()
        self.assertEqual([pick.candidate.container for pick in picks], [
            "user/insecto-charcoal/Broken_Conte.brush",
            "user/demo-pack/Demo_Set.brushset",
            "user/igb-vintage-ink-kit/IGB_Vintage_Ink_Kit.brushset",
            "official/procreate-5/p5-painting.brushset",
            "official/procreate-5/p5-inking.brushset",
            "official/procreate-5/p5-artistic.brushset",
            "official/sweet-treats/sweet-treats.brushset",
            "official/earth/earth.brushset"])

    def test_two_scans_choose_alike(self):
        self.fill()
        first, _ = self.choose()
        second, _ = self.choose()
        self.assertEqual([p.candidate.where for p in first], [p.candidate.where for p in second])

    def test_without_the_official_sets_five_slots_get_another_brush_and_say_so(self):
        self.fill(official=False)
        picks, unfilled = self.choose()
        self.assertEqual(unfilled, [])
        self.assertEqual(self.names(picks)[:3], ["Broken Cont\u00e9", "Steady", "IGB 6B Pencil"])
        self.assertEqual([pick.as_specified for pick in picks], [True] * 3 + [False] * 5)
        self.assertEqual([pick.tier for pick in picks[3:]], [None] * 5)
        hashes = [pick.candidate.archive_sha256 for pick in picks]
        self.assertEqual(len(set(hashes)), 8, "one brush is taken once, however many copies there are")
        for pick in picks[3:]:
            self.assertIn("The library holds no", pick.note)
            self.assertIn(f"It shows nothing about {pick.slot.absent}.", pick.note)
        self.assertNotIn("Steady", self.names(picks)[3:], "the loose copy of a taken brush is not taken again")

    def test_a_fill_in_prefers_an_era_the_set_lacks(self):
        # Brushes with a shape and no grain fit no kind of any slot but the first.
        for stem, name, era, number in (("E0", "Zero", "E0", 70), ("E0b", "Zero Two", "E0", 71),
                                        ("E1", "One", "E1", 72), ("E2", "Two", "E2", 73)):
            self.put(f"user/a/{stem}.brush", fixtures.brush_file(
                fixtures.make_brush(name, era=era, number=number, grain="none")))
        picks, unfilled = self.choose()
        self.assertEqual({pick.slot.number: (pick.candidate.name, pick.tier) for pick in picks},
                         {1: ("Zero", 0), 2: ("One", None), 3: ("Two", None), 4: ("Zero Two", None)})
        self.assertEqual([slot.number for slot in unfilled], [5, 6, 7, 8])

    def test_a_far_substitute_for_one_slot_does_not_take_a_near_one_for_another(self):
        # One E4 brush with jitter, and nothing else: slot 2 has a kind for it, slot 1 has none.
        self.put("user/a/Only.brush", fixtures.brush_file(self.brushes.jittery))
        picks, unfilled = self.choose()
        self.assertEqual([(pick.slot.number, pick.tier) for pick in picks], [(2, 2)])
        self.assertEqual(len(unfilled), 7)

    def substitute(self, files, slot):
        for relative, data in files.items():
            self.put(relative, data)
        picks, _ = self.choose()
        return next(pick for pick in picks if pick.slot.number == slot)

    def test_slot_1_without_an_e0_brush(self):
        marker = fixtures.make_brush("Loose Marker", era="E1b", number=5)
        pick = self.substitute({"user/a/Marker.brush": fixtures.brush_file(marker),
                                "user/a/Steady.brush": fixtures.brush_file(self.brushes.steady)}, 1)
        self.assertEqual((pick.candidate.name, pick.tier), ("Loose Marker", None),
                         "the brush with the fewest keys fills the slot")
        self.assertIn("The library holds no E0 brush (52 keys).", pick.note)
        self.assertIn("It shows nothing about the 52-key format.", pick.note)

    def test_slot_1_prefers_the_named_brush_among_e0_brushes(self):
        pick = self.substitute({"user/zz/Broken_Conte.brush": fixtures.brush_file(self.brushes.conte),
                                "user/aa/Charcoal_Bar.brush": fixtures.brush_file(self.brushes.bar)}, 1)
        self.assertEqual((pick.candidate.name, pick.tier), ("Broken Cont\u00e9", 0))

    def test_slot_2_kinds(self):
        b = self.brushes
        both_e3 = fixtures.make_brush("E3 Both", era="E3", number=74)
        cases = [(b.hue, 1, "Another of its jitter settings is not zero."),
                 (b.jittery, 2, "It has jitter or scatter"),
                 (both_e3, 3, "It is not the 101-key format.")]
        for brush, tier, words in cases:
            with self.subTest(brush=brush.name):
                target = self.put("user/a/Only.brush", fixtures.brush_file(brush))
                picks, _ = self.choose()
                pick = picks[0] if picks[0].slot.number == 2 else picks[1]
                self.assertEqual((pick.slot.number, pick.candidate.name, pick.tier), (2, brush.name, tier))
                self.assertIn(words, pick.note)
                target.unlink()

    def test_slot_3_kinds(self):
        b = self.brushes
        pick = self.substitute({"user/a/HB.brush": fixtures.brush_file(b.other_pencil)}, 3)
        self.assertEqual((pick.candidate.name, pick.tier), ("IGB HB Pencil", 1))
        self.assertIn("other texture names", pick.note)

    def test_slot_3_falls_to_a_legacy_brush_that_names_its_shape(self):
        named = fixtures.make_brush("Named Shape", era="E2", number=75, shape="bundled")
        pick = self.substitute({"user/a/Named.brush": fixtures.brush_file(named)}, 3)
        self.assertEqual((pick.candidate.name, pick.tier), ("Named Shape", 2))

    def test_slot_4_kinds(self):
        pick = self.substitute({"official/sweet-treats/sweet-treats.brushset": fixtures.brushset_file(
            "Sweet", [modern("Candy A", 76, dual=True, drop_keys=shrunk(173)),
                      modern("Candy B", 77, dual=True, reset=True, drop_keys=shrunk(173))])}, 4)
        self.assertEqual((pick.candidate.name, pick.tier), ("Candy A", 1))
        self.assertIn("It is not the 220-key format.", pick.note)

    def test_slot_4_takes_a_legacy_dual_brush_when_there_is_no_modern_one(self):
        old = fixtures.make_brush("Old Dual", number=78, dual=True, grain="none")
        pick = self.substitute({"user/a/Old.brush": fixtures.brush_file(old)}, 4)
        self.assertEqual((pick.candidate.name, pick.tier), ("Old Dual", 2))
        self.assertIn("It is not a modern brush.", pick.note)

    def test_slot_5_kinds(self):
        b = self.brushes
        pick = self.substitute({"official/procreate-5/p5-painting.brushset": fixtures.brushset_file(
            "Painting", [b.round, b.painting_bare])}, 5)
        self.assertEqual((pick.candidate.name, pick.tier), ("Painting Bare", 1))
        self.assertIn("official/procreate-5/p5-inking.brushset", pick.note)
        self.assertIn("It is from another set", pick.note)

    def test_slot_5_takes_a_legacy_brush_without_a_thumbnail_last(self):
        bare = fixtures.make_brush("Bare", number=79, thumbnail=False)
        pick = self.substitute({"user/a/Bare.brush": fixtures.brush_file(bare),
                                "user/a/Steady.brush": fixtures.brush_file(self.brushes.steady)}, 5)
        self.assertEqual((pick.candidate.name, pick.tier), ("Bare", 2))

    def test_slot_5_prefers_the_plain_brush_of_the_inking_set(self):
        self.fill()
        picks, _ = self.choose()
        self.assertEqual(picks[4].candidate.name, "Dry Ink", "not the dual one, and not the Painting one")

    def test_slot_6_with_one_of_the_two_author_files(self):
        half = modern("Half Signed", 80, extras=[("AuthorPicture/AuthorPicture.png", PNG)])
        pick = self.substitute({"official/procreate-5/p5-artistic.brushset": fixtures.brushset_file(
            "Artistic", [half])}, 6)
        self.assertEqual((pick.candidate.name, pick.tier), ("Half Signed", 1))
        self.assertIn("only one of the two", pick.note)

    def test_slot_6_is_not_filled_by_a_brush_that_only_holds_placeholders(self):
        """Some official sets keep a zero-byte `.empty` where an author picture
        would be. It is smaller than any real picture, so by size it would win
        the slot, and the set would then carry no author data at all."""
        hollow = modern("Hollow", 84, shape="bundled", grain="none", extras=[
            ("AuthorPicture/.empty", b""), ("Signature/.empty", b"")])
        blank = modern("Blank Files", 85, shape="bundled", grain="none", extras=[
            ("AuthorPicture/AuthorPicture.png", b""), ("Signature/SignaturePicture.png", b"")])
        self.put("official/earth/earth.brushset", fixtures.brushset_file("Earth", [hollow, blank]))
        self.put("official/procreate-5/p5-artistic.brushset",
                 fixtures.brushset_file("Artistic", [self.brushes.signed]))
        candidates = {c.name: c for c in dt.scan_library(self.library).candidates}
        for name in ("Hollow", "Blank Files"):
            self.assertFalse(candidates[name].author_picture, name)
            self.assertFalse(candidates[name].signature, name)
            self.assertEqual(len(candidates[name].files_under("AuthorPicture/")), 1, "the member is still there")
        self.assertEqual(candidates["Hollow"].empties, 2)
        self.assertLess(candidates["Hollow"].total, candidates["Signed"].total,
                        "the placeholder brush is the smaller one, so size alone would choose it")
        self.assertTrue(candidates["Signed"].author_picture and candidates["Signed"].signature)
        picks, _ = self.choose()
        pick = next(pick for pick in picks if pick.slot.number == 6)
        self.assertEqual((pick.candidate.name, pick.tier), ("Signed", 0))

    def test_placeholders_alone_fit_no_kind_of_slot_6(self):
        hollow = modern("Hollow", 84, shape="bundled", grain="none", extras=[
            ("AuthorPicture/.empty", b""), ("Signature/.empty", b"")])
        self.put("official/procreate-5/p5-artistic.brushset", fixtures.brushset_file("Artistic", [hollow]))
        (candidate,) = dt.scan_library(self.library).candidates
        slot = dt.SLOTS[5]
        self.assertEqual(slot.key, "author")
        self.assertEqual([tier.test(candidate) for tier in slot.tiers], [False, False],
                         "not the kind asked for, and not the nearest kind either")
        picks, _ = self.choose()
        self.assertEqual([(pick.slot.number, pick.tier) for pick in picks], [(1, None)],
                         "it only ever fills a slot as some other brush")
        self.assertIn("SUBSTITUTE", picks[0].shows)

    def test_a_real_picture_beside_a_placeholder_counts(self):
        mixed = modern("Mixed", 86, shape="bundled", grain="none", extras=[
            ("AuthorPicture/.empty", b""), ("AuthorPicture/AuthorPicture.png", PNG),
            ("Signature/SignaturePicture.png", PNG)])
        pick = self.substitute({"official/earth/earth.brushset": fixtures.brushset_file("Earth", [mixed])}, 6)
        self.assertEqual((pick.candidate.name, pick.tier), ("Mixed", 0))

    def test_slot_7_kinds(self):
        files = {"official/procreate-5/p5-painting.brushset": fixtures.brushset_file(
            "Painting", [modern("Dual One", 81, dual=True), modern("Dual Reset", 82, dual=True, reset=True),
                         modern("Reset Only", 83, reset=True)])}
        pick = self.substitute(files, 7)
        self.assertEqual((pick.candidate.name, pick.tier), ("Dual Reset", 1))
        self.assertIn("It is not from Sweet Treats", pick.note)

    def test_slot_7_takes_a_reset_folder_without_a_second_brush_last(self):
        pick = self.substitute({"official/procreate-5/p5-painting.brushset": fixtures.brushset_file(
            "Painting", [modern("Reset Only", 83, reset=True)])}, 7)
        self.assertEqual((pick.candidate.name, pick.tier), ("Reset Only", 2))

    def test_slot_8_kinds(self):
        pick = self.substitute({"official/chinese-calligraphy/chinese-calligraphy.brushset":
                                fixtures.brushset_file("\u6d53\u58a8\u6de1\u5f69", [self.brushes.clay])}, 8)
        self.assertEqual((pick.candidate.name, pick.tier), ("Clay", 1))
        self.assertIn("It is not from the Earth set.", pick.note)

    def test_slot_8_prefers_the_earth_brush_with_its_own_named_texture(self):
        self.fill()
        picks, _ = self.choose()
        self.assertEqual(picks[7].candidate.name, "Limestone")

    def test_a_substitute_never_takes_what_another_slot_asks_for(self):
        # One dual brush with a reset copy, in Sweet Treats: slot 7 asks for it by kind,
        # and slot 4 (any dual brush, as a substitute) must not have taken it first.
        self.put("official/sweet-treats/sweet-treats.brushset",
                 fixtures.brushset_file("Sweet Treats", [self.brushes.candy]))
        self.put("user/a/Steady.brush", fixtures.brush_file(self.brushes.steady))
        picks, _ = self.choose()
        by_slot = {pick.slot.number: (pick.candidate.name, pick.tier) for pick in picks}
        self.assertEqual(by_slot[7], ("Candy Floss", 0))
        self.assertNotIn(4, by_slot)

    def test_a_library_of_three_fills_three_slots(self):
        b = self.brushes
        self.put("user/a/Set.brushset", fixtures.brushset_file("Three", [b.conte, b.steady, b.pencil]))
        picks, unfilled = self.choose()
        self.assertEqual(self.names(picks), ["Broken Cont\u00e9", "Steady", "IGB 6B Pencil"])
        self.assertEqual([slot.number for slot in unfilled], [4, 5, 6, 7, 8])


# ── building, in memory ──────────────────────────────────────────────────────

class Building(LibraryCase):
    def setUp(self):
        super().setUp()
        self.fill()

    def test_it_writes_nothing(self):
        before = fixtures.tree_digest(self.tmp)
        build = self.build()
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertFalse(self.out.exists())
        self.assertEqual(len(build.members), 8)

    def test_the_set_holds_every_members_files_byte_for_byte_in_the_sources_order(self):
        build = self.build()
        names = uuids()
        expected_folders = [names() for _ in range(8)]
        self.assertEqual([member.uuid for member in build.members], expected_folders)
        for member, brush, folder in zip(build.members, self.brushes.expected(), expected_folders):
            self.assertEqual(folder_of(build.set_bytes, folder), brush.members, brush.name)
        held = entries_of(build.set_bytes)
        self.assertEqual(len(held), sum(len(brush.members) for brush in self.brushes.expected()) + 1)
        self.assertEqual(len({name for name, _ in held}), len(held))

    def test_only_the_plist_is_ours_and_it_comes_last_in_the_exact_form(self):
        build = self.build()
        held = entries_of(build.set_bytes)
        folders = [member.uuid for member in build.members]
        self.assertEqual(held[-1][0], "brushset.plist")
        self.assertEqual([name for name, _ in held].count("brushset.plist"), 1)
        self.assertEqual(held[-1][1], plistlib.dumps({"brushes": folders, "name": "ROSW 1 Control"},
                                                     fmt=plistlib.FMT_XML, sort_keys=False))
        tops = []
        for name, _ in held[:-1]:
            if name.split("/")[0] not in tops:
                tops.append(name.split("/")[0])
        self.assertEqual(tops, folders, "one folder per member, each in one run, in slot order")
        self.assertEqual((dt.SET_NAME, dt.SET_FILE), ("ROSW 1 Control", "ROSW-1-control.brushset"))

    def test_the_zip_carries_the_apps_header_fields_and_the_given_date(self):
        build = self.build()
        with zipfile.ZipFile(io.BytesIO(build.set_bytes)) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.comment, b"")
            for info in archive.infolist():
                name = info.orig_filename
                self.assertEqual((info.compress_type, info.flag_bits, info.create_system, info.create_version,
                                  info.extract_version, info.external_attr, info.extra, info.comment),
                                 (8, 6, 0, 0, 20, 0, b"", b""), name)
                self.assertEqual(info.date_time, (2026, 10, 8, 12, 30, 44), name)
                self.assertFalse(name.endswith("/"), name)
                self.assertEqual(info.internal_attr, 1 if name == "brushset.plist" else 0, name)

    def test_what_the_source_zip_did_differently_is_not_carried(self):
        build = self.build()
        stone = build.members[7]
        self.assertEqual(stone.candidate.name, "Limestone")
        carried = [path for path, _ in folder_of(build.set_bytes, stone.uuid)]
        self.assertEqual(carried.count(".empty"), 1, "stored twice in the source, once here")
        self.assertIn("Reset/.empty", carried)
        self.assertIn("Extra/unknown.bin", carried, "a file no reader knows is carried all the same")
        pencil = build.members[2]
        self.assertEqual([path for path, _ in folder_of(build.set_bytes, pencil.uuid)],
                         self.brushes.pencil.paths(), "no .DS_Store and no folder entry")
        with zipfile.ZipFile(io.BytesIO(build.set_bytes)) as archive:
            self.assertEqual({info.compress_type for info in archive.infolist()}, {zipfile.ZIP_DEFLATED})

    def test_each_single_file_holds_one_members_files_at_the_zip_root(self):
        build = self.build()
        self.assertEqual(list(build.singles), [
            "singles/1-Broken_Conte.brush", "singles/2-Steady.brush", "singles/3-IGB_6B_Pencil.brush",
            "singles/4-Oil_Dual.brush", "singles/5-Dry_Ink.brush", "singles/6-Signed.brush",
            "singles/7-Candy_Floss.brush", "singles/8-Limestone.brush"])
        for (name, data), brush in zip(build.singles.items(), self.brushes.expected()):
            self.assertEqual(entries_of(data), brush.members, name)
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                self.assertEqual({(i.flag_bits, i.create_system, i.external_attr) for i in archive.infolist()},
                                 {(6, 0, 0)})
        self.assertIn("Sub01/Brush.archive", [n for n, _ in entries_of(build.singles["singles/4-Oil_Dual.brush"])])
        self.assertIn("Reset/Sub01/Brush.archive",
                      [n for n, _ in entries_of(build.singles["singles/7-Candy_Floss.brush"])])

    def test_fresh_folder_names(self):
        first = dt.build_sitting(self.library, known_bad=None)
        second = dt.build_sitting(self.library, known_bad=None)
        ours = [member.uuid for member in first.members]
        self.assertEqual(len(set(ours)), 8)
        for name in ours:
            self.assertRegex(name, fixtures.UUID_PATTERN)
            self.assertEqual(name, name.upper())
        sources = {brush.uuid for brush in self.brushes.expected()}
        self.assertFalse(sources & set(ours), "a source's folder name is never reused")
        self.assertFalse(set(ours) & {member.uuid for member in second.members}, "fresh on every build")
        with zipfile.ZipFile(io.BytesIO(first.set_bytes)) as archive:
            dates = {info.date_time for info in archive.infolist()}
        self.assertEqual(len(dates), 1, "one date for every entry")
        self.assertNotEqual(dates, {zip_writer.DEFAULT_DATE_TIME}, "with no date given, it is today's")
        self.assertGreaterEqual(min(dates)[0], 2026)

    def test_a_folder_name_that_is_taken_or_malformed_is_drawn_again(self):
        taken = self.brushes.steady.uuid
        good = [fixtures.brush_uuid(n) for n in range(700, 708)]
        offered = iter([good[0], good[0], taken, "not-a-uuid", good[1].lower(), None] + good[1:])
        build = self.build(new_uuid=lambda: next(offered))
        self.assertEqual([member.uuid for member in build.members], good)

    def test_a_source_of_names_that_never_gives_a_new_one_is_an_error(self):
        with self.assertRaises(dt.DeviceTestError) as caught:
            self.build(new_uuid=lambda: fixtures.brush_uuid(1))
        self.assertIn("UUID", str(caught.exception))

    def test_the_manifest(self):
        build = self.build()
        manifest = build.manifest
        self.assertEqual((manifest["schema"], manifest["sitting"]), ("rosw-brushes-device-test/1", "sitting-1"))
        self.assertEqual(manifest["set"], {"file": "ROSW-1-control.brushset", "name": "ROSW 1 Control",
                                           "bytes": len(build.set_bytes), "sha256": sha(build.set_bytes)})
        self.assertEqual(manifest["unfilled"], [])
        self.assertEqual([m["slot"] for m in manifest["members"]], list(range(1, 9)))
        self.assertEqual([m["slot_kind"] for m in manifest["members"]], [slot.key for slot in dt.SLOTS])
        self.assertEqual([m["slot_shows"] for m in manifest["members"]],
                         [slot.shows for slot in dt.SLOTS])
        self.assertEqual([m["shows"] for m in manifest["members"]], [slot.shows for slot in dt.SLOTS],
                         "as specified, a member shows what its slot is for")
        self.assertNotIn("meant_to_show", manifest["members"][0])
        self.assertIs(manifest["complete"], True)
        self.assertEqual(manifest["substitutes"], [])
        for entry, member, brush in zip(manifest["members"], build.members, self.brushes.expected()):
            self.assertEqual(entry["name"], brush.name)
            self.assertEqual(entry["uuid"], member.uuid)
            self.assertTrue(entry["as_specified"])
            self.assertEqual(entry["note"], "")
            self.assertEqual(entry["files"], [{"path": path, "bytes": len(data), "sha256": sha(data)}
                                              for path, data in brush.members])
            self.assertEqual(entry["source"]["container"], member.candidate.container)
            self.assertEqual(entry["single_sha256"], sha(build.singles[entry["single"]]))
        self.assertEqual(manifest["members"][1]["source"], {
            "container": "user/demo-pack/Demo_Set.brushset", "set": "Demo Set ",
            "folder": self.brushes.steady.uuid, "prefix": self.brushes.steady.uuid + "/", "position": 2})
        self.assertEqual(manifest["members"][0]["source"], {
            "container": "user/insecto-charcoal/Broken_Conte.brush", "set": None, "folder": "",
            "prefix": "", "position": 0})
        self.assertEqual(manifest["known_bad"]["sha256"], sha(self.bad_bytes))
        self.assertEqual(manifest["known_bad"]["file"], "known-bad/KNOWN-BAD_old-designer.brush")
        self.assertEqual(manifest["known_bad"]["original_name"], "Untitled_Brush.brush")
        self.assertEqual(manifest["written"], sorted(build.files()))

    def test_the_manifest_names_no_machine_path_and_no_date(self):
        build = self.build()
        text = build.files()["manifest.json"].decode("utf-8")
        self.assertEqual(text, bc.json_text(build.manifest))
        for part in (str(self.tmp), self.tmp.as_posix(), str(Path.home()), "\\\\", "C:"):
            self.assertNotIn(part, text, part)

        def keys(value):
            if isinstance(value, dict):
                for key, inner in value.items():
                    yield key
                    yield from keys(inner)
            elif isinstance(value, list):
                for inner in value:
                    yield from keys(inner)

        self.assertFalse({"date", "date_time", "time", "built", "created", "timestamp"} & set(keys(build.manifest)))
        self.assertNotIn("2026", text)

    def test_what_is_written_and_in_what_order(self):
        files = self.build().files()
        self.assertEqual(list(files)[-3:], ["ROSW-1-control.brushset", "CHECKLIST.md", "manifest.json"])
        self.assertEqual(len([name for name in files if name.startswith("singles/")]), 8)
        self.assertIn("known-bad/KNOWN-BAD_old-designer.brush", files)
        self.assertEqual(files["known-bad/KNOWN-BAD_old-designer.brush"], self.bad_bytes)
        self.assertFalse([name for name in files if "Untitled" in name],
                         "no file here is named like the brush that comes back from the iPad")
        self.assertEqual(len(files), 12)
        for name, data in files.items():
            self.assertIsInstance(data, bytes, name)

    def test_a_brush_that_changes_between_the_scan_and_the_read_stops_the_build(self):
        real = dt.load_member
        target = self.library / "user/insecto-charcoal/Broken_Conte.brush"

        def swap_then_load(library, candidate):
            if candidate.name == "Broken Cont\u00e9":
                target.write_bytes(fixtures.brush_file(self.brushes.bar))
            return real(library, candidate)

        with mock.patch.object(dt, "load_member", swap_then_load):
            with self.assertRaises(dt.DeviceTestError) as caught:
                self.build()
        self.assertIn("changed", str(caught.exception))

    def test_a_missing_library_and_an_empty_one(self):
        for library in (self.tmp / "nowhere", self.tmp):
            with self.assertRaises(dt.EnvironmentProblem) as caught:
                dt.build_sitting(library, known_bad=None)
            self.assertEqual(caught.exception.exit_code, 2)


class Substitutes(LibraryCase):
    def test_a_build_without_the_official_sets_says_so_everywhere(self):
        self.fill(official=False)
        build = self.build()
        self.assertEqual(len(build.members), 8)
        entries = build.manifest["members"]
        self.assertEqual([m["as_specified"] for m in entries], [True] * 3 + [False] * 5)
        self.assertTrue(all(m["note"] for m in entries[3:]))
        plan = dt.render_plan(build, self.library, self.out)
        self.assertEqual(plan.count("SUBSTITUTE"), 5)
        self.assertEqual(plan.count("as specified  "), 3)
        self.assertIn("3 of 8 members are as specified, 5 are substitutes, 0 slots are empty.", plan)
        self.assertIn("WARNING   library/official/ holds no file.", plan)
        self.assertIn("fetch_base_library.py fetch --confirm", plan)
        self.assertIn("NOT THE CONTROL SET", plan)
        self.assertIn("--allow-substitutes", plan)
        self.assertIs(build.complete, False)
        self.assertIs(build.manifest["complete"], False)
        self.assertEqual(build.manifest["substitutes"], [4, 5, 6, 7, 8])
        text = build.checklist
        self.assertIn("**This build is not the full control set.**", text)
        self.assertIn("5 of its 8 brushes are substitutes", text)
        self.assertIn("`brushes/library/official/` holds no official sets", text)
        self.assertNotIn("is empty)", text, "the folder may not exist at all")
        self.assertIn(">     python brushes/pipeline/fetch_base_library.py fetch --confirm", text)
        self.assertIn(">     python brushes/pipeline/device_tests.py build sitting-1 --confirm", text)
        self.assertEqual(text.count(". SUBSTITUTE: stands in for the "), 5)
        self.assertEqual(text.count("Only the three plain questions apply."), 5)
        self.assertNotIn("Does Brush Studio show two brushes", text, "no dual question without a dual brush")
        for member in build.members:
            self.assertEqual(folder_of(build.set_bytes, member.uuid), member.files)

    def test_a_stand_in_is_described_by_its_own_facts_never_by_the_slots(self):
        """Row 8 once read "SUBSTITUTE for: newest format (E0, 52 keys)": the
        oldest format presented as the newest."""
        self.fill(official=False)
        build = self.build()
        rows = dict(re.findall(r"^\| (\d) \| [^|]+ \| ([^|]+) \|  \|  \|  \|$", build.checklist, flags=re.M))
        for member in build.members[3:]:
            candidate = member.candidate
            row = rows[str(member.slot.number)]
            self.assertTrue(row.startswith(f"{candidate.era}, {candidate.keys} keys. SUBSTITUTE: stands in for the "),
                            row)
            self.assertTrue(row.endswith(" and shows nothing about it"), row)
            self.assertNotIn("SUBSTITUTE for:", row)
            entry = build.manifest["members"][member.slot.number - 1]
            self.assertEqual(entry["shows"], f"SUBSTITUTE: it shows nothing about {member.slot.absent}")
            self.assertEqual(entry["slot_shows"], member.slot.shows)
            self.assertNotEqual(entry["shows"], entry["slot_shows"])
        self.assertIn("newest format", rows["8"])
        self.assertNotIn("newest format (", rows["8"], "the bracket never puts the slot's words on another brush")
        for member in build.members[:3]:
            self.assertRegex(rows[str(member.slot.number)], r"^[a-z].* \([EM0-9a-z]+, \d+ keys\)$")

    def test_the_banner_says_what_kind_of_stand_in_each_is(self):
        self.fill(official=False)
        text = self.build().checklist
        self.assertIn("nor anything near it, so another brush from the library", text)
        self.assertNotIn("the nearest kind found stands in", text,
                         "nothing near was found for any of the five")
        # A near kind for one slot (a 242-key brush that is not from Earth), and it alone.
        self.put("official/chinese-calligraphy/chinese-calligraphy.brushset",
                 fixtures.brushset_file("\u6d53\u58a8", [self.brushes.clay]))
        mixed = self.build()
        tiers = [member.pick.tier for member in mixed.members]
        self.assertIn(None, tiers)
        self.assertIn(1, tiers)
        self.assertIn("so the nearest kind found stands in, or, where nothing", mixed.checklist)
        self.assertNotIn("holds no official sets", mixed.checklist)
        near = next(member for member in mixed.members if member.pick.tier == 1)
        self.assertEqual(mixed.manifest["members"][near.slot.number - 1]["shows"],
                         "SUBSTITUTE: a 242-key brush. It is not from the Earth set.")
        self.assertIn("M242, 242 keys. SUBSTITUTE: stands in for the newest format |", mixed.checklist)

    def test_only_near_kinds(self):
        files = self.fill()
        (self.library / "official/earth/earth.brushset").unlink()
        self.put("official/chinese-calligraphy/chinese-calligraphy.brushset",
                 fixtures.brushset_file("\u6d53\u58a8", [self.brushes.clay]))
        build = self.build()
        self.assertTrue(files)
        self.assertEqual([member.pick.tier for member in build.members], [0] * 7 + [1])
        self.assertIn("> brush the plan asks for, so the nearest kind found stands in.", build.checklist)
        self.assertNotIn("another brush from the library", build.checklist)

    def test_a_small_library_leaves_slots_empty(self):
        b = self.brushes
        self.put("user/a/Set.brushset", fixtures.brushset_file("Three", [b.conte, b.steady, b.pencil]))
        build = self.build()
        self.assertEqual(len(build.members), 3)
        self.assertEqual([slot["slot"] for slot in build.manifest["unfilled"]], [4, 5, 6, 7, 8])
        self.assertEqual(len(plistlib.loads(entries_of(build.set_bytes)[-1][1])["brushes"]), 3)
        self.assertIn("Slot 4 is empty", build.checklist)
        self.assertIn("The set holds 3 brushes", build.checklist)
        self.assertIn("EMPTY", dt.render_plan(build, self.library, self.out))
        self.assertIs(build.complete, False)
        self.assertIs(build.manifest["complete"], False)
        self.assertEqual(build.manifest["substitutes"], [])
        self.assertIn("**This build is not the full control set.**", build.checklist)


# ── the known-bad file ───────────────────────────────────────────────────────

class KnownBad(LibraryCase):
    def setUp(self):
        super().setUp()
        self.fill(official=False)

    def test_it_is_copied_byte_for_byte_and_described(self):
        build = self.build()
        self.assertEqual(build.known_bad["file"], "known-bad/KNOWN-BAD_old-designer.brush")
        self.assertEqual(build.known_bad["original_name"], "Untitled_Brush.brush")
        self.assertEqual(build.known_bad["data"], self.bad_bytes)
        self.assertTrue(build.known_bad["broken"])
        self.assertIn("a single piece of text", build.known_bad["finding"])
        self.assertIn("a single piece of text", build.checklist)
        self.assertIn("Open the known-bad file first", build.checklist)
        self.assertNotIn("WARNING", build.known_bad_note)

    def test_no_file_there_means_no_known_bad_folder(self):
        build = self.build(known_bad=self.tmp / "downloads" / "Nothing.brush")
        self.assertIsNone(build.known_bad)
        self.assertIn("there is no file at", build.known_bad_note)
        self.assertFalse([name for name in build.files() if name.startswith("known-bad/")])
        self.assertIsNone(build.manifest["known_bad"])
        self.assertNotIn("known-bad", build.checklist)
        self.assertNotIn("known-bad", " ".join(build.manifest["written"]))
        self.assertIn("## Step 3. Import the control set", build.checklist)

    def test_none_asked_for(self):
        build = self.build(known_bad=None)
        self.assertIsNone(build.known_bad)

    def test_what_it_says_of_each_kind_of_bad_file(self):
        hostile = fixtures.hostile_files()
        cases = {"wrong-magic.brush": "not a binary property list", "truncated-archive.brush": "Brush.archive",
                 "no-archive.brush": "holds no Brush.archive", "not-a-zip.brush": "zip",
                 "lfs-pointer.brushset": "not a zip file", "traversal.brushset": ".."}
        for name, words in cases.items():
            broken, finding = dt.diagnose(hostile[name])
            self.assertTrue(broken, name)
            self.assertIn(words, finding, name)

    def test_a_file_with_nothing_wrong_is_copied_with_a_warning(self):
        fine = self.tmp / "downloads" / "Fine Br\u00fcsh.brush"
        fine.write_bytes(fixtures.brush_file(self.brushes.bar))
        build = self.build(known_bad=fine)
        self.assertEqual(build.known_bad["file"], "known-bad/KNOWN-BAD_old-designer.brush")
        self.assertEqual(build.known_bad["original_name"], "Fine_Brush.brush")
        self.assertFalse(build.known_bad["broken"])
        self.assertIn("WARNING", build.known_bad_note)
        self.assertIn("52 keys", build.known_bad["finding"])

    def test_the_copy_never_carries_the_name_it_came_under(self):
        """Procreate calls a new brush "Untitled Brush". The old designer's file
        is Untitled_Brush.brush. In one folder the two would be a character apart."""
        for name, wanted in (("Untitled_Brush.brush", ".brush"), ("Untitled Brush.BRUSHSET", ".brushset"),
                             ("no extension", ".brush"), ("archive.zip", ".brush")):
            source = self.tmp / "downloads" / name
            source.write_bytes(self.bad_bytes)
            build = self.build(known_bad=source)
            self.assertEqual(build.known_bad["file"], f"known-bad/KNOWN-BAD_old-designer{wanted}", name)
            self.assertNotIn("Untitled", build.known_bad["file"])
            self.assertEqual(build.files()[build.known_bad["file"]], self.bad_bytes)
            self.assertNotIn("Untitled_Brush", build.checklist)
            self.assertNotIn(str(self.tmp), json.dumps(build.manifest))


# ── the checklist ────────────────────────────────────────────────────────────

class TheChecklist(LibraryCase):
    def setUp(self):
        super().setUp()
        self.fill()
        self.build_ = self.build()
        self.text = self.build_.checklist

    def test_it_is_plain_text_a_person_can_follow(self):
        raw = self.build_.files()["CHECKLIST.md"]
        self.assertEqual(raw.decode("utf-8"), self.text)
        self.assertNotIn("\r", self.text)
        self.assertTrue(self.text.startswith("# Sitting 1: the control set\n"))
        self.assertTrue(self.text.endswith("\n"))
        for part in (str(self.tmp), self.tmp.as_posix(), str(Path.home())):
            self.assertNotIn(part, self.text)
        steps = re.findall(r"^## Step (\d)\. (.+)$", self.text, flags=re.M)
        self.assertEqual([int(number) for number, _ in steps], [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual([title for _, title in steps], [
            "Get the files onto the iPad", "Write down the versions", "Open the known-bad file first",
            "Import the control set", "Look at each brush", "The return leg: share two things back",
            "Put the returned files here"])

    def test_the_known_bad_file_comes_before_the_control_set(self):
        self.assertLess(self.text.index("Open the known-bad file first"), self.text.index("Import the control set"))
        self.assertIn("Tap `KNOWN-BAD_old-designer.brush`", self.text)
        self.assertNotIn("Untitled_Brush", self.text)
        self.assertIn("what a refusal looks like", self.text)
        self.assertIn("delete it straight away", self.text)

    def test_the_known_bad_file_is_kept_out_of_what_comes_back(self):
        step_7 = self.text[self.text.index("## Step 7"):]
        self.assertIn("Do not put the known-bad file (`KNOWN-BAD_old-designer.brush`) in `returned/`", step_7)
        self.assertIn("Never a file to bring back", self.text)

    def test_the_canvas_is_opened_before_the_brush_icon_is_asked_for(self):
        """From the Gallery there is no brush icon: a canvas has to be open."""
        step_4 = self.text[self.text.index("## Step 4"):self.text.index("## Step 5")]
        self.assertLess(step_4.index("open any canvas"), step_4.index("tap the brush"))
        self.assertIn("not in the Gallery", step_4)
        step_5 = self.text[self.text.index("## Step 5"):self.text.index("## Step 6")]
        self.assertIn("Stay in that canvas and pick black.", step_5)
        self.assertNotIn("Open any canvas", step_5)

    def test_it_says_what_git_keeps(self):
        head = self.text[:self.text.index("## What this is for")]
        self.assertIn("Git keeps three things of it: `manifest.json`, this checklist", head)
        self.assertNotIn("Nothing in it is committed", self.text)
        self.assertIn("What is in `returned/` is kept in git", self.text)

    def test_it_asks_for_the_versions(self):
        for words in ("Procreate version", "iPadOS version and iPad model"):
            self.assertIn(words, self.text)

    def test_it_names_the_set_and_every_brush_in_order(self):
        self.assertIn("Tap `ROSW-1-control.brushset`", self.text)
        self.assertIn("named **ROSW 1 Control**", self.text)
        names = [brush.name for brush in self.brushes.expected()]
        listed = re.findall(r"^(\d)\. (.+)$", self.text[self.text.index("## Step 4"):self.text.index("## Step 5")],
                            flags=re.M)
        self.assertEqual(listed, [(str(n), name) for n, name in enumerate(names, 1)])
        rows = re.findall(r"^\| (\d) \| ([^|]+) \| ([^|]+) \|  \|  \|  \|$", self.text, flags=re.M)
        self.assertEqual([(number, name) for number, name, _ in rows],
                         [(str(n), name) for n, name in enumerate(names, 1)])
        self.assertIn("| Listed? | Preview? | Draws? |", self.text)
        self.assertNotIn("SUBSTITUTE", self.text)
        self.assertNotIn("not the full control set", self.text)

    def test_the_question_that_belongs_to_each_brush(self):
        asked = re.findall(r"^(\d)\. \*\*(.+?)\.\*\* (.+)$", self.text, flags=re.M)
        self.assertEqual(len(asked), 8)
        by_number = {int(number): words for number, _, words in asked}
        self.assertIn("accent", by_number[1])
        self.assertIn("plain case", by_number[2])
        self.assertIn(f"`{fixtures.BUNDLED_SHAPE}` and `{fixtures.BUNDLED_GRAIN}`", by_number[3])
        self.assertIn("dual brush", by_number[4])
        self.assertIn("Does Brush Studio show two brushes", by_number[4])
        self.assertIn("did Procreate draw one itself", by_number[5])
        self.assertIn("a maker's name, a picture and a signature", by_number[6])
        self.assertIn("reset point", by_number[7])
        self.assertIn(f"`{self.brushes.limestone.bundled_shape}`", by_number[8])

    def test_the_return_leg_and_where_the_files_go(self):
        self.assertIn("**a. The control set.**", self.text)
        self.assertIn("**b. One brand-new, untouched brush.**", self.text)
        self.assertIn("tap the **+**", self.text)
        self.assertIn("`.brush` file", self.text)
        self.assertIn("`.brushset` file", self.text)
        self.assertIn("    brushes/device-tests/sitting-1/returned/\n", self.text)
        self.assertIn("Do not build this sitting again once files are in that folder", self.text)

    def test_what_to_do_when_the_set_fails(self):
        self.assertIn("### If the set does not import, or a brush is missing or will not draw", self.text)
        self.assertIn("Open the files in `singles/` one at a time", self.text)

    def test_it_claims_nothing_about_what_procreate_will_do(self):
        self.assertIn("Nothing this tool has written has been opened in Procreate yet.", self.text)
        for claim in ("opens in Procreate", "Procreate accepts", "is known to work", "guaranteed"):
            self.assertNotIn(claim, self.text)

    def test_a_name_with_odd_characters_is_made_safe(self):
        odd = fixtures.make_brush("Odd | Name\x07 ", era="E0", number=90)
        target = self.put("user/insecto-charcoal/Broken_Conte.brush", fixtures.brush_file(odd))
        self.assertTrue(target.is_file())
        (self.library / "user/insecto-charcoal/Charcoal_Bar.brush").unlink()
        build = self.build()
        self.assertEqual(build.members[0].candidate.name, "Odd | Name\x07 ")
        self.assertIn("| 1 | Odd / Name? |", build.checklist)
        self.assertNotIn("\x07", build.checklist)
        self.assertEqual(build.members[0].single, "singles/1-Odd_Name.brush")


# ── the command ──────────────────────────────────────────────────────────────

class TheCommand(LibraryCase):
    def setUp(self):
        super().setUp()
        self.files = self.fill()

    def test_a_dry_run_prints_the_plan_and_writes_nothing(self):
        before = fixtures.tree_digest(self.tmp)
        code, out, err = self.main("build", "sitting-1")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.rstrip("\n").splitlines()[-1], DRY_RUN)
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertFalse((self.root / "device-tests").exists())
        self.assertNotIn("WRITTEN", out)
        self.assertNotIn("VERIFIED", out)

    def test_the_plan_says_which_source_each_member_came_from(self):
        _, out, _ = self.main("build", "sitting-1")
        b = self.brushes
        for line in (
                "source  user/insecto-charcoal/Broken_Conte.brush   (a loose brush)",
                f"source  user/demo-pack/Demo_Set.brushset!/{b.steady.uuid}   (set 'Demo Set ', place 3)",
                f"source  official/procreate-5/p5-inking.brushset!/{b.dry_ink.uuid}   (set 'Inking', place 3)",
                f"source  official/earth/earth.brushset!/{b.limestone.uuid}   (set 'Earth', place 2)",
                "8 of 8 members are as specified, 0 are substitutes, 0 slots are empty.",
                "user/         5 files,   12 brushes", "official/     5 files,   10 brushes",
                "no thumbnail", "2 stored without compression in the source"):
            self.assertIn(line, out)
        self.assertEqual(out.count("as specified  "), 8)
        self.assertNotIn("SUBSTITUTE", out)
        self.assertNotIn("WARNING", out)
        self.assertIn(f"known-bad copied from {self.bad}", out)

    def test_confirm_writes_the_sitting_and_checks_it(self):
        library_before = fixtures.tree_digest(self.library)
        code, out, err = self.main("build", "sitting-1", "--confirm")
        self.assertEqual((code, err), (0, ""))
        self.assertNotIn(DRY_RUN, out)
        self.assertIn(f"WRITTEN   12 files in {self.out}", out)
        self.assertTrue(out.rstrip("\n").splitlines()[-1].startswith("VERIFIED   8 members, "))
        self.assertEqual(fixtures.tree_digest(self.library), library_before, "the library is never written")
        written = sorted(p.relative_to(self.out).as_posix() for p in self.out.rglob("*") if p.is_file())
        self.assertEqual(written, sorted([
            "CHECKLIST.md", "ROSW-1-control.brushset", "manifest.json",
            "known-bad/KNOWN-BAD_old-designer.brush",
            "singles/1-Broken_Conte.brush", "singles/2-Steady.brush", "singles/3-IGB_6B_Pencil.brush",
            "singles/4-Oil_Dual.brush", "singles/5-Dry_Ink.brush", "singles/6-Signed.brush",
            "singles/7-Candy_Floss.brush", "singles/8-Limestone.brush"]))
        self.assertTrue((self.out / "returned").is_dir())
        self.assertEqual(list((self.out / "returned").iterdir()), [])
        self.assertEqual((self.out / "known-bad" / "KNOWN-BAD_old-designer.brush").read_bytes(),
                         self.bad_bytes)
        self.assertFalse(list(self.out.rglob("*.tmp")))

    def test_what_is_on_disk_is_the_sources_bytes(self):
        self.main("build", "sitting-1", "--confirm")
        data = (self.out / "ROSW-1-control.brushset").read_bytes()
        plist = plistlib.loads(entries_of(data)[-1][1])
        self.assertEqual(plist["name"], "ROSW 1 Control")
        self.assertEqual(len(plist["brushes"]), 8)
        self.assertEqual(len(set(plist["brushes"])), 8)
        for folder, brush in zip(plist["brushes"], self.brushes.expected()):
            self.assertRegex(folder, fixtures.UUID_PATTERN)
            self.assertNotEqual(folder, brush.uuid)
            self.assertEqual(folder_of(data, folder), brush.members, brush.name)
        manifest = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([m["uuid"] for m in manifest["members"]], plist["brushes"])
        for raw in ((self.out / "manifest.json").read_bytes(), (self.out / "CHECKLIST.md").read_bytes()):
            self.assertNotIn(b"\r", raw)
            self.assertNotIn(str(self.tmp).encode("utf-8"), raw)

    def test_verify_passes_on_a_fresh_build_and_prints_the_table(self):
        self.main("build", "sitting-1", "--confirm")
        code, out, err = self.main("verify", "sitting-1")
        self.assertEqual((code, err), (0, ""))
        lines = out.splitlines()
        self.assertTrue(lines[-1].startswith("VERIFIED   8 members, "))
        self.assertIn("folder names   8 in the manifest, 8 in the zip, all distinct, "
                      "all upper-case version-4 UUIDs", out)
        self.assertIn("  form     exact", out)
        self.assertIn("  name     'ROSW 1 Control'", out)
        self.assertIn("  keys     brushes, name", out)
        total = sum(len(brush.members) for brush in self.brushes.expected())
        self.assertEqual(out.count(" identical"), total + 8 + 1,
                         "every file, every single brush file, and the last line")
        self.assertNotIn("DIFFERENT", out)
        self.assertIn(f"{total + 1} entries; wanted: method 8, flags 0x0006, made by 0,0, needs 20", out)
        header_rows = [line for line in lines if re.match(r"^\s+8 0x0006\s+0,0\s+20\s+0\s+[01]\s+0\s+0  ", line)]
        self.assertEqual(len(header_rows), total + 1)
        self.assertEqual(len([row for row in header_rows if row.endswith("brushset.plist")]), 1)
        self.assertIn("known-bad/KNOWN-BAD_old-designer.brush   as copied", out)
        self.assertNotIn("INCOMPLETE", out)

    def test_verify_with_nothing_built(self):
        code, out, err = self.main("verify", "sitting-1")
        self.assertEqual(code, 2)
        self.assertIn("there is no built sitting", err)
        (self.out).mkdir(parents=True)
        (self.out / "manifest.json").write_text("{}", encoding="utf-8")
        (self.out / "ROSW-1-control.brushset").write_bytes(b"")
        code, _, err = self.main("verify", "sitting-1")
        self.assertEqual(code, 2)
        self.assertIn("manifest", err)

    def tampered(self, change):
        self.main("build", "sitting-1", "--confirm")
        change()
        code, out, err = self.main("verify", "sitting-1")
        self.assertEqual((code, err), (1, ""), out[-400:])
        self.assertTrue(out.rstrip("\n").splitlines()[-1].startswith("NOT VERIFIED   "))
        return out

    def test_verify_catches_a_member_file_that_is_not_its_source(self):
        def change():
            path = self.out / "ROSW-1-control.brushset"
            entries = entries_of(path.read_bytes())
            at = next(i for i, (name, _) in enumerate(entries) if name.endswith("/Shape.png"))
            entries[at] = (entries[at][0], entries[at][1] + b"\x00")
            path.write_bytes(zip_writer.write_zip(entries))

        out = self.tampered(change)
        self.assertIn("DIFFERENT", out)
        self.assertIn("is not its source file", out)
        self.assertIn("the set is not the file the manifest describes", out)

    def test_verify_catches_a_library_file_that_changed_since_the_build(self):
        def change():
            self.put("user/insecto-charcoal/Broken_Conte.brush", fixtures.brush_file(self.brushes.bar))

        out = self.tampered(change)
        self.assertIn("member 1: Brush.archive is not its source file", out)

    def test_verify_catches_a_missing_member_file_and_an_added_one(self):
        def change():
            path = self.out / "ROSW-1-control.brushset"
            entries = entries_of(path.read_bytes())
            folder = entries[0][0].split("/")[0]
            entries = [entry for entry in entries if not entry[0].endswith("QuickLook/Thumbnail.png")]
            entries.insert(0, (f"{folder}/Added.txt", b"added"))
            path.write_bytes(zip_writer.write_zip(entries))

        out = self.tampered(change)
        self.assertIn("(missing)", out)

    def test_verify_catches_a_container_zipfile_wrote(self):
        def change():
            path = self.out / "ROSW-1-control.brushset"
            path.write_bytes(fixtures.make_zip(entries_of(path.read_bytes())))

        out = self.tampered(change)
        self.assertIn("flags is 0, not 6", out)
        self.assertNotIn("is not its source file", out, "the members are still their sources")

    def test_verify_catches_a_plist_in_another_form_or_place(self):
        def change():
            path = self.out / "ROSW-1-control.brushset"
            entries = entries_of(path.read_bytes())
            plist = plistlib.loads(entries[-1][1])
            binary = plistlib.dumps(plist, fmt=plistlib.FMT_BINARY, sort_keys=False)
            path.write_bytes(zip_writer.write_zip([("brushset.plist", binary)] + entries[:-1]))

        out = self.tampered(change)
        self.assertIn("brushset.plist is not the last entry", out)
        self.assertIn("brushset.plist cannot be parsed", out)

    def test_verify_catches_a_folder_name_that_is_not_a_uuid_or_is_repeated(self):
        def change():
            path = self.out / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["members"][1]["uuid"] = manifest["members"][0]["uuid"].lower()
            path.write_text(json.dumps(manifest), encoding="utf-8")

        out = self.tampered(change)
        self.assertIn("NOT ALL UUIDs", out)
        self.assertIn("a folder name is not an upper-case version-4 UUID", out)

    def test_verify_catches_a_changed_single_file_and_a_changed_known_bad_copy(self):
        def change():
            (self.out / "singles" / "2-Steady.brush").write_bytes(fixtures.brush_file(self.brushes.hue))
            (self.out / "known-bad" / "KNOWN-BAD_old-designer.brush").write_bytes(b"something else")

        out = self.tampered(change)
        self.assertIn("singles/2-Steady.brush does not hold the source files at its root", out)
        self.assertIn("known-bad/KNOWN-BAD_old-designer.brush is not the file that was copied", out)

    def test_verify_does_not_follow_a_manifest_out_of_the_library(self):
        def change():
            path = self.out / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["members"][0]["source"]["container"] = "../downloads/Untitled_Brush.brush"
            path.write_text(json.dumps(manifest), encoding="utf-8")

        out = self.tampered(change)
        self.assertIn("outside the library", out)

    def test_building_again_gives_new_folder_names_and_replaces_its_own_files_only(self):
        self.main("build", "sitting-1", "--confirm")
        first = plistlib.loads(entries_of((self.out / "ROSW-1-control.brushset").read_bytes())[-1][1])
        (self.out / "singles" / "my-own-note.txt").write_text("keep me", encoding="utf-8")
        (self.out / "scratch.txt").write_text("keep me too", encoding="utf-8")
        # The library changes: the Earth set goes, so slot 8 takes another brush.
        (self.library / "official/earth/earth.brushset").unlink()
        code, out, err = self.main("build", "sitting-1", "--confirm", "--allow-substitutes")
        self.assertEqual((code, err), (0, ""))
        second = plistlib.loads(entries_of((self.out / "ROSW-1-control.brushset").read_bytes())[-1][1])
        self.assertFalse(set(first["brushes"]) & set(second["brushes"]))
        self.assertIn("removed   singles/8-Limestone.brush   (left by an earlier build)", out)
        self.assertFalse((self.out / "singles" / "8-Limestone.brush").exists())
        singles = sorted(p.name for p in (self.out / "singles").iterdir())
        self.assertEqual(len([name for name in singles if name.endswith(".brush")]), 8)
        self.assertIn("my-own-note.txt", singles)
        self.assertEqual((self.out / "scratch.txt").read_text(encoding="utf-8"), "keep me too")
        self.assertTrue(out.rstrip("\n").splitlines()[-1].startswith("VERIFIED   8 members, "))

    def test_a_later_build_without_a_known_bad_file_removes_the_earlier_copy(self):
        self.main("build", "sitting-1", "--confirm")
        self.assertTrue((self.out / "known-bad" / "KNOWN-BAD_old-designer.brush").is_file())
        code, out, _ = self.main("build", "sitting-1", "--confirm", "--known-bad", "")
        self.assertEqual(code, 0)
        self.assertIn("removed   known-bad/KNOWN-BAD_old-designer.brush", out)
        self.assertFalse((self.out / "known-bad" / "KNOWN-BAD_old-designer.brush").exists())

    def test_it_will_not_build_over_files_that_came_back(self):
        self.main("build", "sitting-1", "--confirm")
        (self.out / "returned" / "ROSW 1 Control.brushset").write_bytes(b"what came back")
        before = fixtures.tree_digest(self.out)
        code, out, err = self.main("build", "sitting-1", "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("holds files", err)
        self.assertIn("--out", err)
        self.assertEqual(out, "")
        self.assertEqual(fixtures.tree_digest(self.out), before)
        code, out, err = self.main("build", "sitting-1")
        self.assertEqual((code, out), (1, ""), "a dry run of a build that would be refused is refused too")
        self.assertIn("holds files", err)
        code, _, _ = self.main("verify", "sitting-1")
        self.assertEqual(code, 0, "checking what is there is still allowed")
        code, _, _ = self.main("build", "sitting-1", "--confirm", "--out", str(self.tmp / "second"))
        self.assertEqual(code, 0)

    def test_another_folder_with_out(self):
        elsewhere = self.tmp / "elsewhere" / "s1"
        code, out, err = self.main("build", "sitting-1", "--confirm", "--out", str(elsewhere))
        self.assertEqual((code, err), (0, ""))
        self.assertTrue((elsewhere / "ROSW-1-control.brushset").is_file())
        self.assertFalse(self.out.exists())
        code, _, _ = self.main("verify", "sitting-1", "--out", str(elsewhere))
        self.assertEqual(code, 0)
        inside = self.root / "device-tests" / "trial"
        code, _, _ = self.main("build", "sitting-1", "--confirm", "--out", str(inside))
        self.assertEqual(code, 0)
        self.assertTrue((inside / "CHECKLIST.md").is_file())

    def test_out_may_not_be_the_library_or_any_other_part_of_the_tool(self):
        for folder in ("library", "library/user/x", "vault", "app", "pipeline", "catalog", "."):
            before = fixtures.tree_digest(self.root)
            code, out, err = self.main("build", "sitting-1", "--confirm", "--out", str(self.root / folder))
            self.assertEqual(code, 2, folder)
            self.assertIn("--out", err)
            self.assertEqual(out, "")
            self.assertEqual(fixtures.tree_digest(self.root), before)
        outside = self.tmp / "other-library"
        (outside / "user" / "a").mkdir(parents=True)
        (outside / "user" / "a" / "Steady.brush").write_bytes(fixtures.brush_file(self.brushes.steady))
        code, _, err = self.main("build", "sitting-1", "--confirm", "--library", str(outside),
                                 "--out", str(outside / "tests"))
        self.assertEqual(code, 2)
        self.assertIn("inside the library", err)

    def test_the_default_folder_is_the_declared_one(self):
        paths = bc.resolve_paths()
        self.assertEqual(dt.default_out(paths, "sitting-1"), BRUSHES / "device-tests" / "sitting-1")
        self.assertEqual(dt.resolve_out(paths, None, "sitting-1"), BRUSHES / "device-tests" / "sitting-1")
        spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        self.assertEqual(spec["layout"]["device_tests"], dt.OUT_HOME)
        self.assertEqual(spec["device_test"]["written_to"], f"repo:brushes/{dt.OUT_HOME}/")
        self.assertIn(dt.SET_FILE, spec["device_test"]["files"])

    def test_no_library_no_brushes_and_a_pointer_are_exit_2(self):
        empty = self.tmp / "empty-root"
        (empty / "library").mkdir(parents=True)
        for root, words in ((self.tmp / "no-root", "there is no library"), (empty, "no brush file")):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = dt.main(["build", "sitting-1", "--root", str(root), "--known-bad", ""])
            self.assertEqual(code, 2)
            self.assertIn(words, err.getvalue())
            self.assertEqual(out.getvalue(), "")
        self.put("official/sweet-treats/sweet-treats.brushset", fixtures.LFS_POINTER)
        code, out, err = self.main("build", "sitting-1")
        self.assertEqual(code, 2)
        self.assertIn("git lfs pull", err)

    def test_usage_errors_are_exit_2(self):
        for argv in ([], ["build"], ["build", "sitting-9"], ["verify", "sitting-1", "--confirm"],
                     ["fetch", "sitting-1"], ["build", "sitting-1", "--out"]):
            with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(io.StringIO()):
                dt.main(argv)
            self.assertEqual(raised.exception.code, 2, argv)

    def test_the_known_bad_file_is_looked_for_in_the_home_downloads_folder(self):
        home = self.tmp / "home"
        (home / "Downloads").mkdir(parents=True)
        (home / "Downloads" / "Untitled_Brush.brush").write_bytes(self.bad_bytes)
        with mock.patch.object(Path, "home", return_value=home):
            code, out, _ = self.main("build", "sitting-1", known_bad=False)
        self.assertEqual(code, 0)
        self.assertIn(f"known-bad copied from {home / 'Downloads' / 'Untitled_Brush.brush'}", out)
        with mock.patch.object(Path, "home", return_value=self.tmp / "nobody"):
            code, out, _ = self.main("build", "sitting-1", known_bad=False)
        self.assertEqual(code, 0)
        self.assertIn("known-bad/ is left out", out)

    def test_it_runs_isolated_from_any_directory(self):
        result = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "build", "sitting-1", "--root", str(self.root),
             "--known-bad", str(self.bad)],
            cwd=str(self.tmp), capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", "replace"))
        text = result.stdout.decode("utf-8")
        self.assertIn("'Broken Cont\u00e9'", text, "the console is UTF-8 whatever the machine's code page")
        self.assertEqual(text.rstrip().splitlines()[-1], DRY_RUN)
        self.assertFalse(self.out.exists())


# ── a build that is not the control set ──────────────────────────────────────

class NotTheControlSet(LibraryCase):
    """Without the official sets five of the eight kinds are not in the library.
    Such a build is refused unless it is asked for by name."""

    def setUp(self):
        super().setUp()
        self.fill(official=False)

    def test_a_dry_run_shows_the_plan_and_is_refused(self):
        before = fixtures.tree_digest(self.tmp)
        code, out, err = self.main("build", "sitting-1")
        self.assertEqual(code, 1)
        self.assertIn("3 of 8 members are as specified, 5 are substitutes, 0 slots are empty.", out)
        self.assertIn("NOT THE CONTROL SET", out)
        self.assertNotIn(DRY_RUN, out, "a dry run of a build that would be refused is refused too")
        self.assertIn("error: this is not the control set: 5 of 8 members are substitutes.", err)
        self.assertIn("Nothing is written.", err)
        self.assertIn("python brushes/pipeline/fetch_base_library.py fetch --confirm", err)
        self.assertIn("--allow-substitutes", err)
        self.assertEqual(fixtures.tree_digest(self.tmp), before)

    def test_confirm_is_refused_and_writes_nothing(self):
        before = fixtures.tree_digest(self.tmp)
        code, out, err = self.main("build", "sitting-1", "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("this is not the control set", err)
        self.assertNotIn("WRITTEN", out)
        self.assertNotIn("VERIFIED", out)
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertFalse((self.root / "device-tests").exists())

    def test_empty_slots_are_refused_too(self):
        root = self.tmp / "small"
        target = root / "library" / "user" / "a" / "Set.brushset"
        target.parent.mkdir(parents=True)
        b = self.brushes
        target.write_bytes(fixtures.brushset_file("Three", [b.conte, b.steady, b.pencil]))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = dt.main(["build", "sitting-1", "--confirm", "--root", str(root), "--known-bad", ""])
        self.assertEqual(code, 1)
        self.assertIn("this is not the control set: 5 slots are empty.", err.getvalue())
        self.assertFalse((root / "device-tests").exists())
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = dt.main(["build", "sitting-1", "--confirm", "--allow-substitutes", "--root", str(root),
                            "--known-bad", ""])
        self.assertEqual(code, 0)
        manifest = json.loads((root / "device-tests" / "sitting-1" / "manifest.json").read_text(encoding="utf-8"))
        self.assertIs(manifest["complete"], False)
        self.assertEqual(len(manifest["unfilled"]), 5)

    def test_allow_substitutes_builds_it_and_says_what_it_is(self):
        code, out, err = self.main("build", "sitting-1", "--allow-substitutes")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out.rstrip("\n").splitlines()[-1], DRY_RUN)
        self.assertFalse((self.root / "device-tests").exists())
        code, out, err = self.main("build", "sitting-1", "--confirm", "--allow-substitutes")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("INCOMPLETE   this is not the control set: 5 of 8 members are substitutes "
                      "(slots 4, 5, 6, 7, 8).", out)
        self.assertIn("Allowed by --allow-substitutes.", out)
        last = out.rstrip("\n").splitlines()[-1]
        self.assertTrue(last.startswith("VERIFIED   8 members, "))
        self.assertTrue(last.endswith("NOT the control set (substitutes allowed)"))
        manifest = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertIs(manifest["complete"], False)
        self.assertEqual(manifest["substitutes"], [4, 5, 6, 7, 8])
        self.assertEqual([m["as_specified"] for m in manifest["members"]], [True] * 3 + [False] * 5)
        self.assertIn("**This build is not the full control set.**",
                      (self.out / "CHECKLIST.md").read_text(encoding="utf-8"))

    def test_verify_fails_such_a_build_unless_it_is_allowed(self):
        self.main("build", "sitting-1", "--confirm", "--allow-substitutes")
        code, out, err = self.main("verify", "sitting-1")
        self.assertEqual((code, err), (1, ""))
        self.assertIn("INCOMPLETE   this is not the control set", out)
        self.assertIn("problem: this is not the control set: 5 of 8 members are substitutes", out)
        self.assertTrue(out.rstrip("\n").splitlines()[-1].startswith("NOT VERIFIED   1 problem"))
        self.assertNotIn("DIFFERENT", out, "every file is still its source; only the choice is wrong")
        code, out, err = self.main("verify", "sitting-1", "--allow-substitutes")
        self.assertEqual((code, err), (0, ""))

    def test_verify_reads_the_members_not_the_flag(self):
        self.main("build", "sitting-1", "--confirm", "--allow-substitutes")
        path = self.out / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["complete"] = True
        path.write_text(json.dumps(manifest), encoding="utf-8")
        code, out, _ = self.main("verify", "sitting-1", "--allow-substitutes")
        self.assertEqual(code, 1)
        self.assertIn("the manifest's `complete` flag does not match its members", out)
        self.assertIn("5 of 8 members are substitutes", dt.incomplete(manifest))
        self.assertEqual(dt.incomplete({"members": [{"slot": 1, "as_specified": True}], "unfilled": []}),
                         "it holds 1 members, not 8")

    def test_the_full_library_needs_no_flag_and_takes_it_without_harm(self):
        self.fill()
        code, out, err = self.main("build", "sitting-1", "--confirm")
        self.assertEqual((code, err), (0, ""))
        self.assertNotIn("INCOMPLETE", out)
        self.assertNotIn("NOT THE CONTROL SET", out)
        manifest = json.loads((self.out / "manifest.json").read_text(encoding="utf-8"))
        self.assertIs(manifest["complete"], True)
        self.assertEqual(dt.incomplete(manifest), "")
        self.assertEqual(self.main("verify", "sitting-1")[0], 0)
        self.assertEqual(self.main("verify", "sitting-1", "--allow-substitutes")[0], 0)
        self.assertEqual(dt.refusal(self.build()), "")


# ── agreement with the rest of the tool ──────────────────────────────────────

class Agreement(unittest.TestCase):
    def setUp(self):
        self.spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        self.source = SCRIPT.read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)

    def test_the_caps_are_the_declared_ones(self):
        declared = self.spec["format"]["caps"]
        for name, value in dt.CAPS.items():
            self.assertEqual(value, declared[name], name)

    def test_the_eras_are_the_declared_ones(self):
        declared = self.spec["format"]["era_keys"]
        for era, count in declared.items():
            self.assertEqual(dt.ERA_BY_KEYS[count], era)
        self.assertEqual(set(dt.ERA_BY_KEYS.values()), set(declared))
        self.assertEqual({count for count, era in dt.ERA_BY_KEYS.items() if era == "M220"},
                         {220, 221, 222, 223})
        legacy = [count for era, count in declared.items()
                  if self.spec["format"]["era_family"][era] == "legacy"]
        self.assertEqual(max(legacy), dt.LEGACY_MAX_KEYS)

    def test_the_header_fields_it_checks_are_the_writers(self):
        self.assertEqual({label: wanted for label, _, wanted in dt.HEADER_FIELDS}, {
            "method": 8, "flags": 6, "made-by system": 0, "made-by version": 0, "needs version": 20,
            "external attr": 0, "extra": b"", "comment": b""})
        self.assertEqual({attribute: wanted for _, attribute, wanted in dt.HEADER_FIELDS}, {
            "compress_type": zip_writer.METHOD_DEFLATE, "flag_bits": zip_writer.FLAG_BITS,
            "create_system": zip_writer.CREATE_SYSTEM, "create_version": zip_writer.CREATE_VERSION,
            "extract_version": zip_writer.EXTRACT_VERSION, "external_attr": zip_writer.EXTERNAL_ATTR,
            "extra": b"", "comment": b""})

    def test_the_verbs_and_flags_are_the_declared_ones(self):
        declared = self.spec["cli"]["scripts"]["pipeline/device_tests.py"]
        parser = dt.build_parser()
        verbs = next(action for action in parser._actions if isinstance(action.choices, dict))
        self.assertEqual(list(verbs.choices), declared["verbs"])
        self.assertEqual(declared["confirm"], ["build"])
        roots = set(bc.FLAGS.values())
        for verb, sub in verbs.choices.items():
            flags = {flag for action in sub._actions for flag in action.option_strings}
            self.assertEqual(flags - roots - {"-h", "--help"}, set(declared["flags"][verb]), verb)
        self.assertIn("pipeline/device_tests.py build --confirm",
                      self.spec["persistence"]["writers"][f"repo:brushes/{dt.OUT_HOME}/**"])
        self.assertIn("pipeline/zip_writer.py", self.spec["cli"]["library_modules"])

    def test_the_junk_rule_is_the_one_ingest_uses(self):
        import ingest
        self.assertEqual(dt.JUNK_NAMES, ingest.JUNK_NAMES)
        self.assertEqual(dt.JUNK_FOLDERS, ingest.JUNK_FOLDERS)
        self.assertEqual(dt.EMPTY, ingest.EMPTY)
        self.assertNotIn(dt.EMPTY, dt.JUNK_NAMES)
        self.assertNotIn("_docs", dt.JUNK_FOLDERS, "a member under a folder of that name is still a member")
        self.assertIn("_docs", dt.SKIPPED_LIBRARY_FOLDERS)

    def test_it_is_a_script_in_the_house_form(self):
        self.assertIn('sys.path.insert(0, str(Path(__file__).resolve().parent))', self.source)
        self.assertTrue(self.source.rstrip().endswith('if __name__ == "__main__":\n    raise SystemExit(main())'))
        self.assertIn("bc.open_console()", self.source)
        self.assertIn("python brushes/pipeline/device_tests.py build sitting-1 [--out DIR]", self.source)
        self.assertNotIn("python3", self.source)
        self.assertNotIn(b"\r", SCRIPT.read_bytes())
        self.assertEqual(dt.DRY_RUN_LINE, DRY_RUN)
        self.assertEqual((dt.DeviceTestError.exit_code, dt.EnvironmentProblem.exit_code), (1, 2))

    def test_it_opens_no_connection_and_names_no_machine_path(self):
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertFalse(imported & {"urllib", "http", "socket", "ssl", "ftplib", "requests", "subprocess",
                                     "shutil", "tempfile"})
        self.assertNotRegex(self.source, r"[A-Za-z]:[\\/]Users")
        self.assertNotIn("utopi", self.source)

    def test_every_file_it_opens_itself_is_opened_for_reading(self):
        modes = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
                self.assertEqual(len(node.args), 2)
                modes.append(node.args[1].value)
        self.assertTrue(modes)
        self.assertEqual(set(modes), {"rb"}, "it writes through brush_common only")
        attributes = {node.attr for node in ast.walk(self.tree) if isinstance(node, ast.Attribute)}
        self.assertFalse(attributes & {"extract", "extractall", "write_text", "rmtree", "rename", "replace"}
                         - {"replace"})
        self.assertNotIn("extractall", self.source)
        self.assertNotIn(".extract(", self.source)


if __name__ == "__main__":
    unittest.main()
