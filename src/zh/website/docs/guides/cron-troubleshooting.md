---
sidebar_position: 12
title: "Cron Troubleshooting"
description: "Diagnose and fix common Hermes cron issues — jobs not firing, delivery failures, skill loading errors, and performance problems"
---

# Cron任务故障排查

当Cron作业无法按预期运行时，请按顺序进行以下检查。大多数问题可归为四类：时间设置、任务投递、权限问题或技能加载故障。

---

## 作业未触发

### 检查1：确认该作业存在且处于活跃状态

```bash
hermes cron list
```

请查找该任务，并确认其状态为 `[active]`（而非 `[paused]` 或 `[completed]`）。如果显示为 `[completed]`，则可能已用完重复执行次数——需编辑该任务以重置计数。

### 检查 2：确认调度时间设置正确

格式错误的调度规则会默认被视为单次执行，或直接被拒绝。请测试您的表达式：

| 您的表达式 | 正确的解析结果 |
|------------|----------------|
| `0 9 * * *` | 每天上午 9:00 |
| `0 9 * * 1` | 每周一上午 9:00 |
| `every 2h` | 从现在起每 2 小时执行一次 |
| `30m` | 从现在起 30 分钟后执行 |
| `2025-06-01T09:00:00` | 2025 年 6 月 1 日 UTC 时间上午 9:00 |

如果任务仅执行一次后就从列表中消失，说明这是单次执行调度（如 `30m`、`1d` 或 ISO 时间戳），属于正常现象。

### 检查 3：网关是否正在运行？

Cron 任务由网关的后台计时线程触发，该线程每 60 秒触发一次。普通的 CLI 对话会话**不会**自动触发 Cron 任务。

如果您希望任务能自动执行，必须确保网关正在运行（前台模式可使用 `hermes gateway`，已安装的服务则可使用 `hermes gateway start`）。进行一次性调试时，可使用 `hermes cron tick` 手动触发计时。

### 检查 4：确认系统时钟与时区设置

任务会使用本地时区。如果您的机器时钟有误，或处于与预期不同的时区，任务将会在错误的时间被触发。请务必核实：

```bash
date
hermes cron list   # Compare next_run times with local time
```

## 交付失败

### 检查项 1：确认交付目标正确

交付目标对大小写敏感，且必须配置正确的平台。若目标配置错误，响应将会被静默丢弃。

| 目标 | 所需配置 |
|------|----------|
| `telegram` | `~/.hermes/.env` 文件中的 `TELEGRAM_BOT_TOKEN` |
| `discord` | `~/.hermes/.env` 文件中的 `DISCORD_BOT_TOKEN` |
| `slack` | `~/.hermes/.env` 文件中的 `SLACK_BOT_TOKEN` |
| `whatsapp` | 已配置 WhatsApp 网关 |
| `signal` | 已配置 Signal 网关 |
| `matrix` | 已配置 Matrix 主服务器 |
| `email` | `config.yaml` 中已配置 SMTP |
| `sms` | 已配置 SMS 提供商 |
| `local` | 具有对 `~/.hermes/cron/output/` 的写入权限 |
| `origin` | 将内容发送至创建该任务的聊天窗口 |

其他支持的平台还包括 `mattermost`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot` 以及 `webhook`。您也可以使用 `platform:chat_id` 语法指定特定聊天窗口（例如：`telegram:-1001234567890`）。

若交付失败，任务仍会正常运行——只是不会发送到任何地方。您可以查看 `hermes cron list` 中的 `last_error` 字段（如有显示）以获取最新状态。

### 检查项 2：检查 `[SILENT]` 的使用情况

如果您的定时任务没有输出，或者智能体返回 `[SILENT]`，则内容会被抑制不发送。这对于监控任务来说是刻意设计的——但请确保您的提示语不会意外地抑制所有输出。

若提示语要求“若无变化则回复 [SILENT]”，那么非空响应也会被静默忽略。请检查您的条件逻辑。

### 检查项 3：平台令牌权限

每个消息平台上的机器人都需要特定的权限才能接收消息。如果交付失败且无任何提示：

- **Telegram**：机器人必须是目标群组/频道的管理员
- **Discord**：机器人必须拥有在目标频道发送消息的权限
- **Slack**：机器人必须已被添加到工作空间，并拥有 `chat:write` 权限

### 检查项 4：响应封装

默认情况下，定时任务的响应会被添加头部和尾部信息（即 `config.yaml` 中的 `cron.wrap_response: true` 设置）。某些平台或集成可能无法正确处理这种格式。如需禁用该功能：

```yaml
cron:
  wrap_response: false
```

## 技能加载失败问题

### 检查项 1：确认技能已安装

```bash
hermes skills list
```

在将技能添加到定时任务之前，必须先安装这些技能。如果缺少某个技能，请使用 `hermes skills install <skill-name>` 命令或通过 CLI 中的 `/skills` 功能进行安装。

### 检查项 2：确认技能名称与技能文件夹名称是否一致

技能名称是区分大小写的，且必须与已安装技能的文件夹名称完全相同。如果您的任务指定了 `ai-funding-daily-report`，但对应的技能文件夹名为 `ai-funding-daily-report`，请通过 `hermes skills list` 命令确认准确的名称。

### 检查项 3：依赖交互式工具的技能

定时任务运行时，`cronjob`、`messaging` 和 `clarify` 这些工具集会被禁用。这是为了防止出现递归创建定时任务、直接发送消息（消息发送工作由调度器处理）以及交互式提示的情况。如果某个技能依赖于这些工具集，那么它在定时任务环境中将无法正常工作。请查阅该技能的文档，确认其是否支持在非交互式（无界面）模式下运行。

### 检查项 4：多个技能的加载顺序

当使用多个技能时，它们会按照指定的顺序加载。如果技能 A 需要依赖技能 B 提供的上下文，请确保先加载技能 B：

```bash
/cron add "0 9 * * *" "..." --skill context-skill --skill target-skill
```

在此示例中，`context-skill`会先于`target-skill`加载。

---

## 任务错误与失败处理

### 检查方法 1：查看最近的任务输出

如果某个任务运行后失败，你可以在以下位置找到错误信息：

1. 任务执行所在的聊天界面（若执行成功）
2. `~/.hermes/logs/agent.log`文件中的调度器相关消息（警告信息则位于`errors.log`中）
3. 通过`hermes cron list`查看该任务的`last_run`元数据

### 检查方法 2：常见错误模式

**脚本相关的“找不到文件或目录”错误**
`script`路径必须是绝对路径（或相对于Hermes配置目录的相对路径）。请确认：
```bash
ls ~/.hermes/scripts/your-script.py   # Must exist
hermes cron edit <job_id> --script ~/.hermes/scripts/your-script.py
```

**任务执行时出现“未找到该技能”错误**
该技能必须安装在运行调度器的机器上。如果在不同机器之间切换，技能不会自动同步——请使用 `hermes skills install <skill-name>` 命令重新安装。

**任务虽已运行但无输出结果**
可能是交付目标存在问题（参见上文“交付失败”部分），或是响应被静默抑制（标记为 `[SILENT]`）。

**任务挂起或超时**
调度器采用基于无操作状态的超时机制（默认为600秒，可通过 `HERMES_CRON_TIMEOUT` 环境变量进行配置，设置为 `0` 表示无限制）。只要代理持续主动调用工具，它就可以继续运行——计时器仅在长时间无操作后才会触发。对于耗时较长的任务，建议使用脚本来处理数据收集工作，并仅输出最终结果。

### 检查项3：锁竞争问题

调度器通过基于文件的锁定机制来避免多个任务同时执行。如果存在两个正在运行的网关实例（或者CLI会话与某个网关发生冲突），任务可能会被延迟或跳过。

请终止重复的网关进程：
```bash
ps aux | grep hermes
# Kill duplicate processes, keep only one
```

### 检查项 4：jobs.json 的权限设置

任务信息存储在 `~/.hermes/cron/jobs.json` 文件中。如果当前用户没有对该文件的读取或写入权限，调度器将会静默失败：

```bash
ls -la ~/.hermes/cron/jobs.json
chmod 600 ~/.hermes/cron/jobs.json   # Your user should own it
```

## 性能问题

### 任务启动缓慢

每项定时任务都会创建一个新的 AIAgent 会话，这一过程可能涉及服务提供者身份验证以及模型加载。对于对时间要求严格的调度任务，建议添加缓冲时间（例如将 `0 9 * * *` 改为 `0 8 * * *`）。

### 重叠任务过多

调度器会在每个时间间隔内按顺序执行任务。如果有多项任务同时到期，它们将依次运行。为避免延迟，可考虑错开任务调度时间（例如分别设置 `0 9 * * *` 和 `5 9 * * *`，而非都设置在 `0 9 * * *`）。

### 脚本输出量过大

那些会产生数百兆字节输出量的脚本会降低代理的处理速度，还可能超出令牌限制。建议在脚本层面进行过滤或汇总，仅输出代理所需的信息以供处理。

---

## 诊断命令

```bash
hermes cron list                    # Show all jobs, states, next_run times
hermes cron run <job_id>            # Schedule for next tick (for testing)
hermes cron edit <job_id>           # Fix configuration issues
hermes logs                         # View recent Hermes logs
hermes skills list                  # Verify installed skills
```

## 获取更多帮助

如果您已按照本指南操作但问题依然存在，可尝试以下方法：

1. 使用 `hermes cron run <job_id>` 命令运行任务（该任务将在下一个网关计时周期触发），并查看聊天输出中的错误信息。
2. 检查 `~/.hermes/logs/agent.log` 文件中的调度器相关消息，以及 `~/.hermes/logs/errors.log` 文件中的警告信息。
3. 在 [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 上提交问题报告，需包含以下内容：
   - 任务 ID 及调度时间
   - 交付目标
   - 您的预期结果与实际发生的情况
   - 日志中的相关错误信息

---

*如需完整的 Cron 参考资料，请参阅 [使用 Cron 自动化各种任务](/guides/automate-with-cron) 以及 [定时任务（Cron）](/user-guide/features/cron)。*
