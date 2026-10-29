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

## API keys

One key, `GEMINI_API_KEY`, serves both halves: the `gemini` MCP plugin Claude calls and the
Blender chain run the same Gemini CLI. **Never paste a key into a Claude chat, a prompt, a
commit or an issue**; Claude does not need to see it and the skill is told never to read it.
Do this on your own machine, not in a cloud session:

1. `python docs/setup_keys.py` opens a page on 127.0.0.1 that saves keys to
   `~/.rosw/keys.env`, outside the repo. Enter the new `GEMINI_API_KEY` there. Creative-writing's
   Gemini backend reads this file too.
2. The Gemini CLI does not read `keys.env`, so copy the key where it looks:
   ```powershell
   python blender-gemini/install.py sync-key --dry-run    # says added / updated / unchanged
   python blender-gemini/install.py sync-key              # writes ~/.gemini/.env
   ```
   It prints names and paths, never the key. The file is mode 600 on Linux and macOS, only the
   `GEMINI_API_KEY` line is touched, and no `.rosw-bak` is made (a backup would keep the old key).
   It refuses a value with anything but letters, digits, `_`, `.` and `-`, so a dotenv parser
   cannot read it differently. This does make a second copy of the key on disk;
   `sync-key --remove` takes it out again.
3. `python blender-gemini/install.py check` has a `gemini key` line: where the Gemini CLI can see
   the key (this shell's environment, or `~/.gemini/.env`), or the command that fixes it.

To replace a key, repeat 1 and 2 (`sync-key` reports `updated`), then revoke the old one in
Google AI Studio; nothing here can do that. Exporting `GEMINI_API_KEY` in the shell that starts
Claude Code also works, and `check` counts it.

**The Blender add-on's own keys are separate.** The default profile needs none. The full
profile's `search_assets`, `import_asset` and `generate_3d` can use Sketchfab, Poly Pizza,
Hyper3D and Hunyuan3D, and the add-on (v2.1.9 source) reads `BLENDERMCP_SKETCHFAB_API_KEY`,
`BLENDERMCP_POLYPIZZA_API_KEY`, `BLENDERMCP_HYPER3D_API_KEY`, `BLENDERMCP_HUNYUAN3D_SECRET_ID`,
`BLENDERMCP_HUNYUAN3D_SECRET_KEY` and `BLENDERMCP_PREMIUM_LICENSE_KEY`. It reads them inside
Blender, from its own preferences or panel, or from the environment Blender was started from. They
do not belong in `mcpServers.blender.env` in the Gemini settings, which only reaches the
separate server process. This tool does not store, sync or check them.

Not verified: which `.env` locations the Gemini CLI reads and in what order (sources disagree),
which wins when both the environment and `~/.gemini/.env` set a key, whether you must pick API-key
sign-in once with `/auth` in an interactive `gemini`, and whether a free AI Studio key still
works with the Gemini CLI after the 2026-06-18 account change.

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
