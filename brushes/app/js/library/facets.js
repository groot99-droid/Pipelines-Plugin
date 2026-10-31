// library/facets.js - the filter panel: facet chips from /api/facets, number
// ranges, the built-in library / tagged filters, and the tag chips of the
// closed vocabulary. Every chip is a toggle button (aria-pressed); the panel
// re-renders when a new facets answer arrives and puts keyboard focus back on
// the chip that was pressed.

import {el, clear, uid} from '../dom.js';
import {PRIMARY_FACETS, facetGroups, tagSummary, facetLabel} from './state.js';

const WORDS = {true: 'yes', false: 'no'};
const openState = {more: false, tags: false, axes: new Set()};

function chip({id, text, count, on, disabled, title, onclick}) {
  return el('button', {class: `chip${on ? ' is-on' : ''}${disabled ? ' is-dead' : ''}`, type: 'button', 'aria-pressed': String(!!on),
    'aria-disabled': disabled ? 'true' : null, title: title || null, dataset: {cid: id}, onclick: disabled ? null : onclick},
  el('span', {text}), count === undefined ? null : el('span', {class: 'chip-n', text: String(count)}));
}

function group(label, chips, hint) {
  const id = uid('fg');
  return el('div', {class: 'facet-group', role: 'group', 'aria-labelledby': id},
    el('div', {class: 'facet-label', id, text: label}), hint ? el('div', {class: 'small muted', text: hint}) : null,
    el('div', {class: 'chips'}, chips));
}

/**
 * createFacetPanel({getFilters, onToggle(facet, value), onTag(axis, tag), onRange(facet, min, max)})
 * -> {el, update({facets, libraryCounts, descriptions})}
 */
export function createFacetPanel({getFilters, onToggle, onTag, onRange}) {
  const root = el('div', {class: 'facet-panel'});
  let last = null;

  function enumChips(g, filters) {
    return g.values.map((v) => chip({
      id: `e:${g.name}:${v.value}`, text: g.kind === 'bool' ? WORDS[v.value] || v.value : v.value, count: v.count,
      on: (filters.enums[g.name] || []).includes(v.value), disabled: v.count === 0 && !(filters.enums[g.name] || []).includes(v.value),
      onclick: () => onToggle(g.name, v.value)}));
  }

  function rangeRow(r, filters, descriptions) {
    const current = filters.ranges[r.name] || {min: '', max: ''};
    const lo = el('input', {type: 'number', class: 'num', step: 'any', inputMode: 'decimal', value: current.min, 'aria-label': `${r.label}, from`, placeholder: String(r.min)});
    const hi = el('input', {type: 'number', class: 'num', step: 'any', inputMode: 'decimal', value: current.max, 'aria-label': `${r.label}, up to`, placeholder: String(r.max)});
    const apply = () => onRange(r.name, lo.value, hi.value);
    for (const input of [lo, hi]) {
      input.addEventListener('change', apply);
      input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); apply(); } });
    }
    return el('div', {class: 'range-row', title: descriptions[r.name] || ''},
      el('span', {class: 'range-name', text: r.label}), lo, el('span', {class: 'muted', text: 'to'}), hi,
      el('span', {class: 'small muted', text: `seen ${r.min} to ${r.max}, median ${r.median}`}));
  }

  function render() {
    if (!last) return;
    const focused = document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.cid : null;
    const filters = getFilters();
    const {facets, libraryCounts = {}, descriptions = {}} = last;
    const groups = facetGroups(facets, filters);
    clear(root);
    const primary = groups.enums.filter((g) => PRIMARY_FACETS.includes(g.name));
    const rest = groups.enums.filter((g) => !PRIMARY_FACETS.includes(g.name));
    const lib = ['user', 'official'].map((name) => chip({
      id: `e:library:${name}`, text: name, count: libraryCounts[name], on: (filters.enums.library || []).includes(name),
      onclick: () => onToggle('library', name)}));
    root.append(
      group('Library', lib, 'user = the legacy packs; official = Procreate’s own'),
      group('Tagged', ['true'].map((v) => chip({id: `e:tagged:${v}`, text: 'tagged only', on: (filters.enums.tagged || []).includes(v), onclick: () => onToggle('tagged', v)}))),
      ...primary.map((g) => el('div', {title: descriptions[g.name] || ''}, group(g.label, enumChips(g, filters)))));

    const more = el('details', {class: 'facet-more', open: openState.more, ontoggle: (e) => { openState.more = e.target.open; }},
      el('summary', {text: `More filters (${rest.length + groups.ranges.length})`}),
      ...rest.map((g) => el('div', {title: descriptions[g.name] || ''}, group(g.label, enumChips(g, filters)))),
      groups.ranges.length ? el('div', {class: 'facet-group'}, el('div', {class: 'facet-label', text: 'Number ranges'}),
        el('p', {class: 'small muted', text: 'Leave an end empty for “no limit”. Press Enter or leave the field to apply.'}),
        ...groups.ranges.map((r) => rangeRow(r, filters, descriptions))) : null);
    root.append(more);

    const tags = tagSummary(facets);
    const chosen = Object.values(filters.tags).reduce((n, list) => n + list.length, 0);
    root.append(el('details', {class: 'facet-more', open: openState.tags || chosen > 0, ontoggle: (e) => { openState.tags = e.target.open; }},
      el('summary', {text: `Tags (${tags.tagged} of ${tags.total} brushes tagged)`}),
      el('p', {class: `small ${tags.tagged ? 'muted' : 'bad-text'}`, text: tags.honest}),
      ...tags.axes.map((axis) => el('details', {class: 'tag-axis', open: openState.axes.has(axis.axis) || (filters.tags[axis.axis] || []).length > 0,
        ontoggle: (e) => { if (e.target.open) openState.axes.add(axis.axis); else openState.axes.delete(axis.axis); }},
      el('summary', {text: `${axis.axis} (${axis.values.length})`}),
      el('div', {class: 'chips'}, axis.values.map((v) => {
        const on = (filters.tags[axis.axis] || []).includes(v.tag);
        return chip({id: `t:${axis.axis}:${v.tag}`, text: v.tag, count: v.count, on, disabled: v.count === 0 && !on, title: v.definition,
          onclick: () => onTag(axis.axis, v.tag)});
      }))))));

    if (focused) {
      const again = [...root.querySelectorAll('[data-cid]')].find((n) => n.dataset.cid === focused);
      if (again) again.focus();
    }
  }

  return {
    el: root,
    update(data) { last = data; render(); },
    /** Facet groups for tests and the selftest. */
    chips() { return [...root.querySelectorAll('button.chip')]; },
    label: facetLabel,
  };
}
