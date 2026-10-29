---
name: blender-polyhaven-library
description: Guide for using the Poly Haven Assets add-on in Blender, which mirrors polyhaven.com HDRIs, materials and models into the Asset Browser as a local asset library -- first-time setup, catalogs, downloading, resolution and LOD switching, displacement and texture scale, and scripting against its asset library. Use when the user works with the Poly Haven Asset Browser library or asks how to set it up or fix it. Not for the MCP download tools (blender-assets).
---

# Poly Haven Assets add-on

Written from the add-on's documented behaviour (v1.2.3, Blender 4.5+). The add-on is GPL-3.0
and is **not** bundled with this plugin; the user installs it from Blender Market or the
Poly Haven docs (https://docs.polyhaven.com/en/guides/blender-addon). Do not copy its code
into other projects.

## Setup

1. Install and enable the add-on.
2. **Edit > Preferences > File Paths > Asset Libraries** (Blender 5.2+: the **Assets**
   section): add a library named exactly **Poly Haven** pointing at an empty folder with room
   for the downloads. The add-on refuses to run without that name.
3. In the Asset Browser pick the Poly Haven library; the add-on pulls the asset list from
   `api.polyhaven.com/assets` (cached in that folder for about a week) and downloads
   thumbnails and 1k versions. **Revalidate All Assets** in the add-on preferences re-checks
   file hashes.

## How assets are organised

- Three types: HDRIs, Textures (materials), Models. Each has catalogs by Poly Haven category;
  because an asset can sit in one catalog only, its other categories and tags become asset
  tags, so search by tag in the Asset Browser.
- Per-asset folder: `<library>/<slug>/` with `info.json`, a thumbnail and the `.blend`
  (HDRIs: the `.hdr` plus a generated `.blend`). Images are stored with relative paths so the
  library folder can be moved or shared.
- Default download resolution is 1k. Higher resolutions and model LODs are switched per asset
  from the sidebar panel (resolution and LOD menus) instead of redownloading by hand.

## Using assets

- Drag a model or material from the Asset Browser into the scene. Models come as a
  collection; some carry a scatter/geometry-nodes group that is also marked as an asset.
- Texture panel: real-world scale is stored on the material, and a scale-fix operator
  re-applies it after you resize an object. A displacement setup operator wires the
  displacement map (needs Cycles adaptive subdivision or a subdivided mesh).
- HDRIs become world assets built from a node-group template.

## Troubleshooting

| Symptom | Check |
|---|---|
| "create an asset library named Poly Haven" | The library name must match exactly |
| SSL errors | Add-on preferences > Disable SSL Verification (only behind a broken proxy) |
| Assets missing or stale | Revalidate All Assets; delete `asset_list_cache.json` in the library folder |
| Pink textures | Library folder moved without its sub-folders; revalidate |

## With the MCP tools

The MCP `download_polyhaven_asset` tool is independent of this library: it fetches directly
into the open scene. Use the Asset Browser library for browsing and repeated reuse, and the
MCP tool when Claude should place an asset for you (see blender-assets).
