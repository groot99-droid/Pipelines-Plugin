"""Studio pipeline bookkeeper.

Keeps the state of a run and refuses to mark a stage done until what the spec
declares for that stage is true. It never calls a model and never calls a
connector: the studio-pipeline skill does the work, in a live Claude Code
session, and reports here.

    python studio/pipeline/studio_run.py new --pipeline ui-direction --title "..."
    python studio/pipeline/studio_run.py stage   <run-id>
    python studio/pipeline/studio_run.py facts   <run-id>
    python studio/pipeline/studio_run.py note    <run-id> <project>/<kind>/<slug>.md
    python studio/pipeline/studio_run.py gate    <run-id> <gate>
    python studio/pipeline/studio_run.py confirm <run-id> <stage|flush|park|gate> --words "..."
    python studio/pipeline/studio_run.py advance <run-id>
    python studio/pipeline/studio_run.py back    <run-id> --why "..."
    python studio/pipeline/studio_run.py keep    <run-id> <file in the run folder> --role final|variant|reference|export|concept-frame
    python studio/pipeline/studio_run.py park    <run-id> --constraint NAME --needs "..."
    python studio/pipeline/studio_run.py unpark  <run-id>
    python studio/pipeline/studio_run.py status  [<run-id>] [--json]

Stage order, outputs, checks and confirmation rules are read from spec.yaml.
Nothing about a particular stage or pipeline is written into this file.

What this cannot do:
  - stop a tool call. It can only refuse to record that a stage is done.
  - hear the author. A go-ahead is recorded because the skill says one was
    given, and a checkpoint stage advances when `advance` is run.
  - tell whether an attestation is TRUE. It checks that every needed
    constraint has a row, that each row's level is backed the way that level
    must be, and that what a row cites exists. Whether the gate really says
    what the row claims is for the author to judge at the checkpoint.

Exit codes: 0 done, 1 refused, 2 usage or configuration error.
Requires pyyaml.
"""

import argparse
import json
import re
import secrets
import sys
from datetime import date, timedelta

from studio_common import (
    EXIT_OK, EXIT_REFUSED, EXIT_USAGE, SPEC_PATH, Env, Refused, Usage,
    all_states, artifact_roles, attestation_rows, attesting_stage, cited_notes, current_stage, decisions,
    find_note, gate_path, gate_sections, latest_confirmation, level_of, load_state, log_event,
    normalize, note_index, now, open_console, parse_stamp, read_text, resolve_note, save_state,
    slugify, squeeze, stage_checks, stage_outputs, stamp, unstruck, write_text,
)

# What `confirm` accepts besides a stage that requires confirmation. Each is a
# write that is planned, shown and confirmed on its own: a note written outside
# the record stage, or a brand gate.
EXTRA_CONFIRMATIONS = ("flush", "park", "gate")

# File times and datetime.now() come from clocks of different precision on
# Windows, so a file written just after a confirmation can carry a time just
# before it. Real work takes longer than this to run.
CLOCK_SLACK_SECONDS = 2.0

# A recalled line is copied from one bullet, and is long enough to mean
# something on its own.
QUOTE_MIN_WORDS = 3

PLACEHOLDER_RE = re.compile(r"\{pipeline(?:\.([A-Za-z0-9_.\-]+))?\}")
QUOTED_RE = re.compile(r"\"([^\"]+)\"|“([^”]+)”")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
# `section 2`, `sections 2 and 3`, `§2-4`, `section 2, §5`.
SECTION_NUMBER = r"\d+(?:\s*(?:-|–|to)\s*\d+)?"
SECTIONS_RE = re.compile(
    rf"(?:\bsections?\b|§)\s*({SECTION_NUMBER}(?:\s*(?:,|&|\band\b|\bor\b)\s*(?:§\s*)?{SECTION_NUMBER})*)",
    re.I)
# A range wider than this is a typo, not a citation.
SECTION_RANGE_MAX = 20

STATES = ("resolved", "provisional")


def fill(template, env, state):
    """Replace {pipeline} and {pipeline.a.b} from the run's pipeline entry.

    A value may itself hold a placeholder, as the stage notes do; those are
    filled too.
    """
    name = state["pipeline"]
    cfg = env.pipeline(name)

    def lookup(match):
        path = match.group(1)
        if path is None:
            return name
        value = cfg
        for key in path.split("."):
            if not isinstance(value, dict) or key not in value:
                return f"[nothing under `{path}` for {name} in spec.yaml]"
            value = value[key]
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value).rstrip()

    text = template
    for _ in range(3):
        filled = PLACEHOLDER_RE.sub(lookup, text)
        if filled == text:
            break
        text = filled
    return text.replace("<run-id>", state["run_id"])


def place_note(env, state, relative):
    """The run's note path, checked as a place this run's pipeline may write."""
    return resolve_note(env, relative, placing=True, kind=env.pipeline(state["pipeline"]).get("kind"))


# ── checks ───────────────────────────────────────────────────────────────────
# Each takes (env, state, stage, run_dir) and raises Refused. A stage names the
# ones that apply to it under `checks:` in the spec.

CHECKS = {}


def check(name):
    def register(function):
        CHECKS[name] = function
        return function
    return register


def attested(env, state, stage, run_dir):
    """The attestation's rows. A pipeline that needs no brand context may
    write an attestation with no table."""
    needs = env.pipeline(state["pipeline"]).get("requires_context") or []
    rows = attestation_rows(read_text(run_dir / stage_outputs(stage)[0]), allow_none=not needs)
    for row in rows:
        row["gate"] = row["gate"].strip("`* ")
        row["state_word"] = squeeze(row["state"]).strip("`* ")
    return rows


def quotes_in(source):
    return [first or second for first, second in QUOTED_RE.findall(source)]


def section_numbers(source):
    """Every section a Source cell cites, ranges spread out. Quoted text is
    left out: a line copied from a gate may name a section of its own."""
    numbers = []
    for listed in SECTIONS_RE.findall(QUOTED_RE.sub(" ", source)):
        for piece in re.split(r"\s*(?:,|&|\band\b|\bor\b)\s*", listed, flags=re.I):
            ends = [int(n) for n in re.findall(r"\d+", piece)]
            if len(ends) == 2 and 0 <= ends[1] - ends[0] <= SECTION_RANGE_MAX:
                numbers += [str(n) for n in range(ends[0], ends[1] + 1)]
            else:
                numbers += [str(n) for n in ends]
    return numbers


def matches_need(constraint, need):
    """A Constraint cell is for a need when it is the need, or starts with it
    and goes on after a colon, a bracket, a comma, a semicolon or a dash."""
    said, wanted = squeeze(constraint), squeeze(need)
    return said == wanted or re.match(re.escape(wanted) + r"(?:\s*[:(,;]|\s+[-–—]|\s*[–—])",
                                      said) is not None


@check("outputs_exist")
def outputs_exist(env, state, stage, run_dir):
    for name in stage_outputs(stage):
        path = run_dir / name
        if not path.is_file():
            raise Refused(f"{name} is not in the run folder")
        if not read_text(path).strip():
            raise Refused(f"{name} is empty")


@check("note_path_set")
def note_path_set(env, state, stage, run_dir):
    if not state.get("note_path"):
        raise Refused("this run has no note yet. Set it with: "
                      f"studio_run.py note {state['run_id']} <project>/<kind>/<slug>.md")
    place_note(env, state, state["note_path"])


@check("covers_every_need")
def covers_every_need(env, state, stage, run_dir):
    rows = attested(env, state, stage, run_dir)
    for row in rows:
        if row["gate"] not in env.spec["gates"]:
            raise Refused(f"`{row['gate']}` is not a gate in the spec:\n    {row['row']}")
    for need in env.pipeline(state["pipeline"]).get("requires_context", []):
        mine = [row for row in rows if row["gate"] == need["gate"]]
        if not mine:
            raise Refused(f"the attestation has no row for `{need['gate']}`, "
                          f"which {state['pipeline']} requires")
        wanted = need.get("needs", [])
        for name in wanted:
            hits = [row for row in mine if matches_need(row["constraint"], name)]
            if not hits:
                raise Refused(f"the attestation has no row for `{name}` from `{need['gate']}`. "
                              "One row for each needed constraint, in the wording `facts` prints.")
            if len(hits) > 1:
                raise Refused(f"{len(hits)} rows are for `{name}` from `{need['gate']}`. "
                              "One row for each needed constraint:\n    "
                              + "\n    ".join(row["row"] for row in hits))
        for row in mine:
            covered = [name for name in wanted if matches_need(row["constraint"], name)]
            if len(covered) > 1:
                raise Refused(f"one row is for {len(covered)} needs ({', '.join(covered)}). "
                              f"Each takes its own row:\n    {row['row']}")


@check("no_unresolved")
def no_unresolved(env, state, stage, run_dir):
    marker = env.spec["ladder"]["unresolved_marker"]
    rows = attested(env, state, stage, run_dir)
    unreadable = [row for row in rows if level_of(row) is None]
    if unreadable:
        raise Refused(f"{len(unreadable)} row(s) have a Level that cannot be read:\n    "
                      + "\n    ".join(f"{row['row']}\n      `{row['level']}` is not a level."
                                      for row in unreadable)
                      + "\n  Write it as the ladder names it: L0 AUTHORED, L1 RECALLED, "
                        "L2 DERIVED, STATED or L3.")
    still_open = []
    for row in rows:
        if level_of(row) == "L3":
            still_open.append(f"{row['row']}\n      L3 is {marker}")
        elif row["state_word"] not in STATES:
            still_open.append(f"{row['row']}\n      its state is `{row['state']}`. "
                              "A row that may go on is `resolved` or `PROVISIONAL`.")
    if still_open:
        raise Refused(f"{len(still_open)} constraint(s) are not resolved:\n    "
                      + "\n    ".join(still_open)
                      + "\n  Ask the author. If they state it, the row's level is STATED, with "
                        "the date. If they do not, park the run.")


def back_l0(env, row):
    declared = env.spec["gates"][row["gate"]]
    sections = gate_sections(env, row["gate"])
    if sections is None:
        raise Refused(f"`{row['gate']}` is not authored: there is no {declared['file']}. "
                      f"It cannot resolve at L0:\n    {row['row']}")
    source = QUOTED_RE.sub(" ", row["source"]).casefold()
    if declared["file"].casefold() not in source:
        raise Refused(f"an L0 row names the gate's own file, {declared['file']}, and the section "
                      f"in it:\n    {row['row']}")
    for name, other in env.spec["gates"].items():
        if name != row["gate"] and other["file"].casefold() in source:
            raise Refused(f"an L0 row for `{row['gate']}` cites {other['file']}, another gate's "
                          f"file. One row, one gate:\n    {row['row']}")
    cited = section_numbers(row["source"])
    if not cited:
        raise Refused("an L0 row cites where in the gate the constraint is stated, "
                      f"as `section N`:\n    {row['row']}")
    answers = {item["section"] for item in sections["answers"]}
    gaps = {item["section"]: item["topic"] for item in sections["unresolved"]}
    for number in cited:
        if number in gaps:
            raise Refused(f"section {number} of `{row['gate']}` is where the gate says what it does "
                          f"NOT answer ({gaps[number]}). The file exists; the constraint is "
                          f"unresolved:\n    {row['row']}")
        if number not in answers:
            raise Refused(f"{declared['file']} answers nothing in a section {number}:\n    {row['row']}")


def back_l1(env, row, by_name):
    """Every note cited exists and speaks to the gate, and each quoted line is
    in one bullet of one of them. Returns True when a quoted line sits in a
    decision marked PROVISIONAL: recalled, it is still provisional."""
    marker = env.spec["ladder"]["provisional_marker"]
    names = cited_notes(row["source"])
    if not names:
        raise Refused(f"an L1 row cites the note it recalls from, as [[note]]:\n    {row['row']}")
    quotes = quotes_in(row["source"])
    if not quotes:
        raise Refused("an L1 row copies the line it recalls, in double quotes, exactly as the "
                      f"note has it:\n    {row['row']}")
    lines = []
    for name in names:
        entry = find_note(by_name, name)
        if row["gate"] not in entry["context_brand"]:
            raise Refused(f"{entry['path']} does not list `{row['gate']}` under context_brand, "
                          f"so it is not a note that speaks to that gate:\n    {row['row']}")
        items = decisions(read_text(entry["file"]))
        if items is None:
            raise Refused(f"{entry['path']} has no Decisions in Force. There is no decision in it "
                          f"to recall:\n    {row['row']}")
        lines += [(item, squeeze(item)) for item in items]
    provisional = False
    for quote in quotes:
        said = squeeze(unstruck(quote))
        if len(said.split()) < QUOTE_MIN_WORDS:
            raise Refused(f"the quoted line \"{quote}\" is too short to be a decision. Copy at least "
                          f"{QUOTE_MIN_WORDS} words of it:\n    {row['row']}")
        holding = [raw for raw, flat in lines if said in flat]
        if not holding:
            raise Refused(f"no line under Decisions in Force says \"{quote}\". A recalled line is "
                          "copied, not paraphrased, from one bullet, and not from struck-out text:"
                          f"\n    {row['row']}")
        provisional = provisional or any(marker in raw for raw in holding)
    return provisional


def back_l2(env, state, row, by_name):
    marker = env.spec["ladder"]["provisional_marker"]
    least = env.spec["ladder"]["levels"]["L2"]["min_notes"]
    if row["state_word"] != "provisional":
        raise Refused(f"a derived constraint is always {marker}. It is never presented as "
                      f"settled:\n    {row['row']}")
    kind = env.pipeline(state["pipeline"]).get("kind")
    found = {}
    for name in cited_notes(row["source"]):
        entry = find_note(by_name, name)
        if entry["kind"] != kind:
            raise Refused(f"{entry['path']} is kind `{entry['kind']}`; this run makes `{kind}`. "
                          f"Precedent comes from notes of the same kind:\n    {row['row']}")
        found[entry["path"]] = entry
    if len(found) < least:
        raise Refused(f"a {marker} constraint cites {len(found)} note(s); it needs {least}. "
                      f"Fewer is a coincidence, not precedent:\n    {row['row']}")
    return sorted(found)


def stated_on(state, row):
    """The dates a STATED row gives. Each is a real day, not after today, and
    not more than a day before the run began."""
    written = DATE_RE.findall(row["source"])
    if not written:
        raise Refused("a STATED row gives the date the author stated it, "
                      f"as YYYY-MM-DD:\n    {row['row']}")
    began = parse_stamp(state["created"]).date()
    today = max(date.today(), now().date())
    for text in written:
        try:
            day = date.fromisoformat(text)
        except ValueError:
            raise Refused(f"`{text}` is not a date:\n    {row['row']}") from None
        if day > today:
            raise Refused(f"{text} is after today. A STATED row gives the day the author said "
                          f"it:\n    {row['row']}")
        if day < began - timedelta(days=1):
            raise Refused(f"{text} is before this run began ({began}). A constraint stated for an "
                          "earlier run is recalled from its note, at L1:\n    " + row["row"])
    return written


@check("levels_are_backed")
def levels_are_backed(env, state, stage, run_dir):
    kept_rows(env, state, stage, run_dir)


def kept_rows(env, state, stage, run_dir):
    """Check each row against its level, and return what later writes owe.

    The rows are kept in state.json when the stage is done, so a later write is
    held to them even if attestation.md is changed or removed.
    """
    marker = env.spec["ladder"]["provisional_marker"]
    _, by_name = note_index(env)
    kept = []
    for row in attested(env, state, stage, run_dir):
        level = level_of(row)
        provisional = row["state_word"] == "provisional"
        if provisional and level not in ("L1", "L2"):
            raise Refused("only a derived constraint (L2), or a line recalled from a "
                          f"{marker} decision, is provisional:\n    {row['row']}")
        entry = {"constraint": row["constraint"], "gate": row["gate"], "level": level,
                 "state": row["state_word"], "row": row["row"]}
        if level == "L0":
            back_l0(env, row)
        elif level == "L1":
            recalled_provisional = back_l1(env, row, by_name)
            if recalled_provisional and not provisional:
                raise Refused(f"the line recalled is marked {marker} in its note, so it was "
                              f"derived, not decided. Recalled, it is still {marker}:\n    "
                              + row["row"])
            if provisional and not recalled_provisional:
                raise Refused(f"the line recalled is not marked {marker} in its note. A recalled "
                              f"decision is resolved:\n    {row['row']}")
            entry["quotes"] = quotes_in(row["source"])
        elif level == "L2":
            entry["notes"] = back_l2(env, state, row, by_name)
        elif level == "STATED":
            entry["dates"] = stated_on(state, row)
        kept.append(entry)
    return kept


@check("confirmed")
def confirmed(env, state, stage, run_dir):
    if not latest_confirmation(state, stage["id"]):
        raise Refused(f"`{stage['id']}` needs the author's go-ahead, and none is recorded. "
                      f"After a clear yes: studio_run.py confirm {state['run_id']} {stage['id']} "
                      '--words "<what the author said>"')


@check("confirmed_before_output")
def confirmed_before_output(env, state, stage, run_dir):
    given = latest_confirmation(state, stage["id"])
    if not given:
        raise Refused(f"`{stage['id']}` has no recorded confirmation")
    for name in stage_outputs(stage):
        path = run_dir / name
        if path.is_file() and path.stat().st_mtime < given["at_epoch"] - CLOCK_SLACK_SECONDS:
            raise Refused(f"{name} was written before the confirmation was recorded. "
                          "The work ran ahead of the go-ahead.")


@check("token_held")
def token_held(env, state, stage, run_dir):
    """A local-compute pipeline runs nothing until this run holds a live PASS
    token for its workload class. Any other class of pipeline passes."""
    import compute_gate  # beside this file

    cfg = env.pipeline(state["pipeline"])
    if cfg.get("class") != "local-compute":
        return
    workload = cfg.get("workload")
    if not workload:
        raise Usage(f"`{state['pipeline']}` is local-compute and names no `workload:` class")
    machine = compute_gate.load_machine()
    token = compute_gate.load_token(env, machine)
    if not compute_gate.token_live(token):
        raise Refused(f"no live compute token. A local-compute run holds one first: "
                      f"compute_gate.py mint {workload}, then compute_gate.py consume {state['run_id']}")
    if token["workload"] != workload:
        raise Refused(f"the live token is for `{token['workload']}`, and this run needs `{workload}`")
    if token.get("consumed_by") != state["run_id"]:
        raise Refused("the token is not consumed by this run"
                      + (f" (held by `{token['consumed_by']}`)" if token.get("consumed_by") else "")
                      + f". Consume it: compute_gate.py consume {state['run_id']}")


@check("note_written")
def note_written(env, state, stage, run_dir):
    """The last write of this run's note is a record write, made after the
    record go-ahead, and the vault holds exactly what it wrote. The record
    checks are run again on it."""
    import content_md  # beside this file

    note = place_note(env, state, state["note_path"])
    if not note.is_file():
        raise Refused(f"{state['note_path']} is not in the vault. Apply the plan first.")
    written = state.get("written")
    if not written or written.get("note_path") != state["note_path"]:
        raise Refused(f"this run has not written {state['note_path']}. Plan it, confirm it and "
                      "apply it, as record.")
    if written["purpose"] != "record":
        raise Refused(f"the note was last written as a {written['purpose']}. The record stage ends "
                      "with a record write: plan, confirm and apply it with --as record.")
    given = latest_confirmation(state, "record")
    if given and written["at_epoch"] < given["at_epoch"]:
        raise Refused("the note was written before the latest record go-ahead. "
                      "Plan it and apply it again.")
    text = normalize(read_text(note))
    if content_md.digest(text) != written["sha"]:
        raise Refused("the note in the vault is not the note that was previewed")
    errors, _ = content_md.lint(text, env, state["note_path"])
    errors += content_md.purpose_errors(env, state, "record", text)[0]
    if errors:
        raise Refused("the note does not pass the record checks:\n    " + "\n    ".join(errors))


@check("gate_set")
def gate_set(env, state, stage, run_dir):
    if not state.get("gate"):
        raise Refused("this run names no gate. Set it with: "
                      f"studio_run.py gate {state['run_id']} <gate>")
    if state["gate"] not in env.spec["gates"]:
        raise Refused(f"`{state['gate']}` is not a gate in the spec")


@check("gate_written")
def gate_written(env, state, stage, run_dir):
    """The run wrote its gate after the gate go-ahead, and the file on disk
    is the one that was shown. The gate checks are run again on it."""
    import content_md  # beside this file
    import gate_md

    gate = state.get("gate")
    written = state.get("gate_written")
    if not gate or not written or written.get("gate") != gate:
        raise Refused(f"this run has not written the gate `{gate}`. Plan it with gate_md.py plan, "
                      "show the author the whole file, confirm gate, and apply.")
    given = latest_confirmation(state, "gate")
    if given and written["at_epoch"] < given["at_epoch"]:
        raise Refused("the gate was written before the latest gate go-ahead. Plan it and apply it again.")
    path = gate_path(env, gate)
    if not path.is_file():
        raise Refused(f"{path.name} is not in the gate folder")
    text = normalize(read_text(path))
    if content_md.digest(text) != written["sha"]:
        raise Refused(f"{path.name} is not the gate that was shown to the author")
    errors = gate_md.lint_gate(text) + gate_md.provenance_errors(state, text)
    if errors:
        raise Refused("the gate does not pass its checks:\n    " + "\n    ".join(errors))


def run_checks(env, state, stage):
    run_dir = env.run_dir(state["run_id"])
    for name in stage_checks(env, state, stage):
        if name not in CHECKS:
            raise Usage(f"the spec names a check this file does not have: `{name}`")
        CHECKS[name](env, state, stage, run_dir)


# ── commands ─────────────────────────────────────────────────────────────────

def describe_stage(env, state, stage):
    lines = [f"{stage['title']}  ({stage['id']})"]
    outputs = stage_outputs(stage)
    if outputs:
        lines.append("  writes:   " + ", ".join(outputs) + f"   in {env.run_dir(state['run_id'])}")
    if stage.get("requires_explicit_confirm"):
        lines.append("  needs:    the author's explicit go-ahead, recorded with `confirm`")
    if stage.get("then"):
        lines.append("  then:     " + " ".join(stage["then"].split()))
    elif stage.get("checkpoint"):
        lines.append("  then:     stop and show the author. Advance only when they say so.")
    return lines


def show_next(env, state, stage):
    print("next      " + "\n          ".join(describe_stage(env, state, stage)))


def set_note(env, state, given):
    path = place_note(env, state, given)
    relative = path.relative_to(env.vault).as_posix()
    written = state.get("written") or any(event["event"] == "apply"
                                          for event in state.get("events", []))
    if written and state.get("note_path") and relative != state["note_path"]:
        raise Refused(f"this run has already written {state['note_path']}. "
                      "A run reads and writes one note. Start a new run for another.")
    if state.get("plan") and state["plan"].get("note_path") != relative:
        state["plan"] = None
    state["note_path"] = relative
    state["note_is_new"] = not path.is_file()
    others = [other["run_id"] for other in all_states(env)
              if other["run_id"] != state["run_id"] and other["status"] != "complete"
              and other.get("note_path") == relative]
    return others


def cmd_new(env, args):
    cfg = env.pipeline(args.pipeline)
    if cfg.get("status") != "implemented":
        raise Refused(f"`{args.pipeline}` is `{cfg.get('status')}`. Only an implemented pipeline starts."
                      + "".join(f"\n    open: {item}" for item in cfg.get("open", [])))
    title = " ".join(args.title.split())
    if not title:
        raise Usage("--title is empty")
    run_id = args.run_id or f"{slugify(title)}-{secrets.token_hex(3)}"
    run_dir = env.run_dir(run_id)
    if run_dir.exists():
        raise Usage(f"run `{run_id}` already exists")
    created = stamp(now())
    state = {
        "run_id": run_id,
        "pipeline": args.pipeline,
        "title": title,
        "note_path": None,
        "note_is_new": None,
        "spec_version": env.spec["version"],
        "created": created,
        "updated": created,
        "status": "active",
        "completed_stages": [],
        "next_stage_index": 0,
        "confirmations": [],
        "parked": None,
        "attested": None,
        "plan": None,
        "written": None,
        "gate": None,
        "gate_plan": None,
        "gate_written": None,
        "kept": [],
        "events": [],
    }
    others = set_note(env, state, args.note) if args.note else []
    log_event(state, "new", args.pipeline)
    run_dir.mkdir(parents=True)
    save_state(env, state)
    print(f"run       {run_id}")
    print(f"pipeline  {args.pipeline}")
    print(f"folder    {run_dir}")
    for other in others:
        print(f"warning   run `{other}` is also working on {state['note_path']}")
    show_next(env, state, env.stages[0])
    return EXIT_OK


def cmd_note(env, args):
    state = load_state(env, args.run_id)
    others = set_note(env, state, args.path)
    log_event(state, "note", state["note_path"])
    save_state(env, state)
    print(f"note      {state['note_path']}  ({'new' if state['note_is_new'] else 'continuing'})")
    for other in others:
        print(f"warning   run `{other}` is also working on this note. "
              "The second to write will be refused until it plans again.")
    return EXIT_OK


def cmd_gate(env, args):
    state = load_state(env, args.run_id)
    if env.pipeline(state["pipeline"]).get("writes") != "gate":
        raise Refused(f"`{state['pipeline']}` does not write a brand gate")
    if args.name not in env.spec["gates"]:
        raise Usage(f"no gate `{args.name}` in the spec. Declared: "
                    + ", ".join(sorted(env.spec["gates"])))
    written = state.get("gate_written")
    if written and written["gate"] != args.name:
        raise Refused(f"this run has already written the gate `{written['gate']}`. "
                      "A run writes one gate. Start a new run for another.")
    if state.get("gate_plan") and state["gate_plan"]["gate"] != args.name:
        state["gate_plan"] = None
    state["gate"] = args.name
    log_event(state, "gate", args.name)
    save_state(env, state)
    sections = gate_sections(env, args.name)
    now_is = "rewriting " + gate_path(env, args.name).name if sections is not None else "new"
    print(f"gate      {args.name}  ({now_is})")
    return EXIT_OK


def cmd_stage(env, args):
    state = load_state(env, args.run_id)
    stage = current_stage(env, state)
    if stage is None:
        print(f"run {state['run_id']} is complete. There is no next stage.")
        return EXIT_OK
    if state["status"] == "parked":
        print(f"run {state['run_id']} is PARKED on `{state['parked']['constraint']}`: "
              f"{state['parked']['needs']}")
        print(f"unpark it first: studio_run.py unpark {state['run_id']}")
        return EXIT_OK
    print("\n".join(describe_stage(env, state, stage)))
    print()
    print(" ".join(stage["description"].split()))
    print()
    print(fill(stage["prompt"], env, state).rstrip())
    return EXIT_OK


def gate_facts(env, state):
    cfg = env.pipeline(state["pipeline"])
    notes, _ = note_index(env)
    gates = []
    for need in cfg.get("requires_context", []):
        name = need["gate"]
        declared = env.spec["gates"].get(name)
        if declared is None:
            raise Usage(f"{state['pipeline']} requires `{name}`, which is not under `gates:`")
        sections = gate_sections(env, name)
        gates.append({
            "gate": name,
            "needs": need.get("needs", []),
            "file": gate_path(env, name).as_posix(),
            "on_disk": sections is not None,
            "scope": declared.get("scope"),
            "must_answer": declared.get("must_answer"),
            "answers": (sections or {}).get("answers", []),
            "unresolved": (sections or {}).get("unresolved", []),
            "notes_naming_it": [n["path"] for n in notes if name in n["context_brand"]],
        })
    writing = None
    if state.get("gate") in env.spec["gates"]:
        name = state["gate"]
        sections = gate_sections(env, name)
        writing = {"gate": name, "file": gate_path(env, name).as_posix(),
                   "on_disk": sections is not None,
                   "must_answer": env.spec["gates"][name].get("must_answer"),
                   "answers": (sections or {}).get("answers", []),
                   "unresolved": (sections or {}).get("unresolved", [])}
    return {
        "run_id": state["run_id"],
        "pipeline": state["pipeline"],
        "kind": cfg.get("kind"),
        "gates": gates,
        "writes_gate": writing,
        "open": cfg.get("open", []),
        "notes_in_vault": len(notes),
        "notes_of_this_kind": [n["path"] for n in notes if n["kind"] == cfg.get("kind")],
        "derivation_needs": env.spec["ladder"]["levels"]["L2"]["min_notes"],
        "known_conflicts": env.spec.get("known_conflicts", []),
    }


def cmd_facts(env, args):
    state = load_state(env, args.run_id)
    facts = gate_facts(env, state)
    if args.json:
        print(json.dumps(facts, indent=2, ensure_ascii=False))
        return EXIT_OK
    print(f"facts for {facts['run_id']}  ({facts['pipeline']}, kind {facts['kind']})")
    print("These are file facts. Reading the gate and judging the constraint is still to do.")
    for gate in facts["gates"]:
        print()
        print(f"  {gate['gate']}")
        print("    needed, one attestation row each, in these words:")
        for need in gate["needs"]:
            print(f"      - {need}")
        if gate["on_disk"]:
            print(f"    L0 file:    {gate['file']}")
            if gate["scope"]:
                print(f"    scope:      {gate['scope']}")
            for item in gate["answers"]:
                print(f"      answers       section {item['section']}: {item['topic']}")
            for item in gate["unresolved"]:
                print(f"      DECLARED GAP  section {item['section']}: {item['topic']}")
        else:
            print("    L0 file:    none. This gate is not authored.")
            print(f"    must answer: {gate['must_answer']}")
        if gate["notes_naming_it"]:
            print("    L1 candidates (notes whose context_brand names it):")
            for path in gate["notes_naming_it"]:
                print(f"      {path}")
        else:
            print("    L1 candidates: none")
    if not facts["gates"]:
        print()
        print("  This pipeline needs no brand context. Its attestation says so, with no table.")
    if facts["writes_gate"]:
        writing = facts["writes_gate"]
        print()
        print(f"  writes the gate {writing['gate']}")
        print(f"    must answer: {writing['must_answer']}")
        if writing["on_disk"]:
            print(f"    now:         {writing['file']}")
            for item in writing["answers"]:
                print(f"      answers       section {item['section']}: {item['topic']}")
            for item in writing["unresolved"]:
                print(f"      DECLARED GAP  section {item['section']}: {item['topic']}")
        else:
            print("    now:         not authored")
    print()
    print(f"  notes of kind `{facts['kind']}`: {len(facts['notes_of_this_kind'])}. "
          f"Deriving a constraint needs {facts['derivation_needs']}.")
    for item in facts["open"]:
        print()
        print(f"  open: {' '.join(item.split())}")
    for conflict in facts["known_conflicts"]:
        print()
        print(f"  known conflict `{conflict['id']}`: {' '.join(conflict['what'].split())}")
        print(f"    until settled: {' '.join(conflict['until_settled'].split())}")
    return EXIT_OK


def cmd_confirm(env, args):
    state = load_state(env, args.run_id)
    words = " ".join((args.words or "").split())
    if not words:
        raise Usage("--words is empty. Record what the author actually said.")
    if args.what == "park":
        if state["status"] != "parked":
            raise Refused("the run is not parked. Park it first, then confirm the note that says so.")
    elif args.what == "gate":
        if env.pipeline(state["pipeline"]).get("writes") != "gate":
            raise Refused(f"`{state['pipeline']}` does not write a brand gate")
    elif args.what not in EXTRA_CONFIRMATIONS:
        stage = current_stage(env, state)
        if stage is None:
            raise Refused("the run is complete")
        if state["status"] != "active":
            raise Refused(f"the run is {state['status']}")
        if args.what != stage["id"]:
            raise Refused(f"the run is at `{stage['id']}`, not `{args.what}`. "
                          "A go-ahead is recorded for the stage it was given for.")
        if not stage.get("requires_explicit_confirm"):
            raise Refused(f"`{stage['id']}` does not take a confirmation. "
                          "It is a checkpoint: advance when the author says so.")
    moment = now()
    state.setdefault("confirmations", []).append({
        "what": args.what,
        "at": stamp(moment),
        "at_epoch": moment.timestamp(),
        "words": words,
    })
    log_event(state, "confirm", args.what)
    save_state(env, state)
    print(f"recorded  go-ahead for `{args.what}` at {stamp(moment)}")
    return EXIT_OK


def cmd_advance(env, args):
    state = load_state(env, args.run_id)
    if state["status"] == "parked":
        raise Refused(f"the run is parked on `{state['parked']['constraint']}`. Unpark it first.")
    stage = current_stage(env, state)
    if stage is None or state["status"] == "complete":
        raise Refused("the run is complete. There is nothing to advance.")
    try:
        run_checks(env, state, stage)
        if attesting_stage(stage):
            state["attested"] = kept_rows(env, state, stage, env.run_dir(state["run_id"]))
    except Refused as refusal:
        log_event(state, "refused", f"{stage['id']}: {str(refusal).splitlines()[0]}")
        save_state(env, state)
        raise
    state["completed_stages"].append(stage["id"])
    state["next_stage_index"] += 1
    log_event(state, "advance", stage["id"])
    following = current_stage(env, state)
    if following is None:
        state["status"] = "complete"
        log_event(state, "complete")
    save_state(env, state)
    print(f"done      {stage['title']}")
    if following is None:
        print("complete  the run is finished. The note is the record; this folder may be deleted.")
    else:
        show_next(env, state, following)
    return EXIT_OK


def cmd_back(env, args):
    state = load_state(env, args.run_id)
    why = " ".join((args.why or "").split())
    if not why:
        raise Usage("--why is empty. Say what is being redone, and why.")
    if state["status"] == "complete":
        raise Refused("the run is complete. To change what it made, start a new run on the same note.")
    if state["status"] == "parked":
        raise Refused(f"the run is parked on `{state['parked']['constraint']}`. Unpark it first.")
    index = state["next_stage_index"]
    if index <= 0:
        raise Refused("the run is at its first stage. There is nothing before it.")
    ids = [stage["id"] for stage in env.stages]
    target = index - 1
    redone = set(ids[target:])
    state["confirmations"] = [given for given in state.get("confirmations", [])
                              if given["what"] not in redone]
    state["completed_stages"] = state["completed_stages"][:target]
    state["next_stage_index"] = target
    if any(attesting_stage(stage) for stage in env.stages[target:]):
        state["attested"] = None
    state["plan"] = None
    state["gate_plan"] = None
    log_event(state, "back", f"{ids[index] if index < len(ids) else 'end'} to {ids[target]}: {why}")
    save_state(env, state)
    print(f"back      to {env.stages[target]['title']}. Go-aheads from here on are cleared.")
    show_next(env, state, env.stages[target])
    return EXIT_OK


def cmd_keep(env, args):
    """Copy a file the run made into the assets folder, and remember it: the
    record stage must list every kept file under `artifacts`. Nothing is
    written outside the run folder before the execute go-ahead, so a keep
    needs one too. The note decides the place: <project>/<kind>/<slug>/."""
    import hashlib
    import shutil

    state = load_state(env, args.run_id)
    if state["status"] != "active":
        raise Refused(f"the run is {state['status']}")
    if not state.get("note_path"):
        raise Refused("this run has no note, so there is nowhere to keep a file. Set it with: "
                      f"studio_run.py note {state['run_id']} <project>/<kind>/<slug>.md")
    if not latest_confirmation(state, "execute"):
        raise Refused("nothing is kept before the execute go-ahead. A file made before it was made "
                      "outside the run.")
    roles = artifact_roles(env)
    if args.role not in roles:
        raise Usage(f"--role is one of: {', '.join(roles)}")
    run_dir = env.run_dir(state["run_id"])
    source = (run_dir / args.file).resolve()
    try:
        inside = source.relative_to(run_dir.resolve())
    except ValueError:
        raise Refused(f"{args.file} is not in the run folder. Only what the run made is kept.")
    if not source.is_file():
        raise Refused(f"{inside.as_posix()} is not in the run folder")
    if inside.name == "state.json" or inside.suffix == ".md":
        raise Refused("the run's bookkeeping and stage outputs are not artifacts")
    project, kind, slug = state["note_path"].rsplit(".", 1)[0].split("/")
    relative = f"{project}/{kind}/{slug}/{inside.name}"
    target = env.assets / project / kind / slug / inside.name
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() != sha:
        raise Refused(f"{relative} exists in the assets folder and holds a different file. "
                      "Rename this one; an artifact is never written over.")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.is_file():
        shutil.copy2(source, target)
    kept = [k for k in state.get("kept", []) if k["path"] != relative]
    kept.append({"path": relative, "role": args.role, "sha": sha, "at": stamp(now())})
    state["kept"] = kept
    log_event(state, "keep", f"{relative} as {args.role}")
    save_state(env, state)
    print(f"kept      {target}")
    print("artifacts entry for the note:")
    print(f"  - path: {relative}")
    print(f"    role: {args.role}")
    return EXIT_OK


def cmd_park(env, args):
    state = load_state(env, args.run_id)
    if state["status"] != "active":
        raise Refused(f"the run is {state['status']}")
    constraint = " ".join(args.constraint.split())
    needs = " ".join(args.needs.split())
    if not constraint:
        raise Usage("--constraint is empty. Name what is missing.")
    if not needs:
        raise Usage("--needs is empty. Say what would resolve it.")
    stage = current_stage(env, state)
    where = stage["id"] if stage else "the end"
    state["status"] = "parked"
    state["parked"] = {"constraint": constraint, "needs": needs,
                       "at": stamp(now()), "stage": where}
    log_event(state, "park", f"{constraint}: {needs}")
    save_state(env, state)
    item = (f"- [ ] BLOCKED on `{constraint}`: {needs} "
            f"Run `{state['run_id']}` is parked at {where}.")
    write_text(env.run_dir(state["run_id"]) / "park.md",
               f"# Parked: {state['run_id']}\n\n"
               "Put this first under Next Steps in the note, and set `status: blocked`.\n\n"
               f"{item}\n")
    print(f"parked    on `{constraint}`")
    print("write the blocker into the note. First item under Next Steps:")
    print(f"  {item}")
    if not state.get("note_path"):
        print("this run has no note yet. Set one before planning it: "
              f"studio_run.py note {state['run_id']} <project>/<kind>/<slug>.md")
    return EXIT_OK


def cmd_unpark(env, args):
    state = load_state(env, args.run_id)
    if state["status"] != "parked":
        raise Refused(f"the run is {state['status']}, not parked")
    log_event(state, "unpark", state["parked"]["constraint"])
    state["status"] = "active"
    state["parked"] = None
    save_state(env, state)
    print(f"active    {state['run_id']}")
    stage = current_stage(env, state)
    if stage:
        show_next(env, state, stage)
    return EXIT_OK


def summary(env, state):
    stage = current_stage(env, state)
    return {
        "run_id": state["run_id"],
        "pipeline": state["pipeline"],
        "title": state["title"],
        "status": state["status"],
        "note_path": state.get("note_path"),
        "completed_stages": state["completed_stages"],
        "next_stage": stage["id"] if stage else None,
        "parked": state.get("parked"),
        "created": state.get("created"),
        "updated": state.get("updated"),
    }


def cmd_status(env, args):
    if args.run_id:
        state = load_state(env, args.run_id)
        if args.json:
            print(json.dumps(summary(env, state), indent=2, ensure_ascii=False))
            return EXIT_OK
        print(f"run       {state['run_id']}")
        print(f"title     {state['title']}")
        print(f"pipeline  {state['pipeline']}")
        print(f"status    {state['status']}")
        print(f"note      {state.get('note_path') or '(not set)'}")
        print(f"done      {', '.join(state['completed_stages']) or '(nothing yet)'}")
        if state["status"] == "parked":
            print(f"parked    on `{state['parked']['constraint']}`: {state['parked']['needs']}")
        stage = current_stage(env, state)
        if stage:
            show_next(env, state, stage)
        return EXIT_OK
    broken = []
    runs = [summary(env, state) for state in all_states(env, broken)]
    if args.json:
        print(json.dumps(runs + [{"run_id": run_id, "status": "broken", "problem": problem}
                                 for run_id, problem in broken], indent=2, ensure_ascii=False))
        return EXIT_OK
    if not runs and not broken:
        print(f"no runs under {env.runs}")
        return EXIT_OK
    for run in runs:
        print(f"{run['status']:9s} {run['next_stage'] or '-':8s} {run['pipeline']:14s} {run['run_id']}")
    for run_id, problem in broken:
        print(f"{'broken':9s} {'-':8s} {'-':14s} {run_id}")
        print(f"          {problem}")
    return EXIT_OK


# ── entry ────────────────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="studio_run.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", default=str(SPEC_PATH), help="the spec to read")
    parser.add_argument("--runs-dir", help="where runs are kept (default: from the spec)")
    parser.add_argument("--vault-dir", help="the vault (default: from the spec)")
    parser.add_argument("--context-dir", help="the brand gates (default: from the spec)")
    parser.add_argument("--assets-dir", help="where kept artifacts go (default: from the spec)")
    commands = parser.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="start a run")
    new.add_argument("--pipeline", required=True)
    new.add_argument("--title", required=True)
    new.add_argument("--note", help="vault-relative path of the note, if already known")
    new.add_argument("--run-id")
    new.set_defaults(run=cmd_new)

    note = commands.add_parser("note", help="set the note this run reads and writes")
    note.add_argument("run_id")
    note.add_argument("path")
    note.set_defaults(run=cmd_note)

    gate = commands.add_parser("gate", help="set the brand gate a gate-writing run writes")
    gate.add_argument("run_id")
    gate.add_argument("name")
    gate.set_defaults(run=cmd_gate)

    stage = commands.add_parser("stage", help="print the current stage and its instructions")
    stage.add_argument("run_id")
    stage.set_defaults(run=cmd_stage)

    facts = commands.add_parser("facts", help="what is on disk for each gate this run needs")
    facts.add_argument("run_id")
    facts.add_argument("--json", action="store_true")
    facts.set_defaults(run=cmd_facts)

    confirm = commands.add_parser("confirm", help="record the author's go-ahead")
    confirm.add_argument("run_id")
    confirm.add_argument("what", help="a stage that requires confirmation, or: "
                                      + ", ".join(EXTRA_CONFIRMATIONS))
    confirm.add_argument("--words", required=True, help="what the author said")
    confirm.set_defaults(run=cmd_confirm)

    advance = commands.add_parser("advance", help="mark the current stage done, if its checks pass")
    advance.add_argument("run_id")
    advance.set_defaults(run=cmd_advance)

    back = commands.add_parser("back", help="go back one stage, to redo it")
    back.add_argument("run_id")
    back.add_argument("--why", required=True, help="what is being redone, and why")
    back.set_defaults(run=cmd_back)

    keep = commands.add_parser("keep", help="copy a file the run made into the assets folder")
    keep.add_argument("run_id")
    keep.add_argument("file", help="a file in the run folder")
    keep.add_argument("--role", required=True)
    keep.set_defaults(run=cmd_keep)

    park = commands.add_parser("park", help="stop a run on a constraint that cannot be resolved")
    park.add_argument("run_id")
    park.add_argument("--constraint", required=True)
    park.add_argument("--needs", required=True, help="what would resolve it")
    park.set_defaults(run=cmd_park)

    unpark = commands.add_parser("unpark", help="resume a parked run")
    unpark.add_argument("run_id")
    unpark.set_defaults(run=cmd_unpark)

    status = commands.add_parser("status", help="one run, or all of them")
    status.add_argument("run_id", nargs="?")
    status.add_argument("--json", action="store_true")
    status.set_defaults(run=cmd_status)
    return parser


def main(argv=None):
    open_console()
    args = build_parser().parse_args(argv)
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
