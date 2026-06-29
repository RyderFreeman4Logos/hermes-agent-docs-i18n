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

### 网关集成

在网关模式下，用于决定任务*触发时间*的 cron **触发器**（即“轴B”）是通过可插拔的 `CronScheduler` 提供程序来选定的。网关会调用 `resolve_cron_scheduler()` 函数（位于 `cron/scheduler_provider.py` 文件中），并在一个专用的后台线程中运行选定提供程序的 `start()` 方法，同时还会启动一个独立的网关维护线程。

当前生效的提供程序由 `cron.provider` 配置键决定：

- **空值（默认值）** → 内置的 `InProcessCronScheduler`，它会以每60秒调用一次 `scheduler.tick()` 的方式运行内置的循环处理逻辑。其行为与旧版提供程序完全一致。
- **指定名称的提供程序**（例如 `chronos`，一种适用于零扩展部署的托管型 cron 提供程序）→ 从 `plugins/cron/<name>/` 或 `$HERMES_HOME/plugins/<name>/` 路径中加载。

如果指定的提供程序不存在、无法加载，或返回 `is_available() == False` 的结果，解析器会发出警告并回退到内置提供程序——**绝不会让 cron 陷入无触发器的状态**。由于内置提供程序位于核心代码库中（`cron/scheduler_provider.py`），而非 `plugins/` 目录下，因此不会意外被移除。

所谓“触发”所代表的含义（任务执行与结果传递）对所有提供程序而言都是相同的，相关逻辑仍存在于 `scheduler.run_job()` 和 `scheduler._deliver_result()` 函数中。提供程序仅负责控制触发时机，而无法干预任务的实际执行过程。

在 CLI 模式下，cron 任务仅在运行 `hermes cron` 命令或处于活跃的 CLI 会话期间才会被触发。

### 适用于零扩展部署的托管型 cron（Chronos）

托管型网关可以使用 **Chronos** 提供程序（配置项为 `cron.provider: chronos`）来替代内置的定时器。Chronos 允许处于空闲状态的网关实现**零扩展**，同时仍能触发 cron 任务：它不会像内置方案那样运行每60秒一次的循环以保持进程运行，而是通过 Nous 基础设施在每个任务的真正触发时间点，精确地启动**一个一次性任务处理实例**。当触发时刻到来时，Nous 会通过经过身份验证的 webhook（请求地址为 `POST /api/cron/fire`）向网关发送通知；网关会通过与内置方案相同的 `run_one_job` 路径执行该任务，之后再启动下一个一次性任务处理实例。在两次触发之间，网关进程可以完全停止——它仅在真正需要执行任务时才会唤醒，而不会因定时器而持续运行。

整个流程由 Nous 提供托管型调度器，代理端无需持有任何调度器相关凭证：

```
create/update a cron job
  → Chronos asks Nous to arm a one-shot at the job's next_run_at
      (authenticated with the agent's existing Nous token)
  → at fire time Nous calls the gateway: POST {callback_url}/api/cron/fire
      (authenticated with a short-lived, purpose-scoped Nous-minted JWT)
  → the gateway verifies the token, claims the job (store compare-and-set so
    multi-replica deployments fire at-most-once), runs it, and re-arms the next
    one-shot
```

配置项（均为非敏感信息；在托管型智能体中，Nous会在部署时设置这些值）：

| 键名 | 含义 |
|---|---|
| `cron.provider` | 激活的计时服务，值为 `chronos`（留空则表示使用内置计时器） |
| `cron.chronos.portal_url` | Nous的基础网址（用于触发任务及生成火令牌） |
| `cron.chronos.callback_url` | 网关用于接收外部请求的公共基础网址 |
| `cron.chronos.expected_audience` | 该智能体所生成的火令牌的预期使用方 |
| `cron.chronos.nas_jwks_url` | 用于验证传入火令牌的密钥集 |

如果Chronos配置错误或智能体未登录Nous，`resolve_cron_scheduler()`函数会回退到内置计时器，并记录警告信息——这样任务触发功能就不会丢失。周期性任务会在每次触发后重新启动；而设置“重复N次”的任务在达到指定次数后会正常停止，不会留下未完成的一次性任务。关于智能体与Nous之间的完整交互协议，可参阅`docs/chronos-managed-cron-contract.md`文档。

### 新会话隔离机制

每个定时任务都在一个全新的智能体会话中运行：

- 不保留之前任务的对话历史
- 不记忆之前的定时任务执行记录（除非手动保存到内存或文件中）
- 提示语必须完整独立——定时任务无法提出补充性问题
- `cronjob`工具集已被禁用（以防止递归调用）

## 基于技能的任务处理

定时任务可通过`skills`字段绑定一个或多个技能。在执行时，系统会按指定顺序加载这些技能，再将每个技能对应的SKILL.md文件内容作为上下文注入，同时把任务的提示语作为具体指令附加进去，最终由智能体处理整合后的技能上下文与指令。这种方式无需在定时任务提示语中重复输入完整指令，即可实现可复用、经过测试的工作流程。例如：

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

1. **模块级覆盖** — `_SCRIPT_TIMEOUT`（用于测试或monkeypatch操作）。仅当该值与默认值不同时才会生效。
2. **环境变量** — `HERMES_CRON_SCRIPT_TIMEOUT`
3. **配置文件** — `config.yaml`中的`cron.script_timeout_seconds`项（通过`load_config()`函数读取）
4. **默认值** — 120秒

### 备用提供者机制

`run_job()`函数会将用户配置的备用提供者及凭证池传递给`AIAgent`实例：

- **备用提供者** — 从`config.yaml`中读取`fallback_providers`（列表形式）或`fallback_model`（旧版字典形式），其格式与网关的`_load_fallback_model()`函数要求一致。这些参数会以`fallback_model=`的形式传递给`AIAgent.__init__`方法，该方法会将两种格式统一处理为备用提供者链。
- **凭证池** — 通过`load_pool(provider)`函数，根据已确定的运行时提供者名称从`agent.credential_pool`中加载凭证池。仅当凭证池中存在有效凭证（即`pool.has_credentials()`返回真值）时才会传递该凭证池。此机制可在遇到429限流错误时实现同一提供者下的密钥轮换。

这一设计与网关的行为保持一致——若没有该机制，定时任务在遇到限流时会直接失败而无法尝试恢复。

## 交付方式

定时任务的执行结果可发送到任何支持的目标平台。

仅输入平台名称（如`slack`、`telegram`等）即可将结果发送到该平台配置的**主频道**。若需指定**特定**目标，则可在名称后加上冒号并注明目标地址，格式为`platform:<target>`。目标地址会在任务执行时才进行解析（而非创建任务时），因此即使某个平台尚未连接，任务仍可指定其目标地址，待平台上线后再开始发送结果。

大多数平台还支持第三个参数，即线程或主题标识：`platform:<chat_id>:<thread_id>`。

| 目标类型 | 语法格式 | 示例 |
|----------|----------|------|
| 原始聊天窗口 | `origin` | 将结果发送到创建任务的聊天窗口 |
| 本地文件 | `local` | 保存到`~/.hermes/cron/output/`目录 |
| Telegram | `telegram`、`telegram:<chat_id>`、`telegram:<chat_id>:<thread_id>`、`telegram:@username` | `telegram:-1001234567890:17585` |
| Discord | `discord`、`discord:#channel`、`discord:<channel_id>`、`discord:<channel_id>:<thread_id>` | `discord:#engineering` |
| Slack | `slack`、`slack:#channel`、`slack:<channel_id>`、`slack:<channel_id>:<thread_ts>` | `slack:#engineering` |
| Matrix | `matrix`、`matrix:<!room_id:server>`、`matrix:<@user:server>` | `matrix:!abc123:example.org` |
| 飞书 | `feishu`、`feishu:<chat_id>`、`feishu:<chat_id>:<thread_id>` | `feishu:oc_abc123def` |
| WhatsApp | `whatsapp`、`whatsapp:<jid>`、`whatsapp:+<E.164>` | `whatsapp:123456@g.us` |
| Signal | `signal`、`signal:group:<id>`、`signal:+<E.164>` | `signal:group:aBcD==` |
| 短信 | `sms`、`sms:+<E.164>` | `sms:+<E.164 number>` |
| 邮件 | `email`、`email:<address>` | `email:alerts@example.com` |
| 微信 | `weixin`、`weixin:<wxid>` | `weixin:wxid_abc123` |
| Mattermost | `mattermost`或`mattermost:<channel_id>` | 仅输入名称则发送到Mattermost主频道 |
| Home Assistant | `homeassistant`或`homeassistant:<conversation>` | 仅输入名称则发送到HA对话窗口 |
| 钉钉 | `dingtalk`或`dingtalk:<chat_id>` | 仅输入名称则发送到钉钉 |
| 微信工作台 | `wecom`或`wecom:<chat_id>` | 仅输入名称则发送到微信工作台 |
| BlueBubbles | `bluebubbles`或`bluebubbles:<chat_guid>` | 仅输入名称则通过BlueBubbles发送到iMessage |
| QQ机器人 | `qqbot`或`qqbot:<chat_id>` | 仅输入名称则通过腾讯官方API v2发送到QQ |

第一组平台拥有明确且经过验证的目标地址语法——包括带名称的频道（如`#channel`）、主题/线程、房间/用户ID、群组ID或电话号码。其余平台则支持通用的`platform:<chat_id>`格式（冒号后的值将直接作为目标ID使用）；仅输入平台名称则始终发送到该平台的主频道。

**带名称的频道**（如`slack:#engineering`、`discord:#engineering`，或类似`slack:engineering`的友好名称）会依据网关从已连接的适配器中构建的频道目录进行解析，因此网关必须已发现该频道才能完成名称解析；而纯数字ID（如`slack:C0123ABCD45`）则始终有效。

对于**Telegram主题**，应使用`telegram:<chat_id>:<thread_id>`格式（例如`telegram:-1001234567890:17585`）。**Slack线程**的第三个参数为父消息的`thread_ts`值（例如`slack:C0123ABCD45:1700000000.000100`），因此该格式仅适用于在现有消息下回复时使用。

### 响应封装

默认情况下（即`cron.wrap_response: true`），定时任务的结果会被封装为包含以下内容的格式：
- 一个用于标识定时任务名称及具体任务的头部信息
- 一个底部说明，指出代理无法在对话中查看已发送的消息

若在定时任务响应前添加 `[SILENT]` 前缀，则可完全禁止结果发送——这适用于仅需向文件写入数据或执行其他副作用的任务。

### 会话隔离

定时任务的结果不会被记录到网关的会话对话历史中，仅存在于该定时任务自身的会话中。这一设计可避免目标聊天窗口中的对话出现消息顺序混乱的问题。

## 递归防护机制

运行定时任务的会话中会禁用`cronjob`工具集。此举可防止：
- 定时任务自行创建新的定时任务
- 导致令牌消耗激增的递归调度行为
- 在任务内部意外修改任务调度设置

## 锁定机制

调度器会使用跨进程的基于文件的锁定机制（Unix系统使用`fcntl.flock`，Windows系统使用`msvcrt.locking`）来确保同一批待处理任务不会被重复执行——即便是在网关的进程内定时器与独立的`hermes cron`命令或手动调用的`tick()`函数之间也是如此。如果无法获取锁定，`tick()`函数会立即返回0。

## CLI接口

`hermes cron` CLI工具提供了直接的作业管理功能：

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
