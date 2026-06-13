---
title: "Hyperframes"
sidebar_label: "Hyperframes"
description: "Create HTML-based video compositions, animated title cards, social overlays, captioned talking-head videos, audio-reactive visuals, and shader transitions us..."
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Hyperframes

利用 HyperFrames 可以创建基于 HTML 的视频合成内容、动画标题卡、社交平台用叠加元素、带字幕的出镜视频、随音频变化的视觉效果以及着色器过渡动画。HTML 是视频内容的真实来源文件。当用户希望从 HTML 组件生成 MP4/WebM 格式的视频、需要在媒体上添加文字/LOGO/图表动画、要求字幕与音频同步、需要文本转语音 narration，或是希望将网站转换为视频时，可使用此技能。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/creative/hyperframes` 安装 |
| 路径 | `optional-skills/creative/hyperframes` |
| 版本 | `1.0.0` |
| 开发者 | heygen-com |
| 许可协议 | Apache-2.0 |
| 支持平台 | linux、macos、windows |
| 标签 | `creative`、`video`、`animation`、`html`、`gsap`、`motion-graphics` |
| 相关技能 | [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video)、[`meme-generation`](/docs/user-guide/skills/optional/creative/creative-meme-generation) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能运行时，智能体看到的指令即为内容。
:::

# HyperFrames

HTML 是视频内容的真实来源文件。一个合成项目实际上是一个包含用于控制时序的 `data-*` 属性、用于实现动画的 GSAP 时间轴以及用于设定外观样式的 CSS 的 HTML 文件。HyperFrames 引擎会逐帧捕获页面内容，再通过 FFmpeg 将其编码为 MP4/WebM 格式。

**与 `manim-video` 的区别：** 对于数学/几何演示内容（如方程、3B1B 风格的可视化），请使用 `manim-video`；而对于动态图形、带字幕的出镜视频、产品展示、社交平台用叠加元素、着色器过渡动画，以及任何基于真实视频/音频素材生成的视觉效果，应选用 `hyperframes`。

## 适用场景

- 用户希望从文本、脚本或网站生成视频
- 动画标题卡、底部信息栏或文字型开场动画
- 带字幕的 narration 视频（文本转语音 + 与波形同步的字幕）
- 随音频变化的视觉效果（节奏同步、频谱条、脉冲光效）
- 场景之间的过渡动画（渐变淡入淡出、擦除效果、着色器变形、白色闪过效果）
- 社交平台风格的叠加元素（Instagram/TikTok/YouTube 风格）
- 网站转视频的流程（输入网址即可生成宣传视频）
- 任何需要以确定性方式渲染为视频文件的 HTML/CSS/JS 动画

**不建议**将此技能用于以下场景：
- 纯数学/方程动画（→ 使用 `manim-video`）
- 图像生成或表情包制作（→ 使用 `meme-generation` 或图像模型）
- 实时视频会议或流媒体播放

## 快速参考

```bash
npx hyperframes init my-video               # scaffold a project
cd my-video
npx hyperframes lint                        # validate before preview/render
npx hyperframes preview                     # live-reload browser preview (port 3002)
npx hyperframes render --output final.mp4   # render to MP4
npx hyperframes doctor                      # diagnose environment issues
```

渲染参数：`--quality draft|standard|high` · `--fps 24|30|60` · `--format mp4|webm` · `--docker`（确保结果可复现）· `--strict`。

完整的 CLI 参考文档：[references/cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/cli.md)。

## 设置（只需执行一次）

```bash
bash "$(dirname "$(find ~/.hermes/skills -path '*/hyperframes/SKILL.md' 2>/dev/null | head -1)")/scripts/setup.sh"
```

脚本功能如下：
1. 检查是否已安装 Node.js 22 及以上版本以及 FFmpeg（如未安装则会输出修复指南）。
2. 全局安装 `hyperframes` CLI（命令为 `npm install -g hyperframes@>=0.4.2`）。
3. 通过 Puppeteer 预缓存 `chrome-headless-shell`——这是通过 Chrome 的 `HeadlessExperimental.beginFrame` 捕获方式实现最佳渲染效果所必需的步骤。
4. 运行 `npx hyperframes doctor` 并输出检测结果。

如果设置过程中出现故障，请参阅 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md) 文档。

## 操作步骤

### 1. 编写 HTML 前先做好规划

在动手编写代码之前，需先从宏观层面明确以下内容：
- **内容核心**——叙事脉络、关键节点、情感基调
- **结构框架**——分镜布局、音轨（视频/音频/叠加层）及时长设置
- **视觉风格**——色彩方案、字体选择以及整体动效风格（爆炸感/电影感/流畅感/科技感）
- **核心画面**——针对每个场景，确定所有元素同时最清晰呈现的瞬间。这便是你需要首先确定的静态布局。

**视觉风格确认机制（强制要求）。** 在编写任何分镜的 HTML 代码之前，必须先明确视觉风格。严禁使用默认或通用的颜色方案（如 `#333`、`#3b82f6` 或 Roboto 字体，这些都属于未完成该步骤的迹象）。请按以下顺序确认：

1. **项目根目录下是否存在 `DESIGN.md`？** → 请严格遵循该文件中规定的色彩、字体、动效规则以及“禁止事项”。
2. **用户是否已指定风格名称**（例如“Swiss Pulse”“深色科技风”“高端品牌风”）？→ 请创建一份简版的 `DESIGN.md`，内容包括 `## Style Prompt`（风格描述）、`## Colors`（3-5种带功能说明的十六进制颜色值）、`## Typography`（1-2种字体系列）以及 `## What NOT to Do`（3-5种应避免的设计误区）。
3. **以上选项均不存在？** → 在编写任何 HTML 代码之前，先回答以下三个问题：
   - 氛围风格？（爆炸感/电影感/流畅感/科技感/混乱感/温暖感）
   - 背景是明亮还是暗色调？
   - 是否有指定的品牌色彩、字体或视觉参考？

   根据答案生成一份 `DESIGN.md`。所有分镜的色彩与字体选择都必须有明确的来源，要么来自 `DESIGN.md`，要么遵循用户的明确指示。

### 2. 创建项目骨架结构

```bash
npx hyperframes init my-video --non-interactive
```

模板选项包括：`blank`、`warm-grain`、`play-mode`、`swiss-grid`、`vignelli`、`decision-tree`、`kinetic-type`、`product-promo`、`nyt-graph`。若需选择特定模板，可输入 `--example <名称>`；若要为动画添加媒体素材，可使用 `--video clip.mp4` 或 `--audio track.mp3`。

### 3. 动画前的布局设计

首先编写**标题帧**的静态 HTML+CSS 代码——此时暂无需使用 GSAP。`.scene-content` 容器需通过 `display:flex` + `gap` 属性填满整个场景（设置 `width:100%; height:100%; padding:Npx`）。应利用内边距将内容向内收缩，切勿在内容容器上使用 `position: absolute; top: Npx` 的方式定位（因为当内容高度超过剩余空间时会导致内容溢出）。

只有在标题帧的样式确认无误后，才添加 `gsap.from()` 动画实现元素进入场景（动画效果为**移动到**CSS 设定的位置），以及 `gsap.to()` 动画实现元素离开场景（动画效果为**从**该位置移开）。

完整的属性数据规范与布局规则可参考 [references/composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/composition.md) 文档。

### 4. 使用 GSAP 进行动画制作

所有动画组合都必须满足以下要求：
- 注册对应的时间轴：`window.__timelines["<composition-id>"] = tl`
- 初始化为暂停状态：`gsap.timeline({ paused: true })`——播放控制权由播放器掌握
- 设置有限的重复次数（禁止使用 `repeat: -1`，否则会干扰捕获引擎的运行）。重复次数的计算公式为：`repeat: Math.ceil(duration / cycleDuration) - 1`
- 确保动画结果可预测——不得使用 `Math.random()`、`Date.now()` 或基于实际时间的逻辑。如需模拟随机效果，可使用带种子的伪随机数生成器
- 动画构建过程需同步完成——在创建时间轴时不得使用 `async`/`await`、`setTimeout` 或 Promise 语句

GSAP 的核心 API（包括动画过渡函数、缓动函数、错开动画功能以及时间轴相关操作）的详细说明请参阅 [references/gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/gsap.md)。

### 5. 场景间的过渡效果

多场景动画组合必须包含过渡效果，具体规则如下：
1. **所有场景之间都必须使用过渡效果**——禁止直接跳转
2. **每个场景元素都必须添加进入动画**（使用 `gsap.from(...)`）
3. **除最后一个场景外，不得使用离开动画**——因为场景间的过渡本身就起到了离开动画的作用
4. 最后一个场景可以设置淡出效果

如需安装着色器过渡效果（如 `flash-through-white`、`liquid-wipe` 等），可使用命令 `npx hyperframes add <过渡效果名称>`。完整的过渡效果列表可通过 `npx hyperframes add --list` 查看。

### 6. 音频、字幕、文本转语音、音频响应式效果及高亮显示

- **音频**：必须使用独立的 `<audio>` 元素处理（视频则需设置为 `muted playsinline` 状态）
- **文本转语音**：可使用命令 `npx hyperframes tts "脚本文本" --voice af_nova --output narration.wav` 生成语音文件。可通过 `--list` 查看可用的语音选项。语音 ID 的首字母代表对应语言（`a`/`b` 表示英语，`e` 表示西班牙语，`f` 表示法语，`j` 表示日语，`z` 表示普通话等）——命令行工具会自动识别语音合成的语言环境，如需手动指定可添加 `--lang` 参数。若需处理非英语文本，系统需预先安装 `espeak-ng` 工具
- **字幕**：可使用命令 `npx hyperframes transcribe narration.wav` 生成逐词字幕文件。可根据字幕的风格选择对应的字体与色调（包括宣传风格、企业风格、教程风格、叙事风格、社交媒体风格等，具体选项参见 `references/features.md` 文档中的表格）。**语言规则**：除非确认音频为英语，否则严禁使用 `.en` 风格的轻声字幕模型——因为该模型会直接对非英语音频进行翻译而非转写。每个字幕组在完成退出动画后，都必须通过代码 `tl.set(el, { opacity: 0, visibility: "hidden" }, group.end)` 确保其完全隐藏，否则后续的字幕组仍可能显示该组的内容
- **音频响应式视觉效果**：需预先提取音频中的不同频段（低音、中音、高音），然后在时间轴中使用 `for` 循环逐帧生成对应视觉效果，例如通过 `tl.call(draw, [], f / fps)` 实现动态变化——单一的长时间动画无法实现音频响应式效果。可将低音映射为缩放动画（产生脉冲效果），高音映射为文本阴影/盒阴影效果（产生发光效果），整体音量则映射为透明度、Y 轴位置或背景颜色等属性。应避免使用常见的均衡器条式视觉效果，而是让内容本身主导视觉呈现，音频仅用于驱动视觉效果的变化
- **标记式高亮效果**：通过 CSS+GSAP 技术实现文本强调的突出、圆圈、爆裂、涂鸦、草图等效果，这类效果的结果是可预测的——详细说明请参见 `references/features.md#marker-highlighting`。该类效果支持完全搜索功能，且不使用动画形式的 SVG 过滤效果
- **场景过渡效果**：所有多场景动画组合都必须使用过渡效果（禁止直接跳转）。过渡效果既包括 CSS 原生效果（如推入滑入、模糊渐变、缩放穿过、错开排列的方块等），也可通过 `npx hyperframes add` 命令添加着色器过渡效果（如 `flash-through-white`、`liquid-wipe`、`cross-warp-morph`、`chromatic-split` 等）。不同的过渡效果适用于不同风格和氛围，详细列表可在 `references/features.md#transitions` 中查看。同一动画组合中不得同时使用 CSS 过渡效果与着色器过渡效果

### 7. 代码检查、验证、调试、预览与渲染

```bash
npx hyperframes lint              # catches missing data-composition-id, overlapping tracks, unregistered timelines
npx hyperframes validate          # WCAG contrast audit at 5 timestamps
npx hyperframes inspect           # visual layout audit — overflow, off-frame elements, occluded text
npx hyperframes preview           # live browser preview
npx hyperframes render --quality draft --output draft.mp4    # fast iteration
npx hyperframes render --quality high --output final.mp4     # final delivery
```

`hyperframes validate` 会采样每个文本元素背后的背景像素，并对对比度低于 4.5:1（大字体则为 3:1）的情况发出警告。`hyperframes inspect` 则是用于布局检查的工具——它会在不同时间点渲染页面，从而发现静态检查无法识别的问题（例如在 4.5 秒时标题才超出安全区域、当标题为最长版本时卡片内容溢出、某个元素被过渡效果遮盖等）。尤其建议在包含对话框、卡片、字幕或密集排版的合成内容上使用 `inspect` 功能。

### 8. 网站转视频（若用户提供 URL）

请按照 [references/website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/website-to-video.md) 中的 7 步捕获转视频流程操作：捕获 → DESIGN.md → SCRIPT.md → 分镜脚本 → 合成 → 渲染 → 输出。

## 常见问题

- **`HeadlessExperimental.beginFrame' wasn't found`** —— Chromium 147 及更高版本已移除该协议。请确保使用 `hyperframes@>=0.4.2` 版本（该版本会自动检测并回退到截图模式）。应急方案：设置 `export PRODUCER_FORCE_SCREENSHOT=true`。相关问题可参考 [hyperframes#294](https://github.com/heygen-com/hyperframes/issues/294) 以及 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md)。
- **使用系统自带的 Chrome（而非 `chrome-headless-shell`）** —— 渲染过程可能会卡住 120 秒后超时。请运行 `npx puppeteer browsers install chrome-headless-shell`（setup.sh 脚本已包含此操作）。`hyperframes doctor` 命令可显示将使用的二进制文件。
- **在任何地方使用 `repeat: -1`** —— 会导致捕获引擎失效。务必设置一个有限的重复次数。
- **对后续加载的剪辑元素使用 `gsap.set()`** —— 页面加载时该元素还不存在。应在时间轴上、在剪辑元素的 `data-start` 时间点或之后，使用 `tl.set(selector, vars, timePosition)` 方法。
- **内容文本中使用 `<br>`** —— 强制换行无法考虑实际渲染后的字体宽度，因此会导致自然换行后再通过 `<br>` 进行二次换行。建议使用 `max-width` 属性让文本自动换行。例外情况：那些刻意将每个单词单独占一行的简短显示标题。
- **对 `visibility` 或 `display` 属性进行动画处理** —— GSAP 无法对这些属性做过渡动画。应使用 `autoAlpha` 属性（可同时控制可见性和透明度）。
- **调用 `video.play()` 或 `audio.play()`** —— 播放功能由框架统一管理，切勿自行调用这些方法。
- **异步构建时间轴** —— 页面加载后，捕获引擎会同步读取 `window.__timelines` 数据。切勿将时间轴的构建操作放在 `async`、`setTimeout` 或 Promise 中。
- **将独立的 `index.html` 文件包裹在 `<template>` 中** —— 这会导致浏览器无法显示任何内容。只有通过 `data-composition-src` 加载的**子合成内容**才可使用 `<template>`。
- **用视频代替音频** —— 应始终使用静音的 `<video>` 元素，并搭配独立的 `<audio>` 元素。

## 验证步骤

在渲染前后需进行以下验证：

1. **通过检查、验证和布局分析**：执行 `npx hyperframes lint --strict && npx hyperframes validate && npx hyperframes inspect`（lint 用于检测结构问题，validate 用于检测对比度问题，inspect 用于检测视觉布局及溢出问题——如出现警告，请参考 troubleshooting.md）。
2. **动画协调性检查** —— 对于新制作的合成内容或进行了重大动画修改的情况，需运行动画映射检查。执行 `npx hyperframes init` 可将相关技能脚本复制到项目中，此时路径为项目本地路径：
   ```bash
   node skills/hyperframes/scripts/animation-map.mjs <composition-dir> \
     --out <composition-dir>/.hyperframes/anim-map
   ```
该工具会生成一个包含以下信息的单一 `animation-map.json` 文件：每个动画过渡的摘要、ASCII格式的甘特图时间线、元素错开检测结果、无动画区域信息（持续时间超过1秒的区域）、元素生命周期数据，以及各类状态标记（如 `offscreen`、`collision`、`invisible`、动画速度过快的 `<0.2s`、动画速度过慢的 `>2s` 等）。需仔细查看这些摘要与标记，针对每一项问题进行修正或给出合理解释；若只是细微调整则可直接跳过。

3. **文件存在且大小非零：** 执行命令 `ls -lh final.mp4`。
4. **视频时长与 `data-duration` 参数一致：** 执行命令 `ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4`。
5. **视觉检查：** 提取视频中的中间帧，命令为 `ffmpeg -i final.mp4 -ss 00:00:05 -vframes 1 preview.png`。
6. **确认是否存在预期音频：** 执行命令 `ffprobe -v error -show_streams -select_streams a -of default=nw=1:nk=1 final.mp4 | head -1`。

如果 `hyperframes render` 命令执行失败，请运行 `npx hyperframes doctor` 并在报告问题时附上该工具的输出结果。

## 参考文档

- [composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/composition.md) —— 数据属性、时间线规范、不可违反的规则、排版与资源相关规则
- [cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/cli.md) —— 所有CLI命令说明（包括 init、capture、lint、validate、inspect、preview、render、transcribe、tts、doctor、browser、info、upgrade、benchmark 等）
- [gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/gsap.md) —— HyperFrames所使用的GSAP核心API（包括过渡动画、缓动函数、错开效果、时间线控制、matchMedia功能等）
- [features.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/features.md) —— 字幕功能、文本转语音、音频响应式功能、标记高亮显示、过渡动画（按需加载）
- [website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/website-to-video.md) —— 从网页到视频的7步制作流程
- [troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/hyperframes/references/troubleshooting.md) —— OpenClaw相关问题解决方案、环境变量设置、常见的渲染错误处理方法
