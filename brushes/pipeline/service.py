"""The one layer both servers stand on (brushes/docs/CONTRACTS.md, F10).

`BrushService` answers search, similar, facets, the vocabulary, sets, one
brush, a stored preview, the settings schema, a patch check, an import, the
opening of a library original and an export. The MCP tools (mcp_server.py),
the HTTP routes (app_server.py) and any `--json` output return what these
methods return, so a shape is decided once, here.

    service = BrushService(bc.resolve_paths())
    service.search("watercolour wash", top=8)
    service.build_export({"format": "brush", "brushes": [{"base": {"library_id": "b_..."}}]})

What this module does not do
    It never writes into library/, catalog/ or vault/. The one function that
    puts a file on disk is `write_export` (F12), and it is reachable only
    when the service was made with an export folder; the HTTP server has none.
    It never builds a path from a client's text: a client names a brush by
    its id, which is matched against the catalog and only then used, and a
    path read from the catalog (a container, a preview) is checked to lie
    inside its root before it is opened.

Index states (F10): `fresh`, `stale` (served, and flagged), `memory` (no index
file: built in RAM, nothing written) and `not_ingested` (no catalog: the data
calls refuse with a hint that lists the commands in order). A service never
raises because data is missing; it says so.

Errors are `ApiError(code, message, status, hint, data)`.

Standard library only. Not a command (it has no main).
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import importlib.util
import json
import os
import re
import sys
import threading
import time
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_common as bc  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import gbr  # noqa: E402
import identity  # noqa: E402
import png_io  # noqa: E402
import zip_writer  # noqa: E402
from bplist import CodecError, ContainerError, LimitExceeded  # noqa: E402

SERVER_NAME = "rosw-brushes"
SERVER_VERSION = "0.2.0"

MIB = 1024 * 1024
MAX_UPLOAD = container.CAPS["upload_bytes"]          # 512 MiB: the largest local set is 334 MB
MAX_EXPORT_JSON = 128 * MIB
MAX_PATCH_JSON = 1 * MIB
MCP_TOP_MAX = 25
HTTP_TOP_MAX = 200
MAX_OFFSET = 100_000
PREVIEW_KINDS = ("stroke", "shape", "grain")
PREVIEW_MAX_BYTES = 512 * 1024
INCLUDE_PARTS = ("settings", "tags", "facets", "visual", "textures", "note")
DEFAULT_INCLUDE = ("tags", "facets", "visual", "textures", "note")
TEXTURE_MODES = ("full", "preview", "none")
EXPORT_FORMATS = ("brush", "brushset", "gbr", "kit")
MAX_EXPORT_BRUSHES = 200
MAX_CHANGES = 400
MAX_BASE_MEMBERS = 5000
MAX_KIT_FILES = 64
MAX_NAME = 120
PREVIEW_TILE = 256
LIBRARY_HALVES = ("user", "official")
INDEX_STATES = ("fresh", "stale", "memory", "not_ingested")     # docs/CONTRACTS.md, F10
MODES = ("project", "snapshot")

TAG_FILTER = re.compile(r"^[a-z][a-z_]*=[a-z0-9][a-z0-9,-]*$")     # F9
UUID_NAME = re.compile(r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$")
BUNDLED_NAME = re.compile(r"^[^\x00-\x1f/\\]{1,120}$")
KIT_ENTRY = re.compile(r"^(?:gimp/[A-Za-z0-9._ -]{1,64}\.gbr|(?:ink|mask)/[A-Za-z0-9._ -]{1,64}\.png"
                       r"|stroke-preview\.png|brush-recipe\.md)$")
EXPORT_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,120}\.(?:brush|brushset|gbr|zip)$")
LIBRARY_SUFFIXES = (".brush", ".brushset")

# (what is missing, the script that makes it, the verb, whether that verb is
# built). The path is under the brushes/ folder that holds this code. A writer
# is named in its dry-run form: a status never tells anyone to pass --confirm.
#
# A command is advertised only when the last column says its verb exists: a
# status that names a command which then exits 2 sends its reader nowhere. The
# column is not looked up at run time; test_mcp_server.py runs every row's
# `<verb> --help` and fails when the column and the script disagree.
NEXT_STEPS = (
    ("official", "pipeline/fetch_base_library.py", "fetch", True),
    ("catalog", "pipeline/ingest.py", "build", True),
    ("index", "vault/tools/brush_search.py", "index", True),
)


class ApiError(Exception):
    """A refusal a client can read: a code, a sentence, an HTTP status and,
    when there is one, what to do next (`hint`) and some detail (`data`)."""

    def __init__(self, code, message, status=400, hint=None, data=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.hint = hint
        self.data = data


# ── small helpers ────────────────────────────────────────────────────────────

def repo_relative(path, base):
    """A path as the status reports it: POSIX and relative to `base`, the folder
    that holds the data root (in a checkout, the repository root).

    A folder that a flag or a variable moved outside `base` is shown with
    leading `..` segments. On another drive there is no relative form, and only
    then is the absolute path given.
    """
    path, base = Path(path), Path(base)
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        pass
    try:
        return Path(os.path.relpath(path, base)).as_posix()
    except ValueError:
        return path.as_posix()


def count_files(folder):
    """How many files sit under a folder, at any depth, and how many of them are
    named as brush sets and as single brushes. By name only: no file is opened,
    so a Git LFS pointer counts like the file it stands for. A missing folder
    counts as empty."""
    counts = {"files": 0, "brushset": 0, "brush": 0}
    for _folder, _subfolders, names in os.walk(folder):
        for name in names:
            counts["files"] += 1
            lowered = name.lower()
            if lowered.endswith(".brushset"):
                counts["brushset"] += 1
            elif lowered.endswith(".brush"):
                counts["brush"] += 1
    return counts


def next_steps(missing, tool_root=None, steps=NEXT_STEPS):
    """The commands that would make what is missing, in the order to run them.
    A command is listed only when its verb is built and its script is on disk:
    a status never points at a file that is not there, nor at a verb the script
    does not have."""
    tool_root = Path(tool_root) if tool_root is not None else bc.TOOL_ROOT
    listed = []
    for what, script, verb, built in steps:
        if built and what in missing and (tool_root / script).is_file():
            listed.append(f"python {tool_root.name}/{script} {verb}")
    return listed


def _sig(path):
    """(mtime_ns, size) of a file, or None when it is not there."""
    try:
        stat = os.stat(path)
    except OSError:
        return None
    return (stat.st_mtime_ns, stat.st_size)


def _read_json(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return json.loads(handle.read())


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def check_id(value, what="id"):
    """A brush id, or ApiError(bad_argument). The only form an id takes."""
    if not isinstance(value, str) or not identity.is_brush_id(value):
        raise ApiError("bad_argument", f"{what} must be a brush id like b_0123456789ab", 400,
                       hint="ids come from search_brushes and get_brush")
    return value


def check_set_slug(value):
    if not isinstance(value, str) or not identity.is_set_slug(value):
        raise ApiError("bad_argument", "a set is named by its slug, such as demo-set", 400,
                       hint="list_sets shows the slugs")
    return value


MAX_JSON_DEPTH = 32


def _encodable(value, what):
    """Text that UTF-8 can hold: a lone surrogate (JSON can spell one) would
    reach a property list as half a character."""
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise ApiError("bad_argument", f"{what} holds a lone surrogate, which is not text", 400) from None
    return value


def _text(value, what, maximum, minimum=0):
    if not isinstance(value, str):
        raise ApiError("bad_argument", f"{what} must be text", 400)
    if "\x00" in value:
        raise ApiError("bad_argument", f"{what} may not hold a NUL character", 400)
    if not minimum <= len(value) <= maximum:
        raise ApiError("bad_argument", f"{what} must have {minimum} to {maximum} characters", 400)
    return _encodable(value, what)


def _deep_text_check(value, what):
    """Every string of a JSON value is UTF-8 text, and the value is not nested
    deeper than MAX_JSON_DEPTH."""
    stack = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            raise ApiError("bad_argument", f"{what} is nested more than {MAX_JSON_DEPTH} deep", 400)
        if isinstance(item, str):
            _encodable(item, what)
        elif isinstance(item, dict):
            for key, inner in item.items():
                _encodable(key, what) if isinstance(key, str) else None
                stack.append((inner, depth + 1))
        elif isinstance(item, (list, tuple)):
            stack.extend((inner, depth + 1) for inner in item)


def _list(value, what, maximum, item_max, pattern=None):
    if value is None:
        return []
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ApiError("bad_argument", f"{what} must be a list of text", 400)
    if len(value) > maximum:
        raise ApiError("bad_argument", f"{what} may hold at most {maximum} items", 400)
    out = []
    for item in value:
        item = _text(item, f"each of {what}", item_max, 1)
        if pattern is not None and pattern.match(item) is None:
            raise ApiError("bad_argument", f"{what}: `{item[:60]}` does not fit the grammar", 400,
                           hint="tags are axis=value[,value], for example medium=watercolor")
        out.append(item)
    return out


def _int(value, what, low, high):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ApiError("bad_argument", f"{what} must be a whole number", 400)
    if not low <= value <= high:
        raise ApiError("bad_argument", f"{what} must be {low} to {high}", 400)
    return value


def _flag(value, what):
    if not isinstance(value, bool):
        raise ApiError("bad_argument", f"{what} must be true or false", 400)
    return value


def _object(value, what, maximum_keys=MAX_CHANGES):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ApiError("bad_argument", f"{what} must be an object", 400)
    if len(value) > maximum_keys:
        raise ApiError("bad_argument", f"{what} may hold at most {maximum_keys} keys", 400)
    for key in value:
        if not isinstance(key, str) or len(key) > 128:
            raise ApiError("bad_argument", f"{what} has a key that is not a setting name", 400)
    _deep_text_check(value, what)
    return value


def _b64(value, what, limit):
    """The bytes of a base64 string, or ApiError(bad_argument)."""
    if not isinstance(value, str):
        raise ApiError("bad_argument", f"{what} must be base64 text", 400)
    if len(value) > (limit * 4) // 3 + 8:
        raise ApiError("too_large", f"{what} is larger than {limit:,} bytes", 413)
    try:
        data = base64.b64decode(value.encode("ascii"), validate=True)
    except (binascii.Error, ValueError, UnicodeEncodeError):
        raise ApiError("bad_argument", f"{what} is not valid base64", 400) from None
    if len(data) > limit:
        raise ApiError("too_large", f"{what} is larger than {limit:,} bytes", 413)
    return data


def b64(data):
    return base64.b64encode(data).decode("ascii")


def codec_error(exc, what="the file"):
    """A codec failure as the ApiError a client sees."""
    code = getattr(exc, "code", None)
    detail = getattr(exc, "detail", None) or str(exc)
    if isinstance(exc, LimitExceeded) and code == "upload_bytes":
        return ApiError("too_large", f"{what}: {detail}", 413)
    if isinstance(exc, ContainerError) and code in ("not_a_zip", "not_a_brush", "not_a_brushset"):
        return ApiError("unsupported_file", f"{what}: {detail}", 415,
                        hint="a .brush or .brushset file (or a zip holding them)")
    if isinstance(exc, ContainerError) and code == "lfs_pointer":
        return ApiError("library_missing", f"{what}: {detail}", 409, hint="run git lfs pull")
    return ApiError("corrupt_file", f"{what}: {detail}", 422, data={"codec": code})


def check_export_dir(target, paths):
    """Why `target` may not be an export folder, or None. An export never goes
    inside the tool's own folder or any data root (brush_file.py enforces the
    same rule for --out)."""
    try:
        target = Path(target).resolve()
    except OSError:
        return "that folder cannot be resolved"
    for name, root in (("the brushes tool", bc.TOOL_ROOT), ("the library", paths.library),
                       ("the catalog", paths.catalog), ("the vault", paths.vault)):
        root = Path(root).resolve()
        if target == root or root in target.parents:
            return f"an export folder may not lie inside {name}"
    return None


def write_export(out_dir, filename, data):
    """Put an export on disk: `<out_dir>/<filename>`, never over an existing
    file (F12: the one writer of an export folder). Written through
    `<name>.tmp`, then linked into place (an atomic no-clobber), or moved where
    links are not supported. `filename` is one path part made by this module."""
    if not isinstance(filename, str) or EXPORT_NAME.match(filename) is None:
        raise ApiError("bad_argument", "an export file name is a short ASCII slug and an extension", 400)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / filename
    tmp = out_dir / (filename + ".tmp")
    if target.exists():
        raise ApiError("exists", f"{filename} is already there; nothing was written", 409)
    try:
        with open(tmp, "xb") as handle:
            handle.write(data)
    except FileExistsError:
        raise ApiError("exists", f"{tmp.name} is in the way; nothing was written", 409) from None
    try:
        try:
            os.link(tmp, target)
        except FileExistsError:
            raise ApiError("exists", f"{filename} is already there; nothing was written", 409) from None
        except OSError:
            if target.exists():
                raise ApiError("exists", f"{filename} is already there; nothing was written", 409) from None
            os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()
    return target


# ── the search engine ────────────────────────────────────────────────────────

_ENGINE = None
_ENGINE_LOCK = threading.Lock()


def engine():
    """vault/tools/brush_search.py, loaded by path the way F9 says. Loading
    writes no bytecode: the servers write nothing."""
    global _ENGINE
    with _ENGINE_LOCK:
        if _ENGINE is None:
            path = bc.TOOL_ROOT / "vault" / "tools" / "brush_search.py"
            if not path.is_file():
                raise ApiError("internal", "the search engine (vault/tools/brush_search.py) is not here", 500)
            spec = importlib.util.spec_from_file_location("rosw_brush_search", path)
            module = importlib.util.module_from_spec(spec)
            kept = sys.dont_write_bytecode
            sys.dont_write_bytecode = True
            try:
                spec.loader.exec_module(module)
            finally:
                sys.dont_write_bytecode = kept
            _ENGINE = module
        return _ENGINE


# ── the service ──────────────────────────────────────────────────────────────

class Export:
    """What `build_export` made: the file's bytes and the report of F10."""

    def __init__(self, filename, data, report, dry_run):
        self.filename = filename
        self.data = data
        self.report = report
        self.dry_run = dry_run


class BrushService:
    """Read-only access to the library, the catalog and the vault, and the
    builder of exports. Everything it holds is loaded lazily, under a lock,
    and re-read when the file behind it changes."""

    def __init__(self, paths, *, mode="project", export_dir=None, version=SERVER_VERSION,
                 check_seconds=5.0, log=None):
        if mode not in MODES:
            raise ValueError(f"mode is one of {', '.join(MODES)}")
        self.paths = paths
        self.mode = mode
        self.export_dir = Path(export_dir) if export_dir is not None else None
        self.version = version
        self.check_seconds = check_seconds
        self.log = log
        self._lock = threading.RLock()
        self._catalog_cache = None
        self._index_cache = None
        self._containers = OrderedDict()
        self._schema_rows = None

    # ── paths and the catalog ────────────────────────────────────────────────
    def _shown(self, path):
        return repo_relative(path, self.paths.root.parent)

    def _catalog(self):
        """The parsed catalog.json plus lookup tables, or None when there is
        no readable catalog. Re-read when the file changes."""
        path = self.paths.catalog / "catalog.json"
        signature = _sig(path)
        if signature is None:
            return None
        with self._lock:
            cache = self._catalog_cache
            if cache is not None and cache["sig"] == signature:
                return cache
            try:
                data = _read_json(path)
            except (OSError, ValueError):
                return None
            if not isinstance(data, dict):
                return None
            sets = [row for row in data.get("sets", []) if isinstance(row, dict)]
            cache = {
                "sig": signature, "data": data,
                "ids": {row["id"] for row in data.get("brushes", [])
                        if isinstance(row, dict) and isinstance(row.get("id"), str)},
                "sets": sets,
                "sets_by_slug": {row.get("set_slug"): row for row in sets},
                "packs": {row.get("id"): row for row in data.get("packs", []) if isinstance(row, dict)},
            }
            self._catalog_cache = cache
            return cache

    def _missing(self):
        """What is absent, by the names of NEXT_STEPS."""
        halves = {half: count_files(self.paths.library / half) for half in LIBRARY_HALVES}
        official = halves["official"]["brushset"] + halves["official"]["brush"]
        return [what for what, absent in (("official", not official),
                                          ("catalog", not (self.paths.catalog / "catalog.json").is_file()),
                                          ("index", not self.paths.index.is_file())) if absent]

    def _not_ingested(self, reason=None):
        steps = next_steps(self._missing())
        hint = ("run, in order: " + "; ".join(steps)) if steps else "build the catalog with ingest.py build"
        return ApiError("not_ingested", reason or "there is no catalog yet", 503, hint=hint)

    def _record(self, brush_id):
        """catalog/brushes/<id>.json. The id is matched against the catalog
        first; the file name is built from it only after that."""
        brush_id = check_id(brush_id)
        catalog = self._catalog()
        if catalog is None:
            raise self._not_ingested()
        if brush_id not in catalog["ids"]:
            raise ApiError("unknown_id", f"no brush {brush_id} in the catalog", 404,
                           hint="search_brushes finds ids")
        path = self.paths.catalog / "brushes" / f"{brush_id}.json"
        try:
            record = _read_json(path)
        except (OSError, ValueError):
            raise self._not_ingested(f"catalog/brushes/{brush_id}.json is missing or unreadable") from None
        if not isinstance(record, dict) or record.get("id") != brush_id:
            raise self._not_ingested(f"catalog/brushes/{brush_id}.json does not hold that brush")
        return record

    # ── the index ────────────────────────────────────────────────────────────
    def _index_info(self, build):
        """(index or None, state, reason). `build=False` never builds an index
        in memory (a status stays cheap): without an index file it says
        `memory` and returns no index."""
        with self._lock:
            catalog_file = self.paths.catalog / "catalog.json"
            csig = _sig(catalog_file)
            if csig is None:
                self._index_cache = None
                return None, "not_ingested", f"no catalog: {self._shown(catalog_file)} is missing"
            if self._catalog() is None:                 # a file that is there and is not a catalog
                self._index_cache = None
                return None, "not_ingested", (f"the catalog cannot be read: {self._shown(catalog_file)} is "
                                              "not valid JSON")
            isig = _sig(self.paths.index)
            cache = self._index_cache
            now = time.monotonic()
            same_files = cache is not None and cache["csig"] == csig and cache["isig"] == isig
            if same_files and now - cache["checked"] < self.check_seconds and (build or cache["index"] is None):
                return cache["index"], cache["state"], cache["reason"]
            if isig is None and not build:
                return None, "memory", (f"no index file: {self._shown(self.paths.index)} is missing; "
                                        "it is built in memory when a search needs it")
            search = engine()
            index, from_file, note = None, isig is not None, ""
            if same_files and cache["index"] is not None:
                index, from_file, note = cache["index"], cache["from_file"], cache["note"]
            elif from_file:
                try:
                    index = search.load_index(self.paths.index)
                except (search.UsageError, OSError, ValueError, MemoryError):
                    index, from_file = None, False
                    note = "the index file is unreadable; "
            if index is None:
                try:
                    index = search.build_index(self.paths.vault, self.paths.catalog, write=False)
                except Exception as exc:                # a catalog that cannot be read is "not ingested"
                    self._log(f"building the index in memory failed: {type(exc).__name__}: {exc}")
                    self._index_cache = None
                    return None, "not_ingested", ("the catalog cannot be read "
                                                  f"({self._shown(catalog_file)}): {type(exc).__name__}")
            try:
                fresh = search.check_fresh(index, self.paths.vault, self.paths.catalog)
                state, reason = fresh["state"], fresh["reason"]
            except Exception as exc:                    # cannot tell: say stale, never fresh
                state, reason = "stale", f"could not check the index against its inputs ({type(exc).__name__})"
            if not from_file:
                if state == "stale" and same_files:
                    try:
                        index = search.build_index(self.paths.vault, self.paths.catalog, write=False)
                    except Exception:
                        pass
                state = "memory"
                reason = (f"{note}no index file: {self._shown(self.paths.index)} is missing; built in memory"
                          if isig is None else f"{note}built in memory; nothing is written")
            self._index_cache = {"csig": csig, "isig": isig, "index": index, "state": state,
                                 "reason": reason, "checked": now, "by_id": None,
                                 "from_file": from_file, "note": note}
            return index, state, reason

    def _ready(self):
        """(index, state, by-id table) or ApiError(not_ingested)."""
        index, state, reason = self._index_info(build=True)
        if index is None:
            raise self._not_ingested(reason if state == "not_ingested" else None)
        with self._lock:
            cache = self._index_cache
            if cache is None or cache["index"] is not index:
                cache = self._index_cache = {"csig": None, "isig": None, "index": index, "state": state,
                                             "reason": reason, "checked": time.monotonic(), "by_id": None,
                                             "from_file": True, "note": ""}
            if cache["by_id"] is None:
                cache["by_id"] = {chunk["brush_id"]: chunk for chunk in index["chunks"]
                                  if chunk.get("source_type") == "brush"}
            return index, state, cache["by_id"]

    def _log(self, text):
        if self.log is not None:
            self.log(text)

    # ── status ───────────────────────────────────────────────────────────────
    def vocabulary_axes(self):
        """The tag axes the vocabulary defines, in order; [] when there is none."""
        try:
            search = engine()
            return list(search.load_vocabulary(self.paths.vault))
        except Exception:
            return []

    def status(self):
        """The `library_status` payload of F10. It lists folders and reads the
        catalog's counts, the index state and the vocabulary; it opens no
        brush file."""
        paths = self.paths
        library_files = {half: count_files(paths.library / half) for half in LIBRARY_HALVES}
        brush_files = {half: library_files[half]["brushset"] + library_files[half]["brush"]
                       for half in LIBRARY_HALVES}
        _, state, reason = self._index_info(build=False)
        catalog = self._catalog()
        counts = catalog["data"].get("counts") if catalog is not None else None
        if state not in INDEX_STATES:                    # cannot happen; a status never says null
            state, reason = "stale", reason or "unknown"
        return {
            "server": SERVER_NAME,
            "version": self.version,
            "mode": self.mode,
            "root": self._shown(paths.root),
            "index": {"state": state, "reason": reason},
            "counts": counts if isinstance(counts, dict) else None,
            "library_present": sum(brush_files.values()) > 0,
            "library_files": library_files,
            "vocabulary_axes": self.vocabulary_axes(),
            "export": {"enabled": self.export_dir is not None,
                       "dir": self._shown(self.export_dir) if self.export_dir is not None else None},
            "next_steps": next_steps(self._missing()),
        }

    # ── search ───────────────────────────────────────────────────────────────
    def _filters(self, tags, where, where_not):
        return (_list(tags, "tags", 12, 80, TAG_FILTER), _list(where, "where", 12, 120),
                _list(where_not, "where_not", 12, 120))

    def search(self, query="", tags=(), where=(), where_not=(), top=8, offset=0, *,
               top_max=HTTP_TOP_MAX, require_filter=False, settings=False, source_types=("brush",)):
        """The F9 envelope, plus `index`. With no query and no filter it is the
        library in set order (unless `require_filter`, which refuses that)."""
        query = _text(query if query is not None else "", "query", 500)
        tags, where, where_not = self._filters(tags, where, where_not)
        top = _int(top, "top", 1, top_max)
        offset = _int(offset, "offset", 0, MAX_OFFSET)
        if require_filter and not (query.strip() or tags or where):
            raise ApiError("bad_argument", "give at least one of query, tags or where", 400,
                           hint="for example query \"dry grainy ink\" or tags [\"medium=charcoal\"]")
        index, state, _ = self._ready()
        search = engine()
        try:
            envelope = search.search_index(index, query, tags=tags, where=where, where_not=where_not,
                                           source_types=list(source_types), top=top, offset=offset,
                                           settings=bool(settings))
        except search.UsageError as exc:
            raise ApiError("bad_argument", str(exc), 400) from None
        envelope["index"] = state
        return envelope

    def similar(self, brush_id, top=8, where=(), where_not=(), *, other_sets=False, top_max=HTTP_TOP_MAX):
        brush_id = check_id(brush_id)
        _, where, where_not = self._filters((), where, where_not)
        top = _int(top, "top", 1, top_max)
        index, state, by_id = self._ready()
        if brush_id not in by_id:
            raise ApiError("unknown_id", f"no brush {brush_id} in the catalog", 404,
                           hint="search_brushes finds ids")
        search = engine()
        try:
            envelope = search.similar(index, brush_id, where=where, where_not=where_not, top=top,
                                      other_sets=bool(other_sets))
        except search.UsageError as exc:
            raise ApiError("bad_argument", str(exc), 400) from None
        except search.NotFound as exc:
            raise ApiError("unknown_id", str(exc), 404) from None
        envelope["index"] = state
        return envelope

    def similar_settings(self, settings, tags=(), where=(), where_not=(), top=10, *, other_sets=False,
                         top_max=HTTP_TOP_MAX):
        """Brushes like a settings object that is not a library brush."""
        settings = _object(settings, "settings", 512)
        if not settings:
            raise ApiError("bad_argument", "settings must name at least one setting", 400)
        tags, where, where_not = self._filters(tags, where, where_not)
        top = _int(top, "top", 1, top_max)
        index, state, _ = self._ready()
        search = engine()
        try:
            envelope = search.similar(index, None, settings=settings, tags=tags, where=where,
                                      where_not=where_not, top=top, other_sets=bool(other_sets))
        except search.UsageError as exc:
            raise ApiError("bad_argument", str(exc), 400) from None
        envelope["index"] = state
        return envelope

    def facets(self, tags=(), where=(), where_not=()):
        tags, where, where_not = self._filters(tags, where, where_not)
        index, state, _ = self._ready()
        search = engine()
        try:
            result = search.facet_counts(index, tags=tags, where=where, where_not=where_not)
        except search.UsageError as exc:
            raise ApiError("bad_argument", str(exc), 400) from None
        result["index"] = state
        return result

    # ── the vocabulary ───────────────────────────────────────────────────────
    def _axis_descriptions(self):
        """{axis: sentence} from the comment line above each `<axis>_tags:` key
        of vocabulary.yaml (the author's own words)."""
        out = {}
        try:
            text = bc.read_text(self.paths.vocabulary)
        except OSError:
            return out
        for match in re.finditer(r"^# ([a-z]+)_tags: (.+)$", text, re.M):
            out[match.group(1)] = match.group(2).strip()
        return out

    def _facet_rules(self):
        try:
            data = _read_json(self.paths.schema / "facets.json")
            return {name: row.get("rule") for name, row in data.get("facets", {}).items()
                    if isinstance(row, dict)}
        except (OSError, ValueError, AttributeError):
            return {}

    def vocabulary(self, axis=None):
        """`list_vocabulary`: the tag axes with their tags, and the facets with
        their value ranges. Works in every state; without an index the facet
        values are null."""
        search = engine()
        if axis is not None:
            axis = _text(axis, "axis", 40, 1)
        try:
            vocabulary = search.load_vocabulary(self.paths.vault)
        except search.UsageError:
            vocabulary = {}
        names = list(vocabulary)
        if axis is not None:
            short = axis[:-5] if axis.endswith("_tags") else axis
            if short not in search.AXES:
                raise ApiError("bad_argument", f"unknown tag axis `{axis}`", 400,
                               hint=f"axes: {', '.join(search.AXES)}")
            names = [short] if short in vocabulary else []
        descriptions = self._axis_descriptions()
        axes = {name: {"description": descriptions.get(name), "tags": list(vocabulary[name])}
                for name in names}
        rules = self._facet_rules()
        summary = {}
        try:
            index, _, _ = self._ready()
            summary = search.facet_counts(index)["facets"]
        except ApiError:
            summary = {}
        facets = []
        for name in sorted(set(rules) | set(summary)):
            info = summary.get(name)
            if info is None:
                kind, values = None, None
            elif info["kind"] == "number":
                kind, values = "number", {"min": info["min"], "median": info["median"], "max": info["max"]}
            else:
                kind, values = info["kind"], sorted(info["values"])
            facets.append({"name": name, "type": kind, "values": values, "description": rules.get(name)})
        return {"axes": axes, "facets": facets}

    # ── sets ─────────────────────────────────────────────────────────────────
    def _set_entry(self, row, by_id, catalog):
        pack = catalog["packs"].get(row.get("pack")) or {}
        members = [i for i in row.get("brushes", []) if isinstance(i, str)]
        return {"set_slug": row.get("set_slug"), "set_id": row.get("set_id"), "name": row.get("name"),
                "library": row.get("library"), "vendor": pack.get("vendor"),
                "brush_count": row.get("brush_count"),
                "tagged": sum(1 for i in members if (by_id.get(i) or {}).get("tag_state") == "tagged"),
                "note": row.get("note"), "title": row.get("title"), "kind": row.get("kind"),
                "pack": row.get("pack")}

    def list_sets(self, library=None):
        if library is not None and library not in LIBRARY_HALVES:
            raise ApiError("bad_argument", "library is `user` or `official`", 400)
        _, _, by_id = self._ready()
        catalog = self._catalog()
        return {"sets": [self._set_entry(row, by_id, catalog) for row in catalog["sets"]
                         if library is None or row.get("library") == library]}

    def get_set(self, slug):
        """One set: its row and its brushes as F9 rows, in set order."""
        slug = check_set_slug(slug)
        index, state, by_id = self._ready()
        catalog = self._catalog()
        row = catalog["sets_by_slug"].get(slug)
        if row is None:
            raise ApiError("unknown_id", f"no set {slug} in the catalog", 404, hint="list_sets shows the slugs")
        search = engine()
        rows = [search.make_row(by_id[i], 1.0) for i in row.get("brushes", []) if i in by_id]
        return {"set": self._set_entry(row, by_id, catalog), "brushes": rows, "index": state}

    # ── one brush ────────────────────────────────────────────────────────────
    @staticmethod
    def _include(include):
        if include is None:
            return set(DEFAULT_INCLUDE)
        if isinstance(include, str):
            include = [part for part in include.split(",") if part]
        if not isinstance(include, (list, tuple)) or len(include) > len(INCLUDE_PARTS):
            raise ApiError("bad_argument", "include is a list of parts", 400)
        bad = [part for part in include if part not in INCLUDE_PARTS]
        if bad:
            raise ApiError("bad_argument", f"unknown part `{str(bad[0])[:40]}` in include", 400,
                           hint=f"parts: {', '.join(INCLUDE_PARTS)}")
        return set(include)

    def get_brush(self, brush_id, include=None):
        """`get_brush`: names, sets, library, era, family, the dual summary, the
        preview object and the duplicates; `include` adds `settings`, `tags`,
        `facets`, `visual`, `textures` and `note`."""
        brush_id = check_id(brush_id)
        parts = self._include(include)
        record = self._record(brush_id)
        index, state, by_id = self._ready()
        chunk = by_id.get(brush_id)
        facets = record.get("facets") or {}
        secondary = record.get("secondary")
        seen, sets = set(), []
        home = record.get("home") or {}
        occurrences = [o for o in record.get("occurrences") or [] if isinstance(o, dict)]
        occurrences.sort(key=lambda o: o.get("set_slug") != home.get("set_slug"))      # the home set first
        for occurrence in occurrences:
            slug = occurrence.get("set_slug")
            if slug in seen or slug is None:
                continue
            seen.add(slug)
            sets.append({"set_slug": slug, "set_id": occurrence.get("set_id"),
                         "position": occurrence.get("position"), "pack": occurrence.get("pack")})
        preview = dict(record.get("preview") or {})
        out = {
            "id": brush_id, "name": record.get("name"), "display_name": record.get("display_name"),
            "slug": record.get("slug"), "library": record.get("library"), "pack": record.get("pack"),
            "era": record.get("era"), "family": record.get("family"),
            "key_count": (record.get("format") or {}).get("key_count"),
            "home": home, "sets": sets,
            "dual": ({"name": secondary.get("name"), "era": secondary.get("era"),
                      "blend_code": facets.get("dual_blend_code")} if isinstance(secondary, dict) else None),
            "preview": preview,
            "preview_kinds": [kind for kind in PREVIEW_KINDS if preview.get(kind)],
            "approximate": preview.get("stroke_source") == "rendered-approx",
            "duplicates": list((chunk or {}).get("also_in") or []),
            "occurrences": len(record.get("occurrences") or []),
            "index": state,
        }
        if "facets" in parts:
            out["facets"] = facets
            out["facet_words"] = list(record.get("facet_words") or [])
        if "tags" in parts:
            search = engine()
            out["tag_state"] = (chunk or {}).get("tag_state", "untagged")
            for key in search.TAG_FIELDS:
                out[key] = list((chunk or {}).get(key) or [])
        if "visual" in parts:
            visual = (chunk or {}).get("visual") or ""
            out["visual"] = visual
            out["visual_basis"] = "described-not-measured" if visual else None
        if "textures" in parts:
            out["textures"] = {"shape": record.get("shape"), "grain": record.get("grain"),
                               "secondary": ({"shape": secondary.get("shape"), "grain": secondary.get("grain")}
                                             if isinstance(secondary, dict) else None)}
        if "note" in parts:
            out["note"] = {"path": (chunk or {}).get("note"), "heading": (chunk or {}).get("heading"),
                           "lines": [(chunk or {}).get("start_line"), (chunk or {}).get("end_line")]}
        if "settings" in parts:
            out["settings"] = record.get("settings") or {}
        return out

    # ── previews ─────────────────────────────────────────────────────────────
    def _vault_file(self, relative):
        """A file under vault/_Previews/ named by a stored path, or None when
        the path is not a plain relative path or leaves the previews root."""
        if not isinstance(relative, str) or not relative or "\x00" in relative or "\\" in relative:
            return None
        if relative.startswith("/") or re.match(r"^[A-Za-z]:", relative):
            return None
        if any(part in ("", ".", "..") for part in relative.split("/")):
            return None
        try:
            root = self.paths.previews.resolve()
            path = (self.paths.vault / relative).resolve()
        except OSError:
            return None
        if root != path and root not in path.parents:
            return None
        return path if path.is_file() else None

    def preview(self, brush_id, kind):
        """(png bytes, meta) of a stored preview. Serves the files previews.py
        wrote and nothing else; it renders nothing."""
        brush_id = check_id(brush_id)
        if kind not in PREVIEW_KINDS:
            raise ApiError("bad_argument", f"kind is one of {', '.join(PREVIEW_KINDS)}", 400)
        record = self._record(brush_id)
        stored = (record.get("preview") or {})
        relative = stored.get(kind)
        hint = "python brushes/pipeline/previews.py render"
        if not relative:
            source = stored.get(f"{kind}_source")
            why = ("the brush only names an image inside the drawing app" if source == "bundled"
                   else "no preview has been rendered for it")
            raise ApiError("no_preview", f"no {kind} preview for {brush_id}: {why}", 404, hint=hint)
        path = self._vault_file(relative)
        if path is None:
            raise ApiError("no_preview", f"the {kind} preview of {brush_id} is not in the previews folder",
                           404, hint=hint)
        try:
            if path.stat().st_size > PREVIEW_MAX_BYTES:
                raise ApiError("no_preview", f"the {kind} preview of {brush_id} is larger than "
                                             f"{PREVIEW_MAX_BYTES // 1024} KiB", 404)
            with open(path, "rb") as handle:
                data = handle.read(PREVIEW_MAX_BYTES + 1)
            info = png_io.png_info(data)
        except OSError:
            raise ApiError("no_preview", f"the {kind} preview of {brush_id} cannot be read", 404, hint=hint) from None
        except CodecError:
            raise ApiError("no_preview", f"the {kind} preview of {brush_id} is not a PNG", 404, hint=hint) from None
        meta = {"kind": kind, "width": info["width"], "height": info["height"],
                "source": stored.get(f"{kind}_source"),
                "approximate": kind == "stroke" and stored.get("stroke_source") == "rendered-approx"}
        return data, meta

    def preview_set(self, brush_id, kinds=("stroke",)):
        """`get_preview`: ({id, name, images, missing}, [(kind, png bytes)]).
        An error only when none of the kinds exists."""
        brush_id = check_id(brush_id)
        if isinstance(kinds, str) or not isinstance(kinds, (list, tuple)) or not 1 <= len(kinds) <= 3:
            raise ApiError("bad_argument", "kinds is 1 to 3 of stroke, shape, grain", 400)
        record = self._record(brush_id)
        images, missing, files, last = [], [], [], None
        for kind in dict.fromkeys(kinds):
            try:
                data, meta = self.preview(brush_id, kind)
            except ApiError as exc:
                if exc.code != "no_preview":
                    raise
                missing.append({"kind": kind, "reason": exc.message})
                last = exc
                continue
            images.append({**meta, "reason": ("a stand-in for the real stroke" if meta["approximate"] else None)})
            files.append((kind, data))
        if not files:
            raise ApiError("no_preview", missing[0]["reason"] if len(missing) == 1
                           else f"no preview of {brush_id} exists for the kinds asked", 404,
                           hint=last.hint if last is not None else None, data={"missing": missing})
        return {"id": brush_id, "name": record.get("name"), "images": images, "missing": missing}, files

    # ── the settings schema ──────────────────────────────────────────────────
    def settings_schema(self, group=None, keys=None, detail="compact"):
        """`get_brush_settings_schema`: the rows of schema/silica_keys.json."""
        if detail not in ("compact", "full"):
            raise ApiError("bad_argument", "detail is compact or full", 400)
        schema = brush_model.load_schema()
        groups = schema.get("groups", [])
        rows = schema.get("keys", [])
        if group is not None:
            group = _text(group, "group", 40, 1)
            if group not in {g["id"] for g in groups}:
                raise ApiError("bad_argument", f"unknown group `{group[:40]}`", 400,
                               hint="groups: " + ", ".join(g["id"] for g in groups))
        wanted = None
        if keys is not None:
            wanted = _list(keys, "keys", 60, 64)
        by_key = {row["key"]: row for row in rows}
        chosen = [row for row in rows
                  if (group is None or row.get("group") == group) and (wanted is None or row["key"] in wanted)]
        out_rows = {}
        for row in chosen:
            limits = row.get("limits") or [None, None]
            entry = {"t": row.get("type"), "min": limits[0], "max": limits[1], "def": row.get("default"),
                     "eras": row.get("eras"), "group": row.get("group")}
            if detail == "full":
                entry.update({"label": row.get("label"), "section": row.get("section"),
                              "description": row.get("hint"), "confidence": row.get("confidence"),
                              "enum": row.get("enum"), "observed": row.get("observed"),
                              "limits_hard": row.get("limits_hard"), "aliases": row.get("aliases"),
                              "ui": row.get("ui"), "notes": row.get("notes")})
            out_rows[row["key"]] = entry
        counts = {}
        for row in rows:
            counts[row.get("group")] = counts.get(row.get("group"), 0) + 1
        payload = {"schema_version": schema.get("schema_version"),
                   "groups": [{"group": g["id"], "label": g.get("label"), "keys": counts.get(g["id"], 0)}
                              for g in groups],
                   "keys": out_rows}
        if wanted is not None:
            payload["unknown_keys"] = [key for key in wanted if key not in by_key]
        return payload

    # ── patches ──────────────────────────────────────────────────────────────
    @staticmethod
    def report_patch(brush, changes, *, mode="strict", allow_unknown=False):
        """The PatchReport of apply_patch on `brush`, nothing else. This is the
        function the cases of schema/patch_cases.json are run through."""
        try:
            patched, report = brush_model.apply_patch(brush, changes, mode=mode, allow_unknown=allow_unknown)
        except CodecError as exc:
            raise ApiError("bad_argument", str(exc), 400) from None
        return patched, report

    def _members_folder(self, members, what="base"):
        """A BrushFolder from `[{"path", "b64"}]`, under the F3 caps."""
        if not isinstance(members, list) or not 1 <= len(members) <= MAX_BASE_MEMBERS:
            raise ApiError("bad_argument", f"{what}.members is a list of 1 to {MAX_BASE_MEMBERS} members", 400)
        built, seen, total = [], set(), 0
        for member in members:
            if not isinstance(member, dict) or set(member) - {"path", "b64"} or "path" not in member:
                raise ApiError("bad_argument", f"each member of {what} is {{path, b64}}", 400)
            path = _text(member["path"], "a member path", 255, 1)
            if container.hostile(path):
                raise ApiError("bad_argument", f"member path {path[:60]!r} is refused: {container.hostile(path)}", 400)
            if path in seen:
                raise ApiError("bad_argument", f"member {path[:60]!r} appears twice", 400)
            seen.add(path)
            cap = (container.CAPS["archive_bytes"] if path.rsplit("/", 1)[-1] == container.ARCHIVE
                   else container.CAPS["entry_bytes"])
            data = _b64(member.get("b64", ""), f"member {path[:60]}", cap)
            total += len(data)
            if total > container.CAPS["upload_bytes"]:
                raise ApiError("too_large", "the members together are over the upload cap", 413)
            built.append(container.Member(path, data))
        folder = container.BrushFolder(built)
        if folder.archive is None:
            raise ApiError("bad_argument", f"{what} has no Brush.archive member", 400)
        return folder

    def _decode(self, archive, what="the archive"):
        try:
            return brush_model.decode(archive)
        except CodecError as exc:
            raise codec_error(exc, what) from None

    def _template(self, era):
        """(Brush, description) of the new-brush template of `era`; without the
        donor in the library, the schema-only test base, and it says so."""
        names = {row["id"] for row in brush_model.load_schema().get("eras", [])}
        if era not in names:
            raise ApiError("bad_argument", f"unknown era `{str(era)[:20]}`", 400,
                           hint="eras: " + ", ".join(sorted(names)))
        if era in brush_model.NEW_BRUSH_DONORS:
            try:
                brush = brush_model.new_brush("Patch check", era=era, library=self.paths.library)
                return brush, {"kind": "new_brush_template", "era": era}
            except CodecError as exc:
                if getattr(exc, "code", None) not in ("library_missing", "lfs_pointer", "donor_missing",
                                                      "donor_mismatch"):
                    raise ApiError("bad_argument", str(exc), 400) from None
        try:
            brush = brush_model.case_base(era)
        except CodecError as exc:
            raise ApiError("bad_argument", str(exc), 400) from None
        return brush, {"kind": "schema_defaults", "era": era,
                       "note": "the new-brush template needs a donor brush from the library; this check "
                               "ran against the schema's default values instead"}

    def validate_patch(self, changes, base_id=None, base=None, era=None, *, mode="strict"):
        """`validate_settings_patch` and POST /api/validate-patch: the
        PatchReport of F3 plus `patch_text` (the envelope the app's paste box
        takes) and `base` (what the check ran against)."""
        if changes is None or not isinstance(changes, dict):
            raise ApiError("bad_argument", "changes must be an object of key: value", 400)
        _object(changes, "changes")
        if base_id is not None and base is not None:
            raise ApiError("bad_argument", "give base_id or base, not both", 400)
        if era is not None:
            era = _text(era, "era", 16, 1)
        if len(json.dumps(changes, default=str)) > MAX_PATCH_JSON:
            raise ApiError("too_large", "changes are larger than 1 MiB", 413)
        if base_id is not None:
            check_id(base_id, "base_id")
            folder, _, _ = self.open_library_folder(base_id)
            brush = self._decode(folder.archive, base_id)
            described = {"kind": "library", "id": base_id, "era": brush.era}
        elif base is not None:
            if not isinstance(base, dict) or set(base) - {"members"}:
                raise ApiError("bad_argument", "base is {members: [{path, b64}]}", 400,
                               hint="a base is original bytes, never a to_json model or catalog settings")
            folder = self._members_folder(base.get("members"), "base")
            brush = self._decode(folder.archive, "base")
            described = {"kind": "members", "era": brush.era}
        else:
            brush, described = self._template(era or brush_model.NEW_BRUSH_ERA)
        if era is not None and (base_id is not None or base is not None) and era != brush.era:
            raise ApiError("bad_argument", f"era {era} is not the base's own era ({brush.era})", 400)
        _, report = self.report_patch(brush, changes, mode=mode)
        report = dict(report)
        applied = report["applied"]
        report["patch_text"] = None
        if applied:
            shown = ", ".join(list(applied)[:6]) + (" ..." if len(applied) > 6 else "")
            report["patch_text"] = json.dumps(
                {"schema": brush_model.PATCH_SCHEMA, "base_id": base_id,
                 "summary": f"{len(applied)} setting(s): {shown}", "changes": applied},
                sort_keys=True, ensure_ascii=False, separators=(", ", ": "))
        report["base"] = described
        return report

    # ── the library's originals ──────────────────────────────────────────────
    def _library_path(self, relative):
        """A container of the library named by a catalog path, or ApiError."""
        problem = None
        if (not isinstance(relative, str) or not relative or "\x00" in relative or "\\" in relative
                or relative.startswith("/") or re.match(r"^[A-Za-z]:", relative)
                or any(part in ("", ".", "..") for part in relative.split("/"))
                or not relative.lower().endswith(LIBRARY_SUFFIXES)):
            problem = "the catalog names a file that is not a plain library path"
        if problem is None:
            try:
                root = self.paths.library.resolve()
                path = (self.paths.library / relative).resolve()
            except OSError:
                problem = "the library folder cannot be resolved"
            else:
                if root not in path.parents:
                    problem = "the catalog names a file outside the library"
                elif not path.is_file():
                    problem = f"{relative} is not in the library"
        if problem:
            raise ApiError("library_missing", problem, 409,
                           hint="the originals are needed for this: put the library back (git lfs pull)")
        return path

    def _found(self, relative):
        """container.read_any of a library file, cached by (path, mtime, size)."""
        path = self._library_path(relative)
        signature = (relative, *(_sig(path) or (0, 0)))
        with self._lock:
            hit = self._containers.get(signature)
            if hit is not None:
                self._containers.move_to_end(signature)
                return hit
        try:
            found = container.read_any(container.read_path(path), relative)
        except OSError:
            raise ApiError("library_missing", f"{relative} cannot be read", 409) from None
        except ContainerError as exc:
            raise codec_error(exc, relative) from None
        with self._lock:
            self._containers[signature] = found
            # Two containers at most, and past 256 MiB of source files only the newest:
            # a parsed set holds all of its members in memory.
            while len(self._containers) > 1 and (len(self._containers) > 2 or
                                                 sum(key[2] for key in self._containers) > 256 * MIB):
                self._containers.popitem(last=False)
        return found

    @staticmethod
    def _id_of(folder):
        try:
            return identity.brush_id_from_sha256(identity.content_sha256(*container.identity_inputs(folder)))
        except (ContainerError, identity.IdentityError):
            return None

    def open_library_folder(self, brush_id):
        """(BrushFolder, folder name or None, set name or None): the original
        members of a library brush. The brush is found in the catalog by id,
        read from the container the catalog names, and accepted only when its
        content id is the one asked for."""
        record = self._record(brush_id)
        occurrences = [o for o in record.get("occurrences") or [] if isinstance(o, dict)]
        if not occurrences:
            raise ApiError("library_missing", f"the catalog records no place for {brush_id}", 409)
        last = None
        for occurrence in occurrences:
            try:
                found = self._found(occurrence.get("container"))
            except ApiError as exc:
                last = exc
                continue
            prefix = occurrence.get("entry_prefix") or ""
            uuid_hint = prefix.rstrip("/").rsplit("/", 1)[-1] if prefix else None
            for fast in (True, False):
                for item in found:
                    pairs = item.brushes if isinstance(item, container.BrushSet) else [(None, item)]
                    for uuid, folder in pairs:
                        if fast and uuid != uuid_hint and not (uuid is None and not uuid_hint):
                            continue
                        if self._id_of(folder) == brush_id:
                            return folder, uuid, getattr(item, "name", None) if uuid else None
        if last is not None:
            raise last
        raise ApiError("library_missing", f"{brush_id} is not in the container the catalog names", 409,
                       hint="the catalog may be older than the library; run ingest.py build")

    # ── what a brush looks like to the app ───────────────────────────────────
    def _bundled(self):
        folder = self.paths.library / "bundled"
        return folder if folder.is_dir() else None

    @staticmethod
    def _tile(data):
        """A 256-fit grey PNG of an image, or None."""
        try:
            image = png_io.to_gray8(png_io.read_png(data))
            factor = png_io.fit_factor(image.width, image.height, PREVIEW_TILE, PREVIEW_TILE)
            image = png_io.box_reduce(image, factor)
            return png_io.write_png(image.width, image.height, "L", image.pixels)
        except (CodecError, ValueError):
            return None

    def _texture_entry(self, data, source, name, mode):
        if source in ("embedded", "bundled-supplied") and data is not None:
            entry = {"source": source}
            if source == "bundled-supplied":
                entry["ref"] = name
            try:
                info = png_io.png_info(data)
                entry.update({"width": info["width"], "height": info["height"]})
            except CodecError:
                entry.update({"width": None, "height": None})
            if mode == "full":
                entry["png_b64"] = b64(data)
            elif mode == "preview":
                tile = self._tile(data)
                entry["png_b64"] = b64(tile) if tile is not None else None
                entry["preview"] = True
            return entry
        if source == "bundled":
            return {"source": "bundled", "ref": name, "standin_png_b64": None, "approximate": True}
        if source == "blank":
            return {"source": "blank", "ref": name}
        return {"source": "none"}

    def _describe(self, folder, textures):
        """The settings, meta and textures of one archive (a brush or a Sub01/)."""
        brush = self._decode(folder.archive)
        names = container.texture_names(brush.params)
        resolved = container.resolve_textures(folder, brush.params, bundled=self._bundled())
        known = set()
        for row in self._rows():
            known.add(row["key"])
            known.update(row.get("aliases") or [])
        meta = {"class": brush.root_class[0] if brush.root_class else None,
                "classes": list(brush.root_class), "key_count": brush.key_count,
                "unknown_keys": [key for key in brush.params if key not in known],
                "archive_sha256": sha256_hex(folder.archive)}
        return brush, {
            "name": brush.name, "era": brush.era, "family": brush.family,
            "settings": brush_model.to_json(brush)["params"], "meta": meta,
            "textures": {role: self._texture_entry(data, source, names[role], textures)
                         for role, (data, source) in resolved.items()},
        }

    def _rows(self):
        if self._schema_rows is None:
            self._schema_rows = brush_model.load_schema().get("keys", [])
        return self._schema_rows

    def _brush_response(self, folder, member, textures, library_id, warnings, *, members_in_base):
        brush, described = self._describe(folder, textures)
        thumbnail = folder.thumbnail
        if thumbnail is None:
            thumb = None
        elif textures == "none":
            thumb = {"present": True}
        else:
            thumb = {"png_b64": b64(thumbnail)}
        described["textures"]["thumbnail"] = thumb
        sub = folder.sub
        sub_out = None
        if sub is not None and sub.archive is not None:
            try:
                _, sub_described = self._describe(sub, textures)
                sub_out = {"settings": sub_described["settings"], "textures": sub_described["textures"],
                           "meta": sub_described["meta"]}
            except ApiError:
                warnings = list(warnings) + ["Sub01/Brush.archive cannot be decoded"]
        response = {"kind": "brush", "member": member, "name": described["name"], "era": described["era"],
                    "settings": described["settings"], "meta": described["meta"],
                    "textures": described["textures"], "sub": sub_out,
                    "base": ({"members": [{"path": m.path, "b64": b64(m.data)} for m in folder.members]}
                             if members_in_base else {"library_id": library_id}),
                    "library_id": library_id, "warnings": list(warnings) + list(folder.warnings)}
        for role, member_path, key in (("shape", container.SHAPE, container.SHAPE_KEY),
                                       ("grain", container.GRAIN, container.GRAIN_KEY)):
            if folder.get(member_path) is not None and brush.params.get(key):
                response["warnings"].append(f"info: {member_path} beside a bundled path; the "
                                            f"{member_path} is what the brush uses")
        return response

    def open_library_brush(self, brush_id, textures="full"):
        """GET /api/brush/<id>/open: the import "brush" response from the
        library original. Needs the originals (409 library_missing)."""
        if textures not in TEXTURE_MODES:
            raise ApiError("bad_argument", f"textures is one of {', '.join(TEXTURE_MODES)}", 400)
        folder, uuid, set_name = self.open_library_folder(check_id(brush_id))
        member = f"{set_name}::{uuid}" if uuid else "brush"
        return self._brush_response(folder, member, textures, brush_id, [], members_in_base=textures == "full")

    # ── import ───────────────────────────────────────────────────────────────
    def decode_upload(self, data, filename="", member=None, textures="full"):
        """POST /api/import: a manifest when the file holds several brushes and
        no member is named, else one brush. Read in memory under the F3 caps;
        nothing is written and no entry name is used as a path."""
        if textures not in TEXTURE_MODES:
            raise ApiError("bad_argument", f"textures is one of {', '.join(TEXTURE_MODES)}", 400)
        if not isinstance(data, (bytes, bytearray)) or not data:
            raise ApiError("bad_argument", "the upload is empty", 400)
        if member is not None:
            member = _text(member, "member", 400, 1)
        hint = "".join(ch for ch in str(filename or "") if ch.isprintable())[:120]
        try:
            found = container.read_any(bytes(data), hint)
        except ContainerError as exc:
            raise codec_error(exc, hint or "the upload") from None
        entries = []         # (member key, set name or None, uuid or None, folder)
        for number, item in enumerate(found):
            if isinstance(item, container.BrushSet):
                for uuid, folder in item.brushes:
                    entries.append((f"s{number}/{uuid}", item.name, uuid, folder))
            else:
                entries.append((f"b{number}", None, None, item))
        skipped = [{"entry": str(where)[:200], "reason": str(why)[:200]} for where, why in found.skipped]
        for item in found:
            if isinstance(item, container.BrushSet):
                skipped += [{"entry": f"{item.origin} :: {entry}"[:200], "reason": str(why)[:200]}
                            for entry, why in item.skipped]
        if not entries:
            raise ApiError("unsupported_file", "the file holds no brush", 415,
                           hint="a .brush or .brushset file, or a zip holding them", data={"skipped": skipped})
        catalog = self._catalog()
        ids = catalog["ids"] if catalog is not None else set()
        if member is None and len(entries) > 1:
            return self._manifest(entries, found, skipped, ids)
        if member is None:
            chosen = entries[0]
        else:
            chosen = next((entry for entry in entries if entry[0] == member), None)
            if chosen is None:
                raise ApiError("bad_argument", "no such member in the file", 400,
                               hint="post the file without `member` to list the members")
        key, _, _, folder = chosen
        library_id = self._id_of(folder)
        warnings = [f"skipped {s['entry']}: {s['reason']}" for s in skipped]
        return self._brush_response(folder, key, textures, library_id if library_id in ids else None,
                                    warnings, members_in_base=True)

    def _manifest(self, entries, found, skipped, ids):
        names = [item.name for item in found if isinstance(item, container.BrushSet)]
        brushes = []
        for position, (key, _, _, folder) in enumerate(entries):
            row = {"member": key, "index": position, "name": None, "era": None, "key_count": None,
                   "shape": {"source": None, "ref": None}, "grain": {"source": None, "ref": None},
                   "dual": folder.sub is not None and folder.sub.archive is not None,
                   "has_thumbnail": folder.thumbnail is not None, "library_id": None}
            try:
                brush = brush_model.decode(folder.archive)
                names_of = container.texture_names(brush.params)
                resolved = container.resolve_textures(folder, brush.params, bundled=self._bundled())
                row.update({"name": brush.name, "era": brush.era, "key_count": brush.key_count,
                            "shape": {"source": resolved["shape"][1], "ref": names_of["shape"]},
                            "grain": {"source": resolved["grain"][1], "ref": names_of["grain"]}})
            except CodecError:
                row["name"] = None
            brush_id = self._id_of(folder)
            row["library_id"] = brush_id if brush_id in ids else None
            brushes.append(row)
        warnings = [w for item in found for w in getattr(item, "warnings", [])]
        return {"kind": "brushset", "name": names[0] if names else None, "brush_count": len(brushes),
                "brushes": brushes, "skipped": skipped, "warnings": warnings[:50]}

    # ── export ───────────────────────────────────────────────────────────────
    def _png_replacement(self, role, supplied, current, warnings, what):
        """The bytes to write for a texture the client replaced: kept as it is
        when it is the base's own file or already 8-bit grey, else converted."""
        data = _b64(supplied, f"{what} png_b64", container.CAPS["entry_bytes"])
        if current is not None and sha256_hex(current) == sha256_hex(data):
            return None
        try:
            info = png_io.png_info(data)
            if info["width"] * info["height"] > png_io.MAX_PIXELS:
                raise ApiError("too_large", f"{what} is over the image size cap", 422)
            if info["color_type"] == 0 and info["bit_depth"] == 8 and info["interlace"] == 0:
                return data
            image = png_io.to_gray8(png_io.read_png(data))
            warnings.append(f"converted: the {role} image was written as 8-bit grey")
            return png_io.write_png(image.width, image.height, "L", image.pixels)
        except CodecError as exc:
            raise ApiError("corrupt_file", f"{what}: {getattr(exc, 'detail', None) or exc}", 422) from None

    def _edit_folder(self, folder, spec, label, *, with_thumbnail, mode):
        """Apply `changes`, `textures` (and a thumbnail) to a copy of `folder`.
        Returns (out folder, record, dropped paths, warnings, rejected, the
        patched Brush)."""
        changes = dict(_object(spec.get("changes"), f"{label}.changes"))
        textures = spec.get("textures")
        if textures is not None and not isinstance(textures, dict):
            raise ApiError("bad_argument", f"{label}.textures must be an object", 400)
        textures = textures or {}
        if set(textures) - {"shape", "grain"}:
            raise ApiError("bad_argument", f"{label}.textures names shape and grain only", 400)
        base = self._decode(folder.archive, label)
        out = folder.copy()
        record = {"name": base.name, "era": base.era, "applied": {}, "rejected": [], "warnings": []}
        warnings, dropped = [], []
        for role, member_path, key in (("shape", container.SHAPE, container.SHAPE_KEY),
                                       ("grain", container.GRAIN, container.GRAIN_KEY)):
            texture = textures.get(role)
            if texture is None or texture == {"keep": True}:
                continue
            if not isinstance(texture, dict) or len(texture) != 1 or not set(texture) <= {"keep", "png_b64", "bundled"}:
                raise ApiError("bad_argument", f"{label}.textures.{role} is {{keep}}, {{png_b64}} or {{bundled}}", 400)
            if "keep" in texture:
                if texture["keep"] is not True:
                    raise ApiError("bad_argument", f"{label}.textures.{role}.keep is true", 400)
                continue
            if "bundled" in texture:
                name = texture["bundled"]
                if not isinstance(name, str) or BUNDLED_NAME.match(name) is None:
                    raise ApiError("bad_argument", f"{label}.textures.{role}.bundled is a texture file name", 400)
                if key in changes and changes[key] != name:
                    raise ApiError("bad_argument", f"{key} is named twice in {label}", 400)
                if key not in base.params:
                    raise ApiError("bad_argument", f"this brush's era has no {key}", 400)
                changes[key] = name
                if out.remove(member_path):
                    dropped.append(member_path)
            else:
                replacement = self._png_replacement(role, texture["png_b64"], folder.get(member_path),
                                                    warnings, f"{label}.textures.{role}")
                if replacement is not None:
                    out.set(member_path, replacement)
                    if base.params.get(key) and key not in changes:
                        changes[key] = None
        patched = base
        if changes:
            patched, report = self.report_patch(base, changes, mode=mode)
            record.update({"applied": report["applied"], "rejected": report["rejected"],
                           "warnings": list(report["warnings"]), "unchanged": report["unchanged"]})
            if not report["ok"]:
                return out, record, dropped, warnings, report["rejected"], patched
        modified = brush_model.is_modified(patched)
        data = brush_model.encode(patched)
        if not modified and data != folder.archive:
            raise ApiError("internal", "an unchanged archive did not export as its source bytes", 500)
        record["name"] = patched.name
        record["era"] = patched.era
        record["state"] = brush_model.export_state(patched)
        record["modified"] = modified
        if modified:
            out.set(container.ARCHIVE, data)
        if with_thumbnail:
            self._thumbnail(out, folder, spec.get("thumbnail"), modified, record, warnings, dropped, label)
        return out, record, dropped, warnings, [], patched

    def _thumbnail(self, out, folder, spec, modified, record, warnings, dropped, label):
        if spec is None:
            spec = {"keep": True}
        if not isinstance(spec, dict) or len(spec) != 1 or not set(spec) <= {"keep", "png_b64", "omit"}:
            raise ApiError("bad_argument", f"{label}.thumbnail is {{keep}}, {{png_b64}} or {{omit}}", 400)
        if "omit" in spec:
            if spec["omit"] is not True:
                raise ApiError("bad_argument", f"{label}.thumbnail.omit is true", 400)
            if out.remove(container.THUMBNAIL):
                dropped.append(container.THUMBNAIL)
            return
        if "png_b64" in spec:
            data = _b64(spec["png_b64"], f"{label}.thumbnail png_b64", container.CAPS["entry_bytes"])
            try:
                image = png_io.read_png(data)
                alpha = png_io.alpha_plane(image) or png_io.to_gray8(image)
                if (image.width, image.height) != png_io.THUMBNAIL_SIZE:
                    raise ApiError("bad_argument", f"{label}.thumbnail must be {png_io.THUMBNAIL_SIZE[0]}x"
                                                   f"{png_io.THUMBNAIL_SIZE[1]} pixels", 400)
                out.set(container.THUMBNAIL, png_io.write_thumbnail(alpha.pixels))
            except CodecError as exc:
                raise ApiError("corrupt_file", f"{label}.thumbnail: {getattr(exc, 'detail', None) or exc}", 422) from None
            return
        if spec.get("keep") is not True:
            raise ApiError("bad_argument", f"{label}.thumbnail.keep is true", 400)
        if modified and folder.thumbnail is not None:
            record["warnings"].append({"key": container.THUMBNAIL, "code": "stale_thumbnail"})
            warnings.append(f"stale_thumbnail: {container.THUMBNAIL} is the one drawn before the change")

    def _export_base(self, spec, label):
        """(BrushFolder, source folder name or None, new-brush flag)."""
        base = spec.get("base")
        if base is None:
            era = spec.get("era", brush_model.NEW_BRUSH_ERA)
            if not isinstance(era, str):
                raise ApiError("bad_argument", f"{label}.era must be text", 400)
            name = (spec.get("changes") or {}).get("name") if isinstance(spec.get("changes"), dict) else None
            try:
                brush = brush_model.new_brush(name if isinstance(name, str) else "Untitled Brush", era=era,
                                              library=self.paths.library)
            except CodecError as exc:
                code = getattr(exc, "code", "")
                if code in ("library_missing", "lfs_pointer", "donor_missing", "donor_mismatch"):
                    raise ApiError("library_missing", f"a new brush is made from a donor brush of the "
                                                      f"library: {getattr(exc, 'detail', None) or exc}", 409,
                                   hint="the originals are needed (git lfs pull)") from None
                raise ApiError("bad_argument", str(exc), 400) from None
            return container.BrushFolder.from_parts(brush_model.encode(brush)), None, True
        if not isinstance(base, dict) or len(base) != 1 or not set(base) <= {"library_id", "members"}:
            raise ApiError("bad_argument", f"{label}.base is {{library_id}}, {{members}} or null", 400)
        if "library_id" in base:
            folder, uuid, _ = self.open_library_folder(check_id(base["library_id"], f"{label}.base.library_id"))
            return folder, uuid, False
        return self._members_folder(base["members"], f"{label}.base"), None, False

    def build_export(self, request):
        """The one builder of an export for every surface (F3 "Export"). Returns
        an `Export`; it writes nothing. `request` is the body of POST /api/export."""
        if not isinstance(request, dict):
            raise ApiError("bad_argument", "the export request must be an object", 400)
        unknown = set(request) - {"format", "name", "dry_run", "brushes", "files", "spacing", "filename"}
        if unknown:
            raise ApiError("bad_argument", f"the export request has no `{sorted(unknown)[0][:30]}`", 400)
        fmt = request.get("format")
        if fmt not in EXPORT_FORMATS:
            raise ApiError("bad_argument", f"format is one of {', '.join(EXPORT_FORMATS)}", 400)
        dry_run = _flag(request.get("dry_run", False), "dry_run")
        name = request.get("name")
        if name is not None:
            name = _text(name, "name", MAX_NAME, 1)
        specs = request.get("brushes")
        if specs is None and fmt == "kit":
            specs = []
        if not isinstance(specs, list) or len(specs) > MAX_EXPORT_BRUSHES:
            raise ApiError("bad_argument", f"brushes is a list of at most {MAX_EXPORT_BRUSHES}", 400)
        if fmt in ("brush", "gbr") and len(specs) != 1:
            raise ApiError("bad_argument", f"format {fmt} takes exactly one brush", 400)
        if fmt == "brushset" and not specs:
            raise ApiError("bad_argument", "a brushset takes at least one brush", 400)
        if fmt == "brushset" and name is None:
            raise ApiError("bad_argument", "a brushset needs a name", 400)
        if fmt == "kit" and len(specs) > 1:
            raise ApiError("bad_argument", "a kit takes at most one brush", 400)
        outputs, rejected_all, used = [], [], set()
        for number, spec in enumerate(specs):
            label = f"brushes[{number}]"
            if not isinstance(spec, dict) or set(spec) - {"base", "changes", "mode", "textures", "thumbnail",
                                                          "sub", "uuid", "era"}:
                raise ApiError("bad_argument", f"{label} has an unknown field", 400)
            mode = spec.get("mode", "strict")
            if mode not in brush_model.MODES:
                raise ApiError("bad_argument", f"{label}.mode is strict or clamp", 400)
            folder, source_uuid, is_new = self._export_base(spec, label)
            out, record, dropped, warnings, rejected, patched = self._edit_folder(
                folder, spec, label, with_thumbnail=True, mode=mode)
            sub_spec = spec.get("sub")
            if sub_spec is not None:
                if not isinstance(sub_spec, dict) or set(sub_spec) - {"changes", "textures"}:
                    raise ApiError("bad_argument", f"{label}.sub is {{changes, textures}} or null", 400)
                inner = folder.sub
                if inner is None or inner.archive is None:
                    raise ApiError("bad_argument", f"{label} has no Sub01/ to change", 400)
                sub_out, sub_record, sub_dropped, sub_warnings, sub_rejected, _ = self._edit_folder(
                    inner, sub_spec, f"{label}.sub", with_thumbnail=False, mode=mode)
                rejected = rejected + [dict(item, key=f"sub.{item['key']}") for item in sub_rejected]
                warnings += [f"sub: {text}" for text in sub_warnings]
                record["sub"] = {"applied": sub_record["applied"], "rejected": sub_record["rejected"],
                                 "warnings": sub_record["warnings"]}
                if not rejected:
                    old = {m.path for m in inner.members}
                    for member_ in sub_out.members:
                        out.set(f"{container.SUB}/{member_.path}", member_.data)
                    for path in old - {m.path for m in sub_out.members}:
                        out.remove(f"{container.SUB}/{path}")
                        dropped.append(f"{container.SUB}/{path}")
                    if sub_record.get("modified"):
                        record["modified"] = True
            if rejected:
                rejected_all.append({"brush": number, "name": record.get("name"), "rejected": rejected})
                continue
            if folder.reset is not None:
                warnings.append("Reset/ is kept verbatim")
            reencoded = {container.ARCHIVE}
            if sub_spec is not None:
                reencoded.add(f"{container.SUB}/{container.ARCHIVE}")
            plan = container.member_plan(None if is_new else folder, out, reencoded=reencoded, drop=dropped)
            folder_name = spec.get("uuid")
            if folder_name is not None:
                if not isinstance(folder_name, str) or UUID_NAME.match(folder_name) is None:
                    raise ApiError("bad_argument", f"{label}.uuid is a UUID", 400)
                folder_name = folder_name.upper()
            elif source_uuid and not record.get("modified") and source_uuid not in used:
                folder_name = source_uuid
            else:
                folder_name = container.new_uuid()
            if folder_name in used:
                raise ApiError("bad_argument", f"two brushes of the export are called {folder_name}", 400)
            used.add(folder_name)
            record["uuid"] = folder_name if fmt == "brushset" else None
            outputs.append((folder_name, out, record, plan, warnings, patched))
        if rejected_all:
            raise ApiError("invalid_settings", "some changes were rejected; nothing was built", 422,
                           hint="fix the rejected keys, or send mode \"clamp\" for limits",
                           data={"rejected": [item for entry in rejected_all for item in entry["rejected"]],
                                 "brushes": rejected_all})
        try:
            filename, data, members = self._assemble(fmt, name, request, outputs)
        except ContainerError as exc:
            raise codec_error(exc, "the export") from None
        except zip_writer.ZipWriteError as exc:
            raise ApiError("bad_argument", str(exc), 400) from None
        warnings = [text for entry in outputs for text in entry[4]]
        report = {"filename": filename, "size": len(data), "sha256": sha256_hex(data), "members": members,
                  "brushes": [{"name": entry[2].get("name"), "uuid": entry[2].get("uuid"),
                               "era": entry[2].get("era"), "applied": entry[2].get("applied", {}),
                               "rejected": entry[2].get("rejected", []),
                               "warnings": entry[2].get("warnings", [])} for entry in outputs],
                  "warnings": warnings}
        return Export(filename, data, report, dry_run)

    def _assemble(self, fmt, name, request, outputs):
        """(file name, bytes, member list) of the finished export."""
        if fmt == "brush":
            _, out, record, plan, _, _ = outputs[0]
            return container.safe_filename(record["name"]) + ".brush", container.write_brush(out), plan
        if fmt == "brushset":
            brush_set = container.BrushSet(name, [(uuid, out) for uuid, out, _, _, _, _ in outputs])
            members = []
            for uuid, _, _, plan, _, _ in outputs:
                members += [dict(item, path=f"{uuid}/{item['path']}") for item in plan]
            plist = container.plist_bytes(brush_set)
            members.append({"path": container.SET_PLIST, "size": len(plist), "state": "re-encoded"})
            return container.safe_filename(name) + ".brushset", container.write_brushset(brush_set), members
        if fmt == "gbr":
            _, out, record, _, _, patched = outputs[0]
            data, source = container.resolve_textures(out, patched.params, bundled=self._bundled())["shape"]
            if data is None:
                raise ApiError("bad_argument", "this brush's shape is an image inside the drawing app; there "
                                               "is no image here to write as a .gbr", 400,
                               hint="supply textures.shape.png_b64")
            spacing = request.get("spacing", gbr.SPACING_DEFAULT)
            try:
                image = png_io.read_png(data)
                inverted = brush_model.scalar(patched.params.get("shapeInverted"), False) is True
                body = gbr.from_image(image, inverted=inverted, name=record["name"] or gbr.DEFAULT_NAME,
                                      spacing=spacing)
            except CodecError as exc:
                raise ApiError("bad_argument", getattr(exc, "detail", None) or str(exc), 400) from None
            filename = container.safe_filename(record["name"]) + ".gbr"
            return filename, body, [{"path": filename, "size": len(body), "state": "replaced"}]
        files = request.get("files")
        if not isinstance(files, list) or not 1 <= len(files) <= MAX_KIT_FILES:
            raise ApiError("bad_argument", f"a kit takes 1 to {MAX_KIT_FILES} files", 400)
        entries, total = [], 0
        for item in files:
            if not isinstance(item, dict) or set(item) != {"path", "b64"}:
                raise ApiError("bad_argument", "each kit file is {path, b64}", 400)
            path = _text(item["path"], "a kit file path", 100, 1)
            if KIT_ENTRY.match(path) is None:
                raise ApiError("bad_argument", f"a kit holds gimp/*.gbr, ink/*.png, mask/*.png, "
                                               f"stroke-preview.png and brush-recipe.md, not {path[:60]!r}", 400)
            content = _b64(item["b64"], f"kit file {path}", container.CAPS["entry_bytes"])
            total += len(content)
            if total > 128 * MIB:
                raise ApiError("too_large", "the kit files together are over 128 MiB", 413)
            if path.endswith(".png") and not content.startswith(png_io.SIGNATURE):
                raise ApiError("bad_argument", f"{path} is not a PNG", 400)
            if path.endswith(".gbr"):
                try:
                    gbr.read_gbr(content)
                except CodecError as exc:
                    raise ApiError("bad_argument", f"{path}: {getattr(exc, 'detail', None) or exc}", 400) from None
            entries.append((path, content))
        members = [{"path": path, "size": len(content), "state": "replaced"} for path, content in entries]
        if outputs:
            _, out, record, _, _, _ = outputs[0]
            brush_name = container.safe_filename(record["name"]) + ".brush"
            brush_bytes = container.write_brush(out)
            entries.append((brush_name, brush_bytes))
            members.append({"path": brush_name, "size": len(brush_bytes), "state": "re-encoded"})
        base_name = container.safe_filename(name or (outputs[0][2]["name"] if outputs else "kit"))
        return base_name + "-kit.zip", zip_writer.write_zip(entries), members

    def write_export(self, filename, data):
        """Put a finished export in the export folder (F12). Only when the
        service was made with one."""
        if self.export_dir is None:
            raise ApiError("export_disabled", "this server was not started with an export folder", 403,
                           hint="start it with --export-dir DIR")
        return write_export(self.export_dir, filename, data)

    def export_brush(self, base_id, changes=None, name=None, confirm=False):
        """MCP `export_brush`: a library brush, changed by `changes`, as a
        `.brush` in the export folder. `confirm: false` is a dry run."""
        if self.export_dir is None:
            raise ApiError("export_disabled", "this server was not started with an export folder", 403,
                           hint="start it with --export-dir DIR")
        base_id = check_id(base_id, "base_id")
        _flag(confirm, "confirm")
        changes = dict(_object(changes, "changes"))
        if name is not None:
            changes["name"] = _text(name, "name", MAX_NAME, 1)
        export = self.build_export({"format": "brush", "dry_run": not confirm,
                                    "brushes": [{"base": {"library_id": base_id}, "changes": changes}]})
        stem = export.filename[:-len(".brush")]
        filename = f"{stem}-{base_id[2:10]}.brush"
        payload = {"dry_run": not confirm, "would_write" if not confirm else "written": filename,
                   "size": export.report["size"], "sha256": export.report["sha256"],
                   "members": export.report["members"],
                   "validation": [{"name": b["name"], "applied": b["applied"], "rejected": b["rejected"],
                                   "warnings": b["warnings"]} for b in export.report["brushes"]],
                   "warnings": export.report["warnings"]}
        if confirm:
            self.write_export(filename, export.data)
        return payload
