# 看板工作流通道

**工作流通道**是指看板调度器可用于分配任务的流程类别。每个通道都具有唯一标识（即负责人字符串）、任务生成机制，以及针对接收任务后需执行操作的规范。

本页面即为上述规范文档，主要面向两类用户：

- **操作员**：负责决定在看板上配置哪些工作流通道（即创建何种角色配置、使用哪位负责人）。
- **插件/集成开发人员**：希望新增自定义工作流通道类型（例如封装了 Codex / Claude Code / OpenCode 功能的 CLI 工作进程、基于容器的代码审查工作进程，或通过 API 获取任务的非 Hermes 服务）。

如果您正在编写工作流通道内的实际执行代码——即运行在通道中的智能体——看板生命周期及相关参考信息会自动注入到该智能体的系统提示词中（位于 [`agent/prompt_builder.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/prompt_builder.py) 文件中的 `KANBAN_GUIDANCE` 块）。

## 层级结构

```text
Hermes Kanban  =  canonical task lifecycle + audit trail
Worker lane    =  implementation executor for one assigned card
Reviewer       =  human or human-proxy that gates "done"
GitHub PR      =  upstreamable artifact (optional, for code lanes)
```

Hermes Kanban 负责维护任务的完整生命周期状态——即 `ready` → `running` → `blocked` / `done` / `archived`。虽然各工作通道会执行具体任务，但并不拥有这些状态控制权；它们所做的一切操作都会通过 `kanban_*` 工具（对于非 Hermes 类型的外部工作通道，则通过 API）反馈至 Kanban 核心。而审核人员则负责把控任务状态从“代码修改完成”向“任务结束”的转换。

## 工作通道需要提供的功能

要成为 Kanban 工作通道，某个集成必须提供以下三项功能：

### 1. 被分配者标识字符串

调度器会将 `task.assignee` 的值与 Hermes 配置文件中的名称（即默认的工作通道形式）或已注册的不可实例化标识符（即插件型工作通道形式——详见下文[添加外部 CLI 工作通道](#adding-an-external-cli-worker-lane)）进行匹配。那些无法解析出被分配者的任务会保持 `ready` 状态，并附带 `skipped_nonspawnable` 事件，以便看板管理员进行处理；这些任务不会被悄悄丢弃，也不会由任何默认的备用机制来执行。

### 2. 实例化机制

对于 Hermes 配置文件型工作通道，调度器的 `_default_spawn` 函数会在任务对应的固定工作空间中运行 `hermes -p <assignee> chat -q <prompt>` 命令（如果 `$PATH` 环境变量中不存在 `hermes` shim，则会使用相应的模块形式），同时设置以下环境变量：

| 变量名 | 含义 |
|---|---|
| `HERMES_KANBAN_TASK` | 工作通道当前正在处理的任务 ID |
| `HERMES_KANBAN_DB` | 对应看板的 SQLite 数据文件的绝对路径 |
| `HERMES_KANBAN_BOARD` | 看板的唯一标识符（slug） |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 看板所有工作空间的根目录 |
| `HERMES_KANBAN_WORKSPACE` | 当前任务对应工作空间的绝对路径 |
| `HERMES_KANBAN_RUN_ID` | 当前运行迭代的 ID（用于生命周期状态判断） |
| `HERMES_KANBAN_CLAIM_LOCK` | 占用锁字符串，格式为 `<主机名>:<进程ID>:<UUID>` |
| `HERMES_PROFILE` | 工作通道自身的配置文件名称（用于在评论中标注作者身份） |
| `HERMES_TENANT` | 如果任务属于某个租户，则为其对应的命名空间 |

对于通过插件注册的非 Hermes 类型工作通道，插件会提供自己的可调用函数 `spawn_fn`，该函数接收 `task`、`workspace` 和 `board` 作为参数，并可选择性地返回一个进程 ID，以便用于故障检测。

### 3. 生命周期终止机制

每一次任务处理必须以以下其中一种方式结束：

- `kanban_complete(summary=..., metadata=...)`——任务处理成功，状态变为 `done`。
- `kanban_block(reason=...)`——任务需要等待人工干预，状态变为 `blocked`。当 `kanban_unblock` 被调用时，调度器会重新启动该工作通道。
- 工作进程在未调用任何工具的情况下直接退出。此时 Kanban 核心会终止该进程，并发出 `crashed`（进程已死）、`gave_up`（连续失败保护机制触发）或 `timed_out`（超过最大运行时间）等信号。这是故障处理路径，正常工作的通道不会以这种方式结束。

Kanban 核心会确保每次运行迭代中只会有其中一种方式终止任务。如果某个工作通道既没有调用上述任何终止函数又正常退出，系统会将其视为发生故障。

## 输出信息与需要审核的任务处理规范

对于大多数涉及代码修改的任务，工作通道完成处理后并不代表任务就真正“结束”——它仍需要人工审核。Kanban 核心并未强制要求做到这一点（“代码修改任务”的定义本身较为模糊），而且如果对所有处理代码的任务都强制使用 `block` 而非 `complete`，就会打乱那些不需要审核的工作流程。因此，业界形成了一套额外的处理规范：

- **使用 `block` 而非 `complete`**，并在状态原因前加上 `review-required: ` 前缀，这样在控制面板或执行 `hermes kanban show` 命令时，该任务就会显示为“等待审核”状态。
- **首先在 `kanban_comment` 中写入结构化的元数据**，因为 `kanban_block` 只能存储人类可读的原因文本。评论是用于持久记录信息的渠道——所有与审计相关的字段（如修改的文件列表、运行的测试、差异对比路径或 PR 链接、决策记录等）都应放在评论中。
- **审核人员要么批准并解除阻塞**，这样工作通道就会重新启动，并保留相应的评论记录以便后续跟进；要么通过另一条评论要求对任务进行修改，下一次工作通道运行时就会将这些修改内容作为 `kanban_show` 显示的上下文信息。

系统会自动向工作通道注入 `KANBAN_GUIDANCE` 指引，其中既包含用于真正结束任务的 `kanban_complete` 模式（适用于修正拼写错误、更新文档、撰写研究报告等场景），也包含需要审核的 `review-required` 块模式。

## 日志与审计追踪

调度器会将每个任务对应的worker标准输出/标准错误信息写入路径为 `<board-root>/logs/<task_id>.log` 的文件中。通过 Kanban 元数据也可以查看这些日志：

- `task_runs` 表格中记录了日志文件路径、退出码（如有）、任务摘要以及相关元数据。
- `task_events` 表格则记录了所有的状态变化事件，包括 `promoted`、`claimed`、`heartbeat`、`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`、`reclaimed`、`claim_extended` 等。
- `kanban_show` 命令可以同时返回这两类信息，因此审核人员或后续处理任务的工作通道无需登录控制面板，即可查看完整的任务历史记录。

控制面板会以摘要、元数据块以及退出状态标签的形式展示任务运行历史。CLI 用户可以执行 `hermes kanban tail <task_id>` 命令实时跟踪任务进展，或执行 `hermes kanban runs <task_id>` 查看该任务的历史处理记录。

## 现有的工作通道类型

### Hermes 配置文件型工作通道（默认类型）

这是目前所有 Kanban 工作通道所采用的形式：被分配者是一个配置文件名称，调度器会启动 `hermes -p <profile>` 命令来实例化工作通道，工作通道会自动收到系统注入的 `KANBAN_GUIDANCE` 指引内容，并使用 `kanban_*` 工具来结束当前任务处理。除了定义相应的配置文件外，无需其他额外设置。

在为你的任务队列创建配置文件时，请选择能够准确反映你希望调度器将其路由到的“角色”类型的名称。调度器（如果存在的话）会通过执行 `hermes profile list` 命令来发现这些配置文件名称——系统并不预设固定的角色列表（调度器相关的规则也包含在注入的 `KANBAN_GUIDANCE` 指引中）。

### 调度器型配置文件工作通道

这是配置文件型工作通道的一种特殊形式：调度器本身也是一个 Hermes 配置文件，其工具集包含 `kanban` 功能，但不包含 `terminal`、`file`、`code`、`web` 等用于具体任务执行的工具。调度器的职责是通过 `kanban_create` + `kanban_link` 命令将高层级目标拆解为多个子任务，然后逐步退后监督执行过程。调度器相关的技能模块则负责制定防止工作通道偏离既定流程的规则。

## 添加外部 CLI 工作通道

目前，将非 Hermes 类型的 CLI 工具（如 Codex CLI、Claude Code CLI、OpenCode CLI、本地代码模型运行工具等）作为 Kanban 工作通道来使用，还尚未形成标准化的实现路径。虽然调度器的实例化函数是可插拔的（`dispatch_once` 函数接受一个 `spawn_fn` 参数），插件也可以为非 Hermes 类型的被分配者注册自己的 `spawn_fn`，但相关的集成工作——比如将 CLI 的退出码转换为 `kanban_complete`/`kanban_block` 调用、将 CLI 的工作空间/沙箱规范映射到调度器的 `HERMES_KANBAN_WORKSPACE` 环境变量中、处理身份认证及针对不同 CLI 工具的策略配置等——仍然需要各集成开发者自行设计实现。

如果你考虑添加此类 CLI 工作通道，建议先提交一个问题，详细说明所使用的具体 CLI 工具以及你希望实现的流程。上述规则是所有此类工作通道必须遵守的约束条件，而具体的实现方式（是为每个 CLI 工具单独开发一个插件，还是使用一个通用的 CLI 运行插件并通过配置参数进行定制）则尚无固定标准。

与此相关的历史问题可参考 [#19931](https://github.com/NousResearch/hermes-agent/issues/19931)，以及已关闭但未被合并的针对 Codex 工具的专用 PR [#19924](https://github.com/NousResearch/hermes-agent/pull/19924)——这些内容描述了最初的架构设计思路，但最终并未实现相应的运行工具。

## 调度器能够处理的故障模式

这样一来，工作通道的开发者就不必重复实现以下这些故障处理逻辑：

- **过期的占用锁有效期**——如果某个工作通道获取了任务占用锁后，既不发送心跳信号，也不完成任务处理或触发阻塞状态，那么在经过 `DEFAULT_CLAIM_TTL_SECONDS`（默认为 15 分钟）的时间后，该占用锁就会被回收。不过，只有当工作进程确实已经死亡时才会发生回收；如果只是因为模型响应较慢，在一次无需使用工具的 LLM 调用中花费了 20 多分钟，那么该占用锁只会被“延长”有效期，而不会被立即回收。
- **工作进程崩溃**——当某个工作进程在本地主机上的进程 ID 不再存在时，`detect_crashed_workers` 函数会检测到这种情况并终止该进程；此时该任务对应的 `consecutive_failures` 计数器会增加，一旦达到失败保护阈值，任务就会自动被阻塞。
- **运行迭代级重试**——当某个任务需要重试时（例如在阻塞后、崩溃后或占用锁被回收后），工作通道可以在使用终止工具时通过 `expected_run_id` 参数来快速判断：如果当前正在运行的迭代已经被替换，那么就可以直接终止当前处理。
- **单次任务的最大运行时间限制**——通过 `task.max_runtime_seconds` 参数可以设定每次任务处理的最大墙钟时间，这一限制与进程是否仍在运行无关。它能够捕获那些确实陷入死锁的工作进程，否则即使进程 ID 仍然存在，这些进程也可能会继续运行。
- **滞留任务检测**——如果某个处于 `ready` 状态的任务，其被分配者始终在 `kanban.stranded_threshold_seconds`（默认为 30 分钟）的时间范围内没有发起任何操作，那么在执行 `hermes kanban diagnostics` 命令时，系统会发出 `stranded_in_ready` 警告。如果滞留时间达到阈值的两倍，警告级别会上升为错误；达到六倍则升级为严重错误。这一机制可以一次性捕获因拼写错误导致的被分配者问题、配置文件被删除的情况，以及外部工作池出现故障的情形——它无需依赖具体的任务看板列表，因此具有更强的通用性。

## 相关资源

- [Kanban 概述](./kanban)——面向用户的入门介绍。
- [Kanban 教程](./kanban-tutorial)——结合控制面板的逐步操作指南。
- [`KANBAN_GUIDANCE`](https://github.com/NousResearch/hermes-agent/blob/main/agent/prompt_builder.py)——注入到每个 Kanban 工作通道系统提示语中的、用于指导工作通道及调度器行为的相关指引内容。
