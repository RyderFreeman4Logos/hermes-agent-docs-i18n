# Himalaya 配置参考手册

配置文件位置：`~/.config/himalaya/config.toml`

## 最简 IMAP + SMTP 配置方式

```toml
[accounts.default]
email = "user@example.com"
display-name = "Your Name"
default = true

# IMAP backend for reading emails
backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "user@example.com"
backend.auth.type = "password"
backend.auth.raw = "your-password"

# SMTP backend for sending emails
message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "user@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.raw = "your-password"

# Folder aliases — required whenever server folder names differ
# from himalaya's canonical names. See "Folder Aliases" below.
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "Sent"
folder.aliases.drafts = "Drafts"
folder.aliases.trash = "Trash"
```

## 密码选项

### 原始密码（仅用于测试，不推荐使用）

```toml
backend.auth.raw = "your-password"
```

### 通过命令输入密码（推荐方式）

```toml
backend.auth.cmd = "pass show email/imap"
# backend.auth.cmd = "security find-generic-password -a user@example.com -s imap -w"
```

### 系统密钥环（需启用密钥环功能）

```toml
backend.auth.keyring = "imap-example"
```

随后运行 `himalaya account configure <account>` 命令即可存储密码。

## Gmail 配置

```toml
[accounts.gmail]
email = "you@gmail.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@gmail.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show google/app-password"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@gmail.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show google/app-password"

# Gmail folder mapping. Without these, save-to-Sent fails after
# SMTP delivery succeeds (Gmail's Sent folder is `[Gmail]/Sent Mail`,
# not `Sent`), and `himalaya message send` exits non-zero. Any
# caller that retries on that error will re-run SMTP — duplicate
# emails to recipients. Always include this block for Gmail.
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "[Gmail]/Sent Mail"
folder.aliases.drafts = "[Gmail]/Drafts"
folder.aliases.trash = "[Gmail]/Trash"
```

**注意：** 若启用了双重身份验证，Gmail 需要使用应用密码。 

## iCloud 配置

```toml
[accounts.icloud]
email = "you@icloud.com"
display-name = "Your Name"

backend.type = "imap"
backend.host = "imap.mail.me.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@icloud.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show icloud/app-password"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.mail.me.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@icloud.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show icloud/app-password"
```

**注意：**请在 appleid.apple.com 上生成一个专属于该应用的安全密码。

## 文件夹别名

将 Himalaya 标准的文件夹名称（如 `inbox`、`sent`、`drafts`、`trash`）映射为服务器实际使用的名称。请使用 v1.2.0 版本的 `folder.aliases.X` 语法（复数形式、带点分隔的键名，位于 `[accounts.NAME]` 下方）：

```toml
[accounts.default]
# ... other account config ...

folder.aliases.inbox = "INBOX"
folder.aliases.sent = "Sent"
folder.aliases.drafts = "Drafts"
folder.aliases.trash = "Trash"
```

在 v1.2.0 版本中，对应的 TOML 子部分格式同样适用：

```toml
[accounts.default.folder.aliases]
inbox = "INBOX"
sent = "Sent"
drafts = "Drafts"
trash = "Trash"
```

> **请勿使用单数形式的 `alias`。** 在 v1.2.0 之前的文档中，示例格式为 `[accounts.NAME.folder.alias]`（单数形式）。v1.2.0 版本会自动忽略该子部分——TOML 格式虽能被正确解析，但别名解析器却不会读取该内容。因此，所有查询都会回退到标准名称。在 Gmail 中（其 `sent` 目录的实际路径为 `[Gmail]/Sent Mail`），这意味着在 SMTP 发送成功之后，执行“保存到已发送邮件”操作会失败，且 `himalaya message send` 命令的退出码也会不为零。任何基于该错误代码进行重试的调用方（无论是代理、脚本还是用户），都会重新执行发送操作——包括 SMTP 发送步骤——从而导致向收件人发送重复邮件。请始终使用 `folder.aliases.X`（复数形式）。

## 多个账户

```toml
[accounts.personal]
email = "personal@example.com"
default = true
# ... backend config ...

[accounts.work]
email = "work@company.com"
# ... backend config ...
```

使用 `--account` 参数切换账户：

```bash
himalaya --account work envelope list
```

## Notmuch 后端（本地邮件功能）

```toml
[accounts.local]
email = "user@example.com"

backend.type = "notmuch"
backend.db-path = "~/.mail/.notmuch"
```

## OAuth2身份验证（适用于支持该功能的提供方）

```toml
backend.auth.type = "oauth2"
backend.auth.client-id = "your-client-id"
backend.auth.client-secret.cmd = "pass show oauth/client-secret"
backend.auth.access-token.cmd = "pass show oauth/access-token"
backend.auth.refresh-token.cmd = "pass show oauth/refresh-token"
backend.auth.auth-url = "https://provider.com/oauth/authorize"
backend.auth.token-url = "https://provider.com/oauth/token"
```

## 其他选项

### 签名

```toml
[accounts.default]
signature = "Best regards,\nYour Name"
signature-delim = "-- \n"
```

### 下载目录

```toml
[accounts.default]
downloads-dir = "~/Downloads/himalaya"
```

### 用于内容编辑的工具

通过环境变量设置：

```bash
export EDITOR="vim"
```
