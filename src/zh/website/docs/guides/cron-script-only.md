---
sidebar_position: 13
title: "Script-Only Cron Jobs (No LLM)"
description: "Classic watchdog cron jobs that skip the LLM entirely — a script runs on schedule and its stdout gets delivered to your messaging platform. Memory alerts, disk alerts, CI pings, periodic health checks."
---

# 仅脚本型的定时任务

有时您已经明确知道想要发送的消息内容。这种情况下无需借助智能体进行推理——只需编写一个定时运行的脚本，将其输出（如有）发送至 Telegram、Discord、Slack 或 Signal 即可。

Hermes 将这种模式称为**无智能体模式**，即去掉了大型语言模型的传统 Cron 定时系统。
```
   ┌──────────────────┐          ┌──────────────────┐
   │ scheduler tick   │  every   │ run script       │
   │ (every N minutes)│ ──────▶ │ (bash or python) │
   └──────────────────┘          └──────────────────┘
                                          │
                                          │ stdout
                                          ▼
                                 ┌──────────────────┐
                                 │ delivery router  │
                                 │ (telegram/disc…) │
                                 └──────────────────┘
```
- **无需调用大语言模型。** 不消耗任何令牌、无需执行代理循环，也无需支付模型使用费用。  
- **脚本决定一切。** 由脚本来决定是否触发警报：输出内容则发送消息，无输出则静默运行。  
- **支持 Bash 或 Python。** 扩展名为 `.sh`/`.bash` 的文件会在 `/bin/bash` 环境下执行，其他扩展名则通过当前 Python 解释器运行。位于 `~/.hermes/scripts/` 目录下的任意脚本均可使用。  
- **统一的调度机制。** 与大语言模型任务一同存储在 `cronjob` 中，暂停、恢复、列表查看、日志记录以及消息发送等功能对所有任务均适用相同逻辑。  

## 何时使用该模式  

以下场景适合使用无代理模式：  
- **内存/磁盘/GPU 监控。** 每 5 分钟运行一次，仅在超出阈值时发出警报。  
- **CI 钩子任务。** 部署完成时提交提交 SHA 值；构建失败时发送最近的 100 行日志。  
- **周期性指标统计。** 例如通过简单 API 调用获取“每日上午 9 点的 Stripe 收入”数据并进行格式化展示。  
- **外部事件轮询。** 定期检查 API，一旦状态发生变化即发出警报。  
- **心跳检测。** 每 N 分钟向控制面板发送一次请求，以确认主机正常运行。  

当需要让代理**自行决定**要发送的内容——比如总结长文档、从数据流中筛选重要信息、起草更易理解的文本时，则应使用常规的（基于大语言模型的）cron 任务。无代理模式适用于脚本的标准输出本身就已包含所需消息的场景。  

## 通过聊天创建脚本  

无代理模式的真正优势在于，它可以让代理自动为您设置监控脚本——无需使用编辑器、Shell，也无需记住各种 CLI 参数。您只需描述需求，Hermes 便会生成脚本、安排调度时间，并告知您何时会触发警报。  

### 对话示例  

> **您：** 每 5 分钟检查一次内存使用率，若超过 85% 就通过 Telegram 发送提醒给我。  
> 
> **Hermes：** *(生成 `~/.hermes/scripts/memory-watchdog.sh` 脚本，然后使用 `no_agent=true` 参数调用 `cronjob(...)`)*  
> 
> 已设置完成。该脚本每 5 分钟运行一次，仅当内存使用率超过 85% 时才会向 Telegram 发送警报。脚本文件名为 `memory-watchdog.sh`，任务编号为 `abc123`。  

实际上，代理会在此过程中调用两个工具函数来完成操作。

```python
# 1. Write the check script
write_file(
    path="~/.hermes/scripts/memory-watchdog.sh",
    content='''#!/usr/bin/env bash
ram_pct=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$ram_pct" -ge 85 ]; then
  echo "RAM ${ram_pct}% on $(hostname)"
fi
# Empty stdout = silent tick; no message sent.
''',
)

# 2. Schedule it — no_agent=True skips the LLM on every tick
cronjob(
    action="create",
    schedule="every 5m",
    script="memory-watchdog.sh",
    no_agent=True,
    deliver="telegram",
    name="memory-watchdog",
)
```

从那时起，每次触发都会是免费的：调度器会运行脚本，若标准输出非空则将其发送至 Telegram，而完全不会调用任何模型。

### 代理为您做出的决策

当您提出诸如“在 X 发生时提醒我”或“每 N 分钟检查 Y 并告知我 Z 的情况”之类的请求时，由于消息内容完全由脚本决定，Hermes 的 `cronjob` 工具会自动设置为 `no_agent=True` 模式。而当请求需要推理能力时（例如“总结新出现的问题”、“挑选最有趣的标题”、“起草友好的提醒”），则会恢复使用常规的 LLM 驱动模式。

您无需手动指定 `--no-agent` 参数，只需描述所需的行为即可。

### 通过聊天界面管理监控任务

代理可以像创建任务一样，暂停、恢复、编辑或删除这些任务：

> **您：** 暂停今晚的内存监控任务
>
> **Hermes：** *(调用 `cronjob(action='pause', job_id='abc123')`)*
>
> 已暂停。如需恢复，可输入“重新启动”或使用命令 `hermes cron resume abc123`。

> **您：** 将间隔时间改为每 15 分钟
>
> **Hermes：** *(调用 `cronjob(action='update', job_id='abc123', schedule='every 15m')`)*

从创建、列出、更新到暂停、恢复、立即执行乃至删除，整个任务生命周期都由代理直接处理，您无需学习任何 CLI 命令。

## 通过 CLI 创建任务

更喜欢使用命令行？通过三条命令即可实现相同功能：

```bash
# 1. Write your script
cat > ~/.hermes/scripts/memory-watchdog.sh <<'EOF'
#!/usr/bin/env bash
# Alert when RAM usage is over 85%. Silent otherwise.
RAM_PCT=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$RAM_PCT" -ge 85 ]; then
  echo "⚠ RAM ${RAM_PCT}% on $(hostname)"
fi
# Empty stdout = silent run; no message sent.
EOF
chmod +x ~/.hermes/scripts/memory-watchdog.sh

# 2. Schedule it
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"

# 3. Verify
hermes cron list
hermes cron run <job_id>    # fire it once to test
```

就是这样。没有提示词，没有技能，也没有模型。

## 脚本输出与传递方式的对应关系

| 脚本行为 | 结果 |
|----------|------|
| 以状态码 0 退出，标准输出非空 | 按原样传递标准输出内容 |
| 以状态码 0 退出，标准输出为空 | 仅触发静默标记——不进行任何传递 |
| 以状态码 0 退出，标准输出的最后一行为 `{"wakeAgent": false}` | 触发静默标记（与 LLM 任务共享同一逻辑） |
| 以非零状态码退出 | 会发送错误警报（避免故障时出现静默失败） |
| 脚本超时 | 会发送错误警报 |

“输出为空则静默”的机制正是经典看门狗模式的核心：脚本可以每分钟运行一次，但只有当确实有需要处理的情况时，通道才会收到消息。

## 脚本规则

脚本必须存储在 `~/.hermes/scripts/` 目录中。这一要求在任务创建时和运行时都会被强制执行——绝对路径、`~/` 形式的路径以及路径遍历模式（如 `../`）均会被拒绝。该目录也与 LLM 任务所使用的预检查脚本通道共享。

解释器的选择依据文件扩展名：

| 扩展名 | 解释器 |
|--------|--------|
| `.sh`, `.bash` | `/bin/bash` |
| 其他所有扩展名 | `sys.executable`（当前运行的 Python 解释器） |

我们刻意不支持 `#!/...` 形式的脚本头部指令——明确且简洁地指定解释器，能减少调度器需要信任的配置项。

## 计划调度语法

与其他所有 cron 任务相同：

```bash
hermes cron create "every 5m"        # interval
hermes cron create "every 2h"
hermes cron create "0 9 * * *"       # standard cron: 9am daily
hermes cron create "30m"             # one-shot: run once in 30 minutes
```

如需了解完整的语法格式，请参阅[cron功能参考文档](/user-guide/features/cron)。

## 交付目标

`--deliver`参数可接收网关所识别的所有信息。常见的数据格式包括：

```bash
--deliver telegram                       # platform home channel
--deliver telegram:-1001234567890        # specific chat
--deliver telegram:-1001234567890:17585  # specific Telegram forum topic
--deliver discord:#ops
--deliver slack:#engineering
--deliver signal:+15551234567
--deliver local                          # just save to ~/.hermes/cron/output/
```

对于 Telegram、Discord、Slack、Signal、SMS 和 WhatsApp 等机器人令牌平台，在运行脚本时无需启动网关——该工具会直接使用存储在 `~/.hermes/.env` 或 `~/.hermes/config.yaml` 中的凭据，调用各平台的 REST 接口。

## 编辑与生命周期管理

```bash
hermes cron list                                    # see all jobs
hermes cron pause <job_id>                          # stop firing, keep definition
hermes cron resume <job_id>
hermes cron edit <job_id> --schedule "every 10m"    # adjust cadence
hermes cron edit <job_id> --agent                   # flip to LLM mode
hermes cron edit <job_id> --no-agent --script …     # flip back
hermes cron remove <job_id>                         # delete it
```

在基于大语言模型的任务中可行的所有操作（暂停、继续、手动触发、更改交付目标等），在无智能体任务中同样适用。

## 实际应用示例：磁盘空间警报

```bash
cat > ~/.hermes/scripts/disk-alert.sh <<'EOF'
#!/usr/bin/env bash
# Alert when / or /home is over 90% full.
THRESHOLD=90
df -h / /home 2>/dev/null | awk -v t="$THRESHOLD" '
  NR > 1 && $5+0 >= t {
    printf "⚠ Disk %s full on %s\n", $5, $6
  }
'
EOF
chmod +x ~/.hermes/scripts/disk-alert.sh

hermes cron create "*/15 * * * *" \
  --no-agent \
  --script disk-alert.sh \
  --deliver telegram \
  --name "disk-alert"
```

当两个文件系统的使用率均低于90%时，不会触发任何操作；一旦某个文件系统的使用率超过阈值，就会针对该系统各发送一行通知。

## 与其他模式的对比

| 方法 | 执行内容 | 适用场景 |
|------|----------|----------|
| `cronjob --no-agent`（本页介绍） | 按Hermes预设的时间表运行您的脚本 | 需要定期监控、发出警报或收集指标，且无需进行逻辑推理的场景 |
| `cronjob`（默认模式，基于LLM） | 带有可选预检查脚本的Agent | 当消息内容需要基于数据进行分析和推理时 |
| 操作系统cron任务 + `curl`调用[Webhook订阅](/user-guide/messaging/webhooks) | 按操作系统预设的时间表运行您的脚本 | 当被监控的Hermes服务可能出现异常时 |

对于那些即便在网关故障时也必须触发警报的关键系统健康监控任务，建议使用操作系统的cron任务，再通过简单的`curl`命令调用Hermes的Webhook订阅（或任何外部警报接口）——这类任务作为独立的操作系统进程运行，无需依赖Hermes服务正常运行。而当被监控的对象位于外部时，使用网关内置的调度器则是更合适的选择。

## 相关内容

- [利用Cron实现任意自动化任务](/guides/automate-with-cron) — 基于LLM的Cron调度模式。
- [定时任务（Cron）参考手册](/user-guide/features/cron) — 完整的调度语法、生命周期及消息传递路径说明。
- [Webhook订阅](/user-guide/messaging/webhooks) — 为外部调度器提供的“发送即忘”型HTTP接口。
- [网关内部机制](/developer-guide/gateway-internals) — 消息传递路由器的内部工作原理。
