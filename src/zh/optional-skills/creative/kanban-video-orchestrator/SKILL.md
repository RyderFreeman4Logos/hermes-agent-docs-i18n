---
name: kanban-video-orchestrator
description: Plan, set up, and monitor a multi-agent video production pipeline backed by Hermes Kanban. Use when the user wants to make ANY video — narrative film, product/marketing, music video, explainer, ASCII/terminal art, abstract/generative loop, comic, 3D, real-time/installation — and the work warrants decomposition into specialized profiles (writer, designer, animator, renderer, voice, editor, etc.) coordinated through a kanban board. Performs adaptive discovery to scope the brief, designs an appropriate team for the requested style, generates the setup script that creates Hermes profiles + initial kanban task, then helps monitor execution and intervene when tasks stall or fail. Routes scenes to whichever Hermes rendering / audio / design skill fits each beat (`ascii-video`, `manim-video`, `p5js`, `comfyui`, `touchdesigner-mcp`, `blender-mcp`, `pixel-art`, `baoyu-comic`, `claude-design`, `excalidraw`, `songsee`, `heartmula`, …) plus external APIs for TTS, image-gen, and image-to-video as needed.
version: 1.0.0
author: [SHL0MS, alt-glitch]
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, kanban, multi-agent, orchestration, production-pipeline]
    related_skills: [kanban-orchestrator, kanban-worker, ascii-video, manim-video, p5js, comfyui, touchdesigner-mcp, blender-mcp, pixel-art, ascii-art, songwriting-and-ai-music, heartmula, songsee, spotify, youtube-content, claude-design, excalidraw, architecture-diagram, concept-diagrams, baoyu-comic, baoyu-infographic, humanizer, gif-search, meme-generation]
    credits: |
      The single-project workspace layout, profile-config patching pattern,
      SOUL.md-per-profile model, TEAM.md task-graph convention, and
      `--workspace dir:<path>` discipline are adapted from alt-glitch's
      original multi-agent video pipeline at
      https://github.com/NousResearch/kanban-video-pipeline.
---

# Kanban 视频编排工具

无论是对15秒的产品预告片、5分钟的叙事短片、音乐视频，还是ASCII循环动画等任何类型的视频处理需求，都可以通过Hermes的Kanban流水线来完成。该流水线会将任务拆分并分配给相应的专用智能体。

此技能本身并不负责实际的渲染工作，而是一个元级流水线，其功能包括：

1. 通过精准的匹配机制确定任务范围；
2. 根据视频风格为合适的团队配置角色及所需工具；
3. 生成设置脚本，用于创建Hermes智能体配置、项目工作空间以及初始的Kanban任务；
4. 将任务移交至对应的执行智能体，由其通过Kanban流程完成具体处理；
5. 实时监控任务执行进度，在任务停滞或失败时及时介入干预。

实际的渲染工作会在Kanban流水线启动后由适合该场景的现有技能与工具来完成，这些工具可能包括：`ascii-video`、`manim-video`、`p5js`、`comfyui`、`touchdesigner-mcp`、`blender-mcp`、`songwriting-and-ai-music`、`heartmula`，以及外部API，或是结合PIL和ffmpeg的纯Python代码。

## 何时不应使用此技能

- 当视频属于无需专业分工的连续式流程项目时，可直接编写代码进行处理；
- 若用户仅需快速完成单次转换（例如“将此MP4文件转换为GIF”），建议直接使用ffmpeg；
- 当输出结果为静态图片、GIF或纯音频文件时，应使用对应的专用技能（如`ascii-art`、`gifs`、`meme-generation`、`songwriting-and-ai-music`）；
- 若任务能够被某一个现有的技能完美处理（例如纯ASCII格式的视频），则直接使用该技能即可。

## 工作流程

```
DISCOVER  →  BRIEF  →  TEAM DESIGN  →  SETUP  →  EXECUTE  →  MONITOR
```

### 第1步 — 信息收集（提出恰当的问题）

信息收集过程是**自适应的**：只需询问实际所需的内容。始终从三个问题开始，以明确视频的大致框架：

- **视频内容是什么？**（用一句话简要概括）
- **时长是多少？**（5-30秒的预告片 / 30-90秒的短片 / 90秒-3分钟的讲解视频 / 3-10分钟的电影级作品 / 更长时长）
- **宽高比及目标平台是什么？**（1:1 / 9:16 / 16:9；X平台、Instagram、YouTube、内部平台等）

根据用户的回答确定风格类别，不同风格决定了后续需要询问的问题。**切勿一次性提出所有问题**，每次询问2-4个问题，听取回复后再继续。当用户给出暗示性答案时，可进行合理推测。

完整的收集流程及各类风格的提问清单，请参阅 **[references/intake.md](references/intake.md)**。

### 第2步 — 撰写概要

在掌握足够信息后，使用 `assets/brief.md.tmpl` 模板编写结构化的 `brief.md` 文件。内容需涵盖以下部分：

1. **核心概念**——用一句话概括视频主旨，并明确其情感基调
2. **项目范围**——时长、宽高比、平台要求、截止日期
3. **风格定位**——视觉参考风格、品牌规范、整体语调
4. **分场景规划**——逐镜拆解（包含时长、内容描述及所需工具）
5. **音频元素**——旁白/音乐/音效/静音（如需可按场景细化）
6. **交付物要求**——文件格式、分辨率，以及可选的替代版本（竖屏剪辑版、GIF等）

在组建制作团队之前，需将概要展示给用户确认。**概要即合同**——后续的所有任务都将以此为依据。

### 第3步 — 团队组建

从角色库中挑选适合该视频的角色原型。**应组合不同角色，而非直接复制**。大多数视频需要4-7个角色配置。导演角色始终必备，其余角色则根据概要中的实际需求来确定。

角色库及各类风格的团队配置方案，请参阅 **[references/role-archetypes.md](references/role-archetypes.md)**。

关于各角色对应哪些Hermes技能及工具集的映射关系，可查看 **[references/tool-matrix.md](references/tool-matrix.md)**。

### 第4步 — 环境配置

生成配置脚本 `setup.sh` 并运行它。该脚本会执行以下操作：

1. 创建项目工作目录（`~/projects/video-pipeline/<slug>/`）
2. 将用户提供的所有素材复制到 `taste/`、`audio/`、`assets/` 目录中
3. 通过 `hermes profile create --clone` 命令创建每个Hermes角色配置
4. 为每个角色编写 `SOUL.md` 文件，明确其性格特点及角色定位
5. 配置各角色的YAML文件（包含工具集、需始终加载的技能以及工作目录路径）
6. 编写 `brief.md`、`TEAM.md` 文件，并生成 `taste/` 目录中的相关内容
7. 创建初始任务 `hermes kanban create`，并将其分配给导演处理

可使用 `scripts/bootstrap_pipeline.py` 根据概要文件及团队配置的JSON数据生成 `setup.sh` 脚本。关于脚本结构、角色配置规范以及重要的“共享工作空间”规则，请参阅 **[references/kanban-setup.md](references/kanban-setup.md)**。

### 第5步 — 执行制作

运行 `setup.sh` 脚本。之后向用户提供用于监控项目进度的命令：

```bash
hermes kanban watch --tenant <project-tenant>     # live events
hermes kanban list  --tenant <project-tenant>     # board snapshot
hermes dashboard                                   # visual board UI
```

从这里开始，由“导演配置文件”接管工作，它通过看板工具集将任务拆分并分配给相应的专业配置文件。

### 第6步 — 监控与干预

保持关注——看板系统可以自主运行，但遇到卡住的任务或不良输出时，仍需人工（或人工智能）进行判断。

监控方式包括：定期查询 `kanban list`，使用 `kanban show <id>` 检查那些持续时间超过预期的“运行中”任务，并监测任务的心跳状态。当某个工作人员的输出未通过审核时，可采取的标准干预措施包括：

1. 在该工作人员的任务上留下具体的反馈意见（使用 `kanban_comment`）；
2. 创建一个以原任务为父任务的重新执行任务；
3. 调整任务要求的范围，让“导演”重新进行任务拆分。

有关诊断方法、干预方案以及处理“任务卡住”情况的指南，请参阅 **[references/monitoring.md](references/monitoring.md)**。

## 参考：实际案例

这里提供了六个涵盖不同视频风格的典型流程示例——叙事电影、产品/营销视频、音乐视频、数学/算法讲解视频、ASCII艺术视频以及实时装置艺术视频——展示了同一工作流如何针对不同的团队和任务结构产生不同的成果。详情请参见 **[references/examples.md](references/examples.md)**。

## 重要规则

1. **先探索，后行动。** 在创建任务描述或团队之前，务必先回答至少三个基础问题。一个糟糕的任务描述会影响到整个流程的效率。

2. **让团队与视频类型相匹配。** 不要每次都使用相同的四配置文件组合来处理不同类型的任务。例如，没有节奏分析配置文件的音乐视频很难达到预期效果；而没有编剧配置文件的叙事电影则会产生逻辑混乱的场景。详情请参阅 `references/role-archetypes.md`。

3. **每个项目对应一个工作空间。** 某个视频的所有相关配置文件都共享同一个 `dir:` 工作空间。任务通过共享的文件系统以及结构化的交接方式传递成果。**每次**调用 `kanban_create` 时，都会传入 `workspace_kind="dir"` 和 `workspace_path="<绝对项目路径>"` 这两个参数。

4. **为每个项目设置独立的租户。** 使用特定于项目的租户标识（`--tenant <project-slug>`）。这样可以限制控制台的显示范围，避免与其他正在进行的看板任务相互干扰。

5. **充分利用现有技能。** 如果某个场景适合某种现有的技能，相关的渲染工具应通过在其任务中添加 `--skill <name>` 参数，或在其配置文件中设置 `always_load` 选项来加载该技能。无需重复开发技能已具备的功能。

6. **“导演”绝不直接执行任务。** 即使拥有完整的 `kanban + terminal + file` 工具集，“导演”的 `SOUL.md` 规则也禁止其直接执行任务。它的职责仅限于任务拆分与分配——每一个具体的任务都会转化为针对相应专业配置文件的 `hermes kanban create` 调用。`kanban-orchestrator` 技能对此有更详细的说明。

7. **避免过度拆分任务。** 一个30秒的产品视频并不需要20个任务。应力求构建出最小的任务结构，同时确保任务能够高效并行处理，并设置合适的人工审核节点。

8. **在启动任务前验证API密钥。** 外部API（如文本转语音、图像生成、图像转视频等功能）需要从 `${HERMES_HOME:-~/.hermes}/.env` 文件或用户的密钥存储中获取相应的密钥。如果缺少密钥，工作人员的任务就会失败，从而浪费任务资源。设置脚本中的 `check_key` 工具会在检测到缺失必要密钥时立即终止流程。

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
