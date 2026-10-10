/**
 * PlistEncoder.js - Binary Plist (bplist00) Encoder
 *
 * Implements a complete binary plist encoder in pure JavaScript.
 * This is critical for Procreate brush export compatibility.
 *
 * Binary plist format:
 *   [8-byte magic: "bplist00"]
 *   [object table: encoded objects]
 *   [offset table: byte offsets for each object]
 *   [trailer: 32 bytes with metadata]
 */

export class PlistEncoder {
  constructor() {
    this.objects = [];
    this.objectRefs = new Map();
    this.offsetTable = [];
  }

  /**
   * Encode a JavaScript value to binary plist format
   */
  encode(value) {
    this.objects = [];
    this.objectRefs = new Map();
    this.offsetTable = [];

    const rootIndex = this.addObject(value);

    // Calculate object offsets
    let currentOffset = 8; // After magic header
    const objectOffsets = [];

    for (const obj of this.objects) {
      objectOffsets.push(currentOffset);
      currentOffset += obj.length;
    }

    const offsetTableOffset = currentOffset;

    const maxOffset = offsetTableOffset;
    const offsetSize = maxOffset <= 0xFF ? 1 : maxOffset <= 0xFFFF ? 2 : maxOffset <= 0xFFFFFFFF ? 4 : 8;

    const maxRef = this.objects.length;
    const objectRefSize = maxRef <= 0xFF ? 1 : maxRef <= 0xFFFF ? 2 : 4;

    const offsetTableBytes = [];
    for (const offset of objectOffsets) {
      this.writeInteger(offsetTableBytes, offset, offsetSize);
    }

    // CFBinaryPlistTrailer is exactly 32 bytes: 5 unused, then sortVersion,
    // offsetIntSize, objectRefSize (1 byte each, offsets 5-7), then three
    // big-endian uint64 fields at offsets 8, 16, 24. The offsets below used
    // to start one byte too late (6/7/8 and 9/17/25), which pushed the last
    // 8-byte write to 25..32 -- one byte past this 32-byte buffer.
    const trailer = new Uint8Array(32);
    const trailerView = new DataView(trailer.buffer);

    trailerView.setUint8(5, 0);         // sort version
    trailerView.setUint8(6, offsetSize);
    trailerView.setUint8(7, objectRefSize);
    trailerView.setBigUint64(8, BigInt(this.objects.length), false);
    trailerView.setBigUint64(16, BigInt(rootIndex), false);
    trailerView.setBigUint64(24, BigInt(offsetTableOffset), false);

    const totalSize = 8 + this.objects.reduce((sum, obj) => sum + obj.length, 0) + offsetTableBytes.length + 32;
    const result = new Uint8Array(totalSize);
    let pos = 0;

    result.set(new TextEncoder().encode('bplist00'), pos);
    pos += 8;

    for (const obj of this.objects) {
      result.set(obj, pos);
      pos += obj.length;
    }

    result.set(new Uint8Array(offsetTableBytes), pos);
    pos += offsetTableBytes.length;

    result.set(trailer, pos);

    return result;
  }

  addObject(value) {
    if (value === null || value === undefined) {
      if (this.objects.length === 0) {
        this.objects.push(new Uint8Array([0x00]));
      }
      return 0;
    }

    const key = this.getObjectKey(value);
    if (key !== null && this.objectRefs.has(key)) {
      return this.objectRefs.get(key);
    }

    const index = this.objects.length;

    if (key !== null) {
      this.objectRefs.set(key, index);
    }

    let encoded;
    const type = typeof value;

    if (type === 'boolean') {
      encoded = new Uint8Array([value ? 0x09 : 0x08]);
    } else if (type === 'number') {
      encoded = this.encodeNumber(value);
    } else if (type === 'string') {
      encoded = this.encodeString(value);
    } else if (value instanceof Date) {
      encoded = this.encodeDate(value);
    } else if (value instanceof Uint8Array || value instanceof ArrayBuffer) {
      encoded = this.encodeData(value);
    } else if (Array.isArray(value)) {
      encoded = this.encodeArray(value, index);
    } else if (type === 'object') {
      encoded = this.encodeDict(value, index);
    } else {
      encoded = new Uint8Array([0x00]);
    }

    this.objects.push(encoded);
    return index;
  }

  getObjectKey(value) {
    if (typeof value === 'string') {
      return 's:' + value;
    }
    if (value instanceof Uint8Array) {
      return 'd:' + Array.from(value).join(',');
    }
    return null;
  }

  encodeNumber(value) {
    if (Number.isInteger(value) && value >= -0x8000000000000000n && value <= 0x7FFFFFFFFFFFFFFFn) {
      return this.encodeInteger(value);
    }
    return this.encodeDouble(value);
  }

  encodeInteger(value) {
    const bytes = [];

    if (value >= 0 && value < 0x100) {
      bytes.push(0x10, value & 0xFF);
    } else if (value >= 0 && value < 0x10000) {
      bytes.push(0x11, (value >> 8) & 0xFF, value & 0xFF);
    } else if (value >= 0 && value < 0x100000000) {
      bytes.push(0x12,
        (value >> 24) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF
      );
    } else {
      const view = new DataView(new ArrayBuffer(8));
      view.setBigInt64(0, BigInt(value), false);
      bytes.push(0x13);
      for (let i = 0; i < 8; i++) {
        bytes.push(view.getUint8(i));
      }
    }

    return new Uint8Array(bytes);
  }

  encodeDouble(value) {
    const view = new DataView(new ArrayBuffer(8));
    view.setFloat64(0, value, false);
    const bytes = [0x23];
    for (let i = 0; i < 8; i++) {
      bytes.push(view.getUint8(i));
    }
    return new Uint8Array(bytes);
  }

  encodeString(value) {
    const bytes = [];

    const isAscii = /^[\x00-\x7F]*$/.test(value);

    if (isAscii) {
      const strBytes = new TextEncoder().encode(value);
      const length = strBytes.length;

      if (length < 15) {
        bytes.push(0x50 | length);
      } else {
        bytes.push(0x5F);
        this.writeVariableLength(bytes, length);
      }

      for (const b of strBytes) {
        bytes.push(b);
      }
    } else {
      const utf16Bytes = [];
      for (let i = 0; i < value.length; i++) {
        const code = value.charCodeAt(i);
        utf16Bytes.push((code >> 8) & 0xFF, code & 0xFF);
      }

      const length = value.length;

      if (length < 15) {
        bytes.push(0x60 | length);
      } else {
        bytes.push(0x6F);
        this.writeVariableLength(bytes, length);
      }

      for (const b of utf16Bytes) {
        bytes.push(b);
      }
    }

    return new Uint8Array(bytes);
  }

  encodeData(value) {
    const bytes = [];
    const data = value instanceof ArrayBuffer ? new Uint8Array(value) : value;
    const length = data.length;

    if (length < 15) {
      bytes.push(0x40 | length);
    } else {
      bytes.push(0x4F);
      this.writeVariableLength(bytes, length);
    }

    for (const b of data) {
      bytes.push(b);
    }

    return new Uint8Array(bytes);
  }

  encodeDate(value) {
    const appleEpoch = new Date('2001-01-01T00:00:00Z').getTime();
    const seconds = (value.getTime() - appleEpoch) / 1000;

    const view = new DataView(new ArrayBuffer(8));
    view.setFloat64(0, seconds, false);

    const bytes = [0x33];
    for (let i = 0; i < 8; i++) {
      bytes.push(view.getUint8(i));
    }

    return new Uint8Array(bytes);
  }

  encodeArray(value, currentIndex) {
    const bytes = [];
    const length = value.length;

    if (length < 15) {
      bytes.push(0xA0 | length);
    } else {
      bytes.push(0xAF);
      this.writeVariableLength(bytes, length);
    }

    const elementIndices = [];
    for (const item of value) {
      elementIndices.push(this.addObject(item));
    }

    const refSize = this.objects.length <= 0xFF ? 1 : this.objects.length <= 0xFFFF ? 2 : 4;

    for (const idx of elementIndices) {
      this.writeInteger(bytes, idx, refSize);
    }

    return new Uint8Array(bytes);
  }

  encodeDict(value, currentIndex) {
    const bytes = [];
    const keys = Object.keys(value);
    const length = keys.length;

    if (length < 15) {
      bytes.push(0xD0 | length);
    } else {
      bytes.push(0xDF);
      this.writeVariableLength(bytes, length);
    }

    const keyIndices = [];
    const valueIndices = [];

    for (const key of keys) {
      keyIndices.push(this.addObject(key));
      valueIndices.push(this.addObject(value[key]));
    }

    const refSize = this.objects.length <= 0xFF ? 1 : this.objects.length <= 0xFFFF ? 2 : 4;

    for (const idx of keyIndices) {
      this.writeInteger(bytes, idx, refSize);
    }

    for (const idx of valueIndices) {
      this.writeInteger(bytes, idx, refSize);
    }

    return new Uint8Array(bytes);
  }

  writeInteger(bytes, value, size) {
    for (let i = size - 1; i >= 0; i--) {
      bytes.push((value >> (i * 8)) & 0xFF);
    }
  }

  writeVariableLength(bytes, value) {
    if (value < 0x100) {
      bytes.push(0x10, value);
    } else if (value < 0x10000) {
      bytes.push(0x11, (value >> 8) & 0xFF, value & 0xFF);
    } else if (value < 0x100000000) {
      bytes.push(0x12,
        (value >> 24) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF
      );
    } else {
      const view = new DataView(new ArrayBuffer(8));
      view.setBigUint64(0, BigInt(value), false);
      bytes.push(0x13);
      for (let i = 0; i < 8; i++) {
        bytes.push(view.getUint8(i));
      }
    }
  }
}

export function encodePlist(value) {
  const encoder = new PlistEncoder();
  return encoder.encode(value);
}

export default PlistEncoder;
