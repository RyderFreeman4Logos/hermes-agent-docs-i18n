# 故障排除

## 性能问题

### 第一步——禁用 FES

友好错误系统（FES）会带来极大的性能开销，甚至可能导致速度降低多达 10 倍。请在所有生产环境中的脚本中将其禁用：

```javascript
// BEFORE any p5 code
p5.disableFriendlyErrors = true;

// Or use p5.min.js instead of p5.js — FES is stripped from minified build
```

### 第一步 — pixelDensity(1) 函数

Retina/高DPI显示屏的默认像素密度为2倍或3倍，这会使像素数量增加4到9倍：

```javascript
function setup() {
  pixelDensity(1);        // force 1:1 — always do this first
  createCanvas(1920, 1080);
}
```

### 在高频循环中使用 Math.* 函数

p5 语言中的 `sin()`、`cos()`、`random()`、`min()`、`max()`、`abs()` 等函数均为带有额外开销的封装函数。在高频循环（即每帧需要执行数千次迭代）中，建议直接使用原生的 `Math.*` 函数：

```javascript
// SLOW — p5 wrappers
for (let p of particles) {
  let a = sin(p.angle);
  let d = dist(p.x, p.y, mx, my);
}

// FAST — native Math
for (let p of particles) {
  let a = Math.sin(p.angle);
  let dx = p.x - mx, dy = p.y - my;
  let dSq = dx * dx + dy * dy;  // skip sqrt entirely
}
```

在比较距离时，请使用 `magSq()` 而非 `mag()`，这样可以避免调用耗时的 `sqrt()` 函数。

### 问题诊断

打开 Chrome DevTools > Performance 标签页 > 在绘制代码运行时开始记录。

常见性能瓶颈：
1. **启用了 FES** — 每次调用 p5 函数都会产生 10 倍的额外开销
2. **pixelDensity > 1** — 像素数量增加 4 倍，性能下降 4 倍
3. **绘制调用过多** — 每帧有数千次 `ellipse()` 和 `rect()` 调用
4. **画布过大且涉及像素操作** — 在 4K 画布上使用 `loadPixels()`/`updatePixels()` 函数
5. **粒子系统未经过优化** — 采用全量对比距离的计算方式（时间复杂度为 O(n^2)）
6. **内存泄漏** — 每帧都在创建对象且不进行清理
7. **着色器编译** — 在 `draw()` 函数中而非 `setup()` 函数中调用 `createShader()` 
8. **在 draw() 中使用 console.log()** — 每帧都会进行 DOM 写入，严重影响性能
9. **在 draw() 中操作 DOM** — 会导致布局频繁重算（性能比纯画布操作慢 400-500 倍）

### 解决方案

**减少绘制调用：**
```javascript
// BAD: 10000 individual circles
for (let p of particles) {
  ellipse(p.x, p.y, p.size);
}

// GOOD: single shape with vertices
beginShape(POINTS);
for (let p of particles) {
  vertex(p.x, p.y);
}
endShape();

// BEST: direct pixel manipulation
loadPixels();
for (let p of particles) {
  let idx = 4 * (floor(p.y) * width + floor(p.x));
  pixels[idx] = p.r;
  pixels[idx+1] = p.g;
  pixels[idx+2] = p.b;
  pixels[idx+3] = 255;
}
updatePixels();
```

**用于邻居查询的空间哈希技术：**
```javascript
class SpatialHash {
  constructor(cellSize) {
    this.cellSize = cellSize;
    this.cells = new Map();
  }

  clear() { this.cells.clear(); }

  _key(x, y) {
    return `${floor(x / this.cellSize)},${floor(y / this.cellSize)}`;
  }

  insert(obj) {
    let key = this._key(obj.pos.x, obj.pos.y);
    if (!this.cells.has(key)) this.cells.set(key, []);
    this.cells.get(key).push(obj);
  }

  query(x, y, radius) {
    let results = [];
    let minCX = floor((x - radius) / this.cellSize);
    let maxCX = floor((x + radius) / this.cellSize);
    let minCY = floor((y - radius) / this.cellSize);
    let maxCY = floor((y + radius) / this.cellSize);

    for (let cx = minCX; cx <= maxCX; cx++) {
      for (let cy = minCY; cy <= maxCY; cy++) {
        let key = `${cx},${cy}`;
        let cell = this.cells.get(key);
        if (cell) {
          for (let obj of cell) {
            if (dist(x, y, obj.pos.x, obj.pos.y) <= radius) {
              results.push(obj);
            }
          }
        }
      }
    }
    return results;
  }
}
```

**对象池：**
```javascript
class ParticlePool {
  constructor(maxSize) {
    this.pool = [];
    this.active = [];
    for (let i = 0; i < maxSize; i++) {
      this.pool.push(new Particle(0, 0));
    }
  }

  spawn(x, y) {
    let p = this.pool.pop();
    if (p) {
      p.reset(x, y);
      this.active.push(p);
    }
  }

  update() {
    for (let i = this.active.length - 1; i >= 0; i--) {
      this.active[i].update();
      if (this.active[i].isDead()) {
        this.pool.push(this.active.splice(i, 1)[0]);
      }
    }
  }
}
```

**限制高负载操作：**
```javascript
// Only update flow field every N frames
if (frameCount % 5 === 0) {
  flowField.update(frameCount * 0.001);
}
```

### 帧率目标

| 使用场景 | 目标帧率 | 可接受范围 |
|---------|----------|------------|
| 交互式草图 | 60fps | 30fps |
| 环境动画 | 30fps | 20fps |
| 导出/录制 | 30fps渲染 | 任意帧率（离线场景） |
| 移动端 | 30fps | 20fps |

### 每像素渲染性能预算

基于像素级的操作（如`loadPixels()`循环）是成本最高的常见处理方式。其性能预算取决于画布尺寸以及每像素所需的计算量。

| 画布尺寸 | 像素数量 | 简单噪声算法（1次调用） | fBM算法（4个八度频段） | 域变形算法（3层fBM） |
|---------|----------|----------------------|----------------|--------------------------|
| 540x540 | 291K | 约5ms | 约20ms | 约80ms |
| 1080x1080 | 1.17M | 约20ms | 约80ms | 约300ms以上 |
| 1920x1080 | 2.07M | 约35ms | 约140ms | 约500ms以上 |
| 3840x2160 | 8.3M | 约140ms | 约560ms | 会导致程序崩溃 |

**经验法则：**
- 在1080x1080分辨率下，每像素调用1次`noise()`函数，每帧耗时约20ms（在30fps帧率下可接受）
- 在1080x1080分辨率下，每像素使用4个八度频段的fBM算法，每帧耗时约80ms（处于临界值）
- 在1080x1080分辨率下使用多层域变形算法，每帧耗时300ms以上（无法实现实时渲染，但适用于无循环的导出场景）
- **无头版Chrome在处理像素级操作时的速度比桌面版慢2到5倍**

**解决方案：降低分辨率进行渲染，并采用块状填充方式：**
```javascript
let step = 3;  // render 1/9 of pixels, fill 3x3 blocks
loadPixels();
for (let y = 0; y < H; y += step) {
  for (let x = 0; x < W; x += step) {
    let v = expensiveNoise(x, y);
    for (let dy = 0; dy < step && y+dy < H; dy++)
      for (let dx = 0; dx < step && x+dx < W; dx++) {
        let i = 4 * ((y+dy) * W + (x+dx));
        pixels[i] = v; pixels[i+1] = v; pixels[i+2] = v; pixels[i+3] = 255;
      }
  }
}
updatePixels();
```

将步数设置为2时，处理速度可提升4倍；设置为3时，则可提升9倍。在1080p分辨率下效果清晰可见，对于视频而言也基本可以接受（动态画面会掩盖这一问题）。

## 常见错误

### 1. 忘记重置混合模式

```javascript
blendMode(ADD);
image(glowLayer, 0, 0);
// WRONG: everything after this is ADD blended
blendMode(BLEND);  // ALWAYS reset
```

### 2. 在 draw() 中创建对象

```javascript
// BAD: creates new font object every frame
function draw() {
  let f = loadFont('font.otf');  // NEVER load in draw()
}

// GOOD: load in preload, use in draw
let f;
function preload() { f = loadFont('font.otf'); }
```

### 3. 不要在使用变换功能时调用 push()/pop() 方法

```javascript
// BAD: transforms accumulate
translate(100, 0);
rotate(0.1);
ellipse(0, 0, 50);
// Everything after this is also translated and rotated

// GOOD: isolated transforms
push();
translate(100, 0);
rotate(0.1);
ellipse(0, 0, 50);
pop();
```

### 4. 用于绘制清晰线条的整数坐标

```javascript
// BLURRY: sub-pixel rendering
line(10.5, 20.3, 100.7, 80.2);

// CRISP: integer + 0.5 for 1px lines
line(10.5, 20.5, 100.5, 80.5);  // on pixel boundary
```

### 5. 像素密度相关问题解析

```javascript
// WRONG: assuming pixel array matches canvas dimensions
loadPixels();
let idx = 4 * (y * width + x);  // wrong if pixelDensity > 1

// RIGHT: account for pixel density
let d = pixelDensity();
loadPixels();
let idx = 4 * ((y * d) * (width * d) + (x * d));

// SIMPLEST: set pixelDensity(1) at the start
```

### 6. 颜色模式混淆问题

```javascript
// In HSB mode, fill(255) is NOT white
colorMode(HSB, 360, 100, 100);
fill(255);  // This is hue=255, sat=100, bri=100 = vivid purple

// White in HSB:
fill(0, 0, 100);  // any hue, 0 saturation, 100 brightness

// Black in HSB:
fill(0, 0, 0);
```

### 7. WebGL的原点位于中心位置

```javascript
// In WEBGL mode, (0,0) is CENTER, not top-left
function draw() {
  // This draws at the center, not the corner
  rect(0, 0, 100, 100);

  // For top-left behavior:
  translate(-width/2, -height/2);
  rect(0, 0, 100, 100);  // now at top-left
}
```

### 8. createGraphics 清理操作

```javascript
// BAD: memory leak — buffer never freed
function draw() {
  let temp = createGraphics(width, height);  // new buffer every frame!
  // ...
}

// GOOD: create once, reuse
let temp;
function setup() {
  temp = createGraphics(width, height);
}
function draw() {
  temp.clear();
  // ... reuse temp
}

// If you must create/destroy:
temp.remove();  // explicitly free
```

### 9. noise()函数返回值为0到1之间，而非-1到1。

```javascript
let n = noise(x);  // 0.0 to 1.0 (biased toward 0.5)

// For -1 to 1 range:
let n = noise(x) * 2 - 1;

// For a specific range:
let n = map(noise(x), 0, 1, -100, 100);
```

### 10. draw() 函数中的 saveCanvas() 会保存每一帧画面

```javascript
// BAD: saves a PNG every single frame
function draw() {
  // ... render ...
  saveCanvas('output', 'png');  // DON'T DO THIS
}

// GOOD: save once via keyboard
function keyPressed() {
  if (key === 's') saveCanvas('output', 'png');
}

// GOOD: save once after rendering static piece
function draw() {
  // ... render ...
  saveCanvas('output', 'png');
  noLoop();  // stop after saving
}
```

### 11. draw() 函数中的 console.log() 方法

```javascript
// BAD: writes to DOM console every frame — massive overhead
function draw() {
  console.log(particles.length);  // 60 DOM writes/second
}

// GOOD: log periodically or conditionally
function draw() {
  if (frameCount % 60 === 0) console.log('FPS:', frameRate().toFixed(1));
}
```

### 12. draw() 中的 DOM 操作

```javascript
// BAD: layout thrashing — 400-500x slower than canvas ops
function draw() {
  document.getElementById('counter').innerText = frameCount;
  let el = document.querySelector('.info');  // DOM query per frame
}

// GOOD: cache DOM refs, update infrequently
let counterEl;
function setup() { counterEl = document.getElementById('counter'); }
function draw() {
  if (frameCount % 30 === 0) counterEl.innerText = frameCount;
}
```

### 13. 不要在生产环境中禁用 FES

```javascript
// BAD: every p5 function call has error-checking overhead (up to 10x slower)
function setup() { createCanvas(800, 800); }

// GOOD: disable before any p5 code
p5.disableFriendlyErrors = true;
function setup() { createCanvas(800, 800); }

// ALSO GOOD: use p5.min.js (FES stripped from minified build)
```

## 浏览器兼容性

### Safari相关问题
- WebGL着色器精度：必须始终声明`precision mediump float;`
- `AudioContext`需要用户操作触发（即调用`userStartAudio()`）
- 部分`blendMode()`选项的行为会有所不同

### Firefox相关问题
- `textToPoints()`返回的点数可能略有差异
- WebGL扩展功能可能与Chrome不同
- 颜色配置文件的处理方式可能导致颜色变化

### 移动设备相关问题
- 触摸事件需要通过`return false`来防止页面滚动
- `devicePixelRatio`可能为2倍或3倍——为提升性能建议使用`pixelDensity(1)`
- 建议使用较小的画布尺寸（720p或更低）
- 音频播放同样需要用户明确操作才能启动

## CORS相关问题

```javascript
// Loading images/fonts from external URLs requires CORS headers
// Local files need a server:
// python3 -m http.server 8080

// Or use a CORS proxy for external resources (not recommended for production)
```

## 内存泄漏

### 症状
- 帧率随时间逐渐下降
- 浏览器标签页内存持续无限制增长
- 几分钟后页面变得无响应

### 常见原因

```javascript
// 1. Growing arrays
let history = [];
function draw() {
  history.push(someData);  // grows forever
}
// FIX: cap the array
if (history.length > 1000) history.shift();

// 2. Creating p5 objects in draw()
function draw() {
  let v = createVector(0, 0);  // allocation every frame
}
// FIX: reuse pre-allocated objects

// 3. Unreleased graphics buffers
let layers = [];
function reset() {
  for (let l of layers) l.remove();  // free old buffers
  layers = [];
}

// 4. Event listener accumulation
function setup() {
  // BAD: adds new listener every time setup runs
  window.addEventListener('resize', handler);
}
// FIX: use p5's built-in windowResized()
```

## 调试技巧

### 控制台日志记录

```javascript
// Log once (not every frame)
if (frameCount === 1) {
  console.log('Canvas:', width, 'x', height);
  console.log('Pixel density:', pixelDensity());
  console.log('Renderer:', drawingContext.constructor.name);
}

// Log periodically
if (frameCount % 60 === 0) {
  console.log('FPS:', frameRate().toFixed(1));
  console.log('Particles:', particles.length);
}
```

### 可视化调试

```javascript
// Show frame rate
function draw() {
  // ... your sketch ...
  if (CONFIG.debug) {
    fill(255, 0, 0);
    noStroke();
    textSize(14);
    textAlign(LEFT, TOP);
    text('FPS: ' + frameRate().toFixed(1), 10, 10);
    text('Particles: ' + particles.length, 10, 28);
    text('Frame: ' + frameCount, 10, 46);
  }
}

// Toggle debug with 'd' key
function keyPressed() {
  if (key === 'd') CONFIG.debug = !CONFIG.debug;
}
```

### 隔离问题

```javascript
// Comment out layers to find the slow one
function draw() {
  renderBackground();      // comment out to test
  // renderParticles();    // this might be slow
  // renderPostEffects();  // or this
}
```
