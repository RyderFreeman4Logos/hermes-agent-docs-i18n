# Hermes Agent 自三月起已支持“Routines”功能

Anthropic刚刚发布了[Claude Code Routines](https://claude.com/blog/introducing-routines-in-claudace-code)——这是一种支持定时任务、GitHub事件触发以及API驱动的智能体运行功能。它将提示词、代码仓库和连接器整合在一起，并在他们的基础设施上运行。

这确实是一项很棒的功能，我们早在两个月前就已经实现了它。

---

## 三种触发方式对比

Claude Code Routines提供了三种触发自动化流程的方式：

**1. 定时触发（cron）**
> “每晚凌晨2点：从Linear中获取最亟需解决的缺陷，尝试修复它，并创建一个PR草稿。”

Hermes的对应功能——目前也已可用：
```bash
hermes cron create "0 2 * * *" \
  "Pull the top bug from the issue tracker, attempt a fix, and open a draft PR." \
  --name "Nightly bug fix" \
  --deliver telegram
```

**2. GitHub 事件（Webhook）**  
> “标记涉及 /auth-provider 模块的 Pull Request，并将其发布到 #auth-changes 频道中。”  

Hermes 对应功能——当前已可用：
```bash
hermes webhook subscribe auth-watch \
  --events "pull_request" \
  --prompt "PR #{pull_request.number}: {pull_request.title} by {pull_request.user.login}. Check if it touches the auth-provider module. If yes, summarize the changes." \
  --deliver slack
```

**3. API触发机制**  
> “读取警报内容，确定负责处理该警报的服务，然后将处理摘要发布到#oncall频道。”  

Hermes中的对应功能——目前已可用：
```bash
hermes webhook subscribe alert-triage \
  --prompt "Alert: {alert.name} — Severity: {alert.severity}. Find the owning service, investigate, and post a triage summary with proposed first steps." \
  --deliver slack
```

在他们的博客文章中提到的所有应用场景——任务队列分类、文档版本管理问题、部署验证、警报关联、库迁移以及定制化的 Pull Request 审核——都已有可用的 Hermes 实现方案。无需新增任何功能，该方案自 2026 年 3 月以来便已投入实际使用。

---

## 不同之处

| | Claude Code Routines | Hermes Agent |
|---|---|---|
| **定时任务** | ✅ 基于时间调度 | ✅ 支持任意 cron 表达式以及易于理解的间隔设置 |
| **GitHub 触发机制** | ✅ PR、问题反馈、代码推送事件 | ✅ 通过 webhook 订阅支持任何 GitHub 事件 |
| **API 触发机制** | ✅ 向专用端点发送 POST 请求 | ✅ 通过带 HMAC 认证的 webhook 路由发送 POST 请求 |
| **MCP 连接器** | ✅ 原生连接器 | ✅ 完整的 MCP 客户端支持 |
| **脚本预处理** | ❌ 不支持 | ✅ 可在代理执行前运行 Python 脚本以注入上下文信息 |
| **技能链式调用** | ❌ 不支持 | ✅ 每个自动化流程可加载多个技能 |
| **每日使用限额** | 每日 5–25 次运行 | **无限制** |
| **模型选择** | 仅限 Claude 模型 | **支持任意模型**——Claude、GPT、Gemini、DeepSeek、Qwen 以及本地模型 |
| **消息发送目标** | GitHub 评论 | Telegram、Discord、Slack、短信、邮件、GitHub 评论、webhook 以及本地文件 |
| **基础设施** | Anthropic 的服务器 | **用户自选基础设施**——VPS、家庭服务器或笔记本电脑 |
| **数据存储位置** | Anthropic 的云平台 | **用户的设备** |
| **成本结构** | 需购买 Pro/Max/Team/Enterprise 订阅套餐 | 仅需使用 API 密钥，费用按实际使用量计算 |
| **开源属性** | 非开源 | **开源**——采用 MIT 许可证 |

---

## Hermes 能做到而 Routines 无法实现的功能

### 脚本注入功能

可在代理执行之前先运行一段 Python 脚本。该脚本的标准输出内容将作为上下文信息传递给代理。脚本负责处理那些机械性的任务（如数据获取、差异对比、计算操作），而代理则负责进行逻辑推理。

```bash
hermes cron create "every 1h" \
  "If CHANGE DETECTED, summarize what changed. If NO_CHANGE, respond with [SILENT]." \
  --script ~/.hermes/scripts/watch-site.py \
  --name "Pricing monitor" \
  --deliver telegram
```

`[SILENT]` 模式意味着只有在实际发生事件时才会向您发送通知，绝无垃圾信息。

### 多技能工作流

将各种专业技能串联起来。每项技能都能让智能体掌握特定的功能，而提示词则负责将这些技能整合在一起。

```bash
hermes cron create "0 8 * * *" \
  "Search arXiv for papers on language model reasoning. Save the top 3 as Obsidian notes." \
  --skills "arxiv,obsidian" \
  --name "Paper digest"
```

### 无处不在的交付能力

一次自动化操作，覆盖任意目标地点：

```bash
--deliver telegram                      # Telegram home channel
--deliver discord                       # Discord home channel  
--deliver slack                         # Slack channel
--deliver sms:+15551234567              # Text message
--deliver telegram:-1001234567890:42    # Specific Telegram forum topic
--deliver local                         # Save to file, no notification
```

### 无需绑定特定模型

您的夜间任务分类工作可在 Claude 上运行，部署验证可在 GPT 上执行，而注重成本控制的监控任务则可选择在 DeepSeek 或本地模型上运行。同一个自动化系统，适配任意后端。

---

## 局限性揭示真相

Claude Code Routines 的使用限制为：Pro 版每日 **5 个任务**，Enterprise 版则为 **25 个**，这就是其上限。

Hermes 则没有每日使用限额。如果您愿意，一天内甚至可以运行 500 个自动化任务。唯一的限制在于 API 预算，以及您需要自行决定为不同任务选择何种模型。

在 Sonnet 上进行夜间任务积压分类的成本大约在 0.02 至 0.05 美元之间，而在 DeepSeek 上执行监控检查的成本则仅为几美分。成本控制完全由您掌握。

---

## 开始使用

Hermes Agent 是开源且免费的。其内置的自动化基础设施——包括定时调度器、Webhook 平台、技能系统以及多平台任务分发功能——均已准备就绪。

```bash
pip install hermes-agent
hermes setup
```

30秒即可设置定时任务：
```bash
hermes cron create "0 9 * * 1" \
  "Generate a weekly AI news digest. Search the web for major announcements, trending repos, and notable papers. Keep it under 500 words with links." \
  --name "Weekly digest" \
  --deliver telegram
```

60秒内即可设置GitHub Webhook：
```bash
hermes gateway setup    # enable webhooks
hermes webhook subscribe pr-review \
  --events "pull_request" \
  --prompt "Review PR #{pull_request.number}: {pull_request.title}" \
  --skills "github-code-review" \
  --deliver github_comment
```

完整自动化模板库：[hermes-agent.nousresearch.com/docs/guides/automation-templates](https://hermes-agent.nousresearch.com/docs/guides/automation-templates)

技术文档：[hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com)

GitHub仓库：[github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)

---

*Hermes Agent由[Nous Research](https://nousresearch.com)开发。它采用开源架构，不受模型限制，可在您的基础设施上运行。*
