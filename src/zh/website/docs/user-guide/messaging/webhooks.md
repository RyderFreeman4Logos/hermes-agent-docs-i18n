---
sidebar_position: 13
title: "Webhooks"
description: "Receive events from GitHub, GitLab, and other services to trigger Hermes agent runs"
---

# Webhooks

可从外部服务（如 GitHub、GitLab、JIRA、Stripe 等）接收事件，并自动触发 Hermes Agent 的运行。Webhook 适配器会运行一个 HTTP 服务器，用于接收 POST 请求、验证 HMAC 签名、将请求数据转换为 Agent 可处理的提示语，然后将响应发送回原始服务或另一个已配置的平台。

Agent 会对这些事件进行处理，可通过在 PR 上发表评论、向 Telegram/Discord 发送消息或记录处理结果等方式进行响应。

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
2. 在 `config.yaml` 中定义路由，**或**使用 `hermes webhook subscribe` 动态创建路由。
3. 将您的服务指向 `http://your-server:8644/webhooks/<route-name>`。

---

## 设置

有两种方式可以启用 Webhook 适配器。

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

```json
{"status": "ok", "platform": "webhook"}
```

## 配置路由 {#configuring-routes}

路由用于定义如何处理不同的 webhook 来源。每个路由都是您在 `config.yaml` 文件中的 `platforms.webhook.extra.routes` 下的一个命名条目。

### 路由属性

| 属性 | 是否必填 | 描述 |
|------|----------|------|
| `events` | 否 | 需要接收的事件类型列表（例如 `["pull_request"]`）。如果为空，则接收所有事件。事件类型可从 `X-GitHub-Event`、`X-GitLab-Event` 或请求负载中的 `event_type` 获取。 |
| `secret` | **是** | 用于签名验证的 HMAC 密钥。如果未在路由中设置，将回退使用全局 `secret`。如需仅用于测试，可将其设置为 `"INSECURE_NO_AUTH"`（跳过验证）。 |
| `prompt` | 否 | 使用点号语法访问负载的模板字符串（例如 `{pull_request.title}`）。如果省略此参数，则会将完整的 JSON 负载原样放入提示信息中。需注意，负载中的字段是不可信的——详见 [“已认证不代表可信”](#authenticated-does-not-mean-trusted)。 |
| `filters` | 否 | 在身份验证、请求体过滤和事件过滤之后，以及在由智能体处理或直接发送响应之前执行的声明式负载过滤器。不匹配的情况会返回 `{"status":"ignored","reason":"filter"}`，并返回 HTTP 200 状态码。 |
| `script` | 否 | 位于 `~/.hermes/scripts/` 目录下的过滤/转换脚本。Webhook 负载会以 JSON 格式通过标准输入传递给该脚本。脚本的输出 JSON 会在模板渲染之前替换原始负载；如果输出为文本，则会作为 `script_output` 暴露；若输出为空、为 `[SILENT]` 状态或退出码非零，则会忽略该 Webhook。 |
| `skills` | 否 | 用于在智能体运行时加载的技能名称列表。 |
| `deliver` | 否 | 响应的发送目标：`github_comment`、`telegram`、`discord`、`slack`、`signal`、`sms`、`whatsapp`、`matrix`、`mattermost`、`homeassistant`、`email`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot`，或默认值 `log`。 |
| `deliver_extra` | 否 | 额外的发送配置——具体键值取决于 `deliver` 的类型（例如 `repo`、`pr_number`、`chat_id`）。其值支持与 `prompt` 相同的 `{dot.notation}` 模板语法。 |
| `deliver_only` | 否 | 如果设置为 `true`，则完全跳过智能体处理——直接使用渲染后的 `prompt` 模板作为要发送的实际消息。这种方式无需消耗 LLM 资源，响应速度可在秒级完成。具体使用场景可参考 [直接发送模式](#direct-delivery-mode)。此时要求 `deliver` 必须是真实的目标地址（不能为 `log`）。 |

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

当某个提供方发送的内容较为丰富的事件流，但仅部分载荷需要唤醒智能体或触发“仅交付”模式时，可使用 `filters` 功能。这些过滤器会在签名验证、消息体解析以及事件处理之后，但在提示语渲染、重试机制启用、智能体调度或直接消息交付之前执行。

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

字段路径采用点号表示法。`payload.foo` 会在存在顶层 `payload` 对象时从其读取数据，而对于扁平结构的数据则直接从 webhook 的根部分中读取。`event` / `event_type` 会与解析后的事件类型相匹配，而 `headers.<Name>` 用于读取请求头信息。

### 脚本过滤器与转换功能

当声明式过滤器无法满足需求时，可使用脚本功能。脚本必须存储在当前激活配置文件的 `~/.hermes/scripts/` 目录下；相对路径将在此目录中解析，且禁止访问该目录之外的路径。`.sh` 和 `.bash` 脚本会通过 bash 执行，而其他所有扩展名的脚本则通过当前的 Python 解释器运行。

路由传递的负载数据会以 JSON 格式发送到标准输入流中：

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

脚本输出结果：

- JSON 格式的标准输出将替代 `prompt` 和 `deliver_extra` 所使用的负载内容。
- 非 JSON 格式的文本标准输出则作为 `script_output` 添加到负载中。
- 若标准输出为空、内容为 `[SILENT]`、`{"__hermes_ignore__": true}`、发生超时、脚本不存在或退出码非零，系统将返回 HTTP 200 状态码，并附带信息 `{"status":"ignored","reason":"script"}`。

### 提示词模板

提示词采用点号语法来访问 webhook 负载中的嵌套字段：

- `{pull_request.title}` 对应 `payload["pull_request"]["title"]`
- `{repository.full_name}` 对应 `payload["repository"]["full_name"]`
- `{__raw__}` —— 一种特殊标记，用于以缩进格式输出**整个负载内容**（最多显示 4000 个字符）。适用于需要完整上下文的监控警报或通用 webhook 场景。
- 若某个键不存在，则会以 `{key}` 的形式原样保留（不会报错）。
- 嵌套的字典和列表会被序列化为 JSON 格式，最多显示 2000 个字符。

您可以将 `{__raw__}` 与常规模板变量混合使用：

```yaml
prompt: "PR #{pull_request.number} by {pull_request.user.login}: {__raw__}"
```

如果某个路由未配置 `prompt` 模板，则整个有效载荷将以缩进格式的 JSON 形式输出（内容长度超过 4000 个字符时会被截断）。

相同的点号表示法模板也适用于 `deliver_extra` 参数中的值。

### 论坛主题推送

在向 Telegram 发送 webhook 响应时，您可以通过在 `deliver_extra` 中添加 `message_thread_id`（或 `thread_id`）来指定特定的论坛主题：

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
4. 设置的 **Secret** 需与您的路由配置相匹配（例如 `github-webhook-secret`）
5. 在 **Which events?** 下，选择 **Let me select individual events** 并勾选 **Pull requests**
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

GitLab 的 webhook 功能原理类似，但采用了不同的认证机制。GitLab 以普通的 `X-Gitlab-Token` 请求头形式传递密钥（要求字符串完全匹配，而非 HMAC 校验）。

### 1. 在 GitLab 中创建 webhook

1. 进入你的项目 → **设置** → **Webhooks**
2. 将 **URL** 设置为 `http://your-server:8644/webhooks/gitlab-mr`
3. 输入你的 **密钥令牌**
4. 选择 **合并请求事件**（以及你需要的其他事件）
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

`deliver` 字段用于控制代理在处理完 webhook 事件后，将响应发送到何处。

| 交付类型 | 描述 |
|-----------|------|
| `log` | 将响应记录到网关的日志输出中。这是默认选项，非常适合用于测试。 |
| `github_comment` | 通过 `gh` CLI 将响应作为 PR/issue 的评论发布。需要提供 `deliver_extra.repo` 和 `deliver_extra.pr_number` 参数。必须在网关主机上安装并完成 `gh` CLI 的身份认证（执行 `gh auth login`）。 |
| `telegram` | 将响应发送到 Telegram。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `discord` | 将响应发送到 Discord。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `slack` | 将响应发送到 Slack。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `signal` | 将响应发送到 Signal。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `sms` | 通过 Twilio 将响应发送为短信。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `whatsapp` | 将响应发送到 WhatsApp。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `matrix` | 将响应发送到 Matrix。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `mattermost` | 将响应发送到 Mattermost。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `homeassistant` | 将响应发送到 Home Assistant。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `email` | 将响应发送为电子邮件。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `dingtalk` | 将响应发送到 DingTalk。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `feishu` | 将响应发送到 Feishu/Lark。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `wecom` | 将响应发送到 WeCom。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `weixin` | 将响应发送到微信。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |
| `bluebubbles` | 将响应发送到 BlueBubbles（iMessage）。系统会使用默认频道，或可在 `deliver_extra` 中指定 `chat_id`。 |

若需在跨平台环境中进行交付，目标平台也必须在网关中启用并完成连接。如果在 `deliver_extra` 中未指定 `chat_id`，则响应将被发送到该平台配置的默认频道。

---

## 直接交付模式 {#direct-delivery-mode}

默认情况下，每次 webhook POST 请求都会触发一次代理运行——请求中的负载会被转换为提示词，由代理进行处理，之后再将代理的响应发送出去。这种方式会导致每次事件都会消耗 LLM 令牌。

对于那些仅需**推送纯文本通知**的场景——无需进行任何推理，也无需代理循环处理，只需直接发送消息——可在路由配置中设置 `deliver_only: true`。此时，经过处理的 `prompt` 模板将直接作为消息内容，适配器会将其直接发送到已配置的交付目标。

### 何时使用直接交付模式

- **外部服务推送**——当 Supabase/Firebase 的数据库发生变更时触发 webhook → 立即通过 Telegram 通知用户
- **监控警报**——Datadog/Grafana 的警报 webhook → 将信息推送到 Discord 频道
- **代理间通信**——代理 A 通知代理 B 的用户，告知某个长时间运行的任务已经完成
- **后台任务完成**——Cron 作业执行完毕 → 将结果发布到 Slack

优点：

- **无需消耗 LLM 令牌**——不会调用代理
- **交付速度极快**——仅需一次适配器调用，无需推理循环
- **安全性与代理模式相同**——仍适用 HMAC 身份验证、速率限制、幂等性处理以及消息大小限制等机制
- **同步响应**——一旦交付成功，POST 请求会返回 `200 OK` 状态码；如果目标端拒绝接收，则返回 `502` 状态码，这样上游服务就可以智能地尝试重试

### 示例：从 Supabase 向 Telegram 推送消息

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

您的 Supabase 边缘函数会使用 HMAC-SHA256 对有效载荷进行签名，然后通过 POST 请求将其发送至 `https://your-server:8644/webhooks/antenna-matches`。Webhook 适配器会验证该签名，根据有效载荷中的模板生成内容并发送至 Telegram，最后返回 `200 OK` 状态码。

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
| `200 OK` (status=duplicate) | 在幂等性超时时间（1小时）内存在重复的 `X-GitHub-Delivery` ID，因此不会再次交付。 |
| `401 Unauthorized` | HMAC签名无效或缺失。 |
| `400 Bad Request` | JSON响应体格式错误。 |
| `404 Not Found` | 路由名称未知。 |
| `413 Payload Too Large` | 响应体大小超过了 `max_body_bytes` 的限制。 |
| `429 Too Many Requests` | 超过了该路由的速率限制。 |
| `502 Bad Gateway` | 目标适配器拒绝了消息或发生了异常。错误信息会在服务器端记录；为避免泄露适配器内部细节，响应体仅显示通用的“交付失败”提示。 |

### 配置注意事项

- 若设置 `deliver_only: true`，则 `deliver` 必须是一个有效的目标地址。若设置为 `deliver: log`（或省略 `deliver`）则会在启动时被拒绝——如果发现配置有误，适配器将拒绝启动。
- 在直接交付模式下，`skills` 字段会被忽略（因为没有运行代理，无需注入技能）。
- 模板渲染使用与代理模式相同的 `{dot.notation}` 语法，包括 `{__raw__}` 标记。
- 幂等性处理同样依赖 `X-GitHub-Delivery` / `X-Request-ID` 头部信息——使用相同 ID 进行的重试将返回 `status=duplicate`，且不会再次执行交付操作。

---

## 动态订阅（CLI）{#dynamic-subscriptions}

除了在 `config.yaml` 中定义静态路由外，您还可以通过 `hermes webhook` CLI 命令动态创建 webhook 订阅。当代理本身需要设置事件驱动触发器时，此功能尤为实用。

### 创建订阅

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New issue #{issue.number}: {issue.title}\nBy: {issue.user.login}\n\n{issue.body}" \
  --deliver telegram \
  --deliver-chat-id "-100123456789" \
  --description "Triage new GitHub issues"
```

该操作会返回 webhook 地址以及自动生成的 HMAC 密钥。请将您的服务配置为向该地址发送 POST 请求。

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
- 每当收到新请求时，webhook适配器会立即热加载该文件（基于修改时间判断，几乎不会产生额外开销）  
- `config.yaml` 中定义的静态路由始终优先于同名动态路由  
- 动态订阅与静态路由使用相同的路由格式及功能（事件、提示模板、技能、消息传递方式等）  
- 无需重启网关——完成订阅后即可立即生效  

### 由智能体驱动的订阅

在 `webhook-subscriptions` 技能的引导下，智能体可通过终端工具创建订阅。只需要求智能体“为GitHub Issues设置webhook”，它就会自动执行相应的 `hermes webhook subscribe` 命令。  

---

## 安全性 {#security}

webhook适配器具备多层安全防护机制：  

### HMAC签名验证

适配器会根据不同来源采用相应方法验证传入的webhook签名：  
- **GitHub**：使用 `X-Hub-Signature-256` 标头——以 `sha256=` 开头的HMAC-SHA256十六进制值  
- **GitLab**：使用 `X-Gitlab-Token` 标头——直接比对密钥字符串  
- **通用型（V2，推荐）**：使用 `X-Webhook-Signature-V2` 和 `X-Webhook-Timestamp` 标头——对 `<timestamp>.<body>` 进行HMAC-SHA256加密后的十六进制值。时间戳（以Unix秒为单位）必须与服务器时间相差在±300秒范围内，以此防止被截获的请求被再次发送。  
- **通用型（V1，旧版）**：使用 `X-Webhook-Signature` 标头——仅包含请求内容的原始HMAC-SHA256十六进制值。为保持向后兼容性仍被支持，但缺乏重放保护（被截获的请求可无限次重复发送）；网关会为每个路由记录一次弃用警告。建议所有发送方切换至V2格式。  

如果已配置密钥但未出现任何有效的签名标头，该请求将被拒绝。  

### 必须设置密钥

每个路由都必须有密钥——要么直接在路由上设置，要么从全局 `secret` 中继承。没有密钥的路由会导致适配器在启动时出现错误。仅在开发/测试环境中，可将密钥设置为 `"INSECURE_NO_AUTH"` 以完全跳过验证流程。  

`INSECURE_NO_AUTH` 仅能在网关绑定到回环地址（如 `127.0.0.1`、`localhost`、`::1`）时使用。若与 `0.0.0.0` 或局域网IP等非回环地址结合使用，适配器将拒绝启动——此举可避免意外在公共接口上暴露未经认证的端点。  

### 速率限制

默认情况下，每个路由的请求速率限制为**每分钟30次**（固定时间窗口计算）。如需全局调整此限制，可进行相应配置：

```yaml
platforms:
  webhook:
    extra:
      rate_limit: 60  # requests per minute
```

超过限制的请求将会收到 `429 Too Many Requests` 的响应。

### 等价性处理

交付编号（来自 `X-GitHub-Delivery`、`X-Request-ID` 或时间戳备用值）会被缓存 **1小时**。对于重复的交付请求（例如 webhook 重试），系统会以 `200` 响应静默跳过，从而避免代理程序重复运行。

### 请求体大小限制

超过 **1 MB** 的有效载荷在读取之前就会被拒绝。如需配置该限制，请进行相应设置：

```yaml
platforms:
  webhook:
    extra:
      max_body_bytes: 2097152  # 2 MB
```

### 已通过验证并不等同于可被信任

:::warning
**HMAC 验证用于确认 _发送方_ 的身份，而非 _内容_ 的真实性。** 一个有效的签名仅能证明请求来自掌握该路由密钥的机构（例如 GitHub），但无法说明负载中的 _业务字段* 是由谁编写的——拉取请求标题、提交信息、问题描述以及任何其他上游文本都可能由第三方撰写，因此必须视为不可信内容。

这一信任模型同样适用于代理程序读取的所有内容：网页、文件和工具输出都属于不可信输入。Hermes 无法——也难以通过黑名单机制——可靠地过滤这些不可信文本；因为措辞、编码和翻译方式都可以轻易绕过此类防护。**真正的信任边界在于代理程序的功能范围，而非输入渠道。** 应从以下方面加强安全措施：

- **为运行环境设置沙箱。** 当网关暴露在互联网上时，应通过 Docker 或 SSH 终端后端（或在虚拟机中）来运行它，从而防止被劫持的请求影响到主机。
- **限制可使用的工具集。** 如果某路由仅需要读取和汇总信息，就应禁用 webhook 触发的会话中的 `terminal`、`file` 以及外部操作类工具。功能越少，一旦负载字段中包含恶意指令，其影响范围也就越小。
- **对任何具有破坏性或外部操作功能的请求保持审批机制**，防止恶意指令在无人监督的情况下被执行。
- **精简提示模板设计。** 尽量使用带有命名字段的特定 `prompt`（如 `{pull_request.title}`），而非使用 `{__raw__}` 或会输出整个负载的空白模板，这样只有你预期的字段才会传递给提示系统。
:::

---

## 故障排除 {#troubleshooting}

### Webhook 无法送达

- 确认端口已开放，并且从 webhook 发送端可以访问该端口。
- 检查防火墙规则——端口 `8644`（或你配置的其他端口）必须处于开放状态。
- 确认 URL 路径正确：`http://your-server:8644/webhooks/<route-name>`。
- 使用 `/health` 接口确认服务器正在运行。

### 签名验证失败

- 确保路由配置中的密钥与 webhook 发送端配置的密钥完全一致。
- 对于 GitHub，其签名基于 HMAC 算法——请检查 `X-Hub-Signature-256` 字段。
- 对于 GitLab，其签名则是普通令牌匹配——请检查 `X-Gitlab-Token` 字段。
- 查看网关日志，寻找“无效签名”相关的警告信息。

### 事件被忽略

- 确认该事件类型存在于路由的 `events` 列表中。
- GitHub 的事件类型包括 `pull_request`、`push`、`issues`（对应 `X-GitHub-Event` 标头值）。
- GitLab 的事件类型包括 `merge_request`、`push`（对应 `X-GitLab-Event` 标头值）。
- 如果 `events` 列表为空或未设置，则所有事件都会被接收。

### 代理程序无响应

- 在前台运行网关以查看日志：`hermes gateway run`。
- 检查提示模板是否能够正确渲染。
- 确认交付目标已配置且连接正常。

### 出现重复响应

- 冲突处理缓存本应能避免此问题——请检查 webhook 发送端是否设置了交付 ID 标头（如 `X-GitHub-Delivery` 或 `X-Request-ID`）。
- 交付 ID 的缓存有效期为 1 小时。

### `gh` CLI 错误（GitHub 评论发送相关）

- 在网关主机上运行 `gh auth login` 命令进行登录。
- 确保已登录的 GitHub 用户拥有该仓库的写入权限。
- 检查 `gh` 工具是否已安装，并且其路径已在系统环境变量中配置。

---

## 环境变量 {#environment-variables}

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `WEBHOOK_ENABLED` | 是否启用 webhook 平台适配器 | `false` |
| `WEBHOOK_PORT` | 用于接收 webhook 的 HTTP 服务器端口 | `8644` |
| `WEBHOOK_SECRET` | 全局 HMAC 密钥（当路由未指定自身密钥时作为备用） | _(无)_ |
