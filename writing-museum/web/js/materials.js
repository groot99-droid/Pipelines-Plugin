// Name-based material patches for the museum glTF (contract §7).
//
// patchMaterials(root, renderer, opts) -> stats
//   Material name (lower-case substring)            patch
//   gilt | trim_gold                                 metalness 1, roughness .28, envMapIntensity 1.6
//   brass                                            metalness 1, roughness .35, envMapIntensity 1.4
//   glass | glaze | crystal  (material name only)    transparent alpha blend, depthWrite false, no transmission
//   godray | sunpatch (material or object name)      MeshBasicMaterial, additive, depthWrite false, no shadows
//   ART-* meshes                                     envMapIntensity .35, receive shadows only
//   everything else (non-metal)                      envMapIntensity = opts.envIntensity (default ENV_DIFFUSE)
//   all textures                                     anisotropy = renderer max
//   GEO-* meshes                                     castShadow + receiveShadow, except light-emitting /
//                                                    see-through / fixture pieces (NO_CAST below)
// Classification never renames or re-parents anything, so main.js's wall/floor/ART lists are unaffected.
import * as THREE from 'three';

// envMapIntensity values assume render.js's warm-tinted RoomEnvironment (see RENDER_DEFAULTS.envTint).
export const MATERIAL_DEFAULTS = {
  envDiffuse: 0.3,     // dielectrics (plaster, parquet, marble ...): soft warm fill + floor sheen
  envGilt: 1.3,
  envBrass: 1.2,
  envArt: 0.6,
  envGlass: 1.2,
  // glTF default material (a mesh exported without a material: metallic 1, rough 1, white) -> stone
  defaultStone: { color: [0.55, 0.52, 0.47], roughness: 0.55 },
};

const TEX_SLOTS = [
  'map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap', 'alphaMap',
  'bumpMap', 'lightMap', 'clearcoatMap', 'clearcoatNormalMap', 'clearcoatRoughnessMap',
  'sheenColorMap', 'sheenRoughnessMap', 'specularIntensityMap', 'specularColorMap',
  'transmissionMap', 'thicknessMap', 'iridescenceMap', 'anisotropyMap',
];

// Meshes (object or material name) that must not cast shadows: emissive, transparent,
// or fixtures that would sit around their own light and blot out the room.
const NO_CAST = /glass|glaze|crystal|godray|sunpatch|laylight|candle|oculus_glow|chandelier|sconce|pendant|piclight|flame|bulb/;

function lower(s) { return (s || '').toLowerCase(); }

// GLTFLoader's default material for primitives without one: unnamed MeshStandardMaterial,
// white, metalness 1, roughness 1, no maps.
function isGltfDefault(mat) {
  return mat.isMeshStandardMaterial && !mat.name && mat.metalness === 1 && mat.roughness === 1 &&
    !mat.map && !mat.metalnessMap && !mat.roughnessMap && mat.color.r === 1 && mat.color.g === 1 && mat.color.b === 1;
}

// The GLTFLoader names a single-primitive mesh after its node; multi-primitive meshes become a
// Group (node name) with child meshes, so look one level up for the GEO-/ART- prefix too.
function ownerName(mesh) {
  const n = mesh.name || '';
  if (/^(GEO|ART|FX)-/.test(n)) return n;
  const p = mesh.parent && mesh.parent.name ? mesh.parent.name : '';
  return /^(GEO|ART|FX)-/.test(p) ? p : n;
}

function setAniso(mat, maxAniso, seen) {
  let n = 0;
  for (const slot of TEX_SLOTS) {
    const t = mat[slot];
    if (!t || !t.isTexture) continue;
    if (!seen.has(t)) {
      seen.add(t);
      n++;
    }
    if (t.anisotropy !== maxAniso) {
      t.anisotropy = maxAniso;
      if (t.image) t.needsUpdate = true;
    }
  }
  return n;
}

function makeAdditive(src) {
  const color = new THREE.Color(1, 1, 1);
  let strength = 1;
  if (src.emissive && (src.emissive.r + src.emissive.g + src.emissive.b) > 0) {
    color.copy(src.emissive);
    strength = src.emissiveIntensity !== undefined ? src.emissiveIntensity : 1;
  } else if (src.color) {
    color.copy(src.color);
  }
  color.multiplyScalar(strength);
  const m = new THREE.MeshBasicMaterial({
    name: src.name,
    color,
    map: src.emissiveMap || src.map || null,
    alphaMap: src.alphaMap || null,
    transparent: true,
    opacity: src.opacity !== undefined ? src.opacity : 1,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    side: THREE.DoubleSide,
    vertexColors: !!src.vertexColors,
    fog: false,
  });
  m.userData.patched = 'additive';
  return m;
}

export function patchMaterials(root, renderer, opts = {}) {
  const envDiffuse = opts.envIntensity != null ? opts.envIntensity : MATERIAL_DEFAULTS.envDiffuse;
  const maxAniso = renderer.capabilities.getMaxAnisotropy();
  const stats = {
    maxAnisotropy: maxAniso, textures: 0, materials: 0,
    gilt: 0, brass: 0, glass: 0, additive: 0, art: 0, other: 0,
    castShadow: 0, receiveShadow: 0,
  };
  const texSeen = new Set();
  const matDone = new Map();     // original material -> patched material (identity for in-place patches)
  const additiveCache = new Map();

  function patchOne(mat, mesh, isArt, objName) {
    if (matDone.has(mat)) return matDone.get(mat);
    const mn = lower(mat.name);
    const on = lower(objName);
    stats.textures += setAniso(mat, maxAniso, texSeen);
    stats.materials++;
    if (mat.userData && mat.userData.pbr) {
      // matlib.js / model materials carry their own roughness, metalness and env settings
      stats.pbr = (stats.pbr || 0) + 1;
      matDone.set(mat, mat);
      return mat;
    }

    if (/godray|sunpatch/.test(mn) || /godray|sunpatch/.test(on)) {
      let add = additiveCache.get(mat);
      if (!add) { add = makeAdditive(mat); additiveCache.set(mat, add); stats.additive++; }
      matDone.set(mat, add);
      return add;
    }
    if (isArt) {
      mat.envMapIntensity = MATERIAL_DEFAULTS.envArt;
      mat.userData.patched = 'art';
      stats.art++;
    } else if (/gilt|trim_gold/.test(mn)) {
      mat.metalness = 1;
      mat.roughness = 0.28;
      mat.envMapIntensity = MATERIAL_DEFAULTS.envGilt;
      mat.userData.patched = 'gilt';
      stats.gilt++;
    } else if (/brass/.test(mn)) {
      mat.metalness = 1;
      mat.roughness = 0.35;
      mat.envMapIntensity = MATERIAL_DEFAULTS.envBrass;
      mat.userData.patched = 'brass';
      stats.brass++;
    } else if (/glass|glaze|crystal/.test(mn)) {
      mat.transparent = true;
      mat.depthWrite = false;
      if ('transmission' in mat) mat.transmission = 0;
      if (mat.opacity >= 0.999) mat.opacity = /crystal/.test(mn) ? 0.35 : 0.12;
      mat.envMapIntensity = MATERIAL_DEFAULTS.envGlass;
      mat.side = THREE.DoubleSide;
      mat.userData.patched = 'glass';
      stats.glass++;
    } else {
      if (isGltfDefault(mat)) {
        // e.g. v1 GEO-stairhall_landing has no material: white chrome-grey in a lit scene.
        const d = MATERIAL_DEFAULTS.defaultStone;
        mat.color.setRGB(d.color[0], d.color[1], d.color[2]);
        mat.metalness = 0;
        mat.roughness = d.roughness;
        mat.name = 'MAT-default_stone(viewer)';
        stats.defaulted = (stats.defaulted || 0) + 1;
      }
      // Dielectrics: the environment is a warm probe, keep it as a soft fill.
      // Metals from the file (window_frame .6 etc.) get a stronger reflection.
      mat.envMapIntensity = (mat.metalness || 0) > 0.5 ? 1.2 : envDiffuse;
      mat.userData.patched = 'env';
      stats.other++;
    }
    mat.needsUpdate = true;
    matDone.set(mat, mat);
    return mat;
  }

  root.traverse((obj) => {
    if (!obj.isMesh) return;
    const name = ownerName(obj);
    const isArt = name.startsWith('ART-');
    if (Array.isArray(obj.material)) {
      obj.material = obj.material.map((m) => patchOne(m, obj, isArt, name));
    } else if (obj.material) {
      obj.material = patchOne(obj.material, obj, isArt, name);
    }
    const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
    const additive = mats.some((m) => m && m.userData.patched === 'additive');
    const seeThrough = mats.some((m) => m && m.transparent);
    const matNames = mats.map((m) => lower(m && m.name)).join(' ');
    if (isArt) {
      obj.castShadow = false;
      obj.receiveShadow = true;
    } else if (name.startsWith('GEO-') && !additive) {
      obj.receiveShadow = true;
      obj.castShadow = !seeThrough && !NO_CAST.test(lower(name)) && !NO_CAST.test(matNames);
    } else {
      obj.castShadow = false;
      obj.receiveShadow = !additive;
    }
    if (obj.castShadow) stats.castShadow++;
    if (obj.receiveShadow) stats.receiveShadow++;
  });
  return stats;
}
