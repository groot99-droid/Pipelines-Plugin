// pure-tests.js - checks of the DOM-free modules (state.js, patch.js, schema.js,
// curve.js math, b64.js). No network, no DOM: selftest.js runs them in the
// browser, and any runner that can import ES modules can run them too
// (`pureTests(schemaIndex)` returns [{name, run}]; a test throws to fail).

import {createDoc, deepEqual} from './state.js';
import {parseEnvelope, envelopeText, shorten, dropResolution, diffRows, PATCH_SCHEMA} from './patch.js';
import {indexSchema, widgetFor, availability, groupLayout, unknownKeys, curveValue, curvePairs, sameCurve, advise,
  formatDisplay, parsePoint, formatPoint, previewBadges} from './schema.js';
import {monotoneAt, addPoint, removePoint, movePoint, MAX_POINTS} from './curve.js';
import {bytesToB64, b64ToBytes, pngInfo, isGrey8} from './b64.js';

function ok(condition, message) { if (!condition) throw new Error(message || 'assertion failed'); }
function eq(actual, expected, message) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error(`${message || 'not equal'}: got ${JSON.stringify(actual)}, wanted ${JSON.stringify(expected)}`);
}

const SETTINGS = () => ({
  plotSpacing: 0.25, plotJitter: 0, shapeInverted: false, name: 'Test', maxSize: 1,
  dynamicsPressureSizeCurve: {points: ['{0.000000, 0.000000}', '{1.000000, 1.000000}']},
  mystery: {'$real32': 'x'},
});
const newDoc = (extra = {}) => createDoc({origin: {kind: 'file'}, name: 'Test', era: 'M220', settings: SETTINGS(), textures: {}, ...extra});

export function pureTests(schema) {
  const tests = [];
  const t = (name, run) => tests.push({name, run});

  // ── state.js ──
  t('state: an untouched doc is clean and has an empty patch', () => {
    const d = newDoc();
    ok(!d.dirty && d.dirtyCount === 0); eq(d.patch(), {}); ok(!d.canUndo && !d.canRedo);
  });
  t('state: set records only the changed key; setting it back removes it', () => {
    const d = newDoc();
    d.set('plotSpacing', 0.5); eq(d.patch(), {plotSpacing: 0.5}); ok(d.dirty && d.isChanged('plotSpacing'));
    eq(d.value('plotSpacing'), 0.5); eq(d.originalValue('plotSpacing'), 0.25);
    d.set('plotSpacing', 0.25); eq(d.patch(), {}); ok(!d.dirty);
  });
  t('state: setting the value a key already has changes nothing', () => {
    const d = newDoc(); eq(d.set('plotSpacing', 0.25), []); ok(!d.canUndo);
  });
  t('state: undo and redo walk the history; a new edit drops the redo branch', () => {
    const d = newDoc();
    d.set('plotSpacing', 0.5); d.set('plotJitter', 2);
    ok(d.canUndo); d.undo(); eq(d.patch(), {plotSpacing: 0.5}); ok(d.canRedo);
    d.undo(); eq(d.patch(), {}); ok(!d.canUndo);
    d.redo(); d.redo(); eq(d.patch(), {plotSpacing: 0.5, plotJitter: 2});
    d.undo(); d.set('maxSize', 0.5); ok(!d.canRedo); eq(d.patch(), {plotSpacing: 0.5, maxSize: 0.5});
  });
  t('state: edits of one key in a drag merge into one undo step', () => {
    const d = newDoc();
    for (const v of [0.3, 0.4, 0.5, 0.6]) d.set('plotSpacing', v, {coalesce: true});
    eq(d.historyLength, 2, 'one snapshot besides the original');
    d.undo(); eq(d.patch(), {});
    d.set('plotSpacing', 0.3, {coalesce: true}); d.endCoalesce(); d.set('plotSpacing', 0.4, {coalesce: true});
    eq(d.historyLength, 3, 'endCoalesce splits steps');
  });
  t('state: setMany is one undo step', () => {
    const d = newDoc(); d.setMany({plotSpacing: 0.9, plotJitter: 1, maxSize: 0.2}, {label: 'patch'});
    eq(d.changedKeys().sort(), ['maxSize', 'plotJitter', 'plotSpacing']); d.undo(); eq(d.patch(), {});
  });
  t('state: reset one key, reset all', () => {
    const d = newDoc(); d.set('plotSpacing', 0.5); d.set('plotJitter', 3);
    ok(d.reset('plotSpacing')); eq(d.patch(), {plotJitter: 3}); ok(!d.reset('plotSpacing'));
    d.setTexture('shape', {png_b64: 'AAAA', width: 1, height: 1, how: 'upload'});
    ok(d.dirty); ok(d.resetAll()); ok(!d.dirty); eq(d.patch(), {}); ok(d.textureChange('shape') === null);
    d.undo(); ok(d.dirty, 'reset all can be undone');
  });
  t('state: texture and thumbnail changes are history steps and make the doc dirty', () => {
    const d = newDoc(); d.setThumbnail({mode: 'omit'}); ok(d.dirty); eq(d.thumbnail().mode, 'omit');
    d.undo(); eq(d.thumbnail().mode, 'keep'); ok(!d.dirty);
  });
  t('state: a key the brush lacks can be added and reset', () => {
    const d = newDoc(); ok(!d.has('dynamicsPressureAttackCurve'));
    d.set('dynamicsPressureAttackCurve', {points: ['{0.000000, 0.000000}', '{1.000000, 1.000000}']});
    ok(d.has('dynamicsPressureAttackCurve') && d.isChanged('dynamicsPressureAttackCurve')); d.reset('dynamicsPressureAttackCurve'); ok(!d.has('dynamicsPressureAttackCurve'));
  });
  t('state: the same curve in another point order is not an edit', () => {
    const d = newDoc();
    d.set('dynamicsPressureSizeCurve', {points: ['{1.000000, 1.000000}', '{0.000000, 0.000000}']}); ok(!d.dirty);
    d.set('dynamicsPressureSizeCurve', curveValue([[0, 0], [0.5, 0.3], [1, 1]])); ok(d.dirty);
  });
  t('state: the original is frozen', () => {
    const d = newDoc(); let threw = false;
    try { 'use strict'; d.original.plotSpacing = 9; } catch (_) { threw = true; }
    ok(threw || d.original.plotSpacing === 0.25, 'the opened settings cannot be edited in place');
  });
  t('state: the secondary brush has its own patch', () => {
    const d = createDoc({origin: {kind: 'file'}, era: 'M220', settings: SETTINGS(), sub: {settings: SETTINGS(), meta: {}}, textures: {}});
    d.set('plotSpacing', 0.7, {layer: 'sub'}); eq(d.patch('main'), {}); eq(d.patch('sub'), {plotSpacing: 0.7}); ok(d.dirty);
  });
  t('state: deepEqual compares JSON values', () => {
    ok(deepEqual({a: [1, {b: 2}]}, {a: [1, {b: 2}]})); ok(!deepEqual({a: 1}, {a: 2})); ok(!deepEqual([1], {0: 1})); ok(deepEqual(null, null)); ok(!deepEqual(0, false));
  });
  t('state: events name the changed keys', () => {
    const d = newDoc(); const seen = []; d.subscribe((e) => seen.push([e.type, ...e.keys]));
    d.set('plotSpacing', 0.5); d.undo(); eq(seen, [['change', 'plotSpacing'], ['undo', 'plotSpacing']]);
  });

  // ── patch.js ──
  t('patch: the envelope parses and round-trips through envelopeText', () => {
    const text = envelopeText({baseId: 'b_e9fe9907bee5', changes: {plotSpacing: 0.2, plotJitter: 1}});
    const r = parseEnvelope(text); ok(r.ok, r.error); eq(r.envelope.schema, PATCH_SCHEMA); eq(r.envelope.changes, {plotSpacing: 0.2, plotJitter: 1}); eq(r.envelope.base_id, 'b_e9fe9907bee5');
    ok(!text.includes('\n'), 'compact: one line');
  });
  t('patch: a fenced block and a bare {changes} parse', () => {
    ok(parseEnvelope('```json\n{"changes": {"plotSpacing": 1}}\n```').ok); ok(parseEnvelope('{"changes": {"a": 1}}').ok);
  });
  t('patch: bad input is refused with a reason', () => {
    for (const bad of ['', 'not json', '[]', '{"changes": {}}', '{"changes": 3}', '{"schema": "other/1", "changes": {"a": 1}}', '{"base_id": "nope", "changes": {"a": 1}}']) {
      const r = parseEnvelope(bad); ok(!r.ok && typeof r.error === 'string' && r.error.length > 5, `refused: ${bad}`);
    }
  });
  t('patch: shorten gives the shortest decimal of the same 32-bit float', () => {
    eq(shorten(0.30000001192092896), 0.3); eq(shorten({a: [0.20000000298023224, 2], b: 'x'}), {a: [0.2, 2], b: 'x'}); const s = shorten(0.123456789012); ok(Math.fround(s) === Math.fround(0.123456789012) && String(s).length <= 11, String(s));
  });
  t('patch: a curve loses its resolution on the way into the patch', () => {
    eq(dropResolution({c: {points: ['{0.000000, 0.000000}', '{1.000000, 1.000000}'], resolution: 1024}, a: 1}), {c: {points: ['{0.000000, 0.000000}', '{1.000000, 1.000000}']}, a: 1});
  });
  t('patch: the diff shows opened, now and after', () => {
    const d = newDoc(); d.set('plotSpacing', 0.5);
    const rows = diffRows(schema, d, {plotSpacing: 0.75, plotJitter: 3});
    eq(rows[0].original, '0.25'); eq(rows[0].now, '0.5'); eq(rows[0].after, '0.75'); eq(rows[1].key, 'plotJitter');
  });

  // ── schema.js ──
  t('schema: 14 groups, every row in a known group, every key unique', () => {
    eq(schema.groups.map((g) => g.id), ['ai', 'stroke', 'stabilization', 'taper', 'shape', 'grain', 'dynamics', 'pencil', 'wetmix', 'color', 'rendering', 'properties', 'materials', 'about']);
    const seen = new Set();
    for (const row of schema.rows) { ok(schema.rowsByGroup.has(row.group), `${row.key} group`); ok(!seen.has(row.key), `${row.key} twice`); seen.add(row.key); }
  });
  t('schema: widgetFor gives a known kind for every row', () => {
    const kinds = new Set(['slider', 'number', 'toggle', 'select', 'curve', 'text', 'readonly', 'hidden']);
    for (const row of schema.rows) { const w = widgetFor(row); ok(kinds.has(w.kind), `${row.key}: ${w.kind}`); }
  });
  t('schema: keys of unverified meaning are locked until unlocked; read-only rows never unlock', () => {
    const unknown = schema.rows.find((r) => r.confidence === 'unknown' && r.ui === 'slider');
    ok(unknown, 'an unknown-confidence slider exists'); ok(!widgetFor(unknown).editable); ok(widgetFor(unknown, {allowUnverified: true}).editable);
    const readonly = schema.rows.find((r) => r.ui === 'readonly'); ok(!widgetFor(readonly, {allowUnverified: true}).editable);
  });
  t('schema: availability separates present, optional and other-era keys', () => {
    const row = schema.byKey.get('dynamicsPressureAttackCurve');
    eq(availability(row, {}, 'M220'), 'optional'); eq(availability(row, {}, 'E4'), 'other'); eq(availability(row, {dynamicsPressureAttackCurve: {}}, 'E4'), 'present');
  });
  t('schema: an unrecognised key is listed, never dropped', () => {
    eq(unknownKeys(schema, {plotSpacing: 1, zzzNotAKey: 2}), ['zzzNotAKey']);
  });
  t('schema: groupLayout puts hidden-ui rows in `hidden`', () => {
    const all = Object.fromEntries(schema.rows.map((r) => [r.key, r.default]));
    const lay = groupLayout(schema, 'materials', all, 'M220');
    ok(lay.hidden.length > 0 && lay.hidden.every((i) => i.row.ui === 'hidden'));
  });
  t('schema: display formats', () => {
    eq(formatDisplay({display: 'percent'}, 0.255), '25.5%'); eq(formatDisplay({display: 'signedPercent'}, 0.5), '+50%');
    eq(formatDisplay({display: 'factor'}, 2), '×2'); eq(formatDisplay({display: 'raw'}, 0.123456), '0.1235');
  });
  t('schema: curve values put the end points first, by the server\'s rule', () => {
    eq(curveValue([[0.5, 0.25], [1, 1], [0, 0]]).points, ['{0.000000, 0.000000}', '{1.000000, 1.000000}', '{0.500000, 0.250000}']);
    eq(curveValue([[1, 1], [0, 0]]).points, ['{0.000000, 0.000000}', '{1.000000, 1.000000}']);
    eq(parsePoint('{0.250000, 0.330000}'), [0.25, 0.33]); eq(parsePoint('{0, 0}') !== null, true); ok(parsePoint('nope') === null);
    eq(formatPoint(0.5, 0.25), '{0.500000, 0.250000}');
    ok(sameCurve({points: ['{0.0, 0.0}', '{1.0, 1.0}']}, {points: ['{1.000000, 1.000000}', '{0.000000, 0.000000}']}));
    eq(curvePairs({points: ['{0.000000, 0.000000}', 'bad']}), null);
  });
  t('schema: advisory validation', () => {
    const real = schema.byKey.get('plotSpacing'); ok(advise(real, 1).ok); ok(!advise(real, 'x').ok); ok(!advise(real, NaN).ok); ok(advise(real, 99).outside === true);
    const flag = schema.rows.find((r) => r.type === 'bool'); ok(advise(flag, true).ok); ok(!advise(flag, 1).ok);
    const en = schema.rows.find((r) => r.type === 'int' && r.enum); ok(!advise(en, 1.5).ok); ok(!advise(en, 987654).ok);
    const curve = schema.rows.find((r) => r.type === 'curve_ref'); ok(advise(curve, curveValue([[0, 0], [1, 1]])).ok); ok(!advise(curve, {points: ['{0.0, 1.5}', '{1.0, 1.0}']}).ok);
  });
  t('schema: every row has a preview badge', () => {
    const badges = previewBadges(schema);
    for (const row of schema.rows) ok(['honoured', 'approx', 'ignored'].includes(badges[row.key]), row.key);
  });
  t('schema: indexSchema refuses a file with no keys', () => {
    let threw = false; try { indexSchema({}); } catch (_) { threw = true; } ok(threw);
  });

  // ── curve.js math ──
  t('curve: monotone interpolation stays inside the points and passes through them', () => {
    const pts = [[0, 0], [0.3, 0.1], [0.7, 0.9], [1, 1]];
    for (const [x, y] of pts) ok(Math.abs(monotoneAt(pts, x) - y) < 1e-9, `through (${x}, ${y})`);
    let last = -1; for (let i = 0; i <= 100; i += 1) { const v = monotoneAt(pts, i / 100); ok(v >= last - 1e-9 && v >= 0 && v <= 1, 'monotone'); last = v; }
  });
  t('curve: points are added, moved between neighbours and removed down to two', () => {
    let pairs = [[0, 0], [1, 1]];
    ({pairs} = addPoint(pairs, 0.5, 0.2)); eq(pairs.length, 3);
    pairs = movePoint(pairs, 1, 2, 5); ok(pairs[1][0] < 1 && pairs[1][1] === 1, 'clamped between neighbours and to 0..1');
    ({pairs} = removePoint(pairs, 1)); eq(pairs.length, 2); ({pairs} = removePoint(pairs, 0)); eq(pairs.length, 2, 'two points stay');
    let many = [[0, 0], [1, 1]]; for (let i = 1; i < 40; i += 1) ({pairs: many} = addPoint(many, i / 41, 0.5)); ok(many.length <= MAX_POINTS);
  });

  // ── b64.js ──
  t('b64: bytes round trip and PNG header facts', () => {
    const bytes = new Uint8Array(70000).map((_, i) => i % 251); eq(Array.from(b64ToBytes(bytesToB64(bytes)).slice(69990)), Array.from(bytes.slice(69990)));
    const header = new Uint8Array(33); header.set([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0, 0, 0, 13, 0x49, 0x48, 0x44, 0x52, 0, 0, 4, 52, 0, 0, 1, 68, 8, 0, 0, 0, 0]);
    eq(pngInfo(header), {width: 1076, height: 324, bitDepth: 8, colorType: 0, interlace: 0}); ok(isGrey8(pngInfo(header))); ok(pngInfo(new Uint8Array(40)) === null);
  });

  return tests;
}
