# Hermes Observer Hooks

Hermes observer hooks 是专为那些需要在不改变运行时行为的前提下重建代理执行过程的插件设计的只读遥测接口。该接口支持与 Trace、Metrics、Audit、Replay 以及 Export 相关的集成，例如 Langfuse、OpenTelemetry 风格的收集器以及 NeMo Relay。

Observer hooks 被刻意设计为与后端实现无关。它们会提供稳定的生命周期事件、关联 ID、经过安全处理的负载数据、时间信息、状态值以及错误信息。不过，它们并不会替代 Hermes 的规划器、模型提供器、内存管理机制、工具注册系统、审批用户界面、CLI 命令行工具、网关行为或执行语义。

任何会改变行为的需求处理逻辑或执行封装代码均不属于该 observer 接口的范畴。Observer hooks 的职责仅限于记录所发生的情况，而不应替代提供者的请求、工具参数或执行回调函数。

## 接口规范

插件需在 `register(ctx)` 方法中注册对应的 observer 回调函数：

```python
def register(ctx):
    ctx.register_hook("pre_api_request", on_pre_api_request)
    ctx.register_hook("post_api_request", on_post_api_request)
    ctx.register_hook("pre_tool_call", on_pre_tool_call)
    ctx.register_hook("post_tool_call", on_post_tool_call)
```

每个钩子回调函数都会接收关键字参数。为确保新增字段仍能保持向后兼容性，插件应接受 `**kwargs` 参数。

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

钩子回调采用“故障自动恢复”机制。Hermes 会捕获回调异常，记录警告信息，同时确保代理循环继续运行。

大多数观察者钩子的返回值会被忽略。只有以下那些会影响行为的旧版钩子才会抛出异常：

| 钩子 | 返回行为 |
| --- | --- |
| `pre_llm_call` | 可以返回字符串或 `{"context": "..."}`，以便将临时上下文注入当前用户消息中。 |
| `pre_tool_call` | 可以返回 `{"action": "block", "message": "..."}`，从而在工具执行前阻止其运行。 |
| `transform_tool_result` | 可以在 `post_tool_call` 之后返回替换后的工具结果字符串。 |
| `transform_llm_output` | 可以返回替换后的最终助手文本字符串。 |

遥测插件应将这些会影响行为的返回值视为可选的兼容性功能，而非必须满足的观测要求。

## 关联 ID

观察者负载数据使用稳定 ID，这样插件便无需仅依赖回调顺序即可将事件关联起来。

| 字段 | 含义 |
| --- | --- |
| `session_id` | 对话/会话的唯一标识。 |
| `task_id` | 任务唯一标识，对于子代理及独立执行场景尤为有用。 |
| `turn_id` | 当前轮次中 API 调用与工具调用所共用的用户轮次标识。 |
| `api_request_id` | 提供商的请求尝试匿名标识，不建议解析其字符串格式。 |
| `api_call_count` | 代理循环内的 API 尝试次数。 |
| `tool_call_id` | 如有提供，则为供应商提供的工具调用 ID。 |
| `parent_session_id` / `child_session_id` | 被委托子代理的会话关联标识。 |
| `parent_subagent_id` / `child_subagent_id` | 如有提供，即为子代理的关联标识。 |
| `parent_turn_id` | 生成被委托任务的父轮次标识。 |

消费者应优先使用明确的字段，而非尝试解析复合型 ID。尤其是 `api_request_id`，它属于一种不可见的关联值。

## 事件类型

### 会话生命周期

会话钩子用于描述对话的边界及重置场景：

| 钩子 | 触发时机 |
| --- | --- |
| `on_session_start` | 在系统提示语生成后，当有一个全新会话开始时触发。 |
| `on_session_end` | 当执行 `run_conversation` 调用结束时触发，包括被中断或未完成的轮次。 |
| `on_session_finalize` | 当 CLI 或网关终止某个活跃的会话标识时触发。 |
| `on_session_reset` | 当 CLI 或网关从旧会话标识切换到新会话标识时触发。 |

常见字段包括 `session_id`、`completed`、`interrupted`、`reason`，以及可选的 `old_session_id` 和 `new_session_id`。

`on_session_end` 是针对特定轮次/执行的，它并非对话标识整个生命周期的最终边界。对于那些必须每个会话标识执行一次的生命周期清理操作，应使用 `on_session_finalize` 和 `on_session_reset`。

### 轮次级别的 LLM 钩子

这些钩子用于描述用户轮次的整体情况，而非单个供应商 API 调用：

| 钩子 | 触发时机 |
| --- | --- |
| `pre_llm_call` | 在用户轮次的工具循环开始之前触发。 |
| `post_llm_call` | 在该轮次完成并生成最终助手输出之后触发。 |

`pre_llm_call` 的常见字段包括 `session_id`、`turn_id`、`user_message`、`conversation_history`、`is_first_turn`、`model`、`platform` 和 `sender_id`。

`post_llm_call` 的常见字段包括 `session_id`、`turn_id`、`user_message`、`assistant_response`、`conversation_history`、`model` 和 `platform`。

对于 LLM 耗时遥测，应使用请求级别的 API 钩子；而用于轮次级上下文、兼容性检测以及最终轮次总结，则应使用 `pre_llm_call` 和 `post_llm_call`。

### 请求级别的 API 钩子

API 钩子用于描述代理循环内的供应商请求操作：

| 钩子 | 触发时机 |
| --- | --- |
| `pre_api_request` | 在发起供应商 API 请求之前立即触发。 |
| `post_api_request` | 在收到供应商的成功响应之后触发。 |
| `api_request_error` | 在供应商请求失败或进入可重试错误处理流程之后触发。 |

`pre_api_request` 包含以下内容：

- 身份信息：`session_id`、`task_id`、`turn_id`、`api_request_id`
- 运行时信息：`platform`、`model`、`provider`、`base_url`、`api_mode`
- 尝试元数据：`api_call_count`、`message_count`、`tool_count`、`approx_input_tokens`、`request_char_count`、`max_tokens`
- 时间信息：`started_at`
- 已过滤的请求负载：`request`

`post_api_request` 包含相同的身份/运行时字段，此外还包含：

- `api_duration`、`started_at`、`ended_at`
- `finish_reason`、`message_count`、`response_model`
- `usage`
- `assistant_content_chars`、`assistant_tool_call_count`
- 已过滤的响应负载：`response`
- 兼容性对象：`assistant_message`

`api_request_error` 包含相同的身份/运行时字段，此外还包含：

- `api_duration`、`started_at`、`ended_at`
- `status_code`、`retry_count`、`max_retries`、`retryable`、`reason`
- 结构化的错误信息：`error = {"type": ..., "message": ...}`
- 已过滤的失败请求负载：`request`

经过过滤的 `request`、`response` 和 `error` 字段是面向新消费者的标准观察者输入数据。

### 工具生命周期

工具钩子用于描述单个工具调用：

| 钩子 | 触发时机 |
| --- | --- |
| `pre_tool_call` | 在通过安全检查后派发工具之前触发。 |
| `post_tool_call` | 在工具被派发、取消、阻止或因错误而处理完成之后触发。 |
| `transform_tool_result` | 在 `post_tool_call` 之后、结果被添加到模型上下文中之前触发。 |

`pre_tool_call` 包含 `tool_name`、`args`、`task_id`、`session_id`、`tool_call_id`、`turn_id` 和 `api_request_id`。

`post_tool_call` 包含相同的身份字段，此外还包含 `result`、`duration_ms`、`status`、`error_type` 和 `error_message`。

`status` 是观察者层面定义的生命周期结果。常见值包括：

| 状态 | 含义 |
| --- | --- |
| `ok` | 工具正常完成执行。 |
| `error` | 工具运行后返回了错误结果或引发了错误。 |
| `blocked` | 由于 `pre_tool_call` 钩子的阻止而未执行。 |
| `cancelled` | 在正常完成之前就取消了执行。 |

对于被阻止或取消的执行路径，也会触发 `post_tool_call`，以便遥测插件能够正确结束对应的测量周期。

### 审批生命周期

审批钩子用于描述危险命令的审批提示流程：

| 钩子 | 触发时机 |
| --- | --- |
| `pre_approval_request` | 在显示或发送审批请求之前触发。 |
| `post_approval_response` | 在用户作出响应或请求超时之后触发。 |

常见字段包括 `command`、`description`、`pattern_key`、`pattern_keys`、`session_key` 和 `surface`。

`post_approval_response` 还包含 `choice` 字段，其取值可能为 `once`、`session`、`always`、`deny` 和 `timeout`。

审批钩子仅供观察者使用。插件无法通过这些钩子提前答复或否决审批请求。若希望防止某个工具进入审批流程，应使用 `pre_tool_call` 进行阻止。

### 子代理生命周期

子代理钩子用于描述被委托的子代理任务：

| 钩子 | 触发时机 |
| --- | --- |
| `subagent_start` | 当有一个被委托的子代理被创建时触发。 |
| `subagent_stop` | 当被委托的子代理返回结果或执行失败时触发。 |

`subagent_start` 的字段包括 `parent_session_id`、`parent_turn_id`、`parent_subagent_id`、`child_session_id`、`child_subagent_id`、`child_role` 和 `child_goal`。

`subagent_stop` 的字段包括父子会话 ID、角色/状态字段、`child_summary` 以及 `duration_ms`。

观察者可以利用这些钩子来构建嵌套的流程模型，同时确保子代理的执行与创建它的父轮次保持关联。

## 负载数据安全性

观察者负载数据是为遥测消费者设计的，而非用于直接访问原始对象。新消费者应使用经过过滤的 API 负载数据：

- `pre_api_request.request`
- `post_api_request.response`
- `api_request_error.request`
- `api_request_error.error`

过滤处理会将供应商提供的对象转换为符合 JSON 格式的结构，限制大型负载数据的大小，隐藏敏感键值，并避免在过滤后的字段中暴露原始响应对象。

对于现有的插件，可能仍会存在 `request_messages`、`conversation_history` 和 `assistant_message` 等旧版兼容性字段。新的观测功能消费者应优先使用经过过滤的负载数据。

## 性能优化

默认的未添加性能监控的路径应保持低开销。复杂的请求/响应负载数据构建操作会被 `has_hook()` 函数控制，因此只有当至少有一个插件注册了相关钩子时，Hermes 才会生成经过过滤的 API 遥测负载数据。

插件开发者应保持这一特性：

- 仅注册插件实际使用的钩子。
- 避免对已经过过滤的负载数据再次进行深度复制或重新过滤处理。
- 确保钩子回调的执行速度较快，并采用“故障自动恢复”机制。
- 在条件允许的情况下，将网络导出或批量写入操作移至后台处理。

## 编写观察者插件

最简单的观察者插件：

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

若需进行跨度关联，可使用 `session_id`、`turn_id`、`api_request_id` 以及 `tool_call_id`。当导出格式支持嵌套代理任务或安全生命周期事件时，则可利用子代理与审批钩子功能。

## 现有使用者

随附的 Langfuse 插件为对话轮次、服务提供方请求及工具调用提供了基于钩子的直接可观测性支持。

随附的 NeMo Relay 插件则将相同的通用观察者接口映射到 NeMo Relay 的作用域、大语言模型跨度、工具跨度、标记、ATOF 流以及 ATIF 导出数据上。与 NeMo Relay 相关的配置及示例可见于 [`plugins/observability/nemo_relay/README.md`](../../plugins/observability/nemo_relay/README.md) 文件。
