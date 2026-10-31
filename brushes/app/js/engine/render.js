// render.js - settings to coverage, without a canvas. Pure.
//
// planRender() reads the settings, makes the stroke and its stamps and the
// rasteriser context; runPlan() rasterises a slice of the stamps (so the painter
// can yield between slices); renderCoverage() does it all at once, which is what
// the unit tests use. The painter (paint.js) only turns the coverage into pixels.

import {readModel, strokeOpacity} from './model.js';
import {testPath, drawnPath, VIEW_W, VIEW_H, PRESSURE_LEVELS} from './path.js';
import {buildStamps} from './stamps.js';
import {rasterStamps, estimateOps, grainTable} from './raster.js';
import {standinShape} from './standins.js';
import {hashBytes} from './rng.js';

/** The stroke kind the view shows: 'auto' is a single stamp for a "stamp preview" brush and the S-curve otherwise. */
export function resolveKind(kind, model) {
  const k = kind || 'auto';
  return k === 'auto' ? (model.stamp ? 'tap' : 's-curve') : k;
}

/**
 * view: {w, h (pixels of the coverage buffer), kind, level, pointer, tilt, seed, sizeSource, tall,
 *        raw (drawn samples in U), minStepFrac, minStepU, maxStamps}
 * assets: {mask, grain} from standins.js / assets.js (a default round mask when none).
 */
export function planRender(params, view, assets = {}) {
  const model = readModel(params);
  const wide = !view.tall;
  const height = wide ? VIEW_H.wide : VIEW_H.tall;
  const k = view.w / VIEW_W;
  const kind = resolveKind(view.kind, model);
  const level = typeof view.level === 'number' ? view.level : PRESSURE_LEVELS.heavy;
  let path = null;
  if (kind === 'drawn' && view.raw && view.raw.length) path = drawnPath(view.raw, {level, pointerType: view.pointerType});
  if (!path) path = testPath({kind: kind === 'drawn' ? 's-curve' : kind, height, level, pointer: view.pointer, tilt: view.tilt, speed: view.speed, touchPressure: 0.6});
  const built = buildStamps(model, path, {pointer: view.pointer || 'pencil', seed: view.seed === undefined ? 1 : view.seed,
    sizeSource: view.sizeSource || 'preview', kind, minStepFrac: view.minStepFrac, minStepU: view.minStepU, maxStamps: view.maxStamps});
  const mask = assets.mask || standinShape('', model.shapeInverted).mask;
  const ctx = {acc: view.acc && view.acc.length === view.w * view.h ? view.acc : new Float32Array(view.w * view.h), w: view.w, h: view.h, k,
    mask, grain: assets.grain || null, grainModel: model.grain, maxTransfer: model.maxTransfer};
  if (view.acc && ctx.acc === view.acc) ctx.acc.fill(0);
  if (ctx.grain) ctx.grainLut = grainTable(model.grain.depth, model.grain.inverted);
  return {model, path, built, ctx, kind, strokeOpacity: strokeOpacity(model), opsEstimate: estimateOps(built.stamps, k), pointer: view.pointer || 'pencil'};
}

/** Rasterise stamps [from, to) of a plan; returns the pixels visited. */
export function runPlan(plan, from = 0, to = plan.built.stamps.length) {
  return rasterStamps(plan.built.stamps, from, Math.min(to, plan.built.stamps.length), plan.ctx);
}

/** A hash of the coverage as 8-bit values (what the tests compare; the canvas result carries its own pixel hash). */
export function coverageHash(acc, opacity = 1) {
  const bytes = new Uint8Array(acc.length);
  for (let i = 0; i < acc.length; i += 1) bytes[i] = Math.round(Math.min(1, acc[i] * opacity) * 255);
  return hashBytes(bytes);
}

/** Plan and rasterise at once: {plan, hash, stamps, ops}. */
export function renderCoverage(params, view, assets) {
  const plan = planRender(params, view, assets);
  const ops = runPlan(plan);
  return {plan, ops, stamps: plan.built.stamps.length, hash: coverageHash(plan.ctx.acc, plan.strokeOpacity), acc: plan.ctx.acc};
}
