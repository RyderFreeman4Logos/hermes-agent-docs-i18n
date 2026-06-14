---
name: p5js
description: "p5.js sketches: gen art, shaders, interactive, 3D."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative-coding, generative-art, p5js, canvas, interactive, visualization, webgl, shaders, animation]
    related_skills: [ascii-video, manim-video, excalidraw]
---

# p5.js 生产级处理流程

## 适用场景

当用户需求包括：p5.js 绘画、创意编程、生成艺术、交互式可视化、画布动画、基于浏览器的视觉艺术、数据可视化、着色器效果，或任何基于 p5.js 的项目时，均可使用该流程。

## 功能概述

这是一个专为使用 p5.js 创作交互式与生成型视觉艺术设计的处理流程。它能生成基于浏览器的绘画作品、生成艺术、数据可视化内容、交互体验、3D 场景、音频响应型视觉效果以及动态图形，并可将结果导出为 HTML、PNG、GIF、MP4 或 SVG 格式。该流程涵盖以下功能：2D/3D 渲染、噪声与粒子系统、流场模拟、着色器（GLSL）、像素操作、动态排版、WebGL 场景、音频分析、鼠标/键盘交互，以及无头模式下的高分辨率导出。

## 创意准则

这是在浏览器中实现的视觉艺术。画布是创作媒介，算法则是绘图工具。

**在编写任何代码之前**，先明确创意概念。这件作品想要传达什么？为何能让观众停下滚动？它与普通代码示例有何不同？用户的提示只是起点——需以创造性的视野去解读它。

**首次渲染效果必须出色**。作品在首次加载时就必须具备令人惊艳的视觉效果。如果看起来像 p5.js 教程中的练习、默认配置，或是“AI 生成的创意编程作品”，那就说明有误。在发布之前务必重新思考。

**不要局限于参考资料中的内容**。参考资料中的噪声函数、粒子系统、配色方案及着色器效果仅可作为基础素材。对于每个项目，都应对其进行组合、叠加并加以创新。那些参考资料不过是颜料调色板——真正的作品由你亲手创作。

**要主动发挥创造力**。如果用户仅要求“一个粒子系统”，那么你应该提供一个具备群体行为特性、带有拖尾残影、随深度变化的雾效，以及具有呼吸感的背景噪声场的粒子系统。此外，还应加入至少一项用户未提出但会让其赏心悦目的视觉细节。

**追求层次丰富、构思精巧的作品**。每一帧都应值得细细品味。绝不能使用单调的纯白色背景，必须具备明确的构图层次感、经过精心设计的色彩搭配，以及只有仔细观察才能发现的微小细节。

**注重整体美学一致性，而非功能数量**。所有元素都必须服务于统一的视觉语言——相同的色温、一致的线条粗细风格、和谐的运动速度。一个包含十种互不关联效果的作品，远不如三个相互协调的效果的作品出色。

## 模式

| 模式 | 输入 | 输出 | 参考资料 |
|------|-------|--------|-----------|
| **生成艺术** | 种子值/参数 | 生成的静态或动态视觉作品 | `references/visual-effects.md` |
| **数据可视化** | 数据集/API | 交互式图表、图形及自定义数据展示 | `references/interaction.md` |
| **交互体验** | 无（由用户操作） | 通过鼠标/键盘/触摸操作的绘画作品 | `references/interaction.md` |
| **动画/动态图形** | 时间轴/分镜脚本 | 带时间顺序的序列、动态排版及过渡效果 | `references/animation.md` |
| **3D 场景** | 概念描述 | WebGL 几何体、光照、摄像机及材质设置 | `references/webgl-and-3d.md` |
| **图像处理** | 图像文件 | 像素操作、滤镜效果、马赛克制作及点彩风格处理 | `references/visual-effects.md` § 像素操作 |
| **音频响应型** | 音频文件/麦克风输入 | 由声音驱动的生成型视觉效果 | `references/interaction.md` § 音频输入 |

## 技术栈

每个项目仅需一个独立的 HTML 文件，无需任何构建步骤。

| 层级 | 工具 | 功能 |
|------|------|------|
| 核心 | p5.js 1.11.3（CDN） | 画布渲染、数学运算、变换处理及事件处理 |
| 3D | p5.js WebGL 模式 | 3D 几何体、摄像机、光照效果及 GLSL 着色器 |
| 音频 | p5.sound.js（CDN） | FFT 分析、幅度处理、麦克风输入及振荡器功能 |
| 导出 | 内置的 `saveCanvas()` / `saveGif()` / `saveFrames()` 函数 | 支持 PNG、GIF 及帧序列导出 |
| 视频捕获 | CCapture.js（可选） | 可实现稳定帧率的视频捕获（支持 WebM、GIF 格式） |
| 无头渲染 | Puppeteer + Node.js（可选） | 支持自动高分辨率渲染，可通过 ffmpeg 导出 MP4 文件 |
| SVG 导出 | p5.js-svg 1.6.0（可选） | 用于打印的矢量格式输出——需搭配 p5.js 1.x 版本 |
| 自然介质模拟 | p5.brush（可选） | 支持水彩、炭笔、钢笔等绘画效果——需搭配 p5.js 2.x 及 WebGL |
| 纹理效果 | p5.grain（可选） | 添加电影颗粒感及纹理叠加效果 |
| 字体支持 | Google Fonts / `loadFont()` 函数 | 支持通过 OTF/TTF/WOFF2 格式导入自定义字体以实现个性化排版 |

### 版本说明

默认版本为 **p5.js 1.x**（1.11.3）——该版本稳定性高、文档完善，且兼容的库种类最多。除非项目需要 p5.js 2.x 的功能，否则建议继续使用此版本。

**p5.js 2.x**（2.2+）新增了以下功能：用 `async setup()` 替代原有的 `preload()` 函数、OKLCH/OKLAB 颜色模式、`splineVertex()` 函数、着色器 `.modify()` API、可变字体支持、`textToContours()` 函数以及指针事件处理。若需使用 p5.brush 功能，则必须使用 p5.js 2.x 版本。相关详细信息请参阅 `references/core-api.md` § p5.js 2.0 部分。

## 处理流程

所有项目均遵循相同的 6 个阶段处理流程：

```
CONCEPT → DESIGN → CODE → PREVIEW → EXPORT → VERIFY
```

1. **概念构思**——明确创意愿景：整体氛围、色彩体系、运动表现方式，以及该作品的独特之处。  
2. **设计规划**——选择模式、画布尺寸、交互模型、色彩系统及导出格式，并将概念转化为具体的技术决策。  
3. **编码实现**——编写一个包含内联p5.js的HTML文件，结构如下：全局变量 → `preload()` → `setup()` → `draw()` → 辅助函数 → 类定义 → 事件处理程序。  
4. **预览检查**——在浏览器中打开作品，验证视觉效果。在目标分辨率下进行测试，并检查性能表现。  
5. **导出保存**——通过不同方式保存成果：使用`saveCanvas()`导出PNG格式，`saveGif()`导出GIF格式，`saveFrames()`结合ffmpeg导出MP4格式；对于批量无界面处理，可使用Puppeteer工具。  
6. **最终确认**——检查输出结果是否与初始概念一致？在预期展示尺寸下是否具有足够的视觉冲击力？是否值得装框展示？

## 创意方向

### 美学维度

| 维度 | 可选选项 | 参考资料 |
|------|----------|----------|
| **色彩系统** | HSB/HSL、RGB、命名调色板、程序化和谐配色、渐变插值 | `references/color-systems.md` |
| **噪声效果** | 帕尔金噪声、单纯形噪声、分形噪声（多倍频叠加）、域变形、卷曲噪声 | `references/visual-effects.md` § 噪声 |
| **粒子系统** | 基于物理的粒子运动、群集行为、轨迹绘制、吸引子驱动、流场跟随 | `references/visual-effects.md` § 粒子 |
| **形状语言** | 几何基本形状、自定义顶点、贝塞尔曲线、SVG路径 | `references/shapes-and-geometry.md` |
| **运动风格** | 平滑过渡、弹簧效应、噪声驱动、物理模拟、线性插值、阶梯式运动 | `references/animation.md` |
| **排版设计** | 系统字体、加载的OTF字体、通过`textToPoints()`生成的粒子文字、动态文字效果 | `references/typography.md` |
| **着色器效果** | GLSL片段着色器/顶点着色器、滤镜着色器、后期处理效果、反馈循环 | `references/webgl-and-3d.md` § 着色器 |
| **构图方式** | 网格布局、放射状布局、黄金比例、三分法、自然散布、平铺布局 | `references/core-api.md` § 构图 |
| **交互模型** | 鼠标跟随、点击生成、拖动操作、键盘控制、滚动驱动、麦克风输入响应 | `references/interaction.md` |
| **混合模式** | `BLEND`、`ADD`、`MULTIPLY`、`SCREEN`、`DIFFERENCE`、`EXCLUSION`、`OVERLAY` | `references/color-systems.md` § 混合模式 |
| **图层处理** | 使用`createGraphics()`创建离屏缓冲区、透明度合成、遮罩效果 | `references/core-api.md` § 离屏缓冲区 |
| **纹理生成** | 帕尔金表面纹理、点状纹理、排线纹理、半色调纹理、像素排序效果 | `references/visual-effects.md` § 纹理生成 |

### 项目专属调整规则

切勿使用默认配置。每个项目都应：
- **自定义调色板**——避免直接使用`fill(255, 0, 0)`这样的原始颜色值，而应设计包含3-7种颜色的专属调色板。
- **自定义线条粗细体系**——细线用于细节装饰（0.5），中等粗细用于结构构建（1-2），粗线用于强调重点（3-5）。
- **背景处理**——避免使用简单的`background(0)`或`background(255)`，而应采用带纹理、渐变或多层叠加的背景。
- **多样化的运动效果**——不同元素应具有不同的运动速度：主要元素以1倍速移动，次要元素以0.3倍速，背景元素以0.1倍速。
- **至少一种原创元素**——可自定义粒子行为、创新性的噪声应用方式，或独特的交互响应机制。

### 项目特有的创新设计

每个项目都应至少创造以下一项内容：
- 与整体氛围相匹配的自定义调色板（而非预设调色板）；
- 创新的噪声场组合方式（例如卷曲噪声+域变形+反馈机制）；
- 独特的粒子行为设计（自定义力场、自定义轨迹、自定义生成规则）；
- 用户未提出但能提升作品表现力的交互机制；
- 能够构建视觉层次感的构图技巧。

### 参数设计原则

参数应源自算法本身，而非通用的菜单选项。需思考：“*这个*系统有哪些属性是需要可调优的？”

**优秀的参数**能够体现算法的特性：
- **数量参数**——粒子数、分支数、单元格数等（用于控制密度）；
- **尺度参数**——噪声频率、元素大小、间距等（用于控制纹理质感）；
- **速率参数**——速度、生长速率、衰减速率等（用于控制能量强度）；
- **阈值参数**——触发某种行为变化的条件（用于增强戏剧性效果）；
- **比例参数**——各元素之间的比例关系及力量平衡（用于实现和谐统一）。

**劣质的参数**则是与算法无关的通用控制项：
- “color1”、“color2”、“size”等缺乏上下文意义的参数；
- 用于控制无关效果的切换开关；
- 仅能改变外观而无法影响行为的参数。

每个参数都应改变算法的“思维方式”，而不仅仅是改变其视觉呈现。例如，能够调整噪声倍频的“湍流”参数是优秀的；而仅能改变`ellipse()`函数半径的“粒子大小”滑块则较为浅层。

## 工作流程

### 第一步：明确创意愿景

在编写任何代码之前，先清晰阐述以下内容：
- **氛围与情绪**：观众应感受到怎样的情绪？沉思？充满活力？不安？还是轻松有趣？
- **视觉叙事**：随着时间推移（或用户交互）会发生什么变化？是逐渐构建、逐渐衰减、形态转变，还是周期性波动？
- **色彩世界**：整体风格偏向暖色调还是冷色调？是单色系？互补色系？哪种颜色为主色调？哪种为强调色？
- **形状语言**：倾向于有机曲线？锐利几何形状？点状元素？线条元素？还是多种形式混合？
- **运动表现方式**：是缓慢漂移？剧烈爆发？有节奏的脉动？还是精确的机械运动？
- **独特之处**：究竟是什么让这个作品与众不同？

需将用户的描述转化为具体的美学选择。例如，“令人放松的生成式背景”与“故障艺术数据可视化”在各方面都需要完全不同的设计思路。

### 第二步：技术设计规划

确定以下各项：
- **模式**——从上表中的7种模式中选择一种；
- **画布尺寸**——横屏1920x1080、竖屏1080x1920、正方形1080x1080，或根据窗口大小自适应的`windowWidth/windowHeight`；
- **渲染器**——默认使用`P2D`，如需3D效果、着色器或高级混合模式，则使用`WEBGL`；
- **帧率**——交互式作品设为60fps，背景动画设为30fps，静态生成式作品则使用`noLoop()`；
- **导出目标**——浏览器展示、PNG静态图片、GIF循环动画、MP4视频或SVG矢量图形；
- **交互模型**——被动式（无用户输入）、鼠标驱动、键盘驱动、音频响应式或滚动驱动；
- **观众界面**——对于交互式生成艺术作品，可基于`templates/viewer.html`模板开始开发，该模板已包含种子导航、参数滑块及下载功能；对于简单草图或视频导出，则可使用纯HTML文件。

### 第三步：编写代码实现

对于**交互式生成艺术作品**（需支持种子探索和参数调整）：从`templates/viewer.html`模板开始。先仔细阅读模板，保留其中固定的部分（如种子导航、操作按钮），再替换为自定义的算法及参数控制逻辑。这样即可为用户提供种子前进/后退/随机生成/跳转功能、实时更新的参数滑块以及PNG下载功能，所有功能都已整合完成。

对于**动画、视频导出或简单草图**：则直接使用纯HTML文件：

只需一个HTML文件，其结构如下：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project Name</title>
  <script>p5.disableFriendlyErrors = true;</script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
  <!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/addons/p5.sound.min.js"></script> -->
  <!-- <script src="https://unpkg.com/p5.js-svg@1.6.0"></script> -->  <!-- SVG export -->
  <!-- <script src="https://cdn.jsdelivr.net/npm/ccapture.js-npmfixed/build/CCapture.all.min.js"></script> -->  <!-- video capture -->
  <style>
    html, body { margin: 0; padding: 0; overflow: hidden; }
    canvas { display: block; }
  </style>
</head>
<body>
<script>
// === Configuration ===
const CONFIG = {
  seed: 42,
  // ... project-specific params
};

// === Color Palette ===
const PALETTE = {
  bg: '#0a0a0f',
  primary: '#e8d5b7',
  // ...
};

// === Global State ===
let particles = [];

// === Preload (fonts, images, data) ===
function preload() {
  // font = loadFont('...');
}

// === Setup ===
function setup() {
  createCanvas(1920, 1080);
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  colorMode(HSB, 360, 100, 100, 100);
  // Initialize state...
}

// === Draw Loop ===
function draw() {
  // Render frame...
}

// === Helper Functions ===
// ...

// === Classes ===
class Particle {
  // ...
}

// === Event Handlers ===
function mousePressed() { /* ... */ }
function keyPressed() { /* ... */ }
function windowResized() { resizeCanvas(windowWidth, windowHeight); }
</script>
</body>
</html>
```

## 主要实现模式

- **种子化随机数生成**：为确保结果可复现，始终使用 `randomSeed()` + `noiseSeed()` 
- **颜色模式**：通过 `colorMode(HSB, 360, 100, 100, 100)` 实现直观的颜色控制
- **状态分离**：参数用 CONFIG 管理，颜色用 PALETTE 管理，可变状态则存储在全局变量中
- **基于类的实体**：将粒子、智能体及图形视为具有 `update()` 和 `display()` 方法的类
- **离屏缓冲区**：利用 `createGraphics()` 实现分层合成、轨迹效果及遮罩功能

### 第4步：预览与迭代

- 直接在浏览器中打开HTML文件——基础草图无需服务器支持
- 若需从本地文件加载图像或字体，可使用 `scripts/serve.sh` 或 `python3 -m http.server`
- 通过Chrome开发者工具的“性能”标签页验证是否能达到60帧/秒
- 应在目标导出分辨率下进行测试，而不仅仅是根据窗口大小判断
- 不断调整参数，直至视觉效果符合第一步设定的构思

### 第5步：导出

| 格式 | 方法 | 命令 |
|------|------|------|
| **PNG** | 在 `keyPressed()` 函数中使用 `saveCanvas('output', 'png')` | 按“s”键保存 |
| **高分辨率PNG** | 使用Puppeteer无头模式捕获 | `node scripts/export-frames.js sketch.html --width 3840 --height 2160 --frames 1` |
| **GIF** | `saveGif('output', 5)`——可捕获N秒内容 | 按“g”键保存 |
| **帧序列** | `saveFrames('frame', 'png', 10, 30)`——以30帧/秒的速度录制10秒 | 接着使用 `ffmpeg -i frame-%04d.png -c:v libx264 output.mp4` 转换 |
| **MP4** | 结合Puppeteer帧捕获与ffmpeg工具 | `bash scripts/render.sh sketch.html output.mp4 --duration 30 --fps 30` |
| **SVG** | 使用p5.js-svg创建尺寸为w×h的SVG画布 | `save('output.svg')` |

### 第6步：质量验证

- **是否符合预期设计？**将输出结果与初始创意概念进行对比。若效果显得过于普通，需返回第一步重新构思
- **分辨率检查**：在目标显示尺寸下是否清晰？是否存在锯齿等伪影？
- **性能检查**：在浏览器中能否保持60帧/秒的流畅度？（动画的最低要求为30帧/秒）
- **颜色检查**：各颜色搭配是否协调？需在亮色和暗色显示器上分别测试
- **边界情况测试**：在画布边缘、窗口大小调整时，以及运行10分钟后，效果如何？

## 重要实现注意事项

### 性能优化——先禁用FES功能

Friendly Error System（友好错误系统）会增加多达10倍的开销。在所有正式使用的草图中都应将其禁用：

```javascript
p5.disableFriendlyErrors = true;  // BEFORE setup()

function setup() {
  pixelDensity(1);  // prevent 2x-4x overdraw on retina
  createCanvas(1920, 1080);
}
```

在涉及大量循环运算（如粒子效果、像素操作）的场景中，建议使用 `Math.*` 函数而非 p5 的封装函数——这样能显著提升运行速度。

```javascript
// In draw() or update() hot paths:
let a = Math.sin(t);          // not sin(t)
let r = Math.sqrt(dx*dx+dy*dy); // not dist() — or better: skip sqrt, compare magSq
let v = Math.random();        // not random() — when seed not needed
let m = Math.min(a, b);       // not min(a, b)
```

绝不在 `draw()` 函数内部使用 `console.log()`，也严禁在 `draw()` 中操作 DOM。详情请参阅 `references/troubleshooting.md` 中的“性能”部分。

### 始终采用种子化随机性

每一个生成的草图都必须具备可重复性——相同的种子，必然产生相同的输出。

```javascript
function setup() {
  randomSeed(CONFIG.seed);
  noiseSeed(CONFIG.seed);
  // All random() and noise() calls now deterministic
}
```

在生成内容时切勿使用 `Math.random()`，该函数仅适用于对性能要求极高且与视觉无关的代码。处理视觉元素时请始终使用 `random()` 函数。如需随机种子，可设置：`CONFIG.seed = floor(random(99999))`。

### 生成艺术平台支持（fxhash / Art Blocks）

对于生成艺术平台，应使用该平台提供的确定性随机数生成器，替代 p5 中的 PRNG 函数：

```javascript
// fxhash convention
const SEED = $fx.hash;              // unique per mint
const rng = $fx.rand;               // deterministic PRNG
$fx.features({ palette: 'warm', complexity: 'high' });

// In setup():
randomSeed(SEED);   // for p5's noise()
noiseSeed(SEED);

// Replace random() with rng() for platform determinism
let x = rng() * width;  // instead of random(width)
```

请参阅 `references/export-pipeline.md` 中的“平台导出”部分。

### 颜色模式——使用 HSB

对于生成式艺术而言，HSB（色调、饱和度、亮度）模式比 RGB 模式更易于操作：

```javascript
colorMode(HSB, 360, 100, 100, 100);
// Now: fill(hue, sat, bri, alpha)
// Rotate hue: fill((baseHue + offset) % 360, 80, 90)
// Desaturate: fill(hue, sat * 0.3, bri)
// Darken: fill(hue, sat, bri * 0.5)
```

切勿直接硬编码原始的RGB数值。应先定义一个调色板对象，再通过程序化方式生成不同的色彩变体。详情请参阅 `references/color-systems.md`。

### 噪声效果——多频段处理，而非原始值

直接的 `noise(x, y)` 函数生成的图案呈现为平滑的斑点状。通过叠加多个频段即可获得自然的纹理效果：

```javascript
function fbm(x, y, octaves = 4) {
  let val = 0, amp = 1, freq = 1, sum = 0;
  for (let i = 0; i < octaves; i++) {
    val += noise(x * freq, y * freq) * amp;
    sum += amp;
    amp *= 0.5;
    freq *= 2;
  }
  return val / sum;
}
```

若需实现流畅的有机形态，可使用**域变形**技术：将噪声输出值重新作为噪声输入坐标使用。详情请参阅 `references/visual-effects.md`。

### 图层功能必须使用 createGraphics() —— 这并非可选

单次渲染方式会导致画面显得单调乏味。建议使用离屏缓冲区来进行图像合成：

```javascript
let bgLayer, fgLayer, trailLayer;
function setup() {
  createCanvas(1920, 1080);
  bgLayer = createGraphics(width, height);
  fgLayer = createGraphics(width, height);
  trailLayer = createGraphics(width, height);
}
function draw() {
  renderBackground(bgLayer);
  renderTrails(trailLayer);   // persistent, fading
  renderForeground(fgLayer);  // cleared each frame
  image(bgLayer, 0, 0);
  image(trailLayer, 0, 0);
  image(fgLayer, 0, 0);
}
```

### 性能优化——尽可能采用向量化处理

p5.js的绘图调用成本较高。在处理成千上万个粒子时：

```javascript
// SLOW: individual shapes
for (let p of particles) {
  ellipse(p.x, p.y, p.size);
}

// FAST: single shape with beginShape()
beginShape(POINTS);
for (let p of particles) {
  vertex(p.x, p.y);
}
endShape();

// FASTEST: pixel buffer for massive counts
loadPixels();
for (let p of particles) {
  let idx = 4 * (floor(p.y) * width + floor(p.x));
  pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 255;
}
updatePixels();
```

请参阅 `references/troubleshooting.md` 中的“性能”部分。

### 多个草图的实例模式

全局模式会占用 `window` 资源。在正式环境中，建议使用实例模式：

```javascript
const sketch = (p) => {
  p.setup = function() {
    p.createCanvas(800, 800);
  };
  p.draw = function() {
    p.background(0);
    p.ellipse(p.mouseX, p.mouseY, 50);
  };
};
new p5(sketch, 'canvas-container');
```

当需要在同一页面上嵌入多个草图或与框架集成时，此选项为必选。

### WebGL 模式注意事项

- `createCanvas(w, h, WEBGL)` — 原点位于中心，而非左上角
- Y轴方向相反（WebGL 中正Y值向上，P2D 中则向下）
- 若需获得类似 P2D 的坐标系，需使用 `translate(-width/2, -height/2)`
- 每次执行变换操作前后都应使用 `push()`/`pop()` — 否则矩阵栈会 silently 溢出
- 应在 `rect()`/`plane()` 之前调用 `texture()`，而非之后
- 自定义着色器：使用 `createShader(vert, frag)` — 需在多种浏览器中测试

### 导出 — 键盘绑定规范

每个草图都应在 `keyPressed()` 函数中包含以下内容：

```javascript
function keyPressed() {
  if (key === 's' || key === 'S') saveCanvas('output', 'png');
  if (key === 'g' || key === 'G') saveGif('output', 5);
  if (key === 'r' || key === 'R') { randomSeed(millis()); noiseSeed(millis()); }
  if (key === ' ') CONFIG.paused = !CONFIG.paused;
}
```

### 无界面视频导出——使用 noLoop() 函数

通过 Puppeteer 进行无界面渲染时，该示例代码在初始化阶段**必须**调用 `noLoop()` 函数。如果不使用此函数，p5 的绘制循环将会持续运行，从而导致截图速度变慢——此时代码的执行速度会远远超过截图速度，进而出现帧数缺失或重复的问题。

```javascript
function setup() {
  createCanvas(1920, 1080);
  pixelDensity(1);
  noLoop();                    // capture script controls frame advance
  window._p5Ready = true;      // signal readiness to capture script
}
```

随附的 `scripts/export-frames.js` 脚本会检测 `_p5Ready` 状态，并在每次捕获时调用一次 `redraw()` 函数，从而确保帧与帧之间保持精确的 1:1 对应关系。详情请参阅 `references/export-pipeline.md` 中的“确定性捕获”部分。

对于多场景视频，建议采用逐片段处理架构：为每个场景创建一个独立的 HTML 文件，分别进行渲染，最后使用 `ffmpeg -f concat` 命令将它们合并。相关说明可见 `references/export-pipeline.md` 中的“逐片段架构”部分。

### Agent 工作流程

在构建 p5.js 程序时，请遵循以下步骤：

1. **编写 HTML 文件** —— 创建一个独立的单文件，所有代码均内嵌在其中。
2. **在浏览器中打开** —— 在 macOS 上使用 `open sketch.html`，在 Linux 上使用 `xdg-open sketch.html`。
3. **本地资源**（字体、图片等）需要通过服务器提供：在项目目录中运行 `python3 -m http.server 8080`，然后访问 `http://localhost:8080/sketch.html`。
4. **导出 PNG/GIF 格式** —— 按前述方法添加 `keyPressed()` 快捷键，并告知用户需要按下的按键。
5. **无界面模式导出** —— 使用命令 `node scripts/export-frames.js sketch.html --frames 300` 实现自动帧捕获（程序必须使用 `noLoop()` 和 `_p5Ready`）。
6. **渲染为 MP4 格式** —— 运行命令 `bash scripts/render.sh sketch.html output.mp4 --duration 30`。
7. **迭代优化** —— 修改 HTML 文件后，用户只需刷新浏览器即可查看更改效果。
8. **按需加载参考资料** —— 在开发过程中，可根据需要使用 `skill_view(name="p5js", file_path="references/...")` 函数加载特定的参考文件。

## 性能指标

| 指标 | 目标值 |
|------|--------|
| 交互式帧率 | 持续保持 60fps |
| 动画导出帧率 | 最低 30fps |
| P2D 形状中的粒子数量 | 在 60fps 下为 5,000–10,000 个 |
| 像素缓冲区中的粒子数量 | 在 60fps 下为 50,000–100,000 个 |
| 画布分辨率 | 导出时最高可达 3840×2160，交互模式为 1920×1080 |
| HTML 文件大小 | < 100KB（不包括 CDN 库文件） |
| 加载时间 | 到第一帧的加载时间 < 2秒 |

## 参考资料

| 文件名 | 内容概述 |
|--------|----------|
| `references/core-api.md` | 画布设置、坐标系统、绘制循环、`push()`/`pop()` 函数、离屏缓冲区、构图模式、`pixelDensity()` 函数以及响应式设计相关内容。 |
| `references/shapes-and-geometry.md` | 2D 基础图形、`beginShape()`/`endShape()` 函数、贝塞尔曲线/卡特穆尔-罗姆曲线、`vertex()` 系统、自定义形状、`p5.Vector` 类、有符号距离场以及 SVG 路径转换方法。 |
| `references/visual-effects.md` | 噪声效果（Perlin 噪声、分形噪声、域变形、卷曲效果）、流场、粒子系统（物理模拟、群集行为、轨迹效果）、像素操作、纹理生成方法（点阵纹理、阴影纹理、半色调处理）、反馈循环以及反应-扩散模型。 |
| `references/animation.md` | 基于帧的动画实现、缓动函数、`lerp()`/`map()` 函数、弹簧物理模拟、状态机、时间轴序列控制、基于 `millis()` 的计时方法以及过渡效果模式。 |
| `references/typography.md` | `text()`、`loadFont()`、`textToPoints()` 函数、动态文字效果、文字遮罩、字体度量参数以及响应式文字大小调整方法。 |
| `references/color-systems.md` | `colorMode()` 函数、HSB/HSL/RGB 颜色模式、`lerpColor()`、`paletteLerp()` 函数、程序化调色板生成、色彩和谐搭配、`blendMode()` 函数、渐变渲染效果以及精选的调色板库。 |
| `references/webgl-and-3d.md` | WEBGL 渲染器、3D 基础图形、相机设置、光照效果、材质处理、自定义几何体、GLSL 着色器（`createShader()`、`createFilterShader()` 函数）、帧缓冲区以及后期处理技术。 |
| `references/interaction.md` | 鼠标事件、键盘状态、触摸输入、DOM 元素操作、`createSlider()`/`createButton()` 函数、音频输入处理（p5.sound 的 FFT/幅度分析功能）、滚动驱动的动画效果以及响应式事件处理方法。 |
| `references/export-pipeline.md` | `saveCanvas()`、`saveGif()`、`saveFrames()` 函数、确定性无界面模式捕获、使用 ffmpeg 将帧转换为视频文件、CCapture.js 库、SVG 导出功能、逐片段处理架构、不同平台的导出方案（fxhash 算法）、视频制作中的常见问题。 |
| `references/troubleshooting.md` | 性能分析方法、每像素资源限制、常见错误、浏览器兼容性问题、WebGL 调试技巧、字体加载问题、像素密度相关陷阱、内存泄漏问题以及 CORS 问题解决方案。 |
| `templates/viewer.html` | 交互式查看器模板：包含导航功能（上一帧/下一帧/随机切换/跳转）、参数滑块、PNG 下载功能以及响应式画布。可基于此模板创建可交互的生成艺术作品。 |

---

## 创意发散（仅当用户要求实验性/创意性/独特输出时使用）

如果用户希望获得具有创意、实验性、惊喜效果或非传统风格的输出，应在生成代码之前选择最合适的策略，并详细规划其实现步骤。

- **概念融合** —— 当用户希望将两种不同的视觉元素结合或打造混合风格时使用。
- **SCAMPER 法则** —— 当用户希望对现有的生成艺术模式进行创新改造时使用。
- **远近关联法** —— 当用户给出一个核心概念并希望对其进行拓展探索时使用（例如“以时间为主题创作作品”）。

### 概念融合
1. 确定两种截然不同的视觉系统（例如粒子物理效果与手写风格）。
2. 建立两者之间的对应关系（将粒子视为墨滴，力场视为笔压，场域结构视为字母形态）。
3. 有选择地融合这些元素——仅保留那些能产生有趣视觉效果的对应关系。
4. 将融合后的系统编写为统一的代码结构，而非并列的两个独立系统。

### SCAMPER 转换法
针对现有的生成艺术模式（如流场、粒子系统、L-系统、元胞自动机），通过以下步骤进行系统性改造：
- **替换**：用文本字符替代圆形元素，用渐变效果替代线条。
- **组合**：将两种不同的模式合并在一起（例如流场与沃罗诺伊图结合）。
- **调整**：将二维模式应用于三维投影中。
- **修改**：夸大元素的尺度或扭曲坐标空间。
- **改变用途**：将物理模拟用于文字设计，或将排序算法用于颜色处理。
- **去除**：移除网格结构、颜色元素或对称性特征。
- **反向操作**：让模拟过程反向运行，或反转参数空间。

### 远近关联法
1. 以用户提供的核心概念为起点（例如“孤独”）。
2. 从三个不同层面生成相关联的元素：
   - **近层关联**（显而易见）：空荡的房间、独自一人、寂静氛围。
   - **中层关联**（富有趣味）：一群鱼中有一条游动方向相反，没有通知提示的电话，地铁车厢之间的间隙。
   - **远层关联**（抽象概念）：质数、渐近曲线、凌晨 3 点时的颜色。
3. 重点开发中层关联的元素——这类元素既具有足够的具体性以便可视化，又足够出人意料以带来趣味性。
