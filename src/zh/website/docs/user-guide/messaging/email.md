---
sidebar_position: 7
title: "Email"
description: "Set up Hermes Agent as an email assistant via IMAP/SMTP"
---

# 邮件设置

Hermes 可以通过标准的 IMAP 和 SMTP 协议接收并回复邮件。只需将邮件发送至代理的地址，它就会在原邮件线程中回复——无需任何专用客户端或机器人 API。该功能支持 Gmail、Outlook、Yahoo、Fastmail 以及所有支持 IMAP/SMTP 的邮件服务提供商。

:::info 仅限网关适配器：无外部依赖
本页面介绍的是邮件网关适配器，它利用 Python 自带的 `imaplib`、`smtplib` 和 `email` 模块。使用此路径无需额外的软件包或外部服务。
:::

请注意，这与预装的内置 [Himalaya 邮件技能](/docs/user-guide/skills/bundled/email/email-himalaya) 是不同的。后者允许代理通过终端命令管理邮件，需要使用外部的 `himalaya` CLI 以及 Himalaya 配置文件。

| 使用场景 | 需要配置的内容 | 外部依赖 |
|---|---|---|
| 允许用户向 Hermes 代理发送邮件并接收回复 | 本页面中的邮件网关适配器 | 仅需一个支持 IMAP/SMTP 的邮件账户 |
| 允许代理通过终端工具查看、撰写、移动及管理邮箱中的邮件 | Himalaya 邮件技能 | `himalaya` CLI 以及 `~/.config/himalaya/config.toml` 配置文件 |

---

## 先决条件

- 为你的 Hermes 代理准备一个专用邮件账户（请勿使用个人邮箱）
- 确保该邮件账户已开启 **IMAP** 功能
- 如果使用 Gmail 或其他需要双重身份验证的邮件服务提供商，则需准备 **应用密码**

### Gmail 设置步骤

1. 在您的 Google 账户中开启双重身份验证。  
2. 访问 [应用密码](https://myaccount.google.com/apppasswords) 页面。  
3. 创建一个新的应用密码（选择“邮件”或“其他”）。  
4. 复制生成的 16 位密码——您将使用此密码代替常规密码进行登录。  

### Outlook / Microsoft 365  

1. 进入 [安全设置](https://account.microsoft.com/security) 页面。  
2. 若尚未开启双重身份验证，请立即启用。  
3. 在“其他安全选项”中创建应用密码。  
4. IMAP 主机地址：`outlook.office365.com`，SMTP 主机地址：`smtp.office365.com`。  

### 其他邮件服务提供商  

大多数邮件服务提供商都支持 IMAP/SMTP 协议。请查阅相应提供商的文档，确认以下信息：  
- IMAP 主机地址及端口（通常为使用 SSL 的 993 端口）；  
- SMTP 主机地址及端口（通常为使用 STARTTLS 的 587 端口）；  
- 是否需要应用密码。  

### Proton Mail Bridge / 本地中继服务器  

Proton Mail Bridge（以及类似的自托管 MTA 本地中继服务器）会通过 **STARTTLS** 协议并使用自签名证书在回环接口上监听，因此默认设置（IMAP 993 的隐式 TLS 加密、经过验证的证书）将无法建立连接。您需要在 `~/.hermes/config.yaml` 文件中修改传输设置以绕过此限制：

```yaml
platforms:
  email:
    enabled: true
    extra:
      imap_host: 127.0.0.1
      imap_security: starttls     # tls (default) | starttls | plain
      imap_tls_verify: false      # Bridge uses a self-signed cert
      smtp_host: 127.0.0.1
      smtp_security: starttls     # default: tls on port 465, starttls otherwise
      smtp_tls_verify: false
```

并在 `~/.hermes/.env` 文件中，将 `EMAIL_IMAP_PORT=1143` / `EMAIL_SMTP_PORT=1025` 与 Bridge 凭据一同设置。对于未知的 `*_security` 参数值，系统会输出警告并自动回退至安全的默认值。仅建议在回环主机上禁用 `*_tls_verify` —— 若对其他任何主机关闭该验证功能，Hermes 都会记录警告信息。

---

## 第1步：配置Hermes

最简单的方法：

```bash
hermes gateway setup
```

从平台菜单中选择**Email**。向导会提示您输入电子邮件地址、密码、IMAP/SMTP服务器以及允许的发送方。

### 手动配置

在`~/.hermes/.env`文件中添加以下内容：

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
3. 开始定期轮询新邮件

---

## 工作原理

### 接收邮件

该适配器会以可配置的间隔（默认为 15 秒）轮询 IMAP 收件箱中的未读邮件。对于每封新邮件：
- **主题行**会被作为上下文信息包含在内（例如：`[主题：部署到生产环境]`）
- **回复邮件**（主题行以 `Re:` 开头）无需再添加主题前缀——因为邮件线程的上下文已明确
- **附件**会本地缓存：
  - 图片（JPEG、PNG、GIF、WebP）——可供视觉分析工具使用
  - 文档（PDF、ZIP 等）——可用于文件访问
- **仅包含 HTML 格式的邮件**会去除标签以便提取纯文本
- **自发邮件**会被过滤掉，以避免回复循环
- **自动发送/无人回复的发送方**会被静默忽略，包括 `noreply@`、`mailer-daemon@`、`bounce@`、`no-reply@`，以及带有 `Auto-Submitted`、`Precedence: bulk` 或 `List-Unsubscribe` 标头的邮件

### 发送回复

回复会通过 SMTP 以正确的邮件线程结构发送：
- **In-Reply-To** 和 **References** 标头用于维护邮件线程
- 主题行会保留 `Re:` 前缀（不会出现双 `Re: Re:` 的情况）
- **Message-ID** 会使用代理的域名生成
- 回复内容以 UTF-8 编码的纯文本形式发送

### 文件附件

该代理可以在回复中发送文件附件。只需在回复内容中包含 `MEDIA:/path/to/file`，该文件就会作为附件附在发出的邮件中。

### 跳过附件

如需忽略所有传入的附件（以便防范恶意软件或节省带宽），请在您的 `config.yaml` 文件中添加以下内容：

```yaml
platforms:
  email:
    skip_attachments: true
```

启用该功能后，在解码邮件内容之前会跳过附件及内嵌内容，而邮件正文仍会按常规方式进行处理。

---

## 访问控制

与聊天类平台相比，邮件的访问控制更为严格：

1. **设置了 `EMAIL_ALLOWED_USERS`** → 仅处理来自这些地址的邮件
2. **未设置允许列表** → 未知发件人的邮件将被静默忽略
3. **`EMAIL_ALLOW_ALL_USERS=true`** → 接受所有发件人的邮件（请谨慎使用）
4. **`platforms.email.unauthorized_dm_behavior: pair`** → 未知发件人将收到配对码

:::warning
**为确保正常运行，请使用专用收件箱并配置 `EMAIL_ALLOWED_USERS`。** 邮件配对功能是可选的，因为共享收件箱中往往包含大量无关的未读邮件，Hermes 默认不应自动回复这些联系人。
:::

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| 启动时出现 **“IMAP连接失败”** 错误 | 请检查 `EMAIL_IMAP_HOST` 和 `EMAIL_IMAP_PORT` 的设置。同时确认该邮箱已开启IMAP功能。对于Gmail，需在“设置”→“转发与POP/IMAP”中启用该功能。 |
| 启动时出现 **“SMTP连接失败”** 错误 | 请检查 `EMAIL_SMTP_HOST` 和 `EMAIL_SMTP_PORT` 的设置。同时确认密码正确（使用Gmail时的应用专用密码）。 |
| 无法接收邮件 | 请检查 `EMAIL_ALLOWED_USERS` 是否已包含发件人的邮箱地址。同时查看垃圾邮件文件夹——部分邮件服务商会将自动回复邮件标记为垃圾邮件。 |
| 出现 **“身份验证失败”** 错误 | 对于Gmail，必须使用应用专用密码，而非普通密码。请先确保已开启双重认证功能。 |
| 出现重复回复 | 请确认仅有一个网关实例正在运行。可通过 `hermes gateway status` 命令查看当前状态。 |
| 响应速度缓慢 | 默认的轮询间隔为15秒。如需加快响应速度，可设置 `EMAIL_POLL_INTERVAL=5`（但这样会增加IMAP连接次数）。 |
| 回复邮件未按主题线程显示 | 该适配器使用的是“回复至”（In-Reply-To）标头。某些邮件客户端（尤其是网页版）可能无法正确处理自动发送的邮件及其主题线程。 |

---

## 安全性

:::warning
**请使用专用的邮箱账户。** 切勿使用个人邮箱——该代理会将密码存储在 `.env` 文件中，并能通过IMAP完全访问收件箱。
:::

- 请使用**应用密码**而非主密码（针对启用双重认证的 Gmail 是必需的）  
- 设置 `EMAIL_ALLOWED_USERS` 以限制可与该智能体交互的用户范围  
- 密码存储在 `~/.hermes/.env` 文件中——请保护该文件（执行 `chmod 600` 命令）  
- IMAP 默认使用 SSL（端口 993），SMTP 默认使用 STARTTLS（端口 587）——所有连接均经过加密处理  

---

## 环境变量参考

| 变量名 | 是否必填 | 默认值 | 说明 |
|--------|----------|--------|------|
| `EMAIL_ADDRESS` | 是 | — | 智能体的电子邮件地址 |
| `EMAIL_PASSWORD` | 是 | — | 电子邮件密码或应用密码 |
| `EMAIL_IMAP_HOST` | 是 | — | IMAP 服务器主机地址（例如：`imap.gmail.com`） |
| `EMAIL_SMTP_HOST` | 是 | — | SMTP 服务器主机地址（例如：`smtp.gmail.com`） |
| `EMAIL_IMAP_PORT` | 否 | `993` | IMAP 服务器端口 |
| `EMAIL_SMTP_PORT` | 否 | `587` | SMTP 服务器端口 |
| `EMAIL_POLL_INTERVAL` | 否 | `15` | 检查收件箱的间隔时间（秒） |
| `EMAIL_ALLOWED_USERS` | 否 | — | 以逗号分隔的允许发送邮件的地址列表 |
| `EMAIL_HOME_ADDRESS` | 否 | — | 定时任务的默认发送目标地址 |
| `EMAIL_ALLOW_ALL_USERS` | 否 | `false` | 允许所有发送者发送邮件（不推荐） |
