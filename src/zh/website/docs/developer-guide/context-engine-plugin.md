---
sidebar_position: 9
title: "Context Engine Plugins"
description: "How to build a context engine plugin that replaces the built-in ContextCompressor"
---

# 构建上下文引擎插件

上下文引擎插件通过替代方案来取代内置的 `ContextCompressor`，从而实现更高效的对话上下文管理。例如，采用无损上下文管理（LCM）引擎，通过构建知识有向无环图而非进行有损摘要的方式来处理上下文。

## 工作原理

智能体的上下文管理功能基于 `ContextEngine` ABC（位于 `agent/context_engine.py` 文件中）实现。内置的 `ContextCompressor` 即为其默认实现方式，所有插件引擎都必须遵循相同的接口标准。

同一时间**仅能**启用一个上下文引擎，其选择方式由配置决定：

```yaml
# config.yaml
context:
  engine: "compressor"    # default built-in
  engine: "lcm"           # activates a plugin engine named "lcm"
```

插件引擎**绝不会自动激活**——用户必须手动将 `context.engine` 设置为该插件的名称。

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

智能体会直接读取这些属性，以便进行显示和日志记录：

```python
last_prompt_tokens: int = 0
last_completion_tokens: int = 0
last_total_tokens: int = 0
threshold_tokens: int = 0        # when compression triggers
context_length: int = 0          # model's full context window
compression_count: int = 0       # how many times compress() has run
```

### 可选方法

ABC框架中为这些方法提供了合理的默认值。如有需要，可进行覆盖：

| 方法 | 默认值 | 何时需要覆盖 |
|------|---------|--------------|
| `on_session_start(session_id, **kwargs)` | 无操作 | 需要加载持久化状态（如DAG、数据库） |
| `on_session_end(session_id, messages)` | 无操作 | 需要刷新状态并关闭连接 |
| `on_session_reset()` | 重置令牌计数器 | 需要清除会话级别的状态 |
| `update_model(model, context_length, ...)` | 更新`context_length`与阈值 | 在更换模型时需要重新计算预算 |
| `get_tool_schemas()` | 返回`[]` | 您的引擎提供了可供智能体调用的工具（例如`lcm_grep`） |
| `handle_tool_call(name, args, **kwargs)` | 返回错误JSON | 您已实现了工具处理逻辑 |
| `should_compress_preflight(messages)` | 返回`False` | 可以在API调用前进行简单的成本预估 |
| `get_status()` | 标准的令牌/阈值字典 | 需要展示自定义指标 |

## 引擎工具

上下文引擎可以提供智能体可直接调用的工具。需通过`get_tool_schemas()`返回工具的架构信息，并在`handle_tool_call()`中处理相关调用：

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

将您的引擎放置在 `plugins/context_engine/<名称>/` 目录下。该目录下的 `__init__.py` 文件必须导出一个 `ContextEngine` 的子类，发现系统会自动定位并实例化该类。

### 通过通用插件系统

普通插件同样可以用于注册上下文引擎：

```python
def register(ctx):
    engine = LCMEngine(context_length=200000)
    ctx.register_context_engine(engine)
```

仅允许注册一个引擎。若有第二个插件尝试注册，将会被拒绝并显示警告信息。

## 生命周期

```
1. Engine instantiated (plugin load or directory discovery)
2. on_session_start() — conversation begins
3. update_from_response() — after each API call
4. should_compress() — checked each turn
5. compress() — called when should_compress() returns True
6. on_session_end() — session boundary (CLI exit, /reset, gateway expiry)
```

当访问 `/new` 或 `/reset` 接口时，系统会调用 `on_session_reset()` 函数，从而在无需完全关闭服务的情况下清除当前会话的状态。

## 配置方式

用户可通过 `hermes plugins` → Provider Plugins → Context Engine 来选择对应的引擎，也可直接编辑 `config.yaml` 文件进行配置：

```yaml
context:
  engine: "lcm"   # must match your engine's name property
```

`compression` 配置块（如 `compression.threshold`、`compression.protect_last_n` 等）专为内置的 `ContextCompressor` 设计。如果需要，您的引擎应自行定义配置格式，并在初始化时从 `config.yaml` 中读取相关配置。

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

## 相关内容

- [上下文压缩与缓存](/developer-guide/context-compression-and-caching) —— 内置压缩器的运作原理
- [内存提供者插件](/developer-guide/memory-provider-plugin) —— 用于管理内存的类似单选插件系统
- [插件](/user-guide/features/plugins) —— 插件系统的概述
