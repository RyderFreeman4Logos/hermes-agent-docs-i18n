---
title: "Kanban Video Orchestrator — Plan and run multi-agent video production pipelines"
sidebar_label: "Kanban Video Orchestrator"
description: "Plan and run multi-agent video production pipelines"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 看板式视频编排器

用于规划并执行多智能体视频制作流程。

## 技能元数据

| | |
|---|---|
| Source | Optional — install with `hermes skills install official/creative/kanban-video-orchestrator` |
| Path | `optional-skills/creative\kanban-video-orchestrator` |
| Version | `1.0.0` |
| Author | ['SHL0MS', 'alt-glitch'] |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `video`, `kanban`, `multi-agent`, `orchestration`, `production-pipeline` |
| Related skills | [`ascii-video`](/docs/user-guide/skills/bundled/creative/creative-ascii-video), [`manim-video`](/docs/user-guide/skills/bundled/creative/creative-manim-video), [`p5js`](/docs/user-guide/skills/bundled/creative/creative-p5js), [`comfyui`](/docs/user-guide/skills/optional/creative/creative-comfyui), [`touchdesigner-mcp`](/docs/user-guide/skills/optional/creative/creative-touchdesigner-mcp), [`pixel-art`](/docs/user-guide/skills/optional/creative/creative-pixel-art), [`ascii-art`](/docs/user-guide/skills/optional/creative/creative-ascii-art), [`songwriting-and-ai-music`](/docs/user-guide/skills/bundled/creative/creative-songwriting-and-ai-music), [`heartmula`](/docs/user-guide/skills/optional/creative/creative-heartmula), [`songsee`](/docs/user-guide/skills/bundled/media/media-songsee), [`youtube-content`](/docs/user-guide/skills/bundled/media/media-youtube-content), [`claude-design`](/docs/user-guide/skills/bundled/creative/creative-claude-design), [`excalidraw`](/docs/user-guide/skills/optional/creative/creative-excalidraw), [`architecture-diagram`](/docs/user-guide/skills/bundled/creative/creative-architecture-diagram), [`concept-diagrams`](/docs/user-guide/skills/optional/creative/creative-concept-diagrams), [`baoyu-comic`](/docs/user-guide/skills/optional/creative/creative-baoyu-comic), [`baoyu-infographic`](/docs/user-guide/skills/bundled/creative/creative-baoyu-infographic), [`humanizer`](/docs/user-guide/skills/bundled/creative/creative-humanizer), [`gif-search`](/docs/user-guide/skills/bundled/media/media-gif-search), [`meme-generation`](/docs/user-guide/skills/optional/creative/creative-meme-generation) |

## 参考文档：完整的 SKILL.md

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当该技能处于激活状态时，智能体看到的指令即为此内容。
:::

# 看板视频编排器

无论是对产品进行15秒的预告展示、制作5分钟的叙事短片、音乐视频还是ASCII循环动画，均可通过Hermes看板流程将其封装起来，进而将任务分配给相应的专业智能体角色。

该技能本身并不负责任何内容的渲染工作。它实际上是一个元流程，具体功能包括：

1. 通过精准的筛选机制确定任务范围；
2. 根据视频风格为合适的团队配置资源（包括各角色所需工具）；
3. 生成设置脚本，用于创建Hermes智能体配置、项目工作空间以及初始看板任务；
4. 将任务转交给对应的执行角色，由该角色通过看板系统进一步拆分任务；
5. 实时监控任务执行进度，在任务停滞或失败时提供干预支持。

实际的渲染工作会在看板流程启动后由合适的现有技能和工具来完成，这些工具可能包括 `ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`songwriting-and-ai-music`、`heartmula`，以及外部API，或是结合PIL和ffmpeg的普通Python脚本。

## 何时不应使用此技能

- 若处理的是一个连续的流程型项目且无需专业人员参与，可直接编写代码即可完成。
- 若用户希望快速进行一次性转换（例如“将此 MP4 文件转换为 GIF”），则直接使用 ffmpeg 工具。
- 若输出结果为静态图片、GIF 或仅包含音频的内容，应选用对应的专用技能（如 `ascii-art`、`gifs`、`meme-generation`、`songwriting-and-ai-music`）。
- 若任务能够完美适配某项现有的单一技能（例如纯 ASCII 视频），则直接使用 `ascii-video` 即可。

## 工作流程

```
DISCOVER  →  BRIEF  →  TEAM DESIGN  →  SETUP  →  EXECUTE  →  MONITOR
```

### 第一步 — 信息收集（提出恰当的问题）

信息收集过程是**自适应的**：只需询问实际所需的内容。建议始终从三个问题入手，先确定视频的大致框架：

- **视频内容是什么？**（用一句话简要概括）
- **时长是多少？**（5-30秒的预告片 / 30-90秒的短片 / 90秒-3分钟的说明视频 / 3-10分钟的长片 / 更长）
- **宽高比及目标平台是？**（1:1 / 9:16 / 16:9；X平台、Instagram、YouTube、内部平台等）

根据用户的回答来分类视频风格。风格将决定后续需要询问哪些问题。**切勿一次性提出所有问题**，每次提出2-4个问题，听取回复后再继续。当用户给出暗示性答案时，可进行合理推测。

关于完整的资料收集流程及不同风格的提问清单，请参阅  
**[references/intake.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\kanban-video-orchestrator/references/intake.md)**。

### 第二步 — 撰写概要

在掌握足够信息后，使用 `assets/brief.md.tmpl` 中的模板来生成结构化的 `brief.md` 文件。其内容应包含以下阶段：

1. **概念** — 用一句话概括核心创意 + 确定情感基调
2. **范围** — 时长、宽高比、平台要求、截止日期
3. **风格** — 视觉参考、品牌规范、语气风格
4. **场景** — 逐镜头拆解（时长、内容、目标制作工具）
5. **音频** — 叙述声 / 音乐 / 音效 / 无声（如需可按场景分别说明）
6. **交付物** — 文件格式、分辨率，以及可选的替代版本（竖版剪辑、GIF等）
在搭建团队之前，需先向用户展示项目需求简述以获得确认。**该需求简述即为核心契约**——后续的所有任务都将以此为依据。

### 第 3 步 — 团队架构设计

从角色模板库中挑选适用于该视频的角色原型。**应进行组合配置，而非直接复制**。大多数视频需要 4 至 7 个角色配置。导演角色始终存在，其余角色则根据实际需求来确定。

有关角色模板库及不同风格下的团队配置方案，请参阅  
**[references/role-archetypes.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\kanban-video-orchestrator/references/role-archetypes.md)**。

关于如何将角色映射到对应的 Hermes 技能及工具集，请参阅  
**[references/tool-matrix.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\kanban-video-orchestrator/references/tool-matrix.md)**。

### 第 4 步 — 配置准备

生成一个配置脚本（`setup.sh`）并运行它。该脚本将执行以下操作：

1. 创建项目工作目录（`~/projects/video-pipeline/<slug>/`）
2. 将用户提供的所有资源文件复制到 `taste/`、`audio/`、`assets/` 目录中
3. 通过 `hermes profile create --clone` 命令创建每个 Hermes 角色配置
4. 为每个角色编写 `SOUL.md` 文件，用于定义其性格特征与职责范围
5. 配置各角色的 YAML 设置文件，包括所需工具集、必加载技能及当前工作目录
6. 编写 `brief.md`、`TEAM.md` 文件以及 `taste/` 目录内的内容
7. 启动初始任务 `hermes kanban create`，并将其分配给导演角色处理
使用 `scripts/bootstrap_pipeline.py`，根据简化的团队设计 JSON 文件生成 `setup.sh` 脚本。有关该设置脚本的结构、配置文件模式以及至关重要的“共享工作空间”规则，请参阅 **[references/kanban-setup.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\kanban-video-orchestrator/references/kanban-setup.md)**。

### 第 5 步 — 执行

运行 `setup.sh`。随后向用户提供相应的监控命令：

```bash
hermes kanban watch --tenant <project-tenant>     # live events
hermes kanban list  --tenant <project-tenant>     # board snapshot
hermes dashboard                                   # visual board UI
```

接下来由导演配置接管，它通过看板工具集对任务进行拆分，并将相应任务分配给各专业角色。

### 第 6 步 —— 监控与干预

需保持关注——虽然看板系统可以自主运行，但遇到卡住的任务或不良输出时，仍需要人工（或人工智能）的判断。

监控方式包括：定期查询 `kanban list`，使用 `kanban show <id>` 检查那些耗时超过预期的“运行中”任务，同时监测任务的心跳状态。当某位执行者的输出未通过审核时，可采取的标准干预措施包括：

1. 使用 `kanban_comment` 在该任务上留下具体的反馈意见；
2. 创建一个新的重试任务，并将原任务设为父任务；
3. 调整任务要求的范围，由导演重新进行任务拆分。

有关诊断方法、干预方案以及“任务卡住”时的处理流程，请参阅 **[references/monitoring.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\kanban-video-orchestrator/references/monitoring.md)**。

## 参考资料：实际应用案例

这里提供了六个涵盖不同视频风格的典型流程——故事电影、产品/营销视频、音乐视频、数学/算法讲解视频、ASCII艺术视频以及实时装置艺术视频——展示了同一工作流如何生成截然不同的团队架构与任务结构。详情请见 **[references/examples.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/creative\kanban-video-orchestrator/references/examples.md)**。

## 关键规则

1. **先探索，后行动。** 在开始生成摘要或团队配置之前，务必先回答至少三个基础问题。一份有缺陷的摘要会影响到整个处理流程。

2. **为视频匹配合适的团队配置。** 不要每次任务都重复使用相同的四类角色配置。缺乏节奏分析功能的音乐视频很可能会出现问题；而没有编剧角色的叙事电影则会导致场景逻辑混乱。详情请参阅 `references/role-archetypes.md`。

3. **每个项目对应一个工作空间。** 同一个视频的所有相关配置都会共享同一个 `dir:` 工作空间。任务通过共享文件系统及结构化的交接方式来传递成果。**每次**调用 `kanban_create` 命令时，都需指定 `workspace_kind="dir"` 以及 `workspace_path="<项目的绝对路径>"`。

4. **为每个项目设置独立租户。** 使用针对特定项目设置的租户（`--tenant <project-slug>`）。这样既能确保控制台界面清晰有序，又能避免与其他正在处理的任务相互干扰。

5. **充分利用现有技能。** 当某个场景适合使用现有的技能时，相应的渲染器应通过在其任务中添加 `--skill <name>` 参数，或在其配置中设置 `always_load` 选项来加载该技能。无需重复实现技能已具备的功能。

6. **调度器从不直接执行任务。** 即使拥有完整的“看板 + 终端 + 文件”工具集，调度器的 `SOUL.md` 规则也禁止其自行执行任务。它仅负责任务的分解与路由——每个具体任务都会转化为对对应专家配置文件的 `hermes kanban create` 调用。嵌入到每个看板工作节点系统提示中的看板编排指南对此有更详细的说明。

7. **避免过度分解任务。** 一个30秒的产品视频无需拆分为20个任务。应力求构建出最小的任务图，同时确保任务能够良好并行处理，并设置适当的人工审核节点。

8. **在启动任务前验证API密钥。** 外部API（如文本转语音、图像生成、图像转视频功能）需要使用存储在 `${HERMES_HOME:-~/.hermes}/.env` 文件或用户密钥存储库中的密钥。如果工作节点因缺少密钥而报错，就会浪费一个任务处理槽位。设置脚本中的 `check_key` 工具会在检测到缺失必要密钥时立即终止流程。

## 文件映射表

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
