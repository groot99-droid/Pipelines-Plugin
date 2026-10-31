"""pipeline/container.py: brush files as containers, read and written in memory.

Every input is built by tests/fixtures.py (zipfile and plistlib, independent of
the code under test), and every zip this module writes is read back with
zipfile, never compared with fixed bytes: deflate output depends on the zlib
build. The real library is read only by the opt-in class at the end, when
ROSW_BRUSHES_CORPUS names a folder of brush files.

    python -m unittest discover -s brushes/pipeline/tests
"""

from __future__ import annotations

import ast
import hashlib
import io
import os
import plistlib
import re
import struct
import sys
import unittest
import zipfile
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import fixtures  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import identity  # noqa: E402
import keyed_archive  # noqa: E402
import zip_writer  # noqa: E402
from bplist import ContainerError, LimitExceeded  # noqa: E402

CORPUS = os.environ.get("ROSW_BRUSHES_CORPUS", "")
UUID_FORM = re.compile(r"^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$")


def read_back(data):
    """[(name, bytes)] of every entry, as zipfile reads them."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return [(info.orig_filename, archive.read(info)) for info in archive.infolist()]


def infos(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return archive.infolist()


def full_brush(number=11, family="modern", **options):
    """A brush with every kind of member: Sub01, Reset (with Reset/Sub01),
    author files, `.empty` placeholders and a file nobody knows."""
    options.setdefault("extras", [("Extra/unknown.bin", b"\x00\x01unknown\xff")])
    return fixtures.make_brush("Full Brush", family, number=number, dual=True, reset=True,
                               author=True, empty=("", "Reset", "AuthorPicture"), **options)


def byte_archive(brush):
    """The fixture's archive written by the app's rules: it decodes as fidelity byte."""
    profile = "ios_legacy" if brush.family == "legacy" else "ios_modern"
    return keyed_archive.rule_encode(keyed_archive.decode(brush.archive), profile)


def set_flag(data, name, bit):
    """A copy of a zip with `bit` set in the flags of the entry `name`, in both
    of its headers: how an encrypted entry looks to a reader."""
    out = bytearray(data)
    encoded = name.encode("ascii")
    at = 0
    while True:
        at = out.find(b"PK\x03\x04", at)
        if at < 0:
            break
        size = struct.unpack_from("<H", out, at + 26)[0]
        if bytes(out[at + 30:at + 30 + size]) == encoded:
            struct.pack_into("<H", out, at + 6, struct.unpack_from("<H", out, at + 6)[0] | bit)
        at += 4
    at = 0
    while True:
        at = out.find(b"PK\x01\x02", at)
        if at < 0:
            break
        size = struct.unpack_from("<H", out, at + 28)[0]
        if bytes(out[at + 46:at + 46 + size]) == encoded:
            struct.pack_into("<H", out, at + 8, struct.unpack_from("<H", out, at + 8)[0] | bit)
        at += 4
    return bytes(out)


# ── reading a loose brush ────────────────────────────────────────────────────

class ReadingABrush(unittest.TestCase):
    def setUp(self):
        self.brush = full_brush()
        self.folder = container.read_brush(fixtures.brush_file(self.brush), hint="Full.brush")

    def test_the_members_are_the_zip_entries_in_order_with_their_bytes(self):
        self.assertEqual(self.folder.pairs(), self.brush.members)
        self.assertEqual(self.folder.paths(), self.brush.paths())
        self.assertEqual(self.folder.origin, "Full.brush")

    def test_the_typed_views(self):
        brush, folder = self.brush, self.folder
        self.assertEqual(folder.archive, brush.archive)
        self.assertEqual(folder.shape, brush.member("Shape.png"))
        self.assertEqual(folder.grain, brush.member("Grain.png"))
        self.assertEqual(folder.thumbnail, brush.member("QuickLook/Thumbnail.png"))
        self.assertEqual(folder.author_picture, brush.member("AuthorPicture/AuthorPicture.png"))
        self.assertEqual(folder.signature, brush.member("Signature/SignaturePicture.png"))
        self.assertIsNotNone(folder.author_picture)
        self.assertIsNotNone(folder.signature)

    def test_sub_and_reset_are_folders_of_their_own(self):
        sub = self.folder.sub
        self.assertEqual(sub.paths(), ["Brush.archive", "Shape.png"])
        self.assertEqual(sub.archive, self.brush.subs[0][0])
        reset = self.folder.reset
        self.assertEqual(reset.paths(), [path[len("Reset/"):] for path in self.brush.paths()
                                         if path.startswith("Reset/")])
        self.assertIn("Sub01/Brush.archive", reset.paths(), "the Reset tree keeps its own Sub01/")
        self.assertEqual(reset.sub.archive, self.brush.subs[0][0])
        self.assertNotEqual(reset.archive, self.folder.archive)
        self.assertIsNone(container.BrushFolder([("Brush.archive", b"a")]).sub)
        self.assertIsNone(container.BrushFolder([("Brush.archive", b"a")]).reset)

    def test_extras_are_every_member_no_view_claims(self):
        typed = {"Brush.archive", "Shape.png", "Grain.png", "QuickLook/Thumbnail.png",
                 "AuthorPicture/AuthorPicture.png", "Signature/SignaturePicture.png"}
        expected = [path for path in self.brush.paths()
                    if path not in typed and not path.startswith(("Sub01/", "Reset/"))]
        self.assertEqual(sorted(expected), [".empty", "AuthorPicture/.empty", "Extra/unknown.bin"])
        self.assertEqual(self.folder.extras, [(path, self.brush.member(path)) for path in expected])

    def test_an_unknown_member_warns_and_a_placeholder_does_not(self):
        self.assertEqual(self.folder.unknown_members(), ["Extra/unknown.bin"])
        self.assertEqual(len([w for w in self.folder.warnings if "unknown member" in w]), 1)
        self.assertFalse([w for w in self.folder.warnings if ".empty" in w])

    def test_a_texture_kept_under_its_own_name_raises_no_warning(self):
        named = fixtures.make_brush("Named", "modern", number=13, shape="named", grain="named")
        folder = container.read_brush(fixtures.brush_file(named))
        self.assertEqual(len(folder.extras), 2, "a named texture is an extra: no view has a slot for it")
        self.assertEqual(folder.unknown_members(), [])
        self.assertEqual(folder.warnings, [])

    def test_each_member_keeps_how_the_zip_stored_it(self):
        data = fixtures.brush_file(self.brush, stored=("Shape.png",))
        folder = container.read_brush(data)
        by_name = {info.orig_filename: info for info in infos(data)}
        for member in folder.members:
            info = by_name[member.path]
            self.assertEqual(member.date_time, tuple(info.date_time))
            self.assertEqual(member.form, zip_writer.form_of(info.compress_type, info.flag_bits))
        self.assertEqual(folder.member("Shape.png").form, "stored")

    def test_a_set_is_not_a_brush(self):
        data = fixtures.brushset_file("S", [self.brush])
        with self.assertRaises(ContainerError) as caught:
            container.read_brush(data)
        self.assertEqual(caught.exception.code, "not_a_brush")


# ── reading a set ────────────────────────────────────────────────────────────

class ReadingASet(unittest.TestCase):
    def setUp(self):
        self.brushes = fixtures.standard_official_brushes()

    def read(self, data):
        return container.read_brushset(data, hint="Set.brushset")

    def test_name_order_and_members(self):
        user = fixtures.standard_user_brushes()
        brush_set = self.read(fixtures.brushset_file(fixtures.USER_SET_NAME, user))
        self.assertEqual(brush_set.name, "Demo Set ", "the trailing space is kept")
        self.assertEqual(brush_set.uuids(), [b.uuid for b in user])
        for (uuid, folder), brush in zip(brush_set.brushes, user):
            self.assertEqual(folder.pairs(), brush.members)
            self.assertEqual(folder.source_uuid, uuid)
        self.assertEqual(brush_set.entry_order[-1], "brushset.plist")
        self.assertEqual(brush_set.warnings, [])
        self.assertEqual(brush_set.skipped, [])

    def test_the_plist_is_the_only_brush_order(self):
        reordered = list(reversed(self.brushes))
        data = fixtures.brushset_file("S", self.brushes, zip_order=reordered, plist_first=True)
        brush_set = self.read(data)
        self.assertEqual(brush_set.uuids(), [b.uuid for b in self.brushes])
        self.assertEqual(brush_set.entry_order[0], "brushset.plist")
        self.assertEqual([name.split("/", 1)[0] for name in brush_set.entry_order[1:]][0],
                         reordered[0].uuid, "entry_order is the zip's order")

    def test_extra_plist_keys_are_kept_in_the_order_read(self):
        data = fixtures.brushset_file("S", self.brushes, plist_extra={"iconName": "fixture-icon"})
        brush_set = self.read(data)
        self.assertEqual(brush_set.plist_extra, {"iconName": "fixture-icon"})
        self.assertEqual(brush_set.plist_order, ("brushes", "name", "iconName"))

    def test_the_apps_own_key_order_is_kept_too(self):
        """Earth and Chinese Calligraphy write `iconName` between `brushes` and `name`."""
        plist = plistlib.dumps({"brushes": [b.uuid for b in self.brushes], "iconName": "icon",
                                "name": "Earth"}, fmt=plistlib.FMT_XML, sort_keys=False)
        entries = [(f"{b.uuid}/{path}", data) for b in self.brushes for path, data in b.members]
        brush_set = self.read(fixtures.make_zip(entries + [("brushset.plist", plist)]))
        self.assertEqual(brush_set.plist_order, ("brushes", "iconName", "name"))
        brush_set.name = "Earth renamed"
        written = dict(read_back(container.write_brushset(brush_set)))["brushset.plist"]
        self.assertEqual(list(plistlib.loads(written)), ["brushes", "iconName", "name"])
        self.assertEqual(plistlib.loads(written)["iconName"], "icon")

    def test_a_binary_plist_is_read(self):
        brush_set = self.read(fixtures.brushset_file("Binary", self.brushes, binary_plist=True))
        self.assertEqual((brush_set.name, brush_set.uuids()), ("Binary", [b.uuid for b in self.brushes]))

    def test_one_top_folder_around_the_set(self):
        data = fixtures.brushset_file("S", self.brushes, prefix="S.brushset/")
        brush_set = self.read(data)
        self.assertEqual(brush_set.prefix, "S.brushset/")
        self.assertEqual(brush_set.uuids(), [b.uuid for b in self.brushes])
        names = [name for name, _ in read_back(container.write_brushset(brush_set))]
        self.assertFalse([name for name in names if name.startswith("S.brushset/")],
                         "a set is written without the folder it came in")

    def test_a_folder_the_plist_does_not_list_is_kept_and_flagged(self):
        entries = [(f"{b.uuid}/{path}", data) for b in self.brushes for path, data in b.members]
        plist = fixtures.brushset_plist("S", [self.brushes[1].uuid])
        brush_set = self.read(fixtures.make_zip(entries + [("brushset.plist", plist)]))
        self.assertEqual(brush_set.uuids()[0], self.brushes[1].uuid)
        self.assertEqual(sorted(brush_set.uuids()), sorted(b.uuid for b in self.brushes))
        self.assertEqual(len([w for w in brush_set.warnings if "not listed" in w]), 2)

    def test_a_folder_the_set_does_not_hold(self):
        brush_set = self.read(fixtures.hostile_files()["missing-folder.brushset"])
        self.assertEqual(len(brush_set.brushes), 1)
        self.assertTrue([w for w in brush_set.warnings if "does not hold" in w])

    def test_a_repeated_name_keeps_the_first_with_a_warning(self):
        data = fixtures.brushset_file("S", self.brushes, double_empty=True, stored=True)
        brush_set = self.read(data)
        self.assertEqual([folder.pairs() for _, folder in brush_set.brushes],
                         [b.members for b in self.brushes])
        self.assertEqual(len([w for w in brush_set.warnings if "the first wins" in w]), 1)
        first = fixtures.make_zip([("Brush.archive", self.brushes[0].archive), ("x.bin", b"first"),
                                   ("x.bin", b"second")])
        self.assertEqual(container.read_brush(first).get("x.bin"), b"first")

    def test_stored_entries_are_read(self):
        brush_set = self.read(fixtures.brushset_file("S", self.brushes, stored=True))
        self.assertEqual([folder.pairs() for _, folder in brush_set.brushes],
                         [b.members for b in self.brushes])
        forms = {m.form for _, folder in brush_set.brushes for m in folder.members}
        self.assertEqual(forms, {"stored"})

    def test_a_stray_file_and_a_folder_with_no_archive_belong_to_no_brush(self):
        entries = [(f"{b.uuid}/{path}", data) for b in self.brushes for path, data in b.members]
        entries += [("readme.txt", b"stray"), ("Loose/Shape.png", fixtures.make_png()),
                    ("brushset.plist", fixtures.brushset_plist("S", [b.uuid for b in self.brushes]))]
        brush_set = self.read(fixtures.make_zip(entries))
        skipped = dict(brush_set.skipped)
        self.assertIn("readme.txt", skipped)
        self.assertIn("Loose/", skipped)
        names = [name for name, _ in read_back(container.write_brushset(brush_set))]
        self.assertNotIn("readme.txt", names)
        self.assertFalse([name for name in names if name.startswith("Loose/")])

    def test_a_brush_is_not_a_set(self):
        with self.assertRaises(ContainerError) as caught:
            self.read(fixtures.brush_file(self.brushes[0]))
        self.assertEqual(caught.exception.code, "not_a_brushset")


# ── read_any: sniffing and nesting ───────────────────────────────────────────

class ReadAny(unittest.TestCase):
    def setUp(self):
        self.brush = fixtures.make_brush("Nested", number=31)
        self.brush_bytes = fixtures.brush_file(self.brush)
        self.set_bytes = fixtures.brushset_file("Nested Set", fixtures.standard_user_brushes())

    def test_by_content_not_by_name(self):
        self.assertIsInstance(container.read_any(self.brush_bytes, "x.brushset")[0], container.BrushFolder)
        self.assertIsInstance(container.read_any(self.set_bytes, "x.brush")[0], container.BrushSet)

    def test_a_vendor_zip_with_junk_and_nested_files(self):
        vendor = fixtures.make_zip([
            ("Pack/", b""), ("__MACOSX/Pack/._Nested.brush", b"junk"), ("Pack/.DS_Store", b"junk"),
            ("Pack/Nested.brush", self.brush_bytes), ("Pack/Set.brushset.zip", self.set_bytes),
            ("Pack/guide.pdf", b"%PDF-1.4")])
        found = container.read_any(vendor, "Pack.zip")
        self.assertEqual([type(item).__name__ for item in found], ["BrushFolder", "BrushSet"])
        self.assertEqual([item.origin for item in found],
                         ["Pack.zip!/Pack/Nested.brush", "Pack.zip!/Pack/Set.brushset.zip"])
        self.assertEqual(found[0].pairs(), self.brush.members)
        self.assertEqual(found.skipped, [])

    def test_nesting_stops_at_depth_three(self):
        inner = self.brush_bytes
        name = "a.brush"
        for depth in range(1, 5):
            inner = fixtures.make_zip([(name, inner)])
            name = f"level{depth}.zip"
            found = container.read_any(inner, "outer.zip")
            if depth <= 3:
                self.assertEqual(len(found), 1, depth)
            else:
                self.assertEqual(len(found), 0)
                self.assertIn("nested more than 3", found.skipped[0][1])

    def test_a_nested_file_that_cannot_be_read_is_listed_and_the_rest_read(self):
        vendor = fixtures.make_zip([("bad.brush", b"PK\x03\x04 not really"),
                                    ("pointer.brushset", fixtures.LFS_POINTER),
                                    ("../escape.brush", self.brush_bytes),
                                    ("good.brush", self.brush_bytes),
                                    ("empty.brushset", fixtures.make_zip([("note.txt", b"x")]))])
        found = container.read_any(vendor, "v.zip")
        self.assertEqual(len(found), 1)
        reasons = dict(found.skipped)
        self.assertIn("v.zip!/bad.brush", reasons)
        self.assertIn("Git LFS", reasons["v.zip!/pointer.brushset"])
        self.assertIn("..", reasons["v.zip!/../escape.brush"])
        self.assertIn("no brushset.plist", reasons["v.zip!/empty.brushset"])

    def test_a_zip_with_nothing_in_it_finds_nothing(self):
        found = container.read_any(fixtures.make_zip([("a.pdf", b"x")]), "docs.zip")
        self.assertEqual((list(found), found.skipped), ([], []))

    def test_a_pointer_and_a_file_that_is_not_a_zip(self):
        with self.assertRaises(ContainerError) as caught:
            container.read_any(fixtures.LFS_POINTER, "p.brushset")
        self.assertEqual(caught.exception.code, "lfs_pointer")
        self.assertIn("git lfs pull", str(caught.exception))
        for data in (b"PK\x03\x04 this only starts like a zip", b"", b"plain text"):
            with self.assertRaises(ContainerError) as caught:
                container.read_any(data, "x.brush")
            self.assertEqual(caught.exception.code, "not_a_zip")
        with self.assertRaises(ContainerError):
            container.read_any("text", "x")

    def test_nothing_is_ever_extracted(self):
        with mock.patch.object(zipfile.ZipFile, "extract", side_effect=AssertionError("extract")), \
                mock.patch.object(zipfile.ZipFile, "extractall", side_effect=AssertionError("extractall")):
            found = container.read_any(fixtures.make_zip([("a.brush", self.brush_bytes),
                                                          ("s.brushset", self.set_bytes)]), "x.zip")
        self.assertEqual(len(found), 2)


# ── hostile input and the caps ───────────────────────────────────────────────

class HostileInput(unittest.TestCase):
    def setUp(self):
        self.files = fixtures.hostile_files()

    def test_names_that_point_outside_are_skipped_and_the_rest_read(self):
        brush_set = container.read_brushset(self.files["traversal.brushset"])
        skipped = dict(brush_set.skipped)
        for name in ("../outside.txt", "/absolute.txt", "C:\\drive.txt"):
            self.assertIn(name, skipped)
        self.assertTrue([name for name in skipped if name.endswith("/../../climb.txt")])
        self.assertEqual(len(brush_set.brushes), 1)
        written = [name for name, _ in read_back(container.write_brushset(brush_set))]
        self.assertFalse([name for name in written if ".." in name or "\\" in name or name.startswith("/")])

    def test_a_backslash_is_judged_on_the_name_as_stored(self):
        brush = fixtures.make_brush("Slash", number=41)
        data = fixtures.make_zip(brush.members + [("Sub\\evil.png", b"x")])
        folder = container.read_brush(data)
        self.assertEqual(dict(folder.skipped), {"Sub\\evil.png": "an entry name with a backslash"})
        self.assertEqual(folder.pairs(), brush.members)

    def test_an_encrypted_entry_is_skipped_unread(self):
        brush = fixtures.make_brush("Locked", number=42)
        data = set_flag(fixtures.brush_file(brush), "Grain.png", 0x1)
        with mock.patch.object(zipfile.ZipFile, "open", autospec=True,
                               side_effect=zipfile.ZipFile.open) as opened:
            folder = container.read_brush(data)
        self.assertEqual(dict(folder.skipped), {"Grain.png": "an encrypted entry"})
        self.assertNotIn("Grain.png", folder)
        self.assertFalse([c for c in opened.call_args_list if getattr(c.args[1], "orig_filename", "") == "Grain.png"])

    def test_plists_that_are_not_a_set(self):
        with self.assertRaises(ContainerError) as caught:
            container.read_brushset(self.files["bare-array-plist.brushset"])
        self.assertEqual(caught.exception.code, "bad_plist")
        brush = fixtures.make_brush("P", number=43)
        entries = [(f"{brush.uuid}/{p}", d) for p, d in brush.members]
        for plist in (plistlib.dumps({"name": "x"}), plistlib.dumps({"brushes": [1], "name": "x"}),
                      plistlib.dumps({"brushes": [], "name": 7}), b"<?xml version='1.0'?><plist>",
                      b'<?xml version="1.0"?><!DOCTYPE plist [<!ENTITY a "aaaa">]><plist><dict>'
                      b"<key>name</key><string>&a;</string><key>brushes</key><array/></dict></plist>",
                      b"bplist00 truncated"):
            with self.assertRaises(ContainerError, msg=plist[:40]) as caught:
                container.read_brushset(fixtures.make_zip(entries + [("brushset.plist", plist)]))
            self.assertEqual(caught.exception.code, "bad_plist")

    def test_files_that_hold_no_brush(self):
        for name in ("no-archive.brush", "empty.brushset"):
            with self.assertRaises(ContainerError, msg=name):
                container.read_brush(self.files[name])
            self.assertEqual(list(container.read_any(self.files[name], name)), [])
        with self.assertRaises(ContainerError) as caught:
            container.read_brush(self.files["not-a-zip.brush"])
        self.assertEqual(caught.exception.code, "not_a_zip")

    def test_archives_that_do_not_decode_are_still_members(self):
        for name in ("string-top-archive.brush", "wrong-magic.brush", "truncated-archive.brush"):
            folder = container.read_brush(self.files[name])
            self.assertIsNotNone(folder.archive, name)
            self.assertEqual(container.archive_texture_names(folder.archive),
                             {"shape": None, "grain": None})
            self.assertEqual(read_back(container.write_brush(folder)), folder.pairs())

    def test_the_ratio_cap(self):
        with self.assertRaises(LimitExceeded) as caught:
            container.read_brush(fixtures.ratio_bomb(20))
        self.assertEqual(caught.exception.code, "ratio")
        self.assertIsInstance(caught.exception, ContainerError)

    def test_each_cap_by_its_name(self):
        brush = fixtures.make_brush("Caps", number=44)
        data = fixtures.brush_file(brush)
        biggest = max(len(d) for _, d in brush.members)
        total = sum(len(d) for _, d in brush.members)
        cases = {"zip_entries": len(brush.members) - 1, "archive_bytes": len(brush.archive) - 1,
                 "entry_bytes": biggest - 1, "total_bytes": total - 1, "upload_bytes": len(data) - 1}
        for cap, value in cases.items():
            limits = dict(container.CAPS, **{cap: value})
            with self.assertRaises(LimitExceeded, msg=cap) as caught:
                container.read_brush(data, limits=limits)
            self.assertEqual(caught.exception.code, cap)
            with self.assertRaises(LimitExceeded, msg=cap):
                container.read_any(data, "x", limits=limits)
        self.assertEqual(container.read_brush(data).pairs(), brush.members)

    def test_the_budget_is_per_file(self):
        budget = container.Budget(10)
        budget.spend(6)
        budget.spend(4)
        with self.assertRaises(LimitExceeded) as caught:
            budget.spend(1)
        self.assertEqual(caught.exception.code, "total_bytes")
        self.assertEqual(container.Budget().left, container.CAPS["total_bytes"])

    def test_the_caps_are_the_declared_ones(self):
        mib = 1024 * 1024
        self.assertEqual(container.CAPS, {
            "zip_entries": 5000, "archive_bytes": mib, "entry_bytes": 64 * mib,
            "total_bytes": 2048 * mib, "ratio": 200, "ratio_min_bytes": 16 * mib,
            "nesting_depth": 3, "upload_bytes": 512 * mib})
        self.assertIs(container.DEFAULT_LIMITS, container.CAPS)
        self.assertEqual(container.ZIP_EPOCH, zip_writer.DEFAULT_DATE_TIME)


# ── writing ──────────────────────────────────────────────────────────────────

class Writing(unittest.TestCase):
    def setUp(self):
        self.brushes = fixtures.standard_official_brushes()
        self.data = fixtures.brushset_file("Write Me", self.brushes, plist_extra={"iconName": "i"},
                                           double_empty=True, stored=(f"{self.brushes[2].uuid}/Brush.archive",))
        self.brush_set = container.read_brushset(self.data)

    def test_every_member_comes_back_byte_for_byte(self):
        written = dict(read_back(container.write_brushset(self.brush_set)))
        for brush in self.brushes:
            for path, data in brush.members:
                self.assertEqual(written.pop(f"{brush.uuid}/{path}"), data, path)
        self.assertEqual(list(written), ["brushset.plist"])

    def test_the_canonical_order(self):
        names = [name for name, _ in read_back(container.write_brushset(self.brush_set))]
        self.assertEqual(names[-1], "brushset.plist")
        first = self.brushes[0]
        paths = [name.split("/", 1)[1] for name in names if name.startswith(first.uuid + "/")]
        self.assertEqual(paths[:4], ["Brush.archive", "Shape.png", "Grain.png", "QuickLook/Thumbnail.png"])
        groups = [("AuthorPicture/",), ("Signature/",), ("Sub01/",), ("Reset/",)]
        last = 3
        for (prefix,) in groups:
            positions = [n for n, path in enumerate(paths) if path.startswith(prefix)]
            self.assertTrue(positions and min(positions) > last, prefix)
            self.assertEqual(positions, list(range(positions[0], positions[-1] + 1)), prefix)
            last = max(positions)
        reset = [path for path in paths if path.startswith("Reset/")]
        self.assertEqual(reset[0], "Reset/Brush.archive")
        self.assertLess(reset.index("Reset/QuickLook/Thumbnail.png"), reset.index("Reset/Sub01/Brush.archive"))
        others = paths[last + 1:]
        self.assertEqual(others, sorted(others))
        self.assertEqual([name.split("/", 1)[0] for name in names[:-1] if "/" in name],
                         sorted([name.split("/", 1)[0] for name in names[:-1] if "/" in name],
                                key=[b.uuid for b in self.brushes].index), "brushes in plist order, contiguous")

    def test_preserve_order_replays_the_source(self):
        data = fixtures.brushset_file("S", self.brushes, zip_order=list(reversed(self.brushes)),
                                      plist_first=True)
        brush_set = container.read_brushset(data)
        names = [name for name, _ in read_back(container.write_brushset(brush_set, preserve_order=True))]
        self.assertEqual(names, [name for name, _ in read_back(data)])

    def test_preserve_order_puts_a_new_member_after_its_folder(self):
        uuid, folder = self.brush_set.brushes[1]
        folder.set("Shape.png", fixtures.make_png())
        written = [n for n, _ in read_back(container.write_brushset(self.brush_set, preserve_order=True))]
        own = [n for n in written if n.startswith(uuid + "/")]
        self.assertEqual(own[-1], f"{uuid}/Shape.png")
        self.assertEqual(written.index(own[-1]), written.index(own[-2]) + 1)

    def test_dates_and_forms(self):
        names_dates = {i.orig_filename: i.date_time for i in infos(container.write_brushset(self.brush_set))}
        self.assertEqual(set(names_dates.values()), {container.ZIP_EPOCH})
        kept = container.write_brushset(self.brush_set, source_dates=True)
        self.assertEqual({i.date_time for i in infos(kept)}, {fixtures.ZIP_DATE})
        when = (2026, 10, 29, 12, 0, 0)
        self.assertEqual({i.date_time for i in infos(container.write_brushset(self.brush_set, mtime=when))},
                         {when})
        by_name = {i.orig_filename: i for i in infos(kept)}
        stored = by_name[f"{self.brushes[2].uuid}/Brush.archive"]
        self.assertEqual(stored.compress_type, zipfile.ZIP_STORED, "a stored member is written back stored")
        for info in by_name.values():
            self.assertEqual((info.create_system, info.create_version, info.extract_version,
                              info.external_attr, info.extra, info.comment), (0, 0, 20, 0, b"", b""))

    def test_a_member_made_here_is_written_in_the_default_form(self):
        folder = container.BrushFolder.from_parts(b"archive", shape=fixtures.make_png())
        made = infos(container.write_brush(folder))
        self.assertEqual({(i.compress_type, i.flag_bits) for i in made}, {(8, zip_writer.FLAG_BITS)})

    def test_the_plist_is_kept_while_the_set_is_unchanged(self):
        source = dict(read_back(self.data))["brushset.plist"]
        self.assertEqual(dict(read_back(container.write_brushset(self.brush_set)))["brushset.plist"], source)
        binary = container.read_brushset(fixtures.brushset_file("B", self.brushes, binary_plist=True))
        kept = dict(read_back(container.write_brushset(binary)))["brushset.plist"]
        self.assertTrue(kept.startswith(b"bplist00"), "an unchanged binary plist is written back as it was")
        binary.name = "B2"
        remade = dict(read_back(container.write_brushset(binary)))["brushset.plist"]
        self.assertTrue(remade.startswith(b"<?xml"))
        self.assertEqual(plistlib.loads(remade), {"brushes": binary.uuids(), "name": "B2"})

    def test_unknown_plist_keys_survive_a_change(self):
        new = container.new_uuid()
        self.brush_set.brushes[0] = (new, self.brush_set.brushes[0][1])
        plist = plistlib.loads(dict(read_back(container.write_brushset(self.brush_set)))["brushset.plist"])
        self.assertEqual(plist["iconName"], "i")
        self.assertEqual(plist["brushes"][0], new)
        self.assertEqual(list(plist), ["brushes", "name", "iconName"])

    def test_a_loose_brush(self):
        brush = full_brush(number=51)
        folder = container.read_brush(fixtures.brush_file(brush))
        self.assertEqual(sorted(read_back(container.write_brush(folder))), sorted(brush.members))
        self.assertEqual(read_back(container.write_brush(folder, preserve_order=True)), brush.members)

    def test_what_a_writer_refuses(self):
        folder = container.BrushFolder([("Shape.png", b"x")])
        with self.assertRaises(ContainerError):
            container.write_brush(folder)
        good = container.BrushFolder([("Brush.archive", b"a")])
        for brushes, code in (([("A/B", good)], "bad_folder"), ([("", good)], "bad_folder"),
                              ([("A", good), ("A", good)], "bad_folder"),
                              ([("caf\u00e9", good)], "bad_folder"), ([("A", folder)], "no_archive")):
            with self.assertRaises(ContainerError, msg=repr(brushes)) as caught:
                container.write_brushset(container.BrushSet("S", brushes))
            self.assertEqual(caught.exception.code, code)
        odd = container.BrushFolder([("Brush.archive", b"a"), ("caf\u00e9.png", b"x")])
        with self.assertRaises(ContainerError) as caught:
            container.write_brush(odd)
        self.assertEqual(caught.exception.code, "write", "a name that is not ASCII is not written")
        with self.assertRaises(ContainerError):
            container.BrushFolder([("a", b"1"), ("a", b"2")])

    def test_a_new_uuid(self):
        made = {container.new_uuid() for _ in range(50)}
        self.assertEqual(len(made), 50)
        for uuid in made:
            self.assertRegex(uuid, UUID_FORM)

    def test_safe_filename(self):
        self.assertEqual(container.safe_filename("Sargent\u2019s Oils"), "sargents-oils")
        self.assertEqual(container.safe_filename("\u6d53\u58a8"), "untitled")
        self.assertEqual(container.safe_filename("CON"), "x-con")
        self.assertEqual(container.safe_filename(None), "untitled")

    def test_no_zip_is_written_with_zipfile(self):
        tree = ast.parse((PIPELINE / "container.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                self.assertNotIn(node.attr, ("writestr", "extract", "extractall", "open_write"))
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "ZipFile":
                self.assertEqual(len(node.args), 1, "ZipFile is only ever opened to read")
                self.assertEqual(node.keywords, [])


class ThePlistText(unittest.TestCase):
    def test_the_form_the_app_writes(self):
        made = container.render_plist("Ün\u00ef & <Set> \U0001f4a7 ", ["8E7FA79A-900C-47D9-9805-F226BE3C4B04"])
        expected = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                    '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                    '<plist version="1.0">\n<dict>\n\t<key>brushes</key>\n\t<array>\n'
                    '\t\t<string>8E7FA79A-900C-47D9-9805-F226BE3C4B04</string>\n\t</array>\n'
                    '\t<key>name</key>\n\t<string>Ün\u00ef &amp; &lt;Set&gt; \U0001f4a7 </string>\n'
                    '</dict>\n</plist>\n').encode("utf-8")
        self.assertEqual(made, expected)

    def test_a_name_that_cannot_be_written(self):
        with self.assertRaises(ContainerError):
            container.render_plist("bell\x07", [])


# ── textures and identity ────────────────────────────────────────────────────

class TextureResolution(fixtures.BrushCase):
    def folder(self, members, shape=None, grain=None, family="legacy"):
        archive = fixtures.make_archive(family, "T", bundled_shape=shape, bundled_grain=grain)
        return container.BrushFolder([("Brush.archive", archive)] + list(members))

    def test_the_order(self):
        png, other = fixtures.make_png(4, 4), fixtures.make_png(5, 5)
        bundled = self.tmp / "bundled"
        bundled.mkdir()
        (bundled / "Supplied.png").write_bytes(b"supplied")
        cases = [
            # (members, shape name, grain name) -> (shape source, grain source)
            ([("Shape.png", png), ("Named.png", other)], "Named.png", None, ("embedded", "none")),
            ([("Named.png", other)], "Named.png", "Named.png", ("embedded", "embedded")),
            ([], "Supplied.png", "Supplied.png", ("bundled-supplied", "bundled-supplied")),
            ([], "Brush-Preset-Hard.png", container.BLANK_GRAIN, ("bundled", "blank")),
            ([(container.BLANK_GRAIN, png)], None, container.BLANK_GRAIN, ("none", "embedded")),
            ([("Sub/Named.png", png)], "Sub/Named.png", None, ("bundled", "none")),
            ([("named.png", png)], "Named.png", None, ("bundled", "none")),
            ([("Grain.png", png)], None, "Brush-Preset-Blank.png", ("none", "embedded")),
        ]
        for members, shape, grain, sources in cases:
            folder = self.folder(members, shape, grain)
            got = container.resolve_textures(folder, bundled=bundled)
            self.assertEqual((got["shape"][1], got["grain"][1]), sources, (members, shape, grain))
        folder = self.folder([("Shape.png", png), ("Named.png", other)], "Named.png")
        self.assertEqual(container.resolve_textures(folder)["shape"], (png, "embedded"), "Shape.png wins")
        folder = self.folder([], "Supplied.png")
        self.assertEqual(container.resolve_textures(folder, bundled=bundled)["shape"], (b"supplied", "bundled-supplied"))
        self.assertEqual(container.resolve_textures(folder)["shape"], (None, "bundled"))
        self.assertEqual(container.resolve_textures(folder, bundled={"Supplied.png": b"s"})["shape"],
                         (b"s", "bundled-supplied"))

    def test_a_bundled_name_is_never_a_path(self):
        (self.tmp / "secret.png").write_bytes(b"secret")
        bundled = self.tmp / "bundled"
        bundled.mkdir()
        for name in ("../secret.png", "..\\secret.png", str(self.tmp / "secret.png")):
            folder = self.folder([], name)
            self.assertEqual(container.resolve_textures(folder, bundled=bundled)["shape"], (None, "bundled"), name)
        self.assertEqual(container.resolve_textures(self.folder([], "x.png"), bundled=self.tmp / "missing")["shape"],
                         (None, "bundled"))

    def test_params_and_the_archive_say_the_same(self):
        for brush in fixtures.standard_user_brushes() + fixtures.standard_official_brushes():
            folder = container.BrushFolder(brush.members)
            params = brush_model.decode(brush.archive).params
            self.assertEqual(container.resolve_textures(folder, params), container.resolve_textures(folder))
            got = container.resolve_textures(folder)
            self.assertEqual((got["shape"][1], got["grain"][1]), (brush.shape_source, brush.grain_source),
                             brush.name)
            self.assertEqual((got["shape"][0], got["grain"][0]), (brush.shape, brush.grain), brush.name)
        self.assertEqual(container.texture_names({"bundledShapePath": {"string": "W.png", "wrapper": "NSMutableString"},
                                                  "bundledGrainPath": ""}),
                         {"shape": "W.png", "grain": None})


class Identity(unittest.TestCase):
    """identity.py's formula, fed from the container's members, equals the same
    formula fed from what fixtures.py says went into each brush."""

    def ids(self, brush):
        folder = container.BrushFolder(brush.members)
        return (identity.content_sha256(*container.identity_inputs(folder)),
                identity.content_sha256(brush.archive, brush.shape, brush.grain, brush.subs))

    def test_every_fixture_brush(self):
        brushes = (fixtures.standard_user_brushes() + fixtures.standard_official_brushes()
                   + [full_brush(61), full_brush(62, "legacy"),
                      fixtures.make_brush("Named Dual", "modern", number=63, shape="named", grain="named", dual=True)])
        for brush in brushes:
            mine, theirs = self.ids(brush)
            self.assertEqual(mine, theirs, brush.name)

    def test_what_does_not_enter_it(self):
        brush = full_brush(64)
        base = identity.content_sha256(*container.identity_inputs(container.BrushFolder(brush.members)))
        for path in ("QuickLook/Thumbnail.png", "Reset/Brush.archive", "AuthorPicture/AuthorPicture.png",
                     "Signature/SignaturePicture.png", ".empty", "Extra/unknown.bin"):
            folder = container.BrushFolder(brush.members)
            folder.set(path, b"changed")
            self.assertEqual(identity.content_sha256(*container.identity_inputs(folder)), base, path)
        for path in ("Brush.archive", "Shape.png", "Grain.png", "Sub01/Brush.archive", "Sub01/Shape.png"):
            folder = container.BrushFolder(brush.members)
            folder.set(path, b"changed")
            self.assertNotEqual(identity.content_sha256(*container.identity_inputs(folder)), base, path)

    def test_every_secondary_in_ascending_order(self):
        brush = full_brush(65)
        sub2 = fixtures.make_archive("modern", "Second", bundled_grain=container.BLANK_GRAIN)
        shape2 = fixtures.make_png(3, 3)
        folder = container.BrushFolder(brush.members + [("Sub02/Brush.archive", sub2), ("Sub02/Shape.png", shape2)])
        archive, shape, grain, subs = container.identity_inputs(folder)
        self.assertEqual(subs, [brush.subs[0], (sub2, shape2, None)])
        self.assertEqual(identity.content_sha256(archive, shape, grain, subs),
                         identity.content_sha256(brush.archive, brush.shape, brush.grain,
                                                 brush.subs + [(sub2, shape2, None)]))
        self.assertIn("Sub02/", folder.unknown_members())
        self.assertTrue([w for w in folder.member_warnings() if "beyond Sub01" in w])
        self.assertIn(("Sub02/Brush.archive", sub2), folder.extras)

    def test_a_folder_without_an_archive_has_none(self):
        with self.assertRaises(ContainerError):
            container.identity_inputs(container.BrushFolder([("Shape.png", b"x")]))


# ── what an export did ───────────────────────────────────────────────────────

class EditOneKey(unittest.TestCase):
    """Edit one primary key of a brush that has every kind of member: only
    Brush.archive changes, and every other member stays byte for byte."""

    def test_in_a_set(self):
        brushes = [full_brush(71), full_brush(72, "legacy")]
        data = fixtures.brushset_file("Edit Me", brushes, plist_extra={"iconName": "icon"})
        brush_set = container.read_brushset(data)
        uuid, folder = brush_set.brushes[1]
        base = brush_model.decode(folder.archive)
        patched, report = brush_model.apply_patch(base, {"plotSpacing": 0.75})
        self.assertTrue(report["ok"])
        out = folder.copy()
        out.set("Brush.archive", brush_model.encode(patched))
        plan = container.member_plan(folder, out, reencoded={"Brush.archive"})
        self.assertEqual({entry["path"]: entry["state"] for entry in plan},
                         {path: ("re-encoded" if path == "Brush.archive" else "verbatim")
                          for path in folder.paths()})
        new = container.new_uuid()
        brush_set.brushes[1] = (new, out)
        written = dict(read_back(container.write_brushset(brush_set)))
        for path, original in brushes[1].members:
            if path == "Brush.archive":
                self.assertNotEqual(written[f"{new}/{path}"], original)
            else:
                self.assertEqual(written[f"{new}/{path}"], original, path)
        for path, original in brushes[0].members:
            self.assertEqual(written[f"{brushes[0].uuid}/{path}"], original, path)
        edited = brush_model.decode(written[f"{new}/Brush.archive"])
        self.assertEqual(edited.params["plotSpacing"], 0.75)
        before = {k: v for k, v in base.params.items() if k != "plotSpacing"}
        self.assertEqual({k: v for k, v in edited.params.items() if k != "plotSpacing"}, before)
        plist = plistlib.loads(written["brushset.plist"])
        self.assertEqual(plist, {"brushes": [brushes[0].uuid, new], "name": "Edit Me", "iconName": "icon"})

    def test_the_plan_states(self):
        folder = container.BrushFolder([("Brush.archive", b"a"), ("Shape.png", b"s"), ("Grain.png", b"g")])
        out = folder.copy()
        out.set("Shape.png", b"new shape")
        out.set("QuickLook/Thumbnail.png", b"thumb")
        out.remove("Grain.png")
        with self.assertRaises(ContainerError) as caught:
            container.member_plan(folder, out)
        self.assertEqual(caught.exception.code, "unrequested_drop")
        plan = container.member_plan(folder, out, drop={"Grain.png"})
        self.assertEqual([(entry["path"], entry["state"]) for entry in plan],
                         [("Brush.archive", "verbatim"), ("Shape.png", "replaced"),
                          ("QuickLook/Thumbnail.png", "replaced"), ("Grain.png", "dropped")])
        self.assertEqual(set(container.STATES), {"verbatim", "re-encoded", "replaced", "dropped"})

    def test_set_keeps_place_and_form(self):
        data = fixtures.brush_file(full_brush(73), stored=("Shape.png",))
        folder = container.read_brush(data)
        before = folder.paths()
        copy = folder.copy()
        copy.set("Shape.png", b"other")
        self.assertEqual(copy.paths(), before)
        self.assertEqual(copy.member("Shape.png").form, "stored")
        self.assertIsNone(copy.member("Shape.png").date_time)
        self.assertNotEqual(folder.get("Shape.png"), b"other", "a copy is a copy")


# ── the module and its users ─────────────────────────────────────────────────

class TheModule(unittest.TestCase):
    def setUp(self):
        self.source = (PIPELINE / "container.py").read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)

    def test_a_library_module_with_no_command_line(self):
        names = {node.name for node in self.tree.body if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("main", names)
        self.assertNotIn("__main__", self.source)

    def test_it_opens_no_file_but_by_the_bundled_folder_and_read_path(self):
        opened = [node for node in ast.walk(self.tree) if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Name) and node.func.id == "open"]
        self.assertEqual(len(opened), 2)
        for node in opened:
            self.assertEqual(node.args[1].value, "rb")

    def test_the_file_is_utf8_with_line_feeds(self):
        raw = (PIPELINE / "container.py").read_bytes()
        self.assertNotIn(b"\r", raw)
        raw.decode("utf-8")

    def test_ingest_takes_its_rules_from_here(self):
        import ingest
        self.assertIs(ingest.CAPS, container.CAPS)
        self.assertIs(ingest.JUNK_NAMES, container.JUNK_NAMES)
        self.assertIs(ingest.JUNK_FOLDERS, container.JUNK_FOLDERS)
        self.assertEqual(ingest.EMPTY, container.EMPTY)
        self.assertIs(ingest.sniff, container.sniff)
        self.assertIs(ingest.hostile, container.hostile)
        source = (PIPELINE / "ingest.py").read_text(encoding="utf-8")
        for copy in ('"zip_entries": 5000', 'frozenset({"__macosx"})', 'EMPTY = ".empty"'):
            self.assertNotIn(copy, source)
        with mock.patch.dict(container.CAPS, {"zip_entries": 1}):
            data = fixtures.brush_file(fixtures.make_brush("Two", number=81))
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                with self.assertRaises(ingest.Skip) as caught:
                    ingest.list_entries(archive)
            self.assertIn("the cap is 1", str(caught.exception))

    def test_device_tests_spells_the_same_rules(self):
        import device_tests
        self.assertEqual(device_tests.JUNK_NAMES, container.JUNK_NAMES)
        self.assertEqual(device_tests.JUNK_FOLDERS, container.JUNK_FOLDERS)
        self.assertEqual(device_tests.EMPTY, container.EMPTY)


# ── the real library, opt in ─────────────────────────────────────────────────

@unittest.skipUnless(CORPUS, "set ROSW_BRUSHES_CORPUS to a folder of brush files to run this")
class Corpus(unittest.TestCase):
    """Every container of a real folder (brushes/library for the whole library):
    read in memory, rebuilt from its members with the source's dates and forms,
    and read back. Run it as `python -I`."""

    def test_every_container_rebuilds_its_members(self):
        root = Path(CORPUS)
        files = sorted(p for p in root.rglob("*") if p.suffix.lower() in (".brush", ".brushset")
                       and not any(part.lower() in ("_docs", "__macosx") for part in p.relative_to(root).parts))
        self.assertTrue(files, "the corpus holds no brush file")
        identical = members = 0
        for path in files:
            data = container.read_path(path)
            found = container.read_any(data, path.name)
            self.assertEqual(len(found), 1, path)
            item = found[0]
            prefix = getattr(item, "prefix", "")
            if isinstance(item, container.BrushSet):
                rebuilt = container.write_brushset(item, preserve_order=True, source_dates=True)
                folders = [folder for _, folder in item.brushes]
            else:
                rebuilt = container.write_brush(item, preserve_order=True, source_dates=True)
                folders = [item]
            with zipfile.ZipFile(io.BytesIO(data)) as source:
                seen, wanted = set(), []
                for info in source.infolist():
                    name = info.orig_filename
                    if (name in seen or name.endswith("/") or container.is_junk(name)
                            or not name.startswith(prefix)):
                        continue
                    seen.add(name)
                    wanted.append((name[len(prefix):], source.read(info)))
            self.assertEqual(read_back(rebuilt), wanted, path)
            members += len(wanted)
            identical += rebuilt == data
            for folder in folders:
                digest = identity.content_sha256(*container.identity_inputs(folder))
                self.assertRegex(digest, "^[0-9a-f]{64}$")
        print(f"\n{len(files)} files, {members} members, {identical} rebuilt byte for byte",
              file=sys.stderr)


if __name__ == "__main__":
    unittest.main()
