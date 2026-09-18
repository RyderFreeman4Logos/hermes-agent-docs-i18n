---
sidebar_position: 16
title: "Persistent Goals"
description: "Set a standing goal and let Hermes keep working across turns until it's done. Our take on the Ralph loop."
---

# 持久目标（`/goal`）

`/goal` 能为 Hermes 设置一个在多轮对话中始终有效的目标。每轮结束后，一个轻量级的判断模型会检查助手的上一条回复是否已满足该目标。如果未满足，Hermes 会自动将延续提示词反馈到同一会话中并继续工作——直到目标达成、你暂停或取消该目标，或是轮次预算用尽为止。

这是我们对**Ralph 循环**的实现方式，其灵感直接来源于 Eric Traut（OpenAI）在 [Codex CLI 0.128.0 的 `/goal` 功能](https://github.com/openai/codex) 中提出的设计。保持目标在多轮对话中持续有效，并直至目标达成才停止工作的核心理念源自该方案，而这里的实现则是独立开发并针对 Hermes 的架构进行了优化。

## 何时使用

当需要让 Hermes 在无需你每轮都重新输入提示词的情况下自主迭代处理任务时，可使用 `/goal`：

- “修复 `src/` 目录中的所有代码检查错误，并确保 `ruff check` 通过”
- “将仓库 Y 中的功能 X 迁移过来，包括相关测试，并让 CI 测试通过”
- “调查为何在会话进行到中间时会出现会话 ID 变化的问题，并撰写一份报告”
- “构建一个小型 CLI 工具，根据照片的 EXIF 日期重命名文件，然后针对 `photos/` 文件夹进行测试”

那些仅需助手处理一轮就结束的任务无需使用 `/goal`。而那些*否则你需要反复说三次“继续”*的任务，正是该功能大显身手的地方。

## 目标与看板：我该选择哪一个？

`/goal`与[Kanban](./kanban)都能让Hermes在无需再次输入提示的情况下持续运行，因此人们很容易认为二者之间存在关联。但实际上并非如此——两者的界限十分清晰：

- **`/goal`属于单会话模式**。它通过循环将后续提示反馈到*当前*对话中，直到系统判定任务完成为止。设置目标时不会创建任何看板卡片，也不会将任务分配给其他用户或扩展处理流程，更不存在任何形式的任务传递。
- **Kanban则是由多个任务构成的看板**。每张卡片都会被分配到一个独立的处理进程及会话中。卡片的属性、依赖关系、负责人以及任务流转信息都存储在看板上，而非`/goal`中。
- **二者虽有少量有意设计的重叠部分**。使用`--goal`创建的看板卡片会采用与`/goal`相同的Ralph式后续处理引擎——但仅限于该卡片的独立处理会话内。它借用的是处理引擎，而非整个看板功能。详情请参阅[目标模式卡片](./kanban#goal-mode-cards---goal)。

| 您的需求 | 应使用的工具 |
|---|---|
| 在当前对话中持续处理某项任务直至完成 | `/goal <文本>` |
| 需要处理多个相互关联的任务，涉及依赖关系、任务流转或多个处理用户 | [Kanban](./kanban) — `hermes kanban create …` |
| 需要在看板上创建一张卡片，持续处理直至满足验收标准 | 带有`--goal`参数的看板卡片 |
:::note
如果您希望在看板上进行操作，需要自行执行相关命令（如 `hermes kanban create …`）——`/goal` 功能无法代劳。反之亦然：在此聊天窗口中暂停、恢复或删除某个目标，也不会自动创建、占用或移动看板卡片。
:::

## 快速入门

```
/goal Fix every failing test in tests/hermes_cli/ and make sure scripts/run_tests.sh passes for that directory
```

您将看到的内容：

1. **目标已接受** — `⊙ 目标设定（20轮预算）：<您的目标>`
2. **第1轮开始** — Hermes会像收到普通消息一样开始处理任务。
3. **评估模型运行** — 一轮处理结束后，评估模型会判定结果为`完成`、`继续`或`阻塞`。
4. **必要时进入循环** — 若判定为`继续`，您将看到`↻ 正在向目标推进（1/20）：<评估理由>`，随后Hermes会自动执行下一步操作。
5. **任务终止** — 最终您会看到`✓ 目标达成：<达成原因>`或`⏸ 目标已暂停 — 已使用N/20轮`。

## 命令

| 命令 | 功能说明 |
|---|---|
| `/goal <文本>` | 设置（或替换）当前目标。会立即启动第一轮对话，无需另行发送消息。 |
| `/goal draft <文本>` | 根据自然语言描述的目标生成结构化的完成契约，随后再设置该目标。详情请参阅[完成契约](#completion-contracts)。 |
| `/goal show` | 输出当前活跃目标的完成契约内容。 |
| `/goal` 或 `/goal status` | 显示当前目标、其状态以及已使用的对话轮次。 |
| `/goal pause` | 暂停自动续谈循环，但不会删除该目标。 |
| `/goal resume` | 恢复循环运行（将轮次计数器重置为零）。 |
| `/goal clear` | 完全移除当前目标。 |
| `/goal wait <pid> [reason]` | 将循环挂起在某个后台进程上——在该进程运行期间，系统不会每轮都去触发智能体响应；进程结束后会自动恢复循环。 |
| `/goal unwait` | 移除等待限制，立即恢复循环运行。 |
| `/goal gate add <命令>` | 添加**质量检查门限**：即必须在执行通过的一个Shell命令后，才能判定目标已完成。详情请参阅[质量检查门限](#quality-gates)。 |
| `/goal gate` 或 `/goal gate list` | 列出该目标的所有质量检查门限及其通过/失败状态。 |
| `/goal gate remove <N>` | 删除第N个质量检查门限（编号从1开始）。 |
| `/goal gate clear` | 移除所有质量检查门限。 |
经典的命令行界面、文本用户界面、桌面端、控制面板聊天功能以及消息传递网关均使用同一个共享的 `/goal` 命令处理程序。该处理程序涵盖了草稿/显示、内联合约、等待/取消等待、质量检查机制，以及 clear/stop/done 等别名功能。桌面端的任务控制功能也采用相同的处理程序。目前 ACP 并未宣传或实现 `/goal` 功能。

命令 `/goal draft <text>` 既可以创建任务，又能启动该任务的第一轮处理流程，即便在无法使用草稿功能且 Hermes 转而使用自由格式任务时也同样适用。“draft”是一个完整单词形式的子命令：例如 `/goal drafting docs` 会将“drafting docs”直接作为任务目标，而不会调用草稿生成模型。

各消息平台仍保留自身的访问规则：执行 `/goal gate add` 命令需要明确配置网关管理员；而列出、删除和清除质量检查规则的功能则仍可用于故障恢复。虽然任务的渲染方式和轮次调度因界面类型而异，但命令解析以及已保存的任务更改则是共享的。

## 完成合约

仅使用简单的 `/goal <text>` 命令也能正常工作，但目标描述若过于模糊，则会导致评估标准也不清晰——评估者只能根据你指定的要求来进行判断。Codex 中关于 `/goal` 的指南也强调了这一点：一个完善的任务目标应当明确说明**什么是完成的标准、如何证明已完成、哪些内容不可破坏、任务范围涵盖什么，以及何时应停止执行**。Hermes 将此理念转化为一种可选的“完成合约”，作为现有任务处理流程的附加层。

该合约包含五个字段，全部为可选项：

| 字段 | 含义 |
|---|---|
| `outcome` | 任务完成时必须满足的最终状态。 |
| `verification` | 用于*证明*该最终状态是否达成的具体测试、命令或结果文件。 |
| `constraints` | 不允许发生变更或出现性能退化的部分。 |
| `boundaries` | 任务覆盖的文件、目录、工具或系统范围。 |
| `stop_when` | Hermes 应停止并请求用户输入的条件。 |

设定契约后，两个提示词都会发生变化：**继续执行提示词**会要求智能体聚焦于验证目标并遵守各项约束；而**判定提示词**则规定，只有当有具体证据（如命令输出、文件片段、测试结果）证明已满足验证标准时，才能判定任务完成——而非仅凭“看起来已完成”的主观判断。这直接解决了最常见的 `/goal` 任务失败问题，即因目标描述不清晰导致的过早完成任务或无止境的过度执行。

### 设定契约的两种方式

**1. 让 Hermes 自动生成**（推荐方式——借鉴了 Codex 中“让智能体自行拟定目标”的建议）：

```
/goal draft Migrate the auth service from session cookies to JWT
```

Hermes会通过`goal_judge`辅助模型将您的简短指令扩展为完整的契约，设定目标后还会展示结果，便于您审核或优化各个字段。若该辅助模型不可用，则会回退到普通的自由格式目标——因此撰写内容绝不会妨碍目标的设定。

**2. 以`field: value`格式直接编写**：

```
/goal Migrate auth to JWT
verify: pytest tests/auth passes
constraints: keep the /login response shape unchanged
boundaries: only touch services/auth and its tests
stop when: a DB schema migration is required
```

前几行非字段内容为目标标题；那些已识别的字段前缀（如 `verify:`、`verified by:`、`constraints:`、`preserve:`、`boundaries:`、`scope:`、`stop when:`、`blocked:` 等）会被用于构建对应的契约。仅包含一个冒号的简单目标（例如 “Fix bug: the parser drops commas”）不会被篡改——系统只会提取已知的字段前缀。

若需查看当前的契约，可使用 `/goal show` 命令。这些契约会与目标一起存储在 `SessionDB.state_meta` 中，因此即便执行 `/resume` 操作，它们依然存在。在此功能启用之前的旧目标则保持不变（不包含契约）。契约与 `/subgoal` 规则是相互关联的：子目标会作为法官必须满足的额外条件被纳入契约之中。

## 在目标执行过程中添加规则：/subgoal

在目标处于活跃状态时，你可以使用 `/subgoal <文本>` 命令追加额外的验收标准，而无需重新启动整个循环。每次调用都会在目标的子目标列表中增加一条带编号的项；在下一次轮次中，智能体看到的**继续执行提示**会同时显示原始目标以及“用户在循环过程中添加的额外标准”板块，而**法官的评估提示**也会相应调整，要求必须综合考虑所有子目标——只有当原始目标以及所有子目标均被满足时，该目标才会被视为已完成。

| 命令 | 功能说明 |
|---|---|
| `/subgoal <文本>` | 向当前目标中添加新的判定标准。需先存在有效的 `/goal` 命令。 |
| `/subgoal`（无参数） | 显示当前按编号排列的子目标列表。 |
| `/subgoal remove <N>` | 删除第 N 个子目标（编号从 1 开始计数）。 |
| `/subgoal clear` | 删除所有子目标，但保留原始目标内容不变。 |

子目标会与目标一起存储在 `SessionDB.state_meta` 中，因此即使在执行 `/resume` 后也能保留。若设置新的 `/goal <文本>` 命令，则会替换原有目标并清空子目标列表；`/goal clear` 命令也会产生相同效果。

当您开始执行一个循环任务（例如“修复失败的测试”），但在执行过程中又意识到还需要“为刚修复的漏洞添加回归测试”时，可以使用此命令——`/subgoal add a regression test` 能够在不中断当前循环的前提下完善成功标准。

## 质量关卡

虽然完成契约能让评估模型更加严格，但它本质上仍只是读取文本的大型语言模型。而**质量关卡**则更为严谨：它是一种确定的 Shell 命令，只有当该命令的退出码为 0 时，目标才能被视为已完成。这一机制借鉴了 Prime-Agent 的受限自主模式（`--autonomous-gate`）。

```
/goal Fix the flaky session tests
/goal gate add scripts/run_tests.sh tests/hermes_cli/test_goals.py
```

工作流程：每一轮的处理步骤如下：

1. **先运行各检测门，再由裁判决策。** 若有任何检测门失败，则不会调用裁判——红色标记的检测门即表示目标尚未完成的确凿证据。该检测门的退出码及输出尾部内容（最后约3 KB）将作为后续提示，从而引导智能体针对实际故障进行迭代，而非凭感觉操作。
2. **所有检测门均通过 → 正常进行裁判判定。** 此时，大型语言模型裁判会按照常规方式判断目标是否已完成、被阻塞、需要继续还是等待。
3. **工作区未发生变化 → 不重复运行检测门。** 若某个检测门失败，但自上次失败后工作区内容没有变化（通过HEAD的git指纹及工作树状态来追踪），则不会重新运行该检测门——系统会直接使用之前记录的失败结果，并增加尝试次数。陷入僵局的智能体无法通过无休止地重复运行相同的红色检测组来突破困境。在非git仓库环境中，检测门则始终会被重新运行。
4. **重试次数有限制。** 每个检测门的默认重试次数为3次，超时时间为5分钟。当某个检测门用尽所有重试机会后，目标会自动暂停（类似轮次预算耗尽的情况），并提示用户手动修复问题、移除该检测门或使用`/goal resume`命令继续。

检测门的信息会与目标一起保存在`SessionDB.state_meta`中（因此能够承受`/resume`操作及上下文压缩），且可在运行过程中安全地管理检测门（通过`/goal gate …`命令操作）——检测门仅在轮次切换时才会被执行。

检测门与契约相辅相成：利用契约来明确“智能体应追求的目标”，而通过检测门确保“完成目标”这一状态具有可机械化的验证依据。当两者都设置好后，检测门会优先运行。

## 后台进程的暂停机制：自动触发，同时支持手动干预

某些目标的完成取决于那些需要数分钟时间且会自动运行的任务——例如推送 Pull Request 后的 CI 测试、漫长的构建过程、测试矩阵执行、部署操作，或是速率限制后的冷却时间。若没有相应机制，目标循环会在等待期间不断反复询问智能体“是否已完成？”，从而陷入无意义的忙乱之中。

**这一问题可自动解决。** 在每一轮中，评审系统会同时展示智能体的实时后台进程信息（即当前会话中生成的 `terminal(background=true)` 注册项，包括进程 ID、会话 ID、命令行、运行时长、最新输出内容，以及任何 `watch_patterns`/`notify_on_complete` 触发规则）；由子智能体启动的进程则不会显示，因此父智能体永远不会被分配到某个工作节点的轮询任务中。与此同时，系统还会展示目标状态及智能体的响应。当智能体的实际进度确实受上述某项任务限制时，评审系统会给出 **`wait`** 判定而非 `continue`，此时目标循环会进入“暂停”状态：后续轮次将被跳过（无需进行评审、无需继续处理，也不占用轮次时间），直到等待条件满足为止——之后系统便会带着结果恢复正常运行。进程 ID/会话的等待时间上限为 30 分钟；而那些永远不会退出的进程（如监控进程或被遗忘的轮询程序）则无法使目标无限期处于暂停状态。此外，评审系统还支持基于**时间**的等待方式（`wait_for_seconds`），用于实现退避或冷却等待功能。当目标处于暂停状态时，`/goal status` 命令会显示 `⏳ Goal (parked …)`。

评审系统会根据进程自身发出的信号来选择合适的等待方式：

- **`wait_on_session <id>`** — 当进程的*自身触发条件*被满足时释放：即进程退出，或者（如果是通过`watch_patterns`启动的）其监控模式匹配到对应事件。此选项适用于那些需要长期运行的监视器、服务器或轮询程序，用于在运行过程中发送信号（例如输出`BUILD SUCCESSFUL`后仍继续运行的构建过程，或是`notify_on_complete`类型的监视器），这类进程可能永远不会自行退出。
- **`wait_on_pid <pid>`** — 仅在进程退出时释放。
- **`wait_for_seconds <n>`** — 在固定延迟时间过后释放。

对于这些选项，用户无需输入任何内容——具体决策由系统根据循环传递的进程上下文自动做出。此外还提供了手动控制命令作为替代方案：

| 命令 | 功能说明 |
|---|---|
| `/goal wait <pid> [reason]` | 手动暂停循环，直到指定PID的进程退出。 |
| `/goal unwait` | 清除所有等待屏障（无论是系统自动设置还是手动设置的），并立即恢复循环运行。 |

基于PID或时间的等待屏障会与目标状态一起保存在`SessionDB.state_meta`中，因此即使在执行 `/resume` 操作后也能保留。而 `/goal pause`、`/goal resume` 和 `/goal clear` 命令则会清除该屏障。如果设置屏障时进程已退出（或在暂停期间死亡），或者达到时间阈值，屏障会在下一次检查时自动清除——过期的屏障绝不会导致循环卡住。

典型流程为：智能体提交 Pull Request，使用 `terminal(background=true, notify_on_complete=true)` 启动 CI 监控进程，并报告“正在监控 CI”。评审员看到该监控进程仍在运行后，会针对其进程 ID 返回 `wait` 指令，此时循环将暂停——一旦 CI 完成，循环会立即恢复，根据实际结果对目标进行评估。

## 行为细节

### 评审员

在每个轮次结束后，Hermes 会调用一个辅助模型，传递以下信息：
- 当前的目标文本
- 智能体最新的最终回复（最近约 4 KB 的文本内容）
- 一条系统提示，要求评审员以严格的一行 JSON 格式回复：`{"verdict": "done" | "blocked" | "continue" | "wait", "reason": "<一句话说明>"}`（对于 `wait` 类型的判定，还会包含 `wait_on_session` / `wait_on_pid` / `wait_for_seconds` 参数；旧的 `{"done": <bool>, "reason": "..."}` 格式仍然被接受）

评审员的判断逻辑较为保守：只有当回复**明确**确认目标已完成，或最终成果已清晰生成时，才会将目标标记为 `done`。如果智能体说明某个目标是**无法实现**的（不可能完成、超出范围或需要用户输入），则该目标会被判定为 `blocked`，而绝不会被标记为 `done`：此时目标会因评审员的理由而**暂停**（显示为 `🚫 目标被判定为无法实现 — 已暂停`），这样你就可以通过 `/goal <文本>` 重新定义目标范围，或使用 `/goal resume` 继续处理，从而避免浪费预算或让不合理的任务被误判为已完成。 

### 失败即开放语义

如果判定器出现故障（如网络波动、响应格式错误或辅助客户端不可用），Hermes会将该判定视为“继续”——一个出问题的判定器绝不会阻碍进程的推进。真正的保障在于**轮次预算**。

### 轮次预算

默认值为20次继续轮次（即`config.yaml`文件中的`goals.max_turns`）。一旦达到该预算上限，Hermes会自动暂停，并明确告知您该如何继续操作：

```
⏸ Goal paused — 20/20 turns used. Use /goal resume to keep going, or /goal clear to stop.
```

`/goal resume` 会将计数器重置为零，从而让你能够以可控的步长持续推进任务。

### 用户消息始终具有优先权

在目标任务正在执行期间，你发送的任何真实消息都会优先于后续的继续循环处理。在 CLI 环境中，你的消息会先存入 `_pending_input` 中，排在已排队的继续内容之前；在网关环境中，消息也会通过适配器的 FIFO 机制按相同顺序处理。在你的轮次结束后，判断器会再次运行——因此，如果你的消息恰好能完成目标任务，判断器会立即检测到并终止流程。

### 运行中的安全机制（网关）

当智能体正在运行时，使用 `/goal status`、`/goal pause`、`/goal clear`、`/goal wait` 和 `/goal unwait` 均是安全的——这些命令仅操作控制平面状态，不会中断当前的轮次。如果在运行过程中尝试设置**新的**目标任务（如 `/goal <new text>`），系统会拒绝该操作，并提示你先执行 `/stop`，以避免旧的任务流程与新任务发生冲突。

### 状态持久性

目标任务的状态存储在 `SessionDB.state_meta` 中，键名为 `goal:<session_id>`。这意味着使用 `/resume` 可以从你上次停下的地方继续——设定好目标后关闭笔记本，次日再回来执行 `/resume`，目标任务的状态（无论是运行中、暂停还是已完成）都会保持不变。

### 提示词缓存

后续的对话提示词只是附加在历史记录中的普通用户角色消息，它不会修改系统提示词、更换工具集，也不会以任何可能破坏 Hermes 提示词缓存的方式影响对话内容。执行一个包含 20 轮的目标任务，在缓存占用方面与 20 轮普通对话的成本相同。

## 配置

请在 `~/.hermes/config.yaml` 文件中添加相关配置：

```yaml
goals:
  # Max continuation turns before Hermes auto-pauses and asks you to
  # /goal resume. Default 20. Lower this if you want tighter loops;
  # raise it for long-running refactors.
  max_turns: 20
```

### 选择评判模型

评判功能会使用 `goal_judge` 辅助任务。默认情况下，该任务会由您的主模型来处理（详见[辅助模型](/user-guide/configuration#auxiliary-models)）。如果您希望将评判任务分配给成本更低且速度更快的模型以降低开支，可以添加相应配置进行覆盖：

```yaml
auxiliary:
  goal_judge:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

“法官判定”阶段的输出量较小（约200个输出标记），且每轮仅执行一次，因此选用成本较低、速度较快的模型通常是最佳选择。

## 示例演示

```
You: /goal Create four files /tmp/note_{1..4}.txt, one per turn, each containing its number as text

  ⊙ Goal set (20-turn budget): Create four files /tmp/note_{1..4}.txt, one per turn, each containing its number as text

Hermes: Creating /tmp/note_1.txt now.
  💻 echo "1" > /tmp/note_1.txt   (0.1s)
  I've created /tmp/note_1.txt with the content "1". I'll continue with the remaining files on the next turn as you specified.

  ↻ Continuing toward goal (1/20): Only 1 of 4 files has been created; 3 files remain.

Hermes: [Continuing toward your standing goal]
  💻 echo "2" > /tmp/note_2.txt   (0.1s)
  Created /tmp/note_2.txt. Two more to go.

  ↻ Continuing toward goal (2/20): 2 of 4 files created; 2 remain.

Hermes: [Continuing toward your standing goal]
  💻 echo "3" > /tmp/note_3.txt   (0.1s)
  Created /tmp/note_3.txt.

  ↻ Continuing toward goal (3/20): 3 of 4 files created; 1 remains.

Hermes: [Continuing toward your standing goal]
  💻 echo "4" > /tmp/note_4.txt   (0.1s)
  All four files have been created: /tmp/note_1.txt through /tmp/note_4.txt, each containing its number.

  ✓ Goal achieved: All four files were created with the specified content, completing the goal.

You: _
```

仅需四轮对话、一次 `/goal` 调用，且无需您主动发出“继续”指令。

## 当评估结果出现错误时

没有哪个评估模型是完美的。需注意以下两种错误情况：

**假阴性——实际已达成目标，但评估模型却提示继续。** 此类情况会通过对话轮次限制得到防范。您会看到 `⏸ 目标已暂停`，此时可使用 `/goal clear` 命令或直接发送新消息。

**假阳性——仍有工作未完成，但评估模型却判定目标已达成。** 您会看到 `✓ 目标已实现`，但实际上并非如此。您可以发送后续消息要求继续，或更精确地重新设定目标：`/goal <更具体的描述>`。为降低假阳性出现的概率，评估模型的系统提示被刻意设置得较为保守。

如果您认为某个评估结果缺乏说服力，`↻ 正在朝着目标前进` 或 `✓ 目标已实现` 这两行中的原因说明会明确告知模型是基于什么判断得出该结果的。这通常足以帮助您判断是目标描述本身存在歧义，还是模型的回复有误。

## 设计渊源

`/goal` 命令实际上是 Hermes 对 **Ralph 循环** 模式的实现。这种以用户为中心的设计理念——在多轮对话中持续维持目标状态，直到目标达成才停止，并提供创建/暂停/恢复/清除等控制功能——最初由 OpenAI Codex 团队的 Eric Traut 在 [Codex CLI 0.128.0](https://github.com/openai/codex) 中推广并实现。虽然我们的实现方式有所不同（采用独立的 `CommandDef` 注册表、`SessionDB.state_meta` 持久化存储、辅助客户端评估模型，以及网关端的适配器-FIFO 连续处理机制），但其核心理念源自彼处。理所当然，我们应给予相应的贡献认可。
