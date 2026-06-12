# 监控——实时观察流水线并及时干预

在 `setup.sh` 启动看板后，相关工作将自动运行。该技能在执行阶段的作用在于帮助用户（以及负责监督会话的 AI）尽早发现问题，并采取有效措施进行干预。

## 实时监控命令

```bash
# Live event stream — task spawns, status changes, heartbeats, completions
hermes kanban watch --tenant <project-slug>

# Snapshot of the board
hermes kanban list --tenant <project-slug>
hermes kanban list --tenant <project-slug> --json     # machine-readable

# Per-status counts + oldest-ready age
hermes kanban stats --tenant <project-slug>

# Visual dashboard (browser)
hermes dashboard

# Inspect a specific task (includes comments + events)
hermes kanban show <task-id>

# Follow a single task's event stream
hermes kanban tail <task-id>
```

可使用 `hermes kanban --help` 查看可用的子命令——该看板 CLI 提供了 `init / create / list / show / assign / link / unlink / claim / comment / complete / block / unblock / archive / tail / dispatch / watch / stats / heartbeat / log / runs / context / gc` 等功能。

配套的 `scripts/monitor.py` 脚本会通过 CLI 定期轮询看板状态，并及时暴露常见问题（如任务卡住、心跳信号缺失、重复重试、依赖关系死锁等）。

## 需要关注的指标

### 正常的流水线状态指示

- 任务会按照大致预期的顺序从 `READY → RUNNING → DONE` 转换
- 渲染器会定期发送包含进度信息的 `kanban_heartbeat` 事件（例如“当前帧号：240/720”）
- 每个任务的运行时间均远低于设定的 `max_runtime_seconds` 上限
- 无任务的重试次数超过1次
- 依赖关系箭头能够正常解析（父任务完成后，子任务即可解除阻塞）

### 警示信号

| 症状 | 可能原因 | 应对措施 |
|------|----------|----------|
| 任务处于 `RUNNING` 状态，但2分钟以上无心跳信号 | 工作节点卡住、陷入无限循环或等待输入数据 | 使用 `hermes kanban show <id>` 查看工作节点的最新事件。调度器会自动对超过 `max-runtime` 的任务发送 SIGTERM 信号终止其运行；若需提前停止，可先执行 `hermes kanban block <id>`，再执行 `hermes kanban archive <id>`，随后创建新的任务重新运行。 |
| 同一任务被重试2次以上 | 存在可重复出现的故障（如缺失关键参数、规格错误或工具故障） | 使用 `hermes kanban show <id>` 查看故障相关事件。在重新运行任务之前需先解决根本原因。 |
| 任务运行时间超过 `max_runtime` 上限 | 任务处理速度较慢但仍在推进，或确实已卡住 | 使用 `hermes kanban tail <id>` 查看心跳信号。如果任务仍在正常推进，调度器最终仍会发送 SIGTERM 信号——此时可提高新创建任务的 `max_runtime` 值。 |
| 子任务显示为 `READY` 状态，但父任务仍处于 `RUNNING` 状态且耗时超过预期值的2倍 | 任务级联处理速度过慢，或依赖关系配置错误 | 检查依赖关系图。同时检查父任务：有时父任务虽已完成，但其传递的摘要、元数据等信息为空，导致子任务无内容可处理。 |
| 新任务未出现在列表中 | Director 在任务分解过程中卡住 | 使用 `kanban show` 命令查看 Director 相关任务。这通常是由于 `kanban_create` 调用格式有误所致。 |
| 专项任务瞬间完成 | 分解生成的任务缺少实际内容 | Director 传递的上下文信息不足。需重新创建任务，并明确指定任务内容。 |
| 任务虽已创建却未被调度处理 | Profile 未运行、租户配置不匹配或调度器未启动 | 检查 `hermes profile list`（Profile 是否存在？）、`hermes status`（网关/调度器是否正常运行？），并确认租户信息是否正确。 |
| 某个渲染任务失败 → 查看评审备注 → 渲染器重新处理 → 又再次失败 | 任务需求本身不切实际 | 应调整任务需求，而非责备渲染器。 |

## 应对方案

### 拒绝不合格的输出结果

当渲染器输出的片段未能通过审核时：

```bash
# 1. Comment on the renderer's task with specific feedback
hermes kanban comment <renderer-task-id> "Scene 3 looks too sparse \
— increase visual density. Tighten color palette to brand spec."

# 2. Create a re-render task with the original as parent
hermes kanban create "Scene 3 — re-render with feedback" \
    --assignee renderer-ascii \
    --parent <renderer-task-id> \
    --workspace dir:"$HOME/projects/video-pipeline/<slug>" \
    --tenant <slug> \
    --skill ascii-video \
    --max-runtime 30m
```

### 在运行过程中添加新的依赖项

当编辑器需要某个最初未规划中的资源时（例如字幕文件）：

```bash
# 1. Create the new task and capture its id
NEW_TASK_ID=$(hermes kanban create "Generate SRT captions from voiceover" \
    --assignee captioner \
    --workspace dir:"$HOME/projects/video-pipeline/<slug>" \
    --tenant <slug> \
    --json | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")

# 2. Wire it as a parent of the editor's task with `kanban link`
hermes kanban link "$NEW_TASK_ID" <editor-task-id>
```

`kanban link` 命令的参数顺序为 `parent_id child_id`（父节点在前）。若需移除该依赖关系，请使用 `kanban unlink` 命令。

### 中止陷入停滞状态的 Worker

一旦任务的运行时间超过所设定的 `--max-runtime` 参数值，看板调度器会自动向该任务发送 SIGTERM 信号，若仍未停止则会进一步发送 SIGKILL 信号。如需提前终止此类任务：

```bash
# Mark blocked so the dispatcher leaves it alone, then archive
hermes kanban block <task-id>
hermes kanban archive <task-id>

# Diagnose what happened
hermes kanban show <task-id>      # task body, comments, recent events
hermes kanban tail <task-id>      # follow the live event stream
hermes kanban log <task-id>       # worker process log
```

任务停止后，需决定是修复根本原因并重新创建该任务，还是跳过此步骤并调整相关的依赖任务。

### 调整任务目标

如果在执行过程中用户希望实现完全不同的目标：

1. 取消正在运行的主管任务及其所有处于“运行中”状态的子任务；
2. 编辑 `brief.md` 和 `TEAM.md` 文件；
3. 重新执行最初的 `hermes kanban create` 命令来设置新的任务目标。

切勿尝试在任务运行时直接修改——由于看板系统会记录完整的操作日志，因此先彻底停止任务后再进行调整，会比在运行过程中修改更为清晰明了。

## 定期检查脚本

一种用于无需持续干预的简单轮询监控方式：

```bash
while true; do
    clear
    hermes kanban list --tenant <slug>
    echo "---"
    hermes kanban stats --tenant <slug>
    sleep 30
done
```

如需实时获取事件流，可在另一个终端中运行 `hermes kanban watch --tenant <slug>` 命令——该命令会实时推送任务生命周期中的各类事件。

如需实现自动化干预功能（例如自动重启卡住的任务，或在审核失败时自动重新生成渲染结果），可参考 `scripts/monitor.py` 中的示例代码。

## 何时视为任务完成

当满足以下所有条件时，即可认为整个处理流程已完成：

1. 所有 RENDER 类任务均已执行完毕并通过审核；
2. 编辑器生成的 `output/final.mp4` 文件存在，且通过 `ffprobe` 检测确认其时长及流配置符合预期；
3. 审核人（如有）已给出批准意见；
4. 如需，已生成对应的 masterer 变体版本。

此时，应将 `final.mp4` 文件的路径以及任何审核意见一并呈现给用户。切勿删除该工作空间——用户可能希望仅对某个场景进行进一步修改，而无需重新运行整个处理流程。

## 常见问题与注意事项

- **租户配置错误**：使用错误租户创建的任务不会出现在监控列表中。请始终一致地使用 `--tenant <slug>` 参数。
- **配置文件对应的进程未运行**：如果某个配置文件对应的 worker 未处于在线状态，相关任务将无限期地滞留在 READY 状态。请通过 `hermes profile list` 查看状态，并启动缺失的配置文件对应的 worker。
- **工作空间权限问题**：所有配置文件都需要具备对该工作空间目录的读写权限。如果某个 worker 报告权限错误，请执行 `chmod -R u+rw <workspace>` 命令。
- **音视频同步问题**：编辑器中的片段拼接时长必须与渲染器实际生成的输出时长一致。请勿在编辑器中直接硬编码场景时长，而应从渲染器传递的元数据中读取相应数值。
