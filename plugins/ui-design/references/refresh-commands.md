# Refresh commands (ui-design-catalog-refresh, on demand)

The commands the `ui-design-catalog-refresh` skill runs. Paths start from the plugin root; quote every one, an install path can contain spaces.

## Steps 2-4: fetch, generate, diff

2. **Fetch upstream** into `${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/` (network). Quote every
   path: an install path can contain spaces.
   - Fonts licence metadata: a sparse clone of `google/fonts` limited to its
     `METADATA.pb` files, then record its commit.
     ```
     git clone --depth 1 --filter=blob:none --no-checkout https://github.com/google/fonts.git "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/google-fonts"
     git -C "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/google-fonts" sparse-checkout init --no-cone
     git -C "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/google-fonts" ls-tree -r --name-only HEAD
     ```
     Filter that listing to paths ending in `METADATA.pb`, pass them to
     `sparse-checkout set --stdin`, run `checkout`, and take
     `git -C <that directory> rev-parse HEAD` as the 40-character revision.
   - Icons: in `${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/npm/`, `npm init --yes`, then
     `npm install --ignore-scripts --no-audit --no-fund` of
     `@phosphor-icons/core` and `@phosphor-icons/react` at the versions pinned as
     `PACKAGE_VERSION` and `REACT_VERSION` in
     `${CLAUDE_PLUGIN_ROOT}/maintenance/refresh-icon-catalog.py`, plus `react@19`. Read
     those constants; do not hardcode them here, and never bump them yourself —
     a version bump is the maintainer's call. Then write
     `phosphor-core.json` (the `icons` export of `@phosphor-icons/core`) and
     `phosphor-react-exports.json` (`{"client": [...], "ssr": [...]}`, the sorted
     export names of `@phosphor-icons/react` and `@phosphor-icons/react/ssr`)
     with a short `node --input-type=module` script, and copy both packages'
     `package.json` next to them as `phosphor-core-package.json` and
     `phosphor-react-package.json`.

3. **Generate candidates.** Use today's date as `<date>` (`YYYY-MM-DD`). Each
   command prints a JSON change report on stdout; save it under
   `${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/reports/`. A non-zero exit means the
   candidate failed validation: report the stderr and stop that half.
   `--approve-changes` is passed because the output is a staged candidate, not
   live data; the approval that matters is promotion, covered under "After the
   maintainer approves". Shown wrapped; run each as one line.
   ```
   python "${CLAUDE_PLUGIN_ROOT}/maintenance/refresh-google-fonts.py" --live
     --metadata-root "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/google-fonts"
     --metadata-revision <40-char sha from step 2>
     --existing-csv "${CLAUDE_PLUGIN_ROOT}/catalog/data/google-fonts.csv"
     --output-csv "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/google-fonts.csv"
     --license-output "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/google-font-licenses.json"
     --verified-at <date> --approve-changes

   python "${CLAUDE_PLUGIN_ROOT}/maintenance/refresh-icon-catalog.py"
     --input "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/npm/phosphor-core.json"
     --package-json "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/npm/phosphor-core-package.json"
     --react-package-json "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/npm/phosphor-react-package.json"
     --react-exports-input "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/raw/npm/phosphor-react-exports.json"
     --curated-csv "${CLAUDE_PLUGIN_ROOT}/catalog/data/icons.csv"
     --output "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/phosphor-icons-upstream.json"
     --verified-at <date>
   ```

4. **Diff against live.** For each candidate file, save a diff under
   `${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/reports/`:
   `git diff --no-index -- "${CLAUDE_PLUGIN_ROOT}/catalog/data/<file>" "${CLAUDE_PLUGIN_ROOT}/maintenance/candidates/<file>"`.
   That command exits 1 when the files differ; that is the expected result, not
   an error. A candidate with no diff is reported as unchanged and skipped.

## After approval

Only when the maintainer says in chat to promote a named candidate.

1. Copy the approved candidate over its live file in `${CLAUDE_PLUGIN_ROOT}/catalog/data/`.
2. `python "${CLAUDE_PLUGIN_ROOT}/maintenance/generate-catalog-summary.py" --verified-at <date>`.
   Then update the bold count tokens in `${CLAUDE_PLUGIN_ROOT}/README.md` that its `--check`
   names, if they moved.
3. The relevance fingerprint hashes every CSV under `catalog/data`, so
   `python "${CLAUDE_PLUGIN_ROOT}/maintenance/evaluate-relevance.py"` will now fail with a
   fingerprint mismatch. That is by design. Run it with `--no-thresholds` and
   compare its `metrics` with `${CLAUDE_PLUGIN_ROOT}/catalog/scripts/tests/fixtures/relevance-baseline.json`.
   If any metric moved, stop: that is a ranking change and the maintainer's call.
   If none moved, regenerate `runtimeFingerprint` and `oracleFingerprint` in
   `relevance-thresholds.json` and rewrite the baseline with
   `--no-thresholds --write-baseline`.
4. `python "${CLAUDE_PLUGIN_ROOT}/maintenance/verify.py"` must pass. Leave the changes
   uncommitted for the maintainer.
