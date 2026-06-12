# 核心 API 参考手册

## 画布配置

### createCanvas()

```javascript
// 2D (default renderer)
createCanvas(1920, 1080);

// WebGL (3D, shaders)
createCanvas(1920, 1080, WEBGL);

// Responsive
createCanvas(windowWidth, windowHeight);
```

### 像素密度

高分辨率显示屏默认以2倍像素密度进行渲染。这会导致内存使用量翻倍，同时降低性能表现。

```javascript
// Force 1x for consistent export and performance
pixelDensity(1);

// Match display (default) — sharp on retina but expensive
pixelDensity(displayDensity());

// ALWAYS call before createCanvas()
function setup() {
  pixelDensity(1);        // first
  createCanvas(1920, 1080); // second
}
```

如需导出图像，请始终使用 `pixelDensity(1)` 并设定精确的目标分辨率。切勿依赖设备的缩放功能来生成最终输出。

### 响应式尺寸调整

```javascript
function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  // Recreate offscreen buffers at new size
  bgLayer = createGraphics(width, height);
  // Reinitialize any size-dependent state
}
```

## 坐标系

### P2D（默认）
- 原点：左上角 (0, 0)
- X轴向右增加
- Y轴向下增加
- 角度：默认为弧度制，可使用 `angleMode(DEGREES)` 进行切换

### WEBGL
- 原点：画布中心
- X轴向右增加，Y轴**向上**增加，Z轴朝向观察者增加
- 若想在WEBGL中获得类似P2D的坐标系：使用 `translate(-width/2, -height/2)`

## 绘制循环

```javascript
function preload() {
  // Load assets before setup — fonts, images, JSON, CSV
  // Blocks execution until all loads complete
  font = loadFont('font.otf');
  img = loadImage('texture.png');
  data = loadJSON('data.json');
}

function setup() {
  // Runs once. Create canvas, initialize state.
  createCanvas(1920, 1080);
  colorMode(HSB, 360, 100, 100, 100);
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
}

function draw() {
  // Runs every frame (default 60fps).
  // Set frameRate(30) in setup() to change.
  // Call noLoop() for static sketches (render once).
}
```

### 帧控制

```javascript
frameRate(30);           // set target FPS
noLoop();                // stop draw loop (static pieces)
loop();                  // restart draw loop
redraw();                // call draw() once (manual refresh)
frameCount              // frames since start (integer)
deltaTime               // milliseconds since last frame (float)
millis()                // milliseconds since sketch started
```

## 转换堆栈

每一次转换都会产生累积效应。如需实现隔离处理，可使用 `push()`/`pop()` 函数。

```javascript
push();
  translate(width / 2, height / 2);
  rotate(angle);
  scale(1.5);
  // draw something at transformed position
  ellipse(0, 0, 100, 100);
pop();
// back to original coordinate system
```

### 变换函数

| 函数 | 效果 |
|----------|--------|
| `translate(x, y)` | 移动原点 |
| `rotate(angle)` | 围绕原点旋转（以弧度为单位） |
| `scale(s)` / `scale(sx, sy)` | 从原点开始缩放 |
| `shearX(angle)` | 斜置 X 轴 |
| `shearY(angle)` | 斜置 Y 轴 |
| `applyMatrix(a, b, c, d, e, f)` | 执行任意二维仿射变换 |
| `resetMatrix()` | 清除所有变换 |

### 组合模式：围绕中心旋转

```javascript
push();
  translate(cx, cy);       // move origin to center
  rotate(angle);           // rotate around that center
  translate(-cx, -cy);     // move origin back
  // draw at original coordinates, but rotated around (cx, cy)
  rect(cx - 50, cy - 50, 100, 100);
pop();
```

## 屏外缓冲区（createGraphics）

屏外缓冲区是指可供绘图与合成使用的独立画布。它对于实现以下功能至关重要：
- **分层合成** —— 实现背景、中间层和前景的叠加效果
- **持久轨迹效果** —— 将内容绘制到缓冲区中，通过半透明矩形实现渐隐效果，且无需清除该缓冲区
- **遮罩处理** —— 将遮罩图案绘制到缓冲区中，再通过`image()`函数或像素操作应用该遮罩
- **后期处理** —— 先将场景渲染到缓冲区中，应用各种特效，最后再将结果绘制到主画布上

```javascript
let layer;

function setup() {
  createCanvas(1920, 1080);
  layer = createGraphics(width, height);
}

function draw() {
  // Draw to offscreen buffer
  layer.background(0, 10);  // semi-transparent clear = trails
  layer.fill(255);
  layer.ellipse(mouseX, mouseY, 20);

  // Composite to main canvas
  image(layer, 0, 0);
}
```

### 轨迹效应模式

```javascript
let trailBuffer;

function setup() {
  createCanvas(1920, 1080);
  trailBuffer = createGraphics(width, height);
  trailBuffer.background(0);
}

function draw() {
  // Fade previous frame (lower alpha = longer trails)
  trailBuffer.noStroke();
  trailBuffer.fill(0, 0, 0, 15);  // RGBA — 15/255 alpha
  trailBuffer.rect(0, 0, width, height);

  // Draw new content
  trailBuffer.fill(255);
  trailBuffer.ellipse(mouseX, mouseY, 10);

  // Show
  image(trailBuffer, 0, 0);
}
```

### 多层组合架构

```javascript
let bgLayer, contentLayer, fxLayer;

function setup() {
  createCanvas(1920, 1080);
  bgLayer = createGraphics(width, height);
  contentLayer = createGraphics(width, height);
  fxLayer = createGraphics(width, height);
}

function draw() {
  // Background — drawn once or slowly evolving
  renderBackground(bgLayer);

  // Content — main visual elements
  contentLayer.clear();
  renderContent(contentLayer);

  // FX — overlays, vignettes, grain
  fxLayer.clear();
  renderEffects(fxLayer);

  // Composite with blend modes
  image(bgLayer, 0, 0);
  blendMode(ADD);
  image(contentLayer, 0, 0);
  blendMode(MULTIPLY);
  image(fxLayer, 0, 0);
  blendMode(BLEND);  // reset
}
```

## 组合模式

### 网格布局

```javascript
let cols = 10, rows = 10;
let cellW = width / cols;
let cellH = height / rows;
for (let i = 0; i < cols; i++) {
  for (let j = 0; j < rows; j++) {
    let cx = cellW * (i + 0.5);
    let cy = cellH * (j + 0.5);
    // draw element at (cx, cy) within cell size (cellW, cellH)
  }
}
```

### 径向布局

```javascript
let n = 12;
for (let i = 0; i < n; i++) {
  let angle = TWO_PI * i / n;
  let r = 300;
  let x = width/2 + cos(angle) * r;
  let y = height/2 + sin(angle) * r;
  // draw element at (x, y)
}
```

### 金角螺旋

```javascript
let phi = (1 + sqrt(5)) / 2;
let n = 500;
for (let i = 0; i < n; i++) {
  let angle = i * TWO_PI / (phi * phi);
  let r = sqrt(i) * 10;
  let x = width/2 + cos(angle) * r;
  let y = height/2 + sin(angle) * r;
  let size = map(i, 0, n, 8, 2);
  ellipse(x, y, size);
}
```

### 考虑边距的合成功能

```javascript
const MARGIN = 80;  // pixels from edge
const drawW = width - 2 * MARGIN;
const drawH = height - 2 * MARGIN;

// Map normalized [0,1] coordinates to drawable area
function mapX(t) { return MARGIN + t * drawW; }
function mapY(t) { return MARGIN + t * drawH; }
```

## 随机性与噪声

### 基于种子的随机生成

```javascript
randomSeed(42);
let x = random(100);        // always same value for seed 42
let y = random(-1, 1);      // range
let item = random(myArray);  // random element
```

### 高斯随机数

```javascript
let x = randomGaussian(0, 1);  // mean=0, stddev=1
// Useful for natural-looking distributions
```

### 帕尔林噪声

```javascript
noiseSeed(42);
noiseDetail(4, 0.5);  // 4 octaves, 0.5 falloff

let v = noise(x * 0.01, y * 0.01);  // returns 0.0 to 1.0
// Scale factor (0.01) controls feature size — smaller = smoother
```

## 数学工具函数

| 函数 | 描述 |
|------|------|
| `map(v, lo1, hi1, lo2, hi2)` | 在指定范围之间重新映射数值 |
| `constrain(v, lo, hi)` | 将数值限制在指定范围内 |
| `lerp(a, b, t)` | 线性插值 |
| `norm(v, lo, hi)` | 将数值归一化为 0-1 范围 |
| `dist(x1, y1, x2, y2)` | 欧几里得距离 |
| `mag(x, y)` | 向量模长 |
| `abs()`, `ceil()`, `floor()`, `round()` | 基本数学运算 |
| `sq(n)`, `sqrt(n)`, `pow(b, e)` | 幂运算 |
| `sin()`, `cos()`, `tan()`, `atan2()` | 三角函数（以弧度为单位） |
| `degrees(r)`, `radians(d)` | 角度转换 |
| `fract(n)` | 取小数部分 |

## p5.js 2.0 的变更

p5.js 2.0（2025 年 4 月发布，当前版本为 2.2）引入了一些破坏性变更。在 2026 年 8 之前，p5.js 编辑器默认使用 1.x 版本。只有在使用其新功能时才建议使用 2.x 版本。

### `async setup()` 已取代 `preload()`

```javascript
// p5.js 1.x
let img;
function preload() { img = loadImage('cat.jpg'); }
function setup() { createCanvas(800, 800); }

// p5.js 2.x
let img;
async function setup() {
  createCanvas(800, 800);
  img = await loadImage('cat.jpg');
}
```

### 新增颜色模式

```javascript
colorMode(OKLCH);  // perceptually uniform — better gradients
// L: 0-1 (lightness), C: 0-0.4 (chroma), H: 0-360 (hue)
fill(0.7, 0.15, 200);  // medium-bright saturated blue

colorMode(OKLAB);  // perceptually uniform, no hue angle
colorMode(HWB);    // Hue-Whiteness-Blackness
```

### splineVertex() 已取代 curveVertex()

无需再重复设置第一个/最后一个控制点：

```javascript
// p5.js 1.x — must repeat first and last
beginShape();
curveVertex(pts[0].x, pts[0].y);  // doubled
for (let p of pts) curveVertex(p.x, p.y);
curveVertex(pts[pts.length-1].x, pts[pts.length-1].y);  // doubled
endShape();

// p5.js 2.x — clean
beginShape();
for (let p of pts) splineVertex(p.x, p.y);
endShape();
```

### Shader .modify() API

无需编写完整的 GLSL 代码即可修改内置着色器：

```javascript
let myShader = baseMaterialShader().modify({
  vertexDeclarations: 'uniform float uTime;',
  'vec4 getWorldPosition': `(vec4 pos) {
    pos.y += sin(pos.x * 0.1 + uTime) * 20.0;
    return pos;
  }`
});
```

### 变体字体

```javascript
textWeight(700);  // dynamic weight without loading multiple files
```

### textToContours() 函数与 textToModel() 函数

```javascript
let contours = font.textToContours('HELLO', 0, 0, 200);
// Returns array of contour arrays (closed paths)

let geo = font.textToModel('HELLO', 0, 0, 200);
// Returns p5.Geometry for 3D extruded text
```

### 适用于 p5.js 2.x 的 CDN 解决方案

```html
<script src="https://cdn.jsdelivr.net/npm/p5@2/lib/p5.min.js"></script>
```
