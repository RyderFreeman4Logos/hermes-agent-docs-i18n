---
sidebar_position: 3
title: "Persistent Memory"
description: "How Hermes Agent remembers across sessions — MEMORY.md, USER.md, and session search"
---

# 持久内存

Hermes Agent拥有受限且经过筛选的记忆机制，这些记忆会跨会话持续保留。这使得它能够记住您的偏好设置、项目信息、使用环境以及所学到的内容。

## 工作原理

Agent的记忆由两个文件构成：

| 文件 | 用途 | 字符限制 |
|------|---------|----------|
| **MEMORY.md** | Agent的个人笔记——包括环境相关事实、约定规则以及所学内容 | 2,200字符（约800个token） |
| **USER.md** | 用户档案——记录 Impersonal的偏好设置、沟通风格及期望 | 1,375字符（约500个token） |

这两个文件均存储在`~/.hermes/memories/`目录中，并会在会话开始时以固定快照的形式被注入系统提示词中。Agent可通过`memory`工具自行管理内存——它可以添加、替换或删除其中的条目。

:::info
设置字符限制有助于让记忆内容保持有序。内存不会自动压缩：当写入内容超出限制时，`memory`工具会返回错误，而不会默默删除相关条目。此时Agent需要自行腾出空间——在尝试再次操作前，会在同一轮对话中合并或删除部分条目（详见[内存满时会发生什么](#what-happens-when-memory-is-full)）。需要注意的是，`replace`操作同样受字符限制约束：用更长的内容替换现有条目仍可能导致超出限制，因此新内容必须被截短（或删除其他条目）才能适配。
:::

## 内存如何显示在系统提示词中

在每个会话开始时，内存条目都会从磁盘加载，并以固定块的形式呈现于系统提示词中：

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

该格式包含以下内容：
- 一个标题，标明存储位置为“内存”还是“用户配置文件”
- 使用率及字符计数，以便智能体了解当前容量
- 用`§`（分节符）分隔的各个条目
- 各条目可支持多行

**固定快照模式**：系统提示语会在会话开始时被捕获一次，并在会话期间保持不变。这是有意为之——这样做可以保留大语言模型的前缀缓存，从而提升性能。当智能体在会话过程中添加或删除内存条目时，这些更改会立即保存到磁盘，但直到下一次会话开始才会反映在系统提示语中。工具的响应则始终显示实时状态。

## 内存工具操作

智能体会使用以下操作来调用`memory`工具：
- **add** — 添加新的内存条目
- **replace** — 用更新后的内容替换现有条目（通过`old_text`进行子字符串匹配）
- **remove** — 删除不再相关的条目（通过`old_text`进行子字符串匹配）

该工具没有`read`操作——内存内容会在会话开始时自动注入到系统提示语中。智能体将其记忆内容视为对话上下文的一部分。

### 子字符串匹配

`replace`和`remove`操作采用独特的短子字符串匹配机制——无需提供完整的条目文本。`old_text`参数只需是一个能够唯一标识某一条目的子字符串即可：

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
- 经过验证有效的技能与方法

### `user` —— 用户档案

用于存储关于用户身份、偏好及沟通风格的信息：

- 姓名、角色、时区
- 沟通偏好（简洁型 vs 详细型、格式偏好）
- 不耐烦的事宜及应避免的行为
- 工作流程习惯
- 技术水平

## 该保存哪些内容，又该跳过哪些？

### 应主动保存的内容

智能体会自动保存这些信息——无需手动请求。当它了解到以下内容时会进行保存：

- **用户偏好**：“我更喜欢 TypeScript 而非 JavaScript” → 保存到 `user`
- **环境相关信息**：“该服务器运行的是 Debian 12 系统，搭配 PostgreSQL 16 数据库” → 保存到 `memory`
- **修正建议**：“执行 Docker 命令时无需使用 `sudo`，因为用户已加入 docker 组” → 保存到 `memory`
- **项目规范**：“该项目要求使用制表符缩进，行宽为120个字符，文档注释需采用 Google 风格” → 保存到 `memory`
- **已完成的工作**：“2026-01-15 已将数据库从 MySQL 迁移至 PostgreSQL” → 保存到 `memory`
- **明确要求**：“请记住我的 API 密钥每月都会更换” → 保存到 `memory`

### 应跳过的内容

- **琐碎/显而易见的信息**：“用户询问了 Python 相关内容”——信息过于模糊，无实际用途
- **容易重新获取的事实**：“Python 3.12 支持 f-string 嵌套”——可通过网络搜索查询
- **原始数据块**：大型代码片段、日志文件、数据表格——体积过大，无法存储在内存中
- **会话特定的临时信息**：临时文件路径、一次性调试上下文
- **已存在于上下文文件中的信息**：SOUL.md 和 AGENTS.md 文件中的内容

## 容量管理

为限制系统提示词的长度，`memory` 存储有严格的字符限制：

| 存储目标 | 字符限制 | 典型存储条目数 |
|---------|----------|--------------|
| memory | 2,200 字符 | 8-15 条目 |
| user   | 1,375 字符 | 5-10 条目 |

### 内存已满时的处理方式

当尝试添加超出限制的条目时，工具会返回错误：

```json
{
  "success": false,
  "error": "Memory at 2,100/2,200 chars. Adding this entry (250 chars) would exceed the limit. Consolidate now: use 'replace' to merge overlapping entries into shorter ones or 'remove' stale or less important entries (see current_entries below), then retry this add — all in this turn.",
  "current_entries": ["..."],
  "usage": "2,100/2,200"
}
```

随后，该智能体应执行以下操作：
1. 读取当前的条目（显示在错误响应中）；
2. 确定哪些条目可以删除或合并；
3. 使用 `replace` 功能将相关的条目整合为更简短的版本；
4. 最后使用 `add` 功能添加新条目。

**最佳实践：** 当内存使用率超过 80%（可在系统提示符标题中查看）时，应在添加新条目之前先对现有条目进行合并。例如，将三个独立的“项目使用了 X”条目合并为一个完整的项目描述条目。

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

由于内存条目会被注入到系统提示语中，因此在被接受之前，系统会对其进行注入攻击和数据窃取模式的扫描。任何匹配威胁模式（如提示语注入、凭证窃取、SSH后门）或包含不可见Unicode字符的内容都会被拦截。

## 会话搜索

除了 MEMORY.md 和 USER.md 中的内容外，该智能体还可以使用 `session_search` 工具来搜索过往的对话记录：

- 所有的命令行界面和消息交互会话都存储在基于 FTS5 全文搜索功能的 SQLite 数据库（`~/.hermes/state.db`）中；
- 搜索查询会直接返回数据库中的原始消息——既不会经过大型语言模型的总结，也不会被截断；
- 即使是数周前讨论过的内容，智能体也能找到，即便它们不在当前活跃内存中；
- 智能体还可以在任何找到的会话中向前或向后滚动查看内容。

```bash
hermes sessions list    # Browse past sessions
```

有关三种调用方式（发现/滚动/浏览）及响应格式的详细信息，请参阅[会话搜索工具](/user-guide/sessions#session-search-tool)。

### session_search与memory的对比

| 特性 | 持久内存 | 会话搜索 |
|---------|------------------|----------------|
| **容量** | 总计约1,300个token | 无限制（涵盖所有会话） |
| **速度** | 即时响应（在系统提示中直接显示） | FTS5查询约20毫秒，滚动查询约1毫秒 |
| **成本** | 每次发送提示语都需要支付token费用 | 免费——无需调用大型语言模型 |
| **适用场景** | 需要随时获取的关键事实 | 查找特定的过往对话内容 |
| **管理方式** | 由智能体手动筛选维护 | 自动处理——所有会话均被存储 |
| **token成本** | 每个会话固定费用（约1,300个token） | 按需付费——仅在搜索时产生费用 |

**持久内存**用于存储那些必须始终保留在上下文中的关键事实。而**会话搜索**则适用于“我们上周是否讨论过X？”这类需要智能体从过往对话中调取具体信息的查询场景。

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

## 控制内存写入（`write_approval`）

默认情况下，智能体可以自由地保存内存数据——包括在每个对话轮次结束后进行的后台自我优化分析所需的数据。如果您希望先获得批准后再进行保存，可设置 `memory.write_approval: true`。这一简单的开关机制同时适用于**前台对话轮次**和后台分析过程：

| `write_approval` | 行为表现 |
|------------------|-----------|
| `false`（默认值） | 可自由写入——开关处于关闭状态（即默认行为）。 |
| `true` | 在保存任何数据之前都需要先获得批准。在交互式 CLI 中，前台写入操作会实时提示用户（由于数据量较小，可完整显示）。而在其他场景——如消息平台、脚本以及后台自我优化分析中——所有写入操作都会通过 `/memory pending` 被**暂存**以供审核。 |

> 若要完全关闭内存功能（而不仅仅是设置审核开关），请将 `memory_enabled: false` 设为真值。

您可以通过 CLI 或任何消息平台来查看那些被暂存待审的写入数据：

```
/memory pending             # list staged memory writes (auto ones tagged [auto])
/memory approve <id>        # apply one (or 'all')
/memory reject <id>         # drop one (or 'all')
/memory approval on         # turn the gate on (or 'off') and persist it
```

针对“智能体保存了关于我的错误假设”这一问题，解决方案是设置 `write_approval: true`。这样一来，每一次数据保存——尤其是那些在未收到提示时自动进行的后台保存——都必须在获得您的确认（是/否）之后，才会被写入您的个人资料中。

## 控制技能数据的写入（`skills.write_approval`）

技能功能也采用相同的开启/关闭机制，但由于 `SKILL.md` 文件体积过大，无法在聊天窗口中完整显示，因此其审核流程的界面设计有所不同。

```yaml
skills:
  write_approval: false     # false = write freely (default) | true = require approval
```

当设置 `write_approval: true` 时，无论操作来源如何，该技能进行的写入操作（创建/编辑/补丁应用/write_file/删除）都会先进入**暂存阶段**。您可以直接查看简化的单行摘要，而完整的差异内容则会在单独的通道中呈现。

```
/skills pending             # list staged skill writes + a one-line gist each
/skills diff <id>           # full unified diff (best viewed in CLI or dashboard)
/skills approve <id>        # apply it (or 'all')
/skills reject <id>         # drop it (or 'all')
/skills approval on         # turn the gate on (or 'off') and persist it
```

在消息平台中，可通过技能的概要信息及元数据来批准该技能；若需查看全部更改内容，则可在命令行、控制面板或位于 `~/.hermes/pending/skills/<id>.json` 下的暂存文件中执行 `/skills diff` 命令。更多详细信息请参阅[限制对技能的写入操作](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval)。

## 外部内存提供器

为满足超出 MEMORY.md 和 USER.md 范围的更深层、持久化存储需求，Hermes 提供了 8 种外部内存提供器插件——包括 Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover 以及 Supermemory。

这些外部提供器与内置内存**并行运行**（绝不会替代内置内存），并能够实现知识图谱、语义搜索、自动事实提取以及跨会话用户建模等功能。

```bash
hermes memory setup      # pick a provider and configure it
hermes memory status     # check what's active
```

如需了解各内存提供器的详细信息、配置指南以及对比分析，请参阅 [Memory Providers](./memory-providers.md) 文档。
