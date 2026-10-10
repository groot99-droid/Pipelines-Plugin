/**
 * PanelComponents.js - All Brush Studio Panel Components
 *
 * Creates the UI for each of the 11 brush studio panels.
 *
 * Every panel is a stack of collapsible sections (ui/Section.js) rather than one
 * long list of sliders. Eleven panels x up to nine controls is more than fits on
 * a laptop sidebar, and scrolling past the four groups you are not tuning to
 * reach the one you are is the whole problem. Open/closed state persists, so the
 * shape you leave the sidebar in is the shape you come back to.
 */

import { Slider } from '../ui/Slider.js';
import { CurveEditor } from '../ui/CurveEditor.js';
import { Section, createSectionToolbar } from '../ui/Section.js';
import { generateShape, getShapeGeneratorNames } from '../generators/ShapeGenerator.js';
import { generateGrain, getGrainGeneratorNames } from '../generators/GrainGenerator.js';
import { BLENDING_MODES } from '../editor/BrushState.js';
import { Modal } from '../ui/Modal.js';

const pct = v => `${Math.round((v ?? 0) * 100)}%`;

/**
 * Base panel class
 */
export class BasePanel {
  constructor(container, brushState, onChange) {
    this.container = container;
    this.brushState = brushState;
    this.onChange = onChange;
    this.sliders = [];
    this.sections = [];
    this.toolbar = null;
  }

  /* ── Structure ───────────────────────────────────────────────────────── */

  /** Panel title + the expand/collapse-all control that governs its sections. */
  beginPanel(titleText) {
    this.clear();

    const title = document.createElement('div');
    title.className = 'panel-title';
    title.textContent = titleText;
    this.container.appendChild(title);

    this.toolbar = createSectionToolbar(() => this.sections);
    this.container.appendChild(this.toolbar);
  }

  /**
   * @param {string} id     stable persistence key, `panel.section`
   * @param {string} title
   * @param {object} [opts] {hint, defaultOpen}
   */
  createSection(id, title, opts = {}) {
    const section = new Section({ id, title, ...opts });
    section.header.addEventListener('click', () => this.toolbar && this.toolbar.sync());
    this.sections.push(section);
    this.container.appendChild(section.el);
    return section;
  }

  endPanel() {
    if (this.toolbar) this.toolbar.sync();
  }

  /* ── Controls ────────────────────────────────────────────────────────── */

  createSlider(key, label, options = {}) {
    const container = document.createElement('div');

    const slider = new Slider(container, {
      label,
      min: options.min ?? 0,
      max: options.max ?? 1,
      step: options.step ?? 0.01,
      value: this.brushState.get(key),
      displayFormatter: options.formatter || (v => `${(v * 100).toFixed(0)}%`),
      onChange: (value) => {
        this.brushState.set(key, value);
        if (this.onChange) this.onChange(key, value);
      }
    });

    this.sliders.push({ key, slider });
    return container;
  }

  createToggle(key, label) {
    const container = document.createElement('div');
    container.className = 'toggle-container';

    const value = this.brushState.get(key);

    container.innerHTML = `
      <span class="toggle-label">${label}</span>
      <button type="button" class="toggle-switch ${value ? 'active' : ''}"
              role="switch" aria-checked="${value ? 'true' : 'false'}"
              aria-label="${label}" data-key="${key}">
        <span class="toggle-thumb"></span>
      </button>
    `;

    const toggle = container.querySelector('.toggle-switch');
    toggle.addEventListener('click', () => {
      const newValue = !toggle.classList.contains('active');
      toggle.classList.toggle('active', newValue);
      toggle.setAttribute('aria-checked', newValue ? 'true' : 'false');
      this.brushState.set(key, newValue);
      if (this.onChange) this.onChange(key, newValue);
    });

    return container;
  }

  createDropdown(key, label, options) {
    const container = document.createElement('div');
    container.className = 'dropdown-container';

    const select = document.createElement('select');
    select.className = 'dropdown-select';

    options.forEach(opt => {
      const option = document.createElement('option');
      option.value = opt.value;
      option.textContent = opt.label;
      if (opt.value === this.brushState.get(key)) {
        option.selected = true;
      }
      select.appendChild(option);
    });

    select.addEventListener('change', () => {
      const value = parseInt(select.value);
      this.brushState.set(key, value);
      if (this.onChange) this.onChange(key, value);
    });

    const labelEl = document.createElement('label');
    labelEl.className = 'dropdown-label';
    labelEl.textContent = label;

    container.appendChild(labelEl);
    container.appendChild(select);

    return container;
  }

  /** A generator picker: one button per source, current one carrying the state. */
  createGeneratorSelect(stateKey, names, onPick) {
    const wrap = document.createElement('div');
    wrap.className = 'generator-select';
    const current = this.brushState.get(stateKey);

    names.forEach(name => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'generator-btn' + (name === current ? ' active' : '');
      btn.setAttribute('aria-pressed', String(name === current));
      btn.textContent = name;
      btn.addEventListener('click', () => {
        wrap.querySelectorAll('.generator-btn').forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
        this.brushState.set(stateKey, name);
        onPick(name);
      });
      wrap.appendChild(btn);
    });

    return wrap;
  }

  /** A read-only key/value table. Rows are [label, value] pairs. */
  createSpecTable(rows) {
    const table = document.createElement('table');
    table.className = 'spec-table';
    const body = document.createElement('tbody');
    rows.forEach(([k, v]) => {
      const tr = document.createElement('tr');
      const th = document.createElement('th');
      th.scope = 'row';
      th.textContent = k;
      const td = document.createElement('td');
      td.textContent = v;
      tr.appendChild(th);
      tr.appendChild(td);
      body.appendChild(tr);
    });
    table.appendChild(body);
    return table;
  }

  updateSliders() {
    this.sliders.forEach(({ key, slider }) => {
      slider.setValue(this.brushState.get(key), true);
    });
  }

  clear() {
    this.sliders = [];
    this.sections = [];
    this.toolbar = null;
    this.container.innerHTML = '';
  }
}

/**
 * Stroke Path Panel
 */
export class StrokePathPanel extends BasePanel {
  render() {
    this.beginPanel('Stroke Path');

    this.createSection('stroke.spacing', 'Spacing', { hint: pct(this.brushState.get('brushSpacing')) })
      .add(
        this.createSlider('brushSpacing', 'Spacing', {
          min: 0, max: 5, step: 0.01,
          formatter: v => `${(v * 100).toFixed(0)}%`
        }),
        this.createSlider('brushSpacingJitter', 'Spacing Jitter'),
        this.createSlider('brushFallOff', 'Fall Off')
      );

    this.createSection('stroke.smoothing', 'Smoothing', { hint: pct(this.brushState.get('brushStreamline')) })
      .add(
        this.createSlider('brushStreamline', 'StreamLine'),
        this.createSlider('brushStreamlinePressure', 'StreamLine Pressure'),
        this.createSlider('brushStabilization', 'Stabilization'),
        this.createSlider('brushMotionFiltering', 'Motion Filtering')
      );

    this.createSection('stroke.jitter', 'Jitter', { defaultOpen: false })
      .add(
        this.createSlider('brushJitterX', 'Jitter X'),
        this.createSlider('brushJitterY', 'Jitter Y')
      );

    this.endPanel();
  }
}

/**
 * Taper Panel
 */
export class TaperPanel extends BasePanel {
  render() {
    this.beginPanel('Taper');

    this.createSection('taper.size', 'Size')
      .add(
        this.createSlider('brushTaperSizeStart', 'Size Start'),
        this.createSlider('brushTaperSizeEnd', 'Size End'),
        this.createSlider('brushTaperTip', 'Tip')
      );

    this.createSection('taper.opacity', 'Opacity')
      .add(this.createSlider('brushTaperOpacity', 'Opacity'));

    this.createSection('taper.options', 'Options')
      .add(this.createToggle('brushTaperLinked', 'Linked'));

    this.endPanel();
  }
}

/**
 * Shape Panel
 */
export class ShapePanel extends BasePanel {
  render(shapeCanvas, onShapeChange) {
    this.shapeCanvas = shapeCanvas;
    this.onShapeChange = onShapeChange;

    this.beginPanel('Shape');

    const sourceSection = this.createSection('shape.source', 'Source', {
      hint: this.brushState.get('shapeSource')
    });
    sourceSection.add(
      this.createGeneratorSelect('shapeSource', getShapeGeneratorNames(), (name) => {
        sourceSection.setHint(name);
        this.generateShape(name);
      })
    );

    this.createSection('shape.placement', 'Placement')
      .add(
        this.createSlider('brushShapeScatter', 'Scatter', {
          max: 2, formatter: v => `${(v * 100).toFixed(0)}%`
        }),
        this.createSlider('brushShapeRotation', 'Rotation', {
          max: 6.283, formatter: v => `${(v * 57.2958).toFixed(0)}°`
        }),
        this.createSlider('brushShapeCount', 'Count', {
          min: 1, max: 16, step: 1, formatter: v => v.toFixed(0)
        }),
        this.createSlider('brushShapeCountJitter', 'Count Jitter')
      );

    this.createSection('shape.orientation', 'Orientation', { defaultOpen: false })
      .add(
        this.createToggle('brushShapeRandomized', 'Randomized'),
        this.createToggle('brushAzimuth', 'Azimuth'),
        this.createToggle('brushFlipX', 'Flip X'),
        this.createToggle('brushFlipY', 'Flip Y')
      );

    this.endPanel();
  }

  generateShape(generatorName) {
    const canvas = generateShape(generatorName, 512);
    const ctx = this.shapeCanvas.getContext('2d');
    ctx.clearRect(0, 0, this.shapeCanvas.width, this.shapeCanvas.height);
    ctx.drawImage(canvas, 0, 0);
    if (this.onShapeChange) this.onShapeChange();
  }
}

/**
 * Grain Panel
 */
export class GrainPanel extends BasePanel {
  render(grainCanvas, onGrainChange) {
    this.grainCanvas = grainCanvas;
    this.onGrainChange = onGrainChange;

    this.beginPanel('Grain');

    const sourceSection = this.createSection('grain.source', 'Source', {
      hint: this.brushState.get('grainSource')
    });
    sourceSection.add(
      this.createGeneratorSelect('grainSource', getGrainGeneratorNames(), (name) => {
        sourceSection.setHint(name);
        this.generateGrain(name);
      })
    );

    this.createSection('grain.transform', 'Transform')
      .add(
        this.createSlider('brushGrainScale', 'Scale', {
          max: 2, formatter: v => `${(v * 100).toFixed(0)}%`
        }),
        this.createSlider('brushGrainRotation', 'Rotation', {
          max: 6.283, formatter: v => `${(v * 57.2958).toFixed(0)}°`
        })
      );

    this.createSection('grain.depth', 'Depth', { hint: pct(this.brushState.get('brushGrainDepth')) })
      .add(
        this.createSlider('brushGrainDepth', 'Depth'),
        this.createSlider('brushGrainDepthMin', 'Depth Min'),
        this.createSlider('brushGrainDepthJitter', 'Depth Jitter'),
        this.createSlider('brushGrainOffsetJitter', 'Offset Jitter')
      );

    this.createSection('grain.behaviour', 'Behaviour', { defaultOpen: false })
      .add(
        this.createToggle('brushGrainMoving', 'Moving'),
        this.createToggle('brushGrainZoom', 'Zoom')
      );

    this.endPanel();
  }

  generateGrain(generatorName) {
    const canvas = generateGrain(generatorName, 1024);
    const ctx = this.grainCanvas.getContext('2d');
    ctx.clearRect(0, 0, this.grainCanvas.width, this.grainCanvas.height);
    ctx.drawImage(canvas, 0, 0);
    if (this.onGrainChange) this.onGrainChange();
  }
}

/**
 * Dynamics Panel
 */
export class DynamicsPanel extends BasePanel {
  render() {
    this.beginPanel('Dynamics');

    const sizeHint = `${pct(this.brushState.get('brushSizeMinimum'))} – ${pct(this.brushState.get('brushSizeMaximum'))}`;
    this.createSection('dynamics.size', 'Size', { hint: sizeHint })
      .add(
        this.createSlider('brushSizeMaximum', 'Maximum'),
        this.createSlider('brushSizeMinimum', 'Minimum')
      );

    const opacityHint = `${pct(this.brushState.get('brushOpacityMinimum'))} – ${pct(this.brushState.get('brushOpacityMaximum'))}`;
    this.createSection('dynamics.opacity', 'Opacity', { hint: opacityHint })
      .add(
        this.createSlider('brushOpacityMaximum', 'Maximum'),
        this.createSlider('brushOpacityMinimum', 'Minimum')
      );

    this.createSection('dynamics.bleed', 'Bleed', { defaultOpen: false })
      .add(this.createSlider('brushBleedAmount', 'Bleed Amount'));

    this.endPanel();
  }
}

/**
 * Pencil Panel (Pressure & Tilt)
 */
export class PencilPanel extends BasePanel {
  render() {
    this.beginPanel('Apple Pencil');

    const curvePresets = (apply) => {
      const wrap = document.createElement('div');
      wrap.className = 'curve-presets';
      ['linear', 'easeIn', 'easeOut', 'heavyPressure', 'lightTouch', 'sCurve'].forEach(preset => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'curve-preset-btn';
        btn.textContent = preset.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase());
        btn.addEventListener('click', () => apply(preset));
        wrap.appendChild(btn);
      });
      return wrap;
    };

    const sizeCanvas = document.createElement('canvas');
    sizeCanvas.className = 'curve-canvas';
    this.createSection('pencil.size', 'Pressure → Size')
      .add(sizeCanvas, curvePresets(p => this.sizeCurve.loadPreset(p)));

    const opacityCanvas = document.createElement('canvas');
    opacityCanvas.className = 'curve-canvas';
    this.createSection('pencil.opacity', 'Pressure → Opacity')
      .add(opacityCanvas, curvePresets(p => this.opacityCurve.loadPreset(p)));

    this.endPanel();

    // CurveEditor sets its own backing size (400x160) rather than measuring the
    // element, so it draws correctly even when built inside a collapsed section.
    this.sizeCurve = new CurveEditor(sizeCanvas, {
      onChange: (data) => {
        this.brushState.set('brushPressureSizeResponse', new Uint8Array(new Float64Array(data).buffer));
      }
    });
    this.opacityCurve = new CurveEditor(opacityCanvas, {
      onChange: (data) => {
        this.brushState.set('brushPressureOpacityResponse', new Uint8Array(new Float64Array(data).buffer));
      }
    });

  }
}

/**
 * Wet Mix Panel
 */
export class WetMixPanel extends BasePanel {
  render() {
    this.beginPanel('Wet Mix');

    this.createSection('wet.load', 'Load')
      .add(
        this.createSlider('brushWetDilution', 'Dilution'),
        this.createSlider('brushWetCharge', 'Charge')
      );

    this.createSection('wet.blending', 'Blending')
      .add(
        this.createSlider('brushWetPull', 'Pull'),
        this.createSlider('brushWetAttack', 'Attack'),
        this.createSlider('brushWetBleed', 'Bleed')
      );

    this.createSection('wet.edges', 'Edges', { defaultOpen: false })
      .add(
        this.createToggle('brushWetEdge', 'Wet Edge'),
        this.createToggle('brushWetBurn', 'Burn')
      );

    this.endPanel();
  }
}

/**
 * Color Dynamics Panel
 */
export class ColorDynamicsPanel extends BasePanel {
  render() {
    this.beginPanel('Color Dynamics');

    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.innerHTML = `
      <div class="empty-state-icon">C</div>
      <div class="empty-state-text">Not implemented. Procreate's colour dynamics
      (hue/saturation/brightness jitter per stamp) are not simulated by this
      preview and are not written to the exported brush.</div>
    `;
    this.createSection('color.status', 'Status').add(empty);

    this.endPanel();
  }
}

/**
 * Rendering Panel
 */
export class RenderingPanel extends BasePanel {
  render() {
    this.beginPanel('Rendering');

    const mode = BLENDING_MODES.find(m => m.id === this.brushState.get('brushBlendingMode'));
    this.createSection('rendering.blend', 'Blending', { hint: mode ? mode.name : '' })
      .add(this.createDropdown(
        'brushBlendingMode',
        'Blending Mode',
        BLENDING_MODES.map(m => ({ value: m.id, label: m.name }))
      ));

    this.endPanel();
  }
}

/**
 * About This Brush Panel
 */
export class AboutBrushPanel extends BasePanel {
  render(onReset) {
    this.onReset = onReset;
    this.beginPanel('About This Brush');

    /* ── Identity ── */
    const identity = this.createSection('about.identity', 'Identity');

    const authorContainer = document.createElement('div');
    authorContainer.className = 'dropdown-container';
    const authorLabel = document.createElement('label');
    authorLabel.className = 'dropdown-label';
    authorLabel.textContent = 'Author';
    const authorInput = document.createElement('input');
    authorInput.type = 'text';
    authorInput.className = 'brush-name-input field-block';
    authorInput.value = this.brushState.get('authorName');
    authorInput.addEventListener('change', () => {
      this.brushState.set('authorName', authorInput.value);
    });
    authorContainer.append(authorLabel, authorInput);

    const notesContainer = document.createElement('div');
    notesContainer.className = 'dropdown-container';
    const notesLabel = document.createElement('label');
    notesLabel.className = 'dropdown-label';
    notesLabel.textContent = 'Notes';
    const notesInput = document.createElement('textarea');
    notesInput.className = 'brush-name-input field-block field-notes';
    notesInput.value = this.brushState.get('notes');
    notesInput.addEventListener('change', () => {
      this.brushState.set('notes', notesInput.value);
    });
    notesContainer.append(notesLabel, notesInput);

    identity.add(authorContainer, notesContainer);

    /* ── Specification ──
       Read-only, and read straight off the state rather than restated by hand —
       a spec sheet that can disagree with the brush is worse than none. */
    const spec = this.createSection('about.spec', 'Specification', { defaultOpen: false });
    spec.add(this.createSpecTable(this.specRows()));

    /* ── Reset ── */
    const reset = this.createSection('about.reset', 'Reset', { defaultOpen: false });
    const resetBtn = document.createElement('button');
    resetBtn.type = 'button';
    resetBtn.className = 'btn btn-danger field-block';
    resetBtn.textContent = 'Reset to defaults';
    resetBtn.addEventListener('click', async () => {
      const ok = await Modal.confirm({
        title: 'Reset brush',
        message: 'Reset all brush settings to defaults? Ctrl+Z undoes this afterward if you change your mind.',
        okLabel: 'Reset',
        danger: true,
      });
      if (ok) {
        this.brushState.reset();
        if (this.onReset) this.onReset();
      }
    });
    reset.add(resetBtn);

    this.endPanel();
  }

  specRows() {
    const s = this.brushState.get();
    const mode = BLENDING_MODES.find(m => m.id === s.brushBlendingMode);
    const deg = v => `${Math.round((v ?? 0) * 57.2958)}°`;
    return [
      ['Shape source', s.shapeSource],
      ['Grain source', s.grainSource],
      ['Size range', `${pct(s.brushSizeMinimum)} – ${pct(s.brushSizeMaximum)}`],
      ['Opacity range', `${pct(s.brushOpacityMinimum)} – ${pct(s.brushOpacityMaximum)}`],
      ['Spacing', `${pct(s.brushSpacing)} · jitter ${pct(s.brushSpacingJitter)}`],
      ['StreamLine', pct(s.brushStreamline)],
      ['Stabilization', pct(s.brushStabilization)],
      ['Taper', `start ${pct(s.brushTaperSizeStart)} · end ${pct(s.brushTaperSizeEnd)}`],
      ['Scatter', `${pct(s.brushShapeScatter)} · rotation ${deg(s.brushShapeRotation)}`],
      ['Grain depth', pct(s.brushGrainDepth)],
      ['Wet mix', `dilution ${pct(s.brushWetDilution)} · charge ${pct(s.brushWetCharge)}`],
      ['Blending mode', mode ? mode.name : String(s.brushBlendingMode)],
    ];
  }
}

export default {
  StrokePathPanel,
  TaperPanel,
  ShapePanel,
  GrainPanel,
  DynamicsPanel,
  PencilPanel,
  WetMixPanel,
  ColorDynamicsPanel,
  RenderingPanel,
  AboutBrushPanel
};
