# 看板工作通道

**工作通道**是指看板调度器可用于分配任务的流程类别。每个通道都具有唯一标识（即负责人字符串）、任务生成机制，以及针对已生成任务所需执行操作的规范。

本页面即为该规范，主要面向两类用户：

- **操作员**：负责决定在看板上启用哪些工作通道（即创建何种配置文件、使用哪位负责人）。
- **插件/集成开发人员**：希望添加新的工作通道类型（例如封装了 Codex / Claude Code / OpenCode 功能的 CLI 工作程序、基于容器的代码审查工作程序，或通过 API 获取任务的非 Hermes 服务）。

如果您正在编写工作通道内的实际执行代码——即运行在通道中的智能体，则应参考 [`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) 技能文档，其中包含更详细的实现步骤。

## 层级结构

```text
Hermes Kanban  =  canonical task lifecycle + audit trail
Worker lane    =  implementation executor for one assigned card
Reviewer       =  human or human-proxy that gates "done"
GitHub PR      =  upstreamable artifact (optional, for code lanes)
```

Hermes Kanban 负责维护任务全生命周期的状态真相——即 `ready` → `running` → `blocked` / `done` / `archived`。虽然各工作通道会执行具体任务，但并不拥有状态控制权；它们所做的一切都会通过 `kanban_*` 工具（对于非 Hermes 类型的外部工作器，则通过 API）反馈至 Kanban 核心。而审核人员则负责把控任务状态从“代码修改完成”向“任务结束”的过渡。

## 工作通道需提供的功能

要成为 Kanban 工作通道，一个集成必须提供以下三项功能：

### 1. 被分配者字符串

调度器会将 `task.assignee` 的值与 Hermes 配置文件中的名称（即默认的工作通道形式）或已注册的不可生成标识符（即插件工作通道形式——详见下文[添加外部 CLI 工作通道](#adding-an-external-cli-worker-lane)）进行匹配。那些无法确定被分配者的任务会停留在 `ready` 状态，并附带 `skipped_nonspawnable` 事件，以便看板操作员进行处理；系统不会默默丢弃这些任务，也不会让任何默认的备用工作器去执行它们。

### 2. 启动机制

对于 Hermes 配置文件类型的工作通道，调度器的 `_default_spawn` 函数会在任务的固定工作空间中运行 `hermes -p <assignee> chat -q <prompt>` 命令（如果 `$PATH` 环境变量中不存在 `hermes` shim，则会使用相应的模块形式），同时设置以下环境变量：

| 变量名 | 含义 |
|---|---|
| `HERMES_KANBAN_TASK` | 工作器正在处理的任务 ID |
| `HERMES_KANBAN_DB` | 对应看板的 SQLite 数据文件的绝对路径 |
| `HERMES_KANBAN_BOARD` | 看板的唯一标识符 |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 看板工作空间树的根目录 |
| `HERMES_KANBAN_WORKSPACE` | 当前任务工作空间的绝对路径 |
| `HERMES_KANBAN_RUN_ID` | 当前运行次的 ID（用于生命周期状态判断） |
| `HERMES_KANBAN_CLAIM_LOCK` | 占用锁字符串，格式为 `<主机名>:<进程ID>:<UUID>` |
| `HERMES_PROFILE` | 工作器自身的配置文件名称（用于在评论中标注作者） |
| `HERMES_TENANT` | 如果任务属于特定租户，则为此租户的命名空间 |

对于通过插件注册的非 Hermes 类型工作通道，插件需提供自己的 `spawn_fn` 可调用函数，该函数接收 `task`、`workspace` 和 `board` 作为参数，并可返回一个可选的进程 ID，以便用于故障检测。

### 3. 生命周期终止机制

每一次任务处理都必须以以下三种情况之一作为结束标志：

- `kanban_complete(summary=..., metadata=...)`——任务处理成功，状态变为 `done`。
- `kanban_block(reason=...)`——任务需要等待人工输入，状态变为 `blocked`。当 `kanban_unblock` 被调用时，调度器会重新启动该工作器。
- 工作进程在未调用任何工具的情况下直接退出。此时 Kanban 核心会回收该进程，并发出 `crashed`（进程已死）、`gave_up`（连续失败保护机制触发）或 `timed_out`（超过最大运行时间）等信号。这是故障处理路径，正常工作的工作器不会以这种方式结束。

Kanban 核心会确保每次运行仅以其中一种方式结束。如果工作器既不调用上述任何函数又正常退出，系统会将其视为发生故障。

## 输出信息与需要审核的约定

对于大多数涉及代码修改的任务，工作器完成处理后任务并未真正“结束”——它仍需要人工审核。Kanban 核心并不强制区分这一点（“代码修改任务”的定义本身较为模糊），而且如果对所有处理代码的任务都强制使用“阻塞”而非“完成”状态，就会打乱那些不需要审核的工作流程。因此，业界形成了一些约定：

- **使用“阻塞”而非“完成”状态**，并在 `reason` 前加上 `review-required: ` 前缀，这样在控制面板或执行 `hermes kanban show` 命令时，该任务就会显示为待审核状态。
- **首先将结构化元数据写入 `kanban_comment` 中**，因为 `kanban_block` 只能存储人类可读的 `reason` 字段。评论是持久化的标注渠道——所有与审计相关的信息（如修改的文件、运行的测试、差异路径或 PR 链接、决策记录等）都应放在这里。
- **审核人员要么批准并解除阻塞**，这样工作器就会带着评论线程重新启动，以便后续处理；要么通过另一条评论要求进行修改，下一次工作器运行时就会将这条评论作为 `kanban_show` 显示内容的一部分。

[`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) 技能提供了针对 `kanban_complete`（真正意义上的终止性任务，如拼写错误修正、文档修改、研究报告撰写等）以及“需要审核”的阻塞模式的实战示例。

## 日志与审计追踪

调度器会将每个任务的输出日志（stdout/stderr）写入 `<board-root>/logs/<task_id>.log` 文件中。这些日志可以通过 Kanban 元数据进行查询：

- `task_runs` 表格中记录了 `log_path`、退出码（如有）、任务摘要以及各类元数据。
- `task_events` 表格则记录了所有的状态变化，包括 `promoted`、`claimed`、`heartbeat`、`completed`、`blocked`、`gave_up`、`crashed`、`timed_out`、`reclaimed`、`claim_extended` 等事件。
- `kanban_show` 命令可以同时返回这两类信息，因此审核人员或后续处理的工作器无需登录控制面板，即可查看任务的全历史记录。

控制面板会以摘要、元数据块以及退出状态标签的形式展示运行历史。CLI 用户可以执行 `hermes kanban tail <task_id>` 命令实时跟踪任务进度，或执行 `hermes kanban runs <task_id>` 查看该任务的历史尝试记录。

## 现有的工作通道类型

### Hermes 配置文件型工作通道（默认类型）

这是目前所有 Kanban 工作器所采用的形式：被分配者是一个配置文件名称，调度器会启动 `hermes -p <profile>` 命令，工作器则会自动加载 [`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md) 技能以及 `KANBAN_GUIDANCE` 系统提示块，并使用 `kanban_*` 工具来结束当前运行。除了定义配置文件外，无需其他额外设置。

在为你的工作集群创建配置文件时，请选择与希望由调度器路由到的*角色*相匹配的名称。调度器（如果存在的话）会通过 `hermes profile list` 命令来发现这些配置文件名称——系统并不预设固定的角色列表（关于调度器端的实现规则，可参阅 [`kanban-orchestrator`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-orchestrator/SKILL.md) 技能）。

### 调度器配置文件型工作通道

这是配置文件型工作通道的一种特殊形式：调度器也是一种 Hermes 配置文件，其工具集包含 `kanban` 功能，但不包含用于实现具体任务的 `terminal`、`file`、`code`、`web` 等功能。它的职责是通过 `kanban_create` + `kanban_link` 命令将高层次目标拆解为多个子任务，然后退后一步进行整体协调。调度器技能中包含了防止其出现不当行为的规则。

## 添加外部 CLI 工作通道

将非 Hermes 类型的 CLI 工具（如 Codex CLI、Claude Code CLI、OpenCode CLI、本地代码模型运行器等）作为 Kanban 工作通道来使用，目前还不存在现成的实现路径。虽然调度器的启动函数是可插拔的（`dispatch_once` 函数接受 `spawn_fn` 作为参数），插件也可以为非 Hermes 类型的被分配者注册自己的 `spawn_fn`，但相关的集成工作——如将 CLI 的退出码转换为 `kanban_complete`/`kanban_block` 调用、将 CLI 的工作空间/沙箱规范映射到调度器的 `HERMES_KANBAN_WORKSPACE` 环境变量中、处理身份认证及针对不同 CLI 的策略设置等——仍需由各个集成自行设计实现。

如果你考虑添加此类 CLI 工作通道，建议先提交一个问题，详细说明所使用的具体 CLI 工具以及你希望实现的流程。上述规则是所有此类工作通道必须遵守的约束条件；至于具体的实现方式（是为每种 CLI 创建单独的插件，还是使用一个可通过配置参数定制的通用 CLI 运行器插件），则尚无统一标准。

与此相关的问题记录为 [#19931](https://github.com/NousResearch/hermes-agent/issues/19931)，而针对 Codex 工具的已关闭但未合并的 PR 为 [#19924](https://github.com/NousResearch/hermes-agent/pull/19924)——这些记录描述了最初的架构设计方案，但并未最终实现相应的运行器功能。

## 调度器能够处理的故障模式

这样一来，工作通道的创建者就不必重复实现以下这些故障处理逻辑：

- **过期的占用锁有效期**——如果某个工作器获取了任务占用锁后，既不发送心跳信号，也不完成任务或触发阻塞状态，那么在经过 `DEFAULT_CLAIM_TTL_SECONDS`（默认为 15 分钟）的时间后，该占用锁就会被回收——但前提是该工作器进程确实已经死亡。如果工作器仍在运行（只是因为模型处理速度较慢，在一次无工具调用的 LLM 调用中花费了 20 多分钟），其占用锁只会被*延长*，而不会被回收；只有真正死亡的进程才会被回收。
- **工作器进程崩溃**——当某个工作器的本地进程 ID 消失时，`detect_crashed_workers` 函数会检测到这一情况并回收该进程；此时该任务的 `consecutive_failures` 计数器会增加，一旦达到失败保护阈值，任务可能会自动被阻塞。
- **运行级重试机制**——当任务需要重试时（在阻塞后、崩溃后或占用锁被回收后），工作器可以在用于结束任务的工具中使用 `expected_run_id` 参数，以便在发现自己的当前运行次已被替换时快速失败。
- **单任务最大运行时间限制**——`task.max_runtime_seconds` 参数设置了每次运行的最大墙钟时间限制，无论进程是否仍在运行都会被约束。这一机制可以捕获那些真正陷入死锁的工作器，否则由于占用锁延长机制，这类工作器仍可能继续运行。
- **滞留任务检测**——如果某个处于 `ready` 状态的任务，其被分配者在 `kanban.stranded_threshold_seconds` 时间段内（默认为 30 分钟）始终没有发起任何操作，那么在执行 `hermes kanban diagnostics` 命令时，系统会发出 `stranded_in_ready` 警告。如果滞留时间达到阈值的两倍，警告级别会上升为错误；达到六倍则上升为严重错误。这一机制可以一次性捕获因拼写错误导致的错误被分配者、已被删除的配置文件，以及外部工作器池出现故障等情况——它不依赖具体的任务标识，也不需要为每个看板单独维护允许列表。

## 相关内容

- [Kanban 概述](./kanban)——面向用户的入门介绍。
- [Kanban 教程](./kanban-tutorial)——结合控制面板的逐步操作指南。
- [`kanban-worker`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-worker/SKILL.md)——工作器进程所加载的技能模块。
- [`kanban-orchestrator`](https://github.com/NousResearch/hermes-agent/blob/main/skills/devops/kanban-orchestrator/SKILL.md)——负责协调工作的调度器相关内容。
