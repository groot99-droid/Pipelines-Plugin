---
description: Check which internet platforms Agent Reach can read right now and what each missing one needs
---
Run `agent-reach doctor --json` and summarise it in one table: platform, ready or not, active backend, and the one thing it still needs. `active_backend: null` means doctor chose not to probe live, not that nothing is installed.

If the `agent-reach` command is missing, follow the `reach-setup` skill (`${CLAUDE_PLUGIN_ROOT}/skills/reach-setup/SKILL.md`) and give the user the install line to run themselves.

This command only checks. Do not run `install`, `configure` or `setup`, do not open `~/.agent-reach/`, and do not ask for or print any cookie or token.
