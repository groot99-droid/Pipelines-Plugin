"""The AI generations library: what the author made on Higgsfield, catalogued.

    python studio/library/library.py ingest <page.json>...   [--catalog FILE]
    python studio/library/library.py thumbs  [--force] [--workers N]
    python studio/library/library.py fetch   [--type T] [--id ID]... [--since YYYY-MM-DD] [--limit N] [--dry-run]
    python studio/library/library.py status

`ingest` reads pages saved from the Higgsfield connector's `show_generations`
({"items": [...], "next_cursor": ...}) and merges them into catalog.json by id,
newest first. It keeps the prompt, the model, the date, a short list of
settings, the ids of the inputs and the link to the original. It keeps no link
to an uploaded input (media_input): those are the author's own files, and the
catalog is versioned in a public repo. It prints how many items were new, so a
sync can stop at the first page that adds none.

`thumbs` makes thumbs/<id>.webp, 320 px wide, for every image and video, and
for a 3D model made from an image in the catalog (it reuses that image's
thumb). It needs ffmpeg on PATH; nothing else here does. Audio has none.

`fetch` downloads originals into files/<type>/<id>.<ext>. That folder is not
versioned: a 3D model is around 70 MB, and the whole library several GB. A
file already on disk is skipped; a download lands as .part and is renamed
only when complete.

The connector exists only inside a Claude Code session, so this script never
calls it. The higgsfield-library-sync skill pages the history and hands the
pages here.

Exit codes: 0 done, 1 some items failed, 2 usage error.
"""

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "catalog.json"
THUMBS = HERE / "thumbs"
FILES = HERE / "files"

EXIT_OK, EXIT_FAILED, EXIT_USAGE = 0, 1, 2
TYPES = ("image", "video", "audio", "3d")
THUMB_WIDTH = 320

# Settings worth reading back. Everything else in a job's params is either an
# input (recorded under `inputs`, by id) or the service's own plumbing.
KEPT_SETTINGS = (
    "aspect_ratio", "resolution", "quality", "width", "height", "duration", "seed",
    "mode", "style", "genre", "mood", "voice", "format", "geometry_quality",
    "texture_quality", "target_polycount", "pbr", "generate_audio", "sound",
)


class Usage(Exception):
    pass


def _iso(ts):
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _inputs(params):
    """The ids of what a job was made from. A job's own output keeps its id; an
    upload keeps its id and nothing else."""
    found = []
    for media in params.get("medias") or []:
        data = (media or {}).get("data") or {}
        if data.get("id"):
            found.append({"id": data["id"], "type": data.get("type", ""), "role": media.get("role", "")})
    for key in ("input_image", "input_image_end", "input_video", "input_video_end"):
        data = params.get(key)
        if isinstance(data, dict) and data.get("id"):
            found.append({"id": data["id"], "type": data.get("type", ""), "role": key})
    seen, out = set(), []
    for item in found:
        if item["id"] not in seen:
            seen.add(item["id"])
            out.append(item)
    return out


def normalize(item):
    """One catalog entry from one show_generations item."""
    kind = item.get("type")
    if kind not in TYPES:
        raise ValueError(f"unknown type {kind!r} on {item.get('id')}")
    params = item.get("params") or {}
    results = item.get("results") or {}
    raw = results.get("rawUrl") or ""
    entry = {
        "id": item["id"],
        "type": kind,
        "model": item.get("model") or params.get("model") or "",
        "created": _iso(item["createdAt"]),
        "prompt": (params.get("prompt") or "").strip(),
        "settings": {k: params[k] for k in KEPT_SETTINGS
                     if isinstance(params.get(k), (str, int, float, bool)) and params.get(k) != ""},
        "inputs": _inputs(params),
        "url": raw,
        "ext": raw.rsplit(".", 1)[-1].lower() if "." in raw.rsplit("/", 1)[-1] else "",
    }
    if results.get("minUrl"):
        entry["preview_url"] = results["minUrl"]
    if results.get("durationSec") is not None:
        entry["duration_sec"] = results["durationSec"]
    return entry


def load_catalog(path=CATALOG):
    if not path.exists():
        return {"source": "higgsfield", "items": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_catalog(catalog, path=CATALOG):
    catalog["items"].sort(key=lambda e: (e["created"], e["id"]), reverse=True)
    catalog["count"] = len(catalog["items"])
    catalog["counts"] = {t: sum(1 for e in catalog["items"] if e["type"] == t) for t in TYPES}
    catalog["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tmp = path.with_suffix(".json.part")
    tmp.write_text(json.dumps(catalog, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def ingest(pages, catalog_path=CATALOG):
    """Merge pages into the catalog. Returns (new, updated, skipped)."""
    catalog = load_catalog(catalog_path)
    by_id = {e["id"]: e for e in catalog["items"]}
    new = updated = skipped = 0
    for page in pages:
        data = json.loads(Path(page).read_text(encoding="utf-8"))
        items = data.get("items") if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise Usage(f"{page}: expected {{'items': [...]}} from show_generations")
        for item in items:
            if item.get("status", "completed") != "completed" or not (item.get("results") or {}).get("rawUrl"):
                skipped += 1
                continue
            entry = normalize(item)
            if entry["id"] not in by_id:
                new += 1
            elif by_id[entry["id"]] != entry:
                updated += 1
            by_id[entry["id"]] = entry
    catalog["items"] = list(by_id.values())
    save_catalog(catalog, catalog_path)
    return new, updated, skipped


def _thumb_source(entry, by_id):
    if entry["type"] == "image":
        return entry.get("preview_url") or entry["url"], False
    if entry["type"] == "video":
        return entry["url"], True
    if entry["type"] == "3d":
        for inp in entry["inputs"]:
            src = by_id.get(inp["id"])
            if src and src["type"] == "image":
                return src.get("preview_url") or src["url"], False
    return None, False


def _make_thumb(src, is_video, out):
    tmp = out.with_suffix(".part.webp")
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    if is_video:
        cmd += ["-ss", "0.5"]
    cmd += ["-i", src, "-frames:v", "1", "-vf", f"scale={THUMB_WIDTH}:-2",
            "-c:v", "libwebp", "-quality", "60", str(tmp)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0 or not tmp.exists():
        tmp.unlink(missing_ok=True)
        raise RuntimeError(proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "ffmpeg failed")
    tmp.replace(out)


def thumbs(force=False, workers=8):
    if not shutil.which("ffmpeg"):
        raise Usage("thumbs needs ffmpeg on PATH")
    catalog = load_catalog()
    by_id = {e["id"]: e for e in catalog["items"]}
    THUMBS.mkdir(exist_ok=True)
    jobs = []
    for entry in catalog["items"]:
        out = THUMBS / f"{entry['id']}.webp"
        src, is_video = _thumb_source(entry, by_id)
        if src and (force or not out.exists()):
            jobs.append((entry["id"], src, is_video, out))

    def run(job):
        ident, src, is_video, out = job
        try:
            _make_thumb(src, is_video, out)
            return ident, None
        except Exception as exc:  # one bad item never stops the rest
            return ident, str(exc)

    failed = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for ident, err in pool.map(run, jobs):
            if err:
                failed.append((ident, err))
    print(f"thumbs: {len(jobs) - len(failed)} made, {len(failed)} failed, "
          f"{len(catalog['items']) - len(jobs)} already present or not applicable")
    for ident, err in failed:
        print(f"  {ident}: {err}", file=sys.stderr)
    return failed


def local_path(entry, root=FILES):
    return root / entry["type"] / f"{entry['id']}.{entry['ext'] or 'bin'}"


def select(items, types=None, ids=None, since=None, limit=None):
    out = [e for e in items
           if (not types or e["type"] in types)
           and (not ids or e["id"] in ids)
           and (not since or e["created"] >= since)]
    return out[:limit] if limit else out


def _download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "rosw-studio-library"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(part, "wb") as fh:
        expected = resp.headers.get("Content-Length")
        shutil.copyfileobj(resp, fh, 1 << 20)
    if expected is not None and part.stat().st_size != int(expected):
        part.unlink(missing_ok=True)
        raise RuntimeError(f"short download ({part.name})")
    part.replace(dest)


def fetch(types=None, ids=None, since=None, limit=None, dry_run=False, workers=4):
    catalog = load_catalog()
    chosen = [e for e in select(catalog["items"], types, ids, since, limit) if not local_path(e).exists()]
    if dry_run:
        for e in chosen:
            print(f"{e['type']:5} {e['created'][:10]} {e['id']}  ->  {local_path(e).relative_to(HERE)}")
        print(f"fetch: {len(chosen)} to download (dry run, nothing written)")
        return []

    def run(e):
        try:
            _download(e["url"], local_path(e))
            return e["id"], None
        except Exception as exc:
            return e["id"], str(exc)

    failed = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for n, (ident, err) in enumerate(pool.map(run, chosen), 1):
            if err:
                failed.append((ident, err))
            if n % 25 == 0 or n == len(chosen):
                print(f"fetch: {n}/{len(chosen)}", flush=True)
    print(f"fetch: {len(chosen) - len(failed)} downloaded, {len(failed)} failed")
    for ident, err in failed:
        print(f"  {ident}: {err}", file=sys.stderr)
    return failed


def status():
    catalog = load_catalog()
    items = catalog["items"]
    print(f"catalog: {len(items)} items, updated {catalog.get('updated', 'never')}")
    for t in TYPES:
        of_type = [e for e in items if e["type"] == t]
        local = sum(1 for e in of_type if local_path(e).exists())
        thumbed = sum(1 for e in of_type if (THUMBS / f"{e['id']}.webp").exists())
        print(f"  {t:5}  {len(of_type):5} items  {thumbed:5} thumbs  {local:5} downloaded")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="library.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ingest")
    p.add_argument("pages", nargs="+")
    p.add_argument("--catalog", type=Path, default=CATALOG)
    p = sub.add_parser("thumbs")
    p.add_argument("--force", action="store_true")
    p.add_argument("--workers", type=int, default=8)
    p = sub.add_parser("fetch")
    p.add_argument("--type", action="append", choices=TYPES)
    p.add_argument("--id", action="append")
    p.add_argument("--since", help="YYYY-MM-DD")
    p.add_argument("--limit", type=int)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--workers", type=int, default=4)
    sub.add_parser("status")
    args = parser.parse_args(argv)
    try:
        if args.cmd == "ingest":
            new, updated, skipped = ingest(args.pages, args.catalog)
            print(f"ingest: {new} new, {updated} updated, {skipped} skipped")
            return EXIT_OK
        if args.cmd == "thumbs":
            return EXIT_FAILED if thumbs(args.force, args.workers) else EXIT_OK
        if args.cmd == "fetch":
            failed = fetch(args.type, set(args.id or []), args.since, args.limit, args.dry_run, args.workers)
            return EXIT_FAILED if failed else EXIT_OK
        status()
        return EXIT_OK
    except Usage as exc:
        print(f"library.py: {exc}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
