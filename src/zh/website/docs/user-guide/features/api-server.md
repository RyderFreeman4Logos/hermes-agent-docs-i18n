---
sidebar_position: 14
title: "API Server"
description: "Expose hermes-agent as an OpenAI-compatible API for any frontend"
---

# API服务器

API服务器将hermes-agent以兼容OpenAI的HTTP端点形式暴露出来。任何支持OpenAI格式的前端应用——如Open WebUI、LobeChat、LibreChat、NextChat、ChatBox以及数百种其他应用——都可以连接到hermes-agent并将其作为后端使用。

您的智能体可利用其完整的工具集（终端操作、文件处理、网络搜索、内存功能、技能等）来处理请求，并返回最终响应。在流式交互模式下，工具处理进度会实时显示，便于前端展示智能体的当前操作状态。

:::提示 一个后端即可同时支持模型与工具
要使API服务器真正发挥作用，Hermes本身需要配置好提供商以及工具后端。通过[Nous Portal](/user-guide/features/tool-gateway)订阅服务，即可同时实现这两项功能——300多种模型可通过工具网关获得支持，同时还能实现网页/图像/TTS/浏览器操作等功能。在启动API服务器及Open WebUI、LobeChat等前端应用之前，只需运行一次`hermes setup --portal`命令，即可为它们提供功能完备的工具后端。
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

## 端点

### POST /v1/chat/completions

采用标准的 OpenAI Chat Completions 格式。该接口为无状态设计，每次请求都会通过 `messages` 数组携带完整的对话内容。

**请求：**
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

**内联图片输入：** 用户消息可将 `content` 以包含 `text` 和 `image_url` 元素的数组形式发送。系统同时支持远程的 `http(s)` URL以及 `data:image/...` 格式的URL。

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

**流式响应**（设置 `"stream": true`）：以服务器推送事件（SSE）的形式逐条返回响应数据。在**聊天补全**场景中，流式响应会使用标准的 `chat.completion.chunk` 事件，同时还会加入 Hermes 自定义的 `hermes.tool.progress` 事件，以便更好地展示工具启动状态。而在**响应生成**场景中，则会使用 OpenAI 定义的响应事件类型，如 `response.created`、`response.output_text.delta`、`response.output_item.added`、`response.output_item.done` 和 `response.completed`。

**流式响应中的工具进度显示**：
- **聊天补全**：Hermes 会发送 `event: hermes.tool.progress` 事件来实时显示工具的启动状态，且不会影响已保存的助手对话内容。
- **响应生成**：在 SSE 流式响应过程中，Hermes 会发送符合规范定义的 `function_call` 和 `function_call_output` 事件，从而使客户端能够实时渲染结构化的工具界面。

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
    {"type": "function_call", "name": "terminal", "arguments": "{\"command\": \"ls\"}", "call_id": "call_1"},
    {"type": "function_call_output", "call_id": "call_1", "output": "README.md src/ tests/"},
    {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Your project has..."}]}
  ],
  "usage": {"input_tokens": 50, "output_tokens": 200, "total_tokens": 250}
}
```

**内联图片输入：** `input[].content` 可包含 `input_text` 和 `input_image` 两部分内容。该字段同时支持远程 URL 以及 `data:image/...` 格式的 URL：

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

服务器会自动跳转至该对话中最新的回复，其机制与网关会话中的 `/title` 命令类似。

### GET /v1/responses/\{id\}

根据 ID 查取之前存储的回复。

### DELETE /v1/responses/\{id\}

删除已存储的回复。

### GET /v1/models

列出可作为模型的智能体列表。所显示的模型名称默认为 [个人资料](/user-guide/profiles)中的名称（默认个人资料则为 `hermes-agent`）。大多数前端应用在模型发现功能中都需要调用此接口。

### GET /v1/capabilities

为外部用户界面、调度器以及插件桥接工具提供该 API 服务器功能范围的机器可读描述。

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

在集成控制面板、浏览器界面或控制平面时，可使用此端点。这样无需依赖 Hermes 的内部 Python 实现，即可检测当前运行的 Hermes 版本是否支持任务执行、流式处理、任务取消以及会话连续性功能。

### GET /health

用于健康状态检查，返回 `{"status": "ok"}`。对于需要 `/v1/` 前缀的 OpenAI 兼容客户端，也可通过 **GET /v1/health** 访问该接口。

### GET /health/detailed

针对监控系统与控制平面设计的身份验证后就绪状态检查。它会反馈当前活跃配置文件的配置信息、状态数据库、已配置模型、磁盘空间、网关/平台状态、正在运行的 API 任务、待完成的处理流程以及正在进行的任务委托等各项指标的运行状态。响应内容仅包含状态与计数信息，不会暴露配置值、凭证、路径、命令、队列数据或原始错误信息。

公开的 `/health` 接口仅作为简单的存活检测工具，不执行就绪状态检查。即便检测结果为不就绪，也会返回 HTTP 200 状态码；此时需查看响应中的顶级 `status` 和 `readiness.checks` 字段以获取详细信息。

## Runs API（适用于流式处理的替代方案）

除了 `/v1/chat/completions` 和 `/v1/responses` 接口外，服务器还提供了一个 **runs** API，专为需要长时间会话的场景设计。通过该接口，客户端可订阅任务进度事件，而无需自行处理流式数据传输。

### POST /v1/runs

用于创建新的代理任务运行实例。响应中会返回一个 `run_id`，可用于订阅后续的进度事件。

```json
{
  "run_id": "run_abc123",
  "status": "started"
}
```

该接口可接收一个简单的 `input` 字符串，以及可选的 `session_id`、`instructions`、`conversation_history` 或 `previous_response_id` 参数。当提供了 `session_id` 时，Hermes 会将其显示在运行状态中，以便外部用户界面能够将各次运行与自身的对话 ID 关联起来。

### GET /v1/runs/\{run_id\}

用于轮询当前运行的状态。这对于那些无需保持 SSE 连接即可获取状态的控制面板，或是需要在页面跳转后重新连接的用户界面来说非常有用。

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

在终端状态（如“已完成”、“失败”或“已取消”）出现后，系统会暂时保留这些状态，以便用于轮询和界面状态同步。

### GET /v1/runs/\{run_id\}/events

该接口通过 Server-Sent Events 流式传输任务中工具调用的进度、令牌变化以及生命周期事件。它专为那些希望在不丢失状态的情况下进行连接/断开操作的仪表板及复杂客户端设计。

未被处理的事件缓冲区会在五分钟后过期，从而防止断开连接的客户端无限占用内存。不过，这仅会使传输层状态失效：只要任务执行过程仍在继续，它就会在状态轮询、审批操作、停止控制以及并发计数中保持可见，直到实际执行工作完成为止。而保持连接的 SSE 订阅者则可继续正常接收数据。

### POST /v1/runs/\{run_id\}/stop

用于中断正在运行的智能体轮次。该接口会立即返回 `{"status": "stopping"}`，同时 Hermes 会指示当前活跃的智能体在下一个安全的停止点暂停工作。该任务的状态将一直标记为“正在停止”，直到后台执行工作结束，之后才会变为“已取消”；即便发出了停止请求，仍在运行的任务 Worker 依然会保持可见。

### POST /v1/runs/\{run_id\}/approval

用于处理那些需要人工决策才能继续的任务（例如，受审批策略限制的工具调用）。请求体中需包含审批结果；一旦该结果被记录下来，任务就会恢复运行。该接口在 `/v1/capabilities` 中被标记为 `run_approval` 功能，以便外部界面在弹出审批提示之前就能判断系统是否支持此功能。

## Jobs API（后台调度任务）

服务器提供了一个轻量级的 Jobs CRUD 接口，允许远程客户端管理已调度的/后台运行的智能体任务。所有接口均需通过相同的令牌认证才能访问。

### GET /api/jobs

列出所有已调度的任务。

### POST /api/jobs

创建一个新的调度任务。请求体格式与 `hermes cron` 相同，包括提示语、调度时间、所需技能、提供商配置以及交付目标等字段。

### GET /api/jobs/\{job_id\}

获取某个特定任务的定义及其上次运行状态。

### PATCH /api/jobs/\{job_id\}

更新现有任务的某些字段（如提示语、调度时间等）。部分更新内容会被合并处理。

### DELETE /api/jobs/\{job_id\}

删除某个任务，同时也会取消该任务下正在运行的任何任务。

### POST /api/jobs/\{job_id\}/pause

暂停某个任务而不将其删除。该任务的下次 scheduled-run 时间会被暂缓，直到被重新启动为止。

### POST /api/jobs/\{job_id\}/resume

恢复之前被暂停的任务。

### POST /api/jobs/\{job_id\}/run

立即触发任务运行，跳过原有的调度时间。

## Sessions API（基于 REST 的会话控制）

外部界面无需搭建专用仪表板，即可通过 REST 接口管理 Hermes 会话。所有接口均受 `API_SERVER_KEY` 保护，路径位于 `/api/sessions/*` 下。

| 方法 | 路径 | 描述 |
|------|------|-------------|
| `GET` | `/api/sessions` | 列出所有会话（支持分页——可通过 `limit`、`offset`、`source`、`include_children` 参数控制） |
| `POST` | `/api/sessions` | 创建一个空会话 |
| `GET` | `/api/sessions/{id}` | 读取会话的元数据 |
| `PATCH` | `/api/sessions/{id}` | 更新会话的标题或 `end_reason` 字段 |
| `DELETE` | `/api/sessions/{id}` | 删除某个会话 |
| `GET` | `/api/sessions/{id}/messages` | 查看某个会话的消息历史记录 |
| `POST` | `/api/sessions/{id}/fork` | 通过 `SessionDB` 线索创建该会话的子会话（功能与 CLI 的 `/branch` 命令类似） |
| `POST` | `/api/sessions/{id}/chat` | 执行一次同步式的智能体轮次对话 |
| `POST` | `/api/sessions/{id}/chat/stream` | 为单次对话提供 SSE 流式传输——会发送 `assistant.delta`、`tool.started`、`tool.completed`、`run.completed` 等事件 |

`/v1/capabilities` 接口通过 `session_*` 功能标志以及 `endpoints.session_*` 条目，公开了所有相关的接口信息，这样外部界面就能提前判断系统是否支持这些功能，并采取相应的处理措施。在 `chat` 和 `chat/stream` 类型的请求载荷中，也支持嵌入图片（即多模态感知的传输格式）。

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

通过 `GET /v1/skills` 和 `GET /v1/toolsets`，外部客户端可以通过 REST 接口以确定性的方式列出代理的各项功能，而无需向模型发起请求。这两个接口均为只读性质，并且需要通过 `API_SERVER_KEY` 进行权限验证。

```bash
curl http://localhost:8642/v1/skills \
  -H "Authorization: Bearer $API_SERVER_KEY"
# → [{"name": "github-pr-workflow", "description": "...", "category": "..."}, ...]

curl http://localhost:8642/v1/toolsets \
  -H "Authorization: Bearer $API_SERVER_KEY"
# → [{"name": "core", "label": "...", "description": "...", "enabled": true,
#     "configured": true, "tools": ["read_file", "write_file", ...]}, ...]
```

`/v1/skills`接口会返回技能中心内部使用的相同元数据。而`/v1/toolsets`接口则返回为`api_server`平台解析出的工具集，同时还会列出每个工具集所包含的具体工具列表。这两类信息都会在`/v1/capabilities`下的`endpoints.*`路径中进行展示。

## 长期记忆的作用域设置（`X-Hermes-Session-Key`）

像Open WebUI这样的多用户前端需要一个与转录记录相关的`X-Hermes-Session-Id`（该标识会在每次调用`/new`时变化）**相互独立**的、用于长期记忆（如Honcho等）的稳定通道标识符。您可以在`/v1/chat/completions`、`/v1/responses`或`/v1/runs`请求中传递`X-Hermes-Session-Key`，Hermes会将该键值传递给`AIAgent(gateway_session_key=...)`，随后Honcho记忆提供器便会利用它来确定一个稳定的记忆作用域。

```http
POST /v1/chat/completions HTTP/1.1
Authorization: Bearer ***
X-Hermes-Session-Id: transcript-alpha
X-Hermes-Session-Key: agent:main:webui:dm:user-42
```

规则：长度上限为256个字符，控制字符（`\r`、`\n`、`\x00`）将被拒绝，且该值会以JSON加SSE格式在响应中原样返回。接口`/v1/capabilities`会通过`"session_key_header": "X-Hermes-Session-Key"`来标明对相关功能的支持。若未提供该密钥，Honcho的“每会话独立处理”策略会导致每个`session_id`拥有不同的作用范围——这正是Hermes之前的行为模式。

## 系统提示词处理

当前端发送`system`消息（用于聊天补全）或`instructions`字段（用于响应API）时，hermes-agent会将这些内容**叠加**在其核心系统提示词之上。您的智能体依然保留所有的工具、记忆和技能，前端的系统提示词仅会添加额外的指令。

这意味着您可以在不损失功能的前提下针对不同前端定制行为：
- Open WebUI的系统提示词为：“你是一名Python专家，务必始终添加类型提示。”
- 智能体仍可使用终端、文件操作、网络搜索、记忆等功能。

## 认证方式

通过`Authorization`请求头进行Bearer令牌认证：

```
Authorization: Bearer ***
```

可通过 `API_SERVER_KEY` 环境变量来配置密钥。如果需要通过浏览器直接调用 Hermes，还需将 `API_SERVER_CORS_ORIGINS` 设置为明确的允许列表。

:::warning 安全提示
API 服务器会授予对 hermes-agent 工具集的完全访问权限，**包括终端命令**。无论是在默认的 `127.0.0.1` 回环绑定模式下，还是其他部署场景，**每次部署时都必须设置 `API_SERVER_KEY`**。在明确允许浏览器访问时，请将 `API_SERVER_CORS_ORIGINS` 的范围限定得较窄，以控制浏览器的访问权限。
:::

## 配置选项

### 环境变量

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `API_SERVER_ENABLED` | `false` | 是否启用 API 服务器 |
| `API_SERVER_PORT` | `8642` | HTTP 服务器端口 |
| `API_SERVER_HOST` | `127.0.0.1` | 绑定地址（默认仅为 localhost） |
| `API_SERVER_KEY` | _(必需)_ | 用于身份验证的令牌 |
| `API_SERVER_CORS_ORIGINS` | _(无)_ | 以逗号分隔的允许访问的浏览器域名 |
| `API_SERVER_MODEL_NAME` | _(配置文件名)_ | `/v1/models` 接口中的模型名称。默认为配置文件名，若使用默认配置文件则默认为 `hermes-agent`。 |

### config.yaml 文件配置

```yaml
# Not yet supported — use environment variables.
# config.yaml support coming in a future release.
```

## 安全标头

所有响应均包含以下安全标头：
- `X-Content-Type-Options: nosniff` — 防止 MIME 类型嗅探
- `Referrer-Policy: no-referrer` — 防止引用源泄露

## CORS

API 服务器默认**不**启用浏览器的 CORS 功能。

如需直接通过浏览器访问，需手动设置允许列表：

```bash
API_SERVER_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

当启用 CORS 时：
- **预检响应**会包含 `Access-Control-Max-Age: 600`（缓存时间为 10 分钟）
- **SSE 流式响应**会包含 CORS 标头，以确保浏览器中的 EventSource 客户端能够正常工作
- **`Idempotency-Key`** 是允许使用的请求标头——客户端可将其用于去重处理（响应会按该键缓存 5 分钟）

大多数有文档记载的前端应用，如 Open WebUI，均为服务器间直接通信，因此根本不需要 CORS。

## 兼容的前端应用

任何支持 OpenAI API 格式的前端应用均可使用。已经过测试并配有文档的集成方案如下：

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

若希望为多名用户提供独立的 Hermes 实例（各自的配置、内存和技能），可使用 [配置文件功能](/user-guide/profiles)：

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

每个配置文件的 API 服务器会自动将该配置文件名称作为模型 ID 进行标识：

- `http://localhost:8643/v1/models` → 模型 `alice`
- `http://localhost:8644/v1/models` → 模型 `bob`

在 Open WebUI 中，需为每个模型单独添加连接。模型下拉列表中会将 `alice` 和 `bob` 显示为独立的模型，且每个模型都由一个完全隔离的 Hermes 实例支持。详情请参阅 [Open WebUI 使用指南](/user-guide/messaging/open-webui#multi-user-setup-with-profiles)。

## 局限性

- **响应存储**——针对 `previous_response_id` 存储的响应会保存在 SQLite 中，因此能在网关重启后依然保留。最多可存储 100 条响应（采用最近最少使用策略进行淘汰）。
- **不支持文件上传**——虽然 `/v1/chat/completions` 和 `/v1/responses` 接口都支持内联图片，但通过该 API 不支持上传文件（如 `file`、`input_file`、`file_id`）以及非图片类型的文档输入。
- **模型字段仅作展示**——虽然请求中的 `model` 字段会被接收，但实际上使用的 LLM 模型是在 `config.yaml` 文件的服务器端配置中确定的。

## 代理模式

该 API 服务器同时还可作为 **网关代理模式** 的后端。当其他 Hermes 网关实例通过 `GATEWAY_PROXY_URL` 指向此 API 服务器时，它就会将所有消息转发到此处，而无需自行运行代理节点。这样一来就可以实现分离部署——例如，一个用于处理 Matrix 加密通信的 Docker 容器可以将消息转发给主机上的代理节点。

完整的设置指南请参阅 [Matrix 代理模式](/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos)。
