# Hermes Agent 的 OpenAI 兼容 API 服务器

## 设计初衷

目前所有主流的聊天前端应用（Open WebUI 12.6万★、LobeChat 7.3万★、LibreChat 3.4万★、AnythingLLM 5.6万★、NextChat 8.7万★、ChatBox 3.9万★、Jan 2.6万★、HF Chat-UI 8千★、big-AGI 7千★）均通过支持 SSE 流式传输的 OpenAI 兼容 REST API 与后端进行连接。通过提供该接口，hermes-agent 即可立即作为所有这些应用的后端使用——无需额外定制适配器。

## 功能优势

```
┌──────────────────┐
│  Open WebUI      │──┐
│  LobeChat        │  │    POST /v1/chat/completions
│  LibreChat       │  ├──► Authorization: Bearer <key>     ┌─────────────────┐
│  AnythingLLM     │  │    {"messages": [...]}             │  hermes-agent   │
│  NextChat        │  │                                    │  gateway        │
│  Any OAI client  │──┘    ◄── SSE streaming response      │  (API server)   │
└──────────────────┘                                        └─────────────────┘
```

用户需执行以下操作：
1. 在 `~/.hermes/.env` 文件中设置 `API_SERVER_ENABLED=true`。
2. 运行 `hermes gateway`（API 服务器会与 Telegram/Discord 等平台一同启动）。
3. 将 Open WebUI（或任何前端界面）指向 `http://localhost:8642/v1`。
4. 通过任何支持 OpenAI 的界面与 hermes-agent 进行对话。

## 接口端点

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/v1/chat/completions` | 与智能体进行对话（流式与非流式） |
| GET | `/v1/models` | 列出可用的“模型”（hermes-agent 也会作为模型显示） |
| GET | `/health` | 健康状态检查 |

## 架构设计

### 方案 A：网关平台适配器（推荐）

创建名为 `gateway/platforms/api_server.py` 的新平台适配器，该适配器继承自 `BasePlatformAdapter`。这是最合理的方案，原因如下：
- 可复用所有网关基础设施（会话管理、身份验证、上下文构建）。
- 与其他适配器在同一异步循环中运行。
- 能免费获得消息处理、中断支持以及会话持久化功能。
- 遵循既定架构模式（与 Telegram、Discord 等平台一致）。
- 使用已有的依赖项 `aiohttp.web` 来搭建 HTTP 服务器。

该适配器会在 `connect()` 方法中启动一个 `aiohttp.web.Application` 服务器，并通过标准的 `handle_message()` 流程来处理传入的 HTTP 请求。

### 方案 B：独立组件

在 `gateway/api_server.py` 中创建一个独立的 HTTP 服务器类，直接实例化 AIAgent 对象。虽然实现更简单，但会重复编写会话处理和身份验证逻辑。

**推荐选择方案 A**——它与现有架构相兼容，需要维护的代码更少，还能免费获得网关的所有功能。

## 请求/响应格式

### 非流式对话补全

```
POST /v1/chat/completions
Authorization: Bearer hermes-api-key-here
Content-Type: application/json

{
  "model": "hermes-agent",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What files are in the current directory?"}
  ],
  "stream": false,
  "temperature": 0.7
}
```

响应：
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1710000000,
  "model": "hermes-agent",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Here are the files in the current directory:\n..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 200,
    "total_tokens": 250
  }
}
```

### 聊天补全（流式传输）

使用参数 `"stream": true` 发送相同请求。响应采用 SSE 格式：

```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":"Here "},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":"are "},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### 模型列表

```
GET /v1/models
Authorization: Bearer hermes-api-key-here
```

响应：
```json
{
  "object": "list",
  "data": [{
    "id": "hermes-agent",
    "object": "model",
    "created": 1710000000,
    "owned_by": "hermes-agent"
  }]
}
```

## 核心设计决策

### 1. 会话管理

OpenAI API 是无状态的——每个请求都包含完整的对话内容。
而 hermes-agent 的会话则具有持久状态（记忆、技能、工具上下文）。

**实现方案：混合模式**
- 默认模式：无状态。每个请求相互独立，`messages` 数组即代表整个对话内容，请求之间不会保留会话状态。
- 支持通过 `X-Session-ID` 请求头启用持久会话。当提供该标识后，服务器会在多次请求之间保持会话状态（包括对话历史、记忆上下文及工具状态），从而实现更丰富的智能体行为。
- 会话 ID 还可用于中断功能：在当前请求仍在处理时，若收到相同会话 ID 的新请求，即可触发中断。

### 2. 流式传输

智能体的 `run_conversation()` 方法为同步调用，会一次性返回完整响应。
而要实现真正的 SSE 流式传输，就需要在内容生成时逐块发送。

**第一阶段（最小可行产品）：** 在单独线程中运行智能体，将完整响应以单个 SSE 数据块加上 `[DONE]` 标记的形式返回。所有前端都能正常接收，只是会看到快速返回的单一数据块。虽非真正的流式传输，但已具备基本功能。

**第二阶段：** 为 AIAgent 添加响应回调机制，在大型语言模型生成文本时即可逐块发送。API 服务器通过队列捕获这些数据块，并以 SSE 事件的形式进行流式传输，从而实现真正的逐token流式输出。

**第三阶段：** 进一步实现工具执行进度的流式展示——在智能体运行过程中，实时发送工具调用/结果事件，让前端能够了解智能体的当前操作状态。

### 3. 工具透明度

提供两种模式：
- **不透明模式（默认）：** 前端仅能看到最终响应，工具调用均在服务器端完成且不可见。适用于通用型用户界面。
- **透明模式（通过请求头启用）：** 工具调用会以 OpenAI 格式的 `tool_call/tool_result` 消息形式出现在流数据中，便于具备智能体感知能力的前端使用。

### 4. 认证机制

- 通过 `Authorization: Bearer <key>` 请求头传递令牌
- 令牌可通过 `API_SERVER_KEY` 环境变量进行配置
- 可选：允许仅限本机访问且无需认证（绑定到 127.0.0.1 地址）
- 遵循与其他平台适配器的相同认证逻辑

### 5. 模型映射

前端会发送 `"model": "hermes-agent"`（或其他模型名称）。实际使用的 LLM 模型则在服务器端的 config.yaml 文件中配置。API 服务器会将所有请求的模型名称映射到已配置的 hermes-agent 模型。

也可选择允许直接使用指定模型：如果前端发送 `"model": "anthropic/claude-sonnet-4"`，智能体就会使用该模型。此功能可通过配置开关控制。

## 配置选项

```yaml
# In config.yaml
api_server:
  enabled: true
  port: 8642
  host: "127.0.0.1"        # localhost only by default
  key: "your-secret-key"   # or via API_SERVER_KEY env var
  allow_model_override: false  # let clients choose the model
  max_concurrent: 5         # max simultaneous requests
```

环境变量：
```bash
API_SERVER_ENABLED=true
API_SERVER_PORT=8642
API_SERVER_HOST=127.0.0.1
API_SERVER_KEY=your-secret-key
```

## 实施计划

### 第一阶段：最小可行产品（非流式）—— 提交 Pull Request

1. `gateway/platforms/api_server.py` —— 新增适配器
   - 基于 aiohttp 的 Web 服务器，包含以下接口：
     - `POST /v1/chat/completions` —— 对话补全 API（兼容所有平台）
     - `POST /v1/responses` —— 响应生成 API（支持服务器端状态保留及工具信息保存）
     - `GET /v1/models` —— 列出可用模型
     - `GET /health` —— 系统健康检查
   - 载荷令牌认证中间件
   - 非流式响应机制（启动智能体后直接返回完整结果）
   - 对话补全功能：无状态设计，对话内容以消息数组形式存储
   - 响应生成 API：通过 previous_response_id 在服务器端存储对话历史
     - 按响应编号存储完整的内部对话记录（包括工具调用信息）
     - 在后续请求中，根据已存储的对话链重建完整上下文
   - 前端系统提示语将叠加在 hermes-agent 的核心提示语之上

2. `gateway/config.py` —— 新增 `Platform.API_SERVER` 枚举及相关配置

3. `gateway/run.py` —— 在 `_create_adapter()` 函数中注册该适配器

4. 测试代码位于 `tests/gateway/test_api_server.py` 文件中

### 第二阶段：SSE 流式传输

1. 为上述两个接口添加流式响应功能
   - 对话补全功能：采用 SSE 格式，通过 `choices[0].delta.content` 传输内容
   - 响应生成 API：通过语义化事件（如 `response.output_text.delta` 等）传输数据
   - 在单独线程中运行智能体，并通过回调队列收集输出结果
   - 处理客户端断开连接的情况（自动终止智能体进程）

2. 为 `AIAgent.run_conversation()` 方法新增 `stream_callback` 参数

### 第三阶段：增强功能

1. 工具调用透明模式（可选）
2. 模型直接传递/覆盖功能
3. 并发请求数量限制
4. 使用情况追踪与速率限制机制
5. 为基于浏览器的前端提供 CORS 头信息
6. `GET /v1/responses/{id}` —— 获取已存储的响应结果
7. `DELETE /v1/responses/{id}` —— 删除已存储的响应结果

## 变更文件列表

| 文件 | 修改内容 |
|------|----------|
| `gateway/platforms/api_server.py` | 新增 —— 主要适配器代码（约 300 行） |
| `gateway/config.py` | 新增 Platform.API_SERVER 枚举及相关配置（约 20 行） |
| `gateway/run.py` | 在 _create_adapter() 函数中注册适配器（约 10 行） |
| `tests/gateway/test_api_server.py` | 新增 —— 测试代码（约 200 行） |
| `cli-config.yaml.example` | 增加 api_server 相关配置项 |
| `README.md` | 在平台列表中提及 API 服务器功能 |

## 兼容性矩阵

实现完成后，hermes-agent 可作为即插即用的后端服务，支持以下前端应用：

| 前端应用 | 粉丝数 | 连接方式 |
|----------|-------|-----------|
| Open WebUI | 12.6万 | 设置 → 连接 → 添加 OpenAI API，URL：`http://localhost:8642/v1` |
| NextChat | 8.7万 | 通过 BASE_URL 环境变量配置 |
| LobeChat | 7.3万 | 使用自定义提供者端点 |
| AnythingLLM | 5.6万 | 在 LLM 提供者设置中选择“通用 OpenAI”选项 |
| Oobabooga | 4.2万 | 该应用本身为后端工具，非前端界面 |
| ChatBox | 3.9万 | 通过 API 主机地址配置 |
| LibreChat | 3.4万 | 通过 librechat.yaml 文件指定自定义端点 |
| Chatbot UI | 2.9万 | 需配置自定义 API 端点 |
| Jan | 2.6万 | 需配置远程模型参数 |
| AionUI | 1.8万 | 需配置自定义 API 端点 |
| HF Chat-UI | 0.8万 | 通过 OPENAI_BASE_URL 环境变量配置 |
| big-AGI | 0.7万 | 需配置自定义端点 |
