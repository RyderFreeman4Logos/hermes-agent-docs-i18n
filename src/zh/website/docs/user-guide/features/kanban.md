---
sidebar_position: 12
title: "Kanban (Multi-Agent Board)"
description: "Durable SQLite-backed task board for coordinating multiple Hermes profiles"
---

# Kanban — 多智能体任务协作功能

> **需要操作指南？**请阅读[Kanban教程](./kanban-tutorial)——其中包含四个用户场景（单人开发、批量任务处理、带重试机制的角色流水线、断路器机制），并附有每个场景的仪表板截图。本页面为参考资料，而教程则提供了完整的操作说明。

Hermes Kanban是一种持久化的任务看板，可在您的所有Hermes账户间共享，让多个已命名的智能体协同处理任务，而无需依赖那些稳定性较差的临时子智能体集群。每个任务都对应`~/.hermes/kanban.db`文件中的一行数据；每次任务交接都会生成一行可供所有人读写的记录；每个工作进程都是拥有独立身份的完整操作系统进程。

### 迭代次数上限前的完成检查点

由调度器管理的智能体，在其有限的迭代预算使用量接近90%时，会收到一次检查点通知，该通知会与最新的工具处理结果一同保存，同时系统仍会保留其他可执行工具的调用机会。您可以通过`agent.budget_warning_ratio`参数来设置更早的警告阈值：预算较少的智能体会在其倒数第二次迭代之前就收到警告；而仅执行一次迭代的智能体则没有前置的检查点窗口。该通知会在下一次请求之前被保存在会话记录中。智能体应在确认任务要求后才会调用`kanban_complete`函数，或者先留下进度备注后再继续工作。仅通过提交代码或生成差异对比，绝不能自动完成一个任务。

硬上限、无需工具的最终汇总功能以及连续失败断路器设置均保持不变：那些仍耗尽预算的 Worker 依然会受到次数限制的重试约束。这仅是一种提醒机制，并不能保证模型一定会理会该通知。普通对话及被委托的子任务不会自动继承 Kanban 检查点功能，其迭代警告仍需手动开启。

### 两种交互方式：模型通过工具进行操作，用户则通过 CLI 指令操作

该看板拥有两个入口，二者都基于同一个 `~/.hermes/kanban.db` 数据文件：

- **Agent 通过专用的 `kanban_*` 工具集来操控看板**——包括 `kanban_show`、`kanban_list`、`kanban_complete`、`kanban_request_review`、`kanban_request_changes`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_attach`、`kanban_attach_url`、`kanban_attachments`、`kanban_create`、`kanban_link`、`kanban_unblock` 等。调度器在为每个 Worker 初始化架构时会预置这些工具；编排器配置也可明确启用 `kanban` 工具集。模型通过直接调用这些工具来读取和分配任务，而非通过执行 `hermes kanban` 命令。详情请参阅下文的[Worker 如何与看板交互](#how-workers-interact-with-the-board)。
- **用户（以及脚本和 cron 任务）则通过 CLI 中的 `hermes kanban …` 命令、斜杠命令 `/kanban …`，或是控制面板来操控看板**。这些方式适用于人类操作及自动化流程——即那些没有背后模型负责调用工具的场景。
这两个界面均通过相同的 `kanban_db` 层进行数据传输，因此读取操作能够获得一致的结果，同时写入操作也不会出现偏差。本页其余部分展示了 CLI 示例，因其便于复制粘贴；但实际上，每个 CLI 命令都对应着模型所使用的工具调用功能。

以下是 `delegate_task` 功能无法处理的工作负载类型：

- **研究分类处理**——需要并行开展工作的研究人员、分析人员与撰写人员，且需人工介入监督。
- **定时操作**——每日重复执行的任务，通过数周时间逐步形成报告文档。
- **数字孪生系统**——具有固定名称的持久化助手（如 `inbox-triage`、`ops-review`），能够随着时间积累相关数据。
- **工程开发流程**——包括分解任务 → 在并行工作流中实施 → 审核 → 反复迭代 → 提交 Pull Request 的完整流程。
- **团队协作管理**——由一名专家同时管理多个对象（如50个社交账号、12个需监控的服务）。

如需了解完整的设计理念、与 Cline Kanban / Paperclip / NanoClaw / Google Gemini Enterprise 的对比分析，以及八种典型的协作模式，请查阅仓库中的 `docs/hermes-kanban-v1-spec.pdf` 文件。

## Pull Request 完成契约

在创建 Pull Request 时，可使用 `--completion-contract OWNER/REPO` 参数指定完成契约（对于已有的任务，则可提供精确的 `https://github.com/OWNER/REPO/pull/123` 链接）。`kanban_create` 函数也支持相同的完成契约参数。若需执行纯本地操作，可使用 `local-only` 参数；未指定契约的现有卡片将保持默认设置。文本格式的链接并不在规范范围内。

在完成发布后，需将 `metadata.published_pr` 传递给完成流程。首个匹配的 URL 会永久绑定该卡片；重复尝试无法替代已通过的 PR。CLI 命令 `show --json` 与 `kanban_show` 可用于查看已持久化的配置信息。

统一的 `complete_task` 流程涵盖了工作工具使用、CLI 操作、审核批准以及仪表板状态更新等环节。该流程会读取传统的分支保护机制及当前生效的规则集所需上下文，对具体的 HEAD 检查运行记录及旧版状态进行分页处理，随后重新读取 PR 的 HEAD 和 BASE 分支信息。可选的失败/跳过相关监测数据不会影响那些已通过且属于必做检查的项目。若缺少、处于待处理状态、检测失败、已被取消、超时、数据过期、被跳过或状态为中立的**必做**验证依据，均无法完成该卡片。同样，零次运行即通过、策略内容不可读或 GitHub API 出现故障，也会导致流程无法继续。那些不包含必做检查的仓库则仅需使用本地配置文件即可。执行该操作时，`gh` 工具必须已获得对该仓库检查项及规则的读取权限；此流程不会执行任何远程写入操作。

若审核被拒，相关卡片和工作空间仍会保留。持久的 `pr_acceptance` 事件会存储 PR 的 URL、SHA 值、所需上下文、检查项的 ID/URL、分类信息以及恢复指南；`last_failure_error` 则会显示下一步该采取的操作。可先修复故障、重新运行基础设施检查或稍作等待，之后再尝试完成流程。当需要人工干预时，可使用 `kanban_block` 命令。GitHub 系统返回的普通“失败”信息无法区分是测试失败还是上传文件出错，需查看其保留的 URL 详情。明确的基础设施检测结论与 API 错误会被分别记录。此外，该流程不会启动额外的工作进程。

在同一个 SQLite 锁的约束下，收据持久化以及终端写入的重新检查、运行状态和合约所有权管理：已被回收的 Worker 无法完成新任务或为其添加确认状态。GitHub 的最终读取仅作为任务完成时的快照，并非分布式事务，也不具备任务完成后的持续监控功能。这属于单用户生命周期保护机制，而非针对任意直接数据库写入操作的操作系统级隔离措施。GitHub Enterprise 不在此保障范围内。相关发布/生命周期相关工作可参见：#91230、#84254、#52311；仅通过本地验证和发布操作并不能视为远程确认。

## Kanban 与 `delegate_task` 的区别

二者外观相似，但并非相同的底层机制。

| | `delegate_task` | Kanban |
|---|---|---|
| 形式 | RPC 调用（分叉 → 合并） | 持久消息队列 + 状态机 |
| 父任务行为 | 需等待子任务返回后才继续执行 | 执行 `create` 后即视为已发送，无需关注后续结果 |
| 子任务身份 | 匿名子 Agent | 具有持久内存的命名配置文件 |
| 可恢复性 | 无——失败即终止 | 遇到阻塞则解除阻塞后重新运行；发生崩溃则回收资源 |
| 是否需要人工干预 | 不支持 | 可随时通过评论或解除阻塞进行干预 |
| 每个任务对应的 Agent 数量 | 一次调用仅对应一个子 Agent | 任务整个生命周期内可涉及多个 Agent（用于重试、审核、跟进等） |
| 审计追踪 | 在上下文压缩后会丢失 | 数据永久存储在 SQLite 的持久行中 |
| 协调方式 | 层级式（调用方 → 被调用方） | 对等式——任何配置文件均可读取/修改任意任务 |

**一句话概括区别：** `delegate_task` 是一种函数调用方式，而 Kanban 则是一个工作队列，其中的每一次任务交接都会生成一条记录，任何配置文件或人工都可以查看和编辑这些记录。

**何时使用 `delegate_task`**：当父代理在继续处理前需要一个简短的推理结果，且无需人工干预，同时该结果会返回到父代理的上下文中时。

**何时使用看板机制**：当任务需要跨代理处理、需在重启后仍保留状态、可能需要人工输入、可能由其他角色接手，或需要在事后可被检索到时。

这两种机制可以共存：看板中的工作节点在其运行过程中可在内部调用 `delegate_task`。

## 核心概念

- **看板**——一个独立的任务队列，拥有自己的 SQLite 数据库、工作空间目录以及调度循环。单个安装版本可以包含多个看板（例如每个项目、代码仓库或领域一个看板）；详情请参见下文的[多项目看板](#boards-multi-project)。仅使用单个项目的用户将始终处于 `default` 看板中，在本文档以外的地方不会见到“看板”一词。
- **任务**——包含标题、可选正文、一名负责人（即个人资料名称）、状态（`triage | todo | ready | running | blocked | review | done | archived`）、可选的租户命名空间以及可选的幂等性键（用于避免重复执行自动化任务）的记录行。
- **链接**——记录父任务与子任务之间依赖关系的 `task_links` 行。当所有父任务的状态均为 `done` 时，调度器会将任务状态从 `todo` 提升为 `ready`。
- **评论**——用于代理间通信的协议。代理和人类用户均可添加评论；当工作节点被重新生成时，它会将完整的评论记录作为上下文的一部分进行读取。
- **工作空间**——工作节点所操作的目录。共有三种类型：
- `scratch`（默认值）——位于 `~/.hermes/kanban/workspaces/<id>/` 下的临时目录（在非默认看板中则位于 `~/.hermes/kanban/boards/<slug>/workspaces/<id>/`）。**任务完成后会被删除**——按设计，scratch 目录是临时的。通过 `kanban_complete(artifacts=[...])` 明确指定的文件会在清理之前被复制到持久化的任务附件存储中；传统完成摘要中的现有交付物路径也会得到相同处理，其余的 scratch 文件则会被移除。如果未指定任何 scratch 文件，任务将保持处理中状态，以便工作节点可以修正路径并重新尝试。当需要确保整个工作空间始终可用时，可使用 `worktree:` 或 `dir:<path>` 参数。在首次安装时创建 scratch 工作空间时，调度器会记录警告，并在任务上触发 `tip_scratch_workspace` 事件（可通过 `hermes kanban show <id>` 查看）。

- `dir:<path>`——一个现有的共享目录（如 Obsidian 保险库、邮件操作目录或按账户划分的文件夹）。**必须是绝对路径**。像 `dir:../tenants/foo/` 这样的相对路径会在调度阶段被拒绝，因为它们会根据调度器所处的当前工作目录来解析，而这极易导致歧义，也可能成为攻击手段。除此之外，该路径是可信的——这是你的目录，属于你的文件系统，工作节点是以你的用户身份运行的。这属于“可信本地用户”威胁模型；Kanban 按设计为单主机架构。**任务完成后该目录内容会被保留**。
- `worktree` — 用于编码任务的 Git 工作树，路径位于 `.worktrees/<id>/` 下。可通过 `worktree:<path>` 指定确切的目标路径。工作节点端的 `git worktree add` 命令会创建该工作树，若指定了 `--branch` 参数则会使用该分支。**任务完成后该工作树仍会被保留。**

- **Dispatcher** — 一个长期运行的循环进程，每隔 N 秒（默认为 60 秒）执行以下操作：回收已过期的任务请求、恢复崩溃的工作节点（即进程 ID 已消失但超时时间尚未到期）、将就绪的任务提升到处理队列、以原子方式获取任务权限并启动对应的处理进程。该进程默认在网关内部运行（`kanban.dispatch_in_gateway: true`）。每个循环周期内，一个 Dispatcher 会处理所有看板中的任务；为确保工作节点不会看到其他看板，它们会在启动时被设置为仅关注 `HERMES_KANBAN_BOARD`。如果同一任务连续出现 `kanban.failure_limit` 次启动失败（默认为 2 次），Dispatcher 会自动以最后一次错误作为原因阻止该任务的进一步处理——从而避免因处理进程配置缺失、工作空间无法挂载等问题导致的系统混乱。

- **Tenant** — 看板内部可选的字符串命名空间。一个专家团队可以通过工作空间路径和内存键前缀实现数据隔离，从而为多个企业（如 `--tenant business-a`）提供服务。Tenant 属于软性隔离机制，而看板才是真正的硬性隔离边界。

## 看板（多项目）

看板功能可将不同类型的工作流——每个项目、仓库或业务领域对应一个工作流——分隔到独立的队列中。新安装的 Hermes 版本仅包含一个名为 `default` 的看板（为兼容旧版本，数据存储在 `~/.hermes/kanban.db` 中）。仅需处理单一工作流的用户无需了解看板功能，该功能为可选配置。

每个看板之间是完全隔离的：

- 每个看板拥有独立的 SQLite 数据库（路径为 `~/.hermes/kanban/boards/<slug>/kanban.db`）。
- 分别设置独立的 `workspaces/` 和 `logs/` 目录。
- 为某个任务生成的 Worker **仅**能查看其所在看板的任务——调度器会在子进程环境中设置 `HERMES_KANBAN_BOARD` 变量，而 Worker 可使用的所有 `kanban_*` 工具都会读取该变量值。
- 不允许在多个看板之间关联任务（这样可保持架构简洁；如果确实需要跨项目引用，可使用自由文本提及方式，并通过 ID 手动查找）。

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

看板决议顺序（优先级从高到低）如下：

1. 在 CLI 命令中明确指定 `--board <slug>` 参数。
2. 环境变量 `HERMES_KANBAN_BOARD`（由调度器在启动工作节点时设置，因此工作节点无法查看其他看板）。
3. `~/.hermes/kanban/current`——由 `hermes kanban boards switch` 命令保存的看板标识符。
4. 默认值。

看板标识符需符合规范：仅包含小写字母、数字、连字符和下划线，长度为 1 至 64 个字符，且必须以字母或数字开头。输入的大写字符会自动转换为小写。任何其他字符（如斜杠、空格、点号、`..` 等）都会在 CLI 层被拒绝，从而防止通过路径遍历技巧来指定非法看板名称。

### 通过控制面板管理看板

当存在多个看板（或任意看板中有任务）时，`hermes dashboard` 的看板标签页顶部会显示一个看板切换器。仅使用单个看板的用户只能看到一个小的“+ 新建看板”按钮；只有在需要切换看板时，该切换器才会显示出来。

- **看板下拉菜单** — 用于选择当前使用的看板。您的选择会被保存在浏览器的 `localStorage` 中，因此即使重新加载页面，该设置依然有效，同时也不会导致 CLI 的 `current` 指针跳转到您之前未关闭的终端之外的其他看板。
- **+ 新建看板** — 会弹出模态框，要求输入看板标识、显示名称、描述以及图标。还可以选择自动切换到新创建的看板。
- **设置** — 会打开一个模态框，用于编辑当前看板的显示名称、描述以及**项目目录**（即 `default_workdir`）。项目目录是每个新任务默认继承的看板级工作空间（Git 仓库对应保留的 worktree，普通目录则对应保留的目录）；不过每创建一个任务时仍可对其进行覆盖。清空该字段则会使新任务使用临时的、可丢弃的工作空间。
- **归档** — 仅显示在非 `default` 类型的看板上。确认操作后，该看板的目录会被移至 `boards/_archived/` 目录下。

所有的控制台 API 接口都支持通过 `?board=<slug>` 参数来限定操作范围。事件 WebSocket 在连接时会绑定到特定的看板；若在用户界面中切换看板，则会为新的看板建立一个新的 WebSocket 连接。

## 文件附件

任务可以附带文件附件——如 PDF、图片、源代码文档等——这样工作者就能直接获取所需的素材，而无需您在消息内容中手动粘贴文件路径并指望系统能找到它们。

- **上传** — 在控制面板抽屉中打开任务，然后使用“附件”板块中的*上传文件*按钮（可一次性上传多个文件）。每次上传的文件大小上限为25 MB。  
- **存储位置** — 对于默认看板，文件将存储在`<hermes-home>/kanban/attachments/<task_id>/`路径下；而对于已命名的看板，则存储在`<hermes-home>/kanban/boards/<slug>/attachments/<task_id>/`路径下。如需指定自定义存储位置，可设置`HERMES_KANBAN_ATTACHMENTS_ROOT`环境变量。  
- **工作者的查看方式** — 当调度器将任务分配给工作者后，其工作上下文中会包含一个“附件”板块，列出每个文件的名称及其**绝对路径**。由于工作者拥有完整的文件操作及终端工具访问权限，因此可直接读取附件（通过`read_file`函数或`pdftotext`等Shell工具）。  
- **下载/删除** — 抽屉中会显示每个附件，并提供下载链接及删除（×）按钮。删除附件会同时移除对应的元数据记录及磁盘上的文件。

:::note 远程终端后端  
对于看板工作者而言，其默认使用的本地终端后端可直接解析附件路径。若在远程后端（如Docker、Modal）上运行工作者，则需将看板的`attachments/`目录挂载到工作环境中的沙箱中，这样才能让工作者的上下文能够访问到这些文件的绝对路径。  
:::


## 快速入门

以下命令是由**您**（即人类操作者）来设置看板并创建任务的。一旦任务被分配，调度器便会将对应的配置文件启动为工作节点，之后便由**模型通过 `kanban_*` 工具调用而非 CLI 命令来推进任务处理**——详情请参阅[工作节点如何与看板交互](#how-workers-interact-with-the-board)。

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

当调度器选中 `t_abcd` 并创建 `researcher` 角色配置后，工作节点模型首先会调用 `kanban_show()` 函数来获取自身的任务，而不会执行 `hermes kanban show t_abcd` 这样的命令。

### 内嵌在网关中的调度器（默认配置）

该调度器运行在网关进程内部。无需进行任何安装，也没有独立的服务需要管理——只要网关处于运行状态，符合条件的任务就会在下一个时间间隔（默认为60秒）被处理。

```yaml
# config.yaml
kanban:
  dispatch_in_gateway: true        # default
  dispatch_interval_seconds: 60    # default
  review_dispatch: true            # default: spawn the assigned profile with
                                   # the bundled sdlc-review skill. Set false
                                   # for human-only review boards.
```

为便于调试，可通过设置 `HERMES_KANBAN_DISPATCH_IN_GATEWAY=0` 在运行时覆盖该配置参数。此时仍会遵循标准的网关监控机制：可直接执行 `hermes gateway start` 命令，或将其作为 systemd 用户单元进行集成（详情请参阅网关相关文档）。若没有正在运行的网关，处于“准备中”状态的任务将保持原位，直至有网关启动——`hermes kanban create` 命令在创建任务时会对此情况发出警告。

以独立进程形式运行 `hermes kanban daemon` 的方式现已**废弃**，建议使用网关功能。如果确实无法运行网关（例如无头主机策略禁止运行长生命周期服务等），可使用 `--force` 参数让旧的独立守护进程在单个版本周期内继续运行，但同时针对同一个 `kanban.db` 文件既使用嵌入在网关中的调度器又使用独立守护进程会导致数据竞争问题，此类用法是不被支持的。

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

:::note 未阻塞任务的处理去向  
`unblock` 命令会恢复任务的安全状态阶段：对于父任务已完成的审核类工作，其状态为 **`review`**；对于父任务已完成的实现类工作，状态为 **`ready`**；只要存在未完成的父任务，状态则为 **`todo`**。处于 `todo` 状态的任务会保留其原始状态，并在依赖关系解除后自动恢复为 `review` 或 `ready` 状态。`unblock` 命令绝不会直接将任务发送至 `triage` 状态。  

如果执行了 `unblock` 操作后，任务仍出现在 **`triage`** 状态，那么导致该状态的并非最初的解封操作，而是之后因相同原因再次进行的阻塞操作：当一个任务因相同原因被阻塞、解封后又再次被阻塞，达到 `BLOCK_RECURRENCE_LIMIT` 次（默认值为 `2`）时，系统会停止将其退回 `blocked` 状态——因为若使用定时任务，则会不断尝试解封它——而是将其转至 `triage` 状态，由人工进行决策。这是一种基于数据库的确定性保护机制，而非大型语言模型的主观判断，且任务的文本内容无法规避此规则：重复计数器会在每次解封后依然保留（仅在工作成功完成时才会重置）。若希望让已解封的任务继续留在工作池中，应在解封之前解决“为何任务会反复被阻塞”的问题（如父任务未完成、缺少输入数据或能力不足），或者如果预计会出现此类循环，则可以提高 `BLOCK_RECURRENCE_LIMIT` 的值。  
:::

## 工作人员如何与任务看板交互

**Worker 并无需使用 `hermes kanban` 命令行工具。** 当调度器创建 Worker 时，它会将 `HERMES_KANBAN_TASK=t_abcd` 设置在子进程的运行环境中，这一环境变量会激活模型架构中的专用 **看板工具集**。对于那些在工具集配置中启用了 `kanban` 功能的协调者角色，同样可以使用该工具集。这些工具与 CLI 一样，均通过 Python 的 `kanban_db` 层直接读取和修改看板数据。正在运行的 Worker 可以像使用其他工具一样调用这些功能，它无需了解也不需要使用 `hermes kanban` 命令行工具。

| Tool | Purpose | Required params |
|---|---|---|
| `kanban_show` | Read the current task (title, body, prior attempts, parent handoffs, comments, full pre-formatted `worker_context`). Defaults to the env's task id. | — |
| `kanban_list` | List task summaries with filters for `assignee`, `status`, `tenant`, archived visibility, and limit. Intended for orchestrators discovering board work. | — |
| `kanban_complete` | Finish with `summary` + `metadata` structured handoff. | at least one of `summary` / `result` |
| `kanban_request_review` | Start same-card review with a durable `summary`, optional `metadata`, and optional reviewer profile. The task moves to `review`; this is not a block. | `summary` |
| `kanban_request_changes` | Reviewer verdict from an active review run. Closes that run, reapplies parent gating, and routes the task to its original implementer without block-loop accounting. | `reason` |
| `kanban_block` | Stop work and route by why: `kind=dependency` (waits in `todo`, auto-resumes), `needs_input`/`capability`/`transient` (surface to a human). Repeated same-kind re-blocks auto-escalate to `triage`. | `reason` |
| `kanban_heartbeat` | Signal liveness during long operations. Pure side-effect. | — |
| `kanban_comment` | Append a durable note to the task thread. | `task_id`, `body` |
| `kanban_attach` | Attach a file to a task by passing its bytes inline (base64); stored under the task's attachments dir (25 MB cap). | file bytes + name |
| `kanban_attach_url` | Attach a file to a task by URL. | `url` |
| `kanban_attachments` | List a task's attachments. | — |
| `kanban_create` | (Orchestrators) fan out into child tasks with an `assignee`, optional `parents`, `skills`, etc. | `title`, `assignee` |
| `kanban_link` | (Orchestrators) add a `parent_id → child_id` dependency edge after the fact. | `parent_id`, `child_id` |
| `kanban_unblock` | (Orchestrators) restore a blocked task to its source phase (`review` or `ready`), or `todo` while a parent remains open. | `task_id` |

一个典型的 Worker 运行周期如下所示：

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

这些用于处理外部任务的“(Orchestrators)”工具——即 `kanban_list`、`kanban_create`、`kanban_link`、`kanban_unblock` 以及 `kanban_comment`——均属于同一套工具集。其设计规范（体现在自动注入的看板操作指南中）是：工作节点角色不会分散处理或路由无关任务，而调度器角色则不会执行具体的实现工作。由调度器创建的工作节点在执行会改变任务状态的生命周期操作时仍受任务范围限制，无法修改其他无关任务。

### 为何使用工具而非直接调用 `hermes kanban`？

主要有三个原因：

1. **后端兼容性**：那些终端工具指向远程后端（如 Docker / Modal / Singularity / SSH）的工作节点，需要在容器内部运行 `hermes kanban complete` 命令，而该环境中并未安装 `hermes`，也无法挂载 `~/.hermes/kanban.db` 文件。相比之下，看板工具在代理自身的 Python 进程中运行，因此无论终端后端为何，都能正常访问 `~/.hermes/kanban.db`。

2. **避免 shell 引用问题**：通过 shlex + argparse 传递参数如 `--metadata '{"files": [...]}'` 存在潜在风险。而结构化的工具参数则完全避免了这一问题。

3. **更清晰的错误信息**：工具返回的是结构化的 JSON 数据，模型可以对其进行解析处理；而直接通过标准错误流输出的字符串则需额外解析，且可读性较差。
**在普通会话中不会产生任何架构冗余。** 正常的 `hermes chat` 会话在其架构中不会包含任何 `kanban_*` 工具，除非当前激活的配置文件明确启用了用于任务协调的 `kanban` 工具集。由调度器创建的任务工作节点会因设置了 `HERMES_KANBAN_TASK` 而获得与任务相关的工具；而协调者配置文件则可通过相应设置获得更完善的路由功能。对于从不使用看板功能的用户而言，系统不会带来任何不必要的工具负担。

系统会自动注入看板操作指引，告诉模型何时以及按何种顺序调用相应工具。

### 推荐的交接信息格式

`kanban_complete(summary=..., metadata={...})` 的设计具有高度灵活性：
`summary` 部分是供人类阅读的总结内容，而 `metadata` 则是机器可读取的交接数据，下游的智能体、审核人员或仪表板无需解析文本即可直接复用这些数据。

对于工程任务和审核任务，建议采用这种可选的元数据结构：

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

这些键仅属于约定俗成，并非架构规范所强制要求。其优势在于，每个工作节点都会留下足够的线索，便于后续处理者快速回答以下四个问题：

1. 发生了什么变化？
2. 是如何进行验证的？
3. 若任务失败，有哪些方法可以解决或重新尝试？
4. 哪些风险仍被刻意保留未处理？

请将机密信息、原始日志、令牌、OAuth相关资料以及无关的记录内容排除在`metadata`之外，转而存储指向信息与摘要。如果某个任务没有相关文件或测试用例，请在`summary`中明确说明，而将源代码链接、问题编号或人工审核步骤等实际存在的证据存放在`metadata`中。

### 工作节点的生命周期

所有用于处理看板任务的配置文件都会自动具备工作节点生命周期功能——该功能会在工作节点启动时被注入到其系统提示语中（即`KANBAN_GUIDANCE`模块），因此**无需进行任何安装或配置**。它通过**工具调用**而非CLI命令，向工作节点传授完整的生命周期流程。

1. 程序启动后，调用 `kanban_show()` 函数以获取任务标题、内容、上级任务关联信息、之前的尝试记录以及完整的评论线程。
2. 通过终端工具执行 `cd $HERMES_KANBAN_WORKSPACE` 命令，然后在相应的工作空间中执行任务操作。
3. 在执行耗时较长的操作时，每隔几分钟调用一次 `kanban_heartbeat(note="...")`。**如果任务可能运行超过1小时，建议至少每小时调用一次 `kanban_heartbeat`**——调度器会在没有收到心跳信号且任务运行时间超过 `kanban.dispatch_stale_timeout_seconds`（默认为4小时）时，认为该工作进程可能发生崩溃且未进行清理，从而自动回收该任务。这种回收操作不会造成严重影响（任务会重新回到“待处理”状态并重新被调度，且失败计数器不会增加），但您当前任务的进度将会丢失。
4. 任务完成后，调用 `kanban_complete(summary="...", metadata={...})` 完成标记；如果遇到问题，则调用 `kanban_block(reason="...")` 暂停任务。

最后的 `kanban_complete` / `kanban_block` 调用属于工作进程协议的一部分。如果在工作进程仍在“运行”状态时以状态0退出，调度器会将其视为协议违规行为，并触发 `protocol_violation` 事件。

**代理端预防机制：**在工作进程即将退出且未调用终端看板工具之前，Hermes会检测到这一情况并注入最多两次模拟提示。该机制可有效应对模型先说明下一步操作（如“让我来撰写报告”），随后以`finish_reason=stop`结束运行的常见场景。这些提示会提醒模型立即调用`kanban_complete`或`kanban_block`函数。此防护机制仅适用于由调度器创建的工作进程（即设置了`HERMES_KANBAN_TASK`参数），若需禁用该功能，可设置`HERMES_KANBAN_STOP_NUDGE=0`。

**调度器端恢复机制：**如果模拟提示已被用尽，或工作进程在收到提示前崩溃，调度器会在自动阻止任务而非让其重新进入同一循环之前，给予该违规行为**有限次重试机会**（最多为 `_PROTOCOL_VIOLATION_FAILURE_LIMIT` 次连续违规，默认值为3次）。该重试次数仅统计*连续的*正常退出协议违规情况——交错出现的限流重新排队行为不会计入，其他类型的故障则会重置连续违规计数——并且每个任务可单独设置`max_retries`参数来覆盖这一上限。这种情况通常意味着模型仅输出了纯文本答案，且未通过看板工具界面完成操作后便退出了。

任务的生命周期及相关核心细节（如工作空间类型、交付成果`artifacts`、已创建的看板卡片等）均包含在系统提示块中，因此无论工作进程运行在何种配置下，都能获取这些信息——无需为不同配置单独设置技能。 

### 将额外技能固定到特定任务

有时，单个任务会需要特定的专业技能，而这些技能并非分配者默认具备——例如翻译任务需要“translation”技能，代码审查任务需要“github-code-review”技能，安全审计任务则需要“security-pr-audit”技能。无需每次都修改分配者的个人资料，只需将所需技能直接附加到任务上即可。

**对于协调代理**（即通常情况下的由一个代理将任务转发给另一个代理的情况），可使用 `kanban_create` 工具中的 `skills` 数组来实现：

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

**通过人工指令（CLI/斜杠命令）操作时**，需针对每一项重复输入 `--skill`：

```bash
hermes kanban create "translate README to Japanese" \
    --assignee linguist \
    --skill translation

hermes kanban create "audit auth flow" \
    --assignee reviewer \
    --skill security-pr-audit \
    --skill github-code-review
```

**在控制面板中**，将各项技能以逗号分隔后输入到“创建任务”对话框的**skills**字段中。

调度器会为列出的每项技能生成一个`--skills <name>`参数，这样工作节点在启动时就会加载所有这些技能，同时还会具备自动注入的看板指导功能。这些技能名称必须与分配者账号配置中实际安装的技能一致（可运行`hermes skills list`查看可用技能）；系统不支持运行时安装技能。

### 任务级模型覆盖

无需遵循分配者账号配置的默认设置，可直接将某个任务的执行节点绑定到特定的模型（以及可选的提供方）。

```bash
# At creation
hermes kanban create "hard refactor" --assignee coder \
    --model claude-opus-4.6 --provider anthropic

# Or later — takes effect on the next dispatch
hermes kanban set-model t_abcd claude-opus-4.6 --provider anthropic
hermes kanban set-model t_abcd none    # clear the override
```

调度器会使用指定的固定模型来启动工作节点（若设置了 `--provider <name>` 参数，则会传入该值；而 `--provider` 参数必须搭配模型使用）。控制面板中的“每任务模型”下拉菜单实际上也对应着相同的 `model_override` 字段。若未进行覆盖设置，工作节点将使用其配置文件中指定的模型。

### 成本策略：高端调度器 + 经济型工作节点

Kanban 的按配置文件划分机制使得规划器与工作节点的成本分配更为合理。将项目拆解为范围明确的任务卡片需要高级别的判断力；而针对那些已明确目标、上下文及交接依据的任务卡片，通常无需过多思考即可执行。由于绝大多数计算资源都消耗在工作节点上，因此成本也主要体现在工作节点的模型上。建议将调度器/规划器配置文件运行在高端模型上，而工作节点配置文件则使用经济型模型。每个配置文件在 `~/.hermes/profiles/<name>/` 目录下拥有独立的 `config.yaml` 文件；调度器在启动 `hermes -p <assignee>` 进程时，会注入对应配置文件的 `HERMES_HOME` 环境变量，从而使每个工作节点都能读取到其自身配置文件中的模型设置。

```yaml
# ~/.hermes/config.yaml (orchestrator / dispatcher profile)
model:
  default: "your-frontier-model"

# ~/.hermes/profiles/coder/config.yaml (worker profile)
model:
  default: "your-inexpensive-model"

# ~/.hermes/profiles/researcher/config.yaml (another worker profile)
model:
  default: "your-inexpensive-model"
```

对于那些对处理质量要求较高的卡片，只需通过[按任务指定模型覆盖功能](#per-task-model-override)（在创建时使用`--model`/`--provider`参数，之后可使用`hermes kanban set-model`命令，或通过控制面板的模型下拉菜单）将相应任务分配给性能更强的模型即可，无需修改任何配置文件。

### 生命周期插件钩子

看板状态变更时会触发[插件钩子](/user-guide/features/hooks#plugin-hooks)：`kanban_task_claimed`、`kanban_task_completed`和`kanban_task_blocked`，这些钩子会分别携带`task_id`和`profile_name`参数。由于钩子是在看板数据库更改提交之后才被触发，因此回调函数始终能获取到稳定的数据状态。需要注意的是，不同钩子的触发进程有所区别：`kanban_task_claimed`在**调度器进程**中触发，而`kanban_task_completed`/`kanban_task_blocked`则在**工作进程**中触发——建议在调度器配置文件中注册相应钩子，以便集中监控所有状态变更。

```python
def register(ctx):
    def on_blocked(task_id=None, profile_name=None, **kw):
        ctx.dispatch_tool("terminal", {"command": f"notify-send 'kanban blocked: {task_id}'"})
    ctx.register_hook("kanban_task_blocked", on_blocked)
```

### 目标模式卡片（`--goal`）

默认情况下，每个工作节点仅有一次处理卡片的机会——完成指定任务后，调用 `kanban_complete`/`kanban_block` 即可退出。若要让该工作节点进入**目标循环**模式，可使用 `--goal`（命令行接口）或设置 `goal_mode=True`（通过 `kanban_create` 工具或控制面板），此模式实际上采用了与 `/goal` 接口相同的 Ralph 式引擎：在每个轮次结束后，辅助审核员会将该工作节点的输出与卡片的标题及内容（视为验收标准）进行比对。如果任务尚未完成且轮次预算尚未用尽，工作节点将在**同一会话**中持续处理，直到审核员确认通过、工作节点主动终止任务，或预算耗尽（此时卡片会被**阻塞**以等待人工审核，而不会默默退出）。若审核员判定该目标按当前描述**无法实现**，卡片会立即被阻塞，并附上审核员的理由——此类不可实现的卡片永远不会被标记为已完成，针对此类卡片的 `kanban complete`/`kanban request-review` 操作也会被拒绝，系统会提示用户转而使用 `kanban block` 功能或重新定义任务范围。

```bash
hermes kanban create "Translate the docs site to French" \
    --body "Acceptance: every page translated, no English left, links intact." \
    --assignee linguist \
    --goal \
    --goal-max-turns 15      # optional; default 20
```

该功能适用于那些需要多步骤处理、或要求“持续执行直至满足条件X”类型的任务卡片。对于简单的单次性任务，则无需使用它——每轮都要调用判断器会带来不必要的开销，而且调度器已有的重试与断路机制足以应对临时性的工作者故障。判断器的效果取决于目标描述的质量，因此请将任务内容明确写成**具体的验收标准**。

:::note 目标模式卡片会借用 `/goal` 引擎——但并不会与其建立连接
`--goal` 会在该卡片对应的工作者会话内部运行持续处理循环。它与 [`/goal` 斜杠命令](./goals)共享引擎，但并不共享状态：在聊天会话中设置 `/goal` 标记不会创建、标记或移动任何看板卡片，且目标模式卡片的处理循环对其他聊天会话中的 `/goal status` 查询是不可见的。如果您希望对话能够持续迭代，请使用 [`/goal`](./goals)；若需在看板上执行任务，则应创建相应的卡片。
:::

### 整合器的工作方式

**一个表现良好的整合器不会亲自执行任务。**它会将用户的目标拆解为多个子任务，将这些任务相互关联，再将每个任务分配给您预先设置的某个角色配置，之后便不再干预。整合器的指导规则——包括防诱惑规则、步骤0的角色识别提示（由于调度器在遇到未知的负责人名称时会自动失败，因此整合器必须确保每张卡片都对应机器上实际存在的角色配置），以及以 `kanban_create` / `kanban_link` / `kanban_comment` 为关键点的任务拆解指南——会自动注入到工作者的系统提示中；无需额外安装任何组件。

标准的协调流程（两名并行研究人员将任务交接给撰写者）：

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

调度器的指导信息会自动包含在工作节点的系统提示中——无需为每个配置文件进行任何安装或同步操作。

**在分散执行前先做出决策。**设计决策应由调度器负责，而非工作节点。如果两个并行任务都需要选择相同的内容——比如命名规则、数据结构、文件格式或API接口规范——调度器只需一次性确定并将其应用到**两个任务**中。由于工作节点无法看到其他并行任务，因此每个子任务的描述中都必须包含其依赖的所有决策。例如，对于“构建导出工具”和“构建导入工具”这两个并行任务，不要让每个工作节点自行决定文件格式——应提前选定一种格式（比如带有`version`字段的换行分隔JSON），并将其写入两个任务的描述中，否则这两个任务将永远无法完成数据交互。

为获得最佳效果，建议将此功能与仅包含看板操作工具集（如`kanban`、`gateway`、`memory`）的配置文件搭配使用，这样即使调度器试图执行实现类任务，也根本无法做到。

## 控制面板（GUI）

使用 `/kanban` CLI命令或斜杠命令即可让看板在无界面模式下运行，但对于需要人工参与的场景而言，可视化看板往往是更合适的界面——它支持任务分类、跨配置文件监控、查看评论线程以及在不同列之间拖动任务卡片。Hermes将此功能作为**预装的控制面板插件**提供，位于 `plugins/kanban/` 目录下——它既不属于核心功能，也不是独立的服务，其实现方式遵循[扩展控制面板](./extending-the-dashboard)中的说明。

可通过以下方式打开该控制面板：

```bash
hermes kanban init      # one-time: create kanban.db if not already present
hermes dashboard        # "Kanban" tab appears in the nav, after "Skills"
```

### 该插件能为您带来什么

- 一个**看板**标签页，每个状态对应一列：`triage`、`todo`、`ready`、`running`、`blocked`、`done`（若开启相关开关，则还会显示`archived`列）。
  - `triage`列用于暂存初步的想法。在默认设置下（即`kanban.auto_decompose: true`），调度器会自动对放入此列的任务运行**分解器**。内置的分解器会使用`auxiliary.kanban_decomposer`模型路径，读取您的个人资料信息及任务描述，然后将任务拆解为一系列子任务，这些子任务会被分配给最合适的处理人员。原始任务会作为所有子任务的父任务保留下来，这样当所有子任务处理完毕时，负责该原始任务的负责人（即`kanban.orchestrator_profile`指定的用户，若未指定则使用默认的活跃配置）就能重新启动并判断任务是否完成。您也可以通过点击页面顶部的**Orchestration: Auto/Manual**开关（绿色表示自动模式，浅灰色表示手动模式），或直接编辑`config.yaml`文件来更改模式。这两种模式均可与`hermes kanban specify`命令共存——当您不希望任务被拆解时，仍可使用该命令对单个任务进行配置。
- 任务卡片会显示任务ID、标题、优先级标识、租户标签、负责人员配置、评论/链接数量、**进度指示条**（若任务存在依赖关系，则显示“已完成N个/总共有M个子任务”），以及“创建于N前”。每张卡片上都配有复选框，方便进行多选操作。
- **“Running”列中的按配置文件分类功能**——通过工具栏上的复选框，可以按负责人员对“Running”列中的任务进行分组显示。
- **通过 WebSocket 实时更新** — 该插件会以较短的间隔轮询只读的 `task_events` 表；一旦任何界面（CLI、网关或其他仪表板标签页）发生操作，看板便会立即反映相应变化。为避免大量事件同时触发导致频繁重新获取数据，系统采用了防抖机制。
- **通过拖放更改任务状态** — 可将卡片在列之间拖动以改变其状态。拖放操作会发送 `PATCH /api/plugins/kanban/tasks/:id` 请求，该请求会经过与 CLI 相同的 `kanban_db` 处理逻辑——因此三种界面之间的数据始终保持一致。当任务状态被设置为不可逆状态（如“已完成”、“已归档”、“已阻塞”）时，系统会要求用户确认操作。触摸设备则提供基于指针的操作方式，确保可在平板电脑上正常使用看板。
- **创建任务对话框** — 点击任意列标题处的 “+” 符号，即可打开一个包含各字段的模态窗口：任务标题、负责人、优先级、所需技能、工作空间类型/路径（默认来自看板中的项目目录，也可为每个任务单独设置）、目标模式，以及（可选）从所有现有任务中选择的父任务。按下 Enter 键可创建任务，Shift+Enter 键可在标题字段中插入换行符，Esc 键则可取消操作。从“分类处理”列创建的任务会自动被归入分类处理状态。
- **多选及批量操作** — 按住 Shift/Ctrl 键点击卡片或选中其复选框即可将其加入选择列表。顶部会出现批量操作栏，支持批量更改任务状态、归档任务以及重新分配任务（可通过下拉菜单选择负责人，或选择 “(取消分配)”）。对于不可逆的批量操作，系统会先要求用户确认。即使部分任务操作失败，其余任务仍会继续执行，并会报告相关错误信息。
- 点击卡片（无需按下 Shift/Ctrl 键）即可打开侧边抽屉（按 Escape 键或点击抽屉外部可关闭），其中包含以下功能：
  - **可编辑的标题**——点击标题即可重新命名。
  - **可编辑的负责人/优先级**——点击对应元数据行即可进行修改。
  - **可编辑的描述**——默认以 Markdown 格式显示（支持标题、加粗、斜体、内联代码、代码块、`http(s)` / `mailto:` 链接以及项目列表），并提供“编辑”按钮，点击后会切换为文本输入框。该 Markdown 解析器体积小巧且具备 XSS 防护功能——所有替换操作都会在经过 HTML 转义的输入数据上执行，仅允许 `http(s)` / `mailto:` 链接直接通过，同时始终会为链接设置 `target="_blank"` 和 `rel="noopener noreferrer"` 属性。
  - **依赖关系编辑器**——以芯片图形式展示父任务与子任务的关系，每个任务旁都有一个“×”按钮用于断开关联；此外，其他所有任务上方还配有下拉菜单，可用于添加新的父任务或子任务。若尝试形成循环依赖，服务器端会立即拒绝并给出明确提示。
- **状态操作行**（可选操作包括：→ 分类处理 / → 就绪 / → 运行中 / 暂停 / 解除暂停 / 完成 / 归档），对于处于“分类处理”状态的卡片，该行还提供两项由大语言模型驱动的操作：**⚗ 分解任务**可将该任务拆解为一系列子任务，并根据任务描述将其分配给相应的专家；**✨ 明确任务规范**则用于重新编写单个任务的规范。当大语言模型判断任务无需拆分时，分解功能会自动退化为类似“明确任务规范”的处理方式，因此前者可视为后者的严格超集。这些操作既可通过 CLI 命令执行（如 `hermes kanban decompose <id>`、`specify <id>`、`--all`），也可通过任何网关平台访问（如 `/kanban decompose <id>`），还能通过编程方式调用 `POST /api/plugins/kanban/tasks/:id/decompose` 和 `…/specify` 接口来实现。相关模型可在 `config.yaml` 文件的 `auxiliary.kanban_decomposer` 和 `auxiliary.triage_specifier` 配置项中进行设置。
- 结果展示区域（同样采用 Markdown 格式），支持通过回车键提交评论，同时会显示最近发生的 20 条事件。
- **工具栏筛选器**——包含全文搜索功能、租户下拉选择框（默认值为 `config.yaml` 中的 `dashboard.kanban.default_tenant`）、负责人下拉选择框、“显示已归档项目”切换按钮、“按专家分组展示任务列”切换按钮，以及一个**提醒发送器**按钮，这样用户无需等待 60 秒的时间间隔即可主动发起提醒。
从视觉设计上看，该界面采用大家熟悉的Linear/Fusion布局：深色主题、带有数量标注的列标题、彩色状态点，以及用于标识优先级和租户类型的圆点标签。该插件仅读取主题CSS变量（如`--color-*`、`--radius`、`--font-mono`等），因此会自动适配当前激活的任何控制台主题样式。

### 自动编排与手动编排

对于放入“分拣”列中的任务，看板系统提供了两种处理方式：

**自动模式（默认）** — `kanban.auto_decompose: true`。内置在网关中的调度器会定期运行**分解器**，其执行频率受`kanban.auto_decompose_per_tick`参数限制（默认为每轮3个任务），从而避免大量分拣任务同时处理导致辅助大语言模型负荷过重。分解器会使用内置的分解提示词以及`auxiliary.kanban_decomposer`模型路径，读取已安装的配置文件及其描述，然后指示大语言模型生成一个JSON任务图谱：明确哪些任务需要创建、它们应分配给谁、以及哪些任务之间存在依赖关系。原始的分拣任务将成为该图谱中所有子任务的父节点，因此会一直存在直至整个图谱处理完成——之后它会恢复为“待处理”状态，以便其负责人（即`kanban.orchestrator_profile`指定的配置，或未指定时的默认配置）判断任务是否完成，若工作尚未结束则可继续添加新任务。这就是所谓的“输入简短指令后即可离开”的处理流程。

一个已完成的内置拆分操作会与其子图一起以原子化方式被记录下来。将该根节点移回“分类处理”状态并不会生成新的图结构；普通的依赖关系也不会阻止任务的首次拆分。该完成标记会在事件保留期间一直存在，直至该任务被删除。此机制并非针对独立创建的手动图进行的语义去重处理，也不是对之前已被裁剪的历史记录的修复手段。

当新创建的任务未指定租户时，它将按给定顺序继承其父节点中的第一个非空租户。若指定了明确的租户（包括工具传递的工作者当前活跃租户），则以该租户为准。看板依然代表着严格的隔离边界。

**手动模式** — 设置 `kanban.auto_decompose: false`。此类任务将一直留在“分类处理”状态，直至您主动操作。您可以点击卡片上的 **⚗ 拆分** 按钮，运行命令 `hermes kanban decompose <id>`（或 `--all`），或通过聊天界面使用指令 `/kanban decompose <id>`。此方式与看板原有的拆分行为一致，非常适合需要在何时执行拆分操作方面拥有完全控制权的情况。

**重要注意事项：** 手动模式仅会禁用内置的 Triage 分解器，它不会阻止某个配置文件调用 `kanban_create` 函数，也不会关闭创建者会话的唤醒功能。当设置 `kanban.auto_subscribe_on_create: true` 时，任务的终端事件会通过模拟状态切换来唤醒最初的代理，使其能够检查任务交接情况，并判断是否确实需要开展新的后续工作。若希望任务完成时保持被动状态，则应将该参数设置为 `false`。为便于追溯来源，由内置分解器生成的子任务会使用 `created_by=auto-decomposer`；而由被唤醒的配置文件创建的任务则会携带该配置文件的名称。

您可以通过看板页面顶部的 **Orchestration: Auto/Manual** 按钮（绿色代表自动模式，灰暗灰色代表手动模式）在两种模式之间切换，也可以直接编辑 `config.yaml` 文件来实现切换。这两种模式均能与 `hermes kanban specify` 功能共存——当您不希望任务进一步扩散时，仍可使用该功能对单个任务进行配置重写。

分解器的路由决策取决于配置文件描述，这是一种针对每个配置文件的标记机制，您可以通过 `hermes profile create --description "..."`、`hermes profile describe <name> --text "..."`、`hermes profile describe <name> --auto`（由大语言模型根据该配置文件中已安装的技能及模型自动生成）或扩展后的**编排设置**面板中的配置文件专用编辑器来设置这些描述。即便没有描述信息的配置文件仍会显示在列表中——它们可以通过名称进行路由，但精度较低。分解器绝不会将子任务分配给 `assignee=None` 的对象：当大语言模型选择到未知配置文件时，该子任务将被路由至 `kanban.default_assignee`（如果未设置，则使用当前默认配置文件）。

`kanban.orchestrator_profile` 并不会将对应配置文件的提示词、技能或自定义逻辑加载到分解过程中。它的作用仅是决定任务分发后的根任务/编排任务的负责人。若要更改分解器使用的模型或提供方，需配置 `auxiliary.kanban_decomposer`。若希望使用配置文件中的自定义任务拆分逻辑而非内置分解器，则需切换至手动模式，并让该配置文件显式地创建或分解任务。

相关配置项（均位于 `~/.hermes/config.yaml` 文件的 `kanban:` 下）：

| 键值 | 默认值 | 用途 |
|---|---|---|
| `auto_decompose` | `true` | 分发器会在每个时间间隔自动为分类任务运行内置的分解器。该功能不会限制基于配置文件的 `kanban_create` 调用或创建者轮次启动。 |
| `auto_decompose_per_tick` | `3` | 每个分发器时间间隔内允许的分解次数上限。超出部分将延迟到下一个时间间隔处理。 |
| `orchestrator_profile` | `""` | 分解后分配给根任务/编排任务的配置文件。留空则回退至当前默认配置文件。 |
| `default_assignee` | `""` | 当大语言模型选择未知配置文件时，子任务将归属至此。留空则回退至当前默认值。 |
| `auto_subscribe_on_create` | `true` | 当在持久化网关/TUI 会话中执行 `kanban_create` 操作时，终端事件会通过模拟的状态轮次来恢复对应的代理。若设置为 `false`，则表示采用被动完成方式，或需要显式调用 `kanban_notify-subscribe`。该功能与 `auto_decompose` 独立运行。 |
| `done_sub_retention_days` | `30` | 已标记为“完成”状态的订阅会保留以支持重新打开任务，而标记为“归档”状态的订阅则会被移除。通知器垃圾回收机制会清理那些任务已标记为“完成”或“阻塞”且多日无新事件的订阅，从而控制从不进行归档操作的看板中订阅子表的增长速度。将此值设置为 `0` 可禁用该清理功能。 |

以及两个辅助的大语言模型插槽：

| 键值 | 用途 |
|---|---|
| `auxiliary.kanban_decomposer` | 用于生成任务图的模型（由 Decompose 调用）。可通过设置 `provider`/`model` 参数来替代主聊天模型。 |
| `auxiliary.profile_describer` | 用于自动生成个人资料描述的模型（由 `hermes profile describe --auto` 命令调用）。 |

### 架构

该 GUI 仅作为一个**通过数据库读取数据并写入 kanban_db 的层**，不包含任何独立的业务逻辑：

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

所有接口均位于 `/api/plugins/kanban/` 下，并通过控制面板的临时会话令牌进行保护：

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/board?tenant=<name>&include_archived=…` | Full board grouped by status column, plus tenants + assignees for filter dropdowns |
| `GET` | `/tasks/:id` | Task + comments + events + links |
| `POST` | `/tasks` | Create (wraps `kanban_db.create_task`, accepts `triage: bool` and `parents: [id, …]`) |
| `PATCH` | `/tasks/:id` | Status / assignee / priority / title / body / result |
| `POST` | `/tasks/bulk` | Apply the same patch (status / archive / assignee / priority) to every id in `ids`. Per-id failures reported without aborting siblings |
| `POST` | `/tasks/:id/comments` | Append a comment |
| `POST` | `/tasks/:id/specify` | Run the triage specifier — auxiliary LLM fleshes out the task body and promotes it from `triage` to `todo`. Returns `{ok, task_id, reason, new_title}`; `ok=false` with a human-readable reason on "not in triage" / no aux client / LLM error is a 200, not a 4xx |
| `POST` | `/tasks/:id/decompose` | Run the kanban decomposer — auxiliary LLM produces a task graph and the helper atomically creates the children + links the root + flips `triage → todo`. Returns `{ok, task_id, reason, fanout, child_ids, new_title}`. Same 200-on-LLM-error convention as `/specify`. |
| `GET` | `/profiles` | List installed profiles with their descriptions (consumed by the dashboard's profile-description editor and the orchestrator picker). |
| `PATCH` | `/profiles/:name` | Set or clear a profile's description (user-authored — `description_auto: false`). Returns `{ok, profile, description}`. |
| `POST` | `/profiles/:name/describe-auto` | Generate a description for a profile via `auxiliary.profile_describer`. Persists with `description_auto: true` so the dashboard can surface a "review" badge. |
| `GET` | `/orchestration` | Read the kanban orchestration settings (`orchestrator_profile`, `default_assignee`, `auto_decompose`) plus the *resolved* effective values after fallbacks. |
| `PUT` | `/orchestration` | Update one or more of the three orchestration keys in `config.yaml`. Validates that non-empty profile names actually exist. |
| `POST` | `/links` | Add a dependency (`parent_id` → `child_id`) |
| `DELETE` | `/links?parent_id=…&child_id=…` | Remove a dependency |
| `POST` | `/dispatch?max=…&dry_run=…` | Nudge the dispatcher — skip the 60 s wait |
| `GET` | `/config` | Read `dashboard.kanban` preferences from `config.yaml` — `default_tenant`, `lane_by_profile`, `include_archived_by_default`, `render_markdown` |
| `WS` | `/events?since=<event_id>` | Live stream of `task_events` rows |

每个处理程序都只是一个轻量级的封装层——该插件仅包含约700行Python代码（包括路由模块、WebSocket处理逻辑、批量处理功能以及配置读取器），并未新增任何业务逻辑。还有一个名为 `_conn()` 的小型辅助函数，会在每次读写操作时自动初始化 `kanban.db`，因此无论用户是先打开控制面板、直接调用REST API，还是运行 `hermes kanban init` 命令，程序都能正常启动。

### 控制面板配置

在 `~/.hermes/config.yaml` 文件的 `dashboard.kanban` 部分中，只要修改其中的任意键值，就会改变该面板的默认设置——插件会在加载时通过 `GET /config` 请求读取这些配置值。

```yaml
dashboard:
  kanban:
    default_tenant: acme              # preselects the tenant filter
    lane_by_profile: true             # default for the "lanes by profile" toggle
    include_archived_by_default: false
    render_markdown: true             # set false for plain <pre> rendering
```

每个参数均为可选，若未指定则默认使用所示值。

### 安全模型

控制台的 HTTP 认证中间件会**明确跳过 `/api/plugins/` 路径**（详见 ./extending-the-dashboard#backend-api-routes）。由于控制台默认绑定在本地主机上，因此插件路由被设计为无需认证。这意味着主机上的任何进程都可以访问看板相关的 REST 接口。

而 WebSocket 还需额外一步验证：它要求通过 `?token=…` 查询参数提供控制台的临时会话令牌（因为浏览器无法在升级请求中设置 `Authorization` 头），这一机制与浏览器内置的 PTY 桥接方式一致。

如果您运行 `hermes dashboard --host 0.0.0.0`，则包括看板在内的所有插件路由都将对网络开放。**请勿在共享主机上执行此操作。** 看板中存储着任务内容、评论以及工作空间路径；一旦攻击者获取了这些路由的访问权限，他们就能读取您的整个协作数据，还能创建、重新分配或归档任务。

`~/.hermes/kanban.db` 中的任务数据刻意设计为与用户配置文件无关（这正是其作为协调机制的初衷）。即使您使用 `hermes -p <profile> dashboard` 命令打开控制台，看板仍会显示主机上其他配置文件创建的任务。所有配置文件都由同一用户拥有，但如果您需要同时管理多个角色，了解这一点非常重要。

### 实时更新

`task_events` 是一个只读的 SQLite 表，其中包含单调递增的 `id`。WebSocket 端点会保存每个客户端上次查看的事件 ID，并在新的事件生成时推送相应行数据。当有大量事件同时到达时，前端会重新加载（成本极低的）看板端点——这比针对每种类型的事件都尝试修改本地状态更为简单且准确。由于采用了 WAL 模式，读取循环永远不会阻塞调度器正在处理的 `BEGIN IMMEDIATE` 事务。

### 扩展功能

该插件遵循标准的 Hermes 仪表板插件规范——如需查看完整的清单参考、Shell 插槽、页面级插槽以及插件 SDK，请参阅 [扩展仪表板](./extending-the-dashboard)。无需 fork 该插件，即可实现添加额外列、自定义卡片样式、按租户筛选布局，或完全替换 `tab.override` 内容等功能。

如需禁用该功能而不删除它：在 `config.yaml` 中添加 `dashboard.plugins.kanban.enabled: false`（或删除 `plugins/kanban/dashboard/manifest.json` 文件）。

### 范围限制

该 GUI 被刻意设计得较为精简。插件能够实现的所有功能均可通过 CLI 访问；插件仅是为了提升用户操作体验。自动分配、预算设置、审批流程以及组织结构视图等功能仍属于用户空间范畴——可通过路由器配置文件、其他插件，或复用 `tools/approval.py` 文件来实现，具体内容详见设计规范中的“范围外功能”部分。

## CLI 命令参考

这就是**您**（或脚本、cron作业以及控制面板）用于操作看板的上层接口。在调度器内部运行的工作进程也会使用 `kanban_*` [工具界面](#how-workers-interact-with-the-board)来执行相同的操作——这里的命令行界面与那边的工具均通过 `kanban_db` 进行数据交互，因此从设计上来看，这两个界面是保持一致的。

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

hermes kanban request-review <id> [--summary "..."] [--metadata JSON] [--reviewer PROFILE]
hermes kanban request-changes <id> "<required changes>"               # active reviewer -> implementer
hermes kanban reopen-review  <id>... [--reason "..."]                 # changes requested: 'review' -> ready/todo

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
        [--chat-type dm|group|channel|thread] [--delivery-mode notify|notify+wake|wake]
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

`--max-retries` 是用于为调度器设置针对单个任务的熔断机制参数。设置为 `--max-retries 1` 时，任务在首次执行失败即会被阻塞；而设置为 `--max-retries 3` 时，则允许进行两次重试，仅在第三次失败后才会阻塞。若不指定该参数，则会使用 `config.yaml` 文件中的 `kanban.failure_limit` 值，即默认内置值。

### 并发性、调度及子任务升级配置

| 配置键 | 默认值 | 功能说明 |
|------------|---------|--------------|
| `kanban.max_in_progress` | 未设置（无限制） | 限制同时运行的任务数量。当看板上已有 N 个任务在运行时，调度器将不再创建新任务——这有助于那些处理速度较慢的组件（如本地大语言模型、资源受限的服务器），使其能先完成现有任务，避免任务堆积导致超时。若该值无效或小于 1，则会记录警告并视为无限制。 |
| `kanban.max_in_progress_per_profile` | 未设置（无限制） | `max_in_progress` 的按配置文件划分版本——用于限制每个分配者配置文件可同时运行的任务数量。当某个配置文件处理速度较慢或存在速率限制，而其他配置文件仍需持续处理任务时，此设置非常有用。该值与看板级的 `max_in_progress` 同时生效；只有两者都允许创建新任务，调度流程才能继续进行。 |
| `kanban.auto_promote_children` | `true` | 当 `decompose_triage_task()` 生成没有父阻塞依赖的子任务后，这些子任务会自动被提升至 `ready` 状态，以便调度器能够处理它们。将此值设置为 `false` 可要求手动审核——子任务将一直保持在 `todo` 状态，直到您手动将其提升。 |
| `kanban.default_workdir` | 未设置 | 当既未通过 `--workspace` 参数指定，任务本身也未定义工作目录时，会对新任务应用此看板级默认工作目录。若任务中指定了 `workspace:` 参数，则该参数的优先级仍高于此默认值。 |

```yaml
kanban:
  max_in_progress: 2
  auto_promote_children: false
  default_workdir: ~/work/active-project
```

### 定时任务启动（`scheduled_at`）

为任务设置 `scheduled_at` 参数，即可将其派发时间延迟至指定时刻。调度器会跳过那些 `scheduled_at` 时间位于未来阶段的已准备就绪的任务，直到该时间戳之后的第一个计时点才会对这些任务进行处理。

```bash
hermes kanban create "nightly backup audit" \
  --assignee ops --scheduled-at "2026-06-01T03:00:00Z"
```

### 任务重新生成保护机制

当任务在之前的执行过程中遇到配额限制、认证错误或429限流问题（`blocker_auth`），或在保护时间窗口内已成功完成执行（`recent_success`），又或者最近的任务备注中包含了GitHub Pull Request链接（`active_pr`）时，调度器将拒绝重新生成该任务。这一机制可避免在人工处理人员跟进期间，有大量工作节点重复处理同一个缺陷或任务。详情请参阅[事件参考](#event-reference)中的`respawn_guarded`条目。

### 拖拽删除与批量删除（控制面板）

控制面板的看板页面上设有**回收站区域**——只需将任意任务卡片拖入该区域即可删除该任务，此操作会同步影响关联的`task_events`、子链接及订阅项。系统会通过确认提示防止误操作。此外，也可通过`DELETE /api/plugins/kanban/tasks`接口进行批量删除，需传入格式为`{"ids": ["t_abc", "t_def", ...]}`的JSON数据。

### 工作节点可见性接口

控制面板插件API现已为外部监控工具提供这些只读接口（以及一个用于运行控制的操作接口）：

| 端点 | 返回内容 |
|------|----------|
| `GET /api/plugins/kanban/workers/active` | 当前正在运行的工作节点信息，包括进程ID、配置文件、任务ID、启动时间以及上次心跳时间 |
| `GET /api/plugins/kanban/runs/{id}` | 单次运行详情——任务ID、运行状态、开始/结束时间、退出码以及日志路径 |
| `POST /api/plugins/kanban/runs/{run_id}/terminate` | 终止可回收的运行任务——停止对应工作节点，并释放该任务以便重新调度 |
| `GET /api/plugins/kanban/inspect` | 综合调度器快照——待处理任务数量、进行中任务数量与`max_in_progress`的对比情况，以及近期发生的事件 |

所有这些接口均与Kanban插件API的其他功能一样，需通过相同的控制面板插件认证机制才能访问。

### Kanban Swarm拓扑结构辅助工具

`hermes kanban swarm`可一次性创建一个持久化的**Kanban Swarm v1**架构图：包含一张已完成的根节点/看板卡片、N张并行工作的节点卡片、一张依赖于所有工作节点的验证节点卡片，以及一张依赖于验证节点的综合处理节点卡片。共享的集群上下文（即“看板”信息）会以结构化的JSON注释形式存储在根节点卡片上，因此任何工作节点都能读取到这些信息。

```bash
hermes kanban swarm "Design a multi-region failover plan" \
  --workers researcher,architect,sre \
  --verifier reviewer --synthesizer writer
```

生成的图结构会以原子化方式被持久化：调度器与仪表板读取器看到的要么是没有新的集群，要么是完整的拓扑结构，绝不会出现仅部分连接的根节点/工作节点/验证节点关系图。之后系统便会恢复正常调度流程——工作节点并行运行，所有节点处理完成后验证节点才会启动，而在验证节点确认任务已完成之后，合成器才会开始工作。

## `/kanban` 斜杠命令 {#kanban-slash-command}

每一个 `hermes kanban <action>` 命令都可以通过 `/kanban <action>` 的形式来调用——既可以在交互式的 `hermes chat` 会话中使用，也可以在任何网关平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、电子邮件、短信）上使用。这两种调用方式都会调用完全相同的 `hermes_cli.kanban.run_slash()` 函数入口，该函数会复用 `hermes kanban` 的命令行参数解析结构，因此无论是在 CLI、/kanban 接口还是 `hermes kanban` 命令中，参数形式、标志选项以及输出格式都保持一致。您无需离开聊天界面即可操作任务看板。

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

多字参数的引用方式与在shell中相同——`run_slash`会使用`shlex.split`来解析行中的其余内容，因此`"..."`和`'...'`两种形式均可使用。

### 运行中的使用：`/kanban`可绕过正在运行的代理保护机制

通常情况下，当代理仍在处理任务时，网关会将斜杠命令和用户消息暂存队列中——这正是为防止在当前任务尚未处理完成时意外启动新任务的机制。**`/kanban`明确被排除在这一保护机制之外。** 该看板存储在`~/.hermes/kanban.db`中，而非正在运行的代理的状态中，因此无论是读取操作（如`list`、`show`、`context`、`tail`、`watch`、`stats`、`runs`）还是写入操作（如`comment`、`unblock`、`block`、`assign`、`archive`、`create`、`link`等），都能立即执行，即便是在任务处理过程中也是如此。

这正是实现分离设计的初衷：

- 若某个工作节点因等待其他节点而阻塞，你只需通过手机发送`/kanban unblock t_abcd`指令，调度器就会在下一个时间间隔自动接管该节点的任务。被阻塞的工作节点不会被打断，只是不再处于阻塞状态。
- 如果发现某张任务卡片需要人工补充说明，发送`/kanban comment t_xyz "请使用2026年的方案，而非2025年的"`即可，这些注释会直接添加到任务讨论线程中，下次执行该任务时，`kanban_show()`函数会自动读取这些内容。
- 若想在不中断任务编排进程的情况下了解所有工作节点的运行状态，可使用`/kanban list --mine`或`/kanban stats`命令查看看板，而不会影响当前的对话流程。

### `/kanban create`指令的自动订阅功能（仅限网关）

当您通过网关使用 `/kanban create "…"` 命令创建任务时，该任务的起始聊天记录（包括平台名称、聊天 ID 以及线程 ID）会自动被订阅，以便接收该任务相关的终端事件通知（如 `completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）。每当有新的终端事件发生时，系统都会向您发送一条消息——在任务状态变为 `completed` 时，消息中还会包含 Worker 输出结果摘要的第一行内容——因此您无需自行轮询或记住任务 ID 即可。

```
you> /kanban create "transcribe today's podcast" --assignee transcriber
bot> Created t_9fc1a3  (ready, assignee=transcriber)
     (subscribed — you'll be notified when t_9fc1a3 completes or blocks)

… ~8 minutes later …

bot> ✓ t_9fc1a3 completed by transcriber
     transcribed 42 minutes, saved to podcast/2026-05-04.md
```

当任务状态变为 `done` 时，相关的订阅依然会保持有效——因为该完成状态是可逆的（审核员或控制器可以重新开启已标记为完成的任务），因此源会话会通过重复的重新开启流程持续收到通知。而一旦任务进入不可逆的 `archived` 状态，这些订阅就会自动被移除。在从不进行归档操作的看板上，系统会定期执行垃圾回收操作，清除那些已在 `done` 或 `blocked` 状态下长达 `kanban.done_sub_retention_days` 天（默认为30天，设为0则禁用该功能）且没有新活动的任务对应的订阅，从而避免过时的记录无限积累。如果您通过 `--json` 参数以脚本方式创建任务（即机器输出格式），则不会自动触发订阅功能——因为系统假设此类脚本调用者希望通过 `/kanban notify-subscribe` 接口手动管理订阅。

通过 `kanban_create` 或 `hermes kanban create` 创建任务的调度器工作进程，即便没有 `parents` 及依赖链接字段，也会复制所属任务的所有持久化通知订阅。目标的地址、路由锚点以及交付方式都会被保留；此外，被动订阅不会通过自动订阅功能升级为主动订阅。此复制操作独立于 `auto_subscribe_on_create` 参数，后者用于控制是否将当前对话添加为新的目标地址。对于没有所属任务的纯CLI会话或工作进程，系统不会为其生成任何目标地址。

对于 `kanban_create` 操作，会话链路解析的顺序为：显式的 `session_id`、负责处理任务的持久会话、请求级 API 的来源，最后是当前进程会话。内置的分解功能也会继承其父节点的持久会话。会话链路本身并非通知目标：更改 `session_id` 并不会替换现有的订阅关系；若需改变事件发送的目标，应使用 `notify-subscribe` 和 `notify-unsubscribe` 函数。

基于聊天场景的自动订阅功能以 `notify+wake` 模式创建：当收到终端事件时，目标智能体既能接收被动消息，又能主动响应，从而能够了解看板上下文并用自己的话进行回复。详情请参见下文的[交付模式](#delivery-modes)。

### 消息中的输出截断

网关平台对消息长度设有实际限制。如果执行 `/kanban list`、`/kanban show` 或 `/kanban tail` 命令生成的输出超过约 3800 个字符，响应内容将被截断，并在底部添加“…（已截断；请在终端中使用 \`hermes kanban …\` 查看完整内容）”的提示。而 CLI 接口则没有此类限制。

### 自动补全功能

在交互式 CLI 中，输入 `/kanban ` 后按 Tab 键即可循环查看内置的子命令列表（`list`、`ls`、`show`、`create`、`assign`、`link`、`unlink`、`claim`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`、`dispatch`、`context`、`init`、`gc`）。上述 CLI 参考文档中列出的其他命令（`watch`、`stats`、`runs`、`log`、`assignees`、`heartbeat`、`notify-subscribe`、`notify-list`、`notify-unsubscribe`、`daemon`）同样可用，只是尚未出现在自动补全提示列表中。

## 协作模式

该看板无需新增任何基础功能即可支持以下八种协作模式：

| 模式 | 结构 | 示例 |
|---|---|---|
| **P1 发散式** | N 个同级成员，角色相同 | “同时从5个角度展开调研” |
| **P2 流水线式** | 角色链：探员 → 编辑 → 撰写人 | 每日简报汇总流程 |
| **P3 投票/法定人数制** | N 个同级成员 + 1 名汇总者 | 3名研究人员 → 1名审稿人选定 |
| **P4 长期运行的日志系统** | 相同的配置文件 + 共享目录 + 定时任务 | Obsidian 文档库 |
| **P5 人工干预式** | 工作者设置阻塞 → 用户发表评论 → 解除阻塞 | 面对模糊的决策时使用 |
| **P6 `@提及`** | 通过正文直接路由 | `@审稿人，请查看这个` |
| **P7 线程级工作空间** | 在特定线程中输入 `/kanban here` | 每个项目的专用通道线程 |
| **P8 批量管理式** | 一个配置文件，管理N个对象 | 50个社交账号 |
| **P9 分类指定器** | 初步想法 → 输入 `triage` → 再输入 `hermes kanban specify` 来细化内容 → 最终生成待办任务 | “将这条简短说明转化为结构清晰的待办任务” |
如需查看各功能的实际应用示例，请参阅 `docs/hermes-kanban-v1-spec.pdf`。

## 将上下文传递给后续卡片（父链接）

父链接不仅是一个调度节点，更是从**已完成**的卡片向新卡片传递上下文的通道。当您使用 `--parent <done-card-id>` 创建卡片时，将会发生以下两件事：

1. **卡片立即符合条件。** `create_task` 会根据父卡片的状态来设置子卡片的状态：所有父卡片均为“已完成”状态的子卡片会直接被标记为“待处理”状态——无需等待，也无需手动升级。（对于那些父卡片仍处于处理中的子卡片，则会一直保留在“待办”状态，直到最后一个父卡片处理完毕后通过 `recompute_ready` 功能将其升级。）
2. **父卡片的处理结果也会一同传递。** 为子卡片准备的工作者上下文（由 `build_worker_context` 函数生成，即 `kanban_show()` 的返回值）中包含一个 `## 父任务结果` 部分，其中会原封不动地列出每个父卡片的完成情况摘要及元数据。

```
## Parent task results
### t_77c26979 (completed just now)
Added exponential backoff with jitter to the retry helper.
_metadata_: `{"changed_files": ["hermes_cli/retry.py", "tests/test_retry.py"], "decisions": ["capped backoff at 60s", "jitter = full"]}`
```

正因如此，针对已完成卡片进行的后续工作应采用**创建新的子卡片，而非重新打开已完成的卡片**这一模式。已完成的卡片代表着不可更改的历史记录——其上下文会通过父链接延续下去。而在同一卡片上进行的返工（即对出错卡片的重复尝试）则属于另一种处理机制：这些之前的尝试会被视为该卡片自身上下文中的“历史记录”。

仅依靠工作树或分支是无法替代这一机制的：仓库状态虽然能告诉后续处理任务代码的当前样子，却无法解释其背后的原因——各项决策、运行过的测试以及修改过的文件，都存储在父卡片的结构化传递信息中，而非 Git 里。那些在父卡片完成时还不存在的证据（例如后来出现的 CI 测试失败日志），应当被记录在新卡片的**内容部分**中。

```bash
# Implementation card t_impl is done. CI fails two hours later.
hermes kanban create "Fix CI failure from t_impl: test_retry flakes on 3.11" \
    --assignee coder \
    --parent t_impl \
    --body "$(cat <<'EOF'
CI run #4812 failed after t_impl merged.
Log excerpt: FAILED tests/test_retry.py::test_backoff_jitter - TimeoutError
Acceptance: tests/test_retry.py green on 3.11 and 3.12 in CI.
Use a fresh worktree/branch; do not force-push the original branch.
EOF
)"
```

修复工作节点在启动时会携带原始卡片的摘要与元数据（包括被修改的文件及相关决策），同时还会包含您在卡片正文中添加的新证据。

### 解决冲突的工作节点分支问题

在工程流水线中（具有工作树的P1/P2模式），两个工作节点的分支在合并时可能会出现冲突。切勿让任一工作节点自行判断——处于冲突状态的任务代理缺乏另一方的上下文信息，因此很可能会直接覆盖对方的内容或放弃自身的处理结果。正确的做法是创建一张用于协调的卡片，将其分配给**第三个中立的角色**，并将**所有冲突的卡片**都设为该卡片的父节点：这些父节点会将双方的完成摘要一并传递给协调器，使其能够获取到所有的差异内容以及相应的处理意图。内置的[`agent-merge-conflict-arbiter`可选技能](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/autonomous-ai-agents/agent-merge-conflict-arbiter/SKILL.md)会为该工作节点提供完整的处理流程：对每一处冲突内容进行分类、给出折中的解决方案、进行验证，最后输出一份详细列出所有决策的总结报告。

### 并行任务中的冲突高发点

在大规模的协作任务中，某些文件往往会成为冲突高发点：众多工作者都会向同一个文件添加少量内容，却无人负责维持其文件规模的紧凑，从而导致频繁的合并冲突。解决此问题的方法是一种注释规范，而非新的基础功能。如果某个工作者发现自己的修改内容会持续与同一文件中的其他内容发生冲突，或者自己编辑过的文件不断出现在其他人的最新评论中，就不应默默地继续添加内容。相反，它应在自己的卡片上留下带有特定前缀的注释：

```
hotspot: hermes_cli/kanban_db.py — third conflicting edit to the dispatch loop this wave
```

并在其生成的 `metadata` 中重复该标记。对于那些看到**两个或更多标注相同路径的 `hotspot:` 评论**的协调者（或审核看板的人），应在为该文件安排更多相关任务之前，专门创建一张重构/拆分卡片——拆分磁力文件的成本远低于日后处理由此引发的各类冲突。对于*已经发生*的冲突，则可运用上述的协调卡片模式，并搭配 `agent-merge-conflict-arbiter` 可选技能；而设置热点标记则是从源头解决问题的方法，能有效避免协调流程陷入持续不断的处理状态。

## 多租户使用场景

当一个专家团队同时为多家企业提供服务时，需为每项任务添加租户标签：

```bash
hermes kanban create "monthly report" \
    --assignee researcher \
    --tenant business-a \
    --workspace dir:~/tenants/business-a/data/
```

工作节点会获取 `$HERMES_TENANT` 值，并通过前缀为内存写入数据添加命名空间。看板、调度器以及配置文件定义都是共享的，仅有数据会被限定作用域。

## 桌面端通知

桌面版应用的内置看板插件可直接展示相同的终端事件，无需依赖任何网关平台。只要看板的实时事件套接字处于连接状态，每当发生 `completed`、`blocked`、`gave_up`、`crashed`、`timed_out` 或被路由至分类处理（`block_loop_detected`）等事件时，应用内就会弹出提示框，显示工作节点的交接信息（摘要、阻塞原因或错误详情），同时提供“打开看板”的操作选项。当您离开 Hermes 窗口时，同样的事件还会触发操作系统的原生通知（该功能可通过 **设置 ▸ 通知 ▸ 插件通知** 进行开关控制），因此即便您正在使用其他应用，有任务遇到阻塞情况也能及时获知。

生效范围：桌面端通知依赖于实时事件流，因此仅会在应用运行且启用了看板插件时触发。在应用关闭期间接收到的事件不会在下次启动时以通知形式再次呈现——若需要确保在应用关闭后仍能接收消息，可使用网关订阅功能（详见下文）。

## 网关端通知

当您通过网关（Telegram、Discord、Slack等）运行 `/kanban create …` 命令时，发起对话的聊天频道会自动被添加到新任务的订阅列表中。网关的后台通知机制会每隔几秒查询一次 `task_events`，针对每种终端事件（`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`）向该聊天频道发送一条消息。对于已完成的任务，系统还会发送工作者所使用的 `--result` 参数的第一行内容，这样您无需再执行 `/kanban show` 命令即可查看任务结果。

您也可以通过 CLI 显式管理订阅关系——当脚本或定时任务需要向非其发起来源的聊天频道发送通知时，这一功能尤为实用。

```bash
hermes kanban notify-subscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7 \
    --chat-type group --delivery-mode notify+wake
hermes kanban notify-list
hermes kanban notify-unsubscribe t_abcd \
    --platform telegram --chat-id 12345678 --thread-id 7
```

一旦任务状态变为 `done` 或 `archived`，订阅便会自动取消，无需进行任何清理操作。

### 传递模式

`--delivery-mode` 用于控制通知器对终端事件的响应方式。每个订阅都处于以下三种模式之一（默认且原始行为为 `notify` 模式）：

| 模式 | 被动消息 | 唤醒智能体 | 适用场景 |
|------|----------|------------|---------|
| `notify` | 是 | 否 | 仅希望在聊天中收到提示信息（默认模式）。 |
| `notify+wake` | 是 | 是 | 还希望目标智能体真正介入处理——读取对话上下文并以其自身风格回复。由聊天触发的自动订阅会使用此模式。 |
| `wake` | 否 | 是 | 仅希望智能体对事件作出响应，而不需要额外的通知。 |

对于 `notify+wake` 模式，只有当唤醒操作被加入适配器的处理队列且被动消息已被发送后，传递过程才算完成。若处理程序缺失、路由被拒绝或队列已满，系统会在后续的通知周期中重新尝试，而订阅不会因此失效。已发送的消息会在 SQLite 中单独记录检查点，因此被拒绝的唤醒操作不会重复已记录的检查点消息。`notify` 模式仍为被动模式，不会启动智能体的处理流程。即使消息被接收，也无法保证模型一定会执行或成功回复；常规的处理流程规则依然适用。这并非严格意义上的“一次性传递”：在消息发送与检查点记录之间若发生进程崩溃，消息可能会被重复发送，且现有的“先占式传递”机制并不具备崩溃恢复功能。

“唤醒”机制会向目标网关代理生成一条合成型入站消息，使其能够按照常规流程处理（读取备注与结果、分析原因并回复），而非仅接收简短被动通知。该机制仅在通知器在正在运行的网关进程内执行时才会触发；否则，包含“通知+唤醒”功能的订阅仍会发送被动消息，而仅有“唤醒”功能的订阅在该进程中则不会产生任何作用。

**哪些事件可触发唤醒？**那些会将决策结果反馈给发起方的事件，包括：`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`、`review_requested`（即工作者完成处理后通过`kanban_request_review`提交审核请求）以及`block_loop_detected`（任务在多次被阻塞后被转至“分类处理”阶段）。`status`、`archived`和`unblocked`这些状态虽会被传递，但不会触发唤醒——它们仅属于流程记录中的状态转换，而非决策结果。当`completed`或`review_requested`事件附带处理摘要时，该摘要会通过唤醒机制同步传递，从而使被唤醒的代理能够了解工作者的实际操作内容。

`--chat-type`（`dm` | `group` | `channel` | `thread`）用于记录消息的来源聊天类型，从而确保被唤醒的对话能对应到操作员的**真实**会话：`build_session_key`函数对群组、频道和讨论帖的处理方式与私信不同，因此不准确的`chat-type`值会导致唤醒请求被路由到另一个缺乏上下文的独立会话中。`/kanban`的自动订阅功能以及斜杠命令路径会自动处理这一点——只有通过脚本或cron手动订阅聊天时才需要手动设置该参数。若省略此参数，则保持现有的订阅状态不变（新订阅默认为`dm`类型）。

### 多配置文件设置：消息投递由对应配置文件负责

在“每个配置文件对应一个网关”的部署架构中（即一个调度器，分别为`writer`、`admin`等角色配置独立的网关进程——详见[多网关指南](https://github.com/NousResearch/hermes-agent/blob/main/docs/kanban/multi-gateway.md)），消息的调度与投递由不同的模块负责：

- **调度功能仅由单一节点负责**。恰好只有一个网关会将 `kanban.dispatch_in_gateway: true` 设为真值并运行调度器；其余所有网关则将该值设为 `false`。
- **通知发送由对应配置文件管理**。包括非调度类网关在内的所有网关都会运行通知器，并仅轮询那些其平台适配器所支持的配置文件所标记的订阅项。即便实际执行调度的是 `default` 网关，但通过 `writer` 配置文件的 Telegram 创建的任务，其 `completed`/`blocked` 状态消息仍会由 `writer` 网关负责发送。
- **仅用于路由的复用配置文件**：当订阅项中存储的平台、聊天窗口、线程、作用范围以及父频道标识等信息，通过 `gateway.profile_routes` 机制指向某个特定的已启用配置文件时，该配置文件可使用主适配器。已连接的备用适配器仍具有权威性；若备用适配器注册表不完整，系统绝不会回退到主机器人。那些未匹配、被重新分配、处于禁用状态或标识模糊的路由将无法发送消息，但可尝试重试。缺少必要路由标识的旧记录也不会被自动关联到某个配置文件中。`Wake turns` 功能会保留目标配置文件的运行时作用范围以及指定的传输方式。
- **在配置文件标记机制出现之前创建的旧版订阅项**（即相关记录中不存在 `notifier_profile` 字段），仅由持有实际调度器单例锁定的网关负责发送消息，因此两个网关之间不会发生竞争。
由于 BOARD 数据库中采用了针对每个事件的原子性声明机制，因此可避免在多个网关之间出现重复投递的情况。无需使用中继、共享凭证或额外的调度器——每个配置的网关只需通过自身的适配器进行投递即可。

## 执行记录——每次尝试对应一行数据

任务是工作的逻辑单元，而**执行记录**则代表执行该任务的一次尝试。当调度器获取到可执行的任务时，它会在 `task_runs` 表中创建一行记录，并将 `tasks.current_run_id` 指向该行。当此次尝试结束——无论是完成、阻塞、崩溃、超时、生成失败还是被回收——该执行记录都会带有相应的 `outcome` 字段被关闭，同时任务对应的指针也会被清空。一个已被尝试过三次的任务，会在 `task_runs` 表中生成三行记录。

为何要使用两张表而非直接修改任务数据：首先，为了便于进行实际问题分析，需要保留**完整的尝试历史**（例如“第二次审核者成功通过，第三次则完成了合并”）；其次，需要一个专门的地方来存储每次尝试的元数据——比如哪些文件被修改、运行了哪些测试、审核者记录了哪些发现。这些都属于执行相关的事实，而非任务本身的事实。

**结构化交接**功能也体现在执行记录中。当工作者通过 `kanban_complete()` 方法完成一项任务时，它可以传递：

- `summary`（工具参数）/ `--summary`（CLI命令）——用于人工交接；会在任务执行过程中传递，下游子任务可在其`build_worker_context`中获取该信息。  
- `metadata`（工具参数）/ `--metadata`（CLI命令）——可在任务执行期间使用的自由格式JSON字典；下游子任务会与摘要信息一同以序列化形式获取该数据。  
- `result`（工具参数）/ `--result`（CLI命令）——简短的日志行，会显示在任务行中（属于旧版字段，为保持向后兼容而保留）。  

下游子任务会读取每个父任务的最新已完成执行次的摘要信息及元数据。重试的任务处理节点则会查看自身任务之前的所有尝试记录（包括执行结果、摘要及错误信息），从而避免重复走已经失败过的路径。

```
# What a worker actually does — a tool call, from inside the agent loop:
kanban_complete(
    summary="implemented token bucket, keys on user_id with IP fallback, all tests pass",
    metadata={"changed_files": ["limiter.py", "tests/test_limiter.py"], "tests_run": 14},
    result="rate limiter shipped",
)
```

当您（人类操作员）需要完成工人无法处理的任务时，也可以通过 CLI 实现同样的交接流程——例如那些被放弃的任务，或是您在控制面板中手动标记为已完成的任务。

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

运行记录会显示在控制面板中（抽屉内的“运行历史”板块，每次尝试对应一行彩色条目），也会通过 REST API 提供（调用 `GET /api/plugins/kanban/tasks/:id` 可获取 `runs[]` 数组）。通过发送包含 `{status: "done", summary, metadata}` 参数的 `PATCH /api/plugins/kanban/tasks/:id` 请求，这些信息会被同时传递给内核，因此控制面板上的“标记完成”按钮功能与 CLI 命令具有同等效果。`task_events` 行会标注所属的 `run_id`，便于用户按尝试次数对事件进行分组；而 `completed` 事件会在其负载中嵌入简短摘要（长度限制为 400 字符），这样网关通知组件无需再次执行 SQL 查询即可呈现结构化信息。

**批量关闭的注意事项。** 命令 `hermes kanban complete a b c --summary X` 会被拒绝——因为结构化信息是针对单次运行而言的，将同一摘要复制到多个任务上几乎总是不正确的。不过，在处理“我已完成一批行政任务”这类常见场景时，不使用 `--summary`/`--metadata` 参数进行批量关闭仍然是可行的。

**因状态变更而恢复的运行记录。** 如果你在控制面板中将正在运行的任务从“运行中”状态拖动到其他状态（如“待处理”或直接回到“准备中”），或是归档了仍在运行的任务，该次运行将会以 `outcome='reclaimed'` 的状态结束，而不会成为孤立记录。当 `tasks.current_run_id` 为 `NULL` 时，`task_runs` 行始终处于终止状态，反之亦然——这一规则在 CLI、控制面板、调度器及通知组件中均保持一致。

**针对从未被认领的任务的合成运行记录。** 如果对一个从未被任何人认领的任务进行完成或阻塞操作（例如，操作员在控制台通过摘要信息关闭了一个处于“ready”状态的任务，或者CLI用户执行了`hermes kanban complete <ready-task> --summary X`命令），否则该任务的交接流程就会中断。为此，内核会插入一条持续时间为零的运行记录行（`started_at == ended_at`），并包含相关摘要、元数据及原因，从而确保尝试历史记录的完整性。`completed`/`blocked`事件中的`run_id`指的就是这一行记录。

**实时侧边栏刷新功能。** 当控制台的WebSocket事件流传来用户当前查看的任务的新事件时，侧边栏会自动重新加载内容（这是通过在其`useEffect`依赖列表中加入针对每个任务的事件计数器来实现的）。这样一来，无需再次关闭并打开侧边栏，即可查看任务的新运行记录或更新后的结果。

### 向前兼容性

在`tasks`表中预留了两列可为空的字段，用于v2版本的工作流路由功能：`workflow_template_id`（表示该任务所属的模板）以及`current_step_key`（表示该模板中当前处于激活状态的步骤）。v1版本的内核在路由处理时会忽略这些字段，但允许客户端自行填写，因此v2版本可以在无需再次修改数据结构的情况下新增路由功能。

## 事件参考

每次状态变更都会在`task_events`表中添加一行记录。每行记录可选地包含一个`run_id`，便于用户界面按尝试次数对事件进行分类。这些事件类型被分为三类，从而方便过滤操作（例如：`hermes kanban watch --kinds completed,gave_up,timed_out`）：

**生命周期事件**（表示作为逻辑实体的任务发生了哪些变化）：

| Kind | Payload | When |
|---|---|---|
| `created` | `{assignee, status, parents, tenant}` | Task inserted. `run_id` is `NULL`. |
| `promoted` | — | `todo → ready` because all parents hit `done`. `run_id` is `NULL`. |
| `claimed` | `{lock, expires, run_id}` | Dispatcher atomically claimed a `ready` task for spawn. |
| `completed` | `{result_len, summary?}` | Worker wrote `--result` / `--summary` and task hit `done`. `summary` is the first-line handoff (400-char cap); full version lives on the run row. If `complete_task` is called on a never-claimed task with handoff fields, a zero-duration run is synthesized so `run_id` still points at something. |
| `blocked` | `{reason, kind, recurrences}` | Worker or human flipped the task to `blocked`. `kind` is the typed block reason (`needs_input`, `capability`, `transient`, or `null` for a generic block); `recurrences` is the unblock-loop counter. Synthesizes a zero-duration run when called on a never-claimed task with `--reason`. |
| `dependency_wait` | `{reason, kind}` | Worker blocked with `kind=dependency` — the task is only waiting on another task, so it routes to `todo` (parent-gated, auto-promoted) instead of `blocked`. No human needed. |
| `block_loop_detected` | `{reason, kind, recurrences, limit}` | A task was unblocked and re-blocked for the same reason `BLOCK_RECURRENCE_LIMIT` times (default 2). Instead of landing in `blocked` again — where a cron would keep unblocking it — it routes to `triage` for a human decision, breaking the unblock↔re-block loop. |
| `unblocked` | — | `blocked → ready` (or `todo` if parents are still open), either manually or via `/unblock`. Resets the dispatcher's `consecutive_failures` but deliberately preserves `block_recurrences` so the loop breaker keeps its memory. `run_id` is `NULL`. |
| `archived` | — | Hidden from the default board. If the task was still running, carries the `run_id` of the run that was reclaimed as a side effect. |

**编辑操作**（由人工发起的变更，且不属于状态转换）：

| 类型 | 数据内容 | 触发时机 |
|---|---|---|
| `assigned` | `{assignee}` | 负责人发生变更（包括取消分配）。 |
| `edited` | `{fields}` | 标题或内容被更新。 |
| `reprioritized` | `{priority}` | 优先级发生改变。 |
| `status` | `{status}` | 通过控制面板拖放直接修改了状态（例如从 `todo` 变为 `ready`）。当从 `running` 状态拖出时，会包含对应运行的 `run_id`；否则 `run_id` 为 NULL。 |

**工作节点遥测数据**（用于记录执行过程，而非逻辑任务本身）：

| Kind | Payload | When |
|---|---|---|
| `spawned` | `{pid}` | Dispatcher successfully started a worker process. |
| `heartbeat` | `{note?}` | Worker called `hermes kanban heartbeat $TASK` to signal liveness during long operations. |
| `reclaimed` | `{stale_lock}` | Claim TTL expired without a completion; task goes back to `ready`. |
| `crashed` | `{pid, claimer}` | Worker PID no longer alive but TTL hadn't expired yet. |
| `timed_out` | `{pid, elapsed_seconds, limit_seconds, sigkill}` | `max_runtime_seconds` exceeded; dispatcher SIGTERM'd (then SIGKILL'd after 5 s grace) and re-queued. |
| `stale` | `{elapsed_seconds, last_heartbeat_at, heartbeat_age_seconds, timeout_seconds, pid, terminated}` | Task ran longer than `kanban.dispatch_stale_timeout_seconds` (default 4 h) AND no `kanban_heartbeat` arrived in the last hour. Dispatcher SIGTERM'd the host-local worker (if any), reset the task to `ready` for re-dispatch. Does NOT tick the failure counter (stale is dispatcher-side absence detection, not a worker fault). Workers running long operations should call `kanban_heartbeat` at least once an hour to avoid this. |
| `reconciled` | `{reason, claim_lock, claim_expires, worker_pid}` | Orphaned-card reconciliation: the card was `running` with broken claim bookkeeping (`claim_lock` or `claim_expires` NULL — crash mid-claim, manual SQL, DB restore) and no live worker, so none of the TTL/crash/stale paths could ever recover it. The dispatcher requeued it to `ready` with an explanatory comment. Gated by `kanban.reconcile_orphans` in config.yaml (default `true`). |
| `respawn_guarded` | `{reason}` | Dispatcher refused to re-spawn this ready task this tick. Reasons: `blocker_auth` (last failure was a quota/auth/429 error — wait for the rate window to reset), `recent_success` (a completed run happened in the last hour — wait for review before re-running), `active_pr` (a GitHub PR URL appears in a recent comment — a prior worker already opened a PR). The task stays in `ready`; the next tick gets another chance to spawn. If the underlying condition persists, the normal `consecutive_failures` circuit breaker will auto-block via `gave_up` after `failure_limit` failures. |
| `spawn_failed` | `{error, failures}` | One spawn attempt failed (missing PATH, workspace unmountable, …). Counter increments; task returns to `ready` for retry. |
| `protocol_violation` | `{pid, claimer, exit_code, protocol_violation}` | Worker exited successfully while the task was still `running`, usually because it answered without calling `kanban_complete` or `kanban_block`. Emitted on every violation (the payload's `protocol_violation: true` marker is copied into the run metadata and feeds the violation-only retry budget). Below the budget — up to `_PROTOCOL_VIOLATION_FAILURE_LIMIT` (default 3) *consecutive* violations, per-task `max_retries` overriding — the task simply returns to `ready` for another attempt; when the streak reaches the bound the dispatcher also emits `gave_up` and auto-blocks. |
| `gave_up` | `{failures, effective_limit, limit_source, error}` | Circuit breaker fired after N consecutive non-successful attempts. Task auto-blocks with the last error. The effective limit resolves as task `max_retries`, then dispatcher `failure_limit` / `kanban.failure_limit`, then the built-in default. |

`hermes kanban tail <id>` 可用于查看单个任务的这些信息。而 `hermes kanban watch` 则能实时推送整个看板上的相关数据。

## 不支持的功能

Kanban 模块刻意设计为单主机运行模式。`~/.hermes/kanban.db` 是一个本地的 SQLite 数据文件，调度器会在同一台机器上启动工作进程。目前不支持在两台主机之间共享看板——因为缺乏用于协调“主机 A 上的工作进程 X 与主机 B 上的工作进程 Y”之间交互的机制，且崩溃检测逻辑也假设进程 ID 仅存在于当前主机内。如果需要多主机部署，建议为每台主机单独运行一个看板，并通过 `delegate_task` 命令或消息队列来实现各看板之间的数据交互。

## 设计规范

关于该模块的完整设计内容——包括架构设计、并发正确性分析、与其他系统的对比、实施计划、潜在风险以及未解决的问题——均记载在 `docs/hermes-kanban-v1-spec.pdf` 文件中。在提交任何涉及功能变更的 Pull Request 之前，请务必先阅读该文档。
