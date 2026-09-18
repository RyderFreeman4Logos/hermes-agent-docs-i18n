# 看板教程

本教程将在浏览器中打开控制面板，逐步介绍Hermes看板系统所设计的四种使用场景。如果您尚未阅读[看板概述](./kanban)，请先从那里开始——本教程假定您已经了解任务、运行任务、负责人以及调度器等概念。

## 设置

```bash
hermes kanban init           # optional; first `hermes kanban <anything>` auto-inits
hermes dashboard             # opens http://127.0.0.1:9119 in your browser
# click Kanban in the left nav
```

控制面板是**您**查看系统状态最便捷的界面。调度器启动的代理工作进程无法直接看到控制面板或命令行界面——它们是通过专用的 `kanban_*` [工具集](./kanban#how-workers-interact-with-the-board)（如 `kanban_show`、`kanban_list`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_attach`、`kanban_attach_url`、`kanban_attachments`、`kanban_create`、`kanban_link`、`kanban_unblock`）来操作看板内容的。控制面板、命令行界面以及工作进程工具这三者均通过同一个针对每个看板的 SQLite 数据库进行交互（默认看板为 `~/.hermes/kanban.db`，后续创建的看板则为 `~/.hermes/kanban/boards/<slug>/kanban.db`），因此无论变更来自哪个环节，各看板的数据都保持一致。

本教程全程使用“默认”看板作为示例。如果您需要多个独立的队列（每个项目/仓库/领域一个），可参阅概述中的[多项目看板](./kanban#boards-multi-project)——每个看板仍遵循相同的命令行界面/控制面板/工作进程操作流程，且工作进程实际上无法查看其他看板上的任务。

在教程中，标有 `bash` 的代码块代表**您需要手动执行的命令**；而标有 `# worker tool calls` 的代码块则是被启动的工作进程模型作为工具调用所发出的指令——此处展示是为了让您能完整了解整个流程，而非让您实际执行这些命令。

## 看板概览

![看板概览图](/img/kanban-tutorial/01-board-overview.png)

从左到右共六列：

- **分类筛选** — 初始想法阶段。默认情况下，调度器会自动对这类任务运行**分解器**：内置的分解器使用 `auxiliary.kanban_decomposer`，读取用户的个人资料与任务描述，进而生成一个子任务图，将任务分配给最合适的专家处理。原始任务仍作为父任务保留，以便在所有子任务完成后，由其指定负责人（即 `kanban.orchestrator_profile`，若未设置则使用默认的活跃配置）重新启动并判断任务是否完成。可通过看板页面顶部的 **“编排模式：自动/手动”** 按钮切换模式。在手动模式下，可点击卡片上的 **⚗ 分解** 按钮，或执行命令 `hermes kanban decompose <id>` / `/kanban decompose <id>`。对于无需进一步拆分的单个任务，**✨ 指定** 功能可一次性重写任务的具体要求（目标、实现方法、验收标准），并将其状态提升为“待办”。可在 `config.yaml` 文件中的 `auxiliary.kanban_decomposer` 和 `auxiliary.triage_specifier` 部分配置相关模型。更多详情请参阅主看板指南中的 [自动编排与手动编排对比](./kanban#auto-vs-manual-orchestration)。
- **待办** — 已创建但仍在等待依赖条件满足，或尚未分配负责人。
- **准备中** — 已分配负责人，正在等待调度器进行任务派发。
- **处理中** — 有工作人员正在积极执行该任务。在开启“按负责人分组”功能（默认开启）的情况下，此列会按负责人进行细分，便于快速了解每位工作人员当前的工作内容。
- **阻塞中** — 工作人员需要人工干预，或电路保护机制已触发。
- **已完成** — 任务已处理完毕。
顶部栏提供了搜索、租户和负责人的筛选功能，同时还设有“按配置文件分类任务列”的切换选项，以及“立即派发任务”按钮——该按钮可立即执行一次派发操作，而无需等待后台服务的下一个调度周期。点击任意卡片即可打开其右侧的详情面板。

### 平铺视图

如果按配置文件分类的任务列过于复杂，可关闭“按配置文件分类任务列”选项，此时“进行中”列会合并为按处理时间排序的单一平铺列表：

![关闭按配置文件分类时的看板](/img/kanban-tutorial/02-board-flat.png)

## 故事案例 1 — 独立开发者交付功能

你正在开发一个新功能。遵循常规流程：设计数据结构、实现 API 接口、编写测试用例。这三个任务之间存在父子依赖关系。

```bash
SCHEMA=$(hermes kanban create "Design auth schema" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --body "Design the user/session/token schema for the auth module." \
    --json | jq -r .id)

API=$(hermes kanban create "Implement auth API endpoints" \
    --assignee backend-dev --tenant auth-project --priority 2 \
    --parent $SCHEMA \
    --body "POST /register, POST /login, POST /refresh, POST /logout." \
    --json | jq -r .id)

hermes kanban create "Write auth integration tests" \
    --assignee qa-dev --tenant auth-project --priority 2 \
    --parent $API \
    --body "Cover happy path, wrong password, expired token, concurrent refresh."
```

由于 `API` 的父节点是 `SCHEMA`，而 `tests` 的父节点又是 `API`，因此只有 `SCHEMA` 会立即进入 `ready` 状态。另外两个则会被置于 `todo` 状态，直到其父节点处理完成。这就是依赖推进机制在发挥作用——在尚未有可测试的 API 之前，不会有其他工作进程开始处理测试编写任务。

在下一次调度器触发时（默认为 60 秒，或立即触发若按下 **Nudge dispatcher**），`backend-dev` 配置文件会作为一个工作进程被创建，其环境变量中会包含 `HERMES_KANBAN_TASK=$SCHEMA`。以下是该工作进程在代理内部执行工具调用时的流程：

```python
# worker tool calls — NOT commands you run
kanban_show()
# → returns title, body, worker_context, parents, prior attempts, comments

# (worker reads worker_context, uses terminal/file tools to design the schema,
#  write migrations, run its own checks, commit — the real work happens here)

kanban_heartbeat(note="schema drafted, writing migrations now")

kanban_complete(
    summary="users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); "
            "refresh tokens stored as sessions with type='refresh'",
    metadata={
        "changed_files": ["migrations/001_users.sql", "migrations/002_sessions.sql"],
        "decisions": ["bcrypt for hashing", "JWT for session tokens",
                      "7-day refresh, 15-min access"],
    },
)
```

`kanban_show`命令将`task_id`的默认值设置为` $HERMES_KANBAN_TASK`，这样一来工作节点便无需知晓自身的ID。`kanban_complete`命令会一次性在`kanban_db`中完成多项操作：将任务摘要及元数据写入当前的`task_runs`记录，关闭该任务执行记录，并将任务状态转为`done`。

当`SCHEMA`的状态变为`done`时，依赖关系引擎会自动将`API`的状态提升为`ready`。API工作节点在处理该任务时会调用`kanban_show()`函数，从而看到附加在父任务上的`SCHEMA`摘要及元数据——这样它无需重新阅读冗长的设计文档即可了解相关架构决策。

点击看板上已完成的架构任务，右侧面板会显示所有详细信息：

![单人开发 — 已完成的架构任务面板](/img/kanban-tutorial/03-drawer-schema-task.png)

底部的“执行历史”区域是该功能的重要新增部分。其中会显示单次尝试的结果、状态（`completed`）、处理工作节点`@backend-dev`、执行时长、时间戳，以及完整的任务交接摘要。元数据（如`changed_files`、`decisions`）也会存储在任务执行记录中，任何读取该父任务的下游工作节点均可获取这些信息。

您随时都可以在终端查看相同的数据——这些命令是**您**在查看看板内容，而非工作节点在操作。

```bash
hermes kanban show $SCHEMA
hermes kanban runs $SCHEMA
# #  OUTCOME       PROFILE       ELAPSED  STARTED
# 1  completed     backend-dev        0s  2026-04-27 19:34
#     → users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); refresh tokens ...
```

## 故事2 — 批量任务处理

你有三名工作人员（翻译员、转录员和文案撰写员），以及一堆需要处理的独立任务。你希望他们能够同时工作，并且能实时看到进展情况。这是看板系统最简单的应用场景，也是其初始设计所优化的目标。

创建任务：

```bash
for lang in Spanish French German; do
    hermes kanban create "Translate homepage to $lang" \
        --assignee translator --tenant content-ops
done
for i in 1 2 3 4 5; do
    hermes kanban create "Transcribe Q3 customer call #$i" \
        --assignee transcriber --tenant content-ops
done
for sku in 1001 1002 1003 1004; do
    hermes kanban create "Generate product description: SKU-$sku" \
        --assignee copywriter --tenant content-ops
done
```

启动网关即可，无需再操心其他——它内置了调度器，能够从同一个 kanban.db 文件中处理三种专业配置的任务。

```bash
hermes gateway start
```

现在将看板筛选为 `content-ops`（或直接搜索“Transcribe”），即可看到如下界面：

![筛选为转录任务的舰队视图](/img/kanban-tutorial/07-fleet-transcribes.png)

目前已有两项转录任务完成，一项正在处理中，还有两项处于待处理状态，等待下一个调度周期的触发。在“进行中”列中，任务会按员工档案分组显示（默认为“按档案划分的通道”），这样无需浏览混杂的任务列表即可查看每位员工的当前任务。一旦当前任务完成，调度系统便会立即将下一项待处理任务转为处理状态。由于有三个守护进程同时处理三个不同的任务池，整个内容队列无需人工干预即可被处理完毕。

**Story 1 中关于结构化任务交接的论述在此同样适用。** 当翻译人员完成某次通话后，系统会生成 `kanban_complete(summary="已翻译4页内容，风格与现有营销文案保持一致", metadata={"duration_seconds": 720, "tokens_used": 2100})` 这样的消息——这不仅有助于数据分析，也对所有依赖该结果的后续任务十分有用。

## Story 3 — 带重试机制的角色流水线

正是在这方面，看板系统相较于普通的待办列表展现出更大优势。产品经理编写需求规格，工程师负责实现功能，审核人员首次会拒绝该版本。工程师随后进行修改并再次提交，最终获得审核通过。

通过 `auth-project` 进行筛选后的控制台视图如下：

![多角色功能的流水线视图](/img/kanban-tutorial/08-pipeline-auth.png)

该截图采用了**预创建的下游卡片**模型：实现卡片会包含一个专用的审核者子卡片。在这种模式下，一旦实现工作完成，工程师就必须调用`kanban_complete`函数，这样审核者子卡片才能从“待处理”状态移除。切勿仅仅为了寻求审核而阻塞实现任务的父卡片。

对于由同一张卡片同时负责实现与审核的工作流，请改用一级审核生命周期。完整的实现→审核→修改→重新审核流程如下：

```python
# --- Engineer: first implementation attempt ---
kanban_show()
# (write code, run tests, prepare the candidate)
kanban_request_review(
    summary="implemented reset flow; candidate is ready for review",
    metadata={"changed_files": ["auth/reset.py"], "tests_run": 8},
    reviewer="reviewer",
)
# → the same card enters review; the implementation run closes as
#   outcome='review_requested'

# --- Reviewer: request concrete changes ---
kanban_show()
# (inspect the handoff and candidate)
kanban_request_changes(
    reason="Add password-strength validation and make reset tokens single-use."
)
# → the review run closes as outcome='changes_requested'; the card returns
#   to backend-dev in ready/todo without touching block-loop accounting

# --- Engineer: second implementation attempt ---
kanban_show()  # prior review evidence is in worker_context
# (apply feedback and re-run tests)
kanban_request_review(
    summary="added zxcvbn validation and single-use reset tokens",
    metadata={
        "changed_files": [
            "auth/reset.py",
            "auth/tests/test_reset.py",
            "migrations/003_single_use_reset_tokens.sql",
        ],
        "tests_run": 11,
        "review_iteration": 2,
    },
    reviewer="reviewer",
)

# --- Reviewer: approve ---
kanban_complete(summary="review passed; acceptance criteria verified")
# → done
```

该任务的执行历史现在记录为 `review_requested → changes_requested → review_requested → completed`。每次尝试都有独立的执行主体、摘要、元数据及结果，因此第二位工程师可以清楚地看到审阅者拒绝了哪些内容，同时最终审批过程也具备可追溯性。`kanban_block` 专用于处理真正的外部问题升级（如权限缺失、产品决策变更或基础设施故障），而非常规的审阅反馈。

如果您有意使用截图中所示的下游卡片模型，那么在对应的实现任务完成后，审阅者将打开 `Review password reset PR`：

![审阅者在流程中的卡片视图](/img/kanban-tutorial/09-drawer-pipeline-review.png)

审阅者卡片中的 `worker_context` 会包含已完成的任务交接信息。这是一个独立的卡片工作流，切勿将其与同一卡片上的 `kanban_request_review` 混合使用，否则会导致审阅流程出现重复。

## 故事 4 — 断路器机制与崩溃恢复

实际的执行任务难免会出现故障：凭证缺失、内存溢出导致进程终止、短暂的网络错误等。调度器为此设置了两道防御机制：一是**断路器机制**，当连续出现 N 次故障后会自动阻断任务，避免流程无限陷入混乱；二是**崩溃检测机制**，能在任务对应的执行进程在超时时间到期前消失时自动恢复该任务。

### 断路器机制 — 伪装成永久性故障的情形

当配置文件的环境变量中未设置 `AWS_ACCESS_KEY_ID`，导致部署任务无法启动对应执行进程时的情况：

```bash
hermes kanban create "Deploy to staging (missing creds)" \
    --assignee deploy-bot --tenant ops \
    --max-retries 3
```

调度器会尝试启动工作进程。但由于启动失败（错误信息为 `RuntimeError: AWS_ACCESS_KEY_ID not set`），调度器会释放该任务占用的资源，增加失败计数器，并在下一个时间间隔再次尝试。由于此示例设置了 `--max-retries 3`，因此在连续三次失败后电路保护机制会被触发：任务状态将变为 `blocked`，且结果为 `gave_up`。如果未指定该参数，Hermes 将使用 `kanban.failure_limit` 的默认值（2）。在有人手动解除阻塞之前，不会再进行重试。

点击被阻塞的任务：

![电路保护机制 — 2次启动失败 + 1次放弃](/img/kanban-tutorial/11-drawer-gave-up.png)

共进行了三次尝试，所有任务的 `error` 字段都显示相同的错误信息。前两次的错误为 `spawn_failed`（可重试），第三次则为 `gave_up`（最终失败）。上方的事件日志展示了完整的流程：`created → claimed → spawn_failed → claimed → spawn_failed → claimed → gave_up`。

在终端上：

```bash
hermes kanban runs t_ef5d
# #   OUTCOME        PROFILE        ELAPSED  STARTED
# 1   spawn_failed   deploy-bot          0s  2026-04-27 19:34
#       ! AWS_ACCESS_KEY_ID not set in deploy-bot env
# 2   spawn_failed   deploy-bot          0s  2026-04-27 19:34
#       ! AWS_ACCESS_KEY_ID not set in deploy-bot env
# 3   gave_up        deploy-bot          0s  2026-04-27 19:34
#       ! AWS_ACCESS_KEY_ID not set in deploy-bot env
```

如果已连接 Telegram / Discord / Slack，当发生 `gave_up` 事件时系统会触发网关通知，这样您无需查看状态板即可获知服务中断的情况。

### 崩溃恢复——工作进程在运行过程中异常终止

有时进程启动虽成功，但工作进程随后会因段错误、内存不足或 `systemctl stop` 等原因而终止。调度器会通过调用 `kill(pid, 0)` 来检测到已终止的进程 ID；相应任务的状态会被释放并恢复为 `ready` 状态，随后在下一个调度周期中被分配给新的工作进程处理。

示例数据中的场景即为因内存不足而导致的迁移任务异常：

```bash
# Worker claims, starts scanning 2.4M rows, OOM kills it at ~2.3M
# Dispatcher detects dead pid, releases claim, increments attempt counter
# Retry with a chunked strategy succeeds
```

该面板会完整显示两次尝试的记录：

![崩溃与恢复 — 1次崩溃 + 1次完成](/img/kanban-tutorial/06-drawer-crash-recovery.png)

第一次尝试 — 崩溃，错误信息为“在230万行处发生内存溢出导致进程终止（进程99999已消失）”。第二次尝试 — 完成，其元数据中包含“strategy: “采用LIMIT子句分块处理 + WHERE id > last_id””这样的信息。负责重试的 Worker能够感知到第一次尝试的崩溃情况，从而选择更安全的策略；而这些元数据也能让后续的观察者（或事后分析人员）清晰地了解发生了什么变化。

## 结构化传递 — 为何 `summary` 和 `metadata` 如此重要

在上述每个案例中，Worker 都会在任务结束时调用 `kanban_complete(summary=..., metadata=...)`。这并非装饰性操作——它是工作流各阶段之间主要的传递渠道。

当负责任务 B 的 Worker 被启动并调用 `kanban_show()` 时，它所获取的 `worker_context` 中会包含：

- 任务 B 的**以往尝试记录**（之前的运行结果：最终状态、摘要、错误信息及元数据），这样负责重试的 Worker 就不会重复走那条失败的路径。
- **父任务的执行结果**——针对每个父任务，会包含其最近一次完成运行的摘要和元数据——这样下游 Worker 就能明白上游任务是如何以及为何被完成的。

这种方式取代了传统平面看板系统中需要“在评论和工作输出中翻找信息”的繁琐流程。产品经理可以在需求规格的元数据中编写验收标准，工程师的 Worker 则可以通过父任务的传递结构直接查看这些标准。工程师可以记录自己运行的测试项及通过的数量，审核人员的 Worker 在打开代码差异前就能立即获取到这份列表。

之所以需要批量关闭保护机制，是因为这些数据是针对单次运行的。通过 CLI 执行 `hermes kanban complete a b c --summary X` 的操作将会被拒绝——因为将相同的摘要复制到三个任务中几乎总是错误的做法。对于“我已完成一堆行政任务”这类常见情况，即便不使用交接标志，批量关闭功能依然可用。出于同样的原因，工具界面根本不会提供批量处理选项；`kanban_complete` 函数也始终只能一次处理一个任务。

## 对已完成卡片的后续处理——通过父链接进行 CI 问题修复

故事 1 的实现卡片已被标记为“已完成”。两小时后，合并分支上的 CI 测试失败了。无需重新打开该已完成的卡片——因为已完成卡片属于历史记录，其交接流程会继续向前推进。应创建一张新的修复卡片，并将该已完成的卡片设为其**父卡片**：

```bash
hermes kanban create "Fix CI: test_backoff_jitter flakes on 3.11" \
    --assignee backend-dev \
    --parent t_impl \
    --workspace worktree --branch wt/ci-fix-backoff \
    --body "CI run #4812 failed after t_impl completed.
FAILED tests/test_retry.py::test_backoff_jitter - TimeoutError
Acceptance: tests/test_retry.py green on 3.11 and 3.12."
```

让这一机制得以运行的关键因素有三点：

- **即时派发**。由于父任务已处于 `done` 状态，子任务会直接进入 `ready` 状态——调度器可在下一个时间节点立即处理它。（若父任务仍处于处理中，子任务则需在 `todo` 状态等待。）
- **上下文继承**。修复任务的上下文中包含一个“父任务结果”板块，其中记载着 `t_impl` 的完成总结与元数据——即原始任务处理者记录的修改文件及决策内容——这样在开始查看代码之前，修复任务处理者就能了解代码为何呈现当前状态。
- **最新的证据直接呈现**。当 `t_impl` 完成时，CI 日志尚未生成，因此不会出现在父任务的交接信息中；这些日志会被直接放入新任务的描述部分，与明确的验收标准一同呈现。

建议为修复任务创建全新的工作树/分支。检出原始分支虽能让处理者获取代码仓库的*当前状态*，但却无法获得*修改依据*——这些信息都包含在父任务的交接内容中。通常情况下，由原代码编写者来处理该任务最为合适，因为其具备修复代码所需的技能。

## 查看正在运行的任务

为便于全面了解，以下是仍在处理中的任务的概览界面（即故事 1 中的 API 实现任务，由 `backend-dev` 承接但尚未完成）：

![正在处理中的已分配任务](/img/kanban-tutorial/10-drawer-in-flight.png)

当前状态为“运行中”。正在进行的任务会显示在“运行历史”板块中，其状态标记为“active”，且没有“ended_at”时间戳。如果该工作节点发生故障或超时，调度器会以相应状态结束当前任务，并针对下一个待处理请求启动新任务——而该任务的记录始终不会消失。

## 后续步骤

- [看板概览](./kanban) — 完整的数据模型、事件术语表以及 CLI 参考手册。
- `hermes kanban --help` — 查看所有子命令及参数说明。
- `hermes kanban watch --kinds completed,gave_up,timed_out` — 实时查看整个看板中的终端事件流。
- `hermes kanban notify-subscribe <task> --platform telegram --chat-id <id>` — 当特定任务完成时接收推送通知。
