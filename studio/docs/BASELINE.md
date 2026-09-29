# Baseline

The state of this repo's existing checks before anything under `studio/` was
added. A failure that appears later is measured against this.

Taken on 2026-09-28, on branch `ui-design-plugin` at commit `0d214a2`, with 11
modified and 3 untracked paths in the working tree. Python 3.13.14, pyyaml 6.0.3,
Windows 11.

| Check | Command | Result |
|---|---|---|
| ui-design plugin gate | `python plugins/ui-design/maintenance/verify.py` | 10 of 10 gates passed, 113.4 s |
| creative-writing tests | `python -m unittest discover -s creative-writing/pipeline/tests` | 63 tests, OK, 4.1 s |

The ten gates, in order: validate-csv, validate_data, validate-contract, catalog
summary, indexes, engine tests, maintainer tests, relevance gate, smoke domains,
smoke stacks.

## What this does not cover

- Neither check looks at anything under `studio/`. Its own check is
  `python -m unittest discover -s studio/pipeline/tests`.
- Gate 5 (indexes) and gate 7 (maintainer tests) are the two that a new
  top-level folder, skill or agent can break. Re-run the plugin gate after
  adding one.
