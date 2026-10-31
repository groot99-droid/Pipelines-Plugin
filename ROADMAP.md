# ROSW (Pipelines-Plugin) — Audit & Expansion Roadmap (2026-10-30)

## Context
The author asked for a read-only pass over the whole repo to find what needs **fixing**, **optimizing**, and **generalizing from one tool/use case to many**; to propose **new pipelines** that the newly-available tools make possible; to improve existing **skills and agents**; and to plan a **graphic-design toolkit** (Claude-native image/vector generation, Adobe-specific tools, free artist tools). Nothing is to be built now — the goal is to collect everything and store it for later.

Findings cite paths relative to the repo root. Severity: **P0** broken/unsafe, **P1** wrong or misleading, **P2** quality/optimization.

---

## Part A — Fixes

### P0 (broken or unsafe)
1. **Blender MCP tool prefix is probably wrong.** `plugins/blender/agents/blender-scene-reviewer.md:4` grants `mcp__blender__*`; plugin MCP tools are named `mcp__plugin_<plugin>_<server>__<tool>`. If so, the reviewer has no Blender access. Same prefix in `blender-mcp/SKILL.md:17`, `references/tools.md:3`, `blender-addon-tools/SKILL.md:10`, and enforced by `plugins/blender/tests/test_tool_names.py:169`. Confirm the real names in a live session first, then fix all + the test.
2. **81 untested Blender add-on tools are enabled.** `blender-addons/manifests/*.json` all `"enabled": true` (`build_manifests.py:257`), contrary to the skill's own rule (`blender-addon-tools/SKILL.md:63-64`). `addon-tools/server.py:126` defaults a missing `enabled` to on. → default off, ship drafts, fail-closed default.
3. **Signed links can land in the Meshy ledger.** `studio/pipeline/meshy_client.py:398-407` masks only `data:` URIs; an `https://` input is written verbatim to `meshy_tasks.json` (`:462`) and copied into Method. Also `require_go_ahead` checks only `class == spend` (`:309`), so any spend run can post to Meshy — gate on pipeline id.
4. **Hub `POST /api/runs` has no Origin/Host check** (`studio/hub/serve.py:220-233`) — CSRF/DNS-rebinding on loopback. Low impact, cheap fix.
5. **Public CDN bearer-ish links.** `studio/library/catalog.json` holds permanent CloudFront URLs containing the account user id; `content_md.py:87-97` lint doesn't flag CloudFront/Canva/Figma/Gamma share links. Decide policy; extend lint regardless.

### P1 (wrong / misleading / fragile)
6. **video-editor fails on Windows.** No `encoding=` on read/write across `src/videoeditor/` (`questionnaire.py:158,166`, `cli.py:90,99,142,198`, `render.py:493,549,761`, `captions.py:54,142`, `pack.py:127`, `timeline.py:121`, `transcribe.py:108`, `ledger.py:21`, `package.py:77`, `publish/cli.py:35`); `fc-match` assumed (`captions.py:35`, `platform.py:18`). CI runs it on Linux only (`.github/workflows/verify.yml:66-74`). Fix, then add Windows/macOS to the matrix.
7. **Outdated model id.** `creative-writing/pipeline/llm.py:83` defaults to `claude-sonnet-5` → `claude-sonnet-5-5`. Make it configurable and documented.
8. **Anthropic backend truncation.** `llm.py:107-133` fixed `MAX_TOKENS=8000`, no `stop_reason` check, no retry/streaming; Ollama call 600 s no retry (`llm.py:152`).
9. **Uncaught JSON in vault integration.** `run_pipeline.py:~483-500` `json.loads`/`meta["title"]` on model output; `_run_and_advance` (`:590`) only catches `LLMError`/`VaultIntegrationError`. `_extract_idea_themes` (`:183-231`) misses bulleted themes.
10. **Unpinned servers.** `plugins/blender/.mcp.json` `uvx mcp-for-blender` (docs/tests pinned to 2.2.6, `test_tool_names.py:145`); root `.mcp.json` `npx -y gemini-mcp-tool`. Pin and add a test that the pin matches.
11. **Compute gate is one-laptop-shaped.** `probe.py:190-193` treats only `nvidia-smi` as discrete (AMD/Arc read as integrated); `machine.yaml:26` refuses every class on any NVIDIA box; first GPU only (`probe.py:39`), `C:` only (`:48`); token TTL 1800 s (`machine.yaml:21`) can't cover long renders; one global token (`compute_gate.py:56`).
12. **scene-blender local branch unenforced** — `class: spend`, no `workload`, so `token_held` returns early (`studio_run.py:417`); `spec.yaml:1057` says "scene-3d" where it means scene-blender (also `IDEAS.md:136`).
13. **Spec test rejects hyphenated MCP server names** (`studio/pipeline/tests/test_spec.py:135`), so UUID/hyphen connectors can never be allowlisted.
14. **"63 works" is stale everywhere** (INDEX.md:15, README.md:24, CLAUDE.md:30, `vault/00_INDEX.md:3`, museum README). Vault has ~138 works; 75 lack `_ChunkTags`. **Decision for author:** does the "certified verbatim, do not edit" rule cover all 138 or only the original 63?
15. **Doc drift.** `run_pipeline.py:4-12` + `requirements.txt:6` say librarian is Ollama-only (it supports Gemini); `llm.py:22` points at nonexistent `Pipelines/README.md`; `sound-library/README.md:50-51` says 2,648/16 zips (actual 3,577/23); `docs/index.html:7,29` says "four tools" (7 shown); `IDEAS.md:124` "eight of ten" (12 entries); README layout misses 5 root skills + writing-museum/sound-library/hub/library/workflows; CLAUDE.md layout misses reach-research/references, render-pipeline, sound-library. Blender add-on button "Connect to MCP server" (`blender-mcp/SKILL.md:24`) vs "Start MCP Server" (`blender-gemini/README.md:27`).
16. **HyperFrames is a phantom option** — offered in `questionnaire.py:65-66`, rejected by `cli.py:352`. Implement or remove.
17. **Windows-hostile paths/commands:** `/tmp/` in `plugins/reach/skills/agent-reach/SKILL.md:74,130` and `video-editor/tests/test_doctor.py:76`; bash `export` in `blender-addons/README.md:13`; `manim-video/README.md:22` wrong upstream path + bash-only `setup.sh`.
18. **assemble-3d only accepts `.glb/.gltf`** (`bpy/assemble_plan.py:179-187`); spec tool names (`spec.yaml:1248-1251`) don't match the official `mcp__Blender__*` server available now.

### P2 (quality)
19. `brush` pipeline + `hub/brush/` designer missing; `brush_pack.py` never verified against Procreate; fixtures folder absent.
20. Duplicated logic: key-file reading (`meshy_client.py:161-184`, `llm.py`, `setup_keys.py`); `.part` downloads (`meshy_client.py:239-266`, `library/library.py:228-238` — leaves stray `.part` on error). Extract one helper.
21. Hub scrapes `cmd_new` stdout for run id (`serve.py:136`) → have `studio_run.py` emit JSON.
22. Repo weight: 1,155 of studio's 1,238 files are `studio/library/thumbs/*.webp` (12 MB, grows each sync); 1 MB `studio/docs/inventory/` names a local path. Consider release-artifact thumbs and archiving inventory.
23. `ui-design` ships a second `marketplace.json` that can drift from root; generate it.
24. `blender/backrooms_L1_blockout.py` (outside repo) is untracked, no export step, estimated tri count.

---

## Part B — Generalize single-vendor / single-use pieces

The central pattern: **replace hard-wired vendor tool lists with a provider registry.**

**B1. `providers.yaml` + capability-based allowlists (studio).** Today still-image/video-shot/music-cue/scene-blender call only `mcp__Higgsfield__*`, edit-2d only Adobe, asset-3d only Meshy (`spec.yaml:596-1201`). Introduce `studio/pipeline/providers.yaml` mapping capabilities → providers → tool names:
- `image.generate`: Higgsfield, Adobe Firefly/Express, Canva `generate-image`, Figma `generate_image`/`weave_run_model`, Gamma `generate_image`, Claude-native SVG/canvas (Part E).
- `image.edit`: Adobe (bg remove, fill, expand, adjustments, vectorize), Canva (`remove-background`, `separate-image-layers`), Higgsfield (`upscale_image`, `outpaint_image`, `reframe`), Affinity `execute_script`, local Pillow/ImageMagick/GIMP (`batch_2d` class, currently unused).
- `video.generate/edit`: Higgsfield, Adobe `video_*`, local `plugins/video-editor`.
- `audio.generate`: Higgsfield; `audio.library`: `sound-library/`.
- `model3d.generate`: Meshy (REST), Higgsfield `generate_3d` (Tripo), Higgsfield scene builder; future Rodin/Hunyuan.
- `layout/doc/deck`: Canva, Adobe Express/InDesign (IDML), Figma, Gamma, Affinity.
Pipelines declare capabilities; the recipe stage picks a provider and records it in the note. Resolve by bare tool name at run time so aliased/UUID servers work (fixes #13). Also **generate `.claude/settings.json` permission rules** from `connector.tools` + `connectors.never` so the allowlist is enforced, not advisory (W8).

**B2. 3D provider interface.** Factor `meshy_client.py` into `create / wait / download / ledger / budget` and add a Higgsfield/Tripo adapter behind the same ledger and price checks. Merge scene-blender (cloud) and assemble-3d (local) into one pipeline with backend branches; accept FBX/OBJ/USD/.blend; revive the dropped `camera_path.py` / `lowpoly_gen.py` templates as plan steps.

**B3. Per-project brand context.** `context_root` is global (`spec.yaml:20`) and only 3 of 10 gates exist (visual_identity, typography_system, color_science). Allow `_Context/brand/<project>/` with fallback to global, so Who Did It (pixel art), the Museum, and client work stop forcing STATED rows. Prioritize authoring `brand_voice` (unblocks `ui-build`), `motion_language`, `sound_identity`.

**B4. Multi-source generations library.** `studio/library/library.py:88-112` normalizes Higgsfield only. Add source adapters (Adobe, Canva, Figma, Gamma, Meshy ledgers, `studio/assets/`) and a hub tab; generalize `higgsfield-library-sync` → `generations-library-sync` with a `--source`.

**B5. Compute gate profiles.** Per-machine profiles, AMD/Intel discrete detection, a `gpu` class, job-length tokens/renewal, use or drop `llm_local_*`/`batch_2d`.

**B6. Generalize neighbour skills.** `render-pipeline` is Who-Did-It only (`$WDI` paths) → profile-driven per game (reuse udgt profile pattern). `sound-library` assumes GitHub Releases → storage backend option. `reach-research`/`reach-references` hard-code repo paths → thin toolsets pointing into the reach plugin.

**B7. One Blender route decision note.** Four paths exist: blender plugin (`uvx mcp-for-blender`), `blender-gemini`, the official `mcp__Blender__*` server now in this environment, and studio assemble-3d. Write one routing table (which for what), and align tool names to the official server where possible.

**B8. ui-design beyond screens.** Catalog is UI-only (12 domains, 22 stacks, WCAG contrast). Add a sibling **`graphic-design` catalog/plugin** (Part E) rather than overloading ui-design.

---

## Part C — Optimize existing skills & agents

**Skills**
- Add `allowed-tools` to script-running skills (ui-design, video-editor, udgt, reach-setup, studio-pipeline).
- Split long bodies into `references/`: `ui-design-catalog/SKILL.md` (265 lines), `manim-video/SKILL.md` (264), `ui-design-catalog-refresh` (179). Drop non-standard `version:` in manim-video.
- Fix triggers: `agent-reach` "MUST USE" (`SKILL.md:3-19`) over-claims vs WebSearch/WebFetch and udgt-field-research; `ui-design-catalog` fires on any front-end change; `studio-pipeline` description (`SKILL.md:3`) omits still-image, video-shot, music-cue, edit-2d, scene-blender, brand-gate → under-triggers. Have it read the spec's unused `intent:` lists.
- Add worked examples (call + expected output) to udgt, blender, reach-setup skills.
- Add slash commands (none exist in any plugin): `/ve-doctor`, `/blender-review`, `/reach-doctor`, `/ui-design-verify`, `/studio-status`.
- Add hooks: run `ve publish plan` before any send; block Write/Edit into `studio/vault/` and `creative-writing/vault/` originals (turns advisory rules into enforcement).
- English translations of agent-reach references (currently Chinese, `SKILL.md:137`).

**Agents** (none set `model:`; all 8 inherit)
- Set models: haiku-class for `ui-design-search-part`, `creative-writing-chunk-tagger`, `creative-writing-librarian-native`; sonnet/opus-class for drafter, chapter-analyst, reviewers.
- Fix drafter quietly reintroducing Ollama via Bash `librarian.py` (`creative-writing-drafter.md:44-46`).
- **New agents** (all read-only, one-part-per-invocation like the ui-design pattern):
  - Creative writing: *style-mode linter*, *continuity checker* (project world facts + characters), *fact-checker* (against reach-research notes), *plot-logic critic* (judges ledger links `plot_logic.py` can only shape-check), *annotation writer*, *poetry pairing finder*.
  - Studio (planned in `IDEAS.md:163`, never built): *precedent condenser*, *recipe drafter*, *run reviewer*.
  - video-editor: *render QA* (cuts, loudness, caption safe zones, platform dims/fps via ffprobe), *moment picker* (reads `takes_packed.md`).
  - blender: *asset licence/credit auditor*, *export validator* (scale, normals, materials).
  - udgt: *citation fact-checker* (`[[id]]`, `path:line`).
  - graphic-design: *print preflight reviewer*, *brand-consistency reviewer* (Part E).

**Coverage gaps to fill**
- video-editor questionnaire: real `mixed` recipe; ask `content` before `reframe`; reframe for square; standalone explainer/manim recipe.
- Writing Museum: 10 of ~138 works have rooms; `assets/models.json` empty; no audio.
- Teardowns: no `research/` folder anywhere though `udgt-field-research` targets it; right-door-wrong-exit stops at `06-history.md`.
- Reach channels unused by any toolset: twitter, linkedin, instagram, facebook, xiaohongshu, xiaoyuzhou, v2ex, xueqiu.
- docs/ pages missing: sound-library, blender plugin, blender-gemini, blender-addons, generations library.

---

## Part D — New pipelines to build

Studio pipelines (each = spec entry + capabilities from B1):
| id | Purpose | Providers |
|---|---|---|
| `ui-build` (finish) | token-only markup/CSS, browser-measured | local + Figma `use_figma` |
| `brush` (finish) | Procreate brushes via designer app | local `brush_pack.py`; Krita brush export as 2nd target |
| `vector-mark` | logo/icon/glyph as SVG | Claude-native SVG → svgo → Inkscape/Affinity/Illustrator refine; Adobe `image_vectorize` for raster→vector |
| `layout-print` | poster/flyer/zine/book spread with bleed & PDF/X | Adobe Express/InDesign (IDML), Affinity spreads, Scribus, Canva |
| `deck` | slides from a vault note or teardown | Gamma, Canva, Figma Slides, Adobe Express |
| `social-variants` | one master → platform sizes | Canva `resize-design`, Adobe resize, Higgsfield `reframe` |
| `edit-video` | concat/transcode/caption (fixes memorial-vicar living outside studio) | `plugins/video-editor`, Adobe `video_*` |
| `pixel-sprite` | Who Did It sprites/atlases | Aseprite/LibreSprite/Pixelorama + existing render-pipeline |
| `texture-material` | tileable PBR from prompt/photo | Higgsfield/Firefly → Blender bake; Poly Haven |
| `motion-graphic` | Lottie/SVG/After-Effects-style motion | Claude-native SVG+CSS/Lottie, Adobe `animate_design`, Figma motion, manim |
| `brand-kit` | export gates+tokens to Canva brand kit, Figma variables, Adobe font kit | Canva, Figma `get_variable_defs`/library, Adobe `font_create_kit` |
| `mockup` | product/print mockups | Adobe fill/expand, Higgsfield, Blender |
| `map-art` | worldbuilding maps (Wyrmreach etc.) | Felt, Inkscape, Higgsfield |

Cross-tool chains (meta-pipelines):
1. **Work → room → reel:** creative-writing → scene-3d → `walk_test.mjs` capture → video-editor (captions from verbatim passages) → `ve publish` (dry-run).
2. **Teardown → redesign:** udgt `01-ui.md` → ui-design `--design-system` → page-reviewer.
3. **Sound → video:** sound-library by mood/category per beat → video-editor → note.
4. **Research → draft → check:** reach-research → reference_pull → fact-checker at self_revision.
5. **Backfill:** chunk-tag the 75 untagged works → `00_INDEX.md` → `library.json` → batch `build_museum.py propose`.
6. **Blender → museum/teardown:** backrooms blockout → museum room geometry or right-door-wrong-exit chapter.
7. **Who Did It world loop:** `project: who-did-it` stories → udgt world chapter → render-pipeline → library → museum wing.
8. **Brand-everywhere:** brand-gate → brand-kit → Canva/Figma/Adobe/hub tokens in one pass.

---

## Part E — Graphic-design toolkit plan

### E1. Claude-native generation (honest scope)
Claude does **not** output raster images directly; it writes code that renders them. Native routes:
- **SVG** (logos, icons, patterns, diagrams) — highest fidelity; post-process with `svgo`, check with a viewBox/stroke linter.
- **HTML/CSS + canvas** posters and layouts → PNG/PDF via headless Chromium (Playwright already used by `walk_test.mjs`).
- **p5.js / generative art** (`anthropic-skills:algorithmic-art`), `canvas-design`, `theme-factory`, `brand-guidelines`, `slack-gif-creator`.
- **Blender bpy** for 3D renders, **manim** for math motion.
Plan: a `claude-native-render` helper (`html|svg → png|pdf` at set DPI) shared by `vector-mark`, `layout-print`, `motion-graphic`. Raster generation goes through providers (Higgsfield, Firefly, Canva, Figma, Gamma).

### E2. Adobe-specific
Already connected: **Adobe for Creativity** MCP (Express: image edits, `image_vectorize`, `image_generative_expand`, `image_fill_area`, fonts/`font_create_kit`, `animate_design`, Firefly boards, `export_idml`/`convert_pdf_to_indd`, `document_render_layout`, PDF tools, video tools) + skills `adobe-*` (batch-edit-photos, create-social-variations, design-from-template, retouch-portraits, resize, fonts). Desktop apps (community, unverified — check licence/maintenance before adopting):
- Photoshop/Premiere via UXP: `mikechambers/adb-mcp`.
- Photoshop/Premiere/Illustrator/InDesign: `matrayu/adobe-mcp`.
- Illustrator only: `ie3jp/illustrator-mcp-server` (`npx illustrator-mcp-server`).
- Reconsider the dropped COM/ExtendScript routes (`studio/docs/INVENTORY.md:154-170`) only if UXP servers fall short.
Plan: an `adobe` provider block in `providers.yaml`; a skill that routes cloud (Express MCP) vs desktop (UXP) by task; IDML round-trip for print.

### E3. Free/open tools to merge in
| Tool | Use | Agent route |
|---|---|---|
| **Affinity** (free; MCP already connected: `execute_script`, `render_spread`) | vector + raster + layout in one app | direct |
| **Inkscape** | SVG cleanup, text-to-path, PDF/EPS export | CLI (`inkscape --export-*`) + community MCPs (`inkscape-mcp`, `inkmcp` — Linux-leaning) |
| **GIMP 3** | raster batch edits | `gimp-agent-mcp` (3.0+) or Script-Fu batch |
| **Krita** | painting, brushes | `krita-cli` MCP (localhost HTTP plugin) |
| **Penpot** | open-source Figma alt | official Penpot MCP (hosted or local + plugin) |
| **Blender** | 3D, grease-pencil 2D | official `mcp__Blender__*` |
| **Scribus** | DTP / PDF/X print | Python scripter, headless |
| **ImageMagick / vips** | batch resize/convert | CLI under `batch_2d` |
| **vtracer / potrace** | raster→vector locally | CLI |
| **rembg / Upscayl (Real-ESRGAN)** | bg removal, upscale locally | CLI (CPU-feasible, gate by compute class) |
| **svgo, fonttools** | SVG optimize, font subset | CLI |
| **LibreSprite / Pixelorama** | pixel art for Who Did It | CLI export |
| **Darktable / RawTherapee** | photo grading | CLI |
| **Synfig / OpenToonz / Pencil2D** | 2D animation | CLI render |
| **Lottie (bodymovin) / Rive** | lightweight web motion | JSON output |
All community MCP servers are unverified; adopt under the same rules as blender-addons (draft, off by default, author enables).

### E4. Packaging: `plugins/graphic-design/`
A new self-contained plugin (CLAUDE.md "Adding a tool" rules, `${CLAUDE_PLUGIN_ROOT}` paths):
- `catalog/` (stdlib BM25, same engine as ui-design): print specs (paper sizes, bleed, DPI, CMYK/PDF-X), social size table, logo/identity rules (mark types, clear space, min sizes), illustration styles, poster/editorial grids, packaging dielines, colour for print (ΔE, ink limits) beside WCAG.
- Skills: `graphic-design-catalog`, `vector-mark`, `print-preflight`, `tool-router` (which app/provider for which job, with E2/E3 tables).
- Agents: `print-preflight-reviewer`, `brand-consistency-reviewer`.
- Studio consumes it read-only, like ui-design.

---

## Phasing (when work resumes)
1. **Stabilize:** P0 items 1–5, then P1 6–13.
2. **Truth pass:** doc drift (#14–18), decide "63 vs 138" rule, regenerate INDEX.
3. **Generalize:** B1 providers registry + generated permissions → B2/B4 → B3 per-project brand.
4. **Skills/agents:** Part C (models, allowed-tools, splits, new reviewers, commands/hooks).
5. **Graphic design:** E1 native render helper → E4 plugin catalog → `vector-mark`, `layout-print`, `social-variants`, `brand-kit`.
6. **New pipelines & chains:** remaining Part D.

## Verification (for each phase when executed)
- `python plugins/ui-design/maintenance/verify.py` (runs all gates + index check).
- Per-tool suites: `python -m unittest discover -s studio/pipeline/tests`, `-s creative-writing/pipeline/tests`, `-s plugins/blender/tests`, `-s plugins/video-editor/tests`, `-s plugins/udgt/tests`, `-s blender-addons/tests`, `-s blender-gemini/tests`, `-s sound-library/tests`, `-s writing-museum/build/tests`; `cd agent-reach && python -m pytest tests -q`.
- `claude plugin validate ./plugins/<name>` and `claude plugin validate .`.
- For MCP-name fixes: a live session listing the actual tool names before editing.

## Open decisions for the author
- Does "certified verbatim" cover all ~138 works or only the original 63?
- Keep CDN links/thumbnails in the public repo, or move to releases/ignore?
- New `plugins/graphic-design/` vs extending ui-design?
- Which free tools to adopt first (suggest: Affinity, Inkscape CLI, Penpot, ImageMagick, vtracer).
