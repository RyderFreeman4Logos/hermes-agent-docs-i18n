---
sidebar_position: 12
title: "Kanban (Multi-Agent Board)"
description: "Durable SQLite-backed task board for coordinating multiple Hermes profiles"
---

# 看板模式 —— 多智能体任务协作

> **需要逐步指导？**请阅读[看板教程](./kanban-tutorial)——其中包含四个用户案例（单人开发、批量处理、带重试机制的流程管理、断路器机制），并附有每个案例的仪表板截图。本页面为参考资料，而教程则提供了完整的讲解流程。

Hermes 看板模式是一种持久化的任务看板，可在所有 Hermes 配置文件之间共享，支持多个命名智能体协同处理任务，且无需依赖脆弱的临时子智能体集群。每个任务在 `~/.hermes/kanban.db` 中对应一行记录；每次任务交接都会生成一行可供任何人读写的内容；每个处理任务的工作进程都是拥有独立身份的完整操作系统进程。

### 两种交互方式：模型通过工具操作，用户通过 CLI 操作

该看板提供两个入口，二者都基于同一个 `~/.hermes/kanban.db` 数据库：

- **智能体通过专用的 `kanban_*` 工具集来操作看板**——包括 `kanban_show`、`kanban_list`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`、`kanban_unblock` 等命令。调度器在为每个工作进程创建时，会预先为其加载这些工具；编排型配置文件也可显式启用 `kanban` 工具集。模型通过直接调用这些工具来读取和分配任务，而非通过执行 `hermes kanban` 命令来实现。详情请参见下文的[工作进程如何与看板交互](#how-workers-interact-with-the-board)。
- **您（以及脚本、cron 任务）可通过 CLI 中的 `hermes kanban …` 命令、斜杠命令 `/kanban …`，或通过仪表板来操作看板**。这些方式面向人类用户和自动化脚本——它们背后没有工具调用模型。

两种交互方式都通过同一个 `kanban_db` 层进行数据传输，因此读取操作能获得一致的结果，写入操作也不会出现数据偏差。本页面其余部分提供了 CLI 示例，因为它们便于复制粘贴，但实际上每个 CLI 命令都对应着模型所使用的工具调用方式。

以下场景适用于 `delegate_task` 功能无法处理的工作负载：

- **研究分类工作**——需要并行开展研究的智能体、分析人员与撰写人员，且需人工介入决策。
- **定时任务操作**——每日重复执行的任务，需逐步形成数周以来的工作记录。
- **数字孪生助手**——具有持久身份的命名助手（如 `inbox-triage`、`ops-review`），能够随时间积累工作记忆。
- **工程开发流程**——分解任务 → 在并行工作树中实施 → 审核 → 迭代 → 提交 Pull Request。
- **批量任务管理**——一名专家同时管理多个对象（如50个社交账号、12个需要监控的服务）。

关于完整的设计理念、与 Cline Kanban / Paperclip / NanoClaw / Google Gemini Enterprise 的对比分析，以及八种典型的协作模式，可查阅仓库中的 `docs/hermes-kanban-v1-spec.pdf` 文件。

## 看板模式 vs. `delegate_task` 函数

二者外观相似，但本质并非同一类功能。

| 对比项 | `delegate_task` | 看板模式 |
|---|---|---|
| 形态 | RPC 调用（分叉 → 合并） | 持久消息队列 + 状态机 |
| 父进程行为 | 需要子进程返回后才能继续执行 | 执行 `create` 后即“发完即忘”，无需等待结果 |
| 子进程身份 | 匿名临时智能体 | 具有持久内存的命名配置文件 |
| 可恢复性 | 无——失败即终止 | 可通过“阻塞 → 解锁 → 重新运行”或“崩溃后回收资源”实现恢复 |
| 是否支持人工介入 | 不支持 | 可随时添加评论或解锁任务 |
| 每个任务对应的智能体数量 | 一次调用对应一个临时智能体 | 任务生命周期内可涉及多个智能体（负责重试、审核、跟进等） |
| 审计追踪 | 在上下文压缩后会被丢失 | 数据以持久化行形式存储在 SQLite 中，永不消失 |
| 协调方式 | 层级式（调用方 → 被调用方） | 对等式——任何配置文件均可读取/修改任意任务 |

**一句话区分：** `delegate_task` 是函数调用；而看板模式是一个工作队列，每次任务交接都会生成一行记录，任何配置文件或人类用户均可查看和编辑。

**何时使用 `delegate_task`：** 当父智能体在继续执行前需要一个简短的推理结果，且无需人工参与，结果会直接返回到父智能体的上下文中时。

**何时使用看板模式：** 当任务需要跨智能体协作、需在进程重启后仍能保留状态、可能需要人工输入、可能由其他角色接手处理，或需要在事后能够被查找时。

二者可以共存：一个看板模式的工作进程在运行过程中也可以内部调用 `delegate_task`。

## 核心概念

- **看板**——一个独立的任务队列，拥有自己的 SQLite 数据库、工作空间目录以及调度循环。单次安装可创建多个看板（例如每个项目、仓库或领域一个看板）；详情请参见下文的[多项目看板](#boards-multi-project)部分。仅使用单个项目的用户将始终在 `default` 看板上操作，不会在本文档之外看到“看板”一词。
- **任务**——包含标题、可选正文、一名负责人（配置文件名称）、状态（`triage | todo | ready | running | blocked | done | archived`）、可选租户命名空间以及可选幂等键（用于避免重复处理的自动化操作）的记录行。
- **关联关系**——`task_links` 行用于记录父子任务之间的依赖关系。当所有父任务都标记为“已完成”时，调度器会将相关子任务的状态从 `todo` 提升为 `ready`。
- **评论**——智能体间的通信协议。智能体和人类用户均可添加评论；当工作进程被重新创建时，它会将完整的评论记录作为上下文的一部分读取。
- **工作空间**——工作进程运行的目录。共有三种类型：
  - `scratch`（默认）——位于 `~/.hermes/kanban/workspaces/<id>/` 下的临时目录（在非默认看板中则位于 `~/.hermes/kanban/boards/<slug>/workspaces/<id>/`）。**任务完成后会被删除**——由于 scratch 的设计初衷就是临时存储，因此一旦工作进程或 `hermes kanban complete <id>` 命令将任务标记为完成，该目录就会立即被清除。如果希望保留工作进程的输出结果，请使用 `worktree:` 或 `dir:<path>` 参数。在首次创建 scratch 工作空间时，调度器会记录警告信息，并在对应任务上触发 `tip_scratch_workspace` 事件（可通过 `hermes kanban show <id>` 查看）。
  - `dir:<path>`——现有的共享目录（如 Obsidian 存储库、邮件操作目录、单个账户的文件夹）。**必须是绝对路径**。像 `dir:../tenants/foo/` 这样的相对路径会在调度时被拒绝，因为它们会基于调度器当前所在的目录路径进行解析，而这容易产生歧义，也可能成为安全漏洞的入口。除此之外，该路径是可信的——这是您自己的目录和文件系统，工作进程以您的用户身份运行。这属于“受信任的本地用户”威胁模型；看板模式的设计本身就是单主机运行的。**任务完成后该目录内容会被保留**。
  - `worktree`——用于编码任务的 git 工作树，位于 `.worktrees/<id>/` 目录下。请使用 `worktree:<path>` 参数指定确切的目标路径。工作进程会通过 `git worktree add` 命令创建该工作树，如提供了 `--branch` 参数则会使用指定的分支。**任务完成后该工作树也会被保留**。
- **调度器**——一个长期运行的循环程序，每隔 N 秒（默认为 60 秒）会执行以下操作：回收已失效的任务请求、回收崩溃的工作进程（进程 ID 已消失但 TTL 未过期）、将状态为 `ready` 的任务提升到处理队列、以原子方式分配任务，并创建对应的处理配置文件。默认情况下，调度器在**网关内部**运行（`kanban.dispatch_in_gateway: true`）。每个调度周期内，一个调度器会处理所有看板中的任务；为每个工作进程创建时，会设置 `HERMES_KBANAN_BOARD` 环境变量，使其无法看到其他看板中的任务。如果同一个任务连续出现 `kanban.failure_limit` 次（默认为 2 次）创建失败，调度器会自动将该任务阻塞，并将最后一次出现的错误作为阻塞原因——这样可以避免因对应配置文件不存在、工作空间无法挂载等原因导致的任务处理陷入死循环。
- **租户**——看板内的可选字符串命名空间。一个智能体集群可以通过工作空间路径和内存键前缀实现数据隔离，从而为多个企业提供服务（例如通过 `--tenant business-a` 参数指定）。租户属于软性隔离机制，而看板才是真正的硬性隔离边界。

## 多项目看板

看板模式允许您将不同类型的工作流——每个项目、仓库或领域对应一个工作流——分隔到独立的队列中。新安装的 Hermes 系统仅包含一个名为 `default` 的看板（为兼容旧版本，数据库位于 `~/.hermes/kanban.db`）。仅需处理单一类型工作的用户无需了解看板功能，该功能是可选的。

每个看板都拥有完全独立的隔离机制：

- 每个看板都有独立的 SQLite 数据库（路径为 `~/.hermes/kanban/boards/<slug>/kanban.db`）。
- 分别有独立的 `workspaces/` 和 `logs/` 目录。
- 为某个任务创建的工作进程**仅能看到**该看板中的任务——调度器会在子进程的环境中设置 `HERMES_KBANAN_BOARD` 变量，而工作进程可访问的所有 `kanban_*` 工具都会读取该变量值。
- 不允许在不同看板之间建立任务关联关系（这样能保持架构简洁；如果确实需要跨项目引用任务，可以使用自由文本提及方式，并手动通过 ID 查找对应任务）。

### 通过 CLI 管理看板

```bash
# See what's on disk. Fresh installs show only "default".
hermes kanban boards list

# Create a new board.
hermes kanban boards create atm10-server \
    --name "ATM10 Server" \
    --description "Minecraft modded server ops" \
    --icon 🎮 \
    --switch                   # optional: make it the active board

# Operate on a specific board without switching.
hermes kanban --board atm10-server list
hermes kanban --board atm10-server create "Restart ATM server" --assignee ops

# Change which board is "current" for subsequent calls.
hermes kanban boards switch atm10-server
hermes kanban boards show             # who's active right now?

# Rename the display name (the slug is immutable — it's the directory name).
hermes kanban boards rename atm10-server "ATM10 (Prod)"

# Archive (default) — moves the board's dir to boards/_archived/<slug>-<ts>/.
# Recoverable by moving the dir back.
hermes kanban boards rm atm10-server

# Hard delete — `rm -rf` the board dir. No recovery.
hermes kanban boards rm atm10-server --delete
```

### 板块确定顺序（优先级从高到低）

1. 在 CLI 调用时明确指定 `--board <slug>` 参数。
2. 环境变量 `HERMES_KANBAN_BOARD`（由调度器在启动工作节点时设置，因此工作节点无法查看其他板块）。
3. `~/.hermes/kanban/current` —— 由 `hermes kanban boards switch` 命令保存的板块标识符。
4. 默认值。

板块标识符需符合以下规则：仅允许小写字母、数字、连字符和下划线，长度为 1-64 个字符，且必须以字母或数字开头。输入的大写字符会自动转换为小写。其他任何字符（如斜杠、空格、点号、`..`）都会在 CLI 层被拒绝，从而防止路径遍历攻击被用于指定板块。

### 通过控制面板管理板块

当存在多个板块或某个板块中有任务时，`hermes dashboard` 的看板标签页顶部会显示板块切换器。仅使用单个板块的用户只能看到一个小的“+ 新建板块”按钮；只有在需要切换时，切换器才会显示出来。

- **板块下拉菜单** —— 用于选择当前活跃的板块。您的选择会被保存在浏览器的 `localStorage` 中，因此即使重新加载页面，选择也不会丢失，也不会导致 CLI 的 `current` 指针因终端未关闭而改变。
- **+ 新建板块** —— 会弹出模态框，要求您输入板块标识符、显示名称、描述以及图标。还可以选择自动切换到新板块。
- **归档** —— 仅在非默认板块上显示。确认后会将该板块的目录移至 `boards/_archived/`。

所有控制面板的 API 接口都支持通过 `?board=<slug>` 参数来限定操作的板块范围。事件 WebSocket 在连接时会绑定到某个特定板块；通过界面切换板块时，会为新的板块建立一个新的 WebSocket 连接。

## 文件附件

任务可以携带文件附件——如 PDF、图片、源文件等——这样工作节点就能直接获取所需材料，而无需您在任务内容中手动粘贴路径并希望其能正确找到这些文件。

- **上传** —— 在控制面板的抽屉中打开某项任务，然后使用“附件”部分的“上传文件”按钮（可一次性上传多个文件）。每次上传的文件大小上限为 25 MB。
- **存储位置** —— 对于默认板块，文件存储在 `<hermes-home>/kanban/attachments/<task_id>/` 目录下；对于自定义名称的板块，则存储在 `<hermes-home>/kanban/boards/<slug>/attachments/<task_id>/` 目录下。可以通过设置 `HERMES_KANBAN_ATTACHMENTS_ROOT` 参数来指定自定义存储路径。
- **工作节点的查看方式** —— 当调度器将任务分配给工作节点时，工作节点的上下文会包含一个“附件”部分，列出每个文件的名称及其**绝对路径**。工作节点拥有完整的文件操作和终端工具访问权限，因此可以直接读取附件（如使用 `read_file` 函数或 `pdftotext` 等shell命令）。
- **下载/删除** —— 抽屉中会列出每个附件，并提供下载链接和删除按钮（×）。删除附件会同时移除对应的元数据记录以及磁盘上的文件。

:::note 远程终端后端
在看板工作节点的默认后端——即本地终端后端上，附件路径可以直接解析。如果在远程后端（如 Docker、Modal）上运行工作节点，则需要将板块的 `attachments/` 目录挂载到工作节点的沙箱环境中，这样才能让工作节点上下文中的绝对路径可以被访问。:::

## 快速入门

以下命令是由**您**（人类操作者）来设置板块和创建任务的。一旦任务被分配，调度器就会启动对应的模型配置作为工作节点，之后**模型会通过 `kanban_*` 工具调用而非 CLI 命令来处理任务**——详情请参阅[工作节点如何与板块交互](#how-workers-interact-with-the-board)。

```bash
# 1. Create the board (you)
hermes kanban init

# 2. Start the gateway (hosts the embedded dispatcher)
hermes gateway start

# 3. Create a task (you — or an orchestrator agent via kanban_create)
hermes kanban create "research AI funding landscape" --assignee researcher

# 4. Watch activity live (you)
hermes kanban watch

# 5. See the board (you)
hermes kanban list
hermes kanban stats
```

当调度器获取 `t_abcd` 并创建 `researcher` 类型的智能体配置后，工作节点模型首先会调用 `kanban_show()` 函数来读取自身的任务，而不会执行 `hermes kanban show t_abcd` 这样的命令。

### 内嵌在网关中的调度器（默认配置）

该调度器直接在网关进程内部运行。无需进行任何安装，也不需要单独管理服务——只要网关处于运行状态，符合条件的任务就会在下一个时间间隔（默认为60秒）被处理。

```yaml
# config.yaml
kanban:
  dispatch_in_gateway: true        # default
  dispatch_interval_seconds: 60    # default
```

为便于调试，可通过设置 `HERMES_KANBAN_DISPATCH_IN_GATEWAY=0` 在运行时覆盖配置参数。此时将遵循常规的网关监控机制：直接执行 `hermes gateway start` 命令，或将其作为 systemd 用户单元进行集成（详情请参阅网关相关文档）。若没有正在运行的网关，处于“准备中”的任务将保持原状，直至有网关启动——`hermes kanban create` 命令在创建任务时会对此情况发出警告。

以独立进程形式运行 `hermes kanban daemon` 的方式现已**废弃**，建议使用网关功能。如果确实无法运行网关（例如无头主机策略禁止运行长时间运行的服务等），可使用 `--force` 参数让旧的独立守护进程在单个版本周期内继续运行，但同时针对同一个 `kanban.db` 文件运行嵌入在网关中的调度器与独立的守护进程会导致数据竞争问题，此类用法是不被支持的。

### 可重试的创建操作（适用于自动化流程/ webhook）

```bash
# First call creates the task. Any subsequent call with the same key
# returns the existing task id instead of duplicating.
hermes kanban create "nightly ops review" \
    --assignee ops \
    --idempotency-key "nightly-ops-$(date -u +%Y-%m-%d)" \
    --json
```

### 批量 CLI 指令

所有与生命周期相关的指令均支持传入多个 ID，因此您只需一条命令即可批量处理：

```bash
hermes kanban complete t_abc t_def t_hij --result "batch wrap"
hermes kanban archive  t_abc t_def t_hij
hermes kanban unblock  t_abc t_def
hermes kanban block    t_abc "need input" --ids t_def t_hij
```

## 工作节点如何与看板交互

**工作节点无需直接调用 `hermes kanban` 命令行工具。** 当调度器启动一个工作节点时，它会将 `HERMES_KANBAN_TASK=t_abcd` 设置在子进程的环境变量中，该环境变量会激活模型架构中的专用**看板工具集**。对于那些在工具集配置中启用了 `kanban` 功能的协调器角色，同样可以使用这套工具集。这些工具通过与 CLI 相同的方式，直接通过 Python 的 `kanban_db` 层来读取和修改看板数据。正在运行的工作节点会像使用其他工具一样调用这些函数，它无需知晓也无需使用 `hermes kanban` CLI。

| 工具 | 功能 | 必需参数 |
|---|---|---|
| `kanban_show` | 读取当前任务的信息（标题、内容、之前的尝试记录、上级分配记录、评论以及完整格式化的 `worker_context`）。默认使用环境变量中的任务 ID。 | — |
| `kanban_list` | 根据“负责人”、“状态”、“租户”、“归档可见性”等条件列出任务摘要，并可设置查询上限。适用于协调器查看看板上的任务情况。 | — |
| `kanban_complete` | 通过结构化的 `summary` 和 `metadata` 完成任务交接。 | 必须提供 `summary` 或 `result` 中的至少一个参数 |
| `kanban_block` | 因特殊原因需要人工干预时，用于阻塞任务并说明原因。 | `reason` |
| `kanban_heartbeat` | 在执行耗时操作时发送存活信号。仅具有副作用。 | — |
| `kanban_comment` | 在任务讨论线程中添加持久性备注。 | `task_id`, `body` |
| `kanban_create` | （协调器使用）创建子任务，可指定负责人、上级任务、所需技能等信息。 | `title`, `assignee` |
| `kanban_link` | （协调器使用）事后添加 `parent_id → child_id` 的依赖关系。 | `parent_id`, `child_id` |
| `kanban_unblock` | （协调器使用）将被阻塞的任务恢复为“待处理”状态。 | `task_id` |

一个典型工作节点的处理流程如下：

```
# Model's tool calls, in order:
kanban_show()                                     # no args — uses HERMES_KANBAN_TASK
# (model reads the returned worker_context, does the work via terminal/file tools)
kanban_heartbeat(note="halfway through — 4 of 8 files transformed")
# (more work)
kanban_complete(
    summary="migrated limiter.py to token-bucket; added 14 tests, all pass",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
)
```

相反，**协调器**工作进程会进行并行分发：

```
kanban_show()
kanban_create(
    title="research ICP funding 2024-2026",
    assignee="researcher-a",
    body="focus on seed + series A, North America, AI-adjacent",
)
# → returns {"task_id": "t_r1", ...}
kanban_create(title="research ICP funding — EU angle", assignee="researcher-b", body="…")
# → returns {"task_id": "t_r2", ...}
kanban_create(
    title="synthesize findings into launch brief",
    assignee="writer",
    parents=["t_r1", "t_r2"],                     # promotes to ready when both complete
    body="one-pager, 300 words, neutral tone",
)
kanban_complete(summary="decomposed into 2 research tasks + 1 writer; linked dependencies")
```

这些用于处理外部任务的“(协调器)”工具——即`kanban_list`、`kanban_create`、`kanban_link`、`kanban_unblock`以及`kanban_comment`——均属于同一套工具集。根据`kanban-orchestrator`技能所规定的规范，工作者角色不会分散处理或路由无关任务，而协调器角色则不会执行具体的实现工作。由调度器生成的工作者在执行会破坏任务状态的生命周期操作时仍受任务范围限制，无法修改无关任务。

### 为何使用工具而非直接调用`hermes kanban`

原因有三：

1. **后端兼容性**：那些终端工具指向远程后端（如Docker、Modal、Singularity或SSH）的工作者，需要在容器内部运行`hermes kanban complete`命令，而容器内并未安装`hermes`，也无法挂载`~/.hermes/kanban.db`文件。相比之下，看板工具在代理自身的Python进程中运行，无论终端后端为何，都能正常访问`~/.hermes/kanban.db`。

2. **避免Shell引号问题**：通过shlex + argparse传递`--metadata '{"files": [...]}'`这种方式存在潜在隐患。而结构化的工具参数则完全避免了这一问题。

3. **更清晰的错误信息**：工具返回的是结构化的JSON数据，模型可以对其进行分析处理；而直接通过标准错误流输出的字符串则需要模型自行解析，容易出错。

**常规会话中无额外架构开销**：在普通的`hermes chat`会话中，其架构中不会包含任何`kanban_*`工具，除非当前激活的角色明确为协调器工作启用了看板工具集。由调度器生成的任务工作者由于设置了`HERMES_KANBAN_TASK`参数，因此会获得与任务相关的工具；而协调器角色则可通过配置获得更广泛的路由功能。对于从不使用看板功能的用户而言，无需承担额外的工具负担。

`kanban-worker`和`kanban-orchestrator`技能会告知模型何时以及按何种顺序调用相应工具。

### 推荐的交接信息格式

`kanban_complete(summary=..., metadata={...})`的设计具有高度灵活性：`summary`部分是供人类阅读的总结内容，而`metadata`部分则是机器可读的交接数据，下游的代理、审核人员或监控面板无需解析文字内容即可直接使用这些数据。

对于工程任务和审核任务，建议采用以下可选的元数据格式：

```json
{
  "changed_files": ["path/to/file.py"],
  "verification": ["pytest tests/hermes_cli/test_kanban_db.py -q"],
  "dependencies": ["parent task id or external issue, if any"],
  "blocked_reason": null,
  "retry_notes": "what failed before, if this was a retry",
  "residual_risk": ["what was not tested or still needs human review"]
}
```

这些键仅是一种约定，并非架构层面的强制要求。其优势在于，每个工作节点都能留下足够的线索，以便后续处理者能够快速回答以下四个问题：

1. 发生了什么变化？
2. 是如何进行验证的？
3. 若任务失败，有哪些方法可以解除阻塞或重新尝试？
4. 还有哪些风险被刻意保留未处理？

请将敏感信息、原始日志、令牌、OAuth相关内容以及无关的记录内容排除在`metadata`之外，转而存储指针和摘要信息。如果某个任务没有相关文件或测试用例，应在`summary`中明确说明，而将实际存在的证据（如源代码链接、问题编号或人工审核步骤等）存放在`metadata`中。

### 工作节点技能

任何需要处理看板任务的配置文件都必须加载`kanban-worker`技能。该技能会通过**工具调用**而非CLI命令，向工作节点传授完整的任务处理流程：

1. 启动时，调用`kanban_show()`函数以获取任务标题、内容、上级任务关联信息、之前的尝试记录以及完整的评论线程。
2. 通过终端工具执行`cd $HERMES_KANBAN_WORKSPACE`命令，然后在相应环境中执行任务操作。
3. 在执行耗时较长的操作时，每隔几分钟调用一次`kanban_heartbeat(note="...")`函数。**如果任务可能运行超过1小时，至少每小时需调用一次`kanban_heartbeat`**——调度器会在一小时未收到心跳信号且任务运行时间已超过`kanban.dispatch_stale_timeout_seconds`（默认为4小时）时，认为工作节点发生崩溃且未进行清理操作，从而自动回收该任务。这种回收操作不会造成严重后果（任务会回到`ready`状态以便重新调度，且失败计数器不会增加），但会导致当前任务的进度丢失。
4. 任务完成后，调用`kanban_complete(summary="...", metadata={...})`函数；如果遇到问题，则调用`kanban_block(reason="...")`函数。

最终的`kanban_complete`/`kanban_block`调用属于工作节点协议的一部分。如果工作节点在任务仍处于`running`状态时以状态0退出，调度器会将其视为协议违规行为，触发`protocol_violation`事件，并在下一个周期自动阻塞该任务，而不会让其重新进入同一处理循环。这通常意味着模型仅生成了纯文本答案，便未使用看板工具功能即退出了。

`kanban-worker`是一种预装技能，在安装和更新过程中会自动同步到所有配置文件中，无需单独通过Skills Hub进行安装。请确认你在用于处理看板任务的任意配置文件（如`researcher`、`writer`、`ops`等）中都已包含该技能。

```bash
hermes -p <your-worker-profile> skills list | grep kanban-worker
```

如果缺少捆绑的副本，请为该配置文件恢复它：

```bash
hermes -p <your-worker-profile> skills reset kanban-worker --restore
```

调度器在创建每个工作节点时，还会自动添加 `--skills kanban-worker` 参数，因此即便某个角色的默认技能配置中未包含该技能，工作节点依然能够使用相应的模式库。

### 将额外技能绑定到特定任务

有时单个任务需要处理员角色默认不具备的专用技能——比如翻译任务需要 `translation` 技能，审核任务需要 `github-code-review` 技能，安全审计任务则需要 `security-pr-audit` 技能。无需每次都修改处理员的配置，可直接将所需技能绑定到具体任务上。

**对于协调器代理**（即通常情况下一个代理负责将任务分配给另一个代理的情形），可使用 `kanban_create` 工具中的 `skills` 数组来实现这一功能：

```
kanban_create(
    title="translate README to Japanese",
    assignee="linguist",
    skills=["translation"],
)

kanban_create(
    title="audit auth flow",
    assignee="reviewer",
    skills=["security-pr-audit", "github-code-review"],
)
```

**通过人工指令（CLI/斜杠命令）操作时**，需针对每项技能重复输入 `--skill`：

```bash
hermes kanban create "translate README to Japanese" \
    --assignee linguist \
    --skill translation

hermes kanban create "audit auth flow" \
    --assignee reviewer \
    --skill security-pr-audit \
    --skill github-code-review
```

**在控制面板中**，将所需技能以逗号分隔后输入到内联创建表单的 **skills** 字段中。

这些技能会**叠加**到内置的 `kanban-worker` 上——调度器会为每个技能（包括内置技能）生成一个 `--skills <name>` 参数，这样工作进程启动时就会加载所有这些技能。技能名称必须与分配者账号配置中实际安装的技能一致（可运行 `hermes skills list` 查看可用技能），不支持在运行时动态安装。

### 目标模式卡片（`--goal`）

默认情况下，每个工作进程仅有一次处理其对应卡片的**机会**：完成工作后调用 `kanban_complete`/`kanban_block` 即可退出。若需让该工作进程进入**目标循环**模式（即 `/goal` 接口背后的相同 Ralph 式引擎），则需通过 `--goal`（命令行）或 `goal_mode=True`（`kanban_create` 工具/控制面板）来指定。在这种模式下，每轮结束后，辅助判题器会将工作进程的输出结果与卡片中的标题及内容（视为验收标准）进行比对；如果工作尚未完成且轮次预算尚未用尽，工作进程将在**同一会话中**继续处理，直到判题器认可结果、工作进程主动终止任务，或轮次预算耗尽——此时卡片会被**锁定**以供人工审核，而不会静默退出。

```bash
hermes kanban create "Translate the docs site to French" \
    --body "Acceptance: every page translated, no English left, links intact." \
    --assignee linguist \
    --goal \
    --goal-max-turns 15      # optional; default 20
```

适用于需要开放式处理、多步骤完成，或“持续执行直至满足条件X”类型的任务卡片。对于简单的单次性任务则无需使用该功能——每轮的判定开销并不值得，而且调度器现有的重试/断路机制已能处理临时性的工作者故障。判定的质量取决于目标描述的质量，因此请将任务内容明确写成**具体的验收标准**。

### 编排器技能

**一个表现良好的编排器不会亲自执行任务。**它会将用户的目标拆解为多个子任务，将这些子任务相互关联，再将每个子任务分配给预先设定的不同角色配置，之后便不再干预。`kanban-orchestrator`技能通过工具调用模式来实现这一功能：包括防干扰规则、步骤0阶段的角色配置检测提示（由于调度器在遇到未知的角色名称时会自动失败，因此编排器必须确保所有任务都基于机器上实际存在的角色配置来执行），以及以`kanban_create`/`kanban_link`/`kanban_comment`为关键的操作拆解流程。

典型的编排器工作流程（两名并行处理的研究人员将任务转交给撰写者）：

```
# Goal from user: "draft a launch post on the ICP funding landscape"
kanban_create(title="research ICP funding, NA angle",  assignee="researcher-a", body="…")  # → t_r1
kanban_create(title="research ICP funding, EU angle",  assignee="researcher-b", body="…")  # → t_r2
kanban_create(
    title="synthesize ICP funding research into launch post draft",
    assignee="writer",
    parents=["t_r1", "t_r2"],        # promoted to 'ready' when both researchers complete
    body="one-pager, neutral tone, cite sources inline",
)                                     # → t_w1
# Optional: add cross-cutting deps discovered later without re-creating tasks
kanban_link(parent_id="t_r1", child_id="t_followup")
kanban_complete(
    summary="decomposed into 2 parallel research tasks → 1 synthesis task; writer starts when both researchers finish",
)
```

`kanban-orchestrator` 是一种内置技能。它在安装和更新过程中会自动同步到每个配置文件中，因此无需单独进行 Skills Hub 的安装操作。请检查您的编排器配置文件中是否已包含该技能：

```bash
hermes -p orchestrator skills list | grep kanban-orchestrator
```

如果缺少内置副本，请为该配置文件恢复它：

```bash
hermes -p orchestrator skills reset kanban-orchestrator --restore
```

为获得最佳效果，建议将其与工具集仅限于看板操作（`kanban`、`gateway`、`memory`）的配置文件搭配使用。这样一来，即使协调器试图执行实现任务，也根本无法完成。

## 控制面板（GUI）

使用 `/kanban` CLI 命令或斜杠命令即可在无界面模式下运行看板，但对于需要人工参与的场景而言，可视化的看板通常是更合适的界面——它支持任务分类、跨配置文件监控、查看评论线程以及在不同列之间拖动卡片。Hermes 按照[扩展控制面板](./extending-the-dashboard)中所述的模式，将此功能作为**预装的控制面板插件**提供在 `plugins/kanban/` 目录下——它既非核心功能，也不是独立服务。可通过以下方式打开它：

```bash
hermes kanban init      # one-time: create kanban.db if not already present
hermes dashboard        # "Kanban" tab appears in the nav, after "Skills"
```

### 该插件为您带来的功能

- **看板**选项卡：每个状态对应一列，包括`triage`、`todo`、`ready`、`running`、`blocked`、`done`（开启对应开关后还会显示`archived`列）。
  - `triage`列用于暂存初步构思。在默认设置（`kanban.auto_decompose: true`）下，调度器会自动对放入此处的任务运行**分解器**。内置的分解器会使用`auxiliary.kanban_decomposer`模型路径，读取您的个人资料列表及其中描述的职责信息，然后将任务拆解为一系列子任务，根据任务特性分配给最合适的专家处理。原始任务会作为所有子任务的父任务继续存在，这样当所有子任务处理完毕时，其负责人（`kanban.orchestrator_profile`，若未设置则使用当前默认负责人）便可重新启动来判定任务是否完成。您可以通过页面顶部的**Orchestration: Auto/Manual**切换按钮（翠绿色表示自动模式，灰暗灰色表示手动模式）或直接编辑`config.yaml`文件来切换模式。这两种模式均可与`hermes kanban specify`功能共存——当您不希望任务拆解时，仍可使用该功能对单个任务进行配置重写。
- 任务卡片会显示任务ID、标题、优先级标签、租户标识、负责人员、评论/链接数量、**进度指示条**（若任务存在依赖关系，则显示“已完成N个/共M个子任务”），以及“创建于N前”。每张卡片上都配有复选框，支持多选操作。
- **Running列内的按负责人分组功能**——通过工具栏上的复选框，可按负责人员对Running列进行子分组。
- **通过WebSocket实现实时更新**——该插件会以较短的间隔轮询仅支持追加操作的`task_events`表；一旦有任何配置文件（CLI、网关或其他仪表板选项卡）发生更改，看板会立即反映出来。为了减少频繁刷新带来的负担，系统会对连续的事件进行去抖处理，避免每次都有新事件时都触发重新获取数据。
- 可通过拖放卡片在列之间移动来更改任务状态。拖放操作会发送`PATCH /api/plugins/kanban/tasks/:id`请求，该请求会经过与CLI相同的`kanban_db`代码处理——因此三种使用界面之间的功能始终保持一致。当任务被移动到具有破坏性意义的状态（如`done`、`archived`、`blocked`）时，系统会要求用户确认操作。针对触摸设备，系统还提供了基于指针的操作方式，确保可在平板电脑上正常使用看板。
- **内联创建功能**——点击任意列标题处的“+”号，即可输入任务标题、负责人员、优先级，还可以从所有现有任务的下拉列表中选择父任务。按回车键可创建任务，按Shift+回车键可在标题字段中插入换行符，按Esc键可取消操作。从Triage列创建的任务会自动被暂存到该列中。
- **多选与批量操作功能**——按住Shift或Ctrl键点击卡片或勾选其复选框，即可将其加入选择列表。顶部会出现批量操作栏，提供批量状态转换、归档以及重新分配任务（可通过下拉列表选择负责人，或选择“取消分配”）等功能。对于批量操作，系统会先要求用户确认。即使部分任务处理失败，其余任务仍会继续执行。
- **点击卡片**（无需按住Shift或Ctrl键）即可打开侧边抽屉（按Esc键或点击页面外部可关闭），其中包含：
  - **可编辑的标题**——点击标题即可修改名称。
  - **可编辑的负责人员/优先级**——点击元数据行即可重新设置。
  - **可编辑的描述**——默认以Markdown格式显示（支持标题、加粗、斜体、内联代码、代码块、`http(s)` / `mailto:`链接以及项目列表），还配有“编辑”按钮，点击后会切换为文本输入框。该Markdown渲染器经过特殊处理，具备XSS防护功能——所有替换操作都会在经过HTML转义的输入数据上执行，只有`http(s)` / `mailto:`链接能够直接通过，且始终会设置`target="_blank"` + `rel="noopener noreferrer"`属性。
  - **依赖关系编辑器**——以芯片形式展示父任务和子任务列表，每个项目旁都有一个“×”按钮可用于断开关联；此外还提供其他所有任务的下拉列表，可用于添加新的父任务或子任务。若尝试形成循环依赖，服务器端会立即拒绝并给出明确提示。
  - **状态操作行**（包含→ triage / → ready / → running / block / unblock / complete / archive等选项），对于具有破坏性意义的状态转换，系统会要求用户确认。对于位于**Triage**列的卡片，该操作行还提供了两个由大语言模型驱动的功能：**⚗ Decompose**功能会将任务拆解为一系列子任务，并根据任务描述将它们分配给相应的专家；**✨ Specify**功能则会对单个任务进行配置重写。如果大语言模型判断任务无需拆解，它会自动采用Specify模式进行处理，因此Decompose实际上是Specify模式的扩展版本。这两种功能均可通过CLI命令（`hermes kanban decompose <id>` / `specify <id>` / `--all`）调用，也可通过任何网关平台（`/kanban decompose <id>`）调用，还可以通过编程方式通过`POST /api/plugins/kanban/tasks/:id/decompose`和`…/specify`接口调用。相关模型可在`config.yaml`文件中的`auxiliary.kanban_decomposer`和`auxiliary.triage_specifier`字段中进行配置。
  - 结果展示区域（同样以Markdown格式显示）、评论区（按回车键即可提交评论）以及最近20条事件记录。
- **工具栏过滤器**——支持全文搜索、租户下拉选择（默认值为`config.yaml`文件中指定的`dashboard.kanban.default_tenant`）、负责人员下拉选择、“显示已归档任务”切换开关、“按负责人分组”切换开关，以及一个**Nudge dispatcher**按钮，让您无需等待60秒的时间间隔即可手动触发任务处理。

从视觉设计上看，该看板采用了大家熟悉的Linear / Fusion布局风格：深色主题，列标题旁显示任务数量，状态用彩色圆点标识，优先级和租户信息则通过颜色芯片呈现。该插件仅读取主题CSS变量（如`--color-*`、`--radius`、`--font-mono`等），因此会自动根据当前激活的仪表板主题调整外观。

### 自动调度与手动调度模式

对于您放入Triage列的任务，看板提供了两种处理方式：

**自动模式（默认）**——`kanban.auto_decompose: true`。嵌入在网关中的调度器会每隔一定时间运行一次**分解器**，其运行频率受`kanban.auto_decompose_per_tick`参数限制（默认为每轮间隔处理3个任务），这样可以避免大量Triage列任务同时被处理，从而防止占用过多的辅助大语言模型算力。分解器会使用内置的分解提示词以及`auxiliary.kanban_decomposer`模型路径，读取您已安装的配置文件及其描述信息，然后让大语言模型生成一个JSON格式的任务图谱：明确哪些任务需要创建、这些任务应分配给谁、以及哪些任务之间存在依赖关系。原始的Triage列任务会成为任务图谱中所有子任务的父任务，因此会一直存在，直到整个图谱中的所有任务处理完毕——之后该任务状态会恢复为`ready`，其负责人（`kanban.orchestrator_profile`，若未设置则使用当前默认负责人）便可重新判定任务是否完成，如果仍有工作未完成，还可以继续添加新任务。这就是所谓的“输入简要描述后即可离开”的处理流程。

**手动模式**——`kanban.auto_decompose: false`。Triage列中的任务会一直留在该列中，直到您主动进行处理。您可以点击卡片上的**⚗ Decompose**按钮，运行`hermes kanban decompose <id>`命令（或使用`--all`参数），也可以通过聊天界面输入`/kanban decompose <id>`来触发分解操作。这种模式与分解器出现之前的看板行为一致，适合那些希望完全掌控任务处理流程的用户。

您可以通过看板页面顶部的**Orchestration: Auto/Manual**切换按钮（翠绿色表示自动模式，灰暗灰色表示手动模式）或直接编辑`config.yaml`文件来在两种模式之间切换。这两种模式均可与`hermes kanban specify`功能共存——当您不希望任务拆解时，仍可使用该功能对单个任务进行配置重写。

分解器的任务分配决策取决于配置文件中的描述信息，这些描述信息是通过`hermes profile create --description "..."`、`hermes profile describe <name> --text "..."`、`hermes profile describe <name> --auto`（由大语言模型根据该配置文件中已安装的技能和模型自动生成描述）命令，或通过展开后的**Orchestration settings**面板中的配置文件编辑器来设置的。那些没有描述信息的配置文件仍会显示在列表中——虽然无法通过描述进行精确匹配，但仍然可以通过名称进行分配。分解器绝不会将子任务的负责人员设置为`assignee=None`：当大语言模型无法识别某个配置文件时，该子任务会被分配给`kanban.default_assignee`（若未设置则使用当前默认负责人）。

`kanban.orchestrator_profile`参数并不会在分解过程中加载该配置文件的提示词、技能或自定义逻辑。它的作用只是确定任务拆解完成后，谁来负责处理根任务或整体调度任务。如果您想更改分解器使用的模型或提供方，可以修改`auxiliary.kanban_decomposer`的配置。如果您希望使用特定配置文件的自定义任务拆分逻辑，而非内置的分解器，则需切换到手动模式，并让该配置文件显式地创建或分解任务。

相关配置参数均位于`~/.hermes/config.yaml`文件中的`kanban:`部分，具体如下：

| 参数名 | 默认值 | 作用 |
|---|---|---|
| `auto_decompose` | `true` | 调度器会每隔一定时间自动运行分解器。 |
| `auto_decompose_per_tick` | `3` | 每次调度器轮询时允许分解的任务数量上限。超出此数量的任务将推迟到下一次处理。 |
| `orchestrator_profile` | `""` | 任务拆解完成后，负责处理根任务或整体调度任务的配置文件。若该参数为空，则默认使用当前激活的默认配置文件。 |
| `default_assignee` | `""` | 当大语言模型无法识别某个配置文件时，子任务将分配给该负责人。若该参数为空，则默认使用当前激活的默认负责人。 |

此外还有两个用于辅助大语言模型的参数：

| 参数名 | 作用 |
|---|---|
| `auxiliary.kanban_decomposer` | 用于生成任务图谱的模型（由Decompose功能调用）。可通过设置`provider`/`model`参数来替代主聊天模型。 |
| `auxiliary.profile_describer` | 用于自动生成配置文件描述信息的模型（由`hermes profile describe --auto`命令调用）。 |

### 架构设计

该GUI层仅作为一个**通过数据库读取数据并写入kanban_db的中间层**，本身不包含任何业务逻辑处理功能：

<!-- ascii-guard-ignore -->
```
┌────────────────────────┐      WebSocket (tails task_events)
│   React SPA (plugin)   │ ◀──────────────────────────────────┐
│   HTML5 drag-and-drop  │                                    │
└──────────┬─────────────┘                                    │
           │ REST over fetchJSON                              │
           ▼                                                  │
┌────────────────────────┐     writes call kanban_db.*        │
│  FastAPI router        │     directly — same code path      │
│  plugins/kanban/       │     the CLI /kanban verbs use      │
│  dashboard/plugin_api.py                                    │
└──────────┬─────────────┘                                    │
           │                                                  │
           ▼                                                  │
┌────────────────────────┐                                    │
│  ~/.hermes/kanban.db   │ ───── append task_events ──────────┘
│  (WAL, shared)         │
└────────────────────────┘
```
### REST 接口

所有接口均挂载在 `/api/plugins/kanban/` 下，并通过控制面板的临时会话令牌进行保护：

| 方法 | 路径 | 用途 |
|---|---|---|
| `GET` | `/board?tenant=<name>&include_archived=…` | 按状态列分组显示完整看板，同时提供租户和负责人选项用于下拉筛选 |
| `GET` | `/tasks/:id` | 显示任务内容、评论、事件及相关链接 |
| `POST` | `/tasks` | 创建任务（内部调用 `kanban_db.create_task`，支持 `triage: bool` 和 `parents: [id, …]` 参数） |
| `PATCH` | `/tasks/:id` | 更新任务的状态、负责人、优先级、标题、内容及处理结果 |
| `POST` | `/tasks/bulk` | 对 `ids` 列表中的每个任务应用相同的更新操作（状态、归档、负责人、优先级）。若某项更新失败，不会中断其他任务的处理 |
| `POST` | `/tasks/:id/comments` | 添加评论 |
| `POST` | `/tasks/:id/specify` | 运行分类处理工具——辅助大语言模型会完善任务内容，并将其从“待分类”状态转为“待办”状态。返回值为 `{ok, task_id, reason, new_title}`；当任务不在分类列表中、没有可用辅助客户端或大语言模型出现错误时，虽然 `ok=false` 且包含可读原因，但响应状态仍为 200，而非 4xx 级别 |
| `POST` | `/tasks/:id/decompose` | 运行看板分解工具——辅助大语言模型会生成任务图谱，随后辅助组件会原子化地创建子任务、建立关联，并将任务状态从“待分类”转为“待办”。返回值为 `{ok, task_id, reason, fanout, child_ids, new_title}`。与大语言模型出错时的响应规则相同，仍为 200 状态码 |
| `GET` | `/profiles` | 列出已安装的配置文件及其描述信息（供控制面板的配置描述编辑器和任务调度器选择器使用） |
| `PATCH` | `/profiles/:name` | 设置或清除配置文件的描述信息（由用户手动输入，`description_auto: false`）。返回值为 `{ok, profile, description}` |
| `POST` | `/profiles/:name/describe-auto` | 通过 `auxiliary.profile_describer` 为配置文件自动生成描述信息。该描述信息会以 `description_auto: true` 的形式保存，从而使控制面板能够显示“待审核”标识 |
| `GET` | `/orchestration` | 读取看板任务调度设置（如 `orchestrator_profile`、`default_assignee`、`auto_decompose`），以及经过默认值 fallback 处理后的最终有效值 |
| `PUT` | `/orchestration` | 更新 `config.yaml` 文件中三个调度相关键值中的任意一个。系统会验证指定的配置文件名称确实存在且非空 |
| `POST` | `/links` | 添加依赖关系（格式为 `parent_id` → `child_id`） |
| `DELETE` | `/links?parent_id=…&child_id=…` | 删除依赖关系 |
| `POST` | `/dispatch?max=…&dry_run=…` | 提前触发任务调度器——跳过 60 秒的等待时间 |
| `GET` | `/config` | 从 `config.yaml` 文件中读取 `dashboard.kanban` 相关配置选项，如 `default_tenant`、`lane_by_profile`、`include_archived_by_default`、`render_markdown` 等 |
| `WS` | `/events?since=<event_id>` | 实时流式传输 `task_events` 表中的数据记录 |

每个处理函数都只是一个简单的封装层——该插件本身仅有约 700 行 Python 代码（包含路由器、WebSocket 处理逻辑、批量操作功能及配置读取模块），并未添加任何新的业务逻辑。还有一个名为 `_conn()` 的小型辅助函数，会在每次读写操作时自动初始化 `kanban.db`，因此无论用户是先打开控制面板、直接调用 REST API，还是运行 `hermes kanban init` 命令，都能正常使用功能。

### 控制面板配置

`~/.hermes/config.yaml` 文件中 `dashboard.kanban` 下的任意配置键值都会改变对应选项卡的默认设置——插件会在加载时通过调用 `GET /config` 接口读取这些配置值：

```yaml
dashboard:
  kanban:
    default_tenant: acme              # preselects the tenant filter
    lane_by_profile: true             # default for the "lanes by profile" toggle
    include_archived_by_default: false
    render_markdown: true             # set false for plain <pre> rendering
```

每个参数均为可选项，若未指定则默认使用所示值。

### 安全模型

控制面板的 HTTP 认证中间件会**明确跳过 `/api/plugins/` 路由**（详见[扩展控制面板](./extending-the-dashboard#backend-api-routes)）。由于控制面板默认绑定在本地主机，因此插件路由被设计为无需认证。这意味着主机上的任何进程均可访问看板相关的 REST 接口。

而 WebSocket 连接则需额外一步验证：它要求将控制面板的临时会话令牌作为 `?token=…` 查询参数传递（因为浏览器无法在升级请求中设置 `Authorization` 头），这一方式与浏览器内置的 PTY 桥接所使用的机制一致。

如果您运行 `hermes dashboard --host 0.0.0.0`，那么包括看板在内的所有插件路由都将可从网络访问。**请勿在共享主机上执行此操作。** 看板中存储着任务内容、评论以及工作空间路径；一旦攻击者获取了这些路由的访问权限，他们便能读取您的整个协作数据，还能创建、重新分配或归档任务。

`~/.hermes/kanban.db` 中的任务信息是刻意设计为与特定用户配置无关的（这正是该组件的协调机制）。即便您使用 `hermes -p <profile> dashboard` 命令打开控制面板，它仍然会显示主机上其他用户配置创建的任务。所有用户配置都由同一用户拥有，但若系统中存在多个角色，了解这一点非常重要。

### 实时更新

`task_events` 是一个只读的 SQLite 表，其中包含单调递增的 `id` 字段。WebSocket 端点会记录每个客户端上次查看的事件 ID，并在新的事件生成后立即推送相应数据。当大量事件同时到达时，前端只需重新加载成本极低的看板接口——这比针对每种类型的事件都尝试更新本地状态更为简单且准确。由于采用 WAL 模式，读取操作永远不会阻塞调度器正在处理的 `BEGIN IMMEDIATE` 事务。

### 扩展功能

该插件遵循标准的 Hermes 控制面板插件规范——完整的配置文档、Shell 插槽、页面级插槽以及插件 SDK 都可在[扩展控制面板](./extending-the-dashboard)中找到。无需 fork 该插件，即可实现添加额外列、自定义卡片样式、按租户筛选布局，或完全替换 `tab.override` 功能等需求。

如需禁用该功能而不删除它：只需在 `config.yaml` 中添加 `dashboard.plugins.kanban.enabled: false`（或删除 `plugins/kanban/dashboard/manifest.json` 文件）即可。

### 范围边界

该控制面板的界面设计得极为简洁。插件能够实现的所有功能都可通过 CLI 访问；插件只是为人类用户提供了更便捷的操作方式。自动分配任务、预算管理、审批流程以及组织结构视图等功能仍属于用户空间——可以通过路由器配置、其他插件，或直接复用 `tools/approval.py` 文件来实现，这些内容均在设计规范中的“不在支持范围内”部分有所说明。

## CLI 命令参考

这是**您**（或脚本、cron 任务、控制面板本身）用于操作看板的接口。在调度器内部运行的工作进程也会使用 `kanban_*` [工具接口](#how-workers-interact-with-the-board)来执行相同操作——这里的 CLI 和那边的工具都会通过 `kanban_db` 进行数据交互，因此从设计上讲，这两种接口是相互一致的。

```
hermes kanban init                                     # create kanban.db + print daemon hint
hermes kanban create "<title>" [--body ...] [--assignee <profile>]
                                [--parent <id>]... [--tenant <name>]
                                [--workspace scratch|worktree|worktree:<path>|dir:<path>]
                                [--branch <name>]
                                [--priority N] [--triage] [--idempotency-key KEY]
                                [--max-runtime 30m|2h|1d|<seconds>]
                                [--max-retries N]
                                [--goal] [--goal-max-turns N]
                                [--skill <name>]...
                                [--json]
hermes kanban list [--mine] [--assignee P] [--status S] [--tenant T] [--archived]
        [--workflow-template-id <id>] [--current-step-key <key>]
        [--sort created|created-desc|priority|priority-desc|status|assignee|title|updated]
        [--json]
hermes kanban show <id> [--json]
hermes kanban assign <id> <profile>                    # or 'none' to unassign
hermes kanban reassign <id>... <profile>               # bulk re-assign tasks to a profile
hermes kanban edit <id> [--title ...] [--body ...]     # edit task title / body / priority in place
        [--priority N]
hermes kanban promote <id>...                          # move todo/blocked tasks to ready (recovery)
hermes kanban schedule <id> --at <ISO8601>             # set/clear a task's scheduled_at start time
hermes kanban diagnostics [--json]                     # board health snapshot (alias: diag)
hermes kanban link <parent_id> <child_id>
hermes kanban unlink <parent_id> <child_id>
hermes kanban claim <id> [--ttl SECONDS]
hermes kanban comment <id> "<text>" [--author NAME]

# Bulk verbs — accept multiple ids:
hermes kanban complete <id>... [--result "..."]
hermes kanban block <id> "<reason>" [--ids <id>...]
hermes kanban unblock <id>...
hermes kanban archive <id>...

hermes kanban tail <id>                                # follow a single task's event stream
hermes kanban watch [--assignee P] [--tenant T]        # live stream ALL events to the terminal
        [--kinds completed,blocked,…] [--interval SECS]
hermes kanban heartbeat <id> [--note "..."]            # worker liveness signal for long ops
hermes kanban runs <id> [--json]                       # attempt history (one row per run)
hermes kanban assignees [--json]                       # profiles on disk + per-assignee task counts
hermes kanban dispatch [--dry-run] [--max N]           # one-shot pass
        [--failure-limit N] [--json]
hermes kanban daemon --force                           # DEPRECATED — standalone dispatcher (use `hermes gateway start` instead)
        [--failure-limit N] [--pidfile PATH] [-v]
hermes kanban stats [--json]                           # per-status + per-assignee counts
hermes kanban log <id> [--tail BYTES]                  # worker log from ~/.hermes/kanban/logs/
hermes kanban notify-subscribe <id>                    # gateway bridge hook (used by /kanban in the gateway)
        --platform <name> --chat-id <id> [--thread-id <id>] [--user-id <id>]
hermes kanban notify-list [<id>] [--json]
hermes kanban notify-unsubscribe <id>
        --platform <name> --chat-id <id> [--thread-id <id>]
hermes kanban context <id>                             # what a worker sees
hermes kanban specify [<id> | --all] [--tenant T]      # flesh out a triage-column idea
        [--author NAME] [--json]                       #   into a full spec and promote to todo
hermes kanban gc [--event-retention-days N]            # workspaces + old events + old logs
        [--log-retention-days N]
```

所有命令均可在交互式 CLI 以及消息网关中以斜杠命令的形式使用（详见下文的 [`/kanban` 斜杠命令](#kanban-slash-command)）。

`--max-retries` 是用于为调度器设置单个任务的熔断器参数。设置为 `--max-retries 1` 时，任务在首次执行失败即会被阻塞；而设置为 `--max-retries 3` 则允许两次重试，第三次失败后才会阻塞。若不指定该参数，则会使用 `config.yaml` 中的 `kanban.failure_limit` 值，即默认内置值。

### 并发性、调度及子任务升级配置

| 配置键 | 默认值 | 功能说明 |
|--------|---------|----------|
| `kanban.max_in_progress` | 未设置（无限制） | 限制同时运行的任务数量。当看板上已有 N 个任务在运行时，调度器将不再创建新任务——这有助于那些处理速度较慢的节点（如本地大语言模型、资源受限的服务器），让它们先完成现有任务，避免新任务堆积导致超时。若该值无效或小于 1，则会记录警告并视为无限制。 |
| `kanban.max_in_progress_per_profile` | 未设置（无限制） | 是 `max_in_progress` 的按角色版本——限制每个指定角色的任务同时运行数量。当某个角色处理速度较慢或存在速率限制时，此配置可确保其他角色仍能持续处理任务。该配置与看板级的 `max_in_progress` 同时生效，两者都必须允许创建新任务，流程才能继续。 |
| `kanban.auto_promote_children` | `true` | 当 `decompose_triage_task()` 生成没有父任务阻塞依赖的子任务后，这些子任务会自动被标记为 `ready` 状态，以便调度器处理。若设置为 `false`，则需手动审核——子任务将一直保持在 `todo` 状态，直到您手动将其升级。 |
| `kanban.default_workdir` | 未设置 | 当既未通过 `--workspace` 参数指定，任务本身也未指定工作目录时，会为新任务应用此看板级默认工作目录。若任务中指定了 `workspace:` 参数，则仍以该参数为准。 |

```yaml
kanban:
  max_in_progress: 2
  auto_promote_children: false
  default_workdir: ~/work/active-project
```

### 定时任务启动时间（`scheduled_at`）

为任务设置 `scheduled_at` 参数，即可将任务发送时间延迟至特定时刻。调度器会跳过那些 `scheduled_at` 时间仍在未来、尚未就绪的任务，而是在该时间戳之后的第一个计时周期再对这些任务进行处理。

```bash
hermes kanban create "nightly backup audit" \
  --assignee ops --scheduled-at "2026-06-01T03:00:00Z"
```

### 任务重新派发保护机制

当任务在上一轮执行时遇到配额限制、认证错误或 429 错误（`blocker_auth`），或在保护时间窗口内已成功完成（`recent_success`），又或者最近的任务备注中包含了 GitHub PR 链接（`active_pr`）时，调度器将拒绝重新派发该任务。此机制可避免在人工处理过程中，同一缺陷或任务被重复分配给工作节点，从而造成处理压力激增。详情请参阅 [事件参考](#event-reference) 中的 `respawn_guarded` 行。

### 拖拽删除与批量删除（控制面板）

控制面板在看板页面上提供了**回收站区域**——只需将任意任务卡片拖入该区域即可删除该任务，相关操作会级联影响到关联的 `task_events`、子链接及订阅项。系统还会通过确认提示防止误操作。此外，也可以通过 `DELETE /api/plugins/kanban/tasks` 接口进行批量删除，请求体需为 JSON 格式，内容为 `{"ids": ["t_abc", "t_def", ...]}`。

### 工作节点可见性接口

控制面板插件 API 现已为外部监控工具提供这些只读接口（以及一个用于运行控制的接口）：

| 接口地址 | 返回内容 |
|----------|----------|
| `GET /api/plugins/kanban/workers/active` | 当前正在运行的工作节点信息，包括进程 ID、配置文件、任务 ID、启动时间以及最近的心跳时间 |
| `GET /api/plugins/kanban/runs/{id}` | 单次运行详情，包括任务 ID、状态、开始/结束时间、退出码以及日志路径 |
| `POST /api/plugins/kanban/runs/{run_id}/terminate` | 终止可回收的运行任务——停止对应工作节点，并释放该任务以便重新派发 |
| `GET /api/plugins/kanban/inspect` | 调度器整体状态快照，包括待处理任务列表、进行中任务数量与 `max_in_progress` 阈值的对比情况，以及近期发生的事件 |

所有这些接口均受控于与看板插件 API 其他部分相同的认证机制。

### 看板集群拓扑结构辅助工具

`hermes kanban swarm` 能够一次性创建一个持久化的 **Kanban Swarm v1** 图结构：包括一个已完成的根节点/看板卡片、N 个并行工作的节点卡片、一个需要所有工作节点授权才能访问的验证节点卡片，以及一个需要验证节点授权才能访问的综合处理节点卡片。共享的集群上下文（即“看板”信息）会以结构化 JSON 形式的备注存储在根节点卡片上，因此任何工作节点均可读取这些信息。

```bash
hermes kanban swarm "Design a multi-region failover plan" \
  --workers researcher,architect,sre \
  --verifier reviewer --synthesizer writer
```

生成的图表能够正常分发——各个工作进程会并行运行，所有进程完成后验证器才会启动，而在验证器确认所有任务均无问题后，合成器才会开始工作。

## `/kanban` 斜杠命令 {#kanban-slash-command}

所有的 `hermes kanban <action>` 命令都可以通过 `/kanban <action>` 来执行——既可以在交互式的 `hermes chat` 会话中操作，也可以在任何网关平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、电子邮件、短信）上使用。这两种方式都会调用完全相同的 `hermes_cli.kanban.run_slash()` 函数，该函数会复用 `hermes kanban` 的命令行参数结构，因此 CLI、/kanban 接口以及 `hermes kanban` 命令的参数格式、标志选项和输出形式都保持一致。您无需离开聊天界面即可管理任务看板。

```
/kanban list
/kanban show t_abcd
/kanban create "write launch post" --assignee writer --parent t_research
/kanban comment t_abcd "looks good, ship it"
/kanban unblock t_abcd
/kanban dispatch --max 3
/kanban specify t_abcd                  # flesh out a triage one-liner into a real spec
/kanban specify --all --tenant engineering  # sweep every triage task in one tenant
```

多词参数的引用方式与在命令行shell中相同——`run_slash`会使用`shlex.split`来解析该行剩余内容，因此`"..."`和`'...'`两种形式均可使用。

### 运行中的使用：`/kanban`可绕过正在运行的智能体保护机制

通常情况下，当智能体仍在处理任务时，网关会将命令及用户消息暂存队列中——这正是为防止在当前任务尚未处理完成时就意外启动新任务的机制。**`/kanban`明确被排除在这一限制之外。** 该看板存储在`~/.hermes/kanban.db`文件中，而非正在运行的智能体状态中，因此无论是读取操作（如`list`、`show`、`context`、`tail`、`watch`、`stats`、`runs`）还是写入操作（如`comment`、`unblock`、`block`、`assign`、`archive`、`create`、`link`等），都能立即执行，即便是在任务处理过程中也是如此。

这正是实现二者分离的核心意义：

- 若某个工作节点因等待其他节点而阻塞，你只需通过手机发送`/kanban unblock t_abcd`指令，调度器便会在下一个时间节点继续处理该节点的任务。被阻塞的工作节点不会被打断，只是不再处于阻塞状态。
- 若发现某张任务卡需要人工补充说明，发送`/kanban comment t_xyz "请使用2026年的方案，而非2025年的"`即可将备注添加到任务讨论线程中，下次该任务重新启动时，就会在`kanban_show()`函数中读取到这些备注。
- 若想在不中断任务调度流程的情况下了解所有智能体的运行状态，可使用`/kanban list --mine`或`/kanban stats`来查看看板内容，而不会影响主对话的进行。

### `/kanban create`指令的自动订阅功能（仅限网关端）

当你通过网关使用`/kanban create "…"`创建任务时，发起该操作的聊天记录（包括平台类型、聊天ID及线程ID）会自动被订阅到该任务的终端事件通知中（如`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）。每当发生这些终端事件，你都会收到一条对应消息——在任务完成时甚至会包含工作节点结果摘要的第一行内容——无需手动轮询或记住任务ID即可随时掌握任务状态。

```
you> /kanban create "transcribe today's podcast" --assignee transcriber
bot> Created t_9fc1a3  (ready, assignee=transcriber)
     (subscribed — you'll be notified when t_9fc1a3 completes or blocks)

… ~8 minutes later …

bot> ✓ t_9fc1a3 completed by transcriber
     transcribed 42 minutes, saved to podcast/2026-05-04.md
```

一旦任务状态变为“已完成”或“已归档”，订阅便会自动取消。如果您使用 `--json` 参数通过脚本创建任务（即机器输出），则不会触发自动订阅——因为假设使用脚本的调用者希望通过 `/kanban notify-subscribe` 接口手动管理订阅。

### 消息中的输出截断

网关平台对消息长度设有实际限制。如果执行 `/kanban list`、`/kanban show` 或 `/kanban tail` 命令后生成的输出超过约 3800 个字符，响应内容将被截断，并在底部显示“…（已截断；请在终端中使用 \`hermes kanban …\` 查看完整内容）”的提示。而 CLI 接口则没有此类长度限制。

### 自动补全

在交互式 CLI 中，输入 `/kanban ` 后按 Tab 键，即可循环查看内置的子命令列表（`list`、`ls`、`show`、`create`、`assign`、`link`、`unlink`、`claim`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`、`dispatch`、`context`、`init`、`gc`）。上述 CLI 参考文档中列出的其他命令（`watch`、`stats`、`runs`、`log`、`assignees`、`heartbeat`、`notify-subscribe`、`notify-list`、`notify-unsubscribe`、`daemon`）同样可用——只是目前尚未出现在自动补全提示列表中。

## 协作模式

该看板无需新增任何功能即可支持以下八种协作模式：

| 模式 | 结构 | 示例 |
|---|---|---|
| **P1 发散式** | N 个同级成员，角色相同 | “同时从5个角度展开调研” |
| **P2 流水线式** | 角色链：侦察员 → 编辑者 → 撰写者 | 每日简报汇总流程 |
| **P3 投票/法定人数制** | N 个同级成员 + 1 名决策者 | 3名研究员 → 1名审稿人决定 |
| **P4 长期记录型** | 同一用户账号 + 共享目录 + 定时任务 | Obsidian 文档库 |
| **P5 人工干预式** | 工作者暂阻 → 用户评论 → 解除限制 | 面对模糊的决策时使用 |
| **P6 `@提及`** | 从正文直接路由至指定人员 | `@审稿人，请查看这个` |
| **P7 线程专属工作区** | 在特定线程中使用 `/kanban here` | 每个项目对应的独立线程 |
| **P8 批量管理式** | 一个用户账号，管理N个对象 | 50个社交账号 |
| **P9 分类指定器** | 初步想法 → 使用 `triage` → 再通过 `hermes kanban specify` 填充详细内容 → 转换为待办任务 | “将这条简短说明转化为结构化的任务” |

各模式的实际应用案例可见文档 `docs/hermes-kanban-v1-spec.pdf`。

## 多租户使用场景

当一个专业团队需要为多家企业提供服务时，可为每个任务添加租户标签：

```bash
hermes kanban create "monthly report" \
    --assignee researcher \
    --tenant business-a \
    --workspace dir:~/tenants/business-a/data/
```

工作节点会获取 `$HERMES_TENANT` 值，并通过前缀为内存写入数据添加命名空间。板面、调度器以及配置定义都是共享的，仅有数据会被限制在特定范围内。

## 网关通知功能

当您从网关（如 Telegram、Discord、Slack 等）执行 `/kanban create …` 命令时，发起该操作的聊天频道会自动被添加到新任务的订阅列表中。网关的后台通知机制会每隔几秒查询一次 `task_events`，针对每种终端事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）向对应聊天频道发送一条消息。对于已完成的任务，系统还会发送工作节点 `--result` 参数中的第一行内容，这样您无需再执行 `/kanban show` 命令即可查看任务结果。

您也可以通过 CLI 显式管理订阅关系——这对于那些由脚本或定时任务触发、但并非源自原有聊天频道的通知场景非常有用。

```bash
hermes kanban notify-subscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
hermes kanban notify-list
hermes kanban notify-unsubscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
```

一旦任务状态变为 `done` 或 `archived`，订阅便会自动取消，无需进行任何清理操作。

## 执行记录——每次尝试对应一行数据

任务是工作的逻辑单元，而**执行记录**则代表一次尝试执行该任务的操作。当调度器获取到可执行的任务时，它会在 `task_runs` 表中创建一行记录，并通过 `tasks.current_run_id` 指向该行。当此次尝试结束——无论是成功完成、被阻塞、崩溃、超时、启动失败还是被重新占用——该执行记录都会带有相应的 `outcome` 状态，并且任务对应的指针也会被清空。一个已被尝试过三次的任务，会在 `task_runs` 表中生成三行记录。

为何要使用两个表而非直接修改任务数据？因为在进行实际问题分析时，需要**完整的尝试历史记录**（例如“第二次审核成功通过，第三次则完成了合并”）；同时也需要一个专门的地方来存储每次尝试的元数据——比如哪些文件被修改、运行了哪些测试、审核人员记录了哪些发现。这些都属于执行相关的信息，而非任务本身的信息。

**结构化交接**功能也体现在执行记录中。当某个工作节点通过 `kanban_complete()` 完成任务时，它可以传递以下信息：

- `summary`（工具参数）/ `--summary`（CLI命令行参数）——用于人工交接；该内容会存储在对应执行记录中，下游的工作节点可在其 `build_worker_context` 中查看。
- `metadata`（工具参数）/ `--metadata`（CLI命令行参数）——以自由格式的 JSON 字典形式存储在执行记录中；下游节点会看到与摘要一起序列化后的这些数据。
- `result`（工具参数）/ `--result`（CLI命令行参数）——简短的日志行，会显示在任务记录中（这是一个旧字段，为保持向后兼容而保留）。

下游工作节点会读取每个父任务的最新已完成执行记录中的摘要和元数据。重新尝试的任务处理节点则会查看自己任务之前的所有尝试记录（包括结果、摘要和错误信息），从而避免重复走已经失败过的流程。

```
# What a worker actually does — a tool call, from inside the agent loop:
kanban_complete(
    summary="implemented token bucket, keys on user_id with IP fallback, all tests pass",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
    result="rate limiter shipped",
)
```

当您（人类操作员）需要处理工人无法完成的任务时，也可以通过 CLI 实现同样的交接流程——例如被放弃的任务，或是您在控制面板中手动标记为已完成的任务。

```bash
hermes kanban complete t_abcd \
    --result "rate limiter shipped" \
    --summary "implemented token bucket, keys on user_id with IP fallback, all tests pass" \
    --metadata '{"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14}'

# Review the attempt history on a retried task:
hermes kanban runs t_abcd
#   #  OUTCOME       PROFILE           ELAPSED  STARTED
#   1  blocked       worker               12s  2026-04-27 14:02
#        → BLOCKED: need decision on rate-limit key
#   2  completed     worker                8m   2026-04-27 15:18
#        → implemented token bucket, keys on user_id with IP fallback
```

运行记录会显示在控制面板中（抽屉内的“运行历史”板块，每次尝试对应一行彩色条目），也会通过 REST API 提供（`GET /api/plugins/kanban/tasks/:id` 会返回 `runs[]` 数组）。通过 `PATCH /api/plugins/kanban/tasks/:id` 并传入 `{status: "done", summary, metadata}` 可同时将这些信息传递给内核，因此控制面板中的“标记为已完成”按钮功能等同于 CLI 操作。`task_events` 行会包含所属的 `run_id`，以便界面按尝试次数对事件进行分组；而 `completed` 事件会在其负载中嵌入简短摘要（长度限制为 400 字符），这样网关通知器无需再次发起 SQL 查询即可呈现结构化的任务交接信息。

**批量关闭的注意事项。** 命令 `hermes kanban complete a b c --summary X` 会被拒绝——因为结构化交接是针对单次运行的，所以将同一摘要复制到多个任务上几乎总是错误的。不过，在常见的“我已完成一批管理任务”场景下，不使用 `--summary`/`--metadata` 参数的批量关闭仍然有效。

**因状态变化而回收的运行记录。** 如果你在控制面板中将正在运行的任务从“运行中”状态拖动回“待处理”或直接移至“待办”，或者归档了仍在运行的任务，该正在处理的运行记录将以 `outcome='reclaimed'` 的状态关闭，而不会成为孤立记录。当 `tasks.current_run_id` 为 `NULL` 时，`task_runs` 行始终处于终止状态，反之亦然——这一规则在 CLI、控制面板、调度器及通知器中均保持一致。

**针对从未被认领的已完成任务的合成运行记录。** 如果完成或阻塞了一个从未被认领的任务（例如，有人通过控制面板为“待处理”状态的任务添加摘要后将其标记为已完成，或是 CLI 用户执行 `hermes kanban complete <ready-task> --summary X`），否则任务交接信息就会丢失。此时内核会插入一条时长为零的运行记录（`started_at == ended_at`），其中包含摘要、元数据及原因，从而确保尝试历史记录的完整性。`completed`/`blocked` 事件的 `run_id` 即指向该条记录。

**实时抽屉刷新功能。** 当控制面板的 WebSocket 事件流报告用户当前查看的任务有新事件时，抽屉会自动重新加载（通过在其 `useEffect` 依赖列表中加入针对每个任务的事件计数器实现）。无需再次关闭和打开抽屉，即可查看运行记录的新行或更新后的状态。

### 向前兼容性

在 `tasks` 表中预留了两列可为空的字段，用于 v2 工作流路由：`workflow_template_id`（表示该任务所属的模板）和 `current_step_key`（表示该模板中当前处于激活状态的步骤）。v1 内核在路由时会忽略这些字段，但允许客户端写入它们，因此 v2 版本可以在无需再次修改表结构的情况下添加路由功能。

## 事件参考

每次状态变更都会在 `task_events` 表中新增一行记录。每行记录可选地包含 `run_id`，以便界面按尝试次数对事件进行分组。事件类型可分为三类，便于过滤（例如：`hermes kanban watch --kinds completed,gave_up,timed_out`）：

**生命周期事件**（描述任务作为逻辑单元的状态变化）：

| 类型 | 载荷内容 | 触发时机 |
|---|---|---|
| `created` | `{assignee, status, parents, tenant}` | 任务被创建时。此时 `run_id` 为 `NULL`。 |
| `promoted` | — | 当所有父任务都标记为“已完成”时，任务从“待处理”转为“待处理”。此时 `run_id` 为 `NULL`。 |
| `claimed` | `{lock, expires, run_id}` | 调度器原子性地认领了一个“待处理”任务以启动工作进程。 |
| `completed` | `{result_len, summary?}` | 工作进程通过 `--result`/`--summary` 参数提交结果且任务状态变为“已完成”。`summary` 为简短交接信息（长度限制 400 字符）；完整版本存储在对应运行记录行中。如果对从未被认领且包含交接字段的任务调用 `complete_task`，系统会生成一条时长为零的运行记录，确保 `run_id` 仍有指向。 |
| `blocked` | `{reason}` | 工作进程或人工将任务状态改为“已阻塞”。若对从未被认领的任务并传入 `--reason` 参数，系统也会生成一条时长为零的运行记录。 |
| `unblocked` | — | 任务从“已阻塞”转为“待处理”，可能是手动操作或通过 `/unblock` 命令实现。此时 `run_id` 为 `NULL`。 |
| `archived` | — | 该任务在默认看板中不可见。如果任务仍在运行，其 `run_id` 将指向因状态变化而被回收的对应运行记录。 |

**编辑事件**（由人工发起的非状态变更操作）：

| 类型 | 载荷内容 | 触发时机 |
|---|---|---|
| `assigned` | `{assignee}` | 任务负责人发生变化（包括解除分配）。 |
| `edited` | `{fields}` | 任务的标题或内容被修改。 |
| `reprioritized` | `{priority}` | 任务的优先级发生改变。 |
| `status` | `{status}` | 通过控制面板的拖放操作直接修改了任务状态（例如从“待处理”转为“待处理”）。在从“运行中”状态拖动任务时，该行的 `run_id` 将指向被回收的运行记录；否则为 `NULL`。 |

**工作进程遥测事件**（描述执行过程，而非任务本身的逻辑状态）：

| 类型 | 载荷内容 | 触发时机 |
|---|---|---|
| `spawned` | `{pid}` | 调度器成功启动了一个工作进程。 |
| `heartbeat` | `{note?}` | 在长时间运行的操作期间，工作进程会调用 `hermes kanban heartbeat $TASK` 以报告自身仍在运行。 |
| `reclaimed` | `{stale_lock}` | 任务认领的超时时间到期且未完成，此时任务状态将恢复为“待处理”。 |
| `crashed` | `{pid, claimer}` | 工作进程的 PID 已失效，但其超时时间尚未到期。 |
| `timed_out` | `{pid, elapsed_seconds, limit_seconds, sigkill}` | 任务运行时间超过了 `max_runtime_seconds` 的限制；调度器首先发送 SIGTERM 信号（5 秒宽限期后发送 SIGKILL），然后将该任务重新加入队列。 |
| `stale` | `{elapsed_seconds, last_heartbeat_at, heartbeat_age_seconds, timeout_seconds, pid, terminated}` | 任务运行时间超过了 `kanban.dispatch_stale_timeout_seconds` 的默认值（4 小时），且过去一小时内没有收到任何 `kanban_heartbeat` 信号。调度器会终止本地工作进程（如果存在），并将任务状态重置为“待处理”以重新调度。该事件不会增加失败计数——它属于调度器端的缺失检测，而非工作进程故障。执行长时间操作的进程应至少每小时调用一次 `kanban_heartbeat` 以避免此问题。 |
| `respawn_guarded` | `{reason}` | 调度器决定暂不重新启动该“待处理”任务。原因可能包括：`blocker_auth`（上一次失败是由于配额/认证/429 错误——需等待速率限制窗口重置）、`recent_success`（过去一小时内已有任务完成——需先进行审核后再尝试重新运行）、`active_pr`（最近有评论中提到了 GitHub PR 链接——已有工作进程在处理该 PR）。此时任务仍保持“待处理”状态，下次调度时将获得再次启动的机会。如果导致该状态的条件持续存在，正常的“连续失败”断路器机制将在出现 `failure_limit` 次失败后自动触发 `gave_up` 状态。 |
| `spawn_failed` | `{error, failures}` | 一次启动尝试失败（例如路径缺失、工作区无法挂载等）。失败计数器会增加，任务将返回“待处理”状态以便重新尝试。 |
| `protocol_violation` | `{pid, claimer, exit_code}` | 任务仍处于“运行中”状态时，工作进程已正常退出，通常是因为它在没有调用 `kanban_complete` 或 `kanban_block` 的情况下就结束了操作。调度器也会立即触发 `gave_up` 状态并自动阻止该任务，而不会尝试重新启动。 |
| `gave_up` | `{failures, effective_limit, limit_source, error}` | 在连续 N 次非成功尝试后，断路器被触发。任务将携带最后一次出现的错误自动进入阻塞状态。有效的限制顺序为：先考虑任务的 `max_retries` 值，其次是调度器的 `failure_limit`/`kanban.failure_limit` 值，最后才是默认值。 |

命令 `hermes kanban tail <id>` 可查看单个任务的这些事件记录。而命令 `hermes kanban watch` 则可实时监控整个看板中的所有事件。

## 不支持的功能

Kanban 系统刻意设计为单主机运行模式。`~/.hermes/kanban.db` 是一个本地的 SQLite 文件，调度器也在同一台机器上启动工作进程。目前不支持在多台主机之间共享看板——因为该系统没有用于协调“主机 A 上的工作进程 X、主机 B 上的工作进程 Y”这种场景的机制，且崩溃检测逻辑也假设 PID 是主机本地唯一的。如果需要多主机部署，建议为每台主机单独运行一个看板，并通过 `delegate_task` 或消息队列来实现各看板之间的数据交互。

## 设计规范

完整的系统设计文档——包括架构设计、并发正确性分析、与其他系统的对比、实施计划、潜在风险及未解决的问题——均保存在 `docs/hermes-kanban-v1-spec.pdf` 文件中。在提交任何涉及行为变更的 Pull Request 之前，请先仔细阅读该文档。
