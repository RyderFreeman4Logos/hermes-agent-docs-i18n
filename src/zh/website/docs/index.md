---
slug: /
sidebar_position: 0
title: "Hermes Agent Documentation"
description: "The self-improving AI agent built by Nous Research. A built-in learning loop that creates skills from experience, improves them during use, and remembers across sessions."
hide_table_of_contents: true
displayed_sidebar: docs
---

import Link from "@docusaurus/Link";

# Hermes Agent

由[Nous Research](https://nousresearch.com)打造的自我进化型AI智能体。它是唯一具备内置学习循环的智能体——能够从使用经验中生成技能，在使用过程中不断优化这些技能，促使自身持续保留知识，并在多次会话之间逐步构建对你更深入的了解。

<div
  style={{
    display: "flex",
    gap: "1rem",
    marginBottom: "2rem",
    flexWrap: "wrap",
  }}
>
  <Link
    to="/getting-started/installation"
    style={{
      display: "inline-block",
      padding: "0.6rem 1.2rem",
      backgroundColor: "#FFD700",
      color: "#07070d",
      borderRadius: "8px",
      fontWeight: 600,
      textDecoration: "none",
    }}
  >
    开始使用 →
  </Link>
  <a
    href="https://hermes-agent.nousresearch.com/desktop"
    style={{
      display: "inline-block",
      padding: "0.6rem 1.2rem",
      border: "1px solid rgba(255,215,0,0.2)",
      borderRadius: "8px",
      textDecoration: "none",
    }}
  >
    下载桌面版
  </a>
  <a
    href="https://github.com/NousResearch/hermes-agent"
    style={{
      display: "inline-block",
      padding: "0.6rem 1.2rem",
      border: "1px solid rgba(255,215,0,0.2)",
      borderRadius: "8px",
      textDecoration: "none",
    }}
  >
    在GitHub上查看
  </a>
</div>

## 安装

### Windows或macOS系统

如需轻松安装命令行工具及桌面应用，请从我们的网站[下载Hermes桌面版安装程序](https://hermes-agent.nousresearch.com/desktop)，然后运行该程序。

### 不使用Hermes桌面版的情况

若仅需安装命令行版本而无需桌面版，可执行以下操作：

#### Linux / macOS / WSL2 / Android（Termux）

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

#### Windows（原生版）

在 PowerShell 中运行：

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

请参阅完整的**[安装指南](/getting-started/installation)**，了解安装程序的功能、不同用户权限下的文件结构差异以及针对 Windows 系统的特别说明。

:::提示 快速让 Agent 正常运行的方法
安装完成后，运行 `hermes setup --portal` —— 一个 OAuth 认证即可同时启用模型以及四种工具网关功能（网页搜索、图像生成、文本转语音、浏览器）。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 什么是 Hermes Agent？

它既不是绑定在 IDE 上的代码辅助工具，也不是围绕单一 API 构建的聊天机器人。而是一个**自主型智能体**，运行时间越长，其能力就越强。它可以部署在任何地方——无论是价值 5 美元的虚拟专用服务器、GPU 集群，还是像 Daytona、Modal 这样在空闲时几乎不产生成本的服务器less 架构。你可以在自己从未登录过的云虚拟机上让它工作，同时通过 Telegram 与其进行交互。它并不局限于你的笔记本电脑。

## 快速链接

|                                                                         |                                                                       |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 🚀 **[安装](/getting-started/installation)**                    | 在 Linux、macOS、WSL2 或原生 Windows 系统上 60 秒完成安装        |
| 📖 **[快速入门教程](/getting-started/quickstart)**               | 开展首次对话及体验核心功能                                     |
| 🗺️ **[学习路径](/getting-started/learning-path)**                  | 根据你的使用经验水平查找合适的文档                               |
| ⚙️ **[配置](/user-guide/configuration)**                       | 配置文件、服务提供者、模型及各种选项                             |
| 💬 **[消息网关](/user-guide/messaging)**                       | 设置 Telegram、Discord、Slack、WhatsApp、Teams 等通信渠道         |
| 🔧 **[工具与工具集](/user-guide/features/tools)**                   | 60 多种内置工具及配置方法                                     |
| 🧠 **[记忆系统](/user-guide/features/memory)**                     | 能在多次会话间持续增长的持久化记忆                               |
| 📚 **[技能系统](/user-guide/features/skills)**                     | 智能体自行创建并重复使用的程序化记忆                           |
| 🔌 **[MCP 集成](/user-guide/features/mcp)**                      | 连接 MCP 服务器，筛选其工具，并安全扩展 Hermes 功能               |
| 🧭 **[在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)**               | 实用的 MCP 设置模式、示例及教程                                 |
| 🎙️ **[语音模式](/user-guide/features/voice-mode)**                    | 在 CLI、Telegram、Discord 及 Discord 视频通话中实现实时语音交互   |
| 🗣️ **[在 Hermes 中使用语音模式](/guides/use-voice-mode-with-hermes)** | Hermes 语音工作流的实操设置与使用方法                             |
| 🎭 **[个性设置与 SOUL.md](/user-guide/features/personality)**        | 通过全局 SOUL.md 文件定义 Hermes 的默认对话风格                   |
| 📄 **[上下文文件](/user-guide/features/context-files)**              | 用于为每段对话设定项目上下文的文件                             |
| 🔒 **[安全性](/user-guide/security)**                                 | 命令审批、授权机制及容器隔离技术                                 |
| 💡 **[技巧与最佳实践](/guides/tips)**                            | 让 Hermes 发挥最大效能的实用技巧                                 |
| 🏗️ **[架构设计](/developer-guide/architecture)**                    | 其底层运作原理                                             |
| ❓ **[常见问题与故障排除](/reference/faq)**                          | 常见问题及解决方案                                           |

## 核心功能

- **闭环学习机制** —— 由智能体自行筛选并管理的记忆系统，会定期进行提示；具备自主创建技能的能力，能在使用过程中不断优化技能表现；支持 FTS5 技术实现跨会话信息检索，并结合 LLM 进行内容总结；同时采用 [Honcho](https://github.com/plastic-labs/honcho) 的辩证式用户建模方法
- **可部署在任何地方，不仅限于笔记本电脑** —— 支持 6 种终端后端：本地环境、Docker、SSH、Daytona、Singularity、Modal。Daytona 和 Modal 提供服务器less 持久化功能——当环境处于空闲状态时会被“休眠”，几乎不产生额外成本
- **可集成到你常用的任何平台** —— 支持 CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、电子邮件、短信、钉钉、飞书、企业微信、微信、QQ 客服、元宝、BlueBubbles、Home Assistant、Microsoft Teams、Google Chat 等——通过一个网关即可连接 20 多个平台
- **由模型训练专家打造** —— 由 Hermes、Nomos 和 Psyche 等模型的研发团队 [Nous Research](https://nousresearch.com) 所创建。可与 [Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)、OpenAI 或任何其他接口端点配合使用
- **定时自动化功能** —— 内置 cron 定时任务系统，可将任务交付到任意平台执行
- **任务委托与并行处理** —— 可创建独立的子智能体以并行处理不同任务流；通过 `execute_code` 实现编程式工具调用，将多步骤流程简化为单次推理请求
- **符合开放标准的技能系统** —— 兼容 [agentskills.io](https://agentskills.io) 平台。各项技能具备可移植性、可共享性，且可通过技能中心由社区共同贡献
- **全面的网络控制功能** —— 搜索、信息提取、浏览、视觉处理、图像生成、文本转语音——通过 [Nous Portal](/integrations/nous-portal) 的单一订阅即可使用所有这些功能
- **MCP 支持** —— 可连接任何 MCP 服务器，从而获得更丰富的工具功能
- **适合研究用途** —— 支持批量处理、轨迹导出，以及结合 Atropos 工具进行强化学习训练。同样由 [Nous Research](https://nousresearch.com) 开发——该团队也是 Hermes、Nomos 和 Psyche 模型的创造者

## 面向大语言模型与编程智能体

可供机器读取的文档访问入口：

- **[`/llms.txt`](/llms.txt)** —— 包含所有文档页面的精选索引，每页都配有简短描述。文件大小约 17 KB，可安全地加载到大语言模型的上下文环境中。
- **[`/llms-full.txt`](/llms-full.txt)** —— 将所有文档页面合并为一个 markdown 文件，便于一次性导入。文件大小约 1.8 MB。

这两个文件的访问路径也为 `/docs/llms.txt` 和 `/docs/llms-full.txt`。每次部署后都会自动生成最新版本。
