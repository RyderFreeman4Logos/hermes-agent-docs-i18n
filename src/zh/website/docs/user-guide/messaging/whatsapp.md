---
sidebar_position: 5
title: "WhatsApp"
description: "Set up Hermes Agent as a WhatsApp bot via the built-in Baileys bridge"
---

# WhatsApp 设置

Hermes 通过基于 **Baileys** 的内置桥接方式与 WhatsApp 连接。该方案通过模拟 WhatsApp Web 会话来实现功能，**并不**使用官方的 WhatsApp Business API，因此无需 Meta 开发者账号或企业认证。

> 运行 `hermes gateway setup` 命令，然后选择 **WhatsApp** 即可获得逐步指导。

:::提示 两种 WhatsApp 集成方式
本页面介绍的是 **Baileys 桥接** 方式——设置快捷、适用于个人账号、无需公开 URL，且不存在被封禁的风险。

如果您正在运行真正的企业机器人并追求更高稳定性，建议参考 **[WhatsApp Business Cloud API 指南](./whatsapp-cloud.md)**。这是 Meta 官方支持的方案：无账号封禁风险，但需要 Meta 企业账号以及公开的 webhook URL。

如有必要，这两种适配器也可以针对不同的电话号码同时运行。
:::

:::警告 非官方 API — 存在封禁风险
WhatsApp **并未**正式支持 Business API 之外的第三方机器人。使用第三方桥接可能会带来一定的账号受限风险。为降低风险，请注意：
- 为机器人使用**专用电话号码**（而非个人号码）
- **避免发送大量消息或垃圾信息**，保持正常对话式使用频率
- **不要自动向未主动发消息的用户发送信息**

:::warning WhatsApp Web 协议更新提醒  
WhatsApp 会定期更新其 Web 协议，这可能会导致与第三方桥接工具的兼容性出现暂时性问题。一旦发生这种情况，Hermes 会自动更新对应的桥接依赖。如果 WhatsApp 更新后机器人停止运行，请拉取最新版本的 Hermes 并重新配对。  

:::  

## 两种运行模式  

| 模式 | 工作原理 | 适用场景 |  
|------|----------|----------|  
| **独立机器人号码**（推荐） | 为机器人专用一个电话号码，用户直接向该号码发送消息。 | 用户体验更佳，支持多用户使用，封禁风险更低 |  
| **个人自聊模式** | 使用你自己的 WhatsApp 账号，通过给自己发消息来与机器人交互。 | 设置简单，适合单人使用或测试场景 |  

---

## 先决条件  

- **Node.js v18+** 及 **npm** —— WhatsApp 桥接工具以 Node.js 进程形式运行  
- **安装了 WhatsApp 的手机**（用于扫描二维码）  

与早期的浏览器驱动型桥接工具不同，当前基于 Baileys 的桥接工具无需本地安装 Chromium 或 Puppeteer 相关组件。  

---

## 第一步：运行设置向导

```bash
hermes whatsapp
```

向导将执行以下操作：

1. 询问您希望使用哪种模式（**机器人模式**或**自我对话模式**）
2. 如有需要，安装桥接依赖项
3. 在您的终端中显示一个**二维码**
4. 等待您扫描该二维码

**如何扫描二维码：**

1. 在手机上打开 WhatsApp
2. 进入**设置 → 已关联设备**
3. 点击**关联设备**
4. 将手机摄像头对准终端中的二维码

一旦完成配对，向导会确认连接并退出。您的会话将自动保存。

:::提示
如果二维码显示模糊不清，请确保您的终端宽度至少为60列，并且支持Unicode字符集。您也可以尝试使用其他终端模拟器。
:::

---

## 第2步：获取第二个电话号码（机器人模式）

在机器人模式下，您需要一个尚未在 WhatsApp 中注册的电话号码。有以下三种选择：

| 选项 | 费用 | 备注 |
|------|------|-------|
| **Google Voice** | 免费 | 仅限美国用户。可在[voice.google.com](https://voice.google.com)获取号码。通过 Google Voice 应用通过短信验证 WhatsApp。 |
| **预付费SIM卡** | 一次性5–15美元 | 任何运营商均可。开通后验证 WhatsApp，之后该SIM卡可放置一旁不用。号码必须保持活跃状态（需每90天拨打一次电话）。 |
| **VoIP服务** | 免费–每月5美元 | 如TextNow、TextFree等。部分WhatsApp会屏蔽某些VoIP号码——如果第一个不行，可以尝试其他服务。 |

获取号码后：

1. 在手机上安装 WhatsApp（或使用支持双SIM卡的WhatsApp Business应用）
2. 在 WhatsApp中注册新号码
3. 运行 `hermes whatsapp` 命令，然后扫描该 WhatsApp 账户的二维码

## 第 3 步：配置 Hermes

在您的 `~/.hermes/.env` 文件中添加以下内容：

```bash
# Required
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot                          # "bot" or "self-chat"

# Access control — pick ONE of these options:
WHATSAPP_ALLOWED_USERS=15551234567         # Comma-separated phone numbers (with country code, no +)
# WHATSAPP_ALLOWED_USERS=*                 # OR use * to allow everyone
# WHATSAPP_ALLOW_ALL_USERS=true            # OR set this flag instead (same effect as *)
```

:::提示：允许所有用户的简写方式  
将 `WHATSAPP_ALLOWED_USERS=*` 设为该值即可允许**所有**发送者发送消息（相当于 `WHATSAPP_ALLOW_ALL_USERS=true`）。  
此设置与 [Signal 群组白名单机制](/reference/environment-variables) 保持一致。  
如需使用配对流程，则可删除这两个变量，转而依赖 [私信配对系统](/user-guide/security#dm-pairing-system)。  
:::

`~/.hermes/config.yaml` 中的可选行为设置：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- 全局默认值为 `unauthorized_dm_behavior: pair`，即向未知的私信发送者发送配对码。  
- 设置为 `whatsapp.unauthorized_dm_behavior: ignore` 后，WhatsApp 会对未经授权的私信保持沉默，这通常是处理私人号码私信的更佳选择。  

随后启动网关：

```bash
hermes gateway              # Foreground
hermes gateway install      # Install as a user service
sudo hermes gateway install --system   # Linux only: boot-time system service
```

网关会自动使用已保存的会话来启动 WhatsApp 桥接功能。

---

## 会话持久化

Baileys 桥接工具会将会话数据保存在 `~/.hermes/platforms/whatsapp/session` 目录下。这意味着：

- **会话可在重启后保留**——无需每次都重新扫描二维码
- 会话数据中包含加密密钥及设备凭证
- **切勿共享或提交该会话目录**——它会导致他人完全控制您的 WhatsApp 账户

---

## 重新配对

如果会话中断（如手机重置、WhatsApp 更新或手动断开连接），您会在网关日志中看到连接错误。要解决此问题：

```bash
hermes whatsapp
```

此操作会生成一个新的二维码。再次扫描该二维码即可重新建立会话。网关会通过自动重连机制，处理**暂时性**的断开连接情况（如网络短暂波动、手机暂时断网等）。

---

## 语音消息

Hermes 支持在 WhatsApp 上发送语音消息：

- **接收端**：语音消息（`.ogg` opus 格式）会通过配置好的文本转语音服务自动转写，可选服务包括本地的 `faster-whisper`、Groq Whisper（需提供 `GROQ_API_KEY`）或 OpenAI Whisper（需提供 `VOICE_TOOLS_OPENAI_KEY`）。
- **发送端**：文本转语音生成的回复会以 MP3 音频文件的形式作为附件发送。
- 默认情况下，智能体的回复前会加上“⚕ **Hermes Agent**”前缀。您可以在 `config.yaml` 文件中自定义或禁用此设置。

```yaml
# ~/.hermes/config.yaml
whatsapp:
  reply_prefix: ""                          # Empty string disables the header
  # reply_prefix: "🤖 *My Bot*\n──────\n"  # Custom prefix (supports \n for newlines)
  send_read_receipts: false                 # Mark accepted inbound messages as read (blue ticks)
```

当 `send_read_receipts` 设置为 `true` 时，适配器会在完成私信/群组/提及消息的过滤后，将符合策略要求的已接收消息标记为已读。而被拒绝的消息（例如来自未列入允许列表的发送方）则不会被标记为已读。出于隐私考虑，该功能默认处于禁用状态。更改此设置后，下次连接时桥接子进程将会自动重启。

---

## 消息格式与传递

WhatsApp 支持**流式（渐进式）响应**——与 Discord 和 Telegram 一样，当 AI 生成文本时，机器人会实时编辑消息内容。从传递能力角度来看，WhatsApp 在内部被归类为中等层级平台。

### 分块处理

较长的回复会自动按每块 **4,096 个字符**（即 WhatsApp 的实际显示限制）拆分成多条消息。您无需进行任何配置——网关会负责拆分并依次发送这些消息块。

### 兼容 WhatsApp 的 Markdown 格式

AI 响应中的标准 Markdown 会自动转换为 WhatsApp 的原生格式：

| Markdown | WhatsApp 显示形式 | 最终呈现效果 |
|----------|------------------|--------------|
| `**bold**` | `*bold*` | **bold** |
| `~~strikethrough~~` | `~strikethrough~` | ~~strikethrough~~ |
| `# Heading` | `*Heading*` | 加粗文本（WhatsApp 无原生标题功能） |
| `[link text](url)` | `link text (url)` | 行内链接 |

由于 WhatsApp 原生支持三反引号格式，代码块和行内代码将保持原样不变。

### 工具处理进度显示

当智能体调用各类工具（如网络搜索、文件操作等）时，WhatsApp会显示实时的进度指示器，告知当前正在运行的工具是哪一个。此功能为默认启用状态，无需任何配置。

### 原生投票、以投票形式澄清问题以及位置信息

Baileys桥接适配器（机器人模式）支持多种WhatsApp原生消息类型：

- **投票**——智能体可通过桥接器的 `/send-poll` 接口发送原生WhatsApp投票（包含问题及选项）。用户的投票结果会直接反馈到对话中。
- **将澄清问题以投票形式呈现**——当智能体提出多项选择式的澄清问题时，它会以原生单选投票的形式展示；用户点击选项即可回答问题。如果投票发送失败，适配器会自动回退为纯文本问题。批准提示**绝不会**被转换为投票形式——投票仅用于真正的多项选择式澄清问题。
- **位置标记**——智能体可通过 `/send-location` 接口发送原生位置标记（包含纬度/经度，可选名称/地址）；而接收到的共享位置信息（包括实时位置）则会以位置消息的形式传递给智能体。

所有这些功能在机器人（Baileys）模式下均可直接使用，无需任何配置。 

### 消息批量处理（防抖机制）

WhatsApp会逐条发送消息，因此如果出现大量连续消息（如批量转发、拆分粘贴的内容或多行文本），系统会针对每一条消息单独调用智能体——这不仅会造成令牌浪费，还会生成多个相互独立的回复。该适配器会将同一对话中的连续文本消息暂存起来，在短暂的静默期过后（默认为**5秒**，对于特别长的内容可延长至**10秒**）将它们作为一个整体请求发送出去。您可以通过`config.yaml`文件对相关参数进行调整：

```yaml
# ~/.hermes/config.yaml
gateway:
  platforms:
    whatsapp:
      extra:
        text_batch_delay_seconds: 5.0         # quiet period before flushing a batch
        text_batch_split_delay_seconds: 10.0  # extended delay near the split threshold
```

将 `text_batch_delay_seconds: 0` 设置为该值即可立即发送每条消息（此时将禁用批量处理功能）。

---

## 故障排除

| Problem | Solution |
|---------|----------|
| **QR code not scanning** | Ensure terminal is wide enough (60+ columns). Try a different terminal. Make sure you're scanning from the correct WhatsApp account (bot number, not personal). |
| **QR code expires** | QR codes refresh every ~20 seconds. If it times out, restart `hermes whatsapp`. |
| **Session not persisting** | Check that `~/.hermes/platforms/whatsapp/session` exists and is writable. If containerized, mount it as a persistent volume. |
| **Logged out unexpectedly** | WhatsApp unlinks devices after long inactivity. Keep the phone on and connected to the network, then re-pair with `hermes whatsapp` if needed. |
| **Bridge crashes or reconnect loops** | Restart the gateway, update Hermes, and re-pair if the session was invalidated by a WhatsApp protocol change. |
| **Bot stops working after WhatsApp update** | Update Hermes to get the latest bridge version, then re-pair. |
| **macOS: "Node.js not installed" but node works in terminal** | launchd services don't inherit your shell PATH. Run `hermes gateway install` to re-snapshot your current PATH into the plist, then `hermes gateway start`. See the [Gateway Service docs](./index.md#macos-launchd) for details. |
| **Messages not being received** | Verify `WHATSAPP_ALLOWED_USERS` includes the sender's number (with country code, no `+` or spaces), or set it to `*` to allow everyone. Set `WHATSAPP_DEBUG=true` in `.env` and restart the gateway to see raw message events in `bridge.log`. |
| **Bot replies to strangers with a pairing code** | Set `whatsapp.unauthorized_dm_behavior: ignore` in `~/.hermes/config.yaml` if you want unauthorized DMs to be silently ignored instead. |

## 安全性

:::warning
在正式上线之前，请务必**配置访问控制**。请设置 `WHATSAPP_ALLOWED_USERS` 参数，填入具体的电话号码（需包含国家代码，且不能带有 `+` 符号）；若希望允许所有人发送消息，则可使用 `*`；或者直接将 `WHATSAPP_ALLOW_ALL_USERS` 设置为 `true`。若未进行任何配置，出于安全考虑，网关将会**拒绝接收所有 incoming 消息**。
:::

默认情况下，未经授权的私信仍会收到配对码回复。如果您希望某个私人 WhatsApp 号码对陌生人完全保持沉默，请进行如下设置：

```yaml
whatsapp:
  unauthorized_dm_behavior: ignore
```

- `~/.hermes/platforms/whatsapp/session` 目录中存储着完整的会话凭证——请像保护密码一样严格保密。  
- 设置文件权限：`chmod 700 ~/.hermes/platforms/whatsapp/session`  
- 为机器人使用**专用电话号码**，以避免风险波及您的个人账户。  
- 若怀疑账户已被入侵，请在 WhatsApp 的“设置”→“关联设备”中解除该设备的绑定。  
- 日志中的电话号码会进行部分匿名处理，但仍建议您查看相关的日志保留政策。
