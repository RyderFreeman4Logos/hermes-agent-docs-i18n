---
sidebar_position: 11
title: "Cron Internals"
description: "How Hermes stores, schedules, edits, pauses, skill-loads, and delivers cron jobs"
---

# Cron 内部机制

Cron 子系统用于执行定时任务——从简单的一次性延迟任务，到支持技能注入与跨平台交付的周期性 Cron 表达式任务。

## 关键文件

| 文件 | 功能 |
|------|------|
| `cron/jobs.py` | 任务模型、存储机制，以及对 `jobs.json` 的原子读写操作 |
| `cron/scheduler.py` | 调度器循环——负责检测到期任务、执行任务并跟踪重复执行情况 |
| `tools/cronjob_tools.py` | 面向模型的 `cronjob` 工具注册与处理逻辑 |
| `gateway/run.py` | 网关集成——在长时运行循环中实现 Cron 定时触发 |
| `hermes_cli/cron.py` | CLI 中的 `hermes cron` 子命令 |

## 调度模型

系统支持四种调度格式：

| 格式 | 示例 | 行为特点 |
|------|------|----------|
| **相对延迟** | `30m`, `2h`, `1d` | 一次性任务，在指定时长后触发 |
| **间隔时间** | `every 2h`, `every 30m` | 周期性任务，按固定间隔触发 |
| **Cron 表达式** | `0 9 * * *` | 标准的五字段 Cron 语法（分钟、小时、日期、月份、星期几） |
| **ISO 时间戳** | `2025-01-15T09:00:00` | 一次性任务，在精确到秒的时间点触发 |

面向模型的接口为一个名为 `cronjob` 的工具，提供类似动作的操作：`create`、`list`、`update`、`pause`、`resume`、`run`、`remove`。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 文件中，采用原子写操作机制（先写入临时文件，再重命名）。每条任务记录包含：

```json
{
  "id": "a1b2c3d4e5f6",
  "name": "Daily briefing",
  "prompt": "Summarize today's AI news and funding rounds",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",
    "display": "0 9 * * *"
  },
  "skills": ["ai-funding-daily-report"],
  "deliver": "telegram:-1001234567890",
  "repeat": {
    "times": null,
    "completed": 42
  },
  "state": "scheduled",
  "enabled": true,
  "next_run_at": "2025-01-16T09:00:00Z",
  "last_run_at": "2025-01-15T09:00:00Z",
  "last_status": "ok",
  "created_at": "2025-01-01T00:00:00Z",
  "model": null,
  "provider": null,
  "script": null
}
```

### 任务生命周期状态

| 状态 | 含义 |
|-------|------|
| `scheduled` | 正在运行，将在下一个预定时间触发 |
| `paused` | 已暂停——在恢复之前不会触发 |
| `completed` | 重复执行次数已达上限，或为一次性任务且已触发 |
| `running` | 当前正在执行（临时状态） |

### 向下兼容性

旧版本的任务可能仅包含一个 `skill` 字段，而非 `skills` 数组。调度器会在加载时对其进行标准化处理——单个 `skill` 会被转换为 `skills: [skill]` 的格式。

## 调度器运行时

### 计时周期

调度器以固定的间隔周期性运行（默认为每60秒）：

```text
tick()
  1. Acquire scheduler lock (prevents overlapping ticks)
  2. Load all jobs from jobs.json
  3. Filter to due jobs (next_run <= now AND state == "scheduled")
  4. For each due job:
     a. Set state to "running"
     b. Create fresh AIAgent session (no conversation history)
     c. Load attached skills in order (injected as user messages)
     d. Run the job prompt through the agent
     e. Deliver the response to the configured target
     f. Update run_count, compute next_run
     g. If repeat count exhausted → state = "completed"
     h. Otherwise → state = "scheduled"
  5. Write updated jobs back to jobs.json
  6. Release scheduler lock
```

### 网关集成模式

在网关模式下，调度器会在一个专用的后台线程中运行（位于 `gateway/run.py` 文件中的 `_start_cron_ticker` 函数），该线程会在处理消息的同时，每隔 60 秒调用一次 `scheduler.tick()` 函数。

而在 CLI 模式下，定时任务仅会在执行 `hermes cron` 命令或处于活跃的 CLI 会话期间才会被触发。

### 全新会话隔离机制

每个定时任务都在一个完全独立的智能体会话中运行：

- 不保留之前任务的历史对话记录
- 不记忆之前的定时任务执行情况（除非已保存到内存或文件中）
- 提示语必须具备完整性——定时任务不得提出需要进一步澄清的问题
- `cronjob` 工具集处于禁用状态（具有递归防护机制）

## 基于技能的任务处理

定时任务可通过 `skills` 字段绑定一个或多个技能。在任务执行时，系统会按指定顺序加载这些技能，然后将每个技能对应的 SKILL.md 文件内容作为上下文注入，同时将任务的提示语作为任务指令附加进去，最终由智能体处理整合后的技能上下文与指令。这样一来，无需在定时任务的提示语中重复输入完整的操作指令，即可实现可复用且经过测试的工作流程。例如：

```
Create a daily funding report → attach "ai-funding-daily-report" skill
```

### 脚本驱动的任务

任务还可以通过 `script` 字段附加 Python 脚本。该脚本会在每个智能体轮次执行之前运行，其标准输出会被作为上下文注入到提示词中。借此可以实现数据收集与变化检测功能：

```python
# ~/.hermes/scripts/check_competitors.py
import requests, json
# Fetch competitor release notes, diff against last run
# Print summary to stdout — agent analyzes and reports
```

脚本的超时时间默认为120秒。`_get_script_timeout()`函数通过三层机制来确定这一限制值：

1. **模块级覆盖** — `_SCRIPT_TIMEOUT`（用于测试或monkeypatch操作）。仅当该值与默认值不同时才会被使用。
2. **环境变量** — `HERMES_CRON_SCRIPT_TIMEOUT`
3. **配置文件** — `config.yaml`中的`cron.script_timeout_seconds`项（通过`load_config()`函数读取）
4. **默认值** — 120秒

### 备用提供者机制

`run_job()`函数会将用户配置的备用提供者及凭证池传递给`AIAgent`实例：

- **备用提供者** — 从`config.yaml`中读取`fallback_providers`（列表形式）或`fallback_model`（旧版字典形式），其格式与网关的`_load_fallback_model()`函数要求一致。这些参数会以`fallback_model=`的形式传递给`AIAgent.__init__`方法，该方法会将两种格式统一处理为备用提供者链。
- **凭证池** — 根据确定的运行时提供者名称，通过`agent.credential_pool`中的`load_pool(provider)`函数来加载凭证池。仅当凭证池中存在有效凭证（即`pool.has_credentials()`返回True）时才会传递该凭证池。此机制可在遇到429限流错误时实现同一提供者下的密钥轮换。

这一设计与网关的机制保持一致——若没有该机制，定时任务在遭遇限流时会直接失败而无法尝试恢复。

## 结果交付方式

定时任务的结果可以交付到任何支持的目标平台：

| 目标地址 | 语法格式 | 示例 |
|--------|----------|---------|
| 原始聊天窗口 | `origin` | 将结果发送至创建任务的聊天窗口 |
| 本地文件 | `local` | 保存至`~/.hermes/cron/output/`目录 |
| Telegram | `telegram`或`telegram:<chat_id>` | `telegram:-1001234567890` |
| Discord | `discord`或`discord:#channel` | `discord:#engineering` |
| Slack | `slack` | 发送到Slack的默认频道 |
| WhatsApp | `whatsapp` | 发送到WhatsApp的默认聊天窗口 |
| Signal | `signal` | 发送到Signal应用 |
| Matrix | `matrix` | 发送到Matrix的默认房间 |
| Mattermost | `mattermost` | 发送到Mattermost的默认频道 |
| 邮件 | `email` | 通过邮件发送结果 |
| 短信 | `sms` | 通过短信发送结果 |
| Home Assistant | `homeassistant` | 发送到Home Assistant的对话窗口 |
| DingTalk | `dingtalk` | 发送到DingTalk |
| Feishu | `feishu` | 发送到Feishu |
| WeCom | `wecom` | 发送到WeCom |
| 微信 | `weixin` | 发送到微信 |
| BlueBubbles | `bluebubbles` | 通过BlueBubbles发送至iMessage |
| QQ机器人 | `qqbot` | 通过腾讯官方API v2发送至QQ |

对于Telegram主题频道，需使用`telegram:<chat_id>:<thread_id>`的格式（例如：`telegram:-1001234567890:17585`）。

### 响应封装机制

默认情况下（即`cron.wrap_response: true`），定时任务的结果会被封装为包含以下内容的格式：
- 一个头部信息，用于标识定时任务的名称及具体任务内容
- 一个底部信息，说明代理程序无法在聊天窗口中查看已交付的消息

如果在定时任务响应前添加 `[SILENT]` 前缀，则可完全抑制结果交付——这非常适合那些仅需向文件写入数据或执行其他副作用的操作。

### 会话隔离机制

定时任务的结果不会被记录到网关的会话聊天历史中，它们仅存在于该定时任务自身的会话中。这一设计可避免目标聊天窗口中的消息顺序出现混乱。

## 递归防护机制

运行在定时任务模式下的会话会禁用`cronjob`工具集。这样可以防止：
- 定时任务自行创建新的定时任务
- 导致令牌使用量激增的递归调度行为
- 在任务执行过程中意外修改任务的调度时间

## 锁定机制

调度器会使用跨进程的基于文件的锁定机制（Unix系统使用`fcntl.flock`，Windows系统使用`msvcrt.locking`）来确保同一批待处理任务不会被重复执行——即便是在网关的进程内计时器与独立的`hermes cron`命令或手动调用的`tick()`函数之间也是如此。如果无法获取锁定，`tick()`函数会立即返回0值。

## CLI接口

`hermes cron` CLI工具提供了直接的任务管理功能：

```bash
hermes cron list                    # Show all jobs
hermes cron create                  # Interactive job creation (alias: add)
hermes cron edit <job_id>           # Edit job configuration
hermes cron pause <job_id>          # Pause a running job
hermes cron resume <job_id>         # Resume a paused job
hermes cron run <job_id>            # Trigger immediate execution
hermes cron remove <job_id>         # Delete a job
```

## 相关文档

- [定时任务功能指南](/user-guide/features/cron)
- [网关内部机制](./gateway-internals.md)
- [智能体循环处理机制](./agent-loop.md)
