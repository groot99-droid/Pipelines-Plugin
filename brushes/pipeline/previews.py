"""previews.py: the stroke, shape and grain preview images and the contact sheets
(docs/CONTRACTS.md F5 "Preview-derived fields", F6, F11 and F12).

    python -I brushes/pipeline/previews.py render                  a dry run: what would be made
    python -I brushes/pipeline/previews.py render --confirm        make it
    python -I brushes/pipeline/previews.py render --sheets-only    rebuild the contact sheets from the
                                                                   committed previews, no library needed

Flags of `render`: --only S (the brushes whose home set slug or pack id is S),
--force (measure and render again whatever the manifest says), --no-sheets,
--sheets-only, --stdlib (decode without PIL), --confirm (write; otherwise a dry
run, which touches neither the vault nor the catalog).

What it reads: the catalog (`ingest.py build` must have run), and, to make an
image, the original brush files of the library through container.py, the one
reader. Nothing is extracted to disk. Run it as `python -I`.

What it writes, and nothing else (F12):

  vault/_Previews/<home_set_slug>/<brush_id>.stroke.png         530x162, tracked
  vault/_Previews/_textures/<texture_id>.<n|i>.shape.png        256x256, tracked
  vault/_Previews/_textures/<texture_id>.grain.png              256x256, tracked
  vault/_Previews/manifest.json                                 tracked
  vault/_Previews/_sheets/<set_slug>/sheet-NN.png, sheets.json  802x1496, ignored
  vault/_Previews/_local/...                                    ignored: a pack whose
                                                                `publish_previews` is false
  catalog/thumbnails.json, and the tile paths and `stats` of catalog/textures.json
  the three preview-derived fields of each catalog/brushes/<id>.json and
  catalog.json, only through ingest.apply_preview_results

Every preview is 8-bit grey with no alpha, written by png_io.write_png.

What a stroke preview is (F6). The ink is the alpha channel of the brush file's
own QuickLook thumbnail (colour types 6 and 4); an image with no alpha uses its
luminance, inverted when the border mean is above 127. It is reduced by an
integer box mean to fit 530x162 and centred, stretched so that the 99.5th
percentile (nearest rank, floor 16) of the non-zero ink becomes 255, and
flattened on a dark ground: v = 26 + (229*ink + 127)//255. A thumbnail whose
ink is all zero (or that cannot be read) falls back to Reset/QuickLook/
Thumbnail.png (`reset-thumbnail`); with neither, a hatched placeholder reading
NO THUMBNAIL IN FILE is written (`none`). Nothing is ever drawn that the app did
not draw. The measures kept in thumbnails.json:

  alpha_max     the largest ink value in the thumbnail as stored
  alpha_hi      the level that became 255 (hi of the stretch, on the reduced tile)
  gain          255 / alpha_hi, to 4 places: the factor the stretch applied
  ink_fraction  the share of the 530x162 tile whose ink was above 8, to 4 places
  bbox          [left, top, right, bottom] of the tile's non-zero ink (right and
                bottom one past the last pixel)
  (a `none` entry has these five null)

A shape tile is the whole image (luminance times alpha over black, taken as
255 - v first when the brush says shapeInverted, so that white is always paint)
reduced by an integer box mean to fit 256x256 and centred on black. A grain tile
is the centre 256x256 at 1:1, tiled when the image is smaller, not inverted.
Pixel statistics are measured on the tiles (what the contract's facet rules
say), not on the whole image:

  shape: coverage (mean/255), aspect (bounding-box width over height of values
         above 16), midtone (share of 16 < v < 240 among v > 16), edge_touch
         (the mean of the one-pixel border ring over 255); aspect and midtone are
         null for a tile with nothing above 16
  grain: mean (mean/255), contrast (population standard deviation/255)

A texture the archive only names (source `bundled`) has no image in the file and
gets no tile and no statistics. A shape tile is made for each polarity some
brush uses (`n` not inverted, `i` inverted).

Determinism. No clock, no absolute path, every listing sorted, every number from
integer arithmetic or one correctly rounded float operation. The PNG encoder is
always the standard library's zlib at level 6 (PNG_LEVEL), whether or not PIL is
there: PIL is used only through png_io, as a faster decoder whose pixels are
identical to the pure ones (png_io's own guarantee), and `--stdlib` switches it
off. Deflate output can differ between zlib builds, so "no churn" never depends
on bytes: manifest.json records, for every output, the sha256 of its source, the
PREVIEW_VERSION and the sha256 of its pixels, and a file is rewritten only when
the source hash or the version changed or the file is missing (--force rewrites
what differs). A file whose new bytes equal the old is not written at all, so a
second run writes nothing.

Contact sheets (for the tagger): one column of 8 rows, 802x1496, background 16.
A cell is a 22 px label bar (`NN name  id`, a built-in 5x7 bitmap font at 2x),
the 530x162 stroke, and the shape and grain tiles at 128x128. A texture the
brush only names is drawn as a labelled stand-in. Sets without a note (a loose
pseudo-set none of whose brushes lives there) get no sheets.

Nothing is deleted: a file that no catalog row points to any more is reported
as an orphan and left where it is.

Exit codes: 0 ok (a clean dry run too), 1 failed (the catalog is out of step
with the library, a container cannot be read), 2 usage or environment (no
catalog, no library, an unknown --only).

Standard library only (PIL optional, through png_io).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brush_common as bc  # noqa: E402
import container  # noqa: E402
import identity  # noqa: E402
import ingest  # noqa: E402
import png_io  # noqa: E402
from bplist import CodecError  # noqa: E402

PREVIEW_VERSION = 1
PNG_LEVEL = 6                         # the zlib level of every preview file

STROKE_W, STROKE_H = 530, 162
TILE = 256
SHEET_TILE = 128
SHEET_W, SHEET_H = 802, 1496
SHEET_ROWS = 8
SHEET_PER_CALL = 2                    # spec.yaml tags.sheet.sheets_per_call: sheets one tagger call reads
CELL_W, CELL_H = 794, 186
LABEL_H = 22
BACKGROUND = 16
STROKE_GROUND, STROKE_INK = 26, 255
INK_FLOOR = 8                         # "ink over 8" for ink_fraction

THUMB_MAX_PIXELS = 4_000_000          # the stored thumbnails are 1060x324 at most
TEXTURE_MAX_PIXELS = 4096 * 4096      # the library's largest is 2048x2048

PREVIEWS = "_Previews"
TEXTURES = "_textures"
SHEETS = "_sheets"
LOCAL = "_local"
MANIFEST = "manifest.json"
SHEETS_SCHEMA = "rosw-brushes-sheets/1"
RESET_THUMBNAIL = ingest.RESET_THUMBNAIL
PREVIEW_KB = 128
PREVIEWS_TOTAL_MB = 50
DRY_RUN_LINE = ingest.DRY_RUN_LINE

SIDES = ("n", "i")                    # shape polarity: not inverted, inverted


class PreviewsError(Exception):
    """The command cannot go on. Exit 1."""

    exit_code = bc.EXIT_REFUSED


class EnvironmentProblem(PreviewsError):
    """A missing catalog or library, or an unknown --only. Exit 2."""

    exit_code = bc.EXIT_USAGE


# ── pixels: the stroke ───────────────────────────────────────────────────────

def ink_of(data):
    """The ink of a stored thumbnail as an L image: its alpha channel, or, for
    an image with no alpha, its luminance, inverted when the border is light.
    Raises a PngError (a CodecError) for bytes that are not a usable PNG."""
    img = png_io.read_png(data, max_pixels=THUMB_MAX_PIXELS)
    alpha = png_io.alpha_plane(img)
    if alpha is not None:
        return alpha
    grey = png_io.luminance(img)
    if png_io.border_mean(grey) > 127:
        grey = png_io.negative(grey)
    return grey


def stroke_from_ink(ink):
    """(pixels, measures) of the 530x162 stroke preview made from an ink image,
    or None when there is no ink to show (all zero, also after the reduction)."""
    alpha_max = max(ink.pixels)
    if alpha_max == 0:
        return None
    factor = png_io.fit_factor(ink.width, ink.height, STROKE_W, STROKE_H)
    tile = png_io.center_on(png_io.box_reduce(ink, factor), STROKE_W, STROKE_H, 0)
    stretched = png_io.stretch(tile, floor=16, permille=995)
    if stretched.nonzero == 0:
        return None
    counts = png_io.histogram(tile)
    box = png_io.bbox(tile, 0)
    flat = png_io.flatten_ink(stretched.image, STROKE_GROUND, STROKE_INK)
    measures = {
        "alpha_max": alpha_max,
        "alpha_hi": stretched.hi,
        "gain": round(255 / stretched.hi, 4),
        "ink_fraction": round(sum(counts[INK_FLOOR + 1:]) / len(tile.pixels), 4),
        "bbox": list(box) if box else None,
    }
    return flat.pixels, measures


# ── pixels: textures ─────────────────────────────────────────────────────────

def shape_tile(img, inverted):
    """The 256x256 shape tile of a decoded shape image, white being paint."""
    grey = png_io.to_gray8(img, invert=bool(inverted))
    factor = png_io.fit_factor(grey.width, grey.height, TILE, TILE)
    return png_io.center_on(png_io.box_reduce(grey, factor), TILE, TILE, 0)


def grain_tile(img):
    """The centre 256x256 of a decoded grain image at 1:1, tiled when smaller."""
    grey = png_io.to_gray8(img)
    return png_io.tile_crop(grey, (grey.width - TILE) // 2, (grey.height - TILE) // 2, TILE, TILE)


def _round(value):
    return None if value is None else round(value, 6)


def shape_stats(tile):
    """{coverage, aspect, midtone, edge_touch} of a shape tile (module docstring)."""
    counts = png_io.histogram(tile)
    count = tile.width * tile.height
    total = sum(value * seen for value, seen in enumerate(counts))
    above = sum(counts[17:])
    middle = sum(counts[17:240])
    box = png_io.bbox(tile, 16)
    aspect = (box[2] - box[0]) / (box[3] - box[1]) if box else None
    return {"coverage": _round(total / (count * 255)),
            "aspect": _round(aspect),
            "midtone": _round(middle / above) if above else None,
            "edge_touch": _round(png_io.border_mean(tile, 1) / 255)}


def grain_stats(tile):
    """{mean, contrast} of a grain tile: the mean and the population standard
    deviation, both over 255."""
    counts = png_io.histogram(tile)
    count = tile.width * tile.height
    total = sum(value * seen for value, seen in enumerate(counts))
    squares = sum(value * value * seen for value, seen in enumerate(counts))
    spread = math.sqrt(count * squares - total * total)
    return {"mean": _round(total / (count * 255)), "contrast": _round(spread / (count * 255))}


# ── a 5x7 bitmap font, for the placeholder and the contact sheets ────────────

# Printable ASCII 0x20..0x7E, one glyph each: five columns, bit 0 the top row.
_FONT_HEX = (
    "0000000000", "00005f0000", "0007000700", "147f147f14", "242a7f2a12", "2313086462", "3649552250",
    "0005030000", "001c224100", "0041221c00", "14083e0814", "08083e0808", "0050300000", "0808080808",
    "0060600000", "2010080402", "3e5149453e", "00427f4000", "4261514946", "2141454b31", "1814127f10",
    "2745454539", "3c4a494930", "0171090503", "3649494936", "064949291e", "0036360000", "0056360000",
    "0814224100", "1414141414", "0041221408", "0201510906", "324979413e", "7e1111117e", "7f49494936",
    "3e41414122", "7f4141221c", "7f49494941", "7f09090901", "3e4149497a", "7f0808087f", "00417f4100",
    "2040413f01", "7f08142241", "7f40404040", "7f020c027f", "7f0408107f", "3e4141413e", "7f09090906",
    "3e4151215e", "7f09192946", "4649494931", "01017f0101", "3f4040403f", "1f2040201f", "3f4038403f",
    "6314081463", "0708700807", "6151494543", "007f414100", "0204081020", "0041417f00", "0402010204",
    "4040404040", "0001020400", "2054545478", "7f48444438", "3844444420", "384444487f", "3854545418",
    "087e090102", "0c5252523e", "7f08040478", "00447d4000", "2040443d00", "7f10284400", "00417f4000",
    "7c04180478", "7c08040478", "3844444438", "7c14141408", "081414187c", "7c08040408", "4854545420",
    "043f444020", "3c4040207c", "1c2040201c", "3c4030403c", "4428102844", "0c5050503c", "4464544c44",
    "0008364100", "00007f0000", "0041360800", "1008081008",
)


def _build_font():
    glyphs = tuple(bytes.fromhex(word) for word in _FONT_HEX)
    if len(glyphs) != 95 or any(len(glyph) != 5 for glyph in glyphs):
        raise ValueError("the font table is not 95 glyphs of 5 columns")
    return glyphs


FONT = _build_font()


def ascii_fold(text):
    """Text reduced to printable ASCII: accents dropped by NFKD, anything else
    outside ASCII dropped, controls turned into spaces."""
    folded = unicodedata.normalize("NFKD", str(text))
    out = []
    for char in folded:
        if char.isascii():
            out.append(char if char.isprintable() else " ")
    return "".join(out)


def text_width(text, scale=1):
    return max(0, len(text) * 6 * scale - scale)


def draw_text(canvas, width, x, y, text, *, scale=1, value=255, limit=None):
    """Draw `text` (ASCII; anything else is a ?) into a bytearray canvas of
    `width` columns with its top-left corner at (x, y). Clipped to the canvas
    and to `limit` (an x one past the last column that may be drawn)."""
    height = len(canvas) // width
    limit = width if limit is None else min(limit, width)
    for char in text:
        code = ord(char)
        glyph = FONT[code - 32] if 32 <= code < 127 else FONT[ord("?") - 32]
        for column in range(5):
            bits = glyph[column]
            left = x + column * scale
            if left + scale > limit or left < 0:
                continue
            for row in range(7):
                if bits >> row & 1:
                    top = y + row * scale
                    for dy in range(scale):
                        line = top + dy
                        if 0 <= line < height:
                            start = line * width + left
                            canvas[start:start + scale] = bytes((value,)) * scale
        x += 6 * scale


def _fill(canvas, width, x, y, w, h, value):
    row = bytes((value,)) * w
    for line in range(y, y + h):
        start = line * width + x
        canvas[start:start + w] = row


def _blit(canvas, width, x, y, pixels, w, h):
    for line in range(h):
        start = (y + line) * width + x
        canvas[start:start + w] = pixels[line * w:(line + 1) * w]


def placeholder_stroke(shape_name):
    """The 530x162 tile written when a brush has no usable thumbnail: hatching
    and the words NO THUMBNAIL IN FILE, with the shape's name when it has one."""
    canvas = bytearray(STROKE_W * STROKE_H)
    base = bytes(40 if step < 2 else STROKE_GROUND for step in range(14))
    for y in range(STROKE_H):
        shift = (-y) % 14
        rotated = base[shift:] + base[:shift]
        canvas[y * STROKE_W:(y + 1) * STROKE_W] = (rotated * (STROKE_W // 14 + 1))[:STROKE_W]
    lines = [("NO THUMBNAIL IN FILE", 2)]
    if shape_name:
        lines.append(("shape: " + ascii_fold(shape_name)[:60], 1))
    top = 54
    for text, scale in lines:
        width = text_width(text, scale)
        left = (STROKE_W - width) // 2
        _fill(canvas, STROKE_W, left - 6, top - 4, width + 12, 7 * scale + 8, STROKE_GROUND)
        draw_text(canvas, STROKE_W, left, top, text, scale=scale, value=210)
        top += 7 * scale + 14
    return bytes(canvas)


# ── files ────────────────────────────────────────────────────────────────────

def _sha(data):
    return hashlib.sha256(data).hexdigest()


def png_bytes(width, height, pixels):
    return png_io.write_png(width, height, "L", pixels, level=PNG_LEVEL)


def _read_json(path, default):
    try:
        return json.loads(bc.read_text(path))
    except FileNotFoundError:
        return default
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise EnvironmentProblem(f"{Path(path).name} cannot be read as JSON ({type(exc).__name__}); "
                                 "run `python -I brushes/pipeline/ingest.py build`") from None


def _read_map(path):
    value = _read_json(path, {})
    return value if isinstance(value, dict) else {}


def _preview_dir(local):
    return f"{PREVIEWS}/{LOCAL}" if local else PREVIEWS


def stroke_rel(set_slug, brush_id, local=False):
    return f"{_preview_dir(local)}/{set_slug}/{brush_id}.stroke.png"


def shape_rel(texture_id, side, local=False):
    return f"{_preview_dir(local)}/{TEXTURES}/{texture_id}.{side}.shape.png"


def grain_rel(texture_id, local=False):
    return f"{_preview_dir(local)}/{TEXTURES}/{texture_id}.grain.png"


def manifest_rel(local=False):
    return f"{_preview_dir(local)}/{MANIFEST}"


class Out:
    """Where files go. Nothing is written unless `confirm`; a file whose bytes
    already match is not written either. Remembers what it wrote."""

    def __init__(self, vault, confirm):
        self.vault = Path(vault)
        self.confirm = confirm
        self.written = {}                    # vault-relative path -> (kind, size)

    def path(self, rel):
        return self.vault / rel

    def put(self, rel, data, kind):
        target = self.path(rel)
        try:
            if target.read_bytes() == data:
                return False
        except OSError:
            pass
        if not self.confirm:
            raise AssertionError("a dry run must not write")
        bc.write_bytes(target, data)
        self.written[rel] = (kind, len(data))
        return True

    def put_json(self, path, value, kind, key=None):
        """Write JSON in the one spelling unless the file already holds it."""
        text = bc.json_text(value)
        path = Path(path)
        try:
            if bc.read_text(path) == text:
                return False
        except (OSError, UnicodeDecodeError):
            pass
        if not self.confirm:
            raise AssertionError("a dry run must not write")
        bc.write_text(path, text)
        self.written[key or str(path)] = (kind, len(text.encode("utf-8")))
        return True


# ── the state a run works from ───────────────────────────────────────────────

class State:
    """The catalog and the preview manifests, read once."""

    def __init__(self, paths):
        self.paths = paths
        self.catalog = Path(paths.catalog)
        self.vault = Path(paths.vault)
        index = _read_json(self.catalog / ingest.CATALOG_NAME, None)
        if not isinstance(index, dict):
            raise EnvironmentProblem(f"there is no catalog at {self.catalog}; run "
                                     "`python -I brushes/pipeline/ingest.py build` first")
        self.sets = sorted((row for row in index.get("sets", [])
                            if isinstance(row, dict) and isinstance(row.get("set_slug"), str)),
                           key=lambda row: row["set_slug"])
        self.publish = {pack["id"]: pack.get("publish_previews") is not False
                        for pack in index.get("packs", []) if isinstance(pack, dict) and "id" in pack}
        self.records = {}
        folder = self.catalog / ingest.BRUSHES_DIR
        if folder.is_dir():
            for path in sorted(folder.glob("b_*.json")):
                record = _read_json(path, None)
                if isinstance(record, dict) and isinstance(record.get("id"), str):
                    self.records[record["id"]] = record
        if not self.records:
            raise EnvironmentProblem(f"the catalog at {self.catalog} holds no brush records; run "
                                     "`python -I brushes/pipeline/ingest.py build` first")
        self.textures = _read_map(self.catalog / ingest.TEXTURES_NAME)
        self.thumbnails = _read_map(self.catalog / ingest.THUMBNAILS_NAME)
        self.manifests = {False: _read_map(self.vault / manifest_rel(False)),
                          True: _read_map(self.vault / manifest_rel(True))}

    def is_local(self, record):
        return not self.publish.get(record.get("pack"), True)

    def path_exists(self, rel):
        return (self.vault / rel).is_file()

    def uses(self):
        """texture id -> [(record id, 'primary'|'secondary', role, inverted)], sorted."""
        found = {}
        for brush_id, record in sorted(self.records.items()):
            parts = [("primary", record.get("shape"), record.get("grain"))]
            if isinstance(record.get("secondary"), dict):
                parts.append(("secondary", record["secondary"].get("shape"), record["secondary"].get("grain")))
            for which, shape, grain in parts:
                for role, held in (("shape", shape), ("grain", grain)):
                    texture_id = held.get("texture_id") if isinstance(held, dict) else None
                    if isinstance(texture_id, str) and texture_id in self.textures:
                        found.setdefault(texture_id, []).append(
                            (brush_id, which, role, bool(held.get("inverted")) and role == "shape"))
        return found


def select(state, only):
    """(set slugs, brush ids) that `--only S` selects: S is a set slug or a pack
    id, and a brush is selected by its home set. None, None for no selection."""
    if only is None:
        return None, None
    slugs = {row["set_slug"] for row in state.sets if only in (row["set_slug"], row.get("pack"))}
    if not slugs:
        raise EnvironmentProblem(f"--only {only}: no set slug or pack id of the catalog is {only!r}")
    ids = {brush_id for brush_id, record in state.records.items()
           if record.get("home", {}).get("set_slug") in slugs}
    return slugs, ids


# ── what has to be made ──────────────────────────────────────────────────────

def _manifest_ok(entry, source):
    return (isinstance(entry, dict) and entry.get("preview_version") == PREVIEW_VERSION
            and entry.get("source_sha256") == source)


def stroke_reason(state, record, force):
    """Why this brush's stroke must be made again, or None when it is up to date."""
    if force:
        return "forced"
    local = state.is_local(record)
    rel = stroke_rel(record["home"]["set_slug"], record["id"], local)
    entry = state.thumbnails.get(record["id"])
    if not isinstance(entry, dict) or entry.get("stroke") != rel:
        return "new"
    thumbnail = record.get("thumbnail") or {}
    reset = record.get("reset") or {}
    own = thumbnail.get("sha256") if thumbnail.get("present") else None
    current = [sha for sha in (own, reset.get("thumbnail_sha256")) if sha]
    held = entry.get("source_sha256")
    if (held not in current) if current else (held is not None):
        return "changed"
    if entry.get("stroke_source") not in ("thumbnail",) and own:
        # Made from the Reset/ thumbnail or a placeholder because this one had
        # no ink. The entry does not say which thumbnail that was, so look again.
        return "recheck"
    manifest = state.manifests[local].get(rel)
    if not _manifest_ok(manifest, held):
        return "changed" if manifest else "new"
    if not state.path_exists(rel):
        return "missing"
    return None


class TextureJob:
    """One texture to decode: the tiles it needs and where its bytes come from."""

    def __init__(self, texture_id, local, sides, grain, reasons, source):
        self.texture_id = texture_id
        self.local = local
        self.sides = sides                  # {'n', 'i'} still to make
        self.grain = grain                  # bool
        self.reasons = reasons              # {description: reason}
        self.source = source                # (record id, 'primary'|'secondary')


def texture_jobs(state, uses, selected_ids, force):
    jobs = []
    for texture_id in sorted(uses):
        used = uses[texture_id]
        wanted = [u for u in used if selected_ids is None or u[0] in selected_ids]
        if not wanted:
            continue
        held = state.textures[texture_id]
        sha = held.get("sha256")
        local = all(state.is_local(state.records[u[0]]) for u in used)
        stats = held.get("stats") if isinstance(held.get("stats"), dict) else {}
        reasons, sides, grain = {}, set(), False
        for role in ("shape", "grain"):
            for side in (SIDES if role == "shape" else (None,)):
                if not any(u[2] == role and (role == "grain" or u[3] == (side == "i")) for u in wanted):
                    continue
                if role == "shape":
                    rel = shape_rel(texture_id, side, local)
                    tile = (held.get("shape_tiles") or {}).get(side)
                    measured = ((stats.get("shape") or {}).get(side))
                else:
                    rel = grain_rel(texture_id, local)
                    tile = held.get("grain_tile")
                    measured = stats.get("grain")
                if force:
                    why = "forced"
                elif tile != rel or not isinstance(measured, dict):
                    why = "new"
                elif not _manifest_ok(state.manifests[local].get(rel), sha):
                    why = "changed"
                elif not state.path_exists(rel):
                    why = "missing"
                else:
                    continue
                reasons[rel] = why
                if role == "shape":
                    sides.add(side)
                else:
                    grain = True
        if reasons:
            source = min(((u[0], u[1]) for u in wanted))
            jobs.append(TextureJob(texture_id, local, sides, grain, reasons, source))
    return jobs


def _count(reasons):
    counts = {}
    for why in reasons:
        counts[why] = counts.get(why, 0) + 1
    return ", ".join(f"{number} {why}" for why, number in sorted(counts.items())) or "none"


# ── doing it ─────────────────────────────────────────────────────────────────

class Run:
    """The bookkeeping of one render: problems, warnings, counts."""

    def __init__(self):
        self.failed = []                     # (where, why): the catalog and library disagree
        self.warnings = []                   # (where, why): an image that could not be used
        self.counts = {"stroke": 0, "shape": 0, "grain": 0}

    def fail(self, where, why):
        self.failed.append((where, why))

    def warn(self, where, why):
        self.warnings.append((where, why))


def _problem(exc):
    return getattr(exc, "code", None) or type(exc).__name__


def _folders_of(rel, data):
    """{entry prefix: BrushFolder} of every brush a container holds, spelled as
    the catalog's `entry_prefix` is (ingest.CatalogBuild.read_file)."""
    found = container.read_any(data, rel)
    folders = {}
    for item in found:
        nested = item.origin[len(rel) + 2:] + "!/" if item.origin.startswith(rel + "!/") else ""
        if isinstance(item, container.BrushSet):
            for uuid, folder in item.brushes:
                folders.setdefault(f"{nested}{item.prefix}{uuid}/", folder)
        else:
            folders.setdefault(nested, item)
    return folders


def _folder_for(record, folders):
    """The folder the record describes, checked against its id; or why not."""
    place = record["occurrences"][0]
    folder = folders.get(place["entry_prefix"])
    if folder is None:
        return None, "it is no longer in its container"
    try:
        archive, shape, grain, subs = container.identity_inputs(folder)
        digest = identity.content_sha256(archive, shape, grain, subs)
    except CodecError as exc:
        return None, f"it cannot be read again ({_problem(exc)})"
    if digest != record.get("content_sha256"):
        return None, "it differs from what the catalog describes"
    return folder, None


def make_stroke(own, reset, shape_name):
    """(source, source_sha256, pixels, measures) for a brush's thumbnails (bytes
    or None each), plus a list of what could not be read."""
    unreadable = []
    for source, data in (("thumbnail", own), ("reset-thumbnail", reset)):
        if data is None:
            continue
        try:
            made = stroke_from_ink(ink_of(data))
        except (CodecError, ValueError, OverflowError) as exc:
            unreadable.append(f"{source} is not a usable PNG ({_problem(exc)})")
            continue
        if made is not None:
            return source, _sha(data), made[0], made[1], unreadable
    held = own if own is not None else reset
    return "none", (_sha(held) if held is not None else None), placeholder_stroke(shape_name), None, unreadable


def process_stroke(state, out, run, record, folder, force):
    """Make one brush's stroke preview and record it in thumbnails.json."""
    local = state.is_local(record)
    rel = stroke_rel(record["home"]["set_slug"], record["id"], local)
    own = folder.thumbnail
    reset = folder.reset.thumbnail if folder.reset is not None else None
    thumbnail = record.get("thumbnail") or {}
    if (own is not None) != bool(thumbnail.get("present")) or (
            own is not None and _sha(own) != thumbnail.get("sha256")):
        run.fail(f"{record['id']} {record['display_name']}",
                 "its thumbnail differs from what the catalog describes; run ingest.py build")
        return
    reset_sha = (record.get("reset") or {}).get("thumbnail_sha256")
    if (reset is not None and _sha(reset) != reset_sha) or (reset is None and reset_sha):
        run.fail(f"{record['id']} {record['display_name']}",
                 "its Reset/ thumbnail differs from what the catalog describes; run ingest.py build")
        return
    shape = record.get("shape") or {}
    source, sha, pixels, measures, unreadable = make_stroke(own, reset, shape.get("bundled_name"))
    for why in unreadable:
        run.warn(f"{record['id']} {record['display_name']}", why)
    manifest = state.manifests[local]
    if force or not (_manifest_ok(manifest.get(rel), sha) and state.path_exists(rel)):
        out.put(rel, png_bytes(STROKE_W, STROKE_H, pixels), "stroke")
    manifest[rel] = {"source_sha256": sha, "preview_version": PREVIEW_VERSION, "pixel_sha256": _sha(pixels)}
    entry = {"source_sha256": sha, "stroke": rel, "stroke_source": source,
             "alpha_max": None, "alpha_hi": None, "gain": None, "ink_fraction": None, "bbox": None}
    if measures:
        entry.update(measures)
    state.thumbnails[record["id"]] = entry
    run.counts["stroke"] += 1


def _tile_file(state, out, run, rel, local, sha, tile, kind, force):
    manifest = state.manifests[local]
    if force or not (_manifest_ok(manifest.get(rel), sha) and state.path_exists(rel)):
        out.put(rel, png_bytes(tile.width, tile.height, tile.pixels), kind)
    manifest[rel] = {"source_sha256": sha, "preview_version": PREVIEW_VERSION, "pixel_sha256": _sha(tile.pixels)}
    run.counts[kind] += 1


def process_texture(state, out, run, job, folder, bundled, force):
    """Decode one texture and make the tiles the job asks for."""
    record = state.records[job.source[0]]
    where = f"{job.texture_id} (from {record['id']} {record['display_name']})"
    if job.source[1] == "secondary":
        folder = folder.sub
        if folder is None:
            run.fail(where, "its secondary folder is no longer there")
            return
    resolved = container.resolve_textures(folder, None, bundled=bundled)
    held = state.textures[job.texture_id]
    data = next((found for found in (resolved["shape"][0], resolved["grain"][0])
                 if found is not None and identity.texture_sha256(found) == held.get("sha256")), None)
    if data is None:
        run.fail(where, "the image the catalog describes is no longer in the file; run ingest.py build")
        return
    sha = held["sha256"]
    try:
        img = png_io.read_png(data, max_pixels=TEXTURE_MAX_PIXELS)
    except (CodecError, ValueError, OverflowError, MemoryError) as exc:
        run.warn(where, f"the image is not usable ({_problem(exc)}); no tile, no statistics")
        return
    stats = held.get("stats") if isinstance(held.get("stats"), dict) else {}
    stats = {"shape": dict(stats.get("shape") or {}), "grain": stats.get("grain")}
    stats["shape"].setdefault("n", None)
    stats["shape"].setdefault("i", None)
    tiles = dict(held.get("shape_tiles") or {})
    tiles.setdefault("n", None)
    tiles.setdefault("i", None)
    for side in sorted(job.sides):
        tile = shape_tile(img, side == "i")
        rel = shape_rel(job.texture_id, side, job.local)
        _tile_file(state, out, run, rel, job.local, sha, tile, "shape", force)
        tiles[side] = rel
        stats["shape"][side] = shape_stats(tile)
    if job.grain:
        tile = grain_tile(img)
        rel = grain_rel(job.texture_id, job.local)
        _tile_file(state, out, run, rel, job.local, sha, tile, "grain", force)
        held["grain_tile"] = rel
        stats["grain"] = grain_stats(tile)
    held["shape_tiles"] = tiles
    held["stats"] = stats


def save_state(state, out):
    """Write thumbnails.json, textures.json and the manifests, each only when changed."""
    out.put_json(state.catalog / ingest.THUMBNAILS_NAME, state.thumbnails, "state",
                 f"catalog/{ingest.THUMBNAILS_NAME}")
    out.put_json(state.catalog / ingest.TEXTURES_NAME, state.textures, "state",
                 f"catalog/{ingest.TEXTURES_NAME}")
    for local in (False, True):
        manifest = state.manifests[local]
        path = state.vault / manifest_rel(local)
        if manifest or path.is_file():
            out.put_json(path, manifest, "manifest", manifest_rel(local))


def prune(state):
    """Drop what the catalog no longer points to from thumbnails.json and the
    manifests (a full run only). Files are never deleted."""
    for brush_id in [key for key in state.thumbnails if key not in state.records]:
        del state.thumbnails[brush_id]
    wanted = referenced(state)
    for local in (False, True):
        manifest = state.manifests[local]
        for rel in [key for key in manifest if key not in wanted]:
            del manifest[rel]


# ── the contact sheets ───────────────────────────────────────────────────────

class Tiles:
    """Preview images read back from the vault, one read each."""

    def __init__(self, vault):
        self.vault = Path(vault)
        self.cache = {}

    def get(self, rel, width, height):
        """The pixels of a committed 8-bit grey preview of exactly that size, else None."""
        if not rel:
            return None
        if rel not in self.cache:
            pixels = None
            try:
                img = png_io.read_png((self.vault / rel).read_bytes(), max_pixels=width * height)
                if img.mode == "L" and (img.width, img.height) == (width, height):
                    pixels = img.pixels
            except (OSError, CodecError, ValueError):
                pixels = None
            self.cache[rel] = pixels
        return self.cache[rel]


def _wrap(text, width):
    return [text[i:i + width] for i in range(0, len(text), width)] or [""]


def stand_in(lines, width=SHEET_TILE, height=SHEET_TILE):
    """A cell that says in words what there is no image of."""
    canvas = bytearray(width * height)
    _fill(canvas, width, 0, 0, width, height, 36)
    for edge in (0, height - 1):
        _fill(canvas, width, 0, edge, width, 1, 90)
    for edge in (0, width - 1):
        _fill(canvas, width, edge, 0, 1, height, 90)
    y = 10
    for text, scale in lines:
        for part in _wrap(ascii_fold(text), (width - 12) // (6 * scale)):
            draw_text(canvas, width, 6, y, part, scale=scale, value=200)
            y += 7 * scale + 4
    return bytes(canvas)


def _half(pixels):
    reduced = png_io.box_reduce(png_io.Image(TILE, TILE, "L", pixels), TILE // SHEET_TILE)
    return reduced.pixels


def texture_cell(tiles, preview, role, held):
    """The 128x128 pixels of a shape or grain cell."""
    source = preview.get(f"{role}_source")
    pixels = tiles.get(preview.get(role), TILE, TILE)
    if pixels is not None:
        return _half(pixels)
    if source == "bundled":
        return stand_in([("BUNDLED", 2), (held.get("bundled_name") or "", 1)])
    if source == "blank":
        return stand_in([("BLANK", 2), ("GRAIN", 2)])
    if source == "none":
        return stand_in([("NO", 2), (role.upper(), 2)])
    return stand_in([("NO TILE", 2), ("render has not", 1), ("made one", 1)])


def compose_sheet(cells, tiles):
    """The pixels of one 802x1496 sheet from up to 8 cells, each
    (n, record)."""
    canvas = bytearray(bytes((BACKGROUND,)) * (SHEET_W * SHEET_H))
    for row, (n, record) in enumerate(cells):
        x0, y0 = (SHEET_W - CELL_W) // 2, (SHEET_H - CELL_H * SHEET_ROWS) // 2 + CELL_H * row
        _fill(canvas, SHEET_W, x0, y0, CELL_W, LABEL_H, 64)
        label = f"{n:02d} {ascii_fold(record['display_name'])[:30]}  {record['id']}"
        draw_text(canvas, SHEET_W, x0 + 6, y0 + 4, label, scale=2, value=255, limit=x0 + CELL_W)
        preview = record.get("preview") or {}
        stroke = tiles.get(preview.get("stroke"), STROKE_W, STROKE_H)
        if stroke is None:
            stroke = stand_in([("NO STROKE PREVIEW", 2), ("run previews.py render", 1)], STROKE_W, STROKE_H)
        _blit(canvas, SHEET_W, x0, y0 + LABEL_H, stroke, STROKE_W, STROKE_H)
        gap = (CELL_W - STROKE_W - 2 * SHEET_TILE) // 2
        top = y0 + LABEL_H + (STROKE_H - SHEET_TILE) // 2
        shape = texture_cell(tiles, preview, "shape", record.get("shape") or {})
        grain = texture_cell(tiles, preview, "grain", record.get("grain") or {})
        _blit(canvas, SHEET_W, x0 + STROKE_W + gap, top, shape, SHEET_TILE, SHEET_TILE)
        _blit(canvas, SHEET_W, x0 + STROKE_W + 2 * gap + SHEET_TILE, top, grain, SHEET_TILE, SHEET_TILE)
    return bytes(canvas)


def sheet_files(state, slugs):
    """[(set row, [(sheet file name, [cells])])]: the sheets of each set that has a note."""
    plan = []
    for row in state.sets:
        if not row.get("note") or (slugs is not None and row["set_slug"] not in slugs):
            continue
        members = [(number, state.records[brush_id])
                   for number, brush_id in enumerate(row.get("brushes", []), start=1)
                   if brush_id in state.records]
        sheets = [(f"sheet-{index + 1:02d}.png", members[start:start + SHEET_ROWS])
                  for index, start in enumerate(range(0, len(members), SHEET_ROWS))]
        plan.append((row, sheets))
    return plan


def write_sheets(state, out, slugs, plan=None):
    """Compose and write the sheets. Returns (sets, sheets) planned."""
    tiles = Tiles(state.vault)
    plan = sheet_files(state, slugs) if plan is None else plan
    count = 0
    for row, sheets in plan:
        listed = []
        for name, cells in sheets:
            pixels = compose_sheet(cells, tiles)
            rel = f"{PREVIEWS}/{SHEETS}/{row['set_slug']}/{name}"
            out.put(rel, png_bytes(SHEET_W, SHEET_H, pixels), "sheet")
            count += 1
            listed.append({"file": name, "cells": [
                {"n": n, "id": record["id"], "name": record["display_name"],
                 "stroke_source": (record.get("preview") or {}).get("stroke_source"),
                 "shape_source": (record.get("preview") or {}).get("shape_source"),
                 "grain_source": (record.get("preview") or {}).get("grain_source")}
                for n, record in cells]})
        document = {"schema": SHEETS_SCHEMA, "set_slug": row["set_slug"], "set_id": row.get("set_id"),
                    "rows": SHEET_ROWS, "size": [SHEET_W, SHEET_H], "sheets_per_call": SHEET_PER_CALL,
                    "sheets": listed}
        rel = f"{PREVIEWS}/{SHEETS}/{row['set_slug']}/sheets.json"
        out.put_json(out.path(rel), document, "sheet", rel)
    return len(plan), count


# ── what is on disk ──────────────────────────────────────────────────────────

def kind_of(rel):
    """stroke, shape, grain, manifest, sheet or local for a path under _Previews/."""
    parts = rel.split("/")[1:]
    if not parts:
        return "other"
    if parts[0] == LOCAL:
        return "local"
    if parts[0] == SHEETS:
        return "sheet"
    if parts == [MANIFEST]:
        return "manifest"
    name = parts[-1]
    if name.endswith(".stroke.png"):
        return "stroke"
    if name.endswith(".shape.png"):
        return "shape"
    if name.endswith(".grain.png"):
        return "grain"
    return "other"


def inventory(vault):
    """{kind: [files, bytes]} of everything under _Previews/, and the list of files."""
    base = Path(vault) / PREVIEWS
    kinds, files = {}, []
    if base.is_dir():
        for path in sorted(base.rglob("*")):
            if path.is_file() and not path.name.endswith(".tmp"):
                rel = f"{PREVIEWS}/{path.relative_to(base).as_posix()}"
                held = kinds.setdefault(kind_of(rel), [0, 0])
                held[0] += 1
                held[1] += path.stat().st_size
                files.append(rel)
    return kinds, files


def referenced(state):
    """Every preview image path the catalog points to."""
    wanted = {entry.get("stroke") for entry in state.thumbnails.values() if isinstance(entry, dict)}
    for held in state.textures.values():
        wanted.update(path for path in (held.get("shape_tiles") or {}).values() if path)
        if held.get("grain_tile"):
            wanted.add(held["grain_tile"])
    return wanted


def orphans(state, files):
    """Stroke and tile images (local ones too) that nothing in the catalog points to."""
    wanted = referenced(state)
    return [rel for rel in files
            if rel.endswith((".stroke.png", ".shape.png", ".grain.png"))
            and f"/{SHEETS}/" not in rel and rel not in wanted]


def print_inventory(vault, files, kinds):
    tracked_kinds = ("stroke", "shape", "grain", "manifest")
    tracked = sum(kinds.get(kind, [0, 0])[1] for kind in tracked_kinds)
    print(f"PREVIEWS  {sum(held[0] for held in kinds.values())} files under {PREVIEWS}/")
    for kind in tracked_kinds + ("sheet", "local"):
        if kind in kinds:
            ignored = "  (ignored by git)" if kind in ("sheet", "local") else ""
            print(f"  {kind:<9} {kinds[kind][0]:>6} files  {kinds[kind][1]:>12,} bytes{ignored}")
    print(f"  tracked   {sum(kinds.get(kind, [0, 0])[0] for kind in tracked_kinds):>6} files  "
          f"{tracked:>12,} bytes  (limit {PREVIEWS_TOTAL_MB} MB)")
    if tracked > PREVIEWS_TOTAL_MB * 1024 * 1024:
        print(f"WARNING   the tracked previews are {tracked / 1048576:.1f} MB, over the {PREVIEWS_TOTAL_MB} MB "
              "of F6 and spec.yaml `previews.previews_total_mb`: decide what to commit")
    biggest = max((((Path(vault) / rel).stat().st_size, rel) for rel in files
                   if kind_of(rel) in ("stroke", "shape", "grain")), default=None)
    if biggest and biggest[0] > PREVIEW_KB * 1024:
        print(f"WARNING   {biggest[1]} is {biggest[0]:,} bytes, over the {PREVIEW_KB} KB per file of F6")


# ── the command ──────────────────────────────────────────────────────────────

def _say(text):
    print(text)
    sys.stdout.flush()


def _dry_sheets(state, plan):
    """How many sheets a sheets-only run would write, composed from what is on disk."""
    tiles, changed = Tiles(state.vault), 0
    for row, listing in plan:
        for name, cells in listing:
            data = png_bytes(SHEET_W, SHEET_H, compose_sheet(cells, tiles))
            try:
                same = (state.vault / PREVIEWS / SHEETS / row["set_slug"] / name).read_bytes() == data
            except OSError:
                same = False
            changed += not same
    return changed


def _containers(state, strokes, textures):
    """{library path of a container: [("stroke", record) | ("texture", job)]}."""
    place = {}
    for record, _ in strokes:
        place.setdefault(record["occurrences"][0]["container"], []).append(("stroke", record))
    for job in textures:
        source = state.records[job.source[0]]
        place.setdefault(source["occurrences"][0]["container"], []).append(("texture", job))
    return place


def render_containers(paths, state, out, run, place, force):
    """Read each container once and make what is asked of the brushes in it."""
    library = Path(paths.library)
    if not library.is_dir():
        raise EnvironmentProblem(f"there is no library folder at {library}; the previews to make "
                                 "need the original brush files")
    bundled = library / ingest.BUNDLED_DIR
    bundled = bundled if bundled.is_dir() else None
    for done, rel in enumerate(sorted(place), start=1):
        try:
            data = container.read_path(library / rel)
        except OSError as exc:
            run.fail(rel, f"it cannot be read ({type(exc).__name__})")
            continue
        except CodecError as exc:
            run.fail(rel, f"it cannot be read ({_problem(exc)})")
            continue
        if container.is_lfs_pointer(data):
            raise EnvironmentProblem(f"{rel} is a Git LFS pointer, not a brush file. "
                                     "Run `git lfs pull` and try again.")
        try:
            folders = _folders_of(rel, data)
        except CodecError as exc:
            run.fail(rel, f"it cannot be read ({_problem(exc)})")
            continue
        del data
        for what, item in place[rel]:
            record = item if what == "stroke" else state.records[item.source[0]]
            folder, why = _folder_for(record, folders)
            if folder is None:
                run.fail(f"{record['id']} {record['display_name']} in {rel}", why)
            elif what == "stroke":
                process_stroke(state, out, run, record, folder, force)
            else:
                process_texture(state, out, run, item, folder, bundled, force)
        del folders
        save_state(state, out)
        if done % 10 == 0 or done == len(place):
            _say(f"PROGRESS  {done}/{len(place)} containers; {run.counts['stroke']} strokes, "
                 f"{run.counts['shape']} shape and {run.counts['grain']} grain tiles")


def _catalog_text(catalog):
    try:
        return bc.read_text(Path(catalog) / ingest.CATALOG_NAME)
    except OSError:
        return None


def run_render(paths, *, only=None, force=False, no_sheets=False, sheets_only=False, confirm=False):
    state = State(paths)
    slugs, selected = select(state, only)
    out = Out(state.vault, confirm)
    run = Run()
    print(f"RENDER    {state.catalog}  ->  {state.vault / PREVIEWS}")
    strokes, textures, place, plan = [], [], {}, None
    if not sheets_only:
        uses = state.uses()
        for brush_id, record in sorted(state.records.items()):
            if selected is None or brush_id in selected:
                reason = stroke_reason(state, record, force)
                if reason:
                    strokes.append((record, reason))
        textures = texture_jobs(state, uses, selected, force)
        place = _containers(state, strokes, textures)
        total = len(state.records) if selected is None else len(selected)
        tile_reasons = [why for job in textures for why in job.reasons.values()]
        print(f"STROKES   {len(strokes)} of {total} to make ({_count(why for _, why in strokes)})")
        print(f"TEXTURES  {len(textures)} of {len(uses)} to decode, {len(tile_reasons)} tiles "
              f"({_count(tile_reasons)}); bundled textures get no tile")
        print(f"LIBRARY   {len(place)} containers to read")
    if not no_sheets:
        plan = sheet_files(state, slugs)
        print(f"SHEETS    {len(plan)} sets, {sum(len(sheets) for _, sheets in plan)} sheets of "
              f"{SHEET_ROWS} rows" + ("" if sheets_only else " (made after the previews)"))
        if sheets_only and not confirm:
            print(f"          {_dry_sheets(state, plan)} of them would be written")
    if not confirm:
        print(DRY_RUN_LINE)
        return bc.EXIT_OK

    records_changed = catalog_changed = 0
    if not sheets_only:
        if place:
            render_containers(paths, state, out, run, place, force)
        if selected is None:
            prune(state)
        save_state(state, out)
        before = _catalog_text(state.catalog)
        try:
            records_changed = ingest.apply_preview_results(paths)
        except ingest.IngestError as exc:
            raise PreviewsError(f"the catalog could not be updated: {exc}") from None
        catalog_changed = int(_catalog_text(state.catalog) != before)
    sheet_note = ""
    if not no_sheets:
        sheet_state = state if sheets_only else State(paths)
        sets, count = write_sheets(sheet_state, out, slugs)
        sheet_note = f"; {count} sheets of {sets} sets checked"
    by_kind = {}
    for kind, _ in out.written.values():
        by_kind[kind] = by_kind.get(kind, 0) + 1
    if records_changed:
        by_kind["brush records"] = records_changed
    if catalog_changed:
        by_kind["catalog.json"] = 1
    images = sum(size for kind, size in out.written.values() if kind in ("stroke", "shape", "grain", "sheet"))
    print(f"WROTE     {sum(by_kind.values())} files changed ({images:,} bytes of images)"
          + (": " + ", ".join(f"{number} {kind}" for kind, number in sorted(by_kind.items())) if by_kind else "")
          + sheet_note)
    kinds, files = inventory(state.vault)
    lost = orphans(state, files)
    if lost:
        print(f"ORPHANS   {len(lost)} preview files that no catalog row points to (not removed), "
              f"for example {lost[0]}")
    for where, why in run.warnings:
        print(f"WARNING   {where}: {why}")
    for where, why in run.failed:
        print(f"FAILED    {where}: {why}")
    print_inventory(state.vault, files, kinds)
    if run.failed:
        print(f"REFUSED   {len(run.failed)} items could not be made: the catalog and the library "
              "disagree, or a container cannot be read")
        return bc.EXIT_REFUSED
    return bc.EXIT_OK


def _add_roots(parser, default):
    for name in ("root", "library", "catalog", "vault"):
        parser.add_argument(bc.FLAGS[name], metavar="DIR", default=default, help=bc.FLAG_HELP[name])


def build_parser():
    parser = argparse.ArgumentParser(
        prog="previews.py",
        description="Make the stroke, shape and grain previews and the contact sheets. "
                    "`render` is a dry run without --confirm.")
    _add_roots(parser, None)
    verbs = parser.add_subparsers(dest="verb", metavar="{render}", required=True)
    render = verbs.add_parser("render", help="make the previews (a dry run without --confirm)")
    render.add_argument("--only", metavar="S", help="only the brushes whose home set slug or pack id is S")
    render.add_argument("--force", action="store_true",
                        help="measure and render again whatever the manifest says")
    render.add_argument("--no-sheets", action="store_true", help="do not make the contact sheets")
    render.add_argument("--sheets-only", action="store_true",
                        help="make only the contact sheets, from the committed previews; no library")
    render.add_argument("--stdlib", action="store_true", help="decode without PIL even where it is installed")
    render.add_argument("--confirm", action="store_true", help="really write")
    _add_roots(render, argparse.SUPPRESS)
    return parser


def main(argv=None):
    bc.open_console()
    args = build_parser().parse_args(argv)
    paths = bc.paths_from_args(args)
    if args.no_sheets and args.sheets_only:
        print("error: --no-sheets and --sheets-only cancel each other out", file=sys.stderr)
        return bc.EXIT_USAGE
    held = png_io.HAVE_PIL
    if args.stdlib:
        png_io.HAVE_PIL = False
    try:
        return run_render(paths, only=args.only, force=args.force, no_sheets=args.no_sheets,
                          sheets_only=args.sheets_only, confirm=args.confirm)
    except PreviewsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except ingest.IngestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    finally:
        png_io.HAVE_PIL = held


if __name__ == "__main__":
    raise SystemExit(main())
