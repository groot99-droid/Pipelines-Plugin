// Doors: a clickable leaf (`DOOR-<target>`) inside an era-themed surround with a plaque.
//
// The leaf is a slab in the opening (it collides: scenes.js lists DOOR- meshes among the walls)
// and carries userData {target, name, years, facing, spawn}. Surround pieces go to the scene's
// merged trim (collect) so a hub with 16 doors stays a handful of draw calls. Themes (§ THEMES)
// pick the surround shape (post-and-lintel, arches, pediments, cast iron, art deco, steel) and
// the leaf material; the plaque is a CanvasTexture with the room's name and years.
import * as THREE from 'three';
import { blenderToThree } from './coords.js';

const UP = new THREE.Vector3(0, 1, 0);

export const THEMES = {
  hall: { surround: 'casing', leaf: 'walnut', casing: 'painted_trim', accent: 'gilt', plaque: { bg: '#2b2119', fg: '#e9d7a8' } },
  'post-lintel-megalith': { surround: 'post-lintel', leaf: 'bronze', casing: 'sandstone', accent: 'bronze', post: 0.7, plaque: { bg: '#4a3620', fg: '#f0d9a6' } },
  'post-lintel-timber': { surround: 'post-lintel', leaf: 'oak', casing: 'dark_wood', accent: 'iron', post: 0.45, straps: true, plaque: { bg: '#2a2622', fg: '#d9cdb0' } },
  'doric-pediment': { surround: 'pediment', leaf: 'lacquer', casing: 'marble_white', accent: 'gilt', columns: true, plaque: { bg: '#f1ece2', fg: '#7a5a2a' } },
  'pointed-arch': { surround: 'pointed-arch', leaf: 'oak', casing: 'stone', accent: 'iron', plaque: { bg: '#3a3430', fg: '#e6d8b8' } },
  'round-arch-keystone': { surround: 'round-arch', leaf: 'walnut', casing: 'stone', accent: 'marble_white', keystone: true, plaque: { bg: '#5a4636', fg: '#f0e2c4' } },
  'baroque-pediment': { surround: 'broken-pediment', leaf: 'lacquer', casing: 'marble_dark', accent: 'gilt', columns: true, plaque: { bg: '#3a1e1e', fg: '#f0d28a' } },
  'cast-iron-glass': { surround: 'fanlight', leaf: 'frosted_glass', casing: 'iron', accent: 'brass', plaque: { bg: '#1f2a24', fg: '#e8e4d2' } },
  'art-deco': { surround: 'ziggurat', leaf: 'lacquer', casing: 'lacquer', accent: 'chrome', plaque: { bg: '#141414', fg: '#e8e8ea' } },
  'steel-glass': { surround: 'portal', leaf: 'glass', casing: 'steel', accent: 'steel', backlit: true, plaque: { bg: '#f4f4f6', fg: '#222428' } },
};

function plaqueTexture(name, years, colors, owned) {
  const c = document.createElement('canvas');
  c.width = 768; c.height = 224;
  const g = c.getContext('2d');
  g.fillStyle = colors.bg;
  g.fillRect(0, 0, c.width, c.height);
  g.strokeStyle = colors.fg;
  g.lineWidth = 6;
  g.strokeRect(14, 14, c.width - 28, c.height - 28);
  g.fillStyle = colors.fg;
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  let size = 64;
  g.font = `${size}px Georgia, "Times New Roman", serif`;
  while (g.measureText(name).width > c.width - 80 && size > 28) { size -= 4; g.font = `${size}px Georgia, "Times New Roman", serif`; }
  g.fillText(name, c.width / 2, years ? 92 : 112);
  if (years) {
    g.font = '38px Georgia, "Times New Roman", serif';
    g.globalAlpha = 0.85;
    g.fillText(years, c.width / 2, 162);
    g.globalAlpha = 1;
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  if (owned) owned.textures.add(tex);
  return tex;
}

// Arch shape in the local x/y plane (y up), spanning [-w/2, w/2] × [0, h], as a ring `t` thick.
function archShape(kind, w, h, t) {
  const s = new THREE.Shape();
  const r = w / 2;
  const springs = h - r;               // where the arch starts
  s.moveTo(-r - t, 0);
  s.lineTo(-r - t, springs);
  if (kind === 'round') {
    s.absarc(0, springs, r + t, Math.PI, 0, true);
  } else {
    // pointed: two arcs of radius w centred on the opposite springing points
    const R = w + t;
    const cx = r;               // centre of the left arc is the right springing point
    const apexY = springs + Math.sqrt(Math.max(0, R * R - cx * cx));
    s.quadraticCurveTo(-r - t, springs + (apexY - springs) * 0.75, 0, apexY);
    s.quadraticCurveTo(r + t, springs + (apexY - springs) * 0.75, r + t, springs);
  }
  s.lineTo(r + t, 0);
  s.lineTo(r, 0);
  s.lineTo(r, springs);
  if (kind === 'round') {
    s.absarc(0, springs, r, 0, Math.PI, false);
  } else {
    const R = w;
    const apexY = springs + Math.sqrt(Math.max(0, R * R - r * r));
    s.quadraticCurveTo(r, springs + (apexY - springs) * 0.75, 0, apexY);
    s.quadraticCurveTo(-r, springs + (apexY - springs) * 0.75, -r, springs);
  }
  s.lineTo(-r, 0);
  s.closePath();
  return s;
}

function triangleShape(w, h) {
  const s = new THREE.Shape();
  s.moveTo(-w / 2, 0); s.lineTo(w / 2, 0); s.lineTo(0, h); s.closePath();
  return s;
}

export function buildDoor(d, { matlib, sceneId, height = 7, collect, addMesh, own, owned }) {
  const theme = THEMES[d.theme] || THEMES.hall;
  const p = blenderToThree(d.pos);            // the opening's centre on the wall centre-line, floor level
  const n3 = blenderToThree(d.normal).normalize();  // into the scene
  const w = d.w, h = d.h;
  const T = 0.4;
  // local frame at the wall face: x along the wall, y up, z into the scene
  const face = p.clone().addScaledVector(n3, T / 2);
  const basis = new THREE.Matrix4().makeBasis(new THREE.Vector3().crossVectors(UP, n3).normalize(), UP.clone(), n3.clone());
  const at = (x, y, z) => new THREE.Matrix4().copy(basis).setPosition(face.clone().add(new THREE.Vector3().setFromMatrixColumn(basis, 0).multiplyScalar(x)).addScaledVector(UP, y).addScaledVector(n3, z));

  // the leaf: a slab a little behind the face, inside the opening
  const leafGeo = new THREE.BoxGeometry(w - 0.06, h - 0.04, 0.1);
  leafGeo.applyMatrix4(at(0, h / 2, -0.12));
  const leafMat = matlib.get(theme.leaf);
  const leaf = addMesh(`DOOR-${d.target}`, leafGeo, leafMat, { shadow: true });
  leaf.userData = { target: d.target, doorId: d.id, name: d.name, years: d.years, theme: d.theme, procedural: true,
    facing: n3.clone(), spawn: d.spawn, hubSide: d.hub_side || null, center: p.clone(), width: w };
  // panels on the leaf (cheap relief)
  if (theme.leaf !== 'glass' && theme.leaf !== 'frosted_glass') {
    for (const [px, py, pw, ph] of [[-w / 4 + 0.02, h * 0.68, w / 2 - 0.3, h * 0.42], [w / 4 - 0.02, h * 0.68, w / 2 - 0.3, h * 0.42], [-w / 4 + 0.02, h * 0.22, w / 2 - 0.3, h * 0.28], [w / 4 - 0.02, h * 0.22, w / 2 - 0.3, h * 0.28]]) {
      const panel = new THREE.BoxGeometry(pw, ph, 0.03);
      panel.applyMatrix4(at(px, py, -0.06));
      collect(theme.accent === 'iron' || theme.leaf === 'bronze' ? theme.accent : theme.leaf, panel);
    }
  }
  if (theme.straps) {
    for (const py of [h * 0.25, h * 0.75]) {
      const strap = new THREE.BoxGeometry(w - 0.2, 0.12, 0.02);
      strap.applyMatrix4(at(0, py, -0.05));
      collect('iron', strap);
    }
  }

  // casing: jambs + head (every theme), proud of the face
  const cw = 0.22, cd = 0.08;
  const s = theme.surround;
  const jambH = s === 'round-arch' || s === 'pointed-arch' ? h - w / 2 : h;
  for (const sx of [-1, 1]) {
    const jamb = new THREE.BoxGeometry(cw, jambH + (s === 'casing' ? cw : 0), cd);
    jamb.applyMatrix4(at(sx * (w / 2 + cw / 2), (jambH + (s === 'casing' ? cw : 0)) / 2, cd / 2));
    collect(theme.casing, jamb);
  }
  if (s === 'casing' || s === 'portal' || s === 'ziggurat' || s === 'fanlight' || s === 'pediment' || s === 'broken-pediment' || s === 'post-lintel') {
    const headH = s === 'post-lintel' ? 0.7 : cw;
    const head = new THREE.BoxGeometry(w + 2 * cw + (s === 'post-lintel' ? 2 * (theme.post || 0.5) - 2 * cw : 0), headH, s === 'post-lintel' ? cd * 2 : cd);
    head.applyMatrix4(at(0, h + headH / 2, (s === 'post-lintel' ? cd : cd / 2)));
    collect(theme.casing, head);
  }
  if (s === 'post-lintel') {
    const pw = theme.post || 0.5;
    for (const sx of [-1, 1]) {
      const post = new THREE.BoxGeometry(pw, h, 0.5);
      post.applyMatrix4(at(sx * (w / 2 + cw + pw / 2), h / 2, 0.25));
      collect(theme.casing, post);
    }
  }
  if (s === 'round-arch' || s === 'pointed-arch') {
    const ring = new THREE.ExtrudeGeometry(archShape(s === 'round-arch' ? 'round' : 'pointed', w, h, cw), { depth: cd, bevelEnabled: false });
    ring.applyMatrix4(at(0, 0, 0));
    collect(theme.casing, ring);
    if (theme.keystone) {
      const ks = new THREE.BoxGeometry(0.34, 0.5, cd + 0.06);
      ks.applyMatrix4(at(0, h + cw - 0.1, cd / 2 + 0.03));
      collect(theme.accent, ks);
    }
    // outer order
    const ring2 = new THREE.ExtrudeGeometry(archShape(s === 'round-arch' ? 'round' : 'pointed', w + 2 * cw + 0.1, h + cw + 0.05, 0.16), { depth: cd * 0.6, bevelEnabled: false });
    ring2.applyMatrix4(at(0, 0, 0));
    collect(theme.accent === 'iron' ? theme.casing : theme.accent, ring2);
  }
  if (s === 'pediment' || s === 'broken-pediment') {
    const entH = 0.45;
    const ent = new THREE.BoxGeometry(w + 2 * cw + 1.2, entH, cd + 0.12);
    ent.applyMatrix4(at(0, h + cw + entH / 2, (cd + 0.12) / 2));
    collect(theme.casing, ent);
    const pedW = w + 2 * cw + 1.4;
    if (s === 'pediment') {
      const tri = new THREE.ExtrudeGeometry(triangleShape(pedW, pedW * 0.22), { depth: cd + 0.1, bevelEnabled: false });
      tri.applyMatrix4(at(0, h + cw + entH, 0));
      collect(theme.casing, tri);
      const tym = new THREE.ExtrudeGeometry(triangleShape(pedW - 0.5, (pedW - 0.5) * 0.22 - 0.02), { depth: cd * 0.5, bevelEnabled: false });
      tym.applyMatrix4(at(0, h + cw + entH + 0.06, cd + 0.1 - cd * 0.5 + 0.01));
      collect(theme.accent, tym);
    } else {
      for (const sx of [-1, 1]) {
        const half = new THREE.ExtrudeGeometry(triangleShape(pedW * 0.62, pedW * 0.2), { depth: cd + 0.1, bevelEnabled: false });
        half.applyMatrix4(at(sx * pedW * 0.19, h + cw + entH, 0));
        collect(theme.casing, half);
      }
      const cart = new THREE.SphereGeometry(0.28, 16, 12);
      cart.applyMatrix4(at(0, h + cw + entH + 0.35, cd * 0.5));
      collect(theme.accent, cart);
    }
    if (theme.columns) {
      for (const sx of [-1, 1]) {
        const pts = [];
        for (let k = 0; k <= 6; k++) { const t = k / 6; pts.push(new THREE.Vector2(0.2 * (1 - 0.1 * t * t), 0.3 + (h + cw - 0.45) * t)); }
        const col = new THREE.LatheGeometry(pts, 20);
        col.applyMatrix4(at(sx * (w / 2 + cw + 0.55), 0, 0.35));
        collect(theme.casing, col);
        const base = new THREE.BoxGeometry(0.56, 0.3, 0.56);
        base.applyMatrix4(at(sx * (w / 2 + cw + 0.55), 0.15, 0.35));
        collect(theme.casing, base);
        const cap = new THREE.BoxGeometry(0.5, 0.15, 0.5);
        cap.applyMatrix4(at(sx * (w / 2 + cw + 0.55), h + cw - 0.08, 0.35));
        collect(theme.accent, cap);
      }
    }
  }
  if (s === 'fanlight') {
    const R = w / 2 + cw;
    const fan = new THREE.ExtrudeGeometry(archShape('round', w + 2 * cw, h + cw + R, 0.12), { depth: cd, bevelEnabled: false });
    fan.applyMatrix4(at(0, 0, 0));
    collect(theme.casing, fan);
    const glass = new THREE.CircleGeometry(R - 0.02, 24, 0, Math.PI);
    glass.applyMatrix4(at(0, h + cw, cd * 0.5));
    addMesh(`GEO-${sceneId}_fanglass_${d.target}`, glass, matlib.get('frosted_glass'), { shadow: false });
    for (let k = 1; k < 8; k++) {
      const a = (Math.PI * k) / 8;
      const spoke = new THREE.BoxGeometry(0.03, R - 0.05, 0.03);
      spoke.translate(0, (R - 0.05) / 2, 0);
      spoke.rotateZ(a - Math.PI / 2);
      spoke.applyMatrix4(at(0, h + cw, cd * 0.55));
      collect('iron', spoke);
    }
  }
  if (s === 'ziggurat') {
    for (let k = 0; k < 3; k++) {
      const step = new THREE.BoxGeometry(w + 2 * cw + 0.5 * (k + 1), 0.18, cd + 0.04 * (3 - k));
      step.applyMatrix4(at(0, h + cw + 0.18 * k + 0.09, (cd + 0.04 * (3 - k)) / 2));
      collect(k % 2 ? theme.accent : theme.casing, step);
    }
    for (const sx of [-1, 1]) {
      for (let k = 0; k < 3; k++) {
        const fin = new THREE.BoxGeometry(0.08, h * (0.55 + 0.15 * k), 0.06 + 0.03 * k);
        fin.applyMatrix4(at(sx * (w / 2 + cw + 0.18 + 0.16 * k), h * (0.55 + 0.15 * k) / 2, 0.04));
        collect(theme.accent, fin);
      }
    }
  }
  if (s === 'portal') {
    const frame = new THREE.BoxGeometry(w + 2 * cw + 0.3, 0.12, cd + 0.1);
    frame.applyMatrix4(at(0, h + cw + 0.06, (cd + 0.1) / 2));
    collect('steel', frame);
  }

  // plaque above the opening (or beside it for very tall surrounds)
  const plaqueW = 1.6, plaqueH = plaqueW * (224 / 768);
  const py = s === 'pediment' || s === 'broken-pediment' ? h + cw + 0.2 : s === 'fanlight' ? h + 0.1 + (w / 2 + cw) + 0.35 : h + (s === 'post-lintel' ? 0.75 : s === 'round-arch' || s === 'pointed-arch' ? cw + 0.5 : cw) + plaqueH / 2 + 0.12;
  const plaqueGeo = new THREE.PlaneGeometry(plaqueW, plaqueH);
  plaqueGeo.applyMatrix4(at(0, py, cd + 0.03));
  const ptex = plaqueTexture(d.name || d.target, d.years || '', theme.plaque, owned);
  const pmat = new THREE.MeshStandardMaterial({ map: ptex, roughness: 0.6, metalness: 0.0, emissive: new THREE.Color(theme.backlit ? '#ffffff' : '#000000'), emissiveMap: theme.backlit ? ptex : null, emissiveIntensity: theme.backlit ? 0.8 : 0 });
  pmat.userData.owned = true;
  pmat.userData.pbr = true;
  owned.materials.add(pmat);
  addMesh(`GEO-${sceneId}_plaque_${d.target}`, plaqueGeo, pmat, { shadow: false });
  const backing = new THREE.BoxGeometry(plaqueW + 0.08, plaqueH + 0.08, 0.03);
  backing.applyMatrix4(at(0, py, cd + 0.01));
  collect(theme.accent === 'iron' ? 'iron' : theme.accent, backing);

  return { leaf, theme };
}
