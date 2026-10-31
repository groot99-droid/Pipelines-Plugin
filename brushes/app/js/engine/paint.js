// paint.js - the thin canvas layer: coverage to pixels. DOM (canvas, ImageData).
//
// The stroke band is the coverage buffer mapped through the ink and background
// colours into one ImageData (packed 32-bit words, no per-pixel canvas calls);
// when the render ran at reduced resolution (a draft while a slider moves) it is
// drawn scaled up. Below it, when comparing, goes Procreate's own stored
// thumbnail, drawn from its alpha in the same ink so the two read alike on any
// background. Labels are canvas text.

import {VIEW_W, VIEW_H} from './path.js';
import {hashBytes} from './rng.js';

export const BACKGROUNDS = {
  dark: {label: 'Dark (white ink, like Procreate’s thumbnails)', bg: [27, 26, 24], ink: [255, 255, 255]},
  white: {label: 'White', bg: [255, 255, 255], ink: [17, 17, 17]},
  paper: {label: 'Paper', bg: [241, 234, 217], ink: [43, 38, 32]},
};

const pack = (r, g, b) => (255 << 24) | (b << 16) | (g << 8) | r;          // little endian RGBA words

function inkTable(scheme) {
  const {bg, ink} = scheme; const lut = new Uint32Array(256);
  for (let a = 0; a < 256; a += 1) {
    const t = a / 255;
    lut[a] = pack(Math.round(bg[0] + (ink[0] - bg[0]) * t), Math.round(bg[1] + (ink[1] - bg[1]) * t), Math.round(bg[2] + (ink[2] - bg[2]) * t));
  }
  return lut;
}

/** Canvas size for a view: {cw, bandH, gap, totalH, bandU, totalU} in device pixels and U. */
export const MAX_PIXELS_WIDE = 1000;           // the canvas is never more than this many device pixels across (cost grows with the square)

export function layoutFor(cssW, {tall = false, compare = false, dpr = 1} = {}) {
  dpr = Math.max(1, Math.min(dpr, MAX_PIXELS_WIDE / Math.max(1, cssW)));
  const cw = Math.max(160, Math.round(cssW * dpr));
  const bandU = tall ? VIEW_H.tall : VIEW_H.wide;
  const bandH = Math.round(cw * bandU / VIEW_W);
  const gap = compare ? Math.round(cw * 0.03) : 0;
  const totalH = compare ? bandH * 2 + gap : bandH;
  return {cw, bandH, gap, totalH, bandU, totalU: bandU * totalH / bandH, dpr};
}

export function createPainter(canvas) {
  const ctx = canvas.getContext('2d');
  let image = null; let words = null; let low = null;

  function bandImage(w, h) {
    if (!image || image.width !== w || image.height !== h) { image = new ImageData(w, h); words = new Uint32Array(image.data.buffer); }
    return image;
  }

  return {
    /** Size the canvas box (resizing clears it). */
    resize(layout) {
      if (canvas.width !== layout.cw || canvas.height !== layout.totalH) { canvas.width = layout.cw; canvas.height = layout.totalH; }
      canvas.style.setProperty('--engine-aspect', `${layout.cw} / ${layout.totalH}`);
    },
    background(layout, scheme) {
      const [r, g, b] = scheme.bg;
      ctx.fillStyle = `rgb(${r},${g},${b})`; ctx.fillRect(0, 0, layout.cw, layout.totalH);
    },
    /**
     * Draw the stroke band from a coverage buffer of rw x rh pixels (scaled up to the band when
     * smaller). Returns the hash of the 8-bit alpha of the band at its own resolution.
     */
    stroke(layout, scheme, acc, rw, rh, opacity) {
      const lut = inkTable(scheme);
      const img = bandImage(rw, rh);
      const n = rw * rh;
      const alpha = new Uint8Array(n);
      for (let i = 0; i < n; i += 1) {
        const a = acc[i] * opacity; const q = a <= 0 ? 0 : a >= 1 ? 255 : Math.round(a * 255);
        alpha[i] = q; words[i] = lut[q];
      }
      if (rw === layout.cw && rh === layout.bandH) ctx.putImageData(img, 0, 0);
      else {
        if (!low) low = document.createElement('canvas');
        low.width = rw; low.height = rh;
        low.getContext('2d').putImageData(img, 0, 0);
        ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
        ctx.drawImage(low, 0, 0, layout.cw, layout.bandH);
      }
      return hashBytes(alpha);
    },
    /** Procreate's stored thumbnail (alpha plane of cw x bandH, or null) below the stroke band. */
    thumbnail(layout, scheme, alpha) {
      const y = layout.bandH + layout.gap;
      if (!alpha) return false;
      const img = new ImageData(layout.cw, layout.bandH); const w32 = new Uint32Array(img.data.buffer); const lut = inkTable(scheme);
      for (let i = 0; i < alpha.length; i += 1) w32[i] = lut[alpha[i]];
      ctx.putImageData(img, 0, y);
      return true;
    },
    /** Small labels: [{text, x, y, align}] in device pixels. */
    labels(layout, scheme, list) {
      const px = Math.max(10, Math.round(11 * layout.dpr));
      ctx.font = `${px}px system-ui, sans-serif`; ctx.textBaseline = 'bottom';
      const [r, g, b] = scheme.ink;
      ctx.fillStyle = `rgba(${r},${g},${b},0.62)`;
      for (const item of list) { ctx.textAlign = item.align || 'left'; ctx.fillText(item.text, item.x, item.y, layout.cw - 2 * px); }
    },
    ctx,
  };
}
