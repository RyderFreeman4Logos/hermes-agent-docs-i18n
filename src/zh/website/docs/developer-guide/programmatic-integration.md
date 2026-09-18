---
sidebar_position: 8
title: "Programmatic Integration"
description: "Three protocols for driving hermes-agent from external programs: ACP, the TUI gateway JSON-RPC, and the OpenAI-compatible HTTP API"
---

# 程序化集成

Hermes 提供了三种协议，用于从外部程序驱动 Agent 的运行——IDE 插件、自定义 UI、CI 流水线以及嵌入式子 Agent。您可以根据自身的传输方式与使用场景选择合适的方案。

| 协议 | 传输方式 | 最佳适用场景 | 定义文件 |
|------|----------|--------------|----------|
| **ACP** | 基于 stdio 的 JSON-RPC | 已支持 [Agent Client Protocol](https://github.com/zed-industries/agent-client-protocol) 的 IDE 客户端（如 VS Code、Zed、JetBrains 系列 IDE） | `acp_adapter/` |
| **TUI gateway** | 基于 stdio 或 WebSocket 的 JSON-RPC | 需要实现对会话、斜杠命令、审批流程及流式事件进行精细控制的自定义主机 | `tui_gateway/server.py` |
| **API server** | HTTP + Server-Sent Events | 兼容 OpenAI 的前端界面（如 Open WebUI、LobeChat、LibreChat 等）以及与语言无关的网页客户端 | `gateway/platforms/api_server.py` |

这三种协议均基于相同的 `AIAgent` 核心实现，仅在于数据传输格式及所提供的功能集有所不同。

---

## ACP（Agent Client Protocol）

`hermes acp` 会启动一个基于 stdio 的 ACP 协议 JSON-RPC 服务器。目前 VS Code（Zed Industries 开发的 ACP 扩展）、Zed 以及所有安装了 ACP 插件的 JetBrains IDE 都在实际生产环境中使用该协议。

该协议支持的功能包括：会话创建、提示词提交、Agent 消息分块流式传输、工具调用事件处理、权限请求、会话复制、取消操作以及身份验证。工具的输出会被转换为 IDE 能识别的 ACP `Diff`/`ToolCall` 格式的内容块。

全生命周期管理、事件桥接以及审批流程相关内容：[ACP 内部机制](./acp-internals)。

```bash
hermes acp                  # serve ACP on stdio
hermes acp --check          # verify ACP dependencies and adapter imports
hermes acp --setup          # interactive provider/model setup for ACP terminal auth
```

## TUI Gateway JSON-RPC

`tui_gateway/server.py` 是 Ink TUI（`hermes --tui`）与嵌入式控制面板 PTY 桥接组件之间通信所使用的协议。任何外部主机均可通过标准输入接口（或通过 `tui_gateway/ws.py` 使用 WebSocket）来使用同一协议进行通信。

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
delegation.status       subagent.interrupt      subagent.steer
spawn_tree.save / list / load
terminal.resize         clipboard.paste         image.attach
```

`session.active_list`、`session.activate` 和 `session.close` 是 TUI 会话切换器所使用的进程级实时会话控制函数。若需查找已保存的对话记录，请使用 `session.list` / `/resume`；这些实时会话函数仅适用于当前在 TUI 网关进程中打开的会话。

在同一个已认证的网关内，恢复或激活实时会话会新增一个事件订阅者，而非替换原有的连接。流式事件和终端事件会发送给所有已连接的客户端；即使某个客户端断开连接，其他客户端仍在查看的会话仍会继续。现有的提交独占机制以及配置好的忙碌输入策略依然有效。已连接的客户端可以控制会话中的子代理；而浏览器控制器的功能仍需依赖注册该控制器的连接。此机制既不允许独立的网关进程写入同一个会话，也不意味着在主进程重启后仍能保持提示信息的连续性。

### 对 `prompt.submit` 操作的历史记录进行回退

回退/编辑/重新生成操作，指的是在执行新的对话轮次之前，先删除部分已存储的对话记录的 `prompt.submit` 操作。由于这种写入行为会破坏会话中持久化存储的数据行，因此只有当客户端明确表达该意图时，网关才会接受此类操作。

| 参数 | 含义 |
|-----------|---------|
| `truncate_before_user_ordinal` | 需要截断的用户轮次对应的零基索引。从该轮次之后的所有内容都将被丢弃。仅用于显示的时间轴行（`display_kind` 类型）不会被计入。该参数必须为真实整数，若为 JSON 布尔值则会被拒绝，返回错误码 `4004`。 |
| `truncate_before_row_id` | 需要截断的目标用户轮次对应的 SQLite 行 ID（即 `messages.id` / `row_id`）。这是更推荐的稳定标识方式。当同时提供索引和行 ID 时，网关会验证二者是否一致，若不一致则返回错误码 `4030`。未知或过期的行 ID 也会被拒绝，返回错误码 `4018`——此时不会尝试回退到索引值。 |
| `confirm_truncate` | 每当发送索引、消息 ID 或行 ID 时均需提供此参数。用于确认此次操作确实为回放操作，而非偶然包含多余参数的普通发送请求。若未指定目标就发送该参数，则会被拒绝，返回错误码 `4004`。 |
| `confirm_empty_truncate` | 当截断操作会导致转录内容变为空（即索引值为 `0`）时，此参数也是必需的。 |

若截断参数缺少 `confirm_truncate`，则会被拒绝，返回错误码 `4004` 或 `4029`，且不会执行任何截断操作。实现回放功能的服务器必须在用户提出请求时立即设置该标志，且绝不能在普通发送操作中保留截断参数的状态。建议优先使用 `truncate_before_row_id`（从恢复功能中的 `row_id` / `_row_id` 获取），仅在暂时没有稳定标识时可将索引值作为兼容旧版本或基于乐观行号的备用方案。

当针对持久化会话成功提交截断操作后，`prompt.submit` 的返回结果中还会包含 `survivor_user_row_ids` —— 即按可见用户顺序排列的、保留下来的用户轮次在重写后的新行 ID。由于重写过程会将原有的前缀重新作为新行插入，因此主机在回退操作之前缓存的每个行 ID 在之后都会失效；必须重新绑定此列表中的缓存 ID（若某个条目为 `null`，则表示该轮次没有持久化 ID —— 应直接丢弃该缓存值），否则下次针对更早保留下来的轮次进行回退操作时将会收到 `4018` 错误。

### 流回的事件

包括 `message.delta`、`message.complete`、`tool.start`、`tool.progress`、`tool.complete`、`approval.request`、`clarify.request`、`sudo.request`、`sudo.expire`、`secret.request`、`secret.expire`、`gateway.ready`，以及会话生命周期相关的事件和错误事件。那些表示过期时间的事件会携带原始的 `{ request_id }`；外部主机只需清除对应的待处理提示即可。

### Pi 风格的 RPC 映射

Pi-mono RPC 规范中的每条命令（[问题 #360](https://github.com/NousResearch/hermes-agent/issues/360)）都对应着一个 TUI-gateway 版本：

| Pi 命令 | Hermes 对应功能 |
|----------|-------------------|
| `prompt` | `prompt.submit`（或 ACP 的 `session/prompt`） |
| `steer` | `session.steer` |
| `follow_up` | 在当前轮次结束后排队等待的 `prompt.submit` 请求 |
| `abort` | `session.interrupt` |
| `set_model` | 用于 `/model <provider:model>` 的 `command.dispatch`（可在会话进行中持续使用） |
| `compact` | `session.compress` |
| `get_state` | `session.status` |
| `get_messages` | `session.history` |
| `switch_session` | `session.resume` |
| `fork` | `session.branch` |
| `ui_request` / `ui_response` | `clarify.respond` / `sudo.respond` / `secret.respond` / `approval.respond` |

---

## 兼容 OpenAI 的 API 服务器

`gateway/platforms/api_server.py` 为所有已支持 OpenAI 格式的客户端提供基于 HTTP 的 Hermes 接口。当您需要网页前端、基于 curl 的 CI 运行工具或非 Python 客户端时，该功能非常实用。

接口端点：

```
POST /v1/chat/completions        OpenAI Chat Completions (streaming via SSE)
POST /v1/responses               OpenAI Responses API (stateful)
POST /v1/runs                    Start a run, returns run_id (202)
GET  /v1/runs/{id}               Run status
GET  /v1/runs/{id}/events        SSE stream of lifecycle events
POST /v1/runs/{id}/approval      Resolve a pending approval
POST /v1/runs/{id}/steer         Inject mid-run guidance at the next tool boundary
POST /v1/runs/{id}/stop          Interrupt the run
GET  /v1/capabilities            Machine-readable feature flags
POST /v1/browser-control/register Register a browser controller
GET  /v1/browser-control/ws       Browser-controller WebSocket
GET  /v1/models                  Lists hermes-agent
GET  /api/model/options          Provider-aware picker inventory
GET  /health, /health/detailed
```

设置、请求头（`X-Hermes-Session-Id`、`X-Hermes-Session-Key`）以及前端连接方式：请参考[API服务器](../user-guide/features/api-server)。

浏览器扩展可以选择启用默认处于禁用状态的控制器协议，从而控制开启Hermes对话的特定浏览器会话。API与控制面板均使用同一个基于主体的代理，且具备相同的显式能力白名单；详情请参阅[浏览器扩展控制](../user-guide/features/api-server#browser-extension-control)。

### 模型目录展示方式

为确保与OpenAI的兼容性，`GET /v1/models`接口的设计极为简洁：它仅提供前端所期望的兼容性端点，而非完整的Hermes提供商/模型选择器目录。

如果外部控制平面需要Hermes筛选后的提供商列表、各模型的定价信息或能力提示，可使用以下经过身份验证的选择器接口：

- API服务器REST接口：使用API服务器的承载密钥发送`GET /api/model/options`请求；
- 控制面板后端REST接口：使用`X-Hermes-Session-Token`发送`GET /api/model/options`请求；
- TUI网关RPC接口：发送`model.options`请求。

这些接口均采用相同的负载构建机制以及自定义提供商探测策略：

- 正常加载模式：仅探测当前已配置的自定义提供商，避免离线保存的端点导致选择器卡住；
- 显式刷新模式（`refresh=1`或`refresh: true`）：清除提供商-模型缓存，并探测所有已保存的自定义提供商，从而让目录内容完全更新。

为确保与OpenAI客户端兼容，请使用`/v1/models`接口；而在构建支持Hermes功能的模型选择器时，则应使用`/api/model/options`或`model.options`接口。

`POST /v1/runs/{id}/steer` 是 Hermes 接口 `/steer` 的 HTTP 对应版本：它不会创建新的用户轮次，也不会立即修改正在处理的助手输出。相反，该文本会被追加到当前的运行任务中，并在下一个工具调用边界之后显示给智能体，从而使其能够在不中断当前工具调用流程的情况下调整方向。

只有当运行状态为 `running` 时，才会接受 `/v1/runs/{id}/steer` 的请求。处于排队中、审批暂停、停止中、已取消、失败或已完成状态的运行任务都会返回 `409 run_not_accepting_steer` 错误码，即便在协同关闭过程中服务器仍保留着相关的智能体内部引用。

返回 `200` 状态码（并触发 `run.steered` 事件）仅表示文本已被**加入队列**，并不代表智能体已将其处理。如果在该文本被发送后智能体已经给出了最终回复，且之后没有工具调用边界可供传递该文本，那么这些未送达的文本将会作为 `pending_steer` 状态显示在终端的 `run.completed` 事件及运行状态中，这样客户端就可以将其作为下一次用户轮次重新播放，而不会丢失这些内容。

---

## 我应该使用哪一个？

- **您正在开发 IDE 插件，且该 IDE 已支持 ACP 协议** → 直接使用 ACP 协议，无需在 IDE 端进行任何协议处理。  
- **您正在构建自定义桌面端/网页端/TUI 主机，并希望启用 Hermes 的所有功能**（如斜杠命令、审批流程、信息澄清、多智能体协作、会话分支等）→ 使用 TUI gateway 的 JSON-RPC 协议。  
- **您需要兼容 OpenAI 的前端界面、与语言无关的 HTTP 客户端，或基于 curl 的自动化工具** → 使用 API 服务器。  
- **您希望以 Python 内嵌方式运行智能体而无需启动子进程** → 直接导入 `run_agent.AIAgent`。详情请参阅 [Agent Loop](./agent-loop)。

---

## 模型热切换

在会话进行中切换模型功能在所有支持场景下均可用——其底层实现即为 `/model` 斜杠命令。

- **CLI/TUI**：使用 `/model claude-sonnet-4` 或 `/model openrouter:anthropic/claude-sonnet-4.6`  
- **TUI gateway RPC**：通过 `command.dispatch` 方法传递 `{"command": "/model claude-sonnet-4"}`  
- **ACP**：IDE 会将斜杠命令作为提示发送给智能体，由其负责处理  
- **API 服务器**：需在请求体中添加 `model` 字段  

系统已内置基于提供者类型的自动适配机制——相同的模型名称会自动选择适合当前使用提供者的格式。详情可参阅 `hermes_cli/model_switch.py`。

---

## 关于 `--mode rpc` 的说明

Hermes 并不提供 `--mode rpc` 参数。上述三种协议已能够覆盖所有常见使用场景：ACP 适用于 IDE 协议客户端，TUI gateway 适用于基于标准输入输出流的 JSON-RPC 主机，而 API 服务器则适用于 HTTP 接口。如果您发现现有方案存在真正无法填补的空白，请针对您正在开发的特定应用提交问题报告。
