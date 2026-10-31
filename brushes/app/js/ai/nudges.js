// ai/nudges.js - the offline "suggestions": preset nudges (softer, grainier,
// more taper ...) as deterministic patch generators over schema keys. No model
// is involved and nothing is learned: each preset is a short, readable list of
// moves on settings the brush actually holds, clamped to the schema's limits.
// A preset is a starting point, not a promise about how the stroke will look.
// The patch it makes goes through the same server check and the same diff as
// a patch from Claude before anything is applied.
//
// Pure: no DOM, no network, importable from Node.

import {availability, heldKey, trim} from '../schema.js';

/**
 * A move: [key, op, amount].
 *   add   value + amount * strength
 *   mul   value * (1 + (amount - 1) * strength)
 *   away  push the magnitude away from 0 by amount * strength (keeps the sign; 0 goes positive)
 * Keys whose meaning the schema marks "uncertain" are not used.
 */
export const NUDGES = [
  {id: 'softer', label: 'Softer', about: 'Lighter at the top end, fades in and out, a smoother path.', moves: [
    ['maxOpacity', 'mul', 0.9], ['dynamicsPressureOpacity', 'add', 0.15], ['taperStartLength', 'add', 0.1],
    ['taperEndLength', 'add', 0.15], ['taperOpacity', 'add', 0.1], ['plotSmoothing', 'add', 0.1]]},
  {id: 'harder', label: 'Harder', about: 'Fuller opacity, less pressure fade, shorter tapers. The edge of the stamp itself is in the shape image.', moves: [
    ['maxOpacity', 'add', 0.1], ['dynamicsPressureOpacity', 'add', -0.15], ['taperStartLength', 'mul', 0.6],
    ['taperEndLength', 'mul', 0.6], ['taperOpacity', 'mul', 0.6], ['dynamicsJitterOpacity', 'mul', 0.5]]},
  {id: 'grainier', label: 'Grainier', about: 'The grain shows more, and shows more at light pressure. Only brushes with a grain-depth setting can change.', moves: [
    ['grainDepth', 'add', 0.25], ['grainDepthMinimum', 'add', 0.15], ['grainDepthJitter', 'add', 0.05]]},
  {id: 'smoother', label: 'Smoother', about: 'More path smoothing, less jitter and scatter, less grain, tighter spacing.', moves: [
    ['plotSmoothing', 'add', 0.25], ['plotJitter', 'mul', 0.5], ['dynamicsJitterSize', 'mul', 0.5], ['dynamicsJitterOpacity', 'mul', 0.5],
    ['shapeScatter', 'mul', 0.5], ['grainDepth', 'mul', 0.6], ['grainDepthMinimum', 'mul', 0.6], ['plotSpacing', 'mul', 0.8]]},
  {id: 'more-taper', label: 'More taper', about: 'Longer starts and ends that fade.', moves: [
    ['taperStartLength', 'add', 0.2], ['taperEndLength', 'add', 0.3], ['taperOpacity', 'add', 0.1],
    ['pencilTaperStartLength', 'add', 0.2], ['pencilTaperEndLength', 'add', 0.3], ['pencilTaperOpacity', 'add', 0.1]]},
  {id: 'less-taper', label: 'Less taper', about: 'Shorter starts and ends.', moves: [
    ['taperStartLength', 'mul', 0.5], ['taperEndLength', 'mul', 0.5], ['taperOpacity', 'mul', 0.5],
    ['pencilTaperStartLength', 'mul', 0.5], ['pencilTaperEndLength', 'mul', 0.5], ['pencilTaperOpacity', 'mul', 0.5]]},
  {id: 'more-pressure', label: 'More pressure response', about: 'Pressure changes size and opacity more.', moves: [
    ['dynamicsPressureSize', 'away', 0.25], ['dynamicsPressureOpacity', 'away', 0.25]]},
  {id: 'less-pressure', label: 'Less pressure response', about: 'Pressure changes size and opacity less.', moves: [
    ['dynamicsPressureSize', 'mul', 0.6], ['dynamicsPressureOpacity', 'mul', 0.6]]},
  {id: 'wetter', label: 'Wetter', about: 'More dilution and charge; wet edges where the era has them.', moves: [
    ['dynamicsMix', 'add', 0.2], ['dynamicsLoad', 'add', 0.15], ['wetEdgesAmount', 'add', 0.1]]},
  {id: 'drier', label: 'Drier', about: 'Less dilution, charge and wet edge.', moves: [
    ['dynamicsMix', 'mul', 0.5], ['dynamicsLoad', 'mul', 0.7], ['wetEdgesAmount', 'mul', 0.5]]},
  {id: 'bigger', label: 'Bigger', about: 'A larger maximum size.', moves: [['maxSize', 'mul', 1.3]]},
  {id: 'smaller', label: 'Smaller', about: 'A smaller maximum size.', moves: [['maxSize', 'mul', 0.75]]},
];

export const STRENGTHS = [{id: 'gentle', label: 'Gentle', factor: 0.5}, {id: 'normal', label: 'Normal', factor: 1}, {id: 'strong', label: 'Strong', factor: 1.6}];

const round = (v) => Math.round(v * 10000) / 10000;

function move(op, value, amount, strength) {
  if (op === 'add') return value + amount * strength;
  if (op === 'mul') return value * (1 + (amount - 1) * strength);
  if (op === 'away') return Math.sign(value || 1) * (Math.abs(value) + amount * strength);
  return value;
}

/**
 * makeNudge(id, {schema, settings, era, strength}) ->
 *   {id, label, about, changes: {key: value}, skipped: [{key, reason}]}
 * `settings` are the effective settings of the primary brush. Only keys the
 * brush holds, in this era, with a number value, are moved; each result is
 * clamped to the row's limits and rounded to 4 places. A move that would not
 * change the value (already at a limit) is skipped and said so.
 */
export function makeNudge(id, {schema, settings, era, strength = 1}) {
  const nudge = NUDGES.find((n) => n.id === id);
  if (!nudge) throw new Error(`no nudge ${id}`);
  const changes = {}; const skipped = [];
  for (const [rowKey, op, amount] of nudge.moves) {
    const row = schema.byKey.get(rowKey);
    if (!row) { skipped.push({key: rowKey, reason: 'not in the schema'}); continue; }
    const state = availability(row, settings, era);
    if (state !== 'present') { skipped.push({key: rowKey, reason: state === 'optional' ? 'this brush does not hold it' : `${era || 'this'} era has no such setting`}); continue; }
    const key = heldKey(row, settings);
    const value = settings[key];
    if (typeof value !== 'number' || !Number.isFinite(value)) { skipped.push({key, reason: 'not a number'}); continue; }
    if (op === 'mul' && value === 0) { skipped.push({key, reason: 'is 0, and a multiple of 0 is 0'}); continue; }
    let next = move(op, value, amount, strength);
    if (Array.isArray(row.limits)) next = Math.min(row.limits[1], Math.max(row.limits[0], next));
    next = round(next);
    if (next === round(value)) { skipped.push({key, reason: `already at ${trim(value, 4)}, the end of its range`}); continue; }
    changes[key] = next;
  }
  return {id: nudge.id, label: nudge.label, about: nudge.about, changes, skipped};
}

/** Pure checks: [{name, run}] given the indexed schema. */
export function nudgeTests(schema) {
  const tests = [];
  const t = (name, run) => tests.push({name, run});
  const ok = (c, m) => { if (!c) throw new Error(m || 'assertion failed'); };
  const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${m || 'not equal'}: got ${JSON.stringify(a)}, wanted ${JSON.stringify(b)}`); };
  const settingsFor = (era, patch = {}) => {
    const s = {name: 'T'};
    for (const row of schema.rows) if ((row.eras || []).includes(era) && row.default !== undefined && !(row.aliases || []).length) s[row.key] = row.default;
    return {...s, ...patch};
  };
  const mid = {maxOpacity: 0.8, dynamicsPressureOpacity: 0.3, dynamicsPressureSize: -0.4, taperStartLength: 0.2, taperEndLength: 0.3, taperOpacity: 0.2, plotSmoothing: 0.3,
    plotJitter: 1, grainDepth: 0.5, grainDepthMinimum: 0.2, dynamicsMix: 0.3, dynamicsLoad: 0.5, maxSize: 2, plotSpacing: 0.1, dynamicsJitterSize: 0.4, dynamicsJitterOpacity: 0.4, shapeScatter: 0.6};
  t('ai nudges: every preset exists once and has words', () => {
    eq(new Set(NUDGES.map((n) => n.id)).size, NUDGES.length); for (const n of NUDGES) { ok(n.label && n.about && n.moves.length, n.id); for (const [key] of n.moves) ok(schema.byKey.has(key), `${n.id} names ${key}`); }
  });
  t('ai nudges: each preset changes only keys the brush holds, keeps them in their limits, and never makes NaN', () => {
    const settings = settingsFor('M220', mid);
    for (const n of NUDGES) for (const s of STRENGTHS) {
      const r = makeNudge(n.id, {schema, settings, era: 'M220', strength: s.factor});
      for (const [key, value] of Object.entries(r.changes)) {
        ok(Object.prototype.hasOwnProperty.call(settings, key), `${n.id} wrote a key the brush lacks: ${key}`);
        ok(typeof value === 'number' && Number.isFinite(value), `${n.id} ${key}`);
        const row = schema.byKey.get(key); if (Array.isArray(row.limits)) ok(value >= row.limits[0] && value <= row.limits[1], `${n.id} ${key}=${value}`);
        ok(value !== settings[key], `${n.id} ${key} did not move`);
      }
    }
  });
  t('ai nudges: opposite presets move opposite ways, and a stronger strength moves further', () => {
    const settings = settingsFor('M220', mid);
    const get = (id, key, strength = 1) => makeNudge(id, {schema, settings, era: 'M220', strength}).changes[key];
    ok(get('bigger', 'maxSize') > mid.maxSize && get('smaller', 'maxSize') < mid.maxSize);
    ok(get('wetter', 'dynamicsMix') > mid.dynamicsMix && get('drier', 'dynamicsMix') < mid.dynamicsMix);
    ok(get('more-taper', 'taperEndLength') > mid.taperEndLength && get('less-taper', 'taperEndLength') < mid.taperEndLength);
    ok(get('grainier', 'grainDepth') > mid.grainDepth && get('smoother', 'grainDepth') < mid.grainDepth);
    ok(Math.abs(get('more-pressure', 'dynamicsPressureSize')) > Math.abs(mid.dynamicsPressureSize), 'more pressure response grows a negative value in size');
    ok(Math.abs(get('less-pressure', 'dynamicsPressureSize')) < Math.abs(mid.dynamicsPressureSize));
    ok(get('bigger', 'maxSize', 1.6) > get('bigger', 'maxSize', 0.5));
  });
  t('ai nudges: a brush of an old era is only offered what its era holds, with the reason for the rest', () => {
    const settings = settingsFor('E0', {});
    const r = makeNudge('grainier', {schema, settings, era: 'E0'});
    eq(r.changes, {}); ok(r.skipped.length === 3 && r.skipped.every((s) => /era has no such setting/.test(s.reason)), JSON.stringify(r.skipped));
    const soft = makeNudge('softer', {schema, settings: {...settings, maxOpacity: 0.7}, era: 'E0'}); ok(soft.changes.maxOpacity < 0.7);
  });
  t('ai nudges: a value at its limit or a zero under a multiple is skipped with a reason', () => {
    const settings = settingsFor('M220', {maxOpacity: 1, plotJitter: 0, taperStartLength: 0});
    const harder = makeNudge('harder', {schema, settings, era: 'M220'}); ok(harder.skipped.some((s) => s.key === 'maxOpacity' && /end of its range/.test(s.reason)));
    ok(harder.skipped.some((s) => s.key === 'taperStartLength' && /multiple of 0/.test(s.reason)));
  });
  return tests;
}
