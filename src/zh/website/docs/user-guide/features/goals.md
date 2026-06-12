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

1. **目标已接受** — `⊙ 目标设定（20轮预算）：<您的目标>`
2. **第1轮开始** — Hermes会像收到普通消息一样开始处理该目标。
3. **评审模型运行** — 一轮结束后，评审模型会判定是“完成”还是“继续”。
4. **必要时进入循环** — 若判定为“继续”，您将看到`↻ 正在向目标推进（1/20）：<评审理由>`，随后Hermes会自动执行下一步操作。
5. **任务终止** — 最终您会看到`✓ 目标已达成：<原因>`或`⏸ 目标已暂停 — 已使用N/20轮`。

## 命令

| 命令 | 功能 |
|---|---|
| `/goal <文本>` | 设定（或替换）当前目标。会立即启动第一轮，无需另行发送消息。 |
| `/goal` 或 `/goal status` | 显示当前目标、其状态以及已使用的轮数。 |
| `/goal pause` | 停止自动循环，但不会清除目标。 |
| `/goal resume` | 恢复循环（将轮数计数器重置为零）。 |
| `/goal clear` | 完全删除目标。 |

该功能在命令行界面以及所有网关平台（Telegram、Discord、Slack、Matrix、Signal、WhatsApp、短信、iMessage、Webhook、API服务器和网页控制面板）上均可正常使用。

## 在目标执行过程中添加额外标准：`/subgoal`

当目标处于活跃状态时，您可以使用`/subgoal <文本>`在不重置循环的情况下添加额外的验收标准。每次调用都会在目标的子目标列表中新增一个带编号的条目；智能体在下一轮会看到的**继续执行提示**会包含原始目标以及“用户在循环过程中添加的额外标准”板块，而**评审提示**也会相应调整，要求评审必须考虑所有子目标——只有当原始目标**以及**所有子目标均被满足时，目标才会被标记为已完成。

| 命令 | 功能 |
|---|---|
| `/subgoal <文本>` | 为当前活跃目标添加新的标准。需先有活跃的`/goal`命令。 |
| `/subgoal`（无参数） | 显示当前带编号的子目标列表。 |
| `/subgoal remove <N>` | 删除第N个子目标（从1开始计数）。 |
| `/subgoal clear` | 删除所有子目标，但保留原始目标。 |

子目标会与目标一起保存在`SessionDB.state_meta`中，因此即使执行`/resume`也能保留下来。设置新的`/goal <文本>`会替换原有目标并清除子目标列表；`/goal clear`也会产生相同效果。

当您开始一个循环任务（例如“修复失败的测试”），但在执行过程中发现还希望它“同时为刚修复的漏洞添加回归测试”时，可以使用此功能——`/subgoal add a regression test`可以在不中断当前循环的情况下完善成功标准。

## 行为细节

### 评审模型

每轮结束后，Hermes会调用一个辅助模型，并提供以下信息：

- 当前目标文本
- 智能体最新的最终回复（约最后4 KB的文本）
- 一条系统提示，要求评审模型以严格的JSON格式回复：`{"done": <布尔值>, "reason": "<一句话说明>"}`

该评审模型被设计为较为保守：只有当回复**明确**表明目标已完成、最终成果已清晰生成，或目标本身无法实现/受到阻碍时，才会将目标标记为“完成”（此时会附带原因说明，以避免在不可能完成的任务上浪费预算）。

### 失败即继续的机制

如果评审模型出现故障（如网络中断、响应格式错误、辅助客户端不可用），Hermes会将判定结果视为“继续”——出问题的评审模型绝不会阻碍任务进展。真正的保障机制是**轮数预算**。

### 轮数预算

默认值为20轮（位于`config.yaml`中的`goals.max_turns`字段）。当达到预算上限时，Hermes会自动暂停，并明确告知您接下来的操作步骤：

```
⏸ Goal paused — 20/20 turns used. Use /goal resume to keep going, or /goal clear to stop.
```

`/goal resume` 会将计数器重置为零，这样你就可以分阶段逐步推进任务。

### 用户消息始终具有优先权

在目标任务处于激活状态时，你发送的任何真实消息都会优先于后续的继续循环处理。在 CLI 环境中，你的消息会先存入 `_pending_input` 中，排在已排队的继续内容之前；在网关环境中，消息也会通过适配器的 FIFO 机制以相同顺序处理。在你的轮次结束后，判断器会再次运行——因此，如果你的消息恰好能够完成目标任务，判断器会检测到这一点并立即停止后续处理。

### 运行中的安全机制（网关）

当智能体正在运行时，使用 `/goal status`、`/goal pause` 和 `/goal clear` 均是安全的——这些命令仅修改控制平面状态，不会中断当前的轮次。但在运行过程中设置**新的**目标任务（`/goal <new text>`）会被拒绝，并提示你先执行 `/stop`，以避免旧的任务继续与新任务同时处理。

### 数据持久性

目标任务的状态存储在 `SessionDB.state_meta` 中，键名为 `goal:<session_id>`。这意味着使用 `/resume` 可以直接从上次中断的地方继续——设定好目标后关闭笔记本，次日再打开并执行 `/resume`，目标任务的状态仍将保持不变（无论是处于激活、暂停还是已完成状态）。

### 提示词缓存

后续对话的提示词只是添加到历史记录中的普通用户角色消息而已。它不会修改系统提示词、更换工具集，也不会以任何可能破坏 Hermes 提示词缓存的方式影响对话内容。执行一个包含 20 轮的目标任务，在缓存占用方面与 20 轮普通对话的成本相同。

## 配置

请在 `~/.hermes/config.yaml` 中添加相关配置：

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
