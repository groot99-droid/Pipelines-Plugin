/**
 * GrainGenerator.js - Procedural Grain Generation
 *
 * Generates grayscale grain textures for brush texture.
 * Uses Perlin noise for organic textures.
 */

class PerlinNoise {
  constructor(seed = 12345) {
    this.seed = seed;
    this.permutation = this.generatePermutation();
  }

  generatePermutation() {
    const p = new Array(256);
    for (let i = 0; i < 256; i++) {
      p[i] = i;
    }

    let seed = this.seed;
    for (let i = 255; i > 0; i--) {
      seed = (seed * 16807) % 2147483647;
      const j = seed % (i + 1);
      [p[i], p[j]] = [p[j], p[i]];
    }

    return [...p, ...p];
  }

  fade(t) {
    return t * t * t * (t * (t * 6 - 15) + 10);
  }

  lerp(t, a, b) {
    return a + t * (b - a);
  }

  grad(hash, x, y) {
    const h = hash & 15;
    const u = h < 8 ? x : y;
    const v = h < 4 ? y : h === 12 || h === 14 ? x : 0;
    return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v);
  }

  noise(x, y) {
    const X = Math.floor(x) & 255;
    const Y = Math.floor(y) & 255;

    x -= Math.floor(x);
    y -= Math.floor(y);

    const u = this.fade(x);
    const v = this.fade(y);

    const A = this.permutation[X] + Y;
    const AA = this.permutation[A];
    const AB = this.permutation[A + 1];
    const B = this.permutation[X + 1] + Y;
    const BA = this.permutation[B];
    const BB = this.permutation[B + 1];

    return this.lerp(v,
      this.lerp(u, this.grad(this.permutation[AA], x, y),
                   this.grad(this.permutation[BA], x - 1, y)),
      this.lerp(u, this.grad(this.permutation[AB], x, y - 1),
                   this.grad(this.permutation[BB], x - 1, y - 1))
    );
  }

  fbm(x, y, octaves = 4, persistence = 0.5, lacunarity = 2) {
    let total = 0;
    let frequency = 1;
    let amplitude = 1;
    let maxValue = 0;

    for (let i = 0; i < octaves; i++) {
      total += this.noise(x * frequency, y * frequency) * amplitude;
      maxValue += amplitude;
      amplitude *= persistence;
      frequency *= lacunarity;
    }

    return total / maxValue;
  }
}

// Bug fix: add range() method that generators use
class SeededRandom {
  constructor(seed = 12345) {
    this.seed = seed;
  }

  next() {
    this.seed = (this.seed * 16807) % 2147483647;
    return (this.seed - 1) / 2147483646;
  }

  range(min, max) {
    return min + this.next() * (max - min);
  }
}

export const GrainGenerators = {
  'Flat': (ctx, size = 1024) => {
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, size, size);
  },

  'Paper Fine': (ctx, size = 1024, seed = 12345) => {
    const noise = new PerlinNoise(seed);
    const imageData = ctx.createImageData(size, size);
    const data = imageData.data;

    const scale = 0.02;

    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const n = noise.fbm(x * scale, y * scale, 3, 0.5, 2);
        const value = Math.floor((n * 0.15 + 0.85) * 255);
        const idx = (y * size + x) * 4;
        data[idx] = value;
        data[idx + 1] = value;
        data[idx + 2] = value;
        data[idx + 3] = 255;
      }
    }

    ctx.putImageData(imageData, 0, 0);
  },

  'Paper Rough': (ctx, size = 1024, seed = 12345) => {
    const noise = new PerlinNoise(seed);
    const imageData = ctx.createImageData(size, size);
    const data = imageData.data;

    const scale = 0.008;

    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const n = noise.fbm(x * scale, y * scale, 4, 0.6, 2);
        const value = Math.floor((n * 0.25 + 0.75) * 255);
        const idx = (y * size + x) * 4;
        data[idx] = value;
        data[idx + 1] = value;
        data[idx + 2] = value;
        data[idx + 3] = 255;
      }
    }

    ctx.putImageData(imageData, 0, 0);
  },

  'Canvas': (ctx, size = 1024, seed = 12345) => {
    const rng = new SeededRandom(seed);

    ctx.fillStyle = '#DDDDDD';
    ctx.fillRect(0, 0, size, size);

    const threadSpacing = 8;
    const threadWidth = 2;

    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = threadWidth;

    for (let i = -size; i < size * 2; i += threadSpacing) {
      ctx.globalAlpha = rng.range(0.6, 1);
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i + size, size);
      ctx.stroke();
    }

    ctx.strokeStyle = '#BBBBBB';
    for (let i = -size; i < size * 2; i += threadSpacing) {
      ctx.globalAlpha = rng.range(0.4, 0.8);
      ctx.beginPath();
      ctx.moveTo(i + size, 0);
      ctx.lineTo(i, size);
      ctx.stroke();
    }

    ctx.globalAlpha = 1;

    const noise = new PerlinNoise(seed + 1);
    const imageData = ctx.getImageData(0, 0, size, size);
    const data = imageData.data;

    for (let y = 0; y < size; y += 2) {
      for (let x = 0; x < size; x += 2) {
        const n = noise.noise(x * 0.05, y * 0.05);
        const variation = Math.floor(n * 20);
        const idx = (y * size + x) * 4;
        data[idx] = Math.max(0, Math.min(255, data[idx] + variation));
        data[idx + 1] = Math.max(0, Math.min(255, data[idx + 1] + variation));
        data[idx + 2] = Math.max(0, Math.min(255, data[idx + 2] + variation));
      }
    }

    ctx.putImageData(imageData, 0, 0);
  },

  'Cold Press': (ctx, size = 1024, seed = 12345) => {
    const noise = new PerlinNoise(seed);
    const rng = new SeededRandom(seed);

    const imageData = ctx.createImageData(size, size);
    const data = imageData.data;

    const scale1 = 0.005;
    const scale2 = 0.02;

    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const n1 = noise.fbm(x * scale1, y * scale1, 2, 0.5, 2);
        const n2 = noise.fbm(x * scale2, y * scale2, 3, 0.4, 2);

        const combined = n1 * 0.6 + n2 * 0.4;
        const value = Math.floor((combined * 0.3 + 0.7) * 255);

        const idx = (y * size + x) * 4;
        data[idx] = value;
        data[idx + 1] = value;
        data[idx + 2] = value;
        data[idx + 3] = 255;
      }
    }

    ctx.putImageData(imageData, 0, 0);

    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 1;

    const fiberCount = 100;
    for (let i = 0; i < fiberCount; i++) {
      const x = rng.next() * size;
      const y = rng.next() * size;
      const length = rng.range(20, 80);
      const angle = rng.range(-0.3, 0.3);

      ctx.globalAlpha = rng.range(0.1, 0.3);
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + Math.cos(angle) * length, y + Math.sin(angle) * length);
      ctx.stroke();
    }

    ctx.globalAlpha = 1;
  },

  'Linen': (ctx, size = 1024, seed = 12345) => {
    const rng = new SeededRandom(seed);

    ctx.fillStyle = '#E8E8E8';
    ctx.fillRect(0, 0, size, size);

    const threadSpacing = 6;

    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 1.5;

    for (let y = 0; y < size; y += threadSpacing) {
      ctx.globalAlpha = rng.range(0.5, 0.9);
      ctx.beginPath();

      let currentX = 0;
      let currentY = y + rng.range(-1, 1);
      ctx.moveTo(currentX, currentY);

      while (currentX < size) {
        currentX += rng.range(10, 30);
        currentY = y + rng.range(-1, 1);
        ctx.lineTo(Math.min(currentX, size), currentY);
      }

      ctx.stroke();
    }

    ctx.strokeStyle = '#D0D0D0';

    for (let x = 0; x < size; x += threadSpacing) {
      ctx.globalAlpha = rng.range(0.4, 0.7);
      ctx.beginPath();

      let currentY = 0;
      let currentX = x + rng.range(-1, 1);
      ctx.moveTo(currentX, currentY);

      while (currentY < size) {
        currentY += rng.range(10, 30);
        currentX = x + rng.range(-1, 1);
        ctx.lineTo(currentX, Math.min(currentY, size));
      }

      ctx.stroke();
    }

    ctx.globalAlpha = 1;
  },

  'Concrete': (ctx, size = 1024, seed = 12345) => {
    const noise = new PerlinNoise(seed);
    const imageData = ctx.createImageData(size, size);
    const data = imageData.data;

    const scale = 0.003;

    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const n = noise.fbm(x * scale, y * scale, 5, 0.5, 2);
        const value = Math.floor((n * 0.4 + 0.5) * 255);
        const idx = (y * size + x) * 4;
        data[idx] = value;
        data[idx + 1] = value;
        data[idx + 2] = value;
        data[idx + 3] = 255;
      }
    }

    ctx.putImageData(imageData, 0, 0);
  },

  'Noise': (ctx, size = 1024, seed = 12345) => {
    const rng = new SeededRandom(seed);
    const imageData = ctx.createImageData(size, size);
    const data = imageData.data;

    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const value = Math.floor(rng.next() * 55 + 200);
        const idx = (y * size + x) * 4;
        data[idx] = value;
        data[idx + 1] = value;
        data[idx + 2] = value;
        data[idx + 3] = 255;
      }
    }

    ctx.putImageData(imageData, 0, 0);
  },
};

export function generateGrain(generatorName, size = 1024, seed = 12345) {
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;

  const ctx = canvas.getContext('2d');

  const generator = GrainGenerators[generatorName];
  if (generator) {
    generator(ctx, size, seed);
  } else {
    GrainGenerators['Flat'](ctx, size);
  }

  return canvas;
}

export function getGrainGeneratorNames() {
  return Object.keys(GrainGenerators);
}

export default GrainGenerators;
