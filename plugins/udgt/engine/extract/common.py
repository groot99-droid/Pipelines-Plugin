"""Shared helpers for the extractors: reading text, walking Markdown, building nodes.

Every extractor returns a Part: a list of nodes and a list of edges. A node is a dict with
`id`, `kind`, `area`, `title`, and optionally `text` (a short excerpt), `source` ({path, line})
and `meta`. An edge is {"from", "to", "kind"}. Paths in `source` are relative to the game root.
"""

import fnmatch
import re
from pathlib import Path

EXCERPT = 600
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NUMBERED = re.compile(r"^(?:§\s*)?(\d+(?:\.\d+)*)\.?\s+(.*)$")
BOOK = re.compile(r"^(PART|BOOK)\s+([0-9IVXLC]+)\b[\s.:—-]*(.*)$", re.IGNORECASE)
TABLE_RULE = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


class Part:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.notes = []
        self.bodies = {}

    def node(self, id, kind, area, title, text=None, source=None, meta=None):
        entry = {"id": id, "kind": kind, "area": area, "title": title}
        if text:
            entry["text"] = excerpt(text)
            self.bodies[id] = text
        if source:
            entry["source"] = source
        if meta:
            entry["meta"] = meta
        self.nodes.append(entry)
        return entry

    def edge(self, src, dst, kind):
        self.edges.append({"from": src, "to": dst, "kind": kind})

    def extend(self, other):
        self.nodes.extend(other.nodes)
        self.edges.extend(other.edges)
        self.notes.extend(other.notes)
        self.bodies.update(other.bodies)


def excerpt(text, limit=EXCERPT):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def read(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")


def rel(game, path):
    return Path(path).resolve().relative_to(Path(game).resolve()).as_posix()


def glob(game, patterns, exclude=()):
    """Files under the game root matching any pattern, sorted, minus excluded globs."""
    root = Path(game)
    found = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file():
                found.add(path)
    out = []
    for path in sorted(found):
        name = rel(root, path)
        if any(fnmatch.fnmatch(name, ex) or fnmatch.fnmatch(path.name, ex) for ex in exclude):
            continue
        out.append(path)
    return out


def slug(text, limit=48):
    text = re.sub(r"[`*_\[\]()]", "", text.lower())
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:limit].rstrip("-") or "x"


def strip_md(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    return text.strip()


def sections(text):
    """Split Markdown into heading sections, skipping headings inside code fences.

    Yields dicts: level, raw (heading text), line (1-based), body (lines until the next heading
    of any level), number (dotted section number or BOOK/PART label, or None), title.
    """
    lines = text.splitlines()
    heads = []
    fenced = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = HEADING.match(line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))
    for k, (i, level, raw) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        number, title = section_number(raw)
        yield {
            "level": level,
            "raw": raw,
            "line": i + 1,
            "body": "\n".join(lines[i + 1:end]),
            "number": number,
            "title": title,
        }


def section_number(raw):
    plain = strip_md(raw)
    m = NUMBERED.match(plain)
    if m:
        return m.group(1), m.group(2).strip()
    m = BOOK.match(plain)
    if m:
        label = f"{m.group(1).upper()} {m.group(2).upper()}"
        return label, (m.group(3).strip() or label)
    return None, plain


def split_row(line):
    """Cells of a Markdown table row, honouring escaped pipes and pipes inside backticks."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, cur, tick = [], [], False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "`":
            tick = not tick
        if ch == "|" and not tick:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def tables(text):
    """Every Markdown table in text: (start line 1-based, header cells, rows as (line, cells))."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and TABLE_RULE.match(lines[i + 1].strip()):
            header = split_row(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append((j + 1, split_row(lines[j])))
                j += 1
            yield i + 1, header, rows
            i = j
        else:
            i += 1


def compile_all(patterns):
    return [re.compile(p) for p in patterns]
