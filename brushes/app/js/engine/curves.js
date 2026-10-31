// curves.js - pressure curves for the stroke engine. Pure.
//
// A curve in a brush is {"points": ["{0.25, 0.33}", ...]} (F3 "JSON value
// forms"). How Procreate draws the curve between points is not known; this
// evaluates a monotone cubic through them, the same guess as the curve editor
// (js/curve.js), flat outside the end points. Absent or malformed: the identity.

const POINT = /^\{\s*(-?\d+(?:\.\d+)?(?:e-?\d+)?)\s*,\s*(-?\d+(?:\.\d+)?(?:e-?\d+)?)\s*\}$/i;
export const LUT_SIZE = 256;

/** [[x, y], ...] sorted by x from a curve value, or null when it is not a well-formed curve. */
export function curvePoints(value) {
  if (!value || !Array.isArray(value.points) || value.points.length < 2) return null;
  const pairs = [];
  for (const text of value.points) {
    const m = typeof text === 'string' ? POINT.exec(text) : null;
    if (!m) return null;
    pairs.push([Number(m[1]), Number(m[2])]);
  }
  return pairs.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
}

/** Fritsch-Carlson monotone cubic through sorted points. */
export function monotone(points, x) {
  const n = points.length;
  if (n === 0) return 0;
  if (n === 1 || x <= points[0][0]) return points[0][1];
  if (x >= points[n - 1][0]) return points[n - 1][1];
  const dx = []; const slope = [];
  for (let i = 0; i < n - 1; i += 1) { dx.push(points[i + 1][0] - points[i][0]); slope.push((points[i + 1][1] - points[i][1]) / (dx[i] || 1e-9)); }
  const tangent = [slope[0]];
  for (let i = 1; i < n - 1; i += 1) tangent.push(slope[i - 1] * slope[i] <= 0 ? 0 : (slope[i - 1] + slope[i]) / 2);
  tangent.push(slope[n - 2]);
  for (let i = 0; i < n - 1; i += 1) {
    if (slope[i] === 0) { tangent[i] = 0; tangent[i + 1] = 0; continue; }
    const a = tangent[i] / slope[i]; const b = tangent[i + 1] / slope[i];
    const h = Math.hypot(a, b);
    if (h > 3) { tangent[i] = (3 * a / h) * slope[i]; tangent[i + 1] = (3 * b / h) * slope[i]; }
  }
  let i = 0;
  while (i < n - 2 && x > points[i + 1][0]) i += 1;
  const t = (x - points[i][0]) / dx[i]; const t2 = t * t; const t3 = t2 * t;
  return (2 * t3 - 3 * t2 + 1) * points[i][1] + (t3 - 2 * t2 + t) * dx[i] * tangent[i]
    + (-2 * t3 + 3 * t2) * points[i + 1][1] + (t3 - t2) * dx[i] * tangent[i + 1];
}

export const IDENTITY_CURVE = Object.freeze({identity: true, lut: null, at: (x) => (x < 0 ? 0 : x > 1 ? 1 : x)});

/** {identity, lut, at(x)} for a curve value; `at` maps 0..1 to 0..1 (clamped). */
export function makeCurve(value) {
  const pairs = curvePoints(value);
  if (!pairs) return IDENTITY_CURVE;
  const lut = new Float32Array(LUT_SIZE + 1);
  let identity = true;
  for (let i = 0; i <= LUT_SIZE; i += 1) {
    const x = i / LUT_SIZE;
    const y = Math.min(1, Math.max(0, monotone(pairs, x)));
    lut[i] = y;
    if (Math.abs(y - x) > 1e-4) identity = false;
  }
  if (identity) return IDENTITY_CURVE;
  return {identity: false, lut, at(x) {
    const f = (x < 0 ? 0 : x > 1 ? 1 : x) * LUT_SIZE; const i = Math.floor(f); const j = i < LUT_SIZE ? i + 1 : i;
    return lut[i] + (lut[j] - lut[i]) * (f - i);
  }};
}

/**
 * A dynamics factor from a signed amount d (-1..1) and the curve output c (0..1):
 *   d >= 0: 1 - d (1 - c)      full effect: the factor follows the curve
 *   d <  0: 1 - |d| c          the opposite way round
 * (INFERRED; the corpus holds negative opacity amounts down to -0.57.)
 */
export function dynamicsFactor(d, c) {
  return d >= 0 ? 1 - d * (1 - c) : 1 - (-d) * c;
}
