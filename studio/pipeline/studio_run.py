"""Studio pipeline bookkeeper.

Keeps the state of a run and refuses to mark a stage done until what the spec
declares for that stage is true. It never calls a model and never calls a
connector: the studio-pipeline skill does the work, in a live Claude Code
session, and reports here.

    python studio/pipeline/studio_run.py new --pipeline ui-direction --title "..."
    python studio/pipeline/studio_run.py stage   <run-id>
    python studio/pipeline/studio_run.py facts   <run-id>
    python studio/pipeline/studio_run.py note    <run-id> <project>/<kind>/<slug>.md
    python studio/pipeline/studio_run.py confirm <run-id> <stage|flush|park> --words "..."
    python studio/pipeline/studio_run.py advance <run-id>
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

from studio_common import (
    EXIT_OK, EXIT_REFUSED, EXIT_USAGE, SPEC_PATH, Env, Refused, Usage,
    all_states, attestation_rows, cited_notes, current_stage, latest_confirmation,
    level_of, load_state, log_event, normalize, note_index, now, open_console,
    read_text, resolve_note, save_state, sections, slugify, split_note, squeeze,
    stage_outputs, stamp, write_text,
)

# What `confirm` accepts besides a stage that requires confirmation. Both are
# writes to the vault that happen outside the record stage.
EXTRA_CONFIRMATIONS = ("flush", "park")

# File times and datetime.now() come from clocks of different precision on
# Windows, so a file written just after a confirmation can carry a time just
# before it. Real work takes longer than this to run.
CLOCK_SLACK_SECONDS = 2.0

PLACEHOLDER_RE = re.compile(r"\{pipeline(?:\.([A-Za-z0-9_.\-]+))?\}")
SECTION_RE = re.compile(r"(?:section|§)\s*(\d+)", re.I)
QUOTED_RE = re.compile(r"\"([^\"]+)\"|“([^”]+)”")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

STATES = ("resolved", "provisional")


def fill(template, env, state):
    """Replace {pipeline} and {pipeline.a.b} from the run's pipeline entry."""
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

    return PLACEHOLDER_RE.sub(lookup, template).replace("<run-id>", state["run_id"])


# ── checks ───────────────────────────────────────────────────────────────────
# Each takes (env, state, stage, run_dir) and raises Refused. A stage names the
# ones that apply to it under `checks:` in the spec.

CHECKS = {}


def check(name):
    def register(function):
        CHECKS[name] = function
        return function
    return register


def attested(stage, run_dir):
    rows = attestation_rows(read_text(run_dir / stage_outputs(stage)[0]))
    for row in rows:
        row["gate"] = row["gate"].strip("`* ")
        row["state_word"] = squeeze(row["state"]).strip("`* ")
    return rows


def find_note(by_name, name):
    paths = {entry["path"]: entry for entry in by_name.get(name.casefold(), [])}
    if not paths:
        raise Refused(f"[[{name}]] is not a note in the vault")
    if len(paths) > 1:
        raise Refused(f"[[{name}]] could be any of: {', '.join(sorted(paths))}. Cite it by id.")
    return next(iter(paths.values()))


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
    resolve_note(env, state["note_path"], placing=True)


@check("covers_every_need")
def covers_every_need(env, state, stage, run_dir):
    rows = attested(stage, run_dir)
    for row in rows:
        if row["gate"] not in env.spec["gates"]:
            raise Refused(f"`{row['gate']}` is not a gate in the spec:\n    {row['row']}")
    for need in env.pipeline(state["pipeline"]).get("requires_context", []):
        mine = [row for row in rows if row["gate"] == need["gate"]]
        if not mine:
            raise Refused(f"the attestation has no row for `{need['gate']}`, "
                          f"which {state['pipeline']} requires")
        for wanted in need.get("needs", []):
            if not any(squeeze(wanted) in squeeze(row["constraint"]) for row in mine):
                raise Refused(f"the attestation has no row for `{wanted}` from `{need['gate']}`. "
                              "One row for each needed constraint, in the wording `facts` prints.")


@check("no_unresolved")
def no_unresolved(env, state, stage, run_dir):
    marker = env.spec["ladder"]["unresolved_marker"]
    still_open = []
    for row in attested(stage, run_dir):
        level = level_of(row)
        if level is None:
            still_open.append(f"{row['row']}\n      `{row['level']}` is not a level. "
                              "It is L0, L1, L2 or STATED.")
        elif level == "L3":
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
    if not (env.context / declared["file"]).is_file():
        raise Refused(f"`{row['gate']}` is not authored: there is no {declared['file']}. "
                      f"It cannot resolve at L0:\n    {row['row']}")
    cited = SECTION_RE.findall(row["source"])
    if not cited:
        raise Refused("an L0 row cites where in the gate the constraint is stated, "
                      f"as `section N`:\n    {row['row']}")
    answers = {str(item["section"]) for item in declared.get("answers", [])}
    gaps = {str(item["section"]): item["topic"] for item in declared.get("unresolved", [])}
    for number in cited:
        if number in gaps:
            raise Refused(f"section {number} of `{row['gate']}` is where the gate says what it does "
                          f"NOT answer ({gaps[number]}). The file exists; the constraint is "
                          f"unresolved:\n    {row['row']}")
        if number not in answers:
            raise Refused(f"the spec lists no section {number} for `{row['gate']}`:\n    {row['row']}")


def back_l1(env, row, by_name):
    names = cited_notes(row["source"])
    if not names:
        raise Refused(f"an L1 row cites the note it recalls from, as [[note]]:\n    {row['row']}")
    quotes = [first or second for first, second in QUOTED_RE.findall(row["source"])]
    if not quotes:
        raise Refused("an L1 row copies the line it recalls, in double quotes, exactly as the "
                      f"note has it:\n    {row['row']}")
    entry = find_note(by_name, names[0])
    if row["gate"] not in entry["context_brand"]:
        raise Refused(f"{entry['path']} does not list `{row['gate']}` under context_brand, "
                      f"so it is not a note that speaks to that gate:\n    {row['row']}")
    _, body = split_note(read_text(entry["file"]))
    decisions = squeeze(dict(sections(body)).get("Decisions in Force", ""))
    for quote in quotes:
        if squeeze(quote) not in decisions:
            raise Refused(f"{entry['path']} does not say \"{quote}\" under Decisions in Force. "
                          f"A recalled line is copied, not paraphrased:\n    {row['row']}")


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


@check("levels_are_backed")
def levels_are_backed(env, state, stage, run_dir):
    _, by_name = note_index(env)
    for row in attested(stage, run_dir):
        level = level_of(row)
        if row["state_word"] == "provisional" and level != "L2":
            raise Refused("only a derived constraint (L2) is provisional:\n    " + row["row"])
        if level == "L0":
            back_l0(env, row)
        elif level == "L1":
            back_l1(env, row, by_name)
        elif level == "L2":
            back_l2(env, state, row, by_name)
        elif level == "STATED" and not DATE_RE.search(row["source"]):
            raise Refused("a STATED row gives the date the author stated it, "
                          f"as YYYY-MM-DD:\n    {row['row']}")


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


@check("note_written")
def note_written(env, state, stage, run_dir):
    import content_md  # beside this file

    note = resolve_note(env, state["note_path"], placing=True)
    if not note.is_file():
        raise Refused(f"{state['note_path']} is not in the vault. Apply the plan first.")
    written = normalize(read_text(note))
    proposed = normalize(read_text(run_dir / "note_update.md"))
    if written != proposed:
        raise Refused("the note in the vault is not the note that was previewed")
    errors, _ = content_md.lint(written, env, state["note_path"])
    if errors:
        raise Refused("the note does not pass the lint:\n    " + "\n    ".join(errors))


def run_checks(env, state, stage):
    run_dir = env.run_dir(state["run_id"])
    for name in stage.get("checks", []):
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
    if stage.get("checkpoint"):
        lines.append("  then:     stop and show the author. Advance only when they say so.")
    return lines


def show_next(env, state, stage):
    print("next      " + "\n          ".join(describe_stage(env, state, stage)))


def set_note(env, state, given):
    path = resolve_note(env, given, placing=True)
    relative = path.relative_to(env.vault).as_posix()
    written = [event for event in state.get("events", []) if event["event"] == "apply"]
    if written and state.get("note_path") and relative != state["note_path"]:
        raise Refused(f"this run has already written {state['note_path']}. "
                      "A run reads and writes one note. Start a new run for another.")
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
        on_disk = (env.context / declared["file"]).is_file()
        gates.append({
            "gate": name,
            "needs": need.get("needs", []),
            "file": (env.context / declared["file"]).as_posix(),
            "declared_authored": bool(declared.get("authored")),
            "on_disk": on_disk,
            "agrees": bool(declared.get("authored")) == on_disk,
            "scope": declared.get("scope"),
            "must_answer": declared.get("must_answer"),
            "answers": declared.get("answers", []),
            "unresolved": declared.get("unresolved", []),
            "notes_naming_it": [n["path"] for n in notes if name in n["context_brand"]],
        })
    return {
        "run_id": state["run_id"],
        "pipeline": state["pipeline"],
        "kind": cfg.get("kind"),
        "gates": gates,
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
        if not gate["agrees"]:
            print(f"    MISMATCH:   the spec says authored={gate['declared_authored']}, "
                  f"the disk says {gate['on_disk']}")
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
    print()
    print(f"  notes of kind `{facts['kind']}`: {len(facts['notes_of_this_kind'])}. "
          f"Deriving a constraint needs {facts['derivation_needs']}.")
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
    runs = [summary(env, state) for state in all_states(env)]
    if args.json:
        print(json.dumps(runs, indent=2, ensure_ascii=False))
        return EXIT_OK
    if not runs:
        print(f"no runs under {env.runs}")
        return EXIT_OK
    for run in runs:
        print(f"{run['status']:9s} {run['next_stage'] or '-':8s} {run['pipeline']:14s} {run['run_id']}")
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
        env = Env(args.spec, args.runs_dir, args.vault_dir, args.context_dir)
        return args.run(env, args)
    except Refused as refusal:
        print(f"REFUSED   {refusal}", file=sys.stderr)
        return EXIT_REFUSED
    except Usage as problem:
        print(f"error     {problem}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
