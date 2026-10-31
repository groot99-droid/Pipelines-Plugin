// engine.js - the stroke-preview seam.
//
// THE INTERFACE (phase 3b replaces the body of createEngine and touches no
// other module):
//
//   createEngine(canvas: HTMLCanvasElement) -> {
//     render(params, opts) -> Promise<{engine, drew}>   // draw one preview
//     setBadges(map)                                    // optional
//     dispose()                                         // release everything
//   }
//
//   params  the effective settings: {schemaKey: JSON form} - the opened brush
//           with the user's patch applied (F3 JSON value forms: numbers,
//           booleans, {"points": [...]} curves, {"$data"} ...).
//   opts    {
//             width, height      CSS pixel size of the canvas box
//             era, name          the brush's era id and name
//             thumbnailUrl       blob:/data: URL of Procreate's own stroke
//                                thumbnail (1060x324 white-on-transparent), or null
//             shapeUrl, grainUrl blob: URLs of the shape and grain images, or
//                                null when they ship inside Procreate
//             shapeInfo, grainInfo   {source, ref} as in F10 import
//             dark               true when the page is in dark mode
//           }
//   setBadges(map)  {schemaKey: 'honoured' | 'approx' | 'ignored'}, the
//           `preview` column of silica_keys.json (F4): what the engine does
//           with each key. The panels already show the same badge; an engine
//           that models a key differently should say so by changing the schema.
//
// The 3a placeholder below draws Procreate's own thumbnail if there is one,
// otherwise a labelled box. It renders NOTHING from the settings.

export const ENGINE_NAME = 'placeholder (3a)';

export function createEngine(canvas) {
  let disposed = false;
  let badges = {};
  let serial = 0;
  const ctx = canvas.getContext('2d');

  function colors(dark) {
    const cs = getComputedStyle(canvas);
    const get = (name, fallback) => cs.getPropertyValue(name).trim() || fallback;
    return {paper: dark ? '#0f0e0d' : '#2a2825', text: get('--muted', '#aaa'), line: get('--line', '#555')};
  }

  function size(opts) {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const w = Math.max(160, Math.round(opts.width || canvas.clientWidth || 320));
    const h = Math.max(80, Math.round(opts.height || w * 324 / 1060));
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return {w, h};
  }

  function label(c, w, h, lines) {
    ctx.fillStyle = c.text;
    ctx.font = '14px system-ui, sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    lines.forEach((line, i) => ctx.fillText(line, w / 2, h / 2 + (i - (lines.length - 1) / 2) * 20, w - 24));
  }

  function loadImage(url) {
    return new Promise((resolve) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => resolve(null);
      image.src = url;
    });
  }

  return {
    name: ENGINE_NAME,
    async render(params, opts = {}) {
      if (disposed) return {engine: ENGINE_NAME, drew: 'nothing'};
      const mine = ++serial;
      const {w, h} = size(opts);
      const c = colors(!!opts.dark);
      ctx.fillStyle = c.paper; ctx.fillRect(0, 0, w, h);
      ctx.strokeStyle = c.line; ctx.lineWidth = 1; ctx.strokeRect(0.5, 0.5, w - 1, h - 1);
      if (opts.thumbnailUrl) {
        const image = await loadImage(opts.thumbnailUrl);
        if (image && mine === serial && !disposed) {
          const scale = Math.min(w / image.width, h / image.height);
          const dw = image.width * scale; const dh = image.height * scale;
          ctx.drawImage(image, (w - dw) / 2, (h - dh) / 2, dw, dh);
          ctx.fillStyle = c.text; ctx.font = '11px system-ui, sans-serif'; ctx.textAlign = 'left'; ctx.textBaseline = 'bottom';
          ctx.fillText('Procreate’s own thumbnail, not a render of the settings', 8, h - 6, w - 16);
          return {engine: ENGINE_NAME, drew: 'thumbnail'};
        }
      }
      if (mine !== serial) return {engine: ENGINE_NAME, drew: 'stale'};
      label(c, w, h, ['Stroke preview', 'The stroke engine arrives in phase 3b.', opts.name ? `Brush: ${opts.name}` : '']);
      return {engine: ENGINE_NAME, drew: 'label'};
    },
    setBadges(map) { badges = map || {}; },
    get badges() { return badges; },
    dispose() { disposed = true; serial += 1; ctx.clearRect(0, 0, canvas.width, canvas.height); },
  };
}
