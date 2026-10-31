// engine.js - the stroke preview (phase 3b, tier 1). The documented seam is
//
//   createEngine(canvas: HTMLCanvasElement, {persist = true}) -> {   // persist: remember the view options (not in tests)
//     render(params, opts) -> Promise<{engine, drew, ...}>   // draw one preview
//     setBadges(map)                                         // the badges the page shows
//     dispose()                                              // release everything
//   }
//
//   params  the effective settings: {schemaKey: JSON form}
//   opts    {width, era, name, thumbnailUrl, shapeUrl, grainUrl, shapeInfo, grainInfo, dark}
//
// Preview is an approximation of Procreate. A synthetic stroke (or one the user
// draws) is turned into a list of stamps by rules that are mostly inferred from the
// key names (js/engine/stamps.js), rasterised in software (raster.js, so the same
// settings always give the same pixels), and painted (paint.js). Nothing here is
// Procreate's renderer. describeSupport(key) says per key what is honoured,
// approximate or ignored; js/engine/notes.js is the ledger of proven and guessed.
//
// Extras on the engine object: `ui` (the controls and the ledger, an element),
// `view` / `setView()`, `refresh()`, `onresult` (called with every result),
// `lastResult`, `layout()`.

import {readModel, strokeOpacity} from './engine/model.js';
import {planRender, runPlan} from './engine/render.js';
import {PRESSURE_LEVELS, SPEED_LEVELS} from './engine/path.js';
import {createPainter, layoutFor, BACKGROUNDS} from './engine/paint.js';
import {createAssets} from './engine/assets.js';
import {createControls, loadView, saveView, VIEW_DEFAULTS} from './engine/controls.js';
import {attachInput} from './engine/input.js';
import {SUPPORT, notDrawn} from './engine/support.js';

export {describeSupport, supportNote, engineBadges, supportDifferences, applyEngineSupport, SUPPORT} from './engine/support.js';
export {pureEngineTests} from './engine/tests.js';
export {VIEW_DEFAULTS, BACKGROUNDS};

export const ENGINE_NAME = 'stroke engine, tier 1 (approximate)';
const BURST_MS = 260;                 // renders closer together than this are a drag: draw a draft
const SETTLE_MS = 170;                // after a draft, the full-quality render comes this long after the last change
const FRAME_BUDGET_MS = 12;           // a draft is sized to cost about this much
const SLICE_MS = 10;                  // a full render yields to the page every this many ms
const tick = () => new Promise((resolve) => setTimeout(resolve, 0));
const now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());

export function createEngine(canvas, {persist = true} = {}) {
  const painter = createPainter(canvas);
  const assets = createAssets();
  let view = persist ? loadView() : {...VIEW_DEFAULTS};
  let badges = {};
  let disposed = false;
  let serial = 0;
  let last = null;                    // {params, opts}
  let lastCallAt = 0;
  let settleTimer = 0;
  let nsPerOp = 25;                   // learned cost of one rasterised pixel
  let acc = null;
  let layout = layoutFor(360, {dpr: 1});
  let drawn = {raw: null, pointerType: 'mouse'};
  let signature = ''; let lastResult = null; let inflight = null;
  let ui = null; let controls = null; let detach = null;

  const usedKeys = [...Object.keys(SUPPORT), 'dynamicsMix', 'wetEdgesAmount', 'burntEdgesAmount', 'blendMode', 'extendedBlend', 'dynamicsBlur', 'dynamicsJitterHue', 'dynamicsJitterSaturation',
    'dynamicsJitterLightness', 'dynamicsJitterDarkness', 'dynamicsPressureHue', 'dynamicsPressureSaturation', 'dynamicsPressureBrightness', 'shapeCount'];   // the notes read these too
  const sign = (params, opts) => JSON.stringify([usedKeys.map((k) => params[k]), opts.width, opts.hasSub, opts.shapeUrl, opts.grainUrl, opts.thumbnailUrl,
    opts.shapeInfo && opts.shapeInfo.ref, opts.grainInfo && opts.grainInfo.ref, view, drawn.raw ? drawn.raw.length : 0, drawn.raw && drawn.raw.length ? drawn.raw[drawn.raw.length - 1].t : 0]);

  async function draw(params, opts, {draft}) {
    const t0 = now();
    const mine = serial;
    const dpr = typeof window !== 'undefined' ? Math.min(2, window.devicePixelRatio || 1) : 1;
    const cssW = Math.min(640, Math.max(160, Math.round(opts.width || canvas.clientWidth || 360)));
    const lay = layoutFor(cssW, {tall: view.tall, compare: view.compare, dpr});
    const model = readModel(params);
    const shapeInfo = opts.shapeInfo || {}; const grainInfo = opts.grainInfo || {};
    const [shape, grain, thumbAlpha] = await Promise.all([
      assets.shape(opts.shapeUrl || null, shapeInfo.ref || params.bundledShapePath || '', model.shapeInverted),
      assets.grain(opts.grainUrl || null, grainInfo.ref || params.bundledGrainPath || '', grainInfo.source),
      view.compare ? assets.thumbnailAlpha(opts.thumbnailUrl || null, lay.cw, lay.bandH) : null,
    ]);
    if (mine !== serial || disposed) return {engine: ENGINE_NAME, drew: 'stale'};

    const base = {kind: view.stroke, level: PRESSURE_LEVELS[view.level], speed: SPEED_LEVELS[view.speed], pointer: view.pointer, tilt: view.tilt, seed: view.seed, sizeSource: view.sizeSource,
      tall: view.tall, raw: drawn.raw, pointerType: drawn.pointerType};
    const at = (q) => {
      const w = Math.max(40, Math.round(lay.cw * q)); const h = Math.max(12, Math.round(lay.bandH * q));
      if (!acc || acc.length !== w * h) acc = new Float32Array(w * h);
      return planRender(params, {...base, w, h, acc, minStepFrac: q < 1 ? 0.1 : undefined}, {mask: shape.mask, grain: grain.grain});
    };
    let q = 1; let plan = at(1);
    if (draft) {
      const est = plan.opsEstimate * nsPerOp / 1e6;
      for (const next of [0.75, 0.5, 0.35]) if (est * q * q > FRAME_BUDGET_MS) q = next;
      if (q < 1) plan = at(q);
    }

    const stamps = plan.built.stamps; const r0 = now();
    let from = 0; let ops = 0; let sliceStart = now();
    while (from < stamps.length) {
      const to = Math.min(stamps.length, from + 8);
      ops += runPlan(plan, from, to); from = to;
      if (from < stamps.length && !draft && now() - sliceStart > SLICE_MS) {
        await tick();
        if (mine !== serial || disposed) return {engine: ENGINE_NAME, drew: 'stale'};
        sliceStart = now();
      }
    }
    const rasterMs = now() - r0;
    if (rasterMs > 3 && ops > 20000) nsPerOp = nsPerOp * 0.7 + 0.3 * (rasterMs * 1e6 / ops);

    const scheme = BACKGROUNDS[view.bg] || BACKGROUNDS.dark;
    layout = lay;
    painter.resize(lay); painter.background(lay, scheme);
    const hash = painter.stroke(lay, scheme, plan.ctx.acc, plan.ctx.w, plan.ctx.h, plan.strokeOpacity);
    const tags = ['engine preview, approximate'];
    if (shape.standIn) tags.push('stand-in shape'); if (grain.standIn) tags.push('stand-in grain');
    const labels = [{text: tags.join(' · '), x: 6 * lay.dpr, y: lay.bandH - 4 * lay.dpr}];
    if (view.compare) {
      const shown = painter.thumbnail(lay, scheme, thumbAlpha);
      labels.push({text: shown ? 'Procreate’s own thumbnail (stored in the file)' : 'This brush has no stored thumbnail', x: 6 * lay.dpr, y: lay.totalH - 4 * lay.dpr});
    }
    painter.labels(lay, scheme, labels);

    const notes = [];
    if (shape.standIn) notes.push(`Shape: ${shape.label}. The real image ships inside Procreate; this is not it.`);
    if (grain.standIn) notes.push(`Grain: ${grain.label}. The real image ships inside Procreate; this is not it.`);
    if (plan.built.truncated) notes.push('The stroke was cut at the stamp limit.');
    const skipped = notDrawn(params, {hasSub: opts.hasSub});
    if (skipped.length) notes.push(`Not drawn in this preview: ${skipped.join(', ')}.`);
    const result = {engine: ENGINE_NAME, drew: q < 1 ? 'draft' : 'stroke', ms: now() - t0, rasterMs, stamps: stamps.length, ops, quality: q, hash,
      kind: plan.kind, seed: view.seed, notes, standIn: {shape: shape.standIn, grain: grain.standIn}, strokeOpacity: strokeOpacity(model), truncated: plan.built.truncated};
    return result;
  }

  function publish(result) {
    if (result.drew === 'stale') return result;
    lastResult = result;
    if (controls) controls.setStatus(`${result.stamps} stamps, ${Math.round(result.ms)} ms${result.drew === 'draft' ? ' (draft while you edit)' : ''}. ${result.notes.join(' ')}`);
    if (engineApi.onresult) engineApi.onresult(result);
    return result;
  }

  const engineApi = {
    name: ENGINE_NAME,
    onresult: null,
    get view() { return {...view}; },
    get lastResult() { return lastResult; },
    layout: () => layout,
    get ui() {
      if (!ui) {
        controls = createControls({view, backgrounds: BACKGROUNDS, onChange: (partial) => engineApi.setView(partial)});
        ui = controls.el;
        if (lastResult) controls.setStatus('');
        detach = attachInput(canvas, {
          getLayout: () => layout,
          onStart: () => { view = {...view, stroke: 'drawn'}; if (controls) controls.sync(view); },
          onSamples: (raw, pointerType) => { drawn = {raw: raw.slice(), pointerType}; engineApi.refresh(); },
          onEnd: () => { engineApi.refresh({settle: true}); },
        });
      }
      return ui;
    },
    setView(partial) {
      view = {...view, ...partial};
      if (partial.stroke && partial.stroke !== 'drawn') drawn = {raw: null, pointerType: drawn.pointerType};
      if (persist) saveView({...view, stroke: view.stroke === 'drawn' ? 'auto' : view.stroke});
      if (controls) controls.sync(view);
      return engineApi.refresh({force: true});
    },
    render(params, opts = {}) {
      if (disposed) return Promise.resolve({engine: ENGINE_NAME, drew: 'nothing'});
      last = {params, opts};
      const sig = sign(params, opts);
      if (sig === signature) { if (inflight) return inflight; if (lastResult) return Promise.resolve(lastResult); }
      signature = sig;
      serial += 1;
      const t = now(); const draft = !opts.final && t - lastCallAt < BURST_MS; lastCallAt = t;
      if (settleTimer) { clearTimeout(settleTimer); settleTimer = 0; }
      const mine = serial;
      const run = (async () => {
        let result;
        try { result = publish(await draw(params, opts, {draft})); } catch (error) {
          result = {engine: ENGINE_NAME, drew: 'error', error: String(error && error.message || error), ms: 0, stamps: 0, notes: [`The preview failed: ${error && error.message}`]};
          lastResult = result; if (controls) controls.setStatus(result.notes[0]);
        }
        if (result.drew === 'draft' && mine === serial) {
          settleTimer = setTimeout(() => { settleTimer = 0; if (!disposed && mine === serial) { signature = ''; lastCallAt = 0; engineApi.refresh({force: true}); } }, SETTLE_MS);
        }
        return result;
      })();
      inflight = run;
      run.then(() => { if (inflight === run) inflight = null; }, () => { if (inflight === run) inflight = null; });
      return run;
    },
    /** Draw again from the last params (a control changed, or a drawn stroke moved). */
    refresh({force = false, settle = false} = {}) {
      if (!last || disposed) return Promise.resolve(null);
      if (force) signature = '';
      if (settle) lastCallAt = 0;
      return engineApi.render(last.params, last.opts);
    },
    setBadges(map) { badges = map || {}; },
    get badges() { return badges; },
    dispose() {
      disposed = true; serial += 1;
      if (settleTimer) clearTimeout(settleTimer);
      if (detach) detach();
      assets.clear();
      painter.ctx.clearRect(0, 0, canvas.width, canvas.height);
    },
  };
  return engineApi;
}
