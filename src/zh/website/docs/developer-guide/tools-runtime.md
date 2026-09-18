---
sidebar_position: 9
title: "Tools Runtime"
description: "Runtime behavior of the tool registry, toolsets, dispatch, and terminal environments"
---

# 工具运行时

Hermes工具为自注册函数，它们被归类到不同的工具集中，并通过中央注册/调度系统来执行。

主要文件包括：

- `tools/registry.py`
- `model_tools.py`
- `toolsets.py`
- `tools/terminal_tool.py`
- `tools/environments/*`

## 工具注册机制

每个工具模块在导入时都会调用`registry.register(...)`函数。

`model_tools.py`负责导入/发现各类工具模块，并构建模型所使用的架构列表。

### `registry.register()`的工作原理

`tools/`目录下的每个工具文件都会在模块级别调用`registry.register()`来声明自身。该函数的签名如下：

```python
registry.register(
    name="terminal",               # Unique tool name (used in API schemas)
    toolset="terminal",            # Toolset this tool belongs to
    schema={...},                  # Model-facing schema (description, parameters)
    handler=handle_terminal,       # The function that executes when the tool is called
    check_fn=check_terminal,       # Optional: returns True/False for availability
    requires_env=["SOME_VAR"],     # Optional: env vars needed (for UI display)
    is_async=False,                # Whether the handler is an async coroutine
    description="Run commands",    # Optional ToolEntry registry metadata
    emoji="💻",                    # Emoji for spinner/progress display
)
```

每次调用都会创建一个 `ToolEntry` 对象，该对象会被存储在单例 `ToolRegistry._tools` 字典中，以工具名称作为键。除非调用者设置 `override=True`，否则任何试图覆盖**其他工具集**中已有工具的注册请求都会被拒绝（并记录错误日志）；而对于内置工具的插件覆盖，还需操作员在 `config.yaml` 中设置 `plugins.entries.<plugin_id>.allow_tool_override: true` 才能生效。

`schema["description"]` 是面向模型的官方描述。单独的 `description=` 参数会用于填充 `ToolEntry.description`；若省略该参数，则注册表元数据将自动采用架构描述中的内容。`get_definitions()` 函数会根据 `entry.schema` 生成 OpenAI 函数定义，且不会将 `entry.description` 复制到缺少 `description` 字段的架构中。因此，仅使用 `description=` 是无法向模型描述工具的；当两者内容不同时，模型将优先采用架构中的描述。除非注册表的使用者有特殊需求，否则建议直接在架构中定义描述。

### 工具发现：`discover_builtin_tools()`

当导入 `model_tools.py` 时，它会调用 `tools/registry.py` 中的 `discover_builtin_tools()` 函数。该函数会通过 AST 解析扫描所有的 `tools/*.py` 文件，找出包含顶层 `registry.register()` 调用的模块，随后将其导入。

```python
# tools/registry.py (simplified)
def discover_builtin_tools(tools_dir=None):
    tools_path = Path(tools_dir) if tools_dir else Path(__file__).parent
    for path in sorted(tools_path.glob("*.py")):
        if path.name in {"__init__.py", "registry.py", "mcp_tool.py"}:
            continue
        if _module_registers_tools(path):  # AST check for top-level registry.register()
            importlib.import_module(f"tools.{path.stem}")
```

这种自动发现机制意味着新的工具文件会自动被识别——无需手动维护列表。AST检查仅匹配顶层的`registry.register()`调用（不会检测函数内部的调用），因此`tools/`目录中的辅助模块不会被导入。

每次导入操作都会触发该模块的`registry.register()`调用。对于可选工具中存在的错误（例如图像生成功能缺少`fal_client`），系统会捕获并记录这些错误——它们不会阻碍其他工具的加载。

在完成核心工具的发现后，还会继续发现MCP工具和插件工具：

1. **MCP工具** — `tools.mcp_tool_discovery.discover_mcp_tools()`（由`tools.mcp_tool`接口重新导出）会读取MCP服务器配置，并注册来自外部服务器的工具。
2. **插件工具** — `hermes_cli.plugins.discover_plugins()`会加载用户、项目或pip安装的插件，这些插件可能会注册额外的工具。

## 工具可用性检查（`check_fn`）

每个工具都可以可选地提供一个`check_fn`——即一个可调用函数，当工具可用时返回`True`，否则返回`False`。常见的检查方式包括：

- **API密钥是否存在** — 例如，用于网络搜索的`lambda: bool(os.environ.get("SERP_API_KEY"))`
- **服务是否正在运行** — 例如检查Honcho服务器是否已配置
- **二进制文件是否已安装** — 例如验证浏览器工具是否已安装`playwright`

当`registry.get_definitions()`为模型构建架构列表时，它会依次执行每个工具的`check_fn()`：

```python
# Simplified from registry.py
if entry.check_fn:
    try:
        available = bool(entry.check_fn())
    except Exception:
        available = False   # Exceptions = unavailable
    if not available:
        continue            # Skip this tool entirely
```

主要行为特点：
- 检查结果会**按每次调用进行缓存**——若多个工具使用相同的 `check_fn`，则该函数仅执行一次。
- `check_fn()` 中抛出的异常会被视为“工具不可用”（属于安全保护机制）。
- `is_toolset_available()` 方法用于检测某个工具集的 `check_fn` 是否通过验证，其结果会用于界面显示及工具集筛选。

## 工具集筛选机制

工具集是由多个工具组成的命名包。Hermes 通过以下方式对工具集进行筛选：
- 明确指定的已启用/已禁用工具集列表
- 平台预设（如 `hermes-cli`、`hermes-telegram` 等）
- 动态 MCP 工具集
- 专门定制的专用工具集，例如 `hermes-acp`

### `get_tool_definitions()` 的工具筛选方式

该函数是主要的工具筛选入口，其调用方式为 `model_tools.get_tool_definitions(enabled_toolsets, disabled_toolsets, quiet_mode)`：
1. **若提供了 `enabled_toolsets`**——仅包含属于这些工具集的工具。每个工具集名称会通过 `resolve_toolset()` 函数进行处理，该函数会将复合型工具集拆解为各个独立的工具名称。
2. **若提供了 `disabled_toolsets`**——首先列出所有工具集，再从中剔除被禁用的工具集。
3. **若未提供上述参数**——包含所有已知的工具集。
4. **注册表筛选**——处理后的工具名称列表会被传递给 `registry.get_definitions()`，该函数会应用 `check_fn` 进行进一步筛选，并返回符合 OpenAI 格式的工具定义。
5. **动态架构补丁生成**——在完成筛选后，`execute_code` 和 `browser_navigate` 等工具的架构定义会进行动态调整，仅保留那些真正通过筛选的工具（从而避免模型虚构出不存在的工具）。
### 旧版工具集名称

为保持向后兼容性，那些带有 `_tools` 后缀的旧版工具集名称（例如 `web_tools`、`terminal_tools`）会通过 `_LEGACY_TOOLSET_MAP` 映射为对应的现代工具名称。

## 调度机制

在运行时，工具会通过中央注册表进行调度；而对于内存管理、待办事项处理、会话搜索等部分需在代理层处理的工具，则会通过代理循环机制来处理异常情况。

### 调度流程：模型发起 tool_call → 执行处理器

当模型返回 `tool_call` 后，流程如下：

```
Model response with tool_call
    ↓
agent loop (`agent/conversation_loop.py`, via `run_agent.py`'s `AIAgent` facade)
    ↓
model_tools.handle_function_call(name, args, task_id, user_task)
    ↓
[Agent-loop tools?] → handled directly by agent loop (todo, memory, session_search, delegate_task)
    ↓
[Plugin pre-hook] → invoke_hook("pre_tool_call", ...)
    ↓
registry.dispatch(name, args, **kwargs)
    ↓
Look up ToolEntry by name
    ↓
[Async handler?] → bridge via _run_async()
[Sync handler?]  → call directly
    ↓
Return result string (or JSON error)
    ↓
[Plugin post-hook] → invoke_hook("post_tool_call", ...)
```

### 错误处理机制

所有工具的执行过程都包含两层错误处理机制：

1. **`registry.dispatch()`** —— 捕获处理函数中抛出的任何异常，并以 JSON 格式返回 `{"error": "Tool execution failed: ExceptionType: message"}`。

2. **`handle_function_call()`** —— 为整个调度过程添加额外的 try/except 机制，最终返回 `{"error": "Error executing tool_name: message"}`。

这样的设计可确保模型始终收到格式规范的 JSON 字符串，而不会遇到未处理的异常。

### 需要代理级状态的工具

有四种工具会在被发送到注册表之前就被拦截，因为它们需要使用代理级的状态存储（如 TodoStore、MemoryStore 等）：

- `todo` —— 用于任务规划与跟踪
- `memory` —— 用于持久化内存写入
- `session_search` —— 用于跨会话信息检索
- `delegate_task` —— 用于创建子代理会话

虽然这些工具的架构定义仍会注册在注册表中（以便通过 `get_tool_definitions` 获取），但如果调度流程直接触发了它们，其处理函数会返回一个占位错误信息。

### 异步操作的桥接处理

当某个工具的处理函数为异步时，`_run_async()` 会将其与同步调度路径相连接：

- **CLI 路径（无运行循环）** —— 使用持久化的事件循环来保持缓存的异步客户端处于活跃状态
- **网关路径（有运行循环）** —— 通过 `asyncio.run()` 启动一个临时线程
- **工作线程（并行工具）** —— 利用存储在线程本地存储中的逐线程持久化循环

## DANGEROUS_PATTERNS 审批流程

终端工具集成了在 `tools/approval.py` 中定义的危险命令审批系统：

1. **模式检测** — `DANGEROUS_PATTERNS` 是一个包含 `(正则表达式, 描述)` 元组的列表，用于识别具有破坏性的操作：
   - 递归删除（如 `rm -rf`）
   - 文件系统格式化（如 `mkfs`、`dd`）
   - 有害的 SQL 操作（如 `DROP TABLE`、无 `WHERE` 条件的 `DELETE FROM`）
   - 系统配置覆盖（如 `> /etc/`）
   - 服务操作（如 `systemctl stop`）
   - 远程代码执行（如 `curl | sh`）
   - 分叉炸弹、进程强制终止等。

2. **检测机制** — 在执行任何终端命令之前，`detect_dangerous_command(command)` 函数会将该命令与所有预设模式进行比对。

3. **审批提示** — 若检测到匹配项：
   - **CLI 模式** — 系统会弹出交互式提示，要求用户批准、拒绝或永久允许该操作。
   - **网关模式** — 通过异步审批回调将请求发送至消息平台。
   - **智能审批** — 可选地，辅助大型语言模型可自动批准符合模式的低风险命令（例如，`rm -rf node_modules/` 虽有破坏性，但属于递归删除模式）。

4. **会话状态** — 批准记录会按会话单独保存。一旦您在某个会话中批准了“递归删除”操作，后续的 `rm -rf` 命令将不再触发重复提示。

5. **永久允许列表** — “永久允许”选项会将相关模式写入 `config.yaml` 文件中的 `command_allowlist` 字段，从而在多个会话之间保持有效。

## 终端/运行时环境

该终端系统支持多种后端环境：

- 本地环境
- Docker 容器
- SSH 连接
- Singularity 环境
- Modal 平台
- Daytona 平台
- Vercel 沙箱环境

此外，它还支持：

- 每个任务的当前工作目录覆盖设置  
- 后台进程管理  
- 真实终端模式  
- 高风险命令的审批回调机制  

`tools/process_registry_checkpoint.py` 负责管理运行中进程的快照以及与进程标识符（PID）安全相关的操作。处理完成的输出会单独保存：`tools/process_registry_results.py` 会在配置文件指定的 `logs/process-results/` 目录下，为每个进程生成一份完整的、已脱敏的处理记录。生产者无法通过重写共享的 PID 快照来覆盖其他生产者的结果。注册表会在释放完成事件之前先保存该记录，而一次性延迟机制则会等待这一事件触发。现有的进程查询方法会直接加载已保留的快照，无需依赖 PID 或发送通知。读取操作需要使用持久化会话或其压缩续传功能；仅知道进程标识符并不足以授权读取已保留的结果。无论是在命令行界面还是不发送通知的进程中，注册表都会在启动任何输出读取器之前确定该进程的所有者，并在读取线程中保留生产者的配置上下文。记录的脱敏操作是独立于实时输出禁用选项来执行的；记录的保留时间受时长和数量限制。  

## 并发性  

根据所使用的工具组合及交互需求，工具调用可以顺序执行，也可以同时执行。  

## 相关文档  

- [工具集参考](../reference/toolsets-reference.md)  
- [内置工具参考](../reference/tools-reference.md)  
- [Agent循环内部机制](./agent-loop.md)  
- [ACP内部机制](./acp-internals.md)
