---
sidebar_position: 9
title: "Context Engine Plugins"
description: "How to build a context engine plugin that replaces the built-in ContextCompressor"
---

# 构建上下文引擎插件

上下文引擎插件通过另一种策略来替代内置的 `ContextCompressor`，从而实现对话上下文的管理。例如，采用无损上下文管理（LCM）引擎，通过构建知识图谱而非进行有损摘要的方式来实现上下文管理。

## 工作原理

智能体的上下文管理功能基于 `ContextEngine` ABC（位于 `agent/context_engine.py` 文件中）实现。内置的 `ContextCompressor` 即为其默认实现方式，所有插件引擎都必须遵循相同的接口规范。

同一时间**仅能**启用一个上下文引擎，其选择方式由配置决定：

```yaml
# config.yaml
context:
  engine: "compressor"    # default built-in
  engine: "lcm"           # activates a plugin engine named "lcm"
```

插件引擎**绝不会自动激活**——用户必须明确将 `context.engine` 设置为该插件的名称。

## 目录结构

每个上下文引擎都位于 `plugins/context_engine/<名称>/` 目录下：

```
plugins/context_engine/lcm/
├── __init__.py      # exports the ContextEngine subclass
├── plugin.yaml      # metadata (name, description, version)
└── ...              # any other modules your engine needs
```

## ContextEngine ABC 接口规范

您的引擎必须实现这些**必需的**方法：

```python
from agent.context_engine import ContextEngine

class LCMEngine(ContextEngine):

    @property
    def name(self) -> str:
        """Short identifier, e.g. 'lcm'. Must match config.yaml value."""
        return "lcm"

    def update_from_response(self, usage: dict) -> None:
        """Called after every LLM call with the usage dict.

        Update self.last_prompt_tokens, self.last_completion_tokens,
        self.last_total_tokens from the response.
        """

    def should_compress(self, prompt_tokens: int = None) -> bool:
        """Return True if compaction should fire this turn."""

    def compress(self, messages: list, current_tokens: int = None,
                 focus_topic: str = None) -> list:
        """Compact the message list and return a new (possibly shorter) list.

        The returned list must be a valid OpenAI-format message sequence.

        ``focus_topic`` is an optional topic string from manual
        ``/compress <focus>``; engines that support guided compression should
        prioritise preserving information related to it, others may ignore it.
        """
```

### 引擎必须维护的类属性

代理会直接读取这些属性，以便进行显示和日志记录：

```python
last_prompt_tokens: int = 0
last_completion_tokens: int = 0
last_total_tokens: int = 0
threshold_tokens: int = 0        # when compression triggers
context_length: int = 0          # model's full context window
compression_count: int = 0       # how many times compress() has run
```

### 可选方法

这些方法在ABC框架中已预设了合理的默认值，可根据实际需求进行覆盖：

| 方法 | 默认值 | 何时需要覆盖 |
|------|---------|--------------|
| `on_session_start(session_id, **kwargs)` | 无操作 | 需要加载持久化状态（如DAG、数据库） |
| `on_session_end(session_id, messages)` | 无操作 | 需要刷新状态并关闭连接 |
| `on_session_reset()` | 重置令牌计数器 | 存在需要清除的会话级状态 |
| `update_model(model, context_length, ...)` | 更新`context_length`与阈值 | 在更换模型时需要重新计算资源预算 |
| `get_tool_schemas()` | 返回`[]` | 您的引擎提供了可供智能体调用的工具（例如`lcm_grep`） |
| `handle_tool_call(name, args, **kwargs)` | 返回错误JSON | 您实现了工具处理逻辑 |
| `should_compress_preflight(messages)` | 返回`False` | 可以在API调用前进行简单的成本预估 |
| `get_status()` | 返回标准的令牌/阈值字典 | 需要暴露自定义指标 |
| `select_context(request_messages, *, conversation_messages, incoming_message, budget_tokens)` | 返回`None`（无操作） | 需要选择或路由哪部分上下文进入**当前**请求（如信息检索、主题路由）——详见下文 |
| `on_turn_complete(messages, usage=None, **kwargs)` | 无操作 | 需要处理/索引/监控已完成的对话轮次——详见下文 |

## 单轮对话上下文的选择与监控

`compress()` 的功能在于解决“上下文过长→需予以压缩”的问题。另有两个可选的、默认为空操作的钩子用于处理相互独立的*选择/观察*维度，因此引擎无需再强制将 `should_compress()` 设置为 `True`，也不必滥用 `compress()` 作为每轮对话的回调函数。

```python
def select_context(self, request_messages, *, conversation_messages=None,
                   incoming_message=None, budget_tokens=0):
    """Choose/replace the context for THIS request, before dispatch.

    Return a new message list to use for this one provider call (retrieval,
    topic routing, role/branch switching), or None to leave it unchanged.
    Request-only: the persisted conversation history is never mutated.
    """

def on_turn_complete(self, messages, usage=None, **kwargs):
    """Observe a finished turn after the assistant/tool loop completes.

    Receives a shallow copy of the finalized transcript plus the turn's
    canonical usage dict (or None if no provider response was reached), so the
    engine can ingest/index/summarize for the next select_context(). The return
    value is ignored.
    """
```

契约规则：

- **默认为空操作，失败时保持原样。** 两种模式的默认行为均为`return None`。若钩子函数缺失、发生异常或返回无效值，请求将保持不变——因此，即便引擎运行失败，其效果也绝不比未安装引擎更差。此外，系统还会对继承自ABC类的默认实现进行身份验证并直接跳过，这意味着那些未实现该功能的引擎（包括内置的压缩器）完全无需为每个请求付出任何处理成本。
- **`select_context()`仅用于处理单个请求。** 函数返回的列表会替代单次提供商调用的响应内容，但不会保存任何历史记录。若返回`None`、`[]`、非列表类型，或包含非字典元素的列表，请求将保持原样未被修改。
- **排序与缓存稳定性。** 该钩子函数会在提示词缓存控制机制及所有请求清洗器之前执行，因此：(a) 替换后的内容仍需通过与普通请求相同的验证流程；(b) 由于默认为空操作，请求内容在字节级完全不变——对于未实现该功能的引擎而言，其提示词缓存行为也不会发生改变。而那些会替换列表内容的引擎，仅会更改自身的缓存前缀。该函数会针对每个提供商请求单独计算（在重试时也会重新执行）。
- **`on_turn_complete()`** 仅用于轮次结束后的观测，其对应的 `messages` 数据为只读属性。该钩子的触发属于尽力而为机制：它会在标准的轮次结束节点被触发。但在循环中存在的一些异常的提前返回路径（例如内容策略拦截或服务提供方故障）会直接返回而不会经过最终处理环节，因此这类情况不会触发此钩子——请将其视为对已完成轮次的尽力观测手段，而非所有提前退出场景都会触发的保证性回调。将所有终止路径统一纳入同一个最终处理节点，是后续需要解决的另一个问题。

### 何时使用这些钩子——以及何时不应使用

- **仅当您的模型引擎必须*替换*每次请求对应的上下文时，才需实现 `select_context()`**，例如基于检索增强的内容选择、主题/分支路由、角色切换等功能。这是唯一能够决定哪些消息会被纳入请求的函数：根据官方设计，`pre_llm_call` 插件钩子仅具备注入功能（它只会追加到用户输入的消息中，绝不会重写整个消息列表，以此保留提示词缓存的前缀）。如果无需替换上下文，则无需实现该函数。
- **如果您的插件仅需要对对话轮次进行观察/数据收集**（如索引构建、内存同步、数据分析等），则应实现**内存提供器**（`sync_turn()`——详见[内存提供器插件](./memory-provider-plugin.md)），而非使用上下文引擎。上下文引擎负责管理会话的压缩策略，而内存提供器仅负责观察对话轮次，不承担任何管理职责。`on_turn_complete()`函数是为那些*已经需要*调用`select_context()`的引擎设计的观察机制——这样同一个组件就可以从刚刚处理的对话轮次中学习经验，而非作为通用的对话轮次回调函数。
- **真实调用`select_context()`对提示缓存的影响**。非空操作的选中操作会自然改变相关对话轮次的提示缓存前缀——因为该请求的前缀不再与提供器缓存的前缀匹配，因此这些轮次需要重新生成缓存而非直接读取。引擎应在“没有任何变化”时返回**稳定的选中结果**（即相同的对象或等价的列表），仅在实际的路由决策发生变化时才调整上下文；如果每次对话轮次都随机改变选中结果，那么就意味着每轮都无法复用缓存。

## 引擎工具

上下文引擎可以暴露供智能体直接调用的工具。需通过`get_tool_schemas()`返回工具的架构定义，并在`handle_tool_call()`中处理相应的调用请求：

```python
def get_tool_schemas(self):
    return [{
        "name": "lcm_grep",
        "description": "Search the context knowledge graph",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"],
        },
    }]

def handle_tool_call(self, name, args, **kwargs):
    if name == "lcm_grep":
        results = self._search_dag(args["query"])
        return json.dumps({"results": results})
    return json.dumps({"error": f"Unknown tool: {name}"})
```

在代理启动时，引擎工具会被自动添加到其工具列表中并立即被调用——无需进行任何注册操作。

## 注册方式

### 通过目录方式（推荐）

将您的引擎放置于 `plugins/context_engine/<名称>/` 目录下。该目录下的 `__init__.py` 文件必须导出一个 `ContextEngine` 的子类，发现系统便会自动定位并实例化该类。

### 通过通用插件系统

普通插件同样可以用来注册上下文引擎：

```python
def register(ctx):
    engine = LCMEngine(context_length=200000)
    ctx.register_context_engine(engine)
```

仅允许注册一个引擎。若尝试再次注册第二个插件，系统会发出警告并拒绝该操作。

## 生命周期

```
1. Engine instantiated (plugin load or directory discovery)
2. on_session_start() — conversation begins
3. update_from_response() — after each API call
4. should_compress() — checked each turn
5. compress() — called when should_compress() returns True
6. on_session_end() — session boundary (CLI exit, /reset, gateway shutdown)
```

当访问 `/new` 或 `/reset` 接口时，系统会调用 `on_session_reset()` 函数，从而在无需完全关闭服务的情况下清除当前会话的状态。

## 配置方式

用户可通过 `hermes plugins` → Provider Plugins → Context Engine 来选择对应的引擎，也可直接编辑 `config.yaml` 文件进行配置：

```yaml
context:
  engine: "lcm"   # must match your engine's name property
```

`compression` 配置块（如 `compression.threshold`、`compression.protect_last_n` 等）专为内置的 `ContextCompressor` 设计，但有一个明显的例外：`compression.model_thresholds`（针对不同模型的阈值覆盖设置）属于上下文引擎的规范范畴。主机会在首次调用 `update_model()` 之前，将处理后的映射值赋给 `engine.model_thresholds`，随后基类的 `update_model()` 函数会应用该值（采用最长子串匹配规则，若无法匹配则回退至引擎配置的阈值）。那些重写了 `update_model()` 函数的引擎可自行定义压缩策略，并选择是否使用该映射值——可通过 `from agent.context_compressor import resolve_model_threshold` 来复用相同的解析逻辑。对于其他所有配置项，如果需要，引擎也应自行定义配置格式，在初始化时从 `config.yaml` 中读取相关数据。

## 测试

```python
from agent.context_engine import ContextEngine

def test_engine_satisfies_abc():
    engine = YourEngine(context_length=200000)
    assert isinstance(engine, ContextEngine)
    assert engine.name == "your-name"

def test_compress_returns_valid_messages():
    engine = YourEngine(context_length=200000)
    msgs = [{"role": "user", "content": "hello"}]
    result = engine.compress(msgs)
    assert isinstance(result, list)
    assert all("role" in m for m in result)
```

完整的 ABC 接口测试套件请参见 `tests/agent/test_context_engine.py`。

## 线程安全性

当 `compression.context_timeout_seconds > 0`（默认值）时，Hermes 会在一个带有主机端超时控制的共享守护线程上执行整个压缩流程——这包括您引擎中的 `compress()` 方法及边界回调函数，以及任何内存提供者实现的 `on_pre_compress` / `on_session_switch` 函数。因此，您的引擎必须做好以下准备：

- 调用可能来自任意一个共享线程。请勿依赖线程亲和性或与对话线程共享的 `threading.local` 状态。
- 您接收到的消息列表为私有的深度快照；虽然允许直接修改该列表（遵循旧版接口规范），但只有当压缩流程完成提交后，这些修改才会显现出来。在主机端超时发生后，仍在运行的任务将被丢弃——绝不能在提交之前将数据发布到外部或持久化存储中。
- 不同会话的压缩流程可以在共享线程池中的不同线程上并行执行；而跨会话共享的单一引擎/提供者实例则必须具备线程安全性。

## 参考资料

- [上下文压缩与缓存](/developer-guide/context-compression-and-caching) —— 内置压缩器的工作原理
- [内存提供者插件](/developer-guide/memory-provider-plugin) —— 用于内存管理的类似单选插件系统
- [插件](/user-guide/features/plugins) —— 插件系统概述
