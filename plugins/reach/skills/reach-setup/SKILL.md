---
name: reach-setup
description: Check whether Agent Reach is installed and healthy, show which internet platforms are reachable, and explain exactly what each missing one needs. Use when the user wants Claude to read the web, search, YouTube, Reddit, GitHub, Bilibili or RSS and `agent-reach` is not yet set up, or when a fetch failed and the cause may be a missing tool or login. Not for fetching content itself (that is the agent-reach skill).
---

# Reach setup

All paths here start from `${CLAUDE_PLUGIN_ROOT}`. Reading content is the `agent-reach` skill's job
(`${CLAUDE_PLUGIN_ROOT}/skills/agent-reach/SKILL.md`); this skill only gets the machine ready.

## Steps

1. **Is it installed?** Run `agent-reach version`. If the command is missing, tell the user and give
   them this to run themselves; do not run it for them without a yes:

   ```
   pipx install "git+https://github.com/groot99-droid/Pipelines-Plugin.git#subdirectory=agent-reach"
   ```

   (`python -m venv` plus `pip install` works if `pipx` is not there. Python 3.10 or newer.)
2. **Check, do not change.** `agent-reach doctor --json` reports each platform: `status`, `backends`
   and `active_backend`. `agent-reach install --env=auto` is check-only by default. Summarise the
   result in one table: platform, ready or not, and the one thing it still needs.
   `active_backend: null` means doctor chose not to probe live, not that nothing is installed.
3. **Changes need a yes.** `agent-reach install --system`, `--channels ...` and `configure` change
   the machine or write credentials. Say what each would install or write, and wait for the user.
   Offer `--dry-run` first.
4. **Logins are the user's.** Twitter and XiaoHongShu need a Cookie-Editor export done by the user in
   their browser; Reddit needs a logged-in session. Explain the steps from
   `${CLAUDE_PLUGIN_ROOT}/skills/agent-reach/references/`, and never attempt a login yourself.

## Worked example

User: "Claude can't read this YouTube link, why?"

1. `agent-reach version` prints a version line, so it is installed.
2. `agent-reach doctor --json` lists each platform with `status`, `backends` and `active_backend`.
   Say what it showed, as a table:

   | Platform | Ready | Still needs |
   |----------|-------|-------------|
   | youtube  | no    | `yt-dlp` is not on PATH (give the install line; wait for a yes) |
   | rss      | yes   | nothing |

3. Do not install anything. Offer `agent-reach install --env=auto --dry-run` to show what would change,
   and once the user says yes, hand over to the `agent-reach` skill to fetch the link.

## Never

- Read, print, echo or ask for anything in `~/.agent-reach/` (config, cookies, tokens), or paste a
  key into a command line.
- Run `sudo`, or install a package the doctor output does not name.
- Post, comment or like through any of these tools.
