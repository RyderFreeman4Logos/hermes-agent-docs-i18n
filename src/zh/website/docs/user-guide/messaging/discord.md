---
sidebar_position: 3
title: "Discord"
description: "Set up Hermes Agent as a Discord bot"
---

# Discord 设置指南

Hermes Agent 以机器人形式集成到 Discord 中，让您能够通过私信或服务器频道与 AI 助手进行交流。该机器人会接收您的消息，通过 Hermes Agent 的处理流程（包括工具调用、记忆功能以及推理能力）对其进行处理，并实时给出回复。它支持文本消息、语音消息、文件附件以及斜杠命令。

在开始设置之前，这里有大多数人最关心的问题：Hermes 搭入您的服务器后会如何运作？

## Hermes 的运行方式

| 场景 | 行为表现 |
|---------|----------|
| **私信** | Hermes 会回复每一条消息，无需使用 `@mention` 指定。每条私信都拥有独立的对话会话。 |
| **服务器频道** | 默认情况下，只有当您使用 `@mention` 指定 Hermes 时，它才会作出回应。若在频道中发消息但未提及 Hermes，它将忽略该消息。 |
| **自由回复频道** | 您可以通过设置 `DISCORD_FREE_RESPONSE_CHANNELS` 使特定频道无需 `@mention` 即可回复，或通过设置 `DISCORD_REQUIRE_MENTION=false` 全局禁用 `@mention` 功能。此类频道中的消息会直接在原帖下方回复，不会自动创建新线程，从而保持频道的轻量级特性。 |
| **线程** | Hermes 会在同一线程中回复消息。除非该线程或其所属频道被设置为自由回复模式，否则仍需遵循 `@mention` 规则。从会话历史记录的角度来看，线程与所属频道是相互独立的。 |
| **多用户共享频道** | 出于安全与清晰性的考虑，默认情况下 Hermes 会为频道内的每位用户单独维护会话历史记录。除非您明确禁用此功能，否则在同一频道中交流的两位用户不会共享同一份对话记录。 |
| **提及其他用户的消息** | 当 `DISCORD_IGNORE_NO_MENTION` 设为 `true`（默认值）时，如果某条消息提及了其他用户但未提及该机器人，Hermes 将保持沉默，避免其介入针对其他人的对话。若希望无论消息中提及了谁，机器人都予以回复，请将此参数设置为 `false`。此规则仅适用于服务器频道，不适用于私信。 |
:::提示
如果您希望创建一个普通的机器人帮助频道，让用户无需每次都添加标签即可与Hermes交流，只需将该频道添加到`DISCORD_FREE_RESPONSE_CHANNELS`中即可。
:::

### Discord网关模型

Discord上的Hermes并非那种仅能无状态回复的webhook。它通过完整的消息网关运行，这意味着每条收到的消息都需要经过以下流程：

1. 权限验证（`DISCORD_ALLOWED_USERS`）
2. 提及/自由回复检测
3. 会话查找
4. 会话记录加载
5. 正常的Hermes智能体执行，包括工具、内存功能以及斜杠命令
6. 将回复发送回Discord

这一点非常重要，因为在一个繁忙的服务器中，系统行为既取决于Discord的路由机制，也取决于Hermes的会话策略。

### Discord中的会话模型

默认情况下：

- 每条私信都会拥有独立的会话
- 每个服务器主题帖都有其专属的会话命名空间
- 共享频道中的每位用户在该频道内也拥有独立的会话

因此，即便艾丽斯和鲍勃都在`#research`频道中与Hermes交流，由于它们属于不同的会话，Hermes默认会将这些交流视为独立的对话，即使它们使用的是同一个可见的Discord频道。

该设置可通过`config.yaml`进行配置：

```yaml
group_sessions_per_user: true
```

仅当您明确希望为整个房间设置单一共享对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话虽有利于协作交流，但也存在以下问题：

- 用户需共同承担上下文存储增长及令牌消耗；
- 某人执行的耗时且依赖大量工具的任务可能会占用其他所有人的上下文空间；
- 同一房间内，某人正在运行的任务可能会干扰另一人的后续操作。

### 任务中断与并发处理

Hermes会通过会话密钥来追踪正在运行的智能体。

在默认设置`group_sessions_per_user: true`的情况下：

- 艾丽斯仅能中断自己正在处理的请求，且仅影响该频道内的她自己的会话；
- 鲍勃仍可在同一频道内继续发言，不会继承艾丽斯的操作历史，也不会干扰她的任务执行。

而在`group_sessions_per_user: false`的设置下：

- 整个房间会共享该频道/线程的一个智能体运行名额；
- 不同用户发送的后续消息可能会相互干扰，或排队等待处理。

本指南将为您详细介绍完整的设置流程——从在Discord开发者门户创建机器人，到发送第一条消息。

### 网关WebSocket状态监控

Discord REST接口与网关WebSocket属于两种独立的通信方式。即使REST请求返回成功响应（包括`fetch_user()`返回HTTP 200状态码），也不能保证机器人仍能接收网关事件。因此，Hermes会综合考量智能体的就绪状态、客户端/套接字关闭状态、套接字是否处于开放状态、心跳确认消息的延迟时间以及心跳延迟的上限值，以此来判断智能体的实际运行状况。

当出现指定次数的连续异常样本后，该适配器会触发一个可重试的致命事件。现有的网关重连监控机制会创建一个新的适配器；而 Discord 适配器则不会启动第二个无限制的重连循环。

可在 `config.yaml` 文件中配置这些非敏感阈值：

```yaml
discord:
  websocket_liveness_interval_seconds: 15
  websocket_liveness_failure_threshold: 2
  websocket_heartbeat_ack_max_age_seconds: 60
  websocket_max_latency_seconds: 30
```

旧的 `liveness_interval_seconds` 和 `liveness_failure_threshold` 名称仅作为兼容性别名存在，它们已不再与 REST 探测功能相关。

## 第一步：创建 Discord 应用程序

1. 访问 [Discord 开发者门户](https://discord.com/developers/applications)，使用您的 Discord 账户登录。
2. 点击右上角的 **New Application**。
3. 为应用程序输入名称（例如“Hermes Agent”），并同意开发者服务条款。
4. 点击 **Create**。

您将进入 **General Information** 页面。请记下 **Application ID**——稍后生成邀请链接时需要用到它。

## 第二步：创建机器人

1. 在左侧栏中点击 **Bot**。
2. Discord 会自动为您的应用程序创建一个机器人用户。您可以看到机器人的用户名，该名称可自行修改。
3. 在 **Authorization Flow** 下方：
   - 将 **Public Bot** 设置为 **ON**——这是使用 Discord 提供的邀请链接的必要条件（推荐做法），这样“安装”选项卡就能生成默认的授权 URL。
   - 保持 **Require OAuth2 Code Grant** 的设置为 **OFF**。

:::提示
您可以在该页面为机器人设置自定义头像和横幅。这些内容将会显示在 Discord 中。
:::

:::信息[私有机器人的替代方案]
如果您希望让机器人保持私有状态（即关闭 Public Bot），则必须在第五步中使用 **Manual URL** 方法，而非“安装”选项卡。因为 Discord 提供的链接要求必须开启 Public Bot。
:::

## 第三步：启用特权网关意图

这是整个设置流程中最关键的一步。如果未启用正确的意图，您的机器人虽然能够连接到 Discord，但**将无法读取消息内容**。

在**Bot**页面中，向下滚动至**Privileged Gateway Intents**部分。您会看到三个开关：

| 意图 | 用途 | 是否必需？ |
|------|------|-----------| 
| **Presence Intent** | 查看用户的在线/离线状态 | 可选 |
| **Server Members Intent** | 访问成员列表并解析用户名 | **必需** |
| **Message Content Intent** | 读取消息的文本内容 | **必需** |

请将**Server Members Intent**和**Message Content Intent**两个开关都切换为**开启**状态。

- 若未启用**Message Content Intent**，机器人虽会接收到消息事件，但消息文本为空——也就是说，机器人根本无法看到您输入的内容。
- 若未启用**Server Members Intent**，机器人将无法解析允许的用户列表中的用户名，进而可能无法识别是谁在向其发送消息。

:::warning[这是导致 Discord 机器人无法正常工作的首要原因]
如果您的机器人处于在线状态却从不回复消息，那几乎可以肯定是因为**Message Content Intent**被禁用了。请返回[开发者门户](https://discord.com/developers/applications)，选择您的应用 → Bot → Privileged Gateway Intents，确保**Message Content Intent**已切换为开启状态，然后点击**Save Changes**。
:::

**关于服务器数量限制：**
- 如果您的机器人仅在**100台服务器**内运行，您可以自由地开启或关闭各类意图。
- 若机器人部署在**100台及以上服务器**中，Discord要求您提交验证申请才能使用高级意图功能。对于个人用途而言，这并非问题。

请点击页面底部的**保存更改**。

## 第4步：获取机器人令牌

机器人令牌是Hermes Agent用于以您的机器人身份登录的凭证。仍在**机器人**页面上：

1. 在**令牌**部分，点击**重置令牌**。
2. 如果您的Discord账户已启用双重认证，请输入相应的2FA验证码。
3. Discord会显示新的令牌，请**立即复制它**。

:::warning[令牌仅显示一次]
该令牌只会显示一次。一旦丢失，您需要重置并生成新的令牌。切勿公开分享您的令牌，也勿将其提交到Git中——拥有此令牌的人即可完全控制您的机器人。
:::

请将令牌保存在安全的地方（例如密码管理器），因为第8步时还需要用到它。

## 第5步：生成邀请链接

您需要一个OAuth2链接才能将机器人邀请到您的服务器。有两种实现方式：

### 方案A：使用安装选项卡（推荐）

:::note[需开启公共机器人]
此方法要求在步骤2中将**公共机器人**设置为**开启**状态。如果您将公共机器人设置为关闭，请改用下方的手动URL生成方法。
:::

1. 在左侧导航栏中，点击**安装**。
2. 在**安装场景**下方，启用**服务器安装**选项。
3. 对于**安装链接**，选择**Discord 提供的链接**。
4. 在**服务器安装的默认设置**中：
   - **权限范围**：选择 `bot` 和 `applications.commands`
   - **权限**：选择下方列出的权限。

### 方案 B：手动输入 URL

您也可以直接使用以下格式来构建邀请链接：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

请将 `YOUR_APP_ID` 替换为步骤 1 中获取的应用程序 ID。

### 必需权限

以下是您的机器人所必需的最低权限：

- **查看频道** — 查看其有权访问的频道
- **发送消息** — 回复您的消息
- **嵌入链接** — 格式化丰富的回复内容
- **附加文件** — 发送图片、音频及文件输出
- **读取消息历史记录** — 保留对话上下文

### 推荐的额外权限

- **在主题对话中发送消息** — 在主题对话中进行回复
- **添加表情反应** — 通过表情反应来确认收到消息

### 权限整数值

| 等级 | 权限整数值 | 包含的权限 |
|-------|------------|------------|
| 最低要求 | `117760` | 查看频道、发送消息、读取消息历史记录、附加文件 |
| 推荐配置 | `274878286912` | 上述所有权限，外加嵌入链接、在主题对话中发送消息、添加表情反应 |

## 第 6 步：将机器人邀请到您的服务器

1. 在浏览器中打开邀请链接（可从“安装”选项卡或您手动生成的链接获取）。
2. 在 **添加到服务器** 下拉列表中选择您的服务器。
3. 点击 **继续**，然后点击 **授权**。
4. 如有提示，请完成验证码验证。

:::info
若要邀请机器人，您需要在 Discord 服务器中拥有 **管理服务器** 权限。如果下拉列表中没有显示您的服务器，请让服务器管理员使用邀请链接来操作。
:::

授权完成后，该机器人将出现在您服务器的成员列表中（在启动 Hermes 网关之前，它将显示为离线状态）。

## 第7步：查找您的Discord用户ID

Hermes Agent会利用您的Discord用户ID来控制哪些用户可以与该机器人交互。具体操作如下：

1. 打开Discord（桌面版或网页版）。
2. 进入**设置** → **高级选项**，将**开发者模式**切换为**开启**状态。
3. 关闭设置窗口。
4. 在消息、成员列表或个人资料中右键点击您的用户名，选择**复制用户ID**。

您的用户ID是一个长数字，例如`284102345871466496`。

:::提示
开发者模式还允许您以相同方式复制**频道ID**和**服务器ID**——只需右键点击频道或服务器名称，然后选择“复制ID”。如果您想手动设置主频道，就需要频道ID。
:::

## 第8步：配置Hermes Agent

### 方案A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在系统提示时选择**Discord**，随后在要求输入时粘贴您的机器人令牌和用户 ID。

### 方案 B：手动配置

在您的 `~/.hermes/.env` 文件中添加以下内容：

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=284102345871466496

# Multiple allowed users (comma-separated)
# DISCORD_ALLOWED_USERS=284102345871466496,198765432109876543
```

接着启动网关：

```bash
hermes gateway
```

该机器人应在几秒内登录 Discord 并处于在线状态。你可以通过私信或发送到其可见的频道中发送消息来对其进行测试。

:::提示
为确保持续运行，你可以将 `hermes gateway` 在后台运行或作为 systemd 服务启动。详情请参阅部署指南。
:::

## 配置参考

Discord 的行为通过两个文件进行控制：**`~/.hermes/.env`** 用于存储凭证及环境级开关设置，而 **`~/.hermes/config.yaml`** 则用于存放结构化配置。当两者同时存在时，环境变量始终优先于 config.yaml 中的数值。

### 环境变量（`.env`）

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | **Yes** | — | Bot token from the [Discord Developer Portal](https://discord.com/developers/applications). |
| `DISCORD_ALLOWED_USERS` | Conditional | — | Comma-separated Discord user IDs allowed to interact with the bot. Without this **or** `DISCORD_ALLOWED_ROLES`, the gateway denies all users unless `DISCORD_ALLOW_ALL_USERS=true`, `GATEWAY_ALLOW_ALL_USERS=true`, or `DISCORD_ALLOWED_CHANNELS` explicitly scopes guild access. |
| `DISCORD_ALLOWED_ROLES` | No | — | Comma-separated Discord role IDs. Any member with one of these roles is authorized — OR semantics with `DISCORD_ALLOWED_USERS`. Auto-enables the **Server Members Intent** on connect. Useful when moderation teams churn: new mods get access as soon as the role is granted, no config push needed. |
| `DISCORD_ALLOW_ALL_USERS` | No | `false` | Explicit opt-in to allow every Discord user who can reach the bot. This restores the pre-0.18 open behavior for Discord only; use only for trusted/private guilds or development. |
| `GATEWAY_ALLOW_ALL_USERS` | No | `false` | Global allow-all opt-in for every gateway platform. Prefer the platform-specific `DISCORD_ALLOW_ALL_USERS` unless you intentionally want all connected platforms open. |
| `DISCORD_HOME_CHANNEL` | No | — | Channel ID where the bot sends proactive messages (cron output, reminders, notifications). |
| `DISCORD_HOME_CHANNEL_NAME` | No | `"Home"` | Display name for the home channel in logs and status output. |
| `DISCORD_COMMAND_SYNC_POLICY` | No | `"safe"` | Controls native slash-command startup sync. `"safe"` diffs existing global commands and only updates what changed, recreating commands when Discord metadata changes cannot be applied via patch. `"bulk"` preserves the old `tree.sync()` behavior. `"off"` skips startup sync entirely. |
| `DISCORD_REQUIRE_MENTION` | No | `true` | When `true`, the bot only responds in server channels when `@mentioned`. Set to `false` to respond to all messages in every channel. |
| `DISCORD_THREAD_REQUIRE_MENTION` | No | `false` | When `true`, the in-thread mention shortcut is disabled — threads are gated the same as channels, requiring `@mention` even after the bot has already participated. Use this when multiple bots share a thread and you want each to fire only on explicit `@mention`. |
| `DISCORD_FREE_RESPONSE_CHANNELS` | No | — | Comma-separated channel IDs where the bot responds without requiring an `@mention`, even when `DISCORD_REQUIRE_MENTION` is `true`. |
| `DISCORD_IGNORE_NO_MENTION` | No | `true` | When `true`, the bot stays silent if a message `@mentions` other users but does **not** mention the bot. Prevents the bot from jumping into conversations directed at other people. Only applies in server channels, not DMs. |
| `DISCORD_AUTO_THREAD` | No | `true` | When `true`, automatically creates a new thread for every `@mention` in a text channel, so each conversation is isolated (similar to Slack behavior). Messages already inside threads or DMs are unaffected. |
| `DISCORD_ALLOW_BOTS` | No | `"none"` | Controls how the bot handles messages from other Discord bots. `"none"` — ignore all other bots. `"mentions"` — only accept bot messages that `@mention` Hermes. `"all"` — accept all bot messages. |
| `DISCORD_REACTIONS` | No | `true` | When `true`, the bot adds emoji reactions to messages during processing (👀 when starting, ✅ on success, ❌ on error). Set to `false` to disable reactions entirely. |
| `DISCORD_IGNORED_CHANNELS` | No | — | Comma-separated channel IDs where the bot **never** responds, even when `@mentioned`. Takes priority over all other channel settings. |
| `DISCORD_ALLOWED_CHANNELS` | No | — | Comma-separated channel IDs. When set, the bot **only** responds in these channels (plus DMs if allowed). Overrides `config.yaml` `discord.allowed_channels`. Combine with `DISCORD_IGNORED_CHANNELS` to express allow/deny rules. |
| `DISCORD_NO_THREAD_CHANNELS` | No | — | Comma-separated channel IDs where the bot responds directly in the channel instead of creating a thread. Only relevant when `DISCORD_AUTO_THREAD` is `true`. |
| `DISCORD_HISTORY_BACKFILL` | No | `true` | When `true`, prepend recent channel scrollback (since the bot's last response) to the user message when the bot is mentioned. Recovers context the bot would otherwise miss with `require_mention`. Skipped in DMs and free-response channels. Set to `false` to disable. |
| `DISCORD_HISTORY_BACKFILL_LIMIT` | No | `50` | Maximum number of messages to scan backwards when assembling the backfill block. In practice the scan usually stops earlier — at the bot's own last message in the channel. |
| `DISCORD_REPLY_TO_MODE` | No | `"first"` | Controls reply-reference behavior: `"off"` — never reply to the original message, `"first"` — reply-reference on the first message chunk only (default), `"all"` — reply-reference on every chunk. |
| `DISCORD_ALLOW_MENTION_EVERYONE` | No | `false` | When `false` (default), the bot cannot ping `@everyone` or `@here` even if its response contains those tokens. Set to `true` to opt back in. See [Mention Control](#mention-control) below. |
| `DISCORD_ALLOW_MENTION_ROLES` | No | `false` | When `false` (default), the bot cannot ping `@role` mentions. Set to `true` to allow. |
| `DISCORD_ALLOW_MENTION_USERS` | No | `true` | When `true` (default), the bot can ping individual users by ID. |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | No | `true` | When `true` (default), replying to a message pings the original author. |
| `DISCORD_PROXY` | No | — | Proxy URL for Discord connections (HTTP, WebSocket, REST). Overrides `HTTPS_PROXY`/`ALL_PROXY`. Supports `http://`, `https://`, and `socks5://` schemes. |
| `DISCORD_ALLOW_ANY_ATTACHMENT` | No | `false` | When `true`, the bot accepts attachments of any file type (not just the built-in PDF/text/zip/office allowlist). Unknown types are cached to disk and surfaced to the agent as a local path with `application/octet-stream` MIME so it can inspect them with `terminal` / `read_file` / `ffprobe` / etc. |
| `DISCORD_MAX_ATTACHMENT_BYTES` | No | `33554432` | Maximum bytes per attachment the gateway will download and cache. Default 32 MiB. Set to `0` for no cap (attachments are held in memory while being written, so unlimited carries a real memory cost). |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | No | `0.6` | Grace window the adapter waits before flushing a queued text chunk. Useful for smoothing streamed output. |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | No | `2.0` | Delay between split chunks when a single message exceeds Discord's length limit. |

:::warning 不支持机器人之间的直接对话  
`DISCORD_ALLOW_BOTS` 的作用是允许来自特定可信机器人的输入（例如中转机器人或 webhook 机器人），而非让两个 Hermes 账户相互通信。其默认值为 `"none"`，会忽略所有其他机器人，也是最安全的设置。  

通过为多个 Hermes 账户设置 `"mentions"` 或 `"all"`，使其在共享频道中互相回复，这种架构目前不受支持。Discord 会在每次回复时自动 `@mention` 被回复的对象，因此在 `"mentions"` 模式下，两个机器人将无限循环地满足对方的提及条件，进而陷入确认循环。由于仅支持将 `DISCORD_ALLOW_BOTS` 设为 `"none"`，因此不存在相应的断路保护机制。如果确实需要允许某个特定机器人，应将其权限范围限定得尽可能狭窄，且绝不能让其与其他自动回复机器人交互。  
:::

### 配置文件 (`config.yaml`)  

`~/.hermes/config.yaml` 文件中的 `discord` 部分与上述环境变量对应。Config.yaml 中的设置会作为默认值生效——如果已有相同的环境变量被设置，则以环境变量的值为准。

```yaml
# Discord-specific settings
discord:
  require_mention: true           # Require @mention in server channels
  thread_require_mention: false   # If true, require @mention in threads too (multi-bot threads)
  free_response_channels: ""      # Comma-separated channel IDs (or YAML list)
  auto_thread: true               # Auto-create threads on @mention
  reactions: true                 # Add emoji reactions during processing
  ignored_channels: []            # Channel IDs where bot never responds
  no_thread_channels: []          # Channel IDs where bot responds without threading
  history_backfill: true          # Prepend recent channel scrollback on mention (default: true)
  history_backfill_limit: 50      # Max messages to scan backwards (default: 50)
  missed_message_backfill:        # Replay messages missed while disconnected (opt-in)
    enabled: false
    channels: []                  # Empty uses free_response_channels
    window_seconds: 21600         # Look back at most 6 hours
    limit: 100                    # Global scan cap per reconnect
    max_dispatches: 10            # Recovery dispatch cap per reconnect
  channel_prompts: {}             # Per-channel ephemeral system prompts
  voice_channel_inactivity_timeout_seconds: 300  # Set 0 to stay in VC until explicit /voice leave
  voice_playback_timeout_seconds: 120             # Minimum playback watchdog; long clips get duration+padding
  allow_mentions:                 # What the bot is allowed to ping (safe defaults)
    everyone: false               # @everyone / @here pings (default: false)
    roles: false                  # @role pings (default: false)
    users: true                   # @user pings (default: true)
    replied_user: true            # reply-reference pings the author (default: true)

# Session isolation (applies to all gateway platforms, not just Discord)
group_sessions_per_user: true     # Isolate sessions per user in shared channels
```

#### `discord.require_mention`

**类型：** 布尔值 — **默认值：** `true`

启用此选项后，机器人仅会在被直接`@提及`时才在服务器频道中回复。而无论是否启用该设置，私信始终会收到回复。

#### `discord.thread_require_mention`

**类型：** 布尔值 — **默认值：** `false`

默认情况下，一旦机器人参与了某个主题串（无论是通过被`@提及`自动创建，还是首次回复进入），它就会持续回复该主题串中的后续消息，无需再次被`@提及`。这对于一对一的对话而言是合适的默认设置。

但在**多机器人主题串**中——即用户轮流向不同机器人发送消息的场景下——这种默认设置反而会带来问题：主题串中的其他机器人也会对每一条消息作出回复，从而导致资源浪费并使频道充斥垃圾信息。将`thread_require_mention`设置为`true`即可取消这一主题串内的快捷机制，让主题串的响应规则与普通频道保持一致。此时，明确的`@提及`操作仍会像以前一样正常生效。

```yaml
discord:
  require_mention: true
  thread_require_mention: true    # multi-bot setup
```

#### `discord.free_response_channels`

**类型：** 字符串或列表 — **默认值：** `""`

指定机器人无需通过 `@mention` 即可回复所有消息的频道 ID。可接受以逗号分隔的字符串形式，或 YAML 列表形式：

```yaml
# String format
discord:
  free_response_channels: "1234567890,9876543210"

# List format
discord:
  free_response_channels:
    - 1234567890
    - 9876543210
```

如果某个帖子的父频道在列表中，该帖子也将不会被@提及。

自由回复频道也会**跳过自动分线程功能**——机器人会直接在原消息下方回复，而不会为每条消息创建新帖子。这样一来，该频道仍可作为轻量级的聊天界面使用。如果您需要分线程功能，请勿将频道标记为自由回复类型（应改用常规的@提及流程）。

#### `discord.auto_thread`

**类型：** 布尔值 — **默认值：** `true`

启用此功能后，普通文本频道中的每条@提及都会自动创建一个新帖子来承载对应对话。这不仅能保持主频道的整洁，还能让每段对话拥有独立的会话历史记录。一旦帖子创建完成，后续发送到该帖子的消息就无需再使用@提及——机器人会知道它已参与该对话。在多机器人配置中，若要禁用此内置快捷方式，请将[`thread_require_mention`](#discordthread_require_mention)设置为`true`。

已存在帖子或私信中的消息不受此设置影响。被列入`discord.free_response_channels`或`discord.no_thread_channels`的频道同样会跳过自动分线程功能，机器人会直接在这些频道中回复。

#### `discord.reactions`

**类型：** 布尔值 — **默认值：** `true`

用于控制机器人是否为消息添加表情符号反应作为视觉反馈：
- 当机器人开始处理您的消息时，会添加👀；
- 当回复成功发送时，会添加✅；
- 如果处理过程中出现错误，则会添加❌。
如果觉得表情反应会分散注意力，或者机器人的角色没有“添加表情反应”的权限，可禁用此功能。

#### `discord.ignored_channels`

**类型：** 字符串或列表 — **默认值：** `[]`

即使被直接`@提及`，机器人也**绝不会**回应的频道编号。该设置具有最高优先级——只要频道被列入此列表，无论“是否需要被提及”、“可自由回复的频道”或其他任何设置如何，机器人都会默默忽略该频道内的所有消息。

```yaml
# String format
discord:
  ignored_channels: "1234567890,9876543210"

# List format
discord:
  ignored_channels:
    - 1234567890
    - 9876543210
```

如果某个帖子的父频道位于此列表中，该帖子中的消息也会被忽略。

#### `discord.no_thread_channels`

**类型：** 字符串或列表 — **默认值：** `[]`

指定在此类频道中，机器人将直接回复内容而非自动创建新帖子的频道 ID。此设置仅在 `auto_thread` 设为 `true`（即默认值）时才会生效。在这些频道中，机器人会以普通消息的形式直接回复，而不会生成新的帖子。

```yaml
discord:
  no_thread_channels:
    - 1234567890  # Bot responds inline here
```

对于那些专门用于机器人交互的频道而言，这一功能非常实用，因为使用话题串会带来不必要的干扰。

#### `discord.channel_prompts`

**类型：** 映射 — **默认值：** `{}`

这是针对每个频道的临时系统提示，会在对应的 Discord 频道或话题串中的每一轮对话中自动显示，且不会被保存到对话记录中。

```yaml
discord:
  channel_prompts:
    "1234567890": |
      This channel is for research tasks. Prefer deep comparisons,
      citations, and concise synthesis.
    "9876543210": |
      This forum is for therapy-style support. Be warm, grounded,
      and non-judgmental.
```

行为规则：
- 仅当线程/频道 ID 完全匹配时，匹配才会成功。
- 如果消息出现在某个线程或帖子中，而该线程没有对应的独立条目，Hermes 会回退到父频道/论坛的 ID 进行匹配。
- 提示语会在运行时临时应用，因此修改它们会立即影响后续对话，而无需重新编写之前的会话记录。

#### `discord.history_backfill`

**类型：** 布尔值 — **默认值：** `true`

启用此功能后，机器人会在每次收到 `@mention` 时补充遗漏的频道消息。若设置 `require_mention: true`，机器人仅处理直接提及它的消息——频道中的其他所有消息都不会出现在会话记录中。该功能被触发时会回溯最近的频道历史记录，收集从机器人上次回复到当前提及之间的消息，并将其作为上下文纳入记录。

不同场景下的行为表现：
- **服务器频道**（配合 `require_mention: true` 使用）：会补充机器人上次回复之后的所有消息。当其他参与者在机器人未被提及时发送消息时，此功能非常有用。
- **线程**：仅扫描该线程内的消息——Discord 的 `channel.history()` 函数在获取线程历史时只会返回该线程内的消息，而非父频道的内容。由于线程通常是独立的对话单元，因此这种范围设置更为合适。
- **私信**：会被跳过。每条私信都会触发机器人响应，因此会话记录已经完整，无需补充遗漏的消息。
- **自由回复频道**以及**机器人自行创建的线程**：出于相同原因也会被跳过——由于没有提及限制，也就不存在需要补充的空白部分。
针对每个用户独立的会话（即`group_sessions_per_user: true`模式，这也是默认设置）同样能从中受益：在该模式下，用户的会话中不会包含其他频道参与者发送的上下文信息，以及该用户在标记机器人之前自己发送的消息。而回填功能正好可以填补这两方面的缺失。

```yaml
discord:
  history_backfill: true   # default
```

如需关闭该功能：

```yaml
discord:
  history_backfill: false
```

> **注意：**在机器人正在处理消息的期间（即触发事件与响应之间）传入的消息将不会被捕获。这是出于简化考虑而采取的做法——用户可以重新发送消息或再次添加标签。

#### `discord.history_backfill_limit`

**类型：**整数 — **默认值：**`50`

用于在恢复频道上下文时向后扫描的最大消息数量。实际上，扫描通常会在此之前就停止——即从机器人在该频道中最后发送的消息开始，因为该位置本身就是对话轮次的自然分界点。设置此限制是为了在机器人首次启动或近期历史记录中不存在任何先前消息的长时间间隔情况下提供保障。

```yaml
discord:
  history_backfill: true
  history_backfill_limit: 50
```

#### `discord.missed_message_backfill`

**类型：** 对象 — **默认值：** 禁用

在 Discord 重启或网络中断期间，其 WebSocket 连接的恢复窗口可能会失效。在此期间发送的消息不会作为实时消息事件被送达。启用此选项后，Hermes 会在 Discord 重新连接后，扫描一组已配置的频道和主题历史记录，然后通过与实时消息相同的授权、提及、频道处理、去重及分发路径，将那些尚未被处理的消息发送出去。

```yaml
discord:
  missed_message_backfill:
    enabled: true
    channels: ["123456789012345678"]
    window_seconds: 3600
    limit: 100
    max_dispatches: 10
```

如果 `channels` 为空，Hermes 将使用 `discord.free_response_channels`。仅当机器人需要检查所有可访问的服务器文本频道时，才将其设置为 `"*"`。恢复日志会按用户配置存储在 `gateway/discord_message_recovery.db` 中，从而避免已成功处理的消息在后续重启后被再次处理。

#### `group_sessions_per_user`

**类型：** 布尔值 — **默认值：** `true`

这是一个全局网关设置（并非 Discord 特有），用于控制同一频道内的用户是否拥有独立的会话历史记录。

当值为 `true` 时：在 `#research` 频道中交流的 Alice 和 Bob 每人都会与 Hermes 保持独立的对话记录。当值为 `false` 时：整个频道将共享同一个对话记录以及一个正在运行的机器人实例。

```yaml
group_sessions_per_user: true
```

如需了解各模式的具体作用，请参阅上文的[会话模型](#session-model-in-discord)部分。

#### `display.tool_progress`

**类型：** 字符串 — **默认值：** `"all"` — **可选值：** `off`、`new`、`all`、`verbose`

用于控制机器人在处理任务时是否在聊天中发送进度信息（例如“正在读取文件...”、“正在执行终端命令...”）。这是一个全局设置，适用于所有平台。

```yaml
display:
  tool_progress: "all"    # off | new | all | verbose
```

- `off` — 不显示进度信息  
- `new` — 每轮仅显示第一次工具调用信息  
- `all` — 显示所有工具调用信息（在网关消息中会截断至40个字符）  
- `verbose` — 显示完整的工具调用详情（可能会生成较长的消息）  

#### `display.tool_progress_command`

**类型：** 布尔值 — **默认值：** `false`  

启用该选项后，网关中将提供 `/verbose` 接口命令，无需编辑 config.yaml 即可切换不同的工具进度显示模式（`off → new → all → verbose → off`）。

```yaml
display:
  tool_progress_command: true
```

#### `display.reasoning_style`

**类型：** 字符串 — **Discord 默认值：** `"subtext"` — **可选值：** `code`、`blockquote`、`subtext`

用于控制在开启推理展示功能时，模型推理内容的呈现方式。Discord 的默认设置为 `subtext`，该模式会使用 Discord 自带的灰色小元数据文本格式 `-# `，从而使推理内容在视觉上处于答案的次要位置。`blockquote` 模式会将推理内容以 `>` 引号形式展示，而 `code` 模式（其他平台的默认设置）则会使用代码块进行呈现。对于过长的推理内容，系统仅会显示前 15 行。

```yaml
display:
  platforms:
    discord:
      reasoning_style: subtext   # code | blockquote | subtext
```

## Slash 命令访问控制

默认情况下，所有获授权的用户均可使用所有的 Slash 命令。若希望将权限列表划分为**管理员**（可使用所有 Slash 命令）和**普通用户**（仅能使用明确启用的命令），可在 Discord 平台的 `extra` 区块中添加 `allow_admin_from` 和 `user_allowed_commands` 参数：

```yaml
gateway:
  platforms:
    discord:
      extra:
        # Existing user allowlist (unchanged)
        allow_from:
          - "123456789012345678"  # admin user ID
          - "999888777666555444"  # regular user ID

        # NEW — admins get all slash commands (built-in + plugin)
        allow_admin_from:
          - "123456789012345678"

        # NEW — non-admin allowed users can only run these slash commands.
        # /help and /whoami are always allowed so users can see their access.
        user_allowed_commands:
          - status
          - model
          - history

        # Optional: separate admin / command lists for server channels
        group_allow_admin_from:
          - "123456789012345678"
        group_user_allowed_commands:
          - status
```

**行为规则：**

- 属于某个范围（私信或服务器频道）的 `allow_admin_from` 列表中的用户，可通过实时命令注册表使用**所有**已注册的斜杠命令——包括内置命令和插件注册的命令。
- 不在 `allow_admin_from` 列表中的用户，仅能使用 `user_allowed_commands` 中列出的命令，以及始终允许使用的命令 `/help` 和 `/whoami`。
- 普通聊天内容（非斜杠命令消息）不受影响。非管理员用户仍可正常与智能体对话，只是无法触发任意命令。
- **向后兼容性**：如果某个范围未设置 `allow_admin_from`，则该范围的斜杠命令限制将被禁用。现有安装无需更改即可继续正常工作。
- 私信中的管理员身份并不等同于服务器频道中的管理员身份。每个范围都有独立的管理员列表。

使用 `/whoami` 可查看当前所处的范围、您的权限等级（管理员/用户/无限制），以及您可以使用的斜杠命令。

## 交互式模型选择器

在 Discord 频道中发送不带参数的 `/model` 即可打开基于下拉菜单的模型选择器：

1. **提供商选择**——一个下拉菜单，显示可用的提供商（最多25个）。
2. **模型选择**——另一个下拉菜单，展示所选提供商对应的模型（最多25个）。

该选择器在120秒后超时。仅授权用户（即位于 `DISCORD_ALLOWED_USERS` 列表中的用户）才能使用它。如果您已知模型名称，可直接输入 `/model <名称>`。 

## 用于技能的原生斜杠命令

Hermes 会自动将已安装的技能注册为**原生的 Discord 应用命令**。这意味着这些技能会与内置命令一同出现在 Discord 的自动补全 `/` 菜单中。

- 每个技能都会变成一个 Discord 斜杠命令（例如：/code-review、/ascii-art）
- 这些技能可接受可选的 `args` 字符串参数
- Discord 对每个机器人的应用命令数量设有 100 个的限制——如果您的技能数量超过了此上限，多余的技能将会被跳过，并在日志中留下警告信息
- 这些技能会在机器人启动时与 `/model`、/reset 和 /bg 等内置命令一同被注册

无需进行任何额外配置——通过 `hermes skills install` 安装的任何技能，都将在下一次网关重启时自动注册为 Discord 斜杠命令。

### 禁用斜杠命令注册

如果您针对同一个 Discord 应用运行多个 Hermes 网关（例如测试环境与生产环境），则其中只能有一个网关负责全局斜杠命令的注册——否则最后启动的网关会覆盖之前的设置，导致注册状态反复变动。请在“从属”网关上关闭斜杠命令注册功能：

```yaml
gateway:
  platforms:
    discord:
      extra:
        slash_commands: false   # default: true
```

将“主”网关的此参数设置为 `true` 可保持原有行为，即通过全局 `/` 菜单来调用内置技能及已安装的技能。

## 发送媒体文件（内联 `MEDIA:` 标签）

Discord 适配器支持通过代理响应中输出的内联 `MEDIA:/path/to/file` 标签，为各类常见媒体类型直接上传文件——该适配器会自动提取标签并上传文件：

| 类型 | 传输方式 |
|---|---|
| 图片（PNG/JPG/WebP） | 以 Discord 原生图片附件形式发送，并附带内联预览 |
| 动画 GIF | 通过 `send_animation` 以 `animation.gif` 的格式上传，让 Discord 以内联方式播放（而非静态缩略图） |
| 视频（MP4/MOV） | 使用 `send_video` — 通过 Discord 原生视频播放器播放 |
| 音频/语音 | 使用 `send_voice` — 尽可能以原生语音消息形式发送，否则作为文件附件发送 |
| 文档（PDF/ZIP/docx 等） | 使用 `send_document` — 以带下载按钮的原生附件形式发送 |

Discord 对单次上传文件的大小限制取决于服务器的升级等级：免费账户为 25 MB，高级账户最高可达 500 MB。如果 Hermes 收到 HTTP 413 错误，适配器会回退为提供指向本地缓存路径的链接，而不会静默失败。

## 接收任意类型的文件

用户上传的任何类型文件均可被接收。决定能否向代理发送消息的是授权权限，而非文件扩展名。所有上传的文件都会被下载并缓存到 `~/.hermes/cache/documents/` 目录中，随后以 `DOCUMENT` 类型的消息事件形式传递给代理，使其能够使用 `terminal`（如 `ffprobe`、`unzip`、`file`、`strings` 等命令）或 `read_file` 功能来查看文件内容。

- 已知的文件类型（PDF、docx/xlsx/pptx、zip，以及图片/音频/视频等）会保留其精确的MIME类型。  
- 未知类型的文件则会使用上传时标注的内容类型；若未指定，则默认视为`application/octet-stream`类型。  
- 小型且可被UTF-8解码的文件（如文本、代码、配置文件、HTML、CSS、JSON、YAML等），其内容会在提示词中自动嵌入，最大容量为100 KiB。而无法解码的二进制文件则仅会以路径形式作为上下文备注显示（通过`to_agent_visible_cache_path`功能，Docker/Modal沙箱终端中的内容会自动转换显示），从而避免占用过多的上下文空间。  

唯一的限制条件是单文件大小上限（默认为32 MiB）：

```yaml
discord:
  # Optional — raise/disable the per-file size cap. Default is 32 MiB.
  # The whole file is held in memory while being cached, so unlimited
  # uploads carry a real memory cost.
  max_attachment_bytes: 33554432   # bytes; 0 = unlimited
```

等效的环境变量：`DISCORD_MAX_ATTACHMENT_BYTES=33554432`（如需取消限制，则设置为`0`）。

旧的 `discord.allow_any_attachment` 标志现已失效——系统始终会接受所有类型的文件——保留该标志仅是为了避免现有配置出现错误。

:::警告 无限制带来的内存消耗
若禁用大小限制（将 `max_attachment_bytes` 设置为 `0`），用户即可向机器人上传数GB大小的文件，而网关将会在将其缓存到磁盘的同时，通过内存对其进行处理。此设置仅建议在可信的单用户环境中使用。对于共享型机器人，请保持默认的32 MiB限制或适度提高该数值。
:::

## 交互式确认提示（进一步明确需求）

当机器人调用 `clarify` 工具时——例如询问您偏好的方案、获取任务完成后的反馈，或在做出重要决策前进行确认——Discord会以**每个选项对应一个按钮**的形式展示问题：

> 我应该为控制面板选择哪种框架？
>
> [1. Next.js] [2. Remix] [3. Astro] [其他（直接输入）]

您可以点击带编号的按钮进行回答，或选择 **其他** 并输入自由文本作为答案（您在该频道发送的下一条消息即视为答案）。对于没有预设选项的开放式确认请求，系统会直接跳过按钮，等待您的下一条消息。

一旦作出选择，相关按钮就会自动失效，从而防止重复点击导致问题被多次处理。您可以通过 `~/.hermes/config.yaml` 文件中的 `agent.clarify_timeout` 参数来设置响应超时时间（默认为600秒）。如果您在超时时间内未作回应，机器人会发送一条提示信息以解除阻塞，并继续执行后续操作而不会停滞不前。

## 主频道

您可以指定一个“主频道”，让机器人在此发送主动消息（如定时任务输出、提醒及通知）。设置该频道有两种方式：

### 使用斜杠命令

在机器人所在的任意 Discord 频道中输入 `/sethome`，该频道即会成为主频道。

### 手动配置

将以下内容添加到您的 `~/.hermes/.env` 文件中：

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

请将该 ID 替换为实际的频道 ID（右键点击后选择“以开发者模式复制频道 ID”）。

## 语音消息

Hermes Agent 支持 Discord 语音消息功能：

- **传入的语音消息**会自动通过配置好的文本转语音服务进行转录，可选服务包括本地的 `faster-whisper`（无需密钥）、Groq Whisper（需提供 `GROQ_API_KEY`）或 OpenAI Whisper（需提供 `VOICE_TOOLS_OPENAI_KEY`）。
- **文本转语音**：可使用 `/voice tts` 命令，让机器人在发送文字回复的同时输出语音回应。
- **Discord 语音频道**：Hermes 还能够加入语音频道，聆听用户发言，并在频道内进行回应。

如需完整的设置与操作指南，请参阅：
- [语音模式](/user-guide/features/voice-mode)
- [在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)

### 语音频道音频效果（背景音 + 语音确认音）

当机器人处于语音频道中时，可为其增添更自然的对话感：在开始处理任务前会先发出简短的语音确认（如“让我查一下”）；而在工具运行期间，则会播放轻柔的背景“思考”音效——在说话时该音效会减弱，任务完成后又会恢复原音量，这一功能与 Grok 的语音模式类似。

由于 `discord.py` 每个连接仅支持播放一个音频流，因此 Hermes 会在输出流上安装一个软件混音器，将背景音循环、确认音以及文本转语音回复整合到同一个流中——这些音频会同时播放而不会互相干扰。

此功能**默认处于关闭状态**。如需启用，请在 `config.yaml` 文件中进行设置：

```yaml
discord:
  voice_fx:
    enabled: true          # master switch
    ambient_enabled: true  # idle "thinking" bed while tools run
    ambient_path: ""       # custom loop file (any audio format); "" = built-in synthesised pad
    ambient_gain: 0.18     # idle bed loudness (0.0–1.0)
    duck_gain: 0.06        # ambient loudness while the bot is speaking
    speech_gain: 1.0       # TTS / acknowledgement loudness
    ack_enabled: true      # speak a short phrase before the first tool call of a turn
    ack_phrases:           # picked at random; set to [] to disable the spoken ack
      - "Let me look into that."
      - "One moment."
      - "Checking on that now."
```

备注：  
- 若希望机器人始终留在语音频道中，直到收到明确的 `/voice leave` 命令或手动断开连接，请将 `voice_channel_inactivity_timeout_seconds` 设置为 `0`。默认值仍为历史设定的300秒闲置自动离开时间。  
- `voice_playback_timeout_seconds` 是最低时长限制，而非长文本语音合成的硬性上限。Hermes会检测生成的音频时长，若超过该最低值，则会等待 `时长 + 30秒` 后才开始播放。  
- 确认信号每轮最多触发一次，且仅在机器人处于语音频道且混音器处于激活状态时发送。它使用您配置的文本语音合成服务提供商。  
- `ambient_path` 可接受任何能被 `ffmpeg` 解码的文件，系统会实现无缝循环播放。如需使用内置合成音效，则可将其留空（无需额外资源）。  
- 所有设置均保存在 `config.yaml` 文件中（而非 `.env`），属于行为配置而非敏感信息。  
- 当 `voice_fx.enabled` 设置为 `false` 时，语音播放将直接使用原始的单次播放路径，其余参数保持不变。  

## 论坛频道  
Discord论坛频道（类型15）不支持私信功能——论坛中的每条内容都必须以主题帖形式存在。Hermes会自动检测论坛频道，每当需要向其中发送内容时都会创建新的主题帖，因此文本回复、文本语音合成、图片、语音消息及文件附件均无需机器人进行特殊处理即可正常使用。

- **主题名称**源自消息的第一行内容（已去除 Markdown 标题前缀，长度限制为 100 字符）。如果消息仅包含附件，则以附件的文件名为默认主题名称。
- **附件**会随新主题的初始消息一同发送——无需单独上传，也不会发生部分发送的情况。
- **一次调用，一个主题**：每次向某个论坛发送消息都会创建一个新主题。因此，后续向同一论坛的发送将会生成独立的主题。
- **检测机制分为三层**：首先查询频道目录缓存，其次是进程本地的探测缓存；最后作为兜底方案，通过实时调用 `GET /channels/{id}` 进行探测（该查询结果会被缓存，整个进程运行期间有效）。

通过刷新目录（在支持该功能的平台上使用 `/channels refresh` 命令，或重启网关），即可将机器人启动后新增的论坛频道信息加载到缓存中。

## 故障排除

### 机器人处于在线状态但未响应消息

**原因**：可能是“消息内容意图”被禁用，或是由于未配置访问策略而导致 Discord 认证失败。

**解决方法**：

1. 访问[开发者门户](https://discord.com/developers/applications)，选择您的应用 → 机器人 → 特权网关意图，启用**消息内容意图**，然后保存更改。
2. 确认已配置至少一条 Discord 访问策略：

   ```bash
   # recommended: allow specific users
   DISCORD_ALLOWED_USERS=284102345871466496

   # or allow a trusted guild/dev bot to behave like pre-0.18 Discord
   DISCORD_ALLOW_ALL_USERS=true
   ```

3. 重启网关：

   ```bash
   hermes gateway restart
   ```

如果网关日志显示已连接到 Discord 且 REST API 测试正常，但所有收到的消息都毫无响应，请在 `~/.hermes/logs/gateway.log` 文件中查看相关的警告信息：

```text
No Discord access policy configured; inbound Discord messages will be denied by default.
```

Hermes 0.18 版本会刻意拒绝与外部可访问的适配器建立连接。对于那些未设置 `DISCORD_ALLOWED_USERS`、`DISCORD_ALLOWED_ROLES`、`DISCORD_ALLOWED_CHANNELS` 选项，且也未开启“允许所有用户”功能的 Discord 机器人，虽然能够成功连接，但在开始处理正常消息之前会拒绝接收来自外部用户的请求。

### 启动时出现“特权意图”/`PrivilegedIntentsRequired` 错误

**原因**：Hermes 会请求那些在开发者门户中未被启用为你的机器人所允许的特权网关意图，从而导致 Discord 拒绝建立 WebSocket 连接。Hermes 会始终请求 **消息内容意图**。此外，当你的允许列表使用用户名（而非数字 ID）或设置了 `DISCORD_ALLOWED_ROLES` 时，它还会请求 **服务器成员意图**；而“在线状态意图”则并非必需。

**解决方法**：

1. 访问 [开发者门户](https://discord.com/developers/applications)，选择你的应用，进入“机器人”选项卡，然后查看“特权网关意图”设置。
2. 确保已启用 **消息内容意图**（这是必需的）。如果你使用的是用户名或角色允许列表，则还需启用 **服务器成员意图**。
3. 点击“保存更改”，随后重启网关（执行命令 `hermes gateway restart`）。

网关日志中会明确列出 Hermes 所请求的意图。在相关设置被启用之前，Discord 会持续拒绝连接——这属于开发者门户配置问题，而非不稳定的网络故障。

### 机器人无法查看特定频道中的消息

**原因**：该机器人的角色没有权限查看该频道。

**解决方案**：在 Discord 中，进入频道设置 → 权限设置，为机器人角色添加权限，确保已开启 **查看频道** 和 **读取消息历史记录** 的选项。

### 403 禁止访问错误

**原因**：机器人缺少必要的权限。

**解决方案**：使用第 5 步中的链接重新邀请具有正确权限的机器人，或直接在服务器设置 → 角色中手动调整机器人的权限。

### 机器人处于离线状态

**原因**：Hermes 网关未运行，或者令牌不正确。

**解决方案**：检查 `hermes gateway` 是否正在运行。确认 `.env` 文件中的 `DISCORD_BOT_TOKEN` 是否正确。如果最近已重置令牌，请及时更新。

### 出现“用户未被允许”/机器人忽略你的情况

**原因**：您的用户 ID 不在 `DISCORD_ALLOWED_USERS` 列表中。

**解决方案**：将您的用户 ID 添加到 `~/.hermes/.env` 文件中的 `DISCORD_ALLOWED_USERS` 列表中，然后重启网关。

### 同一频道内的成员意外共享上下文信息

**原因**：`group_sessions_per_user` 功能处于关闭状态，或者该平台无法为该上下文中的消息提供用户 ID。

**解决方案**：在 `~/.hermes/config.yaml` 中设置该参数，然后重启网关：

```yaml
group_sessions_per_user: true
```

如果您有意开启共享房间对话功能，请勿勾选该选项——届时对话记录和中断行为都将被共享。

## 安全性

:::warning
务必设置 `DISCORD_ALLOWED_USERS`（或 `DISCORD_ALLOWED_ROLES`）来限制可与机器人交互的用户范围。若未设置这些参数，出于安全考虑，网关将默认拒绝所有用户访问。请仅授权您信任的人员——获得授权的用户可完全使用该机器人的各项功能，包括调用工具和访问系统。
:::

### 基于角色的访问控制

对于那些通过角色而非单独用户列表来管理访问权限的服务器（如版主团队、客服人员、内部工具使用群体），请使用 `DISCORD_ALLOWED_ROLES` 参数——即以逗号分隔的角色 ID 列表。拥有这些角色中的任意一个的角色成员即具备访问权限。

```bash
# ~/.hermes/.env — works alongside or instead of DISCORD_ALLOWED_USERS
DISCORD_ALLOWED_ROLES=987654321098765432,876543210987654321
```

语义规则：

- **基于用户白名单的“或”逻辑**：若用户的 ID 在 `DISCORD_ALLOWED_USERS` 列表中，**或**其拥有 `DISCORD_ALLOWED_ROLES` 中列出的任何角色权限，则该用户即获得授权。
- **服务器成员意图自动启用**：当设置了 `DISCORD_ALLOWED_ROLES` 后，机器人会在连接时自动启用“成员意图”——这是 Discord 能够在成员记录中同步角色信息所必需的。
- **使用角色 ID 而非名称**：需从 Discord 获取相应角色 ID：进入**用户设置 → 高级设置 → 开启开发者模式**，然后右键点击任意角色选择**复制角色 ID**。
- **私信场景的兜底机制**：在私信中，角色检查会同步查看双方所在的服务器；只要用户在任意共享服务器中拥有被允许的角色权限，其在私信中同样具备访问权限。

当管理团队人员变动时，此机制是最佳选择——新成员在获得对应角色权限后即可立即使用机器人，无需修改 `.env` 配置文件或重启网关。

### 提及控制

默认情况下，即使回复内容中包含 `@everyone`、`@here` 或角色提及符号，Hermes 也会阻止机器人发送此类提及。这是为避免因表述不当的指令或用户重复发布的内容导致整个服务器被刷屏。不过，针对单个用户的 `@user` 提及以及回复引用功能（即“回复于……”的提示图标）仍会保持启用状态，以确保正常对话不受影响。

您可以通过环境变量或 `config.yaml` 文件来放宽这些默认设置：

```yaml
# ~/.hermes/config.yaml
discord:
  allow_mentions:
    everyone: false      # allow the bot to ping @everyone / @here
    roles: false         # allow the bot to ping @role mentions
    users: true          # allow the bot to ping individual @users
    replied_user: true   # ping the author when replying to their message
```

```bash
# ~/.hermes/.env — env vars win over config.yaml
DISCORD_ALLOW_MENTION_EVERYONE=false
DISCORD_ALLOW_MENTION_ROLES=false
DISCORD_ALLOW_MENTION_USERS=true
DISCORD_ALLOW_MENTION_REPLIED_USER=true
```

:::提示
除非您确实知道为何需要“everyone”和“roles”参数，否则请将其值设为“false”。大型语言模型很容易在看似正常的响应中生成`@everyone`这样的字符串；若没有此保护机制，就会向服务器中的所有成员发送通知。
:::

如需了解有关加强Hermes Agent部署安全性的更多信息，请参阅[安全指南](../security.md)。


