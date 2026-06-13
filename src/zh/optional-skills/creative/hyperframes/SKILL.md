---
name: hyperframes
description: Create HTML-based video compositions, animated title cards, social overlays, captioned talking-head videos, audio-reactive visuals, and shader transitions using HyperFrames. HTML is the source of truth for video. Use when the user wants a rendered MP4/WebM from an HTML composition, wants to animate text/logos/charts over media, needs captions synced to audio, wants TTS narration, or wants to convert a website into a video.
version: 1.0.0
author: heygen-com
license: Apache-2.0
platforms: [linux, macos, windows]
prerequisites:
  commands: [node, ffmpeg, npx]
metadata:
  hermes:
    tags: [creative, video, animation, html, gsap, motion-graphics]
    related_skills: [manim-video, meme-generation]
    category: creative
    requires_toolsets: [terminal]
---

# HyperFrames

HTML 是视频内容的真实来源。一个合成内容由一个包含用于控制时序的 `data-*` 属性的 HTML 文件、用于实现动画效果的 GSAP 时间轴，以及用于控制外观样式的 CSS 组成。HyperFrames 引擎会逐帧捕获页面内容，并使用 FFmpeg 将其编码为 MP4/WebM 格式。

**与 `manim-video` 的区别：** 若需要制作数学或几何演示内容（如方程、3B1B 风格的图形），请使用 `manim-video`；而若需制作动态图形、带字幕的出镜讲解、产品展示、社交平台贴片、着色器过渡效果，或是任何基于真实视频/音频素材的内容，应选用 `hyperframes`。

## 适用场景

- 用户要求根据文本、脚本或网页生成渲染后的视频
- 动态标题卡、底部信息栏或排版式开场动画
- 带字幕的旁白视频（文本合成语音与字幕同步于波形）
- 随音频变化的视觉效果（节奏同步、频谱条、脉冲光效）
- 场景之间的过渡效果（渐变淡入淡出、擦除效果、着色器变形、白色闪过）
- 社交平台风格贴片（Instagram/TikTok/YouTube 风格）
- 网站转视频流程（通过 URL 捕获内容并制作宣传视频）
- 任何需要以确定性方式渲染为视频文件的 HTML/CSS/JS 动画

**不推荐用于以下场景：**
- 纯数学或方程动画（→ `manim-video`）
- 图像生成或表情包制作（→ `meme-generation`、图像模型）
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

完整的 CLI 参考文档：[references/cli.md](references/cli.md)。

## 设置（仅需执行一次）

```bash
bash "$(dirname "$(find ~/.hermes/skills -path '*/hyperframes/SKILL.md' 2>/dev/null | head -1)")/scripts/setup.sh"
```

脚本功能如下：
1. 检查系统是否已安装 Node.js 22 及以上版本以及 FFmpeg（如未安装则会输出修复指南）。
2. 全局安装 `hyperframes` CLI 工具（命令为 `npm install -g hyperframes@>=0.4.2`）。
3. 通过 Puppeteer 预缓存 `chrome-headless-shell` —— 这是通过 Chrome 的 `HeadlessExperimental.beginFrame` 捕获方式实现最佳渲染效果所必需的步骤。
4. 运行 `npx hyperframes doctor` 命令并输出检测结果。

如果设置过程中出现故障，请参考 [references/troubleshooting.md](references/troubleshooting.md) 文档。

## 执行步骤

### 1. 编写 HTML 之前的规划

在动手编写代码之前，需先从宏观层面明确以下内容：
- **内容核心** —— 故事脉络、关键场景、情感节奏
- **结构框架** —— 分镜布局、音轨类型（视频/音频/叠加层）及时长设置
- **视觉风格** —— 颜色方案、字体选择以及整体动态风格（爆炸感/电影感/流畅感/科技感）
- **核心画面** —— 对于每个场景而言，指所有元素同时最清晰呈现的瞬间。这正是你需要首先确定的静态布局。

**视觉风格确认环节（强制要求）。** 在编写任何分镜的 HTML 代码之前，必须先确定视觉风格。切勿使用默认或通用的颜色方案来创建分镜（如使用 `#333`、`#3b82f6` 或 Roboto 字体，都说明此步骤已被跳过）。请按以下顺序确认：

1. **项目根目录下是否存在 `DESIGN.md` 文件？** → 请严格遵循该文件中规定的颜色、字体、动态规则以及“禁忌事项”。
2. **用户是否已指定某种风格**（例如“瑞士脉动风”、“深色科技风”、“奢华品牌风”）？→ 则需创建一份简版的 `DESIGN.md`，内容包括 `## Style Prompt`（风格描述）、`## Colors`（3-5种带功能说明的十六进制颜色值）、`## Typography`（1-2种字体系列）以及 `## What NOT to Do`（3-5种应避免的设计误区）。
3. **以上选项均不适用？** → 在编写任何 HTML 代码之前，先回答以下三个问题：
   - 整体氛围是怎样的？（爆炸感/电影感/流畅感/科技感/混乱感/温暖感）
   - 背景是明亮的还是暗色的？
   - 是否有特定的品牌颜色、字体或视觉参考？

   根据回答内容生成一份 `DESIGN.md` 文件。所有分镜的色彩方案和字体选择都必须有明确的来源，要么来自 `DESIGN.md`，要么遵循用户的明确指示。

### 2. 建立项目框架

```bash
npx hyperframes init my-video --non-interactive
```

模板选项包括：`blank`、`warm-grain`、`play-mode`、`swiss-grid`、`vignelli`、`decision-tree`、`kinetic-type`、`product-promo`、`nyt-graph`。若需选择特定模板，可使用 `--example <name>` 参数；若要为动画添加媒体素材，可传递 `--video clip.mp4` 或 `--audio track.mp3` 参数。

### 3. 动画前的布局设计

首先编写**标题帧**的静态 HTML+CSS 代码——此时暂不需要使用 GSAP。`.scene-content` 容器需通过 `display:flex` + `gap` 属性将整个场景填满（设置 `width:100%; height:100%; padding:Npx`）。应利用内边距将内容向内压缩，切勿在内容容器上使用 `position: absolute; top: Npx` 的方式定位（因为当内容高度超过剩余空间时会导致内容溢出）。

只有在标题帧的样式确认无误后，才能添加 `gsap.from()` 动画以实现元素进入场景（动画效果为移动到 CSS 中设定的位置），以及 `gsap.to()` 动画实现元素离开场景（动画效果为从该位置移出）。

完整的属性数据结构及布局规则详见 [references/composition.md](references/composition.md) 文档。

### 4. 使用 GSAP 进行动画制作

所有动画组合都必须满足以下要求：
- 注册对应的时间轴：`window.__timelines["<composition-id>"] = tl`
- 初始化为暂停状态：`gsap.timeline({ paused: true })`——播放控制权由播放器掌握
- 设置有限的循环次数（禁止使用 `repeat: -1`，否则会干扰捕获引擎的工作）。计算公式为：`repeat: Math.ceil(duration / cycleDuration) - 1`
- 确保动画结果可预测——不得使用 `Math.random()`、`Date.now()` 或基于实际时间的逻辑。如需模拟随机效果，可使用已设置种子的伪随机数生成器
- 动画构建过程必须同步进行——在创建时间轴时不得使用 `async`/`await`、`setTimeout` 或 Promise 语句

GSAP 的核心 API（包括缓动函数、动画序列控制、交错动画及时间轴相关功能）的详细说明请参阅 [references/gsap.md](references/gsap.md) 文档。

### 5. 场景之间的过渡效果

包含多个场景的动画组合必须设置过渡效果，具体规则如下：
1. **所有场景之间都必须使用过渡效果**——禁止直接跳转
2. **每个场景元素都必须添加进入动画**（使用 `gsap.from(...)`）
3. **除最后一个场景外，不得使用离开动画**——因为场景之间的过渡本身就起到了离开动画的作用
4. 最后一个场景可以选择渐隐退出

如需使用着色器实现的过渡效果（如 `flash-through-white`、`liquid-wipe` 等），可使用命令 `npx hyperframes add <transition-name>` 进行安装。完整的过渡效果列表可通过 `npx hyperframes add --list` 查看。

### 6. 音频、字幕、文本转语音、音频响应式效果及高亮显示功能

- **音频**：必须使用独立的 `<audio>` 元素播放（视频则需设置为 `muted playsinline` 状态）
- **文本转语音**：可使用命令 `npx hyperframes tts "脚本文本" --voice af_nova --output narration.wav` 实现文本转语音功能。可通过 `--list` 参数查看可用的语音选项。语音编号的首字母代表对应语言（`a`/`b` 表示英语，`e` 表示西班牙语，`f` 表示法语，`j` 表示日语，`z` 表示普通话等）——命令行工具会自动识别语音合成的语言环境，如需手动指定语言可添加 `--lang` 参数。若需处理非英语文本，系统需预先安装 `espeak-ng` 工具
- **字幕**：可使用命令 `npx hyperframes transcribe narration.wav` 生成逐词字幕文件。可根据字幕的风格选择对应的呈现方式（如宣传风格、商务风格、教程风格、叙事风格或社交平台风格，具体选项详见 `references/features.md` 文档中的表格）。**语言规则**：除非确认音频为英语，否则不得使用 `.en` 类型的低语风格字幕模型——因为该模型会直接翻译非英语音频而非进行转录。每个字幕组在完成退出动画后，都必须通过代码 `tl.set(el, { opacity: 0, visibility: "hidden" }, group.end)` 确保其完全隐藏，否则后续的字幕组仍可能显示被遮挡的内容
- **音频响应式视觉效果**：需预先提取音频中的不同频段（低音、中音、高音），然后在时间轴中使用 `for` 循环配合 `tl.call(draw, [], f / fps)` 逐帧生成对应视觉效果——单一的长时间动画无法实现音频响应功能。可将低音映射为 `scale` 动画（产生脉冲效果），高音映射为 `textShadow`/`boxShadow` 动画（产生发光效果），整体音量则映射为 `opacity`/`y`/`backgroundColor` 等属性。应避免使用常见的均衡器条式视觉效果，而应让内容本身主导视觉呈现，音频仅用于驱动视觉效果的变化
- **标记式高亮效果**：通过 CSS+GSAP 实现文本强调的突出、圆圈、爆裂、涂鸦、草图等效果，这类效果的结果是可预测的——详情请参阅 `references/features.md#marker-highlighting` 文档。该效果支持完整播放进度跳转，且不使用动态生成的 SVG 滤镜
- **场景过渡效果**：所有包含多个场景的动画组合都必须使用过渡效果（禁止直接跳转）。过渡效果可选择 CSS 原生效果（如推入滑动、模糊渐变、缩放穿越、错位块状效果），或通过 `npx hyperframes add` 命令添加着色器实现的过渡效果（如 `flash-through-white`、`liquid-wipe`、`cross-warp-morph`、`chromatic-split` 等）。不同风格的过渡效果及其适用场景详见 `references/features.md#transitions` 文档。同一动画组合中不得同时使用 CSS 过渡效果和着色器过渡效果

### 7. 代码检查、验证、调试、预览及渲染

```bash
npx hyperframes lint              # catches missing data-composition-id, overlapping tracks, unregistered timelines
npx hyperframes validate          # WCAG contrast audit at 5 timestamps
npx hyperframes inspect           # visual layout audit — overflow, off-frame elements, occluded text
npx hyperframes preview           # live browser preview
npx hyperframes render --quality draft --output draft.mp4    # fast iteration
npx hyperframes render --quality high --output final.mp4     # final delivery
```

`hyperframes validate` 会检测每个文本元素背后的背景像素，并对对比度低于 4.5:1（大字体则为 3:1）的情况发出警告。`hyperframes inspect` 则是用于布局检查的工具——它会在不同时间点渲染页面，从而发现静态检查无法识别的问题（例如仅在 4.5 秒时标题才超出安全区域、当标题为最长版本时卡片内容溢出、某个元素被过渡效果遮盖等）。尤其建议在包含对话框、卡片、字幕或密集排版的组合场景中使用 `inspect` 功能。

### 8. 网站转视频（若用户提供网址）

请按照 [references/website-to-video.md](references/website-to-video.md) 中的七步流程将页面转换为视频：捕获 → DESIGN.md → SCRIPT.md → 分镜脚本 → 组合设计 → 渲染 → 输出。

## 常见问题

- **`HeadlessExperimental.beginFrame' wasn't found`** —— Chromium 147 及更高版本已移除该协议。请确保使用 `hyperframes@>=0.4.2` 版本（该版本会自动检测并回退到截图模式）。应急方案：设置 `export PRODUCER_FORCE_SCREENSHOT=true`。详情可参阅 [hyperframes#294](https://github.com/heygen-com/hyperframes/issues/294) 以及 [references/troubleshooting.md]。
- **使用系统自带的 Chrome（而非 `chrome-headless-shell`）** —— 渲染过程可能会卡住 120 秒后超时。请运行 `npx puppeteer browsers install chrome-headless-shell`（setup.sh 脚本已包含此操作）。`hyperframes doctor` 命令可显示将会使用的二进制文件。
- **在任何地方使用 `repeat: -1`** —— 会导致捕获引擎失效。务必设置一个有限的重复次数。
- **对后续加载的剪辑元素使用 `gsap.set()`** —— 页面加载时该元素还不存在。应在时间轴上、且在剪辑元素的 `data-start` 属性指定的时间点或之后，使用 `tl.set(selector, vars, timePosition)` 方法进行操作。
- **在内容文本中使用 `<br>`** —— 强制换行无法知晓实际渲染后的字体宽度，因此会导致自然换行后再通过 `<br>` 进行二次换行。建议使用 `max-width` 属性来实现文本自动换行。例外情况：那些刻意将每个单词单独占一行的短显示标题。
- **对 `visibility` 或 `display` 属性进行动画处理** —— GSAP 无法对这些属性进行过渡动画。应使用 `autoAlpha` 属性（可同时控制可见性和透明度）。
- **手动调用 `video.play()` 或 `audio.play()`** —— 播放功能由框架统一管理，切勿自行调用这些方法。
- **异步构建时间轴** —— 页面加载后，捕获引擎会同步读取 `window.__timelines` 数据。切勿将时间轴的构建操作放在 `async`、`setTimeout` 或 Promise 中执行。
- **将独立的 `index.html` 文件包裹在 `<template>` 中** —— 这样做会隐藏浏览器中的所有内容。只有通过 `data-composition-src` 加载的**子组合**才允许使用 `<template>`。
- **用视频替代音频** —— 应始终使用已静音的 `<video>` 元素，并搭配独立的 `<audio>` 元素。

## 验证步骤

在渲染前后需进行以下验证：

1. **通过检查、验证和布局检测**：执行命令 `npx hyperframes lint --strict && npx hyperframes validate && npx hyperframes inspect`（lint 用于检测结构问题，validate 用于检测对比度问题，inspect 用于检测视觉布局及内容溢出问题——如出现警告，请参阅 troubleshooting.md）。
2. **动画协调性检查** —— 对于新创建的组合或经过重大动画修改的场景，需运行动画映射检查。执行 `npx hyperframes init` 可将相关技能脚本复制到项目中，此时路径为项目本地路径：
   ```bash
   node skills/hyperframes/scripts/animation-map.mjs <composition-dir> \
     --out <composition-dir>/.hyperframes/anim-map
   ```
该工具会输出一个包含各类信息的 `animation-map.json` 文件，其中包括每个动画过渡的摘要、ASCII格式的甘特图时间轴、元素错开检测结果、无动画区域信息（持续时间超过1秒的区域）、元素生命周期数据，以及各类状态标记（如 `offscreen`、`collision`、`invisible`、`paced-fast` <0.2秒、`paced-slow` >2秒）。需逐一查看这些摘要与标记，对存在的问题进行修复或给出合理解释；若仅为细微调整，则可直接跳过。

3. **文件存在且大小非零：** 执行命令 `ls -lh final.mp4`。
4. **文件时长与 `data-duration` 匹配：** 执行命令 `ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4`。
5. **视觉检查：** 提取中间帧进行查看，命令为 `ffmpeg -i final.mp4 -ss 00:00:05 -vframes 1 preview.png`。
6. **确认是否存在预期音频：** 执行命令 `ffprobe -v error -show_streams -select_streams a -of default=nw=1:nk=1 final.mp4 | head -1`。

如果 `hyperframes render` 命令执行失败，请运行 `npx hyperframes doctor` 并在提交问题报告时附上该命令的输出结果。

## 参考文档

- [composition.md](references/composition.md) — 数据属性、时间轴规范、不可违反的规则、排版与资源相关规则
- [cli.md](references/cli.md) — 所有CLI命令说明（包括init、capture、lint、validate、inspect、preview、render、transcribe、tts、doctor、browser、info、upgrade、benchmark等）
- [gsap.md](references/gsap.md) — HyperFrames所使用的GSAP核心API（包括动画过渡、缓动函数、错开效果、时间轴控制、matchMedia功能等）
- [features.md](references/features.md) — 字幕功能、文本转语音、音频响应式处理、标记高亮显示、过渡效果（按需加载）
- [website-to-video.md](references/website-to-video.md) — 从网页到视频的7步制作流程
- [troubleshooting.md](references/troubleshooting.md) — OpenClaw相关问题解决方案、环境变量设置、常见的渲染错误处理方法
