---
sidebar_position: 11
sidebar_label: "GitHub PR Reviews via Webhook"
title: "Automated GitHub PR Comments with Webhooks"
description: "Connect Hermes to GitHub so it automatically fetches PR diffs, reviews code changes, and posts comments — triggered by webhooks with no manual prompting"
---

# 利用 Webhook 自动在 GitHub PR 中添加评论

本指南将指导您将 Hermes Agent 与 GitHub 相连接，使其能够自动获取拉取请求的差异内容、分析代码变更，并在触发 Webhook 事件后无需人工干预即可自动发布评论。

每当有新的 PR 被创建或更新时，GitHub 会向您的 Hermes 实例发送一个 Webhook POST 请求。Hermes 会启动对应的 Agent，通过指令让其使用 `gh` CLI 获取差异信息，随后将处理结果回传至该 PR 的讨论区。

:::tip 需要更简单的设置且无需公开端点？
如果您没有公开 URL 或希望快速入门，可以参考[构建 GitHub PR 审核 Agent](./github-pr-review-agent.md)——该方案通过定时任务定期检查 PR 状态，可在 NAT 和防火墙后方正常运行。
:::

:::info 参考文档
如需了解完整的 Webhook 平台参考信息（包括所有配置选项、传输类型、动态订阅功能以及安全模型），请参阅[Webhooks](/user-guide/messaging/webhooks)文档。
:::

:::warning 指令注入风险
Webhook 的负载数据由攻击者控制——PR 标题、提交信息及描述中可能包含恶意指令。若您的 Webhook 端点暴露在互联网上，建议在沙箱环境（如 Docker、SSH 后端）中运行网关。详情请参阅下方的[安全注意事项](#security-notes)部分。
:::

---

## 前提条件

- 已安装并正在运行的 Hermes Agent（`hermes gateway`）
- 已在网关主机上安装并完成认证的[`gh` CLI](https://cli.github.com/)（执行 `gh auth login` 命令）
- 一个可被公网访问的 Hermes 实例地址（若在本地运行，请参考[使用 ngrok 进行本地测试](#local-testing-with-ngrok)）
- 对对应 GitHub 仓库的管理员权限（用于管理 Webhook）

---

## 第一步 — 启用 Webhook 平台

在您的 `~/.hermes/config.yaml` 文件中添加以下内容：

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644          # default; change if another service occupies this port
      rate_limit: 30      # max requests per minute per route (not a global cap)

      routes:
        github-pr-review:
          secret: "your-webhook-secret-here"   # must match the GitHub webhook secret exactly
          events:
            - pull_request

          # The agent is instructed to fetch the actual diff before reviewing.
          # {number} and {repository.full_name} are resolved from the GitHub payload.
          prompt: |
            A pull request event was received (action: {action}).

            PR #{number}: {pull_request.title}
            Author: {pull_request.user.login}
            Branch: {pull_request.head.ref} → {pull_request.base.ref}
            Description: {pull_request.body}
            URL: {pull_request.html_url}

            If the action is "closed" or "labeled", stop here and do not post a comment.

            Otherwise:
            1. Run: gh pr diff {number} --repo {repository.full_name}
            2. Review the code changes for correctness, security issues, and clarity.
            3. Write a concise, actionable review comment and post it.

          deliver: github_comment
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{number}"
```

**关键字段：**

| 字段 | 描述 |
|---|---|
| `secret`（路由级） | 该路由对应的HMAC密钥。若未指定，则回退使用全局配置中的`extra.secret`。 |
| `events` | 需要接收的`X-GitHub-Event`请求头值列表。空列表表示接收所有事件。 |
| `prompt` | 模板内容；`{field}`和 `{nested.field}`会从GitHub发送的请求体中提取对应值。 |
| `deliver` | 通过`gh pr comment`命令发布`github_comment`类型的内容；`log`则仅将信息写入网关日志。 |
| `deliver_extra.repo` | 从请求体中提取对应的仓库地址，例如`org/repo`格式。 |
| `deliver_extra.pr_number` | 从请求体中提取对应的PR编号。 |

:::注意：请求体不包含代码内容
GitHub webhook发送的请求体包含PR的元数据（标题、描述、分支名称、URL等），但**不包含代码差异内容**。上述模板会指示智能体执行`gh pr diff`命令来获取实际的代码变更内容。默认的`hermes-webhook`工具集中已包含`terminal`工具，因此无需额外配置。
:::

---

## 第2步 — 启动网关

```bash
hermes gateway
```

您应该会看到：

```
[webhook] Listening on 0.0.0.0:8644 — routes: github-pr-review
```

验证其是否正在运行：

```bash
curl http://localhost:8644/health
# {"status": "ok", "platform": "webhook"}
```

---

## 第 3 步 — 在 GitHub 上注册 webhook

1. 进入您的代码仓库 → **Settings** → **Webhooks** → **Add webhook**
2. 填写以下信息：
   - **Payload URL：** `https://your-public-url.example.com/webhooks/github-pr-review`
   - **Content type：** `application/json`
   - **Secret：** 与路由配置中设置的 `secret` 值相同
   - **Which events?** → 选择特定事件 → 勾选 **Pull requests**
3. 点击 **Add webhook**

GitHub 会立即发送一个 `ping` 事件以确认连接。该事件可安全忽略——因为它不在您的 `events` 列表中——且返回值仅为 `{"status": "ignored", "event": "ping"}`。该事件仅在 DEBUG 级别被记录，因此在默认日志级别下不会显示在控制台里。

---

## 第 4 步 — 创建测试 Pull Request

创建一个分支，推送更改，然后打开一个 PR。通常在 30–90 秒内（具体时间取决于 PR 的规模及模型处理速度），Hermes 就会发布审核评论。

如需实时跟踪该智能体的处理进度：

```bash
tail -f "${HERMES_HOME:-$HOME/.hermes}/logs/gateway.log"
```

## 使用 ngrok 进行本地测试

如果 Hermes 正在您的笔记本电脑上运行，可使用 [ngrok](https://ngrok.com/) 来将其暴露出来：

```bash
ngrok http 8644
```

复制 `https://...ngrok-free.app` 这一网址，并将其作为您的 GitHub Payload URL。在免费的 ngrok 计划中，该网址会在 ngrok 重启时发生变动——因此您需要在每次使用前更新 GitHub webhook 配置。而付费的 ngrok 账户则可获得静态域名。

您可以直接使用 `curl` 工具对静态路由进行功能测试，无需拥有 GitHub 账户或创建真实的 Pull Request。

:::提示 在本地测试时请使用 `deliver: log`
在测试期间，请将配置中的 `deliver: github_comment` 更改为 `deliver: log`。否则，代理会尝试在测试载荷中的虚拟仓库 `org/repo#99` 下发布评论，从而导致测试失败。在确认提示信息输出正常后，再将其改回 `deliver: github_comment` 即可。
:::

```bash
SECRET="your-webhook-secret-here"
BODY='{"action":"opened","number":99,"pull_request":{"title":"Test PR","body":"Adds a feature.","user":{"login":"testuser"},"head":{"ref":"feat/x"},"base":{"ref":"main"},"html_url":"https://github.com/org/repo/pull/99"},"repository":{"full_name":"org/repo"}}'
SIG=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -hex | awk '{print "sha256="$2}')

curl -s -X POST http://localhost:8644/webhooks/github-pr-review \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: $SIG" \
  -d "$BODY"
# Expected: {"status":"accepted","route":"github-pr-review","event":"pull_request","delivery_id":"..."}
```

接下来，请观察代理的运行情况：
```bash
tail -f "${HERMES_HOME:-$HOME/.hermes}/logs/gateway.log"
```

:::note
`hermes webhook test <name>` 仅适用于通过 `hermes webhook subscribe` 创建的**动态订阅**。它不会读取 `config.yaml` 中定义的路由。
:::

---

## 筛选特定操作

GitHub 会为多种操作发送 `pull_request` 事件，例如：`opened`、`synchronize`、`reopened`、`closed`、`labeled` 等。`events` 列表仅能通过 `X-GitHub-Event` 请求头值进行筛选——无法在路由层面按操作子类型进行筛选。

第一步中的提示已解决了这一问题，它会指示智能体在遇到 `closed` 和 `labeled` 事件时提前停止处理。

:::warning 智能体仍会运行并消耗令牌
虽然“在此处停止”的指令可以避免无意义的处理，但智能体仍会为每个 `pull_request` 事件执行完全部流程，而不会因操作类型不同而有所区别。GitHub Webhook 仅能按事件类型（如 `pull_request`、`push`、`issues` 等）进行筛选，无法按操作子类型（如 `opened`、`closed`、`labeled`）筛选。在路由层面也不存在针对子操作的筛选功能。对于代码库规模较大的项目，要么接受这一成本，要么通过 GitHub Actions 工作流在上游有条件地调用您的 Webhook URL 来进行筛选。
:::

> 该系统不支持 Jinja2 或条件模板语法。仅支持 `{field}` 和 `{nested.field}` 这两种替换方式。其他所有内容都会原样传递给智能体。

---

## 使用技能以确保一致的审核风格

加载 [Hermes 技能](/user-guide/features/skills)，为智能体设定统一的审核角色。在 `config.yaml` 的 `platforms.webhook.extra.routes` 中，为对应路由添加 `skills` 参数即可：

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        github-pr-review:
          secret: "your-webhook-secret-here"
          events: [pull_request]
          prompt: |
            A pull request event was received (action: {action}).
            PR #{number}: {pull_request.title} by {pull_request.user.login}
            URL: {pull_request.html_url}

            If the action is "closed" or "labeled", stop here and do not post a comment.

            Otherwise:
            1. Run: gh pr diff {number} --repo {repository.full_name}
            2. Review the diff using your review guidelines.
            3. Write a concise, actionable review comment and post it.
          skills:
            - review
          deliver: github_comment
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{number}"
```

> **注意：** 仅会加载列表中第一个匹配到的技能。Hermes 不支持同时加载多个技能——后续的条目将被忽略。

---

## 直接将响应发送到 Slack 或 Discord

请用目标平台对应的参数替换路由中的 `deliver` 和 `deliver_extra` 字段：

```yaml
# Inside platforms.webhook.extra.routes.<route-name>:

# Slack
deliver: slack
deliver_extra:
  chat_id: "C0123456789"   # Slack channel ID (omit to use the configured home channel)

# Discord
deliver: discord
deliver_extra:
  chat_id: "987654321012345678"  # Discord channel ID (omit to use home channel)
```

目标平台也必须在网关中处于启用状态并已建立连接。如果省略了`chat_id`，响应将会发送到该平台配置的默认频道。

有效的`deliver`值包括：`log` · `github_comment` · `telegram` · `discord` · `slack` · `signal` · `sms`

---

## GitLab支持

该适配器同样适用于GitLab。GitLab使用`X-Gitlab-Token`进行身份验证（为简单字符串匹配，而非HMAC格式）——Hermes可自动处理这两种验证方式。

在事件过滤方面，GitLab会将`X-GitLab-Event`设置为`Merge Request Hook`、`Push Hook`、`Pipeline Hook`等值。在`events`配置中需使用与这些头部字段完全一致的值：

```yaml
events:
  - Merge Request Hook
```

GitLab 的请求载荷字段与 GitHub 不同——例如，用于存储合并请求标题的字段为 `{object_attributes.title}`，而用于存储合并请求编号的字段则为 `{object_attributes.iid}`。要了解完整的载荷结构，最简单的方法是在 webhook 设置中使用 GitLab 的**测试**按钮，并结合查看**最近交付记录**日志。另一种方法是在路由配置中省略 `prompt` 参数——这样 Hermes 会以格式化 JSON 的形式将完整载荷直接传递给代理，而代理的响应（可在网关日志中通过 `deliver: log` 查看）则会说明其结构。

---

## 安全注意事项

- **切勿在生产环境中使用 `INSECURE_NO_AUTH`**——该模式会完全关闭签名验证功能，仅适用于本地开发。
- 应定期更换 webhook 密钥，并同时更新 GitHub（webhook 设置）以及 `config.yaml` 文件中的密钥。
- 默认情况下，每条路由的请求速率限制为每分钟 30 次（可通过 `extra.rate_limit` 参数进行调整）。超过此限制将返回 `429` 错误。
- 通过 1 小时的幂等性缓存来避免重复处理（即 webhook 重试）。缓存键的优先级为：若存在则使用 `X-GitHub-Delivery`，否则使用 `X-Request-ID`，再辅以毫秒级时间戳。如果未设置这两种标识符，则不会对重试请求进行去重处理。
- **提示注入风险**：合并请求的标题、描述以及提交信息均由攻击者控制，恶意合并请求可能会试图操纵代理的行为。当网关暴露在公共互联网上时，建议在沙箱环境（如 Docker 容器或虚拟机）中运行它。

---

## 故障排查

| 症状 | 检查项 |
|---|---|
| `401 Invalid signature` | `config.yaml` 中的密钥与 GitHub webhook 的密钥不一致 |
| `404 Unknown route` | URL 中的路由名称与 `routes:` 配置中的键不匹配 |
| `429 Rate limit exceeded` | 超过了每条路由每分钟 30 次的请求限制——通常在从 GitHub 界面重新发送测试事件时会出现此问题；可等待一分钟或提高 `extra.rate_limit` 的值 |
| 未发布评论 | 未安装 `gh` 工具、其路径未被添加到系统环境变量中，或未完成身份验证（需执行 `gh auth login`） |
| 代理已运行但无评论生成 | 查看网关日志——如果代理的输出为空或仅为“SKIP”，仍会尝试完成交付流程 |
| 端口已被占用 | 在 `config.yaml` 中修改 `extra.port` 的值 |
| 代理已运行但仅查看合并请求描述 | 提示内容中未包含 `gh pr diff` 指令——因此 webhook 载荷中不包含代码差异信息 |
| 无法看到 ping 事件 | 被忽略的事件仅在 DEBUG 日志级别返回 `{"status":"ignored","event":"ping"}` ——可查看 GitHub 的交付日志（路径：仓库 → 设置 → Webhooks → 对应的 webhook → 最近交付记录） |

GitHub 的**最近交付记录**标签页（路径：仓库 → 设置 → Webhooks → 对应的 webhook）会显示每次交付的完整请求头、载荷内容、HTTP 状态码以及响应体。这是无需查看服务器日志即可快速诊断问题的最佳方式。

---

## 完整配置参考

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: "0.0.0.0"         # bind address (default: 0.0.0.0)
      port: 8644               # listen port (default: 8644)
      secret: ""               # optional global fallback secret
      rate_limit: 30           # requests per minute per route
      max_body_bytes: 1048576  # payload size limit in bytes (default: 1 MB)

      routes:
        <route-name>:
          secret: "required-per-route"
          events: []            # [] = accept all; otherwise list X-GitHub-Event values
          prompt: ""            # {field} / {nested.field} resolved from payload
          skills: []            # first matching skill is loaded (only one)
          deliver: "log"        # log | github_comment | telegram | discord | slack | signal | sms
          deliver_extra: {}     # repo + pr_number for github_comment; chat_id for others
```

## 接下来有哪些功能？

- **[基于定时任务的 PR 审核](./github-pr-review-agent.md)** — 按预定时间间隔自动检查 PR，无需公共接口  
- **[Webhook 参考文档](/user-guide/messaging/webhooks)** — Webhook 平台的完整配置参考指南  
- **[构建插件](/developer-guide/plugins)** — 将审核逻辑封装为可共享的插件  
- **[用户配置文件](/user-guide/profiles)** — 运行拥有独立内存和配置的专用审核员配置文件
