---
sidebar_position: 15
title: "Weixin (WeChat)"
description: "Connect Hermes Agent to personal WeChat accounts via the iLink Bot API"
---

# 微信

将 Hermes 与腾讯旗下的个人即时通讯平台 [微信](https://weixin.qq.com/) 相连。该适配器针对个人微信账号使用腾讯的 **iLink Bot API**——这与企业版微信（WeCom）不同。消息通过长轮询方式传输，因此无需公共端点或 webhook。

:::info
此适配器仅适用于**个人微信账号**。如果您需要企业/公司微信功能，请参考 [WeCom 适配器](./wecom.md)。
:::

:::warning iLink bot 身份——普通微信群可能无法使用
通过二维码登录会将 Hermes 连接到 **iLink bot 身份**（例如 `a5ace6fd482e@im.bot`），而非完全可脚本控制的普通个人微信账号。其后果包括：

- iLink bot 身份通常**无法像普通联系人那样被添加到普通微信群中**。
- 对于大多数机器人类型的账号，iLink 通常**不会将普通微信群的消息事件**（包括提及用于二维码登录的个人账号的 `@` 提及）传递给网关。
- 提及用于扫描二维码的个人微信账号与提及 iLink bot 是不同的——二者属于独立的身份。
- 下面的 `WEIXIN_GROUP_POLICY` / `WEIXIN_GROUP_ALLOWED_USERS` 设置仅当 iLink 真正为你的账号类型返回群组消息时才会生效。若无法返回，无论设置为何值，群组消息都无法送达 Hermes。

实际上，大多数部署情况下只有发送私信到 iLink bot 才能稳定工作。如果配置后群组消息仍无法传输，问题出在 iLink 方面，而非 Hermes。每当 `WEIXIN_GROUP_POLICY` 的值不是 `disabled` 时，网关在启动时都会记录一条 `WARNING` 日志。
:::

## 前提条件

- 一个个人微信账号
- Python 包：`aiohttp` 和 `cryptography`
- 若使用包含 `messaging` 插件的 Hermes 安装版本，则已内置终端二维码生成功能

请安装所需的依赖项：

```bash
pip install aiohttp cryptography
# Optional: for terminal QR code display
pip install hermes-agent[messaging]
```

## 设置

### 1. 运行设置向导

连接微信账号的最简便方式是通过交互式设置流程来完成：

```bash
hermes gateway setup
```

在系统提示时选择**微信**。向导将执行以下操作：

1. 从 iLink Bot API 获取二维码
2. 在您的终端中显示该二维码（或提供对应网址）
3. 等待您使用微信手机应用扫描该二维码
4. 提示您在手机上确认登录
5. 自动将账户凭证保存至 `~/.hermes/weixin/accounts/` 目录中

确认成功后，您将看到类似如下信息的提示：

```
微信连接成功，account_id=your-account-id
```

向导会自动保存 `account_id`、`token` 和 `base_url`，因此您无需手动进行配置。

### 2. 配置环境变量

完成首次二维码登录后，至少需要在 `~/.hermes/.env` 文件中设置账户 ID：

```bash
WEIXIN_ACCOUNT_ID=your-account-id

# Optional: override the token (normally auto-saved from QR login)
# WEIXIN_TOKEN=your-bot-token

# Optional: restrict access
WEIXIN_DM_POLICY=open
WEIXIN_ALLOWED_USERS=user_id_1,user_id_2

# Optional: restore legacy multiline splitting behavior
# WEIXIN_SPLIT_MULTILINE_MESSAGES=true

# Optional: home channel for cron/notifications
WEIXIN_HOME_CHANNEL=chat_id
WEIXIN_HOME_CHANNEL_NAME=Home
```

### 3. 启动网关

```bash
hermes gateway
```

该适配器将恢复已保存的凭据，连接到 iLink API，并开始对消息进行长轮询。

## 功能特性

- **长轮询传输方式** — 无需公共端点、Webhook 或 WebSocket
- **二维码登录** — 通过 `hermes gateway setup` 实现扫描连接功能
- **私信功能** — 支持自定义访问策略；群组消息功能取决于 iLink 是否能为对应身份传递群组事件（对于 iLink 机器人账号通常不支持此功能，详见上文警告）
- **多媒体支持** — 支持图片、视频、文件及语音消息
- **AES-128-ECB 加密 CDN** — 对所有媒体传输内容自动进行加密/解密处理
- **上下文令牌持久化** — 在重启后仍能保持回复的连续性
- **Markdown 格式保留** — 完整保留 Markdown 格式，包括标题、表格和代码块，因此支持 Markdown 的微信客户端可直接渲染这些内容
- **智能消息分片** — 当消息长度未超过限制时，会保持为单个消息气泡；仅当内容过长时才在逻辑边界处进行拆分
- **输入状态指示** — 在智能体处理消息期间，微信客户端会显示“正在输入…”状态
- **SSRF 防护** — 在下载前会对外发媒体 URL 进行验证
- **消息去重机制** — 通过5分钟的滑动时间窗口防止消息被重复处理
- **带退避机制的自动重试** — 能够从临时的 API 错误中恢复

## 配置选项

请在 `config.yaml` 文件的 `platforms.weixin.extra` 下设置以下参数：

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `account_id` | — | iLink 机器人账号 ID（必填） |
| `token` | — | iLink 机器人令牌（必填，通过二维码登录自动保存） |
| `base_url` | `https://ilinkai.weixin.qq.com` | iLink API 的基础地址 |
| `cdn_base_url` | `https://novac2c.cdn.weixin.qq.com/c2c` | 用于媒体传输的 CDN 基础地址 |
| `dm_policy` | `open` | 私信访问策略：`open`、`allowlist`、`disabled`、`pairing` |
| `group_policy` | `disabled` | 群组访问策略：`open`、`allowlist`、`disabled` |
| `allow_from` | `[]` | 当 `dm_policy=allowlist` 时，允许发送私信的用户 ID 列表 |
| `group_allow_from` | `[]` | 当 `group_policy=allowlist` 时，允许加入的群组 ID 列表 |
| `split_multiline_messages` | `false` | 若设置为 `true`，则多行回复会被拆分为多条独立消息（旧版行为）。若设置为 `false`，除非长度超过限制，否则多行回复将保持为单条消息 |
| `text_batch_delay_seconds` | `3.0` | 在将短时间内连续发送的文本消息合并为一条请求之前，需要等待的静默时间（秒数）。由于 iLink 会逐条发送消息，此延迟机制可避免每次发送片段都触发一次智能体调用。将值设为 `0` 可立即发送每条消息 |
| `text_batch_split_delay_seconds` | `5.0` | 当最新的消息片段接近拆分阈值时（即 iLink 可能已对其进行的过长消息分片处理）所使用的额外延迟时间 |

## 访问策略

### 私信策略

用于控制谁可以向该机器人发送私信：

| 值 | 行为 |
|-------|------|
| `open` | 任何人都可以向机器人发送私信（默认值） |
| `allowlist` | 仅 `allow_from` 列表中的用户 ID 可以发送私信 |
| `disabled` | 忽略所有私信请求 |
| `pairing` | 配对模式（用于初始设置阶段） |

```bash
WEIXIN_DM_POLICY=allowlist
WEIXIN_ALLOWED_USERS=user_id_1,user_id_2
```

`WEIXIN_ALLOWED_USERS`是一个**入站过滤规则**，而非邀请系统。通过二维码登录可将一个iLink机器人身份与Hermes关联起来。其他用户无法使用自己的微信账号扫描Hermes的二维码，他们必须通过微信向已关联的iLink机器人或联系人发送消息；只有当发送者的微信用户ID存在于`WEIXIN_ALLOWED_USERS`列表中时，Hermes才会处理该私信。

具体的设置流程如下：

1. 通过`hermes gateway setup`将Hermes与目标账户配对，并记下对应的iLink机器人账号。
2. 让每位被允许使用的用户向该机器人或联系人发送私信。
3. 从网关日志或入站事件数据中获取发送者/用户的微信ID。
4. 将这些ID添加到`WEIXIN_ALLOWED_USERS`列表中，随后重启网关。

如果只有扫描二维码的账号才能与Hermes通信，请确保其他用户是在向iLink机器人身份本身发送消息，而非向用于二维码登录的个人微信账号发送。iLink机器人属于独立的身份实体，而普通的微信联系人/群组路由功能可能会受到腾讯iLink机制的限制。

### 群组策略

该策略用于控制**当iLink为已关联的身份传递群组事件时**，机器人应响应哪些群组。对于通过二维码登录的iLink机器人身份（例如`...@im.bot`），通常根本不会传递群组事件，因此此策略可能不起作用——请参阅页面顶部的iLink机器人限制说明。

| 值 | 行为 |
|-----|------|
| `open` | 若有群组事件送达，机器人会响应所有群组 |
| `allowlist` | 若有群组事件送达，机器人仅响应`group_allow_from`中列出的群组ID |
| `disabled` | 忽略所有群组消息（默认值） |

```bash
WEIXIN_GROUP_POLICY=allowlist
# NOTE: this is a comma-separated list of group chat IDs, NOT member user IDs,
# despite the variable name containing "USERS". Keep this in mind when configuring.
WEIXIN_GROUP_ALLOWED_USERS=group_id_1,group_id_2
```

:::note
对于微信，默认的群组策略为`disabled`（与默认为`open`的企微不同）。这是有意为之——个人微信账号可能隶属于多个群组，而 iLink 机器人身份通常根本无法接收普通微信群消息。如果将 `WEIXIN_GROUP_POLICY` 设置为除 `disabled` 以外的值，网关在启动时会记录一条 `WARNING` 警告信息。
:::

## 媒体支持

### 接收端

该适配器会从用户处接收媒体附件，将其从微信 CDN 下载并解密，随后在本地缓存以供机器人处理：

| 类型 | 处理方式 |
|------|----------|
| **图片** | 下载后使用 AES 解密，并以 JPEG 格式缓存。 |
| **视频** | 下载后使用 AES 解密，并以 MP4 格式缓存。 |
| **文件** | 下载后使用 AES 解密并缓存，同时保留原始文件名。 |
| **语音** | 若存在文本转录结果，则提取为文本；否则直接下载并缓存音频文件（SILK 格式）。 |

**引用消息中的媒体**：引用（回复）消息中的媒体也会被提取出来，这样机器人就能了解用户正在回复的内容。

### 使用 AES-128-ECB 加密的 CDN

微信媒体文件是通过加密的 CDN 进行传输的。适配器会透明地处理这一过程：

- **接收端**：通过包含 `encrypted_query_param` 参数的 URL 从 CDN 下载加密后的媒体，然后使用消息载荷中提供的每文件专用密钥通过 AES-128-ECB 算法进行解密。
- **发送端**：首先在本地使用随机生成的 AES-128-ECB 密钥对文件进行加密，再将加密后的文件上传至 CDN，同时会在发送的消息中包含该加密文件的引用信息。
- AES 密钥长度为 16 字节（128 位）。密钥可能以原始的 base64 格式或十六进制格式提供——适配器可处理这两种格式。
- 此功能需要使用 `cryptography` 这个 Python 包。

无需任何额外配置，加密与解密操作会自动完成。

### 发送端

| 方法 | 发送内容 |
|------|----------|
| `send` | 支持 Markdown 格式的文本消息 |
| `send_image` / `send_image_file` | 通过 CDN 上传的原始图片消息 |
| `send_document` | 通过 CDN 上传的文件附件 |
| `send_video` | 通过 CDN 上传的视频消息 |

所有要发送的媒体内容都会经过加密的 CDN 上传流程：

1. 生成一个随机的 AES-128 密钥。
2. 使用 AES-128-ECB + PKCS#7 填充算法对文件进行加密。
3. 通过 iLink API 的 `getuploadurl` 接口获取上传地址。
4. 将加密后的数据上传至 CDN。
5. 发送包含该加密媒体引用信息的消息。

## 上下文令牌持久化

iLink 机器人 API 要求在向特定对方发送每条消息时，都将对应的 `context_token` 一并返回。适配器会使用基于磁盘的机制来存储这些上下文令牌：

- 每个账号与对方的对应令牌会被保存到 `~/.hermes/weixin/accounts/<account_id>.context-tokens.json` 文件中。
- 程序启动时会恢复之前保存的令牌。
- 每条接收到的消息都会更新该发送者的存储令牌。
- 发送的消息会自动包含最新的上下文令牌。

这样一来，即使网关重启，也能保证回复的连续性。

## Markdown 格式支持

通过 iLink 机器人 API 连接的微信客户端可以直接渲染 Markdown 内容，因此适配器会保留原有的 Markdown 格式而不会对其进行重写：

- **标题**会保持为 Markdown 标题格式（`#`、`##` 等）。
- **表格**会保持为 Markdown 表格格式。
- **代码块**会保持为带边框的代码块形式。
- 代码块外的多余空行会被合并为两个换行符。

## 消息分块传输

只要消息长度在平台允许范围内，就会作为一条完整的聊天消息发送。只有超过长度限制的消息才会被拆分后发送：

- 消息最大长度：**4000 个字符**。
- 即使包含多个段落或换行符，长度在限制以内的消息也会保持完整。
- 超过长度限制的消息会在逻辑分隔点（如段落、空行、代码块）处被拆分。
- 只要可能，代码块会保持完整（除非代码块本身的内容超过了长度限制，否则不会被拆分）。
- 对于过长的单个代码块，则会采用基础适配器的截断逻辑。
- 在发送多个分块消息时，系统会设置 0.3 秒的分块间隔，以避免触发微信的速率限制。

## 输入中状态指示器

适配器会在微信客户端显示输入中状态：

1. 当有新消息到达时，适配器会通过 `getconfig` API 获取一个 `typing_ticket`。
2. 每个用户的输入中状态票证会被缓存 10 分钟。
3. `send_typing` 用于发送开始输入的信号；`stop_typing` 用于发送停止输入的信号。
4. 在机器人处理消息期间，网关会自动触发输入中状态指示。

## 长轮询连接

适配器使用 HTTP 长轮询方式（而非 WebSocket）来接收消息：

### 工作原理

1. **连接**：验证凭据后开始轮询循环。
2. **轮询**：以 35 秒为超时时间调用 `getupdates` 接口；服务器会一直保留该请求，直到有新消息到达或超时时间结束。
3. **分发**：接收到的消息会通过 `asyncio.create_task` 同步分发处理。
4. **同步缓冲区**：一个持续的同步游标（`get_updates_buf`）会被保存到磁盘上，这样适配器在重启后可以从正确的位置继续处理消息。

### 重试策略

遇到 API 错误时，适配器会采用简单的重试机制：

| 错误情况 | 处理方式 |
|----------|----------|
| 短暂性错误（第1–2次） | 2 秒后重新尝试。 |
| 连续出现错误（第3次及以上） | 暂停 30 秒，然后重置重试计数器。 |
| 会话过期（`errcode=-14`） | 暂停 10 分钟（可能需要重新登录）。 |
| 超时 | 立即再次轮询（属于正常的长轮询行为）。 |

### 冗余消除

适配器会通过消息 ID，并在 5 分钟的时间窗口内对接收到的消息进行去重处理。这样可以避免在网络故障或轮询响应重叠的情况下出现重复处理的情况。

### 令牌锁定

同一时间只有一个微信网关实例可以使用某个特定的令牌。适配器会在启动时获取该令牌的锁定权限，并在关闭时释放它。如果已有其他网关正在使用同一个令牌，启动将会失败，并显示相应的错误信息。

## 所有环境变量

| 变量名 | 是否必填 | 默认值 | 描述 |
|--------|----------|---------|------|
| `WEIXIN_ACCOUNT_ID` | ✅ | — | iLink 机器人账号 ID（通过二维码登录获取）。 |
| `WEIXIN_TOKEN` | ✅ | — | iLink 机器人令牌（通过二维码登录后会自动保存）。 |
| `WEIXIN_BASE_URL` | — | `https://ilinkai.weixin.qq.com` | iLink API 的基础地址。 |
| `WEIXIN_CDN_BASE_URL` | — | `https://novac2c.cdn.weixin.qq.com/c2c` | 用于传输媒体的 CDN 基础地址。 |
| `WEIXIN_DM_POLICY` | — | `open` | 私信访问策略：`open`、`allowlist`、`disabled`、`pairing`。 |
| `WEIXIN_GROUP_POLICY` | — | `disabled` | 群组访问策略：`open`、`allowlist`、`disabled`。 |
| `WEIXIN_ALLOWED_USERS` | — | _(空)_ | 用于私信白名单的、以逗号分隔的用户 ID 列表。 |
| `WEIXIN_GROUP_ALLOWED_USERS` | — | _(空)_ | 用于群组白名单的、以逗号分隔的**群聊 ID**列表（而非群成员的用户 ID）。该变量名属于旧版本用法，实际应使用群聊 ID 而非用户 ID。 |
| `WEIXIN_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天频道 ID。 |
| `WEIXIN_HOME_CHANNEL_NAME` | — | `Home` | 主频道显示名称。 |
| `WEIXIN_ALLOW_ALL_USERS` | — | — | 网关级标志，用于允许所有用户访问（由设置向导使用）。 |

## 故障排除

| 问题现象 | 解决方案 |
|----------|----------|
| `Weixin startup failed: aiohttp and cryptography are required` | 需要安装这两个包：`pip install aiohttp cryptography`。 |
| `Weixin startup failed: WEIXIN_TOKEN is required` | 运行 `hermes gateway setup` 完成二维码登录，或手动设置 `WEIXIN_TOKEN`。 |
| `Weixin startup failed: WEIXIN_ACCOUNT_ID is required` | 在 `.env` 文件中设置 `WEIXIN_ACCOUNT_ID`，或运行 `hermes gateway setup`。 |
| `Another local Hermes gateway is already using this Weixin token` | 先停止另一个网关实例——每个令牌只能对应一个轮询程序。 |
| 会话过期（`errcode=-14`） | 您的登录会话已过期。请重新运行 `hermes gateway setup` 并扫描新的二维码。 |
| 设置过程中二维码失效 | 二维码最多会自动刷新 3 次。如果仍然失效，请检查您的网络连接。 |
| 机器人不回复私信 | 检查 `WEIXIN_DM_POLICY` 的设置——如果设置为 `allowlist`，则发送方必须存在于 `WEIXIN_ALLOWED_USERS` 列表中。 |
| 机器人忽略群消息 | 群组策略默认为 `disabled`。可将 `WEIXIN_GROUP_POLICY` 设置为 `open` 或 `allowlist`——但请注意，通过二维码登录的 iLink 机器人身份（格式为 `...@im.bot`）通常根本无法接收普通微信群消息。如果网关日志中未显示任何群消息的原始接收事件，说明问题出在 iLink 端，而非 Hermes 端。 |
| 媒体下载/上传失败 | 确保已安装 `cryptography` 包。同时检查能否访问 `novac2c.cdn.weixin.qq.com`。 |
| `Blocked unsafe URL (SSRF protection)` | 发送的媒体 URL 指向了私有或内部地址。仅允许公共 URL。 |
| 语音消息显示为文本 | 如果微信提供了转录结果，适配器会使用该文本内容。这是正常现象。 |
| 消息出现重复 | 适配器是通过消息 ID 进行去重处理的。如果仍看到重复消息，请检查是否有多个网关实例正在运行。 |
| `iLink POST ... HTTP 4xx/5xx` | iLink 服务返回了 API 错误。请检查令牌的有效性以及网络连接状况。 |
| 终端中的二维码无法显示 | 使用包含消息处理功能的版本重新安装：`pip install hermes-agent[messaging]`。或者直接打开二维码上方显示的网址。 |
