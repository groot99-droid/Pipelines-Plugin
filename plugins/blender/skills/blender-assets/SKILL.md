---
name: blender-assets
description: Choose and bring in 3D assets for a Blender scene through the MCP for Blender integrations -- Poly Haven models, textures and HDRIs, Sketchfab, Poly Pizza low-poly models, and AI generation with Tripo, Hunyuan3D, Hyper3D Rodin or Meshy -- then scale, place and credit them. Use when a Blender task needs a model, material, environment lighting or generated asset rather than a primitive. Needs a live Blender connection (see blender-mcp).
---

# Sourcing assets for Blender

Paths start from `${CLAUDE_PLUGIN_ROOT}`; tool names and parameters are listed in
`${CLAUDE_PLUGIN_ROOT}/skills/blender-mcp/references/tools.md`.

## 1. Check what is enabled

Each source is a checkbox in the add-on's sidebar tab. `get_addon_status` reports them:
`libraries` (polyhaven, sketchfab, polypizza) and `generators` (tripo, hunyuan3d, hyper3d,
meshy), each on or off. Skip any that is off. Never ask for, print or store an API key; if one
is missing, tell the user to paste it into the add-on panel or Preferences.

## 2. Pick the source

| Need | Try first | Then |
|---|---|---|
| Specific real-world object | sketchfab | polyhaven |
| Generic props, furniture, rocks, plants | polyhaven models | sketchfab |
| Stylised or low-poly game props, many cheap props | polypizza | sketchfab |
| Environment lighting | polyhaven hdris | |
| Surface materials | polyhaven textures | |
| Unique item no library has | `generate_3d` | |

Fall back to bpy primitives only when every source is off, nothing suitable exists, a
generator failed, or the user asked for a basic shape or colour.

## 3. Bring it in

- **Search**: `search_assets(source, query, ...)`. For Poly Haven narrow with `asset_type`,
  `category` or `min_size_m` (2+ for walls and ground); `previews=3` attaches thumbnails and is
  cheaper than importing the wrong asset. Sketchfab results carry a licence per model; tell the
  user if it needs credit.
- **Import**: `import_asset(source, id, ...)`.
  - polyhaven: `asset_type` is required (hdris become the world, textures a material, models
    objects). Start at `resolution="1k"`; go higher only for hero close-ups. For a texture pass
    `apply_to=[object names]`, or the material is unused and lost on save.
  - sketchfab: `target_size` (metres, largest side) is required.
  - polypizza: pass `target_size`; source scale and origin are arbitrary.
- **Generate**: `generate_3d(prompt=... or image=..., name=..., provider="auto")`. One object
  per call, never a whole scene, ground, or parts to be assembled. It waits up to about 45 s
  and otherwise returns a `job`; call `generate_3d(job=..., name=...)` to keep waiting.
  Repeating an unfinished request resumes it instead of paying again. Each call can cost the
  user money, so duplicate a result with bpy rather than generating twice.

## 4. After every import

`get_scene_info(query=<name>, fields=["size", "ground"])`: confirm real-world scale, that the
object sits on its surface and does not clip neighbours; then `look`.

## Licences and credit

Poly Haven is CC0. Poly Pizza is CC0 or CC-BY, and most of it is CC-BY, which **requires
credit**: the import result gives the attribution line. Give that line to the user whenever a
CC-BY model is used, or search with `licence="CC0"`. Sketchfab licences vary per model.
