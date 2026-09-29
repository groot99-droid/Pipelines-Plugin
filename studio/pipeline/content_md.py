"""Content MD lint and writer.

The one way a note gets into the studio vault. It checks a proposed note
against studio/vault/SCHEMA.md, previews the change, and writes only after the
author has seen that preview and said yes.

    python studio/pipeline/content_md.py lint  <vault-relative path> [...]
    python studio/pipeline/content_md.py lint  --all
    python studio/pipeline/content_md.py plan  <run-id> [--as record|flush|park]
    python studio/pipeline/content_md.py apply <run-id> [--as record|flush|park] --confirm

`plan` reads runs/<run-id>/note_update.md, which is the COMPLETE note as it
should read afterwards, and writes runs/<run-id>/record_plan.md.
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
import json
import re
import sys

from studio_common import (
    EXIT_OK, EXIT_REFUSED, EXIT_USAGE, SPEC_PATH, Env, Refused, Usage,
    attestation_rows, cited_notes, current_stage, latest_confirmation, level_of,
    load_state, load_yaml, log_event, normalize, now, open_console, outside_fences, read_text,
    resolve_note, save_state, sections, split_note, squeeze, stamp, vault_notes,
    write_text,
)

PURPOSES = ("record", "flush", "park")

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ANY_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
TIMELINE_HEADING_RE = re.compile(r"^### (\d{4}-\d{2}-\d{2}) · \S")
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.I)

# Query parameters that make a link work as a credential for whoever holds it.
BEARER_PARAMETERS = (
    "x-amz-signature", "x-amz-credential", "x-amz-security-token", "x-goog-signature",
    "x-goog-credential", "signature", "sig", "token", "access_token", "auth",
    "authorization", "apikey", "api_key", "key", "secret", "sas",
)
# Links that open for anyone who has them, by host and path.
SHARE_LINK_RES = (
    re.compile(r"^https?://(?:drive|docs)\.google\.com/.*[?&]usp=(?:sharing|share_link|drive_link)", re.I),
    re.compile(r"^https?://(?:www\.)?dropbox\.com/(?:s|sh|scl)/", re.I),
    re.compile(r"^https?://(?:[\w-]+\.)?app\.box\.com/s/", re.I),
    re.compile(r"^https?://(?:[\w-]+\.)?box\.com/s/", re.I),
    re.compile(r"^https?://[\w-]+\.sharepoint\.com/:[a-z]:/", re.I),
    re.compile(r"^https?://[\w-]+-my\.sharepoint\.com/", re.I),
    re.compile(r"^https?://1drv\.ms/", re.I),
    re.compile(r"^https?://onedrive\.live\.com/.*[?&](?:authkey|resid)=", re.I),
    re.compile(r"^https?://(?:we\.tl|wetransfer\.com/downloads)/", re.I),
    re.compile(r"^https?://(?:[\w-]+\.)?adobe\.com/.*(?:/link/|[?&]x_api_client_id=)", re.I),
)
CREDENTIAL_RES = (
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    re.compile(r"\bgsk_[A-Za-z0-9]{8,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
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
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def bullets(text):
    """The list items of a section, each with its continuation lines joined."""
    items = []
    for line in without_comments(text).split("\n"):
        if re.match(r"^\s*[-*] ", line):
            items.append(line.strip())
        elif line.strip() and items and line.startswith((" ", "\t")):
            items[-1] += " " + line.strip()
        elif not line.strip():
            continue
        else:
            items.append(line.strip())
    return items


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


# ── lint ─────────────────────────────────────────────────────────────────────

def bearer_links(text):
    found = []
    for url in URL_RE.findall(text):
        base = url.split("?", 1)[0]
        if any(pattern.search(url) for pattern in SHARE_LINK_RES):
            found.append((base, ["a share link"]))
            continue
        if "?" not in url:
            continue
        query = url.split("?", 1)[1]
        names = {pair.split("=", 1)[0].lower() for pair in re.split(r"[&;]", query) if "=" in pair}
        hit = sorted(names.intersection(BEARER_PARAMETERS))
        if hit:
            found.append((base, hit))
    return found


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
    for gate in lists["context_brand"]:
        if gate not in env.spec["gates"]:
            errors.append(f"`context_brand` names `{gate}`, which is not a gate in the spec. "
                          "The ladder looks notes up by this field.")
    for name in lists["pipelines"]:
        if name not in env.spec["pipelines"]:
            warnings.append(f"`pipelines` names `{name}`, which is not in the spec")

    found = sections(body)
    titles = [title for title, _ in found]
    canonical = rules["sections"]

    preamble = "" if body.startswith("## ") else body.split("\n## ", 1)[0]
    before = [line for line in without_comments(preamble).split("\n") if line.strip()]
    only_a_title = len(before) == 1 and re.match(r"^# \S", before[0])
    if before and not only_a_title:
        errors.append("there is text before the first section. The first screenful answers "
                      "what this is and what to do next; only a `# title` line may come first.")

    for title in titles:
        if title not in canonical:
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

    steps = bullets(content.get("Next Steps", ""))
    if str(status) == "blocked":
        if not steps or not steps[0].startswith("- [ ]"):
            errors.append("status is `blocked`, so the first item under Next Steps must be "
                          "the blocker, as an open checkbox, saying what would unblock it")
    if content.get("Next Steps") and not any(step.startswith(("- [ ]", "- [x]", "- [X]")) for step in steps):
        errors.append("`## Next Steps` holds no checkbox items")

    marker = env.spec["ladder"]["provisional_marker"]
    least = env.spec["ladder"]["levels"]["L2"]["min_notes"]
    for item in bullets(content.get("Decisions in Force", "")):
        if marker in item and len(cited_notes(item)) < least:
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

    for base, names in bearer_links(text):
        errors.append(f"a link to {base} carries {', '.join(names)}. "
                      "A presigned or share link is a credential; it does not go in a note.")
    for pattern in CREDENTIAL_RES:
        if pattern.search(text):
            errors.append("the note holds something shaped like a credential")
            break

    if re.search(r"\{\{[^}]*\}\}", text):
        errors.append("the note still holds a template placeholder, `{{...}}`")

    if relative and kind:
        parts = str(relative).replace("\\", "/").split("/")
        if len(parts) < 2 or parts[-2] != str(kind):
            where = f"`{parts[-2]}/`" if len(parts) >= 2 else "the vault root"
            warnings.append(f"the note sits in {where} but its kind is `{kind}`. "
                            "SCHEMA.md places a note at <project>/<kind>/<slug>.md.")
    return errors, warnings


# ── plan and apply ───────────────────────────────────────────────────────────

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


def first_step(proposed):
    _, body, _ = parse(proposed)
    steps = bullets(dict(sections(body)).get("Next Steps", ""))
    return steps[0] if steps else ""


def purpose_errors(env, state, purpose, proposed):
    """What a note must say because of why it is being written."""
    errors = []
    front, body, _ = parse(proposed)
    if front is None:
        return errors
    run_dir = env.run_dir(state["run_id"])
    lead = first_step(proposed)

    if purpose == "park":
        if state["status"] != "parked" or not state.get("parked"):
            return ["the run is not parked. Park it with studio_run.py park first."]
        if str(front.get("status")) != "blocked":
            errors.append("the run is being parked, so the note's status must be `blocked`")
        constraint = state["parked"]["constraint"]
        if squeeze(constraint) not in squeeze(lead):
            errors.append(f"the first item under Next Steps must name what the run is blocked "
                          f"on: `{constraint}`")

    if purpose == "flush":
        stage = current_stage(env, state)
        if stage is None:
            return ["the run is complete. There is nothing to resume, so nothing to flush."]
        names_stage = re.search(rf"(?<![\w-]){re.escape(stage['id'])}(?![\w-])", lead, re.I)
        if state["run_id"] not in lead or not names_stage:
            errors.append("the first item under Next Steps must name the run and the stage to "
                          f"resume: `{state['run_id']}` at {stage['id']}")

    if purpose == "record":
        attestation = run_dir / "attestation.md"
        if attestation.is_file():
            marker = env.spec["ladder"]["provisional_marker"]
            decisions = bullets(dict(sections(body)).get("Decisions in Force", ""))
            for row in attestation_rows(read_text(attestation)):
                level = level_of(row)
                if level == "L2":
                    names = {name.casefold() for name in cited_notes(row["source"])}
                    held = any(marker in item and names <= {n.casefold() for n in cited_notes(item)}
                               for item in decisions)
                    if not held:
                        errors.append(
                            f"`{row['constraint']}` was derived. It must appear under Decisions "
                            f"in Force marked {marker}, citing the same notes, so that a later "
                            "run does not recall a derivation as a decision.")
                elif level == "STATED":
                    dates = ANY_DATE_RE.findall(row["source"])
                    held = any("STATED" in item and any(date in item for date in dates)
                               for item in decisions)
                    if not held:
                        errors.append(
                            f"`{row['constraint']}` was stated by the author. It must appear under "
                            f"Decisions in Force as `STATED {dates[0] if dates else '<date>'}: ...`, "
                            "so that the next run recalls it.")
    return errors


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
    note = resolve_note(env, state["note_path"], placing=True)
    existing = normalize(read_text(note)) if note.is_file() else None

    errors, warnings = lint(proposed, env, state["note_path"])
    if existing is not None:
        errors += compare(existing, proposed, env)
    errors += purpose_errors(env, state, purpose, proposed)
    front, _, _ = parse(proposed)
    if front:
        listed = front.get("pipelines")
        if not isinstance(listed, list) or state["pipeline"] not in listed:
            warnings.append(f"`pipelines` does not list `{state['pipeline']}`, which is writing this note")
        for other in vault_notes(env):
            if other.resolve() == note or not front.get("id"):
                continue
            taken = (parse(read_text(other))[0] or {}).get("id")
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
    write_text(run_dir / "record_plan.json", json.dumps({
        "note_path": plan["note_path"],
        "purpose": plan["purpose"],
        "is_new": plan["is_new"],
        "proposed_sha": plan["proposed_sha"],
        "existing_sha": plan["existing_sha"],
        "ok": not plan["errors"],
        "planned_at": stamp(moment),
        "planned_at_epoch": moment.timestamp(),
    }, indent=2) + "\n")
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
    record = run_dir / "record_plan.json"
    if not record.is_file():
        raise Refused("there is no plan. Run `content_md.py plan` and show it to the author first.")
    try:
        planned = json.loads(read_text(record))
    except (json.JSONDecodeError, UnicodeDecodeError):
        planned = None
    wanted = ("purpose", "proposed_sha", "existing_sha", "planned_at_epoch", "ok")
    if not isinstance(planned, dict) or any(key not in planned for key in wanted):
        raise Refused("the plan on file cannot be read. Plan again.")
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

    note = resolve_note(env, state["note_path"], placing=True)
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
    if given["at_epoch"] < planned["planned_at_epoch"]:
        raise Refused("the recorded go-ahead is older than the plan. "
                      "The author has not confirmed this plan. Show it, then confirm again.")

    write_text(note, plan["proposed"])
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
        text = read_text(note)
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
