// tests.js - DOM-free checks of the stroke engine, in the shape of js/pure-tests.js:
// pureEngineTests(schemaIndex) -> [{name, run}]; a test throws to fail. They run
// in the browser from selftest.js and in any runner that imports ES modules.
//
// The checks that matter most: the same settings give the same pixels; every key
// the engine claims to use really changes the picture, and every key it calls
// ignored really does not (so a badge cannot lie); no era's key set throws.

import {mulberry32, stampRandoms, hashBytes, STAMP_DRAWS} from './rng.js';
import {makeCurve, curvePoints, dynamicsFactor} from './curves.js';
import {testPath, drawnPath, sampleAt, VIEW_W} from './path.js';
import {readModel, CALIBRATION as C, baseDiameter, strokeOpacity} from './model.js';
import {buildStamps, taperFactor, taperReference, expectedCount, speedFactor} from './stamps.js';
import {makeMask, coverageFrom} from './mips.js';
import {standinShape, standinGrain} from './standins.js';
import {renderCoverage, coverageHash} from './render.js';
import {SUPPORT, describeSupport, engineBadges, supportDifferences, applyEngineSupport} from './support.js';
import {indexSchema} from '../schema.js';

function ok(c, m) { if (!c) throw new Error(m || 'assertion failed'); }
function eq(a, b, m) { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${m || 'not equal'}: got ${JSON.stringify(a)}, wanted ${JSON.stringify(b)}`); }
const near = (a, b, tol, m) => ok(Math.abs(a - b) <= tol, `${m || 'near'}: ${a} vs ${b} (tolerance ${tol})`);

const LINE = {points: ['{0.000000, 0.000000}', '{1.000000, 1.000000}']};
const BEND = {points: ['{0.000000, 0.000000}', '{0.500000, 0.900000}', '{1.000000, 1.000000}']};

/** A rich baseline brush: every key the engine reads has a middling value. */
export function baselineParams() {
  return {
    minSize: 0.1, maxSize: 0.5, previewSize: 0.5, paintSize: 0.35, minOpacity: 0.1, maxOpacity: 1, paintOpacity: 0.8, stamp: false,
    plotSpacing: 0.2, plotJitter: 0.3, dynamicsFalloff: 0.1,
    taperStartLength: 0.3, taperEndLength: 0.4, taperSize: 0.5, taperOpacity: 0.3,
    pencilTaperStartLength: 0.25, pencilTaperEndLength: 0.35, pencilTaperSize: 0.45, pencilTaperOpacity: 0.25,
    shapeScatter: 0.2, shapeRotation: 0.5, shapeRandomise: false, shapeAzimuth: false, shapeAngle: 0.3, shapeRoundness: 0.8,
    shapeFlipXJitter: false, shapeFlipYJitter: false, shapeInverted: false,
    textureMovement: 0.5, textureZoom: 0.3, textureScale: 2, textureInverted: false, grainDepth: 0.7,
    dynamicsSpeedSize: 0.3, dynamicsSpeedOpacity: 0.3, dynamicsJitterSize: 0.2, dynamicsJitterOpacity: 0.2,
    dynamicsPressureSize: 0.7, dynamicsPressureOpacity: 0.4, dynamicsPressureSizeCurve: LINE, dynamicsPressureOpacityCurve: LINE,
    dynamicsTiltSize: 0.4, dynamicsTiltOpacity: 0.3, dynamicsGlazedFlow: 0.6, renderingMaxTransfer: false,
  };
}

/** A lopsided mask (bright left and top, dark right and bottom, an ellipse) so flips and rotations show. */
export function asymmetricLum(w = 64, h = 48) {
  const lum = new Uint8Array(w * h);
  for (let y = 0; y < h; y += 1) {
    for (let x = 0; x < w; x += 1) {
      const dx = (x + 0.5) / w * 2 - 1; const dy = (y + 0.5) / h * 2 - 1;
      lum[y * w + x] = Math.hypot(dx, dy) < 1 ? Math.round(255 * (1 - 0.8 * (x / w)) * (1 - 0.6 * (y / h))) : 0;
    }
  }
  return {lum, w, h};
}
const GRAIN = standinGrain('Brush-Preset-Test').grain;

function assetsFor(params) {
  const {lum, w, h} = asymmetricLum();
  return {mask: makeMask(lum, null, w, h, readModel(params).shapeInverted), grain: GRAIN};
}
const view = (over = {}) => ({w: 424, h: 130, kind: 's-curve', level: 0.6, pointer: 'pencil', tilt: 0.5, seed: 7, sizeSource: 'preview', tall: false, ...over});
const render = (params, over, assets) => renderCoverage(params, view(over), assets || assetsFor(params));

/** The value to try for a key: {value, view, drop} where `view` forces the situation in which the key can matter. */
function probe(key, base) {
  const v = base[key];
  const special = {
    stamp: {value: true, view: {kind: 'auto'}},
    paintSize: {value: 0.6, view: {sizeSource: 'paint'}},
    dynamicsGlazeFlow: {value: 0.2, drop: ['dynamicsGlazedFlow']},
    dynamicsPressureSizeCurve: {value: BEND}, dynamicsPressureOpacityCurve: {value: BEND},
    previewSize: {value: 0.9, view: {kind: 'tap'}}, minSize: {value: 0.4, view: {kind: 'tap'}},
    textureScale: {value: 5}, shapeAngle: {value: 1.2}, shapeRoundness: {value: 0.4},
  };
  let out;
  if (special[key]) out = special[key];
  else if (typeof v === 'boolean') out = {value: !v};
  else out = {value: v < 0.5 ? v + 0.4 : v - 0.4};
  if (/^taper/.test(key)) out = {...out, view: {...(out.view || {}), pointer: 'touch'}};      // the touch taper set is only used by a finger
  if (key === 'shapeAzimuth') out = {...out, base: {shapeRotation: 0.9}};
  return out;
}

/** The value to try for a key the engine ignores, or undefined when it cannot be set generically. */
function ignoredProbe(row) {
  if (row.type === 'real') return typeof row.default === 'number' && Math.abs(row.default - 0.37) > 0.05 ? 0.37 : 0.81;
  if (row.type === 'bool') return row.default !== true;
  if (row.type === 'int' && row.enum) { const vals = Object.keys(row.enum).map(Number); return vals.find((x) => x !== row.default) ?? vals[0]; }
  if (row.type === 'curve_ref') return BEND;
  if (row.type === 'string_ref' && row.key === 'name') return 'a different name';
  return undefined;
}

export function pureEngineTests(schema) {
  const tests = [];
  const t = (name, run) => tests.push({name, run});

  // ── rng, curves ──
  t('rng: mulberry32 is deterministic and in [0, 1)', () => {
    const a = mulberry32(12345); const b = mulberry32(12345);
    const first = [a(), a(), a()]; eq(first, [b(), b(), b()]);
    ok(first.every((x) => x >= 0 && x < 1)); ok(mulberry32(12346)() !== first[0]);
  });
  t('rng: a stamp’s random values depend on (seed, index) only', () => {
    const x = new Float64Array(STAMP_DRAWS); const y = new Float64Array(STAMP_DRAWS);
    stampRandoms(5, 40, x); stampRandoms(5, 41, y); stampRandoms(5, 40, y.fill(0));
    eq(Array.from(x), Array.from(y)); const z = new Float64Array(STAMP_DRAWS); stampRandoms(6, 40, z); ok(z[0] !== x[0]);
    ok(hashBytes(x) === hashBytes(y));
  });
  t('curves: no curve and a straight curve are the identity; a bent curve is monotone and bends', () => {
    ok(makeCurve(undefined).identity && makeCurve(LINE).identity && makeCurve({points: ['bad']}).identity);
    const bent = makeCurve(BEND); ok(!bent.identity);
    let last = -1; for (let i = 0; i <= 50; i += 1) { const y = bent.at(i / 50); ok(y >= last - 1e-9, 'not monotone'); last = y; }
    near(bent.at(0.5), 0.9, 0.02); near(bent.at(-1), 0, 1e-9); near(bent.at(2), 1, 1e-9);
  });
  t('curves: points given out of order are sorted', () => {
    eq(curvePoints({points: ['{1.000000, 1.000000}', '{0.000000, 0.000000}', '{0.500000, 0.900000}']}).map((p) => p[0]), [0, 0.5, 1]);
  });
  t('curves: dynamics factors (positive follows the curve, negative opposes it, zero does nothing)', () => {
    near(dynamicsFactor(1, 0.3), 0.3, 1e-9); near(dynamicsFactor(0.5, 0.2), 0.6, 1e-9); near(dynamicsFactor(0, 0.2), 1, 1e-9); near(dynamicsFactor(-1, 0.25), 0.75, 1e-9);
    near(speedFactor(0.5, 1), 0.5, 1e-9); near(speedFactor(-0.5, 1), 1, 1e-9); near(speedFactor(-0.5, 0), 0.5, 1e-9);
  });

  // ── paths ──
  t('path: the S-curve runs x 87 to 975 on Procreate’s thumbnail path; a tap has no length', () => {
    const p = testPath({kind: 's-curve'}); const q = {};
    sampleAt(p, 0, q); near(q.x, 87, 0.01); near(q.y, 179.2 + 28.8 * Math.sin(2 * Math.PI * (87 - 55) / 1050), 0.2);
    sampleAt(p, p.length, q); near(q.x, 975, 1.5);
    ok(p.length > 880 && p.length < 1000, `length ${p.length}`);
    const tap = testPath({kind: 'tap'}); eq(tap.length, 0); eq(tap.n, 1);
  });
  t('path: pressure is low at both ends and higher in the middle; a finger has constant pressure', () => {
    const p = testPath({kind: 's-curve'}); const q = {};
    sampleAt(p, 0, q); const p0 = q.p; sampleAt(p, p.length / 2, q); const mid = q.p; sampleAt(p, p.length, q);
    ok(p0 < 0.1 && q.p < 0.15 && mid > 0.4, `${p0} ${mid} ${q.p}`);
    const finger = testPath({kind: 's-curve', pointer: 'touch'}); sampleAt(finger, 10, q); const a = q.p; sampleAt(finger, 500, q); eq(a, q.p);
  });
  t('path: a drawn stroke resamples every unit and keeps its length', () => {
    const raw = [{x: 100, y: 100, t: 0}, {x: 200, y: 100, t: 100}, {x: 300, y: 100, t: 200}];
    const p = drawnPath(raw, {pointerType: 'mouse'}); near(p.length, 200, 0.5); ok(p.n >= 199);
  });

  // ── stamps ──
  const flat = {minSize: 0.2, maxSize: 0.2, previewSize: 0, dynamicsPressureSize: 0, plotSpacing: 0.5};
  t('stamps: spacing count = floor(length / step) + 1 on a straight, steady stroke', () => {
    const path = testPath({kind: 'line'}); const model = readModel({...flat});
    const D = baseDiameter(model); const step = C.SPACING_K * 0.5 * D;
    const built = buildStamps(model, path, {pointer: 'touch', seed: 1}); eq(built.stamps.length, expectedCount(path.length, step), 'count');
    const wider = buildStamps(readModel({...flat, plotSpacing: 1}), path, {pointer: 'touch', seed: 1}); ok(wider.stamps.length < built.stamps.length);
    near(built.stamps[1].s - built.stamps[0].s, step, 1e-6);
  });
  t('stamps: a spacing of 0 still ends (a floor on the step) and gives about length / floor stamps', () => {
    const built = buildStamps(readModel({...flat, plotSpacing: 0}), testPath({kind: 'line'}), {pointer: 'touch', minStepFrac: 0.05});
    ok(built.stamps.length > 100 && built.stamps.length < 14001, `${built.stamps.length}`);
  });
  t('stamps: the same stroke from fewer or more control points gives the same stamps', () => {
    const a = drawnPath([{x: 100, y: 50, t: 0}, {x: 500, y: 50, t: 400}], {pointerType: 'mouse'});
    const pts = []; for (let i = 0; i <= 40; i += 1) pts.push({x: 100 + 10 * i, y: 50, t: i * 10});
    const b = drawnPath(pts, {pointerType: 'mouse'}); const model = readModel({...flat});
    const sa = buildStamps(model, a, {pointer: 'touch'}).stamps; const sb = buildStamps(model, b, {pointer: 'touch'}).stamps;
    eq(sa.length, sb.length); near(sa[sa.length - 1].x, sb[sb.length - 1].x, 0.01);
  });
  t('stamps: taper endpoints (size and opacity at the two ends; flat in the middle; none for a tap)', () => {
    const taper = {start: 0.2, end: 0.2, size: 0.8, opacity: 0.5}; const L = 800; const Lref = taperReference(L, 100);
    near(taperFactor(0, L, Lref, taper, taper.size), 0.2, 1e-9); near(taperFactor(L, L, Lref, taper, taper.size), 0.2, 1e-9);
    near(taperFactor(L / 2, L, Lref, taper, taper.size), 1, 1e-9); near(taperFactor(0, L, Lref, taper, taper.opacity), 0.5, 1e-9);
    eq(taperFactor(0, 0, 0, taper, taper.size), 1); eq(taperFactor(0, L, Lref, taper, 0), 1);
    const model = readModel({...flat, taperStartLength: 0.5, taperEndLength: 0.5, taperSize: 1, plotSpacing: 0.1});
    const built = buildStamps(model, testPath({kind: 'line'}), {pointer: 'touch'}); const first = built.stamps[0]; const mid = built.stamps[built.stamps.length >> 1];
    ok(first.d < 0.1 * mid.d, `first ${first.d} mid ${mid.d}`);
  });
  t('stamps: a pen uses the pencil taper set when the brush has one, a finger the touch set', () => {
    const p = {...flat, taperStartLength: 0, taperEndLength: 0, taperSize: 0, pencilTaperStartLength: 0.5, pencilTaperEndLength: 0.5, pencilTaperSize: 1, plotSpacing: 0.1};
    const path = testPath({kind: 'line', pointer: 'touch'});
    const pen = buildStamps(readModel(p), testPath({kind: 'line', level: 1}), {pointer: 'pencil'}); const finger = buildStamps(readModel(p), path, {pointer: 'touch'});
    ok(pen.stamps[0].d < 0.2 * pen.stamps[pen.stamps.length >> 1].d, 'pen tapers'); near(finger.stamps[0].d, finger.stamps[finger.stamps.length >> 1].d, 1e-6, 'finger does not');
  });
  t('stamps: jitter is seeded: same seed same stamps, another seed other stamps, none without jitter', () => {
    const model = readModel({...flat, plotJitter: 1, dynamicsJitterSize: 0.5, dynamicsJitterOpacity: 0.5, shapeScatter: 1, plotSpacing: 0.4});
    const path = testPath({kind: 'line'});
    const a = buildStamps(model, path, {pointer: 'touch', seed: 3}).stamps; const b = buildStamps(model, path, {pointer: 'touch', seed: 3}).stamps; const c = buildStamps(model, path, {pointer: 'touch', seed: 4}).stamps;
    eq(a, b); ok(JSON.stringify(a) !== JSON.stringify(c));
    const calm = buildStamps(readModel({...flat, plotSpacing: 0.4}), path, {pointer: 'touch', seed: 3}).stamps; ok(calm.every((s) => Math.abs(s.y - 162) < 1e-3 && s.angle === 0));
    const R = 1 * C.JITTER_K * baseDiameter(model); ok(a.every((s) => Math.hypot(s.x - sampleAt(path, s.s, {}).x, s.y - 162) <= R + 1e-6), 'position jitter stays inside its radius');
  });
  t('stamps: follow-stroke rotation gives 45 degrees on a diagonal; a fixed angle and randomising behave', () => {
    const diagonal = drawnPath([{x: 100, y: 100, t: 0}, {x: 300, y: 300, t: 200}, {x: 500, y: 500, t: 400}], {pointerType: 'mouse'});
    const follow = buildStamps(readModel({...flat, shapeRotation: 1}), diagonal, {pointer: 'touch'}).stamps; near(follow[5].angle, Math.PI / 4, 0.02);
    const reverse = buildStamps(readModel({...flat, shapeRotation: -1}), diagonal, {pointer: 'touch'}).stamps; near(reverse[5].angle, -Math.PI / 4, 0.02);
    const fixed = buildStamps(readModel({...flat, shapeAngle: 0.7}), diagonal, {pointer: 'touch'}).stamps; ok(fixed.every((s) => s.angle === 0.7));
    const random = buildStamps(readModel({...flat, shapeRandomise: true}), diagonal, {pointer: 'touch'}).stamps; ok(new Set(random.map((s) => s.angle.toFixed(3))).size > random.length / 2);
  });
  t('stamps: pressure to size follows the curve (full pressure effect, identity curve: size tracks pressure)', () => {
    const model = readModel({...flat, minSize: 0.5, maxSize: 0.5, dynamicsPressureSize: 1, plotSpacing: 0.3});
    const built = buildStamps(model, testPath({kind: 'line', level: 1}), {pointer: 'pencil'}); const q = {}; const path = testPath({kind: 'line', level: 1});
    for (const s of [built.stamps[3], built.stamps[built.stamps.length >> 1]]) { sampleAt(path, s.s, q); near(s.d, baseDiameter(model) * q.p, 0.01, 'size = diameter x pressure'); }
  });
  t('stamps: flow keeps very fine spacing from saturating a low flow', () => {
    const p = {...flat, dynamicsGlazedFlow: 0.1};
    const fine = render({...p, plotSpacing: 0.01}, {kind: 'line', pointer: 'touch'}); const coarse = render({...p, plotSpacing: 0.1}, {kind: 'line', pointer: 'touch'});
    const mean = (r) => { let s = 0; let n = 0; const a = r.acc; for (let i = 0; i < a.length; i += 1) if (a[i] > 0.001) { s += a[i]; n += 1; } return s / n; };
    ok(mean(fine) < 0.7, `fine spacing mean ${mean(fine)}`); near(mean(fine), mean(coarse), 0.15, 'about the same density');
  });

  // ── masks, standins, raster ──
  t('mask: invert flips the coverage (shape polarity), and the image’s own alpha scales it', () => {
    const lum = Uint8Array.from([0, 255, 100, 200]); const plain = coverageFrom(lum, null, false); const inv = coverageFrom(lum, null, true);
    eq(Array.from(plain), [0, 255, 100, 200]); eq(Array.from(inv), [255, 0, 155, 55]);
    eq(Array.from(coverageFrom(lum, Uint8Array.from([255, 255, 0, 128]), false)), [0, 255, 0, 100]);
    const a = makeMask(lum, null, 2, 2, false); const b = makeMask(lum, null, 2, 2, true); ok(a.levels[0].data[1] === 255 && b.levels[0].data[1] === 0);
  });
  t('raster: inverting the shape changes the picture, and a stamp’s ink area is about its area', () => {
    const p = baselineParams(); const plain = render(p); const inv = render({...p, shapeInverted: true}); ok(plain.hash !== inv.hash);
    const full = standinShape('Brush-Preset-Blank', false).mask;                              // a flat white square
    const single = renderCoverage({minSize: 0.5, maxSize: 0.5, previewSize: 0, dynamicsPressureSize: 0, plotSpacing: 2, shapeRotation: 0, stamp: true}, view({kind: 'tap', pointer: 'touch'}), {mask: full});
    let sum = 0; for (let i = 0; i < single.acc.length; i += 1) sum += single.acc[i];
    const side = baseDiameter(readModel({minSize: 0.5, maxSize: 0.5, previewSize: 0}), 'preview', 'tap') * (424 / VIEW_W); near(sum, side * side, side * side * 0.06, 'covered pixels');
  });
  t('standins: a blank shape is exact, a bundled name gives a labelled stand-in, a blank grain is exact', () => {
    ok(standinShape('Brush-Preset-Blank.png').exact); const oval = standinShape('Brush-Preset-Oval.png'); ok(!oval.exact && /stand-in/.test(oval.label) && oval.mask.fx / oval.mask.fy === 2);
    ok(standinShape('Brush-Preset-Hard.png').kind === 'hard' && standinShape('Brush-Preset-Ultra-Soft.png').kind === 'ultra-soft' && standinShape('Something-Else.png').kind === 'generic');
    ok(standinGrain('Brush-Preset-Blank.png').exact && standinGrain('Brush-Preset-Blank.png').grain === null); const g = standinGrain('Paper-Rough.png'); ok(!g.exact && g.grain && /stand-in/.test(g.label));
    ok(standinShape('Brush-Preset-Hard.png').mask.levels[0].data.join() !== standinShape('Brush-Preset-Soft.png').mask.levels[0].data.join());
  });
  t('raster: grain depth 0 or a blank grain equals no grain; a deeper grain changes the picture', () => {
    const p = baselineParams(); const none = render(p, {}, {mask: assetsFor(p).mask, grain: null});
    const zero = render({...p, grainDepth: 0}, {}, assetsFor(p)); eq(zero.hash, none.hash, 'depth 0'); ok(render(p).hash !== none.hash, 'grain changes pixels');
  });
  t('raster: the same settings give the same pixels, twice and from fresh buffers', () => {
    const p = baselineParams(); const a = render(p); const b = render(p); eq(a.hash, b.hash); ok(a.stamps > 20 && a.ops > 1000);
    ok(a.acc.every((v) => Number.isFinite(v) && v >= 0 && v <= 1.0001), 'coverage within 0..1');
    ok(render(p, {seed: 8}).hash !== a.hash, 'another seed gives another picture');
  });
  t('raster: coverage stays inside the canvas for a stroke that leaves it', () => {
    const r = render(baselineParams(), {w: 64, h: 20}); ok(r.acc.length === 64 * 20 && r.acc.every(Number.isFinite));
  });

  // ── what is used and what is not ──
  t('settings: every key the engine claims to use changes the picture', () => {
    const base = baselineParams(); const dead = [];
    for (const key of Object.keys(SUPPORT)) {
      if (key === 'bundledShapePath' || key === 'bundledGrainPath') continue;          // chosen by name in assets.js: see the next test
      const p = probe(key, base); const params = {...base, ...(p.base || {})}; for (const d of p.drop || []) delete params[d];
      const a = render(params, p.view); const changed = {...params, [key]: p.value}; const b = render(changed, p.view, assetsFor(changed));
      if (a.hash === b.hash) dead.push(key);
    }
    ok(!dead.length, `these keys are listed as used but changed nothing: ${dead.join(', ')}`);
  });
  t('settings: a bundled shape or grain name changes the stand-in', () => {
    ok(standinShape('Brush-Preset-Oval.png').mask.levels[0].data.length !== standinShape('Brush-Preset-Hard.png').mask.levels[0].data.length);
    ok(standinGrain('Brush-Preset-X.png').grain.levels[0].data.length === 256 * 256);
  });
  t('settings: a key the engine calls ignored changes nothing (all of the schema’s other keys that can be set generically)', () => {
    ok(schema, 'needs the schema'); const base = baselineParams(); const reference = render(base).hash; const moved = [];
    for (const row of schema.rows) {
      if (describeSupport(row.key) !== 'ignored') continue;
      const value = ignoredProbe(row); if (value === undefined) continue;
      if (render({...base, [row.key]: value}).hash !== reference) moved.push(row.key);
    }
    ok(!moved.length, `these keys are called ignored but change the picture: ${moved.join(', ')}`);
  });
  t('settings: every key of every era renders without an exception or a NaN', () => {
    ok(schema, 'needs the schema');
    for (const era of schema.raw.eras) {
      for (const mode of ['default', 'low', 'high']) {
        const params = {};
        for (const row of schema.rows) {
          if (!(row.eras || []).includes(era.id) || row.type !== 'real' && row.type !== 'bool' && row.type !== 'int') continue;
          const o = row.observed || {}; const lim = row.limits;
          const lo = lim ? lim[0] : (typeof o.min === 'number' ? o.min : 0); const hi = lim ? lim[1] : (typeof o.max === 'number' ? o.max : 1);
          params[row.key] = row.type === 'bool' ? mode === 'high' : mode === 'default' ? (typeof row.default === 'number' ? row.default : lo) : mode === 'low' ? lo : hi;
        }
        for (const pointer of ['pencil', 'touch']) { const r = render(params, {pointer, kind: mode === 'high' ? 'scribble' : 's-curve'}); ok(r.acc.every(Number.isFinite), `${era.id} ${mode} ${pointer}: NaN`); }
      }
    }
  });

  // ── the support table ──
  t('support: describeSupport answers honoured, approximate or ignored, and only keys of the schema are listed', () => {
    for (const key of Object.keys(SUPPORT)) { ok(['honoured', 'approximate'].includes(describeSupport(key))); if (schema) ok(schema.byKey.has(key), `${key} is not a schema key`); }
    eq(describeSupport('no-such-key'), 'ignored'); eq(describeSupport('name'), 'ignored'); eq(describeSupport('shapeInverted'), 'honoured');
  });
  t('support: engineBadges covers every row, and applyEngineSupport makes the rows say what the engine does (on a copy)', () => {
    ok(schema, 'needs the schema'); const badges = engineBadges(schema); for (const row of schema.rows) ok(['honoured', 'approx', 'ignored'].includes(badges[row.key]), row.key);
    const copy = indexSchema(JSON.parse(JSON.stringify(schema.raw))); const diffs = applyEngineSupport(copy);
    const reported = supportDifferences(copy); eq(reported.length, diffs.length); for (const row of copy.rows) eq(row.preview, badges[row.key], row.key); ok(Array.isArray(diffs));
  });
  t('model: strokeOpacity maps the slider position into [minOpacity, maxOpacity]; a stamp follows the thumbnail law, a stroke the fitted law', () => {
    near(strokeOpacity(readModel({minOpacity: 0.2, maxOpacity: 1, paintOpacity: 0.5})), 0.6, 1e-9);
    near(baseDiameter(readModel({minSize: 0.1, maxSize: 0.5, previewSize: 0.5}), 'preview', 'tap'), 256 * 0.3, 1e-9);
    near(baseDiameter(readModel({maxSize: 1})), C.STROKE_K, 1e-9); ok(baseDiameter(readModel({maxSize: 4})) > baseDiameter(readModel({maxSize: 1})), 'bigger max, bigger stroke');
    near(baseDiameter(readModel({paintSize: 0.4}), 'paint'), 256 * 0.4, 1e-9);
    ok(coverageHash(new Float32Array(10)) === coverageHash(new Float32Array(10)));
  });
  return tests;
}
