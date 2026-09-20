---
name: ui-design-catalog-refresh
description: Refreshes the ui-design catalog's upstream-derived data -- the Google Fonts and Phosphor icon catalogs -- by fetching the upstream sources, generating review-only candidates under ui-design/maintenance/candidates/, diffing them against the live rows, and stopping for human review. Use when the upstream catalogs may have moved or a refresh is due, not for editing curated rows by hand. Never promotes a candidate on its own.
---

# UI design catalog refresh

Refreshes the two catalogs in `ui-design/catalog/data/` that are derived from
upstream sources: `google-fonts.csv` with `google-font-licenses.json`, and
`phosphor-icons-upstream.json`. It replaces the weekly GitHub workflow the
catalog came from; Pipelines has no CI, so this is the human-run equivalent, and
it keeps that workflow's shape: fetch upstream, generate **candidates** into a
scratch directory, diff them against the live rows, and stop for review.

This must run as a skill, not a standalone script: the review step needs the
Agent tool to invoke `.claude/agents/ui-design-catalog-reviewer.md`, and the
decision to promote is the author's.

## Paths

Your working directory is the Pipelines repo root. All paths are relative to it.
Read `ui-design/spec.yaml` first; it names the catalog root and the standing
rules. Live data is `ui-design/catalog/data/`. Everything this skill writes goes
under `ui-design/maintenance/candidates/` (gitignored): candidates at its top
level, fetched inputs in `raw/`, change reports and diffs in `reports/`.

## Rules that do not bend

- **Read-only against live data.** Never write under `ui-design/catalog/data/`
  during a refresh. Only `ui-design/maintenance/candidates/` is written.
- **Promoting a candidate is an editorial decision with a licensing dimension**
  (see `ui-design/SOURCE-RESEARCH.md`). `catalog-summary.json` records three
  standing policies: a changed family set needs explicit approval, the
  relevance gate must pass, and unlicensed families stay excluded. You report;
  the author decides.
- **Never print, log or ask for `GOOGLE_FONTS_API_KEY`.** Test only whether it is
  set, and never put its value in a command, a file or a message. It is read
  from the environment (see `ui-design/maintenance/.env.example`); if it is
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

1. **Preflight.** Confirm `ui-design/spec.yaml` exists. Run
   `python ui-design/catalog/scripts/validate_data.py`; if the live data is not
   already clean, stop and report that first, because a diff against unhealthy
   data proves nothing. Then check, without printing values: is
   `GOOGLE_FONTS_API_KEY` set; do `git --version`, `node --version` and
   `npm --version` succeed. Fonts need the key and `git`; icons need `node` and
   `npm`. In `--dry-run`, report and stop here.

2. **Fetch upstream** into `ui-design/maintenance/candidates/raw/` (network).
   - Fonts licence metadata: a sparse clone of `google/fonts` limited to its
     `METADATA.pb` files, then record its commit.
     ```
     git clone --depth 1 --filter=blob:none --no-checkout https://github.com/google/fonts.git ui-design/maintenance/candidates/raw/google-fonts
     git -C ui-design/maintenance/candidates/raw/google-fonts sparse-checkout init --no-cone
     git -C ui-design/maintenance/candidates/raw/google-fonts ls-tree -r --name-only HEAD
     ```
     Filter that listing to paths ending in `METADATA.pb`, pass them to
     `sparse-checkout set --stdin`, run `checkout`, and take
     `git -C <that directory> rev-parse HEAD` as the 40-character revision.
   - Icons: in `ui-design/maintenance/candidates/raw/npm/`, `npm init --yes`, then
     `npm install --ignore-scripts --no-audit --no-fund` of
     `@phosphor-icons/core` and `@phosphor-icons/react` at the versions pinned as
     `PACKAGE_VERSION` and `REACT_VERSION` in
     `ui-design/maintenance/refresh-icon-catalog.py`, plus `react@19`. Read
     those constants; do not hardcode them here, and never bump them yourself —
     a version bump is the author's call. Then write
     `phosphor-core.json` (the `icons` export of `@phosphor-icons/core`) and
     `phosphor-react-exports.json` (`{"client": [...], "ssr": [...]}`, the sorted
     export names of `@phosphor-icons/react` and `@phosphor-icons/react/ssr`)
     with a short `node --input-type=module` script, and copy both packages'
     `package.json` next to them as `phosphor-core-package.json` and
     `phosphor-react-package.json`.

3. **Generate candidates.** Use today's date as `<date>` (`YYYY-MM-DD`). Each
   command prints a JSON change report on stdout; save it under
   `ui-design/maintenance/candidates/reports/`. A non-zero exit means the
   candidate failed validation: report the stderr and stop that half.
   `--approve-changes` is passed because the output is a staged candidate, not
   live data; the approval that matters is promotion, covered under "After the
   author approves". Shown wrapped; run each as one line.
   ```
   python ui-design/maintenance/refresh-google-fonts.py --live
     --metadata-root ui-design/maintenance/candidates/raw/google-fonts
     --metadata-revision <40-char sha from step 2>
     --existing-csv ui-design/catalog/data/google-fonts.csv
     --output-csv ui-design/maintenance/candidates/google-fonts.csv
     --license-output ui-design/maintenance/candidates/google-font-licenses.json
     --verified-at <date> --approve-changes

   python ui-design/maintenance/refresh-icon-catalog.py
     --input ui-design/maintenance/candidates/raw/npm/phosphor-core.json
     --package-json ui-design/maintenance/candidates/raw/npm/phosphor-core-package.json
     --react-package-json ui-design/maintenance/candidates/raw/npm/phosphor-react-package.json
     --react-exports-input ui-design/maintenance/candidates/raw/npm/phosphor-react-exports.json
     --curated-csv ui-design/catalog/data/icons.csv
     --output ui-design/maintenance/candidates/phosphor-icons-upstream.json
     --verified-at <date>
   ```

4. **Diff against live.** For each candidate file, save a diff under
   `ui-design/maintenance/candidates/reports/`:
   `git diff --no-index -- ui-design/catalog/data/<file> ui-design/maintenance/candidates/<file>`.
   That command exits 1 when the files differ; that is the expected result, not
   an error. A candidate with no diff is reported as unchanged and skipped.

5. **Review.** For each candidate that differs, invoke the
   `ui-design-catalog-reviewer` subagent via the Agent tool, once per file, giving
   it the candidate path, its diff path and the change report path. Parse the
   `FILE`, `DELTA`, `OVERALL`, `ROW`, `[UNVERIFIED ...]` and `NOTES` lines. Do not
   act on a verdict yourself, and do not treat an `[UNVERIFIED ...]` line as
   resolved.

6. **Report, then stop.** Give the author, per file: the row counts and deltas,
   families or icons added and removed (from the change report), every `BLOCK`
   and `FLAG` row, the reviewer's `[UNVERIFIED ...]` items, and the candidates'
   paths. State plainly that nothing has been promoted and that a changed
   family set needs the author's explicit approval. Do not promote on a
   guess, and do not treat "looks fine" as approval.

## After the author approves

Only when the author says in chat to promote a named candidate, and never
inferred from anything else:

1. Copy the approved candidate over its live file in `ui-design/catalog/data/`.
2. `python ui-design/maintenance/generate-catalog-summary.py --verified-at <date>`.
   Then update the bold count tokens in the root `README.md` that its `--check`
   names, if they moved.
3. The relevance fingerprint hashes every CSV under `catalog/data`, so
   `python ui-design/maintenance/evaluate-relevance.py` will now fail with a
   fingerprint mismatch. That is by design. Run it with `--no-thresholds` and
   compare its `metrics` with `ui-design/catalog/scripts/tests/fixtures/relevance-baseline.json`.
   If any metric moved, stop: that is a ranking change and the author's call.
   If none moved, regenerate `runtimeFingerprint` and `oracleFingerprint` in
   `relevance-thresholds.json` and rewrite the baseline with
   `--no-thresholds --write-baseline`.
4. `python ui-design/maintenance/verify.py` must pass. Leave the changes
   uncommitted for the author.

## Pacing note

Refresh one half at a time when a family set changes: review the fonts diff,
let the author decide, then do icons. Do not chain a refresh into a promotion
in one uninterrupted pass.
