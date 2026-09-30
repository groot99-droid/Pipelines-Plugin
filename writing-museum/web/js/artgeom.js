// Geometry helpers for artwork meshes (both the exported glTF planes and the procedural
// wing's PlaneGeometry). Never assume a local axis: glTF ART planes face local +Y,
// PlaneGeometry faces +Z, so the world normal is read from the normal attribute and
// then checked against the walls (an art plane hangs 0.05 m off its wall, so a ray
// along the wrong side hits the wall immediately).
import * as THREE from 'three';

const _box = new THREE.Box3();
const _size = new THREE.Vector3();
const _center = new THREE.Vector3();
const _ray = new THREE.Raycaster();

export function artCenter(mesh, target = new THREE.Vector3()) {
  _box.setFromObject(mesh);
  return _box.getCenter(target);
}

export function artSize(mesh) {
  _box.setFromObject(mesh);
  _box.getSize(_size);
  return { w: Math.max(_size.x, _size.z), h: _size.y };
}

export function artNormal(mesh, walls = null, target = new THREE.Vector3()) {
  if (mesh.userData.facing) return target.copy(mesh.userData.facing);
  const attr = mesh.geometry && mesh.geometry.attributes && mesh.geometry.attributes.normal;
  if (attr) target.fromBufferAttribute(attr, 0);
  else target.set(0, 0, 1);
  target.transformDirection(mesh.matrixWorld);
  target.y = 0;
  if (target.lengthSq() < 1e-6) target.set(0, 0, 1);
  target.normalize();
  if (walls && walls.length) {
    artCenter(mesh, _center);
    _ray.set(_center, target);
    _ray.far = 0.6;
    if (_ray.intersectObjects(walls, false).length) target.negate();
  }
  mesh.userData.facing = target.clone();
  return target;
}

// Where a visitor stands to look at a work: `distance` metres in front of it, eyes at
// eye height above the floor under that spot (falls back to the work's height).
export function viewingSpot(mesh, { walls = null, groundY = null, distance = 2.2, eyeHeight = 1.7 } = {}) {
  const center = artCenter(mesh, new THREE.Vector3());
  const normal = artNormal(mesh, walls, new THREE.Vector3());
  const position = center.clone().addScaledVector(normal, distance);
  const g = groundY ? groundY(position.x, position.z, center.y - eyeHeight, { up: 1.5, down: 3.0 }) : null;
  position.y = g !== null && g !== undefined ? g + eyeHeight : center.y;
  return { position, lookAt: center, normal };
}

// Mean position of the works hanging in a room box (three.js coords), or null.
export function roomArtCentroid(artMeshes, box, floorY = null) {
  const sum = new THREE.Vector3();
  let n = 0;
  for (const m of artMeshes) {
    artCenter(m, _center);
    if (_center.x < box.min.x || _center.x > box.max.x || _center.z < box.min.z || _center.z > box.max.z) continue;
    if (floorY !== null && (_center.y < floorY - 0.5 || _center.y > floorY + 6.5)) continue;
    sum.add(_center);
    n++;
  }
  return n ? sum.divideScalar(n) : null;
}
