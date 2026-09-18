---
sidebar_position: 11
sidebar_label: "GitHub PR Reviews via Webhook"
title: "Automated GitHub PR Comments with Webhooks"
description: "Connect Hermes to GitHub so it automatically fetches PR diffs, reviews code changes, and posts comments — triggered by webhooks with no manual prompting"
---

# 利用 Webhook 自动在 GitHub PR 中添加评论

本指南将指导您将 Hermes Agent 与 GitHub 相连接，使其能够自动获取拉取请求的差异内容、分析代码变更，并在收到 Webhook 事件触发后自动发布评论，而无需人工干预。

每当有新的 PR 被创建或现有 PR 被更新时，GitHub 会向您的 Hermes 实例发送一个 Webhook POST 请求。Hermes 会启动相应的 Agent，通过指令让其使用 `gh` CLI 获取差异信息，随后将处理结果回复到对应的 PR 讨论帖中。

:::提示 需要更简单的设置且无需公开端点？
如果您没有公开 URL 或希望快速开始使用，可以参考[构建 GitHub PR 审核 Agent](./github-pr-review-agent.md)——该方案通过定时任务定期轮询 PR 活动，可在 NAT 和防火墙环境后正常运行。
:::

:::信息 参考文档
如需了解完整的 Webhook 平台参考资料（包括所有配置选项、传输类型、动态订阅功能以及安全模型），请参阅[Webhooks](/user-guide/messaging/webhooks)文档。
:::

:::警告 指令注入风险
Webhook 的负载数据由攻击者控制——PR 标题、提交信息及描述中可能包含恶意指令。如果您的 Webhook 端点暴露在互联网上，建议在沙箱环境（如 Docker、SSH 后端）中运行网关。详情请参见下方的[安全注意事项](#security-notes)部分。
:::

---

## 前提条件

- 已安装并正在运行 Hermes Agent（包含 `hermes gateway`）  
- 已在网关主机上安装 [`gh` CLI](https://cli.github.com/) 并完成身份验证（执行 `gh auth login`）  
- 一个可公开访问的 Hermes 实例地址（如在本机运行，请参考[使用 ngrok 进行本地测试](#local-testing-with-ngrok)）  
- 对对应 GitHub 仓库的管理员权限（用于管理 webhook）  

---

## 第 1 步 — 启用 webhook 平台

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
| `secret`（路由级）| 该路由对应的HMAC密钥。若未指定，则回退使用全局配置中的`extra.secret`。 |
| `events` | 需要接收的`X-GitHub-Event`请求头值列表。空列表表示接收所有事件。 |
| `prompt` | 模板内容；`{field}`和`{nested.field}`会从GitHub发送的负载数据中提取对应值。 |
| `deliver` | 通过`gh pr comment`命令发布`github_comment`类型的内容；`log`则仅将信息写入网关日志。 |
| `deliver_extra.repo` | 从负载数据中提取的目标仓库地址，例如`org/repo`格式。 |
| `deliver_extra.pr_number` | 从负载数据中提取的PR编号。 |

:::注意 负载数据不包含代码内容
GitHub webhook发送的负载数据包含PR的元数据（标题、描述、分支名称、URL等），但**不包含代码差异内容**。上述prompt会指示智能体运行`gh pr diff`命令来获取实际的代码变更内容。默认的`hermes-webhook`工具集被刻意限制了功能（仅支持网络搜索/提取、图像识别、信息澄清——**不支持终端操作**），因为webhook负载数据可能包含不可信的内容。若希望该路由能够使用`gh`命令，需在路由配置中添加针对该路由的工具集权限：`toolsets: ["terminal", "web"]`——详情请参阅[按路由配置工具集](/docs/user-guide/messaging/webhooks#per-route-toolsets)。
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

1. 进入您的仓库 → **Settings** → **Webhooks** → **Add webhook**
2. 填写以下信息：
   - **Payload URL：** `https://your-public-url.example.com/webhooks/github-pr-review`
   - **Content type：** `application/json`
   - **Secret：** 与路由配置中设置的 `secret` 值相同
   - **Which events？** → 选择特定事件 → 勾选 **Pull requests**
3. 点击 **Add webhook**

GitHub 会立即发送一个 `ping` 事件以确认连接。该事件可安全忽略——因为它不在您的 `events` 列表中——并且会返回 `{"status": "ignored", "event": "ping"}`。该事件仅在 DEBUG 级别被记录，因此在默认日志级别下不会显示在控制台。

---

## 第 4 步 — 创建一个测试 Pull Request

创建一个分支，推送更改，然后打开一个 PR。30–90 秒后（具体时间取决于 PR 的规模和模型），Hermes 应会发布一条审核评论。

如需实时跟踪智能体的处理进度：

```bash
tail -f "${HERMES_HOME:-$HOME/.hermes}/logs/gateway.log"
```

## 使用 ngrok 进行本地测试

如果 Hermes 正在您的笔记本电脑上运行，可借助 [ngrok](https://ngrok.com/) 来将其暴露出来：

```bash
ngrok http 8644
```

复制 `https://...ngrok-free.app` 这一网址，并将其作为您的 GitHub Payload URL。在免费的 ngrok 计划中，该网址会在 ngrok 重启时发生变动——因此您需要在每次使用时更新 GitHub webhook 配置。而付费的 ngrok 账户则可获得静态域名。

您可以直接使用 `curl` 工具对静态路由进行功能测试，无需拥有 GitHub 账户或创建真实的 Pull Request。

:::提示 在本地测试时请使用 `deliver: log`
在测试期间，请将配置中的 `deliver: github_comment` 更改为 `deliver: log`。否则，代理会尝试在测试载荷中的虚拟仓库 `org/repo#99` 下发布评论，从而导致测试失败。在确认提示输出正常后，再将其改回 `deliver: github_comment` 即可。
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

接着即可观察代理的运行情况：
```bash
tail -f "${HERMES_HOME:-$HOME/.hermes}/logs/gateway.log"
```

:::note  
`hermes webhook test <name>` 仅适用于通过 `hermes webhook subscribe` 创建的**动态订阅**。它不会读取 `config.yaml` 中的路由配置。  
:::

---

## 筛选特定操作  

GitHub 会为多种操作发送 `pull_request` 事件，例如：`opened`、`synchronize`、`reopened`、`closed`、`labeled` 等。`events` 列表可通过 `X-GitHub-Event` 请求头值进行筛选，而路由级别的 `filters` 则可以依据 `action` 等负载字段进一步缩小范围。  

第一步中的提示已解决了这一问题，它会指示智能体在遇到 `closed` 和 `labeled` 事件时提前停止处理。  

:::warning 智能体仍会继续运行并消耗令牌  
虽然“在此处停止”的指令能够避免无意义的处理，但智能体仍会为每一个 `pull_request` 事件执行完全部流程，而不会因操作类型不同而有所区别。建议在智能体启动之前就进行筛选。

```yaml
filters:
  - field: "action"
    in: ["opened", "synchronize", "reopened"]
```

对于存储量较大的代码库，您仍然可以通过 GitHub Actions 工作流来实现上游筛选，该工作流会根据条件调用您的 webhook URL。
:::

> 该系统不支持 Jinja2 或条件模板语法。仅支持 `{field}` 和 `{nested.field}` 这两种替换方式，其他所有内容都会原样传递给代理。

---

## 使用技能以实现统一的审查风格

通过加载 [Hermes 技能](/user-guide/features/skills)，可为代理设定统一的审查角色。请在 `config.yaml` 文件的 `platforms.webhook.extra.routes` 中为对应路由添加 `skills` 参数：

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

> **注意：** 仅会加载列表中第一个被找到的技能。Hermes 不支持同时加载多个技能——后续的条目将被忽略。

---

## 直接将响应发送到 Slack 或 Discord

请在路由中的 `deliver` 和 `deliver_extra` 字段中替换为目标平台的相关配置：

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

目标平台也必须在网关中处于启用状态并已建立连接。如果未指定`chat_id`，响应将发送至该平台配置的主频道。

有效的`deliver`值包括：`log` · `github_comment` · `telegram` · `discord` · `slack` · `signal` · `sms`

---

## GitLab支持

该适配器同样适用于GitLab。GitLab使用`X-Gitlab-Token`进行身份验证（采用简单字符串匹配，而非HMAC）——Hermes可自动处理这两种方式。

对于事件过滤，GitLab会将`X-GitLab-Event`设置为`Merge Request Hook`、`Push Hook`、`Pipeline Hook`等值。在`events`配置中需使用与实际相同的头部值：

```yaml
events:
  - Merge Request Hook
```

GitLab 的 payload 字段与 GitHub 不同——例如，合并请求的标题对应 `{object_attributes.title}`，而合并请求编号则对应 `{object_attributes.iid}`。要了解完整的 payload 结构，最简单的方法是在 webhook 设置中使用 GitLab 的 **Test** 按钮，并结合查看 **Recent Deliveries** 日志。另一种方法是在路由配置中省略 `prompt` 参数——这样 Hermes 会以格式化 JSON 的形式将完整 payload 直接传递给代理，而代理的响应（可在带有 `deliver: log` 标记的网关日志中查看）则会说明其结构。

---

## 安全注意事项

- **切勿在生产环境中使用 `INSECURE_NO_AUTH`**——该模式会完全禁用签名验证，仅适用于本地开发。
- 应定期更换 webhook 密钥，并同时在 GitHub（webhook 设置）和 `config.yaml` 文件中更新该密钥。
- 默认情况下，每条路由的请求速率限制为每分钟 30 次（可通过 `extra.rate_limit` 参数进行配置）。超过此限制将会返回 `429` 错误。
- 通过 1 小时的幂等性缓存来避免重复处理（即 webhook 重试）。缓存键的优先级为：若存在则使用 `X-GitHub-Delivery`，否则使用 `X-Request-ID`，最后是毫秒级时间戳。如果未设置这两种标识符，则不会对重试请求进行去重处理。
- **提示注入风险**：合并请求的标题、描述以及提交信息都由攻击者控制，恶意合并请求可能会试图操纵代理的行为。在将网关暴露于公共网络时，建议在沙箱环境（如 Docker 容器或虚拟机）中运行它。

---

## 故障排除

| 症状 | 检查项 |
|---|---|
| `401 Invalid signature` | config.yaml 中的密钥与 GitHub webhook 的密钥不一致 |
| `404 Unknown route` | URL 中的路由名称与 `routes:` 配置中的键不匹配 |
| `429 Rate limit exceeded` | 每个路由的请求频率超过 30 次/分钟——通常在从 GitHub 界面重新发送测试事件时会出现此问题；请等待一分钟或调整 `extra.rate_limit` 参数 |
| 未发布评论 | 未安装 `gh` 工具、该工具不在系统 PATH 路径中，或未完成身份验证（需执行 `gh auth login`） |
| Agent 已运行但无评论生成 | 请查看网关日志——即便 Agent 的输出为空或仅为 “SKIP”，系统仍会尝试发送内容 |
| 端口已被占用 | 修改 config.yaml 中的 `extra.port` 参数 |
| Agent 已运行但仅审核 PR 描述 | 提示语中未包含 `gh pr diff` 指令——因此差异内容并未包含在 webhook 的负载数据中 |
| 无法看到 ping 事件 | 被忽略的事件仅在 DEBUG 日志级别返回 `{"status":"ignored","event":"ping"}` ——请查看 GitHub 的发送日志（路径：仓库 → 设置 → Webhooks → 所选 webhook → 最近的发送记录） |

**GitHub 的“最近发送记录”标签页**（路径：仓库 → 设置 → Webhooks → 所选 webhook）会显示每次内容发送时的完整请求头、负载数据、HTTP 状态码及响应体。这是无需查看服务器日志即可快速诊断故障的最有效方法。

---

## 完整配置参考文档

```yaml
platforms:
  webhook:
    enabled: true
    extra:
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

## 下一步计划？

- **[基于定时任务的 PR 审核功能](./github-pr-review-agent.md)** — 按预定时间间隔自动检查 PR，无需公共接口  
- **[Webhook 使用指南](/user-guide/messaging/webhooks)** — Webhook 平台的完整配置参考文档  
- **[构建插件](/developer-guide/plugins)** — 将审核逻辑封装为可共享的插件  
- **[用户配置文件](/user-guide/profiles)** — 运行具有独立内存和配置的专用审核者配置文件
