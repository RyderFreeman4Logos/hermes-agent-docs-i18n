# 工具矩阵——各角色的技能与工具集

该矩阵将各类角色原型与其应`始终加载`的Hermes技能以及所需工具集对应起来。仅列出公共hermes-agent仓库中已包含的技能（位于`skills/`或`optional-skills/`目录下）。外部API和CLI通过终端工具集调用，因此不会出现在`always_load`列表中。

## 与视频制作相关的Hermes技能

### 视觉/渲染技能（`hermes-agent/skills/creative/`）

| Skill | What it does | Best fit for |
|-------|--------------|--------------|
| `ascii-video` | Production pipeline for ASCII art video — generative, audio-reactive, video-to-ASCII | Renderer for ASCII / terminal / retro pixel content; cinematographer for ASCII projects |
| `ascii-art` | Static ASCII art generation | Concept artist for ASCII style frames; secondary tool for ASCII renderer |
| `manim-video` | Manim CE animations — math, algorithms, 3Blue1Brown-style explainers | Renderer for math, algorithm walkthroughs, technical concept explainers |
| `p5js` | p5.js sketches — generative art, shaders, interactive, 3D | Renderer for generative art, particle systems, organic motion, web-canvas content |
| `comfyui` | Generate images, video, audio with ComfyUI workflows (image-to-image, image-to-video, etc.) | image-generator, image-to-video-generator, or general renderer for AI-generated content |
| `touchdesigner-mcp` | Control a running TouchDesigner instance — real-time visuals, audio-reactive installation art, VJ | Renderer for real-time/audio-reactive content; installation art; live performance |
| `pixel-art` | Pixel art with era palettes (NES, Game Boy, PICO-8) | Renderer for retro game aesthetic; concept artist for pixel-style frames |
| `baoyu-comic` | Knowledge-comic generation (educational, biography, tutorial) | Renderer for comic-style narrative; explainer in panel form |
| `baoyu-infographic` | Infographic generation | Renderer for data-driven explainer scenes |
| `meme-generation` *(optional)* | Generate meme images by overlaying text on templates | Generator for satirical/social content; meme-style stills |

### 设计/预生产技能（`hermes-agent/skills/creative/`）

| 技能 | 功能说明 | 最适合的应用场景 |
|-------|----------|------------------|
| `claude-design` | 设计单次使用的 HTML 文件（落地页、演示文稿、原型等） | 用于制作产品视频风格画面的概念设计师；处理界面复杂的素材的故事板绘制者 |
| `design-md` | 设计 Markdown 文档 | 负责记录视觉规范的场景概念设计师 |
| `popular-web-designs` | 提供热门网页设计的参考模板 | 需要匹配特定 UI 风格的概念设计师或摄影师 |
| `sketch` | 生成简易的 HTML 原型（2-3 种设计版本以供对比） | 探索设计方向的概念设计师；规划 UI 流程的故事板绘制者 |
| `excalidraw` | 生成类似 Excalidraw 风格的手绘图表 | 用于制作故事板；需要草图风格画面的概念设计师 |
| `architecture-diagram` | 绘制软件架构图 | 用于技术类内容的故事板绘制者；讲解系统功能的场景设计者 |
| `concept-diagrams` *(可选)* | 平面化、极简风格的 SVG 图表（适用于教育类可视化内容，如物理、化学、数学、解剖学等主题） | 需要简洁教育类图表来辅助讲解的场景的渲染师或故事板绘制者 |
| `pretext` | 撰写数学/科学类内容 | 负责撰写技术讲解类内容的作者或摄影师 |
| `creative-ideation` | 在约束条件下进行项目创意构思 | 面对开放性需求且需要明确框架的导演或摄影师 |
| `humanizer` | 去除文本中的 AI 特有表达，增添真实人文气息 | 用于后期处理文本的作者或文案撰写人，以避免脚本和语音稿中出现 AI 特有的表述风格 |
### 音频/媒体技能（`hermes-agent/skills/creative/` + `skills/media/`）

| 技能名称 | 功能描述 | 最适合的应用场景 |
|---------|----------|------------------|
| `songwriting-and-ai-music` | 歌曲创作技巧 + Suno提示词模板 | 通过Suno委托制作音乐时的音乐监制 |
| `heartmula` | 开源音乐生成工具（Apache-2.0许可，类似Suno） | 不依赖外部API、需定制音乐的音乐监制 |
| `songsee` | 提供音频文件的频谱图以及梅尔频谱/色度图/MFCC参数 | 音乐监制分析曲目；音效设计师根据节奏设计音效；混音师可视化混音效果 |
| `spotify` | 控制Spotify功能——播放、搜索、创建播放列表、管理歌单 | 音乐监制查找现有曲目；进行参考资料研究 |
| `youtube-content` | 获取视频字幕，并将其转换为章节结构/摘要/文章内容 | 纪录片剪辑、内容改编、制作说明类内容时的资料收集 |
| `gif-search` | 搜索现有GIF图片 | 编辑人员/概念设计师寻找参考素材 |
| `gifs` | GIF处理工具 | 负责制作GIF成品的后期处理师 |

### 看板系统架构

看板插件会自动将基础的流程编排指导嵌入到每个工作节点的系统提示词中——包括`kanban_create`的分支处理模式、任务承接/移交的生命周期，以及针对流程协调者的“拆分任务而非直接执行”原则。无需额外加载任何看板技能，看板任务的处理人员始终能获得这些指导。

## 外部工具（通过终端工具集调用）

这些并非 Hermes 技能，而是配置文件所调用的外部 CLI 工具或 API。它们不会出现在 `always_load` 列表中，而是由对应角色直接执行终端命令来调用。

| 工具 | 功能 | 使用该工具的配置文件 |
|------|------|----------------------|
| `ffmpeg` | 视频/音频编码、拼接、复用 | renderer、editor、audio-mixer、masterer |
| `ffprobe` | 检查媒体文件信息 | 所有涉及媒体处理的配置文件 |
| Whisper（CLI 或 API） | 语音转文字以生成字幕 | captioner |
| 文本转图像 API（FAL / Replicate / OpenAI / Midjourney） | 生成静态图片 | image-generator（作为本地 `comfyui` 的替代方案） |
| 图像转视频 API（Runway / Kling / Luma / Pika） | 为静态图片添加动画效果 | image-to-video-generator |
| 文本转语音 API（ElevenLabs / OpenAI TTS 等） | 生成旁白音频 | voice-talent |
| Suno API 或网页版 | 曲目编排（与 `songwriting-and-ai-music` 配合使用） | music-supervisor |
| Remotion CLI（`npx remotion render`） | 基于 React 的动态图形制作 | renderer-motion-graphics |
| Manim CE（`manim`） | 数学动画渲染（由 `manim-video` 技能的脚本驱动） | renderer-manim |
| Blender（`blender -b`） | 3D 渲染（无界面脚本模式） | renderer-3d |

## Hermes 内置的媒体审阅工具

这些是 Hermes 自带的工具——并非通过终端调用，而是通过其专用的工具集来使用。只需将相应的工具集添加到配置文件中，即可在特定配置文件下启用这些工具。

| 工具 | 工具集 | 功能说明 | 使用该工具的角色 |
|------|---------|----------|----------------|
| `video_analyze` | `video`（可选——需通过 `hermes tools enable video` 启用） | 原生视频理解功能——无需提取帧，即可将完整视频片段发送至多模态大语言模型（通过 OpenRouter 连接 Gemini）进行分析。支持 mp4、webm、mov、avi、mkv 格式，文件大小上限为 50 MB。模型优先使用 `AUXILIARY_VIDEO_MODEL` 环境变量指定的模型，若未指定则回退至 `AUXILIARY_VISION_MODEL`。 | 审核员、摄影师、剪辑师 |
| `vision_analyze` | `vision`（核心功能——默认启用） | 图像/帧分析功能——可用于查看静态图片、缩略图及导出的帧。所有角色无需额外配置即可直接使用该功能。 | 审核员、摄影师、概念艺术家 |

## 各角色的标准工具集配置

### 导演

```yaml
toolsets:
  - kanban
  - terminal
  - file
skills:
  always_load: []
```

主管可通过常规方式访问终端，但 SOUL.md 规则禁止其执行任何操作。审计日志会记录所有违规行为。

```yaml
toolsets:
  - kanban
  - file
skills:
  always_load:
    - humanizer            # post-process scripts to strip AI-tells
```

无需终端——创作者根本不需要它。

### 概念艺术家角色

请完整翻译输入内容，切勿提前终止。

```yaml
toolsets:
  - kanban
  - terminal
  - file
skills:
  always_load:
    # plus one or more (style-dependent):
    # - claude-design       (UI / web product video)
    # - sketch              (quick mockup variants)
    # - excalidraw          (hand-drawn frames)
    # - ascii-art           (ASCII style frames)
    # - pixel-art           (retro/game aesthetic)
    # - popular-web-designs (matching known web aesthetic)
    # - design-md           (text-based design docs)
```

### 分镜编辑器

```yaml
toolsets:
  - kanban
  - file
skills:
  always_load:
    # one of:
    # - excalidraw              (sketch storyboards)
    # - architecture-diagram    (technical/system content)
    # - concept-diagrams        (educational / scientific content)
```

### 摄影指导

```yaml
toolsets:
  - kanban
  - terminal
  - file
  - video               # video_analyze — review full clips natively
  - vision              # vision_analyze — review stills / exported frames
skills:
  always_load:
    # the visual skill that matches the project, e.g.:
    # - ascii-video            (ASCII projects)
    # - manim-video            (math/explainer)
    # - p5js                   (generative)
    # - comfyui                (AI-generated visuals)
    # - touchdesigner-mcp      (real-time/installation)
```

### 渲染器（专用版本）

```yaml
toolsets:
  - kanban
  - terminal
  - file
skills:
  always_load:
    # ONE skill per renderer variant (or empty for external-API renderers):
    # - ascii-video               (renderer-ascii)
    # - manim-video               (renderer-manim)
    # - p5js                      (renderer-p5js)
    # - comfyui                   (renderer-comfyui — img/video AI gen)
    # - touchdesigner-mcp         (renderer-touchdesigner)
    # - pixel-art                 (renderer-pixel)
    # - baoyu-comic               (renderer-comic)
    # - meme-generation           (renderer-meme)
```

对于基于外部 API 的渲染工具（如使用 Runway 的图像转视频生成器、使用 ElevenLabs 的语音合成服务，以及使用 Remotion 的动态图形渲染工具），`always_load` 参数的值为空——这类工具的操作完全由 API 驱动，只需 API 密钥加上终端命令即可（此时仍会自动注入看板相关指引）。

而对于多技能渲染配置（这种情况较为少见，通常为每种技能单独设置一个版本会更清晰），可在每次调用 `kanban_create` 时使用 `--skill <name>` 参数来指定该特定任务应加载哪种技能。

```yaml
toolsets:
  - kanban
  - terminal
  - file
skills:
  always_load:
    # for image-generator that drives ComfyUI locally:
    # - comfyui
env_required:
  # populate based on the chosen API:
  - FAL_KEY                 # or REPLICATE_API_TOKEN, OPENAI_API_KEY for image-gen
  - RUNWAY_API_KEY          # or KLING_API_KEY, LUMA_API_KEY for image-to-video
  - ELEVENLABS_API_KEY      # or OPENAI_API_KEY for TTS
```

如果用户的系统中已本地安装了ComfyUI，那么`comfyui`技能便可以完全替代外部图像生成API（成本更低、控制力更强，同时还支持自定义的图像转视频工作流）。

### music-supervisor

请完整翻译输入内容，切勿提前终止。

```yaml
toolsets:
  - kanban
  - terminal
  - file
skills:
  always_load:
    - songsee                         # spectrograms / audio analysis
    # plus (depending on what the project needs):
    # - songwriting-and-ai-music      (commissioning Suno tracks)
    # - heartmula                     (commissioning open-source local generation)
    # - spotify                       (sourcing existing tracks)
```

### 编辑器 / 音频混音器 / 字幕生成器 / 整合处理工具

```yaml
toolsets:
  - kanban
  - terminal
  - file
  - video              # video_analyze — editor reviews assembled cuts natively
  - vision             # vision_analyze — spot-check frames
skills:
  always_load: []
```

这些功能大多由ffmpeg驱动，无需特殊技能（每个任务处理节点都会自动注入看板操作指南）。对于字幕生成器，需在SOUL.md文件中添加Whisper调用示例。

### 审核员/品牌合规专员

请完整翻译输入内容，不得提前终止。

```yaml
toolsets:
  - kanban
  - terminal           # for media inspection (ffprobe, etc.)
  - file
  - video              # video_analyze — review full clips natively
  - vision             # vision_analyze — review stills / exported frames
skills:
  always_load: []
```

## API密钥要求

在项目初始化阶段需注意这些要求。初始化脚本应在启动相关功能之前，检查`${HERMES_HOME:-~/.hermes}/.env`文件（或macOS钥匙串）中是否包含所有必需的密钥。

| 服务名称 | 环境变量名 | 使用该密钥的功能 |
|---------|---------|------------------|
| ElevenLabs | `ELEVENLABS_API_KEY` | 语音生成功能 |
| OpenAI | `OPENAI_API_KEY` | 图像生成器（DALL-E）、语音生成功能（文本转语音） |
| OpenRouter | `OPENROUTER_API_KEY` | 审核员、摄影师、剪辑师相关功能（`video_analyze`功能会通过`AUXILIARY_VIDEO_MODEL`路由至OpenRouter） |
| FAL | `FAL_KEY` | 图像生成器（FAL流程模型） |
| Replicate | `REPLICATE_API_TOKEN` | 图像生成器（备用服务提供商） |
| Runway | `RUNWAY_API_KEY` | 图像转视频生成功能 |
| Kling | `KLING_API_KEY` | 图像转视频生成功能（备用选项） |
| Luma | `LUMA_API_KEY` | 图像转视频生成功能（备用选项） |
| Suno | `SUNO_API_KEY` | 音乐管理功能（与`songwriting-and-ai-music`技能搭配使用） |
| Spotify | `SPOTIFY_CLIENT_ID` + `SPOTIFY_CLIENT_SECRET` | 音乐管理功能（与`spotify`技能搭配使用） |
| Anthropic | `ANTHROPIC_API_KEY` | 所有Hermes账号（Claude模型） |

如果缺少某项密钥，系统会提示用户补充。密钥的存储优先级为：macOS钥匙串 → `${HERMES_HOME:-~/.hermes}/.env`文件 → 环境变量。

## 技能版本锁定

如需使用特定版本的技能，可通过任务级别的`--skill <名称>=<版本>`参数来指定。默认情况下将使用已安装的最新版本。

## 向矩阵中添加新技能

当有新的 Hermes 公开视频技能发布时：

1. 在本文件顶部的对应表格中添加一行记录；
2. 如果该技能需要专门的渲染器版本，则需在 `role-archetypes.md` 文件中进行补充；
3. 同时更新 `examples.md` 中与该技能相关的各风格示例。
