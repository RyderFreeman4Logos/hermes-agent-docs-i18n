---
sidebar_position: 7
title: "Subagent Delegation"
description: "Spawn isolated child agents for parallel workstreams with delegate_task"
---

# 子代理委托机制

`delegate_task` 工具会创建多个具有独立上下文、继承工具访问权限以及专属终端会话的子 AIAgent 实例。每个子代理都会拥有全新的对话场景并独立工作——仅有其最终的总结内容会被纳入父代理的上下文中。

顶层模型调用会自动在后台执行。Hermes 会立即返回一个处理标识，以便对话能够继续进行，随后会将结果以新消息的形式发送回来。作为协调者的子代理会等待各个工作节点完成处理，汇总所有结果后再返回响应。

## 结果交付机制

消息网关只有在其适配器真正安排了相关任务或将其加入会话队列之后，才会确认后台任务的完成状态。若缺少对应的处理程序、会话路由不匹配或队列已满，该任务将会被标记为待重试；这类拒绝处理的情况不会消耗永久性的交付尝试额度。一旦任务成功通过处理，当前网关内的重复交付就会被抑制，但这并不能证明模型响应或外部回复已经真正完成。在现有的重放时间限制条件下，任务至少仍会尝试交付一次；而实际的网络传输故障则仍需遵循既定的重试策略。

当 API 服务器路由不可用时，系统不会反复发出路由缺失的警告，而是让该请求处于待处理状态。格式错误的消息路由仍会生成诊断信息。在 API 服务器端，异步委托完成只会添加一条持久性的时间线交付记录——后续的模型推理工作由客户端负责。即便将后台进程通知设置为“关闭”，模式监控事件仍会持续在后台运行。

## 后台进程的生命周期

后台终端进程隶属于启动它们的智能体。在委托关系解除时，若关闭某个子进程，其剩余的进程（包括在之前推理轮次中开始的任务）也会被终止，但这不会影响父进程或其他兄弟智能体所拥有的进程。共享终端环境并不会改变进程的所有权。

子进程应在完成构建、测试及其他有时间限制的后台任务后，才能返回最终总结信息。如果需要在子进程完成后继续运行某个 CI 监控工具或服务器，应在父进程会话中启动它；仅提供进程 ID 并不能将进程所有权转移给父进程。

## 单任务模式

```python
delegate_task(
    goal="Debug why tests fail",
    context="Error: assertion in test_foo.py line 42"
)
```

## 并行批处理

默认支持最多 10 个并发子智能体（可配置，无上限限制）：

```python
delegate_task(tasks=[
    {"goal": "Research topic A", "context": "Focus on recent primary sources"},
    {"goal": "Research topic B", "context": "Compare the leading explanations"},
    {"goal": "Fix the build", "context": "Project root: /home/user/project"}
])
```

## 结构化输出（`output_schema`）

每个任务均可包含一个可选的 `output_schema`，即一个 JSON Schema 对象，子节点的最终答案必须符合该对象的规范。子节点在开始处理任务时即可看到该规范，将其视为输出格式要求；当答案返回后，父节点会对答案进行验证，若验证失败，则会向子节点发送一次修正机会，并原封不动地附上所有验证错误信息（不会重新粘贴规范内容）。此时，任务结果将包含 `schema_valid`（真/假）字段；若验证失败，还会额外包含 `schema_errors` 字段。

```python
delegate_task(
    tasks=[{
        "goal": "Check which of these three endpoints return 200",
        "context": "https://a.example, https://b.example, https://c.example",
        "output_schema": {
            "type": "object",
            "properties": {
                "healthy": {"type": "array", "items": {"type": "string"}},
                "failing": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["healthy", "failing"]
        }
    }]
)
```

请保持模式结构的灵活性：仅要求提供实际需要读取的字段。未设置 `output_schema` 的任务不会受到影响。

## 子智能体的上下文机制

:::warning 重要提示：子智能体一无所知
子智能体始于**全新的对话状态**。它们对父智能体的对话历史、之前的工具调用记录，以及任务委托之前的任何讨论内容都毫不知情。子智能体唯一的上下文来源，是父智能体在调用 `delegate_task` 时所提供的 `goal` 和 `context` 字段。
:::

不过有一个例外：当父智能体已确定工作空间目录后，每个子智能体的系统提示都会包含该工作空间中的**项目上下文文件**（顺序为 `.hermes.md` > AGENTS.md > CLAUDE.md > `.cursorrules`，其发现规则、优先级和大小限制与主智能体的系统提示相同；SOUL.md 除外）。在代码库中工作的子智能体会遵循该代码库自身的规范，无需重新识别这些规范。

这意味着父智能体必须在调用时传递子智能体所需的**所有信息**：

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

子代理会接收到根据您的目标与上下文生成的针对性系统提示，该提示会指示其完成任务，并以结构化的方式总结其操作内容、发现结果、已修改的文件以及遇到的任何问题。

## 实际应用示例

### 并行研究

同时针对多个主题展开研究并汇总相关摘要：

```python
delegate_task(tasks=[
    {
        "goal": "Research the current state of WebAssembly in 2025",
        "context": "Focus on: browser support, non-browser runtimes, language support"
    },
    {
        "goal": "Research the current state of RISC-V adoption in 2025",
        "context": "Focus on: server chips, embedded systems, software ecosystem"
    },
    {
        "goal": "Research quantum computing progress in 2025",
        "context": "Focus on: error correction breakthroughs, practical applications, key players"
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
    Fix any issues found and run the test suite (pytest tests/auth/)."""
)
```

### 多文件重构功能

用于处理那些会占用父上下文过多资源的大型重构任务：

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
    Run pytest after to verify nothing broke."""
)
```

## 批量模式详解

当顶层智能体提供 `tasks` 数组时，Hermes 会生成一个后台处理句柄，并并行执行各个子智能体。默认情况下，每个任务完成后，系统会返回**一条**汇总消息。结果仅在父智能体的处理轮次之间传递：父智能体应先完成所有不依赖子智能体的任务，随后结束当前轮次，而非在等待期间不断轮询转录内容、输出结果或 CI 状态。

### 独立完成模式（可选）

若希望每个任务完成后即单独返回结果，可设置 `delegation.independent_completions: true`。仅当此选项启用时，才会显示面向模型的 `group` 字段及分组相关说明。更改该设置后需启动新会话，以便工具结构能反映新设置，同时避免修改现有对话的缓存前缀。包含 `group` 字段的旧请求仍可被接受；若关闭此选项，整个请求仍会统一返回结果。

启用独立完成模式时：

- 若每个结果均可单独处理，则无需设置 `group` 字段。每个任务在完成后会立即上报结果。
- 若需要共同查看输出内容（如进行对比、综合分析或做出统一决策），则应使用相同的 `group` 字符串。该组的所有任务完成后，系统会返回**一条**汇总消息。即便这些任务可独立执行，只要其结果有助于同一决策，也可归入同一组。
- 不同组的结果会独立返回；已分组和未分组的任务可在同一个请求中一并处理。
默认情况下会采用这种分离方式，因为对调度器而言，每个任务单元都代表一个新的处理轮次：一个包含15个任务的调用可能会触发多达15次唤醒操作，从而导致漫长的营销活动被拆分成多个碎片。分组控制的是**结果交付方式，而非执行顺序**：所有任务依然会并行运行。如果任务B需要任务A的输出才能继续执行，那么会先调度任务A，等A完成后再使用其输出结果来调度任务B。

```json
{"tasks": [
  {"goal": "Review PR #101 ..."},
  {"goal": "Review PR #102 ..."},
  {"goal": "Benchmark approach A ...", "group": "bench"},
  {"goal": "Benchmark approach B ...", "group": "bench"}
]}
```

调度处理程序会列出各个单元的信息（`units[].delegation_id`、`group`、`task_indexes`）；这些单元的编号是在对应调用编号后附加了 `-1`、`-2` 等后缀而形成的。由于同一调用中的所有单元共享 `delegation.max_concurrent_children` 所规定的同一并发配额，因此进行分组并不会改变容量计算方式——工作池的大小会随活跃单元的数量自动扩展，从而避免任何单元因池子已满而不得不等待。调度子代理会在当前轮次中等待其处理的所有任务完成，以便整合最终结果。

- **最大并发数**：默认为 10 个任务（可通过 `delegation.max_concurrent_children` 或环境变量 `DELEGATION_MAX_CONCURRENT_CHILDREN` 进行配置；下限为 1，无上限限制）。超过此限制的批次会返回工具错误，而不会被悄悄截断。  
- **线程池**：使用 `ThreadPoolExecutor`，其最大工作线程数即为配置的并发限制值。  
- **进度显示**：在 CLI 模式下，以树状视图实时展示每个子代理的任务调用情况，并为每个任务显示完成状态行。在网关模式下，进度会以批次形式传递给父代理的进度回调函数。CLI 和 TUI 的完成通知会以任务优先的格式显示，例如“子代理任务已完成：请查看更改”；多任务组则显示组名及任务数量。失败或未完成的任务会附带相应的状态标签。这些简短的提示不会替代发送给父代理的完整结果。  
- **结果排序**：在单个单元内，无论任务完成顺序如何，结果都会按任务索引排序，以匹配输入顺序；`TASK i/N` 标签用于标识整个调用序列中的位置。  
- **取消操作**：后续消息无法取消顶层后台批次。使用 `/stop` 命令或关闭/重置当前会话可取消其正在运行的子任务。同步编排器的子任务仍会遵循父任务的中断状态。  

编排器发起的同步单任务委托无需线程池开销，可直接执行。  

### 持久化后台任务完成处理

当后台任务处理完成时，Hermes会先将其完成事件存储在当前活跃配置文件的`state.db`中，之后才会将其放入常规的新一轮处理队列中。如果在任务完成但尚未交付之前Hermes重启，该待处理事件会被恢复，并再次经过相同的所有权校验流程。由于各消耗进程会使用持久性的声明机制，只有成功接收该合成处理结果的进程才会被确认为任务已交付；而失败的尝试则会释放该声明，以便后续重试。

不过，此机制无法在进程崩溃后恢复子任务的执行。如果某个子任务的所属进程在任务运行期间消失，该任务会被标记为“未知”状态，因为Hermes无法确定其外部操作是否实际发生。待处理和已交付的任务记录都是有限制的，并且仅存在于对应配置文件内部。

### 子后台进程的通知机制

子代理启动的后台进程（例如带有`notify_on_complete`选项的`npm ci`命令）在技术上会将它们的完成状态及监控模式通知发送至**父级**对话中，因为任何需要持续运行的进程都需要一个持久性的消耗进程。默认情况下，这些通知在父级对话中会被**抑制**——因为子任务的最终处理结果才是需要交付的内容，而子任务内部构建过程中产生的“进程已结束”提示属于干扰信息。被抑制的事件仍会以调试级别记录下来，其中包含进程会话ID和子代理任务ID，因此仍便于诊断问题。

委托结果本身永远不会被抑制。若要恢复子进程通知的发送（每条通知均会包含“由子代理启动……”的标识行）：

```yaml
delegation:
  surface_child_process_notifications: true   # default: false
```

### 将进程移交给父代理

当子代理任务完成时，其后台进程也会被**终止**，因此那些以 `notify=true` 参数启动的 CI 监控脚本或子代理，根本不会向任何一方汇报进度。子代理的终端输出会明确显示这一点（显示为 `notify_on_complete: false` 并附带 `subagent_note` 字段）。在任务结束之前，子代理有三种可行的处理方式：

- **等待**——使用 `process_manage(action="wait", session_id=...)` 方法，并自行汇报处理结果；
- **强制终止**——使用 `process_manage(action="kill", ...)` 方法；
- **移交处理**——使用 `process_manage(action="handoff", session_id=..., data="<一句话：移交目的>")` 方法。此时运行时系统会在注册表锁定的前提下将进程控制权移交给父代理（每个子代理最多可移交3个进程；仅接受该子代理正在运行的进程，其他进程将导致工具报错）。随后，父代理的聊天窗口中会收到通知，内容为“此进程已由子代理移交给您……目的：……”，父代理即可像处理自己的进程一样对它进行轮询、记录日志或强制终止操作。
当子进程仍在运行时即完成的任务无需进行交接：子进程会读取该任务信息（通过 `poll`/`wait`/`log` 方式）并上报结果。如果子进程从未读取过该任务，其退出码及输出尾部内容将以 `unread_completions` 的形式附加到结果中，并展示给父进程。对于那些仍在运行但既未被终止也未被交接的任务，其名称会以 `orphaned_processes` 的形式出现在结果中，同时在父进程的交接通知中被标记为已终止；这样，父进程就能从运行时系统处得知“监视器仍在运行”这一状态已不再成立，而无需等待子进程的反馈。对于 CI 监视器而言，更好的处理方式依然是：由子进程返回相关信息（如 PR 编号、SHA 值），再由父进程自行启动监视器。

## 模型覆盖

您可以通过 `config.yaml` 为子代理配置不同的模型——这有助于将简单任务分配给成本更低或速度更快的模型：

```yaml
# In ~/.hermes/config.yaml
delegation:
  model: "google/gemini-flash-2.0"    # Cheaper model for subagents
  provider: "openrouter"              # Optional: route subagents to a different provider
```

如果未指定，子智能体将使用与父智能体相同的模型。

### 成本策略：前沿规划器 + 低成本工作节点

将问题拆解为定义明确的子任务需要具备前沿层面的判断能力；而执行那些本身已具备明确目标、完整上下文及输出规范的子任务则通常无需此类能力。与此同时，大量计算资源都消耗在子智能体上——一组并行运行的子智能体通常会耗尽整个任务流程中的绝大部分令牌，因此成本实际上集中在工作节点模型上。通过将`delegation.model`设置为低成本模型，同时让主会话继续使用前沿模型，既能够保证关键环节的规划质量，又能在高消耗环节有效控制成本。

```yaml
# ~/.hermes/config.yaml
model:
  default: "your-frontier-model"     # parent (planner) stays on the frontier model
delegation:
  model: "your-inexpensive-model"    # all delegate_task children run on this
  provider: "openrouter"             # optional: route children to a different provider
```

解析顺序如下：首先优先使用 `delegation.base_url`（直接端点），其次是 `delegation.provider`（通过运行时提供系统解析的完整凭证包）；若两者均未设置，则子代理会继承父代理的提供者和凭证。在所有情况下都会应用 `delegation.model` 参数，若该参数为空，子代理则继承父代理的模型。同时设置 `delegation.base_url` 和 `delegation.provider` 可以保留明确的端点，同时将该提供者的请求覆盖规则及最大输出token数传递给子代理。每个分支都会优先考虑显式指定的 `delegation.request_overrides` 字典内容，并会将其与运行时生成的值进行合并（详情请参见下文的[配置](#configuration)部分）。

需注意，此设置是全局有效的：由于 `delegate_task` 不支持针对单个任务的模型参数，因此批次处理中的所有子任务都将使用已配置的委托模型。对于对质量要求较高、需要更强大模型的子任务，要么为该会话保留空值的 `delegation.model`，要么将任务提交至[看板系统](kanban.md#per-task-model-override)，因为该系统确实支持针对单个任务的模型覆盖功能。

## `/review` 命令

`/review` 命令会启动一个独立的、拥有完整权限的后台子代理，其唯一职责就是审查您当前对话所产生的成果——无论是代码提交请求、差异对比结果、代码内容、文档还是设计稿。该命令可在多种场景下使用：命令行界面、文本用户界面、桌面应用程序，以及各类消息传递平台。

```
/review                       # review whatever the last 10 messages presented
/review focus on security     # add extra instructions for the reviewer
```

具体流程如下：

1. 系统会截取最近10条用户与助手之间的对话记录作为审核者的初始参考依据（工具输出和系统消息除外）。
2. 一个审核子代理会在与 `delegate_task` 相同的后台任务通道中被启动——它拥有完整的常规子代理工具集（终端、网页、文件管理、浏览器等），因此能够实际打开拉取请求、查看代码差异并运行代码，而非仅依据片段内容进行判断。
3. 审核子代理会继承主代理的工作上下文：主代理之前加载的所有技能（无论是预先加载的，还是通过会话中的 `skill_view` 功能加载的），都会在给它的任务说明中列出，并要求其根据这些技能的规则来对代码质量进行评估。与所有子代理一样，它的系统提示词也会嵌入工作区的项目上下文文件（如 AGENTS.md、CLAUDE.md 和 .cursorrules），将其作为必须遵循的规范。
4. 审核完成后，它的完整审核结果会以普通后台子代理任务的完成形式重新回到当前会话中——主代理可以查看该结果并据此采取行动（修复问题、发送跟进消息或回复您）。

标准工作流程为：您的主代理打开一个拉取请求，您输入 `/review` 命令，随后另一个审核者便会开始对该请求进行审查，而您则可继续处理其他工作；最终审核结果会以消息形式返回聊天界面，发送给最初创建该拉取请求的代理。

Dispatch仅会显示“审核已开始。结果将在此处返回。”实时子代理查看器会将该处理任务标记为**审核：当前重点**（若仅使用 `/review` 命令，则显示为**审核近期任务**），并附带简短的单行标签；不过审核者仍会收到完整的操作指令。在传统CLI界面中，编译器上方的面板会显示已用时间及最新操作状态；按下**Ctrl+T**（或**F6**）即可打开包含模型、转录内容、控制选项以及停止功能的列表界面。TUI和桌面版子代理查看器也会显示相同的审核标签。

### 模型选择

默认情况下，审核任务会使用您的主模型来执行。若需指定专用的审核模型，请在 `config.yaml` 文件中设置 `auxiliary.review` 参数：

```yaml
auxiliary:
  review:
    provider: openrouter               # or nous, anthropic, a direct base_url, ...
    model: anthropic/claude-opus-4.6   # a strong reviewer model
```

凭证的解析方式与 `delegation.provider` 的固定配置完全相同（完整的运行时提供程序包包含：基础 URL、API 密钥以及 API 模式）。当 `provider: auto` 且 `model` 为空时，意味着“继承主智能体的模型”——这也是默认设置。

`/review` 被刻意与 `/refine` 分开：`/refine` 用于审查对话内容以更新内存和技能，而 `/review` 则用于审查对话所产生的*成果*。

## 继承的工具访问权限

`delegate_task` 不接受面向模型的 `toolsets` 参数。每个子智能体都会继承父智能体已启用的工具集，因此模型无法赋予子智能体超出父智能体能力的功能。如果需要委托的任务具备额外功能，应在开始对话之前配置好父智能体的工具。

即便父智能体拥有某些工具，子智能体仍可能无法使用它们：
- `delegate_task`——对叶级子智能体（默认情况）是禁用的。对于 `role="orchestrator"` 的子智能体则允许使用，但其使用深度受 `max_spawn_depth` 限制——详情请参见下文的[深度限制与嵌套编排](#depth-limit-and-nested-orchestration)。
- `clarify`——子智能体无法与用户交互。
- `memory`——禁止向共享的持久内存写入数据。
- `send_message`——禁止跨平台产生副作用。
- `cronjob`——禁止以父智能体的名义安排更多任务。

这两种角色均保留了 `execute_code` 功能（用于程序化调用工具），以便子智能体能够批量处理机械性工作。

## 最大迭代次数

每个子智能体都设有迭代次数限制（默认值为250），该限制决定了其能够进行工具调用的轮数。此限制在`config.yaml`中统一设置，适用于所有子智能体，并非`delegate_task`函数中的每次调用参数：

```yaml
# In ~/.hermes/config.yaml
delegation:
  max_iterations: 60   # lower it for fleets of simple tasks, raise it for long investigations
```

当子代理的预算耗尽时，它会返回 `exit_reason: max_iterations` 以及 `truncated: true` 的状态，这样父代理就能判断出任务因预算限制而终止。

## 子代理超时机制

默认情况下，子代理并不设有基于实时时钟的超时限制。它们只会因实际执行过程中的问题而失败——比如 API 错误、工具错误或迭代预算耗尽——而不会因为上层调度机制设定的计时限制而失败。在早期版本中，存在一个硬性时间上限（最初为300秒，后来改为600秒），这常常导致那些正在认真执行任务的子代理被过早终止：深度代码审查、大规模研究分析以及运行缓慢的推理模型通常需要超过10分钟的时间，且在此期间仍会持续取得进展。

不过，真正陷入停滞的子代理依然可以被检测出来：当子代理没有产生任何进展（既没有发起 API 调用，也没有启动任何工具，且活动时间戳也没有更新）时，心跳检测机制就会停止向父代理发送更新信息，从而触发网关的不活跃超时机制。在等待模型响应的过程中，只要仍在尝试连接，就仍被视为有进展——子代理会在等待提供者响应的同时持续更新活动时间戳，因此本地处理速度较慢或预加载过程较长并不会被判定为停滞状态。

如果您无论如何都需要设置硬性时间上限（例如为了控制无人值守的定时任务调度带来的成本），可以在每次安装时选择启用该功能：

```yaml
delegation:
  child_timeout_seconds: 0     # default: 0 = no timeout
  # child_timeout_seconds: 1800  # opt-in hard cap (floor 30s)
```

当设置正值时，将为每个子代理强制施加严格的实时时钟限制；而设置为 `0` 或负值则可取消该限制。

一旦达到预设的时限阈值，子代理的返回结果会附带结构化的超时元数据与错误信息，这样父代理及各类钩子函数便无需解析文本即可区分因超时导致的终止与其他类型的故障：包括 `timeout_seconds`（即预设的时限值）、`timed_out_after_seconds`（实际的耗时时长），以及 `timeout_phase`（若子代理从未发起过首次请求则为 `before_first_llm_call`，否则为 `after_llm_calls`）。在非超时错误情况下，这三个字段的值为 `null`。

## 错误可见性

出现故障的子代理——无论是无法重试的提供者错误（如 404/400 错误）、超时、崩溃，还是无可用输出——都绝不会悄无声息地失败：

- **CLI 环境**：任务分配树会打印一行简明的原因说明，例如 `⚠️ Subagent failed — "your goal": HTTP 404: model not found (after 12s)`。批量运行时，该原因会被附加到对应任务的 `✗` 完成行中。
- **网关平台**（如 Telegram、Discord、Slack 等）：即便该平台的 `tool_progress` 功能处于关闭状态，也会以独立的聊天消息形式发送同样简洁的说明。
- **父代理**：工具返回结果会标注 `status: "failed"` 并附带完整的错误文本，以便模型能够据此采取相应措施（如重试、重新路由或上报错误）。

错误文本会被简化为最具信息量的那一行内容（即异常信息，而非冗长的堆栈跟踪），同时对其长度也会进行限制。

:::提示：零次调用超时的诊断信息输出  
当设置了硬性时间限制后，如果某个子代理在**完全没有**发起任何 API 调用的情况下超时（通常是由于提供方不可达、认证失败或工具结构被拒绝所致），`delegate_task` 会向 `~/.hermes/logs/subagent-timeout-<session>-<timestamp>.log` 文件中写入结构化的诊断信息。这些信息包括该子代理的配置快照、凭证解析过程记录、所有早期错误消息，以及**所有**正在运行的线程的堆栈跟踪信息（而不仅仅是子线程自身的）——如果没有完整的上下文信息，那些在嵌套辅助线程中等待的子线程就很难与响应缓慢的提供方区分开来。  
:::

## 后台子代理的停滞检测机制  

对于后台委托任务（即使用 `delegate_task(background=true)` 创建的任务），系统会通过**基于进度值的停滞监控器**来对其进行监控——默认情况下不会配置任何相关参数。与传统的固定时间超时机制不同，无论任务运行了多久，该监控器都不会中断那些正在取得进展的子线程。  

该监控器会定期采集每个独立子线程的进度信号，包括 API 调用次数、当前正在使用的工具，以及上次活动的时间戳（该时间戳会在**每一个流式处理单元、工具状态切换以及 API 调用节点**处更新，因此即使子线程正在处理一个长度较长的响应，也会一直被视为处于活跃状态）。

1. **处于进展中的子任务绝不会被干扰。** 任何进度提升的信号都会重置计时器。  
2. 若某个子任务的进度因长时间停滞而超过阈值（空闲状态超过450秒，或在工具中运行超过1200秒——正常的缓慢终端命令和网络请求可享有更高的阈值），系统会**中断该子任务**并给予其120秒的缓冲时间。若该子任务能在规定时间内恢复进度，则会通过常规完成路径输出部分结果。  
3. 若某个子任务始终无法返回，系统会强制触发“停滞”完成事件，从而使所属会话能够收到相应结果而不会陷入沉默，同时释放出异步资源以处理新任务。  

“停滞”事件会携带结构化的元数据，这些数据与同步路径超时相关的字段相对应，包括：`stalled_after_quiet_seconds`、`stall_threshold_seconds`、`stall_phase`（“空闲”/“在工具中”）以及`stall_grace_seconds`。  

这一改进解决了长期存在的故障问题——即某些陷入停滞状态的后台子任务会导致会话看似已死机，直到进程重启才能恢复。其根本原因也已被解决：现在的委托子任务会在自身的对话线程中直接发起OpenAI API请求，而非在之前易出问题的嵌套工作线程中执行。此外，停滞监控机制仍作为其他异常情况的安全保障。  

## 监控正在运行的子代理（`/agents`）  

TUI提供了 `/agents` 接口（别名为 `/tasks`），可将递归的 `delegate_task` 调用过程转化为可直接监控的对象，从而实现更高效的审计功能。

- 按父节点分组展示正在运行及最近结束的子代理的实时树状视图  
- 每个分支的成本、令牌数以及被操作的文件统计汇总  
- 终止与暂停控制功能——可在特定子代理运行过程中取消其任务，而不会影响其他子代理的正常运行  
- 事后回溯功能：即便子代理已返回父节点，仍可逐步骤查看其执行历史  

### 编辑器上方的实时活动显示  

传统的命令行界面、文本用户界面以及桌面版应用都会在编辑器上方实时显示子代理的运行状态。您可以在持续输入代码的同时，实时查看任务数量、任务名称、耗时以及最新操作动态。终端栏会根据屏幕高度限制显示的行数，并标明还有多少个工作进程处于隐藏状态；桌面版则可预览最多三个工作进程的信息。  

| 界面类型 | 展开并查看详情 | 控制选中的工作进程 |
|---|---|---|
| 传统命令行界面 | 按 **Ctrl+T**（或 **F6**）可打开全屏实时列表；使用方向键选择，按 **Enter** 可查看操作记录尾部，按 **PgUp/PgDn** 可滚动浏览 | 按 **s** 可打开单独的指令输入界面；按 **x** 后再按 **y** 可请求停止该进程 |
| 文本用户界面 | 按 **Ctrl+T** 或输入 `/agents` 可展开全高度树状结构；按 **Enter/t** 可查看实时操作记录尾部，按 **d** 可查看详细信息（已存档或回放的操作仍可通过按 **Enter** 查看详情） | 按 **e** 可打开指令输入界面；按 **x** 可停止选中的工作进程，按 **X** 可停止其整个子树 |
| 桌面版 | 展开编辑器上方的“子代理”选项，然后选中某个工作进程以查看其运行状态及详细信息 | 使用“引导”功能可下达指令；使用“停止”功能可请求中断该工作进程的运行 |
关闭终端窗口后，您将返回到当前的作曲草稿。Steering会使用自身的输入信息，并显示“已排队”状态而非实际交付状态：子节点会在特定检查点处处理指导内容。执行“停止”操作不会中断其他无关的子节点。

在经典CLI或TUI作曲界面中，按下**F7**键即可切换展示模式，在多行预览与单行概要显示之间切换。概要栏会保留实时字数统计以及展开/恢复提示，空间允许时还会显示最新操作记录。用户仍可继续输入并发送内容；打开或关闭终端窗口都不会影响草稿内容及光标位置。这仅是界面展示方式的选项，而非实际保存的配置更改。

实时转录内容仅为近期有限范围的摘录，并非无限制的对话浏览功能。当某个子节点退出实时记录列表时，它也会同时从界面中消失；完成消息以及TUI/桌面端的历史记录功能仍是查看已完成工作的途径。最新活动状态仅用于展示当前进度，而非完成度的百分比估算。

经典CLI中的`/agents`和`/tasks`命令仍会输出文本格式的概要信息；而**Ctrl+T**（或**F6**）键则能立即打开交互式终端界面，即便父节点正在处理其他任务时也可使用。详情请参阅[TUI — 斜杠命令](/user-guide/tui#slash-commands)。

在经典CLI以及所有网关平台（Telegram、Discord、Slack等）上，`/agents`命令还会列出**带有每个子节点实时活动状态的后台任务**，这些信息直接来自正在运行的各个子节点：

```
Background delegations: 1 running
- deleg_ab12cd34 · running · research the delegation stall monitor
  - child 1: 4 api calls · in web_search · active 12s ago
  - child 2: 7 api calls · between turns · active 3s ago
```

摊位监控器标记的某个委托任务显示为“停滞中 · 450秒无进展 — 正在中断”；而对于那些长时间安静但状态正常的儿童，则会显示其安静时长，这样您就能一目了然地区分“反应慢”与“陷入僵局”的情况。

## 引导正在运行的子代理

中断某个儿童会使其当前正在进行的工作失效；通常您只是希望重新引导它继续工作。

### 从父代理端（面向模型）

父代理会使用当初创建这些子代理时所用的相同 `delegate_task` 工具来管理它们，无需额外的控制工具：

```json
{"action": "list"}
{"action": "steer", "subagent_id": "sa-0-1a2b3c4d", "message": "focus on pricing instead"}
{"action": "stop",  "subagent_id": "sa-0-1a2b3c4d"}
```

- **`list`** 命令用于获取对话中正在运行的子代理信息，包括 `subagent_id`、目标、状态、`running_seconds`、`accepting_steer` 以及实时对话记录的路径。这些标识符也会以 `subagent_ids` 的形式出现在子代理创建的响应中。
- **`steer`** 命令可将修正指令排队发送给正在运行的子代理，而不会中断其运行（具体传递机制见下文）。
- **`stop`** 命令会在子代理的下一次迭代节点提前终止其运行；尽管如此，该子代理的阶段性结果仍会以常规完成消息的形式重新纳入对话流程。

所有控制操作均为同步顺序执行（绝不会在后台运行），且仅作用于调用方自身的子代理树结构——一个对话无法查看或控制另一个会话中的子代理——同时这类操作也不会占用每轮次允许创建子代理的限额，因此即便达到限额限制，`stop` 命令仍可继续使用。

### 通过 TUI/网关（面向会话端）

`tools/delegate_tool_registry.py` 中的 `steer_subagent(subagent_id, text)` 函数是 `interrupt_subagent()` 的对应功能：它通过与 [`/steer`](/reference/slash-commands) 相同的机制将文本发送给正在运行的子代理——该文本会在子代理下一次迭代时附加到其最新的工具处理结果之后，且正在进行的工具调用不会被中断，子代理会将此文本视为外部用户输入。通过程序化方式调用的主机可通过会话级接口 `subagent.steer` RPC 来使用此功能，该接口与 `subagent.interrupt` 接口位于同一层级。

```json
{"method": "subagent.steer", "params": {"session_id": "owning-ui-session", "subagent_id": "sa-0-1a2b3c4d", "text": "focus on pricing instead"}}
```

子代理的 ID 来自 `delegation.status`（或 `list_active_subagents()`）——这一来源与 `subagent.interrupt` 获取 ID 的位置相同。网关仅接受由生成子代理的当前活跃 UI/网关会话发出的指令。缺失、异常、模糊或已过期/被回收的会话标识都会被拒绝；知晓全局子代理 ID 并不能作为授权依据。直接在进程内调用的客户端会刻意保留无作用域的辅助契约。

**“已排队”并不等同于已送达，也绝不意味着成功处理。** “已排队”状态仅表示文本在子代理的处理截止时间之前已被接收，但并不代表子代理已经看到了该文本。接收与处理是同步的：要么子代理仍能读取该文本，要么其对应的文本会以 `pending_steer` 的形式被纳入结果中。在子代理处理完成之后发起的调用将返回 “已拒绝”。如果子代理虽然接收到了指令，但早已给出了最终答案，父代理收到的完成记录会将其标记为 “未处理到指令”，并在摘要中附加相应说明：

```
[steer did not land — the subagent finished before it could be delivered: focus on pricing instead]
```

这样一来，父代理（或负责操控它的操作员）便能区分那些仍遵循旧指令运行的子代理，进而重新下发指导指令作为后续操作，而无需依赖其是否能正确执行。

## 实时记录功能

每次调用 `delegate_task` 命令时，系统都会为每个任务生成一份**仅可追加、便于人工阅读的日志**，这样您（或父代理）就能实时查看子代理的工作情况，而无需等待汇总后的报告。

```
<hermes_home>/cache/delegation/live/<delegation_id>/task-<n>.log
```

调度响应中会以 `live_transcripts` 的形式包含相关路径，且这些文件会在调度时预先生成，因此可以立即投入使用。

```bash
tail -f ~/.hermes/cache/delegation/live/deleg_ab12cd34/task-0.log
```

每行数据都会标注时间戳，同时显示子智能体的响应文本、思考过程、工具调用（`-> tool_name({args})`）、工具返回结果以及最终状态标识。同一目录下的 `manifest.json` 文件用于描述任务批次的信息（目标、任务数量及单个任务的状态）。这些日志在任务完成后仍会保留，既可作为完整操作记录，也可与摘要一起使用；此外，每当有新任务派发时，超过7天的日志目录会自动被清理。由于这些日志存储在 `cache/delegation` 目录下，因此也可以通过远程终端后端（如 Docker/Modal/SSH）进行读取。

## 深度限制与嵌套编排

默认情况下，任务委派采用**扁平结构**：父智能体（深度为0）会生成子智能体（深度为1），而这些子智能体无法再次进行委派。这样的设计旨在防止无限递归的委派现象。

对于多阶段工作流（如先研究再综合，或对子问题进行并行编排），父智能体可以生成能够**自行委派任务**的“编排器”型子智能体：

```python
delegate_task(
    goal="Survey three code review approaches and recommend one",
    role="orchestrator",  # Allows this child to spawn its own workers
    context="...",
)
```

- `role="leaf"`（默认值）：子节点无法进一步委托任务——其行为与扁平式委托完全相同。  
- `role="orchestrator"`：子节点保留`delegation`工具集。其功能受`delegation.max_spawn_depth`参数限制（默认值为**1**，即扁平结构，因此在默认设置下`role="orchestrator"`实际上不起作用）。将`max_spawn_depth`设置为2可允许调度器型子节点生成叶子型孙节点；设置为3及以上则可支持更深的层级结构。该参数没有上限，实际成本才是限制因素。  
- `delegation.orchestrator_enabled: false`：这是一个全局开关，无论子节点的`role`参数为何值，都会强制将其变为`leaf`类型。

**成本警告**：当`max_spawn_depth`设置为3且`max_concurrent_children`也设置为3时，该结构最多可同时存在3×3×3=27个叶子型智能体。每增加一个层级，系统开销就会呈倍数增长——请谨慎调整`max_spawn_depth`值。

## 生命周期与持久性

:::warning 背景任务处理并非持久执行  
对于面向顶层模型的`delegate_task`调用，只要会话支持后续结果传递，这些调用就会在后台自动运行。Hermes会立即返回一个处理标识，实际结果会在子节点或批量任务处理完成后重新纳入对话流程。调度器型子智能体则需在当前轮次中等待其下属任务完成，因为它们必须在返回之前整合这些结果。对于无状态请求/响应接口，若无法在之后传递分离的结果，则会退化为同步执行模式。

- 普通的后续消息不会取消后台子任务。使用 `/stop` 命令可终止正在运行的后台任务，而关闭或重置对应会话则会丢弃其所有活跃的子任务。
- 显式关闭/重置会话会中断该会话下的所有后台子任务。不过，关闭由网关管理的会话对应的 TUI 查看器，并不会终止网关的相关工作。
- Hermes 进程重启**不会**恢复正在运行的子任务。由于 Hermes 无法确定具体发生了哪些副作用，此类尝试的状态会被标记为“未知”。
- 那些在重启前已完成但结果尚未传递的子任务会被重新恢复，并通过对应会话的常规检查流程进行处理。
- 被取消的子任务会返回结构化的结果（`status="interrupted"`, `exit_reason="interrupted"`），但由于父任务也已被中断，这些结果往往无法出现在用户可见的回复中。

若需要实现**持久执行**，即确保任务在会话关闭或进程重启后仍能继续运行，可选用以下方式：

- `cronjob`（action=`create`）——用于安排独立的 Agent 运行任务，能够抵御父任务被中断的影响。
- `terminal(background=True, notify_on_complete=True)`——适用于那些需要在 Agent 执行其他任务时持续运行的长时间 shell 命令。
:::

## 核心属性

- 每个子代理拥有**独立的终端会话**（与父代理分开）
- 子代理继承父代理已启用的工具集；模型无法在每次调用时自行选择或扩展这些工具集
- **嵌套委托为可选功能**——仅角色为 `orchestrator` 的子代理可以进一步委托任务，且需将 `max_spawn_depth` 的默认值 1（即扁平结构）提高才行。可通过设置 `orchestrator_enabled: false` 在全局层面禁用该功能。
- 叶子级子代理**无法**调用 `delegate_task`、`clarify`、`memory`、`send_message`、`cronjob` 这些函数。协调器型子代理保留 `delegate_task` 的调用权限，但其他功能则不可用。两种角色的子代理均保留 `execute_code` 功能（用于程序化调用工具），这样子代理便可批量处理机械性任务，从而避免消耗过多的推理资源。
- **取消操作遵循所属关系**——执行 `/stop` 命令或关闭/重置所属的终端会话，将会终止该会话下的所有后台子进程；处于协调器管理下的同步子进程则会跟随其父进程的中断状态而停止运行。
- 仅最终汇总结果会被纳入父代理的上下文，从而有效控制令牌使用量。
- 子代理继承父代理的**API 密钥、提供方配置以及凭证池**（这有助于在遇到速率限制时实现密钥轮换）。

## 工作树隔离机制

默认情况下，子代理会共享父代理的工作目录——这对于以研究和读取为主的任务来说已经足够，但若有多个子进程同时编辑同一个代码库，则可能会出现冲突。可通过设置 `delegation.worktree_isolation: true` 为每个子代理分配独立的 Git 工作树，该工作树基于代码库当前的 `HEAD` 分支创建（这一设计灵感来自 Muse Code 的 `--subagent-worktree-isolation` 参数）。

```yaml
delegation:
  worktree_isolation: true   # default: false
```

在隔离模式下：

- 每个子代理都在其独立的分支 `hermes-subagent/subagent-<id>` 中的 `<repo>/.worktrees/subagent-<id>` 目录下启动终端，其目标指令会指示它在该目录中进行操作并提交代码。
- 父代理的检出状态保持不变；子代理之间不会互相覆盖对方的修改。
- 当某个子代理完成任务后，其结果条目会新增一个 `worktree` 字段，其中包含 `path`、`branch`、`commits`（相对于基线的提交数）以及 `dirty` 状态信息。父代理可查看或合并每个分支（通过 `git log <branch>`、`git merge <branch>` 命令）。
- 若某个工作树**没有提交记录且状态干净**，则会自动被清理（标记为 `pruned: true`）；而任何仍包含未处理内容的 worktree 都会保留。
- 清理操作需要验证。如果 Git 检查失败，或者最终确认步骤出现错误，该工作树和分支将会被保留，同时结果条目会标记为 `inspection_failed: true` 并附上说明——此时 `commits`/`dirty` 的值将采用默认值而非实际检测结果，因此应直接检查工作树内容，而不要直接认为该子代理未生成任何输出。

适用范围：需手动启用，仅支持 Git 以及本地终端后端。在非 Git 目录中、使用 docker/ssh/modal 后端时，或工作树创建失败的情况下，该功能会静默降级为当前的共享工作空间模式——而不会报错。

## Delegation 模式与 execute_code 模式对比

| 因素 | delegate_task | execute_code |
|------|--------------|-------------|
| **推理机制** | 完整的LLM推理循环 | 仅执行Python代码 |
| **上下文环境** | 新的独立对话上下文 | 无对话上下文，仅脚本执行 |
| **工具访问权限** | 支持所有非受限工具及推理功能 | 通过RPC调用7种工具，无推理功能 |
| **并行处理能力** | 默认支持10个并发子代理（可配置） | 单一脚本执行 |
| **适用场景** | 需要判断力的复杂任务 | 机械式的多步骤流程处理 |
| **Token成本** | 较高（需完整LLM推理循环） | 较低（仅返回标准输出） |
| **用户交互** | 无（子代理无法进行说明） | 无 |

**经验法则：** 当子任务需要推理、判断或多步骤问题解决时，使用`delegate_task`；当需要机械式的数据处理或脚本化工作流时，使用`execute_code`。

## 配置设置

```yaml
# In ~/.hermes/config.yaml
delegation:
  max_iterations: 250                       # Max turns per child (default: 250)
  # max_concurrent_children: 10             # Parallel children per batch (default: 10)
  # independent_completions: false          # true = each task/group returns as it finishes (default: one message per call)
  # worktree_isolation: false               # Give each child its own git worktree (see Worktree Isolation above)
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

# Send per-child request settings on every subagent API call — e.g. OpenRouter
# routing hints when delegating straight to openrouter.ai via base_url:
delegation:
  model: "deepseek/deepseek-v4-flash-0731"
  base_url: "https://openrouter.ai/api/v1"
  api_key: "sk-or-..."
  request_overrides:
    extra_body:
      provider:
        sort: throughput   # children route to the fastest OpenRouter provider
```

当 `base_url` 指向兼容 Anthropic 的接口地址时——例如以 `/anthropic` 结尾的路径、Azure Foundry Claude 的路由，或是 MiniMax 的 `/anthropic` 代理——系统会自动将 `api_mode` 设定为 `anthropic_messages`，这样子代理便无需额外配置即可使用正确的通信格式。仅在自动检测结果出错时（这种情况较为罕见），才需要手动明确设置 `api_mode`。

子代理的压缩触发条件与其父代理相同（默认为 `compression.threshold`，即窗口大小的 0.50 倍）。`delegation.compression_threshold_tokens`（默认值为 0，表示关闭该功能）可对子代理的压缩触发条件设置一个可选的绝对上限，该上限以两者中的较小值为准；此设置不会影响请求载荷或父代理本身。要启用此功能，Token 数量需至少达到 16000；若设置为 `true` 或 `"200k"`，则会视为配置错误并仅会发出警告而被忽略。该功能默认处于关闭状态，因为在保留缓存前缀的前提下，1393 个代理的运行测试显示，20万到40万的限制值在成本上仅存在 5% 的差异，而每次压缩都可能导致部分细节丢失。

`delegation.request_overrides` 会在**三种**请求解析路径中生效——直接使用 `base_url`、指定 `provider`，以及纯继承模式——因此它总能发挥作用。顶层键为 API 关键字参数（例如 `service_tier`）；而 `extra_body` 子字典则会合并到请求的 `extra_body` 中。显式设置的值会**覆盖**运行时或父级生成的默认值：显式的顶层键具有优先权，`extra_body` 则会在相应层级进行深度合并，因此除非你的设置重新定义了它，否则提供方自身的请求配置（例如 `thinking: {type: disabled}`）依然会保留。详情请参阅 [配置 → 委派机制](../configuration.md#delegation)。

:::提示
智能体会根据任务复杂度自动处理委派操作。你无需手动要求其进行委派——在合适的情况下它便会自动执行。:::
