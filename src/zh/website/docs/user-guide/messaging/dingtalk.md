---
sidebar_position: 10
title: "DingTalk"
description: "Set up Hermes Agent as a DingTalk chatbot"
---

# 钉钉集成设置

Hermes Agent 以聊天机器人的形式与钉钉深度集成，让您能够通过私信或群聊与 AI 助手进行交流。该机器人通过钉钉的流式连接模式建立通信——这是一种持久性的 WebSocket 连接，无需公开网址或 webhook 服务器——并利用钉钉的会话 webhook API 以 Markdown 格式回复消息。

在开始设置之前，这里有大多数人最关心的问题：Hermes 在您的钉钉工作空间中会有怎样的表现？

## Hermes 的运行方式

| 场景 | 行为表现 |
|------|----------|
| **私信（1:1 聊天）** | Hermes 会回复每一条消息，无需使用 `@mention` 指定。每条私信都拥有独立的会话。 |
| **群聊** | 只有当您通过 `@mention` 提及 Hermes 时，它才会回复。未被提及的消息将被忽略。 |
| **多用户的共享群组** | 默认情况下，Hermes 会为群组内的每位用户隔离会话历史。除非您明确禁用此功能，否则同一群组中的不同用户之间不会共享对话记录。 |

### 钉钉中的会话模型

默认设置如下：
- 每条私信都拥有独立的会话
- 共享群组中的每位用户在该群组内也拥有独立的会话

这些设置可通过 `config.yaml` 文件进行配置：

```yaml
group_sessions_per_user: true
```

仅当您明确希望为整个群组设置一个共享对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

本指南将为您详细介绍完整的设置流程——从创建 DingTalk 机器人到发送第一条消息。

## 先决条件

安装所需的 Python 包：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[dingtalk]"
```

或者也可以单独操作：

```bash
pip install dingtalk-stream httpx alibabacloud-dingtalk
```

- `dingtalk-stream` — DingTalk 官方用于流式模式（基于 WebSocket 的实时消息传递）的 SDK  
- `httpx` — 用于通过会话 webhook 发送回复的异步 HTTP 客户端  
- `alibabacloud-dingtalk` — DingTalk OpenAPI SDK，支持 AI 卡片、表情反应及媒体下载功能  

## 第一步：创建 DingTalk 应用

1. 访问 [DingTalk 开发者控制台](https://open-dev.dingtalk.com/)。  
2. 使用您的 DingTalk 管理员账号登录。  
3. 点击 **Application Development** → **Custom Apps** → **Create App via H5 Micro-App**（根据控制台版本，也可选择 **Robot**）。  
4. 填写以下信息：  
   - **App Name**：例如 `Hermes Agent`  
   - **Description**：可选  
5. 创建完成后，进入 **Credentials & Basic Info** 页面，找到您的 **Client ID**（AppKey）和 **Client Secret**（AppSecret），并将两者复制下来。

:::warning[凭证仅显示一次]
Client Secret 在创建应用时仅显示一次。一旦丢失，需要重新生成。切勿公开分享这些凭证，也不应将其提交到 Git 中。
:::

## 第二步：启用机器人功能

1. 在应用的设置页面中，选择 **Add Capability** → **Robot**。  
2. 启用机器人功能。  
3. 在 **Message Reception Mode** 下，选择 **Stream Mode**（推荐方式——无需公开 URL）。

:::tip
流式模式是推荐的配置方式。它通过从您的设备发起的长期有效 WebSocket 连接来实现通信，因此无需公开 IP、域名或 webhook 接口。该方式可在 NAT、防火墙后以及本地机器上正常使用。
:::

## 第三步：获取您的 DingTalk 用户 ID

Hermes Agent 会利用您的 DingTalk 用户 ID 来控制哪些用户可以与该机器人交互。DingTalk 用户 ID 是由您所在组织的管理员设置的字母数字字符串。

获取方法如下：

1. 咨询您的 DingTalk 组织管理员——用户 ID 可在 DingTalk 管理者控制台的 **Contacts** → **Members** 页面中查看。  
2. 或者，机器人会记录每条接收到的消息的 `sender_id`。启动网关后，向机器人发送一条消息，然后查看日志即可找到您的用户 ID。

## 第四步：配置 Hermes Agent

### 方案 A：引导式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在提示时选择**钉钉**。设置向导可通过以下两种路径之一进行授权：

- **二维码设备流程（推荐）**：使用钉钉手机应用扫描终端上显示的二维码——您的客户端 ID 和客户端密钥会自动返回并写入 `~/.hermes/.env` 文件中，无需前往开发者控制台操作。
- **手动粘贴**：如果您已拥有相关凭证（或无法方便地扫描二维码），则可在提示时直接粘贴客户端 ID、客户端密钥以及允许使用的用户 ID。

:::note openClaw 品牌标识说明
由于在 API 层级，钉钉的 `verification_uri_complete` 参数已被固定为 openClaw 的身份标识，因此目前通过二维码授权时，其来源字符串均为 `openClaw`，直到阿里巴巴/钉钉-Real-AI 在服务器端注册专用于 Hermes 的模板为止。这仅仅是钉钉展示同意界面的方式——您创建的机器人完全属于您自己，仅对您的租户可见。
:::

### 方案 B：手动配置

在您的 `~/.hermes/.env` 文件中添加以下内容：

```bash
# Required
DINGTALK_CLIENT_ID=your-app-key
DINGTALK_CLIENT_SECRET=your-app-secret

# Security: restrict who can interact with the bot
DINGTALK_ALLOWED_USERS=user-id-1

# Multiple allowed users (comma-separated)
# DINGTALK_ALLOWED_USERS=user-id-1,user-id-2

# Optional: group-chat gating (mirrors Slack/Telegram/Discord/WhatsApp)
# DINGTALK_REQUIRE_MENTION=true
# DINGTALK_FREE_RESPONSE_CHATS=cidABC==,cidDEF==
# DINGTALK_MENTION_PATTERNS=^小马
# DINGTALK_HOME_CHANNEL=cidXXXX==
# DINGTALK_ALLOW_ALL_USERS=true
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true

gateway:
  platforms:
    dingtalk:
      extra:
        # Require @mention in groups before the bot replies (parity with Slack/Telegram/Discord).
        # DMs ignore this — the bot always replies in 1:1 chats.
        require_mention: true

        # Per-platform allowlist. When set, only these DingTalk user IDs can interact with the bot
        # (same semantics as DINGTALK_ALLOWED_USERS, but scoped here instead of in .env).
        allowed_users:
          - user-id-1
          - user-id-2
```

- `group_sessions_per_user: true` 可确保在共享群聊中，每位参与者的上下文彼此隔离。  
- `require_mention: true` 能防止机器人对所有群消息都作出回应——只有当有人@提及它时，机器人才会回复。  
- `dingtalk.extra` 下的 `allowed_users` 可作为 `DINGTALK_ALLOWED_USERS` 的替代选项；如果同时设置了这两个参数，它们将会被合并使用。  

### 启动网关  

配置完成后，即可启动 DingTalk 网关：

```bash
hermes gateway
```

该机器人应在几秒钟内连接到钉钉的流式消息功能。可以通过发送私信或群聊消息来测试其功能。

:::提示
为确保持续运行，您可以将 `hermes gateway` 在后台运行或作为 systemd 服务来部署。详情请参阅部署指南。
:::

## 功能特性

### AI 卡片

Hermes 可以使用钉钉 AI 卡片而非普通的 Markdown 消息进行回复。卡片能够提供更丰富、结构更清晰的展示效果，同时还能在机器人生成回复的过程中实现实时更新。

如需启用 AI 卡片，请在 `config.yaml` 中配置卡片模板 ID：

```yaml
platforms:
  dingtalk:
    enabled: true
    extra:
      card_template_id: "your-card-template-id"
```

您可以在钉钉开发者控制台的“应用AI卡片”设置中找到对应的卡片模板ID。启用AI卡片后，所有回复都会以卡片形式发送，并支持动态文本更新。

### 表情反应

Hermes会自动在您的消息中添加表情反应，以显示处理状态：

- 🤔思考中——在机器人开始处理您的消息时出现
- 🥳已完成——在回复生成完成后出现（会取代“思考中”反应）

这些表情反应在私信和群聊中均有效。

### 显示设置

您可以独立于其他平台自定义钉钉的显示行为：

```yaml
display:
  platforms:
    dingtalk:
      show_reasoning: false   # Show model reasoning/thinking in replies
      streaming: true         # Enable streaming responses (works with AI Cards)
      tool_progress: all      # Show tool execution progress (all/new/off)
      interim_assistant_messages: true  # Show intermediate commentary messages
```

如需获得更简洁的使用体验，可关闭工具处理进度及中间状态提示：

```yaml
display:
  platforms:
    dingtalk:
      tool_progress: off
      interim_assistant_messages: false
```

## 故障排除

### 机器人无响应消息

**原因**：未启用机器人功能，或 `DINGTALK_ALLOWED_USERS` 列表中不包含您的用户 ID。

**解决方法**：请检查应用设置中已启用机器人功能且选择了流式模式。同时确认您的用户 ID 已添加到 `DINGTALK_ALLOWED_USERS` 中。最后重启网关。

### 出现“dingtalk-stream 未安装”错误

**原因**：未安装 `dingtalk-stream` Python 包。

**解决方法**：请进行安装：

```bash
pip install dingtalk-stream httpx
```

### “需要 DINGTALK_CLIENT_ID 和 DINGTALK_CLIENT_SECRET”

**原因**：您的环境变量或 `.env` 文件中未设置这些凭据。

**解决方法**：请确认 `~/.hermes/.env` 文件中的 `DINGTALK_CLIENT_ID` 和 `DINGTALK_CLIENT_SECRET` 设置正确。其中 Client ID 即为您在 DingTalk 开发者控制台获取的 AppKey，Client Secret 则为 AppSecret。

### 流式连接断开/反复重连

**原因**：网络不稳定、DingTalk 平台维护或凭据问题。

**解决方法**：适配器会通过指数退避策略自动重连（2秒 → 5秒 → 10秒 → 30秒 → 60秒）。请检查您的凭据是否有效，以及应用是否已被停用。同时确认您的网络允许发起 WebSocket 出站连接。

### 机器人处于离线状态

**原因**：Hermes 网关未运行或无法建立连接。

**解决方法**：请检查 `hermes gateway` 是否正在运行，并查看终端输出中的错误信息。常见问题包括凭据错误、应用被停用，或是未安装 `dingtalk-stream` 或 `httpx` 库。

### “没有可用的 session_webhook”

**原因**：机器人尝试回复，但缺少会话 webhook 地址。这通常发生在 webhook 过期，或在接收到消息与发送回复之间机器人被重启的情况下。

**解决方法**：向机器人发送新消息——每条新消息都会生成一个新的会话 webhook 用于回复。这是 DingTalk 的正常限制，机器人只能回复其最近接收到的消息。

## 安全性

:::warning
请务必设置 `DINGTALK_ALLOWED_USERS` 以限制可与机器人交互的用户范围。为确保安全，若未设置该参数，网关将默认拒绝所有用户访问。仅添加您信任的人员的 User ID 即可——获授权的用户可完全使用机器人的各项功能，包括调用工具和访问系统权限。
:::

如需了解如何加强 Hermes Agent 的安全性部署，请参阅 [安全指南](../security.md)。

## 备注

- **流式模式**：无需公开 URL、域名或 webhook 服务器。连接通过 WebSocket 从您的设备发起，因此可在 NAT 和防火墙后正常使用。
- **AI 卡片**：可选择使用丰富的 AI 卡片而非普通 Markdown 格式进行回复，可通过 `card_template_id` 进行配置。
- **表情反应**：会自动显示 🤔Thinking/🥳Done 表情来指示处理状态。
- **Markdown 回复**：回复内容将以 DingTalk 的 Markdown 格式呈现，以实现丰富的文本展示效果。
- **媒体支持**：接收到的消息中的图片和文件会自动解析，可供视觉工具处理。
- **消息去重**：适配器会在5分钟的时间窗口内对消息进行去重，避免重复处理同一条消息。
- **自动重连**：若流式连接断开，适配器会通过指数退避策略自动重新连接。
- **消息长度限制**：每条回复的消息长度上限为20,000个字符，超过此长度的回复将被截断。
