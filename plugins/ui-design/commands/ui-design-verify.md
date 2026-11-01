---
description: Run every ui-design gate (data, contract, indexes, tests, relevance, smoke) and report which one fails
---
Run `python "${CLAUDE_PLUGIN_ROOT}/maintenance/verify.py"` from any directory. If `python` is not found, try `python3`.

Report the final line (`OK: all N gates passed`, or the failing gate and the exact re-run command it prints). Do not edit data or fingerprints to make a gate pass; a relevance or fingerprint failure after a deliberate data change is the maintainer's call. Do not install anything.
