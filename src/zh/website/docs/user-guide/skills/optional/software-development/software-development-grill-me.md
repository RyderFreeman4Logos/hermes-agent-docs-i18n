---
title: "Grill Me — Adversarial plan interview before implementation"
sidebar_label: "Grill Me"
description: "Adversarial plan interview before implementation"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据该技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Grill Me

在实现代码之前进行的对抗性规划面试。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/software-development/grill-me` 安装 |
| 路径 | `optional-skills/software-development\grill-me` |
| 版本 | `2.0.0` |
| 创建者 | Rafael Zendron (rafaumeu) + Matt Pocock (mattpocock/skills, grilling) + Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `planning`、`adversarial`、`interview`、`decision-tree`、`pre-implementation`、`review`、`alignment` |
| 相关技能 | [`requesting-code-review`](/docs/user-guide/skills/bundled/software-development/software-development-requesting-code-review)、[`subagent-driven-development`](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development)、[`test-driven-development`](/docs/user-guide/skills/bundled/software-development/software-development-test-driven-development) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当该技能处于激活状态时，智能体看到的指令即为此内容。
:::

# Grill Me

在编写任何代码之前，通过结构化的对抗性提问对计划进行压力测试。该功能会将计划建模为**设计树**——每个决策都会分支出后续的子决策——然后通过多轮对话逐步询问用户，直到所有分支都得到明确解答，避免任何隐含假设。

它融合了原有方法的阶段化流程，以及 mattpocock/skills 库中 `grilling` 功能的“前沿轮次”机制。

## 适用场景

- 用户提出“对我进行严格质询”、“审查我的计划”、“对这个想法进行压力测试”
- 在处理复杂任务之前：身份验证流程、数据结构变更、数据迁移、支付功能
- 当计划中存在未解决的决策或表述模糊时
- 在采用 `subagent-driven-development` 方法进行分解之前

**不适用于**现有代码的审查（请使用 `requesting-code-review`）或简单的单次任务。

## 先决条件

无需任何先决条件。该功能可应用于任何计划或初步构想。

## 核心机制：前沿轮次

将计划映射为设计树。**前沿**指的是那些前置条件已确定的决策——即你现在就可以提出问题，而无需猜测尚未知晓的答案。

通过**轮次**来进行操作：在一条消息中列出当前所有属于前沿的决策，并为每个问题标注你推荐的答案，随后等待回复。如果某个问题的答案依赖于同一轮次中尚未解答的其他问题，则该问题属于后续轮次，而非当前轮次。

每轮的格式如下：

```
❓ Q1 — <question title>: <question body, options if relevant>
➡️ Recommendation: <your recommended answer + one-line why>

❓ Q2 — <question title>: <question body>
➡️ Recommendation: <...>
```

每个答案都会重塑问题树结构：已确定的决策会将探索边界向外扩展，从而解除相关问题的阻塞。随后需重新计算边界并进入下一轮探索。

**事实由你负责收集，决策则由用户做出。** 当某个边界问题需要从环境（代码库、文件系统、配置文件、文档等）中获取信息时，应使用 `search_files` / `read_file` / `terminal` 等工具自行查找——若涉及复杂的探索任务，可通过 `delegate_task` 分配给子智能体处理。凡是能够自行查询到的信息，都不要向用户询问。切勿因某次探索而停滞不前：只有其后续的问题会受到影响，应立即继续探索其余的边界问题。

## 问题覆盖范围（将这些分支整合到问题树中）

**目标理解**——明确真实目标与边界：
- 真正的目标是什么？哪些内容明确属于工作范围，哪些不属于？
- 存在哪些约束条件（时间、技术、团队、预算等）？用户群体是谁？

**技术决策**——针对每一项架构选择：
- “为何选择这种方案而非X？” / “如果Y出现故障会怎样？”
- “最坏的情况是什么？” / “该如何回滚？”
- 对比现有代码库中的类似实现；如果项目中已有相关模式，应明确指出。

**边缘情况处理：**
- “如果用户执行Z操作会怎样？” / “如果依赖项X失效会如何？”
- “如果数据量是预期值的100倍会怎样？” / “这会带来哪些安全风险？”

## 综合总结（当探索边界为空时）

1. 用项目符号列出所有已做出的决策。
2. 列出尚未解决的问题，以及明确不属于工作范围的内容。
3. 提问：“各方意见一致吗？我应该开始实现功能，还是需要调整某些内容？”
在用户确认双方理解一致之前，切勿按照计划采取行动。

## 常见误区

1. **按错误的依赖顺序提问**。那些依赖于尚未得到解答的问题，其实只是带有问号的猜测。应将其留到后续环节再探讨。
2. **跳过代码库查询**。应使用Hermes工具直接在代码中查找信息，而非向用户询问。
3. **将“我不知道”视为最终答案**。应当提供多种选项，解释各方案的利弊，并给出建议。
4. **在询问过程中直接编写代码**。仅进行对齐讨论，只有在获得明确许可后才能编写代码。
5. **过于顺从**。你的职责是发现潜在问题。即便一切看似正常，也需进一步深入检查。
6. **不适应用户的语言习惯**。无论用户使用何种语言，都应使用该语言进行交流。

## 验证标准

- [ ] 每一轮中的所有问题，其前提条件均已得到解决
- [ ] 对每个问题都给出了相应建议
- [ ] 已通过代码库查询获取信息，而非依赖用户回答
- [ ] 在综合分析前，Frontier状态为空（未隐含假设任何分支）
- [ ] 提供了关于所有决策及待办事项的清晰总结
- [ ] 在结束工作前已确认用户理解一致
