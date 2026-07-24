# 长期运行与后台系统

有四个系统在主对话循环之外并行运行。此处为快速参考；完整的开发者说明见 `AGENTS.md`，面向用户的文档则位于 `website/docs/user-guide/features/` 下。

### 任务委派 (`delegate_task`)

创建一个拥有独立上下文和终端会话的子代理。

- **单任务模式：** `delegate_task(goal, context)`。
- **批量模式：** `delegate_task(tasks=[{goal, ...}, ...])` 会并行执行多个子任务，其最大并发数受 `delegation.max_concurrent_children`（默认为 3）限制。
- **后台模式：** `delegate_task(background=true)` 会立即返回一个处理标识，并让主循环继续运行；子任务完成后，其结果会作为新的对话轮次重新加入对话。
- **角色类型：** `leaf`（默认值，不可再次委派）与 `orchestrator`（可创建自己的工作进程，其创建深度受 `delegation.max_spawn_depth` 限制）。
- **非持久化设计。** 即使处于后台运行的子任务也仅存在于当前进程内——若父进程退出，该子任务将会丢失。对于需要长期运行的任务，请使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。

配置项：位于 `config.yaml` 中的 `delegation.*`。

### 定时任务（Cron）

一种持久化调度器——由 `cron/jobs.py` 和 `cron/scheduler.py` 组成。可通过 `cronjob` 工具、`hermes cron` CLI（提供 `list`、`add`、`edit`、`pause`、`resume`、`run`、`remove` 等命令）或 `/cron` 斜杠命令来操作。

- **调度规则：** 可设置持续时间（如 `"30m"`、`"2h"`）、周期表达式（如 `"every monday 9am"`）、五字段 Cron 表达式（如 `"0 9 * * *"`）或 ISO 时间戳。
- **任务级配置选项：** 可指定使用的技能、覆盖默认的模型/提供方、预运行脚本（用于数据收集；若设置 `no_agent=True`，则该脚本即构成整个任务）、从某任务输出获取上下文以供另一任务使用、指定运行目录（该目录会加载对应的 `AGENTS.md`/`CLAUDE.md` 文件），以及支持跨平台执行。
- **固有约束：** 每次运行最多可被强制中断 3 分钟；`.tick.lock` 文件可防止不同进程间出现重复调度；Cron 任务默认会传递 `skip_memory=True` 参数；此外，Cron 任务的输出会以独立头部/尾部格式呈现，而不会直接镜像到目标网关的会话中，从而确保角色切换功能不受影响。

用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

### 技能管理器（技能生命周期管理）

用于对代理创建的技能进行后台维护。它会记录技能的使用情况，将长时间未使用的技能标记为过时，进而将其归档，并保留预运行时的 tar.gz 备份，确保数据不会丢失。

- **CLI 命令：** `hermes curator <动词>` — 支持 `status`、`usage`、`run`、`pause`、`resume`、`pin`、`unpin`、`archive`、`restore`、`list-archived`、`prune`、`backup`、`rollback` 等操作。
- **斜杠命令：** `/curator <子命令>` 功能与 CLI 相同。
- **作用范围：** 仅处理来源为 `created_by: "agent"` 的技能，预装或通过中心节点安装的技能不在管理范围内。该工具**绝不会删除**技能——最严厉的操作也仅为归档。被标记为“固定”的技能可免于所有自动转换和大型语言模型审查流程。
- **成本：** 定期进行的静态检查与过时清理操作是免费的。辅助模型用于“将重叠技能整合为汇总技能”的功能默认处于关闭状态——如需启用，可设置 `curator.consolidate: true` 或执行 `hermes curator run --consolidate`。常规的后台维护操作不会消耗任何计算资源。
- **监控数据：** 日志文件存储在 `~/.hermes/skills/.usage.json` 中，其中记录了每个技能的 `use_count`、`view_count`、`patch_count`、`last_activity_at`、`state` 和 `pinned` 等状态信息。

配置项：`curator.*`（包括 `enabled`、`interval_hours`、`min_idle_hours`、`stale_after_days`、`archive_after_days`、`backup.*` 等）。
用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/curator

### 看板系统（多代理工作队列）

这是一个基于 SQLite 的持久化看板工具，适用于多角色/多工作进程之间的协作。用户可通过 `hermes kanban <动词>` 来操作它；由调度器创建的工作进程会使用受 `HERMES_KANBAN_TASK` 控制的专用 `kanban_*` 命令集，而负责协调的角色则可选择使用更全面的 `kanban` 命令集。除非另有配置，普通会话不会包含任何 `kanban_*` 相关的架构元素。- **常用 CLI 命令：** `init`、`create`、`list`（别名 `ls`）、`show`、`assign`、`link`、`unlink`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`。较少使用的命令包括：`watch`、`stats`、`runs`、`log`、`dispatch`、`daemon`、`gc`。
- **工作节点/调度器工具集：** `kanban_show`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`；对于那些在非调度器启动的任务中仍明确启用 `kanban` 工具集的配置文件，还会额外提供用于看板路由的 `kanban_list` 和 `kanban_unblock` 命令。
- **调度器**默认在网关内部运行（设置 `kanban.dispatch_in_gateway: true`），其功能包括回收过期的任务声明、提升已准备就绪的任务优先级、以原子方式获取任务控制权，以及启动对应的配置文件。当任务连续启动失败达到 `failure_limit` 次后（默认值为 2，可通过 `kanban.failure_limit` 或每任务的 `max_retries` 参数进行配置），调度器会自动将该任务封锁。
- **隔离机制：** 看板构成了硬性隔离边界（工作节点的运行环境会固定包含 `HERMES_KANBAN_BOARD` 环境变量）；而租户则是在看板内部的一种软性命名空间，用于实现工作空间路径与内存键值的隔离。

用户文档地址：https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban
