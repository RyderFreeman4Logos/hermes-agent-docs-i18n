---
sidebar_position: 10
title: "Tutorial: GitHub PR Review Agent"
description: "Build an automated AI code reviewer that monitors your repos, reviews pull requests, and delivers feedback — hands-free"
---

# 教程：构建 GitHub PR 审核智能代理

**问题所在：** 团队提交 PR 的速度远快于您进行审核的效率，导致 PR 堆积数日无人处理。由于没有时间检查，初级开发人员不得不直接合并含有错误的代码。您每天早晨都耗费在查看代码差异上，而无暇进行实际开发。

**解决方案：** 部署一个全天候监控您代码仓库的 AI 智能代理，自动审核每一份新提交的 PR，检测其中的错误、安全问题及代码质量问题，并向您发送汇总报告——这样您只需专注于那些确实需要人工判断的 PR 即可。

**您将完成的内容：**

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│   Cron Timer  ──▶  Hermes Agent  ──▶  GitHub API  ──▶  Review     │
│   (every 2h)       + gh CLI           (PR diffs)       delivery   │
│                    + skill                             (Telegram, │
│                    + memory                            Discord,   │
│                                                        local)     │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

本指南利用**定时任务（cron jobs）**按固定时间间隔轮询相关 Pull Request，无需任何服务器或公共端点，即便处于 NAT 和防火墙之后也能正常工作。

:::提示 需要实时审核功能吗？
如果您拥有可用的公共端点，可以参考[通过 Webhook 实现 GitHub PR 自动评论](./webhook-github-pr-review.md)——当 Pull Request 被创建或更新时，GitHub 会立即将相关事件推送到 Hermes。
:::

---

## 先决条件

- 已安装**Hermes Agent**——请参阅[安装指南](/getting-started/installation)
- 已运行用于执行定时任务的**Gateway**：
  ```bash
  hermes gateway install   # Install as a service
  # or
  hermes gateway           # Run in foreground
  ```
- **已安装 GitHub CLI（`gh`）并完成身份验证**：
  ```bash
  # Install
  brew install gh        # macOS
  sudo apt install gh    # Ubuntu/Debian

  # Authenticate
  gh auth login
  ```
- **消息发送方式已配置**（可选）——[Telegram](/user-guide/messaging/telegram) 或 [Discord](/user-guide/messaging/discord)

:::提示 没有消息发送功能？无需担心
可以使用 `deliver: "local"` 将评论保存到 `~/.hermes/cron/output/` 目录中。这非常适合在设置正式通知之前进行测试。
:::

---

## 第 1 步：验证配置

确保 Hermes 能够访问 GitHub。先发起一次聊天测试：

```bash
hermes
```

使用简单命令进行测试：

```
Run: gh pr list --repo NousResearch/hermes-agent --state open --limit 3
```

您应该会看到一份待处理的拉取请求列表。如果操作成功，那就表示您已经准备就绪。

---

## 第 2 步：尝试手动审核

仍在聊天界面中，让 Hermes 对一个真实的拉取请求进行审核：

```
Review this pull request. Read the diff, check for bugs, security issues,
and code quality. Be specific about line numbers and quote problematic code.

Run: gh pr diff 3888 --repo NousResearch/hermes-agent
```

Hermes 将执行以下操作：
1. 运行 `gh pr diff` 命令以获取代码变更内容；
2. 完整阅读所有的差异对比信息；
3. 撰写结构化的审查报告，并明确指出具体问题。

如果您对审查质量满意，就可以将其自动化了。

---

## 第 3 步：创建审查技能

技能可为 Hermes 提供统一的审查准则，这些准则会在不同会话及定时任务中保持一致。若没有技能作为支撑，审查质量将会参差不齐。

```bash
mkdir -p ~/.hermes/skills/code-review
```

创建 `~/.hermes/skills/code-review/SKILL.md` 文件：

```markdown
---
name: code-review
description: Review pull requests for bugs, security issues, and code quality
---

# Code Review Guidelines

When reviewing a pull request:

## What to Check
1. **Bugs** — Logic errors, off-by-one, null/undefined handling
2. **Security** — Injection, auth bypass, secrets in code, SSRF
3. **Performance** — N+1 queries, unbounded loops, memory leaks
4. **Style** — Naming conventions, dead code, missing error handling
5. **Tests** — Are changes tested? Do tests cover edge cases?

## Output Format
For each finding:
- **File:Line** — exact location
- **Severity** — Critical / Warning / Suggestion
- **What's wrong** — one sentence
- **Fix** — how to fix it

## Rules
- Be specific. Quote the problematic code.
- Don't flag style nitpicks unless they affect readability.
- If the PR looks good, say so. Don't invent problems.
- End with: APPROVE / REQUEST_CHANGES / COMMENT
```

请验证该技能是否已成功加载——启动 `hermes` 后，您应在启动时的技能列表中看到 `code-review`。  

---

## 第 4 步：告知它您的团队规范

唯有如此，该代码审查工具才能真正发挥效用。请开启一个会话，向 Hermes 告知您团队的编码标准：

```
Remember: In our backend repo, we use Python with FastAPI.
All endpoints must have type annotations and Pydantic models.
We don't allow raw SQL — only SQLAlchemy ORM.
Test files go in tests/ and must use pytest fixtures.
```

```
Remember: In our frontend repo, we use TypeScript with React.
No `any` types allowed. All components must have props interfaces.
We use React Query for data fetching, never useEffect for API calls.
```

这些记忆会永久保存——审核者无需每次被告知，就能自动遵循您的规范。  

## 第 5 步：创建自动化的 Cron 任务  

现在将所有组件整合起来。创建一个每 2 小时运行一次的 Cron 任务：

```bash
hermes cron create "0 */2 * * *" \
  "Check for new open PRs and review them.

Repos to monitor:
- myorg/backend-api
- myorg/frontend-app

Steps:
1. Run: gh pr list --repo REPO --state open --limit 5 --json number,title,author,createdAt
2. For each PR created or updated in the last 4 hours:
   - Run: gh pr diff NUMBER --repo REPO
   - Review the diff using the code-review guidelines
3. Format output as:

## PR Reviews — today

### [repo] #[number]: [title]
**Author:** [name] | **Verdict:** APPROVE/REQUEST_CHANGES/COMMENT
[findings]

If no new PRs found, say: No new PRs to review." \
  --name "pr-review" \
  --deliver telegram \
  --skill code-review
```

确认该任务已被安排：

```bash
hermes cron list
```

### 其他有用的调度规则

| 调度规则 | 触发时间 |
|----------|----------|
| `0 */2 * * *` | 每2小时一次 |
| `0 9,13,17 * * 1-5` | 工作日每天三次 |
| `0 9 * * 1` | 每周周一上午汇总 |
| `30m` | 每30分钟一次（适用于高流量仓库） |

---

## 第6步：按需运行

不想等待定时调度？可以手动触发它：

```bash
hermes cron run pr-review
```

或者直接在聊天会话中操作：

```
/cron run pr-review
```

## 深入探索

### 直接将评论发布到 GitHub

无需通过 Telegram 传递内容，让智能体直接在 PR 上进行评论：

在您的 cron 脚本中添加以下内容：

```
After reviewing, post your review:
- For issues: gh pr review NUMBER --repo REPO --comment --body "YOUR_REVIEW"
- For critical issues: gh pr review NUMBER --repo REPO --request-changes --body "YOUR_REVIEW"
- For clean PRs: gh pr review NUMBER --repo REPO --approve --body "Looks good"
```

:::警告
请确保 `gh` 已配置具有 `repo` 权限范围的访问令牌。代码审查将以 `gh` 所认证的账户身份发布。
:::

### 每周 PR 仪表板

在每周一早上生成您所有仓库的概览报告：

```bash
hermes cron create "0 9 * * 1" \
  "Generate a weekly PR dashboard:
- myorg/backend-api
- myorg/frontend-app
- myorg/infra

For each repo show:
1. Open PR count and oldest PR age
2. PRs merged this week
3. Stale PRs (older than 5 days)
4. PRs with no reviewer assigned

Format as a clean summary." \
  --name "weekly-dashboard" \
  --deliver telegram
```

### 多仓库监控

只需在提示词中添加更多仓库即可扩展监控范围。该智能体会按顺序处理这些仓库——无需额外配置。

---

## 故障排除

### “gh: command not found”错误
网关运行在精简环境中。请确保`gh`命令已添加到系统PATH路径中，然后重启网关。

### 审核反馈过于笼统
1. 添加`code-review`技能（第3步）
2. 通过记忆功能向Hermes传授您的代码规范（第4步)
3. 智能体掌握的您的技术栈相关信息越多，审核反馈的质量就越高。

### Cron任务无法运行
```bash
hermes gateway status    # Is the gateway running?
hermes cron list         # Is the job enabled?
```

### 请求频率限制
对于已通过身份验证的用户，GitHub允许每小时发送5,000次API请求。每次PR审核大约需要3到5次请求（包括列表信息、代码差异对比以及可选的评论）。即便每天审核100个PR，也完全在限制范围内。

---

## 接下来可以做什么？

- **[基于Webhook的PR审核功能](./webhook-github-pr-review.md)** —— 当PR被创建时即可立即触发审核（需要一个公开端点）
- **[每日简报机器人](/guides/daily-briefing-bot)** —— 将PR审核与晨间新闻摘要结合在一起
- **[构建插件](/guides/build-a-hermes-plugin)** —— 将审核逻辑封装为可共享的插件
- **[专用审核者配置文件](/user-guide/profiles)** —— 创建拥有独立内存和配置的专属审核者账户
- **[备用提供商机制](/user-guide/features/fallback-providers)** —— 即使某个提供商出现故障，也能确保审核功能正常运行
