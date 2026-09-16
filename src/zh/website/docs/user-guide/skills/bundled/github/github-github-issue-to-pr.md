---
title: "Github Issue To Pr — Carry a GitHub issue to a verified PR with honest CI state"
sidebar_label: "Github Issue To Pr"
description: "Carry a GitHub issue to a verified PR with honest CI state"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据该技能的 SKILL.md 自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 将 GitHub 问题转换为 Pull Request

将 GitHub 问题转化为状态可靠的验证过的 Pull Request。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/github/github-issue-to-pr` |
| 版本 | `0.1.0` |
| 创建者 | Ben Barclay (benbarclay)，Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `GitHub`、`Issues`、`Coding`、`Pull-Requests`、`CI` |
| 相关技能 | [`github-issues`](/docs/user-guide/skills/bundled/github/github-github-issues)、[`github-pr-workflow`](/docs/user-guide/skills/bundled/github/github-github-pr-workflow)、[`systematic-debugging`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging)、[`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development)、[`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能激活时，Agent 就会看到这些指令作为操作指南。
:::

# 将 GitHub 问题转为 Pull Request

将该 GitHub 问题转化为经过测试且验证通过的 Pull Request。该技能负责全流程管控——包括前提条件验证、重复任务排查、分类级修复以及如实的 CI 报告；而相关的 GitHub 及开发技能则各自处理各自的特定环节。

## 适用场景

- “修复问题 #123 并创建一个 PR。”
- “实现这个 GitHub 功能请求。”
- “将这个错误从问题状态推进到 CI 测试通过的状态。”

**不适用于**：审核现有 PR，或回答那些并未要求进行代码修改的问题。

## 操作步骤

### 1. 阅读实时问题内容——包括问题正文及完整讨论串

使用 `terminal` 运行命令 `gh issue view <N> --comments`。问题正文是提交时的快照；最新的评论则反映了当前实际情况：已合并的部分修复、新的根本原因分析、维护者的决策，或是针对你的、会改变任务要求的疑问。同时还需通过 `read_file` 查阅仓库的说明文件（如 `AGENTS.md` 和贡献指南）。当已明确当前要求实现的功能、排除的目标，以及所有未得到解答的讨论串问题后，此步骤即完成。

### 2. 排查已有处理工作及重复任务

在开始编写任何代码之前，先运行命令 `gh pr list --search "#<N>" --state all`，并结合至少两种描述该问题的关键词或同义词组合（如 `gh pr list --search "<subsystem> <symptom>" --state open`）进行查询。热门问题往往会有多个独立的修复方案；重复处理不仅会浪费精力，还会导致功劳被重复计算。此外，还需检查最近的提交记录中是否已有相关修复：可使用命令 `git log --oneline -20 -- <relevant files>` 查看。当已掌握所有相关的开放 PR 以及最近涉及该问题的提交记录，或确认不存在此类内容时，此步骤即完成。

### 3. 根据当前代码及设计初衷验证问题前提

在当前的默认分支上，通过失败的测试用例或测试 fixture 复现缺陷或展示缺失的功能，利用 `search_files` 和 `read_file` 功能定位问题所在路径。随后需要回答第二个问题：该“缺陷”实际上是否是刻意的设计？针对需要修改的代码运行 `git log -p -S "<symbol>"`，并仔细阅读原始提交记录中的设计意图——往往那些被忽视的环节或限制本身就是预期的功能。应当对过时或有误的 issue 描述提出质疑，而非盲目执行修改。只有当在当前代码中找到了根本原因或功能缺口，且该修改并不违背原有设计意图时，步骤才算完成。

### 4. 明确验收标准与风险点

列出验收标准、接口要求、数据迁移/状态变更、兼容性、安全与隐私问题、发布计划以及回滚方案。将每一项标准都与相应的测试用例或明确的验证方法对应起来。只有当审查过程有了清晰的约束条件时，步骤才算完成。

### 5. 实现最小化的完整修改——并修复相关类结构

请在独立的分支或工作树中进行开发。当错误类型需要时，可启用 `systematic-debugging` 或 `test-driven-development` 功能。首先编写回归测试，再实现修复代码。确定修复方案后，使用 `search_files` 查找同一类错误在其他相关位置的出现，并在该 PR 中一次性修复整个问题——留下未修复的同类问题比完全不修复还要糟糕。每修改的一行都必须与原始问题相关联，严禁随意清理代码。只有当目标测试通过、原有错误不再出现，且所有相关位置都得到修复或被明确排除后，才算工作完成。

### 6. 验证回归测试的有效性（破坏性测试）

暂时恢复正在测试的函数原有的行为，运行新的测试并确认其失败；之后再恢复修复后的版本，确认测试通过。无论是否应用修复，都能通过的回归测试其实毫无意义。只有当测试在应用修复前的代码上明确失败时，才算验证完成。

### 7. 运行仓库质量检查后立即提交 PR

对相关代码片段运行格式化、代码检查、类型检查以及仓库规定的标准测试入口；同时在对比代码差异上使用 `requesting-code-review` 功能。之后立即推送代码并提交 PR——PR 才是触发 CI 测试的起点，而 CI 测试的延迟往往是最大的瓶颈，切勿拖延已完成的代码。关于 PR 的编写规范，可参考 `github-pr-workflow`：采用常规的分支/提交机制，正文部分需说明问题、解决方案、测试用例、潜在风险以及排除项。最后再次检查 PR，确认 HEAD SHA 值、基准分支、标题及包含的文件无误。只有当 PR 包含预期的代码差异且 CI 测试正在运行时，才算任务完成。

### 8. 如实反馈 Shepherd CI 结果并形成闭环

可通过 `gh pr checks` / `gh run view --log-failed` 查看实时检测结果及失败日志。需区分是由代码差异导致的故障，还是原有基准或基础设施问题——若不确定，可在默认分支上复现问题；仅针对真正的基础设施偶发故障重新运行测试一次。在没有实时的确切状态证明之前，绝不能声称“通过”、“已合并”或“已发布”。当 PR 被合并后，应在相关问题下留言，附上 PR 链接及简短说明，以便问题报告者能够追踪到问题的解决过程。只有当 CI 状态、剩余阻碍以及问题讨论帖均反映真实情况时，才算完成。

## 常见误区

- 未阅读问题评论便开始编码，或草率检查是否存在重复 PR，又或直接查看当前代码。
- 将原始提交中明确为有意设计的功能“修复”掉。
- 仅修复了某个调用点的问题，而其他类似位置仍存在相同缺陷。
- 发布了在未应用修复的情况下也能通过的回归测试。
- 提交的 PR 中包含未运行的测试或无关的格式改动。
- 仅因存在 PR 就声称问题已解决。

## 验证方式

- [ ] 已完整阅读问题讨论帖，计划中已体现最新评论状态。  
- [ ] 使用问题编号及2种关键词变体执行了重复PR扫描。  
- [ ] 在当前代码环境中复现了问题现象，并通过Git历史记录验证了设计初衷。  
- [ ] 经验证，若不进行修复，回归测试将会失败。  
- [ ] 已修复相关调用点，或明确排除了其影响。  
- [ ] 所有被修改的代码行均与该问题相关联。  
- [ ] CI运行状态仅基于实时检测结果汇报；问题描述中已附上PR链接。
