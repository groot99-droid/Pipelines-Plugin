"""Read and write the PNG images a brush file carries, with the standard library.

    info = png_io.png_info(data)                  # header and chunk names; nothing is inflated
    img = png_io.read_png(data)                   # Image(width, height, mode, pixels, chunks)
    data = png_io.write_png(256, 256, "L", pixels)
    data = png_io.write_thumbnail(alpha)          # 1060x324 coverage in, the app's thumbnail form out

An `Image` is always 8 bits per sample in one of four modes, `L` (grey), `LA`,
`RGB`, `RGBA`, with `pixels` the rows from the top, nothing between them. The
rest of the module is the small set of pixel operations the preview step needs
(grey with polarity, box reduction, crop, flatten, contrast stretch), each one
integer arithmetic with one defined result. docs/CONTRACTS.md, F3 "Images" and
F6, fix the shapes and the numbers.

A PNG out of a brush file is data from a stranger. Reading one:

  - checks the signature, every chunk length and every chunk CRC, and stops at
    IEND;
  - refuses an image of more than `max_pixels` (8192 x 8192) from the header
    alone, before anything is inflated;
  - inflates the image data to the size the header gives and not one byte
    past it, so a small file cannot become a large allocation;
  - raises PngError (or one of its subclasses) for anything wrong. No other
    exception leaves `png_info`, `get_chunks` or `read_png` for bad bytes.

The error classes are the codec's own, defined once in bplist.py: PngError and
PngUnsupported are imported from there. An image over the pixel cap raises
PngLimitExceeded, which is both a PngError and the codec's LimitExceeded, with
the cap's name in spec.yaml as its code (`png_pixels`); so `except PngError`
covers everything a reader here raises, and `except LimitExceeded` every cap.
At the cap an image may still inflate to 8 bytes a pixel and take minutes to
unfilter in pure Python: a caller that reads many images passes a smaller
`max_pixels`.

What is read. Colour types 0, 2, 3, 4 and 6; 8 and 16 bits per sample, and 1,
2 and 4 for grey and palette images; all five row filters; interlaced (Adam7)
or not; a tRNS chunk (palette alpha, or the one transparent colour of a grey
or RGB image; beside a real alpha channel it is ignored). A 16-bit sample is
cut to its high byte. A grey sample of fewer than 8 bits is scaled to 0..255.
A palette image comes back RGB, or RGBA with a tRNS chunk. Gamma and
colour-profile chunks are named in `chunks` and never applied: the samples are
returned as stored. PngUnsupported is raised for one thing only: a critical
chunk this reader does not know (anything upper-case beyond IHDR, PLTE, IDAT
and IEND).

Interlace. docs/CONTRACTS.md F3 says an interlaced image raises PngUnsupported
unless PIL is present. That would make the one result depend on whether PIL
is installed, which F0 and the PIL rule below forbid, so the standard-library
path undoes Adam7 itself: each pass is filtered and packed on its own rows,
decoded as a small image, and laid into place. No image in the library is
interlaced; the path is held by synthetic tests (every mode and depth, sizes
that leave passes empty) and compared with PIL where PIL can be imported.

PIL. `HAVE_PIL` is true when `from PIL import Image` works and the environment
variable ROSW_BRUSHES_NO_PIL is not set to a value other than 0. PIL is then
used for one thing only: undoing the row filters (and the interlace) of an
8-bit grey, grey+alpha, RGB or RGBA image with no tRNS chunk, which is the slow
part in pure Python. Every check and every error is made here first, on both
paths, including the inflation of the image data to exactly the size the
header gives; PIL then reads the same, already checked bytes, and a PIL
result of another size or mode, or a PIL that raises, is thrown away for the
pure one. So every result, image or error, is the same with or without PIL.
Setting `png_io.HAVE_PIL = False` at run time forces the standard-library
path. Under `python -I`, the way a script that reads the library must be run,
a PIL installed in the user's own site-packages is not importable, so those
runs take the pure path.

What is written. 8 bits per sample, not interlaced, filter 0 on every row, one
IDAT chunk made with zlib at `level`, and the chunks IHDR, any supplied
ancillary chunks, IDAT, IEND. A shape or grain is mode `L` with no extra
chunk; a caller that wants the source file's colour profile kept passes its
iCCP chunk (`get_chunks(source, "iCCP")`) as `chunks`. The compressed bytes
depend on the zlib build, so compare what is read back, never the file.

What was measured, in memory and under `python -I`, on the 112 containers of
brushes/library as committed (72 user files, 40 official sets); nothing was
extracted to disk:

  - Listed with `png_info`: all 2,003 PNG members, with no error. Every one is
    8 bits per sample and not interlaced: colour type 0 for shapes, grains and
    the six named in-folder textures of Earth (`GL-Palm-Shape.png` and the
    like) (901), colour type 6 for
    thumbnails, author pictures and signatures (1,081), colour type 4 for the
    thumbnails of the two version-4 sets, Earth and Chinese Calligraphy (21).
  - Decoded with `read_png`: the 1,931 shape, grain, named-texture and
    thumbnail members, which are 1,603 distinct files (author pictures and
    signatures were left alone). The pure decoder read 1,603 of 1,603 with
    no error; its pixels equal PIL 12.3.0's for 1,603 of 1,603 (PIL loaded
    from its own folder for the comparison); the PIL path of this module gave
    the same Image as the pure path for 1,603 of 1,603. Each image, written
    back with `write_png` and read again, gave the same pixels (1,603). Time
    on this machine: about 11 minutes for the 1,603 on the pure path (a
    2048x2048 grey takes a few seconds, a thumbnail well under one), against
    41 seconds with PIL undoing the filters.
  - Colour profiles: 549 of 573 shapes and 296 of 322 grains carry an iCCP
    chunk, a grey profile (`kCGColorSpaceGenericGrayGamma2_2`, 3,315 or 3,332
    bytes, or `ICC Profile`, 3,294 bytes); the rest, Chinese Calligraphy's
    among them (`IHDR, eXIf, IDAT, IEND`), carry none. No thumbnail carries
    one.
  - Thumbnails: of the 1,001 `QuickLook/Thumbnail.png` members, 984 are
    1060x324 (9 are 440x276, 8 are 327x100), 985 carry `sRGB` with intent 0
    and 992 carry `pHYs` (2835, 2835, 1); the chunk lists are `IHDR, sRGB,
    pHYs, iTXt, IDAT, IEND` (606), the same with `eXIf` after `sRGB` (370),
    `IHDR, eXIf, pHYs, iTXt, IDAT, IEND` (16, Earth's grey+alpha ones) and
    `IHDR, sRGB, IDAT, IEND` (9). Of the 985 distinct thumbnails (`Reset/`
    ones included), 924 are exactly "255 wherever alpha is above 0, 0
    elsewhere" (923 RGBA, 1 grey+alpha). The other 61 (41 RGBA, 20
    grey+alpha) are not, and none is coloured: red, green and blue are equal
    in every RGBA one. So the ink of a stored thumbnail is its alpha channel
    (`alpha_plane`), as F6 says, and not its colour. `write_thumbnail` gave
    back the exact pixels of all 923 RGBA thumbnails of the exact form.
  - `write_thumbnail` writes `IHDR, sRGB, pHYs, IDAT, IEND`: the two cheap
    chunks with the observed values, and not the `iTXt` chunk (an XMP packet)
    or `eXIf`.
  - Not measured on a real file, because the library has none: images of 1, 2,
    4 or 16 bits, palette images, tRNS chunks and interlaced images. Those
    paths are held by synthetic tests, and compared with PIL where PIL can be
    imported.
  - Not known: whether the drawing app accepts a PNG written here (filter 0,
    no `iTXt`, no `eXIf`, no `iDOT`, no `iCCP` unless one is passed). Nothing
    written by this module has been opened in it.

Standard library only (PIL optional, as above). Not a command.
"""

from __future__ import annotations

import io
import os
import struct
import sys
import warnings
import zlib
from array import array
from collections import Counter
from itertools import accumulate
from typing import NamedTuple

from bplist import CodecError, LimitExceeded, PngError, PngUnsupported

SIGNATURE = b"\x89PNG\r\n\x1a\n"

# mode -> samples per pixel. An Image is always 8 bits per sample.
MODES = {"L": 1, "LA": 2, "RGB": 3, "RGBA": 4}
COLOR_TYPES = {"L": 0, "LA": 4, "RGB": 2, "RGBA": 6}

MAX_PIXELS = 8192 * 8192          # spec.yaml format.caps.png_pixels
MAX_CHUNKS = 100_000              # chunks walked in one file before it is refused (the most seen is 241)

THUMBNAIL_SIZE = (1060, 324)
THUMBNAIL_SRGB_INTENT = 0
THUMBNAIL_PHYS = (2835, 2835, 1)  # pixels per metre, both ways: 72 per inch

ENV_NO_PIL = "ROSW_BRUSHES_NO_PIL"

# colour type -> samples per pixel in the file, and the bit depths it may have.
_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
_DEPTHS = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
_ADAM7 = ((0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2))

_CHUNK_HEAD = struct.Struct(">I4s")
_U32 = struct.Struct(">I")
_IHDR = struct.Struct(">IIBBBBB")
_PHYS = struct.Struct(">IIB")

# The byte of a native 64-bit word that holds its low eight bits.
_LOW_BYTE = 0 if sys.byteorder == "little" else 7

_NEGATE = bytes(255 - value for value in range(256))
_NONZERO = bytes(255 if value else 0 for value in range(256))
_IS_FULL = bytes(255 if value == 255 else 0 for value in range(256))

# The integer form of ITU-R 601 luma, the weights PIL's "L" conversion uses.
# They sum to 65536, so a grey stored as RGB keeps its value exactly.
_LUMA = (19595, 38470, 7471)


# ── errors ───────────────────────────────────────────────────────────────────

class PngLimitExceeded(PngError, LimitExceeded):
    """An image of more pixels than the cap. `code` is `png_pixels`.

    A PngError, so that one `except` covers everything a reader here raises,
    and the codec's LimitExceeded, which is what docs/CONTRACTS.md says a cap
    raises.
    """


# ── the image ────────────────────────────────────────────────────────────────

class Image(NamedTuple):
    """Decoded pixels: 8 bits per sample, rows from the top, no padding.

    `mode` is L, LA, RGB or RGBA. `chunks` names the chunks of the file the
    image was read from, in file order, with a run of IDAT chunks written
    once; it is empty for an image made here.
    """

    width: int
    height: int
    mode: str
    pixels: bytes
    chunks: tuple = ()

    @property
    def channels(self):
        return MODES[self.mode]

    @property
    def size(self):
        return (self.width, self.height)


def _checked(img, *modes):
    """`img` if it is a sound Image (of one of `modes`, when any are named)."""
    if not isinstance(img, Image):
        raise PngError("bad_image", f"an Image is needed, not {type(img).__name__}")
    if img.mode not in MODES or (modes and img.mode not in modes):
        wanted = " or ".join(modes) if modes else "L, LA, RGB or RGBA"
        raise PngError("bad_image", f"mode {img.mode!r} is not {wanted}")
    if not isinstance(img.pixels, bytes):
        raise PngError("bad_image", f"the pixels of an Image are bytes, not {type(img.pixels).__name__}")
    if img.width < 1 or img.height < 1 or len(img.pixels) != img.width * img.height * MODES[img.mode]:
        raise PngError("bad_image", f"{len(img.pixels)} bytes are not a {img.width}x{img.height} {img.mode} image")
    return img


def _planes(img):
    count = MODES[img.mode]
    return [img.pixels] if count == 1 else [img.pixels[index::count] for index in range(count)]


def _interleave(planes):
    if len(planes) == 1:
        return bytes(planes[0])
    out = bytearray(len(planes[0]) * len(planes))
    for index, plane in enumerate(planes):
        out[index::len(planes)] = plane
    return bytes(out)


# ── PIL, when it is there ────────────────────────────────────────────────────

def _load_pil():
    if os.environ.get(ENV_NO_PIL, "").strip() not in ("", "0"):
        return None
    try:
        from PIL import Image as pil_image
    except Exception:                 # absent, or present and broken: the pure path either way
        return None
    return pil_image


_PIL = _load_pil()
HAVE_PIL = _PIL is not None


def _pil_pixels(data, mode, width, height):
    """The samples as PIL decodes them, or None when PIL fails or sees another image."""
    if _PIL is None:
        return None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with _PIL.open(io.BytesIO(data)) as picture:
                if picture.format != "PNG" or picture.mode != mode or picture.size != (width, height):
                    return None
                pixels = picture.tobytes()
    except Exception:                 # whatever PIL raises, the pure decoder gives the answer or the typed error
        return None
    return pixels if len(pixels) == width * height * MODES[mode] else None


# ── reading: structure ───────────────────────────────────────────────────────

class _Header(NamedTuple):
    width: int
    height: int
    depth: int
    color: int
    interlace: int


def _scan(data):
    """(data as bytes, header, [(name, offset, length)], bytes after IEND).

    Walks every chunk up to IEND, checking each length and CRC, and reads the
    header. Nothing is inflated.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise PngError("not_png", f"PNG data must be bytes, not {type(data).__name__}")
    data = bytes(data)
    if data[:len(SIGNATURE)] != SIGNATURE:
        raise PngError("not_png", "the PNG signature is missing")
    view = memoryview(data)
    end = len(data)
    position = len(SIGNATURE)
    chunks = []
    while True:
        if end - position < 12:
            raise PngError("truncated", f"the file ends inside a chunk header at byte {position}")
        length, kind = _CHUNK_HEAD.unpack_from(data, position)
        if not kind.isalpha():
            raise PngError("bad_chunk", f"a chunk type that is not four letters at byte {position}")
        if length > 0x7FFFFFFF or position + 12 + length > end:
            raise PngError("truncated", f"the {kind.decode('ascii')} chunk at byte {position} runs past "
                                        "the end of the file")
        (crc,) = _U32.unpack_from(data, position + 8 + length)
        if zlib.crc32(view[position + 4:position + 8 + length]) != crc:
            raise PngError("crc", f"the {kind.decode('ascii')} chunk at byte {position} fails its CRC")
        name = kind.decode("ascii")
        if not chunks and (name != "IHDR" or length != _IHDR.size):
            raise PngError("bad_header", "the first chunk is not a 13-byte IHDR")
        chunks.append((name, position + 8, length))
        position += 12 + length
        if name == "IEND":
            break
        if len(chunks) >= MAX_CHUNKS:
            raise PngError("too_many_chunks", f"more than {MAX_CHUNKS:,} chunks")
    width, height, depth, color, compression, filtering, interlace = _IHDR.unpack_from(data, chunks[0][1])
    if not (1 <= width <= 0x7FFFFFFF and 1 <= height <= 0x7FFFFFFF):
        raise PngError("bad_header", f"an image of {width}x{height} pixels")
    if color not in _DEPTHS or depth not in _DEPTHS[color]:
        raise PngError("bad_header", f"colour type {color} with {depth} bits per sample")
    if compression != 0 or filtering != 0 or interlace not in (0, 1):
        raise PngError("bad_header", f"compression {compression}, filter method {filtering}, "
                                     f"interlace {interlace}")
    return data, _Header(width, height, depth, color, interlace), chunks, end - position


def _names(chunks):
    """Chunk names in file order, a run of IDAT written once."""
    names = []
    for name, _, _ in chunks:
        if name == "IDAT" and names and names[-1] == "IDAT":
            continue
        names.append(name)
    return tuple(names)


def _mode(color, has_trns):
    if color == 0:
        return "LA" if has_trns else "L"
    if color in (2, 3):
        return "RGBA" if has_trns else "RGB"
    return "LA" if color == 4 else "RGBA"


def png_info(data):
    """What a PNG says about itself, without inflating its image data.

    Returns a dict: `width`, `height`, `bit_depth`, `color_type`, `interlace`
    (0 or 1) from the header; `mode`, the mode `read_png` returns for such a
    file; `has_alpha`; `chunks`, the chunk names in file order with a run of
    IDAT written once; `idat_chunks` and `idat_bytes`, how the compressed
    data is held; `trailing_bytes`, what follows IEND and is ignored.

    The signature, every chunk length and every CRC are checked, and a bad one
    raises PngError. The pixel cap is not applied: this is how a caller says
    how large a refused image is.
    """
    _, header, chunks, trailing = _scan(data)
    names = _names(chunks)
    mode = _mode(header.color, "tRNS" in names)
    return {
        "width": header.width, "height": header.height,
        "bit_depth": header.depth, "color_type": header.color, "interlace": header.interlace,
        "mode": mode, "has_alpha": mode in ("LA", "RGBA"),
        "chunks": list(names),
        "idat_chunks": sum(1 for name, _, _ in chunks if name == "IDAT"),
        "idat_bytes": sum(length for name, _, length in chunks if name == "IDAT"),
        "trailing_bytes": trailing,
    }


def get_chunks(data, *kinds):
    """[(name, body)] for every chunk of `data` whose name is in `kinds`, in file order.

    For carrying a chunk of one file into another: the iCCP chunk of a shape
    that is being replaced, say. The file is checked as `png_info` checks it.
    """
    data, _, chunks, _ = _scan(data)
    return [(name, data[offset:offset + length]) for name, offset, length in chunks if name in kinds]


def _layout(data, header, chunks):
    """(palette or None, tRNS body or None, [IDAT bodies]) after the order rules."""
    view = memoryview(data)
    palette = trns = None
    idat = []
    closed = False
    for name, offset, length in chunks[1:]:
        if name == "IDAT":
            if closed:
                raise PngError("chunk_order", "the IDAT chunks are not one run")
            idat.append(view[offset:offset + length])
            continue
        if idat:
            closed = True
        if name == "IHDR":
            raise PngError("chunk_order", "a second IHDR chunk")
        if name == "PLTE":
            if palette is not None or idat:
                raise PngError("chunk_order", "a PLTE chunk that is second, or after the image data")
            if length == 0 or length % 3 or length > 768:
                raise PngError("bad_palette", f"a palette of {length} bytes")
            palette = data[offset:offset + length]
        elif name == "tRNS":
            if trns is not None or idat:
                raise PngError("chunk_order", "a tRNS chunk that is second, or after the image data")
            if header.color == 3 and palette is None:
                raise PngError("chunk_order", "a tRNS chunk before the palette")
            trns = data[offset:offset + length]
        elif name != "IEND" and name[0].isupper():
            raise PngUnsupported("critical_chunk", f"the critical chunk {name} is not one this reader knows")
    if not idat:
        raise PngError("no_image_data", "there is no IDAT chunk")
    if header.color == 3:
        if palette is None:
            raise PngError("bad_palette", "a palette image with no PLTE chunk")
        if trns is not None and len(trns) > len(palette) // 3:
            raise PngError("bad_trns", "more tRNS entries than palette entries")
    elif header.color in (4, 6):
        trns = None               # the image has its own alpha; a stray tRNS is ignored
    elif trns is not None and len(trns) != (2 if header.color == 0 else 6):
        raise PngError("bad_trns", f"a tRNS chunk of {len(trns)} bytes for colour type {header.color}")
    return palette, trns, idat


class _Pass(NamedTuple):
    """One block of the image data: the whole image, or one Adam7 pass of it.

    The block is `down` rows of `across` pixels, each row `row` bytes behind
    its filter byte, and starts `start` bytes into the inflated data. Its
    pixel (i, j) is pixel (x0 + i * dx, y0 + j * dy) of the image.
    """

    x0: int
    y0: int
    dx: int
    dy: int
    across: int
    down: int
    row: int
    start: int


def _passes(header):
    """The blocks the inflated image data is made of, in file order: one, or
    the non-empty passes of Adam7."""
    bits = _CHANNELS[header.color] * header.depth
    grid = _ADAM7 if header.interlace else ((0, 0, 1, 1),)
    out = []
    start = 0
    for x0, y0, dx, dy in grid:
        across = (header.width - x0 + dx - 1) // dx
        down = (header.height - y0 + dy - 1) // dy
        if across > 0 and down > 0:
            row = (across * bits + 7) // 8
            out.append(_Pass(x0, y0, dx, dy, across, down, row, start))
            start += down * (row + 1)
    return out


def _raw_size(header):
    """(bytes in one filtered row of the image without its filter byte, bytes
    the image data inflates to)."""
    bits = _CHANNELS[header.color] * header.depth
    last = _passes(header)[-1]
    return (header.width * bits + 7) // 8, last.start + last.down * (last.row + 1)


def _inflate(idat, expected):
    """The image data, which must inflate to exactly `expected` bytes."""
    inflater = zlib.decompressobj()
    try:
        raw = inflater.decompress(b"".join(idat), expected + 1)
    except zlib.error as exc:
        raise PngError("bad_image_data", f"the image data does not inflate: {exc}") from None
    if len(raw) > expected:
        raise PngError("image_data_long", f"the image data inflates past the {expected:,} bytes the header gives")
    if len(raw) < expected:
        raise PngError("image_data_short", f"the image data inflates to {len(raw):,} bytes, "
                                           f"and the header gives {expected:,}")
    return raw


# ── reading: the row filters ─────────────────────────────────────────────────
# Each filter works on the byte one pixel to the left, so a row of `step`
# bytes per pixel is `step` independent rows of one byte per pixel. The lane
# functions below are written for that one-byte case.

def _running(values):
    """Prefix sums modulo 256: the Sub filter undone for one lane."""
    return array("Q", accumulate(values)).tobytes()[_LOW_BYTE::8]


def _average_lane(values, above):
    out = bytearray(len(values))
    left = 0
    index = 0
    for value, up in zip(values, above):
        left = (value + ((left + up) >> 1)) & 255
        out[index] = left
        index += 1
    return out


def _paeth_lane(values, above):
    out = bytearray(len(values))
    left = corner = 0
    index = 0
    for value, up in zip(values, above):
        if up == corner:              # flat above: the predictor is the left neighbour
            left = (value + left) & 255
        elif left == corner:          # flat to the left: the predictor is the one above
            left = (value + up) & 255
        else:
            by_left = up - corner
            by_up = left - corner
            by_corner = by_left + by_up
            if by_left < 0:
                by_left = -by_left
            if by_up < 0:
                by_up = -by_up
            if by_corner < 0:
                by_corner = -by_corner
            if by_left <= by_up and by_left <= by_corner:
                left = (value + left) & 255
            elif by_up <= by_corner:
                left = (value + up) & 255
            else:
                left = (value + corner) & 255
        out[index] = left
        index += 1
        corner = up
    return out


def _by_lane(lane_function, step, line, *others):
    if step == 1:
        return lane_function(line, *others)
    out = bytearray(len(line))
    for lane in range(step):
        out[lane::step] = lane_function(line[lane::step], *(other[lane::step] for other in others))
    return out


def _check_filters(raw, block):
    """Every filter byte of one block is a filter type, 0 to 4."""
    worst = max(raw[block.start:block.start + block.down * (block.row + 1):block.row + 1])
    if worst > 4:
        raise PngError("bad_filter", f"a row with filter type {worst}")


def _unfilter(raw, row, step):
    """The rows of `raw` with their filters undone and their filter bytes gone."""
    types = raw[0::row + 1]
    if not any(types):
        out = bytearray(raw)
        del out[0::row + 1]
        return bytes(out)
    blank = bytes(row)
    low_bits = int.from_bytes(b"\x7f" * row, "little")
    high_bits = int.from_bytes(b"\x80" * row, "little")
    rows = []
    above = blank
    position = 1
    for kind in types:
        line = raw[position:position + row]
        position += row + 1
        if kind == 0:
            current = line
        elif kind == 2:
            # Add two rows byte by byte with no carry between bytes: the low
            # seven bits of each pair are summed, then the top bits put back.
            a = int.from_bytes(line, "little")
            b = int.from_bytes(above, "little")
            current = (((a & low_bits) + (b & low_bits)) ^ ((a ^ b) & high_bits)).to_bytes(row, "little")
        elif line == blank and (kind == 1 or above == blank):
            current = blank           # nothing added to nothing
        elif kind == 1:
            current = _by_lane(_running, step, line)
        elif kind == 3:
            current = _by_lane(_average_lane, step, line, above)
        else:
            current = _by_lane(_paeth_lane, step, line, above)
        rows.append(current)
        above = current
    return b"".join(rows)


# ── reading: samples to an 8-bit mode ────────────────────────────────────────

def _bit_tables(depth):
    """For each sample position in a byte, the table that takes the byte to that sample."""
    mask = (1 << depth) - 1
    return [bytes((value >> shift) & mask for value in range(256))
            for shift in range(8 - depth, -1, -depth)]


def _unpack(samples, header, row):
    """Samples of 1, 2 or 4 bits as one byte each, unscaled, row padding dropped."""
    planes = [samples.translate(table) for table in _bit_tables(header.depth)]
    spread = _interleave(planes)
    per_row = row * len(planes)
    if per_row == header.width:
        return spread
    return b"".join(spread[start:start + header.width] for start in range(0, len(spread), per_row))


def _key_alpha(lanes, key):
    """255 where a pixel differs from the transparent colour in any byte, 0 where it is that colour."""
    size = len(lanes[0])
    if key is None:
        return b"\xff" * size
    match = None
    for lane, wanted in zip(lanes, key):
        only = bytes(255 if value == wanted else 0 for value in range(256))
        hit = int.from_bytes(lane.translate(only), "little")
        match = hit if match is None else match & hit
    return match.to_bytes(size, "little").translate(_NEGATE)


def _palette_pixels(indexes, palette, trns):
    entries = len(palette) // 3
    if max(indexes) >= entries:
        raise PngError("bad_palette", f"a pixel names palette entry {max(indexes)} of {entries}")
    pad = bytes(256 - entries)
    planes = [indexes.translate(palette[channel::3] + pad) for channel in range(3)]
    if trns is not None:
        planes.append(indexes.translate(trns + b"\xff" * (256 - len(trns))))
    return _interleave(planes)


def _to_mode(samples, header, row, palette, trns):
    """Unfiltered samples as the pixels of the Image mode."""
    depth, color = header.depth, header.color
    if depth < 8:
        values = _unpack(samples, header, row)
        if color == 3:
            return _palette_pixels(values, palette, trns)
        grey = values.translate(bytes((value * (255 // ((1 << depth) - 1))) & 255 for value in range(256)))
        if trns is None:
            return grey
        key = [trns[1]] if trns[0] == 0 and trns[1] < (1 << depth) else None
        return _interleave([grey, _key_alpha([values], key)])
    if color == 3:
        return _palette_pixels(samples, palette, trns)
    wide = depth // 8
    pixels = samples if wide == 1 else samples[0::2]
    if trns is None:
        return pixels
    channels = _CHANNELS[color]
    step = channels * wide
    if wide == 2:
        key = list(trns)
    else:
        key = list(trns[1::2]) if not any(trns[0::2]) else None
    alpha = _key_alpha([samples[lane::step] for lane in range(step)], key)
    return _interleave([pixels[channel::channels] for channel in range(channels)] + [alpha])


def _decode(raw, header, blocks, palette, trns, mode):
    """The pixels of the Image, by the standard library, from checked image data."""
    step = max(1, _CHANNELS[header.color] * header.depth // 8)
    if not header.interlace:
        return _to_mode(_unfilter(raw, blocks[0].row, step), header, blocks[0].row, palette, trns)
    # Adam7: each pass is a small image of its own, filtered on its own rows.
    # Decode each one, then lay its pixels into the whole image at their places.
    count = MODES[mode]
    line = header.width * count
    out = bytearray(line * header.height)
    for block in blocks:
        part = raw[block.start:block.start + block.down * (block.row + 1)]
        small = header._replace(width=block.across, height=block.down, interlace=0)
        pixels = _to_mode(_unfilter(part, block.row, step), small, block.row, palette, trns)
        span = block.across * count
        for j in range(block.down):
            first = (block.y0 + j * block.dy) * line + block.x0 * count
            source = pixels[j * span:(j + 1) * span]
            for channel in range(count):
                out[first + channel:first - block.x0 * count + line:block.dx * count] = source[channel::count]
    return bytes(out)


def read_png(data, *, max_pixels=MAX_PIXELS):
    """Decode a PNG to an Image (module docstring: what is read, and the caps).

    Raises PngLimitExceeded (a PngError and a LimitExceeded) for more than
    `max_pixels` pixels, PngUnsupported for a critical chunk this reader does
    not know, PngError for anything else that is wrong with the bytes.
    """
    data, header, chunks, _ = _scan(data)
    if header.width * header.height > max_pixels:
        raise PngLimitExceeded("png_pixels", f"{header.width}x{header.height} is more than {max_pixels:,} pixels")
    palette, trns, idat = _layout(data, header, chunks)
    names = _names(chunks)
    _, expected = _raw_size(header)
    raw = _inflate(idat, expected)
    blocks = _passes(header)
    for block in blocks:
        _check_filters(raw, block)
    mode = _mode(header.color, trns is not None)
    by_pil = (HAVE_PIL and header.depth == 8 and header.color != 3 and "tRNS" not in names
              and "acTL" not in names)
    pixels = _pil_pixels(data, mode, header.width, header.height) if by_pil else None
    if pixels is None:
        pixels = _decode(raw, header, blocks, palette, trns, mode)
    return Image(header.width, header.height, mode, pixels, names)


# ── writing ──────────────────────────────────────────────────────────────────

def _chunk(kind, body):
    return _U32.pack(len(body)) + kind + body + _U32.pack(zlib.crc32(kind + body))


def _dimension(value, what):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 0x7FFFFFFF:
        raise PngError("bad_image", f"the {what} must be a whole number of pixels from 1 up, not {value!r}")
    return value


def write_png(width, height, mode, pixels, *, level=6, chunks=()):
    """The bytes of an 8-bit PNG: not interlaced, filter 0 on every row, one IDAT.

    mode      L, LA, RGB or RGBA; `pixels` is width * height * samples bytes.
    level     the zlib level, 0 to 9.
    chunks    (name, body) pairs written between IHDR and IDAT, in the order
              given. Ancillary chunks only (a lower-case first letter): an
              iCCP chunk taken from another file, an sRGB or pHYs chunk.

    The chunk list is IHDR, the supplied chunks, IDAT, IEND. Raises PngError
    for arguments that do not describe an image.
    """
    if mode not in MODES:
        raise PngError("bad_image", f"mode {mode!r} is not L, LA, RGB or RGBA")
    _dimension(width, "width")
    _dimension(height, "height")
    if not isinstance(pixels, (bytes, bytearray, memoryview)):
        raise PngError("bad_image", f"pixels must be bytes, not {type(pixels).__name__}")
    pixels = bytes(pixels)
    row = width * MODES[mode]
    if len(pixels) != row * height:
        raise PngError("bad_image", f"{len(pixels):,} bytes are not a {width}x{height} {mode} image "
                                    f"({row * height:,} bytes)")
    if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 9:
        raise PngError("bad_image", f"the zlib level is 0 to 9, not {level!r}")
    extra = []
    for item in chunks:
        try:
            kind, body = item
            kind = kind.encode("ascii") if isinstance(kind, str) else bytes(kind)
            body = bytes(body)
        except (TypeError, ValueError):
            raise PngError("bad_chunk", f"a supplied chunk is (name, body), not {item!r}") from None
        if len(kind) != 4 or not kind.isalpha() or not kind[:1].islower():
            raise PngError("bad_chunk", f"only an ancillary chunk may be supplied, not {kind!r}")
        extra.append(_chunk(kind, body))
    # Filter type 0 before every row: one zero byte, then the row as it is.
    raw = b"\x00" + b"\x00".join(pixels[start:start + row] for start in range(0, len(pixels), row))
    header = _IHDR.pack(width, height, 8, COLOR_TYPES[mode], 0, 0, 0)
    return b"".join([SIGNATURE, _chunk(b"IHDR", header), *extra,
                     _chunk(b"IDAT", zlib.compress(raw, level)), _chunk(b"IEND", b"")])


def write_thumbnail(alpha, width=THUMBNAIL_SIZE[0], height=THUMBNAIL_SIZE[1]):
    """A stroke thumbnail in the form the drawing app stores: white on clear.

    `alpha` is width * height bytes of coverage, rows from the top. The result
    is an RGBA PNG with straight alpha: red, green and blue are 255 wherever
    alpha is above 0 and 0 where it is 0. Chunks: IHDR, sRGB (intent 0),
    pHYs (2835, 2835, 1), IDAT, IEND.
    """
    _dimension(width, "width")
    _dimension(height, "height")
    if not isinstance(alpha, (bytes, bytearray, memoryview)):
        raise PngError("bad_image", f"alpha must be bytes, not {type(alpha).__name__}")
    alpha = bytes(alpha)
    if len(alpha) != width * height:
        raise PngError("bad_image", f"{len(alpha):,} bytes of alpha are not {width}x{height} "
                                    f"({width * height:,} bytes)")
    white = alpha.translate(_NONZERO)
    return write_png(width, height, "RGBA", _interleave([white, white, white, alpha]),
                     chunks=(("sRGB", bytes((THUMBNAIL_SRGB_INTENT,))), ("pHYs", _PHYS.pack(*THUMBNAIL_PHYS))))


# ── pixels: channels and polarity ────────────────────────────────────────────

def alpha_plane(img):
    """The alpha channel as an L image, or None for a mode without one."""
    _checked(img)
    if img.mode not in ("LA", "RGBA"):
        return None
    return Image(img.width, img.height, "L", img.pixels[MODES[img.mode] - 1::MODES[img.mode]])


def _luma(img):
    if img.mode == "L":
        return img.pixels
    if img.mode == "LA":
        return img.pixels[0::2]
    step = MODES[img.mode]
    red, green, blue = (img.pixels[channel::step] for channel in range(3))
    if red == green == blue:
        return red
    by_red, by_green, by_blue = ([value * weight for value in range(256)] for weight in _LUMA)
    return bytes([(by_red[r] + by_green[g] + by_blue[b] + 32768) >> 16 for r, g, b in zip(red, green, blue)])


def luminance(img):
    """The brightness of each pixel as an L image, alpha ignored.

    An RGB pixel is (19595 R + 38470 G + 7471 B + 32768) >> 16, the integer
    form of the 601 weights; a grey one is itself.
    """
    _checked(img)
    return Image(img.width, img.height, "L", _luma(img))


def negative(img):
    """255 - v on every colour sample. Alpha is left as it is."""
    _checked(img)
    planes = _planes(img)
    colours = len(planes) - (1 if img.mode in ("LA", "RGBA") else 0)
    planes = [plane.translate(_NEGATE) if index < colours else plane for index, plane in enumerate(planes)]
    return Image(img.width, img.height, img.mode, _interleave(planes))


def _white_where_seen(values, alpha):
    """True when `values` is 255 at every pixel whose alpha is not 0."""
    seen = int.from_bytes(alpha.translate(_NONZERO), "little")
    return seen & int.from_bytes(values.translate(_IS_FULL), "little") == seen


def _ground_table(ink, ground):
    """For each alpha, `ink` laid over `ground` at that alpha."""
    return bytes((ink * a + ground * (255 - a) + 127) // 255 for a in range(256))


def _over(values, alpha, ground):
    """(v * a + ground * (255 - a) + 127) // 255 for each pixel of one channel."""
    if alpha.count(255) == len(alpha):
        return values
    if _white_where_seen(values, alpha):
        return alpha.translate(_ground_table(255, ground))
    back = [ground * (255 - a) + 127 for a in range(256)]
    return bytes([(v * a + back[a]) // 255 for v, a in zip(values, alpha)])


def to_gray8(img, *, invert=False):
    """An image as 8-bit grey: luminance times alpha, over black.

    `invert=True` takes 255 - luminance first, so that a mark drawn dark on
    light comes out light on dark; what is transparent is black either way.
    A thumbnail that is white wherever alpha is not 0 comes out as its alpha
    channel; for the ink of a stored thumbnail take `alpha_plane` itself, since
    some real ones are a few levels short of white.
    """
    _checked(img)
    grey = _luma(img)
    if invert:
        grey = grey.translate(_NEGATE)
    if img.mode in ("LA", "RGBA"):
        grey = _over(grey, img.pixels[MODES[img.mode] - 1::MODES[img.mode]], 0)
    return Image(img.width, img.height, "L", bytes(grey))


def flatten(img, background=0):
    """Lay an image with alpha over a flat background; the result has no alpha.

    L and LA give L, RGB and RGBA give RGB. `background` is one level for
    every channel, or (r, g, b) for a colour image. Each sample is
    (v * a + background * (255 - a) + 127) // 255. An image without alpha
    comes back with its own pixels.
    """
    _checked(img)
    colours = 1 if img.mode in ("L", "LA") else 3
    if isinstance(background, (tuple, list)):
        grounds = list(background)
    else:
        grounds = [background] * colours
    if len(grounds) != colours or any(isinstance(g, bool) or not isinstance(g, int) or not 0 <= g <= 255
                                      for g in grounds):
        raise PngError("bad_image", f"a background for a {img.mode} image is one level from 0 to 255, "
                                    f"or one per colour channel, not {background!r}")
    planes = _planes(img)
    if len(planes) == colours:
        return Image(img.width, img.height, img.mode, img.pixels)
    alpha = planes[-1]
    out = [_over(plane, alpha, ground) for plane, ground in zip(planes, grounds)]
    return Image(img.width, img.height, "L" if colours == 1 else "RGB", _interleave(out))


def flatten_ink(ink, background=26, foreground=255):
    """Coverage drawn as `foreground` on `background`: an L image in, an L image out.

    Each value a becomes (foreground * a + background * (255 - a) + 127) // 255.
    With the defaults that is 26 + (229 * a + 127) // 255, the stroke preview's
    light ink on a dark ground.
    """
    _checked(ink, "L")
    for level in (background, foreground):
        if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 255:
            raise PngError("bad_image", f"a level is 0 to 255, not {level!r}")
    return Image(ink.width, ink.height, "L", ink.pixels.translate(_ground_table(foreground, background)))


# ── pixels: geometry ─────────────────────────────────────────────────────────

def crop(img, left, top, width, height):
    """The width x height part of an image whose top-left pixel is (left, top)."""
    _checked(img)
    if not (0 <= left and 0 <= top and width >= 1 and height >= 1
            and left + width <= img.width and top + height <= img.height):
        raise PngError("bad_image", f"a {width}x{height} crop at ({left}, {top}) does not lie inside "
                                    f"{img.width}x{img.height}")
    if (left, top, width, height) == (0, 0, img.width, img.height):
        return Image(img.width, img.height, img.mode, img.pixels)
    step = MODES[img.mode]
    row = img.width * step
    first = left * step
    return Image(width, height, img.mode, b"".join(
        img.pixels[y * row + first:y * row + first + width * step] for y in range(top, top + height)))


def tile_crop(img, left, top, width, height):
    """A crop whose coordinates wrap round the image, so the image repeats.

    Any `left` and `top`, negative included, and any size: with the image
    larger than the crop this is a plain crop, and with it smaller the image
    is tiled. `tile_crop(img, (img.width - w) // 2, (img.height - h) // 2, w, h)`
    is the centre of a large image, or a small one tiled about its centre.
    """
    _checked(img)
    if width < 1 or height < 1:
        raise PngError("bad_image", f"a crop of {width}x{height}")
    step = MODES[img.mode]
    row = img.width * step
    start = (left % img.width) * step
    repeats = width // img.width + 2
    made = {}
    rows = []
    for y in range(top, top + height):
        source = y % img.height
        if source not in made:
            line = img.pixels[source * row:(source + 1) * row]
            made[source] = (line[start:] + line * repeats)[:width * step]
        rows.append(made[source])
    return Image(width, height, img.mode, b"".join(rows))


def center_on(img, width, height, fill=0):
    """An image centred on a width x height canvas of `fill`.

    A side of the image longer than the canvas is cropped about its centre.
    When the space left over is odd, the extra pixel goes right and below.
    `fill` is one level for every channel, or one per channel.
    """
    _checked(img)
    if width < 1 or height < 1:
        raise PngError("bad_image", f"a canvas of {width}x{height}")
    step = MODES[img.mode]
    fills = list(fill) if isinstance(fill, (tuple, list)) else [fill] * step
    if len(fills) != step or any(isinstance(f, bool) or not isinstance(f, int) or not 0 <= f <= 255
                                 for f in fills):
        raise PngError("bad_image", f"a fill for a {img.mode} image is one level from 0 to 255, "
                                    f"or one per channel, not {fill!r}")
    keep_w, keep_h = min(img.width, width), min(img.height, height)
    part = crop(img, (img.width - keep_w) // 2, (img.height - keep_h) // 2, keep_w, keep_h)
    if (keep_w, keep_h) == (width, height):
        return part
    pixel = bytes(fills)
    left, top = (width - keep_w) // 2, (height - keep_h) // 2
    before, after = pixel * left, pixel * (width - keep_w - left)
    blank = pixel * width
    row = keep_w * step
    rows = [blank] * top
    rows += [before + part.pixels[start:start + row] + after for start in range(0, len(part.pixels), row)]
    rows += [blank] * (height - keep_h - top)
    return Image(width, height, img.mode, b"".join(rows))


def fit_factor(width, height, box_width, box_height):
    """The whole-number reduction that brings width x height inside a box:
    max(1, ceil(max(width / box_width, height / box_height)))."""
    if min(width, height, box_width, box_height) < 1:
        raise PngError("bad_image", "a size is at least 1x1")
    return max(1, -(-width // box_width), -(-height // box_height))


def _reduce_plane(plane, width, height, factor):
    """One channel reduced by box means. Returns (bytes, out width, out height)."""
    out_w, out_h = -(-width // factor), -(-height // factor)
    # Sum a block's pixels as lanes of one big integer: every `factor`-th
    # pixel of a row, widened so that the sums cannot carry into a neighbour.
    lane = 4 if 255 * factor * factor < 1 << 32 else 8
    code = "I" if lane == 4 else "Q"
    low = 0 if sys.byteorder == "little" else lane - 1
    last_w = width - (out_w - 1) * factor
    wide = bytearray(out_w * lane)
    out = bytearray()
    for out_y in range(out_h):
        first = out_y * factor
        rows = min(factor, height - first)
        total = 0
        for y in range(first, first + rows):
            base = y * width
            for dx in range(min(factor, width)):
                part = plane[base + dx:base + width:factor]
                if len(part) != out_w:
                    part += bytes(out_w - len(part))      # the last block is narrower than the rest
                wide[low::lane] = part
                total += int.from_bytes(wide, sys.byteorder)
        sums = memoryview(total.to_bytes(out_w * lane, sys.byteorder)).cast(code)
        count = factor * rows
        half = count // 2
        values = [(block + half) // count for block in sums]
        if last_w != factor:
            count = last_w * rows
            values[-1] = (sums[-1] + count // 2) // count
        out += bytes(values)
    return bytes(out), out_w, out_h


def box_reduce(img, factor):
    """An image reduced by a whole number: each factor x factor block becomes its mean.

    The mean of n pixels is (sum + n // 2) // n. The result is ceil(width /
    factor) by ceil(height / factor); a block cut short by the right or bottom
    edge is the mean of the pixels it does hold. Channels are averaged one by
    one, alpha included and not as a weight, so flatten an image with alpha
    (or take one plane of it) before reducing it.
    """
    _checked(img)
    if isinstance(factor, bool) or not isinstance(factor, int) or factor < 1:
        raise PngError("bad_image", f"a reduction factor is a whole number from 1 up, not {factor!r}")
    if factor == 1:
        return Image(img.width, img.height, img.mode, img.pixels)
    reduced = [_reduce_plane(plane, img.width, img.height, factor) for plane in _planes(img)]
    return Image(reduced[0][1], reduced[0][2], img.mode, _interleave([plane for plane, _, _ in reduced]))


# ── pixels: measures and contrast ────────────────────────────────────────────

def histogram(img):
    """How many pixels of an L image hold each value: a list of 256 counts."""
    _checked(img, "L")
    counts = Counter(img.pixels)
    return [counts.get(value, 0) for value in range(256)]


def bbox(img, threshold=0):
    """(left, top, right, bottom) round the values above `threshold` in an L image.

    `right` and `bottom` are one past the last such pixel. None when no value
    is above the threshold.
    """
    _checked(img, "L")
    mask = img.pixels.translate(bytes(1 if value > threshold else 0 for value in range(256)))
    first = mask.find(1)
    if first < 0:
        return None
    top, bottom = first // img.width, mask.rfind(1) // img.width + 1
    columns = 0
    for y in range(top, bottom):
        columns |= int.from_bytes(mask[y * img.width:(y + 1) * img.width], "big")
    across = columns.to_bytes(img.width, "big")
    return (across.find(1), top, across.rfind(1) + 1, bottom)


def border_mean(img, ring=1):
    """The mean value of the outer `ring` pixels of an L image, all four sides.

    An image too small to have an inside is all border. Used to tell which
    way round an image without alpha is drawn: a mean above 127 is a light
    ground.
    """
    _checked(img, "L")
    if isinstance(ring, bool) or not isinstance(ring, int) or ring < 1:
        raise PngError("bad_image", f"a ring is a whole number of pixels from 1 up, not {ring!r}")
    total, count = sum(img.pixels), img.width * img.height
    if img.width > 2 * ring and img.height > 2 * ring:
        inside = crop(img, ring, ring, img.width - 2 * ring, img.height - 2 * ring)
        total -= sum(inside.pixels)
        count -= inside.width * inside.height
    return total / count


class Stretched(NamedTuple):
    """`stretch` output: the image, and what was done to it."""

    image: Image
    hi: int            # the level that became 255
    gain: float        # 255 / hi: what every value was multiplied by, before the cut at 255
    peak: int          # the largest value in the image as it came
    nonzero: int       # how many pixels were above 0


def stretch(img, *, floor=16, permille=995):
    """Spread a faint L image over the whole range, and say by how much.

    hi = max(floor, the `permille`/1000 percentile, by nearest rank, of the
    values above 0); each value v becomes min(255, (v * 255 + hi // 2) // hi).
    With no value above 0, hi is `floor` and the image is unchanged. The gain
    applied is 255 / hi, reported with `hi` itself so that it can be restated
    exactly.
    """
    _checked(img, "L")
    if isinstance(floor, bool) or not isinstance(floor, int) or not 1 <= floor <= 255:
        raise PngError("bad_image", f"the floor is 1 to 255, not {floor!r}")
    if isinstance(permille, bool) or not isinstance(permille, int) or not 1 <= permille <= 1000:
        raise PngError("bad_image", f"the percentile is 1 to 1000 thousandths, not {permille!r}")
    counts = histogram(img)
    nonzero = len(img.pixels) - counts[0]
    peak = max((value for value in range(255, 0, -1) if counts[value]), default=0)
    hi = floor
    if nonzero:
        rank = (permille * nonzero + 999) // 1000
        seen = 0
        for value in range(1, 256):
            seen += counts[value]
            if seen >= rank:
                hi = max(floor, value)
                break
    table = bytes(min(255, (value * 255 + hi // 2) // hi) for value in range(256))
    return Stretched(Image(img.width, img.height, "L", img.pixels.translate(table)), hi, 255 / hi, peak, nonzero)
