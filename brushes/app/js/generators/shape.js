/**
 * ShapeGenerator.js - Procedural Shape Generation
 *
 * Generates grayscale shape textures for brush stamps.
 * White = mark, black = transparent
 */

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

export const ShapeGenerators = {
  'Hard Circle': (ctx, size = 512) => {
    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 2 - 2, 0, Math.PI * 2);
    ctx.fill();
  },

  'Soft Circle': (ctx, size = 512) => {
    const gradient = ctx.createRadialGradient(
      size / 2, size / 2, 0,
      size / 2, size / 2, size / 2 - 2
    );
    gradient.addColorStop(0, '#FFFFFF');
    gradient.addColorStop(0.7, '#DDDDDD');
    gradient.addColorStop(1, '#000000');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);
  },

  'Splat': (ctx, size = 512, seed = 12345) => {
    const rng = new SeededRandom(seed);
    const centerX = size / 2;
    const centerY = size / 2;
    const maxRadius = size / 2 - 10;

    const bgGradient = ctx.createRadialGradient(
      centerX, centerY, 0,
      centerX, centerY, maxRadius
    );
    bgGradient.addColorStop(0, '#FFFFFF');
    bgGradient.addColorStop(0.8, '#AAAAAA');
    bgGradient.addColorStop(1, '#000000');

    ctx.fillStyle = bgGradient;
    ctx.fillRect(0, 0, size, size);

    const numBlobs = 8 + Math.floor(rng.next() * 8);

    for (let i = 0; i < numBlobs; i++) {
      const angle = (i / numBlobs) * Math.PI * 2 + rng.range(-0.3, 0.3);
      const distance = rng.range(maxRadius * 0.3, maxRadius * 0.8);
      const blobX = centerX + Math.cos(angle) * distance;
      const blobY = centerY + Math.sin(angle) * distance;
      const blobRadius = rng.range(15, 35);

      const blobGradient = ctx.createRadialGradient(
        blobX, blobY, 0,
        blobX, blobY, blobRadius
      );
      blobGradient.addColorStop(0, '#FFFFFF');
      blobGradient.addColorStop(0.5, '#CCCCCC');
      blobGradient.addColorStop(1, 'transparent');

      ctx.fillStyle = blobGradient;
      ctx.beginPath();
      ctx.arc(blobX, blobY, blobRadius, 0, Math.PI * 2);
      ctx.fill();
    }
  },

  'Ink Blot': (ctx, size = 512, seed = 12345) => {
    const rng = new SeededRandom(seed);
    const centerX = size / 2;
    const centerY = size / 2;
    const baseRadius = size / 2 - 20;

    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();

    const points = 12;
    const coords = [];

    for (let i = 0; i < points; i++) {
      const angle = (i / points) * Math.PI * 2;
      const radiusVariation = rng.range(0.7, 1.3);
      const r = baseRadius * radiusVariation;
      const x = centerX + Math.cos(angle) * r;
      const y = centerY + Math.sin(angle) * r;
      coords.push({ x, y });
    }

    ctx.moveTo((coords[0].x + coords[coords.length - 1].x) / 2,
               (coords[0].y + coords[coords.length - 1].y) / 2);

    for (let i = 0; i < points; i++) {
      const next = (i + 1) % points;
      const cpX = (coords[i].x + coords[next].x) / 2;
      const cpY = (coords[i].y + coords[next].y) / 2;
      ctx.quadraticCurveTo(coords[i].x, coords[i].y, cpX, cpY);
    }

    ctx.closePath();
    ctx.fill();

    ctx.globalCompositeOperation = 'destination-out';
    const numHoles = 3 + Math.floor(rng.next() * 5);

    for (let i = 0; i < numHoles; i++) {
      const angle = rng.next() * Math.PI * 2;
      const distance = rng.range(0, baseRadius * 0.6);
      const x = centerX + Math.cos(angle) * distance;
      const y = centerY + Math.sin(angle) * distance;
      const radius = rng.range(5, 15);

      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.globalCompositeOperation = 'source-over';
  },

  'Bristle': (ctx, size = 512, seed = 12345) => {
    const rng = new SeededRandom(seed);
    const centerX = size / 2;
    const centerY = size * 0.8;
    const bristleCount = 20 + Math.floor(rng.next() * 15);

    ctx.strokeStyle = '#FFFFFF';
    ctx.lineCap = 'round';

    for (let i = 0; i < bristleCount; i++) {
      const angle = -Math.PI / 2 + rng.range(-0.4, 0.4);
      const length = size * 0.4 + rng.range(-20, 20);
      const thickness = rng.range(1, 3);

      const endX = centerX + Math.cos(angle) * length;
      const endY = centerY + Math.sin(angle) * length;

      ctx.lineWidth = thickness;
      ctx.globalAlpha = rng.range(0.5, 1);

      ctx.beginPath();
      ctx.moveTo(centerX + rng.range(-10, 10), centerY);
      ctx.quadraticCurveTo(
        centerX + (endX - centerX) * 0.5 + rng.range(-5, 5),
        centerY + (endY - centerY) * 0.5,
        endX + rng.range(-5, 5),
        endY
      );
      ctx.stroke();
    }

    ctx.globalAlpha = 1;
  },

  'Cross Hatch': (ctx, size = 512, seed = 12345) => {
    const rng = new SeededRandom(seed);
    const lineCount = 12;
    const spacing = size / (lineCount + 2);

    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';

    for (let i = 1; i <= lineCount; i++) {
      const y = spacing * i + rng.range(-3, 3);
      ctx.globalAlpha = rng.range(0.4, 0.9);

      ctx.beginPath();
      ctx.moveTo(spacing + rng.range(-5, 5), y);
      ctx.lineTo(size - spacing + rng.range(-5, 5), y);
      ctx.stroke();
    }

    for (let i = 1; i <= lineCount; i++) {
      const x = spacing * i + rng.range(-3, 3);
      ctx.globalAlpha = rng.range(0.4, 0.9);

      ctx.beginPath();
      ctx.moveTo(x, spacing + rng.range(-5, 5));
      ctx.lineTo(x, size - spacing + rng.range(-5, 5));
      ctx.stroke();
    }

    ctx.globalAlpha = 1;
  },

  'Torn Edge': (ctx, size = 512, seed = 12345) => {
    const rng = new SeededRandom(seed);
    const margin = 30;
    const edgePoints = 20;

    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();

    for (let i = 0; i <= edgePoints; i++) {
      const x = margin + (size - margin * 2) * (i / edgePoints);
      const y = margin + rng.range(-8, 8);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }

    for (let i = 0; i <= edgePoints; i++) {
      const x = size - margin + rng.range(-8, 8);
      const y = margin + (size - margin * 2) * (i / edgePoints);
      ctx.lineTo(x, y);
    }

    for (let i = 0; i <= edgePoints; i++) {
      const x = size - margin - (size - margin * 2) * (i / edgePoints);
      const y = size - margin + rng.range(-8, 8);
      ctx.lineTo(x, y);
    }

    for (let i = 0; i <= edgePoints; i++) {
      const x = margin + rng.range(-8, 8);
      const y = size - margin - (size - margin * 2) * (i / edgePoints);
      ctx.lineTo(x, y);
    }

    ctx.closePath();
    ctx.fill();
  },

  'Leaf': (ctx, size = 512) => {
    const centerX = size / 2;
    const centerY = size / 2;
    const width = size * 0.35;
    const height = size * 0.45;

    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();

    ctx.moveTo(centerX, centerY + height);

    ctx.bezierCurveTo(
      centerX + width, centerY + height * 0.5,
      centerX + width, centerY - height * 0.3,
      centerX, centerY - height
    );

    ctx.bezierCurveTo(
      centerX - width, centerY - height * 0.3,
      centerX - width, centerY + height * 0.5,
      centerX, centerY + height
    );

    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle = '#DDDDDD';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(centerX, centerY + height * 0.8);
    ctx.quadraticCurveTo(centerX - 5, centerY, centerX, centerY - height * 0.8);
    ctx.stroke();
  },

  'Star': (ctx, size = 512, seed = 12345) => {
    const rng = new SeededRandom(seed);
    const centerX = size / 2;
    const centerY = size / 2;
    const points = 5 + Math.floor(rng.next() * 3);
    const outerRadius = size / 2 - 15;
    const innerRadius = outerRadius * 0.4;

    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();

    for (let i = 0; i < points * 2; i++) {
      const angle = (i / (points * 2)) * Math.PI * 2 - Math.PI / 2;
      const radius = i % 2 === 0 ? outerRadius : innerRadius;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }

    ctx.closePath();
    ctx.fill();
  },
};

export function generateShape(generatorName, size = 512, seed = 12345) {
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;

  const ctx = canvas.getContext('2d');

  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, size, size);

  const generator = ShapeGenerators[generatorName];
  if (generator) {
    generator(ctx, size, seed);
  }

  return canvas;
}

export function getShapeGeneratorNames() {
  return Object.keys(ShapeGenerators);
}

export default ShapeGenerators;
