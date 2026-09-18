---
sidebar_position: 8
title: "Memory Provider Plugins"
description: "How to build a memory provider plugin for Hermes Agent"
---

# 构建内存提供者插件

内存提供者插件能为 Hermes Agent 提供持久化的、跨会话的知识存储能力，弥补内置的 MEMORY.md 和 USER.md 的不足。本指南将介绍如何构建此类插件。

:::tip
内存提供者是两种**提供者插件**类型之一。另一种为[上下文引擎插件](/developer-guide/context-engine-plugin)，用于替代内置的上下文压缩器。这两种插件都遵循相同的架构模式：单选式配置、通过 `hermes plugins` 进行管理。
:::

## 安装位置

Hermes 会按以下优先级从四个来源查找内存提供者：

| 来源 | 位置 | 备注 |
|---|---|---|
| 内置 | `plugins/memory/<名称>/` | 随 Hermes 一起提供。不再接受新的提供者——详情请参阅[贡献指南](https://github.com/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md)。 |
| 用户自定义 | `$HERMES_HOME/plugins/<名称>/` | 由用户根据个人配置手动添加。 |
| 项目级 | `./.hermes/plugins/<名称>/` | 需通过 `HERMES_ENABLE_PROJECT_PLUGINS=1` 启用。 |
| 包管理 | `hermes_agent.memory_providers` 入口点 | 通过 `pip install` 安装，无需复制任何文件。 |

当名称发生冲突时，优先级较高的来源会覆盖较低优先级的来源，因此用户手动添加的目录永远不会替代已内置的提供者。

:::note
这与常规插件系统的“后添加者优先”规则相反。内存提供者是通过*名称*（`memory.provider`）来激活的，因此如果出现名称冲突，会导致代理的内存被悄悄重定向，而不仅仅是工具被覆盖。
:::

“发现”功能仅用于*枚举*，而绝不会导入任何提供者。在`memory.provider`明确指定其名称之前，不会有任何操作被执行。

### 目录提供者

当与Hermes一同打包时，目录提供者位于`plugins/memory/<name>/`路径下；由用户自行安装时则位于`$/HERMES_HOME/plugins/<name>/`路径下；而对于项目本地使用的提供者，则位于`./.hermes/plugins/<name>/`路径下。

```
plugins/memory/my-provider/
├── __init__.py      # MemoryProvider implementation + register() entry point
├── plugin.yaml      # Metadata (name, description, hooks)
└── README.md        # Setup instructions, config reference, tools
```

### 打包后的提供者

通过 pip 安装的提供者会在 `hermes_agent.memory_providers` 组中注册一个入口点。该入口点的名称即为用户在 `memory.provider` 中所选择的提供者名称，而其值则指向该提供者的 `register(ctx)` 函数：

```toml title="pyproject.toml"
[project.entry-points."hermes_agent.memory_providers"]
my-provider = "my_provider:register"
```

请将入口点指向该**包**，或其内部的 `register(ctx)` 函数，同时将您的实现代码、技能模块及其他资源按照常规的 Python 包结构进行组织。无需在 `$HERMES_HOME/plugins/` 目录下创建副本。

包形式的入口点具备目录安装方式的所有功能，包括 Hermes 会直接从磁盘读取而非导入的两个文件——`config_schema.py`（用于控制面板配置）和 `cli.py`（包含您的 `hermes <provider>` 子命令）。这两个文件均位于包的 `__init__.py` 文件旁，因此如果您发布的是包而非单个模块，请将入口点指向整个包。 

## MemoryProvider 抽象基类

您的插件需要实现来自 `agent/memory_provider.py` 的 `MemoryProvider` 抽象基类：

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
|--------|-----------|-----------------|
| `name`（属性） | 始终调用 | **是** |
| `is_available()` | 智能体初始化时，激活前调用 | **是** —— 不允许进行网络请求 |
| `initialize(session_id, **kwargs)` | 智能体启动时调用 | **是** |
| `get_tool_schemas()` | 初始化完成后，用于工具注入 | **是** |
| `handle_tool_call(tool_name, args, **kwargs)` | 智能体使用用户提供的工具时调用 | **是**（仅当您提供了工具时） |

### 配置相关方法

| 方法 | 用途 | 是否必须实现？ |
|--------|---------|-----------------|
| `get_config_schema()` | 定义用于 `hermes memory setup` 的配置字段 | **是** |
| `save_config(values, hermes_home)` | 将非敏感配置保存到系统默认路径 | **是**（除非仅依赖环境变量） |

### 可选钩子函数

| 方法 | 调用时机 | 使用场景 |
|------|----------|----------|
| `system_prompt_block()` | 系统提示词组装阶段 | 处理静态提供者信息 |
| `prefetch(query, *, session_id="")` | 每次 API 调用之前 | 返回已缓存的上下文 |
| `queue_prefetch(query, *, session_id="")` | 每轮对话结束后 | 为下一轮对话预加载数据 |
| `sync_turn(user, assistant, *, session_id="", messages=None)` | 每轮对话完成后 | 保存对话记录 |
| `on_session_end(messages)` | 对话结束时 | 执行最终数据提取/清理操作 |
| `on_pre_compress(messages)` | 上下文压缩之前 | 在数据被丢弃前保存关键信息 |
| `on_memory_write(action, target, content)` | 内置内存写入操作时 | 将数据同步至您的后端系统 |
| `shutdown()` | 进程退出时 | 清理所有连接 |

### 超大尺寸的预加载结果处理

当外部 `prefetch()` 方法返回的结果超过预设的溢出阈值时，这些数据会被写入一个私有的溢出文件中，并替换为按配置生成的头部/尾部预览内容。该预览会包含完整数据的路径，以便智能体在真正需要时读取全部内容；而处于或低于阈值范围内的结果则会被原样返回。

此功能会使用共享的 `hooks.output_spill` 配置参数（默认为 10,000 字符），详情请参阅[插件 —— 超大上下文溢出处理](/developer-guide/plugins/#oversized-context-spill)。

## 预压缩检查点机制（失败即终止）

`on_pre_compress()` 默认采用尽力而为的模式：如果对应的提供程序出现异常，主机仅会记录该错误并继续执行压缩操作。这种默认设置非常适合用于信息提取场景；但对于那些需要在有损重写之前将转录内容存档到持久存储介质中的提供程序而言，则并不适用。针对这类需求，主机提供了可选的检查点接口（API v2）：

```python
from agent.memory_provider import MemoryProvider

class MyArchivingProvider(MemoryProvider):
    # Opt in: every successful on_pre_compress() return means the durable
    # checkpoint is committed. Raise on any failure — do not return partial
    # success. Version 1 (the inherited default) is the implicit historical
    # contract: best-effort semantics, raw message list.
    pre_compress_checkpoint_api_version = 2

    def on_pre_compress(self, messages, *, require_checkpoint=False):
        # require_checkpoint mirrors the operator's checkpoint_required
        # setting: True means a raise here blocks the lossy rewrite.
        ids = self._archive(messages)   # must be durable before returning
        return f"checkpoint: {ids}"     # forwarded into the summary prompt
```

操作员可针对每项部署启用强制规则执行：

```yaml
compression:
  checkpoint_required: true   # default: false
```

当该功能开启时，除非有正在运行的提供者已完成检查点操作，否则在任何有损重写发生之前，压缩过程都会**被强制阻止**：未压缩的转录内容将会保留，压缩尝试会以`BLOCKED_MISSING_PREREQUISITE`错误告终，且需待存储系统恢复后才能重新尝试。若该功能处于关闭状态（默认），现有提供者的工作方式不会发生任何变化。

该功能会作用于所有的压缩机制，而不仅限于Hermes摘要生成器：在功能开启期间，服务器端的原生压缩功能（`compression.codex_responses_native`）会被禁用；轮次后的微压缩功能（`compression.micro_compact`）会在代理启动时被强制关闭，因为它会将旧对话记录整合到连续的摘要中，且其处理流程中不包含检查点机制；同时`codex_app_server` API模式也将在代理启动时被拒绝——因为Codex代理会在自己的线程中进行压缩，且不存在明确的预压缩边界，因此无法确保必要的检查点存在。唯有具备检查点感知功能的Hermes压缩器仍是唯一可进行有损压缩的机制。

您的提供方所接收的内容取决于其声明的 API 版本。版本 1 的提供方（即默认的现有所有提供方）会遵循原有的协议：仍以与之前完全一致的形式返回原始消息列表。而版本 2 的检查点提供方则会收到经过规范化的直接证据——仅包含用户/助手的文本行；工具结果、系统消息以及助手消息中的 `tool_calls` 载荷（其文本内容会被保留）等信息，都会在主机端被过滤掉。以往的摘要可通过一个持久存在的 `_compressed_summary` 消息标记来识别，该标记即便在进程重启后依然存在，因此恢复会话时不会将新的衍生摘要再次写入您的归档文件中。

**检查点必须具备幂等性。** 在发生故障中断后，下一次压缩尝试会使用相同的对话记录再次调用 `on_pre_compress()` 函数——即使对话记录仅有少量新增内容，所产生的证据也大多会存在重叠。建议按照内容（例如对话记录的摘要）对归档文件进行键值化管理并执行插入或更新操作，这样即便出现重试或数据重叠，也能实现去重，而非积累重复的归档文件。

协议测试文件：`tests/agent/test_pre_compress_checkpoint_contract.py`。

## 配置架构

`get_config_schema()` 函数会返回 `hermes memory setup` 所使用的字段描述符列表：

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

:::提示 最简架构与完整架构的对比
在 `hermes memory setup` 过程中，`get_config_schema()` 中列出的所有字段都将会被询问。那些具有大量选项的提供程序应采用最简架构——仅包含用户**必须**配置的字段（如 API 密钥、必需的凭证信息）。可选设置则应记录在配置文件引用中（例如 `$HERMES_HOME/myprovider.json`），而无需在设置过程中逐一询问。这样一来既能加快设置速度，又能支持高级配置。Supermemory 提供程序就是一个很好的例子——它仅要求用户输入 API 密钥，其余所有选项都存储在 `supermemory.json` 文件中。
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

对于仅依赖环境变量的提供程序，请保持默认的无效操作不变。

## 插件入口点

需完整处理输入内容，不得提前终止。

```python
def register(ctx) -> None:
    """Called by the memory plugin discovery system."""
    ctx.register_memory_provider(MyMemoryProvider())
```

某个提供程序也可以通过同一个回调函数来暴露只读技能。这些技能会依据入口点名称进行识别，并且仅在该内存提供程序处于激活状态时才会被加载。

```python
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "skills"

def register(ctx) -> None:
    ctx.register_memory_provider(MyMemoryProvider())
    ctx.register_skill(
        "maintenance",
        SKILLS_DIR / "maintenance" / "SKILL.md",
        "Maintain the provider's memory store",
    )
```

当 `my-provider` 入口点处于激活状态时，该技能可通过 `skill_view()` 以 `my-provider:maintenance` 的形式被调用。  

## plugin.yaml

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

`messages` 是一个可选的、采用 OpenAI 风格的对话上下文，用于记录当前轮次结束时的信息。当该参数存在时，其中会包含用户与助手的对话内容、助手发起的工具调用以及工具的响应结果。那些无需完整轮次上下文的提供方可以省略 `messages` 参数；Hermes 仍会使用旧版的签名格式继续向它们发送请求。

云服务提供商应明确说明 `messages` 中哪些部分会被传输到设备外部。工具调用及其响应结果中可能包含文件路径、命令输出或其他工作区数据。

## 配置文件隔离

所有的存储路径**必须**使用 `initialize()` 函数中的 `hermes_home` 参数来指定，不得直接硬编码为 `~/.hermes`：

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

内存提供程序插件可以注册自己的 CLI 子命令树（例如 `hermes my-provider status`、`hermes my-provider config`）。该机制采用基于规则的发现系统，无需修改核心文件。

### 工作原理

1. 在插件目录中添加一个 `cli.py` 文件
2. 定义一个 `register_cli(subparser)` 函数来构建 argparse 命令树
3. 内存插件系统会在启动时通过 `discover_plugin_cli_commands()` 发现这些命令
4. 您定义的命令将显示为 `hermes <provider-name> <subcommand>` 的形式

**活动提供程序限制：** 只有当您的提供程序被配置为当前活跃的 `memory.provider` 时，其 CLI 命令才会显示。如果用户未配置您的提供程序，这些命令就不会出现在 `hermes --help` 的输出中。

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

同一时间只能有**一个**外部内存提供者处于激活状态。如果用户试图注册第二个提供者，MemoryManager会发出警告并拒绝该操作。这一机制有助于避免工具架构变得臃肿，同时防止不同后端之间产生冲突。
