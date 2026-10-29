# Changelog

## 0.2.0

- Tool names and parameters checked against mcp-for-blender 2.2.6: `look`, `get_scene_info`
  fields, `search_assets` / `import_asset` and `generate_3d` replace the per-source and
  screenshot tools of older releases. `tests/test_tool_names.py` keeps the documents in step.
- `blender-addons` server (`addon-tools/server.py`): named, typed tools for the user's own
  add-ons from a manifest per add-on, `discover` to draft one, and built-in asset-library tools
  (`library_list`, `library_import`) that read the Poly Haven add-on's local library.
- Skill: blender-addon-tools.

## 0.1.0

- Skills: blender-mcp, blender-assets, blender-polyhaven-library.
- Agent: blender-scene-reviewer (read-only).
- .mcp.json launching `uvx mcp-for-blender` with telemetry disabled.
