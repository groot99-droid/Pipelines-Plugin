// Gamepad controls: an Xbox pad (Bluetooth or USB) or any controller with the W3C "standard"
// mapping. Polled once per frame from the simulation loop -- there is no event stream for stick
// positions, and Firefox does not even fire `gamepadconnected` until a button is pressed.
//
//   left stick / D-pad  walk (camera-relative, analog)      right stick   look
//   A  read the work / go through the door (Explore on the start screen; pause during the tour)
//   B  back (the Esc cascade)        X  floor plan        Y  "Go to"
//   LB / RB  previous / next work (placard or tour)   Menu  help   View  start / end the tour
//
// The stick feeds the same analog `setMoveAxis` the touch joystick uses. The axis is only written
// while the stick is active (plus one zero on release) so a touch joystick is not clobbered.

const DEADZONE = 0.15;
const LOOK_RATE = 2.4;   // rad/s at full deflection
const TOAST_SECONDS = 4;

const BTN = { A: 0, B: 1, X: 2, Y: 3, LB: 4, RB: 5, VIEW: 8, MENU: 9, UP: 12, DOWN: 13, LEFT: 14, RIGHT: 15 };

// Radial deadzone with rescale so motion starts at zero just past the dead zone.
function scaleStick(x, y) {
  const len = Math.hypot(x, y);
  if (len < DEADZONE) return [0, 0];
  const m = Math.min(1, (len - DEADZONE) / (1 - DEADZONE)) / len;
  return [x * m, y * m];
}

function pressed(pad, i) {
  const b = pad.buttons && pad.buttons[i];
  return !!b && (typeof b === 'object' ? b.pressed || b.value > 0.5 : b > 0.5);
}

export function createGamepadControls({ controls, interactions, hud, navigate, tour, ui, enter, blockerEl }) {
  const enabled = typeof navigator !== 'undefined' && typeof navigator.getGamepads === 'function';
  let source = null;        // test hook: () => pad | null
  let connected = false;
  let engaged = false;      // controls.engage() done once after the first input in the museum
  let moving = false;       // stick/D-pad was active last frame (write one zero on release)
  const prev = new Array(17).fill(false);
  let toastTimer = 0;

  const toast = document.createElement('div');
  toast.id = 'gamepad-toast';
  toast.textContent = 'Controller connected · left stick walk · right stick look · A read · B back · X map · Y go to';
  document.body.appendChild(toast);

  function showToast() {
    toast.classList.add('visible');
    toastTimer = TOAST_SECONDS;
  }
  function setConnected(on) {
    if (on === connected) return;
    connected = on;
    document.body.classList.toggle('gamepad', on);
    if (on) showToast();
    else toast.classList.remove('visible');
  }

  if (enabled) {
    window.addEventListener('gamepadconnected', () => setConnected(true));
    window.addEventListener('gamepaddisconnected', () => { if (!readPad()) setConnected(false); });
  }

  function readPad() {
    if (source) return source();
    if (!enabled) return null;
    let pads;
    try { pads = navigator.getGamepads(); } catch (err) { return null; }
    if (!pads) return null;
    let fallback = null;
    for (const p of pads) {
      if (!p || p.connected === false) continue;
      if (p.mapping === 'standard') return p;
      if (!fallback) fallback = p;
    }
    return fallback;
  }

  function blockerVisible() {
    return !!blockerEl && !blockerEl.classList.contains('hidden');
  }

  function rose(pad, i) {
    const now = pressed(pad, i);
    const r = now && !prev[i];
    prev[i] = now;
    return r;
  }

  function onButtons(pad) {
    const a = rose(pad, BTN.A), b = rose(pad, BTN.B), x = rose(pad, BTN.X), y = rose(pad, BTN.Y);
    const lb = rose(pad, BTN.LB), rb = rose(pad, BTN.RB), view = rose(pad, BTN.VIEW), menu = rose(pad, BTN.MENU);
    if (blockerVisible()) {
      if (a || menu) enter({ pointerLock: false });
      return a || menu;
    }
    if (a) {
      if (tour.active()) tour.togglePause();
      else if (interactions.isOpen()) interactions.closePlacard();
      else interactions.openAtCrosshair();
    }
    if (b) ui.back();
    if (x) hud.toggleMap();
    if (y) navigate.toggle();
    if (lb || rb) {
      const dir = rb ? 1 : -1;
      if (tour.active()) { if (dir > 0) tour.next(); else tour.prev(); }
      else if (interactions.isOpen()) { if (dir > 0) interactions.nextWork(); else interactions.prevWork(); }
    }
    if (menu) ui.toggleHelp();
    if (view) ui.toggleTour();
    return a || b || x || y || lb || rb || menu || view;
  }

  function onSticks(pad, delta) {
    const ax = pad.axes || [];
    let [mx, my] = scaleStick(ax[0] || 0, ax[1] || 0);
    if (pressed(pad, BTN.UP)) my -= 1;
    if (pressed(pad, BTN.DOWN)) my += 1;
    if (pressed(pad, BTN.LEFT)) mx -= 1;
    if (pressed(pad, BTN.RIGHT)) mx += 1;
    const active = mx !== 0 || my !== 0;
    if (active) {
      controls.setMoveAxis(mx, -my); // pad y is down-positive; the move axis y is forward
      moving = true;
    } else if (moving) {
      controls.setMoveAxis(0, 0);
      moving = false;
    }

    let [lx, ly] = scaleStick(ax[2] || 0, ax[3] || 0);
    const looking = (lx !== 0 || ly !== 0) && !tour.active();
    if (looking) {
      lx *= Math.abs(lx); // squared response: fine aim near the centre, full rate at the edge
      ly *= Math.abs(ly);
      controls.rotateRadians(lx * LOOK_RATE * delta, ly * LOOK_RATE * delta);
    }
    return active || looking;
  }

  function update(delta) {
    if (toastTimer > 0) {
      toastTimer -= delta;
      if (toastTimer <= 0) toast.classList.remove('visible');
    }
    const pad = readPad();
    if (!pad) {
      if (moving) { controls.setMoveAxis(0, 0); moving = false; }
      if (connected && !source) setConnected(false);
      prev.fill(false);
      return;
    }
    setConnected(true);
    const usedButton = onButtons(pad);
    if (blockerVisible()) {
      if (moving) { controls.setMoveAxis(0, 0); moving = false; }
      return;
    }
    const usedStick = onSticks(pad, delta);
    if ((usedButton || usedStick) && !engaged) {
      engaged = true;
      controls.engage({ pointerLock: false });
    }
  }

  function setSource(fn) {
    source = typeof fn === 'function' ? fn : null;
    prev.fill(false);
  }

  return { enabled, connected: () => connected, update, setSource, LOOK_RATE };
}
