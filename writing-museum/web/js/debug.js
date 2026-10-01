// ?debug overlay and ?view=<framing> camera placement (contract §7).
//
// createDebug({ renderer, scene, camera, pipeline, lights, controls, manifest, roomAt, opts, info })
//   -> { update(delta), setView(name), framings(), overlay }
// The overlay is created by JS with inline styles (index.html / museum.css are not touched).
// Camera position is shown in BLENDER coordinates (x, y-north, z-up) = three (x, -z, y).
import * as THREE from 'three';


// Blender Z-up -> three Y-up
function b2t([x, y, z]) { return new THREE.Vector3(x, z, -y); }

export function applyFraming(camera, f) {
  const pos = b2t(f.pos);
  const tgt = b2t(f.target);
  camera.position.copy(pos);
  camera.up.set(0, 1, 0);
  camera.lookAt(tgt);
  if (f.fov_deg) {
    camera.fov = f.fov_deg;
    camera.updateProjectionMatrix();
  }
}

function makeOverlay() {
  const el = document.createElement('div');
  el.id = 'museum-debug';
  Object.assign(el.style, {
    position: 'fixed', left: '8px', bottom: '8px', zIndex: '40', pointerEvents: 'none',
    font: '11px/1.35 ui-monospace, Consolas, monospace', color: '#f2ead9',
    background: 'rgba(12, 9, 6, 0.78)', border: '1px solid rgba(202, 162, 77, 0.6)',
    borderRadius: '3px', padding: '6px 8px', whiteSpace: 'pre', maxWidth: '46vw', overflow: 'hidden',
  });
  document.body.appendChild(el);
  return el;
}

export function createDebug({ renderer, scene, camera, pipeline, lights, controls, manifest, roomAt, opts, info = {}, scenes = null }) {
  const overlay = opts.debug ? makeOverlay() : null;
  let frames = 0;
  let acc = 0;
  let fps = 0;
  let sinceText = 0;
  let viewName = null;

  function roomLabel() {
    const geo = roomAt ? roomAt(camera.position) : null;
    const g = geo ? geo.id : '-';
    return `${g}  (scene: ${scenes ? scenes.currentId() || '-' : '-'})`;
  }

  function text() {
    const r = renderer.info;
    const p = camera.position;
    const bl = `${p.x.toFixed(2)}, ${(-p.z).toFixed(2)}, ${p.y.toFixed(2)}`;
    const lines = [
      `fps ${fps.toFixed(0)}   calls ${r.render.calls}   tris ${r.render.triangles.toLocaleString()}`,
      `textures ${r.memory.textures}   geometries ${r.memory.geometries}   programs ${r.programs ? r.programs.length : '?'}`,
      `cam (blender) ${bl}   fov ${camera.fov.toFixed(1)}${viewName ? `   view ${viewName}` : ''}`,
      `room ${roomLabel()}`,
      `scene ${scenes ? scenes.currentId() || '?' : '?'}   pipeline ${pipeline ? pipeline.mode : '?'}   env ${info.environment || '-'}   bg ${info.background || '-'}`,
    ];
    if (pipeline && pipeline.state) {
      const s = pipeline.state();
      if (s.bloom) lines.push(`AgX exp ${s.exposure.toFixed(2)}   bloom ${s.bloom.enabled ? s.bloom.strength.toFixed(2) : 'off'} thr ${s.bloom.threshold.toFixed(2)}   msaa ${s.samples}   shadows ${s.shadows ? 'on' : 'off'}`);
    }
    if (lights && lights.state) {
      const l = lights.state();
      lines.push(`lights ${l.mode} (${l.count})  fixtures ${l.fixtures}+${l.dirFixtures}dir   sun ${l.sun.mode}@${l.sun.room || '-'} ${l.sun.intensity}`);
      lines.push(`  chandelier ${l.chandelier || '-'}`);
      lines.push(`  pool ${l.pool.map((n) => (n ? n.replace(/^(fallback-|FX-)/, '') : '-')).join(', ')}`);
    }
    if (info.materials) {
      const m = info.materials;
      lines.push(`materials gilt ${m.gilt} brass ${m.brass} glass ${m.glass} additive ${m.additive} art ${m.art}   aniso ${m.maxAnisotropy}   casters ${m.castShadow}`);
    }
    return lines.join('\n');
  }

  function update(delta) {
    frames++;
    acc += delta;
    sinceText += delta;
    if (acc >= 0.5) { fps = frames / acc; frames = 0; acc = 0; }
    if (overlay && sinceText >= 0.25) {
      sinceText = 0;
      overlay.textContent = text();
    }
  }

  async function setView(name) {
    if (!scenes) return false;
    const r = scenes.applyView(name);
    if (!r) {
      console.warn(`[museum] unknown view "${name}". Known: ${scenes.views().join(', ')}`);
      return false;
    }
    await r;
    viewName = name;
    const blocker = document.getElementById('blocker');
    if (blocker) blocker.classList.add('hidden');
    if (lights) lights.update(camera, 0, true);
    if (overlay) overlay.textContent = text();
    return true;
  }
  function loadFramings() { return Promise.resolve(scenes ? scenes.views() : []); }

  // ---- look-dev helpers (window.museumDebug.measure / probe / tune) -------------------------
  // All of them render one frame first (renderOnce), because a hidden tab does not run rAF.
  let renderOnceFn = null;
  function setRenderOnce(fn) { renderOnceFn = fn; }
  function readFrame() {
    if (renderOnceFn) renderOnceFn();
    const gl = renderer.getContext();
    const w = gl.drawingBufferWidth;
    const h = gl.drawingBufferHeight;
    const px = new Uint8Array(w * h * 4);
    gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, px);
    return { w, h, px };
  }
  // Display-referred luminance stats of the final frame: mean, fraction clipped (>0.96),
  // fraction crushed (<0.05), 10-bin histogram.
  function measure(stride = 13) {
    const { w, h, px } = readFrame();
    let sum = 0, clip = 0, dark = 0, n = 0;
    const hist = new Array(10).fill(0);
    for (let i = 0; i < px.length; i += 4 * stride) {
      const l = (0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2]) / 255;
      sum += l; n++;
      if (l > 0.96) clip++;
      if (l < 0.05) dark++;
      hist[Math.min(9, Math.floor(l * 10))]++;
    }
    const r3 = (v) => +v.toFixed(3);
    return { w, h, mean: r3(sum / n), clip: r3(clip / n), dark: r3(dark / n), hist: hist.map((v) => +(v / n).toFixed(2)) };
  }
  // Mean sRGB 8-bit colour of 5x5 px patches at normalised screen points {name: [x, y]} (y down).
  function probe(points) {
    const { w, h, px } = readFrame();
    const out = {};
    for (const [k, [x, y]] of Object.entries(points)) {
      const X = Math.round(x * (w - 1));
      const Y = Math.round((1 - y) * (h - 1));
      let r = 0, g = 0, b = 0, n = 0;
      for (let dy = -2; dy <= 2; dy++) {
        for (let dx = -2; dx <= 2; dx++) {
          const xx = Math.min(w - 1, Math.max(0, X + dx));
          const yy = Math.min(h - 1, Math.max(0, Y + dy));
          const i = (yy * w + xx) * 4;
          r += px[i]; g += px[i + 1]; b += px[i + 2]; n++;
        }
      }
      out[k] = [Math.round(r / n), Math.round(g / n), Math.round(b / n)];
    }
    return out;
  }
  // Live look-dev: tune({exposure, bloom, bloomThreshold, hemi, env, gilt, art, gains: {type: g}, global})
  function tune(p = {}) {
    if (pipeline && p.exposure !== undefined) pipeline.setExposure(p.exposure);
    if (pipeline && (p.bloom !== undefined || p.bloomThreshold !== undefined)) {
      pipeline.setBloom({ strength: p.bloom, threshold: p.bloomThreshold });
    }
    if (lights) {
      if (p.hemi !== undefined) lights.setHemi(p.hemi);
      if (p.global !== undefined) lights.setGain(p.global);
      for (const [t, g] of Object.entries(p.gains || {})) lights.setTypeGain(t, g);
    }
    const setEnv = (cls, v) => scene.traverse((o) => {
      if (!o.isMesh) return;
      for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
        if (m && m.userData.patched === cls && (cls !== 'env' || (m.metalness || 0) < 0.5)) m.envMapIntensity = v;
      }
    });
    if (p.env !== undefined) setEnv('env', p.env);
    if (p.gilt !== undefined) setEnv('gilt', p.gilt);
    if (p.art !== undefined) setEnv('art', p.art);
    return measure();
  }

  return { update, setView, framings: loadFramings, overlay, text, measure, probe, tune, setRenderOnce };
}
