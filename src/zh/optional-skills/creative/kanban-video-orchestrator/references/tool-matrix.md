# 工具矩阵——各角色的技能与工具集

该表格将各类角色原型与它们应当`始终加载`的Hermes技能以及所需工具集对应起来。仅列出公共hermes-agent仓库中已有的技能（位于`skills/`或`optional-skills/`目录下）。外部API和CLI通过终端工具集调用，因此不会出现在`always_load`列表中。

## 与视频制作相关的Hermes技能

### 视觉/渲染技能（`hermes-agent/skills/creative/`）

| 技能 | 功能说明 | 最适合的应用场景 |
|------|----------|------------------|
| `ascii-video` | 用于生成ASCII艺术视频的完整流程——具备生成能力、可响应音频信号、支持视频转ASCII格式 | 适用于ASCII/终端/复古像素风格内容的渲染；适合处理ASCII风格项目的摄像师角色 |
| `ascii-art` | 生成静态ASCII艺术 | 适用于设计ASCII风格画面的概念艺术家；也可作为ASCII渲染器的辅助工具 |
| `manim-video` | Manim CE动画引擎——可用于展示数学公式、算法，以及类似3Blue1Brown风格的讲解内容 | 适用于数学公式、算法流程及技术概念的可视化渲染 |
| `p5js` | p5.js编程语言——可创建生成艺术、着色器效果、交互式内容及3D图形 | 适用于生成艺术、粒子系统、自然运动效果以及网页画布内容的渲染 |
| `comfyui` | 通过ComfyUI工作流生成图像、视频和音频（包括图像转图像、图像转视频等功能） | 适用于图像生成、视频生成，或是作为AI生成内容的全能渲染工具 |
| `touchdesigner-mcp` | 控制正在运行的TouchDesigner实例——可用于创建实时视觉效果、响应音频的装置艺术作品及视频混音表演 | 适用于实时/响应音频内容的渲染；装置艺术创作；现场表演场景 |
| `blender-mcp` *(可选)* | 通过MCP控制Blender 4.3及以上版本——支持3D建模、动画制作与渲染 | 适用于3D场景、真实感环境及角色动画的渲染 |
| `pixel-art` | 使用特定时代风格调色板（如NES、Game Boy、PICO-8风格）创作像素艺术 | 适用于打造复古游戏风格的视觉效果；适合设计像素风格画面的概念艺术家 |
| `baoyu-comic` | 生成知识类漫画（用于教育、传记或教程制作） | 适用于以漫画形式呈现叙事内容；适合制作分镜式讲解材料 |
| `baoyu-infographic` | 生成信息图 | 适用于制作数据驱动的讲解型视觉内容 |
| `meme-generation` *(可选)* | 通过在模板上叠加文字来生成迷因图片 | 适用于创作讽刺或社交类内容；适合生成迷因风格静态图片 |

### 设计/前期制作技能（`hermes-agent/skills/creative/`）

| 技能 | 功能说明 | 最适合的应用场景 |
|------|----------|------------------|
| `claude-design` | 设计单次使用的HTML格式文档（如落地页、演示文稿、原型界面） | 适用于为产品视频设计风格画面；适合为UI元素密集的内容制作分镜 |
| `design-md` | 设计Markdown格式文档 | 适用于记录视觉设计规范的概念艺术家 |
| `popular-web-designs` | 提供流行网页设计的参考模板 | 适用于概念艺术家；在需要匹配特定UI风格时，也可作为摄像师辅助工具 |
| `sketch` | 快速生成HTML格式的简易原型（提供2-3种设计方案供对比） | 适用于探索不同设计方向的概念艺术家；适合为UI流程制作分镜 |
| `excalidraw` | 生成类似Excalidraw风格的手绘图表 | 适用于制作分镜；适合为草图风格画面设计的概念艺术家 |
| `architecture-diagram` | 绘制软件架构图 | 适用于为技术类内容制作分镜；适合用于解释系统结构的场景 |
| `concept-diagrams` *(可选)* | 生成简洁的扁平化SVG图表（适用于数学、物理、化学、解剖学等领域的教学可视化） | 适用于为需要清晰教育类图表的讲解场景提供渲染或分镜支持 |
| `pretext` | 撰写数学或科学类内容 | 适用于为技术讲解内容撰写文本的作者或摄像师 |
| `creative-ideation` | 在约束条件下进行项目创意构思 | 适用于在任务要求较为宽泛、需要明确框架时的导演或摄像师 |
| `humanizer` | 去除文本中的AI特征，增添真实语气 | 适用于脚本和旁白文案的后期处理，避免出现明显的AI写作痕迹 |

### 音频/媒体处理技能（`hermes-agent/skills/creative/` + `skills/media/`）

| 技能 | 功能说明 | 最适合的应用场景 |
|------|----------|------------------|
| `songwriting-and-ai-music` | 歌曲创作技巧 + Suno提示词模板 | 适用于通过Suno委托创作音乐的音乐总监角色 |
| `heartmula` | 开源音乐生成工具（遵循Apache-2.0许可，功能类似Suno） | 适用于无需依赖外部API即可定制音乐的音乐总监 |
| `songsee` | 分析音频文件的频谱图以及梅尔频率、色度值和MFCC参数 | 适用于分析音乐素材的音乐总监；也可用于为节奏设计音效的音效设计师；以及用于可视化混音效果的编辑人员 |
| `spotify` | 控制Spotify平台——可播放、搜索、排序歌曲及管理播放列表 | 适用于寻找现有音乐素材的音乐总监；也可用于参考研究 |
| `youtube-content` | 下载视频字幕，并将其转换为章节、摘要或帖子内容 | 适用于纪录片剪辑、内容改编以及为讲解视频做资料收集 |
| `gif-search` | 搜索现有的GIF动图 | 适用于为内容寻找参考素材的编辑人员或概念艺术家 |
| `gifs` | GIF处理工具集 | 适用于制作GIF格式最终输出内容的后期处理人员 |

### 看板任务管理基础设施（`hermes-agent/skills/devops/`）

| 技能 | 功能说明 | 何时加载 |
|------|----------|----------|
| `kanban-orchestrator` | 提供任务分解指南以及针对任务协调角色的防误操作规则 | 仅导演角色需要加载 |
| `kanban-worker` | 提供与看板任务处理相关的常见陷阱、示例及边缘情况处理方案（内容比系统自动注入的指导更详细） | 所有角色均可加载；在处理复杂的多步骤工作流时需加载该技能 |

看板插件会自动将基础的协调指导功能注入到每个任务处理角色的系统提示词中，包括`kanban_create`的任务分发模式、任务接收/交接流程，以及针对任务协调角色的“先分解任务，勿直接执行”规则。而`kanban-orchestrator`和`kanban-worker`则是更深入的指南，在角色需要时才会加载。

## 外部工具（通过终端工具集调用）

这些并非Hermes技能，而是角色会调用的外部CLI或API工具。它们不会出现在`always_load`列表中，而是由角色的终端命令直接调用。

| 工具 | 功能说明 | 使用该工具的角色 |
|------|----------|------------------|
| `ffmpeg` | 视频/音频的编码、拼接与多轨混合处理 | 渲染器、编辑人员、音频混音师、后期处理人员 |
| `ffprobe` | 分析媒体文件信息 | 所有需要处理媒体文件的角色 |
| Whisper（CLI或API） | 将语音转换为文字，用于生成字幕 | 字幕制作人员 |
| 文本转图像API（FAL / Replicate / OpenAI / Midjourney） | 生成静态图片 | 图像生成工具（可作为本地`comfyui`的替代方案） |
| 图像转视频API（Runway / Kling / Luma / Pika） | 为静态图片添加动画效果 | 视频生成工具 |
| 文本转语音API（ElevenLabs / OpenAI TTS等） | 生成旁白音频 | 语音配音人员 |
| Suno API或网页界面 | 创作音乐曲目（需与`songwriting-and-ai-music`技能配合使用） | 音乐总监 |
| Remotion CLI（`npx remotion render`） | 基于React技术的动态图形制作工具 | 动态图形渲染人员 |
| Manim CE（`manim`） | 基于数学公式生成动画效果（由`manim-video`技能的配方驱动） | Manim动画渲染人员 |
| Blender（`blender -b`） | 3D场景渲染（可作为`blender-mcp`的替代方案） | 3D渲染人员 |

## Hermes内置的媒体审阅工具

这些是Hermes自带的工具——无需通过终端调用，而是通过专门的工具集使用。可通过在角色配置中添加相应工具集，为特定角色启用这些功能。

| 工具 | 工具集 | 功能说明 | 使用该工具的角色 |
|------|---------|----------|------------------|
| `video_analyze` | `video`（可选——需通过`hermes tools enable video`命令启用） | 具备原生视频理解能力——可直接将完整视频片段发送给多模态大语言模型（通过OpenRouter连接Gemini模型）进行审阅，无需先提取帧。支持mp4、webm、mov、avi、mkv格式，文件大小上限为50 MB。默认模型为`AUXILIARY_VIDEO_MODEL`环境变量指定的模型，若该模型不可用则回退至`AUXILIARY_VISION_MODEL`模型。 | 审阅人员、摄像师、编辑人员 |
| `vision_analyze` | `vision`（核心功能——默认已启用） | 对图像或帧进行详细分析——可用于审阅静态图片、缩略图及导出的帧文件。所有角色无需额外配置即可使用该功能。 | 审阅人员、摄像师、概念艺术家 |

## 各角色的标准工具集配置

### 导演角色

```yaml
toolsets:
  - kanban
  - terminal
  - file
skills:
  always_load:
    - kanban-orchestrator
```

主管的终端访问方式虽为常规模式，但 SOUL.md 规则禁止其执行相关操作。审计日志会记录所有违规行为。

```yaml
toolsets:
  - kanban
  - file
skills:
  always_load:
    - kanban-worker
    - humanizer            # post-process scripts to strip AI-tells
```

无需终端——创作者根本不需要它。

### 概念艺术家

请完整翻译输入内容，切勿提前终止。

```yaml
toolsets:
  - kanban
  - terminal
  - file
skills:
  always_load:
    - kanban-worker
    # plus one or more (style-dependent):
    # - claude-design       (UI / web product video)
    # - sketch              (quick mockup variants)
    # - excalidraw          (hand-drawn frames)
    # - ascii-art           (ASCII style frames)
    # - pixel-art           (retro/game aesthetic)
    # - popular-web-designs (matching known web aesthetic)
    # - design-md           (text-based design docs)
```

### 故事板绘制工具

```yaml
toolsets:
  - kanban
  - file
skills:
  always_load:
    - kanban-worker
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
    - kanban-worker
    # the visual skill that matches the project, e.g.:
    # - ascii-video            (ASCII projects)
    # - manim-video            (math/explainer)
    # - p5js                   (generative)
    # - comfyui                (AI-generated visuals)
    # - blender-mcp            (3D)
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
    - kanban-worker
    # ONE skill per renderer variant (or empty for external-API renderers):
    # - ascii-video               (renderer-ascii)
    # - manim-video               (renderer-manim)
    # - p5js                      (renderer-p5js)
    # - comfyui                   (renderer-comfyui — img/video AI gen)
    # - touchdesigner-mcp         (renderer-touchdesigner)
    # - blender-mcp               (renderer-3d)
    # - pixel-art                 (renderer-pixel)
    # - baoyu-comic               (renderer-comic)
    # - meme-generation           (renderer-meme)
```

对于基于外部 API 的渲染器（如使用 Runway 的图像转视频生成器、使用 ElevenLabs 的语音合成服务，以及使用 Remotion 的动态图形渲染器），`always_load` 选项仅包含 `kanban-worker` —— 因为这类任务是由 API 驱动的，只需 API 密钥加上终端命令即可完成工作。

而对于多技能渲染器配置（这种情况较为少见——通常为每种技能单独设置一个版本会更清晰），则需在每次调用 `kanban_create` 时使用 `--skill <name>` 参数，从而指定该特定任务应加载哪种技能。

### 图像生成器 / 图像转视频生成器 / 语音合成服务

```yaml
toolsets:
  - kanban
  - terminal
  - file
skills:
  always_load:
    - kanban-worker
    # for image-generator that drives ComfyUI locally:
    # - comfyui
env_required:
  # populate based on the chosen API:
  - FAL_KEY                 # or REPLICATE_API_TOKEN, OPENAI_API_KEY for image-gen
  - RUNWAY_API_KEY          # or KLING_API_KEY, LUMA_API_KEY for image-to-video
  - ELEVENLABS_API_KEY      # or OPENAI_API_KEY for TTS
```

如果用户的环境中已本地安装了ComfyUI，那么`comfyui`技能便可以完全替代外部图像生成API（成本更低、控制力更强，同时还支持自定义的图像转视频工作流）。

### music-supervisor

请完整翻译输入内容，切勿提前终止。

```yaml
toolsets:
  - kanban
  - terminal
  - file
skills:
  always_load:
    - kanban-worker
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
  always_load:
    - kanban-worker
```

这些功能大多由 ffmpeg 驱动，除了需要具备 `kanban-worker` 技能外，并无其他特殊要求。对于字幕生成模块，则需在 SOUL.md 文件中添加调用 Whisper 的相关配置。 

### 审核员 / 品牌合规专员

```yaml
toolsets:
  - kanban
  - terminal           # for media inspection (ffprobe, etc.)
  - file
  - video              # video_analyze — review full clips natively
  - vision             # vision_analyze — review stills / exported frames
skills:
  always_load:
    - kanban-worker
```

## API密钥要求

在项目初始化阶段需妥善管理这些密钥。初始化脚本应在启动相关功能之前，检查`${HERMES_HOME:-~/.hermes}/.env`文件（或macOS钥匙串）中是否包含所有必需的密钥。

| 服务名称 | 环境变量名 | 使用场景 |
|---------|---------|---------|
| ElevenLabs | `ELEVENLABS_API_KEY` | 语音生成功能 |
| OpenAI | `OPENAI_API_KEY` | 图像生成器（DALL-E）、语音生成功能（文本转语音） |
| OpenRouter | `OPENROUTER_API_KEY` | 审核员、摄像师、剪辑师功能（`video_analyze`功能会通过`AUXILIARY_VIDEO_MODEL`路由至OpenRouter） |
| FAL | `FAL_KEY` | 图像生成器（FAL流式模型） |
| Replicate | `REPLICATE_API_TOKEN` | 图像生成器（备用服务提供商） |
| Runway | `RUNWAY_API_KEY` | 图像转视频生成器 |
| Kling | `KLING_API_KEY` | 图像转视频生成器（备用选项） |
| Luma | `LUMA_API_KEY` | 图像转视频生成器（备用选项） |
| Suno | `SUNO_API_KEY` | 音乐管理功能（与`songwriting-and-ai-music`技能搭配使用） |
| Spotify | `SPOTIFY_CLIENT_ID` + `SPOTIFY_CLIENT_SECRET` | 音乐管理功能（与`spotify`技能搭配使用） |
| Anthropic | `ANTHROPIC_API_KEY` | 所有Hermes账号（Claude模型） |

如果发现缺少某项密钥，应提示用户添加。密钥的存储优先级为：macOS钥匙串 → `${HERMES_HOME:-~/.hermes}/.env`文件 → 环境变量。

## 技能版本锁定

如需使用特定版本的技能，可通过任务级别的`--skill <名称>=<版本>`参数进行指定。默认情况下将使用已安装的最新版本。

## 向矩阵中添加新技能

当有新的Hermes公开视频技能发布时：

1. 在本文件顶部的相应表格中添加一行记录
2. 如果该技能需要专用渲染器版本，还需在`role-archetypes.md`文件中补充相关内容
3. 更新`examples.md`文件中对应风格的相关示例
