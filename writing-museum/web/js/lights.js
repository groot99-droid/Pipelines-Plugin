// Light pool for the museum viewer (contract §7).
//
// A CONSTANT set of 8 lights lives in the scene for the whole session, so three.js never has to
// recompile shaders for a different light count, and castShadow is never toggled at runtime:
//   1  HemisphereLight           warm fill (no shadows)
//   1  DirectionalLight 'sun'    castShadow; re-fitted to the active room. Modes:
//                                  sun      FX sun of the room, from far outside (windows let it in)
//                                  oculus   FX oculus of the room, from just above the dome
//                                  laylight FX laylight of the room / fallback 'wash': straight down from
//                                           just under the ceiling, so only things inside the room shade
//   1  PointLight 'chandelier'   castShadow; parked on the nearest chandelier on the same level
//                                (or on the best ordinary fixture when there is none)
//   5  PointLights 'pool'        no shadows; re-parked on the nearest fixtures (distance-based,
//                                same-room bonus, hysteresis, fade out/in, re-evaluated <= 4x per second)
// Fixtures come from FX-* empties in the glTF (userData from Blender custom props, see contract §6).
// When the model has none (v1), a manifest/geometry-based fallback builds anchors from the floor
// meshes: a grid of ceiling lights per room plus a chandelier in the rotunda and the stair hall.
import * as THREE from 'three';

export const LIGHT_DEFAULTS = {
  poolSize: 5,
  reevalInterval: 0.25,      // s  (<= 4 evaluations per second)
  hysteresis: 0.8,           // score multiplier for fixtures that already hold a light
  sameRoomBonus: 0.7,        // score multiplier for fixtures in the camera's room
  pictureLightPenalty: 1.3,  // prefer room lights over picture lights when the pool is short
  levelBelow: 3.0,           // "same level": feet may be up to 3 m below a fixture room's floor ...
  levelAboveCeil: 1.0,       // ... and must be at least 1 m below its ceiling
  fadeIn: 0.35, fadeOut: 0.15,
  // Warm sky / dark-wood ground fill. Kept low: render.js's warm PMREM environment already
  // provides most of the ambient term.
  hemi: { sky: 0xffe0bc, ground: 0x3a2a1c, intensity: 0.2 },
  dirShadowMap: 2048, pointShadowMap: 1024,
  // Per-type gains applied to FX intensities (FX files carry physical units already).
  typeGain: { chandelier: 1, sconce: 1, pendant: 1, picture_light: 1, laylight: 1, sun: 1, oculus: 1, wash: 1, ceiling: 1 },
  // Fallback fixtures (model without FX-* empties).
  fallback: {
    spacing: 7.0,            // m between ceiling lights
    height: 4.6,             // m above the room floor (lower than the ceiling so it does not hot-spot)
    tallHeight: 5.2,         // ... in rooms taller than 9 m (stair hall)
    wallClearance: 2.8,      // m from the room box edge
    color: '#ffc890', intensity: 21, distance: 14,
    chandelierColor: '#ffc080', chandelierIntensity: 60, chandelierDistance: 18,
    chandelierHeight: 3.6, chandelierTallHeight: 9.5, // m above the room floor
    washColor: '#ffe9cf', washIntensity: 0.8,
  },
};

const EYE_HEIGHT = 1.7;
const POINT_TYPES = new Set(['chandelier', 'sconce', 'pendant', 'picture_light']);
const DIR_TYPES = new Set(['sun', 'oculus', 'laylight']);

// geometry room id (from GEO-<room>_floor) -> manifest room id
function manifestIdFor(roomId) {
  return roomId; // geo room ids (GEO-<id>_floor) are the manifest room ids
}

function ownerName(obj) {
  const n = obj.name || '';
  if (/^(GEO|ART|FX)-/.test(n)) return n;
  const p = obj.parent && obj.parent.name ? obj.parent.name : '';
  return /^(GEO|ART|FX)-/.test(p) ? p : n;
}

// Rooms from the floor / ceiling meshes of the model (works for v1 and v2 names).
export function collectRooms(root) {
  const rooms = new Map();
  const box = new THREE.Box3();
  const ceilings = new Map();
  root.updateMatrixWorld(true);
  root.traverse((obj) => {
    if (!obj.isMesh) return;
    const name = ownerName(obj);
    let m = /^GEO-(.+?)_floor/.exec(name);
    if (m) {
      box.setFromObject(obj);
      const id = m[1];
      const r = rooms.get(id);
      if (r) r.box.union(box);
      else rooms.set(id, { id, manifestId: manifestIdFor(id), box: box.clone() });
      return;
    }
    m = /^GEO-(.+?)_ceiling/.exec(name);
    if (m) {
      box.setFromObject(obj);
      const prev = ceilings.get(m[1]);
      ceilings.set(m[1], prev === undefined ? box.min.y : Math.min(prev, box.min.y));
    }
  });
  for (const r of rooms.values()) {
    r.floorY = r.box.max.y;
    const c = ceilings.get(r.id);
    r.ceilY = c !== undefined && c > r.floorY + 2 ? c : r.floorY + 6.9;
    r.center = new THREE.Vector3((r.box.min.x + r.box.max.x) / 2, r.floorY, (r.box.min.z + r.box.max.z) / 2);
    r.sizeX = r.box.max.x - r.box.min.x;
    r.sizeZ = r.box.max.z - r.box.min.z;
    r.area = r.sizeX * r.sizeZ;
  }
  return rooms;
}

export function makeRoomAt(rooms) {
  const list = [...rooms.values()];
  return function roomAt(pos, eyeHeight = EYE_HEIGHT) {
    const feet = pos.y - eyeHeight;
    let best = null;
    for (const r of list) {
      const b = r.box;
      if (pos.x < b.min.x - 0.3 || pos.x > b.max.x + 0.3 || pos.z < b.min.z - 0.3 || pos.z > b.max.z + 0.3) continue;
      if (r.floorY > feet + 0.8 || feet > r.ceilY) continue;
      if (!best || r.floorY > best.floorY + 0.01 || (Math.abs(r.floorY - best.floorY) < 0.01 && r.area < best.area)) best = r;
    }
    return best;
  };
}

function colorOf(v, fallback) {
  try {
    if (typeof v === 'string' && v) return new THREE.Color(v);
    if (Array.isArray(v) && v.length >= 3) return new THREE.Color(v[0], v[1], v[2]);
  } catch (e) { /* fall through */ }
  return new THREE.Color(fallback);
}

function collectFx(root, rooms, roomAt) {
  const out = [];
  const tmp = new THREE.Vector3();
  root.updateMatrixWorld(true);
  root.traverse((obj) => {
    const u = obj.userData || {};
    const isFxName = (obj.name || '').startsWith('FX-');
    if (!u.fx_type) {
      if (isFxName) console.warn('[museum] FX empty without fx_type ignored:', obj.name);
      return;
    }
    obj.getWorldPosition(tmp);
    let dir = null;
    if (Array.isArray(u.fx_dir_three) && u.fx_dir_three.length === 3) {
      dir = new THREE.Vector3().fromArray(u.fx_dir_three.map(Number));
      if (dir.lengthSq() > 1e-8) {
        dir.normalize();
        // Direction of travel. A sun/spot must travel downward: if an exporter stored the
        // "toward the light" vector instead, flip it.
        if (dir.y > 0) dir.negate();
      } else dir = null;
    }
    const room = (u.fx_room && rooms.get(u.fx_room)) || roomAt(tmp, 0) || null;
    out.push({
      name: obj.name || `FX-${u.fx_type}`,
      type: String(u.fx_type),
      pos: tmp.clone(),
      color: colorOf(u.fx_color, '#ffe0b0'),
      intensity: Number(u.fx_intensity) || 0,
      distance: Number(u.fx_distance) || 0,
      shadow: Number(u.fx_shadow) || 0,
      room: room ? room.id : (u.fx_room || null),
      roomRef: room,
      dir,
      size: Array.isArray(u.fx_size) ? u.fx_size.map(Number) : null,
      source: 'fx',
    });
  });
  return out;
}

function fallbackAnchors(rooms) {
  const F = LIGHT_DEFAULTS.fallback;
  const out = [];
  // keep grid lights this far from the room's walls (closer ones paint hot spots on the plaster)
  const clampIn = (v, lo, hi) => (hi - lo < 2 * F.wallClearance ? (lo + hi) / 2
    : Math.min(hi - F.wallClearance, Math.max(lo + F.wallClearance, v)));
  for (const r of rooms.values()) {
    const round = r.id === 'rotunda'; // lit by its chandelier only: a grid would hot-spot the drum
    const nx = round ? 0 : Math.max(1, Math.round(r.sizeX / F.spacing));
    const nz = Math.max(1, Math.round(r.sizeZ / F.spacing));
    const tall = r.ceilY - r.floorY > 9;
    const y = r.floorY + Math.min(tall ? F.tallHeight : F.height, r.ceilY - r.floorY - 0.5);
    let k = 0;
    for (let i = 0; i < nx; i++) {
      for (let j = 0; j < nz; j++) {
        const x = clampIn(r.box.min.x + (i + 0.5) * (r.sizeX / nx), r.box.min.x, r.box.max.x);
        const z = clampIn(r.box.min.z + (j + 0.5) * (r.sizeZ / nz), r.box.min.z, r.box.max.z);
        out.push({
          name: `fallback-${r.id}_ceiling_${k++}`, type: 'ceiling', pos: new THREE.Vector3(x, y, z),
          color: new THREE.Color(F.color), intensity: F.intensity, distance: F.distance, shadow: 0,
          room: r.id, roomRef: r, dir: null, size: null, source: 'fallback',
        });
      }
    }
    if (round || tall) {
      const cy = r.floorY + (tall ? F.chandelierTallHeight : F.chandelierHeight);
      out.push({
        name: `fallback-${r.id}_chandelier_0`, type: 'chandelier', pos: new THREE.Vector3(r.center.x, cy, r.center.z),
        color: new THREE.Color(F.chandelierColor), intensity: F.chandelierIntensity, distance: F.chandelierDistance,
        shadow: 1, room: r.id, roomRef: r, dir: null, size: null, source: 'fallback',
      });
    }
  }
  return out;
}

export function createLightRig(scene, renderer, { eyeHeight = EYE_HEIGHT, lightGain = 1, root = null, rooms: roomsIn = null } = {}) {
  const D = LIGHT_DEFAULTS;
  // World-dependent state, replaced by setWorld() on every scene switch.
  let rooms = new Map();
  let roomAt = makeRoomAt(rooms);
  let fx = [];
  let pointFx = [];
  let dirFx = [];
  let mode = 'fallback';
  let pointAnchors = [];
  const gains = { global: lightGain, type: { ...D.typeGain } };

  // ---- the constant light set ------------------------------------------------------------
  const hemi = new THREE.HemisphereLight(D.hemi.sky, D.hemi.ground, D.hemi.intensity);
  hemi.name = 'pool-hemi';
  scene.add(hemi);

  const sun = new THREE.DirectionalLight(0xffffff, 0);
  sun.name = 'pool-sun';
  sun.castShadow = true;
  sun.shadow.mapSize.set(D.dirShadowMap, D.dirShadowMap);
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.03;
  scene.add(sun);
  scene.add(sun.target);

  function makePoint(name, castShadow) {
    const l = new THREE.PointLight(0xffffff, 0, 0, 2);
    l.name = name;
    l.castShadow = castShadow;
    if (castShadow) {
      l.shadow.mapSize.set(D.pointShadowMap, D.pointShadowMap);
      l.shadow.bias = -0.002;
      l.shadow.normalBias = 0.04;
      l.shadow.camera.near = 0.1;
      l.shadow.camera.far = 30;
    }
    l.position.set(0, -1000, 0);
    l.userData.slot = { anchor: null, next: null, level: 0 };
    scene.add(l);
    return l;
  }
  const chandelier = makePoint('pool-chandelier', true);
  const pool = [];
  for (let i = 0; i < D.poolSize; i++) pool.push(makePoint(`pool-point-${i}`, false));
  const all = [hemi, sun, chandelier, ...pool];

  // ---- evaluation ------------------------------------------------------------------------
  let sinceEval = Infinity;
  let currentRoom = null;
  const sunState = { key: null, mode: 'off', room: null, target: 0, level: 0, color: new THREE.Color(1, 1, 1), anchor: null, pending: null };

  function resetSlots() {
    for (const l of [chandelier, ...pool]) {
      const slot = l.userData.slot;
      slot.anchor = null; slot.next = null; slot.level = 0;
      placePoint(l, null);
      l.intensity = 0;
    }
    sunState.key = null; sunState.mode = 'off'; sunState.room = null; sunState.target = 0; sunState.level = 0;
    sunState.anchor = null; sunState.pending = null;
    sun.intensity = 0;
    currentRoom = null;
    sinceEval = Infinity;
  }

  // Re-anchor the constant light set on a new world root (rooms from its floor meshes, fixtures
  // from its FX-* empties, else the fallback grid). The lights themselves are never recreated.
  function setWorld({ root: newRoot, rooms: newRooms = null } = {}) {
    rooms = newRooms || (newRoot ? collectRooms(newRoot) : new Map());
    roomAt = makeRoomAt(rooms);
    fx = newRoot ? collectFx(newRoot, rooms, roomAt) : [];
    pointFx = fx.filter((a) => POINT_TYPES.has(a.type));
    dirFx = fx.filter((a) => DIR_TYPES.has(a.type));
    mode = pointFx.length || dirFx.length ? 'fx' : 'fallback';
    pointAnchors = mode === 'fx' ? pointFx : fallbackAnchors(rooms);
    for (const a of pointAnchors) {
      const r = a.roomRef;
      a.floorY = r ? r.floorY : (a.pos.y >= 7 ? 7.1 : 0.1);
      a.ceilY = r ? r.ceilY : a.floorY + 6.9;
    }
    resetSlots();
  }

  function levelOk(a, feet) {
    return feet >= a.floorY - D.levelBelow && feet <= a.ceilY - D.levelAboveCeil;
  }

  function score(a, cam, holder) {
    let s = a.pos.distanceTo(cam);
    if (currentRoom && a.room === currentRoom.id) s *= D.sameRoomBonus;
    if (a.type === 'picture_light') s *= D.pictureLightPenalty;
    if (holder) s *= D.hysteresis;
    return s;
  }

  function assign(light, anchor, instant) {
    const slot = light.userData.slot;
    slot.next = anchor;
    if (instant) {
      slot.anchor = anchor;
      slot.level = anchor ? 1 : 0;
      placePoint(light, anchor);
    }
  }

  function placePoint(light, a) {
    if (!a) { light.position.set(0, -1000, 0); return; }
    light.position.copy(a.pos);
    light.color.copy(a.color);
    light.distance = a.distance || 0;
    if (light.castShadow) {
      light.shadow.camera.far = Math.max(8, a.distance || 30);
      light.shadow.camera.updateProjectionMatrix();
      renderer.shadowMap.needsUpdate = true;
    }
  }

  function evaluatePoints(cam, instant) {
    const feet = cam.y - eyeHeight;
    const holders = new Set([chandelier, ...pool].map((l) => l.userData.slot.next).filter(Boolean));
    const cands = [];
    for (const a of pointAnchors) {
      if (!levelOk(a, feet)) continue;
      cands.push({ a, s: score(a, cam, holders.has(a)) });
    }
    cands.sort((p, q) => p.s - q.s);

    // chandelier slot: nearest chandelier (same level), else the best fixture overall
    let chand = cands.find((c) => c.a.type === 'chandelier');
    if (!chand && cands.length) chand = cands[0];
    const chandAnchor = chand ? chand.a : null;
    const wanted = cands.filter((c) => c.a !== chandAnchor).slice(0, pool.length).map((c) => c.a);

    if (chandelier.userData.slot.next !== chandAnchor) assign(chandelier, chandAnchor, instant);

    // keep pool lights that already hold a wanted anchor; re-park the others
    const keep = new Set();
    for (const l of pool) {
      const n = l.userData.slot.next;
      if (n && wanted.includes(n) && !keep.has(n)) keep.add(n);
      else if (n) assign(l, null, instant);
    }
    const free = pool.filter((l) => !l.userData.slot.next);
    for (const a of wanted) {
      if (keep.has(a)) continue;
      const l = free.shift();
      if (!l) break;
      assign(l, a, instant);
    }
  }

  function chooseSun() {
    const r = currentRoom;
    if (!r) return null;
    if (mode === 'fx') {
      const inRoom = dirFx.filter((a) => a.room === r.id);
      const pick = inRoom.find((a) => a.type === 'sun') || inRoom.find((a) => a.type === 'oculus') || inRoom.find((a) => a.type === 'laylight');
      if (pick) return { key: `${pick.name}`, mode: pick.type, room: r, anchor: pick };
    }
    // wash: a soft top light for the room, straight down from just under its ceiling
    const F = LIGHT_DEFAULTS.fallback;
    return {
      key: `wash:${r.id}`, mode: 'wash', room: r,
      anchor: { name: `wash-${r.id}`, type: 'wash', color: new THREE.Color(F.washColor), intensity: mode === 'fx' ? F.washIntensity * 0.6 : F.washIntensity, dir: null },
    };
  }

  const _m = new THREE.Matrix4();
  const _v = new THREE.Vector3();
  const _up = new THREE.Vector3();
  function fitSun(choice) {
    const r = choice.room;
    const a = choice.anchor;
    let dir;
    if (choice.mode === 'wash' || choice.mode === 'laylight') dir = new THREE.Vector3(0, -1, 0);
    else if (a.dir) dir = a.dir.clone();
    else if (choice.mode === 'oculus') dir = new THREE.Vector3(0.18, -1, 0.1).normalize();
    else dir = new THREE.Vector3(-0.6, -0.21, 0.77).normalize(); // golden-hour default, ~12 deg elevation

    const target = r.center.clone();
    let topY;
    let margin = 1.0;
    if (choice.mode === 'wash') topY = r.ceilY - 0.06;
    else if (choice.mode === 'laylight') topY = Math.min(r.ceilY, a.pos ? a.pos.y : r.ceilY) - 0.06;
    else if (choice.mode === 'oculus') { topY = (a.pos ? a.pos.y : r.ceilY) + 1.5; margin = 2.0; }
    else { topY = r.ceilY + 12; margin = 5.0; }
    const t = (topY - target.y) / Math.max(0.05, -dir.y);
    const pos = target.clone().addScaledVector(dir, -t);
    sun.position.copy(pos);
    sun.target.position.copy(target);
    sun.updateMatrixWorld();
    sun.target.updateMatrixWorld();

    _up.set(0, 1, 0);
    if (Math.abs(dir.y) > 0.95) _up.set(0, 0, -1);
    sun.shadow.camera.up.copy(_up);
    _m.lookAt(pos, target, _up); // rotation only: columns are camera x, y, z(=backwards) axes
    const xs = new THREE.Vector3().setFromMatrixColumn(_m, 0);
    const ys = new THREE.Vector3().setFromMatrixColumn(_m, 1);
    const zs = new THREE.Vector3().setFromMatrixColumn(_m, 2);
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity, maxD = 0;
    const b = r.box;
    for (const cx of [b.min.x - margin, b.max.x + margin]) {
      for (const cy of [r.floorY - 0.3, r.ceilY]) {
        for (const cz of [b.min.z - margin, b.max.z + margin]) {
          _v.set(cx, cy, cz).sub(pos);
          const px = _v.dot(xs), py = _v.dot(ys), d = -_v.dot(zs);
          minX = Math.min(minX, px); maxX = Math.max(maxX, px);
          minY = Math.min(minY, py); maxY = Math.max(maxY, py);
          maxD = Math.max(maxD, d);
        }
      }
    }
    const cam = sun.shadow.camera;
    cam.left = minX; cam.right = maxX; cam.bottom = minY; cam.top = maxY;
    cam.near = choice.mode === 'wash' || choice.mode === 'laylight' ? 0.01 : 0.5;
    cam.far = maxD + 1;
    cam.updateProjectionMatrix();
    renderer.shadowMap.needsUpdate = true;

    sunState.color.copy(a.color);
    sunState.target = a.intensity;
  }

  function evaluateSun(instant) {
    const choice = chooseSun();
    if (!choice) return;
    if (choice.key === sunState.key) return;
    const firstTime = sunState.key === null;
    sunState.pending = choice;
    if (instant || firstTime) applySun();
  }

  function applySun() {
    const c = sunState.pending;
    sunState.pending = null;
    if (!c) return;
    sunState.key = c.key;
    sunState.mode = c.mode;
    sunState.room = c.room.id;
    sunState.anchor = c.anchor;
    fitSun(c);
    sunState.level = sunState.level || 0;
  }

  function update(camera, delta = 0, force = false) {
    sinceEval += delta;
    const cam = camera.position;
    if (force || sinceEval >= D.reevalInterval) {
      sinceEval = 0;
      const r = roomAt(cam, eyeHeight);
      if (r) currentRoom = r;
      evaluatePoints(cam, force);
      evaluateSun(force);
    }

    // point-light fades
    for (const l of [chandelier, ...pool]) {
      const slot = l.userData.slot;
      if (slot.next !== slot.anchor) {
        slot.level = force ? 0 : slot.level - delta / D.fadeOut;
        if (slot.level <= 0) {
          slot.level = 0;
          slot.anchor = slot.next;
          placePoint(l, slot.anchor);
          if (force && slot.anchor) slot.level = 1;
        }
      } else if (slot.anchor) {
        slot.level = force ? 1 : Math.min(1, slot.level + delta / D.fadeIn);
      }
      const a = slot.anchor;
      l.intensity = a ? a.intensity * (gains.type[a.type] ?? 1) * gains.global * slot.level : 0;
    }

    // sun: cross-fade through zero when the room/mode changes
    if (sunState.pending) {
      sunState.level = force ? 0 : sunState.level - delta / 0.25;
      if (sunState.level <= 0) { sunState.level = 0; applySun(); }
    } else {
      sunState.level = force ? 1 : Math.min(1, sunState.level + delta / 0.4);
    }
    const sa = sunState.anchor;
    sun.color.copy(sunState.color);
    sun.intensity = sa ? sunState.target * (gains.type[sa.type] ?? 1) * gains.global * sunState.level : 0;
  }

  function setGain(g) { gains.global = g; }
  function setTypeGain(type, g) { gains.type[type] = g; }
  function setHemi(intensity) { hemi.intensity = intensity; }

  function state() {
    const s = (l) => (l.userData.slot.anchor ? l.userData.slot.anchor.name : null);
    return {
      mode,
      rooms: rooms.size,
      fixtures: pointAnchors.length,
      dirFixtures: dirFx.length,
      room: currentRoom ? currentRoom.id : null,
      sun: { mode: sunState.mode, room: sunState.room, intensity: +sun.intensity.toFixed(3) },
      chandelier: s(chandelier),
      pool: pool.map(s),
      count: all.length,
    };
  }

  if (root || roomsIn) setWorld({ root, rooms: roomsIn });

  return {
    hemi, sun, chandelier, pool, all, gains, update, state, setGain, setTypeGain, setHemi, setWorld,
    get mode() { return mode; },
    get rooms() { return rooms; },
    get fx() { return fx; },
    get anchors() { return pointAnchors; },
    get roomAt() { return roomAt; },
    get currentRoom() { return currentRoom; },
  };
}
