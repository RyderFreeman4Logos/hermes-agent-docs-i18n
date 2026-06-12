---
sidebar_position: 2
sidebar_label: "Google Workspace"
title: "Google Workspace — Gmail, Calendar, Drive, Sheets & Docs"
description: "Send email, manage calendar events, search Drive, read/write Sheets, and access Docs — all through OAuth2-authenticated Google APIs"
---

# Google Workspace 功能模块

为 Hermes 提供对 Gmail、Calendar、Drive、Contacts、Sheets 和 Docs 的集成支持。采用 OAuth2 协议，并具备自动令牌刷新功能。在可用的情况下，优先使用 [Google Workspace CLI (`gws`)](https://github.com/googleworkspace/cli) 以实现更全面的功能覆盖；否则则回退至 Google 的 Python 客户端库。

**功能模块路径：** `skills/productivity/google-workspace/`

## 设置流程

整个设置过程完全由 Hermes 主导——只需让 Hermes 执行 Google Workspace 的设置任务，它会引导您完成每一步操作。具体流程如下：

1. **创建一个 Google Cloud 项目**，并启用所需的 API（Gmail、Calendar、Drive、Sheets、Docs、People）。
2. **创建 OAuth 2.0 凭证**（桌面应用类型），并下载对应的客户端密钥 JSON 文件。
3. **授权**——Hermes 会生成授权 URL，您在浏览器中确认授权后，再将重定向 URL 粘贴回来。
4. **设置完成**——此后令牌将自动刷新。

:::提示 仅需要使用邮箱功能的用户
如果您仅需使用邮箱功能（无需 Calendar/Drive/Sheets），建议使用 **himalaya** 功能模块——它支持通过 Gmail 应用密码进行登录，仅需 2 分钟即可设置完成，且无需创建 Google Cloud 项目。
:::

## Gmail

### 搜索功能

```bash
$GAPI gmail search "is:unread" --max 10
$GAPI gmail search "from:boss@company.com newer_than:1d"
$GAPI gmail search "has:attachment filename:pdf newer_than:7d"
```

会针对每条消息返回一个 JSON 对象，其中包含 `id`、`from`、`subject`、`date`、`snippet` 以及 `labels` 等字段。

### 读取操作

```bash
$GAPI gmail get MESSAGE_ID
```

以文本形式返回完整的消息内容（优先为纯文本，若无法生成则回退为HTML格式）。

### 发送

```bash
# Basic send
$GAPI gmail send --to user@example.com --subject "Hello" --body "Message text"

# HTML email
$GAPI gmail send --to user@example.com --subject "Report" \
  --body "<h1>Q4 Results</h1><p>Details here</p>" --html

# Custom From header (display name + email)
$GAPI gmail send --to user@example.com --subject "Hello" \
  --from '"Research Agent" <user@example.com>' --body "Message text"

# With CC
$GAPI gmail send --to user@example.com --cc "team@example.com" \
  --subject "Update" --body "FYI"
```

### 自定义发件人显示名称

`--from` 参数允许您自定义发送邮件的发件人显示名称。当多个智能体共享同一个 Gmail 账户，但您希望收件人看到不同的名称时，此功能非常实用：

```bash
# Agent 1
$GAPI gmail send --to client@co.com --subject "Research Summary" \
  --from '"Research Agent" <shared@company.com>' --body "..."

# Agent 2  
$GAPI gmail send --to client@co.com --subject "Code Review" \
  --from '"Code Assistant" <shared@company.com>' --body "..."
```

**工作原理：** `--from` 参数的值会被设置为 MIME 消息中的 RFC 5322 `From` 标头。Gmail 允许用户无需额外配置即可自定义已验证电子邮件地址的显示名称。收件人将看到自定义的显示名称（例如“研究助手”），而电子邮件地址保持不变。

**重要提示：** 如果在 `--from` 参数中使用*其他电子邮件地址*（而非已验证的账户），Gmail 要求将该地址在 Gmail 设置 → 账户 → 以...的名称发送邮件中配置为[发送别名](https://support.google.com/mail/answer/22370)。

`--from` 参数同时适用于“发送”和“回复”操作：

```bash
$GAPI gmail reply MESSAGE_ID \
  --from '"Support Bot" <shared@company.com>' --body "We're on it"
```

### 回复操作

```bash
$GAPI gmail reply MESSAGE_ID --body "Thanks, that works for me."
```

该功能会自动为回复设置线程标识（配置 `In-Reply-To` 和 `References` 标头），并沿用原始消息的线程编号。

```bash
# List all labels
$GAPI gmail labels

# Add/remove labels
$GAPI gmail modify MESSAGE_ID --add-labels LABEL_ID
$GAPI gmail modify MESSAGE_ID --remove-labels UNREAD
```

## 日历功能

```bash
# List events (defaults to next 7 days)
$GAPI calendar list
$GAPI calendar list --start 2026-03-01T00:00:00Z --end 2026-03-07T23:59:59Z

# Create event (timezone required)
$GAPI calendar create --summary "Team Standup" \
  --start 2026-03-01T10:00:00-07:00 --end 2026-03-01T10:30:00-07:00

# With location and attendees
$GAPI calendar create --summary "Lunch" \
  --start 2026-03-01T12:00:00Z --end 2026-03-01T13:00:00Z \
  --location "Cafe" --attendees "alice@co.com,bob@co.com"

# Delete event
$GAPI calendar delete EVENT_ID
```

:::warning
日期时间**必须**包含时区偏移量（例如 `-07:00`），或明确使用协调世界时（`Z`）。仅包含时间戳的格式，如 `2026-03-01T10:00:00`，含义不明确，将被视为协调世界时处理。
:::

## 驱动器

```bash
$GAPI drive search "quarterly report" --max 10
$GAPI drive search "mimeType='application/pdf'" --raw-query --max 5
```

## 表格功能

```bash
# Read a range
$GAPI sheets get SHEET_ID "Sheet1!A1:D10"

# Write to a range
$GAPI sheets update SHEET_ID "Sheet1!A1:B2" --values '[["Name","Score"],["Alice","95"]]'

# Append rows
$GAPI sheets append SHEET_ID "Sheet1!A:C" --values '[["new","row","data"]]'
```

## 文档资料

```bash
$GAPI docs get DOC_ID
```

返回文档标题及完整文本内容。

## 联系方式

```bash
$GAPI contacts list --max 20
```

## 输出格式

所有命令均返回 JSON 格式数据。各服务对应的字段如下：

| 命令 | 字段 |
|---------|------|
| `gmail search` | `id`, `threadId`, `from`, `to`, `subject`, `date`, `snippet`, `labels` |
| `gmail get` | `id`, `threadId`, `from`, `to`, `subject`, `date`, `labels`, `body` |
| `gmail send/reply` | `status`, `id`, `threadId` |
| `calendar list` | `id`, `summary`, `start`, `end`, `location`, `description`, `htmlLink` |
| `calendar create` | `status`, `id`, `summary`, `htmlLink` |
| `drive search` | `id`, `name`, `mimeType`, `modifiedTime`, `webViewLink` |
| `contacts list` | `name`, `emails`, `phones` |
| `sheets get` | 单元格值的二维数组 |

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `NOT_AUTHENTICATED` | 运行设置脚本（让 Hermes 配置 Google Workspace 访问权限） |
| `REFRESH_FAILED` | 令牌已失效——重新执行授权步骤 |
| `HttpError 403: Insufficient Permission` | 缺少所需权限范围——撤销当前授权并使用正确的服务重新授权 |
| `HttpError 403: Access Not Configured` | Google Cloud 控制台未启用该 API |
| `ModuleNotFoundError` | 运行设置脚本时添加 `--install-deps` 参数以安装依赖项 |
