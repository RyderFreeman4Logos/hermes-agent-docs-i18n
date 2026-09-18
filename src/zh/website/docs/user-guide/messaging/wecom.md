---
sidebar_position: 14
title: "WeCom (Enterprise WeChat)"
description: "Connect Hermes Agent to WeCom via the AI Bot WebSocket gateway"
---

# WeCom（企业微信）

将 Hermes 连接到腾讯的企业级即时通讯平台 [WeCom](https://work.weixin.qq.com/)。该适配器利用 WeCom 的 AI 机器人 WebSocket 网关实现实时双向通信，无需使用公共端点或 webhook。

如需配置入站 webhook，请参阅：[WeCom 回调功能](./wecom-callback.md)。

## 前提条件

- 一个 WeCom 组织账号
- 在 WeCom 管理控制台创建的 AI 机器人
- 从机器人凭证页面获取的机器人 ID 和密钥
- Python 包：`aiohttp` 和 `httpx`

## 设置步骤

### 第一步：创建 AI 机器人

#### 推荐方式：扫描创建（仅需一条命令）

```bash
hermes gateway setup
```

选择**WeCom**，然后使用您的 WeCom 手机应用扫描二维码。Hermes 将自动创建一个具有相应权限的机器人应用，并保存相关凭证。

设置向导将执行以下操作：
1. 在终端中显示一个二维码
2. 等待您使用 WeCom 手机应用进行扫描
3. 自动获取机器人 ID 和密钥
4. 指导您完成访问控制配置

#### 备选方案：手动设置

如果无法通过扫描创建，向导将转为手动输入方式：
1. 登录 [WeCom 管理控制台](https://work.weixin.qq.com/wework_admin/frame)
2. 导航至 **Applications** → **Create Application** → **AI Bot**
3. 设置机器人的名称和描述
4. 从凭证页面复制**机器人 ID**和**密钥**
5. 运行 `hermes gateway setup`，选择**WeCom**，并在提示时输入相应凭证

:::warning
请严格保密机器人密钥。任何获取到该密钥的人都可以冒充您的机器人。
:::

### 第 2 步：配置 Hermes

#### 方案 A：交互式设置（推荐）

```bash
hermes gateway setup
```

选择**WeCom**，然后按照提示操作。向导将引导您完成以下步骤：
- 机器人凭证配置（通过二维码扫描或手动输入）
- 访问控制设置（允许列表、配对模式或开放访问）
- 用于接收通知的主频道设置

#### 方案 B：手动配置

在 `~/.hermes/.env` 文件中添加以下内容：

```bash
WECOM_BOT_ID=your-bot-id
WECOM_SECRET=your-secret

# Optional: restrict access
WECOM_ALLOWED_USERS=user_id_1,user_id_2

# Optional: home channel for cron/notifications
WECOM_HOME_CHANNEL=chat_id
```

### 第 3 步：启动网关

```bash
hermes gateway
```

## 功能特性

- **WebSocket传输** —— 支持持久连接，无需公开端点  
- **私信与群组消息** —— 可配置的访问策略  
- **群组级发件人白名单** —— 对每个群组内的交互者进行精细控制  
- **媒体文件支持** —— 支持图片、文件、语音及视频的上传与下载  
- **AES加密的媒体文件** —— 自动解密传入的附件  
- **引用上下文功能** —— 保留回复的线程结构  
- **Markdown格式渲染** —— 支持富文本回复  
- **回复关联机制** —— 回复会与原始消息的上下文相关联  
- **自动重连功能** —— 连接断开时采用指数退避策略重新连接  

:::注意：流式响应与输入指示器  
WeCom适配器通过WeCom的`msgtype: "stream"`协议原生实现流式响应：一旦开始生成回复，客户端会立即显示思考/输入中状态；模型逐词生成回复时，这些内容会依次显示在同一个对话框中，同时工具调用的进度也会显示在该对话框内。默认情况下已启用原生流式响应（在`config.yaml`中设置`display.platforms.wecom.streaming: true`）；如需恢复单次响应模式，可将其值设为`false`。:::

## 配置选项

请在`config.yaml`的`platforms.wecom.extra`部分进行配置：

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `bot_id` | — | WeCom AI 机器人 ID（必填） |
| `secret` | — | WeCom AI 机器人密钥（必填） |
| `websocket_url` | `wss://openws.work.weixin.qq.com` | WebSocket 网关地址 |
| `dm_policy` | `open` | 私信访问权限：`open`、`allowlist`、`disabled`、`pairing` |
| `group_policy` | `open` | 群聊访问权限：`open`、`allowlist`、`disabled` |
| `allow_from` | `[]` | 当 `dm_policy` 设为 `allowlist` 时允许发送私信的用户 ID 列表 |
| `group_allow_from` | `[]` | 当 `group_policy` 设为 `allowlist` 时允许加入的群聊 ID 列表 |
| `groups` | `{}` | 每个群聊的独立配置（详见下文） |
| `stream_keepalive_enabled` | `false` | 是否定期发送保持连接帧，以在对话较长时刷新 WeCom 约6分钟的回复流超时时间 |
| `stream_keepalive_interval_seconds` | `120` | 启用该功能时的保持连接帧发送间隔（秒） |
| `stream_safe_duration_seconds` | `330` | 达到此时长后，流式传输机制将优先选择可靠的主动发送方式 |

## 访问权限策略

### 私信策略

用于控制谁可以向机器人发送私信：

| 值 | 行为 |
|-------|--------|
| `open` | 任何人都可以向机器人发送私信（默认值） |
| `allowlist` | 仅允许 `allow_from` 列表中的用户发送私信 |
| `disabled` | 拒绝所有私信请求 |
| `pairing` | 配对模式（用于初始设置） |

```bash
WECOM_DM_POLICY=allowlist
```

### 群组策略

用于控制机器人响应的群组范围：

| 值 | 行为 |
|-------|----------|
| `open` | 机器人响应所有群组（默认值） |
| `allowlist` | 机器人仅响应 `group_allow_from` 中列出的群组 ID 对应的群组 |
| `disabled` | 忽略所有群组中的消息 |

```bash
WECOM_GROUP_POLICY=allowlist
```

### 按群组划分的发送者白名单

为实现更精细的控制，您可以限制特定群组中哪些用户能够与机器人进行交互。该设置可在 `config.yaml` 文件中进行配置：

```yaml
platforms:
  wecom:
    enabled: true
    extra:
      bot_id: "your-bot-id"
      secret: "your-secret"
      group_policy: "allowlist"
      group_allow_from:
        - "group_id_1"
        - "group_id_2"
      groups:
        group_id_1:
          allow_from:
            - "user_alice"
            - "user_bob"
        group_id_2:
          allow_from:
            - "user_charlie"
        "*":
          allow_from:
            - "user_admin"
```

**工作原理：**

1. `group_policy` 和 `group_allow_from` 控制规则用于决定是否允许某个群组接入。
2. 若群组通过顶层检查，还会进一步参考 `groups.<group_id>.allow_from` 列表（如有）来限制该群组中哪些发送者可以与机器人交互。
3. 对于未明确列出的群组，系统会默认使用通配符 `"*"` 来表示允许所有成员。
4. 允许列表中的条目支持使用 `*` 通配符以允许所有用户访问，且条目匹配为不区分大小写。
5. 条目可选地采用 `wecom:user:` 或 `wecom:group:` 前缀格式——系统会自动去掉该前缀。

如果某个群组未配置 `allow_from` 规则，则该群组中的所有用户均被允许接入（前提是该群组本身通过了顶层策略检查）。

## 媒体支持

### 接收媒体

该适配器负责接收用户发送的媒体附件，并将其缓存在本地以便机器人处理：

| 媒体类型 | 处理方式 |
|----------|----------|
| **图片** | 下载后缓存于本地。支持基于 URL 的图片以及 Base64 编码的图片。 |
| **文件** | 下载后缓存。文件名保留自原始消息。 |
| **语音** | 如有，会提取语音消息的文本转录内容。 |
| **混合消息** | 会解析 WeCom 的混合类型消息（文本+图片），并提取所有组成部分。 |

**引用消息：** 对于被引用的（回复的）消息中的媒体内容也会被提取出来，这样机器人就能了解用户正在回复什么内容。

### AES 加密媒体的解密

WeCom会使用AES-256-CBC算法对部分传入的媒体附件进行加密。该适配器会自动处理这一流程：

- 当传入的媒体内容包含`aeskey`字段时，适配器会下载这些加密数据，并使用带有PKCS#7填充方式的AES-256-CBC算法对其进行解密。
- AES密钥为`aeskey`字段经过base64解码后的结果（长度必须恰好为32字节）。
- 初始向量（IV）则由密钥的前16字节生成。
- 此功能需要安装`cryptography` Python包（可通过`pip install cryptography`命令安装）。

无需任何额外配置——一旦收到加密媒体文件，解密操作就会在后台自动完成。

### 发送（Outbound）

| 方法 | 发送内容 | 大小限制 |
|------|----------|----------|
| `send` | Markdown格式的文本消息 | 4000字符 |
| `send_image` / `send_image_file` | 原生图片消息 | 10 MB |
| `send_document` | 文件附件 | 20 MB |
| `send_voice` | 语音消息（原生语音仅支持AMR格式） | 2 MB |
| `send_video` | 视频消息 | 10 MB |

**分块上传：** 文件会通过“初始化→分块传输→完成”三步流程，以512 KB为大小单位进行上传。该适配器会自动处理这一过程。

**自动降级处理：** 当媒体文件的大小虽超出其对应类型的标准限制，但仍在20 MB的总体文件限制范围内时，系统会自动将其作为普通文件附件发送：
- 大于10 MB的图片 → 作为文件发送
- 大于10 MB的视频 → 作为文件发送
- 大于2 MB的语音文件 → 作为文件发送
- 非AMR格式的音频 → 作为文件发送（WeCom仅支持AMR格式的原生语音）
当文件大小超过20 MB的绝对限制时，系统会拒绝处理该文件，并在聊天界面中发送提示信息。

## 回复模式响应

当机器人通过WeCom回调接收到消息后，适配器会记录下该请求的ID。如果在请求上下文仍然有效的情况下发送回复，适配器会使用WeCom的回复模式（`aibot_respond_msg`）将回复直接与原始消息关联起来。这样一来，就能在WeCom客户端中实现更自然的对话体验。

当处于原生回复流模式时，回复会通过回复模式下的`msgtype: "stream"`帧逐条发送。如果原始请求的上下文已过期或不可用（或者某个流帧发送失败），适配器则会退而使用`aibot_send_msg`功能主动发送消息。

回复模式同样适用于媒体内容：上传的媒体文件可以作为对原始消息的回复被发送出去。

## 连接与重连

适配器会维持与WeCom网关的持久WebSocket连接，其地址为`wss://openws.work.weixin.qq.com`。

### 连接生命周期

1. **连接建立**：打开WebSocket连接，并发送包含bot_id和密钥的`aibot_subscribe`认证帧。
2. **心跳检测**：每隔30秒发送应用层的心跳帧，以保持连接活跃。
3. **消息监听**：持续读取传入的帧数据，并触发相应的消息回调。

### 重连机制

在连接中断时，适配器会采用指数退避策略来尝试重新建立连接：

| 尝试次数 | 延迟时间 |
|---------|-------|
| 第1次重试 | 2秒 |
| 第2次重试 | 5秒 |
| 第3次重试 | 10秒 |
| 第4次重试 | 30秒 |
| 第5次及以后重试 | 60秒 |

每次成功重新连接后，退避计数器将重置为零。在连接断开时，所有待处理的请求都会被标记为失败，从而避免调用方无限期挂起。

### 冗余消息处理

系统会通过消息ID在5分钟的时间窗口内对传入的消息进行去重处理，最大缓存容量为1000条记录。这样一来，即便在重新连接或网络出现故障时，也能防止消息被重复处理。

## 所有环境变量

| 变量名 | 是否必填 | 默认值 | 描述 |
|--------|----------|-------|------|
| `WECOM_BOT_ID` | ✅ | — | WeCom AI机器人编号 |
| `WECOM_SECRET` | ✅ | — | WeCom AI机器人密钥 |
| `WECOM_ALLOWED_USERS` | — | _(空)_ | 用于网关级白名单的、以逗号分隔的用户编号列表 |
| `WECOM_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天ID |
| `WECOM_WEBSOCKET_URL` | — | `wss://openws.work.weixin.qq.com` | WebSocket网关地址 |
| `WECOM_DM_POLICY` | — | `open` | 私信访问策略 |
| `WECOM_GROUP_POLICY` | — | `open` | 群组访问策略 |

## 故障排除

| Problem | Fix |
|---------|-----|
| `WECOM_BOT_ID and WECOM_SECRET are required` | Set both env vars or configure in setup wizard |
| `WeCom startup failed: aiohttp not installed` | Install aiohttp: `pip install aiohttp` |
| `WeCom startup failed: httpx not installed` | Install httpx: `pip install httpx` |
| `invalid secret (errcode=40013)` | Verify the secret matches your bot's credentials |
| `Timed out waiting for subscribe acknowledgement` | Check network connectivity to `openws.work.weixin.qq.com` |
| Bot doesn't respond in groups | Check `group_policy` setting and ensure the group ID is in `group_allow_from` |
| Bot ignores certain users in a group | Check per-group `allow_from` lists in the `groups` config section |
| Media decryption fails | Install `cryptography`: `pip install cryptography` |
| `cryptography is required for WeCom media decryption` | The inbound media is AES-encrypted. Install: `pip install cryptography` |
| Voice messages sent as files | WeCom only supports AMR format for native voice. Other formats are auto-downgraded to file. |
| `File too large` error | WeCom has a 20 MB absolute limit on all file uploads. Compress or split the file. |
| Images sent as files | Images > 10 MB exceed the native image limit and are auto-downgraded to file attachments. |
| `Timeout sending message to WeCom` | The WebSocket may have disconnected. Check logs for reconnection messages. |
| `WeCom websocket closed during authentication` | Network issue or incorrect credentials. Verify bot_id and secret. |
