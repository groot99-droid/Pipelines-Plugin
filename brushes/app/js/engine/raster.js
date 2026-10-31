// raster.js - the software rasteriser: stamps in, coverage out. Pure (typed
// arrays only), so it runs the same in any browser and in Node, and the same
// stamps always give the same numbers.
//
// For each stamp the pixels of its bounding box are mapped back into the mask
// image (rotated, flipped, squashed by roundness) and sampled bilinearly from the
// mip that fits the stamp. The sample, times the grain (if any) and the stamp's
// alpha, builds up in the coverage buffer: normally acc += a (1 - acc), with
// "max transfer" acc = max(acc, a).
//
// Grain: the pattern is tiled in preview units. Its anchor follows `movement`:
// 1 pins it to the canvas, 0 carries it with the stamp, in between a fraction of
// the stamp's travel (INFERRED, and the polarity of the key is not proven).
// `zoom` makes the texel size follow the stamp diameter. `depth` blends the
// grain in: factor = (1 - depth) + depth * grain.

import {CALIBRATION as C} from './model.js';

function chooseLevel(levels, px) {
  for (let i = levels.length - 1; i > 0; i -= 1) if (Math.max(levels[i].w, levels[i].h) >= px) return levels[i];
  return levels[0];
}

/** The 256-entry table from grain luminance to the factor applied to the stamp's coverage. */
export function grainTable(depth, inverted) {
  const lut = new Float32Array(256);
  for (let i = 0; i < 256; i += 1) { const g = inverted ? 1 - i / 255 : i / 255; lut[i] = (1 - depth) + depth * g; }
  return lut;
}

/** A rough count of the pixels the stamps cover (their bounding boxes): the cost estimate of a render. */
export function estimateOps(stamps, k) {
  let ops = 0;
  for (const st of stamps) { const px = Math.max(1.2, st.d * k) * 1.25 + 1; ops += px * px; }
  return ops;
}

/**
 * Rasterise stamps[from..to) into ctx.acc.
 * ctx: {acc: Float32Array(w*h), w, h, k (pixels per U), mask: {levels, fx, fy},
 *       grain: null | {levels, w, h, texelsW, texelsH}, grainModel: {movement, zoom, scale, depth, inverted},
 *       maxTransfer}
 * Returns the number of pixels visited.
 */
export function rasterStamps(stamps, from, to, ctx) {
  const {acc, w, h, k, mask, grain, maxTransfer} = ctx;
  const gm = ctx.grainModel || {movement: 1, zoom: 0, scale: 1, depth: 1, inverted: false};
  const lut = grain ? (ctx.grainLut || (ctx.grainLut = grainTable(gm.depth, gm.inverted))) : null;
  let visited = 0;
  for (let n = from; n < to; n += 1) {
    const st = stamps[n];
    let Dpx = st.d * k;
    if (!(Dpx > 0.05)) continue;
    let alpha = st.alpha;
    if (Dpx < 1.2) { alpha *= (Dpx / 1.2) * (Dpx / 1.2); Dpx = 1.2; }                  // a speck: spread over one pixel
    const lev = chooseLevel(mask.levels, Dpx);
    const mw = lev.w; const mh = lev.h; const md = lev.data;
    const cos = Math.cos(st.angle); const sin = Math.sin(st.angle);
    const cx = st.x * k; const cy = st.y * k;
    const hx = 0.5 * mask.fx * Dpx; const hy = 0.5 * mask.fy * Dpx * st.sy;
    const bx = Math.abs(cos) * hx + Math.abs(sin) * hy; const by = Math.abs(sin) * hx + Math.abs(cos) * hy;
    const x0 = Math.max(0, Math.floor(cx - bx - 1)); const x1 = Math.min(w - 1, Math.ceil(cx + bx + 1));
    const y0 = Math.max(0, Math.floor(cy - by - 1)); const y1 = Math.min(h - 1, Math.ceil(cy + by + 1));
    if (x1 < x0 || y1 < y0) continue;
    const sx = (st.fx ? -1 : 1); const sy = (st.fy ? -1 : 1);
    const ax = sx * cos / (Dpx * mask.fx) * mw; const ay = sx * sin / (Dpx * mask.fx) * mw;
    const bxx = sy * -sin / (Dpx * mask.fy * st.sy) * mh; const byy = sy * cos / (Dpx * mask.fy * st.sy) * mh;
    const dx0 = x0 + 0.5 - cx; const dy0 = y0 + 0.5 - cy;
    const uBase = ax * dx0 + ay * dy0 + 0.5 * mw - 0.5; const vBase = bxx * dx0 + byy * dy0 + 0.5 * mh - 0.5;
    const uMax = mw - 0.5; const vMax = mh - 0.5;

    let gData = null; let gMask = 0; let gox = 0; let goy = 0; let gsx = 0; let gW = 0; let gH = 0; let gYmask = 0;
    if (grain) {
      const z = 1 + gm.zoom * (st.d / C.GRAIN_REF_DIAMETER - 1);
      const texelU = C.GRAIN_TEXEL_U * (grain.texelsW / grain.w) * gm.scale * Math.max(0.02, z);
      const texelPx = texelU * k;
      let level = 0;
      while (level < grain.levels.length - 1 && texelPx * (1 << (level + 1)) <= 1.0001) level += 1;
      const gl = grain.levels[level];
      gData = gl.data; gW = gl.w; gH = gl.h; gMask = gW - 1; gYmask = gH - 1;
      const inv = 1 / (texelU * (1 << level));
      gsx = inv / k;
      gox = 0.5 * gsx - (1 - gm.movement) * st.x * inv;
      goy = 0.5 * gsx - (1 - gm.movement) * st.y * inv;
    }

    for (let y = y0; y <= y1; y += 1) {
      let u = uBase + ay * (y - y0); let v = vBase + byy * (y - y0);
      const gy = grain ? (Math.floor(y * gsx + goy) & gYmask) * gW : 0;
      let i = y * w + x0;
      for (let x = x0; x <= x1; x += 1, i += 1, u += ax, v += bxx) {
        if (u < -0.5 || v < -0.5 || u > uMax || v > vMax) continue;
        let iu = Math.floor(u); let iv = Math.floor(v);
        const fu = u - iu; const fv = v - iv;
        let ju = iu + 1; let jv = iv + 1;
        if (iu < 0) iu = 0; if (iv < 0) iv = 0; if (ju >= mw) ju = mw - 1; if (jv >= mh) jv = mh - 1;
        if (iu >= mw) iu = mw - 1; if (iv >= mh) iv = mh - 1;
        const r0 = iv * mw; const r1 = jv * mw;
        const cov = ((md[r0 + iu] * (1 - fu) + md[r0 + ju] * fu) * (1 - fv) + (md[r1 + iu] * (1 - fu) + md[r1 + ju] * fu) * fv) * (1 / 255);
        if (cov <= 0) continue;
        let a = alpha * cov;
        if (grain) a *= lut[gData[gy + (Math.floor(x * gsx + gox) & gMask)]];
        if (maxTransfer) { if (a > acc[i]) acc[i] = a; } else acc[i] += a * (1 - acc[i]);
      }
    }
    visited += (x1 - x0 + 1) * (y1 - y0 + 1);
  }
  return visited;
}
