# blender-gemini

Lets Claude drive an open Blender through the Gemini CLI.

```
Claude Code ──► gemini MCP server ──► Gemini CLI ──► blender MCP server ──► add-on in Blender
 (.mcp.json)     (gemini-mcp-tool)    (~/.gemini/       (mcp-for-blender,     (socket, localhost
                                       settings.json)    run by uvx)           port 9876)
```

Two halves, each configured once:

| Half | Where | Set up by |
| --- | --- | --- |
| Gemini CLI knows the Blender server | `~/.gemini/settings.json`, `mcpServers.blender` | `python blender-gemini/install.py install` |
| Claude can call Gemini | `.mcp.json` at the repo root, `mcpServers.gemini`; the `blender-gemini` skill | already in the repo; Claude Code asks you to approve the server the first time |

Everything runs on your machine. A Claude Code cloud session has no Blender and no
Gemini login, so the chain only works from a local session.

## Set up

1. **Prerequisites on your machine.** [uv](https://docs.astral.sh/uv/) (for `uvx`), Node.js 16+
   (for `npx`), Blender 3.0+, and a working Gemini CLI login. See "Which CLI" below.
2. **Blender add-on.** `uvx mcp-for-blender install-addon`, then in Blender: Edit → Preferences →
   Add-ons → enable *Interface: MCP for Blender*. Press `N` in the 3D viewport, open the
   *MCP for Blender* tab, click *Start MCP Server*. (`uvx mcp-for-blender setup` also edits
   other AI clients' configs; you don't need it for this.)
3. **Gemini CLI config.**
   ```powershell
   python blender-gemini/install.py install --dry-run     # show the entry, write nothing
   python blender-gemini/install.py install               # read-only profile
   ```
4. **Check.** `python blender-gemini/install.py check` reads, never writes, and names the
   fix for any line that fails. Then start Claude Code in this repo, approve the `gemini`
   server (`/mcp` lists it), and ask for the `blender-gemini` skill.

`uninstall` removes only `mcpServers.blender`. `install` merges into the file: it
refuses one it can't parse as plain JSON (so a settings file with comments is left
alone), keeps the first copy beside it as `settings.json.rosw-bak`, and writes through a
temporary file. `--scope project` uses `./.gemini/settings.json` instead of the user file.

## Profiles

| Profile | Gemini can call | Approval |
| --- | --- | --- |
| `readonly` (default) | `get_scene_info`, `look`, `get_addon_status` | skipped (`trust: true`); they change nothing |
| `full` | every tool except `record_trajectory_feedback`, including `execute_blender_code` | Gemini asks before each call; add `--trust` to skip that |

`execute_blender_code` runs Python in your open Blender session. Save the `.blend` before
using the full profile. Both profiles set `BLENDER_MCP_SAFE_MODE=1`, which makes the server
check scripts first and block file, process and network access (`--no-safe-mode` turns that
off; export and import need it off). The add-on's socket has no authentication, so keep it on
`localhost`.

Both profiles also set `BLENDER_MCP_DISABLE_TELEMETRY=1`: the server sends usage telemetry
unless told not to. Delete that line from the settings file if you want it on.

## What was and was not verified

On 2026-10-10, from the packages' own source and docs: the package name (`mcp-for-blender`,
formerly `blender-mcp`, which still runs), the `BLENDER_MCP_SAFE_MODE`,
`BLENDER_MCP_DISABLE_TELEMETRY`, `BLENDER_HOST` and `BLENDER_PORT` variables, and the
`mcpServers` keys of the Gemini CLI settings. By starting both servers over stdio and
listing their tools: `uvx mcp-for-blender` (server version 1.30.0) exposes
`get_addon_status`, `disable_telemetry`, `get_scene_info`, `execute_blender_code`,
`record_trajectory_feedback`, `look`, `generate_3d`, `search_assets` and `import_asset`, so
the names in `includeTools`/`excludeTools` are real; `npx gemini-mcp-tool` (reports 1.1.4)
exposes `ask-gemini` (`prompt` required; `model`, `sandbox`, `changeMode` optional),
`brainstorm`, `fetch-chunk`, `ping` and `Help`. `install.py` is covered by
`blender-gemini/tests/`, and its CLI was run against a temporary settings file.

**Not run end to end.** There was no Blender, Gemini CLI login or Claude Code client where this
was written, so no tool call has gone through the whole chain. Two things in particular are
unverified: whether `trust: true` lets a tool call
through when the Gemini CLI runs non-interactively (`gemini -p`, which is how `ask-gemini`
runs it), and whether a sandboxed `ask-gemini` call can reach Blender's local port. If the first
fails, Gemini reports the tool as unavailable and the skill passes that on; it does not retry
wider.

## Which CLI

Since 2026-06-18 Google has moved individual accounts (free, AI Pro, AI Ultra) from the Gemini
CLI to the Antigravity CLI (`agy`); the Gemini CLI remains for paid API keys and Code Assist
Standard and Enterprise. `gemini-mcp-tool` follows the same date and defaults to `agy`, so
`.mcp.json` pins `GEMINI_MCP_BACKEND=gemini`. If you are on `agy`, the settings file this tool
writes is not the one it reads, and the sources disagree about where `agy` keeps its MCP
config, so this tool does not write it. `agy plugin import gemini` is the migration command
the sources name; check it against Google's current docs.

## Windows

Claude Code may fail to start a bare `npx` server on native Windows. If `/mcp` shows `gemini`
failing, replace its entry (in `.mcp.json`, or per user with `claude mcp add`) with
`"command": "cmd", "args": ["/c", "npx", "-y", "gemini-mcp-tool"]`. `check` warns about this
on Windows. This is from memory of Claude Code's behaviour and was not tried here.

## Without Gemini in the middle

Claude can call the Blender server directly: `claude mcp add blender -- uvx mcp-for-blender`.
That drops a model hop, a second API bill and the unverified approval question. This tool
exists for when Gemini should be the one doing the Blender work.

## Tests

`python -m unittest discover -s blender-gemini/tests`
