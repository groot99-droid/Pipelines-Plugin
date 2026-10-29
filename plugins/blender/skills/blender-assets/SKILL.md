---
name: blender-assets
description: Choose and bring in 3D assets for a Blender scene through the MCP for Blender integrations -- Poly Haven models, textures and HDRIs, Sketchfab, Poly Pizza low-poly models, and AI generation with Hyper3D Rodin or Hunyuan3D -- then scale, place and credit them. Use when a Blender task needs a model, material, environment lighting or generated asset rather than a primitive. Needs a live Blender connection (see blender-mcp).
---

# Sourcing assets for Blender

Paths start from `${CLAUDE_PLUGIN_ROOT}`; tool names and parameters are listed in
`${CLAUDE_PLUGIN_ROOT}/skills/blender-mcp/references/tools.md`.

## 1. Check what is enabled

Each source is a checkbox in the add-on panel. Call the status tool first and skip any source
that is off: `get_polyhaven_status`, `get_sketchfab_status`, `get_polypizza_status`,
`get_hyper3d_status`, `get_hunyuan3d_status`. Never ask for, print or store an API key; if one
is missing, tell the user to paste it into the add-on panel or Preferences.

## 2. Pick the source

| Need | Try first | Then |
|---|---|---|
| Specific real-world object | Sketchfab | Poly Haven |
| Generic props, furniture, rocks, plants | Poly Haven models | Sketchfab |
| Stylised or low-poly game props, many cheap props | Poly Pizza | Sketchfab |
| Environment lighting | Poly Haven HDRI | |
| Surface materials | Poly Haven textures | |
| Unique item no library has | Hyper3D Rodin or Hunyuan3D | |

Fall back to bpy primitives only when every source is off, nothing suitable exists, a
generator failed, or the user asked for a basic shape or colour.

## 3. Bring it in

- **Poly Haven**: `search_polyhaven_assets` (narrow with `get_polyhaven_categories`), then
  `download_polyhaven_asset(asset_id, asset_type, resolution='1k')`. Start at 1k; go higher
  only for hero close-ups. Textures are applied with `set_texture`.
- **Sketchfab**: `search_sketchfab_models` (downloadable only), look at
  `get_sketchfab_model_preview`, then `download_sketchfab_model(uid, target_size)`. Check the
  model's licence in the search result and tell the user if it needs credit.
- **Poly Pizza**: `search_polypizza_models(query, category?, licence?)`, then
  `download_polypizza_model(model_id, normalize_size=True, target_size=<real height in m>)`;
  source scale and origin are arbitrary.
- **Hyper3D / Hunyuan3D**: one item per job, never a whole scene, ground, or parts to be
  assembled. Generate, poll until done, then import. After import, fix location, scale and
  rotation. Duplicate an imported result with bpy instead of generating twice.
  Free-trial Rodin keys run out daily; tell the user they can wait or use their own key.

## 4. After every import

`get_object_info` for the world bounding box; confirm real-world scale, that the object sits
on its surface and does not clip neighbours, then `get_viewport_screenshot`.

## Licences and credit

Poly Haven is CC0. Poly Pizza is CC0 or CC-BY, and about 69% is CC-BY, which **requires
credit**: `download_polypizza_model` returns a formatted line and stores it on the object as
`polypizza_attribution`. Give that line to the user whenever a CC-BY model is used, or filter
with `licence="CC0"`. Sketchfab licences vary per model.
