# 为 Hermes Agent 做贡献

感谢您为 Hermes Agent 出力！本指南涵盖了您所需的所有内容：搭建开发环境、了解架构设计、确定要开发的功能，以及如何让您的 Pull Request 被合并。

---

## 贡献优先级

我们按照以下顺序重视各类贡献：

1. **错误修复** — 程序崩溃、异常行为、数据丢失等问题。始终为最高优先级。
2. **跨平台兼容性** — macOS、不同 Linux 发行版以及 Windows 上的 WSL2。我们希望 Hermes 能在所有平台上正常运行。
3. **安全性强化** — 命令注入、提示符注入、路径遍历、权限提升等问题。详情请参阅[安全考虑事项](#security-considerations)。
4. **性能与稳定性** — 重试机制、错误处理以及优雅降级功能。
5. **新技能** — 但仅限具有广泛实用价值的技能。详情请参阅[应该是技能还是工具？](#should-it-be-a-skill-or-a-tool)。
6. **新工具** — 几乎没有需求。大多数功能应以技能的形式实现，具体内容见下文。
7. **文档完善** — 错误修正、内容澄清以及新增示例。

---

## 开始之前：先进行搜索

在编写代码之前先快速搜索一下，既能节省您的时间，也能保持 Pull Request 队列的整洁——重复提交的情况十分常见，因此提前花一分钟搜索是值得的。

- 对与您要解决的问题或错误症状相关的**已开放及已合并的 Pull Request 和问题记录**进行搜索——Pull Request 模板中的重复内容检测功能会在代码审核阶段才触发，到那时您可能已经浪费了时间。
  ```bash
  gh search issues --repo NousResearch/hermes-agent "<your terms>"
  gh search prs --repo NousResearch/hermes-agent --state all "<your terms>"
  ```
或者可以使用网页界面：[问题追踪](https://github.com/NousResearch/hermes-agent/issues?q=) · [PRs（所有状态）](https://github.com/NousResearch/hermes-agent/pulls?q=is%3Apr)。  
- **问题追踪系统可能与代码更新存在延迟。** 许多用户请求的功能早已在代码中实现，因此在提出新需求之前，建议先通过源代码搜索（如 `search_files` 功能或编辑器自带的 grep 工具）确认该功能是否已存在。  
- **如果已有开放的 PR 正在处理该问题**，建议优先查看或改进那个 PR，而非重复创建新的提交。  
- **对于规模较大的任务**，可在对应问题上留言表明自己正在处理，以免他人重复开展工作。  

相关内容：#38284 涉及了代理端的类似机制——Hermes 会在进行深度自我排查之前先检查现有的问题与 PR。本部分则是为人工贡献者提供的补充说明。  

---

## 应该将其设计为技能还是工具？

这是新贡献者最常遇到的问题。答案几乎总是**技能**。  

### 何时应将其设为技能：  
- 该功能可通过指令、Shell 命令及现有工具来实现；  
- 它封装了外部 CLI 或 API，且代理能够通过 `terminal` 或 `web_extract` 功能调用这些接口；  
- 无需在代理中集成自定义的 Python 代码或处理 API 密钥管理功能。  
- **示例**：arXiv 搜索、Git 工作流管理、Docker 管理、PDF 处理、通过 CLI 工具发送邮件等。  

### 何时应将其设为工具：

- 需要与 API 密钥、身份验证流程，或由 Agent harness 管理的多组件配置实现端到端集成。  
- 需要具备自定义处理逻辑，且该逻辑必须每次都精确执行（而非依赖 LLM 的“尽力而为”式解读）。  
- 能够处理无法通过终端传输的二进制数据、流式数据或实时事件。  
- 典型应用场景包括：浏览器自动化（Browserbase 会话管理）、文本转语音（音频编码与平台推送）、视觉分析（base64 格式图像处理）。

### 是否应将该技能打包？

打包在 `skills/` 目录中的技能会随每次 Hermes 安装一同提供。这类技能应当**对大多数用户都具有广泛实用性**，例如：文档处理、网络搜索、常见开发工作流、系统管理，且会被大量用户频繁使用。

如果您的技能虽属官方出品且实用，但并非所有人都需要（比如某些付费服务集成或依赖庞大的外部组件），则应将其放入 **`optional-skills/`** 目录——该目录中的技能会随代码仓库一同提供，但默认不会被激活。用户可通过 `hermes skills browse` 查看这些标记为“官方”的技能，并使用 `hermes skills install` 进行安装（无需担心第三方风险，因其具有内置信任度）。

而对于那些专业化、由社区贡献或针对小众场景设计的技能，则更适合发布在 **Skills Hub** 平台上——将其上传至技能注册表后，即可在 [Nous Research Discord](https://discord.gg/NousResearch) 中分享。用户同样可通过 `hermes skills install` 来安装此类技能。

---

## 内存提供器：作为独立插件发布

**我们不再接受向该仓库添加新的内存提供程序。** `plugins/memory/` 目录下现有的内置提供程序（honcho、mem0、supermemory、byterover、hindsight、holographic、openviking、retaindb）已停止接收新功能添加。如果您想添加新的内存后端，应将其发布为**独立的插件仓库**，供用户安装到 `~/.hermes/plugins/` 目录中（或通过 pip 安装）。

独立的记忆插件需满足以下要求：

- 实现相同的 `MemoryProvider` ABC 接口（位于 `agent/memory_provider.py` 文件中），包括 `sync_turn`、`prefetch`、`shutdown` 方法；如需集成设置向导，还可选择实现 `post_setup(hermes_home, config)` 方法；
- 使用相同的发现机制——`discover_memory_providers()` 函数会从用户/项目插件目录及 pip 安装路径中自动检测这些插件；
- 通过 `post_setup()` 方法与 `hermes memory setup` 功能集成，无需修改核心代码；
- 可以在 `cli.py` 文件中使用 `register_cli(subparser)` 方法注册自定义的 CLI 子命令；
- 可享有与内置提供程序相同的生命周期钩子和配置管理功能。

对于那些试图在 `plugins/memory/` 目录下创建新子目录的提交请求，我们将予以拒绝，并建议将其作为独立仓库进行发布。现有的内置提供程序将继续保留，对其进行的错误修复也依然受到欢迎。

这并非质量标准，而是一项关于代码耦合度与维护效率的决策。由于内存提供程序是最常见的插件类型，因此并不适合全部集中存放于此目录中。

---

## 第三方产品集成：以独立插件形式发布

同样的规则也适用于**任何集成第三方产品或项目的插件**——无论是可观测性/指标后端、供应商的 SaaS 连接器、分析仪表板、付费服务集成，还是其他类似的第三方整合方案。**这类插件不会被放入此仓库中。**

原因在于维护负担，而非质量问题。每当有外部产品被纳入核心代码库，维护人员就必须在快速发展的代码体系以及并非由我们所有且无法控制的后端环境中，继续为其提供支持。Hermes 的更新频率很高，核心代码也在不断演进；将第三方产品与之耦合会给维护人员带来无尽的负担。

建议将这些插件作为**独立的插件仓库**来发布：

- 实现相应的 ABC 并使用现有的插件发现路径（`~/.hermes/plugins/`、项目级的 `.hermes/plugins/` 或 pip 入口），详情请参阅[构建 Hermes 插件](https://hermes-agent.nousresearch.com/docs/guides/build-a-hermes-plugin)；
- 通过已提供的接口注册生命周期钩子（`pre_tool_call`、`post_tool_call`、`pre_llm_call`、`post_llm_call`、`on_session_start`、`on_session_end`）、工具（`ctx.register_tool`）以及 CLI 子命令（`ctx.register_cli_command`），无需对核心代码进行修改；
- 如果您的插件需要框架未提供的功能，应提出需求以**扩展通用插件接口**（新增钩子或 `ctx` 方法），切勿在核心代码中为该插件编写特殊处理逻辑；
- 在 [Nous Research Discord](https://discord.gg/NousResearch) 的 `#plugins-skills-and-skins` 频道中宣传您的插件，以便用户发现并安装。

即便一个第三方产品插件开发得十分完善且已通过自动审查，仍可能因上述原因被拒绝——这属于发布决策，而非对代码质量的评判。那些在 `plugins/` 目录下添加此类插件的 Pull Request 也会被拒绝，并提示将其作为独立仓库发布。

---

## 开发环境配置

### 先决条件

| 要求 | 备注 |
|-------------|-------|
| **Git** | 需已安装 `git-lfs` 扩展 |
| **Python 3.11–3.13** | 若缺失，uv 会自动进行安装 |
| **uv** | 快速的 Python 包管理工具（[安装方式](https://docs.astral.sh/uv/)） |
| **Node.js 20+** | 非必需——用于浏览器工具及 WhatsApp 桥接功能（需与根目录下的 `package.json` 中指定的运行环境一致） |

### 使用标准安装程序进行安装

对于大多数贡献者而言，最便捷的开发启动方式与普通用户相同：运行标准安装程序，然后在克隆的代码仓库中进行开发。该安装程序会创建 Hermes 虚拟环境，配置 `hermes` 命令，标记 `hermes update` 的安装方式，并将完整的 Git 项目克隆到 `$HERMES_HOME/hermes-agent` 目录中（通常为 `~/.hermes/hermes-agent`）。这样一来，您的开发环境就能与 CLI、更新工具、延迟依赖安装器、网关以及文档所要求的结构保持一致。

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
cd "${HERMES_HOME:-$HOME/.hermes}/hermes-agent"

# Add dev/test extras on top of the standard install.
uv pip install -e ".[all,dev]"

# Optional: docs site + workspace dependencies.
npm install
```

之后，创建分支，并在该分支上运行测试：

```bash
git checkout -b fix/description
scripts/run_tests.sh
```

### 手动克隆作为备用方案

仅当您明确不想使用 Hermes 的托管安装结构时才应采用此方式（例如在容器或 CI 任务中使用的临时克隆项目）。若选择这种方式安装，请务必从该虚拟环境运行 `hermes` 入口程序；直接使用系统命令 `python3 -m hermes_cli.main` 可能会引入与当前项目无关的系统 Python 包。

请在**已克隆的源代码目录之外**创建虚拟环境。如果虚拟环境位于代理程序运行的目录内，代理程序可能会对其自身checkout的路径执行相对路径命令（如 `rm -rf venv`、`uv venv venv` 等），从而悄无声息地破坏正在运行的运行时环境，导致会话中断。将虚拟环境置于目录之外，可确保工作区中的任何相对路径都无法指向它。

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# Create venv with Python 3.11, OUTSIDE the source tree
uv venv ~/.hermes/venvs/hermes-dev --python 3.11
export VIRTUAL_ENV="$HOME/.hermes/venvs/hermes-dev"
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Install with all extras (messaging, cron, CLI menus, dev tools)
uv pip install -e ".[all,dev]"

# Optional: workspace / docs dependencies
npm install
```

### 开发环境配置

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# Add at minimum an LLM provider key:
echo "OPENROUTER_API_KEY=***" >> ~/.hermes/.env
```

### 运行

```bash
# The standard installer already put `hermes` on PATH.
hermes doctor
hermes chat -q "Hello"
```

如果您使用了手动克隆的备用方案，请从代码检出目录运行 `./hermes`，或明确地创建该克隆版本的虚拟环境符号链接：

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
```

### 运行测试

```bash
# Preferred — matches CI (hermetic `env -i`, per-file subprocess isolation
# via run_tests_parallel.py, worker count auto-scaled); see AGENTS.md
scripts/run_tests.sh

# Alternative (activate the venv first). The wrapper is still recommended
# for parity with GitHub Actions before you open a PR:
pytest tests/ -v
```

## 项目结构

```
hermes-agent/
├── run_agent.py              # AIAgent facade (~1.5k LOC) — the turn loop lives in agent/conversation_loop.py + agent/turn_*.py
├── cli.py                    # HermesCLI class — interactive CLI orchestrator (~4.6k LOC + hermes_cli/cli_*_mixin.py)
├── model_tools.py            # Tool orchestration (thin layer over tools/registry.py)
├── toolsets.py               # Tool groupings and presets (hermes-cli, hermes-telegram, etc.)
├── hermes_state.py           # SessionDB facade (~1.4k LOC); implementation in hermes_state_*.py (21 siblings) — FTS5 search, session titles
├── batch_runner.py           # Parallel batch processing for trajectory generation
│
├── agent/                    # Agent internals (extracted modules)
│   ├── conversation_loop.py      # run_conversation() — the agent turn loop (phases in turn_*.py)
│   ├── tool_executor.py          # Tool dispatch (inline agent-level tools, delegate, registry)
│   ├── session_persistence.py    # Session/trajectory saving
│   ├── prompt_builder.py         # System prompt assembly (identity, skills, context files, memory)
│   ├── context_compressor.py     # Auto-summarization when approaching context limits
│   ├── auxiliary_client.py       # Resolves auxiliary OpenAI clients (summarization, vision)
│   ├── display.py                # KawaiiSpinner, tool progress formatting
│   ├── model_metadata.py         # Model context lengths, token estimation
│   └── trajectory.py             # Trajectory saving helpers
│
├── hermes_cli/               # CLI command implementations
│   ├── main.py                   # Entry point, argument parsing, command dispatch
│   ├── cli_*_mixin.py            # HermesCLI mixins (slash commands, display, session, ...)
│   ├── config.py                 # Config management, migration, env var definitions
│   ├── setup.py                  # Interactive setup wizard
│   ├── auth.py                   # Provider resolution, OAuth, Nous Portal (facade + auth_*.py siblings)
│   ├── models.py                 # OpenRouter model selection lists
│   ├── banner.py                 # Welcome banner, ASCII art
│   ├── commands.py               # Central slash command registry (CommandDef), autocomplete, gateway helpers
│   ├── callbacks.py              # Interactive callbacks (clarify, sudo, approval)
│   ├── doctor.py                 # Diagnostics
│   ├── skills_hub.py             # Skills Hub CLI + /skills slash command
│   ├── skin_engine.py            # Skin/theme engine — data-driven CLI visual customization
│   ├── web_server.py             # Dashboard server (facade + web_server_*.py siblings)
│   └── web_routers/              # Dashboard FastAPI routers (one file per surface)
│
├── tools/                    # Tool implementations (self-registering)
│   ├── registry.py               # Central tool registry (schemas, handlers, dispatch)
│   ├── approval.py               # Dangerous command detection + per-session approval
│   ├── terminal_tool.py          # Terminal orchestration (sudo, env lifecycle, backends)
│   ├── file_operations.py        # read_file, write_file, search, patch, etc.
│   ├── web_tools.py              # web_search, web_extract (Parallel/Firecrawl + Gemini summarization)
│   ├── vision_tools.py           # Image analysis via multimodal models
│   ├── delegate_tool.py          # Subagent spawning and parallel task execution
│   ├── code_execution_tool.py    # Sandboxed Python with RPC tool access (env allowlists in code_execution_env.py)
│   ├── mcp_tool.py               # MCP client (facade + mcp_tool_*.py siblings: config, discovery, transport, ...)
│   ├── browser_tool.py           # Browser automation (facade + browser_tool_*.py siblings)
│   ├── session_search_tool.py    # Search past conversations with FTS5 + anchored windows
│   ├── cronjob_tools.py          # Scheduled task management
│   ├── skill_tools.py            # Skill search, load, manage
│   └── environments/             # Terminal execution backends
│       ├── base.py                   # BaseEnvironment ABC
│       ├── local.py, docker.py, ssh.py, singularity.py, modal.py, daytona.py
│
├── gateway/                  # Messaging gateway
│   ├── run.py                    # GatewayRunner facade (~5.5k LOC); phases in run_*.py (startup, inbound, turn, busy, ...)
│   ├── slash_commands_*.py       # Gateway slash command handler mixins
│   ├── config.py                 # Platform configuration resolution
│   ├── session.py                # Session store, context prompts, explicit resets (+ session_*.py siblings)
│   └── platforms/                # Platform adapters
│       ├── telegram.py, discord_adapter.py, slack.py, whatsapp.py
│
├── scripts/                  # Installer and bridge scripts
│   ├── install.sh                # Linux/macOS installer
│   ├── install.ps1               # Windows PowerShell installer
│   └── whatsapp-bridge/          # Node.js WhatsApp bridge (Baileys)
│
├── skills/                   # Bundled skills (copied to ~/.hermes/skills/ on install)
├── optional-skills/          # Official optional skills (discoverable via hub, not activated by default)
├── tests/                    # Test suite
├── website/                  # Documentation site (hermes-agent.nousresearch.com)
│
├── cli-config.yaml.example   # Example configuration (copied to ~/.hermes/config.yaml)
└── AGENTS.md                 # Development guide for AI coding assistants
```

### 用户配置（存储在 `~/.hermes/` 目录中）

| 路径 | 用途 |
|------|---------|
| `~/.hermes/config.yaml` | 设置选项（模型、终端、工具集、压缩等功能） |
| `~/.hermes/.env` | API 密钥与敏感信息 |
| `~/.hermes/auth.json` | OAuth 认证凭证（Nous Portal 使用） |
| `~/.hermes/skills/` | 所有已激活的技能（打包内置的、通过 Hub 安装的以及由 Agent 创建的） |
| `~/.hermes/memories/` | 持久化记忆内容（MEMORY.md、USER.md 文件） |
| `~/.hermes/state.db` | SQLite 会话数据库 |
| `~/.hermes/sessions/` | 网关路由索引（`sessions.json`）、请求转储记录、网关生成的 `*.jsonl` 转录文件，以及手动导出的 `/save` 文件。系统不再自动生成每会话的 JSON 快照，state.db 即为标准状态存储文件。 |
| `~/.hermes/cron/` | 定时任务相关数据 |
| `~/.hermes/whatsapp/session/` | WhatsApp 桥接工具的认证凭证 |

---

## 架构概览

### 核心循环机制

```
User message → AIAgent._run_agent_loop()
  ├── Build system prompt (prompt_builder.py)
  ├── Build API kwargs (model, messages, tools, reasoning config)
  ├── Call LLM (OpenAI-compatible API)
  ├── If tool_calls in response:
  │     ├── Execute each tool via registry dispatch
  │     ├── Add tool results to conversation
  │     └── Loop back to LLM call
  ├── If text response:
  │     ├── Persist session to DB
  │     └── Return final_response
  └── Context compression if approaching token limit
```

### 核心设计模式

- **自动注册工具**：每个工具文件在导入时都会调用 `registry.register()` 函数。`model_tools.py` 通过导入所有工具模块来触发工具发现机制。
- **工具集分组**：工具被划分到不同的工具集中（如 `web`、`terminal`、`file`、`browser` 等），可根据不同平台需求启用或禁用这些工具集。
- **会话持久化**：所有对话内容均存储在 SQLite 数据库中（由 `hermes_state.py` 负责管理），支持全文搜索并为每个会话设置唯一标题。系统已取消自动生成会话级 JSON 快照的功能；现有文件不会被修改，如需手动导出，请使用 `/save json` 或 `hermes sessions export` 命令。
- **临时注入机制**：系统提示和预填信息会在 API 调用时动态注入，绝不会被保存到数据库或日志中。
- **提供者抽象层**：该智能体可适配任何兼容 OpenAI 的 API。提供者的识别工作在初始化阶段完成，支持通过 Nous Portal OAuth、OpenRouter API 密钥或自定义端点进行配置。
- **提供者路由功能**：在使用 OpenRouter 时，可通过 `config.yaml` 文件中的 `provider_routing` 参数来控制提供者的选择方式（如按吞吐量/延迟/价格排序、允许或忽略特定提供者、设置数据保留策略）。这些配置会以 `extra_body.provider` 的形式嵌入到 API 请求中。

---

## 代码风格规范

- 遵循 **PEP 8** 规范，但允许适当例外（我们不强制要求严格的行长度限制）  
- **注释**：仅用于说明那些不显而易见的意图、权衡因素或 API 的特殊之处。切勿描述代码的功能——`# 增加计数器` 这样的注释毫无意义  
- **错误处理**：捕获特定的异常。使用 `logger.warning()`/`logger.error()` 记录日志；对于意外错误，请设置 `exc_info=True` 以便在日志中显示堆栈跟踪信息  
- **跨平台兼容性**：切勿默认代码仅在 Unix 系统上运行。详情请参阅 [跨平台兼容性](#cross-platform-compatibility)  

---

## 添加新工具

在编写工具之前，先思考：[这是否应该被视为一项技能而非工具？](#should-it-be-a-skill-or-a-tool)  

工具会自动向中央注册表进行注册。每个工具文件都会将其结构定义、处理逻辑及注册信息集中存放于同一位置：

```python
"""my_tool — Brief description of what this tool does."""

import json
from tools.registry import registry


def my_tool(param1: str, param2: int = 10, **kwargs) -> str:
    """Handler. Returns a string result (often JSON)."""
    result = do_work(param1, param2)
    return json.dumps(result)


MY_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "What this tool does and when the agent should use it.",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "What param1 is"},
                "param2": {"type": "integer", "description": "What param2 is", "default": 10},
            },
            "required": ["param1"],
        },
    },
}


def _check_requirements() -> bool:
    """Return True if this tool's dependencies are available."""
    return True


registry.register(
    name="my_tool",
    toolset="my_toolset",
    schema=MY_TOOL_SCHEMA,
    handler=lambda args, **kw: my_tool(**args, **kw),
    check_fn=_check_requirements,
)
```

**连接到工具集（必需）：** 内置工具会自动被发现：当 `model_tools` 被加载时，`tools/registry.py` 中的 `discover_builtin_tools()` 函数会自动导入任何包含顶层 `registry.register(...)` 调用的 `tools/*.py` 文件。无需在 `model_tools.py` 中手动维护导入列表。

您仍需将工具名称添加到 `toolsets.py` 中对应的列表中（例如 `_HERMES_CORE_TOOLS` 或专用的工具集）；否则该工具虽然会注册，但永远不会向智能体暴露。如果您要创建新的工具集，请在 `toolsets.py` 中添加它，并将其连接到相关的平台预设中。

有关基于配置文件的路径选择以及插件与核心组件的使用指南，请参阅 `AGENTS.md` 文件中的“添加新工具”部分。

---

## 添加技能

预置的技能按类别存储在 `skills/` 目录下。官方提供的可选技能则采用相同的结构，存放在 `optional-skills/` 目录中：

```
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md              # Required: main instructions
│       └── scripts/              # Optional: helper scripts
│           └── search_arxiv.py
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── ...
```

### SKILL.md 格式

```markdown
---
name: my-skill
description: Brief description (shown in skill search results)
version: 1.0.0
author: Your Name
license: MIT
platforms: [macos, linux]          # Optional — restrict to specific OS platforms
                                   #   Valid: macos, linux, windows
                                   #   Omit to load on all platforms (default)
required_environment_variables:    # Optional — secure setup-on-load metadata
  - name: MY_API_KEY
    prompt: API key
    help: Where to get it
    required_for: full functionality
prerequisites:                     # Optional legacy runtime requirements
  env_vars: [MY_API_KEY]           #   Backward-compatible alias for required env vars
  commands: [curl, jq]             #   Advisory only; does not hide the skill
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    fallback_for_toolsets: [web]       # Optional — show only when toolset is unavailable
    requires_toolsets: [terminal]      # Optional — show only when toolset is available
---

# Skill Title

Brief intro.

## When to Use
Trigger conditions — when should the agent load this skill?

## Prerequisites
Env vars, install steps, MCP setup, API key sourcing.

## How to Run
Canonical invocation through the `terminal` tool.

## Quick Reference
Table of common commands or API calls.

## Procedure
Step-by-step instructions the agent follows.

## Pitfalls
Known failure modes and how to handle them.

## Verification
How the agent confirms it worked.
```

### 平台专用技能

技能可通过 `platforms` 前置字段来指定其支持的操作系统平台。带有该字段的技能会在不兼容的平台上自动从系统提示、`skills_list()` 函数以及斜杠命令中隐藏。

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders)
platforms: [macos, linux]     # macOS and Linux
platforms: [windows]          # Windows only
```

如果该字段被省略或留空，则该技能将在所有平台上加载（具备向后兼容性）。有关仅适用于 macOS 的技能示例，请参见 `skills/apple/` 目录。

### 条件化技能激活

技能可以定义条件，从而根据当前会话中可用的工具及工具集来决定其在系统提示中显示的时机。这一功能主要用于**备用技能**——即仅在主工具不可用时才需显示的替代方案。

`metadata.hermes` 下支持四个字段：

```yaml
metadata:
  hermes:
    fallback_for_toolsets: [web]      # Show ONLY when these toolsets are unavailable
    requires_toolsets: [terminal]     # Show ONLY when these toolsets are available
    fallback_for_tools: [web_search]  # Show ONLY when these specific tools are unavailable
    requires_tools: [terminal]        # Show ONLY when these specific tools are available
```

**语义说明：**
- `fallback_for_*`：该技能为备用选项。当列出的工具或工具集可用时，它会被**隐藏**；而在这些工具不可用时则**显示**出来。适用于作为高级工具的免费替代方案。
- `requires_*`：该技能需要特定的工具才能正常运行。当列出的工具或工具集不可用时，它会被**隐藏**。适用于依赖特定功能的技能（例如，仅能在拥有终端访问权限时使用的技能）。
- 若同时指定了这两种语义，技能必须同时满足所有条件才会显示。
- 若未指定任何语义，则该技能将始终显示（以确保向后兼容性）。

**示例：**

```yaml
# DuckDuckGo search — shown when Firecrawl (web toolset) is unavailable
metadata:
  hermes:
    fallback_for_toolsets: [web]

# Smart home skill — only useful when terminal is available
metadata:
  hermes:
    requires_toolsets: [terminal]

# Local browser fallback — shown when Browserbase is unavailable
metadata:
  hermes:
    fallback_for_toolsets: [browser]
```

过滤操作在提示语构建阶段于 `agent/prompt_builder.py` 文件中执行。`build_skills_system_prompt()` 函数会获取代理系统中可用的工具及工具集，再通过 `_skill_should_show()` 函数来评估每个技能的启用条件。

### 技能配置元数据

技能可通过 `required_environment_variables` 前置字段声明安全性的加载时配置元数据。若该字段未设置值，不会导致技能无法被识别；而是在实际加载该技能时，仅会触发一个仅适用于命令行的安全提示语。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

用户可以跳过设置步骤，直接继续加载该技能。Hermes仅向模型暴露元数据（如`stored_as`、`skipped`、`validated`），而绝不会泄露其敏感值。原有的`prerequisites.env_vars`格式依然被支持，并已转换为新的数据格式。

```yaml
prerequisites:
  env_vars: [TENOR_API_KEY]       # Legacy alias for required_environment_variables
  commands: [curl, jq]            # Advisory CLI checks
```

网关与消息传递会话绝不会在传输过程中收集敏感信息；它们会指导用户在本地运行 `hermes setup` 命令或更新 `~/.hermes/.env` 文件。

**何时声明必需的环境变量：**
- 该技能使用了需要在加载时安全获取的 API 密钥或令牌
- 即使用户跳过设置步骤，该技能仍能正常工作，但功能可能会受限

**何时声明命令运行前提条件：**
- 该技能依赖于某些可能未安装的 CLI 工具（例如 `himalaya`、`openhue`、`ddgs`）
- 应将命令检查视为使用指南，而非在发现问题时才进行隐藏处理

相关示例可参考 `skills/gifs/gif-search/` 和 `skills/email/himalaya/` 目录。

### 技能开发标准（硬性要求）

所有新开发的或经过升级的技能——无论是内置技能、可选技能还是用户贡献的技能——在合并之前都必须符合这些标准。审核人员会拒绝违反这些标准的 Pull Request。

1. **`description` 字符数必须不超过 60 个字符，仅限一句话，且以句号结尾。** 过长的描述会导致技能列表界面显得臃肿，同时在加载大量技能时也会分散模型的注意力。应描述技能的功能，而非实现方式。禁止使用任何营销用语（如“强大”、“全面”、“无缝”、“先进”等）。不得重复技能名称。可通过以下方式进行检查：
   ```python
   import re, pathlib
   m = re.search(r'^description: (.*)$',
                 pathlib.Path('skills/<cat>/<name>/SKILL.md').read_text(),
                 re.MULTILINE)
   assert len(m.group(1)) <= 60, len(m.group(1))
   ```

良好示例：`按关键词、作者、类别或编号搜索arXiv论文。`  
不良示例：`这是一项功能强大且功能全面的技能，能够让智能体利用关键词、作者和类别等多种标准在arXiv上搜索相关的学术论文。`  

2. **SKILL.md文档中提及的工具必须是Hermes原生工具，或是该技能明确指定的MCP服务器。** 当某个技能需要某种功能时，需用反引号标明对应的工具名称，例如：`` `terminal` ``、`` `web_extract` ``、`` `web_search` ``、`` `read_file` ``、`` `write_file` ``、`` `patch` ``、`` `search_files` ``、`` `vision_analyze` ``、`` `browser_navigate` ``、`` `delegate_task` ``、`` `image_generate` ``、`` `text_to_speech` ``、`` `cronjob` ``、`` `memory` ``、`` `skill_view` ``、`` `todo` ``、`` `execute_code` ``。  

   **切勿使用智能体已封装好的shell命令作为工具名称：**  

   | 不要这样写 | 应该这样写 |
   |---|---|
   | `grep`, `rg` | `search_files` |
   | `cat`, `head`, `tail` | `read_file` |
   | `sed`, `awk` | `patch` |
   | `find`, `ls` | `search_files`（并设置`target='files'`） |
   | 用于内容提取的`curl` | `web_extract` |
   | `echo > file`, `cat <<EOF` | `write_file` |

   如果该技能依赖某个MCP服务器，需明确写出服务器名称，并在`## Prerequisites`部分说明其设置方式。第三方CLI工具（如`ffmpeg`、`gh`或特定SDK）虽可从脚本文件中调用，但描述时应说明是通过`terminal`工具来执行，而非手动启动shell会话。

3. **`platforms:` 筛选机制会根据实际脚本导入情况来进行验证。** 那些仅使用 POSIX 原语的技能（如用于检测进程存活状态的 `fcntl`、`termios`、`os.setsid`、`os.kill(pid, 0)`，以及 `/proc`、硬编码的 `/tmp` 路径、`signal.SIGKILL`、bash heredocs、`osascript`、`apt`、`systemctl` 等）必须通过 `platforms:` 前置字段明确说明其支持的平台。默认策略是首先确保该技能在多平台上都能正常运行——例如使用 `tempfile.gettempdir()`、`pathlib.Path`、`psutil.pid_exists()`，以及 Python 层级的过滤功能而非 `grep`。只有当某个依赖项确实受限于特定平台时（比如 `osascript` 仅适用于 macOS，/proc 仅适用于 Linux），才将其限制在更小的平台范围内。

4. **`author` 字段应首先标注实际贡献者。** 对于外部贡献，应首先列出贡献者的真实姓名和 GitHub 用户名（格式为“Jane Doe (jane-doe)”），“Hermes Agent”则作为次要合作者标注。如果某次提交将“Hermes Agent”列为作者，那是因为该贡献者是使用 Hermes 编写了该技能，此时应将其替换为贡献者的真实姓名——应当表彰的是人，而非工具。

5. **SKILL.md 正文需遵循现代的结构顺序。** 文档开头为 `# <Skill> Skill` 的标题，接着用 2-3 句话说明该技能的功能与限制，之后依次包含以下部分：
   - `## When to Use` — 触发条件
   - `## Prerequisites` — 环境变量、安装步骤、MCP 配置以及 API 密钥的获取方式
   - `## How to Run` — 通过 `terminal` 工具的标准调用方式
   - `## Quick Reference` — 简洁的命令/API 参考表
   - `## Procedure` — 带有可直接复制粘贴的命令的编号步骤列表
- `## 潜在问题` — 已知的限制、速率限制，以及看似异常但实际上正常的情况  
- `## 验证方法` — 用于证明该技能功能正常的单条命令  

对于复杂的技能，文档行数目标约为200行；简单技能则为100行左右。请删除冗余的引言内容、营销性文字，以及已在`## 先决条件`中说明过的环境变量相关内容。  

6. **脚本应存放在`scripts/`目录中，引用文件放在`references/`目录，模板则存放于`templates/`目录。** 不要期望模型在每次调用时都自动编写解析器、XML遍历工具或复杂的逻辑代码——应提供相应的辅助脚本。通过相对于技能目录的路径，在SKILL.md中引用这些脚本。  

7. **测试文件位于`tests/skills/test_<skill>_skill.py`，且仅允许使用标准库、pytest以及`unittest.mock`。禁止进行实时网络请求。可通过`scripts/run_tests.sh tests/skills/test_<skill>_skill.py -q`命令运行测试。该测试必须在完全隔离的CI环境中通过（不得有API密钥泄露）。对于任何依赖环境变量或文件系统的需求，可使用`monkeypatch`和`tmp_path`来解决。**  

8. **`.env.example`文件中的新增内容应被限制在明确标出的区块内。** 请勿修改该文件的其他部分——贡献者提供的`.env.example`版本通常已过时，且若在技能模块之外的区域进行修改，这些更改将在后续处理过程中被忽略。请用`#`对所有值添加注释（这只是文档内容，而非实际配置文件）。  

### 技能开发指南

- **除非绝对必要，否则不要引入外部依赖。** 建议优先使用 Python 标准库、curl 以及现有的 Hermes 工具（如 `web_extract`、`terminal`、`read_file`）。
- **逐步披露信息。** 先介绍最常用的工作流程，将边缘情况和高级用法放在最后。
- **提供辅助脚本**用于处理 XML/JSON 解析或复杂逻辑——不要指望每次都让大语言模型直接编写解析代码。
- **进行测试。** 运行 `hermes --toolsets skills -q "使用 X 技能来完成 Y"`，并确认智能体能够正确遵循指令。

---

## 添加皮肤/主题

Hermes 采用数据驱动的皮肤系统——添加新皮肤无需修改任何代码。

**选项 A：用户自定义皮肤（YAML 文件）**

创建 `~/.hermes/skins/<名称>.yaml` 文件：

```yaml
name: mytheme
description: Short description of the theme

colors:
  banner_border: "#HEX"     # Panel border color
  banner_title: "#HEX"      # Panel title color
  banner_accent: "#HEX"     # Section header color
  banner_dim: "#HEX"        # Muted/dim text color
  banner_text: "#HEX"       # Body text color
  response_border: "#HEX"   # Response box border

spinner:
  waiting_faces: ["(⚔)", "(⛨)"]
  thinking_faces: ["(⚔)", "(⌁)"]
  thinking_verbs: ["forging", "plotting"]
  wings:                     # Optional left/right decorations
    - ["⟪⚔", "⚔⟫"]

branding:
  agent_name: "My Agent"
  welcome: "Welcome message"
  response_label: " ⚔ Agent "
  prompt_symbol: "⚔"

tool_prefix: "╎"             # Tool output line prefix
```

所有字段均为可选——缺失的值将沿用默认主题。

**选项 B：内置主题**

在 `hermes_cli/skin_engine.py` 文件中的 `_BUILTIN_SKINS` 字典中添加该主题。其结构与上文相同，但需以 Python 字典的形式呈现。内置主题随软件包一同提供，始终可用。

**启用方式：**
- 命令行：`/skin mytheme`，或在 config.yaml 中设置 `display.skin: mytheme`
- 配置文件：`display: { skin: mytheme }`

如需查看完整的结构定义及现有主题示例，请参阅 `hermes_cli/skin_engine.py`。

---

## 跨平台兼容性

Hermes 支持在 Linux、macOS 以及原生 Windows 系统（包括 WSL2）上运行。在编写涉及操作系统的代码时，应假设*任何*平台都可能触发您的代码逻辑。

> **在提交 Pull Request 之前：**请运行 `scripts/check-windows-footguns.py`，以检查您的代码差异中是否存在常见的 Windows 不安全模式。该工具基于 grep 实现，运行速度很快；CI 系统也会在每个 PR 上自动执行此检查。

### 关键规则

1. **切勿使用 `os.kill(pid, 0)` 来进行进程存活检测。** `os.kill(pid, 0)` 是 POSIX 标准中用于判断“该 PID 是否存活”的常用方法——信号值 0 仅用于执行无实际作用的权限检查。**但在 Windows 系统上，这一操作并非无作用。** Python 在 Windows 平台上的 `os.kill` 函数会将 `sig=0` 转换为 `CTRL_C_EVENT`（因为两者的整数值均为 0），并通过 `GenerateConsoleCtrlEvent(0, pid)` 发送信号，从而将 Ctrl+C 传递给包含目标 PID 的**整个控制台进程组**。这样一来，“检测进程是否存活”的操作实际上会悄悄“杀死目标进程以及与其共享同一控制台的许多无关进程”。相关问题可参见 [bpo-14484](https://bugs.python.org/issue14484)（该问题自 2012 年提出，由于兼容性原因将永远无法修复）。

   **推荐做法：** 使用 `psutil` 库（其为核心依赖项，始终可用）。

   ```python
   import psutil
   if psutil.pid_exists(pid):
       # process is alive — safe on every platform
       ...
   ```

如果您确实需要使用 Hermes 封装层（它在 `pip install` 完成之前，会为架构搭建阶段的导入提供标准库兜底方案），可以调用 `gateway.status._pid_exists(pid)`。该函数会首先尝试使用 `psutil.pid_exists`，只有在 `psutil` 无法正常使用时，才会仅在 Windows 系统上采用手动实现的 `OpenProcess + WaitForSingleObject` 方法。

若要查找新增的调用位置，可使用 Audit grep 命令：`rg "os\.kill\([^,]+,\s*0\s*\)"`。如果在非测试代码中检测到此类调用，很可能是 Windows 系统的静默终止功能存在缺陷。

2. **在调用外部命令之前，请先使用 `shutil.which()` 检查工具是否存在——切勿默认 Windows 拥有 Linux 所有的工具。** `wmic` 已在 Windows 10 21H1 及更高版本中被移除。而 `ps`、`kill`、`grep`、`awk`、`fuser`、`lsof`、`pgrep` 以及大多数 POSIX 风格的 CLI 工具在 Windows 上根本不存在。建议通过 `shutil.which("tool")` 来检测这些工具的可用性，若无法找到，则需改用 Windows 原生的替代工具——通常是通过 `subprocess.run(["powershell", "-NoProfile", "-Command", ...])` 调用 PowerShell。

至于进程枚举功能，PowerShell 的 `Get-CimInstance Win32_Process` 已成为 `wmic process` 的现代替代方案。具体实现方式可参考 `hermes_cli/gateway.py::_scan_gateway_pids` 文件中的代码逻辑。
   ```

3. **File encoding.** Windows may save `.env` files in `cp1252`. Always
   handle encoding errors:
   ```python
   try:
       load_dotenv(env_path)
   except UnicodeDecodeError:
       load_dotenv(env_path, encoding="latin-1")
   ```
记事本及类似编辑器在保存配置文件（`config.yaml`）时可能会添加 UTF-8 BOM 标记；若要读取可能经过 Windows 图形界面编辑器处理过的文件，请使用 `encoding="utf-8-sig"` 参数。

4. **进程管理。** `os.setsid()`、`os.killpg()`、`os.fork()`、`os.getuid()` 以及 POSIX 信号处理机制在 Windows 系统上有所不同。建议通过 `platform.system()`、`sys.platform` 或 `hasattr(os, "setsid")` 来进行兼容性判断。
   ```python
   if platform.system() != "Windows":
       kwargs["preexec_fn"] = os.setsid
   else:
       kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
   ```

**推荐方案：** 若需终止某个进程及其所有子进程（即 POSIX 系统中 `os.killpg` 的功能），请使用 `psutil`——它可在所有平台上正常运行。
   ```python
   import psutil
   try:
       parent = psutil.Process(pid)
       # Kill children first (leaf-up), then the parent.
       for child in parent.children(recursive=True):
           child.kill()
       parent.kill()
   except psutil.NoSuchProcess:
       pass
   ```

5. **Windows 系统中不存在的信号：`SIGALRM`、`SIGCHLD`、`SIGHUP`、`SIGUSR1`、`SIGUSR2`、`SIGPIPE`、`SIGQUIT`、`SIGKILL`。**如果在 Windows 上尝试使用这些信号，Python 的 `signal` 模块会在导入时抛出 `AttributeError` 异常。建议使用 `getattr(signal, "SIGKILL", signal.SIGTERM)` 方法，或通过平台检测来屏蔽相关代码块。在 Windows 上，`loop.add_signal_handler` 会引发 `NotImplementedError` 异常，务必对其进行捕获处理。

6. **路径分隔符。**应使用 `pathlib.Path` 对象而非字符串拼接并使用 `/` 符号来构建路径。虽然正斜杠在 Windows 上几乎处处可用，但 `subprocess.run(["cmd.exe", "/c", ...])` 以及其他涉及命令行的场景可能要求使用反斜杠——因此应在调用子进程之前通过 `str(path)` 进行转换，而非在 Python 逻辑内部处理。

7. **在 Windows 上创建符号链接需要提升权限**（除非开启了开发者模式）。那些涉及创建符号链接的测试应添加标记 `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")`，以便在 Windows 环境中自动跳过。

8. **默认情况下，NTFS 文件系统并不支持 POSIX 文件权限模式（如 0o600、0o644 等）。**那些依赖 `stat().st_mode & 0o777` 来进行断言的测试在 Windows 上必须被跳过，因为该概念在此系统中并不适用。如有必要，可利用 ACL（如 `icacls`、`pywin32` 库）来实现 Windows 系统下敏感文件的保护。

9. **在 Windows 系统上，以分离模式运行的后台守护进程需要使用 `pythonw.exe`，而非 `python.exe`。** `python.exe` 总是会绑定到控制台，因此容易受到任何关联进程发送的 `CTRL_C_EVENT` 信号的影响。而 `pythonw.exe` 是无需控制台的版本。可在 `subprocess.Popen(creationflags=...)` 中结合使用 `CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB` 这些标志。相关实现参考代码位于 `hermes_cli/gateway_windows.py::_spawn_detached`。

10. **当使用 `.cmd` 或 `.bat` 形式的脚本通过 `subprocess.Popen` 调用时，需要借助 `shutil.which` 函数来定位正确的执行文件。** 在 Windows 上，若将 `"agent-browser"` 传递给 `Popen`，系统会在 `node_modules/.bin/` 目录中查找没有扩展名的 POSIX 命令行脚本，而 `CreateProcessW` 无法执行此类脚本，从而导致“WinError 193 ‘不是有效的 Win32 应用程序’”的错误。应使用 `shutil.which("agent-browser", path=local_bin)`，该函数会考虑系统的 PATH 环境变量，并在 Windows 上自动选择 `.CMD` 格式的脚本。

11. **请勿通过 shell 命令行脚本的方式来运行 Python。** `#!/usr/bin/env python` 这种写法仅能在通过 Unix shell 执行文件时生效。即使在脚本中包含了 shebang 行，Windows 系统上的 `subprocess.run(["./myscript.py"])` 也会失败。应始终明确指定 Python 的执行路径，即使用 `[sys.executable, "myscript.py"]` 这种形式。

12. **安装程序中的 Shell 命令。** 如果您修改了 `scripts/install.sh`，则必须在 `scripts/install.ps1` 中进行相应的修改。这两个脚本是“在 Linux 上能运行并不代表在 Windows 上也能运行”这一现象的典型例证，且其内容曾多次出现不一致——请务必保持二者同步。

13. **Windows 系统中会被 OneDrive 重定向的已知路径：** 桌面、文档、图片、视频。启用 OneDrive 备份后，这些路径的“真实”位置为 `%USERPROFILE%\OneDrive\Desktop`（及其他类似路径），而非 `%USERPROFILE%\Desktop`（该路径实际上是一个空目录）。可通过 `ctypes` + `SHGetKnownFolderPath` 或读取 `Shell Folders` 注册表项来确定真实路径——切勿直接假设使用 `~/Desktop`。

14. **生成的脚本中 CRLF 与 LF 的区别。** Windows 的 `cmd.exe` 和 `schtasks` 命令都是逐行解析的；混合使用或仅包含 LF 结尾的行可能导致多行格式的 `.cmd`/`.bat` 文件出错。在生成供 Windows 执行的脚本时，应使用 `open(path, "w", encoding="utf-8", newline="\r\n")`——或者使用 `open(path, "wb")` 并手动指定字节序列——切勿随意选择编码方式。

15. **单条命令行中使用的两种不同引号规则。** 在 `subprocess.run(["schtasks", "/TR", some_cmd])` 这种用法中，`/TR` 会被 schtasks 自身解析，而 `some_cmd` 字符串则会在任务执行时由 `cmd.exe` 再次解析。由于解析器不同，其转义规则也有所差异。因此应分别使用两种引号处理函数，且严禁混用。可参考 `hermes_cli/gateway_windows.py` 文件中的 `_quote_cmd_script_arg` 和 `_quote_schtasks_arg` 函数作为实现示例。

### 跨平台测试

需要在特定平台上测试其行为表现的测试，必须在其目标平台上执行。

```python
@pytest.mark.linux_only
@pytest.mark.macos_only
@pytest.mark.windows_only
```
除非确实必要，否则应避免直接修改 `sys.platform`，若必须如此，也请同时修改 `platform.system()`、`platform.release()` 和 `platform.mac_ver()`。符号链接、0o600 权限设置、SIGALRM 信号以及 os.setsid/fork 函数均为 Unix 系统所独有。

---

## 安全注意事项

Hermes 具有终端访问权限，因此安全问题至关重要。

### 现有的防护措施

| 防护层级 | 实现方式 |
|---------|----------|
| **Sudo 密码传递** | 使用 `shlex.quote()` 函数防止shell注入攻击 |
| **危险命令检测** | 通过 `tools/approval.py` 中的正则表达式模式实现用户审批流程 |
| **Cron 脚本注入防护** | `tools/cronjob_tools.py` 中的扫描工具可拦截试图覆盖指令的模式 |
| **写入禁止列表** | 对受保护路径（如 `~/.ssh/authorized_keys`、`/etc/shadow`）使用 `os.path.realpath()` 获取真实路径，从而防止通过符号链接绕过限制 |
| **技能模块防护** | 通过 `tools/skills_guard.py` 对 hub 安装的技能模块进行安全扫描 |
| **代码执行沙箱** | `execute_code` 子进程在运行时会被移除环境变量中的 API 密钥 |
| **容器加固** | Docker 环境下会禁用所有特殊权限、防止权限提升，同时设置 PID 限制及限制临时文件系统的大小 |

### 贡献涉及安全敏感的代码时的注意事项

- 在将用户输入嵌入Shell命令时，**务必使用 `shlex.quote()`** 进行处理。  
- 在执行基于路径的访问控制检查之前，**使用 `os.path.realpath()` 解析符号链接**。  
- **切勿记录敏感信息**。API密钥、令牌和密码绝不能出现在日志输出中。  
- 在工具执行过程中需**捕获通用异常**，以避免单次失败导致整个代理循环崩溃。  
- 若您的修改涉及文件路径、进程管理或Shell命令，**必须在所有平台上进行测试**。  

如果您的拉取请求会影响安全性，请在描述中明确说明。  

### 依赖项锁定策略（供应链加固）

鉴于2026年3月发生的 [litellm供应链入侵事件](https://github.com/BerriAI/litellm/issues/24512)以及2026年5月出现的 [Mini Shai-Hulud蠕虫攻击](https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack)，所有依赖项都必须遵守以下规则：

| 来源类型 | 所需处理方式 | 原因说明 |
|---|---|---|
| **PyPI 包** | `>=floor,<next_major` | PyPI 上的版本一旦发布即不可更改，但可在指定范围内推送新版本。设置 `<next_major` 的上限可防止 1.x 版本升级为恶意的 2.0.0 版本。 |
| **Git URL**（如 atroposlib、tinker、yc-bench、Baileys） | 完整的提交 SHA 值 | 分支和标签属于可变的引用；而 SHA 值采用内容寻址机制。 |
| **GitHub Actions** | 完整的提交 SHA 值 + 版本说明 | Action 标签属于可变引用（例如 `tj-actions/changed-files March 2025`）。应通过 `uses: owner/action@<sha>  # vX.Y.Z` 的形式进行固定版本指定。 |
| **仅用于 CI 的 pip 安装** | `==exact` | 由于是在 Hermetic CI 环境中构建，允许版本存在变动。 |

**在 PR 中新增的每一个 PyPI 依赖都必须设置 `<next_major` 的上限。** 若提交的内容包含无限制的 `>=X.Y.Z` 版本指定，将会被审阅者拒绝。`supply-chain-audit.yml` CI 工作流还会标记依赖清单的变更，以便人工审核。

**如何确定上限值：**
- 如果包的版本为 `1.x.y`，则使用 `<2`。
- 如果包的版本为 `0.x.y`（1.0 之前的版本），则使用 `<0.(当前次要版本号 + 2)`——例如当前版本为 `0.29.x`，则使用 `<0.32`。这样既能保留约 2 个次要版本的缓冲空间，又能确保范围足够小，从而降低恶意版本混入的可能性。
- 特例：对于 API 非常稳定的包（如 `aiohttp-socks`），经审阅者判断后可使用 `<1`。

**示例：**
```toml
# ✅ Correct — post-1.0
"openai>=2.21.0,<3"
"pydantic>=2.12.5,<3"

# ✅ Correct — pre-1.0 (tight minor window)
"asyncpg>=0.29,<0.32"
"aiosqlite>=0.20,<0.23"
"hindsight-client>=0.4.22,<0.5"

# ❌ Rejected — no upper bound
"some-package>=1.2.3"

# ❌ Rejected — too tight (blocks legitimate patches)
"some-package==1.2.3"

# ❌ Rejected — too loose for pre-1.0 (allows 80 minor versions)
"some-package>=0.20,<1"
```

**相关 PR 号码：** #2796（移除 litellm）、#2810（上界检查机制）、#9801（SHA 值锁定与供应链审计持续集成流程）。

---

## Pull Request 提交流程

### 分支命名规则

```
fix/description        # Bug fixes
feat/description       # New features
docs/description       # Documentation
test/description       # Tests
refactor/description   # Code restructuring
```

### 提交前准备

1. **运行测试**：使用 `scripts/run_tests.sh`（推荐，与 CI 流水线相同）；或在激活项目虚拟环境后执行 `pytest tests/ -v`。
2. **手动测试**：启动 `hermes` 并调用你修改过的代码路径进行测试。
3. **检查跨平台兼容性**：如果你修改了文件读写、进程管理或终端处理相关功能，需确保其在 macOS、Linux 和 WSL2 环境下都能正常运行。
4. **保持 PR 的聚焦性**：每个 PR 应只包含一个逻辑上的更改。避免将错误修复、代码重构和新功能混在一起。

### PR 描述内容

需包含以下信息：
- **具体修改了什么**以及**原因**
- **如何测试该更改**（错误的复现步骤，功能的用法示例）
- **已在哪些平台上进行测试**
- 引用任何相关的 Issue

### 提交信息格式

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 标准来编写提交信息：

```
<type>(<scope>): <description>
```

| 类型 | 用途 |
|------|------|
| `fix` | 错误修复 |
| `feat` | 新功能开发 |
| `docs` | 文档编写 |
| `test` | 测试相关任务 |
| `refactor` | 代码重构（不改变功能行为） |
| `chore` | 构建、持续集成及依赖项更新 |

作用范围：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security` 等。

示例：
```
fix(cli): prevent crash in save_config_value when model is a string
feat(gateway): add WhatsApp multi-user session isolation
fix(security): prevent shell injection in sudo password piping
test(tools): add unit tests for file_operations
```

---

## 报告问题

- 请使用 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues) 提交问题
- 需提供以下信息：操作系统、Python版本、Hermes版本（通过 `hermes --version` 查看）、完整的错误堆栈信息
- 同时需附上问题复现步骤
- 在提交新问题前请先查看现有问题，避免重复提交
- 若发现安全漏洞，请通过私密渠道进行报告

---

## 社区交流

- **Discord**：[discord.gg/NousResearch](https://discord.gg/NousResearch) —— 用于提问、展示项目成果及分享技能
- **GitHub Discussions**：用于讨论设计方案与架构相关内容
- **Skills Hub**：可将自定义技能上传至注册表，并与社区成员共享

---

## 许可协议

通过贡献代码，即表示您同意您的贡献将依据 [MIT许可证](LICENSE) 进行授权。
