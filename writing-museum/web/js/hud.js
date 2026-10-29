// Floor-plan minimap and the large map (M) for the current scene: rooms come from the geometry
// (lights.js collectRooms boxes), doors from the DOOR- meshes (labelled in the hub), art dots
// from the ART meshes. Clicking a door on the large map enters that room; clicking a room
// teleports inside the current scene.
import * as THREE from 'three';
import { blenderToThree, yawToward } from './coords.js';
import { artCenter, roomArtCentroid } from './artgeom.js';

export function createHud({ camera, rooms, roomsById, manifest, artMeshes, controls, lights = null, onTeleport = null, onDoor = null, redrawHz = 10 }) {
  let roomList = [...rooms.values()];
  let artPts = artMeshes.map((m) => artCenter(m, new THREE.Vector3()));
  let doors = [];
  let sceneId = null;
  let sceneRec = null;
  const fadeEl = document.getElementById('fade');

  // ---- DOM ----------------------------------------------------------------------------
  const mini = document.createElement('canvas');
  mini.id = 'minimap';
  mini.width = 440; mini.height = 440; // 2x for crisp lines at 220 css px
  mini.title = 'Floor plan (M for the full map)';
  const large = document.createElement('div');
  large.id = 'map-large';
  const largeCanvas = document.createElement('canvas');
  const caption = document.createElement('div');
  caption.className = 'map-caption';
  caption.textContent = 'Floor plan · click a door to go through it, a room to go there · M / Esc to close';
  large.appendChild(largeCanvas);
  large.appendChild(caption);
  document.body.appendChild(mini);
  document.body.appendChild(large);

  let mapOpen = false;
  let acc = 0;
  let fadeLevel = 0; // teleport blackout, decayed by update(dt) so it needs no timers or CSS transitions
  let largeView = null; // {ox, oy, scale, level rooms} of the last large draw, for hit-testing

  const feetY = () => camera.position.y - controls.EYE_HEIGHT;
  const levelRooms = (feet) => roomList.filter((r) => feet >= r.floorY - 3 && feet <= r.ceilY - 1);
  const roomName = (r) => {
    const m = roomsById.get(r.manifestId);
    return m ? m.name : r.id;
  };

  function setScene({ rooms: newRooms, doors: newDoors = [], artMeshes: newArt = [], sceneId: id = null, rec = null }) {
    roomList = [...newRooms.values()];
    doors = newDoors;
    artPts = newArt.map((m) => artCenter(m, new THREE.Vector3()));
    sceneId = id;
    sceneRec = rec;
    draw();
  }

  function heading() {
    const { yaw } = controls.getLook();
    return { hx: -Math.sin(yaw), hy: Math.cos(yaw) }; // Blender x/y components of the view direction
  }

  function wrapText(ctx, text, w) {
    const words = String(text).split(/\s+/);
    const lines = [];
    let cur = '';
    for (const word of words) {
      const t = cur ? `${cur} ${word}` : word;
      if (ctx.measureText(t).width <= w || !cur) cur = t;
      else { lines.push(cur); cur = word; }
    }
    if (cur) lines.push(cur);
    return lines;
  }

  // Draw the scene's plan. `view` = {cx, cy (Blender centre), scale (px/m), W, H, labels}
  function drawPlan(ctx, view, current) {
    const { W, H, scale } = view;
    const sx = (bx) => W / 2 + (bx - view.cx) * scale;
    const sy = (by) => H / 2 - (by - view.cy) * scale;
    const feet = feetY();
    ctx.clearRect(0, 0, W, H);
    ctx.lineWidth = Math.max(1, scale * 0.12);
    for (const r of levelRooms(feet)) {
      const x0 = sx(r.box.min.x), x1 = sx(r.box.max.x);
      const y0 = sy(-r.box.min.z), y1 = sy(-r.box.max.z); // Blender y = -three z
      const isCur = current && r.id === current.id;
      ctx.fillStyle = isCur ? 'rgba(202, 162, 77, 0.28)' : 'rgba(242, 234, 217, 0.10)';
      ctx.strokeStyle = isCur ? '#caa24d' : 'rgba(202, 162, 77, 0.55)';
      ctx.beginPath();
      ctx.rect(Math.min(x0, x1), Math.min(y0, y1), Math.abs(x1 - x0), Math.abs(y1 - y0));
      ctx.fill();
      ctx.stroke();
      if (view.labels && sceneId !== 'hub') {
        ctx.fillStyle = isCur ? '#f2ead9' : '#b9ac8f';
        ctx.font = `${Math.max(10, Math.min(16, scale * 1.6))}px Georgia, serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const name = roomName(r);
        const w = Math.abs(x1 - x0) - 6;
        const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
        const lines = wrapText(ctx, name, w);
        const lh = Math.max(11, Math.min(17, scale * 1.7));
        if (lines.length <= 3) lines.forEach((l, i) => ctx.fillText(l, cx, cy + (i - (lines.length - 1) / 2) * lh));
      }
    }
    // doors of this scene (from the DOOR- meshes), labelled on the large map
    const s = Math.max(3, scale * 1.1);
    for (const d of doors) {
      const c = d.userData.center;
      if (!c) continue;
      const px = sx(c.x), py = sy(-c.z);
      ctx.fillStyle = '#e0b95e';
      ctx.fillRect(px - s / 2, py - s / 2, s, s);
      if (view.labels) {
        const f = d.userData.facing || new THREE.Vector3(0, 0, -1);
        const label = d.userData.name || d.userData.target;
        ctx.fillStyle = '#f2ead9';
        ctx.font = `${Math.max(10, Math.min(13, scale * 1.4))}px Georgia, serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = f.z > 0.5 ? 'top' : f.z < -0.5 ? 'bottom' : 'middle';
        const off = s * 0.8 + 4;
        const lx = px - f.x * off * 0; // labels sit inside the scene, on the far side of the wall from the player
        const ly = py + (f.z > 0.5 ? -off : f.z < -0.5 ? off : 0);
        const lines = wrapText(ctx, label, Math.max(60, scale * 7));
        lines.slice(0, 2).forEach((l, i) => ctx.fillText(l, lx, ly + (f.z > 0.5 ? -1 : 1) * (i * 12) * (f.z > 0.5 ? -1 : 1) - (f.z < -0.5 ? (lines.length - 1 - i) * 12 : -i * 12) + (f.z < -0.5 ? 0 : 0)));
      }
    }
    // art dots
    ctx.fillStyle = 'rgba(242, 234, 217, 0.85)';
    const dot = Math.max(1, scale * 0.25);
    for (const p of artPts) {
      if (Math.abs(p.y - (feet + 1.5)) > 3.5) continue;
      ctx.fillRect(sx(p.x) - dot / 2, sy(-p.z) - dot / 2, dot, dot);
    }
    // player
    const { hx, hy } = heading();
    const px = sx(camera.position.x), py = sy(-camera.position.z);
    const len = Math.max(6, scale * 1.6);
    ctx.fillStyle = '#ffd27a';
    ctx.strokeStyle = '#1b1712';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(px + hx * len, py - hy * len);
    ctx.lineTo(px - hy * len * 0.5 - hx * len * 0.6, py - hx * len * 0.5 + hy * len * 0.6);
    ctx.lineTo(px + hy * len * 0.5 - hx * len * 0.6, py + hx * len * 0.5 + hy * len * 0.6);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
  }

  function currentGeoRoom() {
    const feet = feetY();
    let best = null;
    for (const r of roomList) {
      const b = r.box;
      if (camera.position.x < b.min.x - 0.3 || camera.position.x > b.max.x + 0.3 || camera.position.z < b.min.z - 0.3 || camera.position.z > b.max.z + 0.3) continue;
      if (r.floorY > feet + 0.8 || feet > r.ceilY) continue;
      if (!best || r.floorY > best.floorY + 0.01 || (Math.abs(r.floorY - best.floorY) < 0.01 && r.area < best.area)) best = r;
    }
    return best;
  }

  function drawMini() {
    const ctx = mini.getContext('2d');
    const W = mini.width, H = mini.height;
    drawPlan(ctx, { W, H, scale: W / 60, cx: camera.position.x, cy: -camera.position.z, labels: false }, currentGeoRoom());
  }

  function drawLarge() {
    const level = levelRooms(feetY());
    if (!level.length) return;
    const box = new THREE.Box3();
    for (const r of level) box.union(r.box);
    const spanX = box.max.x - box.min.x + 10;
    const spanY = box.max.z - box.min.z + 10;
    const maxW = Math.floor(window.innerWidth * 0.86), maxH = Math.floor(window.innerHeight * 0.8);
    const scale = Math.min(maxW / spanX, maxH / spanY);
    const W = Math.max(200, Math.round(spanX * scale)), H = Math.max(200, Math.round(spanY * scale));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    largeCanvas.width = W * dpr; largeCanvas.height = H * dpr;
    largeCanvas.style.width = `${W}px`; largeCanvas.style.height = `${H}px`;
    const ctx = largeCanvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const view = { W, H, scale, cx: (box.min.x + box.max.x) / 2, cy: -(box.min.z + box.max.z) / 2, labels: true };
    drawPlan(ctx, view, currentGeoRoom());
    largeView = { ...view, level };
  }

  function draw() {
    drawMini();
    if (mapOpen) drawLarge();
  }

  function applyFade() {
    if (fadeEl) fadeEl.style.opacity = fadeLevel > 0.001 ? String(fadeLevel) : '0';
  }
  function fade() {
    fadeLevel = 1;
    applyFade();
  }
  function update(dt) {
    if (fadeLevel > 0) {
      fadeLevel = Math.max(0, fadeLevel - dt / 0.45);
      applyFade();
    }
    acc += dt;
    if (acc < 1 / redrawHz) return;
    acc = 0;
    draw();
  }

  function findGeoRoomAt(pos) {
    const feet = pos.y - controls.EYE_HEIGHT;
    let best = null;
    for (const r of roomList) {
      const b = r.box;
      if (pos.x < b.min.x - 0.3 || pos.x > b.max.x + 0.3 || pos.z < b.min.z - 0.3 || pos.z > b.max.z + 0.3) continue;
      if (Math.abs(r.floorY - feet) > 1.5) continue;
      if (!best || r.area < best.area) best = r;
    }
    return best;
  }

  // Teleport inside the current scene: a manifest room (spawn ?? position) or a geometry room (box centre).
  function teleportToRoom(id) {
    const man = roomsById.get(id);
    let pos;
    if (man && (man.scene === sceneId || !man.scene)) {
      pos = blenderToThree(man.spawn || man.position);
      pos.y += controls.EYE_HEIGHT;
    } else {
      const g = roomList.find((r) => r.id === id);
      if (!g) return false;
      pos = new THREE.Vector3(g.center.x, g.floorY + controls.EYE_HEIGHT, g.center.z);
    }
    const g = findGeoRoomAt(pos);
    const centroid = g ? roomArtCentroid(artMeshes, g.box, g.floorY) : null;
    fade();
    if (centroid && centroid.distanceTo(pos) > 1.5) {
      controls.teleport(pos, { lookAt: new THREE.Vector3(centroid.x, pos.y, centroid.z) });
    } else {
      controls.teleport(pos, { yaw: yawToward(0, -1) });
    }
    if (lights) lights.update(camera, 0, true);
    if (onTeleport) onTeleport(id);
    draw();
    return true;
  }

  // What is under a large-map click: {kind: 'door', id} within 1.6 m of a door, else {kind: 'room', id}.
  function hitAtScreen(clientX, clientY) {
    if (!largeView) return null;
    const rect = largeCanvas.getBoundingClientRect();
    const x = clientX - rect.left, y = clientY - rect.top;
    const bx = largeView.cx + (x - largeView.W / 2) / largeView.scale;
    const by = largeView.cy - (y - largeView.H / 2) / largeView.scale;
    let bestDoor = null, bd = 1.6;
    for (const d of doors) {
      const c = d.userData.center;
      if (!c) continue;
      const dist = Math.hypot(bx - c.x, by - (-c.z));
      if (dist < bd) { bd = dist; bestDoor = d; }
    }
    if (bestDoor) return { kind: 'door', id: bestDoor.userData.target, mesh: bestDoor };
    let best = null;
    for (const r of largeView.level) {
      if (bx < r.box.min.x || bx > r.box.max.x || -by < r.box.min.z || -by > r.box.max.z) continue;
      if (!best || r.area < best.area) best = r;
    }
    return best ? { kind: 'room', id: roomsById.has(best.manifestId) ? best.manifestId : best.id, room: best } : null;
  }
  function roomAtScreen(clientX, clientY) {
    const h = hitAtScreen(clientX, clientY);
    return h && h.kind === 'room' ? h.room : null;
  }

  function openMap() {
    mapOpen = true;
    large.classList.add('open');
    drawLarge();
    // the map is clicked with a free cursor: release a captured mouse (pointer-locked clicks never reach it)
    if (document.pointerLockElement && document.exitPointerLock) document.exitPointerLock();
  }
  function closeMap() { mapOpen = false; large.classList.remove('open'); }
  function toggleMap() { if (mapOpen) closeMap(); else openMap(); }
  function isMapOpen() { return mapOpen; }

  mini.addEventListener('click', (e) => { e.stopPropagation(); toggleMap(); });
  largeCanvas.addEventListener('click', (e) => {
    e.stopPropagation();
    const h = hitAtScreen(e.clientX, e.clientY);
    if (!h) return;
    closeMap();
    if (h.kind === 'door') { if (onDoor) onDoor(h.id, h.mesh); return; }
    teleportToRoom(h.id);
  });
  large.addEventListener('click', (e) => { if (e.target === large) closeMap(); });

  function setArtMeshes(list) { artPts = list.map((m) => artCenter(m, new THREE.Vector3())); }

  draw();
  return { update, draw, toggleMap, openMap, closeMap, isMapOpen, teleportToRoom, setArtMeshes, setScene, roomAtScreen, hitAtScreen, currentGeoRoom, fade,
    get sceneId() { return sceneId; }, get doors() { return doors; } };
}
