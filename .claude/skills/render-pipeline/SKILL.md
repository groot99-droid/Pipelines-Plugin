---
name: render-pipeline
description: Move a Who Did It master (a character .blend kept under studio/assets/who-did-it/) through the game repo's Blender rig and sprite packer into the committed atlases under apps/client/public/assets/. Use when the author wants to render, re-render, pack or ship a who-did-it character or the calibration sheet, or asks how a master reaches the game. Runs the game repo's existing scripts only; not a studio pipeline and not for making a master.
---

# Render pipeline (Who Did It)

Paths starting `studio/` are relative to this repo's root (the ROSW checkout).
Paths starting `tools/`, `apps/` and `assets/` are relative to the **Who Did It checkout**
(`groot99-droid/Who-Did-It`), which must be cloned beside this one; call it `$WDI`.

This skill is a recipe. It adds no script and no dependency, and it is not a studio run: it
writes nothing into `studio/vault/`. Making or changing a master (a concept, a model, a rig
cleanup) is a studio pipeline run (`studio-pipeline` skill); this skill starts once a master
exists. Keys stay in `~/.rosw/keys.env`; none is needed here.

## Where things live

| Thing | Place | Versioned |
|---|---|---|
| Master `.blend`, `.glb`, `.psd` | `studio/assets/who-did-it/<kind>/<slug>/` here | No (`studio/assets/` is git-ignored) |
| Studio note for a master | `studio/vault/who-did-it/<kind>/<slug>.md`, written by the studio pipeline | Yes |
| Master path, hash, date | `$WDI/assets/source/MANIFEST.md` | Yes |
| Rig and render scripts | `$WDI/tools/blender/` | Yes |
| Packer | `$WDI/tools/sprites/` | Yes |
| Exports | `$WDI/apps/client/public/assets/` | Yes, in art-drop PRs |

Kinds: `character`, `design`, `audio`, `video`, `3d`, `ui`, `world`.

## Steps

1. **Check the master.** The character `.blend` follows the contract in `$WDI/tools/blender/README.md`
   (an `Export` collection, parts tagged `wdi_part`, a `Feet` empty, one action per clip). Palettize
   a copy first if materials are untextured PBR:

   ```
   blender -b <master>.blend -P $WDI/tools/blender/palettize.py -- --save
   ```

2. **Render the passes.** From `$WDI`:

   ```
   blender -b --factory-startup -P tools/blender/batch_render.py -- \
     --char <ROSW>/studio/assets/who-did-it/character/<slug>/<slug>.blend \
     --body <slug> --out build/render
   ```

   Options: `--anims`, `--dirs`, `--passes`, `--rig tools/blender/build/render_rig.blend`.
   The rig is built in memory from `tools/blender/build_rig.py` unless `--rig` is given; no
   `.blend` of the rig is ever committed. Output:
   `build/render/<body>/<pass>/char_<body>_<anim>_<dir>_<nnn>.png` plus `manifest.json`.
   The calibration sheet is `--smoke --out apps/client/public/assets/calibration`.

3. **Pack.** From `$WDI` (Node 22 or newer, dependencies already installed by `pnpm install`):

   ```
   node tools/sprites/pack.ts build/render/<body> apps/client/public/assets/chars
   ```

   The packer is deterministic: unchanged frames give byte-identical pages. Keys are
   `char/<body>/<anim>/<dir>`; the body id is never a role name.

4. **Verify** in `$WDI`: `pnpm --filter @wdi/sprites test` and `pnpm --filter @wdi/blender test`,
   then run the client with `?mock=1` and look at the sprites.

5. **Record the master.** Update the master's row in `$WDI/assets/source/MANIFEST.md`
   (`sha256sum <master>`, today's date, the export paths) and add or update the
   `CREDITS.md` row. A new generation needs its catalog id from `studio/library/catalog.json`
   (run `higgsfield-library-sync` first).

6. **Ship.** Commit `apps/client/public/assets/**` in an art-drop PR in `$WDI`
   (CI warns above 25 MB of binaries). Never commit `build/`, a `.blend`, or a Mixamo file.

## Refusals

- A master that is missing or has no studio note is made first through `studio-pipeline`.
- No new script, package or version bump in either repo from this skill.
- Mixamo-bearing `.blend` files stay out of both repos' git (`$WDI/CREDITS.md` policy).
