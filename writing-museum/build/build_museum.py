#!/usr/bin/env python3
"""Build the Writing Museum from its scene specs.

    python writing-museum/build/build_museum.py propose <vault-path> [--id ID] [--order N] [--json]
    python writing-museum/build/build_museum.py check <scene.json>
    python writing-museum/build/build_museum.py build [--lint] [--scenes-dir DIR] [--out-dir DIR]

`propose` reads one work of creative-writing/vault/ (its frontmatter and its _ChunkTags/ sidecar,
nothing else), tallies its tags and prints the scene spec the mapping table (mapping.json)
suggests, with the source of every value. The table is a reference, never binding: a studio run
takes what it takes from it at the recipe stage and records where each value came from.

`check` validates one scene spec (data/scenes/<id>.json): the work exists, the panels exist, the
style names things the viewer has, and the room lays out.

`build` composes every spec under data/scenes/ into data/museum-manifest.json (everything
textual: the rooms, the wing, the works and their passages) and data/museum-layout.json
(everything spatial: hub + one scene per work), runs the lint first, and writes nothing on a
lint failure. It also writes data/library.json (library.py): every work of the vault, with a
room or without, and every scene, for the explore page (web/explore.html). `--lint` checks and
writes nothing.

A scene spec:

    {
      "id": "melting-away",                      the scene, note and door id (slug)
      "order": 3,                                position among the scenes (hall doors, tour order)
      "work": "03_Stories/06_Melting_Away.md",   vault-relative path of the work
      "name": "Melting Away",                    optional; the work's title otherwise
      "hub_side": "S",                           which wall of the hall the door is on: S or N
      "panels": "all",                           or a list of chunk numbers, 1-based
      "min_w": 10, "min_d": 8,                   optional minimum room size in metres
      "style": {                                 all optional; layout.py DEFAULT_STYLE fills the rest
        "theme": "cast-iron-glass", "wall": "#2f2224", "trim": "painted_trim", "floor": "parquet",
        "frame": "black-lacquer", "frame_small": "thin-metal",
        "light": {"color": "#ffb070", "intensity": 110}
      },
      "sources": {...}                           free-form: where each value came from (the run's record)
    }

Exit codes: 0 ok, 1 lint or check failed, 2 usage.
Stdlib only. Reads creative-writing/vault/ and never writes there.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import layout  # noqa: E402
import library  # noqa: E402
import works  # noqa: E402

TOOL = HERE.parent
DATA = TOOL / "data"
SCENES = DATA / "scenes"
MANIFEST_OUT = DATA / "museum-manifest.json"
LIBRARY_OUT = DATA / "library.json"
MAPPING = HERE / "mapping.json"
WING = {"id": works.WING_ID, "name": "Creative Writing", "image_base": "", "nouns": ["works", "passages"], "years": ""}


def load_mapping() -> dict:
    return json.loads(MAPPING.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- propose ------------
def propose(rel_path: str, scene_id: str | None = None, order: int = 1, vault: Path = works.VAULT, mapping: dict | None = None) -> dict:
    """The scene spec the mapping table suggests for a work, and the source of each value."""
    mapping = mapping or load_mapping()
    work = works.read_work(rel_path, vault)
    fm = work["frontmatter"]
    t = works.tallies(work)
    mode = fm.get("mode") or "unclassified"
    mode_row = mapping["mode"].get(mode) or mapping["mode"]["unclassified"]
    mode_key = mode if mode in mapping["mode"] else "unclassified"
    style, sources = {}, {}
    for k in ("theme", "frame", "frame_small"):
        style[k] = mode_row[k]
        sources[k] = f"mapping.json mode.{mode_key} (frontmatter mode: {mode})"
    moods = t["mood_tags"]
    if moods:
        top = moods[0][1]
        tied = [m for m, n in moods if n == top]
        mood = next((m for m in mapping["mood"] if m in tied), tied[0])
        row = mapping["mood"].get(mood)
        if row:
            style["wall"] = row["wall"]
            style["light"] = dict(row["light"])
            n_ch = len(work["chunks"])
            sources["wall"] = sources["light"] = f"mapping.json mood.{mood} (mood_tag in {top} of {n_ch} chunks)"
    for motif, n in t["motif_tags"]:
        row = mapping["motif"].get(motif)
        if row:
            style["floor"], style["trim"] = row["floor"], row["trim"]
            sources["floor"] = sources["trim"] = f"mapping.json motif.{motif} (motif_tag in {n} of {len(work['chunks'])} chunks)"
            break
    for k, v in layout.DEFAULT_STYLE.items():
        if k not in style:
            style[k] = dict(v) if isinstance(v, dict) else v
            sources[k] = "layout.py DEFAULT_STYLE (no row applied)"
    spec = {
        "id": scene_id or work["slug"], "order": int(order), "work": rel_path, "name": work["title"],
        "hub_side": "S" if int(order) % 2 else "N", "panels": "all",
        "min_w": 10, "min_d": 8, "style": style, "sources": sources,
    }
    untagged = [ch["index"] for ch in work["chunks"] if not ch["tagged"]]
    return {"spec": spec, "work": {"title": work["title"], "path": rel_path, "mode": mode, "type": fm.get("type"),
                                   "chunks": len(work["chunks"]), "words": work["words"], "untagged_chunks": untagged},
            "tallies": {k: v for k, v in t.items()},
            "panels": [{"n": ch["index"], "heading": ch["heading"], "file_lines": ch["file_lines"], "words": ch["words"],
                        "dims": works.panel_dims(ch["text"], (fm.get("type") or "") in works.VERSE_TYPES),
                        "mood_tags": ch["mood_tags"], "motif_tags": ch["motif_tags"]} for ch in work["chunks"]]}


def print_proposal(p: dict) -> None:
    w, s = p["work"], p["spec"]
    print(f"{w['title']}  ({w['path']})  {w['type']} · {w['mode']} · {w['chunks']} chunks · {w['words']} words")
    if w["untagged_chunks"]:
        print(f"  untagged chunks (no sidecar match): {w['untagged_chunks']}")
    for fam in ("mood_tags", "motif_tags"):
        print(f"  {fam}: " + (", ".join(f"{k} {n}" for k, n in p['tallies'][fam][:6]) or "none"))
    print("  panels:")
    for pn in p["panels"]:
        d = pn["dims"]
        print(f"    {pn['n']:2d}  lines {pn['file_lines'][0]}–{pn['file_lines'][1]}  {pn['words']:4d} words  {d['w_m']} × {d['h_m']} m  {pn['heading'] or ''}")
    print("  proposed style:")
    for k, v in s["style"].items():
        print(f"    {k:12s} {json.dumps(v):44s} <- {s['sources'][k]}")
    print(f"  hub_side {s['hub_side']} (order {s['order']}), min room {s['min_w']} × {s['min_d']} m, panels: all")


# ---------------------------------------------------------------- check / build ------
def load_specs(scenes_dir: Path) -> list[dict]:
    specs = []
    for path in sorted(scenes_dir.glob("*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        if spec.get("id") != path.stem:
            raise SystemExit(f"{path}: id {spec.get('id')!r} does not match the file name")
        specs.append(spec)
    specs.sort(key=lambda s: (int(s.get("order", 0)), s["id"]))
    return specs


def spec_errors(spec: dict, vault: Path) -> list[str]:
    errors = []
    for key in ("id", "work"):
        if not spec.get(key):
            errors.append(f"missing {key}")
    sid = spec.get("id", "")
    if sid and (not all(c.islower() or c.isdigit() or c == "-" for c in sid) or sid in ("hub",)):
        errors.append(f"id {sid!r} must be lower-case letters, digits and hyphens, and not 'hub'")
    if spec.get("hub_side", "S") not in ("S", "N"):
        errors.append("hub_side must be S or N")
    if spec.get("work") and not (vault / spec["work"]).is_file():
        errors.append(f"work not in the vault: {spec['work']}")
    if errors:
        return errors
    errors += layout.style_errors(layout.style_of(spec), sid)
    try:
        works.entry_for(spec, vault=vault)
    except (ValueError, KeyError, OSError) as e:
        errors.append(str(e))
    return errors


def compose(specs: list[dict], vault: Path = works.VAULT) -> dict:
    entries, room_specs = [], []
    for spec in specs:
        work = works.read_work(spec["work"], vault)
        entry = works.entry_for(spec, work, vault)
        entries.append(entry)
        room_specs.append(works.room_spec_for(spec, work, len(entry["works"])))
    dims = {w["id"]: w["dims"] for e in entries for w in e["works"]}
    result = layout.build(room_specs, entries, lambda w: dims[w["id"]])
    wing = {**WING, "rooms": [s["id"] for s in room_specs]}
    manifest = {"built": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "source": "creative-writing/vault",
                "rooms": result["rooms"], "artists": entries, "wings": [wing]}
    return {"manifest": manifest, "layout_result": result, "entries": entries, "room_specs": room_specs}


def build(scenes_dir: Path = SCENES, out_dir: Path = DATA, lint_only: bool = False, vault: Path = works.VAULT) -> int:
    specs = load_specs(scenes_dir) if scenes_dir.is_dir() else []
    bad = False
    for spec in specs:
        for err in spec_errors(spec, vault):
            print(f"  - {spec.get('id', '?')}: {err}")
            bad = True
    if bad:
        print("CHECK FAILED")
        return 1
    out = compose(specs, vault)
    errors = layout.lint(out["layout_result"], out["entries"], out["room_specs"])
    print(layout.report(out["layout_result"]) or "  (no scenes yet: the hall only)")
    if errors:
        print("LINT FAILED:")
        for e in errors[:60]:
            print("  -", e)
        return 1
    if lint_only:
        print("lint ok")
        return 0
    out_dir.mkdir(parents=True, exist_ok=True)
    mpath = out_dir / "museum-manifest.json"
    mpath.write_text(json.dumps(out["manifest"], ensure_ascii=False, indent=1), encoding="utf-8")
    lpath = layout.write_layout(out["layout_result"], out_dir / "museum-layout.json")
    n_panels = sum(len(e["works"]) for e in out["entries"])
    print(f"Wrote {mpath} — {len(out['entries'])} works, {n_panels} passages, {len(out['manifest']['rooms'])} rooms.")
    print(f"Wrote {lpath} — {len(out['layout_result']['layout']['scenes'])} scenes.")
    lib = library.compose(specs, vault, out)
    bpath = out_dir / "library.json"
    bpath.write_text(json.dumps(lib, ensure_ascii=False, indent=1), encoding="utf-8")
    n_passages = sum(len(w["passages"]) for w in lib["works"])
    print(f"Wrote {bpath} — {len(lib['works'])} works in {len(lib['folders'])} folders, {n_passages} passages, {len(lib['scenes'])} scenes.")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("propose", help="the scene spec the mapping table suggests for a work")
    p.add_argument("work", help="vault-relative path, e.g. 03_Stories/06_Melting_Away.md")
    p.add_argument("--id", default=None)
    p.add_argument("--order", type=int, default=1)
    p.add_argument("--json", action="store_true")
    p.add_argument("--vault", default=None, help=argparse.SUPPRESS)
    c = sub.add_parser("check", help="validate one scene spec")
    c.add_argument("spec")
    c.add_argument("--vault", default=None, help=argparse.SUPPRESS)
    b = sub.add_parser("build", help="compose every scene spec into the manifest and the layout")
    b.add_argument("--lint", action="store_true", help="check only, write nothing")
    b.add_argument("--scenes-dir", default=None)
    b.add_argument("--out-dir", default=None)
    b.add_argument("--vault", default=None, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    vault = Path(args.vault).resolve() if getattr(args, "vault", None) else works.VAULT
    if args.cmd == "propose":
        if not (vault / args.work).is_file():
            print(f"not a work in the vault: {args.work}", file=sys.stderr)
            return 2
        p = propose(args.work, args.id, args.order, vault)
        if args.json:
            print(json.dumps(p, ensure_ascii=False, indent=1))
        else:
            print_proposal(p)
        return 0
    if args.cmd == "check":
        path = Path(args.spec)
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"cannot read {path}: {e}", file=sys.stderr)
            return 2
        errors = spec_errors(spec, vault)
        if spec.get("id") and path.stem != spec["id"]:
            errors.append(f"file name {path.name} does not match id {spec['id']!r}")
        if errors:
            for e in errors:
                print("  -", e)
            print("CHECK FAILED")
            return 1
        entry = works.entry_for(spec, vault=vault)
        print(f"{spec['id']}: {entry['name']} — {len(entry['works'])} passages, style ok")
        return 0
    return build(Path(args.scenes_dir) if args.scenes_dir else SCENES,
                 Path(args.out_dir) if args.out_dir else DATA, args.lint, vault)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
