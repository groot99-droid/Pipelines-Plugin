/**
 * StrokeRenderer.js - Canvas-based Brush Stroke Simulator
 *
 * Renders brush strokes for the preview canvas. Simulates Procreate's brush
 * engine behaviour closely enough to judge a brush by.
 *
 * Three layers, composited into the visible canvas:
 *
 *   base  paper + the Light/Medium/Heavy sample strokes. Rebuilt on every
 *         parameter change, so it is the live readout of the settings.
 *   ink   strokes the operator has drawn and finished. Never rebuilt by a
 *         parameter change — retuning the brush must not wipe your test sheet.
 *   wet   the stroke currently under the pointer. Cleared and replaced by a
 *         full-engine pass when the stroke ends.
 *
 * The wet/ink split is what lets the live pass be fast and the committed pass
 * be correct: while you draw, stamps are laid down incrementally as the pointer
 * moves; on release the whole path is re-run through the same code the sample
 * strokes use, so what stays on the sheet is what the engine actually produces.
 */

export class StrokeRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.shapeCanvas = null;
    this.grainCanvas = null;

    this.offscreenCanvas = document.createElement('canvas');
    this.offscreenCtx = this.offscreenCanvas.getContext('2d');

    // Layers. Sized in setSize(); all three share one coordinate space in CSS px.
    this.base = this.makeLayer();
    this.ink = this.makeLayer();
    this.wet = this.makeLayer();

    this.width = 0;
    this.height = 0;
    this.scale = 1;

    // Ink history for stroke-level undo. Capped: a full-canvas ImageData is
    // ~1MB at this size, and an unbounded stack is a memory leak with a UI.
    this.inkHistory = [];
    this.inkHistoryMax = 12;

    this.lastBrushState = null;
    this.lastPressureLevels = ['light', 'medium', 'heavy'];
  }

  makeLayer() {
    const c = document.createElement('canvas');
    return { canvas: c, ctx: c.getContext('2d') };
  }

  setTextures(shapeCanvas, grainCanvas) {
    this.shapeCanvas = shapeCanvas;
    this.grainCanvas = grainCanvas;
  }

  /* ── Sizing ──────────────────────────────────────────────────────────────
     Backing stores are device pixels; every layer context carries a dpr
     transform so all drawing code below stays in CSS pixels, which is also
     the space pointer coordinates arrive in. */

  setSize(cssWidth, cssHeight) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(1, Math.floor(cssWidth));
    const h = Math.max(1, Math.floor(cssHeight));
    if (w === this.width && h === this.height && dpr === this.scale) return false;

    // Ink is the operator's work — preserve it across a resize rather than
    // silently dropping it when the window changes.
    const preserved = this.width > 0 ? this.ink.canvas.toDataURL() : null;

    this.width = w;
    this.height = h;
    this.scale = dpr;

    for (const layer of [this.base, this.ink, this.wet]) {
      layer.canvas.width = Math.floor(w * dpr);
      layer.canvas.height = Math.floor(h * dpr);
      layer.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    this.canvas.width = Math.floor(w * dpr);
    this.canvas.height = Math.floor(h * dpr);

    if (preserved) {
      const img = new Image();
      img.onload = () => {
        this.ink.ctx.save();
        this.ink.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ink.ctx.drawImage(img, 0, 0, this.ink.canvas.width, this.ink.canvas.height);
        this.ink.ctx.restore();
        this.composite();
      };
      img.src = preserved;
    }
    this.inkHistory = [];
    return true;
  }

  syncSizeToElement() {
    const rect = this.canvas.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      return this.setSize(rect.width, rect.height);
    }
    return false;
  }

  /* ── Compositing ─────────────────────────────────────────────────────── */

  composite() {
    const ctx = this.ctx;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
    ctx.drawImage(this.base.canvas, 0, 0);
    // Ink and wet are transparent sheets of dark stamps; multiply lands them on
    // the paper the same way a stamp drawn straight onto the paper would.
    ctx.globalCompositeOperation = 'multiply';
    ctx.drawImage(this.ink.canvas, 0, 0);
    ctx.drawImage(this.wet.canvas, 0, 0);
    ctx.restore();
  }

  /* ── Sample strokes (the base layer) ─────────────────────────────────── */

  render(brushState, pressureLevels = this.lastPressureLevels) {
    this.syncSizeToElement();
    this.lastBrushState = brushState;
    this.lastPressureLevels = pressureLevels;

    const ctx = this.base.ctx;
    ctx.fillStyle = '#F5F0E8';
    ctx.fillRect(0, 0, this.width, this.height);

    const strokeWidth = this.width * 0.8;
    const strokeX = (this.width - strokeWidth) / 2;

    const pressureValues = { light: 0.3, medium: 0.6, heavy: 1.0 };
    const strokeHeight = this.height / (pressureLevels.length + 1);

    pressureLevels.forEach((level, index) => {
      const y = strokeHeight * (index + 1);
      const pressure = pressureValues[level] || 0.5;
      const path = this.createSCurvePath(strokeX, y, strokeWidth, strokeHeight * 0.3);
      this.renderStrokeTo(ctx, path, brushState, pressure);
    });

    this.composite();
  }

  createSCurvePath(startX, centerY, width, amplitude) {
    const points = [];
    const steps = 100;
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const x = startX + width * t;
      const y = centerY + Math.sin(t * Math.PI * 2 - Math.PI / 2) * amplitude;
      points.push({ x, y, t });
    }
    return points;
  }

  /* ── Ink layer (committed operator strokes) ──────────────────────────── */

  /** Snapshot the ink layer so the stroke about to be drawn can be undone. */
  pushInkHistory() {
    if (!this.width) return;
    try {
      const snap = this.ink.ctx.getImageData(
        0, 0, this.ink.canvas.width, this.ink.canvas.height);
      this.inkHistory.push(snap);
      if (this.inkHistory.length > this.inkHistoryMax) this.inkHistory.shift();
    } catch {
      // getImageData can throw on a tainted canvas; undo degrades, drawing does not.
      this.inkHistory = [];
    }
  }

  canUndoInk() {
    return this.inkHistory.length > 0;
  }

  undoInk() {
    const snap = this.inkHistory.pop();
    if (!snap) return false;
    this.ink.ctx.save();
    this.ink.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ink.ctx.clearRect(0, 0, this.ink.canvas.width, this.ink.canvas.height);
    this.ink.ctx.putImageData(snap, 0, 0);
    this.ink.ctx.restore();
    this.composite();
    return true;
  }

  clearInk() {
    this.ink.ctx.clearRect(0, 0, this.width, this.height);
    this.wet.ctx.clearRect(0, 0, this.width, this.height);
    this.inkHistory = [];
    this.composite();
  }

  hasInk() {
    if (!this.width) return false;
    try {
      const d = this.ink.ctx.getImageData(
        0, 0, this.ink.canvas.width, this.ink.canvas.height).data;
      for (let i = 3; i < d.length; i += 4) if (d[i] !== 0) return true;
      return false;
    } catch {
      return this.inkHistory.length > 0;
    }
  }

  /* ── Live stroke (the wet layer) ─────────────────────────────────────── */

  clearWet() {
    this.wet.ctx.clearRect(0, 0, this.width, this.height);
  }

  /** Lay a single live stamp onto the wet layer. */
  stampWet(x, y, size, opacity, rotation, brushState) {
    this.drawStampTo(this.wet.ctx, x, y, size, opacity, rotation, brushState);
  }

  /**
   * Re-run the finished path through the full engine and bake it into ink.
   * The live wet pass is an approximation; this is the authoritative one.
   */
  commitStroke(path, brushState, basePressure = 1) {
    if (!path || path.length < 2) {
      this.clearWet();
      this.composite();
      return;
    }
    this.pushInkHistory();
    this.clearWet();
    this.renderStrokeTo(this.ink.ctx, path, brushState, basePressure);
    this.composite();
  }

  /* ── Engine ──────────────────────────────────────────────────────────── */

  renderStrokeTo(ctx, path, brushState, pressure) {
    if (!this.shapeCanvas) return;

    const stamps = this.computeStampPositions(
      path,
      brushState.brushSpacing,
      brushState.brushSpacingJitter,
      brushState.brushStreamline
    );

    stamps.forEach((stamp, index) => {
      const stampPressure = this.computeStampPressure(stamp, pressure, brushState, index, stamps.length);
      const stampSize = this.computeSize(brushState, stampPressure);
      const stampOpacity = this.computeOpacity(brushState, stampPressure);
      const rotation = this.computeRotation(brushState, stamp, path);
      const jx = (Math.random() - 0.5) * (brushState.brushJitterX || 0) * stampSize;
      const jy = (Math.random() - 0.5) * (brushState.brushJitterY || 0) * stampSize;
      this.drawStampTo(ctx, stamp.x + jx, stamp.y + jy, stampSize, stampOpacity, rotation, brushState);
    });
  }

  computeStampPositions(path, spacing, spacingJitter, streamline) {
    const stamps = [];
    let distanceAccumulator = 0;
    const baseSpacing = Math.max(2, 20 * spacing);
    // A path carrying per-point input pressure came from a real pointer, and the
    // device already encodes how the stroke starts and ends. Synthesising an
    // extra taper on top of that thins every deliberate hard start.
    const hasInput = path.some(p => typeof p.p === 'number');

    stamps.push({ ...path[0], pressure: hasInput ? (path[0].p ?? 1) : 1, input: path[0].p });

    let lastStampPoint = path[0];

    for (let i = 1; i < path.length; i++) {
      const point = path[i];
      const prevPoint = path[i - 1];

      const dx = point.x - lastStampPoint.x;
      const dy = point.y - lastStampPoint.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      distanceAccumulator += distance;

      const jitteredSpacing = baseSpacing * (1 + (Math.random() - 0.5) * spacingJitter * 2);

      if (distanceAccumulator >= jitteredSpacing) {
        const segment = Math.hypot(point.x - prevPoint.x, point.y - prevPoint.y);
        const excess = distanceAccumulator - jitteredSpacing;
        const ratio = segment > 0 ? Math.max(0, (segment - excess) / segment) : 1;

        const stampX = prevPoint.x + (point.x - prevPoint.x) * ratio;
        const stampY = prevPoint.y + (point.y - prevPoint.y) * ratio;

        const t = i / path.length;
        const input = typeof point.p === 'number'
          ? (prevPoint.p ?? point.p) + ((point.p - (prevPoint.p ?? point.p)) * ratio)
          : undefined;

        stamps.push({
          x: stampX,
          y: stampY,
          t,
          pressure: hasInput ? 1 : this.getEdgePressure(t),
          input
        });

        lastStampPoint = { x: stampX, y: stampY };
        distanceAccumulator = excess;
      }
    }

    const last = path[path.length - 1];
    stamps.push({ ...last, t: 1, pressure: hasInput ? (last.p ?? 0) : 0, input: last.p });

    return stamps;
  }

  getEdgePressure(t) {
    const startTaper = 0.1;
    const endTaper = 0.1;
    if (t < startTaper) return t / startTaper;
    if (t > 1 - endTaper) return (1 - t) / endTaper;
    return 1;
  }

  computeStampPressure(stamp, basePressure, brushState) {
    const input = typeof stamp.input === 'number' ? stamp.input : basePressure;
    let pressure = input * stamp.pressure;

    const taperStart = brushState.brushTaperSizeStart;
    const taperEnd = brushState.brushTaperSizeEnd;

    if (taperStart > 0 && stamp.t < 0.2) {
      pressure *= 1 - taperStart * (1 - stamp.t / 0.2);
    }
    if (taperEnd > 0 && stamp.t > 0.8) {
      pressure *= 1 - taperEnd * (1 - (1 - stamp.t) / 0.2);
    }

    return Math.max(0, Math.min(1, pressure));
  }

  computeSize(brushState, pressure) {
    const minSize = brushState.brushSizeMinimum;
    const maxSize = brushState.brushSizeMaximum;
    const baseSize = minSize + (maxSize - minSize) * pressure;
    return 50 * baseSize;
  }

  computeOpacity(brushState, pressure) {
    const minOpacity = brushState.brushOpacityMinimum;
    const maxOpacity = brushState.brushOpacityMaximum;
    return minOpacity + (maxOpacity - minOpacity) * pressure;
  }

  computeRotation(brushState, stamp, path) {
    let rotation = brushState.brushShapeRotation;

    if (brushState.brushAzimuth) {
      const idx = Math.floor(stamp.t * (path.length - 1));
      const current = path[Math.min(idx, path.length - 1)];
      const next = path[Math.min(idx + 1, path.length - 1)];
      rotation += Math.atan2(next.y - current.y, next.x - current.x);
    }
    if (brushState.brushShapeScatter > 0) {
      rotation += (Math.random() - 0.5) * brushState.brushShapeScatter * Math.PI;
    }
    return rotation;
  }

  drawStampTo(ctx, x, y, size, opacity, rotation, brushState) {
    if (!this.shapeCanvas || size <= 0 || opacity <= 0) return;

    ctx.save();
    ctx.globalCompositeOperation = 'multiply';
    ctx.globalAlpha = opacity;
    ctx.translate(x, y);
    ctx.rotate(rotation);
    ctx.drawImage(this.shapeCanvas, -size / 2, -size / 2, size, size);
    ctx.restore();

    if (this.grainCanvas && brushState.brushGrainDepth > 0) {
      this.applyGrainTo(ctx, x, y, size, opacity, rotation, brushState.brushGrainDepth);
    }
  }

  applyGrainTo(ctx, x, y, size, opacity, rotation, grainDepth) {
    const grainSize = Math.max(2, Math.round(size * 2));
    this.offscreenCanvas.width = grainSize;
    this.offscreenCanvas.height = grainSize;

    this.offscreenCtx.clearRect(0, 0, grainSize, grainSize);
    this.offscreenCtx.drawImage(
      this.grainCanvas,
      0, 0, this.grainCanvas.width, this.grainCanvas.height,
      0, 0, grainSize, grainSize
    );

    ctx.save();
    ctx.globalCompositeOperation = 'multiply';
    ctx.globalAlpha = opacity * grainDepth;
    ctx.translate(x, y);
    ctx.rotate(rotation);
    ctx.drawImage(this.offscreenCanvas, -grainSize / 2, -grainSize / 2, grainSize, grainSize);
    ctx.restore();
  }

  /* ── Compatibility ───────────────────────────────────────────────────── */

  /** Kept for callers that only want the paper back. Ink is untouched. */
  clear() {
    this.base.ctx.fillStyle = '#F5F0E8';
    this.base.ctx.fillRect(0, 0, this.width, this.height);
    this.composite();
  }

  resize(width, height) {
    this.setSize(width, height);
  }
}

export default StrokeRenderer;
