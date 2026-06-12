---
sidebar_position: 6
title: "Signal"
description: "Set up Hermes Agent as a Signal messenger bot via signal-cli daemon"
---

# Signal 设置

Hermes 通过以 HTTP 模式运行的 [signal-cli](https://github.com/AsamK/signal-cli) 守护进程与 Signal 进行连接。该适配器通过 SSE（服务器推送事件）实时传输消息，并通过 JSON-RPC 发送响应。

Signal 是最注重隐私的主流即时通讯工具——默认采用端到端加密，协议开源，且几乎不收集元数据。因此，它非常适合对安全性要求较高的智能体工作流程。

:::info 无需新增 Python 依赖项
Signal 适配器所有通信均使用 `httpx`（本身已是 Hermes 的核心依赖项），无需额外安装任何 Python 包。您只需在外部环境中安装 signal-cli 即可。
:::

---

## 先决条件

- **signal-cli** — 基于 Java 的 Signal 客户端（[GitHub](https://github.com/AsamK/signal-cli)）
- **Java 17+** 运行时环境——signal-cli 所需
- 已安装 Signal 的电话号码（用于作为备用设备绑定）

### 安装 signal-cli

```bash
# macOS
brew install signal-cli

# Linux (download latest release)
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} \
  https://github.com/AsamK/signal-cli/releases/latest | sed 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}.tar.gz"
sudo tar xf "signal-cli-${VERSION}.tar.gz" -C /opt
sudo ln -sf "/opt/signal-cli-${VERSION}/bin/signal-cli" /usr/local/bin/
```

:::警告
signal-cli **并不**包含在 apt 或 snap 的软件仓库中。上述 Linux 安装包是直接从 [GitHub 发布页面](https://github.com/AsamK/signal-cli/releases) 下载的。
:::

---

## 第 1 步：关联您的 Signal 账户

Signal-cli 的运作方式类似**关联设备**——类似于 WhatsApp Web，但专为 Signal 设计。您的手机始终是主设备。

```bash
# Generate a linking URI (displays a QR code or link)
signal-cli link -n "HermesAgent"
```

1. 在手机上打开 **Signal** 应用。
2. 进入 **设置 → 已关联设备**。
3. 点击 **关联新设备**。
4. 扫描二维码或输入 URI 地址。

---

## 第 2 步：启动 signal-cli 守护进程

```bash
# Replace +1234567890 with your Signal phone number (E.164 format)
signal-cli --account +1234567890 daemon --http 127.0.0.1:8080
```

:::提示
请让该进程在后台持续运行。您可以使用 `systemd`、`tmux`、`screen`，或将其作为服务来启动。
:::

验证其运行状态：

```bash
curl http://127.0.0.1:8080/api/v1/check
# Should return: {"versions":{"signal-cli":...}}
```

## 第 3 步：配置 Hermes

最简单的方法：

```bash
hermes gateway setup
```

从平台菜单中选择**Signal**。向导将执行以下操作：

1. 检查是否已安装 signal-cli
2. 提示输入 HTTP URL（默认值为 `http://127.0.0.1:8080`）
3. 测试与后台服务的连接性
4. 要求输入您的账户电话号码
5. 配置允许使用的用户及访问策略

### 手动配置

在 `~/.hermes/.env` 文件中添加相应内容：

```bash
# Required
SIGNAL_HTTP_URL=http://127.0.0.1:8080
SIGNAL_ACCOUNT=+1234567890

# Security (recommended)
SIGNAL_ALLOWED_USERS=+1234567890,+0987654321    # Comma-separated E.164 numbers or UUIDs

# Optional
SIGNAL_GROUP_ALLOWED_USERS=groupId1,groupId2     # Enable groups (omit to disable, * for all)
SIGNAL_HOME_CHANNEL=+1234567890                  # Default delivery target for cron jobs
```

接着启动网关：

```bash
hermes gateway              # Foreground
hermes gateway install      # Install as a user service
sudo hermes gateway install --system   # Linux only: boot-time system service
```

## 访问控制

### 私信访问

私信访问遵循与所有其他 Hermes 平台相同的规则：

1. **设置了 `SIGNAL_ALLOWED_USERS`** → 仅允许列表中的用户发送消息  
2. **未设置允许列表** → 未知用户会收到一个私信配对码（需通过 `hermes pairing approve signal CODE` 才能授权）  
3. **设置了 `SIGNAL_ALLOW_ALL_USERS=true`** → 任何用户均可发送消息（请谨慎使用）

### 群组访问

群组访问由环境变量 `SIGNAL_GROUP_ALLOWED_USERS` 控制：

| 配置方式 | 行为说明 |
|----------|----------|
| 未设置（默认值） | 所有群组消息都会被忽略，机器人仅响应私信。 |
| 指定群组 ID | 仅监控列出的群组（例如 `groupId1,groupId2`）。 |
| 设置为 `*` | 机器人会在其所属的任何群组中响应消息。 |

---

## 功能特性

### 附件传输

该适配器支持双向发送和接收媒体文件。

**接收端**（用户 → 机器人）：
- **图片** — PNG、JPEG、GIF、WebP（通过特殊字节自动识别）
- **音频** — MP3、OGG、WAV、M4A（若配置了 Whisper，语音消息会被转录为文本）
- **文档** — PDF、ZIP 及其他文件类型

**发送端**（机器人 → 用户）：
机器人可通过响应中的 `MEDIA:` 标签发送媒体文件。支持的传输方式包括：

- **图片** — `send_multiple_images` 和 `send_image_file` 可将 PNG、JPEG、GIF、WebP 作为原生 Signal 附件发送
- **语音** — `send_voice` 可将音频文件（OGG、MP3、WAV、M4A、AAC）作为附件发送
- **视频** — `send_video` 可发送 MP4 视频文件
- **文档** — `send_document` 可发送任何类型的文件（PDF、ZIP 等）

所有发送的媒体文件均通过 Signal 的标准附件 API 处理。与某些平台不同，Signal 在协议层面上不会区分语音消息和文件附件。

附件大小限制：**100 MB**（双向均适用）。
:::warning
**Signal 服务器会对附件上传进行速率限制**，该适配器会使用调度机制，将多张图片分批处理（每批32张），并控制上传速度以符合 Signal 服务器的政策。
:::

### 原生格式、引用回复与表情反应

Signal 消息会以**原生格式**显示，而非直接的 Markdown 字符。该适配器会将 Markdown 格式（如 `**粗体**`、`*斜体*`、`` `代码` ``、`~~删除线~~`、`||剧透||`、标题等）转换为 Signal 的 `bodyRanges` 格式，从而使文本在接收方的客户端以真实样式显示，而不会呈现为可见的 `**` / `` ` `` 字符。

**引用回复**：当 Hermes 回复某条特定消息时，它会以原生方式回复并引用原消息内容——这与 Signal 用户自行使用“回复”功能时的界面效果一致。对于因接收消息而自动生成的回复，此功能会自动启用。

**表情反应**：机器人可通过标准表情反应 API 对消息作出反应；在 Signal 中，这些反应会以表情符号的形式显示在对应消息上，而非作为额外文本。

以上功能均无需额外配置——在较新版本的 signal-cli 中已默认支持。如果您的 `signal-cli` 版本过旧，Hermes 会回退到纯文本发送方式，并记录一次警告信息。

### 输入中状态指示

机器人在处理消息时会发送输入中状态指示，更新间隔为每8秒一次。

### 工具处理进度显示

Signal 不支持编辑已发送的消息。因此，即使启用了 `/verbose` 参数并保留了非“关闭”模式，Hermes 也会在 Signal 中隐藏网关工具处理进度提示。

您仍可在 CLI 中查看工具处理状态，且最终的 Signal 回复中会包含正常的助手输出内容。如果您需要在聊天中实时查看每项工具的处理进度，请使用支持消息编辑的消息平台。

### 电话号码遮蔽

所有电话号码都会在日志中被自动遮蔽：
- `+15551234567` → `+155****4567`
- 此规则同时适用于 Hermes 网关日志和全局遮蔽系统。

### 单号码设置下的“给自己发消息”功能

如果您将 signal-cli 作为**关联的辅助设备**运行在自己的电话号码上（而非独立的机器人号码），则可以通过 Signal 的“给自己发消息”功能与 Hermes 进行交互。

只需从手机给自己发送一条消息——signal-cli 会捕获该消息，Hermes 会在同一对话中予以回复。

**工作原理：**
- “给自己发消息”的消息会以 `syncMessage.sentMessage` 格式到达
- 适配器会检测到这些消息是发给机器人自身账户的，然后将其作为普通接收消息进行处理
- 回声保护机制（通过发送时间戳追踪）可防止无限循环——机器人的回复会被自动过滤掉

**无需额外配置**。只要 `SIGNAL_ACCOUNT` 设置为您的电话号码，该功能即可自动生效。

### 健康状态监控

适配器会持续监控 SSE 连接，若出现以下情况会自动重新连接：
- 连接中断（采用指数退避策略：2秒 → 60秒）
- 120秒内无任何活动（此时会向 signal-cli 发送检测请求）

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 设置过程中出现 **“无法连接到 signal-cli”** 错误 | 确保 signal-cli 守护进程正在运行：`signal-cli --account +YOUR_NUMBER daemon --http 127.0.0.1:8080` |
| 未收到消息 | 检查 `SIGNAL_ALLOWED_USERS` 是否已包含发送方号码的 E.164 格式地址（需带有 `+` 前缀） |
| 出现 **“PATH 中未找到 signal-cli”** 错误 | 安装 signal-cli 并确保其已在系统 PATH 中，或使用 Docker 运行 |
| 连接频繁中断 | 查看 signal-cli 的日志以查找错误原因。同时确认已安装 Java 17 或更高版本。 |
| 群组消息被忽略 | 通过 `SIGNAL_GROUP_ALLOWED_USERS` 指定具体的群组 ID，或设置为 `*` 以允许所有群组 |
| 机器人不对任何人响应 | 配置 `SIGNAL_ALLOWED_USERS`，使用私信配对功能，或若希望开放更多访问权限，则通过网关策略明确允许所有用户 |
| 出现重复消息 | 确保您的电话号码上仅有一个 signal-cli 实例在监听 |

---

## 安全性

:::warning
**务必配置访问控制措施**。默认情况下，机器人拥有终端级访问权限。为确保安全，若未设置 `SIGNAL_ALLOWED_USERS` 或未进行私信配对，网关会拒绝所有接收到的消息。
:::

- 所有日志输出中的电话号码都会被遮蔽
- 建议通过私信配对或明确的允许列表来安全地引导新用户使用
- 除非确实需要群组功能，否则请保持群组关闭状态；如需使用群组，请仅允许您信任的群组加入
- Signal 的端到端加密可保护消息在传输过程中的内容安全
- `~/.local/share/signal-cli/` 目录中的 signal-cli 会话数据包含账户凭证——请像保护密码一样妥善保管

---

## 环境变量参考

| 变量名 | 是否必填 | 默认值 | 说明 |
|--------|----------|--------|------|
| `SIGNAL_HTTP_URL` | 是 | — | signal-cli 的 HTTP 接口地址 |
| `SIGNAL_ACCOUNT` | 是 | — | 机器人的电话号码（E.164 格式） |
| `SIGNAL_ALLOWED_USERS` | 否 | — | 用逗号分隔的电话号码/UUID 列表 |
| `SIGNAL_GROUP_ALLOWED_USERS` | 否 | — | 需要监控的群组 ID，或设置为 `*` 表示允许所有群组（留空则表示禁用群组） |
| `SIGNAL_ALLOW_ALL_USERS` | 否 | `false` | 允许任何用户进行交互（跳过允许列表检查） |
| `SIGNAL_HOME_CHANNEL` | 否 | — | cron 作业的默认发送目标频道 |
