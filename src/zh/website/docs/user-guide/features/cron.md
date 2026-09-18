---
sidebar_position: 5
title: "Scheduled Tasks (Cron)"
description: "Schedule automated tasks with natural language, manage them with one cron tool, and attach one or more skills"
---

# 定时任务（Cron）

您可以使用自然语言或 Cron 表达式来安排任务自动运行。Hermes 通过一个统一的 `cronjob` 工具来实现 Cron 任务管理，该工具提供类似操作指令的接口，无需单独的调度、列表或删除工具。

## Cron 目前具备的功能

Cron 任务可以：

- 安排一次性任务或周期性任务
- 暂停、恢复、编辑、触发及删除任务
- 为单个任务绑定零个、一个或多个技能
- 将执行结果返回至原始聊天界面、本地文件或已配置的平台目标地址
- 在带有常规静态工具列表的新的智能体会话中运行
- 以**无智能体模式**运行——即按计划执行脚本，其标准输出会被原样传递，完全不涉及大语言模型（详见下文的[无智能体模式：仅脚本任务](#no-agent-mode-script-only-jobs)部分）

所有这些功能均可通过 `cronjob` 工具在 Hermes 自身实现，因此您无需使用命令行界面，只需用自然语言下达指令即可创建、暂停、编辑或删除任务。

:::tip
**Cron 任务是基于哪种模型运行的？** 任务执行时的模型确定方式如下：先根据每个任务的指定配置 → 查看 `config.yaml` 文件中的 `cron.model` 设置 → 若未指定则使用 `hermes model` 中的全局默认值。

- **任务级固定配置**——由您通过控制面板、`hermes cron create/edit --model … --provider …` 命令，或通过编辑 `~/.hermes/cron/jobs.json` 文件来设置。一旦设置，该配置将一直保持不变，直到您主动更改它。Agent 的 `cronjob` 工具无法设置或修改任务级的模型——推理固定配置由用户自行掌控。

- **`cron.model` / `cron.model_provider`**——这是 cron-fleet 的默认设置：所有未指定固定模型的任务都将使用该模型进行运行，且与您的聊天模型无关。只需设置一次（通过 `hermes config set cron.model <name>`），之后即使您使用 `hermes model` 或 `/model` 命令更换聊天模型，也不会影响已有的 cron 任务。

- **全局默认设置**——仅当上述两项均未设置时，任务才会遵循 `hermes model` 的设置。Hermes 会在任务创建时对对应的模型和提供方进行“快照”处理，该快照即成为任务的实际固定配置：即便您后续更改了全局默认设置（通过 `hermes model`、`/model` 或 `hermes config set model.default …`），任务仍会继续在创建时所指定的模型和提供方上运行，同时每次运行都会输出一条 INFO 级日志说明当前设置与之前的差异。全局模型的更改不会中断任何已安排的定时任务，而无人监控的任务也不会自动继承到付费的模型或提供方（参见 #44585）。若要将某个任务切换到新的默认设置，需为其指定固定配置（通过 `hermes cron edit <job_id> --provider <provider> --model <model>`），或直接设置 `cron.model` 以一次性更新所有任务。在快照功能出现之前创建的任务，则会继续遵循实时的全局默认设置。
无论任务最终由哪个提供商处理，其针对该提供商的特定请求设置（例如自定义提供商所用的 `request_overrides`，如 `extra_body`/`extra_headers`）都会像在交互式会话中一样被带入到定时任务执行过程中。

由于 OAuth 刷新是自动完成的，`hermes setup --portal` 是实现无人值守运行的最简便方式。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

:::提示
**单任务推理强度设置。** 任务可以独立于模型设定的强度，自行指定推理级别：可选值为 `none`、`minimal`、`low`、`medium`、`high`、`xhigh`、`max`、`ultra`。一旦设置，该值将覆盖全局的 `agent.reasoning_effort` 设置以及该任务所有执行实例对应的模型级 `agent.reasoning_overrides` 设置（值为 `none` 时表示禁用推理）。可通过 `hermes cron create/edit --reasoning-effort high` 来设置该值；如需取消设置，则在编辑时传入空字符串，让系统重新遵循默认配置。（此功能刻意未在代理的 `cronjob` 工具中提供——模型配置仍由用户自行决定。）对于模型不支持的级别，提供商会在请求时将其限制或直接忽略——例如，将强度设置为 `xhigh` 的任务，若模型的最大支持强度为 `high`，则实际执行时的强度仍为 `high`。此设置对无需使用代理的任务无效（因为这类任务无需调用大语言模型）。利用该功能，您可以在不改变全局默认设置的情况下，让耗时的定时分析任务以最高强度运行，而那些成本较低的周期性任务则保持最低强度运行。
:::

:::警告
通过 Cron 运行的任务会话无法递归创建更多 Cron 任务。为防止出现失控的调度循环，Hermes 会在 Cron 执行过程中禁用相关的 Cron 管理工具。
:::

## 创建定时任务

### 通过 `/cron` 功能进行聊天

```bash
/cron add "in 30m" "Remind me to check the build"
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

### 通过自然对话方式

像平常一样询问 Hermes 即可：

```text
Every morning at 9am, check Hacker News for AI news and send me a summary on Telegram.
```

Hermes 在内部会使用统一的 `cronjob` 工具。

## 发送前的配置验证

在为定时任务构建相应的代理机制之前，调度器会先验证该任务的配置是否确实能够确保任务成功执行：

- 提供商的 API 密钥有效（如果已配置 `fallback_providers` 串，则跳过此步骤，因为备用路径可以弥补主密钥缺失的问题）；
- 所关联的技能已准备就绪（不存在任何缺失的必需环境变量、命令或凭证文件）；
- 交付平台的目标地址已知且已配置好网关凭证（`local`/`origin` 类型的目标地址不会被检查）。

如果验证失败，该任务的 `last_status` 将被设置为 `blocked_config`，系统会发送一条警报（不会每轮调度都重复发送），并且**不会发起任何 LLM 调用**——配置有误的任务不会消耗任何令牌。只有当任务下次成功执行后，阻塞状态才会解除，届时若再次出现配置问题才会触发警报。

如需禁用此验证机制并恢复旧的行为模式（即任务直接开始执行但在运行过程中失败），可按如下操作：

```yaml
cron:
  preflight: false
```

或者：`hermes config set cron.preflight false`

## 将未固定任务的调度目标更改为新的全局默认值

未固定任务的调度目标将保持在其创建时所对应的提供方/模型上，因此即便更换聊天模型，也不会影响（或中断）现有的定时任务队列。只有当您确实希望让定时任务切换调度目标时：

```bash
hermes cron edit <job_id> --provider <provider> --model <model>   # one job
hermes config set cron.model <model>                               # every unpinned job
```

使用 `hermes config set model.default …` 命令，以及桌面端的模型选择器，可以列出那些未被固定、将保留原有模型的任务，以便您能够有意识地做出选择。每当您修改任务的提供者、模型或基础 URL 时，已存储的快照都会被刷新。

## 基于技能的定时任务

定时任务在执行提示语之前，可以加载一个或多个技能。

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

技能会按顺序加载。提示语则作为附加在这些技能之上的任务指令。

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="Look for new local events and interesting nearby places, then combine them into one short brief.",
    schedule="every 6h",
    name="Local brief",
)
```

当您希望定时运行的智能体能够继承可复用的工作流，同时避免将完整的技能配置文本直接写入 Cron 脚本中时，此功能非常实用。

## 在项目目录内运行任务

默认情况下，Cron 任务会在与任何代码仓库分离的环境中运行——不会加载 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` 文件，且终端、文件处理及代码执行工具均会从网关启动时的工作目录开始运行。如需更改此设置，可通过 CLI 使用 `--workdir` 参数，或通过工具调用使用 `workdir=` 参数：

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

- 该目录下的 `AGENTS.md`、`CLAUDE.md` 以及 `.cursorrules` 文件会被注入到系统提示语中（其加载顺序与交互式 CLI 相同）；
- `terminal`、`read_file`、`write_file`、`patch`、`search_files` 和 `execute_code` 这些功能都会以该目录作为工作目录；
- 该路径必须是存在且为绝对路径——相对路径或不存在的目录在创建/更新时会被拒绝；
- 若需清除 `workdir` 并恢复旧有行为，可在编辑时传入 `--workdir ""`（或通过工具参数设置 `workdir=""`）。

:::注意：隔离性
每次运行的智能体都会将其 `workdir` 与本次运行的唯一任务标识绑定。因此，基于 `workdir` 的任务会使用常规的并行处理池，而不会改变进程全局的终端状态，也不会在多个并发运行之间泄露路径信息。如需限制 Cron 任务的总体并发数量，可设置 `cron.max_parallel_jobs`。
:::

## 编辑任务

无需通过删除并重新创建任务即可对其进行修改。

:::提示：任务引用
下方的 `<job_id>` 占位符（以及 [生命周期操作](#lifecycle-actions) 中的用法）也接受任务名称（不区分大小写）——当你记得任务名为 `morning-digest` 但记不起其十六进制 ID 时，这非常方便。精确的 ID 会优先于名称匹配；如果引用内容并非 ID，且名称与多个任务匹配，则命令会报错并列出可能的 ID，以便你进行区分。
:::

### 聊天模式

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

- 多次使用 `--skill` 可替换任务所绑定的技能列表
- `--add-skill` 会追加到现有列表中，而不会进行替换
- `--remove-skill` 可移除特定的已绑定技能
- `--clear-skills` 可移除所有已绑定的技能

## 生命周期操作

Cron 任务现在具备比单纯创建/删除更完整的生命周期管理功能。

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

功能说明：

- `pause` — 保留任务但不再安排其执行
- `resume` — 恢复任务的执行，并计算下一次运行时间
- `run` — 在下一个调度周期触发任务执行
- `remove` — 完全删除该任务
- `edit` — 修改任务的调度时间、提示信息、交付设置等

**基于名称的查找。** 现在，上述四个用于修改状态的命令（`pause`、`resume`、`run`、`remove`、`edit`）以及代理的 `cronjob` 工具都支持使用任务**名称**（不区分大小写）来替代十六进制 ID 进行操作。如果存在精确的 ID，代理和 CLI 都会优先选择该 ID；而对于名称匹配不唯一的情况（即有多个任务共享同一名称），系统会拒绝操作，并列出所有可能的 ID 供用户明确选择。由于任务名称并非唯一，这一机制至关重要——它能防止在多个任务名称相同的情况下误操作错误的任务。

### 创建已暂停的任务（安全型金丝雀任务）

无需经历“创建后再暂停”的调度竞争问题，即可创建金丝雀任务：

```bash
hermes cron create "every 1h" "Post the digest" --paused --paused-reason "Awaiting review"
hermes cron resume <job_id>
```

`--paused` 选项会在首次锁定写入时将 `enabled: false`、`state: paused`、`next_run_at: null` 以及暂停时间戳和可审计的原因信息存储起来，同时不会注册任何触发器。若省略原因字段，则存储为“已设置为暂停状态；正在等待操作员批准”。若不使用 `--paused`，则保持正常的启用状态创建。`--paused-reason` 需要与 `--paused` 一起使用；无效值会在持久化之前被拒绝。

`cron.jobs.create_job`、定时任务管理工具的 `create` 操作、网关的 `POST /api/jobs` 接口以及控制台的 `POST /api/cron/jobs` 接口都支持相同的 `paused` 布尔值和可选的 `paused_reason` 字符串。使用“恢复”功能可安排下一次运行。暂停仅能阻止自动执行，无法阻止操作员手动干预：现有的明确“立即运行”/强制运行功能依然有效，可用来恢复并执行任务。因此，该机制并不能作为防止操作员运行任务的安全屏障。

## 由代理管理的调度（管理其他定时任务的定时任务）

默认情况下，由调度器启动的代理无法使用 `cronjob` 工具——即定时任务本身不能创建、编辑或删除其他任务。如需启用此功能，可通过 `config.yaml` 进行配置：

```yaml
cron:
  allow_agent_scheduling: true   # default: false
```

启用定时代理后，它便能像处理普通聊天会话一样管理cron任务表：可在预定工作时间内安排后续单次任务、自行调整执行频率，或是运行“cron管理器”任务来统一整理整个任务表（先列出所有任务，再根据需要进行更新、删除或创建）。为确保系统稳定运行，该机制遵循以下两项原则：

- **单一的、由用户拥有的任务表。** 通过cron任务创建的任务会与其他所有任务一同存储在同一个`jobs.json`文件中，且不享有特殊的所有权——你可以像操作自己创建的任务一样，对它们进行列出、编辑或删除。
- **杜绝无效传递。** 由于cron任务的执行是临时的，因此在其内部设置的`deliver: origin`参数会在任务创建时就被解析为该任务自身的具体目标地址（即`platform:chat_id[:thread_id]`，若创建任务无需传递内容，则为目标`local`）。由定时代理创建的任务绝不会将其输出指向已不存在的会话。而明确指定的目标地址（如`local`、`all`、`telegram:<chat_id>`）将会被原样执行。

相比每次运行都创建新任务的方案，建议优先使用能够先列出现有任务再通过ID进行更新的指令。

## 工作原理

**cron任务的执行由网关守护进程负责。** 网关每60秒触发一次调度器，从而在独立的代理会话中执行所有到期的任务。

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
2. 将任务的 `next_run_at` 时间与当前时间进行比对；
3. 为每个即将到期的任务启动一个新的 `AIAgent` 会话；
4. 可选地将一个或多个附加的技能注入到该新会话中；
5. 运行提示语并直至处理完成；
6. 返回最终响应结果；
7. 更新任务运行元数据及下一次调度时间。

`~/.hermes/cron/.tick.lock` 文件用于实现锁机制，防止多个调度间隔同时重复执行同一批任务。

### 执行历史记录

在将任务分配给执行器或服务提供方之前，Hermes会先将每次尝试调度的记录保存到本地配置目录下的 `~/.hermes/cron/executions.db` 文件中。这些记录会依次经历 `claimed`、`running` 等状态，最终进入不可更改的终态之一：`completed`（已完成）、`failed`（失败）或 `unknown`（未知）。系统重启后，只有当原始进程标识符及进程启动特征能够证明该任务已不再被运行时，Hermes才会将那些被放弃的任务标记为 `unknown` 状态。这类未知记录仅作为审计日志存在，不会被自动重新执行。

可通过命令 `hermes cron runs [job-id] --limit 20`（别名：`history`）查看最近的调度尝试记录。终端历史记录有容量限制，但正在运行的任务记录不会被删除。这些历史记录也会被包含在快速备份中。

定时任务还会记录其精确的调度时间，该时间与实际执行时间是分开存储的。如果某个过时的 `jobs.json` 快照重新启动了已被保留的账本标记为已完成的任务，Hermes 会跳过此次重放操作，并重新设定该周期性任务的执行时间。即便该快照的生成时间早于任务调度时间，或是原始任务启动时间较晚，这一机制依然有效。而手动执行的单次任务则不会占用该定时任务的标识。

需要说明的是，这并不能保证“恰好执行一次”的效果：那些没有唯一标识的旧记录、已被删除的历史数据、不可用的账本以及中断的尝试都无法作为任务已完成的证明。将账本本身恢复到更早的备份版本也会导致这些证据消失。外部触发回调仅能识别当前被系统接受的存储数据，而无法反映回调中未包含的上游定时任务信息。

### 连续失败提醒功能

每个任务都会记录一个 `failure_streak` 值，表示连续失败的运行次数（交付失败不计入在内）。那些在代理程序甚至还未开始处理之前就失败的任务——比如更新操作仅部分应用后导致的错误导入，或是无法成功创建的提供方客户端——同样会被计入失败次数并触发警报，其效果与代理程序自身处理失败的情况一致。当某个*周期性*任务的失败次数达到设定阈值时，系统会向聊天界面发送包含提醒信息的失败消息，告知该任务已连续失败 N 次，并建议用户进行修复、暂停任务（使用命令 `hermes cron pause <job>`）或直接删除该任务。任何一次成功的任务执行都会重置该失败计数，而 `hermes cron list` 命令则会在显示失败任务的最近一次运行记录时一并展示该计数。一次性任务则不会触发此类提醒。

```yaml
cron:
  failure_nudge_threshold: 3   # default; 0 disables the nudge
```

### 故障事件：确认已知故障

那些持续出现且总是因*相同*错误而失败的定时任务，会在每次运行时向您发送通知。每一次故障都会被记录为一条永久性的**故障事件**，其标识由该任务名称以及错误信息的标准化签名构成，这些记录与执行历史一同存储在每个配置文件的账本数据库中。

```bash
hermes cron incidents                 # list incidents (newest activity first)
hermes cron incidents --state alerted # filter: detected | alerted | closed
hermes cron incidents ack <id>        # acknowledge — stop re-pinging
```

确认某个故障只会停止针对该特定签名模式的单次运行失败提示。除此之外其他一切都不会改变：运行历史仍会记录每一次失败，连续失败次数也会继续累加；一旦任务因*其他*错误开始失败，就会生成新的故障记录，并再次触发警报。成功的运行不会影响故障记录——因为这些记录是按签名模式而非按任务来管理的。

故障生命周期：`detected`（已记录失败）→ `alerted`（至少有一条失败提示已被发送）→ `closed`（已确认处理；该签名模式的故障终结）。存储的错误文本在写入前会进行保密处理并截断。

记录功能始终处于开启状态，选择忽略也不会产生任何费用——除非您明确执行 `ack` 命令，否则不会抑制任何提示信息。

### 集群健康检查：`hermes cron doctor`

`hermes cron doctor` 是一项针对所有正在运行任务的只读健康检查工具。它会按任务分组显示存在的问题，一旦发现需处理的问题就会以状态码 `1` 退出（正常时为状态码 `0`），因此既可用于终端操作，也可集成到监控脚本或 CI 流水线的健康检查环节中。

```bash
hermes cron doctor
```

每个正在运行的任务的检查项包括：

- 上次执行失败（`last_status`状态异常，并伴有记录的错误信息）；
- 上次交付失败（虽然已生成输出，但未能送达用户手中）；
- 缺少`next_run_at`字段，或该时间已过15分钟的容错窗口而处于过去状态——这表明“任务实际上并未被触发”（可能是调度器故障、网关关闭，或是触发请求被卡住）；
- 脚本缺失、并非文件格式，或所在路径不在`HERMES_HOME/scripts`目录下；
- 无脚本的`no_agent`类型任务；
- 配置的`workdir`目录已不存在。

Doctor工具不会修改任何任务或状态，仅负责报告信息。在深入排查被标记异常的任务时，可将其与`hermes cron incidents`（持久性故障记录）以及`hermes cron runs`（执行日志）结合使用。

## 输出选项

在调度任务时，您可以指定输出文件的存储位置：

| Option | Description | Example |
|--------|-------------|---------|
| `"origin"` | Back to where the job was created | Default on messaging platforms |
| `"local"` | Save to local files only (`~/.hermes/cron/output/`) | Default on CLI |
| `"telegram"` | Telegram home channel | Uses `TELEGRAM_HOME_CHANNEL` |
| `"telegram:123456"` | Specific Telegram chat by ID | Direct delivery |
| `"telegram:-100123:17585"` | Specific Telegram topic | `chat_id:thread_id` format |
| `"discord"` | Discord home channel | Uses `DISCORD_HOME_CHANNEL` |
| `"discord:#engineering"` | Specific Discord channel | By channel name |
| `"slack"` | Slack home channel | |
| `"whatsapp"` | WhatsApp home | |
| `"signal"` | Signal | |
| `"matrix"` | Matrix home room | |
| `"mattermost"` | Mattermost home channel | |
| `"email"` | Email | |
| `"sms"` | SMS via Twilio | |
| `"homeassistant"` | Home Assistant | |
| `"dingtalk"` | DingTalk | |
| `"feishu"` | Feishu/Lark | |
| `"wecom"` | WeCom | |
| `"weixin"` | Weixin (WeChat) | |
| `"bluebubbles"` | BlueBubbles (iMessage) | |
| `"qqbot"` | QQ Bot (Tencent QQ) | |
| `"bot-chat"` | This profile's canonical Bot Chat — the bot reads the output and responds | Machine-local |
| `"bot-chat:research"` | Another local profile's Bot Chat | Validated at create time |
| `"all"` | Fan out to every connected home channel | Resolved at fire time |
| `"telegram,discord"` | Fan out to a specific set of channels | Comma-separated list |
| `"origin,all"` | Deliver to the origin **plus** every other connected channel | Combine any tokens |

智能体的最终响应会自动发送到已配置的 `deliver:` 目标地址——智能体本身并不会主动发送消息，因此无需在 cron 命令中添加任何调用代码。

### 传输失败属于独立状态

任务的执行过程与内容传输是分开跟踪的。当智能体运行成功，但输出内容始终无法送达目标地址时（如平台返回 5xx 错误、遇到速率限制、会话失效，或适配器未检测到发送成功的信号），该任务会将状态记录为 `last_status: delivery_failed`，而绝不会显示为普通的 `ok`，同时会在 `last_delivery_error` 中注明失败原因。使用 `hermes cron list` 查看时，这类任务会以黄色标记显示为 `delivery_failed: <reason>`；`hermes cron doctor` 会将其判定为传输问题；而手动执行 `cronjob run` 时则会出现 `success: false` 及相应的传输错误信息。传输失败不会计入任务的 `failure_streak`（因为智能体已完成其工作）；下一次完全成功的运行会将状态恢复为 `ok`。

### 机器人聊天传输（`bot-chat`）

`bot-chat` 会将输出内容**作为真实消息发送到对应账号的标准化“机器人聊天”会话中**。与其他所有目标地址不同——那些地址的接收者都是阅读频道内容的人类——这里的接收者是机器人本身：它会将收到的内容视为新消息，对需要处理的内容采取相应操作，然后在自己的聊天界面中予以回复。当需要对定时生成的输出进行*处理*而非简单发布时，可使用此功能。

- `bot-chat`（仅此形式）的目标地址为该任务所属的账号个人主页。
- `bot-chat:<profile>` 用于定位**同一台机器上的另一个配置文件**。在创建任务时，系统会通过 `hermes profile list` 对名称进行验证；因此无法定位其他网关或机器上的配置文件，这也确保了不同机器上同名配置文件的唯一性。
- 每次消息投递都会占用目标机器上一个完整的 Agent 工作周期——请注意调度频率。
- 该功能可与其他投递目标（如 `bot-chat`、`telegram`）结合使用，但绝不会被包含在 `all` 选项中。
- 若标准聊天窗口是在具备邮件箱功能的桌面端/命令行界面后端中打开的，那么无论机器人当前是空闲还是忙碌，消息都会**立即被持久化地加入队列**。只有当前正在使用的机器人会处理该消息；Cron 不会启动其他竞争性的 CLI 写入进程。如果没有正在使用的邮件箱所有者，原有的 `hermes chat -c "Bot Chat" --create-if-missing` 通道仍会保持可用状态（仍需遵循常规的会话所有者检测规则）。
- **“已入队”并不等同于“已完成”**。Cron 会在 `last_delivery_queued` 中记录接收 ID 以及 `queued`/`claimed` 状态，此时投递结果为 `queued`（既未成功投递也未失败）。任务执行成功时会显示为 `delivery_queued`；而在其他目标上出现的真正错误仍会被视为投递失败。机器人可能会在稍后完成处理。目标配置文件中的 `runtime/bot_live_delivery/<receipt-id>.json` 文件所保存的持久化接收记录才是权威依据；Cron 中的历史状态不会自动更新。
- 重新检查同一次执行时会查看其现有的接收记录，即便任务负责人已离场也不例外。任务一旦被确认处理，就绝不会回退到其他处理者手中。状态为`failed`、`cancelled`或`ambiguous`的接收记录不会自动重试；在有意开始新任务之前，请先查看聊天记录和接收记录。每次新的定时执行都会生成唯一的交付ID。

### 路由意图（`all`）

使用`all`选项可将一个定时任务发送到您配置的所有消息渠道，而无需逐一指定名称。该选项会在任务触发时进行解析，因此，在您设置`TELEGRAM_HOME_CHANNEL`之前创建的任务，会在设置完成后的下一次调度中开始向Telegram发送消息。

语义说明：`all`会扩展为所有已配置了主渠道的平台。设置为0也是可行的；此时任务不会产生任何交付目标，并会在上游被记录为交付失败。

`all`可与明确指定的目标一起使用。`origin,all`选项会将消息发送到原始聊天窗口以及所有其他已连接的主渠道，同时通过`(platform, chat_id, thread_id)`进行去重处理。

### Telegram定时任务主题（`TELEGRAM_CRON_THREAD_ID`）

当启用Telegram主题模式后，根私信对话将被保留为系统大厅——发送到该处的回复会收到大厅提醒并被拒绝，且`reply_to_message_id`也会被丢弃，因此您无法回复那些进入主聊天窗口的定时任务消息。

建议将定时任务指向专用的论坛主题：

1. 在 Telegram 中打开该机器人的私信窗口，创建一个主题，例如命名为 `Cron`。长按该主题标题 → 选择**复制链接**；链接末尾的数字即为该主题的 `message_thread_id`。
2. 在您的 `.env` 文件中设置 `TELEGRAM_CRON_THREAD_ID=<对应编号>`。

此设置仅适用于定时任务推送。用于其他场景（如重启通知）的 `TELEGRAM_HOME_CHANNEL_THREAD_ID` 值保持不变。若明确指定 `deliver="telegram:chat_id:thread_id"` 的目标地址，仍将优先于环境变量设置。现在，定时任务的回复会直接发送到现有的主题对话中，您可以立即对其进行处理。

### 响应内容封装

默认情况下，定时任务推送的输出内容会带有页眉和页脚，以便接收方知晓该内容来自定时任务：

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

### 推送通知（`cron.delivery.notify`）

Cron 输出属于*最终*的发送结果，而非进度信息，因此默认情况下会带有平台的通知标志一同发送——在 Telegram 中，这意味着即便适配器的通知模式设置为 `important`，简短消息仍会触发推送（否则会在 `disable_notification=true` 的情况下发送，而用户会将这类静默的简短消息报告为“从未送达”）。如需恢复静默发送功能：

```yaml
# ~/.hermes/config.yaml
cron:
  delivery:
    notify: false   # default: true
```

该标志会同时应用于文本发送及任何媒体附件，因此每次执行任务时既不会强制发送其中一项，也不会忽略另一项。

### 交付确认与 `UNVERIFIED` 状态

只有当适配器提供明确的有效证据时，实时适配器的交付才会被标记为已送达：即非过滤掉的任务的显式 `success` 状态（`delivered: false`），以及 `message_id` 或 `raw_response`。即便结果显示为 `success`，但缺少 Slack、Matrix 和 Mattermost 适配器所返回的上述任意一项证据，系统仍会接受该结果（因为这并不代表失败），但该任务会在作业记录中标记为 `last_delivery_unverified`，并会在 `hermes cron list` 中显示出来：

```
⚠ Delivery UNVERIFIED: adapter acked slack:C0123456 without message_id/raw_response
```

在 `hermes cron doctor` 中会显示为“上次交付状态未验证（...）”。一旦有后续成功交付且附带相关证据，该标记就会被清除。空内容（既无文本也无媒体文件）永远不会被传递给适配器；此类交付会直接失败，并以 `last_delivery_error` 的形式进行报告，而不会被标记为已交付。

### 可续接的任务（对定时交付内容回复）

默认情况下，定时交付属于“发送即忘”模式：消息虽已发送，但不会保留在聊天的历史记录中，因此如果您对其回复，智能体将无法记住它之前说过什么。若将任务设置为**可续接**模式，那么已交付的摘要内容就会变成一段可以回复的对话——智能体能直接获取上下文中的信息，而无需再询问“第二项任务是什么？”。

此功能为可选选项，默认处于关闭状态。您可以在全局配置中启用它，也可以通过 `cronjob` 工具的 `attach_to_session` 选项为单个任务单独启用（该选项会覆盖该任务的全局设置）：

```yaml
# ~/.hermes/config.yaml
cron:
  mirror_delivery: false   # set true to make cron deliveries continuable
```

其行为优先在**线程内进行**，且仅限于该任务自身的对话场景：

- **支持线程的平台**（Telegram主题、Discord/Slack线程）：每次消息发送都会开启一个独立的专用线程，任务指令会被注入到该线程的会话中，因此在此线程内的回复能够保留完整上下文。对于周期性任务（例如每日任务），每次执行都会开启一个新的线程，从而确保每次消息的后续讨论彼此独立。
- **仅支持私信的平台**（WhatsApp、Signal、短信）：由于不存在线程，任务指令会被同步到原始私信会话中——私信本身即为对话延续的载体。

系统仅会操作该任务**自身的对话**，具体包括：
- 创建该任务的**原始聊天窗口**；
- 当`deliver: origin`未能定位到原始对话时所使用的**主频道备用选项**（这类任务是由脚本或API创建的，而非通过实时聊天入口创建的），即以用户的主要对话作为原始对话的替代；
- 任务中明确指定的**`platform:chat`目标**，但前提是该任务本身设置了`attach_to_session: true`选项——即任务创建者明确将该目标定义为某个对话。仅靠全局的`mirror_delivery`标志，是无法让明确指定的聊天窗口支持对话延续的。

广播型/扩散型目标（如`all`或平台主频道）则永远无法实现对话延续功能。系统会将镜像内容以带标签的用户消息形式呈现（例如`[Cron delivery: <task name>]`），从而确保在所有模型提供方之间都能安全地切换对话历史。

#### 单一频道内的直接延续（Slack）

上述基于线程的默认行为会在每次消息发送时创建一个独立的线程。如果您希望可续传的任务直接**显示在频道时间轴上**，而不生成额外线程，可将 Slack 的**可续传处理方式**设置为 `in_channel`：

```yaml
# ~/.hermes/config.yaml
slack:
  cron_continuable_surface: in_channel   # default: thread
  reply_in_thread: false                 # required pairing (see below)
  require_mention: false                 # so a plain reply continues the job
```

在“in_channel”模式下，任务指令会以普通的主题频道消息形式发送（不会创建新线程），而您的回复则通过该频道的共享会话来继续处理任务。这三个设置共同决定了消息的传递方式：

- **`cron_continuable_surface: in_channel`** —— 在发送指令时跳过创建线程的步骤。
- **`reply_in_thread: false`**（为必填项）—— 使机器人以“扁平化”方式在频道中直接回复您的内容，并将其绑定到初始任务指令所在的同一整个频道会话中。若未设置此选项，虽然仍可继续处理任务，但回复会出现在新线程中（系统会安全地回退到线程式回复方式，绝不会丢失回复——网关会在启动时记录警告，以便您发现这种不一致情况）。
- **`require_mention: false`**（或将该频道添加到 `free_response_channels` 中）—— 这样您就可以直接发送普通消息进行回复；否则，机器人只有在每次回复时被您 `@` 提及时才会响应。

由于回复是基于**整个频道**的会话进行的，因此信息是共享的：频道中的其他用户以及另一个可继续处理的“in_channel”任务，都可以参与同一场持续对话。这正是“扁平化频道回复”模式所固有的特性，也是用户选择 `reply_in_thread: false` 时已经接受的权衡；如果您希望每次任务的后续处理都相互独立，则应使用默认的“线程”模式。

目前，这是 Slack 才具备的功能。其他平台虽然也能识别该键值，但会回退到“线程”界面（因为它们的消息延续机制各不相同）；具体选择需根据各个平台而定，并在对应平台的配置中设置。这是一个位于网关端的配置标志——通过执行 `/restart` 命令即可启用该功能，无需重新安装 Slack 应用。

:::注意：1 对 1 私信
`cron_continuable_surface` 是一个**频道**级别的设置——由于 1 对 1 私信本身就没有线程与时间线两种形式的区分（其结构本就是扁平的），因此该键值在私信中不起作用。决定私信中的定时任务是否可延续的，是另一个独立的预设选项 **`slack.dm_top_level_threads_as_sessions`**：

- **`false`** —— 所有顶层私信共享同一个滚动式私信会话，因此可延续的定时消息及用户的回复都会出现在**同一个**会话中，任务也能在原有上下文中继续执行。这正是希望在私信中使用可延续定时任务时的理想设置。
- **`true`**（默认值）—— 每条顶层私信消息都对应一个独立的会话，因此对已发送的定时消息的回复会启动一个全新的会话，而该新会话中不会保留原有消息的记录。在这种模式下，无论是定时任务还是其他形式的扁平式消息传递，都无法实现内容延续。

因此，若要将可延续的定时任务发送到 1 对 1 私信，需将 `slack.dm_top_level_threads_as_sessions` 设置为 `false`。对于私信而言，`cron_continuable_surface` 并非必需项（也会被忽略）。
:::

### 沉默抑制功能

如果智能体的最终回复中包含 `[SILENT]` 字符，消息将完全被抑制不发送。虽然相关输出仍会保存在本地以便审计（位于 `~/.hermes/cron/output/` 目录下），但不会向目标地址发送任何消息。

这对于监控那些仅在出现故障时才需要报告状态的作业来说非常有用：

```text
Check if nginx is running. If everything is healthy, respond with only [SILENT].
Otherwise, report the issue.
```

无论是否存在 `[SILENT]` 标记，失败的任务始终会生成报告——只有运行成功的任务才能被设置为静默模式。对于需要安静监控的任务，可在没有需要报告的内容时，指示代理仅回复 `[SILENT]`。

## 脚本超时时间

通过 `script` 参数传入的预运行脚本默认超时时间为 3600 秒（1 小时）。此限制仅适用于脚本本身——基于技能或大型语言模型的任务拥有独立的不活跃时间预算，不受该数值的限制。如果您的脚本需要不同的超时时间，可对其进行修改：

```yaml
# ~/.hermes/config.yaml
cron:
  script_timeout_seconds: 1800   # 30 minutes
```

或者可以设置 `HERMES_CRON_SCRIPT_TIMEOUT` 环境变量。其优先级顺序为：环境变量 → config.yaml 文件中的配置 → 默认的 3600 秒。

Cron 机制还会对任务执行后的会话以及代理资源进行清理操作。这些清理工作会在大语言模型完成一轮响应之后进行，因此与无活动超时机制是分开的。每次清理操作的默认时间为 10 秒。如果存储处理模块或客户端终结器不再返回响应，调度器会记录错误，解除对该任务的正在处理锁定，从而允许后续任务被调度执行，而不会永久跳过该任务。

```yaml
# ~/.hermes/config.yaml
cron:
  cleanup_timeout_seconds: 10
```

仅将 `cleanup_timeout_seconds: 0` 设置为该值，方可恢复旧版的无限时长清理机制。

## 媒体文件发送超时

当通过实时网关适配器发送包含媒体附件的定时任务内容（如生成的 PDF、TTS 音频或导出的报告）时，每次附件上传都会受到超时限制——默认值为 300 秒。对于通过带宽较低的上传链路传输的大文件，可能需要更长的时间：

```yaml
# ~/.hermes/config.yaml
cron:
  media_send_timeout_seconds: 600   # 10 minutes per attachment
```

或者可以设置 `HERMES_CRON_MEDIA_SEND_TIMEOUT` 环境变量。其优先级顺序为：环境变量 → config.yaml 文件设置 → 默认 300 秒。若发送附件超时，该任务的状态将被记录为部分投递失败（不过文本内容仍可正常送达）。

## Bot Chat 投递超时时间

`bot-chat` 投递方式会在目标机器人的聊天界面中完整执行一次智能体对话，因此其超时时间以分钟为单位，而非秒——默认值为 600 秒：

```yaml
# ~/.hermes/config.yaml
cron:
  bot_chat_delivery_timeout_seconds: 900
```

超时交付的情况会记录在 `last_delivery_error` 中；此时机器人仍有可能自行完成当前任务。

## 无智能体模式（仅脚本任务）

对于那些无需大语言模型进行推理的周期性任务——例如传统的看门狗监控、磁盘/内存警报、心跳检测以及 CI 系统的 ping 检测——在创建任务时请设置 `no_agent=True`。调度器会按预定时间运行您的脚本，并直接输出其标准输出结果，从而完全跳过智能体环节：

```bash
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"
```

语义规则：

- 脚本的标准输出（已去除首尾空白）→ 将其原样作为消息发送。
- **标准输出为空 → 无声标记**，不发送任何内容。这采用了“看门狗”模式：“仅在出现异常时才发出通知”。
- 进程退出码非零或超时 → 会发送错误警报，因此故障的看门狗机制不会导致静默失败。
- 最后一行包含 `{"wakeAgent": false}` → 同样为无声标记（与大型语言模型任务使用的规则相同）。
- 无需令牌、模型或提供者回退机制——该任务根本不会触及推理层。

`.sh` / `.bash` 文件会在系统 `PATH` 中可找到 `bash` 时由该命令执行，否则则使用 `/bin/bash`（在 Windows 的 Git Bash 环境中这一点尤为重要）。其他类型的脚本则由当前的 Python 解释器（`sys.executable`）来执行。脚本必须位于 `$HERMES_HOME/scripts/` 目录内——只要解析后的目标路径仍在该目录中，相对路径、绝对路径以及以 `~` 开头的路径都是允许的；超出该目录范围的路径将被拒绝。子进程环境会被进行安全处理（通过 `_sanitize_subprocess_env` 函数），因此提供者 API 密钥及其他由 Hermes 管理的敏感信息**不会**被 cron 脚本继承。

### 代理会为您完成这些配置

`cronjob` 工具的架构允许直接向 Hermes 提供 `no_agent` 参数，因此您只需在聊天中描述看门狗机制，代理便会自动为其完成相关配置：

```text
Ping me on Telegram if RAM is over 85%, every 5 minutes.
```

Hermes 会通过 `write_file` 函数将检查脚本写入 `~/.hermes/scripts/` 目录，随后调用相应函数：

```python
cronjob(action="create", schedule="every 5m",
        script="memory-watchdog.sh", no_agent=True,
        deliver="telegram", name="memory-watchdog")
```

当任务内容完全由脚本决定时（如监控告警、阈值警报、心跳检测等），该工具会自动设置 `no_agent=True`。此外，该工具还支持让代理暂停、恢复、编辑及删除任务——因此整个任务生命周期都由聊天界面驱动，无需任何人操作命令行界面。

如需实际示例，请参阅[仅脚本版定时任务指南](/guides/cron-script-only)。

## 使用 `context_from` 连接多个任务

定时任务在独立的会话中运行，不会保留之前运行的任何记录。但有时，一个任务的输出恰好是下一个任务所需要的输入。`context_from` 参数可自动建立这种关联——在运行时，任务 B 的提示语前会自动添加任务 A 的最新输出作为上下文。

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

- 当作业 2 被触发时，Hermes 会从 `~/.hermes/cron/output/{job1_id}/*.md` 中读取作业 1 的最新输出内容。
- 该输出内容会自动添加到作业 2 的提示语开头。
- 作业 2 无需硬编码“读取此文件”的指令——它可直接将相关内容作为上下文获取。
- 任务链的长度可任意延伸：作业 1 → 作业 2 → 作业 3 → ……

**`context_from` 的支持格式：**

| 格式 | 示例 |
|------|------|
| 单个作业 ID（字符串） | `context_from="a1b2c3d4"` |
| 多个作业 ID（列表） | `context_from=["job_a", "job_b"]` |

输出内容将按照列出的顺序依次拼接。

**保持连续性：继承上一次运行的输出**

设置 `continuity=true` 后，作业会在每次运行时自动注入其*自身*的最新输出。常规的周期性作业通常会在每次启动时“遗忘”之前的记录——比如新闻采集机器人会重复报道相同的内容，监控系统也会对同样的状况反复发出警报。而开启连续性功能后，作业在启动时会保留上一次的记录，从而避免重复处理并能够从上次中断的地方继续工作：

```python
cronjob(
    action="create",
    prompt="Scan HN and arXiv for new agent-tooling papers. Report only items NOT already covered in your previous run's output.",
    schedule="every 6h",
    continuity=True,
    name="Agent Tooling Scout",
)
```

在首次运行时，由于没有历史输出，指令会原样执行。在选择上下文时，系统会跳过静默监控状态（标记为“无变化”）、空输出以及`wakeAgent=false`的审计记录，从而保留最新的有效输出。审计文件仍会保存在磁盘上。错误日志依然可以作为下一次运行的恢复依据；这并非仅保留成功记录的历史过滤机制。在后续运行中，系统会在原有输出前添加连续性说明（旨在“避免重复已报告的内容”）。该功能可与其他上游任务自由结合使用（通过`context_from=["<其他任务ID>"]`并设置`continuity=true`）；若在更新时将`continuity`设置为`false`，则该功能会被关闭，但其他`context_from`条目仍会保留。在内部实现上，该标志以`context_from`中的专用`self`条目形式存储。

通过命令行操作：可使用`hermes cron create "每6小时" "搜索新闻" --continuity`来创建任务，或使用`hermes cron edit <任务ID> --continuity`/`--no-continuity`来切换现有任务的该功能开关。控制面板中的定时任务编辑器及桌面端机器人模式对话框也提供相同的切换功能。

**适用场景：**
- 多阶段处理流程（收集 → 过滤 → 格式化 → 传递）
- 各步骤的输出相互依赖的任务
- 一个任务需要汇总多个其他任务结果的扩展/聚合结构
- 需要基于自身历史报告进行去重处理的周期性扫描/监控任务（此时应设置`continuity=true`）

## 提供商恢复功能

定时任务会继承您所配置的备用服务提供商以及凭证池轮换机制。当主 API 密钥遇到速率限制或对应服务提供商返回错误时，定时任务代理可以：

- 如果您在 `config.yaml` 中配置了 `fallback_providers`（或旧版的 `fallback_model`），则可**切换到备用的服务提供商**；
- 对于同一服务提供商，可**切换到凭证池**（/user-guide/configuration#credential-pool-strategies）中的下一个凭证。

这意味着在高频率运行或业务高峰时段执行的定时任务具备更强的容错能力——单个出现速率限制的密钥不会导致整个任务执行失败。

## 运行失败（`last_error`）

任务执行失败时，系统会记录简明的 `last_error` 信息，该信息会显示在任务列表及 `/cron list` 中，其中凭证模式和 URL 凭证已被遮蔽（包括之前存储的错误记录）。此字段与用于调度任务交接的 `last_fire_error`，以及用于处理交付任务的 `last_delivery_error` 是相互独立的；当任务本身执行失败时，这些字段也可能为空。

若遇到连接故障，请查看当前 Hermes 主页中 `cron/output/<job_id>/` 目录下的任务运行记录。其中的 `## Error` 部分会显示链式堆栈跟踪信息，但凭证模式和 URL 凭证同样会被遮蔽。该文件遵循现有的私有输出文件权限设置；堆栈跟踪中的局部变量信息不会被保存。交付通知和 `last_error` 字段仅显示简明的错误信息，而非完整的堆栈跟踪。在分享相关内容之前，请先仔细查看诊断信息——即便信息已被遮蔽，也不能保证其中的应用程序数据就一定不属于敏感信息。

## 定时任务执行失败 (`last_fire_error`)  

在托管式（managed-cron）部署环境中，定时任务的执行流程是从平台调度器开始，经控制面板传递至网关的内部 API 服务器。如果这一最终环节出现故障——例如网关进程崩溃，或其 API 服务器的监听端口从未启动——任务将根本无法开始执行，因此既没有执行记录，也无法查看 `last_status` 状态。此类问题的典型表现为：手动触发任务时总能正常运行，但自动定时执行却始终失败。  

这类失败会以 `last_fire_error` 的形式标记在任务记录中（包含时间戳及失败原因），可通过以下方式查看：  
- `cronjob` 工具 → `action: "list"`，即可看到 `last_fire_error` 字段；  
- `hermes cron list` 命令，任务下方会显示红色的 `⚠ 定时任务执行失败:` 提示行；  
- 控制面板中的任务视图。  

该标记始终反映当前自动执行的健康状况：新的失败记录会覆盖旧数据，而一旦下次任务成功执行，该标记便会自动清除。若看到此标记，说明任务本身及其调度设置并无问题——问题出在任务执行路径的网关端（最常见的解决方法是通过进程管理工具重启网关，使其加载完整的配置环境：`hermes gateway restart`）。  

### 失败任务的补执

当外部调度器提供商处于激活状态时（即托管部署中的定时任务管理功能），网关还会执行一次补跑扫描：对于那些预定执行时间已过却仍未被触发，且宽限期也已结束的任务，系统会将其接管并在本地执行。这样一来，任务传递过程中的故障所造成的中断时间将从一整天缩短至几分钟而已。该扫描过程会利用与正常任务处理相同的机制来避免重复处理因调度器重试而产生的类似任务。

```yaml
cron:
  misfire_grace_minutes: 10   # wait this long for the scheduler's own retries
                              # before catching up locally; 0 disables catch-up
```

本地（内置行情源）部署无需此功能——该行情源会在下一次数据更新时自动检测到已超时的任务。

## 计划格式

代理的最终响应会自动发送至任务的 `deliver:` 目标地址——代理不再自行发送消息，因此面向用户的内容会直接包含在最终响应中。若需发送至**其他或不同的**目标地址，应在定时任务中列出多个 `deliver:` 目标（用逗号分隔，例如 `deliver: "telegram,discord"`），而非让代理分别发送。

### 相对延迟（单次执行）

```text
in 30m  → Run once in 30 minutes
in 2h   → Run once in 2 hours
in 1d   → Run once in 1 day
```

### 间隔时间（周期性任务）

```text
30m          → Every 30 minutes (bare durations are recurring)
every 30m    → Every 30 minutes
every 2h     → Every 2 hours
every 1d     → Every day
every hour   → Every hour (bare unit = 1)
```

### 自然日/时间调度（周期性任务）

```text
every monday 9am         → Weekly, Mondays at 9:00 AM
every day at 9am         → Daily at 9:00 AM
weekdays at 9am          → Weekdays at 9:00 AM
weekends at 10am         → Saturdays and Sundays at 10:00 AM
daily at 7am             → Daily at 7:00 AM
monday, wednesday at 9am → Mondays and Wednesdays at 9:00 AM
```

Times 支持 `9am`、`9:30pm`、`14:00`、纯24小时制时间格式（如 `at 7`）、`noon` 以及 `midnight`。这些时间格式会在内部转换为 cron 表达式（为此需要 `croniter` 包，该包已默认安装）。

### Cron 表达式

```text
0 9 * * *       → Daily at 9:00 AM
0 9 * * 1-5     → Weekdays at 9:00 AM
0 9 * * MON-FRI → Weekdays at 9:00 AM (named weekdays/months accepted)
0 */6 * * *     → Every 6 hours
30 8 1 * *      → First of every month at 8:30 AM
0 0 * * 0       → Every Sunday at midnight
```

### ISO时间戳

```text
2026-03-15T09:00:00    → One-time at March 15, 2026 9:00 AM
```

## 重复执行行为

| 计划类型 | 默认重复间隔 | 行为表现 |
|--------------|----------------|----------|
| 单次执行（`in 30m`、时间戳） | 1 | 仅运行一次 |
| 定期执行（`every 2h`） | 永久 | 直到被移除前持续运行 |
| Cron表达式 | 永久 | 直到被移除前持续运行 |

您可自行覆盖该设置：

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

对于 `update` 操作，若要移除所有已绑定的技能，请传入 `skills=[]`。

### 手动运行为异步模式

`cronjob(action="run")` 会立即在**后台**启动任务（与 `delegate_task` 的机制类似）：工具调用会立即返回一个处理标识，而任务的执行结果——包括成功/失败状态、交付目标、下一次预定运行时间以及部分输出内容——则会在任务完成后以新消息的形式再次出现在对话中。在此期间，智能体（以及您）可继续执行其他操作；对于正在运行的任务，系统会以“已在运行”为由拒绝重复启动。

此外，您还可以在 `action="run"` 时传入 `prompt` 参数，以便为每次运行注入临时的上下文信息：

```python
cronjob(action="run", job_id="...", prompt="CONTEXT: focus on the EU region today")
```

该上下文会以 `## Run Context` 为标题附加到该单次任务的存储提示中——它不会被永久保存到任务定义中，且需经过与存储提示相同的提示注入扫描。

那些无法接收分离结果的环境（如单次执行的 `hermes -z` 命令、通过 CLI 执行的 `hermes cron run`、cron 子进程以及 Kanban 工作节点）会自动切换为同步执行模式。

## cron 任务可使用的工具集

Cron 会在一个不关联任何聊天平台的全新代理会话中运行每个任务。默认情况下，该 cron 代理会使用你在 `hermes tools` 中为 `cron` 平台配置的工具集——而非 CLI 的默认设置，也不是所有可用的工具。

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

当任务中设置了`enabled_toolsets`时，该设置将起决定性作用；否则，则以`hermes tools`的cron-platform配置为准；若仍无对应配置，Hermes则会回退到内置的默认设置。这一点对于成本控制至关重要：在每一个简单的“获取新闻”任务中都启用`browser`、`delegation`等功能，会使得每次调用LLM时产生的工具结构提示信息变得冗长。

### 完全跳过智能体：使用`wakeAgent`

如果您的cron作业通过`script=`参数指定了预检查脚本，该脚本可以在运行时决定是否需要调用Hermes智能体。只需在脚本中输出一行符合特定格式的最终标准输出即可：

```text
{"wakeAgent": false}
```

……此时，Cron会完全跳过该次刻度下的智能体运行任务。这一功能非常适合那些需要频繁轮询（每1至5分钟一次）的场景，且仅需在状态真正发生变化时才唤醒大型语言模型——否则就会不断为毫无实际输出内容的智能体运行支付费用。

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

#### 方案：低成本的任务预运行判定机制

`wakeAgent` 判定机制提供了一种无需花费任何成本的方案，用于决定某个定时任务是否需要消耗 LLM 令牌。三种常见模式可覆盖大多数使用场景。

**文件变更判定模式**——仅当被监控的文件自上次成功执行后内容发生变动时才启动任务。调度器会记录每个任务的 `last_run_at` 时间，并将其与文件的修改时间（mtime）进行比对。

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

**外部标志门控**——仅在其他进程发出就绪信号时才会启动（例如部署钩子上传了文件，或 CI 任务在状态存储中设置了相应值）。

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

**SQL计数门限**——仅当您的数据库中有新行需要处理时才会启动。该脚本还可以通过`context`将计数信息传递给代理，这样代理无需再次查询即可知晓需要处理的行数。

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
Hermes 自带的 `~/.hermes/state.db` 是一种内部架构，不同版本之间可能会有所变化。请勿通过预运行关卡来查询该数据库，而应直接连接您自己的数据库或使用其他数据源。
:::

致谢：这套方案源于 @iankar8 在 [#2654](https://github.com/NousResearch/hermes-agent/pull/2654) 中提出的探索，他建议引入 sql/file/command 触发器作为另一种并行机制。由于 `script` + `wakeAgent` 关卡已经能以零成本覆盖这三种场景，因此相关改进仅以文档形式呈现。

### 任务链式调用：`context_from`

Cron 作业可以通过在 `context_from` 中列出一个或多个其他作业的名称（或 ID），来获取这些作业最近一次成功的输出结果：

```text
cronjob(action="create", name="daily-digest",
        schedule="every day 7am",
        context_from=["ai-news-fetch", "github-prs-fetch"],
        prompt="Write the daily digest using the outputs above.")
```

本次运行时，所引用任务的最最新完成输出会被作为上下文注入到提示语上方。每一个上游条目都必须是有效的任务 ID 或名称（参见 `cronjob action="list"`）。注意：chain 指令会读取*最最新已完成*的输出——它不会等待同一时间间隔内仍在运行的上游任务。

## 任务存储

任务存储在 `~/.hermes/cron/jobs.json` 文件中。任务运行产生的输出则会被保存到 `~/.hermes/cron/output/{job_id}/{timestamp}.md` 路径下。

任务定义以纯 JSON 格式存储在磁盘中，因此能够经受住 `hermes update`、网关重启以及机器重启等操作。如果在重启过程中任务正处于运行状态，其在执行记录中的状态会被标记为 `unknown`——系统不会自动重新尝试执行该任务，但该任务的下一预定执行时间仍会正常触发。详情请参阅 [执行历史](#execution-history)。

:::tip
建议通过 `cronjob` 工具、`hermes cron edit` 或 `/cron` 命令让智能体来管理任务，而非直接修改 `jobs.json` 文件。当[文件写入安全机制](../security.md#file-write-safety)阻止了写入操作时（例如设置了 `HERMES_WRITE_SAFE_ROOT` 变量），直接编辑可能会在无声无息中失败；而[文件变更验证器](../configuration.md#file-mutation-verifier)会给出明确提示，告知没有任何内容被保存。
:::

任务中的 `model` 和 `provider` 字段可以设置为 `null`。如果省略了这些字段，Hermes 会在执行时从全局配置中自动获取对应值。只有当为特定任务设置了自定义值时，这些字段才会出现在任务记录中。

该存储机制采用原子级文件写入方式，因此即便写入过程被中断，也不会留下未完成的部分作业文件。

## 独立生成的提示语依然至关重要

:::warning 重要提示
定时任务会在一个全新的智能体会话中执行。因此，提示语中必须包含智能体所需的所有信息，尤其是那些无法通过已加载的技能获取的内容。
:::

**错误示例：** `"检查一下那台服务器的问题"`

**正确示例：** `"以用户 'deploy' 身份通过 SSH 登录到服务器 192.168.1.100，使用 'systemctl status nginx' 命令查看 nginx 是否正在运行，并确认 https://example.com 能返回 HTTP 200 状态码。"`

## 安全性

在创建或更新定时任务时，系统会对其提示语进行扫描，以检测注入攻击和凭证窃取的迹象。任何包含隐形 Unicode 欺骗手段、SSH 后门尝试或明显用于窃取机密信息的代码片段都会被阻止。
