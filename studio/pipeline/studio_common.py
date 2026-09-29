"""What studio_run.py and content_md.py share: the spec, the folders it points
at, run state, the rule for what counts as a note, and how a note and an
attestation are read.

Not a command. Requires pyyaml.
"""

import copy
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SPEC_PATH = HERE / "spec.yaml"

EXIT_OK, EXIT_REFUSED, EXIT_USAGE = 0, 1, 2

# The name of a note in a wikilink: up to an alias, a heading, or the
# backslash that escapes an alias's pipe inside a table.
WIKILINK_RE = re.compile(r"\[\[([^\]|#\\]+)")

# One part of a note's path. Letters, digits, space, dot, underscore, hyphen;
# it starts with a letter or digit and does not end in a dot or a space, which
# Windows would silently drop and so make two names one file.
PATH_PART_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9 ._-]*[A-Za-z0-9_-])?$")
WINDOWS_DEVICES = {"con", "prn", "aux", "nul"} | {f"{name}{n}" for name in ("com", "lpt")
                                                   for n in range(1, 10)}

ATTESTATION_COLUMNS = ("constraint", "gate", "level", "source", "state")


class Refused(Exception):
    """A rule in the spec says no."""


class Usage(Exception):
    """The command, the spec or the run is wrong."""


# ── files and time ───────────────────────────────────────────────────────────

def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def write_text(path, text):
    """Write through a temporary file so a failure leaves the old one whole."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8", newline="\n")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def normalize(text):
    """A note as it is stored: LF line endings, one newline at the end."""
    return text.replace("\r\n", "\n").rstrip("\n") + "\n"


def squeeze(text):
    """Text for comparing: one space between words, case folded."""
    return " ".join(str(text).split()).casefold()


def now():
    return datetime.now(timezone.utc)


def stamp(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:48].strip("-") or "run"


def open_console():
    """A legacy Windows console cannot encode every character a note can hold."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


# ── the spec ─────────────────────────────────────────────────────────────────

YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
_SPECS = {}


def load_yaml(text):
    """Parse YAML. Raises ValueError for anything that is not valid.

    PyYAML raises its own error for bad syntax and a plain ValueError for a
    value it cannot build, such as the date 2026-13-45. Both are the same to
    a caller: the text does not parse.
    """
    try:
        return yaml.load(text, Loader=YAML_LOADER)
    except yaml.YAMLError as err:
        raise ValueError(" ".join(str(err).split())) from None


def load_spec(path=SPEC_PATH):
    path = Path(path)
    try:
        facts = path.stat()
        key = (str(path.resolve()), facts.st_mtime_ns, facts.st_size)
        if key not in _SPECS:
            _SPECS.clear()
            _SPECS[key] = load_yaml(read_text(path))
        spec = copy.deepcopy(_SPECS[key])
    except FileNotFoundError:
        raise Usage(f"no spec at {path}")
    except (ValueError, UnicodeDecodeError) as err:
        raise Usage(f"{path} does not parse: {' '.join(str(err).split())}")
    if not isinstance(spec, dict):
        raise Usage(f"{path} is not a mapping")
    for key in ("version", "vault_root", "context_root", "runs_root",
                "content_md", "gates", "ladder", "pipelines", "stages"):
        if key not in spec:
            raise Usage(f"{path} has no `{key}:` block")
    return spec


class Env:
    """The spec and the three folders it points at.

    The folders can be overridden, by argument or by environment variable, so
    the tests never touch the real vault or the real run folder.
    """

    def __init__(self, spec_path=SPEC_PATH, runs_dir=None, vault_dir=None, context_dir=None):
        self.spec_path = Path(spec_path)
        self.spec = load_spec(self.spec_path)
        base = self.spec_path.parent

        def pick(given, variable, declared):
            chosen = given or os.environ.get(variable)
            return Path(chosen).resolve() if chosen else (base / declared).resolve()

        self.runs = pick(runs_dir, "STUDIO_RUNS_DIR", self.spec["runs_root"])
        self.vault = pick(vault_dir, "STUDIO_VAULT_DIR", self.spec["vault_root"])
        self.context = pick(context_dir, "STUDIO_CONTEXT_DIR", self.spec["context_root"])

    @property
    def stages(self):
        return self.spec["stages"]

    def pipeline(self, name):
        try:
            return self.spec["pipelines"][name]
        except KeyError:
            known = ", ".join(sorted(self.spec["pipelines"]))
            raise Usage(f"no pipeline `{name}` in the spec. Declared: {known}")

    def run_dir(self, run_id):
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,80}", run_id or ""):
            raise Usage(f"`{run_id}` is not a run id. Lower-case letters, digits and hyphens.")
        return self.runs / run_id


def stage_outputs(stage):
    if "output_files" in stage:
        return list(stage["output_files"])
    if "output_file" in stage:
        return [stage["output_file"]]
    return []


# ── the vault ────────────────────────────────────────────────────────────────

def reserved_names(env):
    return {name.casefold() for name in env.spec["content_md"].get("reserved_names", [])}


def resolve_note(env, relative, placing=False):
    """A vault-relative note path, checked, as an absolute path.

    `placing` is for a path a run is about to write to. It must then sit where
    SCHEMA.md puts a note: <project>/<kind>/<slug>.md. A note the author placed
    by hand is only read, so it is held to the looser rule.
    """
    text = str(relative).replace("\\", "/").strip()
    if not text:
        raise Usage("the note path is empty")
    if text.startswith("/") or re.match(r"^[A-Za-z]:", text):
        raise Usage(f"`{relative}` is absolute. Give the path inside the vault.")
    parts = text.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise Usage(f"`{relative}` is not a plain path inside the vault")
    for part in parts[:-1]:
        if part.startswith(("_", ".")):
            raise Usage(f"`{part}/` is not a folder for Content MDs")
    for part in parts:
        if not PATH_PART_RE.match(part):
            raise Usage(f"`{part}` in `{relative}` is not a name a note path may use. "
                        "Letters, digits, spaces, dots, underscores and hyphens; "
                        "no dot or space at the end.")
        if part.split(".")[0].casefold() in WINDOWS_DEVICES:
            raise Usage(f"`{part}` is a device name on Windows")
    if not parts[-1].casefold().endswith(".md"):
        raise Usage(f"`{relative}` is not a .md file")
    if parts[-1].casefold() in reserved_names(env):
        raise Usage(f"`{parts[-1]}` is reserved. It is never a Content MD.")
    if placing:
        kinds = env.spec["content_md"]["kinds"]
        if len(parts) != 3 or parts[1] not in kinds:
            raise Usage(f"`{relative}` is not where a note goes. SCHEMA.md places it at "
                        "<project>/<kind>/<slug>.md, or one-offs/<kind>/<slug>.md, "
                        f"with <kind> one of: {', '.join(kinds)}")
    path = (env.vault / Path(*parts)).resolve()
    if env.vault not in path.parents:
        raise Usage(f"`{relative}` leaves the vault")
    if path.exists() and not path.is_file():
        raise Usage(f"`{relative}` is a folder")
    return path


def vault_notes(env):
    """Every file in the vault that may be a Content MD.

    The same rule the path check applies: nothing under a folder whose name
    starts with `_` or `.`, and none of the reserved names in any case.
    """
    if not env.vault.is_dir():
        return []
    reserved = reserved_names(env)
    found = []
    for path in sorted(env.vault.rglob("*.md")):
        relative = path.relative_to(env.vault)
        if any(part.startswith(("_", ".")) for part in relative.parts[:-1]):
            continue
        if relative.name.casefold() in reserved:
            continue
        found.append(path)
    return found


def split_note(text):
    """(frontmatter text, body) or (None, text) when there is no frontmatter."""
    text = text.replace("\r\n", "\n").lstrip("﻿")
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 3)
    if end == -1:
        if text.endswith("\n---"):
            return text[4:-4], ""
        return None, text
    return text[4:end], text[end + 5:]


def front_matter(text):
    """The frontmatter of a note as a dict, or {} when it has none or is broken."""
    raw, _ = split_note(text)
    if raw is None:
        return {}
    try:
        data = load_yaml(raw)
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def outside_fences(text):
    """(line number, line) for each line that is not inside a code fence."""
    fence = None
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.lstrip()
        opener = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence:
            if (opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= len(fence)
                    and not stripped[len(opener.group(1)):].strip()):
                fence = None
            continue
        if opener:
            fence = opener.group(1)
            continue
        yield number, line


def sections(body):
    """[(title, text)] for each `## ` heading outside a code fence, in order."""
    lines = body.split("\n")
    starts = [(number, line[3:].strip()) for number, line in outside_fences(body)
              if line.startswith("## ")]
    found = []
    for index, (number, title) in enumerate(starts):
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) else len(lines)
        found.append((title, "\n".join(lines[number:end])))
    return found


def note_index(env):
    """Every Content MD in the vault, and how a wikilink finds one.

    Obsidian resolves [[name]] by file name, so that is the first key. A note's
    id is the second, because the ladder cites a note by id.
    """
    notes, by_name = [], {}
    for path in vault_notes(env):
        text = read_text(path)
        front = front_matter(text)
        if front.get("type") != env.spec["content_md"]["type"]:
            continue
        brand = front.get("context_brand")
        entry = {
            "path": path.relative_to(env.vault).as_posix(),
            "file": path,
            "id": front.get("id"),
            "kind": front.get("kind"),
            "status": front.get("status"),
            "context_brand": brand if isinstance(brand, list) else [],
        }
        notes.append(entry)
        for key in {path.stem.casefold(), str(front.get("id") or "").casefold()} - {""}:
            by_name.setdefault(key, []).append(entry)
    return notes, by_name


def cited_notes(text):
    """The distinct note names a piece of text links to, in order."""
    seen, names = set(), []
    for name in WIKILINK_RE.findall(text):
        key = name.strip().casefold()
        if key and key not in seen:
            seen.add(key)
            names.append(name.strip())
    return names


# ── the attestation ──────────────────────────────────────────────────────────

def table_cells(line):
    """The cells of one table row. A pipe inside a cell is written `\\|`."""
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|") and not inner.endswith("\\|"):
        inner = inner[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", inner)]


def attestation_rows(text):
    """The rows of the context-resolution table, each a dict keyed by column.

    The table is the first one, outside a code fence, whose header names
    Constraint, Gate, Level, Source and State.
    """
    lines = [line for _, line in outside_fences(text.replace("\r\n", "\n"))]
    wanted = ", ".join(name.capitalize() for name in ATTESTATION_COLUMNS)
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        header = [cell.casefold() for cell in table_cells(line)]
        if sorted(header) != sorted(ATTESTATION_COLUMNS):
            continue
        rows = []
        for number, row in enumerate(lines[index + 1:]):
            if not row.lstrip().startswith("|"):
                break
            cells = table_cells(row)
            if number == 0 and all(re.fullmatch(r":?-{1,}:?", cell) for cell in cells):
                continue
            if len(cells) != len(header):
                raise Refused(f"a row of the attestation has {len(cells)} cells and the table has "
                              f"{len(header)} columns. Write a pipe inside a cell as `\\|`:\n"
                              f"    {row.strip()}")
            entry = dict(zip(header, cells))
            entry["row"] = row.strip()
            rows.append(entry)
        if not rows:
            raise Refused("the context-resolution table in the attestation has no rows")
        return rows
    raise Refused("the attestation has no context-resolution table. "
                  f"It needs one with the columns: {wanted}")


def level_of(row):
    """L0, L1, L2, L3 or STATED, from a cell such as `L0 AUTHORED`; else None."""
    words = row["level"].casefold().replace("-", " ").split()
    for word in words:
        if word in ("l0", "l1", "l2", "l3"):
            return word.upper()
    if "stated" in words:
        return "STATED"
    names = {"authored": "L0", "recalled": "L1", "derived": "L2", "unresolved": "L3"}
    for word in words:
        if word in names:
            return names[word]
    return None


# ── run state ────────────────────────────────────────────────────────────────

STATE_KEYS = ("run_id", "pipeline", "title", "status", "completed_stages", "next_stage_index")


def load_state(env, run_id):
    path = env.run_dir(run_id) / "state.json"
    if not path.is_file():
        raise Usage(f"no run `{run_id}` under {env.runs}")
    try:
        state = json.loads(read_text(path))
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        raise Usage(f"{path} does not parse: {err}. It is written only by studio_run.py; "
                    "if it was edited by hand, start a new run.")
    missing = [key for key in STATE_KEYS if not isinstance(state, dict) or key not in state]
    if missing:
        raise Usage(f"{path} has no {', '.join(missing)}")
    env.pipeline(state["pipeline"])
    return state


def all_states(env):
    """The state of every run that can be read. A broken one is skipped."""
    states = []
    if env.runs.is_dir():
        for path in sorted(env.runs.glob("*/state.json")):
            try:
                states.append(load_state(env, path.parent.name))
            except Usage:
                continue
    return states


def log_event(state, event, detail=""):
    state.setdefault("events", []).append({"at": stamp(now()), "event": event, "detail": detail})


def save_state(env, state):
    state["updated"] = stamp(now())
    write_text(env.run_dir(state["run_id"]) / "state.json",
               json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def current_stage(env, state):
    index = state["next_stage_index"]
    return env.stages[index] if 0 <= index < len(env.stages) else None


def latest_confirmation(state, what):
    matches = [c for c in state.get("confirmations", []) if c["what"] == what]
    return matches[-1] if matches else None
