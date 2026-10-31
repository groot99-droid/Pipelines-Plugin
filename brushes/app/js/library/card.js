// library/card.js - one brush as a card (grid) or a row (list), and the lazy
// loading of its stroke preview.
//
// A preview is Procreate's own stroke thumbnail where the catalog has one
// (`preview.stroke_source` is "thumbnail"); a rendered approximation is marked
// "approximate". The image is fetched with the token (api.previewUrl) only
// when the card scrolls near the viewport.

import {el} from '../dom.js';

let observer = null;
const pending = new WeakMap();

function lazyLoad(img, load) {
  if (typeof IntersectionObserver !== 'function') { load(); return; }
  if (!observer) {
    observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        observer.unobserve(entry.target);
        const job = pending.get(entry.target);
        pending.delete(entry.target);
        if (job) job();
      }
    }, {rootMargin: '300px 0px'});
  }
  pending.set(img, load);
  observer.observe(img);
  // a page that is not being drawn (a background tab) may not deliver observer callbacks: look once, by position
  setTimeout(() => {
    if (!pending.has(img)) return;
    const r = img.getBoundingClientRect();
    if (r.bottom > -300 && r.top < (window.innerHeight || 800) + 300 && (r.width || r.height)) { observer.unobserve(img); pending.delete(img); load(); }
  }, 1200);
}

/** An <img> that shows brush `id`'s preview `kind` once it is near the screen. */
export function previewImage(api, id, kind, {className = 'card-img', width = 212, height = 65, alt = '', live = () => true} = {}) {
  const img = el('img', {class: className, alt, width, height, decoding: 'async'});
  lazyLoad(img, () => {
    api.previewUrl(id, kind).then((url) => { if (live()) img.src = url; }, () => { img.classList.add('is-missing'); img.removeAttribute('src'); });
  });
  return img;
}

const KIND_WORD = {stamp: 'stamp', stroke: 'stroke'};

/** The small facts line under a name: library, era, kind. */
export function factsLine(r) {
  const f = r.facets || {};
  return [r.library, f.era, f.kind ? KIND_WORD[f.kind] || f.kind : null, f.dual ? 'dual' : null].filter(Boolean).join(' · ');
}

/**
 * card(r, opts) -> <li>. r is an F9 row.
 *   opts.api, opts.live()      preview loading
 *   opts.onOpen(r)             open the detail drawer
 *   opts.onDesigner(r), opts.onAdd(r)
 *   opts.list                  a compact row without the big image
 *   opts.showScore             show the match score (cosine ranking)
 *   opts.note                  an extra line (for example the top difference of a similar brush)
 */
export function createCard(r, opts) {
  const {api, live, onOpen, onDesigner, onAdd, list = false, showScore = false, note = null} = opts;
  const approx = r.approximate || (r.preview && r.preview.stroke_source === 'rendered-approx');
  const hasStroke = !!(r.preview && r.preview.stroke);
  const stage = el('button', {class: 'card-stage', type: 'button', 'aria-label': `Details of ${r.name}`, onclick: () => onOpen(r)});
  if (hasStroke) {
    stage.append(previewImage(api, r.brush_id, 'stroke', {
      className: 'card-img', width: list ? 160 : 212, height: list ? 49 : 65, live,
      alt: `${approx ? 'Approximate stroke' : 'Stroke thumbnail'} of ${r.name}`}));
  } else stage.append(el('span', {class: 'card-none small', text: 'No stroke preview'}));
  const alsoIn = (r.also_in || []).length;
  const badges = el('div', {class: 'card-badges'},
    approx ? el('span', {class: 'badge prev-approx', title: 'The preview is drawn by this tool, not Procreate’s own thumbnail.', text: 'approx preview'}) : null,
    alsoIn ? el('span', {class: 'badge', title: (r.also_in || []).map((x) => x.set).join(', '), text: `also in ${alsoIn} set${alsoIn === 1 ? '' : 's'}`}) : null,
    showScore && typeof r.score === 'number' ? el('span', {class: 'badge', title: 'Text match score', text: `match ${r.score.toFixed(2)}`}) : null);
  return el('li', {class: `brush-card${list ? ' is-list' : ''}`, dataset: {id: r.brush_id, set: r.set || ''}},
    stage,
    el('div', {class: 'card-body'},
      el('button', {class: 'card-name linklike', type: 'button', text: r.name, onclick: () => onOpen(r)}),
      el('span', {class: 'small muted card-set', text: r.set_title || r.set || ''}),
      el('span', {class: 'small muted', text: factsLine(r)}),
      badges,
      note ? el('span', {class: 'small card-note', text: note}) : null,
      el('div', {class: 'btn-row card-actions'},
        el('button', {class: 'btn btn-small btn-primary', type: 'button', text: 'Open in Designer', 'aria-label': `Open ${r.name} in the Designer`, onclick: () => onDesigner(r)}),
        el('button', {class: 'btn btn-small', type: 'button', text: 'Add to set', 'aria-label': `Add ${r.name} to the set`, onclick: () => onAdd(r)}))));
}
