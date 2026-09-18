---
sidebar_position: 1
title: "Telegram"
description: "Set up Hermes Agent as a Telegram bot"
---

# Telegram集成设置

Hermes Agent以功能完备的对话型机器人的形式与Telegram集成。一旦完成连接，您便可以在任何设备上与智能体进行聊天，发送会被自动转录的语音备忘录，接收定时任务的结果，还能在群组聊天中使用该智能体。此集成基于[python-telegram-bot](https://python-telegram-bot.org/)构建，支持文本、语音、图片及文件附件的交互。

## 第1步：通过BotFather创建机器人

每个Telegram机器人都需要由Telegram官方的机器人管理工具[@BotFather](https://t.me/BotFather)颁发的API令牌。

1. 打开Telegram并搜索**@BotFather**，或直接访问[t.me/BotFather](https://t.me/BotFather)
2. 发送命令 `/newbot`
3. 选择一个**显示名称**（例如“Hermes Agent”）——内容可任意设置
4. 选择一个**用户名**——该名称必须唯一且以`bot`结尾（例如`my_hermes_bot`）
5. BotFather会回复您的**API令牌**，其格式如下：

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

:::warning
请妥善保管您的机器人令牌，切勿泄露。任何掌握该令牌的人都能控制您的机器人。如果令牌被泄露，请立即通过 BotFather 中的 `/revoke` 命令撤销它。
:::

## 第 2 步：自定义您的机器人（可选）

这些 BotFather 命令有助于提升用户体验。您可以发送消息联系 @BotFather，然后使用以下命令：

| 命令 | 用途 |
|---------|---------|
| `/setdescription` | 用户开始与机器人聊天前显示的“此机器人能做什么？”说明文字 |
| `/setabouttext` | 机器人个人资料页面上的简短描述文字 |
| `/setuserpic` | 为机器人上传头像 |
| `/setcommands` | 定义命令菜单（即聊天界面中的 `/` 按钮） |
| `/setprivacy` | 控制机器人是否能够查看所有群组消息（详见第 3 步） |

:::tip
对于 `/setcommands`，以下是一组实用的初始命令：

```
help - Show help information
new - Start a new conversation
sethome - Set this chat as the home channel
```
:::

### 在线/离线状态指示器（可选）

Telegram 机器人并没有真正的在线/离线状态点——那个绿色圆点其实是*用户账户*的功能，并非 Bot API 为机器人提供的功能。最接近的体现方式是机器人的**简短描述**（即机器人资料页中其名称下方的那行文字）。

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

- 简短描述是对整个机器人**全局**生效的（所有用户均可查看），而非针对单次聊天。用户会在机器人的个人资料页面看到该描述，而不会显示在正在进行的聊天窗口中的实时徽章上。
- 只有通过**正常**方式关闭网关（如使用 `/stop`、`disconnect` 命令）才会将状态设置为“离线”。若发生强制崩溃，则会保留最后已知的状态——这也是个人资料文本指示器固有的局限性。
- 该功能默认处于关闭状态，因为它会修改机器人的全局个人资料。

### 命令菜单的优先级与数量限制（可选）

当 Telegram 网关启动时，Hermes 会自动注册其命令菜单。该菜单由中央的斜杠命令注册表以及符合条件的插件/技能命令构成，随后会对命令数量进行限制，以确保 Telegram 能稳定接收相关数据。默认的限制为 60 个命令——这一数量足以让所有内置命令及常用的技能命令都显示在 Telegram 的 `/` 命令选择器中。

如果您有希望始终显示在 Telegram `/` 命令选择器中的技能命令、插件命令或内置命令，可在 `~/.hermes/config.yaml` 文件中对它们设置优先级：

```yaml
platforms:
  telegram:
    extra:
      command_menu:
        max_commands: 60
        priority_mode: prepend  # prepend | append | replace
        priority:
          - my_plugin_command
          - songsee          # skill commands work here too
```

`priority_mode` 用于控制您的命令列表与 Hermes 内置优先级列表的结合方式：

- `prepend`：先将您的命令置于最前，再显示 Hermes 的默认命令
- `append`：先显示 Hermes 的默认命令，随后再展示您的命令
- `replace`：完全使用您的列表来决定命令的优先级顺序

优先级会在应用数量上限之前，先作用于**合并后的**候选列表（包括核心命令、插件命令以及技能命令）——因此，即便仅核心命令就已占满菜单空间，具有高优先级的技能命令仍能确保拥有对应的菜单位置。此前，技能命令总是会首先按字母顺序被筛选掉，因此无论设置何种 `priority`，排在字母表后面的技能命令都永远无法显示。

Telegram 允许最多配置 100 个 BotCommands，但过大的命令负载可能会导致功能异常。为保证稳定性，Hermes 默认设置为 60 个，并会将用户配置的值限制在 `1..100` 范围内；如需查看完整的命令列表，请使用 `/commands` 命令。

### 内嵌命令选择器：可搜索所有命令（无数量上限）

虽然 `/` 菜单存在数量限制，但 Telegram 的**内嵌模式**却没有此限制。启用该模式后，在任意聊天窗口中输入 `@yourbotname` 后跟上搜索词，即可获得一个实时可搜索的选择器，涵盖**所有** Hermes 命令及已安装的技能——系统会随着每次按键实时生成结果并分页显示，因此绝不会遗漏任何命令。

```
@yourbotname plan            → tap the /plan result to send it
@yourbotname plan migrate auth to OIDC   → sends /plan migrate auth to OIDC
@yourbotname pdf             → finds skills matching "pdf" by name or description
```

第一个单词用于筛选功能目录，其后的所有内容将作为参数被包含在发送的命令中。点击某项结果后，该命令会以普通消息的形式由你发出，从而通过标准命令路径进行处理（即使处于隐私模式，以命令前缀开头的消息仍能送达机器人）。

**一次性设置：** 所有 Telegram 机器人默认均处于非内联模式。你可以在 [@BotFather](https://t.me/BotFather) 中使用 `/setinline` 命令来启用该功能（选择你的机器人，设定任意占位文本，例如“搜索命令和技能...”）。在此之前，Telegram 不会传递内联查询，相应的选择器也将处于无响应状态。

仅允许通过你设置的网关白名单的用户查看结果——未经授权的用户将收到空列表，这样你的技能目录就不会暴露给陌生人（即使机器人未加入的聊天窗口，也可以发送内联查询）。

## 第 3 步：隐私模式（对群组尤为重要）

Telegram 机器人具备**默认已开启的隐私模式**。这正是人们在群组中使用机器人时最容易产生困惑的原因。

**当隐私模式开启时**，你的机器人仅能看到：
- 以 `/` 命令开头的消息
- 直接回复到机器人自身消息的内容
- 服务消息（如成员加入/离开、已固定消息等）
- 机器人具有管理员权限的频道中的消息

**当隐私模式关闭时**，机器人会接收群组中的所有消息。

### 如何关闭隐私模式

1. 给 **@BotFather** 发送消息
2. 发送 `/mybots` 命令
3. 选择你的机器人
4. 进入 **机器人设置 → 群组隐私 → 关闭**
:::warning
更改隐私设置后，**必须将该机器人从任意群组中移除后再重新添加**。Telegram 会在机器人加入群组时缓存其隐私状态，只有将其移除并重新添加后，该状态才会更新。
:::

:::tip
另一种无需关闭隐私模式的方法是将机器人提升为**群组管理员**。管理员机器人无论群组的隐私设置如何，始终能够接收所有消息，从而无需切换全局隐私模式。
:::

### 观看群组聊天而不自动回复

对于类似 OpenClaw/Yuanbao 的群组行为，可配置 Telegram 使机器人能够**查看**普通群组消息，但仅在**直接收到触发消息时**才进行回复：

```yaml
telegram:
  allowed_chats:
    - "-1001234567890"
  group_allowed_chats:
    - "-1001234567890"
  require_mention: true
  observe_unmentioned_group_messages: true
```

启用此模式后，来自明确允许列表中的聊天频道/主题的未提及群组消息会作为已观察到的上下文被添加到共享聊天频道/主题的对话记录中，但不会触发智能体响应。`allowed_chats`用于限定机器人回应的范围；而`group_allowed_chats`则负责授权用于生成已观察上下文的共享群组对话，因此在此模式下需使用相同的聊天ID。后续在该允许列表内的聊天频道/主题中提及`@botname`、回复机器人，或按照配置的提及模式发送消息时，均可利用这些已观察到的上下文。被触发的消息还会被标记上`[nickname|user_id]`，并且会收到每轮对话的安全提示，从而确保模型将之前的内容视为上下文，而非针对机器人的指令。

对应的环境变量：

```bash
TELEGRAM_ALLOWED_CHATS=-1001234567890
TELEGRAM_GROUP_ALLOWED_CHATS=-1001234567890
TELEGRAM_OBSERVE_UNMENTIONED_GROUP_MESSAGES=true
```

这需要 Telegram 将普通群组消息发送至网关，因此请按照上述说明关闭 BotFather 的隐私模式，或将该机器人提升为群组管理员。

## 第 4 步：获取您的用户 ID

Hermes Agent 使用 Telegram 的数字型用户 ID 来控制访问权限。您的用户 ID **并非**用户名，而是一个类似 `123456789` 的数字。

**方法 1（推荐）：** 给 [@userinfobot](https://t.me/userinfobot) 发送消息——它会立即回复您的用户 ID。

**方法 2：** 给 [@get_id_bot](https://t.me/get_id_bot) 发送消息——这也是一个可靠的选择。

请将此数字保存下来，后续步骤中将需要它。

## 第 5 步：配置 Hermes

### 方案 A：交互式设置（推荐）

```bash
hermes gateway setup
```

出现提示时请选择**Telegram**。向导会询问您的机器人令牌及允许的用户 ID，随后会为您生成配置文件。

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

该机器人应在几秒钟内上线。你可以通过 Telegram 向其发送消息进行验证。

## 从基于 Docker 的终端发送生成的文件

如果你的终端后端是 `docker`，请注意 Telegram 附件是由**网关进程**发送的，而非直接从容器内部发送。这意味着最终的 `MEDIA:/...` 路径必须在运行网关的主机上可读。

常见隐患：

- 智能体在 Docker 容器内将文件写入 `/workspace/report.txt`
- 模型输出 `MEDIA:/workspace/report.txt` 作为文件路径
- 由于 `/workspace/report.txt` 仅存在于容器中而不存在于主机上，导致 Telegram 无法成功传输文件

推荐的处理方式：

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/.hermes/cache/documents:/output"
```

接下来：

- 将 Docker 内部的文件写入 `/output/...` 目录；
- 在 `MEDIA:` 中指定**主机可访问的路径**，例如：
  `MEDIA:/home/user/.hermes/cache/documents/report.txt`

如果您已有 `docker_volumes:` 部分，请将新的挂载项添加到同一列表中。YAML 中重复的键会自动覆盖之前的值。

### 支持的 `MEDIA:` 文件扩展名

网关会从代理的回复中提取 `MEDIA:/path/to/file` 格式的标签，并将对应的文件作为平台原生的附件发送。所有网关平台均支持的扩展名如下：

| 类别 | 扩展名 |
|---|---|
| 图片 | `png`, `jpg`, `jpeg`, `gif`, `webp`, `bmp`, `tiff`, `svg` |
| 音频 | `mp3`, `wav`, `ogg`, `m4a`, `opus`, `flac`, `aac` |
| 视频 | `mp4`, `mov`, `webm`, `mkv`, `avi` |
| **文档** | `pdf`, `txt`, `md`, `csv`, `json`, `xml`, `html`, `yaml`, `yml`, `log` |
| **办公文件** | `docx`, `xlsx`, `pptx`, `odt`, `ods`, `odp` |
| **压缩文件** | `zip`, `rar`, `7z`, `tar`, `gz`, `bz2` |
| **电子书/软件包** | `epub`, `apk`, `ipa` |

对于支持该功能的平台（如 Telegram、Discord、Signal、Slack、WhatsApp、飞书、Matrix 等），列表中的任何文件都会以原生附件形式发送；而在不支持的原生附件功能的平台上，则会转换为链接或纯文本形式显示。**加粗**的类别是在最近几版中新增的——如果您之前依赖模型直接输出“文件位于：/path/to/report.docx”的提示，建议改为使用 `MEDIA:/path/to/report.docx` 以实现原生附件发送。

## Webhook 模式

默认情况下，Hermes 通过**长轮询**方式与 Telegram 连接——即网关会向 Telegram 的服务器发送请求以获取最新更新。这种方式非常适合本地部署以及需要持续运行的场景。

对于**云平台部署**（如 Fly.io、Railway、Render 等），**Webhook 模式**更具成本效益。这些平台能够通过接收入站 HTTP 请求来自动唤醒处于暂停状态的机器，但无法响应出站连接。由于轮询属于出站操作，因此基于轮询的机器人永远无法进入休眠状态。而 Webhook 模式则改变了数据传输方向——Telegram 会直接将更新推送到机器人的 HTTPS 地址，从而实现空闲时自动休眠的功能。

| | 轮询（默认） | Webhook |
|---|---|---|
| 数据流向 | 网关 → Telegram（出站） | Telegram → 网关（入站） |
| 最佳适用场景 | 本地服务器、需持续运行的服务 | 具有自动唤醒功能的云平台 |
| 配置要求 | 无需额外配置 | 设置 `TELEGRAM_WEBHOOK_URL` |
| 空闲状态成本 | 机器必须保持运行状态 | 机器可在消息间隔期间进入休眠 |

### 配置方法

请在 `~/.hermes/.env` 文件中添加以下内容：

```bash
TELEGRAM_WEBHOOK_URL=https://my-app.fly.dev/telegram
TELEGRAM_WEBHOOK_SECRET="$(openssl rand -hex 32)"  # required
# TELEGRAM_WEBHOOK_PORT=8443        # optional, default 8443
```

| 变量 | 是否必填 | 描述 |
|----------|----------|-------------|
| `TELEGRAM_WEBHOOK_URL` | 是 | Telegram 用于发送更新的公共 HTTPS 地址。该地址的路径会自动提取（例如上述示例中的 `/telegram`）。 |
| `TELEGRAM_WEBHOOK_SECRET` | **是**（当设置了 `TELEGRAM_WEBHOOK_URL` 时） | Telegram 会在每个 webhook 请求中附带的密钥，用于验证身份。若未设置此值，网关将无法启动——详情请参阅 [GHSA-3vpc-7q5r-276h](https://github.com/NousResearch/hermes-agent/security/advisories/GHSA-3vpc-7q5r-276h)。可通过 `openssl rand -hex 32` 命令生成该密钥。 |
| `TELEGRAM_WEBHOOK_PORT` | 否 | webhook 服务器监听的本地端口（默认值为 `8443`）。 |

当设置了 `TELEGRAM_WEBHOOK_URL` 时，网关将启动 HTTP webhook 服务器而非采用轮询模式。若未设置该值，则仍会使用轮询模式——其行为与之前的版本保持一致。

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

如果 Telegram 的 API 被屏蔽，或者您需要通过代理来传输流量，请设置专用于 Telegram 的代理网址。该设置会优先于通用的 `HTTPS_PROXY` / `HTTP_PROXY` 环境变量。

**方式一：config.yaml（推荐）**

```yaml
telegram:
  proxy_url: "socks5://127.0.0.1:1080"
```

**选项 2：环境变量**

```bash
TELEGRAM_PROXY=socks5://127.0.0.1:1080
```

支持的协议地址为：`http://`、`https://`、`socks5://`。

该代理设置同时适用于Telegram的主连接以及备用IP传输方式。若未指定针对Telegram的专用代理，则网关会回退至`HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY`（或macOS系统的自动代理检测功能）。

如果您的主机上备用IP检测路径出现故障，可设置`HERMES_TELEGRAM_DISABLE_FALLBACK_IPS=true`，以保持通过直接访问`api.telegram.org`路径的冷连接方式。您还可以通过`HERMES_TELEGRAM_FALLBACK_DISCOVERY_TIMEOUT`（单位：秒）来设定DNS-over-HTTPS备用地址检测的超时时间，默认值为`5`秒。

## 主频道

在任意Telegram聊天窗口（私信或群组）中使用 `/sethome` 命令，即可将其指定为**主频道**。定时任务（cron作业）会将执行结果发送至该频道。

您也可以在`~/.hermes/.env`文件中手动进行设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="My Notes"
```

:::提示
群聊的 ID 为负数（例如 `-1001234567890`）。您的个人私信聊天 ID 即为您的用户 ID。
:::

### 在主题模式下的定时消息发送

如果您在机器人的私信功能中启用了主题模式，那么发送到根聊天的定时消息将会出现在仅系统可使用的大厅中——在此回复不会打开任何会话，且您会看到“主聊天频道专用于系统指令”的提示。建议您创建一个专门的论坛主题（例如 `Cron`），并进行相应设置：

```bash
TELEGRAM_CRON_THREAD_ID=<topic_thread_id>
```

`TELEGRAM_CRON_THREAD_ID` 仅在定时发送任务中会覆盖 `TELEGRAM_HOME_CHANNEL_THREAD_ID` 的值。在该主题下发出的回复将延续该主题的现有对话会话。

## 语音消息

### 接收语音（语音转文本）

您在 Telegram 中发送的语音消息会由 Hermes 预置的 STT 服务提供商自动转录，并以文本形式插入对话中。

- `local` 模式使用运行 Hermes 的机器上的 `faster-whisper` 工具——无需 API 密钥
- `groq` 模式使用 Groq Whisper 工具，需要提供 `GROQ_API_KEY`
- `openai` 模式使用 OpenAI Whisper 工具，需要提供 `VOICE_TOOLS_OPENAI_KEY`

#### 跳过 STT 转录：将原始音频文件直接传递给智能体

如果您希望由**智能体本身**处理音频内容——例如进行语音分段、使用自定义转录工具，或仅用于存储录音——可在 `~/.hermes/config.yaml` 文件中设置 `stt.enabled: false`：

```yaml
stt:
  enabled: false
```

在禁用语音转文字功能的情况下，网关仍会将语音/音频附件下载到Hermes的音频缓存中，但**不会对其进行转录**。智能体接收到的消息会带有如下标记：

```
[The user sent a voice message: /home/<user>/.hermes/cache/audio/<hash>.ogg]
```

您的工具或技能可以直接读取该路径中的文件（例如，将其传递给本地的语音分割流程、更强大的转录模型，或上传至长期存储中）。文件扩展名反映了Telegram原本提供的格式（语音备忘录为`.ogg`，音频附件则为`.mp3`/`.m4a`等）。

这一功能与下方的[本地Bot API服务器](#large-files-20mb-via-local-bot-api-server)部分相辅相成，该方案可将Telegram 20MB的文件获取限制提升至2GB——对于时长超过几分钟的录音而言非常实用。

### 输出语音（文本转语音）

当智能体通过文本转语音功能生成音频时，它会以Telegram原生的**语音气泡**形式呈现——即那种圆形的、可直接内嵌播放的格式。

- **OpenAI和ElevenLabs**可直接输出Opus格式音频，无需额外设置。
- **Edge TTS**（默认的免费服务提供商）输出MP3格式，需要借助**ffmpeg**工具将其转换为Opus格式：

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

如果没有安装 ffmpeg，Edge TTS 生成的音频将以普通音频文件的形式发送（仍可播放，但会使用矩形播放器而非语音气泡）。

你需要在 `config.yaml` 文件的 `tts.provider` 键下配置 TTS 提供商。

## 通过本地 Bot API 服务器处理大文件（>20MB）

Telegram 的**公共**Bot API 对 `getFile` 下载的大小限制为**20 MB**，因此任何超过此大小的音频文件、视频或文档都会被 Hermes 直接拒绝，并返回“文件过大”的提示。解决此问题的官方方法是运行一个**本地**的 [telegram-bot-api](https://github.com/tdlib/telegram-bot-api) 守护进程——即使用与 Telegram 相同的服务器软件，但运行在你的本地网络中。本地服务器可将文件大小上限提升至**2 GB**，而当 Hermes 检测到配置了自定义的 `base_url` 时，它也会自动提高自身的内部限制。

这样一来，就可以实现以下工作流程：

- 将较长的语音备忘录（如45分钟的会议记录、播客内容）发送给机器人
- 上传大体积视频以供视觉工具处理
- 存档原始音频，用于离线处理流程，如语音转写、对齐或训练数据准备

### 步骤1：获取 Telegram API 凭证

由于本地服务器会直接与 Telegram 的 MTProto 层通信（而非公共 Bot API），因此需要**MTProto 凭证**：

1. 访问 [my.telegram.org/apps](https://my.telegram.org/apps)，使用你的 Telegram 账户登录。
2. 创建一个新的应用（任意名称和简短描述即可）。
3. 复制 `api_id` 和 `api_hash`——这两个参数都是必需的。

### 步骤2：运行 telegram-bot-api 服务器

由社区维护的 [`aiogram/telegram-bot-api`](https://hub.docker.com/r/aiogram/telegram-bot-api) Docker 镜像是最简便的方案。只需一个简化的 `docker-compose.yaml` 文件（可通过使用 `--local` 模式来提升资源限制）：

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
本地 Bot API 服务器会直接在 URL 路径中接收您的机器人令牌（例如 `/bot<TOKEN>/getMe**，且不进行任何额外身份验证**）。任何能够访问该端口的人都可以完全控制您的机器人——读取其可见的所有消息、以机器人的身份发送消息等等。请将容器绑定到 `127.0.0.1`，和/或在私有网络中通过反向代理来保护它。**切勿将 8081 端口暴露在公共互联网上。**
:::

### 第 3 步：将机器人从公共 API 中登出（一次性操作）

一个机器人同一时间只能在一个 Bot API 服务器上运行。如果您的机器人之前已经在 `api.telegram.org` 上运行（几乎可以肯定如此），则必须在本地服务器接受它之前，先将其从该公共服务器中显式登出：

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/logOut"
# expected response: {"ok":true,"result":true}
```

这是一个一次性迁移步骤——无需在每次重启时重复执行。此后，Telegram 会通过新服务器来传递在 `logOut` 之后收到的所有消息。

请先确认本地服务器能够代表该机器人与 Telegram 进行通信：

```bash
curl "http://127.0.0.1:8081/bot<YOUR_BOT_TOKEN>/getMe"
# expected response: {"ok":true,"result":{"id":...,"is_bot":true,...}}
```

### 第 4 步：将 Hermes 指向本地服务器

在 `~/.hermes/config.yaml` 文件的 `platforms.telegram.extra` 下添加相应的 URL：

```yaml
platforms:
  telegram:
    extra:
      base_url: "http://127.0.0.1:8081/bot"
      base_file_url: "http://127.0.0.1:8081/file/bot"
      local_mode: true        # see Step 5 below — only set this if the bot's data
                              # directory is readable by the Hermes process
```

:::注意 请使用 `platforms.telegram.extra`，而非 `telegram.extra`  
目前仅 `platforms.<name>.extra` 这种格式会被深度合并到平台配置中。直接置于顶层 `telegram.extra` 块下的键值将会被忽略。  
:::

当设置了 `base_url` 后，Hermes 会：  
- 根据本地服务器构建 python-telegram-bot 客户端；  
- 自动将内部文档/音频的大小限制从 20 MB 提高至 2 GB；  
- 在“文件过大”的错误信息中显示当前的限制值（`最大容量：2048 MB。`），以便您清楚了解当前所处的模式。  

请重启网关，并查看相应的确认日志行：

```bash
hermes gateway restart
grep -E "Using custom Telegram base_url|Using Telegram local_mode" ~/.hermes/logs/gateway.log | tail
```

### 第5步：`local_mode` —— 磁盘文件访问

本地服务器提供文件的方式有**两种**：

1. **不使用`--local`参数**（默认方式）：文件通过HTTP协议在 `/file/bot<TOKEN>/<path>` 路径下提供，与公共Bot API的机制相同。20MB的文件大小限制依然存在。此方式仅适用于网络故障时的临时解决方案（例如当无法访问`api.telegram.org`但可以自行托管服务器时）；若想提升文件大小则不适用。
2. **使用`--local`参数**（通过上述的`TELEGRAM_LOCAL=1`设置）：文件会被写入服务器的文件系统，此时`getFile`响应返回的将是**绝对路径**而非HTTP URL。20MB的限制随之被取消。Hermes需要直接从磁盘读取这些字节，而非通过HTTP传输。

要使磁盘读取路径生效，需在上述配置中设置`local_mode: true`，同时确保Hermes进程能够读取服务器返回的路径。具体可分为两种情况：

- **同一台机器**——telegram-bot-api 与 Hermes 运行在同一个主机上。需将数据卷绑定到 Hermes 可读取的目录中（例如 `/var/lib/telegram-bot-api`），并确保文件所有权一致。容器会将其权限降至内部的 `telegram-bot-api` 用户级别（不同镜像的 UID 不同）；最简单的解决办法是在 compose 配置中添加 `user: "<UID>:<GID>"`，从而使文件归属于 Hermes 已在使用的 UID。

- **不同机器**——机器人服务器运行在某个主机上（如 NAS 或独立的虚拟机），而 Hermes 运行在另一台机器上。服务器的数据目录必须以服务器所报告的**相同绝对路径**与 Hermes 所在机器共享（通常为 `/var/lib/telegram-bot-api`）。NFS 是不错的选择；如果不想在文件系统层面处理 UID 不匹配的问题，使用带有 `uid=` 挂载重映射的 CIFS/SMB 也会更便捷。

如果设置了 `local_mode: true`，但 Hermes 无法对返回的文件路径执行 `stat` 操作（可能是权限问题或挂载错误），python-telegram-bot 会自动回退到通过 HTTP 向本地服务器调用 `getFile` 方法——而在 `--local` 模式下，该服务器会返回 `404 Not Found` 错误。这一现象会在 `gateway.log` 中体现为：

```
[Telegram] Failed to cache voice: Not Found
telegram.error.InvalidToken: Not Found
```

如果出现这种情况，说明文件上传功能正常，但文件共享功能存在问题。请以网关运行时的用户身份，在Hermes主机上执行 `ls -la /var/lib/telegram-bot-api/<TOKEN>/voice/` 命令，确认其中有一个文件能够通过 `cat` 命令读取且不会出现权限错误。

### 第6步：进行测试

向该机器人发送大小超过20 MB的语音笔记或音频文件。同时查看网关的日志输出：

```bash
tail -f ~/.hermes/logs/gateway.log | grep -iE "telegram|cache"
```

您应该会看到类似 `[Telegram] Cached user voice at /home/<user>/.hermes/cache/audio/...` 的提示行，而不会出现“文件过大”的拒绝信息。结合上文中的 `stt.enabled: false` 设置，原始音频文件的路径就会被包含在代理的接收消息中，以便后续处理。

## 群聊使用场景

Hermes Agent 在 Telegram 群聊中也可使用，但需注意以下几点：

- **隐私模式**用于决定机器人可以查看哪些消息（详见[步骤3](#step-3-privacy-mode-critical-for-groups)）。
- 即使在群组中，`TELEGRAM_ALLOWED_USERS`规则依然有效——只有经过授权的用户才能触发该机器人。
- 通过设置`telegram.require_mention: true`，可阻止机器人对普通群聊消息作出响应。
- 当满足以下条件时，`telegram.require_mention: true`设置下的群组消息才会被接收：
  - 对机器人发送的某条消息的回复；
  - 包含`@botusername`的提及；
  - 使用`/command@botusername`格式的命令（即包含机器人名称的Telegram机器人菜单命令）；
  - 符合在`telegram.mention_patterns`中配置的正则表达式触发词。
- 在包含多个Hermes机器人的群组中，`telegram.exclusive_bot_mentions`功能可确保消息路由的确定性。当有消息明确提及一个或多个Telegram机器人用户名时，只有被提及的机器人会处理该消息；其他Hermes机器人会在尝试回复或启用触发词机制之前忽略该消息。此功能默认处于开启状态。
- 在BotFather中更改机器人的`@username`后，Hermes会自动识别这一变化，并无需重启网关即可根据新名称进行消息路由。以非`bot`结尾的“可收集型”（Fragment）用户名也受支持。
- 可使用`telegram.ignored_threads`功能，让Hermes在特定的Telegram论坛主题中保持沉默，即便该群组原本允许自由回复或通过提及触发回复。
- 如果未设置`telegram.require_mention`或将其值设为false，Hermes将保持原有的群组处理模式，对能够看到的普通群组消息作出响应。
### 在一个群组中使用多个 Hermes 机器人

如果您在同一个 Telegram 群组中运行多个 Hermes 配置文件，应为每个配置文件创建一个 Telegram 机器人令牌，并为每个配置文件启动一个网关。切勿在多个正在运行的网关中重复使用同一个机器人令牌，否则 Telegram 会拒绝针对该令牌的并发轮询请求。

推荐的群组配置：

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns: []
```

通过此设置，像`@research_bot @ops_bot summarize this`这样的群组消息仅由`research_bot`和`ops_bot`处理。群组中的其他Hermes机器人将保持沉默，即便该消息是对它们之前发送的某条消息的回复，或符合共享唤醒词的条件也是如此。

当两个Hermes机器人互相回复引用内容时，若设置`TELEGRAM_ALLOW_BOTS=all`，它们仍可能陷入无限循环，因为对机器人的回复总会通过`require_mention`检查。将`telegram.bots_requirement: true`（环境变量`TELEGRAM_BOTS_REQUIRE_MENTION`）设为真即可阻断这一路径：只有当其他机器人明确`@提及`当前机器人时，其消息才会触发响应，而人类的回复则仍能正常工作。

在群组对话中，如果消息同时提到了其他参与者（如`@research_bot , @ops_bot 你们都在听吗？`），文本和媒体字幕会完整保留所有提及内容；即便消息仅针对当前机器人，其用户名仍会被移除，因此像`@hermes_bot 2`这样的简短回复依然有效。群组切换时，每个频道的上下文也会携带机器人的Telegram用户名，这样模型就能识别出哪些提及是针对它的。斜杠命令则仍遵循常规的命令触发清理规则。

仅在对旧版群组而言，若不希望明确提及内容覆盖回复和唤醒词触发机制，才应将`exclusive_bot_mentions: false`设为真。

如需同时使用多个配置文件，需为每个配置文件运行一次网关命令。例如：

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

对于规模较小的固定机器人集群，建议使用Shell循环或脚本：针对默认配置文件，调用`hermes gateway <action>`命令；而对于每个自定义配置文件，则分别使用`hermes -p <profile> gateway <action>`命令。相比假设单个进程级命令能够控制每个服务管理器中的所有自定义配置文件，这种方式更为可靠。

### 故障排查：在私聊中正常工作，但在群组中无响应

如果机器人能在私聊中回复消息，但在群组中却保持沉默，请按以下顺序检查相关设置：

1. **Telegram消息传递问题**：关闭BotFather的隐私模式，将机器人提升为群组管理员，或直接@提及该机器人。如果Telegram从未将群组消息传递给机器人，Hermes自然无法响应。
2. **更改隐私设置后的重新加入问题**：在修改BotFather的隐私设置后，先将机器人从群组中移除，然后再重新添加。Telegram可能会对已存在的群组成员关系保留旧的消息传递方式。
3. **Hermes授权问题**：请确保发送者已被列入`TELEGRAM_ALLOWED_USERS`或`TELEGRAM_GROUP_ALLOWED_USERS`列表，或者通过`TELEGRAM_GROUP_ALLOWED_CHATS`允许该群组聊天。
4. **@提及过滤规则问题**：如果设置了`telegram.require_mention: true`，那么除非消息为斜杠命令、对机器人的回复、`@botusername`形式的提及，或符合已配置的`mention_patterns`规则，否则普通的群组聊天消息将被忽略。
5. **多机器人路由问题**：如果一个群组中包含多个机器人，请确保每个Hermes配置文件使用唯一的机器人令牌，并保持`exclusive_bot_mentions`选项处于开启状态，除非您有意采用旧式的共享触发机制。
在 Telegram 群组及超级群组中，存在负数的聊天 ID 是正常现象。如果您使用的是聊天范围授权机制，应将这些 ID 添加到 `TELEGRAM_GROUP_ALLOWED_CHATS` 中，而非发送者用户白名单中。

### 群组触发器配置示例

请将以下内容添加到 `~/.hermes/config.yaml` 文件中：

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

该示例支持所有常规的直接触发方式，以及以 `chompy` 开头的消息，即便这些消息未使用 `@mention` 标签也是如此。在执行提及检测和自由回复检测之前，Telegram 中编号为 `31` 和 `42` 的主题中的消息会被直接忽略。

### 关于 `mention_patterns` 的说明

- 模式匹配采用 Python 正则表达式
- 匹配时不区分大小写
- 模式会同时应用于文本消息和媒体文件的字幕
- 无效的正则表达式会被忽略，相关警告会记录在网关日志中，而不会导致机器人崩溃
- 若希望某模式仅能在消息开头匹配，可使用 `^` 进行定位

## 私聊主题（Bot API 9.4）

Telegram Bot API 9.4（2026年2月发布）引入了**私聊主题**功能——机器人无需创建超级群组，即可在一对一的私聊中直接创建类似论坛的主题讨论串。借助此功能，您可以在现有的私聊中使用 Hermes 创建多个相互隔离的工作空间。

### 应用场景

如果您正在处理多个长期项目，主题功能有助于保持各项目的独立上下文：

- **“网站”主题**——用于开发生产环境中的Web服务
- **“研究”主题**——用于文献查阅和论文探索
- **“综合”主题**——用于处理各类杂项任务及快速提问

每个主题都拥有独立的对话会话、历史记录和上下文，与其他主题完全隔离。

### 配置说明

:::caution 先决条件
在将主题添加到配置文件之前，用户必须先在与机器人的私聊中**启用主题模式**：

1. 在 Telegram 中打开与 Hermes 机器人的私聊窗口。  
2. 点击窗口顶部的机器人名称，以查看聊天信息。  
3. 启用 **Topics** 功能（该开关可将聊天界面转换为论坛形式）。  

若未启用此功能，Hermes 在启动时会输出“该聊天并非论坛”并跳过主题创建流程。这是 Telegram 客户端端的设置——机器人无法通过程序自动启用它。  
:::  

可在 `~/.hermes/config.yaml` 文件的 `platforms.telegram.extra.dm_topics` 部分添加主题内容：

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
4. 每个主题中的消息拥有独立的对话历史、内存清除机制以及上下文窗口。

### 根级私信处理

默认情况下，发送到根级私信（即不在任何主题内的私信）会按常规方式处理。若需将根级私信视为聊天大厅，可设置 `ignore_root_dm: true` —— 对于已配置主题私信的用户，普通消息将被静默忽略，而系统命令（如 `/start`、`/help`、`/status` 等）仍可正常使用。

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

该检查是**按聊天会话单独进行的**：只有那些在 `dm_topics` 中至少有一条记录的用户，其主私信才会受到影响；未配置相关主题的用户则不会受到任何影响。

### 技能绑定

包含 `skill` 字段的主题会在该主题下的新会话开始时自动加载对应的技能。其工作原理与在对话开头输入 `/skill-name` 完全相同——技能内容会被注入到第一条消息中，后续消息则会在对话历史中显示该技能内容。

例如，包含 `skill: arxiv` 的主题，无论何时会话重置（比如执行了 `/new` 或 `/reset` 命令后），都会自动预加载 arxiv 技能。

:::提示
通过非配置方式创建的主题（例如手动调用 Telegram API 创建的），会在收到 `forum_topic_created` 服务消息时被自动检测到。您也可以在网关运行期间向配置中添加新主题——它们会在下一次缓存未命中时被识别出来。
:::

## 多会话私信模式（`/topic`）

这是一种类似 ChatGPT 的多会话私信模式——一个机器人，多个并行对话。与上文由管理员筛选的 `extra.dm_topics` 不同，此模式是**用户驱动的**：无需任何配置，也不需要预先指定主题名称。最终用户只需通过 `/topic` 启用该模式，然后点击 Telegram 的 **+** 按钮创建任意数量的主题，每个主题都对应一个完全独立的 Hermes 会话。

### `/topic` 子命令

| 命令 | 使用场景 | 功能效果 |
|------|---------|--------|
| `/topic` | 根私信，功能尚未启用 | 检查 BotFather 的功能支持情况，启用多会话模式，并创建固定的系统主题 |
| `/topic` | 根私信，功能已启用 | 显示状态：列出可恢复的未关联会话 |
| `/topic` | 已处于某个主题中 | 显示当前主题的会话绑定信息 |
| `/topic help` | 任意场景 | 显示命令的在线使用说明 |
| `/topic off` | 根私信 | 禁用多会话模式，并清除该聊天的所有主题绑定 |
| `/topic <session-id>` | 已处于某个主题中 | 将之前的 Telegram 会话恢复到当前主题中 |

只有经过授权的用户（通过 `TELEGRAM_ALLOWED_USERS` 或平台认证配置进行白名单管理）才能使用 `/topic` 命令。未经授权的发送者将收到拒绝响应，而无法执行该命令。

### 私信主题模式与多会话私信模式的对比

| 对比项 | `extra.dm_topics`（配置驱动） | `/topic`（用户驱动） |
|---|---|---|
| 启用方式 | 由操作员在 `config.yaml` 中配置 | 由最终用户发送 `/topic` 命令启用 |
| 主题列表 | 在配置中预先定义的固定列表 | 用户可自由创建或删除主题 |
| 主题名称 | 由操作员指定 | 由用户自行选择；会自动重命名为与 Hermes 会话标题一致的名称 |
| 根私信的行为 | 普通聊天模式（若设置 `ignore_root_dm: true` 则为大厅模式） | 变为系统大厅模式（非命令类消息将被拒绝接收） |
| 主要应用场景 | 需要绑定技能的永久工作空间 | 快速创建的并行会话 |
| 数据持久化方式 | 通过配置中的 `extra.dm_topics` 存储 | 通过 `telegram_dm_topic_mode` 及 `telegram_dm_topic_bindings` SQLite 表存储 |
这两个功能可以在同一个机器人上同时存在——用户可以通过私信发送 `/topic` 命令，而 `extra.dm_topics` 则继续负责管理其他聊天窗口中由操作员设定的主题。

### 先决条件

在 **@BotFather** 中打开您的机器人 → **Bot Settings → Threads Settings**：

1. 开启 **Threaded Mode**（这将启用 `has_topics_enabled`）
2. 不要禁用用户创建主题的功能（保持 `allows_users_to_create_topics` 为开启状态）

当用户首次发送 `/topic` 命令时，Hermes 会调用 `getMe` 函数来检查这两个设置。如果其中任意一项未开启，Hermes 会发送 BotFather Threads Settings 页面的截图，并说明需要调整哪些选项——只有在满足所有先决条件后，功能才会被激活。

### 激活流程

从根私信窗口发送：

```
/topic
```

Hermes 将执行以下操作：

1. 检查 `getMe().has_topics_enabled` 和 `allows_users_to_create_topics` 的值。
2. 若两者均为 true，则为该私信开启多会话主题模式。
3. 尽力创建一个用于显示状态或发送指令的 **系统** 主题并将其设为固定主题。
4. 回复用户可恢复的之前所有未关联的 Telegram 会话列表。

启用该功能后，**根级私信将变为一个大厅**：常规消息会被拒绝，系统会引导用户查看 **所有消息**。不过在根级私信中，系统指令（如 `/status`、`/sessions`、`/usage`、`/help` 等）依然有效。

### 创建新主题（最终用户操作流程）

1. 在 Telegram 中打开与该机器人的私信。
2. 点击机器人界面顶部的 **所有消息**，然后发送任意消息。
3. Telegram 会为该消息创建一个新主题。
4. Hermes 会在该主题内进行回复——此时该主题即成为一个独立的会话。

每个主题都拥有独立的对话历史、模型状态、工具执行记录以及会话 ID。其隔离标识为 `agent:main:telegram:dm:{chat_id}:{thread_id}`，这与通过配置实现的私信主题隔离机制相同。

### 自动重命名主题

在首次交互之后，Hermes 会通过自动标题生成流程为每个主题生成一个标题，随后 Telegram 会相应地重命名该主题——例如，“新主题”会被改为“数据库迁移方案”。此重命名操作为尽力而为：若失败也会被记录，但不会导致会话中断。

如需禁用此功能并保持手动设置的主题名称不变，请进行如下设置：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_topic_auto_rename: true
```

当此标志处于开启状态时，Hermes 仍会生成一个内部会话标题（供 `hermes sessions`、TUI 等工具使用），但不会修改 Telegram 中的主题名称。这在您通过 BotFather 的线程模式手动管理主题，且不希望每次首次回复都覆盖主题标题时非常有用。

### 在主题内使用 `/new`

该命令可重置当前主题的会话（生成新的会话 ID 并清空历史记录），而不会影响其他主题。Hermes 会回复提示您：若需同时处理多项任务，通常应通过 **All Messages** 功能创建新主题。

### 恢复之前的会话

在某个主题内发送以下内容：

```
/topic <session-id>
```

该功能会将当前主题绑定到已存在的Hermes会话中，而非创建新的会话。这对于在开启主题模式之前开始的对话进行延续非常有用。相关限制如下：

- 目标会话必须属于同一位Telegram用户；
- 目标会话不得已绑定到其他主题。

Hermes会通过会话名称进行确认，并回放上一条助手消息以便提供上下文信息。

如需查看会话ID，可在主私信窗口发送命令 `/topic`（无需参数）——Hermes会列出该用户所有未关联的Telegram会话。

### 在主题内部使用 `/topic`（无需参数）

可显示当前主题的绑定信息：会话名称、会话ID，以及关于使用 `/new` 命令与创建新主题的说明。

### 技术实现细节

- 绑定状态会被保存到 `state.db` 文件中的 `telegram_dm_topic_mode(profile_name, chat_id, user_id, enabled, ...)` 表中。该表的主键为 `(profile_name, chat_id)`，因此当同一位Telegram用户同时与多个机器人进行私信交流时（其中“私人聊天ID”实际上就是用户ID，且在不同机器人之间是相同的），共享同一个 `state.db` 的多路复用型或按用户路由的机器人不会互相覆盖数据。
- 每个主题的绑定信息则会被保存到 `telegram_dm_topic_bindings(profile_name, chat_id, thread_id, session_id, ...)` 表中，其主键为 `(profile_name, chat_id, thread_id)`，并且对 `session_id` 设置了 `ON DELETE CASCADE` 规则——一旦删除某个会话，其对应的主题绑定也会自动被清除。
- 基于主题模式的 SQLite 迁移为**可选功能**：它会在首次调用 `/topic` 时执行，而不会在网关启动时自动运行。只要用户未在该配置文件中运行 `/topic`，`state.db` 文件就不会发生任何变化。架构版本 v3 添加了 `profile_name` 字段；旧格式的记录仅会迁移至 `default` 命名空间中。
- 每条传入的私信消息都会通过**已路由的**配置文件（即 `source.profile`，而非进程全局的当前活动配置文件）来查找对应的 `(profile_name, chat_id, thread_id)` 绑定信息。如果找到匹配项，系统会通过 `SessionStore.switch_session()` 将消息路由至对应的会话，从而确保磁盘上会话密钥与会话 ID 之间的映射关系保持一致。
- 在某个主题内部使用 `/new` 命令可重写绑定记录，使其指向新的会话 ID，这样后续发送的消息就会进入这个新的会话中处理。
- 在 `extra.dm_topics` 中声明的主题**绝不会被自动重命名**——即便启用了多会话模式，操作员指定的主题名称也会被保留。
- 若需关闭聊天中**所有**主题的自动重命名功能（包括通过线程模式创建的临时主题），可设置 `extra.disable_topic_auto_rename: true`。
- 在支持论坛功能的私信中，处于最顶层的“General”主题被视为根大厅，无论 Telegram 是以 `message_thread_id=1` 的格式还是不带 thread_id 的格式传递消息，这一规则均适用。
- 对于根大厅的提醒消息，每**(profile, chat)** 组合每 30 秒最多只能发送一条——即使有用户忘记开启主题模式并在根大厅输入了十条提示，也只会收到一条回复；此外，两个共享同一 chat_id 的多配置文件用户彼此的提醒消息也不会被相互屏蔽。
- 对于每个**（账号资料，聊天窗口）**，BotFather 设置界面的截图发送频率有限制，每5分钟仅可发送一次——在 Threads 功能尚未启用时反复发送 `/topic` 命令也无法重新上传同一张图片。  
- 在某个主题内输入 `/bg <prompt>` 后，结果会返回到该主题中；背景会话不会自动触发对应主题的名称更改。  
- `/topic` 命令本身需经过机器人的用户授权检查——未经授权的私信将会被拒绝，而无法启动该功能。  

### 禁用多会话模式  

在主私信窗口中发送 `/topic off` 即可。Hermes 会关闭**当前账号资料**对应的命名空间，清除该账号资料在对应聊天窗口中的所有 `(thread_id → session_id)` 关联关系，此时主私信窗口将恢复为普通的 Hermes 聊天界面。Telegram 中已存在的主题不会被删除，只是不再作为独立的会话存在。如需重新启用多会话模式，可稍后再次运行 `/topic` 命令。  

如果需要手动清理数据（例如对多个聊天窗口进行批量重置），可通过 `profile_name` 来筛选对应的会话行（单账号安装情况下可使用 `default`）。

```bash
sqlite3 ~/.hermes/state.db \
  "UPDATE telegram_dm_topic_mode SET enabled = 0
     WHERE profile_name = 'default' AND chat_id = '<your_chat_id>';
   DELETE FROM telegram_dm_topic_bindings
     WHERE profile_name = 'default' AND chat_id = '<your_chat_id>';"
```

### Hermes版本降级

如果您将Hermes降级到不支持 `/topic` 功能的旧版本，该功能将直接失效——`state.db` 中仍会保留 `telegram_dm_topic_mode` 和 `telegram_dm_topic_bindings` 这两个表，但旧版本的代码会忽略它们。私信对话将恢复为原有的单线程隔离模式（每个 `message_thread_id` 仍会通过 `build_session_key` 生成独立的会话），因此您现有的Telegram主题功能仍可作为并行会话正常使用。主私信对话不再作为大厅存在，其中的消息会像以往一样直接进入智能体处理。再次升级后，多会话模式将在原有位置重新启用。

## 群组论坛主题技能绑定

已开启**主题模式**（也称为“论坛主题”）的超级群组本身就已实现了按主题的会话隔离——每个 `thread_id` 对应独立的对话。不过，您可能希望像私信主题技能绑定那样，在特定群组主题中有消息到达时自动加载相应技能。

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
| `chat_id` | 是 | 超群的数字 ID（以 `-100` 开头的负数） |
| `name` | 否 | 该主题的易读标签（仅用于参考） |
| `thread_id` | 是 | Telegram 论坛主题的 ID，可在 `t.me/c/<group_id>/<thread_id>` 链接中查看 |
| `skill` | 否 | 在该主题的新会话中自动加载的技能 |

### 工作原理

1. 当有消息进入已映射的群组主题时，Hermes 会从 `group_topics` 配置中查找对应的 `chat_id` 和 `thread_id`。
2. 如果匹配项包含 `skill` 字段，则该技能会自动加载到当前会话中——这一机制与私信主题的技能绑定方式相同。
3. 不包含 `skill` 键的主题仅具备会话隔离功能（与现有行为一致，无变化）。
4. 未映射的 `thread_id` 或 `chat_id` 值将被静默忽略——既不会报错，也不会加载任何技能。

### 与私信主题的区别

| | 私信主题 | 群组主题 |
|---|---|---|
| 配置键 | `extra.dm_topics` | `extra.group_topics` |
| 主题创建 | 若缺少 `thread_id`，Hermes 会通过 API 创建主题 | 由管理员在 Telegram 界面中创建主题 |
| `thread_id` | 创建后会自动填充 | 必须手动设置 |
| `icon_color` / `icon_custom_emoji_id` | 支持 | 不适用（外观由管理员控制） |
| 技能绑定 | ✓ | ✓ |
| 会话隔离 | ✓ | ✓（论坛主题本身即具备此功能） |
:::提示
若要查找某个主题的`thread_id`，可在Telegram网页版或桌面端打开该主题，查看其URL：`https://t.me/c/1234567890/5`——末尾的数字（`5`）即为`thread_id`。超级群组的`chat_id`则是群组ID前加上`-100`前缀（例如，群组`1234567890`对应的`chat_id`为`-1001234567890`）。
:::

## 最新的Bot API功能

- **Bot API 9.4（2026年2月）：**私人聊天主题——机器人可通过`createForumTopic`在一对一的私信中创建论坛主题。Hermes将此功能用于两项不同的用途：由管理员精选的[私人聊天主题](#private-chat-topics-bot-api-94)（通过配置确定，主题列表固定），以及由用户主导的[多会话私信模式](#multi-session-dm-mode-topic)（通过`/topic`指令启用，允许用户创建无限数量的主题）。
- **隐私政策：**Telegram现在要求机器人必须制定隐私政策。可通过BotFather使用`/setprivacy_policy`指令来设置隐私政策，否则Telegram可能会自动生成一个占位文本。如果您的机器人面向公众，这一点尤为重要。
- **Bot API 9.5（2026年3月）：**通过`sendMessageDraft`实现原生流式传输。Hermes支持Telegram的原生流式草稿API，可作为私人聊天的可选传输方式。由于在某些Telegram客户端上，草稿预览可能会出现折叠和重新渲染的情况，因此默认仍采用传统的`editMessageText`传输方式。

### 流式传输（`gateway.streaming.transport`）

当启用流式传输功能（`gateway.streaming.enabled: true`）时，Hermes会从四种传输方式中选择一种：

| 值 | 行为 |
|---|---|
| `auto`（默认值） | 在支持的聊天场景中（目前为 Telegram 私信）使用原生草稿流式传输；在其他场景则采用传统的基于编辑的传输方式。若草稿帧传输失败，会平滑降级处理。 |
| `draft` | 强制使用原生草稿功能。若聊天场景不支持草稿功能（如群组/话题），则会记录降级信息并转而使用编辑模式。 |
| `edit` | 对所有类型的聊天场景均采用传统的逐次调用 `editMessageText` 的轮询方式。 |
| `off` | 完全禁用流式传输（仅发送最终回复，无逐步更新）。 |

配置位置：`~/.hermes/config.yaml`

```yaml
gateway:
  streaming:
    enabled: true
    transport: auto    # auto | draft | edit | off
```

**使用 `edit`（默认值）在私信中显示的效果**——网关会首先发送一条常规的预览消息，随后通过 `editMessageText` 功能逐步更新该消息，从而避免出现 Telegram 中草稿预览被合并或回滚的问题。

**使用 `auto` 或 `draft` 在私信中显示的效果**——Telegram 会展示一个动态的草稿预览，内容会逐个字符进行更新。当回复完成后，它将以普通消息的形式发送，且客户端上的草稿预览会自动消失。由于草稿没有消息 ID，因此最终的内容才会保留在您的聊天记录中。

**群组、超级群组和论坛主题呢？** Telegram 仅允许在私信中使用 `sendMessageDraft` 功能。对于其他类型的聊天场景，网关会自动切换为基于编辑的流程——用户体验与之前保持一致。

**如果草稿预览出现故障怎么办？** 无论是因为短暂的网络错误、服务器端拒绝，还是 Python-telegram-bot 版本过旧导致的故障，系统都会让后续的响应重新回到基于编辑的流程。下一次响应将会重新尝试发送。

## 渲染：富文本消息、表格及链接预览

**富文本消息（Bot API 10.1）**。对于那些使用传统 MarkdownV2 方式会导致显示效果降级的最终回复内容——如表格、任务列表、可折叠的 `<details>` 标签以及块级数学公式——系统会通过 Telegram 的原生 [`sendRichMessage`](https://core.telegram.org/bots/api#sendrichmessage) 函数，并结合代理节点的**原始 Markdown 格式**进行发送，从而确保这些内容能够在客户端直接正确渲染，而无需经过任何客户端端的格式转换。在私信中，由于默认设置了 `rich_drafts: false`，实时预览会以纯文本形式呈现——此时会使用 Telegram 的临时草稿传输机制并采用传统渲染方式（表格及其他仅支持富文本显示的内容在预览中仍以原始 Markdown 格式呈现）——随后再通过 `sendRichMessage` 发送最终完成的回复。若将 `rich_drafts: true` 设为 true，则实时预览也会同时使用 `sendRichMessageDraft` 函数。对于基于编辑的流式回复，可通过 `editMessageText` 函数的 `rich_message` 参数直接对现有的预览内容进行修改完善。而普通回复内容（纯文本、加粗/斜体文字以及简单列表）则仍会通过 MarkdownV2 方式发送，以此确保在不同客户端上字体样式和间距保持一致。

当消息内容超过 32,768 字符的富文本限制时，系统会自动切换到 MarkdownV2 方式；此外，若遇到 Telegram 端返回的任何错误（如旧版 `python-telegram-bot` 版本不支持的接口、解析错误或块/列尺寸过大等），系统也会**无缝回退**到 MarkdownV2 方式——这样您的消息就绝不会丢失。不过，暂时的网络故障并不会导致消息被悄悄重新发送（因此不会出现重复的最终消息）。

**MarkdownV2 备用方案。** 当某条消息无法使用富文本格式时，Hermes 会将其转换为 MarkdownV2 格式。由于 MarkdownV2 本身不支持原生表格语法，因此管道式表格会被进行规范化处理：

- **小型表格**会转换为**行组项目符号列表**——每行内容都会成为列标题下的可读项目符号列表。此方式适用于包含2至4列且单元格内容较短的表格。
- **较大或较宽的表格**则会转而使用带对齐列的**代码块**，以避免内容折叠。

富文本消息为**可选功能**。默认情况下仍会使用传统的 MarkdownV2 格式，因为目前的 Telegram 客户端往往难以将机器人 API 生成的富文本消息复制为纯文本，这对命令片段及在移动设备上查看内容尤为不便。如需实现表格、任务列表、详细信息及数学公式的原生渲染效果，则需启用该功能：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        rich_messages: true
        rich_drafts: false
```

此设置旨在确保客户端渲染与复制功能的兼容性；当 Telegram 拒绝接收富格式 API 调用时，Hermes 会自动回退到默认模式。`rich_drafts` 用于控制私信流式预览是否以富格式呈现（即使用 `sendRichMessageDraft` 功能），其默认值为关闭状态，因为 Telegram Desktop/macOS 能够在聊天界面重新绘制之前，先以普通方式显示富格式草稿内容；若将其设置为开启，则预览将以纯文本形式流式展示，最终发送的仍为原生富格式消息。如果您希望在启用富格式消息的同时保留传统的“始终以代码块显示表格”的行为，可通过在 `config.yaml` 中将 `telegram.pretty_tables` 设置为 `false` 来禁用表格格式化功能（默认值为 `true`）。

**链接预览。** Telegram 会自动为机器人消息中的 URL 生成链接预览。如果您希望禁用这些预览（例如避免出现过长的 `/tools` 输出，或避免智能体回复中列出大量链接等情况），可以采取相应措施：

```yaml
gateway:
  platforms:
    telegram:
      extra:
        disable_link_previews: true
```

启用该功能后，Hermes 会在每条发送的消息中添加 Telegram 的 `LinkPreviewOptions(is_disabled=True)` 参数；而对于较旧版本的 `python-telegram-bot`，则会回退使用传统的 `disable_web_page_preview` 参数。

## 群组白名单设置

Telegram 群组和论坛聊天室提供了两种相互独立的配置选项：

- **发送者用户 ID**（`group_allow_from` / `TELEGRAM_GROUP_ALLOWED_USERS`）—— 一种针对发送者的白名单，仅适用于群组/论坛内的消息。当您希望特定用户能够在群组中调用机器人，而又不想将其添加到 `TELEGRAM_ALLOWED_USERS` 中（因为那样也会赋予他们私信权限）时，可使用此选项。
- **聊天室 ID**（`group_allowed_chats` / `TELEGRAM_GROUP_ALLOWED_CHATS`）—— 一种针对聊天室的白名单。属于这些群组/论坛的任何成员均可与机器人交互。对于以群组成员身份作为访问权限依据的团队/客服机器人而言，此功能非常实用。

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
- `TELEGRAM_GROUP_ALLOWED_USERS` 仅允许列表中指定的发送者在群组/论坛内发送消息；除非该发送者同时被列入 `TELEGRAM_ALLOWED_USERS`，否则仍无法向机器人发送私信。
- 若聊天记录位于 `TELEGRAM_GROUP_ALLOWED_CHATS` 列表中，则无论发送者为谁，该聊天中的所有成员均被允许参与交流。
- 在上述任意参数中使用 `*` 可允许任何发送者或任何类型的聊天。

此规则会在现有的提及/模式触发机制，以及 `group_topics` 和 `ignored_threads` 设置的基础上叠加运行。

### 从 PR #17686 之前的版本迁移说明

在功能分离之前，仅有 `TELEGRAM_GROUP_ALLOWED_USERS` 这一参数，用户需在其中输入**聊天 ID**。为保持向后兼容性，`TELEGRAM_GROUP_ALLOWED_USERS` 中以 `-` 开头的值仍会被视为聊天 ID，并仅会记录一次弃用警告。迁移方式如下：

```bash
# Old (still works, but deprecated)
TELEGRAM_GROUP_ALLOWED_USERS="-1001234567890"

# New
TELEGRAM_GROUP_ALLOWED_CHATS="-1001234567890"
```

### 允许访客被@提及（`guest_mode`）

在常规配置中，`group_allowed_chats`起着严格的过滤作用：即便有成员明确@提及该机器人，来自列表之外群组的消息也会被直接忽略。对于用于提供支持或团队协作的机器人而言，这确实是合适的默认设置。

而对于较为随意的使用场景——比如朋友间的群聊，你希望机器人**大部分时间保持沉默**，但**在收到明确呼叫时再作出响应**——则可以启用`guest_mode`：

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

当设置 `guest_mode: true` 时，只有来自未列入白名单群组的消息在**明确@提及该机器人**的情况下才会被处理。且每一轮对话都必须有提及动作——访客互动不具备会话持续性，因此若未被主动发起对话，机器人不会自动参与好友群组中的讨论。

私信及已列入白名单的群组将保持与以往完全一致的行为模式。

## Slash命令访问控制

默认情况下，所有获准使用的用户均可执行所有Slash命令。若希望将白名单用户分为**管理员**（拥有完整Slash命令权限）和**普通用户**（仅能使用明确启用的命令），可在平台的 `extra` 块中添加 `allow_admin_from` 和 `user_allowed_commands` 参数：

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

- 属于某个范围（私信或群组）的 `allow_admin_from` 列表中的用户，可通过实时注册表运行**所有**已注册的斜杠命令——包括内置命令以及通过插件注册的命令。
- 属于 `allow_from` 列表但**不在** `allow_admin_from` 列表中的用户，仅能运行 `user_allowed_commands` 中列出的命令，此外还可以使用始终允许的命令 `/help` 和 `/whoami`。
- 普通聊天内容（非斜杠格式的消息）不会受到影响。非管理员用户仍可正常与智能体交流，只是无法触发任意命令。
- **向后兼容性**：如果某个范围未设置 `allow_admin_from`，则该范围的斜杠命令限制功能将被关闭。现有安装无需任何更改即可继续正常运行。
- 私信中的管理员身份并不等同于群组中的管理员身份。每个范围都有独立的管理员列表。
- 如果仅设置了 `group_allow_admin_from`，则私信范围将保持无限制（向后兼容）模式。

可使用 `/whoami` 命令查看当前所处的范围、您的权限等级（管理员/用户/无限制），以及您可以运行的斜杠命令列表。

## 交互式模型选择器

在 Telegram 聊天中发送不带参数的 `/model` 命令时，Hermes 会显示一个交互式内联键盘，用于切换模型：

1. **提供商选择**——显示各可用提供商的按钮，并标注对应模型的数量（例如：“OpenAI (15)”，当前所选提供商则为“✓ Anthropic (12)”）。
2. **模型选择**——提供分页的模型列表，支持使用 **上一页**/**下一页** 进行导航，还有 **返回** 按钮可回到提供商选择页面，以及 **取消** 按钮。
顶部会显示当前使用的模型及服务提供商。所有导航操作均通过直接编辑同一条消息来完成，从而避免聊天界面变得杂乱。

:::提示
如果您已知确切的模型名称，可直接输入 `/model <名称>` 而跳过选择界面。此外，您还可以使用 `/model <名称> --global` 选项，使该设置在多次会话之间保持不变。
:::

## DNS-over-HTTPS 备用 IP 地址

在某些受限网络环境中，`api.telegram.org` 可能会解析为无法访问的 IP 地址。Telegram 适配器配备了**备用 IP**机制，能够透明地尝试连接其他备用 IP，同时确保保留正确的 TLS 主机名和 SNI 设置。

### 工作原理

1. 如果已设置了 `TELEGRAM_FALLBACK_IPS`，则直接使用这些 IP 地址。
2. 否则，适配器会通过 DNS-over-HTTPS（DoH）自动查询**Google DNS**和**Cloudflare DNS**，以寻找 `api.telegram.org` 的其他可用 IP。
3. 系统会先尝试已知的 IPv4 版 Telegram API IP 地址，然后再尝试双栈格式的 `api.telegram.org` 主机名。被列入黑名单的 IPv6 连接路径虽会导致连接失败，但不会引发错误，因为这原本是为了防止事件循环被阻塞，从而避免超过 30 秒的初始化时间限制。
4. 如果 DoH 也被屏蔽或超时，系统会使用硬编码的 IPv4 备用地址列表（`149.154.166.110`、`149.154.167.220`）作为首选。此时主机名将作为最后的尝试手段。
5. 一旦某条连接路径成功，它就会被标记为“固定选项”——后续请求将直接使用该路径。对于仅支持 IPv6 的网络，主机名仍会保留作为最后手段。

### 配置方式

```bash
# Explicit fallback IPs (comma-separated)
TELEGRAM_FALLBACK_IPS=149.154.167.220,149.154.167.221
```

或者可在 `~/.hermes/config.yaml` 中配置：

```yaml
platforms:
  telegram:
    extra:
      fallback_ips:
        - "149.154.167.220"
```

:::提示
通常无需手动配置此选项。通过 DoH 实现的自动发现功能已可应对大多数网络受限的场景。仅当您的网络也屏蔽了 DoH 时，才需要使用 `TELEGRAM_FALLBACK_IPS` 环境变量。如果主机上的 IPv6 功能出现故障，您还可以在 `config.yaml` 中设置 `network.force_ipv4: true`，从而在整个系统中跳过 AAAA 查找流程。
:::

## 代理支持

如果您的网络需要通过 HTTP 代理才能访问互联网（企业环境中较为常见），Telegram 适配器会自动读取标准的代理环境变量，并将所有连接路由至该代理。

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

该代理设置同时适用于主传输方式以及所有备用 IP 传输方式。无需进行额外的 Hermes 配置——只要设置了环境变量，系统便会自动使用它。

:::note
此处所述为 Hermes 用于连接 Telegram 的自定义备用传输层。而在其他场景中使用的标准 `httpx` 客户端本身就已能够原生支持代理环境变量。
:::

## 消息反应功能

机器人可以通过添加表情符号反应来作为视觉化的处理反馈：

- 当机器人开始处理您的消息时显示 👀
- 当响应成功发送时显示 👍
- 若处理过程中出现错误则显示 👎

反应功能**默认处于关闭状态**。如需启用该功能，请在 `config.yaml` 中进行设置：

```yaml
telegram:
  reactions: true
```

或者通过环境变量设置：

```bash
TELEGRAM_REACTIONS=true
```

:::note
与 Discord（其反应功能为叠加式）不同，Telegram 的 Bot API 会在单次调用中一次性替换所有机器人反应。从 👀 到 👍/👎 的切换是原子级完成的——您不会同时看到这两种反应。
:::

:::tip
如果机器人没有在群组中添加反应的权限，相关调用将会静默失败，消息处理仍会正常进行。
:::

## 每个频道的提示语

可为特定的 Telegram 群组或论坛主题设置临时系统提示语。该提示语会在每轮对话的运行时被注入——不会被保存到对话记录中——因此更改会立即生效。

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

这些键可以是聊天 ID（群组/超级群组）或论坛主题 ID。对于论坛群组，主题级别的提示会优先于群组级别的提示：

- 在群组 `-1001234567890` 内的主题 `42` 中发送的消息 → 会使用主题 `42` 的提示
- 在主题 `99` 中发送的消息（未指定特定设置） → 会回退到群组 `-1001234567890` 的提示
- 在没有相关设置的群组中发送的消息 → 不会应用任何频道提示

数值形式的 YAML 键会自动转换为字符串格式。

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 机器人完全无响应 | 确认 `TELEGRAM_BOT_TOKEN` 的值正确。检查 `hermes gateway` 的日志以查找错误信息。 |
| 机器人回复“未经授权” | 您的用户 ID 不在 `TELEGRAM_ALLOWED_USERS` 列表中。请使用 @userinfobot 再次确认。 |
| 机器人忽略群组消息 | 可能处于隐私模式。请关闭该模式（参见第3步），或将机器人设为群组管理员。**更改隐私设置后，请务必将机器人移除后再重新添加。** |
| 语音消息无法转录 | 确认语音转文字功能已启用：可选择安装 `faster-whisper` 进行本地转录，或在 `~/.hermes/.env` 文件中设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`。 |
| 语音回复以文件形式显示而非对话气泡 | 需要安装 `ffmpeg`（用于 Edge TTS Opus 格式转换）。 |
| 机器人令牌已被撤销或无效 | 通过 BotFather 的 `/revoke`、`/newbot` 或 `/token` 命令生成新令牌，然后更新您的 `.env` 文件。 |
| Webhook 无法接收更新 | 确认 `TELEGRAM_WEBHOOK_URL` 是可公开访问的（可使用 `curl` 进行测试）。确保您的平台或反向代理能够将来自该 URL 端口的 HTTPS 流量路由到由 `TELEGRAM_WEBHOOK_PORT` 指定的本地监听端口（两者无需为相同数值）。同时需确保 SSL/TLS 加密已启用——Telegram 仅会向 HTTPS 地址发送数据。最后检查防火墙规则。 |

## 执行审批

当机器人试图运行可能具有危险性的命令时，它会在聊天界面中请求您的批准：

> ⚠️ 此命令可能具有危险性（会导致递归删除操作）。如需批准，请回复“yes”。

回复“yes”/“y”表示批准，回复“no”/“n”则表示拒绝。

## 交互式提示（clarify功能）

当智能体调用`clarify`工具——用于询问您偏好的方案、获取任务完成后的反馈，或在需要做出重要决策前进行确认时——Telegram会以**内嵌键盘按钮**的形式展示问题：

> ❓ 我应该为控制面板选择哪种框架？
>
> [1. Next.js] [2. Remix] [3. Astro]
> [✏️ 其他（直接输入）]

点击按钮即可作答，或选择**其他**来输入自由文本回复（您发送的下一条消息将作为答案）。对于没有预设选项的开放式`clarify`调用，系统会直接跳过按钮，等待您的下一条消息。

您可以通过`~/.hermes/config.yaml`中的`agent.clarify_timeout`参数来设置响应超时时间（默认为600秒）。如果您在超时时间内未作答，智能体会发送一条提示信息继续执行，而不会陷入停滞状态。

## 推送通知频率

每当机器人发送消息时，Telegram都会触发一次推送通知。对于那些会持续输出工具处理进度、流式更新和状态回调的复杂智能体对话，这种频繁的通知很容易造成干扰。Telegram适配器提供了两种通知模式：

| 模式 | 行为表现 |
|------|----------|
| `important`（默认） | 仅对**最终回复**、**确认提示**以及**斜杠命令确认信息**发送推送通知。工具处理进度、流式数据块和状态消息则会以`disable_notification=true`的设置被静默处理。 |
| `all` | 机器人发送的每一条消息都会触发推送通知。这是旧版行为；仅当您确实希望随时了解每一次工具调用时才建议启用此模式。 |

相关配置可在`~/.hermes/config.yaml`中设置：

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

遇到未知值时，系统会记录警告并默认将其等级设置为“重要”。

## 在原位置编辑状态消息

Telegram适配器通过`send_or_update_status()`函数来处理定时触发的智能体状态回调（例如“正在压缩上下文……”、“正在调用工具……”等）。该函数会维护一个`{(chat_id, status_key) → message_id}`的缓存机制，后续触发时直接**编辑现有的消息气泡**，而非每次都新增一条消息。不同的`status_key`值会对应独立的消息，因此不同聊天窗口中的消息不会相互冲突。如果编辑失败（例如用户已删除该消息，或消息年龄超过Telegram允许编辑的时间限制），则该缓存条目会被移除，下一次触发时会发送新消息并重新缓存其ID。此功能无需任何配置，即为Telegram的默认行为。那些未实现`send_or_update_status`功能的适配器则会直接使用普通的`send()`函数，且不会进行任何更改。

## 在智能体处理消息期间固定用户输入的消息

当用户发送的消息触发智能体开始处理时，Telegram适配器会将该消息固定显示，直到处理完成后再将其解固定。这是一种简单的视觉提示，表明机器人正在积极处理该消息，而非对其置之不理。此固定功能通过设置`disable_notification=true`来实现，从而避免额外的通知推送。同样，此功能也不需要任何配置。

## 安全性

:::warning
务必设置`TELEGRAM_ALLOWED_USERS`参数，以限制能够与您的机器人交互的用户范围。作为安全措施，若未设置该参数，网关将默认拒绝所有用户的访问。
:::

请切勿公开分享您的机器人令牌。一旦该令牌被盗用，请立即通过 BotFather 的 `/revoke` 命令将其撤销。

如需了解更多详情，请参阅[安全文档](/user-guide/security)。此外，您还可以采用[私信配对功能](/user-guide/messaging#dm-pairing-alternative-to-allowlists)，以更灵活的方式实现用户授权。
