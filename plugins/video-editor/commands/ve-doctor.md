---
description: Show what the video editor has installed and configured (ffmpeg, optional extras, publish credentials by name only)
---
Run `python "${CLAUDE_PLUGIN_ROOT}/bin/ve.py" doctor` and report the result as a short table: each tool or extra, ready or missing, and the one-line install hint for anything missing. If the `python` command is not found, try `python3`.

Do not install anything, do not run `ve publish init` or `revoke`, and do not read the keyring or any `.env`. `doctor` reports credentials by name only; keep it that way.
