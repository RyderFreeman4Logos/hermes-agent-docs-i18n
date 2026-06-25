---
sidebar_position: 1
title: "Telegram"
description: "Set up Hermes Agent as a Telegram bot"
---

# Telegram集成设置

Hermes Agent以功能完备的对话式机器人的形式与Telegram深度集成。一旦完成连接，您即可在任何设备上与智能体进行聊天，发送会自动转录的语音备忘录，接收定时任务执行结果，还能在群组聊天中使用该智能体。此集成基于[python-telegram-bot](https://python-telegram-bot.org/)构建，支持文本、语音、图片及文件附件的交互。

## 第1步：通过BotFather创建机器人

每个Telegram机器人都需要由Telegram官方的机器人管理工具[@BotFather](https://t.me/BotFather)颁发的API令牌。

1. 打开Telegram并搜索**@BotFather**，或直接访问[t.me/BotFather](https://t.me/BotFather)
2. 发送指令 `/newbot`
3. 选择**显示名称**（例如“Hermes Agent”）——该名称可自定义
4. 选择**用户名**——必须唯一且以`bot`结尾（例如`my_hermes_bot`）
5. BotFather会回复您的**API令牌**，其格式如下：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请妥善保管您的机器人令牌，切勿泄露。任何拥有该令牌的人都能控制您的机器人。如果令牌被泄露，请立即通过 BotFather 中的 `/revoke` 命令将其撤销。
:::

## 第 2 步：自定义您的机器人（可选）

这些 BotFather 命令可用于提升用户体验。只需向 @BotFather 发送消息并使用以下命令：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始与机器人聊天前显示的“此机器人能做什么？”说明文字 |
| `/setabouttext` | 机器人个人资料页面上的简短介绍文字 |
| `/setuserpic` | 为机器人上传头像 |
| `/setcommands` | 定义命令菜单（即聊天界面中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否能够查看所有群组消息（详见第 3 步） |

:::tip
对于 `/setcommands` 命令，以下是一组实用的初始命令：

```
help - Show help information
new - Start a new conversation
sethome - Set this chat as the home channel
```
:::

### 在线/离线状态指示器（可选）

Telegram 机器人并不具备真正的在线/离线状态点——那个绿色圆点其实是*用户账户*的功能，并非 Bot API 为机器人提供的功能。最接近的体现方式便是机器人的**简短描述**（即机器人资料页中其名称下方的那行文字）。

启用 `status_indicator` 后，当网关连接成功时，Hermes 会将该简短描述设置为**在线**；而在正常关闭时则设置为**离线**状态。

```yaml
gateway:
  platforms:
    telegram:
      extra:
        status_indicator: true
        # Optional custom strings (defaults: "Online" / "Offline"):
        status_online: "🟢 Online"
        status_offline: "🔴 Offline"
```

备注：

- 简短描述为机器人的**全局**属性（所有用户均可查看），而非针对单次对话。用户会在机器人的个人资料页面看到该描述，而不会显示在正在进行的对话中的实时徽章中。
- 仅当通过**正常方式**关闭网关（使用 `/stop` 或 `disconnect` 命令）时，才会显示“离线”状态。若发生程序崩溃，则会保留最后已知的状态——这正是个人资料文本指示器所固有的局限性。
- 该功能默认处于关闭状态，因为它会修改机器人的全局个人资料。

### 命令菜单的优先级与数量限制（可选）

当 Telegram 网关启动时，Hermes 会自动注册其命令菜单。该菜单由中央的斜杠命令注册表以及符合条件的插件/技能命令构成，随后会对命令数量进行限制，以确保 Telegram 能稳定接收相关数据。默认限制为 60 个命令——这一数量足以显示所有内置命令以及常见的技能命令。

如果您有希望始终显示在 Telegram 的 `/` 命令选择器中的本地命令或插件命令，可在 `~/.hermes/config.yaml` 文件中对它们设置优先级：

```yaml
platforms:
  telegram:
    extra:
      command_menu:
        max_commands: 60
        priority_mode: prepend  # prepend | append | replace
        priority:
          - my_plugin_command
```

`priority_mode` 用于控制您的命令列表与 Hermes 内置优先级列表的结合方式：

- `prepend`：先将您的命令置于最前面，再接 Hermes 的默认顺序
- `append`：先显示 Hermes 的默认顺序，随后才是您的命令
- `replace`：完全使用您的列表来决定优先级顺序

Telegram 允许最多配置 100 个 BotCommands，但过大的命令负载可能会导致功能异常。为确保稳定性，Hermes 默认设置为 60 个，并会将用户设置的数值限制在 `1..100` 范围内；如需查看完整的命令列表，请使用 `/commands` 命令。

## 第 3 步：隐私模式（群组中使用时至关重要）

Telegram 机器人默认开启**隐私模式**。这正是人们在群组中使用机器人时最容易产生困惑的原因。

**当隐私模式开启时**，您的机器人仅能查看：
- 以 `/` 命令开头的消息
- 直接回复给机器人自身消息的内容
- 服务类消息（如成员加入/离开、置顶消息等）
- 机器人具有管理员权限的频道中的消息

**当隐私模式关闭时**，机器人将接收群组中的所有消息。

### 如何关闭隐私模式

1. 给 **@BotFather** 发送消息
2. 输入 `/mybots` 命令
3. 选择您的机器人
4. 进入 **Bot Settings → Group Privacy → Turn off** 进行设置

:::warning
更改隐私设置后，**必须将机器人从相关群组中移除后再重新添加**。Telegram 会缓存机器人加入群组时的隐私状态，只有将其移除并重新添加后，状态才会更新。
:::

:::tip
另一种替代方案是将机器人提升为**群组管理员**。管理员机器人无论隐私模式如何设置，始终能够接收所有消息，这样就不必手动切换全局隐私模式了。
:::

### 查看群组聊天内容而不自动回复

对于类似 OpenClaw/Yuanbao 的群组交互模式，可配置 Telegram 使机器人能够**查看**普通群组消息，但仅在**直接被触发**时才进行回复：

```yaml
telegram:
  allowed_chats:
    - "-1001234567890"
  group_allowed_chats:
    - "-1001234567890"
  require_mention: true
  observe_unmentioned_group_messages: true
```

启用此模式后，来自明确允许列表中的聊天窗口/主题的未提及群组消息会被作为观察到的上下文附加到共享聊天窗口/主题的会话记录中，但不会触发智能体响应。`allowed_chats`用于限定机器人响应的聊天窗口；而`group_allowed_chats`则负责授权用作观察上下文的共享群组会话，因此在此模式下需使用相同的聊天窗口ID。后续在该允许列表中的聊天窗口/主题中出现对`@botname`的提及、对机器人的回复，或符合预设提及模式的消息，均可利用这些已观察到的上下文。被触发的消息还会被标记上`[nickname|user_id]`，并且会收到每轮对话的安全提示，这样模型就会将之前的内容视为上下文，而非针对机器人的指令。

对应的环境变量：

```bash
TELEGRAM_ALLOWED_CHATS=-1001234567890
TELEGRAM_GROUP_ALLOWED_CHATS=-1001234567890
TELEGRAM_OBSERVE_UNMENTIONED_GROUP_MESSAGES=true
```

这需要 Telegram 将普通群组消息发送至网关，因此请按照上述说明关闭 BotFather 的隐私模式，或将该机器人提升为群组管理员。

## 第 4 步：查找您的用户 ID

Hermes Agent 使用 Telegram 的数字型用户 ID 来控制访问权限。您的用户 ID **并非**用户名，而是一个类似 `123456789` 的数字。

**方法 1（推荐）：** 给 [@userinfobot](https://t.me/userinfobot) 发送消息——它会立即回复您的用户 ID。

**方法 2：** 给 [@get_id_bot](https://t.me/get_id_bot) 发送消息——这也是一个可靠的选择。

请将此数字保存下来，下一步操作会需要它。

## 第 5 步：配置 Hermes

### 方案 A：交互式设置（推荐）

```bash
hermes gateway setup
```

在提示时选择**Telegram**。向导会询问您的机器人令牌以及允许的用户 ID，随后会为您生成相应的配置文件。

### 方案 B：手动配置

在 `~/.hermes/.env` 文件中添加以下内容：

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_ALLOWED_USERS=123456789    # Comma-separated for multiple users
```

### 启动网关

```bash
hermes gateway
```

该机器人应在几秒钟内上线。你可以通过 Telegram 向其发送消息来进行验证。

## 从基于 Docker 的终端发送生成的文件

如果你的终端后端是 `docker`，请注意：Telegram 附件是由**网关进程**发送的，而非直接从容器内部发送。这意味着最终的 `MEDIA:/...` 路径必须在运行网关的主机上可读。

常见误区：

- 智能体在 Docker 容器内将文件写入 `/workspace/report.txt`
- 模型输出 `MEDIA:/workspace/report.txt`
- 由于 `/workspace/report.txt` 仅存在于容器内而非主机上，导致 Telegram 无法成功发送文件

推荐做法：

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/.hermes/cache/documents:/output"
```

接着：

- 将 Docker 内部的文件写入 `/output/...` 目录；
- 在 `MEDIA:` 中指定**主机可访问的路径**，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`

如果您已有 `docker_volumes:` 部分，请将新的挂载项添加到同一列表中。YAML 中重复的键会自动覆盖之前的值。

### 支持的 `MEDIA:` 文件扩展名

网关会从智能体的回复中提取 `MEDIA:/path/to/file` 标签，并将对应的文件作为平台原生附件发送。所有网关平台均支持的扩展名如下：

| 类别 | 扩展名 |
|---|---|
| 图片 | `png`, `jpg`, `jpeg`, `gif`, `webp`, `bmp`, `tiff`, `svg` |
| 音频 | `mp3`, `wav`, `ogg`, `m4a`, `opus`, `flac`, `aac` |
| 视频 | `mp4`, `mov`, `webm`, `mkv`, `avi` |
| **文档** | `pdf`, `txt`, `md`, `csv`, `json`, `xml`, `html`, `yaml`, `yml`, `log` |
| **办公文件** | `docx`, `xlsx`, `pptx`, `odt`, `ods`, `odp` |
| **压缩文件** | `zip`, `rar`, `7z`, `tar`, `gz`, `bz2` |
| **书籍/软件包** | `epub`, `apk`, `ipa` |

上述列表中的文件类型在支持的原生附件平台（如 Telegram、Discord、Signal、Slack、WhatsApp、飞书、Matrix 等）上会以原生格式发送；而在不支持的原生附件的平台上，则会以链接或纯文本形式呈现。**加粗**的类别是在最近几版中新增的——如果您之前依赖智能体直接说明“文件位于：/path/to/report.docx”，请改为使用 `MEDIA:/path/to/report.docx` 即可实现原生附件发送。

## Webhook 模式

默认情况下，Hermes 通过**长轮询**方式连接到 Telegram——即网关会向 Telegram 的服务器发起请求以获取最新更新。这种方式非常适合本地部署及始终在线的服务器环境。

对于**云平台部署**（如 Fly.io、Railway、Render 等），**Webhook 模式**更具成本效益。这些平台能够通过接收入站 HTTP 流量自动唤醒处于暂停状态的服务器，但无法通过出站连接实现唤醒。由于轮询属于出站操作，因此基于轮询的机器人永远无法进入休眠状态。而 Webhook 模式则改变了数据传输方向——Telegram 会将更新推送到您的机器人 HTTPS 地址，从而实现空闲时自动休眠的部署方式。

| | 轮询（默认） | Webhook |
|---|---|---|
| 数据流向 | 网关 → Telegram（出站） | Telegram → 网关（入站） |
| 最佳适用场景 | 本地服务器、始终在线服务器 | 具有自动唤醒功能的云平台 |
| 配置要求 | 无需额外配置 | 需设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲状态成本 | 服务器必须保持运行状态 | 服务器可在消息间隔期间进入休眠状态 |

### 配置方法

请在 `~/.hermes/.env` 文件中添加以下内容：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
TELEGRAM_WEBHOOK_SECRET="$(openssl rand -hex 32)"  # required
# TELEGRAM_WEBHOOK_PORT=8443        # optional, default 8443
```

| 变量 | 是否必填 | 描述 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 用于发送更新信息的公共 HTTPS 地址。该地址的路径会自动提取（例如上文中的 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | **是**（当设置了 `TELEGRAM_WEBHOOK_URL` 时） | Telegram 会在每次 webhook 请求中附带此密钥以进行验证。若未提供此密钥，网关将无法启动——详情请参阅 [GHSA-3vpc-7q5r-276h](https://github.com/NousResearch/hermes-agent/security/advisories/GHSA-3vpc-7q5r-276h)。可通过 `openssl rand -hex 32` 命令生成该密钥。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | webhook 服务器监听的本地端口（默认值为 `8443`）。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关将启动 HTTP webhook 服务器而非采用轮询模式。若未设置该参数，则仍会使用轮询模式——其行为与之前的版本保持一致。

### Cloud部署示例（Fly.io）

1. 将这些环境变量添加到您的 Fly.io 应用密钥中：

```bash
fly secrets set TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
fly secrets set TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)
```

2. 在您的 `fly.toml` 文件中配置 webhook 端口：

```toml
[[services]]
  internal_port = 8443
  protocol = "tcp"

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

3. 部署：

```bash
fly deploy
```

网关日志应显示如下内容：`[telegram] 已连接到 Telegram（Webhook 模式）`。

## 代理支持

如果 Telegram 的 API 被屏蔽，或者您需要通过代理来传输流量，请设置专用于 Telegram 的代理地址。该设置会优先于通用的 `HTTPS_PROXY` / `HTTP_PROXY` 环境变量。

**方案 1：config.yaml（推荐）**

```yaml
telegram:
  proxy_url: "socks5://127.0.0.1:1080"
```

**选项 2：环境变量**

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:1080
```

支持的协议类型包括：`http://`、`https://` 和 `socks5://`。

该代理设置同时适用于 Telegram 的主连接以及备用 IP 传输方式。如果未指定针对 Telegram 的专用代理，网关将自动回退至 `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` 设置（或 macOS 系统的自动代理检测功能）。

## 主频道

您可以在任意 Telegram 聊天窗口（私信或群组）中使用 `/sethome` 命令将其指定为**主频道**。定时任务（cron 作业）会将执行结果发送到该频道。

您也可以在 `~/.hermes/.env` 文件中手动进行设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="My Notes"
```

:::提示
群聊的 ID 为负数（例如 `-1001234567890`）。您的个人私信聊天 ID 即为您的用户 ID。
:::

### 主题模式下的定时消息发送

如果在机器人的私信功能中启用了主题模式，那么发送到根聊天的定时消息将会出现在仅系统可使用的大厅中——在那里回复不会打开任何会话，同时还会出现“主聊天窗口专用于系统指令”的提示。建议您创建一个专门的论坛主题（例如 `Cron`），并进行相应设置：

```bash
TELEGRAM_CRON_THREAD_ID=<topic_thread_id>
```

`TELEGRAM_CRON_THREAD_ID` 仅在定时发送任务中会覆盖 `TELEGRAM_HOME_CHANNEL_THREAD_ID` 的值。在该主题下发送的回复将延续该主题现有的对话会话。

## 语音消息

### 接收的语音（语音转文本）

您在 Telegram 中发送的语音消息会由 Hermes 预置的 STT 服务自动转录为文本，并插入到对话中。

- `local` 模式使用运行 Hermes 的机器上的 `faster-whisper` 工具——无需 API 密钥
- `groq` 模式使用 Groq Whisper 工具，需要提供 `GROQ_API_KEY`
- `openai` 模式使用 OpenAI Whisper 工具，需要提供 `VOICE_TOOLS_OPENAI_KEY`

#### 跳过 STT 转录：将原始音频文件直接传递给智能体

如果您希望由**智能体本身**处理音频内容——例如进行语音分段、使用自定义转录工具，或仅用于存储录音——可在 `~/.hermes/config.yaml` 文件中设置 `stt.enabled: false`：

```yaml
stt:
  enabled: false
```

在禁用语音转文字功能的情况下，网关仍会将语音/音频附件下载到Hermes的音频缓存中，但**不会对其进行转录**。智能体接收到的消息会附带如下标记：

```
[The user sent a voice message: /home/<user>/.hermes/cache/audio/<hash>.ogg]
```

您的工具或技能可以直接读取该路径中的文件（例如，将其传递给本地的语音分割流程、更强大的转录模型，或上传至长期存储中）。文件扩展名反映了Telegram原本提供的格式（语音笔记为`.ogg`，音频附件则为`.mp3`/`.m4a`等）。

这一功能与下方的[本地Bot API服务器](#large-files-20mb-via-local-bot-api-server)部分相辅相成，后者可将Telegram 20MB的文件获取限制提升至2GB——对于长度超过几分钟的录音来说非常实用。

### 输出语音（文本转语音）

当智能体通过文本转语音功能生成音频时，它会以Telegram原生的**语音气泡**形式呈现——即那种圆形的、可直接在线播放的格式。

- **OpenAI和ElevenLabs**可直接输出Opus格式音频，无需额外设置。
- **Edge TTS**（默认的免费服务提供商）输出MP3格式，需要使用**ffmpeg**工具将其转换为Opus格式：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

若未安装 ffmpeg，Edge TTS 生成的音频将以普通音频文件的形式发送（仍可播放，但会使用矩形播放器而非语音气泡）。

您可以在 `config.yaml` 文件的 `tts.provider` 键下配置 TTS 提供商。

## 通过本地 Bot API 服务器处理大文件（>20MB）

Telegram 的**公共**Bot API 对 `getFile` 下载大小的限制为**20 MB**，因此任何超过此大小的语音备忘录、音频文件、视频或文档都会被 Hermes 以“文件过大”的回复 silently 拒绝。解决此问题的官方方法是运行一个**本地**的 [telegram-bot-api](https://github.com/tdlib/telegram-bot-api) 守护进程——即与 Telegram 使用相同的服务器软件，但运行在您的本地网络中。本地服务器可将文件大小上限提升至**2 GB**，而当 Hermes 检测到配置了自定义的 `base_url` 时，它也会自动取消自身的内部限制。

这样一来，便可实现以下工作流：

- 将较长的语音备忘录（如45分钟的会议记录、播客）发送给机器人
- 上传大尺寸视频以便视觉工具进行处理
- 存档原始音频，用于离线处理流程，如语音转写、对齐或训练数据准备

### 步骤 1：获取 Telegram API 凭证

由于本地服务器直接与 Telegram 的 MTProto 层通信（而非公共 Bot API），因此需要**MTProto 凭证**：

1. 访问 [my.telegram.org/apps](https://my.telegram.org/apps)，使用您的 Telegram 账户登录。
2. 创建一个新的应用（任意名称和简短描述即可）。
3. 复制 `api_id` 和 `api_hash`——两者都是必需的。

### 步骤 2：运行 telegram-bot-api 服务器

社区维护的 [`aiogram/telegram-bot-api`](https://hub.docker.com/r/aiogram/telegram-bot-api) Docker 镜像是最简便的方案。可以使用一个简化的 `docker-compose.yaml` 文件（通过使用 `--local` 模式即可启用更高的限制）：

```yaml
services:
  tg-bot-api:
    image: aiogram/telegram-bot-api:latest
    container_name: tg-bot-api
    restart: unless-stopped
    ports:
      - "127.0.0.1:8081:8081"   # bind to loopback only; see security note
    environment:
      TELEGRAM_API_ID: "12345"           # your api_id from Step 1
      TELEGRAM_API_HASH: "abcdef..."     # your api_hash from Step 1
      TELEGRAM_LOCAL: "1"                # enable --local mode (raises 20MB → 2GB)
    volumes:
      - ./tg-bot-api-data:/var/lib/telegram-bot-api
```

启动它：

```bash
docker compose up -d tg-bot-api
docker logs --tail 20 tg-bot-api
```

:::warning 安全提示
本地 Bot API 服务器会直接在 URL 路径中接收您的机器人令牌（例如 `/bot<TOKEN>/getMe**，且无需额外身份验证**）。任何能够访问该端口的人都可以完全控制您的机器人——读取其可见的所有消息、以机器人的身份发送消息等。请将容器绑定到 `127.0.0.1`，和/或在私有网络中通过反向代理来保护它。**切勿将 8081 端口暴露在公共互联网上。**
:::

### 第 3 步：将机器人从公共 API 注销（仅执行一次）
一个机器人同一时间只能在**一个** Bot API 服务器上运行。如果您的机器人此前已经在 `api.telegram.org` 上运行（几乎可以肯定如此），则必须在本地服务器允许其接入之前，先在该公共服务器上将其显式注销：

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/logOut"
# expected response: {"ok":true,"result":true}
```

这是一个一次性迁移步骤——无需在每次重启时重复执行。此后，Telegram 会通过新服务器来传递在 `logOut` 之后收到的所有消息。

请验证本地服务器能够代表该机器人与 Telegram 进行通信：

```bash
curl "http://127.0.0.1:8081/bot<YOUR_BOT_TOKEN>/getMe"
# expected response: {"ok":true,"result":{"id":...,"is_bot":true,...}}
```

### 第 4 步：将 Hermes 指向本地服务器

在 `~/.hermes/config.yaml` 文件的 `platforms.telegram.extra` 下添加相应 URL：

```yaml
platforms:
  telegram:
    extra:
      base_url: "http://127.0.0.1:8081/bot"
      base_file_url: "http://127.0.0.1:8081/file/bot"
      local_mode: true        # see Step 5 below — only set this if the bot's data
                              # directory is readable by the Hermes process
```

:::警告 请使用 `platforms.telegram.extra`，而非 `telegram.extra`  
目前仅 `platforms.<name>.extra` 这种格式会被深度合并到平台配置中。直接置于顶层 `telegram.extra` 块下的键值将会被忽略，不会产生任何影响。  
:::

当设置了 `base_url` 后，Hermes 会：  
- 根据本地服务器环境构建 python-telegram-bot 客户端；  
- 自动将内部文档/音频的尺寸上限从 20 MB 提高至 2 GB；  
- 在“文件过大”的错误信息中显示当前的有效限制值（如 `Maximum: 2048 MB.`），以便您清楚知晓当前所处的模式。  

请重启网关，并查看相关的确认日志信息：

```bash
hermes gateway restart
grep -E "Using custom Telegram base_url|Using Telegram local_mode" ~/.hermes/logs/gateway.log | tail
```

### 第5步：`local_mode`——磁盘文件访问

本地服务器提供文件的方式有两种：

1. **不使用`--local`参数**（默认方式）：文件通过HTTP协议在 `/file/bot<TOKEN>/<path>` 路径下提供，与公共Bot API的机制相同。20MB的限制依然存在。这种方式仅适用于网络故障时的临时解决方案（例如当`api.telegram.org`无法访问但可以自行托管服务器时），并不适合用于提升文件上传大小。

2. **使用`--local`参数**（通过设置`TELEGRAM_LOCAL=1`实现）：文件会被直接写入服务器的文件系统，此时`getFile`接口返回的将是**绝对路径**而非HTTP URL，20MB的限制也随之取消。Hermes需要从磁盘直接读取这些文件，而非通过HTTP传输。

要使磁盘读取方式正常工作，需在配置中设置`local_mode: true`，同时确保Hermes进程有权读取服务器返回的路径。具体分为两种场景：

- **同一台机器**：telegram-bot-api与Hermes运行在同一台主机上。需将数据目录挂载到Hermes可读取的路径下（例如`/var/lib/telegram-bot-api`），并确保文件所有权一致。容器会将其权限降至内部的`telegram-bot-api`用户（不同镜像的UID可能不同）；最简单的解决方法是 在compose服务中添加`user: "<UID>:<GID>"`参数，使文件由Hermes当前运行的用户所有。

- **不同机器**：Bot服务器运行在某台主机上（如NAS或独立虚拟机），而Hermes则运行在另一台主机上。此时需以服务器报告的**相同绝对路径**（通常为`/var/lib/telegram-bot-api`）在两台机器之间共享数据目录。NFS是不错的选择；如果不想处理文件系统层面的UID不一致问题，使用带有`uid=`参数映射的CIFS/SMB协议也会更便捷。

如果设置了`local_mode: true`，但Hermes无法读取返回的文件路径（可能是权限问题或挂载错误），python-telegram-bot会自动回退到通过HTTP向本地服务器发起`getFile`请求——而在`--local`模式下，本地服务器会返回`404 Not Found`错误。相关错误信息会显示在`gateway.log`日志中：

```
[Telegram] Failed to cache voice: Not Found
telegram.error.InvalidToken: Not Found
```

如果出现这种情况，说明文件上传功能正常，但文件共享功能却存在问题。请以网关运行的用户身份，在Hermes主机上执行 `ls -la /var/lib/telegram-bot-api/<TOKEN>/voice/` 命令，确认其中有一个文件能够通过 `cat` 命令读取且不会出现权限错误。

### 第6步：进行测试

向该机器人发送大小超过20 MB的语音笔记或音频文件。同时查看网关的日志记录：

```bash
tail -f ~/.hermes/logs/gateway.log | grep -iE "telegram|cache"
```

您应该会看到类似 `[Telegram] Cached user voice at /home/<user>/.hermes/cache/audio/...` 的记录，而不会出现“文件过大”的拒绝提示。结合上文中的 `stt.enabled: false` 设置，原始音频文件的路径将会被包含在代理的接收消息中，以便后续处理。

## 群聊使用场景

Hermes Agent 在 Telegram 群聊中也可使用，但需注意以下几点：

- **隐私模式**决定了机器人能够查看哪些消息（详见[步骤 3](#step-3-privacy-mode-critical-for-groups)）
- `TELEGRAM_ALLOWED_USERS` 规则依然有效——即便在群聊中，也只有经过授权的用户才能触发该机器人
- 可通过设置 `telegram.require_mention: true` 阻止机器人对普通的群聊内容作出响应
- 当 `telegram.require_mention: true` 已启用时，以下类型的群消息才会被接收：
  - 对机器人发送的某条消息的回复
  - 包含 `@botusername` 提及的内容
  - 使用 `/command@botusername` 格式发送的命令（即包含机器人名称的 Telegram 机器人菜单命令）
  - 符合在 `telegram.mention_patterns` 中配置的正则表达式唤醒词的内容
- 在包含多个 Hermes 机器人的群聊中，`telegram.exclusive_bot_mentions` 能确保消息路由的确定性。当有消息明确提及一个或多个 Telegram 机器人用户名时，只有被提及的机器人会处理该消息；其他 Hermes 机器人会在尝试回复或触发唤醒词机制之前忽略该消息。此功能默认处于启用状态。
- 可使用 `telegram.ignored_threads` 设置，让 Hermes 在特定的 Telegram 论坛主题中保持沉默，即便群聊允许自由回复或通过提及来触发响应
- 如果未设置 `telegram.require_mention` 或其值为 false，Hermes 将保持原有的群聊处理方式，对它能够看到的普通群消息作出响应

### 单个群聊中的多个 Hermes 机器人

如果您要在同一个 Telegram 群聊中运行多个 Hermes 实例，应为每个实例创建一个独立的 Telegram 机器人令牌，并为每个实例启动一个网关。切勿在多个运行的网关中重复使用同一个机器人令牌，否则 Telegram 会拒绝针对同一令牌的并发请求。

推荐的群聊配置：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns: []
```

通过此设置，像`@research_bot @ops_bot summarize this`这样的群组消息将仅由`research_bot`和`ops_bot`处理。群组中的其他Hermes机器人将保持沉默，即便该消息是对它们之前发送的某条消息的回复，或符合共享唤醒词的条件也不例外。

仅在对旧版群组而言，若不希望显式提及的指令覆盖回复及唤醒词触发机制时，才应将`exclusive_bot_mentions`设置为`false`。

如需同时使用多个配置文件，请为每个配置文件运行一次网关命令。例如：

```bash
# default profile
hermes gateway start
hermes gateway status
hermes gateway stop

# named profiles
hermes -p research gateway start
hermes -p research gateway status
hermes -p research gateway stop
```

对于规模较小的固定机器人集群，可使用 shell 循环或脚本：针对默认配置文件调用 `hermes gateway <action>`，而对于每个自定义配置文件则分别调用 `hermes -p <profile> gateway <action>`。这种方式比假设单个进程级命令能控制每个服务管理器上的所有自定义配置文件更为可靠。

### 故障排查：在私聊中正常工作但在群组中无响应

如果机器人能在私聊中回复，但在群组中却保持沉默，请按顺序检查以下环节：

1. **Telegram 消息传递问题**：关闭 BotFather 的隐私模式，将机器人提升为群组管理员，或直接@提及该机器人。如果 Telegram 从未将消息传递给机器人，Hermes 就无法对其作出响应。
2. **修改隐私设置后的重新加入问题**：在更改 BotFather 的隐私设置后，先将机器人从群组中移除，然后再重新添加。Telegram 可能会对已存在的群组成员关系保留旧的消息传递方式。
3. **Hermes 权限配置问题**：确保发送者已被列入 `TELEGRAM_ALLOWED_USERS` 或 `TELEGRAM_GROUP_ALLOWED_USERS` 列表，或者通过 `TELEGRAM_GROUP_ALLOWED_CHATS` 允许该群组聊天。
4. **@提及过滤规则问题**：如果设置了 `telegram.require_mention: true`，那么除非消息为斜杠命令、对机器人的回复、`@botusername` 形式的@提及，或符合已配置的 `mention_patterns` 规则，否则普通的群组聊天将被忽略。
5. **多机器人路由问题**：如果一个群组中包含多个机器人，请确保每个 Hermes 配置文件使用唯一的机器人令牌，并保持 `exclusive_bot_mentions` 开启状态，除非你刻意希望使用旧的共享触发机制。

在 Telegram 群组及超级群组中，出现负数的聊天 ID 是正常现象。如果使用基于聊天范围的授权机制，应将这些 ID 放入 `TELEGRAM_GROUP_ALLOWED_CHATS` 中，而非发送者用户白名单中。

### 群组触发配置示例

将以下内容添加到 `~/.hermes/config.yaml` 文件中：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns:
    - "^\\s*chompy\\b"
  ignored_threads:
    - 31
    - "42"
```

该示例支持所有常规的直接触发方式，以及以 `chompy` 开头的消息，即便这些消息未使用 `@mention` 标签。在执行提及检测和自由回复检测之前，Telegram 中主题为 `31` 和 `42` 的消息始终会被忽略。

### 关于 `mention_patterns` 的说明

- 模式规则基于 Python 正则表达式
- 匹配时不区分大小写
- 模式规则会同时应用于文本消息和媒体文件的字幕
- 无效的正则表达式会被忽略，仅在网关日志中留下警告，而不会导致机器人崩溃
- 若希望某模式仅能在消息开头匹配，可使用 `^` 进行定位

## 私聊主题（Bot API 9.4）

Telegram Bot API 9.4（2026年2月版本）引入了**私聊主题**功能——机器人无需创建超级群组，即可在一对一的私聊中直接创建类似论坛的主题讨论串。借助此功能，您可以在现有的私聊中使用 Hermes 创建多个相互隔离的工作空间。

### 应用场景

如果您同时处理多个长期项目，主题功能有助于保持各项目的独立上下文：

- **“网站”主题**——用于开发生产环境中的Web服务
- **“研究”主题**——用于文献综述和论文探索
- **“综合”主题**——用于处理各类杂项任务及快速提问

每个主题都有独立的对话会话、历史记录和上下文，与其他主题完全隔离。

### 配置方法

:::caution 先决条件
在配置文件中添加主题功能之前，用户必须先在与机器人的私聊中**开启主题模式**：

1. 打开 Telegram 中与 Hermes 机器人的私聊
2. 点击聊天顶部的机器人名称以查看聊天信息
3. 启用 **Topics** 功能（即切换为论坛模式）

若未完成此步骤，Hermes 在启动时会记录“该聊天并非论坛”并跳过主题创建流程。这是 Telegram 客户端端的设置——机器人无法通过编程方式启用该功能。
:::

在 `~/.hermes/config.yaml` 文件的 `platforms.telegram.extra.dm_topics` 下添加相应主题即可：

```yaml
platforms:
  telegram:
    extra:
      dm_topics:
      - chat_id: 123456789        # Your Telegram user ID
        topics:
        - name: General
          icon_color: 7322096
        - name: Website
          icon_color: 9367192
        - name: Research
          icon_color: 16766590
          skill: arxiv              # Auto-load a skill in this topic
```

**字段：**

| 字段 | 是否必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 主题显示名称 |
| `icon_color` | 否 | Telegram 图标颜色代码（整数） |
| `icon_custom_emoji_id` | 否 | 主题图标的自定义表情符号 ID |
| `skill` | 否 | 在该主题的新会话中自动加载的技能 |
| `thread_id` | 否 | 创建主题后会自动填充，无需手动设置 |

### 工作原理

1. 当网关启动时，Hermes 会为所有尚未设置 `thread_id` 的主题调用 `createForumTopic` 接口。
2. `thread_id` 会自动保存到 `config.yaml` 文件中，后续重启时将跳过该 API 调用。
3. 每个主题对应一个独立的会话密钥：`agent:main:telegram:dm:{chat_id}:{thread_id}`。
4. 每个主题内的消息拥有独立的对话历史、内存清理机制以及上下文窗口。

### 根级私信处理

默认情况下，发送到根级私信（即不在任何主题内的私信）会按常规方式处理。如需将根级私信视为大厅，则可设置 `ignore_root_dm: true` —— 对于已配置了主题私信的用户，普通消息将被静默忽略，而系统命令（如 `/start`、`/help`、`/status` 等）仍可正常使用。

```yaml
platforms:
  telegram:
    extra:
      ignore_root_dm: true
      dm_topics:
        - chat_id: 123456789
          topics:
            - name: General
```

该检查是**按聊天会话单独进行的**：只有那些在 `dm_topics` 中至少有一个条目的用户，其主私信才会受到影响；未配置相关主题的用户则不会受到影响。

### 技能绑定

包含 `skill` 字段的主题会在该主题下的新会话开始时自动加载对应的技能。其工作原理与在对话开头输入 `/skill-name` 完全相同——技能内容会被注入到第一条消息中，后续消息也会显示在对话历史中。

例如，一个带有 `skill: arxiv` 的主题，无论是因为空闲超时、每日重置还是手动执行 `/reset` 导致会话重置，都会预先加载 arxiv 技能。

:::提示
通过非配置方式创建的主题（例如手动调用 Telegram API 创建的），会在收到 `forum_topic_created` 服务消息时被自动发现。您也可以在网关运行期间向配置中添加主题——它们会在下一次缓存未命中时被识别。
:::

## 多会话私信模式（`/topic`）

这是一种类似 ChatGPT 的多会话私信功能——一个机器人，多个并行对话。与上文由管理员管理的 `extra.dm_topics` 不同，此模式是**用户驱动的**：无需配置，也不需要预先声明主题名称。最终用户只需通过 `/topic` 启用该功能，然后点击 Telegram 的 **+** 按钮创建任意数量的主题，每个主题都是一个完全独立的 Hermes 会话。

### `/topic` 子命令

| 形式 | 使用场景 | 效果 |
|------|---------|------|
| `/topic` | 主私信，尚未启用 | 检查 BotFather 的功能支持情况，启用多会话模式，并创建一个固定的系统主题 |
| `/topic` | 主私信，已启用 | 显示状态：列出可恢复的未关联会话 |
| `/topic` | 已处于某个主题内 | 显示当前主题的会话绑定信息 |
| `/topic help` | 任意场景 | 显示即时用法说明 |
| `/topic off` | 主私信 | 禁用多会话模式，并清除该聊天的所有主题绑定 |
| `/topic <session-id>` | 已处于某个主题内 | 将之前的 Telegram 会话恢复到当前主题中 |

只有经过授权的用户（通过 `TELEGRAM_ALLOWED_USERS` 或平台认证配置列入白名单的用户）才能使用 `/topic` 命令。未经授权的发送者将收到拒绝响应，而无法启用该功能。

### 私信主题与多会话私信模式的对比

| | `extra.dm_topics`（配置驱动） | `/topic`（用户驱动） |
|---|---|---|
| 启用者 | 管理员，在 `config.yaml` 中配置 | 最终用户，通过发送 `/topic` 命令 |
| 主题列表 | 在配置中预先定义的固定集合 | 用户可自由创建或删除主题 |
| 主题名称 | 由管理员指定 | 由用户自行选择；会自动重命名为与 Hermes 会话标题一致的名称 |
| 主私信行为 | 普通聊天模式（若设置 `ignore_root_dm: true` 则为大厅模式） | 变为系统大厅模式（非命令消息将被拒绝） |
| 主要用途 | 需要可选技能绑定的永久工作空间 | 临时性的并行会话 |
| 数据持久性 | 存储在配置文件中的 `extra.dm_topics` | 存储在 `telegram_dm_topic_mode` 和 `telegram_dm_topic_bindings` SQLite 表中 |

这两种功能可以在同一个机器人上共存——用户可以在私信中使用 `/topic` 创建多会话，而 `extra.dm_topics` 则继续负责管理其他聊天中的管理员定义主题。

### 先决条件

在 **@BotFather** 中打开您的机器人 → **Bot Settings → Threads Settings**：

1. 打开 **Threaded Mode**（这将启用 `has_topics_enabled` 设置）
2. **不要**禁用用户创建主题的功能（保持 `allows_users_to_create_topics` 为开启状态）

当用户首次使用 `/topic` 时，Hermes 会调用 `getMe` 函数来检查这两个设置。如果其中任意一项未开启，Hermes 会发送 BotFather Threads Settings 页面的截图，并说明需要切换哪些选项——在满足先决条件之前，功能不会被激活。

### 激活流程

从主私信中发送：

```
/topic
```

Hermes将执行以下操作：

1. 检查`getMe().has_topics_enabled`和`allows_users_to_create_topics`的值。
2. 若两者均为真，则为该私信开启多会话主题模式。
3. 尽力创建一个用于显示状态/指令的**系统**主题并将其设为固定主题。
4. 回复一份用户可恢复的、之前未关联的Telegram会话列表。

启用后，**根级私信将作为一个大厅**：常规消息请求会被拒绝，并引导用户查看**所有消息**。系统指令（如`/status`、`/sessions`、`/usage`、`/help`等）在根级私信中依然有效。

### 创建新主题（最终用户操作流程）

1. 在Telegram中打开与该机器人的私信。
2. 点击机器人界面顶部的**所有消息**，然后发送任意消息。
3. Telegram会为该消息创建一个新主题。
4. Hermes会在该主题内进行回复——此时该主题即成为一个独立的会话。

每个主题都有独立的对话历史、模型状态、工具执行记录以及会话ID。其隔离标识为`agent:main:telegram:dm:{chat_id}:{thread_id}`，这与通过配置实现的私信主题隔离机制相同。

### 自动重命名主题

在首次交互之后，Hermes会通过自动命名流程为每个主题生成标题，此时Telegram中的主题名称也会随之更改——例如“新主题”会变为“数据库迁移方案”。此功能为尽力而为：若命名失败，系统会记录日志但不会导致会话中断。

如需禁用此功能并保持手动设置的主题名称不变，请进行如下设置：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_topic_auto_rename: true
```

当此标志处于开启状态时，Hermes 仍会生成一个内部会话标题（供 `hermes sessions`、TUI 等工具使用），但不会修改 Telegram 中的主题名称。这在您通过 BotFather 的线程模式手动管理主题，且不希望每次首次回复都覆盖主题标题时非常有用。

### 在主题内使用 `/new` 命令

该命令会重置当前主题的会话（生成新的会话 ID 并清除历史记录），而不会影响其他主题。Hermes 会回复提示您：若需同时处理多项任务，通常应通过 **All Messages** 创建新主题。

### 恢复之前的会话

在某个主题内发送相应指令即可。

```
/topic <session-id>
```

此功能会将当前主题绑定到现有的Hermes会话，而非新建一个会话。这对于继续在开启主题模式之前开始的对话非常有用。相关限制如下：

- 目标会话必须属于同一位Telegram用户
- 目标会话不得已绑定到其他主题

Hermes会通过会话名称进行确认，并回放上一条助手消息以提供上下文信息。

如需查看会话ID，可在主私信中发送 `/topic`（无需参数）——Hermes会列出该用户所有未关联的Telegram会话。

### 在主题内部使用 `/topic`（无需参数）

可显示当前主题的绑定信息：会话名称、会话ID，以及关于使用 `/new` 命令与创建新主题的说明。

### 技术实现原理

- 激活状态会被保存到 `state.db` 文件中的 `telegram_dm_topic_mode(chat_id, user_id, enabled, ...)` 字段中
- 每个主题绑定信息则存储在 `telegram_dm_topic_bindings(chat_id, thread_id, session_id, ...)` 中，且针对 `session_id` 设置了 `ON DELETE CASCADE` 规则——删除某个会话时，其对应的主题绑定也会自动清除
- 主题模式的SQLite数据库迁移为**可选功能**：仅在首次调用 `/topic` 时执行，不会在网关启动时自动运行。只要用户未在该配置文件中运行 `/topic`，`state.db` 文件就不会发生任何变化
- 每条收到的私信都会首先查找对应的 `(chat_id, thread_id)` 绑定信息。如果存在，系统会通过 `SessionStore.switch_session()` 将消息路由到已绑定的会话，从而确保磁盘上会话密钥与会话ID之间的映射关系始终一致
- 在主题内部使用 `/new` 命令时，系统会重写绑定记录，使其指向新的会话ID，这样后续消息就会发送到这个新会话中
- 在 `extra.dm_topics` 中声明的主题**绝不会自动重命名**——即使启用了多会话模式，操作员设定的主题名称也会被保留
- 若想关闭聊天中**所有**主题的自动重命名功能，可设置 `extra.disable_topic_auto_rename: true`，这包括通过线程模式创建的临时主题
- 在支持论坛功能的私信中，处于最顶层的“General”主题会被视为主大厅，无论Telegram是使用 `message_thread_id=1` 还是无需 thread_id 参数来传递消息
- 主大厅的提醒消息有频率限制：每个聊天每30秒最多发送一条。如果用户忘记开启主题模式，却在主大厅输入了十条提示语，也不会收到十条回复
- BotFather设置相关的截图也有发送频率限制：每个聊天每5分钟只能发送一张。在尚未启用线程功能时反复尝试发送 `/topic`，也不会重新上传同一张图片
- 在主题内部使用 `/background <prompt>` 命令时，其结果会返回到同一个主题中；后台会话不会触发所属主题的自动重命名
- `/topic` 命令本身也受到机器人用户权限检查的限制——未经授权的私信请求将会被拒绝，而无法激活主题模式

### 关闭多会话模式

在主私信中发送 `/topic off` 即可。Hermes会将该主题的对应记录置为关闭状态，清除聊天中的 `(thread_id → session_id)` 绑定信息，此时主私信就会恢复为普通的Hermes聊天界面。Telegram中的现有主题不会被删除，只是不再作为独立会话存在。如需重新启用多会话模式，可稍后再次运行 `/topic` 命令。

如果需要手动清理数据（例如在多个聊天中批量重置），可直接删除相应的记录：

```bash
sqlite3 ~/.hermes/state.db \
  "UPDATE telegram_dm_topic_mode SET enabled = 0 WHERE chat_id = '<your_chat_id>'; \
   DELETE FROM telegram_dm_topic_bindings WHERE chat_id = '<your_chat_id>';"
```

### Hermes版本降级

如果您将Hermes降级到不支持 `/topic` 功能的旧版本，该功能将直接失效——`state.db` 中仍会保留 `telegram_dm_topic_mode` 和 `telegram_dm_topic_bindings` 这两个表，但旧版本代码会忽略它们。私信对话将恢复为原有的单线程隔离模式（每个 `message_thread_id` 仍会通过 `build_session_key` 生成独立的会话），因此您现有的Telegram主题功能仍可作为并行会话正常使用。主私信对话框不再具备大厅功能，其中的消息会像以往一样直接进入智能体处理。再次升级后，多会话模式将恢复到原来的状态。

## 群组论坛主题技能绑定

已开启**主题模式**（也称为“论坛主题”）的超级群组本身就已经实现了按主题的会话隔离——每个 `thread_id` 对应独立的对话内容。不过，您可能希望像私信主题技能绑定那样，在特定群组主题中有消息到达时自动加载相应技能。

### 使用场景

一个为不同工作流设置论坛主题的团队超级群组：

- **工程**主题 → 自动加载 `software-development` 技能
- **研究**主题 → 自动加载 `arxiv` 技能
- **综合**主题 → 不加载特定技能，使用通用助手

### 配置方法

在 `~/.hermes/config.yaml` 文件的 `platforms.telegram.extra.group_topics` 下添加主题绑定配置：

```yaml
platforms:
  telegram:
    extra:
      group_topics:
      - chat_id: -1001234567890       # Supergroup ID
        topics:
        - name: Engineering
          thread_id: 5
          skill: software-development
        - name: Research
          thread_id: 12
          skill: arxiv
        - name: General
          thread_id: 1
          # No skill — general purpose
```

**字段：**

| 字段 | 是否必填 | 描述 |
|-------|----------|-------------|
| `chat_id` | 是 | 超级群的数字 ID（以 `-100` 开头的负数） |
| `name` | 否 | 该主题的易读标签（仅用于参考） |
| `thread_id` | 是 | Telegram 论坛主题的 ID，可在 `t.me/c/<group_id>/<thread_id>` 链接中查看 |
| `skill` | 否 | 在该主题的新会话中自动加载的技能 |

### 工作原理

1. 当有消息进入已映射的群组主题时，Hermes 会在 `group_topics` 配置中查找对应的 `chat_id` 和 `thread_id`。
2. 如果匹配项包含 `skill` 字段，则该技能会自动加载到当前会话中——这与私信主题的技能绑定方式相同。
3. 不包含 `skill` 键的主题仅具备会话隔离功能（保持原有行为，无变化）。
4. 未映射的 `thread_id` 或 `chat_id` 值将静默忽略——既不会报错，也不会加载任何技能。

### 与私信主题的区别

| | 私信主题 | 群组主题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 主题创建 | 若缺少 `thread_id`，Hermes 会通过 API 创建主题 | 由管理员在 Telegram 用户界面中创建主题 |
| `thread_id` | 创建后会自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（外观由管理员控制） |
| 技能绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛主题已内置此功能） |

:::tip
要查找某个主题的 `thread_id`，可在 Telegram Web 或桌面端打开该主题，查看其 URL：`https://t.me/c/1234567890/5`——最后的数字（`5`）即为 `thread_id`。超级群的 `chat_id` 是在群组 ID 前加上 `-100` 得到的（例如群组 `1234567890` 的 `chat_id` 为 `-1001234567890`）。
:::

## 最新的 Bot API 功能

- **Bot API 9.4（2026 年 2 月）：** 私信主题——机器人可通过 `createForumTopic` 在一对一私信中创建论坛主题。Hermes 将其用于两项不同功能：由管理员精选的[私信主题](#private-chat-topics-bot-api-94)（通过配置确定，主题列表固定），以及由用户主导的[多会话私信模式](#multi-session-dm-mode-topic)（通过 `/topic` 激活，用户可创建无限数量的主题）。
- **隐私政策：** Telegram 现在要求机器人必须拥有隐私政策。可通过 BotFather 使用 `/setprivacy_policy` 设置隐私政策，否则 Telegram 可能会自动生成占位文本。如果您的机器人面向公众，这一点尤为重要。
- **Bot API 9.5（2026 年 3 月）：** 通过 `sendMessageDraft` 实现原生流式发送功能。Hermes 支持 Telegram 的原生流式草稿 API，可作为私信的可选传输方式。由于在某些 Telegram 客户端上草稿预览可能会出现折叠和重新渲染的情况，因此默认仍使用传统的 `editMessageText` 方式。

### 流式传输（`gateway.streaming.transport`）

当启用流式发送功能（`gateway.streaming.enabled: true`）时，Hermes 会从四种传输方式中选择一种：

| 值 | 行为 |
|---|---|
| `auto`（默认值） | 在支持的聊天类型（目前为 Telegram 私信）上使用原生草稿流式发送；其他类型则使用传统的编辑模式。如果草稿帧发送失败，会平滑降级处理。 |
| `draft` | 强制使用原生草稿模式。如果聊天类型不支持草稿（如群组/主题），则会记录降级信息并回退到编辑模式。 |
| `edit` | 对所有聊天类型都使用传统的逐次调用 `editMessageText` 的轮询方式。 |
| `off` | 完全禁用流式发送（仅发送最终回复，无渐进式更新）。 |

在 `~/.hermes/config.yaml` 中配置：

```yaml
gateway:
  streaming:
    enabled: true
    transport: auto    # auto | draft | edit | off
```

**使用 `edit`（默认值）在私信中显示的效果**——网关会先发送一条普通预览消息，随后通过 `editMessageText` 功能逐步更新该内容，从而避免出现 Telegram 中草稿预览被折叠或回滚的问题。

**使用 `auto` 或 `draft` 在私信中显示的效果**——Telegram 会展示一个逐字符更新的动画式草稿预览。当回复完成后，它会以普通消息的形式发送，而客户端上的草稿预览也会自动消失。由于草稿没有消息 ID，因此最终的内容才会保留在聊天记录中。

**群组、超级群组和论坛主题怎么办？** Telegram 仅允许在私信中使用 `sendMessageDraft` 功能。对于其他类型的聊天场景，网关会自动采用基于编辑的方案——用户体验与之前保持一致。

**如果草稿预览出现故障会怎样？** 无论是因为短暂的网络错误、服务器端拒绝响应，还是 Python-telegram-bot 版本过旧导致的故障，系统都会自动将后续的回复切换为基于编辑的方案。下一次回复将会重新尝试发送。

## 渲染：富文本消息、表格及链接预览

**富文本消息（Bot API 10.1）**。对于那些包含传统 MarkdownV2 方案无法处理的元素——如表格、任务列表、可折叠的 `<details>` 标签以及数学公式——系统会使用 Telegram 原生的 [`sendRichMessage`](https://core.telegram.org/bots/api#sendrichmessage) 函数，结合代理端的**原始 Markdown 格式**进行发送，从而实现原生渲染，无需在客户端进行格式简化。在流式回复过程中，最终内容是通过 `editMessageText` 的 `rich_message` 参数对现有预览进行直接编辑来生成的——不会生成第二条消息，也不会删除原有内容，因此不会出现轮次结束时的重复发送现象。在私信中，实时流式预览同样使用 `sendRichMessageDraft`，这样动画式的草稿预览就能与最终的富文本消息保持一致。而普通回复（纯文本、加粗/斜体文字、简单列表）则仍采用 MarkdownV2 方案，以确保在不同客户端上字体大小和间距的一致性。

当内容超过 32,768 字符的富文本限制时，系统会自动跳过富文本渲染路径；如果遇到 Telegram 端的拒绝响应（如旧版 Python-telegram-bot 不支持相应接口、解析错误、块或列尺寸过大等），系统也会**无缝切换**回 MarkdownV2 方案——您的消息绝不会丢失。不过，短暂的网络错误不会被自动重发（不会出现重复的最终消息）。

**MarkdownV2 作为备用方案**。当某条消息无法使用富文本渲染路径时，Hermes 会将该 Markdown 内容转换为 MarkdownV2 格式。由于 MarkdownV2 不支持原生表格语法，因此管道式表格会被转换为标准格式：

- **小型表格**会被拆分成**行组项目符号列表**——每行内容都会变成列标题下的可读项目符号列表，适用于 2–4 列且单元格内容较短的表格。
- **较大或较宽的表格**则会转换为带有对齐列的**代码块格式**，从而避免内容被折叠。

富文本消息是**可选功能**。默认情况下仍使用传统的 MarkdownV2 方案，因为目前的 Telegram 客户端往往难以将 Bot API 生成的富文本消息复制为纯文本，这对于命令片段和在移动设备间传递信息尤为不便。如需实现表格、任务列表、详细内容及数学公式的原生渲染效果：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        rich_messages: true
        rich_drafts: false
```

此设置旨在确保客户端渲染与内容复制功能的兼容性；当 Telegram 拒绝处理富格式 API 调用时，Hermes 会自动回退到默认模式。`rich_drafts` 用于控制 Telegram 私信流式传输过程中实验性的富格式草稿预览功能，默认处于关闭状态，因为 Telegram Desktop/macOS 能够在聊天界面重新绘制之前，直接在上方显示富格式草稿内容。如果您希望在启用富格式消息的同时仍保持传统的“始终以代码块形式显示表格”的行为，可在 `config.yaml` 中将 `telegram.pretty_tables` 设置为 `false` 以禁用表格格式化功能（默认值为 `true`）。

**链接预览。** Telegram 会自动为机器人消息中的网址生成链接预览。如果您希望关闭此功能（避免出现过长的 `/tools` 输出、避免智能体回复中列出大量链接等情况），可进行相应设置：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_link_previews: true
```

启用该功能后，Hermes 会在每条发送的消息中添加 Telegram 的 `LinkPreviewOptions(is_disabled=True)` 参数；而对于较旧版本的 `python-telegram-bot`，则会回退使用传统的 `disable_web_page_preview` 参数。

## 群组白名单设置

Telegram 群组和论坛聊天室提供两种相互独立的配置选项：

- **发送者用户 ID**（`group_allow_from` / `TELEGRAM_GROUP_ALLOWED_USERS`）—— 用于限制发送者范围的白名单，仅适用于群组/论坛内的消息。当您希望特定用户能够在群组中调用机器人，而又不想将其添加到 `TELEGRAM_ALLOWED_USERS` 中（因为那样也会赋予他们私信权限）时，可使用此选项。
- **聊天 ID**（`group_allowed_chats` / `TELEGRAM_GROUP_ALLOWED_CHATS`）—— 用于限制聊天室范围的白名单。属于这些群组/论坛的任何成员均可以与该机器人交互。对于以群组成员身份作为访问权限依据的团队/客服机器人而言，此功能非常实用。

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # Global access (DMs + groups). Users here can always invoke the bot.
        allow_from:
          - "123456789"
        # Sender IDs allowed in groups/forums only. Does NOT grant DM access.
        group_allow_from:
          - "987654321"
        # Entire groups/forums — any member is authorized.
        group_allowed_chats:
          - "-1001234567890"
```

对应的环境变量：

```bash
TELEGRAM_ALLOWED_USERS="123456789"
TELEGRAM_GROUP_ALLOWED_USERS="987654321"
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

行为规则：

- `TELEGRAM_ALLOWED_USERS` 适用于所有类型的聊天（私信、群组、论坛）。
- `TELEGRAM_GROUP_ALLOWED_USERS` 仅允许列表中的发送者在群组/论坛中发送消息；除非其也被列入 `TELEGRAM_ALLOWED_USERS`，否则仍无法向该机器人发送私信。
- 若聊天被添加到 `TELEGRAM_GROUP_ALLOWED_CHATS` 中，则无论发送者是谁，该聊天的所有成员均被允许参与。
- 在上述任意参数中使用 `*` 即可允许任何发送者或任何聊天。
- 该机制会在现有的提及/模式触发规则以及 `group_topics` 和 `ignored_threads` 设置之上运行。

### 从 PR #17686 之前的版本迁移说明

在功能分离之前，仅存在 `TELEGRAM_GROUP_ALLOWED_USERS` 这一参数，用户需在其中输入**聊天 ID**。为保持向后兼容性，`TELEGRAM_GROUP_ALLOWED_USERS` 中以 `-` 开头的值仍会被视为聊天 ID，并仅会记录一次弃用警告。迁移方式如下：

```bash
# Old (still works, but deprecated)
TELEGRAM_GROUP_ALLOWED_USERS="-1001234567890"

# New
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

### 允许访客被@提及（`guest_mode`）

在常规配置中，`group_allowed_chats`起着严格的过滤作用：即使有成员明确@提及该机器人，来自列表之外群组的消息也会被直接忽略。这对于客服或团队专用机器人而言，确实是合适的默认设置。

对于较为随意的使用场景——比如朋友间的群聊，你希望机器人**大部分时间保持沉默**，但**在收到明确召唤时再作出响应**——可以启用`guest_mode`功能：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        group_allowed_chats:
          - "-1001234567890"   # your main allowlisted group
        guest_mode: true       # non-allowlisted groups: allow on @mention only
```

环境等效配置：

```bash
TELEGRAM_GUEST_MODE=true
```

默认值为 `false`。

当设置 `guest_mode: true` 时，只有来自未列入白名单群组的消息在**明确@提及该机器人**的情况下才会被处理。且每一轮对话都必须有提及动作——访客互动不具备会话持续性，因此若未被主动触发，机器人绝不会自动参与朋友群组中的讨论。

私信及已列入白名单的群组将保持与以往完全一致的行为模式。

## 斜杠命令访问控制

默认情况下，所有获准使用的用户均可运行所有斜杠命令。若希望将白名单用户分为**管理员**（拥有完整斜杠命令权限）和**普通用户**（仅能使用您明确启用的命令），可在平台的 `extra` 块中添加 `allow_admin_from` 和 `user_allowed_commands` 参数：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        # Existing allowlists (unchanged)
        allow_from:
          - "123456789"     # admin
          - "555555555"     # regular user
          - "777777777"     # regular user

        # NEW — admins get all slash commands (built-in + plugin)
        allow_admin_from:
          - "123456789"

        # NEW — non-admin allowed users can only run these slash commands.
        # /help and /whoami are always allowed so users can see their access.
        user_allowed_commands:
          - status
          - model
          - history

        # Optional: separate admin/command lists for groups
        group_allow_admin_from:
          - "123456789"
        group_user_allowed_commands:
          - status
```

**行为规则：**

- 对于某个作用域（私信或群组），若用户被列入 `allow_admin_from` 列表，则可通过实时注册表运行**所有**已注册的斜杠命令——包括内置命令以及通过插件注册的命令。
- 若用户仅被列入 `allow_from` 列表而**未**列入 `allow_admin_from` 列表，则只能运行 `user_allowed_commands` 中指定的命令，此外还可以使用始终允许的命令 `/help` 和 `/whoami`。
- 普通聊天内容（非斜杠格式的消息）不受影响。非管理员用户仍可正常与智能体交流，只是无法触发任意命令。
- **向后兼容性**：若某个作用域未设置 `allow_admin_from`，则该作用域的斜杠命令限制功能将被禁用。现有安装无需任何更改即可继续正常工作。
- 私信中的管理员身份并不等同于群组中的管理员身份。每个作用域都有独立的管理员列表。
- 若仅设置了 `group_allow_admin_from`，则私信作用域将保持无限制（向后兼容）模式。

您可以使用 `/whoami` 命令查看当前所处的作用域、您的权限等级（管理员/用户/无限制），以及您可以运行的斜杠命令列表。

## 交互式模型选择器

在 Telegram 聊天中发送不带参数的 `/model` 命令时，Hermes 会显示一个交互式内联键盘，用于切换模型：

1. **提供商选择**——显示所有可用提供商的按钮，并标注对应模型的数量（例如：“OpenAI（15）”，当前所选提供商则为“✓ Anthropic（12）”）。
2. **模型选择**——提供分页的模型列表，支持使用 **上一页**/**下一页** 进行导航，还有 **返回** 按钮可回到提供商选择界面，以及 **取消** 按钮。

当前选定的模型和提供商会显示在页面顶部。所有导航操作均通过直接编辑同一条消息来完成，不会造成聊天界面混乱。

:::提示
如果您已知确切的模型名称，可以直接输入 `/model <名称>` 跳过选择器。您还可以使用 `/model <名称> --global` 选项，使该选择在多次会话之间保持不变。
:::

## DNS-over-HTTPS 备用 IP 地址

在某些受限网络环境中，`api.telegram.org` 可能会解析为无法访问的 IP 地址。Telegram 适配器配备了**备用 IP**机制，能够透明地尝试连接其他备用 IP，同时保留正确的 TLS 主机名和 SNI 信息。

### 工作原理

1. 若已设置 `TELEGRAM_FALLBACK_IPS`，则直接使用该列表中的 IP 地址。
2. 否则，适配器会通过 DNS-over-HTTPS（DoH）自动查询**Google DNS**和**Cloudflare DNS**，以获取 `api.telegram.org` 的其他可用 IP 地址。
3. 通过 DoH 查询得到的、与系统 DNS 查询结果不同的 IP 地址将被用作备用地址。
4. 若 DoH 也被屏蔽，则会作为最后手段使用一个硬编码的备用 IP（`149.154.167.220`）。
5. 一旦某个备用 IP 地址连接成功，它就会变为“固定选项”——后续请求将直接使用该地址，而无需再尝试主路径。

### 配置方式

```bash
# Explicit fallback IPs (comma-separated)
TELEGRAM_FALLBACK_IPS=149.154.167.220,149.154.167.221
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
platforms:
  telegram:
    extra:
      fallback_ips:
        - "149.154.167.220"
```

:::提示
通常无需手动配置此选项。通过 DoH 实现的自动发现功能已能应对大多数网络受限的场景。只有当您的网络也阻断了 DoH 时，才需要使用 `TELEGRAM_FALLBACK_IPS` 环境变量。
:::

## 代理支持

如果您的网络需要通过 HTTP 代理才能访问互联网（在企业环境中较为常见），Telegram 适配器会自动读取标准的代理环境变量，并将所有连接路由至该代理。

### 支持的变量

适配器会按顺序检查这些环境变量，优先使用已设置的第一个变量：

1. `HTTPS_PROXY`
2. `HTTP_PROXY`
3. `ALL_PROXY`
4. `https_proxy` / `http_proxy` / `all_proxy`（小写形式）

### 配置方法

在启动网关之前，请先在您的环境中设置代理信息：

```bash
export HTTPS_PROXY=http://proxy.example.com:8080
hermes gateway
```

或者将其添加到 `~/.hermes/.env` 文件中：

```bash
HTTPS_PROXY=http://proxy.example.com:8080
```

该代理设置同时适用于主传输方式以及所有备用 IP 传输方式。无需额外的 Hermes 配置——只要设置了环境变量，系统便会自动使用它。

:::note
此处所述为 Hermes 用于连接 Telegram 的自定义备用传输层。而在其他场景中使用的标准 `httpx` 客户端本身就已能够原生支持代理环境变量。
:::

## 消息反应功能

机器人可以通过添加表情符号反应作为视觉反馈，来指示消息的处理状态：

- 👀 表示机器人已开始处理您的消息
- ✅ 表示响应已成功发送
- ❌ 表示处理过程中出现了错误

反应功能**默认处于关闭状态**。如需启用该功能，请在 `config.yaml` 中进行配置：

```yaml
telegram:
  reactions: true
```

或者通过环境变量设置：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（其反应效果是叠加的）不同，Telegram 的 Bot API 会在单次调用中一次性替换所有机器人反应。从 👀 到 ✅/❌ 的切换是原子级完成的——您不会同时看到这两种状态。
:::

:::tip
如果机器人没有在群组中添加反应的权限，相关调用会静默失败，消息处理仍会正常继续。
:::

## 每个频道的提示语

可为特定的 Telegram 群组或论坛主题设置临时的系统提示语。该提示语会在每次对话轮次运行时被注入——绝不会保存到对话记录中——因此更改会立即生效。

```yaml
telegram:
  channel_prompts:
    "-1001234567890": |
      You are a research assistant. Focus on academic sources,
      citations, and concise synthesis.
    "42":  |
      This topic is for creative writing feedback. Be warm and
      constructive.
```

键值为聊天 ID（群组/超级群组）或论坛主题 ID。对于论坛群组，主题级别的提示会覆盖群组级别的提示：

- 在群组 `-1001234567890` 中的主题 `42` 发送的消息 → 采用主题 `42` 的提示
- 在主题 `99` 中发送的消息（未指定特定主题）→ 回退到群组 `-1001234567890` 的提示
- 在没有指定主题的群组中发送的消息 → 不适用任何频道提示

数值型的 YAML 键值会自动转换为字符串。

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 机器人完全无响应 | 确认 `TELEGRAM_BOT_TOKEN` 的值正确。检查 `hermes gateway` 的日志以查找错误信息。 |
| 机器人回复“未授权” | 您的用户名不在 `TELEGRAM_ALLOWED_USERS` 列表中。建议使用 @userinfobot 工具再次确认。 |
| 机器人忽略群组内的消息 | 可能开启了隐私模式。请关闭该模式（参见第 3 步），或将机器人设为群组管理员。**更改隐私设置后，请务必将机器人移除后再重新添加。** |
| 语音消息无法转录 | 确认已启用语音转文字功能：可选择安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 文件中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复以文件形式显示而非对话气泡 | 需要安装 `ffmpeg`（用于 Edge TTS Opus 格式转换）。 |
| 机器人令牌已被撤销或无效 | 通过 BotFather 的 `/revoke`、/newbot` 或 /token 命令生成新令牌，然后更新您的 `.env` 文件。 |
| Webhook 无法接收更新 | 确认 `TELEGRAM_WEBHOOK_URL` 是可公开访问的（可使用 `curl` 进行测试）。确保您的平台或反向代理能够将来自该 URL 端口的 HTTPS 流量路由到 `TELEGRAM_WEBHOOK_PORT` 所配置的本地监听端口（两者无需为相同数值）。同时要确保 SSL/TLS 加密已启用——Telegram 仅向 HTTPS 地址发送数据。还需检查防火墙规则。 |

## 执行审批

当机器人试图执行可能具有危险性的命令时，它会在聊天中请求您的批准：

> ⚠️ 此命令可能存在风险（递归删除操作）。如需批准，请回复“yes”。

您可以回复“yes”/“y”表示批准，或回复“no”/“n”表示拒绝。

## 交互式提示（明确需求）

当机器人调用 `clarify` 工具——例如询问您更倾向哪种方案、收集任务完成后的反馈，或在做出重要决策前征求意见时——Telegram 会通过**内嵌键盘按钮**来呈现问题：

> ❓ 我应该使用哪种框架来构建控制面板？
>
> [1. Next.js] [2. Remix] [3. Astro]
> [✏️ 其他（直接输入答案）]

点击按钮即可回答，或选择“其他”以输入自由文本形式的回复（您发送的下一条消息将作为答案）。对于没有预设选项的开放式 `clarify` 调用，则不会显示按钮，直接等待您的下一条消息。

您可以通过 `~/.hermes/config.yaml` 文件中的 `agent.clarify_timeout` 参数来设置响应超时时间（默认为 600 秒）。如果您在超时时间内未作出回应，机器人会发送一条提示信息以解除阻塞，并继续执行后续操作，而不会一直等待。

## 推送通知频率

每当机器人发送消息时，Telegram 都会触发一次推送通知。对于那些会持续输出工具处理进度、流式更新及状态回调的长时间对话，这种方式很快就会造成通知过多。Telegram 适配器提供了两种通知模式：

| 模式 | 行为表现 |
|------|----------|
| `important`（默认值） | 仅**最终回复**、**审批请求**以及**斜杠命令确认信息**会触发推送通知。工具处理进度、流式数据块及状态消息则会以 `disable_notification=true` 的设置发送，不会产生推送。 |
| `all` | 机器人发出的每一条消息都会触发推送通知。这是旧有的行为模式；仅当您确实希望随时了解每一次工具调用时才建议启用此模式。 |

您可以在 `~/.hermes/config.yaml` 文件中配置该选项：

```yaml
display:
  platforms:
    telegram:
      notifications: important   # or "all"
```

环境变量覆盖功能（便于快速进行 A/B 测试）：

```bash
HERMES_TELEGRAM_NOTIFICATIONS=all
```

当遇到未知值时，系统会记录警告信息，并将其默认视为“重要”级别。

## 在原位置编辑状态消息

Telegram适配器通过`send_or_update_status()`函数来处理那些重复出现的智能体状态回调消息（例如“正在压缩上下文……”、“正在调用工具……”）。该函数会维护一个 `{(chat_id, status_key) → message_id}` 的缓存机制，因此在后续触发时直接**编辑现有的消息气泡**，而无需每次都添加新消息。不同的`status_key`值会对应独立的消息，不同聊天窗口之间的消息也绝不会发生冲突。如果编辑失败（比如用户已删除该消息，或消息年龄已超过Telegram允许的编辑时限），则该缓存条目会被移除，下一次触发时系统会发送一条新的消息并重新缓存其ID。此功能无需任何配置——这正是Telegram的默认行为。那些未实现`send_or_update_status`功能的适配器则会直接使用原始的`send()`函数，不会进行任何修改。

## 在智能体处理消息期间固定用户发送的消息

当用户发送的消息触发智能体开始处理时，Telegram适配器会将该消息固定显示，直到处理完成才会将其解固定。这是一种简单的视觉提示，表明机器人正在积极处理该消息，而非忽略它。为避免额外的通知推送，此固定功能使用了`disable_notification=true`参数。同样，此功能也不需要任何配置。

## 安全性

:::warning
务必设置`TELEGRAM_ALLOWED_USERS`参数，以限制能够与您的机器人交互的用户范围。作为安全措施，若未设置该参数，网关将默认拒绝所有用户的访问。
:::

切勿公开分享您的机器人令牌。一旦令牌被盗用，请立即通过BotFather的 `/revoke` 命令将其撤销。

如需了解更多详细信息，请参阅[安全性文档](/user-guide/security)。您还可以采用[私信配对功能](/user-guide/messaging#dm-pairing-alternative-to-allowlists)，以实现更为动态的用户授权方式。
