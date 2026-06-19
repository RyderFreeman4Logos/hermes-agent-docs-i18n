---
title: "Pretext"
sidebar_label: "Pretext"
description: "Use when building creative browser demos with @chenglou/pretext — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry gam..."
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Pretext

当使用 @chenglou/pretext 构建创意型浏览器演示时即可使用该技能——它支持无需 DOM 的 ASCII 艺术文本排版、围绕障碍物的文字流动效果、以文字为几何元素的互动游戏、动态排版，以及基于文字的生成艺术。默认情况下会生成单文件 HTML 演示。

## 技能元数据

| | |
|---|---|
| 来源 | 已内嵌（默认即安装） |
| 路径 | `skills/creative/pretext` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `creative-coding`、`typography`、`pretext`、`ascii-art`、`canvas`、`generative`、`text-layout`、`kinetic-typography` |
| 相关技能 | [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js)、[`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design)、[`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw)、[`html-artifact`](/docs/user-guide/skills/bundled/creative/creative-html-artifact) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能运行时，Agent 就会看到这些指令作为操作指南。
:::

# Pretext 创意演示

## 概述

[`@chenglou/pretext`](https://github.com/chenglou/pretext) 是由 Cheng Lou 开发的一个仅 15KB 大小、无任何依赖的 TypeScript 库（他同样开发过 React 核心、ReasonML 和 Midjourney），专为**无需 DOM 的多行文本测量与排版**而设计。它的功能非常专注：给定 `(text, font, width)` 参数，即可通过 Canvas 测量方式返回换行位置、每行宽度、每个字素的精确位置以及整体高度，全程无需重新布局。

这听起来像管道工程，但实际上并非如此。由于其高效且基于几何计算，它实际上是一种**创意基础工具**：你可以让段落围绕以 60fps 移动的精灵元素重新布局，打造以真实文字构成关卡几何结构的游戏，让 ASCII 标识在文字流中移动，将文本拆解为具有精确字素起始位置的粒子，或是实现无需调用 `getBoundingClientRect` 即可完成的“收缩包装”多行 UI 效果。

开发此技能的目的是让 Hermes 能够利用它创建**令人惊叹的演示效果**——那种人们会发到 X 平台上的作品。你可以查看 `pretext.cool` 以及 `chenglou.me/pretext` 来了解社区中的优秀演示案例。

## 适用场景

当用户要求实现以下功能时，可使用该技能：
- “Pretext 演示”/“超酷的 Pretext 效果”/“以文字实现 X 功能”
- 文字围绕移动的图形流动（适用于首页标题区、杂志版面、动态长文页面）
- 使用**真实文字或段落**而非等宽字体网格实现的 ASCII 艺术效果
- 以文字作为游戏场地、障碍物或砖块的互动游戏（如用字母构成的俄罗斯方块、用文字构成的打砖块游戏）
- 具有字素级物理效果的动态排版（如破碎、散射、群聚、流动效果）
- 排版类生成艺术，尤其适用于非拉丁字母或混合字体场景
- 多行“收缩包装”UI（在尽可能小的容器宽度下仍能完整显示文本）
- 任何需要在渲染前就确定换行位置的场景

**不推荐用于以下情况**：
- CSS 已经能解决布局问题的静态 SVG/HTML 页面——直接使用 CSS 即可
- 富文本编辑器、通用内联格式化引擎（Pretext 的功能范围本就较为有限）
- 图片转文字的功能（可使用 `ascii-art` / `ascii-video` 技能）
- 完全不涉及文字元素的纯 Canvas 生成艺术——此时应使用 `p5js`

## 创意标准

这是在浏览器中呈现的视觉艺术作品。Pretext 只负责提供数值数据，**实际绘制效果需由你完成**。

- **切勿提交“Hello World”式的简单演示**。`hello-orb-flow.html` 模板仅作为**起点**，每个最终提交的演示都应加入有意的色彩、动态效果、构图设计，以及一个用户虽未明确提出但会欣赏的视觉细节。
- **采用深色背景搭配暖色调主色，精心挑选配色方案**。经典的琥珀色配黑色（类似 CRT 显示器/终端风格）很合适，冷白色配炭灰色（适合杂志类设计）以及低饱和度的柔和色彩（类似凸版印刷效果）也是不错的选择。选定一种风格后就要坚持使用。
- **比例字体是核心要素**。Pretext 的设计理念就是“非等宽字体”，因此应充分利用这一特点。可选择 Iowan Old Style、Inter、JetBrains Mono、Helvetica Neue 或变量字体，切勿默认使用无衬线字体。
- **使用真实来源的文本，而非 lorem ipsum**。演示内容应当具有实际意义，可以是简短的宣言、诗歌、真实代码、找到的随机文本，或是该库自身的 README 文件——绝不能使用 `lorem ipsum` 这类虚拟文本。
- **确保首次渲染效果出色**。不得出现加载状态或空白画面，演示页面在打开的瞬间就必须呈现出可直接发布的完美状态。

## 技术栈

每个演示均为独立的单文件 HTML，无需任何构建步骤。

| 层级 | 工具 | 用途 |
|-------|------|---------|
| 核心功能 | 通过 `esm.sh` CDN 引入的 `@chenglou/pretext` | 文本测量与行布局计算 |
| 渲染层 | HTML5 Canvas 2D | 字素渲染及每帧画面合成 |
| 分割处理 | 内置的 `Intl.Segmenter` | 处理表情符号、汉字及组合字符的字素分割 |
| 交互功能 | 原生 DOM 事件 | 鼠标、触摸、滚轮交互——无需任何框架支持 |

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

几乎所有场景都可归结为以下两种形式之一。建议两者都加以了解。

### 场景一 — 先进行测量，再通过 CSS/DOM 进行渲染

```js
const prepared = prepare(text, "16px Inter");
const { height, lineCount } = layout(prepared, 320, 20);
```

你仍然让浏览器来绘制文本。Pretext仅能根据给定的宽度告知文本框的高度，**无需**读取DOM元素。适用于以下场景：
- 行内文本较多的虚拟化列表
- 需要精确控制卡片高度的Masonry布局
- 开发阶段检测“此标签是否能够显示完整”
- 在加载远程文本时防止布局偏移

**务必确保`font`与`letterSpacing`设置与CSS完全一致。** Canvas的`ctx.font`格式（例如`"16px Inter"`、`"500 17px 'JetBrains Mono'"`）必须与实际渲染的CSS格式匹配，否则测量结果会出现偏差。

### 使用场景2 — 自行进行测量与渲染

```js
const prepared = prepareWithSegments(text, FONT);
const { lines } = layoutWithLines(prepared, 320, 26);
for (let i = 0; i < lines.length; i++) {
  ctx.fillText(lines[i].text, 0, i * 26);
}
```

此处即为创意内容的生成场所。由于您拥有该绘图内容，因此可以：
- 将其渲染为画布、SVG、WebGL格式，或适配任意坐标系统
- 对每个字符应用不同的变换效果（旋转、抖动、缩放、透明度调整）
- 利用线条元数据（宽度、字素位置）作为几何结构

对于**每行字符宽度可变**的排版场景（如环绕形状的文字、环形区域内的文字、非矩形列中的文字）：

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

这是整个库中最核心的布局模式。正是它实现了“文本环绕被拖动的精灵显示”的效果——也就是在X平台上广为流传的那个演示案例。

### 值得了解的辅助函数

- `measureLineStats(prepared, maxWidth)` → `{ lineCount, maxLineWidth }` — 返回最宽的行，即多行换行时的最大宽度。
- `walkLineRanges(prepared, maxWidth, callback)` — 无需创建字符串即可遍历各行。当不需要字符本身时，可用于基于字形而非字符的统计或物理计算。
- `@chenglou/pretext/rich-inline` — 用于处理混合字体、图标及提及内容的段落的相同系统。需从子路径导入该模块。

## 演示案例模式

社区中的示例代码（详见 `references/patterns.md`）可归纳为几类典型的布局模式。请选择其中一种进行修改扩展——除非有特殊要求，否则无需自行创建新类别。

| 模式 | 核心API | 示例思路 |
|---|---|---|
| **绕障碍物重排文本** | `layoutNextLineRange` + 每行宽度计算函数 | 文章段落根据被拖动的光标精灵位置自动调整布局 |
| **文本作为几何图形的游戏** | `layoutWithLines` + 每行碰撞矩形检测 | 每块砖块代表一个经过测量的单词的打砖游戏 |
| **破碎/粒子效果** | `walkLineRanges` → 计算每个字形的(x,y)坐标 → 应用物理效果 | 点击后句子会分解为单个字母的特效 |
| **ASCII障碍物排版** | `layoutNextLineRange` + 每行障碍物宽度计算 | 使用位图形式的ASCII图标作为障碍物，实现文字根据其实际几何形状环绕排列的效果，同时支持形状变形和可拖动的线条对象 |
| **多列编辑布局** | 为每列分别调用 `layoutNextLineRange` + 共享光标 | 带有引文块的动态杂志式页面布局 |
| **动态文字效果** | `layoutWithLines` + 每行随时间变化的变换效果 | 模拟《星球大战》中的滚动字幕、波浪效果、弹跳动画或故障艺术效果 |
| **多行自动换行** | `measureLineStats` | 引用卡片能自动适应最紧凑的容器尺寸 |

如需可直接运行的单文件示例，可查看 `templates/donut-orbit.html` 和 `templates/hello-orb-flow.html`。

## 工作流程

1. 根据用户需求，从上表中选择一种布局模式。
2. 从模板开始编写：
   - `templates/hello-orb-flow.html` — 文本环绕移动球体的效果（绕障碍物重排模式）
   - `templates/donut-orbit.html` — 更高级的示例：包含经过测量的ASCII图标障碍物、可拖动的线框球体/立方体、形状变形区域、可选择的DOM文本以及仅开发人员可见的控制界面
   - 使用 `write_file` 函数将代码保存到 `/tmp/` 目录或用户工作区中的新 `.html` 文件中。
3. 更换为符合需求的实际文本内容，长度建议为10-100句，避免使用占位文本。
4. 调整视觉风格——包括字体、配色方案、构图以及交互效果。这是最关键的部分，切勿跳过。
5. 在本地进行测试验证：
   ```sh
   cd <dir-with-html> && python3 -m http.server 8765
   # then open http://localhost:8765/<file>.html
   ```
6. **检查控制台输出**——如果使用无效的字体字符串调用 `prepareWithSegments`，pretext 会抛出错误；所有现代浏览器都支持 `Intl.Segmenter`。

7. **向用户展示文件路径，而不仅仅是代码**——他们希望直接打开该文件。

## 性能注意事项

- `prepare()` / `prepareWithSegments()` 是计算成本较高的操作。针对每组文本与字体，只需调用一次，并将返回的句柄缓存起来。
- 当窗口大小改变时，只需重新运行 `layout()` / `layoutWithLines()`，无需再次准备数据。
- 对于那些文字内容不变但几何形状会变化的逐帧动画，对于常规长度的段落，通过循环频繁调用 `layoutNextLineRange` 的成本相当低，完全可以实现 60fps 的流畅显示。
- 在逐帧渲染 ASCII 图形时，应使用单元缓冲区（如 `Uint8Array` 或类型化数组），根据这些单元数据或投影后的几何信息计算每行的障碍物范围，再将这些范围合并后传递给 `layoutNextLineRange`，最后再绘制文字。
- 应将视觉动画与布局动画保持同步。如果一个球体逐渐变形为立方体，需同时调整渲染的单元缓冲区及障碍物范围，使其数值保持一致；否则动画效果会显得像是硬加上去的，而非真正的流体重排。
- 对于淡入淡出效果，建议使用图层不透明度而非改变字形强度或障碍物尺寸。可将临时的 ASCII 图标放在独立的画布上，通过 CSS 或 GSAP 的不透明度功能实现该画布的淡入淡出，这样就不会出现几何图形缩小的视觉效果。
- 令人意外的是，Canvas 的 `ctx.font` 设置速度相当慢；如果字体不会变化，每帧只需设置一次，而非每次调用 `fillText` 都要设置。

## 常见误区

1. **CSS/Canvas 中的字体字符串不一致**。虽然通过 `ctx.font = "16px Inter"` 进行了测量，但 CSS 中可能定义为 `font-family: Inter, sans-serif; font-size: 16px`。只要 Inter 字体能正常加载，问题不大。但如果 Inter 字体无法加载，CSS 会回退到默认的无衬线字体，从而导致测量结果出现 5-20% 的偏差。务必提前预加载该字体，或使用兼容性更强的字体系列。

2. **在动画循环中重复准备数据**。只有 `layout*` 系列函数的计算成本较低。若每帧都重新调用 `prepare`，会严重拖慢性能。应将准备好的句柄保存在模块作用域内。

3. **忘记使用 `Intl.Segmenter` 进行字素分割**。对于表情符号、组合标记以及 CJK 字符，直接使用 `"é".split("")` 会将其拆分为两个字符。若需获取单个可见字素，应使用 `new Intl.Segmenter(undefined, { granularity: "grapheme" })`。

4. **使用 `break: 'never'` 时未设置 `extraWidth`**。在 `rich-inline` 模式中，若为某个独立组件使用 `break: 'never'`，则必须同时指定用于填充空间的 `extraWidth`——否则组件的边框可能会超出容器范围。

5. **在仅支持 TypeScript 的项目中通过 `unpkg` 引入 `@chenglou/pretext`**。建议使用 `esm.sh`，它能够自动将 TypeScript 导出编译为浏览器可直接使用的 ESM 格式。而 `unpkg` 可能无法找到该模块，或直接返回原始的 TypeScript 代码。

6. **使用等宽字体作为回退方案反而破坏了整体效果**。如果用户看到的输出呈现为等宽字体样式，很可能是 CSS 中的 `font-family` 选项默认选择了等宽字体。应通过开发者工具查看实际渲染的字体。

7.**在围绕形状换行时是跳过该行还是调整宽度**。如果某行的路径过窄，无法容纳一行文字，应直接跳过该行（即执行 `y += lineHeight; continue;`），而非将过小的 `maxWidth` 传递给 `layoutNextLineRange`——否则 pretext 会生成仅包含一个字素的行，看起来很不自然。

8.**发布的演示版本过于简单**。默认的初次渲染效果往往类似教学示例。应进一步添加：暗角效果、微妙的扫描线、空闲时的自动动画，以及精心设计的交互响应（如拖动、悬停、滚动、点击）。缺少这些元素的话，“酷炫的 pretext 演示”只会变成“README 文件里的示例代码”。

## 验证清单

- [ ] 演示文件为独立的单个 `.html` 文件——可通过双击或运行 `python3 -m http.server` 打开。
- [ ] 通过 `esm.sh` 引入 `@chenglou/pretext`，并指定固定版本号。
- [ ] 使用真实的散文文本作为语料，而非伪文本 lorem ipsum，且内容与演示主题相符。
- [ ] 传递给 `prepare` 函数的字体字符串与 CSS 中定义的字体完全一致。
- [ ] `prepare()` / `prepareWithSegments()` 只调用一次，而非每帧都调用。
- [ ] 使用深色背景搭配精心挑选的调色板——而非默认的白色画布。
- [ ] 至少包含一种交互响应（拖动/悬停/滚动/点击）或空闲时的自动动画。
- [ ] 已在本地使用 `python3 -m http.server` 进行测试，确认没有控制台错误。
- [ ] 在中等配置的笔记本电脑上可实现 60fps 的流畅显示（或已记录降级方案）。
- [ ] 添加用户未要求但能提升体验的“额外细节”。

## 参考：社区演示项目

可克隆以下项目以获取灵感或参考实现模式（均为类似 MIT 开源协议，链接来自 [pretext.cool](https://www.pretext.cool/)）：

- **Pretext Breaker**——用文字方块构成的 breakout 游戏——`github.com/rinesh/pretext-breaker`
- **Tetris × Pretext**——俄罗斯方块与 pretext 的结合——`github.com/shinichimochizuki/tetris-pretext`
- **Dragon animation**——龙形动画效果——`github.com/qtakmalay/PreTextExperiments`
- **Somnai editorial engine**——Somnai 编辑引擎演示——`github.com/somnai-dreams/pretext-demos`
- **Bad Apple!! ASCII**——“坏苹果”ASCII 动画——`github.com/frmlinn/bad-apple-pretext`
- **Drag-sprite reflow**——可拖动图标的流体重排演示——`github.com/dokobot/pretext-demo`
- **Alarmy editorial clock**——Alarmy 编辑时钟演示——`github.com/SmisLee/alarmy-pretext-demo`

官方演示平台：[chenglou.me/pretext](https://chenglou.me/pretext/)——包含手风琴式布局、气泡元素、动态布局、编辑引擎、对齐方式对比、网格布局、Markdown 聊天以及富文本笔记等功能。
