#!/usr/bin/env python3
"""Lexical, tag and settings search over the brush library.

Standard library only: no network, no embeddings, no local model. It is the
Procreate-brush counterpart of the creative-writing vault's vault_search.py and
follows docs/CONTRACTS.md F9 (the engine) and F11 (the command line).

One chunk per brush is ranked by TF-IDF cosine over the brush's name, set title,
tags, visual sentence, facet words and texture names. The numbers in a brush's
settings are never vectorised; they answer `--where` filters and `similar`.
Everything the index holds about a brush comes from catalog/brushes/<id>.json
(facets, facet words, preview, settings, content hash), from the notes (heading
and line range), and from the tag sidecars; this tool derives no facet.

    python -I brushes/vault/tools/brush_search.py index [--check]
    python -I brushes/vault/tools/brush_search.py search "dry grainy ink" [--top 5] [--json]
    python -I brushes/vault/tools/brush_search.py search --tag medium=watercolor --where kind=stroke
    python -I brushes/vault/tools/brush_search.py similar b_0123456789ab [--other-sets]
    python -I brushes/vault/tools/brush_search.py facets | files | chunks NOTE | verify | brush ID

Exit codes: 0 ok (an empty result too), 1 refused or failed (id not found, a
stale index under `index --check`), 2 usage or environment (a bad argument, an
unknown tag axis, value or filter key, a missing index or catalog).

Library use: other modules load this file with
importlib.util.spec_from_file_location and call the functions listed in
__all__. They raise UsageError (exit 2) or NotFound (exit 1); only main() exits.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import os
import re
import struct
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

__all__ = [
    "UsageError", "NotFound", "load_index", "build_index", "check_fresh", "search_index", "similar",
    "facet_counts", "chunks_for", "resolve_brush", "load_vocabulary", "tokenize", "main",
]

# ── constants ────────────────────────────────────────────────────────────────

ENGINE = "brush_search/1"
INDEX_SCHEMA = 1
TOKENIZER_VERSION = "t1"
CHUNKER_VERSION = "b1"
SIMILAR_METHOD = "gower-v1"
SIMILAR_WEIGHTS = {"default": 1, "shape_ref": 4, "grain_ref": 3}   # == spec.yaml similar.weights
VISUAL_BASIS = "described-not-measured"
UNVERIFIED_MARKER = "[UNVERIFIED -- not found in source text, do not cite as exact]"

AXES = ("medium", "mark", "texture", "edge", "motif", "use")
TAG_FIELDS = tuple(f"{axis}_tags" for axis in AXES)
TAG_CAPS = {"medium": 2, "mark": 2, "texture": 3, "edge": 2, "motif": 2, "use": 3}
SOURCE_TYPES = ("brush", "set", "index", "moc", "guide")
STATES = ("tagged", "stale", "untagged")

ENV_ROOT = "ROSW_BRUSHES_ROOT"
ENV_LIBRARY = "ROSW_BRUSHES_LIBRARY"
ENV_CATALOG = "ROSW_BRUSHES_CATALOG"
ENV_VAULT = "ROSW_BRUSHES_VAULT"
ENV_INDEX = "ROSW_BRUSHES_INDEX"
ENV_NAMES = {"root": ENV_ROOT, "library": ENV_LIBRARY, "catalog": ENV_CATALOG,
             "vault": ENV_VAULT, "index": ENV_INDEX}

TOOL_VAULT = Path(__file__).resolve().parents[1]        # brushes/vault
TOOL_ROOT = TOOL_VAULT.parent                           # brushes/
SCHEMA_KEYS = TOOL_ROOT / "schema" / "silica_keys.json"

BRUSH_ID_RE = re.compile(r"^b_[0-9a-f]{12}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
EXCLUDE_NAMES = frozenset({"README.md", "OBSIDIAN.md", "CLAUDE.md", "CONVENTIONS.md"})
EXCLUDE_DIRS = frozenset({".git", ".obsidian", "tools", "_BrushTags", "_Previews"})
NUMBERED_DIR_RE = re.compile(r"^\d{2}_")
GUIDES_DIR = "_Guides"

EXPAND_WEIGHT = 0.35          # most one added term counts, against 1 for a word the user typed
EXPAND_FLOOR = 0.10           # least one added term counts, however many a group adds
EXPAND_MASS = 1.0             # the terms a vocabulary group adds share this weight (above the floor)
BUILTIN_KEYS = ("id", "set", "library", "pack", "tagged")
NUMERIC_ENUM_MAX = 12         # an integer key with at most this many values is an enum when no schema says so


class UsageError(Exception):
    """A bad argument or an environment problem: exit 2."""
    exit_code = 2


class NotFound(Exception):
    """A requested brush, note or file does not exist: exit 1."""
    exit_code = 1


# ── paths ────────────────────────────────────────────────────────────────────

def _env(name, environ):
    value = (os.environ if environ is None else environ).get(name)
    return value if value and value.strip() else None


def resolve_roots(vault=None, catalog=None, index=None, environ=None):
    """(vault, catalog, index) as absolute paths. Order for each: the flag, the
    folder's own variable, ROSW_BRUSHES_ROOT (<ROOT>/vault, <ROOT>/catalog), then
    this tool's own vault and the catalog/ beside it. An empty value is absent.
    The index defaults to <vault>/tools/rag_index/index.json."""
    root = _env(ENV_ROOT, environ)
    vault = vault or _env(ENV_VAULT, environ) or (Path(root) / "vault" if root else TOOL_VAULT)
    catalog = catalog or _env(ENV_CATALOG, environ) or (Path(root) / "catalog" if root else TOOL_ROOT / "catalog")
    vault, catalog = Path(vault).resolve(), Path(catalog).resolve()
    index = index or _env(ENV_INDEX, environ) or (vault / "tools" / "rag_index" / "index.json")
    return vault, catalog, Path(index).resolve()


def _paths(vault, catalog):
    return Path(vault), Path(catalog)


# ── text files ───────────────────────────────────────────────────────────────

def read_text(path):
    """A file as text with LF line ends and no byte-order mark."""
    with open(path, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    if text.startswith("﻿"):
        text = text[1:]
    return text.replace("\r\n", "\n").replace("\r", "\n")


def write_text_atomic(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.replace(tmp, path)


def json_text(value):
    """The one spelling of generated JSON (brush_common.json_text, restated here
    because a vault tool imports nothing from pipeline/)."""
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ── tokenizer t1 ─────────────────────────────────────────────────────────────

STOPWORDS = frozenset("""
a an the and or but nor so yet if then than of in on at to for with without by from as is are was were be been
being am it its this that these those i me my we our you your he she him her his hers they them their there here
what which who whom when where why how do does did have has had will would can could should may might must shall
not also into onto upon about via per
""".split())

_ID_RE = re.compile(r"\bb_[0-9a-f]{12}\b")
_HASH_RE = re.compile(r"\bsha256:[0-9a-f:]+")
_POSSESSIVE_RE = re.compile(r"'s\b")
_WORD_RE = re.compile(r"[^\W_]+(?:\.[0-9]+[^\W_]*)*")
_CAMEL_LOWER_UPPER = re.compile(r"(?<=[a-z])(?=[A-Z])")
_CAMEL_ACRONYM = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])")
_PARTS_RE = re.compile(r"\d+(?:\.\d+)?[a-z]{1,2}(?![a-z0-9])|\d+(?:\.\d+)?|[a-z]{1,2}\d+(?![a-z0-9.])|[a-z]+"
                       r"|[^\x00-\x7f]+")


def fold(text):
    """Typographic apostrophes to ', accents and other combining marks dropped."""
    text = text.replace("’", "'").replace("‘", "'").replace("ʼ", "'")
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def stem(token):
    """Light plural stemming, no Porter: ies to y, sses|shes|ches|xes|zzes lose
    `es`, a final s goes unless it follows a, i, o, s or u."""
    if len(token) <= 3 or not token.isascii() or any(ch.isdigit() for ch in token):
        return token
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    for suffix in ("sses", "shes", "ches", "xes", "zzes"):
        if token.endswith(suffix):
            return token[:-2]
    if token.endswith("s") and token[-2] not in "aiosu":
        return token[:-1]
    return token


def tokenize(text):
    """Tokenizer t1, the same on the index and the query side.

    `b_` ids are kept whole and hashes dropped; possessives go; words are runs of
    letters and digits (a decimal such as 0.5 stays whole); camelCase splits and
    a split alphabetic word also emits its joined form; digits stay (6b, 3d, p5);
    colour becomes color and grey gray; stopwords and single letters are dropped
    unless the source word was ALL CAPS ("AN"); plurals are stemmed lightly."""
    if not text:
        return []
    text = fold(str(text))
    tokens = _ID_RE.findall(text)
    text = _HASH_RE.sub(" ", _ID_RE.sub(" ", text))
    text = _POSSESSIVE_RE.sub("", text).replace("'", "")
    for word in _WORD_RE.findall(text):
        capital = len(word) > 1 and word.isupper()
        spaced = _CAMEL_ACRONYM.sub(" ", _CAMEL_LOWER_UPPER.sub(" ", word))
        pieces = spaced.split()
        emitted = []
        for piece in pieces:
            piece = piece.lower().replace("colour", "color").replace("grey", "gray")
            for part in _PARTS_RE.findall(piece):
                if part.isascii() and part.isalpha():
                    if len(part) == 1:
                        continue
                    if part in STOPWORDS and not capital:
                        continue
                emitted.append(stem(part))
        if len(pieces) > 1 and word.isalpha() and word.isascii():
            joined = word.lower().replace("colour", "color").replace("grey", "gray")
            emitted.append(stem(joined))
        tokens.extend(emitted)
    return tokens


# ── vocabulary ───────────────────────────────────────────────────────────────

_VOCAB_HEAD_RE = re.compile(r"^([a-z][a-z_]*):\s*(?:#.*)?$")
_VOCAB_ITEM_RE = re.compile(r"^  - ([a-z0-9][a-z0-9-]*)\s*(?:#\s*(.*?))?\s*$")
_ALSO_RE = re.compile(r"\s*\[also:\s*([^\]]*)\]\s*$")
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class Vocabulary(dict):
    """{axis: [{"tag", "definition"}]} keyed by short axis name (`medium`). A
    lookup also accepts the stored key (`medium_tags`)."""

    @staticmethod
    def _key(key):
        return key[:-5] if isinstance(key, str) and key.endswith("_tags") and key[:-5] in AXES else key

    def __getitem__(self, key):
        return super().__getitem__(self._key(key))

    def __contains__(self, key):
        return super().__contains__(self._key(key))

    def get(self, key, default=None):
        return super().get(self._key(key), default)


def parse_vocabulary_text(text, source="vocabulary.yaml"):
    """The restricted YAML of vocabulary.yaml read by lines: top-level
    `<axis>_tags:` keys, two-space `- tag` items, one `#` definition per tag on
    the same line (a trailing `[also: a, b]` lists synonyms the search expands).
    Returns {stored key: [{"tag", "definition", "synonyms"}]}. Anything else is
    a UsageError that names the line."""
    result = {}
    current = None
    for number, line in enumerate(text.split("\n"), start=1):
        if not line.strip() or line.lstrip().startswith("#") and not line.startswith("  - "):
            continue
        head = _VOCAB_HEAD_RE.match(line)
        if head:
            key = head.group(1)
            if key not in TAG_FIELDS:
                raise UsageError(f"{source} line {number}: `{key}:` is not one of {', '.join(TAG_FIELDS)}")
            if key in result:
                raise UsageError(f"{source} line {number}: `{key}:` appears twice")
            current = result[key] = []
            continue
        item = _VOCAB_ITEM_RE.match(line)
        if item and current is not None:
            tag, comment = item.group(1), item.group(2) or ""
            synonyms = []
            also = _ALSO_RE.search(comment)
            if also:
                synonyms = [s.strip().lower() for s in also.group(1).split(",") if s.strip()]
                comment = comment[:also.start()]
            if any(entry["tag"] == tag for entry in current):
                raise UsageError(f"{source} line {number}: tag `{tag}` appears twice in one axis")
            current.append({"tag": tag, "definition": comment.strip(), "synonyms": synonyms})
            continue
        raise UsageError(f"{source} line {number}: cannot read `{line.strip()[:60]}` "
                         "(expected `<axis>_tags:` or `  - tag   # definition`)")
    return result


def load_vocabulary_full(vault):
    path = Path(vault) / "_BrushTags" / "vocabulary.yaml"
    if not path.is_file():
        raise UsageError(f"no vocabulary at {path.name} under _BrushTags/ of the vault")
    return parse_vocabulary_text(read_text(path), "_BrushTags/vocabulary.yaml")


def load_vocabulary(vault):
    """{axis: [{"tag", "definition"}]}, the axes in the order of AXES. The
    dictionary is keyed by short axis name and also answers `medium_tags`."""
    full = load_vocabulary_full(vault)
    out = Vocabulary()
    for axis, key in zip(AXES, TAG_FIELDS):
        if key in full:
            out[axis] = [{"tag": e["tag"], "definition": e["definition"]} for e in full[key]]
    return out


def vocabulary_fingerprint(vocab):
    """`sha256:16:<hex>` of the canonical JSON of {stored key: sorted tags}."""
    canon = {key: sorted(e["tag"] for e in vocab.get(key, [])) for key in TAG_FIELDS}
    text = json.dumps(canon, sort_keys=True, separators=(",", ":"))
    return "sha256:16:" + _sha256_text(text)[:16]


def _vocab_tags(vocab_by_key):
    return {key: {e["tag"] for e in vocab_by_key.get(key, [])} for key in TAG_FIELDS}


def _expansions(full):
    groups = []
    for key in TAG_FIELDS:
        for entry in full.get(key, []):
            phrases = [tokenize(entry["tag"].replace("-", " "))] + [tokenize(s) for s in entry["synonyms"]]
            phrases = [p for p in phrases if p]
            # Every phrase can trigger the group; only the tag's own words and the
            # one-word synonyms are added to the query, so "clip art" does not add "art".
            seen, terms = set(), []
            for n, phrase in enumerate(phrases):
                if n and len(phrase) > 1:
                    continue
                for token in phrase:
                    if token not in seen:
                        seen.add(token)
                        terms.append(token)
            unique = []
            for phrase in phrases:
                if phrase not in unique:
                    unique.append(phrase)
            groups.append({"tag": f"{key[:-5]}:{entry['tag']}", "phrases": unique, "terms": terms})
    return groups


# ── notes ────────────────────────────────────────────────────────────────────

_HEADING_RE = re.compile(r"^## +(\S.*?) *$")
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_BRUSH_LINE_RE = re.compile(r"^- id: `(b_[0-9a-f]{12})`")
_STUB_RE = re.compile(r"^- `(b_[0-9a-f]{12})`")


def _flat_yaml(lines):
    out = {}
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            out[key.strip()] = [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()]
        else:
            out[key.strip()] = value.strip('"').strip("'")
    return out


def parse_note(text):
    """A note as {"frontmatter", "line_count", "sections"}. Line numbers are
    1-based file lines (frontmatter included). A section is the preamble
    (chunk 0, when it has text) or one `## ` heading to the line before the
    next, outside code fences, with trailing blank lines trimmed. A section
    whose first list line is ``- id: `b_...` `` is a brush section."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    start, frontmatter = 0, {}
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                frontmatter, start = _flat_yaml(lines[1:i]), i + 1
                break
    heads, fence = [], None
    for i in range(start, len(lines)):
        line = lines[i]
        marker = _FENCE_RE.match(line)
        if fence is not None:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence) \
                    and line.strip() == marker.group(1):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        found = _HEADING_RE.match(line)
        if found:
            heads.append((i, found.group(1)))

    def trimmed(first, last):
        while first <= last and not lines[first].strip():
            first += 1
        while last >= first and not lines[last].strip():
            last -= 1
        return first, last

    sections = []
    pre_first, pre_last = trimmed(start, (heads[0][0] - 1) if heads else len(lines) - 1)
    if pre_first <= pre_last:
        sections.append({"chunk_index": 0, "heading": None, "start_line": pre_first + 1,
                         "end_line": pre_last + 1, "brush_id": None, "shared": [],
                         "text": "\n".join(lines[pre_first:pre_last + 1])})
    for n, (at, title) in enumerate(heads, start=1):
        limit = (heads[n][0] - 1) if n < len(heads) else len(lines) - 1
        first, last = trimmed(at, limit)
        body = [ln for ln in lines[at + 1:last + 1] if ln.strip()]
        brush_id = None
        if body:
            found = _BRUSH_LINE_RE.match(body[0])
            brush_id = found.group(1) if found else None
        if not body and brush_id is None:
            continue
        shared = []
        if title == "Shared brushes":
            shared = [m.group(1) for m in (_STUB_RE.match(ln) for ln in lines[at + 1:last + 1]) if m]
        sections.append({"chunk_index": n, "heading": title, "start_line": at + 1, "end_line": last + 1,
                         "brush_id": brush_id, "shared": shared, "text": "\n".join(lines[at:last + 1])})
    return {"frontmatter": frontmatter, "line_count": len(lines), "sections": sections}


def _note_sort_key(rel):
    return rel.casefold(), rel


def iter_notes(vault):
    """(vault-relative POSIX path, source_type) for every note, sorted."""
    vault = Path(vault)
    found = []
    if not vault.is_dir():
        return found
    if (vault / "00_INDEX.md").is_file():
        found.append(("00_INDEX.md", "index"))
    for entry in sorted(vault.iterdir(), key=lambda p: p.name):
        if not entry.is_dir() or entry.name in EXCLUDE_DIRS or entry.name.startswith("."):
            continue
        if NUMBERED_DIR_RE.match(entry.name):
            kind = None
        elif entry.name == GUIDES_DIR:
            kind = "guide"
        else:
            continue
        rels = []
        for path in entry.rglob("*.md"):
            parts = path.relative_to(vault).parts
            if any(p.startswith(".") or p in EXCLUDE_DIRS for p in parts[:-1]) or path.name in EXCLUDE_NAMES:
                continue
            rels.append("/".join(parts))
        for rel in sorted(rels, key=_note_sort_key):
            found.append((rel, kind or ("moc" if rel.rsplit("/", 1)[-1] == "_index.md" else "set")))
    return found


# ── catalog ──────────────────────────────────────────────────────────────────

def load_catalog_json(catalog):
    path = Path(catalog) / "catalog.json"
    if not path.is_file():
        raise UsageError(f"no catalog at {path.parent.name}/catalog.json -- run `python -I brushes/pipeline/ingest.py build`")
    try:
        return json.loads(read_text(path))
    except ValueError as err:
        raise UsageError(f"catalog.json is not valid JSON: {err}") from None


def record_ids(catalog):
    folder = Path(catalog) / "brushes"
    if not folder.is_dir():
        return []
    return sorted(p.stem for p in folder.glob("b_*.json") if BRUSH_ID_RE.match(p.stem))


def load_record(catalog, brush_id):
    if not isinstance(brush_id, str) or not BRUSH_ID_RE.match(brush_id):
        raise UsageError(f"`{brush_id}` is not a brush id (b_ and 12 hex characters)")
    path = Path(catalog) / "brushes" / f"{brush_id}.json"
    if not path.is_file():
        raise NotFound(f"no catalog record for {brush_id}")
    try:
        return json.loads(read_text(path))
    except ValueError as err:
        raise UsageError(f"{path.name} is not valid JSON: {err}") from None


# ── sidecars ─────────────────────────────────────────────────────────────────

def sidecar_path(vault, note):
    return Path(vault) / "_BrushTags" / (note + ".tags.json")


def read_sidecars(vault):
    """Every sidecar under _BrushTags/ as {"path": vault-relative, "note", "data",
    "error"}, sorted by path. A file that does not parse has data None."""
    base = Path(vault) / "_BrushTags"
    found = []
    if not base.is_dir():
        return found
    rels = sorted(("/".join(p.relative_to(base).parts) for p in base.rglob("*.tags.json")), key=_note_sort_key)
    for rel in rels:
        entry = {"path": "_BrushTags/" + rel, "note": rel[:-len(".tags.json")], "data": None, "error": None}
        try:
            data = json.loads(read_text(base / rel))
            if not isinstance(data, dict):
                raise ValueError("the top level is not an object")
            entry["data"] = data
        except (OSError, ValueError) as err:
            entry["error"] = str(err)
        found.append(entry)
    return found


def entry_state(entry, content_sha256):
    """`tagged` when the entry's hash is the brush's, `stale` when it differs."""
    return "tagged" if isinstance(entry, dict) and entry.get("content_sha256") == content_sha256 else "stale"


def resolve_entries(sidecars, hashes):
    """Per brush id the sidecar entry to use, across all sidecars: a current
    entry beats a stale one, then the later `tagged`, then the earlier path.
    Returns ({id: {"entry", "path", "state"}}, orphans, divergent) where orphans
    are (path, id) of entries whose id is no brush and divergent the ids with
    two current entries that carry different tags."""
    chosen, orphans, seen_current = {}, [], {}
    for sc in sidecars:
        brushes = (sc["data"] or {}).get("brushes")
        if not isinstance(brushes, dict):
            continue
        for brush_id in sorted(brushes):
            entry = brushes[brush_id]
            if brush_id not in hashes:
                orphans.append((sc["path"], brush_id))
                continue
            if not isinstance(entry, dict):
                continue
            state = entry_state(entry, hashes[brush_id])
            rank = (state == "tagged", str(entry.get("tagged") or ""))
            best = chosen.get(brush_id)
            if best is None or rank > best["rank"]:
                chosen[brush_id] = {"entry": entry, "path": sc["path"], "state": state, "rank": rank}
            if state == "tagged":
                signature = json.dumps({k: entry.get(k) for k in TAG_FIELDS}, sort_keys=True)
                seen_current.setdefault(brush_id, set()).add(signature)
    divergent = sorted(i for i, sigs in seen_current.items() if len(sigs) > 1)
    return chosen, orphans, divergent


# ── fingerprints ─────────────────────────────────────────────────────────────

def _group_digest(items):
    digest = hashlib.sha256()
    for rel, text_digest in items:
        digest.update(rel.encode("utf-8") + b"\0" + text_digest.encode("ascii") + b"\n")
    return digest.hexdigest()


def input_groups(vault, catalog):
    """sha256 per group of inputs: notes, sidecars, the vocabulary, the catalog
    (catalog.json and every brush record). No absolute path enters a digest."""
    vault, catalog = _paths(vault, catalog)

    def digest_of(path):
        try:
            return _sha256_text(read_text(path))
        except OSError:
            return "-"

    notes = [(rel, digest_of(vault / rel)) for rel, _ in iter_notes(vault)]
    sidecars = [(sc["path"], digest_of(vault / sc["path"])) for sc in read_sidecars(vault)]
    vocab = vault / "_BrushTags" / "vocabulary.yaml"
    vocabulary = [("vocabulary.yaml", digest_of(vocab) if vocab.is_file() else "-")]
    cat = [("catalog.json", digest_of(catalog / "catalog.json") if (catalog / "catalog.json").is_file() else "-")]
    cat += [(f"brushes/{i}.json", digest_of(catalog / "brushes" / f"{i}.json")) for i in record_ids(catalog)]
    return {"notes": _group_digest(notes), "sidecars": _group_digest(sidecars),
            "vocabulary": _group_digest(vocabulary), "catalog": _group_digest(cat)}


def _combined(groups):
    return "sha256:" + _sha256_text(json.dumps(groups, sort_keys=True, separators=(",", ":")) +
                                    f"|{ENGINE}|{TOKENIZER_VERSION}|{CHUNKER_VERSION}")


# ── settings helpers ─────────────────────────────────────────────────────────

def scalar(value):
    """A settings value as a number, bool or string, or None when it has no
    scalar form. A real tag such as {"$real32": "80000000"} is opened."""
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict) and len(value) == 1:
        (tag, inner), = value.items()
        if tag in ("$real32", "$real64"):
            if isinstance(inner, (int, float)) and not isinstance(inner, bool):
                return float(inner)
            if isinstance(inner, str):
                try:
                    raw = bytes.fromhex(inner)
                    if tag == "$real32" and len(raw) == 4:
                        return struct.unpack(">f", raw)[0]
                    if tag == "$real64" and len(raw) == 8:
                        return struct.unpack(">d", raw)[0]
                except ValueError:
                    return None
        if tag == "$int" and isinstance(inner, int) and not isinstance(inner, bool):
            return inner
    return None


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def load_schema_rows(path=None):
    """{key: row} from schema/silica_keys.json, or {} when it cannot be read."""
    try:
        data = json.loads(read_text(Path(path) if path else SCHEMA_KEYS))
        return {row["key"]: row for row in data.get("keys", []) if isinstance(row, dict) and "key" in row}
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def _excluded_feature(key):
    return key in {"paintSize", "paintOpacity", "smudgeSize", "smudgeOpacity", "eraseSize", "eraseOpacity",
                   "previewSize", "version", "creationDate", "color", "name", "authorName"} \
        or key.endswith("Version") or key.startswith("saved")


# ── building the index ───────────────────────────────────────────────────────

def _facet_text(record):
    words = record.get("facet_words") or []
    return " ".join(str(w) for w in words)


def _texture_names(record):
    names = []
    for part in ("shape", "grain"):
        name = ((record.get(part) or {}).get("bundled_name") or "")
        name = re.sub(r"\.[A-Za-z0-9]+$", "", name)
        name = re.sub(r"^Brush-Preset-", "", name)
        if name and name.lower() != "blank":
            names.append(name)
    return " ".join(names)


def _texture_ref(part):
    part = part or {}
    if part.get("texture_id"):
        return part["texture_id"]
    if part.get("bundled_name"):
        return "bundled:" + part["bundled_name"]
    return "none"


def _percentile(sorted_values, fraction):
    return sorted_values[int(round(fraction * (len(sorted_values) - 1)))]


def _build_param_stats(brush_chunks, rows, alias_map):
    """Feature table for `similar`: per key its kind (num, bool, enum), the 1st
    and 99th percentile for numbers, and the schema default. Keys that never
    vary are left out."""
    columns, kinds = {}, {}
    for chunk in brush_chunks:
        for key, form in chunk["settings"].items():
            key = alias_map.get(key, key)
            if _excluded_feature(key):
                continue
            value = scalar(form)
            if isinstance(value, bool) or _number(value):
                columns.setdefault(key, {})[chunk["brush_id"]] = value
    stats = {}
    total = len(brush_chunks)
    for key in sorted(columns):
        row = rows.get(key)
        observed = columns[key]
        default = scalar(row.get("default")) if row and row.get("default") is not None else None
        if row:
            kind = {"real": "num", "int": "enum", "bool": "bool"}.get(row.get("type"))
            if kind is None:
                continue
        elif all(isinstance(v, bool) for v in observed.values()):
            kind = "bool"
        elif all(isinstance(v, int) and not isinstance(v, bool) for v in observed.values()) \
                and len(set(observed.values())) <= NUMERIC_ENUM_MAX:
            kind = "enum"
        else:
            kind = "num"
        if default is not None and not (isinstance(default, bool) or _number(default)):
            default = None
        values = list(observed.values())
        if default is not None and len(observed) < total:
            values += [default] * (total - len(observed))
        if kind == "num":
            numeric = sorted(float(v) for v in values)
            lo, hi = _percentile(numeric, 0.01), _percentile(numeric, 0.99)
            if hi - lo <= 1e-12:
                continue
            stats[key] = {"kind": "num", "lo": lo, "hi": hi, "n": len(observed), "default": default}
        else:
            if len(set(values)) < 2:
                continue
            stats[key] = {"kind": kind, "lo": None, "hi": None, "n": len(observed), "default": default}
    return stats


def _alias_map(rows):
    """{alias: canonical key} from the schema's `aliases`; the canonical key of
    a pair is the one that sorts first."""
    mapping = {}
    for key, row in rows.items():
        for other in row.get("aliases") or []:
            mapping[max(key, other)] = min(key, other)
    return mapping


def _find_sections(vault, catalog_sets, warnings):
    """Parse each set note that is on disk. Returns ({note path: parsed}, missing)."""
    parsed, missing = {}, []
    for slug in sorted(catalog_sets):
        note = catalog_sets[slug].get("note")
        if not note:
            continue
        path = Path(vault) / note
        if path.is_file():
            parsed[note] = parse_note(read_text(path))
        else:
            missing.append(note)
    return parsed, missing


def build_index(vault, catalog, *, write=True, index_path=None):
    """Build the index from the notes, the tag sidecars, the vocabulary and the
    catalog. With write=True it is written (atomically) to `index_path`, by
    default <vault>/tools/rag_index/index.json or ROSW_BRUSHES_INDEX. The index
    holds no timestamp and no absolute path. Returns the index dictionary."""
    vault, catalog = _paths(vault, catalog)
    cat = load_catalog_json(catalog)
    sets = {row["set_slug"]: row for row in cat.get("sets", []) if isinstance(row, dict) and "set_slug" in row}
    warnings = []

    # vocabulary
    try:
        vocab_full = load_vocabulary_full(vault)
    except UsageError as err:
        if "no vocabulary" not in str(err):
            raise
        vocab_full = {}
        warnings.append("WARNING: no _BrushTags/vocabulary.yaml: no tag can be used")
    vocab_tags = _vocab_tags(vocab_full)
    vocab_embed = {key: [{"tag": e["tag"], "definition": e["definition"]} for e in vocab_full.get(key, [])]
                   for key in TAG_FIELDS}

    # records
    records = {}
    for brush_id in record_ids(catalog):
        records[brush_id] = load_record(catalog, brush_id)
    hashes = {i: r.get("content_sha256") for i, r in records.items()}

    # notes
    parsed, missing_notes = _find_sections(vault, sets, warnings)
    located, shared_in = {}, {}
    for note in sorted(parsed):
        for section in parsed[note]["sections"]:
            if section["brush_id"] and section["brush_id"] not in located:
                located[section["brush_id"]] = (note, section)
            for brush_id in section["shared"]:
                shared_in.setdefault(brush_id, set()).add(note)
    if missing_notes:
        warnings.append(f"NOTE: {len(missing_notes)} set note(s) are not on disk, so their brushes carry no "
                        "note location (run notes.py write --confirm, then index again)")

    # sidecars
    sidecars = read_sidecars(vault)
    for sc in sidecars:
        if sc["error"]:
            warnings.append(f"WARNING: sidecar {sc['path']} is not valid JSON and was ignored: {sc['error']}")
    chosen, orphans, divergent = resolve_entries(sidecars, hashes)
    stale_ids = sorted(i for i, c in chosen.items() if c["state"] == "stale")
    dropped = []
    if orphans:
        files = sorted({p for p, _ in orphans})
        warnings.append(f"WARNING: {len(orphans)} sidecar entries name a brush id found in no catalog record: "
                        + ", ".join(files))
    if divergent:
        warnings.append(f"WARNING: {len(divergent)} brush id(s) carry different tags in two sidecars: "
                        + ", ".join(divergent))

    # the chunk for each brush
    brush_chunks = []
    for brush_id, rec in records.items():
        home = (rec.get("home") or {})
        home_slug = home.get("set_slug") or rec.get("pack")
        set_row = sets.get(home_slug, {})
        found = located.get(brush_id)
        tag_lists = {key: [] for key in TAG_FIELDS}
        visual, state = "", "untagged"
        pick = chosen.get(brush_id)
        if pick:
            state = pick["state"]
            if state == "tagged":
                entry = pick["entry"]
                for key in TAG_FIELDS:
                    values = entry.get(key) or []
                    keep = []
                    for value in values if isinstance(values, list) else []:
                        if value in vocab_tags[key]:
                            if value not in keep:
                                keep.append(value)
                        else:
                            dropped.append(f"{key[:-5]}={value}")
                    tag_lists[key] = keep
                visual = str(entry.get("visual") or "")
        also_in = []
        for occ in sorted(rec.get("occurrences") or [], key=lambda o: (str(o.get("set_slug")), str(o.get("pack")))):
            slug = occ.get("set_slug")
            if slug == home_slug or any(a["set"] == slug for a in also_in):
                continue
            note = (sets.get(slug) or {}).get("note")
            also_in.append({"set": slug, "note": note,
                            "heading": "Shared brushes" if note and note in shared_in.get(brush_id, ()) else None})
        preview = rec.get("preview") or {}
        brush_chunks.append({
            "source_type": "brush", "brush_id": brush_id, "content_sha256": rec.get("content_sha256"),
            "name": rec.get("name"), "display_name": rec.get("display_name"),
            "set": home_slug, "set_title": set_row.get("title") or set_row.get("name") or home_slug,
            "library": rec.get("library"), "pack": rec.get("pack"), "era": rec.get("era"),
            "note": found[0] if found else None,
            "heading": found[1]["heading"] if found else None,
            "start_line": found[1]["start_line"] if found else None,
            "end_line": found[1]["end_line"] if found else None,
            "chunk_index": found[1]["chunk_index"] if found else None,
            "position": home.get("position"),
            "facets": rec.get("facets") or {}, "facet_words": rec.get("facet_words") or [],
            "preview": preview, "approximate": preview.get("stroke_source") == "rendered-approx",
            "settings": rec.get("settings") or {},
            "shape_ref": _texture_ref(rec.get("shape")), "grain_ref": _texture_ref(rec.get("grain")),
            "tag_state": state, **tag_lists, "visual": visual, "also_in": also_in,
            "_texture_names": _texture_names(rec), "_pack": str(rec.get("pack") or ""),
        })
    brush_chunks.sort(key=lambda c: (str(c["set"]), c["position"] if isinstance(c["position"], int) else 10 ** 9,
                                     c["brush_id"]))
    if dropped:
        shown = sorted(set(dropped))
        warnings.append(f"WARNING: {len(dropped)} tag(s) not in vocabulary.yaml were dropped: "
                        + ", ".join(shown[:20]) + (" ..." if len(shown) > 20 else ""))
    if stale_ids:
        warnings.append(f"WARNING: {len(stale_ids)} brush-tag mismatch(es) -- content hash changed, tags not "
                        "attached: " + ", ".join(stale_ids[:12]) + (" ..." if len(stale_ids) > 12 else ""))
    missing_sections = [c["brush_id"] for c in brush_chunks
                        if c["note"] is None and (sets.get(c["set"]) or {}).get("note") in parsed]
    if missing_sections:
        warnings.append(f"WARNING: {len(missing_sections)} brush(es) have no section in their set note "
                        "(notes.py check shows what changed): " + ", ".join(missing_sections[:12]))

    # chunks of the notes themselves
    note_chunks = []
    for rel, source_type in iter_notes(vault):
        if source_type == "set" and rel in parsed:
            parsed_note = parsed[rel]
        else:
            path = Path(vault) / rel
            try:
                parsed_note = parse_note(read_text(path))
            except OSError:
                continue
        fm = parsed_note["frontmatter"]
        slug = fm.get("set_slug") or (fm.get("set") if isinstance(fm.get("set"), str) else None) \
            or (rel.rsplit("/", 1)[-1][:-3] if source_type == "set" else None)
        for section in parsed_note["sections"]:
            if section["brush_id"] or section["shared"]:
                continue
            heading = section["heading"] or fm.get("title") or rel.rsplit("/", 1)[-1][:-3]
            note_chunks.append({
                "source_type": source_type, "brush_id": None, "name": heading,
                "set": slug, "set_title": fm.get("title") or slug, "library": fm.get("library") or None,
                "pack": fm.get("pack") or None, "note": rel, "heading": section["heading"],
                "start_line": section["start_line"], "end_line": section["end_line"],
                "chunk_index": section["chunk_index"],
                "snippet": " ".join(section["text"].split())[:200],
                "_text": (heading + " ") * 2 + section["text"],
            })

    chunks = note_chunks + brush_chunks

    # vectors
    tokenized = []
    for chunk in chunks:
        if chunk["source_type"] == "brush":
            tag_text = " ".join(t for key in TAG_FIELDS for t in chunk[key])
            tokens = (tokenize(chunk["name"]) * 3 + tokenize(chunk["set_title"]) + tokenize(chunk["_pack"])
                      + tokenize(tag_text) * 2 + tokenize(chunk["visual"]) + tokenize(_facet_text(chunk))
                      + tokenize(chunk["_texture_names"]))
        else:
            tokens = tokenize(chunk["_text"])
        tokenized.append(tokens)
    n_docs = len(chunks)
    df = Counter()
    for tokens in tokenized:
        df.update(set(tokens))
    idf = {t: round(math.log(n_docs / (1 + df[t])) + 1.0, 6) for t in sorted(df)}
    for chunk, tokens in zip(chunks, tokenized):
        counts = Counter(tokens)
        vector = {t: round(counts[t] * idf[t], 6) for t in sorted(counts)}
        chunk["vector"] = vector
        chunk["norm"] = round(math.sqrt(sum(w * w for w in vector.values())) or 1.0, 6)
        for private in [k for k in chunk if k.startswith("_")]:
            del chunk[private]

    # filters and similarity tables
    rows = load_schema_rows()
    alias_map = _alias_map(rows)
    param_stats = _build_param_stats(brush_chunks, rows, alias_map)
    facet_keys = sorted({k for c in brush_chunks for k in c["facets"]})
    setting_keys = sorted({k for c in brush_chunks for k, v in c["settings"].items() if scalar(v) is not None})
    tagged = sum(1 for c in brush_chunks if c["tag_state"] == "tagged")
    if brush_chunks and tagged < len(brush_chunks):
        warnings.append(f"NOTE: {len(brush_chunks) - tagged} of {len(brush_chunks)} brushes are untagged.")

    groups = input_groups(vault, catalog)
    index = {
        "schema": INDEX_SCHEMA, "tool": "brush_search", "engine": ENGINE,
        "chunker_version": CHUNKER_VERSION, "tokenizer_version": TOKENIZER_VERSION,
        "inputs_fingerprint": _combined(groups), "inputs_groups": groups,
        "vocabulary_fingerprint": vocabulary_fingerprint(vocab_full),
        "vocabulary": vocab_embed, "expansions": _expansions(vocab_full),
        "note_count": len(iter_notes(vault)), "chunk_count": len(chunks), "brush_chunk_count": len(brush_chunks),
        "unique_brush_count": len(brush_chunks), "tagged_count": tagged, "vocab_size": len(idf),
        "similar": {"method": SIMILAR_METHOD, "defaults": bool(rows), "weights": SIMILAR_WEIGHTS,
                    "aliases": alias_map},
        "param_stats": param_stats,
        "where_keys": {"builtin": list(BUILTIN_KEYS), "facets": facet_keys, "settings": setting_keys},
        "idf": idf, "warnings": warnings, "chunks": chunks,
    }
    if write:
        target = Path(index_path) if index_path else resolve_roots(vault=vault, catalog=catalog)[2]
        write_text_atomic(target, json.dumps(index, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return index


def load_index(path):
    """Read an index file. A missing or unreadable file is a UsageError (exit 2)."""
    path = Path(path)
    if not path.is_file():
        raise UsageError(f"no index at {path.name} -- run `python -I brushes/vault/tools/brush_search.py index` first")
    try:
        index = json.loads(read_text(path))
    except (OSError, ValueError) as err:
        raise UsageError(f"the index is not readable ({err}); run `index` to rebuild it") from None
    if not isinstance(index, dict) or index.get("schema") != INDEX_SCHEMA or "chunks" not in index:
        raise UsageError("the index file is from another version of brush_search; run `index` to rebuild it")
    return index


def check_fresh(index, vault, catalog):
    """{"state": "fresh" | "stale", "reason": str}. Stale when the engine or the
    inputs (notes, sidecars, vocabulary, catalog) differ from what built it."""
    if index.get("engine") != ENGINE or index.get("tokenizer_version") != TOKENIZER_VERSION \
            or index.get("chunker_version") != CHUNKER_VERSION:
        return {"state": "stale", "reason": "the index was built by another version of brush_search"}
    if not index.get("inputs_fingerprint"):
        return {"state": "stale", "reason": "the index has no inputs fingerprint"}
    groups = input_groups(vault, catalog)
    if _combined(groups) == index["inputs_fingerprint"]:
        return {"state": "fresh", "reason": "the inputs are those the index was built from"}
    old = index.get("inputs_groups") or {}
    changed = [name for name in ("notes", "sidecars", "vocabulary", "catalog") if groups[name] != old.get(name)]
    return {"state": "stale", "reason": "changed since the index was built: " + (", ".join(changed) or "inputs")}


# ── filters ──────────────────────────────────────────────────────────────────

_TAG_SPEC_RE = re.compile(r"^[a-z][a-z_]*=[a-z0-9][a-z0-9,-]*$")
_WHERE_SPEC_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=[A-Za-z0-9_.,+:/-]*$")
_TRUE = {"true", "yes", "1"}
_FALSE = {"false", "no", "0"}


def _suggest(word, choices):
    close = difflib.get_close_matches(word, list(choices), n=3, cutoff=0.6)
    return f" Did you mean: {', '.join(close)}?" if close else ""


def _axis_name(axis):
    axis = axis.strip().lower()
    short = axis[:-5] if axis.endswith("_tags") else axis
    if short not in AXES:
        raise UsageError(f"unknown tag axis `{axis}`.{_suggest(short, AXES)} Valid axes: {', '.join(AXES)}")
    return short


def parse_tag_filter(index, spec):
    """`axis=v1,v2` (or an (axis, values) pair) to (axis, [values]). An unknown
    axis or a value outside the index's vocabulary is a UsageError that lists
    the valid ones."""
    if isinstance(spec, (tuple, list)):
        if len(spec) != 2:
            raise UsageError(f"a tag filter is (axis, values), not {spec!r}")
        axis, values = spec
        values = [values] if isinstance(values, str) else list(values)
        text_values = [str(v).strip().lower() for v in values]
    else:
        spec = str(spec).strip()
        if not _TAG_SPEC_RE.match(spec):
            raise UsageError(f"bad --tag `{spec}`: expected AXIS=VALUE[,VALUE] such as medium=watercolor "
                             f"(axes: {', '.join(AXES)})")
        axis, _, rest = spec.partition("=")
        text_values = [v for v in rest.split(",") if v]
    axis = _axis_name(str(axis))
    valid = [e["tag"] for e in (index.get("vocabulary") or {}).get(f"{axis}_tags", [])]
    if not text_values:
        raise UsageError(f"tag filter on {axis} has no value")
    for value in text_values:
        if value not in valid:
            hint = f" Valid {axis} tags: {', '.join(valid)}." if valid else f" The vocabulary defines no {axis} tags."
            raise UsageError(f"unknown {axis} tag `{value}`.{_suggest(value, valid)}{hint}")
    return axis, text_values


def _where_keys(index):
    keys = index.get("where_keys") or {}
    return list(keys.get("builtin", BUILTIN_KEYS)), list(keys.get("facets", [])), list(keys.get("settings", []))


def parse_where_filter(index, spec):
    """`KEY=V1,V2` or `KEY=MIN..MAX` to (key, test(chunk)). A key is `id`, `set`,
    `library`, `pack`, `tagged`, a facet name or a raw setting key; an unknown
    key is a UsageError."""
    if isinstance(spec, (tuple, list)):
        spec = f"{spec[0]}={spec[1]}"
    spec = str(spec).strip()
    if not _WHERE_SPEC_RE.match(spec):
        raise UsageError(f"bad filter `{spec}`: expected KEY=V1,V2 or KEY=MIN..MAX (no comparison operators; "
                         "use KEY=MIN.. or KEY=..MAX)")
    key, _, rest = spec.partition("=")
    builtin, facets, settings = _where_keys(index)
    if index.get("brush_chunk_count", len(index.get("chunks", []))) and key not in builtin + facets + settings:
        known = builtin + facets + settings
        raise UsageError(f"unknown filter key `{key}`.{_suggest(key, known)} Valid keys: the facet names, any raw "
                         f"setting key, or {', '.join(builtin)}")
    if ".." in rest:
        low_text, _, high_text = rest.partition("..")
        try:
            low = float(low_text) if low_text else -math.inf
            high = float(high_text) if high_text else math.inf
        except ValueError:
            raise UsageError(f"bad range `{rest}` in `{spec}`: expected MIN..MAX with numbers") from None

        def test(chunk, key=key, low=low, high=high):
            value = _chunk_value(chunk, key)
            return _number(value) and low <= value <= high
        return key, test
    wanted = [v for v in rest.split(",") if v != ""]
    if not wanted:
        raise UsageError(f"filter `{spec}` has no value")

    def test(chunk, key=key, wanted=wanted):
        value = _chunk_value(chunk, key)
        if value is None:
            return False
        for item in wanted:
            lowered = item.lower()
            if isinstance(value, bool):
                if (lowered in _TRUE and value) or (lowered in _FALSE and not value):
                    return True
            elif _number(value):
                try:
                    if abs(value - float(item)) <= 1e-9:
                        return True
                except ValueError:
                    pass
            elif isinstance(value, str) and value.lower() == lowered:
                return True
        return False
    return key, test


def _chunk_value(chunk, key):
    if key == "id":
        return chunk.get("brush_id")
    if key == "set":
        return chunk.get("set")
    if key == "library":
        return chunk.get("library")
    if key == "pack":
        return chunk.get("pack")
    if key == "tagged":
        return chunk.get("tag_state") == "tagged"
    facets = chunk.get("facets") or {}
    if key in facets:
        return facets[key]
    settings = chunk.get("settings") or {}
    if key in settings:
        return scalar(settings[key])
    return None


def _set_test(key, test):
    """`set=...` also matches the sets a brush is shared into."""
    if key != "set":
        return test

    def widened(chunk):
        if test(chunk):
            return True
        return any(test({"set": a["set"]}) for a in chunk.get("also_in") or [])
    return widened


def _listed(value):
    """A filter argument as a list: one string is one filter."""
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def _compile(index, tags, where, where_not):
    tags, where, where_not = _listed(tags), _listed(where), _listed(where_not)
    tag_filters = [parse_tag_filter(index, t) for t in tags or ()]
    where_filters = [parse_where_filter(index, w) for w in where or ()]
    not_filters = [parse_where_filter(index, w) for w in where_not or ()]
    return tag_filters, where_filters, not_filters


def _passes(chunk, tag_filters, where_filters, not_filters):
    for axis, values in tag_filters:
        have = chunk.get(f"{axis}_tags") or []
        if not any(v in have for v in values):
            return False
    for key, test in where_filters:
        if not _set_test(key, test)(chunk):
            return False
    for key, test in not_filters:
        if _set_test(key, test)(chunk):
            return False
    return True


def _normalised(tag_filters, where, where_not):
    where, where_not = _listed(where), _listed(where_not)
    return ([[axis, values] for axis, values in tag_filters],
            [str(w).strip() if not isinstance(w, (tuple, list)) else f"{w[0]}={w[1]}" for w in where or ()],
            [str(w).strip() if not isinstance(w, (tuple, list)) else f"{w[0]}={w[1]}" for w in where_not or ()])


# ── results ──────────────────────────────────────────────────────────────────

def make_row(chunk, score, settings=False):
    """The ROW of F9 for one chunk."""
    is_brush = chunk.get("source_type") == "brush"
    visual = chunk.get("visual") or ""
    row = {
        "brush_id": chunk.get("brush_id"), "name": chunk.get("name"), "set": chunk.get("set"),
        "set_title": chunk.get("set_title"), "library": chunk.get("library"), "pack": chunk.get("pack"),
        "source_type": chunk.get("source_type"), "note": chunk.get("note"), "heading": chunk.get("heading"),
        "start_line": chunk.get("start_line"), "end_line": chunk.get("end_line"), "score": round(score, 4),
    }
    for key in TAG_FIELDS:
        row[key] = list(chunk.get(key) or [])
    row.update({
        "visual": visual, "visual_basis": VISUAL_BASIS if visual else None,
        "tag_state": chunk.get("tag_state") if is_brush else None,
        "facets": dict(chunk.get("facets") or {}), "preview": dict(chunk.get("preview") or {}),
        "approximate": bool(chunk.get("approximate")),
        "also_in": [dict(a) for a in chunk.get("also_in") or []],
        "record": f"brushes/{chunk['brush_id']}.json" if is_brush else None,
    })
    if not is_brush:
        row["snippet"] = chunk.get("snippet", "")
    if settings and is_brush:
        row["settings"] = chunk.get("settings") or {}
    return row


def _check_window(top, offset):
    if not isinstance(top, int) or isinstance(top, bool) or top < 0:
        raise UsageError("top must be a whole number of 0 or more")
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise UsageError("offset must be a whole number of 0 or more")


def _sort_name(chunk):
    return (chunk.get("name") or "").casefold(), chunk.get("brush_id") or "", chunk.get("note") or "", \
        chunk.get("start_line") or 0


def _query_vector(index, query):
    tokens = tokenize(query)
    if not tokens:
        return None, 1.0
    idf = index["idf"]
    weights = Counter(tokens)
    have = set(tokens)
    padded = " " + " ".join(tokens) + " "
    added = Counter()
    for group in index.get("expansions") or []:
        if any((" " + " ".join(p) + " ") in padded for p in group["phrases"]):
            new_terms = [t for t in group["terms"] if t not in have]
            for term in new_terms:
                added[term] += min(EXPAND_WEIGHT, max(EXPAND_FLOOR, EXPAND_MASS / len(new_terms)))
    for term, extra in added.items():
        weights[term] += min(extra, 1.0)
    vector = {t: w * idf[t] for t, w in weights.items() if t in idf}
    norm = math.sqrt(sum(w * w for w in vector.values())) or 1.0
    return vector, norm


def search_index(index, query="", *, tags=(), where=(), where_not=(), source_types=None, top=5, offset=0,
                 settings=False):
    """The envelope of F9. Ranking is `cosine` with a query (filters first),
    `tag-purity` with tag filters only, and `filter-order` otherwise (the
    chunks in set order). Equal scores break by name, then id."""
    _check_window(top, offset)
    query = query or ""
    tag_filters, where_filters, not_filters = _compile(index, tags, where, where_not)
    if source_types:
        source_types = [source_types] if isinstance(source_types, str) else list(source_types)
        bad = [s for s in source_types if s not in SOURCE_TYPES]
        if bad:
            raise UsageError(f"unknown source type `{bad[0]}`; valid: {', '.join(SOURCE_TYPES)}")
    elif tag_filters or where_filters or not_filters:
        source_types = ["brush"]
    qvec, qnorm = _query_vector(index, query)
    scored = []
    for order, chunk in enumerate(index["chunks"]):
        if source_types and chunk["source_type"] not in source_types:
            continue
        if not _passes(chunk, tag_filters, where_filters, not_filters):
            continue
        if qvec is not None:
            vector = chunk["vector"]
            dot = sum(w * vector.get(t, 0.0) for t, w in qvec.items())
            if dot <= 0:
                continue
            score = dot / (qnorm * chunk["norm"])
            if score <= 0:
                continue
        elif query.strip():
            continue                                  # the query had no usable word
        elif tag_filters:
            score = sum(1.0 / max(1, len(chunk.get(f"{axis}_tags") or [])) for axis, _ in tag_filters) \
                    / len(tag_filters)
        else:
            score = 1.0
        scored.append((score, order, chunk))
    if qvec is not None:
        ranking = "cosine"
        scored.sort(key=lambda t: (-round(t[0], 9), _sort_name(t[2])))
    elif tag_filters:
        ranking = "tag-purity"
        scored.sort(key=lambda t: (-round(t[0], 9), _sort_name(t[2])))
    else:
        ranking = "filter-order"
        scored.sort(key=lambda t: t[1])
    unique, seen = [], set()
    for score, order, chunk in scored:
        brush_id = chunk.get("brush_id")
        if brush_id is not None:
            if brush_id in seen:
                continue
            seen.add(brush_id)
        unique.append((score, chunk))
    shown_tags, shown_where, shown_not = _normalised(tag_filters, where, where_not)
    return {"query": query, "tags": shown_tags, "where": shown_where, "where_not": shown_not,
            "ranking": ranking, "total": len(unique), "offset": offset,
            "results": [make_row(c, s, settings) for s, c in unique[offset:offset + top]]}


# ── brush lookup ─────────────────────────────────────────────────────────────

def resolve_brush(index, ref):
    """The brush chunk for a brush id, an id prefix of 6 or more hex characters
    (with or without `b_`), or an exact name (case-insensitive when no exact
    match). An ambiguous reference is a UsageError that lists the ids; an
    unknown one is NotFound."""
    ref = str(ref).strip()
    brushes = [c for c in index["chunks"] if c["source_type"] == "brush"]
    for chunk in brushes:
        if chunk["brush_id"] == ref:
            return chunk
    matches = [c for c in brushes if (c["name"] or "") == ref] \
        or [c for c in brushes if (c["name"] or "").strip().casefold() == ref.casefold() and ref]
    if not matches and re.match(r"^(b_)?[0-9a-f]{6,12}$", ref.lower()):
        prefix = ref.lower() if ref.lower().startswith("b_") else "b_" + ref.lower()
        matches = [c for c in brushes if c["brush_id"].startswith(prefix)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        listed = "; ".join(f"{c['brush_id']} ({c['name']!r} in {c['set']})" for c in matches[:12])
        raise UsageError(f"`{ref}` matches {len(matches)} brushes: {listed}. Use a brush id.")
    raise NotFound(f"no brush matches `{ref}` (give a brush id, an id prefix of 6 or more hex characters, or an "
                   "exact name)")


# ── similar ──────────────────────────────────────────────────────────────────

def _features(settings, index):
    """{key: value} of the settings that take part in `similar`, aliases folded
    and schema defaults filled in."""
    aliases = (index.get("similar") or {}).get("aliases") or {}
    stats = index.get("param_stats") or {}
    folded = {}
    for key, form in (settings or {}).items():
        key = aliases.get(key, key)
        if key in stats:
            value = scalar(form)
            if isinstance(value, bool) or _number(value):
                folded.setdefault(key, value)
    for key, stat in stats.items():
        if key not in folded and stat.get("default") is not None:
            folded[key] = stat["default"]
    return folded


def _weight(key):
    return SIMILAR_WEIGHTS.get(key, SIMILAR_WEIGHTS["default"])


def _compare(query_f, other_f, query_refs, other_refs, stats):
    """(score, compared_keys, coverage, differs) for two feature sets."""
    shared_weight = query_weight = other_weight = 0.0
    total = 0.0
    compared = 0
    deltas = []
    for key, stat in stats.items():
        w = _weight(key)
        a, b = query_f.get(key), other_f.get(key)
        query_weight += w if a is not None else 0
        other_weight += w if b is not None else 0
        if a is None or b is None:
            continue
        if stat["kind"] == "num":
            span = stat["hi"] - stat["lo"]
            sa = min(1.0, max(0.0, (a - stat["lo"]) / span))
            sb = min(1.0, max(0.0, (b - stat["lo"]) / span))
            similarity = 1.0 - abs(sa - sb)
        else:
            similarity = 1.0 if a == b else 0.0
        shared_weight += w
        total += w * similarity
        compared += 1
        if similarity < 1.0:
            deltas.append((w * (1.0 - similarity), key, a, b, 1.0 - similarity))
    for ref in ("shape_ref", "grain_ref"):
        a, b = query_refs.get(ref), other_refs.get(ref)
        w = _weight(ref)
        if a is None:                       # a settings query holds no texture references
            continue
        query_weight += w
        other_weight += w if b is not None else 0
        if b is None:
            continue
        similarity = 1.0 if a == b else 0.0
        shared_weight += w
        total += w * similarity
        compared += 1
        if similarity < 1.0:
            deltas.append((w, ref, a, b, 1.0))
    if shared_weight <= 0:
        return 0.0, 0, 0.0, []
    denominator = max(query_weight, other_weight) or shared_weight
    coverage = shared_weight / denominator
    score = (total / shared_weight) * math.sqrt(coverage)
    deltas.sort(key=lambda t: (-round(t[0], 9), t[1]))

    def shown(v):
        return round(v, 4) if isinstance(v, float) else v
    differs = [{"key": key, "query": shown(a), "other": shown(b), "delta": round(delta, 4)}
               for _, key, a, b, delta in deltas[:3]]
    return score, compared, coverage, differs


def similar(index, brush_id=None, *, settings=None, tags=(), where=(), where_not=(), top=10, other_sets=False):
    """Brushes with settings like those of a library brush (`brush_id`: an id,
    an id prefix or an exact name) or like a settings object that is not a
    library brush. Method `gower-v1`: numbers scaled by the 1st and 99th
    percentile, booleans and enums equal or not, shape_ref weight 4, grain_ref
    weight 3, the rest 1, missing keys filled from schema defaults. Equal scores
    break by name, then id. It compares settings, not how a stroke looks."""
    _check_window(top, 0)
    if (brush_id is None) == (settings is None):
        raise UsageError("similar takes either a brush id or a settings object")
    tag_filters, where_filters, not_filters = _compile(index, tags, where, where_not)
    stats = index.get("param_stats") or {}
    query_chunk = None
    if brush_id is not None:
        query_chunk = resolve_brush(index, brush_id)
        query_f = _features(query_chunk["settings"], index)
        query_refs = {"shape_ref": query_chunk["shape_ref"], "grain_ref": query_chunk["grain_ref"]}
        query_info = {"brush_id": query_chunk["brush_id"], "name": query_chunk["name"], "set": query_chunk["set"],
                      "note": query_chunk["note"], "heading": query_chunk["heading"],
                      "start_line": query_chunk["start_line"], "end_line": query_chunk["end_line"]}
    else:
        if not isinstance(settings, dict):
            raise UsageError("settings must be an object of setting keys and values")
        query_f = _features(settings, index)
        query_refs = {}
        query_info = {"brush_id": None, "settings_keys": len(settings)}
    scored = []
    for chunk in index["chunks"]:
        if chunk["source_type"] != "brush" or chunk is query_chunk:
            continue
        if query_chunk is not None and chunk["brush_id"] == query_chunk["brush_id"]:
            continue
        if other_sets and query_chunk is not None and chunk["set"] == query_chunk["set"]:
            continue
        if not _passes(chunk, tag_filters, where_filters, not_filters):
            continue
        score, compared, coverage, differs = _compare(
            query_f, _features(chunk["settings"], index), query_refs,
            {"shape_ref": chunk["shape_ref"], "grain_ref": chunk["grain_ref"]}, stats)
        if compared == 0:
            continue
        scored.append((score, compared, coverage, differs, chunk))
    scored.sort(key=lambda t: (-round(t[0], 9), (t[4]["name"] or "").casefold(), t[4]["brush_id"]))
    shown_tags, shown_where, shown_not = _normalised(tag_filters, where, where_not)
    results = []
    for score, compared, coverage, differs, chunk in scored[:top]:
        row = make_row(chunk, score)
        row.update({"compared_keys": compared, "coverage": round(coverage, 4), "differs": differs})
        results.append(row)
    return {"query": query_info, "tags": shown_tags, "where": shown_where, "where_not": shown_not,
            "ranking": "similarity", "method": SIMILAR_METHOD, "defaults_filled": bool(
                (index.get("similar") or {}).get("defaults")),
            "total": len(scored), "offset": 0, "results": results}


# ── facet counts ─────────────────────────────────────────────────────────────

def _median(values):
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2


def _summarise(name_to_values, categorical_max=NUMERIC_ENUM_MAX):
    out = {}
    for name in sorted(name_to_values):
        values = name_to_values[name]
        present = [v for v in values if v is not None]
        if present and all(isinstance(v, bool) for v in present):
            kind = "bool"
        elif present and all(_number(v) for v in present) and len(set(present)) > categorical_max:
            kind = "number"
        elif present and all(isinstance(v, (str, bool, int, float)) for v in present):
            kind = "enum"
        else:
            continue
        if kind == "number":
            out[name] = {"kind": "number", "n": len(present), "null": len(values) - len(present),
                         "min": min(present), "median": round(_median(present), 4), "max": max(present)}
        else:
            counts = Counter("null" if v is None else (str(v).lower() if isinstance(v, bool) else str(v))
                             for v in values)
            out[name] = {"kind": kind, "values": {k: counts[k] for k in sorted(counts)}}
    return out


def facet_counts(index, *, tags=(), where=(), where_not=(), settings=False):
    """Counts over the brushes that pass the filters: the facets (values and
    counts, or min/median/max for a number), the tag axes with every
    vocabulary tag and its count, the tag states, and the valid `--where`
    keys. With settings=True the raw numeric setting keys are summarised too."""
    tag_filters, where_filters, not_filters = _compile(index, tags, where, where_not)
    brushes = [c for c in index["chunks"] if c["source_type"] == "brush"
               and _passes(c, tag_filters, where_filters, not_filters)]
    facet_values = {}
    for chunk in brushes:
        for key in (index.get("where_keys") or {}).get("facets", []):
            facet_values.setdefault(key, []).append(chunk["facets"].get(key))
    result = {"brushes": len(brushes), "facets": _summarise(facet_values),
              "tag_state": {state: sum(1 for c in brushes if c["tag_state"] == state) for state in STATES}}
    tag_out = {}
    for axis, key in zip(AXES, TAG_FIELDS):
        counts = Counter(t for c in brushes for t in c.get(key) or [])
        entries = (index.get("vocabulary") or {}).get(key, [])
        tag_out[axis] = {"tagged": sum(1 for c in brushes if c.get(key)),
                         "values": {e["tag"]: counts.get(e["tag"], 0) for e in entries},
                         "definitions": {e["tag"]: e["definition"] for e in entries}}
    result["tags"] = tag_out
    builtin, facets, setting_keys = _where_keys(index)
    result["where_keys"] = {"builtin": builtin, "facets": facets, "settings": setting_keys}
    if settings:
        columns = {}
        for chunk in brushes:
            for key in setting_keys:
                columns.setdefault(key, [])
                value = scalar(chunk["settings"].get(key)) if key in chunk["settings"] else None
                if _number(value):
                    columns[key].append(value)
        result["numeric"] = {k: {"n": len(v), "min": min(v), "median": round(_median(v), 4), "max": max(v)}
                             for k, v in sorted(columns.items()) if v}
    return result


# ── chunks of one note (for the tagger) ──────────────────────────────────────

def _note_path(vault, note):
    note = str(note).replace("\\", "/").strip()
    if not note or note.startswith("/") or ".." in note.split("/") or re.match(r"^[A-Za-z]:", note):
        raise UsageError(f"`{note}` is not a vault-relative note path such as 02_Vendor_Packs/demo-set.md")
    path = (Path(vault) / note)
    return note, path


def _line_range(value):
    if value is None:
        return None
    if isinstance(value, str):
        found = re.match(r"^(\d+)-(\d+)$", value.strip())
        if not found:
            raise UsageError(f"bad line range `{value}`: expected A-B")
        return int(found.group(1)), int(found.group(2))
    low, high = value
    return int(low), int(high)


def chunks_for(vault, catalog, note, *, ids=None, line_range=None, untagged=False, brief=False):
    """The chunks of one note exactly as the index would make them, for the
    tagger: each brush section with its id, heading, line range, content hash,
    facets and preview paths. `ids` (a list or comma string), `line_range`
    ("A-B" or (a, b)) and `untagged` narrow the brushes listed; `brief` leaves
    the text out. Needs no index."""
    vault, catalog = _paths(vault, catalog)
    note, path = _note_path(vault, note)
    if not path.is_file():
        raise NotFound(f"no note {note} in the vault")
    parsed = parse_note(read_text(path))
    cat = load_catalog_json(catalog)
    sets = {row["set_slug"]: row for row in cat.get("sets", []) if isinstance(row, dict) and "set_slug" in row}
    set_row = next((row for slug, row in sorted(sets.items()) if row.get("note") == note), {})
    fm = parsed["frontmatter"]
    if isinstance(ids, str):
        ids = [i.strip() for i in ids.split(",") if i.strip()]
    ids = set(ids) if ids else None
    window = _line_range(line_range)
    sidecars = read_sidecars(vault)
    records = {}
    for section in parsed["sections"]:
        if section["brush_id"] and (Path(catalog) / "brushes" / f"{section['brush_id']}.json").is_file():
            records[section["brush_id"]] = load_record(catalog, section["brush_id"])
    chosen, _, _ = resolve_entries(sidecars, {i: r.get("content_sha256") for i, r in records.items()})
    out = []
    for section in parsed["sections"]:
        brush_id = section["brush_id"]
        if (ids or untagged or window) and not brush_id:
            continue
        if ids and brush_id not in ids:
            continue
        if window and (section["end_line"] < window[0] or section["start_line"] > window[1]):
            continue
        item = {"chunk_index": section["chunk_index"], "heading": section["heading"],
                "start_line": section["start_line"], "end_line": section["end_line"],
                "source_type": "brush" if brush_id else "set", "brush_id": brush_id}
        if brush_id:
            record = records.get(brush_id)
            if record is None:
                item.update({"name": None, "content_sha256": None, "content_fp": None, "tag_state": None,
                             "facets": {}, "facet_words": [], "preview": {}, "approximate": False,
                             "error": "no catalog record for this id"})
            else:
                sha = record.get("content_sha256") or ""
                pick = chosen.get(brush_id)
                state = pick["state"] if pick else "untagged"
                preview = record.get("preview") or {}
                item.update({"name": record.get("name"), "content_sha256": sha, "content_fp": sha[:16],
                             "tag_state": state, "facets": record.get("facets") or {},
                             "facet_words": record.get("facet_words") or [], "preview": preview,
                             "approximate": preview.get("stroke_source") == "rendered-approx"})
            if untagged and item.get("tag_state") == "tagged":
                continue
        else:
            item["name"] = section["heading"]
        if not brief:
            item["text"] = section["text"]
        out.append(item)
    body = "\n".join(s["text"] for s in parsed["sections"])
    return {"file": note, "set": set_row.get("set_slug") or fm.get("set_slug"),
            "set_title": set_row.get("title") or fm.get("title"), "library": set_row.get("library") or fm.get("library"),
            "pack": set_row.get("pack") or fm.get("pack"), "chunker_version": CHUNKER_VERSION,
            "body_fingerprint": "sha256:16:" + _sha256_text(" ".join(body.split()))[:16],
            "brush_count": sum(1 for s in parsed["sections"] if s["brush_id"]), "chunks": out}


# ── verify ───────────────────────────────────────────────────────────────────

_DIGEST_HEAD_RE = re.compile(r"^### (b_[0-9a-f]{12})\b(.*)$")
_CITE_RE = re.compile(r"\(([^()]*?),\s*lines (\d+)-(\d+)\)")
_VALUE_LINE_RE = re.compile(r"^\s*[-*]\s*`([^`]+)`\s*=\s*`?([^`]*?)`?\s*$")
_NAME_LINE_RE = re.compile(r'^\s*[-*]\s*name:\s*"(.*)"\s*$')


def _value_matches(setting, text):
    if isinstance(setting, dict):
        setting_value = scalar(setting)
    else:
        setting_value = setting
    if isinstance(setting_value, bool):
        return text.strip().lower() == ("true" if setting_value else "false")
    if _number(setting_value):
        try:
            return abs(float(text) - float(setting_value)) <= 1e-9 * max(1.0, abs(float(setting_value)))
        except ValueError:
            return False
    if setting is None:
        return text.strip().lower() in ("nil", "null", "none")
    return isinstance(setting_value, str) and setting_value == text


def verify_digest(vault, catalog, digest, *, strict=False):
    """Check a librarian digest. For each `### b_<id>` block the cited note lines
    must hold the id, and every line under `Exact values:` must be a setting
    key and value of the brush's catalog record, or its exact name. A line that
    is not found gets UNVERIFIED_MARKER appended. Returns (text, marked)."""
    vault, catalog = _paths(vault, catalog)
    out, marked = [], 0
    current, record, in_exact, cite_ok = None, None, False, True
    for line in digest.replace("\r\n", "\n").split("\n"):
        head = _DIGEST_HEAD_RE.match(line)
        if head:
            current, in_exact = head.group(1), False
            try:
                record = load_record(catalog, current)
            except (NotFound, UsageError):
                record = None
            cite = _CITE_RE.search(line)
            cite_ok = False
            if cite:
                try:
                    note, path = _note_path(vault, cite.group(1).strip())
                    lines = read_text(path).split("\n")
                    first, last = int(cite.group(2)), int(cite.group(3))
                    window = lines[max(0, first - 1):last]
                    cite_ok = any(f"`{current}`" in ln for ln in window)
                except (OSError, UsageError, NotFound):
                    cite_ok = False
            if not cite_ok or record is None:
                line = line.rstrip() + "  " + UNVERIFIED_MARKER
                marked += 1
            out.append(line)
            continue
        if line.strip().lower().startswith("exact values"):
            in_exact = True
            out.append(line)
            continue
        if in_exact and current is not None and line.strip().startswith(("-", "*")) and "(none)" not in line:
            ok = False
            if record is not None:
                found = _VALUE_LINE_RE.match(line)
                named = _NAME_LINE_RE.match(line)
                if found:
                    key, text = found.group(1), found.group(2)
                    settings = record.get("settings") or {}
                    ok = key in settings and _value_matches(settings[key], text)
                elif named:
                    ok = named.group(1) == (record.get("name") or "")
            if not ok and UNVERIFIED_MARKER not in line:
                line = line.rstrip() + "  " + UNVERIFIED_MARKER
                marked += 1
        elif in_exact and line.strip() and not line.strip().startswith(("-", "*")):
            in_exact = False
        out.append(line)
    return "\n".join(out), marked


# ── output ───────────────────────────────────────────────────────────────────

def _facet_line(row):
    words = row.get("facet_words")
    return " ".join(words) if words else ""


def _print_rows(envelope, out):
    for row in envelope["results"]:
        who = f"{row['brush_id']}  " if row.get("brush_id") else ""
        where = f" -- {row['set_title']}" if row.get("set_title") else ""
        out.write(f"[{row['score']:.3f}] {who}{row['name']}{where}  [{row['source_type']}]\n")
        if row.get("note"):
            lines = f"  lines {row['start_line']}-{row['end_line']}" if row.get("start_line") else ""
            heading = f"  ({row['heading']})" if row.get("heading") else ""
            out.write(f"    {row['note']}{lines}{heading}\n")
        elif row.get("source_type") == "brush":
            out.write("    (no note on disk yet)\n")
        if row.get("source_type") == "brush":
            facets = row["facets"]
            summary = " ".join(f"{k}={facets[k]}" for k in ("kind", "spacing_class", "taper", "size_class", "era")
                               if facets.get(k) is not None)
            out.write(f"    library: {row['library']}  pack: {row['pack']}  {summary}\n")
            bits = [f"{key[:-5]}={','.join(row[key])}" for key in TAG_FIELDS if row.get(key)]
            out.write(f"    tags: {'  '.join(bits)}\n" if bits else f"    tags: ({row['tag_state']})\n")
            if row.get("visual"):
                out.write(f"    visual (described, not measured): {row['visual']}\n")
            if row.get("approximate"):
                out.write("    preview: approximate (rendered stand-in)\n")
        elif row.get("snippet"):
            out.write(f"    {row['snippet']}\n")
        if "compared_keys" in row:
            out.write(f"    compared {row['compared_keys']} keys, coverage {row['coverage']:.2f}\n")
            for diff in row["differs"]:
                out.write(f"    differs: {diff['key']}  {diff['query']} -> {diff['other']}  (delta {diff['delta']})\n")


def _print_envelope(envelope, out):
    if not envelope["results"]:
        out.write("No results found.\n")
        return
    _print_rows(envelope, out)
    shown = len(envelope["results"])
    out.write(f"{shown} of {envelope['total']} matches shown.  ranking: {envelope['ranking']}"
              + (f"  method: {envelope['method']}" if "method" in envelope else "") + "\n")


def _emit_json(value, out):
    out.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


# ── command line ─────────────────────────────────────────────────────────────

def _add_common(parser):
    parser.add_argument("--vault", default=None, help="vault folder (default: ROSW_BRUSHES_VAULT, ROSW_BRUSHES_ROOT/vault, "
                                                      "or this tool's own vault)")
    parser.add_argument("--catalog", default=None, help="catalog folder (default: ROSW_BRUSHES_CATALOG, "
                                                        "ROSW_BRUSHES_ROOT/catalog, or the catalog/ beside the vault)")
    parser.add_argument("--index", default=None, help="index file (default: ROSW_BRUSHES_INDEX or "
                                                      "<vault>/tools/rag_index/index.json)")


def _add_filters(parser):
    parser.add_argument("--tag", action="append", default=[], metavar="AXIS=V[,V2]",
                        help="keep brushes with one of these tags on an axis; repeatable, ANDed")
    parser.add_argument("--where", action="append", default=[], metavar="KEY=V[,V2]|KEY=MIN..MAX",
                        help="keep brushes whose facet or setting matches; repeatable, ANDed")
    parser.add_argument("--where-not", action="append", default=[], dest="where_not", metavar="KEY=V",
                        help="drop brushes whose facet or setting matches; repeatable")


def build_parser():
    parser = argparse.ArgumentParser(prog="brush_search.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    verbs = parser.add_subparsers(dest="verb", required=True)

    p = verbs.add_parser("index", help="build the search index (generated, rebuildable, nothing to confirm)")
    _add_common(p)
    p.add_argument("--check", action="store_true", help="only check the index: exit 0 fresh, 1 stale")
    p.add_argument("--json", action="store_true")

    for name, help_text in (("search", "rank brushes for a query and filters"), ("ask", "the same as search")):
        p = verbs.add_parser(name, help=help_text)
        _add_common(p)
        p.add_argument("query", nargs="?", default="", help="words; optional when a filter is given")
        p.add_argument("--top", type=int, default=5)
        p.add_argument("--offset", type=int, default=0)
        p.add_argument("--json", action="store_true")
        p.add_argument("--source", default=None, metavar="TYPE[,TYPE]",
                       help=f"chunk types to search ({', '.join(SOURCE_TYPES)}); default: all, or brush with a filter")
        p.add_argument("--settings", action="store_true", help="include each brush's settings in the result")
        _add_filters(p)

    p = verbs.add_parser("similar", help="brushes with settings like a brush's")
    _add_common(p)
    p.add_argument("brush", help="brush id, an id prefix of 6 or more hex characters, or an exact name")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--json", action="store_true")
    p.add_argument("--other-sets", action="store_true", dest="other_sets", help="leave out the brush's own set")
    _add_filters(p)

    p = verbs.add_parser("facets", help="facet, tag and vocabulary counts")
    _add_common(p)
    p.add_argument("--axis", default=None, help="show one tag axis")
    p.add_argument("--settings", action="store_true", help="include numeric ranges of the raw setting keys")
    p.add_argument("--json", action="store_true")
    _add_filters(p)

    p = verbs.add_parser("files", help="list the note files")
    _add_common(p)
    p.add_argument("--type", default=None, choices=[t for t in SOURCE_TYPES if t != "brush"])
    p.add_argument("--json", action="store_true")

    p = verbs.add_parser("chunks", help="the chunks of one note, as the index and the tagger see them")
    _add_common(p)
    p.add_argument("note", help="vault-relative note path, such as 02_Vendor_Packs/demo-set.md")
    p.add_argument("--ids", default=None, help="comma-separated brush ids")
    p.add_argument("--range", default=None, dest="line_range", metavar="A-B", help="chunks that overlap these lines")
    p.add_argument("--untagged", action="store_true", help="only brushes without a current tag entry")
    p.add_argument("--brief", action="store_true", help="leave out the chunk text")
    p.add_argument("--json", action="store_true")

    p = verbs.add_parser("verify", help="mark the values of a librarian digest that the record does not hold")
    _add_common(p)
    p.add_argument("--from", default=None, dest="source", metavar="FILE", help="digest file (default: standard input)")
    p.add_argument("--strict", action="store_true", help="exit 1 when anything was marked")

    p = verbs.add_parser("brush", help="everything the index holds about one brush")
    _add_common(p)
    p.add_argument("brush", help="brush id, id prefix or exact name")
    p.add_argument("--settings", action="store_true")
    p.add_argument("--json", action="store_true")
    return parser


def _load(args):
    vault, catalog, index_path = resolve_roots(args.vault, args.catalog, args.index)
    return vault, catalog, index_path


def _cmd_index(args, out, err):
    vault, catalog, index_path = _load(args)
    if not vault.is_dir():
        raise UsageError(f"the vault folder does not exist: {vault.name} (use --vault or ROSW_BRUSHES_VAULT)")
    if args.check:
        if not index_path.is_file():
            out.write("stale: no index file; run `index`\n")
            return 1
        index = load_index(index_path)
        result = check_fresh(index, vault, catalog)
        if args.json:
            _emit_json(result, out)
        else:
            out.write(f"{result['state']}: {result['reason']}\n")
        return 0 if result["state"] == "fresh" else 1
    index = build_index(vault, catalog, write=True, index_path=index_path)
    summary = {"notes": index["note_count"], "chunks": index["chunk_count"], "brushes": index["brush_chunk_count"],
               "tagged": index["tagged_count"], "vocab_terms": index["vocab_size"], "warnings": index["warnings"]}
    if args.json:
        _emit_json(summary, out)
        return 0
    out.write(f"Indexed {summary['notes']} notes -> {summary['chunks']} chunks ({summary['brushes']} brushes, "
              f"{summary['tagged']} tagged), {summary['vocab_terms']} vocab terms.\n")
    for warning in index["warnings"]:
        out.write(warning + "\n")
    out.write(f"Wrote {index_path.name} ({index_path.stat().st_size:,} bytes) under {index_path.parent.name}/\n")
    return 0


def _cmd_search(args, out, err):
    vault, catalog, index_path = _load(args)
    index = load_index(index_path)
    if not (args.query or "").strip() and not (args.tag or args.where or args.where_not):
        raise UsageError("give a query or at least one --tag / --where filter")
    sources = [s.strip() for s in args.source.split(",") if s.strip()] if args.source else None
    envelope = search_index(index, args.query, tags=args.tag, where=args.where, where_not=args.where_not,
                            source_types=sources, top=args.top, offset=args.offset, settings=args.settings)
    if args.json:
        _emit_json(envelope, out)
    else:
        _print_envelope(envelope, out)
    return 0


def _cmd_similar(args, out, err):
    vault, catalog, index_path = _load(args)
    index = load_index(index_path)
    envelope = similar(index, args.brush, tags=args.tag, where=args.where, where_not=args.where_not,
                       top=args.top, other_sets=args.other_sets)
    if args.json:
        _emit_json(envelope, out)
        return 0
    query = envelope["query"]
    out.write(f"Brushes like {query['brush_id']} {query['name']!r} ({query['set']}), method {envelope['method']}; "
              "settings are compared, not how a stroke looks.\n")
    _print_envelope(envelope, out)
    return 0


def _cmd_facets(args, out, err):
    vault, catalog, index_path = _load(args)
    index = load_index(index_path)
    result = facet_counts(index, tags=args.tag, where=args.where, where_not=args.where_not, settings=args.settings)
    axis = _axis_name(args.axis) if args.axis else None
    if axis:
        result = {"brushes": result["brushes"], "tags": {axis: result["tags"][axis]}}
    if args.json:
        _emit_json(result, out)
        return 0
    out.write(f"{result['brushes']} brushes\n")
    if "tag_state" in result:
        out.write("tag state: " + "  ".join(f"{k}={v}" for k, v in result["tag_state"].items()) + "\n")
    if "facets" in result:
        out.write("\nfacets\n")
        for name, info in result["facets"].items():
            if info["kind"] == "number":
                out.write(f"  {name}: {info['min']} .. {info['median']} .. {info['max']}  (n={info['n']})\n")
            else:
                out.write(f"  {name}: " + "  ".join(f"{v}={n}" for v, n in info["values"].items()) + "\n")
    out.write("\ntags (closed vocabulary)\n")
    for name, info in result["tags"].items():
        out.write(f"  {name}: {info['tagged']} brushes tagged\n")
        for tag, count in info["values"].items():
            out.write(f"    {tag} ({count})  {info['definitions'][tag]}\n")
    if "where_keys" in result:
        keys = result["where_keys"]
        out.write("\n--where keys: " + ", ".join(keys["builtin"]) + "; facets: " + ", ".join(keys["facets"])
                  + f"; plus any of the {len(keys['settings'])} raw setting keys\n")
    if "numeric" in result:
        out.write("\nsettings\n")
        for key, info in result["numeric"].items():
            out.write(f"  {key}: {info['min']} .. {info['median']} .. {info['max']}  (n={info['n']})\n")
    return 0


def _cmd_files(args, out, err):
    vault, catalog, index_path = _load(args)
    if not vault.is_dir():
        raise UsageError(f"the vault folder does not exist: {vault.name}")
    rows = []
    for rel, kind in iter_notes(vault):
        if args.type and kind != args.type:
            continue
        rows.append({"file": rel, "source_type": kind})
    if args.json:
        _emit_json(rows, out)
    else:
        for row in rows:
            out.write(f"{row['file']}  [{row['source_type']}]\n")
    return 0


def _cmd_chunks(args, out, err):
    vault, catalog, index_path = _load(args)
    result = chunks_for(vault, catalog, args.note, ids=args.ids, line_range=args.line_range,
                        untagged=args.untagged, brief=args.brief)
    if args.json:
        _emit_json(result, out)
        return 0
    out.write(f"{result['file']}  {result['brush_count']} brushes  body_fingerprint={result['body_fingerprint']}\n")
    for chunk in result["chunks"]:
        label = chunk.get("brush_id") or "(section)"
        state = f"  [{chunk['tag_state']}]" if chunk.get("tag_state") else ""
        fp = f"  fp={chunk['content_fp']}" if chunk.get("content_fp") else ""
        out.write(f"  chunk {chunk['chunk_index']}: lines {chunk['start_line']}-{chunk['end_line']}  "
                  f"{label}  {chunk.get('name')!r}{fp}{state}\n")
    return 0


def _cmd_verify(args, out, err):
    vault, catalog, index_path = _load(args)
    if args.source:
        try:
            text = read_text(args.source)
        except OSError as problem:
            raise UsageError(f"cannot read {args.source}: {problem}") from None
    else:
        text = sys.stdin.read()
    annotated, marked = verify_digest(vault, catalog, text, strict=args.strict)
    out.write(annotated if annotated.endswith("\n") else annotated + "\n")
    if marked:
        err.write(f"{marked} line(s) marked UNVERIFIED\n")
    return 1 if (args.strict and marked) else 0


def _cmd_brush(args, out, err):
    vault, catalog, index_path = _load(args)
    index = load_index(index_path)
    chunk = resolve_brush(index, args.brush)
    row = make_row(chunk, 1.0, settings=args.settings)
    row["content_sha256"] = chunk["content_sha256"]
    row["era"] = chunk.get("era")
    row["facet_words"] = chunk.get("facet_words")
    if args.json:
        _emit_json(row, out)
        return 0
    out.write(f"{row['brush_id']}  {row['name']!r}  ({row['library']}, {row['pack']}, era {row['era']})\n")
    out.write(f"  set: {row['set']} ({row['set_title']})\n")
    if row["note"]:
        out.write(f"  note: {row['note']} lines {row['start_line']}-{row['end_line']} ({row['heading']})\n")
    else:
        out.write("  note: none on disk yet\n")
    for other in row["also_in"]:
        out.write(f"  also in: {other['set']} ({other['note']})\n")
    out.write("  facets: " + " ".join(chunk.get("facet_words") or []) + "\n")
    bits = [f"{key[:-5]}={','.join(row[key])}" for key in TAG_FIELDS if row[key]]
    out.write(f"  tags ({row['tag_state']}): {'  '.join(bits) if bits else '(none)'}\n")
    if row["visual"]:
        out.write(f"  visual (described, not measured): {row['visual']}\n")
    if args.settings:
        for key in sorted(row["settings"]):
            out.write(f"    {key} = {json.dumps(row['settings'][key], ensure_ascii=False)}\n")
    return 0


COMMANDS = {"index": _cmd_index, "search": _cmd_search, "ask": _cmd_search, "similar": _cmd_similar,
            "facets": _cmd_facets, "files": _cmd_files, "chunks": _cmd_chunks, "verify": _cmd_verify,
            "brush": _cmd_brush}


def _console():
    for stream in (sys.stdout, sys.stderr, sys.stdin):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def main(argv=None):
    _console()
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.verb](args, sys.stdout, sys.stderr)
    except (UsageError, NotFound) as problem:
        print(f"error: {problem}", file=sys.stderr)
        return problem.exit_code
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
