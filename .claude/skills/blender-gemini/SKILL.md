---
name: blender-gemini
description: Drive the author's open Blender through the Gemini CLI by calling the gemini MCP server (ask-gemini), which has the Blender MCP server registered. Use when the author asks to look at, inspect or change their Blender scene through Gemini, or to hand Gemini a Blender task. Needs Claude Code running on the author's own machine with Blender open; it cannot work in a cloud session. Not for the Writing Museum, which is a Three.js scene and does not use Blender.
---

# Blender through Gemini

All paths are relative to the repo root, your working directory. The tool is
`blender-gemini/`; read its `README.md` first.

The chain: you call `mcp__gemini__ask-gemini` (the `gemini` server in `.mcp.json`),
which runs the Gemini CLI, which calls the `blender` MCP server registered in the
author's `~/.gemini/settings.json`, which talks to the add-on inside the author's open
Blender. Nothing in that chain exists in a cloud container.

## 1. Preflight

Run `python blender-gemini/install.py check`. It only reads. If it prints `not ready`,
tell the author which lines failed and stop; each line names its fix. Do not run
`install` or `uninstall` yourself unless the author asks: they write to
`~/.gemini/settings.json`, outside the repo.

If `mcp__gemini__ask-gemini` is not among your tools, the author has not approved the
`gemini` server from `.mcp.json` yet (`/mcp` lists it), or Claude Code was started
before the file existed. Say so and stop.

## 2. Ask

Call `mcp__gemini__ask-gemini` with a `prompt` that names the job and the Blender tool
to use. Leave `sandbox` unset (a sandboxed Gemini run may not reach Blender's local
port; not verified), leave `changeMode` unset (it formats replies as code edits), and
leave `model` to the author unless they name one. A long reply comes back in chunks;
the `fetch-chunk` tool returns the rest.

- **Read-only profile (the default install).** Gemini can use `get_scene_info`, `look`
  and `get_addon_status` and nothing else. Ask it to describe the scene, list objects,
  materials or modifiers, or to look at the viewport.
- **Full profile.** Gemini also has `execute_blender_code`, `search_assets`,
  `import_asset` and `generate_3d`. Before asking for any change, tell the author to
  save the `.blend`, and say what you are about to ask for. Ask for one change at a
  time.
- If the author asks for an edit and `check` shows the read-only profile, say the
  profile forbids it and that they can run
  `python blender-gemini/install.py install --profile full` themselves. Do not
  work around it.

## 3. Report faithfully

What comes back is Gemini's account, not a record of what Blender did. After a claimed
change, confirm it with a second read-only ask (`get_scene_info`) and report that. If
Gemini says a tool was unavailable, blocked, or needed approval it could not get, pass
that on as it is: a non-interactive Gemini run may have no way to answer an approval
prompt (how the Gemini CLI treats unapproved MCP tools in `-p` mode is not verified).
Do not retry with a wider profile or a different server to get around it.

Put no secrets, keys or private paths in the `prompt`; it goes to Google. Nothing here
writes to a vault or the repo.
