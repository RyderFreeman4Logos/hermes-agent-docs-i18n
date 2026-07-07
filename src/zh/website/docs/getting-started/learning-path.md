---
sidebar_position: 3
title: 'Learning Path'
description: 'Choose your learning path through the Hermes Agent documentation based on your experience level and goals.'
---

# 学习路径

Hermes Agent功能极为丰富——可作为CLI助手、Telegram/Discord机器人、任务自动化工具，还能用于强化学习模型训练等。本页面会根据您的使用经验及目标，帮助您确定入门起点及学习顺序。

:::提示 从这里开始
如果您尚未安装Hermes Agent，请先阅读[安装指南](/getting-started/installation)，随后完成[快速入门](/getting-started/quickstart)。以下所有内容均假设您已成功完成安装。
:::

:::提示 首次设置Provider
首次使用的用户通常会选择执行 `hermes setup --portal` 命令——一个OAuth授权即可同时启用模型以及四种工具网关功能（搜索、图像处理、文本转语音、浏览器）。详情请参阅[Nous Portal](/integrations/nous-portal)。
:::

## 如何使用本页面

- **了解自己的水平？**请查看[经验等级表](#by-experience-level)，按照对应等级的阅读顺序进行学习。
- **有特定目标？**直接跳至[按使用场景分类](#by-use-case)，找到符合您需求的方案。
- **仅想浏览了解？**可查看[核心功能概览](#key-features-at-a-glance)表格，快速了解Hermes Agent的所有功能。

## 按经验等级划分

| 等级 | 目标 | 推荐学习内容 | 预计耗时 |
|---|---|---|---|
| **初学者** | 能够快速上手，进行基础对话，使用内置工具 | [安装](/getting-started/installation) → [快速入门](/getting-started/quickstart) → [CLI使用指南](/user-guide/cli) → [配置指南](/user-guide/configuration) | 约1小时 |
| **中级用户** | 设置消息机器人，使用内存、定时任务、技能等高级功能 | [会话管理](/user-guide/sessions) → [消息功能](/user-guide/messaging) → [工具功能](/user-guide/features/tools) → [技能功能](/user-guide/features/skills) → [内存功能](/user-guide/features/memory) → [定时任务功能](/user-guide/features/cron) | 约2–3小时 |
| **高级用户** | 开发自定义工具，创建技能，使用强化学习训练模型，为项目做出贡献 | [架构设计](/developer-guide/architecture) → [添加工具](/developer-guide/adding-tools) → [创建技能](/developer-guide/creating-skills) → [项目贡献指南](/developer-guide/contributing) | 约4–6小时 |

## 按使用场景分类

选择符合您需求的场景，每个场景都会按推荐顺序链接到相关文档。

### “我需要一个CLI编程助手”

将Hermes Agent作为交互式终端助手，用于编写、审查和运行代码。

1. [安装](/getting-started/installation)
2. [快速入门](/getting-started/quickstart)
3. [CLI使用指南](/user-guide/cli)
4. [代码执行功能](/user-guide/features/code-execution)
5. [上下文文件功能](/user-guide/features/context-files)
6. [实用技巧](/guides/tips)

:::提示
可通过上下文文件将文件直接放入对话中。Hermes Agent能够读取、编辑并运行您项目中的代码。
:::

### “我需要一个Telegram/Discord机器人”

在您常用的消息平台上部署Hermes Agent作为机器人使用。

1. [安装](/getting-started/installation)
2. [配置指南](/user-guide/configuration)
3. [消息功能概览](/user-guide/messaging)
4. [Telegram集成设置](/user-guide/messaging/telegram)
5. [Discord集成设置](/user-guide/messaging/discord)
6. [语音模式](/user-guide/features/voice-mode)
7. [在Hermes中使用语音模式](/guides/use-voice-mode-with-hermes)
8. [安全指南](/user-guide/security)

完整的项目示例请参考：
- [每日简报机器人](/guides/daily-briefing-bot)
- [团队Telegram助手](/guides/team-telegram-assistant)

### “我想要实现任务自动化”

安排重复性任务，运行批量作业，或串联多个代理操作。

1. [快速入门](/getting-started/quickstart)
2. [定时任务功能](/user-guide/features/cron)
3. [批量处理功能](/user-guide/features/batch-processing)
4. **委托功能**（原“Delegation”）( /user-guide/features/delegation)
5. **钩子功能**（原“Hooks”）( /user-guide/features/hooks)

:::提示
定时任务功能允许Hermes Agent在预设时间自动执行任务——如每日总结、定期检查、自动生成报告等——无需您持续操作。
:::

### “我想要开发自定义工具/技能”

通过自定义工具和可复用的技能包扩展Hermes Agent的功能。

1. [插件功能](/user-guide/features/plugins)
2. [开发Hermes插件](/developer-guide/plugins)
3. [工具功能概览](/user-guide/features/tools)
4. [技能功能概览](/user-guide/features/skills)
5. **MCP（模型上下文协议）**( /user-guide/features/mcp)
6. [架构设计](/developer-guide/architecture)
7. [添加工具](/developer-guide/adding-tools)
8. [创建技能](/developer-guide/creating-skills)

:::提示
对于大多数自定义工具的开发，建议从插件开始。[添加工具](/developer-guide/adding-tools)页面适用于Hermes核心功能的开发，而非普通用户自定义工具的路径。
:::

### “我想要训练模型”

利用强化学习技术，通过Hermes Agent的强化学习训练流程（基于[Atropos](https://github.com/NousResearch/atropos)引擎）优化模型行为。

1. [快速入门](/getting-started/quickstart)
2. [配置指南](/user-guide/configuration)
3. [Atropos强化学习环境](https://github.com/NousResearch/atropos)（外部链接）
4. [Provider路由功能](/user-guide/features/provider-routing)
5. [架构设计](/developer-guide/architecture)

:::提示
如果您还不熟悉Hermes Agent处理对话和工具调用的基本原理，建议先完成初学者路径的学习。
:::

### “我想要将其作为Python库使用”

通过编程方式将Hermes Agent集成到自己的Python应用程序中。

1. [安装](/getting-started/installation)
2. [快速入门](/getting-started/quickstart)
3. [Python库使用指南](/guides/python-library)
4. [架构设计](/developer-guide/architecture)
5. [工具功能](/user-guide/features/tools)
6. [会话管理](/user-guide/sessions)

## 核心功能概览

不确定有哪些功能可用？以下是主要功能的快速概览：

| 功能 | 功能说明 | 链接 |
|---|---|---|
| **工具功能** | 代理可调用的内置工具（文件读写、搜索、命令行等） | [工具功能](/user-guide/features/tools) |
| **技能功能** | 可安装的插件包，用于添加新功能 | [技能功能](/user-guide/features/skills) |
| **内存功能** | 实现会话间的持久化记忆 | [内存功能](/user-guide/features/memory) |
| **上下文文件功能** | 将文件和目录内容纳入对话中 | [上下文文件功能](/user-guide/features/context-files) |
| **MCP功能** | 通过模型上下文协议连接外部工具服务器 | [MCP功能](/user-guide/features/mcp) |
| **定时任务功能** | 安排代理的重复性任务 | [定时任务功能](/user-guide/features/cron) |
| **委托功能** | 创建子代理以实现并行处理 | [委托功能](/user-guide/features/delegation) |
| **代码执行功能** | 运行能够调用Hermes工具的Python脚本 | [代码执行功能](/user-guide/features/code-execution) |
| **浏览器功能** | 支持网页浏览和数据抓取 | [浏览器功能](/user-guide/features/browser) |
| **钩子功能** | 基于事件的回调机制与中间件支持 | [钩子功能](/user-guide/features/hooks) |
| **批量处理功能** | 批量处理多个输入任务 | [批量处理功能](/user-guide/features/batch-processing) |
| **Provider路由功能** | 在多个大语言模型提供商之间路由请求 | [Provider路由功能](/user-guide/features/provider-routing) |

## 接下来该阅读什么

根据您当前的学习阶段：

- **刚完成安装？** → 请阅读[快速入门](/getting-started/quickstart)，开始您的第一次对话测试。
- **已完成快速入门？** → 请阅读[CLI使用指南](/user-guide/cli)和[配置指南](/user-guide/configuration)，自定义您的设置。
- **已掌握基础知识？** → 请深入学习[工具功能](/user-guide/features/tools)、[技能功能](/user-guide/features/skills)和[内存功能](/user-guide/features/memory)，充分释放代理的潜力。
- **正在为团队做准备？** → 请阅读[安全指南](/user-guide/security)和[会话管理](/user-guide/sessions)，了解访问控制与对话管理方法。
- **准备开始开发？** → 请阅读[开发者指南](/developer-guide/architecture)，了解内部架构并开始为项目做出贡献。
- **需要实际案例参考？** → 请查看[指南](/guides/tips)部分，了解真实项目案例及实用技巧。

:::提示
无需全部阅读。只需选择符合您目标的路径，按顺序阅读相关文档，即可快速高效地开始使用。随时可以返回本页面，查找下一步的学习内容。
:::
