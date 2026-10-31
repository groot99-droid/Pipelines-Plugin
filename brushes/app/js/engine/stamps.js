// stamps.js - the stamp list of one stroke: where the stamps go and how big,
// turned and opaque each is. Pure: no canvas, no DOM; the rasteriser draws it.
//
// The walk: a stamp at arc length s, the next at s + step, where
//   step = max(floor, SPACING_K * plotSpacing * diameter)
// (the diameter at that point without its random jitter; the floor keeps a
// spacing of 0 from stamping forever). Everything a stamp needs comes from the
// simulated stroke at s (pressure, speed, tilt, direction) and from its own
// random draws, which are fixed by (seed, stamp index) - see rng.js. Every rule
// is INFERRED or a GUESS (critique-fidelity.md section 2); the page's badges and
// engine/notes.js say so. Nothing here claims to be what Procreate computes.

import {CALIBRATION as C, baseDiameter, taperFor} from './model.js';
import {dynamicsFactor} from './curves.js';
import {sampleAt} from './path.js';
import {STAMP_DRAWS, stampRandoms} from './rng.js';

/** Which random draw of a stamp feeds what (the slots never move, so a setting can be switched without reshuffling the others). */
export const R = {SIZE: 0, OPACITY: 1, JITTER_ANGLE: 2, JITTER_RADIUS: 3, SCATTER: 4, RANDOMISE: 5, FLIP_X: 6, FLIP_Y: 7};

export const MAX_STAMPS = 14000;
const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

/** Speed factor of a signed amount: faster means smaller (or, for a negative amount, bigger). */
export function speedFactor(d, v) {
  return d >= 0 ? 1 - d * v : 1 - (-d) * (1 - v);
}

/**
 * The taper factor at arc length s of a stroke of length L: 1 in the middle, rising from
 * (1 - amount) at either end over `start` / `end` times Lref. `amount` is the taper size or
 * opacity (0 = no taper). A tap (L = 0) is not tapered.
 */
export function taperFactor(s, L, Lref, taper, amount) {
  if (!(L > 0) || !(amount > 0)) return 1;
  const a = taper.start > 0 ? clamp01(s / (taper.start * Lref)) : 1;
  const b = taper.end > 0 ? clamp01((L - s) / (taper.end * Lref)) : 1;
  return (1 - amount * (1 - a)) * (1 - amount * (1 - b));
}

/** The arc length of the taper reference: the stroke's length, at most TAPER_LEN_K diameters. */
export function taperReference(L, D0) {
  return Math.min(L, C.TAPER_LEN_K * D0);
}

/**
 * Build the stamps of a stroke.
 *   model  readModel(params)
 *   path   a path from path.js
 *   cfg    {pointer: 'pencil'|'touch', seed, sizeSource: 'preview'|'paint', kind ('tap' = one stamp),
 *           minStepFrac, minStepU, maxStamps}
 * Returns {stamps, D0, taper, truncated, length}; a stamp is
 *   {x, y, d (diameter, U), angle (rad), alpha (0..1, flow and accumulation applied),
 *    sy (roundness), fx, fy (flips), s (arc length), step}.
 */
export function buildStamps(model, path, cfg = {}) {
  const pointer = cfg.pointer || 'pencil';
  const seed = cfg.seed === undefined ? 1 : cfg.seed;
  const D0 = baseDiameter(model, cfg.sizeSource || 'preview', cfg.kind || (path.length > 0 ? 'stroke' : 'tap'));
  const taper = taperFor(model, pointer);
  const L = path.length;
  const Lref = taperReference(L, D0);
  const minFrac = cfg.minStepFrac === undefined ? 0.05 : cfg.minStepFrac;      // a step is never finer than 5 percent of the diameter (the flow normalisation keeps the density)
  const minAbs = Math.max(C.MIN_STEP_U, cfg.minStepU || 0);
  const maxStamps = cfg.maxStamps || MAX_STAMPS;
  const touch = pointer !== 'pencil';
  const rnd = new Float64Array(STAMP_DRAWS);
  const q = {};
  const stamps = [];
  let s = 0; let index = 0; let truncated = false;

  for (;;) {
    sampleAt(path, s, q);
    stampRandoms(seed, index, rnd);
    const pressure = touch ? C.TOUCH_PRESSURE : q.p;
    const tilt = touch ? 0 : q.tilt;

    const sizeBase = dynamicsFactor(model.pressureSize, model.sizeCurve.at(pressure))
      * speedFactor(model.speedSize, q.v * C.SPEED_REF)
      * (1 + model.tiltSize * tilt * C.TILT_SIZE_K)
      * taperFactor(s, L, Lref, taper, taper.size);
    const dNominal = D0 * Math.max(0, sizeBase);
    const d = dNominal * (1 - model.jitterSize * rnd[R.SIZE]);

    const opacity = dynamicsFactor(model.pressureOpacity, model.opacityCurve.at(pressure))
      * speedFactor(model.speedOpacity, q.v * C.SPEED_REF)
      * (1 - model.tiltOpacity * tilt)
      * (1 - model.jitterOpacity * rnd[R.OPACITY])
      * taperFactor(s, L, Lref, taper, taper.opacity)
      * Math.max(0, 1 - model.falloff * s / (C.FALLOFF_LEN * Math.max(D0, 1)));

    const step = Math.max(minAbs, minFrac * dNominal, C.SPACING_K * model.spacing * dNominal);

    if (d > 0.05 && opacity > 0) {
      let angle = model.shapeAngle;
      if (model.randomise) angle += rnd[R.RANDOMISE] * 2 * Math.PI;
      if (model.azimuth && tilt > 0.02) angle += q.az; else angle += model.rotation * q.dir;
      angle += (rnd[R.SCATTER] - 0.5) * 2 * Math.PI * model.scatter;
      const radius = model.jitter * C.JITTER_K * dNominal * Math.sqrt(rnd[R.JITTER_RADIUS]);
      const around = rnd[R.JITTER_ANGLE] * 2 * Math.PI;
      const base = clamp01(opacity) * model.flow;
      // Flow: a stamp's alpha builds up where stamps overlap. At very fine spacing that would
      // saturate any flow, so the alpha is spread over the overlap (an engine rule, not Procreate's).
      const keep = model.maxTransfer ? 1 : Math.min(1, step / (C.FLOW_REF_STEP * Math.max(d, 1e-6)));
      const alpha = base >= 1 || keep >= 1 ? base : 1 - Math.pow(1 - base, keep);
      stamps.push({
        x: q.x + radius * Math.cos(around), y: q.y + radius * Math.sin(around), d, angle, alpha,
        sy: model.roundness, fx: model.flipX && rnd[R.FLIP_X] < 0.5, fy: model.flipY && rnd[R.FLIP_Y] < 0.5, s, step,
      });
    }

    index += 1;
    if (!(L > 0)) break;                                   // a tap is one stamp
    s += step;
    if (s > L + 1e-9) break;
    if (stamps.length >= maxStamps) { truncated = true; break; }
  }
  return {stamps, D0, taper, truncated, length: L};
}

/** The number of stamps a straight, steady stroke of length L gets at a constant step: floor(L / step) + 1. */
export function expectedCount(L, step) {
  return Math.floor(L / step + 1e-9) + 1;
}
