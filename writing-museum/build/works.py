"""Creative-writing works as Writing Museum entries (no geometry here).

Modelled on the Chronicle Museum's `people_entries.py`: one entry per work in the shape the
viewer already reads (an "artist" whose "works" hang on the walls). Here the artist is the work
and its works are PASSAGES: the chunks that `creative-writing/vault/tools/vault_search.py` cuts
the body into, each a verbatim text panel with the plot, context, mood and motif tags its
`_ChunkTags/` sidecar carries. Nothing in the vault is written; the 63 originals stay verbatim.

A panel's size in metres follows its text: a fixed width for prose or verse and a height from
the wrapped line count at the viewer's panel typography (web/js/procroom.js panelTexture), so the
salon packer (layout.py) can hang it like a painting of that size.
"""
from __future__ import annotations

import importlib.util
import re
import textwrap
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent
REPO = TOOL.parent
VAULT = REPO / "creative-writing" / "vault"
WING_ID = "writing"

# Panel typography, shared with the viewer (procroom.js): pixels per metre of panel, body font,
# line pitch, padding, title band. The viewer fits the text into the panel the builder sized.
PX_PER_M = 900
FONT_PX = 26
LINE_PX = 36
PAD_PX = 70
TITLE_PX = 64
CHAR_PX = 13.2             # mean advance of the serif body face at FONT_PX (measured in Chromium)
WIDTHS = {"prose": 1.2, "verse": 0.9, "short": 0.8}
MIN_H, MAX_H = 0.45, 2.6
MAX_PANEL_WORDS = 260      # a longer chunk is shown as consecutive parts, each a panel
VERSE_TYPES = ("poem", "prose-poem", "song")
TAG_FAMILIES = ("plot_tags", "context_tags", "mood_tags", "motif_tags")

_vs = None


def vault_search():
    """The vault's own frontmatter reader, chunker and sidecar loader, imported from where they live."""
    global _vs
    if _vs is None:
        path = VAULT / "tools" / "vault_search.py"
        spec = importlib.util.spec_from_file_location("vault_search", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _vs = mod
    return _vs


def slug_of(rel_path: str) -> str:
    stem = Path(rel_path).stem
    stem = re.sub(r"^\d+_", "", stem)
    s = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return s or "work"


HEADER_RE = re.compile(r"^\s*(\*\*(Type|Source|Text):\*\*|---\s*$|#\s)")


def is_header_line(line: str) -> bool:
    """A line of the vault's transcription header: `# Title`, `**Type:**`, `**Source:**`, `**Text:**`,
    or the `---` rule that closes it. Added by the transcription above each work; not the author's prose."""
    return bool(HEADER_RE.match(line))


def strip_header(text: str) -> str:
    """The chunk without leading transcription-header lines. The prose itself is untouched."""
    lines = text.split("\n")
    k = 0
    while k < len(lines) and (is_header_line(lines[k]) or not lines[k].strip()):
        k += 1
    return "\n".join(lines[k:]).strip()


def read_work(rel_path: str, vault: Path = VAULT) -> dict:
    """The work, its frontmatter, and its chunks with their sidecar tags. Read-only."""
    vs = vault_search()
    path = vault / rel_path
    text = path.read_text(encoding="utf-8")
    fm, body = vs.split_frontmatter(text)
    offset = text[: len(text) - len(body)].count("\n")   # body line 1 is file line offset + 1
    chunks = vs.chunk_body(body)
    sidecar = vs.load_chunk_tags(vault, rel_path) or {}
    side_chunks = sidecar.get("chunks", []) if isinstance(sidecar, dict) else []
    file_lines = text.splitlines()
    out = []
    for i, ch in enumerate(chunks, start=1):
        fp = vs.chunk_fingerprint(ch["text"])   # of the chunk as the vault cuts it: the sidecar's key
        tags = vs.match_sidecar_chunk(side_chunks, i, fp) or {}
        shown = strip_header(ch["text"])
        if not shown.strip():
            continue
        a = ch["start_line"] + offset
        while a <= len(file_lines) and (is_header_line(file_lines[a - 1]) or not file_lines[a - 1].strip()):
            a += 1
        out.append({
            "index": i, "heading": ch.get("heading"), "start_line": ch["start_line"], "end_line": ch["end_line"],
            "file_lines": [a, ch["end_line"] + offset],
            "text": shown, "words": len(shown.split()), "fingerprint": fp,
            "tagged": bool(tags),
            **{fam: list(tags.get(fam) or []) for fam in TAG_FAMILIES},
            "notes": tags.get("notes") or "",
        })
    title = fm.get("title") or re.sub(r"^\d+_", "", path.stem).replace("_", " ")
    return {"path": rel_path, "slug": slug_of(rel_path), "title": title, "frontmatter": fm, "line_offset": offset,
            "chunks": out, "words": len(body.split())}


def tallies(work: dict) -> dict:
    """Tag counts over the work's chunks, most common first, ties in vocabulary (first-seen) order."""
    out = {}
    for fam in TAG_FAMILIES:
        c = Counter()
        for ch in work["chunks"]:
            c.update(ch[fam])
        out[fam] = c.most_common()
    return out


def wrapped_lines(text: str, width_m: float) -> int:
    chars = max(20, int((width_m * PX_PER_M - 2 * PAD_PX) / CHAR_PX))
    n = 0.0
    paragraphs = text.split("\n\n")
    for pi, para in enumerate(paragraphs):
        for line in para.split("\n"):
            n += max(1, len(textwrap.wrap(line, chars))) if line.strip() else 0.6
        if pi < len(paragraphs) - 1:
            n += 0.6
    return int(round(n)) or 1


def panel_dims(text: str, verse: bool) -> dict:
    words = len(text.split())
    kind = "verse" if verse else ("short" if words < 60 else "prose")
    w = WIDTHS[kind]
    lines = wrapped_lines(text, w)
    h = (2 * PAD_PX + TITLE_PX + lines * LINE_PX) / PX_PER_M
    h = round(min(MAX_H, max(MIN_H, h)), 3)
    ptype = "poem" if verse else ("panel-short" if kind == "short" else "panel")
    return {"h_m": h, "w_m": w, "disp_h": h, "disp_w": w, "scale": 1.0, "source": "panel", "type": ptype, "lines": lines}


def split_long(text: str, max_words: int = MAX_PANEL_WORDS) -> list[str]:
    """A chunk longer than max_words as consecutive parts, cut at paragraph, then line, then sentence ends."""
    if len(text.split()) <= max_words:
        return [text]
    parts, buf, n = [], [], 0
    units = []
    for para in text.split("\n\n"):
        lines = para.split("\n")
        if len(lines) > 1:
            units += [(ln, "\n") for ln in lines[:-1]] + [(lines[-1], "\n\n")]
        elif len(para.split()) > max_words:
            sents = re.split(r"(?<=[.!?])\s+", para)
            units += [(sn, " ") for sn in sents[:-1]] + [(sents[-1], "\n\n")]
        else:
            units.append((para, "\n\n"))
    for unit, sep in units:
        w = len(unit.split())
        if buf and n + w > max_words:
            parts.append(buf)
            buf, n = [], 0
        buf.append((unit, sep))
        n += w
    if buf:
        parts.append(buf)
    out = []
    for part in parts:
        s = "".join(u + sep for u, sep in part)
        out.append(s.strip())
    return [x for x in out if x]


def select_chunks(work: dict, selection) -> list[dict]:
    if selection in (None, "all"):
        return list(work["chunks"])
    wanted = set(int(i) for i in selection)
    picked = [ch for ch in work["chunks"] if ch["index"] in wanted]
    missing = wanted - {ch["index"] for ch in picked}
    if missing:
        raise ValueError(f"{work['path']}: no chunk numbered {sorted(missing)} (it has {len(work['chunks'])})")
    return picked


def intro_for(work: dict, n_panels: int) -> dict:
    """The room's title card, from the frontmatter alone."""
    fm = work["frontmatter"]
    kind = (fm.get("type") or "work").replace("-", " ")
    mode = fm.get("mode") or "unclassified"
    themes = fm.get("themes") or []
    bits = [f"A {kind}, {mode.replace('-', ' ')} mode."]
    if themes:
        bits.append("Themes: " + ", ".join(t.replace("-", " ") for t in themes[:5]) + ".")
    bits.append(f"{n_panels} passage{'s' if n_panels != 1 else ''}, verbatim from {work['path']}.")
    return {"title": work["title"], "years": mode, "summary": " ".join(bits)}


def entry_for(spec: dict, work: dict | None = None, vault: Path = VAULT) -> dict:
    """One manifest entry (artist-shaped) for a scene spec: the work, whose works are its panels."""
    work = work or read_work(spec["work"], vault)
    fm = work["frontmatter"]
    verse = (fm.get("type") or "") in VERSE_TYPES
    chunks = select_chunks(work, spec.get("panels", "all"))
    if not chunks:
        raise ValueError(f"{work['path']}: no passages selected")
    sid = spec["id"]
    n = len(chunks)
    panels = []
    for k, ch in enumerate(chunks, start=1):
        a, b = ch["file_lines"]
        heading = ch["heading"] if ch["heading"] and ch["heading"].strip().lower() != work["title"].strip().lower() else None
        parts = split_long(ch["text"])
        for j, text in enumerate(parts, start=1):
            part = f" · part {j} of {len(parts)}" if len(parts) > 1 else ""
            panels.append({
                "id": f"{sid}--{ch['index']}" + (f"-{j}" if len(parts) > 1 else ""),
                "title": (heading or f"Passage {k}") + part,
                "year": None,
                "medium": f"passage {k} of {n}{part}",
                "location": f"{work['path']} · lines {a}–{b}",
                "description": text,
                "text": text,
                "heading": heading,
                "chunk": ch["index"],
                "image": None,
                "credit": {"work": work["title"], "source_path": work["path"], "lines": [a, b],
                           "author": "the author", "license": "the author's own text, verbatim and unedited"},
                "tags": {fam: ch[fam] for fam in TAG_FAMILIES},
                "notes": ch["notes"],
                "dims": panel_dims(text, verse),
            })
    return {
        "slug": sid, "name": work["title"], "short_name": work["title"], "lifespan": None, "born": None,
        "region": None, "country": None, "movements": [fm.get("mode") or "unclassified"],
        "discipline": [fm.get("type") or "work"], "wikipedia": None, "cover": None,
        "room": sid, "order": int(spec.get("order", 0)), "wing": WING_ID,
        "mode": fm.get("mode") or "unclassified", "type": fm.get("type"), "vault_path": work["path"],
        "themes": [{"slug": t, "title": t.replace("-", " ")} for t in (fm.get("themes") or [])],
        "works": panels,
    }


def room_spec_for(spec: dict, work: dict, n_panels: int) -> dict:
    """The layout builder's room spec for a scene spec."""
    return {
        "id": spec["id"], "name": spec.get("name") or work["title"], "wing": WING_ID,
        "era": work["frontmatter"].get("mode") or "unclassified",
        "years": spec.get("years") or (work["frontmatter"].get("mode") or "unclassified"),
        "min_w": float(spec.get("min_w", 10)), "min_d": float(spec.get("min_d", 8)),
        "intro": spec.get("intro") or intro_for(work, n_panels),
        "style": spec.get("style") or {}, "hub_side": spec.get("hub_side", "S"), "order": int(spec.get("order", 0)),
    }


if __name__ == "__main__":
    import sys
    for rel in sys.argv[1:]:
        w = read_work(rel)
        t = tallies(w)
        print(f"{w['title']}  ({rel}): {len(w['chunks'])} chunks, {w['words']} words, mode {w['frontmatter'].get('mode')}")
        for ch in w["chunks"]:
            d = panel_dims(ch["text"], (w["frontmatter"].get("type") or "") in VERSE_TYPES)
            print(f"  {ch['index']:2d} lines {ch['file_lines'][0]}-{ch['file_lines'][1]}  {ch['words']:4d} w  panel {d['w_m']}×{d['h_m']} m  mood {ch['mood_tags']}  motif {ch['motif_tags']}")
        print("  moods", t["mood_tags"][:4], " motifs", t["motif_tags"][:4])
