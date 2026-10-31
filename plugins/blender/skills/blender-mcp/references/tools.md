# MCP for Blender tools

Checked against `server.py` of `mcp-for-blender` 2.2.6. Claude sees these as `mcp__blender__<name>`.
Every tool also takes `user_prompt`: the user's own words, verbatim. Pass it when telemetry is on;
this plugin turns telemetry off, so it can be left empty.

| Tool | Parameters | Use |
|---|---|---|
| get_addon_status | | Blender version, addon/server match, which `libraries` (polyhaven, sketchfab, polypizza) and `generators` (tripo, hunyuan3d, hyper3d, meshy) are on, telemetry consent |
| get_scene_info | query, root, fields, limit=20 | Scene facts as text, one line per object. `fields`: location, size, ground, rotation, scale, parent, children, hidden, details, materials, modifiers, animation, topology, weights, settings |
| look | mode, target, views, distance, shading, frames, frame_count=6, view, image, max_size=768 | One image. `mode`: viewport, camera, angles, frames. `shading`: solid, material, rendered, wireframe, xray. `image`: "Render Result" or a file path |
| execute_blender_code | code | Run bpy (bmesh, mathutils) in small steps; returns what it prints |
| search_assets | source, query, asset_type='all', category, attributes, min_size_m, licence, animated, limit=20, previews=0 | `source`: polyhaven, sketchfab or polypizza. Results carry each asset's id |
| import_asset | source, id, asset_type, target_size, apply_to, resolution='1k', file_format | Bring a searched asset in. polyhaven needs `asset_type` (hdris, textures, models); sketchfab needs `target_size` (m, largest side) |
| generate_3d | prompt or image, name, provider='auto', quality, bbox_condition, pose_mode, job, wait_seconds=50 | One generated object, imported. `provider`: auto, tripo, hunyuan3d, hyper3d, meshy. Returns a `job` handle if not done; call again with `job` to keep waiting |
| disable_telemetry | | Turn collection off (it can only turn it off) |
| record_trajectory_feedback | feedback (accept, reject, undo, correction), correction_text, step_index | Telemetry feedback; skip it while telemetry is off |

The server also registers app-only tools (`open_viewport`, `viewport_latest`, `viewport_capture`,
`viewport_pick`, `search_mentions`). The host UI calls them; the model never sees them.

There is no export, object-info, node-schema or API-lookup tool in 2.2.6: do those in
`execute_blender_code` (see the blender-mcp skill).

Environment: `BLENDER_HOST`, `BLENDER_PORT`, `BLENDER_MCP_SAFE_MODE=1`, `DISABLE_TELEMETRY=true`.
Credential variables (set in the shell or the add-on preferences; never print values):
`BLENDERMCP_SKETCHFAB_API_KEY`, `BLENDERMCP_POLYPIZZA_API_KEY`, `BLENDERMCP_HYPER3D_API_KEY`,
`BLENDERMCP_HUNYUAN3D_SECRET_ID`, `BLENDERMCP_HUNYUAN3D_SECRET_KEY`, `BLENDERMCP_HUNYUAN3D_API_URL`,
`BLENDERMCP_MESHY_API_KEY`, `BLENDERMCP_TRIPO_API_KEY`.

Tools for the user's own add-ons come from the second server this plugin registers,
`blender-addons` (see the blender-addon-tools skill).
