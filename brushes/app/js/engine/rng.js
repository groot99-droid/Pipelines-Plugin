// rng.js - the seeded random numbers of the stroke engine. Pure.
//
// Every stamp gets its own little generator, seeded from (seed, stamp index) and
// drawn exactly STAMP_DRAWS times whether or not a setting uses the draws. So a
// stamp's random values do not depend on the other stamps, on which settings are
// on, or on how finely the stroke is walked, and the same settings always give
// the same pixels. (Draw slots are fixed: see R in stamps.js.)

export const STAMP_DRAWS = 12;

/** mulberry32: a 32-bit generator; returns a function giving floats in [0, 1). */
export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** A 32-bit mix of two integers (the seed of one stamp's generator). */
export function mix(a, b) {
  let h = Math.imul((a | 0) ^ 0x9e3779b9, 0x85ebca6b) ^ Math.imul((b | 0) + 0x7f4a7c15, 0xc2b2ae35);
  h ^= h >>> 15; h = Math.imul(h, 0x2c1b3c6d);
  h ^= h >>> 12; h = Math.imul(h, 0x297a2d39);
  h ^= h >>> 15;
  return h >>> 0;
}

/** Fill `out` (length STAMP_DRAWS) with the random values of stamp `index`. */
export function stampRandoms(seed, index, out) {
  const next = mulberry32(mix(seed, index));
  for (let i = 0; i < STAMP_DRAWS; i += 1) out[i] = next();
  return out;
}

/** FNV-1a over the bytes of a typed array: the pixel hash of the tests and the result. */
export function hashBytes(view) {
  const bytes = new Uint8Array(view.buffer, view.byteOffset, view.byteLength);
  let h = 0x811c9dc5;
  for (let i = 0; i < bytes.length; i += 1) { h ^= bytes[i]; h = Math.imul(h, 0x01000193); }
  return (h >>> 0).toString(16).padStart(8, '0');
}
