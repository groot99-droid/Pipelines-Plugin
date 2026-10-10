"""What every brushes script shares: where the data is, the exit codes, the
console, and one safe way to write a file.

Roots (brushes/docs/CONTRACTS.md, F2). Each of the four folders a script may be
pointed at is chosen the same way, in this order:

    1. the flag           --root  --library  --catalog  --vault
    2. the environment    ROSW_BRUSHES_ROOT  _LIBRARY  _CATALOG  _VAULT
    3. the default        the brushes/ folder this file sits in, and
                          library/, catalog/ and vault/ inside the root

The search index has no flag of its own here: ROSW_BRUSHES_INDEX, else
<vault>/tools/rag_index/index.json. _Previews/ and _BrushTags/ sit in the
vault.

schema/ and app/ are not data and do not move with the root: they are part of
the code, and always the folders beside pipeline/ (TOOL_ROOT). A script pointed
at another data root, as every test is, still reads the one schema and serves
the one app.

resolve_paths only works out names. It creates nothing and does not check that
a folder exists; a script that needs one says so itself and exits 2.

The tools under vault/tools/ do not import this module (they must run from a
vault copied on its own), but they read the same environment names, and a test
keeps the two spellings equal.

Standard library only. Not a command.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import NamedTuple

# The brushes/ folder: this file is brushes/pipeline/brush_common.py.
TOOL_ROOT = Path(__file__).resolve().parents[1]

EXIT_OK, EXIT_REFUSED, EXIT_USAGE = 0, 1, 2

ENV_ROOT = "ROSW_BRUSHES_ROOT"
ENV_LIBRARY = "ROSW_BRUSHES_LIBRARY"
ENV_CATALOG = "ROSW_BRUSHES_CATALOG"
ENV_VAULT = "ROSW_BRUSHES_VAULT"
ENV_INDEX = "ROSW_BRUSHES_INDEX"
ENV_NAMES = {"root": ENV_ROOT, "library": ENV_LIBRARY, "catalog": ENV_CATALOG,
             "vault": ENV_VAULT, "index": ENV_INDEX}

FLAGS = {"root": "--root", "library": "--library", "catalog": "--catalog", "vault": "--vault"}
FLAG_HELP = {
    "root": "the data root that holds library/, catalog/ and vault/ "
            "(default: the brushes/ folder that holds this code)",
    "library": "the folder of original brush files (default: <root>/library)",
    "catalog": "the generated catalog folder (default: <root>/catalog)",
    "vault": "the brush vault (default: <root>/vault)",
}

# The one port the app server listens on. A busy port is an exit 2, never a
# different port: the browser keeps presets per origin.
APP_PORT = 8719


class Paths(NamedTuple):
    """Every folder and file a script may need, as absolute paths."""

    root: Path
    schema: Path
    catalog: Path
    vault: Path
    previews: Path
    tags: Path
    vocabulary: Path
    index: Path
    library: Path
    app: Path


def _absolute(value):
    return Path(os.path.expanduser(str(value))).resolve()


def _pick(flag_value, env_name, default):
    """flag > environment > default. An empty string counts as not given."""
    if flag_value is not None and str(flag_value).strip():
        return _absolute(flag_value)
    from_env = os.environ.get(env_name, "")
    if from_env.strip():
        return _absolute(from_env)
    return default


def resolve_paths(root=None, library=None, catalog=None, vault=None):
    """Where everything is. Arguments are what the flags were given, or None.

    `root` moves the data (library, catalog, vault). `schema` and `app` are
    code assets and never move: they are TOOL_ROOT's.
    """
    root_path = _pick(root, ENV_ROOT, TOOL_ROOT)
    vault_path = _pick(vault, ENV_VAULT, root_path / "vault")
    tags = vault_path / "_BrushTags"
    return Paths(
        root=root_path,
        schema=TOOL_ROOT / "schema",
        catalog=_pick(catalog, ENV_CATALOG, root_path / "catalog"),
        vault=vault_path,
        previews=vault_path / "_Previews",
        tags=tags,
        vocabulary=tags / "vocabulary.yaml",
        index=_pick(None, ENV_INDEX, vault_path / "tools" / "rag_index" / "index.json"),
        library=_pick(library, ENV_LIBRARY, root_path / "library"),
        app=TOOL_ROOT / "app",
    )


def add_path_arguments(parser, names=("root", "library", "catalog", "vault")):
    """Give an argparse parser the root flags, spelled as every script spells them."""
    for name in names:
        parser.add_argument(FLAGS[name], metavar="DIR", default=None, help=FLAG_HELP[name])
    return parser


def paths_from_args(args):
    """resolve_paths from parsed arguments; a flag the parser lacks is not given."""
    return resolve_paths(*(getattr(args, name, None) for name in ("root", "library", "catalog", "vault")))


def stored_path(path, base):
    """A path as it is written into a file: POSIX, relative to `base`.

    Preview paths and note paths are stored relative to the vault, a container
    path relative to the library. No absolute path is ever written.
    """
    return Path(path).resolve().relative_to(Path(base).resolve()).as_posix()


# ── console ──────────────────────────────────────────────────────────────────

def open_console():
    """Make stdout and stderr UTF-8. A legacy Windows console cannot encode every
    character a brush name can hold, and `python -I` ignores PYTHONIOENCODING."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


# ── files ────────────────────────────────────────────────────────────────────

def read_text(path):
    """A file as UTF-8 text, exactly as stored (no newline translation)."""
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _replace_into(path, write):
    """Write beside the target, then swap: a failure leaves the old file whole."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        write(tmp)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()
    return path


def write_text(path, text):
    """Write text as UTF-8 through `<name>.tmp` and os.replace.

    A `\\n` is written as one byte on every platform. Nothing else is touched,
    so text that already holds `\\r\\n` keeps it.
    """
    def write(tmp):
        with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    return _replace_into(path, write)


def write_bytes(path, data):
    """Write bytes through `<name>.tmp` and os.replace."""
    def write(tmp):
        with open(tmp, "wb") as handle:
            handle.write(data)
    return _replace_into(path, write)


def json_text(value):
    """The one spelling of generated JSON: sorted keys, two-space indent, real
    characters rather than escapes, a final newline, and no NaN or Infinity.
    Two builds of the same data are then the same bytes."""
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"


def write_json(path, value):
    return write_text(path, json_text(value))
