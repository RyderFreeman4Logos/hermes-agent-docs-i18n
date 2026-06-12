# Hermes中间件

Hermes中间件是用于改变观察者钩子行为的辅助组件。观察者钩子仅负责报告发生了什么，而中间件则可以通过在请求执行前对其进行重写，或对执行回调本身进行封装，从而改变实际的处理流程。

该接口设计时刻意保持了与后端的无关性。插件可以利用它来实现本地策略应用、请求格式调整、追踪功能、自适应路由、缓存控制、沙箱选择，甚至将任务转发给NeMo Relay等运行时环境，而无需修改Hermes的规划器、模型提供者适配器、工具注册表、内存管理机制或CLI用户界面。

启用中间件后，插件可以：

- 在Hermes调用LLM提供者之前，重写传递给该提供者的请求参数。
- 在各种约束规则、审批检查、钩子函数以及工具执行逻辑看到这些参数之前，对它们进行重新处理。
- 在保留Hermes的重试、流式处理、中断及钩子功能的前提下，封装实际的LLM执行回调。
- 在保留Hermes的约束规则、审批流程、工具执行后的钩子功能以及工具结果转换机制的前提下，封装实际的工具执行回调。

## 接口规范

插件需通过`register(ctx)`函数来注册中间件：

```python
def register(ctx):
    ctx.register_middleware("llm_request", on_llm_request)
    ctx.register_middleware("llm_execution", on_llm_execution)
    ctx.register_middleware("tool_request", on_tool_request)
    ctx.register_middleware("tool_execution", on_tool_execution)
```

每个中间件回调都会接收以下内容：

- `telemetry_schema_version`：当前为 `hermes.observer.v1`
- `middleware_schema_version`：当前为 `hermes.middleware.v1`
- 运行时上下文，例如 `session_id`、`task_id`、`turn_id`、`api_request_id`、`provider`、`model`、`api_mode`、`tool_name`，以及在适用情况下的 `tool_call_id`。

支持的中间件类型如下：

| 类型 | 请求数据 | 返回格式 | 用途 |
| --- | --- | --- | --- |
| `llm_request` | `request`、`original_request` | `{"request": {...}}` | 在调用实际提供程序之前替换有效的提供程序参数。 |
| `tool_request` | `tool_name`、`args`、`original_args` | `{"args": {...}}` | 在钩子、安全规则、审批流程及执行之前替换有效的工具参数。 |
| `llm_execution` | `request`、`original_request`、`next_call` | 任何提供程序的响应 | 包装或替换实际的提供程序调用。 |
| `tool_execution` | `tool_name`、`args`、`original_args`、`next_call` | 任何工具的返回结果 | 包装或替换实际的工具调用。 |

请求中间件可以返回可选的追踪字段：

```python
return {
    "request": updated_request,
    "source": "my-plugin",
    "reason": "selected fallback model",
}
```

Hermes会将这些追踪记录以`middleware_trace`的格式存储在后续观察者钩子的负载数据中。

执行中间件会接收到一个`next_call`回调函数，调用该函数即可继续执行后续操作链。

```python
def on_tool_execution(**kwargs):
    result = kwargs["next_call"](kwargs["args"])
    return result
```

如果多个插件注册了相同类型的执行中间件，Hermes会按照注册顺序将它们以嵌套链的形式依次运行。中间件出现故障时采用“故障即继续”策略：Hermes仅记录警告信息，然后继续执行下一个中间件或基础运行时路径。

## 执行顺序

### LLM调用

对于每个提供商请求，Hermes会按以下顺序应用中间件：

1. 根据当前对话构建提供商的参数字典。
2. 应用`llm_request`中间件。
3. 使用有效的请求信息触发`pre_api_request`观察者钩子。
4. 通过`llm_execution`中间件执行提供商相关的操作。
5. 触发`post_api_request`或`api_request_error`观察者钩子。

请求中间件可以访问完整的提供商参数字典，其中包括`messages`或Responses API的`input`字段、模型设置、工具定义、流处理选项以及针对该提供商的特定选项。而执行中间件则接收相同的有效请求信息以及`next_call`参数。

### 工具调用

对于每次工具调用，Hermes会按以下顺序应用中间件：

1. 解析并转换模型提供的工具参数。
2. 应用`tool_request`中间件。
3. 对有效的参数执行Hermes常规的预执行流程：检查工具是否可用、处理观察者块指令、执行安全规范检查以及进行审批验证。
4. 通过`tool_execution`中间件执行工具相关的操作。
5. 触发`post_tool_call`观察者钩子。
6. 在将结果重新添加到对话上下文之前，先应用`transform_tool_result`钩子。

`tool_request`中间件会在审批检查之前运行。请谨慎使用该中间件：下游策略将会基于被重写的路径、命令或URL来执行相应的操作。

## 启用机制

中间件仅对已启用的插件生效。对于打包好的插件而言：

```bash
hermes plugins enable <plugin-name>
```

在进行独立的本地测试时，建议为插件启用以及代理程序的运行分别设置一个 `HERMES_HOME` 变量。

```bash
export HERMES_HOME=/tmp/hermes-middleware-test
mkdir -p "$HERMES_HOME"
hermes plugins enable <plugin-name>
hermes chat --query 'Reply exactly ok'
```

在检出源代码时，建议使用 `source` 命令，这样运行时就能识别工作目录中的插件及中间件。

```bash
uv sync
uv run hermes plugins enable <plugin-name>
uv run hermes chat --query 'Reply exactly ok'
```

## 通用插件示例

以下示例刻意设计得较为简单，旨在展示中间件接口的架构，且不依赖 NeMo Relay。

### LLM 请求中间件

该插件会对提供商发起的请求进行标记，并记录一条中间件追踪信息：

```python
def register(ctx):
    ctx.register_middleware("llm_request", tag_llm_request)


def tag_llm_request(**kwargs):
    request = dict(kwargs["request"])
    extra_body = dict(request.get("extra_body") or {})
    extra_body.setdefault("metadata", {})["hermes_middleware_demo"] = True
    request["extra_body"] = extra_body
    return {
        "request": request,
        "source": "middleware-demo",
        "reason": "tagged provider request",
    }
```

有效的请求会被依次传递给 `pre_api_request`、提供程序执行逻辑以及 `post_api_request`。

### 工具请求中间件

该插件会将 `terminal` 调用限制在已知的可用工作目录内：

```python
def register(ctx):
    ctx.register_middleware("tool_request", normalize_terminal_workdir)


def normalize_terminal_workdir(**kwargs):
    if kwargs.get("tool_name") != "terminal":
        return None
    args = dict(kwargs["args"])
    args.setdefault("workdir", "/tmp/hermes-middleware-demo")
    return {
        "args": args,
        "source": "middleware-demo",
        "reason": "defaulted terminal workdir",
    }
```

由于该操作在钩子函数和审批流程之前执行，因此下游的遥测系统与策略机制将监测到已被修改后的 `workdir` 值。

### LLM 执行中间件

该插件会对提供商的调用进行封装，并保留原始的提供商响应内容：

```python
import time


def register(ctx):
    ctx.register_middleware("llm_execution", time_llm_execution)


def time_llm_execution(**kwargs):
    started = time.monotonic()
    response = kwargs["next_call"](kwargs["request"])
    elapsed_ms = int((time.monotonic() - started) * 1000)
    print(f"llm_execution elapsed_ms={elapsed_ms}")
    return response
```

返回与Hermes期望的提供商适配器相同的响应格式。除非运行时环境要求使用特定的封装结构，否则不得将响应包裹在该结构中。

### 工具执行中间件

该插件在保留工具执行结果的同时，对工具的执行过程进行封装：

```python
def register(ctx):
    ctx.register_middleware("tool_execution", annotate_tool_execution)


def annotate_tool_execution(**kwargs):
    result = kwargs["next_call"](kwargs["args"])
    # Metrics, logging, or external routing can happen here.
    return result
```

执行中间件可调用 `next_call(modified_args)`，将经过修改的负载传递给后续的中间件以及基础工具调度器。与特定插件相关的示例应存储在该插件所在的位置。关于 NeMo Relay 自适应执行中间件的详细信息，请参阅 [`plugins/observability/nemo_relay/README.md`](../../plugins/observability/nemo_relay/README.md)。

## 安全注意事项

- 对于相同的输入，中间件应始终产生确定性的输出，除非明确被路由至动态外部系统。
- 请求中间件应返回完整的替换负载，而非仅部分修改后的数据。
- 除非有意缩短执行流程，否则执行中间件应仅调用 `next_call(...)` 一次。
- 若执行中间件在调用 `next_call(...)` 之前就抛出异常，Hermes 会将其视为中间件故障，并继续执行剩余的中间件链及基础执行流程。
- 若执行中间件成功调用了 `next_call(...)`，但在后续处理过程中出现异常，Hermes 会保留下游的处理结果，而不会再次运行对应的提供者或工具。
- 若下游的提供者或工具执行失败，中间件可以选择让该错误继续传播，或主动对其进行转换。Hermes 不会将下游的失败转换为成功的 `None` 结果。
- 工具请求中间件会在审批流程之前运行。如果它修改了文件路径、命令、URL 或参数，那么这些被修改后的值将会被用于安全规则和审批流程的判断。
- 仅读型遥测数据仍应通过观察者钩子来处理。只有在插件需要修改或封装某些功能时，才应使用中间件。
