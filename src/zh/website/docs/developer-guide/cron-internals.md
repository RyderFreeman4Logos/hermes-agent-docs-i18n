---
sidebar_position: 11
title: "Cron Internals"
description: "How Hermes stores, schedules, edits, pauses, skill-loads, and delivers cron jobs"
---

# Cron 内部机制

Cron 子系统用于执行定时任务——从简单的单次延迟任务，到支持技能注入与跨平台交付的周期性 Cron 表达式任务，功能一应俱全。

## 关键文件

| 文件 | 功能 |
|------|------|
| `cron/jobs.py` | 任务模型、存储机制，以及对 `jobs.json` 的原子读写操作 |
| `cron/scheduler.py` | 调度器循环——负责检测到期任务、执行任务并跟踪重复执行情况 |
| `tools/cronjob_tools.py` | 面向模型的 `cronjob` 工具注册与处理逻辑 |
| `gateway/run.py` | 网关集成——在长时间运行的循环中定时触发 Cron 任务 |
| `hermes_cli/cron.py` | CLI 中的 `hermes cron` 子命令 |

## 调度模型

系统支持四种调度格式：

| 格式 | 示例 | 行为特点 |
|------|------|----------|
| **相对延迟** | `30m`, `2h`, `1d` | 单次执行，在指定时间过后触发 |
| **间隔时间** | `every 2h`, `every 30m` | 周期性执行，按固定间隔触发 |
| **Cron 表达式** | `0 9 * * *` | 标准的五字段 Cron 语法（分钟、小时、日期、月份、星期几） |
| **ISO 时间戳** | `2025-01-15T09:00:00` | 单次执行，在精确到秒的时间点触发 |

面向模型的接口为单一的 `cronjob` 工具，提供类似操作命令的功能：`create`、`list`、`update`、`pause`、`resume`、`run`、`remove`。

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

### `last_status` 字面值

`last_status` 是一个封闭的集合，仅由 `cron.jobs.mark_job_run` 写入。所有的渲染器（如 `hermes cron list`/`doctor`、`cronjob` 工具、Web 控制台徽章以及桌面任务检查器）都会对这些字面值进行显式映射——用户无需通过测试 `== "ok"` 来判断“是否已获取结果”：

| 字面值 | 含义 | 详细字段 |
|---------|------|----------|
| `ok` | Agent 运行成功，且（如指定了目标）已确认内容送达 | — |
| `error` | Agent 运行失败 | `last_error` |
| `delivery_failed` | Agent 运行成功，但输出内容未能送达目标 | `last_delivery_error`（此时 `last_error` 为 `null`） |
| `blocked_config` | 预发送验证拒绝启动该任务 | `last_error` |

### 任务生命周期状态

| 状态 | 含义 |
|-------|------|
| `scheduled` | 已激活，将在下一个预定时间触发 |
| `paused` | 已暂停——在恢复之前不会触发 |
| `completed` | 重复执行次数已达上限，或为一次性任务且已执行完成 |
| `running` | 正在执行中（临时状态） |

### 向后兼容性

旧版本的任务可能仅包含一个 `skill` 字段，而非 `skills` 数组。调度器会在加载时对此进行标准化处理——单个 `skill` 会被转换为 `skills: [skill]` 的形式。

## 调度器运行时

### 计时周期

调度器以固定的时间间隔运行（默认为每 60 秒）：

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

在网关模式下，用于决定任务*执行时间*的定时触发器（即“轴B”）是通过可插拔的 `CronScheduler` 提供程序来选定的。网关会调用 `resolve_cron_scheduler()` 函数（位于 `cron/scheduler_provider.py` 文件中），并在一个专用的后台线程中运行选定提供程序的 `start()` 方法，同时还会启动另一个用于处理网关内部任务的线程。

当前激活的提供程序由 `cron.provider` 配置键决定：

- **空值（默认值）** → 内置的 `InProcessCronScheduler`，它会以进程内循环的方式运行，每60秒调用一次 `scheduler.tick()` 方法。其功能与在引入提供程序之前的行为完全一致。
- **指定名称的提供程序**（例如 `chronos`，一种适用于零扩展部署的定时任务管理工具）→ 从 `plugins/cron_providers/<名称>/` 或 `$HERMES_HOME/plugins/<名称>/` 路径下加载。

如果指定的提供程序不存在、无法加载，或返回 `is_available() == False` 的结果，解析器会发出警告并回退到内置提供程序——**绝不会让定时任务在没有触发器的情况下运行**。由于内置提供程序位于核心代码中（`cron/scheduler_provider.py`），而非 `plugins/` 目录下，因此不会意外被移除。

所谓“任务执行”（包括任务运行与结果传递）的含义对所有提供程序而言都是相同的，相关操作仍由 `scheduler.run_job()` 和 `scheduler._deliver_result()` 函数完成。提供程序仅能控制触发机制，而无法控制任务的执行过程。

在命令行模式下，定时任务仅在运行 `hermes cron` 命令或处于活跃的命令行会话期间才会被触发。

### 适用于零扩展部署的托管定时任务服务（Chronos）

托管型网关可以使用 **Chronos** 提供程序（`cron.provider: chronos`）来替代内置的定时器。Chronos 能让处于空闲状态的网关**完全停止运行**，同时仍能执行定时任务：它不会像传统的 60 秒循环那样让进程持续处于活跃状态，而是会请求 Nous 基础设施在每个任务的真正触发时间，**精确地启动一次该任务的单次执行**。当触发时间到来时，Nous 会通过经过身份验证的 webhook（`POST /api/cron/fire`）重新唤醒网关；网关会通过与内置定时器相同的 `run_one_job` 流程来执行该任务，之后再为下一个任务准备单次执行。在两次触发之间，进程可以被完全终止——它仅在真正需要执行任务时才会被唤醒，而不会因周期性计时而持续运行。

其工作流程如下（调度功能由 Nous 提供，代理本身不持有任何调度相关凭证）：

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

配置项（均为非敏感信息；在托管型代理中，Nous会在部署时设置这些值）：

| 键值 | 含义 |
|---|---|
| `cron.provider` | 激活的计时服务，值为 `chronos`（留空则表示使用内置计时器） |
| `cron.chronos.portal_url` | Nous 的基础 URL（用于触发任务及生成 fire-token） |
| `cron.chronos.callback_url` | 网关用于接收传入任务的公共基础 URL |
| `cron.chronos.expected_audience` | 该代理所使用的 fire-token 目标受众 |
| `cron.chronos.nas_jwks_url` | 用于验证传入 fire-token 的密钥集 |

如果 Chronos 配置错误或代理未登录 Nous，`resolve_cron_scheduler()` 函数会回退到内置计时器（并记录警告信息）——这样任务触发功能就不会失效。周期性任务会在每次触发后重新启动；而设定为执行 N 次的任务在次数用尽后会正常停止（不会留下未完成的一次性任务）。关于代理与 Nous 之间交互的完整规范可见 `docs/chronos-managed-cron-contract.md` 文件。

### 新会话隔离机制

每个定时任务都在一个全新的代理会话中运行：

- 不保留之前任务的对话历史记录
- 不记忆之前的定时任务执行情况（不过与其他代理任务一样，持久化存储机制——如 MEMORY.md 和 USER.md——仍会加载，因此长期设置的偏好设置和事实信息可以保留；但每次任务运行的临时对话上下文则不会保留）
- 提示内容必须完整自包含——定时任务不得提出需要进一步澄清的问题
- `cronjob` 工具集已被禁用（以防止递归调用）

## 基于技能的任务处理

定时任务可通过 `skills` 字段绑定一个或多个技能。在任务执行时：

1. 技能会按照指定的顺序加载。
2. 每个技能的SKILL.md文件内容会被作为上下文注入。
3. 任务提示语会被附加作为具体指令。
4. 智能体便会基于整合后的技能上下文与指令来进行处理。

这样一来，无需在定时任务提示语中重复粘贴完整的指令，即可实现可复用且经过测试的工作流程。例如：

```
Create a daily funding report → attach "ai-funding-daily-report" skill
```

### 基于脚本的任务

任务还可以通过 `script` 字段附加 Python 脚本。该脚本会在每个智能体轮次开始前执行，其标准输出会被作为上下文注入到提示词中。这样一来，便可实现数据收集与变化检测功能：

```python
# ~/.hermes/scripts/check_competitors.py
import requests, json
# Fetch competitor release notes, diff against last run
# Print summary to stdout — agent analyzes and reports
```

脚本的超时时间默认为3600秒（1小时）。`_get_script_timeout()`函数通过三层机制来确定这一限制值：

1. **模块级覆盖** — `_SCRIPT_TIMEOUT`（用于测试或动态修改）。仅当该值与默认值不同时才会生效。
2. **环境变量** — `HERMES_CRON_SCRIPT_TIMEOUT`
3. **配置文件** — `config.yaml`中的`cron.script_timeout_seconds`项（通过`load_config()`函数读取）
4. **默认值** — 3600秒（1小时）

此超时限制仅适用于**运行前的脚本**，而不涉及整个Agent。基于技能或大型语言模型的任务则遵循独立的“空闲时间”机制来控制运行时长（相关参数为`HERMES_CRON_TIMEOUT`，默认为空闲600秒，值为`0`表示无限制）——只要这些任务持续调用工具或传输Token，就可以运行数小时；只有在其处于配置好的空闲状态且没有活动时才会被终止。脚本会被发送到持续的线程池中处理（不会被tick锁占用），因此长时间运行的脚本不会阻碍其他待处理任务的执行。

在超时或所有权被取消的情况下，`cron.scheduler_script` 会使用共享的 `agent.deadline.kill_process_tree` 强制终止机制。在 POSIX 环境中，该机制会首先短暂暂停并重新扫描进程树，随后向子进程及其父进程发送终止信号，包括那些处于独立会话中且没有继承输出管道的子进程。这样可以避免“快照后分叉”带来的竞争条件问题。暂停等待的时间是有限制的；若发生发现失败或权限错误，系统仍会采用尽力而为的群组清理方式，而非提供沙箱级的保证。任何因清理而被终止的目标进程，如果终止操作失败，将会重新启动；而已被终止的目标则保持其原始状态。显式的优雅终止信号不会暂停接收进程的执行。Windows 系统则继续使用 `taskkill /F /T` 命令。

### 提供商恢复机制

`run_job()` 会将用户配置的备用提供商及凭证池传递给 `AIAgent` 实例：

- **备用提供商**——从 `config.yaml` 中读取 `fallback_providers`（列表形式）或 `fallback_model`（旧版字典形式），其格式与网关的 `_load_fallback_model()` 函数要求一致。这些配置会以 `fallback_model=` 的形式传递给 `AIAgent.__init__` 方法，该方法会将两种格式统一为一条备用提供商链。
- **凭证池**——通过 `agent.credential_pool` 中的 `load_pool(provider)` 函数，并结合已确定的运行时提供商名称来加载凭证池。只有当凭证池中存在有效凭证（即 `pool.has_credentials()` 返回真值）时，才会传递该凭证池。此机制支持在遇到 429/速率限制错误时对同一提供商的密钥进行轮换。

这一设计与网关的行为保持一致——若没有该机制，定时任务代理在遭遇速率限制时会直接失败而不会尝试恢复。

## 交付模式

定时任务的结果可以发送到任何受支持的平台。若仅输入平台名称（如 `slack`、`telegram` 等），结果将发送至该平台已配置的**主频道**。若需指定**特定**目标地址，则需在冒号后添加目标地址，格式为 `platform:<target>`。目标地址会在任务执行时确定（而非创建任务时），因此即便某个平台尚未连接，任务仍可指定其作为目标地址，待该平台上线后再开始发送内容。大多数平台还支持再添加第三个参数，即可选的讨论串/主题编号，格式为 `platform:<chat_id>:<thread_id>`。

| Target | Syntax | Example |
|--------|--------|---------|
| Origin chat | `origin` | Deliver to the chat where the job was created |
| Local file | `local` | Save to `~/.hermes/cron/output/` |
| Telegram | `telegram`, `telegram:<chat_id>`, `telegram:<chat_id>:<thread_id>`, `telegram:@username` | `telegram:-1001234567890:17585` |
| Discord | `discord`, `discord:#channel`, `discord:<channel_id>`, `discord:<channel_id>:<thread_id>` | `discord:#engineering` |
| Slack | `slack`, `slack:#channel`, `slack:<channel_id>`, `slack:<channel_id>:<thread_ts>` | `slack:#engineering` |
| Matrix | `matrix`, `matrix:<!room_id:server>`, `matrix:<@user:server>` | `matrix:!abc123:example.org` |
| Feishu | `feishu`, `feishu:<chat_id>`, `feishu:<chat_id>:<thread_id>` | `feishu:oc_abc123def` |
| WhatsApp | `whatsapp`, `whatsapp:<jid>`, `whatsapp:+<E.164>` | `whatsapp:123456@g.us` |
| Signal | `signal`, `signal:group:<id>`, `signal:+<E.164>` | `signal:group:aBcD==` |
| SMS | `sms`, `sms:+<E.164>` | `sms:+<E.164 number>` |
| Email | `email`, `email:<address>` | `email:alerts@example.com` |
| Weixin | `weixin`, `weixin:<wxid>` | `weixin:wxid_abc123` |
| Mattermost | `mattermost` or `mattermost:<channel_id>` | Bare name delivers to Mattermost home |
| Home Assistant | `homeassistant` or `homeassistant:<conversation>` | Bare name delivers to HA conversation |
| DingTalk | `dingtalk` or `dingtalk:<chat_id>` | Bare name delivers to DingTalk |
| WeCom | `wecom` or `wecom:<chat_id>` | Bare name delivers to WeCom |
| BlueBubbles | `bluebubbles` or `bluebubbles:<chat_guid>` | Bare name delivers to iMessage via BlueBubbles |
| QQ Bot | `qqbot` or `qqbot:<chat_id>` | Bare name delivers to QQ (Tencent) via Official API v2 |
| Bot Chat | `bot-chat` or `bot-chat:<profile>` | Inject into a local profile's canonical Bot Chat (the bot responds) |

第一组平台拥有明确且经过验证的目标语法——即命名频道（`#channel`）、主题/线程、房间/用户 ID、群组 ID 或电话号码。其余平台则接受通用的 `platform:<chat_id>` 格式（冒号后的值将直接作为目标 ID 使用）；仅使用平台名称时，消息会始终发送至该平台的默认频道。

**命名频道**（如 `slack:#engineering`、`discord:#engineering`，或是更友好的名称 `slack:engineering`）会通过网关从连接的适配器中构建的频道目录进行解析，因此网关必须已发现该频道才能完成名称解析；而直接使用原始 ID（如 `slack:C0123ABCD45`）则始终有效。

对于 **Telegram 主题**，应使用 `telegram:<chat_id>:<thread_id>` 格式（例如 `telegram:-1001234567890:17585`）。至于 **Slack 线程**，第三部分为父消息的 `thread_ts` 值（例如 `slack:C0123ABCD45:1700000000.000100`），因此此格式仅适用于在现有消息下回复的场景。

**Bot Chat**（`bot-chat`、`bot-chat:<profile>`）是一种本地伪平台，并非网关适配器。具备邮件箱功能的默认实时所有者会立即收到持久性通知（无论其当前处于空闲还是忙碌状态），只有该所有者才能处理传入的对话轮次。系统会通过 `scheduler_delivery._deliver_to_bot_chat` 函数，利用 `get_profile_dir` 或任务当前的 `get_hermes_home` 值来确定目标地址，再根据源端默认频道、任务 ID、持久性 `execution_id` 以及目标默认频道来生成接收确认 ID，且在确定所有者之前会先检查该确认信息。已存在的接收确认信息绝不允许启用 CLI 备用方案。若未指定邮件箱所有者，系统将保持原有的 `hermes [-p <profile>] chat --in ~ -c "Bot Chat" --create-if-missing -Q --query-file <tmp>` 命令结构及常规的所有权隔离机制。两种处理路径均会生成真实的实时对话内容，而非仅复制对话记录。已排队或已被认领的接收记录会将对应的接收记录 ID 存入 `last_delivery_queued` 中。交付聚合器会将非真实错误导致的拒绝通知排除在外，并将执行结果标记为 `delivery_outcome=queued`；而成功完成的任务则会被标记为 `last_status=delivery_queued`。针对混合目标发生的真实错误会被视为失败处理，同时仍保留排队中的接收记录元数据。目标配置文件中定义的持久性接收记录是判定任务是否完成的标准依据。所谓“已排队”仅代表历史上的处理状态，并不能作为消息已成功交付的证明。历史性的 cron 状态不会自动跟踪后续的接收完成情况。Bot-Chat 类型目标会被排除在 `all` 模式及凭据预检流程之外。仅用于 Bot-Chat 的外部工作节点可直接绕过网关交付队列；而混合类型的外部工作节点则仍需经过网关转接。参数 `cron.bot_chat_delivery_timeout_seconds`（默认值为 600）仅适用于传统的子进程处理路径。

### 响应封装

默认情况下（`cron.wrap_response: true`），cron 类型的消息交付会包含以下封装内容：
- 一个用于标识 cron 作业名称及任务的标题行；
- 一个脚注，说明代理无法查看对话中的已交付消息。

在 cron 响应中添加 `[SILENT]` 前缀可完全禁用消息交付——这非常适合那些仅需向文件写入数据或执行其他辅助操作的作业。

### 会话隔离

定时任务发送的内容不会被同步到网关会话的对话历史中，仅存在于该定时任务的独立会话中。这样可以避免目标聊天对话中出现消息顺序混乱的问题。

## 递归防护机制

通过禁用定时任务会话中的 `cronjob` 工具集，可防止以下情况发生：
- 定时任务自行创建新的定时任务
- 导致令牌消耗激增的递归调度
- 在任务执行过程中意外修改任务调度设置

## 锁定机制

调度器采用跨进程的基于文件的锁定机制（Unix系统使用 `fcntl.flock`，Windows系统使用 `msvcrt.locking`），以确保即使是在网关的进程内计时器与独立的 `hermes cron` 命令或手动调用的 `tick()` 函数之间，也不会出现重复执行同一批待处理任务的情况。如果无法获取锁，`tick()` 函数会立即返回0值。

## CLI接口

`hermes cron` CLI提供了直接的任务管理功能：

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
