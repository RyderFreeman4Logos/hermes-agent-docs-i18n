---
title: "Setup Wizard Generator — Generate a bash wizard guiding a human through manual setup"
sidebar_label: "Setup Wizard Generator"
description: "Generate a bash wizard guiding a human through manual setup"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 设置向导生成器

用于生成引导用户完成手动设置的 Bash 向导。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/devops/setup-wizard-generator` 安装 |
| 路径 | `optional-skills/devops\setup-wizard-generator` |
| 版本 | `1.0.0` |
| 开发者 | Matt Pocock (mattpocock/skills, wizard) + Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos |
| 标签 | `wizard`、`setup`、`onboarding`、`credentials`、`secrets`、`migration`、`bash`、`human-in-the-loop` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 就会看到这些指令作为操作指南。
:::

# 设置向导生成器

该工具可生成交互式的 Bash **向导**：即一种脚本，它能一步步引导用户完成那些手动操作繁琐、且每次都需要重复说明的流程。它会自动打开各个网址，明确指示用户需要点击和复制的内容，捕获输入的值并将其保存到相应位置（如 `.env` 文件或 GitHub 密钥中），在每个步骤结束后进行确认，并显示还剩多少步骤。

该功能源自 mattpocock/skills 项目中的 MIT 许可版 `wizard` 技能。

## 适用场景

- 需要由人工通过控制台逐步操作的基础设施或第三方服务配置（如 Stripe、Supabase、DNS、OAuth 应用）；
- 凭据、CI 密钥或仓库变量的设置；
- 包含不可逆人工审核步骤的一次性数据迁移或系统切换；
- 用户需交给团队成员执行的任何操作。

请勿将那些机器人可自行完成的步骤纳入此流程——此类操作应直接由机器人执行。

## 先决条件

- `bash`；仅当各阶段需要写入 GitHub 密钥/变量时才需要 `gh` CLI；
- 该技能目录下的模板文件：`templates/template.sh`。

## 执行步骤

### 1. 明确流程范围

详细列出人工需要执行的每一步操作以及过程中需要获取的每个值。首先阅读仓库相关文档，避免盲目提问：

- 配置阶段：`.env`、`.env.example`、`README`、`docker-compose*` 文件、框架配置文件以及 `.github/workflows/*` 文件（其中所有 `secrets.*`/`vars.*` 的引用项都是向导需要生成的值）；
- 数据迁移/系统切换阶段：当前状态、目标状态，以及两者之间不可逆的操作步骤。

向用户展示有序的阶段列表及每个阶段对应的输出值；用户可对阶段进行添加、删除或重新排序。当所有阶段均按顺序列出，且对于每一个需获取的值，你都能明确：(a) 人工从何处获取该值；(b) 该值将被写入何处（`.env` 文件、GitHub 密钥、两者皆有或无存储位置）；(c) 该值是保密的（隐藏项）还是公开的，此时流程即完成。

### 2. 规划每个阶段的执行路径

对于每个步骤，都需要明确描述用户应遵循的具体路径：需要打开哪个网址、在该页面上执行什么操作，以及相关数值显示在何处——例如“控制面板 → 开发者 → API密钥 → 显示测试密钥 → 复制”。如果不确定当前的界面设计或确切命令，请如实说明，并查阅文档或寻求帮助；绝不可编造可能并不存在的步骤。

### 3. 编写向导脚本

将 `templates/template.sh`（位于该技能目录中）复制到目标路径。用按依赖顺序排列的各个步骤对应的 `stage` 变量替换示例中的步骤内容。同时将 `TOTAL_STAGES` 设置为你所定义的步骤总数。

可使用的库函数包括：`stage`、`say`/`step`/`note`/`warn`、`open_url`、`ask`/`ask_secret`、`write_env`、`set_secret`/`set_var`、`pause`/`confirm`、`banner`、`finish`。位于 `STAGES` 标记之后的库函数在所有向导脚本中都是相同的——切勿手动修改这部分内容，保持一致性正是其设计目的。

请遵循模板设定的规则：在要求用户输入数值之前先打开对应网址，敏感信息需通过 `ask_secret` 函数获取，所有需要持久保存的数值则用 `write_env` 处理，仅向 CI 系统所需的密钥使用 `set_secret`，而在执行任何不可撤销的操作前必须调用 `confirm`。每个 `stage` 执行完毕后都会清空屏幕——因此每个步骤应只聚焦于一项任务，避免用户需要查看的内容被滚动遮挡。

默认情况下，向导脚本为临时文件：可将其保存到临时目录或 `scripts/` 目录中，在任务完成后予以删除。只有当用户希望将可重复使用的配置路径存入代码仓库时，才需对其进行提交。

### 4. 验证并移交

- 使用 `bash -n <script>` 命令进行语法检查；若安装了 `shellcheck`，也可使用该工具；随后执行 `chmod +x <script>` 使脚本可执行。  
- **切勿自行从头到尾运行该脚本**：它会自动打开浏览器并等待人工输入。应采用静态追踪方式验证：确保第一步中的所有值都能被正确捕获并传递到指定位置，同时每个 `set_secret` 的名称必须与 CI 环境中的 `secrets.*` 变量引用完全匹配。  
- 需向用户说明具体的运行方法。若该流程可重复执行，应将其代码提交并在 README 中添加相关链接。  

## 常见误区

1. **误修改库相关部分**：`STAGES` 标记之前的所有内容都属于向导库，作者仅可在其下方进行编写。  
2. **随意编造控制面板路径**：第三方 UI 接口可能会发生变化。若不确定操作路径，应查阅最新文档，或标注该路径为近似值。  
3. **为 CI 环境未使用的值设置 `set_secret`**：仅应将工作流实际引用的密钥添加到 GitHub Secrets 中。  
4. **自行运行向导脚本**：该脚本会等待人工输入，因此应通过静态追踪及 `bash -n` 命令来进行验证。  
5. **使用过长的单一阶段**：若每个阶段都会清空屏幕，长阶段的滚动会导致关键指令被遮挡，应将其拆分为多个阶段。  

## 验证清单

- [ ] 在编写之前已与用户确认阶段列表无误  
- [ ] `bash -n` 检查通过，且脚本具备可执行权限  
- [ ] 所有捕获的值均已追溯到其指定的目标位置  
- [ ] 每个 `set_secret` 的名称都与 CI 环境中的 `secrets.*` 变量引用相匹配  
- [ ] 库相关部分未对模板进行任何修改
