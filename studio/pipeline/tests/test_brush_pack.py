"""brush_pack.py: a bundle becomes a .brush whose archive reads back whole.

The last test compares the archive with a brush Procreate itself wrote, when
the author has put one at tests/fixtures/procreate/*.brush. Without it, the
format is checked only for internal consistency, and that test is skipped.
"""

import base64
import contextlib
import io
import json
import plistlib
import shutil
import struct
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

from helpers import PIPELINE  # noqa: F401  (puts the pipeline on sys.path)

import brush_pack

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "procreate"


def png(size, value=128):
    """A greyscale PNG of one value, size x size, from the standard library."""
    raw = b"".join(b"\x00" + bytes([value]) * size for _ in range(size))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def parameters(**overrides):
    values = {key: 0.5 for key in brush_pack.FLOATS}
    values.update({"brushShapeCount": 1, "brushBlendingMode": 0})
    values.update({key: False for key in brush_pack.BOOLS})
    values["brushTaperLinked"] = True
    values.update(overrides)
    return values


def brush_json(name="Dry Stipple", identifier="0F2C6A3E-1B7D-4C1E-9A2B-3D4E5F607182", **overrides):
    return {
        "$schema": brush_pack.BUNDLE_SCHEMA,
        "name": name, "authorName": "the author", "notes": "test", "identifier": identifier, "version": 1,
        "parameters": parameters(**overrides),
        "shapeSource": "Soft Circle", "grainSource": "Paper Fine",
        "curves": {"brushPressureSizeResponse": base64.b64encode(bytes(range(64))).decode(),
                   "brushPressureOpacityResponse": None},
    }


class PackCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="brush-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def bundle(self, name="bundle.zip", brush=None, thumbnail=True, **files):
        path = self.root / name
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("brush.json", json.dumps(brush if brush is not None else brush_json()))
            zf.writestr("Shape.png", files.get("Shape.png", png(4)))
            zf.writestr("Grain.png", files.get("Grain.png", png(8, 200)))
            if thumbnail:
                zf.writestr("Thumbnail.png", png(2, 255))
        return path

    def call(self, *arguments):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = brush_pack.main([str(a) for a in arguments])
        return code, out.getvalue(), err.getvalue()


class Pack(PackCase):
    def test_the_archive_reads_back_with_every_tunable_typed(self):
        out, brush = brush_pack.pack(self.bundle(), self.root)
        self.assertEqual(out.name, "Dry_Stipple.brush")
        with zipfile.ZipFile(out) as zf:
            self.assertEqual(sorted(zf.namelist()),
                             ["Brush.archive", "Grain.png", "QuickLook/Thumbnail.png", "Shape.png"])
            self.assertEqual(zf.getinfo("Brush.archive").compress_type, zipfile.ZIP_DEFLATED)
            self.assertEqual(zf.getinfo("Shape.png").compress_type, zipfile.ZIP_STORED)
            back = brush_pack.unarchive(zf.read("Brush.archive"))
        for key in brush_pack.FLOATS:
            self.assertIsInstance(back[key], float, key)
        for key in brush_pack.INTS:
            self.assertIsInstance(back[key], int, key)
            self.assertNotIsInstance(back[key], bool, key)
        for key in brush_pack.BOOLS:
            self.assertIsInstance(back[key], bool, key)
        self.assertEqual(back["brushTaperLinked"], True)
        self.assertEqual(back["brushName"], "Dry Stipple")
        self.assertEqual(back["brushIdentifier"], "0F2C6A3E-1B7D-4C1E-9A2B-3D4E5F607182")
        self.assertEqual(back["brushPressureSizeResponse"], bytes(range(64)))
        self.assertNotIn("brushPressureOpacityResponse", back)
        self.assertEqual(back["$class"], {"$classname": "MCBrush", "$classes": ["MCBrush", "NSObject"]})
        self.assertEqual(len(back), len(brush_pack.TUNABLES) + 5 + 1 + 1)

    def test_the_plist_is_a_binary_keyed_archive_with_real_uids(self):
        _, brush = brush_pack.pack(self.bundle(), self.root)
        data = brush_pack.archive_bytes(brush)
        self.assertTrue(data.startswith(b"bplist00"))
        plist = plistlib.loads(data)
        self.assertEqual(plist["$archiver"], "NSKeyedArchiver")
        self.assertEqual(plist["$top"]["root"], plistlib.UID(1))
        self.assertEqual(plist["$objects"][0], "$null")
        entry = plist["$objects"][1]
        self.assertIsInstance(entry["$class"], plistlib.UID)
        self.assertIsInstance(entry["brushName"], plistlib.UID)
        self.assertEqual(plist["$objects"][entry["brushName"].data], "Dry Stipple")
        self.assertIsInstance(entry["brushSpacing"], float)

    def test_flat_keys_are_accepted_too(self):
        flat = {"name": "Flat", **parameters(brushSpacing=0.03)}
        _, brush = brush_pack.pack(self.bundle(brush=flat), self.root)
        self.assertEqual(brush["brushSpacing"], 0.03)
        self.assertRegex(brush["brushIdentifier"], brush_pack.UUID_RE)

    def test_a_missing_thumbnail_is_the_shape(self):
        out, _ = brush_pack.pack(self.bundle(thumbnail=False), self.root)
        with zipfile.ZipFile(out) as zf:
            self.assertEqual(zf.read("QuickLook/Thumbnail.png"), zf.read("Shape.png"))

    def test_a_folder_is_a_bundle_too(self):
        folder = self.root / "folder"
        folder.mkdir()
        (folder / "brush.json").write_text(json.dumps(brush_json(name="From folder")), encoding="utf-8")
        (folder / "Shape.png").write_bytes(png(4))
        (folder / "Grain.png").write_bytes(png(4))
        code, out, _ = self.call("pack", folder, "--out", self.root)
        self.assertEqual(code, 0)
        self.assertIn("From_folder.brush", out)

    def test_refusals(self):
        cases = {
            "no shape": lambda: self.bundle_without("Shape.png"),
            "not png": lambda: self.bundle(**{"Shape.png": b"not a png"}),
            "missing tunable": lambda: self.bundle(brush={"name": "x", "parameters": {"brushSpacing": 1}}),
            "wrong type": lambda: self.bundle(brush=brush_json(brushSpacing="fast")),
            "bool as number": lambda: self.bundle(brush=brush_json(brushFlipX=1)),
            "blend out of range": lambda: self.bundle(brush=brush_json(brushBlendingMode=16)),
            "no name": lambda: self.bundle(brush=brush_json(name="  ")),
            "bad curve": lambda: self.bundle(brush={**brush_json(), "curves": {"brushPressureSizeResponse": "***"}}),
        }
        for label, make in cases.items():
            with self.subTest(case=label):
                code, _, err = self.call("pack", make(), "--out", self.root)
                self.assertEqual(code, 1, err)
                self.assertTrue(err.startswith("refused"), err)
        code, _, err = self.call("pack", self.root / "nowhere.zip", "--out", self.root)
        self.assertEqual(code, 2)

    def bundle_without(self, name):
        path = self.root / "short.zip"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("brush.json", json.dumps(brush_json()))
            zf.writestr("Grain.png" if name == "Shape.png" else "Shape.png", png(4))
        return path


class Sets(PackCase):
    def test_a_set_holds_one_folder_per_brush_and_a_manifest(self):
        a = self.bundle("a.zip", brush_json(name="A", identifier="11111111-1111-4111-8111-111111111111"))
        b = self.bundle("b.zip", brush_json(name="B", identifier="22222222-2222-4222-8222-222222222222"))
        code, out, err = self.call("set", a, b, "--name", "Kit v1", "--out", self.root)
        self.assertEqual(code, 0, err)
        path = self.root / "Kit_v1.brushset"
        with zipfile.ZipFile(path) as zf:
            names = sorted(zf.namelist())
            self.assertIn("11111111-1111-4111-8111-111111111111/Brush.archive", names)
            self.assertIn("22222222-2222-4222-8222-222222222222/QuickLook/Thumbnail.png", names)
            manifest = plistlib.loads(zf.read("brushset.plist"))
        self.assertEqual(manifest, {"name": "Kit v1", "brushes": [
            "11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222"]})
        found = brush_pack.inspect(path)
        self.assertEqual(found["kind"], "brushset")
        self.assertEqual(len(found["brushes"]), 2)

    def test_two_brushes_with_one_identifier_are_refused(self):
        a = self.bundle("a.zip", brush_json(name="A"))
        b = self.bundle("b.zip", brush_json(name="B"))
        code, _, err = self.call("set", a, b, "--name", "Kit", "--out", self.root)
        self.assertEqual(code, 1)
        self.assertIn("share an identifier", err)


class Inspect(PackCase):
    def test_inspect_and_compare(self):
        out, _ = brush_pack.pack(self.bundle(), self.root)
        code, text, _ = self.call("inspect", out)
        self.assertEqual(code, 0)
        found = json.loads(text)
        self.assertEqual(found["kind"], "brush")
        self.assertEqual(found["brushes"]["Brush.archive"]["brushName"], "Dry Stipple")
        self.assertEqual(found["brushes"]["Brush.archive"]["brushPressureSizeResponse"], "<64 bytes>")
        code, text, _ = self.call("inspect", self.bundle("b2.zip"))
        self.assertEqual(json.loads(text)["kind"], "bundle")
        other, _ = brush_pack.pack(self.bundle("other.zip", brush_json(name="Other")), self.root)
        code, text, _ = self.call("compare", out, other)
        self.assertEqual((code, text.strip()), (0, "same keys, same types"))

    @unittest.skipUnless(FIXTURES.is_dir() and any(FIXTURES.glob("*.brush")),
                         "no Procreate-written .brush under tests/fixtures/procreate/")
    def test_the_archive_has_the_keys_and_types_procreate_writes(self):
        """The evidence that the format is right: a brush Procreate wrote has
        the same keys, of the same types, as one this packer writes."""
        theirs = next(FIXTURES.glob("*.brush"))
        ours, _ = brush_pack.pack(self.bundle(), self.root)
        self.assertEqual(brush_pack.compare(ours, theirs), [])


if __name__ == "__main__":
    unittest.main()
