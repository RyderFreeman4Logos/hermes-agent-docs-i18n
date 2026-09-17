# Webhook 订阅功能

通过创建动态 Webhook 订阅，外部服务（如 GitHub、GitLab、Stripe、CI/CD 系统、物联网传感器以及监控工具）可以通过向指定 URL 发送事件来触发 Hermes Agent 的运行。

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
请按照提示操作，以启用 Webhook、设置端口并配置全局 HMAC 密钥。

### 方案二：手动配置
在 `~/.hermes/config.yaml` 文件中添加以下内容：
```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "your-webhook-secret-here"
```

若省略 `host` 参数，则会采用双栈默认设置，同时在 IPv4 和 IPv6 地址上监听。
仅当您有意限制绑定地址时，才需指定具体地址。

### 方案 3：环境变量
在 `${HERMES_HOME:-~/.hermes}/.env` 文件中添加相应配置：
```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644
WEBHOOK_SECRET=your-webhook-secret-here
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

所有管理操作均通过 `hermes webhook` CLI 命令完成：

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

该功能会返回 webhook URL 与 HMAC 密钥，用户需将自身的服务配置为向该地址发送 POST 请求。

### 在智能体运行前过滤或转换请求载荷

有两种机制可用于筛选海量事件流（例如 Todoist/GitHub 每次更新都会触发事件），从而仅让相关的载荷唤醒智能体：

- **声明式 `filters`**（仅适用于 config.yaml 中的路由）：用于定义针对载荷字段、事件类型或请求头条件的列表，支持 `equals`、`not_equals`、`contains`、`exists`、`missing`、`in`、`in_file`、`regex` 等运算符，并可通过 `all`/`any`/`not` 进行条件组合。不符合条件的事件会以 HTTP 200 状态码被忽略。
- **路由脚本**（在订阅时使用 `--script` 参数，或在 config 路由中指定 `script:`）：位于 `~/.hermes/scripts/` 目录下的脚本会通过标准输入接收 JSON 格式的载荷。脚本会先处理 JSON 数据并输出结果，该结果将替代原始载荷用于后续的提示模板生成；如果脚本输出为空、返回 `[SILENT]` 状态或非零退出码，则该 webhook 请求会被忽略。脚本默认使用 bash 解释执行 `.sh`/`.bash` 文件，其他类型则用 Python 处理。此外，脚本不得存放于 `~/.hermes/scripts/` 目录之外（以防止路径遍历攻击）。

```bash
hermes webhook subscribe todoist-hermes \
  --prompt "Task changed: {payload.content}" \
  --script "todoist-hermes-label.py" \
  --deliver telegram --deliver-chat-id "12345"
```

完整过滤语法说明：https://hermes-agent.nousresearch.com/docs/user-guide/messaging/webhooks#payload-filters

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
- `{pull_request.user.login}` — PR 的创建者
- `{data.object.amount}` — Stripe 支付金额
- `{sensor.temperature}` — 物联网传感器的读数

如果未指定提示词，则会将完整的 JSON 载荷直接放入代理的提示词中。

## 常见用法模式

### GitHub：新建问题
```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New GitHub issue #{issue.number}: {issue.title}\n\nAction: {action}\nAuthor: {issue.user.login}\nBody:\n{issue.body}\n\nPlease triage this issue." \
  --deliver telegram \
  --deliver-chat-id "-100123456789"
```

接着在 GitHub 仓库的“Settings”→“Webhooks”中添加 webhook：
- Payload URL：此处填写返回的 webhook_url
- Content type：选择 application/json
- Secret：填写返回的 secret 值
- Events：设置为 “Issues”

### GitHub：PR 审核功能
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

### CI/CD：构建通知
```bash
hermes webhook subscribe ci-builds \
  --events "pipeline" \
  --prompt "Build {object_attributes.status} on {project.name} branch {object_attributes.ref}\nCommit: {commit.message}" \
  --deliver discord \
  --deliver-chat-id "1234567890"
```

### 通用监控告警
```bash
hermes webhook subscribe alerts \
  --prompt "Alert: {alert.name}\nSeverity: {alert.severity}\nMessage: {alert.message}\n\nPlease investigate and suggest remediation." \
  --deliver origin
```

### 直接发送模式（无需智能体，零LLM成本）

对于仅需将通知直接推送到用户聊天界面的场景——无需进行任何推理，也无需智能体循环处理——可添加 `--deliver-only` 参数。此时，经过处理的 `--prompt` 模板将直接作为消息内容，被发送至目标适配器。

该模式适用于以下场景：
- 外部服务推送通知（如 Supabase/Firebase Webhook → Telegram）
- 需要原封不动转发的监控警报
- 智能体间通信，即一个智能体向另一个智能体的用户传递信息
- 任何会导致LLM进行多余往返处理的Webhook场景

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 New match: {match.user_name} matched with you!" \
  --description "Antenna match notifications"
```

成功发送后，POST请求会返回`200 OK`状态码；若目标端处理失败，则返回`502`状态码——这样上游服务就能智能地重试。同时，HMAC身份验证、速率限制以及幂等性机制依然有效。

若要实现真正的目标端发送（如Telegram、Discord、Slack、GitHub评论等），必须使用`--deliver`参数；而`--deliver log`参数会被拒绝，因为仅向日志发送内容毫无意义。

## 安全性

- 每个订阅都会自动生成一个HMAC-SHA256密钥（也可通过`--secret`参数自行指定）
- Webhook适配器会对每个收到的POST请求进行签名验证
- 配置文件`config.yaml`中定义的静态路由不会被动态订阅覆盖
- 订阅信息会保存在`~/.hermes/webhook_subscriptions.json`文件中

## 工作原理

1. `hermes webhook subscribe`命令会将订阅信息写入`~/.hermes/webhook_subscriptions.json`文件
2. Webhook适配器会在每个接收到的请求时热加载该文件（基于修改时间判断，几乎不会产生额外开销）
3. 当有符合路由规则的POST请求到达时，适配器会格式化提示内容并触发智能体运行
4. 智能体的响应会被发送到预先配置的目标端（如Telegram、Discord、GitHub评论等）

## 故障排除

如果Webhook无法正常工作：

1. **网关是否正在运行？** 可通过 `systemctl --user status hermes-gateway` 或 `ps aux | grep gateway` 命令进行检查。  
2. **Webhook 服务器是否处于监听状态？** 执行 `curl http://localhost:8644/health` 后，应返回 `{"status": "ok"}` 的结果。  
3. **查看网关日志：** 使用命令 `grep webhook ~/.hermes/logs/gateway.log | tail -20` 查看相关日志。  
4. **签名不匹配？** 请确认您服务中的密钥与 `hermes webhook list` 中显示的密钥一致。GitHub 会发送 `X-Hub-Signature-256` 头部信息，而 GitLab 则会发送 `X-Gitlab-Token`。  
5. **防火墙或 NAT 的影响？** 服务端必须能够访问该 Webhook 地址。在本地开发时，建议使用隧道工具（如 ngrok、cloudflared）来绕过限制。  
6. **事件类型错误？** 请检查 `--events` 参数是否与服务实际发送的事件类型匹配。可使用命令 `hermes webhook test <name>` 来验证路由配置是否正常。
