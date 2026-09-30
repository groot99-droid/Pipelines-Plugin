"""What studio_run.py and content_md.py share: the spec, the folders it points
at, run state, the rule for what counts as a note, and how a note and an
attestation are read.

Not a command. Requires pyyaml.
"""

import copy
import json
import ntpath
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
PATH_PART_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9 ._-]*[A-Za-z0-9_-])?")
PATH_PART_MAX = 100
WINDOWS_DEVICES = {"con", "prn", "aux", "nul"} | {f"{name}{n}" for name in ("com", "lpt")
                                                   for n in range(1, 10)}

ATTESTATION_COLUMNS = ("constraint", "gate", "level", "source", "state")

# A code fence: up to three spaces, then three or more backticks or tildes.
FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
# A table line, as a reader sees one. Four spaces in, it is code.
TABLE_LINE_RE = re.compile(r"^ {0,3}\|")
# A list item, with its marker.
BULLET_RE = re.compile(r"^\s*[-*+] ")
# Struck-out text, which a reader sees crossed through.
STRUCK_RE = re.compile(r"~~.*?~~|<(s|del|strike)>.*?</\1>", re.S | re.I)


class Refused(Exception):
    """A rule in the spec says no."""


class Usage(Exception):
    """The command, the spec or the run is wrong."""


# ── files and time ───────────────────────────────────────────────────────────

def read_text(path):
    """A file as UTF-8 text. Anything else is a usage error that names it."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise Usage(f"{path} is not UTF-8 text. Save it as UTF-8 and try again.") from None


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


def warn(message):
    print(f"warning   {message}", file=sys.stderr)


def normalize(text):
    """A note as it is stored: LF line endings, one newline at the end."""
    return text.replace("\r\n", "\n").rstrip("\n") + "\n"


def squeeze(text):
    """Text for comparing: one space between words, case folded."""
    return " ".join(str(text).split()).casefold()


def unstruck(text):
    """The text with anything struck out removed."""
    return STRUCK_RE.sub(" ", text)


def now():
    return datetime.now(timezone.utc)


def stamp(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_stamp(text):
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:48].strip("-") or "run"


def open_console():
    """A legacy Windows console cannot encode every character a note can hold."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


# ── the spec ─────────────────────────────────────────────────────────────────

class UniqueKeyLoader(getattr(yaml, "CSafeLoader", yaml.SafeLoader)):
    """The safe loader, refusing a key written twice in one mapping.

    Plain YAML keeps the last value and says nothing, so a field written twice
    in a note's frontmatter would change silently.
    """

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            seen = set()
            for key_node, _ in node.value:
                if key_node.tag == "tag:yaml.org,2002:merge":
                    continue
                key = self.construct_object(key_node, deep=True)
                try:
                    repeated = key in seen
                    seen.add(key)
                except TypeError:
                    continue
                if repeated:
                    raise yaml.constructor.ConstructorError(
                        None, None, f"`{key}` is written twice", key_node.start_mark)
        return super().construct_mapping(node, deep=deep)


_SPECS = {}


def load_yaml(text):
    """Parse YAML. Raises ValueError for anything that is not valid.

    PyYAML raises its own error for bad syntax and a plain ValueError for a
    value it cannot build, such as the date 2026-13-45. Both are the same to
    a caller: the text does not parse.
    """
    try:
        return yaml.load(text, Loader=UniqueKeyLoader)
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
    except ValueError as err:
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

    def __init__(self, spec_path=SPEC_PATH, runs_dir=None, vault_dir=None, context_dir=None,
                 assets_dir=None):
        self.spec_path = Path(spec_path)
        self.spec = load_spec(self.spec_path)
        base = self.spec_path.parent

        def pick(given, variable, declared):
            chosen = given or os.environ.get(variable)
            return Path(chosen).resolve() if chosen else (base / declared).resolve()

        self.runs = pick(runs_dir, "STUDIO_RUNS_DIR", self.spec["runs_root"])
        self.vault = pick(vault_dir, "STUDIO_VAULT_DIR", self.spec["vault_root"])
        self.context = pick(context_dir, "STUDIO_CONTEXT_DIR", self.spec["context_root"])
        self.assets = pick(assets_dir, "STUDIO_ASSETS_DIR", self.spec.get("assets_root", "../assets"))

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


def attesting_stage(stage):
    """True for the stage whose output is the attestation."""
    return "levels_are_backed" in stage.get("checks", [])


def stage_checks(env, state, stage):
    """The checks a stage runs for this run: the stage's own, then any its
    pipeline adds for that stage under `checks:`."""
    extra = (env.pipeline(state["pipeline"]).get("checks") or {}).get(stage["id"], [])
    return list(stage.get("checks", [])) + list(extra)


# ── the brand gates ──────────────────────────────────────────────────────────

# A gate's sections: `## N. Title`. Section 0 is its provenance, a section
# titled Unresolved is what it declares it does not answer, and every other
# numbered section is an answer. The carried gates also hold a routing glossary,
# which answers nothing.
GATE_HEADING_RE = re.compile(r"^## (\d+)\. (.+?)\s*$")
NOT_ANSWERS = ("provenance", "unresolved", "routing glossary")


def gate_path(env, name):
    return env.context / env.spec["gates"][name]["file"]


def gate_sections(env, name, text=None):
    """What a gate answers and what it declares it does not, read from its own
    headings: {"answers": [...], "unresolved": [...]}, each item a section
    number and a topic. None when the gate has no file: it is not authored."""
    if text is None:
        path = gate_path(env, name)
        if not path.is_file():
            return None
        text = read_text(path)
    lines = [line for _, line in outside_fences(text.replace("\r\n", "\n"))]
    headings = [(index, GATE_HEADING_RE.match(line)) for index, line in enumerate(lines)]
    headings = [(index, match.group(1), match.group(2)) for index, match in headings if match]
    found = {"answers": [], "unresolved": []}
    for position, (index, number, title) in enumerate(headings):
        folded = title.strip("*_ ").casefold()
        if folded == "unresolved":
            end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
            found["unresolved"].append({"section": number, "topic": gap_topic(lines[index + 1:end])})
        elif number != "0" and folded not in NOT_ANSWERS:
            found["answers"].append({"section": number, "topic": title.strip()})
    return found


def gap_topic(lines):
    """What an Unresolved section leaves open: its bullets, or its first sentence."""
    items = [line.strip()[2:].strip() for line in lines if re.match(r"^\s*[-*+] ", line)]
    text = "; ".join(items) if items else " ".join(" ".join(lines).split())
    if not items:
        text = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
    return re.sub(r"[*_`]", "", text)[:160]


# ── the vault ────────────────────────────────────────────────────────────────

def reserved_names(env):
    return {name.casefold() for name in env.spec["content_md"].get("reserved_names", [])}


def artifact_roles(env):
    return list(env.spec["content_md"].get("artifact_roles", []))


def artifact_path(env, relative):
    """The file an artifact's path names, under the assets folder, or a
    sentence saying why the path is not one. A path is relative to the assets
    folder, forward slashes, no `..`, no scheme, no drive."""
    if not isinstance(relative, str) or not relative.strip():
        return None, "an artifact's `path` is text"
    text = relative.strip().replace("\\", "/")
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", text) or text.startswith("//"):
        return None, f"`{relative}` is a link. An artifact is a file under the assets folder, never a link"
    if text.startswith("/") or ".." in text.split("/"):
        return None, f"`{relative}` leaves the assets folder"
    parts = [part for part in text.split("/") if part]
    if not parts or any(not PATH_PART_RE.fullmatch(part) for part in parts):
        return None, f"`{relative}` is not a path of plain names (letters, digits, space, dot, _ and -)"
    return env.assets.joinpath(*parts), None


def windows_reserved(part):
    """A name Windows treats as a device, or folds onto another name."""
    if part.split(".")[0].rstrip(" ").casefold() in WINDOWS_DEVICES:
        return True
    return bool(getattr(ntpath, "isreserved", lambda name: False)(part))


def resolve_note(env, relative, placing=False, kind=None):
    """A vault-relative note path, checked, as an absolute path.

    `placing` is for a path a run is about to write to. It must then sit where
    SCHEMA.md puts a note: <project>/<kind>/<slug>.md, and with `kind` given,
    in that kind's folder. A note the author placed by hand is only read, so it
    is held to the looser rule.
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
    reserved = reserved_names(env)
    for part in parts:
        if not PATH_PART_RE.fullmatch(part):
            raise Usage(f"`{part}` in `{relative}` is not a name a note path may use. "
                        "Letters, digits, spaces, dots, underscores and hyphens; "
                        "no dot or space at the end.")
        if len(part) > PATH_PART_MAX:
            raise Usage(f"a part of `{relative}` is {len(part)} characters long. "
                        f"Keep each under {PATH_PART_MAX + 1}.")
        if windows_reserved(part):
            raise Usage(f"`{part}` is a device name on Windows")
        if part.casefold() in reserved:
            raise Usage(f"`{part}` is reserved. It is never a Content MD, nor a folder of them.")
    if not parts[-1].casefold().endswith(".md"):
        raise Usage(f"`{relative}` is not a .md file")
    if placing:
        kinds = env.spec["content_md"]["kinds"]
        if len(parts) != 3 or parts[1] not in kinds:
            raise Usage(f"`{relative}` is not where a note goes. SCHEMA.md places it at "
                        "<project>/<kind>/<slug>.md, or one-offs/<kind>/<slug>.md, "
                        f"with <kind> one of: {', '.join(kinds)}")
        if kind is not None and parts[1] != kind:
            raise Usage(f"`{relative}` is in the `{parts[1]}` folder. This run makes `{kind}`, "
                        f"so its note goes at <project>/{kind}/<slug>.md")
    path = (env.vault / Path(*parts)).resolve()
    if env.vault not in path.parents:
        raise Usage(f"`{relative}` leaves the vault")
    folder = env.vault
    for part in parts[:-1]:
        folder = folder / part
        if folder.exists() and not folder.is_dir():
            raise Usage(f"`{folder.relative_to(env.vault).as_posix()}` is a file, "
                        f"so `{relative}` cannot sit under it")
    if path.exists() and not path.is_file():
        raise Usage(f"`{relative}` is a folder")
    return path


def vault_notes(env):
    """Every file in the vault that may be a Content MD.

    The same rule the path check applies: nothing under a folder whose name
    starts with `_` or `.`, none of the reserved names in any case, and files
    only: a folder named `x.md` is not a note.
    """
    if not env.vault.is_dir():
        return []
    reserved = reserved_names(env)
    found = []
    for path in sorted(env.vault.rglob("*.md")):
        relative = path.relative_to(env.vault)
        if any(part.startswith(("_", ".")) for part in relative.parts[:-1]):
            continue
        if any(part.casefold() in reserved for part in relative.parts):
            continue
        if not path.is_file():
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


# ── reading Markdown as a reader sees it ─────────────────────────────────────

def scan(text):
    """Each line as a reader sees it, and what is left open at the end.

    Returns ([(line number, line, where)], fence left open, comment left open).
    `where` is "fence" for a line inside a code fence, fence lines included,
    and "text" otherwise. A "text" line has any HTML comment in it removed; a
    line wholly inside a comment is blank. An unclosed comment hides the rest
    of the file, as it does in a reader.

    A backtick fence's info string cannot hold a backtick, so a line that
    starts with inline code, such as ```x``` is the flag, opens no fence.
    """
    found, fence, comment = [], None, False
    for number, line in enumerate(text.split("\n"), 1):
        if fence:
            closer = FENCE_RE.match(line)
            if (closer and closer.group(2)[0] == fence[0] and len(closer.group(2)) >= len(fence)
                    and not closer.group(3).strip()):
                fence = None
            found.append((number, line, "fence"))
            continue
        visible, rest = "", line
        while rest:
            if comment:
                end = rest.find("-->")
                if end == -1:
                    rest = ""
                    break
                comment = False
                rest = rest[end + 3:]
            else:
                start = rest.find("<!--")
                if start == -1:
                    visible += rest
                    break
                visible += rest[:start]
                rest = rest[start + 4:]
                comment = True
        opener = FENCE_RE.match(visible)
        if opener and not (opener.group(2)[0] == "`" and "`" in opener.group(3)):
            fence = opener.group(2)
            found.append((number, line, "fence"))
            continue
        found.append((number, visible, "text"))
    return found, fence is not None, comment


def outside_fences(text):
    """(line number, line) for each line a reader sees as text: not inside a
    code fence, with HTML comments removed."""
    for number, line, where in scan(text)[0]:
        if where == "text":
            yield number, line


def heading_title(line):
    """The title of a `## ` heading, without the closing hashes it may carry."""
    return re.sub(r"(?:\s+#+)?\s*$", "", line[3:]).strip()


def sections(body):
    """[(title, text)] for each `## ` heading a reader sees, in order."""
    lines = body.split("\n")
    starts = [(number, heading_title(line)) for number, line in outside_fences(body)
              if line.startswith("## ")]
    found = []
    for index, (number, title) in enumerate(starts):
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) else len(lines)
        found.append((title, "\n".join(lines[number:end])))
    return found


def bullets(text):
    """The list items of a section, each with its continuation lines joined.

    Read as a reader sees them: nothing inside a code fence or a comment.
    """
    items = []
    for _, line in outside_fences(text):
        if BULLET_RE.match(line):
            items.append(line.strip())
        elif line.strip() and items and line.startswith((" ", "\t")):
            items[-1] += " " + line.strip()
        elif not line.strip():
            continue
        else:
            items.append(line.strip())
    return items


def decisions(text):
    """The bullets under Decisions in Force, struck-out text removed, or None
    when the note has no such section."""
    _, body = split_note(text)
    found = dict(sections(body))
    if "Decisions in Force" not in found:
        return None
    return [unstruck(item) for item in bullets(found["Decisions in Force"])]


# ── notes and links ──────────────────────────────────────────────────────────

def link_key(name):
    """How a wikilink's target is looked up: case folded, without `.md`."""
    key = name.strip().replace("\\", "/").strip("/").casefold()
    return key[:-3] if key.endswith(".md") else key


def note_index(env):
    """Every Content MD in the vault, and how a wikilink finds one.

    Obsidian resolves [[name]] by file name, so that is the first key; the
    path inside the vault is the second. A note's id is the third, because the
    ladder cites a note by id. A file that is not UTF-8 is skipped, and said so.
    """
    notes, by_name = [], {}
    for path in vault_notes(env):
        try:
            text = read_text(path)
        except Usage as problem:
            warn(f"skipped: {problem}")
            continue
        front = front_matter(text)
        if front.get("type") != env.spec["content_md"]["type"]:
            continue
        brand = front.get("context_brand")
        relative = path.relative_to(env.vault)
        entry = {
            "path": relative.as_posix(),
            "file": path,
            "id": front.get("id"),
            "kind": front.get("kind"),
            "status": front.get("status"),
            "context_brand": [gate for gate in brand if isinstance(gate, str)]
                             if isinstance(brand, list) else [],
        }
        notes.append(entry)
        keys = {path.stem, str(front.get("id") or ""), relative.with_suffix("").as_posix()}
        for key in {link_key(key) for key in keys} - {""}:
            by_name.setdefault(key, []).append(entry)
    return notes, by_name


def cited_notes(text):
    """The distinct note names a piece of text links to, in order."""
    seen, names = set(), []
    for name in WIKILINK_RE.findall(text):
        key = link_key(name)
        if key and key not in seen:
            seen.add(key)
            names.append(name.strip())
    return names


def find_note(by_name, name):
    """The one note a wikilink names. Refused when there is none, or several."""
    paths = {entry["path"]: entry for entry in by_name.get(link_key(name), [])}
    if not paths:
        raise Refused(f"[[{name}]] is not a note in the vault")
    if len(paths) > 1:
        raise Refused(f"[[{name}]] could be any of: {', '.join(sorted(paths))}. Cite it by id.")
    return next(iter(paths.values()))


def notes_cited(by_name, text):
    """The paths of the notes a text links to, where a link names exactly one."""
    found = set()
    for name in cited_notes(text):
        paths = {entry["path"] for entry in by_name.get(link_key(name), [])}
        if len(paths) == 1:
            found |= paths
    return found


# ── the attestation ──────────────────────────────────────────────────────────

def table_cells(line):
    """The cells of one table row. A pipe inside a cell is written `\\|`."""
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|") and not inner.endswith("\\|"):
        inner = inner[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", inner)]


def attestation_tables(text):
    """(visible lines, [(line index, header)]) for each context-resolution
    table a reader sees."""
    lines = [line for _, line in outside_fences(text.replace("\r\n", "\n"))]
    tables = []
    for index, line in enumerate(lines):
        if not TABLE_LINE_RE.match(line):
            continue
        header = [cell.casefold() for cell in table_cells(line)]
        if sorted(header) == sorted(ATTESTATION_COLUMNS):
            tables.append((index, header))
    return lines, tables


def attestation_rows(text, allow_none=False):
    """The rows of the context-resolution table, each a dict keyed by column.

    The table is the one a reader sees, outside a code fence and a comment,
    whose header names Constraint, Gate, Level, Source and State. There must be
    exactly one: rows in a second table would never be checked. With
    `allow_none`, for a pipeline that needs no context, no table and an empty
    table are both no rows.
    """
    lines, tables = attestation_tables(text)
    wanted = ", ".join(name.capitalize() for name in ATTESTATION_COLUMNS)
    if not tables and allow_none:
        return []
    if not tables:
        raise Refused("the attestation has no context-resolution table. "
                      f"It needs one with the columns: {wanted}")
    if len(tables) > 1:
        raise Refused(f"the attestation has {len(tables)} context-resolution tables. Write one. "
                      "Rows in a second table would not be read, so they would never be checked.")
    index, header = tables[0]
    rows = []
    for number, row in enumerate(lines[index + 1:]):
        if not TABLE_LINE_RE.match(row):
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
    if not rows and not allow_none:
        raise Refused("the context-resolution table in the attestation has no rows")
    return rows


def level_of(row):
    """L0, L1, L2, L3 or STATED, from a cell such as `L0 AUTHORED`; else None.

    Emphasis and code marks around the level are not part of it.
    """
    words = re.sub(r"[*_`~]", " ", row["level"]).casefold().replace("-", " ").split()
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
    except json.JSONDecodeError as err:
        raise Usage(f"{path} does not parse: {err}. It is written only by studio_run.py; "
                    "if it was edited by hand, start a new run.")
    missing = [key for key in STATE_KEYS if not isinstance(state, dict) or key not in state]
    if missing:
        raise Usage(f"{path} has no {', '.join(missing)}")
    env.pipeline(state["pipeline"])
    return state


def all_states(env, broken=None):
    """The state of every run that can be read. A broken one is left out, and
    added to `broken` as (run id, what is wrong) when a list is given."""
    states = []
    if env.runs.is_dir():
        for path in sorted(env.runs.glob("*/state.json")):
            try:
                states.append(load_state(env, path.parent.name))
            except Usage as problem:
                if broken is not None:
                    broken.append((path.parent.name, str(problem)))
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
