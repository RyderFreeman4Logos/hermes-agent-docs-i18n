# 颜色系统

## 颜色模式

### HSB（适用于生成艺术创作）

```javascript
colorMode(HSB, 360, 100, 100, 100);
// Hue: 0-360 (color wheel position)
// Saturation: 0-100 (gray to vivid)
// Brightness: 0-100 (black to full)
// Alpha: 0-100

fill(200, 80, 90);        // blue, vivid, bright
fill(200, 80, 90, 50);    // 50% transparent
```

HSB模式的优势：
- 色相旋转：`(baseHue + offset) % 360`
- 减淡饱和度：降低S值
- 减暗色调：降低B值
- 单色变体：固定H值，调整S和B值
- 互补色：`(hue + 180) % 360`
- 类似色：`hue +/- 30`

### HSL模式

```javascript
colorMode(HSL, 360, 100, 100, 100);
// Lightness 50 = pure color, 0 = black, 100 = white
// More intuitive for tints (L > 50) and shades (L < 50)
```

### RGB颜色模式

```javascript
colorMode(RGB, 255, 255, 255, 255);  // default
// Direct channel control, less intuitive for procedural palettes
```

## 颜色对象

```javascript
let c = color(200, 80, 90);    // create color object
fill(c);

// Extract components
let h = hue(c);
let s = saturation(c);
let b = brightness(c);
let r = red(c);
let g = green(c);
let bl = blue(c);
let a = alpha(c);

// Hex colors work everywhere
fill('#e8d5b7');
fill('#e8d5b7cc');  // with alpha

// Modify via setters
c.setAlpha(128);
c.setRed(200);
```

## 颜色插值

### lerpColor

```javascript
let c1 = color(0, 80, 100);    // red
let c2 = color(200, 80, 100);  // blue
let mixed = lerpColor(c1, c2, 0.5);  // midpoint blend
// Works in current colorMode
```

### paletteLerp（p5.js 1.11及以上版本）

可同时对多种颜色进行插值处理。

```javascript
let colors = [
  color('#2E0854'),
  color('#850E35'),
  color('#EE6C4D'),
  color('#F5E663')
];
let c = paletteLerp(colors, t);  // t = 0..1, interpolates through all
```

### 手动多止点梯度法

```javascript
function multiLerp(colors, t) {
  t = constrain(t, 0, 1);
  let segment = t * (colors.length - 1);
  let idx = floor(segment);
  let frac = segment - idx;
  idx = min(idx, colors.length - 2);
  return lerpColor(colors[idx], colors[idx + 1], frac);
}
```

## 渐变渲染

### 线性渐变

```javascript
function linearGradient(x1, y1, x2, y2, c1, c2) {
  let steps = dist(x1, y1, x2, y2);
  for (let i = 0; i <= steps; i++) {
    let t = i / steps;
    let c = lerpColor(c1, c2, t);
    stroke(c);
    let x = lerp(x1, x2, t);
    let y = lerp(y1, y2, t);
    // Draw perpendicular line at each point
    let dx = -(y2 - y1) / steps * 1000;
    let dy = (x2 - x1) / steps * 1000;
    line(x - dx, y - dy, x + dx, y + dy);
  }
}
```

### 径向渐变

```javascript
function radialGradient(cx, cy, r, innerColor, outerColor) {
  noStroke();
  for (let i = r; i > 0; i--) {
    let t = 1 - i / r;
    fill(lerpColor(innerColor, outerColor, t));
    ellipse(cx, cy, i * 2);
  }
}
```

### 基于噪声的梯度算法

```javascript
function noiseGradient(colors, noiseScale, time) {
  loadPixels();
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      let n = noise(x * noiseScale, y * noiseScale, time);
      let c = multiLerp(colors, n);
      let idx = 4 * (y * width + x);
      pixels[idx] = red(c);
      pixels[idx+1] = green(c);
      pixels[idx+2] = blue(c);
      pixels[idx+3] = 255;
    }
  }
  updatePixels();
}
```

## 程序化调色板生成

### 互补色模式

```javascript
function complementary(baseHue) {
  return [baseHue, (baseHue + 180) % 360];
}
```

### 类比功能

```javascript
function analogous(baseHue, spread = 30) {
  return [
    (baseHue - spread + 360) % 360,
    baseHue,
    (baseHue + spread) % 360
  ];
}
```

### 三元结构

```javascript
function triadic(baseHue) {
  return [baseHue, (baseHue + 120) % 360, (baseHue + 240) % 360];
}
```

### 分色互补色方案

```javascript
function splitComplementary(baseHue) {
  return [baseHue, (baseHue + 150) % 360, (baseHue + 210) % 360];
}
```

### 四宫格（矩形）

```javascript
function tetradic(baseHue) {
  return [baseHue, (baseHue + 60) % 360, (baseHue + 180) % 360, (baseHue + 240) % 360];
}
```

### 单色变体

```javascript
function monoVariations(hue, count = 5) {
  let colors = [];
  for (let i = 0; i < count; i++) {
    let s = map(i, 0, count - 1, 20, 90);
    let b = map(i, 0, count - 1, 95, 40);
    colors.push(color(hue, s, b));
  }
  return colors;
}
```

## 精选调色板库

### 温暖色调调色板

```javascript
const SUNSET = ['#2E0854', '#850E35', '#EE6C4D', '#F5E663'];
const EMBER  = ['#1a0000', '#4a0000', '#8b2500', '#cd5c00', '#ffd700'];
const PEACH  = ['#fff5eb', '#ffdab9', '#ff9a76', '#ff6b6b', '#c94c4c'];
const COPPER = ['#1c1108', '#3d2b1f', '#7b4b2a', '#b87333', '#daa06d'];
```

### 精致色板

```javascript
const OCEAN   = ['#0a0e27', '#1a1b4b', '#2a4a7f', '#3d7cb8', '#87ceeb'];
const ARCTIC  = ['#0d1b2a', '#1b263b', '#415a77', '#778da9', '#e0e1dd'];
const FOREST  = ['#0b1a0b', '#1a3a1a', '#2d5a2d', '#4a8c4a', '#90c990'];
const DEEP_SEA = ['#000814', '#001d3d', '#003566', '#006d77', '#83c5be'];
```

### 中性色调面板

```javascript
const GRAPHITE = ['#1a1a1a', '#333333', '#555555', '#888888', '#cccccc'];
const CREAM    = ['#f4f0e8', '#e8dcc8', '#c9b99a', '#a89070', '#7a6450'];
const SLATE    = ['#1e293b', '#334155', '#475569', '#64748b', '#94a3b8'];
```

### 生动色彩调色板

```javascript
const NEON     = ['#ff00ff', '#00ffff', '#ff0080', '#80ff00', '#0080ff'];
const RAINBOW  = ['#ff0000', '#ff8000', '#ffff00', '#00ff00', '#0000ff', '#8000ff'];
const VAPOR    = ['#ff71ce', '#01cdfe', '#05ffa1', '#b967ff', '#fffb96'];
const CYBER    = ['#0f0f0f', '#00ff41', '#ff0090', '#00d4ff', '#ffd000'];
```

### 大地色调系列

```javascript
const TERRA    = ['#2c1810', '#5c3a2a', '#8b6b4a', '#c4a672', '#e8d5b7'];
const MOSS     = ['#1a1f16', '#3d4a2e', '#6b7c4f', '#9aab7a', '#c8d4a9'];
const CLAY     = ['#3b2f2f', '#6b4c4c', '#9e7676', '#c9a0a0', '#e8caca'];
```

## 混合模式

```javascript
blendMode(BLEND);       // default — alpha compositing
blendMode(ADD);         // additive — bright glow effects
blendMode(MULTIPLY);    // darkening — shadows, texture overlay
blendMode(SCREEN);      // lightening — soft glow
blendMode(OVERLAY);     // contrast boost — high/low emphasis
blendMode(DIFFERENCE);  // color subtraction — psychedelic
blendMode(EXCLUSION);   // softer difference
blendMode(REPLACE);     // overwrite (no alpha blending)
blendMode(REMOVE);      // subtract alpha
blendMode(LIGHTEST);    // keep brighter pixel
blendMode(DARKEST);     // keep darker pixel
blendMode(BURN);        // darken + saturate
blendMode(DODGE);       // lighten + saturate
blendMode(SOFT_LIGHT);  // subtle overlay
blendMode(HARD_LIGHT);  // strong overlay

// ALWAYS reset after use
blendMode(BLEND);
```

### 混合模式方案

| 效果 | 模式 | 适用场景 |
|------|------|----------|
| 加法发光 | `ADD` | 光束、火焰、粒子效果 |
| 阴影叠加 | `MULTIPLY` | 纹理处理、暗角效果 |
| 柔和光线混合 | `SCREEN` | 雾气、薄雾、背光效果 |
| 高对比度 | `OVERLAY` | 强烈的合成效果 |
| 颜色负片 | `DIFFERENCE` | 故障艺术风格、迷幻效果 |
| 图层合成 | `BLEND` | 标准的阿尔法通道叠加 |

## 背景处理技术

### 纹理背景

```javascript
function texturedBackground(baseColor, noiseScale, noiseAmount) {
  loadPixels();
  let r = red(baseColor), g = green(baseColor), b = blue(baseColor);
  for (let i = 0; i < pixels.length; i += 4) {
    let x = (i / 4) % width;
    let y = floor((i / 4) / width);
    let n = (noise(x * noiseScale, y * noiseScale) - 0.5) * noiseAmount;
    pixels[i] = constrain(r + n, 0, 255);
    pixels[i+1] = constrain(g + n, 0, 255);
    pixels[i+2] = constrain(b + n, 0, 255);
    pixels[i+3] = 255;
  }
  updatePixels();
}
```

### 背景介绍

```javascript
function vignette(strength = 0.5, radius = 0.7) {
  loadPixels();
  let cx = width / 2, cy = height / 2;
  let maxDist = dist(0, 0, cx, cy);
  for (let i = 0; i < pixels.length; i += 4) {
    let x = (i / 4) % width;
    let y = floor((i / 4) / width);
    let d = dist(x, y, cx, cy) / maxDist;
    let factor = 1.0 - smoothstep(constrain((d - radius) / (1 - radius), 0, 1)) * strength;
    pixels[i] *= factor;
    pixels[i+1] *= factor;
    pixels[i+2] *= factor;
  }
  updatePixels();
}

function smoothstep(t) { return t * t * (3 - 2 * t); }
```

### 电影颗粒效果

```javascript
function filmGrain(amount = 30) {
  loadPixels();
  for (let i = 0; i < pixels.length; i += 4) {
    let grain = random(-amount, amount);
    pixels[i] = constrain(pixels[i] + grain, 0, 255);
    pixels[i+1] = constrain(pixels[i+1] + grain, 0, 255);
    pixels[i+2] = constrain(pixels[i+2] + grain, 0, 255);
  }
  updatePixels();
}
```
