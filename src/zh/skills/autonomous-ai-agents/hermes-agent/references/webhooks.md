# Webhook 订阅

通过创建动态 Webhook 订阅，外部服务（如 GitHub、GitLab、Stripe、CI/CD 系统、物联网传感器及监控工具）可以通过向指定 URL 发送事件来触发 Hermes Agent 的运行。

## 设置（必须先完成）

在创建订阅之前，必须先启用 Webhook 功能。请通过以下方式进行检查：
```bash
hermes webhook list
```

如果显示“未启用 Webhook 平台”，请进行设置：

### 方案一：设置向导
```bash
hermes gateway setup
```
请按照提示操作，以启用 Webhook、设置端口以及定义全局 HMAC 密钥。

### 方案二：手动配置
在 `~/.hermes/config.yaml` 文件中添加以下内容：
```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8644
      secret: "generate-a-strong-secret-here"
```

### 方案 3：环境变量
在 `${HERMES_HOME:-~/.hermes}/.env` 文件中添加如下内容：
```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644
WEBHOOK_SECRET=generate-a-strong-secret-here
```

配置完成后，启动（或重启）网关：
```bash
hermes gateway run
# Or if using systemd:
systemctl --user restart hermes-gateway
```

验证其是否正在运行：
```bash
curl http://localhost:8644/health
```

## 命令

所有管理操作均通过 `hermes webhook` CLI 命令来完成：

### 创建订阅
```bash
hermes webhook subscribe <name> \
  --prompt "Prompt template with {payload.fields}" \
  --events "event1,event2" \
  --description "What this does" \
  --skills "skill1,skill2" \
  --deliver telegram \
  --deliver-chat-id "12345" \
  --secret "optional-custom-secret"
```

返回 webhook 地址及 HMAC 密钥。用户需将其服务配置为向该地址发送 POST 请求。

### 列出订阅项
```bash
hermes webhook list
```

### 取消订阅
```bash
hermes webhook remove <name>
```

### 测试订阅功能
```bash
hermes webhook test <name>
hermes webhook test <name> --payload '{"key": "value"}'
```

## 提示词模板

提示词支持使用 `{dot.notation}` 格式来访问嵌套的负载字段：

- `{issue.title}` — GitHub 问题标题
- `{pull_request.user.login}` — PR 的提交者
- `{data.object.amount}` — Stripe 支付金额
- `{sensor.temperature}` — 物联网传感器的读数

如果未指定提示词，则会将完整的 JSON 负载直接注入到代理的提示词中。

## 常见用法模式

### GitHub：新建问题
```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New GitHub issue #{issue.number}: {issue.title}\n\nAction: {action}\nAuthor: {issue.user.login}\nBody:\n{issue.body}\n\nPlease triage this issue." \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```

接着在 GitHub 仓库的“设置”→“Webhooks”中添加 Webhook：
- Payload URL：即返回的 webhook_url
- Content type：application/json
- Secret：即返回的 secret
- Events：“Issues”

### GitHub：PR 审核
```bash
hermes webhook subscribe github-prs \
  --events "pull_request" \
  --prompt "PR #{pull_request.number} {action}: {pull_request.title}\nBy: {pull_request.user.login}\nBranch: {pull_request.head.ref}\n\n{pull_request.body}" \
  --skills "github-code-review" \
  --deliver github_comment
```

### Stripe：支付事件
```bash
hermes webhook subscribe stripe-payments \
  --events "payment_intent.succeeded,payment_intent.payment_failed" \
  --prompt "Payment {data.object.status}: {data.object.amount} cents from {data.object.receipt_email}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```

### CI/CD：构建通知功能
```bash
hermes webhook subscribe ci-builds \
  --events "pipeline" \
  --prompt "Build {object_attributes.status} on {project.name} branch {object_attributes.ref}\nCommit: {commit.message}" \
  --deliver discord \
  --deliver-chat-id "1234567890"
```

### 通用监控警报
```bash
hermes webhook subscribe alerts \
  --prompt "Alert: {alert.name}\nSeverity: {alert.severity}\nMessage: {alert.message}\n\nPlease investigate and suggest remediation." \
  --deliver origin
```

### 直接发送模式（无需智能体，零LLM成本）

对于仅需将通知直接推送到用户聊天窗口的场景——无需进行任何推理，也无需智能体循环处理——可添加 `--deliver-only` 参数。此时，经过处理的 `--prompt` 模板将直接作为消息内容，被发送至目标适配器。

此模式适用于以下场景：
- 外部服务推送通知（如 Supabase/Firebase Webhook → Telegram）
- 需要原封不动转发的监控警报
- 智能体间的通信，即一个智能体需向另一个智能体的用户传达信息
- 任何会导致LLM往返处理而浪费资源的Webhook场景

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 New match: {match.user_name} matched with you!" \
  --description "Antenna match notifications"
```

当消息成功送达时，POST请求会返回`200 OK`状态码；若目标地址无法访问，则返回`502`状态码——这样上游服务便可智能地进行重试。同时，HMAC身份验证、速率限制以及幂等性机制依然有效。

若要实现真正的目标地址（如Telegram、Discord、Slack、GitHub评论等）发送消息，必须使用`--deliver`参数；而`--deliver log`参数会被拒绝，因为仅传输日志并无实际意义。

## 安全性

- 每个订阅项都会自动生成一个HMAC-SHA256密钥（也可通过`--secret`参数自行指定）
- Webhook适配器会对每一条接收到的POST请求的签名进行验证
- 配置文件`config.yaml`中定义的静态路由无法被动态订阅项覆盖
- 订阅信息会保存在`~/.hermes/webhook_subscriptions.json`文件中

## 工作原理

1. `hermes webhook subscribe`命令会将订阅信息写入`~/.hermes/webhook_subscriptions.json`文件
2. Webhook适配器会在收到每个请求时热加载该文件（基于修改时间控制，几乎不会带来额外开销）
3. 当有符合路由规则的POST请求到达时，适配器会格式化提示内容并触发智能体运行
4. 智能体的响应会被发送到预先配置的目标地址（如Telegram、Discord、GitHub评论等）

## 故障排除

如果Webhook无法正常工作，请按以下步骤排查：

1. **网关是否正在运行？** 可通过`systemctl --user status hermes-gateway`或`ps aux | grep gateway`命令进行检查
2. **Webhook服务器是否处于监听状态？** 执行`curl http://localhost:8644/health`命令，应返回`{"status": "ok"}`这样的结果
3. **查看网关日志：** 使用`grep webhook ~/.hermes/logs/gateway.log | tail -20`命令查看相关日志
4. **签名是否匹配？** 确保您服务中使用的密钥与`hermes webhook list`命令显示的密钥一致。GitHub会发送`X-Hub-Signature-256`头信息，GitLab则发送`X-Gitlab-Token`头信息
5. **是否存在防火墙或NAT限制？** 服务端必须能够访问Webhook地址。在本地开发时，建议使用隧道工具（如ngrok、cloudflared）来建立连接
6. **事件类型是否错误？** 检查`--events`参数所指定的过滤条件是否与服务实际发送的事件类型相符。可使用`hermes webhook test <name>`命令来验证路由是否正常工作
