// textures.js - shape and grain images, the invert switches, and the thumbnail.
//
// F10 import: textures.shape / grain is {source: "embedded", width, height,
// png_b64} (the file's own PNG, untouched), {source: "bundled", ref,
// standin_png_b64: null} (the image ships inside Procreate; the server never
// makes one up, so neither does this panel), {source: "blank", ref} or
// {source: "none"}. F10 export: a replaced image goes as {png_b64}; the server
// keeps an 8-bit grey PNG as given and converts anything else, reporting
// `converted`. The thumbnail must be 1060x324.

import {el, clear} from './dom.js';
import {b64ToBytes, bytesToB64, pngInfo, describePng, isGrey8, blobFromB64} from './b64.js';
import {toast} from './ui.js';
import {ShapeGenerators} from './generators/shape.js';
import {GrainGenerators} from './generators/grain.js';

export const THUMB_SIZE = [1060, 324];
export const MAX_IMAGE_BYTES = 64 * 1024 * 1024;       // container cap `entry_bytes` (F3)
export const MAX_PIXELS = 8192 * 8192;

const ROLES = {
  shape: {title: 'Shape', invertKey: 'shapeInverted', generators: ShapeGenerators, size: 512,
    help: 'The stamp. White is paint unless Inverted is on.'},
  grain: {title: 'Grain', invertKey: 'textureInverted', generators: GrainGenerators, size: 1024,
    help: 'The texture the stroke is drawn through.'},
};

/** What to show for a role now: {kind, b64, label, replaced, info}. Pure given the doc. */
export function textureView(doc, role) {
  const replacement = doc.textureChange(role);
  if (replacement) {
    return {kind: 'image', b64: replacement.png_b64, replaced: true, info: replacement.info || null,
      label: `${replacement.how === 'generated' ? 'Generated' : 'Uploaded'}: ${replacement.label || ''}`.trim()};
  }
  const entry = (doc.textures || {})[role] || {source: 'none'};
  if (entry.png_b64) {
    return {kind: 'image', b64: entry.png_b64, replaced: false, info: entry.width ? {width: entry.width, height: entry.height} : null,
      label: entry.source === 'bundled-supplied' ? `Supplied copy of ${entry.ref}` : 'Embedded in the brush file'};
  }
  if (entry.source === 'bundled') return {kind: 'bundled', ref: entry.ref, replaced: false, label: `Ships inside Procreate: ${entry.ref}`};
  if (entry.source === 'blank') return {kind: 'blank', ref: entry.ref, replaced: false, label: 'Blank (no texture)'};
  return {kind: 'none', replaced: false, label: 'No image'};
}

export function thumbnailView(doc) {
  const t = doc.thumbnail();
  if (t.mode === 'omit') return {kind: 'omitted', label: 'The exported file will have no thumbnail.'};
  if (t.mode === 'replace') return {kind: 'image', b64: t.png_b64, replaced: true, label: 'Replacement thumbnail'};
  const original = doc.textures && doc.textures.thumbnail;
  if (original && original.png_b64) return {kind: 'image', b64: original.png_b64, replaced: false, label: 'Procreate’s own thumbnail'};
  if (original && original.present) return {kind: 'present', label: 'The brush has a thumbnail (not loaded).'};
  return {kind: 'none', label: 'The brush has no thumbnail.'};
}

/** Turn a canvas into {png_b64, width, height}, flattened on black (shape and grain are grey images). */
export async function canvasToReplacement(canvas, label) {
  const flat = document.createElement('canvas');
  flat.width = canvas.width; flat.height = canvas.height;
  const g = flat.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, flat.width, flat.height);
  g.drawImage(canvas, 0, 0);
  const blob = await new Promise((resolve) => flat.toBlob(resolve, 'image/png'));
  const bytes = new Uint8Array(await blob.arrayBuffer());
  const info = pngInfo(bytes);
  return {png_b64: bytesToB64(bytes), width: flat.width, height: flat.height, how: 'generated', label, info};
}

export function createTextures({getEngine} = {}) {
  let doc = null;
  let unsubscribe = null;
  let urls = [];
  const root = el('div', {class: 'textures'});

  function url(b64) {
    const u = URL.createObjectURL(blobFromB64(b64));
    urls.push(u);
    return u;
  }

  function imageBox(view, alt) {
    if (view.kind === 'image') return el('img', {class: 'tex-img', src: url(view.b64), alt});
    const text = {bundled: `Ships inside Procreate: ${view.ref || ''}. No image is available here.`, blank: 'Blank texture. Nothing to show.',
      none: 'No image.', omitted: 'No thumbnail will be written.', present: view.label}[view.kind] || view.label;
    return el('div', {class: `tex-placeholder tex-${view.kind}`, role: 'img', 'aria-label': text}, el('span', {text}));
  }

  async function readPng(file, {exact} = {}) {
    if (!file) return null;
    if (file.size > MAX_IMAGE_BYTES) { toast(`${file.name} is larger than 64 MiB.`, 'error'); return null; }
    const bytes = new Uint8Array(await file.arrayBuffer());
    const info = pngInfo(bytes);
    if (!info) { toast(`${file.name} is not a PNG file.`, 'error'); return null; }
    if (info.width * info.height > MAX_PIXELS) { toast(`${file.name} is larger than 8192×8192 pixels.`, 'error'); return null; }
    if (exact && (info.width !== exact[0] || info.height !== exact[1])) {
      toast(`The thumbnail must be ${exact[0]}×${exact[1]} pixels; this is ${info.width}×${info.height}.`, 'error');
      return null;
    }
    return {bytes, info};
  }

  function roleCard(role) {
    const cfg = ROLES[role];
    const view = textureView(doc, role);
    const fileInput = el('input', {type: 'file', accept: 'image/png', class: 'offscreen', id: `file-${role}`, 'aria-label': `Choose a PNG for the ${role}`,
      onchange: async (e) => {
        const picked = await readPng(e.target.files[0]);
        e.target.value = '';
        if (!picked) return;
        doc.setTexture(role, {png_b64: bytesToB64(picked.bytes), width: picked.info.width, height: picked.info.height,
          how: 'upload', label: describePng(picked.info), info: picked.info});
        toast(`${cfg.title} image replaced${isGrey8(picked.info) ? '' : '; the server will convert it to 8-bit grey on export'}.`, 'ok');
      }});
    const names = Object.keys(cfg.generators);
    const pick = el('select', {class: 'select', id: `gen-${role}`, 'aria-label': `Generator for the ${role}`}, names.map((n) => el('option', {value: n, text: n})));
    const genBtn = el('button', {class: 'btn', type: 'button', text: 'Generate', onclick: async () => {
      const canvas = document.createElement('canvas');
      canvas.width = cfg.size; canvas.height = cfg.size;
      const g = canvas.getContext('2d');
      g.fillStyle = '#000'; g.fillRect(0, 0, cfg.size, cfg.size);
      cfg.generators[pick.value](g, cfg.size, 12345);
      doc.setTexture(role, await canvasToReplacement(canvas, pick.value));
    }});
    const invert = doc.has(cfg.invertKey, 'main')
      ? el('label', {class: 'check'}, el('input', {type: 'checkbox', checked: doc.value(cfg.invertKey, 'main') === true,
        onchange: (e) => doc.set(cfg.invertKey, e.target.checked, {layer: 'main'})}), el('span', {text: `Inverted (${cfg.invertKey})`}))
      : null;
    const facts = view.kind === 'image' && view.info ? `${view.info.width}×${view.info.height}` : '';
    return el('section', {class: 'card tex-card'},
      el('h3', {text: cfg.title}),
      imageBox(view, `${cfg.title} image`),
      el('p', {class: 'small', text: [view.label, facts].filter(Boolean).join('. ')}),
      el('p', {class: 'small muted', text: cfg.help}),
      invert,
      el('div', {class: 'btn-row'},
        el('label', {class: 'btn', htmlFor: `file-${role}`, tabIndex: 0, role: 'button',
          onkeydown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); } }, text: 'Replace with a PNG…'}),
        view.replaced ? el('button', {class: 'btn', type: 'button', text: 'Use the original', onclick: () => doc.setTexture(role, null)}) : null),
      fileInput,
      el('div', {class: 'btn-row'}, pick, genBtn));
  }

  function thumbCard() {
    const view = thumbnailView(doc);
    const fileInput = el('input', {type: 'file', accept: 'image/png', class: 'offscreen', id: 'file-thumb', 'aria-label': 'Choose a 1060 by 324 PNG for the thumbnail',
      onchange: async (e) => {
        const picked = await readPng(e.target.files[0], {exact: THUMB_SIZE});
        e.target.value = '';
        if (picked) doc.setThumbnail({mode: 'replace', png_b64: bytesToB64(picked.bytes)});
      }});
    return el('section', {class: 'card tex-card tex-thumb'},
      el('h3', {text: 'Thumbnail'}),
      el('div', {class: 'thumb-stage'}, imageBox(view, 'Brush thumbnail')),
      el('p', {class: 'small', text: view.label}),
      el('p', {class: 'small muted', text: `Procreate shows this in the brush list. ${THUMB_SIZE[0]}×${THUMB_SIZE[1]} PNG. After an edit the old thumbnail no longer matches the brush (the export says so).`}),
      el('div', {class: 'btn-row'},
        el('label', {class: 'btn', htmlFor: 'file-thumb', tabIndex: 0, role: 'button',
          onkeydown: (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); } }, text: 'Replace…'}),
        doc.thumbnail().mode !== 'keep' ? el('button', {class: 'btn', type: 'button', text: 'Keep the original', onclick: () => doc.setThumbnail({mode: 'keep'})}) : null,
        doc.thumbnail().mode !== 'omit' ? el('button', {class: 'btn', type: 'button', text: 'Leave out', onclick: () => doc.setThumbnail({mode: 'omit'})}) : null),
      fileInput);
  }

  function render() {
    for (const u of urls) URL.revokeObjectURL(u);
    urls = [];
    clear(root);
    if (!doc) { root.append(el('p', {class: 'muted', text: 'Open a brush to see its images.'})); return; }
    root.append(roleCard('shape'), roleCard('grain'), thumbCard());
    if (getEngine) { const engine = getEngine(); if (engine && engine.refresh) engine.refresh(); }
  }

  return {
    el: root,
    setDoc(next) {
      if (unsubscribe) unsubscribe();
      doc = next;
      if (doc) unsubscribe = doc.subscribe((e) => {
        if (e.type === 'layer') return;
        if (e.keys.some((k) => k.startsWith('texture:') || k === 'shapeInverted' || k === 'textureInverted')) render();
      });
      render();
    },
  };
}

/** b64ToBytes re-exported for the selftest's replace-then-export check. */
export {b64ToBytes};
