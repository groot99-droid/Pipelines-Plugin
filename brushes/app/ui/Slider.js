/**
 * Slider.js - Custom Slider Component
 *
 * Keyboard accessible, real-time value display, reset on double-click.
 */

export class Slider {
  constructor(container, options = {}) {
    this.container = typeof container === 'string'
      ? document.querySelector(container)
      : container;

    this.options = {
      min: 0,
      max: 1,
      step: 0.01,
      value: 0,
      label: '',
      displayFormatter: (v) => v.toFixed(2),
      onChange: null,
      ...options
    };

    this.value = this.options.value;
    this.defaultValue = this.options.value;
    this.isDragging = false;

    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="slider-container">
        <div class="slider-header">
          <span class="slider-label">${this.options.label}</span>
          <span class="slider-value">${this.options.displayFormatter(this.value)}</span>
        </div>
        <div class="slider-track">
          <div class="slider-fill"></div>
          <div class="slider-thumb" tabindex="0" role="slider"
            aria-valuemin="${this.options.min}"
            aria-valuemax="${this.options.max}"
            aria-valuenow="${this.value}"
            aria-label="${this.options.label}"></div>
        </div>
      </div>
    `;

    this.track = this.container.querySelector('.slider-track');
    this.fill = this.container.querySelector('.slider-fill');
    this.thumb = this.container.querySelector('.slider-thumb');
    this.valueDisplay = this.container.querySelector('.slider-value');

    this.bindEvents();
    this.updateVisuals();
  }

  bindEvents() {
    this.thumb.addEventListener('mousedown', (e) => this.onDragStart(e));
    this.track.addEventListener('mousedown', (e) => this.onTrackClick(e));

    this.thumb.addEventListener('touchstart', (e) => this.onDragStart(e), { passive: false });
    this.track.addEventListener('touchstart', (e) => this.onTrackClick(e), { passive: false });

    this.container.addEventListener('dblclick', () => this.reset());

    this.thumb.addEventListener('keydown', (e) => this.onKeyDown(e));

    document.addEventListener('mousemove', (e) => this.onDragMove(e));
    document.addEventListener('mouseup', () => this.onDragEnd());
    document.addEventListener('touchmove', (e) => this.onDragMove(e), { passive: false });
    document.addEventListener('touchend', () => this.onDragEnd());
  }

  onDragStart(e) {
    e.preventDefault();
    this.isDragging = true;
    this.thumb.style.cursor = 'grabbing';
  }

  onDragMove(e) {
    if (!this.isDragging) return;

    e.preventDefault();

    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const rect = this.track.getBoundingClientRect();
    const percent = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));

    this.setValueFromPercent(percent);
  }

  onDragEnd() {
    if (this.isDragging) {
      this.isDragging = false;
      this.thumb.style.cursor = 'grab';
    }
  }

  onTrackClick(e) {
    if (e.target === this.thumb) return;

    const rect = this.track.getBoundingClientRect();
    const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));

    this.setValueFromPercent(percent);
  }

  onKeyDown(e) {
    const step = e.shiftKey ? this.options.step * 10 : this.options.step;

    switch (e.key) {
      case 'ArrowLeft':
      case 'ArrowDown':
        e.preventDefault();
        this.setValue(this.value - step);
        break;
      case 'ArrowRight':
      case 'ArrowUp':
        e.preventDefault();
        this.setValue(this.value + step);
        break;
      case 'Home':
        e.preventDefault();
        this.setValue(this.options.min);
        break;
      case 'End':
        e.preventDefault();
        this.setValue(this.options.max);
        break;
    }
  }

  setValueFromPercent(percent) {
    const range = this.options.max - this.options.min;
    let value = this.options.min + percent * range;

    value = Math.round(value / this.options.step) * this.options.step;

    this.setValue(value);
  }

  setValue(value, silent = false) {
    value = Math.max(this.options.min, Math.min(this.options.max, value));
    value = Math.round(value / this.options.step) * this.options.step;

    if (Math.abs(value - this.value) < this.options.step / 2) return;

    this.value = value;
    this.updateVisuals();

    if (!silent && this.options.onChange) {
      this.options.onChange(this.value);
    }
  }

  updateVisuals() {
    const range = this.options.max - this.options.min;
    const percent = (this.value - this.options.min) / range;

    this.fill.style.width = `${percent * 100}%`;
    this.thumb.style.left = `${percent * 100}%`;
    this.valueDisplay.textContent = this.options.displayFormatter(this.value);

    this.thumb.setAttribute('aria-valuenow', this.value);
  }

  reset() {
    this.setValue(this.defaultValue);
  }

  getValue() {
    return this.value;
  }

  setDefaultValue(value) {
    this.defaultValue = value;
  }

  destroy() {
    this.container.innerHTML = '';
  }
}

export default Slider;
