"""Brand gate writer.

The one way a brand gate gets into studio/vault/_Context/brand/. A gate encodes
the author's taste, so it is transcribed from what the author said in a
brand-gate run's interview and never generated. This script cannot tell where
the words came from. It checks the file's shape and that its provenance names
the author, a date in the run and the run itself; it shows the author the WHOLE
file; and it writes only after the author's go-ahead.

    python studio/pipeline/gate_md.py lint  <gate> [...]
    python studio/pipeline/gate_md.py lint  --all
    python studio/pipeline/gate_md.py plan  <run-id>
    python studio/pipeline/gate_md.py apply <run-id> --confirm

A gate file:

    # <gate>
    ## 0. Provenance        who answered, when, and in which run
    ## 1. <Title>           a numbered section for each thing the gate answers
    ...
    ## N. Unresolved        last, when anything is unanswered: a bullet each

What a gate answers is read from these headings. The spec names the gates and
what each must answer, and nothing more.

`plan` reads runs/<run-id>/gate_update.md, the COMPLETE gate, writes
runs/<run-id>/gate_plan.md with the whole file in it for the author, and keeps
the plan in the run's state.json. `apply` without --confirm is a dry run.

Exit codes: 0 done, 1 refused, 2 usage or configuration error.
Requires pyyaml.
"""

import argparse
import difflib
import re
import sys
from datetime import date, timedelta

from content_md import CREDENTIAL_RES, bearer_links, digest
from studio_common import (
    EXIT_OK, EXIT_REFUSED, EXIT_USAGE, GATE_HEADING_RE, NOT_ANSWERS, SPEC_PATH, Env, Refused,
    Usage, gate_path, latest_confirmation, load_state, log_event, normalize, now, open_console,
    outside_fences, parse_stamp, read_text, save_state, scan, sections, stamp, write_text,
)

DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


# ── the shape of a gate ──────────────────────────────────────────────────────

def lint_gate(text):
    """Errors in a gate file's shape, as sentences."""
    errors = []
    text = normalize(text)
    scanned, open_fence, open_comment = scan(text)
    if open_fence:
        errors.append("a code fence is opened and never closed, so the sections after it are not seen")
    if open_comment:
        errors.append("an HTML comment `<!--` is never closed, so everything after it is hidden")
    visible = [line for _, line, where in scanned if where == "text"]
    first = next((line for line in visible if line.strip()), "")
    if not first.startswith("# "):
        errors.append("a gate opens with a `# <gate>` title line")
    headings = []
    for line in visible:
        if not line.startswith("## "):
            continue
        match = GATE_HEADING_RE.match(line)
        if not match:
            errors.append(f"`{line.strip()[:60]}` is not a gate section. Each is `## N. Title`.")
            continue
        headings.append((int(match.group(1)), match.group(2).strip("*_ ").casefold()))
    if not headings or headings[0][0] != 0 or headings[0][1] != "provenance":
        errors.append("the first section is `## 0. Provenance`: who answered, when, and in which run")
    numbers = [number for number, _ in headings]
    if numbers != sorted(set(numbers)):
        errors.append("the sections are numbered in order, each number once")
    gaps = [index for index, (_, title) in enumerate(headings) if title == "unresolved"]
    if len(gaps) > 1:
        errors.append("a gate has one Unresolved section")
    if gaps and gaps[-1] != len(headings) - 1:
        errors.append("the Unresolved section comes last")
    if not any(number != 0 and title not in NOT_ANSWERS for number, title in headings):
        errors.append("the gate answers nothing: it has no numbered section besides provenance "
                      "and Unresolved")
    for base, names in bearer_links(text):
        errors.append(f"a link to {base} carries {', '.join(names)}. A presigned or share link "
                      "is a credential; it does not go in a gate.")
    for pattern in CREDENTIAL_RES:
        if pattern.search(text):
            errors.append("the gate holds something shaped like a credential")
            break
    if re.search(r"\{\{[^}]*\}\}", "\n".join(line for _, line in outside_fences(text))):
        errors.append("the gate still holds a template placeholder, `{{...}}`")
    return errors


def provenance_errors(state, text):
    """The Provenance section names the author, a date in the run, and the run."""
    found = next((body for title, body in sections(normalize(text))
                  if re.match(r"0\.\s*provenance\b", title, re.I)), None)
    if found is None:
        return ["the gate has no Provenance section"]
    prose = "\n".join(line for _, line in outside_fences(found))
    errors = []
    if not re.search(rf"(?<![\w-]){re.escape(state['run_id'])}(?![\w-])", prose):
        errors.append(f"the Provenance section names the run the gate was transcribed in: "
                      f"`{state['run_id']}`")
    if not re.search(r"\bauthor\b", prose, re.I):
        errors.append("the Provenance section says who answered: the author")
    began = parse_stamp(state["created"]).date() - timedelta(days=1)
    today = max(date.today(), now().date())
    days = []
    for text_ in DATE_RE.findall(prose):
        try:
            days.append(date.fromisoformat(text_))
        except ValueError:
            continue
    if not any(began <= day <= today for day in days):
        errors.append("the Provenance section gives the date of the interview, as YYYY-MM-DD, "
                      "within this run")
    return errors


# ── plan and apply ───────────────────────────────────────────────────────────

def target(env, state):
    """(gate name, path) this run may write. Refused for a run that does not
    write gates, or names none."""
    if env.pipeline(state["pipeline"]).get("writes") != "gate":
        raise Refused(f"`{state['pipeline']}` does not write a brand gate")
    gate = state.get("gate")
    if not gate:
        raise Refused(f"this run names no gate. Set it with: studio_run.py gate {state['run_id']} <gate>")
    if gate not in env.spec["gates"]:
        raise Usage(f"`{gate}` is not a gate in the spec")
    path = gate_path(env, gate).resolve()
    if path.parent != env.context.resolve():
        raise Usage(f"the spec puts `{gate}` outside the gate folder: {path}")
    return gate, path


def make_plan(env, state):
    gate, path = target(env, state)
    proposal = env.run_dir(state["run_id"]) / "gate_update.md"
    if not proposal.is_file():
        raise Refused(f"there is no gate_update.md in {proposal.parent}. Write the complete gate there first.")
    proposed = normalize(read_text(proposal))
    existing = normalize(read_text(path)) if path.is_file() else None
    errors = lint_gate(proposed) + provenance_errors(state, proposed)
    title = next((line for _, line in outside_fences(proposed) if line.strip()), "")
    if title.startswith("# ") and not re.search(rf"(?<![\w-]){re.escape(gate)}(?![\w-])", title):
        errors.append(f"the title line names the gate: `# {gate}`")
    diff = "".join(difflib.unified_diff(
        (existing or "").splitlines(keepends=True), proposed.splitlines(keepends=True),
        fromfile=f"{path.name} (now)", tofile=f"{path.name} (proposed)")) if existing is not None else ""
    return {
        "gate": gate,
        "path": path,
        "is_new": existing is None,
        "proposed_sha": digest(proposed),
        "existing_sha": digest(existing) if existing is not None else None,
        "errors": errors,
        "diff": diff,
        "proposed": proposed,
    }


def render_plan(state, plan):
    verdict = "REFUSED" if plan["errors"] else "ready for the author"
    lines = [
        f"# Gate plan: {state['run_id']}", "",
        f"- gate: `{plan['gate']}` ({'new' if plan['is_new'] else 'rewrites ' + plan['path'].name})",
        f"- verdict: **{verdict}**", "",
    ]
    if plan["errors"]:
        lines += ["## Errors", ""] + [f"- {item}" for item in plan["errors"]] + [""]
    lines += ["## The whole gate, as it would be written", "",
              "~~~~markdown", plan["proposed"].rstrip("\n"), "~~~~", ""]
    if plan["diff"]:
        lines += ["## What changes", "", "~~~~diff", plan["diff"].rstrip("\n"), "~~~~", ""]
    if not plan["errors"]:
        lines += [
            "## To write it", "",
            "Nothing has been written. After the author has read the whole gate and said yes:", "",
            "```",
            f'python studio/pipeline/studio_run.py confirm {state["run_id"]} gate '
            '--words "<what the author said>"',
            f"python studio/pipeline/gate_md.py apply {state['run_id']} --confirm",
            "```", "",
        ]
    return "\n".join(lines)


def cmd_plan(env, args):
    state = load_state(env, args.run_id)
    plan = make_plan(env, state)
    run_dir = env.run_dir(state["run_id"])
    moment = now()
    write_text(run_dir / "gate_plan.md", render_plan(state, plan))
    state["gate_plan"] = {
        "gate": plan["gate"],
        "proposed_sha": plan["proposed_sha"],
        "existing_sha": plan["existing_sha"],
        "ok": not plan["errors"],
        "at": stamp(moment),
        "at_epoch": moment.timestamp(),
    }
    log_event(state, "gate-plan", f"{plan['gate']}: {'refused' if plan['errors'] else 'ready'}")
    save_state(env, state)
    print(f"plan      {run_dir / 'gate_plan.md'}")
    print(f"gate      {plan['gate']}  ({'new' if plan['is_new'] else 'rewrite'})")
    if plan["errors"]:
        raise Refused("the proposed gate is not written:\n    " + "\n    ".join(plan["errors"]))
    print("ready     nothing is written yet. Show the author the whole gate in the plan.")
    return EXIT_OK


def cmd_apply(env, args):
    state = load_state(env, args.run_id)
    planned = state.get("gate_plan")
    if not planned:
        raise Refused("there is no gate plan. Run `gate_md.py plan` and show the author the whole gate first.")
    if planned["gate"] != state.get("gate"):
        raise Refused(f"the plan was made for `{planned['gate']}`, and this run names "
                      f"`{state.get('gate')}`. Plan again.")
    if not planned["ok"]:
        raise Refused("the gate plan on file was refused. Fix the gate and plan again.")
    plan = make_plan(env, state)
    if plan["errors"]:
        raise Refused("the proposed gate is not written:\n    " + "\n    ".join(plan["errors"]))
    if plan["proposed_sha"] != planned["proposed_sha"]:
        raise Refused("gate_update.md changed after the plan was made. "
                      "The author has not seen this version. Plan again.")
    if plan["existing_sha"] != planned["existing_sha"]:
        raise Refused("the gate on disk changed after the plan was made. Plan again.")
    if not args.confirm:
        print("DRY RUN   nothing is written without --confirm.")
        print(f"would write  {plan['path']}")
        print(f"preview      {env.run_dir(state['run_id']) / 'gate_plan.md'}")
        return EXIT_OK
    given = latest_confirmation(state, "gate")
    if not given:
        raise Refused("no go-ahead is recorded for `gate`. After the author has read the whole gate "
                      f'and said yes: studio_run.py confirm {state["run_id"]} gate --words "<what the author said>"')
    if given["at_epoch"] < planned["at_epoch"]:
        raise Refused("the recorded go-ahead is older than the plan. "
                      "The author has not confirmed this gate. Show it, then confirm again.")
    write_text(plan["path"], plan["proposed"])
    moment = now()
    state["gate_written"] = {"gate": plan["gate"], "sha": plan["proposed_sha"],
                             "at": stamp(moment), "at_epoch": moment.timestamp()}
    state["gate_plan"] = None
    log_event(state, "gate-apply", plan["gate"])
    save_state(env, state)
    print(f"written   {plan['path']}")
    return EXIT_OK


def cmd_lint(env, args):
    names = [name for name in env.spec["gates"] if gate_path(env, name).is_file()] if args.all \
        else args.gates
    if not names:
        print(f"no gates under {env.context}")
        return EXIT_OK
    failed = 0
    for name in names:
        if name not in env.spec["gates"]:
            raise Usage(f"no gate `{name}` in the spec")
        path = gate_path(env, name)
        if not path.is_file():
            raise Usage(f"`{name}` is not authored: there is no {path.name}")
        errors = lint_gate(read_text(path))
        print(f"{'FAIL' if errors else 'ok  '}  {name}")
        for item in errors:
            print(f"        error    {item}")
        failed += bool(errors)
    print(f"{len(names)} gate(s), {failed} failing")
    return EXIT_REFUSED if failed else EXIT_OK


# ── entry ────────────────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="gate_md.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", default=str(SPEC_PATH), help="the spec to read")
    parser.add_argument("--runs-dir", help="where runs are kept (default: from the spec)")
    parser.add_argument("--vault-dir", help="the vault (default: from the spec)")
    parser.add_argument("--context-dir", help="the brand gates (default: from the spec)")
    parser.add_argument("--assets-dir", help="where kept artifacts go (default: from the spec)")
    commands = parser.add_subparsers(dest="command", required=True)

    lint = commands.add_parser("lint", help="check gate files for their shape")
    lint.add_argument("gates", nargs="*", help="gate names")
    lint.add_argument("--all", action="store_true", help="every authored gate")
    lint.set_defaults(run=cmd_lint)

    plan = commands.add_parser("plan", help="preview a gate write; writes nothing to the gate folder")
    plan.add_argument("run_id")
    plan.set_defaults(run=cmd_plan)

    apply_ = commands.add_parser("apply", help="write the planned gate")
    apply_.add_argument("run_id")
    apply_.add_argument("--confirm", action="store_true",
                        help="write it. Without this, apply is a dry run.")
    apply_.set_defaults(run=cmd_apply)
    return parser


def main(argv=None):
    open_console()
    args = build_parser().parse_args(argv)
    if args.command == "lint" and not args.all and not args.gates:
        print("error     give a gate, or --all", file=sys.stderr)
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
