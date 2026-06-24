---
sidebar_position: 8
sidebar_label: "SMS (Twilio)"
title: "SMS (Twilio)"
description: "Set up Hermes Agent as an SMS chatbot via Twilio"
---

# SMS 设置（Twilio）

Hermes 通过 [Twilio](https://www.twilio.com/) API 实现与短信服务的连接。用户向您的 Twilio 电话号码发送短信，即可获得 AI 回复——体验与 Telegram 或 Discord 类似，但通过标准短信实现。

:::info 共享凭证
短信网关会与可选的 [电话功能插件](/reference/skills-catalog) 共享凭证。如果您已为语音通话或一次性短信配置过 Twilio，该网关将使用相同的 `TWILIO_ACCOUNT_SID`、`TWILIO_AUTH_TOKEN` 和 `TWILIO_PHONE_NUMBER`。
:::

---

## 前提条件

- **Twilio 账户** — [在 twilio.com 注册](https://www.twilio.com/try-twilio)（提供免费试用）
- 具备短信发送功能的 **Twilio 电话号码**
- **可公开访问的服务器** — 短信到达时，Twilio 会将 webhook 发送到您的服务器
- **aiohttp** — `cd ~/.hermes/hermes-agent && uv pip install -e ".[sms]"`

---

## 第 1 步：获取您的 Twilio 凭证

1. 访问 [Twilio 控制台](https://console.twilio.com/)
2. 从控制面板复制您的 **账户 SID** 和 **认证令牌**
3. 转到 **电话号码 → 管理 → 活动号码** — 记下您的 E.164 格式电话号码（例如：`+15551234567`）

---

## 第 2 步：配置 Hermes

### 交互式设置（推荐）

```bash
hermes gateway setup
```

从平台列表中选择**SMS (Twilio)**。向导将会提示您输入相应的凭据。

### 手动设置

将其添加到`~/.hermes/.env`文件中：

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567

# Security: restrict to specific phone numbers (recommended)
SMS_ALLOWED_USERS=+15559876543,+15551112222

# Optional: set a home channel for cron job delivery
SMS_HOME_CHANNEL=+15559876543
```

## 第3步：配置Twilio Webhook

Twilio需要知道应将接收到的消息发送到何处。在[Twilio控制台](https://console.twilio.com/)中：

1. 转至**电话号码 → 管理 → 活动中的号码**
2. 点击您的电话号码
3. 在**消息功能 → 有新消息到达**下方，设置如下参数：
   - **Webhook地址**：`https://your-server:8080/webhooks/twilio`
   - **HTTP方法**：`POST`

:::提示 如何公开您的Webhook
如果您是在本地运行Hermes，建议使用隧道服务来公开该Webhook地址：

```bash
# Using cloudflared
cloudflared tunnel --url http://localhost:8080

# Using ngrok
ngrok http 8080
```

将生成的公开 URL 设置为您的 Twilio webhook 地址。
:::

**请将 `SMS_WEBHOOK_URL` 设置为与在 Twilio 中配置的相同地址。** 这一项对于 Twilio 的签名验证至关重要——若缺少该设置，适配器将无法启动：

```bash
# Must match the webhook URL in your Twilio Console
SMS_WEBHOOK_URL=https://your-server:8080/webhooks/twilio
```

Webhook 端口默认值为 `8080`。如需更改，请使用以下方式：

```bash
SMS_WEBHOOK_PORT=3000
```

## 第4步：启动网关

```bash
hermes gateway
```

您应该会看到：

```
[sms] Twilio webhook server listening on 127.0.0.1:8080, from: +1555***4567
```

如果出现“拒绝启动：需要 SMS_WEBHOOK_URL”这样的提示，请将 `SMS_WEBHOOK_URL` 设置为在 Twilio 控制台配置的公共 URL（详见第 3 步）。

向您的 Twilio 号码发送短信——Hermes 将通过短信进行回复。

---

## 环境变量

| 变量 | 是否必填 | 描述 |
|------|----------|------|
| `TWILIO_ACCOUNT_SID` | 是 | Twilio 账户 SID（以 `AC` 开头） |
| `TWILIO_AUTH_TOKEN` | 是 | Twilio 认证令牌（也用于验证 webhook 签名） |
| `TWILIO_PHONE_NUMBER` | 是 | 您的 Twilio 电话号码（E.164 格式） |
| `SMS_WEBHOOK_URL` | 是 | 用于 Twilio 签名验证的公共 URL——必须与 Twilio 控制台中的 webhook URL 完全一致 |
| `SMS_WEBHOOK_PORT` | 否 | Webhook 监听端口（默认值：`8080`） |
| `SMS_WEBHOOK_HOST` | 否 | Webhook 绑定地址（默认值：`127.0.0.1`） |
| `SMS_INSECURE_NO_SIGNATURE` | 否 | 设置为 `true` 可禁用签名验证（仅适用于本地开发——**不推荐用于生产环境**） |
| `SMS_ALLOWED_USERS` | 否 | 允许发送消息的 E.164 电话号码，以逗号分隔 |
| `SMS_ALLOW_ALL_USERS` | 否 | 设置为 `true` 可允许任何人发送消息（不推荐） |
| `SMS_HOME_CHANNEL` | 否 | 用于定时任务/通知发送的电话号码 |
| `SMS_HOME_CHANNEL_NAME` | 否 | 主通道的显示名称（默认值：`Home`） |

---

## SMS 相关特性

- **仅支持纯文本**——由于短信会将其视为普通字符，因此 Markdown 会被自动移除。
- **1600 字符限制**——过长的回复内容会在自然分隔处（换行符及空格）被拆分为多条消息发送。
- **防止回环**——会忽略来自您自身 Twilio 号码的消息，以避免消息循环。
- **电话号码保密处理**——为保护隐私，日志中的电话号码会被隐藏处理。

---

## 安全性

### Webhook 签名验证

Hermes 通过验证 `X-Twilio-Signature` 标头（采用 HMAC-SHA1 算法）来确认传入的 webhook 确实源自 Twilio，从而防止攻击者注入伪造消息。

**`SMS_WEBHOOK_URL` 是必填项**。请将其设置为在 Twilio 控制台配置的公共 URL。若未设置该值，适配器将无法启动。

对于没有公共 URL 的本地开发环境，您可以禁用签名验证：

```bash
# Local dev only — NOT for production
SMS_INSECURE_NO_SIGNATURE=true
```

### 用户白名单

**默认情况下，网关会拒绝所有用户访问。** 请配置白名单：

```bash
# Recommended: restrict to specific phone numbers
SMS_ALLOWED_USERS=+15559876543,+15551112222

# Or allow all (NOT recommended for bots with terminal access)
SMS_ALLOW_ALL_USERS=true
```

:::warning
短信服务本身不支持内置加密。除非您充分了解其安全风险，否则请勿将敏感操作通过短信进行。对于需要高安全性的场景，建议使用 Signal 或 Telegram。
:::

---

## 故障排除

### 消息无法送达

1. 确认您的 Twilio webhook URL 正确且可公开访问
2. 核对 `TWILIO_ACCOUNT_SID` 和 `TWILIO_AUTH_TOKEN` 的值是否正确
3. 查看 Twilio 控制台 → **监控 → 日志 → 消息传递**，查找相关的传输错误
4. 确保您的电话号码已添加到 `SMS_ALLOWED_USERS` 列表中（或设置 `SMS_ALLOW_ALL_USERS=true`）

### 回复消息无法发送

1. 检查 `TWILIO_PHONE_NUMBER` 的设置是否正确（需为带 `+` 号的 E.164 格式）
2. 确认您的 Twilio 账户拥有支持发送短信的号码
3. 查看 Hermes 网关日志，查找与 Twilio API 相关的错误信息

### Webhook 端口冲突

如果端口 8080 已被占用，请更换其他端口：

```bash
SMS_WEBHOOK_PORT=3001
```

请在 Twilio 控制台中更新 webhook URL，使其与之保持一致。
