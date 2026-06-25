---
sidebar_position: 5
title: "Scheduled Tasks (Cron)"
description: "Schedule automated tasks with natural language, manage them with one cron tool, and attach one or more skills"
---

# 定时任务（Cron）

您可以使用自然语言或 Cron 表达式来安排任务自动执行。Hermes 通过一个统一的 `cronjob` 工具来实现 Cron 任务管理，该工具提供类似操作指令的接口，无需单独的调度、列表或删除工具。

## Cron 的当前功能

Cron 任务可以：

- 安排一次性任务或周期性任务
- 暂停、恢复、编辑、触发及删除任务
- 为单个任务绑定零个、一个或多个技能
- 将执行结果返回至原始聊天界面、本地文件或已配置的平台目标地址
- 在具有常规静态工具列表的全新智能体会话中运行
- 以**无智能体模式**运行——即按计划执行脚本，其标准输出会被原样传递，完全不涉及大语言模型（详见下文的[无智能体模式：仅脚本任务](#no-agent-mode-script-only-jobs)部分）

所有这些功能均可通过 `cronjob` 工具在 Hermes 中实现，因此您无需使用命令行界面，只需用简单的语言指令即可创建、暂停、编辑或删除任务。

:::提示
在创建任务时，若未明确指定 `provider`/`model` 参数，该任务将遵循由 `hermes model` 设置的全球默认值——Hermes 会为该任务“快照”保存对应的提供者和模型版本。如果后续全球默认值发生变更，该任务将会**直接失败**：它不会执行任何操作，也不会发起推理请求，同时会发出警告，提示您需要明确指定提供者和模型参数（使用命令 `cronjob action=update job_id=… provider=… model=…`）才能继续运行。这样可避免无人监控的任务在后台悄悄切换到付费的提供者或模型，从而产生不必要的费用（问题编号 #44585）。如果您希望任务始终使用全球默认值，可在更改默认值后将其固定为新值。对于无人监控的运行场景，`hermes setup --portal` 是最简便的选择，因为其会自动处理 OAuth 刷新流程。更多信息请参阅 [Nous Portal](/integrations/nous-portal)。
:::

:::警告
在 Cron 执行的会话中无法递归创建更多 Cron 任务。为防止出现无限循环的调度现象，Hermes 会禁用 Cron 执行过程中的相关管理工具。
:::

## 创建定时任务

### 在聊天界面中使用 `/cron` 命令

```bash
/cron add 30m "Remind me to check the build"
/cron add "every 2h" "Check server status"
/cron add "every 1h" "Summarize new feed items" --skill blogwatcher
/cron add "every 1h" "Use both skills and combine the result" --skill blogwatcher --skill maps
```

### 通过独立 CLI 使用

```bash
hermes cron create "every 2h" "Check server status"
hermes cron create "every 1h" "Summarize new feed items" --skill blogwatcher
hermes cron create "every 1h" "Use both skills and combine the result" \
  --skill blogwatcher \
  --skill maps \
  --name "Skill combo"
```

### 通过自然对话实现

像平常一样与Hermes交流即可：

```text
Every morning at 9am, check Hacker News for AI news and send me a summary on Telegram.
```

Hermes 在内部会使用统一的 `cronjob` 工具。

## 基于技能的定时任务

定时任务在处理提示词之前，可以加载一个或多个技能。

### 单个技能

```python
cronjob(
    action="create",
    skill="blogwatcher",
    prompt="Check the configured feeds and summarize anything new.",
    schedule="0 9 * * *",
    name="Morning feeds",
)
```

### 多个技能

技能会按顺序加载。提示词则作为叠加在这些技能之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="Look for new local events and interesting nearby places, then combine them into one short brief.",
    schedule="every 6h",
    name="Local brief",
)
```

当您希望定时运行的智能体能够继承可复用的工作流，同时避免将完整的技能配置文本嵌入到 Cron 脚本本身时，此功能便十分实用。

## 在项目目录内运行任务

默认情况下，Cron 任务会在与任何代码仓库分离的环境中运行——不会加载 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` 文件，且终端、文件处理及代码执行工具均会从网关启动时的工作目录开始运行。如需更改此设置，可通过 CLI 使用 `--workdir` 参数，或通过工具调用使用 `workdir=` 参数来实现。

```bash
# Standalone CLI (schedule and prompt are positional)
hermes cron create "every 1d at 09:00" \
  "Audit open PRs, summarize CI health, and post to #eng" \
  --workdir /home/me/projects/acme
```

```python
# From a chat, via the cronjob tool
cronjob(
    action="create",
    schedule="every 1d at 09:00",
    workdir="/home/me/projects/acme",
    prompt="Audit open PRs, summarize CI health, and post to #eng",
)
```

当设置了 `workdir` 时：

- 该目录下的 `AGENTS.md`、`CLAUDE.md` 以及 `.cursorrules` 文件会被注入到系统提示语中（其加载顺序与交互式 CLI 中的顺序一致）
- `terminal`、`read_file`、`write_file`、`patch`、`search_files` 和 `execute_code` 这些功能都会以该目录作为工作目录
- 该路径必须是存在且为绝对路径——相对路径或不存在的目录在创建/更新时会被拒绝
- 若需清除 `workdir` 并恢复旧有行为，可在编辑时传递 `--workdir ""`（或通过工具使用 `workdir=""`）

:::note 序列化处理
设置了 `workdir` 的任务会在调度器的时钟周期内依次执行，而非在并行池中运行。这是有意为之：Cron 工作进程会通过全局进程终端状态来应用任务的工作目录，因此同时运行的两个具有不同工作目录的任务会互相干扰当前工作目录。未设置工作目录的任务则仍会像以往一样以并行方式运行。
:::

## 编辑任务

无需删除并重新创建任务即可对其进行修改。

:::tip 任务引用
下方的 `<job_id>` 占位符（以及 [生命周期操作](#lifecycle-actions) 中的用法）也接受任务名称（不区分大小写）——当你记得任务名为 `morning-digest` 但记不起其十六进制 ID 时，这种方式非常方便。精确的 ID 会优先于名称匹配；如果引用内容并非 ID，且名称与多个任务匹配，则命令会拒绝执行，并列出可能的 ID 以便你区分。
:::

### 聊天

```bash
/cron edit <job_id> --schedule "every 4h"
/cron edit <job_id> --prompt "Use the revised task"
/cron edit <job_id> --skill blogwatcher --skill maps
/cron edit <job_id> --remove-skill blogwatcher
/cron edit <job_id> --clear-skills
```

### 独立 CLI

```bash
hermes cron edit <job_id> --schedule "every 4h"
hermes cron edit <job_id> --prompt "Use the revised task"
hermes cron edit <job_id> --skill blogwatcher --skill maps
hermes cron edit <job_id> --add-skill maps
hermes cron edit <job_id> --remove-skill blogwatcher
hermes cron edit <job_id> --clear-skills
```

备注：

- 多次使用 `--skill` 会替换任务所关联的技能列表
- `--add-skill` 会在现有列表末尾添加新技能，而不会替换原有内容
- `--remove-skill` 用于移除特定的已关联技能
- `--clear-skills` 用于移除所有已关联的技能

## 生命周期操作

现在，Cron 任务的生命周期比单纯的创建/删除更为丰富。

### 聊天功能

```bash
/cron list
/cron pause <job_id>
/cron resume <job_id>
/cron run <job_id>
/cron remove <job_id>
```

### 独立 CLI

```bash
hermes cron list
hermes cron pause <job_id_or_name>
hermes cron resume <job_id_or_name>
hermes cron run <job_id_or_name>
hermes cron remove <job_id_or_name>
hermes cron edit <job_id_or_name> [...flags]
hermes cron status
hermes cron tick
```

其功能如下：

- `pause` — 保留该任务，但停止对其调度
- `resume` — 重新启用该任务，并计算下一次执行时间
- `run` — 在下一个调度周期触发该任务执行
- `remove` — 完全删除该任务
- `edit` — 修改任务的调度时间、提示信息、交付设置等

**基于名称的查找。** 现在，上述四个用于修改状态的命令（`pause`、`resume`、`run`、`remove`、`edit`）以及代理工具的 `cronjob` 均可接受任务**名称**（不区分大小写）来替代十六进制 ID 进行操作。如果存在精确的 ID，代理和 CLI 都会优先使用该 ID；而对于名称匹配不唯一的情况（即有多个任务共享同一名称），系统会拒绝操作，并列出所有可能的 ID 供用户明确选择。由于任务名称并非唯一，这一机制至关重要——它能防止在存在同名任务时意外修改到错误的任务。

## 工作原理

**Cron 执行由网关守护进程负责。** 网关每 60 秒触发一次调度，然后在独立的代理会话中执行所有到期任务。

```bash
hermes gateway install     # Install as a user service
sudo hermes gateway install --system   # Linux: boot-time system service for servers
hermes gateway             # Or run in foreground

hermes cron list
hermes cron status
```

### 网关调度器行为

在每个时间间隔内，Hermes会执行以下操作：

1. 从 `~/.hermes/cron/jobs.json` 中加载任务列表；
2. 将每个任务的 `next_run_at` 时间与当前时间进行比对；
3. 为每个即将运行的任务启动一个新的 `AIAgent` 会话；
4. 可选地将一个或多个附加的技能注入到该新会话中；
5. 运行提示语并等待处理完成；
6. 返回最终响应结果；
7. 更新任务运行元数据及下一次调度时间。

`~/.hermes/cron/.tick.lock` 文件用于锁定资源，防止多个调度周期同时重复执行同一批任务。

## 输出目标选择

在安排任务时，您可以指定输出的去向：

| 选项 | 描述 | 示例 |
|------|------|------|
| `"origin"` | 返回任务创建的源头 | 消息平台上的默认选项 |
| `"local"` | 仅保存到本地文件（`~/.hermes/cron/output/`） | CLI工具的默认选项 |
| `"telegram"` | 发送到Telegram主频道 | 使用 `TELEGRAM_HOME_CHANNEL` 变量 |
| `"telegram:123456"` | 按ID发送到特定Telegram聊天窗口 | 直接发送 |
| `"telegram:-100123:17585"` | 按格式 `chat_id:thread_id` 发送到特定Telegram主题 | |
| `"discord"` | 发送到Discord主频道 | 使用 `DISCORD_HOME_CHANNEL` 变量 |
| `"discord:#engineering"` | 按频道名称发送到特定Discord频道 | |
| `"slack"` | 发送到Slack主频道 | |
| `"whatsapp"` | 发送到WhatsApp主账号 | |
| `"signal"` | 发送到Signal应用 | |
| `"matrix"` | 发送到Matrix主房间 | |
| `"mattermost"` | 发送到Mattermost主频道 | |
| `"email"` | 通过邮件发送 | |
| `"sms"` | 通过Twilio发送短信 | |
| `"homeassistant"` | 发送到Home Assistant设备 | |
| `"dingtalk"` | 发送到钉钉 | |
| `"feishu"` | 发送到飞书/Lark | |
| `"wecom"` | 发送到企业微信 | |
| `"weixin"` | 发送到微信 | |
| `"bluebubbles"` | 发送到BlueBubbles（iMessage） | |
| `"qqbot"` | 发送到QQ机器人 | |
| `"all"` | 同时发送到所有已连接的频道 | 在任务执行时动态确定目标 |
| `"telegram,discord"` | 同时发送到指定的多个频道 | 用逗号分隔的列表 |
| `"origin,all"` | 先发送到任务创建地，再发送到其他所有已连接频道 | 可组合任意选项 |

代理的最终响应会自动发送出去，您无需在定时任务提示语中手动调用 `send_message` 函数。

### 路由意图（`all`）

使用 `all` 选项后，您只需安排一次定时任务，即可将其发送到所有已配置的消息频道，而无需逐一指定频道名称。该选项会在**任务实际执行时**才确定具体目标，因此如果您在设置 `TELEGRAM_HOME_CHANNEL` 之前就创建了任务，那么该任务将在设置完成后的下一个调度周期才开始使用Telegram作为输出渠道。

语义说明：`all` 会扩展为所有已配置有主频道的平台。即使设置为 `0`，任务也不会产生任何输出目标，且会在系统日志中记录为发送失败。

`all` 选项可与明确的指定目标一起使用。例如，`origin,all` 表示先将任务发送到任务创建地，再发送到其他所有已连接的频道，同时通过 `(平台, 聊天ID, 主题ID)` 组合来避免重复发送。

### Telegram定时任务主题（`TELEGRAM_CRON_THREAD_ID`）

当启用Telegram主题模式时，主私信窗口会被保留作为系统大厅——发送到该窗口的回复会收到大厅提示并被拒绝，且 `reply_to_message_id` 信息也会被丢弃，因此您无法回复那些发送到主聊天窗口的定时任务消息。

建议将定时任务指向专门的论坛主题：

1. 在Telegram中打开机器人的私信窗口，创建一个名为“Cron”之类的主题。长按主题标题 → 选择**复制链接**；链接末尾的数字即为该主题的 `message_thread_id`。
2. 在您的 `.env` 文件中设置 `TELEGRAM_CRON_THREAD_ID=<该ID>`。

此设置仅适用于定时任务的输出。其他场景下使用的 `TELEGRAM_HOME_CHANNEL_THREAD_ID`（如重启通知）则保持不变。如果明确指定了 `deliver="telegram:chat_id:thread_id"`，则该指定仍会优先于环境变量设置。现在，对定时任务消息的回复会发送到对应的主题会话中，您可以直接对其进行处理。

### 响应格式封装

默认情况下，发送出的定时任务输出会带有标题和页脚，以便接收方能够识别其为定时任务产生的内容：

```
Cronjob Response: Morning feeds
-------------

<agent output here>

Note: The agent cannot see this message, and therefore cannot respond to it.
```

若希望直接输出未经封装的代理原始结果，可将 `cron.wrap_response` 的值设置为 `false`：

```yaml
# ~/.hermes/config.yaml
cron:
  wrap_response: false
```

### 可持续任务（回复定时触发消息）

默认情况下，定时触发的消息属于“发送即忘”类型：消息虽已发送，但不会保留在聊天记录中，因此如果您对其回复，智能体将无法记住它之前说过什么。若将任务设置为**可持续**模式，该定时发送的简报就会变成一段可回复的对话——智能体能够掌握上下文信息，而无需反复询问“第2项任务是什么？”。

此功能为可选选项，默认处于关闭状态。您可以在全局配置中启用该功能，也可通过 `cronjob` 工具的 `attach_to_session` 选项为单个任务单独启用（该选项会覆盖该任务的全局设置）：

```yaml
# ~/.hermes/config.yaml
cron:
  mirror_delivery: false   # set true to make cron deliveries continuable
```

该功能优先在**消息线程**中运行，且内容仅限于任务发起的原始聊天窗口：

- **支持线程的平台**（Telegram主题、Discord/Slack线程）：每次消息发送都会开启一个独立的线程，任务指令会被嵌入该线程的会话中，因此在此线程内的回复能够保留完整上下文。对于周期性任务（例如每日任务），每次执行都会创建一个新的线程，从而确保每次消息的后续讨论相互独立。
- **仅支持私信的平台**（WhatsApp、Signal、短信）：由于不存在线程，任务指令会被复制到原始私信会话中——私信本身即为对话延续的载体。

系统始终只操作原始聊天窗口：不会对其他分发目标（如“全部”或指定其他聊天的消息）进行线程化处理。复制的消息会以带标签的用户轮次形式呈现（例如`[Cron delivery: <task name>]`），从而确保在所有模型提供商之间都能保持对话历史的有序切换。

### 沉默抑制功能

如果智能体的最终回复包含`[SILENT]`标记，该消息将被完全屏蔽。系统仍会为审计目的将相关输出保存在本地（路径为`~/.hermes/cron/output/`），但不会向目标地址发送任何消息。

此功能适用于监控那些仅在出现异常时才需要反馈的任务。

```text
Check if nginx is running. If everything is healthy, respond with only [SILENT].
Otherwise, report the issue.
```

无论是否存在 `[SILENT]` 标记，失败的任务始终会生成报告——只有运行成功的任务才能被设置为静默模式。对于需要安静监控的任务，当没有需要报告的内容时，可指示代理仅回复 `[SILENT]`。

## 脚本超时时间

通过 `script` 参数传入的预运行脚本默认超时时间为120秒。如果您的脚本需要更长的执行时间——例如，为了加入随机延迟以避免出现类似机器人的固定时间模式——您可以相应地延长该时间限制：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 300   # 5 minutes
```

或者设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。参数的优先级顺序为：环境变量 → config.yaml 文件中的设置 → 默认的 120 秒。

## 无智能体模式（仅脚本任务）

对于那些不需要大语言模型进行推理的周期性任务——例如传统的看门狗监控、磁盘/内存警报、心跳检测以及 CI 环境的 ping 检测——在创建任务时请设置 `no_agent=True`。调度器会按预定时间运行您的脚本，并直接输出其标准输出结果，从而完全跳过智能体环节：

```bash
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"
```

语义规则：

- 脚本的标准输出（已去除首尾空白）→ 将其原样作为消息发送。
- **标准输出为空 → 无声标记，不发送任何内容**。这采用的是看门狗机制：“仅在出现异常时才发出通知”。
- 程序非零退出或超时 → 会发送错误警报，因此故障的看门狗机制不会导致静默失败。
- 最后一行包含 `{"wakeAgent": false}` → 同样为无声标记（与大语言模型任务所使用的规则一致）。
- 无需令牌、模型或提供者作为备用方案——该任务根本不会涉及推理层。

`.sh` / `.bash` 文件在 `/bin/bash` 环境下运行；其他类型的脚本则在当前 Python 解释器（`sys.executable`）环境下执行。脚本必须存放在 `~/.hermes/scripts/` 目录中（遵循与预运行脚本机制相同的沙箱规则）。

### 代理会为您完成这些配置

`cronjob` 工具的架构允许直接向 Hermes 暴露 `no_agent` 参数，因此您只需在聊天中描述看门狗机制，代理便会自动为其进行配置：

```text
Ping me on Telegram if RAM is over 85%, every 5 minutes.
```

Hermes 会通过 `write_file` 函数将检查脚本写入 `~/.hermes/scripts/` 目录，随后调用相应函数：

```python
cronjob(action="create", schedule="every 5m",
        script="memory-watchdog.sh", no_agent=True,
        deliver="telegram", name="memory-watchdog")
```

当消息内容完全由脚本决定时（如监控警报、阈值报警、心跳检测等），该工具会自动设置 `no_agent=True`。此外，这一工具还允许用户暂停、恢复、编辑及删除任务——因此整个任务生命周期都由聊天界面驱动，无需任何人操作命令行界面。

如需实际示例，请参阅[仅脚本版定时任务指南](/guides/cron-script-only)。

## 使用 `context_from` 连接多个任务

定时任务在独立的会话中运行，不会保留之前运行的记录。但有时，一个任务的输出恰好是下一个任务所需的数据。`context_from` 参数可自动建立这种关联——在运行时，任务B的提示语前会自动添加任务A的最新输出作为上下文。

```python
# Job 1: Collect raw data
cronjob(
    action="create",
    prompt="Fetch the top 10 AI/ML stories from Hacker News. Save them to ~/.hermes/data/briefs/raw.md in markdown format with title, URL, and score.",
    schedule="0 7 * * *",
    name="AI News Collector",
)

# Job 2: Triage — receives Job 1's output as context
# Get Job 1's ID from: cronjob(action="list")
cronjob(
    action="create",
    prompt="Read ~/.hermes/data/briefs/raw.md. Score each story 1–10 for engagement potential and novelty. Output the top 5 to ~/.hermes/data/briefs/ranked.md.",
    schedule="30 7 * * *",
    context_from="<job1_id>",
    name="AI News Triage",
)

# Job 3: Ship — receives Job 2's output as context
cronjob(
    action="create",
    prompt="Read ~/.hermes/data/briefs/ranked.md. Write 3 tweet drafts (hook + body + hashtags). Deliver to telegram:7976161601.",
    schedule="0 8 * * *",
    context_from="<job2_id>",
    name="AI News Brief",
)
```

**工作原理：**

- 当任务 2 被触发时，Hermes 会从 `~/.hermes/cron/output/{job1_id}/*.md` 中读取任务 1 的最新输出内容。
- 该输出内容会自动添加到任务 2 的提示语开头。
- 任务 2 无需硬编码“读取此文件”的指令——它可直接将相关内容作为上下文获取。
- 任务链的长度可任意延伸：任务 1 → 任务 2 → 任务 3 → ...

**`context_from` 的支持格式：**

| 格式 | 示例 |
|------|------|
| 单个任务 ID（字符串） | `context_from="a1b2c3d4"` |
| 多个任务 ID（列表） | `context_from=["job_a", "job_b"]` |

输出内容将按照列出的顺序进行拼接。

**适用场景：**

- 多阶段处理流程（收集 → 过滤 → 格式化 → 交付）
- 各步骤之间存在依赖关系的任务（第 N 步的工作依赖于第 N-1 步的输出）
- 需要某个任务汇总其他多个任务结果的扩展/汇聚型架构

## 提供商故障恢复机制

定时任务会继承您配置的备用提供商以及凭证池轮换机制。如果主 API 密钥出现速率限制，或对应提供商返回错误，定时任务代理可以：

- 如果在 `config.yaml` 中配置了 `fallback_providers`（或旧版的 `fallback_model`），则自动切换到备用提供商。
- 对于同一提供商，自动切换到 [凭证池](/user-guide/configuration#credential-pool-strategies) 中的下一组凭证。

这意味着高频运行或在高峰时段执行的定时任务具备更强的容错能力——单个出现速率限制的密钥不会导致整个任务执行失败。

## 时间调度格式

代理的最终响应会自动发送——您无需在针对同一目标地址的定时任务提示语中再添加 `send_message` 指令。如果定时任务调用了 `send_message` 但目标地址正是调度器已计划发送内容的地址，Hermes 会跳过重复发送操作，而是要求模型将面向用户的内容放入最终响应中。仅当需要发送到其他额外地址或不同地址时，才使用 `send_message`。

### 相对延迟（单次执行）

```text
30m     → Run once in 30 minutes
2h      → Run once in 2 hours
1d      → Run once in 1 day
```

### 间隔时间（周期性任务）

```text
every 30m    → Every 30 minutes
every 2h     → Every 2 hours
every 1d     → Every day
```

### Cron 表达式

```text
0 9 * * *       → Daily at 9:00 AM
0 9 * * 1-5     → Weekdays at 9:00 AM
0 */6 * * *     → Every 6 hours
30 8 1 * *      → First of every month at 8:30 AM
0 0 * * 0       → Every Sunday at midnight
```

### ISO时间戳

```text
2026-03-15T09:00:00    → One-time at March 15, 2026 9:00 AM
```

## 重复执行行为

| 计划类型 | 默认重复频率 | 行为表现 |
|--------------|----------------|----------|
| 单次执行（`30m`，时间戳） | 1 | 仅运行一次 |
| 定期执行（`每2小时`） | 永久 | 直到被移除前持续运行 |
| Cron表达式 | 永久 | 直到被移除前持续运行 |

您也可以自行覆盖该设置：

```python
cronjob(
    action="create",
    prompt="...",
    schedule="every 2h",
    repeat=5,
)
```

## 通过编程方式管理任务

面向智能体的 API 仅是众多工具之一：

```python
cronjob(action="create", ...)
cronjob(action="list")
cronjob(action="update", job_id="...")
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")
cronjob(action="run", job_id="...")
cronjob(action="remove", job_id="...")
```

若要执行`update`操作，可传入`skills=[]`参数以移除所有已绑定的技能。

## Cron作业可使用的工具集

Cron会在一个全新的代理会话中运行每项任务，且该会话不关联任何聊天平台。默认情况下，Cron代理会使用**在`hermes tools`中为`cron`平台配置的工具集**——而非CLI的默认设置，亦非所有可用工具。

```bash
hermes tools
# → pick the "cron" platform in the curses UI
# → toggle toolsets on/off just like you would for Telegram/Discord/etc.
```

通过 `cronjob.create` 请求中的 `enabled_toolsets` 字段（或通过对现有任务执行 `cronjob.update` 操作），即可实现对每项任务的更精细控制。

```text
cronjob(action="create", name="weekly-news-summary",
        schedule="every sunday 9am",
        enabled_toolsets=["web", "file"],      # just web + file, no terminal/browser/etc.
        prompt="Summarize this week's AI news: ...")
```

当任务中设置了 `enabled_toolsets` 时，该设置将起决定性作用；否则，则以 `hermes tools` 的 cron-platform 配置为准；若仍无法确定，Hermes 会回退到内置的默认设置。这一点对于成本控制至关重要：如果在每一个简单的“获取新闻”任务中都启用 `moa`、`browser`、`delegation` 等工具，就会导致每次调用大型语言模型时工具结构提示信息变得臃肿。

### 完全跳过智能体：使用 `wakeAgent`

如果您的定时任务通过 `script=` 参数指定了预检查脚本，该脚本可以在运行时决定是否需要调用 Hermes 智能体。只需在脚本的输出中添加一行符合以下格式的最终内容即可：

```text
{"wakeAgent": false}
```

……此时，Cron 会完全跳过该轮次的代理运行。这一功能非常适合那些需要频繁轮询（每1至5分钟一次）的场景，且仅需在状态真正发生变化时才唤醒大语言模型——否则就会不断产生无实际内容的代理响应，造成不必要的资源消耗。

```python
# pre-check script
import json, sys
latest = fetch_latest_issue_count()
prev = read_state("issue_count")
if latest == prev:
    print(json.dumps({"wakeAgent": False}))   # skip this tick
    sys.exit(0)
write_state("issue_count", latest)
print(json.dumps({"wakeAgent": True, "context": {"new_issues": latest - prev}}))
```

如果未指定 `wakeAgent` 参数，其默认值为 `true`（即按常规方式唤醒智能体）。

#### 方案：低成本的预运行判定机制

`wakeAgent` 判定机制提供了一种无需任何成本的方式，用于决定某个定时任务是否需要消耗任何大语言模型令牌。三种常见模式即可覆盖大多数使用场景。

**文件变更判定模式**——仅当被监控的文件自上次成功执行后有了新内容时才运行该任务。调度器会记录每个任务的 `last_run_at` 时间，并将其与文件的修改时间（mtime）进行比较。

```bash
#!/bin/bash
# ~/.hermes/scripts/feed-changed.sh
FEED="$HOME/data/feed.json"
STATE="$HOME/.hermes/scripts/.feed-changed.last"
test -f "$FEED" || { echo '{"wakeAgent": false}'; exit 0; }
mtime=$(stat -c %Y "$FEED")
last=$(cat "$STATE" 2>/dev/null || echo 0)
if [ "$mtime" -le "$last" ]; then
  echo '{"wakeAgent": false}'
else
  echo "$mtime" > "$STATE"
  echo '{"wakeAgent": true}'
fi
```

```text
cronjob(action="create", name="process-feed",
        schedule="every 30m",
        script="feed-changed.sh",
        prompt="A new ~/data/feed.json has landed. Summarize what changed.")
```

**外部标志触发机制**——仅在其他进程发出就绪信号时才会启动（例如部署钩子上传了文件，或 CI 任务在状态存储中设置了相应值）。

```bash
#!/bin/bash
# ~/.hermes/scripts/flag-ready.sh
if test -f /tmp/new-data-ready; then
  rm -f /tmp/new-data-ready
  echo '{"wakeAgent": true}'
else
  echo '{"wakeAgent": false}'
fi
```

```text
cronjob(action="create", name="nightly-analysis",
        schedule="0 9 * * *",
        script="flag-ready.sh",
        prompt="Run the nightly analysis over today's batch.")
```

**SQL计数门限**——仅当您的数据库中有新行需要处理时才会运行该脚本。此外，该脚本还可以通过`context`将计数信息传递给代理，这样代理无需再次查询即可知晓需要处理的记录数量。

```python
#!/usr/bin/env python
# ~/.hermes/scripts/new-rows.py
import json, sqlite3
conn = sqlite3.connect("/home/me/data/app.db")
n = conn.execute(
    "SELECT COUNT(*) FROM messages WHERE ts > strftime('%s','now','-2 hours')"
).fetchone()[0]
if n < 1:
    print(json.dumps({"wakeAgent": False}))
else:
    print(json.dumps({"wakeAgent": True, "context": {"new_rows": n}}))
```

```text
cronjob(action="create", name="summarize-new-msgs",
        schedule="every 2h",
        script="new-rows.py",
        prompt="Summarize the new messages from the last 2 hours.")
```

无论您要从脚本中查询何种数据源——无论是 Postgres、HTTP API，还是自定义的状态存储——都可以采用相同的模式，而无需在 cron 子系统中内置 SQL 解析器。

:::提示
Hermes 自带的 `~/.hermes/state.db` 是一种内部架构，不同版本之间会发生变化。请勿通过预运行关卡来查询该数据库，而应直接使用您自己的数据库或数据源。
:::

致谢：这套文档的编写灵感源自 @iankar8 在 [#2654](https://github.com/NousResearch/hermes-agent/pull/2654) 中提出的建议，他建议引入 sql/file/command 触发器作为另一种并行机制。由于 `script` + `wakeAgent` 关卡已经能以零成本覆盖这三种场景，因此相关改进最终以文档形式呈现。

### 任务链式调用：`context_from`

Cron 任务可以通过在 `context_from` 中列出一个或多个其他任务的名称（或 ID），来获取这些任务最近一次成功的输出结果：

```text
cronjob(action="create", name="daily-digest",
        schedule="every day 7am",
        context_from=["ai-news-fetch", "github-prs-fetch"],
        prompt="Write the daily digest using the outputs above.")
```

本次运行时，相关任务最近完成的输出结果会被作为上下文插入提示语上方。每个上游条目都必须是有效的任务 ID 或名称（参见 `cronjob action="list"`）。注意：该功能仅读取*最近已完成*的输出结果，而不会等待同一时间戳内仍在运行的上游任务。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 文件中。任务运行产生的输出则保存至 `~/.hermes/cron/output/{job_id}/{timestamp}.md` 路径下。

任务中的 `model` 和 `provider` 字段可设置为 `null`。若省略这些字段，Hermes 会在执行时从全局配置中自动获取对应值；只有当为特定任务设置了自定义值时，这些字段才会出现在任务记录中。

该存储机制采用原子文件写入方式，因此即使写入过程被中断，也不会留下未完成的任务文件。

## 独立提示语依然重要

:::warning 重要提示
定时任务是在全新的代理会话中运行的。因此，提示语中必须包含代理所需的所有信息，尤其是那些无法通过已加载的技能获取的内容。
:::

**错误示例：** `"Check on that server issue"`

**正确示例：** `"以用户 'deploy' 的身份 SSH 登录到服务器 192.168.1.100，使用 'systemctl status nginx' 命令检查 nginx 是否正在运行，并验证 https://example.com 是否返回 HTTP 200 状态码。"`

## 安全性

在创建或更新定时任务时，系统会对其提示语进行扫描，以检测注入攻击和凭证窃取的迹象。那些包含隐形 Unicode 特技、SSH 后门尝试或明显用于窃取机密信息的代码片段都会被拦截。
