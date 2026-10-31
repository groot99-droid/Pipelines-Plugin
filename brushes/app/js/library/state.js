// library/state.js - the Library tab's filter state and its words. Pure: no
// DOM, no network, importable from Node.
//
// A filter state is plain data (it can be stored or compared):
//   {enums: {facet: [value, ...]}, ranges: {facet: {min, max}}, tags: {axis: [tag, ...]}}
// Several values of one facet are an OR (F9: a comma list); different facets
// and axes are ANDed. `library:` and `tagged:` are F9's built-in `where` keys
// and live in `enums` like any facet. buildParams() turns a state into the
// query parameters of GET /api/search and /api/facets.

export const PRIMARY_FACETS = ['kind', 'spacing_class', 'taper', 'pressure_size_class', 'pressure_opacity_class',
  'wet_mix', 'dual', 'has_grain', 'size_class', 'era', 'grain_source', 'shape_source'];

export const FACET_LABELS = {
  kind: 'Kind', spacing_class: 'Spacing', taper: 'Taper', pressure_size_class: 'Pressure changes size',
  pressure_opacity_class: 'Pressure changes opacity', wet_mix: 'Wet mix', dual: 'Dual brush', has_grain: 'Has grain',
  size_class: 'Size', era: 'Era', grain_source: 'Grain image', shape_source: 'Shape image', library: 'Library',
  tagged: 'Tagged', family: 'Family', grain_movement: 'Grain movement', is_stamp: 'Stamp', scatter: 'Scatter',
  jitter_size: 'Size jitter', jitter_opacity: 'Opacity jitter', jitter_position: 'Position jitter', streamline: 'StreamLine',
  tilt: 'Tilt', speed: 'Speed', translucent: 'Translucent', wet_edges: 'Wet edges', burnt_edges: 'Burnt edges',
  shape_rotation: 'Shape rotates', randomised: 'Randomized', azimuth: 'Azimuth', color_dynamics: 'Color dynamics',
  uses_bundled_shape: 'Bundled shape', uses_bundled_grain: 'Bundled grain', stroke_source: 'Stroke preview from',
  spacing: 'Spacing (number)', size_max: 'Maximum size', size_min: 'Minimum size', opacity_max: 'Maximum opacity',
  opacity_min: 'Minimum opacity', pressure_size: 'Pressure to size', pressure_opacity: 'Pressure to opacity',
};

/** Values in a meaningful order where there is one; otherwise by how many brushes have them. */
const VALUE_ORDER = {
  spacing_class: ['continuous', 'tight', 'visible', 'dotted'],
  size_class: ['fine', 'medium', 'broad', 'max'],
  taper: ['none', 'start', 'end', 'both'],
  pressure_size_class: ['none', 'low', 'medium', 'high', 'inverse'],
  pressure_opacity_class: ['none', 'low', 'medium', 'high', 'inverse'],
  era: ['E0', 'E1', 'E1b', 'E1c', 'E2', 'E3', 'E4', 'M172', 'M173', 'M220', 'M242'],
  library: ['user', 'official'],
};

export function facetLabel(name) {
  return FACET_LABELS[name] || name.replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase());
}

export const emptyFilters = () => ({enums: {}, ranges: {}, tags: {}});

const clone = (f) => ({enums: {...f.enums}, ranges: {...f.ranges}, tags: {...f.tags}});

function toggled(list, value) {
  const set = new Set(list || []);
  if (set.has(value)) set.delete(value); else set.add(value);
  return [...set];
}

export function toggleValue(filters, facet, value) {
  const next = clone(filters);
  const list = toggled(filters.enums[facet], String(value));
  if (list.length) next.enums[facet] = list; else delete next.enums[facet];
  return next;
}

export function toggleTag(filters, axis, tag) {
  const next = clone(filters);
  const list = toggled(filters.tags[axis], tag);
  if (list.length) next.tags[axis] = list; else delete next.tags[axis];
  return next;
}

/** min/max are numbers or '' (open end). Both open removes the filter. */
export function setRange(filters, facet, min, max) {
  const next = clone(filters);
  const lo = min === '' || min === null || min === undefined ? '' : Number(min);
  const hi = max === '' || max === null || max === undefined ? '' : Number(max);
  const bad = (v) => v !== '' && !Number.isFinite(v);
  if ((lo === '' && hi === '') || bad(lo) || bad(hi)) delete next.ranges[facet];
  else next.ranges[facet] = {min: lo, max: hi};
  return next;
}

export function removeChip(filters, chip) {
  if (chip.type === 'enum') return toggleValue(filters, chip.facet, chip.value);
  if (chip.type === 'tag') return toggleTag(filters, chip.facet, chip.value);
  const next = clone(filters);
  delete next.ranges[chip.facet];
  return next;
}

export function hasFilters(filters) {
  return Object.keys(filters.enums).length + Object.keys(filters.ranges).length + Object.keys(filters.tags).length > 0;
}

const rangeText = (r) => `${r.min}..${r.max}`;

/** {q, tag: [...], where: [...], where_not: []}: the parameters of /api/search and /api/facets. */
export function buildParams(q, filters) {
  const where = [];
  for (const [facet, values] of Object.entries(filters.enums)) where.push(`${facet}=${values.join(',')}`);
  for (const [facet, range] of Object.entries(filters.ranges)) where.push(`${facet}=${rangeText(range)}`);
  const tag = Object.entries(filters.tags).map(([axis, values]) => `${axis}=${values.join(',')}`);
  return {q: (q || '').trim(), tag, where, where_not: []};
}

/** The chips of the active filters, in a stable order: {id, type, facet, value, label}. */
export function activeChips(filters) {
  const chips = [];
  for (const [facet, values] of Object.entries(filters.enums)) {
    for (const value of values) chips.push({id: `e:${facet}:${value}`, type: 'enum', facet, value, label: `${facetLabel(facet)}: ${value}`});
  }
  for (const [facet, range] of Object.entries(filters.ranges)) {
    const text = range.min === '' ? `up to ${range.max}` : range.max === '' ? `from ${range.min}` : `${range.min} to ${range.max}`;
    chips.push({id: `r:${facet}`, type: 'range', facet, value: rangeText(range), label: `${facetLabel(facet)}: ${text}`});
  }
  for (const [axis, values] of Object.entries(filters.tags)) {
    for (const value of values) chips.push({id: `t:${axis}:${value}`, type: 'tag', facet: axis, value, label: `${axis}: ${value}`});
  }
  return chips;
}

/**
 * Facet groups for the chip panel from a /api/facets answer:
 *   enums  [{name, label, kind, values: [{value, count}]}] (enum and bool facets; the value `null` is not a filter)
 *   ranges [{name, label, min, median, max}]
 * A chosen value stays visible even if the current filters leave it with no brushes.
 */
export function facetGroups(facetsAnswer, filters = emptyFilters()) {
  const enums = []; const ranges = [];
  for (const [name, info] of Object.entries((facetsAnswer && facetsAnswer.facets) || {})) {
    if (info.kind === 'number') { ranges.push({name, label: facetLabel(name), min: info.min, median: info.median, max: info.max, n: info.n}); continue; }
    const counts = info.values || {};
    const chosen = filters.enums[name] || [];
    const names = new Set([...Object.keys(counts), ...chosen]);
    names.delete('null');
    const values = [...names].map((value) => ({value, count: counts[value] || 0}));
    const order = VALUE_ORDER[name];
    values.sort(order
      ? (a, b) => (order.indexOf(a.value) + 1 || 99) - (order.indexOf(b.value) + 1 || 99)
      : (a, b) => b.count - a.count || a.value.localeCompare(b.value));
    if (values.length) enums.push({name, label: facetLabel(name), kind: info.kind, values});
  }
  const rank = (n) => (PRIMARY_FACETS.includes(n) ? PRIMARY_FACETS.indexOf(n) : 100);
  enums.sort((a, b) => rank(a.name) - rank(b.name) || a.name.localeCompare(b.name));
  return {enums, ranges: ranges.sort((a, b) => a.name.localeCompare(b.name))};
}

/**
 * The tag side of /api/facets: {tagged, total, honest, axes: [{axis, tagged, values: [{tag, count, definition}]}]}.
 * `honest` is the sentence about how much of the library carries tags.
 */
export function tagSummary(facetsAnswer) {
  const state = (facetsAnswer && facetsAnswer.tag_state) || {};
  const total = (facetsAnswer && facetsAnswer.brushes) || 0;
  const taggedAll = state.tagged || 0;
  const axes = [];
  for (const [axis, info] of Object.entries((facetsAnswer && facetsAnswer.tags) || {})) {
    const defs = info.definitions || {};
    axes.push({axis, tagged: info.tagged || 0, values: Object.entries(info.values || {}).map(([tag, count]) => ({tag, count, definition: defs[tag] || ''}))});
  }
  const totalAll = (state.tagged || 0) + (state.stale || 0) + (state.untagged || 0) || total;
  const honest = taggedAll === 0
    ? `0 of ${totalAll} brushes are tagged yet, so tag filters match nothing for now.`
    : `${taggedAll} of ${totalAll} brushes are tagged; tag filters only see those.`;
  return {tagged: taggedAll, total: totalAll, honest, axes};
}

/** One sentence on how the result list is ordered, from the F9 envelope's `ranking`. */
export function rankingText(envelope) {
  const ranking = envelope && envelope.ranking;
  if (ranking === 'cosine') return 'Ordered by text match: your words against each brush’s note (its names, facet words and tags). The score is a cosine similarity, 0 to 1.';
  if (ranking === 'tag-purity') return 'Ordered by tag purity: brushes whose tags are mostly the ones you chose come first.';
  if (ranking === 'filter-order') return 'No words to match, so the brushes that pass the filters are shown in set order.';
  return '';
}

/** "224 brushes", "No brush matches", with the filter count. */
export function resultsText(total, shown, chips) {
  if (!total) return chips ? 'No brush matches these words and filters.' : 'No brushes match.';
  return `${shown < total ? `${shown} of ${total}` : total} brush${total === 1 ? '' : 'es'}${chips ? ` with ${chips} filter${chips === 1 ? '' : 's'}` : ''}`;
}

/** Remembered preferences: the last query and the view mode. Never filters, never a token. */
export function sanitizePrefs(raw) {
  const view = raw && (raw.view === 'list' || raw.view === 'grid') ? raw.view : 'grid';
  const q = raw && typeof raw.q === 'string' ? raw.q.slice(0, 200) : '';
  return {view, q};
}

/** Pure checks: [{name, run}] for selftest.js and any Node runner. */
export function libraryStateTests() {
  const tests = [];
  const t = (name, run) => tests.push({name, run});
  const ok = (c, m) => { if (!c) throw new Error(m || 'assertion failed'); };
  const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${m || 'not equal'}: got ${JSON.stringify(a)}, wanted ${JSON.stringify(b)}`); };
  t('library state: toggling a value adds and removes it; two values of one facet are an OR', () => {
    let f = emptyFilters();
    f = toggleValue(f, 'kind', 'stamp'); eq(buildParams('', f).where, ['kind=stamp']);
    f = toggleValue(f, 'kind', 'stroke'); eq(buildParams('', f).where, ['kind=stamp,stroke']);
    f = toggleValue(f, 'kind', 'stamp'); f = toggleValue(f, 'kind', 'stroke'); ok(!hasFilters(f)); eq(buildParams('', f).where, []);
  });
  t('library state: ranges, tags and chips build the F9 grammar and can be removed', () => {
    let f = setRange(emptyFilters(), 'spacing', 0.05, ''); f = setRange(f, 'size_max', '', 4); f = toggleTag(f, 'medium', 'charcoal');
    const p = buildParams('  dry ink ', f);
    eq(p.q, 'dry ink'); eq(p.where, ['spacing=0.05..', 'size_max=..4']); eq(p.tag, ['medium=charcoal']);
    const chips = activeChips(f); eq(chips.length, 3);
    for (const chip of chips) f = removeChip(f, chip);
    ok(!hasFilters(f));
    ok(!hasFilters(setRange(emptyFilters(), 'spacing', '', '')), 'an open range is no filter');
    ok(!hasFilters(setRange(emptyFilters(), 'spacing', 'abc', '')), 'a non-number is no filter');
  });
  t('library state: facet groups are ordered, hide the null value and keep a chosen value visible', () => {
    const answer = {brushes: 10, facets: {
      spacing_class: {kind: 'enum', values: {dotted: 1, continuous: 5, tight: 2}},
      blend_code: {kind: 'enum', values: {0: 8, null: 2}}, spacing: {kind: 'number', n: 10, min: 0, median: 0.02, max: 2}}};
    const g = facetGroups(answer, toggleValue(emptyFilters(), 'spacing_class', 'visible'));
    eq(g.enums[0].values.map((v) => v.value), ['continuous', 'tight', 'visible', 'dotted']);
    eq(g.enums.find((e) => e.name === 'blend_code').values.map((v) => v.value), ['0']); eq(g.ranges.map((r) => r.name), ['spacing']);
  });
  t('library state: the tag summary says plainly that nothing is tagged yet', () => {
    const s = tagSummary({brushes: 990, tag_state: {tagged: 0, stale: 0, untagged: 990}, tags: {medium: {tagged: 0, values: {charcoal: 0}, definitions: {charcoal: 'x'}}}});
    ok(s.honest.startsWith('0 of 990 brushes are tagged yet'), s.honest); eq(s.axes[0].values[0], {tag: 'charcoal', count: 0, definition: 'x'});
    ok(tagSummary({brushes: 10, tag_state: {tagged: 4, stale: 0, untagged: 6}, tags: {}}).honest.startsWith('4 of 10'));
  });
  t('library state: ranking words, result words and stored preferences are bounded', () => {
    for (const r of ['cosine', 'tag-purity', 'filter-order']) ok(rankingText({ranking: r}).length > 20);
    eq(resultsText(0, 0, 0), 'No brushes match.'); eq(resultsText(224, 24, 2), '24 of 224 brushes with 2 filters');
    eq(sanitizePrefs({view: 'x', q: 'a'.repeat(500)}).q.length, 200); eq(sanitizePrefs(null), {view: 'grid', q: ''});
  });
  return tests;
}
