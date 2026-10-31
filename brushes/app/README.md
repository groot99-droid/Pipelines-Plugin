# brushes/app

The browser app of the brushes tool: a **Library** tab (search the catalog) and a
**Designer** tab (open a brush, change its settings, export a `.brush` or
`.brushset`). Vanilla ES modules: no build step, no framework, no CDN, no inline
script or style, no network except the loopback server that serves it
(`docs/CONTRACTS.md` F10 "HTTP"; the CSP forbids the rest).

**Nothing this app writes is proven to open in Procreate** until the iPad
sittings in `brushes/device-tests/` are done. The page says so in a banner.

## Run it

```
python -I brushes/pipeline/app_server.py            # or add --no-browser
```

It prints `Open http://localhost:8719/#t=<token>`. Open that exact line: the
token is in the fragment, is read into memory by `js/api.js`, and is sent as
`X-ROSW-Token`. It is never stored. The server walks `app/` when it starts, so
restart it after adding a file (or run it with `--dev`).

The self-test is `selftest.html`, with the same fragment
(`http://localhost:8719/selftest.html#t=<token>`; the app header links to it).
It prints PASS / FAIL / SKIP per check, sets the title to `selftest: PASS n/n`,
and leaves the results in `window.__selftest`. It reads the real library and
writes nothing. The 403/404/400/415/422 "Failed to load resource" lines in the
browser console during a run are the deliberate sad-path requests; the self-test
counts only `console.error` calls and uncaught errors made by the page's code.

## File map

| File | Role |
|---|---|
| `index.html`, `styles.css` | the shell (two tabs, honest-status banner) and the one stylesheet (light/dark, 16px gutters, 44px targets) |
| `selftest.html`, `js/selftest.js`, `js/pure-tests.js` | the self-test; `pure-tests.js` holds the DOM-free checks |
| `js/main.js` | boot: token, schema, status, tabs |
| `js/api.js` | the server client: token, fetch wrappers, F10 error shape, every endpoint the app uses |
| `js/schema.js` | **pure**: `silica_keys.json` (F4) to what the panels need: layout, widget kinds, availability by era, curves, advisory validation |
| `js/state.js` | **pure**: the brush as the opened original plus a patch of changed keys; undo, redo, reset, dirty |
| `js/patch.js` | **pure**: the patch envelope (F3), the diff, `shorten` |
| `js/b64.js` | base64, sha256, PNG header facts |
| `js/dom.js`, `js/ui.js` | `el()` (the only DOM builder; no HTML strings), toast, confirm dialog, clipboard, download |
| `js/panels.js`, `js/widgets.js`, `js/curve.js` | the schema-driven settings tabs, one widget per `ui` kind, the curve editor |
| `js/textures.js` | shape, grain and thumbnail: show, replace, generate, invert |
| `js/opener.js` | open from the library, from a dropped file (a set shows its brush list), or a new brush |
| `js/patchbox.js` | paste a patch from Claude, check it with the server, review the diff, apply; copy your patch |
| `js/exporter.js` | build the export request, run it (dry run, then the real call), save, show the report (`renderExportResult`); the set basket; `.gbr`, kit and app-source exports |
| `js/designer.js` | lays the Designer tab out around one doc |
| `js/library.js`, `js/library/*.js`, `library.css` | the Library tab (3c): `library.js` (query, filters, results, mode), `library/state.js` (**pure** filter-chip state and wording), `card.js` (card and lazy preview), `facets.js` (chip panel), `drawer.js` (detail and Similar), `sets.js` (Sets browser), `basket.js` (the set basket dialog); see "Library, AI assist, extra exports" below |
| `js/ai.js`, `js/ai/prompt.js`, `js/ai/nudges.js` | the AI tab (3c): `ai.js` is the tab, `prompt.js` (**pure**) builds the request for Claude and finds the patch in a reply, `nudges.js` (**pure**) are the offline preset suggestions |
| `js/kit.js`, `js/kit-build.js`, `js/schema-load.js` | the extra exports (3c): `kit.js` (**pure**) recipe text, ink / mask pixel math, zip directory reader, what each format is for; `kit-build.js` turns the shape and grain into the kit's PNGs in the browser; `schema-load.js` loads the schema once for labels |
| `js/selftest-library.js` | the 3c checks (Library, AI, `.gbr`, kit, source zip), run by one line at the end of `selftest.js`; `libraryPureTests(schema)` holds the DOM-free ones |
| `js/engine.js` | the stroke preview (3b): `createEngine`, `describeSupport`, `pureEngineTests`; see Engine below |
| `js/engine/*.js` | the engine's modules: pure (`rng`, `curves`, `model`, `path`, `stamps`, `mips`, `standins`, `raster`, `render`, `support`, `tests`) and DOM (`assets`, `paint`, `controls`, `input`, `notes`, `opts`, `browser-checks`) |
| `js/generators/shape.js`, `grain.js` | the old designer's procedural shapes and grains, kept (LF line endings) to generate a texture |

## How a brush is edited

`js/state.js` keeps the settings exactly as the server decoded them (frozen) and
a patch of the keys the user changed. A widget calls `doc.set()` only on user
input; opening or redrawing a brush edits nothing. Export sends only the patch
(`changes`), the replaced textures and the thumbnail choice; the server patches
the original archive (F3 "Export"). A brush nobody edited exports as its source
archive, byte for byte: the self-test checks it (dry run says every member is
`verbatim`, the saved bytes match `X-ROSW-Export`'s sha256, and the exported
file decodes to the same `archive_sha256` and settings).

Library brushes export with `base: {library_id}`; an opened file or a new brush
exports with the members the server sent back. After an export the panel shows
the command to check the file:
`python -I brushes/pipeline/brush_file.py inspect <file>`.

## The seams for later phases

**Stroke engine (3b): `js/engine.js`.** The seam is
`createEngine(canvas) -> { render(params, opts), setBadges(map), dispose() }`
(see the comment at the top of the file and the Engine section below);
`designer.js` calls `render` once per animation frame per burst of edits.

**Library tab, AI assist, extra exports (3c): done, see the next section.** The
seams stay as they were: `mountLibrary(container, ctx)` with `ctx = {api,
openInDesigner(id), addToSet(id, name), toast, basket}` (`basket` is new and
optional; mount point `#library-mount`), `registerGroupPanel('ai', ...)` in
`panels.js` (now `renderAiTab` from `ai.js`, mount `#ai-mount`), and
`exportRequest` / `runExport` taking `extra` (`spacing`, `files`) for `gbr` and `kit`.

## Library, AI assist, extra exports (3c)

**Library tab.** A query box (GET `/api/search`, 300 ms debounce, stale answers
dropped), facet chips from GET `/api/facets` (the enum and boolean facets as toggle
buttons, a few primary ones open and the rest under "More filters", number facets
as from/to fields, the built-in `library` and `tagged` filters), tag chips from the
closed vocabulary, active-filter chips with "Clear all", a result grid or list
(the layout is remembered), and "How these are ordered" in words from the
envelope's `ranking`. Several values of one facet are an OR, different facets are
an AND (F9). Facet counts are for the filters only, not for the words (the facets
route takes no query). **Tags:** the chips say how many brushes are tagged and
dim the ones with no brush; with 0 of 990 tagged they say so and match nothing.
Cards show Procreate's own stroke thumbnail (fetched with the token, lazily, as the
card nears the screen); a card whose preview is `rendered-approx` says so. The
detail drawer (a `<dialog>`) shows names, library and pack, home set and
position, era and family, the dual brush, the sets it lives in (click to open the
set), tags and the visual description (or "not tagged yet"), the measured facets
and the words the search sees, shape and grain source, and the vault note path
and lines. **Similar**: GET `/api/brush/<id>/similar`; with "Other sets only" on, the
page sends that brush's settings to POST `/api/similar` with `where_not: set=<home
set>` (the GET route has no such switch). **Sets**: the list from `/api/sets`
(filter by name and by user / official) and a set page in set order with "Add all
to the set". **Basket**: "Set basket: N" in the header opens the basket (shared
with the Designer's Export section) with a name and "Export .brushset". Only the
last words and the layout go to localStorage (`rosw.brushes.lib.q`, `.lib.view`,
and the set name); never the filters, never the token.

**AI tab ("Ask Claude").** The Claude route is paste only (F10): there is no
model behind the page and no patch inbox.
1. *Ask Claude*: you type what you want; "Copy request" builds a compact request
   from the open brush: your words, name, era and id, a table of the keys this
   brush holds and may change (key, label, kind and range, value now, one line of
   meaning; unverified keys and blend-mode codes are left out), the rules the server
   enforces, the exact F3 envelope, two valid examples built from this brush's own
   keys, and the reply format. It is about 6 to 7 thousand characters (bound
   14,000) and holds no token. "Show the request" previews it.
2. *Paste the reply*: the whole chat reply goes in; the patch inside it (a fenced
   block or a bare object) is picked out and handed to the Patch box of the
   Designer, which the server checks (`/api/validate-patch`); you see the diff and
   press Apply (one undo step). The hand-over uses `window.__brushApp.designer.patchBox`,
   or the `#patch-paste` box if that is missing.
3. *Quick suggestions (no model)*: softer, harder, grainier, smoother, more or
   less taper, more or less pressure response, wetter, drier, bigger, smaller.
   Each is a short list of moves on keys the brush holds (`js/ai/nudges.js`),
   clamped to the schema's limits, at a gentle, normal or strong size; the result is
   checked by the server and shown as a diff, and Apply is one undo step. They are
   fixed rules, not predictions: a brush of an era that lacks the keys gets "nothing
   to change" and the reason.
4. *Ollama*: **not available from this page.** The old designer called a local
   Ollama directly. The F10 CSP would let the page connect to `http://localhost:*`,
   but this build does not, on purpose: the page talks only to its own server, and
   the server has no route that forwards to Ollama. A future proxy would need: a
   route such as `POST /api/assist` in `app_server.py` that forwards a prompt to an
   Ollama on this machine; a loopback-only target and a model allow-list fixed at
   server start; size caps, a time limit and one request at a time; the same token
   check as every route and no logging of the token or the prompt; and the reply
   would still go through the Patch box and the server's validation. The tab lists
   the same points.

**Extra exports** (Designer, Export section; every result shows the file name,
size, sha256 (checked against `X-ROSW-Export`), what the format is for, what it
holds (the server's member list) and warnings). What each is for is in
`js/kit.js` `FORMAT_NOTES`.
- **`.gbr`** (`format: 'gbr'`, `spacing` 1 to 1000, default 10): the shape as a GIMP
  brush tip, from an embedded or replaced shape image. A bundled shape is refused by
  the server (the image ships inside Procreate); the panel says what to do.
- **Universal Kit** (`format: 'kit'`): the server only zips the `files` the page
  supplies (`gimp/*.gbr`, `ink/*.png`, `mask/*.png`, `stroke-preview.png`,
  `brush-recipe.md`) and can add the `.brush`. The page makes them: the `.gbr` from a
  gbr export; `ink/` (black on transparent, alpha is coverage) and `mask/` (grey,
  white is paint) from the shape and, when it is an image, the grain, honouring the
  Inverted switches, at most 1024 px; `stroke-preview.png` is the thumbnail stored in
  the brush (Procreate's picture, not a render by this app); the recipe lists every
  setting with its label and says nothing in the kit has been tried in other apps.
  What cannot be made (a bundled grain, no thumbnail) is left out and listed.
- **App source** (`GET /api/app-source.zip`): the files this page is made of, no
  brush and no token; shown with size, sha256 and its entry list.
- Not offered, because F10 has no such format: `.abr`, `.afbrushes`, and a zip of a
  brush's own source files. Nothing here claims Procreate (or any app) opens an export.

**Self-test (3c).** `js/selftest-library.js`: the pure checks of every 3c module,
the Library driven by clicks (search "watercolour wash", a facet chip narrows and
matches a direct API call, a number range, the empty state, the drawer and
Similar with "Other sets only", Sets, the basket exporting a `.brushset` that
reads back, preferences hold no token, a slow and a failing server), the AI tab
(request for Brush Pen has the envelope, fits the bound and holds no token; a pasted
reply reaches the Patch box; a suggestion applies as one undo step; every preset
on brushes of four eras is accepted by `/api/validate-patch`), `.gbr` bytes
(GIMP v2 header, size, spacing), the kit's entries and ink / mask PNG and recipe,
and the source zip. It puts the saved words and layout back as it found them.

## Not done in 3a (on purpose)

(3a list; the Library, facets, similar, `.gbr`, kit and AI route are done in 3c;
Ollama stays out.) No presets
store, no bundled-texture stand-in images (`schema/bundled_textures.json` does
not exist; a bundled shape or grain is shown as "ships inside Procreate", never
an invented image), no editing of the secondary (dual) brush's textures, no
roll-parameter editor (read only), no editing of `color`, `creationDate`.

## Engine

`js/engine.js` draws a **stroke preview** next to the settings. **It is an
approximation of Procreate and says so under the canvas** ("Preview is an
approximation of Procreate", with a collapsed ledger of what is proven and what
is guessed). It is not Procreate's renderer, it never claims to match it, and a
picture that looks right here proves nothing about how Procreate draws.

**How it works.** The settings (`doc.effective('main')`) become a *stamp list*
(`js/engine/stamps.js`, pure): a synthetic stroke (`path.js`: Procreate's own
thumbnail S-curve, a line, a scribble, a tap, or one you draw on the preview with
a mouse, a finger or an Apple Pencil) is walked at the brush's spacing; each
stamp gets a size, opacity, angle, flips and position from simulated pressure,
speed and tilt, the pressure curves, taper, jitter, scatter, rotation and fall
off. `raster.js` draws the stamps in software (typed arrays, no canvas) through
the shape mask and the grain; `paint.js` turns the coverage into pixels.
Determinism: every stamp has its own seeded generator (`rng.js`), so the same
settings and seed give the same pixels; the seed is shown and changeable. While a
slider moves the preview draws a half-resolution draft and settles to the full
render 170 ms after the last change; a full render is time-sliced so the page is
never blocked for long. The canvas is at most 1000 device pixels across. Measured
on the dev laptop (a 600 px canvas, full quality): 10 ms for a pen-like brush,
10 to 28 ms for grainy or big-stamp brushes; a 960 px canvas costs 16 to 66 ms,
which is why a slider drag draws a draft. The self-test logs the timing and does
not assert it.

**Controls** ("Preview options"): stroke (Auto shows one stamp for a "stamp
preview" brush), input (Apple Pencil uses the pencil taper set when the brush has
one, Finger the touch set and no pressure), pressure (light, medium, heavy),
simulated tilt, background (dark with white ink like Procreate's thumbnails,
white, paper), size from (preview size or paint size), seed, "Show Procreate's own
thumbnail below" (its stored thumbnail drawn in the same ink, for comparing), and a
taller preview. They are remembered per browser.

**Badges.** `describeSupport(key)` returns `honoured`, `approximate` or `ignored`
for each key, from `js/engine/support.js`. The self-test proves both ways that it
tells the truth: every key listed there changes the picture, and every other key
of the schema that can be set generically does not. The panels read
`row.preview`; `designer.js` calls `applyEngineSupport(schema)` once so the badge
shows the engine's answer (only in memory; `schema/silica_keys.json` is not
edited, and `supportDifferences(schema)` lists where the two disagree).
`honoured` is used for one rule only (shape polarity, proven on 391 shapes);
everything else is `approximate`.

**Proven, measured, inferred, guessed** (the same statuses as the design notes and
`critique-fidelity.md`; the constants live in `js/engine/model.js`
`CALIBRATION`):

| Status | What |
|---|---|
| proven | shape polarity `shapeInverted ? 255 - v : v` (391 shapes) |
| measured | the S-curve path of Procreate's thumbnails (24 thumbnails); the single-stamp size law `256 x (minSize + (maxSize - minSize) x previewSize)` (143 legacy stamps, within 3 to 25 percent; it also reproduced a stamp brush's own thumbnail by eye); the thickness of a stroke thumbnail along its length, a hump `sin(pi u)^1.4` (36 pressure-sensitive library thumbnails) |
| inferred | what each key means (from its name and observed range): taper, jitter, scatter, rotation, falloff, flow, the pressure and speed laws, the curve shape between points, the pencil taper set, `renderingMaxTransfer` as max accumulation |
| guess | every constant: spacing factor, jitter radius, taper length, falloff length, tilt gain, grain unit, the stroke size (`90 x maxSize^0.3`, a log-regression fit to 329 library stroke thumbnails with a residual of a factor of two: a thumbnail stroke hardly follows `previewSize` or `paintSize`), reading the thickness hump as pressure, the simulated speed, flow normalisation at fine spacing |
| stand-in | a bundled shape or grain has no image in the app (it ships inside Procreate): the preview draws a generated stand-in, labels it on the canvas and in the status line, and never shows it as the real texture. A blank grain and a blank shape are exact. |
| not drawn | wet mix, colour dynamics, blend modes, dual brushes, wet and burnt edges, barrel roll, hover, materials, stabilisation, shape count, grain brightness and contrast, per-key pressure curves of jitter, and every key a badge calls ignored |

Differences from `design-app.md` section 3: `shapeRandomise` rotates each stamp at
random (the design says once per stroke); the stroke size uses a fit to library
thumbnails (`90 x maxSize^0.3`) rather than `sqrt(previewSize)`, and only a single
stamp (Tap, or a stamp-preview brush on Auto) uses the thumbnail law; `shapeRoundness`,
`shapeAngle` and the flip jitters are drawn (the schema called them ignored);
`dynamicsTiltAngle` is not (the schema called it approximate); there is no
`calibrate.html` yet, so every constant is still a placeholder.

**Tests.** `pureEngineTests(schemaIndex)` (also run by `selftest.js`) covers the
rng, curves, path, spacing count, taper endpoints, jitter, rotation, mask polarity,
determinism, "changed key changes pixels / ignored key does not" and a no-exception
render of every era's key set. `js/engine/browser-checks.js` renders real library
brushes of every era and checks determinism, polarity of an embedded shape and the
layouts.
