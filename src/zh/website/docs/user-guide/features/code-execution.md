---
sidebar_position: 8
title: "Code Execution"
description: "Programmatic Python execution with RPC tool access — collapse multi-step workflows into a single turn"
---

# 代码执行（程序化工具调用）

`execute_code` 工具允许智能体编写 Python 脚本，以程序化方式调用 Hermes 工具，从而将多步骤工作流整合为单次 LLM 应答。该脚本在智能体主机上的子进程中运行，并通过 Unix 域套接字 RPC 与 Hermes 进行通信。

## 工作原理

1. 智能体使用 `from hermes_tools import ...` 编写 Python 脚本；
2. Hermes 会生成一个包含 RPC 函数的 `hermes_tools.py` 存根模块；
3. Hermes 打开一个 Unix 域套接字并启动一个 RPC 监听线程；
4. 脚本在子进程中运行，工具调用会通过套接字传回 Hermes；
5. 仅脚本的 `print()` 输出会被返回给 LLM，中间工具的处理结果永远不会进入上下文窗口。

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

## 代理何时会使用此功能

当出现以下情况时，代理会使用 `execute_code` 功能：

- **3次及以上的工具调用**，且这些调用之间存在处理逻辑
- 需要对大量数据进行筛选或条件分支处理
- 需要遍历处理结果

其核心优势在于：中间工具的运行结果不会进入上下文窗口——只有最终的 `print()` 输出会被返回，从而大幅降低令牌使用量。

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

**何时选择 `project` 模式：** 当您希望 `import pandas`、`from my_project import foo` 以及类似 `open(".env")` 的相对路径能像在 `terminal()` 中那样正常工作时。这几乎总是用户的需求。

**何时切换到 `strict` 模式：** 当您需要极高的可重复性——即无论用户激活了哪个虚拟环境，每次会话都使用相同的解释器；同时希望将脚本与项目目录完全隔离，避免因相对路径而意外读取项目文件。

```yaml
# ~/.hermes/config.yaml
code_execution:
  mode: project   # or "strict"
```

`project` 模式下的回退机制：如果 `VIRTUAL_ENV` / `CONDA_PREFIX` 未被设置、无效，或指向的 Python 版本低于 3.8，解析器会自动回退到 `sys.executable` —— 确保代理始终拥有可正常运行的解释器。

两种模式下均遵循相同的关键安全准则：

- 环境清理（移除 API 密钥、令牌及凭证）
- 工具白名单（脚本不得递归调用 `execute_code`、`delegate_task` 或 MCP 工具）
- 资源限制（超时时间、标准输出上限、工具调用次数上限）

模式切换仅改变脚本的运行位置及执行它们的解释器，而不会影响脚本能访问的凭证或可调用的工具。

## 资源限制

| 资源类型 | 限制值 | 备注 |
|----------|--------|------|
| **超时时间** | 5 分钟（300 秒） | 脚本首先收到 SIGTERM 信号，5 秒宽限期过后将被强制终止 |
| **标准输出** | 50 KB | 超出限制时输出会被截断，并显示 `[output truncated at 50KB]` 提示 |
| **标准错误** | 10 KB | 程序非正常退出时，该内容会包含在输出中以便调试 |
| **工具调用次数** | 每次执行 50 次 | 达到上限时会返回错误 |

所有限制均可通过 `config.yaml` 文件进行配置：

```yaml
# In ~/.hermes/config.yaml
code_execution:
  mode: project      # project (default) | strict
  timeout: 300       # Max seconds per script (default: 300)
  max_tool_calls: 50 # Max tool calls per execution (default: 50)
```

## 脚本中工具调用的工作原理

当您的脚本调用类似 `web_search("query")` 这样的函数时：

1. 该调用会被序列化为 JSON 格式，通过 Unix 域套接字发送给父进程；
2. 父进程会通过标准的 `handle_function_call` 处理器来处理该请求；
3. 处理结果会通过套接字传回；
4. 函数最终返回解析后的结果。

这意味着脚本中的工具调用与常规工具调用行为完全一致——具有相同的速率限制、错误处理机制及功能能力。唯一的限制是 `terminal()` 函数仅支持前台运行（不支持 `background` 或 `pty` 参数）。

## 错误处理

当脚本执行失败时，智能体将会收到结构化的错误信息：

- **非零退出码**：错误输出中会包含标准错误流内容，从而使智能体能够查看完整的堆栈跟踪信息；
- **超时**：脚本会被强制终止，智能体会收到提示信息 `"Script timed out after 300s and was killed."`；
- **执行中断**：如果在脚本运行过程中用户发送了新消息，脚本将会被终止，智能体会显示 `[execution interrupted — user sent a new message]`；
- **工具调用次数限制**：当达到 50 次调用的上限时，后续的工具调用将会返回错误信息。

响应内容始终包含 `status`（成功/失败/超时/中断）、`output`、`tool_calls_made` 以及 `duration_seconds` 等字段。

## 安全性

:::danger 安全模型
子进程在**极简环境**中运行。API 密钥、令牌及凭证默认会被移除。脚本只能通过 RPC 通道来调用工具——除非得到明确允许，否则无法从环境变量中读取敏感信息。
:::

名称中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD` 或 `AUTH` 字段的变量将被排除在外。只有安全的系统变量（如 `PATH`、`HOME`、`LANG`、`SHELL`、`PYTHONPATH`、`VIRTUAL_ENV` 等）才会被传递给子进程。

### 技能相关环境变量的传递

当某个技能在其配置文件的前置信息中声明了 `required_environment_variables` 后，这些变量会在该技能加载完成后**自动传递**给 `execute_code` 和 `terminal` 两个子进程。这样一来，技能即可使用其指定的 API 密钥，同时不会降低对任意代码的安全防护水平。

对于非技能类使用场景，您可以在 `config.yaml` 文件中明确指定允许通过的变量列表：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

详情请参阅[安全指南](/user-guide/security#environment-variable-passthrough)。

### 子进程中的 `HERMES_*` 变量

子进程仅会以精确名称的形式接收一组固定数量的运行所需 `HERMES_*` 变量：

- `HERMES_HOME`
- `HERMES_PROFILE`
- `HERMES_CONFIG`
- `HERMES_ENV`

（此外还包括 `HERMES_RPC_DIR` / `HERMES_RPC_SOCKET` / `TZ` / `HOME`，这些变量是 Hermes 为确保 RPC 通道正常工作而明确注入的）。

:::注意 行为变更
在早期版本中，任何名称以 `HERMES_` 开头的变量都会被传递给子进程。为加强安全性，这一宽泛的前缀已被移除：因为该机制可能导致那些不包含敏感子字符串的 `HERMES_*` 命名配置（例如 `HERMES_BASE_URL`、`HERMES_KANBAN_DB` 或 `HERMES_*_WEBHOOK` 接口地址）泄露到任意沙箱代码中。

如果某个 `execute_code` 脚本，或其导入时所引用的仓库/插件模块依赖于上述四种运行所需变量之外的 `HERMES_*` 变量，那么在子进程中该变量将会被设置为**未定义**状态。此行为是刻意为之，并非漏洞。
:::

**解决方案——手动重新启用该变量。** 两种方式都会将该变量同时传递给 `execute_code` *和* `terminal` 子进程，且都不会削弱敏感信息过滤机制（由 Hermes 管理的提供程序凭证绝不会通过这种方式被重新允许访问）：

1. **在每台机器的 `config.yaml` 中**——将具体的变量名称添加到传递允许列表中：

   ```yaml
   terminal:
     env_passthrough:
       - HERMES_KANBAN_DB
       - HERMES_BASE_URL
   ```

2. **在技能的 frontmatter 中按技能单独声明**——通过此方式声明后，每当该技能被加载时便会自动完成注册：

   ```yaml
   required_environment_variables:
     - HERMES_KANBAN_DB
   ```

**故障诊断方法**。当子进程使用了一个或多个未被允许的 `HERMES_*` 变量时，Hermes 会输出一条简短的 `debug` 日志，列明这些变量的名称，并提示可利用 `env_passthrough` 机制来解决该问题。请开启调试日志模式运行程序（使用 `hermes logs --level DEBUG`，或查看 `~/.hermes/logs/agent.log`），如果脚本的表现如同缺少了某个 `HERMES_*` 变量，便可在日志中查找类似 “execute_code: dropped N non-allowlisted HERMES_* var(s)” 的提示。

Hermes 会始终将脚本以及自动生成的 `hermes_tools.py` RPC 接口模板写入一个临时暂存目录，该目录会在程序执行完毕后自动清除。在“严格”模式下，脚本也会在该临时目录中运行；而在“项目”模式下，则会在会话的工作目录中运行（该暂存目录仍会被加入 `PYTHONPATH`，因此模块导入依然有效）。子进程会在独立的进程组中运行，这样在超时或中断时便可轻松终止它。

## execute_code 与 terminal 的区别

| 使用场景 | execute_code | terminal |
|----------|-------------|----------|
| 需要在多个步骤间调用工具的复杂工作流 | ✅ | ❌ |
| 简单的shell命令执行 | ❌ | ✅ |
| 对大量工具输出进行过滤/处理 | ✅ | ❌ |
| 运行构建或测试套件 | ❌ | ✅ |
| 遍历搜索结果 | ✅ | ❌ |
| 交互式/后台进程 | ❌ | ✅ |
| 需要在环境中使用API密钥 | ⚠️ 仅可通过[passthrough](/user-guide/security#environment-variable-passthrough)实现 | ✅（大多数情况可直接使用） |

**经验法则**：当需要以编程方式调用 Hermes 工具，并且在多次调用之间需要执行逻辑时，应使用 `execute_code`；而用于运行shell命令、执行构建操作或普通进程时，则适合使用 `terminal`。

## 平台支持情况

代码执行功能依赖于 Unix 域套接字，因此**仅支持 Linux 和 macOS**系统。在 Windows 系统上此功能会被自动禁用，此时代理会回退到传统的顺序式工具调用方式。
