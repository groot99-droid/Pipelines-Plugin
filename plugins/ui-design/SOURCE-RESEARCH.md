# Source research — extending the design-system catalog

Baseline (from `catalog/data/catalog-summary.json`, as it stood on 2026-08-13):
88 styles / 192 products / 192 palettes / 74 font pairings / 119 UX guidelines /
17 motion presets / 25 chart types / 22 stacks / 1,934 Google Fonts / 1,512 Phosphor icons.

Everything below is scored against *that* baseline: what it adds that you do not already have.

---

## Tier 1 — fills a real gap, permissively licensed, machine-readable

### 1. W3C DTCG design tokens + Style Dictionary
- Spec: https://tr.designtokens.org/format/ · https://github.com/design-tokens/community-group
- Transformer: https://github.com/amzn/style-dictionary (Apache-2.0)
- **Gap it fills:** your generator emits a *described* system (prose + hex). It does not emit a
  portable artifact. Emitting DTCG-compliant `tokens.json` makes output consumable by Tokens Studio,
  Supernova, Penpot, Style Dictionary, Zeroheight — 14+ tools natively in 2026.
- **Action:** ~~add a `--format dtcg` exporter~~ — **done**, see `scripts/tokens.py`.
  `-f dtcg` on the CLI; `--persist` also writes `tokens.json` beside `MASTER.md`.

### 2. Reference token sets from shipped systems
- Material 3: https://github.com/material-foundation/material-color-utilities (Apache-2.0) — HCT color
  space + tonal-palette generation from a single seed. This is a real algorithm, not a lookup table.
- IBM Carbon: https://github.com/carbon-design-system/carbon (Apache-2.0) — full token JSON.
- GitHub Primer: https://github.com/primer/primitives (MIT) — already ships DTCG-shaped tokens.
- Adobe Spectrum: https://github.com/adobe/spectrum-tokens (Apache-2.0)
- USWDS: https://github.com/uswds/uswds (public domain) — best-documented spacing/type scale rationale.
- **Gap it fills:** your 192 palettes are curated/static. Tonal-palette generation gives you
  *derivable* full ramps (50–950) + guaranteed contrast pairs for any seed color.

### 3. APCA / contrast validation
- https://github.com/Myndex/SAPC-APCA (W3C-permissive) + `apca-w3` npm
- Culori (https://github.com/Evercoder/culori, MIT) for OKLCH/OKLAB conversion.
- **Gap it fills:** your checklist *says* "4.5:1 minimum" but nothing enforces it. Ship a validator
  that fails a generated palette before it reaches the user. Note APCA was dropped from the WCAG 3
  draft in 2023 — keep WCAG 2.2 ratios as the gate, APCA as advisory.

### 4. Platform rule corpora
- https://github.com/ehmo/platform-design-skills — 300–450 rules distilled from Apple HIG +
  Material 3 + WCAG 2.2, across iOS/iPadOS/macOS/watchOS/visionOS/tvOS/Android/Web.
- https://github.com/dickwu/apple-design-skill — includes `pull-hig.mjs`, a re-scraper for HIG.
- **Gap it fills:** your 22 stacks are framework-level (react, swiftui, flutter…) but you have no
  *platform-convention* layer. Check licensing before ingesting; prefer the scraper + your own
  distillation over copying rule text.

---

## Tier 2 — broadens coverage

### 5. Icons
- Iconify (https://github.com/iconify/icon-sets, MIT metadata) — 200k+ icons, 150+ sets, one
  normalized JSON schema. Superset of your Phosphor snapshot.
- Lucide (ISC, ~1,780 icons) — the shadcn/ui default, so it is what your React output will actually
  land in. Tabler (MIT, 5,900+) for breadth.
- **Action:** keep Phosphor curated, add Lucide as the React-stack default, use Iconify metadata for
  semantic search rather than shipping all 200k.

### 6. shadcn registry ecosystem
- registry.directory · https://ui.shadcn.com/docs/registry · tweakcn (https://github.com/jnsahaj/tweakcn)
- **Gap it fills:** shadcn registries are now a distribution format — a design system can *be* a
  registry. tweakcn themes follow the official CSS-variable contract, so a palette from your
  generator can emit a drop-in tweakcn-compatible theme block.
- **Action:** ~~second exporter~~ — **done**, `-f shadcn`; `--persist` also writes `theme.css`.

### 7. Motion
Your `motion.csv` is 17 GSAP-only presets. Missing: springs, CSS-native, and Framer Motion/Motion.
- https://motion.dev/docs/spring (stiffness/damping/mass model)
- Material 3 motion spec (emphasized/standard easing sets + duration tokens)
- **Action:** ~~add `Spring Params` / `CSS Snippet` / `prefers-reduced-motion` columns~~ —
  **done** via `scripts/add-motion-columns.py` (idempotent migration).

### 8. Penpot
- https://github.com/penpot/penpot — native design tokens (not a plugin) + an official MCP server
  merged into the main repo under `/mcp` since Dec 2025.
- **Gap it fills:** a round-trip target that does not require a Figma license. Your generated system
  could be pushed into a real editable design file.

---

## Tier 3 — research data, useful for validation not for shipping

- **WebUI** (~400k web pages, 6 device viewports each) — https://arxiv.org/pdf/2301.13280
- **RICO** (Android app screens) — https://huggingface.co/datasets/Voxel51/rico
- **Enrico** (1,460 hand-labeled UIs, 20 design topics) — https://userinterfaces.aalto.fi/enrico/
- **Use:** not training data for you — use them to *validate* that your 192 product categories and
  34 landing patterns match observed real-world layout distributions. Enrico's 20 topics are a
  sanity check on your category taxonomy. Check licenses: RICO is research-use.
- Common Crawl top-500 contrast audit: https://arxiv.org/pdf/2602.24067 — empirical baseline for
  "how bad is contrast in the wild", useful for justifying your gates.

## Skills / plugins worth studying (not necessarily ingesting)
- `anthropics/claude-code` → `plugins/frontend-design` — the official skill; note how it phrases
  anti-defaults ("not Inter + purple gradients"), which overlaps your anti-pattern list.
- Curated lists: `travisvn/awesome-claude-skills`, `VoltAgent/awesome-agent-skills`
- `klaufel/awesome-design-systems`, `component-driven/awesome-list` — bookmark-level, good for
  finding systems you have not catalogued.

---

## Recommended order of work
1. ~~DTCG token exporter~~ — **done** (`scripts/tokens.py`, `-f dtcg`, 20 tests)
2. ~~Contrast validator as a hard gate~~ — **done** (`scripts/contrast.py`, `--strict-contrast`).
   Text pairs enforce 4.5:1; non-text (border/ring) stay advisory at 3:1, because an audit
   of all 192 palettes showed every text pair already passes while 173/192 use a sub-3:1
   border by design. Gating on those would fail 90% of the catalog.
3. Tonal-ramp generation via material-color-utilities (static palettes → derivable ramps)
4. ~~shadcn-theme exporter~~ — **done** (`scripts/shadcn_theme.py`, `-f shadcn`, oklch via
   `scripts/oklch.py`). `chart-*`/`sidebar-*` deliberately omitted rather than fabricated.
5. ~~Motion CSV: spring + CSS + reduced-motion columns~~ — **done**. 3 columns x 17 rows,
   authored per row (a spring is not inferable from an easing name). Scrub/loop/timer rows
   say `n/a - <why>` rather than carrying a plausible-but-wrong number. DTCG now emits
   spring params and the reduced-motion fallback under `$extensions`.
6. Platform rule layer (HIG/M3/WCAG) — largest effort, check licensing first

## Licensing note
Apache-2.0 / MIT / ISC / public-domain sources above are safe to ingest with attribution.
Apple HIG text is **not** — distill rules yourself from the scraper rather than copying prose.
RICO/Enrico are research-licensed. Track all of this in `data-provenance.json`, which already has
the right schema for it.

---

## Harvesting tokens from real sites (added this session)

`maintenance/harvest-site-tokens.py` — **maintainer tooling, deliberately not part of `catalog/`.**

The skill tells users its scripts use "only the standard library — no third-party
packages, no network access" (`.claude/skills/ui-design-catalog/SKILL.md`). The skill
runs only `catalog/`, so `maintenance/` stays out of it and that claim stays true. A test
(`TestNotShipped`) asserts the tool is absent from `catalog/scripts/`, and
`maintenance/validate-contract.py` fails if anything under `catalog/` imports a
third-party package. Harvested values reach users only as reviewed CSV rows, never as a
live fetch.

### Why computed styles, not a crawler
A design token is what the browser *resolved*. Static HTML+CSS fetching misses the
cascade, JS-applied themes, and `@layer`/`@theme` blocks. Three failure modes hit while
building this, each of which returns plausible-looking data:

1. **Storybook/iframe shells** — `primer.style` redirects into a Storybook. Outer document:
   0 custom properties, but a complete type scale *of Storybook's own chrome*.
2. **Tokens outside `:root`** — Tailwind v4 declares in `@theme`/`@layer`, and cross-origin
   stylesheets throw on `.cssRules`. Reading stylesheets found **2 variables** on a page
   with hundreds.
3. **Modern color spaces** — `getComputedStyle` returns `oklab()`/`lab()`. On
   tailwindcss.com only **1 of 13** distinct backgrounds was `rgb()`; an rgb-only parser
   drops ~90% and reports success.

Fix for (3) is the useful trick: canonicalize every color through a **1×1 canvas**, using
the browser's own color engine. Handles every present and future color function exactly.

### Licensing
Harvested values describe one page of one site at one moment. Measurements (a 1.5
line-height ratio, an 8px spacing base) are facts; a site's specific brand palette is its
identity. Aggregate statistics across many sites are safe to record; lifting one site's
palette wholesale into the catalog is not. Record provenance in `data-provenance.json`.
