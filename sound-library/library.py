"""The sound library: the author's own sound effects, catalogued.

    python sound-library/library.py ingest <zip|dir>... [--category C] [--release TAG] [--replace]
    python sound-library/library.py ingest --from-release TAG [--category C] [--replace]
    python sound-library/library.py search "<query>" [--category C] [--loopable] [--max-seconds N] [--json]
    python sound-library/library.py show <id>
    python sound-library/library.py fetch [--id ID]... [--category C] [--query Q] [--from <zip|dir>]... [--release TAG] [--dry-run]
    python sound-library/library.py verify
    python sound-library/library.py status

`ingest` reads WAV files from zips or folders (or, with --from-release, from
every zip attached to that GitHub Release) and merges them into catalog.json:
one entry per file, with its name, category, duration, sample rate, channels,
bit depth, size, sha256, the tags its name yields, and where it came from (the
release tag, the asset and the member inside it). It copies each file into
files/<category>/<slug>.wav, which is not versioned. The category comes from
--category or from the zip's name (Motor_Bikes_Pt3.zip -> motor-bikes).

`search` ranks the catalog by the words of a query against each entry's name,
tags and category, and says which results are on disk.

`fetch` puts originals on disk. With --from it takes them from a local zip or
folder by content hash, without the network. Otherwise it downloads the asset
the entry records from that GitHub Release (a public repo needs no token),
extracts the member and checks its sha256. A download lands as .part and is
renamed only when complete.

The catalog is versioned and the repo is public: a name, a duration and a hash
become public when pushed. The originals never do. Exit codes: 0 done, 1 some
items failed, 2 usage error.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE / "catalog.json"
FILES = HERE / "files"
REPO = os.environ.get("SOUND_LIBRARY_REPO", "groot99-droid/Pipelines-Plugin")
API = "https://api.github.com"

EXIT_OK, EXIT_FAILED, EXIT_USAGE = 0, 1, 2
AUDIO_EXT = (".wav", ".aif", ".aiff", ".flac", ".mp3", ".ogg", ".m4a")
STOPWORDS = {"a", "an", "and", "the", "of", "in", "on", "to", "by", "with", "at", "loopable"}
UPLOAD_PREFIX = re.compile(r"^[0-9a-f]{8}-")
PART_SUFFIX = re.compile(r"[ _-]*(pt|part)[ _-]*\d+$", re.IGNORECASE)


class Usage(Exception):
    pass


# ── names ────────────────────────────────────────────────────────────────────

def slug(text):
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "untitled"


def asset_name(path):
    """The name a zip has on the author's machine: the harness prefixes an
    upload with eight hex digits and a dash."""
    return UPLOAD_PREFIX.sub("", Path(path).name)


def category_from(path):
    stem = Path(asset_name(path)).stem
    return slug(PART_SUFFIX.sub("", stem))


def display_name(member):
    return Path(member).stem.strip()


def tags_from(name):
    words = re.findall(r"[a-z0-9]+", name.lower())
    out = []
    for word in words:
        if word not in STOPWORDS and word not in out:
            out.append(word)
    return out


def is_loopable(name):
    return "loop" in name.lower()


# ── WAV ──────────────────────────────────────────────────────────────────────

def wav_info(data):
    """Channels, sample rate, bit depth and duration of a RIFF/WAVE file, read
    from its chunks. Anything that is not one gives None."""
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return None
    pos, fmt, data_len = 12, None, None
    while pos + 8 <= len(data):
        ident, size = data[pos:pos + 4], struct.unpack("<I", data[pos + 4:pos + 8])[0]
        body = pos + 8
        if ident == b"fmt " and size >= 16:
            tag, channels, rate, _, _, bits = struct.unpack("<HHIIHH", data[body:body + 16])
            fmt = {"format_tag": tag, "channels": channels, "sample_rate": rate, "bit_depth": bits}
        elif ident == b"data":
            data_len = min(size, len(data) - body)
        pos = body + size + (size & 1)
    if not fmt or data_len is None:
        return None
    frame = fmt["channels"] * fmt["bit_depth"] // 8
    seconds = data_len / (fmt["sample_rate"] * frame) if frame and fmt["sample_rate"] else 0.0
    return {"channels": fmt["channels"], "sample_rate": fmt["sample_rate"],
            "bit_depth": fmt["bit_depth"], "duration_s": round(seconds, 3)}


# ── catalog ──────────────────────────────────────────────────────────────────

def load(catalog=CATALOG):
    if not catalog.exists():
        return {"version": 1, "repo": REPO, "items": []}
    with catalog.open(encoding="utf-8") as handle:
        return json.load(handle)


def save(data, catalog=CATALOG):
    data["items"].sort(key=lambda e: e["id"])
    tmp = catalog.with_suffix(".json.part")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    tmp.replace(catalog)


def by_id(data):
    return {e["id"]: e for e in data["items"]}


def local_path(entry, files=FILES):
    return files / entry["file"]


def is_present(entry, files=FILES):
    return local_path(entry, files).exists()


# ── sources ──────────────────────────────────────────────────────────────────

def _members(source):
    """Every audio file in a zip or a folder: (member name, bytes, asset name).
    A zip's __MACOSX entries and ._ resource forks are skipped."""
    source = Path(source)
    if source.is_dir():
        for path in sorted(source.rglob("*")):
            if path.is_file() and path.suffix.lower() in AUDIO_EXT and not path.name.startswith("._"):
                yield str(path.relative_to(source)).replace(os.sep, "/"), path.read_bytes(), source.name
        return
    if not zipfile.is_zipfile(source):
        raise Usage(f"{source}: not a zip and not a folder")
    with zipfile.ZipFile(source) as archive:
        for info in sorted(archive.infolist(), key=lambda i: i.filename):
            name = info.filename
            if info.is_dir() or "__MACOSX" in name or Path(name).name.startswith("._"):
                continue
            if Path(name).suffix.lower() in AUDIO_EXT:
                yield name, archive.read(info), asset_name(source)


# ── ingest ───────────────────────────────────────────────────────────────────

def ingest(sources, category=None, release=None, replace=False, catalog=CATALOG, files=FILES, today=None):
    """Merge every audio file of the sources into the catalog and copy it into
    files/. Returns (new, same, replaced, refused)."""
    data = load(catalog)
    index = by_id(data)
    hashes = {e["sha256"]: e["id"] for e in data["items"]}
    added = (today or date.today()).isoformat()
    new = same = replaced = refused = 0
    for source in sources:
        cat = slug(category) if category else category_from(source)
        for member, blob, asset in _members(source):
            name = display_name(member)
            ident = f"{cat}/{slug(name)}"
            digest = hashlib.sha256(blob).hexdigest()
            info = wav_info(blob) or {}
            ext = Path(member).suffix.lower().lstrip(".")
            entry = {
                "id": ident, "name": name, "category": cat,
                "file": f"{cat}/{slug(name)}.{ext}", "format": ext,
                "bytes": len(blob), "sha256": digest,
                "duration_s": info.get("duration_s"), "sample_rate": info.get("sample_rate"),
                "channels": info.get("channels"), "bit_depth": info.get("bit_depth"),
                "loopable": is_loopable(name), "tags": tags_from(name),
                "source": {"release": release, "asset": asset, "member": member},
                "added": added,
            }
            if ident in index:
                old = index[ident]
                if old["sha256"] == digest:
                    same += 1
                    if release and not old["source"].get("release"):
                        old["source"] = entry["source"]
                    _place(blob, local_path(old, files))
                    continue
                if not replace:
                    print(f"refused {ident}: a different file has this id (use --replace)")
                    refused += 1
                    continue
                entry["added"] = old.get("added", added)
                data["items"] = [e for e in data["items"] if e["id"] != ident]
                replaced += 1
            else:
                new += 1
            if digest in hashes and hashes[digest] != ident:
                print(f"note {ident}: same content as {hashes[digest]}")
            hashes[digest] = ident
            data["items"].append(entry)
            index[ident] = entry
            _place(blob, local_path(entry, files))
    save(data, catalog)
    return new, same, replaced, refused


def _place(blob, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() == hashlib.sha256(blob).hexdigest():
        return
    part = dest.with_name(dest.name + ".part")
    part.write_bytes(blob)
    part.replace(dest)


# ── search ───────────────────────────────────────────────────────────────────

def search(query, category=None, loopable=None, max_seconds=None, catalog=CATALOG, files=FILES):
    """Entries ranked by how many words of the query they carry, then by name.
    An empty query lists everything the filters allow."""
    words = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if w not in STOPWORDS]
    out = []
    for entry in load(catalog)["items"]:
        if category and entry["category"] != slug(category):
            continue
        if loopable and not entry["loopable"]:
            continue
        if max_seconds is not None and (entry["duration_s"] or 0) > max_seconds:
            continue
        haystack = " ".join([entry["name"].lower(), entry["category"], " ".join(entry["tags"])])
        hay_words = set(re.findall(r"[a-z0-9]+", haystack))
        exact = sum(1 for w in words if w in hay_words)
        partial = sum(1 for w in words if w not in hay_words and w in haystack)
        score = exact * 2 + partial
        if words and score == 0:
            continue
        out.append((score, entry))
    out.sort(key=lambda t: (-t[0], t[1]["name"].lower()))
    return [dict(e, present=is_present(e, files)) for _, e in out]


def _fmt_seconds(seconds):
    return "?" if seconds is None else f"{seconds:6.1f}s"


def print_results(results):
    if not results:
        print("nothing matches")
        return
    for entry in results:
        flags = ("loop " if entry["loopable"] else "     ") + ("here" if entry["present"] else "    ")
        print(f"{entry['id']:<44} {_fmt_seconds(entry['duration_s'])}  {flags}  {entry['name']}")


# ── fetch ────────────────────────────────────────────────────────────────────

def _select(data, ids=None, category=None, query=None):
    chosen = data["items"]
    if ids:
        index = by_id(data)
        missing = [i for i in ids if i not in index]
        if missing:
            raise Usage("not in the catalog: " + ", ".join(missing))
        chosen = [index[i] for i in ids]
    if category:
        chosen = [e for e in chosen if e["category"] == slug(category)]
    if query:
        words = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if w not in STOPWORDS]
        chosen = [e for e in chosen
                  if any(w in " ".join([e["name"].lower(), e["category"], " ".join(e["tags"])]) for w in words)]
    return chosen


def fetch_from_local(sources, wanted, files=FILES):
    """Place every wanted entry whose content is in one of the sources."""
    by_hash = {e["sha256"]: e for e in wanted}
    placed = []
    for source in sources:
        for _, blob, _ in _members(source):
            entry = by_hash.get(hashlib.sha256(blob).hexdigest())
            if entry and not is_present(entry, files):
                _place(blob, local_path(entry, files))
                placed.append(entry["id"])
    return placed


def _get(url, dest=None, opener=None):
    request = urllib.request.Request(url, headers={"User-Agent": "rosw-sound-library",
                                                   "Accept": "application/octet-stream" if dest else "application/vnd.github+json"})
    open_ = opener or urllib.request.urlopen
    with open_(request, timeout=120) as response:
        if dest is None:
            return json.loads(response.read().decode("utf-8"))
        dest.parent.mkdir(parents=True, exist_ok=True)
        part = dest.with_name(dest.name + ".part")
        with part.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        part.replace(dest)
        return dest


def release_assets(tag, repo=REPO, opener=None):
    """asset name -> download url, for one release of the repo."""
    info = _get(f"{API}/repos/{repo}/releases/tags/{tag}", opener=opener)
    return {a["name"]: a["browser_download_url"] for a in info.get("assets", [])}


def download_release(tag, dest, repo=REPO, opener=None):
    """Every zip attached to a release, downloaded into dest. Returns the paths."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, url in sorted(release_assets(tag, repo, opener).items()):
        if not name.lower().endswith(".zip"):
            continue
        path = dest / name
        if not path.exists():
            _get(url, path, opener)
        paths.append(path)
    if not paths:
        raise Usage(f"release {tag} of {repo} has no zip attached")
    return paths


def fetch_from_release(wanted, release=None, repo=REPO, files=FILES, opener=None, cache=None):
    """Download each wanted entry's asset from its release and extract the
    member. Returns (placed ids, failures as (id, reason))."""
    placed, failed = [], []
    cache = Path(cache) if cache else Path(tempfile.mkdtemp(prefix="sound-library-"))
    assets_by_tag = {}
    for entry in wanted:
        if is_present(entry, files):
            continue
        src = entry["source"]
        tag = release or src.get("release")
        if not tag:
            failed.append((entry["id"], "no release recorded; pass --release TAG or use --from"))
            continue
        try:
            if tag not in assets_by_tag:
                assets_by_tag[tag] = release_assets(tag, repo, opener)
            url = assets_by_tag[tag].get(src["asset"])
            if not url:
                failed.append((entry["id"], f"release {tag} has no asset {src['asset']}"))
                continue
            zip_path = cache / f"{tag}--{src['asset']}"
            if not zip_path.exists():
                _get(url, zip_path, opener)
            blob = _member_from_zip(zip_path, src["member"], entry["sha256"])
            if blob is None:
                failed.append((entry["id"], f"{src['asset']} holds no file with sha256 {entry['sha256'][:12]}"))
                continue
            _place(blob, local_path(entry, files))
            placed.append(entry["id"])
        except Exception as err:  # noqa: BLE001 - one failure must not stop the rest
            failed.append((entry["id"], str(err)))
    return placed, failed


def _member_from_zip(zip_path, member, sha256):
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        order = ([member] if member in names else []) + [n for n in names if n != member]
        for name in order:
            if Path(name).suffix.lower() not in AUDIO_EXT or "__MACOSX" in name:
                continue
            blob = archive.read(name)
            if hashlib.sha256(blob).hexdigest() == sha256:
                return blob
    return None


# ── verify, status ───────────────────────────────────────────────────────────

def verify(catalog=CATALOG, files=FILES):
    """Problems with the catalog or the files on disk, as strings."""
    data = load(catalog)
    problems, seen, hashes = [], set(), {}
    for entry in data["items"]:
        for key in ("id", "name", "category", "file", "sha256", "source", "tags"):
            if key not in entry:
                problems.append(f"{entry.get('id', '?')}: missing {key}")
        ident = entry.get("id", "")
        if ident in seen:
            problems.append(f"{ident}: duplicate id")
        seen.add(ident)
        if ident != f"{entry.get('category')}/{slug(entry.get('name', ''))}":
            problems.append(f"{ident}: id does not match category and name")
        if not str(entry.get("file", "")).startswith(entry.get("category", "") + "/"):
            problems.append(f"{ident}: file is outside its category folder")
        digest = entry.get("sha256", "")
        if digest in hashes:
            problems.append(f"{ident}: same content as {hashes[digest]}")
        hashes.setdefault(digest, ident)
        path = local_path(entry, files)
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            problems.append(f"{ident}: the file on disk does not match the catalog")
    return problems


def status(catalog=CATALOG, files=FILES):
    data = load(catalog)
    rows = {}
    for entry in data["items"]:
        row = rows.setdefault(entry["category"], {"items": 0, "here": 0, "seconds": 0.0, "bytes": 0})
        row["items"] += 1
        row["here"] += int(is_present(entry, files))
        row["seconds"] += entry.get("duration_s") or 0
        row["bytes"] += entry.get("bytes") or 0
    return rows


def print_status(rows):
    if not rows:
        print("the catalog is empty")
        return
    print(f"{'category':<16} {'items':>5} {'on disk':>7} {'minutes':>8} {'MB':>7}")
    tot = {"items": 0, "here": 0, "seconds": 0.0, "bytes": 0}
    for cat, row in sorted(rows.items()):
        print(f"{cat:<16} {row['items']:>5} {row['here']:>7} {row['seconds'] / 60:>8.1f} {row['bytes'] / 1e6:>7.1f}")
        for key in tot:
            tot[key] += row[key]
    print(f"{'total':<16} {tot['items']:>5} {tot['here']:>7} {tot['seconds'] / 60:>8.1f} {tot['bytes'] / 1e6:>7.1f}")


# ── main ─────────────────────────────────────────────────────────────────────

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ingest", help="add the audio files of zips or folders to the catalog")
    p.add_argument("sources", nargs="*")
    p.add_argument("--category", help="override the category the zip's name gives")
    p.add_argument("--release", help="the GitHub Release tag the zips are (or will be) attached to")
    p.add_argument("--from-release", metavar="TAG", help="download every zip attached to this release and ingest them")
    p.add_argument("--replace", action="store_true", help="let a different file take an existing id")

    p = sub.add_parser("search", help="rank the catalog against a query")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--category")
    p.add_argument("--loopable", action="store_true")
    p.add_argument("--max-seconds", type=float)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("show", help="one entry, as JSON")
    p.add_argument("id")

    p = sub.add_parser("fetch", help="put originals on disk")
    p.add_argument("--id", action="append", dest="ids")
    p.add_argument("--category")
    p.add_argument("--query")
    p.add_argument("--from", action="append", dest="sources", metavar="ZIP_OR_DIR",
                   help="take the files from a local zip or folder instead of the network")
    p.add_argument("--release", help="read the assets of this release tag instead of the recorded one")
    p.add_argument("--dry-run", action="store_true")

    sub.add_parser("verify", help="check the catalog and the files on disk")
    sub.add_parser("status", help="counts by category")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "ingest":
            sources, release = args.sources, args.release
            if args.from_release:
                if sources or (release and release != args.from_release):
                    raise Usage("--from-release takes no sources and no other --release")
                release = args.from_release
                sources = download_release(release, Path(tempfile.mkdtemp(prefix="sound-library-")))
                print(f"downloaded {len(sources)} zip(s) from release {release}")
            elif not sources:
                raise Usage("give zips or folders, or --from-release TAG")
            new, same, replaced, refused = ingest(sources, args.category, release, args.replace)
            print(f"{new} new, {same} already there, {replaced} replaced, {refused} refused")
            return EXIT_FAILED if refused else EXIT_OK
        if args.cmd == "search":
            results = search(args.query, args.category, args.loopable, args.max_seconds)
            if args.json:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print_results(results)
            return EXIT_OK
        if args.cmd == "show":
            entry = by_id(load()).get(args.id)
            if not entry:
                raise Usage(f"not in the catalog: {args.id}")
            print(json.dumps(dict(entry, present=is_present(entry), path=str(local_path(entry))), indent=2))
            return EXIT_OK
        if args.cmd == "fetch":
            data = load()
            wanted = _select(data, args.ids, args.category, args.query)
            todo = [e for e in wanted if not is_present(e)]
            if args.dry_run:
                for entry in todo:
                    print(f"would fetch {entry['id']}  ({entry['bytes'] / 1e6:.1f} MB from {entry['source']['asset']})")
                print(f"{len(todo)} to fetch, {len(wanted) - len(todo)} already here")
                return EXIT_OK
            if args.sources:
                placed = fetch_from_local(args.sources, todo)
                left = [e for e in todo if e["id"] not in placed]
                print(f"{len(placed)} placed from local files, {len(left)} not found in them")
                return EXIT_FAILED if left else EXIT_OK
            placed, failed = fetch_from_release(todo, args.release)
            for ident, reason in failed:
                print(f"failed {ident}: {reason}")
            print(f"{len(placed)} fetched, {len(failed)} failed, {len(wanted) - len(todo)} already here")
            return EXIT_FAILED if failed else EXIT_OK
        if args.cmd == "verify":
            problems = verify()
            for line in problems:
                print(line)
            print("ok" if not problems else f"{len(problems)} problem(s)")
            return EXIT_FAILED if problems else EXIT_OK
        if args.cmd == "status":
            print_status(status())
            return EXIT_OK
    except Usage as err:
        print(f"usage: {err}", file=sys.stderr)
        return EXIT_USAGE
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
