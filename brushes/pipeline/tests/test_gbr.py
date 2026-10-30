"""pipeline/gbr.py: the GIMP brush file, version 2, greyscale.

The second implementation is `parse` below: seven big-endian integers, a name
and a body, read straight from the format definition with struct. What the
module writes is checked against that and against one file spelled out byte by
byte, never against the module's own reader alone.

No GIMP and no real .gbr file is used: none was at hand. These tests hold the
writer to the published layout and to "255 is paint"; that GIMP shows the
result as intended is a check for a person (the module docstring says which).

    python -m unittest discover -s brushes/pipeline/tests
"""

import inspect
import random
import struct
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import bplist  # noqa: E402
import fixtures  # noqa: E402
import gbr  # noqa: E402
import png_io  # noqa: E402

HEADER = struct.Struct(">7I")
GIMP = (ord("G") << 24) + (ord("I") << 16) + (ord("M") << 8) + ord("P")


def parse(data):
    """A .gbr file as its fields, read here."""
    header_size, version, width, height, depth, magic, spacing = HEADER.unpack(data[:28])
    return {"header_size": header_size, "version": version, "width": width, "height": height,
            "depth": depth, "magic": magic, "spacing": spacing,
            "name": data[28:header_size], "body": data[header_size:]}


def disc(side):
    """A hard round mark as coverage: 255 inside the circle, 0 outside."""
    middle = (side - 1) / 2
    reach = side / 2 - 1
    return bytes(255 if (x - middle) ** 2 + (y - middle) ** 2 <= reach ** 2 else 0
                 for y in range(side) for x in range(side))


class Layout(unittest.TestCase):
    def test_one_file_byte_by_byte(self):
        data = gbr.write_gbr(2, 2, bytes([0, 255, 128, 1]), name="A")
        self.assertEqual(data.hex(), "".join([
            "0000001e",              # header size: 28 + "A" + its zero byte
            "00000002",              # version
            "00000002", "00000002",  # width, height
            "00000001",              # bytes per pixel: greyscale
            "47494d50",              # "GIMP"
            "0000000a",              # spacing: 10
            "4100",                  # the name and its zero byte
            "00ff8001",              # the mask, as given
        ]))

    def test_the_fields(self):
        mask = random.Random(3).randbytes(7 * 5)
        fields = parse(gbr.write_gbr(7, 5, mask, name="Seven by five", spacing=25))
        self.assertEqual(fields["header_size"], 28 + len(b"Seven by five") + 1)
        self.assertEqual((fields["version"], fields["width"], fields["height"], fields["depth"]), (2, 7, 5, 1))
        self.assertEqual(fields["magic"], GIMP)
        self.assertEqual(fields["spacing"], 25)
        self.assertEqual(fields["name"], b"Seven by five\x00")
        self.assertEqual(fields["body"], mask, "the mask is stored as given, row by row")
        self.assertEqual((gbr.VERSION, gbr.MAGIC, gbr.HEADER_BYTES, gbr.BYTES_GREY), (2, b"GIMP", 28, 1))

    def test_the_file_is_header_name_and_mask_and_nothing_else(self):
        for width, height in ((1, 1), (3, 9), (64, 64), (300, 2)):
            data = gbr.write_gbr(width, height, bytes(width * height), name="n")
            self.assertEqual(len(data), 28 + 2 + width * height)

    def test_a_mask_may_be_a_bytearray_or_a_memoryview(self):
        mask = bytes(range(12))
        expected = gbr.write_gbr(4, 3, mask)
        self.assertEqual(gbr.write_gbr(4, 3, bytearray(mask)), expected)
        self.assertEqual(gbr.write_gbr(4, 3, memoryview(mask)), expected)


class Polarity(unittest.TestCase):
    """In the file 255 is paint: the body is coverage, never its negative."""

    def test_a_hard_round_mark_is_a_solid_disc(self):
        side = 33
        fields = parse(gbr.write_gbr(side, side, disc(side), name="Hard round"))
        body = fields["body"]
        self.assertEqual(body[(side // 2) * side + side // 2], 255, "the centre paints")
        for corner in (0, side - 1, side * (side - 1), side * side - 1):
            self.assertEqual(body[corner], 0, "a corner does not")
        self.assertEqual(body, disc(side))

    def test_a_shape_image_with_white_as_paint_is_the_coverage(self):
        shape = png_io.read_png(fixtures.make_png(16, 16, "L"))       # a soft dot, bright in the middle
        body = parse(gbr.from_image(shape, inverted=False))["body"]
        self.assertEqual(body, shape.pixels)
        self.assertGreater(body[8 * 16 + 8], 200)
        self.assertEqual(body[0], 0)

    def test_a_shape_image_with_black_as_paint_is_turned_round(self):
        drawn_dark = png_io.Image(33, 33, "L", bytes(255 - v for v in disc(33)))
        body = parse(gbr.from_image(drawn_dark, inverted=True))["body"]
        self.assertEqual(body, disc(33), "the same disc, whichever way the image was drawn")
        self.assertNotEqual(parse(gbr.from_image(drawn_dark))["body"], disc(33))

    def test_colour_is_weighed_and_alpha_never_paints(self):
        rng = random.Random(5)
        rgba = png_io.Image(6, 4, "RGBA", rng.randbytes(96))
        for inverted in (False, True):
            expected = png_io.to_gray8(rgba, invert=inverted).pixels
            self.assertEqual(parse(gbr.from_image(rgba, inverted=inverted))["body"], expected)
        clear = png_io.Image(2, 2, "LA", bytes([0, 0, 255, 0, 90, 0, 7, 0]))
        self.assertEqual(parse(gbr.from_image(clear, inverted=True))["body"], bytes(4),
                         "a transparent pixel is no paint, inverted or not")
        self.assertEqual(parse(gbr.from_image(clear, inverted=False))["body"], bytes(4))

    def test_the_stored_size_is_the_images(self):
        fields = parse(gbr.from_image(png_io.Image(9, 4, "L", bytes(36)), name="wide", spacing=40))
        self.assertEqual((fields["width"], fields["height"], fields["spacing"], fields["name"]),
                         (9, 4, 40, b"wide\x00"))

    def test_what_is_not_an_image(self):
        for bad in (None, b"bytes", (2, 2, "L", bytes(4)), png_io.Image(2, 2, "L", bytes(3))):
            with self.assertRaises(gbr.GbrError, msg=repr(bad)) as caught:
                gbr.from_image(bad)
            self.assertEqual(caught.exception.code, "gbr_mask")


class Spacing(unittest.TestCase):
    def test_the_default_is_gimps_own_and_comes_from_no_brush_setting(self):
        self.assertEqual(gbr.SPACING_DEFAULT, 10)
        self.assertEqual((gbr.SPACING_MIN, gbr.SPACING_MAX), (1, 1000))
        self.assertEqual(parse(gbr.write_gbr(1, 1, b"\xff"))["spacing"], 10)
        self.assertEqual(parse(gbr.from_image(png_io.Image(1, 1, "L", b"\xff")))["spacing"], 10)

    def test_the_caller_chooses_it(self):
        for spacing in (1, 2, 10, 25, 100, 141, 999, 1000):
            self.assertEqual(parse(gbr.write_gbr(1, 1, b"\xff", spacing=spacing))["spacing"], spacing)

    def test_out_of_range_or_not_a_whole_number_is_refused(self):
        for spacing in (0, -1, 1001, 2.5, 10.0, True, None, "10"):
            with self.assertRaises(gbr.GbrError, msg=repr(spacing)) as caught:
                gbr.write_gbr(1, 1, b"\xff", spacing=spacing)
            self.assertEqual(caught.exception.code, "gbr_spacing")

    def test_nothing_here_turns_brush_settings_into_a_spacing(self):
        """The writers take a spacing; no function works one out, and none is
        handed the archive's settings."""
        self.assertEqual(list(inspect.signature(gbr.write_gbr).parameters),
                         ["width", "height", "mask", "name", "spacing"])
        self.assertEqual(list(inspect.signature(gbr.from_image).parameters),
                         ["img", "inverted", "name", "spacing"])
        own = sorted(name for name, value in vars(gbr).items()
                     if callable(value) and getattr(value, "__module__", None) == "gbr" and not name.startswith("_"))
        self.assertEqual(own, ["Gbr", "GbrError", "from_image", "read_gbr", "write_gbr"])
        source = (PIPELINE / "gbr.py").read_text(encoding="utf-8")
        code = source.split('"""', 2)[2]
        for word in ("plotSpacing", "sqrt", "SPACING_K"):
            self.assertNotIn(word, code)


class Names(unittest.TestCase):
    def test_a_name_is_utf8_with_one_zero_byte(self):
        for name in ("Hard round", "Broken Conté", "濃墨 1", "Autumn Stamps ", "  two  spaces", "💧", ""):
            fields = parse(gbr.write_gbr(1, 1, b"\x00", name=name))
            self.assertEqual(fields["name"], name.encode("utf-8") + b"\x00", repr(name))
            self.assertEqual(fields["header_size"], 28 + len(name.encode("utf-8")) + 1)

    def test_the_default_name(self):
        self.assertEqual(parse(gbr.write_gbr(1, 1, b"\x00"))["name"], b"Untitled\x00")

    def test_a_long_name_is_cut_at_a_character(self):
        cases = {"a" * 300: 255, "é" * 200: 254, "濃" * 100: 255, "💧" * 64: 252, "a" + "é" * 200: 255,
                 "a" * 255: 255, "a" * 256: 255}
        for name, kept in cases.items():
            fields = parse(gbr.write_gbr(1, 1, b"\x00", name=name))
            stored = fields["name"][:-1]
            self.assertEqual(len(stored), kept, name[:3])
            self.assertLessEqual(len(fields["name"]), 256, "GIMP refuses a longer name")
            self.assertTrue(name.startswith(stored.decode("utf-8")), "cut between characters, never inside one")
            self.assertEqual(fields["body"], b"\x00")
        self.assertEqual(gbr.MAX_NAME_BYTES, 255)

    def test_names_that_cannot_be_written(self):
        for name in ("a\x00b", "\x00", None, b"bytes", 7, "\ud800"):
            with self.assertRaises(gbr.GbrError, msg=repr(name)) as caught:
                gbr.write_gbr(1, 1, b"\x00", name=name)
            self.assertEqual(caught.exception.code, "gbr_name")


class Limits(unittest.TestCase):
    def test_a_side_is_one_to_ten_thousand_pixels(self):
        self.assertEqual(gbr.MAX_SIDE, 10_000)
        self.assertEqual(parse(gbr.write_gbr(10_000, 1, bytes(10_000)))["width"], 10_000)
        self.assertEqual(parse(gbr.write_gbr(1, 10_000, bytes(10_000)))["height"], 10_000)
        for width, height in ((0, 1), (1, 0), (10_001, 1), (1, 10_001), (-1, 1), (1.0, 1), (True, 1), (None, 1),
                              ("2", 2)):
            with self.assertRaises(gbr.GbrError, msg=repr((width, height))) as caught:
                gbr.write_gbr(width, height, bytes(1))
            self.assertEqual(caught.exception.code, "gbr_size")

    def test_the_mask_must_fit_the_size(self):
        for mask in (bytes(5), bytes(7), b"", "sixsix", [0] * 6, None):
            with self.assertRaises(gbr.GbrError, msg=repr(mask)) as caught:
                gbr.write_gbr(3, 2, mask)
            self.assertEqual(caught.exception.code, "gbr_mask")

    def test_the_error_is_a_codec_error(self):
        self.assertTrue(issubclass(gbr.GbrError, bplist.CodecError))
        self.assertFalse(issubclass(gbr.GbrError, png_io.PngError))
        error = gbr.GbrError("gbr_size", "too wide")
        self.assertEqual((error.code, error.detail, str(error)), ("gbr_size", "too wide", "gbr_size: too wide"))


class ReadBack(unittest.TestCase):
    def test_what_is_written_is_read(self):
        mask = random.Random(9).randbytes(12 * 7)
        back = gbr.read_gbr(gbr.write_gbr(12, 7, mask, name="Broken Conté ", spacing=33))
        self.assertEqual(back, gbr.Gbr(12, 7, 1, 33, "Broken Conté ", mask))
        self.assertEqual(gbr.read_gbr(bytearray(gbr.write_gbr(1, 1, b"\x09", name=""))).name, "")

    def test_a_shape_png_through_to_the_mask(self):
        side = 33
        shape_png = png_io.write_png(side, side, "L", disc(side))
        back = gbr.read_gbr(gbr.from_image(png_io.read_png(shape_png), inverted=False, name="Hard round"))
        self.assertEqual((back.width, back.height, back.depth, back.name), (side, side, 1, "Hard round"))
        self.assertEqual(back.pixels[(side // 2) * side + side // 2], 255)
        self.assertEqual(back.pixels[0], 0)

    def test_a_colour_brush_written_by_hand_is_read(self):
        body = bytes(range(2 * 3 * 4))
        data = HEADER.pack(28 + 4, 2, 2, 3, 4, GIMP, 20) + b"rgb\x00" + body
        self.assertEqual(gbr.read_gbr(data), gbr.Gbr(2, 3, 4, 20, "rgb", body))

    def good(self):
        return gbr.write_gbr(3, 2, bytes(range(6)), name="ok", spacing=15)

    def test_what_is_not_this_kind_of_file(self):
        good = self.good()

        def header(**changes):
            fields = dict(header_size=31, version=2, width=3, height=2, depth=1, magic=GIMP, spacing=15)
            fields.update(changes)
            return HEADER.pack(*fields.values()) + good[28:]
        self.assertEqual(gbr.read_gbr(header()), gbr.read_gbr(good))
        bad = {
            "too short for a header": good[:27], "empty": b"",
            "another magic": header(magic=GIMP + 1), "version 1": header(version=1), "version 3": header(version=3),
            "two bytes per pixel": header(depth=2), "no width": header(width=0), "no height": header(height=0),
            "too wide": header(width=10_001), "no room for a name": header(header_size=28),
            "a header size below the header": header(header_size=20),
            "a header size past the file": header(header_size=500),
            "a name longer than GIMP reads": header(header_size=28 + 257),
            "a name with no zero byte": good[:28] + b"okk" + good[31:],
            "a zero byte inside the name": HEADER.pack(32, 2, 3, 2, 1, GIMP, 15) + b"o\x00k\x00" + good[31:],
            "a name that is not UTF-8": good[:28] + b"\xff\xfe\x00" + good[31:],
            "a body too short": good[:-1], "a body too long": good + b"\x00",
            "more pixels than bytes": header(width=4),
        }
        for what, data in bad.items():
            with self.assertRaises(gbr.GbrError, msg=what) as caught:
                gbr.read_gbr(data)
            self.assertEqual(caught.exception.code, "gbr_data", what)
        for data in ("text", None, 5):
            with self.assertRaises(gbr.GbrError):
                gbr.read_gbr(data)

    def test_no_damage_raises_anything_but_a_gbr_error(self):
        good = self.good()
        for length in range(len(good)):
            with self.assertRaises(gbr.GbrError, msg=f"cut to {length}"):
                gbr.read_gbr(good[:length])
        for position in range(len(good)):
            for flip in (0x01, 0x80, 0xFF):
                changed = bytearray(good)
                changed[position] ^= flip
                try:
                    back = gbr.read_gbr(bytes(changed))
                except gbr.GbrError:
                    continue
                self.assertEqual((back.width, back.height, back.depth), (3, 2, 1),
                                 "a change that is still a brush is a change to the spacing, the name or the mask")
        rng = random.Random(2)
        for _ in range(300):
            try:
                gbr.read_gbr(rng.randbytes(rng.randrange(0, 80)))
            except gbr.GbrError:
                pass


if __name__ == "__main__":
    unittest.main()
