# 贡献者快速参考指南

专为偶尔参与贡献及提交 Pull Request 的用户准备。完整的开发者文档请访问：https://hermes-agent.nousresearch.com/docs/developer-guide/

### 项目结构

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # Extensive pytest suite (run via scripts/run_tests.sh)
└── website/              # Docusaurus docs site
```

配置文件：`~/.hermes/config.yaml`（用于存储设置），`~/.hermes/.env`（用于存储 API 密钥）——若已设置 `$HERMES_HOME`，则这两个文件均位于该路径下。

### 添加工具

需要准备两个文件。自动发现功能会导入任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件，但只有当某个工具的名称被添加到工具集中时，它才会向智能体*公开*。

**1. 创建 `tools/your_tool.py` 文件：**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. 将其集成到 `toolsets.py` 中的工具集中** —— 将该工具的名称添加到 `_HERMES_CORE_TOOLS`（所有平台通用）或特定的工具集中。

所有的处理函数都必须返回 JSON 字符串。在获取路径时请使用 `get_hermes_home()` 函数，切勿直接硬编码 `~/.hermes` 路径。对于自定义的或仅限本地使用的工具，建议在 `~/.hermes/plugins/` 目录下编写插件，而非修改核心代码——详情请参阅开发者指南。

### 添加斜杠命令

1. 在 `hermes_cli/commands.py` 文件的 `COMMAND_REGISTRY` 中添加 `CommandDef` 定义。
2. 在 `cli.py` 文件中的 `process_command()` 函数中编写对应的处理逻辑。
3. （可选）在 `gateway/run.py` 文件中添加网关处理函数。

所有的使用场景（帮助文本、自动补全功能、Telegram 菜单、Slack 映射等）都会自动从这个中心注册表中获取相关功能。

### Agent 循环（概览）

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### 测试

请使用标准化的测试运行器——该运行器能够确保与持续集成流程保持一致（采用封闭式的 `env -i` 环境配置，不设置任何凭证信息，时区固定为 UTC，并通过 `scripts/run_tests_parallel.py` 实现逐文件子进程隔离——不使用 xdist 工具，且工作进程数量会自动调整）：

```bash
scripts/run_tests.sh                          # full suite
scripts/run_tests.sh tests/tools/             # one directory
scripts/run_tests.sh tests/tools/test_x.py    # one file
scripts/run_tests.sh -v --tb=long             # pass-through pytest flags
```

- 测试会自动将 `HERMES_HOME` 重定向至临时目录——绝不会触碰真实的 `~/.hermes/` 目录。  
- 脚本会依次检查 `.venv`、`venv`，以及共享工作区的虚拟环境。  
- **Windows 系统**：该封装仅支持 POSIX 标准；如需使用直接调用 pytest 的解决方案，请参阅 `references/windows-quirks.md`。  

**跨平台测试防护机制**：那些依赖 POSIX 标准系统调用的测试需要添加跳过标记。代码库中已包含的常见标记如下：  
- 创建符号链接 → `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")`（参见 `tests/cron/test_cron_script.py`）  
- POSIX 文件权限（如 0o600 等）→ `@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX mode bits not enforced on Windows")`（参见 `tests/hermes_cli/test_auth_toctou_file_modes.py`）  
- `signal.SIGALRM` → 该信号仅适用于 Unix 系统（当前各测试的超时处理已不再直接使用该信号；详情见 `tests/conftest.py::pytest_configure` 中的 win32 超时处理方案）  
- 实时 Winsock 功能/针对 Windows 的回归测试 → `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`  

如果被测代码同时调用了 `platform.system()`、`platform.release()` 或 `platform.mac_ver()` 函数，仅修改 `sys.platform` 是不够的。因为这些函数会独立读取真实的操作系统信息，因此在 Windows 环境下将 `sys.platform` 设为 `"linux"` 的测试，其结果仍会是 `platform.system() == "Windows"`，从而继续执行针对 Windows 的处理逻辑。需同时修改这三个函数的返回值。

```python
monkeypatch.setattr(sys, "platform", "linux")
monkeypatch.setattr(platform, "system", lambda: "Linux")
monkeypatch.setattr(platform, "release", lambda: "6.8.0-generic")
```

如需示例代码，请参阅 `tests/agent/test_prompt_builder.py::TestEnvironmentHints`。

### 系统提示的运行环境部分

关于主机/后端的相关信息（操作系统、`$/HOME`、当前工作目录、终端后端及Shell环境）由 `agent/prompt_builder.py::build_environment_hints()` 函数生成。对于提示编写者而言，需遵循一个重要原则：当使用**远程**终端后端（如 `docker`、`singularity`、`modal`、`daytona`、`ssh`、`managed_modal`）时，主机信息将被隐藏，且所有文件操作都会在对应的后端容器内执行——因此提示中绝不能描述代理无法访问的主机信息。

### 提交规范

```
type: concise subject line

Optional body.
```

类型：`fix:`、`feat:`、`refactor:`、`docs:`、`chore:`

### 核心规则

- **严禁破坏提示词缓存** —— 交谈过程中不得更改上下文、工具或系统提示词
- **消息角色交替发送** —— 严禁连续出现两条助手消息或两条用户消息
- 所有路径均需使用 `hermes_constants` 中的 `get_hermes_home()` 函数（可保障用户配置安全）
- 配置值应存放在 `config.yaml` 文件中，敏感信息则需保存在 `.env` 文件中
- 新工具必须定义 `check_fn` 函数，以便仅在满足特定条件时才会被启用
