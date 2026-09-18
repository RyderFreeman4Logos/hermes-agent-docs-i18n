---
sidebar_position: 14
title: "API Server"
description: "Expose hermes-agent as an OpenAI-compatible API for any frontend"
---

# API服务器

API服务器将hermes-agent作为兼容OpenAI协议的HTTP接口对外提供。任何支持OpenAI格式的前端应用——如Open WebUI、LobeChat、LibreChat、NextChat、ChatBox以及数百种其他应用——均可连接到hermes-agent并将其作为后端使用。

您的智能体可利用其完整的工具集（终端操作、文件处理、网络搜索、内存功能、技能模块）来处理请求，并返回最终响应。在流式交互模式下，工具处理进度会以内联形式显示，便于前端实时了解智能体的当前操作状态。

:::提示 一个后端即可同时支持模型与工具
若要使Hermes真正发挥作用，API服务器需要配置相应的提供者及工具后端。通过[Nous Portal](/user-guide/features/tool-gateway)订阅服务即可同时满足这两项需求——300多种模型可通过工具网关实现调用，同时还能支持网页、图像、文本转语音及浏览器相关功能。在启动API服务器及Open WebUI、LobeChat等前端应用之前，只需运行一次`hermes setup --portal`命令，即可获得具备完整工具功能的后端。
:::

## 快速入门

### 1. 启用API服务器

在`~/.hermes/.env`文件中添加以下内容：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=change-me-local-dev
# Optional: only if a browser must call Hermes directly
# API_SERVER_CORS_ORIGINS=http://localhost:3000
```

### 2. 启动网关

```bash
hermes gateway
```

您将看到：

```
[API Server] API server listening on http://127.0.0.1:8642
```

### 3. 连接前端应用

将任何兼容 OpenAI 的客户端指向 `http://localhost:8642/v1` 即可：

```bash
# Test with curl
curl http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer change-me-local-dev" \
  -H "Content-Type: application/json" \
  -d '{"model": "hermes-agent", "messages": [{"role": "user", "content": "Hello!"}]}'
```

或者，您也可以连接 Open WebUI、LobeChat 或其他任何前端界面——详细操作步骤请参阅 [Open WebUI 集成指南](/user-guide/messaging/open-webui)。

## 接口端点

### POST /v1/chat/completions

采用标准的 OpenAI Chat Completions 格式。该接口为无状态设计，每次请求都会通过 `messages` 数组包含完整的对话内容。

**请求示例：**
```json
{
  "model": "hermes-agent",
  "messages": [
    {"role": "system", "content": "You are a Python expert."},
    {"role": "user", "content": "Write a fibonacci function"}
  ],
  "stream": false
}
```

**响应：**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "hermes-agent",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "Here's a fibonacci function..."},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 50, "completion_tokens": 200, "total_tokens": 250}
}
```

**内联图片输入：** 用户消息可以将 `content` 以包含 `text` 和 `image_url` 元素的数组形式发送。系统同时支持远程的 `http(s)` URL以及 `data:image/...` 格式的URL。

```json
{
  "model": "hermes-agent",
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "What is in this image?"},
        {"type": "image_url", "image_url": {"url": "https://example.com/cat.png", "detail": "high"}}
      ]
    }
  ]
}
```

上传的文件（通过 `file` / `input_file` / `file_id` 参数传递）以及非图片类型的 `data:` URL 都会返回 `400 unsupported_content_type` 错误。

**流式响应**（设置 `"stream": true`）：以服务器推送事件（SSE）的形式逐条返回响应数据。在**聊天补全**场景中，流式响应会使用标准的 `chat.completion.chunk` 事件，同时还会添加 Hermes 自定义的 `hermes.tool.progress` 事件，以便更好地展示工具启动状态。而在**常规响应**场景中，则会使用 OpenAI 定义的响应事件类型，如 `response.created`、`response.output_text.delta`、`response.output_item.added`、`response.output_item.done` 和 `response.completed`。

**流式响应中的工具进度显示**：
- **聊天补全**：Hermes 会发送 `event: hermes.tool.progress` 事件来实时显示工具的启动状态，而不会干扰已保存的助手对话内容。
- **常规响应**：在 SSE 流式响应过程中，Hermes 会发送符合规范定义的 `function_call` 和 `function_call_output` 事件，从而使客户端能够实时渲染结构化的工具界面。

### POST /v1/responses

采用 OpenAI Responses API 格式。通过 `previous_response_id` 参数支持服务器端维护对话状态——服务器会存储完整的对话历史记录（包括工具调用及其结果），从而无需客户端自行管理即可保留多轮对话的上下文。

**请求格式：**
```json
{
  "model": "hermes-agent",
  "input": "What files are in my project?",
  "instructions": "You are a helpful coding assistant.",
  "store": true
}
```

**响应：**
```json
{
  "id": "resp_abc123",
  "object": "response",
  "status": "completed",
  "model": "hermes-agent",
  "output": [
    {"type": "function_call", "status": "completed", "name": "terminal", "arguments": "{\"command\": \"ls\"}", "call_id": "call_1"},
    {"type": "function_call_output", "status": "completed", "call_id": "call_1", "output": "README.md src/ tests/"},
    {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Your project has..."}]}
  ],
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

`output` 数组中的工具调用早已由 Hermes Agent 在服务器端执行完毕——为了在结构化的工具界面中显示，这些调用会被标记为 `"status": "completed"` 的状态，而绝不会作为需要客户端执行的待处理调用呈现。

**内嵌图片输入：** `input[].content` 可以包含 `input_text` 和 `input_image` 两部分。该字段支持远程 URL 以及 `data:image/...` 格式的 URL：

```json
{
  "model": "hermes-agent",
  "input": [
    {
      "role": "user",
      "content": [
        {"type": "input_text", "text": "Describe this screenshot."},
        {"type": "input_image", "image_url": "data:image/png;base64,iVBORw0K..."}
      ]
    }
  ]
}
```

上传的文件（`input_file` / `file_id`）以及非图片类型的 `data:` URL 都会返回 `400 unsupported_content_type` 错误。

#### 基于 previous_response_id 的多轮对话

通过串联响应来保留各轮对话中的完整上下文（包括工具调用信息）：

```json
{
  "input": "Now show me the README",
  "previous_response_id": "resp_abc123"
}
```

服务器会根据存储的响应链重新构建完整的对话内容——所有之前的工具调用及其结果都会被保留下来。由于这些请求属于连续调用，因此它们会共享同一个会话，这样一来，多轮对话在控制面板和会话历史记录中就会显示为单个条目。

#### 命名对话

建议使用 `conversation` 参数，而非通过跟踪响应 ID 来实现。

```json
{"input": "Hello", "conversation": "my-project"}
{"input": "What's in src/?", "conversation": "my-project"}
{"input": "Run the tests", "conversation": "my-project"}
```

服务器会自动跳转至该对话中的最新回复，功能类似网关会话中的 `/title` 命令。

### GET /v1/responses/\{id\}

根据 ID 获取之前存储的回复。

### DELETE /v1/responses/\{id\}

删除已存储的回复。

### GET /v1/models

列出可作为模型的智能体。显示的模型名称默认为 [个人资料](/user-guide/profiles)中的名称（默认个人资料则为 `hermes-agent`）。大多数前端在搜索模型时都需要此接口。

`/v1/models` 是专为兼容 OpenAI 而设计的简化接口。它**不会**列出 Hermes 能够路由到的所有已认证的提供商/模型组合，也不会提供价格信息或功能详情。

### GET /api/model/options

支持 Hermes 的客户端可以获取与控制台和 TUI 中相同的精选提供商/模型列表。该接口使用 API 服务器常规的承载式身份验证机制，返回的内容包括提供商信息、模型功能提示以及那些不在 OpenAI 兼容的 `/v1/models` 响应中的价格元数据：

```bash
curl \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  "http://127.0.0.1:8642/api/model/options"
```

该数据载荷与控制台“模型”页面以及 TUI 的 `model.options` RPC 所使用的格式完全一致。它返回经过身份验证的提供者信息、精心筛选后的模型列表、各模型的定价详情，以及模型功能的相关提示。

对于自定义提供者而言，常规加载方式会被刻意设置得较为保守：Hermes 仅会检测**当前选中**的自定义端点，因此过时或离线的保存端点不会影响模型选择器的工作。而通过显式刷新操作，则会启动全面检测，并清除提供者模型缓存。

```bash
curl \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  "http://127.0.0.1:8642/api/model/options?refresh=1"
```

当兼容 OpenAI 的客户端仅需在聊天或回复请求中返回模型名称时，可使用 `/v1/models`。而对于已通过身份验证的界面，若需要更丰富的、专为 Hermes 设计的模型选择器元数据，则应使用 `/api/model/options`。

### GET /v1/capabilities

该接口会为外部界面、调度器以及插件桥接工具提供机器可读的描述，用以说明 API 服务器的稳定功能范围。

```json
{
  "object": "hermes.api_server.capabilities",
  "platform": "hermes-agent",
  "model": "hermes-agent",
  "auth": {"type": "bearer", "required": true},
  "features": {
    "chat_completions": true,
    "responses_api": true,
    "run_submission": true,
    "run_status": true,
    "run_events_sse": true,
    "run_stop": true
  }
}
```

在集成控制面板、浏览器用户界面或控制平面时，可使用此接口。通过该接口，相关组件无需依赖 Hermes 的内部 Python 实现，即可自行判断当前运行的 Hermes 版本是否支持任务执行、流式处理、任务取消以及会话连续性功能。

## 浏览器扩展控制

Hermes 能够通过经过身份验证的扩展程序来路由浏览器工具，从而管控与当前 Hermes 会话关联的浏览器会话。该功能默认处于禁用状态，如需启用，请将 `browser.extension_control.enabled` 的值设置为 `true`：

```yaml
browser:
  extension_control:
    enabled: true
```

本地 API 路径同样需要 API 服务器的承载密钥。控制器仅能针对已存在的服务器会话进行注册。Hermes 会从经过身份验证的服务器状态中获取控制器主体信息，而客户端提供的 `principal_id` 则会被忽略。

可通过 `GET /v1/capabilities` 来查询实时合约信息。`browser_extension_control` 对象会说明该功能是否已启用、协议版本、传输方式名称，以及具体的功能允许列表：

```text
controller.noop
browser_back
browser_click
browser_navigate
browser_press
browser_screenshot
browser_scroll
browser_snapshot
browser_tab_activate
browser_tabs
browser_type
```

不在该列表中的请求功能将被过滤掉。原始 CDP 数据、任意脚本执行、控制台访问、文件上传、图像提取以及视觉分析等功能均不属于控制器协议的支持范围。

当某个请求没有绑定的控制器标识，或者相关功能被禁用时，Hermes 会保留原有的浏览器后端。一旦网关为该请求绑定具体的控制器主体和传输协议，该通道即具有权威性：那些缺失、不明确、断开连接或无法正常工作的控制器将会直接拒绝请求，而不会悄悄切换到其他本地/云端浏览器。选定确切的控制器后，其返回的结果或错误信息即具有权威性，Hermes 永不会再通过其他后端重复执行同一操作。

### 本地 API 注册

1. 发送经过身份验证的 `POST /v1/browser-control/register` 请求，需包含 `protocol_version`、`session_id`、`controller_id`、`browser_profile_id` 以及所需的 `capabilities` 参数。
2. Hermes 会返回一个仅可使用一次的访问令牌，其有效时间为 30 秒，同时还会限定控制器的作用范围为服务器端支持的那些功能。
3. 打开 `GET /v1/browser-control/ws` 请求，需同时启用以下两种 WebSocket 子协议：`hermes-browser-control-v1` 和 `hermes-browser-control-ticket.<ticket>`。

该访问令牌绝不能通过查询字符串传递。任何未知、已过期、被重复使用或格式错误的令牌都将在 WebSocket 升级阶段被拒绝。

### 控制器帧结构

Hermes会发送包含`command_id`、`action`、不可变的`arguments`、浏览器/控制器标识以及原始`tool_call_id`的`browser.controller.command`数据帧。控制器则会回复`browser.controller.result`、相同的`command_id`、一个明确的布尔值`ok`，以及`result`或`error`状态。当发生取消操作或超时时，会发送`browser.controller.cancel`信号；而延迟到达的结果将被忽略。

如果出现意外的连接丢失，系统会将控制器标记为离线状态，并保留正在处理中的任务，直到每个命令达到其预设的截止时间。使用相同的主体、配置文件、会话、控制器标识、浏览器配置文件以及传输标识重新建立连接后，虽然可以恢复数据传输，但在清除所有已延迟的取消请求之前，不会接受新的任务。在重新连接时，协商确定的功能参数可能会发生变化，但这些参数并不属于身份识别字段。如果在同一经过身份验证的会话通道中使用不同的控制器标识或浏览器配置文件，则属于强制替换场景：在新的控制器能够处理请求之前，原有的待处理任务将会被取消。如需主动执行强制断开操作，可在已通过身份验证的控制器传输通道上发送`browser.controller.detach`指令，这将立即取消所有待处理任务。而仅仅关闭套接字则被视为可恢复的连接中断。

经过身份验证的仪表板传输方式会通过其 Gateway RPC/事件通道，提供相同的注册、结果、心跳、能力以及所有权相关机制。在这两种传输方式中，要完成选择，必须在主体、配置文件、会话、控制器、浏览器配置文件、传输类型以及能力这些参数上实现唯一且精确的匹配。一旦选定某个控制器，即便该控制器出现故障，系统也会直接放弃该尝试，而不会通过其他浏览器后端重新发起请求。

## 每次请求的模型选择机制

经过身份验证的客户端可以通过发送以下参数，来覆盖 Hermes 的默认模型选择逻辑：

- `model` — 当前轮次所需的目标模型编号
- `provider` — 用于为当前轮次获取凭证及运行时环境的 Hermes 提供商标识
- `model_options` — 与当前请求相关的推理规则或服务层控制参数

上述请求参数同样适用于以下接口：

- `POST /v1/chat/completions`
- `POST /v1/responses`
- `POST /v1/runs`
- `POST /api/sessions/{session_id}/chat`
- `POST /api/sessions/{session_id}/chat/stream`

各参数的优先级是明确固定的：

1. 若某个会话已设置了模型，则优先采用该会话中的 `/model` 覆盖值
2. 当请求中的 `model` 参数对应到已配置的路由别名时，优先使用静态的 `gateway.platforms.api_server.model_routes` 映射关系
3. 若没有匹配到任何路由别名，则直接使用请求中指定的 `model`/`provider` 参数
4. 最后才采用全局网关配置或环境默认值
无论最终选择哪种模型或提供方，`model_options` 都会保持请求级作用域。如果某个请求指定的 `provider` 与已配置的 `model_routes` 别名冲突，Hermes 会直接以 `400` 错误码拒绝该请求，而不会默默地用其他提供方的配置来替代。

在兼容 OpenAI 的接口中，显式指定 `model` 值为可选功能。常见的 OpenAI 客户端通常会直接硬编码模型名称（如 `gpt-4o` 等），现有的部署方案也依赖这些默认值以便回退到网关的默认设置。因此，在发送 `POST /v1/chat/completions` 和 `POST /v1/responses` 请求时，若未同时指定 `provider`，则对应的 `model` 值将被忽略，除非您主动启用该功能。

```yaml
gateway:
  platforms:
    api_server:
      direct_model_requests: true
```

那些明确指定了 `provider` 参数的请求，以及使用 Hermes 原生 `/v1/runs` 和会话聊天端点的请求，无论该标志如何设置，都会始终使用所指定的模型。

示例：

```json
{
  "model": "MiniMax-M3",
  "provider": "minimax",
  "model_options": {
    "reasoning_effort": "high",
    "service_tier": "priority"
  },
  "messages": [
    {"role": "user", "content": "Summarize the repo status."}
  ]
}
```

### GET /health

用于健康检查，返回 `{"status": "ok"}`。对于需要 `/v1/` 前缀的 OpenAI 兼容客户端，也可通过 **GET /v1/health** 访问该接口。

### GET /health/detailed

针对监控平面和控制平面进行的身份验证后的就绪状态检查。它会报告当前激活配置文件的配置信息、状态数据库、已配置模型、磁盘空间、网关/平台状态、正在运行的 API 任务、待完成的进程以及正在处理的委托任务等的就绪状态。响应中仅提供状态信息和数量统计，不会暴露配置值、凭证、路径、命令、队列负载或原始错误信息。

公开的 `/health` 接口仍可作为简单的存活检测工具，但不会执行就绪状态检查。即便检测结果为未就绪，也会返回 HTTP 200 状态码；此时需查看顶层的 `status` 和 `readiness.checks` 字段。

## Runs API（适合流式处理的替代方案）

除了 `/v1/chat/completions` 和 `/v1/responses` 接口外，服务器还提供了一个 **runs** API，适用于需要长期会话的场景——客户端可通过该接口订阅进度事件，而无需自行管理数据流处理过程。

### POST /v1/runs

用于创建新的智能体运行任务。返回一个 `run_id`，可用于订阅相关的进度事件。

```json
{
  "run_id": "run_abc123",
  "status": "started"
}
```

该接口可接收一个简单的 `input` 字符串，以及可选的 `session_id`、`instructions`、`conversation_history` 或 `previous_response_id` 参数。当提供了 `session_id` 时，Hermes 会将其显示在运行状态中，以便外部用户界面能够将各次运行与自身的对话 ID 对应起来。

为确保任务可以安全地重试创建，需在请求中添加 `Idempotency-Key` 请求头（内容为1–255个可见的ASCII字符）。Hermes会在开始处理任务前永久保留该密钥。若再次发起相同请求，系统会通过HTTP 202状态码返回原有的 `run_id`，并标记 `Idempotency-Replayed: true`，这一机制在网关重启后、任务完成、失败或被取消时依然有效。若使用相同的密钥但发送不同的JSON数据，则会返回带有 `idempotency_key_conflict` 错误码的HTTP 409响应。这些密钥会根据经过身份验证的API配置文件/凭据进行隔离，并在最后一次状态更新后的24小时内保留；客户端应使用唯一且难以被猜测的密钥，绝不可将其用于无关操作。未包含该请求头的请求将遵循旧有机制，始终创建新的运行任务。

当 `session_id` 指定了一个现有的Hermes会话，且未明确提供 `conversation_history` 或 `previous_response_id` 时，系统会加载该会话中当前正在使用的对话记录。会话轮次锁定机制可防止多个操作同时写入数据，并在出现竞争情况时会自动刷新对话记录。

### GET /v1/runs/\{run_id\}

用于轮询当前任务的运行状态。这对于那些无需保持SSE连接即可获取状态的后台面板，或需要在页面跳转后重新连接的用户界面来说非常有用。

```json
{
  "object": "hermes.run",
  "run_id": "run_abc123",
  "status": "completed",
  "session_id": "space-session",
  "model": "hermes-agent",
  "output": "Done.",
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

在达到终端状态（`completed`、`failed` 或 `cancelled`）后，系统仍会短暂保留相关状态，以便用于轮询及界面同步。

### GET /v1/runs/\{run_id\}/events

该接口通过 Server-Sent Events 流式传输任务执行过程中的工具调用进度、令牌变化量以及生命周期事件。它专为那些希望在不丢失状态的情况下进行连接/断开操作的仪表板应用和复杂客户端设计。

当智能体将任务委派给后台子智能体时，该流还会包含 `subagent.start` 和 `subagent.complete` 等生命周期事件，从而使客户端能够实时了解委派结果——包括超时和失败情况——而无需在子智能体工作时等待沉默的响应。`subagent.complete` 事件中会包含子智能体的状态、执行摘要、耗时、令牌/成本数据、用于关联的 `child_session_id`，以及其所属于批次的 `delegation_id`（以便区分并发或嵌套的任务）；文本字段在离开处理流程前会经过强制的机密信息遮蔽处理。针对单个工具的子任务事件（如 `subagent.tool`、进度更新）则**不会**被转发——因为这些属于高频率的界面干扰信息，如需详细记录可查看每个子任务的实时转录文件。只要父流处于开启状态，这些事件就会持续发送；即便在任务后期才断开连接，已完成的任务的 SSE 流也不会重新打开，其终端状态也不会发生改变。

#### 独立的结果与会话历史记录

在后台委托模式下，需要通过某种方式读取服务器端的会话历史记录：既可以在“聊天补全”请求中明确标注 `X-Hermes-Session-Id`，也可以使用原生的 `/api/sessions/{id}/chat` 请求，或是借助会话历史记录的 “运行” 请求来实现。而那些不包含头部信息的“聊天补全”请求、响应链式处理，以及通过 `previous_response_id` 或由客户端提供的历史记录进行的“运行”请求，则会以同步方式执行委托操作，并在当前轮次中直接返回结果。仅从请求内容中提取会话 ID 是无法实现分离式交付的。

对于可恢复的请求，每次委托单元都会保存一次补全结果。该结果可通过 `GET /api/sessions/{id}/messages` 获取，同时也会出现在下一次客户端轮次的会话历史记录中。重复发起请求不会再次插入相同的结果；临时性的任务失败通知则拥有独立的标识。在客户端持有会话租约并遵循压缩后的内容继续处理时，交付过程会暂时等待。无论是在 JSON 格式还是流式响应中，“聊天补全”功能都会体现您所指定的会话 ID；即便在内容经过压缩后，也请继续发送该 ID。

补全结果**绝不会主动触发模型的新一轮响应**，也不会绕过当前正在处理中的人机确认步骤。下一轮响应的主动权始终在客户端手中。那些继续使用自身历史记录快照的客户端，应选择同步委托模式，而非期望服务器端的交付内容能自动合并到这些快照中。

未消耗的事件缓冲区会在五分钟后过期，因此断开的客户端无法无限占用内存。此机制仅影响传输状态：正在运行的任务在其实际执行完毕之前，仍会显示在状态查询、审批、停止控制以及并发计数中。而保持连接的SSE订阅者则可继续正常接收数据。

### POST /v1/runs/\{run_id\}/stop

用于中断正在运行的代理轮次。该接口会立即返回`{"status": "stopping"}`，同时Hermes会要求当前活跃的代理在下一个安全的停止点处终止运行。该任务的状态将一直标记为“停止中”，直到其背后的执行任务真正结束，之后才会变为“已取消”；即便提交了停止请求，仍在运行的工作进程也不会因此被隐藏。

### POST /v1/runs/\{run_id\}/approval

用于处理那些需要人工决策才能继续的待审批任务（例如受审批策略限制的工具调用）。请求体中需包含审批结果；一旦该结果被记录，任务即可恢复运行。此接口在 `/v1/capabilities` 中被标注为 `run_approval` 功能，以便外部用户界面在弹出审批提示之前判断系统是否支持该功能。

## 任务API（后台调度任务）

服务器提供了一个轻量级的任务CRUD接口，便于远程客户端管理已调度的/后台运行的代理任务。所有接口均需通过相同的令牌认证才能访问。

### GET /api/jobs

列出所有已安排的调度任务。

### POST /api/jobs

创建一个新的定时任务。请求体格式与 `hermes cron` 相同——包括提示词、调度时间、所需技能、提供商配置覆盖以及交付目标。

### GET /api/jobs/\{job_id\}

获取单个任务的定义信息及其上次运行状态。

### PATCH /api/jobs/\{job_id\}

更新现有任务的各项字段（如提示词、调度时间等）。支持部分更新，这些更改会被合并应用。

### DELETE /api/jobs/\{job_id\}

删除某个任务，同时会取消其正在进行的运行任务。

### POST /api/jobs/\{job_id\}/pause

暂停任务而不将其删除。该任务的下次预定运行时间将被暂缓，直到被重新启动。

### POST /api/jobs/\{job_id\}/resume

恢复之前已暂停的任务。

### POST /api/jobs/\{job_id\}/run

立即触发任务运行，跳过原定的调度时间。

## 会话 API（基于 REST 的会话管理）

外部界面无需搭建专用控制面板，即可通过 REST 接口管理 Hermes 会话。所有接口均需通过 `API_SERVER_KEY` 来授权，且位于 `/api/sessions/*` 路径下。

| 方法 | 路径 | 描述 |
|------|------|-------------|
| `GET` | `/api/sessions` | 列出会话（支持分页——可通过`limit`、`offset`、`source`、`include_children`参数控制） |
| `POST` | `/api/sessions` | 创建一个空会话 |
| `GET` | `/api/sessions/{id}` | 读取会话元数据 |
| `PATCH` | `/api/sessions/{id}` | 更新会话标题或`end_reason`字段 |
| `DELETE` | `/api/sessions/{id}` | 删除会话 |
| `GET` | `/api/sessions/{id}/messages` | 查看某会话的消息历史记录 |
| `POST` | `/api/sessions/{id}/fork` | 通过`SessionDB`谱系结构对该会话进行分支处理（功能与CLI命令`/branch`一致） |
| `POST` | `/api/sessions/{id}/chat` | 执行一次同步式的智能体轮次响应 |
| `POST` | `/api/sessions/{id}/chat/stream` | 基于单次轮次响应的SSE数据流格式——会发送`assistant.delta`、`tool.started`、`tool.completed`、`run.completed`等事件 |

`/v1/capabilities`接口通过`session_*`特性标志以及`endpoints.session_*`条目来公开所有可用功能，以便外部用户界面能够检测相应支持能力并实现安全降级处理。在`chat`及`chat/stream`类型的请求数据中支持内联图片传输（该路径为多模态感知型路径）。

```bash
# fork a session and run one turn
curl -X POST http://localhost:8642/api/sessions/$ID/fork \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  -d '{"title": "explore alt path"}'

# stream a turn over SSE
curl -N -X POST http://localhost:8642/api/sessions/$ID/chat/stream \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  -d '{"input": "what files changed in the last hour?"}'
```

## 技能与工具集的查询

通过 `GET /v1/skills` 和 `GET /v1/toolsets`，外部客户端可以通过 REST 接口以确定性的方式列出该智能体的功能，而无需向模型发起请求。这两个接口均为只读性质，并受到 `API_SERVER_KEY` 的访问控制。

```bash
curl http://localhost:8642/v1/skills \
  -H "Authorization: Bearer $API_SERVER_KEY"
# → [{"name": "github-pr-workflow", "description": "...", "category": "..."}, ...]

curl http://localhost:8642/v1/toolsets \
  -H "Authorization: Bearer $API_SERVER_KEY"
# → [{"name": "core", "label": "...", "description": "...", "enabled": true,
#     "configured": true, "tools": ["read_file", "write_file", ...]}, ...]
```

`/v1/skills`接口会返回技能中心内部使用的相同元数据。而`/v1/toolsets`则返回为`api_server`平台解析出的工具集，同时还会列出每个工具集所包含的具体工具列表。这两项内容均会在`/v1/capabilities`下的`endpoints.*`路径中被列出。

## 长期记忆的作用域定义（`X-Hermes-Session-Key`）

像Open WebUI这样的多用户前端需要一个稳定的、针对每个频道的标识符，用于管理长期记忆（如Honcho等），该标识符需与基于对话记录的`X-Hermes-Session-Id`（会在执行`/new`操作时发生变化）**相互独立**。可以在`/v1/chat/completions`、`/v1/responses`或`/v1/runs`请求中传递`X-Hermes-Session-Key`，Hermes会将该键值传递给`AIAgent(gateway_session_key=...)`，随后Honcho内存提供程序会利用它来确定一个稳定的记忆作用域。

```http
POST /v1/chat/completions HTTP/1.1
Authorization: Bearer ***
X-Hermes-Session-Id: transcript-alpha
X-Hermes-Session-Key: agent:main:webui:dm:user-42
```

规则：长度不得超过256个字符，控制字符（`\r`、`\n`、`\x00`）将被拒绝，且该值会通过响应（JSON + SSE格式）原样返回。接口`/v1/capabilities`会通过`"session_key_header": "X-Hermes-Session-Key"`来表明对相关功能的支持。若未提供该密钥，Honcho的“每会话独立处理”策略会导致每个`session_id`拥有不同的作用范围——这正是Hermes之前的行为方式。

## 系统提示词处理

当前端发送`system`消息（用于聊天补全）或`instructions`字段（用于响应API）时，hermes-agent会将这些内容**叠加**在其核心系统提示词之上。您的智能体依然保留所有的工具、记忆和技能，前端的系统提示词仅会添加额外的指令。

这意味着您可以在不损失功能的前提下，针对不同前端定制智能体的行为：
- Open WebUI的系统提示词为：“你是一名Python专家，始终要添加类型提示。”
- 智能体仍然具备终端操作、文件处理、网络搜索、记忆功能等。

## 认证

通过`Authorization`请求头进行Bearer令牌认证：

```
Authorization: Bearer ***
```

可通过 `API_SERVER_KEY` 环境变量来配置密钥。如果需要通过浏览器直接调用 Hermes，还需将 `API_SERVER_CORS_ORIGINS` 设置为明确的允许列表。

### 多配置文件路由（`/p/<profile>/…`）

当启用[多配置文件网关路由](/user-guide/multi-profile-gateways)（即设置 `gateway.multiplex_profiles` 为 true）时，共享监听器会通过 `/p/<profile>/` 这一 URL 前缀为每个配置文件提供服务——且**认证会绑定到被路由的特定配置文件**：

- 发往 `/p/<profile>/v1/...` 的请求必须使用该配置文件自身的 `API_SERVER_KEY`（位于 `~/.hermes/profiles/<profile>/.env` 文件中）。对于带有命名前缀的请求，系统会拒绝使用默认监听器的密钥。
- 不带前缀的路由以及 `/p/default/...` 路由仍会使用默认配置文件的密钥。
- 若某个命名配置文件没有自己的 `API_SERVER_KEY`，则该配置文件的相关服务将无法正常访问，直到为其设置密钥为止。
- 运行任务是按配置文件隔离的：`/v1/runs/{run_id}` 及其对应的 `events`、`stop`、`steer`、`approval` 等路由仅响应创建该运行任务的配置文件（包括通过 `/api/sessions/{id}/chat/stream` 启动的运行任务）；其他配置文件的运行任务 ID 将返回 `404` 错误，而不会是 `403` 错误。

:::warning 重大变更（2026 年 7 月）
在此次修复之前，任何 `/p/<profile>/` 前缀下都会接受有效的默认配置文件密钥。如果您之前依赖在所有配置文件前缀下使用同一把共享密钥，现在需要在每个配置文件的 `.env` 文件中设置独立的 `API_SERVER_KEY`——在带有命名前缀的请求中使用重复的默认密钥将会导致 `401` 错误。
:::

:::warning 安全提示
API 服务器会授予对 hermes-agent 工具集的完全访问权限，**包括终端命令**。无论是在默认的 `127.0.0.1` 本地回环绑定模式下，还是其他部署场景下，**都必须设置 `API_SERVER_KEY`**。若明确允许浏览器发起请求，建议将 `API_SERVER_CORS_ORIGINS` 的值设置得较为严格，以控制浏览器的访问权限。
:::

## 配置选项

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `API_SERVER_ENABLED` | `false` | 是否启用 API 服务器 |
| `API_SERVER_PORT` | `8642` | HTTP 服务器端口 |
| `API_SERVER_HOST` | `127.0.0.1` | 绑定地址（默认仅为 localhost） |
| `API_SERVER_KEY` | _(必需)_ | 用于身份验证的令牌 |
| `API_SERVER_CORS_ORIGINS` | _(无)_ | 允许访问的浏览器地址，以逗号分隔 |
| `API_SERVER_MODEL_NAME` | _(配置文件名)_ | `/v1/models` 接口下对应的模型名称。默认为配置文件名，若使用默认配置文件则默认为 `hermes-agent` |

### config.yaml 文件
上述设置也可存储在 `~/.hermes/config.yaml` 文件中的 `gateway.api_server:` 子部分中：

```yaml
gateway:
  api_server:
    enabled: true
    port: 8642
    host: 127.0.0.1
    key: your-secret-key
    cors_origins: http://localhost:3000
    model_name: my-hermes
    max_concurrent_runs: 10   # concurrent-run cap; 0 disables the limit
```

`port`、`key`、`host`、`cors_origins` 以及 `model_name` 会自动被整合到平台的 `extra` 设置中，因此它们的行为与对应的 `API_SERVER_*` 环境变量完全一致。环境变量的优先级高于 `config.yaml` 中的配置值。该配置块也可放在 `gateway.platforms.api_server:` 下，或顶层の `platforms.api_server:` 部分中。

### 并发运行限制

API 服务器会限制同时在 OpenAI 兼容端点与 Runs 端点上运行的代理数量。此限制值可从 `gateway.api_server.max_concurrent_runs` 中读取（默认值为 **10**；设置为 `0` 即取消限制，负数值则会被强制视为 0）。当达到该限制时，新的启动请求将会被拒绝，并返回 **HTTP 429** 错误码“Too many concurrent runs (max N)”——客户端应稍作等待后重试。

## 安全标头

所有响应都会包含以下安全标头：
- `X-Content-Type-Options: nosniff` —— 防止 MIME 类型探测
- `Referrer-Policy: no-referrer` —— 防止引用源信息泄露

## CORS 支持

API 服务器默认**不**启用浏览器的 CORS 功能。

如需直接通过浏览器访问，需手动设置允许列表：

```bash
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

当启用 CORS 时：
- **预检响应**会包含 `Access-Control-Max-Age: 600`（缓存时间为 10 分钟）
- **SSE 流式响应**会包含 CORS 标头，以确保浏览器中的 EventSource 客户端能够正常工作
- **`X-Hermes-Session-Id`**属于允许的请求标头，因此位于白名单来源地址的浏览器可以发起会话续传请求
- **`Idempotency-Key`**也是允许的请求标头——客户端可将其用于去重处理（响应会根据该键缓存 5 分钟）

大多数有相关文档记载的前端应用，如 Open WebUI，均为服务器间直接通信，根本无需使用 CORS。

## 兼容的前端应用

任何支持 OpenAI API 格式的前端应用均可使用。经过测试并配有文档说明的集成方案如下：

| 前端应用 | 粉丝数 | 连接方式 |
|----------|-------|----------|
| [Open WebUI](/user-guide/messaging/open-webui) | 12.6万 | 提供完整使用指南 |
| LobeChat | 7.3万 | 使用自定义提供商端点 |
| LibreChat | 3.4万 | 在 librechat.yaml 中配置自定义端点 |
| AnythingLLM | 5.6万 | 使用通用 OpenAI 提供商 |
| NextChat | 8.7万 | 通过 BASE_URL 环境变量配置 |
| ChatBox | 3.9万 | 通过 API Host 设置配置 |
| Jan | 2.6万 | 通过远程模型配置 |
| HF Chat-UI | 0.8万 | 通过 OPENAI_BASE_URL 配置 |
| big-AGI | 0.7万 | 使用自定义端点 |
| OpenAI Python SDK | — | `OpenAI(base_url="http://localhost:8642/v1")` |
| curl | — | 直接发送 HTTP 请求 |

## 基于配置文件的多用户设置

若希望为不同用户提供独立的 Hermes 实例（拥有各自的配置、内存和技能），可使用[配置文件功能](/user-guide/profiles)：

```bash
# Create a profile per user
hermes profile create alice
hermes profile create bob

# Configure each profile's API server on a different port. API_SERVER_* are env
# vars (not config.yaml keys), so write them to each profile's .env:
cat >> ~/.hermes/profiles/alice/.env <<EOF
API_SERVER_ENABLED=true
API_SERVER_PORT=8643
API_SERVER_KEY=alice-secret
EOF

cat >> ~/.hermes/profiles/bob/.env <<EOF
API_SERVER_ENABLED=true
API_SERVER_PORT=8644
API_SERVER_KEY=bob-secret
EOF

# Start each profile's gateway
hermes -p alice gateway &
hermes -p bob gateway &
```

每个配置文件的 API 服务器都会自动将该配置文件名称作为模型 ID 进行标识：

- `http://localhost:8643/v1/models` → 模型 `alice`
- `http://localhost:8644/v1/models` → 模型 `bob`

在 Open WebUI 中，需为它们分别添加连接。模型下拉列表会将 `alice` 和 `bob` 显示为独立的模型，且每个模型都由一个完全隔离的 Hermes 实例支撑。详情请参阅 [Open WebUI 使用指南](/user-guide/messaging/open-webui#multi-user-setup-with-profiles)。

## 局限性

- **响应存储**——针对 `previous_response_id` 存储的响应会保存在 SQLite 中，因此即便网关重启也不会丢失。最多可存储 100 条响应（采用最近最少使用策略进行淘汰）。
- **不支持文件上传**——虽然 `/v1/chat/completions` 和 `/v1/responses` 都支持内联图片，但通过该 API 不支持上传文件（如 `file`、`input_file`、`file_id`）以及非图片格式的文档输入。
- **简单的 OpenAI 客户端仍会看到别名**——`/v1/models` 会显示稳定的 Hermes 别名（即 `hermes-agent` 或当前激活的配置文件名称）。功能更强大的客户端则可以在请求中明确指定 `provider` / `model_options` 参数以进行覆盖。

## 代理模式

该 API 服务器同时也可作为 **网关代理模式** 的后端。当其他 Hermes 网关实例通过 `GATEWAY_PROXY_URL` 指向此 API 服务器时，它就会将所有消息转发至此，而无需自行运行代理节点。这样一来即可实现分离部署——例如，一个用于处理 Matrix 加密通信的 Docker 容器可以将消息转发给主机上的代理节点。

如需完整的设置指南，请参阅 [Matrix 代理模式](/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos)。
