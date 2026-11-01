---
description: List the studio's runs and where each one stands (stage, parked, go-ahead recorded)
---
Run `python studio/pipeline/studio_run.py status` from the repo root. If $ARGUMENTS names a run id, run `python studio/pipeline/studio_run.py status $ARGUMENTS` instead.

Report each run as one line: id, pipeline, current stage, whether it is parked, and whether the author's go-ahead for that stage has been recorded. Read-only: do not advance, confirm, back, park, unpark or keep anything, and never edit a run's `state.json`.
