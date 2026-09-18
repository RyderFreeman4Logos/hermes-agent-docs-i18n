---
sidebar_position: 11
title: "Plugin LLM Access"
description: "Run any LLM call from inside a plugin via ctx.llm — chat or structured, sync or async. Host-owned auth, fail-closed trust gate, optional JSON Schema validation."
---

# 插件调用大型语言模型

`ctx.llm` 是插件进行大型语言模型调用的推荐方式。无论是聊天补全、结构化信息提取、同步处理、异步处理，还是是否需要处理图像——所有操作都通过同一接口完成，遵循相同的信任机制，并使用由主机管理的凭证。

当插件需要执行与模型相关但并非代理对话流程中的任务时，就会使用这一方式。例如：将工具错误转换为非工程师也能理解的格式的钩子函数；在消息入队前对其进行转换的网关适配器；用于总结长文本的斜杠命令；对昨日活动进行评分并向状态看板写入一条记录的定时任务；以及用于判断某条消息是否值得唤醒代理的预过滤机制。

这类任务本就不应由代理持续参与处理。它们只需要一次大型语言模型调用，得到一个文本形式的回复，然后即可完成。

## 最简化的调用方式

```python
result = ctx.llm.complete(messages=[{"role": "user", "content": "ping"}])
return result.text
```

整段 API 代码仅需一行即可实现。无需任何密钥、提供者配置，也无需进行 SDK 初始化。该插件会自动适配用户当前使用的提供者与模型；当用户更换提供者时，插件也会随之自动切换。  

## 更完整的聊天示例

```python
result = ctx.llm.complete(
    messages=[
        {"role": "system", "content": "Rewrite errors as one short sentence a non-engineer can act on."},
        {"role": "user",   "content": traceback_text},
    ],
    max_tokens=64,
    purpose="hooks.error-rewrite",
)
return result.text
```

`purpose`是一个自由格式的审计字符串——它会被记录在`agent.log`以及`result.audit`中，以便操作员能够查看是哪个插件发起了哪次调用。该字段虽为非必填项，但对于那些频繁触发的操作而言，建议将其设置。

## 结构化输出

当插件需要结构化的响应时，请切换到结构化输出模式：

```python
result = ctx.llm.complete_structured(
    instructions="Score this support reply for urgency (0–1) and pick a category.",
    input=[{"type": "text", "text": message_body}],
    json_schema=TRIAGE_SCHEMA,
    purpose="support.triage",
    temperature=0.0,
    max_tokens=128,
)

if result.parsed["urgency"] > 0.8:
    await dispatch_to_oncall(result.parsed["category"], message_body)
```

主机会向提供者请求 JSON 格式的输出，作为备用方案在本地对其进行解析；如果已安装 `jsonschema`，还会根据预设的架构对解析结果进行验证，最终通过 `result.parsed` 返回 Python 对象。若模型无法生成有效的 JSON，则 `result.parsed` 的值为 `None`，而 `result.text` 则会包含原始响应内容。

## 该功能带来的优势

* **一次调用，多种输出格式**：支持聊天场景的 `complete()`、结构化 JSON 场景的 `complete_structured()`，以及 asyncio 场景的 `acomplete()` 和 `acomplete_structured()`。参数相同，返回的结果对象也一致。
* **主机掌控凭据管理**：OAuth 令牌、刷新流程、凭据池以及针对单个任务的临时配置调整——Hermes 所具备的所有凭据管理功能均可应用。插件本身无法直接获取令牌，主机会通过 `result.audit` 将相关调用信息反馈给插件。
* **操作范围受限**：仅支持单次同步或异步调用，不存在流式处理、工具循环或需要管理的对话状态。只需输入数据、获取结果并返回即可。
* **安全限制机制**：未经配置的插件无法自行选择提供者、模型、智能体或存储的凭据。默认策略为“使用用户当前正在使用的资源”。操作员可在 `config.yaml` 中为特定插件指定自定义配置。

## 快速入门

下面提供了两个完整的插件示例——一个用于聊天场景，另一个用于结构化数据处理。二者均封装在同一个 `register(ctx)` 函数中，无需任何外部配置即可针对用户当前使用的模型正常运行。

### 聊天场景补全功能 —— `/tldr`

```python
def register(ctx):
    ctx.register_command(
        name="tldr",
        handler=lambda raw: _tldr(ctx, raw),
        description="Summarise the supplied text in one paragraph.",
        args_hint="<text>",
    )


def _tldr(ctx, raw_args: str) -> str:
    text = raw_args.strip()
    if not text:
        return "Usage: /tldr <text to summarise>"
    result = ctx.llm.complete(
        messages=[
            {"role": "system",
             "content": "Summarise the user's text in one tight paragraph. No preamble."},
            {"role": "user", "content": text},
        ],
        max_tokens=256,
        temperature=0.3,
        purpose="tldr",
    )
    return result.text
```

`result.text` 包含模型的响应内容；`result.usage` 记录了Token数量；而 `result.provider` 与 `result.model` 则用于标注来源信息。

### 结构化提取 — `/paste-to-tasks`

```python
def register(ctx):
    ctx.register_command(
        name="paste-to-tasks",
        handler=lambda raw: _paste_to_tasks(ctx, raw),
        description="Turn freeform meeting notes into structured tasks.",
        args_hint="<text>",
    )


_TASKS_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "owner":  {"type": "string"},
                    "action": {"type": "string"},
                    "due":    {"type": "string", "description": "ISO date or empty"},
                },
                "required": ["action"],
            },
        },
    },
    "required": ["tasks"],
}


def _paste_to_tasks(ctx, raw_args: str) -> str:
    if not raw_args.strip():
        return "Usage: /paste-to-tasks <meeting notes>"
    result = ctx.llm.complete_structured(
        instructions=(
            "Extract concrete action items from these meeting notes. "
            "One task per actionable line. If no owner is named, leave 'owner' blank."
        ),
        input=[{"type": "text", "text": raw_args}],
        json_schema=_TASKS_SCHEMA,
        schema_name="meeting.tasks",
        purpose="paste-to-tasks",
        temperature=0.0,
        max_tokens=512,
    )
    if result.parsed is None:
        return f"Couldn't parse a response. Raw output:\n{result.text}"
    lines = [f"- [{t.get('owner') or '?'}] {t['action']}" for t in result.parsed["tasks"]]
    return "\n".join(lines) or "(no tasks found)"
```

第三个示例涉及图像输入，位于 [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example) 仓库中（该仓库用于存放参考插件，并不随 hermes-agent 一同打包）。关于异步接口（使用 `asyncio.gather()` 的 `acomplete()` / `acomplete_structured()`），请参阅同一仓库中的 [`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example)。

## 何时选择哪种方法

| 需求 | 推荐使用 |
|---|---|
| 自由格式的文本回复（翻译、总结、重写、生成） | `complete()` |
| 多轮对话式提示（系统指令 + 少量示例 + 用户输入） | `complete()` |
| 返回符合结构规范的键值对数据 | `complete_structured()` |
| 接收图像或文本输入并返回结构化数据 | `complete_structured()` |
| 在异步代码中调用（如网关适配器、异步钩子） | `acomplete()` / `acomplete_structured()` |

其余方面——包括提供者选择、模型加载、身份验证、备用方案、超时处理以及视觉处理路由——在这四种方法中均保持一致。

## API 接口

`ctx.llm` 是 `agent.plugin_llm.PluginLlm` 的实例。

### `complete()`

```python
result = ctx.llm.complete(
    messages=[{"role": "user", "content": "Hi"}],
    provider=None,         # optional, gated — Hermes provider id (e.g. "openrouter")
    model=None,            # optional, gated — whatever string that provider expects
    temperature=None,
    max_tokens=None,
    timeout=None,          # seconds
    agent_id=None,         # optional, gated
    profile=None,          # optional, gated — explicit auth-profile name
    purpose="optional-audit-string",
    task=None,             # optional — a plugin-registered auxiliary slot
)
# → PluginLlmCompleteResult(text, provider, model, agent_id, usage, audit)
```

普通对话完成功能。`messages`采用OpenAI标准的格式——即由多个`{"role": "...", "content": "..."}`字典构成的列表。多轮提示（系统指令 + 少量示例的用户/助手对话对 + 最终用户输入）的处理方式与使用OpenAI SDK时完全一致。

`provider=`和`model=`这两个参数是相互独立的，其格式与主机主配置中的`model.provider`和`model.model`相同。只需设置`model=`即可使用用户当前所选的提供商，但搭配不同的模型；若要完全更换提供商，则需同时设置这两个参数。未指定运算符的任一参数都会引发`PluginLlmTrustError`错误。

### `complete_structured()`

```python
result = ctx.llm.complete_structured(
    instructions="What you want extracted.",
    input=[
        {"type": "text",  "text": "..."},
        {"type": "image", "data": b"...", "mime_type": "image/png"},
        {"type": "image", "url":  "https://..."},
    ],
    json_schema={...},     # optional — triggers parsed result + validation
    json_mode=False,       # set True without a schema to ask for JSON anyway
    schema_name=None,      # optional human-readable schema name
    system_prompt=None,
    provider=None,         # optional, gated
    model=None,            # optional, gated
    temperature=None,
    max_tokens=None,
    timeout=None,
    agent_id=None,
    profile=None,
    purpose=None,
    task=None,             # optional — a plugin-registered auxiliary slot
)
# → PluginLlmStructuredResult(text, provider, model, agent_id,
#                             usage, parsed, content_type, audit)
```

输入内容可以是文本或图像块（原始字节会自动通过 `data:` URL 进行 Base64 编码）。当指定了 `json_schema` 或设置 `json_mode=True` 时，主机会通过 `response_format` 请求 JSON 格式的输出，作为备用方案在本地对其进行解析；如果已安装 `jsonschema`，还会根据该规范对解析结果进行验证。

* `result.content_type == "json"` — `result.parsed` 是一个符合您所定义规范的 Python 对象。
* `result.content_type == "text"` — 解析或验证失败；请查看 `result.text` 以获取模型的原始响应内容。

### 异步模式

```python
result = await ctx.llm.acomplete(messages=..., task="classifier")
result = await ctx.llm.acomplete_structured(
    instructions=..., input=..., task="classifier"
)
```

其参数与返回类型与同步版本相同。这些功能适用于网关适配器、异步钩子，以及任何已在 asyncio 循环中运行的插件代码。

### 任务路由的辅助调用

当某个插件需要自定义配置的辅助调用路径时，可在四种调用方式中添加 `task=` 参数。该任务需在插件初始化阶段进行注册；在操作员通过 `auxiliary.<task>` 重置其提供者和模型之前，将沿用插件默认设置。

```python
def register(ctx):
    ctx.register_auxiliary_task(
        "classifier", display_name="Classifier", description="Classify input."
    )


result = ctx.llm.complete(messages=[...], task="classifier")
result = ctx.llm.complete_structured(instructions=..., input=..., task="classifier")
```

```yaml
auxiliary:
  classifier:
    provider: openrouter
    model: vendor/model-id
```

插件可为自身的任务提供提供商/模型注册的默认值。在 `auxiliary.<task>` 中配置的操作符可覆盖这些默认值，并决定具体的部署方案。一个插件仅能使用其自行注册的任务；若遇到未知或非本插件注册的任务名称，将在调用提供商之前失败。`allow_task_override: true` 是一种明确的操作符权限设置，允许使用 Hermes 内置的辅助任务，但不可使用其他插件的任务。如需保留当前活跃的主提供商/模型，可省略 `task=` 参数（或使用 `"auto"`）。

```python
@dataclass
class PluginLlmCompleteResult:
    text: str                    # the assistant's response
    provider: str                # e.g. "openrouter", "anthropic"
    model: str                   # whatever the provider returned for this call
    agent_id: str                # whose model/auth was used
    usage: PluginLlmUsage        # tokens + cache + cost estimate
    audit: Dict[str, Any]        # plugin_id, purpose, profile

@dataclass
class PluginLlmStructuredResult:
    # same fields as PluginLlmCompleteResult, plus:
    parsed: Optional[Any]        # JSON object when content_type == "json"
    content_type: str            # "json" or "text"
    # audit also carries schema_name when supplied
```

当提供方返回相应字段时，`usage` 会包含 `input_tokens`、`output_tokens`、`total_tokens`、`cache_read_tokens`、`cache_write_tokens` 以及 `cost_usd`。

## 信任机制

默认行为为“故障即关闭”。若不存在 `plugins.entries` 配置块，插件可以：

* 对用户当前使用的提供方和模型调用四种方法中的任意一种，
* 设置请求配置参数（如 `temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`），

仅此而已。在操作员未进行授权之前，`provider=`、`model=`、`agent_id=` 和 `profile=` 参数会引发 `PluginLlmTrustError` 错误。同样，除非操作员为内置任务授予了 `allow_task_override` 权限，否则 `task=` 参数也只能使用插件已注册的辅助任务。

**大多数插件根本无需使用此部分配置。** 那些仅通过调用 `ctx.llm.complete(messages=...)` 且不进行任何参数覆盖的插件，会直接使用用户当前激活的模型和提供方，从而实现零配置运行。只有在插件明确希望指定与用户不同的模型或提供方时，下方配置块才具有意义。

```yaml
plugins:
  entries:
    my-plugin:
      llm:
        # Allow this plugin to choose a different Hermes provider
        # (must be one Hermes already knows about — same names as
        # `hermes model` and config.yaml model.provider).
        allow_provider_override: true

        # Optionally restrict which providers. Use ["*"] for any.
        allowed_providers:
          - openrouter
          - anthropic

        # Allow this plugin to ask for a specific model.
        allow_model_override: true

        # Optionally restrict which models. Use ["*"] for any.
        # Models are matched literally against whatever string the
        # plugin sends — Hermes does not look anything up.
        allowed_models:
          - openai/gpt-4o-mini
          - anthropic/claude-3-5-haiku

        # Allow cross-agent calls (rare).
        allow_agent_id_override: false

        # Allow the plugin to request a specific stored auth profile
        # (e.g. a different OAuth account on the same provider).
        allow_profile_override: false
```

对于扁平插件，插件 ID 即为其清单文件中的 `name:` 字段；而对于嵌套插件，则为从路径中提取的键值（如 `image_gen/openai`、`memory/honcho` 等）。

### 该限制机制所管控的内容

| 可覆盖参数       | 默认值 | 配置键                         |
| --------------- | ------- | ------------------------------ |
| `provider=`     | 拒绝    | `allow_provider_override: true`  |
| ↳ 允许列表       | —       | `allowed_providers: [...]`       |
| `model=`        | 拒绝    | `allow_model_override: true`     |
| ↳ 允许列表       | —       | `allowed_models: [...]`          |
| `agent_id=`     | 拒绝    | `allow_agent_id_override: true`  |
| `profile=`      | 拒绝    | `allow_profile_override: true`   |
| 内置的 `task=`  | 拒绝    | `allow_task_override: true`      |

各项覆盖设置是独立受控的。即便启用了 `allow_model_override`，也不代表同时会启用 `allow_provider_override`——除非该插件也通过了提供商限制检查，否则它仍然会被绑定在用户当前使用的提供商上。

### 该限制机制无需管控的内容

* 请求配置参数——如 `temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`、`schema_name`、`json_mode`——始终被允许使用；这些参数不会涉及凭据或路由选择。
* 默认的拒绝策略意味着未配置的插件仍可执行有用任务——它只是会使用当前启用的提供者和模型来运行。对于那些需要更精细路由控制的插件，操作员只需关注 `plugins.entries` 即可。

## 主机所掌控的内容

此处列出了 `ctx.llm` 为插件提供的所有功能，这样您就无需再自行查找了：

* **提供者解析。** 从用户的配置文件中读取 `model.provider` 和 `model.model` 值（在可信的情况下也会采用显式覆盖的设置）。
* **身份认证。** 从 `~/.hermes/auth.json` 文件或环境变量中获取 API 密钥、OAuth 令牌或刷新令牌，若已配置凭证池，则也会使用该池中的凭证；插件本身无法直接访问这些凭证。
* **视觉处理路由。** 当输入为图像且用户当前使用的文本模型仅支持文本处理时，系统会自动切换到已配置的视觉处理模型。
* **回退机制。** 若用户指定的主要提供者返回 5xx 或 429 错误，请求会先经过 Hermes 的常规聚合器感知型回退流程，之后才会向插件返回错误。
* **超时设置。** 优先遵循用户指定的 `timeout=` 参数，若未指定则使用 `auxiliary.<task>.timeout` 配置值或全局辅助配置的默认值。
* **JSON 格式处理。** 当用户要求以 JSON 格式获取结果时，会将 `response_format` 参数传递给提供者；若提供者返回了格式化的响应，则会在本地对该响应进行重新解析。
* **模式验证。** 若已安装 `jsonschema` 工具，则会根据用户指定的 `json_schema` 对响应数据进行验证；否则仅记录调试信息，不会执行严格的验证流程。
* **审计日志。** 每次调用都会在 `agent.log` 文件中写入一条 INFO 级别的日志，内容包括插件标识、使用的相关提供者/模型、操作目的以及各类型的令牌使用总量。

## 插件负责处理的内容

* **请求格式**：用于聊天场景时为 `messages` 格式，用于结构化任务时则为 `instructions` + `input` 格式。插件负责构建提示词，而主机则负责执行该提示词。
* **数据结构**：可返回任意您期望的格式，主机不会自动推断其结构。
* **错误处理**：当输入为空或数据结构验证失败时，`complete_structured()` 会抛出 `ValueError` 异常；若信任机制拒绝某些配置变更，则会触发 `PluginLlmTrustError` 异常。其他情况（如服务提供商返回 5xx 错误、未配置认证信息、超时等）则由 `auxiliary_client.call_llm()` 所抛出的异常决定。
* **成本问题**：每次调用都会消耗用户所使用的付费服务提供商的额度。在处理每个网关消息的 `complete()` 回调时，务必考虑 Token 消耗情况，避免不必要的循环调用。

## 在插件架构中的定位

现有的 `ctx.*` 方法是对 Hermes 现有子系统的扩展：

| 方法 | 功能说明 |
|------|----------|
| `ctx.register_tool` | 添加代理可调用的工具 |
| `ctx.register_platform` | 连接新的网关适配器 |
| `ctx.register_image_gen_provider` | 更换图像生成后端 |
| `ctx.register_memory_provider` | 更换内存管理后端 |
| `ctx.register_context_engine` | 更换上下文压缩器 |
| `ctx.register_hook` | 监听生命周期事件 |
`ctx.llm` 是首个让插件能够在无需依赖上述任何组件的情况下，*独立地*调用用户当前正在使用的同一模型的接口。这也是它唯一的职责。如果您的插件需要注册代理调用的工具，可使用 `register_tool`；若需对生命周期事件作出响应，则使用 `register_hook`；而无论出于何种原因——无论是结构化需求还是非结构化需求——都需要进行模型调用时，则应使用 `ctx.llm`。

## 参考资料

* 实现代码：[`agent/plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/plugin_llm.py)
* 测试用例：[`tests/agent/test_plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/tests/agent/test_plugin_llm.py)
* 参考插件（配套仓库）：
  * [`plugin-llm-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example) —— 支持基于图像输入的同步结构化数据提取
  * [`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example) —— 使用 `asyncio.gather()` 实现异步处理
* 辅助客户端（底层引擎）：详见 [Provider Runtime](/developer-guide/provider-runtime)。
