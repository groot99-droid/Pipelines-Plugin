// schema.js - schema/silica_keys.json (F4) turned into what the panels need.
// Pure: no DOM, no network. Importable from Node.
//
// A row says: key, type, eras, default, limits, observed, enum, group, section,
// label, confidence, ui, display, step, hint, ai, preview, advanced. The panels
// are generated from rows; nothing about a key is written in the app except
// how to draw a `ui` kind.

export const PREVIEW_LABELS = {
  honoured: 'The stroke preview follows this setting.',
  approx: 'The stroke preview follows this setting only roughly.',
  ignored: 'The stroke preview does not use this setting.',
};

export const CONFIDENCE_LABELS = {
  verified: 'Observed directly in a file.',
  inferred: 'Label, group and range are inferred from the key name and the library.',
  unknown: 'Meaning not established. The label is a guess.',
};

export function indexSchema(raw) {
  if (!raw || !Array.isArray(raw.keys) || !Array.isArray(raw.groups)) throw new Error('silica_keys.json has no keys or groups');
  const byKey = new Map();
  const rowsByGroup = new Map();
  for (const group of raw.groups) rowsByGroup.set(group.id, []);
  for (const row of raw.keys) {
    byKey.set(row.key, row);
    for (const alias of row.aliases || []) if (!byKey.has(alias)) byKey.set(alias, row);
    if (!rowsByGroup.has(row.group)) rowsByGroup.set(row.group, []);
    rowsByGroup.get(row.group).push(row);
  }
  const groups = [...raw.groups].sort((a, b) => a.order - b.order);
  const eras = new Map((raw.eras || []).map((era) => [era.id, era]));
  return {raw, version: raw.schema_version, rows: raw.keys, byKey, groups, rowsByGroup, eras};
}

/**
 * How a row relates to one brush:
 *   present - the brush holds the key
 *   optional - the brush's era lists the key but this brush has not got it (can be added)
 *   other    - the key belongs to other eras only
 */
export function availability(row, settings, era) {
  if (Object.prototype.hasOwnProperty.call(settings, row.key)) return 'present';
  for (const alias of row.aliases || []) if (Object.prototype.hasOwnProperty.call(settings, alias)) return 'present';
  return (row.eras || []).includes(era) ? 'optional' : 'other';
}

/** The key under which the brush actually holds this row (the alias of its era, or the key). */
export function heldKey(row, settings) {
  if (Object.prototype.hasOwnProperty.call(settings, row.key)) return row.key;
  for (const alias of row.aliases || []) if (Object.prototype.hasOwnProperty.call(settings, alias)) return alias;
  return row.key;
}

/** Keys the brush holds that no schema row (or alias) names: shown read-only, never dropped. */
export function unknownKeys(index, settings) {
  return Object.keys(settings).filter((key) => !index.byKey.has(key));
}

/**
 * The rows of one group for one brush, in sections, in schema order.
 * Returns {sections: [{name, items: [{row, state, key}]}], hidden: [{row,state,key}], otherEra: n}
 * `hidden` holds rows whose ui is `hidden` (internal values; listed read-only).
 */
export function groupLayout(index, groupId, settings, era) {
  const sections = [];
  const byName = new Map();
  const hidden = [];
  let otherEra = 0;
  for (const row of index.rowsByGroup.get(groupId) || []) {
    const state = availability(row, settings, era);
    if (state === 'other') { otherEra += 1; continue; }
    const item = {row, state, key: heldKey(row, settings)};
    if (row.ui === 'hidden') { hidden.push(item); continue; }
    const name = row.section || groupId;
    if (!byName.has(name)) { const s = {name, items: []}; byName.set(name, s); sections.push(s); }
    byName.get(name).items.push(item);
  }
  return {sections, hidden, otherEra};
}

/** Count rows per group that a brush can show (for the tab badges). */
export function groupCounts(index, settings, era) {
  const counts = {};
  for (const group of index.groups) {
    const layout = groupLayout(index, group.id, settings, era);
    counts[group.id] = layout.sections.reduce((n, s) => n + s.items.length, 0) + layout.hidden.length;
  }
  return counts;
}

/**
 * What to draw for a row.
 * kind: slider | number | toggle | select | curve | text | readonly | hidden
 * editable is false for read-only kinds and for confidence `unknown` rows until `allowUnverified`.
 */
export function widgetFor(row, {allowUnverified = false} = {}) {
  let kind = row.ui;
  if (kind === 'stepper') kind = 'number';
  if (!['slider', 'number', 'toggle', 'select', 'curve', 'text', 'readonly', 'hidden'].includes(kind)) kind = 'readonly';
  if (kind === 'slider' && !(Array.isArray(row.limits) && row.limits.length === 2)) kind = 'number';
  if (kind === 'select' && !row.enum) kind = 'number';
  if (kind === 'readonly' || kind === 'hidden') return {kind, editable: false, reason: 'This value is read only in the app.'};
  if (row.confidence === 'unknown' && !allowUnverified) {
    return {kind, editable: false, reason: 'The meaning of this key is not established, so it is locked. Unlock unverified keys to edit it.'};
  }
  return {kind, editable: true, reason: null};
}

export function enumOptions(row) {
  const options = Object.entries(row.enum || {}).map(([value, info]) => ({
    value: Number(value), label: info.label || `Value ${value}`, verified: !!info.verified}));
  options.sort((a, b) => a.value - b.value);
  return options;
}

/** A number as the row's `display` shows it: percent, signedPercent, factor, raw, enum. */
export function formatDisplay(row, value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return String(value);
  switch (row.display) {
    case 'percent': return `${trim(value * 100, 1)}%`;
    case 'signedPercent': return `${value > 0 ? '+' : ''}${trim(value * 100, 1)}%`;
    case 'factor': return `×${trim(value, 3)}`;
    default: return trim(value, 4);
  }
}

export function trim(value, places) {
  if (!Number.isFinite(value)) return String(value);
  const text = value.toFixed(places);
  return text.includes('.') ? text.replace(/0+$/, '').replace(/\.$/, '') : text;
}

/** Compact text for any JSON form (curves, rolls, arrays, dates, tags). */
export function formatValue(row, value) {
  if (value === undefined) return '—';
  if (value === null) return 'none';
  if (typeof value === 'number') return row ? formatDisplay(row, value) : trim(value, 6);
  if (typeof value === 'boolean') return value ? 'on' : 'off';
  if (typeof value === 'string') return JSON.stringify(value);
  if (value && Array.isArray(value.points)) return `curve of ${value.points.length} points`;
  return JSON.stringify(value);
}

/** {min, max, obsMin, obsMax, count} for a number row; null when the row has no range. */
export function rangeInfo(row) {
  const limits = Array.isArray(row.limits) ? row.limits : null;
  const observed = row.observed || {};
  const hasObserved = typeof observed.min === 'number' && typeof observed.max === 'number';
  if (!limits && !hasObserved) return null;
  return {
    min: limits ? limits[0] : observed.min, max: limits ? limits[1] : observed.max,
    obsMin: hasObserved ? observed.min : null, obsMax: hasObserved ? observed.max : null,
    count: observed.count || 0,
  };
}

export function observedText(row) {
  const r = rangeInfo(row);
  if (!r || r.obsMin === null) return row.observed && row.observed.count ? `seen in ${row.observed.count} brushes` : 'never observed';
  return `observed ${trim(r.obsMin, 4)} to ${trim(r.obsMax, 4)} in ${r.count} brushes`;
}

export function defaultText(row) {
  return formatValue(row, row.default);
}

export function searchText(row) {
  return `${row.key} ${row.label} ${row.section} ${row.hint || ''}`.toLowerCase();
}

/** {key: 'honoured'|'approx'|'ignored'} for the engine's setBadges (3b). */
export function previewBadges(index) {
  const out = {};
  for (const row of index.rows) { out[row.key] = row.preview; for (const a of row.aliases || []) out[a] = row.preview; }
  return out;
}

// ── curves: {"points": ["{0.250000, 0.330000}", ...]} (F3 "JSON value forms") ──

const POINT = /^\{\s*(-?\d+(?:\.\d+)?(?:e-?\d+)?)\s*,\s*(-?\d+(?:\.\d+)?(?:e-?\d+)?)\s*\}$/i;

export function parsePoint(text) {
  const m = typeof text === 'string' ? POINT.exec(text) : null;
  return m ? [Number(m[1]), Number(m[2])] : null;
}

export function formatPoint(x, y) {
  return `{${x.toFixed(6)}, ${y.toFixed(6)}}`;
}

/** [[x,y],...] in file order, or null when the value is not a well-formed curve. */
export function curvePairs(value) {
  if (!value || !Array.isArray(value.points)) return null;
  const pairs = value.points.map(parsePoint);
  return pairs.every((p) => p !== null) ? pairs : null;
}

/**
 * The curve value for edited points: the lowest-x and highest-x points first,
 * the points between them after, by x - the order the server writes (F3). The
 * `resolution` of a legacy curve is not sent: it is not a setting.
 */
export function curveValue(pairs) {
  const sorted = [...pairs].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const ordered = sorted.length > 2 ? [sorted[0], sorted[sorted.length - 1], ...sorted.slice(1, -1)] : sorted;
  return {points: ordered.map(([x, y]) => formatPoint(clamp01(x), clamp01(y)))};
}

export function clamp01(v) { return Math.min(1, Math.max(0, v)); }

/** Two curve values are the same curve when their point sets match (the server compares so too). */
export function sameCurve(a, b) {
  const pa = curvePairs(a); const pb = curvePairs(b);
  if (!pa || !pb || pa.length !== pb.length) return false;
  const sort = (p) => [...p].sort((u, v) => u[0] - v[0] || u[1] - v[1]);
  const sa = sort(pa); const sb = sort(pb);
  return sa.every((p, i) => Math.abs(p[0] - sb[i][0]) < 5e-7 && Math.abs(p[1] - sb[i][1]) < 5e-7);
}

/** Advisory check of a value against a row: {ok, code, reason}. Python is the authority (F3). */
export function advise(row, value) {
  const fail = (code, reason) => ({ok: false, code, reason});
  switch (row.type) {
    case 'real':
      if (typeof value !== 'number' || !Number.isFinite(value)) return fail('wrong_type', 'a number is needed');
      return {ok: true, outside: Array.isArray(row.limits) && (value < row.limits[0] || value > row.limits[1])};
    case 'int':
      if (typeof value !== 'number' || !Number.isInteger(value)) return fail('wrong_type', 'a whole number is needed');
      if (row.enum && !(String(value) in row.enum)) return fail('not_in_enum', `${value} is not one of the values the library holds`);
      return {ok: true};
    case 'bool':
      return typeof value === 'boolean' ? {ok: true} : fail('wrong_type', 'on or off is needed');
    case 'string_ref':
      return value === null || typeof value === 'string' ? {ok: true} : fail('wrong_type', 'text is needed');
    case 'curve_ref': {
      const pairs = curvePairs(value);
      if (!pairs || pairs.length < 2 || pairs.length > 64) return fail('curve_invalid', 'a curve has 2 to 64 points');
      return pairs.every(([x, y]) => x >= 0 && x <= 1 && y >= 0 && y <= 1) ? {ok: true} : fail('curve_invalid', 'every coordinate is 0 to 1');
    }
    default:
      return fail('read_only', 'this value is read only');
  }
}
