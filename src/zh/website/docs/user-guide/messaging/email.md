---
sidebar_position: 7
title: "Email"
description: "Set up Hermes Agent as an email assistant via IMAP/SMTP"
---

# 邮件设置

Hermes 可以通过标准的 IMAP 和 SMTP 协议接收并回复邮件。只需将邮件发送到代理的地址，它就会在原邮件线程中回复——无需特殊的客户端或机器人 API。该功能支持 Gmail、Outlook、Yahoo、Fastmail 以及任何支持 IMAP/SMTP 的邮件服务提供商。

:::info 仅限网关适配器：无外部依赖
本页面介绍的是邮件网关适配器，它使用 Python 自带的 `imaplib`、`smtplib` 和 `email` 模块。此路径无需额外的软件包或外部服务。
:::

这与预装的 [Himalaya 邮件技能](/docs/user-guide/skills/bundled/email/email-himalaya) 是不同的，后者允许代理通过终端命令管理邮件，需要使用外部的 `himalaya` CLI 以及 Himalaya 配置文件。

| 使用场景 | 需要配置的内容 | 外部依赖 |
|---|---|---|
| 允许用户给 Hermes 代理发送邮件并接收回复 | 本页面中的邮件网关适配器 | 仅需一个支持 IMAP/SMTP 的邮件账户 |
| 允许代理通过终端工具查看、撰写、移动及管理邮箱中的邮件 | Himalaya 邮件技能 | `himalaya` CLI 以及 `~/.config/himalaya/config.toml` 文件 |

---

## 先决条件

- 为你的 Hermes 代理准备一个专用的邮件账户（请勿使用个人邮箱）
- 确保该邮件账户已启用 IMAP 功能
- 如果使用 Gmail 或其他需要双重认证的邮件服务提供商，则需准备应用密码

### Gmail 设置

1. 在你的 Google 账户中开启双重认证
2. 访问 [应用密码](https://myaccount.google.com/apppasswords)
3. 创建一个新的应用密码（选择“邮件”或“其他”）
4. 复制生成的 16 位密码——之后将使用此密码代替常规密码

### Outlook / Microsoft 365

1. 访问 [安全设置](https://account.microsoft.com/security)
2. 若尚未开启双重认证，则进行开启
3. 在“其他安全选项”中创建应用密码
4. IMAP 主机地址：`outlook.office365.com`，SMTP 主机地址：`smtp.office365.com`

### 其他邮件服务提供商

大多数邮件服务提供商都支持 IMAP/SMTP。请查阅相应提供商的文档，了解以下信息：
- IMAP 主机地址和端口（通常为带有 SSL 的 993 端口）
- SMTP 主机地址和端口（通常为带有 STARTTLS 的 587 端口）
- 是否需要应用密码

---

## 第一步：配置 Hermes

最简单的方法：

```bash
hermes gateway setup
```

从平台菜单中选择**Email**。向导会提示您输入电子邮件地址、密码、IMAP/SMTP服务器以及允许的发送方。

### 手动配置

将其添加到 `~/.hermes/.env` 文件中：

```bash
# Required
EMAIL_ADDRESS=hermes@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop    # App password (not your regular password)
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_SMTP_HOST=smtp.gmail.com

# Security (recommended)
EMAIL_ALLOWED_USERS=your@email.com,colleague@work.com

# Optional
EMAIL_IMAP_PORT=993                    # Default: 993 (IMAP SSL)
EMAIL_SMTP_PORT=587                    # Default: 587 (SMTP STARTTLS)
EMAIL_POLL_INTERVAL=15                 # Seconds between inbox checks (default: 15)
EMAIL_HOME_ADDRESS=your@email.com      # Default delivery target for cron jobs
```

## 第 2 步：启动网关

```bash
hermes gateway              # Run in foreground
hermes gateway install      # Install as a user service
sudo hermes gateway install --system   # Linux only: boot-time system service
```

在启动时，该适配器会执行以下操作：
1. 测试 IMAP 和 SMTP 连接
2. 将所有现有的收件箱邮件标记为“已读”（仅处理新邮件）
3. 开始轮询新邮件

---

## 工作原理

### 接收邮件

该适配器会以可配置的间隔（默认为 15 秒）轮询 IMAP 收件箱中的未读邮件。对于每封新邮件：
- **主题行**会被作为上下文信息包含在内（例如：`[主题：部署到生产环境]`）
- **回复邮件**（主题行以 `Re:` 开头）会省略主题前缀——因为其对话上下文已明确
- **附件**会被本地缓存：
  - 图片（JPEG、PNG、GIF、WebP）→ 可供视觉分析工具使用
  - 文档（PDF、ZIP 等）→ 可用于文件访问
- **仅包含 HTML 格式的邮件**会去掉标签以便提取纯文本
- **自发邮件**会被过滤掉，以避免回复循环
- **自动发送/无需回复的发送方**会被直接忽略——包括 `noreply@`、`mailer-daemon@`、`bounce@`、`no-reply@`，以及带有 `Auto-Submitted`、`Precedence: bulk` 或 `List-Unsubscribe` 标头的邮件

### 发送回复

回复会通过 SMTP 以正确的邮件对话结构发送：
- **In-Reply-To** 和 **References** 标头用于维护对话上下文
- 主题行会保留 `Re:` 前缀（不会出现双 `Re: Re:` 的情况）
- **Message-ID** 会使用代理的域名生成
- 回复内容以纯文本（UTF-8 编码）形式发送

### 文件附件

该代理可以在回复中发送文件附件。只需在回复内容中加入 `MEDIA:/path/to/file`，该文件就会作为附件附在发出的邮件中。

### 跳过附件

如需忽略所有接收到的附件（出于恶意软件防护或节省带宽的考虑），可在 `config.yaml` 文件中进行相应设置：

```yaml
platforms:
  email:
    skip_attachments: true
```

启用该功能后，在解码邮件内容之前，附件及内嵌内容将被跳过处理。而邮件正文仍会按常规方式被处理。

---

## 访问控制

邮件的访问控制规则与其他所有Hermes平台一致：

1. **设置了`EMAIL_ALLOWED_USERS`** → 仅处理来自这些地址的邮件
2. **未设置允许列表** → 未知发件人将收到配对码
3. **`EMAIL_ALLOW_ALL_USERS=true`** → 接受所有发件人的邮件（请谨慎使用）

:::warning
**务必配置`EMAIL_ALLOWED_USERS`。** 如果不设置此参数，任何知晓代理邮箱地址的人都可以发送指令。默认情况下，代理拥有终端访问权限。
:::

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 启动时出现“IMAP连接失败” | 检查`EMAIL_IMAP_HOST`和`EMAIL_IMAP_PORT`的值。确保账户已启用IMAP功能。对于Gmail，需在“设置”→“转发与POP/IMAP”中开启该功能。 |
| 启动时出现“SMTP连接失败” | 检查`EMAIL_SMTP_HOST`和`EMAIL_SMTP_PORT`的值。确认密码正确（Gmail需使用应用专用密码）。 |
| 无法接收邮件 | 检查`EMAIL_ALLOWED_USERS`是否包含发件人的邮箱地址。同时查看垃圾邮件文件夹——某些邮件服务商会将自动回复标记为垃圾邮件。 |
| 出现“身份验证失败”错误 | 对于Gmail，必须使用应用专用密码，而非普通密码。请先确保已启用双重认证。 |
| 出现重复回复 | 确保仅有一个网关实例正在运行。可查看`hermes gateway status`来确认。 |
| 响应速度缓慢 | 默认的轮询间隔为15秒。可通过设置`EMAIL_POLL_INTERVAL=5`缩短间隔以加快响应速度（但会增加IMAP连接次数）。 |
| 回复邮件未正确按主题分组 | 该适配器使用“回复至”（In-Reply-To）标头。某些邮件客户端（尤其是网页版）可能无法正确处理自动发送的邮件及其主题分组。 |

---

## 安全性

:::warning
**请使用专用邮箱账户。** 千万不要使用个人邮箱——代理会将密码存储在`.env`文件中，并能通过IMAP完全访问收件箱。
:::

- 请使用**应用专用密码**，而非普通密码（对于已启用双重认证的Gmail，这是必需的）
- 设置`EMAIL_ALLOWED_USERS`以限制可与代理交互的用户范围
- 密码存储在`~/.hermes/.env`文件中——请保护好该文件（设置权限为`chmod 600`）
- IMAP默认使用SSL协议（端口993），SMTP默认使用STARTTLS协议（端口587）——所有连接均为加密传输

---

## 环境变量参考

| 变量 | 是否必填 | 默认值 | 说明 |
|------|----------|--------|------|
| `EMAIL_ADDRESS` | 是 | — | 代理的邮箱地址 |
| `EMAIL_PASSWORD` | 是 | — | 邮箱密码或应用专用密码 |
| `EMAIL_IMAP_HOST` | 是 | — | IMAP服务器主机地址（例如`imap.gmail.com`） |
| `EMAIL_SMTP_HOST` | 是 | — | SMTP服务器主机地址（例如`smtp.gmail.com`） |
| `EMAIL_IMAP_PORT` | 否 | `993` | IMAP服务器端口 |
| `EMAIL_SMTP_PORT` | 否 | `587` | SMTP服务器端口 |
| `EMAIL_POLL_INTERVAL` | 否 | `15` | 检查收件箱的间隔时间（秒） |
| `EMAIL_ALLOWED_USERS` | 否 | — | 以逗号分隔的允许发送邮件的地址列表 |
| `EMAIL_HOME_ADDRESS` | 否 | — | 定时任务邮件的默认发送目标地址 |
| `EMAIL_ALLOW_ALL_USERS` | 否 | `false` | 允许所有发件人发送邮件（不推荐） |
