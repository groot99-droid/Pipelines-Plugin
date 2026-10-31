// path.js - the synthetic strokes of the preview, with their simulated pressure,
// speed and tilt. Pure.
//
// A path is a polyline resampled every PATH_STEP U along its length (U = the
// preview's own unit, 1060 across), each sample carrying pressure p (0..1), speed
// v (0..1), tilt (0 upright .. 1 flat), pen azimuth and the stroke direction
// (unwrapped, so a loop keeps counting). `sampleAt(path, s, out)` reads it at an
// arc length. The default S-curve is Procreate's own thumbnail path (MEASURED on
// 24 thumbnails: y = 179.2 + 28.8 sin(2 pi (x - 55) / 1050) between x = 87 and
// 975 of a 1060 x 324 image). The pressure and speed profiles are synthetic.

export const PATH_STEP = 1;
export const VIEW_W = 1060;
export const VIEW_H = {wide: 324, tall: 540};
export const PRESSURE_LEVELS = {light: 0.3, medium: 0.6, heavy: 1.0};
export const SPEED_LEVELS = {slow: 0.5, medium: 1, fast: 3};
export const STROKE_KINDS = ['auto', 's-curve', 'line', 'scribble', 'tap', 'drawn'];

/**
 * Pressure along the stroke for u in 0..1, scaled by the level: a hump sin(pi u)^1.4 that peaks mid
 * stroke. It is the median thickness profile of 36 pressure-sensitive library thumbnails (MEASURED
 * as thickness; read here as pressure, which is a guess).
 */
export function pressureProfile(u, level) {
  const shape = Math.pow(Math.sin(Math.PI * Math.min(1, Math.max(0, u))), 1.4);
  return Math.min(1, Math.max(0.02, level * shape));
}

/**
 * Speed (0..1) along the stroke: slow at both ends, quicker in the middle, scaled by the speed level.
 * The medium level is a gentle stroke (0.12 to 0.3): Procreate's own thumbnails do not look as if
 * speed dynamics were strong in them. The scale is a guess.
 */
export function speedProfile(u, scale = 1) {
  return Math.min(1, scale * (0.12 + 0.18 * Math.pow(Math.sin(Math.PI * Math.min(1, Math.max(0, u))), 0.8)));
}

function unwrapDirection(xs, ys) {
  const n = xs.length; const dir = new Float32Array(n);
  let last = 0;
  for (let i = 0; i < n; i += 1) {
    const a = xs[Math.min(n - 1, i + 1)] - xs[Math.max(0, i - 1)]; const b = ys[Math.min(n - 1, i + 1)] - ys[Math.max(0, i - 1)];
    let angle = a === 0 && b === 0 ? last : Math.atan2(b, a);
    if (i > 0) { while (angle - last > Math.PI) angle -= 2 * Math.PI; while (angle - last < -Math.PI) angle += 2 * Math.PI; }
    dir[i] = angle; last = angle;
  }
  return dir;
}

/** Control points [[x, y], ...] to a Catmull-Rom curve resampled every PATH_STEP: {xs, ys, length}. */
export function resample(points) {
  const dense = [];
  const P = (i) => points[Math.min(points.length - 1, Math.max(0, i))];
  for (let i = 0; i < points.length - 1; i += 1) {
    const [p0, p1, p2, p3] = [P(i - 1), P(i), P(i + 1), P(i + 2)];
    const span = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]);
    const steps = Math.max(1, Math.ceil(span / 0.5));
    for (let k = 0; k < steps; k += 1) {
      const t = k / steps; const t2 = t * t; const t3 = t2 * t;
      const f = (a, b, c, d) => 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
      dense.push([f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])]);
    }
  }
  dense.push(points[points.length - 1].slice(0, 2));
  const cum = [0];
  for (let i = 1; i < dense.length; i += 1) cum.push(cum[i - 1] + Math.hypot(dense[i][0] - dense[i - 1][0], dense[i][1] - dense[i - 1][1]));
  const length = cum[cum.length - 1];
  const n = Math.max(2, Math.floor(length / PATH_STEP) + 1);
  const xs = new Float32Array(n); const ys = new Float32Array(n);
  let j = 0;
  for (let i = 0; i < n; i += 1) {
    const s = Math.min(length, i * PATH_STEP);
    while (j < cum.length - 2 && cum[j + 1] < s) j += 1;
    const span = cum[j + 1] - cum[j]; const t = span > 0 ? (s - cum[j]) / span : 0;
    xs[i] = dense[j][0] + (dense[j + 1][0] - dense[j][0]) * t; ys[i] = dense[j][1] + (dense[j + 1][1] - dense[j][1]) * t;
  }
  return {xs, ys, length};
}

function assemble(kind, xs, ys, length, {pressure, speed, tilt, azimuth}) {
  const n = xs.length; const p = new Float32Array(n); const v = new Float32Array(n);
  const tiltA = new Float32Array(n); const az = new Float32Array(n);
  const dir = unwrapDirection(xs, ys);
  for (let i = 0; i < n; i += 1) {
    const u = n > 1 ? i / (n - 1) : 0;
    p[i] = pressure(u, i); v[i] = speed(u, i); tiltA[i] = tilt(u, i); az[i] = azimuth(u, i, dir[i]);
  }
  return {kind, n, length, step: PATH_STEP, xs, ys, p, v, tilt: tiltA, az, dir};
}

function controlPoints(kind, h) {
  const mid = h / 2; const dy = (h - 324) / 2;
  if (kind === 'line') return [[87, mid], [350, mid], [610, mid], [975, mid]];
  if (kind === 'scribble') {
    const pts = []; const amp = h * 0.36;
    for (let i = 0; i <= 14; i += 1) {
      const t = i / 14; const edge = i === 0 || i === 14 ? 0.15 : 1;
      pts.push([120 + 820 * t, mid + (i % 2 ? 1 : -1) * amp * (0.35 + 0.65 * Math.sin(Math.PI * t)) * edge]);
    }
    return pts;
  }
  const pts = [];                                          // the S-curve: Procreate's thumbnail path
  for (let x = 87; x <= 975; x += 74) pts.push([x, 179.2 + dy + 28.8 * Math.sin(2 * Math.PI * (x - 55) / 1050)]);
  pts.push([975, 179.2 + dy + 28.8 * Math.sin(2 * Math.PI * (975 - 55) / 1050)]);
  return pts;
}

/**
 * A test stroke. opts: {kind: 's-curve'|'line'|'scribble'|'tap', height, level (0..1 pressure
 * scale), speed (scale of the speed profile), pointer: 'pencil'|'touch', touchPressure, tilt (0..1)}.
 */
export function testPath(opts = {}) {
  const kind = opts.kind || 's-curve';
  const h = opts.height || VIEW_H.wide;
  const level = opts.level === undefined ? PRESSURE_LEVELS.heavy : opts.level;
  const pencil = (opts.pointer || 'pencil') === 'pencil';
  const tilt = pencil ? (opts.tilt || 0) : 0;
  const touchP = opts.touchPressure === undefined ? 0.6 : opts.touchPressure;
  const parts = {
    pressure: (u) => (pencil ? pressureProfile(u, level) : touchP),
    speed: (u) => speedProfile(u, opts.speed === undefined ? 1 : opts.speed),
    tilt: () => tilt,
    azimuth: (u) => -Math.PI / 4 + 0.35 * Math.sin(2 * Math.PI * u),
  };
  if (kind === 'tap') {
    const xs = new Float32Array([VIEW_W / 2]); const ys = new Float32Array([h / 2]);
    return assemble('tap', xs, ys, 0, {...parts, pressure: () => (pencil ? Math.max(0.5, level) : touchP), speed: () => 0});
  }
  const {xs, ys, length} = resample(controlPoints(kind, h));
  return assemble(kind, xs, ys, length, parts);
}

/**
 * A drawn stroke from raw pointer samples [{x, y, t (ms), p, tilt, az}] in U. Light smoothing,
 * resampled; speed comes from the time stamps (6 U per ms is full speed).
 */
export function drawnPath(raw, opts = {}) {
  if (!raw || raw.length === 0) return null;
  const level = opts.level === undefined ? PRESSURE_LEVELS.heavy : opts.level;
  const pen = opts.pointerType === 'pen';
  if (raw.length === 1) {
    const only = raw[0];
    return assemble('drawn', new Float32Array([only.x]), new Float32Array([only.y]), 0,
      {pressure: () => (pen ? only.p : level), speed: () => 0, tilt: () => only.tilt || 0, azimuth: () => only.az || 0});
  }
  const pts = [raw[0]];
  for (let i = 1; i < raw.length; i += 1) if (Math.hypot(raw[i].x - pts[pts.length - 1].x, raw[i].y - pts[pts.length - 1].y) >= 1.5) pts.push(raw[i]);
  if (pts.length < 2) pts.push(raw[raw.length - 1]);
  const {xs, ys, length} = resample(pts.map((q) => [q.x, q.y]));
  const cum = [0];
  for (let i = 1; i < pts.length; i += 1) cum.push(cum[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y));
  const total = cum[cum.length - 1] || 1;
  const at = (field, s, fallback) => {
    let lo = 0; let hi = pts.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (cum[mid] <= s) lo = mid; else hi = mid; }
    const span = cum[hi] - cum[lo]; const t = span > 0 ? (s - cum[lo]) / span : 0;
    const a = pts[lo][field]; const b = pts[hi][field];
    return typeof a === 'number' && typeof b === 'number' ? a + (b - a) * t : fallback;
  };
  const speedAt = (s) => {
    const a = Math.max(0, s - 12); const b = Math.min(total, s + 12);
    const ta = at('t', a, 0); const tb = at('t', b, 1);
    return Math.min(1, Math.max(0, ((b - a) / Math.max(1, tb - ta)) / 6));
  };
  return assemble('drawn', xs, ys, length, {
    pressure: (u) => (pen ? Math.min(1, Math.max(0.02, at('p', u * total, level))) : level),
    speed: (u) => speedAt(u * total),
    tilt: (u) => (pen ? at('tilt', u * total, 0) : 0),
    azimuth: (u, i, dir) => (pen ? at('az', u * total, dir) : dir),
  });
}

/** Read the path at arc length s into `out` ({x, y, p, v, tilt, az, dir, u}); returns out. */
export function sampleAt(path, s, out) {
  const f = Math.min(path.n - 1, Math.max(0, s / path.step));
  const i = Math.min(path.n - 1, Math.floor(f)); const j = Math.min(path.n - 1, i + 1); const t = f - i;
  const mixv = (a) => a[i] + (a[j] - a[i]) * t;
  out.x = mixv(path.xs); out.y = mixv(path.ys); out.p = mixv(path.p); out.v = mixv(path.v);
  out.tilt = mixv(path.tilt); out.az = mixv(path.az); out.dir = mixv(path.dir);
  out.u = path.length > 0 ? Math.min(1, s / path.length) : 0;
  return out;
}
