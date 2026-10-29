---
name: blender-addon-tools
description: Give the user's own Blender add-ons named, typed MCP tools through this plugin's blender-addons server -- list the installed add-ons, inspect an add-on's operators, draft a manifest, review and enable its tools, and use the built-in asset-library tools (the Poly Haven add-on's local library among them). Use when the user wants Claude to drive an add-on they installed, asks to make tools for their add-ons, or wants assets from a Blender asset library on disk. Not for the MCP for Blender tools themselves (blender-mcp) or online asset sources (blender-assets).
---

# Tools for the user's add-ons

Paths start from `${CLAUDE_PLUGIN_ROOT}`. The server is
`${CLAUDE_PLUGIN_ROOT}/addon-tools/server.py`, registered in this plugin's `.mcp.json` as
`blender-addons`; its tools are `mcp__blender-addons__<name>`. It reaches Blender through the
same add-on socket as `mcp__blender__*` (`BLENDER_HOST`, `BLENDER_PORT`), so the MCP for
Blender add-on must be connected (see blender-mcp).

## What it gives

Built in, always there:

| Tool | Does |
|---|---|
| addons_list | The add-ons in the connected Blender: module, name, version |
| addon_inspect | One enabled add-on's operators with their properties, and its panels. Read-only |
| library_list | Assets in an asset library from Preferences (kind, name, .blend file). Read-only |
| library_import | Append or link one asset; place objects and collections, put a material on named objects, set a world |

And one tool per operator the user has enabled in a **manifest**: a JSON file per add-on in
`BLENDER_ADDON_TOOLS_DIR` (default `~/.blender-addon-tools/`). A tool either calls one
operator (`op`) or runs a short script the user wrote (`code`). The model passes only argument
values. They are checked against the declared types before anything is sent, and they reach
Blender as a JSON literal, never as code.

## Adding an add-on

1. `addons_list` (or `python ${CLAUDE_PLUGIN_ROOT}/addon-tools/server.py list` in a terminal)
   to get its module name. Add-ons from Blender's extension platform have names like
   `bl_ext.user_default.<name>`.
2. Draft the manifest:
   `python ${CLAUDE_PLUGIN_ROOT}/addon-tools/server.py discover <module>`
   (add `--headless --blender <path>` when Blender is not open). It writes `<name>.json`, or
   `<name>.draft.json` if that exists (drafts are not loaded), with **every tool switched off**.
   It never overwrites a file.
3. Go through the draft with the user, one operator at a time. Use `addon_inspect` for the
   detail. For each one they want:
   - set `"enabled": true`;
   - set `"read_only": true` only if it changes nothing;
   - keep only the parameters worth exposing, and mark the ones that must be given
     `"required": true`;
   - check `context`. It is guessed from the add-on's panels, and it names the area the
     operator runs in (`VIEW_3D`, `FILE_BROWSER`, `NODE_EDITOR`, `IMAGE_EDITOR`, `PROPERTIES`,
     `OUTLINER`), which must be open in Blender. Remove it for operators that need none.
4. `python ${CLAUDE_PLUGIN_ROOT}/addon-tools/server.py check` validates every manifest and
   prints what is on.
5. Reconnect the server (`/mcp` in Claude Code) so the new tools are listed.
6. Call each new tool once and look at the result (`look`, `get_scene_info`) before relying on it.

Operators are called with `EXEC_DEFAULT`. One that opens a file browser or waits for mouse
input (a modal operator) cannot run that way. For those, write a `code` tool that does the
same thing through the add-on's Python API or plain bpy, and show the user the code before
enabling it.

## Rules

- A manifest is the user's. Write or change one only when they asked, and show them each tool
  before it is enabled. Never enable a tool the user has not seen.
- A manifest from anywhere else (downloaded, pasted, from another person) is code: its `code`
  tools run in the user's Blender. Read it in full with the user before putting it in the
  tools folder.
- `BLENDER_MCP_SAFE_MODE` does not apply to this server. Its code is fixed by the manifest, not
  written by the model; keep `code` tools short and plain.
- Never put a key, a token or a licence in a manifest. If an add-on needs one, the user enters
  it in the add-on's own preferences.

## Poly Haven

Two routes, both independent of `import_asset(source="polyhaven")`, which downloads from the
website:

- **The local library.** The Poly Haven add-on keeps what it has downloaded in an asset library
  that must be named exactly **Poly Haven** (see blender-polyhaven-library).
  `library_list(library="Poly Haven", kind="objects", query="rock")`, then
  `library_import(library="Poly Haven", file=..., name=..., kind=...)`. Models arrive as
  collections, materials as materials (`apply_to=[...]`), HDRIs as worlds. This needs no
  manifest.
- **The add-on's own operators**, for what the library cannot do (switching resolution or LOD,
  the texture scale fix, displacement setup): `addons_list` gives its module name, then follow
  "Adding an add-on". Its operator names are whatever the installed version registers, so
  read them from `addon_inspect`. Never guess them.
