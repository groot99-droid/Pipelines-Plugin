# Brush designer

Subsystem `brush-designer` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.9 · 34 entries · 21 corrections made to the first reading.

## Summary

tools/brush-designer/ is a browser-only single-page app titled "Procreate Brush Designer". It has no build step, no CLI and no server of its own. It holds a 52-parameter brush state, generates a 512x512 shape texture and a 1024x1024 grain texture on canvas, and previews strokes on a sheet you can draw on. It has five exports, and each one reaches disk only as a browser download: Procreate .brush, Procreate .brushset (the UI only ever packs the current brush), GIMP/Krita .gbr, a "Universal Kit" zip (ink/mask PNGs, a .gbr, stroke-preview.png and a markdown recipe for Photoshop, Affinity, Clip Studio, Krita, GIMP and others), and a "Download Source" zip.

Reading export/PlistEncoder.js shows a serious problem that was not run to confirm. For arrays and dicts, addObject reserves an index before encoding the children but pushes the container after them. Every container's object reference (including the trailer's root index) therefore points at the wrong object. The Brush.archive and brushset.plist bytes are most likely not valid bplists.

The AI Assist tab talks to local Ollama (default http://localhost:11434). It sends GET /api/tags, then a non-streaming POST /api/generate with model llama3.1:8b (tier sm) or mistral-nemo:12b (tier md), then POST /api/generate {keep_alive:0} to unload the model. The prompt carries the current values of the 43 exportable brush* tunables and asks for a JSON patch {changes, summary}. Every key is validated and clamped, and the result is applied as one undoable step. Name, author, notes, shapeSource, grainSource and the pressure curves are rejected.

Presets live in localStorage (brushPresets) and IndexedDB (ProcreateBrushDesigner v1 / presetImages). Five built-ins are seeded once, users can add their own, and there is no delete UI. The only code CDN dependency is fflate@0.8.2 (UMD global) from cdn.jsdelivr.net; styles.css also @imports JetBrains Mono from Google Fonts. The app needs an HTTP origin: .claude/launch.json 'hub-static-server' (python3 -m http.server 8347) or tools/launcher/Start-Hub.ps1 (loopback, ports 8765-8774). The hub's Brushes tab embeds it through a same-origin iframe (../tools/brush-designer/index.html) and nothing else; the only shared state is the localStorage keys hub:endpoint and hub:tier.

Module map (exports -> class):
- DOM-free (no browser API references):
  - editor/BrushState.js: DEFAULT_BRUSH_STATE, BRUSH_PROPERTY_RANGES, BLENDING_MODES, BrushState, default BrushState.
  - editor/HistoryManager.js: HistoryManager.
  - export/PlistEncoder.js: PlistEncoder, encodePlist.
  - export/BrushArchive.js: BrushArchive.
- Near-core, fetch plus localStorage only in its getters/setters: ai/OllamaAssist.js exports the OllamaAssist object.
- Needs a Canvas 2D implementation (each calls document.createElement('canvas')):
  - generators/ShapeGenerator.js: ShapeGenerators, generateShape, getShapeGeneratorNames.
  - generators/GrainGenerator.js: GrainGenerators, generateGrain, getGrainGeneratorNames.
  - export/GbrEncoder.js: GbrEncoder.
- Canvas plus toBlob plus the global fflate (and URL/anchor for the download):
  - export/BrushExporter.js: BrushExporter.
  - export/UniversalKitExporter.js: UniversalKitExporter.
- Browser-bound UI:
  - app.js: default ProcreateBrushDesigner, which also sets window.app.
  - editor/PresetLibrary.js: localStorage, IndexedDB and canvas.
  - panels/PanelComponents.js: BasePanel plus 10 panel classes; the default export is an object of the 10.
  - panels/AIAssistPanel.js.
  - preview/StrokeRenderer.js.
  - preview/StrokeInput.js.
  - ui/Slider.js, ui/CurveEditor.js, ui/Section.js (Section, createSectionToolbar), ui/Modal.js, ui/Toast.js (Toast, getToast).

Nothing routes to it. DECISIONS.md D2 specifies a headless adapter plus skills/brush_designer.skill.md; neither exists. skills/ holds 9 files, none of them brush_designer. Unimplemented or stubbed: .brush/.brushset import, the Color Dynamics tab, custom texture upload (CSS only), tilt, and any way to change the generator seed. README calls it '~4,000 lines'; the files are about 5,700 lines of JS and HTML, or 7,129 counting styles.css. Git working-tree state (untracked or modified files) could not be checked with the allowed tools. The root wet-stipple-brush.md exists and is empty.

## Tools

### Procreate Brush Designer (web app shell)

`web-app` · status `runs-today`

Paths: `tools/brush-designer/index.html`, `tools/brush-designer/app.js`, `tools/brush-designer/styles.css`

Manual browser tool for editing a 52-parameter brush plus generated shape and grain textures. You test the brush on a drawable preview sheet and download it in Procreate, GIMP/Krita or multi-app formats.

**Entry points**

- `python3 -m http.server 8347 (.claude/launch.json configuration 'hub-static-server'), then open http://localhost:8347/tools/brush-designer/index.html`
  - does: Serves the repo over HTTP and loads the app. README: 'open index.html from a static server' / 'Needs an HTTP origin, not file://'.
  - changes: nothing on disk
- `.\Start-Hub.ps1 [-Port <1024-65535, default 8765>] [-PortSearch <1-50, default 10>] [-NoBrowser] (run from tools\launcher), then http://localhost:<port>/tools/brush-designer/index.html`
  - does: Starts or reuses python -m http.server <port> --bind 127.0.0.1 --directory <repo root> and opens /hub/. The designer sits on the same origin.
  - changes: starts a hidden background python process
- `window.app (global ProcreateBrushDesigner instance, created on DOMContentLoaded at app.js line 674)`
  - does: In-page handle to brushState, history, presetLibrary, strokeRenderer, strokeInput and panels. It also exposes the methods exportBrush, exportBrushset, exportGbr, exportUniversalKit, exportSource, saveCurrentAsPreset, loadPreset, importBrush (stub), applyAIPatch, undo, redo, renderPreview and switchPanel.
  - changes: in-page state; the export methods trigger browser downloads
- `Keyboard (document-level keydown): Ctrl/Cmd+Z undo; Ctrl/Cmd+Y redo; the code also has a Ctrl/Cmd+Shift+Z redo branch inside the e.key === 'z' check`
  - does: Brush-state undo/redo (50 steps). The listener has no target check, so it also catches Ctrl+Z inside text fields (brush name, notes, AI instruction) and calls preventDefault.
  - changes: in-memory state

**Inputs**

- Brush name (#brushName header input; applied on 'change'; creates no history entry)
- Slider, toggle, dropdown and generator-button edits from the 10 parameter tabs
- Pointer strokes on #previewCanvas
- Natural-language instruction in the AI Assist tab
- Preset clicks and Save Preset prompts

**Outputs**

- <name>.brush
- <name>.brushset
- <name>.gbr
- <name>-universal-kit.zip, where <name> is state.name with every [^a-zA-Z0-9] replaced by _
- procreate-brush-designer-source.zip (fixed name)

**Reads**

- localStorage: brushPresets, brushDesigner.sections.v1, hub:endpoint, hub:tier
- IndexedDB: database ProcreateBrushDesigner v1, store presetImages
- Its own source files via relative fetch() (Download Source only)

**Writes**

- localStorage: brushPresets, brushDesigner.sections.v1, hub:endpoint, hub:tier
- IndexedDB ProcreateBrushDesigner/presetImages
- Browser download location (anchor-click download; the browser chooses the folder)

**Depends on**

- Modern browser with ES modules, Canvas 2D, Blob/URL.createObjectURL, IndexedDB, localStorage and Pointer Events
- fflate@0.8.2 UMD from https://cdn.jsdelivr.net/npm/fflate@0.8.2/umd/index.js (global `fflate`; the only code CDN)
- Google Fonts @import for JetBrains Mono (styles.css line 1)
- A static HTTP server
- Optional: Ollama at http://localhost:11434 for AI Assist

**Gates and checkpoints**

- No auth, compute-gate or approval checks; state/compute_gate.json is never read.
- Reset to defaults requires Modal.confirm ('Reset brush').
- Save preset requires a name from Modal.prompt; Cancel aborts.
- Every export is wrapped in try/catch and reports errors as toasts.
- Panel edits are pushed to history after a 500 ms debounce, labelled with the last key changed. The preview re-renders after a 16 ms debounce.

**Invoked by**

- A human in a browser
- hub/index.html Brushes tab (iframe #brushFrame)
- The 'Open in a new tab ↗' link in hub/index.html

**Invokes**

- editor/BrushState.js
- editor/HistoryManager.js
- editor/PresetLibrary.js
- preview/StrokeRenderer.js
- preview/StrokeInput.js
- export/BrushExporter.js
- export/GbrEncoder.js
- export/UniversalKitExporter.js
- generators/ShapeGenerator.js
- generators/GrainGenerator.js
- panels/PanelComponents.js
- panels/AIAssistPanel.js
- ui/Toast.js
- ui/Modal.js

**Notes**

index.html contains:
- A header: name input, Undo (title 'Undo (Ctrl+Z)'), Redo (title 'Redo (Ctrl+Y)'), and an Export ▾ menu with 5 items.
- 11 sidebar tabs: AI Assist, Stroke Path (default), Taper, Shape, Grain, Dynamics, Pencil, Wet Mix, Color Dynamics, Rendering, About This Brush.
- The preview stage: #previewCanvas, #brushCursor, Light/Medium/Heavy/All sample buttons, Undo stroke, Clear, and the #previewReadout.
- A 512 #shapeCanvas and a 1024 #grainCanvas.
- The presets sidebar: + save, ↑ import, and a hidden file input accepting .brush,.brushset.
- A toast container.

styles.css is 1,424 lines and styles the chrome only. Its section headers: tokens, reset, layout, header, buttons, sidebar, panel, preview, textures, presets, slider, curve editor, 'Image Uploader' (no JS uses .image-uploader), generator select, toggle, dropdown, toasts, spinner, empty state, export menu, responsive, focus, modal, AI panel, sections, spec table, nib cursor. DECISIONS.md says the artwork colours (#F5F0E8 paper, white/grey generator fills) were deliberately left unthemed.

State-sync gaps, from reading the code:
- On undo, redo, AI patch or preset load, onStateChange calls updateSliders() on the open panel only. Toggles, the blend dropdown, generator buttons, author/notes fields and the curve editors keep showing stale values until the panel is re-rendered.
- Shape and grain canvases are not in history. Undo and redo can change shapeSource/grainSource without regenerating the canvases. AI patches cannot touch those keys.
- Generator picks, pressure-curve edits, header-name edits and author/notes edits call brushState.set without onPanelChange, so they create no history entry of their own.
- After an undo, the toast shows the label of the entry now on top, not the action that was undone.

Keyboard: whether Ctrl+Shift+Z reaches the redo branch depends on the browser reporting e.key as lowercase 'z' while Shift is held (see open questions).

README calls it '~4,000 lines' and 'the piece that most closely resembles a finished tool'. The Read line counts give 5,705 JS/HTML lines. README line 212 records tools/brush-designer/ as coming from the 'Claude-Code' source repo. Git working-tree claims (modified or untracked files) could not be verified: .git/ is off-limits and only Read/Glob/Grep are allowed.

### BrushState (parameter model)

`library` · status `runs-today`

Paths: `tools/brush-designer/editor/BrushState.js`

The single source of truth for brush configuration: defaults, numeric ranges, the blend-mode table, and an observable state object.

**Entry points**

- `import { BrushState, DEFAULT_BRUSH_STATE, BRUSH_PROPERTY_RANGES, BLENDING_MODES } from './editor/BrushState.js'`
  - does: Exports the state class and the schema tables (default export: BrushState)
  - changes: nothing
- `new BrushState(initialState?) ; .get(key?) ; .set(key, value) ; .setState(partial) ; .reset() ; .subscribe(cb) -> unsubscribe ; BrushState.getRange(prop) ; BrushState.clamp(prop, value) ; BrushState.format(prop, value) ; .toJSON() ; .fromJSON(json) ; .toExportFormat() ; .createBrushObject() ; .createClassDescriptor() ; .generateUUID()`
  - does: Creates, reads, patches, resets (keeping the identifier), clamps and formats values, and serialises. Listeners receive (state, changedKeys, oldState). A UUID v4 (Math.random) is generated when no identifier is supplied.
  - changes: in-memory state only

**Inputs**

- Partial state objects

**Outputs**

- State snapshots (shallow copies)
- JSON string
- NSKeyedArchiver-shaped object from toExportFormat() (unused)

**Depends on**

- None. Pure ES module with zero browser references (Math.random only), so it should import under Node as-is (not tested).

**Gates and checkpoints**

- setState and set do no validation or clamping. Values are clamped only by OllamaAssist.validatePatch and by the Slider bounds.

**Invoked by**

- app.js
- panels/PanelComponents.js (BLENDING_MODES)
- panels/AIAssistPanel.js (BRUSH_PROPERTY_RANGES)
- ai/OllamaAssist.js (BRUSH_PROPERTY_RANGES, BLENDING_MODES)
- export/UniversalKitExporter.js (BRUSH_PROPERTY_RANGES, BLENDING_MODES)

**Notes**

DEFAULT_BRUSH_STATE holds 52 parameters, matching README's '52 parameters'. Groups (key = default, [range]):
- Metadata (5): name='Untitled Brush', authorName='', notes='', identifier='' (replaced by a UUID in the constructor), version=1.
- Stroke Path (9): brushSpacing=0.03 [0-5.0]; brushSpacingJitter, brushStreamline=0.15, brushStreamlinePressure, brushStabilization, brushMotionFiltering, brushJitterX, brushJitterY, brushFallOff (the rest default 0) [0-1].
- Shape (8): brushShapeScatter=0 [0-2], brushShapeRotation=0 [0-6.283 rad], brushShapeCount=1 [1-16 step 1], brushShapeCountJitter=0 [0-1], brushShapeRandomized=false, brushAzimuth=false, brushFlipX=false, brushFlipY=false.
- Grain (8): brushGrainScale=1.0 [0-2], brushGrainRotation=0 [0-6.283], brushGrainDepth=0.7, brushGrainDepthMin=0, brushGrainDepthJitter=0, brushGrainOffsetJitter=0 [0-1], brushGrainMoving=false, brushGrainZoom=false.
- Dynamics (5): brushSizeMaximum=1.0, brushSizeMinimum=0, brushOpacityMaximum=1.0, brushOpacityMinimum=0, brushBleedAmount=0 [0-1].
- Taper (5): brushTaperSizeStart=0, brushTaperSizeEnd=0, brushTaperTip=0.5, brushTaperOpacity=0 [0-1], brushTaperLinked=true.
- Wet Mix (7): brushWetDilution, brushWetCharge, brushWetPull, brushWetAttack, brushWetBleed (all 0, [0-1]), brushWetEdge=false, brushWetBurn=false.
- Rendering (1): brushBlendingMode=0, integer id 0-15 over 16 BLENDING_MODES (Normal, Multiply, Screen, Overlay, Darken, Lighten, Color Dodge, Color Burn, Soft Light, Hard Light, Difference, Exclusion, Hue, Saturation, Color, Luminosity).
- Pressure curves (2): brushPressureSizeResponse=null and brushPressureOpacityResponse=null. The Pencil tab sets each to a 64-byte Uint8Array view of a Float64Array of 8 bezier coordinates.
- Sources (2): shapeSource='Soft Circle', grainSource='Paper Fine'. A comment says "or 'upload' for custom", but no upload exists.

By type: 33 numeric keys in BRUSH_PROPERTY_RANGES, 9 booleans, 1 enum, 2 binary curves, 2 generator names, 5 metadata. The 43 brush* tunables (33 numeric, 9 boolean, blend mode) are both the set written to Brush.archive and the set the AI may change. toExportFormat/createBrushObject duplicate BrushArchive's structure without type coercion and are never called; toJSON/fromJSON are also never called (grep-verified).

### HistoryManager (undo/redo)

`library` · status `runs-today`

Paths: `tools/brush-designer/editor/HistoryManager.js`

Keeps a 50-step undo/redo stack of BrushState snapshots.

**Entry points**

- `new HistoryManager(50) ; .push(state, action) ; .undo() ; .redo() ; .canUndo() ; .canRedo() ; .getLastAction() ; .getNextAction() ; .getUndoSize() ; .getRedoSize() ; .clear()`
  - does: push deep-clones the state with JSON.parse(JSON.stringify()) and clears the redo stack. undo moves the top entry to redo and returns the new top's snapshot, or null. redo returns the moved entry's snapshot.
  - changes: in-memory stacks

**Inputs**

- State snapshots plus action labels

**Outputs**

- Restored state snapshots

**Depends on**

- None (DOM-free)

**Gates and checkpoints**

- Stack capped at 50 (the oldest entry is shifted off); a new push clears redo

**Invoked by**

- app.js

**Notes**

Snapshots cover BrushState only, not the shape/grain canvases. Because cloning goes through JSON, a Uint8Array pressure curve would come back from undo/redo as a plain index-keyed object. That follows from the code; it was not verified by running.

### PresetLibrary (+ Presets sidebar)

`library` · status `runs-today`

Paths: `tools/brush-designer/editor/PresetLibrary.js`, `tools/brush-designer/app.js`

Stores and loads named brush presets. Settings and a thumbnail go to localStorage; shape/grain PNG data URLs go to IndexedDB.

**Entry points**

- `UI: Presets sidebar '+' (#savePresetBtn) -> Modal.prompt 'Preset name' (default = brush name) -> Modal.prompt 'Category' (default 'Custom') -> presetLibrary.addPreset(name, category, brushState, shapeCanvas, grainCanvas)`
  - does: Saves the current brush as a preset with a 128px thumbnail. settings = brushState.get(), the full state.
  - changes: localStorage brushPresets; IndexedDB ProcreateBrushDesigner/presetImages
- `UI: click a preset card -> app.loadPreset(preset)`
  - does: Loads the stored shape/grain PNGs into the canvases, runs brushState.setState(preset.settings), re-textures the preview and pushes a 'Loaded preset: <name>' history entry
  - changes: in-memory state and canvases
- `presetLibrary.addBuiltInPresets() (awaited from app.init)`
  - does: Seeds 5 built-in presets. Seeding is skipped if any stored preset shares a name with any built-in.
  - changes: localStorage and IndexedDB
- `PresetLibrary API: getPreset(id), getAllPresets(), getPresetsByCategory(c), getCategories(), loadImageData(id), saveImageData(id, shape, grain), updatePreset(id, updates), deletePreset(id), importBrush(file)`
  - does: CRUD helpers. updatePreset, deletePreset, getPreset and getAllPresets have no caller. importBrush returns null.
  - changes: localStorage/IndexedDB (update/delete)

**Inputs**

- BrushState
- shape canvas
- grain canvas
- preset name and category

**Outputs**

- Preset records {id, name, category, tags, thumbnail, createdAt, settings}

**Reads**

- localStorage brushPresets
- IndexedDB ProcreateBrushDesigner (v1), store presetImages {id, shapeData, grainData, updatedAt} (keyPath id)

**Writes**

- localStorage brushPresets
- IndexedDB presetImages

**Depends on**

- Browser localStorage, IndexedDB and canvas (document.createElement, drawImage, toDataURL)
- generators/ShapeGenerator.js and generators/GrainGenerator.js (dynamic import, built-ins only)

**Gates and checkpoints**

- The name prompt must return a non-empty value, otherwise the save is aborted

**Invoked by**

- app.js

**Invokes**

- generators/ShapeGenerator.js generateShape(name, 512)
- generators/GrainGenerator.js generateGrain(name, 1024)

**Notes**

Built-ins (name / category / settings):
- Classic Pencil / Drawing: spacing 0.03, streamline 0.15, sizeMax 0.5, grainDepth 0.7, Soft Circle + Paper Fine.
- Ink Pen / Inking: spacing 0.01, streamline 0.7, sizeMax 0.8, taperStart 0.25, taperEnd 0.35, Hard Circle + Flat.
- Watercolor Wash / Painting: spacing 0.08, wetDilution 0.5, wetCharge 0.7, grainMoving true, wetEdge true, Ink Blot + Cold Press.
- Dry Brush / Texture: spacing 0.05, scatter 0.3, jitterX/Y 0.2, Bristle + Canvas.
- Stamp Texture / Texture: spacing 1.2, scatter 0.4, shapeRandomized true, blendingMode 1 (Multiply), Torn Edge + Linen.

Built-in settings are partial, and each also sets identifier = preset id. Loading one does not reset unlisted parameters, and it overwrites the brush UUID with the same id every time. User presets store the full state, so loading one overwrites everything, including name and identifier. Pressure curves in user presets go through JSON and would come back as plain objects (unverified). There is no delete or rename UI. renderPresets injects preset.name and thumbnail into innerHTML without escaping.

### ShapeGenerator

`library` · status `runs-today`

Paths: `tools/brush-designer/generators/ShapeGenerator.js`

Procedurally draws grayscale brush-tip shape textures (white = mark, black = transparent).

**Entry points**

- `generateShape(generatorName, size = 512, seed = 12345) -> HTMLCanvasElement`
  - does: Fills the canvas black, then runs the named generator. An unknown name leaves a black (empty) canvas.
  - changes: nothing
- `getShapeGeneratorNames() ; ShapeGenerators[name](ctx, size, seed) (ShapeGenerators is also the default export)`
  - does: Lists the generator names. The generator functions accept any 2D context.
  - changes: the context passed in

**Inputs**

- generator name
- size
- seed

**Outputs**

- canvas

**Depends on**

- Canvas 2D. The only DOM use is document.createElement('canvas') inside generateShape.

**Invoked by**

- app.js setupCanvases
- panels/PanelComponents.js ShapePanel
- editor/PresetLibrary.js

**Notes**

9 generators: Hard Circle, Soft Circle, Splat, Ink Blot, Bristle, Cross Hatch, Torn Edge, Leaf, Star. Output is deterministic (Park-Miller SeededRandom). Hard Circle, Soft Circle and Leaf ignore the seed. No caller passes a seed, so it is always 12345.

### GrainGenerator

`library` · status `runs-today`

Paths: `tools/brush-designer/generators/GrainGenerator.js`

Procedurally draws grayscale grain (paper/texture) images using Perlin fBm and seeded random strokes.

**Entry points**

- `generateGrain(generatorName, size = 1024, seed = 12345) -> HTMLCanvasElement`
  - does: Runs the named generator. An unknown name falls back to 'Flat'.
  - changes: nothing
- `getGrainGeneratorNames() ; GrainGenerators[name](ctx, size, seed) (GrainGenerators is also the default export)`
  - does: Lists the generator names. The generator functions accept any 2D context.
  - changes: the context passed in

**Inputs**

- generator name
- size
- seed

**Outputs**

- canvas

**Depends on**

- Canvas 2D (createImageData, putImageData, getImageData). The only browser reference is document.createElement('canvas').

**Invoked by**

- app.js setupCanvases
- panels/PanelComponents.js GrainPanel
- editor/PresetLibrary.js

**Notes**

8 generators: Flat, Paper Fine, Paper Rough, Canvas, Cold Press, Linen, Concrete, Noise. Deterministic. No caller passes a seed, so it is always 12345.

### PlistEncoder (bplist00)

`library` · status `partial`

Paths: `tools/brush-designer/export/PlistEncoder.js`

Pure-JS binary property list (bplist00) encoder used for Brush.archive and brushset.plist.

**Entry points**

- `new PlistEncoder().encode(value) -> Uint8Array ; encodePlist(value) (default export PlistEncoder)`
  - does: Encodes booleans, ints, doubles, ASCII/UTF-16 strings, Dates, data (Uint8Array/ArrayBuffer), arrays and dicts. Strings and data are deduplicated.
  - changes: nothing

**Inputs**

- JS value tree

**Outputs**

- bplist00 bytes

**Depends on**

- None (DOM-free; uses TextEncoder, DataView and BigInt)

**Invoked by**

- export/BrushArchive.js
- export/BrushExporter.js createBrushsetPlist

**Notes**

The encoder runs without throwing, but reading the code shows an object-table bug. addObject sets index = objects.length, encodes the children of an array or dict (each pushed to this.objects), and only then pushes the container. So the returned index points at the container's first child, not the container itself. The trailer's root index (0) therefore names the first key string ('$version' for Brush.archive, the first UUID for brushset.plist), and every nested dict or array reference is off. Leaf objects are indexed correctly. Separately, the reference width inside containers is computed from objects.length at encode time, while the trailer uses the final count; this only matters past 255 objects.

There is no bplist UID (0x8X) type, so NSKeyedArchiver references {UID: n} are written as ordinary one-key dicts. A comment records an earlier fix to the 32-byte trailer offsets. encodePlist is never called. Nothing here was run.

### BrushArchive (Brush.archive encoder)

`library` · status `runs-today`

Paths: `tools/brush-designer/export/BrushArchive.js`

Builds the NSKeyedArchiver-shaped MCBrush object from brush state and encodes it as a binary plist, which becomes the Brush.archive entry of a .brush.

**Entry points**

- `BrushArchive.encode(brushStateOrPlainState) -> Uint8Array ; BrushArchive.createBrushObject(state) ; BrushArchive.createClassDescriptor()`
  - does: Builds {$version:100000, $archiver:'NSKeyedArchiver', $top:{root:{UID:1}}, $objects:['$null', brushDict{$class:{UID:2}, ...}, {$classname:'MCBrush', $classes:['MCBrush','NSObject']}]} and runs PlistEncoder
  - changes: nothing

**Inputs**

- BrushState instance (uses .get()) or plain state object

**Outputs**

- Brush.archive bytes

**Depends on**

- export/PlistEncoder.js (DOM-free)

**Gates and checkpoints**

- Type coercion: parseFloat for floats; parseInt for brushShapeCount, brushBlendingMode and brushVersion; !! for booleans; String() for text. Null/undefined values are skipped.

**Invoked by**

- export/BrushExporter.js

**Invokes**

- export/PlistEncoder.js

**Notes**

Writes the 43 brush* tunables, plus brushName (default 'Untitled Brush'), brushAuthorName, brushNotes, brushIdentifier (a new UUID if empty) and brushVersion, plus the pressure-curve values when truthy. The curves are written as-is: a Uint8Array becomes plist data, while a plain object (after an undo or preset round-trip) becomes a dict. shapeSource/grainSource are not written; the textures travel as Shape.png and Grain.png. The object structure is fine, but the bytes inherit PlistEncoder's index bug.

### Export .brush (Procreate)

`library` · status `runs-today`

Paths: `tools/brush-designer/export/BrushExporter.js`, `tools/brush-designer/app.js`

Packages one brush as a Procreate .brush ZIP.

**Entry points**

- `UI: Export ▾ -> 'Export .brush (Procreate)' (data-export="brush") -> app.exportBrush()`
  - does: Builds the file and downloads <sanitized name>.brush
  - changes: browser download
- `await BrushExporter.exportBrush(brushState, shapeCanvas, grainCanvas) -> Blob ; BrushExporter.canvasToGrayscalePNG(canvas, size) ; BrushExporter.canvasToInkAlphaPNG(canvas, size) ; BrushExporter.generateThumbnail(shape, grain, 256) ; BrushExporter.downloadBlob(blob, filename)`
  - does: Builds a ZIP containing Brush.archive (deflate level 6), Shape.png (512 grayscale, stored), Grain.png (1024 grayscale, stored) and QuickLook/Thumbnail.png (256 composite on #F5F0E8, stored), via fflate.zipSync
  - changes: nothing; downloadBlob triggers an anchor-click download

**Inputs**

- BrushState
- shape canvas
- grain canvas

**Outputs**

- application/octet-stream Blob (.brush ZIP)

**Writes**

- Browser download: <sanitized name>.brush

**Depends on**

- Global fflate (zipSync) from the CDN
- Canvas (document.createElement, getImageData, toBlob)
- URL.createObjectURL and document for downloadBlob
- export/BrushArchive.js

**Gates and checkpoints**

- Errors are caught and shown as a toast

**Invoked by**

- app.js exportBrush

**Invokes**

- export/BrushArchive.js
- fflate.zipSync

**Notes**

The export runs and produces a file. Whether Procreate accepts it is unverified: the Brush.archive bytes carry the PlistEncoder container-index bug. canvasToGrayscalePNG writes luminance into RGB with alpha 255. The only claim in the repo that a file opened in Procreate is a ticked checkbox in the worked-example note.

### Export .brushset (Procreate)

`library` · status `partial`

Paths: `tools/brush-designer/export/BrushExporter.js`, `tools/brush-designer/app.js`

Packages one or more brushes as a Procreate .brushset ZIP.

**Entry points**

- `UI: Export ▾ -> 'Export .brushset (Procreate)' (data-export="brushset") -> app.exportBrushset()`
  - does: Downloads <sanitized name>.brushset containing only the current brush
  - changes: browser download
- `await BrushExporter.exportBrushset(name, [{brushState, shapeCanvas, grainCanvas}, ...]) -> Blob`
  - does: For each brush it writes <identifier>/Brush.archive, <identifier>/Shape.png, <identifier>/Grain.png and <identifier>/QuickLook/Thumbnail.png, then brushset.plist (a bplist array of the identifiers, level 6)
  - changes: nothing

**Inputs**

- set name (unused)
- array of brushes

**Outputs**

- application/octet-stream Blob (.brushset ZIP)

**Writes**

- Browser download: <sanitized name>.brushset

**Depends on**

- Global fflate
- Canvas
- export/BrushArchive.js
- export/PlistEncoder.js

**Gates and checkpoints**

- Errors are caught and shown as a toast

**Invoked by**

- app.js exportBrushset

**Invokes**

- export/BrushArchive.js
- export/PlistEncoder.js
- fflate.zipSync

**Notes**

The API accepts several brushes, but the UI always passes a single-element array, and there is no way to collect several brushes into a set. The name argument is never written into the archive. Folder names come from state.identifier. Every brush loaded from the same built-in preset shares that preset's id, so two such brushes would collide. brushset.plist inherits the PlistEncoder root-index bug. The worked-example note says a single-brush set imports into Procreate as a new group.

### Export .gbr (GIMP / Krita)

`library` · status `runs-today`

Paths: `tools/brush-designer/export/GbrEncoder.js`, `tools/brush-designer/app.js`

Writes the shape texture as a GIMP brush version 2 (.gbr) grayscale file, which Krita can also import as a brush tip.

**Entry points**

- `UI: Export ▾ -> 'Export .gbr (GIMP / Krita)' (data-export="gbr") -> app.exportGbr() (synchronous)`
  - does: Downloads <sanitized name>.gbr. The header name is the unsanitized state.name.
  - changes: browser download
- `GbrEncoder.encode(sourceCanvas, { name = 'Brush', spacingPercent = 10, size = null }) -> Uint8Array`
  - does: Writes 7 big-endian uint32 fields (header_size = 28 + name bytes + 1, version 2, width, height, bytes 1, magic 'GIMP', spacing), then a null-terminated UTF-8 name, then inverted-luminance pixels (black = opaque paint)
  - changes: nothing

**Inputs**

- shape canvas
- name
- spacingPercent = round(brushSpacing*100)

**Outputs**

- Uint8Array .gbr

**Writes**

- Browser download: <sanitized name>.gbr

**Depends on**

- Canvas 2D (document.createElement, getImageData)

**Gates and checkpoints**

- Spacing clamped to 1-1000

**Invoked by**

- app.js exportGbr
- export/UniversalKitExporter.js

**Notes**

Carries the shape only; the grain and all other parameters are not represented. No caller uses the size option. The header comment says the layout was checked against GIMP's gimpbrush-header.h; that source is not in the repo.

### Export Universal Kit (.zip)

`library` · status `runs-today`

Paths: `tools/brush-designer/export/UniversalKitExporter.js`, `tools/brush-designer/app.js`

Multi-app kit for brush engines whose native formats are undocumented: image-based brush tips plus a recipe.

**Entry points**

- `UI: Export ▾ -> 'Export Universal Kit (.zip)' (data-export="kit") -> app.exportUniversalKit()`
  - does: Downloads <sanitized name>-universal-kit.zip
  - changes: browser download
- `await UniversalKitExporter.export(brushState, shapeCanvas, grainCanvas, previewCanvas) -> Blob ; UniversalKitExporter.buildRecipe(state, spacingPercent) -> string`
  - does: Zip contents: gimp/shape.gbr (level 6); ink/shape-ink.png (512) and ink/grain-ink.png (1024), black RGB with alpha = luminance; mask/shape-mask.png and mask/grain-mask.png (grayscale); stroke-preview.png (the composited preview canvas, if toBlob succeeds); brush-recipe.md (level 6)
  - changes: nothing

**Inputs**

- BrushState
- shape canvas
- grain canvas
- preview canvas

**Outputs**

- application/zip Blob

**Writes**

- Browser download: <sanitized name>-universal-kit.zip

**Depends on**

- Global fflate
- Canvas/toBlob
- export/GbrEncoder.js
- export/BrushExporter.js
- editor/BrushState.js

**Gates and checkpoints**

- Deliberately does NOT write .abr (Photoshop), .afbrushes (Affinity) or .sut (Clip Studio). The header comment and the recipe explain these formats are undocumented or proprietary.

**Invoked by**

- app.js exportUniversalKit

**Invokes**

- export/GbrEncoder.js
- BrushExporter.canvasToInkAlphaPNG
- BrushExporter.canvasToGrayscalePNG
- fflate.zipSync

**Notes**

The recipe gives import steps for Photoshop (Edit -> Define Brush Preset), Affinity Photo/Designer, Clip Studio Paint, Krita (Settings -> Manage Resources... -> Import Resources -> Brush tips), GIMP (brushes folder via Edit -> Preferences -> Folders -> Brushes) and 'anything else' (Rebelle, ArtRage, Paint Tool SAI). It includes a Parameters table of the 33 ranged properties plus Blending Mode; the 9 booleans are not listed. It ends with '_Exported from the Studio Headless OS brush designer._'

### Export: Download Source

`web-app` · status `partial`

Paths: `tools/brush-designer/app.js`

Zips the app's own source files, fetched over HTTP, for download.

**Entry points**

- `UI: Export ▾ -> 'Download Source' (data-export="source") -> app.exportSource()`
  - does: Fetches a hard-coded list of 22 relative paths and zips each one that responds OK under procreate-brush-designer/<path> (level 6)
  - changes: browser download procreate-brush-designer-source.zip

**Inputs**

- The served source files

**Outputs**

- procreate-brush-designer-source.zip

**Reads**

- The 22 source paths via relative fetch()

**Writes**

- Browser download

**Depends on**

- Global fflate
- HTTP origin

**Gates and checkpoints**

- Missing or failed files are skipped silently

**Invoked by**

- app.js export menu

**Invokes**

- fetch
- fflate.zipSync

**Notes**

The list includes README.md, which does not exist in tools/brush-designer/ and is skipped. It omits preview/StrokeInput.js and ui/Section.js, both imported by the app, so the downloaded source would not run as-is.

### Import .brush / .brushset

`web-app` · status `stub`

Paths: `tools/brush-designer/app.js`, `tools/brush-designer/editor/PresetLibrary.js`, `tools/brush-designer/index.html`

Intended to import an existing Procreate brush.

**Entry points**

- `UI: Presets '↑' (#importBrushBtn, title 'Import .brush') -> hidden #importFileInput accept='.brush,.brushset' -> app.importBrush(file)`
  - does: Only shows the toast 'Import not yet fully implemented'
  - changes: nothing

**Inputs**

- A .brush or .brushset file

**Invoked by**

- User

**Notes**

PresetLibrary.importBrush(file) also returns null. There is no bplist decoder anywhere in the codebase.

### OllamaAssist (local-model JSON-patch client)

`protocol` · status `runs-today`

Paths: `tools/brush-designer/ai/OllamaAssist.js`

Client for the local Ollama REST API, plus the prompt and validation contract for AI edits to brush parameters.

**Entry points**

- `GET {endpoint}/api/tags (AbortSignal.timeout(6000)) via OllamaAssist.fetchTags(endpoint) -> model names`
  - does: Lists served models. familyMatches(tag, served) compares the part before ':'.
  - changes: nothing
- `POST {endpoint}/api/generate body {model, prompt, stream:false, keep_alive:'5m', options} via OllamaAssist.generate(endpoint, {model, prompt, options})`
  - does: Single non-streaming completion that returns data.response. There is no timeout on this call. The panel passes options {temperature:0.2, num_ctx, num_predict}.
  - changes: loads the model in Ollama
- `POST {endpoint}/api/generate body {model, keep_alive:0} via OllamaAssist.evict(endpoint, model)`
  - does: Best-effort model unload. The panel calls it only after generate succeeds; it is skipped if fetchTags or generate throws.
  - changes: Ollama model residency
- `OllamaAssist.buildPrompt(instruction, state) ; .buildPropertyTable(state) ; .extractJSON(text) ; .validatePatch(changes) -> {applied, rejected}`
  - does: Pure helpers. They build the prompt, extract the first balanced {...} after stripping <think> blocks (null on failure), and validate/clamp against the schema.
  - changes: nothing
- `OllamaAssist.getEndpoint()/setEndpoint(v)/getTierKey()/setTierKey(v)/getTier() ; OllamaAssist.DEFAULT_ENDPOINT ; OllamaAssist.TIERS`
  - does: Reads and writes the localStorage keys hub:endpoint (default http://localhost:11434) and hub:tier (default 'sm'; an unknown key falls back to sm)
  - changes: localStorage

**Inputs**

- Natural-language instruction
- Current brush state
- Endpoint and tier

**Outputs**

- {applied: {key: clampedValue}, rejected: [{key, reason}]} plus the model's summary

**Reads**

- localStorage hub:endpoint, hub:tier

**Writes**

- localStorage hub:endpoint, hub:tier

**Depends on**

- Ollama HTTP server (default http://localhost:11434)
- Model llama3.1:8b (tier sm: num_ctx 8192, num_predict 400) or mistral-nemo:12b (tier md: num_ctx 4096, num_predict 400)
- fetch, AbortSignal.timeout, localStorage
- editor/BrushState.js (BRUSH_PROPERTY_RANGES, BLENDING_MODES)

**Gates and checkpoints**

- The model gets no write access. It must return {"changes":{...},"summary":"..."}, and every key is validated.
- The 9 boolean props are coerced: true, 'true' or 1 become true; anything else becomes false.
- brushBlendingMode is rounded and clamped to 0-15; non-finite values are rejected ('not a number').
- The 33 ranged numeric props are clamped to their min/max; non-finite values are rejected ('not a number').
- Any other key (name, notes, authorName, shapeSource, grainSource, the pressure curves, identifier) is rejected as 'unknown property'.
- Unparseable output returns null so the caller can show the raw text.

**Invoked by**

- panels/AIAssistPanel.js

**Invokes**

- Ollama /api/tags
- Ollama /api/generate

**Notes**

What is sent: the instruction plus a table of the current values of the 33 ranged numeric properties (each with its range and a short hint), the 9 booleans, and brushBlendingMode with all 16 mode names. The AI can therefore change exactly the 43 exportable brush* tunables.

The header comment says it shares endpoint and tier with hub/ (hub/ollama.js and hub/app.js use the same localStorage keys), since both are served from one origin. TIERS is hard-coded here, whereas hub/app.js overrides its tiers from dashboard.json hardware.local_llm. The values currently match: llama3.1:8b/8192 and mistral-nemo:12b/4096, endpoint http://localhost:11434.

It does not consult state/compute_gate.json or the llm_local_sm/llm_local_md workload gating described in README. It reads no env vars. OLLAMA_ORIGINS is an Ollama-side setting documented in README and OBSIDIAN.md; OLLAMA_HOST appears in OBSIDIAN.md, BOOT.md and others, not in README.

### AI Assist tab

`web-app` · status `runs-today`

Paths: `tools/brush-designer/panels/AIAssistPanel.js`

Conversational editing: you describe a change, a local model proposes a validated parameter patch, and it is applied as one undoable step.

**Entry points**

- `UI: sidebar tab '✦ AI Assist' (data-panel="ai") -> textarea #aiInstruction -> 'Apply with AI' (#aiApplyBtn) or Ctrl/Cmd+Enter`
  - does: Runs AIAssistPanel.handleApply(): fetchTags, model-family check, buildPrompt, generate, evict, extractJSON, validatePatch, then onApply(applied, summary). onApply is app.applyAIPatch, which calls brushState.setState and pushes a history entry. The panel then renders a before/after diff and any ignored keys, and clears the textarea.
  - changes: brush state, history
- `UI: ⚙ (#aiSettingsBtn) -> Endpoint (#aiEndpoint) and Tier (#aiTier: 'sm — llama3.1:8b (everyday)' / 'md — mistral-nemo:12b (AC + quiet desktop)')`
  - does: Changes the Ollama endpoint (empty resets to the default) or the tier, and refreshes the connection dot: on / warn 'not pulled' / off 'unreachable'. Rendering the tab also calls GET /api/tags.
  - changes: localStorage hub:endpoint, hub:tier

**Inputs**

- Instruction text
- Endpoint
- Tier

**Outputs**

- Applied patch (one history entry labelled with the model's summary or 'AI edit: <instruction>')
- Diff and ignored-keys display

**Reads**

- Current BrushState
- localStorage hub:endpoint, hub:tier

**Writes**

- BrushState via app.applyAIPatch
- localStorage hub:endpoint, hub:tier

**Depends on**

- ai/OllamaAssist.js
- Local Ollama with the tier model pulled

**Gates and checkpoints**

- An empty instruction is refused ('Describe a change first.')
- A busy lock blocks concurrent requests, with an elapsed-seconds spinner
- If the tier model's family is not served, it throws "'<model>' is not served — installed: ... Run: ollama pull <model>"
- If no JSON can be extracted, nothing is applied and the raw response is shown (escaped)
- If validation leaves no keys, nothing is applied and the rejected keys are listed
- Every applied patch is one Ctrl+Z step

**Invoked by**

- app.js initPanels (panels.ai)

**Invokes**

- ai/OllamaAssist.js
- app.applyAIPatch

**Notes**

Not a BasePanel subclass; updateSliders() is a no-op. The UI note says CPU generation typically takes 30-90 seconds. The summary and raw text are escaped, but the model-supplied rejected key names are inserted into innerHTML unescaped (renderDiff and renderNoChanges). An applied patch triggers a preview re-render through the state subscription; the shape and grain canvases are never touched.

### Stroke Path tab

`web-app` · status `runs-today`

Paths: `tools/brush-designer/panels/PanelComponents.js`

Sliders for spacing, smoothing and jitter.

**Entry points**

- `UI: sidebar tab 'Stroke Path' (data-panel="stroke", the default) -> StrokePathPanel.render()`
  - does: Section stroke.spacing: brushSpacing (0-5), brushSpacingJitter, brushFallOff. Section stroke.smoothing: brushStreamline, brushStreamlinePressure, brushStabilization, brushMotionFiltering. Section stroke.jitter (collapsed by default): brushJitterX, brushJitterY.
  - changes: BrushState; localStorage brushDesigner.sections.v1 (section open state)

**Inputs**

- Slider input

**Outputs**

- State changes

**Reads**

- BrushState

**Writes**

- BrushState

**Depends on**

- ui/Slider.js
- ui/Section.js

**Invoked by**

- app.js switchPanel

**Invokes**

- BrushState.set
- app.onPanelChange

**Notes**

The preview does not simulate brushFallOff, brushStabilization, brushMotionFiltering or brushStreamlinePressure. brushStreamline is used only by live pointer input.

### Taper tab

`web-app` · status `runs-today`

Paths: `tools/brush-designer/panels/PanelComponents.js`

Taper size and opacity controls.

**Entry points**

- `UI: sidebar tab 'Taper' (data-panel="taper") -> TaperPanel.render()`
  - does: taper.size: brushTaperSizeStart, brushTaperSizeEnd, brushTaperTip. taper.opacity: brushTaperOpacity. taper.options: brushTaperLinked toggle.
  - changes: BrushState

**Inputs**

- Sliders
- toggle

**Outputs**

- State changes

**Reads**

- BrushState

**Writes**

- BrushState

**Depends on**

- ui/Slider.js
- ui/Section.js

**Invoked by**

- app.js switchPanel

**Invokes**

- BrushState.set
- app.onPanelChange

**Notes**

The preview simulates only brushTaperSizeStart and brushTaperSizeEnd.

### Shape tab

`web-app` · status `runs-today`

Paths: `tools/brush-designer/panels/PanelComponents.js`

Picks the shape generator and sets stamp placement and orientation.

**Entry points**

- `UI: sidebar tab 'Shape' (data-panel="shape") -> ShapePanel.render(shapeCanvas, onTextureChange)`
  - does: shape.source: one button per generator (9). A pick sets shapeSource and redraws the 512 shape canvas. shape.placement: brushShapeScatter (0-2), brushShapeRotation (0-6.283 rad), brushShapeCount (1-16), brushShapeCountJitter. shape.orientation (collapsed): brushShapeRandomized, brushAzimuth, brushFlipX, brushFlipY.
  - changes: BrushState; #shapeCanvas

**Inputs**

- Generator pick
- sliders
- toggles

**Outputs**

- State changes
- regenerated shape texture

**Reads**

- BrushState

**Writes**

- BrushState
- shape canvas

**Depends on**

- generators/ShapeGenerator.js
- ui/Slider.js
- ui/Section.js

**Invoked by**

- app.js switchPanel

**Invokes**

- generateShape
- app.onTextureChange

**Notes**

There is no custom-image upload, although BrushState comments and styles.css (.image-uploader) mention one. A generator pick creates no history entry.

### Grain tab

`web-app` · status `runs-today`

Paths: `tools/brush-designer/panels/PanelComponents.js`

Picks the grain generator and sets grain transform, depth and behaviour.

**Entry points**

- `UI: sidebar tab 'Grain' (data-panel="grain") -> GrainPanel.render(grainCanvas, onTextureChange)`
  - does: grain.source: 8 generator buttons. A pick sets grainSource and redraws the 1024 grain canvas. grain.transform: brushGrainScale (0-2), brushGrainRotation. grain.depth: brushGrainDepth, brushGrainDepthMin, brushGrainDepthJitter, brushGrainOffsetJitter. grain.behaviour (collapsed): brushGrainMoving, brushGrainZoom.
  - changes: BrushState; #grainCanvas

**Inputs**

- Generator pick
- sliders
- toggles

**Outputs**

- State changes
- regenerated grain texture

**Reads**

- BrushState

**Writes**

- BrushState
- grain canvas

**Depends on**

- generators/GrainGenerator.js
- ui/Slider.js
- ui/Section.js

**Invoked by**

- app.js switchPanel

**Invokes**

- generateGrain
- app.onTextureChange

**Notes**

Of the grain settings, the preview uses only brushGrainDepth. A generator pick creates no history entry.

### Dynamics tab

`web-app` · status `runs-today`

Paths: `tools/brush-designer/panels/PanelComponents.js`

Size and opacity ranges, and bleed.

**Entry points**

- `UI: sidebar tab 'Dynamics' (data-panel="dynamics") -> DynamicsPanel.render()`
  - does: dynamics.size: brushSizeMaximum, brushSizeMinimum. dynamics.opacity: brushOpacityMaximum, brushOpacityMinimum. dynamics.bleed (collapsed): brushBleedAmount.
  - changes: BrushState

**Inputs**

- Sliders

**Outputs**

- State changes

**Reads**

- BrushState

**Writes**

- BrushState

**Depends on**

- ui/Slider.js
- ui/Section.js

**Invoked by**

- app.js switchPanel

**Invokes**

- BrushState.set
- app.onPanelChange

**Notes**

In the preview, stamp size = 50 px × (min + (max − min) × pressure) and opacity = min + (max − min) × pressure. brushBleedAmount is exported only.

### Pencil tab (Apple Pencil pressure curves)

`web-app` · status `partial`

Paths: `tools/brush-designer/panels/PanelComponents.js`, `tools/brush-designer/ui/CurveEditor.js`

Bezier pressure-to-size and pressure-to-opacity response curves.

**Entry points**

- `UI: sidebar tab 'Pencil' (data-panel="pencil"; panel title 'Apple Pencil') -> PencilPanel.render()`
  - does: Two 400x160 CurveEditors (sections pencil.size and pencil.opacity) with presets linear, easeIn, easeOut, heavyPressure, lightTouch and sCurve. On change it writes brushPressureSizeResponse or brushPressureOpacityResponse = new Uint8Array(new Float64Array(8 floats).buffer).
  - changes: BrushState

**Inputs**

- Dragging the two middle control points (mouse/touch)
- preset buttons

**Outputs**

- 64-byte curve blobs in state; Brush.archive writes them as plist data

**Writes**

- BrushState

**Depends on**

- ui/CurveEditor.js
- ui/Section.js

**Gates and checkpoints**

- Endpoints (0,0) and (1,1) are fixed

**Invoked by**

- app.js switchPanel

**Invokes**

- CurveEditor

**Notes**

The editor always opens at 'linear'. setCurveData is never called, so a saved curve is not shown again. The preview renderer ignores the curves. Curve edits call brushState.set directly without onPanelChange, so they get no history entry of their own. The byte order is the platform's Float64Array order. The class comment says 'Pressure & Tilt', but no tilt controls exist.

### Wet Mix tab

`web-app` · status `runs-today`

Paths: `tools/brush-designer/panels/PanelComponents.js`

Wet-mix parameters.

**Entry points**

- `UI: sidebar tab 'Wet Mix' (data-panel="wetmix") -> WetMixPanel.render()`
  - does: wet.load: brushWetDilution, brushWetCharge. wet.blending: brushWetPull, brushWetAttack, brushWetBleed. wet.edges (collapsed): brushWetEdge, brushWetBurn.
  - changes: BrushState

**Inputs**

- Sliders
- toggles

**Outputs**

- State changes

**Reads**

- BrushState

**Writes**

- BrushState

**Depends on**

- ui/Slider.js
- ui/Section.js

**Invoked by**

- app.js switchPanel

**Invokes**

- BrushState.set
- app.onPanelChange

**Notes**

Exported only; the preview does not simulate wet mix.

### Color Dynamics tab

`web-app` · status `stub`

Paths: `tools/brush-designer/panels/PanelComponents.js`

Placeholder for Procreate's colour dynamics.

**Entry points**

- `UI: sidebar tab 'Color Dynamics' (data-panel="color") -> ColorDynamicsPanel.render()`
  - does: Shows a 'Not implemented' empty state: colour dynamics are neither simulated nor exported
  - changes: nothing

**Depends on**

- ui/Section.js

**Invoked by**

- app.js switchPanel

**Notes**

BrushState has no colour-dynamics parameters.

### Rendering tab

`web-app` · status `runs-today`

Paths: `tools/brush-designer/panels/PanelComponents.js`

Blend mode selection.

**Entry points**

- `UI: sidebar tab 'Rendering' (data-panel="rendering") -> RenderingPanel.render()`
  - does: Section rendering.blend: a dropdown for brushBlendingMode over the 16 BLENDING_MODES (ids 0-15, parseInt)
  - changes: BrushState

**Inputs**

- Dropdown

**Outputs**

- State change

**Reads**

- BrushState

**Writes**

- BrushState

**Depends on**

- editor/BrushState.js BLENDING_MODES
- ui/Section.js

**Invoked by**

- app.js switchPanel

**Invokes**

- BrushState.set
- app.onPanelChange

**Notes**

The preview always composites with multiply, whatever the blend mode. The dropdown does not resync on undo (only sliders do).

### About This Brush tab

`web-app` · status `runs-today`

Paths: `tools/brush-designer/panels/PanelComponents.js`

Author and notes metadata, a read-only spec sheet, and reset.

**Entry points**

- `UI: sidebar tab 'About This Brush' (data-panel="about") -> AboutBrushPanel.render(onReset)`
  - does: about.identity: authorName input and notes textarea (applied on 'change'). about.spec (collapsed): a 12-row read-only table computed from state. about.reset (collapsed): 'Reset to defaults'.
  - changes: BrushState authorName/notes; reset

**Inputs**

- Author
- notes
- reset click

**Outputs**

- Metadata in state, later written as brushAuthorName/brushNotes and into the kit recipe

**Reads**

- BrushState

**Writes**

- BrushState

**Depends on**

- ui/Modal.js
- ui/Section.js

**Gates and checkpoints**

- Reset requires Modal.confirm. It then runs brushState.reset() (identifier kept) and app.onReset(), which regenerates the canvases from the default sources and pushes 'Reset to defaults' to history.

**Invoked by**

- app.js switchPanel

**Invokes**

- BrushState.reset
- app.onReset

**Notes**

Author and notes edits bypass onPanelChange, so they get no history entry of their own. The brush name is edited in the header input #brushName, not here.

### Stroke preview / test sheet

`web-app` · status `runs-today`

Paths: `tools/brush-designer/preview/StrokeRenderer.js`, `tools/brush-designer/preview/StrokeInput.js`

Canvas approximation of the brush engine. It draws sample S-curve strokes at light, medium and heavy pressure, and gives you a surface to draw on with pen pressure or a speed-based substitute.

**Entry points**

- `new StrokeRenderer(canvas) ; .setTextures(shape, grain) ; .render(state, ['light','medium','heavy']) ; .commitStroke(path, state, basePressure) ; .stampWet(...) ; .clearWet() ; .undoInk() ; .clearInk() ; .canUndoInk() ; .hasInk() ; .computeSize/computeOpacity(state, pressure) ; .composite()`
  - does: Three layers. base: paper #F5F0E8 plus sample strokes at pressures 0.3/0.6/1.0. ink: committed user strokes, kept across parameter changes and resizes, with 12-step undo. wet: the live stroke. The device-pixel ratio is capped at 2.
  - changes: canvas pixels
- `new StrokeInput(canvas, renderer, getBrushState, {onStatus, onStrokeEnd})`
  - does: Pointer events with coalesced samples. Uses pen pressure when pointerType is 'pen' and pressure > 0; otherwise a speed-derived pressure (0.35-1.0). Applies streamline smoothing. Escape abandons a stroke; a tap commits a single stamp.
  - changes: renderer layers
- `UI: Sample Light / Medium / Heavy / All; Undo stroke (#undoStrokeBtn); Clear (#clearSheetBtn)`
  - does: Chooses which sample rows to show; undoes or clears the user's ink
  - changes: preview only

**Inputs**

- BrushState
- shape and grain canvases
- pointer events

**Outputs**

- The preview canvas, also captured as stroke-preview.png in the Universal Kit

**Depends on**

- Canvas 2D, window.devicePixelRatio, Image, Pointer Events, performance.now

**Gates and checkpoints**

- Ink undo history is capped at 12 ImageData snapshots and cleared on resize (the ink itself is preserved)

**Invoked by**

- app.js

**Notes**

Parameters the preview simulates: brushSpacing, brushSpacingJitter, brushStreamline (live input only; passed to computeStampPositions but unused there), brushJitterX/Y, brushTaperSizeStart/End, brushSizeMinimum/Maximum, brushOpacityMinimum/Maximum, brushShapeRotation, brushAzimuth, brushShapeScatter (used as random rotation), and brushGrainDepth.

Everything else is exported but not previewed: stabilization, motion filtering, fall-off, streamline pressure, shape count/count jitter/flip/randomized, grain scale/rotation/moving/zoom/min/jitters, taper tip/opacity/linked, wet mix, bleed, blend mode and the pressure curves.

The readout shows the pressure source as 'pen' or 'speed'. The cursor ring shows the size at full pressure.

### UI component kit

`library` · status `runs-today`

Paths: `tools/brush-designer/ui/Slider.js`, `tools/brush-designer/ui/CurveEditor.js`, `tools/brush-designer/ui/Section.js`, `tools/brush-designer/ui/Modal.js`, `tools/brush-designer/ui/Toast.js`

DOM widgets used by the panels and the app shell.

**Entry points**

- `new Slider(container, {min, max, step, value, label, displayFormatter, onChange}) ; .setValue(v, silent) ; .reset() ; .getValue()`
  - does: Keyboard-accessible slider (arrows, Shift for ×10, Home/End); double-click resets it to its initial value
  - changes: DOM
- `new CurveEditor(canvas, {width:400, height:160, onChange}) ; .loadPreset(name) ; .getCurveData() ; .setCurveData(data)`
  - does: Four-point cubic bezier editor. getCurveData returns 8 floats [x0,y0..x3,y3].
  - changes: DOM
- `new Section({id, title, hint, defaultOpen}) ; .add(...nodes) ; .setOpen(open) ; .setHint(text) ; createSectionToolbar(getSections)`
  - does: Collapsible sections whose open state persists in localStorage 'brushDesigner.sections.v1', plus an Expand all / Collapse all toolbar
  - changes: localStorage brushDesigner.sections.v1
- `Modal.prompt({title, label, defaultValue, placeholder}) -> Promise<string|null> ; Modal.confirm({title, message, okLabel, danger}) -> Promise<boolean>`
  - does: In-page replacements for window.prompt and window.confirm (input is escaped)
  - changes: DOM
- `getToast().success|error|info(message, duration=3000) ; new Toast(container='#toastContainer')`
  - does: Non-blocking notifications in #toastContainer
  - changes: DOM

**Reads**

- localStorage brushDesigner.sections.v1

**Writes**

- localStorage brushDesigner.sections.v1

**Depends on**

- Browser DOM

**Invoked by**

- panels/PanelComponents.js
- app.js

**Notes**

All UI; not usable headless. Toast inserts the message as innerHTML without escaping, including exception messages from exports. Slider inserts its label unescaped; the labels are hard-coded.

### Hub Brushes tab (embedding)

`web-app` · status `runs-today`

Paths: `hub/index.html`, `hub/styles.css`, `hub/app.js`

Embeds the brush designer inside THE HUB as an iframe.

**Entry points**

- `hub/index.html tab button data-tab="brushes" -> section #view-brushes -> <iframe class="brush-frame" id="brushFrame" title="Procreate Brush Designer" src="../tools/brush-designer/index.html" loading="lazy">`
  - does: Loads the designer same-origin (no sandbox attribute) inside the hub. .brush-frame is 100% wide and 78vh tall.
  - changes: nothing
- `Link 'Open in a new tab ↗' href="../tools/brush-designer/index.html" target="_blank" rel="noopener"`
  - does: Opens the designer standalone
  - changes: nothing

**Depends on**

- Hub served over HTTP from the repo root

**Invoked by**

- User clicking the Brushes tab (hub/app.js stores the last tab in localStorage hub:tab)

**Invokes**

- tools/brush-designer/index.html

**Notes**

The hub's hint says 'nothing here talks to it besides embedding the page'. There is no postMessage and no programmatic channel. Because the two are same-origin, they share localStorage, including hub:endpoint and hub:tier. hub/app.js seeds hub:endpoint from dashboard.json hardware.local_llm.endpoint only when that key is unset. No other file in the repo (dashboard.json, router.js, control_room.html, skills/) references the designer.

### Start-Hub.ps1 launcher

`launcher` · status `runs-today`

Paths: `tools/launcher/Start-Hub.ps1`, `tools/launcher/README.md`, `tools/launcher/Install-Shortcut.ps1`

Serves the repo root on loopback and opens the hub. This is the documented one-press way to reach the embedded brush designer.

**Entry points**

- `.\Start-Hub.ps1 [-Port <1024-65535, default 8765>] [-PortSearch <1-50, default 10>] [-NoBrowser]`
  - does: Reuses a running hub server on ports Port..Port+PortSearch-1. A port counts as a hub server if GET /hub/index.html returns 200 and contains 'Studio Headless OS'. Otherwise it starts python.exe (falling back to python3.exe) -m http.server <free> --bind 127.0.0.1 --directory <root>, hidden. It waits up to 15 s, opens http://localhost:<port>/hub/ unless -NoBrowser is given, and prints 'THE HUB is live at <url>'.
  - changes: starts a hidden background python process
- `.\Start-Hub.ps1 -Stop`
  - does: Stops the processes listening on probed ports that answer as the hub server
  - changes: kills processes
- `Shortcut target written by Install-Shortcut.ps1: powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "<repo>\tools\launcher\Start-Hub.ps1"`
  - does: Desktop and Start Menu 'Studio Hub' shortcuts; the Start Menu copy has the hotkey CTRL+ALT+H
  - changes: nothing beyond Start-Hub's effects

**Outputs**

- 'THE HUB is live at <url>' line

**Reads**

- hub/index.html (existence check)

**Depends on**

- Windows PowerShell
- Python 3 on PATH

**Gates and checkpoints**

- Throws if hub\index.html is missing, all probed ports are busy, Python is not found, or the server does not come up within 15 s

**Invoked by**

- User; the Studio Hub shortcuts created by Install-Shortcut.ps1 (Ctrl+Alt+H on the Start Menu copy)

**Invokes**

- python -m http.server

**Notes**

Not run during this verification. Usage comes from the param() block, the .EXAMPLE lines (.\Start-Hub.ps1, .\Start-Hub.ps1 -Stop), the launcher README and Install-Shortcut.ps1.

### hub-static-server launch config

`launcher` · status `runs-today`

Paths: `.claude/launch.json`

Claude preview/launch configuration that serves the repo root, from which both /hub/ and /tools/brush-designer/index.html load.

**Entry points**

- `python3 -m http.server 8347 (configuration name 'hub-static-server', port 8347)`
  - does: Static server; README names it as the way to give the hub and the designer an HTTP origin
  - changes: starts a python process

**Depends on**

- python3 on PATH

**Invoked by**

- Claude preview tooling / user

**Invokes**

- python3 -m http.server

**Notes**

Unlike Start-Hub.ps1, it does not pass --bind 127.0.0.1, so the listener uses http.server's default bind address.

### brush_designer skill + headless adapter

`skill` · status `specified-not-implemented`

Paths: `DECISIONS.md`, `Router.md`, `README.md`

Planned programmatic API over the DOM-free core, so the Router and agents can run the brush designer and emit a Content MD.

**Notes**

DECISIONS.md D2 chooses to 'wrap the DOM-free core in a programmatic API the Router and agents can call, and write skills/brush_designer.skill.md'. It lists the DOM references per module (BrushState 0, each generator 1, BrushExporter 5), names OffscreenCanvas or a Node canvas as substitutes, and records 'Not yet done. No adapter and no skill file'. D7 says brush_designer should be written first as the reference implementation, and the five migration-pending skills follow its pattern. Router.md: 'Not yet routed — see DECISIONS.md.' skills/ holds 9 skill files, none for brush_designer.

What a headless driver would need, based on the code:
(a) Node-importable with no shims: editor/BrushState.js, editor/HistoryManager.js, export/PlistEncoder.js and export/BrushArchive.js. BrushArchive.encode(plainState) returns Brush.archive bytes directly, but PlistEncoder's container-index bug must be fixed before those bytes are trustworthy. OllamaAssist.buildPrompt, extractJSON and validatePatch are pure. fetchTags and generate take an explicit endpoint and need fetch/AbortSignal.timeout. The endpoint/tier getters need a localStorage substitute.
(b) Needs a Canvas 2D implementation: generateShape and generateGrain (both call document.createElement('canvas')), GbrEncoder.encode, BrushExporter.canvasToGrayscalePNG, canvasToInkAlphaPNG and generateThumbnail (all via canvas.toBlob), and UniversalKitExporter (previewCanvas.toBlob).
(c) fflate must be supplied as globalThis.fflate; the app gets it only from the CDN <script> tag.
(d) BrushExporter.downloadBlob must be replaced by a file write, because it clicks an anchor.
(e) Presets depend on browser localStorage and IndexedDB.
An alternative with no adapter: serve index.html, load it in a headless browser, drive the global window.app (brushState.setState, exportBrush, ...) and capture the downloads.

### Worked-example Content MD: Dry Stipple brush

`data` · status `never-exercised`

Paths: `vault/_examples/example-stipple-brush.md`

Worked example of a vault Content MD with kind: brush that records brush_designer work.

**Invoked by**

- vault/SCHEMA.md lists _examples/ as 'worked examples, safe to delete'

**Notes**

Frontmatter:
- id cmd_20260823_dry-stipple-brush; type content-md; kind brush
- title 'Dry Stipple — Texture Brush'; project "[[Brush Kit v1]]"; status in-progress
- skills [brush_designer]; context_brand [visual_identity]; context_domain [classical_illustration]
- artifacts: assets/brushes/dry-stipple-v3.brush (final) and dry-stipple-v1.brush (variant); tags [brush, texture, procreate]

Neither artifact exists: there is no assets/brushes/ directory. No tool in the repo produced this note, so it is illustrative.

The Method section says 'Reproduce from tools/brush-designer/ defaults'. It uses real keys: brushSpacing 0.14, brushSpacingJitter 0.18, brushStreamline 0.12, brushStreamlinePressure 0.40, brushJitterX/Y 0.22. It mixes in names that are not in the model:
- 'blendMode' (the model uses brushBlendingMode)
- 'grain noise generator, scale 0.6, contrast 0.75': a 'Noise' grain generator and brushGrainScale do exist, but there is no contrast parameter
- 'shape default round, hardness 0.35': there is no hardness parameter and no 'default round' generator
- v1's 'square grain': no such generator

It says 'Export via the Export panel'; in the app it is a menu. It links [[wet-stipple-brush]].

### wet-stipple-brush.md (root)

`data` · status `stub`

Paths: `wet-stipple-brush.md`

Presumably the target of the [[wet-stipple-brush]] wikilink in the example note.

**Invoked by**

- [[wet-stipple-brush]] link in vault/_examples/example-stipple-brush.md

**Notes**

The file exists and is empty (0 bytes). It sits at the repo root, not under vault/. Its git status (claimed untracked) cannot be checked with the allowed tools.

## Usage flows

### Launch standalone

1. From the repo root, run python3 -m http.server 8347 (the .claude/launch.json 'hub-static-server' configuration), or run .\Start-Hub.ps1 from tools\launcher.
2. Open http://localhost:<port>/tools/brush-designer/index.html. It needs an HTTP origin, not file://.
3. index.html loads fflate@0.8.2 from cdn.jsdelivr.net as a global, then app.js as an ES module.
4. On DOMContentLoaded, app.js creates window.app. It generates the 'Soft Circle' 512 shape and the 'Paper Fine' 1024 grain, builds the renderer, input handler and panels (Stroke Path shown), pushes the 'Initial state' history entry, seeds the built-in presets if none are present, renders the preview and shows a 'loaded' toast.

### Launch inside the hub

1. Run .\Start-Hub.ps1 (or the Studio Hub shortcut / Ctrl+Alt+H). It opens http://localhost:8765/hub/, or the next free port up to 8774.
2. Click the 'Brushes' tab (data-tab="brushes").
3. The iframe #brushFrame lazy-loads ../tools/brush-designer/index.html from the same origin. Alternatively, 'Open in a new tab ↗' opens it standalone.
4. The Ollama endpoint and tier are shared with the hub through localStorage hub:endpoint and hub:tier.

### Design a brush manually and export to Procreate

1. Rename it in the header (#brushName; applied on change, no history entry).
2. Shape tab: pick one of the 9 generators and adjust placement and orientation. Grain tab: pick one of the 8 generators and adjust transform, depth and behaviour.
3. Tune Stroke Path, Taper, Dynamics, Pencil curves, Wet Mix and Rendering. Slider and toggle changes re-render the preview within 16 ms and are pushed to history after 500 ms.
4. Draw on the preview sheet to test. Switch between the Light/Medium/Heavy/All sample rows; use Undo stroke or Clear.
5. Optionally fill in Author and Notes under About This Brush.
6. Export ▾ -> 'Export .brush (Procreate)'. BrushExporter.exportBrush zips Brush.archive (BrushArchive + PlistEncoder), Shape.png, Grain.png and QuickLook/Thumbnail.png, and the browser downloads <name>.brush. Procreate compatibility is unverified; see the PlistEncoder note.
7. Or Export ▾ -> 'Export .brushset' for a single-brush set: <identifier>/... plus brushset.plist.

### AI-assisted parameter edit

1. Make sure Ollama is reachable (default http://localhost:11434) and the tier model is pulled: llama3.1:8b for sm, mistral-nemo:12b for md.
2. Open the '✦ AI Assist' tab; this calls GET /api/tags for the connection dot. Optionally use ⚙ to change the endpoint (hub:endpoint) and tier (hub:tier).
3. Type an instruction (e.g. 'make the grain rougher and reduce streamline') and press Apply with AI, or Ctrl/Cmd+Enter.
4. The panel calls GET /api/tags again and checks the model family. If the model is missing, it shows an 'ollama pull <model>' hint.
5. It sends POST /api/generate {model, prompt: property table + request, stream:false, keep_alive:'5m', options:{temperature:0.2, num_ctx, num_predict:400}}. If that succeeds, it sends POST /api/generate {model, keep_alive:0} to evict the model.
6. extractJSON parses the first balanced {...}, ignoring <think> blocks. validatePatch clamps or coerces the 43 allowed keys and rejects all others.
7. If anything is valid, app.applyAIPatch runs brushState.setState(applied) and pushes one history entry. The panel shows the before-to-after diff and any ignored keys.
8. Ctrl+Z reverts the whole AI edit in one step. The shape and grain canvases are never touched.

### Save and load presets

1. Presets '+' -> Modal.prompt 'Preset name' -> Modal.prompt 'Category' (default Custom).
2. addPreset makes a 128px thumbnail, stores the shape and grain PNG data URLs in IndexedDB ProcreateBrushDesigner/presetImages, and stores the metadata and full settings in localStorage brushPresets.
3. Click a card: the stored PNGs load into the canvases, settings are applied with setState (partial for built-ins, full for user presets), and a 'Loaded preset: <name>' history entry is added.
4. There is no delete or rename UI.

### Export to non-Procreate apps

1. Export ▾ -> 'Export .gbr (GIMP / Krita)' produces <name>.gbr: shape only, spacing = round(brushSpacing*100) clamped to 1-1000.
2. Export ▾ -> 'Export Universal Kit (.zip)' produces gimp/shape.gbr, ink/*.png (black on transparent), mask/*.png (grayscale), stroke-preview.png and brush-recipe.md.
3. Follow brush-recipe.md: in Photoshop use Edit -> Define Brush Preset with ink/shape-ink.png; in Affinity or Clip Studio use brush-from-image; in Krita use Import Resources -> Brush tips; in GIMP use the brushes folder. Set spacing to the stated percent.

### Headless drive (not implemented; what it would take)

1. Option A (adapter, per DECISIONS.md D2): in Node, import editor/BrushState.js and export/BrushArchive.js directly. BrushArchive.encode(state) returns Brush.archive bytes, but fix PlistEncoder's container-index bookkeeping first.
2. Supply a Canvas 2D implementation for generateShape and generateGrain, which call document.createElement('canvas'). ShapeGenerators[name](ctx,size,seed) and GrainGenerators[name](ctx,size,seed) accept any context.
3. Replace BrushExporter's canvas.toBlob PNG output with a PNG encoder, set globalThis.fflate from the fflate package, and zip Brush.archive, Shape.png, Grain.png and QuickLook/Thumbnail.png to disk instead of calling downloadBlob.
4. For AI edits, call OllamaAssist.buildPrompt, generate(endpoint, ...), extractJSON and validatePatch with an explicit endpoint, bypassing the localStorage-backed getters.
5. Write skills/brush_designer.skill.md and a vault Content MD (kind: brush, like vault/_examples/example-stipple-brush.md) to satisfy the Router loop.
6. Option B (no code changes): serve the repo, open index.html in a headless browser, call window.app.brushState.setState({...}) and window.app.exportBrush() (or the other export methods), and capture the browser download.

## Relationships

| From | Relation | To |
|---|---|---|
| Procreate Brush Designer (web app shell) | owns the single BrushState instance and subscribes to its changes | BrushState (parameter model) |
| Procreate Brush Designer (web app shell) | pushes snapshots (50 steps); Ctrl+Z/Y | HistoryManager (undo/redo) |
| Procreate Brush Designer (web app shell) | seeds built-ins, saves and loads presets | PresetLibrary (+ Presets sidebar) |
| Procreate Brush Designer (web app shell) | renders the preview on state change; forwards pointer status to the readout and cursor | Stroke preview / test sheet |
| Procreate Brush Designer (web app shell) | Export menu item data-export=brush | Export .brush (Procreate) |
| Procreate Brush Designer (web app shell) | Export menu item data-export=brushset (single brush) | Export .brushset (Procreate) |
| Procreate Brush Designer (web app shell) | Export menu item data-export=gbr | Export .gbr (GIMP / Krita) |
| Procreate Brush Designer (web app shell) | Export menu item data-export=kit | Export Universal Kit (.zip) |
| Procreate Brush Designer (web app shell) | Export menu item data-export=source | Export: Download Source |
| Procreate Brush Designer (web app shell) | import button wired to a stub | Import .brush / .brushset |
| Procreate Brush Designer (web app shell) | uses Toast and Modal; panels use Slider, Section and CurveEditor | UI component kit |
| Export .brush (Procreate) | encodes Brush.archive | BrushArchive (Brush.archive encoder) |
| Export .brushset (Procreate) | encodes one Brush.archive per brush | BrushArchive (Brush.archive encoder) |
| Export .brushset (Procreate) | encodes brushset.plist (array of identifiers) | PlistEncoder (bplist00) |
| BrushArchive (Brush.archive encoder) | binary plist serialisation (inherits the container-index bug) | PlistEncoder (bplist00) |
| Export Universal Kit (.zip) | embeds gimp/shape.gbr via GbrEncoder.encode | Export .gbr (GIMP / Krita) |
| Export Universal Kit (.zip) | reuses BrushExporter.canvasToInkAlphaPNG and canvasToGrayscalePNG | Export .brush (Procreate) |
| Export Universal Kit (.zip) | captures the preview canvas as stroke-preview.png | Stroke preview / test sheet |
| AI Assist tab | fetchTags, buildPrompt, generate, evict, extractJSON, validatePatch | OllamaAssist (local-model JSON-patch client) |
| AI Assist tab | each applied patch is one history entry via app.applyAIPatch | HistoryManager (undo/redo) |
| OllamaAssist (local-model JSON-patch client) | validates against BRUSH_PROPERTY_RANGES and BLENDING_MODES; may change only the 43 brush* tunables | BrushState (parameter model) |
| OllamaAssist (local-model JSON-patch client) | shares localStorage hub:endpoint and hub:tier with hub/ollama.js and hub/app.js (same origin) | Hub Brushes tab (embedding) |
| Shape tab | generator buttons call generateShape(name, 512) | ShapeGenerator |
| Grain tab | generator buttons call generateGrain(name, 1024) | GrainGenerator |
| PresetLibrary (+ Presets sidebar) | dynamic import to render built-in preset textures | ShapeGenerator |
| PresetLibrary (+ Presets sidebar) | dynamic import to render built-in preset textures | GrainGenerator |
| Pencil tab (Apple Pencil pressure curves) | uses CurveEditor | UI component kit |
| About This Brush tab | reset gated by Modal.confirm | UI component kit |
| Hub Brushes tab (embedding) | same-origin iframe src ../tools/brush-designer/index.html; no programmatic channel | Procreate Brush Designer (web app shell) |
| Start-Hub.ps1 launcher | serves the repo root over loopback HTTP and opens /hub/ | Hub Brushes tab (embedding) |
| hub-static-server launch config | serves the repo root on port 8347, giving the app its HTTP origin | Procreate Brush Designer (web app shell) |
| brush_designer skill + headless adapter | planned wrapper over the DOM-free core (DECISIONS.md D2); not built | BrushState (parameter model) |
| brush_designer skill + headless adapter | planned headless .brush encoding path; not built | BrushArchive (Brush.archive encoder) |
| Worked-example Content MD: Dry Stipple brush | records skills: [brush_designer] and 'Reproduce from tools/brush-designer/ defaults' | brush_designer skill + headless adapter |
| Worked-example Content MD: Dry Stipple brush | wikilink [[wet-stipple-brush]]; the root file is empty | wet-stipple-brush.md (root) |

**Open questions the files could not settle**

- Do the exported .brush and .brushset files open in Procreate? Reading PlistEncoder.addObject shows container objects get the wrong index, so the trailer root and nested references point at the wrong objects. There is also no bplist UID type, and brushset.plist is a bare array of UUID strings. The only claim of a successful open is a ticked checkbox in the worked example, which SCHEMA.md calls 'safe to delete'.
- With Shift held, does the browser report e.key as 'Z'? If so, the Ctrl/Cmd+Shift+Z redo branch in app.js (inside `if (e.key === 'z')`) never fires. This can't be settled from the repo.
- Does the AI Assist fetch to Ollama need OLLAMA_ORIGINS to allow the static-server origin (http://localhost:8347 or :8765)? README says the hub's Ask tab needs 'one more origin to allow'; the brush-designer code and docs say nothing.
- Should OllamaAssist's hard-coded TIERS follow dashboard.json hardware.local_llm, as hub/app.js does? The values currently match but could drift.
- Should AI Assist go through the compute gate (state/compute_gate.json, workload llm_local_sm/llm_local_md) described in README? Today it does not.
- Which runtime is intended for the D2 headless adapter: OffscreenCanvas, a Node canvas library, or a headless browser? D2 names the first two; nothing is chosen or built.
- Do pressure curves (Uint8Array) survive undo/redo and preset save/load? Both go through JSON, which would turn them into plain objects that PlistEncoder then writes as a dict rather than data. Unverified by running.
- Procreate's expected byte order and layout for brushPressureSizeResponse/brushPressureOpacityResponse are not documented in the repo. The code writes the platform's Float64Array bytes of 8 control-point coordinates.
- How should the worked example's Method fields that are not in the model (blendMode, grain 'contrast', shape 'hardness', 'default round', 'square grain') map onto real parameters?
- What is the root file wet-stipple-brush.md for? It is empty, sits outside vault/, and its git tracking status could not be checked.
- The assets/brushes/ artifacts named in the example note do not exist. Is that intended because it is only an example?
- Every brush loaded from the same built-in preset gets that preset's id as its identifier (and .brushset folder name). Is that collision intended?

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: PlistEncoder is a working bplist00 encoder (status runs-today)
  - evidence: tools/brush-designer/export/PlistEncoder.js addObject (lines 88-130): index = this.objects.length is reserved, then encodeArray/encodeDict call addObject for the children (which push first), and only then is the container pushed (line 128). The returned index, and the trailer root index at line 65, therefore point at the container's first child. For Brush.archive the root is the '$version' key string. Status changed to partial; .brush/.brushset validity flagged.
- **corrected**: Undo, redo and AI patches can change shapeSource/grainSource without regenerating the canvases
  - evidence: ai/OllamaAssist.js validatePatch rejects any key not in BOOLEAN_PROPS, brushBlendingMode or BRUSH_PROPERTY_RANGES, so shapeSource and grainSource are 'unknown property'. Only undo/redo (app.js undo/redo -> setState) can change them without a canvas redraw.
- **corrected**: OllamaAssist.evict runs 'right after each request'
  - evidence: panels/AIAssistPanel.js handleApply lines 143-157: evict is awaited only after generate returns. A throw in fetchTags, the model check or generate skips it.
- **corrected**: Start-Hub invocation 'powershell -File tools/launcher/Start-Hub.ps1 ...'
  - evidence: tools/launcher/Start-Hub.ps1 .EXAMPLE shows '.\Start-Hub.ps1' and '.\Start-Hub.ps1 -Stop'. Install-Shortcut.ps1 line 96 builds '-NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "<...>\Start-Hub.ps1"'. The inventory's form is not in the source; it was replaced with the source forms.
- **corrected**: Outputs: 'procreate-brush-designer-source.zip (the <name> part is state.name with every [^a-zA-Z0-9] replaced by _)'
  - evidence: app.js line 541: the source zip name is fixed. The sanitization at lines 430/450/468/486 applies to the .brush, .brushset, .gbr and -universal-kit.zip names.
- **corrected**: Worked-example note status 'generated'
  - evidence: vault/_examples/example-stipple-brush.md is a hand-written worked example (vault/SCHEMA.md: 'worked examples, safe to delete'). The artifacts it names (assets/brushes/*.brush) do not exist and no skill file exists, so nothing generated it. Status changed to never-exercised.
- **unverifiable**: Git working-tree state: StrokeInput.js and Section.js untracked; app.js, index.html, PanelComponents.js, StrokeRenderer.js, styles.css, CurveEditor.js, Toast.js modified; wet-stipple-brush.md untracked
  - evidence: Checking requires git or .git/ access, both excluded by the hard rules (Read/Glob/Grep only, no .git/). The files exist on disk; tracking status is unconfirmed.
- **corrected**: Env var names OLLAMA_ORIGINS and OLLAMA_HOST appear in repo docs (OBSIDIAN.md, README)
  - evidence: Grep: OLLAMA_ORIGINS is in README.md line 73 and OBSIDIAN.md lines 78/83/172. OLLAMA_HOST is in OBSIDIAN.md, BOOT.md, skills/local_rag_orchestration.skill.md, tools/vault_rag.py and tools/bootstrap.sh, but not README.md.
- **added**: Only generator picks skip history
  - evidence: panels/PanelComponents.js: PencilPanel CurveEditor onChange (lines 446/451), AboutBrushPanel author/notes 'change' (lines 549/562) and app.js brush name 'change' (line 164) all call brushState.set without onChange/onPanelChange, so none of them creates its own history entry.
- **added**: Panels resync on state change
  - evidence: app.js onStateChange line 320 calls panels[current].updateSliders(). BasePanel.updateSliders (PanelComponents.js lines 198-202) iterates only this.sliders, so toggles, the dropdown, generator buttons, text fields and curve editors keep stale display after undo, redo, AI patch or preset load.
- **added**: Keyboard: Ctrl/Cmd+Shift+Z redo
  - evidence: app.js lines 172-186: a document-level keydown with no target filter checks e.key === 'z' and then e.shiftKey. It also intercepts Ctrl+Z inside text inputs with preventDefault. Whether Shift+Z reports lowercase 'z' is browser behaviour and is not verifiable from the repo.
- **corrected**: Loading any preset merges partial settings
  - evidence: editor/PresetLibrary.js addPreset line 115 stores settings = brushState.get() (full state, including name and identifier). Only the built-ins (lines 213-275) are partial, and those set identifier = preset id (line 307).
- **corrected**: Ink kept across resizes with 12-step undo
  - evidence: preview/StrokeRenderer.js setSize: the ink is preserved through a toDataURL round-trip, but line 98 sets inkHistory = [], so undo history is lost on resize.
- **added**: Unescaped HTML sinks
  - evidence: panels/AIAssistPanel.js lines 195/207 put model-supplied rejected keys into innerHTML unescaped. app.js renderPresets lines 601-606 does the same with preset.name. ui/Toast.js line 37 inserts the message, including error.message, unescaped.
- **corrected**: Grain tab dependencies: generators/GrainGenerator.js only
  - evidence: GrainPanel extends BasePanel, which uses ui/Slider.js and ui/Section.js (PanelComponents.js imports, lines 13-15). The same applies to the Dynamics, Wet Mix, Rendering and Color Dynamics tabs.
- **added**: README '~4,000 lines'
  - evidence: The Read line counts give 5,705 lines of JS plus index.html (app.js 677, PanelComponents 629, StrokeRenderer 428, ...) and 7,129 including styles.css (1,424).
- **added**: Module-by-module export map absent
  - evidence: Export lists taken from each file's export statements (e.g., PanelComponents.js exports BasePanel plus 10 panels and a default object; Section.js exports Section and createSectionToolbar; Toast.js exports Toast and getToast; the generators export ShapeGenerators/GrainGenerators plus their helper functions). Added to the summary.
- **added**: .claude/launch.json only mentioned inline
  - evidence: .claude/launch.json defines configuration 'hub-static-server': runtimeExecutable python3, args ['-m','http.server','8347'], port 8347. Added as a launcher entry.
- **corrected**: Hub 'Open in a new tab' link attributes
  - evidence: hub/index.html line 189 has target="_blank" rel="noopener". The iframe (lines 191-192) has title 'Procreate Brush Designer' and no sandbox attribute.
- **added**: skills/ state per DECISIONS D2 ('eight files, not nine')
  - evidence: Glob skills/** now returns 9 .skill.md files (adobe_firefly, adobe_suite_uxp, blender_python, hardware_compute, higgsfield_api, local_rag_orchestration, suno_audio, css_html_ui, ui_ux_intelligence). None is brush_designer, so D2's 'not yet done' still holds.
- **added**: Provenance of tools/brush-designer/
  - evidence: README.md line 212 maps tools/brush-designer/ (and agents/) to the 'Claude-Code' source repo.
