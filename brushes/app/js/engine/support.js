// support.js - what the stroke engine does with each key, for the badges. Pure.
//
// describeSupport(key) is the engine's own answer: 'honoured' (the engine
// applies the rule exactly as the evidence proves it), 'approximate' (it applies
// a rule that is inferred or guessed, or only part of the key's effect), or
// 'ignored' (the key changes nothing in the preview). A key is listed here only
// when a render really changes with it (the self-test checks that); a key not
// listed is ignored. The schema's `preview` column (silica_keys.json) is authored
// separately; supportDifferences() lists where the two disagree and
// applyEngineSupport() makes the panels show the engine's answer.

const A = 'approximate';
const H = 'honoured';

/** key -> [status, what the engine does with it]. */
export const SUPPORT = {
  // stroke path
  plotSpacing: [A, 'Step between stamps = spacing x stamp diameter (the factor is a guess).'],
  plotJitter: [A, 'Random offset of each stamp, up to jitter x half a diameter (a guess).'],
  dynamicsFalloff: [A, 'The stroke fades along its length (the length is a guess).'],
  // taper (touch set and the Apple Pencil set; a pen uses the pencil set when the brush has one)
  taperStartLength: [A, 'Length of the start taper, as a fraction of a reference length (a guess).'],
  taperEndLength: [A, 'Length of the end taper, as a fraction of a reference length (a guess).'],
  taperSize: [A, 'How much the stamp shrinks at the stroke ends.'],
  taperOpacity: [A, 'How much the stamp fades at the stroke ends.'],
  pencilTaperStartLength: [A, 'As taperStartLength, for the Apple Pencil.'],
  pencilTaperEndLength: [A, 'As taperEndLength, for the Apple Pencil.'],
  pencilTaperSize: [A, 'As taperSize, for the Apple Pencil.'],
  pencilTaperOpacity: [A, 'As taperOpacity, for the Apple Pencil.'],
  // shape
  bundledShapePath: [A, 'A bundled shape is drawn as a generated stand-in, marked as such.'],
  shapeInverted: [H, 'Polarity of the shape image: white is paint unless inverted (proven on 391 shapes).'],
  shapeScatter: [A, 'Random rotation of each stamp.'],
  shapeRotation: [A, 'Rotation follows the stroke direction by this factor.'],
  shapeRandomise: [A, 'A random rotation for each stamp (it may be once per stroke in Procreate).'],
  shapeAzimuth: [A, 'With a tilted pen the stamp turns with the pen azimuth; upright it has no effect.'],
  shapeAngle: [A, 'A fixed rotation added to every stamp.'],
  shapeRoundness: [A, 'Squashes the stamp across its own height.'],
  shapeFlipXJitter: [A, 'Each stamp is mirrored left-right with probability one half.'],
  shapeFlipYJitter: [A, 'Each stamp is mirrored top-bottom with probability one half.'],
  // grain
  bundledGrainPath: [A, 'A bundled grain is drawn as generated noise, marked as such; a blank grain is exact.'],
  textureMovement: [A, '1 pins the grain to the canvas, 0 carries it with each stamp (the polarity is not proven).'],
  textureZoom: [A, 'The grain scales with the stamp size.'],
  textureScale: [A, 'Grain size (the unit is a guess).'],
  textureInverted: [A, 'Inverts the grain.'],
  grainDepth: [A, 'How strongly the grain cuts into the stamp (the older eras apply it in full).'],
  // dynamics
  dynamicsSpeedSize: [A, 'Faster strokes get smaller (or bigger when negative); the speed is simulated.'],
  dynamicsSpeedOpacity: [A, 'Faster strokes get fainter (or stronger when negative); the speed is simulated.'],
  dynamicsJitterSize: [A, 'A random reduction of each stamp’s size.'],
  dynamicsJitterOpacity: [A, 'A random reduction of each stamp’s opacity.'],
  // pressure and tilt (the pressure is simulated)
  dynamicsPressureSize: [A, 'How much the pressure curve changes the stamp size.'],
  dynamicsPressureOpacity: [A, 'How much the pressure curve changes the stamp opacity.'],
  dynamicsPressureSizeCurve: [A, 'The curve between pressure and size (drawn as a monotone cubic, a guess).'],
  dynamicsPressureOpacityCurve: [A, 'The curve between pressure and opacity (drawn as a monotone cubic, a guess).'],
  dynamicsTiltSize: [A, 'A tilted pen draws bigger stamps (simulated tilt, the gain is a guess).'],
  dynamicsTiltOpacity: [A, 'A tilted pen draws fainter stamps (simulated tilt, the gain is a guess).'],
  // rendering
  dynamicsGlazeFlow: [A, 'Opacity of each stamp before it builds up (legacy name).'],
  dynamicsGlazedFlow: [A, 'Opacity of each stamp before it builds up.'],
  renderingMaxTransfer: [A, 'Overlapping stamps take the strongest value instead of building up (a reading of the name).'],
  // properties
  stamp: [A, 'A "stamp preview" brush shows one stamp when the stroke choice is Auto.'],
  previewSize: [A, 'Where in the minimum-to-maximum size range the single preview stamp sits (a stroke does not use it).'],
  paintSize: [A, 'With "paint size" chosen, the size the brush was last used at.'],
  minSize: [A, 'Lower end of the size range; only the single preview stamp uses it.'],
  maxSize: [A, 'Upper end of the size range; a stroke’s size grows slowly with it (a fit, not a law).'],
  minOpacity: [A, 'Lower end of the opacity range.'],
  maxOpacity: [A, 'Upper end of the opacity range.'],
  paintOpacity: [A, 'Where in the opacity range the stroke is drawn.'],
};

export function describeSupport(key) {
  const hit = SUPPORT[key];
  return hit ? hit[0] : 'ignored';
}

export function supportNote(key) {
  const hit = SUPPORT[key];
  return hit ? hit[1] : 'The stroke preview does not use this setting.';
}

/** The schema's own word for a status ('approximate' is 'approx' there). */
export const SCHEMA_WORD = {honoured: 'honoured', approximate: 'approx', ignored: 'ignored'};

/** {key: 'honoured'|'approx'|'ignored'} for setBadges, covering every row and alias of a schema index. */
export function engineBadges(schema) {
  const out = {};
  for (const row of schema.rows) {
    const word = SCHEMA_WORD[describeSupport(row.key)];
    out[row.key] = word;
    for (const alias of row.aliases || []) out[alias] = SCHEMA_WORD[describeSupport(alias)] === 'ignored' ? word : SCHEMA_WORD[describeSupport(alias)];
  }
  return out;
}

/** [{key, schema, engine}] for every row whose authored `preview` differs from the engine's answer. */
export function supportDifferences(schema) {
  const out = [];
  for (const row of schema.rows) {
    const engine = SCHEMA_WORD[describeSupport(row.key)];
    const authored = row.authoredPreview || row.preview;           // applyEngineSupport() keeps the authored word
    if (authored !== engine) out.push({key: row.key, schema: authored, engine});
  }
  return out;
}

/**
 * Make the schema index report the engine's answer in `row.preview`, which the panels read for
 * their badge. Only the in-memory rows change, never the file. Returns what was different.
 */
export function applyEngineSupport(schema) {
  const diffs = supportDifferences(schema);
  for (const d of diffs) { const row = schema.byKey.get(d.key); if (row) { row.authoredPreview = row.authoredPreview || row.preview; row.preview = d.engine; } }
  return diffs;
}

const above = (params, keys, limit = 0.02) => keys.some((k) => typeof params[k] === 'number' && params[k] > limit);

/**
 * What this brush uses that the preview does not draw (labels, for the status line): the big things
 * that change how a real stroke looks, so a viewer does not mistake a missing effect for a bug.
 */
export function notDrawn(params, {hasSub = false} = {}) {
  const out = [];
  if (above(params, ['dynamicsMix'])) out.push('wet mix');
  if (above(params, ['wetEdgesAmount'])) out.push('wet edges');
  if (above(params, ['burntEdgesAmount'])) out.push('burnt edges');
  if ((params.blendMode > 0) || (params.extendedBlend > 0)) out.push('a blend mode');
  if (above(params, ['dynamicsBlur'])) out.push('blur');
  if (above(params, ['dynamicsJitterHue', 'dynamicsJitterSaturation', 'dynamicsJitterLightness', 'dynamicsJitterDarkness', 'dynamicsPressureHue', 'dynamicsPressureSaturation', 'dynamicsPressureBrightness'])) out.push('colour dynamics');
  if (above(params, ['shapeCount'])) out.push('shape count');
  if (hasSub) out.push('the secondary (dual) brush');
  return out;
}
