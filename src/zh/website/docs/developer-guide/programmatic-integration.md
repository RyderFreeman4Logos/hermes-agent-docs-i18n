---
sidebar_position: 8
title: "Programmatic Integration"
description: "Three protocols for driving hermes-agent from external programs: ACP, the TUI gateway JSON-RPC, and the OpenAI-compatible HTTP API"
---

# 程序化集成

Hermes 提供了三种协议，用于从外部程序驱动 Agent 的运行——IDE 插件、自定义 UI、CI 流水线以及嵌入式子 Agent。您可以根据自身的传输方式和使用场景选择合适的方案。

| 协议 | 传输方式 | 最佳适用场景 | 定义文件 |
|------|----------|--------------|----------|
| **ACP** | 基于 stdio 的 JSON-RPC | 已支持 [Agent Client Protocol](https://github.com/zed-industries/agent-client-protocol) 的 IDE 客户端（如 VS Code、Zed、JetBrains 系列 IDE） | `acp_adapter/` |
| **TUI gateway** | 基于 stdio 或 WebSocket 的 JSON-RPC | 需要实现对会话、斜杠命令、审批流程以及流式事件进行精细控制的自定义主机 | `tui_gateway/server.py` |
| **API server** | HTTP + Server-Sent Events | 兼容 OpenAI 的前端界面（如 Open WebUI、LobeChat、LibreChat 等）以及与语言无关的网页客户端 | `gateway/platforms/api_server.py` |

这三种协议均基于相同的 `AIAgent` 核心实现，其差异仅在于数据传输格式以及所提供的功能集。

---

## ACP（Agent Client Protocol）

`hermes acp` 会启动一个基于 stdio 的 JSON-RPC 服务器，该服务器遵循 ACP 协议运行。目前 VS Code（Zed Industries 开发的 ACP 扩展）、Zed 以及所有安装了 ACP 插件的 JetBrains IDE 都在生产环境中使用该协议。

该协议支持的功能包括：会话创建、提示词提交、流式传输 Agent 消息片段、工具调用事件处理、权限请求、会话分叉、取消操作以及身份验证。工具的输出会被转换为 IDE 能识别的 ACP `Diff`/`ToolCall` 内容块。

关于完整的生命周期管理、事件桥接机制以及审批流程的详细信息，请参阅：[ACP 内部实现](./acp-internals)。

```bash
hermes acp                  # serve ACP on stdio
hermes acp --bootstrap      # print install snippet for an ACP-capable IDE
```

## TUI Gateway JSON-RPC

`tui_gateway/server.py` 是 Ink TUI（`hermes --tui`）与嵌入式控制面板 PTY 桥接组件之间通信所使用的协议。任何外部主机均可通过标准输入输出（或通过 `tui_gateway/ws.py` 使用 WebSocket）来使用同一协议进行通信。

### 方法列表（已选中）

```
prompt.submit           prompt.background       session.steer
session.create          session.list            session.active_list
session.activate        session.close           session.interrupt
session.history         session.compress        session.branch
session.title           session.usage           session.status
clarify.respond         sudo.respond            secret.respond
approval.respond        config.set / config.get commands.catalog
command.resolve         command.dispatch        cli.exec
reload.mcp              reload.env              process.stop
delegation.status       subagent.interrupt      spawn_tree.save / list / load
terminal.resize         clipboard.paste         image.attach
```

`session.active_list`、`session.activate` 和 `session.close` 是 TUI 会话切换器所使用的进程级实时会话控制函数。若需查找已保存的对话记录，请使用 `session.list` / `/resume`；这些函数仅适用于当前在 TUI 网关进程中打开的会话。

### 流回的事件

包括 `message.delta`、`message.complete`、`tool.start`、`tool.progress`、`tool.complete`、`approval.request`、`clarify.request`、`sudo.request`、`sudo.expire`、`secret.request`、`secret.expire`、`gateway.ready`，以及会话生命周期相关事件和错误事件。过期事件会携带原始的 `{ request_id }`；外部主机只需清除对应的待处理提示即可。

### Pi 风格的 RPC 映射

Pi-mono RPC 规范中的每个命令（[问题 #360](https://github.com/NousResearch/hermes-agent/issues/360)）在 TUI 网关中都有对应的实现：

| Pi 命令 | Hermes 对应函数 |
|----------|-------------------|
| `prompt` | `prompt.submit`（或 ACP 的 `session/prompt`） |
| `steer` | `session.steer` |
| `follow_up` | 在当前轮次结束后排队执行的 `prompt.submit` |
| `abort` | `session.interrupt` |
| `set_model` | 对于 `/model <provider:model>` 命令，使用 `command.dispatch`（在会话进行中且效果持久） |
| `compact` | `session.compress` |
| `get_state` | `session.status` |
| `get_messages` | `session.history` |
| `switch_session` | `session.resume` |
| `fork` | `session.branch` |
| `ui_request` / `ui_response` | `clarify.respond` / `sudo.respond` / `secret.respond` / `approval.respond` |

---

## 兼容 OpenAI 的 API 服务器

`gateway/platforms/api_server.py` 可通过 HTTP 提供 hermes 接口，适用于任何已支持 OpenAI 格式的客户端。当您需要网页前端、基于 curl 的 CI 运行工具或非 Python 客户端时，该功能非常有用。

接口端点：

```
POST /v1/chat/completions        OpenAI Chat Completions (streaming via SSE)
POST /v1/responses               OpenAI Responses API (stateful)
POST /v1/runs                    Start a run, returns run_id (202)
GET  /v1/runs/{id}               Run status
GET  /v1/runs/{id}/events        SSE stream of lifecycle events
POST /v1/runs/{id}/approval      Resolve a pending approval
POST /v1/runs/{id}/stop          Interrupt the run
GET  /v1/capabilities            Machine-readable feature flags
GET  /v1/models                  Lists hermes-agent
GET  /health, /health/detailed
```

设置、请求头（`X-Hermes-Session-Id`、`X-Hermes-Session-Key`）以及前端集成方式：[API服务器](../user-guide/features/api-server)。

---

## 我该选择哪种方案？

- **您正在开发IDE插件，且该IDE已支持ACP协议** → 选择ACP方案。无需在IDE端进行任何协议处理。
- **您正在开发自定义桌面端/网页端/TUI主机，并希望使用Hermes的所有功能**（斜杠命令、审批流程、信息澄清、多智能体协作、会话分支等）→ 选择TUI网关JSON-RPC方案。
- **您需要兼容OpenAI的前端、与语言无关的HTTP客户端，或基于curl的自动化工具** → 选择API服务器方案。
- **您希望以Python原进程方式嵌入Hermes，而不使用子进程** → 直接导入`run_agent.AIAgent`模块。详情请参阅[智能体循环机制](./agent-loop)。

---

## 模型热切换

在会话进行中切换模型在所有接口上均支持——其底层实现即为 `/model` 斜杠命令。

- **CLI/TUI**：使用 `/model claude-sonnet-4` 或 `/model openrouter:anthropic/claude-sonnet-4.6`
- **TUI网关RPC**：通过 `command.dispatch` 方法传递 `{"command": "/model claude-sonnet-4"}` 参数
- **ACP**：IDE会将斜杠命令作为提示语发送，由智能体负责处理
- **API服务器**：在请求体中添加 `model` 字段，或设置 `X-Hermes-Model` 头部参数

系统已内置基于提供方类型的自动适配机制——相同的模型名称会自动选择适合当前使用提供方的格式。详情可参考 `hermes_cli/model_switch.py` 文件。

---

## 关于 `--mode rpc` 的说明

Hermes 并不提供 `--mode rpc` 参数。上述三种协议已覆盖所有常见使用场景：ACP适用于IDE协议客户端，TUI网关适用于标准输入输出JSON-RPC主机，API服务器则适用于HTTP接口。如果您发现现有方案无法满足特定需求，请针对您正在开发的实际应用提交问题报告。
