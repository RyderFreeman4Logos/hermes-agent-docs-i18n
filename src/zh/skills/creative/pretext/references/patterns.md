# 前提模式

适用于最常见的前提演示场景的可直接复制代码片段。每个模式均为独立单元——从 `https://esm.sh/@chenglou/pretext@0.0.6` 导入后，将其放入 HTML 的 `<script type="module">` 标签中即可使用。

## 1. 绕过障碍物（宽度可变的通道）

最经典的前提动作演示。逐行询问“这里的通道有多宽？”，让角色据此改变行进路线。

```js
const prepared = prepareWithSegments(TEXT, FONT);
const LINE_H = 24;

function drawFlow(ctx, obstacle /* {x,y,r} */, COL_X, COL_W, H) {
  let cursor = { segmentIndex: 0, graphemeIndex: 0 };
  let y = 72;
  while (y < H - 40) {
    const dy = y - obstacle.y;
    const inBand = Math.abs(dy) < obstacle.r;
    let x = COL_X, w = COL_W;
    if (inBand) {
      const half = Math.sqrt(obstacle.r ** 2 - dy ** 2);
      const leftW  = Math.max(0, (obstacle.x - half) - COL_X);
      const rightW = Math.max(0, (COL_X + COL_W) - (obstacle.x + half));
      if (leftW >= rightW) { x = COL_X;                 w = leftW  - 12; }
      else                 { x = obstacle.x + half + 12; w = rightW - 12; }
      if (w < 40) { y += LINE_H; continue; } // skip rather than squeeze
    }
    const range = layoutNextLineRange(prepared, cursor, w);
    if (!range) break;
    const line = materializeLineRange(prepared, range);
    ctx.fillText(line.text, x, y);
    cursor = range.end;
    y += LINE_H;
  }
}
```

**障碍物类型：** 圆形（位于上方）、矩形（需对行段应用 `Math.max(0, …)` 处理）、多个障碍物（对各段进行排序，并输出剩余宽度最大的车道）、动态障碍物（每帧重新计算——前提是计算速度足够快）。

## 2. 文本转几何体游戏（带碰撞检测的单词积木）

首先使用 `layoutWithLines` 获取稳定的线条矩形，然后将每个单词视为用于物理计算的轴对齐矩形。

```js
const prepared = prepareWithSegments(WORDS.join(" "), FONT);
const { lines } = layoutWithLines(prepared, FIELD_W, 28);

// Build brick rects: split each line on spaces and measure word-by-word.
const bricks = [];
let y = 50;
for (const line of lines) {
  let x = 10;
  for (const word of line.text.split(" ")) {
    const wPx = ctx.measureText(word).width; // or use walkLineRanges per word
    bricks.push({ x, y, w: wPx, h: 24, text: word, hp: 1 });
    x += wPx + ctx.measureText(" ").width;
  }
  y += 28;
}
```

碰撞检测：标准AABB形状与球体之间的碰撞。当“生命值”降至0时，该砖块即被“吞噬”。为提升视觉效果，会随着生命值的减少而降低砖块的透明度，并在碰撞时从字母上释放出粒子轨迹。  

## 3. 粉碎/爆炸式文字效果  

通过使用`walkLineRanges`结合手动字符遍历方式，获取每个字形的`(x, y)`坐标，进而生成粒子效果。

```js
const prepared = prepareWithSegments(TEXT, FONT);
const particles = [];
let y = 100;
walkLineRanges(prepared, COL_W, (line) => {
  // materialize so we get per-grapheme positions
  const range = materializeLineRange(prepared, line);
  const seg = new Intl.Segmenter(undefined, { granularity: "grapheme" });
  let x = COL_X;
  for (const { segment } of seg.segment(range.text)) {
    const w = ctx.measureText(segment).width;
    particles.push({ ch: segment, x, y, vx: 0, vy: 0, homeX: x, homeY: y });
    x += w;
  }
  y += LINE_H;
});

// On click, kick particles outward from click point; ease them back to (homeX, homeY).
canvas.addEventListener("click", (e) => {
  for (const p of particles) {
    const dx = p.x - e.clientX, dy = p.y - e.clientY;
    const d = Math.hypot(dx, dy) || 1;
    const force = 400 / (d * 0.2 + 1);
    p.vx += (dx / d) * force;
    p.vy += (dy / d) * force;
  }
});

function tick(dt) {
  for (const p of particles) {
    p.vx *= 0.92; p.vy *= 0.92;
    p.vx += (p.homeX - p.x) * 0.06;
    p.vy += (p.homeY - p.y) * 0.06;
    p.x += p.vx * dt; p.y += p.vy * dt;
  }
}
```

## 4. 将 ASCII 图形视为移动障碍物

这种“酷炫演示”效果的核心思路是：先将 ASCII 标志、精灵图或位图转换为单元格缓冲区，再将其中被占据的单元格转换成逐行的障碍物段。系统会在这些障碍物段周围排列文本，从而使文字实际环绕着移动的 ASCII 对象呈现，而不会被视觉上完全覆盖。

如需查看完整的实现示例，请参考该技能中的 `templates/donut-orbit.html` 文件。请将其视为参考案例而非标准实现方案——它展示了如何从 ASCII 标志中提取障碍物段、将线形结构映射到障碍物行中、在 DOM 层保持文本的可选择性，以及如何通过 `?dev` 参数隐藏调试控件。核心结构如下：

```js
const CELL_W = 12, CELL_H = 15;
const cols = Math.ceil(W / CELL_W), rows = Math.ceil(H / CELL_H);
const asciiMask = new Uint8Array(cols * rows);
const obstacleRows = Array.from({ length: rows }, () => []);

function rasterizeLogo(time) {
  asciiMask.fill(0);
  for (const r of obstacleRows) r.length = 0;

  for (const block of logoBlocks(time)) {
    const r0 = Math.floor(block.y0 / CELL_H);
    const r1 = Math.ceil(block.y1 / CELL_H);
    for (let r = r0; r <= r1; r++) {
      obstacleRows[r]?.push([block.x0 - 18, block.x1 + 22]);
      // Fill asciiMask cells here for drawing.
    }
  }

  mergeRowSpans(obstacleRows);
}

function drawParagraphs(prepared) {
  let cursor = { segmentIndex: 0, graphemeIndex: 0 };
  for (let y = yStart; y < yEnd; y += LINE_H) {
    const spans = obstacleRows[Math.floor(y / CELL_H)];
    for (const [x0, x1] of freeIntervalsAround(spans)) {
      const range = layoutNextLineRange(prepared, cursor, x1 - x0);
      if (!range) return;
      ctx.fillText(materializeLineRange(prepared, range).text, x0, y);
      cursor = range.end;
    }
  }
}
```

关键在于，ASCII几何结构并不仅仅是用于装饰的。那些用于绘制标志或可拖动对象的移动范围，同样也会影响传递给`layoutNextLineRange`的行间距设置。

### 实测范围优于固定填充

在将标志或位图转换为网格单元时，应先测量每行实际占用的单元格数量，再在此基础上添加少量边缘填充。切勿使用一个巨大的边界框。通过精确测量范围，能够让文字看起来仿佛是在字母形状周围自然流动。

```js
const rowMin = new Float32Array(rows).fill(Infinity);
const rowMax = new Float32Array(rows).fill(-Infinity);

for (const cell of visibleCells) {
  rowMin[cell.row] = Math.min(rowMin[cell.row], cell.x);
  rowMax[cell.row] = Math.max(rowMax[cell.row], cell.x + CELL_W);
}

for (let row = 0; row < rows; row++) {
  if (!Number.isFinite(rowMin[row])) continue;
  obstacleRows[row].push([rowMin[row] - halo, rowMax[row] + halo]);
}
```

若需获得清晰的像素艺术风格字体效果，应在添加字符范围之前先对相邻行进行平滑处理。通常设置1-2行的光晕效果，即可避免文字轮廓变形，同时防止代码或正文触及边缘。

### 变形形状需要相应的变形障碍物

当可见物体发生形态变化时（如从球体变为立方体，或从标志变为粒子等），也需同步调整碰撞场。一个令人信服的演示案例会为渲染缓冲区与预设的障碍物行使用相同的`mix`值。

```js
function pushMorphedRows(aRows, bRows, mix) {
  for (let row = 0; row < rows; row++) {
    const a = aRows[row] ?? [centerX, centerX];
    const b = bRows[row] ?? [centerX, centerX];
    obstacleRows[row].push([
      a[0] + (b[0] - a[0]) * mix,
      a[1] + (b[1] - a[1]) * mix,
    ]);
  }
}
```

若缺乏此项功能，图像内容可能会发生变形，而文字仍会沿旧形状排列，从而导致“前提效应”失效。

### 将视觉层与碰撞逻辑分离

当视觉处理不应影响布局时，可使用独立的画布。例如，可在单独的画布层上通过 CSS 的不透明度属性让 ASCII 对象逐渐淡出，同时通过明确的形状状态来控制其障碍物行。直接调整字符的亮度或缩放障碍物的范围，往往会让对象看起来像是正在缩小，而非真正淡出。

## 5. 带共享光标的多列排版

经典的杂志布局为三列结构：文字从第1列的末尾流向第2列的顶部，以此类推。借助“前提效应”，由于光标可在多次 `layoutNextLineRange` 调用之间保持同步，这种排版便变得极为简单。

```js
const prepared = prepareWithSegments(ARTICLE, FONT);
let cursor = { segmentIndex: 0, graphemeIndex: 0 };

for (const col of [COL1, COL2, COL3]) {
  let y = col.y;
  while (y < col.y + col.h) {
    const range = layoutNextLineRange(prepared, cursor, col.w);
    if (!range) return;
    const line = materializeLineRange(prepared, range);
    ctx.fillText(line.text, col.x, y);
    cursor = range.end;
    y += LINE_H;
  }
}
```

若需添加引号，可将其视为中间列中的障碍物，并在其周围使用模式 #1 来实现。

## 6. 多行紧凑排版（最佳适配尺寸卡片）

在限定最大宽度的条件下，寻找仍能保持相同行数的**最小**容器宽度。此功能适用于聊天气泡、引语卡片以及工具提示的尺寸调整。

```js
const prepared = prepareWithSegments(text, FONT);
const { lineCount, maxLineWidth } = measureLineStats(prepared, MAX_W);
// card width = maxLineWidth + padding; card height = lineCount * LINE_H + padding
```

若需通过演示来*直观展示*这一效果，可设置卡片在1秒内从`MAX_W`逐渐缩小至`maxLineWidth`——虽然行数保持不变，但其右边缘会不断向内收缩。

## 7. 动态排版

可实现每行内容随时间变化的动画效果。`layoutWithLines`功能能够生成稳定的线条，而索引`i`则用于控制动画的时序偏移。

```js
const { lines } = layoutWithLines(prepared, W - 80, 40);
function frame(t) {
  for (let i = 0; i < lines.length; i++) {
    const phase = t * 0.001 - i * 0.15;
    const y = 100 + i * 40 + Math.sin(phase) * 12;
    const opacity = 0.4 + 0.6 * Math.max(0, Math.sin(phase));
    ctx.globalAlpha = opacity;
    ctx.fillText(lines[i].text, 40, y);
  }
}
```

变体效果：《星球大战》式滚动（每行视角偏移）、波浪式（正弦函数生成的Y轴偏移）、弹跳式（渐进式出现效果）、故障艺术风（通过`Intl.Segmenter`为每个字符生成随机偏移）。

## 8. 字体堆叠样式

| 风格 | 字体字符串 | 色彩搭配建议 |
|------|-------------|--------------|
| 新闻/严肃风格 | `17px/1.4 "Iowan Old Style", Georgia, serif` | 深炭灰`#0c0d10`背景搭配骨色`#e8e6df`文字 |
| CRT显示器/终端风格 | `600 13px "JetBrains Mono", ui-monospace, monospace` | 深黑`#07070a`背景搭配琥珀色`hsl(38 60% 62%)`文字 |
| 人文主义/现代风格 | `500 17px Inter, ui-sans-serif, system-ui, sans-serif` | 深海军蓝`#0b1020`背景搭配米白色`#f3efe6`文字 |
| 展示/海报风格 | `700 64px "Playfair Display", serif` | 奶油色`#f0ebe0`背景搭配亮红色`#ff4130`文字 |
| 工程领域风格 | `14px "IBM Plex Mono", monospace` | 几近纯黑`#0a0a0c`背景搭配霓虹绿`#7cff7c`文字 |

务必显式加载网页字体（通过Google Fonts链接标签或`@font-face`指令），以确保画布尺寸与CSS渲染结果一致。
