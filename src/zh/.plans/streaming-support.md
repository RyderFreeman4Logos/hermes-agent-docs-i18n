# Hermes Agent 的 LLM 响应流式输出支持

## 概述

该功能为所有平台添加了逐词流式输出 LLM 响应的能力。启用后，用户将看到响应实时生成，而无需等待完整内容生成完毕。流式输出通过配置选项开启，默认处于关闭状态，同时所有现有的非流式代码路径仍将保持原有功能。

## 设计原则

1. **特性开关控制**：通过 config.yaml 中的 `streaming.enabled: true` 来启用该功能，默认值为关闭。关闭时，所有现有代码路径均不受影响，不会对当前功能造成任何风险。
2. **基于回调机制**：只需在 AIAgent 中注入一个简单的 `stream_callback(text_delta: str)` 函数即可。Agent 不需要也不关心接收方如何处理这些生成的文本片段。
3. **平滑降级处理**：如果对应 Provider 不支持流式输出，或流式输出因任何原因失败，系统会自动无缝切换回非流式处理路径。
4. **跨平台通用核心**：无论调用方是 CLI、Telegram、Discord 还是 API 服务器，AIAgent 中的流式输出机制都能保持一致的工作方式。

---

## 架构

```
                              stream_callback(delta)
                                    │
  ┌─────────────┐    ┌─────────────▼──────────────┐
  │  LLM API    │    │      queue.Queue()          │
  │  (stream)   │───►│  thread-safe bridge between │
  │             │    │  agent thread & consumer    │
  └─────────────┘    └─────────────┬──────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
              ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
              │    CLI     │ │  Gateway  │ │ API Server│
              │ print to   │ │ edit msg  │ │ SSE event │
              │ terminal   │ │ on Tg/Dc  │ │ to client │
              └───────────┘ └───────────┘ └───────────┘
```

该代理在单个线程中运行。回调函数会将令牌放入一个线程安全的队列中。
每个消费者都在其自身的上下文环境中读取该队列（异步任务、主线程等）。

---

## 配置

### config.yaml

```yaml
streaming:
  enabled: false          # Master switch. Default off.
  # Per-platform overrides (optional):
  # cli: true             # Override for CLI only
  # telegram: true        # Override for Telegram only
  # discord: false        # Keep Discord non-streaming
  # api_server: true      # Override for API server
```

### 环境变量

```
HERMES_STREAMING_ENABLED=true    # Master switch via env
```

### 标志值的读取方式

- **CLI**：`load_cli_config()`函数会读取`streaming.enabled`的值并设置环境变量，AIAgent在启动时会检查该变量。
- **Gateway**：`_run_agent()`函数会读取配置文件，然后决定是否将`stream_callback`参数传递给AIAgent的构造函数。
- **API服务器**：对于那些在请求中明确指定`stream=true`的聊天补全类请求，无论配置如何都会启用流式处理（因为这是客户端主动要求的）；而对于非流式请求，则会按照配置来处理。

### 优先级规则

1. **API服务器**：客户端的`stream`字段具有最高优先级，可覆盖其他所有设置。
2. **平台特定配置覆盖**（例如`streaming.telegram: true`）。
3. **全局`streaming.enabled`标志**。
4. **默认值**：关闭。

---

## 实施计划

### 第一阶段：在AIAgent中构建核心流式处理基础设施

**文件路径**：`run_agent.py`

#### 1a. 在__init__方法中添加`stream_callback`参数（约5行代码）

```python
def __init__(self, ..., stream_callback: callable = None, ...):
    self.stream_callback = stream_callback
```

其他初始化设置无需更改。该回调函数为可选项——若设置为 None，则所有功能将保持与之前完全一致。

#### 1b. 添加 _run_streaming_chat_completion() 方法（约 65 行代码）

用于 Chat Completions API 流式处理的新增方法：

```python
def _run_streaming_chat_completion(self, api_kwargs: dict):
    """Stream a chat completion, emitting text tokens via stream_callback.
    
    Returns a fake response object compatible with the non-streaming code path.
    Falls back to non-streaming on any error.
    """
    stream_kwargs = dict(api_kwargs)
    stream_kwargs["stream"] = True
    stream_kwargs["stream_options"] = {"include_usage": True}
    
    accumulated_content = []
    accumulated_tool_calls = {}  # index -> {id, name, arguments}
    final_usage = None
    
    try:
        stream = self.client.chat.completions.create(**stream_kwargs)
        
        for chunk in stream:
            if not chunk.choices:
                # Usage-only chunk (final)
                if chunk.usage:
                    final_usage = chunk.usage
                continue
            
            delta = chunk.choices[0].delta
            
            # Text content — emit via callback
            if delta.content:
                accumulated_content.append(delta.content)
                if self.stream_callback:
                    try:
                        self.stream_callback(delta.content)
                    except Exception:
                        pass
            
            # Tool call deltas — accumulate silently
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in accumulated_tool_calls:
                        accumulated_tool_calls[idx] = {
                            "id": tc_delta.id or "",
                            "name": "", "arguments": ""
                        }
                    if tc_delta.function:
                        if tc_delta.function.name:
                            accumulated_tool_calls[idx]["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            accumulated_tool_calls[idx]["arguments"] += tc_delta.function.arguments
        
        # Build fake response compatible with existing code
        tool_calls = []
        for idx in sorted(accumulated_tool_calls):
            tc = accumulated_tool_calls[idx]
            if tc["name"]:
                tool_calls.append(SimpleNamespace(
                    id=tc["id"], type="function",
                    function=SimpleNamespace(name=tc["name"], arguments=tc["arguments"]),
                ))
        
        return SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(
                    content="".join(accumulated_content) or "",
                    tool_calls=tool_calls or None,
                    role="assistant",
                ),
                finish_reason="tool_calls" if tool_calls else "stop",
            )],
            usage=final_usage,
            model=self.model,
        )
    
    except Exception as e:
        logger.debug("Streaming failed, falling back to non-streaming: %s", e)
        return self.client.chat.completions.create(**api_kwargs)
```

#### 1c. 修改 Responses API 的_run_codex_stream() 方法（约10行代码）

该方法已会对数据流进行遍历。需在此基础上添加回调函数调用逻辑：

```python
def _run_codex_stream(self, api_kwargs: dict):
    with self.client.responses.stream(**api_kwargs) as stream:
        for event in stream:
            # Emit text deltas if streaming callback is set
            if self.stream_callback and hasattr(event, 'type'):
                if event.type == 'response.output_text.delta':
                    try:
                        self.stream_callback(event.delta)
                    except Exception:
                        pass
        return stream.get_final_response()
```

#### 1d. 修改 _interruptible_api_call()（约5行）

添加流式处理分支：

```python
def _call():
    try:
        if self.api_mode == "codex_responses":
            result["response"] = self._run_codex_stream(api_kwargs)
        elif self.stream_callback is not None:
            result["response"] = self._run_streaming_chat_completion(api_kwargs)
        else:
            result["response"] = self.client.chat.completions.create(**api_kwargs)
    except Exception as e:
        result["error"] = e
```

#### 1e. 向消费者发送流结束信号（约5行）

在API调用返回后，需向回调函数发送流处理完毕的信号，
以便消费者能够完成最终操作（如移除光标、关闭SSE连接等）：

```python
# In run_conversation(), after _interruptible_api_call returns:
if self.stream_callback:
    try:
        self.stream_callback(None)  # None = end of stream signal
    except Exception:
        pass
```

消费者端检查逻辑：`if delta is None: finalize()`

**第一阶段测试用例：**（约150行）
- 使用模拟流数据测试 `_run_streaming_chat_completion` 函数
- 测试发生错误时自动切换为非流式处理模式
- 测试在流式处理过程中工具调用的累积情况
- 验证 `stream_callback` 能正确接收增量数据
- 测试流处理结束时返回 `None` 信号
- 测试当回调值为 `None` 时禁用流式处理功能

---

### 第二阶段：网关端消费者（Telegram、Discord等）

**文件：gateway/run.py**

#### 2a. 读取流式处理配置（约15行）

在 `_run_agent()` 函数中，创建 AIAgent 对象之前：

```python
# Read streaming config
_streaming_enabled = False
try:
    # Check per-platform override first
    platform_key = source.platform.value if source.platform else ""
    _stream_cfg = {}  # loaded from config.yaml streaming section
    if _stream_cfg.get(platform_key) is not None:
        _streaming_enabled = bool(_stream_cfg[platform_key])
    else:
        _streaming_enabled = bool(_stream_cfg.get("enabled", False))
except Exception:
    pass
# Env var override
if os.getenv("HERMES_STREAMING_ENABLED", "").lower() in ("true", "1", "yes"):
    _streaming_enabled = True
```

#### 2b. 配置队列与回调功能（约15行）

```python
_stream_q = None
_stream_done = None
_stream_msg_id = [None]  # mutable ref for the async task

if _streaming_enabled:
    import queue as _q
    _stream_q = _q.Queue()
    _stream_done = threading.Event()
    
    def _on_token(delta):
        if delta is None:
            _stream_done.set()
        else:
            _stream_q.put(delta)
```

在 AIAgent 的构造函数中传入参数 `stream_callback=_on_token`。

#### 2c. Telegram/Discord 流式预览任务（约 50 行）

```python
async def stream_preview():
    """Progressively edit a message with streaming tokens."""
    if not _stream_q:
        return
    adapter = self.adapters.get(source.platform)
    if not adapter:
        return
    
    accumulated = []
    token_count = 0
    last_edit = 0.0
    MIN_TOKENS = 20          # Don't show until enough context
    EDIT_INTERVAL = 1.5      # Respect Telegram rate limits
    
    try:
        while not _stream_done.is_set():
            try:
                chunk = _stream_q.get(timeout=0.1)
                accumulated.append(chunk)
                token_count += 1
            except queue.Empty:
                continue
            
            now = time.monotonic()
            if token_count >= MIN_TOKENS and (now - last_edit) >= EDIT_INTERVAL:
                preview = "".join(accumulated) + " ▌"
                if _stream_msg_id[0] is None:
                    r = await adapter.send(
                        chat_id=source.chat_id,
                        content=preview,
                        metadata=_thread_metadata,
                    )
                    if r.success and r.message_id:
                        _stream_msg_id[0] = r.message_id
                else:
                    await adapter.edit_message(
                        chat_id=source.chat_id,
                        message_id=_stream_msg_id[0],
                        content=preview,
                    )
                last_edit = now
        
        # Drain remaining tokens
        while not _stream_q.empty():
            accumulated.append(_stream_q.get_nowait())
        
        # Final edit — remove cursor, show complete text
        if _stream_msg_id[0] and accumulated:
            await adapter.edit_message(
                chat_id=source.chat_id,
                message_id=_stream_msg_id[0],
                content="".join(accumulated),
            )
    
    except asyncio.CancelledError:
        # Clean up on cancel
        if _stream_msg_id[0] and accumulated:
            try:
                await adapter.edit_message(
                    chat_id=source.chat_id,
                    message_id=_stream_msg_id[0],
                    content="".join(accumulated),
                )
            except Exception:
                pass
    except Exception as e:
        logger.debug("stream_preview error: %s", e)
```

#### 2d. 若已开始流式传输则跳过最终发送（约10行）

在`_process_message_background()`（base.py）函数中，获取响应后，如果处于流式传输状态且`_stream_msg_id[0]`已被设置，说明最终响应已通过分步编辑的方式送达。此时应跳过常规的`self.send()`调用，以避免重复发送消息。

这是最复杂的集成点——我们需要让网关的`_run_agent`向基础适配器的响应发送模块反馈已送达的消息。可选方案如下：

- **方案A**：在结果字典中返回一个特殊标记：
  `result["_streamed_msg_id"] = _stream_msg_id[0]`
  基础适配器检测到该标记后便跳过`send()`操作。

- **方案B**：用最终响应内容替换已发送的消息（由于思维块过滤等原因，最终响应可能与累计的文本内容略有差异），而不发送新消息。

- **方案C**：由流式预览任务处理完整的最终响应（包括任何后续处理），然后由处理程序返回`None`以跳过常规的发送流程。

推荐采用**方案A**——这种方式的分离最为清晰。结果字典本身已包含元数据，再添加一个字段风险较低。

**各平台的特殊考虑：**

| 平台       | 编辑支持情况 | 速率限制     | 流式传输方式               |
|------------|--------------|--------------|----------------------------|
| Telegram   | ✅ 可编辑消息文本 | 约20次/分钟  | 每1.5秒编辑一次             |
| Discord    | ✅ 可编辑消息 | 每条消息5次/5秒 | 每1.2秒编辑一次             |
| Slack      | ✅ 可更新聊天内容 | 第3级限制（约50次/分钟） | 每1.5秒编辑一次             |
| WhatsApp   | ❌ 不支持编辑 | 无限制       | 跳过流式传输，使用常规方式   |
| HomeAssistant | ❌ 不支持编辑 | 无限制       | 跳过流式传输               |
| API服务器   | ✅ 原生SSE支持 | 无限制       | 实时SSE事件传输             |

由于WhatsApp和HomeAssistant不支持消息编辑，因此会自动切换到非流式传输模式。

**第二阶段的测试用例**：（约100行）
- 测试流式预览功能能否正确发送/编辑消息
- 测试在流式传输已送达时是否能够跳过最终发送
- 测试WhatsApp/HomeAssistant平台的平滑降级处理
- 测试根据不同平台配置禁用流式传输的功能
- 测试流式消息中是否能正确传递`thread_id`元数据

---

### 第3阶段：CLI流式传输

**文件：cli.py**

#### 3a. 在CLI聊天循环中设置回调函数（约20行）

在`_chat_once()`函数或Agent被调用的其他位置：

```python
if streaming_enabled:
    _stream_q = queue.Queue()
    _stream_done = threading.Event()
    
    def _cli_stream_callback(delta):
        if delta is None:
            _stream_done.set()
        else:
            _stream_q.put(delta)
    
    agent.stream_callback = _cli_stream_callback
```

#### 3b. 令牌显示线程/任务（约30行）

启动一个用于读取队列并打印令牌的线程：

```python
def _stream_display():
    """Print tokens to terminal as they arrive."""
    first_token = True
    while not _stream_done.is_set():
        try:
            delta = _stream_q.get(timeout=0.1)
        except queue.Empty:
            continue
        if first_token:
            # Print response box top border
            _cprint(f"\n{top}")
            first_token = False
        sys.stdout.write(delta)
        sys.stdout.flush()
    # Drain remaining
    while not _stream_q.empty():
        sys.stdout.write(_stream_q.get_nowait())
    sys.stdout.flush()
    # Print bottom border
    _cprint(f"\n\n{bot}")
```

**集成挑战：prompt_toolkit**

该 CLI 使用了用于控制终端的 prompt_toolkit。在 prompt_toolkit 处于活跃状态时直接向 stdout 写入数据可能会导致显示异常。现有的 KawaiiSpinner 已通过使用 prompt_toolkit 的 `patch_stdout` 上下文解决了这一问题，流式显示功能也需要采用相同方式。

另一种方案是：对每个令牌块使用 `_cprint()` 函数（该函数会通过 prompt_toolkit 的渲染器处理数据）。但这种方式对于单个令牌而言可能会比较慢。

推荐做法是：以小批量（例如每 50 毫秒）收集令牌，然后一次性使用 `_cprint()` 输出整个批次。这样既能保证显示的响应速度，又能确保与 prompt_toolkit 兼容。

**第三阶段的测试内容：**（约 50 行）
- 测试 CLI 的流式回调功能配置
- 测试带流式功能的响应框边框显示效果
- 测试在流式功能被禁用时的回退机制

---

### 第四阶段：API 服务器的真正流式传输

**文件：gateway/platforms/api_server.py**

当智能体支持逐令牌的 SSE 传输时，需将模拟流式的 `_write_sse_chat_completion()` 函数替换为真正的逐令牌 SSE 传输功能。

#### 4a. 为 stream=true 的请求配置流式回调功能（约 20 行）

```python
if stream:
    _stream_q = queue.Queue()
    
    def _api_stream_callback(delta):
        _stream_q.put(delta)  # None = done
    
    # Pass callback to _run_agent
    result, usage = await self._run_agent(
        ..., stream_callback=_api_stream_callback,
    )
```

#### 4b. 真实 SSE 写入器（约40行代码）

```python
async def _write_real_sse(self, request, completion_id, model, stream_q):
    response = web.StreamResponse(
        headers={"Content-Type": "text/event-stream", "Cache-Control": "no-cache"},
    )
    await response.prepare(request)
    
    # Role chunk
    await response.write(...)
    
    # Stream content chunks as they arrive
    while True:
        try:
            delta = await asyncio.get_event_loop().run_in_executor(
                None, lambda: stream_q.get(timeout=0.1)
            )
        except queue.Empty:
            continue
        
        if delta is None:  # End of stream
            break
        
        chunk = {"id": completion_id, "object": "chat.completion.chunk", ...
                 "choices": [{"delta": {"content": delta}, ...}]}
        await response.write(f"data: {json.dumps(chunk)}\n\n".encode())
    
    # Finish + [DONE]
    await response.write(...)
    await response.write(b"data: [DONE]\n\n")
    return response
```

**挑战：并发执行问题**

该智能体在线程执行器中运行，而SSE数据的写入则发生在异步事件循环中。队列起到了连接两者的作用。但目前 `_run_agent()` 函数在返回之前会等待所有操作完成。若要实现真正的流式传输，就需要在后台启动智能体，并在其运行过程中持续输出令牌数据。

```python
# Start agent in background
agent_task = asyncio.create_task(self._run_agent_async(...))

# Stream tokens while agent runs
await self._write_real_sse(request, ..., stream_q)

# Agent is done by now (stream_q received None)
result, usage = await agent_task
```

为此，需要将 `_run_agent` 函数拆分为一个不会阻塞并等待结果的异步版本，或是在单独的任务中执行它。

**响应 API 的 SSE 格式：**

对于设置 `stream=true` 的 `/v1/responses` 接口，其 SSE 事件格式有所不同：

```
event: response.output_text.delta
data: {"type":"response.output_text.delta","delta":"Hello"}

event: response.completed  
data: {"type":"response.completed","response":{...}}
```

这需要一个独立的 SSE 写入器，用于发送符合 Responses API 格式的事件。

**第 4 阶段测试用例：**（约 80 行）
- 使用模拟代理测试真实的 SSE 流式传输
- 测试 SSE 事件格式（Chat Completions 与 Responses 的区别）
- 测试在流式传输过程中客户端断开连接的情况
- 测试在无法使用回调时切换为伪流式传输的功能

---

## 集成问题与边界情况

### 1. 流式传输期间的工具调用

当模型返回的是工具调用指令而非文本时，不会生成任何文本令牌。
此时 `stream_callback` 函数根本不会被调用以传递文本内容。在工具执行完成后，下一次 API 调用才会生成最终的文本响应——流式传输随即会重新开始。

流式预览功能需要处理这一情况：如果在工具调用阶段没有新的令牌到达，则不应发送或编辑任何消息。而工具处理进度消息则可继续按原有方式工作。

### 2. 消息重复问题

最大的风险在于：代理通过常规路径（现有的发送机制）发送了最终响应，而流式预览已经先展示了该内容，从而导致用户看到两次相同的响应。

预防措施：当处于流式传输状态且已有令牌被传递时，应抑制最终响应的发送。`result["_streamed_msg_id"]` 这一标记会告知基础适配器跳过其常规发送逻辑。

### 3. 响应的后处理

最终生成的响应可能与累计的流式传输令牌存在差异：
- 需去除思考块内容（即删除 `<think>...</think>` 标签）
- 清理末尾的空白字符
- 为工具返回的结果添加媒体标签

流式预览展示的是原始令牌内容，而最终呈现的版本应经过上述后处理。这意味着最终的编辑操作（如移除光标）应使用经过处理的 `final_response`，而非仅使用累计下来的流式文本。

### 4. 流式传输期间的上下文压缩

如果代理在对话进行过程中触发了上下文压缩，那么压缩前的流式令牌所对应的上下文与压缩后的令牌上下文是不同的。但实际上这并非问题——因为上下文压缩发生在两次 API 调用之间，而非流式传输过程中。

### 5. 流式传输过程中的中断

用户在流式传输进行时发送新消息→触发中断。此时流式传输会被终止（HTTP 连接关闭），累计的令牌会原样显示（不包含光标），同时中断消息也会按常规方式处理。这一功能已由 `_interruptible_api_call` 函数通过关闭客户端连接来实现。

### 6. 多模型切换/回退机制

如果主模型出现故障，代理会切换到其他模型，此时流式传输状态将会重置。而备用模型可能支持也可能不支持流式传输功能。`_run_streaming_chat_completion` 函数中的优雅回退机制可解决这一问题。

### 7. 编辑操作的速率限制

- Telegram：每分钟约 20 次编辑操作（为安全起见，建议间隔至少 3 秒）
- Discord：每条消息每 5 秒内最多 5 次编辑
- Slack：每分钟约 50 次 API 调用

1.5 秒的编辑间隔对所有平台而言都较为保守。如果遇到 429 速率限制错误，只需跳过当前编辑周期，稍后再试即可。

---

## 文件变更汇总

| 文件 | 阶段 | 变更内容 |
|------|-------|---------|
| `run_agent.py` | 1 | 添加 `stream_callback` 参数，新增 `_run_streaming_chat_completion()` 函数，修改 `_run_codex_stream()` 和 `_interruptible_api_call()` 函数 |
| `gateway/run.py` | 2 | 添加流式传输配置读取功能，完善队列/回调机制，新增流式预览任务，添加抑制最终响应发送的逻辑 |
| `gateway/platforms/base.py` | 2 | 在响应处理函数中添加对 `_streamed_msg_id` 的检测逻辑 |
| `cli.py` | 3 | 添加流式传输相关功能，实现令牌显示功能，集成响应框展示功能 |
| `gateway/platforms/api_server.py` | 4 | 实现真正的 SSE 写入器，完善流式传输回调的连接逻辑 |
| `hermes_cli/config.py` | 1 | 添加流式传输的默认配置项 |
| `cli-config.yaml.example` | 1 | 增加流式传输相关的配置章节 |
| `tests/test_streaming.py` | 1-4 | 新增测试文件——包含约 380 行测试代码 |

**各阶段新增代码总量**：约 500 行
**测试代码总量**：约 380 行

---

## 推进计划

1. **第 1 阶段**（核心功能）：将相关代码合并到主分支。默认情况下流式传输功能处于关闭状态。该改动不会影响现有功能，可通过环境变量进行测试。

2. **第 2 阶段**（网关层）：将相关代码合并到主分支。在 Telegram 平台上手动进行测试。可通过配置文件中的 `streaming.telegram: true` 选项来启用该功能。

3. **第 3 阶段**（命令行界面）：将相关代码合并到主分支。在终端环境中进行测试。可通过 `streaming.cli: true` 或 `streaming.enabled: true` 选项来启用该功能。

4. **第 4 阶段**（API 服务器层）：将相关代码合并到主分支。使用 Open WebUI 进行测试。当客户端发送 `stream: true` 参数时，该功能将自动启用。

每个阶段均可独立合并并测试。在整个过程中，流式传输功能默认处于关闭状态。待所有阶段都稳定后，可考虑将默认设置改为开启状态。

---

## 配置参考（最终状态）

```yaml
# config.yaml
streaming:
  enabled: false          # Master switch (default: off)
  cli: true               # Per-platform override
  telegram: true
  discord: true
  slack: true
  api_server: true        # API server always streams when client requests it
  edit_interval: 1.5      # Seconds between message edits (default: 1.5)
  min_tokens: 20          # Tokens before first display (default: 20)
```

```bash
# Environment variable override
HERMES_STREAMING_ENABLED=true
```
