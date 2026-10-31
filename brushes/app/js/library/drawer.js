// library/drawer.js - the brush detail drawer (a <dialog>, so Escape closes it,
// focus stays inside and goes back to the card), and "Similar brushes".
//
// Detail: GET /api/brush/<id>?include=facets,tags,visual,textures,note.
// Similar: GET /api/brush/<id>/similar answers with the brush's own record
// (and what differs per neighbour). With "other sets only" on, the page sends
// that brush's settings to POST /api/similar with `where_not: set=<home set>`,
// because the GET route has no such switch (a gap noted in README).

import {el, clear} from '../dom.js';
import {copyText} from '../ui.js';
import {trim} from '../schema.js';
import {createCard, previewImage} from './card.js';

const AXES = ['medium', 'mark', 'texture', 'edge', 'motif', 'use'];
const INCLUDE = 'facets,tags,visual,textures,note';

function fmtValue(v) {
  if (typeof v === 'number') return trim(v, 4);
  if (typeof v === 'boolean') return v ? 'on' : 'off';
  if (v === null || v === undefined) return 'none';
  const text = String(v).replace(/^bundled:/, '').replace(/\.(jpg|png)$/i, '');
  return text.length > 26 ? `${text.slice(0, 24)}…` : text;
}

const REF_LABELS = {shape_ref: 'Shape image', grain_ref: 'Grain image'};

/** The line shown under a similar brush: its two biggest differences, with schema labels when known. */
export function differenceLine(differs, schema) {
  const picked = (differs || []).slice(0, 2).map((d) => {
    const row = schema && schema.byKey.get(d.key);
    return `${REF_LABELS[d.key] || (row ? row.label : d.key)}: ${fmtValue(d.query)} → ${fmtValue(d.other)}`;
  });
  return picked.length ? `Differs in ${picked.join('; ')}` : 'Same compared settings';
}

export function createDrawer({ctx, getSchema, openSet}) {
  const dialog = el('dialog', {class: 'drawer', 'aria-labelledby': 'drawer-title'});
  const stack = [];
  let current = null;
  let serial = 0;

  dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });

  function close() { if (dialog.open) dialog.close(); }

  function openBrush(id, {push = true} = {}) {
    if (push && current && current !== id) stack.push(current);
    current = id;
    show(id);
    if (!dialog.open) { if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', ''); }
  }

  function back() {
    const id = stack.pop();
    if (id) { current = id; show(id); }
  }

  async function show(id) {
    const mine = ++serial;
    clear(dialog);
    dialog.append(frame('Loading…', [el('p', {class: 'muted', role: 'status', text: 'Loading the brush…'})], null));
    let brush; let schema = null;
    try {
      [brush, schema] = await Promise.all([ctx.api.brush(id, INCLUDE), getSchema().catch(() => null)]);
    } catch (error) {
      if (mine !== serial) return;
      clear(dialog);
      dialog.append(frame('Brush not available', [el('div', {class: 'notice notice-bad', role: 'alert'}, el('strong', {text: error.code || 'error'}),
        el('p', {text: error.message}), error.hint ? el('p', {class: 'small', text: error.hint}) : null)], null));
      return;
    }
    if (mine !== serial) return;
    clear(dialog);
    dialog.append(frame(brush.name, body(brush, schema), brush));
  }

  function frame(title, children, brush) {
    return el('div', {class: 'drawer-frame'},
      el('div', {class: 'drawer-head'},
        stack.length ? el('button', {class: 'btn btn-small', type: 'button', text: 'Back', onclick: back}) : null,
        el('h2', {id: 'drawer-title', class: 'drawer-title', text: title}),
        el('button', {class: 'btn btn-small', type: 'button', text: 'Close', 'aria-label': 'Close the details', onclick: close})),
      brush ? el('div', {class: 'btn-row'},
        el('button', {class: 'btn btn-primary', type: 'button', text: 'Open in Designer', onclick: () => { close(); ctx.openInDesigner(brush.id); }}),
        el('button', {class: 'btn', type: 'button', text: 'Add to set', onclick: () => ctx.addToSet(brush.id, brush.name)})) : null,
      ...children);
  }

  function facts(brush) {
    const home = brush.home || {};
    const rows = [
      ['Library', `${brush.library}${brush.pack ? ` · pack ${brush.pack}` : ''}`],
      ['Home set', home.set_slug ? `${home.set_slug}${home.position ? `, number ${home.position}` : ''}` : '—'],
      ['Era', `${brush.era || '?'} (${brush.family || '?'} family), ${brush.key_count ?? '?'} keys`],
      ['Dual brush', brush.dual ? `yes: ${brush.dual.name || 'second brush'} (${brush.dual.era || '?'}), blend code ${brush.dual.blend_code ?? '?'}` : 'no'],
      ['Id', brush.id],
    ];
    return el('dl', {class: 'facts'}, rows.flatMap(([k, v]) => [el('dt', {text: k}), el('dd', {text: v})]));
  }

  function previews(brush) {
    const kinds = brush.preview_kinds || [];
    const live2 = () => current === brush.id;
    const strokeNote = brush.approximate ? 'An approximate drawing made by this tool, not Procreate’s own thumbnail.' : 'Procreate’s own stroke thumbnail.';
    return el('div', {class: 'drawer-previews'},
      kinds.includes('stroke') ? el('figure', {class: 'fig'}, el('div', {class: 'fig-stage'}, previewImage(ctx.api, brush.id, 'stroke', {className: 'fig-img', width: 530, height: 162, alt: `Stroke of ${brush.name}`, live: live2})),
        el('figcaption', {class: 'small muted', text: strokeNote})) : el('p', {class: 'muted small', text: 'This brush has no stroke preview.'}),
      el('div', {class: 'fig-row'},
        ...['shape', 'grain'].filter((k) => kinds.includes(k)).map((k) => el('figure', {class: 'fig fig-small'},
          el('div', {class: 'fig-stage'}, previewImage(ctx.api, brush.id, k, {className: 'fig-img', width: 128, height: 128, alt: `${k} of ${brush.name}`, live: live2})),
          el('figcaption', {class: 'small muted', text: k}))),
        ...['shape', 'grain'].filter((k) => !kinds.includes(k)).map((k) => el('p', {class: 'small muted', text: `No ${k} image stored${brush.textures && brush.textures[k] && brush.textures[k].source === 'bundled' ? ' (it ships inside Procreate)' : ''}.`}))));
  }

  function tagsBlock(brush) {
    const any = AXES.some((a) => (brush[`${a}_tags`] || []).length);
    return el('section', {class: 'drawer-sec'}, el('h3', {text: 'Tags and description'}),
      any ? el('dl', {class: 'facts'}, AXES.flatMap((a) => [el('dt', {text: a}), el('dd', {text: (brush[`${a}_tags`] || []).join(', ') || '—'})]))
        : el('p', {class: 'muted', text: `Not tagged yet (${brush.tag_state || 'untagged'}). Tags come from looking at the stroke previews; none have been written for this brush.`}),
      brush.visual ? el('p', {text: brush.visual}) : null,
      brush.visual ? el('p', {class: 'small muted', text: `This description was ${brush.visual_basis === 'described-not-measured' ? 'written from looking at the picture, not measured' : 'supplied'}.`}) : null);
  }

  function facetBlock(brush) {
    const f = brush.facets || {};
    const entries = Object.entries(f).filter(([, v]) => v !== null && v !== undefined);
    return el('details', {class: 'drawer-sec'}, el('summary', {text: `Facts measured from the settings (${entries.length})`}),
      el('dl', {class: 'facts small'}, entries.flatMap(([k, v]) => [el('dt', {text: k}), el('dd', {text: fmtValue(v)})])),
      (brush.facet_words || []).length ? el('p', {class: 'small muted', text: `Words the search sees: ${brush.facet_words.join(', ')}`}) : null);
  }

  function setsBlock(brush) {
    const sets = brush.sets || [];
    const others = (brush.duplicates || []).map((d) => d.set).filter((s) => !sets.some((x) => x.set_slug === s));
    return el('section', {class: 'drawer-sec'}, el('h3', {text: 'Where it lives'}),
      el('ul', {class: 'plain-list'}, sets.map((s) => el('li', {}, el('button', {class: 'btn btn-small', type: 'button', text: `${s.set_slug}${s.position ? ` (#${s.position})` : ''}`,
        onclick: () => { close(); openSet(s.set_slug); }})))),
      others.length ? el('p', {class: 'small muted', text: `A near-identical brush is also in: ${others.join(', ')}.`}) : null,
      brush.occurrences > sets.length ? el('p', {class: 'small muted', text: `${brush.occurrences} occurrences in the library.`}) : null);
  }

  function texturesBlock(brush) {
    const t = brush.textures || {};
    const line = (name, v) => (v ? `${name}: ${v.source}${v.bundled_name ? ` (${v.bundled_name})` : ''}${v.inverted ? ', inverted' : ''}` : `${name}: none`);
    return el('p', {class: 'small', text: [line('Shape', t.shape), line('Grain', t.grain), t.secondary ? 'The dual brush has its own shape and grain.' : null].filter(Boolean).join(' · ')});
  }

  function noteBlock(brush) {
    const n = brush.note || {};
    if (!n.path) return null;
    const where = `${n.path}${n.heading ? `, “${n.heading}”` : ''}${n.lines && n.lines[0] ? `, lines ${n.lines[0]} to ${n.lines[1]}` : ''}`;
    return el('p', {class: 'small'}, el('span', {class: 'muted', text: 'Vault note: '}), el('span', {class: 'mono', text: where}), ' ',
      el('button', {class: 'btn btn-small btn-quiet', type: 'button', text: 'Copy path', onclick: async () => ctx.toast((await copyText(n.path)) ? 'Path copied.' : 'Copy failed.', 'info')}));
  }

  function body(brush, schema) {
    const out = el('div', {class: 'drawer-body'});
    const similarBox = el('div', {class: 'similar-box', 'aria-live': 'polite'});
    const toggle = el('input', {type: 'checkbox', id: 'sim-other', class: 'switch', onchange: () => runSimilar()});
    let simSerial = 0;

    async function runSimilar() {
      const mine = ++simSerial;
      clear(similarBox);
      similarBox.append(el('p', {class: 'muted', text: 'Looking for similar brushes…'}));
      let result;
      try {
        if (toggle.checked) {
          const full = await ctx.api.brush(brush.id, 'settings');
          const home = (brush.home || {}).set_slug;
          result = await ctx.api.similarSettings({settings: full.settings, top: 13, where_not: home ? [`set=${home}`] : []});
          result.results = (result.results || []).filter((r) => r.brush_id !== brush.id).slice(0, 12);
        } else {
          result = await ctx.api.similar(brush.id, 12);
        }
      } catch (error) {
        if (mine !== simSerial) return;
        clear(similarBox);
        similarBox.append(el('div', {class: 'notice notice-bad', role: 'alert'}, el('strong', {text: error.code || 'error'}), el('p', {text: error.message}),
          el('button', {class: 'btn btn-small', type: 'button', text: 'Try again', onclick: runSimilar})));
        return;
      }
      if (mine !== simSerial) return;
      clear(similarBox);
      const list = result.results || [];
      similarBox.append(el('p', {class: 'small muted', text: `Method ${result.method || '?'}: numeric settings scaled by the library’s spread, on/off and choices equal or not, textures weighted extra. ${toggle.checked ? 'Compared using this brush’s settings; its own set is left out.' : ''}`}));
      if (!list.length) { similarBox.append(el('p', {class: 'muted', text: 'No similar brush found.'})); return; }
      similarBox.append(el('ul', {class: 'cards cards-small'}, list.map((r) => createCard(r, {
        api: ctx.api, live: () => current === brush.id, list: true, showScore: false, note: differenceLine(r.differs, schema),
        onOpen: (x) => openBrush(x.brush_id), onDesigner: (x) => { close(); ctx.openInDesigner(x.brush_id); }, onAdd: (x) => ctx.addToSet(x.brush_id, x.name)}))));
    }

    out.append(previews(brush), facts(brush), setsBlock(brush), tagsBlock(brush), texturesBlock(brush), facetBlock(brush), noteBlock(brush),
      el('section', {class: 'drawer-sec'}, el('h3', {text: 'Similar brushes'}),
        el('p', {class: 'small muted', text: 'Brushes whose settings are close to this one’s. It compares settings, not how a stroke looks.'}),
        el('div', {class: 'btn-row'},
          el('button', {class: 'btn btn-primary', type: 'button', text: 'Find similar brushes', onclick: runSimilar}),
          el('label', {class: 'check', htmlFor: 'sim-other'}, toggle, el('span', {text: 'Other sets only'}))),
        similarBox));
    return [out];
  }

  return {el: dialog, open: openBrush, close, get current() { return current; }};
}
