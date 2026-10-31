"""Write a GIMP brush file (.gbr, version 2, greyscale) from a shape mask.

    data = gbr.write_gbr(width, height, mask, name="Hard Round")
    data = gbr.from_image(png_io.read_png(shape_png), inverted=False, name="Hard Round")

`mask` is coverage, one byte per pixel, rows from the top: 255 is full paint,
0 is none. The file holds those bytes as they are.

The layout (every number a 32-bit unsigned integer, most significant byte
first):

    bytes  0-3    header size: 28 + the length of the name with its final zero byte
    bytes  4-7    version: 2
    bytes  8-11   width
    bytes 12-15   height
    bytes 16-19   bytes per pixel: 1 (greyscale)
    bytes 20-23   magic: "GIMP"
    bytes 24-27   spacing, a percentage of the brush width
    bytes 28-     the name, UTF-8, ending in one zero byte
    then          width * height bytes, row by row

Which way round the mask is. In the file, 255 is paint. Source: GIMP's own
code, on the master branch at gitlab.gnome.org/GNOME/gimp, read as raw files
through page fetches (not from a checkout, so no commit is pinned):

  - app/core/gimpbrush-header.h: the seven big-endian fields above ("All
    field entries are MSB"), GIMP_BRUSH_MAGIC, GIMP_BRUSH_MAX_SIZE 10000 and
    GIMP_BRUSH_MAX_NAME 256, and "next comes the brush name,
    null-terminated", then width * height * bytes of data.
  - app/core/gimpbrush-load.c (gimp_brush_load_brush) reads the body of a
    1-byte brush straight into the brush mask with no change, and for a
    4-byte (RGBA) brush copies each alpha byte into the same mask and the
    colour into a separate pixmap. The mask is therefore opacity: 255 is
    opaque, that is, full paint. It refuses a name longer than
    GIMP_BRUSH_MAX_NAME bytes counting the zero byte, and does not check
    the spacing.
  - app/core/gimpbrush-save.c writes the mask straight out, with
    `header_size = sizeof (GimpBrushHeader) + strlen (name) + 1`, version
    2, bytes 1 for a mask alone, and the name written with its zero byte.
  - app/file-data/file-data-gbr.c, which turns an open grey image into a
    brush and back, inverts in both directions (`m[i] = 255 - m[i]`, under
    the comment "invert"): in a GIMP image a grey brush is drawn black on
    white, and in the file it is stored as coverage.

Confidence: high for the layout and for "255 is paint", because both come from
the loader's and saver's source. Not verified by opening a file: no GIMP and no
.gbr, .gih or .vbr file was found on this machine (Program Files, AppData,
Downloads, Documents, ProgramData), so nothing written here has been loaded by
GIMP. The check that would settle it is one export of a hard round shape: it
must show as a solid disc in GIMP's brush list, not as a square with a hole.

A shape image of a brush archive is the same way round when `shapeInverted` is
false: white is paint (CONTRACTS.md F3; the design's fidelity review observed
`shapeInverted ? 255 - v : v` on 391 shapes; not measured again here).
`from_image` takes the image and that flag and makes the coverage with
`png_io.to_gray8`: luminance, inverted when the flag is set, times alpha.

Spacing is a parameter and nothing here works it out. The default, 10, is the
default of GIMP's own "export as brush" procedure (app/file-data/file-data.c,
procedure file-gbr-export-internal, argument `spacing`: 1 to 1000, default
10), not a value taken from a brush archive: how the archive's spacing setting
maps to a percentage of the brush width has not been measured, so no such
conversion is offered (the design's `round(100*sqrt(2)*plotSpacing)` rests on
a guessed constant and is not used). GIMP's loader stores whatever the header
says; this writer keeps to the 1 to 1000 its export procedure accepts.

Limits, from app/core/gimpbrush-header.h: a side of at most 10,000 pixels
(GIMP_BRUSH_MAX_SIZE) and a name of at most 256 bytes with its zero byte
(GIMP_BRUSH_MAX_NAME). A longer name is cut at a character boundary; a larger
mask is refused.

Standard library only. Not a command.
"""

from __future__ import annotations

import struct
from typing import NamedTuple

from bplist import CodecError
import png_io

MAGIC = b"GIMP"
VERSION = 2
HEADER_BYTES = 28
BYTES_GREY = 1

SPACING_MIN, SPACING_MAX = 1, 1000
SPACING_DEFAULT = 10              # GIMP's export default; not derived from any brush setting

MAX_SIDE = 10_000                 # GIMP_BRUSH_MAX_SIZE
MAX_NAME_BYTES = 255              # GIMP_BRUSH_MAX_NAME is 256 with the final zero byte
DEFAULT_NAME = "Untitled"

_HEADER = struct.Struct(">II II I 4s I")


class GbrError(CodecError):
    """A mask, a name or a spacing that cannot be written as a brush, or bytes that are not one."""


class Gbr(NamedTuple):
    """What `read_gbr` returns. `depth` is bytes per pixel: 1 grey, 4 RGBA."""

    width: int
    height: int
    depth: int
    spacing: int
    name: str
    pixels: bytes


def _name_bytes(name):
    if not isinstance(name, str):
        raise GbrError("gbr_name", f"a brush name is text, not {type(name).__name__}")
    if "\x00" in name:
        raise GbrError("gbr_name", "a brush name may not hold a zero character")
    try:
        encoded = name.encode("utf-8")
    except UnicodeEncodeError:
        raise GbrError("gbr_name", "a brush name must be writable as UTF-8") from None
    if len(encoded) > MAX_NAME_BYTES:
        # Cut on a character boundary: a continuation byte is 10xxxxxx.
        cut = MAX_NAME_BYTES
        while cut and (encoded[cut] & 0xC0) == 0x80:
            cut -= 1
        encoded = encoded[:cut]
    return encoded


def write_gbr(width, height, mask, *, name=DEFAULT_NAME, spacing=SPACING_DEFAULT):
    """The bytes of a version 2 greyscale .gbr file.

    mask      width * height bytes of coverage, rows from the top; 255 is full
              paint. Written as given.
    name      the brush name GIMP shows. Kept as given, cut to 255 bytes of UTF-8.
    spacing   the spacing field: a whole percentage of the brush width, 1 to
              1000. The caller chooses it.

    Raises GbrError for a size outside 1 to 10,000, a mask of the wrong
    length, a name with a zero character, or a spacing out of range.
    """
    for value, what in ((width, "width"), (height, "height")):
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= MAX_SIDE:
            raise GbrError("gbr_size", f"the {what} of a brush is 1 to {MAX_SIDE:,} pixels, not {value!r}")
    if not isinstance(mask, (bytes, bytearray, memoryview)):
        raise GbrError("gbr_mask", f"a mask is bytes, not {type(mask).__name__}")
    mask = bytes(mask)
    if len(mask) != width * height:
        raise GbrError("gbr_mask", f"{len(mask):,} bytes are not a {width}x{height} mask ({width * height:,} bytes)")
    if isinstance(spacing, bool) or not isinstance(spacing, int) or not SPACING_MIN <= spacing <= SPACING_MAX:
        raise GbrError("gbr_spacing", f"spacing is a whole number from {SPACING_MIN} to {SPACING_MAX}, "
                                      f"not {spacing!r}")
    encoded = _name_bytes(name) + b"\x00"
    header = _HEADER.pack(HEADER_BYTES + len(encoded), VERSION, width, height, BYTES_GREY, MAGIC, spacing)
    return header + encoded + mask


def from_image(img, *, inverted=False, name=DEFAULT_NAME, spacing=SPACING_DEFAULT):
    """A .gbr file from a decoded shape image.

    `inverted` is the brush's `shapeInverted`: false when white is paint in
    the image, true when black is. The coverage is the image's luminance
    (255 - luminance when inverted) times its alpha, so a transparent pixel
    never paints.
    """
    try:
        grey = png_io.to_gray8(img, invert=bool(inverted))
    except png_io.PngError as exc:
        raise GbrError("gbr_mask", exc.detail) from None
    return write_gbr(grey.width, grey.height, grey.pixels, name=name, spacing=spacing)


def read_gbr(data):
    """Read back a version 2 .gbr file: Gbr(width, height, depth, spacing, name, pixels).

    For checking what was written. It reads the two depths GIMP writes (1 and
    4 bytes per pixel) and nothing older than version 2; `pixels` is the body
    as stored. Raises GbrError for anything else.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise GbrError("gbr_data", f"a brush file is bytes, not {type(data).__name__}")
    data = bytes(data)
    if len(data) < HEADER_BYTES:
        raise GbrError("gbr_data", "the file is shorter than a brush header")
    header_size, version, width, height, depth, magic, spacing = _HEADER.unpack_from(data)
    if magic != MAGIC or version != VERSION:
        raise GbrError("gbr_data", f"not a version {VERSION} GIMP brush (version {version}, magic {magic!r})")
    if not (1 <= width <= MAX_SIDE and 1 <= height <= MAX_SIDE) or depth not in (1, 4):
        raise GbrError("gbr_data", f"a brush of {width}x{height} with {depth} bytes per pixel")
    name_size = header_size - HEADER_BYTES
    if not 1 <= name_size <= MAX_NAME_BYTES + 1 or header_size > len(data):
        raise GbrError("gbr_data", f"a header size of {header_size}")
    raw_name = data[HEADER_BYTES:header_size]
    if raw_name[-1:] != b"\x00" or b"\x00" in raw_name[:-1]:
        raise GbrError("gbr_data", "the name does not end in exactly one zero byte")
    try:
        name = raw_name[:-1].decode("utf-8")
    except UnicodeDecodeError:
        raise GbrError("gbr_data", "the name is not UTF-8") from None
    body = data[header_size:]
    if len(body) != width * height * depth:
        raise GbrError("gbr_data", f"{len(body):,} bytes of pixels for a {width}x{height} brush "
                                   f"of {depth} byte(s) per pixel")
    return Gbr(width, height, depth, spacing, name, body)
