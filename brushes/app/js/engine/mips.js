// mips.js - the mask and grain images of the rasteriser as typed arrays. Pure.
//
// A mask is a coverage image (0 = no paint, 255 = full) with a chain of
// half-size copies so a small stamp is drawn from a small image (no aliasing).
// A grain is a luminance image the stroke is drawn through, tiled; it is stored
// at power-of-two sizes so a tile lookup is a bit mask.

/** Box-filter half size copy of a single-channel image. */
export function halve(data, w, h) {
  const nw = Math.max(1, w >> 1); const nh = Math.max(1, h >> 1);
  const out = new Uint8Array(nw * nh);
  for (let y = 0; y < nh; y += 1) {
    const y0 = Math.min(h - 1, y * 2); const y1 = Math.min(h - 1, y0 + 1);
    for (let x = 0; x < nw; x += 1) {
      const x0 = Math.min(w - 1, x * 2); const x1 = Math.min(w - 1, x0 + 1);
      out[y * nw + x] = (data[y0 * w + x0] + data[y0 * w + x1] + data[y1 * w + x0] + data[y1 * w + x1] + 2) >> 2;
    }
  }
  return {data: out, w: nw, h: nh};
}

/** {levels: [{data, w, h}, ...]} from the base image down to at most `min` pixels on the short side. */
export function buildMips(data, w, h, min = 8) {
  const levels = [{data, w, h}];
  while (Math.min(levels[levels.length - 1].w, levels[levels.length - 1].h) > min) {
    const last = levels[levels.length - 1];
    levels.push(halve(last.data, last.w, last.h));
  }
  return {levels};
}

/**
 * The coverage of a shape image: `shapeInverted ? 255 - lum : lum`, times the image's own alpha
 * (PROVEN polarity on 391 shapes, critique-fidelity.md). `lum` and `alpha` are Uint8Arrays of w*h.
 */
export function coverageFrom(lum, alpha, inverted) {
  const out = new Uint8Array(lum.length);
  for (let i = 0; i < lum.length; i += 1) {
    const v = inverted ? 255 - lum[i] : lum[i];
    out[i] = alpha ? Math.round(v * alpha[i] / 255) : v;
  }
  return out;
}

/** A mask {levels, w, h, aspect: [fx, fy]} from lum/alpha at the given polarity. The longest side fits the stamp diameter. */
export function makeMask(lum, alpha, w, h, inverted) {
  const mips = buildMips(coverageFrom(lum, alpha, inverted), w, h);
  const side = Math.max(w, h);
  return {levels: mips.levels, w, h, fx: w / side, fy: h / side};
}

const pow2 = (n) => { let p = 1; while (p < n) p <<= 1; return p; };
export const isPow2 = (n) => n > 0 && (n & (n - 1)) === 0;
export {pow2};

/**
 * A grain {levels, w, h, texelsW, texelsH} from a luminance image whose sides are powers of two
 * (the caller resamples to that), remembering the size the image had originally so the scale is
 * in the image's own texels.
 */
export function makeGrain(lum, w, h, originalW, originalH) {
  if (!isPow2(w) || !isPow2(h)) throw new Error('grain sides must be powers of two');
  const mips = buildMips(lum, w, h, 4);
  return {levels: mips.levels, w, h, texelsW: originalW || w, texelsH: originalH || h};
}
