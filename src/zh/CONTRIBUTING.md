# 为 Hermes Agent 做贡献

感谢您为 Hermes Agent 出力！本指南涵盖了您所需的一切内容：开发环境搭建、架构理解、功能开发决策以及如何让您的 Pull Request 被合并。

---

## 贡献优先级

我们按照以下顺序重视各类贡献：

1. **错误修复** — 程序崩溃、异常行为、数据丢失等问题。始终是最高优先级。
2. **跨平台兼容性** — macOS、不同 Linux 发行版以及 Windows 上的 WSL2。我们希望 Hermes 能在所有平台上正常运行。
3. **安全性强化** — shell 注入、命令提示符注入、路径遍历、权限提升等问题。详情请参阅[安全考虑事项](#security-considerations)。
4. **性能与稳定性** — 重试逻辑、错误处理机制以及优雅降级功能。
5. **新技能开发** — 但仅限具有广泛实用价值的技能。详情请参阅[应该是技能还是工具？](#should-it-be-a-skill-or-a-tool)。
6. **新工具开发** — 很少有需求。大多数功能应以技能的形式实现，具体内容见下文。
7. **文档完善** — 错误修正、内容澄清以及新增示例。

---

## 开始之前：先进行搜索

在开始编写代码之前先快速搜索一下，既能节省您的时间，也能保持 Pull Request 队列的整洁——此类问题中重复提交的情况很常见，因此花一分钟提前排查是值得的。

- 对与您要解决的问题或错误现象相关的**已开放和已合并的 Pull Request 与问题记录**进行搜索——Pull Request 模板中的重复内容检测功能会在代码审核阶段才触发，到那时您可能已经浪费了时间。
  ```bash
  gh search issues --repo NousResearch/hermes-agent "<your terms>"
  gh search prs --repo NousResearch/hermes-agent --state all "<your terms>"
  ```
或者使用网页界面：[issues](https://github.com/NousResearch/hermes-agent/issues?q=) · [PRs（所有状态）](https://github.com/NousResearch/hermes-agent/pulls?q=is%3Apr)。  
- **问题追踪系统可能会落后于代码更新。** 许多用户请求的功能早已在代码中实现，因此在提出新需求前，建议先通过源码搜索（如 `search_files` 或编辑器自带的 grep 功能）确认该功能是否已存在。  
- **如果已有开放的 PR 正在处理该问题**，建议优先查看或改进现有 PR，而非重复提交新的 PR。  
- **对于规模较大的任务**，可在对应 issue 下留言说明你正在处理该问题，以免他人重复开展工作。  

相关内容：#38284 涉及了 Agent 端的类似机制——Hermes 会在尝试深度自我排查之前，先检查现有的 issue 和 PR。本部分则是为人工贡献者补充的说明。  

---

## 应该将其设计为技能还是工具？

这是新贡献者最常遇到的问题。答案几乎总是**技能**。  

### 何时将其设为技能：  
- 该功能可通过指令、Shell 命令及现有工具来实现；  
- 它封装了外部 CLI 或 API，Agent 可通过 `terminal` 或 `web_extract` 调用这些接口；  
- 无需在 Agent 中集成自定义 Python 代码或管理 API 密钥；  
- **示例**：arXiv 搜索、Git 工作流、Docker 管理、PDF 处理、通过 CLI 工具发送邮件等。  

### 何时将其设为工具：  
- 需要与 API 密钥、认证流程或由 Agent 管理的多组件配置进行端到端集成；  
- 需要每次都精确执行的自定义处理逻辑（而非依赖 LLM 的“尽力而为”解读）；  
- 需要处理二进制数据、流式数据或无法通过终端传输的实时事件；  
- **示例**：浏览器自动化（Browserbase 会话管理）、文本转语音（音频编码及平台推送）、视觉分析（base64 图像处理）等。  

### 技能是否需要打包？  
打包在 `skills/` 目录中的技能会随每个 Hermes 安装包一同提供。这类技能应**对大多数用户都有广泛用途**，例如文档处理、网络研究、常见开发工作流、系统管理等功能，并且会被大量用户频繁使用。  

如果你的技能虽已正式开发且实用，但并非所有人都需要（比如某些付费服务集成或依赖重型库的功能），可将其放入 **`optional-skills/`** 目录——该目录中的技能会随仓库一起提供，但默认不会被激活。用户可通过 `hermes skills browse` 查看这些“官方”技能，并使用 `hermes skills install` 安装（无需担心第三方依赖问题，因其具有内置信任度）。  

如果你的技能属于专业领域、由社区贡献或针对特定场景设计，更适合放在**技能中心**——将其上传到技能注册表，并在 [Nous Research Discord](https://discord.gg/NousResearch) 中分享。用户同样可通过 `hermes skills install` 安装此类技能。  

---

## 内存提供器：应以独立插件形式发布  

**我们不再接受新的内存提供器加入此仓库。** `plugins/memory/` 目录下已有的内置提供器（honcho、mem0、supermemory、byterover、hindsight、holographic、openviking、retaindb）已停止接收新功能。如果你想添加新的内存后端，应将其作为**独立插件仓库**发布，供用户安装到 `~/.hermes/plugins/` 目录中（或通过 pip 安装）。  

独立内存插件需满足以下要求：  
- 实现相同的 `MemoryProvider` ABC 接口（位于 `agent/memory_provider.py` 文件中），包括 `sync_turn`、`prefetch`、`shutdown` 方法，还可根据需要实现 `post_setup(hermes_home, config)` 方法以支持设置向导集成；  
- 使用相同的发现机制——`discover_memory_providers()` 函数会从用户/项目插件目录及 pip 安装路径中识别这些插件；  
- 通过 `post_setup()` 方法与 `hermes memory setup` 功能集成，无需修改核心代码；  
- 可在 `cli.py` 文件中使用 `register_cli(subparser)` 方法注册自己的 CLI 子命令；  
- 可享有与内置提供器相同的生命周期钩子和配置管理功能。  

对于试图在 `plugins/memory/` 下创建新目录的 PR，我们将予以拒绝，并提示用户将相关提供器作为独立仓库发布。现有的内置提供器将继续保留，对其的错误修复依然欢迎。  

这并非质量标准问题，而是出于耦合度控制和维护效率的考虑。内存提供器是最常见的插件类型，不应全部集中存放于此目录中。  

---

## 开发环境配置  

### 先决条件  

| 需求项 | 说明 |
|--------|------|
| **Git** | 需安装 `git-lfs` 扩展功能 |
| **Python 3.11+** | 若未安装，uv 工具会自动帮你安装 |
| **uv** | 快速的 Python 包管理工具（[安装指南](https://docs.astral.sh/uv/)） |
| **Node.js 20+** | 可选——用于浏览器工具及 WhatsApp 桥接功能（需与项目根目录的 `package.json` 中指定的引擎版本一致） |

### 使用标准安装程序进行配置  

对于大多数贡献者而言，最简便的开发环境搭建方式就是遵循普通用户的操作流程：运行标准安装程序，然后在克隆的仓库目录中进行开发。安装程序会创建 Hermes 虚拟环境，配置 `hermes` 命令入口，设定 `hermes update` 的更新机制，并将完整的 Git 项目克隆到 `$HERMES_HOME/hermes-agent` 目录中（通常为 `~/.hermes/hermes-agent`）。这样一来，你的开发环境布局就会与 CLI 工具、更新程序、延迟依赖安装器、网关及文档所期望的格式保持一致。

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
cd "${HERMES_HOME:-$HOME/.hermes}/hermes-agent"

# Add dev/test extras on top of the standard install.
uv pip install -e ".[all,dev]"

# Optional: browser tools / docs site dependencies.
npm install
```

之后，创建分支，并在该分支上运行测试：

```bash
git checkout -b fix/description
scripts/run_tests.sh
```

### 手动克隆回退方案

仅当您明确不想使用 Hermes 的托管安装结构时才应采用此方法（例如在容器或 CI 任务中使用的临时克隆项目）。若选择这种方式进行安装，请务必从该虚拟环境内运行 `hermes` 入口程序；否则，直接使用系统命令 `python3 -m hermes_cli.main` 可能会引入无关的系统 Python 包。

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# Create venv with Python 3.11
uv venv venv --python 3.11
export VIRTUAL_ENV="$(pwd)/venv"

# Install with all extras (messaging, cron, CLI menus, dev tools)
uv pip install -e ".[all,dev]"

# Optional: browser tools
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

如果您使用了手动克隆的备用方案，请从代码检出目录运行 `./hermes`，或明确地创建该克隆版本的虚拟环境链接：

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
```

### 运行测试

```bash
# Preferred — matches CI (hermetic env, 4 xdist workers); see AGENTS.md
scripts/run_tests.sh

# Alternative (activate the venv first). The wrapper is still recommended
# for parity with GitHub Actions before you open a PR:
pytest tests/ -v
```

## 项目结构

```
hermes-agent/
├── run_agent.py              # AIAgent class — core conversation loop, tool dispatch, session persistence
├── cli.py                    # HermesCLI class — interactive TUI, prompt_toolkit integration
├── model_tools.py            # Tool orchestration (thin layer over tools/registry.py)
├── toolsets.py               # Tool groupings and presets (hermes-cli, hermes-telegram, etc.)
├── hermes_state.py           # SQLite session database with FTS5 full-text search, session titles
├── batch_runner.py           # Parallel batch processing for trajectory generation
│
├── agent/                    # Agent internals (extracted modules)
│   ├── prompt_builder.py         # System prompt assembly (identity, skills, context files, memory)
│   ├── context_compressor.py     # Auto-summarization when approaching context limits
│   ├── auxiliary_client.py       # Resolves auxiliary OpenAI clients (summarization, vision)
│   ├── display.py                # KawaiiSpinner, tool progress formatting
│   ├── model_metadata.py         # Model context lengths, token estimation
│   └── trajectory.py             # Trajectory saving helpers
│
├── hermes_cli/               # CLI command implementations
│   ├── main.py                   # Entry point, argument parsing, command dispatch
│   ├── config.py                 # Config management, migration, env var definitions
│   ├── setup.py                  # Interactive setup wizard
│   ├── auth.py                   # Provider resolution, OAuth, Nous Portal
│   ├── models.py                 # OpenRouter model selection lists
│   ├── banner.py                 # Welcome banner, ASCII art
│   ├── commands.py               # Central slash command registry (CommandDef), autocomplete, gateway helpers
│   ├── callbacks.py              # Interactive callbacks (clarify, sudo, approval)
│   ├── doctor.py                 # Diagnostics
│   ├── skills_hub.py             # Skills Hub CLI + /skills slash command
│   └── skin_engine.py            # Skin/theme engine — data-driven CLI visual customization
│
├── tools/                    # Tool implementations (self-registering)
│   ├── registry.py               # Central tool registry (schemas, handlers, dispatch)
│   ├── approval.py               # Dangerous command detection + per-session approval
│   ├── terminal_tool.py          # Terminal orchestration (sudo, env lifecycle, backends)
│   ├── file_operations.py        # read_file, write_file, search, patch, etc.
│   ├── web_tools.py              # web_search, web_extract (Parallel/Firecrawl + Gemini summarization)
│   ├── vision_tools.py           # Image analysis via multimodal models
│   ├── delegate_tool.py          # Subagent spawning and parallel task execution
│   ├── code_execution_tool.py    # Sandboxed Python with RPC tool access
│   ├── session_search_tool.py    # Search past conversations with FTS5 + anchored windows
│   ├── cronjob_tools.py          # Scheduled task management
│   ├── skill_tools.py            # Skill search, load, manage
│   └── environments/             # Terminal execution backends
│       ├── base.py                   # BaseEnvironment ABC
│       ├── local.py, docker.py, ssh.py, singularity.py, modal.py, daytona.py
│
├── gateway/                  # Messaging gateway
│   ├── run.py                    # GatewayRunner — platform lifecycle, message routing, cron
│   ├── config.py                 # Platform configuration resolution
│   ├── session.py                # Session store, context prompts, reset policies
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
| `~/.hermes/config.yaml` | 设置选项（模型、终端、工具集、压缩功能等） |
| `~/.hermes/.env` | API 密钥与敏感信息 |
| `~/.hermes/auth.json` | OAuth 认证凭证（Nous Portal 使用） |
| `~/.hermes/skills/` | 所有已激活的技能（包括打包内置的、通过 Hub 安装的以及由 Agent 创建的技能） |
| `~/.hermes/memories/` | 持久化记忆内容（MEMORY.md、USER.md 文件） |
| `~/.hermes/state.db` | SQLite 会话数据库 |
| `~/.hermes/sessions/` | 网关路由索引（`sessions.json`）、请求日志追踪信息、网关生成的 `*.jsonl` 转录文件；若设置了 `sessions.write_json_snapshots: true`，还可包含每个会话的 JSON 快照。默认情况下不会生成会话级快照，状态数据以 state.db 为准。 |
| `~/.hermes/cron/` | 定时任务相关数据 |
| `~/.hermes/whatsapp/session/` | WhatsApp 桥接服务的认证凭证 |

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

- **自动注册工具**：每个工具文件在导入时会调用 `registry.register()` 函数。`model_tools.py` 通过导入所有工具模块来触发发现流程。
- **工具集分组**：工具会被归类到不同的工具集中（如 `web`、`terminal`、`file`、`browser` 等），并且可以根据不同平台启用或禁用这些工具集。
- **会话持久化**：所有对话内容都存储在 SQLite 数据库中（由 `hermes_state.py` 负责管理），支持全文搜索，并为每个会话设置唯一标题。原本存在于 `~/.hermes/sessions/` 目录中的会话级 JSON 快照已被 SQLite 存储方式取代，默认处于关闭状态；如果您的外部工具需要直接读取这些 JSON 文件，可通过设置 `sessions.write_json_snapshots: true` 来重新启用该功能。
- **临时注入机制**：系统提示和预填信息会在 API 调用时动态注入，不会被保存到数据库或日志中。
- **提供者抽象层**：该智能体可适配任何兼容 OpenAI 的 API。提供者的识别工作会在初始化阶段完成，支持通过 Nous Portal OAuth、OpenRouter API 密钥或自定义端点进行配置。
- **提供者路由机制**：在使用 OpenRouter 时，可通过 `config.yaml` 中的 `provider_routing` 参数来控制提供者的选择方式（例如按吞吐量/延迟/价格排序、允许或忽略特定提供者、设定数据保留策略）。这些配置会以 `extra_body.provider` 的形式嵌入到 API 请求中。

---

## 代码风格规范

- 遵循 **PEP 8** 标准，但部分实际情况可适当放宽限制（我们不强制要求严格的行长度限制）。
- **注释**：仅用于解释那些不显而易见的逻辑意图、设计权衡或 API 的特殊行为。无需对代码的功能进行冗余描述——例如 `# 增加计数器` 这类注释毫无意义。
- **错误处理**：应捕获特定的异常，并使用 `logger.warning()`/`logger.error()` 进行日志记录；对于意外错误，需设置 `exc_info=True` 以确保日志中能显示完整的堆栈跟踪信息。
- **跨平台兼容性**：切勿假设代码仅在 Unix 系统上运行。更多相关内容请参阅 [跨平台兼容性](#cross-platform-compatibility) 部分。

---

## 添加新工具

在编写新工具之前，请先思考：[这是否更适合被定义为技能而非工具？](#should-it-be-a-skill-or-a-tool)

工具会自动向中央注册表进行注册。每个工具文件都会将自身的结构定义、处理逻辑以及注册信息集中存放在一起。

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

您仍需将工具名称添加到 `toolsets.py` 中对应的列表中（例如 `_HERMES_CORE_TOOLS` 或专门的工具集）；否则该工具虽然会注册，但不会向智能体暴露。如果您要创建新的工具集，请在 `toolsets.py` 中添加它，并将其连接到相关的平台预设中。

有关基于配置文件的路径选择以及插件与核心组件的使用指南，请参阅 `AGENTS.md` 文档中的“添加新工具”部分。

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

技能可通过 `platforms` 前置字段来指定其支持的操作系统平台。包含该字段的技能会在不兼容的平台上自动从系统提示、`skills_list()` 函数以及斜杠命令中隐藏。

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders)
platforms: [macos, linux]     # macOS and Linux
platforms: [windows]          # Windows only
```

如果该字段被省略或留空，则该技能将在所有平台上加载（具备向后兼容性）。有关仅适用于 macOS 的技能示例，请参阅 `skills/apple/` 目录。

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
- 如果同时指定了这两种语义，技能才会在该两种条件均满足时显示。
- 如果未指定任何语义，则该技能将始终显示（保持向后兼容性）。

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

过滤操作在提示语构建阶段于 `agent/prompt_builder.py` 文件中执行。`build_skills_system_prompt()` 函数会获取代理提供的所有可用工具及工具集，进而通过 `_skill_should_show()` 函数来评估每个技能的显示条件。

### 技能配置元数据

技能可通过 `required_environment_variables` 前置字段声明安全的加载时配置元数据。若该字段未设置值，不会导致技能无法被识别；而是在实际加载该技能时，仅会触发针对命令行界面的安全提示语。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

用户可以跳过设置步骤，直接继续加载该技能。Hermes仅向模型暴露元数据（如`stored_as`、`skipped`、`validated`），而绝不会泄露其密钥值。原有的`prerequisites.env_vars`格式依然被支持，并已转换为新的表示形式。

```yaml
prerequisites:
  env_vars: [TENOR_API_KEY]       # Legacy alias for required_environment_variables
  commands: [curl, jq]            # Advisory CLI checks
```

网关与消息传递会话绝不会在传输过程中收集敏感信息；它们会指导用户在本地运行 `hermes setup` 命令或更新 `~/.hermes/.env` 文件。

**何时声明必需的环境变量：**
- 该技能使用了需要在加载时安全获取的 API 密钥或令牌
- 即使用户跳过设置步骤，该技能仍能正常使用，但功能可能会略有下降

**何时声明命令运行前提条件：**
- 该技能依赖于某些可能尚未安装的 CLI 工具（例如 `himalaya`、`openhue`、`ddgs`）
- 应将命令检查视为参考建议，而非在发现问题时才进行隐藏处理

可参考 `skills/gifs/gif-search/` 和 `skills/email/himalaya/` 中的示例。

### 技能开发标准（硬性要求）

所有新开发的或经过升级的技能——无论是内置技能、可选技能还是用户贡献的技能——在合并之前都必须符合这些标准。审核人员会拒绝违反这些标准的提交请求。

1. **`description` 字符数不得超过 60 个，需为单句结构，并以句号结尾。** 过长的描述会导致技能列表界面显得臃肿，且在加载大量技能时也会分散模型的注意力。应描述技能的功能，而非实现方式。禁止使用任何营销用语（如“强大”、“全面”、“无缝”、“先进”）。同时不得重复技能名称。可通过以下方式进行检查：
   ```python
   import re, pathlib
   m = re.search(r'^description: (.*)$',
                 pathlib.Path('skills/<cat>/<name>/SKILL.md').read_text(),
                 re.MULTILINE)
   assert len(m.group(1)) <= 60, len(m.group(1))
   ```

良好示例：`按关键词、作者、分类或编号搜索arXiv论文。`  
较差示例：`这是一项功能强大且功能全面的技能，能够让智能体利用关键词、作者和分类等多种标准在arXiv上搜索相关的学术论文。`

2. **SKILL.md正文中提及的工具必须是Hermes原生工具，或是该技能明确指定的MCP服务器。** 当技能需要某种功能时，需用反引号标明对应的工具名称：`` `terminal` ``, `` `web_extract` ``, `` `web_search` ``, `` `read_file` ``, `` `write_file` ``, `` `patch` `", `` `search_files` `", `` `vision_analyze` `", `` `browser_navigate` `", `` `delegate_task` `", `` `image_generate` `", `` `text_to_speech` `", `` `cronjob` `", `` `memory` `", `` `skill_view` `", `` `todo` `", `` `execute_code` ``。

   禁止使用智能体已封装好的Shell工具名称：

   | 不要这样写 | 应该这样写 |
   |---|---|
   | `grep`, `rg` | `search_files` |
   | `cat`, `head`, `tail` | `read_file` |
   | `sed`, `awk` | `patch` |
   | `find`, `ls` | `search_files`（并设置`target='files'`） |
   | 用于内容提取的`curl` | `web_extract` |
   | `echo > file`, `cat <<EOF` | `write_file` |

   如果技能依赖于某个MCP服务器，需明确写出该服务器名称，并在`## Prerequisites`部分说明其设置方式。第三方CLI工具（如`ffmpeg`、`gh`或特定SDK）虽可从脚本文件中调用，但描述时应说明是通过`terminal`工具来执行，而非手动启动Shell会话。

3. **`platforms:`限制会根据实际导入的脚本进行校验。** 使用仅支持POSIX系统的原生函数（如`fcntl`、`termios`、`os.setsid`、用于检测存活状态的`os.kill(pid, 0)`、`/proc`目录、硬编码的`/tmp`路径、`signal.SIGKILL`、bash heredoc语法、`osascript`、`apt`、`systemctl`等）的技能，必须通过`platforms:`前置字段声明其支持的平台。默认原则是先实现跨平台兼容——例如使用`tempfile.gettempdir()`、`pathlib.Path`、`psutil.pid_exists()`，以及Python层面的过滤功能而非`grep`。只有当某种依赖确实受限于特定平台时（如`osascript`仅适用于macOS，`/proc`仅适用于Linux），才将其限制在更窄的范围。

4. **`author`字段应首先标注实际贡献者。** 对于外部贡献，需先列出贡献者的真实姓名及GitHub用户名（格式为`Jane Doe (jane-doe)`），“Hermes Agent”则作为次要协作方。如果贡献者的提交记录中将“Hermes Agent”列为作者，那是因为他们使用Hermes编写了该技能，此时应替换为他们的真实姓名——应表彰个人贡献，而非工具。

5. **SKILL.md的正文需遵循现代的章节结构。** 首先使用`# <Skill> Skill`作为标题，用2-3句话说明该技能的功能与局限性，随后依次包含以下内容：
   - `## When to Use` — 触发条件
   - `## Prerequisites` — 环境变量、安装步骤、MCP设置及API密钥获取方式
   - `## How to Run` — 通过`terminal`工具的标准调用方式
   - `## Quick Reference` — 简洁的命令/API参考表
   - `## Procedure` — 带有可直接复制粘贴的命令的编号步骤说明
   - `## Pitfalls` — 已知的限制、速率限制，以及看似出错但实际上正常的情况
   - `## Verification` — 一个可验证技能是否正常的单一命令

   复杂技能的文档长度宜控制在200行左右，简单技能则为100行左右。应删除冗余的引言、营销性文字，以及已在`## Prerequisites`中说明过的环境变量内容。

6. **脚本文件应存放在`scripts/`目录中，引用文件放在`references/`目录，模板则存于`templates/`目录。** 不要期望模型每次调用时都能内联编写解析器、XML遍历工具或复杂的逻辑——应提供相应的辅助脚本。在SKILL.md中引用脚本时，需使用相对于技能目录的路径。

7. **测试文件位于`tests/skills/test_<skill>_skill.py`处**，且只能使用标准库、pytest以及`unittest.mock`这些工具。禁止进行实时网络请求。可通过`scripts/run_tests.sh tests/skills/test_<skill>_skill.py -q`命令运行测试。测试必须在hermetic CI环境中通过（不能出现API密钥泄露的情况）。对于任何依赖环境变量或文件系统的功能，可使用`monkeypatch`和`tmp_path`来模拟。

8. **`.env.example`文件中的示例内容应被置于一个边界清晰的独立区块中。** 不要修改该文件的其他部分——由贡献者提供的`.env.example`版本通常已经过时，且若在技能专属区块之外进行修改，这些更改将在后续恢复过程中被忽略。所有值都应以`#`开头进行注释（这只是文档内容，而非实际配置）。

### 技能编写指南

- **除非绝对必要，否则不要引入外部依赖。** 建议优先使用Python标准库、curl以及Hermes现有的工具（如`web_extract`、`terminal`、`read_file`）。
- **采用渐进式披露原则。** 先介绍最常用的工作流程，边缘情况和高级用法则放在文档末尾。
- **为XML/JSON解析或复杂逻辑提供辅助脚本**——不要期望大型语言模型每次都能内联编写解析代码。
- **务必进行测试。** 运行命令`hermes --toolsets skills -q "Use the X skill to do Y"`，并确认智能体能正确执行指令。

---

## 添加皮肤/主题

Hermes采用了数据驱动的皮肤系统——添加新皮肤无需修改任何代码。

**方案A：用户自定义皮肤（YAML文件）**

创建`~/.hermes/skins/<名称>.yaml`文件：

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

所有字段均为可选项——缺失的值将沿用默认主题的设置。

**选项 B：内置主题**

在 `hermes_cli/skin_engine.py` 文件中的 `_BUILTIN_SKINS` 字典中添加相应主题。其结构与上文相同，但需以 Python 字典的形式呈现。内置主题随软件包一同提供，始终可用。

**启用方式：**
- 命令行：`/skin mytheme`，或在 config.yaml 中设置 `display.skin: mytheme`
- 配置文件：`display: { skin: mytheme }`

如需查看完整的结构定义及现有主题示例，请参阅 `hermes_cli/skin_engine.py`。

---

## 跨平台兼容性

Hermes 支持在 Linux、macOS 以及原生 Windows 系统（包括 WSL2）上运行。在编写涉及操作系统的代码时，应假设*任何*平台都可能触发该代码路径。

> **在提交 Pull Request 之前：**请运行 `scripts/check-windows-footguns.py`，以检测代码差异中常见的、在 Windows 上存在安全风险的写法。该工具基于 grep 实现，效率很高；CI 系统也会在每个 PR 上自动执行此检查。

### 关键规则

1. **切勿使用 `os.kill(pid, 0)` 进行进程存活检测。**`os.kill(pid, 0)` 是 POSIX 标准中用于判断“该进程是否存活”的方法——信号 0 仅用于进行权限检查，不会实际执行任何操作。**但在 Windows 系统上，它并非无操作。**Python 在 Windows 上的 `os.kill` 函数会将 `sig=0` 转换为 `CTRL_C_EVENT`（两者的整数值均为 0，因此会发生冲突），并通过 `GenerateConsoleCtrlEvent(0, pid)` 将该信号发送给包含目标进程 PID 的**整个控制台进程组**，从而向该组内的所有进程发送 Ctrl+C。这样一来，“检测进程是否存活”的操作实际上会“杀死目标进程以及与其共享同一控制台的许多无关进程”。相关问题可参见 [bpo-14484](https://bugs.python.org/issue14484)（自 2012 年以来一直未解决，出于兼容性考虑也永远不会修复）。

   **推荐做法：**使用 `psutil` 库（它是核心依赖项，始终可用）。

   ```python
   import psutil
   if psutil.pid_exists(pid):
       # process is alive — safe on every platform
       ...
   ```

如果您确实需要使用 Hermes 封装层（它在 `pip install` 完成之前会提供标准库的备用方案），请使用 `gateway.status._pid_exists(pid)`。该函数会首先调用 `psutil.pid_exists`，只有在 `psutil` 无法正常使用时，才会仅在 Windows 系统上采用手动实现的 `OpenProcess + WaitForSingleObject` 方法。

要查找新的调用位置，可使用 Audit grep 命令：`rg "os\.kill\([^,]+,\s*0\s*\)"`。如果在非测试代码中检测到此类调用，很可能是 Windows 系统的静默终止功能存在缺陷。

2. **在调用外部命令之前，请先使用 `shutil.which()` 检查工具是否存在——切勿假设 Windows 拥有 Linux 所有的工具。** `wmic` 已在 Windows 10 21H1 及更高版本中被移除。而 `ps`、`kill`、`grep`、`awk`、`fuser`、`lsof`、`pgrep` 以及大多数 POSIX 风格的 CLI 工具在 Windows 上根本不存在。建议使用 `shutil.which("tool")` 来检测工具是否可用，若不可用则改用 Windows 原生的替代工具——通常是通过 `subprocess.run(["powershell", "-NoProfile", "-Command", ...])` 调用 PowerShell。

对于进程枚举操作，PowerShell 的 `Get-CimInstance Win32_Process` 是 `wmic process` 的现代替代方案。具体实现方式可参考 `hermes_cli/gateway.py::_scan_gateway_pids` 文件中的代码模式。

3. **`termios` 和 `fcntl` 仅适用于 Unix 系统。** 在处理相关功能时，务必同时捕获 `ImportError` 和 `NotImplementedError` 异常。
   ```python
   try:
       from simple_term_menu import TerminalMenu
       menu = TerminalMenu(options)
       idx = menu.show()
   except (ImportError, NotImplementedError):
       # Fallback: numbered menu for Windows
       for i, opt in enumerate(options):
           print(f"  {i+1}. {opt}")
       idx = int(input("Choice: ")) - 1
   ```

4. **文件编码。** Windows系统在保存`.env`文件时可能会使用`cp1252`编码。务必妥善处理编码错误：
   ```python
   try:
       load_dotenv(env_path)
   except UnicodeDecodeError:
       load_dotenv(env_path, encoding="latin-1")
   ```
记事本及类似编辑器在保存配置文件（`config.yaml`）时可能会为其添加 UTF-8 BOM 标记；如果读取的是可能经过 Windows 图形界面编辑器处理的文件，建议使用 `encoding="utf-8-sig"` 参数进行读取。

5. **进程管理。** `os.setsid()`、`os.killpg()`、`os.fork()`、`os.getuid()` 以及 POSIX 信号处理机制在 Windows 系统上存在差异。建议通过 `platform.system()`、`sys.platform` 或 `hasattr(os, "setsid")` 等方式来进行条件判断。
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

6. **Windows 系统中不存在的信号：`SIGALRM`、`SIGCHLD`、`SIGHUP`、`SIGUSR1`、`SIGUSR2`、`SIGPIPE`、`SIGQUIT`、`SIGKILL`。**如果在 Windows 上尝试使用这些信号，Python 的 `signal` 模块会在导入时抛出 `AttributeError` 异常。建议使用 `getattr(signal, "SIGKILL", signal.SIGTERM)` 方法，或通过平台检测将相关代码块包裹起来。在 Windows 上，`loop.add_signal_handler` 会引发 `NotImplementedError` 异常，务必进行捕获处理。

7. **路径分隔符。**应使用 `pathlib.Path` 对象而非用 `/` 进行字符串拼接。虽然正斜杠在 Windows 上几乎到处都可用，但 `subprocess.run(["cmd.exe", "/c", ...])` 及其他 Shell 环境可能要求使用反斜杠——因此应在子进程调用边界处通过 `str(path)` 进行转换，而非在 Python 逻辑内部处理。

8. **在 Windows 上创建符号链接需要提升权限**（除非启用了开发者模式）。若测试中涉及创建符号链接，应添加标记 `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")` 以跳过该测试。

9. **默认情况下，NTFS 文件系统不会强制执行 POSIX 文件权限模式（如 0o600、0o644 等）。**那些依赖 `stat().st_mode & 0o777` 来进行断言的测试在 Windows 上必须被跳过——因为该概念在 NTFS 上并不适用。如有必要，可使用 ACL（如 `icacls`、`pywin32`）来实现对 Windows 系统中敏感文件的保护。

10. **在 Windows 上运行独立的后台守护进程需使用 `pythonw.exe`，而非 `python.exe`。**`python.exe` 总是会分配控制台或与其关联，这使其容易受到任何同级进程发送的 `CTRL_C_EVENT` 信号的影响。而 `pythonw.exe` 是无需控制台的版本。可在 `subprocess.Popen(creationflags=...)` 中结合使用 `CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB` 标志。相关实现可参考 `hermes_cli/gateway_windows.py::_spawn_detached` 文件。

11. **当使用 `.cmd` 或 `.bat` 启动脚本时，`subprocess.Popen` 需要借助 `shutil.which` 函数来定位可执行文件。**在 Windows 上，若直接将 `"agent-browser"` 传递给 `Popen`，它会查找 `node_modules/.bin/` 目录中那个没有扩展名的 POSIX 启动脚本，而 `CreateProcessW` 无法执行此类文件，从而导致 `WinError 193 "not a valid Win32 application"` 错误。建议使用 `shutil.which("agent-browser", path=local_bin)`，该函数会考虑 PATHEXT 设置，并在 Windows 上自动选择 `.CMD` 格式的可执行文件。

12. **切勿使用 Shell 启动行作为运行 Python 的方式。**`#!/usr/bin/env python` 仅能在通过 Unix Shell 执行文件时生效。即使在文件中存在启动行，使用 `subprocess.run(["./myscript.py"])` 在 Windows 上也会失败。应始终明确指定 Python 的执行路径：`[sys.executable, "myscript.py"]`。

13. **安装程序中的 Shell 命令。**如果修改了 `scripts/install.sh` 文件，也需同步修改 `scripts/install.ps1` 文件。这两个脚本是“在 Linux 上可行不代表在 Windows 上也能运行”这一现象的典型例子，且其实现方式已多次变更——务必保持两者完全一致。

14. **在 Windows 上，以下路径会被 OneDrive 重定向：桌面、文档、图片、视频文件夹。**当启用 OneDrive 备份功能时，这些文件夹的“真实”路径为 `%USERPROFILE%\OneDrive\Desktop` 等，而非看似存在的空目录 `%USERPROFILE%\Desktop`。可通过 `ctypes` + `SHGetKnownFolderPath` 函数或读取 `Shell Folders` 注册表项来确定真实路径——切勿直接假设使用 `~/Desktop`。

15. **生成的脚本中应使用 CRLF 还是 LF 行结束符？**Windows 系统的 `cmd.exe` 和 `schtasks` 工具都是逐行解析命令的，混合使用行结束符或仅使用 LF 格式的行尾可能会导致多行 `.cmd`/`.bat` 文件出错。在生成 Windows 可执行的脚本时，应使用 `open(path, "w", encoding="utf-8", newline="\r\n")`，或直接使用 `open(path, "wb")` 并显式指定字节序列。

16.**在一个命令行中不能混用两种不同的引号规则。**`subprocess.run(["schtasks", "/TR", some_cmd])` 中，`/TR` 部分由 `schtasks` 自身解析，而 `some_cmd` 字符串则会在任务执行时由 `cmd.exe` 重新解析。由于解析器不同，其转义规则也有所差异。因此应分别使用不同的引号处理函数，切勿混用。相关实现可参考 `hermes_cli/gateway_windows.py::_quote_cmd_script_arg` 和 `_quote_schtasks_arg` 函数。

### 跨平台测试策略

那些依赖仅适用于 POSIX 系统的系统调用的测试需要添加跳过标记。常见示例包括：
- 符号链接相关测试 → `@pytest.mark.skipif(sys.platform == "win32", ...)`
- 文件权限模式为 `0o600` 的测试 → `@pytest.mark.skipif(sys.platform.startswith("win"), ...)`
- `signal.SIGALRM` 相关测试 → 仅适用于 Unix 系统（参见 `tests/conftest.py::_enforce_test_timeout`）
- `os.setsid` / `os.fork` 相关测试 → 仅适用于 Unix 系统
- 需要实时 Winsock 功能或针对 Windows 特有的回归测试 → `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`

如果在跨平台测试中通过 monkeypatch 修改了 `sys.platform`，也应同时修改 `platform.system()`、`platform.release()` 和 `platform.mac_ver()` 这些函数——因为它们各自都会独立读取真实的操作系统信息，否则即使部分函数被修改，Windows 环境下的测试仍可能走错分支。

---

## 安全性考量

Hermes 具有终端访问权限，因此安全性至关重要。

### 现有的安全防护措施

| 防护层级 | 实现方式 |
|---------|----------|
| **Sudo 密码传递保护** | 使用 `shlex.quote()` 函数防止 Shell 注入攻击 |
| **危险命令检测** | 在 `tools/approval.py` 中通过正则表达式配合用户审批流程进行检测 |
| **Cron 任务注入防护** | `tools/cronjob_tools.py` 中的扫描工具可识别并阻止可能篡改任务的指令模式 |
| **写操作禁止列表** | 对敏感路径（如 `~/.ssh/authorized_keys`、`/etc/shadow`）通过 `os.path.realpath()` 获取真实路径，从而防止通过符号链接绕过限制 |
| **技能模块安全防护** | 通过 `tools/skills_guard.py` 对 hub 安装的技能模块进行安全扫描 |
| **代码执行沙箱** | `execute_code` 子进程在运行时会将环境变量中的 API 密钥移除 |
| **容器加固措施** | 在 Docker 环境中会取消所有额外权限、禁止权限提升、设置 PID 上限，并限制临时文件系统的大小 |

### 在提交涉及安全敏感的代码时的注意事项

- 在将用户输入插入 Shell 命令时，务必始终使用 `shlex.quote()` 进行转义处理。
- 在进行基于路径的访问控制检查之前，应先通过 `os.path.realpath()` 获取路径的真实内容。
- **绝不对敏感信息进行日志记录。**API 密钥、令牌和密码等敏感数据绝不能出现在日志输出中。
- 应在工具执行周围添加异常处理机制，避免某次失败导致整个代理循环崩溃。
- 如果你的修改涉及文件路径、进程管理或 Shell 命令，必须在所有平台上进行测试。

如果你的 Pull Request 可能影响系统安全，请在描述中明确说明。

### 依赖项锁定策略（供应链安全加固）

在 2026 年 3 月发生的 [litellm 供应链攻击事件](https://github.com/BerriAI/litellm/issues/24512)以及 2026 年 5 月出现的 [Mini Shai-Hulud 僵虫攻击事件](https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack)之后，所有依赖项都必须遵循以下规则：

| 依赖来源类型 | 要求的锁定方式 | 原因说明 |
|---|---|---|
| **PyPI 包** | 使用 `>=floor,<next_major` 的版本范围 | PyPI 上的版本一旦发布即不可更改，但开发者仍可推送新版本到该范围。设置 `<next_major` 的上限可以防止原本安装的是 1.x 版本被升级为恶意的 2.0.0 版本。 |
| **Git URL 指定的依赖**（如 atroposlib、tinker、yc-bench、Baileys 等） | 需锁定完整的提交 SHA 值 | 分支和标签都是可变的引用，而 SHA 值是基于内容唯一标识的。 |
| **GitHub Actions 相关依赖** | 需锁定完整的提交 SHA 值以及版本注释 | Action 的标签也是可变的引用（例如 tj-actions/changed-files 2025 年 3 月版本），因此应将其锁定为 `uses: owner/action@<sha>  # vX.Y.Z` 的形式。 |
| **仅用于 CI 环境的 pip 安装依赖** | 可使用 `==exact` 精确锁定版本 | Hermetic 的 CI 环境构建频率较低，允许使用固定版本。 |

**在 Pull Request 中新增的任何 PyPI 依赖项都必须设置 `<next_major` 作为版本上限。**那些指定无限制 `>=X.Y.Z` 版本范围的依赖项将会被审稿人拒绝。`supply-chain-audit.yml` CI 工作流还会自动标记依赖清单中的变更，以便人工审核。

**如何确定版本上限：**
- 如果该包的当前版本为 `1.x.y`，则上限可设置为 `<2`。
- 如果该包处于 `0.x.y` 版本阶段（即 1.0 之前），则上限可设置为 `<0.(当前次要版本号 + 2)`。例如，如果当前版本是 `0.29.x`，则上限为 `<0.32`。这样的设置能在保留一定版本灵活性的同时，确保恶意篡改后的版本不太可能落入该范围内。
- 特例：那些 API 非常稳定的包（如 `aiohttp-socks`），经审稿人评估后也可使用 `<1` 作为上限。

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

1. **运行测试**：使用 `scripts/run_tests.sh`（推荐，与 CI 流水线相同），或在激活项目虚拟环境后执行 `pytest tests/ -v`。
2. **手动测试**：启动 `hermes` 并调用你修改过的代码路径进行测试。
3. **检查跨平台兼容性**：如果你修改了文件读写、进程管理或终端处理相关功能，需确保其在 macOS、Linux 和 WSL2 环境下都能正常运行。
4. **保持 PR 的专注性**：每个 PR 应只包含一个逻辑上的更改。切勿将错误修复、代码重构和新功能合并到同一个 PR 中。

### PR 描述内容

需包含以下信息：
- **具体修改了什么**以及**原因**
- **如何测试该更改**（错误的复现步骤，功能的使用示例）
- **在哪些平台上进行了测试**
- 参考相关的 Issues 编号

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

适用范围：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security` 等。

示例：
```
fix(cli): prevent crash in save_config_value when model is a string
feat(gateway): add WhatsApp multi-user session isolation
fix(security): prevent shell injection in sudo password piping
test(tools): add unit tests for file_operations
```

---

## 报告问题

- 请通过 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues) 提交问题
- 需提供以下信息：操作系统、Python版本、Hermes版本（使用 `hermes version` 命令查看）、完整的错误堆栈信息
- 同时需附上问题重现的步骤
- 在提交新问题前请先查看已有问题，避免重复提交
- 若发现安全漏洞，请通过私密渠道进行报告

---

## 社区交流

- **Discord**：[discord.gg/NousResearch](https://discord.gg/NousResearch) —— 用于提问、展示项目成果及分享技能
- **GitHub Discussions**：用于讨论设计方案与架构相关内容
- **Skills Hub**：可将自定义技能上传至注册表，并在社区中分享

---

## 许可协议

通过贡献代码，即表示您同意您的贡献将依据 [MIT许可证](LICENSE) 进行授权。
