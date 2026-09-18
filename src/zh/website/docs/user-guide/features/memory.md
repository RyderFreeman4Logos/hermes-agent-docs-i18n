---
sidebar_position: 3
title: "Persistent Memory"
description: "How Hermes Agent remembers across sessions — MEMORY.md, USER.md, and session search"
---

# 持久内存

Hermes Agent 拥有有限且经过精心管理的记忆空间，这些记忆会跨会话持续保留。这使得它能够记住您的偏好设置、项目信息、使用环境以及所学到的知识。

## 工作原理

Agent 的记忆由两个文件组成：

| 文件 | 用途 | 字符限制 |
|------|------|----------|
| **MEMORY.md** | Agent 的个人笔记——包括环境相关事实、常用规则及所学内容 | 2,200 字符（约 800 个标记） |
| **USER.md** | 用户档案——存储您的偏好设置、沟通风格及期望 | 1,375 字符（约 500 个标记） |

这两个文件均保存在 `~/.hermes/memories/` 目录中，并会在会话开始时以固定快照的形式被注入系统提示词中。Agent 可通过 `memory` 工具自行管理内存——它可以添加、替换或删除相关条目。

:::caution 每个 Hermes 家目录仅对应一个 Agent
请勿让两个 Agent 进程指向同一个 Hermes 家目录。内存写入操作是自动进行的，且会在会话开始时重新加载到系统提示词中。因此，若两个 Agent 共享同一个家目录，它们的条目将会相互叠加，形成既非它们本身（也非您）创建的混合状态。按设计，内存是按 [用户档案](/user-guide/profiles) 进行隔离管理的——请为第二个 Agent 创建独立的用户档案；如果它们需要共享内存，则应使用 [外部内存提供器](/user-guide/features/memory-providers)。 
:::

:::info
字符限制有助于控制内存使用量。系统**不会**自动压缩内存：当写入内容超出限制时，`memory` 工具会返回错误，而不会悄悄删除相关条目。此时代理需要自行释放空间——在重新尝试之前，会在同一轮操作中合并或删除部分条目（详见[内存已满时会发生什么](#what-happens-when-memory-is-full)）。需要注意的是，`replace` 操作也受此限制：用更长的内容替换现有条目仍可能导致内存溢出，因此新内容必须被截短（或删除其他条目）才能适配。
:::

## 内存如何显示在系统提示中

在每个会话开始时，内存条目会从磁盘加载并以固定块的形式呈现于系统提示中：

```
══════════════════════════════════════════════
MEMORY (your personal notes) [67% — 1,474/2,200 chars]
══════════════════════════════════════════════
User's project is a Rust web service at ~/code/myapi using Axum + SQLx
§
This machine runs Ubuntu 22.04, has Docker and Podman installed
§
User prefers concise responses, dislikes verbose explanations
```

该格式包含以下要素：
- 一个标题，标明存储位置为 MEMORY 还是 USER PROFILE
- 使用率及字符计数，以便智能体了解当前容量情况
- 以 `§`（分节符）作为分隔符的各个条目
- 各条目可支持多行内容

**固定快照模式**：系统提示语会在会话开始时被捕获一次，并在会话期间保持不变。这是有意为之——这样做能够保留大语言模型的前缀缓存，从而提升性能。当智能体在会话过程中添加或删除内存条目时，这些更改会立即保存到磁盘，但直到下一次会话开始才会体现在系统提示语中。工具的响应则始终反映实时状态。

## 内存工具操作

智能体会使用 `memory` 工具执行以下操作：
- **add** — 添加新的内存条目
- **replace** — 用更新后的内容替换现有条目（通过 `old_text` 进行子字符串匹配）
- **remove** — 删除不再相关的条目（通过 `old_text` 进行子字符串匹配）

该工具没有 `read` 操作——内存内容会在会话开始时自动注入到系统提示语中。智能体会将这些记忆视为对话上下文的一部分。

### 子字符串匹配

`replace` 和 `remove` 操作采用独特的短子字符串匹配机制——无需提供完整条目文本。`old_text` 参数只需是一个能够唯一标识某一条目的子字符串即可：

```python
# If memory contains "User prefers dark mode in all editors"
memory(action="replace", target="memory",
       old_text="dark mode",
       content="User prefers light mode in VS Code, dark mode in terminal")
```

如果子字符串匹配到多个条目，系统会返回错误，要求提供更具体的匹配条件。

## 两个存储目标详解

### `memory` —— 智能体个人笔记

用于存储智能体需要记住的关于环境、工作流程及经验教训的信息：

- 环境相关信息（操作系统、工具、项目结构）
- 项目规范与配置设置
- 发现的工具特性及解决方案
- 已完成任务的记录
- 表现良好的技能与方法

### `user` —— 用户档案

用于存储关于用户身份、偏好及沟通风格的信息：

- 姓名、角色、时区
- 沟通偏好（简洁型 vs 详细型、格式偏好）
- 讨厌的事物及应避免的行为
- 工作流程习惯
- 技术水平

## 应保存与应跳过的内容

### 应主动保存的内容

智能体会自动进行保存，无需手动操作。以下情况会触发保存：
- **用户偏好**：“我更喜欢 TypeScript 而非 JavaScript” → 保存至 `user`
- **环境信息**：“该服务器运行的是 Debian 12 系统，搭配 PostgreSQL 16 数据库” → 保存至 `memory`
- **纠错提示**：“Docker 命令无需使用 `sudo`，因为用户已加入 docker 组” → 保存至 `memory`
- **项目规范**：“该项目要求使用制表符，行宽为 120 个字符，文档注释需采用 Google 风格” → 保存至 `memory`
- **已完成工作**：“2026-01-15 已将数据库从 MySQL 迁移至 PostgreSQL” → 保存至 `memory`
- **明确要求**：“请记住我的 API 密钥每月都会更换” → 保存至 `memory`

### 应跳过的内容

- **琐碎/显而易见的信息**：例如“用户询问了Python相关内容”——描述过于模糊，无法提供实际帮助。  
- **容易通过搜索获取的事实**：例如“Python 3.12支持f-string嵌套”——这类信息可通过网络搜索得到。  
- **原始数据量过大**：如庞大的代码块、日志文件或数据表格——其体积超出内存承载范围。  
- **会话特定的临时内容**：如临时文件路径、一次性调试相关上下文。  
- **已存储在上下文文件中的信息**：即SOUL.md和AGENTS.md文件中的内容。  

## 容量管理  

为确保系统提示信息的长度可控，内存使用有严格的字符限制：  

| 存储类型 | 字符限制 | 典型存储条目数 |
|---------|----------|----------------|
| memory | 2,200字符 | 8-15条 |
| user    | 1,375字符 | 5-10条 |

### 内存满时会发生什么？  

当尝试添加超出限制的条目时，工具会返回错误提示：

```json
{
  "success": false,
  "error": "Memory at 2,100/2,200 chars. Adding this entry (250 chars) would exceed the limit. Consolidate now: use 'replace' to merge overlapping entries into shorter ones or 'remove' stale or less important entries (see current_entries below), then retry this add — all in this turn.",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

此时，代理应执行以下操作：
1. 读取当前的条目（显示在错误响应中）
2. 确定那些可以删除或合并的条目
3. 使用 `replace` 功能将相关的条目合并为更简短的版本
4. 最后使用 `add` 功能添加新条目

**最佳实践：** 当内存使用率超过 80%（可在系统提示符头部查看）时，应在添加新条目之前先对现有条目进行合并。例如，将三个独立的“项目使用了 X”条目合并为一个完整的项目描述条目。

### 优质内存条目的实际示例

**简洁且信息密集的条目效果最佳：**

```
# Good: Packs multiple related facts
User runs macOS 14 Sonoma, uses Homebrew, has Docker Desktop and Podman. Shell: zsh with oh-my-zsh. Editor: VS Code with Vim keybindings.

# Good: Specific, actionable convention
Project ~/code/api uses Go 1.22, sqlc for DB queries, chi router. Run tests with 'make test'. CI via GitHub Actions.

# Good: Lesson learned with context
The staging server (10.0.1.50) needs SSH port 2222, not 22. Key is at ~/.ssh/staging_ed25519.

# Bad: Too vague
User has a project.

# Bad: Too verbose
On January 5th, 2026, the user asked me to look at their project which is
located at ~/code/api. I discovered it uses Go version 1.22 and...
```

## 防止重复内容

内存系统会自动拒绝完全相同的条目。如果您尝试添加已存在的内容，系统会返回成功响应，并提示“未添加重复内容”。

## 安全扫描

由于这些内容会被注入到系统提示语中，因此在被接受之前，系统会对内存条目进行注入攻击和数据窃取模式的扫描。任何匹配威胁模式（如提示语注入、凭证窃取、SSH后门）或包含不可见Unicode字符的内容都会被阻止。

## 会话搜索

除了MEMORY.md和USER.md之外，该智能体还可以使用`session_search`工具来搜索之前的对话记录：

- 所有的命令行界面及消息交互会话均存储在采用FTS5全文本搜索功能的SQLite数据库（`~/.hermes/state.db`）中；
- 搜索查询会直接返回数据库中的原始消息——既不会经过大型语言模型的总结，也不会被截断；
- 即使是数周前讨论过的内容，智能体也能找到，即便它们不在当前活跃内存中；
- 智能体还可以在找到的任意会话记录中实现上下滚动查看。

```bash
hermes sessions list    # Browse past sessions
```

有关三种调用方式（发现/滚动/浏览）及响应格式的详细信息，请参阅[会话搜索工具](/user-guide/sessions#session-search-tool)。

### session_search与memory的对比

| 特性 | 持久内存 | 会话搜索 |
|---------|----------|----------|
| **容量** | 总计约1,300个token | 无限制（涵盖所有会话） |
| **速度** | 即时响应（在系统提示中直接显示） | FTS5查询约20毫秒，滚动查询约1毫秒 |
| **成本** | 每次发送提示语都会产生token费用 | 免费——无需调用大型语言模型 |
| **适用场景** | 需要随时获取的关键事实 | 查找特定的过往对话内容 |
| **管理方式** | 由智能体手动筛选维护 | 自动处理——所有会话均被保存 |
| **token成本** | 每个会话固定费用（约1,300个token） | 按需收费——仅在搜索时产生费用 |

**持久内存**用于存储那些必须始终处于上下文中的关键事实。而**会话搜索**则适用于“上周我们讨论过X吗？”这类需要智能体从过往对话中调取具体信息的查询场景。

## 学习历程（`/journey`）

学习历程以时间轴形式展示Hermes所学到的所有内容——已保存的技能和记忆条目会按时间顺序排列（最旧的在上方，最新的在下方），同时还配有可操作的“星图”滑块，可用于回放知识构建的过程。相同的图表数据还会用于呈现三个不同的界面。

- **经典 CLI/独立模式** — `hermes journey`（别名：`hermes learning`、`hermes memory-graph`）可在终端中展示时间线。相关参数包括：`--play`用于播放构建过程（可通过`--fps`调整速度），`--width`/`--height`用于修改显示尺寸，`--no-color`用于禁用颜色显示，`--json`则用于输出原始的图结构数据。
- **TUI模式** — `/journey`（别名： `/learning`、 `/memory-graph`）会以叠加方式打开时间线视图。
- **桌面应用** — 输入 `/journey`即可打开星图/记忆图面板，该面板以交互式可视化形式展示相同的节点信息。

除了查看之外，这里还是对Hermes所学内容进行**筛选与修正**的场所：

| 命令 | 功能说明 |
|---------|----------|
| `hermes journey list` | 列出节点ID——即技能名称以及内存块的`memory:<source>:<index>`标识。 |
| `hermes journey delete <node> [-y]` | 删除某个节点。技能会被**归档**（可恢复），而内存块则会被直接移除。使用`-y`选项可跳过确认提示。 |
| `hermes journey edit <node>` | 会在默认编辑器中打开该节点的内容，即技能的`SKILL.md`文件或对应的内存块内容。 |

在CLI的聊天界面中使用 `/journey` 命令时，同样可以使用`list`、`delete <id>`、`edit <id>`这些子命令；而桌面面板则可直接对节点进行编辑和删除操作。

## 配置设置

```yaml
# In ~/.hermes/config.yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
  write_approval: false     # false = write freely (default) | true = require approval
```

将`memory_enabled`和`user_profile_enabled`**同时**设置为`false`，可完全关闭内置存储功能：`memory`工具会被从架构中移除，其相关说明也会从系统提示中消失，这样模型就永远不会被告知存在它无法使用的工具。而通过`memory.provider`指定的外部提供器（如Hindsight、Mem0、Honcho等）则不会受到影响，仍会保留自身的工具——当您希望使用第三方内存后端来**替代**内置文件存储时，可选用此方式。将`memory`列入`agent.disabled_toolsets`则属于更为彻底的关闭方式：它同时会隐藏外部提供器的工具。

仅将`memory_enabled`设置为`false`（用户配置仍启用）时，该工具会保留——因为它用于支持用户配置存储——但系统提示会将完整的内存使用指南替换为仅针对用户配置的简化版说明。该工具的架构仅会标识`user`目标，且直接或分阶段写入被禁用的`MEMORY.md`文件的操作都会被拒绝。反之，另一种配置则仅允许对`memory`进行操作，并拒绝写入`USER.md`文件。

## 控制内存写入（`write_approval`）

默认情况下，智能体可以自由保存内存数据——包括在每轮对话结束后进行的后台自我优化分析所生成的数据。如果您希望先进行审批后再保存，可设置`memory.write_approval: true`。这是一个简单的开关机制，同时适用于**所有**前台对话环节以及后台分析过程。

| `write_approval` | 行为设置 |
|------------------|-----------|
| `false`（默认值） | 可自由写入——无需通过审核（即前置审核模式）。 |
| `true` | 在保存任何内容之前必须获得批准。在交互式 CLI 中，前台写入操作会即时提示用户（内容长度较短，可完整显示）。而在其他场景下——如消息平台、脚本以及后台自我优化审查流程中——写入的内容会以 `/memory pending` 的形式**暂存**以便后续审核。 |

> 若要完全关闭内存功能（而不仅仅是设置审核），需同时将 `memory_enabled: false` 和 `user_profile_enabled: false` 设为该值。一旦这两个内置存储被禁用，内置的 `memory` 工具也会自动隐藏。

可通过 CLI 或任何消息平台查看已暂存的写入内容：

```
/memory pending             # list staged memory writes (auto ones tagged [auto])
/memory approve <id>        # apply one (or 'all')
/memory reject <id>         # drop one (or 'all')
/memory approval on         # turn the gate on (or 'off') and persist it
```

针对“智能体保存了关于我的错误假设”这一问题，解决方案是设置 `write_approval: true`。这样一来，每一次数据保存——尤其是那些在未收到提示时自动进行的后台操作——都必须在获得您的确认（是/否）之后，才能被写入您的个人资料中。

## 后台审核通知（`display.memory_notifications`）

在每一轮对话结束后，智能体的后台自我优化机制可能会悄悄地保存某些记忆信息或更新相关技能。这就是 Hermes 所采用的“基于用户同意的学习循环”：通过反复的修正与经验积累，这些知识会被整合为简洁的记忆条目或程序化技能；而 `write_approval` 功能则允许在相关数据影响后续对话之前，先将其暂存以供审核。默认情况下，系统会在聊天界面显示简短的“💾 记忆已更新”提示，让您知晓该操作已执行。您也可以自行调整此类通知的显示频率。

```yaml
display:
  memory_notifications: on    # off | on (default) | verbose
```

| 值 | 行为 |
|-------|-----------|
| `off` | 不发送聊天通知。审查过程仍会执行并记录日志——只是您不会看到相关提示行。 |
| `on`（默认值） | 显示通用提示，例如 `💾 内存已更新`、`💾 技能 ‘foo’ 已修复`。 |
| `verbose` | 显示变更内容的简要预览，例如 `💾 内存 ➕ 用户偏好简短回复`，或显示技能内容从“旧版”到“新版”的差异片段。 |

> 此设置仅适用于**网关**层的聊天通知。审查过程本身以及对内存/技能存储的写入操作均不受此设置影响。您可以通过 `display.platforms.<platform>.memory_notifications` 按平台单独配置该设置。

在 `on` 和 `verbose` 模式下，成功的技能批量处理都会明确标注每一项已执行的操作，包括相关支持文件的写入/删除以及技能的删除操作。处于待审批阶段的写入操作或已被回滚的批量处理不会被视为已完成变更。批量处理摘要会基于实际执行的结果生成，而不会假设所有请求的写入操作都已成功完成。

## 在成本更低的模型上运行审查（`auxiliary.background_review`）

默认情况下，审查是在您的**主聊天模型**上运行的，它会重新播放对话内容——由于这些对话已存储在提示词缓存中，因此只需进行低成本的缓存读取即可。如果您使用的是成本较高的主模型，也可以选择在成本更低的模型上执行审查：

```yaml
auxiliary:
  background_review:
    provider: openrouter
    model: google/gemini-3-flash-preview   # auto (default) = main chat model
```

当将该功能指向与主模型**不同**的模型时，审查过程将在该模型上执行，且成本会大幅降低（在基准测试中约为原来的1/3至1/5）。由于不同的模型无法复用主模型的提示缓存，因此该功能会自动仅重放对话的精简**摘要**——即最新几轮的完整内容以及早期对话的总结——而非整个对话记录，从而最大限度地减少写入新缓存的数据量。在测试中，内存捕获结果与使用主模型时的完全一致，技能捕获结果也几乎相同。

若将此设置保持为`auto`（或设置为你的主模型），则一切照旧——审查过程将继续在主模型上运行，并重放完整的预热缓存内容。

### 使用同一模型的审查机制

使用与父模型相同的模型进行审查时，**始终会继承父模型的推理工作量**。无论路径是设置为`auto`还是明确选择父模型提供商/模型，设置`auxiliary.background_review.reasoning_effort`都无法改变这一规则。

在功能启用时，推理设置、系统提示、完整的对话快照以及工具定义在初始阶段都会与父模型保持完全一致，这样审查过程就能复用其提示缓存的前缀部分。仅更改审查过程中的思考层级就会打破这种一致性。对于使用同一模型的审查，目前不存在独立的“独立工作量”切换选项。

若希望在不增加主要对话处理负担的前提下减少审核工作，可调整 `memory.nudge_interval` / `skills.creation_nudge_interval` 的值，按照下文所述禁用自动审核功能，或将审核任务转交给其他模型处理。采用其他模型进行审核时会使用摘要信息，且不会共享父任务的预热前缀；与之相关的独立任务处理开销问题正在 [#94825](https://github.com/NousResearch/hermes-agent/issues/94825) 中跟踪处理。这些频率控制与路由策略并不会解除同一模型内的推理关联。

### 禁用自动审核（`enabled` 参数）

在负载较高的主机上，审核子任务可能会占用相当大比例的总令牌量。操作人员可在无需将提示间隔重置为零的情况下禁用该功能：

```yaml
auxiliary:
  background_review:
    enabled: true              # false = skip automatic post-turn forks
```

当设置 `enabled: false` 时，不会自动触发轮次后的分叉处理；不过仍可手动执行 `/refine` 命令。

分叉使用的记录会保存在 `session_model_usage` 中，且任务类型会被标记为 `task='background_review'`，同时还会在 `agent.log` 文件中写入完成记录（格式为：`Background review complete: thread=bg-review calls=… in=… out=… result=…`）。

### 允许使用范围受限的额外审核工具（`extra_tools`）

默认情况下，后台审核可使用内存操作、技能管理以及只读文件处理工具。如果某个配置文件提供了另一种适用于无人值守审核的安全工具，可通过其名称将其启用：

```yaml
auxiliary:
  background_review:
    extra_tools:
      - propose_shared_memory
```

该工具必须已为父代理所可用；此设置仅将其添加到审核副本的运行时白名单中。它并不会启用任意工具，未列在此处的工具仍会被禁止使用。建议将列表保持简洁，优先选择那些会提交人工审核提案的工具，而非直接应用外部修改或破坏性更改的工具。默认情况下，该列表为空。

### 本地模型：审核任务会等待空闲 GPU（延迟执行）

在云服务提供商环境中，审核过程仅需数秒即可完成，且会与您后续的操作同时进行。而当审核的运行环境为**托管型本地 llama-server**（设置 → 本地模型）时，同一个 GPU 会被下一个请求占用——对于大型模型而言，这一占用时间可能长达数分钟——此时发送新的请求将会取消正在进行的审核任务，从而导致已学习到的内容被丢弃。因此，在托管型本地运行环境中，审核任务**默认为延迟执行**：会在当前轮次结束后被排队，直到机器进入一段短暂的空闲期后再开始执行。审核本身的内容不会发生变化——模型、完整对话记录的回放以及所有写入操作均保持不变，仅有执行时间会发生改变。

```yaml
auxiliary:
  background_review:
    defer: auto            # auto (default) | never
    defer_max_age_s: 1800  # run a queued review anyway after this long
```

| 值 | 行为 |
|-------|-----------|
| `auto`（默认值） | 将运行环境为托管本地服务器的评审任务放入队列，在空闲时执行；其他所有运行环境（云平台、外部服务器）则如往常一样立即启动。 |
| `never` | 保持旧有行为：无论在何处，均在回合结束时立即启动，包括在托管的本地 GPU 上。 |

已入队的评审任务会在每个会话中合并处理（新回合的快照会替换旧快照——由于评审会重放整个对话过程，因此不会丢失任何内容）；被新提示抢先处理的评审任务会被重新放入队列而非丢弃；而等待时间超过 `defer_max_age_s` 的评审任务，即便机器始终处于忙碌状态也会被执行。明确的 `/refine` 指令始终会立即执行。该队列存储在内存中：当应用退出时，仍在队列中的评审任务将会丢失，这与正在处理中的分支被中断时的结果相同。

## 控制技能写入功能（`skills.write_approval`）

技能同样使用相同的开启/关闭机制，但由于 `SKILL.md` 文件体积过大，无法在聊天窗口中完整显示，因此其评审用户界面有所不同：

```yaml
skills:
  write_approval: false     # false = write freely (default) | true = require approval
```

当设置 `write_approval: true` 时，无论数据来源如何，该技能在执行写入操作（创建/编辑/修补/写入文件/删除）时都会先将内容**暂存**。您可以直接查看简化的单行摘要，而完整的差异内容则会在单独的通道中呈现。

```
/skills pending             # list staged skill writes + a one-line gist each
/skills diff <id>           # full unified diff (best viewed in CLI or dashboard)
/skills approve <id>        # apply it (or 'all')
/skills reject <id>         # drop it (or 'all')
/skills approval on         # turn the gate on (or 'off') and persist it
```

在消息平台中，您可以根据技能的概要及元数据来批准该技能；若需查看完整的变更内容，则可通过命令行、控制面板，或访问 `~/.hermes/pending/skills/<id>.json` 下的暂存文件并执行 `/skills diff` 命令。更多详细信息请参阅[限制对技能的写入操作](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval)。

## 外部内存提供器

为满足超出 MEMORY.md 和 USER.md 范围的更深层、持久化存储需求，Hermes 内置了 8 种外部内存提供器插件——包括 Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover 以及 Supermemory。

这些外部提供器与内置内存**并行运行**（绝不会替代内置内存），并能够实现知识图谱、语义搜索、自动事实提取以及跨会话用户建模等功能。

```bash
hermes memory setup      # pick a provider and configure it
hermes memory status     # check what's active
```

如需了解各内存提供器的详细信息、配置指南以及对比分析，请参阅 [Memory Providers](./memory-providers.md) 文档。
