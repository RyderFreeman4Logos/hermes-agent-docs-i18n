# SimpleX Chat

[SimpleX Chat](https://simplex.chat/) 是一个私有的去中心化消息平台，用户可自主掌控自己的联系人及群组。与其他平台不同，SimpleX 不会为用户分配永久性的用户 ID——每个联系人都会通过连接时生成的随机内部 ID 来标识，这一设计使其成为目前隐私保护最为出色的消息应用之一。

> 运行 `hermes gateway setup` 命令，并选择 **SimpleX** 以获取操作指南。

## 先决条件

- 已安装 **simplex-chat** CLI 并以守护进程形式运行
- 已安装 Python 包 **websockets**（可通过 `pip install websockets` 安装）

## 安装 simplex-chat

请从 [simplex-chat GitHub 发布页面](https://github.com/simplex-chat/simplex-chat/releases)下载最新版本：

```bash
# Linux / macOS binary
curl -L https://github.com/simplex-chat/simplex-chat/releases/latest/download/simplex-chat-ubuntu-22_04-x86_64 -o simplex-chat
chmod +x simplex-chat
```

SimpleX Chat 项目并未为该聊天客户端提供预构建的 Docker 镜像；若想在 Docker 环境中运行它，需从 [simplex-chat 仓库](https://github.com/simplex-chat/simplex-chat) 中获取源代码并自行构建。

## 启动守护进程

```bash
simplex-chat -p 5225
```

默认情况下，该守护进程会在 `ws://127.0.0.1:5225` 的 WebSocket 端口上监听请求。

## 配置 Hermes

### 通过设置向导

```bash
hermes gateway setup
```

选择 **SimpleX Chat**，然后按照提示操作。

### 通过环境变量设置

将这些内容添加到 `~/.hermes/.env` 文件中：

```
SIMPLEX_WS_URL=ws://127.0.0.1:5225
SIMPLEX_ALLOWED_USERS=<contact-id-1>,<contact-id-2>
SIMPLEX_HOME_CHANNEL=<contact-id>
```

| 变量 | 是否必填 | 描述 |
|---|---|---|
| `SIMPLEX_WS_URL` | 是 | simplex-chat 守护进程的 WebSocket 地址 |
| `SIMPLEX_ALLOWED_USERS` | 建议使用 | 以逗号分隔的允许列表。每项可以是数字形式的 `contactId`，也可以是显示名称——两种形式均可。 |
| `SIMPLEX_ALLOW_ALL_USERS` | 可选 | 设置为 `true` 即可允许所有联系人（请谨慎使用） |
| `SIMPLEX_AUTO_ACCEPT` | 可选 | 自动接受来自其他联系人的添加请求（默认值为 `true`） |
| `SIMPLEX_GROUP_ALLOWED` | 可选 | 以逗号分隔的机器人可加入的群组 ID，或使用 `*` 表示所有群组。若省略此参数，则完全忽略群组消息 |
| `SIMPLEX_HOME_CHANNEL` | 可选 | 用于定时任务通知的默认联系人/群组 ID |
| `SIMPLEX_HOME_CHANNEL_NAME` | 可选 | 主通道的人性化标签 |
| `HERMES_SIMPLEX_TEXT_BATCH_DELAY` | 可选 | 静默间隔秒数（默认值为 `0.8`），用于将连续发送的文本消息合并为一个事件 |

## 查找您的联系人 ID 或显示名称

启动守护进程后，与您的机器人联系人开启对话。数字形式的 `contactId` 会出现在会话日志中。如果您希望使用 SimpleX 用户界面中显示的名称，那也是可行的——`SIMPLEX_ALLOWED_USERS` 接受这两种形式。

## 权限设置

默认情况下**所有联系人都会被拒绝访问**。您必须：

1. 将 `SIMPLEX_ALLOWED_USERS` 设置为以逗号分隔的 `contactId` 和/或显示名称列表（例如，`SIMPLEX_ALLOWED_USERS=4,alice` 表示允许 ID 为 4 的联系人或显示名称为 “alice” 的联系人），或者  
2. 使用**私信配对**方式——向该机器人发送任意消息，它便会回复一个配对码。通过命令 `hermes pairing approve simplex <CODE>` 输入该代码即可。

## 群聊

默认情况下，此适配器会忽略群聊消息——否则，群组中的机器人将需要处理所有成员的通信。如需使用群聊功能，请明确开启相应选项：

```
SIMPLEX_GROUP_ALLOWED=12,34          # specific group IDs
# or
SIMPLEX_GROUP_ALLOWED=*              # any group the bot is in
```

若要通过前缀为聊天 ID 添加 `group:` 来对群组进行指定，例如：可将 `simplex:group:12` 用作 cron 的 `deliver=` 目标，或直接在 `hermes send` 调用中使用。

## 使用 `hermes send` 发送消息

SimpleX 可作为独立的发送目标使用——虽然必须运行对应的守护进程，但对于纯文本消息而言，并不需要实时运行的网关。

```bash
hermes send --to simplex:alice "hello"          # DM by contact display name
hermes send --to simplex:group:12 "hello"       # group by numeric ID
hermes send --to simplex "hello"                # SIMPLEX_HOME_CHANNEL
```

在网关运行期间，适配器会定期（每5分钟刷新一次）将您的联系人及允许加入的群组列出到频道目录中，因此使用 `hermes send --list` 命令即可按名称查看这些联系人及群组。在首次启动网关之前，该平台仍会出现在 `--list` 的列表中，并显示“尚未发现任何频道”的提示——不过上述那种直接指定的目标地址依然可以正常使用。

## 附件处理

该适配器支持双向传输原生 SimpleX 附件功能：

- **接收端**——通过守护进程的 XFTP 流程（`rcvFileDescrReady` → `/freceive` → 等待 `rcvFileComplete`）接收传入的图片、语音笔记和文件，这些附件会以 `MessageEvent.media_urls` 的形式呈现，并附带相应的 `MessageType`（如 `PHOTO`、`VOICE`、`TEXT` 以及文档类型）。
- **发送端**——`send_image_file`、`send_voice`、`send_document` 和 `send_video` 等函数均使用包含 `filePath` 的结构化 `/_send` 格式进行发送，这样接收端的 SimpleX 客户端就能直接在线显示图片并播放语音笔记，而无需让用户下载。

Agent 的回复内容中也可以嵌入 `MEDIA:/path/to/file` 标签——适配器会自动从回复文本中提取该标签，并将对应文件作为语音笔记（音频格式）或文档进行发送。

## 结合 cron 任务使用 SimpleX

```python
cronjob(
    action="create",
    schedule="every 1h",
    deliver="simplex",          # uses SIMPLEX_HOME_CHANNEL
    prompt="Check for alerts and summarise."
)
```

或者通过定时任务的 `deliver:` 字段来指定特定联系人，也可以借助 [`hermes send` CLI](/guides/pipe-script-output) 在Shell脚本中实现该操作。

```bash
hermes send simplex:<contact-id> "Done!"
```

## 隐私说明

- SimpleX 绝不会泄露电话号码或电子邮件地址——联系人之间仅通过匿名标识进行交互  
- Hermes 与后台服务之间的连接为本地 WebSocket 协议（`ws://127.0.0.1:5225`）——数据不会离开您的设备  
- 消息在传输至后台服务之前，会先通过 SimpleX 协议进行端到端加密  

## 故障排除

**错误提示：“无法连接到后台服务”** ——请确认 `simplex-chat -p 5225` 已在运行，且端口与 `SIMPLEX_WS_URL` 设置一致。  

**错误提示：“未安装 websockets 库”** ——请执行命令 `pip install websockets` 进行安装。  

**消息无法接收** ——请检查该联系人的标识是否已添加到 `SIMPLEX_ALLOWED_USERS` 列表中，或通过私信配对方式对其进行授权。
