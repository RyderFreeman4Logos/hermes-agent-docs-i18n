# 工具矩阵——各角色的技能与工具集

该矩阵将各类角色类型与其应`始终加载`的Hermes技能以及所需工具集对应起来。仅列出公共hermes-agent仓库中已包含的技能（位于`skills/`或`optional-skills/`目录下）。外部API和CLI通过终端工具集调用，因此不会出现在`always_load`列表中。

## 与视频制作相关的Hermes技能

### 视觉/渲染技能（`hermes-agent/skills/creative/`）

| 技能 | 功能说明 | 最适合的场景 |
|------|----------|--------------|
| `ascii-video` | 用于生成ASCII艺术视频的完整流程——支持生成式创作、音频驱动效果以及视频转ASCII功能 | 适用于ASCII/终端/复古像素风格内容的渲染；可作为ASCII项目的“摄影师” |
| `ascii-art` | 生成静态ASCII艺术 | 适合负责设计ASCII风格画面的概念艺术家；也可作为ASCII渲染器的辅助工具 |
| `manim-video` | Manim CE动画引擎——用于制作数学、算法类内容，以及类似3Blue1Brown风格的讲解视频 | 适用于数学公式、算法流程及技术概念的可视化渲染 |
| `p5js` | p5.js编程语言——可创建生成艺术、着色器效果、交互式内容及3D图形 | 适用于生成艺术、粒子系统、自然运动效果以及网页画布类内容的渲染 |
| `comfyui` | 通过ComfyUI工作流生成图像、视频和音频（包括图像转图像、图像转视频等功能） | 适用于图像生成、视频生成或作为AI生成内容的全能渲染工具 |
| `touchdesigner-mcp` | 控制正在运行的TouchDesigner实例——可创建实时视觉效果、音频驱动的装置艺术作品及视频艺术家作品 | 适用于实时/音频驱动型内容的渲染；装置艺术创作；现场表演场景 |
| `blender-mcp` *(可选)* | 通过MCP控制Blender 4.3及以上版本——支持3D建模、动画制作及渲染 | 适用于3D场景、真实感环境及角色动画的渲染 |
| `pixel-art` | 使用特定时代配色方案（如NES、Game Boy、PICO-8风格）制作像素艺术 | 适用于复古游戏风格的渲染；也可作为像素风格画面的概念艺术家工具 |
| `baoyu-comic` | 生成知识类漫画（用于教育、传记或教程场景） | 适用于以漫画形式呈现叙事内容的渲染；可作为分镜形式的讲解工具 |
| `baoyu-infographic` | 生成信息图表 | 适用于数据驱动型讲解场景的渲染 |
| `meme-generation` *(可选)* | 通过在模板上叠加文字来生成迷因图片 | 适用于讽刺或社交类内容的创作；也可用于生成迷因风格静态图片 |

### 设计/前期制作技能（`hermes-agent/skills/creative/`）

| 技能 | 功能说明 | 最适合的场景 |
|------|----------|--------------|
| `claude-design` | 设计一次性使用的HTML文档（如登录页、演示文稿或原型页面） | 适用于为产品视频设计风格画面；也可用于UI元素较多的内容的分镜绘制 |
| `design-md` | 设计Markdown格式的文档 | 适用于负责记录视觉设计规范的概念艺术家 |
| `popular-web-designs` | 提供流行网页设计的参考范例 | 适用于概念艺术家；在需要匹配特定UI风格时也可作为“摄影师”辅助工具 |
| `sketch` | 快速生成用于对比的HTML原型（2-3种设计版本） | 适用于探索不同设计方向的概念艺术家；也可用于UI流程的分镜绘制 |
| `excalidraw` | 生成类似Excalidraw风格的手绘图表 | 适用于分镜绘制；也可作为草图风格画面的概念艺术家工具 |
| `architecture-diagram` | 绘制软件架构图 | 适用于技术类内容的分镜绘制；也可用于讲解系统结构的场景 |
| `concept-diagrams` *(可选)* | 生成扁平化、极简风格的SVG图表（适用于数学、物理、化学、解剖学等领域的教学可视化） | 适用于需要简洁教育性图表的讲解场景的渲染/分镜工具 |
| `pretext` | 撰写数学或科学类内容 | 适用于负责撰写技术讲解文本的作者或“摄影师” |
| `creative-ideation` | 在约束条件下进行项目创意构思 | 适用于在任务要求模糊需要明确框架时的导演或“摄影师” |
| `humanizer` | 去除文本中的AI痕迹，增添真实语气 | 适用于脚本或旁白文案的后期处理，避免出现明显的AI特征 |

### 音频/媒体技能（`hermes-agent/skills/creative/` + `skills/media/`）

| 技能 | 功能说明 | 最适合的场景 |
|------|----------|--------------|
| `songwriting-and-ai-music` | 歌曲创作技巧 + Suno提示词模板 | 适用于通过Suno委托制作音乐时的音乐监制 |
| `heartmula` | 开源音乐生成工具（遵循Apache-2.0许可，功能类似Suno） | 适用于无需外部API即可定制音乐的音乐监制 |
| `songsee` | 分析音频文件的频谱图以及梅尔频谱、色度谱和MFCC参数 | 适用于音乐监制分析音轨；音效设计师根据节奏设计音效；混音师可视化混音效果 |
| `spotify` | 控制Spotify平台——播放、搜索、创建播放列表及管理播放列表 | 适用于音乐监制寻找现有音乐素材；也可用于参考研究 |
| `youtube-content` | 获取视频字幕并转换为章节、摘要或帖子内容 | 适用于纪录片剪辑、内容改编以及制作讲解类视频时的资料收集 |
| `gif-search` | 搜索现有的GIF图片 | 适用于编辑人员或概念艺术家寻找参考素材 |
| `gifs` | GIF相关工具集 | 适用于负责处理GIF输出文件的后期制作人员 |

### 看板工作流基础设施

看板插件会自动将基础的流程编排指导嵌入到每个工作节点的系统提示词中——包括`kanban_create`的分发模式、任务交接生命周期，以及针对流程协调者的“分解而非直接执行”原则。无需额外加载看板相关技能，因为这些指导始终对看板类型的工作节点有效。

## 外部工具（通过终端工具集调用）

这些并非Hermes技能，而是各角色配置文件会调用的外部CLI或API。它们不会出现在`always_load`列表中，而是由对应角色的终端命令直接调用。

| 工具 | 功能说明 | 使用该工具的角色类型 |
|------|----------|----------------------|
| `ffmpeg` | 视频/音频的编码、拼接及多路复用处理 | 渲染器、编辑器、音频混音师、后期制作人员 |
| `ffprobe` | 分析媒体文件信息 | 所有需要处理媒体文件的角色类型 |
| Whisper（CLI或API） | 语音转文本功能，用于生成字幕 | 字幕生成工具 |
| 文本转图像API（FAL / Replicate / OpenAI / Midjourney） | 生成静态图片 | 图像生成工具（可作为本地`comfyui`的替代方案） |
| 图像转视频API（Runway / Kling / Luma / Pika） | 将静态图片转化为动画视频 | 视频生成工具 |
| 文本转语音API（ElevenLabs / OpenAI TTS等） | 生成旁白音频 | 语音合成工具 |
| Suno API或网页界面 | 用于歌曲创作（需与`songwriting-and-ai-music`技能配合使用） | 音乐监制 |
| Remotion CLI（`npx remotion render`） | 基于React技术的动态图形制作工具 | 动态图形渲染工具 |
| Manim CE（`manim`） | 基于数学公式的动画渲染（由`manim-video`技能的配方驱动） | Manim动画渲染工具 |
| Blender（`blender -b`） | 3D渲染功能（可作为`blender-mcp`的替代方案） | 3D渲染工具 |

## Hermes内置的媒体审阅工具

这些是Hermes的原生工具——无需通过终端调用，而是通过专门的工具集直接使用。可通过在角色配置文件中添加相应工具集来为特定角色启用这些功能。

| 工具 | 工具集 | 功能说明 | 使用该工具的角色类型 |
|------|---------|----------|----------------------|
| `video_analyze` | `video`（可选——需通过`hermes tools enable video`命令启用） | 原生视频理解能力——可直接将完整视频片段发送给多模态大语言模型（通过OpenRouter连接Gemini模型）进行审阅，无需逐帧提取。支持mp4、webm、mov、avi、mkv格式，文件大小上限为50 MB。默认模型为`AUXILIARY_VIDEO_MODEL`，若该模型不可用则回退至`AUXILIARY_VISION_MODEL`。 | 审阅员、摄影师、编辑 |
| `vision_analyze` | `vision`（核心功能——默认已启用） | 图像/帧分析功能——可用于审阅静态图片、缩略图及导出的帧画面。所有角色类型均可直接使用该功能，无需额外启用。 | 审阅员、摄影师、概念艺术家 |

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

### 概念艺术家

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

### 故事板绘制工具

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

对于外部 API 渲染器（如使用 Runway 的图像转视频生成器、使用 ElevenLabs 的语音合成服务，以及使用 Remotion 的动态图形渲染器），`always_load` 参数的值为空——这类工具的工作流程由 API 驱动，仅需 API 密钥加上终端命令即可（即便如此，看板系统仍会自动注入相关指引）。

而对于多技能渲染器配置（这种情况较为少见，通常为每种技能单独设置一个版本会更清晰），则可在每次调用 `kanban_create` 时使用 `--skill <name>` 参数来指定该特定任务应加载哪项技能。

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

这些功能大多由ffmpeg驱动，无需特殊技能（每个任务处理节点都会自动注入看板操作指南）。对于字幕生成器，需在SOUL.md文件中添加Whisper调用相关配置。

### 审核员/品牌合规专员

请完整翻译输入内容，切勿提前终止。

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
