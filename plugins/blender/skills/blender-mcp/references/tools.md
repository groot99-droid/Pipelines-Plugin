# MCP for Blender tools

Every tool also takes an optional `user_prompt` string (the user's request, for context);
ignore it unless a tool requires it (`get_scene_info` does).

| Tool | Parameters | Use |
|---|---|---|
| get_addon_status | | Blender version; addon/server version match |
| get_scene_info | user_prompt | Objects, materials, scene summary |
| get_object_info | object_name | Transform, materials, world bounding box |
| get_viewport_screenshot | max_size=1000 | See the viewport |
| execute_blender_code | code | Run bpy in small steps |
| describe_node_type | bl_idname, property_overrides | Node property/socket schema without touching the scene |
| bpy_api_lookup | query | RNA types, properties, functions, operators |
| get_polyhaven_status | | Is the Poly Haven checkbox on in the addon |
| get_polyhaven_categories | asset_type='hdris' | hdris / textures / models categories |
| search_polyhaven_assets | asset_type='all', categories | Find assets |
| download_polyhaven_asset | asset_id, asset_type, resolution='1k', file_format | Download and import |
| set_texture | object_name, texture_id | Apply a downloaded Poly Haven texture |
| get_sketchfab_status | | Needs API key in the addon |
| search_sketchfab_models | query, categories, count=20, downloadable=True | Realistic models |
| get_sketchfab_model_preview | uid | Thumbnail |
| download_sketchfab_model | uid, target_size | Import scaled to target_size |
| get_polypizza_status | | Needs API key |
| search_polypizza_models | query, category, licence ('CC0'/'CC-BY'), animated, limit=20 | Low-poly models |
| download_polypizza_model | model_id, normalize_size, target_size=1.0 | Import; returns attribution |
| get_hyper3d_status | | Rodin enabled? key type? |
| generate_hyper3d_model_via_text | text_prompt, bbox_condition | Start a Rodin job |
| generate_hyper3d_model_via_images | input_image_paths / input_image_urls, bbox_condition | Start from images |
| poll_rodin_job_status | subscription_key or request_id | Wait for completion |
| import_generated_asset | name, task_uuid or request_id | Import the Rodin result |
| get_hunyuan3d_status | | Mode: OFFICIAL_API or LOCAL_API |
| generate_hunyuan3d_model | text_prompt or input_image_url | Start a job |
| poll_hunyuan_job_status | job_id | Wait |
| import_generated_asset_hunyuan | name, zip_file_url | Import (prefer .glb) |
| export_scene | filepath, format, object_names, selection_only, apply_modifiers | GLB/FBX out |
| disable_telemetry | | Turn collection off |
| record_trajectory_feedback | feedback, correction_text, step_index | Telemetry feedback; skip when disabled |

Environment: `BLENDER_HOST`, `BLENDER_PORT`, `BLENDER_MCP_SAFE_MODE=1`, `DISABLE_TELEMETRY=true`.
Credential variables (set in the shell or add-on preferences; never print values):
`BLENDERMCP_SKETCHFAB_API_KEY`, `BLENDERMCP_POLYPIZZA_API_KEY`, `BLENDERMCP_HYPER3D_API_KEY`,
`BLENDERMCP_HUNYUAN3D_SECRET_ID`, `BLENDERMCP_HUNYUAN3D_SECRET_KEY`, `BLENDERMCP_HUNYUAN3D_API_URL`.
