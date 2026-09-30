// Render pipeline for the Chronicle Museum viewer (v2 hyper-realism pass, Phase 1).
//
//  - readRenderOptions(search)          URL flags -> options object (see OPTION_DOC below)
//  - configureRenderer(renderer, opts)  AgX tone mapping, exposure, soft shadow maps
//  - setupEnvironment(renderer, scene, opts)  PMREM(RoomEnvironment) as scene.environment,
//                                        sky_v2.jpg (equirect, sRGB) or a warm dark colour as background
//  - createPipeline(renderer, scene, camera, opts)
//        EffectComposer (multisampled HalfFloat target) -> RenderPass -> UnrealBloomPass -> OutputPass.
//        ?classic bypasses all of it and calls renderer.render directly (old look, for A/B).
//
// Verified against three r160 sources: AgXToneMapping (=6), EffectComposer(renderer, renderTarget),
// WebGLRenderTarget options {type, samples}, RenderTarget.copy() copies samples (so the composer's
// clone for renderTarget2 is multisampled too), UnrealBloomPass(resolution, strength, radius, threshold)
// with HalfFloat mips and a LuminosityHighPass on linear HDR input, OutputPass applying
// renderer.toneMapping + toneMappingExposure + sRGB transfer, RoomEnvironment(renderer) (renderer only
// switches its key light to physical intensity), PMREMGenerator.fromScene(scene, sigma, near, far).
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export const SKY_URL = '../assets/sky.jpg';

// Tuned defaults (see the Phase 1 report for how they were chosen).
export const RENDER_DEFAULTS = {
  exposure: 1.0,        // AgX exposure (contract: 1, ?exposure= overrides)
  bloomStrength: 0.32,
  bloomRadius: 0.5,
  bloomThreshold: 1.0,  // linear HDR luminance; only emissive / specular values above 1 bloom
  bloomSmooth: 0.15,
  samples: 4,           // MSAA samples of the composer target
  skyIntensity: 1.0,    // scene.backgroundIntensity for sky_v2.jpg
  warmBackground: 0x16110b,
  classicBackground: 0x0a0806,
  // RoomEnvironment is a neutral white studio. Used as-is it floods every surface with grey fill
  // light (walls read as grey plaster, gilt reflects white softboxes). Before prefiltering it we
  // tint it like a lamp-lit interior: warm walls/props, warm light panels, and a dark wooden floor
  // plane so reflections have a dark lower hemisphere (metal then reads as metal).
  envTint: {
    wall: '#8c7a66',    // room box (BackSide)
    prop: '#7a6a58',    // the six furniture boxes
    light: '#ffd9a8',   // multiplies the emissive panels and the key point light (~3000 K)
    floor: '#2a1a0e',   // added floor plane (null disables it)
  },
};

// URL flags understood by the viewer. Everything is optional.
//   ?classic            old look: no tone mapping / env / bloom / shadows, hemisphere light only
//   ?exposure=1.2       AgX exposure
//   ?bloom=0.3          bloom strength (0 disables the pass)
//   ?env=0.5            envMapIntensity for non-metal materials (materials.js)
//   ?lights=1.0         global multiplier on all punctual light intensities (lights.js)
//   ?shadows=0          disable shadow maps
//   ?debug              overlay (debug.js)
//   ?view=<name>        place the camera at a layout view on load (scenes.js applyView)
//   ?room=<id>          start in a room (scenes.js)
//   ?work=<id>          start in front of a work with its placard open (navigate.js)
//   ?resume=1           restore the last saved scene and position (persist.js)
//   ?wing=0             leave the People wing out (its doors and rooms)
//   ?tourDwell=6        seconds the guided tour pauses at each work (tour.js)
//   ?test               no animation loop; the test harness drives museumDebug.step()/renderOnce()
export function readRenderOptions(search = window.location.search) {
  const p = new URLSearchParams(search);
  const num = (k, d) => {
    if (!p.has(k)) return d;
    const v = parseFloat(p.get(k));
    return Number.isFinite(v) ? v : d;
  };
  const flag = (k) => p.has(k) && p.get(k) !== '0' && p.get(k) !== 'false';
  return {
    classic: flag('classic'),
    debug: p.has('debug'),
    view: p.get('view') || null,
    exposure: num('exposure', RENDER_DEFAULTS.exposure),
    bloomStrength: num('bloom', RENDER_DEFAULTS.bloomStrength),
    envIntensity: p.has('env') ? num('env', null) : null,
    lightGain: num('lights', 1.0),
    shadows: !(p.has('shadows') && (p.get('shadows') === '0' || p.get('shadows') === 'false')),
    skyIntensity: num('sky', RENDER_DEFAULTS.skyIntensity),
    test: p.has('test'),
    room: p.get('room') || null,
    work: p.get('work') || null,
    resume: flag('resume'),
    wing: !(p.has('wing') && (p.get('wing') === '0' || p.get('wing') === 'false')),
    tourDwell: num('tourDwell', 6),
  };
}

export function configureRenderer(renderer, opts) {
  if (opts.classic) {
    renderer.toneMapping = THREE.NoToneMapping;
    renderer.toneMappingExposure = 1;
    renderer.shadowMap.enabled = false;
    return;
  }
  renderer.toneMapping = THREE.AgXToneMapping;
  renderer.toneMappingExposure = opts.exposure;
  renderer.shadowMap.enabled = opts.shadows;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  // The museum is static: shadow maps are re-rendered only when lights.js moves a
  // shadow-casting light (it sets renderer.shadowMap.needsUpdate).
  renderer.shadowMap.autoUpdate = false;
  renderer.shadowMap.needsUpdate = true;
}

async function urlExists(url) {
  try {
    const r = await fetch(url, { method: 'HEAD', cache: 'no-store' });
    return r.ok;
  } catch (e) {
    return false;
  }
}

// Warm the RoomEnvironment scene in place (r160 layout: one PointLight, a BackSide
// MeshStandardMaterial room box, six MeshStandardMaterial boxes, six MeshBasicMaterial light panels
// whose colour holds the panel intensity). The added floor plane sits on the room box floor (y = -0.95).
export function tintRoomEnvironment(room, tint) {
  if (!tint) return room;
  const light = new THREE.Color(tint.light || '#ffffff');
  const wall = new THREE.Color(tint.wall || '#ffffff');
  const prop = new THREE.Color(tint.prop || '#ffffff');
  room.traverse((o) => {
    if (o.isLight) { o.color.multiply(light); return; }
    if (!o.isMesh || !o.material) return;
    const m = o.material;
    if (m.isMeshBasicMaterial) m.color.multiply(light);
    else if (m.side === THREE.BackSide) m.color.copy(wall);
    else m.color.copy(prop);
  });
  if (tint.floor) {
    const floor = new THREE.Mesh(
      new THREE.PlaneGeometry(40, 40),
      new THREE.MeshStandardMaterial({ color: new THREE.Color(tint.floor), roughness: 0.6 }),
    );
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.9;
    room.add(floor); // disposed with the room (RoomEnvironment.dispose traverses its meshes)
  }
  return room;
}

export async function setupEnvironment(renderer, scene, opts) {
  const info = { environment: 'none', background: 'color' };
  if (opts.classic) {
    scene.background = new THREE.Color(RENDER_DEFAULTS.classicBackground);
    scene.environment = null;
    return info;
  }
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment(renderer);
  tintRoomEnvironment(room, RENDER_DEFAULTS.envTint);
  const envRT = pmrem.fromScene(room, 0.04);
  scene.environment = envRT.texture;
  room.dispose();
  pmrem.dispose();
  info.environment = 'RoomEnvironment(warm)';

  scene.background = new THREE.Color(RENDER_DEFAULTS.warmBackground);
  if (await urlExists(SKY_URL)) {
    try {
      const tex = await new THREE.TextureLoader().loadAsync(SKY_URL);
      tex.mapping = THREE.EquirectangularReflectionMapping;
      tex.colorSpace = THREE.SRGBColorSpace;
      scene.background = tex;
      scene.backgroundIntensity = opts.skyIntensity;
      info.background = 'sky';
    } catch (e) {
      console.warn('[museum] sky.jpg failed to load; using the warm background colour', e);
    }
  }
  return info;
}

export function createPipeline(renderer, scene, camera, opts) {
  const size = renderer.getSize(new THREE.Vector2());

  if (opts.classic) {
    return {
      mode: 'classic',
      composer: null,
      bloomPass: null,
      render() { renderer.render(scene, camera); },
      setSize() {},
      setExposure() {},
      setBloom() {},
      state() { return { mode: 'classic' }; },
      dispose() {},
    };
  }

  // Composer resets info itself would only show the last full-screen pass; count the whole frame.
  renderer.info.autoReset = false;

  const pr = renderer.getPixelRatio();
  // A hidden tab can report a 0x0 window; zero-sized attachments make the framebuffer incomplete.
  size.x = Math.max(1, size.x);
  size.y = Math.max(1, size.y);
  const target = new THREE.WebGLRenderTarget(size.x * pr, size.y * pr, {
    type: THREE.HalfFloatType,
    samples: RENDER_DEFAULTS.samples,
  });
  target.texture.name = 'museum.composer.rt1';
  const composer = new EffectComposer(renderer, target);

  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(size.x, size.y),
    opts.bloomStrength,
    RENDER_DEFAULTS.bloomRadius,
    RENDER_DEFAULTS.bloomThreshold,
  );
  bloomPass.highPassUniforms.smoothWidth.value = RENDER_DEFAULTS.bloomSmooth;
  bloomPass.enabled = opts.bloomStrength > 0;
  composer.addPass(bloomPass);

  const outputPass = new OutputPass();
  composer.addPass(outputPass);

  // Keep the composer in step with the renderer. The canvas can be 0x0 while the tab is hidden
  // (zero-sized attachments make the framebuffer incomplete), so sizes are applied lazily.
  const _cur = new THREE.Vector2();
  const composerSize = new THREE.Vector2(size.x, size.y);
  let composerPR = pr;
  function render(delta) {
    renderer.getSize(_cur);
    if (_cur.x < 1 || _cur.y < 1) return; // nothing to draw into
    if (_cur.x !== composerSize.x || _cur.y !== composerSize.y || renderer.getPixelRatio() !== composerPR) {
      setSize(_cur.x, _cur.y);
    }
    renderer.info.reset();
    composer.render(delta);
  }

  function setSize(w, h) {
    if (w < 1 || h < 1) return;
    composerPR = renderer.getPixelRatio();
    composer.setPixelRatio(composerPR);
    composer.setSize(w, h);
    composerSize.set(w, h);
  }

  function setExposure(v) { renderer.toneMappingExposure = v; }

  function setBloom({ strength, radius, threshold, smooth } = {}) {
    if (strength !== undefined) { bloomPass.strength = strength; bloomPass.enabled = strength > 0; }
    if (radius !== undefined) bloomPass.radius = radius;
    if (threshold !== undefined) bloomPass.threshold = threshold;
    if (smooth !== undefined) bloomPass.highPassUniforms.smoothWidth.value = smooth;
  }

  function state() {
    return {
      mode: 'composer',
      toneMapping: 'AgX',
      exposure: renderer.toneMappingExposure,
      samples: target.samples,
      bloom: {
        enabled: bloomPass.enabled,
        strength: bloomPass.strength,
        radius: bloomPass.radius,
        threshold: bloomPass.threshold,
        smooth: bloomPass.highPassUniforms.smoothWidth.value,
      },
      shadows: renderer.shadowMap.enabled,
    };
  }

  function dispose() {
    composer.dispose();
    bloomPass.dispose();
  }

  return { mode: 'composer', composer, renderPass, bloomPass, outputPass, render, setSize, setExposure, setBloom, state, dispose };
}
