# AgentMail Core

常用 CLI 功能包括：创建收件箱、发送邮件、读取新邮件、在主题回复中回复、给任务添加标签以及获取附件。需要密钥吗？请参考 [signup.md](signup.md) 文档。需要实时邮件送达功能？请使用 [webhooks.md](webhooks.md) 或 [websockets.md](websockets.md)。

## 设置

```bash
npm install -g agentmail-cli@latest
export AGENTMAIL_API_KEY="am_..."
agentmail inboxes list --format json
```

## 收件箱

```bash
agentmail inboxes create \
  --username support \
  --display-name "Support Agent" \
  --client-id support-agent-primary \
  --format json

agentmail inboxes get --inbox-id support@agentmail.to --format json
```

若要使用 `@agentmail.to`，请省略 `domain` 参数。在重复执行创建指令时，请使用稳定的 `client_id` 值。

## 发送消息

需完整翻译输入内容，不得提前终止。

```bash
agentmail inboxes:messages send \
  --inbox-id support@agentmail.to \
  --to customer@example.com \
  --subject "Hello" \
  --text "Plain-text body." \
  --html "<p>Plain-text body.</p>" \
  --label outreach \
  --format json
```

在可能的情况下，请同时发送 `text` 和 `html` 格式的内容。`to`、`cc` 和 `bcc` 收件人的总数上限为 50 人。

## 阅读并回复

```bash
agentmail inboxes:messages list --inbox-id support@agentmail.to --label unread --format json
agentmail inboxes:messages get --inbox-id support@agentmail.to --message-id <message_id> --format json
agentmail inboxes:threads get --inbox-id support@agentmail.to --thread-id <thread_id> --format json
```

在输入大语言模型时，建议使用 `extracted_text` 或 `extracted_html`。部分邮件虽然包含 `html` 格式的内容，但却没有对应的 `text` 格式内容。

```bash
agentmail inboxes:messages reply \
  --inbox-id support@agentmail.to \
  --message-id <message_id> \
  --text "Thanks, I will take a look." \
  --format json

agentmail inboxes:messages reply-all \
  --inbox-id support@agentmail.to \
  --message-id <message_id> \
  --text "Thanks, everyone." \
  --format json

agentmail inboxes:messages forward \
  --inbox-id support@agentmail.to \
  --message-id <message_id> \
  --to teammate@example.com \
  --format json
```

## 标签

可将标签用作轻量级状态：`unread`、`handled`、`needs-review`。

```bash
agentmail inboxes:messages update \
  --inbox-id support@agentmail.to \
  --message-id <message_id> \
  --add-labels handled \
  --remove-labels unread \
  --format json
```

## 附件

```bash
agentmail inboxes:messages get-attachment \
  --inbox-id support@agentmail.to \
  --message-id <message_id> \
  --attachment-id <attachment_id> \
  --format json
```

请在返回的下载链接过期之前及时获取它。如需了解有关附件发送的相关参数，可查看 `agentmail inboxes:messages send --help` 的说明。

## REST 接口说明

仅当命令行界面不可用或缺少某些必要功能时，才可使用 REST 接口。

```bash
curl https://api.agentmail.to/v0/inboxes \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY"
```

基础 URL 为：`https://api.agentmail.to/v0` 和 `https://api.agentmail.eu/v0`。错误响应体中会包含 `name` 和 `message` 字段；验证错误则包含 `errors` 字段。遇到 429 错误时，应遵循 `Retry-After` 指令并适当延迟后再进行请求。
