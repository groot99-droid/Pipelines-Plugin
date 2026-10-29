// Third-party GLTF/GLB models (assets/models.json, fetched by fetch_models.py): a shared loader
// with Draco support (the Smithsonian scans are Draco-compressed), a cache per model id, and
// reference-counted clones so a scene can be disposed without touching the cached source.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const MODELS_URL = '../assets/models.json';
const MODELS_ROOT = '../assets/models/';
const DRACO_PATH = './vendor/three/examples/jsm/libs/draco/gltf/';

export function createModels(renderer) {
  const draco = new DRACOLoader();
  draco.setDecoderPath(DRACO_PATH);
  const loader = new GLTFLoader();
  loader.setDRACOLoader(draco);
  const maxAniso = renderer ? renderer.capabilities.getMaxAnisotropy() : 1;

  let catalog = null;
  const catalogReady = fetch(MODELS_URL).then((r) => (r.ok ? r.json() : { models: {} })).then((j) => { catalog = j.models || {}; return catalog; })
    .catch(() => { catalog = {}; return catalog; });

  const cache = new Map();   // id -> { promise, gltf, refs, height, pinned }
  const stats = { loads: 0, failures: 0 };

  function entry(id) {
    if (cache.has(id)) return cache.get(id);
    const e = { promise: null, gltf: null, refs: 0, height: 1, pinned: false, rec: null };
    e.promise = catalogReady.then(() => {
      const rec = catalog[id];
      if (!rec || !rec.file) throw new Error(`model ${id} is not in models.json (run fetch_models.py)`);
      e.rec = rec;
      e.pinned = !!rec.pinned;
      return loader.loadAsync(MODELS_ROOT + id + '/' + rec.file);
    }).then((gltf) => {
      const root = gltf.scene;
      // Voyager scenes store the upright rotation outside the GLB: apply it once to the source.
      if (e.rec.voyager_rotation && e.rec.voyager_rotation.length === 4) {
        const q = new THREE.Quaternion().fromArray(e.rec.voyager_rotation);
        root.quaternion.copy(q);
      }
      root.updateMatrixWorld(true);
      const box = new THREE.Box3().setFromObject(root);
      const size = box.getSize(new THREE.Vector3());
      e.height = Math.max(1e-3, size.y);
      e.bbox = box;
      root.traverse((o) => {
        if (!o.isMesh) return;
        o.castShadow = true;
        o.receiveShadow = true;
        for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
          if (!m) continue;
          m.userData.pbr = true;
          m.userData.model = id;
          if (m.map) m.map.anisotropy = maxAniso;
          if (m.envMapIntensity === undefined || m.envMapIntensity === 1) m.envMapIntensity = 0.5;
        }
      });
      e.gltf = gltf;
      stats.loads++;
      return e;
    }).catch((err) => {
      stats.failures++;
      console.warn('[museum] model failed:', id, err && err.message);
      cache.delete(id);
      throw err;
    });
    cache.set(id, e);
    return e;
  }

  // A clone scaled so its height is `targetH` (or the catalogue's target_h), standing on y = 0.
  async function acquire(id, { targetH = null } = {}) {
    const e = await entry(id).promise;
    const rec = e.rec;
    const h = targetH || rec.target_h || e.height;
    const s = h / e.height;
    const clone = e.gltf.scene.clone(true);
    clone.updateMatrixWorld(true);
    const holder = new THREE.Group();
    holder.name = `MODEL-${id}`;
    holder.add(clone);
    clone.scale.multiplyScalar(s);
    clone.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(clone);
    const c = box.getCenter(new THREE.Vector3());
    clone.position.set(-c.x, -box.min.y, -c.z); // centred in x/z, standing on y=0
    holder.userData.modelId = id;
    holder.userData.credits = rec;
    holder.userData.size = box.getSize(new THREE.Vector3());
    e.refs++;
    return holder;
  }

  function release(id) {
    const e = cache.get(id);
    if (!e) return;
    e.refs = Math.max(0, e.refs - 1);
    if (e.refs === 0 && !e.pinned && e.gltf) {
      e.gltf.scene.traverse((o) => {
        if (!o.isMesh) return;
        if (o.geometry) o.geometry.dispose();
        for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
          if (!m) continue;
          for (const k of ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap']) if (m[k] && m[k].dispose) m[k].dispose();
          m.dispose();
        }
      });
      cache.delete(id);
    }
  }

  function credits(id) { return catalog ? catalog[id] || null : null; }
  function state() { return { ...stats, cached: [...cache.keys()] }; }

  return { acquire, release, credits, catalogReady, state, cache };
}
