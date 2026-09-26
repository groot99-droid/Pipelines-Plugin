# Changelog

All notable changes to the ui-design plugin. The version here must match
`.claude-plugin/plugin.json`; `maintenance/validate-contract.py` checks that.

## [0.1.0] - Unreleased

First packaging of the ui-design tool as a Claude Code plugin.

### Added

- Plugin manifest and a one-plugin marketplace entry (`.claude-plugin/`).
- Skills `ui-design-catalog`, `ui-design-multipart` and `ui-design-catalog-refresh`, and
  agents `ui-design-search-part`, `ui-design-page-reviewer` and
  `ui-design-catalog-reviewer`, at the plugin root.
- The search catalog (`catalog/`), the brief router (`route.py`, `ROUTER.md`), the
  generated `INDEX.md`, the declared contract (`spec.yaml`) and the rule references.
- Maintenance tooling (`maintenance/`) with one command, `verify.py`, that runs every gate.
- `NOTICE`, listing the upstream sources the data draws on.

### Changed

- Every path in the skills, agents and docs starts from `${CLAUDE_PLUGIN_ROOT}` instead
  of a repository root, so the plugin works from any project once installed.
  `validate-contract.py` now fails on a hard-coded repo path, on a variable placed in
  frontmatter, and on a missing `.gitignore` or `.gitattributes`.
- `route.py` prints commands that point at the script's own location.
- Persisting a design system now requires an explicit `--output-dir` that the user has
  confirmed; nothing is written by default.
- `ui-design-multipart` and `ROUTER.md` say what to do with the router's `not_covered`
  list: report it, and never dispatch an agent for it.
- `ui-design-catalog-refresh` refuses to run from an installed (cached) copy of the
  plugin, because anything written there is discarded on update.
- `route.py` can give one stack its own query for a concern (`STACK_QUERY_OVERRIDES`).
  Next.js and Astro accessibility, which the shared query never reached although both
  stacks have accessibility rows, now use their own wording and are dispatched instead
  of being reported as `not_covered`. No other stack's query changed; a test fails if an
  override stops finding rows in its stack.
- The Astro row "Default to zero JS" now says "JavaScript" and "browser" alongside the
  terse "JS", so plain-language queries reach it. The held-out case
  `stack-astro-zero-js-paraphrase` went from grade 0 to grade 2; `mrrAt3`, `ndcgAt3`,
  `precisionAt1` and `precisionAt3` rose and no metric fell. The relevance fingerprint
  and baseline were regenerated for the changed data. That case was used to choose the
  wording, so it no longer measures generalisation for this row.
- `LICENSE` carries a second copyright line for the additions beside the upstream one.
