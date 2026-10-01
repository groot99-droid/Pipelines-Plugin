"""Content MD lint and writer.

The one way a note gets into the studio vault. It checks a proposed note
against studio/vault/SCHEMA.md, previews the change, and writes only after the
author has seen that preview and said yes.

    python studio/pipeline/content_md.py lint  <vault-relative path> [...]
    python studio/pipeline/content_md.py lint  --all
    python studio/pipeline/content_md.py plan  <run-id> [--as record|flush|park]
    python studio/pipeline/content_md.py apply <run-id> [--as record|flush|park] --confirm

`plan` reads runs/<run-id>/note_update.md, which is the COMPLETE note as it
should read afterwards, writes runs/<run-id>/record_plan.md for the author to
read, and keeps the plan in the run's state.json.
`apply` without --confirm is a dry run: it prints what it would do and writes
nothing.

The order is fixed: plan, then the author's go-ahead (studio_run.py confirm),
then apply. A go-ahead recorded before the plan was made does not count, and a
note changed after the plan was made must be planned again.

`--as` says why the note is being written:
    record   the last stage of a run
    flush    a session is stopping mid-run. The first Next Step names the run
             and the stage to resume
    park     the run is blocked. The first Next Step names the constraint

Once a run's context is attested, every write owes what the attestation found:
each derived constraint as a PROVISIONAL decision, each stated one as STATED
with its date, each on a line of its own.

An artifact listed under `artifacts` is a file under studio/assets/, named
by its path relative to that folder, with a role the spec allows. It got there
through `studio_run.py keep`, and a record write lists every file the run
kept. A missing file is a warning in `lint` (the assets are not versioned) and
a refusal in a record write.

What the lint catches in a link or a credential is a list of known shapes:
signed query parameters, the share links of a few hosts, and a few key
prefixes. A shape it does not know passes.

Exit codes: 0 done, 1 refused, 2 usage or configuration error.
Requires pyyaml.
"""

import argparse
import datetime as dt
import difflib
import hashlib
import re
import sys
from urllib.parse import unquote_plus

from studio_common import (
    EXIT_OK, EXIT_REFUSED, EXIT_USAGE, SPEC_PATH, Env, Refused, Usage,
    artifact_path, artifact_roles, bullets, cited_notes, current_stage, decisions, latest_confirmation, load_state, load_yaml,
    log_event, normalize, note_index, notes_cited, now, open_console, outside_fences, read_text,
    resolve_note, save_state, scan, sections, split_note, squeeze, stamp, unstruck, vault_notes,
    warn, write_text,
)

PURPOSES = ("record", "flush", "park")

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMELINE_HEADING_RE = re.compile(r"^### (\d{4}-\d{2}-\d{2}) · \S")
# A line that looks like a Timeline entry's heading, however it was written.
ENTRY_LIKE_RE = re.compile(r"^\s*#{1,6}\s*\d{4}-\d{2}-\d{2}")
CHECKBOX_RE = re.compile(r"^[-*+] \[[ xX]\]")
OPEN_BOX_RE = re.compile(r"^[-*+] \[ \]")
# A heading off the margin, or with a tab after its hashes. A reader shows it
# as a heading; the tools read only `## ` at the margin.
STRAY_HEADING_RE = re.compile(r"^(?: {1,3}#{1,6}(?:[ \t]|$)|#{1,6}\t)")
# A line of = or - under a paragraph line makes that line a heading.
SETEXT_RE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
NOT_A_PARAGRAPH_RE = re.compile(r"^ {0,3}(?:[#|>]|[-*+] |\d+[.)] )")

# A link, with or without its scheme: a host with a dot, then a path or query.
LINK_RE = re.compile(r"(?:[a-z][a-z0-9+.-]*://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?::\d+)?"
                     r"(?:[/?#][^\s<>\"`)\]]*)?", re.I)
# Query parameters that make a link work as a credential for whoever holds it.
BEARER_PARAMETERS = (
    "x-amz-signature", "x-amz-credential", "x-amz-security-token", "x-goog-signature",
    "x-goog-credential", "signature", "sig", "token", "access_token", "auth",
    "authorization", "apikey", "api_key", "key", "secret", "sas",
)
# Links that open for anyone who has them, by host and path.
SHARE_LINK_RES = (
    re.compile(r"^(?:https?://)?(?:drive|docs)\.google\.com/.*[?&]usp=(?:sharing|share_link|drive_link)", re.I),
    re.compile(r"^(?:https?://)?(?:www\.)?dropbox\.com/(?:s|sh|scl)/", re.I),
    re.compile(r"^(?:https?://)?(?:[\w-]+\.)?box\.com/s/", re.I),
    re.compile(r"^(?:https?://)?[\w-]+\.sharepoint\.com/:[a-z]:/", re.I),
    re.compile(r"^(?:https?://)?[\w-]+-my\.sharepoint\.com/", re.I),
    re.compile(r"^(?:https?://)?1drv\.ms/", re.I),
    re.compile(r"^(?:https?://)?onedrive\.live\.com/.*[?&](?:authkey|resid)=", re.I),
    re.compile(r"^(?:https?://)?(?:we\.tl|wetransfer\.com/downloads)/", re.I),
    re.compile(r"^(?:https?://)?(?:[\w-]+\.)?adobe\.com/.*(?:/link/|[?&]x_api_client_id=)", re.I),
)
CREDENTIAL_RES = (
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{16,}"),
    re.compile(r"\bgsk_[A-Za-z0-9]{8,}"),
    re.compile(r"\bhf_[A-Za-z0-9]{20,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


# ── reading a note ───────────────────────────────────────────────────────────

def timeline_entries(body):
    """Each `### ` entry under Timeline, as text, in order."""
    text = dict(sections(body)).get("Timeline")
    if text is None:
        return []
    lines = text.split("\n")
    starts = [number for number, line in outside_fences(text) if line.startswith("### ")]
    entries = []
    for index, number in enumerate(starts):
        end = starts[index + 1] - 1 if index + 1 < len(starts) else len(lines)
        block = [line.rstrip() for line in lines[number - 1:end]]
        while block and not block[-1]:
            block.pop()
        entries.append("\n".join(block))
    return entries


def without_comments(text):
    return re.sub(r"<!--.*?(?:-->|\Z)", "", text, flags=re.S)


def as_date(value):
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str) and DATE_RE.match(value.strip()):
        try:
            return dt.date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def parse(text):
    """(frontmatter dict or None, body, problem or None)"""
    raw, body = split_note(text)
    if raw is None:
        return None, body, "the note has no frontmatter. It must open with a `---` block."
    try:
        front = load_yaml(raw)
    except ValueError as err:
        return None, body, f"the frontmatter does not parse: {err}"
    if not isinstance(front, dict):
        return None, body, "the frontmatter is not a set of fields"
    return front, body, None


def gates_listed(front):
    brand = front.get("context_brand")
    return [gate for gate in brand if isinstance(gate, str)] if isinstance(brand, list) else []


# ── lint ─────────────────────────────────────────────────────────────────────

def bearer_links(text):
    """(link without its query, [why]) for each link that is a credential.

    A link is found with or without its scheme, and its parameter names are
    read after percent-decoding, so `X%2DAmz%2DSignature` is still a signature.
    """
    found = []
    for match in LINK_RE.finditer(text):
        url = match.group(0)
        base = url.split("?", 1)[0]
        if any(pattern.search(url) for pattern in SHARE_LINK_RES):
            found.append((base, ["a share link"]))
            continue
        decoded = unquote_plus(url)
        names = {name.strip().lower() for name in re.findall(r"[?&;]([^=&;?#\s]+)=", decoded)}
        hit = sorted(names.intersection(BEARER_PARAMETERS))
        if hit:
            found.append((base, hit))
    return found


def body_shape_errors(body):
    """What a reader would see differently from what the tools read."""
    errors = []
    scanned, open_fence, open_comment = scan(body)
    if open_fence:
        errors.append("a code fence is opened and never closed. Everything after it reads as "
                      "code, so the sections below it are not seen.")
    if open_comment:
        errors.append("an HTML comment `<!--` is never closed. Everything after it is hidden.")
    previous = ""
    for _, line, where in scanned:
        if where != "text":
            previous = ""
            continue
        if STRAY_HEADING_RE.match(line):
            errors.append(f"`{line.strip()[:60]}` is a heading off the margin, or with a tab. "
                          "Write a heading at the margin with one space: `## Title`.")
        elif SETEXT_RE.match(line) and previous.strip() and not NOT_A_PARAGRAPH_RE.match(previous):
            errors.append(f"the line under `{previous.strip()[:60]}` underlines it, which makes it "
                          "a heading. Write a heading as `## Title`.")
        previous = line
    return errors


def timeline_errors(body):
    errors = []
    text = dict(sections(body)).get("Timeline")
    if text is None:
        return errors
    entered = False
    for _, line in outside_fences(text):
        if line.startswith("### "):
            entered = True
        elif ENTRY_LIKE_RE.match(line):
            errors.append(f"`{line.strip()[:60]}` reads like a Timeline entry but is not read as "
                          "one. Write it `### YYYY-MM-DD · <what did the work>`, at the margin.")
        elif not entered and line.strip():
            errors.append(f"the Timeline has text before its first entry: `{line.strip()[:60]}`. "
                          "Every line of it belongs to a `### YYYY-MM-DD · ...` entry.")
            entered = True
    return errors


def lint(text, env, relative=None):
    """(errors, warnings) for one note, as lists of sentences."""
    rules = env.spec["content_md"]
    errors, warnings = [], []
    text = text.replace("\r\n", "\n")

    front, body, problem = parse(text)
    if problem:
        return [problem], warnings

    for field in rules["required"]:
        if front.get(field) in (None, "", []):
            errors.append(f"`{field}` is required and is missing or empty")
    known = set(rules["required"]) | set(rules["optional"])
    for field in front:
        if field not in known:
            warnings.append(f"`{field}` is not a field SCHEMA.md defines")

    if front.get("type") not in (None, rules["type"]):
        errors.append(f"`type` must be `{rules['type']}`, not `{front['type']}`")
    note_id = front.get("id")
    if note_id and not re.match(rules["id_pattern"], str(note_id)):
        errors.append(f"`id` is `{note_id}`. It must read cmd_<YYYYMMDD>_<slug>, "
                      "lower case, words joined by hyphens.")
    kind = front.get("kind")
    if kind is not None and str(kind) not in rules["kinds"]:
        errors.append(f"`kind` is `{kind}`. It must be one of: {', '.join(rules['kinds'])}")
    status = front.get("status")
    if status is not None and str(status) not in rules["statuses"]:
        errors.append(f"`status` is `{status}`. It must be one of: {', '.join(rules['statuses'])}")

    created, updated = as_date(front.get("created")), as_date(front.get("updated"))
    if front.get("created") is not None and created is None:
        errors.append("`created` is not a date written YYYY-MM-DD")
    if front.get("updated") is not None and updated is None:
        errors.append("`updated` is not a date written YYYY-MM-DD")
    if created and updated and updated < created:
        errors.append(f"`updated` ({updated}) is before `created` ({created})")

    lists = {}
    for field in ("pipelines", "context_brand", "context_domain", "tags", "artifacts"):
        value = front.get(field)
        if value is None:
            lists[field] = []
        elif isinstance(value, list):
            lists[field] = value
        else:
            lists[field] = []
            errors.append(f"`{field}` must be a list")
    for field in ("context_brand", "pipelines"):
        for item in lists[field]:
            if not isinstance(item, str):
                errors.append(f"`{field}` holds `{item}`, which is not a name. Write each as a "
                              f"plain word, as in [some_gate], not [[some_gate]].")
    for gate in lists["context_brand"]:
        if isinstance(gate, str) and gate not in env.spec["gates"]:
            errors.append(f"`context_brand` names `{gate}`, which is not a gate in the spec. "
                          "The ladder looks notes up by this field.")
    for name in lists["pipelines"]:
        if isinstance(name, str) and name not in env.spec["pipelines"]:
            warnings.append(f"`pipelines` names `{name}`, which is not in the spec")
    more, notes = artifact_errors(env, lists["artifacts"])
    errors += more
    warnings += notes

    errors += body_shape_errors(body)

    found = sections(body)
    titles = [title for title, _ in found]
    canonical = rules["sections"]
    folded = {title.casefold(): title for title in canonical}

    preamble = "" if body.startswith("## ") else body.split("\n## ", 1)[0]
    before = [line for line in without_comments(preamble).split("\n") if line.strip()]
    only_a_title = len(before) == 1 and re.match(r"^# \S", before[0])
    if before and not only_a_title:
        errors.append("there is text before the first section. The first screenful answers "
                      "what this is and what to do next; only a `# title` line may come first.")

    for title in titles:
        if title in canonical:
            continue
        if title.casefold() in folded:
            errors.append(f"`## {title}` is written `## {folded[title.casefold()]}`. "
                          "The tools read a section by its exact title.")
        else:
            warnings.append(f"`## {title}` is not a section SCHEMA.md defines")
    seen = set()
    for title in titles:
        if title in seen:
            errors.append(f"`## {title}` appears more than once")
        seen.add(title)
    ordered = [title for title in titles if title in canonical]
    if ordered != sorted(ordered, key=canonical.index):
        errors.append("the sections are out of order. SCHEMA.md fixes it: "
                      + ", ".join(canonical))

    raw = dict(found)
    content = {title: without_comments(text_).strip() for title, text_ in found}
    for title in rules["always"]:
        if not content.get(title):
            errors.append(f"`## {title}` is required and is missing or empty")
    needs_next = str(status) not in rules["next_steps_optional_when"]
    if needs_next and not content.get("Next Steps"):
        errors.append(f"`## Next Steps` is required while status is `{status}`. "
                      "Only a complete or archived note may omit it.")
    if titles and titles[0] != "Overview":
        errors.append("`## Overview` must be the first section. "
                      "The first screenful answers: what is this.")
    if "Next Steps" in titles and titles.index("Next Steps") != 1:
        errors.append("`## Next Steps` must come second, straight after Overview. "
                      "The first screenful answers: what do I do next.")

    steps = bullets(raw.get("Next Steps", ""))
    if str(status) == "blocked":
        if not steps or not OPEN_BOX_RE.match(steps[0]):
            errors.append("status is `blocked`, so the first item under Next Steps must be "
                          "the blocker, as an open checkbox, saying what would unblock it")
    if content.get("Next Steps") and not any(CHECKBOX_RE.match(step) for step in steps):
        errors.append("`## Next Steps` holds no checkbox items")

    marker = env.spec["ladder"]["provisional_marker"]
    least = env.spec["ladder"]["levels"]["L2"]["min_notes"]
    for item in bullets(raw.get("Decisions in Force", "")):
        if marker in unstruck(item) and len(cited_notes(item)) < least:
            errors.append(f"a {marker} decision cites {len(cited_notes(item))} note(s); "
                          f"it needs {least}: {item[:100]}")

    entries = timeline_entries(body)
    for entry in entries:
        heading = entry.split("\n", 1)[0]
        if not TIMELINE_HEADING_RE.match(heading):
            errors.append(f"a Timeline entry is headed `{heading}`. "
                          "It must read `### YYYY-MM-DD · <what did the work>`.")
    dates = [entry[4:14] for entry in entries
             if TIMELINE_HEADING_RE.match(entry.split("\n", 1)[0])]
    if dates != sorted(dates):
        errors.append("Timeline entries are not oldest first. New entries go at the end.")
    errors += timeline_errors(body)

    for base, names in bearer_links(text):
        errors.append(f"a link to {base} carries {', '.join(names)}. "
                      "A presigned or share link is a credential; it does not go in a note.")
    for pattern in CREDENTIAL_RES:
        if pattern.search(text):
            errors.append("the note holds something shaped like a credential")
            break

    visible = "\n".join(line for _, line in outside_fences(text))
    if re.search(r"\{\{[^}]*\}\}", visible):
        errors.append("the note still holds a template placeholder, `{{...}}`")

    if relative and kind:
        parts = str(relative).replace("\\", "/").split("/")
        if len(parts) < 2 or parts[-2] != str(kind):
            where = f"`{parts[-2]}/`" if len(parts) >= 2 else "the vault root"
            warnings.append(f"the note sits in {where} but its kind is `{kind}`. "
                            "SCHEMA.md places a note at <project>/<kind>/<slug>.md.")
    return errors, warnings


# ── what a write owes ────────────────────────────────────────────────────────

def artifact_errors(env, artifacts, must_exist=False):
    """(errors, warnings) for the `artifacts` list: each entry a path under
    the assets folder and a role the spec allows. A file that is not there is
    a warning, or an error when `must_exist`."""
    errors, warnings = [], []
    roles = artifact_roles(env)
    seen = set()
    for entry in artifacts:
        if not isinstance(entry, dict) or set(entry) - {"path", "role"} or "path" not in entry:
            errors.append("each artifact is `- path: ...` and `role: ...`, and nothing else")
            continue
        target, problem = artifact_path(env, entry.get("path"))
        if problem:
            errors.append(problem)
            continue
        if entry.get("role") not in roles:
            errors.append(f"artifact `{entry['path']}` has role `{entry.get('role')}`. "
                          f"It is one of: {', '.join(roles)}")
        if entry["path"] in seen:
            errors.append(f"artifact `{entry['path']}` is listed twice")
        seen.add(entry["path"])
        if not target.is_file():
            (errors if must_exist else warnings).append(
                f"artifact `{entry['path']}` is not under the assets folder ({env.assets})")
    return errors, warnings


def digest(text):
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def compare(existing, proposed, env):
    """Errors that only show when the new note is set beside the old one."""
    old, old_body, problem = parse(existing)
    if problem:
        return ["the note already in the vault cannot be read (" + problem + "), so a change "
                "to its Timeline or its fixed fields could not be seen. Fix it by hand first."]
    new, new_body, problem = parse(proposed)
    if problem:
        return []
    errors = []
    for field in env.spec["content_md"]["immutable"]:
        if str(old.get(field)) != str(new.get(field)):
            errors.append(f"`{field}` changed from `{old.get(field)}` to `{new.get(field)}`. "
                          "It is fixed for the life of the note.")
    before, after = as_date(old.get("updated")), as_date(new.get("updated"))
    if before and after and after < before:
        errors.append(f"`updated` went backwards, from {before} to {after}")
    was, now_ = timeline_entries(old_body), timeline_entries(new_body)
    if now_[:len(was)] != was:
        for index, entry in enumerate(was):
            if index >= len(now_) or now_[index] != entry:
                heading = entry.split("\n", 1)[0]
                errors.append(f"the Timeline entry `{heading}` was changed or removed. "
                              "The Timeline is append-only: correct a wrong entry with a new one.")
                break
    return errors


def provisional_kept(env, state, existing, proposed):
    """A PROVISIONAL decision already in the note stays as it is, unless this
    run's attestation has a constraint the author stated."""
    if any(row["level"] == "STATED" for row in state.get("attested") or []):
        return []
    marker = env.spec["ladder"]["provisional_marker"]
    after = {squeeze(item) for item in decisions(proposed) or [] if marker in item}
    return [f"the {marker} decision \"{item[:80]}\" was changed or removed. It stays as it is until "
            "the author states the constraint, which is a STATED row in a run's attestation."
            for item in decisions(existing) or [] if marker in item and squeeze(item) not in after]


def owed(state):
    """The attested rows a write must carry into Decisions in Force."""
    return [row for row in state.get("attested") or []
            if row["level"] in ("L2", "STATED")
            or (row["level"] == "L1" and row["state"] == "provisional")]


def carries(env, row, line, by_name):
    """True when one Decisions in Force line records the row as it must be."""
    marker = env.spec["ladder"]["provisional_marker"]
    if row["level"] == "STATED":
        return bool(re.search(r"\bSTATED\b", line)) and any(day in line for day in row["dates"])
    if marker not in line:
        return False
    if row["level"] == "L2":
        return set(row["notes"]) <= notes_cited(by_name, line)
    return all(squeeze(unstruck(quote)) in squeeze(line) for quote in row["quotes"])


def assign(rows, lines, fits, prefer=None):
    """Give each row a line of its own, where one can be found.

    Returns {row index: line index}. A plain matching: a row may take a line
    another row holds if that row can move to another line. With `prefer`, a
    row tries the lines it prefers first (the ones that name it), so three
    STATED rows of the same day keep their own lines.
    """
    owner = {}

    def order(row):
        indices = range(len(lines))
        if prefer is None:
            return list(indices)
        return sorted(indices, key=lambda index: not prefer(rows[row], lines[index]))

    def place(row, tried):
        for index in order(row):
            if index in tried or not fits(rows[row], lines[index]):
                continue
            tried.add(index)
            if index not in owner or place(owner[index], tried):
                owner[index] = row
                return True
        return False

    for row in range(len(rows)):
        place(row, set())
    return {row: index for index, row in owner.items()}


def owed_errors(env, state, front, proposed):
    """(errors, warnings) for what the attestation found and the note must say."""
    rows = owed(state)
    if not rows:
        return [], []
    marker = env.spec["ladder"]["provisional_marker"]
    errors, warnings = [], []
    lines = decisions(proposed) or []
    _, by_name = note_index(env)

    def fits(row, line):
        return carries(env, row, line, by_name)

    given = assign(rows, lines, fits, prefer=lambda row, line: squeeze(row["constraint"]) in squeeze(line))
    listed = gates_listed(front)
    for index, row in enumerate(rows):
        name = row["constraint"]
        if row["gate"] not in listed:
            errors.append(f"`{name}` speaks to `{row['gate']}`, and context_brand does not list it. "
                          "The next run finds this note's decisions by that field.")
        if index in given:
            if squeeze(name) not in squeeze(lines[given[index]]):
                warnings.append(f"the line for `{name}` does not name it: {lines[given[index]][:100]}")
            continue
        if any(fits(row, line) for line in lines):
            errors.append(f"`{name}` has no line of its own under Decisions in Force. Each "
                          "constraint the attestation derived or the author stated takes its own "
                          "bullet.")
        elif row["level"] == "L2":
            errors.append(f"`{name}` was derived. It must appear under Decisions in Force marked "
                          f"{marker}, citing the same notes, so that a later run does not recall a "
                          "derivation as a decision.")
        elif row["level"] == "STATED":
            errors.append(f"`{name}` was stated by the author. It must appear under Decisions in "
                          f"Force as `STATED {row['dates'][0]}: ...`, so that the next run "
                          "recalls it.")
        else:
            errors.append(f"`{name}` was recalled from a {marker} decision. It stays marked {marker} "
                          "under Decisions in Force, with the line as it was recalled.")
    return errors, warnings


def first_step(proposed):
    _, body, _ = parse(proposed)
    steps = bullets(dict(sections(body)).get("Next Steps", ""))
    return steps[0] if steps else ""


def names(text, word):
    return re.search(rf"(?<![\w-]){re.escape(word)}(?![\w-])", text, re.I) is not None


def purpose_errors(env, state, purpose, proposed):
    """(errors, warnings): what a note must say because of why it is written,
    and what every write owes once the run's context is attested."""
    errors, warnings = [], []
    front, body, _ = parse(proposed)
    if front is None:
        return errors, warnings
    lead = first_step(proposed)

    if purpose == "park":
        if state["status"] != "parked" or not state.get("parked"):
            return ["the run is not parked. Park it with studio_run.py park first."], warnings
        if str(front.get("status")) != "blocked":
            errors.append("the run is being parked, so the note's status must be `blocked`")
        constraint = state["parked"]["constraint"]
        if squeeze(constraint) not in squeeze(lead):
            errors.append(f"the first item under Next Steps must name what the run is blocked "
                          f"on: `{constraint}`")

    if purpose == "flush":
        stage = current_stage(env, state)
        if stage is None:
            return ["the run is complete. There is nothing to resume, so nothing to flush."], warnings
        if not names(lead, state["run_id"]) or not names(lead, stage["id"]):
            errors.append("the first item under Next Steps must name the run and the stage to "
                          f"resume: `{state['run_id']}` at {stage['id']}")

    if purpose == "record":
        listed = front.get("artifacts") if isinstance(front.get("artifacts"), list) else []
        more, _ = artifact_errors(env, listed, must_exist=True)
        errors += more
        by_path = {e["path"]: e.get("role") for e in listed if isinstance(e, dict) and "path" in e}
        for kept in state.get("kept", []):
            if kept["path"] not in by_path:
                errors.append(f"the run kept `{kept['path']}` and the note does not list it under "
                              "`artifacts`. Every kept file is recorded, or it is not kept.")
            elif by_path[kept["path"]] != kept["role"]:
                errors.append(f"`{kept['path']}` was kept as `{kept['role']}`, and the note says "
                              f"`{by_path[kept['path']]}`")

    more, notes = owed_errors(env, state, front, proposed)
    return errors + more, warnings + notes


# ── plan and apply ───────────────────────────────────────────────────────────

def note_place(env, state):
    return resolve_note(env, state["note_path"], placing=True,
                        kind=env.pipeline(state["pipeline"]).get("kind"))


def make_plan(env, state, purpose):
    run_dir = env.run_dir(state["run_id"])
    if not state.get("note_path"):
        raise Refused("this run has no note. Set it with: "
                      f"studio_run.py note {state['run_id']} <project>/<kind>/<slug>.md")
    proposal = run_dir / "note_update.md"
    if not proposal.is_file():
        raise Refused(f"there is no note_update.md in {run_dir}. "
                      "Write the complete note there first.")
    proposed = normalize(read_text(proposal))
    note = note_place(env, state)
    existing = normalize(read_text(note)) if note.is_file() else None

    errors, warnings = lint(proposed, env, state["note_path"])
    if existing is not None:
        errors += compare(existing, proposed, env)
        errors += provisional_kept(env, state, existing, proposed)
    more, notes = purpose_errors(env, state, purpose, proposed)
    errors += more
    warnings += notes
    front, _, _ = parse(proposed)
    if front:
        listed = front.get("pipelines")
        if not isinstance(listed, list) or state["pipeline"] not in listed:
            warnings.append(f"`pipelines` does not list `{state['pipeline']}`, which is writing this note")
        for other in vault_notes(env):
            if other.resolve() == note or not front.get("id"):
                continue
            try:
                taken = (parse(read_text(other))[0] or {}).get("id")
            except Usage as problem:
                warn(f"skipped: {problem}")
                continue
            if str(taken) == str(front["id"]):
                errors.append(f"`id` is `{front['id']}`, which "
                              f"{other.relative_to(env.vault).as_posix()} already has. "
                              "The ladder cites a note by its id.")

    diff = "".join(difflib.unified_diff(
        (existing or "").splitlines(keepends=True), proposed.splitlines(keepends=True),
        fromfile=f"vault/{state['note_path']} (now)" if existing is not None else "(no note yet)",
        tofile=f"vault/{state['note_path']} (proposed)"))
    return {
        "note_path": state["note_path"],
        "purpose": purpose,
        "is_new": existing is None,
        "unchanged": existing == proposed,
        "proposed_sha": digest(proposed),
        "existing_sha": digest(existing) if existing is not None else None,
        "errors": errors,
        "warnings": warnings,
        "diff": diff,
        "proposed": proposed,
    }


def render_plan(state, plan):
    verdict = "REFUSED" if plan["errors"] else "ready for the author"
    lines = [
        f"# Record plan: {state['run_id']}", "",
        f"- note: `{plan['note_path']}` ({'new' if plan['is_new'] else 'existing'})",
        f"- written as: {plan['purpose']}",
        f"- verdict: **{verdict}**", "",
    ]
    if plan["errors"]:
        lines += ["## Errors", ""] + [f"- {item}" for item in plan["errors"]] + [""]
    if plan["warnings"]:
        lines += ["## Warnings", ""] + [f"- {item}" for item in plan["warnings"]] + [""]
    if plan["unchanged"]:
        lines += ["## Change", "", "None. The proposed note is the note already in the vault.", ""]
    else:
        lines += ["## Change", "", "~~~~diff", plan["diff"].rstrip("\n"), "~~~~", ""]
    if not plan["errors"]:
        lines += [
            "## To write it", "",
            "Nothing has been written. After the author has read this and said yes:", "",
            "```",
            f'python studio/pipeline/studio_run.py confirm {state["run_id"]} {plan["purpose"]} '
            '--words "<what the author said>"',
            f"python studio/pipeline/content_md.py apply {state['run_id']} "
            f"--as {plan['purpose']} --confirm",
            "```", "",
        ]
    return "\n".join(lines)


def cmd_plan(env, args):
    state = load_state(env, args.run_id)
    plan = make_plan(env, state, args.purpose)
    run_dir = env.run_dir(state["run_id"])
    moment = now()
    write_text(run_dir / "record_plan.md", render_plan(state, plan))
    state["plan"] = {
        "note_path": plan["note_path"],
        "purpose": plan["purpose"],
        "is_new": plan["is_new"],
        "proposed_sha": plan["proposed_sha"],
        "existing_sha": plan["existing_sha"],
        "ok": not plan["errors"],
        "at": stamp(moment),
        "at_epoch": moment.timestamp(),
    }
    log_event(state, "plan", f"{plan['purpose']}: {'refused' if plan['errors'] else 'ready'}")
    save_state(env, state)
    print(f"plan      {run_dir / 'record_plan.md'}")
    print(f"note      {plan['note_path']}  ({'new' if plan['is_new'] else 'existing'})")
    for item in plan["warnings"]:
        print(f"warning   {item}")
    if plan["errors"]:
        raise Refused("the proposed note is not written:\n    " + "\n    ".join(plan["errors"]))
    print("ready     nothing is written yet. Show the author the plan.")
    return EXIT_OK


def cmd_apply(env, args):
    state = load_state(env, args.run_id)
    run_dir = env.run_dir(state["run_id"])
    planned = state.get("plan")
    if not planned:
        raise Refused("there is no plan. Run `content_md.py plan` and show it to the author first.")
    if planned["note_path"] != state.get("note_path"):
        raise Refused(f"the plan was made for {planned['note_path']}, and this run's note is now "
                      f"{state.get('note_path')}. Plan again.")
    if planned["purpose"] != args.purpose:
        raise Refused(f"the plan was made as `{planned['purpose']}`, not `{args.purpose}`. Plan again.")
    if not planned["ok"]:
        raise Refused("the plan on file was refused. Fix the note and plan again.")
    plan = make_plan(env, state, args.purpose)
    if plan["errors"]:
        raise Refused("the proposed note is not written:\n    " + "\n    ".join(plan["errors"]))
    if plan["proposed_sha"] != planned["proposed_sha"]:
        raise Refused("note_update.md changed after the plan was made. "
                      "The author has not seen this version. Plan again.")
    if plan["existing_sha"] != planned["existing_sha"]:
        raise Refused("the note in the vault changed after the plan was made. Plan again.")

    note = note_place(env, state)
    if not args.confirm:
        print("DRY RUN   nothing is written without --confirm.")
        print(f"would write  {note}")
        print(f"as           {args.purpose}")
        print(f"preview      {run_dir / 'record_plan.md'}")
        return EXIT_OK

    given = latest_confirmation(state, args.purpose)
    if not given:
        raise Refused(f"no go-ahead is recorded for `{args.purpose}`. After the author has read "
                      f"the plan and said yes: studio_run.py confirm {state['run_id']} "
                      f'{args.purpose} --words "<what the author said>"')
    if given["at_epoch"] < planned["at_epoch"]:
        raise Refused("the recorded go-ahead is older than the plan. "
                      "The author has not confirmed this plan. Show it, then confirm again.")

    write_text(note, plan["proposed"])
    moment = now()
    state["written"] = {
        "purpose": args.purpose,
        "note_path": state["note_path"],
        "sha": plan["proposed_sha"],
        "at": stamp(moment),
        "at_epoch": moment.timestamp(),
    }
    state["plan"] = None
    log_event(state, "apply", f"{args.purpose}: {state['note_path']}")
    state["note_is_new"] = False
    save_state(env, state)
    print(f"written   {note}")
    if args.purpose == "record":
        print(f"then      python studio/pipeline/studio_run.py advance {state['run_id']}")
    return EXIT_OK


def cmd_lint(env, args):
    if args.all:
        targets = [path.relative_to(env.vault).as_posix() for path in vault_notes(env)]
    else:
        targets = [path.replace("\\", "/") for path in args.paths]
    if not targets:
        print(f"no notes under {env.vault}")
        return EXIT_OK
    failed, ids = 0, {}
    for relative in targets:
        note = resolve_note(env, relative)
        if not note.is_file():
            raise Usage(f"no note at {relative}")
        try:
            text = read_text(note)
        except Usage as problem:
            print(f"FAIL  {relative}")
            print(f"        error    {problem}")
            failed += 1
            continue
        errors, warnings = lint(text, env, relative)
        front = parse(text)[0] or {}
        if front.get("id"):
            first = ids.setdefault(str(front["id"]), relative)
            if first != relative:
                errors.append(f"`id` is `{front['id']}`, which {first} already has. "
                              "The ladder cites a note by its id.")
        print(f"{'FAIL' if errors else 'ok  '}  {relative}")
        for item in errors:
            print(f"        error    {item}")
        for item in warnings:
            print(f"        warning  {item}")
        failed += bool(errors)
    print(f"{len(targets)} note(s), {failed} failing")
    return EXIT_REFUSED if failed else EXIT_OK


# ── entry ────────────────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="content_md.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", default=str(SPEC_PATH), help="the spec to read")
    parser.add_argument("--runs-dir", help="where runs are kept (default: from the spec)")
    parser.add_argument("--vault-dir", help="the vault (default: from the spec)")
    parser.add_argument("--context-dir", help="the brand gates (default: from the spec)")
    parser.add_argument("--assets-dir", help="where kept artifacts go (default: from the spec)")
    commands = parser.add_subparsers(dest="command", required=True)

    lint_ = commands.add_parser("lint", help="check notes against SCHEMA.md")
    lint_.add_argument("paths", nargs="*", help="vault-relative paths")
    lint_.add_argument("--all", action="store_true", help="every note in the vault")
    lint_.set_defaults(run=cmd_lint)

    plan = commands.add_parser("plan", help="preview a note write; writes nothing to the vault")
    plan.add_argument("run_id")
    plan.add_argument("--as", dest="purpose", choices=PURPOSES, default="record")
    plan.set_defaults(run=cmd_plan)

    apply_ = commands.add_parser("apply", help="write the planned note")
    apply_.add_argument("run_id")
    apply_.add_argument("--as", dest="purpose", choices=PURPOSES, default="record")
    apply_.add_argument("--confirm", action="store_true",
                        help="write it. Without this, apply is a dry run.")
    apply_.set_defaults(run=cmd_apply)
    return parser


def main(argv=None):
    open_console()
    args = build_parser().parse_args(argv)
    if args.command == "lint" and not args.all and not args.paths:
        print("error     give a path, or --all", file=sys.stderr)
        return EXIT_USAGE
    try:
        env = Env(args.spec, args.runs_dir, args.vault_dir, args.context_dir, args.assets_dir)
        return args.run(env, args)
    except Refused as refusal:
        print(f"REFUSED   {refusal}", file=sys.stderr)
        return EXIT_REFUSED
    except Usage as problem:
        print(f"error     {problem}", file=sys.stderr)
        return EXIT_USAGE
    except OSError as problem:
        print(f"error     {problem}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
