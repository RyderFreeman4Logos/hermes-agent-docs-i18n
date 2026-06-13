---
sidebar_position: 5
title: "WhatsApp"
description: "Set up Hermes Agent as a WhatsApp bot via the built-in Baileys bridge"
---

# WhatsApp 设置指南

Hermes 通过基于 **Baileys** 的内置桥接组件与 WhatsApp 连接。该方式通过模拟 WhatsApp Web 会话来实现功能，**并不**使用官方的 WhatsApp Business API，因此无需 Meta 开发者账号或企业认证。

> 运行 `hermes gateway setup` 命令，然后选择 **WhatsApp**，即可按照引导完成设置。

:::提示：两种 WhatsApp 集成方式
本页面介绍的是 **Baileys 桥接方案**——设置快捷、适用于个人账号、无需公开 URL，且不存在账号被封的风险。

如果您正在运行正式的企业机器人并追求更高的稳定性，建议参考 **[WhatsApp Business Cloud API 使用指南](./whatsapp-cloud.md)**。这是 Meta 官方支持的方案：无账号封禁风险，但需要拥有 Meta 企业账号以及公开的 webhook URL。

如有必要，这两种适配器也可以针对不同的电话号码同时运行。

:::

:::警告：非官方 API——存在账号封禁风险
WhatsApp 并未正式支持 Business API 之外的第三方机器人。使用第三方桥接可能会带来一定的账号受限风险。为降低风险，请注意：
- 为机器人使用**专用电话号码**（而非个人号码）
- **避免发送大量消息或垃圾信息**，保持正常对话式交流
- **不要自动向未主动发消息的用户发送信息**

:::

:::警告：WhatsApp Web 协议更新
WhatsApp 会定期更新其 Web 协议，这可能会导致与第三方桥接的兼容性出现暂时性问题。遇到这种情况时，Hermes 会自动更新相应的桥接依赖项。如果 WhatsApp 更新后机器人停止工作，请下载最新版本的 Hermes 并重新配对。

:::

## 两种运行模式

| 模式 | 工作原理 | 适用场景 |
|------|----------|----------|
| **独立机器人号码**（推荐） | 为机器人专用一个电话号码，用户直接向该号码发送消息。 | 用户体验更佳、支持多用户使用、账号封禁风险更低 |
| **个人自聊模式** | 使用您自己的 WhatsApp 账号，通过给自己发消息来与智能体交流。 | 设置简单、仅适合单用户使用、适用于测试阶段 |

---

## 前提条件

- **Node.js v18+** 及 **npm**——WhatsApp 桥接组件以 Node.js 进程的形式运行
- **安装了 WhatsApp 的手机**（用于扫描二维码）

与旧版的浏览器驱动型桥接不同，当前基于 Baileys 的桥接无需依赖本地的 Chromium 或 Puppeteer 环境。

---

## 第一步：运行设置向导

```bash
hermes whatsapp
```

向导将执行以下操作：

1. 询问您希望使用哪种模式（**机器人模式**或**自我对话模式**）
2. 如有需要，安装桥接依赖项
3. 在终端中显示一个**二维码**
4. 等待您扫描该二维码

**如何扫描二维码：**

1. 在手机上打开 WhatsApp
2. 进入**设置 → 已关联设备**
3. 点击**关联设备**
4. 将手机摄像头对准终端中的二维码

一旦完成配对，向导会确认连接并退出。您的会话将会被自动保存。

:::提示
如果二维码显示模糊不清，请确保您的终端宽度至少为60列，并且支持Unicode字符集。您也可以尝试使用其他终端模拟器。
:::

---

## 第2步：获取第二个电话号码（机器人模式）

在机器人模式下，您需要一个尚未在 WhatsApp 中注册的电话号码。有以下三种选择：

| 选项 | 费用 | 备注 |
|------|------|-------|
| **Google Voice** | 免费 | 仅限美国用户。可在[voice.google.com](https://voice.google.com)获取号码。通过 Google Voice 应用通过短信验证 WhatsApp。 |
| **预付费SIM卡** | 一次性5–15美元 | 任何运营商均可。激活后验证 WhatsApp，之后该SIM卡可放置不用。号码必须保持活跃状态（每90天需拨打一次电话）。 |
| **VoIP服务** | 免费–每月5美元 | 如TextNow、TextFree等。部分WhatsApp会屏蔽某些VoIP号码——如果第一个不行，可以尝试其他服务。 |

获取号码后：

1. 在手机上安装 WhatsApp（或使用支持双SIM卡的WhatsApp Business应用）
2. 在 WhatsApp中注册新号码
3. 运行`hermes whatsapp`命令，然后扫描该WhatsApp账户的二维码

---

## 第3步：配置Hermes

在您的`~/.hermes/.env`文件中添加以下内容：

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
将 `WHATSAPP_ALLOWED_USERS=*` 设置为该值即可允许**所有**发送者发送消息（相当于 `WHATSAPP_ALLOW_ALL_USERS=true`）。  
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

此操作会生成一个新的二维码。再次扫描该二维码即可重新建立会话。网关通过内置的重连机制，能够自动处理**暂时性**的断开连接情况（如网络波动、手机短暂离线等）。

---

## 语音消息

Hermes 支持在 WhatsApp 上发送语音消息：

- **接收端**：语音消息（`.ogg` opus 格式）会通过已配置的文本转语音服务自动转写，可选服务包括本地的 `faster-whisper`、Groq Whisper（需提供 `GROQ_API_KEY`）或 OpenAI Whisper（需提供 `VOICE_TOOLS_OPENAI_KEY`）。
- **发送端**：文本转语音生成的回复会以 MP3 音频文件的形式作为附件发送。
- 默认情况下，智能体的回复前会加上“⚕ **Hermes Agent**”前缀。您可以在 `config.yaml` 文件中自定义或禁用此设置。

```yaml
# ~/.hermes/config.yaml
whatsapp:
  reply_prefix: ""                          # Empty string disables the header
  # reply_prefix: "🤖 *My Bot*\n──────\n"  # Custom prefix (supports \n for newlines)
```

## 消息格式与传输

WhatsApp 支持**流式（渐进式）响应**——与 Discord 和 Telegram 一样，当 AI 生成文本时，机器人会实时编辑消息内容。从传输能力来看，WhatsApp 在内部被归类为中等层级平台。

### 分块处理

过长的回复会自动按每块 **4,096 个字符**（即 WhatsApp 的实际显示限制）拆分成多条消息。您无需进行任何配置——网关会自动处理分块，并依次发送这些消息。

### 兼容 WhatsApp 的 Markdown 格式

AI 回复中的标准 Markdown 会自动转换为 WhatsApp 原生的格式：

| Markdown | WhatsApp 显示形式 | 最终呈现效果 |
|----------|------------------|--------------|
| `**bold**` | `*bold*` | **bold** |
| `~~strikethrough~~` | `~strikethrough~` | ~~strikethrough~~ |
| `# Heading` | `*Heading*` | 加粗文本（WhatsApp 无原生标题功能） |
| `[link text](url)` | `link text (url)` | 行内链接 |

由于 WhatsApp 原生支持三反引号格式，代码块和行内代码将保持原样。

### 工具处理进度

当机器人调用工具（如网络搜索、文件操作等）时，WhatsApp 会显示实时进度指示器，告知当前正在运行哪个工具。此功能为默认开启状态，无需额外配置。

### 消息批量发送（防抖机制）

WhatsApp 是逐条发送消息的，因此如果短时间内发送大量内容（如批量转发、粘贴分割的多行文本），可能会导致每次发送都触发一次机器人调用——这不仅会浪费令牌，还会产生多个相互独立的回复。适配器会缓存同一对话中的连续文本消息，在短暂的静默期过后（默认为 **5 秒**，对于非常长的内容可延长至 **10 秒**）将它们合并为一个请求发送。您可以通过 `config.yaml` 文件进行相关调整：

```yaml
# ~/.hermes/config.yaml
gateway:
  platforms:
    whatsapp:
      extra:
        text_batch_delay_seconds: 5.0         # quiet period before flushing a batch
        text_batch_split_delay_seconds: 10.0  # extended delay near the split threshold
```

将 `text_batch_delay_seconds: 0` 设为该值即可立即发送每条消息（此时将禁用批量处理功能）。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| **二维码无法扫描** | 确保终端宽度足够（60列以上），可尝试更换终端。同时确认是从正确的 WhatsApp 账户进行扫描（需使用机器人号码，而非个人号码）。 |
| **二维码过期** | 二维码大约每20秒更新一次。若出现超时情况，请重启 `hermes whatsapp`。 |
| **会话无法持久化** | 检查 `~/.hermes/platforms/whatsapp/session` 文件是否存在且可写。若在容器环境中运行，需将其挂载为持久卷。 |
| **意外登出** | WhatsApp会在长时间无操作后断开设备连接。请保持手机开机并处于网络连接状态，必要时再通过 `hermes whatsapp` 重新配对。 |
| **桥接服务崩溃或不断重连** | 重启网关，更新 Hermes 版本；若因 WhatsApp 协议变更导致会话失效，还需重新进行配对。 |
| **WhatsApp 更新后机器人停止工作** | 请升级 Hermes 以获取最新版本的桥接服务，然后再重新配对。 |
| **macOS系统：显示“未安装Node.js”，但终端中能正常使用Node** | launchd服务不会继承用户的shell路径。请运行 `hermes gateway install` 将当前路径信息重新写入plist文件，之后再执行 `hermes gateway start`。详情可参阅[网关服务文档](./index.md#macos-launchd)。 |
| **无法接收消息** | 请确认 `WHATSAPP_ALLOWED_USERS` 中已包含发件人的号码（需包含国家代码，且不能有“+”号或空格）；如需允许所有人发送消息，可将其设置为 `*`。此外可在 `.env` 文件中设置 `WHATSAPP_DEBUG=true`，重启网关后便能在 `bridge.log` 文件中查看原始消息日志。 |
| **机器人向陌生人回复配对码** | 若希望直接忽略未经授权的私信，可在 `~/.hermes/config.yaml` 中设置 `whatsapp.unauthorized_dm_behavior: ignore`。 |

---

## 安全性

:::warning
在正式上线之前，请务必配置访问控制机制。可通过指定具体的电话号码（包含国家代码，且不带“+”号）来设置 `WHATSAPP_ALLOWED_USERS`；若希望允许所有人发送消息，可使用 `*`；或者直接设置 `WHATSAPP_ALLOW_ALL_USERS=true`。若未进行任何相关配置，网关会出于安全考虑**拒绝接收所有 incoming消息**。
:::

默认情况下，未经授权的私信仍会收到配对码回复。如果您希望某个私人 WhatsApp 号码对陌生人完全保持沉默，可进行如下设置：

```yaml
whatsapp:
  unauthorized_dm_behavior: ignore
```

- `~/.hermes/platforms/whatsapp/session` 目录中存储着完整的会话凭证——请像保护密码一样严格保管它。  
- 设置文件权限：`chmod 700 ~/.hermes/platforms/whatsapp/session`  
- 为机器人使用**专用电话号码**，以避免风险波及您的个人账户。  
- 若怀疑账户遭入侵，请在 WhatsApp 的“设置”→“关联设备”中解除该设备的绑定。  
- 日志中的电话号码会进行部分脱敏处理，但仍建议您查看相关的日志保留政策。
