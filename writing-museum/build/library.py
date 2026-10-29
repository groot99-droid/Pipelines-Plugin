"""The library: every work of the creative-writing vault, and every scene, as one JSON file the
explore page (web/explore.html) reads.

`build_museum.py build` writes data/library.json beside the manifest and the layout. Where the
manifest carries only the works that have a room, the library carries all of them, so the page
can be read through from one end to the other: each work's frontmatter, the blurb its folder's
`_index.md` gives it, and its passages, verbatim and cited by file lines, cut the way the vault's
own search tool cuts them (works.read_work), with the tags their `_ChunkTags/` sidecar carries.
The scenes section is the scene specs as written, with the panel count and room size the build
gave each one, and the path of the note that records how it was made.

Read-only over the vault, like the rest of this folder. The transcription header above a work's
text is left off its passages; nothing in the text is changed.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import works

FRONTMATTER_KEYS = ("type", "mode", "genre", "status", "pov", "tense", "themes", "archetypes",
                    "source_volume", "source_lines")
NOTE_DIR = "studio/vault/writing-museum/3d"

INDEX_LINE_RE = re.compile(r"^\s*[-*]\s+\[\[([^\]|]+)(?:\|[^\]]*)?\]\]\s*[—–-]+\s*(.*)$")
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]")
ARROW_RE = re.compile(r"\s*(?:→|->)\s*annotation:.*$")


def list_works(vault: Path) -> list[str]:
    """Vault-relative paths of the works, in the vault's own order: every .md under a numbered
    folder except a folder's `_index.md`. The same rule vault_search.py indexes by."""
    vs = works.vault_search()
    return [path.relative_to(vault).as_posix()
            for path, kind in vs.iter_source_files(vault, include_annotations=False) if kind == "work"]


def folder_name(folder: str, index_fm: dict | None) -> str:
    """"Stories" from `03_Stories`, or from the folder index's title when it has one."""
    title = (index_fm or {}).get("title") or ""
    title = re.sub(r"\s*[—–-]+\s*Index\s*$", "", title).strip()
    title = re.sub(r"^\d{2}[_ ]", "", title).strip().replace("_", " ")
    return title or re.sub(r"^\d{2}_", "", folder).replace("_", " ")


def read_folder_index(vault: Path, folder: str) -> dict:
    """The folder's `_index.md`: its name, its one-paragraph description, and the blurb it gives
    each work. All optional: a folder without one gets a name from its own and no blurbs."""
    path = vault / folder / "_index.md"
    out = {"folder": folder, "name": folder_name(folder, None), "about": "", "blurbs": {}}
    if not path.is_file():
        return out
    vs = works.vault_search()
    fm, body = vs.split_frontmatter(path.read_text(encoding="utf-8"))
    out["name"] = folder_name(folder, fm)
    for line in body.splitlines():
        m = INDEX_LINE_RE.match(line)
        if m:
            target = m.group(1).strip()
            rel = target if target.endswith(".md") else target + ".md"
            blurb = ARROW_RE.sub("", m.group(2)).strip()
            blurb = WIKILINK_RE.sub(lambda w: (w.group(2) or w.group(1)).strip(), blurb)
            out["blurbs"][rel] = blurb.strip(" .") + ("." if blurb.strip() else "")
        elif line.strip() and not out["about"] and not line.lstrip().startswith(("#", "-", "*", "|", ">")):
            out["about"] = WIKILINK_RE.sub(lambda w: (w.group(2) or w.group(1)).strip(), line.strip())
    return out


def passage_of(ch: dict) -> dict:
    return {
        "n": ch["index"], "heading": ch["heading"], "lines": list(ch["file_lines"]), "words": ch["words"],
        "text": ch["text"], "tagged": ch["tagged"],
        "tags": {fam: list(ch[fam]) for fam in works.TAG_FAMILIES},
    }


def work_entry(rel: str, vault: Path, blurb: str = "", scene: str | None = None) -> dict:
    w = works.read_work(rel, vault)
    fm = w["frontmatter"]
    folder = rel.split("/", 1)[0] if "/" in rel else ""
    meta = {}
    for key in FRONTMATTER_KEYS:
        value = fm.get(key)
        if value in (None, "", []):
            continue
        meta[key] = [str(v) for v in value] if isinstance(value, list) else str(value)
    return {
        "slug": w["slug"], "path": rel, "title": w["title"], "folder": folder,
        **meta,
        "words": w["words"], "blurb": blurb, "scene": scene,
        "passages": [passage_of(ch) for ch in w["chunks"]],
    }


def scene_entry(spec: dict, n_panels: int, room: dict | None) -> dict:
    size = list(room.get("size", [])) if room else []
    return {
        "id": spec["id"], "order": int(spec.get("order", 0)), "work": spec["work"],
        "slug": works.slug_of(spec["work"]), "name": spec.get("name") or "",
        "hub_side": spec.get("hub_side", "S"), "panels": spec.get("panels", "all"),
        "passages": n_panels, "size": size,
        "style": spec.get("style") or {}, "sources": spec.get("sources") or {},
        "intro": (room or {}).get("intro") or {},
        "note": f"{NOTE_DIR}/{spec['id']}.md",
    }


def compose(specs: list[dict], vault: Path = works.VAULT, composed: dict | None = None) -> dict:
    """The library: folders in vault order, every work in each, and the scenes in hall order.
    `composed` is build_museum.compose()'s result for the same specs, for each scene's panel
    count and room size; without it those fields are counted here and left empty."""
    by_work = {s["work"]: s["id"] for s in specs}
    folders, folder_rows, work_rows = {}, [], []
    for rel in list_works(vault):
        folder = rel.split("/", 1)[0] if "/" in rel else ""
        if folder not in folders:
            folders[folder] = read_folder_index(vault, folder)
            folder_rows.append({"folder": folder, "name": folders[folder]["name"], "about": folders[folder]["about"]})
        blurb = folders[folder]["blurbs"].get(rel, "")
        work_rows.append(work_entry(rel, vault, blurb, by_work.get(rel)))
    panels = {}
    rooms = {}
    if composed:
        panels = {e["slug"]: len(e["works"]) for e in composed["entries"]}
        rooms = composed["layout_result"]["layout"]["scenes"]
    scene_rows = []
    for spec in sorted(specs, key=lambda s: (int(s.get("order", 0)), s["id"])):
        n = panels.get(spec["id"])
        if n is None:
            n = len(works.entry_for(spec, vault=vault)["works"])
        scene_rows.append(scene_entry(spec, n, rooms.get(spec["id"])))
    return {
        "built": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "creative-writing/vault",
        "folders": folder_rows, "works": work_rows, "scenes": scene_rows,
    }
