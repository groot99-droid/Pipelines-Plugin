# CLAUDE.md — Brush Vault

## Purpose & scope

This file governs how Claude works **inside** the brush vault: finding Procreate brushes by what they do, citing them correctly, adding tags, and helping the author write under a note's `## Notes` heading. The vault is a library of **facts about brush files**, and the facts come from one place, `brushes/catalog/`, which `ingest.py` builds from the originals in `brushes/library/`. It is not a place to design brushes: the designer app and the export commands do that, and they write files elsewhere.

It does **not** license editing a generated note, a preview, a tag sidecar or the catalog by hand. All of those have a writer (table below), and a hand edit is refused or overwritten.

## Where this vault sits, and how to read the paths

This vault lives at `brushes/vault/` inside the `Pipelines` repo, as the data half of the brushes tool. The code that writes into it is `brushes/pipeline/`; the facts it is written from are `brushes/catalog/`; the original brush files are `brushes/library/`.

**Every path in this file is vault-relative** unless it starts with `brushes/`: `02_Vendor_Packs/igb-vintage-ink-kit.md`, `tools/brush_search.py`, `_BrushTags/vocabulary.yaml`. That is the form the search tool reports and accepts. From the repo root, prefix `brushes/vault/`. Commands below are written for the repo root and use `python`, never `python3`.

## Vault navigation

- [[00_INDEX.md]] — counts, a list of every note by folder, and a table of how many brushes carry each facet word. Generated.
- `<folder>/_index.md` — one per numbered folder, one bullet per note. Generated.
- `<folder>/<set_slug>.md` — **one note per brushset** that is the home of at least one brush. The note holds one section per brush.
- `_Previews/` — grey PNG previews of strokes, shapes and grains. Generated; notes link to them.
- `_BrushTags/` — the tag vocabulary (`vocabulary.yaml`, authored) and one `.tags.json` sidecar per note (written by the tagger's script).
- `tools/` — `brush_search.py`, `brush_tags.py`, and the ignored search index.

| Folder | Holds | Rule (the first row that fits decides) |
|---|---|---|
| `01_Procreate_Defaults` | Procreate's own downloadable sets (Procreate 1, 2, 3, 5 and the extras) | the set's `library` is `official` |
| `04_My_Brushes` | the author's own brushes and designer exports | its pack's `pack_kind` is `mine` |
| `03_Loose` | a vendor pack's loose `.brush` files that are not repeated in a real set | the set's `kind` is `loose` |
| `02_Vendor_Packs` | everything else: a real set of a vendor pack | anything else |

`ingest.py build` writes each set's note path into the catalog; `notes.py` reads it from there. A loose file that repeats a brush of a real set is filed under that set: a set whose every brush is homed elsewhere has **no note at all** (`00_INDEX.md` names it).

## What is generated, and by what

| Content | Written by |
|---|---|
| a note above its `## Notes` heading; every `_index.md`; `00_INDEX.md` above its `## Notes` | `brushes/pipeline/notes.py write --confirm`, from `brushes/catalog/` |
| `_Previews/` | `brushes/pipeline/previews.py render --confirm` |
| `_BrushTags/*.tags.json` and the two `.jsonl` logs | `tools/brush_tags.py apply --confirm` |
| `tools/rag_index/` (ignored) | `tools/brush_search.py index` |
| `brushes/catalog/**` | `brushes/pipeline/ingest.py build` (and `previews.py render --confirm` for the preview fields) |

## What is authored

Only these. Everything else is generated or logged.

- The text under each note's `## Notes` heading (and under that heading in each `_index.md` and in `00_INDEX.md`).
- `_BrushTags/vocabulary.yaml`, the closed tag vocabulary.
- This file, `brushes/spec.yaml`, `brushes/docs/CONTRACTS.md`, `brushes/schema/*.json`, `brushes/library/sources.json`.

## Rules for editing notes

1. **Never write the generated part of a note with Write or Edit.** Change the catalog or the template and regenerate: a dry run first (`python -I brushes/pipeline/notes.py write`), then `--confirm`. The generated part is everything from the frontmatter to the blank line before `## Notes`; its `generated_fingerprint` is the first 16 hex characters of the sha256 of that text with the fingerprint value blanked (`generated_fingerprint: ""`). A hand-edited generated part no longer matches its fingerprint and the note is `REFUSED`: nothing is written for it and the run exits 1. `--overwrite-generated` replaces it, shows the lines it throws away, and still needs `--confirm`.
2. **Write only below `## Notes`.** The split is at the *last* line that is exactly `## Notes`. Never add another `## Notes` line of your own: the first one would be pulled into the generated part and the note refused. Use `###` for sub-headings. Everything from that line to the end of the file is kept byte for byte (CRLF included) on every regeneration.
3. **Do not create notes by hand.** A note is created by `notes.py write --confirm`. A file the catalog does not ask for is reported as an `orphan` and never deleted; `notes.py check` exits 1 for it.
4. **Never fabricate a setting.** Every number or texture name you quote must appear in the cited brush section or in `brushes/catalog/brushes/<brush_id>.json`. A note rounds for reading (`%.3f` for size and spacing, `%.2f` elsewhere); the exact value is in the record. If a value is `n/a` in a note, the file does not carry that key (older eras lack some keys: the five oldest eras have no pencil taper keys, and the oldest has no blend mode); say so, do not guess.
5. **Cite brush ids.** Names are not unique: some sets hold two brushes with one name (their headings get ` (2)`, ` (3)` in plist order) and many names recur across sets. Every claim cites `<brush_id>` plus the note path and heading as the search tool returned them. Line numbers are 1-based file lines.
6. **Reserved headings.** `Overview`, `Shared brushes` and `Notes` are structure. A brush that is really called one of those is headed `Overview (brush)` and so on.
7. **Regenerate after every catalog change, in this order:** `ingest.py build`, `previews.py render --confirm`, `notes.py write --confirm`, `brush_search.py index`, tag backfill, `brush_search.py index` again. Run `python -I brushes/pipeline/notes.py check` to see whether the notes still match the catalog (it exits 1 on any drift, writes nothing and needs no library, so it suits CI).

## A note, and a brush section

A note is: frontmatter; `# <title>`; `## Overview` (a generated paragraph of counts, sources and the pack's licence note); one `## <brush display name>` per brush **whose home is this set**, in plist order; an optional `## Shared brushes` (one stub line per member whose home is another set, linking to its section there); then `## Notes`. Layout version `b1` (`CHUNKER_VERSION`), template `brushset-note/1`.

A **brush section** is an H2 whose first list line matches ``- id: `b_<12 hex>` ``. It has twelve list lines, always present, in this order:

| Line | Holds |
|---|---|
| `id` | the brush id, its position in the set (`2 of 6`), its format era and its archive key count |
| `kind` | `stroke` or `stamp`, the spacing class and the exact spacing; `dual` when a second brush is stored inside |
| `shape` | where the shape image is (`embedded` with its size and polarity, `bundled` by file name, `none`), the measured tile numbers once previews exist, and scatter, rotation, randomised, azimuth |
| `grain` | the same for the grain (`blank` is Procreate's blank grain), then scale, movement, zoom |
| `size` | minimum to maximum size with its class, and the opacity range |
| `pressure` | the size and opacity pressure classes with their numbers |
| `tilt` | the tilt settings above the threshold, or `none` |
| `speed` | the two speed settings, or `none` |
| `taper` | the taper class, the pencil start/end lengths and the touch start/end lengths |
| `render` | the render code, blend mode, flow and whether the wet-mix guess holds |
| `facets` | the brush's facet words, space-separated, exactly as in its record |
| `preview` | where the stroke preview came from, and which texture images are not in the file |

Under the lines is the stroke preview, ``![[_Previews/<home set>/<brush id>.stroke.png]]``. A link may point at a file that does not exist yet; `notes.py` never creates an image.

## Facet glossary

Facets are computed from the archive by code (`brushes/pipeline/ingest.py`, thresholds in `brushes/schema/facets.json`) and stored in each brush record. **A facet class is a heuristic and a name guess.** Always quote the raw number beside the class, as the notes do (`spacing tight (0.026)`). A facet word uses `-`, a facet name `_`. The six texture facets at the end are `null` until `previews.py render` has measured the tiles; a note written before then shows no texture numbers, and `notes.py check` reports it as changed once they exist.

| Facet | Words | What it is |
|---|---|---|
| `kind` | `stroke` `stamp` | S(stamp) is true: stamp; otherwise stroke. The schema labels the key `Stamp preview`; what the app does with it is not measured |
| `is_stamp` | no word | S(stamp) is true |
| `spacing` | no word | plotSpacing, rounded |
| `spacing_class` | `spacing-continuous` `spacing-tight` `spacing-visible` `spacing-dotted` | the class of spacing |
| `shape_source` | `shape-embedded` `shape-bundled` | container.resolve_textures: embedded, bundled, bundled-supplied or none |
| `uses_bundled_shape` | no word | the shape is an image named by the archive that ships inside the drawing app |
| `grain_source` | `grain-embedded` `grain-bundled` `grain-blank` `grain-none` | container.resolve_textures: embedded, bundled, bundled-supplied, blank or none |
| `has_grain` | no word | an embedded grain (whose contrast, once measured, is at least embedded_min_contrast), or a bundled grain that is not the blank one |
| `uses_bundled_grain` | no word | the grain is an image named by the archive that ships inside the drawing app, the blank one included |
| `grain_movement` | no word | textureMovement: static_at or less static; rolling_from or more rolling; else partial |
| `grain_application_code` | no word | textureApplication, the raw number |
| `wet_mix` | `wet-mix` | dynamicsRenderType == 3 when the archive has that key; otherwise dynamicsMix > 0. A name guess (docs/CONTRACTS.md F5); render_code carries the raw number |
| `render_code` | no word | the raw render switches: `render-type-<n>` from dynamicsRenderType; `glaze-type-<n>` from dynamicsGlazeType (E0); `transfer-<max or std>.<mod or flat>.<rec or simple>` from the three rendering* keys (modern) |
| `taper` | `taper-start` `taper-end` `taper-both` | none, start, end or both, from taper_start and taper_end |
| `taper_start` | no word | the largest of the keys is above the bound |
| `taper_end` | no word | the largest of the keys is above the bound |
| `pressure_size` | no word | dynamicsPressureSize, rounded |
| `pressure_size_class` | `pressure-size-inverse` `pressure-size-low` `pressure-size-medium` `pressure-size-high` | the class of pressure_size |
| `pressure_opacity` | no word | dynamicsPressureOpacity, rounded |
| `pressure_opacity_class` | `pressure-opacity-inverse` `pressure-opacity-low` `pressure-opacity-medium` `pressure-opacity-high` | the class of pressure_opacity |
| `tilt` | `tilt` | any of the keys is above the bound |
| `speed` | `speed` | the absolute value of any of the keys is above the bound |
| `size_min` | no word | minSize, rounded |
| `size_max` | no word | maxSize, rounded |
| `size_class` | `size-fine` `size-medium` `size-broad` `size-max` | the class of size_max |
| `opacity_min` | no word | minOpacity, rounded |
| `opacity_max` | no word | maxOpacity, rounded |
| `translucent` | `translucent` | opacity_max is below the bound |
| `dual` | `dual` | the brush folder holds Sub01/Brush.archive (not the dualBlendMode key) |
| `dual_blend_code` | no word | dualBlendMode, the raw number |
| `blend_code` | `blend-<n>` (not for 0) | blendMode, the raw number |
| `blend_extended_code` | no word | extendedBlend, the raw number |
| `scatter` | `scatter` | shapeScatter is above the bound |
| `shape_rotation` | `shape-rotation` | shapeRotation is not 0 |
| `randomised` | `randomised` | shapeRandomise is true |
| `azimuth` | `azimuth` | shapeAzimuth is true |
| `jitter_size` | `jitter-size` | dynamicsJitterSize is above the bound |
| `jitter_opacity` | `jitter-opacity` | dynamicsJitterOpacity is above the bound |
| `jitter_position` | `jitter-position` | plotJitter is above the bound |
| `streamline` | `streamline` | plotSmoothing is above the bound; a name guess |
| `color_dynamics` | `color-dynamics` | any hue, saturation, lightness, darkness, brightness or secondary-colour dynamics key is not 0 |
| `wet_edges` | `wet-edges` | wetEdgesAmount is above the bound |
| `burnt_edges` | `burnt-edges` | burntEdgesAmount is above the bound |
| `era` | `era-<id>` (lower case) | brush_model.detect_era: an era id, or X<count> |
| `family` | no word | brush_model: legacy or modern (an X<count> archive takes its nearest era's) |
| `stroke_source` | `no-thumbnail` | preview.stroke_source: at build, thumbnail, reset-thumbnail or none from which member exists; settled by apply_preview_results |
| `shape_coverage` | no word | mean of the normalised shape tile over 255 |
| `shape_aspect` | `shape-tall` `shape-even` `shape-wide` | width over height of the bounding box of tile values above 16 |
| `shape_midtone` | `shape-hard` `shape-mixed` `shape-soft` | share of tile values between 16 and 240 among values above 16 |
| `shape_edge_touch` | no word | the border ring's mean over 0.05 |
| `grain_mean` | no word | mean of the grain tile over 255 |
| `grain_contrast` | `grain-flat` `grain-subtle` `grain-medium` `grain-strong` | population standard deviation of the grain tile over 255 |

## Measured, described, bundled

- **Measured** — facets and texture statistics are computed by code from the files.
- **Procreate's render** — a stored thumbnail is the drawing app's own picture of the brush's stroke, exact even when the shape and grain are bundled. `rendered-approx` is reserved and v1 never writes it.
- **Described** — a sidecar's `visual:` sentence is *Claude's description of a preview*, `visual_basis: described-not-measured`. It is never a measurement; do not cite it as one.
- **Bundled** — a shape or grain that only has a file name (`Brush-Preset-Hard.png`) ships inside Procreate and is not in the library. There is no tile for it. **Never describe a bundled texture's look from its file name.** If the file was supplied at `library/bundled/<name>` the source reads `bundled-supplied` and a real tile exists.
- **Placeholders** — when a brush has no usable thumbnail (`stroke_source` is `none`, facet word `no-thumbnail`) its preview tile is a placeholder and carries no visual information.
- Label and enum meanings in `brushes/schema/silica_keys.json` are inferred from key names unless the schema marks them `verified`. Say "the key `dynamicsRenderType` is 3", not "this brush is wet-mixing".
- Nothing here has been opened in Procreate: `brushes/spec.yaml` `device_test` records every path as `untested` and wording must stay "has not been opened in Procreate".

## Searching: `tools/brush_search.py`

Self-contained search over the notes and the brush records (TF-IDF over one chunk per brush, plus tag and facet filters). Standard library only, no network, no embeddings.

```
python brushes/vault/tools/brush_search.py index [--check]         # rebuild the index; --check exits 0 when fresh, 1 when stale
python brushes/vault/tools/brush_search.py search "<query>" [--tag AXIS=V[,V2]]... [--where KEY=V|MIN..MAX]... [--where-not KEY=V]... [--top N] [--offset N] [--source TYPE] [--settings] [--json]
python brushes/vault/tools/brush_search.py ask    "<query>" ...    # the same, a second spelling
python brushes/vault/tools/brush_search.py similar <brush id | id prefix | exact name> [--other-sets] [--top N]   # brushes with similar settings
python brushes/vault/tools/brush_search.py facets  [--axis A] [--settings]   # facet, tag and vocabulary counts, over the filtered set
python brushes/vault/tools/brush_search.py files   [--type T]               # the note files the index holds
python brushes/vault/tools/brush_search.py chunks  <note path> [--ids …] [--range A-B] [--untagged] [--brief]   # a note's chunks, as the tagger sees them
python brushes/vault/tools/brush_search.py verify  [--from FILE] [--strict]  # mark values in a digest that the brush record does not hold
python brushes/vault/tools/brush_search.py brush   <brush id | prefix | name> [--settings]   # everything the index holds about one brush
```

Run any verb with `--help` for its exact flags. What the contract fixes (`brushes/docs/CONTRACTS.md`, F9):

- `--tag AXIS=V[,V2]` is repeatable and ANDed; a comma list is OR. The axis is the short name (`medium`) or the stored key (`medium_tags`). An unknown axis or value exits 2 with the valid list.
- `--where KEY=V1,V2` and `--where KEY=MIN..MAX` (inclusive; either side may be empty), `--where-not KEY=V`. A key is a facet name, a raw setting key, or one of `id`, `set`, `library`, `tagged`. There are no comparison operators, so the grammar is safe to type unquoted.
- A result row carries `brush_id`, `name`, `set`, `note`, `heading`, `start_line`, `end_line`, the six tag lists, `visual`, `tag_state` (`tagged`, `stale` or `untagged`), `facets`, `preview`, `also_in` and `record`. Settings are included only when asked.
- Ranking is `cosine` for a query, `tag-purity` for tags only, `filter-order` for filters only. Results are de-duplicated by brush id.

**When to search rather than recall:** before saying a brush exists or does not, before comparing brushes, before recommending one ("a soft charcoal that tapers"), and whenever you quote a number. Cite results as brush id + note path + heading/line range, exactly as the tool returned them.

## Tagging

A brush has up to six kinds of tag, from a **closed vocabulary** the author owns: `_BrushTags/vocabulary.yaml`, with top-level `<axis>_tags:` keys, two-space `- tag` items and one `#` definition per tag on the same line.

| Axis (stored key) | Cap per brush |
|---|---|
| `medium` (`medium_tags`) | 2 |
| `mark` (`mark_tags`) | 2 |
| `texture` (`texture_tags`) | 3 |
| `edge` (`edge_tags`) | 2 |
| `motif` (`motif_tags`) | 2 |
| `use` (`use_tags`) | 3 |

How it works:

1. `tools/brush_tags.py plan [--only SUBSTR] [--ids …] [--force] [--limit N]` lists what is left to tag, batched by contact sheet. The tagger reads **contact sheets** (`_Previews/_sheets/<set_slug>/sheet-NN.png`, ignored by git, 8 brushes each, at most two sheets per call), not the notes' numbers.
2. The tagging agent **returns text only**, one block per brush (`### brush <id> (name: "…", chunk <n>, lines <a>-<b>, fp: <16 hex>)` followed by the six `*_tags:` lines, `visual:`, `evidence:`, `notes:` and `suggestions:`). It writes no file.
3. `tools/brush_tags.py apply --file NOTE [--ids …] [--from FILE] [--confirm]` (the note's vault path or its set slug; the reply on standard input unless `--from`) checks each block and, with `--confirm`, writes the sidecar `_BrushTags/<note path>.tags.json`. It rejects a block whose id is not in the note, whose `fp` differs from the catalog, whose tag is outside the vocabulary, that is over a cap, or whose `visual:` is empty while its evidence is not `none`. A word outside the vocabulary is logged as a suggestion for the author, never accepted.
4. `brush_tags.py check [--strict]` checks every sidecar against the vocabulary and the catalog and finds stale or missing entries (an entry is stale when its `content_sha256` differs from the catalog's); `suggestions` lists the logged proposals.

Rules: **never write a sidecar or a log by hand.** Tag a brush only from its preview and its facts. Visual tags (`texture`, `edge`) and `visual:` are withheld only when `stroke_source` is `none`; a bundled shape or grain does not withhold them, but the tagger must not describe a texture it cannot see. A tag is a description of a preview, never a measurement. The `tags:` list in a note's frontmatter is **not** the brush tags: it is the fixed `brushset`, `library/<library>` and `era/<id>` list, so a note never depends on the sidecars. Tag results reach you through the search tool.

## What never to write

- Anything under `brushes/library/`, `brushes/catalog/` or the original `.brush` / `.brushset` files — not from here.
- A note, `_index.md` or `00_INDEX.md` above its `## Notes` heading; a `.tags.json` sidecar; a `.jsonl` log; anything in `_Previews/` or `tools/rag_index/`.
- A timestamp or an absolute path into any generated file. The notes hold neither, and two runs on the same catalog give the same bytes.
- An author picture or a signature. They are personal images, recorded by presence only and never copied to a preview.
- A claim about licence beyond what the pack's manifest entry says. `redistribute` (`yes`, `no`, `unknown`) is recorded information in `brushes/library/sources.json`; it gates nothing and a note quotes it.

## Publication

Originals, the catalog, the notes, the tag sidecars and the tracked previews are committed; the original brush files go through Git LFS. The search index (`tools/rag_index/`), the contact sheets (`_Previews/_sheets/`) and the previews of a pack whose manifest says `publish_previews: false` (`_Previews/_local/`) are ignored. Shape and grain tiles are reduced copies of vendor art, so a pack can opt out of publishing them.
