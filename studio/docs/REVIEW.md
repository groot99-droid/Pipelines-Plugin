# Review of the studio pipeline, 2026-09-28

Five lenses read and ran the code after the first round of fixes: bypass,
correctness, consistency, dry run, tests. A second agent reproduced each
finding. 59 findings, 1 judged not a problem. They collapse to the problems
below.

**Status: none of these is fixed yet.** The code is as it was when the review
ran: 182 tests pass, and every hole below is open. The first `ui-direction` run
waits on the four marked high.

The full reports were temp files. This is what they said, and the fix decided
for each.

## High

| # | Problem | Fix decided |
|---|---|---|
| 1 | **Record can be finished through a flush or a park.** `note_written` only compares the vault note with `note_update.md`. A note refused as a record can be written `--as flush`, then `confirm record` and `advance` complete the run | Keep the plan and the last write in `state.json` (`plan`, `written`). `note_written` requires the last write to be a `record` write whose sha is the vault note, and re-runs the record checks |
| 2 | **Only the first attestation table is read**, and one inside an HTML comment, an indented block or `<details>` counts. L3 rows in a second table are never seen | Read what a reader sees: comments and fences blanked, a table line indented at most three spaces. Refuse when more than one table has the header |
| 3 | **The L1 quote check is a substring test on the whole section.** A quote of one space passes on a note with no Decisions in Force. Struck-out text, comments, fenced text and text across two bullets all pass | Refuse when the section is missing. Match inside one visible bullet, struck-out text removed, quote at least three words |
| 4 | **A PROVISIONAL decision can be recalled at L1 as resolved**, and the next record can drop the marker | When the bullet holding the quote is PROVISIONAL, the row's state must be PROVISIONAL. Such a row owes a PROVISIONAL bullet at every later write. A PROVISIONAL bullet already in the note stays unless this run's attestation has a STATED row |

## Medium

| # | Problem | Fix decided |
|---|---|---|
| 5 | `apply` never compares the planned note path. `note` can re-point the run after the plan and the yes, and the note lands where no plan named | `apply` refuses when the planned path is not the run's path. `note` drops the plan when the path changes |
| 6 | `record_plan.json` is trusted. A hand-written one lets an old go-ahead write with no preview | The plan lives in `state.json`, the one trusted file. `record_plan.json` is no longer written |
| 7 | Deleting or rewriting `attestation.md` after context turns off the record checks | When context is marked done, the parsed rows are kept in `state.json`. Every later write is checked against them |
| 8 | A flush is not held to the L2 and STATED rule, so a derivation can reach the vault as settled with no record stage, and an author's statement can be lost | Once context is done, every write owes them: record, flush and park |
| 9 | One Decisions line satisfies every row that shares a date or a set of notes | Each owed row takes its own bullet. More rows than bullets is refused. A bullet that does not name the constraint is a warning |
| 10 | A STATED or L2 decision is accepted without its gate in `context_brand`, so the next run cannot recall it | Refuse the write when the gate is missing |
| 11 | `covers_every_need` is a substring test. One row covers several needs, and "NOT the palette" covers `palette` | The Constraint cell equals the need, or starts with it followed by `:` `(` `,` `;` or a dash. One row per need, no duplicates. Extra rows are allowed and still checked |
| 12 | An L0 row's cited file is never read. A row for one gate can cite another gate's file, or none | The Source names the gate's own file and no other gate's |
| 13 | The Timeline check misses a heading written ` ## Timeline` or `##<TAB>Timeline`, a line starting with inline code that opens a phantom fence, and a Timeline written as bullets with no `### ` entries | Lint refuses: an unclosed fence or comment, a heading not at the margin, a heading made by underlining, a section title that differs from a canonical one only in case, a Timeline line before the first entry, and a line that reads like an entry heading but is not one of the entries read |
| 14 | One non-UTF-8 file in the vault, or a UTF-16 stage output, crashes `facts`, `advance`, `plan` and `lint` with a traceback | `read_text` raises a usage error naming the file. A vault scan skips the file and says so |
| 15 | The documents tell the executor to go back a stage and to retry execute. The bookkeeper cannot | Add `studio_run.py back <run-id> --why "..."`: one stage back, that stage's and later go-aheads cleared, what was kept from those stages dropped |
| 16 | The documents say `runs/` may be deleted once the note is written. A flushed or parked note then names a run that is gone | Say: once the run is complete or abandoned. Tell the skill what to do when the named run is missing: a new run on the same note |
| 17 | The lint misses `sk-proj-` keys, a signed link with no scheme, a percent-encoded parameter name, and a link with an apostrophe in its path | Widen the `sk-` pattern. Search the decoded text for the parameter names, with or without a scheme. Stop ending a link at an apostrophe |
| 18 | Record step 7 says to add each gate used to `context_brand`. For product work that files a client's decisions under the studio's gates | Reword to SCHEMA.md's meaning: the gates this note's decisions speak to. Say under "What is not enforced" that the level chosen is not checked against the ladder's order |

## Low

- The L0 check reads the first number after `section`. `section 2-5` passes, though 5 is a declared gap. `sections 2 and 3` is refused. Fix: read every number and range, outside quoted text; accept the plural.
- An L0 row that quotes `visual_identity` section 2 word for word is refused, because the quote holds `§7`. Same fix.
- A STATED row accepts `1999-99-99`. Fix: a real date, not after today, not more than a day before the run was created.
- The path check accepts `nul .md`, a name ending in a newline, a reserved name as a folder, a 300-character name, and a parent that is a file. Fix: `fullmatch`, `ntpath.isreserved`, every part checked, 100 characters, parents walked. `OSError` in either command is exit 2.
- `context_brand: [[visual_identity]]` crashes the lint. Fix: each item is a word.
- A folder named `x.md` crashes every vault scan. Fix: files only.
- A Level cell written `**L0 AUTHORED**` is refused with advice to park. Fix: strip the marks; an unreadable level gets its own message.
- `[[proj/ui/aurora]]` and `[[aurora.md]]` are refused as not in the vault. Fix: index by path as well; drop `.md`.
- A derived row cited by id cannot be matched at record by a note that cites by name. Fix: compare the notes, not the names.
- `back_l1` checks only the first note cited. Fix: every note cited exists and speaks to the gate.
- The lint refuses `* [ ]` and `+ [ ]`, `{{...}}` inside a code fence, and `## Overview ##`. Fix: accept them.
- A flush lead naming run `k-12` passes for run `k-1`. Fix: match the run id on word boundaries.
- A run may write under a kind its pipeline does not make. Fix: the folder is the pipeline's kind.
- `status` drops a run whose state cannot be read. Fix: list it as broken.
- A frontmatter key written twice keeps the last value silently. Fix: refuse a repeated key.

## Documents and the spec

- `spec.yaml` header: gate `file:` and `tokens.file` are relative to `context_root`, not to the spec.
- The comment above `reserved_names` says folders; they are file names.
- The recipe note prints `executes_through.contract` literally. Use `{pipeline.executes_through.contract}`, `.guide` and `.router`, and say that `CLAUDE_PLUGIN_ROOT` here is `plugins/ui-design`.
- The execute note forbids a search not in the recipe and also orders one retry. The recipe names the one retry allowed for each search.
- The execute and record notes ask for provenance fields that only `--design-system` returns. For `--domain` and `--stack`: the domain, the file, and the top row's category and issue.
- The review note: the diff is written by hand against the ten colours in `tokens.json`, and the floors are computed from them, not taken from the engine's report.
- `known_conflicts` `carried-paths` does not cover the `tools/ui-ux-pro-max` commands in `color_science` section 4 and `typography_system` section 5.
- `visual_identity` states no scope for the whole gate. The need "that product work is not bound by it" resolves as STATED, or at L1 from a note that recorded it, until the author adds one. Say so in the pipeline's `open:` list and have `facts` print it.
- The record stage prints "stop and show the author" after the write, while the skill advances straight after `apply`. Give a stage an optional `then:` line in the spec.
- The intake prompt does not name the `note` command, and the consumer is carried only as prose. Add the command, and a `consumer:` line at the top of `brief.md`.
- Nothing says what a studio-surface note holds when the run proposes nothing. An empty proposal goes in the Timeline and under Open Questions; a diff goes in a fenced block under its Next Steps item.
- `_Pipelines/studio.md`: a failed stage leaves the run at the same stage, not its state untouched.
- The skill's flush section does not say to set the note first. The intake prompt says the note is written at record; it can first be written at a flush or a park.
- `_Context/brand/README.md` on font weights is looser than the spec: 500 is for a status word only.

## Tests to add

- Flush then advance at record, and park, unpark, advance at record: both refused.
- A plan refused for a duplicate id, the other note removed, then apply: refused as "the plan on file was refused".
- Advance at record with no record go-ahead.
- Two tables; a table in a comment; a table indented four spaces.
- A blank quote, a one-letter quote, a struck-out line, a quote across two bullets.
- Two STATED rows with one date and one Decisions line.
- The clock-slack test asserts that `confirm` returned 0 and that the refusal is "before the confirmation".
- Assertions that name the exact refusal, where they now accept any.
- Reserved names tested at a valid placement, one run per case.
- Two notes with one file name cited at L1; a file that is not a Content MD cited as precedent; a fenced `### ` line inside the Timeline; a complete run on the same note gives no warning; parking a complete run.

## What held

Nine of the thirteen refusals in the spec are pinned by a test that fails when
the check is removed. 36 of 45 mutations were caught. A whole run that follows
the skill to the letter completes, parks, flushes and resumes as documented. No
review agent wrote into the repo.
