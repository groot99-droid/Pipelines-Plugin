// panels.js - the settings panels, generated from schema/silica_keys.json (F4).
//
// Fourteen tabs, the schema's group ids (F10 "The app"): ai, stroke,
// stabilization, taper, shape, grain, dynamics, pencil, wetmix, color,
// rendering, properties, materials, about. Each row shows the label, a control
// for its `ui` kind, the confidence badge, the preview-status badge (what the
// 3b stroke engine will do with the key), the default, the observed range, and
// a reset button once the key is edited.
//
// Seam for 3c: registerGroupPanel('ai', {mode: 'replace', render(container, ctx)})
// swaps what a tab shows; mode 'append' adds below the generated rows.

import {el, clear, uid} from './dom.js';
import {groupLayout, groupCounts, widgetFor, defaultText, observedText, searchText, unknownKeys,
  advise, CONFIDENCE_LABELS, PREVIEW_LABELS} from './schema.js';
import {buildControl} from './widgets.js';
import {toast} from './ui.js';

const registry = new Map();

/** mode: 'replace' draws the whole tab; 'append' draws below the rows. render(container, ctx). */
export function registerGroupPanel(groupId, {mode = 'append', render}) {
  registry.set(groupId, {mode, render});
}

registerGroupPanel('ai', {
  mode: 'replace',
  render(container, ctx) {
    container.append(
      el('div', {class: 'card'},
        el('h3', {text: 'AI assist'}),
        el('p', {text: 'The assistant arrives in a later phase. For now Claude is the assistant: it proposes a settings patch, and you paste it into the Patch box.'}),
        el('button', {class: 'btn', type: 'button', text: 'Go to the Patch box', onclick: () => ctx.focusPatchBox && ctx.focusPatchBox()}),
        el('div', {class: 'mount', id: 'ai-mount', 'data-mount': 'ai'})));
  },
});

registerGroupPanel('about', {
  mode: 'append',
  render(container, ctx) {
    const doc = ctx.doc;
    const facts = [
      ['Name', doc.name || '(none)'], ['Era', doc.era || 'unknown'], ['Class', (doc.meta.classes || []).join(' > ') || '—'],
      ['Keys in the archive', String(doc.meta.key_count ?? '—')], ['Archive sha256', doc.meta.archive_sha256 || '—'],
      ['Opened from', describeOrigin(doc.origin)], ['Library id', doc.libraryId || 'not in the library'],
    ];
    container.append(el('section', {class: 'card'}, el('h3', {text: 'This brush'}),
      el('dl', {class: 'facts'}, ...facts.flatMap(([k, v]) => [el('dt', {text: k}), el('dd', {text: v})]))));
    const unknown = unknownKeys(ctx.schema, doc.effective(ctx.layer));
    container.append(el('section', {class: 'card', id: 'unknown-keys'},
      el('h3', {text: `Unrecognised keys (${unknown.length})`}),
      el('p', {class: 'muted', text: unknown.length
        ? 'The brush holds these keys but the schema does not name them. They are shown read only and are written back exactly as read.'
        : 'None: every key of this brush is in the schema.'}),
      unknown.length ? el('dl', {class: 'facts mono'}, ...unknown.flatMap((k) => [el('dt', {text: k}), el('dd', {text: JSON.stringify(doc.value(k, ctx.layer))})])) : null));
  },
});

export function describeOrigin(origin) {
  if (!origin) return 'unknown';
  if (origin.kind === 'library') return `the library (${origin.id})`;
  if (origin.kind === 'new') return `a new ${origin.era || ''} brush from the donor template`.replace('  ', ' ');
  return `file ${origin.filename || ''}${origin.member ? ' (a brush of a set)' : ''}`;
}

export function createPanels({schema, focusPatchBox}) {
  let doc = null;
  let group = 'stroke';
  let filter = '';
  let allowUnverified = false;
  let unsubscribe = null;
  let rows = new Map();                         // key -> row component of the visible tab

  const filterInput = el('input', {type: 'search', class: 'text', id: 'panel-filter', placeholder: 'Filter settings by name or key',
    autocomplete: 'off', oninput: (e) => { filter = e.target.value.trim().toLowerCase(); renderTab(); renderTabs(); }});
  const unlock = el('input', {type: 'checkbox', id: 'unlock-unverified', onchange: (e) => { allowUnverified = e.target.checked; renderTab(); }});
  const layerBar = el('div', {class: 'segmented', role: 'group', 'aria-label': 'Which brush to edit'});
  const tabBar = el('div', {class: 'tabs tabs-scroll', role: 'tablist', 'aria-label': 'Setting groups'});
  const panel = el('div', {class: 'tabpanel', role: 'tabpanel', id: 'settings-panel', tabIndex: -1});
  const root = el('div', {class: 'panels'},
    el('div', {class: 'panel-tools'},
      el('div', {class: 'field grow'}, el('label', {htmlFor: 'panel-filter', text: 'Filter'}), filterInput),
      el('label', {class: 'check', htmlFor: 'unlock-unverified'}, unlock, el('span', {text: 'Unlock keys with unverified meaning'})),
      layerBar),
    tabBar, panel);

  function ctxFor() { return {doc, schema, layer: doc.active, focusPatchBox}; }

  function layout(groupId) {
    return groupLayout(schema, groupId, doc.effective(doc.active), doc.era);
  }

  function matches(row) { return !filter || searchText(row).includes(filter); }

  function changedInGroup(groupId) {
    let n = 0;
    for (const key of doc.changedKeys(doc.active)) { const r = schema.byKey.get(key); if (r && r.group === groupId) n += 1; }
    return n;
  }

  function renderTabs() {
    clear(tabBar);
    if (!doc) return;
    const counts = groupCounts(schema, doc.effective(doc.active), doc.era);
    const extra = unknownKeys(schema, doc.effective(doc.active)).length;
    schema.groups.forEach((g) => {
      let count = counts[g.id] + (g.id === 'about' ? extra : 0);
      if (filter) {
        const lay = layout(g.id);
        count = [...lay.sections.flatMap((s) => s.items), ...lay.hidden].filter((i) => matches(i.row)).length;
      }
      const changed = changedInGroup(g.id);
      const tab = el('button', {type: 'button', role: 'tab', class: 'tab', id: `tab-${g.id}`, 'aria-selected': g.id === group ? 'true' : 'false',
        'aria-controls': 'settings-panel', tabIndex: g.id === group ? 0 : -1, dataset: {group: g.id},
        onclick: () => selectGroup(g.id),
        onkeydown: (e) => tabKeys(e, g.id)},
      el('span', {text: g.label}), el('span', {class: 'count', text: String(count)}),
      changed ? el('span', {class: 'dot', title: `${changed} edited`, 'aria-label': `${changed} edited`, text: '●'}) : null);
      if (filter && count === 0) tab.classList.add('is-empty');
      tabBar.append(tab);
    });
  }

  function tabKeys(event, id) {
    const ids = schema.groups.map((g) => g.id);
    const i = ids.indexOf(id);
    let next = null;
    if (event.key === 'ArrowRight') next = ids[(i + 1) % ids.length];
    else if (event.key === 'ArrowLeft') next = ids[(i - 1 + ids.length) % ids.length];
    else if (event.key === 'Home') next = ids[0];
    else if (event.key === 'End') next = ids[ids.length - 1];
    if (next) { event.preventDefault(); selectGroup(next); const t = tabBar.querySelector(`#tab-${next}`); if (t) t.focus(); }
  }

  function selectGroup(id) {
    group = id;
    renderTab(); renderTabs();
  }

  function renderLayerBar() {
    clear(layerBar);
    layerBar.hidden = !(doc && doc.hasSub);
    if (layerBar.hidden) return;
    for (const [layer, text] of [['main', 'Primary brush'], ['sub', 'Secondary (dual) brush']]) {
      layerBar.append(el('button', {type: 'button', class: 'seg', 'aria-pressed': String(doc.active === layer), text,
        onclick: () => doc.setActive(layer)}));
    }
  }

  function renderTab() {
    clear(panel);
    rows = new Map();
    panel.setAttribute('aria-labelledby', `tab-${group}`);
    if (!doc) return;
    const reg = registry.get(group);
    if (reg && reg.mode === 'replace') { reg.render(panel, ctxFor()); return; }
    const lay = layout(group);
    let shown = 0;
    for (const section of lay.sections) {
      const items = section.items.filter((i) => matches(i.row));
      if (!items.length) continue;
      shown += items.length;
      panel.append(el('section', {class: 'section'}, el('h3', {class: 'section-title', text: section.name}),
        el('div', {class: 'rows'}, items.map((item) => buildRow(item)))));
    }
    const hidden = lay.hidden.filter((i) => matches(i.row));
    if (hidden.length) {
      shown += hidden.length;
      panel.append(el('details', {class: 'section internal'}, el('summary', {text: `Internal values, read only (${hidden.length})`}),
        el('div', {class: 'rows'}, hidden.map((item) => buildRow(item)))));
    }
    if (!shown && filter) panel.append(el('p', {class: 'muted', text: 'No setting in this group matches the filter.'}));
    if (lay.otherEra) panel.append(el('p', {class: 'muted small', text: `${lay.otherEra} setting(s) of this group belong to other eras and are not shown for an ${doc.era || 'unknown-era'} brush.`}));
    if (reg && reg.mode === 'append') reg.render(panel, ctxFor());
  }

  function buildRow(item) {
    const {row, state, key} = item;
    const layer = doc.active;
    const id = uid('k');
    const gate = widgetFor(row, {allowUnverified});
    const label = row.label;
    let comp = null;
    if (state === 'optional') {
      const add = el('button', {class: 'btn btn-small', type: 'button', text: 'Add to this brush', id,
        onclick: () => doc.set(key, row.default === undefined ? null : row.default, {layer})});
      comp = {el: el('div', {}, el('span', {class: 'muted', text: 'Not set in this brush. '}), add), update() {}, setEditable() {}};
    } else {
      comp = buildControl(row, {
        id, label, allowUnverified,
        onSet(value, opts) {
          const verdict = advise(row, value);
          if (!verdict.ok) { toast(`${label}: ${verdict.reason}.`, 'warn'); rowComp.update(); return; }
          doc.set(key, value, {coalesce: opts && opts.coalesce, layer});
        },
        onCommit() { doc.endCoalesce(); },
      });
    }
    const resetBtn = el('button', {class: 'btn btn-small btn-quiet', type: 'button', text: 'Reset', hidden: true,
      'aria-label': `Reset ${label} to the opened value`, onclick: () => doc.reset(key, layer)});
    const badges = el('span', {class: 'badges'},
      el('span', {class: `badge conf-${row.confidence}`, title: CONFIDENCE_LABELS[row.confidence] || '', text: row.confidence}),
      el('span', {class: `badge prev-${row.preview}`, title: PREVIEW_LABELS[row.preview] || '', text: `preview: ${row.preview}`}),
      key !== row.key ? el('span', {class: 'badge', title: `This era names the key ${key}`, text: 'alias'}) : null);
    const changedBadge = el('span', {class: 'badge badge-changed', text: 'edited', hidden: true});
    const lock = !gate.editable && gate.kind !== 'readonly' && gate.kind !== 'hidden'
      ? el('p', {class: 'small muted', text: gate.reason}) : null;
    const detailLines = [
      row.hint ? el('p', {text: row.hint}) : null,
      el('p', {class: 'small muted', text: `Key ${key}. Era(s): ${(row.eras || []).join(', ')}.`}),
      row.notes ? el('p', {class: 'small muted', text: row.notes}) : null,
    ];
    const node = el('div', {class: 'row', dataset: {key}},
      el('div', {class: 'row-head'}, el('label', {class: 'row-label', htmlFor: id, text: label}), changedBadge, badges),
      el('div', {class: 'row-control'}, comp.el, resetBtn),
      el('p', {class: 'row-meta small muted', text: `${key} · default ${defaultText(row)} · ${row.type === 'real' || row.type === 'int' ? observedText(row) : row.type}`}),
      lock,
      el('details', {class: 'row-more'}, el('summary', {text: 'About this setting'}), ...detailLines));
    const rowComp = {
      el: node, key, layer, state,
      update() {
        if (state === 'optional') return;
        const value = doc.value(key, layer);
        comp.update(value, doc.originalValue(key, layer));
        const changed = doc.isChanged(key, layer);
        resetBtn.hidden = !changed; changedBadge.hidden = !changed;
        node.classList.toggle('is-changed', changed);
      },
    };
    if (comp.setEditable) comp.setEditable(gate.editable && state !== 'optional');
    rows.set(key, rowComp);
    rowComp.update();
    return node;
  }

  function onDocEvent(event) {
    if (event.type === 'layer') { renderLayerBar(); renderTab(); renderTabs(); return; }
    let rebuild = false;
    for (const key of event.keys) {
      const comp = rows.get(key);
      if (!comp) continue;
      const nowHeld = doc.has(key, doc.active);
      if ((comp.state === 'optional') === nowHeld) rebuild = true;
      else comp.update();
    }
    if (rebuild) renderTab(); else if (group === 'about') renderTab();
    renderTabs();
  }

  return {
    el: root,
    setDoc(next) {
      if (unsubscribe) unsubscribe();
      doc = next;
      if (!doc) { clear(panel); clear(tabBar); return; }
      unsubscribe = doc.subscribe(onDocEvent);
      renderLayerBar(); renderTab(); renderTabs();
    },
    selectGroup,
    /** Show the row of a key (switches tab, clears the filter). */
    showKey(key) {
      const row = schema.byKey.get(key);
      if (!row) return false;
      filter = ''; filterInput.value = '';
      selectGroup(row.group);
      const comp = rows.get(key) || rows.get(row.key);
      if (comp) { comp.el.scrollIntoView({block: 'center'}); comp.el.classList.add('flash'); setTimeout(() => comp.el.classList.remove('flash'), 1500); }
      return !!comp;
    },
    /** Every control of the visible tab: for the selftest. */
    visibleRows() { return rows; },
    get group() { return group; },
  };
}
