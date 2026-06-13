---
sidebar_position: 3
title: "Curator"
description: "Background maintenance for agent-created skills — usage tracking, staleness, archival, and LLM-driven review"
---

# 管理器

管理器是专为**由智能体创建的技能**设计的后台维护工具。它负责记录每个技能的查看、使用及修复频率，将长期未被使用的技能逐步从“活跃”状态转为“过时”状态，最终归档；同时会定期运行简短的辅助模型检查，提出合并或修复偏差的建议。

其存在目的是避免通过[自我改进循环](/user-guide/features/skills#agent-managed-skills-skill_manage-tool)创建的技能无限堆积。每当智能体解决新问题并保存一个技能时，该技能就会被存放在`~/.hermes/skills/`目录中。若不进行维护，最终会出现大量几乎重复的技能，不仅污染技能库，还会浪费计算资源。

默认情况下（`prune_builtins: true`），管理器会在**`archive_after_days`天**未使用时，将**未使用的预置内置技能**（随代码仓库一同提供的技能）与它主要管理的智能体创建技能一并归档。而通过[agentskills.io](https://agentskills.io)安装的Hub技能则始终不在其处理范围内。若要将行为恢复为仅管理智能体创建技能的旧模式，可设置`curator.prune_builtins: false`，此时预置技能将不会被触碰。此外，管理器**绝不会自动删除**技能——最糟糕的结果也只是将其归档到`~/.hermes/skills/.archive/`目录中，该目录中的内容仍可恢复。

该功能关联[问题 #7816](https://github.com/NousResearch/hermes-agent/issues/7816)。

## 运行机制

管理器的触发基于空闲状态检测，而非cron守护进程。在CLI会话启动时，以及网关的cron定时器线程中定期触发时，Hermes会检查以下条件：

1. 自上次运行管理器以来已过去足够的时间（`interval_hours`，默认为**7天**）；
2. 智能体已处于空闲状态足够长时间（`min_idle_hours`，默认为**2小时**）。

若两个条件均满足，系统会启动一个`AIAgent`的后台副本——这与内存/技能自我改进功能所采用的机制相同。该副本拥有独立的提示词缓存，且不会干扰当前正在进行的对话。

:::info 首次运行行为
在全新安装环境中（或执行`hermes update`后首次触发预管理器模式时），管理器**不会立即运行**。系统会首先将`last_run_at`的初始值设置为“当前时间”，并将首次实际处理时间推迟整整一个`interval_hours`间隔。这样您就有足够的时间来审查技能库，标记重要技能，或选择完全不参与管理。

如果您想在实际运行前查看管理器会执行哪些操作，可运行`hermes curator run --dry-run`命令——该命令会生成相同的检查报告，而不会对技能库进行任何修改。
:::

一次运行包含两个阶段：

1. **自动转换**（确定性处理，无需LLM参与）。超过`stale_after_days`（30天）未使用的技能会被标记为“过时”状态；超过`archive_after_days`（90天）未使用的技能则会被移至`~/.hermes/skills/.archive/`目录。
2. **LLM检查**（使用单个辅助模型进行8次迭代处理）。该副本智能体会逐一检查所有智能体创建的技能，可通过`skill_view`功能读取这些技能的内容，然后针对每个技能决定是保留、通过`skill_manage`工具进行修复、合并重复的技能，还是通过终端工具将其归档。在合并操作中，一个技能被视为一个完整的包：如果该技能包含`references/`、`templates/`、`scripts/`、`assets/`这些目录，或包含指向这些路径的相对链接，管理器必须要么将其作为独立技能保留，要么重新定位所需的支持文件并修改路径，要么完整保留整个包——而不会仅将`SKILL.md`文件的内容合并到另一个技能的`references/`文件中。

被标记为“固定”的技能既不受管理器自动转换操作的影响，也不受智能体自身的`skill_manage`工具的操作影响。详情请参见下文[固定技能](#pinning-a-skill)部分。

## 配置

所有相关设置均位于`config.yaml`文件中的`curator:`部分（而非`.env`文件——这些并非敏感信息）。默认值为：

```yaml
curator:
  enabled: true
  interval_hours: 168          # 7 days
  min_idle_hours: 2
  stale_after_days: 30
  archive_after_days: 90
  prune_builtins: true         # archive unused bundled built-in skills too (hub skills always exempt)
```

如需完全禁用该功能，可将 `curator.enabled` 设置为 `false`。

### 在成本更低的辅助模型上运行审核

Curator 的 LLM 审核任务属于常规的辅助任务类型——即 `auxiliary.curator`，与视觉处理、压缩、会话搜索等功能处于同一类别。“自动”选项表示“使用我的主聊天模型”；如需指定特定的提供商和模型来执行审核任务，则可覆盖该设置。

**最简单的方法——使用 `hermes model`：**

```bash
hermes model                   # → "Auxiliary models — side-task routing"
                               # → pick "Curator" → pick provider → pick model
```

在网页控制台的 **Models** 选项卡下也可找到相同的选择器。

**直接使用 config.yaml 文件（等效方式）：**

```yaml
auxiliary:
  curator:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 600               # generous — reviews can take several minutes
```

若保留默认值 `provider: auto`，审核流程将通过您的主要聊天模型来处理，这一行为与其他所有辅助任务保持一致。

:::注意：旧版配置
在早期版本中，会使用一次性的 `curator.auxiliary.{provider,model}` 配置块。该方式仍然有效，但会生成弃用警告日志——建议改用上述的 `auxiliary.curator` 配置方式，这样审核器就能与其他辅助任务共享相同的配置项（如 `hermes model`、控制台中的“模型”选项卡、`base_url`、`api_key`、`timeout` 以及 `extra_body`）。
:::

## CLI命令行界面

```bash
hermes curator status         # last run, counts, pinned list, LRU top 5
hermes curator run            # trigger a review now (blocks until the LLM pass finishes)
hermes curator run --background  # fire-and-forget: start the LLM pass in a background thread
hermes curator run --dry-run  # preview only — report without any mutations
hermes curator backup         # take a manual snapshot of ~/.hermes/skills/
hermes curator rollback       # restore from the newest snapshot
hermes curator rollback --list     # list available snapshots
hermes curator rollback --id <ts>  # restore a specific snapshot
hermes curator rollback -y         # skip the confirmation prompt
hermes curator pause          # stop runs until resumed
hermes curator resume
hermes curator pin <skill>    # never auto-transition this skill
hermes curator unpin <skill>
hermes curator restore <skill>  # move an archived skill back to active
hermes curator list-archived    # list skills currently in ~/.hermes/skills/.archive/
hermes curator archive <skill>  # manually archive a single skill now
hermes curator prune [--days N] # bulk-archive agent-created skills idle >= N days (default 90)
```

## 备份与回滚

在每次执行真实的 Curator 处理之前，Hermes 会先对 `~/.hermes/skills/` 目录生成一个 tar.gz 格式的快照，文件路径为 `~/.hermes/skills/.curator_backups/<utc-iso>/skills.tar.gz`。如果某次处理意外地归档或合并了您不希望被修改的文件，您只需一条命令即可撤销整个处理过程：

```bash
hermes curator rollback        # restore newest snapshot (with confirmation)
hermes curator rollback -y     # skip the prompt
hermes curator rollback --list # see all snapshots with reason + size
```

回滚操作本身是可逆的：在替换技能树之前，Hermes会先创建一个标记为`pre-rollback to <target-id>`的快照，这样一旦发生错误的回滚，只需使用`--id`参数恢复到该快照即可。

您也可以随时通过`hermes curator backup --reason "before-refactor"`手动创建快照。所指定的`--reason`参数会存储在快照的`manifest.json`文件中，并可在`--list`命令中查看。

为控制磁盘使用量，系统会自动将过期的快照删除，保留的数量最多为`curator.backup.keep`个（默认值为5）。

```yaml
curator:
  backup:
    enabled: true
    keep: 5
```

将 `curator.backup.enabled: false` 设置为 true 即可禁用自动快照功能。即便已禁用备份，只要先将该参数设置为 true，手动执行 `hermes curator backup` 命令依然有效——这两个选项是相互关联的，因此无法在修改技能时意外跳过运行前的快照生成。

`hermes curator status` 命令还会列出最近使用频率最低的五个技能，这是快速判断哪些技能接下来可能过时的便捷方式。

在正在运行的会话中（无论是 CLI 还是网关平台），都可以通过 `/curator` 路径访问相同的子命令。

## “agent-created” 的含义

Curator 仅管理在 `~/.hermes/skills/.usage.json` 文件中被明确标记为 **agent-created** 的技能。一个技能要符合此条件，必须同时满足以下所有要求：

1. 其名称不在 `~/.hermes/skills/.bundled_manifest` 中（即随仓库一起提供的预打包技能）。
2. 其名称不在 `~/.hermes/skills/.hub/lock.json` 中（即通过 hub 安装的技能）。
3. 其 `.usage.json` 文件中包含 `"created_by": "agent"` 或 `"agent_created": true` 字段。

目前，只有**后台自我改进审查分支**会在定期审查过程中（大约每 10 次 agent 轮次）创建新的汇总技能时设置此标记。该后台分支以 `"background_review"` 作为写入来源（通过 `tools/skill_provenance.py` 实现），这是唯一能触发 `skill_manage` 函数中 `mark_agent_created()` 方法的路径。

而在对话过程中，由前台 agent 通过 `skill_manage(action="create")` 创建的技能则不会被标记为 agent-created——这类技能被视为用户主动创建的，Curator 故意不对它们进行干预。

:::warning 您手动编写的技能不会被 Curator 管理
如果您手动创建了 `SKILL.md` 文件，或让 Hermes 加载外部技能目录，那么这些技能的 `.usage.json` 文件中 `created_by` 字段的值将为 null（或该字段根本不存在）。Curator 不会对这类技能进行任何处理。您根据需求让前台 agent 创建的技能也是如此。

**要查看 Curator 实际管理的技能列表**，请运行 `hermes curator status` 命令。如果显示的 agent-created 技能数量为 0，说明目前没有技能处于 Curator 的管理范围内——此时会跳过 LLM 审查流程，报告中将显示 `Model: (未确定) via (未确定)`，且 `Duration` 字段值为 0s。
:::

被标记为 agent-created 的技能会经历完整的生命周期：

- `active` → （30 天未使用）`stale` → （90 天未使用）`archived`
- 被固定的技能可绕过所有自动状态转换
- 已归档的技能可通过 `hermes curator restore <name>` 命令恢复

如果您希望保护某个特定技能，避免其被任何方式修改——比如您依赖的自行编写的技能——可以使用 `hermes curator pin <name>` 命令。详情请参见下一节。

## 固定技能

固定技能可以防止其被删除，无论是 Curator 的自动归档流程，还是 agent 调用的 `skill_manage(action="delete")` 命令都无法对其产生影响。一旦技能被固定：

- Curator 在执行自动状态转换（`active → stale → archived`）时会跳过该技能，并且会指示 LLM 审查流程也不对其进行处理。
- agent 的 `skill_manage` 工具也会拒绝对该技能执行删除操作，同时提示用户使用 `hermes curator unpin <name>` 命令解除固定。不过，补丁应用和内容编辑仍然可以进行，因此 agent 可以在发现问题时直接改进被固定技能的内容，无需反复进行固定/解除固定的操作。

使用以下命令即可对技能进行固定或解除固定：

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

该标志会以 `"pinned": true` 的形式存储在 `~/.hermes/skills/.usage.json` 文件中对应技能的条目里，因此能够跨会话保留。

只有**由智能体创建**的技能才能被固定——如果您尝试对打包技能或通过 Hub 安装的技能执行 `hermes curator pin` 指令，该命令将会拒绝执行并给出相应说明。Hub 安装的技能永远不会受到 Curator 的修改。对于打包的内置技能，只有当 `curator.prune_builtins: true`（默认值）被设置为真时才会被处理，即便如此也仅会在长时间未使用后进行归档——绝不会被修补、合并或删除。若要将打包技能完全排除在外，可设置 `curator.prune_builtins: false`。

有一小部分**受保护的内置技能**被硬编码为无论如何都不会被归档或合并，这一规则不受 `curator.prune_builtins` 的设置、技能的固定状态或大型语言模型的判断影响。这些技能承担着核心的用户体验功能——例如，`plan` 功能就支撑着 `/plan` 这一斜杠命令流程——因此，若擅自对其归档，就会导致相关斜杠命令出现“未知命令”的错误，而用户却不会收到任何提示。受保护的内置技能会被完全从 Curator 的处理候选列表中剔除，因此合并操作根本不会涉及它们。

如果您需要比“不会被删除”更强的保障——比如在智能体仍可读取该技能内容的情况下彻底冻结其内容——可以直接使用编辑器修改 `~/.hermes/skills/<name>/SKILL.md` 文件。固定功能是为了防止工具层面的删除，而非限制您对文件系统的访问。

## 使用情况监控数据

Curator 会在 `~/.hermes/skills/.usage.json` 文件中维护一个侧车进程，其中每个技能对应一条记录：

```json
{
  "my-skill": {
    "use_count": 12,
    "view_count": 34,
    "last_used_at": "2026-04-24T18:12:03Z",
    "last_viewed_at": "2026-04-23T09:44:17Z",
    "patch_count": 3,
    "last_patched_at": "2026-04-20T22:01:55Z",
    "created_at": "2026-03-01T14:20:00Z",
    "state": "active",
    "pinned": false,
    "archived_at": null
  }
}
```

计数器会在以下情况增加：

- `view_count`：智能体对该技能调用了 `skill_view` 函数。
- `use_count`：该技能被加载到对话的提示词中。
- `patch_count`：对该技能执行了 `skill_manage patch/edit/write_file/remove_file` 操作。

预装技能及通过中心节点安装的技能将被明确排除在遥测数据记录之外。

## 每次运行报告

每次执行 curator 功能时，都會在 `~/.hermes/logs/curator/` 目录下生成一个带有时间戳的子目录：

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # machine-readable: full fidelity, stats, LLM output
    └── REPORT.md     # human-readable summary
```

`REPORT.md` 是查看某次运行结果的便捷方式——它能显示哪些技能发生了转换、LLM 审核者给出了什么意见，以及该次运行修复了哪些技能。无需逐行搜索 `agent.log`，即可快速完成审计工作。

:::note 未找到候选技能？报告会显示 `(not resolved)`
当审核员没有需要审查的**由智能体生成的技能**时，LLM 审核流程将直接跳过。此时报告标题会显示为 `Model: (not resolved) via (not resolved)`，同时标注 `Duration: 0s`——这并不意味着存在配置错误或模型加载失败，只是说明没有候选技能可供使用，因此也无需调用任何模型。自动转换阶段仍会正常运行，并正常输出相关统计信息。
:::

### 摘要中的重命名映射表

如果某次运行将多个技能归类到同一个类别下（或合并了相近的重复技能），则在运行结束后显示给用户的摘要中会包含一个明确的重命名映射表，列明审核员所应用的每一组 `旧名称 → 新名称` 对应关系。该映射表是与各技能的转换记录相辅相成的，因此当大量技能被重命名时，无需对比 JSON 报告，即可一目了然地查看这些变化。相关提示也会显示在 `hermes curator pin` 下，方便您立即固定该类别名称，从而锁定新的标签。

## 恢复已归档的技能

如果审核员已将您仍需要的某个技能归档：

```bash
hermes curator restore <skill-name>
```

此操作会将该技能从 `~/.hermes/skills/.archive/` 移回活跃的技能树中，并将其状态重置为“活跃”。如果此后已有同名且通过包形式或 Hub 安装的技能被安装，恢复操作将会被拒绝（因为新技能会覆盖原有技能）。

## 按环境禁用功能

Curator 功能默认处于开启状态。若要关闭它：

- **仅针对某个配置文件**：编辑 `~/.hermes/config.yaml`（或当前活跃配置文件的配置文件），并将 `curator.enabled` 设置为 `false`。
- **仅针对单次运行**：执行 `hermes curator pause`——该暂停状态会在不同会话之间保持；如需重新启用，则使用 `resume` 命令。

此外，如果尚未达到 `min_idle_hours` 所设定的空闲时间，Curator 也会拒绝运行，因此在日常使用的开发机器上，它通常只会在无人使用的空闲时段运行。

## 相关内容

- [技能系统](/user-guide/features/skills)——技能的运作原理以及用于持续优化技能的自我提升机制
- [内存管理](/user-guide/features/memory)——用于维护长期记忆的并行后台审查机制
- [打包技能目录](/reference/skills-catalog)
- [问题 #7816](https://github.com/NousResearch/hermes-agent/issues/7816)——最初的提案及设计讨论记录
