---
sidebar_position: 3
title: "Curator"
description: "Background maintenance for agent-created skills — usage tracking, staleness, archival, and LLM-driven review"
---

# 管理器

管理器是专为**智能体创建的技能**设计的后台维护工具。它负责记录每项技能的查看频率、使用次数以及更新频率，将长期未被使用的技能状态从“活跃”逐步转移到“过时”直至“归档”，同时会定期启动简短的辅助模型评估，提出合并或修复异常的建议。

该组件的存在旨在避免通过[自我提升循环](/user-guide/features/skills#agent-managed-skills-skill_manage-tool)创建的技能无限堆积。每当智能体解决新问题并保存技能时，该技能就会被存放在`~/.hermes/skills/`目录中。若不进行维护，最终会导致大量高度相似的技能出现，不仅污染技能库，还会浪费计算资源。

默认情况下（`prune_builtins: true`），管理器会在**`archive_after_days`天未使用后**，将**未被使用的预装内置技能**（随代码仓库一同提供）与它主要管理的智能体创建技能一并归档。而通过[agentskills.io](https://agentskills.io)安装的Hub技能则始终不在其处理范围内。若要将行为恢复为仅管理智能体创建技能的旧模式，可设置`curator.prune_builtins: false`，此时预装技能将不会被任何操作影响。此外，管理器**绝不会自动删除**技能——最糟糕的情况也只是将其归档到`~/.hermes/skills/.archive/`目录中，该处的技能仍可恢复。

该功能与[问题 #7816](https://github.com/NousResearch/hermes-agent/issues/7816)相关。

## 运行机制

“管理器”是由闲置状态检测触发的，而非通过定时任务启动。在 CLI 会话开始时、网关系统进行日常维护时，以及桌面端/`hermes serve` 的定时维护时间点，Hermes 会检查以下条件：

1. 自上次运行“管理器”以来已过去足够长的时间（间隔时间为 `interval_hours`，默认为 **7 天**）； 
2. 代理处于闲置状态的时间也足够长（最小闲置时间为 `min_idle_hours`，默认为 **2 小时**）。

桌面端及其他 `hermes serve` 后端均共享现有的每小时维护定时器（首次检测在 90 秒后进行），该定时器与定时任务无关。它们会从进程启动时间以及同一用户配置文件中最近的聊天活动时间开始计算闲置时长，即便会话关闭或被终止，也会保留该活动的时间戳；同时，在该配置文件的对话处理正在进行时，系统会跳过“管理器”的运行。处于连接状态但无活动的窗口不会阻碍维护任务的执行。此定时器还会定期检查个人技能同步与组织技能同步功能的状态，具体是否执行取决于这些功能自身的启用设置；同一用户配置文件对应的正在运行的消息网关将负责处理这些任务。

该定时器为所在后端的用户配置文件提供服务。维护操作在单独的工作线程中执行，关闭后端并不会中断当前正在进行的维护任务。不过，为同一用户配置文件启动多个独立的 `hermes serve` 进程，仍可能导致“管理器”的间隔检测出现竞争条件。

当上述两个条件均满足时，系统会创建一个 `AIAgent` 的后台进程副本——这一机制与内存/技能自我提升提示的实现方式相同。该副本拥有独立的提示缓存，且绝不会干扰正在进行的对话处理。

:::info 首次运行行为  
在全新安装环境（或执行 `hermes update` 后预筛选器首次启动时），筛选器**不会立即运行**。首次运行会将 `last_run_at` 的时间设置为“当前时间”，并推迟第一次实际处理，间隔时间为一个完整的 `interval_hours`。这样，在筛选器真正开始处理之前，您有足够的时间来审查技能库、标记重要技能，或选择完全不进行任何操作。  

如果您想查看筛选器在实际运行前会执行哪些操作，可以运行 `hermes curator run --dry-run` —— 该命令会生成与实际运行相同的审查报告，而不会对技能库进行任何修改。  
:::  

一次运行包含两个阶段：  

1. **自动筛选**（确定性处理，无需大语言模型）。超过 `stale_after_days`（30天）未使用的技能会被标记为“过时”；超过 `archive_after_days`（90天）未使用的技能则会移至 `~/.hermes/skills/.archive/` 目录。这是一种始终处于激活状态的技能精简机制——只要筛选器处于启用状态，就会自动执行此操作，且不会产生额外的模型计算成本。  
   - **已标记的技能**以及**任何定时任务所引用的技能**（包括已暂停或禁用的任务）都将被完全跳过——在自动筛选过程中，这些技能会被视为已标记状态，从而避免因任务延迟或暂停而导致其被错误归档。此外，在合并技能组时，系统还会重新处理定时任务中对技能的引用关系。  
   - **从未被使用过的技能**（`use_count == 0`）会享有缓冲期：它们至少需要达到 `stale_after_days` 的时长才会被归档。零次使用仅代表目前没有使用记录，并不能证明该技能可以随时被丢弃。
2. **LLM整合功能**（通过单次辅助模型处理实现，具有较高的迭代上限——通常一次完整的整理流程需要50至100次API调用）——**默认处于关闭状态**。当设置`curator.consolidate: true`时，该代理会遍历其创建的所有技能，可通过`skill_view`功能读取任意技能，并针对每个技能单独判断是保留、通过`skill_manage`工具进行修复、将重叠的技能整合为类别级“伞形结构”，还是通过终端工具将其归档。此整合功能会将一个技能视为一个完整的包：如果该技能包含`references/`、`templates/`、`scripts/`、`assets/`目录，或这些路径的相对链接，整理工具必须选择将其作为独立技能保留、重新定位所需的支持文件并修改路径，或者原封不动地归档整个包——而不会仅将`SKILL.md`文件的内容合并到另一个技能的`references/`目录中。

:::info 整合功能为可选项
默认情况下，整理工具仅执行**筛选功能**——即通过确定性的静态检查标记过时的技能，并将长期未被使用的技能归档。而基于特定策略的LLM**整合功能**（构建“伞形结构”、合并重叠技能）默认处于关闭状态，因为它会在每次运行时消耗辅助模型的计算资源，还会对您的技能库进行大规模的结构调整。如需启用该功能，请设置`curator.consolidate: true`，或通过`hermes curator run --consolidate`命令按需执行一次。

:::

被固定的技能既不受整理工具的自动转换操作影响，也不受代理自身`skill_manage`工具的操作影响。详情请参阅下文的[固定技能](#pinning-a-skill)部分。

## 配置选项

所有设置均保存在 `config.yaml` 文件的 `curator:` 子目录下（而非 `.env` 文件——该内容并非机密信息）。默认值为：

```yaml
curator:
  enabled: true
  interval_hours: 168          # 7 days
  min_idle_hours: 2
  stale_after_days: 30
  archive_after_days: 90
  consolidate: false           # LLM umbrella-building pass — opt-in (prune-only by default)
  prune_builtins: true         # archive unused bundled built-in skills too (hub skills always exempt)
```

如需完全禁用该功能，请将 `curator.enabled` 设置为 `false`。若希望保持持续剪枝功能，同时启用大语言模型整合功能，则应将 `curator.consolidate` 设置为 `true`。

### 在成本更低的辅助模型上运行审查任务

Curator 的大语言模型审查功能属于常规的辅助任务类型——即 `auxiliary.curator`，与视觉处理、压缩、会话搜索等功能处于同一类别。“自动”选项表示“使用我的主聊天模型”；如需指定特定的提供商和模型来执行审查任务，可手动覆盖该设置。

**最简单的方法——使用 `hermes model`：**

```bash
hermes model                   # → "Auxiliary models — side-task routing"
                               # → pick "Curator" → pick provider → pick model
```

在网页控制台的 **Models** 选项卡下也可找到相同的选择器。

**直接使用 config.yaml（等效方式）：**

```yaml
auxiliary:
  curator:
    provider: openrouter
    model: google/gemini-3-flash-preview
    timeout: 600               # generous — reviews can take several minutes
```

若保持默认值 `provider: auto`，审核流程将经由您的主要聊天模型处理，其行为与其他所有辅助任务一致。

:::注意：旧版配置
早期版本使用过一次性的 `curator.auxiliary.{provider,model}` 配置块。该方式依然有效，但会输出弃用警告信息——建议迁移到上述的 `auxiliary.curator` 配置方式，这样审核器就能与其他所有辅助任务共享相同的配置项（如 `hermes model`、控制面板的“模型”选项卡、`base_url`、`api_key`、`timeout`、`extra_body`）。
:::

## CLI命令行界面

```bash
hermes curator status         # last run, counts, pinned list, LRU top 5
hermes curator run            # trigger a run now (blocks until done). Prune-only unless curator.consolidate: true
hermes curator run --consolidate # force the LLM consolidation pass on for this run, overriding the config default
hermes curator run --background  # fire-and-forget: start the run in a background thread
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
hermes curator adopt <skill>    # hand an unmanaged skill to the curator
hermes curator adopt --all-unmanaged   # hand over every unmanaged skill
hermes curator list-unmanaged   # itemize skills with no provenance marker
hermes curator restore <skill>  # move an archived skill back to active
hermes curator list-archived    # list skills currently in ~/.hermes/skills/.archive/
hermes curator archive <skill>  # manually archive a single skill now
hermes curator prune [--days N] # bulk-archive agent-created skills idle >= N days (default 90)
hermes curator ledger           # list the per-mutation audit ledger (all actors)
hermes curator ledger --skill <name> --limit 50  # filter/paginate ledger entries
hermes curator rollback <entry-id>  # undo a single mutation from the ledger
hermes curator purge [--days N] [--dry-run]  # delete archived skills older than the TTL (explicit only)
```

## 备份与回滚

在每次执行真正的 Curator 处理之前，Hermes 会先在 `~/.hermes/skills/.curator_backups/<utc-iso>/skills.tar.gz` 处创建 `~/.hermes/skills/` 目录的 tar.gz 备份文件。如果某次处理意外地归档或合并了您不希望被修改的文件，您只需一条命令即可撤销整个处理过程：

```bash
hermes curator rollback        # restore newest snapshot (with confirmation)
hermes curator rollback -y     # skip the prompt
hermes curator rollback --list # see all snapshots with reason + size
```

回滚操作本身是可逆的：在替换技能树之前，Hermes会先创建一个标记为`pre-rollback to <target-id>`的快照，这样一旦发生误操作，只需通过`--id`参数恢复到该快照即可。

您也可以随时使用`hermes curator backup --reason "before-refactor"`手动创建快照。所指定的`--reason`参数会存储在快照的`manifest.json`文件中，并可在`--list`命令中查看。

为控制磁盘使用量，系统会将过期的快照自动删除，保留的数量上限为`curator.backup.keep`（默认值为5）。

```yaml
curator:
  backup:
    enabled: true
    keep: 5
```

如需关闭自动快照功能，可设置 `curator.backup.enabled: false`。即便已禁用备份，只要先将该参数设置为 `true`，手动执行 `hermes curator backup` 命令依然有效——因为这两个选项是相互关联的，这样就能确保在执行任何变更操作前都会自动创建快照，避免意外遗漏。

`hermes curator status` 命令还会列出最近使用频率最低的五个技能，便于快速判断哪些技能接下来可能会变得过时。

在正在运行的会话中（无论是 CLI 还是网关平台），都可以通过 `/curator` 路径访问相同的子命令。

## 审计日志与单次编辑回滚

全流程快照可用于“撤销上一次 curator 操作所做的所有更改”，但有时您可能希望知道*具体是谁修改了什么内容*，并仅撤销某一项变更。每一次技能变更——无论是 curator 的自动转换、Agent 的 `skill_manage` 调用，还是您自己通过 CLI 执行的归档/恢复/清除操作——都会在 `~/.hermes/skills/.curator_ledger.jsonl` 文件中的只读 JSONL 日志中添加一条记录：

- **执行主体** — `curator`（后台审查与自动转换）、`agent`（前台代理工具调用）或 `user`（CLI命令）
- **操作类型** — `create`、`edit`、`patch`、`delete`、`write_file`、`remove_file`、`archive`、`restore`、`purge`、`rollback`
- **证据信息** — 删除意图（合并操作使用 `absorbed_into`，清理操作为空值，以及是否由可恢复归档路径处理该操作），如有会包含触发会话的ID
- **操作前/后状态** — 每个文件对应的 `{path, sha256}` 格式清单。文件内容以内容寻址方式存储在 `~/.hermes/.curator_backups/blobs/` 目录下，并通过哈希值进行去重，因此即使有上百条记录涉及同一个未更改的文件，也仅需一个数据块即可存储。

```bash
hermes curator ledger                  # newest 20 entries
hermes curator ledger --skill my-skill --limit 50
hermes curator rollback <entry-id>     # restore that one mutation's before-state
```

单条记录回滚会精确地将变更所影响的文件从对象存储中恢复原状（同时移除其创建的文件），技能树中的其他内容则不会发生任何变动。与整棵树回滚类似，该操作首先会获取当前状态的安全日志条目，并采用**失败即终止**机制：如果无法写入安全日志，则不会进行任何更改。由于前台删除操作也会被记录在日志中，因此可以使用 `hermes curator rollback <entry-id>` 命令恢复被彻底删除的技能。

该日志仅用于数据采集，而非访问控制机制——即便写入日志失败，原始变更依然会执行。如需禁用此功能，请执行：

```yaml
skills:
  ledger: false
```

## 归档内容的TTL清除功能

默认情况下，已归档的技能会永久保留。若希望限制`~/.hermes/skills/.archive/`目录的大小，可设置TTL并手动执行清除操作——该清除过程绝不会自动运行，且每项被清除的技能都会先被记录到日志中（包含二进制数据），因此即便进行了清除，也能留下可供审计和恢复的痕迹：

```yaml
curator:
  archive_ttl_days: 180   # 0 (default) = never purge
```

```bash
hermes curator purge --dry-run   # preview what would be deleted
hermes curator purge             # delete archives older than the TTL (with confirmation)
hermes curator purge --days 90   # one-off TTL override
```

## 什么是“由智能体创建”的技能

技能管理器仅会管理在 `~/.hermes/skills/.usage.json` 文件中明确标记为**由智能体创建**的技能。只有同时满足以下所有条件的技能才会被纳入管理范围：

1. 其名称**不在** `~/.hermes/skills/.bundled_manifest` 中（即非随仓库一同打包的预置技能）；
2. 其名称**不在** `~/.hermes/skills/.hub/lock.json` 中（即非通过技能中心安装的技能）；
3. 其 `.usage.json` 文件中包含 `"created_by": "agent"` 或 `"agent_created": true` 这一字段。

目前，只有**后台自我优化审查分支**会在定期审查过程中（大约每10次智能体轮转后）创建新的上层技能时设置此标记。该后台分支以 `"background_review"` 作为写入源路径（通过 `tools/skill_provenance.py` 实现），这是唯一能触发 `skill_manage` 函数中 `mark_agent_created()` 方法的路径。

而在对话过程中，通过 `skill_manage(action="create")` 方法由前台智能体创建的技能则不会被标记为“由智能体创建”——这类技能被视为用户主动发起的，因此技能管理器有意不对它们进行干预。

:::warning 你手动创建的技能不会被纳入管理
如果你手动创建了 `SKILL.md` 文件，或指定Hermes使用外部技能目录，那么相应技能的 `.usage.json` 文件中 `created_by` 字段的值将为 `null`（或该字段根本不存在）。技能管理器不会对这些技能进行任何处理。同样，根据你的要求由前台智能体创建的技能也不在管理范围内。

**如需查看策展人实际管理的技能列表**，请运行 `hermes curator status` 命令。如果由智能体创建的技能数量为 0，说明目前没有技能处于该策展人的管理范围内——此时将跳过大语言模型的审核流程，报告会显示 `Model: (未确定) via (未确定)`，同时 `Duration` 字段值为 `0s`。
:::

### 使用未被管理的技能

`hermes curator status` 命令除了会显示已管理的技能数量外，还会一并展示**未被管理**的技能数量：

```
curator-managed skills: 43 total  (agent-created=43  bundled=0)
  active     41
  stale       2
  archived    0

unmanaged (no provenance marker): 112 total
  pre-dates marker    34
  foreground-created  78
  never auto-staled or archived — `hermes curator adopt <name>` hands one over
```

这112条记录虽然符合筛选条件，但由于以下两种原因而永远无法在生命周期管理中被查看：

- **早于标记时间**——该记录的创建时间早于`created_by`字段的出现，因此完全不包含任何来源标识信息。从记录本身确实无法判断其创建者。
- **前台创建**——由于用户请求的技能属于自身所有，前台通过`skill_manage(create)`函数刻意未设置该标记。

因此，一个庞大的知识库虽然看似已经过完整整理，但实际上大部分内容都是不可修改的。`adopt`功能则通过**声明机制**填补了这一空白：

```bash
hermes curator list-unmanaged                    # itemize them, with reasons
hermes curator adopt <name> [<name> ...]         # hand specific skills over
hermes curator adopt --all-unmanaged --dry-run   # preview the full list
hermes curator adopt --all-unmanaged             # hand over everything (prompts)
hermes curator adopt --all-unmanaged --yes       # skip the prompt
```

技能被采用后，会留下与后台审核分支相同的 `created_by: agent` 标记。但这一过程**不会**重置闲置计时器——已被采用的技能会保留其原有的 `last_activity_at` 时间戳，因此即便将不再使用的技能库交由系统管理，也不会为其重新开启90天的有效期限。那些长期处于闲置状态的技能在下次审核时很可能会被标记为“过期”（或“归档”），这正是该机制的设计意图。

技能的采用机制还能解除自动*优化*功能的限制。后台审核分支不会对非管理员管理的技能进行修改，因此一旦发现你的某个技能已过时，系统只会指出问题并建议将其采用而非直接编辑。而由用户主动发起的编辑操作则完全不受影响——你和智能体始终可以根据需要自行编辑自己的技能。

:::注意 `created_by` 是一个策略标志，而非来源说明
虽然存储的字段名为 `created_by`，但其实际含义是“是否允许自动管理机制对此进行操作？”，而非“谁创建了该文件”。这是两个不同的问题；对于在该标记出现之前的记录，其创建者信息根本无法追溯。之所以保留这个名称，是因为它已经存在于每个 `.usage.json` 文件中；应将其视为一种策略设定。命令 `hermes curator adopt` 只是改变了这一策略，并不会说明文件的真实创建者是谁。
:::

:::note 来源必须明确声明，不可推断  
技能的采用始终是手动操作。遥测数据无法确定技能的创建者：一个拥有数千个补丁的技能只能证明该智能体对其进行了**维护**，并不能说明智能体就是其**创建者**——因为Hermes会持续为你编辑用户自行编写的技能。如果采用自动判断“看起来像是智能体生成的，那就直接采用”的机制，最终可能会导致你亲手编写的技能被归档。`adopt`命令会拒绝处理那些已打包、通过Hub安装、来自外部来源，或是属于其他所有者的受保护内置技能。  
:::

真正由智能体创建的技能会经历完整的生命周期：  
- `active` → （30天未使用）`stale` → （90天未使用）`archived`  
被固定的技能可绕过所有自动转换流程  
通过`hermes curator restore <name>`命令即可恢复已归档的技能  

如果你希望保护某个特定技能，避免其被任何方式修改——比如你依赖的自行编写的技能——可以使用`hermes curator pin <name>`命令。详情请参见下一节。  

## 固定技能  

固定功能可以防止技能被删除，无论是通过管理工具的自动归档流程，还是智能体的`skill_manage(action="delete")`命令调用，都无法删除已固定的技能。一旦技能被固定：  
- **管理工具**在执行自动转换（`active → stale → archived`）时会跳过该技能，并指示其大语言模型审查环节也不对其进行处理。  
- 智能体的`skill_manage`工具也会拒绝对该技能执行删除操作，同时提示用户使用`hermes curator unpin <name>`命令来解除固定。不过补丁和编辑仍然可以应用，因此智能体可以在遇到问题时直接改进已固定技能的内容，无需反复进行固定/解除固定的操作。  

使用以下命令即可固定或解除固定技能：

```bash
hermes curator pin <skill>
hermes curator unpin <skill>
```

该标志会以 `"pinned": true` 的形式存储在 `~/.hermes/skills/.usage.json` 文件中的技能条目中，因此能够跨会话保留。任何定时任务 `skills:` 列表中指定的技能，在**自动切换**场景下也会受到同样的保护机制（只要相关引用存在，管理工具就不会将其标记为过时或归档），即便该任务处于暂停或禁用状态也是如此。若同时希望阻止执行 `skill_manage delete` 操作，建议明确使用固定标记功能。

只有**由智能体创建**的技能才能被固定——若尝试对打包技能或通过 Hub 安装的技能使用 `hermes curator pin` 命令，系统会予以拒绝并给出相应说明。Hub 安装的技能永远不会受到管理工具的修改。而打包的内置技能仅会在 `curator.prune_builtins: true`（默认值）的情况下被处理，即便如此也仅会在长时间未使用后进行归档，绝不会被修补、合并或删除。如需完全豁免打包技能，可将其该参数设置为 `false`。

有一小部分**受保护的内置技能**被硬编码为永远不可归档且不可合并，这一规则不受 `curator.prune_builtins` 设置、固定标记状态或大型语言模型判断结果的影响。这类技能承担着核心的用户体验功能，若擅自对其归档，会导致对应的命令触发“未知命令”错误，而用户却不会收到任何提示。（目前该列表为空——其最初的成员 `plan` 已升级为独立的内置命令 `/plan`，磁盘上不再存在对应的技能文件。）受保护的内置技能会被完全从管理工具的候选列表中剔除，因此合并处理阶段根本不会涉及它们。

如果您需要比“不会被删除”更强的保障——例如在智能体仍可读取该技能内容的同时将其完全锁定——可以使用编辑器直接修改 `~/.hermes/skills/<name>/SKILL.md` 文件。这种锁定机制能够防止工具层面的删除操作，而无法阻止对文件系统的直接访问。

## 使用情况追踪

维护工具会在 `~/.hermes/skills/.usage.json` 中为每个技能维护一个对应的记录，以此实现使用情况追踪：

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

计数器会在以下情况时增加：

- `view_count`：智能体对该技能调用了 `skill_view` 函数。
- `use_count`：该技能被加载到对话的提示词中。
- `patch_count`：对该技能执行了 `skill_manage patch/edit/write_file/remove_file` 操作。

预打包技能及通过 Hub 安装的技能将被明确排除在遥测数据记录之外。

## 每次运行报告

每次执行 Curator 功能时，都會在 `~/.hermes/logs/curator/` 目录下生成一个带有时间戳的子目录：

```
~/.hermes/logs/curator/
└── 20260429-111512/
    ├── run.json      # machine-readable: full fidelity, stats, LLM output
    └── REPORT.md     # human-readable summary
```

`REPORT.md` 是查看某次运行结果的便捷方式——可以了解哪些技能发生了转换、LLM 审核员给出了什么反馈，以及该次运行修复了哪些技能。无需搜索 `agent.log` 即可进行审计。

:::note 未找到候选技能？报告会显示 `(not resolved)`
当审核员没有**由智能体生成的技能**可供审核时，LLM 审核流程将直接跳过。报告标题会显示 `Model: (not resolved) via (not resolved)`，同时标注 `Duration: 0s`——这并不意味着存在配置错误或模型解析失败，仅仅表示没有候选技能，因此也从未调用过任何模型。自动转换阶段仍会正常运行并输出相应的计数信息。
:::

### 摘要中的重命名映射表

如果某次运行将多个技能归类到同一个类别下（或合并了相近的重复技能），则在运行结束后显示给用户的摘要中会包含一个明确的重命名映射表，列明审核员应用的每一组 `旧名称 → 新名称` 对应关系。该映射表与每项技能的转换记录相互补充，因此当大量技能被重命名时，无需对比 JSON 报告，即可一目了然地查看这些变化。此信息也会在 `hermes curator pin` 下显示，便于您立即固定该类别名称，从而锁定新的标签。

## 恢复已归档的技能

如果审核员已将您仍需要的某些技能归档：

```bash
hermes curator restore <skill-name>
```

此操作会将该技能从 `~/.hermes/skills/.archive/` 移回活跃的技能树中，并将其状态重置为 `active`。如果此后有以相同名称安装的打包技能或通过 Hub 安装的技能，恢复操作将会被拒绝（因为这会导致上层技能被覆盖）。

## 按环境禁用功能

Curator 功能默认处于开启状态。若要关闭它：

- **仅针对某个配置文件**：编辑 `~/.hermes/config.yaml`（或当前活跃配置文件的配置文件），并将 `curator.enabled` 设置为 `false`。
- **仅针对单次运行**：执行 `hermes curator pause` —— 暂停状态会在不同会话之间保持；如需重新启用，可使用 `resume` 命令。

此外，如果尚未经过 `min_idle_hours` 所设定的空闲时间，Curator 也会拒绝运行，因此在处于活跃开发状态的机器上，它自然只会在闲置时段执行任务。

## 相关内容

- [技能系统](/user-guide/features/skills) —— 技能的通用工作原理以及用于持续优化它们的自我提升机制
- [内存管理](/user-guide/features/memory) —— 用于维护长期记忆的并行后台处理机制
- [打包技能目录](/reference/skills-catalog)
- [问题 #7816](https://github.com/NousResearch/hermes-agent/issues/7816) —— 初始提案及设计讨论记录
