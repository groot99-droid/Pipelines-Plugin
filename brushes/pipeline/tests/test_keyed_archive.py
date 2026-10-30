"""pipeline/keyed_archive.py: a Brush.archive as a graph, written back byte for byte.

Four kinds of evidence, kept apart:

  synthetic graphs   `build` below makes archives with the shape of the app's
                     own (envelope, numbering, class entries, curves, roll
                     objects, a shared empty array) from made-up keys and
                     values, straight into the logical graph. Nothing here is
                     copied from a brush file.
  plistlib           reads what the encoder wrote, and writes the fixtures'
                     archives, which this module must take as fidelity "table".
  frozen goldens     goldens_codec.json holds the sha256 of the encoder's
                     output for the synthetic graphs under each profile. They
                     were recorded only after the encoder had reproduced every
                     archive of the real library, so a change to the byte path
                     shows here, where there is no library.
  the real library   opt-in. Set ROSW_BRUSHES_CORPUS to a library folder and
                     run this file with an isolated interpreter:

        python -I -m unittest discover -s brushes/pipeline/tests -p test_keyed_archive.py

                     Every Brush.archive of every .brush and .brushset under
                     it is read in memory and must come back byte for byte.

    python -m unittest discover -s brushes/pipeline/tests
"""

import collections
import hashlib
import io
import json
import os
import plistlib
import re
import struct
import sys
import unittest
import zipfile
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))         # for `fixtures`, when one file is run by path

import bplist  # noqa: E402
import fixtures  # noqa: E402
import keyed_archive as ka  # noqa: E402
from bplist import BplistError, CodecError, LimitExceeded, PDict, Real, UID  # noqa: E402
from keyed_archive import Archive, ArchiveError  # noqa: E402

GOLDENS = Path(__file__).resolve().with_name("goldens_codec.json")
CORPUS = os.environ.get("ROSW_BRUSHES_CORPUS", "").strip()

LEGACY_TOP = ("$version", "$objects", "$archiver", "$top")
MODERN_TOP = ("$version", "$archiver", "$top", "$objects")

BRUSH = ("SilicaBrush", "ValkyrieBrush", "NSObject")
BRUSH_OLDEST = ("SilicaBrush", "NSObject")
CURVE = ("ValkyrieMagnitudinalCurve", "NSObject")
MUTABLE_ARRAY = ("NSMutableArray", "NSArray", "NSObject")
ARRAY = ("NSArray", "NSObject")
ROLL = ("ValkyrieBrushRollParameters", "NSObject")
DATE = ("NSDate", "NSObject")
MUTABLE_STRING = ("NSMutableString", "NSString", "NSObject")

IDENTITY = ("{0.000000, 0.000000}", "{1.000000, 1.000000}")
THREE_POINTS = ("{0.000000, 0.000000}", "{1.000000, 1.000000}", "{0.250000, 0.330000}")


# ── synthetic graphs ─────────────────────────────────────────────────────────

WORDS = ("Pressure", "Tilt", "Jitter", "Opacity", "Size", "Bleed", "Hue", "Taper", "Grain",
         "Shape", "Speed", "Flow")
REALS = (0.0, 0.0, 1.0, 0.5, 0.0, 0.25, 0.3, 1.0, 0.0, 0.5, 0.0, 0.123, 0.0, 1.0, 0.75, 0.0)
INTS = (0, 1, 2, 0, 1, 4, 0, 27)


def scalar_keys(count):
    """`count` made-up root keys with made-up values: (key, value) pairs.
    Reals are 4-byte; the mix repeats whole and fractional values on purpose."""
    pairs = []
    for n in range(count):
        first, second = WORDS[n % 12], WORDS[(n * 5 + n // 12) % 12]
        key = f"dynamics{first}{second}{n}" if n % 4 else f"plot{second}{n}"
        if n % 7 == 0:
            value = (n // 7) % 3 == 0
        elif n % 7 == 1:
            value = INTS[(n // 7) % len(INTS)]
        else:
            value = Real.f32(REALS[n % len(REALS)])
        pairs.append((key, value))
    return pairs


def shuffled(pairs):
    """A fixed order that is neither the order made nor alphabetical."""
    return sorted(pairs, key=lambda pair: hashlib.sha256(pair[0].encode("utf-8")).hexdigest())


class Graph:
    """`$objects`, numbered the way the app numbers it: an instance, then
    what it holds, then its class entry the first time the class is used."""

    def __init__(self):
        self.objects = ["$null"]
        self.classes = {}

    def add(self, value):
        self.objects.append(value)
        return UID(len(self.objects) - 1)

    def class_of(self, chain):
        if chain not in self.classes:
            self.classes[chain] = self.add(PDict([("$classname", chain[0]),
                                                  ("$classes", list(chain))]))
        return self.classes[chain]

    def string(self, text, wrapped=False):
        if text is None:
            return UID(0)
        if not wrapped:
            return self.add(text)
        holder = PDict()
        uid = self.add(holder)
        holder.extend([("$class", self.class_of(MUTABLE_STRING)), ("NS.string", text)])
        return uid

    def curve(self, points, legacy):
        curve, array = PDict(), PDict()
        uid = self.add(curve)
        array_uid = self.add(array)
        array.append(("NS.objects", [self.add(point) for point in points]))
        array.append(("$class", self.class_of(MUTABLE_ARRAY)))
        curve.append(("points", array_uid))
        if legacy:
            curve.append(("resolution", 1024))
        curve.append(("$class", self.class_of(CURVE)))
        return uid

    def roll(self):
        roll = PDict()
        uid = self.add(roll)
        roll.extend([("activationFalloff", Real.f32(1.5707963705062866)),
                     ("activationOrigin", Real.f32(3.1415927410125732)),
                     ("$class", self.class_of(ROLL)), ("mode", 1),
                     ("activationRange", Real.f32(3.1415927410125732))])
        return uid

    def date(self, seconds):
        date = PDict()
        uid = self.add(date)
        date.extend([("NS.time", Real.f64(seconds)), ("$class", self.class_of(DATE))])
        return uid

    def array(self, items=()):
        array = PDict()
        uid = self.add(array)
        array.append(("NS.objects", [self.add(item) for item in items]))
        array.append(("$class", self.class_of(ARRAY)))
        return uid


LEGACY_CURVES = ("dynamicsPressureOpacityCurve", "dynamicsPressureBleedCurve",
                 "dynamicsPressureSizeCurve")
MODERN_CURVES = tuple(f"dynamicsPressure{stem}Curve" for stem in (
    "Opacity", "Size", "ShapeRoundness", "Bleed", "TransferModulation", "Hue", "Saturation",
    "Brightness", "SecondaryColor"))
SAVED = tuple(f"saved{tool}{what}" for tool in ("Paint", "Erase", "Smudge")
              for what in ("Sizes", "Opacities"))
ROLLS_FIRST = ("shapeScatterRollParameters", "shapeCountRollParameters", "plotJitterRollParameters")
ROLLS_LAST = tuple(f"dynamicsRoll{stem}Parameters" for stem in (
    "Size", "Opacity", "Bleed", "Hue", "Saturation", "Brightness", "SecondaryColor")) + (
    "attackRollParameters",)


def build(kind):
    """A synthetic archive, never decoded from bytes: `source` is None.

    legacy-plain    44 scalar keys, no curves, the oldest class chain
    legacy-curves   93 scalar keys, three curves (one of three points), a name
                    that needs UTF-16, a bundled shape name
    modern          182 scalar keys, nine curves, eleven roll objects, six keys
                    on one empty array, a date, an author
    modern-extras   `modern` with a wrapped name, a saved-sizes array of its
                    own holding a bare real, one string entry under two keys,
                    and keys and a class no schema knows
    """
    graph = Graph()
    root = PDict()
    graph.add(root)
    refs = []
    if kind.startswith("legacy"):
        curves = kind == "legacy-curves"
        scalars = scalar_keys(93 if curves else 44)
        refs.append(("bundledShapePath", graph.string("Brush-Golden-Hard.png" if curves else None)))
        refs.append(("bundledGrainPath", graph.string(None)))
        refs.append(("color", graph.add(bytes(range(16)))))
        if curves:
            for key in LEGACY_CURVES:
                refs.append((key, graph.curve(THREE_POINTS if key.endswith("SizeCurve") else IDENTITY,
                                              legacy=True)))
        refs.append(("name", graph.string("Golden Cont\u00e9" if curves else "Golden Plain")))
        refs.append(("$class", graph.class_of(BRUSH if curves else BRUSH_OLDEST)))
        top_order = LEGACY_TOP
    else:
        extras = kind == "modern-extras"
        scalars = scalar_keys(182)
        shape = graph.string("GL-Golden-Grain.png")
        refs.append(("bundledShapePath", shape))
        refs.append(("bundledGrainPath", shape if extras else graph.string("GL-Golden-Grain.png")))
        refs.append(("bundledMetallicPath", graph.string(None)))
        refs.append(("bundledRoughnessPath", graph.string(None)))
        shared = graph.array()
        refs.extend((key, shared) for key in SAVED[1:])
        refs.append(("color", graph.add(bytes(16))))
        refs.extend((key, graph.roll()) for key in ROLLS_FIRST)
        for key in MODERN_CURVES:
            refs.append((key, graph.curve(THREE_POINTS if key.endswith("BleedCurve") else IDENTITY,
                                          legacy=False)))
        refs.extend((key, graph.roll()) for key in ROLLS_LAST)
        refs.append(("name", graph.string("\u6c34\u58a8 Golden" if extras else "Golden Modern",
                                          wrapped=extras)))
        refs.append(("authorName", graph.string("Golden")))
        refs.append(("creationDate", graph.date(694224000.25)))
        refs.append(("bundledHeightPath", UID(0)))
        if extras:
            refs.append(("savedPaintSizes", graph.array([Real.f32(0.2402)])))
            unknown = PDict()
            unknown_uid = graph.add(unknown)
            unknown.extend([("zeta", Real.f64(2.5)), ("$class", UID(0)), ("alpha", [UID(0), 7, True]),
                            ("nested", PDict([("deep", [Real.f32(-0.0), Real.f32(0.0)])]))])
            unknown.set("$class", graph.class_of(("RoswUnknownThing", "NSObject")))
            refs.append(("unknownObject", unknown_uid))
            scalars += [("unknownReal64", Real.f64(1.0)), ("unknownNegative", -5),
                        ("unknownWide", 2 ** 40), ("unknownNegativeZero", Real.f32(-0.0)),
                        ("unknownFour", Real.f32(4.0)), ("unknownFourAgain", Real.f32(4.0)),
                        ("unknownShort", 1024), ("unknownText", "inline text"),
                        ("unknownTag", "Wet Mix"), ("unknownTagAgain", "Wet Mix"),
                        ("unknownLong", "a value string too long to share"),
                        ("unknownLongAgain", "a value string too long to share")]
        else:
            refs.append(("savedPaintSizes", shared))
        refs.append(("$class", graph.class_of(BRUSH)))
        top_order = MODERN_TOP
    root.extend(shuffled(scalars + refs))
    return Archive(top_order, 100000, "NSKeyedArchiver", graph.objects)


KINDS = ("legacy-plain", "legacy-curves", "modern", "modern-extras")


def from_plistlib(data):
    """A plistlib-written archive as a logical graph, converted here and not by
    the decoder: every real becomes 4 bytes, as the app stores them, except
    the date's."""
    def logical(value, key=None):
        if isinstance(value, plistlib.UID):
            return UID(value.data)
        if isinstance(value, float):
            return Real.f64(value) if key == "NS.time" else Real.f32(value)
        if isinstance(value, dict):
            return PDict((k, logical(v, k)) for k, v in value.items())
        if isinstance(value, list):
            return [logical(v) for v in value]
        return value
    top = plistlib.loads(data)
    return Archive(tuple(top), top["$version"], top["$archiver"], logical(top["$objects"]),
                   top=logical(top["$top"]))


def comparable(value):
    """A plistlib value with nothing left to chance: a real by its bits."""
    if isinstance(value, plistlib.UID):
        return ("uid", value.data)
    if isinstance(value, float):
        return ("real", struct.pack(">d", value))
    if isinstance(value, dict):
        return {key: comparable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [comparable(item) for item in value]
    return value


def differing(before, after):
    """Compare two archives through plistlib: (entries of `$objects` that
    differ, root keys that differ). Asserts the envelope is the same."""
    one, two = plistlib.loads(before), plistlib.loads(after)
    assert list(one) == list(two), "the top order changed"
    assert all(comparable(one[key]) == comparable(two[key])
               for key in ("$version", "$archiver", "$top")), "the envelope changed"
    assert len(one["$objects"]) == len(two["$objects"]), "the number of entries changed"
    entries = [n for n, (x, y) in enumerate(zip(one["$objects"], two["$objects"]))
               if comparable(x) != comparable(y)]
    at = one["$top"]["root"].data
    old, new = one["$objects"][at], two["$objects"][at]
    assert list(old) == list(new), "the root key order changed"
    return entries, [key for key in old if comparable(old[key]) != comparable(new[key])]


def code_of(case, error, call, *args, **kwargs):
    with case.assertRaises(error) as caught:
        call(*args, **kwargs)
    return caught.exception.code


def record(archive, profile):
    data = ka.rule_encode(archive, profile)
    table = bplist.parse_table(data)
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "objects": len(table.objects), "ref_size": table.ref_size,
            "offset_size": table.offset_size}


# ── the two profiles ─────────────────────────────────────────────────────────

class Profiles(unittest.TestCase):
    def test_the_two_names_in_order(self):
        self.assertEqual(list(ka.PROFILES), ["ios_legacy", "ios_modern"])
        self.assertIn(ka.DEFAULT_PROFILE, ka.PROFILES)

    def test_the_legacy_rule_shares_four_class_names(self):
        for text in ("NSObject", "NSArray", "NSMutableArray", "NSDate"):
            self.assertTrue(ka.legacy_shared(text), text)
        for text in ("NSString", "NSMutableString", "SilicaBrush", "ValkyrieBrush", "", "$null",
                     "nsobject", "{0.000000, 0.000000}"):
            self.assertFalse(ka.legacy_shared(text), text)

    def test_the_modern_rule_is_what_fits_in_a_pointer(self):
        eligible = ("", "a", "$null", "NSArray", "NSDate", "\x00\x7f{}~|^", "1234567",  # 7: any ASCII
                    "NSObject", "NSString", "Wind.png", "6B Pencil", "Brush Pen",       # 9: the 64
                    "eilotrm.apd", "nsIc ufkMSh", "tailor mode")                        # 11: the first 32
        for text in eligible:
            self.assertTrue(ka.tagged_pointer_eligible(text), ascii(text))
        refused = ("NSMutableArray", "SilicaBrush", "ValkyrieBrush", "NSMutableString",
                   "{0.000000, 0.000000}", "Brush-Preset-Blank.png",
                   "Golden!!", "a{bcdefg", "Golden Qo",          # 8 or 9 with a character outside
                   "NSObjectXX", "0123456789a", "Golden Mode",   # 10 or 11 outside the first 32
                   "eilotrm.apdn",                               # 12 is too long whatever it holds
                   "caf\u00e9", "\u6c34", "a\x80")               # not ASCII
        for text in refused:
            self.assertFalse(ka.tagged_pointer_eligible(text), ascii(text))

    def test_the_alphabet(self):
        self.assertEqual(len(ka.A6), 64)
        self.assertEqual(len(set(ka.A6)), 64)
        self.assertTrue(ka.A6.isascii())
        self.assertEqual(ka.A6[:32], "eilotrm.apdnsIc ufkMShjTRxgC4013")
        self.assertEqual([c for c in "0123456789. -_/" if c not in ka.A6], [])
        self.assertEqual([c for c in "qQZ!{}$,:" if c in ka.A6], [])
        self.assertTrue(ka.tagged_pointer_eligible("12345678"))
        self.assertFalse(ka.tagged_pointer_eligible("1234567890"))     # ten: 2 is not in the first 32

    def test_a_graph_without_curves_is_the_same_bytes_under_both(self):
        archive = build("legacy-plain")
        self.assertEqual(ka.rule_encode(archive, "ios_legacy"), ka.rule_encode(archive, "ios_modern"))
        decoded = ka.decode(ka.rule_encode(archive, "ios_modern"))
        self.assertEqual((decoded.profile, decoded.fidelity), ("ios_legacy", "byte"))
        self.assertEqual(ka.matching_profiles(decoded, decoded.source), ["ios_legacy", "ios_modern"])

    def test_a_graph_with_curves_tells_the_two_apart(self):
        for kind in ("legacy-curves", "modern", "modern-extras"):
            archive = build(kind)
            legacy, modern = (ka.rule_encode(archive, name) for name in ka.PROFILES)
            self.assertNotEqual(legacy, modern, kind)
            for name, data in (("ios_legacy", legacy), ("ios_modern", modern)):
                decoded = ka.decode(data)
                self.assertEqual((decoded.profile, decoded.fidelity), (name, "byte"), kind)
                self.assertEqual(ka.matching_profiles(decoded, data), [name], kind)
                self.assertEqual(decoded.objects, archive.objects, kind)
                self.assertEqual(decoded.top_order, archive.top_order, kind)

    def test_what_differs_is_which_class_names_share_an_object(self):
        archive = build("modern")
        counts = {}
        for name in ka.PROFILES:
            table = bplist.parse_table(ka.rule_encode(archive, name))
            keys = {ref for node in table.objects if node[0] == "dict" for ref in node[1]}
            counts[name] = collections.Counter(
                node[1] for number, node in enumerate(table.objects)
                if node[0] == "ascii" and number not in keys)
        self.assertEqual({text: counts["ios_legacy"][text] for text in
                          ("NSObject", "NSArray", "NSMutableArray", "NSDate")},
                         {"NSObject": 1, "NSArray": 1, "NSMutableArray": 1, "NSDate": 1})
        self.assertEqual({text: counts["ios_modern"][text] for text in
                          ("NSObject", "NSArray", "NSMutableArray", "NSDate")},
                         {"NSObject": 1, "NSArray": 1, "NSMutableArray": 2, "NSDate": 1})
        # "Golden" (the author) fits in a pointer; it is used once, so one object either way.
        self.assertEqual(counts["ios_modern"]["Golden"], 1)
        for name in ka.PROFILES:
            self.assertEqual(counts[name]["SilicaBrush"], 2)
            self.assertEqual(counts[name]["ValkyrieMagnitudinalCurve"], 2)
            self.assertEqual(counts[name]["{0.000000, 0.000000}"], 9)
        self.assertEqual(counts["ios_modern"]["GL-Golden-Grain.png"], 2)

    def test_an_unknown_profile_is_refused(self):
        self.assertEqual(code_of(self, ArchiveError, ka.rule_encode, build("modern"), "ios_17"),
                         "profile")
        self.assertEqual(code_of(self, ArchiveError, ka.rule_encode, build("modern"), None),
                         "profile")


# ── decode and encode ────────────────────────────────────────────────────────

class RoundTrip(unittest.TestCase):
    def test_every_synthetic_graph_comes_back_as_built(self):
        for kind in KINDS:
            archive = build(kind)
            for name in ka.PROFILES:
                data = ka.rule_encode(archive, name)
                decoded = ka.decode(data)
                self.assertEqual(decoded.objects, archive.objects, kind)
                self.assertEqual((decoded.top_order, decoded.version, decoded.archiver, decoded.top),
                                 (archive.top_order, 100000, "NSKeyedArchiver",
                                  PDict([("root", UID(1))])), kind)
                self.assertEqual(decoded.fidelity, "byte", kind)
                self.assertIs(ka.encode(decoded), decoded.source, kind)
                self.assertEqual(decoded.source, data)
                self.assertFalse(ka.is_modified(decoded))
                table = bplist.parse_table(data)
                self.assertTrue(table.contiguous)
                self.assertEqual(bplist.serialize_table(table), data)

    def test_the_legacy_graphs_use_one_byte_references_and_the_modern_two(self):
        sizes = {kind: record(build(kind), "ios_modern") for kind in KINDS}
        self.assertEqual({kind: row["ref_size"] for kind, row in sizes.items()},
                         {"legacy-plain": 1, "legacy-curves": 1, "modern": 2, "modern-extras": 2})
        self.assertLess(sizes["legacy-curves"]["objects"], 256)
        self.assertGreater(sizes["modern"]["objects"], 256)
        self.assertEqual({row["offset_size"] for row in sizes.values()}, {2})

    def test_plistlib_reads_what_the_encoder_writes(self):
        for kind in KINDS:
            archive = build(kind)
            for name in ka.PROFILES:
                top = plistlib.loads(ka.rule_encode(archive, name))
                self.assertEqual(tuple(top), archive.top_order)
                self.assertEqual(top["$version"], 100000)
                self.assertEqual(top["$top"], {"root": plistlib.UID(1)})
                objects = top["$objects"]
                self.assertEqual(len(objects), len(archive.objects))
                self.assertEqual(objects[0], "$null")
                root = objects[1]
                self.assertEqual(list(root), ka.root(archive).keys())
                for key, value in ka.root(archive):
                    if isinstance(value, Real):
                        self.assertEqual(struct.pack(">d", root[key]), struct.pack(">d", value.value), key)
                    elif isinstance(value, UID):
                        self.assertEqual(root[key], plistlib.UID(value.value), key)
                    else:
                        self.assertEqual(root[key], value, key)
                        self.assertIs(type(root[key]), type(value), key)

    def test_the_top_order_is_data_and_is_written_back(self):
        archive = build("modern")
        self.assertEqual(ka.decode(ka.rule_encode(archive, "ios_modern")).top_order, MODERN_TOP)
        archive.top_order = LEGACY_TOP
        legacy_order = ka.rule_encode(archive, "ios_modern")
        self.assertEqual(tuple(plistlib.loads(legacy_order)), LEGACY_TOP)
        self.assertEqual(ka.decode(legacy_order).top_order, LEGACY_TOP)
        self.assertNotEqual(legacy_order, ka.rule_encode(build("modern"), "ios_modern"))

    def test_every_width_and_wrapper_survives(self):
        decoded = ka.decode(ka.rule_encode(build("modern-extras"), "ios_modern"))
        root = ka.root(decoded)
        self.assertEqual(root.get("unknownReal64"), Real.f64(1.0))
        self.assertEqual(root.get("unknownReal64").width, 8)
        self.assertEqual(root.get("unknownFour"), Real.f32(4.0))
        self.assertEqual(root.get("unknownFour").width, 4)
        self.assertEqual(root.get("unknownNegativeZero").bits, b"\x80\x00\x00\x00")
        self.assertEqual((root.get("unknownNegative"), root.get("unknownWide"), root.get("unknownShort")),
                         (-5, 2 ** 40, 1024))
        self.assertEqual(root.get("unknownText"), "inline text")
        self.assertIsInstance(ka.deref(decoded, root.get("color")), bytes)
        date = ka.deref(decoded, root.get("creationDate"))
        self.assertEqual(date.get("NS.time"), Real.f64(694224000.25))
        for key, value in root:
            if key.startswith(("dynamics", "plot")) and isinstance(value, Real):
                self.assertEqual(value.width, 4, key)
            if isinstance(value, bool):
                self.assertIn(value, (True, False))

    def test_unknown_keys_and_classes_are_kept_as_read(self):
        archive = build("modern-extras")
        decoded = ka.decode(ka.rule_encode(archive, "ios_modern"))
        root = ka.root(decoded)
        unknown = ka.deref(decoded, root.get("unknownObject"))
        self.assertEqual(unknown.keys(), ["zeta", "$class", "alpha", "nested"])
        self.assertEqual(unknown.get("alpha"), [UID(0), 7, True])
        self.assertEqual(unknown.get("nested"), PDict([("deep", [Real.f32(-0.0), Real.f32(0.0)])]))
        self.assertEqual(ka.class_name(decoded, root.get("unknownObject")), "RoswUnknownThing")
        self.assertEqual(ka.class_chain(decoded, root.get("unknownObject")),
                         ["RoswUnknownThing", "NSObject"])
        self.assertEqual(root.keys(), ka.root(archive).keys())

    def test_looking_things_up(self):
        archive = build("modern-extras")
        root = ka.root(archive)
        self.assertIs(root, archive.objects[1])
        self.assertEqual(ka.class_name(archive, UID(1)), "SilicaBrush")
        self.assertEqual(ka.class_chain(archive, UID(1)), list(BRUSH))
        self.assertEqual(ka.class_chain(build("legacy-plain"), UID(1)), list(BRUSH_OLDEST))
        self.assertEqual(ka.class_name(archive, root.get("name")), "NSMutableString")
        self.assertEqual(ka.deref(archive, root.get("name")).get("NS.string"), "\u6c34\u58a8 Golden")
        self.assertEqual(ka.class_name(archive, root.get("creationDate")), "NSDate")
        self.assertEqual(ka.class_name(archive, root.get("savedEraseSizes")), "NSArray")
        self.assertIsNone(ka.class_name(archive, root.get("authorName")))      # a plain string
        self.assertIsNone(ka.class_name(archive, UID(0)))
        self.assertIsNone(ka.deref(archive, root.get("bundledHeightPath")))    # nil
        self.assertEqual(ka.deref(archive, 5), 5)
        self.assertEqual(code_of(self, ArchiveError, ka.deref, archive, UID(10 ** 6)), "dangling_uid")
        self.assertEqual(ka.uids_in([UID(3), PDict([("a", [UID(1), 2]), ("b", UID(0))]), "x"]),
                         [UID(3), UID(1), UID(0)])

    def test_one_entry_under_several_keys_stays_one_entry(self):
        for kind, keys in (("modern", SAVED), ("modern-extras", SAVED[1:]),
                           ("modern-extras", ("bundledShapePath", "bundledGrainPath"))):
            decoded = ka.decode(ka.rule_encode(build(kind), "ios_modern"))
            root = ka.root(decoded)
            self.assertEqual(len({root.get(key) for key in keys}), 1, keys)
        plain = ka.root(ka.decode(ka.rule_encode(build("modern"), "ios_modern")))
        self.assertNotEqual(plain.get("bundledShapePath"), plain.get("bundledGrainPath"))


class PlistlibFixtures(unittest.TestCase):
    """The fixtures' archives are written by plistlib: the right graph in a
    layout the app never makes."""

    def test_a_fixture_archive_is_fidelity_table_and_passes_through(self):
        for family, era in (("legacy", "E0"), ("legacy", "E4"), ("modern", None)):
            data = fixtures.make_archive(family, "Fixture \u00e9", era=era, bundled_shape="S.png")
            archive = ka.decode(data)
            self.assertEqual((archive.fidelity, archive.profile), ("table", None), era)
            self.assertEqual(archive.source, data)
            self.assertIs(ka.encode(archive), archive.source)
            self.assertIs(ka.encode(archive, profile="ios_legacy"), archive.source)
            self.assertEqual(ka.matching_profiles(archive, data), [])
            read = fixtures.read_archive(data)
            root = ka.root(archive)
            self.assertEqual(sorted(root.keys()), read["keys"])
            self.assertEqual(tuple(archive.top_order), tuple(read["top_order"]))
            self.assertEqual(ka.class_chain(archive, UID(1)), read["class_chain"])
            self.assertEqual(ka.deref(archive, root.get("name")), "Fixture \u00e9")
            # plistlib stores every real in 8 bytes, and the decoder says so.
            self.assertEqual({v.width for _, v in root if isinstance(v, Real)}, {8})
            self.assertTrue(bplist.parse_table(data).contiguous)

    def test_without_verify_nothing_is_claimed(self):
        data = ka.rule_encode(build("modern"), "ios_modern")
        unverified = ka.decode(data, verify=False)
        self.assertEqual((unverified.fidelity, unverified.profile), ("table", None))
        self.assertIs(ka.encode(unverified), unverified.source)
        self.assertEqual(unverified.objects, ka.decode(data).objects)

    def test_a_changed_table_archive_is_written_by_the_rules(self):
        data = fixtures.make_archive("legacy", "Fixture", era="E4")
        archive = ka.decode(data)
        ka.root(archive).set("plotSpacing", Real.f32(0.75))
        self.assertTrue(ka.is_modified(archive))
        default = ka.encode(archive)
        chosen = ka.encode(archive, profile="ios_legacy")
        self.assertEqual(default, ka.rule_encode(archive, ka.DEFAULT_PROFILE))
        self.assertNotEqual(default, chosen)
        again = ka.decode(chosen)
        self.assertEqual((again.fidelity, again.profile), ("byte", "ios_legacy"))
        entries, keys = differing(data, chosen)
        self.assertEqual((entries, keys), ([1], ["plotSpacing"]))
        self.assertEqual(plistlib.loads(chosen)["$objects"][1]["plotSpacing"], 0.75)

    def test_a_value_the_rules_cannot_write_is_fidelity_table_not_an_error(self):
        """A 16-byte int past 2**64 is a valid property list (the table replays
        it) but no writer of the app's makes one: the file is read, kept and
        returned untouched, and only a changed graph is refused."""
        archive = build("legacy-plain")
        ka.root(archive).set("plotPressure0", 2 ** 63)
        table = bplist.parse_table(ka.rule_encode(archive, "ios_legacy"))
        at = table.objects.index(("int", 16, 2 ** 63))
        table.objects[at] = ("int", 16, 2 ** 100)
        data = bplist.serialize_table(table)
        self.assertEqual(bplist.serialize_table(bplist.parse_table(data)), data)
        read = ka.decode(data)
        self.assertEqual((read.fidelity, read.profile), ("table", None))
        self.assertEqual(ka.matching_profiles(read, data), [])
        self.assertEqual(ka.root(read).get("plotPressure0"), 2 ** 100)
        self.assertIs(ka.encode(read), read.source)
        ka.root(read).set("plotPressure1", Real.f32(0.5))
        self.assertEqual(code_of(self, BplistError, ka.encode, read), "int_range")

    def test_a_fixture_graph_in_the_apps_own_widths_is_byte_exact(self):
        """The same shapes, converted to 4-byte reals outside the decoder."""
        for family, era, profile in (("legacy", "E0", "ios_legacy"), ("legacy", "E3", "ios_legacy"),
                                     ("legacy", "E4", "ios_legacy"), ("modern", None, "ios_modern"),
                                     ("modern", None, "ios_legacy")):
            source = fixtures.make_archive(family, "Fixture Brush", era=era, wrap_name=era == "E3",
                                           curves={"dynamicsPressureSizeCurve": THREE_POINTS}
                                           if era != "E0" else None)
            archive = from_plistlib(source)
            data = ka.rule_encode(archive, profile)
            decoded = ka.decode(data)
            self.assertEqual((decoded.fidelity, decoded.profile), ("byte", profile), era)
            self.assertEqual(decoded.objects, archive.objects)
            self.assertEqual(ka.renumber(decoded).objects, decoded.objects, era)
            self.assertEqual(comparable(plistlib.loads(data)["$objects"]),
                             comparable(plistlib.loads(source)["$objects"]), era)


# ── editing ──────────────────────────────────────────────────────────────────

class Editing(unittest.TestCase):
    def decoded(self, kind="legacy-curves", profile="ios_legacy"):
        return ka.decode(ka.rule_encode(build(kind), profile))

    def test_an_unchanged_archive_is_its_source_and_a_changed_one_is_not(self):
        archive = self.decoded()
        root = ka.root(archive)
        self.assertFalse(ka.is_modified(archive))
        key = next(k for k, v in root if v == Real.f32(0.25))
        root.set(key, Real.f32(0.5))
        self.assertTrue(ka.is_modified(archive))
        self.assertNotEqual(ka.encode(archive), archive.source)
        root.set(key, Real.f32(0.25))                 # put back: the same graph again
        self.assertFalse(ka.is_modified(archive))
        self.assertIs(ka.encode(archive), archive.source)

    def test_a_built_archive_has_no_source_and_is_always_written_by_the_rules(self):
        archive = build("modern")
        self.assertTrue(ka.is_modified(archive))
        self.assertEqual(ka.encode(archive), ka.rule_encode(archive, ka.DEFAULT_PROFILE))
        self.assertEqual(ka.encode(archive, profile="ios_legacy"), ka.rule_encode(archive, "ios_legacy"))
        archive.profile = "ios_legacy"
        self.assertEqual(ka.encode(archive), ka.rule_encode(archive, "ios_legacy"))

    def test_the_same_number_in_another_width_or_sign_is_a_change(self):
        for old, new in ((Real.f32(1.0), Real.f64(1.0)), (Real.f32(0.0), Real.f32(-0.0)),
                         (Real.f32(1.0), 1), (Real.f32(1.0), True)):
            archive = self.decoded()
            root = ka.root(archive)
            key = next(k for k, v in root if v == old)
            root.set(key, new)
            self.assertTrue(ka.is_modified(archive), (old, new))
        archive = self.decoded()
        root = ka.root(archive)
        key = next(k for k, v in root if v is True)
        root.set(key, 1)
        self.assertTrue(ka.is_modified(archive))

    def test_changing_one_key_leaves_every_other_key_alone(self):
        """In the file one 0.0 object serves every key that holds 0.0."""
        for kind, profile in (("legacy-curves", "ios_legacy"), ("modern", "ios_modern")):
            archive = self.decoded(kind, profile)
            before_table = bplist.parse_table(archive.source)
            root = ka.root(archive)
            zeros = [k for k, v in root if v == Real.f32(0.0)]
            self.assertGreater(len(zeros), 10)
            zero_refs = {ref for node in before_table.objects if node[0] == "dict"
                         for ref in node[2] if before_table.objects[ref] == ("real", 4, bytes(4))}
            self.assertEqual(len(zero_refs), 1, "one shared object in the file")
            root.set(zeros[3], Real.f32(0.3))
            data = ka.encode(archive)
            entries, keys = differing(archive.source, data)
            self.assertEqual((entries, keys), ([1], [zeros[3]]), kind)
            after = ka.decode(data)
            self.assertEqual((after.fidelity, after.profile), ("byte", profile))
            new_root = ka.root(after)
            self.assertEqual([k for k, v in new_root if v == Real.f32(0.0)],
                             [k for k in zeros if k != zeros[3]])
            self.assertEqual(new_root.get(zeros[3]), Real.f32(0.3))
            self.assertEqual(len(bplist.parse_table(data).objects), len(before_table.objects) + 1)
            self.assertEqual(len(data), len(archive.source) + 7)       # one 5-byte real, one 2-byte offset

    def test_a_value_that_becomes_whole_joins_the_shared_object(self):
        archive = self.decoded("modern", "ios_modern")
        root = ka.root(archive)
        key = next(k for k, v in root if v == Real.f32(0.123))
        root.set(key, Real.f32(1.0))
        data = ka.encode(archive)
        self.assertEqual(differing(archive.source, data), ([1], [key]))
        self.assertEqual(len(bplist.parse_table(data).objects),
                         len(bplist.parse_table(archive.source).objects) - 1)

    def test_a_bool_an_int_and_a_string_can_be_changed_too(self):
        archive = self.decoded("modern", "ios_modern")
        root = ka.root(archive)
        flag = next(k for k, v in root if v is True)
        number = next(k for k, v in root if isinstance(v, int) and not isinstance(v, bool) and v == 27)
        root.set(flag, False)
        root.set(number, 70000)
        archive.objects[root.get("name").value] = "Renamed \U0001f4a7"
        data = ka.encode(archive)
        entries, keys = differing(archive.source, data)
        self.assertEqual(entries, [1, root.get("name").value])
        self.assertEqual(keys, sorted([flag, number], key=root.keys().index))
        top = plistlib.loads(data)
        self.assertEqual(top["$objects"][root.get("name").value], "Renamed \U0001f4a7")
        self.assertEqual(top["$objects"][1][number], 70000)
        self.assertIs(top["$objects"][1][flag], False)
        self.assertEqual(ka.decode(data).fidelity, "byte")

    def test_uids_still_name_the_same_entries_after_an_edit(self):
        archive = self.decoded("modern-extras", "ios_modern")
        root = ka.root(archive)
        root.set("unknownFour", Real.f32(5.5))
        data = ka.encode(archive)
        one, two = plistlib.loads(archive.source), plistlib.loads(data)
        targets = 0
        for old, new in zip(one["$objects"], two["$objects"]):
            if isinstance(old, dict):
                for key, value in old.items():
                    for uid in (value if isinstance(value, list) else [value]):
                        if isinstance(uid, plistlib.UID):
                            self.assertEqual(comparable(new[key]), comparable(value))
                            if uid.data != 1:
                                self.assertEqual(comparable(one["$objects"][uid.data]),
                                                 comparable(two["$objects"][uid.data]))
                            targets += 1
        self.assertGreater(targets, 90)

    def test_one_entry_under_two_keys_is_the_callers_to_split(self):
        archive = self.decoded("modern", "ios_modern")
        root = ka.root(archive)
        shared = root.get("savedPaintSizes")
        self.assertEqual({root.get(key) for key in SAVED}, {shared})
        # Six keys name one entry: a key that is to differ gets an entry of its own.
        archive.objects.append(Real.f32(0.2402))
        size = UID(len(archive.objects) - 1)
        archive.objects.append(PDict([("NS.objects", [size]),
                                      ("$class", archive.objects[shared.value].get("$class"))]))
        root.set("savedPaintSizes", UID(len(archive.objects) - 1))
        after = ka.decode(ka.encode(ka.renumber(archive)))
        new_root = ka.root(after)
        others = {new_root.get(key) for key in SAVED[1:]}
        self.assertEqual(len(others), 1)
        self.assertNotIn(new_root.get("savedPaintSizes"), others)
        self.assertEqual(ka.deref(after, others.pop()).get("NS.objects"), [])
        mine = ka.deref(after, new_root.get("savedPaintSizes")).get("NS.objects")
        self.assertEqual(ka.deref(after, mine[0]), Real.f32(0.2402))
        self.assertEqual(len(after.objects), len(archive.objects))
        self.assertEqual(ka.renumber(after).objects, after.objects)


# ── numbering ────────────────────────────────────────────────────────────────

class Numbering(unittest.TestCase):
    def test_a_graph_numbered_like_the_apps_is_left_alone(self):
        for kind in KINDS:
            archive = ka.decode(ka.rule_encode(build(kind), "ios_modern"))
            same = ka.renumber(archive)
            self.assertIsNot(same, archive)
            self.assertIsNot(same.objects, archive.objects)
            self.assertEqual(same.objects, archive.objects, kind)
            self.assertFalse(ka.is_modified(same))
            self.assertIs(ka.encode(same), archive.source)

    def test_a_clone_is_a_separate_graph_that_is_still_unchanged(self):
        archive = ka.decode(ka.rule_encode(build("modern-extras"), "ios_modern"))
        copy = ka.clone(archive)
        self.assertEqual((copy.objects, copy.top, copy.top_order, copy.profile, copy.fidelity),
                         (archive.objects, archive.top, archive.top_order, "ios_modern", "byte"))
        self.assertIsNot(copy.objects, archive.objects)
        self.assertIsNot(copy.objects[1], archive.objects[1])
        self.assertFalse(ka.is_modified(copy))
        self.assertIs(ka.encode(copy), archive.source)
        ka.deref(copy, ka.root(copy).get("unknownObject")).get("alpha").append(8)
        self.assertTrue(ka.is_modified(copy))
        self.assertFalse(ka.is_modified(archive))
        self.assertEqual(repr(archive),
                         f"<Archive byte ios_modern {len(archive.objects)} entries, "
                         f"{len(archive.source)} source bytes>")
        self.assertEqual(repr(build("legacy-plain")), "<Archive table None 5 entries, no source>")

    def test_the_copy_shares_nothing_with_the_original(self):
        archive = ka.decode(ka.rule_encode(build("legacy-curves"), "ios_legacy"))
        copy = ka.renumber(archive)
        ka.root(copy).set("plotPressure0", False)
        ka.deref(copy, ka.root(copy).get("dynamicsPressureSizeCurve")).set("resolution", 2048)
        self.assertFalse(ka.is_modified(archive))
        self.assertTrue(ka.is_modified(copy))

    def test_a_small_graph_step_by_step(self):
        """The root holds a curve and a name; the curve holds an array of two
        points. Entries are given in a jumbled order and come back in the
        app's: instance, contents, then the class the first time it is used."""
        jumbled = Archive(MODERN_TOP, 100000, "NSKeyedArchiver", [
            "$null",
            PDict([("size", Real.f32(0.5)), ("$class", UID(2)), ("name", UID(9)), ("curve", UID(6)),
                   ("nothing", UID(0))]),
            PDict([("$classname", "SilicaBrush"), ("$classes", ["SilicaBrush", "NSObject"])]),
            PDict([("$classname", "Curve"), ("$classes", ["Curve", "NSObject"])]),
            "{1, 1}",
            PDict([("$classname", "NSMutableArray"), ("$classes", list(MUTABLE_ARRAY))]),
            PDict([("$class", UID(3)), ("points", UID(8))]),
            "{0, 0}",
            PDict([("NS.objects", [UID(7), UID(4)]), ("$class", UID(5))]),
            "A Name",
            "nothing refers to this",
        ])
        tidy = ka.renumber(jumbled, ["curve", "name"])
        self.assertEqual(tidy.objects, [
            "$null",
            PDict([("size", Real.f32(0.5)), ("$class", UID(9)), ("name", UID(8)), ("curve", UID(2)),
                   ("nothing", UID(0))]),
            PDict([("$class", UID(7)), ("points", UID(3))]),                    # the curve
            PDict([("NS.objects", [UID(4), UID(5)]), ("$class", UID(6))]),      # its array
            "{0, 0}", "{1, 1}",                                                  # the points
            PDict([("$classname", "NSMutableArray"), ("$classes", list(MUTABLE_ARRAY))]),
            PDict([("$classname", "Curve"), ("$classes", ["Curve", "NSObject"])]),
            "A Name",
            PDict([("$classname", "SilicaBrush"), ("$classes", ["SilicaBrush", "NSObject"])]),
        ])
        self.assertIsNone(tidy.source)
        self.assertEqual(ka.renumber(tidy, ["curve", "name"]).objects, tidy.objects)
        # The other order of the root's children gives the other numbering.
        swapped = ka.renumber(jumbled, ["name", "curve"])
        self.assertEqual(swapped.objects[2], "A Name")
        self.assertEqual(ka.root(swapped).get("curve"), UID(3))
        # Without an order, the present numbers decide: the curve (6) before the name (9).
        self.assertEqual(ka.renumber(jumbled).objects, tidy.objects)
        # The input is untouched.
        self.assertEqual(jumbled.objects[1].get("curve"), UID(6))
        self.assertEqual(len(jumbled.objects), 11)

    def test_a_scrambled_graph_comes_back_in_the_apps_order(self):
        for kind in ("legacy-curves", "modern", "modern-extras"):
            archive = build(kind)
            count = len(archive.objects)
            # Reverse every entry but `$null` and the root, and rename every UID to match.
            moved = {0: 0, 1: 1}
            moved.update({number: count + 1 - number for number in range(2, count)})

            def renamed(value):
                if isinstance(value, UID):
                    return UID(moved[value.value])
                if isinstance(value, PDict):
                    return PDict((key, renamed(item)) for key, item in value)
                if isinstance(value, list):
                    return [renamed(item) for item in value]
                return value
            scrambled = [None] * count
            for number, entry in enumerate(archive.objects):
                scrambled[moved[number]] = renamed(entry)
            order = [key for key, value in sorted(
                ((k, v) for k, v in ka.root(archive) if isinstance(v, UID) and v.value),
                key=lambda pair: pair[1].value)]
            jumbled = Archive(archive.top_order, 100000, "NSKeyedArchiver", scrambled)
            self.assertNotEqual(jumbled.objects, archive.objects)
            self.assertEqual(ka.renumber(jumbled, order).objects, archive.objects, kind)

    def test_one_entry_under_six_keys_is_numbered_once(self):
        archive = build("modern")
        tidy = ka.renumber(archive)
        self.assertEqual(tidy.objects, archive.objects)
        root = ka.root(tidy)
        self.assertEqual({root.get(key) for key in SAVED}, {root.get("savedPaintSizes")})
        self.assertEqual(sum(1 for entry in tidy.objects if isinstance(entry, PDict)
                             and entry.get("NS.objects") == []), 1)

    def test_a_root_that_is_not_entry_one(self):
        archive = Archive(MODERN_TOP, 100000, "NSKeyedArchiver",
                          ["$null", "a name", PDict([("name", UID(1)), ("$class", UID(3))]),
                           PDict([("$classname", "X"), ("$classes", ["X"])])],
                          top=PDict([("root", UID(2))]))
        data = ka.rule_encode(archive, "ios_modern")
        decoded = ka.decode(data)
        self.assertEqual(decoded.top, PDict([("root", UID(2))]))
        self.assertEqual(ka.root(decoded).keys(), ["name", "$class"])
        tidy = ka.renumber(decoded)
        self.assertEqual(tidy.top, PDict([("root", UID(1))]))
        self.assertEqual(tidy.objects, ["$null", PDict([("name", UID(2)), ("$class", UID(3))]),
                                        "a name", PDict([("$classname", "X"), ("$classes", ["X"])])])
        self.assertIsNone(tidy.source)

    def test_uids_that_form_a_cycle_are_data_not_a_loop(self):
        """An instance may name itself, and two may name each other: a UID is
        a number, not a container, so nothing follows it without a visited set."""
        loop = ("Loop", "NSObject")
        archive = Archive(MODERN_TOP, 100000, "NSKeyedArchiver", [
            "$null",
            PDict([("self", UID(1)), ("next", UID(2)), ("$class", UID(4))]),
            PDict([("back", UID(3)), ("$class", UID(4))]),
            PDict([("forth", UID(2)), ("up", UID(1)), ("$class", UID(4))]),
            PDict([("$classname", loop[0]), ("$classes", list(loop))]),
        ])
        decoded = ka.decode(ka.rule_encode(archive, "ios_modern"))
        # "Loop" is both the class name and the head of its chain: shared only by ios_modern.
        self.assertEqual((decoded.fidelity, decoded.profile), ("byte", "ios_modern"))
        self.assertEqual(decoded.objects, archive.objects)
        self.assertEqual(ka.renumber(decoded).objects, archive.objects)
        self.assertIs(ka.encode(decoded), decoded.source)
        self.assertEqual(ka.class_name(decoded, UID(3)), "Loop")

    def test_a_long_chain_of_instances_is_walked_without_recursion(self):
        count = 20_000
        chain = ["$null"] + [PDict([("next", UID(n + 1))]) for n in range(1, count)]
        chain.append(PDict([("next", UID(0))]))
        archive = Archive(LEGACY_TOP, 100000, "NSKeyedArchiver", chain)
        decoded = ka.decode(ka.rule_encode(archive, "ios_legacy"))
        self.assertEqual(len(decoded.objects), count + 1)
        self.assertEqual(ka.renumber(decoded).objects, decoded.objects)
        reversed_chain = Archive(LEGACY_TOP, 100000, "NSKeyedArchiver",
                                 ["$null", PDict([("next", UID(count))])]
                                 + [PDict([("next", UID(n - 1 if n > 2 else 0))])
                                    for n in range(2, count + 1)])
        tidy = ka.renumber(reversed_chain)
        self.assertEqual([entry.get("next") for entry in tidy.objects[1:4]], [UID(2), UID(3), UID(4)])
        self.assertEqual(tidy.objects[-1], PDict([("next", UID(0))]))


# ── what is not a keyed archive ──────────────────────────────────────────────

class Refusals(unittest.TestCase):
    def envelope(self, **changes):
        values = {"$version": 100000, "$archiver": "NSKeyedArchiver",
                  "$top": PDict([("root", UID(1))]),
                  "$objects": ["$null", PDict([("$class", UID(2))]),
                               PDict([("$classname", "X"), ("$classes", ["X"])])]}
        values.update(changes)
        return bplist.dumps(PDict((k, v) for k, v in values.items() if v is not None),
                            shared=ka.legacy_shared)

    def test_the_plain_envelope_is_accepted(self):
        archive = ka.decode(self.envelope())
        self.assertEqual((archive.fidelity, archive.version), ("byte", 100000))
        self.assertEqual(archive.top_order, ("$version", "$archiver", "$top", "$objects"))

    def test_an_envelope_that_is_not_one(self):
        nested = PDict([("root", UID(1))])
        cases = {
            "a missing key": (self.envelope(**{"$archiver": None}), "envelope"),
            "an extra key": (self.envelope(extra=1), "envelope"),
            "a version that is not an int": (self.envelope(**{"$version": "1"}), "envelope"),
            "a version that is a bool": (self.envelope(**{"$version": True}), "envelope"),
            "an archiver that is not text": (self.envelope(**{"$archiver": 5}), "envelope"),
            "objects that are not an array": (self.envelope(**{"$objects": nested}), "envelope"),
            "a top that is not a dict": (self.envelope(**{"$top": [UID(1)]}), "envelope"),
            "a top holding something else": (self.envelope(**{"$top": PDict([("root", 1)])}), "envelope"),
            "a top with no root": (self.envelope(**{"$top": PDict([("trunk", UID(1))])}), "no_root"),
            "a nil root": (self.envelope(**{"$top": PDict([("root", UID(0))])}), "no_root"),
            "a root that is a class name": (self.envelope(**{"$objects": ["$null", "text"]}), "no_root"),
            "a root past the end": (self.envelope(**{"$top": PDict([("root", UID(3))])}), "dangling_uid"),
            "no entries at all": (self.envelope(**{"$objects": []}), "null_object"),
            "entry 0 is not $null": (self.envelope(**{"$objects": [
                "null", PDict([("$class", UID(0))])]}), "null_object"),
            "a class that is not there": (self.envelope(**{"$objects": [
                "$null", PDict([("$class", UID(9))])]}), "dangling_uid"),
            "a dangling UID in an array": (self.envelope(**{"$objects": [
                "$null", PDict([("points", [UID(1), UID(200)])])]}), "dangling_uid"),
        }
        for what, (data, code) in cases.items():
            self.assertEqual(code_of(self, ArchiveError, ka.decode, data), code, what)
        twice = bplist.dumps(PDict([("$version", 1), ("$version", 2), ("$top", nested),
                                    ("$objects", ["$null"])]), shared=ka.legacy_shared)
        self.assertEqual(code_of(self, ArchiveError, ka.decode, twice), "envelope")

    def test_a_top_object_that_is_not_a_dict(self):
        for value in ("only a string", [1, 2], 5, UID(1)):
            data = bplist.dumps(value, shared=ka.legacy_shared)
            self.assertEqual(code_of(self, ArchiveError, ka.decode, data), "envelope", repr(value))

    def test_the_fixtures_hostile_archives(self):
        good = fixtures.make_archive("legacy", "Host", era="E4")
        string_top = plistlib.dumps("only a string", fmt=plistlib.FMT_BINARY)
        self.assertEqual(code_of(self, ArchiveError, ka.decode, string_top), "envelope")
        self.assertEqual(code_of(self, BplistError, ka.decode, b"not a property list at all"),
                         "bad_magic")
        self.assertEqual(code_of(self, BplistError, ka.decode, fixtures.LFS_POINTER), "bad_magic")
        with self.assertRaises(BplistError):
            ka.decode(good[:len(good) // 2])
        bare = plistlib.dumps(["folder"], fmt=plistlib.FMT_BINARY)
        self.assertEqual(code_of(self, ArchiveError, ka.decode, bare), "envelope")

    def test_every_truncation_and_every_changed_byte_raises_only_codec_errors(self):
        data = ka.rule_encode(build("legacy-plain"), "ios_legacy")
        outcomes = collections.Counter()
        for cut in range(0, len(data), 3):
            with self.assertRaises(CodecError):
                ka.decode(data[:cut])
        for position in range(0, len(data), 2):
            for value in (0x00, 0xFF, data[position] ^ 0x01):
                if value == data[position]:
                    continue
                changed = data[:position] + bytes((value,)) + data[position + 1:]
                try:
                    archive = ka.decode(changed)
                except CodecError as exc:
                    outcomes[type(exc).__name__] += 1
                else:
                    outcomes[archive.fidelity] += 1
                    self.assertIs(ka.encode(archive), archive.source)
        self.assertGreater(outcomes["BplistError"], 100)
        self.assertGreater(outcomes["ArchiveError"], 10)
        self.assertGreater(outcomes["byte"] + outcomes["table"], 100)

    def test_an_archive_over_a_cap(self):
        self.assertEqual(code_of(self, LimitExceeded, ka.decode, b"bplist00" + bytes(1 << 20)),
                         "archive_bytes")
        deep = leaf = []
        for _ in range(bplist.MAX_DEPTH - 4):     # the envelope, `$objects` and the root come first
            leaf.append([])
            leaf = leaf[0]
        archive = Archive(MODERN_TOP, 1, "A", ["$null", PDict([("deep", deep)])])
        self.assertEqual(ka.decode(ka.rule_encode(archive, "ios_modern")).objects, archive.objects)
        leaf.append([])
        self.assertEqual(code_of(self, LimitExceeded, ka.rule_encode, archive, "ios_modern"),
                         "plist_depth")

    def test_a_graph_that_cannot_be_written(self):
        def broken(change):
            archive = build("legacy-plain")
            change(archive)
            return archive
        cases = {
            "top_order": (lambda a: setattr(a, "top_order", ("$version", "$top", "$objects")), "envelope"),
            "version": (lambda a: setattr(a, "version", 1.0), "envelope"),
            "archiver": (lambda a: setattr(a, "archiver", None), "envelope"),
            "objects": (lambda a: setattr(a, "objects", []), "null_object"),
            "null": (lambda a: a.objects.__setitem__(0, "null"), "null_object"),
            "top": (lambda a: setattr(a, "top", {"root": UID(1)}), "envelope"),
            "no root": (lambda a: setattr(a, "top", PDict()), "no_root"),
            "dangling": (lambda a: ka.root(a).set("name", UID(999)), "dangling_uid"),
            "bool uid": (lambda a: ka.root(a).set("name", UID(True)), "dangling_uid"),
            "root not an instance": (lambda a: a.objects.__setitem__(1, "text"), "no_root"),
        }
        for what, (change, code) in cases.items():
            archive = broken(change)
            self.assertEqual(code_of(self, ArchiveError, ka.rule_encode, archive, "ios_legacy"), code, what)
            self.assertEqual(code_of(self, ArchiveError, ka.encode, archive), code, what)
            self.assertEqual(code_of(self, ArchiveError, ka.renumber, archive), code, what)
        untyped = build("legacy-plain")
        ka.root(untyped).set("plotPressure0", 0.5)
        self.assertEqual(code_of(self, BplistError, ka.encode, untyped), "untyped_real")
        looped = build("legacy-plain")
        loop = []
        loop.append(loop)
        ka.root(looped).set("plotPressure0", loop)
        for call in (ka.encode, ka.renumber, ka.clone):
            self.assertEqual(code_of(self, LimitExceeded, call, looped), "plist_depth")
        self.assertTrue(ka.is_modified(looped))
        ragged = build("legacy-plain")
        ragged.objects[1].append(("one", "two", "three"))
        self.assertEqual(code_of(self, ArchiveError, ka.encode, ragged), "bad_value")


# ── frozen goldens ───────────────────────────────────────────────────────────

GOLDEN_VECTORS = (("legacy-plain", "ios_legacy"), ("legacy-plain", "ios_modern"),
                  ("legacy-curves", "ios_legacy"), ("legacy-curves", "ios_modern"),
                  ("modern", "ios_modern"), ("modern", "ios_legacy"),
                  ("modern-extras", "ios_modern"), ("modern-extras", "ios_legacy"))


def current_vectors():
    return {f"{kind}/{profile}": record(build(kind), profile) for kind, profile in GOLDEN_VECTORS}


class FrozenGoldens(unittest.TestCase):
    """The encoder's output for the synthetic graphs, pinned.

    A failure here means the byte path changed. If that was meant, run the
    opt-in library test first; only when it still reproduces every real
    archive may the vectors be replaced with the ones the failure prints.
    """

    @classmethod
    def setUpClass(cls):
        with open(GOLDENS, "r", encoding="utf-8", newline="") as handle:
            cls.text = handle.read()
        cls.stored = json.loads(cls.text)

    def test_the_file_is_generated_json_with_no_machine_in_it(self):
        self.assertEqual(self.stored["schema"], "rosw-brushes-codec-goldens/1")
        self.assertEqual(self.text, json.dumps(self.stored, ensure_ascii=False, indent=2,
                                               sort_keys=True, allow_nan=False) + "\n")
        self.assertNotIn("\r", self.text)
        # No drive letter, no home folder, no clock: the file is the same on every machine.
        self.assertIsNone(re.search(r"[A-Za-z]:[\\/]|/(?:Users|home)/|\d{4}-\d{2}-\d{2}", self.text))
        self.assertEqual(sorted(self.stored), ["about", "recorded_after", "rule", "schema", "vectors"])
        proof = self.stored["recorded_after"]
        self.assertEqual(proof["byte_identical"], proof["archives"])
        self.assertGreater(proof["archives"], 1000)

    def test_every_vector_is_still_what_the_encoder_writes(self):
        now = current_vectors()
        self.assertEqual(sorted(self.stored["vectors"]), sorted(now))
        for name in sorted(now):
            self.assertEqual(self.stored["vectors"][name], now[name],
                             f"{name}: the encoder now writes {json.dumps(now[name], sort_keys=True)}")

    def test_the_vectors_cover_both_profiles_and_both_reference_sizes(self):
        vectors = self.stored["vectors"]
        self.assertGreaterEqual(len(vectors), 5)
        self.assertEqual({name.split("/")[1] for name in vectors}, set(ka.PROFILES))
        for profile in ka.PROFILES:
            sizes = {row["ref_size"] for name, row in vectors.items() if name.endswith("/" + profile)}
            self.assertEqual(sizes, {1, 2}, profile)
        self.assertEqual(vectors["legacy-plain/ios_legacy"], vectors["legacy-plain/ios_modern"])
        distinct = {row["sha256"] for row in vectors.values()}
        self.assertEqual(len(distinct), len(vectors) - 1)

    def test_the_synthetic_graphs_are_the_same_on_every_run(self):
        for kind in KINDS:
            self.assertEqual(build(kind).objects, build(kind).objects)
        keys = [key for key, _ in scalar_keys(182)]
        self.assertEqual(len(set(keys)), 182)
        self.assertEqual(keys[:3], ["plotPressure0", "dynamicsTiltBleed1", "dynamicsJitterSpeed2"])
        values = dict(scalar_keys(182))
        self.assertEqual((values["plotPressure0"], values["dynamicsTiltBleed1"],
                          values["dynamicsJitterSpeed2"]), (True, 0, Real.f32(1.0)))


# ── the real library, opt-in ─────────────────────────────────────────────────

LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"
SKIPPED_FOLDERS = {"__macosx", "_docs"}
ARCHIVE_NAME = "Brush.archive"


def library_archives(root):
    """(container, entry, bytes) for every Brush.archive under `root`, read in
    memory: nothing is extracted and no entry name is used as a path."""
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if (not path.is_file() or path.suffix.lower() not in (".brush", ".brushset")
                or any(part.lower() in SKIPPED_FOLDERS for part in relative.parts)):
            continue
        data = path.read_bytes()
        if data.startswith(LFS_HEADER):
            raise AssertionError(f"{relative.as_posix()} is a Git LFS pointer: run git lfs pull")
        seen = set()
        with zipfile.ZipFile(io.BytesIO(data)) as container:
            for info in container.infolist():
                name = info.orig_filename
                parts = name.split("/")
                if (parts[-1] != ARCHIVE_NAME or name in seen
                        or any(part.lower() in SKIPPED_FOLDERS for part in parts)):
                    continue
                seen.add(name)
                if info.file_size > bplist.MAX_BYTES:
                    raise AssertionError(f"{relative.as_posix()}: {name} is over the archive cap")
                yield relative.as_posix(), name, container.read(info)


def place(entry):
    parts = entry.split("/")[:-1]
    if parts[-2:] == ["Reset", "Sub01"]:
        return "Reset/Sub01"
    return parts[-1] if parts and parts[-1] in ("Reset", "Sub01") else "main"


@unittest.skipUnless(CORPUS, "set ROSW_BRUSHES_CORPUS to a library folder to walk the real brush files")
class RealLibrary(unittest.TestCase):
    """Every Brush.archive of the library, byte for byte. 100 percent or a failure."""

    @classmethod
    def setUpClass(cls):
        if not sys.flags.isolated:
            raise AssertionError(
                "brush files are read only by an isolated interpreter. Run:  python -I -m unittest "
                "discover -s brushes/pipeline/tests -p test_keyed_archive.py")
        root = Path(CORPUS).resolve()
        if not root.is_dir():
            raise AssertionError(f"ROSW_BRUSHES_CORPUS is not a folder: {CORPUS}")
        cls.rows = collections.OrderedDict()
        cls.problems = collections.defaultdict(list)
        cls.samples = {}
        cls.unique = {}
        for container, entry, data in library_archives(root):
            pack = "/".join(container.split("/")[:2]) if container.count("/") >= 2 else container
            row = cls.rows.setdefault(pack, collections.Counter())
            where = f"{container} :: {entry}"
            row["archives"] += 1
            row["at " + place(entry)] += 1
            digest = hashlib.sha256(data).hexdigest()
            if digest not in cls.unique:
                cls.unique[digest] = cls.check(data, where)
                row["unique"] += 1
            for name, passed in cls.unique[digest].items():
                row[name] += passed
        if not cls.rows:
            raise AssertionError(f"no .brush or .brushset file under {root}")
        cls.total = collections.Counter()
        for row in cls.rows.values():
            cls.total.update(row)
        cls.report()

    @classmethod
    def check(cls, data, where):
        """One archive against every identity; what failed is noted with the
        first differing offset."""
        result = dict.fromkeys(("replay", "byte", "ios_legacy", "ios_modern", "source", "numbering"), False)
        try:
            table = bplist.parse_table(data)
            result["replay"] = table.contiguous and bplist.serialize_table(table) == data
            if not result["replay"]:
                cls.problems["replay"].append(where)
            archive = ka.decode(data)
        except CodecError as exc:
            cls.problems["read"].append(f"{where}: {exc}")
            return result
        matches = ka.matching_profiles(archive, data)
        result["byte"] = archive.fidelity == "byte" and archive.profile == (matches or [None])[0]
        for name in matches:
            result[name] = True
        if not result["byte"]:
            notes = []
            for name in ka.PROFILES:
                ours = ka.rule_encode(archive, name)
                first = next((n for n, (x, y) in enumerate(zip(ours, data)) if x != y),
                             min(len(ours), len(data)))
                notes.append(f"{name}: first difference at byte {first}, {len(ours)} bytes "
                             f"against {len(data)}")
            cls.problems["byte"].append(f"{where}: " + "; ".join(notes))
        result["source"] = ka.encode(archive) is archive.source and archive.source == data
        if not result["source"]:
            cls.problems["source"].append(where)
        result["numbering"] = ka.renumber(archive).objects == archive.objects
        if not result["numbering"]:
            cls.problems["numbering"].append(where)
        if archive.fidelity == "byte":
            cls.samples.setdefault((archive.profile, table.ref_size), (where, data))
        return result

    @classmethod
    def report(cls):
        lines = ["", f"{'pack':40} {'arch':>5} {'uniq':>5} {'replay':>6} {'byte':>5} "
                     f"{'legacy':>6} {'modern':>6} {'number':>6}"]
        for pack, row in list(cls.rows.items()) + [("TOTAL", cls.total)]:
            lines.append(f"{pack:40} {row['archives']:5} {row['unique']:5} {row['replay']:6} "
                         f"{row['byte']:5} {row['ios_legacy']:6} {row['ios_modern']:6} "
                         f"{row['numbering']:6}")
        places = ", ".join(f"{key[3:]} {count}" for key, count in sorted(cls.total.items())
                           if key.startswith("at "))
        lines.append(f"where the archives sit: {places}")
        sys.stderr.write("\n".join(lines) + "\n")

    def all_pass(self, name):
        self.assertEqual(self.problems[name][:20], [], name)
        self.assertEqual(self.total[name], self.total["archives"], name)

    def test_it_found_archives(self):
        self.assertGreater(self.total["archives"], 0)
        self.assertEqual(self.problems["read"][:20], [])

    def test_every_table_replays_byte_for_byte(self):
        self.all_pass("replay")

    def test_every_archive_is_reproduced_by_a_profile(self):
        self.all_pass("byte")
        self.assertEqual(self.total["byte"], self.total["archives"])

    def test_an_unchanged_archive_is_returned_as_its_source(self):
        self.all_pass("source")

    def test_every_archive_is_numbered_the_way_renumber_numbers(self):
        self.all_pass("numbering")

    def test_one_changed_real_changes_one_key_and_nothing_else(self):
        self.assertTrue(self.samples)
        for (profile, ref_size), (where, data) in sorted(self.samples.items()):
            for value in (0.3, 1.0):
                archive = ka.decode(data)
                root = ka.root(archive)
                key = next(k for k, v in root if v == Real.f32(0.0))
                held_zero = [k for k, v in root if v == Real.f32(0.0) and k != key]
                root.set(key, Real.f32(value))
                out = ka.encode(archive)
                entries, keys = differing(data, out)
                self.assertEqual((entries, keys), ([archive.top.get("root").value], [key]), where)
                again = ka.decode(out)
                self.assertEqual((again.fidelity, again.profile), ("byte", profile), where)
                new_root = ka.root(again)
                self.assertEqual(new_root.get(key), Real.f32(value), where)
                self.assertEqual([k for k in held_zero if new_root.get(k) != Real.f32(0.0)], [], where)
                one, two = plistlib.loads(data)["$objects"], plistlib.loads(out)["$objects"]
                for old, new in zip(one, two):
                    if isinstance(old, dict):
                        for field, held in old.items():
                            if isinstance(held, plistlib.UID):
                                self.assertEqual(new[field], held, where)


if __name__ == "__main__":
    unittest.main()
