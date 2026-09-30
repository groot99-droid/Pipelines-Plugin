// Material library: PBR texture sets (CC0, assets/textures/<set>/) with world-space tiling.
//
// Geometry built by procroom.js bakes its world transform and gets UVs from world coordinates
// divided by the material's `tile` (metres per repeat), so tiling is seamless across pieces and
// merged geometries. Every material here carries userData.pbr = true: materials.js's
// name-based gilt/brass overrides skip them.
import * as THREE from 'three';

const TEX_ROOT = '../assets/textures/';

const SETS = {
  parquet: { albedo: 'parquet/albedo.jpg', normal: 'parquet/normal.jpg', arm: 'parquet/arm.jpg', tile: [3.4, 3.4] },
  marble: { albedo: 'marble/albedo.jpg', normal: 'marble/normal.jpg', roughness: 'marble/roughness.jpg', tile: [2.0, 2.0] },
  plaster: { albedo: 'plaster/albedo.jpg', normal: 'plaster/normal.jpg', roughness: 'plaster/roughness.jpg', tile: [3.0, 1.5] },
  metal: { albedo: 'metal/albedo.jpg', normal: 'metal/normal.jpg', roughness: 'metal/roughness.jpg', metalness: 'metal/metalness.jpg', tile: [0.5, 0.5] },
};

// slot -> recipe. color multiplies the albedo; rough/metal multiply the maps (or are the value when there is no map).
const SLOTS = {
  parquet: { set: 'parquet', color: '#b98b5f', rough: 0.9, normalScale: 1.0, env: 0.35 },
  marble_white: { set: 'marble', color: '#f1ece2', rough: 0.55, normalScale: 0.5, env: 0.45 },
  marble_dark: { set: 'marble', color: '#3a3330', rough: 0.5, normalScale: 0.5, env: 0.5 },
  plaster_wall: { set: 'plaster', color: '#d9cbb2', rough: 1.0, normalScale: 0.6, env: 0.3 },
  plaster_ceiling: { set: 'plaster', color: '#f2ede2', rough: 1.0, normalScale: 0.4, env: 0.25 },
  painted_trim: { set: 'plaster', color: '#efe6d6', rough: 0.7, normalScale: 0.3, env: 0.35, tile: [1.0, 0.5] },
  stone: { set: 'plaster', color: '#a89b86', rough: 1.0, normalScale: 0.8, env: 0.25, tile: [1.5, 0.75] },
  sandstone: { set: 'plaster', color: '#b8955e', rough: 1.0, normalScale: 0.9, env: 0.25, tile: [1.2, 0.6] },
  gilt: { set: 'metal', color: '#f0c56a', rough: 0.32, metal: 1.0, normalScale: 0.3, env: 1.3 },
  brass: { set: 'metal', color: '#d3a35d', rough: 0.38, metal: 1.0, normalScale: 0.3, env: 1.2 },
  bronze: { set: 'metal', color: '#6d4a2a', rough: 0.45, metal: 1.0, normalScale: 0.4, env: 1.0 },
  iron: { set: 'metal', color: '#2c2d2c', rough: 0.55, metal: 1.0, normalScale: 0.5, env: 0.8 },
  steel: { set: 'metal', color: '#c9cbcd', rough: 0.3, metal: 1.0, normalScale: 0.2, env: 1.2 },
  chrome: { set: 'metal', color: '#e6e6e8', rough: 0.15, metal: 1.0, normalScale: 0.1, env: 1.4 },
  oak: { set: 'parquet', color: '#9a7048', rough: 0.75, normalScale: 0.6, env: 0.3, tile: [1.2, 1.2] },
  walnut: { set: 'parquet', color: '#6a4a34', rough: 0.6, normalScale: 0.5, env: 0.35, tile: [1.0, 1.0] },
  dark_wood: { set: 'parquet', color: '#2e1f16', rough: 0.55, normalScale: 0.4, env: 0.35, tile: [0.8, 0.8] },
  lacquer: { set: null, color: '#141212', rough: 0.25, metal: 0.0, env: 0.8 },
  frosted_glass: { set: null, color: '#dfe9ee', rough: 0.35, metal: 0.0, env: 1.0, transparent: true, opacity: 0.55 },
  glass: { set: null, color: '#ffffff', rough: 0.05, metal: 0.0, env: 1.2, transparent: true, opacity: 0.18 },
  laylight: { set: null, color: '#fff6e6', rough: 0.9, metal: 0.0, env: 0.0, emissive: '#fff2dc', emissiveIntensity: 1.15 },
  bulb: { set: null, color: '#fff3d8', rough: 0.9, metal: 0.0, env: 0.0, emissive: '#ffd9a0', emissiveIntensity: 2.6 },
  candle: { set: null, color: '#fff7e8', rough: 0.9, metal: 0.0, env: 0.0, emissive: '#ffe3b0', emissiveIntensity: 3.0 },
  canvas: { set: null, color: '#efe6d2', rough: 0.6, metal: 0.0, env: 0.5 },
  mat_board: { set: null, color: '#f4efe4', rough: 0.95, metal: 0.0, env: 0.3 },
  backing: { set: null, color: '#1a1512', rough: 0.9, metal: 0.0, env: 0.1 },
};

export function createMaterialLibrary(renderer, { texRoot = TEX_ROOT } = {}) {
  const loader = new THREE.TextureLoader();
  const maxAniso = renderer ? renderer.capabilities.getMaxAnisotropy() : 1;
  const textures = new Map();
  const materials = new Map();

  function tex(rel, srgb) {
    if (textures.has(rel)) return textures.get(rel);
    const t = loader.load(texRoot + rel);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.anisotropy = maxAniso;
    t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
    textures.set(rel, t);
    return t;
  }

  // Returns the material for a slot, optionally tinted (a tinted variant is cached per colour).
  function get(slot, { color = null } = {}) {
    const key = color ? `${slot}@${color}` : slot;
    if (materials.has(key)) return materials.get(key);
    const r = SLOTS[slot] || SLOTS.plaster_wall;
    const set = r.set ? SETS[r.set] : null;
    const params = {
      name: `MAT-v2_${key}`,
      color: new THREE.Color(color || r.color),
      roughness: r.rough !== undefined ? r.rough : 1,
      metalness: r.metal !== undefined ? r.metal : 0,
      envMapIntensity: r.env !== undefined ? r.env : 0.3,
    };
    if (set) {
      params.map = tex(set.albedo, true);
      if (set.normal) { params.normalMap = tex(set.normal, false); params.normalScale = new THREE.Vector2(r.normalScale || 1, r.normalScale || 1); }
      if (set.arm) { params.aoMap = tex(set.arm, false); params.roughnessMap = tex(set.arm, false); params.metalnessMap = tex(set.arm, false); params.aoMapIntensity = 1; }
      if (set.roughness) params.roughnessMap = tex(set.roughness, false);
      if (set.metalness) params.metalnessMap = tex(set.metalness, false);
      if (r.metal !== undefined && !set.metalness && !set.arm) params.metalness = r.metal;
    }
    if (r.emissive) { params.emissive = new THREE.Color(r.emissive); params.emissiveIntensity = r.emissiveIntensity || 1; }
    if (r.transparent) { params.transparent = true; params.opacity = r.opacity; params.depthWrite = false; params.side = THREE.DoubleSide; }
    const m = new THREE.MeshStandardMaterial(params);
    m.userData.pbr = true;
    m.userData.slot = slot;
    m.userData.tile = r.tile || (set ? set.tile : [1, 1]);
    materials.set(key, m);
    return m;
  }

  function tileOf(slot) {
    const r = SLOTS[slot] || SLOTS.plaster_wall;
    return r.tile || (r.set ? SETS[r.set].tile : [1, 1]);
  }

  return { get, tileOf, textures, materials, slots: Object.keys(SLOTS) };
}

// World-space UVs for a geometry whose positions are already in world (three.js) coordinates:
// each vertex takes the two world axes perpendicular to its dominant normal axis, divided by tile.
export function applyWorldUV(geometry, tile = [1, 1]) {
  const pos = geometry.attributes.position;
  let nor = geometry.attributes.normal;
  if (!nor) { geometry.computeVertexNormals(); nor = geometry.attributes.normal; }
  const tu = Array.isArray(tile) ? tile[0] : tile;
  const tv = Array.isArray(tile) ? tile[1] : tile;
  const uv = new Float32Array(pos.count * 2);
  for (let i = 0; i < pos.count; i++) {
    const nx = Math.abs(nor.getX(i)), ny = Math.abs(nor.getY(i)), nz = Math.abs(nor.getZ(i));
    const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
    let u, v;
    if (ny >= nx && ny >= nz) { u = x; v = z; }        // floors / ceilings
    else if (nx >= nz) { u = z; v = y; }               // walls facing ±x
    else { u = x; v = y; }                             // walls facing ±z
    uv[2 * i] = u / tu;
    uv[2 * i + 1] = v / tv;
  }
  geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  return geometry;
}
