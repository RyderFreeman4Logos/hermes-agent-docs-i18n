---
sidebar_position: 7
title: "Sessions"
description: "Session persistence, resume, search, management, and per-platform session tracking"
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# 会话

Hermes Agent 会自动将每段对话保存为一个会话。会话功能支持对话续接、跨会话搜索以及完整的对话历史管理。

## 会话的工作原理

无论通过 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Teams 还是其他任何消息平台进行的对话，都会作为包含完整消息历史的会话被存储下来。这些会话被记录在以下位置：

1. **SQLite 数据库**（`~/.hermes/state.db`）——包含结构化的会话元数据以及支持 FTS5 全文搜索功能的完整消息历史

SQLite 数据库存储的内容包括：
- 会话 ID、来源平台、用户 ID
- **会话标题**（唯一且易于识别的名称）
- 模型名称及配置参数
- 系统提示词的快照
- 完整的消息历史（包括发送者角色、消息内容、工具调用记录及工具返回结果）
- 输入/输出 token 数量
- 时间戳（开始时间、结束时间）
- 上级会话 ID（用于因压缩需求而拆分会话时使用）

### 什么会被纳入上下文

Hermes 会保存会话历史以便恢复对话，但不会重复发送所有处理过的内容。在每一轮对话中，模型只能看到选定的系统提示词、当前的对话窗口，以及 Hermes 为该轮明确注入的任何内容。

媒体附件作为单轮对话的输入内容进行处理：

- 图片可以直接附加到下一次模型调用中；如果当前使用的模型不支持直接处理图像，则会先将其分析为文本描述。
- 若启用了语音转文字功能，音频会被转录为文本。
- 文本文档会包含提取出的文本内容；其他类型的文档通常仅以保存的本地路径和简短说明的形式呈现。
- 附件路径以及提取/生成的文本可能会出现在对话记录中，但原始的图片、音频或二进制文件数据不会被重复复制到后续的提示词中。

例如，如果用户发送了一张图片并让 Hermes 用它制作表情包，Hermes 可能会使用视觉功能查看该图片一次，然后运行图像处理脚本。后续的对话不会自动将原始的 JPEG 文件纳入上下文，只会包含写入对话中的内容，比如用户的请求、简短的图片描述、本地缓存路径或助手的最终回复。

导致上下文体积增大的最常见原因并非媒体文件本身，而是冗长的文本：粘贴的对话记录、完整的日志、大量的工具输出、冗长的差异对比内容、重复的状态报告以及详细的调试信息。相比将大型文件直接复制到聊天中，建议使用摘要、文件路径、精选片段以及基于工具的查询方式。

:::tip
当会话变得过长时，可使用 `/compress` 命令进行压缩；如需开始新的对话线程，则使用 `/new` 命令；只有当您想从存储中删除已结束的旧会话时，才使用 `hermes sessions prune` 命令。压缩可以减少当前上下文的内容量，但并不等同于隐私删除操作。使用 `/new` 命令时可以指定一个名称（例如 `/new payments-refactor`），以便提前设置新会话的初始标题——这样之后就可以通过 `/resume <name>` 命令或 `/sessions` 选项卡轻松找到该会话。
:::

### 会话来源

每个会话都会标注其来源平台：

| 来源 | 描述 |
|--------|-------------|
| `cli` | 交互式 CLI（`hermes` 或 `hermes chat`） |
| `telegram` | Telegram 消息应用 |
| `discord` | Discord 服务器/私信 |
| `slack` | Slack 工作空间 |
| `whatsapp` | WhatsApp 消息应用 |
| `signal` | Signal 消息应用 |
| `matrix` | Matrix 房间及私信 |
| `mattermost` | Mattermost 频道 |
| `email` | 电子邮件（IMAP/SMTP） |
| `sms` | 通过 Twilio 发送的短信 |
| `dingtalk` | DingTalk 消息应用 |
| `feishu` | Feishu/Lark 消息应用 |
| `wecom` | WeCom（企业微信） |
| `weixin` | 微信（个人账号） |
| `bluebubbles` | 通过 BlueBubbles macOS 服务器传输的 Apple iMessage |
| `qqbot` | 通过官方 API v2 的腾讯 QQ 机器人 |
| `homeassistant` | Home Assistant 对话记录 |
| `webhook` | 接收的 webhook 请求 |
| `api-server` | API 服务器发起的请求 |
| `acp` | ACP 编辑器集成功能 |
| `cron` | 定时执行的 cron 作业 |
| `batch` | 批量处理任务 |

## 通过 CLI 继续会话

可以使用 `--continue` 或 `--resume` 参数从 CLI 继续之前的对话：

### 继续上一个会话

```bash
# Resume the most recent CLI session
hermes --continue
hermes -c

# Or with the chat subcommand
hermes chat --continue
hermes chat -c
```

该功能会从 SQLite 数据库中查找最新的 `cli` 会话，并加载其完整的对话历史记录。

### 按名称恢复会话

如果您已为某个会话设置了标题（详见下文的[会话命名](#session-naming)），则可以通过名称来恢复该会话：

```bash
# Resume a named session
hermes -c "my project"

# If there are lineage variants (my project, my project #2, my project #3),
# this automatically resumes the most recent one
hermes -c "my project"   # → resumes "my project #3"
```

### 恢复特定会话

```bash
# Resume a specific session by ID
hermes --resume 20250305_091523_a1b2c3d4
hermes -r 20250305_091523_a1b2c3d4

# Resume by title
hermes --resume "refactoring auth"

# Or with the chat subcommand
hermes chat --resume 20250305_091523_a1b2c3d4
```

退出 CLI 会话时，系统会显示会话 ID，您也可以通过命令 `hermes sessions list` 查看这些 ID。

### 恢复会话时的对话摘要

当您恢复会话时，Hermes 会在输入提示符之前的样式化面板中，简要展示上一次对话的摘要：

<img className="docs-terminal-figure" src={useBaseUrl('/img/docs/session-recap.svg')} alt="恢复 Hermes 会话时显示的、带有样式的上一次对话摘要面板预览。" />
<p className="docs-figure-caption">在返回实时输入界面之前，恢复模式会先展示一个简洁的摘要面板，列出最近的用户和助手消息。</p>

该摘要功能包括：
- 用**金色 `●`**标记**用户消息**，用**绿色 `◆`**标记**助手回复**
- 会对过长的消息进行**截断**（用户消息限 300 字符，助手消息限 200 字符或 3 行）
- 将**工具调用**汇总为包含工具名称的计数形式（例如：`[3 次工具调用：terminal, web_search]`）
- 会**隐藏**系统消息、工具结果以及内部推理过程
- 对最后 10 条消息进行**大写显示**，并标注“... 更早还有 N 条消息...”的提示
- 采用**浅色样式**，以便与当前正在进行的对话区分开来

如需禁用此摘要功能并恢复最简的单行显示模式，请在 `~/.hermes/config.yaml` 中进行相应设置：

```yaml
display:
  resume_display: minimal   # default: full
```

:::提示
会话 ID 的格式为 `YYYYMMDD_HHMMSS_<十六进制字符串>`——CLI/TUI 会话使用 6 位字符的十六进制后缀（例如 `20250305_091523_a1b2c3`），而网关会话则使用 8 位字符的后缀（例如 `20250305_091523_a1b2c3d4`）。您可以通过会话 ID（完整形式或唯一前缀）或对话标题来继续对话，这两种方式均支持与 `-c` 和 `-r` 参数一起使用。
:::

## 跨平台交接

在 CLI 会话中输入 `/handoff <平台名>`，即可将正在进行的对话转移到对应消息平台的主题频道中。智能体将从 CLI 停下的位置继续处理——保持相同的会话 ID、完整的角色感知型对话记录、工具调用信息等全部内容不变。

```bash
# Inside a CLI session
/handoff telegram
```

处理流程如下：

1. CLI会首先验证 `<platform>` 是否已启用且设置了主频道（需在目标聊天窗口中执行一次 `/sethome` 命令进行配置）。
2. 接着，CLI会将当前会话标记为待处理状态，并对网关进行**阻塞轮询**。如果智能体正处于回复过程中，CLI会拒绝处理请求，要求先等待当前回复完成。
3. 网关监控器随后接管会话控制，并向目标适配器请求创建一个新的讨论线程：
   - **Telegram**：开启一个新的论坛主题（若聊天窗口启用了Bot API 9.4+的“主题”模式，则为私信主题；否则为论坛超级群组主题）。
   - **Discord**：在主文本频道下创建一个1440分钟自动归档的讨论线程。
   - **Slack**：发布一条起始消息，并将该消息的 `ts` 时间戳作为讨论线程的锚点。
   - **WhatsApp / Signal / Matrix / SMS**：这些平台不支持原生讨论线程，因此会直接转而使用主频道。
4. 网关会将目标密钥重新绑定到您现有的CLI会话ID上，随后构造一个模拟的用户回复轮次，要求智能体进行确认与总结。该回复会被发送到新创建的讨论线程中。
5. 当网关反馈操作成功后，CLI会输出 `/resume` 指令提示，并正常退出程序。

   ```
   ↻ Handoff complete. The session is now active on telegram.
     Resume it on this CLI later with: /resume my-session-title
   ```

6. 从那时起，对话会保留在该平台上。只需在新的对话线程中回复即可——该频道内的所有授权用户均可共享同一会话，后续任何真实用户发送的消息也能无缝接入，因为该线程的会话密钥中不包含 `user_id`。

**返回 CLI 模式：** 当您想回到桌面端时，只需运行 `/resume <标题>`（或在终端中执行 `hermes -r "<标题>"`），即可从平台停止的位置继续操作。

**故障处理方式：**
- 未配置主频道 → CLI 会以 `/sethome` 的提示拒绝操作。
- 平台未启用/网关未运行 → CLI 会在 60 秒后超时，并显示明确提示信息，同时您的 CLI 会话仍保持完整。
- 对话线程创建失败（权限问题或主题模式关闭）→ 系统会直接切换到主频道并完成操作；虽然不存在线程隔离，但信息传递功能依然正常。
- `adapter.send` 发生故障（速率限制或临时 API 错误）→ 信息传递会被标记为失败并显示原因；相关记录会被清除，以便您重新尝试。

**需了解的局限性：** 对于那些不支持对话线程、但采用多用户群组主频道的平台，系统会将合成对话轮次视为类似私信的会话。这种机制适用于常规的自定义私信主频道，但不太适合真正的群聊场景。Telegram、Discord 和 Slack 等平台均支持对话线程——这属于最常见的使用场景——因此大多数情况下都不会遇到此问题。

## 会话命名

为会话设置易于识别的标题，以便方便查找和恢复。

### 自动生成的标题

在首次对话之后，Hermes 会自动为每个会话生成一个简短的描述性标题（3–7 个单词）。该功能通过后台线程及高效的辅助模型实现，因此不会增加延迟。您可以通过 `hermes sessions list` 或 `hermes sessions browse` 命令查看这些自动生成的标题。

每个会话仅会自动生成一次标题，如果您已手动设置过标题，则不会再生成。

### 手动设置标题

可在任何聊天会话中（无论是 CLI 模式还是网关模式）使用 `/title` 接口命令来设置标题：

```
/title my research project
```

标题会立即应用。如果该会话尚未在数据库中创建（例如，在发送第一条消息之前就调用了 `/title` 命令），则该请求会被暂存，待会话启动后才会应用。

您也可以通过命令行重命名现有的会话：

```bash
hermes sessions rename 20250305_091523_a1b2c3d4 "refactoring auth module"
```

### 标题规则

- **唯一性** — 两个会话不得使用相同的标题  
- **长度限制** — 最多100个字符，以确保列表显示整洁  
- **自动净化** — 会自动移除控制字符、零宽字符以及右到左排版相关字符  
- **支持常规Unicode字符** — 表情符号、CJK字符及带重音的字符均可使用  

### 压缩时的自动会话延续功能

当某个会话的上下文被压缩（通过 `/compress` 手动操作或自动压缩）时，Hermes会创建一个新的延续会话。如果原会话有标题，新会话将自动获得一个带序号的标题：

```
"my project" → "my project #2" → "my project #3"
```

当您通过项目名称恢复会话（`hermes -c "my project"`）时，系统会自动选择该项目历史记录中最新的会话。

### 在消息平台中使用 /title 命令

 `/title` 命令在所有网关平台（Telegram、Discord、Slack、WhatsApp）上均可使用：

- `/title My Research` — 设置会话标题
- `/title` — 显示当前标题

## 会话管理命令

Hermes 通过 `hermes sessions` 提供了一整套会话管理命令：

### 列出所有会话

```bash
# List recent sessions (default: last 20)
hermes sessions list

# Filter by platform
hermes sessions list --source telegram

# Show more sessions
hermes sessions list --limit 50
```

当会话带有标题时，输出结果会显示标题、预览内容以及对应的时间戳：

```
Title                  Preview                                  Last Active   ID
────────────────────────────────────────────────────────────────────────────────────────────────
refactoring auth       Help me refactor the auth module please   2h ago        20250305_091523_a
my project #3          Can you check the test failures?          yesterday     20250304_143022_e
—                      What's the weather in Las Vegas?          3d ago        20250303_101500_f
```

当会话没有标题时，会采用更简洁的格式：

```
Preview                                            Last Active   Src    ID
──────────────────────────────────────────────────────────────────────────────────────
Help me refactor the auth module please             2h ago        cli    20250305_091523_a
What's the weather in Las Vegas?                    3d ago        tele   20250303_101500_f
```

### 导出会话记录

```bash
# Export all sessions to a JSONL file
hermes sessions export backup.jsonl

# Export sessions from a specific platform
hermes sessions export telegram-history.jsonl --source telegram

# Export a single session
hermes sessions export session.jsonl --session-id 20250305_091523_a1b2c3d4
```

导出的文件中，每行包含一个 JSON 对象，其中记载了完整的会话元数据以及所有消息内容。

### 删除会话

```bash
# Delete a specific session (with confirmation)
hermes sessions delete 20250305_091523_a1b2c3d4

# Delete without confirmation
hermes sessions delete 20250305_091523_a1b2c3d4 --yes
```

### 重命名会话

```bash
# Set or change a session's title
hermes sessions rename 20250305_091523_a1b2c3d4 "debugging auth flow"

# Multi-word titles don't need quotes in the CLI
hermes sessions rename 20250305_091523_a1b2c3d4 debugging auth flow
```

如果该名称已被其他会话占用，则会显示错误提示。

### 清理旧会话

```bash
# Delete ended sessions older than 90 days (default)
hermes sessions prune

# Custom age threshold
hermes sessions prune --older-than 30

# Only prune sessions from a specific platform
hermes sessions prune --source telegram --older-than 60

# Skip confirmation
hermes sessions prune --older-than 30 --yes
```

:::info
“剪枝”功能仅会删除**已结束**的会话（即那些已被手动终止或自动重置的会话），活跃中的会话绝不会被删除。
:::

### 会话统计信息

```bash
hermes sessions stats
```

输出：

```
Total sessions: 142
Total messages: 3847
  cli: 89 sessions
  telegram: 38 sessions
  discord: 15 sessions
Database size: 12.4 MB
```

如需更深入的分析——包括令牌使用情况、成本估算、工具明细以及活动模式——请使用 [`hermes insights`](/reference/cli-commands#hermes-insights) 工具。

## 会话搜索工具

该智能体内置了 `session_search` 工具，它能够利用 SQLite 的 FTS5 引擎对所有历史对话进行全文搜索，并允许智能体逐条查看找到的任意会话内容。无需调用大型语言模型，无需总结，也无需截断处理。所有查询结果均为数据库中的原始消息。

### 三种调用方式

该工具会根据您设置的参数自动推断您的需求，无需指定 `mode` 参数。

**1. 搜索功能——传入 `query` 参数：**

```python
session_search(query="auth refactor", limit=3)
```

运行FTS5算法，通过会话链路对匹配结果进行去重，进而返回Top N个会话。每个结果包含以下字段：

- `session_id`、`title`、`when`、`source`
- `snippet` — 经FTS5算法高亮标注的匹配内容片段
- `bookend_start` — 该会话中前3条用户与助手的对话消息（即任务发起/开始部分）
- `messages` — FTS5匹配结果前后各5条对话消息，其中目标匹配消息会被特别标记
- `bookend_end` — 该会话中最后3条用户与助手的对话消息（即问题解决/决策部分）
- `match_message_id`、`messages_before`、`messages_after`

通过这些边界信息及指定窗口内的对话内容，无需获取完整对话记录即可还原“任务发起 → 匹配结果 → 问题解决”的完整流程。在真实的会话数据库上，处理时间通常为15–50毫秒。

**2. Scroll方式 — 传入`session_id`与`around_message_id`：**

```python
session_search(session_id="20260510_174648_805cc2", around_message_id=590803, window=10)
```

该功能会返回以锚点为中心、包含±`window`条消息的窗口范围。不支持FTS5机制，也不提供起始/结束边界消息——仅展示指定范围内的内容。在发现调用之后，当需要超出默认±5条消息范围的上下文信息时，可使用此功能。

- **向前进页**：将`messages[-1].id`作为`around_message_id`参数传回
- **向后退页**：将`messages[0].id`作为`around_message_id`参数传回
- 边界消息会作为定位标记同时出现在两个窗口中
- 当`messages_before`或`messages_after`的值小于`window`时，表示当前已处于会话的起始或结束位置

每次滚动调用的典型处理时间约为1–2毫秒。

**3. 浏览模式——无需参数：**

```python
session_search()
```

按时间顺序返回最近的会话记录（包含标题、预览内容及时间戳）。当用户未明确提及具体主题，仅询问“我之前在做什么”时，该功能非常有用。

### FTS5 查询语法

关键词模式支持标准的 FTS5 查询语法：

- 简单关键词：`docker deployment`（FTS5 默认采用 AND 逻辑）
- 短语查询：`"exact phrase"`
- 布尔运算：`docker OR kubernetes`、`python NOT java`
- 前缀匹配：`deploy*`

### 可选参数

- `sort` — `newest` 或 `oldest`，在 FTS5 排序结果之上再进一步排序。如需仅按相关性排序（默认值，适用于探索性检索），可省略该参数；对于“我们上次停留在哪里”的问题使用 `newest`，对于“X 是如何开始的”问题则使用 `oldest`。
- `role_filter` — 用逗号分隔需要包含的角色。默认情况下，Discovery 功能仅考虑 `user,assistant` 角色（工具输出通常属于干扰信息）。如需包含工具输出以调试工具行为，可设置 `user,assistant,tool`；如仅需搜索工具输出，则设置为 `tool`。

### 使用场景

系统会自动提示智能体使用会话搜索功能：

> “当用户提及过往对话中的内容，或您怀疑存在相关历史上下文时，请先使用 session_search 检索相关信息，再要求用户重复说明。”

常见触发场景包括：“我们之前做过这个”、“还记得吗”、“上次……”、“正如我之前提到的”，或是任何涉及当前对话窗口之外项目/人员/概念的提及。

## 各平台的会话跟踪机制

### 网关会话

在消息平台上，会话通过由消息来源生成的确定性会话键来标识：

| 聊天类型 | 默认键格式 | 行为规则 |
|-----------|--------------|----------|
| Telegram 私信 | `agent:main:telegram:dm:<chat_id>` | 每条私信对话对应一个独立会话 |
| Discord 私信 | `agent:main:discord:dm:<chat_id>` | 每条私信对话对应一个独立会话 |
| WhatsApp 私信 | `agent:main:whatsapp:dm:<canonical_identifier>` | 每位私信用户对应一个独立会话（若存在映射关系，LID/电话号码别名将合并为一个身份） |
| 群组聊天 | `agent:main:<platform>:group:<chat_id>:<user_id>` | 当平台提供用户 ID 时，群组内每个用户对应一个独立会话 |
| 群组主题帖 | `agent:main:<platform>:group:<chat_id>:<thread_id>` | 默认情况下，所有主题帖参与者共享同一个会话；若设置 `thread_sessions_per_user: true`，则每位用户拥有独立会话 |
| 频道聊天 | `agent:main:<platform>:channel:<chat_id>:<user_id>` | 当平台提供用户 ID 时，频道内每个用户对应一个独立会话 |

当 Hermes 无法获取共享聊天中的参与者标识时，它会为该聊天室创建一个共享会话。

### 共享会话与独立会话

默认情况下，`config.yaml` 中的 `group_sessions_per_user` 设置为 `true`。这意味着：

- Alice 和 Bob 可以在同一个 Discord 频道中分别与 Hermes 对话，而无需共享对话记录
- 某位用户长时间进行的复杂工具操作不会影响另一位用户的上下文窗口
- 由于运行中的智能体键与独立会话键一致，中断处理也能针对每位用户单独进行

如果您希望使用共享的“群组大脑”机制，可进行相应设置：

```yaml
group_sessions_per_user: false
```

这会将群组/频道恢复为每个房间一个共享会话的模式，从而保留对话的上下文信息，同时也能共享令牌成本、中断状态以及上下文数据量。

### 会话重置策略

网关会话会根据可配置的策略自动重置：

- **idle** — 静止 N 分钟后重置
- **daily** — 每天固定时间点重置
- **both** — 以先满足的条件为准（静置或每日定时）
- **none** — 不会自动重置

在会话自动重置之前，智能体会有机会保存对话中的重要记忆或技能信息。

无论采用何种策略，只要存在**正在运行的后台进程**，该会话就绝不会被自动重置。

## 存储位置

| 内容 | 路径 | 说明 |
|------|------|------|
| SQLite 数据库 | `~/.hermes/state.db` | 所有会话元数据及消息，采用 FTS5 进行索引 |
| 网关消息 | `~/.hermes/state.db` | SQLite —— 所有会话消息的标准化存储方式 |
| 网关路由索引 | `~/.hermes/sessions/sessions.json` | 将会话键映射到对应的活跃会话 ID（包含来源元数据及过期标志） |

SQLite 数据库采用 WAL 模式，支持多个读取进程和单个写入进程，非常适合网关的多平台架构。

:::note 旧版 JSONL 转录文件
在 `state.db` 成为标准存储格式之前创建的会话，可能在 `~/.hermes/sessions/` 目录下留下一些 `*.jsonl` 文件。Hermes 已不再读取或写入这些文件。在确认对应的会话已存在于 `state.db` 中后，可安全删除它们。
:::

### 数据库结构

`state.db` 中的关键表包括：

- **sessions** — 会话元数据（ID、来源、用户 ID、模型类型、标题、时间戳、令牌计数）。标题具有唯一索引（允许为空，但非空标题必须唯一）。
- **messages** — 完整的消息历史记录（发送方角色、内容、工具调用信息、工具名称、令牌计数）
- **messages_fts** — 用于对消息内容进行全文搜索的 FTS5 虚拟表

## 会话过期与清理

### 自动清理机制

- 网关会话会根据配置的策略自动重置
- 在重置之前，智能体会先保存即将过期的会话中的记忆和技能信息
- 可选的自动清理功能：当 `sessions.auto_prune` 设置为 `true` 时，那些已结束且超过 `sessions.retention_days`（默认为 90 天）的会话，会在 CLI 或网关启动时被自动删除
- 在实际删除了相关记录后，系统会对 `state.db` 执行 `VACUUM` 操作以释放磁盘空间（SQLite 在普通 DELETE 操作时不会自动缩小文件大小）
- 自动清理最多每 `sessions.min_interval_hours`（默认为 24 小时）执行一次；最近一次清理的时间戳会存储在 `state.db` 中，因此同一 `HERMES_HOME` 下的所有 Hermes 进程都能共享该信息

默认情况下此功能是**关闭**的——会话历史对于 `session_search` 检索功能非常重要，若擅自删除可能会让用户感到意外。如需启用该功能，请在 `~/.hermes/config.yaml` 中进行设置：

```yaml
sessions:
  auto_prune: true          # opt in — default is false
  retention_days: 90        # keep ended sessions this many days
  vacuum_after_prune: true  # reclaim disk space after a pruning sweep
  min_interval_hours: 24    # don't re-run the sweep more often than this
```

无论会话已存在多久，活跃会话都绝不会被自动清理。

### 手动清理

```bash
# Prune sessions older than 90 days
hermes sessions prune

# Delete a specific session
hermes sessions delete <session_id>

# Export before pruning (backup)
hermes sessions export backup.jsonl
hermes sessions prune --older-than 30 --yes
```

:::提示
该数据库的增长速度较慢（通常数百个会话的容量为10-15 MB），且会话历史记录是实现`session_search`功能、检索过往对话内容的关键，因此系统默认禁用了自动清理功能。如果您运行的网关或定时任务负载较重，且`state.db`文件对性能产生了显著影响（实际观察到的问题表现为：当会话数达到约1000个时，`state.db`容量可达384 MB，从而导致FTS5插入操作及 `/resume` 查询功能变慢），则建议启用此功能。如需进行一次性清理，可无需开启自动清理功能，直接使用`hermes sessions prune`命令。
