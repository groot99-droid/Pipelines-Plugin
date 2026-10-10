/**
 * BrushState.js - Canonical Brush Settings Object
 *
 * Defines all brush properties that Procreate expects in Brush.archive.
 * This is the single source of truth for brush configuration.
 */

// Default values for all brush properties
export const DEFAULT_BRUSH_STATE = {
  // Metadata
  name: 'Untitled Brush',
  authorName: '',
  notes: '',
  identifier: '',
  version: 1,

  // Stroke Path
  brushSpacing: 0.03,
  brushSpacingJitter: 0,
  brushStreamline: 0.15,
  brushStreamlinePressure: 0,
  brushStabilization: 0,
  brushMotionFiltering: 0,
  brushJitterX: 0,
  brushJitterY: 0,
  brushFallOff: 0,

  // Shape
  brushShapeScatter: 0,
  brushShapeRotation: 0,
  brushShapeCount: 1,
  brushShapeCountJitter: 0,
  brushShapeRandomized: false,
  brushAzimuth: false,
  brushFlipX: false,
  brushFlipY: false,

  // Grain
  brushGrainScale: 1.0,
  brushGrainRotation: 0,
  brushGrainDepth: 0.7,
  brushGrainDepthMin: 0,
  brushGrainDepthJitter: 0,
  brushGrainOffsetJitter: 0,
  brushGrainMoving: false,
  brushGrainZoom: false,

  // Dynamics
  brushSizeMaximum: 1.0,
  brushSizeMinimum: 0,
  brushOpacityMaximum: 1.0,
  brushOpacityMinimum: 0,
  brushBleedAmount: 0,

  // Taper
  brushTaperSizeStart: 0,
  brushTaperSizeEnd: 0,
  brushTaperTip: 0.5,
  brushTaperOpacity: 0,
  brushTaperLinked: true,

  // Wet Mix
  brushWetDilution: 0,
  brushWetCharge: 0,
  brushWetPull: 0,
  brushWetAttack: 0,
  brushWetBleed: 0,
  brushWetEdge: false,
  brushWetBurn: false,

  // Rendering
  brushBlendingMode: 0, // 0=Normal, 1=Multiply, 2=Screen, etc.

  // Pressure Curves (serialized bezier data)
  brushPressureSizeResponse: null,
  brushPressureOpacityResponse: null,

  // Shape/Grain source
  shapeSource: 'Soft Circle', // or 'upload' for custom
  grainSource: 'Paper Fine',  // or 'upload' for custom
};

// Property ranges and validation
export const BRUSH_PROPERTY_RANGES = {
  brushSpacing: { min: 0, max: 5.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushSpacingJitter: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushStreamline: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushStreamlinePressure: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushStabilization: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushMotionFiltering: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushJitterX: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushJitterY: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushFallOff: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },

  brushShapeScatter: { min: 0, max: 2.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushShapeRotation: { min: 0, max: 6.283, step: 0.01, display: v => `${(v * 57.2958).toFixed(0)}°` },
  brushShapeCount: { min: 1, max: 16, step: 1, display: v => v.toFixed(0) },
  brushShapeCountJitter: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },

  brushGrainScale: { min: 0, max: 2.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushGrainRotation: { min: 0, max: 6.283, step: 0.01, display: v => `${(v * 57.2958).toFixed(0)}°` },
  brushGrainDepth: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushGrainDepthMin: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushGrainDepthJitter: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushGrainOffsetJitter: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },

  brushSizeMaximum: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushSizeMinimum: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushOpacityMaximum: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushOpacityMinimum: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushBleedAmount: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },

  brushTaperSizeStart: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushTaperSizeEnd: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushTaperTip: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushTaperOpacity: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },

  brushWetDilution: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushWetCharge: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushWetPull: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushWetAttack: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
  brushWetBleed: { min: 0, max: 1.0, step: 0.01, display: v => `${(v * 100).toFixed(0)}%` },
};

// Blending modes
export const BLENDING_MODES = [
  { id: 0, name: 'Normal' },
  { id: 1, name: 'Multiply' },
  { id: 2, name: 'Screen' },
  { id: 3, name: 'Overlay' },
  { id: 4, name: 'Darken' },
  { id: 5, name: 'Lighten' },
  { id: 6, name: 'Color Dodge' },
  { id: 7, name: 'Color Burn' },
  { id: 8, name: 'Soft Light' },
  { id: 9, name: 'Hard Light' },
  { id: 10, name: 'Difference' },
  { id: 11, name: 'Exclusion' },
  { id: 12, name: 'Hue' },
  { id: 13, name: 'Saturation' },
  { id: 14, name: 'Color' },
  { id: 15, name: 'Luminosity' },
];

export class BrushState {
  constructor(initialState = {}) {
    this.state = { ...DEFAULT_BRUSH_STATE };
    this.listeners = new Set();

    // Generate UUID if not provided
    if (!initialState.identifier) {
      this.state.identifier = this.generateUUID();
    }

    // Apply initial state
    this.setState(initialState);
  }

  /**
   * Get current state (or specific property)
   */
  get(key) {
    if (key) {
      return this.state[key];
    }
    return { ...this.state };
  }

  /**
   * Set state (partial update)
   */
  setState(updates) {
    const oldState = { ...this.state };
    const changed = [];

    for (const [key, value] of Object.entries(updates)) {
      if (this.state[key] !== value) {
        this.state[key] = value;
        changed.push(key);
      }
    }

    if (changed.length > 0) {
      this.notify(changed, oldState);
    }

    return changed;
  }

  /**
   * Set a single property
   */
  set(key, value) {
    if (this.state[key] !== value) {
      const oldState = { ...this.state };
      this.state[key] = value;
      this.notify([key], oldState);
      return true;
    }
    return false;
  }

  /**
   * Reset to defaults
   */
  reset() {
    const oldState = { ...this.state };
    const uuid = this.state.identifier;
    this.state = { ...DEFAULT_BRUSH_STATE, identifier: uuid };
    this.notify(Object.keys(DEFAULT_BRUSH_STATE), oldState);
  }

  /**
   * Subscribe to state changes
   */
  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  /**
   * Notify listeners of changes
   */
  notify(changedKeys, oldState) {
    for (const listener of this.listeners) {
      listener(this.state, changedKeys, oldState);
    }
  }

  /**
   * Generate a UUID v4
   */
  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  /**
   * Get property range info
   */
  static getRange(property) {
    return BRUSH_PROPERTY_RANGES[property] || { min: 0, max: 1, step: 0.01, display: v => v.toString() };
  }

  /**
   * Clamp a value to its valid range
   */
  static clamp(property, value) {
    const range = BRUSH_PROPERTY_RANGES[property];
    if (!range) return value;
    return Math.max(range.min, Math.min(range.max, value));
  }

  /**
   * Format a value for display
   */
  static format(property, value) {
    const range = BRUSH_PROPERTY_RANGES[property];
    if (!range) return value.toString();
    return range.display(value);
  }

  /**
   * Create a snapshot for export
   */
  toExportFormat() {
    return {
      '$version': 100000,
      '$archiver': 'NSKeyedArchiver',
      '$top': {
        'root': { 'UID': 1 }
      },
      '$objects': [
        '$null',
        this.createBrushObject(),
        this.createClassDescriptor(),
      ]
    };
  }

  /**
   * Create the brush object for NSKeyedArchiver
   */
  createBrushObject() {
    const obj = {
      '$class': { 'UID': 2 }
    };

    const properties = [
      'brushSpacing', 'brushSpacingJitter', 'brushStreamline', 'brushStreamlinePressure',
      'brushStabilization', 'brushMotionFiltering', 'brushJitterX', 'brushJitterY', 'brushFallOff',
      'brushShapeScatter', 'brushShapeRotation', 'brushShapeCount', 'brushShapeCountJitter',
      'brushShapeRandomized', 'brushAzimuth', 'brushFlipX', 'brushFlipY',
      'brushGrainScale', 'brushGrainRotation', 'brushGrainDepth', 'brushGrainDepthMin',
      'brushGrainDepthJitter', 'brushGrainOffsetJitter', 'brushGrainMoving', 'brushGrainZoom',
      'brushSizeMaximum', 'brushSizeMinimum', 'brushOpacityMaximum', 'brushOpacityMinimum',
      'brushBleedAmount', 'brushTaperSizeStart', 'brushTaperSizeEnd', 'brushTaperTip',
      'brushTaperOpacity', 'brushTaperLinked', 'brushWetDilution', 'brushWetCharge',
      'brushWetPull', 'brushWetAttack', 'brushWetBleed', 'brushWetEdge', 'brushWetBurn',
      'brushBlendingMode',
    ];

    for (const prop of properties) {
      const value = this.state[prop];
      if (value !== undefined && value !== null) {
        obj[prop] = value;
      }
    }

    obj['brushName'] = this.state.name;
    obj['brushAuthorName'] = this.state.authorName || '';
    obj['brushNotes'] = this.state.notes || '';
    obj['brushIdentifier'] = this.state.identifier;
    obj['brushVersion'] = this.state.version;

    if (this.state.brushPressureSizeResponse) {
      obj['brushPressureSizeResponse'] = this.state.brushPressureSizeResponse;
    }
    if (this.state.brushPressureOpacityResponse) {
      obj['brushPressureOpacityResponse'] = this.state.brushPressureOpacityResponse;
    }

    return obj;
  }

  /**
   * Create the class descriptor for NSKeyedArchiver
   */
  createClassDescriptor() {
    return {
      '$classname': 'MCBrush',
      '$classes': ['MCBrush', 'NSObject']
    };
  }

  /**
   * Serialize to JSON
   */
  toJSON() {
    return JSON.stringify(this.state);
  }

  /**
   * Load from JSON
   */
  fromJSON(json) {
    try {
      const parsed = JSON.parse(json);
      this.setState(parsed);
      return true;
    } catch (e) {
      console.error('Failed to parse brush state:', e);
      return false;
    }
  }
}

export default BrushState;
