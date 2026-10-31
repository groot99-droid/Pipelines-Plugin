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
// Formats here: brush and brushset. gbr and kit are the same call with another
// `format` (3c).

import {el, clear, uid} from './dom.js';
import {api, ApiError} from './api.js';
import {sha256Hex} from './b64.js';
import {toast, downloadBlob, copyText} from './ui.js';

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

export function exportRequest({format, name, brushes, dryRun}) {
  const request = {format, dry_run: !!dryRun, brushes};
  if (name) request.name = name;
  return request;
}

/** The command that checks a saved file (CONTRACTS F11). */
export function inspectCommand(filename) {
  return `python -I brushes/pipeline/brush_file.py inspect "${filename}"`;
}

/** Dry run, then the real export; saves the file. Resolves to the result shown in the panel. */
export async function runExport({format, name, brushes, save = true}) {
  const dry = await api.exportBrush(exportRequest({format, name, brushes, dryRun: true}));
  const real = await api.exportBrush(exportRequest({format, name, brushes, dryRun: false}));
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

  async function guarded(fn) {
    if (busy) return;
    busy = true; brushBtn.disabled = true; setBtn.disabled = true;
    clear(resultBox);
    resultBox.append(el('p', {class: 'muted', text: 'Building the export…'}));
    try { await fn(); } catch (error) { showError(error); } finally { busy = false; brushBtn.disabled = false; setBtn.disabled = false; }
  }

  function showError(error) {
    clear(resultBox);
    const rejected = error.data && Array.isArray(error.data.rejected) ? error.data.rejected : [];
    resultBox.append(el('div', {class: 'notice notice-bad', role: 'alert'},
      el('strong', {text: `Export refused: ${error.code || 'error'}`}),
      el('p', {text: error.message || String(error)}),
      error.hint ? el('p', {class: 'small', text: error.hint}) : null,
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
      showResult(result, basket.items.some((i) => i.kind === 'edited'));
      if (onExported) onExported(result);
    });
  }

  function showResult(result, edited) {
    clear(resultBox);
    const report = result.report || {};
    const members = report.members || [];
    const states = members.reduce((acc, m) => { acc[m.state] = (acc[m.state] || 0) + 1; return acc; }, {});
    const command = inspectCommand(result.filename);
    const allVerbatim = members.length > 0 && members.every((m) => m.state === 'verbatim');
    resultBox.append(el('div', {class: 'notice notice-ok'},
      el('strong', {text: `Saved ${result.filename}`}),
      el('p', {class: 'small', text: `${result.size.toLocaleString()} bytes. sha256 ${result.sha256 ? result.sha256.slice(0, 16) + '…' : '(not computed: needs a secure context)'}. `
        + (result.shaMatches === true ? 'The saved bytes match the server’s hash.' : result.shaMatches === false ? 'THE SAVED BYTES DO NOT MATCH THE SERVER’S HASH.' : '')}),
      allVerbatim ? el('p', {text: 'Nothing was changed: every member is the original, byte for byte.'}) : null,
      !allVerbatim && edited ? el('p', {text: 'Edited settings were written into the original archive; everything else is kept as it was.'}) : null,
      el('p', {class: 'small muted', text: 'Not proven to open in Procreate. See brushes/device-tests/ for the iPad sittings.'})));
    if (report.warnings && report.warnings.length) {
      resultBox.append(el('div', {class: 'notice notice-warn'}, el('strong', {text: `Warnings (${report.warnings.length})`}),
        el('ul', {}, report.warnings.map((w) => el('li', {text: w})))));
    }
    for (const b of report.brushes || []) {
      const applied = Object.keys(b.applied || {});
      resultBox.append(el('p', {class: 'small', text: `${b.name || 'Brush'} (${b.era || '?'}): ${applied.length} setting(s) changed${b.rejected && b.rejected.length ? `, ${b.rejected.length} rejected` : ''}.`}));
    }
    resultBox.append(el('details', {class: 'members'}, el('summary', {text: `Members (${members.length}): ${Object.entries(states).map(([s, n]) => `${n} ${s}`).join(', ')}`}),
      el('table', {class: 'table'}, el('thead', {}, el('tr', {}, el('th', {text: 'Path'}), el('th', {text: 'Size'}), el('th', {text: 'State'}))),
        el('tbody', {}, members.map((m) => el('tr', {}, el('td', {class: 'mono', text: m.path}), el('td', {text: String(m.size)}), el('td', {text: m.state})))))));
    resultBox.append(el('div', {class: 'cmd'},
      el('p', {class: 'small', text: 'To check the file, run this from the repository root (use the folder the browser saved it to):'}),
      el('pre', {class: 'mono', text: command}),
      el('button', {class: 'btn btn-small', type: 'button', text: 'Copy command', onclick: async () => toast((await copyText(command)) ? 'Command copied.' : 'Copy failed: select the text instead.', 'info')})));
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
      el('div', {class: 'btn-row'}, brushBtn)),
    el('div', {class: 'card'}, el('h3', {text: 'A set'}),
      el('div', {class: 'field'}, el('label', {htmlFor: 'set-name', text: 'Set name'}), nameInput),
      basketBox,
      el('div', {class: 'btn-row'},
        el('button', {class: 'btn', type: 'button', text: 'Add the open brush (with edits)', onclick: () => {
          const doc = getDoc(); if (!doc) { toast('Open a brush first.', 'warn'); return; }
          basket.addDoc(doc); toast('Added to the set.', 'ok'); }}),
        el('button', {class: 'btn btn-quiet', type: 'button', text: 'Empty the set', onclick: () => basket.clear()}),
        setBtn)),
    resultBox);
  return {el: root, exportOne, exportSet};
}
