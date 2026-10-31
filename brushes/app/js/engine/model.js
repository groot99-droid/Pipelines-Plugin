// model.js - the brush settings the stroke engine reads, as plain numbers. Pure.
//
// `readModel(params)` takes the effective settings ({schemaKey: JSON form}, any
// era) and returns what the engine uses, with the neutral value for every key the
// brush does not hold (an older era simply lacks the key). Nothing here is
// Procreate's own code: each rule is labelled in CALIBRATION (and in
// engine/notes.js, which the page shows) as PROVEN, MEASURED, INFERRED or GUESS.

import {makeCurve} from './curves.js';

/**
 * Constants of the model. They are placeholders to be fitted against Procreate's
 * own thumbnails (design-app.md section 3.4); the status says how much to trust one.
 * Units: U is the preview's own unit, 1060 U across (the width of Procreate's
 * stroke thumbnail), so a stamp D U wide is D/1060 of the canvas.
 */
export const CALIBRATION = {
  UNIT: 256,                 // U for a size of 1.0                  MEASURED for stamp thumbnails (legacy, 143 stamps within 3 to 25 percent)
  STROKE_K: 90,              // stroke diameter = K * maxSize^EXP    GUESS fitted to 329 library stroke thumbnails (log regression, residual sd 0.7: a factor of two)
  STROKE_EXP: 0.3,           // Procreate's stroke thumbnails hardly depend on previewSize or paintSize; the thickness grows only slowly with maxSize
  SPACING_K: 1.0,            // step = K * plotSpacing * diameter    GUESS (design says sqrt 2, measured on one vendor family)
  FLOW_REF_STEP: 0.1,        // below this step (in diameters) flow is normalised so fine spacing does not saturate   GUESS (engine rule)
  JITTER_K: 0.5,             // position jitter radius = plotJitter * K * diameter   GUESS
  TAPER_LEN_K: 12,           // taper length = fraction * min(length, K diameters)   GUESS
  FALLOFF_LEN: 40,           // falloff reaches full strength over this many diameters   GUESS
  TILT_SIZE_K: 1.5,          // size gain per unit tilt amount        GUESS
  SPEED_REF: 1,              // speed is already 0..1 in the simulated stroke
  GRAIN_TEXEL_U: 0.45,       // U per grain texel at textureScale 1   GUESS, set by eye on 2 library brushes (0.3 and 0.5 each matched one thumbnail's speckle)
  GRAIN_REF_DIAMETER: 256,   // diameter at which Zoom changes nothing   GUESS
  TOUCH_PRESSURE: 0.6,       // a finger has no pressure   GUESS
  MIN_STEP_U: 0.4,           // smallest step along the stroke, U
};

const num = (p, key, fallback) => (typeof p[key] === 'number' && Number.isFinite(p[key]) ? p[key] : fallback);
const flag = (p, key) => p[key] === true;
const first = (p, keys, fallback) => { for (const k of keys) if (typeof p[k] === 'number' && Number.isFinite(p[k])) return p[k]; return fallback; };

const TOUCH_TAPER = ['taperStartLength', 'taperEndLength', 'taperSize', 'taperOpacity'];
const PENCIL_TAPER = ['pencilTaperStartLength', 'pencilTaperEndLength', 'pencilTaperSize', 'pencilTaperOpacity'];

function taperSet(p, [start, end, size, opacity]) {
  return {
    present: [start, end, size, opacity].some((k) => typeof p[k] === 'number'),
    start: num(p, start, 0), end: num(p, end, 0), size: num(p, size, 0), opacity: num(p, opacity, 0),
  };
}

export function readModel(p = {}) {
  const touch = taperSet(p, TOUCH_TAPER);
  const pencil = taperSet(p, PENCIL_TAPER);
  const minSize = num(p, 'minSize', 0);
  const maxSize = num(p, 'maxSize', 1);
  const minOpacity = num(p, 'minOpacity', 0);
  const maxOpacity = num(p, 'maxOpacity', 1);
  return {
    minSize, maxSize, previewSize: num(p, 'previewSize', 0.3), paintSize: num(p, 'paintSize', Math.min(maxSize, Math.max(minSize, 0.3))),
    minOpacity, maxOpacity, paintOpacity: num(p, 'paintOpacity', 1),
    stamp: flag(p, 'stamp'),
    spacing: num(p, 'plotSpacing', 0.1), jitter: num(p, 'plotJitter', 0), falloff: num(p, 'dynamicsFalloff', 0),
    touch, pencil,
    scatter: num(p, 'shapeScatter', 0), rotation: num(p, 'shapeRotation', 0), randomise: flag(p, 'shapeRandomise'), azimuth: flag(p, 'shapeAzimuth'),
    shapeAngle: num(p, 'shapeAngle', 0), roundness: Math.min(1, Math.max(0.05, num(p, 'shapeRoundness', 1))),
    flipX: flag(p, 'shapeFlipXJitter'), flipY: flag(p, 'shapeFlipYJitter'), shapeInverted: flag(p, 'shapeInverted'),
    grain: {
      movement: Math.min(1, Math.max(0, num(p, 'textureMovement', 1))), zoom: Math.min(1, Math.max(0, num(p, 'textureZoom', 0))),
      scale: Math.max(0.05, num(p, 'textureScale', 1)), inverted: flag(p, 'textureInverted'),
      depth: Math.min(1, Math.max(0, num(p, 'grainDepth', 1))),          // the legacy eras have no depth: the grain applies in full
    },
    speedSize: num(p, 'dynamicsSpeedSize', 0), speedOpacity: num(p, 'dynamicsSpeedOpacity', 0),
    jitterSize: num(p, 'dynamicsJitterSize', 0), jitterOpacity: num(p, 'dynamicsJitterOpacity', 0),
    pressureSize: num(p, 'dynamicsPressureSize', 0), pressureOpacity: num(p, 'dynamicsPressureOpacity', 0),
    sizeCurve: makeCurve(p.dynamicsPressureSizeCurve), opacityCurve: makeCurve(p.dynamicsPressureOpacityCurve),
    tiltSize: num(p, 'dynamicsTiltSize', 0), tiltOpacity: num(p, 'dynamicsTiltOpacity', 0),
    flow: Math.min(1, Math.max(0, first(p, ['dynamicsGlazedFlow', 'dynamicsGlazeFlow'], 1))),
    maxTransfer: flag(p, 'renderingMaxTransfer'),
  };
}

/** The taper set for an input: a pen uses the pencil variant when the brush has one. */
export function taperFor(model, pointer) {
  return pointer === 'pencil' && model.pencil.present ? model.pencil : model.touch;
}

/** The stroke opacity: the opacity slider position mapped between the brush's minimum and maximum. */
export function strokeOpacity(model) {
  const lo = Math.min(model.minOpacity, model.maxOpacity); const hi = Math.max(model.minOpacity, model.maxOpacity);
  return Math.min(1, Math.max(0, lo + (hi - lo) * model.paintOpacity));
}

/**
 * The stamp diameter at full pressure, in U.
 *   'preview', one stamp (kind 'tap', or a brush's "stamp preview"): 256 * (minSize + (maxSize - minSize)
 *              * previewSize), the law of Procreate's stamp thumbnail (MEASURED on 143 legacy stamps).
 *   'preview', a stroke: STROKE_K * maxSize^STROKE_EXP, a fit to 329 library stroke thumbnails (a GUESS:
 *              the thumbnail stroke hardly follows previewSize, so the law does not use it).
 *   'paint':   256 * paintSize, the size the brush was last used at (INFERRED).
 */
export function baseDiameter(model, source = 'preview', kind = 'stroke') {
  if (source === 'paint') return CALIBRATION.UNIT * Math.max(0, model.paintSize);
  if (kind === 'tap') return CALIBRATION.UNIT * Math.max(0, model.minSize + (model.maxSize - model.minSize) * model.previewSize);
  return CALIBRATION.STROKE_K * Math.pow(Math.max(1e-4, model.maxSize), CALIBRATION.STROKE_EXP);
}
