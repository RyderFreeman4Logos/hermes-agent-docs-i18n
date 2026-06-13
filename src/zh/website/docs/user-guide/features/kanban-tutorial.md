# 看板功能教程

本教程将通过在浏览器中打开控制面板，逐步演示Hermes看板系统设计的四种使用场景。如果您尚未阅读[看板功能概述](./kanban)，请先从那里开始——本教程假定您已经了解任务、运行任务、负责人以及调度员的概念。

## 设置

```bash
hermes kanban init           # optional; first `hermes kanban <anything>` auto-inits
hermes dashboard             # opens http://127.0.0.1:9119 in your browser
# click Kanban in the left nav
```

控制面板是**您**查看系统状态最便捷的界面。调度器创建的代理工作进程无法直接访问控制面板或命令行界面——它们通过专用的 `kanban_*` [工具集](./kanban#how-workers-interact-with-the-board)（如 `kanban_show`、`kanban_list`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`、`kanban_unblock`）来操作看板。控制面板、命令行界面以及工作进程工具这三者均通过同一个针对每个看板的 SQLite 数据库进行交互（默认看板为 `~/.hermes/kanban.db`，后续创建的看板则为 `~/.hermes/kanban/boards/<slug>/kanban.db`），因此无论变更来自哪个层面，各看板的数据始终保持一致。

本教程将全程使用 `default` 看板。如果您需要多个独立的队列（每个项目/仓库/领域一个），请参阅概述中的[多项目看板](./kanban#boards-multi-project)——每个看板都遵循相同的命令行界面/控制面板/工作进程流程，且工作进程实际上无法查看其他看板上的任务。

在整篇教程中，标有 `bash` 的代码块代表**您**需要执行的命令；而标有 `# worker tool calls` 的代码块则是派生的工作进程模型发出的工具调用指令——此处展示是为了让您能完整了解整个流程，而非让您实际执行这些指令。

## 看板概览

![看板概览图](/img/kanban-tutorial/01-board-overview.png)

从左到右共六列：

- **分类筛选**——原始想法阶段。默认情况下，调度器会自动对这里的任务运行**分解器**：内置的分解器使用 `auxiliary.kanban_decomposer`，读取您的个人资料与任务描述，进而生成一个子任务图谱，将任务分配给最合适的专家处理。原始任务作为父任务仍保留在系统中，其负责人（即 `kanban.orchestrator_profile`，若未设置则使用默认的活跃个人资料）会在所有任务处理完毕后重新启动，负责判断任务是否完成。您可以通过切换看板页面顶部的**“编排模式：自动/手动”**开关来改变模式。在手动模式下，可点击卡片上的**⚗ 分解**按钮，或执行命令 `hermes kanban decompose <id>` / `/kanban decompose <id>`。对于无需进一步拆分的单个任务，**✨ 指定**功能可一次性重写任务目标、实现方案及验收标准，然后将该任务提升至“待办”状态。您可以在 `config.yaml` 文件中的 `auxiliary.kanban_decomposer` 和 `auxiliary.triage_specifier` 配置项中调整相关模型参数。更多详情请参阅主看板指南中的[自动编排与手动编排对比](./kanban#auto-vs-manual-orchestration)。
- **待办**——已创建但仍在等待依赖条件满足，或尚未分配负责人。
- **准备就绪**——已分配负责人，正在等待调度器派发任务。
- **处理中**——有工作进程正在执行该任务。若启用了“按负责人分组”功能（默认开启），此列会按负责人进行细分，让您能一目了然地了解每位工作人员当前的工作内容。
- **阻塞中**——工作进程需要人工干预，或出现了断路器保护机制触发。
- **已完成**——任务已处理完毕。

顶部栏提供搜索、租户及负责人筛选功能，同时还设有“按负责人分组”开关以及“立即派发任务”按钮，该按钮可立即执行一次任务派发操作，而无需等待后台服务的下一次定时调度。点击任意卡片即可打开其右侧的详情面板。

### 平铺视图

如果按负责人分组的显示方式过于复杂，您可以关闭“按负责人分组”功能，此时“处理中”列会简化为按任务派发时间排序的单一平铺列表：

![关闭按负责人分组后的看板](/img/kanban-tutorial/02-board-flat.png)

## 故事一——独立开发者发布新功能

您正在开发一个新功能。典型的开发流程包括：设计数据结构、实现 API 接口、编写测试用例。这些任务之间存在父子依赖关系。

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

由于 `API` 的父节点是 `SCHEMA`，而 `tests` 的父节点又是 `API`，因此只有 `SCHEMA` 会立即进入 `ready` 状态。另外两个则仍处于 `todo` 状态，直到其父节点处理完成。这就是依赖推进机制在发挥作用——在还没有可供测试的 API 之前，不会有其他工作进程去处理测试编写任务。

在下一次调度器触发时（默认为 60 秒，或立即触发若按下 **Nudge dispatcher**），`backend-dev` 配置文件会作为工作进程启动，其环境变量中会包含 `HERMES_KANBAN_TASK=$SCHEMA`。以下是从代理内部视角看到的该工作进程的工具调用流程：

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

`kanban_show`函数将`task_id`的默认值设置为`$

```bash
hermes kanban show $SCHEMA
hermes kanban runs $SCHEMA
# #  OUTCOME       PROFILE       ELAPSED  STARTED
# 1  completed     backend-dev        0s  2026-04-27 19:34
#     → users(id, email, pw_hash), sessions(id, user_id, jti, expires_at); refresh tokens ...
```

## 故事 2 — 批量任务处理

你有三名员工（翻译员、转录员和文案撰写员），以及一堆需要处理的独立任务。你希望他们能够同时工作，并且能看到各自的进度。这是看板系统最简单的应用场景，也是其初始设计所优化的目标。

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

启动网关即可，无需再操心其他——它内置了调度器，能够从同一个 kanban.db 文件中处理三种专业配置的各类任务。

```bash
hermes gateway start
```

现在将看板筛选为 `content-ops`（或直接搜索“Transcribe”），即可看到如下界面：

![筛选为转录任务的舰队视图](/img/kanban-tutorial/07-fleet-transcribes.png)

已有两项转录任务完成，一项正在处理中，还有两项处于待处理状态，等待下一次调度器触发。由于“进行中”列是按人员配置文件分组的（默认为“按配置文件划分的通道”），因此无需在混杂的任务列表中查找，即可清晰查看每位工作人员当前正在处理的任务。一旦当前任务完成，调度器会立即将下一个待处理任务转为处理中状态。由于有三个守护进程同时处理三个不同的任务池，整个内容队列无需人工干预即可被清空。

**Story 1 中关于结构化任务交接的论述在此同样适用。** 当翻译人员完成一项任务后，系统会输出 `kanban_complete(summary="已翻译4页内容，风格与现有营销文案保持一致", metadata={"duration_seconds": 720, "tokens_used": 2100})` —— 这些信息不仅有助于分析，也对所有依赖该任务的后续处理非常重要。

## Story 3 — 带重试机制的角色流水线

这正是看板相比普通待办列表的优势所在。产品经理编写需求规格，工程师负责实现功能，审核人员首次驳回后，工程师再带着修改意见重新提交，最终获得审核通过。

通过 `auth-project` 进行筛选后的仪表板视图如下：

![多角色功能的流水线视图](/img/kanban-tutorial/08-pipeline-auth.png)

可以同时看到三阶段的任务链：`Spec: password reset flow`（已完成，由产品经理负责）、`Implement password reset flow`（已完成，由后端开发人员负责）、`Review password reset PR`（待处理，由审核人员负责）。每个任务的下方都会以绿色标出其上游任务，同时将下游依赖任务以关联形式展示出来。

其中比较有趣的是实现阶段的任务，因为它曾遭遇阻塞并经历了重试。以下是通过工具对每位工作人员模型的调用，展示的完整三节点协作流程：

```python
# --- PM worker spawns on $SPEC and writes the acceptance criteria ---
# worker tool calls
kanban_show()
kanban_complete(
    summary="spec approved; POST /forgot-password sends email, "
            "GET /reset/:token renders form, POST /reset applies new password",
    metadata={"acceptance": [
        "expired token returns 410",
        "reused last-3 password returns 400 with message",
        "successful reset invalidates all active sessions",
    ]},
)
# → $SPEC is done; $IMPL auto-promotes from todo to ready

# --- Engineer worker spawns on $IMPL (first attempt) ---
# worker tool calls
kanban_show()   # reads $SPEC's summary + acceptance metadata in worker_context
# (engineer writes code, runs tests, opens PR)
# Reviewer feedback arrives — engineer decides the concerns are valid and blocks
kanban_block(
    reason="Review: password strength check missing, reset link isn't "
           "single-use (can be replayed within 30min)",
)
# → $IMPL transitions to blocked; run 1 closes with outcome='blocked'
```

现在，您（作为人类操作者或独立的审核员账号）可以查看该封禁原因，确认修复方向明确后，通过控制面板的“解封”按钮，或通过 CLI/Slash 命令来进行解封操作。

```bash
hermes kanban unblock $IMPL
# or from a chat: /kanban unblock $IMPL
```

调度器会将 `$IMPL` 的状态恢复为 `ready`，并在下一个时间间隔重新启动 `backend-dev` 工作进程。此次重新启动实际上是对同一任务的**新一轮执行**：

```python
# --- Engineer worker spawns on $IMPL (second attempt) ---
# worker tool calls
kanban_show()
# → worker_context now includes the run 1 block reason, so this worker knows
#   which two things to fix instead of re-reading the whole spec
# (engineer adds zxcvbn check, makes reset tokens single-use, re-runs tests)
kanban_complete(
    summary="added zxcvbn strength check, reset tokens are now single-use "
            "(stored + deleted on success)",
    metadata={
        "changed_files": [
            "auth/reset.py",
            "auth/tests/test_reset.py",
            "migrations/003_single_use_reset_tokens.sql",
        ],
        "tests_run": 11,
        "review_iteration": 2,
    },
)
```

点击该实现任务后，侧边栏会显示**两次尝试记录**：

![包含两次运行记录的任务界面——先被阻断后又完成](/img/kanban-tutorial/04b-drawer-retry-history-scrolled.png)

- **第1次运行**——被`@backend-dev`标记为`blocked`状态。审核反馈直接显示在结果下方：“缺少密码强度检查，重置链接并非一次性使用（可在30分钟内重复使用）”。
- **第2次运行**——由`@backend-dev`标记为`completed`状态。此时会有新的摘要信息与元数据。

每次运行都会在`task_runs`表中生成一行记录，每行都包含独立的运行结果、摘要及元数据。重试历史并非附加在“最新状态”任务之上的概念性补充，而是核心展示内容。当负责重试的worker打开该任务时，`build_worker_context`会向其显示之前的尝试记录，这样二次处理的worker就能了解第一次为何被阻断，并针对具体问题进行修正，而无需从头开始重新运行。

接下来由审核人员处理。当他们打开“审核密码重置PR”时，会看到如下界面：

![审核人员在管道界面中的侧边栏视图](/img/kanban-tutorial/09-drawer-pipeline-review.png)

上级任务链接指向已完成的实现任务。当审核人员的worker在“审核密码重置PR”任务上启动并调用`kanban_show()`函数时，返回的`worker_context`中会包含上级任务最近一次已完成运行的摘要及元数据——这样审核人员无需查看差异对比，就能直接了解到“已添加zxcvbn密码强度检查，重置令牌现为一次性使用”，同时还能立即看到修改过的文件列表。

## 故事4 — 断路器机制与崩溃恢复

实际运行中难免会出现故障：凭证缺失、内存不足导致进程终止、短暂的网络错误等。调度器为此设计了双重防护机制：一是**断路器机制**，在连续出现N次失败后会自动阻断任务，避免任务状态一直处于混乱状态；二是**崩溃检测机制**，能在任务对应的worker进程在超时时间到期前崩溃时自动接管该任务。

### 断路器机制——模拟永久性故障

例如，某个部署任务因配置文件的环境变量中未设置`AWS_ACCESS_KEY_ID`，从而导致无法启动对应的worker进程：

```bash
hermes kanban create "Deploy to staging (missing creds)" \
    --assignee deploy-bot --tenant ops \
    --max-retries 3
```

调度器会尝试启动工作进程。但由于启动失败（错误信息为“RuntimeError: AWS_ACCESS_KEY_ID未设置”），调度器会释放该任务占用的资源，增加失败计数器，然后在下一个时间间隔再次尝试。由于本示例设置了`--max-retries 3`，因此在连续三次失败后电路保护机制会被触发：任务状态将变为“blocked”，且结果为“gave_up”。如果未指定该参数，Hermes会使用`kanban.failure_limit`（默认值为2）作为最大重试次数。在有人手动解除阻塞之前，不会再进行重试。

点击处于“blocked”状态的任务：

![电路保护机制——2次启动失败 + 1次放弃](/img/kanban-tutorial/11-drawer-gave-up.png)

共进行了三次尝试，每次的“error”字段都显示相同的错误信息。前两次为“spawn_failed”（可重试），第三次为“gave_up”（最终失败）。上方的事件日志展示了完整的流程：`created → claimed → spawn_failed → claimed → spawn_failed → claimed → gave_up`。

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

如果已配置 Telegram / Discord / Slack，当发生 `gave_up` 事件时系统会触发网关通知，这样您无需查看监控面板即可知晓服务中断的情况。

### 崩溃恢复——工作进程在运行过程中死亡

有时进程启动虽成功，但工作进程随后会因段错误、内存不足或 `systemctl stop` 等原因而死亡。调度器会通过调用 `kill(pid, 0)` 来检测到已死亡的任务进程；相应任务会被释放，状态恢复为 `ready`，随后在下一个计时周期中被分配给新的工作进程处理。

示例数据中的情况是某次迁移操作因内存不足而导致的故障：

```bash
# Worker claims, starts scanning 2.4M rows, OOM kills it at ~2.3M
# Dispatcher detects dead pid, releases claim, increments attempt counter
# Retry with a chunked strategy succeeds
```

该面板会完整展示两次尝试的历史记录：

![崩溃与恢复——1次崩溃 + 1次完成](/img/kanban-tutorial/06-drawer-crash-recovery.png)

第一次尝试——状态为“崩溃”，错误信息为“在230万行处因内存不足被终止（进程99999已消失）”。第二次尝试——状态为“完成”，其元数据中包含“strategy”: "chunked with LIMIT + WHERE id > last_id"。负责重试的 worker 在其上下文中感知到了第一次尝试的崩溃，因此选择了更安全的策略；这些元数据能让后续的观察者（或事后分析人员）清晰地了解发生了什么变化。

## 结构化任务交接——为何“summary”与“metadata”如此重要

在上述每个案例中，worker 都会在最后调用 `kanban_complete(summary=..., metadata=...)`。这并非装饰性操作——它是工作流各阶段之间主要的任务交接渠道。

当负责任务 B 的 worker 被启动并调用 `kanban_show()` 时，它所获取的 `worker_context` 中会包含：

- 任务 B 的**以往尝试记录**（之前的运行结果：最终状态、摘要、错误信息及元数据），这样负责重试的 worker 就不会重复走已失败的路线。
- **父任务的结果**——针对每个父任务，会包含其最近一次已完成运行的摘要和元数据——这样下游 worker 就能了解上游任务的执行原因与方式。

这取代了传统平面式看板系统中那种“需在评论和工作输出中翻找信息”的麻烦做法。产品经理可以在需求规格的元数据中编写验收标准，工程师的 worker 则可以通过父任务交接结构直接查看这些标准。工程师会记录自己运行的测试项及通过的数量，审核人员的 worker 在打开代码差异前就能拿到这份清单。

之所以需要“批量关闭”保护机制，是因为这些数据是针对单次运行而言的。通过 CLI 执行 `hermes kanban complete a b c --summary X` 的操作会被拒绝——将同一份摘要复制到三个任务中几乎总是一种错误操作。对于“我已完成一批行政任务”这类常见场景，即便不使用交接标志也能实现批量关闭。出于同样的原因，工具界面根本不提供批量操作选项；`kanban_complete` 始终只支持一次处理一个任务。

## 查看正在运行的任务

为便于全面了解，以下是仍在处理中的任务的面板界面（即案例1中的API实现，由 `backend-dev` 负责但尚未完成）：

![已被占用、正在处理的任务](/img/kanban-tutorial/10-drawer-in-flight.png)

该任务的状态为“运行中”。当前正在进行的运行记录会显示在“运行历史”部分，状态标记为“active”，且没有“ended_at”时间戳。如果负责此任务的 worker 死亡或超时，调度器会以相应的结果关闭此次运行，并在下次有人认领时开启新的尝试——该尝试记录行永远不会消失。

## 后续步骤

- [看板概览](./kanban)——完整的数据模型、事件词汇表及 CLI 参考文档。
- `hermes kanban --help`——所有子命令及参数说明。
- `hermes kanban watch --kinds completed,gave_up,timed_out`——实时查看整个看板中的终端事件流。
- `hermes kanban notify-subscribe <task> --platform telegram --chat-id <id>`——当特定任务完成时接收通知。
