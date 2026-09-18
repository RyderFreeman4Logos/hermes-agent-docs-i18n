---
title: "Hyperframes — Render MP4/WebM videos from HTML compositions"
sidebar_label: "Hyperframes"
description: "Render MP4/WebM videos from HTML compositions"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Hyperframes

基于 HTML 组件渲染 MP4/WebM 视频。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/creative/hyperframes` 安装 |
| 路径 | `optional-skills/creative\hyperframes` |
| 版本 | `1.0.0` |
| 开发者 | heygen-com |
| 许可协议 | Apache-2.0 |
| 支持平台 | linux、macos、windows |
| 标签 | `creative`、`video`、`animation`、`html`、`gsap`、`motion-graphics` |
| 相关技能 | [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video)、[`meme-generation`](/docs/user-guide/skills/optional/creative/creative-meme-generation) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能运行时，智能体所看到的指令即为此内容。
:::

# HyperFrames

HTML 是视频内容的真实来源。一个组件实际上是一个包含用于控制时序的 `data-*` 属性、用于实现动画效果的 GSAP 时间轴以及用于设定外观样式的 CSS 的 HTML 文件。HyperFrames 引擎会逐帧捕获页面内容，并使用 FFmpeg 将其编码为 MP4/WebM 格式。

**与 `manim-video` 的区别：** 对于数学或几何演示内容（如方程式、3B1B 风格的图表），建议使用 `manim-video`；而对于动态图形、带字幕的出镜讲解、产品展示、社交平台叠加效果、着色器过渡效果，以及任何基于真实视频/音频素材的内容，则应使用 `hyperframes`。

## 适用场景

- 用户需要将文本、脚本或网页内容转换为视频
- 动态标题卡、底部字幕或排版式开场动画
- 带字幕的旁白视频（文本转语音与字幕同步至波形）
- 随音频变化的视觉效果（节拍同步、频谱条、脉冲光效）
- 场景之间的过渡效果（渐变淡入淡出、擦除效果、着色器变形、白色闪过）
- 社交媒体风格叠加元素（Instagram/TikTok/YouTube风格）
- 网页转视频流程（捕获网址并生成宣传视频）
- 任何需要以确定性方式渲染为视频文件的HTML/CSS/JS动画

**不推荐**将此技能用于以下场景：
- 纯数学公式动画（→ `manim-video`）
- 图像生成或表情包制作（→ `meme-generation`、图像模型）
- 实时视频会议或流媒体播放

## 快速参考

```bash
npx hyperframes init my-video               # scaffold a project
cd my-video
npx hyperframes lint                        # validate before preview/render
npx hyperframes preview                     # live-reload preview (long-lived server, port 3002)
npx hyperframes render --output final.mp4   # render to MP4
npx hyperframes doctor                      # diagnose environment issues
```

`preview` 是一个**长期运行**的 Next.js 服务器，用于保持 Chrome 渲染工作进程处于活跃状态。使用完毕后务必将其停止（详见[清理指南](#cleanup)）——若忽视此操作，闲置的 `chrome-headless-shell` 工作进程将继续存活。在无 GPU 的主机环境（如 WSL、容器及 CI 环境）中，这些进程会通过软件实现的 WebGL（swiftshader）技术无限占用每个 CPU 核心。

渲染参数：`--quality draft|standard|high` · `--fps 24|30|60` · `--format mp4|webm` · `--docker`（确保结果可复现）· `--strict`。

完整的 CLI 参考文档：[references/cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/cli.md)。

## 设置（仅需执行一次）

```bash
bash "$(dirname "$(find ~/.hermes/skills -path '*/hyperframes/SKILL.md' 2>/dev/null | head -1)")/scripts/setup.sh"
```

该脚本的功能如下：
1. 检查是否已安装 Node.js 22 及以上版本以及 FFmpeg（若未安装则输出相应的修复说明）。
2. 全局安装 `hyperframes` CLI（执行命令：`npm install -g hyperframes@>=0.4.2`）。
3. 通过 Puppeteer 预缓存 `chrome-headless-shell`——这是通过 Chrome 的 `HeadlessExperimental.beginFrame` 捕获方式实现最佳渲染效果所必需的步骤。
4. 运行 `npx hyperframes doctor` 并输出检测结果。

如果设置过程中出现故障，请参阅 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/troubleshooting.md) 文档。

## 操作步骤

### 1. 编写 HTML 前进行规划

在开始编写代码之前，需先从宏观层面明确以下内容：
- **内容核心**——故事情节主线、关键节点、情感高潮点
- **结构框架**——画面构图、音轨（视频/音频/叠加层）以及各部分时长
- **视觉风格**——色彩方案、字体选择以及动画风格（爆发式/电影感/流畅型/科技感）
- **核心画面**——针对每个场景，确定所有元素同时最清晰可见的瞬间。这部分内容将作为您首先需要设计的静态布局。

**视觉风格确认机制（强制要求）。** 在编写任何画面构图的 HTML 代码之前，必须先确定视觉风格。严禁使用默认或通用的颜色值（如 `#333`、`#3b82f6` 或 Roboto 字体，这些都会表明该步骤已被跳过）。请按以下顺序进行确认：

1. **项目根目录下存在 `DESIGN.md` 文件？** → 直接沿用该文件中规定的颜色、字体、动画规则以及“禁忌事项”要求。
2. **用户已指定风格名称**（例如“Swiss Pulse”、“深色科技风”、“奢侈品牌风”）？→ 生成一份简洁的 `DESIGN.md` 文件，内容包括 `## Style Prompt`、`## Colors`（3-5种带用途说明的十六进制颜色值）、`## Typography`（1-2种字体系列）以及 `## What NOT to Do`（3-5项应避免的设计误区）。
3. **以上情况均不符合？** → 在生成任何 HTML 内容之前，先询问用户三个问题：
   - 氛围风格？（充满活力 / 电影感 / 流畅自然 / 科技感 / 混乱无序 / 温暖舒适）
   - 背景采用浅色还是深色？
   - 是否有指定的品牌颜色、字体或视觉参考？

   根据用户的回答后再生成 `DESIGN.md` 文件。所有设计元素的颜色方案与字体选择都必须有明确的来源，要么来自 `DESIGN.md`，要么遵循用户的具体指示。

### 2. 框架搭建

```bash
npx hyperframes init my-video --non-interactive
```

模板选项包括：`blank`、`warm-grain`、`play-mode`、`swiss-grid`、`vignelli`、`decision-tree`、`kinetic-type`、`product-promo`、`nyt-graph`。若需选择特定模板，可输入 `--example <名称>`；若要为动画添加媒体素材，则可使用 `--video clip.mp4` 或 `--audio track.mp3`。

### 3. 动画前的布局设计

首先编写**标题区域**的静态 HTML+CSS 代码——此时还无需使用 GSAP。`.scene-content` 容器应通过 `display:flex` + `gap` 属性将整个场景填满（`width:100%; height:100%; padding:Npx`）。建议使用内边距将内容向内缩进，而绝不要在内容容器上使用 `position: absolute; top: Npx`，否则当内容高度超过剩余空间时会导致内容溢出。

只有在标题区域的外观符合预期后，才添加 `gsap.from()` 动画以实现从其他状态**过渡到** CSS 定义的位置，以及使用 `gsap.to()` 动画实现从该位置**返回**的动画效果。

有关完整的数据属性结构及布局规则，请参阅 [references/composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/composition.md) 文档。

### 4. 使用 GSAP 进行动画制作

所有动画组合都必须满足以下要求：
- 注册时间轴：`window.__timelines["<composition-id>"] = tl`  
- 暂停启动：`gsap.timeline({ paused: true })` —— 播放由播放器控制  
- 使用有限的重复次数（禁止使用 `repeat: -1`，否则会破坏捕获引擎）。计算方式如下：`repeat: Math.ceil(duration / cycleDuration) - 1`。  
- 确保行为可预测——不得使用 `Math.random()`、`Date.now()` 或基于实际时间的逻辑。如需伪随机数，可使用带种子的伪随机数生成器。  
- 同步构建时间轴——在创建时间轴的过程中不得使用 `async`/`await`、`setTimeout` 或 Promise。  

有关 GSAP 核心 API（如动画过渡、缓动函数、错开效果及时间轴功能）的详细信息，请参阅 [references/gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/gsap.md)。  

### 5. 场景之间的切换  

多场景组合必须包含场景切换效果。相关规则如下：  
1. **场景之间务必使用切换效果**——禁止直接跳转。  
2. **每个场景元素都必须添加进入动画**（使用 `gsap.from(...)`）。  
3. **除最后一个场景外，不得使用离开动画**——因为切换本身即视为离开效果。  
4. 最后一个场景可以渐隐退出。  

如需安装着色器切换效果（如 `flash-through-white`、`liquid-wipe` 等），可使用命令 `npx hyperframes add <transition-name>`。完整效果列表可通过 `npx hyperframes add --list` 查看。  

### 6. 音频、字幕、文本转语音、音频响应式效果及高亮显示  

- **音频**：必须使用独立的 `<audio>` 元素（视频则需设置为 `muted playsinline`）。
- **文本转语音：** 使用命令 `npx hyperframes tts "脚本文本" --voice af_nova --output narration.wav` 即可实现转换。若需查看可用语音列表，可使用 `--list` 参数。语音 ID 的首字母代表对应语言（`a`/`b` 表示英语，`e` 表示西班牙语，`f` 表示法语，`j` 表示日语，`z` 表示普通话等）——命令行工具会自动识别音素化引擎的地域设置，仅需通过 `--lang` 参数进行手动覆盖。若需处理非英语语音，系统需预先安装 `espeak-ng` 工具。
- **字幕生成：** 运行命令 `npx hyperframes transcribe narration.wav` 即可获得单词级的转录文本。可根据文本风格选择合适的字幕风格（如激昂型、商务型、教程型、叙事型或社交媒体风格——详情请参阅 `references/features.md` 文件中的表格）。**语言规则：** 除非确认音频为英语，否则切勿使用 `.en` 类型的低语音效模型——这类模型会尝试翻译非英语音频而非进行转录。每个字幕组在动画过渡结束后，都必须通过 `tl.set(el, { opacity: 0, visibility: "hidden" }, group.end)` 显式设置其不可见，否则这些字幕内容会渗入后续的字幕组中。
- **音频驱动的视觉效果：** 首先需提取音频的各频段（低音/中音/高音），然后通过 `tl.call(draw, [], f / fps)` 与 `for` 循环结合，在时间轴上逐帧生成视觉效果——单一的长时间过渡动画无法对音频变化做出响应。可将低音映射为 `scale`（脉冲效果），高音映射为 `textShadow`/`boxShadow`（发光效果），整体音量则映射为 `opacity`/`y`/`backgroundColor` 等属性。应避免使用千篇一律的均衡器条式视觉元素，而应让内容主导视觉呈现，音频决定其动态变化。
- **标记式高亮效果**：可通过高亮、圈出、爆裂、涂鸦、草图等效果来强调文本，这些功能均基于确定的 CSS+GSAP 实现——详情请参阅 `references/features.md#marker-highlighting`。该方案支持全文搜索，且不使用带有动画效果的 SVG 过滤器。
- **场景切换**：所有多场景组合都必须使用过渡效果（禁止直接跳转）。您可以选择 CSS 原生过渡效果（如推入式滑动、模糊渐变、缩放展示、错落块状切换等），或通过 `npx hyperframes add` 引入着色器过渡效果（如“白色闪现过渡”、“液体擦拭过渡”、“交叉变形过渡”、“色彩分割过渡”等）。相关效果与氛围设置详见 `references/features.md#transitions`。同一组合中不得同时使用 CSS 过渡与着色器过渡效果。

### 7. 代码检查、验证、检测、预览与渲染

```bash
npx hyperframes lint              # catches missing data-composition-id, overlapping tracks, unregistered timelines
npx hyperframes validate          # WCAG contrast audit at 5 timestamps
npx hyperframes inspect           # visual layout audit — overflow, off-frame elements, occluded text
npx hyperframes preview           # live browser preview
npx hyperframes render --quality draft --output draft.mp4    # fast iteration
npx hyperframes render --quality high --output final.mp4     # final delivery
```

`hyperframes validate` 会采样每个文本元素背后的背景像素，并对对比度低于 4.5:1（大字体则为 3:1）的情况发出警告。`hyperframes inspect` 则是用于布局分析的工具——它会在不同时间点加载页面，从而检测出静态检查工具无法发现的缺陷（例如在 4.5 秒时标题才会超出安全区域、当标题为最长版本时卡片内容会溢出、某个元素最终会出现在过渡特效之后等）。对于包含对话框、卡片、字幕或密集排版的页面，尤其建议使用 `inspect` 工具进行检测。

### 8. 网站转视频（若用户提供 URL）

请按照 [references/website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/website-to-video.md) 中描述的 7 步视频录制流程操作：捕获 → DESIGN.md → SCRIPT.md → 分镜脚本 → 组合设计 → 渲染 → 输出。

## 清理工作

`render` 操作为一次性执行（完成后工作进程会立即退出）。而 `preview` 则并非如此——它会持续运行一个后台的 Next.js 服务器，使 Chrome 工作进程保持运行状态，直到你手动停止它。切勿让预览进程长期运行：在无 GPU 的主机上，每个闲置的工作进程都会占用一个 CPU 核心，若预览窗口长时间打开，将会累积多个这样的进程。

当用户完成查看后（或在开始新的预览之前），请及时停止预览进程。

```bash
pkill -f "hyperframes.*preview"     # the Studio server (frees port 3002)
pkill -f chrome-headless-shell      # its render workers; only safe if nothing else uses them
```

如果不确定其他工具是否使用了 `chrome-headless-shell`，可先执行命令 `pgrep -af chrome-headless-shell` 进行查看。处理因进程卡住导致大量空闲工作线程占用 CPU 的情况也可采用相同方法——详情请参阅 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/troubleshooting.md#runaway-cpu-from-leftover-preview-workers)。

## 常见问题

- **让 `preview` 一直运行**——它是一个长期运行的服务器，用于管理 Chrome 工作线程；在 WSL、容器或 CI 环境中，这些空闲工作线程会各自占用一个 CPU 核心（通过软件 WebGL 实现功能）。任务完成后请务必停止该服务——详情参见 [Cleanup](#cleanup) 部分。

- **出现 “`HeadlessExperimental.beginFrame' wasn't found” 错误**——Chromium 147 及更高版本已移除该协议。请确保使用的是 `hyperframes@>=0.4.2` 版本（该版本会自动检测并回退到截图模式）。作为临时解决方案，可设置 `export PRODUCER_FORCE_SCREENSHOT=true`。更多信息请参阅 [hyperframes#294](https://github.com/heygen-com/hyperframes/issues/294) 以及 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/troubleshooting.md)。

- **使用系统自带的 Chrome（而非 `chrome-headless-shell`）**——会导致渲染过程卡住约 120 秒后超时。请运行命令 `npx puppeteer browsers install chrome-headless-shell`（setup.sh 脚本已内置此操作）。执行 `hyperframes doctor` 命令即可查看系统将使用哪个版本的 Chrome。

- **在任何地方出现 `repeat: -1` 参数**——会破坏捕获引擎的正常运行。请始终设置一个有限的重复次数。
- **针对后续加载的剪辑元素使用 `gsap.set()`**——该元素在页面加载时并不存在。应在时间轴中，在该剪辑的 `data-start` 属性所在位置或之后，使用 `tl.set(selector, vars, timePosition)` 方法。
- **内容文本中使用 `<br>`**——强制换行无法感知实际渲染后的字体宽度，因此建议采用自然换行后再添加 `<br>` 实现双重换行。可通过设置 `max-width` 来让文本自动换行。例外情况：那些刻意将每个单词单独占一行的简短显示标题。
- **为 `visibility` 或 `display` 属性制作动画**——GSAP 无法对这些属性进行过渡动画。应使用 `autoAlpha` 方法（可同时控制可见性和透明度）。
- **调用 `video.play()` 或 `audio.play()`**——播放功能由框架统一管理，切勿自行调用这些方法。
- **异步构建时间轴**——页面加载后，捕获引擎会同步读取 `window.__timelines` 数据。切勿将时间轴的构建过程封装在 `async`、`setTimeout` 或 Promise 中。
- **被 `<template>` 包裹的独立 `index.html` 文件**——会隐藏浏览器中的所有内容。仅有通过 `data-composition-src` 加载的**子合成内容**才会使用 `<template>`。
- **用视频替代音频**——应始终使用静音的 `<video>` 元素，并搭配独立的 `<audio>` 元素。

## 验证

渲染前后：

1. **通过代码检查、验证与布局检测：** 执行 `npx hyperframes lint --strict && npx hyperframes validate && npx hyperframes inspect`（代码检查可发现结构问题，验证功能可检测对比度问题，布局检测则能找出视觉排版或内容溢出等问题——如出现警告，请参阅 troubleshooting.md 文档）。
2. **动画编排** —— 对于全新的合成内容或较大的动画改动，需运行动画映射工具。执行 `npx hyperframes init` 可将相关技能脚本复制到项目中，因此其路径为项目本地路径：
   ```bash
   node skills/hyperframes/scripts/animation-map.mjs <composition-dir> \
     --out <composition-dir>/.hyperframes/anim-map
   ```
该功能会输出一个包含以下信息的单一 `animation-map.json` 文件：每个过渡过程的概要信息、ASCII格式的甘特图时间轴、元素错开检测结果、无动画区域（持续时间超过1秒），以及各元素的生命周期状态和标记（如 `offscreen`、`collision`、`invisible`、动画速度过快的 `<0.2s`、动画速度过慢的 `>2s` 等）。需逐一查看这些概要与标记，对存在的问题进行修复或给出合理解释；若仅为微小调整，则可直接跳过。

3. **文件存在且大小非零：** 执行命令 `ls -lh final.mp4`。
4. **文件时长与 `data-duration` 匹配：** 执行命令 `ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4`。
5. **视觉检查：** 提取动画中间阶段的帧：执行命令 `ffmpeg -i final.mp4 -ss 00:00:05 -vframes 1 preview.png`。
6. **确认是否存在预期音频：** 执行命令 `ffprobe -v error -show_streams -select_streams a -of default=nw=1:nk=1 final.mp4 | head -1`。

如果 `hyperframes render` 命令执行失败，请运行 `npx hyperframes doctor` 并在报告问题时附上该命令的输出结果。

## 参考资料

- [composition.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/composition.md) — 数据属性、时间轴规范、不可违背的规则以及排版与资源相关规则  
- [cli.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/cli.md) — 所有 CLI 命令（init、capture、lint、validate、inspect、preview、render、transcribe、tts、doctor、browser、info、upgrade、benchmark）  
- [gsap.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/gsap.md) — 用于 HyperFrames 的 GSAP 核心 API（动画过渡、缓动函数、错开动画、时间轴控制以及 matchMedia 功能）  
- [features.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/features.md) — 字幕功能、文本转语音、音频响应式处理、标记高亮显示以及过渡效果（按需加载）  
- [website-to-video.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/website-to-video.md) — 从网页到视频的 7 步制作流程  
- [troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\hyperframes/references/troubleshooting.md) — OpenClaw 相关问题解决方案、环境变量设置以及常见的渲染错误处理
