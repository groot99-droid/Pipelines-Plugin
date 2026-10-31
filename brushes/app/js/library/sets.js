// library/sets.js - the Sets browser: GET /api/sets (the list), GET
// /api/sets/<slug> (one set, its brushes in set order).

import {el, clear} from '../dom.js';
import {createCard} from './card.js';

export function createSets({ctx, openBrush, getView}) {
  const root = el('div', {class: 'sets'});
  let sets = null;
  let library = '';
  let filter = '';
  let serial = 0;
  let current = null;

  const listBox = el('div', {class: 'sets-list-box'});
  const pageBox = el('div', {class: 'set-page', hidden: true});
  root.append(listBox, pageBox);

  function notice(error, retry) {
    return el('div', {class: 'notice notice-bad', role: 'alert'}, el('strong', {text: error.code || 'error'}), el('p', {text: error.message}),
      error.hint ? el('p', {class: 'small', text: error.hint}) : null,
      retry ? el('button', {class: 'btn btn-small', type: 'button', text: 'Try again', onclick: retry}) : null);
  }

  async function loadList() {
    clear(listBox);
    listBox.append(el('p', {class: 'muted', role: 'status', text: 'Loading the sets…'}));
    try {
      sets = (await ctx.api.sets()).sets || [];
    } catch (error) {
      clear(listBox); listBox.append(notice(error, loadList)); return;
    }
    renderList();
  }

  function renderList() {
    clear(listBox);
    const input = el('input', {type: 'search', class: 'text', id: 'set-filter', value: filter, autocomplete: 'off', placeholder: 'Filter sets by name, vendor or pack',
      oninput: (e) => { filter = e.target.value.trim().toLowerCase(); renderRows(); }});
    const seg = el('div', {class: 'segmented', role: 'group', 'aria-label': 'Which library'},
      [['', 'All'], ['user', 'User'], ['official', 'Official']].map(([value, text]) => el('button', {type: 'button', class: 'seg', 'aria-pressed': String(library === value), text,
        onclick: () => { library = value; renderList(); }})));
    listBox.append(el('div', {class: 'sets-tools'}, el('div', {class: 'field grow'}, el('label', {htmlFor: 'set-filter', text: 'Filter'}), input), seg));
    listBox.append(el('p', {class: 'small muted', id: 'sets-count', 'aria-live': 'polite'}), el('ul', {class: 'set-rows', id: 'set-rows'}));
    renderRows();
  }

  function renderRows() {
    const rows = (sets || []).filter((s) => (!library || s.library === library)
      && (!filter || `${s.title} ${s.name} ${s.vendor || ''} ${s.pack || ''} ${s.set_slug}`.toLowerCase().includes(filter)));
    const list = listBox.querySelector('#set-rows'); const count = listBox.querySelector('#sets-count');
    clear(list);
    count.textContent = rows.length ? `${rows.length} set${rows.length === 1 ? '' : 's'}` : 'No set matches.';
    for (const s of rows) {
      list.append(el('li', {}, el('button', {class: 'set-row', type: 'button', onclick: () => showSet(s.set_slug)},
        el('strong', {text: s.title || s.name}),
        el('span', {class: 'small muted', text: [s.vendor, s.library, s.kind].filter(Boolean).join(' · ')}),
        el('span', {class: 'small', text: `${s.brush_count} brush${s.brush_count === 1 ? '' : 'es'} · ${s.tagged} tagged`}))));
    }
  }

  async function showSet(slug) {
    const mine = ++serial;
    current = slug;
    listBox.hidden = true; pageBox.hidden = false;
    clear(pageBox);
    pageBox.append(el('p', {class: 'muted', role: 'status', text: 'Loading the set…'}));
    let data;
    try { data = await ctx.api.set(slug); } catch (error) {
      if (mine !== serial) return;
      clear(pageBox); pageBox.append(backButton(), notice(error, () => showSet(slug))); return;
    }
    if (mine !== serial) return;
    const s = data.set; const brushes = data.brushes || [];
    clear(pageBox);
    pageBox.append(backButton(),
      el('h3', {tabIndex: -1, class: 'set-title', text: s.title || s.name}),
      el('p', {class: 'small muted', text: [s.vendor, s.library, s.pack ? `pack ${s.pack}` : null, `${s.brush_count} brushes`, s.note ? `note ${s.note}` : null].filter(Boolean).join(' · ')}),
      el('div', {class: 'btn-row'}, el('button', {class: 'btn', type: 'button', text: `Add all ${brushes.length} to the set`, disabled: !brushes.length,
        onclick: () => {
          let added = 0;
          for (const r of brushes) if (ctx.basketAdd ? ctx.basketAdd(r.brush_id, r.name) : (ctx.addToSet(r.brush_id, r.name), true)) added += 1;
          ctx.toast(ctx.basketAdd ? `Added ${added} brush${added === 1 ? '' : 'es'} to the set.` : 'Added.', 'ok');
        }})),
      brushes.length ? el('ul', {class: `cards${getView() === 'list' ? ' cards-list' : ''}`, 'aria-label': `Brushes of ${s.title || s.name}`}, brushes.map((r) => createCard(r, {
        api: ctx.api, live: () => current === slug, list: getView() === 'list',
        onOpen: (x) => openBrush(x.brush_id), onDesigner: (x) => ctx.openInDesigner(x.brush_id), onAdd: (x) => ctx.addToSet(x.brush_id, x.name)})))
        : el('p', {class: 'muted', text: 'This set has no brush in the catalog.'}));
    const heading = pageBox.querySelector('.set-title'); if (heading) heading.focus();
  }

  function backButton() {
    return el('button', {class: 'btn btn-small', type: 'button', text: 'All sets', onclick: () => { serial += 1; pageBox.hidden = true; listBox.hidden = false; current = null; }});
  }

  return {
    el: root,
    show() { if (sets === null) loadList(); },
    open: showSet,
    get loaded() { return sets !== null; },
  };
}
