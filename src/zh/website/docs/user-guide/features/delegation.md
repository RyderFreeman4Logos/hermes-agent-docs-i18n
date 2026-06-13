---
sidebar_position: 7
title: "Subagent Delegation"
description: "Spawn isolated child agents for parallel workstreams with delegate_task"
---

# 子代理委派

`delegate_task` 工具会创建具有独立上下文、受限工具集以及专属终端会话的子 AIAgent 实例。每个子代理都会拥有全新的对话环境并独立工作——仅有其最终总结会被纳入父代理的上下文中。

## 单任务模式

```python
delegate_task(
    goal="Debug why tests fail",
    context="Error: assertion in test_foo.py line 42",
    toolsets=["terminal", "file"]
)
```

## 并行批处理

默认支持最多同时运行3个子智能体（可配置，无固定上限）：

```python
delegate_task(tasks=[
    {"goal": "Research topic A", "toolsets": ["web"]},
    {"goal": "Research topic B", "toolsets": ["web"]},
    {"goal": "Fix the build", "toolsets": ["terminal", "file"]}
])
```

## 子智能体上下文的工作原理

:::warning 重要提示：子智能体一无所知
子智能体启动时处于**全新的对话状态**。它们对父智能体的对话历史、之前的工具调用记录，以及任务委托之前的任何讨论内容都完全不知情。子智能体所能获取的上下文仅来自父智能体在调用 `delegate_task` 函数时设置的 `goal` 和 `context` 字段。
:::

这意味着父智能体必须在调用中传递子智能体所需的**所有信息**：

```python
# BAD - subagent has no idea what "the error" is
delegate_task(goal="Fix the error")

# GOOD - subagent has all context it needs
delegate_task(
    goal="Fix the TypeError in api/handlers.py",
    context="""The file api/handlers.py has a TypeError on line 47:
    'NoneType' object has no attribute 'get'.
    The function process_request() receives a dict from parse_body(),
    but parse_body() returns None when Content-Type is missing.
    The project is at /home/user/myproject and uses Python 3.11."""
)
```

子代理会接收到一个基于您的目标与上下文生成的精准系统提示，该提示会指示其完成任务，并以结构化的方式总结其操作内容、发现结果、修改过的文件以及遇到的任何问题。

## 实际应用示例

### 并行研究

同时针对多个主题展开研究并汇总相关摘要：

```python
delegate_task(tasks=[
    {
        "goal": "Research the current state of WebAssembly in 2025",
        "context": "Focus on: browser support, non-browser runtimes, language support",
        "toolsets": ["web"]
    },
    {
        "goal": "Research the current state of RISC-V adoption in 2025",
        "context": "Focus on: server chips, embedded systems, software ecosystem",
        "toolsets": ["web"]
    },
    {
        "goal": "Research quantum computing progress in 2025",
        "context": "Focus on: error correction breakthroughs, practical applications, key players",
        "toolsets": ["web"]
    }
])
```

### 代码审查与修复

将审查及修复工作流程委托给全新的上下文环境：

```python
delegate_task(
    goal="Review the authentication module for security issues and fix any found",
    context="""Project at /home/user/webapp.
    Auth module files: src/auth/login.py, src/auth/jwt.py, src/auth/middleware.py.
    The project uses Flask, PyJWT, and bcrypt.
    Focus on: SQL injection, JWT validation, password handling, session management.
    Fix any issues found and run the test suite (pytest tests/auth/).""",
    toolsets=["terminal", "file"]
)
```

### 多文件重构功能

用于处理那些会占据父上下文过多资源的大型重构任务：

```python
delegate_task(
    goal="Refactor all Python files in src/ to replace print() with proper logging",
    context="""Project at /home/user/myproject.
    Use the 'logging' module with logger = logging.getLogger(__name__).
    Replace print() calls with appropriate log levels:
    - print(f"Error: ...") -> logger.error(...)
    - print(f"Warning: ...") -> logger.warning(...)
    - print(f"Debug: ...") -> logger.debug(...)
    - Other prints -> logger.info(...)
    Don't change print() in test files or CLI output.
    Run pytest after to verify nothing broke.""",
    toolsets=["terminal", "file"]
)
```

## 批量模式详解

当您提供 `tasks` 数组时，子代理会通过线程池以**并行方式**运行：

- **最大并发数**：默认为 3 个任务（可通过 `delegation.max_concurrent_children` 或环境变量 `DELEGATION_MAX_CONCURRENT_CHILDREN` 进行配置；下限为 1，无上限限制）。超过此限制的批次会返回工具错误，而不会被悄悄截断。
- **线程池**：使用 `ThreadPoolExecutor`，其最大工作线程数即为配置的并发限制值。
- **进度显示**：在 CLI 模式下，以树状视图实时展示每个子代理的工具调用情况，并显示每项任务的完成状态。在网关模式下，进度会以批次形式传递给父进程的进度回调函数。
- **结果排序**：无论任务完成顺序如何，结果都会按任务索引排序，以保持与输入顺序一致。
- **中断传播**：中断父进程（例如发送新消息）会同时中断所有正在运行的子进程。

单任务委托则无需线程池开销，可直接执行。

## 模型覆盖

您可以通过 `config.yaml` 为子代理配置不同的模型——这对于将简单任务委托给成本更低或响应更快的模型非常有用。

```yaml
# In ~/.hermes/config.yaml
delegation:
  model: "google/gemini-flash-2.0"    # Cheaper model for subagents
  provider: "openrouter"              # Optional: route subagents to a different provider
```

如果未指定，子智能体将使用与父智能体相同的模型。

## 工具集选择建议

`toolsets` 参数用于控制子智能体可使用的工具。请根据任务需求进行选择：

| 工具集模式 | 适用场景 |
|------------|----------|
| `["terminal", "file"]` | 代码编写、调试、文件编辑、构建操作 |
| `["web"]` | 研究、事实核查、文档查询 |
| `["terminal", "file", "web"]` | 全栈任务（默认值） |
| `["file"]` | 只读分析、无需执行的代码审查 |
| `["terminal"]` | 系统管理、进程控制 |

无论您如何指定，某些工具集对子智能体都是不可用的：
- `delegation` — 对叶级子智能体（默认情况）禁用。对于 `role="orchestrator"` 的子智能体则保留可用，但其使用次数受 `max_spawn_depth` 限制——详情请参见下文的[深度限制与嵌套编排](#depth-limit-and-nested-orchestration)。
- `clarify` — 子智能体无法与用户交互
- `memory` — 禁止向共享的持久内存写入数据
- `code_execution` — 子智能体需逐步推理
- `send_message` — 禁止跨平台操作（例如发送 Telegram 消息）

## 最大迭代次数

每个子智能体都有一个迭代次数限制（默认为 50），用于控制其可进行的工具调用轮数：

```python
delegate_task(
    goal="Quick file check",
    context="Check if /etc/nginx/nginx.conf exists and print its first 10 lines",
    max_iterations=10  # Simple task, don't need many turns
)
```

## 子代理超时设置

默认情况下，子代理**不存在基于实际时间的超时限制**。它们仅会因自身实际执行过程中的问题而失败——例如 API 错误、工具故障或迭代次数耗尽——而不会受到上层委托层级计时器的限制。在早期版本中曾设定过硬性上限（300秒，后来改为600秒），这常常导致那些正在执行复杂任务（如深度代码审查、大规模研究分析或运行速度较慢的推理模型）的子代理在任务进行到一半时就被强制终止，而这类任务往往需要10分钟以上的时间才能稳步完成。

系统仍能检测出真正陷入停滞的子代理：当某个子代理没有取得任何进展（既没有发起 API 调用，也没有启动任何工具）时，心跳检测机制会停止向父代理上报其运行状态，进而触发网关的不活跃超时机制，从而终止该卡住的 Worker。

如果您仍希望设置硬性上限（例如为无人监控的定时任务委托机制控制成本），可以在每次安装时手动启用该功能：

```yaml
delegation:
  child_timeout_seconds: 0     # default: 0 = no timeout
  # child_timeout_seconds: 1800  # opt-in hard cap (floor 30s)
```

当设置正值时，将为每个子代理强制设定严格的时钟时间限制；而设置为 `0` 或负值则可取消该限制。

:::提示：零次调用超时的诊断信息输出
在设置了严格的时间上限后，如果某个子代理在**完全未进行任何 API 调用**的情况下超时（通常是由于提供方不可达、认证失败或工具架构被拒绝所致），`delegate_task` 会向 `~/.hermes/logs/subagent-timeout-<session>-<timestamp>.log` 文件中写入结构化的诊断信息，其中包含该子代理的配置快照、凭证解析过程记录以及所有早期错误消息。相比之前的静默超时行为，这种方式能更轻松地定位问题根源。
:::

## 监控正在运行的子代理（`/agents`）

TUI 提供了 `/agents` 叠加视图（别名为 `/tasks`），可将递归的 `delegate_task` 分发过程转化为直观的审计界面：

- 按父代理分组展示正在运行及最近结束的子代理的树状结构视图
- 每个分支的耗时、令牌使用量以及文件操作统计汇总
- 终止与暂停控制功能——可在不干扰其他子代理运行的情况下，中止某个特定子代理的任务
- 事后分析功能：即便子代理已返回父代理，也可逐步骤查看其执行历史

传统的 CLI 只会以文本形式输出 `/agents` 的概要信息；而 TUI 才是这一叠加视图功能发挥最大价值的场景。详情请参阅 [TUI — 斜杠命令](/user-guide/tui#slash-commands)。

## 深度限制与嵌套编排

默认情况下，代理分配采用**扁平结构**：父代理（深度为 0）会生成子代理（深度为 1），而这些子代理无法再进一步进行代理分配。这样的设计可防止递归代理无限扩散。

对于多阶段工作流（如研究→合成，或针对子问题的并行编排），父代理可以生成**编排器型**子代理，这类子代理具备自行分配任务执行节点的能力：

```python
delegate_task(
    goal="Survey three code review approaches and recommend one",
    role="orchestrator",  # Allows this child to spawn its own workers
    context="...",
)
```

- `role="leaf"`（默认值）：子代理无法进一步委托任务——其行为与扁平委托模式完全相同。  
- `role="orchestrator"`：子代理保留`delegation`工具集。其功能受`delegation.max_spawn_depth`限制（默认值为**1**，即扁平结构，因此在默认设置下`role="orchestrator"`无实际作用）。将`max_spawn_depth`设置为2可允许调度器型子代理生成叶子型孙代理；设置为3及以上则可支持更深的层次结构。该参数并无上限——实际成本才是限制因素。  
- `delegation.orchestrator_enabled: false`：这是一个全局开关，无论`role`参数为何值，都会强制所有子代理变为`leaf`类型。

**成本警告**：当`max_spawn_depth: 3`且`max_concurrent_children: 3`时，该结构最多可同时运行3×3×3=27个叶子型代理。每增加一个层级，资源消耗都会呈倍数增长——请谨慎调整`max_spawn_depth`值。

## 生命周期与持久性

:::warning `delegate_task`为同步操作——不具备持久性  
`delegate_task`在**父代理当前轮次内**执行。它会阻塞父代理，直到所有子代理完成任务或被取消。它**不属于**后台任务队列：

- 若父代理被中断（用户发送新消息、执行 `/stop` 或 `/new` 命令），所有正在运行的子代理都会被取消，并返回`status="interrupted"`状态。它们正在进行中的工作将会丢失。  
- 子代理在父代理的轮次结束后不会继续运行。  
- 被取消的子代理会返回结构化结果（`status="interrupted"`，`exit_reason="interrupted"`），但由于父代理也被中断，这些结果往往无法出现在用户可见的回复中。

对于那些必须能够抵御中断或持续运行超过当前轮次的**持久性长任务**，建议使用以下方式：

- `cronjob`（action=`create`）——安排独立的代理运行任务，不会受到父代理轮次中断的影响。  
- `terminal(background=True, notify_on_complete=True)`——用于运行长时间运行的Shell命令，可在代理执行其他操作时继续运行。  
:::

## 核心特性

- 每个子代理拥有**独立的终端会话**（与父代理分离）。  
- **嵌套委托为可选功能**——仅`role="orchestrator"`类型的子代理才能进一步委托任务，且前提是必须将`max_spawn_depth`从默认的1（扁平结构）提高。可通过设置`orchestrator_enabled: false`全局禁用此功能。  
- 叶子型子代理**无法调用**`delegate_task`、`clarify`、`memory`、`send_message`和`execute_code`这些函数。调度器型子代理虽保留`delegate_task`功能，但仍无法使用其余四个函数。  
- **中断传播机制**——中断父代理会同时中断所有正在运行的子代理（包括调度器下的孙代理）。  
- 仅最终汇总结果会被纳入父代理的上下文，从而有效控制令牌使用效率。  
- 子代理会继承父代理的**API密钥、提供商配置及凭证池**（这有助于在遇到速率限制时实现密钥轮换）。

## 委托任务与代码执行功能的对比

| 对比项 | `delegate_task` | `execute_code` |
|--------|--------------|-------------|
| **运行逻辑** | 完整的LLM推理循环 | 仅执行Python代码 |
| **上下文环境** | 独立的新鲜对话上下文 | 无对话上下文，仅为脚本执行环境 |
| **工具访问权限** | 可使用所有非阻塞型工具，并支持推理功能 | 通过RPC调用7种工具，但不具备推理能力 |
| **并行处理能力** | 默认可同时运行3个子代理（可配置） | 仅单个脚本执行 |
| **适用场景** | 需要推理、判断或多步骤解决的复杂任务 | 需要机械式数据处理或按脚本执行的流程 |
| **令牌消耗** | 较高（需完整执行LLM推理循环） | 较低（仅返回标准输出） |
| **用户交互** | 无（子代理无法主动请求澄清） | 无 |

**实用建议**：当子任务需要推理、判断或多步骤问题解决时，使用`delegate_task`；而当需要执行机械式的数据处理或基于脚本的工作流时，则应选用`execute_code`。

## 配置选项

```yaml
# In ~/.hermes/config.yaml
delegation:
  max_iterations: 50                        # Max turns per child (default: 50)
  # max_concurrent_children: 3              # Parallel children per batch (default: 3)
  # max_spawn_depth: 1                      # Tree depth (floor 1, no ceiling, default 1 = flat). Raise to 2 to allow orchestrator children to spawn leaves; 3+ for deeper trees.
  # orchestrator_enabled: true              # Disable to force all children to leaf role.
  model: "google/gemini-3-flash-preview"             # Optional provider/model override
  provider: "openrouter"                             # Optional built-in provider
  api_mode: anthropic_messages                       # optional; auto-detected from base_url for anthropic_messages endpoints

# Or use a direct custom endpoint instead of provider:
delegation:
  model: "qwen2.5-coder"
  base_url: "http://localhost:1234/v1"
  api_key: "local-key"
  # api_mode: "anthropic_messages"  # Optional. Wire protocol override for base_url ("chat_completions", "codex_responses", or "anthropic_messages"). Empty = auto-detect from URL (e.g. /anthropic suffix). Set explicitly for endpoints the heuristic can't classify (Azure AI Foundry, MiniMax, Zhipu GLM, LiteLLM proxies, …).
```

当 `base_url` 指向兼容 Anthropic 的接口地址时——例如以 `/anthropic` 结尾的路径、Azure Foundry Claude 的路由，或是 MiniMax 的 `/anthropic` 代理——系统会自动将 `api_mode` 设定为 `anthropic_messages`，这样子代理便无需用户额外配置即可使用正确的通信格式。只有在自动检测出现错误时（这种情况较为罕见），才需要手动明确设置 `api_mode`。

:::提示
该智能体会根据任务复杂度自动决定是否进行任务委派。您无需特意要求它委派任务——在合适的情况下它会自动处理。
:::
