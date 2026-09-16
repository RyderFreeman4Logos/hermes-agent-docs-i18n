---
title: "Agentmail — Use when an agent needs AgentMail CLI email inboxes"
sidebar_label: "Agentmail"
description: "Use when an agent needs AgentMail CLI email inboxes"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Agentmail

当智能体需要使用 AgentMail CLI 邮箱功能时使用。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/email/agentmail` 安装 |
| 路径 | `optional-skills/email\agentmail` |
| 版本 | `1.0.0` |
| 开发者 | Haakam Aujla (Haakam21)、AgentMail |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Email`、`CLI`、`AgentMail`、`Communication` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。智能体在技能启用时会看到这些指令作为操作指南。
:::

# AgentMail 技能

AgentMail 为智能体提供专属邮箱，用于发送邮件、接收回复、完成邮件验证码流程以及处理传入邮件循环。它适用于智能体自身的邮箱，而非用户现有的 IMAP/SMTP 邮箱。

请先使用 `agentmail` CLI 工具。仅在框架要求使用 MCP 工具时才使用 MCP；仅在 CLI 缺少某项必要功能时才使用 REST 接口。

## 适用场景

- 智能体需要拥有属于自己的电子邮件地址。
- 任务涉及邮件验证码流程、回复、主题串、标签或附件处理。
- 智能体需要通过 Webhook 或 WebSocket 接收传入邮件。

## 先决条件

- 能够通过 `terminal` 工具执行命令。
- 已安装 CLI 工具：

```bash
npm install -g agentmail-cli@latest
```

- 导出 API 密钥：

```bash
export AGENTMAIL_API_KEY="am_..."
```

还没有 API 密钥？请参考 [signup.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/signup.md) 进行注册。

## 如何运行

当其他命令或脚本需要获取 ID 时，请使用 `--format json` 参数。

```bash
agentmail inboxes list --format json
```

## 快速参考

- [AgentMail 智能体参考文档](https://agentmail.md)：托管版文档。
- [AgentMail](https://agentmail.to)：产品介绍页面。
- [控制台](https://console.agentmail.to)：API 密钥与账户管理。
- [文档中心](https://docs.agentmail.to)：完整的产品文档。
- [signup.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/signup.md)：自主注册及 OTP 验证流程。
- [core.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/core.md)：收件箱、消息、对话线程、标签与附件相关说明。
- [webhooks.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/webhooks.md)：发送至公共 HTTPS 服务器的事件处理方式。
- [websockets.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/websockets.md)：发送至本地智能体进程的事件处理方式。
- [mcp.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/mcp.md)：MCP 集成指南。

## 操作步骤

1. 安装 `agentmail-cli@latest`，然后运行 `agentmail inboxes list --format json` 进行验证。  
2. 若没有 API 密钥，请按照 [signup.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/signup.md) 的说明完成注册。  
3. 对于收件箱管理、发送邮件、阅读邮件、回复邮件、转发邮件、标记标签、整理主题以及处理附件等操作，可参考 [core.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/core.md)。  
4. 仅在轮询方式无法满足需求时，才使用 [webhooks.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/webhooks.md) 或 [websockets.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/email\agentmail/references/websockets.md)。  

## 常见问题  

- 建议使用 `AGENTMAIL_API_KEY` 而非 `--api-key`。  
- 绝对不要在提示词、日志、URL 或已提交的文件中暴露 `AGENTMAIL_API_KEY`。  
- 在需要重试创建操作时，应使用稳定的 `client_id` 值。  
- 若存在相关数据，建议优先使用 `extracted_text` 或 `extracted_html` 作为输入给大型语言模型。  
- 应对 `message.received` 事件做出响应，而非处理代理自身发送的邮件。  

## 验证方法

```bash
agentmail inboxes list --format json
```
