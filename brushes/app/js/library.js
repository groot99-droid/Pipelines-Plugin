// library.js - the Library tab (phase 3c).
//
// THE SEAM (unchanged since 3a)
//   mountLibrary(container, ctx) -> {refresh(), dispose(), search(text), ...}
//   ctx = {
//     api,                          // api.js: search, facets, sets, similar, previewUrl ...
//     openInDesigner(brushId),      // loads the brush in the Designer and switches tab
//     addToSet(brushId, name),      // puts a library brush in the .brushset basket
//     toast(message, kind),
//     basket                        // optional: exporter.js createBasket(), for the count and the export
//   }
//
// What it shows: a query box (GET /api/search, debounced), facet and tag chips
// (GET /api/facets, /api/vocabulary), the ordering in words, a result grid or
// list with Procreate's own stroke thumbnails (lazy), a detail drawer with
// "Similar brushes", a Sets browser (GET /api/sets), and the set basket.
// It remembers the last words and the view (grid or list) in localStorage;
// never the filters, never the token.
//
// Pure parts (filter state, wording) are in library/state.js; the pieces are
// library/card.js, facets.js, drawer.js, sets.js and basket.js.

import {el, clear} from './dom.js';
import {schemaIndex} from './schema-load.js';
import {createBasket} from './exporter.js';
import {prefs} from './ui.js';
import {buildParams, emptyFilters, toggleValue, toggleTag, setRange, removeChip, activeChips, hasFilters,
  rankingText, resultsText, sanitizePrefs} from './library/state.js';
import {createCard} from './library/card.js';
import {createFacetPanel} from './library/facets.js';
import {createDrawer} from './library/drawer.js';
import {createSets} from './library/sets.js';
import {createBasketView} from './library/basket.js';

const PAGE = 24;
const DEBOUNCE_MS = 300;
const SLOW_MS = 700;

export function mountLibrary(container, rawCtx) {
  const stored = sanitizePrefs({view: prefs.get('lib.view'), q: prefs.get('lib.q')});
  const basket = rawCtx.basket || (window.__brushApp && window.__brushApp.basket) || createBasket();
  const ctx = {...rawCtx, basket, basketAdd: (id, name) => basket.addLibrary(id, name)};
  const {api} = ctx;

  let filters = emptyFilters();
  let query = stored.q;
  let view = stored.view;
  let mode = 'search';
  let offset = 0;
  let total = 0;
  let envelope = null;
  let serial = 0;
  let activeRun = 0;
  let disposed = false;
  let started = false;
  let timer = 0;
  let slowTimer = 0;
  let facetsData = null;
  const extras = {libraryCounts: {}, descriptions: {}};
  const getSchema = schemaIndex;

  // ── pieces ──
  const input = el('input', {type: 'search', class: 'text', id: 'lib-q', value: query, autocomplete: 'off', enterKeyHint: 'search',
    placeholder: 'Try: watercolour wash, dry charcoal, fine ink…', oninput: () => { clearTimeout(timer); timer = setTimeout(() => run(true), DEBOUNCE_MS); }});
  const form = el('form', {class: 'inline-form lib-form', role: 'search', onsubmit: (e) => { e.preventDefault(); clearTimeout(timer); run(true); }},
    el('label', {htmlFor: 'lib-q', class: 'sr-only', text: 'Search the brush library'}), input,
    el('button', {class: 'btn btn-primary', type: 'submit', text: 'Search'}));
  const count = el('p', {class: 'lib-count', role: 'status', 'aria-live': 'polite'});
  const ranking = el('details', {class: 'lib-ranking'}, el('summary', {text: 'How these are ordered'}), el('p', {class: 'small muted', id: 'lib-ranking-text'}));
  const note = el('div', {class: 'lib-note'});
  const chipsRow = el('div', {class: 'chips active-chips', 'aria-label': 'Active filters', role: 'group'});
  const list = el('ul', {class: 'cards', 'aria-label': 'Search results'});
  const more = el('button', {class: 'btn', type: 'button', text: 'Load more', hidden: true, onclick: () => run(false)});
  const viewSeg = el('div', {class: 'segmented', role: 'group', 'aria-label': 'Result layout'});
  const facetPanel = createFacetPanel({
    getFilters: () => filters,
    onToggle: (facet, value) => change(toggleValue(filters, facet, value)),
    onTag: (axis, tag) => change(toggleTag(filters, axis, tag)),
    onRange: (facet, min, max) => change(setRange(filters, facet, min, max)),
  });
  const filtersBox = el('details', {class: 'filters-box', open: !window.matchMedia || window.matchMedia('(min-width: 56rem)').matches},
    el('summary', {text: 'Filters'}),
    el('p', {class: 'small muted', text: 'Counts are for the filters only, not for your words.'}), facetPanel.el);
  const drawer = createDrawer({ctx, getSchema, openSet: (slug) => { setMode('sets'); sets.open(slug); }});
  const sets = createSets({ctx, openBrush: (id) => drawer.open(id), getView: () => view});
  const basketView = createBasketView({basket, toast: ctx.toast});
  const modeSeg = el('div', {class: 'segmented', role: 'group', 'aria-label': 'Browse by'});
  const searchView = el('div', {class: 'lib-search'});
  const setsView = el('div', {class: 'lib-sets', hidden: true}, sets.el);

  searchView.append(form,
    el('div', {class: 'lib-body'},
      el('aside', {class: 'lib-filters', 'aria-label': 'Filters'}, filtersBox),
      el('section', {class: 'lib-results', 'aria-label': 'Results'}, chipsRow,
        el('div', {class: 'lib-meta'}, count, viewSeg), ranking, note, list, el('div', {class: 'btn-row'}, more))));
  container.append(el('div', {class: 'library'},
    el('div', {class: 'lib-head'}, el('h2', {text: 'Library'}), modeSeg, basketView.button),
    searchView, setsView, drawer.el, basketView.el));

  function renderSegs() {
    clear(modeSeg); clear(viewSeg);
    for (const [value, text] of [['search', 'Search'], ['sets', 'Sets']]) {
      modeSeg.append(el('button', {type: 'button', class: 'seg', 'aria-pressed': String(mode === value), text, onclick: () => setMode(value)}));
    }
    for (const [value, text] of [['grid', 'Grid'], ['list', 'List']]) {
      viewSeg.append(el('button', {type: 'button', class: 'seg', 'aria-pressed': String(view === value), text, 'aria-label': `${text} layout`, onclick: () => setView(value)}));
    }
  }

  function setMode(next) {
    mode = next;
    searchView.hidden = mode !== 'search'; setsView.hidden = mode !== 'sets';
    if (mode === 'sets') sets.show();
    renderSegs();
  }

  function setView(next) {
    view = next; prefs.set('lib.view', view);
    list.classList.toggle('cards-list', view === 'list');
    renderSegs();
    if (envelope) rebuildCards();
  }

  // ── filters ──
  function change(next) {
    filters = next;
    renderChips();
    run(true);
  }

  function renderChips() {
    clear(chipsRow);
    const chips = activeChips(filters);
    chipsRow.hidden = !chips.length;
    for (const c of chips) {
      chipsRow.append(el('button', {class: 'chip is-on chip-active', type: 'button', 'aria-label': `Remove filter ${c.label}`, onclick: () => change(removeChip(filters, c))},
        el('span', {text: c.label}), el('span', {class: 'chip-x', 'aria-hidden': 'true', text: '×'})));
    }
    if (chips.length) chipsRow.append(el('button', {class: 'btn btn-small btn-quiet', type: 'button', text: 'Clear all filters', onclick: () => change(emptyFilters())}));
  }

  // ── results ──
  const cardOpts = () => ({
    api, live: () => !disposed, list: view === 'list', showScore: !!(envelope && envelope.ranking === 'cosine' && query.trim()),
    onOpen: (x) => drawer.open(x.brush_id), onDesigner: (x) => ctx.openInDesigner(x.brush_id), onAdd: (x) => ctx.addToSet(x.brush_id, x.name),
  });
  let rowsShown = [];

  function rebuildCards() {
    clear(list);
    list.classList.toggle('cards-list', view === 'list');
    rowsShown.forEach((r) => list.append(createCard(r, cardOpts())));
  }

  function showError(error, retry) {
    clear(note);
    note.append(el('div', {class: 'notice notice-bad', role: 'alert'}, el('strong', {text: error.code || 'error'}), el('p', {text: error.message}),
      error.hint ? el('p', {class: 'small', text: error.hint}) : null,
      el('button', {class: 'btn btn-small', type: 'button', text: 'Try again', onclick: retry})));
  }

  async function run(fresh) {
    const mine = ++serial;
    activeRun = mine;
    try { await execute(mine, fresh); } finally { if (activeRun === mine) activeRun = 0; }
  }

  async function execute(mine, fresh) {
    query = input.value.trim();
    prefs.set('lib.q', query);
    if (fresh) offset = 0;
    clear(note);
    list.setAttribute('aria-busy', 'true');
    clearTimeout(slowTimer);
    slowTimer = setTimeout(() => { if (mine === serial) count.textContent = 'Still searching… the search server is slow to answer.'; }, SLOW_MS);
    const params = buildParams(query, filters);
    const facetsRequest = fresh ? api.facets({tag: params.tag, where: params.where}).catch((error) => ({error})) : Promise.resolve(null);
    let result;
    try {
      result = await api.search({...params, top: PAGE, offset});
    } catch (error) {
      if (mine !== serial || disposed) return;
      clearTimeout(slowTimer); list.removeAttribute('aria-busy');
      if (fresh) { rowsShown = []; clear(list); }
      count.textContent = 'The search failed.';
      showError(error, () => run(fresh));
      more.hidden = true;
      return;
    }
    clearTimeout(slowTimer);
    if (mine !== serial || disposed) return;
    list.removeAttribute('aria-busy');
    envelope = result;
    total = result.total || 0;
    const rows = result.results || [];
    if (fresh) rowsShown = [];
    rowsShown = rowsShown.concat(rows);
    if (fresh) rebuildCards(); else rows.forEach((r) => list.append(createCard(r, cardOpts())));
    offset += rows.length;
    const chips = activeChips(filters).length;
    count.textContent = resultsText(total, Math.min(offset, total), chips) + (result.index && result.index !== 'fresh' ? ` (search index: ${result.index})` : '');
    ranking.querySelector('#lib-ranking-text').textContent = rankingText(result) || 'No ordering information.';
    ranking.hidden = !total;
    more.hidden = offset >= total;
    if (!total) {
      note.append(el('div', {class: 'notice'}, el('p', {text: hasFilters(filters) ? 'Nothing matches. Remove a filter or use fewer words.' : 'Nothing matches. Try other words, or clear the box to browse everything.'}),
        hasFilters(filters) ? el('button', {class: 'btn btn-small', type: 'button', text: 'Clear all filters', onclick: () => change(emptyFilters())}) : null));
    }
    if (result.index === 'stale') note.append(el('div', {class: 'notice notice-warn'}, el('p', {text: 'The search index is older than the catalog; results may miss recent changes.'})));
    const f = await facetsRequest;
    if (f && mine === serial && !disposed) {
      if (f.error) { facetsData = null; clear(facetPanel.el); facetPanel.el.append(el('p', {class: 'small bad-text', text: `Filters unavailable: ${f.error.message}`})); } else { facetsData = f; facetPanel.update({facets: f, ...extras}); }
    }
  }

  function loadExtras() {
    api.status().then((s) => { extras.libraryCounts = (s.counts && s.counts.by_library) || {}; if (facetsData) facetPanel.update({facets: facetsData, ...extras}); }, () => {});
    api.vocabulary().then((v) => {
      for (const f of v.facets || []) if (f.description) extras.descriptions[f.name] = f.description;
      if (facetsData) facetPanel.update({facets: facetsData, ...extras});
    }, () => {});
  }

  renderSegs();
  renderChips();
  setView(view);

  return {
    refresh() {
      if (!started) { started = true; loadExtras(); run(true); }
    },
    dispose() { disposed = true; clearTimeout(timer); clearTimeout(slowTimer); basketView.destroy(); clear(container); },
    /** Set the words and search now. Resolves when the results are on screen. */
    async search(text) { input.value = text; clearTimeout(timer); started = true; await run(true); },
    /** Toggle a facet value chip (as a click on it would) and wait for the results. */
    async toggleFacet(facet, value) { change(toggleValue(filters, facet, value)); await settled(); },
    async clearFilters() { change(emptyFilters()); await settled(); },
    async settled() { await settled(); },
    state() { return {mode, view, query, total, shown: rowsShown.length, filters, ranking: envelope && envelope.ranking, cards: list.children.length}; },
    drawer, sets, basketView, facetPanel, setMode,
  };

  function settled() {
    return new Promise((resolve) => {
      const tick = () => { if (disposed || activeRun === 0) resolve(); else setTimeout(tick, 30); };
      tick();
    });
  }
}
