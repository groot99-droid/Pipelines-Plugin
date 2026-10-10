"""Synthetic brush files for the brushes tests.

Every test builds its data here, in a temporary folder. No test reads the real
library, the real catalog or the real vault, and the writers below refuse a
target inside the real brushes/ folder.

This module is an independent oracle. It imports nothing from brushes/pipeline:
archives are written with plistlib, images with zlib and struct, containers
with zipfile. So a test that reads a fixture through the code under test is
comparing two implementations, not one with itself.

What a fixture is, and is not:

  - A fixture archive has the SHAPE of a brush archive: the keyed-archiver
    envelope, the object order, the class chains, the curve and roll objects,
    and a real era's key names. It is not byte-identical to anything the
    drawing app wrote: plistlib stores every real as eight bytes and shares
    objects by its own rule. Byte-exact vectors belong to the codec's own tests.
  - The seven legacy key sets (E0 to E4) are the documented ones, by name.
    The values are made up.
  - The modern key set is reconstructed from the documented inventory of the
    220-key era. Twenty-seven of its names (the `...Tilt` and `...TiltAngle`
    keys) are spelled from a pattern and have not been compared with a real
    file: MODERN_KEYS_VERIFIED says so. Do not assert that a modern fixture is
    detected as M220 until that flag is true.
  - Images are a few pixels across. `make_png` writes stored (uncompressed)
    deflate blocks by default, so its bytes are the same on every platform and
    every zlib build. Zip bytes are NOT stable across platforms: never pin them.

Standard library only.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import plistlib
import shutil
import struct
import tempfile
import unittest
import uuid
import warnings
import zipfile
import zlib
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
BRUSHES = PIPELINE.parent
REPO = BRUSHES.parent

ENV_PREFIX = "ROSW_BRUSHES_"


# ── temporary folders ────────────────────────────────────────────────────────

def refuse_real(target):
    """Raise if `target` is inside the real brushes/ folder. Returns the path."""
    resolved = Path(target).resolve()
    real = BRUSHES.resolve()
    if resolved == real or real in resolved.parents:
        raise ValueError(f"fixtures write to temporary folders only, not into {real}")
    return resolved


def temp_dir(case, prefix="brushes-test-"):
    """A fresh temporary folder, removed when the test case ends."""
    path = Path(tempfile.mkdtemp(prefix=prefix)).resolve()
    case.addCleanup(shutil.rmtree, path, ignore_errors=True)
    return path


def clean_env(case):
    """Hide every ROSW_BRUSHES_* variable for the length of one test."""
    kept = {k: v for k, v in os.environ.items() if not k.upper().startswith(ENV_PREFIX)}
    patcher = mock.patch.dict(os.environ, kept, clear=True)
    patcher.start()
    case.addCleanup(patcher.stop)


def tree_digest(folder):
    """One sha256 over every file under `folder`: path, then bytes. Equal before
    and after means nothing was written, renamed or removed."""
    folder = Path(folder)
    digest = hashlib.sha256()
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        digest.update(path.relative_to(folder).as_posix().encode("utf-8") + b"\x00")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


class BrushCase(unittest.TestCase):
    """A test case with a temporary data root and no ROSW_BRUSHES_* variables."""

    def setUp(self):
        super().setUp()
        clean_env(self)
        self.tmp = temp_dir(self)


# ── PNG ──────────────────────────────────────────────────────────────────────

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# mode -> (PNG colour type, samples per pixel); always 8 bits per sample.
PNG_MODES = {"L": (0, 1), "LA": (4, 2), "RGB": (2, 3), "RGBA": (6, 4)}
_MODE_OF_TYPE = {colour: mode for mode, (colour, _) in PNG_MODES.items()}


def _chunk(kind, body):
    return (struct.pack(">I", len(body)) + kind + body
            + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF))


def _zlib_stored(raw):
    """A zlib stream of stored blocks: the same bytes from every zlib build."""
    out = [b"\x78\x01"]
    blocks = [raw[i:i + 65535] for i in range(0, len(raw), 65535)] or [b""]
    for number, block in enumerate(blocks, start=1):
        out.append(struct.pack("<BHH", 1 if number == len(blocks) else 0,
                               len(block), len(block) ^ 0xFFFF))
        out.append(block)
    out.append(struct.pack(">I", zlib.adler32(raw) & 0xFFFFFFFF))
    return b"".join(out)


def soft_dot(width, height, seed=0):
    """A grey painter: a round mark, bright in the middle, on black."""
    cx, cy = (width - 1) / 2, (height - 1) / 2
    reach = max(min(width, height) / 2, 1)

    def paint(x, y):
        distance = math.hypot(x - cx, y - cy) / reach
        return max(0, min(255, int(round(255 * (1 - distance))) - (seed * 7) % 32))
    return paint


def speckle(seed=0):
    """A grey painter: repeatable noise, different for each seed."""
    def paint(x, y):
        value = (x * 73856093) ^ (y * 19349663) ^ ((seed + 1) * 83492791)
        return (value ^ (value >> 13)) * 1274126177 % 256
    return paint


def stroke_band(width, height, seed=0):
    """An RGBA painter in the form of a stored thumbnail: a white stroke on a
    clear background, 255 in the colour channels wherever alpha is not zero."""
    middle = (height - 1) / 2
    reach = max(height / 3, 1)

    def paint(x, y):
        wobble = math.sin((x + seed) / max(width, 1) * math.pi * 2) * height / 8
        distance = abs(y - middle - wobble) / reach
        alpha = max(0, min(255, int(round(200 * (1 - distance)))))
        return (255, 255, 255, alpha) if alpha else (0, 0, 0, 0)
    return paint


def make_png(width=8, height=8, mode="L", paint=None, *, compress=False, extra_chunks=()):
    """An 8-bit PNG: `mode` is L (grey), LA, RGB or RGBA.

    paint(x, y) returns one int for L and a tuple for the others; without it a
    soft dot (L), or a stroke band (RGBA), or mid-grey is drawn. Rows use
    filter 0. `compress=True` uses zlib.compress for a large image, at the cost
    of platform-dependent bytes. `extra_chunks` is a list of (4-byte type,
    body) written between IHDR and IDAT.
    """
    colour, samples = PNG_MODES[mode]
    if paint is None:
        if mode == "L":
            paint = soft_dot(width, height)
        elif mode == "RGBA":
            paint = stroke_band(width, height)
        else:
            paint = (lambda x, y: (128,) * samples)
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            value = paint(x, y)
            rows.extend((value,) if samples == 1 else value)
    if len(rows) != height * (1 + width * samples):
        raise ValueError(f"the painter does not return {samples} sample(s) per pixel")
    body = zlib.compress(bytes(rows), 9) if compress else _zlib_stored(bytes(rows))
    header = struct.pack(">IIBBBBB", width, height, 8, colour, 0, 0, 0)
    return (PNG_SIGNATURE + _chunk(b"IHDR", header)
            + b"".join(_chunk(kind, data) for kind, data in extra_chunks)
            + _chunk(b"IDAT", body) + _chunk(b"IEND", b""))


def read_png(data):
    """What a fixture PNG holds: a dict of width, height, mode, chunks and the
    raw samples. Reads what make_png writes (8-bit, filter 0, not interlaced)
    and checks every CRC; anything else raises ValueError."""
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG")
    position, chunks, header, packed = len(PNG_SIGNATURE), [], None, b""
    while position < len(data):
        length, kind = struct.unpack(">I4s", data[position:position + 8])
        body = data[position + 8:position + 8 + length]
        (crc,) = struct.unpack(">I", data[position + 8 + length:position + 12 + length])
        if crc != zlib.crc32(kind + body) & 0xFFFFFFFF:
            raise ValueError(f"bad CRC in {kind!r}")
        chunks.append(kind.decode("ascii"))
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            packed += body
        position += 12 + length
    width, height, depth, colour, _, _, interlace = header
    if depth != 8 or interlace or colour not in _MODE_OF_TYPE:
        raise ValueError("only 8-bit, non-interlaced grey, grey+alpha, RGB and RGBA")
    mode = _MODE_OF_TYPE[colour]
    stride = width * PNG_MODES[mode][1]
    raw = zlib.decompress(packed)
    if len(raw) != height * (stride + 1):
        raise ValueError("the image data has the wrong length")
    pixels = bytearray()
    for row in range(height):
        start = row * (stride + 1)
        if raw[start] != 0:
            raise ValueError("only filter 0 rows")
        pixels.extend(raw[start + 1:start + 1 + stride])
    return {"width": width, "height": height, "mode": mode, "chunks": chunks, "pixels": bytes(pixels)}


# ── archive keys ─────────────────────────────────────────────────────────────

LEGACY_ERAS = ("E0", "E1", "E1b", "E1c", "E2", "E3", "E4")
# Root key counts, `$class` included.
LEGACY_KEY_COUNTS = {"E0": 52, "E1": 61, "E1b": 62, "E1c": 63, "E2": 67, "E3": 88, "E4": 101}
MODERN_ERA = "M220"
MODERN_KEY_COUNT = 220
MODERN_KEYS_VERIFIED = False

CLASS_KEY = "$class"
BRUSH_CHAIN = ("SilicaBrush", "ValkyrieBrush", "NSObject")
BRUSH_CHAIN_E0 = ("SilicaBrush", "NSObject")
CURVE_CHAIN = ("ValkyrieMagnitudinalCurve", "NSObject")
MUTABLE_ARRAY_CHAIN = ("NSMutableArray", "NSArray", "NSObject")
ARRAY_CHAIN = ("NSArray", "NSObject")
ROLL_CHAIN = ("ValkyrieBrushRollParameters", "NSObject")
DATE_CHAIN = ("NSDate", "NSObject")
MUTABLE_STRING_CHAIN = ("NSMutableString", "NSString", "NSObject")

IDENTITY_CURVE = ("{0.000000, 0.000000}", "{1.000000, 1.000000}")
BLANK_GRAIN = "Brush-Preset-Blank.png"
BUNDLED_SHAPE = "Brush-Preset-Hard.png"
BUNDLED_GRAIN = "Brush-Preset-Stained-Paper-1.jpg"
# Seconds since 2001-01-01, fixed so that no fixture depends on the clock.
CREATED = 694224000.0

_CORE = (
    "bundledGrainPath", "bundledShapePath", "color", "dynamicsFalloff", "dynamicsGlazeFlow",
    "dynamicsJitterOpacity", "dynamicsJitterSize", "dynamicsLoad", "dynamicsMix",
    "dynamicsPressureOpacity", "dynamicsPressureSize", "dynamicsSpeedOpacity",
    "dynamicsSpeedSize", "dynamicsTiltAngle", "dynamicsTiltOpacity", "dynamicsTiltSize",
    "eraseOpacity", "eraseSize", "maxOpacity", "maxSize", "minOpacity", "minSize", "name",
    "oriented", "paintOpacity", "paintSize", "plotJitter", "plotSmoothing", "plotSpacing",
    "shapeAzimuth", "shapeInverted", "shapeOrientation", "shapeRandomise", "shapeRotation",
    "shapeScatter", "smudgeOpacity", "smudgeSize", "stamp", "taperEndLength", "taperOpacity",
    "taperSize", "taperStartLength", "textureFilter", "textureInverted", "textureMovement",
    "textureOrientation", "textureRotation", "textureScale", "textureZoom",
)
LEGACY_CURVES = ("dynamicsPressureOpacityCurve", "dynamicsPressureBleedCurve",
                 "dynamicsPressureSizeCurve")
# (first era, last era, keys). `$class` is in every era and is added by the builder.
_LEGACY_SPANS = (
    ("E0", "E4", _CORE),
    ("E0", "E0", ("dynamicsGlazeType",)),
    ("E0", "E2", ("dynamicsPressureSpeed",)),
    ("E1", "E4", ("version", "blendMode", "dynamicsRenderType", "previewSize",
                  "dynamicsPressureBleed", "dynamicsPressureMix", "dynamicsSmudgeAccumulation",
                  "dynamicsWetAccumulation", "dynamicsTiltBleed", "dynamicsTiltGradation")),
    ("E1b", "E4", ("dynamicsTiltCompression",)),
    ("E1c", "E4", ("dynamicsMixSoftening",)),
    ("E2", "E4", ("blendGammaCorrect", "shapeFilter", "shapeFilterMode", "textureFilterMode")),
    ("E3", "E4", LEGACY_CURVES + (
        "dynamicsPressureSizeSpeed", "dynamicsPressureOpacitySpeed", "dynamicsPressureBleedSpeed",
        "pencilTaperStartLength", "pencilTaperEndLength", "pencilTaperSize", "pencilTaperOpacity",
        "pencilTaperShape", "pencilTaperSizeLinked", "pencilTipAnimation", "taperPressure",
        "taperShape", "taperSizeLinked", "taperVersion", "dynamicsJitterHue",
        "dynamicsJitterSaturation", "dynamicsJitterLightness", "dynamicsJitterDarkness")),
    ("E3", "E3", ("dynamicsColorVariation",)),
    ("E4", "E4", ("extendedBlend", "dynamicsPressureSmoothing", "dynamicsJitterStrokeHue",
                  "dynamicsJitterStrokeSaturation", "dynamicsJitterStrokeLightness",
                  "dynamicsJitterStrokeDarkness", "dynamicsPressureHue",
                  "dynamicsPressureSaturation", "dynamicsPressureBrightness",
                  "dynamicsPressureSecondaryColor", "dynamicsTiltHue", "dynamicsTiltSaturation",
                  "dynamicsTiltBrightness", "dynamicsTiltSecondaryColor")),
)

# Legacy keys the modern era no longer carries. dynamicsGlazeFlow is renamed
# dynamicsGlazedFlow; the three rendering* booleans stand where
# dynamicsRenderType stood.
MODERN_DROPPED = ("dynamicsGlazeFlow", "dynamicsRenderType")

_TILT_BOOLS = ("attack", "darknessJitter", "hueJitter", "lightnessJitter", "plotJitter",
               "saturationJitter", "secondaryColorJitter", "shapeCount", "textureDepth")
_TILT_ANGLES = _TILT_BOOLS + ("bleed", "brightness", "gradation", "hue", "opacity", "saturation",
                              "secondaryColor", "shapeRoundness", "size")
# Names spelled from a documented pattern, not read from a file.
MODERN_UNVERIFIED_KEYS = (tuple(f"{stem}Tilt" for stem in _TILT_BOOLS)
                          + tuple(f"{stem}TiltAngle" for stem in _TILT_ANGLES))

_ROLL_STEMS = ("Size", "Opacity", "Bleed", "Hue", "Saturation", "Brightness", "SecondaryColor")
MODERN_SAVED = tuple(f"saved{tool}{what}" for tool in ("Paint", "Erase", "Smudge")
                     for what in ("Sizes", "Opacities"))
MODERN_BUNDLED = ("bundledShapePath", "bundledGrainPath", "bundledMetallicPath",
                  "bundledRoughnessPath", "bundledHeightPath")
# Modern curves and roll objects in the order the app archives them.
MODERN_CURVES = (
    "dynamicsPressureOpacityCurve", "dynamicsPressureSizeCurve",
    "dynamicsPressureShapeRoundnessCurve", "dynamicsPressureBleedCurve",
    "dynamicsPressureTransferModulationCurve", "dynamicsPressureHueCurve",
    "dynamicsPressureSaturationCurve", "dynamicsPressureBrightnessCurve",
    "dynamicsPressureSecondaryColorCurve",
)
MODERN_ROLLS_FIRST = ("shapeScatterRollParameters", "shapeCountRollParameters",
                      "plotJitterRollParameters")
MODERN_ROLLS_LAST = tuple(f"dynamicsRoll{stem}Parameters" for stem in _ROLL_STEMS) + (
    "attackRollParameters",)
_MODERN_NEW = (
    ("authorName", "creationDate", "importedFromABR", "plotSpacingVersion",
     "plotFFTSmoothingAmount", "plotFFTSmoothingBias", "plotMovingAverageStabilization",
     "shapeAngle", "shapeCount", "shapeCountJitter", "shapeRoundness", "shapeFlipXJitter",
     "shapeFlipYJitter", "dynamicsPressureShapeRoundness",
     "dynamicsPressureShapeRoundnessMinimum", "dynamicsTiltShapeRoundness",
     "dynamicsTiltShapeRoundnessMinimum", "grainDepth", "grainDepthMinimum", "grainDepthJitter",
     "grainBlendMode", "grainOrientation", "textureApplication", "textureBrightness",
     "textureContrast", "textureOffsetJitter", "texturizedGrainFollowsCamera",
     "renderingMaxTransfer", "renderingModulatedTransfer", "renderingRecursiveMixing",
     "dynamicsGlazedFlow", "wetEdgesAmount", "burntEdgesAmount", "burntEdgesBlendMode",
     "dualBlendMode", "dynamicsBlur", "dynamicsBlurJitter", "dynamicsWetnessJitter",
     "dynamicsPressureResponse", "dynamicsPressureOpacityTransfer", "paintPressure",
     "maxPressureSizeClamped", "jitterSecondary", "jitterStrokeSecondary",
     "attackRoll", "plotJitterRoll", "shapeCountRoll", "shapeScatterRoll", "shapeRoll",
     "shapeRollMode", "hoverFill", "hoverOutline", "hoverPressure", "metallicAmount",
     "metallicScale", "metallicGrainInverted", "roughnessAmount", "roughnessScale",
     "roughnessGrainInverted", "heightAmount", "heightScale", "bundledMetallicPath",
     "bundledRoughnessPath", "bundledHeightPath")
    + tuple(k for k in MODERN_CURVES if k not in LEGACY_CURVES)
    + MODERN_UNVERIFIED_KEYS
    + tuple(f"dynamicsRoll{stem}" for stem in _ROLL_STEMS)
    + MODERN_ROLLS_FIRST + MODERN_ROLLS_LAST + MODERN_SAVED
)

_BOOLS = frozenset((
    "oriented", "shapeAzimuth", "shapeInverted", "shapeRandomise", "stamp", "textureFilter",
    "textureInverted", "blendGammaCorrect", "shapeFilter", "pencilTaperSizeLinked",
    "pencilTipAnimation", "taperSizeLinked", "importedFromABR", "shapeFlipXJitter",
    "shapeFlipYJitter", "textureOffsetJitter", "texturizedGrainFollowsCamera",
    "renderingMaxTransfer", "renderingModulatedTransfer", "renderingRecursiveMixing",
    "maxPressureSizeClamped", "attackRoll", "plotJitterRoll", "shapeCountRoll",
    "shapeScatterRoll", "shapeRoll", "metallicGrainInverted", "roughnessGrainInverted",
) + tuple(f"{stem}Tilt" for stem in _TILT_BOOLS))
_INTS = frozenset((
    "shapeOrientation", "textureOrientation", "dynamicsGlazeType", "version", "blendMode",
    "dynamicsRenderType", "shapeFilterMode", "textureFilterMode", "taperVersion",
    "dynamicsColorVariation", "extendedBlend", "plotSpacingVersion", "grainBlendMode",
    "grainOrientation", "textureApplication", "burntEdgesBlendMode", "dualBlendMode",
    "shapeRollMode", "hoverFill", "hoverOutline",
))
_STRINGS = frozenset(MODERN_BUNDLED + ("name", "authorName"))
_DEFAULTS = {
    "dynamicsGlazeFlow": 1.0, "dynamicsGlazedFlow": 1.0, "dynamicsLoad": 0.5, "dynamicsMix": 0.5,
    "eraseOpacity": 1.0, "eraseSize": 0.5, "maxOpacity": 1.0, "maxSize": 1.0,
    "paintOpacity": 1.0, "paintSize": 0.5, "plotSpacing": 0.1, "smudgeOpacity": 0.8,
    "smudgeSize": 0.5, "textureMovement": 1.0, "textureScale": 1.0, "textureZoom": 1.0,
    "oriented": False, "textureFilter": True, "shapeFilter": True, "pencilTipAnimation": True,
    "shapeOrientation": 1, "textureOrientation": 1, "dynamicsGlazeType": 1, "version": 2,
    "taperVersion": 1, "previewSize": 0.3, "dynamicsPressureSpeed": 0.3,
    "dynamicsSmudgeAccumulation": 0.75, "dynamicsWetAccumulation": 0.75,
    "dynamicsTiltCompression": 1.0, "dynamicsPressureSizeSpeed": 0.3,
    "dynamicsPressureOpacitySpeed": 0.3, "dynamicsPressureBleedSpeed": 0.3,
    "plotSpacingVersion": 1, "shapeRoundness": 1.0, "dynamicsPressureShapeRoundness": 1.0,
    "dynamicsPressureShapeRoundnessMinimum": 1.0, "dynamicsTiltShapeRoundness": 1.0,
    "dynamicsTiltShapeRoundnessMinimum": 1.0, "grainDepth": 1.0, "grainBlendMode": 1,
    "grainOrientation": 1, "textureOffsetJitter": True, "texturizedGrainFollowsCamera": True,
    "burntEdgesBlendMode": 1, "paintPressure": 1.0, "hoverPressure": 1.0, "metallicScale": 0.16,
    "roughnessScale": 0.16, "heightAmount": 0.5, "heightScale": 0.16,
}
_DEFAULTS.update({f"{stem}TiltAngle": 0.1 for stem in _TILT_ANGLES})


def _f32(value):
    """A real as the app stores it: rounded to a 32-bit float."""
    return struct.unpack(">f", struct.pack(">f", float(value)))[0]


def legacy_keys(era):
    """Every root key of a legacy era, `$class` included, sorted."""
    if era not in LEGACY_ERAS:
        raise ValueError(f"{era!r} is not one of {', '.join(LEGACY_ERAS)}")
    at = LEGACY_ERAS.index(era)
    keys = {CLASS_KEY}
    for first, last, names in _LEGACY_SPANS:
        if LEGACY_ERAS.index(first) <= at <= LEGACY_ERAS.index(last):
            keys.update(names)
    return sorted(keys)


def modern_keys():
    """The reconstructed 220-key modern set, `$class` included, sorted."""
    keys = set(legacy_keys("E4")) - set(MODERN_DROPPED)
    keys.update(_MODERN_NEW)
    return sorted(keys)


def keys_for(family="legacy", era=None):
    if family == "legacy":
        return legacy_keys(era or "E4")
    if family == "modern" and era in (None, MODERN_ERA):
        return modern_keys()
    raise ValueError(f"no fixture key set for family {family!r}, era {era!r}")


def kind_of(key):
    """How a fixture stores a key: real, int, bool, string, data, curve, roll,
    array or date."""
    if key in _BOOLS:
        return "bool"
    if key in _INTS:
        return "int"
    if key in _STRINGS:
        return "string"
    if key == "color":
        return "data"
    if key == "creationDate":
        return "date"
    if key.endswith("Curve"):
        return "curve"
    if key in MODERN_ROLLS_FIRST or key in MODERN_ROLLS_LAST:
        return "roll"
    if key in MODERN_SAVED:
        return "array"
    return "real"


def default_for(key):
    kind = kind_of(key)
    if key in _DEFAULTS:
        value = _DEFAULTS[key]
        return _f32(value) if kind == "real" else value
    return {"bool": False, "int": 0, "real": 0.0}.get(kind)


def point_string(x, y):
    return "{%.6f, %.6f}" % (x, y)


# ── archives ─────────────────────────────────────────────────────────────────

NIL = plistlib.UID(0)


class _Objects:
    """The `$objects` list of a keyed archive, numbered the way the app numbers
    it: an instance, then what it holds, then its class on first use."""

    def __init__(self):
        self.items = ["$null"]
        self._classes = {}

    def add(self, value):
        self.items.append(value)
        return plistlib.UID(len(self.items) - 1)

    def class_of(self, chain):
        if chain not in self._classes:
            self._classes[chain] = self.add({"$classname": chain[0], "$classes": list(chain)})
        return self._classes[chain]

    def string(self, text, wrapped=False):
        if text is None:
            return NIL
        if not wrapped:
            return self.add(text)
        holder = {}
        uid = self.add(holder)
        holder[CLASS_KEY] = self.class_of(MUTABLE_STRING_CHAIN)
        holder["NS.string"] = text
        return uid

    def curve(self, points, legacy):
        curve, array = {}, {}
        uid = self.add(curve)
        array_uid = self.add(array)
        array["NS.objects"] = [self.add(point) for point in points]
        array[CLASS_KEY] = self.class_of(MUTABLE_ARRAY_CHAIN)
        curve["points"] = array_uid
        if legacy:
            curve["resolution"] = 1024
        curve[CLASS_KEY] = self.class_of(CURVE_CHAIN)
        return uid

    def roll(self):
        roll = {}
        uid = self.add(roll)
        roll["activationFalloff"] = _f32(math.pi / 2)
        roll["activationOrigin"] = _f32(math.pi)
        roll[CLASS_KEY] = self.class_of(ROLL_CHAIN)
        roll["mode"] = 1
        roll["activationRange"] = _f32(math.pi)
        return uid

    def date(self, seconds):
        date = {}
        uid = self.add(date)
        date["NS.time"] = float(seconds)
        date[CLASS_KEY] = self.class_of(DATE_CHAIN)
        return uid

    def empty_array(self):
        array = {}
        uid = self.add(array)
        array["NS.objects"] = []
        array[CLASS_KEY] = self.class_of(ARRAY_CHAIN)
        return uid


def _points(spec):
    return tuple(p if isinstance(p, str) else point_string(*p) for p in spec)


def make_archive(family="legacy", name="Fixture Brush", overrides=None, *, era=None,
                 bundled_shape=None, bundled_grain=None, curves=None, author=None,
                 created=CREATED, color=bytes(16), wrap_name=False, extra_keys=None,
                 drop_keys=()):
    """The bytes of a Brush.archive, written with plistlib.

    family          "legacy" (era E0 to E4, default E4) or "modern" (the
                    reconstructed 220-key set)
    overrides       {key: value} for scalar keys of that key set; an unknown key
                    raises KeyError, so a typo cannot pass silently
    bundled_shape   a file name for bundledShapePath, or None for nil
    bundled_grain   the same for bundledGrainPath
    curves          {curve key: points}; a point is "{x, y}" text or an (x, y)
                    pair. Curves not named are the two-point identity
    author          modern only: authorName, or None for nil
    wrap_name       store the name as an NSMutableString instance
    extra_keys      {key: scalar} added to the root as keys no schema knows
    drop_keys       root keys to leave out
    """
    keys = keys_for(family, era)
    legacy = family == "legacy"
    era = era or ("E4" if legacy else MODERN_ERA)
    overrides = dict(overrides or {})
    curves = dict(curves or {})
    for key in list(overrides) + list(curves):
        if key not in keys:
            raise KeyError(f"{key} is not a key of the {era} fixture")

    objects = _Objects()
    root = {}
    objects.add(root)
    refs = {}
    strings = {"bundledShapePath": bundled_shape, "bundledGrainPath": bundled_grain,
               "authorName": author}

    def curve(key):
        refs[key] = objects.curve(_points(curves.get(key, IDENTITY_CURVE)), legacy)

    if legacy:
        refs["bundledShapePath"] = objects.string(bundled_shape)
        refs["bundledGrainPath"] = objects.string(bundled_grain)
        refs["color"] = objects.add(bytes(color))
        for key in LEGACY_CURVES:
            if key in keys:
                curve(key)
        refs["name"] = objects.string(name, wrap_name)
        chain = BRUSH_CHAIN_E0 if era == "E0" else BRUSH_CHAIN
    else:
        for key in MODERN_BUNDLED[:4]:
            refs[key] = objects.string(strings.get(key))
        shared = objects.empty_array()
        refs.update(dict.fromkeys(MODERN_SAVED, shared))
        refs["color"] = objects.add(bytes(color))
        for key in MODERN_ROLLS_FIRST:
            refs[key] = objects.roll()
        for key in MODERN_CURVES:
            curve(key)
        for key in MODERN_ROLLS_LAST:
            refs[key] = objects.roll()
        refs["name"] = objects.string(name, wrap_name)
        refs["authorName"] = objects.string(author)
        refs["creationDate"] = objects.date(created)
        refs["bundledHeightPath"] = NIL
        chain = BRUSH_CHAIN
    refs[CLASS_KEY] = objects.class_of(chain)

    for key in keys:
        if key in drop_keys:
            continue
        if key in refs:
            root[key] = refs[key]
        else:
            value = overrides.get(key, default_for(key))
            root[key] = _f32(value) if kind_of(key) == "real" else value
    for key, value in (extra_keys or {}).items():
        root[key] = value

    envelope = {"$version": 100000, "$archiver": "NSKeyedArchiver",
                "$top": {"root": plistlib.UID(1)}, "$objects": objects.items}
    order = (("$version", "$objects", "$archiver", "$top") if legacy
             else ("$version", "$archiver", "$top", "$objects"))
    return plistlib.dumps({key: envelope[key] for key in order},
                          fmt=plistlib.FMT_BINARY, sort_keys=False)


def read_archive(data):
    """A fixture archive as plain facts, read back with plistlib.

    Returns a dict: top_order, objects, root (the raw root dict, references
    still as plistlib.UID), keys (sorted), values (every root key resolved one
    level: a string, bytes, a number, or the referenced object), name,
    class_chain.
    """
    top = plistlib.loads(data)
    objects = top["$objects"]
    root = objects[top["$top"]["root"].data]

    def resolve(value):
        if isinstance(value, plistlib.UID):
            return None if value.data == 0 else objects[value.data]
        return value

    values = {key: resolve(value) for key, value in root.items()}
    name = values.get("name")
    if isinstance(name, dict):
        name = name.get("NS.string")
    return {"top_order": list(top), "objects": objects, "root": root, "keys": sorted(root),
            "values": values, "name": name, "class_chain": values[CLASS_KEY]["$classes"]}


# ── brush folders ────────────────────────────────────────────────────────────

ARCHIVE = "Brush.archive"
SHAPE = "Shape.png"
GRAIN = "Grain.png"
THUMBNAIL = "QuickLook/Thumbnail.png"
AUTHOR_PICTURE = "AuthorPicture/AuthorPicture.png"
SIGNATURE = "Signature/SignaturePicture.png"
SUB = "Sub01"
RESET = "Reset"
EMPTY = ".empty"
PLIST = "brushset.plist"
UUID_PATTERN = r"^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[0-9A-F]{4}-[0-9A-F]{12}$"


def brush_uuid(number):
    """A repeatable folder name in the app's form: an upper-case version-4 UUID."""
    return str(uuid.UUID(int=(number * 0x9E3779B97F4A7C15F39CC0605CEDC835) % (1 << 128),
                         version=4)).upper()


class Brush:
    """One synthetic brush folder.

    members      [(path inside the folder, bytes)] in the order they are zipped
    archive      the Brush.archive bytes
    shape, grain the image bytes the folder carries and the archive uses, or
                 None when the brush only names an image inside the app
    subs         [(archive, shape, grain)] for each secondary folder, in order
    shape_source "embedded" | "bundled"
    grain_source "embedded" | "bundled" | "blank" | "none"

    archive, shape, grain and subs are exactly what the identity formula takes.
    """

    def __init__(self, name, members, **facts):
        self.name = name
        self.members = list(members)
        self.family = facts["family"]
        self.era = facts["era"]
        self.uuid = facts["uuid"]
        self.archive = facts["archive"]
        self.shape = facts["shape"]
        self.grain = facts["grain"]
        self.subs = list(facts["subs"])
        self.shape_source = facts["shape_source"]
        self.grain_source = facts["grain_source"]
        self.bundled_shape = facts["bundled_shape"]
        self.bundled_grain = facts["bundled_grain"]

    def paths(self):
        return [path for path, _ in self.members]

    def member(self, path):
        """The bytes of the first member with that path, or None."""
        return next((data for name, data in self.members if name == path), None)

    def __repr__(self):
        return f"<fixture Brush {self.name!r} {self.era} {len(self.members)} members>"


def _texture(choice, role, seed, size):
    """(member name or None, image bytes or None, bundled name or None, source)."""
    paint = soft_dot(size, size, seed) if role == "shape" else speckle(seed)
    if isinstance(choice, (bytes, bytearray)):
        return (SHAPE if role == "shape" else GRAIN), bytes(choice), None, "embedded"
    if choice == "embedded":
        return (SHAPE if role == "shape" else GRAIN), make_png(size, size, "L", paint), None, "embedded"
    if choice == "named":
        # A texture kept in the folder under its own name, which the archive's
        # bundled path points at.
        name = f"GL-Fixture-{role.capitalize()}-{seed}.png"
        return name, make_png(size, size, "L", paint), name, "embedded"
    if choice == "bundled":
        return None, None, (BUNDLED_SHAPE if role == "shape" else BUNDLED_GRAIN), "bundled"
    if choice == "blank" and role == "grain":
        return None, None, BLANK_GRAIN, "blank"
    if choice == "none" and role == "grain":
        return None, None, None, "none"
    raise ValueError(f"{choice!r} is not a {role} choice")


def make_brush(name="Fixture Brush", family="legacy", *, era=None, number=1, shape="embedded",
               grain="embedded", thumbnail=True, dual=False, reset=False, author=False,
               empty=(), extras=(), overrides=None, size=8, **archive_options):
    """One brush folder, as an ordered member list plus what went into it.

    shape      "embedded" | "bundled" | "named" | PNG bytes
    grain      "embedded" | "bundled" | "blank" | "none" | "named" | PNG bytes
    thumbnail  True (a small RGBA stroke) | False | "LA" (grey with alpha) | PNG bytes
    dual       add a Sub01/ secondary brush with its own archive and shape
    reset      add a Reset/ copy (its archive differs in paintSize); with
               `dual`, also Reset/Sub01/
    author     add the author picture and signature (and, in a modern archive,
               an author name)
    empty      folders, relative to the brush folder, that get a zero-byte
               `.empty` member ("" is the brush folder itself)
    extras     [(path, bytes)] of members no reader knows
    number     varies the folder UUID and the pixels, so two brushes differ
    Other keywords go to make_archive.
    """
    shape_member, shape_bytes, bundled_shape, shape_source = _texture(shape, "shape", number, size)
    grain_member, grain_bytes, bundled_grain, grain_source = _texture(grain, "grain", number, size)
    if author and family == "modern":
        archive_options.setdefault("author", "Fixture Author")
    archive = make_archive(family, name, overrides, era=era, bundled_shape=bundled_shape,
                           bundled_grain=bundled_grain, **archive_options)
    members = [(ARCHIVE, archive)]
    if shape_member:
        members.append((shape_member, shape_bytes))
    if grain_member:
        members.append((grain_member, grain_bytes))
    if thumbnail is True:
        members.append((THUMBNAIL, make_png(53, 16, "RGBA", stroke_band(53, 16, number))))
    elif thumbnail == "LA":
        members.append((THUMBNAIL, make_png(
            53, 16, "LA", lambda x, y: (255, stroke_band(53, 16, number)(x, y)[3]))))
    elif isinstance(thumbnail, (bytes, bytearray)):
        members.append((THUMBNAIL, bytes(thumbnail)))
    if author:
        members.append((AUTHOR_PICTURE, make_png(6, 6, "RGBA", lambda x, y: (40, 90, 200, 255))))
        members.append((SIGNATURE, make_png(12, 4, "RGBA", lambda x, y: (0, 0, 0, 255 * (y == 2)))))
    subs = []
    if dual:
        sub_archive = make_archive(family, f"{name} Secondary", era=era, bundled_grain=BLANK_GRAIN)
        sub_shape = make_png(size, size, "L", soft_dot(size, size, number + 100))
        members += [(f"{SUB}/{ARCHIVE}", sub_archive), (f"{SUB}/{SHAPE}", sub_shape)]
        subs.append((sub_archive, sub_shape, None))
    if reset:
        size_key = {"paintSize": 0.25}
        reset_archive = make_archive(family, name, {**(overrides or {}), **size_key}, era=era,
                                     bundled_shape=bundled_shape, bundled_grain=bundled_grain,
                                     **archive_options)
        members.append((f"{RESET}/{ARCHIVE}", reset_archive))
        if shape_member:
            members.append((f"{RESET}/{shape_member}", shape_bytes))
        if grain_member:
            members.append((f"{RESET}/{grain_member}", grain_bytes))
        members.append((f"{RESET}/{THUMBNAIL}",
                        make_png(53, 16, "RGBA", stroke_band(53, 16, number + 50))))
        if dual:
            members += [(f"{RESET}/{SUB}/{ARCHIVE}", subs[0][0]),
                        (f"{RESET}/{SUB}/{SHAPE}", subs[0][1])]
    for folder in empty:
        members.append((f"{folder}/{EMPTY}" if folder else EMPTY, b""))
    members += [(path, bytes(data)) for path, data in extras]
    return Brush(name, members, family=family, era=era or ("E4" if family == "legacy" else MODERN_ERA),
                 uuid=brush_uuid(number), archive=archive, shape=shape_bytes, grain=grain_bytes,
                 subs=subs, shape_source=shape_source, grain_source=grain_source,
                 bundled_shape=bundled_shape, bundled_grain=bundled_grain)


# ── containers ───────────────────────────────────────────────────────────────

ZIP_DATE = (2019, 4, 1, 12, 0, 0)


def make_zip(entries, *, stored=()):
    """A zip built in memory from ordered (name, bytes) pairs.

    A name given twice is written twice, and a name is written exactly as
    given: on Windows zipfile would turn a backslash into a slash, so the name
    is put back after the entry object is made. `stored` names entries kept
    without compression (True for all of them); the rest are deflated. Like the
    app's own files, entries carry create_system 0 and no external attributes.
    """
    buffer = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)        # "Duplicate name"
        with zipfile.ZipFile(buffer, "w") as archive:
            for name, data in entries:
                info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
                info.filename = info.orig_filename = name
                info.create_system = 0
                keep = stored is True or name in stored
                info.compress_type = zipfile.ZIP_STORED if keep else zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
                info.external_attr = 0                      # writestr fills one in
    return buffer.getvalue()


def zip_entries(data):
    """[(name, bytes)] for every entry of a zip, in file order, duplicates kept.

    The name is the one stored in the file (`orig_filename`). zipfile's own
    `filename` has backslashes rewritten on Windows, so a reader that must
    refuse a backslash name has to look at `orig_filename` too.
    """
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return [(info.orig_filename, archive.read(info)) for info in archive.infolist()]


def brushset_plist(name, uuids, extra=None, binary=False):
    """The set's plist: `brushes` (folder names in display order), `name`, then
    any extra keys. XML unless `binary`."""
    content = {"brushes": list(uuids), "name": name}
    content.update(extra or {})
    return plistlib.dumps(content, fmt=plistlib.FMT_BINARY if binary else plistlib.FMT_XML,
                          sort_keys=False)


def brush_file(brush, *, stored=()):
    """A loose `.brush`: the folder's members at the root of a zip."""
    return make_zip(brush.members, stored=stored)


def brushset_file(name, brushes, *, plist_extra=None, binary_plist=False, plist_first=False,
                  zip_order=None, double_empty=False, stored=(), prefix=""):
    """A `.brushset`: one upper-case UUID folder per brush, and brushset.plist.

    plist_extra    extra plist keys, for example {"iconName": "..."}
    plist_first    put the plist first in the zip instead of last
    zip_order      the brushes in another zip order than the plist's (the plist
                   is the only display order)
    double_empty   write every `.empty` member twice, as one official set does
    stored         entry names kept uncompressed, or True for all
    prefix         a single top folder around everything, as a set zipped from
                   a file manager has (give it with its trailing slash)
    """
    brushes = list(brushes)
    plist = (prefix + PLIST, brushset_plist(name, [b.uuid for b in brushes], plist_extra,
                                           binary_plist))
    entries = [plist] if plist_first else []
    for brush in (zip_order or brushes):
        for path, data in brush.members:
            entry = (f"{prefix}{brush.uuid}/{path}", data)
            entries.append(entry)
            if double_empty and path.rsplit("/", 1)[-1] == EMPTY:
                entries.append(entry)
    if not plist_first:
        entries.append(plist)
    return make_zip(entries, stored=stored)


# ── inputs a reader must refuse or survive ───────────────────────────────────

LFS_POINTER = (b"version https://git-lfs.github.com/spec/v1\n"
               b"oid sha256:" + b"0" * 64 + b"\nsize 12345\n")


def hostile_files():
    """{file name: bytes} of containers no reader may trust.

    Each one is small. None may make a reader write outside its target, hang,
    or raise anything but its own documented error.
    """
    good = make_brush("Hostile Host", number=90)
    half = good.archive[:len(good.archive) // 2]
    string_top = plistlib.dumps("only a string", fmt=plistlib.FMT_BINARY)
    return {
        # Entry names that point outside the container.
        "traversal.brushset": make_zip(
            [(f"{good.uuid}/{path}", data) for path, data in good.members]
            + [("../outside.txt", b"x"), ("/absolute.txt", b"x"), ("C:\\drive.txt", b"x"),
               (f"{good.uuid}/../../climb.txt", b"x"),
               (PLIST, brushset_plist("Traversal", [good.uuid]))]),
        # The plist is a binary plist whose top object is a bare array.
        "bare-array-plist.brushset": make_zip(
            [(f"{good.uuid}/{path}", data) for path, data in good.members]
            + [(PLIST, plistlib.dumps([good.uuid], fmt=plistlib.FMT_BINARY))]),
        # The plist lists a folder the zip does not hold.
        "missing-folder.brushset": make_zip(
            [(f"{good.uuid}/{path}", data) for path, data in good.members]
            + [(PLIST, brushset_plist("Missing", [good.uuid, brush_uuid(91)]))]),
        # The archive's top object is a string, not the keyed-archiver envelope.
        "string-top-archive.brush": make_zip([(ARCHIVE, string_top)]),
        "wrong-magic.brush": make_zip([(ARCHIVE, b"not a property list at all")]),
        "truncated-archive.brush": make_zip([(ARCHIVE, half)]),
        "no-archive.brush": make_zip([(SHAPE, make_png())]),
        "empty.brushset": make_zip([]),
        "not-a-zip.brush": b"PK\x03\x04 this only starts like a zip",
        # A Git LFS pointer left where the real file should be.
        "lfs-pointer.brushset": LFS_POINTER,
    }


def ratio_bomb(megabytes=20):
    """A `.brush` whose Shape.png is `megabytes` of zeros that deflate to
    almost nothing. Built on demand: it costs a moment."""
    good = make_brush("Bomb", shape="bundled", grain="none", thumbnail=False, number=92)
    return make_zip([(ARCHIVE, good.archive), (SHAPE, bytes(megabytes * 1024 * 1024))])


# ── a small library on disk ──────────────────────────────────────────────────

USER_PACK = "demo-pack"
OFFICIAL_PACK = "demo-official"
USER_SET_NAME = "Demo Set "                 # the trailing space is part of the name
USER_SET_SLUG = "demo-set"
OFFICIAL_SET_NAME = "\u6d53\u58a8 Modern 1"   # a name with no ASCII form of its own
OFFICIAL_SET_SLUG = "demo-modern"


def standard_user_brushes():
    """The four brushes of the user set: an E4 with both images, an E3 that
    only names bundled images, an E0 with an accented name, and a second brush
    with the first one's name but other settings."""
    return [
        make_brush("Demo Inker", number=1),
        make_brush("Demo  Pencil", era="E3", number=2, shape="bundled", grain="blank"),
        make_brush("Broken Cont\u00e9", era="E0", number=3, grain="none"),
        make_brush("Demo Inker", number=4, overrides={"plotSpacing": 0.5, "stamp": True}),
    ]


def standard_official_brushes():
    """The three brushes of the official-style set: a dual brush with author
    files and a Reset tree; a brush with no thumbnail; and one with textures
    kept under their own names, `.empty` members, a grey+alpha thumbnail and a
    file no reader knows."""
    return [
        make_brush("Modern Dual", "modern", number=11, dual=True, reset=True, author=True),
        make_brush("Modern Plain", "modern", number=12, shape="bundled", grain="none",
                   thumbnail=False),
        make_brush("Modern Earth", "modern", number=13, shape="named", grain="named",
                   thumbnail="LA", empty=("", RESET),
                   extras=[("Extra/unknown.bin", b"\x00\x01unknown\xff")],
                   overrides={"version": 4}),
    ]


def standard_sources():
    """A manifest in the library/sources.json schema, for the synthetic library."""
    return {
        "schema": "rosw-brushes-sources/1",
        "packs": [{
            "id": USER_PACK, "kind": "vendor", "vendor": "Fixture Vendor",
            "product": "Demo Pack", "source_url": None,
            "licence_note": "synthetic test data", "redistribute": "yes",
            "publish_previews": True, "evidence": "written by the test fixtures",
            "match": ["Demo Pack/**", "**/Demo_Pack.zip", "Demo_Pack.zip"],
            "sets": {USER_SET_NAME: {"slug": USER_SET_SLUG, "title": "Demo Set"}},
        }],
        "official": {
            "host": "downloads.invalid", "base": "https://downloads.invalid/fixtures/",
            "index_page": "https://downloads.invalid/",
            "packs": [{"id": OFFICIAL_PACK, "kind": "official", "vendor": "Fixture Vendor",
                       "product": "Demo official sets", "licence_note": "synthetic test data",
                       "redistribute": "yes", "publish_previews": True}],
            "files": [],
        },
    }


def write_library(root):
    """Write the standard synthetic library under `root` and describe it.

        sources.json
        user/demo-pack/Demo_Set.brushset        four brushes
        user/demo-pack/Demo_Inker.brush         the set's first brush again, loose
        user/demo-pack/Loose_Marker.brush       a loose brush found nowhere else
        official/demo-official/demo-modern.brushset   three modern brushes

    Returns {"library", "sources", "user_set", "official_set", "loose",
    "files"}: the two sets as {"file", "name", "slug", "brushes"}, the loose
    brushes as [{"file", "brush", "duplicate"}], and every file written as
    {library-relative POSIX path: bytes}.
    """
    root = refuse_real(root)
    user = standard_user_brushes()
    official = standard_official_brushes()
    marker = make_brush("Loose Marker", era="E1b", number=5, grain="bundled")
    files = {
        f"user/{USER_PACK}/Demo_Set.brushset": brushset_file(USER_SET_NAME, user),
        f"user/{USER_PACK}/Demo_Inker.brush": brush_file(user[0]),
        f"user/{USER_PACK}/Loose_Marker.brush": brush_file(marker),
        f"official/{OFFICIAL_PACK}/{OFFICIAL_SET_SLUG}.brushset": brushset_file(
            OFFICIAL_SET_NAME, official, plist_extra={"iconName": "fixture-icon"},
            double_empty=True, stored=(f"{official[2].uuid}/{ARCHIVE}",)),
    }
    sources = standard_sources()
    official_path = f"official/{OFFICIAL_PACK}/{OFFICIAL_SET_SLUG}.brushset"
    sources["official"]["files"].append({
        "pack": OFFICIAL_PACK, "slug": OFFICIAL_SET_SLUG, "title": "Modern 1 (fixture)",
        "path": "Demo/demo-modern.brushset", "bytes": len(files[official_path]),
        "md5": hashlib.md5(files[official_path], usedforsecurity=False).hexdigest()})
    for relative, data in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    sources_path = root / "sources.json"
    with open(sources_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(sources, ensure_ascii=False, indent=2) + "\n")
    return {
        "library": root,
        "sources": sources_path,
        "user_set": {"file": f"user/{USER_PACK}/Demo_Set.brushset", "name": USER_SET_NAME,
                     "slug": USER_SET_SLUG, "brushes": user},
        "official_set": {"file": official_path, "name": OFFICIAL_SET_NAME,
                         "slug": OFFICIAL_SET_SLUG, "brushes": official},
        "loose": [{"file": f"user/{USER_PACK}/Demo_Inker.brush", "brush": user[0], "duplicate": True},
                  {"file": f"user/{USER_PACK}/Loose_Marker.brush", "brush": marker,
                   "duplicate": False}],
        "files": files,
    }
