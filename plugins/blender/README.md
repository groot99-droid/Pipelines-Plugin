# blender

Claude Code plugin for working with a live Blender.

| Piece | What it is |
|---|---|
| `.mcp.json` | Launches the [MCP for Blender](https://github.com/ahujasid/blender-mcp) server (`uvx mcp-for-blender`) with telemetry disabled, and `blender-addons` (`addon-tools/server.py`) |
| `blender-mcp` | Connect, inspect, script with bpy, verify with screenshots, export |
| `blender-assets` | Choose and import models, textures, HDRIs and generated assets; scale and credit them |
| `blender-polyhaven-library` | The Poly Haven Assets add-on: setup, catalogs, resolution/LOD, troubleshooting |
| `blender-addon-tools` | Named, typed tools for your own Blender add-ons (the `blender-addons` server in `addon-tools/`) |
| `blender-scene-reviewer` | Read-only agent that reviews the open scene |

## Install

```
/plugin marketplace add groot99-droid/Pipelines-Plugin
/plugin install blender@rosw
```

## Setup

1. Install `uv` (official installer).
2. `uvx mcp-for-blender install-addon`, enable **Interface: MCP for Blender** in Blender, then
   **N panel > MCP for Blender > Connect to MCP server**.
3. Install this plugin; its `.mcp.json` registers both servers. API keys for Sketchfab,
   Poly Pizza, Hyper3D, Hunyuan3D, Meshy and Tripo go in the add-on panel or Preferences, never
   in files here.
4. Optional: tools for your own add-ons. Run `python addon-tools/server.py discover --list` with
   Blender connected, then see the `blender-addon-tools` skill.

The server runs arbitrary Python in Blender. Consider `BLENDER_MCP_SAFE_MODE=1` for untrusted
prompts. The Poly Haven add-on is GPL-3.0 and is not bundled; see NOTICE.
