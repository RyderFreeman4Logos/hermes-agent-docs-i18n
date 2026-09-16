---
title: "Decision Questionnaire — Turn an unanswerable decision into a questionnaire doc"
sidebar_label: "Decision Questionnaire"
description: "Turn an unanswerable decision into a questionnaire doc"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 决策问卷生成器

将难以独自解答的决策问题转化为问卷文档。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/productivity/decision-questionnaire` 安装 |
| 路径 | `optional-skills/productivity\decision-questionnaire` |
| 版本 | `1.0.0` |
| 开发者 | Matt Pocock (mattpocock/skills, to-questionnaire) + Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `questionnaire`、`decision`、`async`、`stakeholder`、`discovery`、`communication` |
| 相关技能 | [`会议行动项生成`](/docs/user-guide/skills/bundled/productivity/productivity-meeting-action-items)、[`文档转行动项`](/docs/user-guide/skills/bundled/productivity/productivity-document-to-action-items) |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为此内容。
:::

# 决策问卷生成器

可将用户无法独立解答的问题转化为**问卷**：一种 Markdown 格式的文档，用户可将其交给他人异步填写，或在会议中共同完成填写。接收方拥有用户所缺乏的知识，而问卷则能帮助从中提取这些信息。

该功能源自 mattpocock/skills 项目下基于 MIT 许可证的 `to-questionnaire` 技能。

## 适用场景

- 基于他人（领域专家、利益相关方、供应商联系人或运维人员）所提供的事实或判断来做出决策；  
- 用户表示“我需要向X咨询这个问题”，或不断推迟决策，等待他人的意见；  
- 正在为某次会议做准备，且该会议要求必须获得明确的答复。  

若答案可从环境中的资源（代码库、文档、网页等）中获取，则**不得**使用此方法——应先自行查找答案。  

## 核心原则：询问发送方，而非主题本身  

用户无法回答与主题相关的问题（这正是使用该工具的初衷），但他们始终可以回答关于发送方的问题。只需通过两次简短的交流来询问相关内容：  

1. **发送对象是谁？** 其角色、专业能力以及与用户的关系。这有助于确定问卷的基调以及需要包含的背景信息量。在明确知晓接收者身份及其掌握而用户不具备的信息后即可完成此步骤。  
2. **你需要对方提供什么答复？** 用户独自无法决定的具体决策或事实。在列出用户离开时必须能够完成的任务或做出的决定清单后即可完成此步骤。  

随后**编写问卷**：根据以下结构，针对接收者已知信息与用户需求之间的差距设计问题。将问卷内容写入当前目录下的 `decision-questionnaire-<slug>.md` 文件中（slug取自主题名称），并记录该文件的绝对路径。当文件已存在且第二步中的所有事项都对应有相应问题时，即可完成编写。  

## 文档结构

将其设计为**信息收集问卷**：用户缺乏相关背景信息，而信息接收方掌握这些内容。请按重要性由高到低排列问题（由于是异步处理，您可能只有一次提问机会）。当问题数量超过少量时，可按照主题将其归类在`##`标题下。

模板：

```markdown
# <Questionnaire title>

**Purpose:** why this questionnaire exists and the decision riding on it.

**From:** <the user> · **To:** <the recipient> ·
**How your answers will be used:** <where they go>

## Context

One paragraph orienting a recipient who wasn't in the user's head. Enough
to answer well, not a page.

## How to answer

Deadline and rough effort. Partial answers and "I don't know" are useful:
flag anything you're unsure of rather than skipping it.

## <Theme heading>

### <One question — a single idea, never compound>

_Why this matters: <one line, only where the question could be misread or
invite a throwaway answer>._

>

## Anything else?

A closing catch-all: anything we didn't ask that we should know?
```

每个问题下方都会直接显示一个答案占位符（`>`）。

## 常见误区

1. **过度追问用户相关细节**。用户可能无法回答——这正是文档存在的意义。只需询问发送方即可。
2. **复合型问题**。每个问题只涵盖一个核心点；需将“且/或”关联的问题拆分开。
3. **隐藏关键问题**。应优先呈现最重要的问题，避免让次要的、异步接收方容易忽略的内容占据突出位置。
4. **信息堆砌**。只需用一段文字进行背景介绍，无需罗列全部历史记录。
5. **对模糊问题遗漏“为何重要”的说明**。这一部分能让敷衍的回答变得有用——但对于本身已明确的问题则无需添加。

## 验证清单

- [ ] 在起草前，通过两次交流确认接收方的角色/知识水平以及所需达成的结果
- [ ] 所有步骤2中的内容都至少有一个问题进行覆盖
- [ ] 问题均为单核心点、按重要性排序，并包含答案占位符
- [ ] 文件已生成，并向用户告知其绝对路径
