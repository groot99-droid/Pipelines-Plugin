"""Index and search of the studio vault. Standard library only.

    python studio/vault/tools/vault_index.py rows                      # every note, one row each, as JSON
    python studio/vault/tools/vault_index.py index [--out PATH]        # build the search index
    python studio/vault/tools/vault_index.py search "<query>" [--top 5] [--kind K] [--status S]

A row holds what a desk needs to list a note: its frontmatter, its Overview,
how many Next Steps are open and the first one. It never holds the note's
body. The index adds one TF-IDF vector per section and a short preview, so a
search names the note and the section without the index carrying the text.

The index is written to rag_index/index.json beside this script, which git
ignores: it records a machine-local vault path. The vault is resolved from
this script's location, or from STUDIO_VAULT_DIR, so it runs from anywhere.

The rules for what counts as a note are studio_common's, so this reads exactly
the notes the pipeline writes.
"""

import argparse
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent.parent / "pipeline"
sys.path.insert(0, str(PIPELINE))

import studio_common  # noqa: E402
from studio_common import Env, Usage, read_text, sections, split_note, warn  # noqa: E402

DEFAULT_INDEX = HERE / "rag_index" / "index.json"
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*|\d+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have", "in", "is",
    "it", "its", "of", "on", "or", "that", "the", "this", "to", "was", "were", "with", "not",
    "no", "but", "so", "if", "then", "than", "into", "over", "under", "one", "two", "each",
    "every", "any", "all", "when", "where", "which", "who", "what", "how", "why", "will",
    "can", "may", "must", "never", "always", "here", "there", "they", "them", "their", "we",
    "our", "you", "your", "i", "me", "my",
}
MAX_CHUNK_WORDS = 300
PREVIEW_CHARS = 200
OVERVIEW_CHARS = 400
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|([^\]]*))?\]\]")
OPEN_BOX_RE = re.compile(r"^\s*[-*+] \[ \] ?(.*)$")


def tokenize(text):
    return [t.lower() for t in TOKEN_RE.findall(text) if len(t) > 1 and t.lower() not in STOPWORDS]


def plain(text):
    """Text as a reader sees it: wikilinks shown by their alias or name,
    emphasis marks and inline code marks dropped."""
    text = WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1), text)
    return re.sub(r"[*_`]", "", text)


def as_list(value):
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def as_text(value):
    return "" if value is None else str(value)


def project_name(value):
    """`[[Project Aurora]]` -> `Project Aurora`; a bare string as it is."""
    text = as_text(value).strip()
    match = WIKILINK_RE.fullmatch(text)
    return (match.group(2) or match.group(1)).strip() if match else text


def note_row(env, path):
    """One note as a row, or None when the file is not a Content MD."""
    text = read_text(path)
    front = studio_common.front_matter(text)
    if front.get("type") != env.spec["content_md"]["type"]:
        return None
    _, body = split_note(text)
    parts = dict(sections(body))
    overview = " ".join(plain(parts.get("Overview", "")).split())
    if len(overview) > OVERVIEW_CHARS:
        overview = overview[:OVERVIEW_CHARS].rsplit(" ", 1)[0] + "…"
    open_steps = [m.group(1).strip() for line in parts.get("Next Steps", "").splitlines()
                  for m in [OPEN_BOX_RE.match(line)] if m]
    return {
        "path": path.relative_to(env.vault).as_posix(),
        "id": as_text(front.get("id")),
        "title": as_text(front.get("title")) or path.stem,
        "kind": as_text(front.get("kind")),
        "status": as_text(front.get("status")),
        "project": project_name(front.get("project")),
        "created": as_text(front.get("created")),
        "updated": as_text(front.get("updated")),
        "pipelines": as_list(front.get("pipelines")),
        "context_brand": as_list(front.get("context_brand")),
        "tags": as_list(front.get("tags")),
        "overview": overview,
        "next_steps_open": len(open_steps),
        "first_step": plain(open_steps[0]) if open_steps else "",
    }


def note_rows(env):
    """Every Content MD in the vault as a row, newest update first. A file
    that is not UTF-8 is skipped, and said so on stderr."""
    rows = []
    for path in studio_common.vault_notes(env):
        try:
            row = note_row(env, path)
        except Usage as problem:
            warn(f"skipped: {problem}")
            continue
        if row:
            rows.append(row)
    rows.sort(key=lambda r: (r["updated"] or r["created"], r["title"]), reverse=True)
    return rows


def chunk_sections(body):
    """(heading, text) pieces of a note's body, a long section split at
    paragraph boundaries so no piece runs past MAX_CHUNK_WORDS."""
    pieces = []
    for title, text in sections(body):
        words, current, count = [], [], 0
        for paragraph in re.split(r"\n\s*\n", text):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            length = len(paragraph.split())
            if current and count + length > MAX_CHUNK_WORDS:
                pieces.append((title, "\n\n".join(current)))
                current, count = [], 0
            current.append(paragraph)
            count += length
        if current:
            pieces.append((title, "\n\n".join(current)))
        del words
    return pieces


def build_index(env):
    """The search index: the rows, one vector per section piece, and the idf."""
    rows = note_rows(env)
    by_path = {row["path"]: row for row in rows}
    raw_chunks = []
    for path in studio_common.vault_notes(env):
        relative = path.relative_to(env.vault).as_posix()
        if relative not in by_path:
            continue
        try:
            text = read_text(path)
        except Usage:
            continue
        _, body = split_note(text)
        for heading, piece in chunk_sections(body):
            tokens = tokenize(plain(piece))
            if not tokens:
                continue
            preview = " ".join(plain(piece).split())
            if len(preview) > PREVIEW_CHARS:
                preview = preview[:PREVIEW_CHARS].rsplit(" ", 1)[0] + "…"
            raw_chunks.append({"path": relative, "title": by_path[relative]["title"],
                               "heading": heading, "preview": preview, "tokens": tokens})
    total = len(raw_chunks) or 1
    document_frequency = Counter()
    for chunk in raw_chunks:
        document_frequency.update(set(chunk["tokens"]))
    idf = {term: math.log((1 + total) / (1 + df)) + 1.0 for term, df in document_frequency.items()}
    chunks = []
    for chunk in raw_chunks:
        counts = Counter(chunk.pop("tokens"))
        vector = {term: count * idf[term] for term, count in counts.items()}
        norm = math.sqrt(sum(weight * weight for weight in vector.values())) or 1.0
        chunk["vector"] = {term: round(weight, 4) for term, weight in vector.items()}
        chunk["norm"] = round(norm, 4)
        chunks.append(chunk)
    return {
        "vault": str(env.vault),
        "built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "notes": rows,
        "idf": {term: round(value, 4) for term, value in idf.items()},
        "chunks": chunks,
    }


def search_index(index, query, top=5, kind=None, status=None):
    """Cosine similarity over the section vectors, best first, as
    (score, chunk) pairs. `kind` and `status` narrow to notes that match."""
    tokens = tokenize(query)
    if not tokens:
        return []
    idf = index["idf"]
    counts = Counter(tokens)
    qvec = {term: count * idf.get(term, 0.0) for term, count in counts.items()}
    qnorm = math.sqrt(sum(w * w for w in qvec.values())) or 1.0
    allowed = None
    if kind or status:
        allowed = {row["path"] for row in index["notes"]
                   if (not kind or row["kind"] == kind) and (not status or row["status"] == status)}
    scored = []
    for chunk in index["chunks"]:
        if allowed is not None and chunk["path"] not in allowed:
            continue
        vector = chunk["vector"]
        dot = sum(weight * vector.get(term, 0.0) for term, weight in qvec.items())
        if dot <= 0:
            continue
        scored.append((dot / (qnorm * chunk["norm"]), chunk))
    scored.sort(key=lambda pair: -pair[0])
    return scored[:top]


def load_index(path):
    path = Path(path)
    if not path.is_file():
        raise Usage(f"no index at {path}. Run: python {Path(__file__).name} index")
    return json.loads(read_text(path))


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_rows(env, args):
    print(json.dumps(note_rows(env), indent=2, ensure_ascii=False))
    return 0


def cmd_index(env, args):
    out = Path(args.out) if args.out else DEFAULT_INDEX
    index = build_index(env)
    studio_common.write_text(out, json.dumps(index, ensure_ascii=False) + "\n")
    print(f"vault     {env.vault}")
    print(f"notes     {len(index['notes'])}")
    print(f"sections  {len(index['chunks'])}")
    print(f"wrote     {out}")
    return 0


def cmd_search(env, args):
    index = load_index(args.index or DEFAULT_INDEX)
    hits = search_index(index, args.query, top=args.top, kind=args.kind, status=args.status)
    if args.json:
        print(json.dumps([{"score": round(score, 4), **chunk_public(chunk)} for score, chunk in hits],
                         indent=2, ensure_ascii=False))
        return 0
    if not hits:
        print("no match")
        return 0
    for score, chunk in hits:
        print(f"{score:.3f}  {chunk['path']}  ·  {chunk['heading']}")
        print(f"       {chunk['preview']}")
    return 0


def chunk_public(chunk):
    return {key: chunk[key] for key in ("path", "title", "heading", "preview")}


def build_parser():
    parser = argparse.ArgumentParser(prog="vault_index.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", default=str(studio_common.SPEC_PATH), help="the spec to read")
    parser.add_argument("--runs-dir", help="where runs are kept (default: from the spec)")
    parser.add_argument("--vault-dir", help="the vault (default: from the spec)")
    parser.add_argument("--context-dir", help="the brand gates (default: from the spec)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("rows", help="every note as a row, as JSON")
    p_index = sub.add_parser("index", help="build the search index")
    p_index.add_argument("--out", default=None)
    p_search = sub.add_parser("search", help="search the index")
    p_search.add_argument("query")
    p_search.add_argument("--top", type=int, default=5)
    p_search.add_argument("--kind", default=None)
    p_search.add_argument("--status", default=None)
    p_search.add_argument("--index", default=None)
    p_search.add_argument("--json", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        env = Env(args.spec, args.runs_dir, args.vault_dir, args.context_dir)
        return {"rows": cmd_rows, "index": cmd_index, "search": cmd_search}[args.command](env, args)
    except Usage as problem:
        print(f"error     {problem}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
