"""pipeline/zip_writer.py: the zip container, written the way the app's own
brush files are.

zipfile is the second implementation here: everything the writer makes is read
back with it, and the header fields are also read straight from the bytes with
struct, so a field zipfile does not show cannot hide. Compressed bytes are never
compared with a fixed vector: they depend on the zlib build.

    python -m unittest discover -s brushes/pipeline/tests
"""

import ast
import io
import os
import struct
import sys
import unittest
import zipfile
import zlib
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import fixtures  # noqa: E402
import zip_writer  # noqa: E402

XML = (b'<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0">\n<dict>\n'
       b"\t<key>name</key>\n\t<string>Set</string>\n</dict>\n</plist>\n")
LOCAL = struct.Struct("<4sHHHHHIIIHH")
CENTRAL = struct.Struct("<4sHHHHHHIIIHHHHHII")
END = struct.Struct("<4sHHHHIIH")


def sample():
    """A brush set's worth of entries: binary archives, images, nested folders,
    an empty file and a text plist."""
    brush = fixtures.make_brush("Writer Fixture", "modern", number=21, dual=True, reset=True,
                                author=True, empty=("", "Reset"))
    entries = [(f"{brush.uuid}/{path}", data) for path, data in brush.members]
    entries.append(("brushset.plist", XML))
    return entries


def read_back(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return [(info.orig_filename, archive.read(info)) for info in archive.infolist()]


def infos(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return archive.infolist()


def raw_headers(data):
    """Every header of a zip, parsed here with struct: (end record, central
    records, local records), each a dict of the fields as stored."""
    end_at = len(data) - END.size
    sig, disk, cd_disk, here, total, cd_size, cd_offset, comment = END.unpack(data[end_at:])
    end = {"sig": sig, "disk": disk, "cd_disk": cd_disk, "here": here, "total": total,
           "cd_size": cd_size, "cd_offset": cd_offset, "comment": comment, "at": end_at}
    central, local = [], []
    at = cd_offset
    for _ in range(total):
        (sig, made_by, needs, flags, method, time, date, crc, packed, size, name_len, extra_len,
         comment_len, disk_start, internal, external, offset) = CENTRAL.unpack(data[at:at + CENTRAL.size])
        name = data[at + CENTRAL.size:at + CENTRAL.size + name_len]
        central.append({"sig": sig, "made_by": made_by, "needs": needs, "flags": flags,
                        "method": method, "time": time, "date": date, "crc": crc, "packed": packed,
                        "size": size, "extra_len": extra_len, "comment_len": comment_len,
                        "disk_start": disk_start, "internal": internal, "external": external,
                        "offset": offset, "name": name})
        at += CENTRAL.size + name_len + extra_len + comment_len
        (sig, needs, flags, method, time, date, crc, packed, size, name_len,
         extra_len) = LOCAL.unpack(data[offset:offset + LOCAL.size])
        start = offset + LOCAL.size + name_len + extra_len
        local.append({"sig": sig, "needs": needs, "flags": flags, "method": method, "time": time,
                      "date": date, "crc": crc, "packed": packed, "size": size,
                      "extra_len": extra_len, "name": data[offset + LOCAL.size:offset + LOCAL.size + name_len],
                      "offset": offset, "data": data[start:start + packed], "end": start + packed})
    end["cd_end"] = at
    return end, central, local


class WhatItWrites(unittest.TestCase):
    def setUp(self):
        self.entries = sample()
        self.data = zip_writer.write_zip(self.entries)

    def test_it_returns_bytes_and_zipfile_reads_back_the_same_entries_in_order(self):
        self.assertIsInstance(self.data, bytes)
        self.assertEqual(read_back(self.data), self.entries)
        with zipfile.ZipFile(io.BytesIO(self.data)) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.comment, b"")

    def test_the_header_fields_are_the_ones_the_apps_own_files_carry(self):
        listed = infos(self.data)
        self.assertEqual(len(listed), len(self.entries))
        for info in listed:
            name = info.orig_filename
            self.assertEqual(info.compress_type, zipfile.ZIP_DEFLATED, name)
            self.assertEqual(info.flag_bits, 0x0006, name)
            self.assertEqual(info.create_system, 0, name)
            self.assertEqual(info.create_version, 0, name)
            self.assertEqual(info.extract_version, 20, name)
            self.assertEqual(info.external_attr, 0, name)
            self.assertEqual(info.extra, b"", name)
            self.assertEqual(info.comment, b"", name)
            self.assertEqual(info.volume, 0, name)

    def test_the_same_fields_read_straight_from_the_bytes(self):
        end, central, local = raw_headers(self.data)
        self.assertEqual(end["sig"], b"PK\x05\x06")
        self.assertEqual((end["disk"], end["cd_disk"], end["comment"]), (0, 0, 0))
        self.assertEqual(end["here"], end["total"])
        self.assertEqual(end["total"], len(self.entries))
        self.assertEqual(end["cd_end"], end["at"], "the end record follows the directory at once")
        self.assertEqual(end["cd_size"], end["at"] - end["cd_offset"])
        self.assertEqual(end["at"] + END.size, len(self.data), "nothing follows the end record")
        expected_offset = 0
        for (name, content), entry, head in zip(self.entries, central, local):
            self.assertEqual(entry["sig"], b"PK\x01\x02")
            self.assertEqual(head["sig"], b"PK\x03\x04")
            self.assertEqual(entry["made_by"], 0, "create_version 0 and create_system 0")
            self.assertEqual((entry["needs"], head["needs"]), (20, 20))
            self.assertEqual((entry["flags"], head["flags"]), (6, 6))
            self.assertEqual((entry["method"], head["method"]), (8, 8))
            self.assertEqual((entry["extra_len"], head["extra_len"], entry["comment_len"]), (0, 0, 0))
            self.assertEqual((entry["disk_start"], entry["external"]), (0, 0))
            self.assertEqual(entry["name"], name.encode("ascii"))
            self.assertEqual(head["name"], entry["name"])
            for field in ("time", "date", "crc", "packed", "size"):
                self.assertEqual(head[field], entry[field], (name, field))
            self.assertEqual(entry["size"], len(content))
            self.assertEqual(entry["crc"], zlib.crc32(content) & 0xFFFFFFFF)
            self.assertEqual(entry["offset"], expected_offset, "entries follow each other with no gap")
            expected_offset = head["end"]
        self.assertEqual(end["cd_offset"], expected_offset, "the directory follows the last entry")

    def test_the_flags_carry_no_data_descriptor_no_encryption_and_no_utf8_bit(self):
        for info in infos(self.data):
            self.assertFalse(info.flag_bits & 0x0001)
            self.assertFalse(info.flag_bits & 0x0008)
            self.assertFalse(info.flag_bits & 0x0800)

    def test_no_entry_is_a_folder(self):
        names = [info.orig_filename for info in infos(self.data)]
        self.assertTrue(any("/" in name for name in names), "the sample has nested names")
        self.assertFalse([name for name in names if name.endswith("/")])
        self.assertFalse([info for info in infos(self.data) if info.is_dir()])

    def test_each_entry_is_a_raw_deflate_stream_made_at_level_1(self):
        _, _, local = raw_headers(self.data)
        for (name, content), head in zip(self.entries, local):
            self.assertEqual(zlib.decompress(head["data"], -zlib.MAX_WBITS), content, name)
            maker = zlib.compressobj(1, zlib.DEFLATED, -zlib.MAX_WBITS)
            self.assertEqual(head["data"], maker.compress(content) + maker.flush(), name)

    def test_an_empty_file_is_still_a_deflated_entry(self):
        empties = [info for info in infos(self.data) if info.orig_filename.endswith(".empty")]
        self.assertEqual(len(empties), 2)
        for info in empties:
            self.assertEqual((info.file_size, info.compress_type), (0, zipfile.ZIP_DEFLATED))
            self.assertEqual(info.internal_attr, 0)

    def test_the_internal_attribute_marks_text_and_nothing_else(self):
        by_name = {info.orig_filename: info.internal_attr for info in infos(self.data)}
        self.assertEqual(by_name["brushset.plist"], 1)
        del by_name["brushset.plist"]
        self.assertEqual(set(by_name.values()), {0}, "archives, images and empty files are binary")

    def test_the_same_input_gives_the_same_bytes(self):
        self.assertEqual(zip_writer.write_zip(self.entries), self.data)
        self.assertEqual(zip_writer.write_zip(iter(self.entries)), self.data)

    def test_it_writes_what_a_fixture_container_holds(self):
        brushes = fixtures.standard_official_brushes()
        made = fixtures.brushset_file("Fixture", brushes, plist_extra={"iconName": "icon"})
        entries = fixtures.zip_entries(made)
        self.assertEqual(read_back(zip_writer.write_zip(entries)), entries)


class TextOrBinary(unittest.TestCase):
    def test_zlibs_rule(self):
        self.assertTrue(zip_writer.is_text(XML))
        self.assertTrue(zip_writer.is_text(b"plain words\r\n\twith a tab"))
        self.assertTrue(zip_writer.is_text("Cont\u00e9".encode("utf-8")), "bytes from 128 up are text")
        self.assertFalse(zip_writer.is_text(b""), "nothing at all is binary")
        self.assertFalse(zip_writer.is_text(b"\x07\x08\x0b\x0c\x1a\x1b"), "only tolerated bytes: binary")
        self.assertTrue(zip_writer.is_text(b"\x07\x08\x0b\x0c\x1a\x1b and a word"))
        for value in list(range(0, 7)) + list(range(14, 26)) + list(range(28, 32)):
            self.assertFalse(zip_writer.is_text(b"words " + bytes([value]) + b" words"), value)
        self.assertFalse(zip_writer.is_text(fixtures.make_png()))
        self.assertFalse(zip_writer.is_text(fixtures.make_archive()))

    def test_the_bit_is_set_from_the_whole_entry(self):
        late = b"a" * 70000 + b"\x00"
        data = zip_writer.write_zip([("early.txt", b"a" * 70000), ("late.bin", late)])
        self.assertEqual([info.internal_attr for info in infos(data)], [1, 0])


class Dates(unittest.TestCase):
    def test_the_default_date_is_fixed(self):
        data = zip_writer.write_zip([("a.txt", b"a")])
        self.assertEqual(infos(data)[0].date_time, zip_writer.DEFAULT_DATE_TIME)
        self.assertEqual(zip_writer.DEFAULT_DATE_TIME, (2020, 1, 1, 0, 0, 0))

    def test_one_date_for_every_entry_or_an_entry_its_own(self):
        when = (2026, 10, 8, 17, 30, 44)
        own = (2019, 8, 1, 17, 36, 34)
        data = zip_writer.write_zip([("a", b"a"), ("b", b"b", own), ("c", b"c")], date_time=when)
        self.assertEqual([info.date_time for info in infos(data)], [when, own, when])

    def test_an_odd_second_is_stored_as_the_even_one_before_it(self):
        data = zip_writer.write_zip([("a", b"a")], date_time=(2026, 12, 31, 23, 59, 59))
        self.assertEqual(infos(data)[0].date_time, (2026, 12, 31, 23, 59, 58))

    def test_the_first_and_the_last_date_a_zip_holds(self):
        for when in ((1980, 1, 1, 0, 0, 0), (2107, 12, 31, 23, 59, 58)):
            data = zip_writer.write_zip([("a", b"a")], date_time=when)
            self.assertEqual(infos(data)[0].date_time, when)

    def test_a_date_a_zip_cannot_hold_is_refused(self):
        bad = [(1979, 12, 31, 23, 59, 59), (2108, 1, 1, 0, 0, 0), (2026, 0, 1, 0, 0, 0),
               (2026, 13, 1, 0, 0, 0), (2026, 1, 0, 0, 0, 0), (2026, 1, 32, 0, 0, 0),
               (2026, 1, 1, 24, 0, 0), (2026, 1, 1, 0, 60, 0), (2026, 1, 1, 0, 0, 60),
               (2026, 1, 1), "2026-01-01", (2026, 1, 1, 0, 0, "x"), (1980, 1, 0, 0, 0, 2),
               (1980, 2, 0, 0, 0, 0), (1981, 1, 0, 0, 0, 0)]
        for when in bad:
            with self.assertRaises(zip_writer.ZipWriteError, msg=repr(when)):
                zip_writer.write_zip([("a", b"a")], date_time=when)
            with self.assertRaises(zip_writer.ZipWriteError, msg=repr(when)):
                zip_writer.write_zip([("a", b"a", when)])
        with self.assertRaises(zip_writer.ZipWriteError):
            zip_writer.write_zip([("a", b"a")], date_time=None)

    def test_an_entry_date_of_none_is_the_default(self):
        when = (2026, 10, 8, 17, 30, 44)
        data = zip_writer.write_zip([("a", b"a", None), ("b", b"b", None, None)], date_time=when)
        self.assertEqual([info.date_time for info in infos(data)], [when, when])

    def test_the_zero_date_the_app_writes_is_stored_as_read(self):
        """Every stored `.empty` of two official sets carries date field 32 and
        time field 0: day 0 of January 1980, which zipfile reads back as is."""
        self.assertEqual(zip_writer.ZERO_DATE, (1980, 1, 0, 0, 0, 0))
        data = zip_writer.write_zip([(".empty", b"", zip_writer.ZERO_DATE, "stored")])
        self.assertEqual(infos(data)[0].date_time, zip_writer.ZERO_DATE)
        _, central, local = raw_headers(data)
        self.assertEqual((central[0]["date"], central[0]["time"]), (32, 0))
        self.assertEqual((local[0]["date"], local[0]["time"]), (32, 0))


class Forms(unittest.TestCase):
    """The three forms read off the library's files: fast (the default),
    normal, and stored. Every other header field is the same in all three."""

    def setUp(self):
        self.content = b"<plist>\n" + bytes(range(256)) * 40
        self.entries = [("fast.bin", self.content, None, "fast"),
                        ("normal.bin", self.content, None, "normal"),
                        ("stored.bin", self.content, None, "stored"),
                        (".empty", b"", zip_writer.ZERO_DATE, "stored"),
                        ("default.bin", self.content)]
        self.data = zip_writer.write_zip(self.entries)

    def test_each_form_has_its_method_and_flag_bits(self):
        _, central, local = raw_headers(self.data)
        wanted = [(8, 6), (8, 0), (0, 0), (0, 0), (8, 6)]
        self.assertEqual([(entry["method"], entry["flags"]) for entry in central], wanted)
        self.assertEqual([(head["method"], head["flags"]) for head in local], wanted)
        for entry, head in zip(central, local):
            self.assertEqual((entry["made_by"], entry["needs"], head["needs"], entry["external"],
                              entry["extra_len"], head["extra_len"], entry["comment_len"]),
                             (0, 20, 20, 0, 0, 0, 0))

    def test_each_form_stores_its_data_its_way(self):
        _, _, local = raw_headers(self.data)
        for level, head in ((1, local[0]), (6, local[1]), (1, local[4])):
            maker = zlib.compressobj(level, zlib.DEFLATED, -zlib.MAX_WBITS)
            self.assertEqual(head["data"], maker.compress(self.content) + maker.flush())
        self.assertEqual(local[2]["data"], self.content)
        self.assertEqual((local[2]["packed"], local[2]["size"]), (len(self.content), len(self.content)))
        self.assertEqual((local[3]["packed"], local[3]["size"], local[3]["data"]), (0, 0, b""))

    def test_zipfile_reads_every_form_back(self):
        self.assertEqual(read_back(self.data), [entry[:2] for entry in self.entries])
        with zipfile.ZipFile(io.BytesIO(self.data)) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual([info.compress_type for info in archive.infolist()],
                             [zipfile.ZIP_DEFLATED, zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED,
                              zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED])

    def test_the_text_bit_is_the_same_in_every_form(self):
        self.assertEqual([info.internal_attr for info in infos(self.data)], [0, 0, 0, 0, 0])
        text = zip_writer.write_zip([(f"{form}.txt", b"words\n", None, form) for form in zip_writer.FORMS])
        self.assertEqual([info.internal_attr for info in infos(text)], [1, 1, 1])

    def test_form_of_names_what_a_reader_sees(self):
        for name in zip_writer.FORMS:
            data = zip_writer.write_zip([("a", b"abc", None, name)])
            info = infos(data)[0]
            self.assertEqual(zip_writer.form_of(info.compress_type, info.flag_bits), name)
        for method, flags in ((8, 2), (8, 4), (8, 0x0800 | 6), (8, 1 | 6), (8, 8), (12, 0), (0, 6), (14, 0)):
            self.assertIsNone(zip_writer.form_of(method, flags), (method, flags))

    def test_a_form_that_is_not_one_of_the_three_is_refused(self):
        for form in ("deflate", "FAST", 8, b"fast", ("fast",)):
            with self.assertRaises(zip_writer.ZipWriteError, msg=repr(form)):
                zip_writer.write_zip([("a", b"a", None, form)])

    def test_a_fixture_zip_rebuilt_in_its_own_forms_is_the_same_bytes(self):
        """make_zip writes stored and deflated entries the way zipfile does;
        an entry zipfile stores is one this writer can store the same way."""
        entries = [("a.bin", b"x" * 100), ("b.bin", b"")]
        made = fixtures.make_zip(entries, stored=True)
        with zipfile.ZipFile(io.BytesIO(made)) as archive:
            forms = [zip_writer.form_of(i.compress_type, i.flag_bits) for i in archive.infolist()]
        self.assertEqual(forms, ["stored", "stored"])
        again = zip_writer.write_zip([(n, d, fixtures.ZIP_DATE, f) for (n, d), f in zip(entries, forms)])
        self.assertEqual(read_back(again), entries)


class WhatItRefuses(unittest.TestCase):
    def refused(self, entries):
        with self.assertRaises(zip_writer.ZipWriteError, msg=repr(entries)[:80]) as caught:
            zip_writer.write_zip(entries)
        self.assertIsInstance(caught.exception, ValueError)
        return str(caught.exception)

    def test_names(self):
        bad = ["", "folder/", "/absolute", "C:/drive", "c:relative", "a\\b", "../up", "a/../b",
               "a/./b", "./a", "a//b", "caf\u00e9.png", "\u6d53\u58a8/Brush.archive", "a\x00b",
               "line\nbreak", "tab\there", "del\x7f", None, 7, b"Brush.archive"]
        for name in bad:
            self.refused([(name, b"x")])
            with self.assertRaises(zip_writer.ZipWriteError, msg=repr(name)):
                zip_writer.check_name(name)

    def test_names_that_are_fine(self):
        good = ["Brush.archive", ".empty", "Reset/.empty", "QuickLook/Thumbnail.png",
                "8E7FA79A-900C-47D9-9805-F226BE3C4B04/Reset/Sub01/Brush.archive",
                "name with spaces & signs (1)!.png", "..hidden", "a..b/c"]
        for name in good:
            self.assertEqual(zip_writer.check_name(name), name.encode("ascii"))
        data = zip_writer.write_zip([(name, name.encode("ascii")) for name in good])
        self.assertEqual([name for name, _ in read_back(data)], good)

    def test_a_name_given_twice(self):
        message = self.refused([("a/Brush.archive", b"1"), ("b", b"2"), ("a/Brush.archive", b"3")])
        self.assertIn("twice", message)

    def test_a_name_too_long_for_the_field(self):
        self.refused([("n" * 65536, b"x")])
        self.assertEqual(len(read_back(zip_writer.write_zip([("n" * 65535, b"x")]))[0][0]), 65535)

    def test_data_that_is_not_bytes(self):
        for data in ("text", None, 5, ["b"], io.BytesIO(b"x")):
            self.refused([("a", data)])

    def test_bytes_like_data_is_taken(self):
        made = zip_writer.write_zip([("a", bytearray(b"one")), ("b", memoryview(b"two"))])
        self.assertEqual(read_back(made), [("a", b"one"), ("b", b"two")])

    def test_an_entry_of_the_wrong_shape(self):
        for entry in ("ab", ("a",), ("a", b"x", zip_writer.DEFAULT_DATE_TIME, "more"), None, b"ab"):
            self.refused([entry])

    def test_nothing_partial_comes_back_when_a_later_entry_is_refused(self):
        with self.assertRaises(zip_writer.ZipWriteError):
            zip_writer.write_zip([("good", b"x"), ("bad/", b"y")])

    def test_more_than_the_plain_format_holds(self):
        with mock.patch.object(zip_writer, "MAX_ENTRIES", 2):
            self.assertEqual(len(read_back(zip_writer.write_zip([("a", b""), ("b", b"")]))), 2)
            self.assertIn("zip64", self.refused([("a", b""), ("b", b""), ("c", b"")]))
        with mock.patch.object(zip_writer, "MAX_BYTES", 64):
            self.assertIn("zip64", self.refused([("big", os.urandom(200))]))
            self.assertIn("zip64", self.refused([(f"n{i}", b"0123456789") for i in range(8)]))
        self.assertEqual(zip_writer.MAX_ENTRIES, 0xFFFE)
        self.assertEqual(zip_writer.MAX_BYTES, 0xFFFFFFFE)


class Sizes(unittest.TestCase):
    def test_no_entries_is_a_valid_empty_zip(self):
        data = zip_writer.write_zip([])
        self.assertEqual(data, b"PK\x05\x06" + bytes(18))
        self.assertEqual(read_back(data), [])

    def test_data_that_does_not_shrink_is_deflated_all_the_same(self):
        noise = os.urandom(200000)
        data = zip_writer.write_zip([("Grain.png", noise)])
        info = infos(data)[0]
        self.assertEqual(info.compress_type, zipfile.ZIP_DEFLATED)
        self.assertGreater(info.compress_size, info.file_size, "as some images in the app's files are")
        self.assertEqual(read_back(data), [("Grain.png", noise)])

    def test_a_megabyte_of_each_kind(self):
        entries = [("zeros", bytes(1 << 20)), ("noise", os.urandom(1 << 20)),
                   ("text", b"the same line again\n" * 50000)]
        self.assertEqual(read_back(zip_writer.write_zip(entries)), entries)

    def test_many_entries(self):
        entries = [(f"folder-{n // 100}/file-{n}.bin", n.to_bytes(4, "big") * (n % 7)) for n in range(3000)]
        data = zip_writer.write_zip(entries)
        self.assertEqual(read_back(data), entries)
        end, central, _ = raw_headers(data)
        self.assertEqual((end["total"], len(central)), (3000, 3000))


class TheModule(unittest.TestCase):
    def setUp(self):
        self.source = (PIPELINE / "zip_writer.py").read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)

    def test_it_does_not_lean_on_zipfile_and_is_standard_library_only(self):
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertEqual(imported, {"__future__", "re", "struct", "zlib"})

    def test_it_is_a_library_module_with_no_command_line(self):
        functions = {node.name for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)}
        self.assertNotIn("main", functions)
        self.assertNotIn("__main__", self.source)
        public = {name for name in functions if not name.startswith("_")}
        self.assertEqual(public, {"write_zip", "check_name", "is_text", "form_of"})

    def test_it_opens_no_file(self):
        calls = {node.func.id for node in ast.walk(self.tree)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertNotIn("open", calls)

    def test_the_constants_say_what_the_headers_carry(self):
        self.assertEqual((zip_writer.METHOD_DEFLATE, zip_writer.FLAG_BITS, zip_writer.EXTRACT_VERSION,
                          zip_writer.CREATE_VERSION, zip_writer.CREATE_SYSTEM, zip_writer.EXTERNAL_ATTR,
                          zip_writer.DEFLATE_LEVEL), (8, 0x0006, 20, 0, 0, 0, 1))
        self.assertEqual(zip_writer.METHOD_STORED, 0)
        self.assertEqual(zip_writer.FORMS, {"fast": (8, 0x0006, 1), "normal": (8, 0x0000, 6),
                                            "stored": (0, 0x0000, None)})
        self.assertEqual(zip_writer.DEFAULT_FORM, "fast")

    def test_the_file_is_utf8_with_line_feeds(self):
        raw = (PIPELINE / "zip_writer.py").read_bytes()
        self.assertNotIn(b"\r", raw)
        raw.decode("utf-8")


if __name__ == "__main__":
    unittest.main()
