import * as THREE from 'three';

// Manifest and layout positions are authored in Blender's Z-up convention
// (x east, y north, z up). The glTF export used export_yup=True, which maps
// Blender (x, y, z) -> three.js (x, z, -y). Every position or direction read
// from the manifest / layout files must go through these helpers.
export function blenderToThree(p) {
  return new THREE.Vector3(p[0], p[2], -p[1]);
}

export function threeToBlender(v) {
  return [v.x, -v.z, v.y];
}

// Yaw (YXZ euler, rotation about +y) that makes the camera look along the
// horizontal three.js direction (dx, dz). At yaw 0 the camera looks down -z.
export function yawToward(dx, dz) {
  return Math.atan2(-dx, -dz);
}

// Blender compass heading in degrees (0 = east/+x, 90 = north/+y) -> yaw.
export function yawFromHeadingDeg(deg) {
  const t = (deg * Math.PI) / 180;
  return yawToward(Math.cos(t), -Math.sin(t));
}
