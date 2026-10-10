/**
 * PresetLibrary.js - Preset Storage and Retrieval
 *
 * Uses localStorage for preset metadata and IndexedDB for image blobs.
 */

const DB_NAME = 'ProcreateBrushDesigner';
const DB_VERSION = 1;
const STORE_NAME = 'presetImages';

export class PresetLibrary {
  constructor() {
    this.db = null;
    this.presets = this.loadFromLocalStorage();
    this.initDB();
  }

  async initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        }
      };
    });
  }

  loadFromLocalStorage() {
    try {
      const data = localStorage.getItem('brushPresets');
      if (data) {
        return JSON.parse(data);
      }
    } catch (e) {
      console.error('Failed to load presets:', e);
    }
    return [];
  }

  saveToLocalStorage() {
    try {
      const metadata = this.presets.map(p => ({
        id: p.id,
        name: p.name,
        category: p.category,
        tags: p.tags,
        thumbnail: p.thumbnail,
        createdAt: p.createdAt,
        settings: p.settings
      }));
      localStorage.setItem('brushPresets', JSON.stringify(metadata));
    } catch (e) {
      console.error('Failed to save presets:', e);
    }
  }

  async saveImageData(id, shapeData, grainData) {
    if (!this.db) await this.initDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);

      const request = store.put({
        id,
        shapeData,
        grainData,
        updatedAt: Date.now()
      });

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async loadImageData(id) {
    if (!this.db) await this.initDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], 'readonly');
      const store = transaction.objectStore(STORE_NAME);

      const request = store.get(id);

      request.onsuccess = () => {
        resolve(request.result || null);
      };
      request.onerror = () => reject(request.error);
    });
  }

  async addPreset(name, category, brushState, shapeCanvas, grainCanvas) {
    const id = this.generateUUID();

    const thumbnail = await this.generateThumbnail(shapeCanvas, grainCanvas);
    const shapeData = shapeCanvas.toDataURL('image/png');
    const grainData = grainCanvas.toDataURL('image/png');

    const preset = {
      id,
      name,
      category: category || 'Custom',
      tags: [],
      thumbnail,
      createdAt: Date.now(),
      settings: brushState.get ? brushState.get() : { ...brushState }
    };

    await this.saveImageData(id, shapeData, grainData);

    this.presets.push(preset);
    this.saveToLocalStorage();

    return preset;
  }

  async updatePreset(id, updates) {
    const index = this.presets.findIndex(p => p.id === id);
    if (index === -1) return null;

    this.presets[index] = { ...this.presets[index], ...updates };
    this.saveToLocalStorage();

    return this.presets[index];
  }

  async deletePreset(id) {
    const index = this.presets.findIndex(p => p.id === id);
    if (index === -1) return false;

    this.presets.splice(index, 1);
    this.saveToLocalStorage();

    if (this.db) {
      const transaction = this.db.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      await new Promise((resolve, reject) => {
        const request = store.delete(id);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    }

    return true;
  }

  getPreset(id) {
    return this.presets.find(p => p.id === id);
  }

  getAllPresets() {
    return [...this.presets];
  }

  getPresetsByCategory(category) {
    return this.presets.filter(p => p.category === category);
  }

  getCategories() {
    const categories = new Set(this.presets.map(p => p.category));
    return Array.from(categories).sort();
  }

  async generateThumbnail(shapeCanvas, grainCanvas, size = 128) {
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#F5F0E8';
    ctx.fillRect(0, 0, size, size);

    const shapeSize = size * 0.6;
    const shapeX = (size - shapeSize) / 2;
    const shapeY = (size - shapeSize) / 2;
    ctx.drawImage(shapeCanvas, shapeX, shapeY, shapeSize, shapeSize);

    if (grainCanvas) {
      ctx.globalCompositeOperation = 'multiply';
      ctx.globalAlpha = 0.5;
      ctx.drawImage(grainCanvas, 0, 0, size, size);
    }

    return canvas.toDataURL('image/png');
  }

  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  async importBrush(file) {
    return null;
  }

  /**
   * Add built-in presets
   * Bug fix: import generateShape and generateGrain from their respective modules
   */
  async addBuiltInPresets() {
    const builtIns = [
      {
        name: 'Classic Pencil',
        category: 'Drawing',
        settings: {
          brushSpacing: 0.03,
          brushStreamline: 0.15,
          brushSizeMaximum: 0.5,
          brushGrainDepth: 0.7,
          shapeSource: 'Soft Circle',
          grainSource: 'Paper Fine'
        }
      },
      {
        name: 'Ink Pen',
        category: 'Inking',
        settings: {
          brushSpacing: 0.01,
          brushStreamline: 0.7,
          brushSizeMaximum: 0.8,
          brushTaperSizeStart: 0.25,
          brushTaperSizeEnd: 0.35,
          shapeSource: 'Hard Circle',
          grainSource: 'Flat'
        }
      },
      {
        name: 'Watercolor Wash',
        category: 'Painting',
        settings: {
          brushSpacing: 0.08,
          brushWetDilution: 0.5,
          brushWetCharge: 0.7,
          brushGrainMoving: true,
          brushWetEdge: true,
          shapeSource: 'Ink Blot',
          grainSource: 'Cold Press'
        }
      },
      {
        name: 'Dry Brush',
        category: 'Texture',
        settings: {
          brushSpacing: 0.05,
          brushShapeScatter: 0.3,
          brushJitterX: 0.2,
          brushJitterY: 0.2,
          shapeSource: 'Bristle',
          grainSource: 'Canvas'
        }
      },
      {
        name: 'Stamp Texture',
        category: 'Texture',
        settings: {
          brushSpacing: 1.2,
          brushShapeScatter: 0.4,
          brushShapeRandomized: true,
          brushBlendingMode: 1,
          shapeSource: 'Torn Edge',
          grainSource: 'Linen'
        }
      }
    ];

    // Check if built-ins already exist
    const hasBuiltIns = this.presets.some(p =>
      builtIns.some(b => b.name === p.name)
    );

    if (hasBuiltIns) return;

    // Bug fix: import from the correct separate modules
    const { generateShape } = await import('../generators/ShapeGenerator.js');
    const { generateGrain } = await import('../generators/GrainGenerator.js');

    for (const builtIn of builtIns) {
      const id = this.generateUUID();

      const shapeCanvas = generateShape(builtIn.settings.shapeSource, 512);
      const grainCanvas = generateGrain(builtIn.settings.grainSource, 1024);

      const thumbnail = await this.generateThumbnail(shapeCanvas, grainCanvas);

      const shapeData = shapeCanvas.toDataURL('image/png');
      const grainData = grainCanvas.toDataURL('image/png');

      const preset = {
        id,
        name: builtIn.name,
        category: builtIn.category,
        tags: [],
        thumbnail,
        createdAt: Date.now(),
        settings: { ...builtIn.settings, identifier: id }
      };

      await this.saveImageData(id, shapeData, grainData);
      this.presets.push(preset);
    }

    this.saveToLocalStorage();
  }
}

export default PresetLibrary;
