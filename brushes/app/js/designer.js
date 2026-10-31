// designer.js - the Designer tab: opens a brush, then lays out the preview, the
// settings panels, textures, patch box and export around one doc (state.js).

import {el, clear, isTyping} from './dom.js';
import {createPanels} from './panels.js';
import {createTextures, thumbnailView} from './textures.js';
import {createPatchBox} from './patchbox.js';
import {createExportPanel} from './exporter.js';
import {createOpener, openLibraryBrush} from './opener.js';
import {createEngine} from './engine.js';
import {previewBadges} from './schema.js';
import {blobFromB64} from './b64.js';
import {confirmDialog, toast} from './ui.js';

export function createDesigner({schema, status, basket, dialog, goLibrary, onDocChange}) {
  let doc = null;
  let unsubscribe = null;
  let thumbUrl = null;
  let frame = 0;

  const root = el('div', {class: 'designer'});
  const engineCanvas = el('canvas', {class: 'engine-canvas', role: 'img', 'aria-label': 'Stroke preview'});
  const engineNote = el('p', {class: 'small muted engine-note'});
  const engine = createEngine(engineCanvas);
  engine.setBadges(previewBadges(schema));

  const panels = createPanels({schema, focusPatchBox: () => { patchSection.open = true; patchBox.focus(); }});
  const textures = createTextures();
  const patchBox = createPatchBox({schema, getDoc: () => doc});
  const exportPanel = createExportPanel({getDoc: () => doc, basket});

  const guardDirty = async () => {
    if (!doc || !doc.dirty) return true;
    return confirmDialog(dialog, {title: 'Discard your edits?', message: `${doc.dirtyCount} edit(s) to the open brush have not been exported. Opening another brush drops them.`, yes: 'Discard and open', no: 'Keep editing'});
  };
  const opener = createOpener({status, guardDirty, onDoc: (next) => setDoc(next), goLibrary});

  // ── the bar above the workspace ──
  const nameOut = el('h2', {class: 'brush-name', id: 'brush-name'});
  const metaOut = el('p', {class: 'small muted brush-meta'});
  const dirtyOut = el('span', {class: 'dirty', role: 'status'});
  const undoBtn = el('button', {class: 'btn', type: 'button', text: 'Undo', onclick: () => doc && doc.undo()});
  const redoBtn = el('button', {class: 'btn', type: 'button', text: 'Redo', onclick: () => doc && doc.redo()});
  const resetBtn = el('button', {class: 'btn', type: 'button', text: 'Reset all', onclick: async () => {
    if (!doc || !doc.dirty) return;
    const ok = await confirmDialog(dialog, {title: 'Reset all edits?', message: 'Every setting, image and thumbnail change goes back to the opened brush. Undo brings them back.', yes: 'Reset all', no: 'Cancel'});
    if (ok) doc.resetAll();
  }});
  const openDetails = el('details', {class: 'open-another'}, el('summary', {class: 'btn', text: 'Open another brush'}));
  const bar = el('div', {class: 'brush-bar'},
    el('div', {class: 'brush-id'}, nameOut, metaOut),
    el('div', {class: 'brush-actions'}, dirtyOut, undoBtn, redoBtn, resetBtn));

  // ── the side column ──
  const section = (title, body, open) => el('details', {class: 'side-section', open}, el('summary', {text: title}), body);
  const previewSection = section('Preview', el('div', {class: 'preview-box'}, engineCanvas, engineNote), true);
  const textureSection = section('Textures', textures.el, true);
  const patchSection = section('Patch from Claude', patchBox.el, false);
  const exportSection = section('Export', exportPanel.el, true);
  for (const [id, s] of [['sec-preview', previewSection], ['sec-textures', textureSection], ['sec-patch', patchSection], ['sec-export', exportSection]]) s.id = id;
  const jump = el('nav', {class: 'jump', 'aria-label': 'Jump to'},
    [['Settings', '#settings'], ['Textures', '#sec-textures'], ['Patch', '#sec-patch'], ['Export', '#sec-export']]
      .map(([text, href]) => el('a', {class: 'btn btn-small', href, text, onclick: (e) => {
        e.preventDefault();
        const target = root.querySelector(href);
        if (target) { if (target.tagName === 'DETAILS') target.open = true; target.scrollIntoView({block: 'start'}); }
      }})));
  const workspace = el('div', {class: 'workspace', hidden: true},
    el('aside', {class: 'side'}, previewSection, textureSection, patchSection, exportSection),
    el('div', {class: 'main-col', id: 'settings'}, panels.el));

  const welcome = el('div', {class: 'welcome'}, el('h2', {text: 'Open a brush'}), opener.el);
  root.append(bar, openDetails, jump, welcome, workspace);
  bar.hidden = true; jump.hidden = true; openDetails.hidden = true;

  // ── wiring ──
  function setDoc(next) {
    if (unsubscribe) unsubscribe();
    doc = next;
    unsubscribe = doc.subscribe(onEvent);
    panels.setDoc(doc); textures.setDoc(doc); patchBox.setDoc(doc);
    bar.hidden = false; jump.hidden = false; openDetails.hidden = false; workspace.hidden = false;
    welcome.hidden = true;
    clear(openDetails); openDetails.append(el('summary', {class: 'btn', text: 'Open another brush'}), opener.el);
    nameOut.textContent = doc.name || 'Untitled brush';
    metaOut.textContent = `${doc.era || 'unknown era'} · ${doc.meta.key_count ?? '?'} keys · ${doc.hasSub ? 'dual brush' : 'single brush'} · ${originText()}`;
    if (doc.warnings.length) toast(doc.warnings.slice(0, 2).join(' '), 'warn', 8000);
    onEvent({type: 'open', keys: []});
    if (onDocChange) onDocChange(doc);
    queuePreview();
  }

  function originText() {
    const o = doc.origin;
    return o.kind === 'library' ? `library ${o.id}` : o.kind === 'new' ? `new ${o.era} brush` : `file ${o.filename || ''}`;
  }

  function onEvent(event) {
    undoBtn.disabled = !doc.canUndo; redoBtn.disabled = !doc.canRedo;
    undoBtn.title = doc.undoLabel ? `Undo: ${doc.undoLabel}` : 'Nothing to undo';
    redoBtn.title = doc.redoLabel ? `Redo: ${doc.redoLabel}` : 'Nothing to redo';
    resetBtn.disabled = !doc.dirty;
    const n = doc.dirtyCount;
    dirtyOut.textContent = n ? `Edited: ${n} change${n === 1 ? '' : 's'}, not exported` : 'Unedited';
    dirtyOut.classList.toggle('is-dirty', n > 0);
    const liveName = doc.value('name', 'main');
    if (typeof liveName === 'string' && liveName) nameOut.textContent = liveName;
    queuePreview();
  }

  function queuePreview() {
    if (frame) return;
    frame = requestAnimationFrame(() => { frame = 0; renderPreview(); });
  }

  async function renderPreview() {
    if (!doc) return;
    if (thumbUrl) { URL.revokeObjectURL(thumbUrl); thumbUrl = null; }
    const view = thumbnailView(doc);
    if (view.kind === 'image') thumbUrl = URL.createObjectURL(blobFromB64(view.b64));
    const box = engineCanvas.parentElement;
    const result = await engine.render(doc.effective('main'), {
      width: Math.min(box.clientWidth || 360, 640), era: doc.era, name: doc.name, thumbnailUrl: thumbUrl,
      dark: window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches,
      shapeInfo: (doc.textures || {}).shape, grainInfo: (doc.textures || {}).grain,
    });
    engineNote.textContent = `Preview engine: ${engine.name}. ${result.drew === 'thumbnail' ? 'This is the picture stored in the brush file.' : ''}`;
  }

  document.addEventListener('keydown', (event) => {
    if (!doc || root.closest('[hidden]') || isTyping(event)) return;
    const mod = event.ctrlKey || event.metaKey;
    if (!mod) return;
    const key = event.key.toLowerCase();
    if (key === 'z' && !event.shiftKey) { event.preventDefault(); doc.undo(); }
    else if ((key === 'z' && event.shiftKey) || key === 'y') { event.preventDefault(); doc.redo(); }
  });
  window.addEventListener('beforeunload', (event) => { if (doc && doc.dirty) { event.preventDefault(); event.returnValue = ''; } });
  window.addEventListener('resize', queuePreview);
  const scheme = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  if (scheme && scheme.addEventListener) scheme.addEventListener('change', queuePreview);

  return {
    el: root, panels, textures, patchBox, exportPanel, opener, engine,
    getDoc: () => doc,
    setDoc,
    guardDirty,
    async openLibrary(id) { await opener.openLibrary(id); },
    async openLibraryDirect(id) { if (!(await guardDirty())) return null; const next = await openLibraryBrush(id); setDoc(next); return next; },
  };
}
