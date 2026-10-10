/**
 * app.js - Main Application Entry Point
 *
 * Root: state machine, panel routing, event bus
 */

import { BrushState } from './editor/BrushState.js';
import { PresetLibrary } from './editor/PresetLibrary.js';
import { HistoryManager } from './editor/HistoryManager.js';
import { StrokeRenderer } from './preview/StrokeRenderer.js';
import { StrokeInput } from './preview/StrokeInput.js';
import { BrushExporter } from './export/BrushExporter.js';
import { GbrEncoder } from './export/GbrEncoder.js';
import { UniversalKitExporter } from './export/UniversalKitExporter.js';
import { getToast } from './ui/Toast.js';
import { Modal } from './ui/Modal.js';
import { generateShape } from './generators/ShapeGenerator.js';
import { generateGrain } from './generators/GrainGenerator.js';
import {
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
} from './panels/PanelComponents.js';
import { AIAssistPanel } from './panels/AIAssistPanel.js';

class ProcreateBrushDesigner {
  constructor() {
    this.brushState = new BrushState();
    this.presetLibrary = new PresetLibrary();
    this.history = new HistoryManager(50);
    this.strokeRenderer = null;
    this.strokeInput = null;
    this.sampleLevels = ['light', 'medium', 'heavy'];
    this.currentPanel = 'stroke';
    this.panels = {};
    this.debounceTimer = null;

    // Canvas elements
    this.previewCanvas = null;
    this.shapeCanvas = null;
    this.grainCanvas = null;

    this.init();
  }

  async init() {
    // Get DOM elements
    this.previewCanvas = document.getElementById('previewCanvas');
    this.shapeCanvas = document.getElementById('shapeCanvas');
    this.grainCanvas = document.getElementById('grainCanvas');

    // Set up canvases
    this.setupCanvases();

    // Initialize stroke renderer
    this.strokeRenderer = new StrokeRenderer(this.previewCanvas);
    this.strokeRenderer.setTextures(this.shapeCanvas, this.grainCanvas);

    // The preview is a surface you draw on, not a picture of one.
    this.strokeInput = new StrokeInput(
      this.previewCanvas,
      this.strokeRenderer,
      () => this.brushState.get(),
      {
        onStatus: (info) => this.onPointerStatus(info),
        onStrokeEnd: () => this.updateSheetButtons()
      }
    );

    // Initialize panels
    this.initPanels();

    // Set up event listeners
    this.bindEvents();

    // Subscribe to state changes
    this.brushState.subscribe((state, changedKeys) => {
      this.onStateChange(state, changedKeys);
    });

    // Add initial history state
    this.history.push(this.brushState.get(), 'Initial state');

    // Load built-in presets
    await this.presetLibrary.addBuiltInPresets();
    this.renderPresets();

    // Initial render
    this.renderPreview();

    // Show welcome toast
    getToast().success('Procreate Brush Designer loaded');
  }

  setupCanvases() {
    // Set shape canvas size
    this.shapeCanvas.width = 512;
    this.shapeCanvas.height = 512;

    // Set grain canvas size
    this.grainCanvas.width = 1024;
    this.grainCanvas.height = 1024;

    // Generate initial shape and grain
    const shapeName = this.brushState.get('shapeSource');
    const grainName = this.brushState.get('grainSource');

    const shapeCanvas = generateShape(shapeName, 512);
    const grainCanvas = generateGrain(grainName, 1024);

    // Copy to display canvases
    const shapeCtx = this.shapeCanvas.getContext('2d');
    shapeCtx.drawImage(shapeCanvas, 0, 0);

    const grainCtx = this.grainCanvas.getContext('2d');
    grainCtx.drawImage(grainCanvas, 0, 0);
  }

  initPanels() {
    const panelContent = document.getElementById('panelContent');

    this.panels = {
      stroke: new StrokePathPanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      taper: new TaperPanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      shape: new ShapePanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      grain: new GrainPanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      dynamics: new DynamicsPanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      pencil: new PencilPanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      wetmix: new WetMixPanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      color: new ColorDynamicsPanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      rendering: new RenderingPanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      about: new AboutBrushPanel(panelContent, this.brushState, (k, v) => this.onPanelChange(k, v)),
      ai: new AIAssistPanel(panelContent, this.brushState, (patch, summary) => this.applyAIPatch(patch, summary))
    };

    // Render initial panel
    this.switchPanel('stroke');
  }

  bindEvents() {
    // Tab switching
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const panel = tab.dataset.panel;
        this.switchPanel(panel);

        // Update active tab
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
      });
    });

    // Brush name input
    const brushNameInput = document.getElementById('brushName');
    brushNameInput.addEventListener('change', () => {
      this.brushState.set('name', brushNameInput.value);
    });

    // Undo/Redo buttons
    document.getElementById('undoBtn').addEventListener('click', () => this.undo());
    document.getElementById('redoBtn').addEventListener('click', () => this.redo());

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'z') {
          e.preventDefault();
          if (e.shiftKey) {
            this.redo();
          } else {
            this.undo();
          }
        } else if (e.key === 'y') {
          e.preventDefault();
          this.redo();
        }
      }
    });

    // Export menu
    const exportBtn = document.getElementById('exportBtn');
    const exportMenu = document.getElementById('exportMenu');

    exportBtn.addEventListener('click', () => {
      exportMenu.style.display = exportMenu.style.display === 'none' ? 'block' : 'none';
    });

    // Close export menu on outside click
    document.addEventListener('click', (e) => {
      if (!exportBtn.contains(e.target) && !exportMenu.contains(e.target)) {
        exportMenu.style.display = 'none';
      }
    });

    // Export actions
    exportMenu.querySelectorAll('[data-export]').forEach(item => {
      item.addEventListener('click', () => {
        const type = item.dataset.export;
        exportMenu.style.display = 'none';

        if (type === 'brush') {
          this.exportBrush();
        } else if (type === 'brushset') {
          this.exportBrushset();
        } else if (type === 'gbr') {
          this.exportGbr();
        } else if (type === 'kit') {
          this.exportUniversalKit();
        } else if (type === 'source') {
          this.exportSource();
        }
      });
    });

    // Save preset button
    document.getElementById('savePresetBtn').addEventListener('click', () => {
      this.saveCurrentAsPreset();
    });

    // Import brush button
    document.getElementById('importBrushBtn').addEventListener('click', () => {
      document.getElementById('importFileInput').click();
    });

    // Import file input
    document.getElementById('importFileInput').addEventListener('change', (e) => {
      this.importBrush(e.target.files[0]);
      e.target.value = ''; // Reset
    });

    // Sample-stroke buttons pick which pressure levels the base layer shows.
    // They rebuild the sample strokes only -- the operator's own ink is on a
    // separate layer and is never wiped by a settings change.
    document.querySelectorAll('.preview-mode-btn[data-pressure]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.preview-mode-btn[data-pressure]').forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');

        const mode = btn.dataset.pressure;
        this.sampleLevels = mode === 'all' ? ['light', 'medium', 'heavy'] : [mode];
        this.renderPreview();
      });
    });

    document.getElementById('undoStrokeBtn').addEventListener('click', () => {
      if (this.strokeRenderer.undoInk()) {
        this.updateSheetButtons();
        getToast().info('Undid last stroke');
      }
    });

    document.getElementById('clearSheetBtn').addEventListener('click', () => {
      this.strokeRenderer.clearInk();
      this.updateSheetButtons();
    });

    // Window resize
    window.addEventListener('resize', () => {
      this.debounceRender();
    });
  }

  switchPanel(panelName) {
    this.currentPanel = panelName;

    // Instant. motion.hover is none in this system -- a 150ms fade on a panel
    // swap was 150ms of nothing before the controls arrived.
    const panel = this.panels[panelName];

    if (panelName === 'shape') {
      panel.render(this.shapeCanvas, () => this.onTextureChange());
    } else if (panelName === 'grain') {
      panel.render(this.grainCanvas, () => this.onTextureChange());
    } else if (panelName === 'about') {
      panel.render(() => this.onReset());
    } else {
      panel.render();
    }

    document.getElementById('panelContent').scrollTop = 0;
  }

  onPanelChange(key, value) {
    // Debounce history push
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      this.history.push(this.brushState.get(), `Changed ${key}`);
      this.updateUndoRedoButtons();
    }, 500);

    this.debounceRender();
  }

  applyAIPatch(patch, description) {
    this.brushState.setState(patch);
    this.history.push(this.brushState.get(), description || 'AI edit');
    this.updateUndoRedoButtons();
  }

  onStateChange(state, changedKeys) {
    // Update brush name input if changed
    if (changedKeys.includes('name')) {
      document.getElementById('brushName').value = state.name;
    }

    // Update panel sliders if needed
    if (this.panels[this.currentPanel]) {
      this.panels[this.currentPanel].updateSliders();
    }

    this.debounceRender();
  }

  onTextureChange() {
    this.strokeRenderer.setTextures(this.shapeCanvas, this.grainCanvas);
    this.debounceRender();
  }

  onReset() {
    this.setupCanvases();
    this.onTextureChange();
    this.history.push(this.brushState.get(), 'Reset to defaults');
    this.updateUndoRedoButtons();

    // Re-render current panel
    this.switchPanel(this.currentPanel);
  }

  debounceRender() {
    clearTimeout(this.renderTimer);
    this.renderTimer = setTimeout(() => this.renderPreview(), 16); // ~60fps
  }

  renderPreview(pressureLevels = this.sampleLevels) {
    this.strokeRenderer.render(this.brushState.get(), pressureLevels);
    this.updateSheetButtons();
  }

  updateSheetButtons() {
    const undoBtn = document.getElementById('undoStrokeBtn');
    const clearBtn = document.getElementById('clearSheetBtn');
    if (!undoBtn || !clearBtn) return;
    const canUndo = this.strokeRenderer.canUndoInk();
    undoBtn.disabled = !canUndo;
    clearBtn.disabled = !canUndo && !this.strokeRenderer.hasInk();
  }

  /**
   * Pointer readout + brush-size cursor.
   *
   * The readout names where pressure came from. A mouse reports a constant 0.5,
   * so speed stands in for it -- saying "speed" rather than showing a number
   * that looks like a sensor reading is the difference between a substitute and
   * a lie.
   */
  onPointerStatus(info) {
    const cursor = document.getElementById('brushCursor');
    const readout = document.getElementById('previewReadout');

    if (cursor) {
      if (info.hover) {
        const d = Math.max(4, info.diameter);
        cursor.style.width = `${d}px`;
        cursor.style.height = `${d}px`;
        cursor.style.transform = `translate(${info.hover.x - d / 2}px, ${info.hover.y - d / 2}px)`;
        cursor.style.display = 'block';
      } else {
        cursor.style.display = 'none';
      }
    }

    if (readout) {
      if (info.drawing) {
        readout.textContent =
          `${info.pointerType} · ${info.pressureSource} pressure ${Math.round(info.pressure * 100)}% · ${Math.round(info.diameter)}px`;
      } else if (info.hover) {
        readout.textContent =
          `${info.pointerType} · ${info.pressureSource} pressure · ${Math.round(info.diameter)}px nib`;
      } else {
        readout.textContent = 'draw on the sheet';
      }
    }
  }

  undo() {
    const state = this.history.undo();
    if (state) {
      this.brushState.setState(state);
      this.updateUndoRedoButtons();
      getToast().info('Undo: ' + this.history.getLastAction());
    }
  }

  redo() {
    const state = this.history.redo();
    if (state) {
      this.brushState.setState(state);
      this.updateUndoRedoButtons();
      getToast().info('Redo: ' + this.history.getNextAction());
    }
  }

  updateUndoRedoButtons() {
    document.getElementById('undoBtn').disabled = !this.history.canUndo();
    document.getElementById('redoBtn').disabled = !this.history.canRedo();
  }

  async exportBrush() {
    try {
      getToast().info('Exporting brush...');

      const blob = await BrushExporter.exportBrush(
        this.brushState,
        this.shapeCanvas,
        this.grainCanvas
      );

      const name = this.brushState.get('name').replace(/[^a-zA-Z0-9]/g, '_');
      BrushExporter.downloadBlob(blob, `${name}.brush`);

      getToast().success('Brush exported successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      getToast().error('Export failed: ' + error.message);
    }
  }

  async exportBrushset() {
    try {
      getToast().info('Exporting brushset...');

      const brushes = [{
        brushState: this.brushState,
        shapeCanvas: this.shapeCanvas,
        grainCanvas: this.grainCanvas
      }];

      const name = this.brushState.get('name').replace(/[^a-zA-Z0-9]/g, '_');
      const blob = await BrushExporter.exportBrushset(name, brushes);

      BrushExporter.downloadBlob(blob, `${name}.brushset`);
      getToast().success('Brushset exported successfully!');
    } catch (error) {
      console.error('Brushset export failed:', error);
      getToast().error('Export failed: ' + error.message);
    }
  }

  exportGbr() {
    try {
      getToast().info('Exporting .gbr...');

      const state = this.brushState.get();
      const spacingPercent = Math.round((state.brushSpacing || 0) * 100);
      const bytes = GbrEncoder.encode(this.shapeCanvas, { name: state.name, spacingPercent });
      const name = state.name.replace(/[^a-zA-Z0-9]/g, '_');

      BrushExporter.downloadBlob(new Blob([bytes], { type: 'application/octet-stream' }), `${name}.gbr`);
      getToast().success('.gbr exported! Also importable in Krita as a brush tip.');
    } catch (error) {
      console.error('.gbr export failed:', error);
      getToast().error('Export failed: ' + error.message);
    }
  }

  async exportUniversalKit() {
    try {
      getToast().info('Building universal kit...');

      const blob = await UniversalKitExporter.export(
        this.brushState, this.shapeCanvas, this.grainCanvas, this.previewCanvas
      );

      const name = this.brushState.get('name').replace(/[^a-zA-Z0-9]/g, '_');
      BrushExporter.downloadBlob(blob, `${name}-universal-kit.zip`);
      getToast().success('Universal kit exported!');
    } catch (error) {
      console.error('Universal kit export failed:', error);
      getToast().error('Export failed: ' + error.message);
    }
  }

  async exportSource() {
    const sourceFiles = [
      'index.html',
      'app.js',
      'styles.css',
      'README.md',
      'editor/BrushState.js',
      'editor/HistoryManager.js',
      'editor/PresetLibrary.js',
      'export/BrushArchive.js',
      'export/BrushExporter.js',
      'export/PlistEncoder.js',
      'export/GbrEncoder.js',
      'export/UniversalKitExporter.js',
      'ai/OllamaAssist.js',
      'generators/ShapeGenerator.js',
      'generators/GrainGenerator.js',
      'panels/PanelComponents.js',
      'panels/AIAssistPanel.js',
      'preview/StrokeRenderer.js',
      'ui/CurveEditor.js',
      'ui/Slider.js',
      'ui/Toast.js',
      'ui/Modal.js',
    ];

    try {
      getToast().info('Packaging source files...');

      const zip = {};
      const encoder = new TextEncoder();

      await Promise.all(sourceFiles.map(async (path) => {
        try {
          const res = await fetch(path);
          if (!res.ok) return;
          const text = await res.text();
          zip[`procreate-brush-designer/${path}`] = [encoder.encode(text), { level: 6 }];
        } catch {
          // skip missing files silently
        }
      }));

      const zipped = fflate.zipSync(zip);
      BrushExporter.downloadBlob(
        new Blob([zipped], { type: 'application/zip' }),
        'procreate-brush-designer-source.zip'
      );

      getToast().success('Source exported!');
    } catch (error) {
      console.error('Source export failed:', error);
      getToast().error('Source export failed: ' + error.message);
    }
  }

  async saveCurrentAsPreset() {
    const name = await Modal.prompt({
      title: 'Save preset', label: 'Preset name', defaultValue: this.brushState.get('name'),
    });
    if (!name) return;

    try {
      const category = (await Modal.prompt({
        title: 'Save preset', label: 'Category', defaultValue: 'Custom',
      })) || 'Custom';

      await this.presetLibrary.addPreset(
        name,
        category,
        this.brushState,
        this.shapeCanvas,
        this.grainCanvas
      );

      this.renderPresets();
      getToast().success('Preset saved!');
    } catch (error) {
      console.error('Failed to save preset:', error);
      getToast().error('Failed to save preset');
    }
  }

  renderPresets() {
    const container = document.getElementById('presetsList');
    container.innerHTML = '';

    const categories = this.presetLibrary.getCategories();

    categories.forEach(category => {
      const presets = this.presetLibrary.getPresetsByCategory(category);

      const categoryEl = document.createElement('div');
      categoryEl.className = 'preset-category';

      const title = document.createElement('div');
      title.className = 'preset-category-title';
      title.textContent = category;
      categoryEl.appendChild(title);

      const cards = document.createElement('div');
      cards.className = 'preset-cards';

      presets.forEach(preset => {
        const card = document.createElement('div');
        card.className = 'preset-card';
        card.innerHTML = `
          <img class="preset-thumbnail" src="${preset.thumbnail}" alt="${preset.name}">
          <div class="preset-info">
            <div class="preset-name">${preset.name}</div>
          </div>
        `;

        card.addEventListener('click', () => this.loadPreset(preset));
        cards.appendChild(card);
      });

      categoryEl.appendChild(cards);
      container.appendChild(categoryEl);
    });
  }

  async loadPreset(preset) {
    try {
      // Load image data
      const imageData = await this.presetLibrary.loadImageData(preset.id);

      if (imageData) {
        // Load shape
        if (imageData.shapeData) {
          await this.loadImageToCanvas(imageData.shapeData, this.shapeCanvas);
        }

        // Load grain
        if (imageData.grainData) {
          await this.loadImageToCanvas(imageData.grainData, this.grainCanvas);
        }
      }

      // Apply settings
      this.brushState.setState(preset.settings);

      // Update textures
      this.onTextureChange();

      // Add to history
      this.history.push(this.brushState.get(), `Loaded preset: ${preset.name}`);
      this.updateUndoRedoButtons();

      getToast().success(`Loaded preset: ${preset.name}`);
    } catch (error) {
      console.error('Failed to load preset:', error);
      getToast().error('Failed to load preset');
    }
  }

  loadImageToCanvas(dataUrl, canvas) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
        resolve();
      };
      img.onerror = reject;
      img.src = dataUrl;
    });
  }

  async importBrush(file) {
    if (!file) return;

    getToast().info('Import not yet fully implemented');
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new ProcreateBrushDesigner();
});

export default ProcreateBrushDesigner;
