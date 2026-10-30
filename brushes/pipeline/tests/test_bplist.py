"""pipeline/bplist.py: binary property lists, read and written byte for byte.

Three oracles stand beside the code under test. The exact bytes of every
object kind are written out here by hand from the file format; plistlib, the
standard library's own reader and writer, checks both directions; and
`assemble` below builds a file from raw pieces with struct alone, so a
malformed or oddly laid out one can be made without the writer under test.

Nothing here reads the brush library. The proof on real files is the opt-in
test in test_keyed_archive.py.

    python -m unittest discover -s brushes/pipeline/tests
"""

import datetime
import plistlib
import random
import struct
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import bplist  # noqa: E402
from bplist import (BplistError, CodecError, ContainerError, Date, LimitExceeded,  # noqa: E402
                    ObjectTable, PDict, Real, UID)

MAGIC = b"bplist00"


def never(text):
    return False


def always(text):
    return True


def trailer(count, top, table_offset, *, offset_size=1, ref_size=1, head=bytes(6)):
    return head + bytes((offset_size, ref_size)) + struct.pack(">QQQ", count, top, table_offset)


def assemble(chunks, *, top=0, ref_size=1, offset_size=1, offsets=None, count=None,
             table_offset=None, gap=b"", head=bytes(6), before_trailer=b""):
    """A property list from raw object bytes, by struct alone. Every argument
    after `chunks` overrides what an honest file would hold."""
    honest, position = [], len(MAGIC)
    for chunk in chunks:
        honest.append(position)
        position += len(chunk)
    body = MAGIC + b"".join(chunks) + gap
    table = b"".join(offset.to_bytes(offset_size, "big")
                     for offset in (honest if offsets is None else offsets))
    return (body + table + before_trailer
            + trailer(len(chunks) if count is None else count, top,
                      len(body) if table_offset is None else table_offset,
                      offset_size=offset_size, ref_size=ref_size, head=head))


def single(chunk):
    """The file whose one object is `chunk`."""
    return MAGIC + chunk + b"\x08" + trailer(1, 0, 8 + len(chunk))


def plain(value):
    """A logical value as plistlib would hand it over."""
    if isinstance(value, Real):
        return value.value
    if isinstance(value, UID):
        return plistlib.UID(value.value)
    if isinstance(value, PDict):
        return {key: plain(item) for key, item in value}
    if isinstance(value, list):
        return [plain(item) for item in value]
    return value


def code_of(case, error, call, *args, **kwargs):
    with case.assertRaises(error) as caught:
        call(*args, **kwargs)
    return caught.exception.code


# ── every object kind, byte for byte ─────────────────────────────────────────

F32_ONE = bytes.fromhex("3f800000")
F64_ONE = bytes.fromhex("3ff0000000000000")
SCALARS = [
    # (logical value, the object's bytes, the node parse_table returns)
    (False, "08", ("bool", False)),
    (True, "09", ("bool", True)),
    (0, "1000", ("int", 1, 0)),
    (255, "10ff", ("int", 1, 255)),
    (256, "110100", ("int", 2, 256)),
    (1024, "110400", ("int", 2, 1024)),
    (65535, "11ffff", ("int", 2, 65535)),
    (65536, "1200010000", ("int", 4, 65536)),
    (100000, "12000186a0", ("int", 4, 100000)),
    (2 ** 32 - 1, "12ffffffff", ("int", 4, 2 ** 32 - 1)),
    (2 ** 32, "130000000100000000", ("int", 8, 2 ** 32)),
    (2 ** 63 - 1, "137fffffffffffffff", ("int", 8, 2 ** 63 - 1)),
    (-1, "13ffffffffffffffff", ("int", 8, -1)),
    (-(2 ** 63), "138000000000000000", ("int", 8, -(2 ** 63))),
    (Real(F32_ONE), "223f800000", ("real", 4, F32_ONE)),
    (Real.f32(0.0), "2200000000", ("real", 4, bytes(4))),
    (Real.f32(-0.0), "2280000000", ("real", 4, b"\x80\x00\x00\x00")),
    (Real.f32(0.1), "223dcccccd", ("real", 4, bytes.fromhex("3dcccccd"))),
    (Real(F64_ONE), "233ff0000000000000", ("real", 8, F64_ONE)),
    (Real.f64(0.1), "233fb999999999999a", ("real", 8, bytes.fromhex("3fb999999999999a"))),
    (Date(F64_ONE), "333ff0000000000000", ("date", F64_ONE)),
    (b"", "40", ("data", b"")),
    (b"\x01\x02", "420102", ("data", b"\x01\x02")),
    (bytes(range(16)), "4f1010000102030405060708090a0b0c0d0e0f", ("data", bytes(range(16)))),
    ("", "50", ("ascii", "")),
    ("abc", "53616263", ("ascii", "abc")),
    ("$null", "55246e756c6c", ("ascii", "$null")),
    ("NSKeyedArchiver", "5f100f4e534b657965644172636869766572", ("ascii", "NSKeyedArchiver")),
    ("\u00e9", "6100e9", ("utf16", "\u00e9")),
    ("Cont\u00e9", "650043006f006e007400e9", ("utf16", "Cont\u00e9")),
    ("\u6c34\u58a8", "626c3458a8", ("utf16", "\u6c34\u58a8")),
    ("\U0001f4a7", "62d83ddca7", ("utf16", "\U0001f4a7")),        # one character, two units
    (UID(0), "8000", ("uid", 1, 0)),
    (UID(1), "8001", ("uid", 1, 1)),
    (UID(255), "80ff", ("uid", 1, 255)),
    (UID(256), "810100", ("uid", 2, 256)),
    (UID(65536), "8300010000", ("uid", 4, 65536)),
    (UID(2 ** 32), "870000000100000000", ("uid", 8, 2 ** 32)),
]


class EveryObjectKind(unittest.TestCase):
    def test_each_scalar_is_written_as_the_format_says(self):
        for value, spelled, _ in SCALARS:
            self.assertEqual(bplist.dumps(value, shared=never).hex(),
                             single(bytes.fromhex(spelled)).hex(), repr(value))

    def test_each_scalar_is_read_back_with_its_width(self):
        for value, spelled, node in SCALARS:
            data = single(bytes.fromhex(spelled))
            table = bplist.parse_table(data)
            self.assertEqual(table.objects, [node], repr(value))
            self.assertEqual((table.top, table.offset_size, table.ref_size, table.contiguous),
                             (0, 1, 1, True))
            read = bplist.loads(data)
            self.assertEqual(read, value)
            self.assertIs(type(read), type(value))
            self.assertEqual(bplist.serialize_table(table), data)

    def test_plistlib_reads_the_same_values(self):
        for value, spelled, _ in SCALARS:
            if isinstance(value, Date):
                continue
            self.assertEqual(plistlib.loads(single(bytes.fromhex(spelled))), plain(value),
                             repr(value))

    def test_a_sixteen_byte_int_is_read_and_replayed(self):
        """The standard library writes one for a value past eight signed bytes."""
        data = plistlib.dumps(2 ** 63, fmt=plistlib.FMT_BINARY)
        table = bplist.parse_table(data)
        self.assertEqual(table.objects, [("int", 16, 2 ** 63)])
        self.assertEqual(bplist.serialize_table(table), data)
        self.assertEqual(bplist.dumps(2 ** 63, shared=never), data)
        self.assertEqual(code_of(self, BplistError, bplist.dumps, 2 ** 64, shared=never),
                         "int_range")
        self.assertEqual(code_of(self, BplistError, bplist.dumps, -(2 ** 63) - 1, shared=never),
                         "int_range")

    def test_a_small_array_and_a_small_dict(self):
        self.assertEqual(bplist.dumps([True], shared=never).hex(),
                         (MAGIC + bytes.fromhex("a101" "09") + b"\x08\x0a" + trailer(2, 0, 11)).hex())
        self.assertEqual(bplist.dumps(PDict([("a", True)]), shared=never).hex(),
                         (MAGIC + bytes.fromhex("d10102" "5161" "09") + b"\x08\x0b\x0d"
                          + trailer(3, 0, 14)).hex())
        self.assertEqual(bplist.dumps([], shared=never), single(b"\xa0"))
        self.assertEqual(bplist.dumps(PDict(), shared=never), single(b"\xd0"))

    def test_a_count_of_fifteen_or_more_is_written_as_an_int(self):
        for length, head in ((14, "5e"), (15, "5f100f"), (255, "5f10ff"), (256, "5f110100"),
                             (65535, "5f11ffff"), (65536, "5f1200010000")):
            data = bplist.dumps("x" * length, shared=never)
            self.assertTrue(data.startswith(MAGIC + bytes.fromhex(head) + b"x"), length)
            self.assertEqual(bplist.loads(data), "x" * length)
        for length, head in ((14, "4e"), (15, "4f100f"), (300, "4f11012c")):
            self.assertTrue(bplist.dumps(bytes(length), shared=never).startswith(
                MAGIC + bytes.fromhex(head)), length)
        for length, head in ((14, "6e"), (15, "6f100f")):
            self.assertTrue(bplist.dumps("\u00e9" * length, shared=never).startswith(
                MAGIC + bytes.fromhex(head)), length)
        for length, head in ((14, "ae"), (15, "af100f"), (300, "af11012c")):
            data = bplist.dumps([7] * length, shared=never)
            self.assertTrue(data.startswith(MAGIC + bytes.fromhex(head)), length)
            self.assertEqual(bplist.loads(data), [7] * length)
        many = PDict((f"k{n:03}", n) for n in range(15))
        self.assertTrue(bplist.dumps(many, shared=never).startswith(MAGIC + bytes.fromhex("df100f")))

    def test_a_utf16_count_is_in_units_not_characters(self):
        text = "\U0001f4a7" * 8                      # 8 characters, 16 units
        data = bplist.dumps(text, shared=never)
        self.assertTrue(data.startswith(MAGIC + bytes.fromhex("6f1010d83ddca7")))
        self.assertEqual(bplist.loads(data), text)

    def test_ascii_is_bytes_and_anything_else_is_utf16(self):
        self.assertEqual(bplist.flatten("plain ~ text", shared=never).objects[0][0], "ascii")
        for text in ("caf\u00e9", "\u2019", "a\x80"):
            self.assertEqual(bplist.flatten(text, shared=never).objects[0][0], "utf16", ascii(text))

    def test_byte_count(self):
        for n, width in ((0, 1), (255, 1), (256, 2), (65535, 2), (65536, 4),
                         (2 ** 32 - 1, 4), (2 ** 32, 8)):
            self.assertEqual(bplist.byte_count(n), width, n)


# ── the writer's rules ───────────────────────────────────────────────────────

class WriterRules(unittest.TestCase):
    def objects(self, value, shared=never):
        table = bplist.flatten(value, shared=shared)
        self.assertEqual(table.top, 0)
        self.assertTrue(table.contiguous)
        return table.objects

    def test_a_dict_is_numbered_before_its_keys_and_its_keys_before_its_values(self):
        value = PDict([("b", PDict([("y", 1), ("x", [2, 3])])), ("a", 4)])
        self.assertEqual(self.objects(value), [
            ("dict", (1, 2), (3, 10)),          # the top dict takes the first number
            ("ascii", "b"), ("ascii", "a"),     # then both of its keys
            ("dict", (4, 5), (6, 7)),           # then its first value, a dict, whole:
            ("ascii", "y"), ("ascii", "x"),     #   its keys
            ("int", 1, 1),                      #   its first value
            ("array", (8, 9)),                  #   its second value, an array, whole
            ("int", 1, 2), ("int", 1, 3),
            ("int", 1, 4),                      # and only then the top dict's second value
        ])

    def test_key_order_is_the_order_given(self):
        forward = bplist.dumps(PDict([("a", 1), ("b", 2)]), shared=never)
        backward = bplist.dumps(PDict([("b", 2), ("a", 1)]), shared=never)
        self.assertNotEqual(forward, backward)
        self.assertEqual(bplist.loads(backward).keys(), ["b", "a"])
        self.assertEqual(bplist.dumps({"b": 2, "a": 1}, shared=never), backward)

    def test_a_key_is_one_object_in_the_whole_file(self):
        value = [PDict([("k", 1), ("m", 2)]), PDict([("m", 3), ("k", 4)])]
        objects = self.objects(value)
        self.assertEqual([node for node in objects if node[0] == "ascii"],
                         [("ascii", "k"), ("ascii", "m")])
        self.assertEqual(objects[1][1], (2, 3))
        self.assertEqual(objects[6][1], (3, 2))

    def test_a_key_and_an_equal_value_string_are_two_objects(self):
        for shared in (never, always):
            objects = self.objects(PDict([("name", "name"), ("other", "name")]), shared)
            texts = [node for node in objects if node == ("ascii", "name")]
            self.assertEqual(len(texts), 2 if shared is always else 3)
            self.assertNotIn(objects[0][1][0], objects[0][2])

    def test_every_bool_is_a_new_object_but_all_refer_to_the_first(self):
        objects = self.objects([True, False, True, True, False])
        self.assertEqual(objects[0], ("array", (1, 2, 1, 1, 2)))
        self.assertEqual(objects[1:], [("bool", True), ("bool", False), ("bool", True),
                                       ("bool", True), ("bool", False)])

    def test_the_orphan_pattern_byte_for_byte(self):
        data = bplist.dumps(PDict([("a", True), ("b", True), ("c", False)]), shared=never)
        self.assertEqual(data.hex(), (
            MAGIC + bytes.fromhex("d3010203040406" "5161" "5162" "5163" "09" "09" "08")
            + bytes((8, 15, 17, 19, 21, 22, 23)) + trailer(7, 0, 24)).hex())
        self.assertEqual(plistlib.loads(data), {"a": True, "b": True, "c": False})

    def test_every_uid_is_a_new_object_but_all_refer_to_the_first_of_its_value(self):
        objects = self.objects([UID(5), UID(0), UID(5), UID(300), UID(0)])
        self.assertEqual(objects[0], ("array", (1, 2, 1, 4, 2)))
        self.assertEqual(objects[1:], [("uid", 1, 5), ("uid", 1, 0), ("uid", 1, 5),
                                       ("uid", 2, 300), ("uid", 1, 0)])

    def test_an_int_is_one_object_per_value(self):
        objects = self.objects([3, 70000, 3, 0, 70000, 0])
        self.assertEqual(objects, [("array", (1, 2, 1, 3, 2, 3)), ("int", 1, 3),
                                   ("int", 4, 70000), ("int", 1, 0)])

    def test_a_bool_and_an_int_of_the_same_value_are_different_things(self):
        objects = self.objects([1, True, 0, False])
        self.assertEqual(objects, [("array", (1, 2, 3, 4)), ("int", 1, 1), ("bool", True),
                                   ("int", 1, 0), ("bool", False)])

    def test_a_whole_real32_is_shared_and_a_fractional_one_is_not(self):
        zero, one, four, half = (Real.f32(x) for x in (0.0, 1.0, 4.0, 0.5))
        objects = self.objects([zero, half, one, zero, half, four, one, four, Real.f32(-3.0),
                                Real.f32(-3.0), Real.f32(16777216.0), Real.f32(16777216.0)])
        self.assertEqual(objects[0], ("array", (1, 2, 3, 1, 4, 5, 3, 5, 6, 6, 7, 7)))
        self.assertEqual([node[2] for node in objects[1:]],
                         [zero.bits, half.bits, one.bits, half.bits, four.bits,
                          Real.f32(-3.0).bits, Real.f32(16777216.0).bits])

    def test_negative_zero_is_not_zero(self):
        objects = self.objects([Real.f32(0.0), Real.f32(-0.0), Real.f32(0.0)])
        self.assertEqual(objects, [("array", (1, 2, 1)), ("real", 4, bytes(4)),
                                   ("real", 4, b"\x80\x00\x00\x00")])
        self.assertNotEqual(Real.f32(0.0), Real.f32(-0.0))

    def test_a_real_that_is_not_a_number_is_never_shared(self):
        for value in (float("inf"), float("-inf"), float("nan")):
            objects = self.objects([Real.f32(value), Real.f32(value)])
            self.assertEqual(objects[0], ("array", (1, 2)), value)

    def test_a_real64_is_never_shared_and_never_narrowed(self):
        objects = self.objects([Real.f64(1.0), Real.f64(1.0), Real.f32(1.0), Real.f64(0.25)])
        self.assertEqual(objects[0], ("array", (1, 2, 3, 4)))
        self.assertEqual([node[1] for node in objects[1:]], [8, 8, 4, 8])

    def test_a_value_string_is_shared_only_when_the_rule_says_so(self):
        value = ["NSObject", "NSMutableArray", "NSObject", "NSMutableArray"]
        self.assertEqual(self.objects(value, never)[0], ("array", (1, 2, 3, 4)))
        self.assertEqual(self.objects(value, always)[0], ("array", (1, 2, 1, 2)))
        self.assertEqual(self.objects(value, lambda text: text == "NSObject")[0],
                         ("array", (1, 2, 1, 3)))

    def test_data_is_never_shared(self):
        self.assertEqual(self.objects([b"same", b"same"], always),
                         [("array", (1, 2)), ("data", b"same"), ("data", b"same")])

    def test_a_date_is_never_shared(self):
        self.assertEqual(self.objects([Date(F64_ONE), Date(F64_ONE)], always)[0],
                         ("array", (1, 2)))

    def test_what_has_no_form_is_refused(self):
        self.assertEqual(code_of(self, BplistError, bplist.dumps, 1.5, shared=never),
                         "untyped_real")
        self.assertEqual(code_of(self, BplistError, bplist.dumps, [None], shared=never),
                         "unsupported")
        self.assertEqual(code_of(self, BplistError, bplist.dumps, {1: "x"}, shared=never),
                         "bad_key")
        self.assertEqual(code_of(self, BplistError, bplist.dumps, PDict([(1, "x")]), shared=never),
                         "bad_key")
        self.assertEqual(code_of(self, BplistError, bplist.dumps, PDict(["ab"]), shared=never),
                         "bad_value")
        self.assertEqual(code_of(self, BplistError, bplist.dumps, PDict([("a", 1, 2)]),
                                 shared=never), "bad_value")
        self.assertEqual(code_of(self, BplistError, bplist.dumps, UID(-1), shared=never),
                         "uid_range")
        self.assertEqual(code_of(self, BplistError, bplist.dumps, {datetime.date(2020, 1, 1)},
                                 shared=never), "unsupported")

    def test_a_value_that_holds_itself_is_refused_not_followed(self):
        loop = []
        loop.append(loop)
        self.assertEqual(code_of(self, LimitExceeded, bplist.dumps, loop, shared=never),
                         "plist_depth")
        deep = leaf = []
        for _ in range(bplist.MAX_DEPTH - 1):
            leaf.append([])
            leaf = leaf[0]
        self.assertEqual(bplist.loads(bplist.dumps(deep, shared=never)), deep)
        leaf.append([])
        self.assertEqual(code_of(self, LimitExceeded, bplist.dumps, deep, shared=never),
                         "plist_depth")

    def test_more_values_than_the_cap_are_refused(self):
        self.assertEqual(code_of(self, LimitExceeded, bplist.flatten, [True] * 50, shared=never,
                                 max_objects=50), "plist_objects")
        self.assertEqual(len(bplist.flatten([True] * 49, shared=never, max_objects=50).objects), 50)

    def test_the_cap_counts_values_and_keys_where_they_stand_as_the_reader_does(self):
        """An array of ten dicts with one key and one value between them is
        thirteen objects and thirty-one places. What the writer accepts, the
        reader reads."""
        value = [PDict([("k", 7)]) for _ in range(10)]
        self.assertEqual(len(bplist.flatten(value, shared=never).objects), 13)
        table = bplist.flatten(value, shared=never, max_objects=31)
        self.assertEqual(bplist.resolve(table, max_objects=31), value)
        self.assertEqual(code_of(self, LimitExceeded, bplist.flatten, value, shared=never,
                                 max_objects=30), "plist_objects")
        self.assertEqual(code_of(self, LimitExceeded, bplist.resolve, table, max_objects=30),
                         "plist_objects")


class TrailerSizes(unittest.TestCase):
    def sizes(self, data):
        return data[-26], data[-25], struct.unpack(">QQQ", data[-24:])

    def test_the_reference_size_changes_at_256_objects(self):
        """An array of n different fractional reals is n + 1 objects."""
        for count, ref_size in ((255, 1), (256, 2), (257, 2)):
            value = [Real.f32(n + 0.5) for n in range(count - 1)]
            data = bplist.dumps(value, shared=never)
            _, stored, (objects, top, _) = self.sizes(data)
            self.assertEqual((objects, top, stored), (count, 0, ref_size), count)
            self.assertEqual(bplist.loads(data), value)
            self.assertEqual(bplist.parse_table(data).contiguous, True)

    def test_an_unreferenced_object_counts_towards_the_reference_size(self):
        value = [True] * 255                       # 1 array + 255 bools, 254 of them unreferenced
        data = bplist.dumps(value, shared=never)
        self.assertEqual(self.sizes(data)[1], 2)
        self.assertEqual(data[8:11], bytes.fromhex("af10ff"))
        self.assertEqual(data[11:15], bytes.fromhex("0001 0001"))
        self.assertEqual(bplist.loads(data), value)

    def test_the_offset_size_changes_when_the_table_starts_at_256(self):
        """One data object: 3 bytes of marker and count, then the payload."""
        for payload, table_offset, offset_size in ((244, 255, 1), (245, 256, 2)):
            data = bplist.dumps(bytes(payload), shared=never)
            stored, _, (_, _, at) = self.sizes(data)
            self.assertEqual((at, stored), (table_offset, offset_size))
            self.assertEqual(len(data), table_offset + offset_size + 32)

    def test_the_offset_size_changes_when_the_table_starts_at_65536(self):
        for payload, table_offset, offset_size in ((65523, 65535, 2), (65524, 65536, 4)):
            data = bplist.dumps(bytes(payload), shared=never)
            stored, _, (_, _, at) = self.sizes(data)
            self.assertEqual((at, stored), (table_offset, offset_size))
            self.assertEqual(bplist.loads(data), bytes(payload))

    def test_the_trailer_is_six_zero_bytes_two_sizes_and_three_numbers(self):
        data = bplist.dumps(PDict([("k", [1, 2, 3])]), shared=never)
        self.assertEqual(data[-32:-26], bytes(6))
        self.assertEqual(data[-26:-24], b"\x01\x01")
        self.assertEqual(struct.unpack(">QQQ", data[-24:]), (6, 0, len(data) - 32 - 6))


# ── the table, kept verbatim ─────────────────────────────────────────────────

PLISTLIB_VALUES = [
    True, 0, -5, 2 ** 40, 1.5, "text", "caf\u00e9 \U0001f4a7", b"\x00\xff", plistlib.UID(7),
    [], {}, [1, [2, [3, [4]]]], {"b": 1, "a": {"c": [True, False, True]}},
    {"$version": 100000, "$objects": ["$null", {"$class": plistlib.UID(2), "x": 0.25}],
     "$archiver": "NSKeyedArchiver", "$top": {"root": plistlib.UID(1)}},
    ["x" * 300, b"y" * 70000, list(range(300))],
    datetime.datetime(2020, 5, 17, 12, 30, 0),
]


class TableReplay(unittest.TestCase):
    def test_a_file_plistlib_wrote_is_replayed_byte_for_byte(self):
        for value in PLISTLIB_VALUES:
            data = plistlib.dumps(value, fmt=plistlib.FMT_BINARY, sort_keys=False)
            table = bplist.parse_table(data)
            self.assertTrue(table.contiguous, repr(value)[:40])
            self.assertEqual(bplist.serialize_table(table), data, repr(value)[:40])

    def test_three_hundred_objects_use_two_byte_references(self):
        value = [float(n) + 0.5 for n in range(300)]
        data = plistlib.dumps(value, fmt=plistlib.FMT_BINARY)
        table = bplist.parse_table(data)
        self.assertEqual((table.ref_size, len(table.objects)), (2, 301))
        self.assertEqual(bplist.serialize_table(table), data)
        self.assertEqual([real.value for real in bplist.resolve(table)], value)

    def test_widths_no_writer_would_choose_are_kept(self):
        chunks = [
            bytes.fromhex("a6" "000001" "000002" "000003" "000004" "000005" "000006"),
            bytes.fromhex("13" "0000000000000001"),        # the int 1 in eight bytes
            bytes.fromhex("12" "00000001"),                # ... and in four
            bytes.fromhex("82" "000005"),                  # a UID in three bytes
            bytes.fromhex("63" "006100620063"),            # ASCII text stored as UTF-16
            bytes.fromhex("08"),
            bytes.fromhex("23" "3ff0000000000000"),
            bytes.fromhex("09"),                           # nothing refers to this one
        ]
        data = assemble(chunks, ref_size=3, offset_size=4)
        table = bplist.parse_table(data)
        self.assertEqual(table.objects, [
            ("array", (1, 2, 3, 4, 5, 6)), ("int", 8, 1), ("int", 4, 1), ("uid", 3, 5),
            ("utf16", "abc"), ("bool", False), ("real", 8, F64_ONE), ("bool", True)])
        self.assertEqual((table.ref_size, table.offset_size, table.contiguous), (3, 4, True))
        self.assertEqual(bplist.serialize_table(table), data)
        self.assertEqual(bplist.resolve(table), [1, 1, UID(5), "abc", False, Real(F64_ONE)])
        # The logical value, written by the rules, is another file of the same meaning.
        ruled = bplist.dumps(bplist.resolve(table), shared=never)
        self.assertNotEqual(ruled, data)
        self.assertEqual(bplist.loads(ruled), bplist.resolve(table))

    def test_a_top_object_that_is_not_the_first_is_kept(self):
        data = assemble([b"\x09", b"\xa1\x00"], top=1)
        table = bplist.parse_table(data)
        self.assertEqual((table.top, table.contiguous), (1, True))
        self.assertEqual(bplist.resolve(table), [True])
        self.assertEqual(bplist.serialize_table(table), data)

    def test_an_unusual_layout_is_read_and_flagged_not_contiguous(self):
        honest = assemble([b"\xa2\x01\x02", b"\x10\x07", b"\x53abc"])
        self.assertTrue(bplist.parse_table(honest).contiguous)
        odd = {
            "a gap between the objects and the table":
                assemble([b"\xa2\x01\x02", b"\x10\x07", b"\x53abc"], gap=b"\x00\x00"),
            "objects stored out of order":
                assemble([b"\x10\x07", b"\xa2\x01\x02", b"\x53abc"], offsets=[10, 8, 13]),
            "a count written the long way":
                assemble([b"\xaf\x10\x02\x01\x02", b"\x10\x07", b"\x53abc"]),
            "a trailer that is not zero where it is unused":
                assemble([b"\xa2\x01\x02", b"\x10\x07", b"\x53abc"], head=b"\x00\x00\x00\x00\x00\x01"),
            "bytes between the table and the trailer":
                assemble([b"\xa2\x01\x02", b"\x10\x07", b"\x53abc"], before_trailer=b"\x00"),
        }
        for what, data in odd.items():
            table = bplist.parse_table(data)
            self.assertFalse(table.contiguous, what)
            self.assertEqual(bplist.resolve(table), [7, "abc"], what)
            self.assertEqual(bplist.serialize_table(table), honest, what)

    def test_a_hand_made_table_is_written_and_read_back(self):
        table = ObjectTable([("dict", (1,), (2,)), ("utf16", "cl\u00e9"), ("array", (3, 3, 4)),
                             ("real", 4, F32_ONE), ("data", b"\x00" * 20)], 0, 2, 2)
        data = bplist.serialize_table(table)
        again = bplist.parse_table(data)
        self.assertEqual((again.objects, again.top, again.offset_size, again.ref_size),
                         (table.objects, 0, 2, 2))
        self.assertEqual(bplist.resolve(again),
                         PDict([("cl\u00e9", [Real(F32_ONE), Real(F32_ONE), b"\x00" * 20])]))

    def test_a_table_that_cannot_be_written_is_refused(self):
        bad = {
            "bad_table": [ObjectTable([]), ObjectTable([("bool", True)] * 300, 0, 2, 1),
                          ObjectTable([("data", bytes(300)), ("bool", True)], 0, 1, 1),
                          ObjectTable([("bool", True)], 0, 0, 1),
                          ObjectTable([("bool", True)], 0, 1, 9)],
            "ref_range": [ObjectTable([("array", (1,))]), ObjectTable([("bool", True)], 1),
                          ObjectTable([("dict", (0,), (5,))])],
            "bad_node": [ObjectTable([("int", 3, 1)]), ObjectTable([("real", 4, b"\x00")]),
                         ObjectTable([("set", ())]), ObjectTable([("int", 1, -1)]),
                         ObjectTable([("int", 1, 256)]), ObjectTable([("uid", 9, 1)]),
                         ObjectTable([("ascii", "\u00e9")]), ObjectTable([("dict", (0,), ())]),
                         ObjectTable([("date", b"short")]), ObjectTable([None])],
        }
        for code, tables in bad.items():
            for table in tables:
                self.assertEqual(code_of(self, BplistError, bplist.serialize_table, table), code,
                                 repr(table.objects)[:50])


class LogicalTree(unittest.TestCase):
    def test_plistlib_and_this_module_read_each_others_files(self):
        for value in PLISTLIB_VALUES[:-1]:
            data = plistlib.dumps(value, fmt=plistlib.FMT_BINARY, sort_keys=False)
            mine = bplist.loads(data)
            self.assertEqual(plain(mine), value)
            for rule in (never, always):
                self.assertEqual(plistlib.loads(bplist.dumps(mine, shared=rule)), value)

    def test_a_date_object_is_read(self):
        data = plistlib.dumps(datetime.datetime(2001, 1, 1, 0, 0, 1), fmt=plistlib.FMT_BINARY)
        self.assertEqual(bplist.loads(data), Date(F64_ONE))
        self.assertEqual(bplist.loads(data).value, 1.0)
        self.assertEqual(bplist.dumps(Date(F64_ONE), shared=never), data)

    def test_every_real_keeps_its_width(self):
        value = [Real.f32(0.1), Real.f64(0.1)]
        read = bplist.loads(bplist.dumps(value, shared=never))
        self.assertEqual(read, value)
        self.assertEqual([real.width for real in read], [4, 8])
        self.assertNotEqual(read[0], read[1])
        self.assertNotEqual(read[0].value, read[1].value)
        self.assertEqual(Real.f32(0.1).value, struct.unpack(">f", struct.pack(">f", 0.1))[0])
        self.assertEqual(repr(Real.f32(1.0)), "Real.f32(1.0)")
        self.assertEqual(repr(Real.f64(1.0)), "Real.f64(1.0)")
        self.assertEqual({Real.f32(1.0), Real.f32(1.0), Real.f64(1.0)}, {Real.f32(1.0), Real.f64(1.0)})

    def test_a_real_is_four_or_eight_bytes_and_a_real32_has_a_range(self):
        self.assertEqual(code_of(self, BplistError, Real, b"\x00\x00"), "bad_real")
        self.assertEqual(code_of(self, BplistError, Real, 1.0), "bad_real")
        self.assertEqual(code_of(self, BplistError, Real.f32, 1e39), "real_range")
        self.assertEqual(code_of(self, BplistError, Real.f64, 10 ** 400), "real_range")
        for not_a_number in ("1.0", None, True, b"\x00\x00\x00\x00"):
            self.assertEqual(code_of(self, BplistError, Real.f32, not_a_number), "bad_real")
            self.assertEqual(code_of(self, BplistError, Real.f64, not_a_number), "bad_real")
        self.assertEqual(Real.f32(3), Real.f32(3.0))
        self.assertEqual(Real.f32(float("inf")).value, float("inf"))
        self.assertEqual(code_of(self, BplistError, Date, b"\x00"), "bad_date")

    def test_each_place_in_the_tree_has_a_value_of_its_own(self):
        """One array object under two keys is read as two lists."""
        data = assemble([b"\xd2\x01\x02\x03\x03", b"\x51a", b"\x51b", b"\xa1\x04", b"\x10\x07"])
        tree = bplist.loads(data)
        self.assertEqual(tree, PDict([("a", [7]), ("b", [7])]))
        self.assertIsNot(tree.get("a"), tree.get("b"))
        tree.get("a").append(8)
        self.assertEqual(tree.get("b"), [7])

    def test_a_repeated_key_is_kept(self):
        data = assemble([b"\xd2\x01\x01\x02\x03", b"\x51k", b"\x10\x01", b"\x10\x02"])
        tree = bplist.loads(data)
        self.assertEqual(list(tree), [("k", 1), ("k", 2)])
        self.assertEqual(tree.get("k"), 1)
        self.assertEqual(bplist.loads(bplist.dumps(tree, shared=never)), tree)

    def test_pdict(self):
        pairs = PDict([("a", 1), ("b", 2)])
        self.assertEqual((pairs.keys(), pairs.values()), (["a", "b"], [1, 2]))
        self.assertTrue(pairs.has("a") and not pairs.has("z"))
        self.assertEqual((pairs.get("b"), pairs.get("z"), pairs.get("z", 9)), (2, None, 9))
        pairs.set("a", 5)
        pairs.set("c", 6)
        self.assertEqual(list(pairs), [("a", 5), ("b", 2), ("c", 6)])
        self.assertTrue(pairs.drop("b") and not pairs.drop("b"))
        self.assertEqual(pairs, PDict([("a", 5), ("c", 6)]))
        self.assertEqual(pairs.items(), [("a", 5), ("c", 6)])
        self.assertEqual(repr(PDict([("a", 1)])), "PDict([('a', 1)])")

    def test_a_pdict_is_a_list_but_not_an_array(self):
        """The trap in the type: both forms pass isinstance(value, list)."""
        tree = bplist.loads(bplist.dumps(PDict([("d", PDict()), ("a", [])]), shared=never))
        self.assertIsInstance(tree.get("d"), list)
        self.assertFalse(bplist.is_array(tree.get("d")))
        self.assertTrue(bplist.is_array(tree.get("a")))
        self.assertFalse(bplist.is_array(tree))
        self.assertFalse(bplist.is_array("text") or bplist.is_array((1, 2)))
        self.assertIs(type(tree.get("d")), PDict)
        self.assertIs(type(tree.get("a")), list)
        self.assertNotIn("d", tree)                     # `in` looks for a pair
        self.assertTrue(tree.has("d"))


# ── input from a stranger ────────────────────────────────────────────────────

SAMPLE = PDict([
    ("$version", 100000),
    ("$objects", ["$null",
                  PDict([("size", Real.f32(0.25)), ("on", True), ("off", False), ("n", 3),
                         ("name", UID(2)), ("color", UID(3)), ("$class", UID(4)), ("on2", True)]),
                  "Sample \u00e9", bytes(16),
                  PDict([("$classname", "Sample"), ("$classes", ["Sample", "NSObject"])])]),
    ("$archiver", "NSKeyedArchiver"),
    ("$top", PDict([("root", UID(1))])),
])


class HostileInput(unittest.TestCase):
    """Whatever the bytes, the reader raises its own error or returns: no other
    exception, no long wait, nothing sized by a number the file made up."""

    def read(self, data):
        try:
            return bplist.resolve(bplist.parse_table(data))
        except CodecError as exc:
            self.assertIsInstance(exc.code, str)
            return exc

    def test_what_is_not_a_property_list(self):
        for data, code in ((b"", "bad_magic"), (b"bplist00", "truncated"),
                           (b"not a property list at all, but long enough to hold a trailer",
                            "bad_magic"),
                           (b"bplist01" + bytes(40), "bad_magic"),
                           (b"<?xml version='1.0'?><plist><true/></plist>         ", "bad_magic"),
                           (MAGIC + bytes(33), "truncated"),
                           (MAGIC + bytes(34), "bad_trailer")):
            self.assertEqual(code_of(self, BplistError, bplist.parse_table, data), code, data[:12])
        self.assertEqual(code_of(self, BplistError, bplist.parse_table, "bplist00"), "not_bytes")
        self.assertEqual(code_of(self, BplistError, bplist.parse_table, None), "not_bytes")
        self.assertEqual(bplist.loads(bytearray(single(b"\x09"))), True)
        self.assertEqual(bplist.loads(memoryview(single(b"\x09"))), True)

    def test_every_truncation_is_refused(self):
        data = bplist.dumps(SAMPLE, shared=never)
        self.assertEqual(bplist.loads(data), SAMPLE)
        for cut in range(len(data)):
            result = self.read(data[:cut])
            self.assertIsInstance(result, BplistError, cut)

    def test_every_single_byte_change_is_survived(self):
        data = bplist.dumps(SAMPLE, shared=never)
        refused = 0
        for position in range(len(data)):
            for value in (0x00, 0xFF, data[position] ^ 0x01, data[position] ^ 0x80):
                if value == data[position]:
                    continue
                changed = data[:position] + bytes((value,)) + data[position + 1:]
                refused += isinstance(self.read(changed), CodecError)
        self.assertGreater(refused, len(data))

    def test_random_bytes_behind_a_good_header_are_survived(self):
        rng = random.Random(20261003)
        good = bplist.dumps(SAMPLE, shared=never)
        for _ in range(400):
            body = bytes(rng.randrange(256) for _ in range(rng.randrange(1, 80)))
            for data in (assemble([body]), MAGIC + body + good[-40:], good[:20] + body + good[20:]):
                self.read(data)

    def test_a_trailer_that_lies(self):
        chunks = [b"\xa1\x01", b"\x09"]
        cases = {
            "an offset size of 0": (dict(offset_size=1), {-26: 0}, "bad_trailer"),
            "an offset size of 9": (dict(), {-26: 9}, "bad_trailer"),
            "a reference size of 0": (dict(), {-25: 0}, "bad_trailer"),
            "a reference size of 200": (dict(), {-25: 200}, "bad_trailer"),
            "no objects": (dict(count=0), {}, "bad_trailer"),
            "a top object that does not exist": (dict(top=2), {}, "ref_range"),
            "a top object of 2**63": (dict(top=2 ** 63), {}, "ref_range"),
            "more objects than the table holds": (dict(count=3), {}, "offset_range"),
            "2**60 objects": (dict(count=2 ** 60), {}, "offset_range"),
            "2**64 - 1 objects": (dict(count=2 ** 64 - 1), {}, "offset_range"),
            "a table inside the header": (dict(table_offset=4), {}, "offset_range"),
            "a table at offset 8": (dict(table_offset=8), {}, "offset_range"),
            "a table past the end": (dict(table_offset=10 ** 6), {}, "offset_range"),
            "a table at 2**63": (dict(table_offset=2 ** 63), {}, "offset_range"),
            "a table inside the trailer": (dict(table_offset=12), {}, "offset_range"),
        }
        for what, (changes, patches, code) in cases.items():
            data = bytearray(assemble(chunks, **changes))
            for position, value in patches.items():
                data[position] = value
            self.assertEqual(code_of(self, BplistError, bplist.parse_table, bytes(data)), code, what)

    def test_an_offset_out_of_range(self):
        chunks = [b"\xa1\x01", b"\x09"]
        for what, offsets in (("into the header", [8, 3]), ("at the table itself", [8, 11]),
                              ("past the end", [8, 200]), ("zero", [0, 10])):
            data = assemble(chunks, offsets=offsets)
            self.assertEqual(code_of(self, BplistError, bplist.parse_table, data), "offset_range",
                             what)
        wide = assemble(chunks, offsets=[8, 2 ** 63], offset_size=8)
        self.assertEqual(code_of(self, BplistError, bplist.parse_table, wide), "offset_range")

    def test_a_reference_out_of_range(self):
        for chunks in ([b"\xa1\x02", b"\x09"], [b"\xd1\x01\x05", b"\x51k"],
                       [b"\xd1\x09\x01", b"\x51k"]):
            self.assertEqual(code_of(self, BplistError, bplist.parse_table, assemble(chunks)),
                             "ref_range")
        wide = assemble([b"\xa1\xff\xff\xff\xff\xff\xff\xff\xff", b"\x09"], ref_size=8)
        self.assertEqual(code_of(self, BplistError, bplist.parse_table, wide), "ref_range")
        self.assertEqual(code_of(self, BplistError, bplist.parse_table,
                                 assemble([b"\x09"] * 300, offset_size=2)), "bad_trailer")

    def test_a_count_larger_than_the_file(self):
        """The count is checked against the bytes that are left before anything is read."""
        huge = struct.pack(">Q", 2 ** 60)
        for marker in (b"\x4f", b"\x5f", b"\x6f", b"\xaf", b"\xdf"):
            for count in (b"\x10\xff", b"\x11\xff\xff", b"\x12\x7f\xff\xff\xff", b"\x13" + huge,
                          b"\x13" + b"\xff" * 8):
                data = assemble([marker + count + b"\x00" * 4, b"\x09"])
                self.assertEqual(code_of(self, BplistError, bplist.parse_table, data), "truncated",
                                 (marker + count).hex())
        for chunk, code in ((b"\x5f\x09", "bad_count"), (b"\x5f\x14" + bytes(16), "bad_count"),
                            (b"\x5f", "truncated"), (b"\x5f\x11\x00", "truncated"),
                            (b"\x13\x00", "truncated"), (b"\x23\x00\x00", "truncated"),
                            (b"\x33\x00", "truncated"), (b"\x87\x00", "truncated"),
                            (b"\x61\x00", "truncated")):
            data = MAGIC + chunk + b"\x08" + trailer(1, 0, 8 + len(chunk))
            self.assertEqual(code_of(self, BplistError, bplist.parse_table, data), code, chunk.hex())

    def test_a_marker_this_reader_does_not_read(self):
        for marker, code in ((0x00, "unsupported"), (0x0F, "unsupported"), (0x01, "bad_marker"),
                             (0x15, "bad_marker"), (0x20, "bad_marker"), (0x21, "bad_marker"),
                             (0x24, "bad_marker"), (0x30, "bad_marker"), (0x34, "bad_marker"),
                             (0x70, "unsupported"), (0x8F, "bad_marker"), (0x90, "bad_marker"),
                             (0xB0, "unsupported"), (0xC0, "unsupported"), (0xE0, "bad_marker"),
                             (0xF0, "bad_marker")):
            data = single(bytes((marker,)) + bytes(16))
            self.assertEqual(code_of(self, BplistError, bplist.parse_table, data), code, hex(marker))

    def test_a_string_that_is_not_what_its_marker_says(self):
        self.assertEqual(code_of(self, BplistError, bplist.parse_table, single(b"\x52a\xe9")),
                         "bad_string")
        lone = single(b"\x62\xd8\x3d\x00\x41")           # half a pair, then a letter
        table = bplist.parse_table(lone)
        self.assertEqual(bplist.serialize_table(table), lone)
        self.assertEqual(len(bplist.resolve(table)), 2)

    def test_a_dict_key_that_is_not_text(self):
        data = assemble([b"\xd1\x01\x02", b"\x10\x05", b"\x09"])
        self.assertEqual(code_of(self, BplistError, bplist.loads, data), "bad_key")
        self.assertEqual(bplist.serialize_table(bplist.parse_table(data)), data)

    def test_an_array_that_holds_itself(self):
        for chunks in ([b"\xa1\x00"],                                  # itself
                       [b"\xa1\x01", b"\xa1\x02", b"\xa1\x00"],        # a ring of three
                       [b"\xd1\x01\x00", b"\x51k"],                    # a dict as its own value
                       [b"\xa2\x01\x02", b"\x09", b"\xd1\x03\x00", b"\x51k"]):
            data = assemble(chunks)
            table = bplist.parse_table(data)
            self.assertEqual(bplist.serialize_table(table), data)
            self.assertEqual(code_of(self, BplistError, bplist.resolve, table), "cycle")

    def test_containers_nested_too_deep(self):
        def nested(levels):
            chunks = [bytes((0xA1, n + 1)) for n in range(levels - 1)] + [b"\xa0"]
            return assemble(chunks, offset_size=2)
        tree = bplist.loads(nested(bplist.MAX_DEPTH))
        depth = 0
        while tree:
            tree, depth = tree[0], depth + 1
        self.assertEqual(depth, bplist.MAX_DEPTH - 1)
        self.assertEqual(code_of(self, LimitExceeded, bplist.loads, nested(bplist.MAX_DEPTH + 1)),
                         "plist_depth")
        self.assertEqual(code_of(self, LimitExceeded, bplist.loads, nested(200)), "plist_depth")

    def test_a_small_table_that_unfolds_without_end(self):
        """Forty arrays, each naming the next one twice: 2**40 values on paper."""
        chunks = [bytes((0xA2, n + 1, n + 1)) for n in range(40)] + [b"\x09"]
        data = assemble(chunks)
        table = bplist.parse_table(data)
        self.assertEqual(len(table.objects), 41)
        self.assertEqual(code_of(self, LimitExceeded, bplist.resolve, table), "plist_objects")
        self.assertEqual(code_of(self, LimitExceeded, bplist.resolve, table, max_objects=10),
                         "plist_objects")
        # Shared a little, it is simply copied out.
        small = assemble([bytes((0xA2, n + 1, n + 1)) for n in range(4)] + [b"\x09"])
        self.assertEqual(bplist.loads(small), [[[[True, True]] * 2] * 2] * 2)

    def test_objects_that_overlap(self):
        """Many offsets pointing at one large array would multiply the work."""
        big = b"\xaf\x11\x01\x00" + b"\x01" * 256
        data = assemble([big, b"\x09"] + [b""] * 60, offsets=[8, 8 + len(big)] + [8] * 60,
                        offset_size=2)
        self.assertEqual(code_of(self, BplistError, bplist.parse_table, data), "overlap")

    def test_more_objects_than_the_cap(self):
        data = assemble([b"\x09"] * 300, ref_size=2, offset_size=2)
        self.assertEqual(len(bplist.parse_table(data).objects), 300)
        self.assertEqual(code_of(self, LimitExceeded, bplist.parse_table, data, max_objects=299),
                         "plist_objects")
        self.assertEqual(bplist.MAX_OBJECTS, 100_000)

    def test_more_bytes_than_the_cap(self):
        data = bplist.dumps(bytes(5000), shared=never)
        self.assertEqual(bplist.loads(data), bytes(5000))
        self.assertEqual(code_of(self, LimitExceeded, bplist.parse_table, data, max_bytes=5000),
                         "archive_bytes")
        self.assertEqual(code_of(self, LimitExceeded, bplist.parse_table,
                                 MAGIC + bytes(bplist.MAX_BYTES)), "archive_bytes")
        self.assertEqual(bplist.MAX_BYTES, 1 << 20)

    def test_the_largest_file_allowed_is_read_quickly(self):
        """A megabyte of one-byte objects, and a megabyte that is one array."""
        count = 100_000
        many = assemble([b"\xa0"] + [b"\x09"] * (count - 1), ref_size=4, offset_size=4)
        self.assertEqual(len(bplist.parse_table(many).objects), count)
        refs = bplist.MAX_BYTES - 200
        wide = assemble([b"\xaf\x12" + struct.pack(">I", refs) + b"\x01" * refs, b"\x09"],
                        offset_size=4)
        self.assertLessEqual(len(wide), bplist.MAX_BYTES)
        table = bplist.parse_table(wide)
        self.assertEqual(len(table.objects[0][1]), refs)
        self.assertEqual(code_of(self, LimitExceeded, bplist.resolve, table), "plist_objects")


class Errors(unittest.TestCase):
    def test_the_family(self):
        for error in (bplist.BplistError, bplist.ArchiveError, bplist.BrushModelError,
                      bplist.ContainerError, bplist.PngError):
            self.assertTrue(issubclass(error, CodecError), error.__name__)
        self.assertTrue(issubclass(LimitExceeded, ContainerError))
        self.assertTrue(issubclass(bplist.PngUnsupported, bplist.PngError))
        self.assertTrue(issubclass(CodecError, ValueError))

    def test_an_error_of_the_codec_is_never_rewrapped_as_another(self):
        """They are ValueErrors, and the writer also turns stray ValueErrors
        into its own: the one must not be taken for the other."""
        table = ObjectTable([("array", (5,))])
        self.assertEqual(code_of(self, BplistError, bplist.serialize_table, table), "ref_range")
        self.assertEqual(code_of(self, BplistError, bplist.serialize_table,
                                 ObjectTable([("ascii", "\u00e9")])), "bad_node")

    def test_an_error_carries_a_code_and_a_sentence(self):
        error = BplistError("bad_magic", "the file does not begin `bplist00`")
        self.assertEqual((error.code, error.detail), ("bad_magic", "the file does not begin `bplist00`"))
        self.assertEqual(str(error), "bad_magic: the file does not begin `bplist00`")
        self.assertEqual(str(LimitExceeded("plist_depth")), "plist_depth")

    def test_the_caps_are_the_declared_ones(self):
        self.assertEqual((bplist.MAX_BYTES, bplist.MAX_OBJECTS, bplist.MAX_DEPTH),
                         (1024 * 1024, 100000, 64))


if __name__ == "__main__":
    unittest.main()
