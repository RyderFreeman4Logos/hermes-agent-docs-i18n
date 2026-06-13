---
sidebar_position: 8
title: "Mattermost"
description: "Set up Hermes Agent as a Mattermost bot"
---

# Mattermost 集成设置

Hermes Agent 以机器人形式集成到 Mattermost 中，让你能够通过私信或团队频道与 AI 助手进行对话。Mattermost 是一款自托管的开源 Slack 替代产品——你可以在自己的基础设施上运行它，从而完全掌控数据安全。该机器人通过 Mattermost 的 REST API（v4）和 WebSocket 实现实时事件连接，借助 Hermes Agent 的处理流程（包括工具调用、内存管理和推理功能）来处理消息，并实时给出回复。它支持文本、文件附件、图片以及斜杠命令。

无需额外的 Mattermost 库——适配器使用的是已作为 Hermes 依赖项存在的 `aiohttp` 库。

在开始设置之前，这里先解答大家最关心的问题：Hermes 在接入你的 Mattermost 实例后会有怎样的表现。

## Hermes 的运行方式

| 场景 | 行为表现 |
|------|----------|
| **私信** | Hermes 会回复每条消息，无需使用 `@mention` 指定。每条私信都拥有独立的会话。 |
| **公开/私有频道** | 只有当你使用 `@mention` 提及 Hermes 时，它才会回复；否则会忽略该消息。 |
| **主题讨论串** | 若设置 `MATTERMOST_REPLY_MODE=thread`，Hermes 会在你的原消息下以主题串形式回复。此类主题串的上下文与父频道相互独立。 |
| **多用户共享频道** | 默认情况下，Hermes 会为频道内的每位用户单独维护会话历史。除非你明确禁用该功能，否则在同一频道内交流的两个人不会共享同一条对话记录。 |

:::提示
如果你希望 Hermes 以主题串形式（嵌套在原始消息下方）回复，请设置 `MATTERMOST_REPLY_MODE=thread`。默认值为 `off`，此时消息会以扁平形式发送到频道中。
:::

### Mattermost 中的会话模型

默认情况下：

- 每条私信都拥有独立的会话
- 每个主题讨论串都有独立的会话命名空间
- 共享频道中的每位用户在该频道内也拥有独立的会话

这些设置可通过 `config.yaml` 文件进行配置：

```yaml
group_sessions_per_user: true
```

仅当您明确希望为整个频道设置一个共享对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话对于协作频道而言非常有用，但同时也存在以下问题：

- 用户需要共享上下文数据及令牌成本
- 某人执行的耗时且依赖大量工具的任务可能会增加其他所有人的上下文负载
- 某人正在运行的任务可能会干扰同一频道中其他人的后续操作

本指南将引导您完成整个设置流程——从在 Mattermost 中创建机器人到发送第一条消息。

## 第 1 步：启用机器人账户

在创建机器人之前，必须先在您的 Mattermost 服务器上启用机器人账户功能。

1. 以**系统管理员**身份登录 Mattermost。
2. 转至 **系统控制台** → **集成** → **机器人账户**。
3. 将 **启用机器人账户创建** 设置为 **true**。
4. 点击 **保存**。

:::info
如果您没有系统管理员权限，请让您的 Mattermost 管理员为您启用机器人账户并创建一个。
:::

## 第 2 步：创建机器人账户

1. 在 Mattermost 中，点击左上角的 **☰** 菜单 → **集成** → **机器人账户**。
2. 点击 **添加机器人账户**。
3. 填写相关信息：
   - **用户名**：例如 `hermes`
   - **显示名称**：例如 `Hermes Agent`
   - **描述**：可选
   - **角色**：选择 `成员` 即可
4. 点击 **创建机器人账户**。
5. Mattermost 会显示**机器人令牌**。请立即将其复制下来。

:::warning[Token仅显示一次]
机器人令牌在创建机器人账户时仅显示一次。一旦丢失，您需要从机器人账户设置中重新生成。切勿公开分享您的令牌，也不要将其提交到 Git——拥有该令牌的人即可完全控制该机器人。
:::

请将令牌保存在安全的地方（例如密码管理器），因为第 5 步会用到它。

:::tip
您也可以选择使用**个人访问令牌**而非机器人账户。请前往 **个人资料** → **安全** → **个人访问令牌** → **创建令牌**。如果您希望 Hermes 以您的个人账号而非独立的机器人账号进行回复，此方法非常有用。
:::

## 第 3 步：将机器人添加到频道

若要让机器人能够在特定频道中响应消息，需先将其添加为该频道的成员：

1. 打开希望让机器人加入的频道。
2. 点击频道名称 → **添加成员**。
3. 搜索您的机器人用户名（例如 `hermes`），然后将其添加进去。

对于私信，只需直接与机器人发送消息即可——它将能够立即回复。

## 第 4 步：查找您的 Mattermost 用户 ID

Hermes Agent 会使用您的 Mattermost 用户 ID 来控制谁可以与该机器人交互。要获取该 ID，请按以下步骤操作：

1. 点击左上角的**头像** → **个人资料**。
2. 您的用户 ID 会显示在个人资料对话框中——点击即可复制。

您的用户 ID 是一个由 26 个字符组成的字母数字字符串，例如 `3uo8dkh1p7g1mfk49ear5fzs5c`。

:::warning
您的用户 ID **并非**用户名。用户名是 `@` 后面的部分（例如 `@alice`）。用户 ID 是 Mattermost 内部使用的长格式字母数字标识符。
:::

**另一种方法**：您也可以通过 API 获取用户 ID：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-mattermost-server/api/v4/users/me | jq .id
```

:::提示
要获取**频道编号**：点击频道名称 → **查看信息**。频道编号会显示在信息面板中。如果您想手动设置主频道，就需要这个编号。
:::

## 第5步：配置Hermes Agent

### 方案A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

在系统提示时选择**Mattermost**，随后根据要求粘贴服务器地址、机器人令牌以及用户ID。

### 方案 B：手动配置

在您的 `~/.hermes/.env` 文件中添加以下内容：

```bash
# Required
MATTERMOST_URL=https://mm.example.com
MATTERMOST_TOKEN=***
MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c

# Multiple allowed users (comma-separated)
# MATTERMOST_ALLOWED_USERS=3uo8dkh1p7g1mfk49ear5fzs5c,8fk2jd9s0a7bncm1xqw4tp6r3e

# Optional: reply mode (thread or off, default: off)
# MATTERMOST_REPLY_MODE=thread

# Optional: respond without @mention (default: true = require mention)
# MATTERMOST_REQUIRE_MENTION=false

# Optional: channels where bot responds without @mention (comma-separated channel IDs)
# MATTERMOST_FREE_RESPONSE_CHANNELS=channel_id_1,channel_id_2
```

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 可确保在共享频道和对话线程中，每位参与者的上下文彼此隔离。

### 启动网关

配置完成后，即可启动 Mattermost 网关：

```bash
hermes gateway
```

该机器人应在几秒内连接到您的 Mattermost 服务器。您可以发送一条消息给它——无论是私信还是在其被添加到的频道中——以此进行测试。

:::提示
为确保持续运行，您可以将 `hermes gateway` 在后台运行或作为 systemd 服务来启动。详情请参阅部署文档。
:::

## 主频道

您可以指定一个“主频道”，机器人会向该频道发送主动消息（如定时任务输出、提醒及通知）。设置方式有两种：

### 使用斜杠命令

在机器人所在的任意 Mattermost 频道中输入 `/sethome`，该频道即成为主频道。

### 手动配置

将以下内容添加到您的 `~/.hermes/.env` 文件中：

```bash
MATTERMOST_HOME_CHANNEL=abc123def456ghi789jkl012mn
```

请将该 ID 替换为实际的频道 ID（点击频道名称 → 查看信息 → 复制 ID 即可）。

## 回复模式

`MATTERMOST_REPLY_MODE` 设置用于控制 Hermes 发送回复的方式：

| 模式 | 行为说明 |
|------|----------|
| `off`（默认值） | Hermes 会像普通用户一样在频道中直接发送文本消息。 |
| `thread` | Hermes 会在原始消息下以主题帖的形式进行回复，从而在频繁的来回交流中保持频道整洁。 |

可在您的 `~/.hermes/.env` 文件中设置该参数：

```bash
MATTERMOST_REPLY_MODE=thread
```

## 提及行为

默认情况下，该机器人仅在被 `@mentioned` 时才会在频道中回复。您可以根据需求进行修改：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MATTERMOST_REQUIRE_MENTION` | `true` | 若设置为 `false`，则机器人会回应频道中的所有消息（私信始终有效）。 |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | _(无)_ | 以逗号分隔的频道 ID 列表，即使 `require_mention` 为 `true`，机器人也会在这些频道中无需 `@mention` 即直接回复。 |

在 Mattermost 中查找频道 ID 的方法：进入该频道，点击频道名称栏，然后在 URL 或频道详情中查看 ID。

当机器人被 `@mentioned` 时，系统会在处理消息之前自动移除其中的提及内容。

## 频道白名单（`allowed_channels`）

可将机器人的响应范围限制在指定的 Mattermost 频道中。一旦设置此选项，机器人**仅**会在列表中所列的频道中回复——来自其他任何频道的消息都将被忽略，即便其中包含了对该机器人的 `@mentioned` 提及。

**私信不受此限制**，因此授权用户始终可以通过私信与机器人进行交流。

```yaml
mattermost:
  allowed_channels:
    - "abc123def456ghi789jkl012mno"   # #ops
    - "xyz987uvw654rst321opq098nml"   # #incident-response
```

或通过环境变量（以逗号分隔）：

```bash
MATTERMOST_ALLOWED_CHANNELS="abc123def456ghi789jkl012mno,xyz987uvw654rst321opq098nml"
```

行为规则：

- 空值/未设置 → 无限制（完全兼容旧版本）。
- 非空值 → 频道 ID 必须存在于列表中，否则在执行其他任何限制条件（如提及要求、`MATTERMOST_FREE_RESPONSE_CHANNELS` 等）之前，消息将被丢弃。
- 可通过 Mattermost 用户界面 → 频道标题 → “查看信息”来查找频道 ID，或从频道 URL 中读取该 ID。

另请参阅：[管理员/用户命令分隔](../../reference/slash-commands.md#permissions-and-adminuser-split)。

## 故障排除

### 机器人无响应消息

**原因**：机器人未被添加到该频道，或者 `MATTERMOST_ALLOWED_USERS` 列表中不包含您的用户 ID。

**解决方法**：将机器人添加到频道中（进入频道名称 → 添加成员 → 搜索该机器人）。确认您的用户 ID 已列入 `MATTERMOST_ALLOWED_USERS`。然后重启网关。

### 403 禁止访问错误

**原因**：机器人令牌无效，或机器人没有在该频道发帖的权限。

**解决方法**：检查 `.env` 文件中的 `MATTERMOST_TOKEN` 是否正确。确保机器人账户未被停用。确认机器人已被添加到频道中。如果使用的是个人访问令牌，请确保您的账户拥有相应权限。

### WebSocket 连接断开/重连循环

**原因**：网络不稳定、Mattermost 服务器重启，或 WebSocket 连接存在防火墙/代理问题。

**解决方法**：适配器会以指数退避方式自动重连（2秒 → 60秒）。检查服务器的 WebSocket 配置——反向代理（如 nginx、Apache）需要配置 WebSocket 升级头。确认 Mattermost 服务器上的防火墙没有阻止 WebSocket 连接。

对于 nginx，需确保配置文件中包含以下内容：

```nginx
location /api/v4/websocket {
    proxy_pass http://mattermost-backend;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 600s;
}
```

### 启动时出现“认证失败”错误

**原因**：令牌或服务器地址不正确。

**解决方法**：确认 `MATTERMOST_URL` 指向正确的 Mattermost 服务器地址（需包含 `https://`，且末尾不可有斜杠）。同时检查 `MATTERMOST_TOKEN` 是否有效——可使用 curl 命令进行测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/api/v4/users/me
```

如果该操作返回了您机器人的用户信息，说明令牌有效；若返回错误，则需重新生成令牌。

### 机器人处于离线状态

**原因**：Hermes 网关未运行或连接失败。

**解决方法**：检查 `hermes gateway` 是否正在运行，并查看终端输出中的错误信息。常见问题包括：URL 错误、令牌已过期，或无法连接到 Mattermost 服务器。

### 出现“用户未被授权”/机器人忽略您的情况

**原因**：您的用户 ID 不在 `MATTERMOST_ALLOWED_USERS` 列表中。

**解决方法**：将您的用户 ID 添加到 `~/.hermes/.env` 文件中的 `MATTERMOST_ALLOWED_USERS` 列表中，然后重启网关。请注意：用户 ID 是一个由 26 个字符组成的字母数字字符串，而非您的 `@用户名`。

## 每个频道的提示语

您可以为特定的 Mattermost 频道设置临时的系统提示语。这些提示语会在每次对话轮次运行时被注入，不会被保存到对话记录中，因此更改会立即生效。

```yaml
mattermost:
  channel_prompts:
    "channel_id_abc123": |
      You are a research assistant. Focus on academic sources,
      citations, and concise synthesis.
    "channel_id_def456": |
      Code review mode. Be precise about edge cases and
      performance implications.
```

这些密钥即为 Mattermost 频道 ID（可通过频道 URL 或 API 查找）。匹配到的频道中的所有消息都会被注入相应的提示语，作为临时的系统指令发送给用户。

## 安全性

:::warning
请务必设置 `MATTERMOST_ALLOWED_USERS` 参数，以限制能够与该机器人交互的用户范围。为确保安全，若未设置此参数，网关将默认拒绝所有用户的访问。仅添加您信任的用户 ID 即可——获得授权的用户可完全使用该代理的所有功能，包括调用工具及访问系统权限。
:::

如需了解有关强化 Hermes Agent 部署安全性的更多信息，请参阅 [安全指南](../security.md)。

## 备注

- **兼容自托管环境**：可适用于任何自托管的 Mattermost 实例，无需 Mattermost Cloud 账户或订阅服务。
- **无额外依赖**：该适配器使用 Hermes Agent 自带的 `aiohttp` 库来处理 HTTP 和 WebSocket 沟通。
- **兼容团队版和企业版**：同时支持 Mattermost 的团队版（免费）和企业版。
