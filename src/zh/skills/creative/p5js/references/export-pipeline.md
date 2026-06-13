# 导出流程

## PNG格式导出

### 直接在草图界面中操作（快捷键）

```javascript
function keyPressed() {
  if (key === 's' || key === 'S') {
    saveCanvas('output', 'png');
    // Downloads output.png immediately
  }
}
```

### 定时导出（静态生成）

```javascript
function setup() {
  createCanvas(3840, 2160);
  pixelDensity(1);
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  noLoop();
}

function draw() {
  // ... render everything ...
  saveCanvas('output-seed-' + CONFIG.seed, 'png');
}
```

### 高分辨率导出

对于超出屏幕尺寸的分辨率，可使用 `pixelDensity()` 函数或较大的离屏缓冲区来实现。

```javascript
function exportHighRes(scale) {
  let buffer = createGraphics(width * scale, height * scale);
  buffer.scale(scale);
  // Re-render everything to buffer at higher resolution
  renderScene(buffer);
  buffer.save('highres-output.png');
}
```

### 批量种子导出

```javascript
function exportBatch(startSeed, count) {
  for (let i = 0; i < count; i++) {
    CONFIG.seed = startSeed + i;
    randomSeed(CONFIG.seed);
    noiseSeed(CONFIG.seed);
    // Render
    background(0);
    renderScene();
    saveCanvas('seed-' + nf(CONFIG.seed, 5), 'png');
  }
}
```

## GIF导出

### saveGif()

```javascript
function keyPressed() {
  if (key === 'g' || key === 'G') {
    saveGif('output', 5);
    // Captures 5 seconds of animation
    // Options: saveGif(filename, duration, options)
  }
}

// With options
saveGif('output', 5, {
  delay: 0,        // delay before starting capture (seconds)
  units: 'seconds' // or 'frames'
});
```

限制事项：
- GIF格式最多支持256种颜色，因此渐变效果会出现抖动伪影
- 过大的画布尺寸会导致文件体积急剧增大
- 制作GIF时建议使用较小的画布（640x360），而PNG/MP4格式则可选用更大尺寸的画布
- 帧率仅为近似值

### GIF的最佳设置参数

```javascript
// For GIF output, use smaller canvas and lower framerate
function setup() {
  createCanvas(640, 360);
  frameRate(15);  // GIF standard
  pixelDensity(1);
}
```

## 帧序列导出

### saveFrames()

```javascript
function keyPressed() {
  if (key === 'f') {
    saveFrames('frame', 'png', 10, 30);
    // 10 seconds, 30 fps → 300 PNG files
    // Downloads as individual files (browser may block bulk downloads)
  }
}
```

### 手动导出框架（更高程度掌控）

```javascript
let recording = false;
let frameNum = 0;
const TOTAL_FRAMES = 300;

function keyPressed() {
  if (key === 'r') recording = !recording;
}

function draw() {
  // ... render frame ...

  if (recording) {
    saveCanvas('frame-' + nf(frameNum, 4), 'png');
    frameNum++;
    if (frameNum >= TOTAL_FRAMES) {
      recording = false;
      noLoop();
      console.log('Recording complete: ' + frameNum + ' frames');
    }
  }
}
```

### 确定性捕获（对视频处理至关重要）

若要实现完美无缺的无头模式帧捕获，必须采用 `noLoop()` + `redraw()` 的组合方式。否则，在 Chrome 中 p5 的绘制循环会持续运行，而 Puppeteer 的截图速度则会变得极为缓慢——这会导致渲染进度超前，进而出现帧重复或缺失的问题。

```javascript
function setup() {
  createCanvas(1920, 1080);
  pixelDensity(1);
  noLoop();                    // STOP the automatic draw loop
  window._p5Ready = true;      // Signal to capture script
}

function draw() {
  // This only runs when redraw() is called by the capture script
  // frameCount increments exactly once per redraw()
}
```

随附的 `scripts/export-frames.js` 脚本会检测 `window._p5Ready` 的存在，并自动切换到确定性模式。若未使用该脚本，则会回退到定时捕获方式（精度较低）。 

### ffmpeg：将帧导出为 MP4 文件

```bash
# Basic encoding
ffmpeg -framerate 30 -i frame-%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# High quality
ffmpeg -framerate 30 -i frame-%04d.png \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  output.mp4

# With audio
ffmpeg -framerate 30 -i frame-%04d.png -i audio.mp3 \
  -c:v libx264 -c:a aac -shortest \
  output.mp4

# Loop for social media (3 loops)
ffmpeg -stream_loop 2 -i output.mp4 -c copy output-looped.mp4
```

### 视频导出时的注意事项

**YUV420格式会导致画面过暗。** H.264编码采用YUV420色彩空间，该空间会对较暗的RGB数值进行四舍五入处理。RGB(8,8,8)以下的颜色值可能会变为纯黑色。那些细微的暗部细节（如微弱的粒子轨迹、淡色的噪声纹理），虽然在PNG格式的帧中清晰可见，但在编码后的视频中却会消失不见。

**解决方法：** 确保所有可见内容的最低亮度在10左右。可以通过编码几帧并对比MP4格式的视频帧与原始PNG文件，来进行测试。

```bash
# Extract a frame from MP4 for comparison
ffmpeg -i output.mp4 -vf "select=eq(n\,100)" -vframes 1 check.png
```

**静态画面在视频中会显得异常。** 如果某个算法仅生成单张静态图像（例如预先计算好的吸引子热图），在视频中就会呈现为卡顿或故障画面。即便是静态内容，也务必添加动画效果：
- 逐步展示效果（从中心向外扩展、横向扫描）
- 缓慢参数变化（调整颜色映射、微调噪声偏移量）
- 类摄像机运镜效果（缓慢缩放、轻微平移）
- 添加动态粒子或颗粒叠加效果

**场景切换是必不可少的。** 视觉风格截然不同的场景之间生硬切换会显得十分突兀。建议使用渐变过渡效果：

```javascript
const FADE_FRAMES = 15;  // half-second at 30fps
let fade = 1;
if (localFrame < FADE_FRAMES) fade = localFrame / FADE_FRAMES;
if (localFrame > SCENE_FRAMES - FADE_FRAMES) fade = (SCENE_FRAMES - localFrame) / FADE_FRAMES;
fade = fade * fade * (3 - 2 * fade);  // smoothstep
// Apply: multiply all alpha/brightness by fade
```

### 单片段架构（多场景视频）

对于包含多个场景的视频，需将每个场景分别渲染为独立的 HTML 文件和 MP4 片段，再通过 ffmpeg 将其拼接在一起。这样一来，即便需要重新渲染某个场景，也不会影响到其他场景。

**目录结构：**
```
project/
├── capture-scene.js          # Shared: node capture-scene.js <html> <outdir> <frames>
├── render-all.sh             # Renders all + stitches
├── scenes/
│   ├── 00-intro.html         # Each scene is self-contained
│   ├── 01-particles.html
│   ├── 02-noise.html
│   └── 03-outro.html
└── clips/
    ├── 00-intro.mp4          # Each clip rendered independently
    ├── 01-particles.mp4
    ├── 02-noise.mp4
    ├── 03-outro.mp4
    └── concat.txt
```

**使用 ffmpeg 的 concat 功能拼接片段：**
```bash
# concat.txt (order determines final sequence)
file '00-intro.mp4'
file '01-particles.mp4'
file '02-noise.mp4'
file '03-outro.mp4'

# Lossless stitch (all clips must have same codec/resolution/fps)
ffmpeg -f concat -safe 0 -i concat.txt -c copy final.mp4
```

**重新渲染单个场景：**
```bash
node capture-scene.js scenes/01-particles.html clips/01-particles 150
ffmpeg -y -framerate 30 -i clips/01-particles/frame-%04d.png \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p clips/01-particles.mp4
# Then re-stitch
ffmpeg -y -f concat -safe 0 -i clips/concat.txt -c copy final.mp4
```

**无需重新渲染即可调整顺序：** 只需修改 concat.txt 中的顺序并再次进行拼接操作，无需重新渲染任何帧。

**每个场景的 HTML 文件必须满足以下要求：**
- 在初始化阶段调用 `noLoop()` 并设置 `window._p5Ready = true`
- 为确保输出结果的一致性，需使用基于 `frameCount` 的计时方式（而非 `millis()`）
- 自行实现淡入/淡出效果
- 完全独立，各场景之间不得共享状态

### ffmpeg：将帧序列转换为 GIF 格式（更高质量）

```bash
# Generate palette first for optimal colors
ffmpeg -i frame-%04d.png -vf "fps=15,palettegen=max_colors=256" palette.png

# Render GIF using palette
ffmpeg -i frame-%04d.png -i palette.png \
  -lavfi "fps=15 [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=3" \
  output.gif
```

## 无头模式导出（Puppeteer）

适用于自动化处理、服务器端渲染或持续集成场景。通过无头版 Chrome 浏览器来执行绘图任务。

### export-frames.js（Node.js 脚本）

完整实现代码请参见 `scripts/export-frames.js` 文件。基本结构如下：

```javascript
const puppeteer = require('puppeteer');

async function captureFrames(htmlPath, outputDir, options) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  await page.setViewport({
    width: options.width || 1920,
    height: options.height || 1080,
    deviceScaleFactor: 1
  });

  await page.goto(`file://${path.resolve(htmlPath)}`, {
    waitUntil: 'networkidle0'
  });

  // Wait for sketch to initialize
  await page.waitForSelector('canvas');
  await page.waitForTimeout(1000);

  for (let i = 0; i < options.frames; i++) {
    const canvas = await page.$('canvas');
    await canvas.screenshot({
      path: path.join(outputDir, `frame-${String(i).padStart(4, '0')}.png`)
    });

    // Advance one frame
    await page.evaluate(() => { redraw(); });
    await page.waitForTimeout(1000 / options.fps);
  }

  await browser.close();
}
```

### render.sh（完整处理流程）

完整的渲染脚本请参见 `scripts/render.sh`。处理流程如下：

```
1. Launch Puppeteer → open sketch HTML
2. Capture N frames as PNG sequence
3. Pipe to ffmpeg → encode H.264 MP4
4. Optional: add audio track
5. Clean up temp frames
```

## SVG导出功能

### 使用p5.js-svg库

```html
<script src="https://unpkg.com/p5.js-svg@1.5.1"></script>
```

```javascript
function setup() {
  createCanvas(1920, 1080, SVG);  // SVG renderer
  noLoop();
}

function draw() {
  // Only vector operations (no pixels, no blend modes)
  stroke(0);
  noFill();
  for (let i = 0; i < 100; i++) {
    let x = random(width);
    let y = random(height);
    ellipse(x, y, random(10, 50));
  }
  save('output.svg');
}
```

限制事项：  
- 不支持 `loadPixels()`、`updatePixels()`、`filter()`、`blendMode()`  
- 不支持 WebGL  
- 不支持像素级特效  
- 适用场景：线条艺术、几何图案、图表  

### 混合模式：光栅背景 + SVG 叠加  
先将背景效果渲染为 PNG，再在上方叠加 SVG 以呈现清晰的矢量元素。  

## 导出格式选择指南  

| 需求 | 格式 | 方法 |
|------|------|------|
| 单张静态图片 | PNG | `saveCanvas()` 或 `keyPressed()` |
| 打印级质量静态图 | 高分辨率 PNG | `pixelDensity(1)` + 大尺寸画布 |
| 短时长动画循环 | GIF | `saveGif()` |
| 长时长动画 | MP4 | 逐帧序列 + ffmpeg |
| 社交媒体视频 | MP4 | `scripts/render.sh` |
| 矢量/打印用图 | SVG | p5.js-svg 渲染器 |
| 批量不同版本 | PNG 序列 | 种子循环 + `saveCanvas()` |
| 交互式部署 | HTML | 单个独立文件 |
| 无界面渲染 | PNG/MP4 | Puppeteer + ffmpeg |

## 超高分辨率的平铺处理  
对于超出单张画布承载范围的分辨率（例如用于打印的 10000×10000）：

```javascript
function renderTiled(totalW, totalH, tileSize) {
  let cols = ceil(totalW / tileSize);
  let rows = ceil(totalH / tileSize);

  for (let ty = 0; ty < rows; ty++) {
    for (let tx = 0; tx < cols; tx++) {
      let buffer = createGraphics(tileSize, tileSize);
      buffer.push();
      buffer.translate(-tx * tileSize, -ty * tileSize);
      renderScene(buffer, totalW, totalH);
      buffer.pop();
      buffer.save(`tile-${tx}-${ty}.png`);
      buffer.remove();  // free memory
    }
  }
  // Stitch with ImageMagick:
  // montage tile-*.png -tile 4x4 -geometry +0+0 final.png
}
```

## CCapture.js — 确定性视频捕获功能

内置的 `saveFrames()` 函数存在诸多局限性：捕获的帧数较少、易出现内存问题，同时还无法实现浏览器内的直接下载。CCapture.js 通过接入浏览器的计时功能，能够无视实际的渲染速度，始终保持固定的时间间隔，从而解决了所有这些问题。

```html
<script src="https://cdn.jsdelivr.net/npm/ccapture.js-npmfixed/build/CCapture.all.min.js"></script>
```

### 基本设置

```javascript
let capturer;
let recording = false;

function setup() {
  createCanvas(1920, 1080);
  pixelDensity(1);

  capturer = new CCapture({
    format: 'webm',       // 'webm', 'gif', 'png', 'jpg'
    framerate: 30,
    quality: 99,           // 0-100 for webm/jpg
    // timeLimit: 10,      // auto-stop after N seconds
    // motionBlurFrames: 4 // supersampled motion blur
  });
}

function draw() {
  // ... render frame ...

  if (recording) {
    capturer.capture(document.querySelector('canvas'));
  }
}

function keyPressed() {
  if (key === 'c') {
    if (!recording) {
      capturer.start();
      recording = true;
      console.log('Recording started');
    } else {
      capturer.stop();
      capturer.save();  // triggers download
      recording = false;
      console.log('Recording saved');
    }
  }
}
```

### 格式对比

| 格式 | 质量 | 文件大小 | 浏览器支持情况 |
|------|------|----------|----------------|
| **WebM** | 高 | 中等 | 仅 Chrome |
| **GIF** | 256色 | 较大 | 所有浏览器（通过 gif.js worker 实现） |
| **PNG序列** | 无损 | 非常大（以TAR格式存储） | 所有浏览器 |
| **JPEG序列** | 有损 | 较大（以TAR格式存储） | 所有浏览器 |

### 重要提示：时间处理机制

CCapture.js 会覆盖 `Date.now()`、`setTimeout`、`requestAnimationFrame` 和 `performance.now()` 这些函数。这意味着：
- `millis()` 返回的是模拟时间（非常适合录制需求）
- `deltaTime` 为固定值（1000/帧率）
- 即使每帧处理时间长达500毫秒，仍能以30fps的流畅速度进行录制
- **注意**：音频同步会失效（音频将按实时时间播放，而非模拟时间）

## 编程方式导出（canvas API）

对于需要超出 `saveCanvas()` 功能的自定义导出流程：

```javascript
// Canvas to Blob (for upload, processing)
document.querySelector('canvas').toBlob((blob) => {
  // Upload to server, process, etc.
  let url = URL.createObjectURL(blob);
  console.log('Blob URL:', url);
}, 'image/png');

// Canvas to Data URL (for inline embedding)
let dataUrl = document.querySelector('canvas').toDataURL('image/png');
// Use in <img src="..."> or send as base64
```

## SVG导出（p5.js-svg）

```html
<script src="https://unpkg.com/p5.js-svg@1.6.0"></script>
```

```javascript
function setup() {
  createCanvas(1920, 1080, SVG);  // SVG renderer
  noLoop();
}

function draw() {
  // Only vector operations work (no pixel ops, no blendMode)
  stroke(0);
  noFill();
  for (let i = 0; i < 100; i++) {
    ellipse(random(width), random(height), random(10, 50));
  }
  save('output.svg');
}
```

**SVG 使用的重要注意事项：**
- 对于动态绘制的图形，**必须在 `draw()` 函数中调用 `clear()`**——SVG DOM 会不断累积子元素，从而导致内存占用过高
- SVG 渲染器**不支持** `blendMode()` 函数
- `filter()`、`loadPixels()`、`updatePixels()` 等函数也无法正常使用
- 需要 **p5.js 1.11.x 版本**——与 p5.js 2.x 不兼容
- 非常适合用于：线条艺术、几何图案以及绘图仪输出内容

## 平台导出

### fxhash 规范

```javascript
// Replace p5's random with fxhash's deterministic PRNG
const rng = $fx.rand;

// Declare features for rarity/filtering
$fx.features({
  'Palette': paletteName,
  'Complexity': complexity > 0.7 ? 'High' : 'Low',
  'Has Particles': particleCount > 0
});

// Declare on-chain parameters
$fx.params([
  { id: 'density', name: 'Density', type: 'number',
    options: { min: 1, max: 100, step: 1 } },
  { id: 'palette', name: 'Palette', type: 'select',
    options: { options: ['Warm', 'Cool', 'Mono'] } },
  { id: 'accent', name: 'Accent Color', type: 'color' }
]);

// Read params
let density = $fx.getParam('density');

// Build: npx fxhash build → upload.zip
// Dev: npx fxhash dev → localhost:3300
```

### Art Blocks / 通用平台

```javascript
// Platform provides a hash string
const hash = tokenData.hash;  // Art Blocks convention

// Build deterministic PRNG from hash
function prngFromHash(hash) {
  let seed = parseInt(hash.slice(0, 16), 16);
  // xoshiro128** or similar
  return function() { /* ... */ };
}

const rng = prngFromHash(hash);
```
