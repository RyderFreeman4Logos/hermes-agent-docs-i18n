---
sidebar_position: 3
title: "Agent Loop Internals"
description: "Detailed walkthrough of AIAgent execution, API modes, tools, callbacks, and fallback behavior"
---

# Agent循环内部机制

核心调度引擎为`run_agent.py`中的`AIAgent`类——这是一个体积庞大的文件，负责处理从提示词构建、工具调用到提供者故障切换等所有任务。

## 核心职责

`AIAgent`的主要职责包括：

- 通过`prompt_builder.py`整合有效的系统提示词及工具结构定义
- 选择合适的提供者/API模式（chat_completions、codex_responses、anthropic_messages）
- 支持取消功能的可中断模型调用
- 执行工具调用（顺序执行或通过线程池并发执行）
- 以OpenAI消息格式维护对话历史
- 处理数据压缩、重试机制以及备用模型切换
- 跟踪父子Agent之间的迭代次数限制
- 在上下文丢失前清空持久内存

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

`chat()` 是 `run_conversation()` 的简化封装版本，它负责从返回结果字典中提取 `final_response` 字段。

## API 模式

Hermes 支持三种 API 执行模式，这些模式的确定依据包括所选的提供商、显式参数以及基础 URL 的特征分析：

| API 模式 | 适用场景 | 客户端类型 |
|----------|----------|-------------|
| `chat_completions` | 兼容 OpenAI 的接口（OpenRouter、自定义接口及大多数提供商） | `openai.OpenAI` |
| `codex_responses` | OpenAI Codex / Responses API | 使用 Responses 格式的 `openai.OpenAI` |
| `anthropic_messages` | 原生的 Anthropic Messages API | 通过适配器实现的 `anthropic.Anthropic` |

不同的 API 模式决定了消息的格式、工具调用的结构、响应的解析方式以及缓存/流式处理的机制。在发起 API 调用之前和之后，这三种模式最终都会转换为相同的内部消息格式（即 OpenAI 风格的 `role`/`content`/`tool_calls` 字典）。

**模式确定顺序：**
1. 显式的 `api_mode` 构造函数参数（优先级最高）
2. 根据提供商特性判断（例如，使用 `anthropic` 提供商则对应 `anthropic_messages` 模式）
3. 基于基础 URL 的特征分析（例如，URL 为 `api.anthropic.com` 则对应 `anthropic_messages` 模式）
4. 默认模式：`chat_completions`

## 对话轮生命周期

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

推理内容（来自具备扩展思维能力的模型）会存储在 `assistant_msg["reasoning"]` 中，也可通过 `reasoning_callback` 选项进行展示。

### 消息轮换规则

Agent 循环会强制执行严格的消息角色轮换规则：

- 系统消息之后：`用户 → 助手 → 用户 → 助手 → ...`
- 调用工具时：`助手（包含 tool_calls）→ 工具 → 工具 → ... → 助手`
- **严禁**连续出现两条助手消息
- **严禁**连续出现两条用户消息
- **仅允许** `tool` 角色的消息连续出现（即并行工具处理结果）

Provider 会验证这些消息序列，若发现格式错误的对话历史将予以拒绝。

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

当被中断时（用户发送新消息、执行 `/stop` 命令或发送信号）：
- API 线程将被终止（对应响应会被丢弃）
- 智能体可以选择处理新的输入，或干净地关闭
- 不会将有遗漏的响应插入对话历史中

## 工具执行

### 顺序执行与并发执行

当模型返回工具调用请求时：
- **单次工具调用** → 直接在主线程中执行
- **多次工具调用** → 通过 `ThreadPoolExecutor` 实现并发执行
  - 注意：被标记为交互式工具的调用（例如 `clarify`）将强制采用顺序执行方式
  - 不管实际执行顺序如何，结果都会按照最初的工具调用顺序重新排列

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

某些工具会在被传递到`handle_function_call()`之前，就被`run_agent.py`拦截：

| 工具 | 拦截原因 |
|------|----------|
| `todo` | 用于读取/写入代理本地的任务状态 |
| `memory` | 向存在字符长度限制的持久化内存文件写入数据 |
| `session_search` | 通过代理的会话数据库查询会话历史记录 |
| `delegate_task` | 创建具有独立上下文的子代理 |

这些工具会直接修改代理状态，并在不经过注册表的情况下返回模拟的工具结果。

## 回调接口

`AIAgent`支持特定平台的回调功能，可在CLI、网关及ACP集成中实现实时进度显示：

| 回调函数 | 触发时机 | 使用方 |
|----------|----------|-------|
| `tool_progress_callback` | 每次工具执行前后 | CLI加载指示器、网关进度消息 |
| `thinking_callback` | 模型开始/停止思考时 | CLI“正在思考...”提示 |
| `reasoning_callback` | 模型返回推理内容时 | CLI推理结果展示、网关推理模块 |
| `clarify_callback` | 调用`clarify`工具时 | CLI输入提示、网关交互式消息 |
| `step_callback` | 每次代理轮次结束后 | 网关步骤跟踪、ACP进度显示 |
| `stream_delta_callback` | 每个流式数据单元处理时（如已启用） | CLI流式数据展示 |
| `tool_gen_callback` | 从流式数据中解析出工具调用时 | CLI工具预览界面 |
| `status_callback` | 状态发生变化时（如思考中、执行中等） | ACP状态更新 |

## 预算与回退机制

### 迭代预算

代理通过`IterationBudget`来跟踪迭代次数：

- 默认值：90次迭代（可通过`agent.max_turns`参数配置）
- 每个代理拥有独立的预算额度。子代理也有独立的预算，其上限为`delegation.max_iterations`（默认为50次）——父代理与所有子代理的迭代次数总和可超过父代理的限额
- 当迭代次数达到100%时，代理将停止运行并返回工作完成总结

### 回退模型

当主模型出现故障时（如429限流、5xx服务器错误、401/403认证错误），系统会按以下步骤处理：

1. 检查配置文件中的`fallback_providers`列表
2. 按顺序尝试每个备选模型
3. 若某备选模型成功，则继续使用该模型进行对话
4. 若遇到401/403认证错误，会先尝试刷新凭证，再切换到其他模型

此外，回退机制也独立适用于各类辅助任务——视觉处理、数据压缩和网页提取等功能均拥有各自的回退流程，可通过`auxiliary.*`配置项进行自定义设置。

## 数据压缩与持久化

### 何时触发压缩

- **预请求阶段**（在API调用之前）：当对话内容占模型上下文窗口容量的50%以上时
- **网关自动压缩**：当对话内容占比超过85%时（该机制更为激进，会在各轮对话之间自动执行）

### 压缩过程中的处理方式

1. 首先将内存数据刷新到磁盘，以避免数据丢失
2. 对中间阶段的对话内容进行简洁总结
3. 保留最后N条消息的原貌（通过`compression.protect_last_n`参数控制，默认为20条）
4. 工具调用与结果消息会保持在一起，不会被拆分
5. 会生成一个新的会话链路ID——压缩操作实际上会创建一个“子会话”

### 会话持久化

每次对话轮次结束后，系统会执行以下操作：

- 将对话内容保存到会话存储中（通过`hermes_state.py`使用SQLite数据库）
- 将内存中的更改同步到`MEMORY.md`和`USER.md`文件
- 后续可通过`/resume`命令或`hermes chat --resume`选项恢复该会话

## 核心源代码文件

| 文件 | 功能说明 |
|------|----------|
| `run_agent.py` | AIAgent类——完整的代理运行循环实现 |
| `agent/prompt_builder.py` | 从内存、技能、上下文文件及个性设置中组装系统提示词 |
| `agent/context_engine.py` | ContextEngine抽象基类——支持可插拔的上下文管理机制 |
| `agent/context_compressor.py` | 默认上下文压缩引擎——基于有损总结算法的实现 |
| `agent/prompt_caching.py` | 负责Anthropic提示词的缓存标记及缓存性能统计 |
| `agent/auxiliary_client.py` | 用于处理视觉处理、内容总结等辅助任务的LLM客户端 |
| `model_tools.py` | 工具架构定义集合以及`handle_function_call()`函数的调度逻辑 |

## 相关文档

- [提供程序运行时解析](./provider-runtime.md)
- [提示词组装机制](./prompt-assembly.md)
- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
- [工具运行时机制](./tools-runtime.md)
- [架构概览](./architecture.md)
