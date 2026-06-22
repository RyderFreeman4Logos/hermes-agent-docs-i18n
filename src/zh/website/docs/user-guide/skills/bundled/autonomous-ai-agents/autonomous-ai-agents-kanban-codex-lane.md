---
title: "Kanban Codex Lane"
sidebar_label: "Kanban Codex Lane"
description: "Use when a Hermes Kanban worker wants to run Codex CLI as an isolated implementation lane while Hermes keeps ownership of task lifecycle, reconciliation, tes..."
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Kanban Codex 工作流

当 Hermes 的看板工作节点希望以独立的工作流模式运行 Codex CLI 时使用，同时由 Hermes 负责任务生命周期管理、差异同步、测试以及结果交接。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/autonomous-ai-agents/kanban-codex-lane` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent |
| 许可协议 | MIT |
| 标签 | `kanban`, `codex`, `worktrees`, `autonomous-agents`, `prediction-market-bot` |
| 相关技能 | [`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex), [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容获取操作指令。
:::

# Kanban Codex 工作流

## 概述

该技能为看板工作节点定义了一种轻量级的 Hermes+Codex 双工作流模式。Hermes 始终是任务的主导者：它负责调用 `kanban_show` 函数，判断是否适合使用 Codex，创建或选择独立的代码工作空间，启动并监控 Codex 的运行，处理任何出现的差异，执行验证操作，最终记录 `kanban_complete` 或 `kanban_block` 状态以完成任务交接。而 Codex 仅作为输入端工作流存在——其输出既不能视为任务完成的信号，也不能被视为可信的审核结果，更不允许直接修改看板的持久化状态。

设计这种模式的目的是让 Hermes 工作节点能够在不更换调度器的情况下，借助 Codex 实现有限的实现辅助功能。调度器仍需负责创建 Hermes 工作节点；工作节点可选择在自己的运行过程中启动 Codex，经过独立审查和测试后，再决定接受、部分接受或拒绝该工作流的结果。

## 适用场景

在满足以下所有条件时，可使用 Codex 工作流：

- 该看板任务属于编码、重构、文档编写、测试或结构迁移类任务，并且有明确的验收标准。
- Hermes 能够在单次运行中完成对有限差异的评估。
- 可以通过独立的 git 工作树/分支复制或检出代码仓库。
- 在 Codex 运行结束后，Hermes 能够自行执行相关的测试。
- 提示词中已明确列出了所有安全约束以及不允许修改的文件。

在出现以下任何情况时，不应使用 Codex 工作流：

- 任务需要依赖看板描述中未涵盖的人工判断。
- 工作节点缺乏访问代码仓库的权限、Codex 的认证信息，或没有足够时间处理差异结果。
- 修改内容涉及机密信息、凭证存储、私人用户数据或生产环境中的订单系统。
- 直接进行少量编辑比启动另一个智能体更快更安全。
- 该任务仅用于研究目的，应生成书面交接文档而非差异对比结果。
- 工作节点可能仅依据 Codex 的自我报告就轻易将任务标记为已完成。

## 责任划分规则

1. Hermes 负责整个看板任务的生命周期管理。Codex 绝不能替代工作节点，调用 `kanban_complete`、`kanban_block`、`kanban_create`、网关消息功能或任何 Hermes 看板 CLI 命令。
2. Hermes 承担最终验收责任。在经过审查和验证之前，应将 Codex 提交的代码变更/差异视为不可信的补丁。
3. Hermes 负责测试执行工作。虽然 Codex 可以运行测试，但这些测试结果仅具有参考价值；Hermes 需要使用代码仓库的官方工具重新执行必要的验证流程。
4. Hermes 负责确保安全。如果 Codex 改变了安全边界、风险控制机制、实时交易行为或机密信息处理方式，即使测试通过也必须拒绝该工作流。
5. Hermes 负责清理工作。需终止处于挂起状态的 Codex 进程，并在不再需要时删除临时创建的工作树。

## 所需的工作树与分支格式

切勿在共享的、未清理过的代码状态下直接运行 Codex。应使用能够将该工作流与对应看板任务关联起来的分支/工作树名称，从而将不可信的修改内容隔离起来。

推荐使用的变量：

```bash
TASK_ID="${HERMES_KANBAN_TASK:-t_manual}"
REPO="/path/to/repo"
BASE="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
SAFE_TASK="$(printf '%s' "$TASK_ID" | tr -cd '[:alnum:]_-')"
BRANCH="codex/${SAFE_TASK}/$(date -u +%Y%m%d%H%M%S)"
WORKTREE="/tmp/${SAFE_TASK}-codex-lane"
```

创建隔离通道：

```bash
git -C "$REPO" fetch --all --prune
git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "$BASE"
git -C "$WORKTREE" status --short --branch
```

若当前的看板工作区已经是为该任务专门创建的独立 Git 工作树，那么只有在执行 `git status --short` 后显示状态正常（除有意进行的 Hermes 编辑外）的情况下，才可在其中创建一个同级 Codex 分支。否则，请创建一个独立的临时工作树，在完成对齐后再通过 cherry-pick 或复制方式将已通过的提交拉回该临时工作树中。

对齐后的清理工作：

```bash
git -C "$REPO" worktree remove "$WORKTREE"
git -C "$REPO" branch -D "$BRANCH"  # only after accepted commits were copied/cherry-picked or intentionally rejected
```

如果工作树需要作为审核用的工件，请予以保留；将其记录在 `codex_lane.artifacts` 中，并在任务交接时提及该工作树。

## Codex 功能检查

在启动 Codex 之前请先执行这些检查。若缺少 Codex 功能，通常只需跳过对应流程即可，除非 Hermes 能够直接完成该任务，否则这并不构成任务执行的阻碍。

```bash
command -v codex
codex --version
codex features list | grep -i goals || true
```

如果需要支持 `/goal` 功能，请在确认该功能已可用之后，再通过特征标志来启用或启动该功能。

```bash
codex features enable goals || true
codex --enable goals --version
```

认证可以通过 `OPENAI_API_KEY` 或 Codex CLI 的 OAuth 状态信息（通常为 `~/.codex/auth.json`）来完成。请勿输出令牌文件内容。缺少 `OPENAI_API_KEY` 并不意味着无法进行认证。

## 模式选择

对于需要限定范围且仅需单次编辑、同时要求 Codex 编辑完成后自动退出的场景，请使用 `codex exec` 命令：

```python
terminal(
    command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE,
    background=True,
    pty=True,
    notify_on_complete=True,
)
```

仅当需要执行涉及多步骤的复杂任务，且能够从持久的目标跟踪功能中受益时，才应使用 Codex 的 `/goal` 命令。如果该功能默认处于禁用状态，可通过 PTY/tmux 会话以交互方式启动，或使用 `codex --enable goals` 参数来启用它。目标描述应具备完整性，需包含仓库路径、任务编号、安全约束、允许的操作范围、验收标准、测试要求以及预期提交的代码内容。

可供直接粘贴到 Codex 中的 `/goal` 目标描述示例：

```text
/goal Work in this repository only: <WORKTREE>. Task: <TASK_ID> <TITLE>.
Hermes owns the Kanban lifecycle; do not call Hermes kanban tools or messaging.
Create small commits on branch <BRANCH>. Follow the PMB safety constraints in the prompt.
Run the requested verification commands and report exact outputs. Stop after producing a diff and summary.
```

对于 prediction-market-bot 以及那些对安全性要求极高的项目，请勿使用 `--yolo` 参数。建议在隔离的工作树中使用 `--full-auto` 参数，随后由 Hermes 负责同步处理。

## 提示词构建

在进行 prediction-market-bot 相关工作时，请使用 `templates/pmb-codex-lane-prompt.md` 中提供的模板。对于其他项目，则保持相同的结构，只需将针对 PMB 的安全约束部分替换为该项目特有的规则即可。

每个 Codex 提示词都必须包含以下内容：

- `task_id`、任务标题以及完整的看板验收标准；
- 项目路径、工作树路径、分支名称以及允许操作的文件范围；
- 明确声明：Kanban 生命周期由 Hermes 管理，Codex 仅充当输入通道；
- 必须输出的成果：简明摘要、被修改的文件列表、提交的代码变更记录、运行的测试结果以及已知风险；
- 禁止执行的操作：访问敏感信息、发送外部消息、修改看板状态、进行无关的代码重构，以及非必要的依赖项升级；
- Codex 可以运行的验证命令，以及之后由 Hermes 执行的命令。

对于 PMB 项目，必须原封不动地加入以下强制性的安全约束：

```text
PMB safety constraints:
- live-SIM is paper-only; do not add or enable live REST order entry.
- Never use market orders.
- Do not add execution crossing or bypass price/risk checks.
- Do not fake passive fills, fills, PnL, order states, or reconciliation evidence.
- Do not weaken risk gates, limits, kill switches, or fail-closed behavior.
- Keep research/selection outside the C++ hot path unless explicitly requested.
- Do not read, print, write, or require secrets/tokens/credentials.
```

## 监控、超时与终止机制

通过 PTY 功能在后台启动耗时的 Codex 任务，并实时发送完成通知：

```python
result = terminal(
    command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE,
    background=True,
    pty=True,
    notify_on_complete=True,
)
session_id = result["session_id"]
```

在无需干扰的情况下进行监控：

```python
process(action="poll", session_id=session_id)
process(action="log", session_id=session_id, limit=200)
process(action="wait", session_id=session_id, timeout=300)
```

对于持续时间超过两分钟的通道，每隔几分钟发送一次看板心跳信号，例如：`kanban_heartbeat(note="Codex通道正在<WORKTREE>中运行；正在等待测试结果或差异对比")`。

终止条件：

- 该任务在剩余的运行时间内无法产生任何有用输出。
- Codex请求机密信息、生产环境凭证或外部权限。
- Codex试图在工作目录之外修改文件。
- Codex启动了无关的代码重写操作或依赖关系变更。
- 在工作节点超时即将到来时，Codex仍在运行且不存在安全的部分生成物。

终止命令：

```python
process(action="kill", session_id=session_id)
```

在终止任务后，需检查 `git status --short` 的输出；仅在确保安全的前提下保留有用的补丁，并记录 `codex_lane.result: timed_out` 或 `rejected` 及具体的 `rejected_reason`。

## 核对清单

Hermes 在接受任何 Codex 任务结果之前必须完成以下核对：

- [ ] `git -C <WORKTREE> status --short --branch` 的结果显示仅包含预期文件。
- [ ] `git -C <WORKTREE> diff --stat` 与 `git diff` 的输出已由 Hermes 审核。
- [ ] 任务中不包含任何机密信息、凭证、生成的缓存数据、无关内容或本地临时文件。
- [ ] 已遵守 PMB 安全约束：无实时 REST 订单提交，无市价单，无跨执行场景操作，无虚假被动成交记录或损益数据，未削弱风险控制机制，且无机密信息存在。
- [ ] Codex 提交的代码规模足够小，便于进行精确的挑选或合并操作。
- [ ] Hermes 已使用 `scripts/run_tests.sh`（针对 Hermes Agent）或对应仓库提供的测试脚本（针对其他仓库），自行运行了标准测试。
- [ ] 由 Codex 运行的测试结果与 Hermes 自行运行的测试结果需分开列出。
- [ ] 被接受的提交或差异已应用到 Hermes 所管理的代码空间/分支中。
- [ ] 被拒绝或部分通过的任务需说明具体原因；如有相关有效文件，还需提供其路径。

接受结果分类：

- `accepted`：Codex 提供的差异或提交内容已过审核、应用并得到验证。
- `partial`：部分 Codex 任务内容经过修改或挑选后被接受，被拒绝的部分已有记录。
- `rejected`：无任何 Codex 修改内容被接受，且已记录原因。
- `timed_out`：Codex 任务超时未完成，可能存在或不存在有用的结果文件。

## kanban_complete 元数据结构

对于所有经过该处理流程的任务，都需在 `metadata.codex_lane` 下添加此对象。若未使用 Codex，则将 `used` 设置为 `false`，并在 `rejected_reason` 字段或对应的 `notes` 字段中说明原因。

```json
{
  "codex_lane": {
    "used": true,
    "mode": "exec | goal | skipped",
    "worktree": "/absolute/path/to/codex/worktree",
    "branch": "codex/t_caa69668/20260508100000",
    "command": "codex exec --full-auto ...",
    "result": "accepted | rejected | partial | timed_out",
    "accepted_commits": ["<sha1>", "<sha2>"],
    "rejected_reason": "empty when fully accepted; otherwise concrete reason",
    "tests_run": [
      {"command": "scripts/run_tests.sh tests/tools/test_x.py", "exit_code": 0, "owner": "hermes"},
      {"command": "codex-reported: npm test", "exit_code": 0, "owner": "codex"}
    ],
    "artifacts": ["/absolute/path/to/log-or-patch"]
  }
}
```

对于那些明确跳过 Codex 的任务：

```json
{
  "codex_lane": {
    "used": false,
    "mode": "skipped",
    "worktree": null,
    "branch": null,
    "command": null,
    "result": "rejected",
    "accepted_commits": [],
    "rejected_reason": "Direct Hermes edit was smaller and safer than spawning Codex.",
    "tests_run": [],
    "artifacts": []
  }
}
```

## 常见误区

1. 将 Codex 的自动生成结果视为最终验证。务必检查代码差异，并通过 Hermes 重新运行测试。
2. 在用户主分支中直接运行 Codex。应始终在独立的个工作树或分支中进行操作。
3. 让 Codex 独自管理看板状态。虽然 Codex 可以汇总进度，但实际看板状态的更新仍由 Hermes 完成。
4. 在提示词中忽略 PMB 安全约束。若遗漏安全相关说明，即视为看板配置错误。
5. 使用 `/goal` 功能进行快速编辑。除非需要持久的多步骤任务延续，否则建议优先使用 `codex exec`。
6. 在未记录原因的情况下终止卡住的任务通道。`rejected_reason` 字段必须明确说明终止决策的理由。
7. 仅因测试通过就接受范围过广且无关的修改。应仅接受那些属于指定范围内的变更，或直接拒绝此类修改。

## 验证清单

- [ ] 已在执行 `command -v codex`、`codex --version` 及可选的目标功能检查之后，才决定是否运行 Codex。
- [ ] Codex 确实仅在独立的个工作树或分支中运行。
- [ ] 提示词中已明确说明任务范围、职责分配规则、适用时的 PMB 安全约束以及验证命令。
- [ ] Hermes 已检查过代码差异文件及涉及安全性的文件。
- [ ] Hermes 已独立运行标准测试。
- [ ] `kanban_complete.metadata.codex_lane` 的结构符合上述规范。
- [ ] 临时进程及不必要的个工作树均已清理完毕。
