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

由 [Nous Research](https://nousresearch.com) 开发的自我进化型 AI 智能体。它是唯一具备内置学习循环的智能体——能够从使用经验中构建技能，在使用过程中不断优化这些技能，主动促使自己保留知识，并在多次会话之间逐步构建出对你更深入的了解。

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
  <Link
    to="/user-guide/bot-mode"
    style={{
      display: "inline-block",
      padding: "0.6rem 1.2rem",
      border: "1px solid rgba(255,215,0,0.2)",
      borderRadius: "8px",
      textDecoration: "none",
    }}
  >
    探索机器人体验
  </Link>
  <a
    href="https://hermes-agent.nousresearch.com/"
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
</div>

## 安装

### Windows 或 macOS

如需轻松安装命令行工具及桌面应用程序，请从我们的网站[下载 Hermes Desktop 安装程序](https://hermes-agent.nousresearch.com/)并运行它。

### 无需 Hermes Desktop 的情况：

如仅需安装命令行工具而无需 Hermes Desktop，请运行以下命令：

#### Linux / macOS / WSL2 / Android (Termux)

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

#### Windows（原生版）

在 PowerShell 中运行：

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

如需了解安装程序的功能、不同用户权限下的目录结构以及针对 Windows 系统的特别说明，请参阅完整的**[安装指南](/getting-started/installation)**。完整的平台支持列表请查看**[平台支持情况](/getting-started/platform-support)**。

:::提示 最快捷的代理启动方式
安装完成后，运行 `hermes setup --portal` 即可——一个 OAuth 认证即可同时使用模型以及全部四种工具网关功能（网页搜索、图像生成、文本转语音、浏览器）。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 什么是 Hermes Agent？

它既不是绑定在 IDE 上的编码辅助工具，也不是围绕单一 API 构建的聊天机器人。而是一个**自主代理**，运行时间越长，其能力就越强。它可以部署在任何地方——无论是价格仅为 5 美元的 VPS、GPU 集群，还是像 Daytona、Modal 这样在空闲时几乎无需成本的服务器less 平台。您可以在 Telegram 中与它交互，而它则会在您无需亲自登录的云虚拟机上运行。它并不受限于您的笔记本电脑。

## 快速链接

|                                                                         |                                                                       |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 🚀 **[Installation](/getting-started/installation)**                    | Install in 60 seconds on Linux, macOS, WSL2, native Windows, Nix & NixOS or Android |
| 📖 **[Quickstart Tutorial](/getting-started/quickstart)**               | Your first conversation and key features to try                       |
| 🗺️ **[Learning Path](/getting-started/learning-path)**                  | Find the right docs for your experience level                         |
| ⚙️ **[Configuration](/user-guide/configuration)**                       | Config file, providers, models, and options                           |
| 💬 **[Messaging Gateway](/user-guide/messaging)**                       | Set up Telegram, Discord, Slack, WhatsApp, Teams, or more             |
| 🤖 **[Bot Mode](/user-guide/bot-mode)**                                | Named Bots with their own model, memory, skills, routines, and chats  |
| 🔧 **[Tools & Toolsets](/user-guide/features/tools)**                   | 60+ built-in tools and how to configure them                          |
| 🧠 **[Memory System](/user-guide/features/memory)**                     | Persistent memory that grows across sessions                          |
| 📚 **[Skills System](/user-guide/features/skills)**                     | Procedural memory the agent creates and reuses                        |
| 🔌 **[MCP Integration](/user-guide/features/mcp)**                      | Connect to MCP servers, filter their tools, and extend Hermes safely  |
| 🧭 **[Use MCP with Hermes](/guides/use-mcp-with-hermes)**               | Practical MCP setup patterns, examples, and tutorials                 |
| 🎙️ **[Voice Mode](/user-guide/features/voice-mode)**                    | Real-time voice interaction in CLI, Telegram, Discord, and Discord VC |
| 🗣️ **[Use Voice Mode with Hermes](/guides/use-voice-mode-with-hermes)** | Hands-on setup and usage patterns for Hermes voice workflows          |
| 🎭 **[Personality & SOUL.md](/user-guide/features/personality)**        | Define Hermes' default voice with a global SOUL.md                    |
| 📄 **[Context Files](/user-guide/features/context-files)**              | Project context files that shape every conversation                   |
| 🔒 **[Security](/user-guide/security)**                                 | Command approval, authorization, container isolation                  |
| 💡 **[Tips & Best Practices](/guides/tips)**                            | Quick wins to get the most out of Hermes                              |
| 🏗️ **[Architecture](/developer-guide/architecture)**                    | How it works under the hood                                           |
| ❓ **[FAQ & Troubleshooting](/reference/faq)**                          | Common questions and solutions                                        |

## 核心功能

- **闭环学习机制** — 由智能体自主筛选并管理记忆内容，定期进行优化提示；支持智能体自主创建技能，且在使用过程中持续自我提升；具备FTS5跨会话信息检索功能，并可通过大语言模型实现内容总结；同时采用[Honcho](https://github.com/plastic-labs/honcho)的辩证式用户建模技术。
- **随处运行，不止限于笔记本** — 支持7种终端后端：本地环境、Docker、SSH、Daytona、Singularity、Modal以及Vercel Sandbox。Daytona和Modal还支持无服务器持久化功能——当系统处于空闲状态时，会自动进入休眠模式，几乎不会产生额外成本。
- **多平台无缝接入** — 支持CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、电子邮件、短信、钉钉、飞书、企业微信、微信、QQ机器人、元宝、BlueBubbles、Home Assistant、Microsoft Teams、Google Chat等20多种平台，仅需一个接口即可实现连接。
- **由模型训练专家打造** — 由Hermes、Nomos和Psyche背后的实验室[Nous Research](https://nousresearch.com)开发。可与[Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)、OpenAI或任何其他接口端点协同使用。
- **定时自动化任务** — 内置cron调度功能，可将任务交付至任意支持的平台执行。
- **[机器人模式](/user-guide/bot-mode)** — 可构建一支稳定的专业机器人团队，它们能在群聊中以及通过`@mentions`指令协同工作。
- **任务委托与并行处理** — 能够创建独立的子智能体以并行处理不同任务流。通过`execute_code`实现编程式工具调用，可将多步骤流程简化为单次推理请求。
- **开放标准技能** — 兼容 [agentskills.io](https://agentskills.io)。这些技能具备可移植性、可共享性，且可通过 Skills Hub 由社区共同贡献。  
- **全面网页控制功能** — 搜索、提取、浏览、视觉处理、图像生成、文本转语音——通过 [Nous Portal](/integrations/nous-portal) 的单一订阅即可同时使用所有功能。  
- **MCP 支持** — 可连接任意 MCP 服务器，从而拓展工具功能。  
- **科研级功能** — 支持批量处理、轨迹导出，以及结合 Atropos 进行强化学习训练。该功能由 [Nous Research](https://nousresearch.com) 开发，该团队正是 Hermes、Nomos 和 Psyche 模型的背后研发力量。  

## 面向大语言模型与编程智能体

可供机器读取的文档访问入口：  
- **[`/llms.txt`](/llms.txt)** — 包含每页文档的精选索引及简短描述，大小约 17 KB，可安全地加载到大语言模型的上下文中。  
- **[`/llms-full.txt`](/llms-full.txt)** — 将所有文档页面合并为一个 Markdown 文件，便于一次性读取，大小约为 1.8 MB。  

这两个文件的路径也为 `/docs/llms.txt` 和 `/docs/llms-full.txt`。每次部署后都会自动生成最新版本。
