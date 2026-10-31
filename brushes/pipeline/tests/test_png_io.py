"""pipeline/png_io.py: the PNG reader and writer, and the pixel helpers.

Everything here is synthetic. The second implementation is this file's own
encoder (`encode`, with the five row filters written the long way from the PNG
specification) and the reader and writer in fixtures.py, so that what the
module decodes was never encoded by the module, and what it encodes is read
back by something else. No test reads the real library.

Every test runs on the standard-library path: `HAVE_PIL` is switched off for
each one. The classes at the end switch it back on where PIL is importable and
are skipped where it is not, which is every CI machine.

The real library is opt-in. Set ROSW_BRUSHES_CORPUS to a library folder and
run this file with an isolated interpreter:

    python -I -m unittest discover -s brushes/pipeline/tests -p test_png_io.py

Every PNG member of every .brush and .brushset under it is read in memory with
`png_info`, and each container's first Shape.png, Grain.png and
QuickLook/Thumbnail.png is decoded in full and written back. It takes some
minutes: the large shapes are decoded by the standard library.

    python -m unittest discover -s brushes/pipeline/tests
"""

import collections
import hashlib
import io
import os
import random
import struct
import subprocess
import sys
import time
import unittest
import zipfile
import zlib
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import bplist  # noqa: E402
import fixtures  # noqa: E402
import png_io  # noqa: E402

try:
    from PIL import Image as PilImage
except Exception:                                   # absent on CI
    PilImage = None

CORPUS = os.environ.get("ROSW_BRUSHES_CORPUS", "").strip()

SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
MODE_OF = {0: "L", 2: "RGB", 4: "LA", 6: "RGBA"}
ADAM7 = ((0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2))
FILTER_CHOICES = ((0,), (1,), (2,), (3,), (4,), (0, 1, 2, 3, 4), (4, 3, 2, 1, 0), (3, 4, 1), (2, 2, 4, 0, 3))


# ── an encoder that is not the module's ──────────────────────────────────────

def chunk(kind, body=b""):
    return (struct.pack(">I", len(body)) + kind + body
            + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF))


def ihdr(width, height, depth, color, interlace=0, compression=0, method=0):
    return chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, depth, color, compression, method, interlace))


def assemble(*chunks):
    return SIGNATURE + b"".join(chunks)


def paeth(a, b, c):
    """The predictor, as the PNG specification writes it."""
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def filter_row(kind, line, above, step):
    out = bytearray()
    for index, value in enumerate(line):
        left = line[index - step] if index >= step else 0
        up = above[index]
        corner = above[index - step] if index >= step else 0
        predicted = (0, left, up, (left + up) // 2, paeth(left, up, corner))[kind]
        out.append((value - predicted) & 255)
    return bytes(out)


def filtered(rows, step, kinds):
    """Each row behind its filter byte; `kinds` is cycled over the rows."""
    out = bytearray()
    above = bytes(len(rows[0])) if rows else b""
    for index, line in enumerate(rows):
        kind = kinds[index % len(kinds)]
        out.append(kind)
        out += filter_row(kind, line, above, step)
        above = line
    return bytes(out)


def split(data, size):
    return [data[start:start + size] for start in range(0, len(data), size)]


def encode(width, height, color, depth, samples, *, kinds=(0,), palette=None, trns=None, pieces=1,
           before=(), level=6):
    """A PNG from file-layout samples (rows of packed samples, no filter bytes)."""
    row = (width * CHANNELS[color] * depth + 7) // 8
    assert len(samples) == row * height, "the test built the wrong amount of data"
    step = max(1, CHANNELS[color] * depth // 8)
    packed = zlib.compress(filtered(split(samples, row), step, kinds), level)
    parts = [ihdr(width, height, depth, color)] + [chunk(kind, body) for kind, body in before]
    if palette is not None:
        parts.append(chunk(b"PLTE", palette))
    if trns is not None:
        parts.append(chunk(b"tRNS", trns))
    parts += [chunk(b"IDAT", piece) for piece in split(packed, max(1, -(-len(packed) // pieces)))]
    return assemble(*parts, chunk(b"IEND"))


def encode_interlaced(width, height, color, depth, samples, *, kinds=(0,), palette=None, trns=None):
    """The same image as Adam7 passes, each pass filtered on its own rows.

    For 8 and 16 bits, `samples` is the file layout of the whole image (rows
    of whole-byte pixels). For 1, 2 and 4 bits it is a list of sample values,
    one per pixel, and each pass row is packed on its own, as the
    specification has it: a pass row starts on a byte.
    """
    raw = bytearray()
    for x0, y0, dx, dy in ADAM7:
        if x0 >= width or y0 >= height:
            continue
        if depth < 8:
            across = len(range(x0, width, dx))
            values = [samples[y * width + x] for y in range(y0, height, dy) for x in range(x0, width, dx)]
            rows = split(pack_bits(values, across, depth), (across * depth + 7) // 8)
            raw += filtered(rows, 1, kinds)
            continue
        step = CHANNELS[color] * depth // 8
        rows = [b"".join(samples[(y * width + x) * step:(y * width + x + 1) * step]
                         for x in range(x0, width, dx)) for y in range(y0, height, dy)]
        raw += filtered(rows, step, kinds)
    parts = [ihdr(width, height, depth, color, interlace=1)]
    if palette is not None:
        parts.append(chunk(b"PLTE", palette))
    if trns is not None:
        parts.append(chunk(b"tRNS", trns))
    return assemble(*parts, chunk(b"IDAT", zlib.compress(bytes(raw))), chunk(b"IEND"))


def pack_bits(values, width, depth):
    """Sample values of 1, 2 or 4 bits as packed rows, most significant first."""
    out = bytearray()
    for start in range(0, len(values), width):
        bits = "".join(format(value, f"0{depth}b") for value in values[start:start + width])
        bits += "0" * (-len(bits) % 8)
        out += int(bits, 2).to_bytes(len(bits) // 8, "big")
    return bytes(out)


def noise(count, seed):
    return random.Random(seed).randbytes(count)


def smooth(width, height, step, seed=0):
    """Slow ramps: neighbours are often equal, which the fast branches of a decoder like."""
    return bytes(((x // 3) * 2 + (y // 2) * 5 + channel * 40 + seed) & 255
                 for y in range(height) for x in range(width) for channel in range(step))


def sparse(width, height, step, seed=0):
    """Mostly zero, with a few marks: whole blank rows, and blank rows under marked ones."""
    rng = random.Random(seed)
    out = bytearray(width * height * step)
    for y in range(height):
        if y % 4 == 1:
            for _ in range(max(1, width // 5)):
                out[(y * width + rng.randrange(width)) * step + rng.randrange(step)] = rng.randrange(1, 256)
    return bytes(out)


def pictures(width, height, step, seed=0):
    return (noise(width * height * step, seed), smooth(width, height, step, seed), sparse(width, height, step, seed))


class PngCase(unittest.TestCase):
    """Every test decodes with the standard library, whatever is installed."""

    USE_PIL = False

    def setUp(self):
        super().setUp()
        patcher = mock.patch.object(png_io, "HAVE_PIL", self.USE_PIL)
        patcher.start()
        self.addCleanup(patcher.stop)

    def refused(self, data, code, kind=png_io.PngError, **options):
        with self.assertRaises(kind) as caught:
            png_io.read_png(data, **options)
        self.assertEqual(caught.exception.code, code, str(caught.exception))
        return caught.exception


# ── reading ──────────────────────────────────────────────────────────────────

class ReadEightBit(PngCase):
    def test_what_the_fixtures_write_is_read_the_same(self):
        for mode in ("L", "LA", "RGB", "RGBA"):
            samples = png_io.MODES[mode]
            painter = (lambda x, y: (x * 7 + y * 13) % 256) if samples == 1 else (
                lambda x, y, n=samples: tuple((x * 7 + y * 13 + c * 50) % 256 for c in range(n)))
            for compress in (False, True):
                data = fixtures.make_png(9, 7, mode, painter, compress=compress)
                image = png_io.read_png(data)
                oracle = fixtures.read_png(data)
                self.assertEqual((image.width, image.height, image.mode), (9, 7, mode))
                self.assertEqual(image.pixels, oracle["pixels"], mode)
                self.assertEqual(list(image.chunks), oracle["chunks"], mode)
                self.assertIsInstance(image.pixels, bytes)

    def test_every_filter_in_every_mode(self):
        for color in (0, 4, 2, 6):
            step = CHANNELS[color]
            for width, height in ((1, 1), (1, 6), (7, 1), (2, 5), (13, 11), (40, 23)):
                for number, samples in enumerate(pictures(width, height, step, seed=color + width)):
                    for kinds in FILTER_CHOICES:
                        data = encode(width, height, color, 8, samples, kinds=kinds)
                        image = png_io.read_png(data)
                        self.assertEqual(image.pixels, samples,
                                         f"colour {color} {width}x{height} picture {number} filters {kinds}")
                        self.assertEqual(image.mode, MODE_OF[color])

    def test_a_long_row_of_every_filter(self):
        # Wide enough that a running sum passes any small counter.
        width = 5000
        for samples in (b"\xff" * (width * 3), noise(width * 3, 3)):
            for kinds in ((1,), (3,), (4,), (2,), (1, 2, 3, 4)):
                self.assertEqual(png_io.read_png(encode(width, 3, 0, 8, samples, kinds=kinds)).pixels, samples, kinds)

    def test_the_image_data_may_be_cut_into_any_number_of_idat_chunks(self):
        samples = noise(31 * 17 * 4, 5)
        whole = png_io.read_png(encode(31, 17, 6, 8, samples, kinds=(4, 1)))
        for pieces in (2, 3, 50):
            data = encode(31, 17, 6, 8, samples, kinds=(4, 1), pieces=pieces)
            image = png_io.read_png(data)
            self.assertEqual(image.pixels, samples)
            self.assertEqual(image.chunks, whole.chunks, "a run of IDAT is named once")
            self.assertGreaterEqual(png_io.png_info(data)["idat_chunks"], 2)

    def test_stored_and_compressed_data_are_the_same_image(self):
        samples = smooth(20, 10, 2)
        self.assertEqual(png_io.read_png(encode(20, 10, 4, 8, samples, level=0)).pixels, samples)
        self.assertEqual(png_io.read_png(encode(20, 10, 4, 8, samples, level=9)).pixels, samples)

    def test_bytes_bytearray_and_memoryview_are_all_read(self):
        data = encode(5, 4, 2, 8, noise(60, 1), kinds=(3,))
        expected = png_io.read_png(data)
        self.assertEqual(png_io.read_png(bytearray(data)), expected)
        self.assertEqual(png_io.read_png(memoryview(data)), expected)

    def test_unknown_ancillary_chunks_are_named_and_not_applied(self):
        samples = noise(6 * 6, 2)
        extras = [(b"gAMA", struct.pack(">I", 45455)), (b"iCCP", b"name\x00\x00" + zlib.compress(b"profile")),
                  (b"quUX", b"anything")]
        image = png_io.read_png(encode(6, 6, 0, 8, samples, before=extras))
        self.assertEqual(image.pixels, samples, "gamma and a colour profile leave the samples alone")
        self.assertEqual(image.chunks, ("IHDR", "gAMA", "iCCP", "quUX", "IDAT", "IEND"))

    def test_bytes_after_iend_are_ignored_and_counted(self):
        data = encode(3, 3, 0, 8, noise(9, 4))
        self.assertEqual(png_io.read_png(data + b"left over").pixels, png_io.read_png(data).pixels)
        self.assertEqual(png_io.png_info(data + b"left over")["trailing_bytes"], 9)
        self.assertEqual(png_io.png_info(data)["trailing_bytes"], 0)

    def test_a_stream_without_its_final_checksum_is_still_the_image(self):
        samples = noise(8 * 8, 6)
        packed = zlib.compress(filtered(split(samples, 8), 1, (0,)))
        data = assemble(ihdr(8, 8, 8, 0), chunk(b"IDAT", packed[:-4]), chunk(b"IEND"))
        self.assertEqual(png_io.read_png(data).pixels, samples)


class ReadOtherDepths(PngCase):
    def test_sixteen_bits_keep_the_high_byte(self):
        for color in (0, 4, 2, 6):
            step = CHANNELS[color] * 2
            samples = noise(9 * 5 * step, color)
            for kinds in FILTER_CHOICES[:6]:
                image = png_io.read_png(encode(9, 5, color, 16, samples, kinds=kinds))
                self.assertEqual(image.mode, MODE_OF[color])
                self.assertEqual(image.pixels, samples[0::2], f"colour {color} filters {kinds}")

    def test_grey_of_one_two_and_four_bits_is_scaled_to_the_whole_range(self):
        for depth, scale in ((1, 255), (2, 85), (4, 17)):
            for width, height in ((1, 1), (3, 2), (8, 3), (13, 5)):
                rng = random.Random(depth * 100 + width)
                values = [rng.randrange(1 << depth) for _ in range(width * height)]
                for kinds in ((0,), (1, 2, 3, 4)):
                    image = png_io.read_png(encode(width, height, 0, depth, pack_bits(values, width, depth),
                                                   kinds=kinds))
                    self.assertEqual(image.mode, "L")
                    self.assertEqual(list(image.pixels), [value * scale for value in values],
                                     f"{depth} bits, {width}x{height}")

    def test_a_palette_image_is_rgb(self):
        palette = bytes(range(10, 10 + 3 * 16))
        for depth in (1, 2, 4, 8):
            entries = min(16, 1 << depth)
            rng = random.Random(depth)
            indexes = [rng.randrange(entries) for _ in range(11 * 4)]
            samples = bytes(indexes) if depth == 8 else pack_bits(indexes, 11, depth)
            image = png_io.read_png(encode(11, 4, 3, depth, samples, kinds=(0, 1, 2, 3, 4),
                                           palette=palette[:entries * 3]))
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.pixels, b"".join(palette[i * 3:i * 3 + 3] for i in indexes), depth)

    def test_a_palette_with_trns_is_rgba_and_short_trns_means_opaque(self):
        palette = bytes(range(30, 30 + 3 * 4))
        indexes = [0, 1, 2, 3, 3, 2, 1, 0]
        image = png_io.read_png(encode(4, 2, 3, 2, pack_bits(indexes, 4, 2), palette=palette, trns=b"\x00\x80"))
        alpha = [0, 128, 255, 255]
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.pixels, b"".join(palette[i * 3:i * 3 + 3] + bytes([alpha[i]]) for i in indexes))

    def test_one_transparent_grey(self):
        samples = bytes([0, 7, 200, 7, 255, 8])
        image = png_io.read_png(encode(3, 2, 0, 8, samples, trns=b"\x00\x07"))
        self.assertEqual(image.mode, "LA")
        self.assertEqual(image.pixels, b"".join(bytes([v, 0 if v == 7 else 255]) for v in samples))
        # A key no 8-bit sample can equal makes nothing transparent.
        image = png_io.read_png(encode(3, 2, 0, 8, samples, trns=b"\x01\x07"))
        self.assertEqual(image.pixels[1::2], b"\xff" * 6)

    def test_one_transparent_grey_below_eight_bits_is_matched_before_scaling(self):
        values = [0, 5, 15, 5, 9, 1]
        image = png_io.read_png(encode(3, 2, 0, 4, pack_bits(values, 3, 4), trns=b"\x00\x05"))
        self.assertEqual(image.mode, "LA")
        self.assertEqual(image.pixels, b"".join(bytes([v * 17, 0 if v == 5 else 255]) for v in values))

    def test_one_transparent_grey_at_sixteen_bits_needs_both_bytes(self):
        samples = b"\x12\x34" + b"\x12\x35" + b"\x13\x34" + b"\x12\x34"
        image = png_io.read_png(encode(4, 1, 0, 16, samples, trns=b"\x12\x34"))
        self.assertEqual(image.pixels, bytes([0x12, 0, 0x12, 255, 0x13, 255, 0x12, 0]))

    def test_one_transparent_colour(self):
        key = bytes([10, 20, 30])
        pixels = [key, bytes([10, 20, 31]), bytes([11, 20, 30]), key, bytes([0, 0, 0]), bytes([10, 21, 30])]
        image = png_io.read_png(encode(3, 2, 2, 8, b"".join(pixels), kinds=(4,), trns=b"\x00\x0a\x00\x14\x00\x1e"))
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.pixels, b"".join(p + (b"\x00" if p == key else b"\xff") for p in pixels))

    def test_one_transparent_colour_at_sixteen_bits(self):
        key = bytes([1, 2, 3, 4, 5, 6])
        near = bytes([1, 2, 3, 4, 5, 7])           # the same high bytes, another low byte
        image = png_io.read_png(encode(2, 1, 2, 16, key + near, trns=key))
        self.assertEqual(image.pixels, bytes([1, 3, 5, 0, 1, 3, 5, 255]))

    def test_trns_beside_a_real_alpha_channel_is_ignored(self):
        samples = noise(4 * 3 * 4, 9)
        image = png_io.read_png(encode(4, 3, 6, 8, samples, trns=b"\x00\x01\x00\x02\x00\x03"))
        self.assertEqual((image.mode, image.pixels), ("RGBA", samples))
        image = png_io.read_png(encode(4, 3, 4, 8, samples[:24], trns=b"\x00\x01"))
        self.assertEqual((image.mode, image.pixels), ("LA", samples[:24]))


ADAM7_SIZES = ((1, 1), (1, 9), (9, 1), (2, 2), (3, 2), (5, 5), (8, 8), (9, 9), (20, 13), (33, 17))


class Interlaced(PngCase):
    """Adam7 is undone by the standard library too, so no result depends on PIL."""

    def test_every_eight_bit_mode_at_sizes_that_leave_passes_empty(self):
        for color in (0, 4, 2, 6):
            step = CHANNELS[color]
            for width, height in ADAM7_SIZES:
                for number, samples in enumerate(pictures(width, height, step, seed=color + width)):
                    for kinds in ((0,), (1, 2, 3, 4), (4,), (3, 1)):
                        image_read = png_io.read_png(encode_interlaced(width, height, color, 8, samples,
                                                                       kinds=kinds))
                        self.assertEqual((image_read.mode, image_read.pixels), (MODE_OF[color], samples),
                                         f"colour {color} {width}x{height} picture {number} filters {kinds}")

    def test_an_interlaced_image_is_its_plain_twin(self):
        samples = noise(20 * 13 * 4, 3)
        plain = png_io.read_png(encode(20, 13, 6, 8, samples, kinds=(4, 1)))
        laced = png_io.read_png(encode_interlaced(20, 13, 6, 8, samples, kinds=(2, 3)))
        self.assertEqual(laced._replace(chunks=()), plain._replace(chunks=()))
        self.assertEqual(laced.chunks, ("IHDR", "IDAT", "IEND"))

    def test_sixteen_bits_interlaced_keep_the_high_byte(self):
        for color in (0, 4, 2, 6):
            step = CHANNELS[color] * 2
            for width, height in ((1, 1), (5, 5), (9, 9), (13, 6)):
                samples = noise(width * height * step, color + width)
                image_read = png_io.read_png(encode_interlaced(width, height, color, 16, samples, kinds=(1, 4)))
                self.assertEqual(image_read.pixels, samples[0::2], f"colour {color} {width}x{height}")

    def test_grey_below_eight_bits_interlaced(self):
        for depth, scale in ((1, 255), (2, 85), (4, 17)):
            for width, height in ADAM7_SIZES:
                rng = random.Random(depth * 31 + width * 7 + height)
                values = [rng.randrange(1 << depth) for _ in range(width * height)]
                for kinds in ((0,), (1, 2, 3, 4)):
                    image_read = png_io.read_png(encode_interlaced(width, height, 0, depth, values, kinds=kinds))
                    self.assertEqual((image_read.mode, list(image_read.pixels)),
                                     ("L", [value * scale for value in values]),
                                     f"{depth} bits, {width}x{height}, filters {kinds}")

    def test_a_palette_interlaced_with_and_without_trns(self):
        palette = bytes(range(40, 40 + 3 * 16))
        for depth in (1, 2, 4, 8):
            entries = min(16, 1 << depth)
            for width, height in ((1, 1), (7, 3), (9, 9), (17, 10)):
                rng = random.Random(depth + width)
                indexes = [rng.randrange(entries) for _ in range(width * height)]
                samples = bytes(indexes) if depth == 8 else indexes
                colours = b"".join(palette[i * 3:i * 3 + 3] for i in indexes)
                data = encode_interlaced(width, height, 3, depth, samples, kinds=(0, 2, 4),
                                         palette=palette[:entries * 3])
                self.assertEqual((png_io.read_png(data).mode, png_io.read_png(data).pixels), ("RGB", colours),
                                 f"{depth} bits {width}x{height}")
                alpha = bytes([0, 99]) + b"\xff" * (entries - 2)
                data = encode_interlaced(width, height, 3, depth, samples, palette=palette[:entries * 3],
                                         trns=alpha[:2])
                expected = b"".join(palette[i * 3:i * 3 + 3] + alpha[i:i + 1] for i in indexes)
                self.assertEqual(png_io.read_png(data).pixels, expected, f"{depth} bits {width}x{height} tRNS")

    def test_one_transparent_grey_and_colour_interlaced(self):
        grey = bytes([7, 1, 7, 7, 200, 7, 3, 7, 7] * 3)
        image_read = png_io.read_png(encode_interlaced(9, 3, 0, 8, grey, trns=b"\x00\x07"))
        self.assertEqual(image_read.pixels, b"".join(bytes([v, 0 if v == 7 else 255]) for v in grey))
        key = bytes([10, 20, 30])
        pixels = [key if (index * 5) % 3 == 0 else bytes([index, 20, 30]) for index in range(9 * 5)]
        image_read = png_io.read_png(encode_interlaced(9, 5, 2, 8, b"".join(pixels), kinds=(4,),
                                                       trns=b"\x00\x0a\x00\x14\x00\x1e"))
        self.assertEqual(image_read.pixels, b"".join(p + (b"\x00" if p == key else b"\xff") for p in pixels))

    def test_png_info_names_it(self):
        info = png_io.png_info(encode_interlaced(9, 9, 0, 8, noise(81, 1)))
        self.assertEqual((info["interlace"], info["width"], info["height"], info["mode"]), (1, 9, 9, "L"))

    def test_a_broken_interlaced_image_is_an_error(self):
        data = encode_interlaced(9, 9, 0, 8, noise(81, 1))
        cut = assemble(ihdr(9, 9, 8, 0, interlace=1), chunk(b"IDAT", zlib.compress(b"\x00" * 20)), chunk(b"IEND"))
        self.refused(cut, "image_data_short")
        # The seven passes of a 9x9 grey image: (pixels across, rows) per pass, each row behind a filter byte.
        passes = [(2, 2), (1, 2), (3, 1), (2, 3), (5, 2), (4, 5), (9, 4)]
        whole = sum(down * (across + 1) for across, down in passes)
        self.assertEqual((whole, sum(across * down for across, down in passes)), (100, 81))

        def laced(raw):
            return assemble(ihdr(9, 9, 8, 0, interlace=1), chunk(b"IDAT", zlib.compress(bytes(raw))), chunk(b"IEND"))
        self.assertEqual(png_io.read_png(laced(bytes(whole))).pixels, bytes(81))
        self.refused(laced(bytes(whole + 1)), "image_data_long")
        self.refused(laced(bytes(whole - 1)), "image_data_short")
        self.refused(data[:-20], "truncated")
        # A bad filter byte on the last row of the last pass only.
        raw = bytearray(whole)
        raw[whole - 10] = 6
        self.refused(laced(raw), "bad_filter")

    def test_hostile_interlaced_bytes_raise_only_png_errors(self):
        data = encode_interlaced(9, 7, 6, 8, noise(9 * 7 * 4, 4), kinds=(0, 1, 2, 3, 4))
        for position in range(len(SIGNATURE), len(data)):
            changed = bytearray(data)
            changed[position] ^= 0x5A
            try:
                png_io.read_png(bytes(changed))
            except png_io.PngError:
                pass


# ── what a stranger's file may hold ──────────────────────────────────────────

class Hostile(PngCase):
    def small(self):
        return encode(5, 4, 6, 8, noise(80, 11), kinds=(0, 1, 2, 3, 4), before=[(b"tEXt", b"k\x00v")])

    def test_every_truncation_is_a_png_error(self):
        data = self.small()
        for length in range(len(data)):
            with self.assertRaises(png_io.PngError, msg=f"cut to {length} bytes"):
                png_io.read_png(data[:length])
            with self.assertRaises(png_io.PngError, msg=f"cut to {length} bytes"):
                png_io.png_info(data[:length])

    def test_every_changed_byte_is_a_png_error(self):
        data = self.small()
        for position in range(len(data)):
            for flip in (0x01, 0xFF):
                changed = bytearray(data)
                changed[position] ^= flip
                with self.assertRaises(png_io.PngError, msg=f"byte {position} ^ {flip:#x}"):
                    png_io.read_png(bytes(changed))

    def test_random_bytes_behind_a_signature_never_raise_anything_else(self):
        rng = random.Random(8)
        for _ in range(300):
            data = SIGNATURE + rng.randbytes(rng.randrange(0, 80))
            for reader in (png_io.read_png, png_io.png_info):
                with self.assertRaises(png_io.PngError):
                    reader(data)

    def test_well_formed_chunks_in_any_order_never_raise_anything_else(self):
        rng = random.Random(12)
        good = zlib.compress(filtered(split(noise(12, 1), 4), 1, (0,)))
        stock = [ihdr(4, 3, 8, 0), ihdr(4, 3, 8, 3), ihdr(4, 3, 2, 3), chunk(b"PLTE", bytes(12)),
                 chunk(b"tRNS", b"\x00\x01"), chunk(b"IDAT", good), chunk(b"IDAT", good[:5]),
                 chunk(b"IDAT", b""), chunk(b"IEND"), chunk(b"bKGD", b"\x00"), chunk(b"ZZZZ", b"")]
        for _ in range(600):
            data = assemble(*(rng.choice(stock) for _ in range(rng.randrange(1, 7))), chunk(b"IEND"))
            try:
                png_io.read_png(data)
            except png_io.PngError:
                pass
        # Not every such file is refused: this one is a sound image.
        sound = assemble(stock[0], stock[9], stock[4], stock[5], stock[8])
        self.assertEqual(png_io.read_png(sound).mode, "LA")

    def test_what_is_not_a_png(self):
        for data in (b"", b"GIF89a", SIGNATURE[:7], b"\x89PNG\r\n\x1a\r" + bytes(40)):
            self.refused(data, "not_png")
        for data in ("text", None, 7, ["x"]):
            self.refused(data, "not_png")

    def test_a_bad_crc_is_named(self):
        data = bytearray(self.small())
        data[-1] ^= 0x10                              # the CRC of IEND
        self.refused(bytes(data), "crc")

    def test_a_chunk_type_must_be_four_letters(self):
        data = assemble(ihdr(1, 1, 8, 0), chunk(b"ab1d", b""), chunk(b"IDAT", zlib.compress(b"\x00\x00")),
                        chunk(b"IEND"))
        self.refused(data, "bad_chunk")

    def test_headers_that_describe_no_image(self):
        body = chunk(b"IDAT", zlib.compress(bytes(64))) + chunk(b"IEND")
        bad = {
            "no width": ihdr(0, 4, 8, 0), "no height": ihdr(4, 0, 8, 0),
            "a width past 2^31": ihdr(0x80000000, 1, 8, 0),
            "colour type 5": ihdr(4, 4, 8, 5), "colour type 1": ihdr(4, 4, 8, 1),
            "3 bits": ihdr(4, 4, 3, 0), "RGB at 4 bits": ihdr(4, 4, 4, 2), "palette at 16 bits": ihdr(4, 4, 16, 3),
            "grey+alpha at 4 bits": ihdr(4, 4, 4, 4), "compression 1": ihdr(4, 4, 8, 0, compression=1),
            "filter method 1": ihdr(4, 4, 8, 0, method=1), "interlace 2": ihdr(4, 4, 8, 0, interlace=2),
        }
        for what, header in bad.items():
            with self.subTest(what):
                self.refused(SIGNATURE + header + body, "bad_header")
                with self.assertRaises(png_io.PngError):
                    png_io.png_info(SIGNATURE + header + body)
        first = assemble(chunk(b"gAMA", struct.pack(">I", 1)), ihdr(4, 4, 8, 0)) + body
        self.refused(first, "bad_header")
        self.refused(assemble(chunk(b"IHDR", bytes(12))) + body, "bad_header")

    def test_the_pixel_cap_is_applied_from_the_header_alone(self):
        tiny = chunk(b"IDAT", zlib.compress(b"\x00")) + chunk(b"IEND")
        with mock.patch.object(png_io.zlib, "decompressobj", side_effect=AssertionError("nothing may be inflated")):
            for width, height in ((8193, 8192), (8192, 8193), (0x7FFFFFFF, 0x7FFFFFFF), (1, 8192 * 8192 + 1)):
                error = self.refused(SIGNATURE + ihdr(width, height, 8, 0) + tiny, "png_pixels",
                                     png_io.PngLimitExceeded)
                self.assertIsInstance(error, png_io.PngError)
        self.assertEqual(png_io.MAX_PIXELS, 8192 * 8192)

    def test_the_pixel_cap_can_be_lowered(self):
        data = encode(4, 4, 0, 8, noise(16, 1))
        self.assertEqual(png_io.read_png(data, max_pixels=16).width, 4)
        self.refused(data, "png_pixels", png_io.PngLimitExceeded, max_pixels=15)
        info = png_io.png_info(SIGNATURE + ihdr(60000, 60000, 8, 0) + chunk(b"IEND"))
        self.assertEqual((info["width"], info["height"]), (60000, 60000), "png_info reports what it will not read")

    def test_image_data_is_never_inflated_past_what_the_header_gives(self):
        asked = []
        real = zlib.decompressobj

        class Watched:
            def __init__(self):
                self.inner = real()

            def decompress(self, data, max_length=0):
                asked.append(max_length)
                return self.inner.decompress(data, max_length)

        bomb = assemble(ihdr(2, 2, 8, 0), chunk(b"IDAT", zlib.compress(bytes(16 << 20), 9)), chunk(b"IEND"))
        self.assertLess(len(bomb), 20_000)
        with mock.patch.object(png_io.zlib, "decompressobj", Watched):
            self.refused(bomb, "image_data_long")
        self.assertEqual(asked, [2 * (2 + 1) + 1], "one byte more than the image, to see that there is more")

    def test_image_data_of_the_wrong_length_or_kind(self):
        def with_data(packed, color=0, depth=8):
            return assemble(ihdr(4, 4, depth, color), chunk(b"IDAT", packed), chunk(b"IEND"))
        self.refused(with_data(zlib.compress(bytes(19))), "image_data_short")
        self.refused(with_data(zlib.compress(bytes(21))), "image_data_long")
        self.refused(with_data(b""), "image_data_short")
        self.refused(with_data(b"not zlib at all"), "bad_image_data")
        self.refused(with_data(zlib.compress(noise(20, 1), 0)[:15]), "image_data_short")
        self.assertEqual(png_io.read_png(with_data(zlib.compress(bytes(20)))).pixels, bytes(16))

    def test_a_filter_type_above_four(self):
        raw = bytearray(bytes(20))
        raw[10] = 5
        self.refused(assemble(ihdr(4, 4, 8, 0), chunk(b"IDAT", zlib.compress(bytes(raw))), chunk(b"IEND")),
                     "bad_filter")

    def test_chunk_order(self):
        data = zlib.compress(bytes(20))
        idat, end = chunk(b"IDAT", data), chunk(b"IEND")
        head = ihdr(4, 4, 8, 0)
        self.refused(assemble(head, end), "no_image_data")
        self.refused(assemble(head, idat), "truncated")                      # no IEND
        self.refused(assemble(head, chunk(b"IDAT", data[:6]), chunk(b"tEXt", b"a\x00b"),
                              chunk(b"IDAT", data[6:]), end), "chunk_order")
        self.refused(assemble(head, head, idat, end), "chunk_order")
        self.refused(assemble(head, idat, chunk(b"PLTE", bytes(3)), end), "chunk_order")
        self.refused(assemble(head, chunk(b"PLTE", bytes(3)), chunk(b"PLTE", bytes(3)), idat, end), "chunk_order")
        self.refused(assemble(head, idat, chunk(b"tRNS", b"\x00\x00"), end), "chunk_order")
        self.refused(assemble(head, chunk(b"tRNS", b"\x00\x00"), chunk(b"tRNS", b"\x00\x00"), idat, end),
                     "chunk_order")

    def test_palette_rules(self):
        idat, end = chunk(b"IDAT", zlib.compress(bytes(20))), chunk(b"IEND")
        head = ihdr(4, 4, 8, 3)
        self.refused(assemble(head, idat, end), "bad_palette")
        for size in (0, 4, 771):
            self.refused(assemble(head, chunk(b"PLTE", bytes(size)), idat, end), "bad_palette")
        self.refused(assemble(head, chunk(b"tRNS", b"\x00"), chunk(b"PLTE", bytes(6)), idat, end), "chunk_order")
        self.refused(assemble(head, chunk(b"PLTE", bytes(6)), chunk(b"tRNS", bytes(3)), idat, end), "bad_trns")
        beyond = zlib.compress(b"\x00\x00\x00\x00\x02" + bytes(15))
        self.refused(assemble(head, chunk(b"PLTE", bytes(6)), chunk(b"IDAT", beyond), end), "bad_palette")
        self.assertEqual(png_io.read_png(assemble(head, chunk(b"PLTE", bytes(6)), idat, end)).mode, "RGB")
        # A palette offered to an RGB image is only a suggestion.
        rgb = assemble(ihdr(1, 1, 8, 2), chunk(b"PLTE", bytes(6)), chunk(b"IDAT", zlib.compress(bytes(4))), end)
        self.assertEqual(png_io.read_png(rgb).pixels, bytes(3))

    def test_trns_of_the_wrong_size(self):
        idat, end = chunk(b"IDAT", zlib.compress(bytes(20))), chunk(b"IEND")
        self.refused(assemble(ihdr(4, 4, 8, 0), chunk(b"tRNS", bytes(3)), idat, end), "bad_trns")
        rgb = chunk(b"IDAT", zlib.compress(bytes(4 * 13)))
        self.refused(assemble(ihdr(4, 4, 8, 2), chunk(b"tRNS", bytes(2)), rgb, end), "bad_trns")

    def test_an_unknown_critical_chunk_is_unsupported(self):
        idat, end = chunk(b"IDAT", zlib.compress(bytes(20))), chunk(b"IEND")
        self.refused(assemble(ihdr(4, 4, 8, 0), chunk(b"QUUX", b"?"), idat, end), "critical_chunk",
                     png_io.PngUnsupported)

    def test_too_many_chunks(self):
        many = [chunk(b"tEXt", b"a\x00b")] * 12
        data = assemble(ihdr(1, 1, 8, 0), *many, chunk(b"IDAT", zlib.compress(b"\x00\x00")), chunk(b"IEND"))
        self.assertEqual(png_io.read_png(data).pixels, b"\x00")
        with mock.patch.object(png_io, "MAX_CHUNKS", 10):
            self.refused(data, "too_many_chunks")
            with self.assertRaises(png_io.PngError):
                png_io.png_info(data)
        self.assertGreaterEqual(png_io.MAX_CHUNKS, 10_000)

    def test_a_large_blank_image_is_read_quickly(self):
        # 4 MiB of nothing behind a few hundred bytes: every filter type over blank rows.
        side = 2048
        raw = b"".join(bytes([kind]) + bytes(side) for kind in (0, 1, 2, 3, 4)) * (side // 5 + 1)
        raw = raw[:side * (side + 1)]
        data = assemble(ihdr(side, side, 8, 0), chunk(b"IDAT", zlib.compress(raw, 9)), chunk(b"IEND"))
        image = png_io.read_png(data)
        self.assertEqual(image.pixels.count(0), side * side)


class Errors(unittest.TestCase):
    def test_the_error_classes_are_the_codecs_own(self):
        self.assertIs(png_io.CodecError, bplist.CodecError)
        self.assertIs(png_io.PngError, bplist.PngError)
        self.assertIs(png_io.PngUnsupported, bplist.PngUnsupported)
        self.assertTrue(issubclass(png_io.PngError, png_io.CodecError))
        self.assertTrue(issubclass(png_io.PngUnsupported, png_io.PngError))
        error = png_io.PngError("crc", "the IDAT chunk fails its CRC")
        self.assertEqual((error.code, error.detail), ("crc", "the IDAT chunk fails its CRC"))
        self.assertEqual(str(error), "crc: the IDAT chunk fails its CRC")

    def test_the_pixel_cap_is_a_png_error_and_a_limit_exceeded(self):
        self.assertTrue(issubclass(png_io.PngLimitExceeded, png_io.PngError))
        self.assertTrue(issubclass(png_io.PngLimitExceeded, bplist.LimitExceeded))
        self.assertFalse(issubclass(png_io.PngLimitExceeded, png_io.PngUnsupported))
        data = SIGNATURE + ihdr(9000, 9000, 8, 0) + chunk(b"IDAT", b"") + chunk(b"IEND")
        for expected in (png_io.PngError, bplist.LimitExceeded, bplist.CodecError, ValueError):
            with self.assertRaises(expected) as caught:
                png_io.read_png(data)
            self.assertEqual(caught.exception.code, "png_pixels", "the cap's name in spec.yaml")
            self.assertIn("9000x9000", caught.exception.detail)


# ── png_info ─────────────────────────────────────────────────────────────────

class Info(PngCase):
    def test_the_header_and_the_chunk_list(self):
        data = encode(31, 17, 6, 8, noise(31 * 17 * 4, 5), pieces=4,
                      before=[(b"sRGB", b"\x00"), (b"pHYs", struct.pack(">IIB", 2835, 2835, 1))])
        info = png_io.png_info(data)
        self.assertEqual({key: info[key] for key in ("width", "height", "bit_depth", "color_type", "interlace")},
                         {"width": 31, "height": 17, "bit_depth": 8, "color_type": 6, "interlace": 0})
        self.assertEqual(info["mode"], "RGBA")
        self.assertIs(info["has_alpha"], True)
        self.assertEqual(info["chunks"], ["IHDR", "sRGB", "pHYs", "IDAT", "IEND"])
        self.assertEqual(info["idat_chunks"], 4)
        self.assertEqual(info["idat_bytes"], sum(len(body) for _, body in png_io.get_chunks(data, "IDAT")))
        self.assertEqual(sorted(info), sorted(["width", "height", "bit_depth", "color_type", "interlace", "mode",
                                               "has_alpha", "chunks", "idat_chunks", "idat_bytes",
                                               "trailing_bytes"]))

    def test_the_mode_is_the_one_read_png_returns(self):
        palette = bytes(12)
        cases = [
            (encode(2, 2, 0, 8, bytes(4)), "L"), (encode(2, 2, 0, 8, bytes(4), trns=b"\x00\x09"), "LA"),
            (encode(2, 2, 4, 8, bytes(8)), "LA"), (encode(2, 2, 2, 8, bytes(12)), "RGB"),
            (encode(2, 2, 2, 8, bytes(12), trns=bytes(6)), "RGBA"), (encode(2, 2, 6, 8, bytes(16)), "RGBA"),
            (encode(2, 2, 3, 8, bytes(4), palette=palette), "RGB"),
            (encode(2, 2, 3, 8, bytes(4), palette=palette, trns=b"\x00"), "RGBA"),
            (encode(2, 2, 0, 16, bytes(8)), "L"), (encode(2, 2, 6, 16, bytes(32)), "RGBA"),
        ]
        for data, mode in cases:
            info = png_io.png_info(data)
            self.assertEqual(info["mode"], mode)
            self.assertEqual(png_io.read_png(data).mode, mode)
            self.assertEqual(info["has_alpha"], mode in ("LA", "RGBA"))

    def test_nothing_is_inflated(self):
        data = assemble(ihdr(4, 4, 8, 0), chunk(b"IDAT", b"this is not a zlib stream"), chunk(b"IEND"))
        with mock.patch.object(png_io.zlib, "decompressobj", side_effect=AssertionError("png_info inflates nothing")):
            self.assertEqual(png_io.png_info(data)["width"], 4)

    def test_get_chunks_returns_bodies_in_file_order(self):
        data = encode(2, 2, 0, 8, bytes(4), before=[(b"tEXt", b"a\x00one"), (b"gAMA", b"\x00\x00\xb1\x8f"),
                                                     (b"tEXt", b"b\x00two")])
        self.assertEqual(png_io.get_chunks(data, "tEXt"), [("tEXt", b"a\x00one"), ("tEXt", b"b\x00two")])
        self.assertEqual(png_io.get_chunks(data, "gAMA", "tEXt")[1], ("gAMA", b"\x00\x00\xb1\x8f"))
        self.assertEqual(png_io.get_chunks(data, "iCCP"), [])
        with self.assertRaises(png_io.PngError):
            png_io.get_chunks(data[:-3], "tEXt")


# ── writing ──────────────────────────────────────────────────────────────────

def inflate(data):
    """(header fields, raw filtered rows) of a PNG, read here."""
    position, header, packed = len(SIGNATURE), None, b""
    while position < len(data):
        length, kind = struct.unpack(">I4s", data[position:position + 8])
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", data[position + 8:position + 21])
        elif kind == b"IDAT":
            packed += data[position + 8:position + 8 + length]
        position += 12 + length
    return header, zlib.decompress(packed)


class Write(PngCase):
    def test_what_is_written_is_read_by_the_fixture_reader(self):
        for mode, color in (("L", 0), ("LA", 4), ("RGB", 2), ("RGBA", 6)):
            pixels = noise(13 * 7 * png_io.MODES[mode], color)
            data = png_io.write_png(13, 7, mode, pixels)
            oracle = fixtures.read_png(data)          # 8-bit, filter 0, not interlaced, every CRC right, or it raises
            self.assertEqual((oracle["width"], oracle["height"], oracle["mode"]), (13, 7, mode))
            self.assertEqual(oracle["pixels"], pixels)
            self.assertEqual(oracle["chunks"], ["IHDR", "IDAT", "IEND"])
            header, raw = inflate(data)
            self.assertEqual(header, (13, 7, 8, color, 0, 0, 0))
            self.assertEqual(set(raw[0::13 * png_io.MODES[mode] + 1]), {0}, "filter 0 on every row")
            self.assertEqual(png_io.read_png(data), png_io.Image(13, 7, mode, pixels, ("IHDR", "IDAT", "IEND")))

    def test_a_shape_is_grey_with_three_chunks_at_level_six(self):
        pixels = smooth(64, 64, 1)
        data = png_io.write_png(64, 64, "L", pixels)
        info = png_io.png_info(data)
        self.assertEqual((info["color_type"], info["bit_depth"], info["interlace"]), (0, 8, 0))
        self.assertEqual(info["chunks"], ["IHDR", "IDAT", "IEND"])
        self.assertEqual(info["idat_chunks"], 1)
        self.assertEqual(data, png_io.write_png(64, 64, "L", pixels, level=6), "6 is the default level")

    def test_the_level_changes_the_size_and_never_the_pixels(self):
        pixels = smooth(80, 60, 3)
        sizes = {}
        for level in (0, 1, 6, 9):
            data = png_io.write_png(80, 60, "RGB", pixels, level=level)
            self.assertEqual(png_io.read_png(data).pixels, pixels)
            sizes[level] = len(data)
        self.assertGreater(sizes[0], sizes[9])

    def test_a_supplied_iccp_chunk_is_carried_over(self):
        profile = b"kCGColorSpaceGenericGrayGamma2_2\x00\x00" + zlib.compress(b"an ICC profile would be here")
        source = fixtures.make_png(6, 6, "L", extra_chunks=[(b"iCCP", profile)])
        carried = png_io.get_chunks(source, "iCCP")
        self.assertEqual(carried, [("iCCP", profile)])
        pixels = noise(36, 2)
        data = png_io.write_png(6, 6, "L", pixels, chunks=carried)
        self.assertEqual(png_io.png_info(data)["chunks"], ["IHDR", "iCCP", "IDAT", "IEND"])
        self.assertEqual(png_io.get_chunks(data, "iCCP"), carried)
        self.assertEqual(fixtures.read_png(data)["pixels"], pixels)

    def test_supplied_chunks_keep_their_order_and_may_be_named_in_bytes(self):
        data = png_io.write_png(1, 1, "L", b"\x07",
                                chunks=[(b"sRGB", b"\x00"), ("pHYs", bytes(9)), ("tEXt", b"a\x00b")])
        self.assertEqual(png_io.png_info(data)["chunks"], ["IHDR", "sRGB", "pHYs", "tEXt", "IDAT", "IEND"])

    def test_only_ancillary_chunks_may_be_supplied(self):
        for bad in ([("IDAT", b"")], [("IHDR", bytes(13))], [("IEND", b"")], [("PLTE", bytes(3))],
                    [("abc", b"")], [("ab1d", b"")], [("abcde", b"")], ["iCCP"], [("iCCP",)], [(7, b"")],
                    [("iCCP", "text")], [("iCCP", None)]):
            with self.assertRaises(png_io.PngError, msg=repr(bad)) as caught:
                png_io.write_png(1, 1, "L", b"\x00", chunks=bad)
            self.assertEqual(caught.exception.code, "bad_chunk")

    def test_arguments_that_are_not_an_image(self):
        good = dict(width=2, height=2, mode="L", pixels=bytes(4))
        for change in ({"mode": "P"}, {"mode": "l"}, {"width": 0}, {"height": 0}, {"width": -1}, {"width": 2.0},
                       {"width": True}, {"height": 1 << 31}, {"pixels": bytes(3)}, {"pixels": bytes(5)},
                       {"pixels": "abcd"}, {"pixels": [0, 0, 0, 0]}, {"mode": "RGB"}):
            with self.assertRaises(png_io.PngError, msg=repr(change)) as caught:
                png_io.write_png(**dict(good, **change))
            self.assertEqual(caught.exception.code, "bad_image")
        for level in (-1, 10, 6.0, True, None):
            with self.assertRaises(png_io.PngError, msg=repr(level)):
                png_io.write_png(2, 2, "L", bytes(4), level=level)

    def test_pixels_may_be_a_bytearray_or_a_memoryview(self):
        pixels = noise(12, 3)
        expected = png_io.write_png(2, 2, "RGB", pixels)
        self.assertEqual(png_io.write_png(2, 2, "RGB", bytearray(pixels)), expected)
        self.assertEqual(png_io.write_png(2, 2, "RGB", memoryview(pixels)), expected)


class Thumbnail(PngCase):
    def alpha(self, width=1060, height=324):
        # Every level, hard zeros, and a 1 beside a 0.
        return bytes((0 if (x // 40 + y // 40) % 3 == 0 else (x * 3 + y) % 256) for y in range(height)
                     for x in range(width))

    def test_the_form_the_app_stores(self):
        alpha = self.alpha()
        data = png_io.write_thumbnail(alpha)
        info = png_io.png_info(data)
        self.assertEqual((info["width"], info["height"]), (1060, 324))
        self.assertEqual((info["color_type"], info["bit_depth"], info["interlace"]), (6, 8, 0))
        self.assertEqual(info["chunks"], ["IHDR", "sRGB", "pHYs", "IDAT", "IEND"])
        self.assertEqual(png_io.get_chunks(data, "sRGB", "pHYs"),
                         [("sRGB", b"\x00"), ("pHYs", struct.pack(">IIB", 2835, 2835, 1))])
        self.assertEqual(png_io.THUMBNAIL_SIZE, (1060, 324))

    def test_white_wherever_there_is_ink_and_nothing_where_there_is_none(self):
        alpha = self.alpha()
        self.assertEqual(set(alpha), set(range(256)), "the test covers every level")
        oracle = fixtures.read_png(png_io.write_thumbnail(alpha))
        pixels = oracle["pixels"]
        self.assertEqual(oracle["mode"], "RGBA")
        self.assertEqual(pixels[3::4], alpha, "straight alpha, as given")
        white = bytes(255 if a else 0 for a in alpha)
        for channel in range(3):
            self.assertEqual(pixels[channel::4], white)

    def test_reading_it_back_gives_the_coverage(self):
        alpha = self.alpha(64, 20)
        image = png_io.read_png(png_io.write_thumbnail(alpha, 64, 20))
        self.assertEqual((image.width, image.height, image.mode), (64, 20, "RGBA"))
        self.assertEqual(png_io.alpha_plane(image).pixels, alpha)
        self.assertEqual(png_io.to_gray8(image).pixels, alpha)

    def test_the_size_and_the_bytes_must_agree(self):
        for call in (lambda: png_io.write_thumbnail(bytes(1060 * 324 - 1)),
                     lambda: png_io.write_thumbnail(bytes(10), 3, 3),
                     lambda: png_io.write_thumbnail("x" * 9, 3, 3),
                     lambda: png_io.write_thumbnail(bytes(0), 0, 4)):
            with self.assertRaises(png_io.PngError):
                call()
        self.assertEqual(png_io.png_info(png_io.write_thumbnail(bytearray(9), 3, 3))["width"], 3)


# ── pixel helpers ────────────────────────────────────────────────────────────

def image(width, height, mode, seed=0):
    return png_io.Image(width, height, mode, noise(width * height * png_io.MODES[mode], seed))


def pixel(img, x, y):
    step = png_io.MODES[img.mode]
    start = (y * img.width + x) * step
    return img.pixels[start:start + step]


def luma(r, g, b):
    return (19595 * r + 38470 * g + 7471 * b + 32768) >> 16


class GreyAndAlpha(unittest.TestCase):
    def test_grey_is_itself_and_inverts(self):
        img = image(9, 5, "L", 1)
        self.assertEqual(png_io.to_gray8(img).pixels, img.pixels)
        self.assertEqual(png_io.to_gray8(img, invert=True).pixels, bytes(255 - v for v in img.pixels))
        self.assertEqual(png_io.to_gray8(img).mode, "L")

    def test_grey_with_alpha_is_the_product_over_black(self):
        img = image(11, 7, "LA", 2)
        pairs = list(zip(img.pixels[0::2], img.pixels[1::2]))
        self.assertEqual(png_io.to_gray8(img).pixels, bytes((v * a + 127) // 255 for v, a in pairs))
        self.assertEqual(png_io.to_gray8(img, invert=True).pixels,
                         bytes(((255 - v) * a + 127) // 255 for v, a in pairs),
                         "inverted first, so what is transparent stays black")

    def test_every_grey_level_and_alpha_pair(self):
        pixels = bytes(value for v in range(256) for a in range(256) for value in (v, a))
        img = png_io.Image(256, 256, "LA", pixels)
        self.assertEqual(png_io.to_gray8(img).pixels,
                         bytes((v * a + 127) // 255 for v in range(256) for a in range(256)))

    def test_colour_becomes_luminance(self):
        img = image(10, 6, "RGB", 3)
        triples = list(zip(img.pixels[0::3], img.pixels[1::3], img.pixels[2::3]))
        expected = bytes(luma(*t) for t in triples)
        self.assertEqual(png_io.luminance(img).pixels, expected)
        self.assertEqual(png_io.to_gray8(img).pixels, expected)
        rgba = png_io.Image(10, 6, "RGBA", b"".join(bytes(t) + bytes([a]) for t, a in zip(triples, noise(60, 4))))
        self.assertEqual(png_io.luminance(rgba).pixels, expected, "alpha is ignored")
        self.assertEqual(png_io.to_gray8(rgba).pixels,
                         bytes((luma(*t) * a + 127) // 255 for t, a in zip(triples, noise(60, 4))))

    def test_luminance_over_a_grid_of_colours(self):
        levels = range(0, 256, 5)
        triples = [(r, g, b) for r in levels for g in levels for b in levels]
        img = png_io.Image(len(triples), 1, "RGB", bytes(v for t in triples for v in t))
        self.assertEqual(png_io.luminance(img).pixels, bytes(luma(*t) for t in triples))

    def test_a_grey_stored_as_colour_keeps_every_level(self):
        img = png_io.Image(256, 1, "RGB", bytes(v for level in range(256) for v in (level,) * 3))
        self.assertEqual(png_io.luminance(img).pixels, bytes(range(256)))
        self.assertEqual((luma(255, 255, 255), luma(0, 0, 0), luma(255, 0, 0), luma(0, 255, 0), luma(0, 0, 255)),
                         (255, 0, 76, 150, 29))
        primaries = png_io.Image(3, 1, "RGB", bytes([255, 0, 0, 0, 255, 0, 0, 0, 255]))
        self.assertEqual(png_io.luminance(primaries).pixels, bytes([76, 150, 29]))

    def test_the_stored_thumbnail_form_is_its_alpha(self):
        alpha = bytes([0, 1, 2, 127, 128, 254, 255, 0, 9])
        white = bytes(255 if a else 0 for a in alpha)
        rgba = png_io.Image(3, 3, "RGBA", b"".join(bytes([w, w, w, a]) for w, a in zip(white, alpha)))
        self.assertEqual(png_io.to_gray8(rgba).pixels, alpha)
        la = png_io.Image(3, 3, "LA", b"".join(bytes([w, a]) for w, a in zip(white, alpha)))
        self.assertEqual(png_io.to_gray8(la).pixels, alpha)
        # Colour left behind where alpha is 0 does not show.
        stray = png_io.Image(3, 3, "LA", b"".join(bytes([200 if a == 0 else 255, a]) for a in alpha))
        self.assertEqual(png_io.to_gray8(stray).pixels, alpha)

    def test_the_alpha_plane(self):
        rgba = image(5, 4, "RGBA", 5)
        self.assertEqual(png_io.alpha_plane(rgba), png_io.Image(5, 4, "L", rgba.pixels[3::4]))
        la = image(5, 4, "LA", 6)
        self.assertEqual(png_io.alpha_plane(la).pixels, la.pixels[1::2])
        self.assertIsNone(png_io.alpha_plane(image(5, 4, "L")))
        self.assertIsNone(png_io.alpha_plane(image(5, 4, "RGB")))

    def test_the_negative_leaves_alpha_alone(self):
        for mode in ("L", "LA", "RGB", "RGBA"):
            img = image(6, 3, mode, 7)
            step = png_io.MODES[mode]
            has_alpha = mode in ("LA", "RGBA")
            expected = bytes(v if has_alpha and index % step == step - 1 else 255 - v
                             for index, v in enumerate(img.pixels))
            self.assertEqual(png_io.negative(img), png_io.Image(6, 3, mode, expected))

    def test_what_is_not_an_image_is_refused(self):
        for bad in (None, (2, 2, "L", bytes(4)), png_io.Image(2, 2, "L", bytes(3)), png_io.Image(2, 2, "P", bytes(4)),
                    png_io.Image(0, 2, "L", b""), png_io.Image(2, 2, "L", bytearray(4)),
                    png_io.Image(2, 2, "L", [0, 0, 0, 0])):
            for function in (png_io.to_gray8, png_io.luminance, png_io.alpha_plane, png_io.negative, png_io.flatten):
                with self.assertRaises(png_io.PngError, msg=f"{function.__name__}({bad!r})"):
                    function(bad)


class Flatten(unittest.TestCase):
    def test_grey_with_alpha_over_a_level(self):
        img = image(13, 9, "LA", 1)
        for ground in (0, 26, 128, 255):
            expected = bytes((v * a + ground * (255 - a) + 127) // 255
                             for v, a in zip(img.pixels[0::2], img.pixels[1::2]))
            self.assertEqual(png_io.flatten(img, ground), png_io.Image(13, 9, "L", expected))

    def test_colour_with_alpha_over_a_level_or_a_colour(self):
        img = image(7, 5, "RGBA", 2)
        quads = [img.pixels[i:i + 4] for i in range(0, len(img.pixels), 4)]
        for ground in (0, 200, (10, 120, 250)):
            levels = ground if isinstance(ground, tuple) else (ground,) * 3
            expected = bytes((q[c] * q[3] + levels[c] * (255 - q[3]) + 127) // 255 for q in quads for c in range(3))
            self.assertEqual(png_io.flatten(img, ground), png_io.Image(7, 5, "RGB", expected))

    def test_an_image_without_alpha_comes_back_as_it_is(self):
        for mode in ("L", "RGB"):
            img = image(4, 4, mode, 3)
            self.assertEqual(png_io.flatten(img, 99).pixels, img.pixels)
            self.assertEqual(png_io.flatten(img, 99).mode, mode)

    def test_opaque_alpha_is_the_colour_and_clear_alpha_is_the_ground(self):
        colour = noise(12, 4)
        opaque = png_io.Image(4, 3, "LA", b"".join(bytes([v, 255]) for v in colour))
        self.assertEqual(png_io.flatten(opaque, 77).pixels, colour)
        clear = png_io.Image(4, 3, "LA", b"".join(bytes([v, 0]) for v in colour))
        self.assertEqual(png_io.flatten(clear, 77).pixels, bytes([77]) * 12)

    def test_white_ink_over_a_dark_ground_is_the_stroke_preview_rule(self):
        alpha = bytes(range(256))
        expected = bytes(26 + (229 * a + 127) // 255 for a in alpha)
        self.assertEqual((expected[0], expected[255]), (26, 255))
        self.assertEqual(png_io.flatten_ink(png_io.Image(256, 1, "L", alpha)).pixels, expected)
        la = png_io.Image(256, 1, "LA", b"".join(bytes([255, a]) for a in alpha))
        self.assertEqual(png_io.flatten(la, 26).pixels, expected)
        rgba = png_io.Image(256, 1, "RGBA", b"".join(bytes([255 if a else 0] * 3 + [a]) for a in alpha))
        self.assertEqual(png_io.flatten(rgba, 26).pixels, bytes(v for v in expected for _ in range(3)))

    def test_ink_levels_can_be_chosen(self):
        alpha = bytes(range(256))
        for ground, ink in ((0, 255), (255, 0), (16, 200)):
            self.assertEqual(png_io.flatten_ink(png_io.Image(16, 16, "L", alpha), ground, ink).pixels,
                             bytes((ink * a + ground * (255 - a) + 127) // 255 for a in alpha))
        self.assertEqual(png_io.flatten_ink(png_io.Image(16, 16, "L", alpha), 0, 255).pixels, alpha)

    def test_bad_grounds_are_refused(self):
        la, rgba = image(2, 2, "LA"), image(2, 2, "RGBA")
        for img, ground in ((la, 256), (la, -1), (la, 1.5), (la, True), (la, (1, 2, 3)), (rgba, (1, 2)),
                            (rgba, (1, 2, 256)), (rgba, "white")):
            with self.assertRaises(png_io.PngError, msg=repr(ground)):
                png_io.flatten(img, ground)
        for ground, ink in ((256, 0), (0, -1), (True, 0), (0, 1.0)):
            with self.assertRaises(png_io.PngError):
                png_io.flatten_ink(image(2, 2, "L"), ground, ink)
        with self.assertRaises(png_io.PngError):
            png_io.flatten_ink(la)


class Geometry(unittest.TestCase):
    def test_crop(self):
        for mode in ("L", "LA", "RGB", "RGBA"):
            img = image(9, 7, mode, 1)
            part = png_io.crop(img, 2, 3, 5, 4)
            self.assertEqual((part.width, part.height, part.mode), (5, 4, mode))
            self.assertEqual(part.pixels, b"".join(pixel(img, 2 + x, 3 + y) for y in range(4) for x in range(5)))
            self.assertEqual(png_io.crop(img, 0, 0, 9, 7).pixels, img.pixels)
            self.assertEqual(png_io.crop(img, 8, 6, 1, 1).pixels, pixel(img, 8, 6))

    def test_a_crop_must_lie_inside(self):
        img = image(9, 7, "L")
        for box in ((-1, 0, 2, 2), (0, -1, 2, 2), (8, 0, 2, 1), (0, 6, 1, 2), (0, 0, 0, 1), (0, 0, 1, 0),
                    (0, 0, 10, 7)):
            with self.assertRaises(png_io.PngError, msg=repr(box)):
                png_io.crop(img, *box)

    def test_a_tiled_crop_wraps(self):
        for mode in ("L", "RGBA"):
            img = image(5, 4, mode, 2)
            for left, top, width, height in ((0, 0, 5, 4), (1, 1, 3, 2), (3, 2, 9, 9), (-2, -3, 12, 11),
                                             (7, 9, 1, 1), (-10, 0, 23, 2)):
                part = png_io.tile_crop(img, left, top, width, height)
                self.assertEqual((part.width, part.height, part.mode), (width, height, mode))
                self.assertEqual(part.pixels, b"".join(pixel(img, (left + x) % 5, (top + y) % 4)
                                                       for y in range(height) for x in range(width)),
                                 (left, top, width, height))
        with self.assertRaises(png_io.PngError):
            png_io.tile_crop(image(5, 4, "L"), 0, 0, 0, 3)

    def test_the_centre_of_a_large_grain_and_a_small_one_tiled(self):
        large = image(40, 30, "L", 3)
        centre = png_io.tile_crop(large, (40 - 16) // 2, (30 - 16) // 2, 16, 16)
        self.assertEqual(centre, png_io.crop(large, 12, 7, 16, 16))
        small = image(6, 6, "L", 4)
        tiled = png_io.tile_crop(small, (6 - 16) // 2, (6 - 16) // 2, 16, 16)
        self.assertEqual(pixel(tiled, 5, 5), pixel(small, 0, 0))
        self.assertEqual(pixel(tiled, 11, 11), pixel(small, 0, 0))

    def test_centred_on_a_canvas(self):
        img = image(4, 2, "L", 5)
        out = png_io.center_on(img, 9, 5, fill=7)
        self.assertEqual((out.width, out.height), (9, 5))
        for y in range(5):
            for x in range(9):
                inside = 2 <= x < 6 and 1 <= y < 3      # 5 spare columns: 2 left, 3 right; 3 spare rows: 1 above
                self.assertEqual(pixel(out, x, y), pixel(img, x - 2, y - 1) if inside else b"\x07", (x, y))

    def test_centred_when_larger_is_a_centre_crop(self):
        img = image(10, 8, "RGB", 6)
        self.assertEqual(png_io.center_on(img, 4, 8), png_io.crop(img, 3, 0, 4, 8))
        mixed = png_io.center_on(img, 4, 12, fill=(1, 2, 3))
        self.assertEqual((mixed.width, mixed.height), (4, 12))
        self.assertEqual(pixel(mixed, 0, 0), bytes([1, 2, 3]))
        self.assertEqual(pixel(mixed, 0, 2), pixel(img, 3, 0))
        self.assertEqual(pixel(mixed, 3, 9), pixel(img, 6, 7))
        self.assertEqual(pixel(mixed, 3, 10), bytes([1, 2, 3]))
        self.assertEqual(png_io.center_on(img, 10, 8).pixels, img.pixels)

    def test_a_fill_per_channel(self):
        out = png_io.center_on(image(1, 1, "LA", 1), 3, 1, fill=(9, 0))
        self.assertEqual(out.pixels[:2], bytes([9, 0]))
        for fill in (256, -1, (1,), (1, 2, 3), 1.0, True):
            with self.assertRaises(png_io.PngError, msg=repr(fill)):
                png_io.center_on(image(1, 1, "LA"), 3, 3, fill=fill)
        with self.assertRaises(png_io.PngError):
            png_io.center_on(image(1, 1, "L"), 0, 3)

    def test_the_fit_factor(self):
        for size, box, factor in (((1060, 324), (530, 162), 2), ((440, 276), (530, 162), 2),
                                  ((327, 100), (530, 162), 1), ((2048, 2048), (256, 256), 8),
                                  ((2000, 2000), (256, 256), 8), ((256, 256), (256, 256), 1),
                                  ((257, 10), (256, 256), 2), ((650, 571), (256, 256), 3), ((1, 1), (256, 256), 1),
                                  ((10, 2049), (256, 256), 9)):
            self.assertEqual(png_io.fit_factor(*size, *box), factor, (size, box))
        with self.assertRaises(png_io.PngError):
            png_io.fit_factor(0, 1, 2, 2)


def reduce_reference(img, factor):
    step = png_io.MODES[img.mode]
    out_w, out_h = -(-img.width // factor), -(-img.height // factor)
    out = bytearray()
    for out_y in range(out_h):
        for out_x in range(out_w):
            for channel in range(step):
                block = [img.pixels[(y * img.width + x) * step + channel]
                         for y in range(out_y * factor, min(img.height, out_y * factor + factor))
                         for x in range(out_x * factor, min(img.width, out_x * factor + factor))]
                out.append((sum(block) + len(block) // 2) // len(block))
    return png_io.Image(out_w, out_h, img.mode, bytes(out))


class BoxReduce(unittest.TestCase):
    def test_against_the_long_way(self):
        for mode in ("L", "LA", "RGB", "RGBA"):
            for width, height in ((1, 1), (5, 3), (16, 16), (17, 9), (33, 31), (2, 40)):
                img = image(width, height, mode, width + height)
                for factor in (1, 2, 3, 4, 5, 8, 16, 40):
                    self.assertEqual(png_io.box_reduce(img, factor), reduce_reference(img, factor),
                                     f"{mode} {width}x{height} by {factor}")

    def test_a_factor_larger_than_the_image_gives_one_pixel(self):
        img = image(7, 3, "LA", 4)
        out = png_io.box_reduce(img, 1000)
        self.assertEqual(out, reduce_reference(img, 1000))
        self.assertEqual(out.size, (1, 1))

    def test_extremes_do_not_overflow(self):
        for width, height, factor in ((64, 64, 16), (40, 30, 7), (300, 4, 150)):
            white = png_io.Image(width, height, "L", b"\xff" * (width * height))
            out = png_io.box_reduce(white, factor)
            self.assertEqual(set(out.pixels), {255}, (width, height, factor))

    def test_a_half_rounds_up(self):
        def one(*values):
            return png_io.box_reduce(png_io.Image(2, 2, "L", bytes(values)), 2).pixels[0]
        self.assertEqual(one(0, 0, 0, 1), 0)             # 0.25
        self.assertEqual(one(0, 0, 1, 1), 1)             # 0.5
        self.assertEqual(one(1, 1, 1, 0), 1)             # 0.75
        self.assertEqual(one(255, 255, 255, 254), 255)   # 254.75
        self.assertEqual(one(255, 254, 254, 254), 254)   # 254.25

    def test_the_sizes_previews_use(self):
        thumbnail = image(1060, 324, "L", 1)
        self.assertEqual(png_io.box_reduce(thumbnail, 2).size, (530, 162))
        old = png_io.Image(440, 276, "L", bytes(440 * 276))
        self.assertEqual(png_io.box_reduce(old, png_io.fit_factor(440, 276, 530, 162)).size, (220, 138))
        odd = png_io.Image(650, 571, "L", bytes(650 * 571))
        self.assertEqual(png_io.box_reduce(odd, 3).size, (217, 191))

    def test_a_very_large_factor_uses_wider_sums(self):
        # 255 * factor * factor no longer fits 32 bits from 4105 up.
        white = png_io.Image(4105, 2, "L", b"\xff" * 8210)
        self.assertEqual(png_io.box_reduce(white, 4105), png_io.Image(1, 1, "L", b"\xff"))
        img = image(4200, 3, "L", 9)
        self.assertEqual(png_io.box_reduce(img, 4199), reduce_reference(img, 4199))
        self.assertEqual(png_io.box_reduce(img, 4104), reduce_reference(img, 4104))

    def test_factor_one_is_the_image_and_a_bad_factor_is_refused(self):
        img = image(7, 7, "RGB", 1)
        self.assertEqual(png_io.box_reduce(img, 1), png_io.Image(7, 7, "RGB", img.pixels))
        for factor in (0, -2, 1.5, True, None, "2"):
            with self.assertRaises(png_io.PngError, msg=repr(factor)):
                png_io.box_reduce(img, factor)


class Measures(unittest.TestCase):
    def test_histogram(self):
        img = image(50, 40, "L", 1)
        self.assertEqual(png_io.histogram(img), [img.pixels.count(bytes([v])) for v in range(256)])
        self.assertEqual(sum(png_io.histogram(img)), 2000)
        with self.assertRaises(png_io.PngError):
            png_io.histogram(image(2, 2, "LA"))

    def test_bbox(self):
        pixels = bytearray(10 * 8)
        for x, y, value in ((3, 2, 200), (7, 5, 17), (4, 6, 16), (9, 0, 1)):
            pixels[y * 10 + x] = value
        img = png_io.Image(10, 8, "L", bytes(pixels))
        self.assertEqual(png_io.bbox(img), (3, 0, 10, 7))
        self.assertEqual(png_io.bbox(img, 16), (3, 2, 8, 6), "above the threshold, not at it")
        self.assertEqual(png_io.bbox(img, 17), (3, 2, 4, 3))
        self.assertIsNone(png_io.bbox(img, 200))
        self.assertIsNone(png_io.bbox(png_io.Image(4, 4, "L", bytes(16))))
        self.assertEqual(png_io.bbox(png_io.Image(4, 4, "L", b"\x01" * 16)), (0, 0, 4, 4))
        self.assertEqual(png_io.bbox(png_io.Image(1, 1, "L", b"\x09")), (0, 0, 1, 1))

    def test_bbox_against_the_long_way(self):
        rng = random.Random(4)
        for _ in range(40):
            width, height = rng.randrange(1, 20), rng.randrange(1, 20)
            pixels = bytes(rng.choice((0, 0, 0, 0, 0, 0, 9, 40)) for _ in range(width * height))
            marked = [(x, y) for y in range(height) for x in range(width) if pixels[y * width + x] > 16]
            expected = None
            if marked:
                expected = (min(x for x, _ in marked), min(y for _, y in marked),
                            max(x for x, _ in marked) + 1, max(y for _, y in marked) + 1)
            self.assertEqual(png_io.bbox(png_io.Image(width, height, "L", pixels), 16), expected)

    def test_the_border_mean(self):
        img = png_io.Image(3, 3, "L", bytes([10, 20, 30, 40, 250, 60, 70, 80, 90]))
        self.assertEqual(png_io.border_mean(img), (10 + 20 + 30 + 40 + 60 + 70 + 80 + 90) / 8)
        big = image(12, 9, "L", 2)
        ring = [big.pixels[y * 12 + x] for y in range(9) for x in range(12) if x in (0, 11) or y in (0, 8)]
        self.assertEqual(png_io.border_mean(big), sum(ring) / len(ring))
        ring2 = [big.pixels[y * 12 + x] for y in range(9) for x in range(12) if x < 2 or x > 9 or y < 2 or y > 6]
        self.assertEqual(png_io.border_mean(big, ring=2), sum(ring2) / len(ring2))
        thin = png_io.Image(5, 2, "L", bytes(range(10)))
        self.assertEqual(png_io.border_mean(thin), 4.5, "an image with no inside is all border")
        self.assertGreater(png_io.border_mean(png_io.Image(4, 4, "L", b"\xff" * 16)), 127)
        for ring in (0, -1, 1.0, True):
            with self.assertRaises(png_io.PngError):
                png_io.border_mean(big, ring=ring)


class Stretch(unittest.TestCase):
    def table(self, hi):
        return [min(255, (v * 255 + hi // 2) // hi) for v in range(256)]

    def test_the_nearest_rank_percentile_of_what_is_not_zero(self):
        # 1000 inked pixels: the 995th smallest sets the level.
        pixels = bytes([100] * 995 + [200] * 5 + [0] * 3000)
        out = png_io.stretch(png_io.Image(100, 40, "L", pixels))
        self.assertEqual((out.hi, out.peak, out.nonzero), (100, 200, 1000))
        self.assertEqual(out.gain, 2.55)
        self.assertEqual(set(out.image.pixels), {0, 255}, "100 becomes 255, and 200 is cut at 255")
        pixels = bytes([100] * 994 + [200] * 6 + [0] * 3000)
        self.assertEqual(png_io.stretch(png_io.Image(100, 40, "L", pixels)).hi, 200)

    def test_every_value_follows_the_rule(self):
        img = image(60, 50, "L", 3)
        out = png_io.stretch(img)
        ordered = sorted(v for v in img.pixels if v)
        rank = -(-995 * len(ordered) // 1000)
        self.assertEqual(out.hi, max(16, ordered[rank - 1]))
        table = self.table(out.hi)
        self.assertEqual(out.image.pixels, bytes(table[v] for v in img.pixels))
        self.assertEqual(out.gain, 255 / out.hi)
        self.assertEqual(out.peak, max(img.pixels))

    def test_a_faint_image_is_lifted_and_the_gain_reported(self):
        faint = png_io.Image(8, 4, "L", bytes([0, 1, 2, 3, 4, 5, 6, 7] * 4))
        out = png_io.stretch(faint)
        self.assertEqual((out.hi, out.peak, out.nonzero), (16, 7, 28), "never stretched past the floor")
        self.assertEqual(out.gain, 255 / 16)
        self.assertEqual(out.image.pixels[:8], bytes((v * 255 + 8) // 16 for v in range(8)))
        self.assertEqual(out.image.pixels[7], 112)
        mid = png_io.Image(4, 1, "L", bytes([0, 30, 60, 60]))
        out = png_io.stretch(mid)
        self.assertEqual((out.hi, out.gain), (60, 4.25))
        self.assertEqual(out.image.pixels, bytes([0, 128, 255, 255]))

    def test_a_full_range_image_is_left_alone(self):
        # More than one pixel in 200 is already at 255.
        img = png_io.Image(16, 17, "L", bytes(range(256)) + b"\xff" * 16)
        out = png_io.stretch(img)
        self.assertEqual((out.hi, out.gain), (255, 1.0))
        self.assertEqual(out.image.pixels, img.pixels)
        # A lone 255 among many is not the level: the 99.5th percentile is.
        lone = png_io.Image(256, 4, "L", bytes(range(256)) * 4)
        self.assertEqual(png_io.stretch(lone).hi, 254)

    def test_no_ink_at_all(self):
        blank = png_io.Image(5, 5, "L", bytes(25))
        out = png_io.stretch(blank)
        self.assertEqual((out.hi, out.peak, out.nonzero, out.image.pixels), (16, 0, 0, bytes(25)))

    def test_the_floor_and_the_percentile_can_be_set(self):
        img = png_io.Image(4, 1, "L", bytes([1, 2, 3, 4]))
        self.assertEqual(png_io.stretch(img, floor=1).hi, 4)
        self.assertEqual(png_io.stretch(img, floor=1, permille=500).hi, 2)
        self.assertEqual(png_io.stretch(img, floor=1, permille=1).hi, 1)
        self.assertEqual(png_io.stretch(img, floor=1, permille=1000).hi, 4)
        for options in ({"floor": 0}, {"floor": 256}, {"permille": 0}, {"permille": 1001}, {"floor": 1.5},
                        {"permille": True}):
            with self.assertRaises(png_io.PngError, msg=repr(options)):
                png_io.stretch(img, **options)
        with self.assertRaises(png_io.PngError):
            png_io.stretch(image(2, 2, "RGB"))


class TheStrokePreviewChain(PngCase):
    """F6 end to end on a made-up thumbnail: the helpers give the contract's numbers."""

    def test_alpha_reduced_stretched_and_flattened(self):
        width, height = 1060, 324
        alpha = bytes(min(60, max(0, 60 - abs(y - 162))) if 100 <= x < 900 else 0
                      for y in range(height) for x in range(width))
        thumbnail = png_io.read_png(png_io.write_thumbnail(alpha))
        ink = png_io.alpha_plane(thumbnail)
        factor = png_io.fit_factor(ink.width, ink.height, 530, 162)
        small = png_io.center_on(png_io.box_reduce(ink, factor), 530, 162)
        out = png_io.stretch(small)
        tile = png_io.flatten_ink(out.image)
        self.assertEqual((factor, tile.size, tile.mode), (2, (530, 162), "L"))
        self.assertEqual(out.peak, 60)
        self.assertLess(out.hi, 61)
        self.assertEqual(min(tile.pixels), 26)
        self.assertEqual(max(tile.pixels), 255, "a faint stroke reaches full ink after the stretch")
        written = png_io.write_png(tile.width, tile.height, "L", tile.pixels)
        self.assertEqual(fixtures.read_png(written)["pixels"], tile.pixels)


# ── the optional fast path ───────────────────────────────────────────────────

class NoPilSwitch(unittest.TestCase):
    PROBE = ("import sys; sys.path.insert(0, sys.argv[1]); import png_io\n"
             "try:\n    import PIL.Image\n    there = True\nexcept Exception:\n    there = False\n"
             "print(png_io.HAVE_PIL, there)")

    def run_probe(self, value):
        env = {k: v for k, v in os.environ.items() if k != png_io.ENV_NO_PIL}
        if value is not None:
            env[png_io.ENV_NO_PIL] = value
        done = subprocess.run([sys.executable, "-c", self.PROBE, str(PIPELINE)], env=env, capture_output=True,
                              timeout=120)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        have, there = done.stdout.decode("ascii").split()
        return have == "True", there == "True"

    def test_the_environment_variable_forces_the_standard_library(self):
        self.assertEqual(png_io.ENV_NO_PIL, "ROSW_BRUSHES_NO_PIL")
        for value in ("1", "yes", "true"):
            have, _ = self.run_probe(value)
            self.assertFalse(have, value)

    def test_without_it_pil_is_used_exactly_when_it_can_be_imported(self):
        for value in (None, "", "0"):
            have, there = self.run_probe(value)
            self.assertEqual(have, there, repr(value))

    def test_the_flag_can_be_switched_off_at_run_time(self):
        data = encode(6, 6, 6, 8, noise(144, 1), kinds=(4,))
        with mock.patch.object(png_io, "HAVE_PIL", False), \
                mock.patch.object(png_io, "_pil_pixels", side_effect=AssertionError("PIL was asked")):
            self.assertEqual(png_io.read_png(data).pixels, noise(144, 1))


@unittest.skipUnless(PilImage is not None and png_io._PIL is not None, "PIL is not importable here")
class WithPil(PngCase):
    """The fast path gives what the pure path gives, and is really taken."""

    USE_PIL = True

    def both(self, data):
        with mock.patch.object(png_io, "HAVE_PIL", False):
            pure = png_io.read_png(data)
        calls = []
        real = png_io._pil_pixels

        def watched(*args):
            calls.append(real(*args))
            return calls[-1]
        with mock.patch.object(png_io, "_pil_pixels", watched):
            fast = png_io.read_png(data)
        return pure, fast, calls

    def test_eight_bit_images_are_identical_on_both_paths(self):
        for color in (0, 4, 2, 6):
            step = CHANNELS[color]
            for width, height in ((1, 1), (7, 5), (40, 23)):
                for samples in pictures(width, height, step, seed=color):
                    for kinds in FILTER_CHOICES:
                        pure, fast, calls = self.both(encode(width, height, color, 8, samples, kinds=kinds))
                        self.assertEqual(fast, pure)
                        self.assertEqual(pure.pixels, samples)
                        self.assertEqual(calls, [samples], "PIL did the work, once")

    def test_what_pil_is_not_asked_for(self):
        palette = bytes(48)
        for data in (encode(4, 4, 3, 8, bytes(16), palette=palette), encode(4, 4, 0, 16, bytes(32)),
                     encode(4, 4, 0, 4, bytes(8)), encode(4, 4, 0, 8, bytes(16), trns=b"\x00\x00"),
                     encode(4, 4, 2, 8, bytes(48), trns=bytes(6)), encode(4, 4, 6, 8, bytes(64), trns=bytes(6))):
            pure, fast, calls = self.both(data)
            self.assertEqual(fast, pure)
            self.assertEqual(calls, [])

    def test_a_pil_that_fails_or_disagrees_is_ignored(self):
        data = encode(5, 5, 0, 8, noise(25, 2), kinds=(4,))
        for stand_in in (mock.Mock(open=mock.Mock(side_effect=OSError("broken"))),
                         mock.Mock(open=mock.Mock(side_effect=RuntimeError("anything")))):
            with mock.patch.object(png_io, "_PIL", stand_in):
                self.assertEqual(png_io.read_png(data).pixels, noise(25, 2))
        other = encode(5, 5, 4, 8, noise(50, 3))

        class WrongPicture:
            @staticmethod
            def open(stream):
                return PilImage.open(io.BytesIO(other))
        with mock.patch.object(png_io, "_PIL", WrongPicture):
            self.assertEqual(png_io.read_png(data).pixels, noise(25, 2), "another mode is not this image")

    def test_interlaced_eight_bit_images_are_the_same_on_both_paths(self):
        for color in (0, 4, 2, 6):
            step = CHANNELS[color]
            for width, height in ADAM7_SIZES:
                samples = noise(width * height * step, width)
                for kinds in ((0,), (1, 2, 3, 4)):
                    pure, fast, calls = self.both(encode_interlaced(width, height, color, 8, samples, kinds=kinds))
                    self.assertEqual(fast, pure)
                    self.assertEqual((pure.mode, pure.pixels), (MODE_OF[color], samples),
                                     f"colour {color} {width}x{height}")
                    self.assertEqual(calls, [samples], "PIL did the work, once")

    def test_other_interlaced_images_are_read_by_the_pure_path_alone_and_agree_with_pil(self):
        rng = random.Random(33)
        palette = rng.randbytes(48)
        cases = [(encode_interlaced(9, 9, 0, 16, noise(162, 1)), "L"),
                 (encode_interlaced(9, 9, 3, 8, bytes(rng.randrange(16) for _ in range(81)), palette=palette), "RGB"),
                 (encode_interlaced(11, 6, 3, 4, [rng.randrange(16) for _ in range(66)], palette=palette,
                                    trns=rng.randbytes(9)), "RGBA"),
                 (encode_interlaced(13, 5, 0, 2, [rng.randrange(4) for _ in range(65)], kinds=(1, 4)), "L"),
                 (encode_interlaced(13, 5, 0, 1, [rng.randrange(2) for _ in range(65)], kinds=(3,)), "L")]
        for data, mode in cases:
            pure, fast, calls = self.both(data)
            self.assertEqual(fast, pure)
            self.assertEqual(calls, [])
            with PilImage.open(io.BytesIO(data)) as picture:
                if mode == "L" and picture.mode not in ("L", "1", "P"):
                    continue                        # a 16-bit grey this PIL keeps at 16 bits
                self.assertEqual(pure.pixels, picture.convert(mode).tobytes(), mode)

    def test_the_pure_decoder_agrees_with_pil_on_the_forms_pil_is_not_used_for(self):
        def by_pil(data, mode):
            with PilImage.open(io.BytesIO(data)) as picture:
                return picture.convert(mode).tobytes()
        rng = random.Random(21)
        palette = rng.randbytes(48)
        for depth in (1, 2, 4, 8):
            entries = min(16, 1 << depth)
            indexes = [rng.randrange(entries) for _ in range(13 * 6)]
            samples = bytes(indexes) if depth == 8 else pack_bits(indexes, 13, depth)
            data = encode(13, 6, 3, depth, samples, kinds=(0, 1, 2, 3, 4), palette=palette[:entries * 3])
            self.assertEqual(png_io.read_png(data).pixels, by_pil(data, "RGB"), f"palette at {depth} bits")
            data = encode(13, 6, 3, depth, samples, palette=palette[:entries * 3], trns=rng.randbytes(entries - 1))
            self.assertEqual(png_io.read_png(data).pixels, by_pil(data, "RGBA"), f"palette and tRNS at {depth} bits")
        for depth in (1, 2, 4):
            values = [rng.randrange(1 << depth) for _ in range(13 * 6)]
            data = encode(13, 6, 0, depth, pack_bits(values, 13, depth), kinds=(4, 3, 2, 1, 0))
            self.assertEqual(png_io.read_png(data).pixels, by_pil(data, "L"), f"grey at {depth} bits")
        for color, mode in ((2, "RGB"), (6, "RGBA"), (4, "LA")):
            data = encode(7, 5, color, 16, rng.randbytes(35 * CHANNELS[color] * 2), kinds=(1, 2, 3, 4))
            with PilImage.open(io.BytesIO(data)) as picture:
                if picture.mode != mode:
                    continue                        # this PIL keeps 16 bits here; nothing to compare
                self.assertEqual(png_io.read_png(data).pixels, picture.tobytes(), f"16-bit colour type {color}")

    def test_pil_reduces_and_weighs_colour_as_the_helpers_do(self):
        # Powers of two only. For other factors PIL multiplies by a rounded
        # reciprocal and can land one below (sum + n // 2) // n, which is why
        # the helpers never hand a reduction to PIL.
        img = image(37, 22, "L", 5)
        picture = PilImage.frombytes("L", (37, 22), img.pixels)
        for factor in (2, 4, 8):
            reduced = picture.reduce(factor)
            ours = png_io.box_reduce(img, factor)
            self.assertEqual((ours.size, ours.pixels), (reduced.size, reduced.tobytes()), factor)
        colour = image(19, 11, "RGB", 6)
        self.assertEqual(png_io.luminance(colour).pixels,
                         PilImage.frombytes("RGB", (19, 11), colour.pixels).convert("L").tobytes())


@unittest.skipUnless(PilImage is not None and png_io._PIL is not None, "PIL is not importable here")
class HostileWithPil(Hostile):
    """The same refusals, with the same codes, when PIL is there to be asked."""

    USE_PIL = True


@unittest.skipUnless(PilImage is not None and png_io._PIL is not None, "PIL is not importable here")
class ReadEightBitWithPil(ReadEightBit):
    USE_PIL = True


# ── the real library, opt-in ─────────────────────────────────────────────────

LIBRARY_JUNK_NAMES = {".ds_store", "thumbs.db", "desktop.ini"}
LIBRARY_ROLES = {"Shape.png": "shape", "Grain.png": "grain", "QuickLook/Thumbnail.png": "thumbnail"}


def library_pngs(root):
    """(container, entry, bytes) for every PNG member under `root`, read in memory.

    The reading rules of F3 that matter here: a zip over BytesIO, nothing
    extracted, junk and folder entries dropped, unsafe or encrypted names
    skipped, the first of a duplicate name kept, and the caps on entries,
    file size and inflated entry size.
    """
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".brush", ".brushset"):
            continue
        if path.stat().st_size > 512 << 20:
            raise AssertionError(f"{path} is over the 512 MiB upload cap")
        container = path.relative_to(root).as_posix()
        with zipfile.ZipFile(io.BytesIO(path.read_bytes())) as archive:
            infos = archive.infolist()
            if len(infos) > 5000:
                raise AssertionError(f"{container} holds more than 5,000 entries")
            seen = set()
            for info in infos:
                name = info.orig_filename
                parts = name.split("/")
                if (info.is_dir() or parts[0] == "__MACOSX" or parts[-1].lower() in LIBRARY_JUNK_NAMES
                        or name.startswith("/") or ".." in parts or "\\" in name or info.flag_bits & 1
                        or name in seen or not name.lower().endswith(".png")):
                    continue
                seen.add(name)
                if info.file_size > 64 << 20:
                    raise AssertionError(f"{container} :: {name} inflates past 64 MiB")
                yield container, name, archive.read(info)


@unittest.skipUnless(CORPUS, "set ROSW_BRUSHES_CORPUS to a library folder to read its real images")
class RealLibrary(unittest.TestCase):
    """Every PNG member's header and chunks, and a full decode of each container's
    first shape, grain and thumbnail. 100 percent or a failure."""

    @classmethod
    def setUpClass(cls):
        if not sys.flags.isolated:
            raise AssertionError("brush files are read only by an isolated interpreter. Run:  python -I -m "
                                 "unittest discover -s brushes/pipeline/tests -p test_png_io.py")
        root = Path(CORPUS).resolve()
        if not root.is_dir():
            raise AssertionError(f"ROSW_BRUSHES_CORPUS is not a folder: {CORPUS}")
        cls.patcher = mock.patch.object(png_io, "HAVE_PIL", False)
        cls.patcher.start()
        cls.containers = set()
        cls.infos = []
        cls.problems = collections.defaultdict(list)
        cls.decoded = collections.Counter()
        cls.seen = {}
        picked = set()
        started = time.perf_counter()
        for container, entry, data in library_pngs(root):
            cls.containers.add(container)
            where = f"{container} :: {entry}"
            try:
                info = png_io.png_info(data)
            except png_io.PngError as exc:
                cls.problems["png_info"].append(f"{where}: {exc}")
                continue
            cls.infos.append(info)
            parts = entry.split("/")
            role = LIBRARY_ROLES.get("/".join(parts[-2:])) or LIBRARY_ROLES.get(parts[-1])
            if role is None or "Reset" in parts or (container, role) in picked:
                continue
            picked.add((container, role))
            digest = hashlib.sha256(data).hexdigest()
            if digest not in cls.seen:
                cls.seen[digest] = cls.check(data, info, where)
            cls.decoded[f"{role} {info['color_type']} {'ok' if cls.seen[digest] else 'failed'}"] += 1
        cls.seconds = time.perf_counter() - started
        sys.stderr.write(f"\n{len(cls.containers)} containers, {len(cls.infos)} PNG members, "
                         f"decoded {dict(sorted(cls.decoded.items()))} in {cls.seconds:.0f} s\n")

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    @classmethod
    def check(cls, data, info, where):
        try:
            img = png_io.read_png(data)
        except png_io.PngError as exc:
            cls.problems["read_png"].append(f"{where}: {exc}")
            return False
        if (img.width, img.height, img.mode) != (info["width"], info["height"], info["mode"]):
            cls.problems["header"].append(where)
            return False
        if len(img.pixels) != img.width * img.height * png_io.MODES[img.mode] or img.chunks != tuple(info["chunks"]):
            cls.problems["shape"].append(where)
            return False
        back = png_io.read_png(png_io.write_png(img.width, img.height, img.mode, img.pixels))
        if back.pixels != img.pixels:
            cls.problems["write_png"].append(where)
            return False
        if img.mode in ("LA", "RGBA") and info["width"] * info["height"] <= 1060 * 324:
            alpha = png_io.alpha_plane(img).pixels
            rebuilt = png_io.read_png(png_io.write_thumbnail(alpha, img.width, img.height))
            if png_io.alpha_plane(rebuilt).pixels != alpha:
                cls.problems["write_thumbnail"].append(where)
                return False
        return True

    def test_every_member_has_a_sound_header_and_chunk_list(self):
        self.assertGreater(len(self.infos), 0, "no PNG member found")
        self.assertEqual(self.problems["png_info"][:20], [])

    def test_the_sample_spans_the_library_and_decodes(self):
        self.assertGreaterEqual(len(self.containers), 10)
        for name in ("read_png", "header", "shape", "write_png", "write_thumbnail"):
            self.assertEqual(self.problems[name][:20], [], name)
        self.assertFalse(any(key.endswith("failed") for key in self.decoded), self.decoded)
        self.assertGreater(sum(self.decoded.values()), 0)


if __name__ == "__main__":
    unittest.main()
