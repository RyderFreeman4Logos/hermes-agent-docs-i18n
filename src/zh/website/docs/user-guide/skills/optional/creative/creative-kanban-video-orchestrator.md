---
title: "Kanban Video Orchestrator — Plan, set up, and monitor a multi-agent video production pipeline backed by Hermes Kanban"
sidebar_label: "Kanban Video Orchestrator"
description: "Plan, set up, and monitor a multi-agent video production pipeline backed by Hermes Kanban"
---

/* 本页面由 website/scripts/generate-skill-docs.py 根据该技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */ 

# Kanban 视频编排工具

基于 Hermes Kanban 平台，用于规划、搭建并监控多智能体视频制作流程。当用户需要制作各类视频——无论是叙事电影、产品/营销视频、音乐视频、解说视频、ASCII/终端艺术作品、抽象/生成循环视频、漫画、3D 视频、实时艺术或装置艺术——且这类工作需要拆分为由不同角色（编剧、设计师、动画师、渲染师、配音员、剪辑师等）承担的任务，并通过看板进行协调时，便可使用此工具。该工具会通过智能适配机制明确项目需求，根据所需风格组建合适的团队，生成用于创建 Hermes 智能体配置文件及初始看板任务的设置脚本，进而协助监控任务执行情况，在任务停滞或失败时及时介入处理。它还会根据不同场景的需求，将相应任务分配给合适的 Hermes 渲染/音频/设计智能体（如 `ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`blender-mcp`、`pixel-art`、`baoyu-comic`、`claude-design`、`excalidraw`、`songsee`、`heartmula` 等），并在必要时调用外部 API 实现文本转语音、图像生成及图像转视频等功能。

## 技能元数据

| | |
|---|---|
| 来源 | 可选——可通过 `hermes skills install official/creative/kanban-video-orchestrator` 安装 |
| 路径 | `optional-skills/creative/kanban-video-orchestrator` |
| 版本 | `1.0.0` |
| 开发者 | ['SHL0MS', 'alt-glitch'] |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `video`、`kanban`、`multi-agent`、`orchestration`、`production-pipeline` |
| 相关技能 | [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video)、[`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video)、[`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js)、[`comfyui`](/docs/user-guide/skills/bundled/creative/creative-comfyui)、[`touchdesigner-mcp`](/docs/user-guide/skills/bundled/creative/creative-touchdesigner-mcp)、[`blender-mcp`](/docs/user-guide/skills/optional/creative/creative-blender-mcp)、[`pixel-art`](/docs/user-guide/skills/optional/creative/creative-pixel-art)、[`ascii-art`](/docs/user-guide/skills/bundled/creative/creative-ascii-art)、[`songwriting-and-ai-music`](/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music)、[`heartmula`](/docs/user-guide/skills/bundled/media/media-heartmula)、[`songsee`](/docs/user-guide/skills/bundled/media/media-songsee)、`spotify`、[`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content)、[`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design)、[`excalidraw`](/docs/user-guide/skills/bundled/creative/creative-excalidraw)、[`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram)、[`concept-diagrams`](/docs/user-guide/skills/optional/creative/creative-concept-diagrams)、[`baoyu-comic`](/docs/user-guide/skills/optional/creative/creative-baoyu-comic)、[`baoyu-infographic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-infographic)、[`humanizer`](/docs/user-guide/skills/bundled/creative/creative-humanizer)、[`gif-search`](/docs/user-guide/skills/bundled/media/media-gif-search)、[`meme-generation`](/docs/user-guide/skills/optional/creative/creative-meme-generation) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当该技能处于激活状态时，智能体所看到的指令即为此内容。
:::

# Kanban 视频编排工具

无论是对15秒的产品预告片、5分钟的叙事短片、音乐视频还是ASCII循环动画等任何类型的视频制作需求，均可通过Hermes Kanban流程将其封装起来，进而将任务拆分分配给不同的专业智能体角色。

该技能本身并不负责任何渲染工作。它实际上是一个元流程，具体功能包括：

1. 通过精准的识别机制明确项目需求范围；
2. 根据视频风格确定合适的团队组成（包括各角色的职责及所需工具）；
3. 生成设置脚本，用于创建Hermes智能体配置文件、项目工作空间以及初始看板任务；
4. 将任务交由对应的负责人智能体处理，由其通过看板进一步拆分任务；
5. 监控任务执行情况，在任务停滞或失败时提供协助。

实际的渲染工作则会在看板流程启动后由合适的现有智能体及工具来完成，这些工具可能包括 `ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`blender-mcp`、`songwriting-and-ai-music`、`heartmula`，或是外部API，甚至是结合PIL和ffmpeg的普通Python脚本。

## 何时不宜使用此技能

- 当视频项目属于单一的连续式流程，无需专业分工时——可直接编写代码完成制作；
- 当用户仅需快速进行一次性转换（例如“将此MP4文件转换为GIF”）时——可直接使用ffmpeg工具；
- 当输出结果为静态图片、GIF或仅包含音频的内容时——应使用对应的专用技能（如 `ascii-art`、`gifs`、`meme-generation`、`songwriting-and-ai-music`）；
- 当任务完全适合某一个现有的单一技能处理时（例如纯粹的ASCII视频——可直接使用 `ascii-video`）。

## 工作流程

```
DISCOVER  →  BRIEF  →  TEAM DESIGN  →  SETUP  →  EXECUTE  →  MONITOR
```

### 第1步 — 信息收集（提出恰当的问题）

信息收集过程是**自适应的**：只需询问实际需要的内容。首先通过三个问题确定视频的大致框架：

- **视频内容是什么？**（用一句话简要描述）
- **时长是多少？**（5-30秒的预告片 / 30-90秒的短片 / 90秒-3分钟的说明视频 / 3-10分钟的长片 / 更长）
- **宽高比及目标平台是什么？**（1:1 / 9:16 / 16:9；X平台、Instagram、YouTube、内部平台等）

根据回答对视频风格进行分类，不同的风格决定了后续需要询问的问题。**切勿一次性提出所有问题**，每次询问2-4个问题，听取用户反馈后再继续。当用户给出暗示性答案时，可做出合理推测。

完整的收集流程及不同风格的提问清单，请参阅  
**[references/intake.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/intake.md)**。

### 第2步 — 撰写概要

在掌握足够信息后，使用`assets/brief.md.tmpl`中的模板生成结构化的`brief.md`文件。其内容包含以下部分：

1. **概念**——用一句话概括核心创意 + 情感基调
2. **范围**——时长、宽高比、平台要求、截止日期
3. **风格**——视觉参考、品牌规范、语调要求
4. **场景**——逐镜拆解（包含时长、内容描述及目标处理工具）
5. **音频**——旁白/音乐/音效/无声（如需可按场景细分）
6. **交付物**——文件格式、分辨率，以及可选的替代版本（竖屏版、GIF等）

在设计制作团队之前，需将概要展示给用户确认。**概要即合同**——后续的所有任务都将以此为依据。

### 第3步 — 团队组建

从角色库中挑选适合该视频的角色原型。**应组合不同角色，而非简单复制**。大多数视频需要4-7个角色配置。导演角色必不可少，其余角色则根据概要的具体需求来确定。

角色库及不同风格的团队组合方案，请参阅  
**[references/role-archetypes.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/role-archetypes.md)**。

关于各角色对应Hermes技能及工具集的映射关系，可查看  
**[references/tool-matrix.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/tool-matrix.md)**。

### 第4步 — 环境准备

生成一个设置脚本`setup.sh`并运行它。该脚本会执行以下操作：

1. 创建项目工作目录（`~/projects/video-pipeline/<slug>/`）
2. 将用户提供的所有素材复制到`taste/`、`audio/`、`assets/`文件夹中
3. 通过`hermes profile create --clone`为每个角色创建Hermes配置文件
4. 为每个配置文件编写`SOUL.md`文件（包含角色性格设定与职责描述）
5. 配置各角色的YAML文件（包括工具集、需始终加载的技能及当前工作目录）
6. 编写`brief.md`、`TEAM.md`文件以及`taste/`文件夹中的内容
7. 启动初始任务`hermes kanban create`，并将该任务分配给导演处理

可通过`scripts/bootstrap_pipeline.py`根据概要文件及团队配置的JSON数据生成`setup.sh`脚本。关于设置脚本的结构、角色配置规范以及重要的“共享工作空间”规则，请参阅  
**[references/kanban-setup.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/kanban-setup.md)**。

### 第5步 — 执行制作

运行`setup.sh`脚本。之后向用户提供用于监控项目进度的命令：

```bash
hermes kanban watch --tenant <project-tenant>     # live events
hermes kanban list  --tenant <project-tenant>     # board snapshot
hermes dashboard                                   # visual board UI
```

从这里开始，由“导演角色配置”接管工作，它通过看板工具集将任务拆分并分配给相应的专业角色配置。

### 第6步 — 监控与干预

需保持关注——虽然看板系统可以自主运行，但遇到卡住的任务或质量不佳的输出时，仍需要人工（或人工智能）进行判断。

监控方式包括：定期查询 `kanban list`，使用 `kanban show <id>` 检查那些耗时超过预期的“运行中”任务，并查看任务的心跳状态。当某个工作者的输出未通过审核时，可采取的标准干预措施包括：

1. 在该工作者的任务上留下具体的反馈意见（使用 `kanban_comment`）；
2. 创建一个以原任务为父任务的重新执行任务；
3. 调整任务要求的范围，再由“导演角色”负责重新拆分任务。

有关诊断方案、干预流程以及处理“任务卡住”问题的指南，请参阅 **[references/monitoring.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/monitoring.md)**。

## 参考：实际案例

这里提供了六个涵盖不同视频风格的典型流程示例——故事片、产品/营销视频、音乐视频、数学/算法讲解视频、ASCII艺术视频以及实时装置艺术视频——展示了如何通过相同的工作流生成截然不同的团队配置和任务结构。详情请见 **[references/examples.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative/kanban-video-orchestrator/references/examples.md)**。

## 重要规则

1. **先探索，后行动。** 在开始创建任务描述或团队之前，必须至少回答三个基础问题。一个糟糕的任务描述会影响到整个流程的顺利进行。

2. **让团队与视频类型相匹配。** 不要每次都使用相同的四角色配置模式。如果制作音乐视频却没有节奏分析角色，那么结果必然不佳；同样，如果制作故事片却没有编剧角色，产生的场景也会缺乏逻辑性。详情请参阅 `references/role-archetypes.md`。

3. **每个项目对应一个工作空间。** 同一个视频的所有相关角色配置都共享同一个 `dir:` 工作空间。任务通过共享文件系统以及结构化的交接方式传递成果。**每次**调用 `kanban_create` 时，都会传入 `workspace_kind="dir"` 以及 `workspace_path="<项目的绝对路径>"` 这两个参数。

4. **为每个项目设置独立租户。** 应使用特定于项目的租户标识（`--tenant <project-slug>`）。这样可以限制控制台显示的内容范围，避免与其他正在进行的看板任务相互干扰。

5. **充分利用现有技能。** 当某个场景适合某种现有的技能时，相应的渲染工具应通过在其任务中添加 `--skill <name>` 参数，或在其角色配置中设置 `always_load` 选项来加载该技能。无需重复实现技能已具备的功能。

6. **“导演角色”绝不直接执行任务。** 即便拥有完整的“看板 + 终端 + 文件”工具集，“导演角色”的 `SOUL.md` 规则也禁止其直接执行任务。它的职责仅限于拆分任务并分配给相应角色——每一个具体的任务都会转化为针对某个专业角色配置的 `hermes kanban create` 调用。系统自动生成的看板编排指南对此有更详细的说明。

7. **避免过度拆分任务。** 一个30秒的产品视频并不需要20个任务。应力求构建出最小的任务结构，同时确保任务能够高效并行处理，并设置适当的人工审核节点。

8. **在启动任务前先验证API密钥。** 外部API（如文本转语音、图像生成、图像转视频等功能）需要从 `${HERMES_HOME:-~/.hermes}/.env` 文件或用户的密钥存储库中获取相应的密钥。如果工作者因缺少密钥而出现错误，就会浪费一个任务处理名额。设置脚本中的 `check_key` 辅助函数会在检测到缺失必要密钥时立即终止任务执行。

## 文件结构图

```
SKILL.md                            ← this file (workflow + rules)
references/
  intake.md                         ← discovery question banks per style
  role-archetypes.md                ← role library (writer, designer, animator, …)
  tool-matrix.md                    ← skill + toolset mapping per role
  kanban-setup.md                   ← setup script structure & profile config
  monitoring.md                     ← watch + intervene patterns
  examples.md                       ← six worked pipelines
assets/
  brief.md.tmpl                     ← brief skeleton
  setup.sh.tmpl                     ← setup script skeleton
  soul.md.tmpl                      ← profile personality skeleton
scripts/
  bootstrap_pipeline.py             ← generate setup.sh from brief + team JSON
  monitor.py                        ← polling + intervention helpers
```
