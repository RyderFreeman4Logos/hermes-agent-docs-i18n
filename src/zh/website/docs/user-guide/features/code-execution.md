---
sidebar_position: 8
title: "Code Execution"
description: "Programmatic Python execution with RPC tool access — collapse multi-step workflows into a single turn"
---

# 代码执行（程序化工具调用）

`execute_code` 工具允许智能体编写 Python 脚本，以程序化方式调用 Hermes 工具，从而将多步骤工作流整合为单次大语言模型响应。该脚本在智能体主机上的子进程中运行，并通过 Unix 域套接字 RPC 与 Hermes 进行通信。

## 工作原理

1. 智能体使用 `from hermes_tools import ...` 编写 Python 脚本；
2. Hermes 会生成一个包含 RPC 函数的 `hermes_tools.py` 存根模块；
3. Hermes 打开一个 Unix 域套接字并启动一个 RPC 监听线程；
4. 脚本在子进程中运行，工具调用会通过套接字传回给 Hermes；
5. 仅脚本的 `print()` 输出会被返回给大语言模型，而中间工具处理结果永远不会进入上下文窗口。

```python
# The agent can write scripts like:
from hermes_tools import web_search, web_extract

results = web_search("Python 3.13 features", limit=5)
for r in results["data"]["web"]:
    content = web_extract([r["url"]])
    # ... filter and process ...
print(summary)
```

**脚本中可用的工具：** `web_search`、`web_extract`、`read_file`、`write_file`、`search_files`、`patch`、`terminal`（仅限前台使用）。

## Agent何时使用此功能

当出现以下情况时，Agent会使用`execute_code`功能：

- **3次及以上的工具调用**，且这些调用之间存在处理逻辑
- 需要对大量数据进行筛选或条件分支处理
- 需要遍历处理结果

其核心优势在于：中间阶段的工具处理结果不会进入上下文窗口——只有最终的`print()`输出会被返回，从而大幅降低token使用量。

## 实际应用示例

### 数据处理流程

```python
from hermes_tools import search_files, read_file
import json

# Find all config files and extract database settings
matches = search_files("database", path=".", file_glob="*.yaml", limit=20)
configs = []
for match in matches.get("matches", []):
    content = read_file(match["path"])
    configs.append({"file": match["path"], "preview": content["content"][:200]})

print(json.dumps(configs, indent=2))
```

### 多步骤网络调研功能

```python
from hermes_tools import web_search, web_extract
import json

# Search, extract, and summarize in one turn
results = web_search("Rust async runtime comparison 2025", limit=5)
summaries = []
for r in results["data"]["web"]:
    page = web_extract([r["url"]])
    for p in page.get("results", []):
        if p.get("content"):
            summaries.append({
                "title": r["title"],
                "url": r["url"],
                "excerpt": p["content"][:500]
            })

print(json.dumps(summaries, indent=2))
```

### 批量文件重构

```python
from hermes_tools import search_files, read_file, patch

# Find all Python files using deprecated API and fix them
matches = search_files("old_api_call", path="src/", file_glob="*.py")
fixed = 0
for match in matches.get("matches", []):
    result = patch(
        path=match["path"],
        old_string="old_api_call(",
        new_string="new_api_call(",
        replace_all=True
    )
    if "error" not in str(result):
        fixed += 1

print(f"Fixed {fixed} files out of {len(matches.get('matches', []))} matches")
```

### 构建与测试流程

```python
from hermes_tools import terminal, read_file
import json

# Run tests, parse results, and report
result = terminal("cd /project && python -m pytest --tb=short -q 2>&1", timeout=120)
output = result.get("output", "")

# Parse test output
passed = output.count(" passed")
failed = output.count(" failed")
errors = output.count(" error")

report = {
    "passed": passed,
    "failed": failed,
    "errors": errors,
    "exit_code": result.get("exit_code", -1),
    "summary": output[-500:] if len(output) > 500 else output
}

print(json.dumps(report, indent=2))
```

## 执行模式

`execute_code` 具有两种执行模式，可通过 `~/.hermes/config.yaml` 文件中的 `code_execution.mode` 参数进行控制：

| 模式 | 工作目录 | Python 解释器 |
|------|----------|----------------|
| **`project`**（默认） | 会话的工作目录（与 `terminal()` 相同） | 当前激活的 `VIRTUAL_ENV` / `CONDA_PREFIX` 环境中的 Python，若未找到则使用 Hermes 自带的 Python |
| `strict` | 一个与用户项目隔离的临时暂存目录 | `sys.executable`（即 Hermes 自带的 Python） |

**何时选择 `project` 模式：** 当你需要让 `import pandas`、`from my_project import foo` 以及类似 `open(".env")` 的相对路径调用方式与在 `terminal()` 中完全一致时。这几乎总是用户的需求。

**何时切换到 `strict` 模式：** 当你需要实现最高程度的可重复性——即无论用户激活了哪个虚拟环境，每次会话都使用相同的解释器；同时希望将脚本与项目目录隔离，避免因相对路径而意外读取项目文件。

```yaml
# ~/.hermes/config.yaml
code_execution:
  mode: project   # or "strict"
```

`project` 模式下的回退机制：如果 `VIRTUAL_ENV` / `CONDA_PREFIX` 未被设置、存在问题，或指向的 Python 版本低于 3.8，解析器会自动回退至 `sys.executable` —— 确保代理始终拥有可正常运行的解释器。

两种模式下均遵循相同的关键安全准则：

- 环境清理（移除 API 密钥、令牌及敏感凭证）
- 工具白名单（脚本不得递归调用 `execute_code`、`delegate_task` 或 MCP 工具）
- 资源限制（超时时间、标准输出上限及工具调用次数上限）

模式切换仅改变脚本的运行位置及执行它们的解释器，不会影响脚本能访问的凭证或可调用的工具。

## 资源限制

| 资源类型 | 限制值 | 备注 |
|----------|--------|------|
| **超时时间** | 5 分钟（300 秒） | 脚本首先会收到 SIGTERM 信号，5 秒宽限期过后才会被强制终止 |
| **标准输出** | 50 KB | 仅显示开头和结尾部分内容；完整输出会保存至 `~/.hermes/cache/exec/` 目录，路径信息也会一并返回 |
| **标准错误** | 10 KB | 当脚本退出码非零时，相关错误信息会包含在输出中以便调试 |
| **工具调用次数** | 每次执行最多 50 次 | 达到上限时会返回错误 |

所有限制均可通过 `config.yaml` 文件进行配置：

```yaml
# In ~/.hermes/config.yaml
code_execution:
  mode: project      # project (default) | strict
  timeout: 300       # Max seconds per script (default: 300)
  max_tool_calls: 50 # Max tool calls per execution (default: 50)
```

## 调用间的状态保持（会话内核）

在本地终端后端，`execute_code` 函数并不会为每次调用都启动全新的解释器。每个会话都会拥有一个持久化的 Python 内核，因此某次调用中定义的变量、导入的模块以及加载的数据在后续调用中依然有效。智能体只需加载数据集一次，即可在多轮对话中反复查询，而无需每次都重新读取。子智能体则拥有各自独立的内核，不同会话之间的内核绝不会共享。

导致内核终止的情况包括：

- **超时或中断**：当某个代码单元超过超时时间（或被主动中断）时，该内核进程会被终止，其状态也会被有意清除；系统会给出相应提示，随后新的调用会启动一个全新的内核。
- **`reset=true`**：智能体可以通过设置 `reset: true` 来丢弃当前内核的状态并重新开始。这也是响应环境变化的一种方式——内核创建时其环境是固定的，因此新加入的允许通过变量在内核被重置之前是不可见的。
- **空闲超时与强制终止**：内核会在会话结束时终止，具体时间为经过 `code_execution.kernel_idle_timeout` 秒的空闲时间后（默认为 1800 秒）；或者当活跃的内核数量超过 `code_execution.max_session_kernels` 的上限（默认为 4 个）时，最旧的内核会被强制终止。

其安全机制与一次性脚本相同：环境清理、工具白名单以及每次调用可使用的工具额度均适用于所有代码单元，而工具调用权限（审批、会话限制、允许列表等）也会在每个代码单元中被重新验证。

```yaml
# ~/.hermes/config.yaml
code_execution:
  kernel_idle_timeout: 1800   # seconds a kernel may sit idle before it is reaped
  max_session_kernels: 4      # kernels kept alive at once; oldest is evicted past this
```

**远程后端**（Docker、SSH、Modal）会使用具有相同接口协议的远程会话内核来运行任务。如果无法在相应后端启动该内核，Hermes 会转而将每次调用作为独立脚本执行，并在结果中说明这一情况。

**大量输出处理**：输出内容超过 50 KB 时，系统会以首尾截取的方式在线显示，完整文本则会保存在 `~/.hermes/cache/exec/` 目录下，结果中会同时提供文件路径，这样代理就可以使用 `read_file` 函数分页查看内容，而无需重新运行脚本。

## 脚本中的工具调用机制

当您的脚本调用类似 `web_search("query")` 这样的函数时：

1. 该调用会被序列化为 JSON 格式，通过 Unix 域套接字发送给父进程；
2. 父进程会通过标准的 `handle_function_call` 处理器来处理该请求；
3. 处理结果会通过套接字传回；
4. 函数最终返回解析后的结果。

这意味着脚本中的工具调用与常规工具调用行为完全一致——具备相同的速率限制、错误处理机制及功能支持。唯一的限制是 `terminal()` 函数仅支持前台使用（不支持 `background` 或 `pty` 参数）。

## 错误处理

当脚本执行失败时，代理会收到结构化的错误信息：

- **非零退出码**：错误输出会被一并返回，从而使智能体能够查看完整的堆栈跟踪信息。  
- **超时**：脚本将被强制终止，智能体将收到消息“脚本在300秒后超时并被终止”。  
- **中断**：如果在脚本执行过程中用户发送了新消息，脚本将会立即结束，智能体会显示 “[执行被中断 — 用户发送了新消息]” 的提示。  
- **工具调用限制**：一旦达到50次调用的上限，后续的工具调用都会返回错误信息。

响应内容始终包含 `status`（成功/失败/超时/中断）、`output`、`tool_calls_made` 以及 `duration_seconds` 这几项信息。

## 安全性

:::danger 安全模型  
子进程在**极简环境**中运行。API密钥、令牌及凭证默认会被移除。脚本仅能通过RPC通道来调用工具——除非得到明确允许，否则无法从环境变量中读取敏感信息。  
:::

凡是名称中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD` 或 `AUTH` 的环境变量都会被排除在外。只有安全的系统变量（如 `PATH`、`HOME`、`LANG`、`SHELL`、`PYTHONPATH`、`VIRTUAL_ENV` 等）才会被传递给子进程。

### 技能环境变量传递机制  

当某个技能在其配置文件中声明了 `required_environment_variables` 后，该技能加载完成后，这些变量会**自动传递**给 `execute_code` 和 `terminal` 两个子进程。这样一来，技能即可使用其指定的API密钥，同时不会因允许任意代码运行而降低整体安全性。

对于非技能型使用场景，您可以在 `config.yaml` 中明确列出允许使用的变量：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

如需详细信息，请参阅[安全指南](/user-guide/security#environment-variable-passthrough)。

### 子进程中的 `HERMES_*` 变量

子进程仅会按固定名称接收少量必需的 `HERMES_*` 运行时变量：

- `HERMES_HOME`
- `HERMES_PROFILE`
- `HERMES_CONFIG`
- `HERMES_ENV`

（此外还包括 `HERMES_RPC_DIR` / `HERMES_RPC_SOCKET` / `TZ` / `HOME`，这些是由 Hermes 显式注入的，以确保 RPC 通道正常工作）。

:::注意 行为变更
在早期版本中，任何名称以 `HERMES_` 开头的变量都会被传递给子进程。为加强安全性，这一宽泛的前缀已被移除：因为该机制可能导致那些不包含机密子串的 `HERMES_*` 命名配置（例如 `HERMES_BASE_URL`、`HERMES_KANBAN_DB` 或 `HERMES_*_WEBHOOK` 接口地址）泄露到任意沙箱代码中。

如果某个 `execute_code` 脚本，或其导入时所引用的仓库/插件模块依赖于上述四种必需变量之外的 `HERMES_*` 变量，那么在子进程中该变量将会被设置为**未定义**状态。这种变化是刻意为之，并非错误。
:::

**解决方案——手动重新启用该变量。** 无论是通过 `execute_code` 还是 `terminal` 子进程传递变量，都不会削弱机密信息过滤机制（由 Hermes 管理的提供程序凭证绝不会因此被重新允许传递）：

1. **在每台机器的 `config.yaml` 中**——将具体的变量名称添加到传递允许列表中：

   ```yaml
   terminal:
     env_passthrough:
       - HERMES_KANBAN_DB
       - HERMES_BASE_URL
   ```

2. **在技能的 frontmatter 中按技能单独声明**——通过此方式声明后，每当该技能被加载时就会自动完成注册：

   ```yaml
   required_environment_variables:
     - HERMES_KANBAN_DB
   ```

**故障诊断。** 当子进程使用了一个或多个未被允许的 `HERMES_*` 变量时，Hermes 会输出一条简短的 `debug` 日志，列出这些变量名称，并提示可利用 `env_passthrough` 机制来解决该问题。若脚本的表现如同缺少了 `HERMES_*` 变量，建议开启调试模式运行（使用 `hermes logs --level DEBUG` 命令，或查看 `~/.hermes/logs/agent.log` 文件），并查找类似 “execute_code: dropped N non-allowlisted HERMES_* var(s)” 的记录。

Hermes 会始终将脚本以及自动生成的 `hermes_tools.py` RPC 接口桩文件写入一个临时暂存目录，该目录会在执行完成后被清理。在 `strict` 模式下，脚本也会在该目录中运行；而在 `project` 模式下，则在会话的工作目录中执行（暂存目录仍会被加入 `PYTHONPATH`，因此仍可正常导入依赖）。子进程会在独立的进程组中运行，这样在超时或中断时便可轻松终止它。

## execute_code 与 terminal 的对比

| 使用场景 | execute_code | terminal |
|----------|-------------|----------|
| 需要在多个步骤间调用工具的复杂工作流 | ✅ | ❌ |
| 简单的 shell 命令 | ❌ | ✅ |
| 对大量工具输出进行过滤/处理 | ✅ | ❌ |
| 运行构建或测试套件 | ❌ | ✅ |
| 遍历搜索结果 | ✅ | ❌ |
| 交互式/后台进程 | ❌ | ✅ |
| 需要在环境中使用 API 密钥 | ⚠️ 仅可通过 [passthrough](/user-guide/security#environment-variable-passthrough) 实现 | ✅（大多数情况可直接使用） |
**实用建议：** 当您需要以编程方式调用 Hermes 工具，并且在多次调用之间需要执行逻辑时，应使用 `execute_code`。而用于运行 shell 命令、构建任务及处理流程的场景，则适合使用 `terminal`。

## 平台支持

代码执行功能支持在 **Linux、macOS 和 Windows** 系统上使用。在 Linux 和 macOS 上，RPC 通信通过 Unix 域套接字实现；而在 Windows 系统中，由于 `AF_UNIX` 方式不可靠，Hermes 会自动切换为回环 TCP 套接字作为沙箱内的 RPC 传输方式。至于远程终端后端（如 Docker/SSH/Modal 等），则采用基于文件的 RPC 传输机制，且要求后端环境中必须安装 Python 3。
