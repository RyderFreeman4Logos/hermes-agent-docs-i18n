---
sidebar_position: 3
title: 'Learning Path'
description: 'Choose your learning path through the Hermes Agent documentation based on your experience level and goals.'
---

# 学习路径

Hermes Agent功能极为丰富——可作为CLI助手、Telegram/Discord机器人、任务自动化工具，还能用于强化学习训练等诸多场景。本页面会根据您的使用经验及目标需求，为您指引入门方向及推荐阅读资料。

:::提示 从这里开始
如果您尚未安装Hermes Agent，请先阅读[安装指南](/getting-started/installation)，随后完成[快速入门](/getting-started/quickstart)。以下所有内容均假设您已成功完成安装。
:::

:::提示 首次配置Provider
首次使用的用户通常希望执行`hermes setup --portal`命令——通过一次OAuth授权即可同时使用模型以及四种工具网关功能（搜索/图像/TTS/浏览器）。详情请参阅[Nous Portal](/integrations/nous-portal)。
:::

## 如何使用本页面

- **了解自己的水平？**请查看[经验等级表](#by-experience-level)，按照对应等级的阅读顺序进行学习。
- **有特定目标？**可直接跳至[按使用场景分类](#by-use-case)，找到匹配您的应用场景。
- **仅想简单浏览？**可查看[核心功能概览表](#key-features-at-a-glance)，快速了解Hermes Agent的所有功能。

## 按经验等级划分

| 级别 | 目标 | 推荐阅读资料 | 预计耗时 |
|---|---|---|---|
| **初学者** | 能够快速上手，进行基础对话，使用内置工具 | [安装指南](/getting-started/installation) → [快速入门](/getting-started/quickstart) → [CLI 使用指南](/user-guide/cli) → [配置指南](/user-guide/configuration) | 约1小时 |
| **中级用户** | 设置消息机器人，使用内存、定时任务及技能等高级功能 | [会话管理](/user-guide/sessions) → [消息功能](/user-guide/messaging) → [工具功能](/user-guide/features/tools) → [技能功能](/user-guide/features/skills) → [内存功能](/user-guide/features/memory) → [定时任务功能](/user-guide/features/cron) | 约2–3小时 |
| **高级用户** | 开发自定义工具，创建技能，利用强化学习训练模型，为项目做出贡献 | [架构设计](/developer-guide/architecture) → [添加工具](/developer-guide/adding-tools) → [创建技能](/developer-guide/creating-skills) → [项目贡献指南](/developer-guide/contributing) | 约4–6小时 |

## 按使用场景选择

根据您的需求选择对应的场景。每个场景都会按推荐顺序为您链接到相关文档。

### “我需要一个CLI编程助手”

将Hermes Agent用作交互式终端助手，用于编写、审查和运行代码。

1. [安装指南](/getting-started/installation)  
2. [快速入门](/getting-started/quickstart)  
3. [CLI 使用指南](/user-guide/cli)  
4. [代码执行功能](/user-guide/features/code-execution)  
5. [上下文文件](/user-guide/features/context-files)  
6. [实用技巧](/guides/tips)  

:::tip  
通过上下文文件将文件直接传递到对话中。Hermes Agent 可以读取、编辑并运行您项目中的代码。  
:::

### “我想要一个 Telegram/Discord 机器人”  
在您常用的消息平台上将 Hermes Agent 部署为机器人。  

1. [安装指南](/getting-started/installation)  
2. [配置设置](/user-guide/configuration)  
3. [消息功能概览](/user-guide/messaging)  
4. [Telegram 配置](/user-guide/messaging/telegram)  
5. [Discord 配置](/user-guide/messaging/discord)  
6. [语音模式](/user-guide/features/voice-mode)  
7. [如何与 Hermes 一起使用语音模式](/guides/use-voice-mode-with-hermes)  
8. [安全性说明](/user-guide/security)  

如需完整的项目示例，请参阅：  
- [每日简报机器人](/guides/daily-briefing-bot)  
- [团队 Telegram 助手](/guides/team-telegram-assistant)  

### “我想要自动化任务”  
安排定时任务、执行批量作业，或串联多个代理操作。  

1. [快速入门](/getting-started/quickstart)  
2. [Cron 定时调度](/user-guide/features/cron)  
3. [批量处理功能](/user-guide/features/batch-processing)  
4. [任务委托机制](/user-guide/features/delegation)  
5. [钩子功能](/user-guide/features/hooks)
:::提示
Cron任务功能允许Hermes Agent按照预定时间表自动执行各类任务——比如每日汇总、定期检查、自动生成报告等——无需您亲自操作。
:::

### “我需要一组专业的智能机器人”
您可以创建拥有独立模型、内存、技能、工作流程及聊天记录的命名机器人，再将它们通过群组聊天或`@提及`的方式组合在一起使用。
1. [桌面端](/user-guide/desktop)
2. [个人资料](/user-guide/profiles)
3. [机器人模式](/user-guide/bot-mode)
4. [Cron定时调度](/user-guide/features/cron)
5. [多连接桌面端](/user-guide/multi-connection-desktop)

### “我想要构建自定义工具/技能”
您可以使用自己的工具和可复用的技能包来扩展Hermes Agent的功能。
1. [插件](/user-guide/features/plugins)
2. [开发Hermes插件](/developer-guide/plugins)
3. [工具概览](/user-guide/features/tools)
4. [技能概览](/user-guide/features/skills)
5. [MCP（模型上下文协议）](/user-guide/features/mcp)
6. [架构设计](/developer-guide/architecture)
7. [添加工具](/developer-guide/adding-tools)
8. [创建技能](/developer-guide/creating-skills)

:::提示
对于大多数自定义工具的开发，建议从插件开始入手。[添加工具](/developer-guide/adding-tools)页面适用于Hermes核心功能的开发，而非常规的用户/自定义工具开发路径。
:::

### “我想要训练模型”
您可以利用Hermes Agent基于[Atropos](https://github.com/NousResearch/atropos)开发的强化学习训练流程，通过强化学习来优化模型的行为表现。

1. [快速入门](/getting-started/quickstart)  
2. [配置指南](/user-guide/configuration)  
3. [Atropos RL环境](https://github.com/NousResearch/atropos)（外部链接）  
4. [提供者路由功能](/user-guide/features/provider-routing)  
5. [架构设计](/developer-guide/architecture)  

:::提示  
在您已了解Hermes Agent处理对话及工具调用的基本原理后，进行强化学习训练效果会更佳。如果您是新手，建议先完成入门学习路径。  
:::

### “我希望将其作为Python库使用”  
通过编程方式将Hermes Agent集成到您自己的Python应用程序中。  

1. [安装指南](/getting-started/installation)  
2. [快速入门](/getting-started/quickstart)  
3. [Python库使用指南](/guides/python-library)  
4. [架构设计](/developer-guide/architecture)  
5. [工具功能](/user-guide/features/tools)  
6. [会话管理](/user-guide/sessions)  

## 核心功能概览  
不确定有哪些功能可用？以下是主要功能的简要列表：

| 功能特性 | 功能说明 | 链接 |
|---|---|---|
| **工具** | 智能体可调用的内置工具（文件读写、搜索、命令行等） | [工具](/user-guide/features/tools) |
| **技能** | 可安装的插件包，用于增添新功能 | [技能](/user-guide/features/skills) |
| **持久内存** | 跨会话保持内存数据 | [持久内存](/user-guide/features/memory) |
| **机器人模式** | 支持具备持久聊天记录、固定流程、群组聊天及`@提及`功能的专用机器人 | [机器人模式](/user-guide/bot-mode) |
| **上下文文件** | 将文件和目录内容引入对话中 | [上下文文件](/user-guide/features/context-files) |
| **MCP** | 通过模型上下文协议连接外部工具服务器 | [MCP](/user-guide/features/mcp) |
| **定时任务** | 安排智能体重复执行任务 | [定时任务](/user-guide/features/cron) |
| **任务委派** | 创建子智能体以并行处理任务 | [任务委派](/user-guide/features/delegation) |
| **代码执行** | 运行可程序化调用Hermes工具的Python脚本 | [代码执行](/user-guide/features/code-execution) |
| **浏览器功能** | 支持网页浏览和数据抓取 | [浏览器功能](/user-guide/features/browser) |
| **钩子机制** | 基于事件的回调功能及中间件 | [钩子机制](/user-guide/features/hooks) |
| **批量处理** | 批量处理多个输入数据 | [批量处理](/user-guide/features/batch-processing) |
| **提供商路由** | 在多个大语言模型提供商之间路由请求 | [提供商路由](/user-guide/features/provider-routing) |

## 推荐阅读内容

根据您当前所处的阶段：

- **刚完成安装？** → 请前往[快速入门](/getting-started/quickstart)，开始您的第一次对话测试。
- **已完成快速入门？** → 请阅读[CLI使用指南](/user-guide/cli)和[配置指南](/user-guide/configuration)，对系统进行个性化设置。
- **已掌握基础功能？** → 您可以探索[工具](/user-guide/features/tools)、[智能技能](/user-guide/features/skills)以及[记忆功能](/user-guide/features/memory)，从而充分释放该智能体的强大能力。
- **正在为团队搭建环境？** → 请阅读[安全指南](/user-guide/security)和[会话管理指南](/user-guide/sessions)，了解访问控制与对话管理的相关知识。
- **准备开始开发？** → 请参阅[开发者指南](/developer-guide/architecture)，深入了解系统内部架构，进而开始贡献代码。
- **需要实际案例参考？** → 请查看[指南](/guides/tips)板块，获取真实项目案例与实用技巧。

:::tip
您无需通读所有内容。只需选择符合您目标的路径，按顺序查看相关链接，即可快速高效地开展工作。随时可以返回此页面，查找下一步的操作指引。
:::
