---
sidebar_position: 16
title: "Persistent Goals"
description: "Set a standing goal and let Hermes keep working across turns until it's done. Our take on the Ralph loop."
---

# 持久目标（`/goal`）

`/goal` 能为 Hermes 设定一个在多轮对话中始终有效的目标。每轮结束后，一个轻量级的判断模型会检查助手的上一条回复是否已满足该目标。如果未满足，Hermes 会自动将续写提示反馈到同一会话中并继续工作——直到目标达成、你暂停或删除该目标，或是轮次预算耗尽为止。

这是我们对**Ralph 循环**的实现方式，其灵感直接来源于 Eric Traut（OpenAI）在 [Codex CLI 0.128.0 的 `/goal` 功能](https://github.com/openai/codex) 中提出的设计。保持目标在多轮对话中持续有效，并直至目标达成才停止工作的核心理念源自该设计，而这里的实现则是独立开发的，并针对 Hermes 的架构进行了优化。

## 适用场景

在以下需要 Hermes 自主迭代处理、无需你每轮都重新输入提示的任务中，可使用 `/goal`：

- “修复 `src/` 目录中的所有代码检查错误，并确保 `ruff check` 通过”
- “将仓库 Y 中的功能 X 迁移过来，包括相关测试，并让 CI 测试通过”
- “调查为何在会话运行过程中进行压缩时有时会出现会话 ID 变化的问题，并撰写报告”
- “构建一个小型 CLI 工具，根据照片的 EXIF 日期重命名文件，然后针对 photos/ 文件夹进行测试”

那些助手只需处理一轮就会停止的任务无需使用 `/goal`。而那些*否则你需要反复说三次“继续”*的任务，正是该功能大显身手的地方。

## 快速入门

```
/goal Fix every failing test in tests/hermes_cli/ and make sure scripts/run_tests.sh passes for that directory
```

您将看到的内容：

1. **目标已接受** — `⊙ 目标已设定（20轮预算）：<您的目标>`
2. **第1轮开始** — Hermes会像收到普通消息一样开始处理该目标。
3. **评审器运行** — 一轮结束后，评审模型会决定是“完成”还是“继续”。
4. **必要时进入循环** — 若判定为“继续”，您将看到`↻ 正在向目标推进（1/20）：<评审理由>`，随后Hermes会自动执行下一步操作。
5. **终止** — 最终您会看到`✓ 目标已达成：<原因>`或`⏸ 目标已暂停 — 已使用N/20轮`。

## 命令

| 命令 | 功能 |
|---|---|
| `/goal <文本>` | 设定（或替换）当前目标。会立即启动第一轮，无需单独发送消息。 |
| `/goal draft <文本>` | 根据自然语言描述的目标草拟结构化的完成契约，随后再设定该目标。详见[完成契约](#completion-contracts)。 |
| `/goal show` | 显示当前目标的完成契约内容。 |
| `/goal` 或 `/goal status` | 显示当前目标、其状态以及已使用的轮数。 |
| `/goal pause` | 停止自动继续循环，但不会清除目标。 |
| `/goal resume` | 恢复循环（将轮数计数器重置为零）。 |
| `/goal clear` | 完全删除该目标。 |
| `/goal wait <pid> [reason]` | 将循环挂起在后台进程上——在该进程运行期间，系统不会每轮都去触发Agent；进程退出后则会自动恢复。 |
| `/goal unwait` | 移除等待限制，立即恢复循环。 |

该功能在命令行界面以及所有网关平台（Telegram、Discord、Slack、Matrix、Signal、WhatsApp、SMS、iMessage、Webhook、API服务器和网页控制面板）上均可正常使用。

## 完成契约

仅使用简单的`/goal <文本>`指令也能正常工作，但目标若过于模糊，则会导致评审结果同样模糊——评审模型只能根据您指定的内容进行判断。Codex中的 `/goal` 使用指南也强调了这一点：一个完善的目标准则是明确说明**什么是完成的标准、如何证明已完成、哪些内容不可破坏、哪些在处理范围内，以及何时应停止**。Hermes会将这些要求转化为可选的**完成契约**，叠加在现有的目标循环之上。

一份契约包含五个字段，均为可选：

| 字段 | 含义 |
|---|---|
| `outcome` | 完成时必须满足的单一最终状态。 |
| `verification` | 用于*证明*该最终状态达成的具体测试、命令或结果文件。 |
| `constraints` | 不允许发生变化或出现退化的内容。 |
| `boundaries` | 属于处理范围的文件、目录、工具或系统。 |
| `stop_when` | Hermes应停止并请求用户输入的条件。 |

一旦设定了契约，提示语也会随之改变：**继续执行提示**会要求Agent以验证标准为依据并遵守各项约束；而**评审提示**则要求只有在有具体证据（如命令结果、文件片段、测试输出）证明满足验证标准时，才能判定为“完成”——而非仅凭主观判断认为“看起来已完成”。这有效解决了使用 `/goal` 指令时最常见的问题，即因目标描述不充分导致的过早完成或无休止的过度继续处理。

### 设定契约的两种方式

**1. 让Hermes自动草拟**（推荐方式——借鉴了Codex中“让Agent自行草拟目标”的建议）：

```
/goal draft Migrate the auth service from session cookies to JWT
```

Hermes会通过`goal_judge`辅助模型将您输入的简短指令扩展为完整的契约，设定目标后还会展示结果，便于您查看或优化各个字段。若该辅助模型不可用，则会回退到普通的自由格式目标设定——因此撰写内容绝不会妨碍目标的设定。

**2. 以`field: value`的形式直接编写**：

```
/goal Migrate auth to JWT
verify: pytest tests/auth passes
constraints: keep the /login response shape unchanged
boundaries: only touch services/auth and its tests
stop when: a DB schema migration is required
```

前几行非字段内容为目标标题；而那些已识别的字段前缀（如 `verify:`、`verified by:`、`constraints:`、`preserve:`、`boundaries:`、`scope:`、`stop when:`、`blocked:` 等）则用于构建对应的契约。仅包含冒号的简单目标（例如 “Fix bug: the parser drops commas”）不会被过度解析——系统只会提取已知的字段前缀。

可使用 `/goal show` 命令查看当前的契约内容。这些契约会与目标一起存储在 `SessionDB.state_meta` 中，因此即便执行 `/resume` 恢复流程，它们依然存在。在此功能启用之前的旧目标则保持不变（不包含契约）。契约与 `/subgoal` 规则相互配合：子目标会被作为法官必须满足的额外条件纳入契约之中。

## 在目标执行过程中添加条件：/subgoal

在目标处于活跃状态时，你可以使用 `/subgoal <文本>` 命令追加额外的验收标准，而无需重置整个循环流程。每次调用都会在目标的子目标列表中新增一项带编号的条目；代理人在下一轮会看到的**继续执行提示**中，除了原始目标外，还会包含一个“用户在循环过程中添加的额外条件”板块；同时**法官提示**也会相应调整，要求法官必须考虑所有子目标——只有当原始目标以及所有子目标都得到满足时，该目标才会被视为已完成。

| 命令 | 功能说明 |
|---|---|
| `/subgoal <文本>` | 为当前活跃目标追加新的条件。需先有一个处于活跃状态的 `/goal`。 |
| `/subgoal`（无参数） | 显示当前已编号的子目标列表。 |
| `/subgoal remove <N>` | 删除第 N 项子目标（从 1 开始计数）。 |
| `/subgoal clear` | 移除所有子目标，但保留原始目标不变。 |

子目标会与目标一同存储在 `SessionDB.state_meta` 中，因此即便执行 `/resume` 恢复流程，它们依然存在。若设置新的 `/goal <文本>`，则会替换原有目标并清空子目标列表；`/subgoal clear` 则具有相同效果。

当你开始一个循环任务（比如“修复失败的测试”），但在执行过程中又意识到还需要“为刚修复的漏洞添加回归测试”时，就可以使用此功能——通过 `/subgoal add a regression test` 即可完善成功标准，而不会中断正在运行的循环。

## 暂停等待后台进程：自动处理，亦可手动干预

某些目标的完成取决于需要数分钟才能自动完成的操作，比如推送代码后的持续集成测试、长时间构建、测试矩阵运行、部署操作或速率限制冷却期等。如果没有相应机制，目标循环会迫使代理人在每轮都重复询问“是否已完成？”，造成无意义的忙等待。

**这一问题会由系统自动处理。** 在每一轮中，法官都会看到代理人的实时后台进程信息（即 `terminal(background=true)` 中记录的进程ID、会话ID、命令内容、运行时长、最新输出以及任何 `watch_patterns`/`notify_on_complete` 触发条件），同时还会看到目标状态及代理人的响应。当代理人的进度确实受这些后台进程影响时，法官会给出 **`wait`** 的判定而非 `continue`，此时循环就会**暂停**：后续轮次将跳过（不进行法官评估、不继续执行、也不消耗轮次），直到相关条件得到满足——之后循环会带着结果恢复正常运行。法官也可以基于**时间**设置暂停条件（如 `wait_for_seconds`）以实现延迟或冷却等待。当处于暂停状态时，`/goal status` 命令会显示 `⏳ Goal (parked …)`。

法官会根据进程自身的信号选择合适的等待方式：

- **`wait_on_session <id>`** — 当进程的*自身触发条件*满足时才会释放：比如进程退出，或者（如果是通过 `watch_patterns` 启动的）其监控模式匹配到对应条件。这种方式适用于那些会在运行过程中主动发送信号的长期运行的监视器/服务器/轮询程序（例如打印出 `BUILD SUCCESSFUL` 后仍继续运行的构建进程，或是 `notify_on_complete` 类型的监视器），这类进程可能永远不会自行退出。
- **`wait_on_pid <pid>`** — 仅当进程退出时才会释放。
- **`wait_for_seconds <n>`** — 在固定延迟时间过后释放。

对此无需手动输入任何指令——由法官根据循环传递的进程上下文自行决定。当然，也提供了手动干预命令作为备用方案：

| 命令 | 功能说明 |
|---|---|
| `/goal wait <pid> [reason]` | 手动暂停循环，直到该 PID 对应的进程退出。 |
| `/goal unwait` | 清除所有等待限制（无论是法官设置的还是手动设置的），立即恢复循环。 |

这种基于进程ID或时间的等待限制会与目标一起存储在 `SessionDB.state_meta` 中，因此即便执行 `/resume` 恢复流程，它们依然存在。`/goal pause`、`/goal resume` 和 `/goal clear` 命令都会清除这些限制。如果设置限制时该进程已经退出（或在暂停期间退出），或者时间阈值已到，那么在下次检查时限制就会自动清除——过期的限制绝不会导致循环卡住。

典型流程如下：代理人推送代码后，启动一个带有 `terminal(background=true, notify_on_complete=true)` 参数的持续集成监视器，并报告“正在监控 CI 进程”。法官看到监视进程仍在运行后，会针对该进程的 PID 给出 `wait` 判定，此时循环就会暂停；一旦 CI 测试完成，法官会根据实际结果重新评估目标状态。

## 行为细节

### 法官角色

在每一轮结束后，Hermes 会调用一个辅助模型，传入以下信息：

- 当前的目标文本
- 代理人最新的最终响应内容（最近约 4 KB 的文本）
- 一条系统提示，要求法官以严格格式的 JSON 格式回复：`{"done": <布尔值>, "reason": "<一句话说明原因>"}`

法官的设计理念是谨慎行事：只有当响应**明确**表明目标已完成，或者最终成果已清晰生成，又或者目标本身不可实现/被阻塞时（此时会标记为已完成并附上阻塞原因，以避免在无法完成的任务上浪费资源），才会判定目标为已完成。

### 失败即继续的语义

如果法官出现故障（如网络中断、响应格式错误、辅助模型不可用等），Hermes 会将该判定视为 `continue`——一个出错的法官绝不会阻碍流程进展。真正的保障机制其实是**轮次预算**。

### 轮次预算

默认值为 20 轮继续执行次数（对应 `config.yaml` 中的 `goals.max_turns` 参数）。一旦达到该预算限制，Hermes 会自动暂停，并明确告知你下一步该怎么做：

```
⏸ Goal paused — 20/20 turns used. Use /goal resume to keep going, or /goal clear to stop.
```

`/goal resume` 会将计数器重置为零，从而让你能够以可控的步长持续推进任务。

### 用户消息始终具有优先级

在目标任务运行期间，你发送的任何真实消息都会优先于后续的自动回复循环处理。在 CLI 环境中，你的消息会先存入 `_pending_input` 中，而不会参与队列中的自动回复处理；在网关环境中，消息也会通过适配器的 FIFO 机制按相同顺序处理。在你的消息处理完成后，评估器会再次启动——因此，如果你的消息恰好能够完成目标任务，评估器会立即检测到并终止后续流程。

### 运行中的安全机制（网关）

当智能体正在运行时，使用 `/goal status`、`/goal pause`、`/goal clear`、`/goal wait` 和 `/goal unwait` 命令是安全的——这些命令仅修改控制平面状态，不会中断当前的对话轮次。但在运行过程中设置**新**目标任务（即执行 `/goal <new text>`）会被拒绝，并提示你先执行 `/stop` 命令，以避免旧的任务流程与新任务流程发生冲突。

### 数据持久性

目标任务的状态存储在 `SessionDB.state_meta` 中，键名为 `goal:<session_id>`。这意味着使用 `/resume` 命令后，系统可以准确接续上一次中断的位置——无论你是设置了目标任务后关闭笔记本，还是次日再回来执行 `/resume`，目标任务的状态都会保持不变（无论是处于运行中、暂停状态还是已完成）。

### 提示词缓存

自动回复的提示词只是附加在对话历史记录中的普通用户角色消息，它不会修改系统提示词、更换工具集，也不会以任何可能破坏 Hermes 提示词缓存的方式影响对话内容。执行一个包含 20 轮的目标任务，在缓存占用方面与 20 轮普通对话的消耗相同。

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

评判功能会使用 `goal_judge` 辅助任务。默认情况下，该任务会由您的主模型来处理（详见[辅助模型](/user-guide/configuration#auxiliary-models)）。如果您希望将评判任务分配给成本更低且速度更快的模型以降低费用，可以添加相应的覆盖配置：

```yaml
auxiliary:
  goal_judge:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

“法官裁决”部分的输出量较少（约200个标记），且每轮仅执行一次，因此通常选用成本低、速度快的模型即可。

## 示例演示

请完整翻译输入内容，切勿提前停止。

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

仅需四轮对话、一次 `/goal` 调用，且无需您主动发出“继续执行”的指令。

## 当智能评审员出现错误时

没有哪个智能评审员是完美的。需注意以下两种错误情况：

**假阴性——实际目标已达成，但评审员却要求继续。** 此类情况会通过对话轮次限制得到规避。您会看到 `⏸ 目标已暂停`，此时可以执行 `/goal clear` 命令或直接发送新消息。

**假阳性——仍有工作未完成，但评审员却判定目标已达成。** 您会看到 `✓ 目标已实现`，但实际上并非如此。您可以发送后续消息要求继续执行，或通过更精确的指令重新设定目标：`/goal <更具体的描述>`。为降低假阳性出现的概率，智能评审员的系统提示词被刻意设计得较为保守。

如果您认为某个智能评审员的判定不够令人信服，`↻ 正在朝着目标前进` 或 `✓ 目标已实现` 这两行中的原因说明会明确告知评审员的具体判断依据。这通常足以帮助您判断是目标描述存在歧义，还是模型的回应出现了问题。

## 设计渊源

`/goal` 命令实际上是 Hermes 对 **Ralph 循环** 模式的实现。这种以用户为中心的设计理念——在多轮对话中持续维护目标状态，直至目标达成才停止，并提供创建、暂停、恢复和清除等控制功能——最初由 OpenAI Codex 团队的 Eric Traut 在 [Codex CLI 0.128.0](https://github.com/openai/codex) 中推广并实现。虽然我们的实现方式有所不同（采用了独立的 `CommandDef` 注册表、`SessionDB.state_meta` 持久化存储、辅助客户端型智能评审员，以及网关端的适配器-FIFO 连续处理机制），但其核心思想仍源自彼处。理所当然，我们也要对此表示感谢。
