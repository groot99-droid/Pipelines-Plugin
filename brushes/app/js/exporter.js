// exporter.js - build the export request (F10 "Export request"), run it, save
// the file, show what the server says.
//
// The app sends ONLY what changed: `changes` (the doc's patch), `textures`
// ({keep} or {png_b64}) and `thumbnail`. The base is original bytes: a library
// id, or the members of an opened file (F3 "Export"). Python owns decode,
// encode and zip. An export is a dry run first (the server's report lists
// every member as verbatim / re-encoded / replaced / dropped and the warnings
// in words), then the real call, whose X-ROSW-Export header carries the size
// and sha256 that the saved bytes are checked against.
//
// Formats: brush, brushset, gbr (the shape as a GIMP brush tip) and kit (a zip
// of pictures and a recipe for other apps); `extra` carries the fields only
// those two take (`spacing`, `files`). The app's own source zip is a plain GET.
// What each file is for: kit.js FORMAT_NOTES.

import {el, clear, uid} from './dom.js';
import {api, ApiError} from './api.js';
import {sha256Hex} from './b64.js';
import {toast, downloadBlob, copyText} from './ui.js';
import {FORMAT_NOTES, listZip} from './kit.js';
import {buildKitFiles} from './kit-build.js';
import {schemaIndex} from './schema-load.js';

/** One entry of `brushes[]` for a doc. */
export function brushSpec(doc) {
  const spec = {
    base: doc.origin.kind === 'library' ? {library_id: doc.libraryId || doc.origin.id} : doc.base,
    changes: doc.patch('main'),
    mode: 'strict',
  };
  const textures = {};
  for (const role of ['shape', 'grain']) {
    const replacement = doc.textureChange(role);
    if (replacement) textures[role] = {png_b64: replacement.png_b64};
  }
  if (Object.keys(textures).length) spec.textures = textures;
  const thumb = doc.thumbnail();
  if (thumb.mode === 'omit') spec.thumbnail = {omit: true};
  else if (thumb.mode === 'replace') spec.thumbnail = {png_b64: thumb.png_b64};
  else spec.thumbnail = {keep: true};
  if (doc.hasSub) {
    const subChanges = doc.patch('sub');
    if (Object.keys(subChanges).length) spec.sub = {changes: subChanges};
  }
  return spec;
}

export function exportRequest({format, name, brushes, dryRun, extra}) {
  const request = {format, dry_run: !!dryRun, brushes, ...(extra || {})};
  if (name) request.name = name;
  return request;
}

/** The command that checks a saved file (CONTRACTS F11). */
export function inspectCommand(filename) {
  return `python -I brushes/pipeline/brush_file.py inspect "${filename}"`;
}

/** Dry run, then the real export; saves the file. Resolves to the result shown in the panel. */
export async function runExport({format, name, brushes, save = true, extra}) {
  const dry = await api.exportBrush(exportRequest({format, name, brushes, dryRun: true, extra}));
  const real = await api.exportBrush(exportRequest({format, name, brushes, dryRun: false, extra}));
  if (real.kind !== 'file') throw new ApiError('parse', 'The export answered with a report, not a file.');
  const bytes = new Uint8Array(await real.blob.arrayBuffer());
  const sha = await sha256Hex(bytes);
  const result = {
    filename: real.filename, size: bytes.length, sha256: sha, info: real.info, report: dry.report,
    shaMatches: real.info && sha ? real.info.sha256 === sha : null,
    sizeMatches: real.info ? real.info.size === bytes.length : null,
    bytes,
  };
  if (save) downloadBlob(real.blob, real.filename);
  return result;
}

/** Export the basket as one .brushset (dry run, then the real call). Saves unless `save` is false. */
export function exportBasket({basket, name, save = true}) {
  if (!basket.items.length) throw new ApiError('bad_argument', 'The set is empty.');
  return runExport({format: 'brushset', name, brushes: basket.items.map((i) => i.spec), save});
}

/** The app's own source as a zip (GET /api/app-source.zip), with its entry list. Saves unless `save` is false. */
export async function exportSource({save = true} = {}) {
  const {blob, filename} = await api.appSourceZip();
  const bytes = new Uint8Array(await blob.arrayBuffer());
  const entries = listZip(bytes);
  if (save) downloadBlob(blob, filename);
  return {filename, size: bytes.length, sha256: await sha256Hex(bytes), info: null, shaMatches: null, sizeMatches: null, bytes,
    report: {members: entries.map((e) => ({path: e.name, size: e.size, state: e.method === 0 ? 'stored' : 'compressed'})), warnings: [], brushes: []}};
}

/**
 * Show a finished export in `box`: file name, size, sha256 (with the server's
 * check), what the format is for, what it holds (the server's member list),
 * warnings, and for .brush / .brushset the command that checks the file.
 *   opts.what    'brush' | 'brushset' | 'gbr' | 'kit' | 'source' (kit.js FORMAT_NOTES)
 *   opts.edited  true when edited settings went in
 *   opts.notes   extra lines (for example what a kit left out)
 */
export function renderExportResult(box, result, {what = 'brush', edited = false, notes = []} = {}) {
  clear(box);
  const info = FORMAT_NOTES[what] || FORMAT_NOTES.brush;
  const report = result.report || {};
  const members = report.members || [];
  const states = members.reduce((acc, m) => { acc[m.state] = (acc[m.state] || 0) + 1; return acc; }, {});
  const allVerbatim = members.length > 0 && members.every((m) => m.state === 'verbatim');
  const sha = result.sha256;
  box.append(el('div', {class: 'notice notice-ok'},
    el('strong', {text: `Saved ${result.filename}`}),
    el('p', {class: 'small', text: `${result.size.toLocaleString()} bytes.`}),
    el('p', {class: 'small'}, 'sha256 ', el('code', {class: 'sha', text: sha || '(not computed: needs a secure context)'}),
      result.shaMatches === true ? ' The saved bytes match the server’s hash.' : result.shaMatches === false ? ' THE SAVED BYTES DO NOT MATCH THE SERVER’S HASH.' : ''),
    el('p', {class: 'small'}, el('strong', {text: `${info.title}: `}), info.what, ' ', info.use),
    el('p', {class: 'small', text: `Holds: ${info.contains}`}),
    what === 'brush' || what === 'brushset' ? (allVerbatim ? el('p', {text: 'Nothing was changed: every member is the original, byte for byte.'})
      : edited ? el('p', {text: 'Edited settings were written into the original archive; everything else is kept as it was.'}) : null) : null,
    ...notes.map((n) => el('p', {class: 'small', text: n})),
    what === 'brush' || what === 'brushset' ? el('p', {class: 'small muted', text: 'Not proven to open in Procreate. See brushes/device-tests/ for the iPad sittings.'}) : null));
  if (report.warnings && report.warnings.length) {
    box.append(el('div', {class: 'notice notice-warn'}, el('strong', {text: `Warnings (${report.warnings.length})`}),
      el('ul', {}, report.warnings.map((w) => el('li', {text: w})))));
  }
  for (const b of report.brushes || []) {
    const applied = Object.keys(b.applied || {});
    box.append(el('p', {class: 'small', text: `${b.name || 'Brush'} (${b.era || '?'}): ${applied.length} setting(s) changed${b.rejected && b.rejected.length ? `, ${b.rejected.length} rejected` : ''}.`}));
  }
  box.append(el('details', {class: 'members', open: what === 'kit' || what === 'gbr'}, el('summary', {text: `Contents (${members.length}): ${Object.entries(states).map(([s, n]) => `${n} ${s}`).join(', ')}`}),
    el('table', {class: 'table'}, el('thead', {}, el('tr', {}, el('th', {text: 'Path'}), el('th', {text: 'Size'}), el('th', {text: 'State'}))),
      el('tbody', {}, members.map((m) => el('tr', {}, el('td', {class: 'mono', text: m.path}), el('td', {text: String(m.size)}), el('td', {text: m.state})))))));
  if (what === 'brush' || what === 'brushset') {
    const command = inspectCommand(result.filename);
    box.append(el('div', {class: 'cmd'},
      el('p', {class: 'small', text: 'To check the file, run this from the repository root (use the folder the browser saved it to):'}),
      el('pre', {class: 'mono', text: command}),
      el('button', {class: 'btn btn-small', type: 'button', text: 'Copy command', onclick: async () => toast((await copyText(command)) ? 'Command copied.' : 'Copy failed: select the text instead.', 'info')})));
  }
}

/** A set in the making: library brushes and edited copies, exported as one .brushset. */
export function createBasket() {
  const items = [];
  const listeners = new Set();
  const notify = () => listeners.forEach((fn) => fn());
  return {
    items,
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
    addLibrary(id, label) {
      if (items.some((i) => i.key === `lib:${id}`)) return false;
      items.push({key: `lib:${id}`, label: label || id, spec: {base: {library_id: id}, changes: {}, mode: 'strict'}, kind: 'library'});
      notify();
      return true;
    },
    addDoc(doc) {
      items.push({key: `doc:${uid('d')}`, label: `${doc.value('name', 'main') || doc.name || 'Untitled'} (edited copy)`, spec: brushSpec(doc), kind: 'edited'});
      notify();
    },
    remove(key) { const i = items.findIndex((x) => x.key === key); if (i >= 0) { items.splice(i, 1); notify(); } },
    clear() { items.length = 0; notify(); },
  };
}

export function createExportPanel({getDoc, basket, onExported}) {
  const root = el('div', {class: 'export'});
  const nameInput = el('input', {type: 'text', class: 'text', id: 'set-name', value: 'My brush set', maxLength: 120, 'aria-label': 'Set name'});
  const resultBox = el('div', {class: 'export-result', 'aria-live': 'polite'});
  const brushBtn = el('button', {class: 'btn btn-primary', type: 'button', text: 'Export .brush', onclick: () => exportOne()});
  const setBtn = el('button', {class: 'btn', type: 'button', text: 'Export .brushset', onclick: () => exportSet()});
  const basketBox = el('div', {class: 'basket'});
  let busy = false;
  const setBusy = (on) => { for (const b of [brushBtn, setBtn, gbrBtn, kitBtn, srcBtn]) b.disabled = on; };

  async function guarded(fn) {
    if (busy) return;
    busy = true; setBusy(true);
    clear(resultBox);
    resultBox.append(el('p', {class: 'muted', text: 'Building the export…'}));
    try { await fn(); } catch (error) { showError(error); } finally { busy = false; setBusy(false); }
  }

  function showError(error) {
    clear(resultBox);
    const rejected = error.data && Array.isArray(error.data.rejected) ? error.data.rejected : [];
    resultBox.append(el('div', {class: 'notice notice-bad', role: 'alert'},
      el('strong', {text: `Export refused: ${error.code || 'error'}`}),
      el('p', {text: error.message || String(error)}),
      error.hint ? el('p', {class: 'small', text: error.hint}) : null,
      /image inside the drawing app/.test(error.message || '') ? el('p', {class: 'small', text: 'This brush’s shape ships inside Procreate, so there is no picture to write. Replace the shape in the Textures section (upload or generate one) and export again.'}) : null,
      rejected.length ? el('ul', {}, rejected.map((r) => el('li', {text: `${r.key}: ${r.code}${r.reason ? ` - ${r.reason}` : ''}`}))) : null));
  }

  async function exportOne() {
    const doc = getDoc();
    if (!doc) { toast('Open a brush first.', 'warn'); return; }
    await guarded(async () => {
      const result = await runExport({format: 'brush', brushes: [brushSpec(doc)]});
      showResult(result, doc.dirty);
      if (onExported) onExported(result);
    });
  }

  async function exportSet() {
    const name = nameInput.value.trim();
    if (!name) { toast('Give the set a name.', 'warn'); nameInput.focus(); return; }
    if (!basket.items.length) { toast('Add brushes to the set first.', 'warn'); return; }
    await guarded(async () => {
      const result = await runExport({format: 'brushset', name, brushes: basket.items.map((i) => i.spec)});
      showResult(result, basket.items.some((i) => i.kind === 'edited'), 'brushset');
      if (onExported) onExported(result);
    });
  }

  function showResult(result, edited, what = 'brush', notes = []) {
    renderExportResult(resultBox, result, {what, edited, notes});
  }

  // ── the other formats: .gbr, the Universal Kit, the app's source ──
  const spacingInput = el('input', {type: 'number', class: 'num', id: 'gbr-spacing', min: 1, max: 1000, step: 1, value: 10, inputMode: 'numeric', 'aria-label': 'GIMP brush spacing in percent'});
  const withBrush = el('input', {type: 'checkbox', id: 'kit-brush', class: 'switch'});
  const gbrBtn = el('button', {class: 'btn', type: 'button', text: 'Export .gbr', onclick: () => exportGbr()});
  const kitBtn = el('button', {class: 'btn', type: 'button', text: 'Export Universal Kit', onclick: () => exportKit()});
  const srcBtn = el('button', {class: 'btn', type: 'button', text: 'Download app source', onclick: () => exportAppSource()});

  const spacingValue = () => {
    const n = Number(spacingInput.value);
    return Number.isInteger(n) && n >= 1 && n <= 1000 ? n : null;
  };

  async function gbrFor(doc, spacing) {
    return runExport({format: 'gbr', brushes: [brushSpec(doc)], extra: {spacing}, save: false});
  }

  async function exportGbr() {
    const doc = getDoc();
    if (!doc) { toast('Open a brush first.', 'warn'); return; }
    const spacing = spacingValue();
    if (spacing === null) { toast('Spacing is a whole number from 1 to 1000.', 'warn'); spacingInput.focus(); return; }
    await guarded(async () => {
      const result = await runExport({format: 'gbr', brushes: [brushSpec(doc)], extra: {spacing}});
      showResult(result, doc.dirty, 'gbr', [`Spacing ${spacing}% of the brush width.`]);
      if (onExported) onExported(result);
    });
  }

  async function exportKit() {
    const doc = getDoc();
    if (!doc) { toast('Open a brush first.', 'warn'); return; }
    const spacing = spacingValue() || 10;
    await guarded(async () => {
      let gbrBytes = null;
      try { gbrBytes = (await gbrFor(doc, spacing)).bytes; } catch (error) {
        if (!['bad_argument'].includes(error.code)) throw error;       // a bundled shape: the kit goes without a .gbr
      }
      const schema = await schemaIndex().catch(() => null);
      const kit = await buildKitFiles(doc, {schema, gbrBytes, gbrSpacing: spacing});
      const brushes = withBrush.checked ? [brushSpec(doc)] : [];
      const result = await runExport({format: 'kit', name: doc.value('name', 'main') || doc.name || 'kit', brushes, extra: {files: kit.files}});
      showResult(result, doc.dirty, 'kit', kit.notes);
      if (onExported) onExported(result);
    });
  }

  async function exportAppSource() {
    await guarded(async () => {
      const result = await exportSource();
      showResult(result, false, 'source');
    });
  }

  function renderBasket() {
    clear(basketBox);
    if (!basket.items.length) {
      basketBox.append(el('p', {class: 'muted small', text: 'The set is empty. Add brushes from the Library tab, or add the open brush with its edits.'}));
      return;
    }
    basketBox.append(el('ol', {class: 'basket-list'}, basket.items.map((item) =>
      el('li', {}, el('span', {text: item.label}), el('button', {class: 'btn btn-small btn-quiet', type: 'button', text: 'Remove',
        'aria-label': `Remove ${item.label} from the set`, onclick: () => basket.remove(item.key)})))));
  }
  basket.subscribe(renderBasket);
  renderBasket();

  root.append(
    el('div', {class: 'card'}, el('h3', {text: 'This brush'}),
      el('p', {class: 'small muted', text: 'Saves a .brush. A brush nobody edited is saved as it was read.'}),
      el('div', {class: 'btn-row'}, brushBtn),
      el('p', {class: 'small muted', text: FORMAT_NOTES.brush.use})),
    el('div', {class: 'card'}, el('h3', {text: 'A set'}),
      el('div', {class: 'field'}, el('label', {htmlFor: 'set-name', text: 'Set name'}), nameInput),
      basketBox,
      el('div', {class: 'btn-row'},
        el('button', {class: 'btn', type: 'button', text: 'Add the open brush (with edits)', onclick: () => {
          const doc = getDoc(); if (!doc) { toast('Open a brush first.', 'warn'); return; }
          basket.addDoc(doc); toast('Added to the set.', 'ok'); }}),
        el('button', {class: 'btn btn-quiet', type: 'button', text: 'Empty the set', onclick: () => basket.clear()}),
        setBtn),
      el('p', {class: 'small muted', text: FORMAT_NOTES.brushset.use})),
    el('div', {class: 'card'}, el('h3', {text: 'For other apps'}),
      el('p', {class: 'small muted', text: 'These are plain pictures and a GIMP brush tip, not Procreate files. They keep the shape and the grain image; the dynamics, taper and the rest stay in the recipe as words.'}),
      el('div', {class: 'field'}, el('label', {htmlFor: 'gbr-spacing', text: 'GIMP spacing, percent of the brush width'}), spacingInput),
      el('div', {class: 'btn-row'}, gbrBtn, kitBtn,
        el('label', {class: 'check', htmlFor: 'kit-brush'}, withBrush, el('span', {text: 'Put the .brush in the kit too'}))),
      el('details', {class: 'format-notes'}, el('summary', {text: 'What these files are for'}),
        ...['gbr', 'kit'].map((id) => el('div', {}, el('h4', {text: FORMAT_NOTES[id].title}), el('p', {class: 'small', text: `${FORMAT_NOTES[id].what} ${FORMAT_NOTES[id].contains} ${FORMAT_NOTES[id].use}`}))))),
    el('div', {class: 'card'}, el('h3', {text: 'This app'}),
      el('p', {class: 'small muted', text: `${FORMAT_NOTES.source.what} ${FORMAT_NOTES.source.contains}`}),
      el('div', {class: 'btn-row'}, srcBtn)),
    resultBox);
  return {el: root, exportOne, exportSet, exportGbr, exportKit, exportAppSource};
}
