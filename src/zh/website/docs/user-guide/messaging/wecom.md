---
sidebar_position: 14
title: "WeCom (Enterprise WeChat)"
description: "Connect Hermes Agent to WeCom via the AI Bot WebSocket gateway"
---

# WeCom（企业微信）

可将 Hermes 连接到腾讯的企业级即时通讯平台 [WeCom](https://work.weixin.qq.com/)。该适配器利用 WeCom 的 AI 机器人 WebSocket 网关实现实时双向通信，无需使用公共端点或 webhook。

如需设置接收方 webhook，请参阅：[WeCom 回调功能](./wecom-callback.md)。

## 前提条件

- 一个 WeCom 组织账号
- 在 WeCom 管理控制台创建的 AI 机器人
- 从机器人凭证页面获取的机器人 ID 和密钥
- Python 包：`aiohttp` 和 `httpx`

## 设置步骤

### 第 1 步：创建 AI 机器人

#### 推荐方式：扫描创建（仅需一条命令）

```bash
hermes gateway setup
```

选择**WeCom**，然后使用您的 WeCom 手机应用扫描二维码。Hermes 将自动创建具有相应权限的机器人应用，并保存相关凭证。

设置向导将执行以下操作：
1. 在终端中显示一个二维码
2. 等待您使用 WeCom 手机应用进行扫描
3. 自动获取机器人 ID 和密钥
4. 指导您完成访问控制配置

#### 备选方案：手动设置

如果无法通过扫描创建，向导将转为手动输入方式：
1. 登录[WeCom 管理控制台](https://work.weixin.qq.com/wework_admin/frame)
2. 导航至**应用程序** → **创建应用** → **AI 机器人**
3. 设置机器人的名称和描述
4. 从凭证页面复制**机器人 ID**和**密钥**
5. 运行 `hermes gateway setup`，选择**WeCom**，并在提示时输入相应凭证

:::warning
请务必妥善保管机器人密钥，任何获取到该密钥的人都可以冒充您的机器人。
:::

### 第 2 步：配置 Hermes

#### 方案 A：交互式设置（推荐）

```bash
hermes gateway setup
```

选择**WeCom**，然后按照提示操作。向导将引导您完成以下步骤：
- 机器人凭证设置（通过二维码扫描或手动输入）
- 访问控制配置（允许列表、配对模式或开放访问）
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

### 第3步：启动网关

```bash
hermes gateway
```

## 功能特性

- **WebSocket传输** —— 支持持久连接，无需公开端点  
- **私信与群组消息** —— 可配置的访问策略  
- **群组级发件人白名单** —— 对每个群组内的互动用户进行精细控制  
- **多媒体支持** —— 支持图片、文件、语音及视频的上传与下载  
- **AES加密媒体传输** —— 自动解密接收到的附件  
- **引用上下文功能** —— 保留回复的线程结构  
- **Markdown格式渲染** —— 提供富文本形式的回复  
- **回复关联机制** —— 回复会与原始消息的上下文相关联  
- **自动重连功能** —— 连接断开时采用指数退避策略重新连接  

:::注意：流式响应与输入状态指示  
WeCom适配器会将每条回复作为一条完整的消息发送——它**不会**逐个字符地流式发送回复，也不会显示输入状态指示。上述的“回复关联机制”仅用于将回复与其对应的原始请求关联起来，并非实时流式传输。:::

## 配置选项

请在`config.yaml`文件中的`platforms.wecom.extra`部分设置以下参数：

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `bot_id` | — | WeCom智能机器人ID（必填） |
| `secret` | — | WeCom智能机器人密钥（必填） |
| `websocket_url` | `wss://openws.work.weixin.qq.com` | WebSocket网关地址 |
| `dm_policy` | `open` | 私信访问权限：`open`、`allowlist`、`disabled`、`pairing` |
| `group_policy` | `open` | 群组访问权限：`open`、`allowlist`、`disabled` |
| `allow_from` | `[]` | 当`dm_policy`设置为`allowlist`时，允许发送私信的用户ID列表 |
| `group_allow_from` | `[]` | 当`group_policy`设置为`allowlist`时，允许加入的群组ID列表 |
| `groups` | `{}` | 各群组的独立配置（详见下文） |

## 访问策略

### 私信策略

用于控制谁可以向该机器人发送私信：

| 值 | 行为说明 |
|-------|----------|
| `open` | 任何人都可以向机器人发送私信（默认值） |
| `allowlist` | 仅允许`allow_from`列表中的用户发送私信 |
| `disabled` | 拒绝所有私信请求 |
| `pairing` | 配对模式（用于初始设置阶段） |

```bash
WECOM_DM_POLICY=allowlist
```

### 群组策略

用于控制机器人响应的群组范围：

| 值 | 行为 |
|-------|----------|
| `open` | 机器人响应所有群组（默认值） |
| `allowlist` | 机器人仅响应 `group_allow_from` 中列出的群组 ID 对应的群组 |
| `disabled` | 忽略所有群组消息 |

```bash
WECOM_GROUP_POLICY=allowlist
```

### 按群组划分的发送者白名单

为了实现更精细的控制，您可以限制特定群组中哪些用户能够与机器人交互。该设置可在 `config.yaml` 文件中进行配置：

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
2. 若群组通过顶层检查，那么 `groups.<group_id>.allow_from` 列表（若存在）将进一步限制该群组中哪些发送者可以与机器人交互。
3. 未明确列出的群组默认使用通配符 `"*"` 来表示允许所有成员。
4. 允许列表中的条目支持使用 `*` 通配符来允许所有用户，且条目匹配时不区分大小写。
5. 条目可选地采用 `wecom:user:` 或 `wecom:group:` 前缀格式——该前缀会自动被移除。

如果某个群组未配置 `allow_from`，则假定该群组本身通过了顶层策略检查，群组中的所有用户均被允许接入。

## 媒体支持

### 接收媒体

适配器会接收用户发送的媒体附件，并将其本地缓存以便机器人处理：

| 类型 | 处理方式 |
|------|----------|
| **图片** | 下载后本地缓存。支持基于 URL 的图片以及 Base64 编码的图片。 |
| **文件** | 下载后缓存。文件名保留自原始消息。 |
| **语音** | 如有语音消息，会提取其文本转录内容。 |
| **混合消息** | WeCom 的混合类型消息（文本+图片）会被解析，并提取所有组成部分。 |

**引用消息：** 引用（回复）消息中的媒体也会被提取出来，这样机器人就能了解用户正在回复什么内容。

### AES 加密媒体的解密

WeCom 会使用 AES-256-CBC 对部分接收到的媒体附件进行加密。适配器可自动处理此功能：

- 当接收到的媒体项包含 `aeskey` 字段时，适配器会下载加密后的字节数据，并使用 PKCS#7 填充方式通过 AES-256-CBC 进行解密。
- AES 密钥为 `aeskey` 字段经 Base64 解码后的值（长度必须恰好为 32 字节）。
- 初始化向量（IV）由密钥的前 16 字节生成。
- 此功能需要安装 `cryptography` Python 包（可通过 `pip install cryptography` 安装）。

无需额外配置——一旦收到加密媒体，解密过程会自动完成。

### 发送媒体

| 方法 | 发送内容 | 大小限制 |
|------|----------|----------|
| `send` | Markdown 格式的文本消息 | 4000 字符 |
| `send_image` / `send_image_file` | 原生图片消息 | 10 MB |
| `send_document` | 文件附件 | 20 MB |
| `send_voice` | 语音消息（原生语音仅支持 AMR 格式） | 2 MB |
| `send_video` | 视频消息 | 10 MB |

**分块上传：** 文件会通过“初始化→分块传输→完成”三步协议，以 512 KB 的块大小进行上传。适配器可自动处理此流程。

**自动降级处理：** 当媒体大小超过其对应类型的上限，但仍在 20 MB 的总文件限制之内时，系统会自动将其作为普通文件附件发送：

- 图片大于 10 MB → 作为文件发送
- 视频大于 10 MB → 作为文件发送
- 语音大于 2 MB → 作为文件发送
- 非 AMR 格式的音频 → 作为文件发送（WeCom 原生语音仅支持 AMR 格式）

超过 20 MB 的文件会被拒绝，同时会在聊天界面显示相关提示信息。

## 回复模式响应

当机器人通过 WeCom 回调接收到消息时，适配器会记住该请求的 ID。如果在请求上下文仍然有效时发送响应，适配器会使用 WeCom 的回复模式（`aibot_respond_msg`）将响应直接与原始消息关联起来。这样能在 WeCom 客户端带来更自然的对话体验。

完整响应会以单条消息的形式发送——适配器不会逐次分批发送消息内容。如果原始请求的上下文已过期或不可用，适配器则会退而使用 `aibot_send_msg` 方法主动发送消息。

回复模式也适用于媒体：上传的媒体可以作为对原始消息的回复进行发送。

## 连接与重连

适配器会保持与 WeCom 网关的持久 WebSocket 连接，地址为 `wss://openws.work.weixin.qq.com`。

### 连接生命周期

1. **连接：** 建立 WebSocket 连接，并发送包含 bot_id 和密钥的 `aibot_subscribe` 认证帧。
2. **心跳检测：** 每 30 秒发送一次应用层的心跳帧，以维持连接活跃状态。
3. **消息监听：** 持续读取传入的帧，并触发相应的消息回调。

### 重连机制

当连接中断时，适配器会采用指数退避策略尝试重新连接：

| 重试次数 | 延迟时间 |
|---------|----------|
| 第 1 次重试 | 2 秒 |
| 第 2 次重试 | 5 秒 |
| 第 3 次重试 | 10 秒 |
| 第 4 次重试 | 30 秒 |
| 第 5 次及以后 | 60 秒 |

每次成功重新连接后，退避计数器会重置为 0。在连接断开时，所有待处理的请求都会被标记为失败，从而避免调用方无限期挂起。

### 去重处理

通过消息 ID 对接收到的消息进行去重处理，去重窗口时间为 5 分钟，缓存最大容量为 1000 条记录。这样可以防止在连接恢复或网络故障期间对消息进行重复处理。

## 所有环境变量

| 变量名 | 是否必填 | 默认值 | 说明 |
|--------|----------|--------|------|
| `WECOM_BOT_ID` | ✅ | — | WeCom AI 机器人 ID |
| `WECOM_SECRET` | ✅ | — | WeCom AI 机器人密钥 |
| `WECOM_ALLOWED_USERS` | — | _(空)_ | 以逗号分隔的用户名列表，用于网关级别的允许列表 |
| `WECOM_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天 ID |
| `WECOM_WEBSOCKET_URL` | — | `wss://openws.work.weixin.qq.com` | WebSocket 网关地址 |
| `WECOM_DM_POLICY` | — | `open` | 私信访问策略 |
| `WECOM_GROUP_POLICY` | — | `open` | 群组访问策略 |

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `需要设置 WECOM_BOT_ID 和 WECOM_SECRET` | 设置这两个环境变量，或在设置向导中完成配置 |
| `WeCom 启动失败：未安装 aiohttp` | 安装 aiohttp：`pip install aiohttp` |
| `WeCom 启动失败：未安装 httpx` | 安装 httpx：`pip install httpx` |
| `密钥无效（错误码=40013）` | 确认密钥与机器人的凭证一致 |
| `等待订阅确认超时` | 检查与 `openws.work.weixin.qq.com` 的网络连接 |
| 机器人在群组中无响应 | 检查 `group_policy` 设置，确保该群组 ID 已包含在 `group_allow_from` 中 |
| 机器人忽略群组中的某些用户 | 查看 `groups` 配置部分中的各群组专用 `allow_from` 列表 |
| 媒体解密失败 | 安装 `cryptography`：`pip install cryptography` |
| `WeCom 媒体解密需要 cryptography` | 接收到的媒体为 AES 加密格式，需安装该包：`pip install cryptography` |
| 语音消息被作为文件发送 | WeCom 原生语音仅支持 AMR 格式，其他格式会自动降级为文件发送 |
| `文件过大` 错误 | WeCom 对所有文件上传设有 20 MB 的绝对上限，建议压缩或分割文件 |
| 图片被作为文件发送 | 大于 10 MB 的图片超过了原生图片的限制，会被自动降级为文件附件 |
| `向 WeCom 发送消息超时` | 可能是 WebSocket 连接已断开，查看日志中的重连信息 |
| `认证过程中 WeCom WebSocket 被关闭` | 可能是网络问题或凭证错误，请确认 bot_id 和密钥是否正确 |
