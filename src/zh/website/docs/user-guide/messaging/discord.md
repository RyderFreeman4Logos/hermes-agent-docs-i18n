---
sidebar_position: 3
title: "Discord"
description: "Set up Hermes Agent as a Discord bot"
---

# Discord 设置

Hermes Agent 以机器人形式集成到 Discord 中，让你能够通过私信或服务器频道与 AI 助手进行对话。该机器人会接收你的消息，通过 Hermes Agent 的处理流程（包括工具调用、内存管理和推理功能）进行处理，并实时回复。它支持文本消息、语音消息、文件附件以及斜杠命令。

在开始设置之前，这里有大多数人最关心的问题：Hermes 进入你的服务器后会如何运行？

## Hermes 的运行方式

| 场景 | 行为表现 |
|------|----------|
| **私信** | Hermes 会回复每一条消息，无需使用 `@mention`。每条私信都拥有独立的会话。 |
| **服务器频道** | 默认情况下，Hermes 仅在收到 `@mention` 提及时才会回复。如果在未提及它的频道中发消息，Hermes 会忽略该消息。 |
| **自由回复频道** | 可以通过 `DISCORD_FREE_RESPONSE_CHANNELS` 将特定频道设置为无需提及即可回复，或通过 `DISCORD_REQUIRE_MENTION=false` 全局禁用提及功能。这些频道中的消息会直接在原位置得到回复——系统不会自动创建新主题，从而保持频道的轻量级特性。 |
| **主题帖** | Hermes 会在同一主题帖中回复。除非该主题帖或其所属频道被设置为自由回复模式，否则仍需遵循提及规则。主题帖的会话历史与所属频道相互独立。 |
| **多用户共享频道** | 出于安全性和清晰度的考虑，默认情况下，Hermes 会为频道内的每位用户单独维护会话历史。除非你明确禁用此功能，否则在同一频道中交流的两个人不会共享同一个对话记录。 |
| **提及其他用户的消息** | 当 `DISCORD_IGNORE_NO_MENTION` 设为 `true`（默认值）时，如果消息提及了其他用户但未提及机器人，Hermes 会保持沉默。这样可避免机器人插手针对其他人的对话。若希望机器人无论提及谁都会回复，可将该值设为 `false`。此规则仅适用于服务器频道，不适用于私信。 |

:::提示
如果你希望创建一个普通的机器人帮助频道，让人们无需每次都提及机器人即可与 Hermes 对话，只需将该频道添加到 `DISCORD_FREE_RESPONSE_CHANNELS` 中即可。
:::

### Discord 网关模型

Discord 上的 Hermes 并非那种仅进行无状态回复的 webhook。它会经过完整的消息网关处理，这意味着每条传入的消息都要依次经历以下步骤：

1. 权限验证（`DISCORD_ALLOWED_USERS`）
2. 提及/自由回复检查
3. 会话查找
4. 加载会话对话记录
5. 执行完整的 Hermes Agent 处理流程，包括工具调用、内存管理和斜杠命令
6. 将回复发送回 Discord

这一点很重要，因为在一个繁忙的服务器中，机器人的行为既取决于 Discord 的路由机制，也取决于 Hermes 的会话策略。

### Discord 中的会话模型

默认情况下：

- 每条私信都有独立的会话
- 每个服务器主题帖都有独立的会话命名空间
- 共享频道中的每位用户在该频道内也有独立的会话

因此，即使艾丽斯和鲍勃在同一个可见的 Discord 频道 `#research` 中与 Hermes 对话，Hermes 也会默认将它们的对话视为独立的交流，因为它们拥有各自的会话。

这一行为可通过 `config.yaml` 文件进行配置：

```yaml
group_sessions_per_user: true
```

仅当您明确希望为整个房间设置单一的共享对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作交流十分有用，但同时也存在以下问题：

- 用户需要共享上下文存储空间及令牌成本  
- 某人执行的耗时且依赖大量工具的任务可能会占用其他所有人的上下文资源  
- 同一房间内，某人正在运行的任务可能会干扰另一人的后续操作  

### 干扰与并发处理

Hermes通过会话键来追踪正在运行的智能体。在默认设置`group_sessions_per_user: true`的情况下：  
- Alice中断自己正在处理的请求时，仅会影响该频道内的她的会话  
- Bob仍可在同一频道中继续发言，不会继承Alice的对话历史，也不会干扰她的任务执行  

而当设置为`group_sessions_per_user: false`时：  
- 整个房间会共享该频道/线程的一个智能体运行槽位  
- 不同用户发送的后续消息可能会互相干扰，或依次排队等待处理  

本指南将为您详细介绍完整的设置流程——从在Discord开发者门户创建机器人到发送第一条消息。  

### Gateway WebSocket运行状态监控

Discord REST接口与Gateway WebSocket属于不同的通信方式。即使REST请求返回成功响应（包括`fetch_user()`返回HTTP 200状态码），也无法保证机器人仍能接收Gateway事件。因此，Hermes会综合考量智能体的就绪状态、客户端/套接字关闭状态、套接字是否处于开放状态、心跳确认消息的延迟以及心跳延迟的上限值等指标。  

一旦出现连续指定次数的异常状态，适配器就会触发一个可重试的致命错误事件。此时，现有的网关重连监控机制会创建一个新的适配器；而Discord适配器则不会启动第二个无限制的重连循环。  

您可以在`config.yaml`文件中配置这些非敏感阈值：

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

1. 在左侧边栏中点击 **Bot**。
2. Discord 会自动为您的应用程序创建一个机器人用户。您可以看到机器人的用户名，该名称可自行修改。
3. 在 **Authorization Flow** 下方：
   - 将 **Public Bot** 设置为 **ON**——这是使用 Discord 提供的邀请链接的必要条件（推荐做法），这样“安装”选项卡就能生成默认的授权 URL。
   - 保持 **Require OAuth2 Code Grant** 的设置为 **OFF**。

:::提示
您可以在该页面为机器人设置自定义头像和横幅。这些内容就是用户在 Discord 中看到的样子。
:::

:::信息[私有机器人的替代方案]
如果您希望保持机器人私密（即将 Public Bot 设置为 OFF），则必须在第五步中使用 **Manual URL** 方法，而非“安装”选项卡。因为 Discord 提供的链接要求必须开启 Public Bot 功能。
:::

## 第三步：启用特权网关意图

这是整个设置过程中最关键的一步。如果未正确启用相应意图，您的机器人虽然能连接到 Discord，但**将无法读取消息内容**。

在 **Bot** 页面中，向下滚动至 **Privileged Gateway Intents**。您会看到三个开关：

| 意图 | 用途 | 是否必需 |
|------|------|----------|
| **Presence Intent** | 查看用户的在线/离线状态 | 可选 |
| **Server Members Intent** | 访问成员列表并解析用户名 | **必需** |
| **Message Content Intent** | 读取消息的文本内容 | **必需** |

请将 **Server Members Intent** 和 **Message Content Intent** 两个开关都切换为 **ON**。

- 如果未启用 **Message Content Intent**，机器人虽然会收到消息事件，但消息文本为空——机器人实际上无法看到您输入的内容。
- 如果未启用 **Server Members Intent**，机器人将无法解析允许通信用户的用户名，可能无法识别是谁在与其发送消息。

:::警告[这是 Discord 机器人无法正常工作的首要原因]
如果您的机器人已上线却从不回复消息，几乎可以肯定是因为 **Message Content Intent** 被禁用了。请返回 [开发者门户](https://discord.com/developers/applications)，选择您的应用程序 → Bot → Privileged Gateway Intents，确保 **Message Content Intent** 已切换为 ON 状态，然后点击 **Save Changes**。
:::

**关于服务器数量的限制：**
- 如果您的机器人仅在**100 个服务器**以内活动，可以自由地开启或关闭这些意图。
- 如果机器人已在**100 个或更多服务器**中运行，Discord 要求您提交验证申请才能使用特权意图。对于个人使用而言，这无需担心。

点击页面底部的 **Save Changes**。

## 第四步：获取机器人令牌

机器人令牌是 Hermes Agent 用于以您的机器人身份登录的凭证。仍在 **Bot** 页面上：

1. 在 **Token** 区域下方，点击 **Reset Token**。
2. 如果您的 Discord 账户已启用双重认证，请输入相应的 2FA 码。
3. Discord 会显示新的令牌，请**立即复制它**。

:::警告[令牌仅显示一次]
该令牌只会显示一次。一旦丢失，您需要重新生成新的令牌。切勿公开分享您的令牌，也不要将其提交到 Git——拥有该令牌的人即可完全控制您的机器人。
:::

请将令牌存储在安全的地方（例如密码管理器），因为第八步时会用到它。

## 第五步：生成邀请链接

您需要一个 OAuth2 链接，以便将机器人邀请到您的服务器。有两种实现方式：

### 方案 A：使用“安装”选项卡（推荐）

:::注意[需要开启 Public Bot]
此方法要求在第一步中将 **Public Bot** 设置为 **ON**。如果您将其设置为 OFF，请改用下方的手动 URL 方法。
:::

1. 在左侧边栏中点击 **Installation**。
2. 在 **Installation Contexts** 下方，启用 **Guild Install**。
3. 对于 **Install Link**，选择 **Discord Provided Link**。
4. 在 **Guild Install** 的 **Default Install Settings** 中：
   - **Scopes**：选择 `bot` 和 `applications.commands`
   - **Permissions**：选择下方列出的权限。

### 方案 B：手动生成 URL

您也可以直接使用以下格式来构建邀请链接：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

请将 `YOUR_APP_ID` 替换为步骤 1 中获取的应用程序 ID。

### 必需权限

以下是您的机器人所需的最低权限：

- **查看频道** — 查看其有权访问的频道
- **发送消息** — 回复您的消息
- **嵌入链接** — 格式化丰富回复内容
- **附加文件** — 发送图片、音频及文件输出
- **读取消息历史记录** — 保留对话上下文

### 推荐的额外权限

- **在主题对话中发送消息** — 在主题对话中进行回复
- **添加表情反应** — 通过表情反应确认收到消息

### 权限整数值

| 等级 | 权限整数值 | 包含的权限 |
|-------|------------|------------|
| 最低要求 | `117760` | 查看频道、发送消息、读取消息历史记录、附加文件 |
| 推荐配置 | `274878286912` | 上述所有权限外加嵌入链接、在主题对话中发送消息、添加表情反应 |

## 第 6 步：邀请机器人到您的服务器

1. 在浏览器中打开邀请链接（可从“安装”选项卡或您手动生成的链接获取）。
2. 在 **添加到服务器** 下拉列表中选择您的服务器。
3. 点击 **继续**，然后点击 **授权**。
4. 如有提示，请完成验证码验证。

:::info
若要邀请机器人，您需要在 Discord 服务器中拥有 **管理服务器** 权限。如果下拉列表中没有显示您的服务器，请让服务器管理员使用邀请链接。
:::

授权完成后，该机器人将出现在您服务器的成员列表中（在启动 Hermes 网关之前，它会显示为离线状态）。

## 第 7 步：查找您的 Discord 用户 ID

Hermes Agent 会利用您的 Discord 用户 ID 来控制哪些用户可以与机器人交互。具体操作如下：

1. 打开 Discord（桌面版或网页版）。
2. 进入 **设置** → **高级设置**，将 **开发者模式** 开启。
3. 关闭设置窗口。
4. 在消息、成员列表或个人资料中右键点击自己的用户名，然后选择 **复制用户 ID**。

您的用户 ID 是一个类似 `284102345871466496` 的长数字。

:::tip
开发者模式还允许您以相同方式复制 **频道 ID** 和 **服务器 ID** — 右键点击频道或服务器名称，然后选择“复制 ID”。如果您想手动设置主频道，则需要频道 ID。
:::

## 第 8 步：配置 Hermes Agent

### 方案 A：交互式设置（推荐）

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

该机器人应在几秒内出现在 Discord 中。您可以向其发送消息——无论是私信还是发送到它能看到的频道——以此进行测试。

:::提示
您可以将 `hermes gateway` 在后台运行或作为 systemd 服务运行，以实现持续运行。详情请参阅部署文档。
:::

## 配置参考

Discord 的行为通过两个文件来控制：**`~/.hermes/.env`** 用于存储凭证和环境级开关，而 **`~/.hermes/config.yaml`** 则用于存储结构化设置。当两者都设置有值时，环境变量始终优先于 config.yaml 中的数值。

### 环境变量（`.env`）

| 变量 | 是否必填 | 默认值 | 描述 |
|------|----------|--------|------|
| `DISCORD_BOT_TOKEN` | **是** | — | 来自 [Discord 开发者门户](https://discord.com/developers/applications) 的机器人令牌。 |
| `DISCORD_ALLOWED_USERS` | 条件性 | — | 以逗号分隔的、允许与机器人交互的 Discord 用户 ID。如果没有设置此变量**或** `DISCORD_ALLOWED_ROLES`，除非设置了 `DISCORD_ALLOW_ALL_USERS=true`、`GATEWAY_ALLOW_ALL_USERS=true` 或 `DISCORD_ALLOWED_CHANNELS` 明确限定了服务器访问权限，否则网关会拒绝所有用户访问。 |
| `DISCORD_ALLOWED_ROLES` | 否 | — | 以逗号分隔的 Discord 角色 ID。拥有这些角色中的任意一个的角色成员即被授权——该设置与 `DISCORD_ALLOWED_USERS` 具有互斥逻辑。连接时会自动启用 **Server Members Intent**。当管理团队频繁变动时非常有用：新管理员一旦被授予相应角色即可获得访问权限，无需推送配置。 |
| `DISCORD_ALLOW_ALL_USERS` | 否 | `false` | 明确允许所有能够找到该机器人的 Discord 用户访问。此设置仅恢复 0.18 版本之前的开放行为，仅适用于可信的私人服务器或开发环境。 |
| `GATEWAY_ALLOW_ALL_USERS` | 否 | `false` | 为所有网关平台提供的全局“允许所有人”选项。除非您有意让所有连接的平台都保持开放状态，否则建议优先使用特定平台的 `DISCORD_ALLOW_ALL_USERS` 设置。 |
| `DISCORD_HOME_CHANNEL` | 否 | — | 机器人用于发送主动消息（如定时任务输出、提醒、通知等）的频道 ID。 |
| `DISCORD_HOME_CHANNEL_NAME` | 否 | `"Home"` | 日志和状态输出中显示的频道名称。 |
| `DISCORD_COMMAND_SYNC_POLICY` | 否 | `"safe"` | 控制原生斜杠命令的启动同步方式。`"safe"` 模式会对比现有的全局命令，仅更新发生变化的部分；当 Discord 元数据变更无法通过补丁应用时，会重新生成命令。`"bulk"` 模式则保持旧的 `tree.sync()` 行为。`"off"` 模式则完全跳过启动同步。 |
| `DISCORD_REQUIRE_MENTION` | 否 | `true` | 当该设置为 `true` 时，机器人仅在被 `@mentioned` 时才会在服务器频道中回复。将其设置为 `false` 可让机器人在所有频道的所有消息中都做出回复。 |
| `DISCORD_THREAD_REQUIRE_MENTION` | 否 | `false` | 当该设置为 `true` 时，会禁用线程内的提及快捷方式——此时线程的访问规则与频道相同，即使机器人已经参与了对话，也必须通过 `@mention` 才能触发回复。当多个机器人共享一个线程且您希望每个机器人仅在收到明确 `@mention` 时才响应时，可使用此设置。 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 否 | — | 以逗号分隔的频道 ID，即使 `DISCORD_REQUIRE_MENTION` 为 `true`，机器人也会在这些频道中无需 `@mention` 即可回复。 |
| `DISCORD_IGNORE_NO_MENTION` | 否 | `true` | 当该设置为 `true` 时，如果消息提及了其他用户但**未提及**机器人，机器人将保持沉默。这可以防止机器人擅自介入针对其他人的对话。此设置仅适用于服务器频道，不适用于私信。 |
| `DISCORD_AUTO_THREAD` | 否 | `true` | 当该设置为 `true` 时，机器人会在文本频道中每个 `@mention` 都自动创建一个新线程，从而使每段对话相互隔离（类似 Slack 的行为）。已存在于线程或私信中的消息不受影响。 |
| `DISCORD_ALLOW_BOTS` | 否 | `"none"` | 控制机器人如何处理来自其他 Discord 机器人的消息。`"none"` —— 忽略所有其他机器人；`"mentions"` —— 仅接受提及 Hermes 的机器人消息；`"all"` —— 接受所有机器人消息。 |
| `DISCORD_REACTIONS` | 否 | `true` | 当该设置为 `true` 时，机器人会在处理消息时添加表情符号反应（启动时为 👀，成功时为 ✅，失败时为 ❌）。将其设置为 `false` 可完全禁用反应功能。 |
| `DISCORD_IGNORED_CHANNELS` | 否 | — | 以逗号分隔的频道 ID，即使被 `@mentioned`，机器人也**绝不会**在这些频道中回复。此设置的优先级高于所有其他频道相关设置。 |
| `DISCORD_ALLOWED_CHANNELS` | 否 | — | 以逗号分隔的频道 ID。一旦设置此值，机器人将**仅**在这些频道中回复（如果允许的话，也会在私信中回复）。该设置会覆盖 `config.yaml` 中的 `discord.allowed_channels`。可结合 `DISCORD_IGNORED_CHANNELS` 来定义允许/拒绝规则。 |
| `DISCORD_NO_THREAD_CHANNELS` | 否 | — | 以逗号分隔的频道 ID，机器人会在这些频道中直接回复，而不会创建线程。此设置仅在 `DISCORD_AUTO_THREAD` 为 `true` 时有效。 |
| `DISCORD_HISTORY_BACKFILL` | 否 | `true` | 当该设置为 `true` 时，当有人提及机器人时，机器人会在用户消息前补充最近的频道滚动内容（即自机器人上次回复以来的内容）。这有助于恢复在“必须提及”模式下可能丢失的上下文。私信和自由回复频道中此功能会被跳过。将其设置为 `false` 可禁用该功能。 |
| `DISCORD_HISTORY_BACKFILL_LIMIT` | 否 | `50` | 在构建补充内容块时，向后扫描的最大消息数量。实际上，扫描通常会在更早的时候停止——即到达机器人在该频道中的最后一条消息。 |
| `DISCORD_REPLY_TO_MODE` | 否 | `"first"` | 控制回复引用行为：`"off"` —— 永不回复原始消息；`"first"` —— 仅在第一个消息块中添加回复引用（默认值）；`"all"` —— 在每个消息块中都添加回复引用。 |
| `DISCORD_ALLOW_MENTION_EVERYONE` | 否 | `false` | 当该设置为 `false`（默认值）时，即使机器人回复中包含了 `@everyone` 或 `@here` 这些标记，它也无法发送这些提及。将其设置为 `true` 可重新启用此功能。详情请参见下文的 [提及控制](#mention-control) 部分。 |
| `DISCORD_ALLOW_MENTION_ROLES` | 否 | `false` | 当该设置为 `false`（默认值）时，机器人无法处理 `@role` 形式的提及。将其设置为 `true` 可允许此类提及。 |
| `DISCORD_ALLOW_MENTION_USERS` | 否 | `true` | 当该设置为 `true`（默认值）时，机器人可以根据用户 ID 提及特定用户。 |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | 否 | `true` | 当该设置为 `true`（默认值）时，回复消息时会自动提及原始发件人。 |
| `DISCORD_PROXY` | 否 | — | 用于连接 Discord 的代理服务器 URL（支持 HTTP、WebSocket、REST 协议）。此设置会覆盖 `HTTPS_PROXY`/`ALL_PROXY` 的值。支持 `http://`、`https://` 和 `socks5://` 协议。 |
| `DISCORD_ALLOW_ANY_ATTACHMENT` | 否 | `false` | 当该设置为 `true` 时，机器人将接受所有类型的附件（而不仅限于内置的 PDF、文本、zip、Office 文件类型）。未知类型的附件会被缓存到磁盘，并以 `application/octet-stream` 的 MIME 类型作为本地路径呈现给代理，以便其使用 `terminal` / `read_file` / `ffprobe` 等工具进行查看。 |
| `DISCORD_MAX_ATTACHMENT_BYTES` | 否 | `33554432` | 网关下载并缓存每个附件的最大字节数。默认值为 32 MiB。将其设置为 `0` 可取消字节数限制（由于附件在写入时会保留在内存中，因此无限制会带来较大的内存消耗）。 |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | 否 | `0.6` | 适配器在刷新已排队的文本块之前等待的缓冲时间。有助于平滑流式输出。 |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 否 | `2.0` | 当单条消息超过 Discord 的长度限制时，分割各部分之间的延迟时间。 |

:::警告 不支持机器人之间的对话
设置 `DISCORD_ALLOW_BOTS` 的目的是允许来自特定可信机器人的输入（例如中继机器人或 webhook 机器人），而非让两个 Hermes 账户之间互相通信。默认值 `"none"` 会忽略所有其他机器人，是较为安全的设置。

通过为多个 Hermes 账户分别设置 `"mentions"` 或 `"all"`，使其在同一个共享频道中互相回复，这种拓扑结构目前不受支持。Discord 会在每次回复时自动提及被回复的发件人，因此在 `"mentions"` 模式下，两个机器人会无限循环地满足对方的提及条件，从而导致确认循环。由于支持的配置方式就是将 `DISCORD_ALLOW_BOTS` 保持为 `"none"`，因此不存在相应的断路器机制。如果您确实需要接受某个特定机器人，应将其允许范围限定得尽可能狭窄，且绝不能让其与其他自动回复的代理交互。
:::

### 配置文件（`config.yaml`）

`~/.hermes/config.yaml` 文件中的 `discord` 部分与上述环境变量对应。config.yaml 中的设置将作为默认值应用——如果相应的环境变量已设置，环境变量的值将优先生效。

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

启用该选项后，机器人仅会在被直接`@提及`时才在服务器频道中回复。而无论此设置如何，私信始终会收到回复。

#### `discord.thread_require_mention`

**类型：** 布尔值 — **默认值：** `false`

默认情况下，一旦机器人参与了某个主题帖（无论是通过被`@提及`自动创建的，还是首次回复后形成的），它就会持续回复该主题帖中的后续消息，无需再次被`@提及`。这对于一对一对话而言是合理的默认设置。

但在**多机器人主题帖**中——即用户轮流向不同机器人发送消息的场景——这种默认设置反而会带来问题：主题帖中的其他机器人也会对每一条消息作出回复，从而导致资源浪费并造成频道信息过载。将`thread_require_mention`设置为`true`即可取消这一主题帖内的快捷回复功能，使主题帖的响应规则与普通频道保持一致。不过，明确的`@提及`操作仍会像以前一样正常生效。

```yaml
discord:
  require_mention: true
  thread_require_mention: true    # multi-bot setup
```

#### `discord.free_response_channels`

**类型：** 字符串或列表 — **默认值：** `""`

指定机器人无需通过`@mention`即可回复所有消息的频道ID。可接受以逗号分隔的字符串形式，或YAML列表形式：

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

如果某个帖子的父频道在列表中，该帖子也将不会被提及。  

“自由回复频道”还会**跳过自动分线程功能**——机器人会直接在原消息下方回复，而不会为每条消息创建新帖子。这样就能让该频道继续作为轻量级的聊天空间使用。如果您需要分线程功能，请勿将频道标记为自由回复频道（应改用常规的`@mention`机制）。  

#### `discord.auto_thread`

**类型：** 布尔值 — **默认值：** `true`  

启用此功能后，普通文本频道中的每个`@mention`都会自动为对应对话创建一个新帖子。这样既能保持主频道的整洁，又能让每段对话拥有独立的会话历史记录。一旦创建了帖子，后续发送到该帖子的消息就无需再使用`@mention`——因为机器人已经知道自己在参与该对话。在多机器人配置中，若要禁用此内嵌回复快捷方式，请将[`thread_require_mention`](#discordthread_require_mention)设置为`true`。  

已存在的帖子或私信中的消息不受此设置影响。被列入`discord.free_response_channels`或`discord.no_thread_channels`的频道同样会跳过自动分线程功能，机器人会直接在这些频道中回复。  

#### `discord.reactions`

**类型：** 布尔值 — **默认值：** `true`  

用于控制机器人是否为消息添加表情符号反应作为视觉反馈：  
- 当机器人开始处理您的消息时，会添加👀；  
- 当回复成功发送时，会添加✅；  
- 如果处理过程中出现错误，则会添加❌。  

如果您觉得这些反应干扰了聊天体验，或者机器人的角色没有**添加反应**权限，可以禁用此功能。  

#### `discord.ignored_channels`

**类型：** 字符串或列表 — **默认值：** `[]`  

指定机器人**永远不回复**的频道ID，即便这些频道被直接`@提及`也不例外。此设置具有最高优先级——只要频道在列表中，无论`require_mention`、`free_response_channels`或其他任何设置如何，机器人都会完全忽略该频道中的所有消息。

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

如果某个帖子的父频道在列表中，该帖子中的消息也会被忽略。

#### `discord.no_thread_channels`

**类型：** 字符串或列表 — **默认值：** `[]`

指定机器人将直接在这些频道中回复消息，而不会自动创建新帖子。此设置仅在 `auto_thread` 设为 `true`（即默认值）时生效。在这些频道中，机器人会以普通消息的形式直接回复，而不会生成新的帖子。

```yaml
discord:
  no_thread_channels:
    - 1234567890  # Bot responds inline here
```

对于那些专门用于机器人与用户交互的频道而言，此功能非常实用——因为在这些频道中，过多的对话线程只会增添不必要的干扰。

#### `discord.channel_prompts`

**类型：** 映射 — **默认值：** `{}`

用于在指定的 Discord 频道或对话线程中的每一轮对话中自动插入的临时系统提示语，且不会被保存到对话记录中。

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
- 如果消息出现在某个线程或帖子中，而该线程没有对应的显式条目，Hermes 会回退使用其所属的父频道/论坛 ID。
- 提示信息会在运行时临时应用，因此修改这些提示会立即影响后续对话，而无需重写之前的会话记录。

#### `discord.history_backfill`

**类型：** 布尔值 — **默认值：** `true`

启用此功能后，机器人会在每次收到 `@mention` 时补全遗漏的频道消息。若设置 `require_mention: true`，机器人仅处理直接提及它的消息——频道中的其他所有消息都不会出现在会话记录中。该功能在触发时会回溯最近的频道历史记录，收集机器人上次回复与当前提及之间的消息，并将其作为上下文包含进来。

不同场景下的行为表现：
- **服务器频道**（当 `require_mention: true` 时）：补全功能会扫描从机器人上次回复之后的所有消息。这在其他参与者在机器人未被提及时发消息的情况下非常有用。
- **线程**：补全功能仅扫描该线程本身——Discord 的 `channel.history()` 函数在获取线程信息时只会返回该线程内的消息，而不会包含父频道的内容。由于线程通常是独立的对话单元，因此这种范围设置更为合适。
- **私信**：会被跳过。因为每条私信都会触发机器人响应，所以会话记录已经完整，无需再填补任何缺失内容。
- **自由回复频道**以及**机器人自行创建的线程**：出于相同原因也会被跳过——由于没有提及限制，因此不存在需要补全的空白。

针对按用户管理的会话（默认值为 `group_sessions_per_user: true`）而言，该功能同样有益：用户的会话中可能缺少其他频道参与者发布的消息，以及用户在主动提及机器人之前发送的消息。补全功能可以填补这两方面的缺失。

```yaml
discord:
  history_backfill: true   # default
```

如需关闭该功能：

```yaml
discord:
  history_backfill: false
```

> **注意：**在机器人正在处理消息期间（即从触发事件到其响应之间）传入的消息将不会被捕获。这是一种公认的简化处理方式——用户可以重新发送消息或再次添加标签。

#### `discord.history_backfill_limit`

**类型：**整数 — **默认值：**`50`

用于在恢复频道上下文时向后扫描的最大消息数量。实际上，扫描通常会在更早的时候停止——即机器人在该频道中发出的最后一条消息处，因为那通常是不同轮次交流的自然分界点。此限制旨在为机器人冷启动以及近期历史记录中不存在任何先前消息的长时间间隔情况提供保障。

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

这是一个全局网关设置（与 Discord 无关），用于控制同一频道内的用户是否拥有独立的会话历史记录。

当值为 `true` 时：在 `#research` 频道中交流的 Alice 和 Bob 每人都会与 Hermes 维持独立的对话记录。当值为 `false` 时：整个频道共享同一份对话记录以及一个正在运行的机器人实例。

```yaml
group_sessions_per_user: true
```

如需了解各模式的详细作用，请参阅上文的[会话模型](#session-model-in-discord)部分。

#### `display.tool_progress`

**类型：** 字符串 — **默认值：** `"all"` — **可选值：** `off`、`new`、`all`、`verbose`

用于控制机器人在处理任务时是否在聊天窗口中发送进度信息（例如“正在读取文件...”、“正在执行终端命令...”）。这是一个全局设置，适用于所有平台。

```yaml
display:
  tool_progress: "all"    # off | new | all | verbose
```

- `off` — 不显示进度信息  
- `new` — 每轮仅显示第一次工具调用记录  
- `all` — 显示所有工具调用记录（在网关消息中会截断至40个字符）  
- `verbose` — 显示完整的工具调用详情（可能会生成较长的消息）  

#### `display.tool_progress_command`

**类型：** 布尔值 — **默认值：** `false`  

启用该选项后，网关中将提供 `/verbose` 接口命令，无需编辑 config.yaml 即可循环切换不同的工具进度显示模式（`off → new → all → verbose → off`）。

```yaml
display:
  tool_progress_command: true
```

## Slash命令访问控制

默认情况下，所有获授权的用户均可使用所有Slash命令。若希望将权限列表划分为**管理员**（可使用所有Slash命令）和**普通用户**（仅能使用明确启用的命令），可在Discord平台的`extra`字段中添加`allow_admin_from`与`user_allowed_commands`参数：

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

- 属于某个范围（私信或服务器频道）的 `allow_admin_from` 列表中的用户，可通过实时命令注册表运行**所有**已注册的斜杠命令——包括内置命令和插件注册的命令。
- 不在 `allow_admin_from` 列表中的用户，仅能运行 `user_allowed_commands` 中列出的命令，以及始终允许使用的命令 `/help` 和 `/whoami`。
- 普通聊天内容（非斜杠消息）不受影响。非管理员用户仍可正常与智能体对话，只是无法触发任意命令。
- **向后兼容性**：如果某个范围未设置 `allow_admin_from`，则该范围的斜杠命令限制将被禁用。现有安装无需更改即可继续正常工作。
- 私信中的管理员身份并不等同于服务器频道中的管理员身份。每个范围都有独立的管理员列表。

可使用 `/whoami` 命令查看当前所处的作用范围、您的权限等级（管理员/用户/无限制），以及您可以运行的斜杠命令。

## 交互式模型选择器

在 Discord 频道中发送不带参数的 `/model` 命令，即可打开基于下拉菜单的模型选择器：

1. **提供商选择**——一个下拉列表，显示可用的提供商（最多25个）。
2. **模型选择**——另一个下拉列表，展示所选提供商对应的模型（最多25个）。

该选择器在120秒后超时。仅授权用户（即列入 `DISCORD_ALLOWED_USERS` 的用户）才能使用它。如果您已知模型名称，可直接输入 `/model <名称>`。

## 技能的原生斜杠命令

Hermes 会自动将已安装的技能注册为**Discord 原生应用命令**。这意味着这些技能会与内置命令一同出现在 Discord 的自动补全 `/` 菜单中。

- 每个技能都会变成一个 Discord 斜杠命令（例如 `/code-review`、`/ascii-art`）。
- 这些技能可接受可选的 `args` 字符串参数。
- Discord 对每个机器人的应用命令数量有限制，为100个——如果您的技能数量超过此限制，多余的技能将会被跳过，并在日志中留下警告信息。
- 技能会在机器人启动时与 `/model`、`/reset` 和 `/background` 等内置命令一同被注册。

无需额外配置——通过 `hermes skills install` 安装的任何技能，都将在下一次网关重启时自动作为 Discord 斜杠命令进行注册。

### 禁用斜杠命令注册

如果您针对同一个 Discord 应用运行多个 Hermes 网关（例如测试环境与生产环境），则应仅让其中一个网关负责全局斜杠命令的注册——否则最后启动的网关会覆盖之前的设置，导致注册状态频繁变动。请在“从属”网关上关闭斜杠命令注册功能。

```yaml
gateway:
  platforms:
    discord:
      extra:
        slash_commands: false   # default: true
```

将“主”网关的此参数设置为 `true` 可保持原有行为——即使用全局 `/` 菜单来调用内置技能及已安装的技能。

## 发送媒体文件（内联 `MEDIA:` 标签）

Discord 适配器支持通过智能体响应中生成的内联 `MEDIA:/path/to/file` 标签，为各类常见媒体类型直接上传文件——该适配器会自动解析标签并完成文件上传：

| 类型 | 传输方式 |
|---|---|
| 图片（PNG/JPG/WebP） | 以 Discord 原生图片附件形式发送，并附带内联预览 |
| 动画 GIF | 通过 `send_animation` 以 `animation.gif` 格式上传，让 Discord 以内联方式播放（而非静态缩略图） |
| 视频（MP4/MOV） | 使用 `send_video` —— 由 Discord 原生视频播放器播放 |
| 音频/语音 | 使用 `send_voice` —— 尽可能以原生语音消息形式发送，否则作为文件附件 |
| 文档（PDF/ZIP/docx 等） | 使用 `send_document` —— 以带有下载按钮的原生附件形式呈现 |

Discord 对单次上传文件的大小限制取决于服务器的升级等级：免费账户为 25 MB，高级账户最高可达 500 MB。如果 Hermes 收到 HTTP 413 错误，适配器会回退为提供指向本地缓存路径的链接，而不会静默失败。

## 接收任意类型的文件

用户上传的任何类型文件均可被接收。决定文件能否被智能体处理的关键在于是否拥有发送消息的权限，而非文件扩展名。所有上传的文件都会被下载并缓存在 `~/.hermes/cache/documents/` 目录下，随后以 `DOCUMENT` 类型的消息事件形式传递给智能体，使其能够通过 `terminal`（如 `ffprobe`、`unzip`、`file`、`strings` 等工具）或 `read_file` 函数来查看文件内容。

- 已知的文件类型（PDF、docx/xlsx/pptx、zip、图片/音频/视频等）会保留其精确的 MIME 类型。
- 未知类型的文件则默认使用上传时声明的内容类型，若未指定则视为 `application/octet-stream`。
- 小型的、可 UTF-8 解码的文件（文本、代码、配置文件、HTML、CSS、JSON、YAML 等），其内容最多可自动注入到提示词中，上限为 100 KiB。无法解码的二进制文件则仅会以指向文件路径的上下文备注形式呈现（通过 `to_agent_visible_cache_path` 功能，Docker/Modal 沙箱终端中的备注会自动翻译），从而避免占用过多上下文空间。

唯一的限制条件仍是单文件大小上限（默认为 32 MiB）：

```yaml
discord:
  # Optional — raise/disable the per-file size cap. Default is 32 MiB.
  # The whole file is held in memory while being cached, so unlimited
  # uploads carry a real memory cost.
  max_attachment_bytes: 33554432   # bytes; 0 = unlimited
```

对应的环境变量为：`DISCORD_MAX_ATTACHMENT_BYTES=33554432`（如需取消限制，则设置为 `0`）。

旧的 `discord.allow_any_attachment` 标志现已失效——所有文件类型都将被允许通过——保留该标志仅是为了避免现有配置出现错误。

:::警告 无限制带来的内存消耗
若禁用大小限制（将 `max_attachment_bytes` 设置为 `0`），用户即可向机器人上传数GB大小的文件，而网关将会在将其缓存到磁盘的同时，通过内存对其进行处理。此设置仅建议在可信的单用户环境中使用。对于共享型机器人，建议保持默认的32 MiB限制或适度提高该数值。
:::

## 交互式确认提示（进一步明确需求）

当机器人调用 `clarify` 工具时——例如询问您偏好的方案、收集任务完成后的反馈，或在做出重要决策前进行确认——Discord会以**每个选项对应一个按钮**的形式展示问题：

> 我应该为控制面板选择哪种框架？
>
> [1. Next.js] [2. Remix] [3. Astro] [其他（直接输入）]

您可以点击编号按钮进行回答，或选择 **其他** 并输入自由文本作为答复（您在该频道发送的下一条消息即视为答案）。对于没有预设选项的开放式确认请求，Discord会直接忽略按钮，等待您的下一条消息。

一旦用户作出选择，相应按钮就会自动失效，从而防止重复点击导致问题被多次处理。您可以通过 `~/.hermes/config.yaml` 文件中的 `agent.clarify_timeout` 参数来设置响应超时时间（默认为600秒）。若在规定时间内未收到回复，机器人会发送一条提示信息以解除阻塞，并继续正常工作而不会挂起。

## 主频道

您可以指定一个“主频道”，让机器人向该频道发送主动消息（如定时任务执行结果、提醒及通知等）。设置主频道有两种方式：

### 使用斜杠命令

在机器人所在的任意Discord频道中输入 `/sethome`，该频道即会被设为主频道。

### 手动配置

在您的 `~/.hermes/.env` 文件中添加以下内容：

```bash
DISCORD_HOME_CHANNEL=123456789012345678
DISCORD_HOME_CHANNEL_NAME="#bot-updates"
```

请将该 ID 替换为实际的频道 ID（右键点击后选择“以开发者模式复制频道 ID”）。

## 语音消息

Hermes Agent 支持 Discord 语音消息功能：

- **传入的语音消息**会自动通过配置好的文本转语音服务进行转录，可选服务包括本地的 `faster-whisper`（无需密钥）、Groq Whisper（需提供 `GROQ_API_KEY`）或 OpenAI Whisper（需提供 `VOICE_TOOLS_OPENAI_KEY`）。
- **文本转语音**：可使用 `/voice tts` 命令，让机器人同时发送语音回复和文字回复。
- **Discord 语音频道**：Hermes 还可以加入语音频道，聆听用户发言，并在频道内进行回应。

如需完整的设置与操作指南，请参阅：
- [语音模式](/user-guide/features/voice-mode)
- [如何在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)

### 语音频道音频效果（背景音 + 口头确认音）

当机器人处于语音频道中时，可为其增添更自然的对话感：在开始处理任务前会先有简短的口头确认语（如“让我查一下”）；而在工具运行期间，则会播放轻柔的背景“思考”音效——说话时该背景音会减弱，任务完成后又会恢复原音，这一效果与 Grok 的语音模式类似。

由于 discord.py 每个连接仅支持播放一个音频流，因此 Hermes 会在输出流上安装一个软件混音器，将背景音循环、确认语及文本转语音回复整合到同一个流中——这些音频会同步播放而非互相干扰。

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

注意事项：  
- 确认音效最多每轮触发一次，且仅当机器人处于语音频道且混音器处于启用状态时才会触发。该功能会使用您配置的文本转语音服务提供商。  
- `ambient_path` 可接受任何 `ffmpeg` 能够解码的文件格式，系统会对其进行无缝循环播放。若留空，则会使用内置的合成背景音（无需额外资源）。  
- 所有设置均保存在 `config.yaml` 文件中（而非 `.env`），这些为行为配置而非敏感信息。  
- 当 `voice_fx.enabled` 设置为 `false` 时，语音播放将直接使用原始的单次播放路径，其他设置不会发生变化。  

## 论坛频道  

Discord 论坛频道（类型 15）不支持直接消息发送——论坛中的每条内容都必须以主题帖形式存在。Hermes 会自动检测论坛频道，每当需要向其中发送内容时都会创建一个新的主题帖，因此文本回复、文本转语音、图片、语音消息以及文件附件均可正常发送，无需机器人进行特殊处理。  

- **主题帖名称**源自消息的第一行内容（去除 Markdown 标题前缀后，长度限制为 100 字符）。如果消息仅包含附件，则会使用附件的文件名作为主题帖名称。  
- **附件**会随新创建的主题帖一同发送——无需单独上传步骤，也不会出现部分发送的情况。  
- **一次发送，一个主题帖**：每次向论坛发送内容都会生成一个新的主题帖。因此，后续对同一论坛的多次发送将会产生多个独立的主题帖。  
- **多层检测机制**：首先查询频道目录缓存，若未找到则查询进程本地的探测缓存，最后作为兜底方案查询实时接口 `GET /channels/{id}`（其返回结果会被缓存，整个进程运行期间有效）。  

若要更新目录列表（在支持该功能的平台上可使用 `/channels refresh` 命令，或重启网关），即可将机器人启动后新增的论坛频道加入缓存中。  

## 故障排除  

### 机器人处于在线状态但未响应消息  

**原因**：可能是“消息内容意图”被禁用，或是由于未配置访问策略导致 Discord 认证失败。  

**解决方法**：  
1. 访问 [开发者门户](https://discord.com/developers/applications)，选择您的应用 → 机器人 → 特权网关意图，启用 **消息内容意图**，然后保存更改。  
2. 确认已配置至少一个 Discord 访问策略：

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

如果网关日志显示已连接到 Discord 且 REST API 测试正常，但所有收到的消息都毫无响应，请在 `~/.hermes/logs/gateway.log` 文件中查看此警告信息：

```text
No Discord access policy configured; inbound Discord messages will be denied by default.
```

Hermes 0.18 版本会刻意拒绝与外部可访问的适配器建立连接。对于那些未设置 `DISCORD_ALLOWED_USERS`、`DISCORD_ALLOWED_ROLES`、`DISCORD_ALLOWED_CHANNELS` 且也未开启“允许所有用户”选项的 Discord 机器人，虽然能够成功连接，但在开始处理正常消息之前会拒绝接收来自其他用户的请求。

### 启动时出现“不允许的意图”错误

**原因**：您的代码请求了在开发者门户中未被启用的意图。

**解决方案**：在机器人设置中启用全部三种特权网关意图（在线状态、服务器成员、消息内容），随后重启机器人。

### 机器人无法查看特定频道中的消息

**原因**：机器人的角色没有权限查看该频道。

**解决方案**：在 Discord 中进入该频道的设置 → 权限选项，为机器人的角色添加权限，确保已勾选“查看频道”和“读取消息历史记录”。

### 出现 403 禁止访问错误

**原因**：机器人缺少必要的权限。

**解决方案**：使用第 5 步中的链接重新邀请机器人，并为其分配正确的权限；或者直接在服务器设置 → 角色中手动调整机器人的权限。

### 机器人处于离线状态

**原因**：Hermes 网关未运行，或是令牌不正确。

**解决方案**：检查 `hermes gateway` 是否正在运行。确认 `.env` 文件中的 `DISCORD_BOT_TOKEN` 值是否正确。如果您最近重置了令牌，请及时更新它。

### 出现“用户未被允许”/机器人忽略您的情况

**原因**：您的用户 ID 不在 `DISCORD_ALLOWED_USERS` 列表中。

**解决方案**：在 `~/.hermes/.env` 文件中将您的用户 ID 添加到 `DISCORD_ALLOWED_USERS` 中，然后重启网关。

### 同一频道内的用户会意外共享上下文信息

**原因**：`group_sessions_per_user` 功能处于关闭状态，或者该平台无法为该上下文中的消息生成用户 ID。

**解决方案**：在 `~/.hermes/config.yaml` 文件中设置该参数，然后重启网关即可。

```yaml
group_sessions_per_user: true
```

如果您有意进行群组对话，无需设置此项——但请注意，此时对话记录和打断行为将会被共享。

## 安全性

:::warning
务必设置 `DISCORD_ALLOWED_USERS`（或 `DISCORD_ALLOWED_ROLES`）来限制可与机器人交互的用户范围。若未设置这些参数，出于安全考虑，网关将默认拒绝所有用户访问。请仅授权您信任的人员——获得授权的用户可完全使用该机器人的各项功能，包括调用工具和访问系统。
:::

### 基于角色的访问控制

对于通过角色而非单独用户列表来管理访问权限的服务器（如版主团队、客服人员、内部工具平台），请使用 `DISCORD_ALLOWED_ROLES` —— 即以逗号分隔的角色 ID 列表。拥有这些角色中的任意一个的角色成员即具备访问权限。

```bash
# ~/.hermes/.env — works alongside or instead of DISCORD_ALLOWED_USERS
DISCORD_ALLOWED_ROLES=987654321098765432,876543210987654321
```

语义规则：

- **用户白名单模式**：若用户的 ID 在 `DISCORD_ALLOWED_USERS` 列表中，**或**其拥有 `DISCORD_ALLOWED_ROLES` 中列出的任何角色权限，则该用户即被授权使用。
- **服务器成员意图自动启用**：当设置了 `DISCORD_ALLOWED_ROLES` 后，机器人会在连接时自动启用“成员意图”功能——这是 Discord 能够在成员记录中同步角色信息所必需的。
- **需使用角色 ID，而非名称**：请在 Discord 中获取角色 ID：进入**用户设置 → 高级设置 → 打开开发者模式**，然后右键点击任意角色选择**复制角色 ID**。
- **私信场景的备用机制**：在私信中，角色检查会同步查看双方所在的服务器；只要用户在任意共享服务器中拥有被允许的角色权限，其在私信中也具备使用权限。

当监管团队成员更替时，此模式尤为适用——新成员在获得相应角色权限后即可立即使用机器人，无需修改 `.env` 配置文件或重启网关。

### 提及控制

默认情况下，即使回复内容中出现了 `@everyone`、`@here` 或角色提及符，Hermes 也会阻止机器人发送此类提及。这是为避免因表述不当的指令或用户重复的内容导致整个服务器被刷屏。不过，针对单个用户的 `@user` 提及以及回复引用功能（即“回复于…”图标）仍会保持启用状态，以确保正常对话不受影响。

您可以通过环境变量或 `config.yaml` 文件来放宽这些默认限制：

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

如需了解有关增强Hermes Agent部署安全性的更多信息，请参阅[安全指南](../security.md)。


