/**
 * StrokeInput.js - Pointer input for the preview canvas
 *
 * Turns the preview from a picture of the brush into the brush. Draw on it with
 * a mouse, a finger, or a pen; the settings in the sidebar are what you are
 * drawing with, live.
 *
 * Two passes per stroke:
 *   while drawing  stamps are laid incrementally onto the renderer's wet layer
 *                  as the pointer moves — cheap, so it keeps up with the hand.
 *   on release     the whole recorded path is handed to StrokeRenderer.commitStroke,
 *                  which re-runs it through the same engine that draws the sample
 *                  strokes. What stays on the sheet is what the engine produces,
 *                  not what the fast path approximated.
 *
 * Pressure comes from the device when the device has any (`pointerType === 'pen'`).
 * A mouse reports a constant 0.5, which would draw a dead, uniform line — so for
 * mouse and touch, speed stands in for pressure: fast is light, slow is heavy.
 * That is a substitution, and the readout says which one is in force rather than
 * implying the mouse has a pressure sensor.
 */

const MOUSE_FAST = 2.4;   // px/ms treated as "as fast as it gets"
const MOUSE_FLOOR = 0.35; // lightest a speed-derived stroke goes
const MOUSE_CEIL = 1.0;

export class StrokeInput {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {import('./StrokeRenderer.js').StrokeRenderer} renderer
   * @param {() => object} getBrushState
   * @param {object} [handlers]
   * @param {(info: object) => void} [handlers.onStatus]
   * @param {() => void} [handlers.onStrokeEnd]
   */
  constructor(canvas, renderer, getBrushState, handlers = {}) {
    this.canvas = canvas;
    this.renderer = renderer;
    this.getBrushState = getBrushState;
    this.handlers = handlers;

    this.drawing = false;
    this.pointerId = null;
    this.path = [];
    this.smooth = null;
    this.lastStamp = null;
    this.accumulator = 0;
    this.lastEventTime = 0;
    this.speedPressure = 0.8;
    this.pointerType = 'mouse';
    this.lastPressure = 0;
    this.hover = null;

    this.enabled = true;

    this.bind();
  }

  bind() {
    const c = this.canvas;
    c.style.touchAction = 'none';
    c.addEventListener('pointerdown', e => this.onDown(e));
    c.addEventListener('pointermove', e => this.onMove(e));
    c.addEventListener('pointerup', e => this.onUp(e));
    c.addEventListener('pointercancel', e => this.onUp(e));
    c.addEventListener('pointerleave', e => this.onLeave(e));
    c.addEventListener('pointerenter', e => this.onEnter(e));
    // The canvas takes focus so the stroke surface is reachable and its focus
    // ring visible; Escape abandons a stroke in progress.
    c.addEventListener('keydown', e => {
      if (e.key === 'Escape' && this.drawing) this.abort();
    });
  }

  setEnabled(on) {
    this.enabled = on;
    this.canvas.classList.toggle('is-drawable', on);
  }

  /* ── Coordinates ─────────────────────────────────────────────────────── */

  toLocal(e) {
    const r = this.canvas.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }

  /* ── Pressure ────────────────────────────────────────────────────────── */

  pressureFor(e, pt, now) {
    if (e.pointerType === 'pen' && e.pressure > 0) {
      return Math.max(0.02, Math.min(1, e.pressure));
    }
    // Speed substitute. Smoothed hard, or the line flickers between weights on
    // the natural jitter of a hand moving a mouse.
    if (this.lastStamp && now > this.lastEventTime) {
      const dist = Math.hypot(pt.x - this.lastStamp.x, pt.y - this.lastStamp.y);
      const speed = dist / Math.max(1, now - this.lastEventTime);
      const target = MOUSE_CEIL - Math.min(1, speed / MOUSE_FAST) * (MOUSE_CEIL - MOUSE_FLOOR);
      this.speedPressure += (target - this.speedPressure) * 0.25;
    }
    return Math.max(MOUSE_FLOOR, Math.min(MOUSE_CEIL, this.speedPressure));
  }

  /* ── Stroke lifecycle ────────────────────────────────────────────────── */

  onDown(e) {
    if (!this.enabled || e.button !== 0) return;
    e.preventDefault();
    this.canvas.focus({ preventScroll: true });
    this.canvas.setPointerCapture(e.pointerId);

    const pt = this.toLocal(e);
    const now = performance.now();

    this.drawing = true;
    this.pointerId = e.pointerId;
    this.pointerType = e.pointerType || 'mouse';
    this.speedPressure = 0.8;
    this.lastEventTime = now;
    this.lastStamp = { x: pt.x, y: pt.y };
    this.smooth = { x: pt.x, y: pt.y };
    this.accumulator = 0;

    const p = this.pressureFor(e, pt, now);
    this.lastPressure = p;
    this.path = [{ x: pt.x, y: pt.y, p }];

    this.renderer.clearWet();
    this.stampAt(pt.x, pt.y, p, 0);
    this.renderer.composite();
    this.report();
  }

  onMove(e) {
    if (!this.enabled) return;
    const pt = this.toLocal(e);

    if (!this.drawing || e.pointerId !== this.pointerId) {
      this.hover = pt;
      this.report();
      return;
    }
    e.preventDefault();

    // Coalesced events recover the samples the browser batched into one move —
    // without them a fast stroke is a polyline between widely spaced points.
    const events = typeof e.getCoalescedEvents === 'function'
      ? e.getCoalescedEvents()
      : [e];

    for (const ev of (events.length ? events : [e])) {
      this.consume(ev);
    }

    this.hover = pt;
    this.renderer.composite();
    this.report();
  }

  consume(e) {
    const raw = this.toLocal(e);
    const now = performance.now();
    const state = this.getBrushState();

    // StreamLine: pull the drawn point toward the raw point rather than jumping
    // to it. This is the same knob the exported brush carries, so tuning it here
    // is tuning the thing you ship.
    const streamline = Math.max(0, Math.min(0.98, state.brushStreamline || 0));
    const k = Math.max(0.06, 1 - streamline * 0.92);
    this.smooth = {
      x: this.smooth.x + (raw.x - this.smooth.x) * k,
      y: this.smooth.y + (raw.y - this.smooth.y) * k
    };

    const p = this.pressureFor(e, this.smooth, now);
    this.lastEventTime = now;
    this.lastPressure = p;

    const from = this.lastStamp;
    const to = this.smooth;
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const dist = Math.hypot(dx, dy);
    if (dist < 0.01) return;

    const angle = Math.atan2(dy, dx);
    const spacing = Math.max(2, 20 * (state.brushSpacing ?? 0.05));
    const jitter = state.brushSpacingJitter ?? 0;

    // Walk the segment laying a stamp every `spacing` px, carrying the leftover
    // distance into the next segment so spacing is continuous across events
    // rather than restarting at every pointermove.
    let walked = 0;
    for (;;) {
      const step = spacing * (1 + (Math.random() - 0.5) * jitter * 2);
      const need = Math.max(0.01, step - this.accumulator);
      if (walked + need > dist) break;
      walked += need;
      this.accumulator = 0;
      this.stampAt(
        from.x + Math.cos(angle) * walked,
        from.y + Math.sin(angle) * walked,
        p, angle
      );
    }
    this.accumulator += dist - walked;
    this.lastStamp = { x: to.x, y: to.y };
    this.path.push({ x: to.x, y: to.y, p });
  }

  stampAt(x, y, pressure, angle) {
    const state = this.getBrushState();
    const r = this.renderer;

    const size = r.computeSize(state, pressure);
    const opacity = r.computeOpacity(state, pressure);

    let rotation = state.brushShapeRotation || 0;
    if (state.brushAzimuth) rotation += angle;
    if (state.brushShapeScatter > 0) {
      rotation += (Math.random() - 0.5) * state.brushShapeScatter * Math.PI;
    }
    const jx = (Math.random() - 0.5) * (state.brushJitterX || 0) * size;
    const jy = (Math.random() - 0.5) * (state.brushJitterY || 0) * size;

    r.stampWet(x + jx, y + jy, size, opacity, rotation, state);
  }

  onUp(e) {
    if (!this.drawing || e.pointerId !== this.pointerId) return;
    this.drawing = false;
    try { this.canvas.releasePointerCapture(e.pointerId); } catch { /* already released */ }

    const path = this.path;
    this.path = [];
    this.pointerId = null;

    if (path.length < 2) {
      // A tap is a single stamp, and the fast path already drew it correctly.
      this.renderer.pushInkHistory();
      const state = this.getBrushState();
      const p = path[0]?.p ?? 1;
      const size = this.renderer.computeSize(state, p);
      const opacity = this.renderer.computeOpacity(state, p);
      this.renderer.drawStampTo(
        this.renderer.ink.ctx, path[0].x, path[0].y, size, opacity,
        state.brushShapeRotation || 0, state);
      this.renderer.clearWet();
      this.renderer.composite();
    } else {
      this.renderer.commitStroke(path, this.getBrushState(), 1);
    }

    this.report();
    if (this.handlers.onStrokeEnd) this.handlers.onStrokeEnd();
  }

  abort() {
    this.drawing = false;
    this.path = [];
    this.pointerId = null;
    this.renderer.clearWet();
    this.renderer.composite();
    this.report();
  }

  onEnter(e) {
    this.pointerType = e.pointerType || 'mouse';
    this.hover = this.toLocal(e);
    this.report();
  }

  onLeave() {
    this.hover = null;
    this.report();
  }

  /* ── Readout ─────────────────────────────────────────────────────────── */

  report() {
    if (!this.handlers.onStatus) return;
    const state = this.getBrushState();
    this.handlers.onStatus({
      hover: this.hover,
      drawing: this.drawing,
      pointerType: this.pointerType,
      pressure: this.drawing ? this.lastPressure : null,
      // The cursor ring shows the widest the brush goes, which is the number you
      // are actually judging when you set Size Maximum.
      diameter: this.renderer.computeSize(state, 1),
      pressureSource: this.pointerType === 'pen' ? 'pen' : 'speed'
    });
  }
}

export default StrokeInput;
