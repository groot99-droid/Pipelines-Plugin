// assets.js - the images the preview draws with: the brush's own shape and grain
// (a PNG the page holds as a blob: URL), and Procreate's stored thumbnail. DOM:
// it decodes through an <img> and a scratch canvas. Decoded images are cached by
// URL, so a slider drag does not decode anything.
//
// A bundled shape or grain has no image here (it ships inside Procreate): the
// caller gets a generated stand-in from standins.js and the label to show.

import {makeMask, makeGrain, pow2} from './mips.js';
import {standinShape, standinGrain} from './standins.js';

const MASK_MAX = 512;
const GRAIN_MAX = 1024;
const KEEP = 10;

function scratch(w, h) {
  const canvas = document.createElement('canvas');
  canvas.width = w; canvas.height = h;
  return canvas;
}

function loadImage(url) {
  return new Promise((resolve) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => resolve(null);
    image.src = url;
  });
}

function remember(map, key, value) {
  map.set(key, value);
  if (map.size > KEEP) map.delete(map.keys().next().value);
  return value;
}

export function createAssets() {
  const images = new Map();      // url -> {lum, alpha, w, h, width, height} (shape) | grain entry
  const masks = new Map();       // url|inverted -> mask
  const grains = new Map();      // url -> grain
  const thumbs = new Map();      // url|w|h -> Uint8Array alpha

  async function decode(url, {maxSide, powerOfTwo}) {
    const key = `${url}|${maxSide}|${powerOfTwo ? 1 : 0}`;
    if (images.has(key)) return images.get(key);
    const image = await loadImage(url);
    if (!image) return remember(images, key, null);
    const width = image.naturalWidth; const height = image.naturalHeight;
    const shrink = Math.min(1, maxSide / Math.max(width, height));
    let w = Math.max(1, Math.round(width * shrink)); let h = Math.max(1, Math.round(height * shrink));
    if (powerOfTwo) { w = Math.min(maxSide, pow2(w)); h = Math.min(maxSide, pow2(h)); }
    const canvas = scratch(w, h);
    const g = canvas.getContext('2d', {willReadFrequently: true});
    g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
    g.drawImage(image, 0, 0, w, h);
    const px = g.getImageData(0, 0, w, h).data;
    const lum = new Uint8Array(w * h); const alpha = new Uint8Array(w * h);
    let opaque = true;
    for (let i = 0, j = 0; i < lum.length; i += 1, j += 4) {
      lum[i] = (px[j] * 77 + px[j + 1] * 151 + px[j + 2] * 28) >> 8;
      alpha[i] = px[j + 3];
      if (px[j + 3] !== 255) opaque = false;
    }
    return remember(images, key, {lum, alpha: opaque ? null : alpha, w, h, width, height});
  }

  return {
    /**
     * The shape mask: {mask, exact, standIn, label}. `url` is the brush's own PNG, or null when it
     * is bundled / absent (then a generated stand-in for `ref`).
     */
    async shape(url, ref, inverted) {
      if (url) {
        const key = `${url}|${inverted ? 1 : 0}`;
        if (masks.has(key)) return {mask: masks.get(key), exact: true, standIn: false, label: 'the brush’s own shape image'};
        const entry = await decode(url, {maxSide: MASK_MAX, powerOfTwo: false});
        if (entry) return {mask: remember(masks, key, makeMask(entry.lum, entry.alpha, entry.w, entry.h, inverted)), exact: true, standIn: false, label: 'the brush’s own shape image'};
      }
      const stand = standinShape(ref, inverted);
      return {mask: stand.mask, exact: stand.exact, standIn: !stand.exact, label: stand.label};
    },
    /** The grain: {grain|null, exact, standIn, label}. */
    async grain(url, ref, source) {
      if (url) {
        if (grains.has(url)) return {grain: grains.get(url), exact: true, standIn: false, label: 'the brush’s own grain image'};
        const entry = await decode(url, {maxSide: GRAIN_MAX, powerOfTwo: true});
        if (entry) return {grain: remember(grains, url, makeGrain(entry.lum, entry.w, entry.h, entry.width, entry.height)), exact: true, standIn: false, label: 'the brush’s own grain image'};
      }
      if (source === 'blank' || source === 'none' || !ref) return {grain: null, exact: true, standIn: false, label: source === 'none' ? 'no grain' : 'blank grain'};
      const stand = standinGrain(ref);
      return {grain: stand.grain, exact: stand.exact, standIn: !stand.exact, label: stand.label};
    },
    /** Procreate's stored thumbnail as an alpha plane resampled to w x h, or null. */
    async thumbnailAlpha(url, w, h) {
      if (!url) return null;
      const key = `${url}|${w}|${h}`;
      if (thumbs.has(key)) return thumbs.get(key);
      const image = await loadImage(url);
      if (!image) return remember(thumbs, key, null);
      const canvas = scratch(w, h);
      const g = canvas.getContext('2d', {willReadFrequently: true});
      g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
      g.drawImage(image, 0, 0, w, h);
      const px = g.getImageData(0, 0, w, h).data;
      const alpha = new Uint8Array(w * h);
      for (let i = 0, j = 3; i < alpha.length; i += 1, j += 4) alpha[i] = px[j];
      return remember(thumbs, key, alpha);
    },
    clear() { images.clear(); masks.clear(); grains.clear(); thumbs.clear(); },
  };
}
