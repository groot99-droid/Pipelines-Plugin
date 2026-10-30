"""pipeline/tests/fixtures.py: the synthetic brush files every other test uses.

A fixture that is wrong makes every test built on it wrong, so the builder is
checked here against the documented shape of the real files: the keyed-archive
envelope, the object order, each era's key count, the member layout of a brush
folder, the plist text.

    python -m unittest discover -s brushes/pipeline/tests
"""

import ast
import io
import json
import os
import plistlib
import re
import shutil
import struct
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import fixtures as fx  # noqa: E402
import identity  # noqa: E402


def as_f32(value):
    return struct.unpack(">f", struct.pack(">f", value))[0]


class Independence(unittest.TestCase):
    def test_the_builder_imports_the_standard_library_only(self):
        tree = ast.parse((Path(fx.__file__)).read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertEqual(imported - set(sys.stdlib_module_names), set())

    def test_it_points_at_the_real_folders_only_to_refuse_them(self):
        self.assertEqual(fx.BRUSHES.name, "brushes")
        self.assertEqual(fx.PIPELINE, PIPELINE)
        for target in (fx.BRUSHES, fx.BRUSHES / "library", fx.BRUSHES / "vault" / "x", fx.BRUSHES / "catalog"):
            with self.assertRaises(ValueError, msg=str(target)):
                fx.refuse_real(target)
        with self.assertRaises(ValueError):
            fx.write_library(fx.BRUSHES / "library")
        self.assertFalse((fx.BRUSHES / "library" / "user").exists() and
                         (fx.BRUSHES / "library" / "user" / fx.USER_PACK).exists())


class TemporaryFolders(fx.BrushCase):
    def test_the_case_has_a_folder_outside_the_repository(self):
        self.assertTrue(self.tmp.is_dir())
        self.assertNotIn(fx.REPO.resolve(), self.tmp.parents)
        self.assertEqual(fx.refuse_real(self.tmp), self.tmp)

    def test_the_brushes_variables_are_hidden(self):
        self.assertEqual([k for k in os.environ if k.upper().startswith(fx.ENV_PREFIX)], [])

    def test_a_tree_digest_sees_every_change(self):
        (self.tmp / "a").mkdir()
        (self.tmp / "a" / "one.txt").write_bytes(b"1")
        first = fx.tree_digest(self.tmp)
        self.assertEqual(fx.tree_digest(self.tmp), first)
        (self.tmp / "a" / "one.txt").write_bytes(b"2")
        second = fx.tree_digest(self.tmp)
        (self.tmp / "a" / "one.txt").rename(self.tmp / "a" / "two.txt")
        third = fx.tree_digest(self.tmp)
        self.assertEqual(len({first, second, third}), 3)


class HiddenVariables(unittest.TestCase):
    def test_a_variable_set_outside_comes_back_afterwards(self):
        name = fx.ENV_PREFIX + "ROOT"
        os.environ[name] = "outside"
        self.addCleanup(os.environ.pop, name, None)
        seen = []

        class Inner(fx.BrushCase):
            def runTest(self):
                seen.append(os.environ.get(name))

        result = unittest.TestResult()
        Inner().run(result)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(seen, [None])
        self.assertEqual(os.environ.get(name), "outside")


class Images(unittest.TestCase):
    def test_a_grey_image(self):
        data = fx.make_png(8, 6, "L")
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        image = fx.read_png(data)
        self.assertEqual((image["width"], image["height"], image["mode"]), (8, 6, "L"))
        self.assertEqual(image["chunks"], ["IHDR", "IDAT", "IEND"])
        self.assertEqual(len(image["pixels"]), 48)
        self.assertGreater(max(image["pixels"]), 0)
        self.assertEqual(struct.unpack(">IIBBBBB", data[16:29]), (8, 6, 8, 0, 0, 0, 0))

    def test_every_mode(self):
        for mode, (colour, samples) in fx.PNG_MODES.items():
            data = fx.make_png(5, 3, mode)
            image = fx.read_png(data)
            self.assertEqual(image["mode"], mode)
            self.assertEqual(len(image["pixels"]), 5 * 3 * samples)
            self.assertEqual(data[25], colour)
        self.assertEqual(fx.PNG_MODES["L"], (0, 1))
        self.assertEqual(fx.PNG_MODES["RGBA"], (6, 4))

    def test_the_pixels_are_the_painters(self):
        data = fx.make_png(2, 2, "L", lambda x, y: x + 2 * y)
        self.assertEqual(fx.read_png(data)["pixels"], bytes([0, 1, 2, 3]))
        rgba = fx.make_png(1, 2, "RGBA", lambda x, y: (10, 20, 30, 40 + y))
        self.assertEqual(fx.read_png(rgba)["pixels"], bytes([10, 20, 30, 40, 10, 20, 30, 41]))

    def test_the_bytes_do_not_depend_on_the_zlib_build(self):
        data = fx.make_png(2, 2, "L", lambda x, y: x + 2 * y)
        idat = data[data.index(b"IDAT") + 4:data.index(b"IEND") - 8]
        rows = b"\x00\x00\x01\x00\x02\x03"
        expected = b"\x78\x01" + b"\x01\x06\x00\xf9\xff" + rows + struct.pack(">I", zlib.adler32(rows))
        self.assertEqual(idat, expected)
        self.assertEqual(zlib.decompress(idat), rows)
        self.assertEqual(fx.make_png(2, 2, "L", lambda x, y: x + 2 * y), data)

    def test_a_large_image_can_be_compressed(self):
        big = fx.make_png(300, 300, "L", fx.speckle(3), compress=True)
        image = fx.read_png(big)
        self.assertEqual((image["width"], image["height"]), (300, 300))
        self.assertEqual(image["pixels"], fx.read_png(fx.make_png(300, 300, "L", fx.speckle(3)))["pixels"])

    def test_a_stored_stream_longer_than_one_block(self):
        raw = bytes(range(256)) * 600
        self.assertEqual(zlib.decompress(fx._zlib_stored(raw)), raw)
        self.assertEqual(zlib.decompress(fx._zlib_stored(b"")), b"")

    def test_extra_chunks_sit_between_header_and_data(self):
        data = fx.make_png(2, 2, "RGBA", extra_chunks=[(b"sRGB", b"\x00")])
        self.assertEqual(fx.read_png(data)["chunks"], ["IHDR", "sRGB", "IDAT", "IEND"])

    def test_a_thumbnail_is_white_where_it_is_not_clear(self):
        pixels = fx.read_png(fx.make_png(53, 16, "RGBA", fx.stroke_band(53, 16, 1)))["pixels"]
        alphas = set()
        for i in range(0, len(pixels), 4):
            r, g, b, a = pixels[i:i + 4]
            self.assertEqual((r, g, b), (255, 255, 255) if a else (0, 0, 0))
            alphas.add(a)
        self.assertIn(0, alphas)
        self.assertGreater(max(alphas), 100)

    def test_seeds_make_different_textures(self):
        self.assertNotEqual(fx.make_png(8, 8, "L", fx.speckle(1)), fx.make_png(8, 8, "L", fx.speckle(2)))
        self.assertNotEqual(fx.make_png(8, 8, "L", fx.soft_dot(8, 8, 1)), fx.make_png(8, 8, "L", fx.soft_dot(8, 8, 2)))

    def test_the_reader_refuses_what_it_does_not_understand(self):
        with self.assertRaises(ValueError):
            fx.read_png(b"not a png")
        good = bytearray(fx.make_png(2, 2))
        good[-13] ^= 0xFF                                    # inside the IDAT body
        with self.assertRaises(ValueError):
            fx.read_png(bytes(good))
        with self.assertRaises(ValueError):
            fx.make_png(2, 2, "RGBA", lambda x, y: (1, 2, 3))


class KeySets(unittest.TestCase):
    def test_each_legacy_era_has_its_documented_key_count(self):
        self.assertEqual(fx.LEGACY_ERAS, ("E0", "E1", "E1b", "E1c", "E2", "E3", "E4"))
        self.assertEqual(fx.LEGACY_KEY_COUNTS, {"E0": 52, "E1": 61, "E1b": 62, "E1c": 63,
                                                "E2": 67, "E3": 88, "E4": 101})
        for era, count in fx.LEGACY_KEY_COUNTS.items():
            keys = fx.legacy_keys(era)
            self.assertEqual(len(keys), count, era)
            self.assertEqual(len(set(keys)), count, era)
            self.assertIn("$class", keys)

    def test_what_each_era_adds_and_drops(self):
        keys = {era: set(fx.legacy_keys(era)) for era in fx.LEGACY_ERAS}
        self.assertEqual(keys["E0"] - keys["E1"], {"dynamicsGlazeType"})
        self.assertEqual(len(keys["E1"] - keys["E0"]), 10)
        self.assertIn("version", keys["E1"])
        self.assertNotIn("version", keys["E0"])
        self.assertEqual(keys["E1b"] - keys["E1"], {"dynamicsTiltCompression"})
        self.assertEqual(keys["E1c"] - keys["E1b"], {"dynamicsMixSoftening"})
        self.assertEqual(keys["E2"] - keys["E1c"],
                         {"blendGammaCorrect", "shapeFilter", "shapeFilterMode", "textureFilterMode"})
        self.assertEqual(keys["E2"] - keys["E3"], {"dynamicsPressureSpeed"})
        self.assertEqual(len(keys["E3"] - keys["E2"]), 22)
        self.assertTrue(set(fx.LEGACY_CURVES) <= keys["E3"])
        self.assertEqual(keys["E3"] - keys["E4"], {"dynamicsColorVariation"})
        self.assertEqual(len(keys["E4"] - keys["E3"]), 14)
        common = set.intersection(*keys.values())
        self.assertEqual(len(common), 50, "the keys every legacy archive has")

    def test_the_modern_set_is_220_keys_and_is_the_schemas_m220(self):
        keys = fx.modern_keys()
        self.assertEqual(len(keys), fx.MODERN_KEY_COUNT)
        self.assertEqual(fx.MODERN_KEY_COUNT, 220)
        self.assertEqual(len(set(keys)), 220)
        # The flag is true because the set is the schema's M220 key set, read
        # off the library; the flag and that evidence must agree.
        schema = json.loads((Path(__file__).resolve().parents[2] / "schema" / "silica_keys.json")
                            .read_text(encoding="utf-8"))
        m220 = next(row for row in schema["eras"] if row["id"] == "M220")
        self.assertEqual(set(keys) | {fx.CLASS_KEY}, set(m220["key_order"]))
        self.assertTrue(fx.MODERN_KEYS_VERIFIED)
        self.assertEqual(len(fx.MODERN_UNVERIFIED_KEYS), 27)
        self.assertTrue(set(fx.MODERN_UNVERIFIED_KEYS) <= set(keys))
        for gone in ("dynamicsRenderType", "dynamicsGlazeFlow", "dynamicsGlazeType",
                     "dynamicsPressureSpeed", "dynamicsColorVariation"):
            self.assertNotIn(gone, keys)
        for new in ("renderingMaxTransfer", "renderingModulatedTransfer", "renderingRecursiveMixing",
                    "dynamicsGlazedFlow", "authorName", "creationDate", "shapeCount", "grainDepth",
                    "wetEdgesAmount", "burntEdgesAmount", "dualBlendMode", "bundledHeightPath"):
            self.assertIn(new, keys)
        self.assertEqual(len(set(keys) - set(fx.legacy_keys("E4"))), 121)

    def test_keys_for(self):
        self.assertEqual(fx.keys_for(), fx.legacy_keys("E4"))
        self.assertEqual(fx.keys_for("legacy", "E0"), fx.legacy_keys("E0"))
        self.assertEqual(fx.keys_for("modern"), fx.modern_keys())
        self.assertEqual(fx.keys_for("modern", "M220"), fx.modern_keys())
        for family, era in (("legacy", "M220"), ("modern", "E4"), ("other", None)):
            with self.assertRaises(ValueError):
                fx.keys_for(family, era)

    def test_every_key_has_a_kind_and_scalars_have_a_default(self):
        kinds = {"real", "int", "bool", "string", "data", "curve", "roll", "array", "date"}
        for key in set(fx.modern_keys()) | set(fx.legacy_keys("E0")) | set(fx.legacy_keys("E3")):
            if key == "$class":
                continue
            kind = fx.kind_of(key)
            self.assertIn(kind, kinds, key)
            default = fx.default_for(key)
            if kind == "real":
                self.assertIsInstance(default, float, key)
                self.assertEqual(default, as_f32(default), key)
            elif kind == "bool":
                self.assertIsInstance(default, bool, key)
            elif kind == "int":
                self.assertIs(type(default), int, key)
            else:
                self.assertIsNone(default, key)


class Archives(unittest.TestCase):
    def test_the_envelope(self):
        for family, order in (("legacy", ["$version", "$objects", "$archiver", "$top"]),
                              ("modern", ["$version", "$archiver", "$top", "$objects"])):
            data = fx.make_archive(family, "Envelope")
            self.assertTrue(data.startswith(b"bplist00"))
            top = plistlib.loads(data)
            self.assertEqual(list(top), order)
            self.assertEqual(top["$version"], 100000)
            self.assertEqual(top["$archiver"], "NSKeyedArchiver")
            self.assertEqual(top["$top"], {"root": plistlib.UID(1)})
            self.assertEqual(top["$objects"][0], "$null")
            self.assertIsInstance(top["$objects"][1], dict)

    def test_every_legacy_era(self):
        for era, count in fx.LEGACY_KEY_COUNTS.items():
            facts = fx.read_archive(fx.make_archive("legacy", f"Era {era}", era=era))
            self.assertEqual(facts["keys"], fx.legacy_keys(era), era)
            self.assertEqual(len(facts["keys"]), count)
            self.assertEqual(facts["name"], f"Era {era}")
            chain = ["SilicaBrush", "NSObject"] if era == "E0" else ["SilicaBrush", "ValkyrieBrush", "NSObject"]
            self.assertEqual(facts["class_chain"], chain, era)
            self.assertEqual(len(facts["objects"]), 5 if era in ("E0", "E1", "E1b", "E1c", "E2") else 19, era)

    def test_the_object_order_of_the_common_101_key_layout(self):
        facts = fx.read_archive(fx.make_archive("legacy", "Brush ", bundled_grain=fx.BLANK_GRAIN))
        objects = facts["objects"]
        uid = plistlib.UID
        self.assertEqual(len(objects), 20)
        self.assertEqual(objects[2], "Brush-Preset-Blank.png")
        self.assertEqual(objects[3], bytes(16))
        self.assertEqual(objects[4], {"points": uid(5), "resolution": 1024, "$class": uid(9)})
        self.assertEqual(list(objects[4]), ["points", "resolution", "$class"])
        self.assertEqual(objects[5], {"NS.objects": [uid(6), uid(7)], "$class": uid(8)})
        self.assertEqual(objects[6:8], ["{0.000000, 0.000000}", "{1.000000, 1.000000}"])
        self.assertEqual(objects[8]["$classes"], ["NSMutableArray", "NSArray", "NSObject"])
        self.assertEqual(objects[9]["$classes"], ["ValkyrieMagnitudinalCurve", "NSObject"])
        self.assertEqual(objects[10], {"points": uid(11), "resolution": 1024, "$class": uid(9)})
        self.assertEqual(objects[14], {"points": uid(15), "resolution": 1024, "$class": uid(9)})
        self.assertEqual(objects[18], "Brush ")
        self.assertEqual(objects[19], {"$classname": "SilicaBrush",
                                       "$classes": ["SilicaBrush", "ValkyrieBrush", "NSObject"]})
        root = facts["root"]
        self.assertEqual(root["bundledShapePath"], uid(0))
        self.assertEqual(root["bundledGrainPath"], uid(2))
        self.assertEqual(root["color"], uid(3))
        self.assertEqual(root["dynamicsPressureOpacityCurve"], uid(4))
        self.assertEqual(root["dynamicsPressureBleedCurve"], uid(10))
        self.assertEqual(root["dynamicsPressureSizeCurve"], uid(14))
        self.assertEqual(root["name"], uid(18))
        self.assertEqual(root["$class"], uid(19))

    def test_scalars_have_the_right_python_types(self):
        values = fx.read_archive(fx.make_archive())["values"]
        self.assertIs(type(values["plotSpacing"]), float)
        self.assertEqual(values["plotSpacing"], as_f32(0.1))
        self.assertIs(values["stamp"], False)
        self.assertIs(values["textureFilter"], True)
        self.assertIs(type(values["version"]), int)
        self.assertEqual(values["version"], 2)
        self.assertIs(type(values["shapeOrientation"]), int)
        self.assertIsNone(values["bundledShapePath"])
        self.assertEqual(values["color"], bytes(16))

    def test_overrides_and_their_guard(self):
        data = fx.make_archive("legacy", "O", {"plotSpacing": 0.75, "stamp": True, "blendMode": 8})
        values = fx.read_archive(data)["values"]
        self.assertEqual((values["plotSpacing"], values["stamp"], values["blendMode"]), (0.75, True, 8))
        with self.assertRaises(KeyError):
            fx.make_archive("legacy", "O", {"plotSpacng": 1.0})
        with self.assertRaises(KeyError):
            fx.make_archive("legacy", "O", {"version": 2}, era="E0")
        with self.assertRaises(KeyError):
            fx.make_archive("legacy", "O", era="E2", curves={"dynamicsPressureSizeCurve": fx.IDENTITY_CURVE})

    def test_a_real_is_stored_at_32_bit_precision(self):
        value = fx.read_archive(fx.make_archive("legacy", "R", {"plotSpacing": 0.042}))["values"]["plotSpacing"]
        self.assertNotEqual(value, 0.042)
        self.assertEqual(value, as_f32(0.042))

    def test_names_survive_exactly(self):
        for name in ("Brush ", " Glow ", "Demo  Pencil", "Broken Cont\u00e9", "\u6d53\u58a8", "\U0001f4a7 Wet", ""):
            self.assertEqual(fx.read_archive(fx.make_archive("legacy", name))["name"], name)
            self.assertEqual(fx.read_archive(fx.make_archive("modern", name))["name"], name)

    def test_a_wrapped_name(self):
        facts = fx.read_archive(fx.make_archive("modern", "Wrapped", wrap_name=True))
        holder = facts["values"]["name"]
        self.assertEqual(list(holder), ["$class", "NS.string"])
        self.assertEqual(facts["name"], "Wrapped")
        self.assertEqual(facts["objects"][holder["$class"].data]["$classes"],
                         ["NSMutableString", "NSString", "NSObject"])

    def test_bundled_names(self):
        values = fx.read_archive(fx.make_archive(
            "legacy", "B", bundled_shape=fx.BUNDLED_SHAPE, bundled_grain=fx.BUNDLED_GRAIN))["values"]
        self.assertEqual(values["bundledShapePath"], "Brush-Preset-Hard.png")
        self.assertEqual(values["bundledGrainPath"], "Brush-Preset-Stained-Paper-1.jpg")

    def test_a_curve_with_an_extra_point_after_the_endpoints(self):
        data = fx.make_archive("legacy", "C", curves={
            "dynamicsPressureSizeCurve": [(0, 0), (1, 1), (0.289169, 0.552224)]})
        facts = fx.read_archive(data)
        curve = facts["values"]["dynamicsPressureSizeCurve"]
        points = [facts["objects"][ref.data] for ref in facts["objects"][curve["points"].data]["NS.objects"]]
        self.assertEqual(points, ["{0.000000, 0.000000}", "{1.000000, 1.000000}", "{0.289169, 0.552224}"])
        self.assertEqual(fx.point_string(0.289169, 0.552224), "{0.289169, 0.552224}")

    def test_unknown_and_missing_keys(self):
        data = fx.make_archive("legacy", "U", extra_keys={"somethingNew": 0.5, "anotherFlag": True},
                               drop_keys=("previewSize",))
        keys = fx.read_archive(data)["keys"]
        self.assertIn("somethingNew", keys)
        self.assertIn("anotherFlag", keys)
        self.assertNotIn("previewSize", keys)
        self.assertEqual(len(keys), 101 + 2 - 1)

    def test_the_modern_archive(self):
        facts = fx.read_archive(fx.make_archive("modern", "Modern", author="An Author"))
        objects, root, values = facts["objects"], facts["root"], facts["values"]
        self.assertEqual(facts["keys"], fx.modern_keys())
        self.assertEqual(len(objects), 60)
        self.assertEqual(len(fx.read_archive(fx.make_archive("modern", "Modern"))["objects"]), 59,
                         "one object fewer without an author name")
        self.assertEqual(facts["class_chain"], ["SilicaBrush", "ValkyrieBrush", "NSObject"])
        self.assertEqual(values["authorName"], "An Author")
        self.assertEqual(list(values["creationDate"]), ["NS.time", "$class"])
        self.assertEqual(values["creationDate"]["NS.time"], fx.CREATED)
        self.assertEqual(len({root[key].data for key in fx.MODERN_SAVED}), 1, "one shared empty array")
        self.assertEqual(values["savedPaintSizes"]["NS.objects"], [])
        self.assertEqual(objects[values["savedPaintSizes"]["$class"].data]["$classes"], ["NSArray", "NSObject"])
        self.assertEqual(root["bundledHeightPath"], plistlib.UID(0))
        curves = [key for key in facts["keys"] if fx.kind_of(key) == "curve"]
        rolls = [key for key in facts["keys"] if fx.kind_of(key) == "roll"]
        self.assertEqual((len(curves), len(rolls)), (9, 11))
        self.assertEqual(len({root[key].data for key in curves + rolls}), 20, "none is shared")
        for key in curves:
            self.assertEqual(list(values[key]), ["points", "$class"], key)
        for key in rolls:
            self.assertEqual(list(values[key]),
                             ["activationFalloff", "activationOrigin", "$class", "mode", "activationRange"], key)
            self.assertEqual(values[key]["mode"], 1)
            self.assertEqual(values[key]["activationOrigin"], as_f32(3.141592653589793))
        self.assertIs(values["renderingMaxTransfer"], False)
        self.assertEqual(values["dynamicsGlazedFlow"], 1.0)

    def test_no_author_is_nil(self):
        self.assertIsNone(fx.read_archive(fx.make_archive("modern", "Anon"))["values"]["authorName"])

    def test_the_same_request_gives_the_same_bytes(self):
        for family in ("legacy", "modern"):
            self.assertEqual(fx.make_archive(family, "Twice"), fx.make_archive(family, "Twice"))
        self.assertNotEqual(fx.make_archive("legacy", "A"), fx.make_archive("legacy", "B"))

    def test_an_archive_is_small(self):
        self.assertLess(len(fx.make_archive("modern", "Small")), 16 * 1024)


class BrushFolders(unittest.TestCase):
    def test_a_plain_brush(self):
        brush = fx.make_brush("Plain")
        self.assertEqual(brush.paths(), ["Brush.archive", "Shape.png", "Grain.png", "QuickLook/Thumbnail.png"])
        self.assertEqual((brush.family, brush.era), ("legacy", "E4"))
        self.assertEqual(brush.member("Brush.archive"), brush.archive)
        self.assertEqual(brush.member("Shape.png"), brush.shape)
        self.assertEqual(brush.member("Grain.png"), brush.grain)
        self.assertIsNone(brush.member("Nope.png"))
        self.assertEqual((brush.shape_source, brush.grain_source), ("embedded", "embedded"))
        self.assertEqual(brush.subs, [])
        self.assertEqual(fx.read_png(brush.shape)["mode"], "L")
        self.assertEqual(fx.read_png(brush.member("QuickLook/Thumbnail.png"))["mode"], "RGBA")
        self.assertIn("Plain", repr(brush))

    def test_bundled_blank_and_missing_textures(self):
        brush = fx.make_brush("B", shape="bundled", grain="blank")
        self.assertEqual(brush.paths(), ["Brush.archive", "QuickLook/Thumbnail.png"])
        self.assertIsNone(brush.shape)
        self.assertIsNone(brush.grain)
        self.assertEqual((brush.shape_source, brush.grain_source), ("bundled", "blank"))
        values = fx.read_archive(brush.archive)["values"]
        self.assertEqual(values["bundledShapePath"], fx.BUNDLED_SHAPE)
        self.assertEqual(values["bundledGrainPath"], fx.BLANK_GRAIN)
        none = fx.make_brush("N", grain="none")
        self.assertEqual(none.grain_source, "none")
        self.assertIsNone(fx.read_archive(none.archive)["values"]["bundledGrainPath"])
        bundled = fx.make_brush("G", grain="bundled")
        self.assertEqual((bundled.grain_source, bundled.bundled_grain), ("bundled", fx.BUNDLED_GRAIN))
        with self.assertRaises(ValueError):
            fx.make_brush("X", shape="blank")

    def test_textures_kept_under_their_own_name(self):
        brush = fx.make_brush("Earth", "modern", number=13, shape="named", grain="named")
        values = fx.read_archive(brush.archive)["values"]
        self.assertNotIn("Shape.png", brush.paths())
        self.assertIn(values["bundledShapePath"], brush.paths())
        self.assertIn(values["bundledGrainPath"], brush.paths())
        self.assertEqual(brush.member(values["bundledShapePath"]), brush.shape)
        self.assertEqual(brush.member(values["bundledGrainPath"]), brush.grain)
        self.assertEqual(brush.shape_source, "embedded")

    def test_supplied_bytes_are_used_as_they_are(self):
        brush = fx.make_brush("Own", shape=b"shape bytes", grain=b"grain bytes", thumbnail=b"thumb")
        self.assertEqual((brush.shape, brush.grain), (b"shape bytes", b"grain bytes"))
        self.assertEqual(brush.member("QuickLook/Thumbnail.png"), b"thumb")

    def test_thumbnail_choices(self):
        self.assertNotIn("QuickLook/Thumbnail.png", fx.make_brush("T", thumbnail=False).paths())
        grey = fx.make_brush("T", thumbnail="LA")
        self.assertEqual(fx.read_png(grey.member("QuickLook/Thumbnail.png"))["mode"], "LA")

    def test_the_full_tree(self):
        brush = fx.make_brush("Full", "modern", number=11, dual=True, reset=True, author=True)
        self.assertEqual(brush.paths(), [
            "Brush.archive", "Shape.png", "Grain.png", "QuickLook/Thumbnail.png",
            "AuthorPicture/AuthorPicture.png", "Signature/SignaturePicture.png",
            "Sub01/Brush.archive", "Sub01/Shape.png",
            "Reset/Brush.archive", "Reset/Shape.png", "Reset/Grain.png", "Reset/QuickLook/Thumbnail.png",
            "Reset/Sub01/Brush.archive", "Reset/Sub01/Shape.png"])
        self.assertEqual(len(brush.subs), 1)
        self.assertEqual(brush.subs[0], (brush.member("Sub01/Brush.archive"), brush.member("Sub01/Shape.png"), None))
        self.assertEqual(fx.read_archive(brush.member("Sub01/Brush.archive"))["name"], "Full Secondary")
        self.assertEqual(fx.read_archive(brush.archive)["values"]["authorName"], "Fixture Author")
        live = fx.read_archive(brush.archive)["values"]
        reset = fx.read_archive(brush.member("Reset/Brush.archive"))["values"]
        self.assertEqual({k for k in live if live[k] != reset[k]} - {"creationDate", "$class"} - set(
            k for k in live if isinstance(live[k], (dict, list))), {"paintSize"})
        self.assertNotEqual(brush.member("Reset/Brush.archive"), brush.archive)
        self.assertEqual(brush.member("Reset/Shape.png"), brush.shape)

    def test_empty_members_and_unknown_files(self):
        brush = fx.make_brush("E", empty=("", "Reset"), extras=[("Extra/unknown.bin", b"\x00\x01")])
        self.assertEqual(brush.paths()[-3:], [".empty", "Reset/.empty", "Extra/unknown.bin"])
        self.assertEqual(brush.member(".empty"), b"")
        self.assertEqual(brush.member("Reset/.empty"), b"")
        self.assertEqual(brush.member("Extra/unknown.bin"), b"\x00\x01")

    def test_folder_names_are_upper_case_version_4_uuids(self):
        names = [fx.brush_uuid(n) for n in range(1, 60)]
        self.assertEqual(len(set(names)), 59)
        for name in names:
            self.assertRegex(name, fx.UUID_PATTERN)
        self.assertEqual(fx.brush_uuid(1), fx.brush_uuid(1))
        self.assertEqual(fx.make_brush("U", number=5).uuid, fx.brush_uuid(5))

    def test_the_number_changes_the_pixels_not_the_archive(self):
        one, two = fx.make_brush("N", number=1), fx.make_brush("N", number=2)
        self.assertEqual(one.archive, two.archive)
        self.assertNotEqual(one.shape, two.shape)
        self.assertNotEqual(one.grain, two.grain)


PLIST_TEXT = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
    '<plist version="1.0">\n'
    '<dict>\n'
    '\t<key>brushes</key>\n'
    '\t<array>\n'
    '\t\t<string>{0}</string>\n'
    '\t\t<string>{1}</string>\n'
    '\t</array>\n'
    '\t<key>name</key>\n'
    '\t<string>{2}</string>\n'
    '</dict>\n'
    '</plist>\n')


class Containers(unittest.TestCase):
    def setUp(self):
        self.brushes = fx.standard_user_brushes()

    def test_a_loose_brush_has_its_members_at_the_root(self):
        data = fx.brush_file(self.brushes[0])
        self.assertEqual(fx.zip_entries(data), self.brushes[0].members)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for info in archive.infolist():
                self.assertEqual(info.compress_type, zipfile.ZIP_DEFLATED)
                self.assertEqual(info.external_attr, 0)
                self.assertEqual(info.create_system, 0)
                self.assertFalse(info.is_dir())

    def test_the_plist_is_the_documented_text(self):
        one, two = fx.brush_uuid(1), fx.brush_uuid(2)
        self.assertEqual(fx.brushset_plist("Demo Set ", [one, two]).decode("utf-8"),
                         PLIST_TEXT.format(one, two, "Demo Set "))
        self.assertEqual(fx.brushset_plist("A & <B>", [one, two]).decode("utf-8"),
                         PLIST_TEXT.format(one, two, "A &amp; &lt;B&gt;"))
        emoji = fx.brushset_plist("\U0001f4a7Everything", [one, two])
        self.assertIn("\U0001f4a7Everything".encode("utf-8"), emoji)

    def test_extra_plist_keys_follow_name(self):
        data = fx.brushset_plist("X", [fx.brush_uuid(1)], {"iconName": "icon"})
        self.assertEqual(list(plistlib.loads(data)), ["brushes", "name", "iconName"])
        self.assertLess(data.index(b"<key>name</key>"), data.index(b"<key>iconName</key>"))
        binary = fx.brushset_plist("X", [fx.brush_uuid(1)], binary=True)
        self.assertTrue(binary.startswith(b"bplist00"))
        self.assertEqual(plistlib.loads(binary)["name"], "X")

    def test_a_brushset(self):
        data = fx.brushset_file("Demo Set ", self.brushes)
        entries = fx.zip_entries(data)
        names = [name for name, _ in entries]
        self.assertEqual(names[-1], "brushset.plist")
        plist = plistlib.loads(entries[-1][1])
        self.assertEqual(plist, {"brushes": [b.uuid for b in self.brushes], "name": "Demo Set "})
        expected = [(f"{b.uuid}/{path}", blob) for b in self.brushes for path, blob in b.members]
        self.assertEqual(entries[:-1], expected)
        self.assertEqual(len(names), len(set(names)))

    def test_zip_order_need_not_be_plist_order(self):
        shuffled = [self.brushes[2], self.brushes[0], self.brushes[3], self.brushes[1]]
        data = fx.brushset_file("Demo", self.brushes, zip_order=shuffled, plist_first=True)
        entries = fx.zip_entries(data)
        self.assertEqual(entries[0][0], "brushset.plist")
        self.assertEqual(plistlib.loads(entries[0][1])["brushes"], [b.uuid for b in self.brushes])
        seen = list(dict.fromkeys(name.split("/")[0] for name, _ in entries[1:]))
        self.assertEqual(seen, [b.uuid for b in shuffled])

    def test_a_set_inside_one_top_folder(self):
        entries = fx.zip_entries(fx.brushset_file("Demo", self.brushes[:1], prefix="Demo Set/"))
        self.assertTrue(all(name.startswith("Demo Set/") for name, _ in entries))
        self.assertEqual(entries[-1][0], "Demo Set/brushset.plist")

    def test_empty_members_written_twice_and_stored_entries(self):
        earth = fx.standard_official_brushes()[2]
        stored = f"{earth.uuid}/Brush.archive"
        data = fx.brushset_file("Earth", [earth], plist_extra={"iconName": "i"}, double_empty=True,
                                stored=(stored,))
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
        names = [info.orig_filename for info in infos]
        self.assertEqual(names.count(f"{earth.uuid}/.empty"), 2)
        self.assertEqual(names.count(f"{earth.uuid}/Reset/.empty"), 2)
        kinds = {info.filename: info.compress_type for info in infos}
        self.assertEqual(kinds[stored], zipfile.ZIP_STORED)
        self.assertEqual(kinds["brushset.plist"], zipfile.ZIP_DEFLATED)
        everything = fx.make_zip([("a.txt", b"a" * 100)], stored=True)
        with zipfile.ZipFile(io.BytesIO(everything)) as archive:
            self.assertEqual(archive.infolist()[0].compress_type, zipfile.ZIP_STORED)

    def test_a_name_given_twice_is_kept_twice(self):
        entries = fx.zip_entries(fx.make_zip([("x/.empty", b""), ("x/.empty", b""), ("y", b"1")]))
        self.assertEqual([name for name, _ in entries], ["x/.empty", "x/.empty", "y"])


class Hostile(unittest.TestCase):
    def setUp(self):
        self.files = fx.hostile_files()

    def test_the_set_of_cases(self):
        self.assertEqual(sorted(self.files), [
            "bare-array-plist.brushset", "empty.brushset", "lfs-pointer.brushset",
            "missing-folder.brushset", "no-archive.brush", "not-a-zip.brush",
            "string-top-archive.brush", "traversal.brushset", "truncated-archive.brush",
            "wrong-magic.brush"])
        for name, data in self.files.items():
            self.assertLess(len(data), 64 * 1024, name)
            self.assertFalse(name.endswith(".zip"))

    def test_names_that_point_outside(self):
        names = [name for name, _ in fx.zip_entries(self.files["traversal.brushset"])]
        for bad in ("../outside.txt", "/absolute.txt", "C:\\drive.txt"):
            self.assertIn(bad, names)
        self.assertIn(b"C:\\drive.txt", self.files["traversal.brushset"],
                      "the backslash is in the file's bytes on every platform")
        self.assertTrue(any(name.endswith("/../../climb.txt") for name in names))
        self.assertIn("brushset.plist", names)

    def test_the_malformed_plists_and_archives(self):
        entries = dict(fx.zip_entries(self.files["bare-array-plist.brushset"]))
        self.assertIsInstance(plistlib.loads(entries["brushset.plist"]), list)
        missing = dict(fx.zip_entries(self.files["missing-folder.brushset"]))
        listed = plistlib.loads(missing["brushset.plist"])["brushes"]
        folders = {name.split("/")[0] for name in missing if "/" in name}
        self.assertEqual(len(set(listed) - folders), 1)
        string_top = dict(fx.zip_entries(self.files["string-top-archive.brush"]))["Brush.archive"]
        self.assertIsInstance(plistlib.loads(string_top), str)
        wrong = dict(fx.zip_entries(self.files["wrong-magic.brush"]))["Brush.archive"]
        self.assertFalse(wrong.startswith(b"bplist00"))
        truncated = dict(fx.zip_entries(self.files["truncated-archive.brush"]))["Brush.archive"]
        self.assertTrue(truncated.startswith(b"bplist00"))
        with self.assertRaises(Exception):
            plistlib.loads(truncated)
        self.assertNotIn("Brush.archive", dict(fx.zip_entries(self.files["no-archive.brush"])))
        self.assertEqual(fx.zip_entries(self.files["empty.brushset"]), [])

    def test_what_is_not_a_zip(self):
        self.assertFalse(zipfile.is_zipfile(io.BytesIO(self.files["not-a-zip.brush"])))
        pointer = self.files["lfs-pointer.brushset"]
        self.assertTrue(pointer.startswith(b"version https://git-lfs.github.com/spec/v1\n"))
        self.assertEqual(pointer, fx.LFS_POINTER)
        self.assertFalse(zipfile.is_zipfile(io.BytesIO(pointer)))

    def test_the_ratio_bomb_is_small_until_inflated(self):
        data = fx.ratio_bomb(megabytes=17)
        self.assertLess(len(data), 256 * 1024)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            info = archive.getinfo("Shape.png")
        self.assertEqual(info.file_size, 17 * 1024 * 1024)
        self.assertGreater(info.file_size / info.compress_size, 200)


class Library(fx.BrushCase):
    def test_what_is_written_and_where(self):
        library = fx.write_library(self.tmp)
        self.assertEqual(library["library"], self.tmp)
        written = sorted(p.relative_to(self.tmp).as_posix() for p in self.tmp.rglob("*") if p.is_file())
        self.assertEqual(written, sorted(list(library["files"]) + ["sources.json"]))
        self.assertEqual(written, [
            "official/demo-official/demo-modern.brushset", "sources.json",
            "user/demo-pack/Demo_Inker.brush", "user/demo-pack/Demo_Set.brushset",
            "user/demo-pack/Loose_Marker.brush"])
        for relative, data in library["files"].items():
            self.assertEqual((self.tmp / relative).read_bytes(), data)
            self.assertTrue(zipfile.is_zipfile(io.BytesIO(data)), relative)
            self.assertFalse(relative.endswith(".zip"))
            self.assertRegex(relative, r"^[A-Za-z0-9._/-]+$")
        self.assertLess(sum(len(data) for data in library["files"].values()), 256 * 1024)

    def test_the_manifest_is_in_the_real_schema(self):
        library = fx.write_library(self.tmp)
        raw = library["sources"].read_bytes()
        self.assertNotIn(b"\r", raw)
        sources = json.loads(raw.decode("utf-8"))
        self.assertEqual(sources["schema"], "rosw-brushes-sources/1")
        pack = sources["packs"][0]
        self.assertEqual(set(pack), {"id", "kind", "vendor", "product", "source_url", "licence_note",
                                     "redistribute", "publish_previews", "evidence", "match", "sets"})
        self.assertEqual(pack["sets"], {"Demo Set ": {"slug": "demo-set", "title": "Demo Set"}})
        official = sources["official"]["files"][0]
        self.assertEqual(set(official), {"pack", "slug", "title", "path", "bytes", "md5"})
        self.assertEqual(official["bytes"], len(library["files"][library["official_set"]["file"]]))
        self.assertRegex(official["md5"], r"^[0-9a-f]{32}$")
        self.assertEqual(sources["official"]["host"], "downloads.invalid")

    def test_the_user_set(self):
        library = fx.write_library(self.tmp)
        user = library["user_set"]
        self.assertEqual((user["name"], user["slug"]), ("Demo Set ", "demo-set"))
        self.assertEqual(identity.slugify(user["name"]), user["slug"])
        entries = dict(fx.zip_entries(library["files"][user["file"]]))
        plist = plistlib.loads(entries["brushset.plist"])
        self.assertEqual(plist["name"], "Demo Set ")
        self.assertEqual(plist["brushes"], [brush.uuid for brush in user["brushes"]])
        self.assertEqual([brush.era for brush in user["brushes"]], ["E4", "E3", "E0", "E4"])
        self.assertEqual([brush.name for brush in user["brushes"]],
                         ["Demo Inker", "Demo  Pencil", "Broken Cont\u00e9", "Demo Inker"])

    def test_the_loose_duplicate_is_the_first_set_member(self):
        library = fx.write_library(self.tmp)
        duplicate, marker = library["loose"]
        self.assertTrue(duplicate["duplicate"])
        self.assertFalse(marker["duplicate"])
        loose = dict(fx.zip_entries(library["files"][duplicate["file"]]))
        first = library["user_set"]["brushes"][0]
        self.assertEqual(loose, dict(first.members))

        def ident(brush):
            return identity.brush_id(brush.archive, brush.shape, brush.grain, brush.subs)

        ids = {ident(brush) for brush in library["user_set"]["brushes"]}
        self.assertIn(ident(duplicate["brush"]), ids)
        self.assertNotIn(ident(marker["brush"]), ids)
        self.assertEqual(marker["brush"].era, "E1b")

    def test_the_official_style_set(self):
        library = fx.write_library(self.tmp)
        official = library["official_set"]
        data = library["files"][official["file"]]
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            plist = plistlib.loads(archive.read("brushset.plist"))
        names = [info.filename for info in infos]
        self.assertEqual(list(plist), ["brushes", "name", "iconName"])
        self.assertEqual(plist["name"], official["name"])
        self.assertFalse(plist["name"].isascii())
        dual, plain, earth = official["brushes"]
        self.assertIn(f"{dual.uuid}/Sub01/Brush.archive", names)
        self.assertIn(f"{dual.uuid}/Reset/Sub01/Brush.archive", names)
        self.assertIn(f"{dual.uuid}/AuthorPicture/AuthorPicture.png", names)
        self.assertIn(f"{dual.uuid}/Signature/SignaturePicture.png", names)
        self.assertEqual([n for n in names if n.startswith(plain.uuid)], [f"{plain.uuid}/Brush.archive"])
        self.assertEqual(names.count(f"{earth.uuid}/.empty"), 2)
        self.assertIn(f"{earth.uuid}/Extra/unknown.bin", names)
        stored = [info.filename for info in infos if info.compress_type == zipfile.ZIP_STORED]
        self.assertEqual(stored, [f"{earth.uuid}/Brush.archive"])
        self.assertEqual(fx.read_archive(earth.archive)["values"]["version"], 4)
        self.assertEqual([brush.family for brush in official["brushes"]], ["modern"] * 3)

    def test_building_twice_gives_the_same_library(self):
        other = Path(tempfile.mkdtemp(prefix="brushes-test-"))
        self.addCleanup(shutil.rmtree, other, True)
        first, second = fx.write_library(self.tmp), fx.write_library(other)
        self.assertEqual(first["files"], second["files"])
        self.assertEqual(fx.tree_digest(self.tmp), fx.tree_digest(other))


class ModuleSource(unittest.TestCase):
    def test_the_fixture_file_names_no_machine_path(self):
        text = Path(fx.__file__).read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"[A-Za-z]:[\\/]Users|/home/|/Users/", text))


if __name__ == "__main__":
    unittest.main()
