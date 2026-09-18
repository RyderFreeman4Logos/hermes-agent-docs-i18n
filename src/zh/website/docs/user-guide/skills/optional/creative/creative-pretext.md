---
title: "Pretext — Build creative browser demos with DOM-free text layout"
sidebar_label: "Pretext"
description: "Build creative browser demos with DOM-free text layout"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Pretext

利用无需 DOM 的文本排版方式构建创意级浏览器演示。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/pretext` 安装 |
| 路径 | `optional-skills/creative\pretext` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `creative-coding`、`typography`、`pretext`、`ascii-art`、`canvas`、`generative`、`text-layout`、`kinetic-typography` |
| 相关技能 | [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js)、[`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design)、[`excalidraw`](/docs/user-guide/skills/optional/creative/creative-excalidraw)、[`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，Agent 就会依据此内容执行操作。
:::

# Pretext创意演示

## 概述

[`@chenglou/pretext`](https://github.com/chenglou/pretext) 是由 Cheng Lou（React核心、ReasonML、Midjourney项目开发者）打造的一个仅15KB大小的零依赖TypeScript库，专为**无需DOM的多行文本测量与布局**而设计。它仅实现一个功能：给定`(文本, 字体, 宽度)`参数，即可通过Canvas测量方式返回换行位置、每行宽度、每个字符的位置以及整体高度——整个过程无需重新布局。

这听起来像是管道工程？其实并非如此。由于其高效且基于几何计算，它实际上是一种**创意基础工具**：你可以让段落围绕以60fps速度移动的精灵元素动态重排，构建以真实文字构成关卡几何结构的游戏，在文本中显示ASCII图标，将文本拆解为具有精确字符起始位置的粒子，或是无需使用`getBoundingClientRect`方法即可高效渲染多层UI。

开发此功能是为了让Hermes能够利用它打造**令人惊叹的演示效果**——那种人们会发布在X平台上的精彩示例。你可以访问`pretext.cool`和`chenglou.me/pretext`查看社区分享的演示案例集。

## 适用场景

当用户需要以下功能时，可使用该库：
- “伪装演示”/“酷炫的伪装效果”/“文本即X”
- 文本环绕动态形状流动的效果（用于首页板块、新闻排版及动画长文页面）
- 使用**真实单词或段落文字**而非等宽字体矩阵实现的ASCII艺术效果
- 以文本作为游戏场地、障碍物或砖块的益智游戏（如用字母构成的俄罗斯方块、用段落文字构成的打砖块游戏）
- 具有逐字符物理特性的动态排版效果（如破碎、散落、群聚、流动等）
- 排版生成艺术，尤其是涉及非拉丁字母或混合字母体系的创作
- 多行“紧凑包裹”式用户界面（在保证文字完整显示的前提下追求最窄的容器宽度）
- 任何需要在渲染之前就确定换行位置的场景

**不适用于以下情况：**
- CSS已能解决布局问题的静态SVG/HTML页面——直接使用CSS即可
- 富文本编辑器及通用内联格式化引擎（Pretext的设计初衷就是功能较为精简）
- 图像转文本的场景（应使用`ascii-art`/`ascii-video`技能）
- 无文本相关功能的纯Canvas生成艺术——请使用`p5js`库

## 创意标准

这是在浏览器中呈现的视觉艺术作品。Pretext仅负责输出数值数据，**实际的艺术效果由您自行绘制**。

- **切勿仅提供“Hello World”式的简单演示。** `hello-orb-flow.html` 模板仅是*起点*，每一个正式发布的演示都应加入精心设计的色彩、动态效果、构图元素，以及一处用户虽未明确提出但会倍感惊喜的视觉细节。
- **深色背景搭配暖色调主色，色彩方案需经过深思熟虑。** 经典的琥珀色与黑色组合（适用于CRT显示器/终端界面）效果不错，冷白色与炭灰色的组合（适用于新闻类内容）以及低饱和度的淡彩风格（适用于凸版印刷效果）也同样适用。请选择一种并坚持使用。
- **比例合适的字体至关重要。** Pretext 的整体设计理念就是“非等宽字体”，因此应充分利用这一特点。可选择 Iowan Old Style、Inter、JetBrains Mono、Helvetica Neue 或变量字体，绝不能使用默认的无衬线字体。
- **使用真实内容而非伪文本。** 演示所用的文本必须具有实际意义，可以是简短的宣言、诗歌、真实的代码片段、找到的古籍文字，或是该库自身的 README 文件——绝不能用 `lorem ipsum` 这类伪文本。
- **首屏呈现效果需极为出色。** 不得出现加载状态或空白界面，演示页面在打开的瞬间就必须呈现出可直接发布的完美状态。

## 技术栈

每个演示都应是一个独立的 HTML 文件，无需任何构建步骤。

| 层级 | 工具 | 用途 |
|------|------|------|
| 核心层 | 通过 `esm.sh` CDN 引入的 `@chenglou/pretext` | 文本测量与行布局处理 |
| 渲染层 | HTML5 Canvas 2D | 字形渲染及逐帧构图 |
| 分割层 | 内置的 `Intl.Segmenter` | 对表情符号、汉字符及组合标记进行字形分割 |
| 交互层 | 原生的 DOM 事件 | 鼠标、触摸、滚轮操作——无需任何框架 |

```html
<script type="module">
import {
  prepare, layout,                   // use-case 1: simple height
  prepareWithSegments, layoutWithLines,  // use-case 2a: fixed-width lines
  layoutNextLineRange, materializeLineRange, // use-case 2b: streaming / variable width
  measureLineStats, walkLineRanges,  // stats without string allocation
} from "https://esm.sh/@chenglou/pretext@0.0.6";
</script>
```

锁定版本。撰写本文时为 `@0.0.6` 版本——如果演示效果出现异常，请前往 [npm](https://www.npmjs.com/package/@chenglou/pretext) 查看最新版本。

## 两种应用场景

几乎所有情况都可归结为以下两种形式之一。建议掌握这两种用法。

### 场景一：先进行测量，再通过 CSS/DOM 进行渲染

```js
const prepared = prepare(text, "16px Inter");
const { height, lineCount } = layout(prepared, 320, 20);
```

你仍然让浏览器来绘制文本。Pretext仅能根据给定的宽度告知文本框的高度，**无需**读取DOM元素。适用于以下场景：
- 行内文本较多的虚拟列表
- 需要精确控制卡片高度的Masonry布局
- 开发阶段检测“该标签是否能够完整显示”
- 在加载远程文本时防止布局偏移

**请确保`font`与`letterSpacing`的设置与CSS完全一致。** Canvas中的`ctx.font`格式（例如`"16px Inter"`、`"500 17px 'JetBrains Mono'"`）必须与实际渲染的CSS格式相匹配，否则测量结果会出现偏差。

### 场景2 — 自行进行测量与渲染

```js
const prepared = prepareWithSegments(text, FONT);
const { lines } = layoutWithLines(prepared, 320, 26);
for (let i = 0; i < lines.length; i++) {
  ctx.fillText(lines[i].text, 0, i * 26);
}
```

这里便是创意内容得以实现的场所。由于您拥有该绘图内容，因此可以：
- 将其渲染为画布格式、SVG、WebGL图像，或适用于任何坐标系的图形
- 为每个字符应用不同的变换效果（旋转、抖动、缩放、透明度调整）
- 利用线条的元数据（线宽、字形位置）作为几何结构

对于**每行字符宽度可变**的排版场景（如环绕在形状周围的文字、环形区域内的文字，以及非矩形列中的文字）：

```js
let cursor = { segmentIndex: 0, graphemeIndex: 0 };
let y = 0;
while (true) {
  const lineWidth = widthAtY(y);  // your function: how wide is the corridor at this y?
  const range = layoutNextLineRange(prepared, cursor, lineWidth);
  if (!range) break;
  const line = materializeLineRange(prepared, range);
  ctx.fillText(line.text, leftEdgeAtY(y), y);
  cursor = range.end;
  y += lineHeight;
}
```

这是整个库中最核心的模板。正是它实现了“文本环绕被拖动的精灵元素”这一效果——也就是在X平台上广为流传的那个演示案例。

### 值得了解的辅助函数

- `measureLineStats(prepared, maxWidth)` → `{ lineCount, maxLineWidth }` — 返回最宽的行，即多行换行时的最大宽度。
- `walkLineRanges(prepared, maxWidth, callback)` — 无需创建字符串即可遍历各行。当您不需要获取具体字符内容时，可用于基于字形而非字符的计算或物理模拟。
- `@chenglou/pretext/rich-inline` — 适用于混合使用字体、芯片元素及提及标签的段落的相同系统。需从该子路径导入。

## 演示模板模式

社区中的优秀案例（详见 `references/patterns.md`）可归纳为几类核心模板。请选择其中一种进行改造——除非有特殊要求，否则无需自行创建新类别。

| 模式 | 核心 API | 示例思路 |
|---|---|---|
| **绕障碍物重排** | `layoutNextLineRange` + 每行宽度计算函数 | 文本段落根据拖动的光标位置自动调整布局 |
| **文本作为几何图形的游戏** | `layoutWithLines` + 每行碰撞检测区域 | 每块砖块代表一个特定单词的打砖游戏 |
| **破碎/粒子效果** | `walkLineRanges` → 每个字符的 (x,y) 坐标 → 物理模拟 | 点击后句子会分解为单个字母的特效 |
| **ASCII 障碍物排版** | `layoutNextLineRange` + 每行障碍物长度计算 | 使用位图形式的 ASCII 标识符，结合形状变形与可拖动的线条元素，让文本围绕其实际几何结构排列 |
| **多列编辑布局** | 每列分别使用 `layoutNextLineRange` + 共享光标 | 带有引文插图的动态杂志版面 |
| **动态文字效果** | `layoutWithLines` + 随时间变化的每行变换 | 类似《星球大战》字幕的滚动、波浪、弹跳及故障艺术效果 |
| **多行自动换行** | `measureLineStats` | 引文卡片会自动调整大小以适应最紧凑的容器 |

如需可直接运行的单文件示例，请查看 `templates/donut-orbit.html` 和 `templates/hello-orb-flow.html`。

## 工作流程

1. 根据用户的需求描述，从上表中选择一种模板模式。  
2. 从预设模板开始创建：  
   - `templates/hello-orb-flow.html` —— 文本围绕移动的球体重新排列（绕障碍物重排模式）  
   - `templates/donut-orbit.html` —— 更高级的示例：可测量的ASCII图标作为障碍物、可拖动的线形球体/立方体、可变形的形状区域、可选择的DOM文本以及仅开发人员可见的控制选项  
   - 将内容写入 `/tmp/` 目录或用户工作区中的新 `.html` 文件中。  
3. 用符合需求描述的真实文本内容替换示例文本，段落长度应在10到100句之间，且不得使用伪文本。  
4. 调整视觉风格——包括字体、配色方案、布局以及交互效果。这是核心工作环节，切勿跳过。  
5. 在本地进行验证：
   ```sh
   cd <dir-with-html> && python -m http.server 8765
   # then open http://localhost:8765/<file>.html
   ```
6. **检查控制台输出**——如果使用无效的字体字符串调用 `prepareWithSegments`，pretext 函数将会抛出异常；所有现代浏览器都支持 `Intl.Segmenter` 接口。  
7. **向用户显示文件路径，而不仅仅是代码**——他们希望直接打开该文件。

## 性能注意事项

- `prepare()` / `prepareWithSegments()` 是计算成本较高的函数。对于每组文本与字体组合，只需调用**一次**，并将返回的句柄缓存起来。  
- 当窗口大小发生变化时，仅需重新执行 `layout()` / `layoutWithLines()` 函数，无需再次进行准备操作。  
- 对于那些文字内容不变但几何形状会变化的逐帧动画，对于常规长度的段落，通过循环调用 `layoutNextLineRange` 的开销足够低，可在 60fps 下每帧更新一次。  
- 在逐帧渲染 ASCII 图形时，应使用单元格缓冲区（如 `Uint8Array` 或类型化数组），根据这些单元格或投影后的几何形状计算每行的障碍物范围，合并这些范围后，在绘制文字之前将其传递给 `layoutNextLineRange`。  
- 应将视觉动画与布局动画保持同步。如果一个球体逐渐变形为立方体，需同时调整渲染的单元格缓冲区与障碍物范围，使其数值保持一致；否则动画效果会显得像是人工添加的，而非真正的几何重排。  
- 对于淡入淡出效果，建议使用图层不透明度而非调整字形强度或障碍物尺寸。可将临时的 ASCII 图形放在独立的画布上，通过 CSS 或 GSAP 的不透明度功能实现画布淡入淡出，这样就不会出现几何形状缩小的视觉效果。  
- 令人意外的是，Canvas 的 `ctx.font` 设置速度相当慢；如果字体不会发生变化，应在每帧中**仅设置一次**，而非每次调用 `fillText` 都重新设置。

## 常见问题与陷阱

1. **CSS/Canvas 字体字符串的测量偏差问题。** 虽然通过代码检测得到的字体值为 `ctx.font = "16px Inter"`，但 CSS 中的实际定义却是 `font-family: Inter, sans-serif; font-size: 16px`。只要 Inter 字体能够成功加载，就不会出现问题；但如果该字体无法加载，CSS 会回退到默认的无衬线字体，从而导致测量值出现 5% 到 20% 的偏差。因此，务必提前预加载目标字体，或选择兼容性更强的字体。

2. **在动画循环中重复执行准备操作。** 只有 `layout*` 相关操作的成本较低，若在每一帧都重新调用 `prepare` 方法，将会严重拖累性能。建议将已准备好的相关数据保存在模块作用域内，避免重复处理。

3. **忽略用于字符拆分的 `Intl.Segmenter` 接口。** 对于表情符号、组合标记以及中文字符而言，直接使用 `"é".split("")` 会将其拆分为两个字符。若需单独获取每个可见的字形，应使用 `new Intl.Segmenter(undefined, { granularity: "grapheme" })` 进行处理。

4. **未设置 `extraWidth` 却使用 `break: 'never'` 的芯片元素。** 在 `rich-inline` 模式中，若为某个原子级芯片或提及元素设置了 `break: 'never'`，则必须同时指定 `extraWidth` 值以控制元素内边距——否则芯片的边框可能会超出容器范围。

5. **在仅支持 TypeScript 的项目中通过 `unpkg` 引入 `@chenglou/pretext` 库。** 建议使用 `esm.sh` 工具，它能够自动将 TypeScript 导出模块编译为浏览器可直接使用的 ESM 格式。而直接使用 `unpkg` 可能会导致库文件无法加载，或仅输出原始的 TypeScript 代码。

6. **使用等宽字体作为回退方案会彻底破坏设计效果。** 当用户看到类似等宽字体的输出时，往往是因为 CSS 中的 `font-family` 设置意外回退到了等宽字体系列。建议通过开发者工具查看实际渲染的字体类型，以确保设计效果不受影响。

7. **绕过行与调整宽度**：在沿形状排列内容时，若某行的通道过窄而无法容纳一行文本，应*跳过该行*（即执行 `y += lineHeight; continue;`），而非将极小的 `maxWidth` 值传给 `layoutNextLineRange`——否则 Pretext 会生成看起来破碎的单字行。

8. **打造出色的演示效果**：默认的初始渲染效果往往类似教程级别。建议添加：渐变边框、微妙的扫描线效果、空闲时的自动动画，以及精心设计的交互响应（拖动、悬停、滚动、点击）。缺少这些元素的话，“酷炫的 Pretext 演示”只会沦为“README 的实习生复刻品”。

## 验证清单

- [ ] 演示文件为独立的单个 `.html` 文件——可通过双击或 `python -m http.server` 打开  
- [ ] 已通过 `esm.sh` 导入指定版本的 `@chenglou/pretext`  
- [ ] 语料为真实文本，而非伪文本，并与演示主题相符  
- [ ] 传递给 `prepare` 函数的字体字符串与 CSS 中定义的字体完全一致  
- [ ] `prepare()` / `prepareWithSegments()` 只调用一次，而非每帧都调用  
- [ ] 使用深色背景搭配精心挑选的配色方案——而非默认的白色画布  
- [ ] 至少包含一种交互响应（拖动/悬停/滚动/点击）或空闲时的自动动画  
- [ ] 已通过 `python -m http.server` 在本地进行测试，确认无控制台错误  
- [ ] 在中等配置的笔记本电脑上可实现 60fps 的流畅运行（或已记录降级处理方案）  
- [ ] 添加用户未要求的、能体现巧思的细节  

## 参考：社区演示案例

可克隆这些项目以获取灵感或参考实现模式（均为类似 MIT 许可协议的开源项目，链接见 [pretext.cool](https://www.pretext.cool/)）：

- **Pretext Breaker** — 基于文字块的分割功能 — `github.com/rinesh/pretext-breaker`  
- **Tetris × Pretext** — `github.com/shinichimochizuki/tetris-pretext`  
- **Dragon animation** — `github.com/qtakmalay/PreTextExperiments`  
- **Somnai 编辑引擎** — `github.com/somnai-dreams/pretext-demos`  
- **Bad Apple!! ASCII** — `github.com/frmlinn/bad-apple-pretext`  
- **Drag-sprite 重排功能** — `github.com/dokobot/pretext-demo`  
- **Alarmy 编辑时钟** — `github.com/SmisLee/alarmy-pretext-demo`  

官方演示平台：[chenglou.me/pretext](https://chenglou.me/pretext/) — 支持手风琴式布局、气泡组件、动态布局、编辑引擎、对齐方式对比、网格布局、Markdown 聊天以及富文本笔记功能。
