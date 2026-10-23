"""UDGT: UI, Dataset & Gameplay Teardown of a game's repository.

    python udgt.py scan   --profile <teardown>/profile.json [--game <checkout>]
    python udgt.py check  --profile P [--game G] [--strict] [--json]
    python udgt.py diff   --profile P [--game G]
    python udgt.py brief  <stage> --profile P [--json]
    python udgt.py record <stage> --profile P --question Q --answer A [--asked-as chat|file]
    python udgt.py build  --profile P [--game G]
    python udgt.py query  "<words>" --profile P [--kind K] [--area A] [--limit N] [--json]
    python udgt.py show   <node-id> --profile P [--json]
    python udgt.py stages --profile P

`scan` reads the game checkout (never writes it) and writes teardown.json beside the profile: a
graph of nodes (sections, decisions, open questions, datasets, records, code areas, anchors,
tokens, copy, screens, screenshots, pull requests, plans, answers) and the edges between them,
plus the commit list. `check` writes nothing: it reports broken citations, notes from the
extractors, links in the chapters that point nowhere, and whether teardown.json is behind the
game. `diff` compares a fresh scan with teardown.json. `brief` prints a stage's questions for the
owner, with the gaps the scan found. `record` appends the owner's answer verbatim to answers.json;
nothing else writes that file and nothing edits an answer. `build` renders the explorer page
into <teardown>/explorer/, themed with the game's own design tokens and fonts (the font files
the profile names are copied from the game; nothing else is).

Stdlib only. Exit codes: 0 done, 1 check found problems (with --strict) or a lookup missed,
2 usage error.
"""

import argparse
import datetime
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
sys.path.insert(0, str(HERE))

from extract import code, datasets, decisions, docs, future, history, lore, refs, tables, ui  # noqa: E402
from extract.common import rel  # noqa: E402
import profile as profiles  # noqa: E402

EXIT_OK, EXIT_FAILED, EXIT_USAGE = 0, 1, 2
TEARDOWN = "teardown.json"
ANSWERS = "answers.json"
CHAPTER_LINK = re.compile(r"\[\[([a-z]+:[^\]|]+)(?:\|[^\]]*)?\]\]")


class Usage(Exception):
    pass


# ---------------------------------------------------------------- scanning

def extract_all(prof, game):
    part = docs.extract(game, prof)
    for module in (decisions, tables, datasets, code, ui):
        part.extend(module.extract(game, prof))
    doc_paths = [n["source"]["path"] for n in part.nodes if n["kind"] == "doc"]
    hist_part, hist = history.extract(game, prof, doc_paths)
    part.extend(hist_part)
    for n in part.nodes:
        if n["kind"] == "doc":
            n.setdefault("meta", {})["history"] = hist.get("docs", {}).get(n["source"]["path"])
    sections = [n for n in part.nodes if n["kind"] == "section"]
    part.extend(future.extract(sections, part.bodies, prof))
    part.extend(lore.extract(prof))
    part.extend(load_answers(prof))
    ids = {n["id"] for n in part.nodes}
    # citations in text, then the structural edges' targets resolved the same way
    sources = [(nid, body) for nid, body in part.bodies.items() if nid in ids]
    cite_edges, broken = refs.link(sources, prof.get("refs", []), ids)
    edges = []
    for e in part.edges:
        if e["from"].startswith("commit:"):
            continue
        hit = refs.resolve(e["to"], ids)
        if hit:
            edges.append(dict(e, to=hit))
        else:
            broken.append({"from": e["from"], "target": e["to"], "ref": e["kind"]})
    edges.extend(cite_edges)
    edges = dedupe_edges(edges)
    commits = hist.get("commits", [])
    for c in commits:
        c["ids"] = [i for i in c["ids"] if f"dec:{i}" in ids]
    return part, edges, broken, hist


def dedupe_edges(edges):
    seen, out = set(), []
    for e in edges:
        key = (e["from"], e["to"], e["kind"])
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


def load_answers(prof):
    from extract.common import Part
    part = Part()
    for k, a in enumerate(read_answers(prof)["answers"], 1):
        part.node(f"answer:{k}", "answer", "owner", f"{a['stage']}: {a['question'][:90]}",
                  text=f"Q: {a['question']}\nA: {a['answer']}",
                  meta={"stage": a["stage"], "date": a["date"], "question": a["question"],
                        "answer": a["answer"], "asked_as": a.get("asked_as", "chat")})
    return part


def compose(prof, game):
    part, edges, broken, hist = extract_all(prof, game)
    counts = {}
    for n in part.nodes:
        counts[n["kind"]] = counts.get(n["kind"], 0) + 1
    return {
        "udgt": 1,
        "name": prof["name"],
        "slug": prof["slug"],
        "scanned": datetime.date.today().isoformat(),
        "game": {"repo": prof.get("game", {}).get("repo"), "browse": prof.get("game", {}).get("browse"),
                 "head": hist.get("head"),
                 "shallow": hist.get("shallow")},
        "lore": {spec["id"]: {"browse": spec.get("browse")} for spec in prof.get("lore", [])},
        "stages": [{k: s[k] for k in ("id", "slug", "title", "areas") if k in s} for s in prof["stages"]],
        "explorer": prof.get("explorer", {}),
        "compare": prof.get("compare", []),
        "counts": dict(sorted(counts.items())),
        "nodes": part.nodes,
        "edges": edges,
        "commits": hist.get("commits", []),
        "notes": part.notes,
        "broken": broken,
    }


def dumps(data):
    """JSON with one list entry per line: compact, and a diff shows which entries changed."""
    if not isinstance(data, dict):
        return json.dumps(data, ensure_ascii=False)
    parts = []
    for key, value in data.items():
        if isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            body = ",\n  ".join(json.dumps(v, ensure_ascii=False, separators=(",", ":")) for v in value)
            parts.append(f"{json.dumps(key)}: [\n  {body}\n ]")
        else:
            parts.append(f"{json.dumps(key)}: {json.dumps(value, ensure_ascii=False)}")
    return "{\n " + ",\n ".join(parts) + "\n}"


def save_json(path, data):
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_text(dumps(data) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_teardown(prof):
    path = prof["_home"] / TEARDOWN
    if not path.exists():
        raise Usage(f"no {TEARDOWN} beside the profile yet: run `scan` first")
    return json.loads(path.read_text(encoding="utf-8"))


def read_answers(prof):
    path = prof["_home"] / ANSWERS
    if not path.exists():
        return {"answers": []}
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- commands

def cmd_scan(prof, args):
    game = profiles.game_root(prof, args.game)
    data = compose(prof, game)
    save_json(prof["_home"] / TEARDOWN, data)
    print(f"scanned {game} at {(data['game']['head'] or '?')[:7]}: {len(data['nodes'])} nodes, "
          f"{len(data['edges'])} edges, {len(data['commits'])} commits")
    for kind, n in data["counts"].items():
        print(f"  {kind:<12} {n}")
    for note in data["notes"]:
        print(f"  note: {note}")
    if data["broken"]:
        print(f"  {len(data['broken'])} citations point nowhere (see `check`)")
    return EXIT_OK


def chapter_files(prof):
    folder = prof["_home"] / "chapters"
    return sorted(folder.glob("*.md")) if folder.is_dir() else []


def cmd_check(prof, args):
    findings = []
    game = profiles.game_root(prof, args.game)
    data = compose(prof, game)
    ids = {n["id"] for n in data["nodes"]}
    for b in data["broken"]:
        findings.append({"kind": "broken-ref", "where": b["from"], "what": f"{b['ref']} -> {b['target']}"})
    for note in data["notes"]:
        findings.append({"kind": "note", "where": "scan", "what": note})
    for n in data["nodes"]:
        meta = n.get("meta", {})
        if n["kind"] == "plan" and meta.get("withdrawn") and meta["withdrawn"] < meta["count"]:
            findings.append({"kind": "mixed-plan", "where": n["id"],
                             "what": f"{meta['withdrawn']} of {meta['count']} sentences say it was withdrawn"})
        if n["kind"] == "question" and not meta.get("resolved"):
            findings.append({"kind": "unresolved", "where": n["id"], "what": n["title"]})
    for path in chapter_files(prof):
        text = path.read_text(encoding="utf-8")
        for m in CHAPTER_LINK.finditer(text):
            if m.group(1) not in ids:
                line = text[: m.start()].count("\n") + 1
                findings.append({"kind": "chapter-link", "where": f"chapters/{path.name}:{line}",
                                 "what": f"[[{m.group(1)}]] is not in the teardown"})
    saved = prof["_home"] / TEARDOWN
    if saved.exists():
        old = json.loads(saved.read_text(encoding="utf-8"))
        if old.get("game", {}).get("head") != data["game"]["head"]:
            findings.append({"kind": "stale", "where": TEARDOWN,
                             "what": f"scanned at {(old['game'].get('head') or '?')[:7]}, game is at {(data['game']['head'] or '?')[:7]}"})
    else:
        findings.append({"kind": "stale", "where": TEARDOWN, "what": "never scanned"})
    if args.json:
        print(json.dumps(findings, indent=1, ensure_ascii=False))
    else:
        kinds = {}
        for f in findings:
            kinds.setdefault(f["kind"], []).append(f)
        for kind, rows in kinds.items():
            print(f"{kind}: {len(rows)}")
            for f in rows[: args.limit]:
                print(f"  {f['where']}: {f['what']}")
            if len(rows) > args.limit:
                print(f"  ... {len(rows) - args.limit} more (--limit)")
        if not findings:
            print("clean")
    bad = [f for f in findings if f["kind"] in ("broken-ref", "chapter-link", "stale")]
    return EXIT_FAILED if args.strict and bad else EXIT_OK


def cmd_diff(prof, args):
    old = load_teardown(prof)
    new = compose(prof, profiles.game_root(prof, args.game))
    before = {n["id"]: n for n in old["nodes"]}
    after = {n["id"]: n for n in new["nodes"]}
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(i for i in set(after) & set(before)
                     if (after[i].get("text"), after[i].get("meta")) != (before[i].get("text"), before[i].get("meta")))
    known = {c["h"] for c in old.get("commits", [])}
    fresh = [c for c in new["commits"] if c["h"] not in known]
    print(f"game: {(old['game'].get('head') or '?')[:7]} -> {(new['game']['head'] or '?')[:7]}, {len(fresh)} new commits")
    for c in fresh[: args.limit]:
        print(f"  {c['d']} {c['h']} {c['s']}")
    for label, rows in (("added", added), ("removed", removed), ("changed", changed)):
        print(f"{label}: {len(rows)}")
        for i in rows[: args.limit]:
            print(f"  {i}  {(after.get(i) or before.get(i))['title'][:90]}")
    return EXIT_OK


def stage_gaps(data, st, limit=12):
    words = [w.lower() for w in st.get("keywords", [])]
    areas = set(st["areas"])

    def relevant(n):
        hay = (n["title"] + " " + n.get("text", "")).lower()
        return n.get("area") in areas or any(w in hay for w in words)

    gaps = []
    for n in data["nodes"]:
        if n["kind"] == "open" and relevant(n):
            gaps.append({"id": n["id"], "kind": "open", "text": n["text"]})
        elif n["kind"] == "question" and not n.get("meta", {}).get("resolved") and relevant(n):
            gaps.append({"id": n["id"], "kind": "unresolved", "text": n["text"]})
        elif n["kind"] == "plan" and n["meta"].get("withdrawn") and relevant(n):
            gaps.append({"id": n["id"], "kind": "withdrawn-plan", "text": n["text"]})
    return gaps[:limit]


def cmd_brief(prof, args):
    st = profiles.stage(prof, args.stage)
    data = load_teardown(prof)
    prior = [a for a in read_answers(prof)["answers"] if a["stage"] == st["id"]]
    areas = set(st["areas"])
    counts = {}
    for n in data["nodes"]:
        if n.get("area") in areas:
            counts[n["kind"]] = counts.get(n["kind"], 0) + 1
    brief = {"stage": st["id"], "slug": st["slug"], "title": st["title"],
             "prompts": st["prompts"], "gaps": stage_gaps(data, st),
             "in_scope": counts, "answered": prior}
    if args.json:
        print(json.dumps(brief, indent=1, ensure_ascii=False))
        return EXIT_OK
    print(f"Stage {st['id']} — {st['title']}")
    print("In scope: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    print("\nQuestions for the owner:")
    for k, p in enumerate(st["prompts"], 1):
        print(f"  {k}. {p}")
    if brief["gaps"]:
        print("\nGaps the scan found:")
        for g in brief["gaps"]:
            print(f"  [{g['kind']}] {g['id']}: {g['text'][:160]}")
    if prior:
        print("\nAlready answered:")
        for a in prior:
            print(f"  {a['date']} Q: {a['question']}\n             A: {a['answer']}")
    return EXIT_OK


def cmd_record(prof, args):
    st = profiles.stage(prof, args.stage)
    question, answer = args.question.strip(), args.answer.strip()
    if not question or not answer:
        raise Usage("record needs a non-empty --question and --answer (the owner's words, verbatim)")
    book = read_answers(prof)
    book.setdefault("about", "The owner's answers to the teardown briefs, verbatim, in the order given. "
                             "Appended by `udgt.py record`; never generated or edited.")
    book["answers"].append({"stage": st["id"], "question": question, "answer": answer,
                            "date": datetime.date.today().isoformat(), "asked_as": args.asked_as})
    save_json(prof["_home"] / ANSWERS, book)
    print(f"recorded answer {len(book['answers'])} for stage {st['id']} ({st['slug']})")
    return EXIT_OK


def copy_fonts(prof, game, out):
    """Copy the font files the profile names from the game into explorer/fonts/; @font-face rules."""
    fonts = prof.get("ui", {}).get("fonts", [])
    if not fonts:
        return [], []
    if game is None:
        return [], ["no game checkout: fonts not copied, the page falls back to system fonts"]
    folder = out / "fonts"
    folder.mkdir(exist_ok=True)
    rules, notes = [], []
    for font in fonts:
        src = game / font["file"]
        if not src.is_file():
            notes.append(f"font {font['file']} not found in the game")
            continue
        shutil.copyfile(src, folder / src.name)
        rules.append("@font-face {\n"
                     f"  font-family: '{font['family']}';\n"
                     f"  font-weight: {font.get('weight', '400')};\n"
                     "  font-display: swap;\n"
                     f"  src: url('fonts/{src.name}') format('woff2');\n"
                     "}")
    return rules, notes


def theme_css(data, prof, font_rules=()):
    """The game's fonts and tokens, then the explorer's roles mapped onto them."""
    tokens = [(n["title"], n["meta"]["value"]) for n in data["nodes"] if n["kind"] == "token"]
    lines = ["/* Generated by udgt.py build from the game's design tokens. Do not edit. */"]
    lines += list(font_rules)
    lines.append(":root {")
    lines += [f"  {name}: {value};" for name, value in tokens]
    lines.append("}")
    theme = prof.get("explorer", {}).get("theme", {})
    if theme:
        lines.append(":root {")
        for role, value in theme.items():
            lines.append(f"  --x-{role}: {value};")
        lines.append("}")
    return "\n".join(lines) + "\n"


def cmd_build(prof, args):
    data = load_teardown(prof)
    out = prof["_home"] / "explorer"
    out.mkdir(exist_ok=True)
    for name in ("index.html", "explorer.css", "explorer.js"):
        shutil.copyfile(PLUGIN / "explorer" / name, out / name)
    try:
        game = profiles.game_root(prof, args.game)
    except profiles.ProfileError:
        game = None
    rules, notes = copy_fonts(prof, game, out)
    (out / "theme.css").write_text(theme_css(data, prof, rules), encoding="utf-8")
    for note in notes:
        print(f"  note: {note}")
    chapters = []
    for path in chapter_files(prof):
        text = path.read_text(encoding="utf-8")
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), path.stem)
        chapters.append({"file": path.name, "title": title, "markdown": text})
    save_json(out / "chapters.json", {"chapters": chapters})
    print(f"built {rel(prof['_home'], out)}/ with {len(chapters)} chapters; serve the teardown folder and open explorer/index.html")
    return EXIT_OK


def score(node, words):
    hay_title = node["title"].lower()
    hay_id = node["id"].lower()
    hay_text = node.get("text", "").lower()
    total = 0
    for w in words:
        hits = 3 * hay_title.count(w) + 2 * hay_id.count(w) + hay_text.count(w)
        if not hits:
            return 0
        total += hits
    return total


def cmd_query(prof, args):
    data = load_teardown(prof)
    words = [w.lower() for w in re.findall(r"[\w.:-]+", args.words)]
    if not words:
        raise Usage("query needs words")
    rows = []
    for n in data["nodes"]:
        if args.kind and n["kind"] != args.kind:
            continue
        if args.area and n.get("area") != args.area:
            continue
        s = score(n, words)
        if s:
            rows.append((s, n))
    rows.sort(key=lambda r: (-r[0], r[1]["id"]))
    rows = rows[: args.limit]
    if args.json:
        print(json.dumps([n for _, n in rows], indent=1, ensure_ascii=False))
    else:
        for s, n in rows:
            src = n.get("source")
            where = f"  {src['path']}:{src['line']}" if src else ""
            print(f"{n['id']}  [{n['kind']}] {n['title'][:90]}{where}")
    return EXIT_OK if rows else EXIT_FAILED


def cmd_show(prof, args):
    data = load_teardown(prof)
    node = next((n for n in data["nodes"] if n["id"] == args.id), None)
    if not node:
        print(f"no node {args.id}; try `query`", file=sys.stderr)
        return EXIT_FAILED
    out_edges = [e for e in data["edges"] if e["from"] == args.id]
    in_edges = [e for e in data["edges"] if e["to"] == args.id]
    commits = [c for c in data["commits"] if node["kind"] == "decision" and args.id[4:] in c["ids"]]
    if args.json:
        print(json.dumps({"node": node, "out": out_edges, "in": in_edges, "commits": commits},
                         indent=1, ensure_ascii=False))
        return EXIT_OK
    print(json.dumps(node, indent=1, ensure_ascii=False))
    for label, rows, key in (("cites / links to", out_edges, "to"), ("cited by", in_edges, "from")):
        if rows:
            print(f"\n{label} ({len(rows)}):")
            for e in rows[: args.limit]:
                print(f"  {e['kind']:<14} {e[key]}")
    if commits:
        print(f"\ncommits citing it ({len(commits)}):")
        for c in commits[: args.limit]:
            print(f"  {c['d']} {c['h']} {c['s']}")
    return EXIT_OK


def cmd_stages(prof, args):
    answered = {}
    for a in read_answers(prof)["answers"]:
        answered[a["stage"]] = answered.get(a["stage"], 0) + 1
    have = {p.name.split("-", 1)[0] for p in chapter_files(prof)}
    for s in prof["stages"]:
        mark = "chapter written" if s["id"].zfill(2) in have else "no chapter yet"
        print(f"{s['id']:>2} {s['slug']:<12} {s['title']:<40} {answered.get(s['id'], 0)} answers, {mark}")
    return EXIT_OK


def main(argv=None):
    parser = argparse.ArgumentParser(prog="udgt.py", description="UI, Dataset & Gameplay Teardown")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add(name, func, game=False):
        p = sub.add_parser(name)
        p.add_argument("--profile", required=True, help="the teardown's profile.json")
        if game:
            p.add_argument("--game", help="the game checkout (default: UDGT_GAME, then the profile's game.paths)")
        p.add_argument("--limit", type=int, default=25)
        p.set_defaults(func=func)
        return p

    add("scan", cmd_scan, game=True)
    p = add("check", cmd_check, game=True)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--json", action="store_true")
    add("diff", cmd_diff, game=True)
    p = add("brief", cmd_brief)
    p.add_argument("stage")
    p.add_argument("--json", action="store_true")
    p = add("record", cmd_record)
    p.add_argument("stage")
    p.add_argument("--question", required=True)
    p.add_argument("--answer", required=True)
    p.add_argument("--asked-as", default="chat", choices=["chat", "file"])
    add("build", cmd_build, game=True)
    p = add("query", cmd_query)
    p.add_argument("words")
    p.add_argument("--kind")
    p.add_argument("--area")
    p.add_argument("--json", action="store_true")
    p = add("show", cmd_show)
    p.add_argument("id")
    p.add_argument("--json", action="store_true")
    add("stages", cmd_stages)
    args = parser.parse_args(argv)
    try:
        prof = profiles.load(args.profile)
        return args.func(prof, args)
    except (profiles.ProfileError, Usage) as err:
        print(f"udgt: {err}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
