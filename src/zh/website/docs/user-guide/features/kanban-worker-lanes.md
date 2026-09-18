# 看板工作通道

**工作通道**是看板调度器用于分配任务的一类流程。每个通道都具有唯一标识（即负责人字符串）、任务生成机制，以及针对已生成任务应执行操作的规范。

本页面即为该操作规范，主要面向两类用户：

- **操作员**：负责决定在看板上配置哪些工作通道（需创建哪些配置文件、使用哪些负责人）。
- **插件/集成开发人员**：希望添加新的工作通道类型（如封装了Codex/Claude Code/OpenCode的CLI工作程序、容器化审核工作程序，或通过API获取任务的非Hermes服务）。

如果您正在编写工作通道内的实际执行代码——即运行在通道中的智能体——看板生命周期及相关参考信息会自动注入到该智能体的系统提示词中（位于[`agent/prompt_builder.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/prompt_builder.py)文件中的`KANBAN_GUIDANCE`模块）。

## 层级结构

```text
Hermes Kanban  =  canonical task lifecycle + audit trail
Worker lane    =  implementation executor for one assigned card
Reviewer       =  human or human-proxy that gates "done"
GitHub PR      =  upstreamable artifact (optional, for code lanes)
```

Hermes Kanban掌控着任务的全生命周期状态——从`ready`到`running`，再到`review`/`blocked`/`done`/`archived`。工作通道虽负责执行任务，但并不拥有这些状态信息；它们所执行的操作都会通过`kanban_*`工具（对于非Hermes的外部工作通道，则通过API）反馈至Kanban核心系统。审核人员则负责把控任务状态从“代码已编写”过渡到“任务已完成”的流程。

## 工作通道的功能职责

要成为Kanban工作通道，某个集成必须提供以下三项功能：

### 1. 负责人字符串

调度器会将`task.assignee`的值与Hermes用户配置文件名称（即默认的工作通道形式）或已注册的不可生成标识符（即插件型工作通道形式——详见下文的[添加外部CLI工作通道](#adding-an-external-cli-worker-lane)）进行匹配。那些无法确定负责人的任务会保持`ready`状态，并触发`skipped_nonspawnable`事件，以便看板管理员进行处理；这些任务不会被悄悄忽略，也不会由任何默认机制擅自执行。

### 2. 任务启动机制

对于Hermes用户配置文件类型的工作通道，调度器的 `_default_spawn` 函数会在任务的固定工作空间中运行 `hermes -p <assignee> chat -q <prompt>` 命令（如果 `$PATH` 环境变量中不存在 `hermes` shim，则会使用相应的模块形式），同时设置以下环境变量：

| 变量 | 含义 |
|---|---|
| `HERMES_KANBAN_TASK` | 工作节点正在处理的任务编号 |
| `HERMES_KANBAN_DB` | 各看板对应的 SQLite 文件的绝对路径 |
| `HERMES_KANBAN_BOARD` | 看板的唯一标识符 |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 该看板下工作空间树的根目录 |
| `HERMES_KANBAN_WORKSPACE` | 当前任务对应工作空间的绝对路径 |
| `HERMES_KANBAN_RUN_ID` | 当前运行任务的编号（用于生命周期控制） |
| `HERMES_KANBAN_CLAIM_LOCK` | 占用锁字符串（格式为 `<主机名>:<进程ID>:<UUID>`） |
| `HERMES_PROFILE` | 工作节点自身的配置文件名称（用于标注 `kanban_comment` 的作者信息） |
| `HERMES_TENANT` | 若任务属于特定租户，则为此租户的命名空间 |

对于通过插件注册的非 Hermes 流道，相关插件会提供自己的 `spawn_fn` 可调用函数，该函数接收 `task`、`workspace` 和 `board` 参数，并返回一个可选的进程 ID 以用于故障检测。

### 子进程作用域

任务分配属于调度工作节点，而非它启动的每一个程序。Hermes 的子进程辅助工具会将“非所有者隔离机制”应用到 shell、执行内核、cron 定时任务、钩子函数、语言服务器以及普通的 stdio MCP 服务器中。即便脚本移除了继承来的任务编号，这些子进程仍会保持隔离状态：此时对 CLI 和工具的修改请求会被拒绝，该脚本也不会被视为任务协调器。同时，看板/数据库路由信息及工作空间路径依然保留。子进程无需执行架构迁移即可读取现有的看板，但看板的所有者必须负责对其进行初始化。

调度器会明确为新分配的工作者授予独立的运行时作用域。受管理的Hermes-tools MCP端点同样可以代表其上级工作者执行任务，而执行者的普通子进程则仍会被限制在相应作用域内。工作者仅能处理任务生命周期的交接以及向所负责的任务附加文件；“解封”操作则仍仅限于编排者使用。跨任务评论及后续任务的创建功能将保持原有的行为模式。

负责编写集成代码的开发人员应在实际启动进程时，先合并各种环境覆盖设置，再使用`agent.delegation_context.delegated_child_subprocess_env`参数。该方式能够保留调用者的身份凭证与配置策略。这属于协作式的运行时作用域管理，**并非操作系统层面的限制**：它无法阻止恶意代码故意清除任务溯源元数据或直接访问SQLite数据库。

### 3. 生命周期终止机制

每个任务都必须以以下两种情况之一作为结束标志：

- `kanban_complete(summary=..., metadata=...)` — 任务完成，状态变为 `done`。
- `kanban_request_review(summary=..., metadata=..., reviewer=...)` — 同卡片实现工作已完成并进入正式审查阶段；状态变为 `review`。除非禁用了 `kanban.review_dispatch`，否则调度器会加载预置的 `sdlc-review` 技能。审查者可通过 `kanban_complete` 批准任务，使用 `kanban_request_changes` 提出可操作的修改建议，或通过 `kanban_block` 上报真正的外部阻碍问题。
- `kanban_block(reason=...)` — 任务需等待人工干预，状态变为 `blocked`。当执行 `kanban_unblock` 时，调度器会重新启动该任务。
- 工作进程在未调用任何工具的情况下退出。内核会检测到这种情况，并发出 `crashed`（进程崩溃）、`gave_up`（连续失败保护机制触发）或 `timed_out`（超过最大运行时间）等信号。这是任务失败的路径；正常运行的工作进程不会以这种方式结束。

Kanban 内核会确保每次运行中恰好有一个此类操作被执行。那些既不调用这些操作又正常退出的工作进程会被视为已崩溃。

## 输出与审查交接

对于涉及代码修改的任务，需根据任务图所指定的模型来选择相应的审查流程：

- **同一卡片评审**：调用 `kanban_request_review(summary=..., metadata=..., reviewer=...)`。任务将直接进入“评审”状态，而不会影响任务重复处理的核算逻辑。调度器默认会使用内置的 `sdlc-review` 技能来处理该任务。评审人可通过 `kanban_complete` 批准任务，或调用 `kanban_request_changes(reason=...)` 结束评审流程并将任务转回给原执行者；仅在遇到真正需要外部介入的情况时才对任务进行阻塞。
- **预先创建的下游评审/测试/发布卡片**：使用 `kanban_show` 可查看子卡片的 ID，在确定最终操作前，可通过 `kanban_show(task_id=...)` 查看这些卡片。如果某个子卡片属于下游的评审/测试/发布阶段，则需在对应的执行阶段调用 `kanban_complete`。在该父卡片被标记为“已完成”或“已归档”之前，子卡片无法升级状态。切勿重复请求同一卡片的评审，也绝不能用 `review-required:` 对父卡片进行永久阻塞——这两种做法都可能导致下游任务流程受阻或出现重复处理。
- **仅限人工处理的看板**：将 `kanban.review_dispatch: false` 设为值。这样，任务就可以一直处于“评审”状态，直到有专人批准，或通过 `reopen-review` 功能及控制面板将其恢复到“准备中”或“待办”状态。

这两种评审模式均会在任务生命周期状态转换时实现结构化的交接。请勿在 `summary` 或 `metadata` 中存放敏感信息、令牌或原始个人身份信息，因为相关记录是持久保存的。

注入的 `KANBAN_GUIDANCE` 规则涵盖了两种图表结构、`kanban_complete` 操作、同一卡片评审循环，以及针对真正阻塞情况的 `kanban_block` 功能。

## 日志与审计追踪

调度器会将每个任务的工作者标准输出/标准错误内容写入 `<board-root>/logs/<task_id>.log` 文件中。通过看板元数据即可查看这些日志：

- `task_runs` 行包含 `log_path`、退出码（如有）、摘要以及相关元数据。
- `task_events` 行记录了所有的状态变化，包括 `promoted`、`claimed`、`heartbeat`、`completed`、`blocked`、`review_requested`、`changes_requested`、`review_reopened`、`gave_up`、`crashed`、`timed_out`、`reclaimed`、`claim_extended` 等。
- `kanban_show` 函数会同时返回这两类信息，因此审核人员或后续处理的工作者无需登录控制台，即可查看该任务的完整历史记录。

控制台以摘要、元数据块以及退出状态标签的形式展示任务执行历史。CLI 用户可以使用 `hermes kanban tail <task_id>` 实时跟踪任务进展，或使用 `hermes kanban runs <task_id>` 查看历史任务记录列表。

## 现有的通道类型

### Hermes 配置文件通道（默认）

这是目前所有看板工作者所采用的格式：负责人为配置文件名称，调度器会启动 `hermes -p <profile>` 命令，工作者会自动获得注入的 `KANBAN_GUIDANCE` 系统提示块，并可使用 `kanban_*` 工具来终止任务执行。除了定义配置文件外，无需其他额外设置。

在为你的任务队列创建配置文件时，请选择与希望调度器分配的任务*角色*相匹配的名称。调度器（如有）会通过 `hermes profile list` 命令来发现这些配置文件名称——系统并不预设固定的角色列表（合约中的调度器相关部分包含在注入的 `KANBAN_GUIDANCE` 中）。

### 编排器专责通道

这是“通道”概念的一种特殊形式：编排器是一种Hermes配置文件，其工具集包含`kanban`功能，但不包含用于实际执行的`terminal`/`file`/`code`/`web`等功能。它的职责是通过`kanban_create` + `kanban_link`将高层目标拆解为子任务，然后退后一步进行监控。编排器技能则用于定义防止操作偏差的规则。

## 添加外部CLI工作线程通道

将非Hermes CLI工具（如Codex CLI、Claude Code CLI、OpenCode CLI、本地代码模型运行器等）作为看板工作线程来使用，目前尚无现成的实现方案。调度器的任务生成函数是可插拔的（`spawn_fn`是`dispatch_once`函数的一个参数），插件可以为非Hermes类型的执行者注册自己的`spawn_fn`，但相关的集成工作——如将CLI的退出码转换为`kanban_complete`/`kanban_block`调用、将CLI的工作区/沙箱规范映射到调度器的`HERMES_KANBAN_WORKSPACE`环境变量、处理身份认证及针对不同CLI的策略设置等——仍需根据具体集成场景进行设计。

如果您考虑添加CLI通道，请提交一个问题，详细说明所使用的具体CLI工具以及您希望实现的工作流程。上述要求是所有此类通道必须满足的约束条件；至于实现方式（是为每个CLI创建单独插件，还是使用可通过配置参数化的通用CLI运行器插件），则尚无定论。

该问题的历史记录可见于 [#19931](https://github.com/NousResearch/hermes-agent/issues/19931)，以及已被关闭但未合并的针对 Codex 的 PR [#19924](https://github.com/NousResearch/hermes-agent/pull/19924)——这些文档描述了最初的架构设计方案，但并未最终被采用。

## 分发器可处理的故障模式

这样一来，任务创建者便无需重复实现以下功能：

- **过期的声明有效期**——那些已发起请求却始终不发送心跳、不完成任务也不进入阻塞状态的 worker，在经过 `DEFAULT_CLAIM_TTL_SECONDS`（默认为15分钟）后会被回收，但前提是该 worker 进程确实已经死亡。如果 worker 仍在运行（例如由于模型响应缓慢，在单次无工具辅助的 LLM 调用中耗时超过20分钟），其声明有效期反而会得到延长而非被终止；只有真正死亡的进程才会被回收。
- **崩溃的 worker**——当 `detect_crashed_workers` 检测到本地 PID 已消失的 worker 时，系统会立即回收该进程；此时相关任务的“连续失败次数”会增加，且一旦触发故障保护机制，任务可能会自动进入阻塞状态。
- **运行级重试**——在任务被重试时（无论是在阻塞后、崩溃后还是回收后），worker 可以利用终止工具时的 `expected_run_id` 参数，快速判断自身当前的任务运行是否已被替代，从而及时终止任务。
- **单任务最大运行时间限制**——无论进程是否存活，`task.max_runtime_seconds` 都会对每次任务的实时时长设置硬性上限。这一机制能够拦截那些真正陷入死锁的 worker，否则凭借“活跃 PID”机制，这类 worker 仍可能继续运行。
- **停滞任务检测**——若某个已处于待处理状态的任务，其负责人在 `kanban.stranded_threshold_seconds`（默认为30分钟）内始终未提交任何处理记录，该任务会在 `hermes kanban diagnostics` 中以 `stranded_in_ready` 警告的形式显示出来。当超时时间达到阈值的两倍时，警告级别会升级为错误；达到六倍时则变为严重错误。该功能可通过单一信号检测到负责人输入错误、个人资料被删除以及外部工作者池故障等问题，且无需识别具体身份，也不需要为每个看板单独设置允许列表。
- **旧版审核依赖死锁**——当某个带有 `review-required:` 标记的父任务处于阻塞状态，而其一个或多个直接子任务仍被限制在 `todo` 状态时，系统会立即触发 `review_dependency_deadlock` 错误。相关诊断信息为只读性质：它仅建议完成已完成阶段或解除错误关联，而不会自动解除对用户的限制。

## 相关内容

- [看板概览](./kanban)——面向用户的入门介绍。
- [看板教程](./kanban-tutorial)——结合仪表板操作的逐步指导。
- [`KANBAN_GUIDANCE`](https://github.com/NousResearch/hermes-agent/blob/main/agent/prompt_builder.py)——嵌入到每个看板工作者系统提示词中的工作者与协调器生命周期相关内容。
