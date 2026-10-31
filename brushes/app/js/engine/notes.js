// notes.js - what the preview is and is not, in the page. DOM only for the builder.
//
// "Preview is an approximation of Procreate": the engine draws a synthetic
// stroke from the settings by rules that are mostly inferred from key names and
// observed ranges. This list is the honest ledger (the same statuses as
// design-app.md and critique-fidelity.md; the README's Engine section repeats it).

import {el} from '../dom.js';

export const NOTE = 'Preview is an approximation of Procreate. It draws a synthetic stroke from the settings by rules that are mostly guessed; it is not Procreate’s renderer.';

export const LEDGER = [
  {status: 'proven', what: 'Shape polarity: white is paint, unless Inverted is on (391 shapes checked).'},
  {status: 'measured', what: 'The default S-curve is the path of Procreate’s own stroke thumbnails (24 thumbnails); the single-stamp size law 256 x (min + (max - min) x previewSize) holds within 3 to 25 percent on 143 legacy stamps; the thickness of a stroke thumbnail follows a hump over its length (36 thumbnails).'},
  {status: 'inferred', what: 'What each key means (from its name and observed range): taper, jitter, scatter, rotation, falloff, flow, the pressure and speed laws, the curve shape between points, the pencil taper set.'},
  {status: 'guess', what: 'Every constant: the spacing factor, the jitter radius, the taper length, the grain unit, the stroke size (a fit to 329 library thumbnails that is off by a factor of two for a typical brush), reading the hump as pressure, the simulated speed, the accumulation of flow at fine spacing.'},
  {status: 'stand-in', what: 'A shape or grain that ships inside Procreate has no image here; the preview draws a generated stand-in and labels it. A blank grain is exact.'},
  {status: 'not drawn', what: 'Wet mix, colour dynamics, blend modes, dual brushes, wet and burnt edges, barrel roll, hover, materials, stabilisation, count, texture brightness and contrast, and any setting a badge calls ignored.'},
];

/** A closed <details> element with the ledger. */
export function createNotes() {
  return el('details', {class: 'engine-ledger'},
    el('summary', {class: 'small', text: 'What is proven, what is guessed'}),
    el('ul', {class: 'small ledger-list'}, LEDGER.map((row) => el('li', {}, el('strong', {text: `${row.status}: `}), row.what))));
}
