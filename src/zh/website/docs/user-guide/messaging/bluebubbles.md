# BlueBubbles（iMessage）

可通过 [BlueBubbles](https://bluebubbles.app/) 将 Hermes 连接到 Apple iMessage —— 这是一款免费的开源 macOS 服务器，能够实现 iMessage 与任意设备的通信。

## 前提条件

- 一台运行着 [BlueBubbles Server](https://bluebubbles.app/) 的**Mac 电脑**（且需保持开机状态）
- 该 Mac 上的 Messages.app 已登录对应的 Apple ID
- BlueBubbles Server 版本需为 v1.0.0 或更高（Webhook 功能需要此版本）
- Hermes 与 BlueBubbles 服务器之间需具备网络连接

## 设置步骤

### 1. 安装 BlueBubbles Server

从 [bluebubbles.app](https://bluebubbles.app/) 下载并安装该软件。按照设置向导完成配置：使用您的 Apple ID 登录，并选择连接方式（局域网、Ngrok、Cloudflare 或动态域名）。

### 2. 获取服务器地址与密码

在 BlueBubbles Server 中进入 **设置 → API**，记下以下信息：
- **服务器地址**（例如：`http://192.168.1.10:1234`）
- **服务器密码**

### 3. 配置 Hermes

运行设置向导即可完成配置。

```bash
hermes gateway setup
```

选择**BlueBubbles (iMessage)**，然后输入您的服务器地址和密码。

或者直接在`~/.hermes/.env`文件中设置环境变量：

```bash
BLUEBUBBLES_SERVER_URL=http://192.168.1.10:1234
BLUEBUBBLES_PASSWORD=your-server-password
```

#### 可选功能：要求在群聊中提及才能响应

默认情况下，Hermes 会回应所有经过授权的 BlueBubbles/iMessage 私信及群聊消息。若希望让群聊消息需要主动触发响应，可启用“提及验证”功能：

```yaml
platforms:
  bluebubbles:
    enabled: true
    extra:
      require_mention: true
```

当设置 `require_mention: true` 时，私信功能仍可正常使用，但群聊消息除非符合指定的提及模式，否则会被忽略。如果您未自定义匹配模式，Hermes 将对 “Hermes” 及 “@Hermes agent” 这两种格式采用较为保守的默认设置。

如需使用自定义智能体名称，请设置正则表达式模式：

```yaml
platforms:
  bluebubbles:
    extra:
      require_mention: true
      mention_patterns:
        - '(?<![\w@])@?amos\b[,:\-]?'
```

### 4. 授权用户

请选择一种方式：

**直接消息配对（推荐）：**
当有人给您发送 iMessage 时，Hermes 会自动向对方发送配对码。您只需通过以下操作进行确认即可：
```bash
hermes pairing approve bluebubbles <CODE>
```
使用 `hermes pairing list` 命令可以查看待验证的代码以及已通过授权的用户。

**在 `~/.hermes/.env` 文件中预授权特定用户**：
```bash
BLUEBUBBLES_ALLOWED_USERS=user@icloud.com,+15551234567
```

**开放访问权限**（位于 `~/.hermes/.env` 文件中）：
```bash
BLUEBUBBLES_ALLOW_ALL_USERS=true
```

### 5. 启动网关

```bash
hermes gateway run
```

Hermes将会连接到您的BlueBubbles服务器，注册一个Webhook，进而开始监听iMessage消息。 

## 工作原理

```
iMessage → Messages.app → BlueBubbles Server → Webhook → Hermes
Hermes → BlueBubbles REST API → Messages.app → iMessage
```

- **接收消息**：当有新消息到达时，BlueBubbles会向本地监听器发送Webhook事件。无需轮询，可实现即时传递。
- **发送消息**：Hermes通过BlueBubbles的REST API来发送消息。
- **多媒体内容**：双向通信均支持图片、语音消息、视频和文档。接收到的附件会被下载并缓存到本地，以便智能体处理。

## 环境变量

| 变量名 | 是否必填 | 默认值 | 描述 |
|--------|----------|--------|------|
| `BLUEBUBBLES_SERVER_URL` | 是 | — | BlueBubbles服务器地址 |
| `BLUEBUBBLES_PASSWORD` | 是 | — | 服务器密码 |
| `BLUEBUBBLES_WEBHOOK_HOST` | 否 | `127.0.0.1` | Webhook监听器的绑定地址 |
| `BLUEBUBBLES_WEBHOOK_PORT` | 否 | `8645` | Webhook监听器端口 |
| `BLUEBUBBLES_WEBHOOK_PATH` | 否 | `/bluebubbles-webhook` | Webhook URL路径 |
| `BLUEBUBBLES_HOME_CHANNEL` | 否 | — | 用于定时发送消息的电话号码或邮箱地址 |
| `BLUEBUBBLES_ALLOWED_USERS` | 否 | — | 以逗号分隔的授权用户列表 |
| `BLUEBUBBLES_ALLOW_ALL_USERS` | 否 | `false` | 允许所有用户发送消息 |
| `BLUEBUBBLES_REQUIRE_MENTION` | 否 | `false` | 在群组聊天中回复前是否需要指定被提及对象 |
| `BLUEBUBBLES_MENTION_PATTERNS` | 否 | Hermes唤醒词 | 用于匹配群组中被提及对象的JSON数组，各模式之间以换行符或逗号分隔 |

是否自动标记消息为已读，由`~/.hermes/config.yaml`文件中`platforms.bluebubbles.extra`下的`send_read_receipts`键控制（默认值为`true`）。目前暂无对应的环境变量。

## 功能特性

### 文本消息
可以发送和接收iMessage。系统会自动去除Markdown格式，以确保以纯净的纯文本形式传递。

### 多媒体内容
- **图片**：照片会直接显示在iMessage对话中。
- **语音消息**：音频文件会作为iMessage语音消息发送。
- **视频**：支持发送视频附件。
- **文档**：文件可作为iMessage附件发送。

### 回复表情
包括“喜欢”、“点赞”、“不喜欢”、“大笑”、“强调”和“疑问”等表情反应。此功能需要使用BlueBubbles的[私有API辅助工具](https://docs.bluebubbles.app/helper-bundle/installation)。

### 输入中提示
当智能体正在处理消息时，会在iMessage对话中显示“正在输入...”的状态。此功能同样需要私有API支持。

### 已读回执
消息处理完成后会自动标记为已读。此功能也需要私有API支持。

### 聊天地址指定
可以通过邮箱或电话号码来指定聊天对象——Hermes会自动将其转换为BlueBubbles的聊天GUID，无需手动输入原始GUID格式。

## 私有API

部分功能需要使用BlueBubbles的[私有API辅助工具](https://docs.bluebubbles.app/helper-bundle/installation)：
- 回复表情功能
- 输入中提示功能
- 已读回执功能
- 根据地址创建新聊天功能

即使没有私有API，基础的文本消息发送和多媒体传输功能依然可用。

## 故障排除

### “无法连接到服务器”
- 确认服务器URL正确且Mac电脑已开机。
- 检查BlueBubbles服务器是否正在运行。
- 确保网络连接正常（检查防火墙和端口转发设置）。

### 消息未送达
- 进入BlueBubbles服务器的“设置”→“API”→“Webhooks”，确认Webhook已注册。
- 检查从Mac电脑能否访问该Webhook地址。
- 查看`hermes logs gateway`中的Webhook错误信息（或使用`hermes logs -f`实时查看日志）。

### “私有API辅助工具未连接”
- 安装私有API辅助工具：[docs.bluebubbles.app](https://docs.bluebubbles.app/helper-bundle/installation)
- 没有该辅助工具时，基础的消息发送功能仍然可用；只有回复表情、输入中提示和已读回执功能需要它。

