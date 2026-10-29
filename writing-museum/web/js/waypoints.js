import * as THREE from 'three';
import { blenderToThree } from './coords.js';

const TRAIL_COLOR = 0xd9a839;
const DOOR_IN = 2.0; // m inside a door where a route starts / ends

// BFS over the manifest's room graph (room.connects_to).
export function findPath(roomsById, fromId, toId) {
  if (!roomsById.has(fromId)) fromId = roomsById.keys().next().value;
  if (fromId === toId) return [fromId];
  const visited = new Set([fromId]);
  const queue = [[fromId]];
  while (queue.length) {
    const path = queue.shift();
    const last = path[path.length - 1];
    const room = roomsById.get(last);
    for (const n of (room && room.connects_to) || []) {
      if (n === toId) return [...path, n];
      if (!visited.has(n)) {
        visited.add(n);
        queue.push([...path, n]);
      }
    }
  }
  return [fromId, toId];
}

function doorPoint(room, neighbourId, inward = 0) {
  const d = room && room.doors && room.doors[neighbourId];
  if (!d) return null;
  const p = blenderToThree(d);
  if (inward) {
    // step into the room: away from the wall the door sits in (rooms: doors on the S/E/W walls;
    // hub: doors on the N/S walls). The room centre tells us which way "in" is.
    const c = blenderToThree(room.position);
    const v = new THREE.Vector3(c.x - p.x, 0, c.z - p.z);
    if (room.kind === 'hub') v.set(0, 0, c.z - p.z);
    if (v.lengthSq() > 1e-6) p.addScaledVector(v.normalize(), inward);
  }
  return p;
}

// Every scene is its own coordinate frame, so a route is a list of per-scene segments:
//   [{ scene, roomId, pts: [three.js points], exitDoor: nextRoomId | null }]
// The first segment starts at fromPoint (else the room's spawn), each later one at the door the
// visitor arrives through, and each ends at the door to the next room (or at toPoint).
export function routeSegments(roomsById, roomPath, { fromPoint = null, toPoint = null } = {}) {
  const segs = [];
  for (let i = 0; i < roomPath.length; i++) {
    const room = roomsById.get(roomPath[i]);
    if (!room) continue;
    const prevId = i > 0 ? roomPath[i - 1] : null;
    const nextId = i < roomPath.length - 1 ? roomPath[i + 1] : null;
    const pts = [];
    const push = (v) => { if (v && (!pts.length || pts[pts.length - 1].distanceTo(v) > 0.05)) pts.push(v); };
    if (i === 0 && fromPoint) push(fromPoint.clone());
    else if (prevId) push(doorPoint(room, prevId, DOOR_IN) || blenderToThree(room.spawn || room.position));
    else push(blenderToThree(room.spawn || room.position));
    if (nextId) {
      const exit = doorPoint(room, nextId, DOOR_IN);
      if (room.kind === 'hub' && exit) {
        // walk the hall's centre line between the two doors
        const start = pts[pts.length - 1];
        push(new THREE.Vector3(start.x, start.y, 0));
        push(new THREE.Vector3(exit.x, exit.y, 0));
      }
      push(exit);
      push(doorPoint(room, nextId, 0));
    } else {
      push(toPoint ? toPoint.clone() : blenderToThree(room.position));
    }
    segs.push({ scene: room.scene || room.id, roomId: room.id, pts, exitDoor: nextId });
  }
  return segs;
}

// Backwards-compatible flat point list (used by tests): the current scene's segment only.
export function routePoints(roomsById, roomPath, opts = {}) {
  const segs = routeSegments(roomsById, roomPath, opts);
  return segs.length ? segs[0].pts : [];
}

export function createWaypointTrail(scene, manifest, camera = null, { currentScene = () => null } = {}) {
  const roomsById = new Map(manifest.rooms.map((r) => [r.id, r]));
  let trailMesh = null;
  let target = null; // { toRoomId, toPoint }

  function clear({ keepTarget = false } = {}) {
    if (trailMesh) {
      scene.remove(trailMesh);
      trailMesh.geometry.dispose();
      trailMesh.material.dispose();
      trailMesh = null;
    }
    if (!keepTarget) target = null;
  }

  function drawPoints(pts) {
    if (pts.length < 2) return;
    const curve = new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0.15);
    const segments = Math.max(16, pts.length * 8);
    const tubeGeo = new THREE.TubeGeometry(curve, segments, 0.09, 8, false);
    const mat = new THREE.MeshBasicMaterial({ color: TRAIL_COLOR, transparent: true, opacity: 0.85, depthWrite: false });
    trailMesh = new THREE.Mesh(tubeGeo, mat);
    trailMesh.renderOrder = 10;
    trailMesh.name = 'trail';
    scene.add(trailMesh);
  }

  function segmentsTo(fromRoomId, toRoomId, fromPoint = null, toPoint = null) {
    const roomPath = findPath(roomsById, fromRoomId, toRoomId);
    let start = fromPoint || (camera ? camera.position : null);
    if (start) {
      const feet = camera ? camera.position.y - 1.7 : start.y;
      start = new THREE.Vector3(start.x, feet + 0.05, start.z);
    }
    return routeSegments(roomsById, roomPath, { fromPoint: start, toPoint });
  }

  function showPathTo(fromRoomId, toRoomId, fromPoint = null, toPoint = null) {
    clear();
    target = { toRoomId, toPoint: toPoint ? toPoint.clone() : null };
    const segs = segmentsTo(fromRoomId, toRoomId, fromPoint, toPoint);
    const cur = currentScene();
    const seg = segs.find((s) => s.scene === cur) || segs[0];
    if (seg) drawPoints(seg.pts.map((p) => new THREE.Vector3(p.x, p.y, p.z)));
  }

  // After a scene switch: redraw the remaining route from where the visitor now stands.
  function refresh() {
    if (!target) return;
    const cur = currentScene();
    if (!cur) return;
    const fromRoom = cur;
    if (trailMesh) { scene.remove(trailMesh); trailMesh.geometry.dispose(); trailMesh.material.dispose(); trailMesh = null; }
    if (fromRoom === target.toRoomId && !target.toPoint) { target = null; return; }
    const segs = segmentsTo(fromRoom, target.toRoomId, null, target.toPoint);
    const seg = segs.find((s) => s.scene === cur) || segs[0];
    if (seg) drawPoints(seg.pts);
  }

  function update() {
    if (trailMesh) {
      const pulse = 0.5 + 0.5 * Math.sin(performance.now() * 0.004);
      trailMesh.material.opacity = 0.55 + 0.35 * pulse;
    }
  }

  return { showPathTo, clear, refresh, update, segmentsTo, hasTrail: () => trailMesh !== null, target: () => target,
    findPath: (a, b) => findPath(roomsById, a, b) };
}
