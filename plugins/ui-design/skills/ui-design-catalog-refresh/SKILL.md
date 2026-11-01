---
name: ui-design-catalog-refresh
description: Refreshes the ui-design catalog's upstream-derived data -- the Google Fonts and Phosphor icon catalogs -- by fetching the upstream sources, generating review-only candidates under the plugin's maintenance/candidates/, diffing them against the live rows, and stopping for human review. Use when the upstream catalogs may have moved or a refresh is due, not for editing curated rows by hand. Never promotes a candidate on its own.
---

# UI design catalog refresh

Refreshes the two catalogs in `${CLAUDE_PLUGIN_ROOT}/catalog/data/` that are derived from
upstream sources: `google-fonts.csv` with `google-font-licenses.json`, and
`phosphor-icons-upstream.json`. It replaces the weekly GitHub workflow the
catalog came from; it is the human-run equivalent, and it keeps that workflow's
shape: fetch upstream, generate **candidates** into a scratch directory, diff
them against the live rows, and stop for review.

This must run as a skill, not a standalone script: the review step needs the
Agent tool to invoke the `ui-design:ui-design-catalog-reviewer` agent, and the
decision to promote is the maintainer's.

This is maintenance work for whoever keeps the catalog, not something a project
that merely uses the plugin needs.

## Where this may run

`${CLAUDE_PLUGIN_ROOT}` is this plugin's install directory, and every path below starts from it.
Your working directory is a project, not the plugin. If a path shows a `$`
followed by `{CLAUDE_PLUGIN_ROOT}` where an absolute path should be, the
variable was not expanded: stop and say so.

**Refuse to run from an installed copy.** Claude Code keeps every installed
plugin version in its own cache directory, and anything written there is thrown
away when the plugin updates. This skill writes candidates under the plugin and,
after approval, promotes data into it, so on an installed copy the work would be
lost and the installed data would drift from the published plugin. Before doing
anything else, look at the plugin directory's path: if it contains `plugins/cache`
or `plugins\cache`, stop, report that, and tell the user to run the skill from a
clone of the plugin's repository, loaded for the session with
`claude --plugin-dir <path to the clone>`. Do not work around this by copying the
plugin somewhere else.

Read `${CLAUDE_PLUGIN_ROOT}/spec.yaml` first; it names the catalog root and the standing
rules. Live data is `${CLAUDE_PLUGIN_ROOT}/catalog/data/`. Everything this skill writes goes
under `${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/` (gitignored): candidates at its top
level, fetched inputs in `raw/`, change reports and diffs in `reports/`.

## Rules that do not bend

- **Read-only against live data.** Never write under `${CLAUDE_PLUGIN_ROOT}/catalog/data/`
  during a refresh. Only `${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/` is written.
- **Promoting a candidate is an editorial decision with a licensing dimension**
  (see `${CLAUDE_PLUGIN_ROOT}/SOURCE-RESEARCH.md`). `catalog-summary.json` records three
  standing policies: a changed family set needs explicit approval, the
  relevance gate must pass, and unlicensed families stay excluded. You report;
  the maintainer decides.
- **Never print, log or ask for `GOOGLE_FONTS_API_KEY`.** Test only whether it is
  set, and never put its value in a command, a file or a message. It is read
  from the environment (see `${CLAUDE_PLUGIN_ROOT}/maintenance/.env.example`); if it is
  unset, say so and stop the fonts half.
- **Never install anything.** If `git`, `node` or `npm` is missing, skip the half
  that needs it and say so. Never run a package-manager or system-modifying
  command to fix that.
- **Never delete a marker or lock.** `.google-font-refresh.incomplete.json` means
  a prior refresh was interrupted and needs review; `.google-font-refresh.lock`
  means one may still be running. Report either and stop that half.

## Arguments

Parse from the skill's `args` (space-separated, any order):
- `--fonts-only` / `--icons-only` — run one half. With neither, run both.
- `--dry-run` — do step 1 and report what would run; make zero network calls
  and write zero files.

## Procedure

1. **Preflight.** Confirm the plugin path is not an installed cache copy (see
   "Where this may run") and that `${CLAUDE_PLUGIN_ROOT}/spec.yaml` exists. Run
   `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/validate_data.py"`; if the live data is not
   already clean, stop and report that first, because a diff against unhealthy
   data proves nothing. Then check, without printing values: is
   `GOOGLE_FONTS_API_KEY` set; do `git --version`, `node --version` and
   `npm --version` succeed. Fonts need the key and `git`; icons need `node` and
   `npm`. In `--dry-run`, report and stop here.

2. **Fetch upstream** into `${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/` (network):
   a sparse clone of `google/fonts` for the licence metadata, and the pinned
   Phosphor npm packages for icons. Never bump the pinned versions.
3. **Generate candidates** with `refresh-google-fonts.py` and `refresh-icon-catalog.py`,
   saving each JSON change report under `.../candidates/reports/`. A non-zero exit
   means the candidate failed validation: report the stderr and stop that half.
4. **Diff against live** with `git diff --no-index` (exit 1 means they differ, which
   is expected). A candidate with no diff is reported as unchanged and skipped.

   The exact commands for steps 2-4 are in
   `${CLAUDE_PLUGIN_ROOT}/references/refresh-commands.md`; read it before running them.

5. **Review.** For each candidate that differs, invoke the
   `ui-design:ui-design-catalog-reviewer` subagent via the Agent tool, once per file, giving
   it the candidate path, its diff path and the change report path. Parse the
   `FILE`, `DELTA`, `OVERALL`, `ROW`, `[UNVERIFIED ...]` and `NOTES` lines. Do not
   act on a verdict yourself, and do not treat an `[UNVERIFIED ...]` line as
   resolved.

6. **Report, then stop.** Give the maintainer, per file: the row counts and deltas,
   families or icons added and removed (from the change report), every `BLOCK`
   and `FLAG` row, the reviewer's `[UNVERIFIED ...]` items, and the candidates'
   paths. State plainly that nothing has been promoted and that a changed
   family set needs the maintainer's explicit approval. Do not promote on a
   guess, and do not treat "looks fine" as approval.

## After the maintainer approves

Only when the maintainer says in chat to promote a named candidate, and never
inferred from anything else:

Promote only that candidate, following the numbered steps in
`${CLAUDE_PLUGIN_ROOT}/references/refresh-commands.md` ("After approval"): copy it over
its live file, regenerate the catalog summary, check the relevance metrics (stop if
any moved: that is a ranking change and the maintainer's call), refresh the
fingerprints only if none moved, and run `verify.py`. Leave the changes uncommitted
for the maintainer.

## Pacing note

Refresh one half at a time when a family set changes: review the fonts diff,
let the maintainer decide, then do icons. Do not chain a refresh into a promotion
in one uninterrupted pass.
