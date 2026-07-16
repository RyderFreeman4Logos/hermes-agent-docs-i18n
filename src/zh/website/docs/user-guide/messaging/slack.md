---
sidebar_position: 4
title: "Slack"
description: "Set up Hermes Agent as a Slack bot using Socket Mode"
---

# Slack 设置

通过 Socket 模式将 Hermes Agent 作为机器人连接到 Slack。Socket 模式使用 WebSocket 而非公共 HTTP 端点，因此您的 Hermes 实例无需公开访问——它可以在防火墙后、笔记本电脑上或私有服务器上运行。

:::warning 传统 Slack 应用已废弃
基于 RTM API 的传统 Slack 应用已于 **2025 年 3 月完全废弃**。Hermes 使用带有 Socket 模式的现代 Bolt SDK。如果您有旧的传统应用，必须按照以下步骤创建一个新的应用。
:::

## 概览

| 组件 | 值 |
|-----------|-------|
| **库** | Python 版的 `slack-bolt` / `slack_sdk`（Socket 模式） |
| **连接方式** | WebSocket — 无需公共 URL |
| **所需授权令牌** | 机器人令牌（`xoxb-`）+ 应用级令牌（`xapp-`） |
| **用户标识** | Slack 成员 ID（例如 `U01ABC2DEF3`） |

---

## 第 1 步：创建 Slack 应用

最快捷的方法是粘贴 Hermes 为您生成的清单文件。该文件会一次性声明所有内置的 slash 命令（如 `/btw`、`/stop`、`/model` 等）、所有必需的 OAuth 权限范围、所有事件订阅，并启用 Socket 模式。

### 方案 A：使用 Hermes 生成的清单文件（推荐）

1. 生成清单文件。新的 Slack 应用必须使用 Agent 视图来创建：
   ```bash
   hermes slack manifest --agent-view --write
   ```
该操作会生成 `~/.hermes/slack-manifest.json` 文件，并输出可直接粘贴的配置说明。那些仍使用 Slack 旧版助手界面的现有应用，在准备好迁移之前可省略 `--agent-view` 参数。

2. 访问 [https://api.slack.com/apps](https://api.slack.com/apps)，选择**创建新应用** → **从应用清单创建**。
3. 选择对应的工作空间，粘贴 JSON 内容，进行审核后点击**下一步** → **创建**。
4. 直接跳至**步骤 6：将应用安装到工作空间**。该清单已自动处理了权限范围、事件及斜杠命令的相关配置。

### 方案 B：从零开始（手动创建）

1. 访问 [https://api.slack.com/apps](https://api.slack.com/apps)
2. 点击**创建新应用**
3. 选择**从零开始**
4. 输入应用名称（例如“Hermes Agent”），并选定对应的工作空间
5. 点击**创建应用**

随后会进入应用的**基本信息**页面，接着按照下方的步骤 2–6 操作即可。

---

## 步骤 2：配置机器人令牌的权限范围

在侧边栏中导航至**功能 → OAuth 与权限**。向下滚动到**权限范围 → 机器人令牌权限范围**，并添加以下项：

| 权限范围 | 用途 |
|---------|------|
| `chat:write` | 以机器人身份发送消息 |
| `app_mentions:read` | 检测在频道中被@提及的情况 |
| `channels:history` | 读取机器人所在公共频道的消息 |
| `channels:read` | 列出并获取公共频道的信息 |
| `groups:history` | 读取机器人被邀请加入的私密频道的消息 |
| `im:history` | 读取直接消息的历史记录 |
| `im:read` | 查看基本的直接消息信息 |
| `im:write` | 打开并管理直接消息 |
| `mpim:history` | 读取群组直接消息（多人直接消息）的历史记录 |
| `mpim:read` | 查看基本的群组直接消息信息 |
| `users:read` | 查询用户信息 |
| `files:read` | 读取并下载附件，包括语音笔记/音频文件 |
| `files:write` | 上传文件（图片、音频、文档） |

:::caution 缺少权限范围 = 缺少相应功能
如果未添加 `channels:history` 和 `groups:history`，机器人**将无法接收频道中的消息**——它仅能在直接消息中运行。若缺少 `files:read`，Hermes 虽可进行聊天，但**无法可靠地读取用户上传的附件**。这些是最常被忽略的权限范围。
:::

**可选权限范围：**

| 权限范围 | 用途 |
|---------|------|
| `groups:read` | 列出并获取私密频道的信息 |

---

## 步骤 3：启用 Socket 模式

Socket 模式允许机器人通过 WebSocket 连接，而无需公开 URL。

1. 在侧边栏中，进入**设置 → Socket 模式**
2. 将**启用 Socket 模式**切换为开启状态
3. 系统会提示您创建一个**应用级令牌**：
   - 为其命名，例如 `hermes-socket`（名称并无特殊要求）
   - 添加 **`connections:write`** 权限范围
   - 点击**生成**
4. **复制该令牌**——其开头为 `xapp-`。这就是您的 `SLACK_APP_TOKEN`。

:::tip
您随时可以在**设置 → 基本信息 → 应用级令牌**处查找或重新生成应用级令牌。
:::

---

## 步骤 4：订阅事件

此步骤至关重要——它决定了机器人能够接收哪些类型的消息。

1. 在侧边栏中，进入**功能 → 事件订阅**
2. 将**启用事件**切换为开启状态
3. 展开**订阅机器人事件**选项，然后添加以下项：

| 事件类型 | 是否必需 | 用途 |
|---------|----------|------|
| `message.im` | **是** | 机器人可接收直接消息 |
| `message.mpim` | **是** | 机器人可接收其被加入的**群组直接消息**中的内容 |
| `message.channels` | **是** | 机器人可接收其被加入的**公共频道**中的消息 |
| `message.groups` | **建议添加** | 机器人可接收其被邀请加入的**私密频道**中的消息 |
| `app_mention` | **是** | 防止在机器人被@提及时出现 Bolt SDK 错误 |

4. 点击页面底部的**保存更改**

:::danger 缺少事件订阅是最常见的配置问题
如果机器人能在直接消息中正常工作，但**在频道中无法接收消息**，那几乎可以肯定是因为您忘记了添加 `message.channels`（针对公共频道）和/或 `message.groups`（针对私密频道）。如果没有这些事件，Slack 就不会将频道中的消息传递给机器人。
:::


---

## 步骤 5：启用“消息”标签页

此步骤可让用户向机器人发送直接消息。若未启用，用户在尝试给机器人发直接消息时将会看到**“已关闭向该应用发送消息的功能”**的提示。

1. 在侧边栏中，进入**功能 → 应用主页**
2. 滚动到**显示标签页**部分
3. 将**消息标签页**切换为开启状态
4. 勾选**“允许用户通过消息标签页发送斜杠命令和消息”**

:::danger 若未完成此步骤，直接消息将完全无法发送
即便已配置所有正确的权限范围和事件订阅，只要未启用“消息”标签页，Slack 也不会允许用户向机器人发送直接消息。这是 Slack 平台的要求，而非 Hermes 的配置问题。
:::

---

## 步骤 6：将应用安装到工作空间

1. 在侧边栏中，进入**设置 → 安装应用**
2. 点击**安装到工作空间**
3. 查看相关权限设置后点击**允许**
4. 授权完成后，您会看到一个以 `xoxb-` 开头的**机器人用户 OAuth 令牌**
5. **复制该令牌**——这就是您的 `SLACK_BOT_TOKEN`。

:::tip
如果日后需要更改权限范围或事件订阅，必须**重新安装应用**才能使更改生效。安装应用页面会显示相关提示。
:::

---

## 步骤 7：查找白名单所需的用户 ID

Hermes 在构建白名单时使用的是 Slack 的**成员 ID**（而非用户名或显示名称）。

要查找成员 ID：

1. 在 Slack 中点击该用户的姓名或头像
2. 点击**查看完整资料**
3. 点击**⋮**（更多）按钮
4. 选择**复制成员 ID**

成员 ID 的格式类似 `U01ABC2DEF3`。您至少需要拥有自己的成员 ID。

---

## 步骤 8：配置 Hermes

在您的 `~/.hermes/.env` 文件中添加以下内容：

```bash
# Required
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_ALLOWED_USERS=U01ABC2DEF3              # Comma-separated Member IDs

# Optional
SLACK_HOME_CHANNEL=C01234567890              # Default channel for cron/scheduled messages
SLACK_HOME_CHANNEL_NAME=general              # Human-readable name for the home channel (optional)
```

或者运行交互式设置流程：

```bash
hermes gateway setup    # Select Slack when prompted
```

接着启动网关：

```bash
hermes gateway              # Foreground
hermes gateway install      # Install as a user service
sudo hermes gateway install --system   # Linux only: boot-time system service
```

:::提示 Codex推理耗时与安全性设置
对于基于Codex的Slack对等代理频道，建议将`agent.reasoning_effort`设置为`high`或更低值。当设置为`xhigh`时，代理会在整个轮次中都在进行隐式推理，而不会输出任何可见的助手文本；此时Hermes会隐藏线程中的相关“轮次未完成”警告，仅将诊断信息记录在网关日志中。
:::

---

## 第9步：将机器人邀请到频道

启动网关后，您需要**将机器人邀请**到希望其响应的任意频道中：

```
/invite @Hermes Agent
```

该机器人**不会**自动加入频道，您必须逐个将其邀请到各个频道中。

```bash
hermes slack manifest --agent-view --write
```

请在**Features → App Manifest**中更新清单文件，随后在 Slack 提示时重新安装应用。Agent 模式无法切换回 Assistant 模式，用户在进行切换后可能需要强制刷新 Slack。生成的 Agent 清单文件会订阅 `message.im`、`app_home_opened` 和 `app_context_changed` 事件，这样 Hermes 即可识别出“消息”标签页中的私信，并在用户发出指令时获取其当前的 Slack 上下文信息。Hermes 仅将该上下文作为标签提供，而不会读取所查看频道的聊天历史记录。

### 更新后的斜杠命令刷新方法

当 Hermes 添加了新命令（例如执行 `hermes update` 后），需重新生成清单文件并更新您的 Slack 应用：

```bash
hermes slack manifest --write
```

接下来在 Slack 中操作：
1. 打开 [https://api.slack.com/apps](https://api.slack.com/apps) → 选择你的 Hermes 应用；
2. 进入 **Features → App Manifest → Edit**；
3. 粘贴 `~/.hermes/slack-manifest.json` 文件中的新内容；
4. 点击 **Save**。如果权限范围或斜杠命令发生了变化，Slack 会提示你需要重新安装该应用。

### 旧版的 `/hermes <subcommand>` 方式仍然有效

为兼顾旧版配置文件的兼容性，你仍可以输入 `/hermes btw run the tests` — Hermes 会以与 `/btw run the tests` 相同的方式处理该命令。自由格式的提问也同样可行：`/hermes what's the weather?` 会被视为普通消息处理。

### 在主题回复中使用命令（使用 `!cmd` 前缀）

Slack 本身不允许在主题回复中使用原生斜杠命令——尝试在主题回复中输入 `/queue`，Slack 会回复 *“/queue 不支持在主题回复中使用。抱歉！”* 目前没有应用端的设置可以重新启用此功能，因为 Slack 也不会将这些命令传递给 Hermes。

作为变通方案，Hermes 会将开头的 `!` 视为可在主题回复（以及其他任何地方）使用的替代命令前缀。你可以像发送普通主题回复一样输入 `!queue`、`!stop`、`!model gpt-5.4` 等命令——Hermes 会将其视为斜杠命令形式，并在同一主题回复中给出响应。

由于仅会检查第一个单词是否在已知命令列表中，像 `!nice work` 这样的普通消息会原封不动地传递给智能体。

需要用户确认的命令（如危险命令或 `execute_code` 的执行授权）通常会以交互式按钮的形式呈现。当无法显示按钮且 Hermes 转而使用文本提示时，它会指示用户回复 `!approve` 或 `!deny`——这两种形式在主题回复中同样有效。

### 进阶用法：仅输出斜杠命令数组

如果你是手动维护 Slack 配置文件，且仅需获取斜杠命令列表：

```bash
hermes slack manifest --slashes-only > /tmp/slashes.json
```

将该数组粘贴到您现有清单的 `features.slash_commands` 键中。

---

## 机器人的响应方式

了解 Hermes 在不同场景下的行为表现：

| 场景 | 行为 |
|---------|----------|
| **私信** | 机器人会回复每条消息——无需使用 @mention |
| **频道** | 机器人**仅在被 @提及时才会回复**（例如：`@Hermes Agent 现在几点了？`）。在频道中，Hermes 会在该消息对应的讨论串中回复。 |
| **讨论串** | 如果在现有讨论串中 @提及 Hermes，它会在同一讨论串中回复。一旦机器人已在某个讨论串中进入活跃会话，**后续在该讨论串中的回复无需再 @提及**——机器人会自动延续对话。 |

:::提示
在频道中，始终需要通过 @mention 机器人来启动对话。一旦机器人进入某个讨论串并处于活跃状态，您就可以直接在该讨论串中回复而无需再次 @提及。在讨论串之外，未使用 @mention 的消息会被忽略，以避免在繁忙的频道中产生信息杂乱。
:::

---

## 配置选项

除了第 8 步中要求的环境变量外，您还可以通过 `~/.hermes/config.yaml` 自定义 Slack 机器人的行为。

### 讨论串与回复行为

```yaml
platforms:
  slack:
    # Controls how multi-part responses are threaded
    # "off"   — never thread replies to the original message
    # "first" — first chunk threads to user's message (default)
    # "all"   — all chunks thread to user's message
    reply_to_mode: "first"

    extra:
      # Whether to reply in a thread (default: true).
      # When false, channel messages get direct channel replies instead
      # of threads. Messages inside existing threads still reply in-thread.
      reply_in_thread: true

      # Also post thread replies to the main channel
      # (Slack's "Also send to channel" feature).
      # Only the first chunk of the first reply is broadcast.
      reply_broadcast: false

      # Render agent messages as Slack Block Kit blocks (default: false).
      # When true, the final agent message is sent with structured blocks —
      # section headers, dividers, true nested lists (via rich_text), and
      # native Block Kit tables — instead of flat mrkdwn text. A plain-text
      # fallback is always sent alongside for notifications/accessibility.
      # Tables exceeding Slack's limits (100 rows / 20 cols / 10k chars)
      # gracefully fall back to aligned monospace.
      rich_blocks: false

      # Append Slack-native feedback controls to final Block Kit replies.
      # Requires rich_blocks: true. Default: false.
      feedback_buttons: false

      # Suggested prompts pinned at the top of Agent view's Messages tab.
      # Either a list of {title, message} rows, or a titled object:
      # {title: "Start here", prompts: [{title: "Plan", message: "..."}]}
      suggested_prompts: []

      # Title Agent/Assistant DM threads from the first user message.
      # Default: true. Set false to leave Slack's default thread titles.
      assistant_thread_titles: true

      # Continuable-cron delivery surface (default: "thread").
      # "in_channel" delivers a continuable cron job FLAT into the channel
      # (no dedicated thread); pair with reply_in_thread: false (and
      # require_mention: false) so a plain reply continues the job.
      # See the cron guide → "Flat, in-channel continuation".
      cron_continuable_surface: thread
```

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `platforms.slack.reply_to_mode` | `"first"` | 多部分消息的线程模式：`"off"`、`"first"` 或 `"all"` |
| `platforms.slack.extra.reply_in_thread` | `true` | 当设置为 `false` 时，频道消息将直接回复而非以线程形式发送。已存在线程中的消息仍会以线程形式回复。 |
| `platforms.slack.extra.reply_broadcast` | `false` | 当设置为 `true` 时，线程回复也会发布到主频道。仅会广播第一部分内容。 |
| `platforms.slack.extra.rich_blocks` | `false` | 当设置为 `true` 时，智能体消息将以 [Block Kit](https://docs.slack.dev/block-kit/) 块格式呈现（包括标题、分隔符、真正的嵌套列表以及原生表格）。同时始终会发送纯文本作为备用格式。超过 Slack 限制的表格将回退为对齐的等宽字体格式。无需重新安装应用，仅需在发送端进行更改即可。 |
| `platforms.slack.extra.feedback_buttons` | `false` | 当与 `rich_blocks` 一起设置为 `true` 时，会在最终回复中添加 Slack 原生的反馈控件。 |
| `platforms.slack.extra.suggested_prompts` | `[]` | 最多可提供四个 `{title, message}` 格式的提示，用于智能体/助手的私信入口；可接受列表形式或 `{title, prompts}` 格式。 |
| `platforms.slack.extra.assistant_thread_titles` | `true` | 当设置为 `true` 时，会根据第一个用户消息为智能体/助手的私信线程命名。 |
| `platforms.slack.extra.cron_continuable_surface` | `"thread"` | [可延续的定时任务](../features/cron.md#flat-in-channel-continuation-slack) 的发送方式。`"thread"` 选项会为每次任务发送创建一个专用线程（默认值）；`"in_channel"` 选项则直接将任务内容发布到频道时间线中。若要使普通的频道回复能够延续任务，需将 `in_channel` 与 `reply_in_thread: false`（以及 `require_mention: false`）一起使用。 |

### 会话隔离

```yaml
# Global setting — applies to Slack and all other platforms
group_sessions_per_user: true
```

当设置为 `true`（默认值）时，共享频道中的每位用户都会拥有独立的对话会话。在 `#general` 频道中与 Hermes 交流的两位用户将拥有各自的对话历史和上下文。

若希望启用协作模式，让整个频道共用一个对话会话，则可将该值设置为 `false`。请注意，这意味着所有用户将共享上下文数据及令牌消耗，且任何一位用户执行 `/reset` 指令都会清除所有人的对话会话。

### 提及与触发行为

```yaml
slack:
  # Require @mention in channels (this is the default behavior;
  # the Slack adapter enforces @mention gating in channels regardless,
  # but you can set this explicitly for consistency with other platforms)
  require_mention: true

  # Prevent thread auto-engagement: only reply to channel messages that
  # contain an explicit @mention. With this OFF (default), Slack can
  # "auto-engage" — remembering past mentions in a thread and following
  # up on bot-message replies, and resuming active sessions without a
  # fresh mention. With strict_mention ON, every new channel message
  # must @mention the bot before Hermes will respond.
  strict_mention: false

  # Custom mention patterns that trigger the bot
  # (in addition to the default @mention detection)
  mention_patterns:
    - "hey hermes"
    - "hermes,"

  # Text prepended to every outgoing message
  reply_prefix: ""
```

:::提示 何时使用 `strict_mention`  
在那些 Slack 默认的“机器人会记住该对话线程”功能令用户感到意外的高频工作空间中，可将此选项设置为 `true`——例如，在一个漫长的技术支持对话线程中，机器人最初提供了帮助，而您希望除非再次被明确提及，否则它保持沉默。私信及正在进行的交互式会话则不受影响。  
:::

:::信息  
Slack 支持这两种模式：默认情况下，必须使用 `@mention` 才能启动对话，但您也可以通过 `config.yaml` 中的 `SLACK_FREE_RESPONSE_CHANNELS`（以逗号分隔的频道 ID）或 `slack.free_response_channels` 来指定无需回应的特定频道。一旦机器人在某个对话线程中建立了活跃会话，后续的回复就无需再使用提及方式。在**1:1 私信**中，机器人始终无需提及即可响应。  
:::

:::注意 群组私信（MPIM）属于共享空间，并非 1:1 私信  
**1:1 直接消息**是与单个人的私人对话，因此无需提及即可触发响应。而**群组私信（MPIM/多人私信）**则是*共享空间*——多个人都可以看到并触发机器人响应——因此它遵循与频道相同的操作规则：`require_mention`、`strict_mention`、`free_response_channels` 以及 `allowed_channels` 均适用。只有当真正被 `@mention` 时，机器人才会添加 `:eyes:`/`:white_check_mark:` 等表情反应。若希望机器人在特定的群组私信中自由响应，只需将其频道 ID（以 `G` 开头）添加到 `free_response_channels` 中即可。  
:::

### 频道白名单（`allowed_channels`）  
可将机器人限制在指定的 Slack 频道范围内——当机器人被邀请加入众多频道，但仅需在少数几个频道中响应时，此功能非常有用。一旦设置此选项，来自列表之外频道的消息将**被直接忽略**，即便其中提到了该机器人。  
**1:1 私信不受此过滤规则限制**，因此授权用户始终可以通过直接消息与机器人联系。而**群组私信（MPIM）则不在例外之列**——与频道一样，MPIM 必须被列入白名单（其 ID 以 `G` 开头），否则其消息也会被丢弃。

```yaml
slack:
  allowed_channels:
    - "C0123456789"   # #ops
    - "C0987654321"   # #incident-response
```

或通过环境变量（以逗号分隔）：

```bash
SLACK_ALLOWED_CHANNELS="C0123456789,C0987654321"
```

行为规则：

- 空值/未设置 → 无限制（完全向后兼容）。
- 非空值 → 频道 ID 必须存在于指定列表中；否则，在执行其他任何限制条件（如提及要求、`free_response_channels` 等）之前，该消息将被直接丢弃。
- Slack 频道 ID 以 `C`（公共频道）、`G`（私有频道）或 `D`（私信）开头。可通过 Slack 用户界面的“打开频道详情”→“关于”面板或 API 查阅这些信息。

另请参阅：[管理员/用户斜杠命令分离](../../reference/slash-commands.md#permissions-and-adminuser-split)。

### 未授权用户处理方式

```yaml
slack:
  # What happens when an unauthorized user (not in SLACK_ALLOWED_USERS) DMs the bot
  # "pair"   — prompt them for a pairing code (default)
  # "ignore" — silently drop the message
  unauthorized_dm_behavior: "pair"
```

您也可以为所有平台全局设置此参数：

```yaml
unauthorized_dm_behavior: "pair"
```

在 `slack:` 下的特定平台设置会优先于全局设置生效。

### 语音转录

请翻译完整的输入内容，切勿提前终止。

```yaml
# Global setting — enable/disable automatic transcription of incoming voice messages
stt_enabled: true
```

当设置为 `true`（默认值）时，传入的音频消息会在被智能体处理之前，先通过已配置的文本转语音服务进行自动转录。

### 完整示例

```yaml
# Global gateway settings
group_sessions_per_user: true
unauthorized_dm_behavior: "pair"
stt_enabled: true

# Slack-specific settings
slack:
  require_mention: true
  unauthorized_dm_behavior: "pair"

# Platform config
platforms:
  slack:
    reply_to_mode: "first"
    extra:
      reply_in_thread: true
      reply_broadcast: false
```

## 主页频道

请将 `SLACK_HOME_CHANNEL` 设置为 Hermes 用于发送定时消息、cron 任务结果以及其他主动通知的频道 ID。若需查找频道 ID，请按以下步骤操作：

1. 在 Slack 中右键点击该频道名称
2. 点击 **查看频道详情**
3. 滚动到页面底部——频道 ID 即显示在那里

```bash
SLACK_HOME_CHANNEL=C01234567890
```

请确保该机器人已**被邀请加入对应频道**（使用命令 `/invite @Hermes Agent`）。

---

## 多工作区支持

Hermes 可通过单个网关实例同时连接**多个 Slack 工作区**。每个工作区都会使用独立的机器人用户 ID 进行身份验证。

### 配置方式

在 `SLACK_BOT_TOKEN` 中以**逗号分隔的列表形式**提供多个机器人令牌：

```bash
# Multiple bot tokens — one per workspace
SLACK_BOT_TOKEN=xoxb-workspace1-token,xoxb-workspace2-token,xoxb-workspace3-token

# A single app-level token is still used for Socket Mode
SLACK_APP_TOKEN=xapp-your-app-token
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
platforms:
  slack:
    token: "xoxb-workspace1-token,xoxb-workspace2-token"
```

### OAuth令牌文件

除了从环境变量或配置文件中获取令牌外，Hermes还会从以下位置的**OAuth令牌文件**中加载令牌：

```
~/.hermes/slack_tokens.json
```

该文件是一个 JSON 对象，用于将团队 ID 与令牌条目进行映射：

```json
{
  "T01ABC2DEF3": {
    "token": "xoxb-workspace-token-here",
    "team_name": "My Workspace"
  }
}
```

该文件中的令牌会与通过 `SLACK_BOT_TOKEN` 指定的令牌合并，重复的令牌会自动去重。

### 工作原理

- 列表中的**第一个令牌**为主令牌，用于 Socket 模式连接（AsyncApp）。
- 启动时，每个令牌都会通过 `auth.test` 进行身份验证。网关会将每个 `team_id` 对应到独立的 `WebClient` 和 `bot_user_id`。
- 当有消息到达时，Hermes 会使用对应工作空间的客户端来回复。
- 为保持与那些需要单一机器人身份的功能的兼容性，系统会使用主 `bot_user_id`（即第一个令牌中的值）。

---

## 语音消息

Hermes 支持在 Slack 中发送语音消息：

- **接收端**：语音/音频消息会自动使用配置好的文本转语音服务进行转写，可选服务包括本地的 `faster-whisper`、Groq Whisper（需提供 `GROQ_API_KEY`）或 OpenAI Whisper（需提供 `VOICE_TOOLS_OPENAI_KEY`）。
- **发送端**：文本转语音生成的回复会以音频文件附件的形式发送。

---

## 每个频道的提示语

可为特定的 Slack 频道设置临时的系统提示语。这些提示语会在每次对话时动态注入，不会被保存到对话记录中，因此更改会立即生效。

```yaml
slack:
  channel_prompts:
    "C01RESEARCH": |
      You are a research assistant. Focus on academic sources,
      citations, and concise synthesis.
    "C02ENGINEERING": |
      Code review mode. Be precise about edge cases and
      performance implications.
```

这些密钥即为 Slack 频道 ID（可通过频道详情页 → “关于” → 滚动到页面底部查看）。匹配频道中的所有消息都会作为临时的系统指令接收该提示词。

## 按频道绑定的技能

每当在特定频道或私信中开启新会话时，系统会自动加载对应技能。与每轮都会注入的频道专用提示词不同，按频道绑定的技能会在**会话开始时**以用户消息的形式注入——它将成为对话历史的一部分，后续轮次无需再次加载。

对于私信或具有特定用途的频道（如抽认卡工具、行业专属问答机器人、支持服务分流频道等），这种方式尤为理想，因为无需让模型自身的技能选择器在每次简短回复时都决定是否加载相应技能。

```yaml
slack:
  channel_skill_bindings:
    # DM channel — always runs in "german-flashcards" mode
    - id: "D0ATH9TQ0G6"
      skills:
        - german-flashcards
    # Research channel — preload multiple skills in order
    - id: "C01RESEARCH"
      skills:
        - arxiv
        - writing-plans
    # Short form: single skill as a string
    - id: "C02SUPPORT"
      skill: hubspot-on-demand
```

**备注：**  
- 绑定是通过频道 ID 进行匹配的。在已绑定的频道中的多线程消息，其线程会继承父频道的绑定设置。  
- 技能仅在会话启动时（新建会话或自动重置后）加载。若需更改绑定，需执行 `/new` 命令或等待会话自动重置，更改才能生效。  
- 可结合 `channel_prompts` 使用，以便在技能指令基础上为每个频道设置特定的语气或限制条件。

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 机器人不回复私信 | 确认已在事件订阅中包含 `message.im`，并重新安装应用 |
| 机器人在私信中能响应，但在频道中无法响应 | **最常见的问题。**请在事件订阅中添加 `message.channels` 和 `message.groups`，重新安装应用，然后使用 `/invite @Hermes Agent` 将机器人邀请至该频道 |
| 机器人不回复频道中的@提及 | 1) 确认已订阅 `message.channels` 事件。2) 机器人必须已被邀请进入该频道。3) 确保已添加 `channels:history` 权限范围。4) 在更改权限范围或事件后重新安装应用 |
| 机器人忽略私密频道中的消息 | 需同时添加 `message.groups` 事件订阅和 `groups:history` 权限范围，之后重新安装应用并使用 `/invite` 命令邀请机器人 |
| 机器人不回复群组私信（多人私信） | 需添加 `message.mpim` 事件订阅以及 `mpim:history`（还需 `mpim:read`）权限范围，之后**重新安装**应用。若没有 `message.mpim`，即使一对一私信能正常发送，Slack 也不会将群组私信传递给机器人 |
| 在私信中出现“已禁用向此应用发送消息”的提示 | 在应用主页设置中启用**消息标签页**（参见第5步） |
| 出现“not_authed”或“invalid_auth”错误 | 重新生成机器人令牌和应用令牌，并更新 `.env` 文件 |
| 机器人能响应，但无法在频道中发布内容 | 使用 `/invite @Hermes Agent` 将机器人邀请至该频道 |
| 机器人可以聊天，但无法读取上传的图片/文件 | 需添加 `files:read` 权限，之后**重新安装**应用。当 Slack 返回权限/认证失败时，Hermes 现已在聊天界面中显示附件访问相关的诊断信息 |
| 出现 `missing_scope` 错误 | 在 OAuth 和权限设置中添加所需的权限范围，之后**重新安装**应用 |
| Socket连接频繁断开 | 检查网络状况；虽然 Bolt 会自动重连，但不稳定的连接会导致延迟 |
| 更改了权限范围或事件，但没有任何变化 | 每次更改权限范围或事件订阅后，都必须将应用**重新安装**到工作空间中 |

### 快速检查清单

如果机器人在频道中无法正常工作，请确认以下**所有**项：  

1. ✅ 已订阅 `message.channels` 事件（适用于公共频道）  
2. ✅ 已订阅 `message.groups` 事件（适用于私密频道）  
3. ✅ 已订阅 `app_mention` 事件  
4. ✅ 已为公共频道添加 `channels:history` 权限范围  
5. ✅ 已为私密频道添加 `groups:history` 权限范围  
6. ✅ 在添加权限范围或事件后已**重新安装**应用  
7. ✅ 已使用 `/invite @Hermes Agent` 将机器人邀请至该频道  
8. ✅ 在消息中已对机器人进行**@提及**  

---

## 安全性

:::warning
**务必设置 `SLACK_ALLOWED_USERS`**，填入授权用户的成员 ID。出于安全考虑，若未设置此参数，网关将默认**拒绝所有消息**。切勿共享机器人令牌——应将其视同密码对待。
:::

- 令牌应存储在 `~/.hermes/.env` 文件中（文件权限需设置为 `600`）  
- 定期通过 Slack 应用设置轮换令牌  
- 审核谁有权访问您的 Hermes 配置目录  
- Socket 模式意味着不会暴露任何公共端点，从而减少了攻击面
