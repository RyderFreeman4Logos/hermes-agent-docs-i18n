---
title: "Openclaw Migration — Migrate a user's OpenClaw customization footprint into Hermes Agent"
sidebar_label: "Openclaw Migration"
description: "Migrate a user's OpenClaw customization footprint into Hermes Agent"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# OpenClaw 迁移

将用户的 OpenClaw 定制配置迁移至 Hermes Agent。该功能会从 ~/.openclaw 中导入与 Hermes 兼容的记忆体、SOUL.md 文件、命令允许列表、用户技能以及选定的工作区资源，同时详细列出无法迁移的内容及其原因。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/migration/openclaw-migration` 命令安装 |
| 路径 | `optional-skills/migration/openclaw-migration` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent（Nous Research） |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Migration`、`OpenClaw`、`Hermes`、`Memory`、`Persona`、`Import` |
| 相关技能 | [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能激活后，智能体将依据此内容执行操作。
:::

# OpenClaw -> Hermes 迁移

当用户希望以最少的手动操作将 OpenClaw 配置迁移至 Hermes Agent 时，可使用此技能。

## CLI 命令

如需快速且无需交互式的迁移操作，可直接使用内置的 CLI 命令：

```bash
hermes claw migrate              # Full interactive migration
hermes claw migrate --dry-run    # Preview what would be migrated
hermes claw migrate --preset user-data   # Migrate without secrets
hermes claw migrate --overwrite  # Overwrite existing conflicts
hermes claw migrate --source /custom/path/.openclaw  # Custom source
```

该 CLI 命令会运行下文所述的相同迁移脚本。当您需要一种具备交互式引导功能、可预览试运行结果并能针对每项内容解决冲突的迁移方式时，可通过代理使用此技能。

**首次设置：** `hermes setup` 向导会自动检测 `~/.openclaw` 目录，并在开始配置前提示进行迁移。

## 该技能的功能

它通过 `scripts/openclaw_to_hermes.py` 脚本来实现以下功能：

- 将 `SOUL.md` 文件导入 Hermes 主目录，文件名保持不变；
- 将 OpenClaw 的 `MEMORY.md` 和 `USER.md` 文件转换为 Hermes 对应的内存条目；
- 将 OpenClaw 中的命令审批规则合并到 Hermes 的 `command_allowlist` 中；
- 迁移与 Hermes 兼容的消息设置，如 `TELEGRAM_ALLOWED_USERS`，并将 OpenClaw 的工作区设置映射为 Hermes 的工作目录配置；
- 将 OpenClaw 的技能复制到 `~/.hermes/skills/openclaw-imports/` 目录中；
- 可选地将 OpenClaw 的工作区说明文件复制到用户指定的 Hermes 工作区中；
- 将兼容的工作区资源（如 `workspace/tts/` 目录下的文件）复制到 `~/.hermes/tts/` 目录中；
- 对那些没有直接对应 Hermes 存储路径的非机密文档进行归档；
- 生成结构化报告，列出已迁移的项目、存在冲突的项目、被跳过的项目及其原因。

## 路径解析

该辅助脚本位于以下路径：

- `scripts/openclaw_to_hermes.py`

若通过 Skills Hub 安装此技能，其默认路径为：

- `~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`

请勿尝试使用如 `~/.hermes/skills/openclaw-migration/...` 这类简写路径。

在运行该辅助脚本之前，请遵循以下步骤：

1. 优先使用位于 `~/.hermes/skills/migration/openclaw-migration/` 下的已安装路径；
2. 若该路径无法使用，则查看已安装的技能目录，根据其中的 `SKILL.md` 文件确定脚本的准确位置；
3. 仅当已安装路径不存在或技能被手动移动时，才将 `find` 命令作为备用方案；
4. 调用终端工具时，切勿传递 `workdir: "~"` 参数。应使用用户主目录等绝对路径，或者完全省略 `workdir` 参数。

若使用 `--migrate-secrets` 参数，该脚本还会导入一组经过筛选的、与 Hermes 兼容的机密信息，目前包括：

- `TELEGRAM_BOT_TOKEN`

## 默认工作流程

1. 首先通过试运行进行预览；
2. 简要总结哪些内容可以迁移、哪些无法迁移以及哪些会被归档；
3. 若有 `clarify` 工具可用，应使用它来获取用户决策，而非要求用户直接输入文字回复；
4. 若试运行发现导入的技能目录存在冲突，应在执行前询问用户如何处理这些冲突；
5. 在执行前，让用户从两种支持的迁移模式中选择一种；
6. 仅当用户希望同步工作区说明文件时，才询问目标工作区路径；
7. 使用相应的预设参数和标志执行迁移操作；
8. 概要说明迁移结果，重点包括：
   - 已迁移的内容；
   - 被归档以供人工审核的内容；
   - 被跳过的内容及其原因。

## 用户交互协议

Hermes CLI 支持使用 `clarify` 工具进行交互式提问，但其功能有限制：

- 每次只能提供一个选项；
- 预定义的选项最多为 4 个；
- 还会自动提供一个“其他”选项供用户输入自由文本。

它**不支持**在单个提问中提供真正的多选复选框。

对于每次 `clarify` 调用，需满足以下要求：

- 必须包含一个非空的 `question` 字段；
- 仅在实际需要用户选择的提问中才包含 `choices` 字段；
- `choices` 中的选项应为 2 到 4 个纯文本选项；
- 绝不可使用 `...` 等占位符或截断后的选项形式；
- 绝不可通过额外空格来填充或美化选项内容；
- 绝不可在提问中添加虚假的表单字段，如“请输入目录路径”、留空行供填写，或使用 `_____` 等符号；
- 对于需要用户输入路径的开放式提问，只需提出问题即可；用户可在面板下方的常规 CLI 输入框中输入内容。

如果 `clarify` 调用返回错误，需查看错误信息，修正相关参数，然后使用有效的 `question` 和干净的选项列表重新尝试一次。

当 `clarify` 工具可用且试运行结果显示需要用户做出决策时，**接下来的操作必须是再次调用 `clarify` 工具**。切勿以常规助手回复的方式结束当前对话，例如：

- “让我为您列出可选选项”
- “您想怎么做？”
- “以下是可选选项”

如果需要用户做出决策，应先通过 `clarify` 获取用户的决定，然后再继续输出文字说明。如果仍有未解决的决策问题，不得在这些问题之间插入解释性文字。收到一次 `clarify` 的回复后，通常应立即进行下一次必要的 `clarify` 调用。

当试运行结果显示以下情况时，应将 `workspace-agents` 视为未解决的决策问题：

- `kind="workspace-agents"`
- `status="skipped"`
- 原因中包含“未提供目标工作区”

在这种情况下，必须在执行前询问用户关于工作区说明文件的处理方式。切勿默认将其视为应跳过该步骤。

由于存在上述限制，建议采用以下简化的决策流程：

1. 对于 `SOUL.md` 文件的冲突，使用 `clarify` 提供以下选项供用户选择：
   - 保留现有版本
   - 用备份版本覆盖
   - 先进行查看
2. 如果试运行显示有一个或多个 `kind="skill"` 类型的项目且状态为 `conflict`，则使用 `clarify` 提供以下选项：
   - 保留现有的技能
   - 用备份版本覆盖有冲突的技能
   - 将有冲突的技能导入到重命名的文件夹中
3. 对于工作区说明文件的处理，使用 `clarify` 提供以下选项：
   - 跳过工作区说明文件的同步
   - 复制到指定的工作区路径
   - 稍后决定
4. 如果用户选择复制工作区说明文件，则需进一步提出开放式 `clarify` 问题，要求用户输入**绝对路径**；
5. 如果用户选择“跳过工作区说明文件”或“稍后决定”，则无需添加 `--workspace-target` 参数即可继续；
6. 对于迁移模式的选择，使用 `clarify` 提供以下三个选项：
   - 仅迁移用户数据
   - 执行完整的兼容性迁移（包括已筛选的机密信息）
   - 取消迁移
7. “仅迁移用户数据”意味着：迁移用户数据及兼容的配置文件，但**不**导入已筛选的机密信息；
8. “完整的兼容性迁移”意味着：迁移相同的兼容用户数据，同时导入已筛选的机密信息（如果存在的话）；
9. 如果无法使用 `clarify` 工具，则需以普通文本形式提出相同的问题，但仍要将用户的回答限制在“仅迁移用户数据”、“完整的兼容性迁移”或“取消迁移”这三种选项之中。

执行前提条件：

- 只有在因“未提供目标工作区”而导致 `workspace-agents` 任务被跳过的问题得到解决后，才能执行迁移；
- 解决该问题的有效方式仅有以下几种：
  - 用户明确选择“跳过工作区说明文件”；
  - 用户明确选择“稍后决定”；
  - 用户在选择“复制到指定的工作区路径”后提供了具体的工作区路径；
- 试运行中未指定目标工作区，并不意味着可以立即执行迁移；
- 只有在所有必要的 `clarify` 决策问题都得到解决后，才能执行迁移。

请严格使用以下格式的 `clarify` 参数作为默认结构：

- `{"question":"您现有的 SOUL.md 文件与导入的版本存在冲突，我应该怎么做？","choices":["keep existing","overwrite with backup","review first"]}`
- `{"question":"已有一个或多个从 OpenClaw 导入的技能存在于 Hermes 中，我该如何处理这些冲突？","choices":["keep existing skills","overwrite conflicting skills with backup","import conflicting skills under renamed folders"]}`
- `{"question":"请选择迁移模式：仅迁移用户数据，还是执行包含已筛选机密信息的完整兼容性迁移？","choices":["user-data only","full compatible migration","cancel"]}`
- `{"question":"您是否希望将 OpenClaw 的工作区说明文件复制到 Hermes 的某个工作区中？","choices":["skip workspace instructions","copy to a workspace path","decide later"]}`
- `{"question":"请提供目标工作区路径，以便复制工作区说明文件。"}`

## 决策与命令的对应关系

需将用户的决策准确映射为相应的命令参数：

- 如果用户选择对 `SOUL.md` 保留现有版本，则**不要**添加 `--overwrite` 参数；
- 如果用户选择用备份版本覆盖，则添加 `--overwrite` 参数；
- 如果用户选择先进行查看，则在执行前暂停，让用户先查看相关文件；
- 如果用户选择保留现有的技能，则添加 `--skill-conflict skip` 参数；
- 如果用户选择用备份版本覆盖有冲突的技能，则添加 `--skill-conflict overwrite` 参数；
- 如果用户选择将有冲突的技能导入到重命名的文件夹中，则添加 `--skill-conflict rename` 参数；
- 如果用户选择“仅迁移用户数据”，则使用 `--preset user-data` 参数执行迁移，且**不要**添加 `--migrate-secrets` 参数；
- 如果用户选择“完整的兼容性迁移”，则使用 `--preset full --migrate-secrets` 参数执行迁移；
- 仅当用户明确提供了具体的绝对路径时，才添加 `--workspace-target` 参数；
- 如果用户选择“跳过工作区说明文件”或“稍后决定”，则无需添加 `--workspace-target` 参数。

在执行迁移之前，需用通俗的语言再次说明具体的执行计划，并确保该计划与用户的决策一致。

## 执行后的报告规则

执行完成后，应以脚本生成的 JSON 输出结果作为最权威的依据。

1. 所有的计数数据均来源于 `report.summary` 部分；
2. 仅当某项内容的 `status` 字段确切为 `migrated` 时，才将其列入“已成功迁移”的列表中；
3. 除非报告显示某项内容已被标记为“已迁移”，否则不得声称该冲突已得到解决；
4. 除非 `kind="soul"` 类型的项目在报告中被标记为 `status="migrated"`，否则不得声明 `SOUL.md` 文件已被覆盖；
5. 如果 `report.summary.conflict` 的数值大于 0，则需单独列出冲突相关内容，而不得隐含迁移已成功的含义；
6. 如果计数数据与列出的项目内容不一致，则需在回复之前调整列表，使其与报告内容保持一致；
7. 若报告中有 `output_dir` 路径信息，应一并列出，以便用户查看 `report.json`、`summary.md` 文件、备份文件以及被归档的文件；
8. 对于内存条目或用户配置文件因空间不足而被归档的情况，除非报告明确指出了归档路径，否则不得声称这些条目已被归档。如果存在 `details.overflow_file` 文件，则应说明所有的溢出内容均已导出到该文件中；
9. 如果某个技能是导入到重命名的文件夹中的，需在报告中说明其最终存储位置，并提及 `details.renamed_from` 字段中记录的原始文件夹名称；
10. 如果报告中有 `report.skill_conflict_mode` 字段，则应以该字段所指定的规则作为判断导入技能冲突处理方式的依据；
11. 如果某项内容的 `status` 为 `skipped`，则不得将其描述为已被覆盖、备份、迁移或解决；
12. 如果 `kind="soul"` 类型的项目状态为 `skipped`，且原因显示“目标与源文件相同”，则应说明该项目保持不变，无需提及任何备份操作；
13. 如果某个被重命名的导入技能的 `details.backup` 字段为空，则不得暗示 Hermes 中原有的技能已被重命名或备份。只需说明导入的版本已被放置到新的目标位置，并提及 `details.renamed_from` 字段中记录的原有文件夹名称。

## 迁移预设选项

在日常使用中，建议优先选择以下两种预设模式：

- `user-data`
- `full`

`user-data` 模式包含以下内容：

- `soul`
- `workspace-agents`
- `memory`
- `user-profile`
- `messaging-settings`
- `command-allowlist`
- `skills`
- `tts-assets`
- `archive`

`full` 模式则包含 `user-data` 模式中的所有内容，此外还包含：

- `secret-settings`该辅助脚本仍支持在类别层级使用 `--include` / `--exclude` 参数，但应将其视为一种高级的备用功能，而非默认的用户体验。  

## 命令  

执行包含完整资源发现的模拟运行：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py
```

在使用终端工具时，建议采用如下这种绝对调用方式：

```json
{"command":"python3 /home/USER/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py","workdir":"/home/USER"}
```

使用用户数据预设进行模拟运行：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --preset user-data
```

执行用户数据迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict skip
```

执行完全兼容的迁移：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset full --migrate-secrets --skill-conflict skip
```

按包含工作区指令的方式执行：

```bash
python3 ~/.hermes/skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py --execute --preset user-data --skill-conflict rename --workspace-target "/absolute/workspace/path"
```

默认情况下，请勿将 `$PWD` 或用户主目录设置为工作空间目标，应首先询问用户明确指定的工作空间路径。

## 重要规则

1. 除非用户明确要求立即执行，否则应在写入数据前先进行试运行。
2. 默认情况下不得迁移机密信息。令牌、认证数据块、设备凭证以及原始网关配置均不应被导入 Hermes，除非用户明确要求迁移这些机密内容。
3. 除非用户明确希望如此，否则不得默默覆盖非空的 Hermes 目标。若启用了备份功能，辅助脚本会保留原有数据。
4. 始终需向用户提供已跳过项目的报告。该报告是迁移流程的必要部分，而非可选附加项。
5. 应优先使用主 OpenClaw 工作空间（`~/.openclaw/workspace/`），而非 `workspace.default/`。仅当主工作空间中的文件缺失时，才将默认工作空间作为备用。
6. 即使处于机密信息迁移模式，也仅能在目标 Hermes 环境正常的情况下迁移机密信息。不受支持的认证数据块仍需标记为已跳过。
7. 若试运行显示有大量资产需要复制、存在冲突的 `SOUL.md` 文件或内存条目已满，应在执行前分别指出这些问题。
8. 若用户不确定，应默认仅处理“用户数据”部分。
9. 仅当用户明确提供了目标工作空间路径时，才包含 `workspace-agents` 目录。
10. 将类别级别的 `--include`/`--exclude` 选项视为高级应急手段，而非常规操作方式。
11. 若存在 `clarify` 功能，切勿在试运行总结时使用含糊的“您想做什么？”这类表述，而应使用结构化的后续提示。
12. 当可以使用明确的选项式提示时，不要使用开放式的 `clarify` 提示。应优先提供可选选项，仅在需要输入绝对路径或审核文件时才允许自由输入文本。
13. 试运行结束后，若仍有未解决的决策问题，切勿仅作总结便结束流程，应立即针对最高优先级的阻塞性问题使用 `clarify` 功能。
14. 后续问题的处理优先级如下：
    - `SOUL.md` 文件冲突
    - 导入的技能之间存在冲突
    - 迁移模式选择
    - 工作空间目标设置
15. 不得在同一条消息中承诺稍后会给出选项，而应通过实际调用 `clarify` 功能来呈现选项。
16. 在获取用户对迁移模式的回答后，需明确检查 `workspace-agents` 问题是否仍未解决。若仍有未解决项，下一步操作必须是对工作空间设置使用 `clarify` 功能。
17. 在获得任何 `clarify` 的回答后，若还有其他必须做出的决策，切勿复述刚刚的决策内容，应立即提出下一个必要问题。

## 预期结果

成功执行迁移后，用户应获得以下结果：

- Hermes 人物状态已被导入
- Hermes 内存文件已填充转换后的 OpenClaw 知识
- OpenClaw 技能会出现在 `~/.hermes/skills/openclaw-imports/` 目录下
- 一份迁移报告，列出所有冲突、遗漏或不受支持的数据信息
