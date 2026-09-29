#!/usr/bin/env python3
"""Self-contained TF-IDF search over the Creative-Writing vault.

Stdlib only -- no network calls, no embeddings, no Ollama dependency.
See CLAUDE.md ("Using tools/vault_search.py") for when/how this should be invoked.

Usage:
    python tools/vault_search.py index  [--vault PATH] [--out PATH] [--no-annotations]
    python tools/vault_search.py search "query" [--top 5] [--json] [--index PATH]
    python tools/vault_search.py ask    "query" [--top 5] [--json] [--index PATH]
"""
import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "so", "of", "in", "on", "at",
    "to", "for", "with", "without", "by", "from", "as", "is", "was", "were", "are", "be",
    "been", "being", "it", "its", "this", "that", "these", "those", "i", "you", "he", "she",
    "we", "they", "them", "his", "her", "their", "my", "your", "our", "not", "no", "do",
    "does", "did", "have", "has", "had", "will", "would", "can", "could", "should", "may",
    "might", "must", "there", "here", "what", "which", "who", "whom", "when", "where", "why",
    "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
    "only", "own", "same", "too", "very", "just", "about", "into", "over", "after", "before",
    "between", "up", "down", "out", "off", "again", "further", "once",
}

TOKEN_RE = re.compile(r"[A-Za-z']+")
HEADING_LINE_RE = re.compile(r"^#{1,6}\s+.+$")

NUMBERED_DIR_RE = re.compile(r"^\d{2}_")
# Craft notes (_Craft/): cross-cutting analysis of the works, not the author's own
# prose. Indexed as their own source type so a search result says what it is.
CRAFT_DIR_NAME = "_Craft"
EXCLUDE_FILENAMES = {"README.md", "OBSIDIAN.md", "CLAUDE.md", "CONVENTIONS.md"}
EXCLUDE_DIR_NAMES = {".git", ".obsidian", "tools"}

MIN_CHUNK_WORDS = 150
MAX_CHUNK_WORDS = 400

# Bumped only when chunk_body()'s algorithm itself changes -- lets a
# chunk-tag sidecar's staleness be checked without recomputing anything.
CHUNKER_VERSION = "v1"

TAG_FIELDS = ("plot_tags", "context_tags", "mood_tags", "motif_tags")
TAG_FIELD_ALIASES = {"plot": "plot_tags", "context": "context_tags",
                      "mood": "mood_tags", "motif": "motif_tags"}


# --------------------------------------------------------------------------
# Tokenization / TF-IDF
# --------------------------------------------------------------------------

def tokenize(text):
    return [t.lower() for t in TOKEN_RE.findall(text) if len(t) > 1 and t.lower() not in STOPWORDS]


# --------------------------------------------------------------------------
# Frontmatter parsing (small YAML subset: key: value / key: [a, b] / quoted strings)
# --------------------------------------------------------------------------

def split_frontmatter(text):
    if not (text.startswith("---\n") or text.startswith("---\r\n")):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_block = text[4:end]
    rest_start = text.find("\n", end + 1)
    body = text[rest_start + 1:] if rest_start != -1 else ""
    return parse_simple_yaml(fm_block), body


def parse_simple_yaml(block):
    fm = {}
    for line in block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()] if inner else []
            fm[key] = items
        else:
            fm[key] = val.strip('"').strip("'")
    return fm


# --------------------------------------------------------------------------
# Chunking
# --------------------------------------------------------------------------

def _split_paragraphs(body):
    lines = body.splitlines()
    paragraphs = []
    cur_lines, cur_start = [], None
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            if cur_lines:
                paragraphs.append((cur_start, i - 1, "\n".join(cur_lines)))
                cur_lines = []
            continue
        if not cur_lines:
            cur_start = i
        cur_lines.append(line)
    if cur_lines:
        paragraphs.append((cur_start, len(lines), "\n".join(cur_lines)))
    return paragraphs


def _looks_like_heading(stripped):
    if not stripped or "\n" in stripped:
        return False
    if HEADING_LINE_RE.match(stripped):
        return True
    words = stripped.split()
    if len(words) <= 8 and not stripped.endswith((".", ",", ";", ":", "!", "?")):
        if stripped[0].isupper() or stripped[0] in "*_\"'":
            return True
    return False


def chunk_body(body):
    paragraphs = _split_paragraphs(body)
    chunks = []
    buf_text, buf_start, buf_end, buf_words = [], None, None, 0
    current_heading = None

    def flush():
        nonlocal buf_text, buf_start, buf_end, buf_words
        if buf_text:
            joined = "\n\n".join(buf_text)
            chunks.append({
                "start_line": buf_start, "end_line": buf_end,
                "text": joined, "heading": current_heading,
            })
        buf_text, buf_start, buf_end, buf_words = [], None, None, 0

    for start, end, text in paragraphs:
        stripped = text.strip()
        if not stripped:
            continue
        word_count = len(stripped.split())
        if word_count <= 8 and _looks_like_heading(stripped) and buf_words >= 0:
            flush()
            current_heading = stripped.lstrip("#").strip(" *_\"'")
            continue
        if buf_start is None:
            buf_start = start
        buf_end = end
        buf_text.append(stripped)
        buf_words += word_count
        if buf_words >= MIN_CHUNK_WORDS:
            flush()
    flush()

    if not chunks and body.strip():
        chunks.append({"start_line": 1, "end_line": len(body.splitlines()) or 1,
                        "text": body.strip(), "heading": None})
    return chunks


def chunk_fingerprint(text, length=16):
    """Stable content hash for a chunk (or a whole body), tolerant of
    incidental line-wrap differences via the same whitespace-flattening
    make_preview() already does. Used to detect a stale chunk-tag sidecar
    without needing to touch any vault markdown file."""
    flat = " ".join(text.split())
    digest = hashlib.sha256(flat.encode("utf-8")).hexdigest()[:length]
    return f"sha256:{length}:{digest}"


# --------------------------------------------------------------------------
# Chunk-tag sidecars (_ChunkTags/) -- per-chunk plot/context/mood/motif
# tags, kept OUT of the vault's own markdown (the 63 originals' bodies are
# verbatim and untouched; frontmatter is file-level only, not per-chunk).
# See _ChunkTags/vocabulary.yaml for the closed tag vocabulary.
# --------------------------------------------------------------------------

def chunk_tags_sidecar_path(vault_root, rel_path):
    return vault_root / "_ChunkTags" / (rel_path + ".tags.json")


def load_chunk_tags(vault_root, rel_path):
    """Read a work's chunk-tag sidecar, or None if it doesn't exist / can't
    be parsed. Never raises -- a missing or broken sidecar just means the
    file's chunks stay untagged, exactly like before this feature existed."""
    path = chunk_tags_sidecar_path(vault_root, rel_path)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def match_sidecar_chunk(sidecar_chunks, position_index, fingerprint):
    """Find the sidecar chunk record for a freshly-chunked chunk at
    position_index (1-based), verified by content fingerprint. Tries the
    same position first (the common case when nothing has changed), then
    falls back to scanning all sidecar chunks by fingerprint (handles
    reordering). Returns None -- not a guess -- if nothing matches, so the
    caller can report a mismatch instead of silently misattaching tags."""
    if 0 <= position_index - 1 < len(sidecar_chunks):
        candidate = sidecar_chunks[position_index - 1]
        if candidate.get("content_fingerprint") == fingerprint:
            return candidate
    for candidate in sidecar_chunks:
        if candidate.get("content_fingerprint") == fingerprint:
            return candidate
    return None


# --------------------------------------------------------------------------
# File discovery
# --------------------------------------------------------------------------

def iter_source_files(vault_root, include_annotations=True):
    index_md = vault_root / "00_INDEX.md"
    if index_md.exists():
        yield index_md, "index"

    for entry in sorted(vault_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in EXCLUDE_DIR_NAMES or entry.name.startswith("."):
            continue
        if entry.name == "_Annotations":
            continue
        if NUMBERED_DIR_RE.match(entry.name):
            for path in sorted(entry.rglob("*.md")):
                yield path, ("moc" if path.name == "_index.md" else "work")

    if include_annotations:
        ann_dir = vault_root / "_Annotations"
        if ann_dir.exists():
            for path in sorted(ann_dir.rglob("*.md")):
                yield path, "annotation"

    craft_dir = vault_root / CRAFT_DIR_NAME
    if craft_dir.exists():
        for path in sorted(craft_dir.rglob("*.md")):
            yield path, "craft"


# --------------------------------------------------------------------------
# Index build
# --------------------------------------------------------------------------

def make_preview(text, length=200):
    flat = " ".join(text.split())
    return flat[:length] + ("..." if len(flat) > length else "")


def build_index(vault_root, include_annotations=True):
    chunks = []
    sidecar_cache = {}
    mismatch_count = 0
    mismatch_files = set()

    for path, source_type in iter_source_files(vault_root, include_annotations):
        if path.name in EXCLUDE_FILENAMES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        fm, body = split_frontmatter(text)
        rel = path.relative_to(vault_root).as_posix()

        meta_fields = {k: fm[k] for k in ("title", "type", "mode", "genre", "themes",
                                           "project", "archetypes") if fm.get(k)}
        if meta_fields:
            parts = []
            for k, v in meta_fields.items():
                v_str = ", ".join(v) if isinstance(v, list) else str(v)
                parts.append(f"{k}: {v_str}")
            meta_text = "\n".join(parts)
            chunks.append({
                "file": rel, "chunk_index": 0, "heading": "(frontmatter)",
                "start_line": 0, "end_line": 0, "text": meta_text,
                "source_type": source_type,
                **{k: [] for k in TAG_FIELDS},
            })

        # Chunk tags only apply to actual works -- annotations/MOCs/the
        # index aren't what reference_pull is trying to find more of.
        sidecar = None
        if source_type == "work":
            if rel not in sidecar_cache:
                sidecar_cache[rel] = load_chunk_tags(vault_root, rel)
            sidecar = sidecar_cache[rel]
        sidecar_chunks = sidecar.get("chunks", []) if sidecar else []

        for idx, c in enumerate(chunk_body(body), start=1):
            tag_lists = {k: [] for k in TAG_FIELDS}
            if sidecar_chunks:
                fp = chunk_fingerprint(c["text"])
                matched = match_sidecar_chunk(sidecar_chunks, idx, fp)
                if matched:
                    for k in TAG_FIELDS:
                        tag_lists[k] = matched.get(k, [])
                else:
                    mismatch_count += 1
                    mismatch_files.add(rel)
            chunks.append({
                "file": rel, "chunk_index": idx, "heading": c["heading"],
                "start_line": c["start_line"], "end_line": c["end_line"],
                "text": c["text"], "source_type": source_type,
                **tag_lists,
            })

    for i, c in enumerate(chunks):
        c["id"] = f"c_{i:04d}"
        c["preview"] = make_preview(c["text"])

    n_docs = len(chunks)
    df = Counter()
    tokenized = []
    for c in chunks:
        # Fold tag values into the vectorized text (not the preview, which
        # stays clean) so tagged vocabulary becomes lexically searchable
        # too, on top of the structured --tag filter added in search_index.
        tag_text = " ".join(t for k in TAG_FIELDS for t in c.get(k, []))
        toks = tokenize(c["text"] + (" " + tag_text if tag_text else ""))
        tokenized.append(toks)
        for t in set(toks):
            df[t] += 1

    idf = {t: math.log(n_docs / (1 + df[t])) + 1.0 for t in df}

    for c, toks in zip(chunks, tokenized):
        tf = Counter(toks)
        vec = {t: tf[t] * idf.get(t, 0.0) for t in tf}
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        c["vector"] = vec
        c["norm"] = norm
        del c["text"]

    files_seen = {c["file"] for c in chunks}
    index = {
        "vault": str(vault_root),
        "built": datetime.now(timezone.utc).isoformat(),
        "file_count": len(files_seen),
        "chunk_count": len(chunks),
        "vocab_size": len(idf),
        "idf": idf,
        "chunks": chunks,
        "_chunk_tag_mismatches": {"count": mismatch_count, "files": sorted(mismatch_files)},
    }
    return index


def cmd_index(args):
    vault_root = Path(args.vault).resolve() if args.vault else Path(__file__).resolve().parent.parent
    out_path = Path(args.out) if args.out else (Path(__file__).resolve().parent / "rag_index" / "index.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    index = build_index(vault_root, include_annotations=not args.no_annotations)
    mismatches = index.pop("_chunk_tag_mismatches", {"count": 0, "files": []})
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(index, f)

    print(f"Indexed {index['file_count']} files -> {index['chunk_count']} chunks, "
          f"{index['vocab_size']} vocab terms.")
    if mismatches["count"]:
        files_str = ", ".join(mismatches["files"])
        print(f"WARNING: {mismatches['count']} chunk-tag mismatches across "
              f"{len(mismatches['files'])} file(s) -- sidecars may be stale: {files_str}")
    print(f"Wrote {out_path}")


# --------------------------------------------------------------------------
# Search
# --------------------------------------------------------------------------

def load_index(index_path):
    if not index_path.exists():
        print(f"No index found at {index_path} -- run `index` first.", file=sys.stderr)
        sys.exit(1)
    with index_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _chunk_matches_tags(c, tag_filters):
    if not tag_filters:
        return True
    for field, value in tag_filters:
        key = TAG_FIELD_ALIASES.get(field, field)
        values = [v.lower() for v in c.get(key, [])]
        if value.lower() not in values:
            return False
    return True


def search_index(index, query, top=5, source_types=None, tag_filters=None):
    """tag_filters: list of (field, value) pairs, ANDed together, where
    field is one of plot/context/mood/motif (or the raw *_tags key name).
    query may be empty when tag_filters is given -- a pure tag lookup
    ("give me chunks tagged context=isolation") returns matching chunks
    with a fixed sentinel score instead of a cosine rank; when both are
    given, a chunk must match every tag filter AND rank by cosine."""
    toks = tokenize(query) if query else []
    if not toks and not tag_filters:
        return []

    idf = index["idf"]
    qvec, qnorm = {}, 1.0
    if toks:
        qtf = Counter(toks)
        qvec = {t: qtf[t] * idf.get(t, 0.0) for t in qtf}
        qnorm = math.sqrt(sum(w * w for w in qvec.values())) or 1.0

    scored = []
    for c in index["chunks"]:
        if source_types and c["source_type"] not in source_types:
            continue
        if not _chunk_matches_tags(c, tag_filters):
            continue
        if toks:
            vec = c["vector"]
            dot = sum(w * vec.get(t, 0.0) for t, w in qvec.items())
            if dot <= 0:
                continue
            score = dot / (qnorm * c["norm"])
            if score <= 0:
                continue
        else:
            score = 1.0
        scored.append((score, c))

    scored.sort(key=lambda pair: -pair[0])
    return scored[:top]


def _parse_tag_args(tag_specs):
    if not tag_specs:
        return None
    filters = []
    for spec in tag_specs:
        if "=" not in spec:
            print(f"Invalid --tag '{spec}' -- expected FIELD=VALUE, e.g. context=isolation", file=sys.stderr)
            sys.exit(1)
        field, _, value = spec.partition("=")
        filters.append((field.strip().lower(), value.strip()))
    return filters


def cmd_search(args):
    index_path = Path(args.index) if args.index else (Path(__file__).resolve().parent / "rag_index" / "index.json")
    index = load_index(index_path)
    tag_filters = _parse_tag_args(args.tag)
    results = search_index(index, args.query, top=args.top, tag_filters=tag_filters)

    if not results:
        if args.json:
            print(json.dumps([]))
        else:
            print("No results found.")
        return

    if args.json:
        out = [{
            "file": c["file"], "chunk_index": c["chunk_index"], "heading": c["heading"],
            "start_line": c["start_line"], "end_line": c["end_line"],
            "score": round(score, 4), "preview": c["preview"], "source_type": c["source_type"],
            **{k: c.get(k, []) for k in TAG_FIELDS},
        } for score, c in results]
        print(json.dumps(out, indent=2))
    else:
        for score, c in results:
            loc = f"lines {c['start_line']}-{c['end_line']}" if c["start_line"] else "frontmatter"
            heading = f" ({c['heading']})" if c["heading"] else ""
            print(f"[{score:.3f}] {c['file']}{heading}  {loc}  [{c['source_type']}]")
            print(f"    {c['preview']}")
            tag_bits = [f"{label}={','.join(c[key])}" for label, key in
                        (("plot", "plot_tags"), ("context", "context_tags"),
                         ("mood", "mood_tags"), ("motif", "motif_tags")) if c.get(key)]
            if tag_bits:
                print(f"    tags: {'  '.join(tag_bits)}")


def cmd_files(args):
    vault_root = Path(args.vault).resolve() if args.vault else Path(__file__).resolve().parent.parent
    out = []
    for path, source_type in iter_source_files(vault_root, include_annotations=not args.no_annotations):
        if path.name in EXCLUDE_FILENAMES:
            continue
        if args.type and source_type != args.type:
            continue
        out.append({"file": path.relative_to(vault_root).as_posix(), "source_type": source_type})

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for r in out:
            print(f"{r['file']}  [{r['source_type']}]")


def cmd_chunks(args):
    """Dump chunk boundaries + fingerprints for one file, using the exact
    same split_frontmatter()/chunk_body() the index build uses -- this is
    what the chunk-tagger subagent calls so its tags line up with the
    chunks build_index will actually produce."""
    vault_root = Path(args.vault).resolve() if args.vault else Path(__file__).resolve().parent.parent
    path = vault_root / args.path
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)
    text = path.read_text(encoding="utf-8")
    _, body = split_frontmatter(text)
    out_chunks = [{
        "chunk_index": idx, "heading": c["heading"],
        "start_line": c["start_line"], "end_line": c["end_line"],
        "text": c["text"], "content_fingerprint": chunk_fingerprint(c["text"]),
    } for idx, c in enumerate(chunk_body(body), start=1)]
    result = {"file": args.path, "body_fingerprint": chunk_fingerprint(body),
               "chunker_version": CHUNKER_VERSION, "chunks": out_chunks}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{args.path}  body_fingerprint={result['body_fingerprint']}  ({len(out_chunks)} chunks)")
        for c in out_chunks:
            print(f"  chunk {c['chunk_index']}: lines {c['start_line']}-{c['end_line']}  "
                  f"heading={c['heading']!r}  fp={c['content_fingerprint']}")


def build_arg_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="Build/rebuild the TF-IDF index.")
    p_index.add_argument("--vault", default=None, help="Vault root (default: parent of tools/).")
    p_index.add_argument("--out", default=None, help="Index output path (default: tools/rag_index/index.json).")
    p_index.add_argument("--no-annotations", action="store_true", help="Skip _Annotations/ during indexing.")
    p_index.set_defaults(func=cmd_index)

    for name in ("search", "ask"):
        p_search = sub.add_parser(name, help="Search the vault index.")
        p_search.add_argument("query", nargs="?", default="",
                               help="Lexical query. Optional if --tag is given.")
        p_search.add_argument("--top", type=int, default=5)
        p_search.add_argument("--json", action="store_true")
        p_search.add_argument("--index", default=None, help="Index path (default: tools/rag_index/index.json).")
        p_search.add_argument("--tag", action="append", default=None,
                               help="Filter to chunks tagged FIELD=VALUE (plot/context/mood/motif). "
                                    "Repeatable; multiple --tag flags are ANDed together.")
        p_search.set_defaults(func=cmd_search)

    p_files = sub.add_parser("files", help="List vault source files (for the chunk-tagger subagent).")
    p_files.add_argument("--vault", default=None, help="Vault root (default: parent of tools/).")
    p_files.add_argument("--type", default=None, choices=["index", "moc", "work", "annotation", "craft"])
    p_files.add_argument("--no-annotations", action="store_true")
    p_files.add_argument("--json", action="store_true")
    p_files.set_defaults(func=cmd_files)

    p_chunks = sub.add_parser("chunks", help="Show chunk boundaries + fingerprints for one file.")
    p_chunks.add_argument("path", help="Vault-relative path, e.g. 03_Stories/06_Melting_Away.md")
    p_chunks.add_argument("--vault", default=None, help="Vault root (default: parent of tools/).")
    p_chunks.add_argument("--json", action="store_true")
    p_chunks.set_defaults(func=cmd_chunks)

    return parser


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    parser = build_arg_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
