---
sidebar_position: 8
title: "Memory Provider Plugins"
description: "How to build a memory provider plugin for Hermes Agent"
---

# 构建内存提供者插件

内存提供者插件能够为 Hermes Agent 提供持久化的、跨会话的知识存储能力，弥补内置的 MEMORY.md 和 USER.md 的不足。本指南将介绍如何构建此类插件。

:::tip
内存提供者是两种**提供者插件**类型之一。另一种为 [上下文引擎插件](/developer-guide/context-engine-plugin)，它用于替代内置的上下文压缩器。这两种插件均遵循相同的架构模式：单选式配置、通过 `hermes plugins` 进行管理。
:::

## 目录结构

每个内存提供者插件都位于 `plugins/memory/<名称>/` 目录下：

```
plugins/memory/my-provider/
├── __init__.py      # MemoryProvider implementation + register() entry point
├── plugin.yaml      # Metadata (name, description, hooks)
└── README.md        # Setup instructions, config reference, tools
```

## MemoryProvider抽象基类

您的插件需要实现来自`agent/memory_provider.py`的`MemoryProvider`抽象基类：

```python
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-provider"

    def is_available(self) -> bool:
        """Check if this provider can activate. NO network calls."""
        return bool(os.environ.get("MY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        """Called once at agent startup.

        kwargs always includes:
          hermes_home (str): Active HERMES_HOME path. Use for storage.
        """
        self._api_key = os.environ.get("MY_API_KEY", "")
        self._session_id = session_id

    # ... implement remaining methods
```

## 必须实现的方法

### 核心生命周期方法

| 方法 | 调用时机 | 是否必须实现？ |
|------|----------|----------------|
| `name`（属性） | 始终调用 | **是** |
| `is_available()` | Agent初始化时，激活前 | **是** —— 不允许进行网络请求 |
| `initialize(session_id, **kwargs)` | Agent启动时 | **是** |
| `get_tool_schemas()` | 初始化完成后，用于工具注入 | **是** |
| `handle_tool_call(tool_name, args, **kwargs)` | Agent使用用户提供的工具时 | **是**（仅当用户提供了工具时） |

### 配置相关方法

| 方法 | 用途 | 是否必须实现？ |
|------|------|----------------|
| `get_config_schema()` | 定义用于`hermes memory setup`的配置字段 | **是** |
| `save_config(values, hermes_home)` | 将非敏感配置保存到系统指定位置 | **是**（除非仅依赖环境变量） |

### 可选钩子方法

| 方法 | 调用时机 | 适用场景 |
|------|----------|----------|
| `system_prompt_block()` | 系统提示语组装时 | 提供静态的Provider信息 |
| `prefetch(query, *, session_id="")` | 每次API调用之前 | 返回已预取的上下文信息 |
| `queue_prefetch(query)` | 每轮对话结束后 | 为下一轮对话提前预热数据 |
| `sync_turn(user, assistant, *, session_id="")` | 每轮对话完成后 | 保存对话内容以供后续使用 |
| `on_session_end(messages)` | 对话结束时 | 执行最终的数据提取或清理操作 |
| `on_pre_compress(messages)` | 上下文压缩之前 | 在数据被丢弃前保存有价值的洞察信息 |
| `on_memory_write(action, target, content)` | 内置内存写入操作时 | 将数据同步到用户自定义的后端系统 |
| `shutdown()` | 进程退出时 | 清理所有连接资源 |

## 配置架构

`get_config_schema()`方法会返回一份列表，其中包含`hermes memory setup`所使用的所有字段描述信息：

```python
def get_config_schema(self):
    return [
        {
            "key": "api_key",
            "description": "My Provider API key",
            "secret": True,           # → written to .env
            "required": True,
            "env_var": "MY_API_KEY",   # explicit env var name
            "url": "https://my-provider.com/keys",  # where to get it
        },
        {
            "key": "region",
            "description": "Server region",
            "default": "us-east",
            "choices": ["us-east", "eu-west", "ap-south"],
        },
        {
            "key": "project",
            "description": "Project identifier",
            "default": "hermes",
        },
    ]
```

标记为 `secret: True` 且包含 `env_var` 的字段会被保存到 `.env` 文件中。而非机密字段则会传递给 `save_config()` 函数处理。

:::提示 最简架构与完整架构
在 `hermes memory setup` 过程中，`get_config_schema()` 中列出的所有字段都将会被询问。那些拥有大量选项的提供程序应采用最简架构——仅包含用户**必须**配置的字段（如 API 密钥、必需的凭证信息）。可选设置则应记录在配置文件引用中（例如 `$HERMES_HOME/myprovider.json`），而无需在设置过程中逐一询问。这样一来既能加快设置流程，又能支持高级配置功能。Supermemory 提供程序就是一个很好的例子——它仅要求用户输入 API 密钥，其他所有选项都存储在 `supermemory.json` 文件中。
:::

## 保存配置

```python
def save_config(self, values: dict, hermes_home: str) -> None:
    """Write non-secret config to your native location."""
    import json
    from pathlib import Path
    config_path = Path(hermes_home) / "my-provider.json"
    config_path.write_text(json.dumps(values, indent=2))
```

对于仅依赖环境变量的提供程序，请保持默认的无需操作设置不变。

## 插件入口点

需完整处理整个输入内容，不得提前终止。

```python
def register(ctx) -> None:
    """Called by the memory plugin discovery system."""
    ctx.register_memory_provider(MyMemoryProvider())
```

## plugin.yaml 配置文件

```yaml
name: my-provider
version: 1.0.0
description: "Short description of what this provider does."
hooks:
  - on_session_end    # list hooks you implement
```

## 线程契约

**`sync_turn()` 必须为非阻塞式调用。** 如果您的后端存在延迟（如 API 调用、大语言模型处理等），请在后台线程中执行相关操作：

```python
def sync_turn(self, user_content, assistant_content, *, session_id="", messages=None):
    def _sync():
        try:
            self._api.ingest(user_content, assistant_content, session_id=session_id, messages=messages)
        except Exception as e:
            logger.warning("Sync failed: %s", e)

    if self._sync_thread and self._sync_thread.is_alive():
        self._sync_thread.join(timeout=5.0)
    self._sync_thread = threading.Thread(target=_sync, daemon=True)
    self._sync_thread.start()
```

`messages` 是一个可选的、采用 OpenAI 风格的对话上下文，用于记录当前轮次结束时的信息。当该参数存在时，其中会包含用户与助手的消息、助手发起的工具调用以及工具的响应结果。那些无需完整轮次上下文的服务提供商可以省略 `messages` 参数；Hermes 仍会使用旧版的签名格式继续向它们发送请求。

云服务提供商应明确说明 `messages` 中哪些部分会被发送到设备外部。工具调用和工具响应中可能包含文件路径、命令输出或其他工作区数据。

## 配置文件隔离

所有存储路径**必须**使用 `initialize()` 函数中的 `hermes_home` 参数来指定，不得直接硬编码为 `~/.hermes`：

```python
# CORRECT — profile-scoped
from hermes_constants import get_hermes_home
data_dir = get_hermes_home() / "my-provider"

# WRONG — shared across all profiles
data_dir = Path("~/.hermes/my-provider").expanduser()
```

## 测试

如需了解端到端的测试示例，请查看 `tests/agent/test_memory_provider.py` 以及相关的内存功能测试文件（`tests/agent/test_memory_session_switch.py`、`tests/agent/test_memory_user_id.py`、`tests/run_agent/test_memory_provider_init.py`）。

```python
from agent.memory_manager import MemoryManager

mgr = MemoryManager()
mgr.add_provider(my_provider)
mgr.initialize_all(session_id="test-1", platform="cli")

# Test tool routing
result = mgr.handle_tool_call("my_tool", {"action": "add", "content": "test"})

# Test lifecycle
mgr.sync_all("user msg", "assistant msg")
mgr.on_session_end([])
mgr.shutdown_all()
```

## 添加 CLI 命令

内存提供程序插件可以注册自己的 CLI 子命令树（例如 `hermes my-provider status`、`hermes my-provider config`）。该机制采用基于规则的发现系统——无需修改核心文件。

### 工作原理

1. 在插件目录中添加一个 `cli.py` 文件
2. 定义一个 `register_cli(subparser)` 函数，用于构建 argparse 命令树
3. 内存插件系统会在启动时通过 `discover_plugin_cli_commands()` 函数发现这些命令
4. 您定义的命令将显示为 `hermes <provider-name> <subcommand>` 的形式

**活跃提供程序限制：** 只有当您的提供程序被配置为当前的 `memory.provider` 时，其 CLI 命令才会显示。如果用户未配置您的提供程序，这些命令就不会出现在 `hermes --help` 的输出中。

### 示例

```python
# plugins/memory/my-provider/cli.py

def my_command(args):
    """Handler dispatched by argparse."""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("Provider is active and connected.")
    elif sub == "config":
        print("Showing config...")
    else:
        print("Usage: hermes my-provider <status|config>")

def register_cli(subparser) -> None:
    """Build the hermes my-provider argparse tree.

    Called by discover_plugin_cli_commands() at argparse setup time.
    """
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="Show provider status")
    subs.add_parser("config", help="Show provider config")
    subparser.set_defaults(func=my_command)
```

### 参考实现

如需查看包含 13 个子命令、跨配置文件管理（`--target-profile`）以及配置读写功能的完整示例，请参阅 `plugins/memory/honcho/cli.py`。

### 带 CLI 的目录结构

```
plugins/memory/my-provider/
├── __init__.py      # MemoryProvider implementation + register()
├── plugin.yaml      # Metadata
├── cli.py           # register_cli(subparser) — CLI commands
└── README.md        # Setup instructions
```

## 单一提供者规则

同一时间只能有**一个**外部内存提供者处于激活状态。如果用户试图注册第二个提供者，MemoryManager会发出警告并拒绝该操作。这一机制有助于避免工具架构变得臃肿，同时防止不同后端之间出现冲突。
