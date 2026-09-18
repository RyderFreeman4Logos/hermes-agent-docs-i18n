# Hermes Observer Hooks

Hermes observer hooks 是专为那些需要在不改变运行时行为的前提下重建代理执行过程的插件设计的只读遥测接口。该接口支持与 Langfuse、OpenTelemetry 风格的收集器以及 NeMo Relay 等工具进行轨迹追踪、指标收集、审计记录、回放以及数据导出等功能集成。

Observer hooks 被刻意设计为与后端实现无关。它们会提供稳定的生命周期事件、关联 ID、经过安全处理的负载数据、时间信息、状态值以及错误信息等字段。不过，它们并不会替代 Hermes 的规划器、模型提供器、内存管理机制、工具注册系统、审批用户界面、命令行接口、网关行为或执行语义。

任何会改变行为的请求处理逻辑或执行封装代码均不属于该 observer 接口的范围。Observer hooks 的职责仅限于记录所发生的情况，而不应替代提供者的请求、工具参数或执行回调函数。

Hermes 还自带一个基于 NeMo Relay 的原生共享指标机制，该机制直接利用上述生命周期边界，无需额外启用任何可观测性插件。详情请参阅 [Relay shared metrics](relay-shared-metrics.md) 文档。

## 接口规范

插件需在 `register(ctx)` 方法中注册 observer 回调函数：

```python
def register(ctx):
    ctx.register_hook("pre_api_request", on_pre_api_request)
    ctx.register_hook("post_api_request", on_post_api_request)
    ctx.register_hook("pre_tool_call", on_pre_tool_call)
    ctx.register_hook("post_tool_call", on_post_tool_call)
```

每个钩子回调函数都会接收关键字参数。为确保新增字段仍具备向后兼容性，插件应接受 `**kwargs` 参数。

```python
def on_post_tool_call(**kwargs):
    tool_name = kwargs.get("tool_name")
    status = kwargs.get("status")
    result = kwargs.get("result")
```

插件管理器会将此字段注入到每个钩子函数的负载中：

```text
telemetry_schema_version = "hermes.observer.v1"
```

钩子回调采用“故障即继续”机制。Hermes 会捕获回调异常并记录警告，同时确保代理循环持续运行。

大多数观察者钩子的返回值都会被忽略。只有那些会影响行为的旧版钩子才会抛出异常：

| 钩子 | 返回行为 |
| --- | --- |
| `pre_llm_call` | 可以返回字符串或 `{"context": "..."}`，以便将临时上下文注入当前用户消息中。 |
| `pre_tool_call` | 可以返回 `{"action": "block", "message": "..."}` 以在工具执行前阻止其运行，或返回 `{"action": "modify", "args": {...}}` 以修改工具的输入参数。 |
| `transform_tool_result` | 可以在 `post_tool_call` 之后返回替换后的工具结果字符串。 |
| `transform_llm_output` | 可以返回替换后的最终助手回复文本字符串。 |

遥测插件应将这些会影响行为的返回值视为可选的兼容性功能，而非必须满足的可观测性要求。

## 关联 ID

观察者数据包使用稳定 ID，这样插件便无需仅依赖回调顺序即可将不同事件关联起来。

| 字段 | 含义 |
| --- | --- |
| `session_id` | 对话/会话的唯一标识。 |
| `task_id` | 任务唯一标识，尤其适用于子智能体及独立执行场景。 |
| `turn_id` | 当前轮次中 API 调用与工具调用所共用的用户轮次标识。 |
| `api_request_id` | 提供商层面的 API 请求唯一标识，其字符串格式不可解析。 |
| `api_call_count` | 智能体循环过程中的 API 请求次数。 |
| `tool_call_id` | 如有提供，为供应商生成的工具调用编号。 |
| `parent_session_id` / `child_session_id` | 用于关联被委托任务的子会话的标识。 |
| `parent_subagent_id` / `child_subagent_id` | 如有提供，用于关联子智能体的标识。 |
| `parent_turn_id` | 触发任务委托的父轮次标识。 |

客户端应优先使用明确的字段，而非尝试解析复合型标识。尤其是 `api_request_id`，属于不可识别的关联值。

## 事件类型

### 会话生命周期

会话钩子用于定义对话的边界及触发重置操作：

| 钩子 | 触发时机 |
| --- | --- |
| `on_session_start` | 在系统提示语生成后，开启全新的会话时触发。 |
| `on_session_end` | 执行 `run_conversation` 调用结束时触发，包括被中断或未完成的轮次。 |
| `on_session_finalize` | CLI 或网关终止当前活跃的会话标识时触发。 |
| `on_session_reset` | CLI 或网关从旧会话标识切换到新会话标识时触发。 |

常见的字段包括 `session_id`、`completed`、`interrupted`、`reason`，以及可选的 `old_session_id` 和 `new_session_id`。

`on_session_end` 是以轮次/运行为范围的钩子，它并不一定是每个聊天身份的最终生命周期边界。对于那些必须在每个聊天身份对应的会话中仅执行一次的生命周期清理操作，请使用 `on_session_finalize` 和 `on_session_reset`。

### 轮次范围的 LLM 钩子

这类钩子用于处理用户的完整轮次，而非单个提供商 API 调用：

| 钩子 | 触发时机 |
| --- | --- |
| `pre_llm_call` | 在用户轮次的工具调用循环开始之前。 |
| `post_llm_call` | 在该轮次结束并生成助手最终回复之后。 |

`pre_llm_call` 中常见的字段包括 `session_id`、`turn_id`、`user_message`、`conversation_history`、`is_first_turn`、`model`、`platform` 以及 `sender_id`。

`post_llm_call` 中常见的字段包括 `session_id`、`turn_id`、`user_message`、`assistant_response`、`conversation_history`、`model` 以及 `platform`。

若需监控 LLM 的整个处理过程，请使用以请求为范围的 API 钩子；而若需要获取轮次级别的上下文信息、确保兼容性或生成该轮次的总结，则应使用 `pre_llm_call` 和 `post_llm_call`。

### 请求范围的 API 钩子

这类 API 钩子用于描述在智能体循环内部发生的提供商 API 调用：

| 钩子 | 触发时机 |
| --- | --- |
| `pre_api_request` | 在发起提供商 API 请求之前立即触发。 |
| `post_api_request` | 在提供商返回成功响应之后触发。 |
| `api_request_error` | 在提供商请求失败或出现可重试的错误时触发。 |

`pre_api_request` 中包含的内容有：

- 身份标识：`session_id`、`task_id`、`turn_id`、`api_request_id`  
- 运行环境：`platform`、`model`、`provider`、`base_url`、`api_mode`  
- 尝试元数据：`api_call_count`、`message_count`、`tool_count`、  
  `approx_input_tokens`、`request_char_count`、`max_tokens`  
- 时间信息：`started_at`  
- 已过滤的请求载荷：`request`  

`post_api_request` 包含上述相同的身份/运行环境字段，此外还包含：  

- `api_duration`、`started_at`、`ended_at`  
- `finish_reason`、`message_count`、`response_model`  
- `usage`  
- `assistant_content_chars`、`assistant_tool_call_count`  
- 已过滤的响应载荷：`response`  
- 兼容性对象：`assistant_message`  

`api_request_error` 包含上述相同的身份/运行环境字段，此外还包含：  

- `api_duration`、`started_at`、`ended_at`  
- `status_code`、`retry_count`、`max_retries`、`retryable`、`reason`  
- 结构化的错误信息 `error = {"type": ..., "message": ...}`  
- 已过滤的失败请求载荷：`request`  

经过过滤后的 `request`、`response` 和 `error` 字段是为新使用者提供的标准输入数据。  

### 工具生命周期  

工具钩子用于描述具体的工具调用行为：  

| 钩子名称 | 触发时机 |
| --- | --- |
| `pre_tool_call` | 在通过安全规则审核的工具被调用之前触发。 |
| `post_tool_call` | 在工具调用完成、被取消、被阻止或出现错误后触发。 |
| `transform_tool_result` | 在 `post_tool_call` 之后、结果被添加到模型上下文之前触发。 |

`pre_tool_call` 包含 `tool_name`、`args`、`task_id`、`session_id`、  
`tool_call_id`、`turn_id` 和 `api_request_id` 等字段。

`post_tool_call` 除了包含相同的身份字段外，还包含 `result`、`duration_ms`、`status`、`error_type` 以及 `error_message` 这些字段。

`status` 表示工具执行后的生命周期状态。常见值包括：

| 状态 | 含义 |
| --- | --- |
| `ok` | 工具正常完成执行。 |
| `error` | 工具运行后返回了错误结果或引发了异常。 |
| `blocked` | 有 `pre_tool_call` 钩子阻止了执行。 |
| `cancelled` | 执行在正常完成之前被取消。 |

对于被阻止或已取消的执行路径，系统也会触发 `post_tool_call`，以便遥测插件能够正确地结束相关时间跨度记录。

### 审批生命周期

审批钩子用于处理危险命令的审批提示：

| 钩子 | 触发时机 |
| --- | --- |
| `pre_approval_request` | 在显示或发送审批请求之前。 |
| `post_approval_response` | 用户作出响应或请求超时之后。 |

这些钩子常见的字段包括 `command`、`description`、`pattern_key`、`pattern_keys`、`session_key` 以及 `surface`。

`post_approval_response` 还包含 `choice` 字段，其取值可能为 `once`、`session`、`always`、`deny` 和 `timeout` 等。

审批钩子仅具备观察功能，插件无法通过这些钩子预先答复或否决审批请求。若希望阻止工具进入审批流程，可使用 `pre_tool_call` 钩子进行拦截。

### 子代理生命周期

子代理钩子用于描述分配给子代理的任务执行情况：

| 钩子 | 触发时机 |
| --- | --- |
| `subagent_start` | 有子代理被创建并开始工作。 |
| `subagent_stop` | 被分配的子代理返回结果或执行失败。 |
`subagent_start`字段包括`parent_session_id`、`parent_turn_id`、`parent_subagent_id`、`child_session_id`、`child_subagent_id`、`child_role`以及`child_goal`。

`subagent_stop`字段则包含父子会话ID、角色/状态信息、`child_summary`、执行时长`duration_ms`，以及仅包含元数据的`tool_call_history`。每条历史记录都会记载工具名称、参数名称、受限制的副作用目标、输入/输出字节数量以及执行结果。URL查询字符串和片段会被移除，同时故意不包含原始参数、提示语、命令、内容、头部信息及结果数据。

观察者可通过这些接口来构建嵌套式任务流程，同时确保子智能体的执行与生成它的父轮次保持关联。

## 载荷安全性

观察者载荷是为遥测数据接收方设计的，而非用于直接访问原始对象。新的数据接收方应使用经过安全处理的API载荷：

- `pre_api_request.request`
- `post_api_request.response`
- `api_request_error.request`
- `api_request_error.error`

此类安全处理机制会将提供方对象转换为符合JSON格式的结构，限制大型载荷的尺寸，隐藏敏感键值，并避免在处理后的字段中暴露原始响应对象。

对于现有的插件，可能仍会保留`request_messages`、`conversation_history`和`assistant_message`等旧版兼容字段。新的可观测性数据接收方应优先使用经过安全处理的载荷。

## 性能表现

默认的未添加监控功能的请求路径应保持低开销。复杂的请求/响应数据载荷构建功能通过 `has_hook()` 机制进行控制，因此只有当至少有一个插件注册了相应的钩子时，Hermes 才会生成经过过滤处理的 API 监控数据载荷。

插件开发者应当遵循以下原则：

- 仅注册插件实际会使用的钩子。
- 避免对已处理过的载荷进行深度复制或再次过滤。
- 确保钩子回调的响应速度，并采用“失败即返回”策略。
- 在条件允许的情况下，将网络导出或批量写入操作交由其他组件处理。

## 编写观察者插件

最简化的观察者插件：

```python
def register(ctx):
    ctx.register_hook("pre_api_request", on_pre_api_request)
    ctx.register_hook("post_api_request", on_post_api_request)
    ctx.register_hook("pre_tool_call", on_pre_tool_call)
    ctx.register_hook("post_tool_call", on_post_tool_call)


def on_pre_api_request(**kwargs):
    start_llm_span(
        request_id=kwargs.get("api_request_id"),
        turn_id=kwargs.get("turn_id"),
        request=kwargs.get("request"),
        model=kwargs.get("model"),
    )


def on_post_api_request(**kwargs):
    finish_llm_span(
        request_id=kwargs.get("api_request_id"),
        response=kwargs.get("response"),
        usage=kwargs.get("usage"),
        duration=kwargs.get("api_duration"),
    )


def on_pre_tool_call(**kwargs):
    start_tool_span(
        call_id=kwargs.get("tool_call_id"),
        name=kwargs.get("tool_name"),
        args=kwargs.get("args"),
    )


def on_post_tool_call(**kwargs):
    finish_tool_span(
        call_id=kwargs.get("tool_call_id"),
        result=kwargs.get("result"),
        status=kwargs.get("status"),
        duration_ms=kwargs.get("duration_ms"),
    )
```

若需实现跨时间段的链路关联，可使用 `session_id`、`turn_id`、`api_request_id` 以及 `tool_call_id`。当导出格式支持嵌套代理任务或安全生命周期事件时，可利用子代理与审批钩子功能。

## 现有用户案例

预装的 Langfuse 插件可直接通过钩子机制实现对对话轮次、服务提供方请求以及工具调用的可观测性监控。

原生的 NeMo Relay SDK 集成则可将 Hermes 的会话、对话轮次、大语言模型及工具的整个生命周期映射到 Relay 系统中。通过显式的 Relay 插件配置，还可添加 [ATOF、ATIF 或 OTEL](https://docs.nvidia.com/nemo/relay/configure-plugins/observability/about) 导出工具以及执行中间件；相关详情请参阅 [Relay 共享指标文档](relay-shared-metrics.md)。
