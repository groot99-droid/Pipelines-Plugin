# blender-addons

Tool manifests for the author's own Blender add-ons, for the blender plugin's `blender-addons` MCP
server (`plugins/blender/addon-tools/server.py`). Each manifest turns some of an add-on's operators
into named, typed tools (`mcp__blender-addons__<name>`). Arguments are checked against the declared
types, and they reach Blender as a JSON literal, never as code.

## Use them

Point the server at this folder, then reconnect it (`/mcp` in Claude Code):

```bash
export BLENDER_ADDON_TOOLS_DIR="$PWD/blender-addons/manifests"
```

```bash
python plugins/blender/addon-tools/server.py check --dir blender-addons/manifests
```

Blender has to be open with the MCP for Blender add-on connected (the same socket `mcp__blender__*`
uses). A tool checks that its add-on is enabled before anything runs. It accepts the extension under any
repository name (`bl_ext.blender_org.<id>`, `bl_ext.user_default.<id>`).

## What they are, and what they are not

- They were drafted from each add-on's **published source** on extensions.blender.org, in the version
  below. The zips were read with `ast` and nothing in them was run (`build_manifests.py`).
- They have **not been run against the author's Blender** (2026-10-29). Before relying on a tool, call it
  once and look at the result. If the installed version differs, `server.py discover <module>` drafts
  that version's operators to compare.
- Most of these operators read their settings from the add-on's panel (export folders, presets, bake
  sizes). A tool passes only the parameters it lists; everything else is whatever the panel holds.
- Operators run with `EXEC_DEFAULT`. A tool whose add-on draws in the 3D viewport or the node editor runs
  in that area, which has to be open.
- The manifests only name operators. They copy no add-on code. The add-ons are GPL-3.0-or-later and stay
  where the author installed them.

| Add-on | Version read | Licence | Manifest | Tools |
|---|---|---|---|---|
| ACT: Game Asset Creation Toolset | 2025.2.1 | GPL-3.0-or-later | `act.json` | act_export, act_create_palette, act_delete_unused_materials, act_delete_duplicated_materials, act_align, act_clear_normals, act_calc_normals, act_obj_name_to_mesh_name, act_collection_name_to_obj_name, act_select_negative_scaled_objects, act_cleanup_empties, act_numbering, act_lod_to_objname, act_remove_lod_from_objname, act_uv_clear, act_uv_add, act_mark_seams_from_uv, act_material_to_viewport, act_random_viewport_color, act_clear_vc |
| Auto-Scale FPS | 1.3.2 | GPL-3.0-or-later | `fps.json` | fps_enable_auto_fps_scale, fps_disable_auto_fps_scale |
| Bake To Single Material | 1.0.2 | GPL-3.0-or-later | `bake.json` | bake_to_single_material |
| CAD2Cube — DXF Importer | 1.5.1 | GPL-3.0-or-later | `cad2cube.json` | cad2cube_import_dxf |
| Easy Arrangement | 0.2.2 | GPL-3.0-or-later | `arrange.json` | arrange_apply, arrange_reset |
| Easy Clouds | 2.2.0 | GPL-3.0-or-later | `clouds.json` | clouds_create_cloud, clouds_create_layer, clouds_create_sphere |
| Easy Pivot | 1.0.2 | GPL-3.0-or-later | `pivot.json` | pivot_bake_pivot, pivot_reset_pivot, pivot_to_active |
| Easy Tree | 1.0.1 | GPL-3.0-or-later | `tree.json` | tree_add, tree_hide_leaves, tree_show_leaves |
| EasyMesh Batch Exporter | 1.6.2 | GPL-3.0-or-later | `easymesh.json` | easymesh_batch_export, easymesh_load_export_preset, easymesh_clear_export_indicators |
| Formula to Nodes | 2.1.0 | GPL-3.0-or-later | `formula.json` | formula_generate, formula_generate_script, formula_check |
| Game Asset Optimizer | 1.0.2 | GPL-3.0-or-later | `optimizer.json` | optimizer_batch_optimize, optimizer_dual_uv_unwrap, optimizer_generate_lods, optimizer_auto_decimate, optimizer_smart_vertex_merge |
| Marching Cube | 0.5.0 | GPL-3.0-or-later | `marching.json` | marching_cube_add |
| NS Toolkit - Mesh Cleanup Pro | 1.0.1 | GPL-3.0-or-later | `cleanup.json` | cleanup_tris_to_quads_merge, cleanup_highlight_topology, cleanup_clear_highlight |
| OMI Physics Body glTF Extension | 1.6.5 | GPL-3.0-or-later | `omi.json` | omi_physics_auto_fit, omi_physics_bake_scale, omi_physics_validate_scene, omi_physics_reset_defaults |
| Photo Relief | 1.0.1 | GPL-3.0-or-later | `relief.json` | relief_create |
| PROTO Game Asset Tools | 2.5.0 | GPL-3.0-or-later | `proto.json` | proto_batch_export, proto_quick_export_mesh, proto_quick_export_mesh_and_animations, proto_quick_export_allactions, proto_quick_export_curaction, proto_apply_all_modifiers_keep_shape_keys, proto_apply_active_modifier_keep_shape_keys, proto_vertex_group_to_vertex_color, proto_fill_vertex_color, proto_timelinetoaction |
| STEP Importer | 1.2.1 | GPL-3.0-or-later | `step.json` | step_import, step_cleanup_selected |
| Super Duper Batch Exporter | 2.9.3 | GPL-3.0-or-later | `sdbe.json` | sdbe_export, sdbe_list_add, sdbe_list_add_collection, sdbe_clear_list |
| Terrain Mixer | 3.1.3 | GPL-3.0-or-later | `terrain.json` | terrain_replace_with_terrain, terrain_add_tm_world, terrain_fix_clipping_distance, terrain_bake, terrain_setup_asset_library |
| Texture Pipeline Studio | 8.10.1 | GPL-3.0-or-later | `tps.json` | tps_assign_textures, tps_convert_to_udim, tps_lod_swap |
| Topology Doctor | 1.0.0 | GPL-3.0-or-later | `topo.json` | topo_analyze |
| Unreal Groom Importer | 1.0.1 | GPL-3.0-or-later | `groom.json` | groom_import |
| Unreal PSK/PSA | 9.1.3 | GPL-3.0-or-later | `unreal.json` | unreal_psk_import, unreal_psa_import_all, unreal_psk_export, unreal_psa_export |

`sources.json` records, per add-on, the zip's sha256, its page, and every operator id its source
registers. The tests check each manifest against it.

### Left out, and why

| Add-on or operator | Why |
|---|---|
| Script Launcher, Script Manager Pro | Each runs any `.py` file from disk, which would make a tool a way to run arbitrary code |
| Keyframe Selected, Time Tracker, Unreal Viewport Navigation - WASD | Interactive or display-only: hotkeys, a timer, viewport fly navigation |
| Node Align | Its operators have no `execute` of their own (they work through the editor's interaction) |
| Easy Pivot's Edit Pivot, and other modal operators | They wait for mouse input, so they cannot run with `EXEC_DEFAULT` |
| PROTO's `import_scene.fbx` and `export_scene.fbx` | They replace Blender's own FBX operators; the `proto_quick_export_*` tools cover export |
| The list editing operators (add, remove, move an export item) | Panel bookkeeping, done more safely in the add-on's panel |
| Higgsfield | Not on extensions.blender.org, so there was no source to read. Run `server.py discover <module>` on the author's machine |
| MCP (Blender Model Context Protocol) | It is the bridge itself; the `mcp__blender__*` tools already cover it |

Free-text parameters that reach an add-on's own parser: Marching Cube's equations (`eq`, `a_eq` … `h_eq`)
are checked by the add-on against an allow-list of names and operators before numexpr evaluates them.
CAD2Cube's `layer_filter` and the PSA name filters are matched as text.

## Rebuild

```bash
python blender-addons/build_manifests.py <folder of zips>
```

The script needs Python 3.11 or later. It takes the zips from extensions.blender.org (their sha256 is in
`sources.json`) and rewrites `manifests/` and `sources.json`. `CURATED` lists which operators become tools;
`NAMES` and `OVERRIDES` set a tool's name and any parameters that the source alone does not settle. Review
the diff before you commit it.

## Tests

```bash
python -m unittest discover -s blender-addons/tests
```

Every manifest must load in the server and match its source record. Each tool's code must compile. No
key-shaped value or outside link may appear. No Blender is needed.
