---
sidebar_position: 11
title: "Plugin LLM Access"
description: "Run any LLM call from inside a plugin via ctx.llm — chat or structured, sync or async. Host-owned auth, fail-closed trust gate, optional JSON Schema validation."
---

# 插件调用大型语言模型

`ctx.llm` 是插件调用大型语言模型的标准方式。无论是聊天补全、结构化信息提取、同步处理、异步处理，还是是否需要图像输入——所有操作都通过同一接口实现，具备相同的信任机制，并使用由主机管理的凭证。

当插件需要执行与模型相关但并不属于代理对话流程的任务时，就会使用这一方式。例如：将工具返回的错误信息转换为非工程师也能理解的格式；在消息入队前对其进行转换的网关适配器；用于总结长文本的斜杠命令；对昨日活动进行评分并往状态看板写入一条记录的定时任务；以及用于判断某条消息是否值得唤醒代理的预过滤机制。

这类任务本就不应让代理持续参与处理。它们只需要一次大型语言模型调用，得到一个结构化的回复，然后即可完成。

## 最简化的调用方式

```python
result = ctx.llm.complete(messages=[{"role": "user", "content": "ping"}])
return result.text
```

整段 API 代码仅用一行即可实现。无需任何密钥、提供者配置，也无需进行 SDK 初始化。该插件会自动适配用户当前使用的提供者和模型；当用户更换提供者时，插件也会随之自动切换。  

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

`purpose` 是一个自由格式的审计字符串——它会出现在 `agent.log` 以及 `result.audit` 中，以便操作员能够查看是哪个插件发出了哪次调用。该字段虽非必填，但对于频繁触发的操作而言建议设置。

## 结构化输出

当插件需要类型化的回复时，请切换到结构化输出模式：

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

主机会向提供者请求 JSON 格式的输出，作为备用方案在本地对其进行解析；如果已安装 `jsonschema`，还会根据该规范对解析结果进行验证，最终通过 `result.parsed` 返回 Python 对象。若模型无法生成有效的 JSON，则 `result.parsed` 的值为 `None`，而 `result.text` 则会包含原始响应内容。

## 该功能模式的优势

* **一次调用，多种输出格式**。支持用于聊天场景的 `complete()`、用于结构化 JSON 的 `complete_structured()`，以及用于 asyncio 场景的 `acomplete()` 和 `acomplete_structured()`。参数相同，返回的结果对象也一致。
* **主机掌控凭证管理**。OAuth 令牌、刷新流程、凭证池、针对单任务的临时凭证覆盖——Hermes 所具备的所有凭证管理功能均适用。插件本身无法直接获取令牌，主机会通过 `result.audit` 将相关调用信息反馈给插件。
* **操作范围受限**。仅支持单次同步或异步调用，无流式处理、无工具循环，也无需管理对话状态。只需输入数据、获取结果并返回即可。
* **安全封闭机制**。未经配置的插件无法自行选择提供者、模型、智能体或存储的凭证。默认策略为“使用用户当前正在使用的资源”。操作员可在 `config.yaml` 中为特定插件指定自定义设置。

## 快速入门

下面提供了两个完整的插件示例——一个用于聊天，另一个用于结构化数据处理。这两个插件均封装在同一个 `register(ctx)` 函数中，无需任何外部配置即可针对用户当前激活的模型正常运行。

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

`result.text`为模型的响应内容；`result.usage`包含令牌计数信息；而`result.provider`与`result.model`则用于标注来源信息。

### 结构化提取——/paste-to-tasks

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

第三个示例涉及图像输入，位于[`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example)仓库中（该仓库用于存放参考插件，并未随hermes-agent一同打包）。关于异步接口（使用`asyncio.gather()`的`acomplete()`/`acomplete_structured()`），请参阅同一仓库中的[`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example)。

## 何时选择哪种方式

| 需求 | 推荐使用 |
|---|---|
| 自由格式文本响应（翻译、总结、重写、生成） | `complete()` |
| 多轮对话式提示（系统指令+少量示例+用户输入） | `complete()` |
| 返回符合特定结构规范的字典数据 | `complete_structured()` |
| 图像或文本输入并返回结构化字典数据 | `complete_structured()` |
| 在异步代码中调用（如网关适配器、异步钩子） | `acomplete()` / `acomplete_structured()` |

其余方面——如提供者选择、模型解析、身份验证、备用方案、超时处理以及视觉功能路由——在这四种方式中均保持一致。

## API接口

`ctx.llm`是`agent.plugin_llm.PluginLlm`的实例。

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
)
# → PluginLlmCompleteResult(text, provider, model, agent_id, usage, audit)
```

普通聊天任务完成功能。`messages`采用OpenAI标准的格式——即由多个`{"role": "...", "content": "..."}`字典构成的列表。多轮对话提示（系统指令 + 少量示例的用户/助手对 + 最终用户输入）的处理方式与使用OpenAI SDK时完全一致。

`provider=`和`model=`这两个参数是相互独立的，其格式与主机主配置中的`model.provider`和`model.model`相同。只需设置`model=`即可使用用户当前选定的提供商，但搭配不同的模型；若同时设置这两个参数，则可彻底更换提供商。未指定运算符的任一参数都会引发`PluginLlmTrustError`错误。

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
)
# → PluginLlmStructuredResult(text, provider, model, agent_id,
#                             usage, parsed, content_type, audit)
```

输入内容可以是文本或图像块（原始字节会自动通过`data:` URL进行Base64编码）。当指定了`json_schema`或设置`json_mode=True`时，主机会通过`response_format`请求JSON格式的输出，在本地对其进行解析作为备用方案；如果已安装`jsonschema`工具，还会根据您定义的架构对输出内容进行验证。

* `result.content_type == "json"` — 表示`result.parsed`是一个符合您所定架构的Python对象。
* `result.content_type == "text"` — 表示解析或验证失败；可查看`result.text`以获取模型的原始响应内容。

### 异步模式

```python
result = await ctx.llm.acomplete(messages=...)
result = await ctx.llm.acomplete_structured(instructions=..., input=...)
```

其参数与返回结果类型均与同步版本相同。您可以在网关适配器、异步钩子，或任何已在 asyncio 循环中运行的插件代码中使用它们。

### 结果属性

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
class PluginLlmStructuredResult(PluginLlmCompleteResult):
    parsed: Optional[Any]        # JSON object when content_type == "json"
    content_type: str            # "json" or "text"
    # audit also carries schema_name when supplied
```

当提供方返回相应字段时，`usage` 会包含 `input_tokens`、`output_tokens`、`total_tokens`、`cache_read_tokens`、`cache_write_tokens` 以及 `cost_usd`。

## 信任机制

默认行为为“故障即关闭”。在没有 `plugins.entries` 配置块的情况下，插件可以：

* 对用户当前使用的提供方和模型调用四种方法中的任意一种，
* 设置请求配置参数（如 `temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`），

仅此而已。在操作员未进行相关设置之前，`provider=`、`model=`、`agent_id=` 和 `profile=` 参数会引发 `PluginLlmTrustError` 异常。

**大多数插件根本不需要这一部分配置。** 那些仅调用 `ctx.llm.complete(messages=...)` 且不进行任何参数覆盖的插件，会直接使用用户当前激活的模型和提供方，从而实现零配置运行。只有在插件明确希望指定不同于用户当前设置的模型或提供方时，下方这段配置才具有意义。

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

插件标识对于扁平型插件而言，即为清单文件中的 `name:` 字段；而对于嵌套型插件，则为基于路径生成的键值（如 `image_gen/openai`、`memory/honcho` 等）。

### 网关所控制的规则

| 覆盖项 | 默认值 | 配置键 |
| ------ | ------- | ------ |
| `provider=` | 拒绝 | `allow_provider_override: true` |
| ↳ 允许列表 | — | `allowed_providers: [...]` |
| `model=` | 拒绝 | `allow_model_override: true` |
| ↳ 允许列表 | — | `allowed_models: [...]` |
| `agent_id=` | 拒绝 | `allow_agent_id_override: true` |
| `profile=` | 拒绝 | `allow_profile_override: true` |

各项覆盖规则是独立控制的。即便启用了 `allow_model_override`，也**不会**自动启用 `allow_provider_override`——只有同时通过提供者相关网关验证后，被允许选择模型的插件才能使用用户当前配置的提供者。

### 网关无需控制的规则

* 请求格式相关参数——如 `temperature`、`max_tokens`、`timeout`、`system_prompt`、`purpose`、`messages`、`instructions`、`input`、`json_schema`、`schema_name`、`json_mode`——始终被允许使用；这些参数并不涉及凭据或路由选择。
* 由于默认采取拒绝策略，未进行配置的插件依然可以正常工作——它只会使用用户当前激活的提供者和模型。只有那些需要更精细路由控制的插件，操作者才需要关注 `plugins.entries` 设置。

## 主机负责处理的内容

`ctx.llm` 会为插件处理以下所有事务，从而免去您的麻烦：

* **提供者识别**：从用户配置中读取 `model.provider` 和 `model.model` 字段（若插件被授权，也会使用显式指定的覆盖值）。
* **身份认证**：从 `~/.hermes/auth.json` 或环境变量中获取 API 密钥、OAuth 令牌或刷新令牌；若已配置凭据池，也会从中取用。插件本身无法看到这些凭据。
* **视觉处理路由**：当收到图像输入且用户当前激活的文本模型仅为文本类型时，主机会自动切换到已配置的视觉模型进行处理。
* **回退机制**：如果用户的主要提供者返回 5xx 或 429 错误，请求会先经过 Hermes 的常规聚合器感知型回退流程，之后才会向插件返回错误。
* **超时控制**：优先遵循您设置的 `timeout=` 参数，若未设置则使用 `auxiliary.<task>.timeout` 配置值或全局辅助配置的默认值。
* **JSON 格式处理**：当您要求以 JSON 格式获取响应时，主机会先将 `response_format` 参数传递给提供者；如果提供者返回了 JSON 格式的响应，主机则会从受代码隔离的区域重新解析该响应。
* **模式验证**：若已安装 `jsonschema` 库，主机会根据您指定的 `json_schema` 对响应进行验证；否则仅记录调试信息，不会执行严格的验证流程。
* **审计日志**：每次调用都会在 `agent.log` 文件中写入一条 INFO 级日志，内容包括插件标识、使用的相关提供者/模型、操作目的以及 token 消耗总量。

## 插件负责处理的内容

* **请求格式构建**：聊天类请求需使用 `messages` 参数，结构化请求则需使用 `instructions` 和 `input` 参数。插件负责构建提示词，主机则负责执行该提示词。
* **响应格式定义**：插件可自行决定希望得到的响应格式，主机不会自动推断。
* **错误处理**：函数 `complete_structured()` 在输入为空或模式验证失败时会抛出 `ValueError` 异常；当信任网关拒绝某项覆盖请求时，会触发 `PluginLlmTrustError` 异常。其他异常（如提供者返回 5xx 错误、未配置凭据、超时等）则由 `auxiliary_client.call_llm()` 函数抛出的异常决定。
* **成本计算**：每次调用都会使用用户已付费的提供者服务。因此，在处理每个网关消息时，切勿在不考虑 token 消耗的情况下反复调用 `complete()` 函数。

## 该接口在插件体系中的定位

现有的 `ctx.*` 方法都是对 Hermes 现有子系统的扩展：

| `ctx.register_tool` | 添加代理可调用的工具 |
| `ctx.register_platform` | 连接新的网关适配器 |
| `ctx.register_image_gen_provider` | 替换图像生成后端 |
| `ctx.register_memory_provider` | 替换内存处理后端 |
| `ctx.register_context_engine` | 替换上下文压缩模块 |
| `ctx.register_hook` | 监听生命周期事件 |

而 `ctx.llm` 是首个无需依赖上述任何扩展，即可让插件**独立地**使用用户当前正在使用的模型进行运行的接口。它的唯一功能就是实现这一点。如果您的插件需要注册代理可调用的工具，请使用 `register_tool`；如果需要响应生命周期事件，则使用 `register_hook`；而无论出于何种原因，无论是结构化请求还是非结构化请求，都需要通过 `ctx.llm` 自行发起模型调用。

## 参考资料

* 实现代码：[`agent/plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/agent/plugin_llm.py)
* 测试用例：[`tests/agent/test_plugin_llm.py`](https://github.com/NousResearch/hermes-agent/blob/main/tests/agent/test_plugin_llm.py)
* 参考插件（配套仓库）：
  * [`plugin-llm-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-example) —— 实现图像输入与结构化数据提取的同步处理
  * [`plugin-llm-async-example`](https://github.com/NousResearch/hermes-example-plugins/tree/main/plugin-llm-async-example) —— 使用 `asyncio.gather()` 实现异步处理
* 辅助客户端（底层引擎）：详见 [提供者运行时](/developer-guide/provider-runtime)。
