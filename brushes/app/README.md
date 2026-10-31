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
| `js/exporter.js` | build the export request, run it (dry run, then the real call), save, show the report; the set basket |
| `js/designer.js` | lays the Designer tab out around one doc |
| `js/library.js` | the Library tab (minimal; 3c replaces it) |
| `js/engine.js` | the stroke-preview seam (3b replaces its body) |
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

**Stroke engine (3b): `js/engine.js`.** Replace the body of

```js
createEngine(canvas) -> { render(params, opts) -> Promise<...>, setBadges(map), dispose() }
```

`params` is the effective settings (`doc.effective('main')`); `opts` carries the
size, era, name, thumbnail URL and the shape and grain image URLs; the full
contract is the comment at the top of the file. `setBadges` receives the
`preview` column of the schema (`honoured` / `approx` / `ignored`), which the
panels already show as a badge on every row. `designer.js` calls `render` on
every doc change (one `requestAnimationFrame` per burst); nothing else needs to
change. Draw white-on-dark: Procreate's thumbnails are white on transparent.

**Library tab, AI assist, extra exports (3c).**
- `js/library.js` exports `mountLibrary(container, ctx)`; `ctx` is
  `{api, openInDesigner(id), addToSet(id, name), toast}`. Rewrite the file
  behind that signature (facets, sets, similar, a drawer). The mount point is
  `#library-mount`.
- `js/panels.js` exports `registerGroupPanel(groupId, {mode, render})`. The `ai`
  tab is a placeholder (`mode: 'replace'`, mount `#ai-mount`); `about` appends
  the brush facts and the unrecognised keys. A 3c module registers its own.
- `js/exporter.js`: `exportRequest({format, ...})` and `runExport()` are
  format-agnostic; `gbr` and `kit` are another `format` plus `spacing` / `files`
  (F10). `brushSpec(doc)` is one `brushes[]` entry. The set basket
  (`createBasket`) is shared by the Library tab (`addToSet`) and the export
  panel.

## Not done in 3a (on purpose)

No stroke engine (a placeholder shows Procreate's own thumbnail), no `.gbr` or
kit export, no Ollama assist, no facets or similar-brush search, no presets
store, no bundled-texture stand-in images (`schema/bundled_textures.json` does
not exist; a bundled shape or grain is shown as "ships inside Procreate", never
an invented image), no editing of the secondary (dual) brush's textures, no
roll-parameter editor (read only), no editing of `color`, `creationDate`.
