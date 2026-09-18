---
sidebar_position: 13
title: "Script-Only Cron Jobs (No LLM)"
description: "Classic watchdog cron jobs that skip the LLM entirely — a script runs on schedule and its stdout gets delivered to your messaging platform. Memory alerts, disk alerts, CI pings, periodic health checks."
---

# 仅脚本型的定时任务

有时您已经明确知道想要发送的具体内容。无需借助智能体来处理这些信息——您只需一个可按定时器运行的脚本，其输出（如有）即可被发送至 Telegram、Discord、Slack 或 Signal。

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
- **无需调用大语言模型。** 不消耗任何令牌、不触发任何代理循环，也无需支付模型使用费用。  
- **脚本决定一切。** 由脚本来决定是否发送警报：若输出内容存在，则会发送消息；若无输出，则仅进行静默计时。  
- **支持 Bash 或 Python。** 扩展名为 `.sh` / `.bash` 的文件会在系统 `PATH` 中查找可用的 `bash` 进行执行，否则将使用 `/bin/bash`；其他扩展名的文件则由当前的 Python 解释器处理。所有脚本路径必须位于 `~/.hermes/scripts/` 目录内（相对路径、绝对路径或以 `~` 开头的路径均可，只要仍在该目录中）。Cron 脚本**不会**继承 Hermes 进程环境中的提供者凭证。  
- **统一的调度机制。** 与基于大语言模型的任务一同存储在 `cronjob` 中——暂停、恢复、列表查看、日志记录以及消息发送等功能对所有任务均适用相同规则。  

## 何时使用该模式

以下场景适合使用无代理模式：  
- **内存/磁盘/GPU 监控。** 每 5 分钟运行一次，仅在超出阈值时发出警报。  
- **CI 钩子任务。** 构建完成时提交代码的 SHA 值；构建失败时发送最近的 100 行日志。  
- **周期性指标采集。** 例如通过简单 API 调用获取“每日上午 9 点的 Stripe 收入”数据，再对其进行格式化展示。  
- **外部事件轮询。** 定期检查某个 API，一旦状态发生变化即发出警报。  
- **心跳检测。** 每 N 分钟向控制面板发送一次请求，以确认主机仍在运行。  

而当需要让代理**自行决定**要输出的内容——比如总结长文档、从数据流中筛选重要信息、起草易于理解的文本时，则应使用常规的（基于大语言模型的）Cron 任务。无代理模式仅适用于脚本的标准输出本身就已经是所需消息的场景。

## 通过对话创建监控任务

无代理模式的真正优势在于，代理可以自动为您设置监控机制——无需编辑器、无需终端，也无需记住任何 CLI 参数。您只需描述需求，Hermes 便会生成脚本、安排执行时间，并告知您何时触发警报。

### 对话示例

> **您：** 每5分钟检查一次内存使用率，若超过85%就在Telegram上给我发消息。
>
> **Hermes：** *(生成 `~/.hermes/scripts/memory-watchdog.sh` 文件，然后使用 `no_agent=true` 参数调用 `cronjob(...)`)*
>
> 监控已设置完成。脚本每5分钟执行一次，仅当内存使用率超过85%时才会向 Telegram 发送警报。脚本文件名为 `memory-watchdog.sh`，任务编号为 `abc123`。

在底层，代理会调用两个工具来完成该功能：

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

从那时起，每次触发都会免费：调度器会运行脚本，若标准输出非空则将其发送至 Telegram，而完全不会调用任何模型。

### 代理为您做出的决策

当您提出诸如“在 X 发生时提醒我”或“每 N 分钟检查 Y 并告知我 Z 的情况”之类的请求时，由于消息内容完全由脚本决定，Hermes 的 `cronjob` 工具会自动采用 `no_agent=True` 模式。而当请求需要逻辑推理时（例如“总结新出现的 issue”、“挑选最有趣的标题”、“起草一封友好的提醒函”），则会回退到常规的 LLM 驱动模式。

您无需手动指定 `--no-agent` 参数，只需描述所需的行为即可。

### 通过聊天界面管理监控任务

代理可以像创建任务一样，暂停、恢复、编辑或删除任务：

> **您：** 暂停今晚的内存监控任务
>
> **Hermes：** *(调用 `cronjob(action='pause', job_id='abc123')`)*
>
> 已暂停。如需恢复，请输入“重新启动”或使用命令 `hermes cron resume abc123`。

> **您：** 将间隔改为每 15 分钟
>
> **Hermes：** *(调用 `cronjob(action='update', job_id='abc123', schedule='every 15m')`)*

从创建、列表、更新、暂停、恢复到立即执行、删除，整个任务生命周期都可由代理自动处理，您无需学习任何 CLI 命令。

## 通过 CLI 创建任务

更喜欢使用终端？通过 CLI 仅需三条命令即可实现相同功能：

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

## 脚本输出与传递机制的对应关系

| 脚本行为 | 结果 |
|----------|------|
| 退出码为0，标准输出非空 | 按原样传递标准输出内容 |
| 退出码为0，标准输出为空 | 仅发出无声标记——不进行任何传递 |
| 退出码为0，标准输出的最后一行为 `{"wakeAgent": false}` | 仅发出无声标记（与LLM任务共享同一判定逻辑） |
| 退出码非0 | 会发送错误警报（这样出问题的监控脚本也不会静默失败） |
| 脚本超时 | 会发送错误警报 |

“输出为空则无声”的机制正是经典监控模式的核心：脚本可以每分钟运行一次，但只有当真正有需要处理的情况时，通道才会收到消息。

## 脚本规范

脚本必须存放于 `~/.hermes/scripts/` 目录中。这一要求在任务创建时和运行时都会被严格执行——绝对路径、`~/` 形式的路径以及路径遍历模式（如 `../`）均会被拒绝。该目录也与LLM任务所使用的预检查脚本通道共享。

解释器的选择依据文件扩展名确定：

| 扩展名 | 解释器 |
|--------|--------|
| `.sh`, `.bash` | 来自 `PATH` 的 `bash`（默认为 `/bin/bash`） |
| 其他所有扩展名 | `sys.executable`（当前运行的Python解释器） |

我们刻意不支持以 `#!/...` 开头的脚本声明——明确且简洁地指定解释器，能减少调度器需要依赖的配置项。

## 安排时间的语法

与其他所有cron任务相同：

```bash
hermes cron create "every 5m"        # interval
hermes cron create "every 2h"
hermes cron create "0 9 * * *"       # standard cron: 9am daily
hermes cron create "30m"             # one-shot: run once in 30 minutes
```

如需完整的语法说明，请参阅 [cron 功能参考文档](/user-guide/features/cron)。

## 传递目标

`--deliver` 参数可接收网关所识别的所有内容。常见格式如下：

```bash
--deliver telegram                       # platform home channel
--deliver telegram:-1001234567890        # specific chat
--deliver telegram:-1001234567890:17585  # specific Telegram forum topic
--deliver discord:#ops
--deliver slack:#engineering
--deliver signal:+15551234567
--deliver local                          # just save to ~/.hermes/cron/output/
```

对于 Telegram、Discord、Slack、Signal、SMS 和 WhatsApp 等机器人令牌平台，在运行脚本时无需启动网关——该工具会直接使用存储在 `~/.hermes/.env` 或 `~/.hermes/config.yaml` 中的凭证，调用各个平台的 REST 接口。

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

在基于大语言模型的任务中可行的所有操作（暂停、恢复、手动触发、更改交付目标等），在无智能体任务中同样适用。

## 实际应用示例：磁盘空间预警

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

当两个文件系统的使用率均低于90%时，不会触发任何操作；一旦某个文件系统的使用率超过阈值，就会针对该系统分别发送一行通知。

## 与其他模式的对比

| 方法 | 执行内容 | 适用场景 |
|------|----------|----------|
| `cronjob --no-agent`（本页介绍） | 按Hermes设定的时间表运行您的脚本 | 需要定期监控、发送警报或收集指标，且无需进行逻辑推理的场景 |
| `cronjob`（默认模式，基于LLM） | 带有可选预检查脚本的Agent | 当消息内容需要基于数据进行分析和推理时 |
| 操作系统级cron + `curl`调用[Webhook订阅地址](/user-guide/messaging/webhooks) | 按操作系统设定的时间表运行您的脚本 | 当Hermes本身可能出现故障（即您正在监控的对象出现问题）时 |

对于那些即便在网关关闭的情况下也必须触发警报的关键系统健康监控任务，建议使用操作系统级的cron，再通过简单的`curl`命令向Hermes的Webhook订阅地址（或任何外部警报端点）发送请求——这类脚本作为独立的操作系统进程运行，无需依赖Hermes处于正常状态。而当被监控的对象位于外部时，使用网关内置的调度器则是更合适的选择。

## 相关内容

- [利用Cron实现自动化任务](/guides/automate-with-cron) — 基于LLM的Cron使用模式。
- [定时任务（Cron）参考文档](/user-guide/features/cron) — 完整的调度语法、生命周期及消息分发规则。
- [Webhook订阅功能](/user-guide/messaging/webhooks) — 为外部调度器提供的“发送即忘”型HTTP接口。
- [网关内部机制](/developer-guide/gateway-internals) — 消息分发路由器的内部工作原理。
