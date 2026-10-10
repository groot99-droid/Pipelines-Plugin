/**
 * BrushArchive.js - NSKeyedArchiver Structure for Brush.archive
 *
 * Assembles the binary plist payload for Procreate brush files.
 */

import { PlistEncoder } from './PlistEncoder.js';

export class BrushArchive {
  /**
   * Encode brush state to Brush.archive format
   */
  static encode(brushState) {
    const encoder = new PlistEncoder();

    const archive = {
      '$version': 100000,
      '$archiver': 'NSKeyedArchiver',
      '$top': {
        'root': { 'UID': 1 }
      },
      '$objects': [
        '$null',
        null,
        null,
      ]
    };

    archive.$objects[1] = this.createBrushObject(brushState);
    archive.$objects[2] = this.createClassDescriptor();

    return encoder.encode(archive);
  }

  static createBrushObject(brushState) {
    const state = brushState.get ? brushState.get() : brushState;

    const obj = {
      '$class': { 'UID': 2 }
    };

    this.addFloatProperty(obj, 'brushSpacing', state.brushSpacing);
    this.addFloatProperty(obj, 'brushSpacingJitter', state.brushSpacingJitter);
    this.addFloatProperty(obj, 'brushStreamline', state.brushStreamline);
    this.addFloatProperty(obj, 'brushStreamlinePressure', state.brushStreamlinePressure);
    this.addFloatProperty(obj, 'brushStabilization', state.brushStabilization);
    this.addFloatProperty(obj, 'brushMotionFiltering', state.brushMotionFiltering);
    this.addFloatProperty(obj, 'brushJitterX', state.brushJitterX);
    this.addFloatProperty(obj, 'brushJitterY', state.brushJitterY);
    this.addFloatProperty(obj, 'brushFallOff', state.brushFallOff);

    this.addFloatProperty(obj, 'brushShapeScatter', state.brushShapeScatter);
    this.addFloatProperty(obj, 'brushShapeRotation', state.brushShapeRotation);
    this.addIntProperty(obj, 'brushShapeCount', state.brushShapeCount);
    this.addFloatProperty(obj, 'brushShapeCountJitter', state.brushShapeCountJitter);
    this.addBoolProperty(obj, 'brushShapeRandomized', state.brushShapeRandomized);
    this.addBoolProperty(obj, 'brushAzimuth', state.brushAzimuth);
    this.addBoolProperty(obj, 'brushFlipX', state.brushFlipX);
    this.addBoolProperty(obj, 'brushFlipY', state.brushFlipY);

    this.addFloatProperty(obj, 'brushGrainScale', state.brushGrainScale);
    this.addFloatProperty(obj, 'brushGrainRotation', state.brushGrainRotation);
    this.addFloatProperty(obj, 'brushGrainDepth', state.brushGrainDepth);
    this.addFloatProperty(obj, 'brushGrainDepthMin', state.brushGrainDepthMin);
    this.addFloatProperty(obj, 'brushGrainDepthJitter', state.brushGrainDepthJitter);
    this.addFloatProperty(obj, 'brushGrainOffsetJitter', state.brushGrainOffsetJitter);
    this.addBoolProperty(obj, 'brushGrainMoving', state.brushGrainMoving);
    this.addBoolProperty(obj, 'brushGrainZoom', state.brushGrainZoom);

    this.addFloatProperty(obj, 'brushSizeMaximum', state.brushSizeMaximum);
    this.addFloatProperty(obj, 'brushSizeMinimum', state.brushSizeMinimum);
    this.addFloatProperty(obj, 'brushOpacityMaximum', state.brushOpacityMaximum);
    this.addFloatProperty(obj, 'brushOpacityMinimum', state.brushOpacityMinimum);
    this.addFloatProperty(obj, 'brushBleedAmount', state.brushBleedAmount);

    this.addFloatProperty(obj, 'brushTaperSizeStart', state.brushTaperSizeStart);
    this.addFloatProperty(obj, 'brushTaperSizeEnd', state.brushTaperSizeEnd);
    this.addFloatProperty(obj, 'brushTaperTip', state.brushTaperTip);
    this.addFloatProperty(obj, 'brushTaperOpacity', state.brushTaperOpacity);
    this.addBoolProperty(obj, 'brushTaperLinked', state.brushTaperLinked);

    this.addFloatProperty(obj, 'brushWetDilution', state.brushWetDilution);
    this.addFloatProperty(obj, 'brushWetCharge', state.brushWetCharge);
    this.addFloatProperty(obj, 'brushWetPull', state.brushWetPull);
    this.addFloatProperty(obj, 'brushWetAttack', state.brushWetAttack);
    this.addFloatProperty(obj, 'brushWetBleed', state.brushWetBleed);
    this.addBoolProperty(obj, 'brushWetEdge', state.brushWetEdge);
    this.addBoolProperty(obj, 'brushWetBurn', state.brushWetBurn);

    this.addIntProperty(obj, 'brushBlendingMode', state.brushBlendingMode);

    this.addStringProperty(obj, 'brushName', state.name || 'Untitled Brush');
    this.addStringProperty(obj, 'brushAuthorName', state.authorName || '');
    this.addStringProperty(obj, 'brushNotes', state.notes || '');
    this.addStringProperty(obj, 'brushIdentifier', state.identifier || this.generateUUID());
    this.addIntProperty(obj, 'brushVersion', state.version || 1);

    if (state.brushPressureSizeResponse) {
      obj['brushPressureSizeResponse'] = state.brushPressureSizeResponse;
    }
    if (state.brushPressureOpacityResponse) {
      obj['brushPressureOpacityResponse'] = state.brushPressureOpacityResponse;
    }

    return obj;
  }

  static createClassDescriptor() {
    return {
      '$classname': 'MCBrush',
      '$classes': ['MCBrush', 'NSObject']
    };
  }

  static addFloatProperty(obj, key, value) {
    if (value !== undefined && value !== null) {
      obj[key] = parseFloat(value);
    }
  }

  static addIntProperty(obj, key, value) {
    if (value !== undefined && value !== null) {
      obj[key] = parseInt(value);
    }
  }

  static addBoolProperty(obj, key, value) {
    if (value !== undefined && value !== null) {
      obj[key] = !!value;
    }
  }

  static addStringProperty(obj, key, value) {
    if (value !== undefined && value !== null) {
      obj[key] = String(value);
    }
  }

  static generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
}

export default BrushArchive;
