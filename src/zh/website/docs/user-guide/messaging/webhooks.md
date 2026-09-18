---
sidebar_position: 13
title: "Webhooks"
description: "Receive events from GitHub, GitLab, and other services to trigger Hermes agent runs"
---

# Webhooks

可从外部服务（如 GitHub、GitLab、JIRA、Stripe 等）接收事件，并自动触发 Hermes Agent 的运行。Webhook 适配器会运行一个 HTTP 服务器，用于接收 POST 请求、验证 HMAC 签名、将请求数据转换为 Agent 可处理的提示语，随后再将响应发送回原始服务或另一个已配置的平台。

Agent 会对这些事件进行处理，并可通过在 PR 上添加评论、向 Telegram/Discord 发送消息或记录处理结果等方式进行响应。

## 视频教程

<div style={{position: 'relative', width: '100%', aspectRatio: '16 / 9', marginBottom: '1.5rem'}}>
  <iframe
    src="https://www.youtube.com/embed/WNYe5mD4fY8"
    title="Hermes Agent — Webhooks 教程"
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0}}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

---

## 快速入门

1. 通过 `hermes gateway setup` 命令或环境变量启用 Webhooks 功能。
2. 在 `config.yaml` 文件中定义路由，**或**使用 `hermes webhook subscribe` 动态创建路由。
3. 将您的服务指向 `http://your-server:8644/webhooks/<route-name>` 地址。

---

## 设置

启用 Webhook 适配器有两种方式。

### 通过设置向导

```bash
hermes gateway setup
```

请按照提示操作，以启用 Webhook、设置端口，并设定全局 HMAC 密钥。

### 通过环境变量设置

在 `~/.hermes/.env` 文件中添加以下内容：

```bash
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644        # default
WEBHOOK_SECRET=your-global-secret
```

### 验证服务器状态

在网关启动后：

```bash
curl http://localhost:8644/health
```

预期响应：


请完整翻译输入内容，切勿提前终止。

```json
{"status": "ok", "platform": "webhook"}
```

## 配置路由 {#configuring-routes}

路由用于定义如何处理不同的 Webhook 来源。在您的 `config.yaml` 文件中，每个路由都是 `platforms.webhook.extra.routes` 下的一个带名称的条目。

### 路由属性

| Property | Required | Description |
|----------|----------|-------------|
| `events` | No | List of event types to accept (e.g. `["pull_request"]`). If empty, all events are accepted. Event type is read from `X-GitHub-Event`, `X-GitLab-Event`, or `event_type` in the payload. |
| `secret` | **Yes** | HMAC secret for signature validation. Falls back to the global `secret` if not set on the route. Set to `"INSECURE_NO_AUTH"` for testing only (skips validation). |
| `profile` | No | Profile authorized to execute this route when `gateway.multiplex_profiles` is enabled. Omit it for a default-profile-only route; set a profile name (for example `coder`) to bind the route and its secret to `/p/coder/webhooks/<route>`. |
| `prompt` | No | Template string with dot-notation payload access (e.g. `{pull_request.title}`). If omitted, the full JSON payload is dumped into the prompt. Payload fields are untrusted — see [Authenticated does not mean trusted](#authenticated-does-not-mean-trusted). |
| `filters` | No | Declarative payload filters evaluated after auth/body/event filtering and before agent or direct delivery work. Non-matches return `{"status":"ignored","reason":"filter"}` with HTTP 200. |
| `script` | No | Filter/transform script under `~/.hermes/scripts/`. The webhook payload is passed as JSON on stdin. JSON object stdout replaces the payload before templating; text stdout is exposed as `script_output`; empty stdout, `[SILENT]`, or a nonzero exit code ignores the webhook. |
| `skills` | No | List of skill names to load for the agent run. |
| `toolsets` | No | List of toolset keys (e.g. `["terminal", "file", "web"]`) that **replaces** the platform-level webhook toolset for runs triggered by this route only. Manual config edit only — not settable via `hermes webhook subscribe`, so agent-created subscriptions cannot self-grant elevated tools. Names are validated the same way as `platform_toolsets` entries (unknown or platform-restricted names are dropped). See [Per-route toolsets](#per-route-toolsets). |
| `deliver` | No | Where to send the response: `github_comment`, `telegram`, `discord`, `slack`, `signal`, `sms`, `whatsapp`, `matrix`, `mattermost`, `homeassistant`, `email`, `dingtalk`, `feishu`, `wecom`, `weixin`, `bluebubbles`, `qqbot`, or `log` (default). |
| `deliver_extra` | No | Additional delivery config — keys depend on `deliver` type (e.g. `repo`, `pr_number`, `chat_id`). Values support the same `{dot.notation}` templates as `prompt`. |
| `deliver_only` | No | If `true`, skip the agent entirely — the rendered `prompt` template becomes the literal message that gets delivered. Zero LLM cost, sub-second delivery. See [Direct Delivery Mode](#direct-delivery-mode) for use cases. Requires `deliver` to be a real target (not `log`). |

### 完整示例

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "global-fallback-secret"
      routes:
        github-pr:
          events: ["pull_request"]
          secret: "github-webhook-secret"
          prompt: |
            Review this pull request:
            Repository: {repository.full_name}
            PR #{number}: {pull_request.title}
            Author: {pull_request.user.login}
            URL: {pull_request.html_url}
            Diff URL: {pull_request.diff_url}
            Action: {action}
          skills: ["github-code-review"]
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{number}"
        deploy-notify:
          events: ["push"]
          secret: "deploy-secret"
          prompt: "New push to {repository.full_name} branch {ref}: {head_commit.message}"
          filters:
            - field: "ref"
              equals: "refs/heads/main"
          deliver: "telegram"
```

### 载荷过滤器

当某个提供方发送大量事件流，但仅有部分载荷需要唤醒智能体或触发“仅交付”功能时，可使用 `filters`。这些过滤器会在签名验证、消息体解析以及 `events` 处理之后执行，但在提示词渲染、重试机制应用、智能体调度或直接消息交付之前运行。

```yaml
platforms:
  webhook:
    extra:
      routes:
        todoist:
          events: ["item:updated"]
          secret: "todoist-secret"
          filters:
            - field: "payload.labels"
              contains: "hermes"
            - any:
                - field: "payload.priority"
                  equals: 4
                - field: "payload.project_id"
                  in_file: "~/.hermes/data/todoist/watchlist.json"
          prompt: "Todoist task changed: {payload.content}"
```

支持的运算符：

- `exists: true|false`
- `missing: true`
- `equals` / `not_equals`
- 适用于字符串、列表及字典键的 `contains`
- 适用于内联列表的 `in`
- 适用于 JSON 数组、JSON 对象（使用键值）或换行分隔的文本文件的 `in_file`
- `regex`
- `all`、`any` 以及 `not` 组

字段路径采用点号表示法。`payload.foo` 会在存在顶层 `payload` 对象时从其读取数据，而对于扁平结构的数据，则直接从 webhook 的根内容中读取。`event` / `event_type` 会与解析后的事件类型相匹配，而 `headers.<Name>` 用于读取请求头信息。

### 脚本过滤器与转换功能

当声明式过滤器无法满足需求时，可使用脚本功能。脚本必须存放于当前激活配置文件的 `~/.hermes/scripts/` 目录下；相对路径会在此处解析，且禁止访问该目录以外的路径。`.sh` 和 `.bash` 格式的脚本将使用 bash 运行，其他所有扩展名的脚本则通过当前的 Python 解释器执行。

路由传入的负载会以 JSON 格式发送到标准输入流中：

```python
# ~/.hermes/scripts/todoist-hermes-label.py
import json
import sys

payload = json.load(sys.stdin)
labels = payload.get("payload", {}).get("labels", [])
if "hermes" not in labels:
    print("[SILENT]")
    raise SystemExit(0)

payload["body"] = payload["payload"]["content"]
print(json.dumps(payload))
```

脚本执行结果：

- JSON 格式的标准输出将替代 `prompt` 和 `deliver_extra` 所使用的负载数据。
- 非 JSON 格式的文本标准输出则作为 `script_output` 添加到负载数据中。
- 若标准输出为空、内容为 `[SILENT]`、`{"__hermes_ignore__": true}`、发生超时、脚本缺失或退出码非零，系统将返回 HTTP 200 状态码，并附带信息 `{"status":"ignored","reason":"script"}`。

### 提示词模板

提示词采用点号语法来访问 webhook 负载数据中的嵌套字段：

- `{pull_request.title}` 对应 `payload["pull_request"]["title"]`
- `{repository.full_name}` 对应 `payload["repository"]["full_name"]`
- `{__raw__}` —— 一种特殊标记，用于以缩进格式输出**整个负载数据**（内容长度超过 4000 字符时会截断）。该标记适用于需要完整上下文的监控警报或通用 webhook 场景。
- 若某个键不存在，系统会保留 `{key}` 的原始字符串形式（不会报错）。
- 嵌套的字典和列表会被序列化为 JSON 格式，内容长度超过 2000 字符时也会被截断。

您可以将 `{__raw__}` 与常规模板变量混合使用：

```yaml
prompt: "PR #{pull_request.number} by {pull_request.user.login}: {__raw__}"
```

如果某个路由未配置 `prompt` 模板，那么整个请求载荷将以缩进格式的 JSON 形式输出（内容长度超过 4000 个字符时会被截断）。

相同的点号表示法模板也适用于 `deliver_extra` 参数中的值。

### 论坛主题发送功能

在向 Telegram 发送 webhook 响应时，你可以通过在 `deliver_extra` 中添加 `message_thread_id`（或 `thread_id`）来指定特定的论坛主题：

```yaml
webhooks:
  routes:
    alerts:
      events: ["alert"]
      prompt: "Alert: {__raw__}"
      deliver: "telegram"
      deliver_extra:
        chat_id: "-1001234567890"
        message_thread_id: "42"
```

如果在 `deliver_extra` 中未指定 `chat_id`，则消息将回退到为目标平台配置的主频道中发送。

---

## GitHub PR 审核（分步指南）{#github-pr-review}

本指南将帮助您为每个拉取请求设置自动代码审核功能。

### 1. 在 GitHub 中创建 webhook

1. 进入您的仓库 → **Settings** → **Webhooks** → **Add webhook**
2. 将 **Payload URL** 设置为 `http://your-server:8644/webhooks/github-pr`
3. 将 **Content type** 设置为 `application/json`
4. 设置的 **Secret** 需与您的路由配置一致（例如 `github-webhook-secret`）
5. 在 **Which events?** 下方，选择 **Let me select individual events** 并勾选 **Pull requests**
6. 点击 **Add webhook**

### 2. 添加路由配置

按照上述示例，将 `github-pr` 路由添加到您的 `~/.hermes/config.yaml` 文件中。

### 3. 确保 `gh` CLI 已完成身份验证

`github_comment` 发送类型会使用 GitHub CLI 来发布评论：

```bash
gh auth login
```

### 4. 进行测试

在代码仓库中创建一个拉取请求。此时 webhook 会被触发，Hermes 会处理该事件，并在拉取请求上留下审核评论。

---

## GitLab Webhook 配置 {#gitlab-webhook-setup}

GitLab 的 webhook 功能原理类似，但采用了不同的认证机制。GitLab 以普通的 `X-Gitlab-Token` 标头形式发送密钥（要求字符串完全匹配，而非 HMAC 加密）。

### 1. 在 GitLab 中创建 webhook

1. 进入你的项目 → **设置** → **Webhooks**
2. 将 **URL** 设置为 `http://your-server:8644/webhooks/gitlab-mr`
3. 输入你的 **Secret token**
4. 选择 **Merge request events**（以及你需要的其他事件类型）
5. 点击 **添加 webhook**

### 2. 添加路由配置

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        gitlab-mr:
          events: ["merge_request"]
          secret: "your-gitlab-secret-token"
          prompt: |
            Review this merge request:
            Project: {project.path_with_namespace}
            MR !{object_attributes.iid}: {object_attributes.title}
            Author: {object_attributes.last_commit.author.name}
            URL: {object_attributes.url}
            Action: {object_attributes.action}
          deliver: "log"
```

## 交付选项 {#delivery-options}

`deliver` 字段用于控制在处理完 webhook 事件后，将智能体的响应发送到何处。

| Deliver Type | Description |
|-------------|-------------|
| `log` | Logs the response to the gateway log output. This is the default and is useful for testing. |
| `github_comment` | Posts the response as a PR/issue comment via the `gh` CLI. Requires `deliver_extra.repo` and `deliver_extra.pr_number`. The `gh` CLI must be installed and authenticated on the gateway host (`gh auth login`). |
| `telegram` | Routes the response to Telegram. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `discord` | Routes the response to Discord. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `slack` | Routes the response to Slack. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `signal` | Routes the response to Signal. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `sms` | Routes the response to SMS via Twilio. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `whatsapp` | Routes the response to WhatsApp. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `matrix` | Routes the response to Matrix. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `mattermost` | Routes the response to Mattermost. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `homeassistant` | Routes the response to Home Assistant. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `email` | Routes the response to Email. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `dingtalk` | Routes the response to DingTalk. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `feishu` | Routes the response to Feishu/Lark. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `wecom` | Routes the response to WeCom. Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `weixin` | Routes the response to Weixin (WeChat). Uses the home channel, or specify `chat_id` in `deliver_extra`. |
| `bluebubbles` | Routes the response to BlueBubbles (iMessage). Uses the home channel, or specify `chat_id` in `deliver_extra`. |

若需实现跨平台消息推送，目标平台也必须在网关中处于启用状态并已建立连接。如果在 `deliver_extra` 参数中未指定 `chat_id`，响应将会发送至该平台配置的默认频道。

---

## 直接推送模式 {#direct-delivery-mode}

默认情况下，每个 webhook POST 请求都会触发智能体运行——请求中的数据内容会作为提示语，由智能体进行处理，随后将处理结果返回。因此，每次事件都会消耗 LLM 令牌。

对于仅需**发送纯文本通知**的场景——无需智能体进行推理或循环处理，只需直接传递消息——可在路由配置中设置 `deliver_only: true`。此时，生成的 `prompt` 模板将直接作为消息正文，适配器会将其直接发送至预设的推送目标。

### 何时使用直接推送模式

- **外部服务推送**——当 Supabase/Firebase 的数据库发生变更时触发 webhook → 立即通过 Telegram 通知用户
- **监控警报**——Datadog/Grafana 的警报 webhook → 将信息推送到 Discord 频道
- **智能体间通信**——智能体 A 通知智能体 B 的用户某项长时间运行的任务已完成
- **后台任务完成**——Cron 作业执行完毕 → 将结果发布到 Slack

优势：

- **零 LLM 标记消耗**——无需调用智能体  
- **亚秒级响应速度**——仅需一次适配器调用，无需进行推理循环  
- **与智能体模式相同的安全性**——仍采用 HMAC 认证、速率限制、幂等性处理以及请求体大小限制等安全机制  
- **同步响应机制**——一旦消息送达成功，POST 请求将返回 `200 OK` 状态码；若目标端拒绝接收，则返回 `502` 状态码，从而让上游服务能够智能地实现重试  

### 示例：通过 Supabase 向 Telegram 推送消息

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "global-secret"
      routes:
        antenna-matches:
          secret: "antenna-webhook-secret"
          deliver: "telegram"
          deliver_only: true
          prompt: "🎉 New match: {match.user_name} matched with you!"
          deliver_extra:
            chat_id: "{match.telegram_chat_id}"
```

您的 Supabase 边缘函数会使用 HMAC-SHA256 对有效载荷进行签名，然后通过 POST 请求将其发送至 `https://your-server:8644/webhooks/antenna-matches`。Webhook 适配器会验证该签名，根据有效载荷中的内容渲染模板，再将结果发送至 Telegram，最后返回 `200 OK` 状态码。

### 示例：通过 CLI 动态订阅

```bash
hermes webhook subscribe antenna-matches \
  --deliver telegram \
  --deliver-chat-id "123456789" \
  --deliver-only \
  --prompt "🎉 New match: {match.user_name} matched with you!" \
  --description "Antenna match notifications"
```

### 响应码

| 状态码 | 含义 |
|--------|------|
| `200 OK` | 交付成功。响应体为：`{"status": "delivered", "route": "...", "target": "...", "delivery_id": "..."}` |
| `200 OK` (status=duplicate) | 在幂等性超时时间（1小时）内存在重复的 `X-GitHub-Delivery` ID，因此不会重新交付。 |
| `401 Unauthorized` | HMAC签名无效或缺失。 |
| `400 Bad Request` | JSON响应体格式错误。 |
| `404 Not Found` | 路由名称未知。 |
| `413 Payload Too Large` | 响应体大小超过了 `max_body_bytes` 的限制。 |
| `429 Too Many Requests` | 超过了该路由的速率限制。 |
| `502 Bad Gateway` | 目标适配器拒绝了消息或发生了异常。错误信息会在服务器端记录；为避免泄露适配器内部细节，响应体仅显示通用的“交付失败”提示。 |

### 配置注意事项

- 若设置 `deliver_only: true`，则 `deliver` 必须是一个有效的目标地址。若设置为 `deliver: log`（或省略 `deliver`）则会在启动时被拒绝——如果发现配置有误，适配器将拒绝启动。
- 在直接交付模式下，`skills` 字段会被忽略（因为没有代理在运行，无需注入技能）。
- 模板渲染使用与代理模式相同的 `{dot.notation}` 语法，包括 `{__raw__}` 标记。
- 幂等性处理同样依赖 `X-GitHub-Delivery` / `X-Request-ID` 头部信息——使用相同 ID 进行的重试将返回 `status=duplicate`，且不会重新交付。

---

## 动态订阅（CLI）{#dynamic-subscriptions}

除了在 `config.yaml` 中配置静态路由外，您还可以使用 `hermes webhook` CLI 命令动态创建 Webhook 订阅。当代理本身需要设置基于事件的触发机制时，此功能尤为实用。

### 创建订阅

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New issue #{issue.number}: {issue.title}\nBy: {issue.user.login}\n\n{issue.body}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789" \
  --description "Triage new GitHub issues"
```

该接口会返回 webhook 地址以及自动生成的 HMAC 密钥。请将您的服务配置为向该地址发送 POST 请求。

### 列出订阅项

```bash
hermes webhook list
```

### 取消订阅

```bash
hermes webhook remove github-issues
```

### 测试订阅功能

```bash
hermes webhook test github-issues
hermes webhook test github-issues --payload '{"issue": {"number": 42, "title": "Test"}}'
```

### 动态订阅的工作原理

- 订阅信息存储在 `~/.hermes/webhook_subscriptions.json` 文件中  
- 每当收到新请求时，webhook适配器会立即热加载该文件（基于修改时间控制，开销极低）  
- `config.yaml` 中定义的静态路由始终优先于同名动态路由  
- 动态订阅与静态路由使用相同的路由格式及功能（事件、提示模板、技能、消息传递方式等）  
- 无需重启网关——完成订阅后立即生效  

### 由智能体驱动的订阅

在 `webhook-subscriptions` 技能的引导下，智能体可通过终端工具创建订阅。只需要求智能体“为GitHub Issues设置webhook”，它就会自动执行相应的 `hermes webhook subscribe` 命令。  

---

## 按路由划分的工具集 {#per-route-toolsets}

Webhook智能体默认仅使用经过严格限制的工具集（`web_search`、`web_extract`、`vision_analyze`、`clarify`），因为webhook请求可能包含不可信的第三方内容——绝不能让公开的PR标题或问题评论擅自侵入用户的终端界面。  

对于**可信**的路由——例如本地主机运行的系统监控进程或内部CI系统——您可以仅为该路由授予更广泛的功能权限，而无需影响其他所有webhook路由：

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        oom-emergency:
          secret: "monitor-secret"
          prompt: "Memory emergency: {detail}. Diagnose with ps/free/py-spy and report."
          toolsets: ["terminal", "file", "code_execution", "web"]
          deliver: "telegram"
```

对于动态订阅，可直接编辑 `~/.hermes/webhook_subscriptions.json` 文件，添加 `toolsets` 键即可：

```json
{
  "oom-emergency": {
    "secret": "...",
    "prompt": "...",
    "toolsets": ["terminal", "file", "web"],
    "deliver": "telegram"
  }
}
```

行为与安全特性：

- 路由列表会**替代**该路由执行任务时平台级的 webhook 工具集解析机制（两者不会合并）。
- 名称验证遵循与 `platform_toolsets` 配置相同的流程——未知名称以及平台限制的工具集将被直接忽略。
- `hermes webhook subscribe` 明确**不支持**工具集参数。高级工具的授权需通过手动编辑配置文件实现，因此运行时自行创建订阅的智能体无法自动获得 `terminal` 权限。
- 仅应将高级工具集授予那些您能完全控制发送方、且拥有有效 HMAC 密钥的路由。任何能够向该路由发送经过有效签名处理的负载的人，实际上都在使用具备这些工具的智能体。

---

## 安全性 {#security}

Webhook 适配器采用了多层安全防护机制：

### HMAC 签名验证

适配器会根据不同来源采用相应的方法，对传入的 webhook 签名进行验证：

- **GitHub**：使用 `X-Hub-Signature-256` 标头——该标头为以 `sha256=` 开头的 HMAC-SHA256 十六进制摘要。  
- **GitLab**：使用 `X-Gitlab-Token` 标头——只需与预设的密钥字符串完全匹配即可。  
- **标准 Webhooks**：使用 `webhook-id`、`webhook-timestamp` 和 `webhook-signature` 标头——签名内容格式为 `{id}.{timestamp}.{raw_body}`，并附加 `v1,<base64-hmac-sha256>` 格式的签名。  
- **通用类型（V2，推荐）**：使用 `X-Webhook-Signature-V2` 和 `X-Webhook-Timestamp` 标头——签名内容为 `<timestamp>.<body>` 的 HMAC-SHA256 十六进制摘要。时间戳必须位于服务器时间的 ±300 秒范围内，这样才能防止被截获的请求被后续重放。  
- **通用类型（V1，旧版）**：使用 `X-Webhook-Signature` 标头——仅包含请求体本身的原始 HMAC-SHA256 十六进制摘要。为保持向后兼容性，该格式仍被支持，但不存在防重放机制（被截获的请求可无限次重放）；网关会在每个路由上记录一次弃用警告。建议所有发送方切换至 V2 格式。  

如果已配置密钥，但未使用任何已识别的签名标头，则该请求将被拒绝。  

### 必须设置密钥  

每个路由都必须拥有一个密钥——该密钥可直接在路由上设置，也可从全局 `secret` 中继承。若路由未设置密钥，适配器在启动时将会因错误而失败。仅在开发或测试环境中，可将密钥设置为 `"INSECURE_NO_AUTH"` 以完全跳过验证流程。

当启用多配置文件路由功能时，路由的 `profile` 字段会将该密钥绑定到特定的执行目标。不包含 `profile` 字段的路由则仅支持默认配置文件。即便请求携带有效的路由签名，只要其 `/p/<profile>/` 前缀与路由绑定信息不匹配，仍会被拒绝。

`INSECURE_NO_AUTH` 仅在网关绑定到回环地址（如 `127.0.0.1`、`localhost`、`::1`）时才会被接受。若该参数与 `0.0.0.0` 或局域网 IP 这类非回环地址结合使用，适配器将拒绝启动——此举旨在防止意外在公共接口上暴露未经身份验证的端点。

### 速率限制

默认情况下，每条路由的请求速率限制为**每分钟 30 次**（采用固定时间窗口算法）。如需全局配置此限制，请进行相应设置：

```yaml
platforms:
  webhook:
    extra:
      rate_limit: 60  # requests per minute
```

超过限制的请求将会收到 `429 Too Many Requests` 的响应。

### 可重试性

交付标识符（来自 `X-GitHub-Delivery`、`svix-id`、`webhook-id`、`X-Request-ID` 或时间戳作为备用）会被缓存 **1 小时**。重复的交付操作（例如 webhook 重试）会以 `200` 响应被静默跳过，从而避免代理程序重复运行。

### 请求体大小限制

超过 **1 MB** 的有效载荷在读取之前就会被拒绝。可对此进行配置：

```yaml
platforms:
  webhook:
    extra:
      max_body_bytes: 2097152  # 2 MB
```

### 已验证并不等同于可信

:::warning
**HMAC验证用于确认_发送方_的身份，而非_内容_的真实性。** 一个有效的签名仅能证明该请求来自掌握对应路由密钥的实体（例如GitHub），但无法说明请求体中的_业务字段_由谁编写——PR标题、提交信息、问题描述以及任何其他上游文本都可能由任意第三方生成，因此必须视为不可信内容。

这一信任模型同样适用于智能体读取的所有内容：网页、文件和工具输出都属于不可信输入。Hermes既无法也不可能通过黑名单机制可靠地净化这些不可信文本；因为措辞、编码和翻译方式都极易让此类防护被绕过。**真正的信任边界在于智能体的功能范围，而非输入渠道。** 应从强化智能体功能层面着手进行防护：

- **为运行环境创建沙箱隔离。** 当网关暴露在互联网上时，应通过 Docker 或 SSH 终端后端（或在虚拟机中）来运行它，这样即便遭到劫持，攻击者也无法影响主机本身。
- **限制工具使用范围。** 如果任务仅需要读取和汇总信息，可在由 webhook 触发的会话中禁用 `terminal`、`file` 以及外出操作类工具。功能越少，一旦载荷字段中被注入恶意指令，其造成的影响范围也会越小。
- **对所有破坏性或向外发送数据的操作保持审批机制。** 这样可以防止被注入的指令在无人监控的情况下执行。
- **精简模板结构。** 建议使用包含命名字段（如 `{pull_request.title}`）的特定 `prompt`，而非使用 `{__raw__}` 或会输出整个载荷的空白模板，这样只有你希望传递的字段才会进入提示词中。
:::

---

## 故障排除 {#troubleshooting}

### webhook 无法送达

- 确认端口已开放，并且从 webhook 发送端能够访问该端口。
- 检查防火墙规则——端口 `8644`（或你配置的其他端口）必须处于开放状态。
- 确认 URL 路径正确：`http://your-server:8644/webhooks/<route-name>`。
- 使用 `/health` 接口确认服务器正在运行。

### 签名验证失败

- 确保你的路由配置中的密钥与 webhook 发送端配置的密钥完全一致。
- 对于 GitHub，该密钥是基于 HMAC 的——请检查 `X-Hub-Signature-256` 字段。
- 对于 GitLab，该密钥则是简单的令牌匹配——请检查 `X-Gitlab-Token` 字段。
- 查看网关日志中是否有“签名无效”的警告信息。

### 事件被忽略

- 确保事件类型存在于您路由的 `events` 列表中  
- GitHub 事件使用的值为 `pull_request`、`push`、`issues`（即 `X-GitHub-Event` 请求头中的值）  
- GitLab 事件使用的值为 `merge_request`、`push`（即 `X-GitLab-Event` 请求头中的值）  
- 若 `events` 为空或未设置，则会接受所有事件  

### Agent无响应  

- 在前台运行网关以查看日志：`hermes gateway run`  
- 检查提示模板是否正确渲染  
- 确认交付目标已配置且处于连接状态  

### 出现重复响应  

- 冲突处理缓存应可避免此问题——请检查 webhook 源是否发送了交付 ID 请求头（如 `X-GitHub-Delivery`、`svix-id`、`webhook-id` 或 `X-Request-ID`）  
- 交付 ID 的缓存有效期为1小时  

### `gh` CLI错误（GitHub评论发送相关）  

- 在网关主机上运行 `gh auth login`  
- 确保已登录的 GitHub 用户具有该仓库的写入权限  
- 检查 `gh` 已安装且路径已添加到系统环境变量中  

---

## 环境变量 {#environment-variables}

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `WEBHOOK_ENABLED` | 启用webhook平台适配器 | `false` |
| `WEBHOOK_PORT` | 用于接收webhook的HTTP服务器端口 | `8644` |
| `WEBHOOK_SECRET` | 全局HMAC密钥（当路由未指定自身密钥时作为备用） | _(无)_ |
