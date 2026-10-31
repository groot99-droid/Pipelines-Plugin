// library.js - the Library tab. 3a ships a minimal version so the app is usable
// now; phase 3c replaces this module (facets, sets, similar, the drawer) behind
// the same seam.
//
// THE SEAM
//   mountLibrary(container, ctx) -> {refresh(), dispose()}
//   ctx = {
//     api,                          // api.js: search, facets, sets, similar, previewUrl ...
//     openInDesigner(brushId),      // loads the brush in the Designer and switches tab
//     addToSet(brushId, name),      // puts a library brush in the .brushset basket
//     toast(message, kind)
//   }
// The container is #library-mount; the module owns everything inside it.
//
// F10: GET /api/search?q&tag&where&where_not&top&offset answers the F9
// envelope {total, offset, results: [{brush_id, name, set_title, library,
// facets: {era, kind, ...}, preview: {stroke}, ...}]}. With no filter it
// browses in set order.

import {el, clear} from './dom.js';

const PAGE = 24;

export function mountLibrary(container, ctx) {
  let offset = 0;
  let total = 0;
  let query = '';
  let serial = 0;
  let disposed = false;

  const input = el('input', {type: 'search', class: 'text', id: 'lib-q', placeholder: 'Search brushes: ink, charcoal, soft grain…', autocomplete: 'off'});
  const form = el('form', {class: 'inline-form', role: 'search', onsubmit: (e) => { e.preventDefault(); query = input.value.trim(); load(true); }},
    el('label', {htmlFor: 'lib-q', class: 'sr-only', text: 'Search the brush library'}), input,
    el('button', {class: 'btn btn-primary', type: 'submit', text: 'Search'}));
  const count = el('p', {class: 'small muted', 'aria-live': 'polite'});
  const list = el('ul', {class: 'cards', 'aria-label': 'Search results'});
  const more = el('button', {class: 'btn', type: 'button', text: 'Load more', hidden: true, onclick: () => load(false)});
  const note = el('div', {class: 'lib-note'});
  container.append(el('div', {class: 'library'},
    el('h2', {text: 'Library'}), form, count, note, list, el('div', {class: 'btn-row'}, more)));

  function card(r) {
    const img = el('img', {class: 'card-img', alt: '', width: 212, height: 65, loading: 'lazy'});
    if (r.preview && r.preview.stroke) {
      ctx.api.previewUrl(r.brush_id, 'stroke').then((url) => { if (!disposed) img.src = url; }, () => { img.classList.add('is-missing'); });
    } else img.classList.add('is-missing');
    const f = r.facets || {};
    return el('li', {class: 'brush-card'},
      el('div', {class: 'card-stage'}, img),
      el('div', {class: 'card-body'},
        el('strong', {class: 'card-name', text: r.name}),
        el('span', {class: 'small muted', text: `${r.set_title || r.set || ''}`}),
        el('span', {class: 'small muted', text: [r.library, f.era, f.kind].filter(Boolean).join(' · ')}),
        el('div', {class: 'btn-row'},
          el('button', {class: 'btn btn-small btn-primary', type: 'button', text: 'Open in designer', 'aria-label': `Open ${r.name} in the designer`,
            onclick: () => ctx.openInDesigner(r.brush_id)}),
          el('button', {class: 'btn btn-small', type: 'button', text: 'Add to set', 'aria-label': `Add ${r.name} to the set`,
            onclick: () => ctx.addToSet(r.brush_id, r.name)}))));
  }

  async function load(fresh) {
    const mine = ++serial;
    if (fresh) { offset = 0; clear(list); }
    clear(note);
    try {
      const result = await ctx.api.search({q: query, top: PAGE, offset});
      if (mine !== serial || disposed) return;
      total = result.total || 0;
      (result.results || []).forEach((r) => list.append(card(r)));
      offset += (result.results || []).length;
      count.textContent = total ? `${Math.min(offset, total)} of ${total} brushes` : 'No brushes match.';
      more.hidden = offset >= total;
    } catch (error) {
      if (mine !== serial) return;
      note.append(el('div', {class: 'notice notice-bad', role: 'alert'}, el('strong', {text: error.code || 'error'}), el('p', {text: error.message}),
        error.hint ? el('p', {class: 'small', text: error.hint}) : null));
      more.hidden = true;
    }
  }

  return {
    refresh() { if (!list.children.length) load(true); },
    dispose() { disposed = true; clear(container); },
    search(text) { input.value = text; query = text; return load(true); },
  };
}
