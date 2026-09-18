---
sidebar_position: 11
title: "Automate Anything with Cron"
description: "Real-world automation patterns using Hermes cron — monitoring, reports, pipelines, and multi-skill workflows"
---

# 利用 Cron 自动化任何任务

[每日简报机器人教程](/guides/daily-briefing-bot)介绍了相关基础知识。本指南则进一步深入——为你展示五种可直接应用于实际工作流的自动化模式。

如需完整的功能参考，请查看[定时任务（Cron）](/user-guide/features/cron)。

:::info 核心概念
Cron 作业会在全新的智能体会话中运行，不会保留当前对话的任何记忆。因此，提示语必须**完全独立**——需包含智能体所需了解的所有信息。
:::

:::tip 不需要大语言模型？你有两种无需使用令牌的方案。
- **周期性监控模式**：脚本可直接生成所需的消息内容（如内存警报、磁盘警报、心跳检测等）：可使用[仅脚本型的 Cron 作业](/guides/cron-script-only)。采用相同的调度机制，但不依赖大语言模型。你可以在对话中让 Hermes 为你设置此类任务——`cronjob` 工具会自动判断是否使用 `no_agent=True` 并为你生成脚本。
- **从正在运行的脚本中执行单次操作**：适用于持续集成步骤、提交后钩子、部署脚本或外部调度的监控程序：可使用[`hermes send`](/guides/pipe-script-output)功能，将标准输出或文件直接发送到 Telegram / Discord / Slack 等平台，而无需配置 Cron 任务。
:::

---

## 模式 1：网站变更监控器

持续监视某个网址的变动，仅在内容发生变化时发出通知。

这里的“秘密武器”就是 `script` 参数。每次执行之前，都会先运行一段 Python 脚本，其标准输出内容将作为智能体的工作上下文。该脚本负责处理那些机械性的任务（如数据获取、差异对比），而智能体则负责进行逻辑判断（此次变更是否有价值？）。

现在来创建监控脚本：

```bash
mkdir -p ~/.hermes/scripts
```

```python title="~/.hermes/scripts/watch-site.py"
import hashlib, json, os, urllib.request

URL = "https://example.com/pricing"
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.watch-site-state.json")

# Fetch current content
req = urllib.request.Request(URL, headers={"User-Agent": "Hermes-Monitor/1.0"})
content = urllib.request.urlopen(req, timeout=30).read().decode()
current_hash = hashlib.sha256(content.encode()).hexdigest()

# Load previous state
prev_hash = None
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        prev_hash = json.load(f).get("hash")

# Save current state
with open(STATE_FILE, "w") as f:
    json.dump({"hash": current_hash, "url": URL}, f)

# Output for the agent
if prev_hash and prev_hash != current_hash:
    print(f"CHANGE DETECTED on {URL}")
    print(f"Previous hash: {prev_hash}")
    print(f"Current hash: {current_hash}")
    print(f"\nCurrent content (first 2000 chars):\n{content[:2000]}")
else:
    print("NO_CHANGE")
```

配置定时任务：

```bash
/cron add "every 1h" "If the script output says CHANGE DETECTED, summarize what changed on the page and why it might matter. If it says NO_CHANGE, respond with just [SILENT]." --script ~/.hermes/scripts/watch-site.py --name "Pricing monitor" --deliver telegram
```

:::提示 [静默] 技巧  
对于定时任务监控，可指示代理在未检测到任何变化时仅回复 `[SILENT]`。Cron 机制会将 `[SILENT]` 视为“无变化标记”，因此只有当真正发生异常时才会发送通知——从而避免在正常时段收到大量冗余信息。  
:::

:::提示 避免错误通知出现在共享频道中  
`[SILENT]` 仅适用于任务成功执行的情况——若任务执行失败，系统会向该任务的指定接收地址发送 `⚠️ Cron 'X' failed…` 的通知。对于那些发送到繁忙共享频道的任务，可设置 `--failure-deliver local` 以完全屏蔽此类通知（不过任务运行状态仍可在 `hermes cron list` 和运行历史记录中查看）；或者使用 `--failure-deliver slack:C_OPS` 将错误通知定向发送至运维频道。其语法与 `--deliver` 相同；若省略该参数，则错误通知仍会按照之前的规则跟随 `--deliver` 一起发送。  
:::

---

## 模式 2：每周报告  

该模式会从多个来源汇总信息并生成结构化的报告，每周执行一次，结果将发送至您的个人频道。

```bash
/cron add "0 9 * * 1" "Generate a weekly report covering:

1. Search the web for the top 5 AI news stories from the past week
2. Search GitHub for trending repositories in the 'machine-learning' topic
3. Check Hacker News for the most discussed AI/ML posts

Format as a clean summary with sections for each source. Include links.
Keep it under 500 words — highlight only what matters." --name "Weekly AI digest" --deliver telegram
```

通过 CLI：

```bash
hermes cron create "0 9 * * 1" \
  "Generate a weekly report covering the top AI news, trending ML GitHub repos, and most-discussed HN posts. Format with sections, include links, keep under 500 words." \
  --name "Weekly AI digest" \
  --deliver telegram
```

`0 9 * * 1` 是一种标准的 Cron 表达式，含义为每周一上午 9:00。

---

## 模式 3：GitHub 仓库监控器

用于监控仓库中新增的议题、拉取请求或版本发布。

```bash
/cron add "every 6h" "Check the GitHub repository NousResearch/hermes-agent for:
- New issues opened in the last 6 hours
- New PRs opened or merged in the last 6 hours
- Any new releases

Use the terminal to run gh commands:
  gh issue list --repo NousResearch/hermes-agent --state open --json number,title,author,createdAt --limit 10
  gh pr list --repo NousResearch/hermes-agent --state all --json number,title,author,createdAt,mergedAt --limit 10

Filter to only items from the last 6 hours. If nothing new, respond with [SILENT].
Otherwise, provide a concise summary of the activity." --name "Repo watcher" --deliver discord
```

:::warning 自包含提示词  
请注意，该提示词中明确写出了具体的 `gh` 命令。由于 cron agent 没有之前运行时的对话历史记录，因此必须将所有指令完整地写明。（虽然持久内存会被加载，从而使得保存在 MEMORY.md 中的设置能够延续使用，但切勿依赖它来存储对任务至关重要的细节。）  
:::

---

## 模式 4：数据收集流程  

定期抓取数据并保存到文件中，进而分析数据随时间的变化趋势。该模式将用于数据收集的脚本与用于分析的 agent 相结合。

```python title="~/.hermes/scripts/collect-prices.py"
import json, os, urllib.request
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.hermes/data/prices")
os.makedirs(DATA_DIR, exist_ok=True)

# Fetch current data (example: crypto prices)
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
data = json.loads(urllib.request.urlopen(url, timeout=30).read())

# Append to history file
entry = {"timestamp": datetime.now().isoformat(), "prices": data}
history_file = os.path.join(DATA_DIR, "history.jsonl")
with open(history_file, "a") as f:
    f.write(json.dumps(entry) + "\n")

# Load recent history for analysis
lines = open(history_file).readlines()
recent = [json.loads(l) for l in lines[-24:]]  # Last 24 data points

# Output for the agent
print(f"Current: BTC=${data['bitcoin']['usd']}, ETH=${data['ethereum']['usd']}")
print(f"Data points collected: {len(lines)} total, showing last {len(recent)}")
print(f"\nRecent history:")
for r in recent[-6:]:
    print(f"  {r['timestamp']}: BTC=${r['prices']['bitcoin']['usd']}, ETH=${r['prices']['ethereum']['usd']}")
```

```bash
/cron add "every 1h" "Analyze the price data from the script output. Report:
1. Current prices
2. Trend direction over the last 6 data points (up/down/flat)
3. Any notable movements (>5% change)

If prices are flat and nothing notable, respond with [SILENT].
If there's a significant move, explain what happened." \
  --script ~/.hermes/scripts/collect-prices.py \
  --name "Price tracker" \
  --deliver telegram
```

脚本负责自动执行数据收集工作，而智能体则负责添加推理层。

---

## 模式 5：多技能工作流

通过将多个技能串联起来，可处理复杂的定时任务。在提示语被执行之前，这些技能会按顺序加载。

```bash
# Use the arxiv skill to find papers, then the obsidian skill to save notes
/cron add "0 8 * * *" "Search arXiv for the 3 most interesting papers on 'language model reasoning' from the past day. For each paper, create an Obsidian note with the title, authors, abstract summary, and key contribution." \
  --skill arxiv \
  --skill obsidian \
  --name "Paper digest"
```

直接通过该工具操作：

```python
cronjob(
    action="create",
    skills=["arxiv", "obsidian"],
    prompt="Search arXiv for papers on 'language model reasoning' from the past day. Save the top 3 as Obsidian notes.",
    schedule="0 8 * * *",
    name="Paper digest",
    deliver="local"
)
```

技能是按顺序加载的——首先加载 `arxiv`（用于教授智能体如何检索论文），接着是 `obsidian`（用于教授其如何撰写笔记）。提示词则负责将它们串联起来。

---

## 管理任务

```bash
# List all active jobs
/cron list

# Trigger a job immediately (for testing)
/cron run <job_id>

# Pause a job without deleting it
/cron pause <job_id>

# Edit a running job's schedule or prompt
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "Updated task description"

# Add or remove skills from an existing job
/cron edit <job_id> --skill arxiv --skill obsidian
/cron edit <job_id> --clear-skills

# Remove a job permanently
/cron remove <job_id>
```

## 输出目标

`--deliver` 参数用于控制结果输出的位置：

| 目标 | 示例 | 使用场景 |
|------|------|----------|
| `origin` | `--deliver origin` | 创建该任务的同一聊天窗口（默认值） |
| `local` | `--deliver local` | 仅保存到本地文件 |
| `telegram` | `--deliver telegram` | 您的 Telegram 主频道 |
| `discord` | `--deliver discord` | 您的 Discord 主频道 |
| `slack` | `--deliver slack` | 您的 Slack 主频道 |
| 特定聊天窗口 | `--deliver telegram:-1001234567890` | 指定的 Telegram 群组 |
| 主题帖子 | `--deliver telegram:-1001234567890:17585` | 指定的 Telegram 主题帖子 |
| 机器人聊天窗口 | `--deliver bot-chat` | 将输出插入当前账户的官方机器人聊天窗口——机器人会读取并作出回应 |
| 命名型机器人聊天窗口 | `--deliver bot-chat:research` | 其他本地账户的机器人聊天窗口 |

### 通过机器人聊天窗口输出

选择 `bot-chat` 目标时，任务输出会以**真实消息的形式**发送到账户的官方“机器人聊天窗口”中——机器人会像处理其他消息一样接收它，对需要处理的指令作出响应，并在该聊天窗口中回复。当您希望机器人能够*查看并响应* scheduled output，而不仅仅是将其存档在运行历史记录中时，应选择此目标。

注意事项：

- **本地执行模式。** 配置文件必须存在于运行调度器的机器上（可通过 `hermes profile list` 查看）。名称在创建时即会被验证；无法指定其他网关或机器上的配置文件。
- **消耗一个机器人轮次。** 每次消息发送都会在目标机器人的对话窗口中触发一次完整的代理处理流程——对于高频任务，需相应规划预算。
- **可组合使用。** `--deliver bot-chat,telegram` 选项可将消息同时发送到机器人及您的 Telegram 主频道。`all` 参数永远不会被扩展为仅针对机器人对话窗口。

- 发送的消息会添加前缀，以便机器人识别其为调度任务生成，而非用户手动发送。

---

## 实用建议

**确保提示语内容完整。** 定时任务中的代理无法记住之前的对话历史。请将网址、代码库名称、格式要求及发送说明直接包含在提示语中。

**谨慎使用 `[SILENT]`。** 对于仅需监控的任务，可加入“若无变化，请仅回复 `[SILENT]`”之类的指示。在无需反馈的情况下，无需让代理解释该标记——Cron 会直接将 `[SILENT]` 视为抑制消息发送的指令。

**通过脚本进行数据收集。** `script` 参数允许 Python 脚本处理繁琐的操作（如 HTTP 请求、文件读写、状态跟踪）。代理仅能看到脚本的标准输出，并对其进行分析处理。相比让代理自行执行这些操作，这种方式更高效且更可靠。

**使用 `/cron run` 进行测试。** 在等待定时任务触发之前，可先使用 `/cron run <job_id>` 立即执行任务，并检查输出结果是否正确。

**调度表达式。** 支持的格式包括：相对延迟（如 `30m`）、间隔时间（如 `every 2h`）、标准 Cron 表达式（如 `0 9 * * *`）以及 ISO 时间戳（如 `2025-06-15T09:00:00`）。系统不支持类似“每天上午 9 点”这样的自然语言描述，应使用 `0 9 * * *` 代替。

---

*如需完整的 Cron 参考信息——包括所有参数、边界情况及内部实现机制——请参阅 [定时任务（Cron）](/user-guide/features/cron)。*
