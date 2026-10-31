// standins.js - what the preview draws when a brush's shape or grain ships inside
// Procreate and the app has no copy. Pure.
//
// These are NOT Procreate's textures. A bundled shape or grain is only a name
// (`Brush-Preset-Oval.png`); the app never has the image (the server makes none
// up, and neither does the textures panel). So the preview substitutes a generated
// image and says so on the canvas and in the status line. Exact means the name
// fully determines the image (a blank texture is flat white); everything else is a
// generic stand-in whose softness or noise is invented.

import {makeMask, makeGrain} from './mips.js';
import {mulberry32} from './rng.js';

const SIZE = 256;

function discMask(w, h, profile) {
  const lum = new Uint8Array(w * h);
  for (let y = 0; y < h; y += 1) {
    for (let x = 0; x < w; x += 1) {
      const dx = (x + 0.5) / w * 2 - 1; const dy = (y + 0.5) / h * 2 - 1;
      lum[y * w + x] = Math.round(255 * profile(Math.hypot(dx, dy)));
    }
  }
  return lum;
}
const feather = (f) => (r) => (r >= 1 ? 0 : r <= 1 - f ? 1 : (() => { const t = (1 - r) / f; return t * t * (3 - 2 * t); })());
const gaussian = (sigma) => (r) => (r >= 1 ? 0 : Math.exp(-0.5 * (r / sigma) * (r / sigma)) * (1 - r * r * r * r));

const SHAPES = [
  {re: /preset-blank/i, name: 'blank', exact: true, label: 'flat white square', make: () => ({lum: new Uint8Array(64 * 64).fill(255), w: 64, h: 64})},
  {re: /preset-ultra-soft/i, name: 'ultra-soft', label: 'soft round stand-in', make: () => ({lum: discMask(SIZE, SIZE, gaussian(0.4)), w: SIZE, h: SIZE})},
  {re: /preset-medium-hard/i, name: 'medium-hard', label: 'round stand-in, 15% feather', make: () => ({lum: discMask(SIZE, SIZE, feather(0.15)), w: SIZE, h: SIZE})},
  {re: /preset-hard/i, name: 'hard', label: 'hard round stand-in', make: () => ({lum: discMask(SIZE, SIZE, feather(0.015)), w: SIZE, h: SIZE})},
  {re: /preset-medium/i, name: 'medium', label: 'round stand-in, 50% feather', make: () => ({lum: discMask(SIZE, SIZE, feather(0.5)), w: SIZE, h: SIZE})},
  {re: /preset-soft/i, name: 'soft', label: 'soft round stand-in', make: () => ({lum: discMask(SIZE, SIZE, gaussian(0.3)), w: SIZE, h: SIZE})},
  {re: /preset-oval/i, name: 'oval', label: 'oval 2:1 stand-in', make: () => ({lum: discMask(SIZE, SIZE / 2, feather(0.12)), w: SIZE, h: SIZE / 2})},
];

/** {mask, exact, kind, label} for a bundled shape name (or no name at all). */
export function standinShape(ref, inverted) {
  const hit = SHAPES.find((s) => s.re.test(ref || ''));
  const spec = hit || {name: 'generic', exact: false, label: 'generic round stand-in', make: () => ({lum: discMask(SIZE, SIZE, feather(0.3)), w: SIZE, h: SIZE})};
  const {lum, w, h} = spec.make();
  return {mask: makeMask(lum, null, w, h, inverted), exact: !!spec.exact, kind: spec.name, label: `${spec.label} for ${ref || 'an unnamed shape'}`};
}

/** Tileable value noise, 256 x 256, fixed seed: the generic stand-in for a bundled grain. */
export function noiseGrain(seed = 7) {
  const n = 256;
  const next = mulberry32(seed);
  const lum = new Float32Array(n * n);
  let amp = 1; let total = 0;
  for (const cells of [8, 16, 32, 64]) {
    const grid = new Float32Array(cells * cells);
    for (let i = 0; i < grid.length; i += 1) grid[i] = next();
    for (let y = 0; y < n; y += 1) {
      for (let x = 0; x < n; x += 1) {
        const gx = x / n * cells; const gy = y / n * cells;
        const ix = Math.floor(gx); const iy = Math.floor(gy);
        let fx = gx - ix; let fy = gy - iy;
        fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy);
        const g = (a, b) => grid[((b % cells) * cells) + (a % cells)];
        const top = g(ix, iy) * (1 - fx) + g(ix + 1, iy) * fx; const bottom = g(ix, iy + 1) * (1 - fx) + g(ix + 1, iy + 1) * fx;
        lum[y * n + x] += amp * (top * (1 - fy) + bottom * fy);
      }
    }
    total += amp; amp *= 0.55;
  }
  const out = new Uint8Array(n * n);
  for (let i = 0; i < out.length; i += 1) out[i] = Math.round(255 * Math.min(1, Math.max(0, ((lum[i] / total) - 0.5) * 2.2 + 0.5)));
  return {lum: out, w: n, h: n};
}

/** {grain, exact, label}: null grain for a blank texture (exact), a generic noise otherwise. */
export function standinGrain(ref) {
  if (/preset-blank/i.test(ref || '')) return {grain: null, exact: true, label: 'blank'};
  const {lum, w, h} = noiseGrain();
  return {grain: makeGrain(lum, w, h, w, h), exact: false, label: `generic noise stand-in for ${ref || 'an unnamed grain'}`};
}
