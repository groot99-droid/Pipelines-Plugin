// opener.js - the three ways to get a brush into the designer (F10):
//
//   library  GET  /api/brush/<id>/open     the original, decoded (409 library_missing without the files)
//   file     POST /api/import              a dropped or picked .brush / .brushset / .zip; a set answers
//                                          with a manifest and the page posts the file again with ?member=
//   new      POST /api/export (base null)  the server builds a brush from its donor template; the bytes
//                                          are decoded with /api/import so the panels show the real values
//
// An opened brush is a doc (state.js). A library brush keeps only {library_id}
// as its export base; a file keeps the members the server sent back.

import {el, clear} from './dom.js';
import {api, ApiError} from './api.js';
import {createDoc} from './state.js';
import {toast} from './ui.js';

export function docFromResponse(response, origin) {
  const fromLibrary = origin.kind === 'library';
  return createDoc({
    origin, name: response.name, era: response.era, settings: response.settings, sub: response.sub, meta: response.meta,
    textures: response.textures, libraryId: response.library_id || (fromLibrary ? origin.id : null),
    base: fromLibrary ? {library_id: origin.id} : response.base, warnings: response.warnings || [],
  });
}

export async function openLibraryBrush(id) {
  return docFromResponse(await api.openBrush(id, 'full'), {kind: 'library', id});
}

/** Import a file. Resolves to {doc} for one brush or {manifest} for a set. */
export async function importFile(file, member) {
  const response = await api.importFile(file, {member});
  if (response.kind === 'brushset') return {manifest: response};
  return {doc: docFromResponse(response, {kind: 'file', filename: file.name, member: member || response.member || null})};
}

/** A new brush from the donor template of `era`. */
export async function newBrush(era) {
  const made = await api.exportBrush({format: 'brush', dry_run: false, brushes: [{base: null, era, changes: {name: 'New brush'}}]});
  if (made.kind !== 'file') throw new ApiError('parse', 'The new-brush export did not answer with a file.');
  const file = new File([made.blob], made.filename, {type: 'application/octet-stream'});
  const response = await api.importFile(file, {});
  if (response.kind !== 'brush') throw new ApiError('parse', 'The new brush decoded as a set.');
  return docFromResponse(response, {kind: 'new', era, filename: made.filename});
}

export function createOpener({status, guardDirty, onDoc, goLibrary}) {
  const root = el('div', {class: 'opener'});
  const feedback = el('div', {class: 'opener-feedback', 'aria-live': 'polite'});
  const manifestBox = el('div', {class: 'manifest'});
  let busy = false;

  function showError(error) {
    clear(feedback);
    feedback.append(el('div', {class: 'notice notice-bad', role: 'alert'},
      el('strong', {text: error.code ? `${error.code}` : 'Error'}), el('p', {text: error.message || String(error)}),
      error.hint ? el('p', {class: 'small', text: error.hint}) : null));
  }

  async function run(job) {
    if (busy) return;
    busy = true;
    clear(feedback); feedback.append(el('p', {class: 'muted', text: 'Working…'}));
    try {
      const doc = await job();
      if (doc) { if (!(await guardDirty())) { clear(feedback); return; } clear(feedback); clear(manifestBox); onDoc(doc); }
    } catch (error) { showError(error); } finally { busy = false; }
  }

  function openFile(file, member) {
    const caps = status && status.caps ? status.caps.max_upload_bytes : 0;
    if (caps && file.size > caps) { showError({code: 'too_large', message: `${file.name} is larger than the server accepts (${caps.toLocaleString()} bytes).`}); return; }
    run(async () => {
      const result = await importFile(file, member);
      if (result.manifest) { showManifest(file, result.manifest); clear(feedback); return null; }
      return result.doc;
    });
  }

  function showManifest(file, manifest) {
    clear(manifestBox);
    manifestBox.append(el('h3', {text: `${manifest.name || file.name}: ${manifest.brush_count} brushes`}),
      manifest.warnings && manifest.warnings.length ? el('p', {class: 'small muted', text: manifest.warnings.slice(0, 3).join(' ')}) : null,
      el('ul', {class: 'manifest-list'}, manifest.brushes.map((b) =>
        el('li', {}, el('div', {}, el('strong', {text: b.name || '(unreadable)'}),
          el('span', {class: 'small muted', text: ` ${b.era || '?'} · ${b.key_count ?? '?'} keys · shape ${b.shape.source || '?'} · grain ${b.grain.source || '?'}${b.dual ? ' · dual' : ''}${b.library_id ? ' · in the library' : ''}`})),
        el('button', {class: 'btn btn-small', type: 'button', text: 'Open', disabled: !b.name, 'aria-label': `Open ${b.name || 'brush'} in the designer`,
          onclick: () => openFile(file, b.member)})))),
      manifest.skipped && manifest.skipped.length ? el('p', {class: 'small muted', text: `${manifest.skipped.length} entries were skipped.`}) : null);
  }

  const fileInput = el('input', {type: 'file', id: 'open-file', class: 'offscreen', accept: '.brush,.brushset,.zip',
    'aria-label': 'Choose a .brush or .brushset file', onchange: (e) => { const f = e.target.files[0]; e.target.value = ''; if (f) openFile(f); }});
  const drop = el('label', {class: 'dropzone', htmlFor: 'open-file', tabIndex: 0, role: 'button',
    onkeydown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); } }},
  el('strong', {text: 'Drop a .brush or .brushset here'}), el('span', {class: 'small muted', text: 'or tap to choose a file. It is read in memory and never written.'}));
  drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('is-over'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('is-over'));
  drop.addEventListener('drop', (e) => {
    e.preventDefault(); drop.classList.remove('is-over');
    const f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
    if (f) openFile(f);
  });

  const idInput = el('input', {type: 'text', class: 'text', id: 'open-id', placeholder: 'b_e9fe9907bee5', autocomplete: 'off', spellcheck: false,
    'aria-label': 'A library brush id'});
  const idForm = el('form', {class: 'inline-form', onsubmit: (e) => {
    e.preventDefault();
    const id = idInput.value.trim();
    if (!/^b_[0-9a-f]{12}$/.test(id)) { showError({code: 'bad_argument', message: 'A brush id looks like b_ followed by 12 hex digits.'}); return; }
    run(() => openLibraryBrush(id));
  }}, idInput, el('button', {class: 'btn', type: 'submit', text: 'Open by id'}));

  const eras = (status && status.new_brush_eras) || ['M220', 'E4'];
  const eraSelect = el('select', {class: 'select', id: 'new-era', 'aria-label': 'Era of the new brush'}, eras.map((e) => el('option', {value: e, text: e === (status && status.new_brush_era) ? `${e} (default)` : e})));

  root.append(
    el('div', {class: 'opener-grid'},
      el('section', {class: 'card'}, el('h3', {text: 'From the library'}),
        el('p', {class: 'small muted', text: 'Search the library, then open a brush in the designer. The original is never changed.'}),
        el('div', {class: 'btn-row'}, el('button', {class: 'btn btn-primary', type: 'button', text: 'Search the library', onclick: goLibrary})), idForm),
      el('section', {class: 'card'}, el('h3', {text: 'From a file'}), drop, fileInput),
      el('section', {class: 'card'}, el('h3', {text: 'New brush'}),
        el('p', {class: 'small muted', text: 'Starts from a real brush of the chosen era (the donor template). Its shape and grain are empty: add images in Textures.'}),
        el('div', {class: 'btn-row'}, eraSelect, el('button', {class: 'btn', type: 'button', text: 'Create', onclick: () => run(() => newBrush(eraSelect.value))})))),
    feedback, manifestBox);

  return {
    el: root, openLibrary: (id) => run(() => openLibraryBrush(id)),
    openFile, toastOnly: (m) => toast(m),
  };
}
