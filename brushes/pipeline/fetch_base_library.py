"""Download Procreate's older default brush sets into library/official/.

    python brushes/pipeline/fetch_base_library.py list
    python brushes/pipeline/fetch_base_library.py fetch [--only S] [--delay N] [--accept-upstream] [--confirm]
    python brushes/pipeline/fetch_base_library.py verify

This is the only script in brushes/ that opens a network connection
(docs/CONTRACTS.md, section 0 and F11). What it will and will not do:

  - It reads the `official` block of library/sources.json: one host, one base
    address, and a list of files, each pinned by size and MD5. It never writes
    that file.
  - `fetch` is a dry run unless --confirm is given. A dry run reads the local
    files, prints the plan, and opens no connection.
  - Every request is an HTTPS GET to the one host the manifest names, and that
    host must be one of ALLOWED_HOSTS below: a manifest reached through
    --library or ROSW_BRUSHES_LIBRARY that names any other host is refused by
    `fetch` with exit 2, dry run or not, and no opener is ever built for it.
    (`list` and `verify` open no connection and still read such a manifest.)
    The opener has no handler for http, ftp or file addresses and uses no
    proxy, a redirect to any other address is refused, and the address a
    response says it came from is checked again.
  - A file is streamed to `<name>.brushset.part`, its size and MD5 are compared
    with the pins, and only then is it moved to
    library/official/<pack>/<slug>.brushset. A file already there that matches
    its pins is skipped without a request.
  - When the size, the MD5 or the server's ETag differs from the pins, the
    download is thrown away and reported as "upstream changed"; the run goes on
    with the other files and ends with exit 1. --accept-upstream keeps such a
    file and reports its real size and MD5, so the author can review it and
    update the manifest by hand.
  - It waits --delay seconds between requests (1 by default), retries three
    times (after 2, 4 and 8 seconds) on a server error or a broken connection,
    and never asks for a file larger than 200 MB.
  - One line per downloaded file is appended to library/official/fetch_log.jsonl:
    the address, the size, the MD5, the sha256 and the server's ETag and
    Last-Modified headers. The log holds no time taken from this machine's
    clock and no path outside the library.
  - `verify` hashes the local files again, with no connection.

A downloaded set is a file from a stranger. This script hashes and stores it
and never opens it.

Exit codes: 0 ok, 1 refused or failed, 2 usage or environment.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402
import identity  # noqa: E402

SOURCES_NAME = "sources.json"
SOURCES_SCHEMA = "rosw-brushes-sources/1"
OFFICIAL_DIR = "official"
LOG_NAME = "fetch_log.jsonl"
LOG_SCHEMA = "rosw-brushes-fetch/1"
SET_SUFFIX = ".brushset"
PART_SUFFIX = ".part"

FETCH_VERSION = "1"
USER_AGENT = f"rosw-brushes/{FETCH_VERSION} (+https://github.com/groot99-droid/Pipelines-Plugin)"
TIMEOUT_SECONDS = 60
RETRY_WAITS = (2, 4, 8)                      # seconds before the second, third and fourth attempt
DEFAULT_DELAY = 1.0                          # seconds between two requests
MAX_DOWNLOAD_BYTES = 200 * 1000 * 1000       # no single file is larger than this
CHUNK = 1024 * 1024
SPACE_MARGIN = 64 * 1024 * 1024

# A clone made without Git LFS holds a small pointer file where a set should be.
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"
LFS_POINTER_MAX = 1024
# GitHub refuses a plain blob over 100 MB; the repository's own limit is 95.
PLAIN_BLOB_LIMIT = 95 * 1000 * 1000

DRY_RUN_LINE = "DRY RUN   nothing is written without --confirm."

# The hosts a connection may be opened to (docs/CONTRACTS.md, section 0;
# spec.yaml runtime.network.hosts). The manifest says which host its files are
# on; this tuple says which hosts are believed. A test keeps the three equal.
ALLOWED_HOSTS = ("download-assets.procreate.art",)

_HOST = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+")
_MD5 = re.compile(r"[0-9a-f]{32}")
_URL_PATH = re.compile(r"[A-Za-z0-9._~%!$&'()*+,;=:@/-]+")


class ManifestError(Exception):
    """sources.json is missing or cannot be used. The command exits 2."""


class Refused(Exception):
    """A rule said no to one file. Never retried."""


class UpstreamChanged(Refused):
    """The server's file is not the one the manifest pins."""


class FetchFailed(Exception):
    """One file could not be downloaded."""


class _Retry(Exception):
    """A failure worth another attempt: a server error or a broken connection."""


class OfficialFile(NamedTuple):
    pack: str
    slug: str
    title: str
    url: str
    bytes: int | None
    md5: str | None

    @property
    def key(self):
        return f"{self.pack}/{self.slug}"

    @property
    def stored(self):
        """Where the file lives, as a POSIX path relative to the library."""
        return f"{OFFICIAL_DIR}/{self.pack}/{self.slug}{SET_SUFFIX}"


class Official(NamedTuple):
    host: str
    base: str
    files: tuple


class Local(NamedTuple):
    """What is on disk where one official file belongs."""

    state: str               # missing | ok | differs | unpinned | pointer
    detail: str
    size: int | None
    md5: str | None
    sha256: str | None


# ── the manifest ─────────────────────────────────────────────────────────────

def check_url(url, host):
    """Raise Refused unless `url` is an https address on exactly `host`."""
    try:
        parts = urllib.parse.urlsplit(url)
        port = parts.port
    except ValueError:
        raise Refused(f"not an address this script may open: {url!r}") from None
    if parts.scheme != "https":
        raise Refused(f"only https is allowed, not {url!r}")
    if parts.netloc != host or parts.hostname != host or port is not None or parts.username is not None:
        raise Refused(f"only the host {host} is allowed, not {url!r}")
    return url


def check_host(host):
    """Raise ManifestError unless `host` is one a connection may be opened to."""
    if host not in ALLOWED_HOSTS:
        raise ManifestError(f"official.host is {host!r}; this script opens a connection only to "
                            f"{', '.join(ALLOWED_HOSTS)}")
    return host


def load_official(library):
    """The `official` block of <library>/sources.json, checked. Reads only."""
    path = Path(library) / SOURCES_NAME
    try:
        manifest = json.loads(bc.read_text(path))
    except FileNotFoundError:
        raise ManifestError(f"there is no manifest at {path} (point --library at the folder "
                            "that holds sources.json)") from None
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ManifestError(f"{path} cannot be read as JSON: {exc}") from None
    if not isinstance(manifest, dict) or manifest.get("schema") != SOURCES_SCHEMA:
        raise ManifestError(f"{path} is not a {SOURCES_SCHEMA} manifest")
    block = manifest.get("official")
    if not isinstance(block, dict):
        raise ManifestError(f"{path} has no `official` block")
    host, base, entries = block.get("host"), block.get("base"), block.get("files")
    if not isinstance(host, str) or _HOST.fullmatch(host) is None:
        raise ManifestError(f"official.host must be a lower-case host name, not {host!r}")
    if not isinstance(base, str) or not base.startswith(f"https://{host}/") or not base.endswith("/"):
        raise ManifestError(f"official.base must start with https://{host}/ and end with a slash")
    if "?" in base or "#" in base or _URL_PATH.fullmatch(base[len("https://"):]) is None:
        raise ManifestError("official.base may hold only the characters of a plain address path")
    if not isinstance(entries, list):
        raise ManifestError("official.files must be a list")
    files, seen = [], set()
    for number, entry in enumerate(entries, start=1):
        where = f"official.files[{number}]"
        if not isinstance(entry, dict):
            raise ManifestError(f"{where} must be an object")
        pack, slug, rel = entry.get("pack"), entry.get("slug"), entry.get("path")
        if not identity.is_pack_id(pack) or not identity.is_set_slug(slug):
            raise ManifestError(f"{where}: pack and slug must be lower-case slugs (a pack id of at "
                                f"most {identity.PACK_ID_MAX} characters), not {pack!r} and {slug!r}")
        if (not isinstance(rel, str) or _URL_PATH.fullmatch(rel) is None or rel.startswith("/")
                or ":" in rel or any(part in ("", ".", "..") for part in rel.split("/"))):
            raise ManifestError(f"{where}: path must be a relative address path, not {rel!r}")
        size, md5 = entry.get("bytes"), entry.get("md5")
        if size is not None and (type(size) is not int or not 0 < size <= MAX_DOWNLOAD_BYTES):
            raise ManifestError(f"{where}: bytes must be a size up to {MAX_DOWNLOAD_BYTES:,}, or null")
        if md5 is not None and (not isinstance(md5, str) or _MD5.fullmatch(md5) is None):
            raise ManifestError(f"{where}: md5 must be 32 lower-case hex characters, or null")
        try:
            url = check_url(base + rel, host)
        except Refused as exc:
            raise ManifestError(f"{where}: {exc}") from None
        title = entry.get("title")
        item = OfficialFile(pack, slug, title if isinstance(title, str) else slug, url, size, md5)
        if item.key in seen:
            raise ManifestError(f"{where}: {item.key} is listed twice")
        seen.add(item.key)
        files.append(item)
    return Official(host, base, tuple(files))


def select(files, only):
    """The files whose `pack/slug` holds `only`; all of them when it is empty."""
    if not only:
        return list(files)
    wanted = only.lower()
    return [item for item in files if wanted in item.key]


# ── local files ──────────────────────────────────────────────────────────────

def is_lfs_pointer(path, size=None):
    size = path.stat().st_size if size is None else size
    if size > LFS_POINTER_MAX:
        return False
    with open(path, "rb") as handle:
        return handle.read(len(LFS_HEADER)) == LFS_HEADER


def hash_file(path):
    """(size, md5, sha256) of a file, read in pieces."""
    md5, sha256, size = hashlib.md5(usedforsecurity=False), hashlib.sha256(), 0
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(CHUNK)
            if not chunk:
                break
            size += len(chunk)
            md5.update(chunk)
            sha256.update(chunk)
    return size, md5.hexdigest(), sha256.hexdigest()


def pin_mismatch(item, size, md5):
    """Why a size and MD5 are not the pinned ones, or an empty string."""
    reasons = []
    if item.bytes is not None and size != item.bytes:
        reasons.append(f"size {size:,}, pinned {item.bytes:,}")
    if item.md5 is not None and md5 is not None and md5 != item.md5:
        reasons.append(f"md5 {md5}, pinned {item.md5}")
    return "; ".join(reasons)


def local_state(library, item, *, full=True):
    """What is on disk for one file. `full=False` compares the size only."""
    path = Path(library) / item.stored
    if not path.is_file():
        return Local("missing", "", None, None, None)
    size = path.stat().st_size
    if is_lfs_pointer(path, size):
        return Local("pointer", "a Git LFS pointer, not the file: run git lfs pull", size, None, None)
    md5 = sha256 = None
    if full:
        size, md5, sha256 = hash_file(path)
    reason = pin_mismatch(item, size, md5)
    if reason:
        return Local("differs", reason, size, md5, sha256)
    if item.bytes is None and item.md5 is None:
        return Local("unpinned", "no size or md5 is pinned, so it cannot be checked", size, md5, sha256)
    return Local("ok", "", size, md5, sha256)


def unexpected_files(library, files):
    """Files under official/ that the manifest does not account for."""
    folder = Path(library) / OFFICIAL_DIR
    if not folder.is_dir():
        return []
    expected = {item.stored for item in files} | {f"{OFFICIAL_DIR}/{LOG_NAME}"}
    found = []
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            stored = bc.stored_path(path, library)
            if stored not in expected:
                found.append(stored)
    return found


# ── the network ──────────────────────────────────────────────────────────────

class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    """Follows a redirect only to an https address on the one allowed host."""

    def __init__(self, host):
        self.host = host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl, self.host)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def make_opener(host):
    """An opener that can speak https and nothing else, and uses no proxy.
    ManifestError for a host outside ALLOWED_HOSTS: none is built for it."""
    check_host(host)
    opener = urllib.request.OpenerDirector()
    for handler in (urllib.request.UnknownHandler(), urllib.request.HTTPSHandler(),
                    urllib.request.HTTPDefaultErrorHandler(), SameHostRedirect(host),
                    urllib.request.HTTPErrorProcessor()):
        opener.add_handler(handler)
    return opener


def _header(response, name, limit=200):
    """A response header as plain printable ASCII, or None."""
    headers = getattr(response, "headers", None)
    value = headers.get(name) if headers is not None else None
    if value is None:
        return None
    text = "".join(ch for ch in str(value) if " " <= ch <= "~").strip()
    return text[:limit] or None


def _etag_md5(etag):
    """The MD5 an ETag states, when it is a plain one (no multipart suffix)."""
    if not etag:
        return None
    bare = etag[2:] if etag.startswith("W/") else etag
    bare = bare.strip('"').lower()
    return bare if _MD5.fullmatch(bare) else None


def _remove(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def download(item, dest, opener, host, *, accept_upstream=False):
    """One GET, streamed to `<dest>.part`, checked, then moved into place.

    Returns the log record. Raises UpstreamChanged or Refused (not retried),
    urllib.error.HTTPError, or _Retry.
    """
    check_url(item.url, host)
    request = urllib.request.Request(
        item.url, method="GET",
        headers={"User-Agent": USER_AGENT, "Accept": "*/*", "Accept-Encoding": "identity"})
    part = dest.with_name(dest.name + PART_SUFFIX)
    try:
        response = opener.open(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError:
        raise
    except (urllib.error.URLError, http.client.HTTPException, OSError) as exc:
        raise _Retry(f"no connection: {exc}") from None
    try:
        check_url(response.geturl(), host)
        status = getattr(response, "status", None)
        if status != 200:
            raise FetchFailed(f"the server answered {status}, not 200")
        etag, modified = _header(response, "ETag"), _header(response, "Last-Modified")
        length = _header(response, "Content-Length")
        length = int(length) if length is not None and length.isdigit() else None
        if length is not None and length > MAX_DOWNLOAD_BYTES:
            raise Refused(f"the server offers {length:,} bytes; nothing over "
                          f"{MAX_DOWNLOAD_BYTES:,} is downloaded")
        # What the headers already say, before a byte of the body is read.
        early = pin_mismatch(item, item.bytes if length is None else length, _etag_md5(etag))
        if early and not accept_upstream:
            raise UpstreamChanged(early)
        md5, sha256, size = hashlib.md5(usedforsecurity=False), hashlib.sha256(), 0
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(part, "wb") as out:
            while True:
                try:
                    chunk = response.read(CHUNK)
                except (http.client.HTTPException, OSError) as exc:
                    raise _Retry(f"the connection broke after {size:,} bytes: {exc}") from None
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_DOWNLOAD_BYTES:
                    raise Refused(f"the server sent more than {MAX_DOWNLOAD_BYTES:,} bytes")
                md5.update(chunk)
                sha256.update(chunk)
                out.write(chunk)
        if length is not None and size != length:
            raise _Retry(f"{size:,} bytes arrived of the {length:,} announced")
        if size == 0:
            raise FetchFailed("the server sent an empty file")
        late = pin_mismatch(item, size, md5.hexdigest())
        if late and not accept_upstream:
            raise UpstreamChanged(late)
        os.replace(part, dest)
    finally:
        response.close()
        _remove(part)
    if item.bytes is None and item.md5 is None:
        pins = "none"
    else:
        pins = "differ" if late else "match"
    return {"schema": LOG_SCHEMA, "pack": item.pack, "slug": item.slug, "file": item.stored,
            "url": item.url, "bytes": size, "md5": md5.hexdigest(), "sha256": sha256.hexdigest(),
            "etag": etag, "last_modified": modified, "pins": pins}


def fetch_one(item, dest, opener, host, *, accept_upstream, sleep, say):
    """download(), with the retries. Raises Refused or FetchFailed."""
    attempt = 0
    while True:
        try:
            return download(item, dest, opener, host, accept_upstream=accept_upstream)
        except urllib.error.HTTPError as exc:
            code, body = exc.code, getattr(exc, "fp", None)
            if body is not None:
                body.close()
            if not 500 <= code < 600:
                raise FetchFailed(f"the server answered {code}") from None
            problem = f"the server answered {code}"
        except _Retry as exc:
            problem = str(exc)
        if attempt >= len(RETRY_WAITS):
            raise FetchFailed(f"{problem} (gave up after {attempt + 1} attempts)")
        wait = RETRY_WAITS[attempt]
        attempt += 1
        say(f"            {problem}; trying again in {wait} s")
        sleep(wait)


def append_log(library, record):
    path = Path(library) / OFFICIAL_DIR / LOG_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(line)


# ── the verbs ────────────────────────────────────────────────────────────────

def _say(text=""):
    print(text)


def _row(item, word, note=""):
    size = "?" if item.bytes is None else f"{item.bytes:,}"
    line = f"  {word:<9} {item.key:<42} {size:>12}"
    return f"{line}  {note}" if note else line


def _heading(official, library, files):
    known = sum(item.bytes or 0 for item in files)
    _say(f"official sets   {len(files)} files, {known:,} bytes pinned")
    _say(f"host            {official.host} (https only)"
         + ("" if official.host in ALLOWED_HOSTS
            else "   NOT A HOST THIS SCRIPT MAY OPEN: `fetch` refuses this manifest"))
    _say(f"library         {Path(library) / OFFICIAL_DIR}")


def _large(sizes):
    """Lines naming every file too large for a plain git blob."""
    return [f"  over {PLAIN_BLOB_LIMIT // 1_000_000} MB   {stored}   {size:,} bytes (Git LFS only)"
            for stored, size in sizes if size > PLAIN_BLOB_LIMIT]


def run_list(library, official):
    """Print the manifest's files and whether each is here. Reads sizes only."""
    _heading(official, library, official.files)
    _say()
    counts = {}
    for item in official.files:
        local = local_state(library, item, full=False)
        word = {"ok": "present", "unpinned": "present"}.get(local.state, local.state)
        counts[word] = counts.get(word, 0) + 1
        _say(_row(item, word, f"md5 {item.md5 or '?'}  {item.title}"))
        if local.detail:
            _say(f"            {local.detail}")
    _say()
    _say("  " + ", ".join(f"{count} {word}" for word, count in sorted(counts.items()))
         + "   (sizes compared; `verify` checks the MD5 too)")
    return bc.EXIT_OK


def run_verify(library, official):
    """Hash every local file again and compare with the pins. No connection."""
    _heading(official, library, official.files)
    _say()
    counts, sizes, total = {}, [], 0
    for item in official.files:
        local = local_state(library, item)
        counts[local.state] = counts.get(local.state, 0) + 1
        if local.size is not None and local.state != "pointer":
            total += local.size
            sizes.append((item.stored, local.size))
        note = f"md5 {local.md5}" if local.md5 else ""
        _say(_row(item, local.state.upper() if local.state != "ok" else "ok", note))
        if local.detail:
            _say(f"            {local.detail}")
    extra = unexpected_files(library, official.files)
    for stored in extra:
        _say(f"  unexpected  {stored}   (not in the manifest)")
    for line in _large(sizes):
        _say(line)
    _say()
    present = len(sizes)
    _say(f"  {counts.get('ok', 0)} of {len(official.files)} files are present and match their pins; "
         f"{present} present, {total:,} bytes on disk")
    if counts.get("pointer"):
        print(f"error: {counts['pointer']} file(s) are Git LFS pointers. Run `git lfs pull`.",
              file=sys.stderr)
        return bc.EXIT_USAGE
    if counts.get("ok", 0) != len(official.files):
        _say("  NOT VERIFIED   " + ", ".join(f"{count} {state}" for state, count in sorted(counts.items())
                                              if state != "ok"))
        return bc.EXIT_REFUSED
    return bc.EXIT_OK


def run_fetch(library, official, *, only=None, delay=DEFAULT_DELAY, accept_upstream=False,
              confirm=False, opener=None, sleep=time.sleep, disk_free=None):
    """Plan, and with `confirm` download, the selected files.

    An `opener` is handed in only by the tests, which answer from a table and
    open no connection. Without one the real opener would be built, so the
    manifest's host must be an allowed one, for a dry run as for a real run.
    """
    if opener is None:
        try:
            check_host(official.host)
        except ManifestError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return bc.EXIT_USAGE
    files = select(official.files, only)
    if not files:
        print(f"error: --only {only!r} matches none of the {len(official.files)} files "
              "(it is compared with `pack/slug`; see `list`)", file=sys.stderr)
        return bc.EXIT_USAGE
    _heading(official, library, files)
    _say()
    todo, kept_sizes = [], []
    for item in files:
        local = local_state(library, item)
        if local.state == "pointer":
            print(f"error: {item.stored} is a Git LFS pointer, not the file. Run `git lfs pull`; "
                  "this script does not overwrite a pointer.", file=sys.stderr)
            return bc.EXIT_USAGE
        if local.state in ("ok", "unpinned"):
            kept_sizes.append((item.stored, local.size))
            _say(_row(item, "skip", "already here" + ("" if local.state == "ok" else "; " + local.detail)))
            continue
        todo.append(item)
        _say(_row(item, "download" if local.state == "missing" else "replace",
                  "" if local.state == "missing" else f"the local file differs ({local.detail})"))
        _say(f"            {item.url}")
        _say(f"            -> {item.stored}")
    need = sum(item.bytes or 0 for item in todo)
    _say()
    _say(f"  {len(todo)} to download ({need:,} bytes pinned), {len(files) - len(todo)} already here")
    if not confirm:
        _say()
        _say(DRY_RUN_LINE)
        return bc.EXIT_OK
    if not todo:
        return bc.EXIT_OK

    free = (disk_free or _disk_free)(library)
    if free < need + SPACE_MARGIN:
        print(f"error: {need:,} bytes are needed and only {free:,} are free under {library}",
              file=sys.stderr)
        return bc.EXIT_USAGE

    opener = opener or make_opener(official.host)
    failed, done, changed = [], [], []
    _say()
    for number, item in enumerate(todo):
        if number:
            sleep(delay)
        dest = Path(library) / item.stored
        try:
            record = fetch_one(item, dest, opener, official.host, accept_upstream=accept_upstream,
                               sleep=sleep, say=_say)
        except UpstreamChanged as exc:
            changed.append(item)
            _say(_row(item, "CHANGED", f"upstream changed: {exc}"))
            continue
        except (Refused, FetchFailed) as exc:
            failed.append(item)
            _say(_row(item, "FAILED", str(exc)))
            continue
        append_log(library, record)
        done.append(record)
        note = f"md5 {record['md5']}"
        if record["pins"] == "differ":
            note += "   ACCEPTED though it differs from the pins: update sources.json by hand"
        elif record["pins"] == "none":
            note += "   nothing was pinned: record this size and md5 in sources.json"
        _say(f"  {'fetched':<9} {item.key:<42} {record['bytes']:>12,}  {note}")

    got = sum(record["bytes"] for record in done)
    _say()
    _say(f"  {len(done)} downloaded ({got:,} bytes), {len(changed)} changed upstream, {len(failed)} failed")
    for line in _large(kept_sizes + [(record["file"], record["bytes"]) for record in done]):
        _say(line)
    if changed:
        _say("  upstream changed; review and update sources.json, or pass --accept-upstream "
             "to keep the new file")
    return bc.EXIT_REFUSED if failed or changed else bc.EXIT_OK


def _disk_free(folder):
    folder = Path(folder)
    while not folder.exists() and folder.parent != folder:
        folder = folder.parent
    return shutil.disk_usage(folder).free


# ── the command line ─────────────────────────────────────────────────────────

def _delay(text):
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a number of seconds") from None
    if not 0 <= value <= 3600:
        raise argparse.ArgumentTypeError("the delay is between 0 and 3600 seconds")
    return value


def _add_roots(parser, default):
    for name in ("root", "library"):
        parser.add_argument(bc.FLAGS[name], metavar="DIR", default=default, help=bc.FLAG_HELP[name])


def build_parser():
    parser = argparse.ArgumentParser(
        prog="fetch_base_library.py",
        description="Download Procreate's older default brush sets into library/official/. "
                    "`fetch` is a dry run without --confirm.")
    _add_roots(parser, None)
    verbs = parser.add_subparsers(dest="verb", metavar="{list,fetch,verify}", required=True)
    listing = verbs.add_parser("list", help="show the files the manifest names and which are here")
    fetch = verbs.add_parser("fetch", help="download what is missing (a dry run without --confirm)")
    fetch.add_argument("--only", metavar="S", default=None,
                       help="only the files whose pack/slug contains S")
    fetch.add_argument("--delay", metavar="N", type=_delay, default=DEFAULT_DELAY,
                       help=f"seconds to wait between two requests (default {DEFAULT_DELAY:g})")
    fetch.add_argument("--accept-upstream", action="store_true",
                       help="keep a file whose size or MD5 differs from the manifest's pins")
    fetch.add_argument("--confirm", action="store_true", help="really download and write")
    verify = verbs.add_parser("verify", help="hash the local files again; no connection")
    for sub in (listing, fetch, verify):
        _add_roots(sub, argparse.SUPPRESS)
    return parser


def main(argv=None, *, opener=None, sleep=None, disk_free=None):
    """`opener`, `sleep` and `disk_free` exist for the tests, which use no network."""
    bc.open_console()
    args = build_parser().parse_args(argv)
    library = bc.paths_from_args(args).library
    try:
        official = load_official(library)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return bc.EXIT_USAGE
    if args.verb == "list":
        return run_list(library, official)
    if args.verb == "verify":
        return run_verify(library, official)
    return run_fetch(library, official, only=args.only, delay=args.delay,
                     accept_upstream=args.accept_upstream, confirm=args.confirm,
                     opener=opener, sleep=sleep or time.sleep, disk_free=disk_free)


if __name__ == "__main__":
    raise SystemExit(main())
