# SimpleX Chat

[SimpleX Chat](https://simplex.chat/) 是一个私有的去中心化消息平台，用户可自主掌控自己的联系人及群组。与其他平台不同，SimpleX 不会为用户分配永久性的用户 ID——每个联系人都会通过连接时生成的随机内部 ID 来标识，这一设计使其成为目前最注重隐私的消息应用之一。

> 运行 `hermes gateway setup` 命令，并选择 **SimpleX** 以获取逐步指导。

## 先决条件

- 已安装 **simplex-chat** CLI 并以守护进程形式运行
- 已安装 Python 包 **websockets**（可通过 `pip install websockets` 安装）

## 安装 simplex-chat

从 [simplex-chat GitHub 发布页面](https://github.com/simplex-chat/simplex-chat/releases)下载最新版本：

```bash
# Linux / macOS binary
curl -L https://github.com/simplex-chat/simplex-chat/releases/latest/download/simplex-chat-ubuntu-22_04-x86_64 -o simplex-chat
chmod +x simplex-chat
```

SimpleX Chat 项目并未提供该聊天客户端的预构建 Docker 镜像；若想在 Docker 环境中运行它，需从 [simplex-chat 仓库](https://github.com/simplex-chat/simplex-chat) 中自行编译源代码。

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
| `SIMPLEX_ALLOWED_USERS` | 建议设置 | 以逗号分隔的允许列表。每项可以是数字形式的 `contactId`，也可以是显示名称——两种形式均可使用 |
| `SIMPLEX_ALLOW_ALL_USERS` | 可选 | 设置为 `true` 即可允许所有联系人（请谨慎使用） |
| `SIMPLEX_AUTO_ACCEPT` | 可选 | 自动接受来自其他联系人的请求（默认值为 `true`） |
| `SIMPLEX_GROUP_ALLOWED` | 可选 | 以逗号分隔的机器人所属群组 ID，或使用 `*` 表示所有群组。若不设置，则完全忽略群组消息 |
| `SIMPLEX_HOME_CHANNEL` | 可选 | 用于定时任务消息发送的默认联系人/群组 ID |
| `SIMPLEX_HOME_CHANNEL_NAME` | 可选 | 主通道的人类可读标签 |
| `HERMES_SIMPLEX_TEXT_BATCH_DELAY` | 可选 | 静默间隔秒数（默认值为 `0.8`），用于将连续发送的文本消息合并为一个事件 |

## 查找您的联系人 ID 或显示名称

启动守护进程后，与您的代理联系人开始对话。数字形式的 `contactId` 可在会话日志中查看，或通过 `hermes send_message action=list` 命令获取。如果您希望使用 SimpleX 用户界面中显示的名称，也是可行的——`SIMPLEX_ALLOWED_USERS` 参数接受这两种形式。

## 权限控制

默认情况下，**所有联系人都会被拒绝访问**。您必须采取以下措施之一：

1. 将 `SIMPLEX_ALLOWED_USERS` 设置为以逗号分隔的 `contactId` 和/或显示名称列表（例如，`SIMPLEX_ALLOWED_USERS=4,alice` 表示允许联系人 ID 为 4 的用户或显示名称为 “alice” 的用户），或者
2. 使用**私信配对**方式——向机器人发送任意消息，它会回复一个配对码。随后通过 `hermes pairing approve simplex <CODE>` 命令输入该代码即可完成授权。

## 群组聊天

默认情况下，该适配器会忽略群组消息——否则处于群组中的机器人将需要处理所有成员的通信。如需启用群组功能，请明确进行配置：

```
SIMPLEX_GROUP_ALLOWED=12,34          # specific group IDs
# or
SIMPLEX_GROUP_ALLOWED=*              # any group the bot is in
```

可通过在聊天 ID 前添加 `group:` 前缀来对消息进行分组，例如在 `send_message` 函数中使用 `simplex:group:12`，或将其作为 Cron 任务的 `deliver=` 目标。

## 附件

该适配器支持双向传输原生 SimpleX 附件：

- **接收端**——通过守护进程的 XFTP 流程接收传入的图片、语音笔记和文件（流程为：`rcvFileDescrReady` → `/freceive` → 等待 `rcvFileComplete`），这些附件会以 `MessageEvent.media_urls` 的形式呈现，并附带相应的 `MessageType`（如 `PHOTO`、`VOICE`、`TEXT` 以及文档类型）。
- **发送端**——`send_image_file`、`send_voice`、`send_document` 和 `send_video` 函数均使用包含 `filePath` 的结构化 `/_send` 格式，这样接收端的 SimpleX 客户端就能直接显示图片并播放语音笔记，而无需让用户下载。

智能体回复中也可以在纯文本中嵌入 `MEDIA:/path/to/file` 标签——适配器会从内容中提取该标签，并将文件以语音笔记（音频格式）或文档的形式发送出去。

## 在 Cron 任务中使用 SimpleX

```python
cronjob(
    action="create",
    schedule="every 1h",
    deliver="simplex",          # uses SIMPLEX_HOME_CHANNEL
    prompt="Check for alerts and summarise."
)
```

或者指定特定的联系人：

```python
send_message(target="simplex:<contact-id>", message="Done!")
```

## 隐私说明

- SimpleX 绝不会泄露电话号码或电子邮件地址——联系人之间仅通过匿名标识进行交互  
- Hermes 与守护进程之间的通信采用本地 WebSocket 协议（`ws://127.0.0.1:5225`）——数据不会离开您的设备  
- 消息在传输至守护进程之前，会先通过 SimpleX 协议进行端到端加密  

## 故障排除

**“无法连接到守护进程”** — 请确认 `simplex-chat -p 5225` 正在运行，且端口与 `SIMPLEX_WS_URL` 设置一致。  

**“未安装 websockets 库”** — 请执行 `pip install websockets` 命令进行安装。  

**“无法接收消息”** — 请检查该联系人的标识是否已列入 `SIMPLEX_ALLOWED_USERS` 列表，或通过私信配对方式将其添加为允许联系人。
