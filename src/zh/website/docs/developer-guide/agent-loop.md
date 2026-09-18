---
sidebar_position: 3
title: "Agent Loop Internals"
description: "Detailed walkthrough of AIAgent execution, API modes, tools, callbacks, and fallback behavior"
---

# Agent循环内部机制

核心调度引擎为`AIAgent`类。目前`run_agent.py`仅作为一个轻量级的接口层：实际的循环逻辑位于`agent/conversation_loop.py`中，每个轮次阶段则分别处理在`agent/turn_*.py`文件中（包括迭代准备、API调用、API错误处理、内容溢出、截断以及恢复机制）；构造函数相关的配置则放在`agent/agent_init.py`中。而从提示语构建到工具调用，再到提供者故障切换等所有功能，都通过分散在`agent/*.py`模块中的代码集成在`AIAgent`类中。

## 核心职责

`AIAgent`负责以下工作：

- 通过`prompt_builder.py`构建有效的系统提示语及工具结构定义
- 选择合适的提供者/API模式（如chat_completions、codex_responses、anthropic_messages等）
- 支持取消功能的可中断模型调用
- 执行工具调用（可通过顺序执行或线程池实现并发处理）
- 以OpenAI消息格式保存对话历史记录
- 处理数据压缩、重试机制以及备用模型切换功能
- 跟踪父代理与子代理之间的迭代预算使用情况
- 在上下文丢失前清除持久化内存中的数据

## 两个入口点

```python
# Simple interface — returns final response string
response = agent.chat("Fix the bug in main.py")

# Full interface — returns dict with messages, metadata, usage stats
result = agent.run_conversation(
    user_message="Fix the bug in main.py",
    system_message=None,           # auto-built if omitted
    conversation_history=None,      # auto-loaded from session if omitted
    task_id="task_abc123"
)
```

`chat()` 是 `run_conversation()` 的简化封装版本，它从返回结果字典中提取 `final_response` 字段。

## API 模式

Hermes 支持三种 API 执行模式，这些模式的确定依据包括所选的提供商、明确的参数以及基础 URL 的特征分析：

| API 模式 | 适用场景 | 客户端类型 |
|----------|----------|-------------|
| `chat_completions` | 兼容 OpenAI 的接口（OpenRouter、自定义接口及大多数提供商） | `openai.OpenAI` |
| `codex_responses` | OpenAI Codex / Responses API | 使用 Responses 格式的 `openai.OpenAI` |
| `anthropic_messages` | 原生的 Anthropic Messages API | 通过适配器使用的 `anthropic.Anthropic` |

不同的 API 模式决定了消息的格式、工具调用的结构、响应的解析方式以及缓存/流式处理的机制。在发起 API 调用之前和之后，这三种模式最终都会转换为相同的内部消息格式（即 OpenAI 风格的 `role`/`content`/`tool_calls` 字典）。

**模式确定顺序：**
1. 明确指定的 `api_mode` 构造函数参数（优先级最高）
2. 根据提供商类型进行识别（例如，使用 `anthropic` 提供商则对应 `anthropic_messages` 模式）
3. 基于基础 URL 的特征分析（例如，URL 为 `api.anthropic.com` 则对应 `anthropic_messages` 模式）
4. 默认模式：`chat_completions`

## 对话轮次生命周期

智能体循环的每一轮都会按照以下顺序执行：

```text
run_conversation()
  1. Generate task_id if not provided
  2. Append user message to conversation history
  3. Build or reuse cached system prompt (prompt_builder.py)
  4. Check if preflight compression is needed (>50% context)
  5. Build API messages from conversation history
     - chat_completions: OpenAI format as-is
     - codex_responses: convert to Responses API input items
     - anthropic_messages: convert via anthropic_adapter.py
  6. Inject ephemeral prompt layers (budget warnings, context pressure)
  7. Apply prompt caching markers if on Anthropic
  8. Make interruptible API call (_interruptible_api_call)
  9. Parse response:
     - If tool_calls: execute them, append results, loop back to step 5
     - If text response: persist session, flush memory if needed, return
```

### 消息格式

所有消息在内部均采用与 OpenAI 兼容的格式进行传输：

```python
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "...", "tool_calls": [...]}
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

来自支持深度思考的模型的推理内容会存储在 `assistant_msg["reasoning"]` 中，也可通过 `reasoning_callback` 选项进行展示。

### 消息轮换规则

Agent 循环会严格遵循消息角色的轮换顺序：

- 系统消息之后：`用户 → 助手 → 用户 → 助手 → ...`
- 调用工具时：`助手（携带 tool_calls）→ 工具 → 工具 → ... → 助手`
- **绝不允许**连续出现两条助手消息
- **绝不允许**连续出现两条用户消息
- **仅允许** `tool` 角色的消息连续出现（即并行工具结果）

Providers 会验证这些消息序列，若发现格式错误的历史记录将会予以拒绝。

## 可中断的 API 调用

API 请求会被封装在 `_interruptible_api_call()` 函数中，该函数会在后台线程中执行实际的 HTTP 请求，同时持续监控中断事件：

```text
┌────────────────────────────────────────────────────┐
│  Main thread                  API thread           │
│                                                    │
│   wait on:                     HTTP POST           │
│    - response ready     ───▶   to provider         │
│    - interrupt event                               │
│    - timeout                                       │
└────────────────────────────────────────────────────┘
```

当任务被中断时（用户发送新消息、执行 `/stop` 命令或发送信号）：
- API 线程将被终止（相应响应也会被丢弃）
- 智能体可以选择处理新的输入，或者干净地关闭
- 不会向对话历史中插入不完整的响应

## 工具执行机制

### 顺序执行与并行执行

当模型返回工具调用请求时：
- **单次工具调用** → 直接在主线程中执行
- **多次工具调用** → 通过 `ThreadPoolExecutor` 实现并行执行
  - 注意：被标记为交互式工具的调用（如 `clarify`）将强制按顺序执行
  - 不论实际执行顺序如何，结果都会按照最初的工具调用顺序重新插入

### 执行流程

```text
for each tool_call in response.tool_calls:
    1. Resolve handler from tools/registry.py
    2. Fire pre_tool_call plugin hook
    3. Check if dangerous command (tools/approval.py)
       - If dangerous: invoke approval_callback, wait for user
    4. Execute handler with args + task_id
    5. Fire post_tool_call plugin hook
    6. Append {"role": "tool", "content": result} to history
```

### Agent级工具

某些工具会在被调用`handle_function_call()`之前，由`agent/tool_executor.py`（由`agent/conversation_loop.py`触发）进行拦截：

| 工具 | 拦截原因 |
|------|----------|
| `todo` | 用于读取/写入代理本地的任务状态 |
| `memory` | 向存在字符长度限制的持久化内存文件中写入数据 |
| `session_search` | 通过代理的会话数据库查询会话历史记录 |
| `delegate_task` | 创建具有独立上下文的子代理 |

这些工具会直接修改代理状态，并在无需经过注册表的情况下返回模拟的工具结果。

## 回调接口

`AIAgent`支持特定平台的回调功能，可在CLI、网关及ACP集成环境中实现实时进度显示：

| 回调函数 | 触发时机 | 使用方 |
|----------|-----------|--------|
| `tool_progress_callback` | 每次工具执行前后 | CLI旋转加载指示器、网关进度消息 |
| `thinking_callback` | 模型开始/停止思考时 | CLI“正在思考...”提示 |
| `reasoning_callback` | 模型返回推理内容时 | CLI推理结果展示、网关推理模块 |
| `clarify_callback` | 调用`clarify`工具时 | CLI输入提示、网关交互式消息 |
| `step_callback` | 每轮完整对话结束后 | 网关步骤追踪、ACP进度显示 |
| `stream_delta_callback` | 每个流式数据块（启用时） | CLI流式数据展示 |
| `tool_gen_callback` | 从流式数据中解析出工具调用时 | CLI工具预览（以旋转加载指示器形式呈现） |
| `status_callback` | 状态发生变化时（如思考中、执行中等） | ACP状态更新 |

## 预算与回退机制

### 迭代预算

智能体通过`IterationBudget`来跟踪迭代次数：

- 默认值：500次迭代（可通过`agent.max_turns`参数配置）
- 每个智能体拥有独立的预算额度。子智能体的预算上限为`delegation.max_iterations`（默认为50次）——父智能体与所有子智能体的总迭代次数可超过父智能体的上限
- 当迭代次数达到100%时，智能体会停止运行并返回已完成工作的总结

### 回退模型

当主模型出现故障时（如429限流、5xx服务器错误、401/403认证错误）：

1. 检查配置文件中的 `fallback_providers` 列表。  
2. 按顺序尝试每个备用提供方。  
3. 若成功，则使用新的提供方继续对话。  
4. 遇到 401/403 错误时，先尝试刷新凭证，再切换备用提供方。  

该备用系统还独立处理各类辅助任务——视觉处理、压缩以及网页提取功能均拥有各自的备用流程，可通过 `auxiliary.*` 配置项进行设置。  

## 压缩与持久化  

### 触发压缩的场景  

- **预检查阶段**（API 调用之前）：当对话内容占模型上下文窗口的 50% 以上时。  
- **网关自动压缩**：当对话内容占上下文窗口的 85% 以上时（更为激进，会在对话轮次之间自动执行）。  

### 压缩过程中的操作  

1. 首先将内存内容刷新到磁盘，以避免数据丢失。  
2. 对对话中的中间轮次内容进行总结，生成简短的摘要。  
3. 最后 N 条消息会被完整保留（通过 `compression.protect_last_n` 参数控制，默认值为 20）。  
4. 工具调用与结果消息会保持绑定，不会被拆分。  
5. 系统会生成新的会话标识符（压缩操作会创建一个“子”会话）。  

### 会话持久化  

在每个对话轮次结束后：  
- 消息会被保存到会话存储中（通过 `hermes_state.py` 使用 SQLite 存储）。  
- 内存中的变更内容会被同步到 `MEMORY.md` 和 `USER.md` 文件中。  
- 后续可通过 `/resume` 命令或 `hermes chat --resume` 参数恢复该会话。  

## 主要源文件

| 文件名 | 用途 |
|------|------|
| `run_agent.py` | `AIAgent` 接口层——公共入口点；对话循环及轮次处理逻辑位于 `agent/` 目录下 |
| `agent/conversation_loop.py` | 对话循环逻辑（即 `run_conversation()` 函数的实现部分） |
| `agent/turn_*.py` | 各轮次处理模块：iteration_prep、api_call、api_error、overflow、truncation、recovery |
| `agent/tool_executor.py` | 工具调用执行功能以及代理层级的工具拦截机制 |
| `agent/prompt_builder.py` | 基于内存、技能信息、上下文文件及角色设定来构建系统提示词 |
| `agent/context_engine.py` | ContextEngine 抽象基类——支持可插拔的上下文管理方案 |
| `agent/context_compressor.py` | 默认上下文引擎——采用有损压缩算法处理上下文信息 |
| `agent/prompt_caching.py` | Anthropic 提示词缓存标记及缓存性能指标管理 |
| `agent/auxiliary_client.py` | 用于执行视觉处理、摘要生成等辅助任务的备用大语言模型客户端 |
| `model_tools.py` | 工具结构规范集合以及 `handle_function_call()` 调用分发逻辑 |

## 相关文档

- [提供程序运行时解析](./provider-runtime.md)
- [提示词构建](./prompt-assembly.md)
- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
- [工具运行时机制](./tools-runtime.md)
- [架构概览](./architecture.md)
