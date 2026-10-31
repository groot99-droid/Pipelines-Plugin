---
name: brush-library
description: Answers questions about the author's Procreate brush library (their brush packs and Procreate's own legacy sets) from the brush vault, by searching it with brushes/vault/tools/brush_search.py or the brushes MCP tools and citing brush ids, sets and note lines. Use when the author asks which brush to use, what a brush's settings are, which brushes are alike, or what the library holds. Not for editing or exporting a brush, which is the brush-designer skill, and not for tagging, which is brush-tag-backfill.
---

# Brush library

All paths are relative to the **Pipelines repo root**, your working
directory. The vault is `brushes/vault/`; **read `brushes/vault/CLAUDE.md`
first**, it is authoritative. A path that `brush_search.py` reports or
accepts is vault-relative (`02_Vendor_Packs/igb-vintage-ink-kit.md`). This
skill writes nothing in the vault.

## How to answer

1. **Check the index is current.**
   ```
   python -I brushes/vault/tools/brush_search.py index --check
   ```
   Exit 0 is fresh, 1 stale. If stale or missing (exit 2), run
   `python -I brushes/vault/tools/brush_search.py index`: it writes only an
   ignored, rebuildable cache. If it says there is no catalog or no notes,
   stop and give the author the regeneration order in the vault's
   `CLAUDE.md` rule 7; do not answer from memory.

2. **Turn the question into searches and run them yourself** (cheap lookups).
   ```
   python -I brushes/vault/tools/brush_search.py search "<words>" --top 8
   python -I brushes/vault/tools/brush_search.py search --tag medium=charcoal --tag edge=soft --top 8
   python -I brushes/vault/tools/brush_search.py search "inker" --where kind=stroke --where taper=both
   python -I brushes/vault/tools/brush_search.py search --where plotSpacing=..0.05 --where library=official
   python -I brushes/vault/tools/brush_search.py similar "<brush id | exact name>" --other-sets --top 8
   python -I brushes/vault/tools/brush_search.py facets [--axis medium]
   python -I brushes/vault/tools/brush_search.py brush <brush id> [--settings]
   ```
   Add `--json` for the full row. `ask` is a second spelling of `search`.
   - `--tag AXIS=V[,V2]` is repeatable and ANDed, a comma list is OR. The
     axes are `medium mark texture edge motif use`. Tag values are a closed
     list: `facets` prints every axis, tag and definition. An unknown axis,
     tag or key exits 2 with the valid list; it is not an empty result.
   - `--where KEY=V1,V2`, `KEY=MIN..MAX` (inclusive, either side may be
     empty) and `--where-not KEY=V`. A key is a facet name (`kind`,
     `size_class`, `taper`, `shape_source`, `grain_source`, `era`), a raw
     setting key (`plotSpacing`), or `id`, `set`, `library`, `pack`,
     `tagged`. No comparison operators.
   - **Tags exist only where the tagger has run.** Check the first line of
     `facets` (`tag state: tagged=N stale=N untagged=N`); when most brushes are
     untagged a `--tag` search returns only the tagged few. Fall back to
     words plus facet filters, and say so.
   - A query ranks by `cosine`, tags alone by `tag-purity`, filters alone
     by `filter-order`; `total` is how many matched, you see the top few.
   - For "something like X", find X's id by search, then `similar`.

3. **Do not Read set notes yourself.** A note can hold over a hundred
   brushes. For one brush's section use
   `brush_search.py chunks <note path> --ids <id> --brief`, then Read only
   its line range. If the answer needs settings, a comparison or anything the
   result does not show, pass up to ten results (each `brush_id`, `note`,
   `start_line`-`end_line`) and a focus to the `brush-librarian-native`
   subagent via the Agent tool.

4. **Check the digest** before you cite a value from it:
   ```
   python -I brushes/vault/tools/brush_search.py verify --from <digest file>
   ```
   (or the digest on standard input). It appends
   `[UNVERIFIED -- not found in source text, do not cite as exact]` to any
   line it cannot match to the brush's record; treat those as non-citable.

## The MCP tools

The server `brushes` (`python -I brushes/pipeline/mcp_server.py`, read-only)
returns the same shapes as the command line. Contract names: `library_status`,
`search_brushes`, `get_brush`, `similar_brushes`, `list_sets`,
`list_vocabulary`, `get_preview`, `get_brush_settings_schema`,
`validate_settings_patch`. **Today the server is a stub that lists only
`library_status`**; check what `tools/list` offers before relying on any other.
`library_status` reports the index state (`fresh`, `stale`, `memory`,
`not_ingested`) and the commands that would fix what is missing. Prefer the
MCP tool when it is listed, the command line otherwise; never mix their
results as if from two sources.

## Reading a result

A row has `brush_id`, `name`, `set`, `note`, `heading`, `start_line`,
`end_line`, `score`, the six `*_tags` lists, `visual`, `tag_state`
(`tagged`, `stale`, `untagged`), `facets`, `preview`, `also_in`, `record`.
Settings only with `--settings`. Results are de-duplicated by brush id;
`also_in` names the other sets that repeat it. Names are not unique, so
always carry the id.

## Answering

- Cite every brush as **id, name, set, note path and line range**, exactly as
  the tool returned them. Never invent a citation.
- An exact value comes from the record (`brush <id> --settings`, or the
  librarian's "Exact values" not marked UNVERIFIED). Notes round for reading;
  say "about" for a rounded one. Report `blendMode`, `dynamicsRenderType` and
  other enums as numbers: labels are inferred from key names.
- Say "described, not measured" for anything from `visual` or tags. Facet
  classes are heuristics: quote the number beside the class.
- A bundled shape or grain only has a file name and ships inside Procreate;
  never describe its look from the name. `no-thumbnail` means the stroke
  preview is a placeholder.
- `similar` compares **settings, not how a stroke looks** (`gower-v1`), and
  mostly finds siblings from one vendor template unless you pass
  `--other-sets`. Say so.
- **Never claim a brush or an exported file opens or works in Procreate.**
  Nothing this tool has written has been opened there (see the
  brush-designer skill). Say "has not been opened in Procreate".
- Claim nothing about licence beyond the pack's entry in
  `brushes/library/sources.json`; `redistribute` is recorded information.
- If nothing was retrieved, say the library has no match. Do not answer from
  general knowledge of Procreate or of what such a brush "usually" does.

## Opening a brush in the designer

To edit, export or open a brush in the designer, hand its id to the
`brush-designer` skill (the app opens a library brush from its id). This
skill never changes or exports a brush.
