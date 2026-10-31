"""The notes writer: one Markdown note per brushset, generated from the catalog.

    python -I brushes/pipeline/notes.py write [--only S] [--diff] [--overwrite-generated] [--confirm]
    python -I brushes/pipeline/notes.py check

Reads `catalog/` (catalog.json, brushes/<id>.json, textures.json,
containers.json) and the notes that already exist in `vault/`. It reads no
brush file and no library folder, so it needs no Git LFS object. Standard
library only. The layout is docs/CONTRACTS.md F7; who may write what is F12.

write    Render every note and compare it with the file on disk.

             new         the note does not exist: it is created
             changed     the generated part differs: only it is rewritten
             unchanged   nothing to do; the file is not touched
             REFUSED     the generated part was edited by hand (its stored
                         fingerprint is not that of its text), or the file has
                         no `## Notes` line. Nothing is written for it and the
                         run exits 1, unless --overwrite-generated is given for
                         the first case
             orphan      a generated note whose set is not in the catalog. It
                         is reported and never deleted

         The generated part of a note is everything above its `## Notes`
         line. The `## Notes` line and everything after it belong to the author
         and are kept byte for byte. A dry run (no --confirm) prints the plan
         and writes nothing; --diff also prints what would change. --only S
         limits the run to the note of set slug (or pack id) S and leaves the
         folder indexes and 00_INDEX.md alone.

         The same rules write each folder's `_index.md` (a map of content) and
         `00_INDEX.md`; they too keep an author's `## Notes` section.

check    Compare every expected file with the disk and report drift: a note
         that is missing, one whose generated part is stale or was edited, one
         with no set behind it. Exit 1 on any drift, 0 when the vault is what
         the catalog says. Writes nothing.

A note is a pure function of the catalog: no timestamp, no absolute path, every
list sorted, the same input gives the same bytes. An exact value is quoted from
`catalog/brushes/<brush_id>.json`, never invented; a number a note rounds for
reading is rounded the way F7 says (%.3f for size and spacing, %.2f elsewhere).

Exit codes: 0 ok (a clean dry run too), 1 refused or drifted, 2 usage or
environment (a bad argument, no catalog).
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402

DRY_RUN_LINE = "DRY RUN   nothing is written without --confirm."

# The layout version the chunker of vault/tools/brush_search.py reads (F7).
CHUNKER_VERSION = "b1"
TEMPLATE_NOTE = "brushset-note/1"
TEMPLATE_MOC = "moc-index/1"
TEMPLATE_INDEX = "vault-index/1"

CATALOG_SCHEMA = "rosw-brushes-catalog/1"
NOTES_HEADING = "## Notes"
RESERVED_HEADINGS = ("Overview", "Shared brushes", "Notes")
SET_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,47}$")
BRUSH_ID = re.compile(r"^b_[0-9a-f]{12}$")

# The twelve list lines of a brush section, in order (F7).
BRUSH_LINES = ("id", "kind", "shape", "grain", "size", "pressure", "tilt", "speed", "taper",
               "render", "facets", "preview")

FOLDER_OFFICIAL, FOLDER_MINE, FOLDER_LOOSE, FOLDER_OTHER = (
    "01_Procreate_Defaults", "04_My_Brushes", "03_Loose", "02_Vendor_Packs")
NOTE_FOLDERS = ("01_Procreate_Defaults", "02_Vendor_Packs", "03_Loose", "04_My_Brushes")
FOLDER_TITLES = {"01_Procreate_Defaults": "Procreate Defaults", "02_Vendor_Packs": "Vendor Packs",
                 "03_Loose": "Loose Brushes", "04_My_Brushes": "My Brushes"}
INDEX_NAME = "00_INDEX.md"
MOC_NAME = "_index.md"
AUTHOR_NOTE = "Everything above `## Notes` is generated from the catalog. Write only below it."

FP_BLANK = 'generated_fingerprint: ""'
FP_LINE = re.compile(r'^generated_fingerprint: "sha256:16:([0-9a-f]{16})"$', re.MULTILINE)
NOTES_LINE = re.compile(r"^## Notes\r?$", re.MULTILINE)

NEW, CHANGED, UNCHANGED, REFUSED, ORPHAN = "new", "changed", "unchanged", "REFUSED", "orphan"

# A character no heading, table cell or YAML scalar may carry: controls, line
# and paragraph separators, byte-order marks, lone surrogates, non-characters.
_UNFIT = re.compile("[\x00-\x1f\x7f-\x9f  ﻿￾￿\ud800-\udfff]")


class NotesError(Exception):
    """The command cannot go on."""

    exit_code = bc.EXIT_REFUSED


class UsageProblem(NotesError):
    """A bad argument or an environment that is not ready. Exit 2."""

    exit_code = bc.EXIT_USAGE


# ── text helpers ─────────────────────────────────────────────────────────────

def one_line(text):
    """Text on one line: every unfit character becomes a space."""
    return _UNFIT.sub(" ", str(text))


def code_span(text):
    """A name inside backticks (a backtick cannot sit inside one)."""
    return "`" + one_line(text).replace("`", "'") + "`"


def yaml_quoted(text):
    """A double-quoted YAML scalar. A double quote becomes a single one (F7);
    a backslash is doubled, which is what YAML needs and a plain reader shows."""
    return '"' + one_line(text).replace('"', "'").replace("\\", "\\\\") + '"'


_YAML_WORDS = frozenset(("true", "false", "yes", "no", "on", "off", "y", "n", "null", "~", ""))
_PLAIN = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./-]*$")
_NUMBERISH = re.compile(r"^[0-9][0-9_.eE+-]*$")


def yaml_plain(text):
    """A scalar as it is written bare when that is safe, quoted when YAML would
    read it as something else (a boolean, a number, an empty value)."""
    text = one_line(text)
    if _PLAIN.match(text) and text.lower() not in _YAML_WORDS and not _NUMBERISH.match(text):
        return text
    return yaml_quoted(text)


def link_label(text):
    """A wikilink alias: the characters that end or split a link become spaces."""
    return re.sub(r"\s+", " ", re.sub(r"[|\[\]]", " ", one_line(text))).strip() or "Untitled"


def link_heading(text):
    """A heading as a wikilink target: Obsidian cannot target these characters."""
    return re.sub(r"\s+", " ", re.sub(r"[#|^:\[\]]", " ", one_line(text))).strip()


def fnum(value, places=2):
    """A number for reading, or `n/a`. `-0.00` is written `0.00`."""
    number = scalar(value)
    if number is None:
        return "n/a"
    text = f"{number:.{places}f}"
    if text.startswith("-") and not text.strip("-0."):
        text = text[1:]
    return text


def yesno(value):
    return "n/a" if not isinstance(value, bool) else ("yes" if value else "no")


def scalar(value):
    """A catalog value as a float, or None. A real key may hold a tag
    (`{"$real32": "80000000"}`, F3), which is opened here."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, dict):
        for tag, code in (("$real32", ">f"), ("$real64", ">d")):
            if tag in value:
                inner = value[tag]
                if isinstance(inner, (int, float)) and not isinstance(inner, bool):
                    number = float(inner)
                elif isinstance(inner, str):
                    try:
                        number = struct.unpack(code, bytes.fromhex(inner))[0]
                    except (ValueError, struct.error):
                        return None
                else:
                    return None
                break
        else:
            if "$int" in value and isinstance(value["$int"], int) and not isinstance(value["$int"], bool):
                number = float(value["$int"])
            else:
                return None
    else:
        return None
    return number if number == number and number not in (float("inf"), float("-inf")) else None


def setting(record, *keys):
    """The first of `keys` the brush's settings hold, as a number (None if absent)."""
    settings = record.get("settings")
    if not isinstance(settings, dict):
        return None
    for key in keys:
        if key in settings:
            return scalar(settings[key])
    return None


def setting_raw(record, *keys):
    settings = record.get("settings")
    if not isinstance(settings, dict):
        return None
    for key in keys:
        if key in settings:
            return settings[key]
    return None


_NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                 "eleven", "twelve")


def count_word(n):
    return _NUMBER_WORDS[n] if 0 <= n < len(_NUMBER_WORDS) else f"{n:,}"


def plural(n, word, many=None):
    return word if n == 1 else (many or word + "s")


def capitalise(text):
    return text[:1].upper() + text[1:]


def join_and(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def sealed(text_with_blank_fingerprint):
    """Fill in `generated_fingerprint`: the first 16 hex of the sha256 of the
    generated part with the value blanked (F7 "Regeneration")."""
    digest = hashlib.sha256(text_with_blank_fingerprint.encode("utf-8")).hexdigest()[:16]
    return text_with_blank_fingerprint.replace(FP_BLANK, f'generated_fingerprint: "sha256:16:{digest}"', 1)


def _frontmatter_span(text):
    """(start, end) of the frontmatter block's inner lines, or None."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    return None if end < 0 else (4, end + 1)


def fingerprint_holds(generated):
    """True when the stored fingerprint is that of the text it sits in."""
    span = _frontmatter_span(generated)
    if span is None:
        return False
    head = generated[span[0]:span[1]]
    match = FP_LINE.search(head)
    if not match:
        return False
    blanked = generated[:span[0]] + head.replace(match.group(0), FP_BLANK, 1) + generated[span[1]:]
    return hashlib.sha256(blanked.encode("utf-8")).hexdigest()[:16] == match.group(1)


# ── the catalog ──────────────────────────────────────────────────────────────

def _read_json(path, what):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise UsageProblem(f"{what} is missing: {path}; run `ingest.py build` first") from None
    except (OSError, ValueError) as exc:
        raise UsageProblem(f"{what} cannot be read ({exc}): {path}") from None


class Catalog:
    """What the notes are made from: catalog.json, the brush records, the two
    small maps (textures.json, containers.json). Read-only."""

    def __init__(self, folder):
        self.folder = Path(folder)
        index = _read_json(self.folder / "catalog.json", "the catalog")
        if not isinstance(index, dict) or index.get("schema") != CATALOG_SCHEMA:
            raise UsageProblem(f"{self.folder / 'catalog.json'} is not a {CATALOG_SCHEMA} file")
        self.index = index
        self.sets = [row for row in index.get("sets", [])]
        self.packs = {pack["id"]: pack for pack in index.get("packs", []) if isinstance(pack, dict) and "id" in pack}
        self.brush_rows = index.get("brushes", [])
        self.counts = index.get("counts", {})
        self.textures = self._optional("textures.json")
        self.containers = self._optional("containers.json")
        self._records = {}
        slugs = [row.get("set_slug") for row in self.sets]
        for slug in slugs:
            if not isinstance(slug, str) or not SET_SLUG.match(slug):
                raise UsageProblem(f"the catalog holds a set with a bad slug: {slug!r}")
        if len(set(slugs)) != len(slugs):
            raise UsageProblem("the catalog holds two sets with one slug")
        self.set_by_slug = {row["set_slug"]: row for row in self.sets}

    def _optional(self, name):
        path = self.folder / name
        if not path.is_file():
            return {}
        data = _read_json(path, name)
        return data if isinstance(data, dict) else {}

    def record(self, brush_id):
        if brush_id not in self._records:
            if not isinstance(brush_id, str) or not BRUSH_ID.match(brush_id):
                raise UsageProblem(f"the catalog names a bad brush id: {brush_id!r}")
            record = _read_json(self.folder / "brushes" / f"{brush_id}.json", f"the record of {brush_id}")
            if not isinstance(record, dict) or record.get("id") != brush_id:
                raise UsageProblem(f"catalog/brushes/{brush_id}.json is not that brush's record")
            self._records[brush_id] = record
        return self._records[brush_id]

    def pack(self, pack_id):
        return self.packs.get(pack_id) or {}

    def texture_size(self, texture_id):
        entry = self.textures.get(texture_id) if isinstance(texture_id, str) else None
        if isinstance(entry, dict) and isinstance(entry.get("width"), int) and isinstance(entry.get("height"), int):
            return entry["width"], entry["height"]
        return None

    def container_bytes(self, sha):
        entry = self.containers.get(sha) if isinstance(sha, str) else None
        size = entry.get("bytes") if isinstance(entry, dict) else None
        return size if isinstance(size, int) and not isinstance(size, bool) else None


def route_folder(row):
    """The folder of a set's note: the first row of F7 that fits."""
    if row.get("library") == "official":
        return FOLDER_OFFICIAL
    if row.get("pack_kind") == "mine":
        return FOLDER_MINE
    if row.get("kind") == "loose":
        return FOLDER_LOOSE
    return FOLDER_OTHER


def safe_note_path(rel):
    """A vault-relative note path the catalog may name: one of the four folders,
    a slug, `.md`. Anything else (an absolute path, `..`, a backslash) is refused."""
    if not isinstance(rel, str) or "\\" in rel or rel.startswith("/") or ":" in rel:
        return False
    parts = PurePosixPath(rel).parts
    return (len(parts) == 2 and parts[0] in NOTE_FOLDERS and parts[1].endswith(".md")
            and SET_SLUG.match(parts[1][:-3]) is not None)


def note_sets(cat):
    """The set rows that get a note, sorted by slug. Refuses a catalog whose
    note paths are unsafe or are not where F7 puts them."""
    rows = []
    for row in sorted(cat.sets, key=lambda r: r["set_slug"]):
        note = row.get("note")
        if note is None:
            continue
        if not safe_note_path(note):
            raise NotesError(f"the catalog names an unsafe note path for {row['set_slug']}: {note!r}")
        expected = f"{route_folder(row)}/{row['set_slug']}.md"
        if note != expected:
            raise NotesError(f"the catalog puts {row['set_slug']} at {note} but F7 routes it to {expected}; "
                             "run `ingest.py build`")
        rows.append(row)
    return rows


def members_of(row):
    """A set's brush ids in plist order, each once."""
    seen, out = set(), []
    for brush_id in row.get("brushes", []):
        if brush_id not in seen:
            seen.add(brush_id)
            out.append(brush_id)
    return out


def home_of(record):
    home = record.get("home")
    return home.get("set_slug") if isinstance(home, dict) else None


def headings_for(cat, rows):
    """{set_slug: {brush_id: heading}} for the brushes each note holds.

    A heading is the display name on one line; a reserved word gets ` (brush)`;
    a repeat inside the note gets ` (2)`, ` (3)` in plist order (F5 "Duplicates
    and homes"). A numbered heading that is itself taken is skipped over."""
    out = {}
    for row in rows:
        slug = row["set_slug"]
        used, seen, mapping = set(), {}, {}
        for brush_id in members_of(row):
            record = cat.record(brush_id)
            if home_of(record) != slug:
                continue
            base = one_line(record.get("display_name") or record.get("name") or "").strip() or "Untitled"
            if base in RESERVED_HEADINGS:
                base += " (brush)"
            number = seen.get(base, 0) + 1
            heading = base if number == 1 else f"{base} ({number})"
            while heading in used:
                number += 1
                heading = f"{base} ({number})"
            seen[base] = number
            used.add(heading)
            mapping[brush_id] = heading
        out[slug] = mapping
    return out


# ── one brush section ────────────────────────────────────────────────────────

def _word_class(words, candidates):
    """The class of a measured facet, read from the record's facet words."""
    for word in candidates:
        if word in words:
            return word.split("-", 1)[1]
    return None


def _with_class(label, number_text):
    return f"{label} ({number_text})" if label else number_text


def shape_line(cat, record):
    shape = record.get("shape") if isinstance(record.get("shape"), dict) else {}
    facets = record.get("facets") if isinstance(record.get("facets"), dict) else {}
    words = set(record.get("facet_words") or [])
    source = shape.get("source")
    name = shape.get("bundled_name")
    if source == "embedded":
        size = cat.texture_size(shape.get("texture_id"))
        parts = ["embedded" + (f" {size[0]}x{size[1]}" if size else "") + f", inverted {yesno(shape.get('inverted'))}"]
    elif source == "bundled":
        parts = [(f"bundled {code_span(name)}" if name else "bundled") + " (inside Procreate, not in this library)"]
    elif source == "bundled-supplied":
        parts = [(f"bundled-supplied {code_span(name)}" if name else "bundled-supplied")
                 + " (a file supplied in library/bundled)"]
    else:
        parts = ["none"]
    if facets.get("shape_coverage") is not None:
        parts.append(f"coverage {fnum(facets['shape_coverage'])}")
    if facets.get("shape_aspect") is not None:
        label = _word_class(words, ("shape-even", "shape-wide", "shape-tall"))
        parts.append("aspect " + _with_class(label, fnum(facets["shape_aspect"])))
    if facets.get("shape_midtone") is not None:
        label = _word_class(words, ("shape-hard", "shape-mixed", "shape-soft"))
        parts.append("edges " + _with_class(label, fnum(facets["shape_midtone"])))
    if facets.get("shape_edge_touch") is not None:
        parts.append(f"edge touch {fnum(facets['shape_edge_touch'])}")
    parts.append(f"scatter {fnum(setting(record, 'shapeScatter'))}")
    parts.append(f"rotation {fnum(setting(record, 'shapeRotation'))}")
    parts.append(f"randomised {yesno(setting_raw(record, 'shapeRandomise'))}")
    parts.append(f"azimuth {yesno(setting_raw(record, 'shapeAzimuth'))}")
    return " · ".join(parts)


def grain_line(cat, record):
    grain = record.get("grain") if isinstance(record.get("grain"), dict) else {}
    facets = record.get("facets") if isinstance(record.get("facets"), dict) else {}
    words = set(record.get("facet_words") or [])
    source = grain.get("source")
    name = grain.get("bundled_name")
    if source == "embedded":
        size = cat.texture_size(grain.get("texture_id"))
        parts = ["embedded" + (f" {size[0]}x{size[1]}" if size else "") + f", inverted {yesno(grain.get('inverted'))}"]
    elif source == "blank":
        parts = ["blank (" + code_span(name or "Brush-Preset-Blank.png") + ")"]
    elif source == "bundled":
        parts = [(f"bundled {code_span(name)}" if name else "bundled") + " (inside Procreate, not in this library)"]
    elif source == "bundled-supplied":
        parts = [(f"bundled-supplied {code_span(name)}" if name else "bundled-supplied")
                 + " (a file supplied in library/bundled)"]
    else:
        parts = ["none"]
    if facets.get("grain_mean") is not None:
        parts.append(f"mean {fnum(facets['grain_mean'])}")
    if facets.get("grain_contrast") is not None:
        label = _word_class(words, ("grain-flat", "grain-subtle", "grain-medium", "grain-strong"))
        parts.append("contrast " + _with_class(label, fnum(facets["grain_contrast"])))
    parts.append(f"scale {fnum(setting(record, 'textureScale'))}")
    parts.append(f"movement {fnum(setting(record, 'textureMovement'))}")
    parts.append(f"zoom {fnum(setting(record, 'textureZoom'))}")
    application = facets.get("grain_application_code")
    if application is not None:
        parts.append(f"application {fnum(application, 0)}")
    return " · ".join(parts)


def preview_line(record):
    preview = record.get("preview") if isinstance(record.get("preview"), dict) else {}
    stroke = {"thumbnail": "Procreate's own thumbnail",
              "reset-thumbnail": "the thumbnail inside the Reset folder (the brush's own is empty or absent)",
              "none": "no thumbnail in the file (the preview is a placeholder)",
              "rendered-approx": "an approximate render, not Procreate's own"}.get(
                  preview.get("stroke_source"), "unknown source")
    missing = [kind for kind, key in (("shape", "shape_source"), ("grain", "grain_source"))
               if preview.get(key) == "bundled"]
    if len(missing) == 2:
        stroke += "; shape and grain images are not in the file"
    elif missing:
        stroke += f"; the {missing[0]} image is not in the file"
    return stroke


def stroke_link(cat, record):
    """The vault-relative path of the stroke preview: the record's own, else the
    path F6 will give it (the file may not exist yet; notes never create it)."""
    preview = record.get("preview") if isinstance(record.get("preview"), dict) else {}
    path = preview.get("stroke")
    if isinstance(path, str) and path:
        return path
    pack = cat.pack(record.get("pack"))
    base = "_Previews/_local" if pack.get("publish_previews") is False else "_Previews"
    return f"{base}/{home_of(record)}/{record['id']}.stroke.png"


def _pair(record, start_key, end_key):
    """`0.11/0.24`, or `n/a` when the brush's era has neither key."""
    start, end = setting(record, start_key), setting(record, end_key)
    return "n/a" if start is None and end is None else f"{fnum(start)}/{fnum(end)}"


def brush_section(cat, record, heading, set_row):
    facets = record.get("facets") if isinstance(record.get("facets"), dict) else {}
    fmt = record.get("format") if isinstance(record.get("format"), dict) else {}
    home = record.get("home") if isinstance(record.get("home"), dict) else {}
    position = home.get("position")
    where = f"{position} of {set_row.get('brush_count')}" if isinstance(position, int) else "n/a"
    lines = [f"## {heading}", ""]
    lines.append(f"- id: `{record['id']}` · {where} · era {one_line(record.get('era', 'n/a'))} · "
                 f"{fmt.get('key_count', 'n/a')} keys")
    kind = (f"kind: {one_line(facets.get('kind', 'n/a'))} · spacing {one_line(facets.get('spacing_class', 'n/a'))} "
            f"({fnum(facets.get('spacing'), 3)})")
    if facets.get("dual") is True:
        kind += " · dual"
        if facets.get("dual_blend_code") is not None:
            kind += f" (blend {fnum(facets['dual_blend_code'], 0)})"
    lines.append("- " + kind)
    lines.append("- shape: " + shape_line(cat, record))
    lines.append("- grain: " + grain_line(cat, record))
    lines.append(f"- size: {fnum(facets.get('size_min'), 3)} to {fnum(facets.get('size_max'), 3)} "
                 f"({one_line(facets.get('size_class', 'n/a'))}) · opacity {fnum(facets.get('opacity_min'))} "
                 f"to {fnum(facets.get('opacity_max'))}")
    lines.append(f"- pressure: size {one_line(facets.get('pressure_size_class', 'n/a'))} "
                 f"({fnum(facets.get('pressure_size'))}) · opacity "
                 f"{one_line(facets.get('pressure_opacity_class', 'n/a'))} ({fnum(facets.get('pressure_opacity'))})")
    if facets.get("tilt") is True:
        tilt = [f"{label} {fnum(setting(record, key))}"
                for label, key in (("size", "dynamicsTiltSize"), ("opacity", "dynamicsTiltOpacity"),
                                   ("gradation", "dynamicsTiltGradation"), ("bleed", "dynamicsTiltBleed"))
                if (setting(record, key) or 0.0) > 0.02]
        lines.append("- tilt: " + (" · ".join(tilt) if tilt else "yes"))
    else:
        lines.append("- tilt: none")
    if facets.get("speed") is True:
        lines.append(f"- speed: size {fnum(setting(record, 'dynamicsSpeedSize'))} · "
                     f"opacity {fnum(setting(record, 'dynamicsSpeedOpacity'))}")
    else:
        lines.append("- speed: none")
    lines.append(f"- taper: {one_line(facets.get('taper', 'n/a'))} · "
                 f"pencil {_pair(record, 'pencilTaperStartLength', 'pencilTaperEndLength')}"
                 f" · touch {_pair(record, 'taperStartLength', 'taperEndLength')}")
    blend = f"blend {fnum(facets.get('blend_code'), 0)}"
    if facets.get("blend_extended_code") is not None:
        blend += f" (extended {fnum(facets['blend_extended_code'], 0)})"
    lines.append(f"- render: {one_line(facets.get('render_code', 'n/a'))} · {blend} · "
                 f"flow {fnum(setting(record, 'dynamicsGlazeFlow', 'dynamicsGlazedFlow'))} · "
                 f"wet mix {yesno(facets.get('wet_mix'))}")
    words = [one_line(word) for word in (record.get("facet_words") or [])]
    lines.append("- facets: " + (" ".join(words) if words else "(none)"))
    lines.append("- preview: " + preview_line(record))
    lines.append("")
    lines.append(f"![[{stroke_link(cat, record)}]]")
    lines.append("")
    return lines


# ── one note ─────────────────────────────────────────────────────────────────

def _tally(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def _phrase_sentence(counts, total, phrases):
    """One sentence about how `total` brushes divide over categories.

    `phrases` maps a category to (singular verb phrase, plural verb phrase). One
    category covering everything reads "All six ..."; a split reads
    "One ... and three ..." in a fixed category order. A brush whose category is
    not in `phrases` is counted apart ("is not recorded"), never dropped."""
    present = [key for key in phrases if counts.get(key)]
    rest = total - sum(counts.get(key, 0) for key in present)
    pieces = [(counts[key],) + tuple(phrases[key]) for key in present]
    if rest > 0:
        pieces.append((rest, "has no recorded value", "have no recorded value"))
    if not pieces:
        return None
    if len(pieces) == 1:
        _n, sing, plur = pieces[0]
        if total == 1:
            return f"It {sing}."
        if total == 2:
            return f"Both {plur}."
        return f"All {count_word(total)} {plur}."
    return capitalise(join_and(f"{count_word(n)} {sing if n == 1 else plur}" for n, sing, plur in pieces)) + "."


SHAPE_PHRASES = {
    "embedded": ("carries its own shape image", "carry their own shape image"),
    "bundled": ("uses a shape that ships inside Procreate", "use a shape that ships inside Procreate"),
    "bundled-supplied": ("uses a shape from a file supplied in library/bundled",
                         "use a shape from a file supplied in library/bundled"),
    "none": ("has no shape image", "have no shape image"),
}
GRAIN_PHRASES = {
    "embedded": ("embeds a grain image", "embed a grain image"),
    "bundled": ("uses a grain that ships inside Procreate", "use a grain that ships inside Procreate"),
    "bundled-supplied": ("uses a grain from a file supplied in library/bundled",
                         "use a grain from a file supplied in library/bundled"),
    "blank": ("uses the blank grain", "use the blank grain"),
    "none": ("has no grain", "have no grain"),
}
KIND_PHRASES = {
    "stroke": ("is a stroke brush", "are stroke brushes"),
    "stamp": ("is a stamp", "are stamps"),
}


def _sources_text(cat, set_row, member_records):
    """`read from ...` for a set: the container files its brushes were found in."""
    slug = set_row["set_slug"]
    found = {}
    for record in member_records:
        for occurrence in record.get("occurrences") or []:
            if isinstance(occurrence, dict) and occurrence.get("set_slug") == slug and occurrence.get("container"):
                found[occurrence["container"]] = occurrence.get("container_sha256")
    names = sorted(found)
    if not names:
        return ""
    if set_row.get("kind") == "loose":
        sizes = [cat.container_bytes(found[name]) for name in names]
        if all(size is not None for size in sizes):
            return f"({sum(sizes):,} bytes in all)"
        return ""
    parts = []
    for name in names:
        size = cat.container_bytes(found[name])
        parts.append(code_span(PurePosixPath(name).name) + (f" ({size:,} bytes)" if size is not None else ""))
    return "read from " + join_and(parts)


def overview(cat, set_row, pack, members, homed):
    """The Overview paragraph: counts and sources, every word from the catalog."""
    total = len(members)
    pack_id = set_row.get("pack")
    vendor = pack.get("vendor")
    pack_text = f"the pack {code_span(pack_id)}" + (f" ({one_line(vendor)})" if vendor else "")
    records = [cat.record(i) for i in members]
    sources = _sources_text(cat, set_row, records)
    if set_row.get("kind") == "loose":
        first = (f"{capitalise(count_word(total))} loose brush {plural(total, 'file')} from {pack_text}"
                 + (f" {sources}" if sources else "") + ".")
    else:
        first = (f"{capitalise(count_word(total))} {plural(total, 'brush', 'brushes')} from {pack_text}"
                 + (f", {sources}" if sources else "") + ".")
    sentences = [first]
    here = [cat.record(i) for i in homed]
    if len(homed) != total:
        other = total - len(homed)
        sentences.append(
            f"{capitalise(count_word(len(homed)))} {plural(len(homed), 'has', 'have')} "
            f"{plural(len(homed), 'its', 'their')} {plural(len(homed), 'section')} in this note; the other "
            f"{count_word(other)} {plural(other, 'is', 'are')} homed in another set and listed under Shared brushes.")
    if here:
        n = len(here)
        kinds = _tally((r.get("facets") or {}).get("kind") for r in here)
        eras = _tally(r.get("era") for r in here)
        kind_phrases = dict(KIND_PHRASES)
        listing = ""
        if len(eras) == 1:
            era = one_line(next(iter(eras)))
            kind_phrases = {k: (x + f" in format era {era}", y + f" in format era {era}")
                            for k, (x, y) in kind_phrases.items()}
        elif len(eras) > 1:
            listing = join_and(f"{one_line(e)} ({c})" for e, c in sorted(eras.items(), key=lambda kv: str(kv[0])))
        sentence = _phrase_sentence(kinds, n, kind_phrases)
        if sentence:
            sentences.append(sentence)
        if listing:
            sentences.append(f"Their format eras are {listing}.")
        shapes = _tally((r.get("shape") or {}).get("source") or "none" for r in here)
        sentence = _phrase_sentence(shapes, n, SHAPE_PHRASES)
        if sentence:
            sentences.append(sentence)
        grains = _tally((r.get("grain") or {}).get("source") or "none" for r in here)
        sentence = _phrase_sentence(grains, n, GRAIN_PHRASES)
        if sentence:
            sentences.append(sentence)
        dual = sum(1 for r in here if (r.get("facets") or {}).get("dual") is True)
        if dual:
            sentences.append(f"{capitalise(count_word(dual))} {plural(dual, 'is a dual brush', 'are dual brushes')}, "
                             "with a second brush stored inside the first.")
        reset = sum(1 for r in here if r.get("reset"))
        if reset:
            sentences.append(f"{capitalise(count_word(reset))} {plural(reset, 'keeps', 'keep')} a Reset folder in the file.")
    redistribute = pack.get("redistribute") or "unknown"
    licence = pack.get("licence_note")
    tail = f"Redistribution is recorded as {one_line(redistribute)}"
    if licence:
        tail += f"; licence note: {one_line(licence).strip()}"
    tail = tail.rstrip()
    sentences.append(tail if tail.endswith((".", "!", "?")) else tail + ".")
    return " ".join(sentences)


def render_note(cat, set_row, headings):
    """The generated part of one set's note: frontmatter through the blank line
    before `## Notes`, fingerprint filled in."""
    slug = set_row["set_slug"]
    members = members_of(set_row)
    homed = [i for i in members if home_of(cat.record(i)) == slug]
    shared = [i for i in members if i not in set(homed)]
    pack = cat.pack(set_row.get("pack"))
    records = [cat.record(i) for i in homed]
    eras = sorted({str(r.get("era")) for r in records})
    kinds = sorted({str((r.get("facets") or {}).get("kind")) for r in records})
    title = one_line(set_row.get("title") or set_row.get("name") or slug).strip() or slug
    tags = ["brushset", f"library/{set_row.get('library')}"] + [f"era/{era}" for era in eras]
    front = [
        "---",
        f"title: {yaml_quoted(title)}",
        "type: brushset",
        f"set_name: {yaml_quoted(set_row.get('name', slug))}",
        f"set_slug: {yaml_plain(slug)}",
        f"set_id: {yaml_plain(set_row.get('set_id', ''))}",
        f"library: {yaml_plain(set_row.get('library', ''))}",
        f"pack: {yaml_plain(set_row.get('pack', ''))}",
        f"pack_kind: {yaml_plain(set_row.get('pack_kind', ''))}",
        f"vendor: {yaml_quoted(pack.get('vendor') or '')}",
        f"redistribute: {yaml_plain(pack.get('redistribute') or 'unknown')}",
        f"brush_count: {len(members)}",
        "eras: [" + ", ".join(eras) + "]",
        "kinds: [" + ", ".join(kinds) + "]",
        f"template: {TEMPLATE_NOTE}",
        FP_BLANK,
        "tags: [" + ", ".join(yaml_plain(tag) for tag in tags) + "]",
        "---",
        "",
        f"# {title}",
        "",
        "## Overview",
        "",
        overview(cat, set_row, pack, members, homed),
        "",
        AUTHOR_NOTE,
        "",
    ]
    for brush_id in homed:
        front.extend(brush_section(cat, cat.record(brush_id), headings[slug][brush_id], set_row))
    if shared:
        front.extend(["## Shared brushes", ""])
        for brush_id in shared:
            record = cat.record(brush_id)
            home_slug = home_of(record)
            home_row = cat.set_by_slug.get(home_slug)
            if home_row is None or home_row.get("note") is None or brush_id not in headings.get(home_slug, {}):
                raise NotesError(f"{brush_id} (in {slug}) has its home in {home_slug!r}, which has no note")
            name = one_line(record.get("display_name") or record.get("name") or "").strip() or "Untitled"
            target = home_row["note"][:-3]
            front.append(f"- `{brush_id}` {name}: see [[{target}#{link_heading(headings[home_slug][brush_id])}]]")
        front.append("")
    return sealed("\n".join(front) + "\n")


def _kind_text(kinds):
    return "/".join(kinds) if kinds else "none"


def note_bullet(cat, set_row, headings):
    """One map-of-content bullet for a note."""
    slug = set_row["set_slug"]
    members = members_of(set_row)
    homed = [cat.record(i) for i in members if home_of(cat.record(i)) == slug]
    pack = cat.pack(set_row.get("pack"))
    eras = sorted({str(r.get("era")) for r in homed})
    kinds = sorted({str((r.get("facets") or {}).get("kind")) for r in homed})
    title = link_label(set_row.get("title") or set_row.get("name") or slug)
    return (f"- [[{set_row['note'][:-3]}|{title}]]: {len(members)} {plural(len(members), 'brush', 'brushes')}"
            f" · {link_label(pack.get('vendor') or set_row.get('pack') or 'unknown')}"
            f" · {'/'.join(eras) if eras else 'none'} · {_kind_text(kinds)}")


def render_moc(cat, folder, rows, headings):
    """`<folder>/_index.md`: one bullet per note of the folder."""
    mine = sorted((r for r in rows if r["note"].startswith(folder + "/")),
                  key=lambda r: (str(r.get("title") or r.get("name") or "").casefold(), r["set_slug"]))
    brushes = sum(1 for r in mine for i in members_of(r) if home_of(cat.record(i)) == r["set_slug"])
    lines = ["---", f"title: {yaml_quoted(FOLDER_TITLES[folder] + ' - Index')}", "type: moc", f"folder: {folder}",
             f"note_count: {len(mine)}", f"template: {TEMPLATE_MOC}", FP_BLANK, "tags: [moc]", "---", "",
             f"# {FOLDER_TITLES[folder]}", "",
             f"{len(mine)} {plural(len(mine), 'note')}, {brushes:,} {plural(brushes, 'brush', 'brushes')} "
             f"whose first home is in this folder." if mine else "No notes in this folder yet.", ""]
    for row in mine:
        lines.append(note_bullet(cat, row, headings))
    if mine:
        lines.append("")
    lines += [AUTHOR_NOTE, ""]
    return sealed("\n".join(lines) + "\n")


def render_index(cat, rows, headings):
    """`00_INDEX.md`: counts, per-folder lists, facet-word and era tables."""
    counts = cat.counts if isinstance(cat.counts, dict) else {}
    by_library = counts.get("by_library") if isinstance(counts.get("by_library"), dict) else {}
    all_ids = [row["id"] for row in cat.brush_rows if isinstance(row, dict) and "id" in row]
    word_counts, era_counts = {}, {}
    for brush_id in all_ids:
        record = cat.record(brush_id)
        for word in set(record.get("facet_words") or []):
            word_counts[word] = word_counts.get(word, 0) + 1
        era_counts[str(record.get("era"))] = era_counts.get(str(record.get("era")), 0) + 1
    without = [r for r in cat.sets if r.get("note") is None]
    lines = ["---", 'title: "Brush Library - Index"', "type: index", f"template: {TEMPLATE_INDEX}", FP_BLANK,
             "tags: [index]", "---", "", "# Brush Library - Index", "",
             f"**{len(all_ids):,} brushes** in **{len(rows)} notes**, one note per brushset. Every note is "
             "generated from `catalog/`; the author's text lives under each note's `## Notes`.", "",
             "See also [[CLAUDE.md]] (how to work in this vault).", "", "## Counts", "",
             "| What | Count |", "|---|---|",
             f"| brushes (each counted once) | {len(all_ids):,} |",
             f"| places they occur | {counts.get('occurrences', 0):,} |",
             f"| sets and loose sets in the catalog | {len(cat.sets)} |",
             f"| notes | {len(rows)} |",
             f"| packs | {counts.get('packs', len(cat.packs))} |",
             f"| textures | {counts.get('textures', len(cat.textures)):,} |",
             f"| user library | {by_library.get('user', 0):,} |",
             f"| official library | {by_library.get('official', 0):,} |", ""]
    if without:
        names = ", ".join(f"`{one_line(r['set_slug'])}`" for r in sorted(without, key=lambda r: r["set_slug"]))
        lines += [f"{len(without)} {plural(len(without), 'set has', 'sets have')} no note, because every brush in "
                  f"{plural(len(without), 'it')} is already homed in a real set: {names}.", ""]
    lines += ["## Folders", ""]
    for folder in NOTE_FOLDERS:
        mine = sorted((r for r in rows if r["note"].startswith(folder + "/")),
                      key=lambda r: (str(r.get("title") or r.get("name") or "").casefold(), r["set_slug"]))
        brushes = sum(1 for r in mine for i in members_of(r) if home_of(cat.record(i)) == r["set_slug"])
        lines += [f"### {FOLDER_TITLES[folder]} ({len(mine)} {plural(len(mine), 'note')}, {brushes:,} "
                  f"{plural(brushes, 'brush', 'brushes')})", "", f"MOC: [[{folder}/_index|{FOLDER_TITLES[folder]} index]]", ""]
        for row in mine:
            lines.append(note_bullet(cat, row, headings))
        if mine:
            lines.append("")
    lines += ["## Format eras", "", "| Era | Brushes |", "|---|---|"]
    for era, n in sorted(era_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| {one_line(era)} | {n:,} |")
    lines += ["", "## Facet words", "",
              "The words each brush's `- facets:` line carries, over all brush records (a brush is counted once "
              "however many sets hold it). They are computed from the files by code; the thresholds behind the "
              "classes are heuristics (see [[CLAUDE.md]]).", "",
              "| Facet word | Brushes |", "|---|---|"]
    for word, n in sorted(word_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{one_line(word)}` | {n:,} |")
    lines += ["", AUTHOR_NOTE, ""]
    return sealed("\n".join(lines) + "\n")


def render_all(cat, only_slug=None):
    """{vault-relative path: generated text}, sorted by path. With `only_slug`,
    just that set's note (and nothing else)."""
    rows = note_sets(cat)
    headings = headings_for(cat, rows)
    out = {}
    for row in rows:
        if only_slug is None or row["set_slug"] == only_slug:
            out[row["note"]] = render_note(cat, row, headings)
    if only_slug is None:
        for folder in NOTE_FOLDERS:
            out[f"{folder}/{MOC_NAME}"] = render_moc(cat, folder, rows, headings)
        out[INDEX_NAME] = render_index(cat, rows, headings)
    return dict(sorted(out.items()))


# ── comparing with the disk ──────────────────────────────────────────────────

class Outcome:
    def __init__(self, status, text=None, plus=0, minus=0, reason="", lost=(), diff=()):
        self.status, self.text, self.plus, self.minus = status, text, plus, minus
        self.reason, self.lost, self.diff = reason, list(lost), list(diff)


def split_at_notes(text):
    """(generated, tail) split at the last line that is exactly `## Notes`, or
    None. The tail starts at that line and is the author's."""
    last = None
    for match in NOTES_LINE.finditer(text):
        last = match
    return None if last is None else (text[:last.start()], text[last.start():])


def _delta(old, new):
    """Lines (removed, added) between two texts."""
    a, b = old.split("\n"), new.split("\n")
    removed = added = 0
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "delete"):
            removed += i2 - i1
        if tag in ("replace", "insert"):
            added += j2 - j1
    return removed, added


def _diff_lines(path, old, new):
    return list(difflib.unified_diff(old.split("\n"), new.split("\n"), fromfile=f"a/{path}",
                                     tofile=f"b/{path}", lineterm="", n=1))


def classify(path, existing, generated, *, overwrite=False):
    """What `write` does with one file: `existing` is the text on disk or None."""
    if existing is None:
        return Outcome(NEW, generated + NOTES_HEADING + "\n", plus=generated.count("\n") + 1,
                       diff=_diff_lines(path, "", generated + NOTES_HEADING + "\n"))
    parts = split_at_notes(existing)
    if parts is None:
        return Outcome(REFUSED, reason="it has no `## Notes` line, so the author's text cannot be told from the "
                                       "generated part; put your text under a `## Notes` heading by hand")
    old, tail = parts
    old_lf = old.replace("\r\n", "\n")
    if old_lf == generated:
        return Outcome(UNCHANGED)
    removed, added = _delta(old_lf, generated)
    hand_edited = not fingerprint_holds(old_lf)
    lost_lines = []
    if hand_edited:
        old_lines, new_lines = old_lf.split("\n"), generated.split("\n")
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
        for tag, i1, i2, _j1, _j2 in matcher.get_opcodes():
            if tag in ("replace", "delete"):
                lost_lines.extend(old_lines[i1:i2])
        if not overwrite:
            return Outcome(REFUSED, plus=added, minus=removed, lost=lost_lines,
                           reason="the generated part was edited by hand (its fingerprint does not match its "
                                  "text); nothing is written. Move your text under `## Notes`, or pass "
                                  "--overwrite-generated to replace the generated part")
    return Outcome(CHANGED, generated + tail, plus=added, minus=removed, lost=lost_lines if hand_edited else (),
                   reason="overwrites hand edits" if hand_edited else "",
                   diff=_diff_lines(path, old_lf, generated))


def target_path(vault, rel):
    """The file for a vault-relative path, refused if it would leave the vault."""
    vault_root = Path(vault).resolve()
    target = (vault_root / rel).resolve()
    if vault_root != target and vault_root not in target.parents:
        raise NotesError(f"{rel} would be written outside the vault")
    return target


def read_existing(vault, rel):
    path = target_path(vault, rel)
    if not path.exists():
        return None
    if not path.is_file():
        raise NotesError(f"{rel} exists and is not a file")
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return ""      # not text we can split: classify() refuses it (no `## Notes`)


def find_orphans(vault, expected):
    """Generated notes under the four folders that no set of the catalog asks for."""
    found = []
    root = Path(vault)
    for folder in NOTE_FOLDERS:
        directory = root / folder
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            rel = f"{folder}/{path.name}"
            if rel in expected or path.name == MOC_NAME:
                continue
            try:
                head = path.read_bytes()[:4096].decode("utf-8", errors="replace")
            except OSError:
                continue
            if _looks_generated(head):
                found.append(rel)
    return found


def _looks_generated(head):
    return head.startswith("---\n") and "type: brushset" in head and "generated_fingerprint:" in head


# ── commands ─────────────────────────────────────────────────────────────────

def plan(paths, *, only=None, overwrite=False, say=print):
    """Compare every expected file with the disk. Returns (outcomes, orphans)
    where outcomes is {rel: Outcome}."""
    cat = Catalog(paths.catalog)
    only_slug = None
    if only is not None:
        rows = note_sets(cat)
        matches = [r for r in cat.sets if r["set_slug"] == only or r.get("pack") == only]
        if not matches:
            raise UsageProblem(f"--only {only!r}: there is no set slug or pack id of that name in the catalog")
        slugs = {r["set_slug"] for r in matches if r.get("note") is not None}
        for r in matches:
            if r.get("note") is None:
                say(f"skipped   {r['set_slug']} has no note (all its brushes are homed in another set)")
        if not slugs:
            return {}, []
        rendered = {}
        headings = headings_for(cat, rows)
        for row in rows:
            if row["set_slug"] in slugs:
                rendered[row["note"]] = render_note(cat, row, headings)
        rendered = dict(sorted(rendered.items()))
    else:
        rendered = render_all(cat)
    outcomes = {}
    for rel, generated in rendered.items():
        existing = read_existing(paths.vault, rel)
        outcomes[rel] = classify(rel, existing, generated, overwrite=overwrite)
    orphans = [] if only is not None else find_orphans(paths.vault, set(rendered))
    return outcomes, orphans


def _print_outcome(rel, outcome, show_diff, say):
    if outcome.status == CHANGED:
        extra = f"  ({outcome.reason})" if outcome.reason else ""
        say(f"{'changed':<10}{rel}  (+{outcome.plus} -{outcome.minus}){extra}")
    elif outcome.status == REFUSED:
        say(f"{'REFUSED':<10}{rel}  {outcome.reason}")
    else:
        say(f"{outcome.status:<10}{rel}")
    if outcome.lost and outcome.status in (CHANGED, REFUSED):
        shown = outcome.lost[:30]
        say(f"          {'lines lost' if outcome.status == CHANGED else 'lines that differ'} "
            f"({len(outcome.lost)}):")
        for line in shown:
            say(f"            - {line}")
        if len(outcome.lost) > len(shown):
            say(f"            ... and {len(outcome.lost) - len(shown)} more")
    if show_diff and outcome.diff and outcome.status in (NEW, CHANGED):
        for line in outcome.diff:
            say(line)


def run_write(paths, *, only=None, show_diff=False, overwrite=False, confirm=False, say=print):
    outcomes, orphans = plan(paths, only=only, overwrite=overwrite, say=say)
    for rel, outcome in outcomes.items():
        _print_outcome(rel, outcome, show_diff, say)
    for rel in orphans:
        say(f"{'orphan':<10}{rel}  (no set of the catalog asks for it; it is never deleted)")
    tally = _tally(outcome.status for outcome in outcomes.values())
    say(f"SUMMARY   {len(outcomes)} files: {tally.get(NEW, 0)} new, {tally.get(CHANGED, 0)} changed, "
        f"{tally.get(UNCHANGED, 0)} unchanged, {tally.get(REFUSED, 0)} refused, {len(orphans)} orphan")
    refused = tally.get(REFUSED, 0)
    if not confirm:
        say(DRY_RUN_LINE)
        return bc.EXIT_REFUSED if refused else bc.EXIT_OK
    written = 0
    for rel, outcome in outcomes.items():
        if outcome.status in (NEW, CHANGED):
            bc.write_text(target_path(paths.vault, rel), outcome.text)
            written += 1
    say(f"WROTE     {written} {plural(written, 'file')}"
        + (f"; {refused} refused, nothing written for {plural(refused, 'it', 'them')}" if refused else ""))
    return bc.EXIT_REFUSED if refused else bc.EXIT_OK


def run_check(paths, say=print):
    outcomes, orphans = plan(paths, say=say)
    drift = 0
    for rel, outcome in outcomes.items():
        if outcome.status == UNCHANGED:
            continue
        drift += 1
        if outcome.status == NEW:
            say(f"{'missing':<10}{rel}")
        else:
            _print_outcome(rel, outcome, False, say)
    for rel in orphans:
        drift += 1
        say(f"{'orphan':<10}{rel}  (no set of the catalog asks for it)")
    if drift:
        say(f"DRIFT     {drift} of {len(outcomes)} files do not match the catalog; "
            "`notes.py write` shows the plan")
        return bc.EXIT_REFUSED
    say(f"OK        {len(outcomes)} files match the catalog")
    return bc.EXIT_OK


# ── the command line ─────────────────────────────────────────────────────────

def _add_roots(parser, default):
    for name in ("root", "catalog", "vault"):
        parser.add_argument(bc.FLAGS[name], metavar="DIR", default=default, help=bc.FLAG_HELP[name])


def build_parser():
    parser = argparse.ArgumentParser(
        prog="notes.py",
        description="Write one Markdown note per brushset from the catalog. `write` is a dry run "
                    "without --confirm; only the generated part of a note is ever rewritten.")
    _add_roots(parser, None)
    verbs = parser.add_subparsers(dest="verb", metavar="{write,check}", required=True)
    write = verbs.add_parser("write", help="create or refresh the notes (a dry run without --confirm)")
    write.add_argument("--only", metavar="S", help="the note of one set slug or pack id; the indexes are left alone")
    write.add_argument("--diff", action="store_true", help="print what would change, as a unified diff")
    write.add_argument("--overwrite-generated", action="store_true",
                       help="replace a generated part that was edited by hand (shows the lost lines; "
                            "still needs --confirm)")
    write.add_argument("--confirm", action="store_true", help="really write")
    check = verbs.add_parser("check", help="exit 1 when any note differs from what the catalog gives; "
                                           "writes nothing")
    for sub in (write, check):
        _add_roots(sub, argparse.SUPPRESS)
    return parser


def main(argv=None):
    bc.open_console()
    args = build_parser().parse_args(argv)
    paths = bc.paths_from_args(args)
    try:
        if args.verb == "check":
            return run_check(paths)
        return run_write(paths, only=args.only, show_diff=args.diff, overwrite=args.overwrite_generated,
                         confirm=args.confirm)
    except NotesError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return bc.EXIT_REFUSED
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        print(f"error: the catalog is not shaped as F5 says ({type(exc).__name__}: {exc}); "
              "run `ingest.py build` again", file=sys.stderr)
        return bc.EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
