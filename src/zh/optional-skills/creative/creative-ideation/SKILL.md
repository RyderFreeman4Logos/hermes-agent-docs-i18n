---
name: ideation
title: Creative Ideation — Constraint-Driven Project Generation
description: "Generate project ideas via creative constraints."
version: 1.0.0
author: SHL0MS
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Creative, Ideation, Projects, Brainstorming, Inspiration]
    category: creative
    requires_toolsets: []
---

# 创意构思

## 适用场景

当用户表示“我想打造点什么”、“给我一个项目灵感”、“我好无聊”、“该做点什么”、“给我点启发”，或是类似“我有工具但不知道该从何下手”的表述时，均可使用此功能。它适用于代码开发、艺术创作、硬件设计、写作、工具制作以及任何可以创造出来的事物。

通过设定创意约束来生成项目想法——约束条件 + 明确方向 = 创意诞生。

## 工作原理

1. **从以下约束库中选择一个约束条件**——可以是随机选取的，也可根据用户的领域或当前心情匹配。
2. **对其进行宽泛解读**——一个编程相关提示可以转化为硬件项目，艺术创作提示则可变为 CLI 工具。
3. **生成3个符合该约束条件的具体项目想法**。
4. **如果用户选定其中一个，即可开始实现它**——创建项目、编写代码并最终完成作品。

## 核心原则

所有提示都会被尽可能宽泛地解读。“这包括 X 吗？”→ 当然包括。这些提示会提供方向指引和适度约束，缺少其中任何一方，创意都无法产生。

## 约束条件库

### 面向开发者

**解决自己的需求：**
打造你希望本周就能出现的工具，代码行数不超过50行，并立即发布。

**自动化繁琐任务：**
你的工作流程中哪部分最令人头疼？用脚本将其自动化。原本每天要花费5分钟解决的问题，现在只需2小时即可解决。

**应该存在的 CLI 工具：**
想象一下你希望拥有的某个命令，比如 `git undo-that-thing-i-just-did`、`docker why-is-this-broken`、`npm explain-yourself`，现在就去实现它吧。

**仅用现有组件组合出新事物：**
完全使用现有的 API、库和数据集来创建作品，唯一的创新点在于你如何将它们整合在一起。

**“弗兰肯斯坦周”挑战：**
让原本能做 X 的工具具备 Y 功能。比如一个可以播放音乐的 Git 仓库、一个能生成诗歌的 Dockerfile、一个会发送赞美信息的定时任务。

**减法思维：**
在一个代码库中，你能删除多少内容而不使其崩溃？将工具简化到其最基本的功能形态，不断删减直至仅保留核心部分。

**高概念、低努力：**
拥有深刻的创意，但实现方式要尽可能简单。创意本身应足够出色，而实现过程则只需一个下午即可完成。如果耗时更长，那就说明你想得太多了。

### 面向创作者与艺术家

**直接模仿某样东西：**
挑选你欣赏的作品——无论是某个工具、艺术作品还是界面设计——然后从零开始重新创造它。学习的过程就在于你的版本与原作之间的差异。

**百万量级创作：**
“百万”这个数字听起来很多，但实际上也并非不可实现。100万像素对应一张1MB大小的图片，100万次 API 调用大概只需要一个工作日的时间。任何事物在达到百万量级时都会变得有趣。

**创造会“消亡”的作品：**
设计一个每天都会失去一项功能的网站、一个会逐渐遗忘的聊天机器人、一个不断倒数的计时器——以此探讨衰败、消亡或放手的过程。

**运用大量数学知识：**
生成几何图形、进行着色器优化、创作数学艺术、实现计算折纸等。是时候重新温习一下反正弦函数是什么了。

### 面向所有人

**文本即通用界面：**
打造仅以文本作为交互界面的作品，没有按钮，没有图形，只有输入和输出的文字。文本几乎可以融入任何类型的作品中。

**从笑点倒推实现：**
先想到一个有趣的句子，再反向设计将其变为现实。比如“我教会我的恒温器对我进行心理操控”，现在就去实现它吧。

**故意设计糟糕的界面：**
刻意打造使用起来极其不便的作品。比如需要满足47项条件的密码输入框、所有标签都包含虚假信息的表单，或是会评判用户命令的 CLI 工具。

**重做旧项目：**
回忆起一个旧项目，然后完全从零开始重新实现它，不要参考原来的代码。看看你的思维方式发生了哪些变化。

更多涵盖沟通、规模、哲学、转换等领域的30多种约束条件，请参阅 `references/full-prompt-library.md` 文件。

## 根据用户需求匹配约束条件

| 用户表述 | 建议选择的约束条件 |
|---------|------------------|
| “我想打造点什么”（无明确方向） | 随机选取——任意约束条件 |
| “我正在学习[某种语言]” | 直接模仿某样东西、自动化繁琐任务 |
| “我想要点与众不同的东西” | 故意设计糟糕的界面、“弗兰肯斯坦周”挑战、从笑点倒推实现 |
| “我想要实用的东西” | 解决自己的需求、应该存在的 CLI 工具、自动化繁琐任务 |
| “我想要美观的作品” | 运用大量数学知识、百万量级创作 |
| “我感到精疲力尽” | 高概念、低努力、创造会“消亡”的作品 |
| “周末项目” | 仅用现有组件组合出新事物、从笑点倒推实现 |
| “我想要接受挑战” | 百万量级创作、减法思维、重做旧项目 |

## 输出格式

```
## Constraint: [Name]
> [The constraint, one sentence]

### Ideas

1. **[One-line pitch]**
   [2-3 sentences: what you'd build and why it's interesting]
   ⏱ [weekend / week / month] • 🔧 [stack]

2. **[One-line pitch]**
   [2-3 sentences]
   ⏱ ... • 🔧 ...

3. **[One-line pitch]**
   [2-3 sentences]
   ⏱ ... • 🔧 ...
```

## 示例

```
## Constraint: The CLI tool that should exist
> Think of a command you've wished you could type. Now build it.

### Ideas

1. **`git whatsup` — show what happened while you were away**
   Compares your last active commit to HEAD and summarizes what changed,
   who committed, and what PRs merged. Like a morning standup from your repo.
   ⏱ weekend • 🔧 Python, GitPython, click

2. **`explain 503` — HTTP status codes for humans**
   Pipe any status code or error message and get a plain-English explanation
   with common causes and fixes. Pulls from a curated database, not an LLM.
   ⏱ weekend • 🔧 Rust or Go, static dataset

3. **`deps why <package>` — why is this in my dependency tree**
   Traces a transitive dependency back to the direct dependency that pulled
   it in. Answers "why do I have 47 copies of lodash" in one command.
   ⏱ weekend • 🔧 Node.js, npm/yarn lockfile parsing
```

用户在选定方案后，即可开始开发——创建项目、编写代码，并通过迭代不断优化。

## 出处说明

该约束式方法灵感来源于 [wttdotm.com/prompts.html](https://wttdotm.com/prompts.html)，后经调整与扩展，应用于软件开发及通用创意构思场景。
