// Builds one scene (the hall or a work's room) from data/museum-layout.json.
//
// Writing Museum: a hang whose manifest work carries `text` is a PASSAGE, drawn into a
// CanvasTexture here (panelTexture) at the typography the builder sized it for
// (build/works.py: PX_PER_M, FONT_PX, LINE_PX, PAD_PX, TITLE_PX); a hang with an image is
// streamed from `thumbUrl` as in the Chronicle Museum.
//
// Everything is authored in Blender Z-up metres (coords.js converts). Meshes are named by the
// viewer's classification contract: `wall`/`outer` collide, `floor`/`landing`/`step` are
// walkable, `GEO-<scene>_floor*` defines the geo room, `ART-` is a clickable work, `DOOR-` a
// clickable door, `SCULPT-` a clickable sculpture, `FX-` empties anchor the light pool.
// Decorative pieces (mouldings, frames, pedestals) are merged per material into a few meshes,
// with world-space UVs so the PBR tiling is continuous.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { blenderToThree } from './coords.js';
import { applyWorldUV } from './matlib.js';
import { buildDoor } from './doors.js';

const UP = new THREE.Vector3(0, 1, 0);
const ART_PROUD = 0.05;         // art plane distance from the wall face
const CONCURRENCY = 4;
const PLACEHOLDER = 0xefe6d2;

// Text panels (shared constants with build/works.py).
const PANEL = { pxPerM: 900, font: 26, line: 36, pad: 70, title: 64, maxPx: 2048,
  paper: '#f3ecdc', ink: '#2b241c', rule: '#8a7a62', serif: 'Georgia, "Times New Roman", serif' };

function wrapText(g, text, maxW) {
  const out = [];
  const paragraphs = String(text).split(/\n\s*\n/);
  paragraphs.forEach((para, pi) => {
    for (const raw of para.split('\n')) {
      const words = raw.split(/\s+/).filter(Boolean);
      if (!words.length) { out.push(''); continue; }
      let cur = '';
      for (const w of words) {
        const t = cur ? `${cur} ${w}` : w;
        if (!cur || g.measureText(t).width <= maxW) cur = t;
        else { out.push(cur); cur = w; }
      }
      out.push(cur);
    }
    if (pi < paragraphs.length - 1) out.push('');
  });
  return out;
}

// A passage as a paper panel: the title band, a rule, the text wrapped to the panel's width and
// shrunk (never below 12 px) until it fits the height the builder gave the panel.
export function panelTexture(work, h, { owned = null, maxAniso = 1 } = {}) {
  const W = Math.min(PANEL.maxPx, Math.max(64, Math.round(h.w * PANEL.pxPerM)));
  const H = Math.min(PANEL.maxPx, Math.max(64, Math.round(h.h * PANEL.pxPerM)));
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const g = c.getContext('2d');
  g.fillStyle = PANEL.paper;
  g.fillRect(0, 0, W, H);
  g.textBaseline = 'top';
  const pad = PANEL.pad, maxW = W - 2 * pad;
  const titleTop = Math.round(pad * 0.55);
  g.fillStyle = PANEL.rule;
  g.font = `600 ${Math.round(PANEL.font * 0.8)}px ${PANEL.serif}`;
  let title = String(work.title || '').toUpperCase();
  while (title && g.measureText(title).width > maxW) title = title.slice(0, -2);
  g.fillText(title, pad, titleTop);
  g.fillRect(pad, titleTop + Math.round(PANEL.font * 1.15), maxW, 2);
  const top = titleTop + PANEL.title;
  const maxH = H - pad - top;
  let font = PANEL.font, line = PANEL.line, lines;
  for (;;) {
    g.font = `${font}px ${PANEL.serif}`;
    lines = wrapText(g, work.text || '', maxW);
    if (lines.length * line <= maxH || font <= 12) break;
    font -= 1;
    line = Math.round(font * 1.38);
  }
  g.fillStyle = PANEL.ink;
  lines.forEach((ln, i) => { if (ln) g.fillText(ln, pad, top + i * line); });
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = maxAniso;
  if (owned) owned.textures.add(tex);
  return tex;
}

// Moulding profiles: closed polylines of [u (out from the wall face), v (height above the floor)].
export const PROFILES = {
  skirting: [[0, 0], [0.035, 0], [0.035, 0.2], [0.025, 0.215], [0.032, 0.245], [0.02, 0.27], [0, 0.28]],
  dado: [[0, 0.9], [0.04, 0.9], [0.055, 0.925], [0.04, 0.975], [0, 0.98]],
  picture_rail: [[0, 5.76], [0.035, 5.76], [0.048, 5.79], [0.03, 5.83], [0, 5.83]],
  cornice: [[0, 6.5], [0.03, 6.5], [0.03, 6.58], [0.08, 6.63], [0.08, 6.7], [0.15, 6.76], [0.17, 6.84], [0.3, 6.93], [0.36, 7.0], [0, 7.0]],
  cornice_hub: [[0, 8.35], [0.04, 8.35], [0.04, 8.46], [0.12, 8.53], [0.12, 8.62], [0.2, 8.7], [0.24, 8.8], [0.42, 8.92], [0.5, 9.0], [0, 9.0]],
};
const PROFILE_TILE = [1.0, 0.5];

// ---------------------------------------------------------------- geometry helpers ------
function boxGeometry(ext) {
  const sx = ext.x[1] - ext.x[0], sy = ext.y[1] - ext.y[0], sz = ext.z[1] - ext.z[0];
  const geo = new THREE.BoxGeometry(sx, sz, sy);
  geo.translate((ext.x[0] + ext.x[1]) / 2, (ext.z[0] + ext.z[1]) / 2, -(ext.y[0] + ext.y[1]) / 2);
  return geo;
}

function latheGeometry(rec) {
  const pts = rec.profile_rz.map(([r, z]) => new THREE.Vector2(r, z));
  const [p0, p1] = rec.phi || [0, 360];
  const geo = new THREE.LatheGeometry(pts, rec.segments || 32, THREE.MathUtils.degToRad(p0 + 90), THREE.MathUtils.degToRad(p1 - p0));
  const c = blenderToThree(rec.center || [0, 0, 0]);
  geo.translate(c.x, c.y, c.z);
  return geo;
}

// Horizontal fan (top face) between two Blender angles.
function discGeometry(rec) {
  const [p0, p1] = rec.phi || [0, 360];
  const seg = rec.segments || 32;
  const c = blenderToThree(rec.center || [0, 0, 0]);
  const y = c.y + (rec.z ? rec.z[1] : 0);
  const r = rec.radius;
  const pos = [];
  const a0 = THREE.MathUtils.degToRad(p0), a1 = THREE.MathUtils.degToRad(p1);
  for (let i = 0; i < seg; i++) {
    const t0 = a0 + (a1 - a0) * (i / seg), t1 = a0 + (a1 - a0) * ((i + 1) / seg);
    pos.push(c.x, y, c.z);
    pos.push(c.x + r * Math.cos(t0), y, c.z - r * Math.sin(t0));
    pos.push(c.x + r * Math.cos(t1), y, c.z - r * Math.sin(t1));
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  const nor = new Float32Array(pos.length);
  for (let i = 0; i < pos.length; i += 3) { nor[i] = 0; nor[i + 1] = 1; nor[i + 2] = 0; }
  geo.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
  return geo;
}

// Sweep a profile along a wall run A->B (Blender points on the wall centre-line, `n` the inward
// normal). Local x = profile u (into the room), y = up, z = along the run; the basis is kept
// right-handed by flipping the run direction when needed. `mitre` = [start, end] inside corners.
function extrudeRun(profile, A, B, n, { wallT = 0.4, mitre = [false, false] } = {}) {
  const a = blenderToThree(A), b = blenderToThree(B);
  const n3 = blenderToThree(n).normalize();
  a.addScaledVector(n3, wallT / 2);
  b.addScaledVector(n3, wallT / 2);
  const d = b.clone().sub(a);
  const len = d.length();
  if (len < 0.05) return null;
  d.normalize();
  const zAxis = new THREE.Vector3().crossVectors(n3, UP).normalize();
  let start = a, m0 = mitre[0], m1 = mitre[1];
  if (zAxis.dot(d) < 0) { start = b; m0 = mitre[1]; m1 = mitre[0]; }
  const shape = new THREE.Shape(profile.map(([u, v]) => new THREE.Vector2(u, v)));
  const geo = new THREE.ExtrudeGeometry(shape, { depth: len, bevelEnabled: false, steps: 1 });
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const u = pos.getX(i), z = pos.getZ(i);
    if (m0 && z < 1e-4) pos.setZ(i, z + u);
    else if (m1 && z > len - 1e-4) pos.setZ(i, z - u);
  }
  const M = new THREE.Matrix4().makeBasis(n3, UP.clone(), zAxis).setPosition(start);
  geo.applyMatrix4(M);
  geo.computeVertexNormals();
  return geo;
}

// Picture frame: a rectangle with a hole, extruded with a bevel (cushion moulding). Local x
// along the wall, y up, z out of the wall; the back face sits on the wall (z = 0).
function frameGeometry(w, h, fw, depth, style) {
  const bs = style === 'thin-metal' ? fw * 0.15 : fw * 0.3;
  const bt = Math.min(depth * 0.45, fw * 0.4);
  const hole = { w: w + 2 * bs + 0.012, h: h + 2 * bs + 0.012 };
  const outer = { w: hole.w + 2 * fw, h: hole.h + 2 * fw };
  const shape = new THREE.Shape();
  shape.moveTo(-outer.w / 2, -outer.h / 2);
  shape.lineTo(outer.w / 2, -outer.h / 2);
  shape.lineTo(outer.w / 2, outer.h / 2);
  shape.lineTo(-outer.w / 2, outer.h / 2);
  shape.closePath();
  const inner = new THREE.Path();
  inner.moveTo(-hole.w / 2, -hole.h / 2);
  inner.lineTo(-hole.w / 2, hole.h / 2);
  inner.lineTo(hole.w / 2, hole.h / 2);
  inner.lineTo(hole.w / 2, -hole.h / 2);
  inner.closePath();
  shape.holes.push(inner);
  const geo = new THREE.ExtrudeGeometry(shape, {
    depth: Math.max(0.01, depth - 2 * bt), bevelEnabled: true, bevelThickness: bt, bevelSize: bs,
    bevelSegments: style === 'thin-metal' ? 1 : 2, steps: 1,
  });
  geo.translate(0, 0, bt);
  return geo;
}

function wallBasis(n3) {
  // local x along the wall, y up, z = outward normal (right-handed)
  const x = new THREE.Vector3().crossVectors(UP, n3).normalize();
  return new THREE.Matrix4().makeBasis(x, UP.clone(), n3.clone());
}

function cylinderGeometry(r0, r1, h, seg = 24) {
  return new THREE.CylinderGeometry(r1, r0, h, seg); // top radius r1, bottom r0
}

// ---------------------------------------------------------------- the builder -----------
export function buildScene(rec, ctx) {
  const { matlib, manifestIndex, renderer, models, imageRoot = '../../', roomsById = null } = ctx;
  const sid = rec.id;
  const root = new THREE.Group();
  root.name = `WORLD-${sid}`;
  const owned = { geometries: new Set(), materials: new Set(), textures: new Set() };
  const doors = [];
  const artMeshes = [];
  const fxEmpties = [];
  const sculpts = [];
  const pending = [];        // promises (models) the scene is still waiting on
  const wallTint = rec.style && rec.style.wall ? rec.style.wall : null;
  const maxAniso = renderer ? renderer.capabilities.getMaxAnisotropy() : 1;

  const mat = (slot, opts) => matlib.get(slot, opts);
  function own(geo) { owned.geometries.add(geo); return geo; }
  function addMesh(name, geo, material, { shadow = true, visible = true } = {}) {
    const m = new THREE.Mesh(own(geo), material);
    m.name = name;
    m.castShadow = shadow;
    m.receiveShadow = true;
    m.visible = visible;
    m.userData.procedural = true;
    root.add(m);
    return m;
  }
  function slotMaterial(slot) {
    if (slot === 'plaster_wall' && wallTint) return mat('plaster_wall', { color: wallTint });
    return mat(slot);
  }
  const merged = new Map(); // material -> [geometries] (decorative, merged at the end)
  function collect(slot, geo, opts = {}) {
    const m = opts.material || slotMaterial(slot);
    applyWorldUV(geo, m.userData.tile || [1, 1]);
    if (!merged.has(m)) merged.set(m, []);
    merged.get(m).push(geo.index ? geo.toNonIndexed() : geo);
  }

  // ---- structure ---------------------------------------------------------------------
  for (const b of rec.boxes || []) {
    const geo = boxGeometry(b);
    const m = slotMaterial(b.material);
    applyWorldUV(geo, m.userData.tile || [1, 1]);
    addMesh(b.name, geo, m);
  }
  for (const s of rec.shapes || []) {
    let geo;
    if (s.kind === 'lathe') geo = latheGeometry(s);
    else if (s.kind === 'disc') geo = discGeometry(s);
    else continue;
    const m = slotMaterial(s.material);
    applyWorldUV(geo, m.userData.tile || [1, 1]);
    const mesh = addMesh(s.name, geo, m, { shadow: !/dome|oculus|apse_dome/.test(s.name) });
    if (s.kind === 'lathe' || s.kind === 'disc') {
      // lathes/discs are single surfaces: show both sides so the drum is solid from inside and out
      mesh.material = m.userData.doubleSided || (m.userData.doubleSided = m.clone());
      mesh.material.side = THREE.DoubleSide;
      mesh.material.userData.pbr = true;
      mesh.material.userData.tile = m.userData.tile;
    }
  }

  // ---- mouldings (profile sweeps, mitred at inside corners) ----------------------------
  const runEnds = [];
  for (const mo of rec.mouldings || []) for (const run of mo.runs || []) runEnds.push([run[0], run[2]], [run[1], run[2]]);
  function isCorner(p, n) {
    return runEnds.some(([q, nq]) => Math.hypot(q[0] - p[0], q[1] - p[1]) < 0.05 && (nq[0] !== n[0] || nq[1] !== n[1]));
  }
  for (const mo of rec.mouldings || []) {
    const profile = PROFILES[mo.profile];
    if (!profile || !mo.runs) continue;
    for (const [A, B, n] of mo.runs) {
      const geo = extrudeRun(profile, A, B, n, { mitre: [isCorner(A, n), isCorner(B, n)] });
      if (geo) collect(mo.material || 'painted_trim', geo);
    }
  }
  // pilasters (hub): giant order between the doors
  (rec.pilasters || []).forEach(([x, y, z], i) => {
    const inward = y < 0 ? 1 : -1;
    const base = { x: [x - 0.45, x + 0.45], y: y < 0 ? [y + 0.2, y + 0.55] : [y - 0.55, y - 0.2], z: [0, 0.35] };
    const shaft = { x: [x - 0.35, x + 0.35], y: y < 0 ? [y + 0.2, y + 0.45] : [y - 0.45, y - 0.2], z: [0.35, 8.0] };
    const cap = { x: [x - 0.5, x + 0.5], y: y < 0 ? [y + 0.2, y + 0.6] : [y - 0.6, y - 0.2], z: [8.0, 8.35] };
    void inward;
    collect('marble_white', boxGeometry(base));
    collect('plaster_ceiling', boxGeometry(shaft));
    collect('gilt', boxGeometry(cap));
  });

  // ---- doors -------------------------------------------------------------------------
  for (const d of rec.doors || []) {
    if (roomsById && d.target !== 'hub' && !roomsById.has(d.target)) continue; // wing switched off
    const built = buildDoor(d, { matlib, sceneId: sid, height: rec.height || 7, wallTint, collect, addMesh, own, owned });
    doors.push(built.leaf);
  }

  // ---- works: art planes + frames -----------------------------------------------------
  const perRoomArt = [];
  const _n = new THREE.Vector3();
  const hangs = Object.values(rec.hangs || {});
  const frameStyleMaterial = { 'gilt-ornate': 'gilt', 'gilt-simple': 'gilt', 'dark-wood': 'dark_wood', 'black-lacquer': 'lacquer', 'thin-metal': 'iron' };
  for (const h of hangs) {
    const entry = manifestIndex.byWorkId.get(h.id);
    if (!entry) { console.warn('[museum] hang without a manifest work:', h.id); continue; }
    const pos = blenderToThree(h.pos);
    _n.copy(blenderToThree(h.normal)).normalize();
    const geo = new THREE.PlaneGeometry(h.w, h.h);
    const material = new THREE.MeshStandardMaterial({ name: `MAT-ART-${entry.artist.slug}__${h.id}`, color: PLACEHOLDER, roughness: 0.55, metalness: 0, envMapIntensity: 0.6 });
    material.userData.owned = true;
    owned.materials.add(material);
    const mesh = new THREE.Mesh(own(geo), material);
    mesh.name = `ART-${entry.artist.slug}__${h.id}`;
    mesh.position.copy(pos);
    mesh.lookAt(pos.clone().add(_n));
    const isText = typeof entry.work.text === 'string' && !entry.work.image;
    mesh.userData = { workId: h.id, room: h.room, wall: h.wall, along: h.along, z: h.pos[2], w: h.w, h: h.h, scale: h.scale,
      procedural: true, panel: isText,
      thumbUrl: isText ? null : imageRoot + ((manifestIndex.wingsById.get(entry.wing) || {}).image_base || 'Art-Talk-main/') + (entry.work.thumb || entry.work.image),
      facing: _n.clone() };
    if (isText) {
      material.map = panelTexture(entry.work, h, { owned, maxAniso });
      material.color.set(0xffffff);
      material.needsUpdate = true;
    }
    mesh.castShadow = false;
    mesh.receiveShadow = true;
    root.add(mesh);
    artMeshes.push(mesh);
    perRoomArt.push(mesh);
    // frame + mat board behind
    const fr = h.frame || { style: 'none', width: 0, depth: 0 };
    if (fr.style && fr.style !== 'none' && fr.width > 0) {
      const fgeo = frameGeometry(h.w, h.h, fr.width, fr.depth, fr.style);
      const facePoint = pos.clone().addScaledVector(_n, -ART_PROUD);
      fgeo.applyMatrix4(wallBasis(_n).setPosition(facePoint));
      fgeo.computeVertexNormals();
      collect(frameStyleMaterial[fr.style] || 'gilt', fgeo);
      const bs = fr.style === 'thin-metal' ? fr.width * 0.15 : fr.width * 0.3;
      const back = new THREE.PlaneGeometry(h.w + 2 * bs + 0.06, h.h + 2 * bs + 0.06);
      back.applyMatrix4(wallBasis(_n).setPosition(facePoint.clone().addScaledVector(_n, 0.012)));
      collect('mat_board', back);
    } else if (h.type === 'hanging-scroll' || h.type === 'handscroll') {
      // scroll rods: two dark cylinders at the top and bottom edge
      const facePoint = pos.clone().addScaledVector(_n, -ART_PROUD);
      for (const sgn of [1, -1]) {
        const rod = new THREE.CylinderGeometry(0.02, 0.02, h.w + 0.12, 12);
        rod.rotateZ(Math.PI / 2);
        rod.applyMatrix4(wallBasis(_n).setPosition(facePoint.clone().addScaledVector(UP, sgn * (h.h / 2 + 0.02)).addScaledVector(_n, 0.05)));
        collect('dark_wood', rod);
      }
    }
  }

  // ---- fixtures: FX empties + bodies --------------------------------------------------
  (rec.fx || []).forEach((f, i) => {
    const p = blenderToThree(f.pos);
    const e = new THREE.Object3D();
    e.name = f.name || `FX-${sid}_${f.type}_${i}`;
    e.position.copy(p);
    e.userData = { fx_type: f.type, fx_color: f.color, fx_intensity: f.intensity, fx_distance: f.distance, fx_shadow: f.shadow, fx_room: sid };
    if (f.dir) e.userData.fx_dir_three = blenderToThree(f.dir).toArray();
    if (f.size) e.userData.fx_size = f.size;
    root.add(e);
    fxEmpties.push(e);
    const idx = fxEmpties.length - 1;
    if (f.type === 'sconce') {
      const n3 = f.dir ? blenderToThree(f.dir).normalize() : new THREE.Vector3(0, 0, -1);
      const wallPt = p.clone().addScaledVector(n3, -0.3);
      const arm = new THREE.CylinderGeometry(0.02, 0.02, 0.28, 10);
      arm.rotateX(Math.PI / 2);
      arm.applyMatrix4(wallBasis(n3).setPosition(wallPt.clone().addScaledVector(n3, 0.14).addScaledVector(UP, -0.1)));
      collect('brass', arm);
      const plate = new THREE.CylinderGeometry(0.09, 0.09, 0.02, 16);
      plate.rotateX(Math.PI / 2);
      plate.applyMatrix4(wallBasis(n3).setPosition(wallPt.clone().addScaledVector(n3, 0.01).addScaledVector(UP, -0.1)));
      collect('brass', plate);
      const cup = new THREE.CylinderGeometry(0.06, 0.035, 0.12, 14);
      cup.translate(p.x, p.y - 0.06, p.z);
      collect('brass', cup);
      const bulb = new THREE.SphereGeometry(0.055, 14, 10);
      bulb.translate(p.x, p.y + 0.02, p.z);
      collect('bulb', bulb);
    } else if (f.type === 'picture_light') {
      const n3 = new THREE.Vector3(0, 0, -1);
      const over = f.over ? artMeshes.find((m) => m.userData.workId === f.over) : null;
      if (over) n3.copy(over.userData.facing);
      const w = over ? Math.min(1.2, over.userData.w * 0.6) : 0.6;
      const tube = new THREE.CylinderGeometry(0.02, 0.02, w, 10);
      tube.rotateZ(Math.PI / 2);
      tube.applyMatrix4(wallBasis(n3).setPosition(p.clone().addScaledVector(n3, 0.02)));
      collect('brass', tube);
      const armG = new THREE.CylinderGeometry(0.012, 0.012, 0.3, 8);
      armG.rotateX(Math.PI / 2);
      armG.applyMatrix4(wallBasis(n3).setPosition(p.clone().addScaledVector(n3, -0.13).addScaledVector(UP, 0.02)));
      collect('brass', armG);
      const glow = new THREE.BoxGeometry(w * 0.9, 0.012, 0.03);
      glow.applyMatrix4(wallBasis(n3).setPosition(p.clone().addScaledVector(n3, 0.02).addScaledVector(UP, -0.02)));
      collect('candle', glow);
    } else if (f.type === 'laylight') {
      const sz = f.size || [3, 2];
      const g = new THREE.PlaneGeometry(sz[0], sz[1]);
      g.rotateX(Math.PI / 2);
      g.translate(p.x, p.y + 0.15, p.z);
      collect('laylight', g);
      const frame = new THREE.BoxGeometry(sz[0] + 0.3, 0.06, sz[1] + 0.3);
      frame.translate(p.x, p.y + 0.19, p.z);
      collect('painted_trim', frame);
    } else if (f.type === 'chandelier' || f.type === 'pendant') {
      const ceilY = (rec.height || 7) + (sid === 'hub' && Math.hypot(f.pos[0] - (rec.rotunda ? rec.rotunda.center[0] : 1e9), f.pos[1]) < 7 ? 1.0 : 0);
      if (f.model && models) {
        const pr = models.acquire(f.model).then((holder) => {
          const size = holder.userData.size;
          holder.position.set(p.x, p.y - size.y / 2, p.z);
          holder.name = `GEO-${sid}_chandelier_${idx}`;
          holder.traverse((o) => { if (o.isMesh) { o.castShadow = false; o.userData.shared = true; } });
          root.add(holder);
          const chain = new THREE.CylinderGeometry(0.015, 0.015, Math.max(0.05, ceilY - (p.y + size.y / 2)), 8);
          chain.translate(p.x, (ceilY + p.y + size.y / 2) / 2, p.z);
          addMesh(`GEO-${sid}_chain_${idx}`, chain, mat('brass'), { shadow: false });
        }).catch(() => {});
        pending.push(pr);
      } else {
        const body = new THREE.SphereGeometry(0.18, 16, 12);
        body.translate(p.x, p.y, p.z);
        addMesh(`GEO-${sid}_chandelier_${idx}`, body, mat('bulb'), { shadow: false });
      }
    }
  });

  // ---- props: pedestals + sculptures, benches, wall reliefs -----------------------------
  (rec.props || []).forEach((pr, i) => {
    const p = blenderToThree(pr.pos);
    const yawRad = THREE.MathUtils.degToRad((pr.yaw_deg || 0) + 90);
    let topY = p.y;
    if (pr.pedestal) {
      const pd = pr.pedestal;
      const r = pd.r || 0.42;
      if (pd.kind === 'column') {
        const plinth = new THREE.BoxGeometry(r * 2.2, 0.25, r * 2.2);
        plinth.translate(p.x, p.y + 0.125, p.z);
        collect(pd.material || 'marble_white', plinth);
        const shaftH = pd.h - 0.25 - 0.22;
        const pts = [];
        for (let k = 0; k <= 8; k++) {
          const t = k / 8;
          pts.push(new THREE.Vector2(r * 0.72 * (1 - 0.12 * t * t), 0.25 + shaftH * t));
        }
        const shaft = new THREE.LatheGeometry(pts, 32);
        shaft.translate(p.x, p.y, p.z);
        collect(pd.material || 'marble_white', shaft);
        const ech = new THREE.LatheGeometry([new THREE.Vector2(r * 0.63, 0), new THREE.Vector2(r * 0.72, 0.05), new THREE.Vector2(r * 0.9, 0.11), new THREE.Vector2(r * 0.95, 0.14)], 32);
        ech.translate(p.x, p.y + 0.25 + shaftH, p.z);
        collect(pd.material || 'marble_white', ech);
        const abacus = new THREE.BoxGeometry(r * 2.0, 0.08, r * 2.0);
        abacus.translate(p.x, p.y + pd.h - 0.04, p.z);
        collect(pd.material || 'marble_white', abacus);
        topY = p.y + pd.h;
      } else {
        const w = Math.max(1.2, (pd.w || 1.4));
        const plinth = new THREE.BoxGeometry(w, pd.h, w);
        plinth.translate(p.x, p.y + pd.h / 2, p.z);
        collect(pd.material || 'marble_dark', plinth);
        const lip = new THREE.BoxGeometry(w + 0.12, 0.06, w + 0.12);
        lip.translate(p.x, p.y + pd.h - 0.03, p.z);
        collect('marble_white', lip);
        topY = p.y + pd.h;
      }
    }
    if (!pr.model || !models) return;
    const promise = models.acquire(pr.model).then((holder) => {
      const size = holder.userData.size;
      holder.rotation.y = yawRad;
      if (pr.mount === 'wall') {
        const n3 = blenderToThree(pr.normal || [0, 1, 0]).normalize();
        holder.position.copy(p).addScaledVector(n3, size.z / 2 + 0.02);
        holder.position.y = p.y - size.y / 2;
        holder.lookAt(holder.position.clone().add(n3));
      } else {
        holder.position.set(p.x, topY, p.z);
      }
      holder.name = pr.name.startsWith('SCULPT-') ? `MODEL-${pr.model}` : pr.name;
      holder.traverse((o) => { if (o.isMesh) o.userData.shared = true; });
      root.add(holder);
      if (pr.name.startsWith('SCULPT-')) {
        holder.updateMatrixWorld(true);
        const box = new THREE.Box3().setFromObject(holder);
        const sz = box.getSize(new THREE.Vector3());
        const c = box.getCenter(new THREE.Vector3());
        const proxy = new THREE.Mesh(own(new THREE.BoxGeometry(Math.max(0.3, sz.x), Math.max(0.3, sz.y), Math.max(0.3, sz.z))), new THREE.MeshBasicMaterial({ visible: false }));
        proxy.material.userData.owned = true;
        owned.materials.add(proxy.material);
        proxy.position.copy(c);
        proxy.name = pr.name;
        proxy.visible = false;
        proxy.userData = { model: pr.model, credits: holder.userData.credits, procedural: true };
        root.add(proxy);
        sculpts.push(proxy);
        // collider around the pedestal footprint (contains `wall` on purpose)
        if (pr.pedestal) {
          const fw = Math.max(sz.x, sz.z, (pr.pedestal.r || 0.42) * 2.2) + 0.5;
          const col = new THREE.Mesh(own(new THREE.BoxGeometry(fw, 1.6, fw)), proxy.material);
          col.position.set(p.x, p.y + 0.8, p.z);
          col.name = `GEO-${sid}_wall_plinth_${i}`;
          col.visible = false;
          root.add(col);
        }
      } else if (pr.name.includes('bench')) {
        const col = new THREE.Mesh(own(new THREE.BoxGeometry(size.x + 0.3, 1.4, size.z + 0.3)), new THREE.MeshBasicMaterial({ visible: false }));
        col.material.userData.owned = true;
        owned.materials.add(col.material);
        col.position.set(p.x, p.y + 0.7, p.z);
        col.rotation.y = yawRad;
        col.name = `GEO-${sid}_wall_bench_${i}`;
        col.visible = false;
        root.add(col);
      }
    }).catch(() => {});
    pending.push(promise);
  });

  // ---- merge the decorative geometry per material ---------------------------------------
  let k = 0;
  for (const [m, geos] of merged) {
    if (!geos.length) continue;
    const g = geos.length === 1 ? geos[0] : mergeGeometries(geos, false);
    if (!g) continue;
    for (const geo of geos) if (geo !== g) geo.dispose();
    const slot = m.userData.slot || 'x';
    addMesh(`GEO-${sid}_trim_${slot}_${k++}`, g, m, { shadow: !/bulb|candle|laylight|glass/.test(slot) });
  }

  // ---- textures: stream this scene's works ---------------------------------------------
  const loader = new THREE.TextureLoader();
  const queue = [];
  let active = 0;
  let cancelled = false;
  const stats = { loads: 0, failures: 0 };
  function pump() {
    while (active < CONCURRENCY && queue.length) {
      const job = queue.shift();
      active++;
      job().catch(() => {}).finally(() => { active--; pump(); });
    }
  }
  function loadMesh(mesh) {
    if (mesh.material.map || cancelled || !mesh.userData.thumbUrl) return Promise.resolve();
    return new Promise((resolve) => {
      queue.push(() => loader.loadAsync(mesh.userData.thumbUrl).then((tex) => {
        if (cancelled) { tex.dispose(); return; }
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.anisotropy = maxAniso;
        owned.textures.add(tex);
        mesh.material.map = tex;
        mesh.material.color.set(0xffffff);
        mesh.material.needsUpdate = true;
        stats.loads++;
      }).catch((e) => {
        stats.failures++;
        console.warn('[museum] work image failed:', mesh.userData.thumbUrl, e && e.message);
      }).finally(resolve));
      pump();
    });
  }
  let texturesPromise = null;
  function loadTextures() {
    if (!texturesPromise) texturesPromise = Promise.all(perRoomArt.map(loadMesh));
    return texturesPromise;
  }
  function whenLoaded() { return Promise.all([loadTextures(), ...pending]).then(() => world); }

  function dispose() {
    cancelled = true;
    queue.length = 0;
    root.traverse((o) => {
      if (o.isMesh && !o.userData.shared) {
        if (o.geometry && owned.geometries.has(o.geometry)) o.geometry.dispose();
      }
    });
    for (const g of owned.geometries) g.dispose();
    for (const t of owned.textures) t.dispose();
    for (const m of owned.materials) m.dispose();
    for (const pr of rec.props || []) if (pr.model && models) models.release(pr.model);
    for (const f of rec.fx || []) if (f.model && models) models.release(f.model);
    owned.geometries.clear(); owned.textures.clear(); owned.materials.clear();
  }

  root.updateMatrixWorld(true);
  const world = { id: sid, rec, root, doors, artMeshes, fx: fxEmpties, sculpts, owned, loadTextures, whenLoaded, dispose, textureStats: stats };
  return world;
}
