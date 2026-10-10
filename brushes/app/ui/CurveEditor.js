/**
 * CurveEditor.js - Bezier Pressure/Tilt Curve Editor
 *
 * Interactive canvas for editing response curves.
 * Exports serialized 4-point bezier arrays.
 */

export class CurveEditor {
  constructor(canvas, options = {}) {
    this.canvas = typeof canvas === 'string'
      ? document.querySelector(canvas)
      : canvas;

    this.ctx = this.canvas.getContext('2d');

    this.options = {
      width: 400,
      height: 160,
      onChange: null,
      ...options
    };

    this.canvas.width = this.options.width;
    this.canvas.height = this.options.height;

    // Control points (x, y) normalized 0-1 - start at linear
    this.points = [
      { x: 0, y: 0 },
      { x: 0.33, y: 0.33 },
      { x: 0.67, y: 0.67 },
      { x: 1, y: 1 }
    ];

    this.draggedPoint = null;
    this.pointRadius = 8;
    this.hoverPoint = null;

    this.init();
  }

  init() {
    this.bindEvents();
    this.draw();
  }

  bindEvents() {
    this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
    this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
    this.canvas.addEventListener('mouseup', () => this.onMouseUp());
    this.canvas.addEventListener('mouseleave', () => this.onMouseUp());

    this.canvas.addEventListener('touchstart', (e) => this.onTouchStart(e), { passive: false });
    this.canvas.addEventListener('touchmove', (e) => this.onTouchMove(e), { passive: false });
    this.canvas.addEventListener('touchend', () => this.onMouseUp());
  }

  getMousePos(e) {
    const rect = this.canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;

    return {
      x: (clientX - rect.left) * (this.canvas.width / rect.width),
      y: (clientY - rect.top) * (this.canvas.height / rect.height)
    };
  }

  onMouseDown(e) {
    const pos = this.getMousePos(e);
    const point = this.getPointAt(pos);

    if (point !== null && point !== 0 && point !== 3) {
      this.draggedPoint = point;
    }
  }

  onMouseMove(e) {
    const pos = this.getMousePos(e);

    if (this.draggedPoint !== null) {
      this.points[this.draggedPoint].x = Math.max(0, Math.min(1, pos.x / this.canvas.width));
      this.points[this.draggedPoint].y = 1 - Math.max(0, Math.min(1, pos.y / this.canvas.height));

      this.draw();

      if (this.options.onChange) {
        this.options.onChange(this.getCurveData());
      }
    } else {
      const point = this.getPointAt(pos);
      this.hoverPoint = point;
      this.canvas.style.cursor = point !== null && point !== 0 && point !== 3
        ? 'move'
        : 'crosshair';
      this.draw();
    }
  }

  onMouseUp() {
    this.draggedPoint = null;
  }

  onTouchStart(e) {
    e.preventDefault();
    this.onMouseDown(e);
  }

  onTouchMove(e) {
    e.preventDefault();
    this.onMouseMove(e);
  }

  getPointAt(pos) {
    for (let i = 0; i < this.points.length; i++) {
      const px = this.points[i].x * this.canvas.width;
      const py = (1 - this.points[i].y) * this.canvas.height;

      const dx = pos.x - px;
      const dy = pos.y - py;

      if (Math.sqrt(dx * dx + dy * dy) < this.pointRadius * 2) {
        return i;
      }
    }
    return null;
  }

  draw() {
    const { width, height } = this.canvas;

    this.ctx.fillStyle = '#000000';
    this.ctx.fillRect(0, 0, width, height);

    this.drawGrid();
    this.drawCurve();
    this.drawPoints();
  }

  drawGrid() {
    const { width, height } = this.canvas;

    this.ctx.strokeStyle = '#1F1F1F';
    this.ctx.lineWidth = 1;

    for (let i = 1; i < 4; i++) {
      const x = (width / 4) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, height);
      this.ctx.stroke();
    }

    for (let i = 1; i < 4; i++) {
      const y = (height / 4) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(width, y);
      this.ctx.stroke();
    }

    this.ctx.strokeStyle = '#383838';
    this.ctx.setLineDash([5, 5]);
    this.ctx.beginPath();
    this.ctx.moveTo(0, height);
    this.ctx.lineTo(width, 0);
    this.ctx.stroke();
    this.ctx.setLineDash([]);
  }

  drawCurve() {
    const { width, height } = this.canvas;

    this.ctx.strokeStyle = '#00E5FF';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();

    this.ctx.moveTo(this.points[0].x * width, (1 - this.points[0].y) * height);
    this.ctx.bezierCurveTo(
      this.points[1].x * width, (1 - this.points[1].y) * height,
      this.points[2].x * width, (1 - this.points[2].y) * height,
      this.points[3].x * width, (1 - this.points[3].y) * height
    );
    this.ctx.stroke();
  }

  drawPoints() {
    const { width, height } = this.canvas;

    for (let i = 0; i < this.points.length; i++) {
      const x = this.points[i].x * width;
      const y = (1 - this.points[i].y) * height;

      const isFixed = i === 0 || i === 3;

      this.ctx.fillStyle = isFixed ? '#6E6E6E' : '#00E5FF';
      if (this.hoverPoint === i) {
        this.ctx.fillStyle = '#FFFFFF';
      }

      this.ctx.beginPath();
      this.ctx.arc(x, y, this.pointRadius, 0, Math.PI * 2);
      this.ctx.fill();

      this.ctx.fillStyle = '#000000';
      this.ctx.beginPath();
      this.ctx.arc(x, y, this.pointRadius - 3, 0, Math.PI * 2);
      this.ctx.fill();
    }
  }

  getCurveData() {
    return [
      this.points[0].x, this.points[0].y,
      this.points[1].x, this.points[1].y,
      this.points[2].x, this.points[2].y,
      this.points[3].x, this.points[3].y
    ];
  }

  setCurveData(data) {
    if (!data || data.length !== 8) return;

    for (let i = 0; i < 4; i++) {
      this.points[i].x = data[i * 2];
      this.points[i].y = data[i * 2 + 1];
    }

    this.draw();
  }

  loadPreset(preset) {
    switch (preset) {
      case 'linear':
        this.points = [
          { x: 0, y: 0 },
          { x: 0.33, y: 0.33 },
          { x: 0.67, y: 0.67 },
          { x: 1, y: 1 }
        ];
        break;
      case 'easeIn':
        this.points = [
          { x: 0, y: 0 },
          { x: 0.42, y: 0 },
          { x: 0.67, y: 0.67 },
          { x: 1, y: 1 }
        ];
        break;
      case 'easeOut':
        this.points = [
          { x: 0, y: 0 },
          { x: 0.33, y: 0.33 },
          { x: 0.58, y: 1 },
          { x: 1, y: 1 }
        ];
        break;
      case 'heavyPressure':
        this.points = [
          { x: 0, y: 0 },
          { x: 0.2, y: 0.1 },
          { x: 0.5, y: 0.3 },
          { x: 1, y: 1 }
        ];
        break;
      case 'lightTouch':
        this.points = [
          { x: 0, y: 0 },
          { x: 0.5, y: 0.7 },
          { x: 0.8, y: 0.9 },
          { x: 1, y: 1 }
        ];
        break;
      case 'sCurve':
        this.points = [
          { x: 0, y: 0 },
          { x: 0.25, y: 0.1 },
          { x: 0.75, y: 0.9 },
          { x: 1, y: 1 }
        ];
        break;
    }

    this.draw();

    if (this.options.onChange) {
      this.options.onChange(this.getCurveData());
    }
  }

  destroy() {
    // Clean up
  }
}

export default CurveEditor;
