---
sidebar_position: 15
title: "Automation Blueprints"
description: "Ready-to-use automation blueprints — scheduled tasks, GitHub event triggers, API webhooks, and multi-skill workflows"
---

# 自动化蓝图

这里提供了常见自动化场景的蓝图模板，可直接复制使用。每个蓝图均采用 Hermes 内置的 [cron 计时调度器](/user-guide/features/cron) 实现基于时间的触发，同时通过 [Webhook 平台](/user-guide/messaging/webhooks) 支持事件驱动的触发方式。

所有蓝图均适用于**任意模型**，无需绑定到特定的服务提供商。

如需查看采用表单形式而非 cron 语法的参数化蓝图，请参阅 [自动化蓝图目录](/reference/automation-blueprints-catalog)。

:::提示 三种触发类型
| 触发方式 | 触发条件 | 使用工具 |
|---------|----------|----------|
| **定时触发** | 按固定间隔运行（每小时、每夜、每周） | `cronjob` 工具或 `/cron` 命令 |
| **GitHub 事件触发** | 当有 PR 创建、代码推送、问题提交或 CI 测试结果时触发 | Webhook 平台（`hermes webhook subscribe`） |
| **API 调用触发** | 外部服务向您的端点发送 JSON 数据时触发 | Webhook 平台（通过 config.yaml 路由配置或 `hermes webhook subscribe`） |

以上三种触发方式均支持将结果发送至 Telegram、Discord、Slack、短信、邮件、GitHub 评论或本地文件。
:::

---

## 开发工作流程

### 每夜待办事项分类处理

每晚对新增问题进行标记、优先级排序并生成汇总信息，随后将摘要发布到团队频道中。

**触发方式：** 定时触发（每夜）

```bash
hermes cron create "0 2 * * *" \
  "You are a project manager triaging the NousResearch/hermes-agent GitHub repo.

1. Run: gh issue list --repo NousResearch/hermes-agent --state open --json number,title,labels,author,createdAt --limit 30
2. Identify issues opened in the last 24 hours
3. For each new issue:
   - Suggest a priority label (P0-critical, P1-high, P2-medium, P3-low)
   - Suggest a category label (bug, feature, docs, security)
   - Write a one-line triage note
4. Summarize: total open issues, new today, breakdown by priority

Format as a clean digest. If no new issues, respond with [SILENT]." \
  --name "Nightly backlog triage" \
  --deliver telegram
```

### 自动代码审查功能

在每个拉取请求创建时自动进行审查，并直接在对应请求上发布审查意见。

**触发方式：** GitHub Webhook

**选项 A — 动态订阅（CLI）：**

```bash
hermes webhook subscribe github-pr-review \
  --events "pull_request" \
  --prompt "Review this pull request:
Repository: {repository.full_name}
PR #{pull_request.number}: {pull_request.title}
Author: {pull_request.user.login}
Action: {action}
Diff URL: {pull_request.diff_url}

Fetch the diff with: curl -sL {pull_request.diff_url}

Review for:
- Security issues (injection, auth bypass, secrets in code)
- Performance concerns (N+1 queries, unbounded loops, memory leaks)
- Code quality (naming, duplication, error handling)
- Missing tests for new behavior

Post a concise review. If the PR is a trivial docs/typo change, say so briefly." \
  --skill github-code-review \
  --deliver github_comment
```

**选项 B — 静态路由（config.yaml）：**

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      port: 8644
      secret: "your-global-secret"
      routes:
        github-pr-review:
          events: ["pull_request"]
          secret: "github-webhook-secret"
          prompt: |
            Review PR #{pull_request.number}: {pull_request.title}
            Repository: {repository.full_name}
            Author: {pull_request.user.login}
            Diff URL: {pull_request.diff_url}
            Review for security, performance, and code quality.
          skills: ["github-code-review"]
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{pull_request.number}"
```

接下来在 GitHub 中操作：**设置 → Webhooks → 添加 Webhook**，然后填写以下参数：Payload URL 为 `http://your-server:8644/webhooks/github-pr-review`，内容类型选择 `application/json`，密钥设置为 `github-webhook-secret`，事件类型选择 **Pull requests**。

### 文档偏离检测

系统会每周扫描已合并的 Pull Request，以识别那些需要更新文档的 API 变更。

**触发方式：** 定时扫描（每周一次）

```bash
hermes cron create "0 9 * * 1" \
  "Scan the NousResearch/hermes-agent repo for documentation drift.

1. Run: gh pr list --repo NousResearch/hermes-agent --state merged --json number,title,files,mergedAt --limit 30
2. Filter to PRs merged in the last 7 days
3. For each merged PR, check if it modified:
   - Tool schemas (tools/*.py) — may need docs/reference/tools-reference.md update
   - CLI commands (hermes_cli/commands.py, hermes_cli/main.py) — may need docs/reference/cli-commands.md update
   - Config options (hermes_cli/config.py) — may need docs/user-guide/configuration.md update
   - Environment variables — may need docs/reference/environment-variables.md update
4. Cross-reference: for each code change, check if the corresponding docs page was also updated in the same PR

Report any gaps where code changed but docs didn't. If everything is in sync, respond with [SILENT]." \
  --name "Docs drift detection" \
  --deliver telegram
```

### 依赖项安全审计

每日扫描项目依赖项中存在的已知漏洞。

**触发条件：** 定时任务（每日执行）

```bash
hermes cron create "0 6 * * *" \
  "Run a dependency security audit on the hermes-agent project.

1. cd ~/.hermes/hermes-agent && source .venv/bin/activate
2. Run: pip audit --format json 2>/dev/null || pip audit 2>&1
3. Run: npm audit --json 2>/dev/null (in website/ directory if it exists)
4. Check for any CVEs with CVSS score >= 7.0

If vulnerabilities found:
- List each one with package name, version, CVE ID, severity
- Check if an upgrade is available
- Note if it's a direct dependency or transitive

If no vulnerabilities, respond with [SILENT]." \
  --name "Dependency audit" \
  --deliver telegram
```

## DevOps与监控

### 部署验证

在每次部署完成后自动触发冒烟测试。当部署任务完成时，您的CI/CD流水线会向Webhook发送请求。

**触发方式：** API调用（Webhook）

```bash
hermes webhook subscribe deploy-verify \
  --events "deployment" \
  --prompt "A deployment just completed:
Service: {service}
Environment: {environment}
Version: {version}
Deployed by: {deployer}

Run these verification steps:
1. Check if the service is responding: curl -s -o /dev/null -w '%{http_code}' {health_url}
2. Search recent logs for errors: check the deployment payload for any error indicators
3. Verify the version matches: curl -s {health_url}/version

Report: deployment status (healthy/degraded/failed), response time, any errors found.
If healthy, keep it brief. If degraded or failed, provide detailed diagnostics." \
  --deliver telegram
```

您的 CI/CD 流水线会触发它：

```bash
curl -X POST http://your-server:8644/webhooks/deploy-verify \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$(echo -n '{"service":"api","environment":"prod","version":"2.1.0","deployer":"ci","health_url":"https://api.example.com/health"}' | openssl dgst -sha256 -hmac 'your-secret' | cut -d' ' -f2)" \
  -d '{"service":"api","environment":"prod","version":"2.1.0","deployer":"ci","health_url":"https://api.example.com/health"}'
```

### 警报分类处理

通过将监控警报与最近的变更信息关联起来，从而制定相应的应对方案。该功能支持 Datadog、PagerDuty、Grafana，以及任何能够发送 JSON 数据的警报系统。

**触发方式：** API 调用（Webhook）

```bash
hermes webhook subscribe alert-triage \
  --prompt "Monitoring alert received:
Alert: {alert.name}
Severity: {alert.severity}
Service: {alert.service}
Message: {alert.message}
Timestamp: {alert.timestamp}

Investigate:
1. Search the web for known issues with this error pattern
2. Check if this correlates with any recent deployments or config changes
3. Draft a triage summary with:
   - Likely root cause
   - Suggested first response steps
   - Escalation recommendation (P1-P4)

Be concise. This goes to the on-call channel." \
  --deliver slack
```

### 运行时间监控器

每30分钟检查一次终端节点，仅在出现故障时发送通知。

**触发条件：** 定时任务（每30分钟一次）

```python title="~/.hermes/scripts/check-uptime.py"
import urllib.request, json, time

ENDPOINTS = [
    {"name": "API", "url": "https://api.example.com/health"},
    {"name": "Web", "url": "https://www.example.com"},
    {"name": "Docs", "url": "https://docs.example.com"},
]

results = []
for ep in ENDPOINTS:
    try:
        start = time.time()
        req = urllib.request.Request(ep["url"], headers={"User-Agent": "Hermes-Monitor/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        results.append({"name": ep["name"], "status": resp.getcode(), "ms": elapsed})
    except Exception as e:
        results.append({"name": ep["name"], "status": "DOWN", "error": str(e)})

down = [r for r in results if r.get("status") == "DOWN" or (isinstance(r.get("status"), int) and r["status"] >= 500)]
if down:
    print("OUTAGE DETECTED")
    for r in down:
        print(f"  {r['name']}: {r.get('error', f'HTTP {r[\"status\"]}')} ")
    print(f"\nAll results: {json.dumps(results, indent=2)}")
else:
    print("NO_ISSUES")
```

```bash
hermes cron create "every 30m" \
  "If the script reports OUTAGE DETECTED, summarize which services are down and suggest likely causes. If NO_ISSUES, respond with [SILENT]." \
  --script ~/.hermes/scripts/check-uptime.py \
  --name "Uptime monitor" \
  --deliver telegram
```

## 研究与情报分析

### 竞品代码库监测工具

持续监控竞品的代码库，发现值得关注的 Pull Request、新功能以及架构决策。

**触发方式：** 定时任务（每日执行）

```bash
hermes cron create "0 8 * * *" \
  "Scout these AI agent repositories for notable activity in the last 24 hours:

Repos to check:
- anthropics/claude-code
- openai/codex
- All-Hands-AI/OpenHands
- Aider-AI/aider

For each repo:
1. gh pr list --repo <repo> --state all --json number,title,author,createdAt,mergedAt --limit 15
2. gh issue list --repo <repo> --state open --json number,title,labels,createdAt --limit 10

Focus on:
- New features being developed
- Architectural changes
- Integration patterns we could learn from
- Security fixes that might affect us too

Skip routine dependency bumps and CI fixes. If nothing notable, respond with [SILENT].
If there are findings, organize by repo with brief analysis of each item." \
  --skill competitive-pr-scout \
  --name "Competitor scout" \
  --deliver telegram
```

### AI新闻摘要

每周汇总人工智能/机器学习领域最新进展。

**触发条件：** 定时任务（每周执行一次）

```bash
hermes cron create "0 9 * * 1" \
  "Generate a weekly AI news digest covering the past 7 days:

1. Search the web for major AI announcements, model releases, and research breakthroughs
2. Search for trending ML repositories on GitHub
3. Check arXiv for highly-cited papers on language models and agents

Structure:
## Headlines (3-5 major stories)
## Notable Papers (2-3 papers with one-sentence summaries)
## Open Source (interesting new repos or major releases)
## Industry Moves (funding, acquisitions, launches)

Keep each item to 1-2 sentences. Include links. Total under 600 words." \
  --name "Weekly AI digest" \
  --deliver telegram
```

### 带备注的论文摘要功能

每日扫描 arXiv 并将摘要保存至您的笔记系统中。

**触发条件：** 定时任务（每日）

```bash
hermes cron create "0 8 * * *" \
  "Search arXiv for the 3 most interesting papers on 'language model reasoning' OR 'tool-use agents' from the past day. For each paper, create an Obsidian note with the title, authors, abstract summary, key contribution, and potential relevance to Hermes Agent development." \
  --skill arxiv --skill obsidian \
  --name "Paper digest" \
  --deliver local
```

## GitHub 事件自动化功能

### 问题自动标记

自动为新创建的问题添加标签并作出响应。

**触发条件：** GitHub webhook

```bash
hermes webhook subscribe github-issues \
  --events "issues" \
  --prompt "New GitHub issue received:
Repository: {repository.full_name}
Issue #{issue.number}: {issue.title}
Author: {issue.user.login}
Action: {action}
Body: {issue.body}
Labels: {issue.labels}

If this is a new issue (action=opened):
1. Read the issue title and body carefully
2. Suggest appropriate labels (bug, feature, docs, security, question)
3. If it's a bug report, check if you can identify the affected component from the description
4. Post a helpful initial response acknowledging the issue

If this is a label or assignment change, respond with [SILENT]." \
  --deliver github_comment
```

### CI失败分析

用于分析CI构建失败的原因，并在相关PR中生成诊断报告。

**触发方式：** GitHub webhook

```yaml
# config.yaml route
platforms:
  webhook:
    enabled: true
    extra:
      routes:
        ci-failure:
          events: ["check_run"]
          secret: "ci-secret"
          prompt: |
            CI check failed:
            Repository: {repository.full_name}
            Check: {check_run.name}
            Status: {check_run.conclusion}
            PR: #{check_run.pull_requests.0.number}
            Details URL: {check_run.details_url}

            If conclusion is "failure":
            1. Fetch the log from the details URL if accessible
            2. Identify the likely cause of failure
            3. Suggest a fix
            If conclusion is "success", respond with [SILENT].
          deliver: "github_comment"
          deliver_extra:
            repo: "{repository.full_name}"
            pr_number: "{check_run.pull_requests.0.number}"
```

### 在不同仓库之间自动同步端口变更

当某个仓库中的 Pull Request 被合并时，自动将相应的变更同步到另一个仓库中。

**触发方式：** GitHub Webhook

```bash
hermes webhook subscribe auto-port \
  --events "pull_request" \
  --prompt "PR merged in the source repository:
Repository: {repository.full_name}
PR #{pull_request.number}: {pull_request.title}
Author: {pull_request.user.login}
Action: {action}
Merge commit: {pull_request.merge_commit_sha}

If action is 'closed' and pull_request.merged is true:
1. Fetch the diff: curl -sL {pull_request.diff_url}
2. Analyze what changed
3. Determine if this change needs to be ported to the Go SDK equivalent
4. If yes, create a branch, apply the equivalent changes, and open a PR on the target repo
5. Reference the original PR in the new PR description

If action is not 'closed' or not merged, respond with [SILENT]." \
  --skill github-pr-workflow \
  --deliver log
```

## 业务运营

### Stripe支付监控

追踪支付事件并获取失败情况的汇总信息。

**触发方式：** API调用（Webhook）

```bash
hermes webhook subscribe stripe-payments \
  --events "payment_intent.succeeded,payment_intent.payment_failed,charge.dispute.created" \
  --prompt "Stripe event received:
Event type: {type}
Amount: {data.object.amount} cents ({data.object.currency})
Customer: {data.object.customer}
Status: {data.object.status}

For payment_intent.payment_failed:
- Identify the failure reason from {data.object.last_payment_error}
- Suggest whether this is a transient issue (retry) or permanent (contact customer)

For charge.dispute.created:
- Flag as urgent
- Summarize the dispute details

For payment_intent.succeeded:
- Brief confirmation only

Keep responses concise for the ops channel." \
  --deliver slack
```

### 日度收入汇总

每日清晨自动汇总核心业务指标。

**触发条件：** 定时任务（每日执行）

```bash
hermes cron create "0 8 * * *" \
  "Generate a morning business metrics summary.

Search the web for:
1. Current Bitcoin and Ethereum prices
2. S&P 500 status (pre-market or previous close)
3. Any major tech/AI industry news from the last 12 hours

Format as a brief morning briefing, 3-4 bullet points max.
Deliver as a clean, scannable message." \
  --name "Morning briefing" \
  --deliver telegram
```

## 多技能工作流

### 安全审计流程

通过整合多种技能，实现每周全面的安全审查。

**触发条件：** 定时任务（每周执行）

```bash
hermes cron create "0 3 * * 0" \
  "Run a comprehensive security audit of the hermes-agent codebase.

1. Check for dependency vulnerabilities (pip audit, npm audit)
2. Search the codebase for common security anti-patterns:
   - Hardcoded secrets or API keys
   - SQL injection vectors (string formatting in queries)
   - Path traversal risks (user input in file paths without validation)
   - Unsafe deserialization (pickle.loads, yaml.load without SafeLoader)
3. Review recent commits (last 7 days) for security-relevant changes
4. Check if any new environment variables were added without being documented

Write a security report with findings categorized by severity (Critical, High, Medium, Low).
If nothing found, report a clean bill of health." \
  --skill codebase-security-audit \
  --name "Weekly security audit" \
  --deliver telegram
```

### 内容处理流程

按照既定计划开展内容的研究、撰写与准备工作。

**触发条件：** 计划时间（每周）

```bash
hermes cron create "0 10 * * 3" \
  "Research and draft a technical blog post outline about a trending topic in AI agents.

1. Search the web for the most discussed AI agent topics this week
2. Pick the most interesting one that's relevant to open-source AI agents
3. Create an outline with:
   - Hook/intro angle
   - 3-4 key sections
   - Technical depth appropriate for developers
   - Conclusion with actionable takeaway
4. Save the outline to ~/drafts/blog-$(date +%Y%m%d).md

Keep the outline to ~300 words. This is a starting point, not a finished post." \
  --name "Blog outline" \
  --deliver local
```

## 快速参考指南

### Cron 计时表达式语法

| 表达式 | 含义 |
|---------|------|
| `every 30m` | 每 30 分钟执行一次 |
| `every 2h` | 每 2 小时执行一次 |
| `0 2 * * *` | 每天凌晨 2:00 执行 |
| `0 9 * * 1` | 每周一上午 9:00 执行 |
| `0 9 * * 1-5` | 工作日每周日上午 9:00 执行 |
| `0 3 * * 0` | 每周日凌晨 3:00 执行 |
| `0 */6 * * *` | 每 6 小时执行一次 |

### 交付目标

| 目标类型 | 标识参数 | 备注 |
|----------|---------|-------|
| 同一聊天窗口 | `--deliver origin` | 默认值——将结果发送至任务创建处 |
| 本地文件 | `--deliver local` | 仅保存输出结果，不发送通知 |
| Telegram | `--deliver telegram` | 发送到主频道，或使用 `telegram:CHAT_ID` 指定特定频道 |
| Discord | `--deliver discord` | 发送到主频道，或使用 `discord:CHANNEL_ID` 指定特定频道 |
| Slack | `--deliver slack` | 发送到主频道 |
| SMS | `--deliver sms:+15551234567` | 直接发送至手机号码 |
| 特定主题帖 | `--deliver telegram:-100123:456` | 发送到 Telegram 论坛的特定主题帖 |

### Webhook 模板变量

| 变量名 | 描述 |
|--------|-------|
| `{pull_request.title}` | Pull Request 的标题 |
| `{issue.number}` | Issue 的编号 |
| `{repository.full_name}` | 仓库地址，格式为 `owner/repo` |
| `{action}` | 事件类型（如新建、关闭等） |
| `{__raw__}` | 完整的 JSON 数据内容（长度超过 4000 字符时会被截断） |
| `{sender.login}` | 触发该事件的 GitHub 用户账号 |

### [SILENT] 模式

当 Cron 任务的响应中包含 `[SILENT]` 时，将不会发送任何通知。此模式可用于在无需通知的运行场景下避免消息刷屏：

```
If nothing noteworthy happened, respond with [SILENT].
```

这意味着只有当智能体有内容需要汇报时，您才会收到通知。
