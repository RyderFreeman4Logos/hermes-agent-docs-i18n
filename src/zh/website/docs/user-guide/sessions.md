---
sidebar_position: 7
title: "Sessions"
description: "Session persistence, resume, search, management, and per-platform session tracking"
---

import useBaseUrl from '@docusaurus/useBaseUrl';

# 会话

Hermes Agent 会自动将每次对话保存为一个会话。通过会话功能，可以实现对话续接、跨会话搜索以及完整的对话历史管理。

## 会话的工作原理

无论是通过 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Teams 还是其他任何消息平台进行的对话，都会被作为包含完整消息历史的会话存储下来。这些会话会被记录在以下位置：

1. **SQLite 数据库**（`~/.hermes/state.db`）——包含结构化的会话元数据及 FTS5 全文搜索功能，以及完整的消息历史记录

SQLite 数据库中存储的内容包括：
- 会话 ID、来源平台、用户 ID
- **会话标题**（唯一且易于识别的名称）
- 模型名称及配置参数
- 系统提示词快照
- 完整的消息历史记录（包括发送方角色、消息内容、工具调用信息及工具返回结果）
- 令牌数量（输入/输出）
- 时间戳（开始时间、结束时间）
- 上级会话 ID（用于基于压缩需求拆分会话）

### 什么会被纳入上下文

Hermes 会保存会话历史以便实现对话续接，但不会重复发送所有已处理过的内容。在每一轮对话中，模型只能看到选定的系统提示词、当前的对话窗口，以及 Hermes 为该轮特意添加的任何内容。

媒体附件则被视为当前轮次内的输入内容进行处理：

- 图片可以直接附加在后续的模型调用中，或者当当前使用的模型不支持直接处理视觉信息时，可先被分析为文本描述。
- 若配置了语音转文字功能，音频将会被转录为文本。
- 文本文档可直接包含其中提取出的文本；而其他类型的文档则通常通过保存的本地路径及简短说明来表示。
- 附件路径以及提取或生成的文本会出现在对话记录中，但原始的图片、音频或二进制文件数据不会被重复复制到后续的提示词中。

例如，如果用户发送一张图片并让Hermes据此制作表情包，Hermes可能会先用视觉功能查看一次该图片，然后运行图像处理脚本。在后续的对话中，上下文不会自动包含原始的JPEG文件，而只会保留对话中记录的内容，比如用户的请求、简短的图片描述、本地缓存路径或助手的最终回复。

导致上下文内容不断增多的最常见原因并非媒体文件本身，而是冗长的文本：粘贴的对话记录、完整的日志、大量的工具输出、冗长的差异对比内容、反复出现的状态报告以及详细的错误信息。相比将大量原始数据复制到聊天中，建议使用摘要、文件路径、精选摘录以及基于工具的查询结果。

:::提示  
当会话时间过长时，可使用 `/compress` 命令进行压缩；如需开启新线程，则使用 `/new` 命令。而只有当您想从存储中删除已结束的旧会话时，才应使用 `hermes sessions prune` 命令。如果只是因为 `state.db` 文件体积过大，建议先尝试非破坏性方案：`hermes sessions optimize` 命令可以合并 FTS5 索引段并对数据库执行 VACUUM 操作，且不会影响任何会话数据。压缩功能仅能减少当前活跃的上下文量，并不构成隐私数据的删除。在调用 `/new` 命令时可传入名称参数（例如 `/new payments-refactor`），以便预先设置新会话的标题——这有助于日后通过 `/resume <name>` 命令或“会话选择器”快速找到该会话。  
:::

### 会话来源  

每个会话都会标注其来源平台：

| 来源 | 描述 |
|------|------|
| `cli` | 交互式命令行界面（`hermes` 或 `hermes chat`） |
| `telegram` | Telegram 消息应用 |
| `discord` | Discord 服务器/私信 |
| `slack` | Slack 工作空间 |
| `whatsapp` | WhatsApp 消息应用 |
| `signal` | Signal 消息应用 |
| `matrix` | Matrix 房间及私信 |
| `mattermost` | Mattermost 频道 |
| `email` | 电子邮件（IMAP/SMTP） |
| `sms` | 通过 Twilio 发送短信 |
| `dingtalk` | DingTalk 消息应用 |
| `feishu` | Feishu/Lark 消息应用 |
| `wecom` | WeCom（企业微信） |
| `weixin` | 微信（个人账号） |
| `bluebubbles` | 通过 BlueBubbles macOS 服务器发送 Apple iMessage |
| `qqbot` | 通过官方 API v2 的 QQ 客户端 |
| `homeassistant` | Home Assistant 对话功能 |
| `webhook` | 接收外部 webhook 请求 |
| `api-server` | API 服务器请求 |
| `acp` | ACP 编辑器集成 |
| `cron` | 定时执行的 cron 任务 |
| `batch` | 批量处理操作 |

## CLI 会话续接

使用 `--continue` 或 `--resume` 从命令行界面续接之前的对话：

### 继续上一次会话 |

```bash
# Resume the most recent CLI session
hermes --continue
hermes -c

# Or with the chat subcommand
hermes chat --continue
hermes chat -c
```

该功能会从 SQLite 数据库中查找最新的 `cli` 会话，并加载其完整的对话历史记录。

#### 按终端继续

单独使用 `-c` 时会考虑终端环境：每个 CLI 会话都会在 `~/.hermes/terminal-sessions/` 目录下生成一个小型标记文件，该文件的键值为对应的终端类型（如 tty 设备、tmux 分区、kitty 窗口、wezterm 分区、Zellij 分区、Windows Terminal 会话等）。当您在*同一*终端中再次运行 `hermes -c` 时，Hermes 会恢复该终端的专属会话——这样并排的两个分区各自都能继续对话，而不会都使用全局最新的会话。如果该终端没有标记文件（首次使用、会话已被删除，或标记文件已超过30天未更新），则 `-c` 会回退到使用最新会话的模式。`-c "名称"` 和 `--resume` 的功能不受影响。您可以通过在 `config.yaml` 中设置 `session.terminalcontinue: false` 来禁用此功能。

### 按名称恢复

如果您为某个会话设置了标题（详见下文的[会话命名](#session-naming)），则可以通过名称来恢复该会话：

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

# Resume the most recent session — same lookup as -c
hermes --resume latest

# Or with the chat subcommand
hermes chat --resume 20250305_091523_a1b2c3d4
```

当您退出 CLI 会话时，系统会显示会话 ID，您也可以使用 `hermes sessions list` 命令来查看它们。

:::note
`latest` 是 `--resume` 参数的保留关键字。即使存在名为 “latest” 的会话，仍可通过其 ID 或使用 `-c latest`（基于标题匹配）来访问该会话。
:::

### 在指定目录中继续运行

在启动或恢复会话之前，可通过传递 `--in <dir>` 参数切换到目标目录。结合使用 `--resume latest`（或 `-c`）后，系统会自动选择该目录工作空间中最新的会话——这样就不必先执行 `cd` 命令，也不需要记住会话 ID：

```bash
# Resume the latest session that belongs to ./my-project
hermes --resume latest --in ./my-project

# Works with the TUI too
hermes --tui --resume latest --in ./my-project
```

`--in` 参数还会将会话固定在该目录中：已恢复的会话所记录的工作目录不会被还原（效果等同于使用了 `--no-restore-cwd` 参数）。

### 恢复时会重置工作目录

恢复 CLI 会话时，系统还会自动切换回该会话所记录的工作目录（即其 Git 仓库根目录或项目目录），这样对话就能在原来的工作空间中继续进行。如果您希望保持当前所在位置，请使用 `--no-restore-cwd` 参数：

```bash
hermes --resume 20250305_091523_a1b2c3 --no-restore-cwd
```

当出现 `↪ restored workspace dir: …` 这一行时，即表示切换已完成。恢复失败不会影响恢复过程的继续进行。

### 按工作区筛选会话

`hermes sessions list` 命令支持使用 `--workspace <needle>` 参数，仅显示那些工作区键（Git 仓库根目录或当前工作目录）与之匹配的会话——匹配条件可以是路径子串或完全一致的目录名称。

```bash
hermes sessions list --workspace my-project
hermes sessions list --workspace ~/code/hermes-agent
```

### 恢复会话时的对话摘要

当您恢复会话时，Hermes 会在输入提示符之前的样式化面板中展示先前对话的简短摘要：

<img className="docs-terminal-figure" src={useBaseUrl('/img/docs/session-recap.svg')} alt="恢复 Hermes 会话时显示的先前对话摘要面板的样式化预览。" />
<p className="docs-figure-caption">在返回实时输入界面之前，恢复模式会先展示一个简短的摘要面板，列出最近的用户和助手发言内容。</p>

该摘要功能包含以下特点：
- **用户消息**以金色 `●` 标示，**助手回复**以绿色 `◆` 标示
- 会对过长的消息进行**截断处理**（用户消息限300字符，助手消息限200字符或3行）
- **工具调用**会汇总为包含工具名称的计数形式（例如：`[3次工具调用：terminal, web_search]`）
- 会**隐藏**系统消息、工具结果及内部推理过程
- 最后10条对话会被**标上大写符号**，并显示“... 更早还有N条消息...”的提示
- 采用**暗色样式**，以便与当前正在进行的对话区分开来

如需禁用此摘要功能并保持最简的单行显示模式，请在 `~/.hermes/config.yaml` 中进行相应设置：

```yaml
display:
  resume_display: minimal   # default: full
```

:::提示
会话 ID 的格式为 `YYYYMMDD_HHMMSS_<十六进制字符串>`——CLI/TUI 会话使用 6 位字符的十六进制后缀（例如 `20250305_091523_a1b2c3`），而网关会话则使用 8 位字符的后缀（例如 `20250305_091523_a1b2c3d4`）。您可以通过会话 ID（完整形式或唯一前缀）或对话标题来继续对话，这两种方式均支持与 `-c` 和 `-r` 参数一起使用。
:::

## 跨平台交接

在 CLI 会话中输入 `/handoff <平台名>`，即可将正在进行的对话转移到对应消息平台的频道中。智能体将从 CLI 中停止的位置继续处理——保持相同的会话 ID、完整的角色感知型对话记录、工具调用信息等全部内容不变。

```bash
# Inside a CLI session
/handoff telegram
```

具体流程如下：

1. CLI会首先验证 `<platform>` 是否已启用且设置了主频道（需在目标聊天窗口中执行一次 `/sethome` 命令进行配置）。
2. 接着，CLI会将当前会话标记为待处理状态，并对网关进行**阻塞轮询**。如果智能体正处于回复途中，系统会拒绝处理请求，需等待其当前回复完成。
3. 网关监控模块随后接管对话流转，并向目标适配器请求创建一个新的讨论线程：
   - **Telegram**：创建一个新的论坛主题（若聊天窗口启用了Bot API 9.4+的“主题”模式，则为私信主题；否则为论坛超级群组主题）。
   - **Discord**：在主文本频道下创建一个1440分钟自动归档的讨论线程。
   - **Slack**：发布一条起始消息，并将该消息的 `ts` 时间戳作为讨论线程的锚点。
   - **WhatsApp / Signal / Matrix / SMS**：这些平台不支持原生讨论线程，因此会直接转至主频道处理。
4. 网关会将目标密钥重新绑定到您当前的CLI会话ID上，随后构造一个模拟的用户回复轮次，要求智能体进行确认并总结内容。该回复将会发布到新创建的讨论线程中。
5. 当网关反馈操作成功后，CLI会输出 `/resume` 指令提示，并正常退出程序。

   ```
   ↻ Handoff complete. The session is now active on telegram.
     Resume it on this CLI later with: /resume my-session-title
   ```

6. 从那时起，对话会保留在该平台上。您可以在新的讨论线程中回复——该频道内的任何授权用户都能共享同一会话，后续在该线程中发送的实时用户消息也能无缝接入，因为这些消息不包含 `user_id`，因此不会影响会话状态。

**返回 CLI 模式：** 当您想回到桌面端时，只需运行 `/resume <title>`（或在终端中执行 `hermes -r "<title>"`），即可从平台上次停止的位置继续操作。

**可能出现的故障情况：**
- 未配置主频道 → CLI 会通过提示信息 `/sethome` 告知您需进行配置。
- 网关未运行（没有程序处理请求）→ CLI 会在 60 秒后超时，并显示明确提示，同时您的 CLI 会话状态依然保持完整。
- 数据传输缓慢：一旦网关接管会话，它会通过真实智能体的响应来重新播放整个会话内容，对于较长的会话而言，这一过程可能需要几分钟时间。CLI 会显示“仍在传输中...”的进度提示，并持续等待最长 15 分钟——它绝不会将传输缓慢的情况误报为“网关未运行”。
- 讨论线程创建失败（权限问题或主题模式关闭）→ 系统会直接切换到主频道并完成操作；虽然缺乏线程隔离功能，但会话传递本身仍可正常进行。
- `adapter.send` 发生故障（速率限制或临时的 API 错误）→ 会话传递会被标记为失败，并显示具体原因；相关记录会被清除，以便您重新尝试。
**需了解的局限性：** 对于不支持线程功能、但具备多用户群组频道平台的系统，合成对话轮次会以私信模式呈现。这种方式适用于独立的私信型群组频道（即常见配置），但不太适合真正需要共享的群聊场景。而 Telegram、Discord 和 Slack 等平台均支持线程功能——这正是最常见的使用场景——因此大多数情况下都不会遇到此问题。

## 会话命名

为会话设置易于理解的标题，以便轻松查找和恢复会话。

### 自动生成的标题

在首次对话之后，Hermes 会自动为每个会话生成一个简短的描述性标题（3–7个单词）。该功能通过后台线程及高效的辅助模型实现，因此不会增加任何延迟。您可以通过 `hermes sessions list` 或 `hermes sessions browse` 命令查看这些自动生成的标题。

每个会话仅会自动生成一次标题；如果您已手动设置标题，则不会再次生成。

### 手动设置标题

可在任意聊天会话中（无论是 CLI 还是网关）使用 `/title` 接口命令来设置标题：

```
/title my research project
```

标题会立即应用。如果该会话尚未在数据库中创建（例如，在发送第一条消息之前就调用了 `/title` 命令），则该操作会被排队，待会话启动后才会应用。

您也可以通过命令行重命名现有的会话：

```bash
hermes sessions rename 20250305_091523_a1b2c3d4 "refactoring auth module"
```

### 标题规则

- **唯一性** — 两个会话不得使用相同的标题
- **长度限制** — 最多100个字符，以确保列表显示整洁
- **自动净化** — 会自动移除控制字符、零宽字符以及右到左排版相关的特殊字符
- **支持普通Unicode字符** — 表情符号、CJK字符及带重音的字符均可正常使用

### 压缩时的自动会话延续功能

当某个会话的上下文被压缩（通过 `/compress` 手动操作或自动压缩）时，Hermes会创建一个新的会话来延续该任务。如果原会话有标题，新会话将自动获得一个带编号的标题：

```
"my project" → "my project #2" → "my project #3"
```

当您通过项目名称启动任务（`hermes -c "my project"`）时，系统会自动选择该项目历史记录中最新的会话。

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

### 导出会话

`hermes sessions export` 是针对每种导出格式的命令入口，可通过 `--format` 参数进行选择：

| 格式 | 输出内容 | 适用场景 |
|------|----------|----------|
| `jsonl`（默认） | 每个会话一个 JSON 对象 | 备份、在不同设备间传输 |
| `md` / `qmd` | 每个会话一个 Markdown/Quarto 文件 + 元数据文件 | 可读性强的归档、笔记记录 |
| `html` | 单页独立文件（多会话时包含侧边栏） | 共享、浏览 |
| `trace` | Claude Code 格式的 JSONL | HF Agent Trace Viewer，配合 `--upload` 使用 |

此外还支持 `--only user-prompts` 参数，仅导出用户输入的提示词内容（格式为 jsonl 或 md）。

所有格式都支持相同的筛选参数：`--session-id` 用于选择单个会话，或使用完整的 `prune`/`archive` 筛选集进行批量操作——包括 `--older-than` / `--newer-than` / `--before` / `--after`（时间范围可指定为 `5h`/`2d`/`1w`、具体天数或 ISO 时间戳）、`--source`、`--title`、`--model`、`--provider`、`--cwd`、`--min/--max-messages`、`--min/--max-tokens`、`--min/--max-cost`、`--min/--max-tool-calls`、`--user`、`--chat-id`、`--chat-type`、`--branch`、`--end-reason`。`--dry-run` 参数可预览筛选结果而不会实际写入文件。`--redact` 参数可用于从任何格式的导出内容中删除敏感信息（如 API 密钥、令牌、凭证），建议用于需要共享的文件。注意：批量筛选仅作用于已结束的会话；未加筛选的 `export` 命令会导出所有会话内容，包括正在进行的会话。

#### JSONL（默认格式）

```bash
# Export all sessions to a JSONL file
hermes sessions export backup.jsonl

# Export sessions from a specific platform
hermes sessions export telegram-history.jsonl --source telegram

# Export a single session
hermes sessions export session.jsonl --session-id 20250305_091523_a1b2c3d4

# Redact API keys/tokens/credentials from the exported content
hermes sessions export backup.jsonl --redact
```

导出的文件中，每一行都包含一个 JSON 对象，其中记载了完整的会话元数据以及所有消息内容。

#### HTML 格式

使用 `--format html` 选项可生成一个独立的 HTML 文件——无需任何外部依赖——该文件具备样式化的消息气泡、可折叠的工具输出功能；对于多会话导出场景，还配有侧边栏以便在不同会话之间切换：

```bash
# One session as a standalone HTML page
hermes sessions export --format html --session-id 20250305_091523_a1b2c3d4 transcript.html

# All Telegram sessions from the last week in one file, secrets redacted
hermes sessions export --format html --newer-than 1w --source telegram --redact archive.html
```

#### 仅输出提示词

`--only user-prompts` 选项仅导出您输入的提示词内容——不包含助手的回复、工具的输出以及系统上下文。该功能适用于构建提示词库或查看您曾提出的请求内容：

```bash
# One JSONL record per prompt (session id, index, timestamp, text)
hermes sessions export prompts.jsonl --session-id 20250305_091523_a1b2c3d4 --only user-prompts

# Markdown, straight to stdout
hermes sessions export - --session-id 20250305_091523_a1b2c3d4 --only user-prompts --format md
```

支持使用 `--format jsonl`（默认值）或 `md` 格式，批量导出时同样适用相同的过滤规则，同时可与 `--redact` 选项结合使用。

#### 推理过程记录（HF Agent Trace Viewer）

使用 `--format trace` 选项可输出 Claude Code JSONL 格式的数据——这正是 Hugging Face Hub 在其 [Agent Trace Viewer](https://huggingface.co/docs/hub/agent-traces) 中自动识别的数据格式。您可以将这些数据保存到本地，或添加 `--upload` 选项将其上传到您自己的私有 `hermes-traces` 数据集中（该操作会读取 `HF_TOKEN`）：

```bash
# Trace of the most recent session, to stdout
hermes sessions export --format trace

# One session to a local trace file
hermes sessions export --format trace --session-id 20250305_091523_a1b2c3d4 trace.jsonl

# Upload straight to your private HF traces dataset
hermes sessions export --format trace --session-id 20250305_091523_a1b2c3d4 --upload
```

默认情况下，追踪数据导出内容会经过机密信息脱敏处理（因其本应离开服务器）；在人工审核之后，可使用 `--no-redact` 选项取消脱敏。除非指定了 `--public`，否则 `--upload` 选项所对应的导出内容为私有格式。通过过滤器进行批量追踪数据导出时，每次会生成一个 `<id>.trace.jsonl` 文件。

#### Markdown / QMD 格式

若希望在隐藏或删除旧会话之前保留可读的基于文件的存档，可使用 `--format md` 或 `--format qmd` 选项。采用 Markdown/QMD 格式导出时，每个会话会对应一个文件，这些文件会被保存在指定目录中（默认路径为 `~/.hermes/session-exports`）。

```bash
# Export one session to Markdown
hermes sessions export --format md --session-id 20250305_091523_a1b2c3d4

# Export a compression lineage as one logical document
hermes sessions export --format md --session-id 20250305_091523_a1b2c3d4 --lineage logical

# Preview ended sessions older than 90 days without writing files
hermes sessions export --format md --older-than 90 --dry-run

# Export ended Telegram sessions older than 2 weeks to QMD files
hermes sessions export --format qmd --older-than 2w --source telegram

# Export long Claude sessions, secrets redacted
hermes sessions export --format md --model sonnet --min-messages 50 --redact

# Only after verification, export and delete one explicitly named session
hermes sessions export --format md --session-id 20250305_091523_a1b2c3d4 --delete-after-verified --yes
```

在通过 Markdown/QMD 格式导出时，每个导出的会话都会生成一个 `.md` 或 `.qmd` 文件，同时还会生成一个 `manifest.jsonl` 文件，其中包含文件路径、消息数量、调用链 ID 以及 SHA-265 哈希值。批量导出至少需要应用一个筛选条件，否则将无法执行；仅进行纯批量导出的操作会被拒绝。`--delete-after-verified` 选项仅能与 `--session-id` 一起使用，并且必须搭配 `--yes` 参数。由于删除父会话的同时也会移除其下属的代理/子代理会话，因此该模式会在删除任何内容之前，将每个代理单独导出并进行验证。如果在导出过程中代理集合发生了变化，系统将拒绝执行删除操作。`--redact` 选项会在写入文件之前从消息内容和工具输出中删除敏感信息（如 API 密钥、令牌和凭证），对于任何计划共享的导出内容，均建议使用此选项。

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

### 固定会话

“固定”功能会设置一个永久性的“保留”标记：被固定的会话不会被纳入`sessions.auto_archive`的过期清理范围，且始终会显示在列表中。这一标记与桌面侧边栏的“已固定”区域所使用的标记相同——无论通过哪种界面进行固定，双方都能看到该标记。

```bash
# Pin one or more sessions (unique ID prefixes work)
hermes sessions pin 20250305_091523_a1b2c3d4
hermes sessions pin 20250305 20250306

# Remove the pin
hermes sessions unpin 20250305_091523_a1b2c3d4

# List pinned sessions
hermes sessions pinned

# Machine-readable output, e.g. for a nightly backup of your pin set
hermes sessions pinned --json > pinned-sessions.json
```

### 清理旧会话

```bash
# Delete ended sessions inactive for 90 days (default)
hermes sessions prune

# Custom age threshold — bare numbers are days
hermes sessions prune --older-than 30

# Durations work too: 5h, 30m, 2d, 1w
hermes sessions prune --older-than 12h

# Delete only a specific time window (e.g. a batch of test sessions
# created in the last 5 hours)
hermes sessions prune --newer-than 5h

# Explicit window with absolute timestamps
hermes sessions prune --after "2026-07-05 09:00" --before "2026-07-05 14:30"

# Only prune sessions from a specific platform (all ages — any filter
# disables the implicit 90-day default)
hermes sessions prune --source telegram
hermes sessions prune --source cron --older-than 60   # add a time flag to narrow

# More filters — all AND together
hermes sessions prune --newer-than 5h --title "smoke test"   # title substring
hermes sessions prune --older-than 30 --max-messages 3        # tiny sessions
hermes sessions prune --cwd ~/scratch --end-reason done       # by cwd / end reason
hermes sessions prune --model gpt-5 --older-than 1w           # by model (substring)
hermes sessions prune --provider openrouter --older-than 60   # by billing provider
hermes sessions prune --branch feature/old-experiment         # by git branch
hermes sessions prune --user 12345678 --chat-type group       # by messaging origin
hermes sessions prune --max-tokens 500 --older-than 7         # by token usage
hermes sessions prune --max-cost 0.01 --max-tool-calls 0      # cheap, tool-less runs

# Preview what would be deleted, without deleting anything
hermes sessions prune --newer-than 5h --dry-run

# Skip confirmation
hermes sessions prune --older-than 30 --yes
```

时间值（`--older-than`、`--newer-than`、`--before`、`--after`）可以接受时长形式（如 `5h`、`30m`、`2d`、`1w`）、纯数字形式的天数，或是 ISO 时间戳格式（如 `2026-07-05`、`2026-07-05 14:30`）。`--older-than`/`--before` 用于设置上限，而 `--newer-than`/`--after` 用于设置下限。`--older-than`/`--newer-than` 组会以最新的消息活动时间作为判断依据（若会话为空，则回退至会话开始时间）；`--before`/`--after` 则直接以会话开始时间为依据。可通过组合任意一对参数来定义时间范围。

属性过滤器包括：`--source`（平台，需完全匹配）、`--title` / `--model` / `--branch`（不区分大小写的子字符串匹配）、`--provider`（计费服务提供商，需完全匹配）、`--end-reason`、`--user`、`--chat-id`、`--chat-type`（需完全匹配）、`--cwd`（路径前缀），此外还有数值范围限制参数：`--min/--max-messages`、`--min/--max-tokens`（输入+输出总量）、`--min/--max-cost`（单位为美元，实际费用优先，若无法获取则使用估算值），以及 `--min/--max-tool-calls`。一旦使用了任意过滤器，系统将不再适用默认的90天限制，因此执行 `hermes sessions prune --source cron` 或 `--model gpt-4o` 时会匹配所有年龄段的会话——需添加时间参数来缩小范围。只有完全不指定任何参数的 `hermes sessions prune` 命令才会保留90天的时间限制。每次非 `--yes` 模式下的执行都会先显示匹配数量以及最旧和最新的匹配会话，然后再询问用户是否确认。

默认情况下，已归档的会话会被跳过；如需同时删除这些会话，请使用 `--include-archived` 参数。

:::info
“清理”操作仅会删除**已结束**的会话（即那些已被明确终止或自动重置的会话），活跃中的会话绝不会被删除。:::

### 批量归档会话

如果您希望在不删除任何内容的情况下将某些会话移出列表，可使用 `hermes sessions archive` 命令。该命令与 `prune` 命令使用相同的筛选条件，但会将匹配的会话以“隐藏”方式处理（设置与通过桌面端/控制台界面单独归档会话相同的标记——消息和搜索功能依然保持完整）。

```bash
# Archive everything from the last 5 hours (e.g. 75 CI smoke-test sessions)
hermes sessions archive --newer-than 5h

# Archive by title substring, preview first
hermes sessions archive --title "dry run" --dry-run
hermes sessions archive --title "dry run" --yes
```

至少需要设置一个筛选条件——仅使用 `hermes sessions archive` 命令是无法将您的全部会话历史记录进行归档的。已归档的会话不会显示在 `hermes sessions list` 及 `/resume` 功能中，但仍然存储在数据库中，您可以通过桌面端或控制面板的会话列表将其解压恢复。 

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

如需更深入的分析——包括令牌使用情况、成本估算、工具使用明细以及活动模式等——请使用 [`hermes insights`](/reference/cli-commands#hermes-insights) 工具。

### 修复丢失路由标识的网关会话

如果某个网关对话在重启后“回退到过去”，重新开始几天前的话题，仿佛之前的消息从未出现过，那么该实时对话可能会被困在失去路由标识的会话行中（这一问题已在 v0.21 版本的会话连续性功能中得到修复；当前版本通过设计机制避免了此类情况，并能在运行时自动恢复）。

`hermes sessions repair-routing` 工具可查找那些没有路由标识且包含消息的会话行，并将它们重新关联到其正在继续的对话中——但前提是相关证据必须十分明确：

```bash
# Report only — shows each orphan, the proposed adoption, and the evidence
hermes sessions repair-routing

# Perform the adoptions (stop the gateway first — a running gateway holds
# the old routing in memory and would write it back over the repair)
hermes sessions repair-routing --apply

# Widen/narrow the contiguity window (default 900 seconds)
hermes sessions repair-routing --max-gap-seconds 300
```

证据规则：

- **传承关系**——孤立会话的 `parent_session_id` 指向同一平台中某条带键记录的会话行（该记录为已存事实，无需时间范围限制）；
- **连续性**——在孤立会话开始的时间窗口内，同一平台中恰好只有一条带键记录处于静默状态。

若出现任何歧义情况（如存在两个候选前序会话、有两个孤立会话均指向同一个前序会话），系统会说明原因并保持原状——错误的关联操作会导致一个对话被错误地合并到另一个聊天流中。被替代的记录会通过 `superseded_by_repair` 标记并退役，因此重启恢复流程也无法将其重新启用。

修复功能**刻意不设置自动模式**：如果该聊天流此后又产生了新的对话历史，由您来决定继续沿用哪条对话线程。无论采用何种方式，被搁置的对话均可通过 `/resume` 命令或会话搜索功能继续查看——只有对话路由会发生改变。请先进行备份（`cp ~/.hermes/state.db ~/.hermes/state.db.bak`）。

## 从 Claude Code 和 Codex CLI 导入会话

您在其他智能体 CLI 中启动了对话？可以将其导入 Hermes 并在此处继续交流。Hermes 能读取 Claude Code 的会话日志（位于 `~/.claude/projects/` 目录）以及 Codex CLI 的会话记录（位于 `~/.codex/sessions/` 目录）——这些外部文件仅会被读取，绝不会被修改。

```bash
# Interactive picker across both tools, newest first
hermes sessions import

# Limit to one tool, or point at a specific file
hermes sessions import --from claude
hermes sessions import --from codex ~/.codex/sessions/2026/08/15/rollout-....jsonl

# Import-and-resume in one step
hermes --resume @claude
hermes --resume @codex
```

`hermes sessions import` 命令会创建一个名为“Imported from Claude Code: <第一条用户消息>”（或 Codex CLI）的新 Hermes 会话，并输出该会话的 ID 以及可直接复制的 `hermes --resume <id>` 命令。而 `--resume @claude` / `--resume @codex` 命令则会显示相同的选项列表，直接将用户带入已导入的对话中。

**Hermes Desktop** 的命令面板中也提供了相同的导入功能（**Import session**）。该功能会列出连接的后端所在机器上的日志——而非运行应用程序的电脑——仅提供只读预览，而 **Continue in Hermes** 则会将对话内容复制到所选的配置文件中。浏览操作不会写入用户的会话存储，导入操作也不会修改源文件；若重复导入相同的日志，系统会直接使用已有的副本，而不会再次生成新内容。

保留下来的内容包括：有序的用户/助手对话记录，以及被浓缩在助手回复中的简短 `[ran tool: …]` 工具使用记录。系统提示、注入的上下文、推理过程以及工具的原始输出则会被剔除——此次导入生成的是经过整理的对话文本，而非逐字复制的内容。

## 会话搜索工具

该智能体内置了 `session_search` 工具，它能够利用 SQLite 的 FTS5 引擎对所有历史对话进行全文搜索，并允许智能体浏览找到的任意会话。此工具不会调用大型语言模型，而是直接从数据库中获取实际消息内容并展示，而非生成摘要。

### 四种调用方式

该工具会根据你设置的参数推断你的需求，无需指定 `mode` 参数。

**1. 发现功能 — 传递 `query` 参数：**

```python
session_search(query="auth refactor", limit=3)
```

该功能运行FTS5算法，通过会话关联关系对匹配结果进行去重，进而返回排名靠前的N个会话。Discovery默认采用自适应详细程度展示方式：排名最高的结果显示其完整的上下文窗口及相关消息，而排名较低的则以简洁形式呈现。若需完整展示所有结果，可传递`detail="full"`参数。

每个结果包含以下字段：

- `session_id`、`title`、`when`、`source`
- `snippet`——经FTS5算法高亮标注的匹配内容片段
- `detail`——`full`或`compact`
- `bookend_start` / `bookend_end`——完整结果包含的前后各3条用户与助手的消息；简洁结果则为空列表
- `messages`——完整结果包含FTS5匹配内容前后各±5条消息；简洁结果仅显示被标记的关联消息
- `match_message_id`、`messages_before`、`messages_after`

排名第一的结果会直接呈现目标→匹配内容→解决方案的完整链路。若另有简洁格式的结果看起来更具参考价值，可使用其会话ID和消息ID通过滚动功能查看详细内容。在实际会话数据库中，处理时间通常仅为数十毫秒。

**2. 滚动查看——传递`session_id` + `around_message_id`参数：**

```python
session_search(session_id="20260510_174648_805cc2", around_message_id=590803, window=10)
```

该功能会返回以锚点为中心、包含±`window`条消息的窗口内容。不支持FTS5查询，也不提供起始/结束边界信息——仅返回指定范围内的消息片段。在发现调用之后，当需要超出默认±5条消息范围的上下文时即可使用此功能。

- **向前滚动**：将 `messages[-1].id` 作为 `around_message_id` 参数传入；
- **向后滚动**：将 `messages[0].id` 作为 `around_message_id` 参数传入；
- 边界消息会作为定位标记同时出现在两个窗口中；
- 当 `messages_before` 或 `messages_after` 的数量小于 `window` 值时，表示当前处于会话的起始或结束位置。

每次滚动调用的典型处理时间仅为1–2毫秒。

**3. 读取操作——无需指定锚点，直接传入 `session_id` 即可：**

```python
session_search(session_id="20260510_174648_805cc2")
```

会返回整个会话内容；对于较大的会话，则会返回受限的头部/尾部视图。该数据格式也可用于解析 `@session:<profile>/<id>` 链接。

**4. 浏览——无需参数：**

```python
session_search()
```

按时间顺序返回最近的会话记录（包含标题、预览内容及时间戳）。当用户未明确说明具体主题，仅询问“我之前在做什么”时，该功能非常有用。

### FTS5 查询语法

关键词模式支持标准的 FTS5 查询语法：

- 简单关键词：`docker deployment`（FTS5 默认采用 AND 逻辑）
- 短语查询：`"exact phrase"`
- 布尔运算：`docker OR kubernetes`、`python NOT java`
- 前缀匹配：`deploy*`

### 可选参数

- `sort` — `newest` 或 `oldest`，在 FTS5 排序结果之上进一步排序。如仅需按相关性排序（默认值，适用于探索性检索），可省略该参数；对于“我们之前讨论到 X 的地方在哪里”这类问题，使用 `newest`；对于“X 是如何开始的”这类问题，则使用 `oldest`。
- `detail` — `adaptive`（默认值），仅完整展示排名最高的检索结果；`full` 则完整展示所有检索结果。
- `role_filter` — 用逗号分隔需要包含的角色。默认情况下，检索会包含 `user,assistant`（工具输出通常为干扰信息）。如需包含工具输出以调试工具行为，可设置 `user,assistant,tool`；如仅搜索工具输出，则设置为 `tool`。

### 使用场景

系统会在以下情况下自动提示使用会话搜索功能：

> “当用户提及过去对话中的内容，或您认为存在相关背景信息时，请先使用 session_search 检索出来，再要求用户重复说明。”

常见触发语句包括：“我们之前做过这个”、“还记得吗”、“上次……”、“正如我之前提到的”，或是任何提及当前界面中未显示的项目、人员或概念的表述。

## 各平台会话跟踪机制

### 网关会话

在消息平台上，会话是通过根据消息来源生成的确定性会话密钥来标识的：

| 聊天类型 | 默认密钥格式 | 行为表现 |
|-----------|--------------------|----------|
| Telegram私信 | `agent:main:telegram:dm:<chat_id>` | 每个私信对话对应一个会话 |
| Discord私信 | `agent:main:discord:dm:<chat_id>` | 每个私信对话对应一个会话 |
| WhatsApp私信 | `agent:main:whatsapp:dm:<canonical_identifier>` | 每个私信用户对应一个会话（若存在映射关系，LID/电话别名会合并为同一身份） |
| 群组聊天 | `agent:main:<platform>:group:<chat_id>:<user_id>` | 当平台提供用户ID时，群内每个用户对应一个会话 |
| 群组话题/线程 | `agent:main:<platform>:group:<chat_id>:<thread_id>` | 默认情况下所有话题参与者共享同一个会话；若设置`thread_sessions_per_user: true`，则每个用户拥有独立会话 |
| 频道聊天 | `agent:main:<platform>:channel:<chat_id>:<user_id>` | 当平台提供用户ID时，频道内每个用户对应一个会话 |

当Hermes无法获取共享聊天的参与者标识时，它会为该房间使用一个共享会话。

### 共享会话与独立会话的区别

默认情况下，Hermes在`config.yaml`中会将`group_sessions_per_user`设置为`true`。这意味着：

- Alice和Bob可以在同一个Discord频道中分别与Hermes交互，而不会共享对话记录
- 一个用户进行的长时间、涉及大量工具的任务不会占用另一个用户的上下文窗口
- 由于运行中的代理密钥与独立会话密钥一致，中断处理也会保持针对每个用户的独立处理。
如果您希望使用一个共享的“房间大脑”，请设置如下：

```yaml
group_sessions_per_user: false
```

这样一来，群组/频道将恢复为每个房间一个共享会话，既能保留对话的上下文信息，又能共享令牌成本、中断状态以及上下文数据量。

### 会话连续性

网关对话在长时间无操作或达到每日时间限制时不会重置。如需启动新的对话，请使用 `/new` 或 `/reset` 命令；上下文压缩功能仍会自动运行。旧的 `session_reset` 设置、重置策略覆盖项以及重置计时器环境变量均会被忽略。为释放资源，缓存中的智能体可能会被释放，而不会替换掉持久化的对话记录。重启恢复后的新鲜度限制会影响自动续谈功能，但不会影响发送消息时加载的对话历史。

### 崩溃与重启后的连续性

网关聊天被设计为**一个连续的会话**——随着数据量不断增加，该会话会持续进行压缩——直到您明确执行 `/new`（或 `/reset`）命令为止。这种连续性在网关崩溃、重启或更新后依然保持不变：

- 在创建会话记录的任何路径上（如 `/new`、发送第一条消息时，或通过 `/branch` 创建子会话），会话标识信息（路由键、聊天内容、来源信息）都会以**原子方式**被写入。一旦写入失败，下一个对话轮次中的路由刷新功能会自动修复该会话记录。
- 重启后，网关会为每个聊天重新匹配到具有最新**实际活动记录**的会话——那些过时且无效的会话记录绝不可能取代您当前正在进行的对话。
- 恢复机制会**遵循 `/new` 路径的边界规则**：如果某个聊天的最新事件是人为执行的重置操作，恢复过程将从头开始，而不会尝试追溯到重置之前的旧会话。仅凭时间流逝本身，并不会阻碍对持续有效对话的恢复。

## 存储位置

| 内容 | 路径 | 说明 |
|------|------|------|
| SQLite 数据库 | `~/.hermes/state.db` | 所有会话元数据及消息，采用 FTS5 索引技术 |
| 网关消息 | `~/.hermes/state.db` | SQLite 存储——所有会话消息的标准存储格式 |
| 网关路由索引 | `~/.hermes/state.db` 中的 `gateway_routing` 表 | 将会话键映射到对应的活跃会话 ID（包含来源信息及过期标志） |
| 旧版路由镜像 | `~/.hermes/sessions/sessions.json` | 路由索引的向后兼容镜像，当 `gateway.write_sessions_json: true`（默认值）时生成 |

该 SQLite 数据库采用 WAL 模式，支持多线程读取和单线程写入，非常适合网关的多平台架构需求。

:::warning `sessions.json` 并非会话列表  
网关路由索引存储在 `state.db` 内的 `gateway_routing` 表中；`~/.hermes/sessions/sessions.json` 仅是该表的**旧版副本**，旨在保持向后兼容性（可通过设置 `gateway.write_sessions_json: false` 关闭此功能）。它将消息传递会话键（格式为 `agent:main:<platform>:...`）映射到对应的活跃会话 ID。由于该文件仅包含网关/消息传递相关的条目，因此若您正在使用消息传递平台，其中只会显示相关条目（例如 `agent:main:whatsapp:dm:...`）。  

这是**正常现象**，并不表示您的 CLI 会话丢失。`hermes sessions list`、`/sessions` 接口以及控制面板均读取 `state.db` 文件，而该文件保存着**所有**类型的会话（CLI、TUI 以及网关会话）。`~/.hermes/sessions/saved/*.json` 下的 `/save` 快照仅作为便捷导出功能使用，并非索引文件。  

如果 CLI 会话确实未出现在 `hermes sessions list` 中，原因可能是 `state.db` 未能接收这些会话——请运行 `hermes sessions repair` 命令，并留意 CLI 启动时是否出现 `⚠ Session store unavailable` 的警告，该提示表明此次运行时 SQLite 持久化操作失败。  
:::  

:::note 旧版 JSONL 转录文件  
在 `state.db` 成为标准格式之前创建的会话，可能在 `~/.hermes/sessions/` 目录下留下一些 `*.jsonl` 文件。Hermes 已不再读取或写入这些文件。在确认对应会话确实存在于 `state.db` 中后，即可安全删除它们。  
:::  

### 数据库结构  

`state.db` 中的关键表：

- **sessions** — 会话元数据（id、来源、user_id、模型类型、标题、时间戳、token计数）。标题具有唯一索引（允许为空，但非空标题必须唯一）。
- **messages** — 完整的消息历史记录（角色、内容、tool_calls、工具名称、token计数）。
- **messages_fts** — 用于对消息内容进行全文搜索的FTS5虚拟表。

## 会话过期与清理

### 自动清理机制

- 网关对话会在用户无操作时持续保留；如需明确设置边界，可使用 `/new` 或 `/reset` 命令。
- 在重置之前，智能体会将即将过期的会话中的记忆和技能信息保存下来。
- 自动剪枝功能（自#54189版本起默认启用）：当 `sessions.auto_prune` 设为 `true` 时，处于非活跃状态且已过期 `sessions.retention_days` 天（默认为90天）的会话，会在CLI、网关或定时任务启动时被自动删除。
- 只有在同时满足以下两个条件时，才会对实际已被删除行的 `state.db` 文件执行 `VACUUM` 操作以释放磁盘空间：自上次成功执行 `VACUUM` 操作以来已至少过去 `sessions.min_vacuum_interval_days` 天（默认为30天），且文件中可回收的页面比例超过25%（即 `PRAGMA freelist_count / page_count` 的值）。对于数据密度较高的数据库而言，为了回收几MB的空间而进行完整重写是不值得的（SQLite在单纯使用DELETE语句时不会缩小文件大小）。
- 自动剪枝操作最多每 `sessions.min_interval_hours` 小时（默认为24小时）执行一次；最近一次操作的记录会存储在 `state.db` 文件中，因此同一 `HERMES_HOME` 目录下的所有Hermes进程都能共享该信息。
如果不进行剪枝处理，`state.db` 的大小将会无限制地增长——在通过网关及定时任务方式安装的版本中，短短几周内文件大小就可达数GB。如果您希望永久保留所有已结束的会话（即#54189版本之前的行为），则可在 `~/.hermes/config.yaml` 中关闭该功能：

```yaml
sessions:
  auto_prune: false         # default is true — set false to keep all history
  retention_days: 90        # keep ended sessions active within this window
  vacuum_after_prune: true  # reclaim disk space after a pruning sweep
  min_vacuum_interval_days: 30 # don't rewrite the DB more often than this
  min_interval_hours: 24    # don't re-run the sweep more often than this
```

那些已明确设置了上述任意键值的现有安装实例会保留其原有值；仅有未设置键值的实例才会采用新的默认值。

只有**已结束**的会话才会被删除。无论时长如何，活跃会话都绝不会被自动清理。已结束会话是根据其最后一条消息的时间来计算年龄的，因此，即便某次长时间对话是在保留期限开始之前开始的，也不会仅仅因为这个原因就被删除。

**来自自动化任务的过期未关闭会话**。某些任务——如定时任务、看板工作节点、子代理、一次性 CLI 运行——可能在未标记会话已结束的情况下终止，而清理操作仅会删除*已结束*的会话记录。为防止这类会话无限积累，每次自动清理时还会*关闭*那些最后活动时间已超过 `retention_days` 的来自上述来源（`cli`、`cron`、`kanban`、`acp`、`api_server`、`subagent`、`tool`）的未关闭会话（`end_reason: startup_orphan_reap`）。这种关闭操作是可逆的——会话仍可恢复——并且该会话记录会从关闭时间开始计算年龄，只有经过另一个完整的保留周期后，在*后续*的清理中才会被删除。消息平台会话（Telegram、Discord 等）、TUI/桌面会话、已固定会话，以及正处于实时轮询或压缩处理中的会话，均不会被此清理操作关闭。

### 过长聊天记录防护机制

有两项限制可防止过长的聊天记录一次性加载到内存中（两者默认值均为 `20000` 条活跃消息；将值设为 `0` 即可禁用该防护）：

```yaml
sessions:
  max_resume_messages: 20000   # interactive resume (CLI / TUI / Desktop)
  max_export_messages: 20000   # one-shot in-memory export of a single session
```

`max_resume_messages` 限制的是**实际加载的内容范围**，而非整个对话历史：

- 普通的交互式恢复功能（CLI 的 `--resume` 命令及 TUI 界面）会完整呈现所有的压缩记录——包括每一个压缩后的片段以及当前的提示信息——因此其限制范围覆盖了整个记录链。
- 桌面端的冷恢复功能则通过 REST 接口获取对话记录，并仅在内存中保存当前提示信息片段，因此其限制仅限于该提示信息本身。对于那些经过多次压缩、拥有大量片段（数十个压缩段，以及少量提示信息背后成千上万的存档行）的长期对话，这正是压缩功能的设计目的，此类对话仍可正常打开；其页脚显示的消息数量反映的是存储的完整记录链，而非当前提示信息。

当恢复请求被拒绝时，客户端会收到错误代码 `4130`，同时会告知具体的限制范围（“覆盖整个记录链”或“仅限于当前提示信息片段”）。对于这类会话，`hermes sessions export` 功能依然可用。

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
自动清理功能**默认处于开启状态**：在启动时，会移除已静止超过 `sessions.retention_days` 天（默认为90天）的已结束会话，而正在使用的会话则不会受到影响（详情请参见上文[自动清理](#automatic-cleanup)）。会话历史记录是实现跨历史对话的`session_search`检索功能的基础，因此，如果您希望永久保留所有已结束的会话，请在`config.yaml`中将`sessions.auto_prune`设置为`false`，或增大`retention_days`的值。即使关闭了自动清理功能，仍可使用`hermes sessions prune`命令进行一次性清理操作（经观察，若完全不进行清理，会导致`state.db`文件大小达到384 MB，且包含约1000个会话，进而降低FTS5的插入速度以及 `/resume`功能的响应速度）。
