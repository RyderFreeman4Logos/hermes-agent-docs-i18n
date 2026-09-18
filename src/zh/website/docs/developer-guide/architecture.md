---
sidebar_position: 1
title: "Architecture"
description: "Hermes Agent internals — major subsystems, execution paths, data flow, and where to read next"
---

# 架构

本页面是Hermes Agent内部结构的顶层概览图。借助它您可以快速了解代码库的整体架构，随后可深入查看各子系统对应的文档以获取实现细节。

## 系统概览

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        Entry Points                                  │
│                                                                      │
│  CLI (cli.py)    Gateway (gateway/run.py)    ACP (acp_adapter/)     │
│  Batch Runner    API Server                  Python Library          │
└──────────┬──────────────┬───────────────────────┬───────────────────┘
           │              │                       │
           ▼              ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AIAgent (run_agent.py)                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Prompt       │  │ Provider     │  │ Tool         │               │
│  │ Builder      │  │ Resolution   │  │ Dispatch     │               │
│  │ (prompt_     │  │ (runtime_    │  │ (model_      │               │
│  │  builder.py) │  │  provider.py)│  │  tools.py)   │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                       │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐               │
│  │ Compression  │  │ 3 API Modes  │  │ Tool Registry│               │
│  │ & Caching    │  │ chat_compl.  │  │ (registry.py)│               │
│  │              │  │ codex_resp.  │  │ 70+ tools    │               │
│  │              │  │ anthropic    │  │ 28 toolsets  │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────┴─────────────────┴─────────────────┴───────────────────────┘
           │                                    │
           ▼                                    ▼
┌───────────────────┐              ┌──────────────────────┐
│ Session Storage   │              │ Tool Backends         │
│ (SQLite + FTS5)   │              │ Terminal (7 backends) │
│ hermes_state.py   │              │ Browser (5 backends)  │
│ gateway/session.py│              │ Web (4 backends)      │
└───────────────────┘              │ MCP (dynamic)         │
                                   │ File, Vision, etc.    │
                                   └──────────────────────┘
```

## 目录结构

```text
hermes-agent/
├── run_agent.py              # AIAgent facade — loop lives in agent/conversation_loop.py + agent/turn_*.py
├── cli.py                    # HermesCLI facade — mixins in hermes_cli/cli_*_mixin.py
├── model_tools.py            # Tool discovery, schema collection, dispatch
├── toolsets.py               # Tool groupings and platform presets
├── hermes_state.py           # SQLite session/state database facade (+ hermes_state_*.py siblings)
├── hermes_constants.py       # HERMES_HOME, profile-aware paths
├── batch_runner.py           # Batch trajectory generation
│
├── agent/                    # Agent internals
│   ├── prompt_builder.py     # System prompt assembly
│   ├── context_engine.py     # ContextEngine ABC (pluggable)
│   ├── context_compressor.py # Default engine — lossy summarization
│   ├── prompt_caching.py     # Anthropic prompt caching
│   ├── auxiliary_client.py   # Auxiliary LLM for side tasks (vision, summarization)
│   ├── model_metadata.py     # Model context lengths, token estimation
│   ├── models_dev.py         # models.dev registry integration
│   ├── anthropic_adapter.py  # Anthropic Messages API format conversion
│   ├── display.py            # KawaiiSpinner, tool preview formatting
│   ├── skill_commands.py     # Skill slash commands
│   ├── memory_manager.py    # Memory manager orchestration
│   ├── memory_provider.py   # Memory provider ABC
│   └── trajectory.py         # Trajectory saving helpers
│
├── hermes_cli/               # CLI subcommands and setup
│   ├── main.py               # Entry point — `hermes` subcommands (parsers in subcommands/, main_*.py)
│   ├── config.py             # DEFAULT_CONFIG, OPTIONAL_ENV_VARS, migration
│   ├── commands.py           # COMMAND_REGISTRY — central slash command definitions
│   ├── auth.py               # PROVIDER_REGISTRY, credential resolution (+ auth_*.py siblings)
│   ├── runtime_provider.py   # Provider → api_mode + credentials
│   ├── models.py             # Model catalog, provider model lists
│   ├── model_switch.py       # /model command logic (CLI + gateway shared)
│   ├── setup.py              # Interactive setup wizard (+ setup_*.py siblings)
│   ├── skin_engine.py        # CLI theming engine
│   ├── skills_config.py      # hermes skills — enable/disable per platform
│   ├── skills_hub.py         # /skills slash command
│   ├── tools_config.py       # hermes tools — enable/disable per platform
│   ├── plugins.py            # PluginManager — discovery, loading, hooks
│   ├── callbacks.py          # Terminal callbacks (clarify, sudo, approval)
│   └── gateway.py            # hermes gateway start/stop
│
├── tools/                    # Tool implementations (one file per tool)
│   ├── registry.py           # Central tool registry
│   ├── approval.py           # Dangerous command detection
│   ├── terminal_tool.py      # Terminal orchestration
│   ├── process_registry.py   # Background process management
│   ├── file_tools.py         # read_file, write_file, patch, search_files
│   ├── web_tools.py          # web_search, web_extract
│   ├── browser_tool.py       # Browser automation tools facade (+ browser_tool_*.py siblings)
│   ├── code_execution_tool.py # execute_code sandbox
│   ├── delegate_tool.py      # Subagent delegation
│   ├── mcp_tool.py           # MCP client facade (+ mcp_tool_*.py siblings)
│   ├── credential_files.py   # File-based credential passthrough
│   ├── env_passthrough.py    # Env var passthrough for sandboxes
│   ├── ansi_strip.py         # ANSI escape stripping
│   └── environments/         # Terminal backends (local, docker, ssh, modal, daytona, singularity)
│
├── gateway/                  # Messaging platform gateway
│   ├── run.py                # GatewayRunner facade — message dispatch (+ run_*.py siblings)
│   ├── session.py            # SessionStore — conversation persistence
│   ├── delivery.py           # Outbound message delivery
│   ├── pairing.py            # DM pairing authorization
│   ├── hooks.py              # Hook discovery and lifecycle events
│   ├── mirror.py             # Cross-session message mirroring
│   ├── status.py             # Token locks, profile-scoped process tracking
│   ├── builtin_hooks/        # Extension point for always-registered hooks (none shipped)
│   └── platforms/            # Built-in adapters: signal, weixin, bluebubbles,
│                             #   qqbot, whatsapp_cloud, yuanbao, webhook, api_server
│
├── plugins/platforms/        # Bundled platform plugins: telegram, discord, slack,
│                             #   whatsapp, matrix, mattermost, email, sms, dingtalk,
│                             #   feishu, wecom, homeassistant, irc, line, teams,
│                             #   google_chat, buzz, ntfy, photon, raft, simplex
│
├── acp_adapter/              # ACP server (VS Code / Zed / JetBrains)
├── cron/                     # Scheduler (jobs.py, scheduler.py)
├── plugins/memory/           # Memory provider plugins
├── plugins/context_engine/   # Context engine plugins
├── skills/                   # Bundled skills (always available)
├── optional-skills/          # Official optional skills (install explicitly)
├── website/                  # Docusaurus documentation site
└── tests/                    # Pytest suite (~25,000 tests across ~1,250 files)
```

## 数据流

### CLI 会话

```text
User input → HermesCLI.process_input()
  → AIAgent.run_conversation()
    → prompt_builder.build_system_prompt()
    → runtime_provider.resolve_runtime_provider()
    → API call (chat_completions / codex_responses / anthropic_messages)
    → tool_calls? → model_tools.handle_function_call() → loop
    → final response → display → save to SessionDB
```

### 网关消息

```text
Platform event → Adapter.on_message() → MessageEvent
  → GatewayRunner._handle_message()
    → authorize user
    → resolve session key
    → create AIAgent with session history
    → AIAgent.run_conversation()
    → deliver response back through adapter
```

### 定时任务

```text
Scheduler tick → load due jobs from jobs.json
  → create fresh AIAgent (no history)
  → inject attached skills as context
  → run job prompt
  → deliver response to target platform
  → update job state and next_run
```

## 推荐阅读顺序

如果您是代码库的新手：

1. **本页面** — 熟悉整体架构
2. **[Agent Loop 内部机制](./agent-loop.md)** — AIAgent 的工作原理
3. **[提示词组装](./prompt-assembly.md)** — 系统提示词的构建方法
4. **[Provider 运行时解析](./provider-runtime.md)** — 提供者的选择机制
5. **[添加提供者](./adding-providers.md)** — 添加新提供者的实用指南
6. **[工具运行时](./tools-runtime.md)** — 工具注册表、调度机制及环境管理
7. **[会话存储](./session-storage.md)** — SQLite 数据结构、FTS5 索引及会话追溯功能
8. **[网关内部机制](./gateway-internals.md)** — 消息平台网关实现
9. **[上下文压缩与提示词缓存](./context-compression-and-caching.md)** — 压缩与缓存技术
10. **[ACP 内部机制](./acp-internals.md)** — IDE 集成方案

## 主要子系统

### Agent Loop

同步调度引擎（由 `run_agent.py` 接口提供，核心逻辑位于 `agent/conversation_loop.py` 和 `agent/turn_*.py` 文件中）。负责处理提供者选择、提示词构建、工具执行、重试机制、备用方案、回调处理、数据压缩及持久化存储等功能。针对不同的提供者后端，支持三种 API 模式。

→ [Agent Loop 内部机制](./agent-loop.md)

### 提示词系统

贯穿整个对话生命周期的提示词构建与维护功能：

- **`system_prompt.py` + `prompt_builder.py`** — 负责按顺序组织系统提示层结构（`stable` → `context` → `volatile`）：身份/工具指引/技能信息、上下文文件，以及内存/配置/时间戳模块。  
- **`prompt_caching.py`** — 应用 Anthropic 的缓存断点机制来实现前缀内容缓存。  
- **`context_compressor.py`** — 当上下文长度超过阈值时，自动总结中间对话内容。  

→ [提示语组装](./prompt-assembly.md)，[上下文压缩与提示语缓存](./context-compression-and-caching.md)

### 提供商解析

这是一个通用的运行时解析器，被 CLI、网关、定时任务、ACP 以及各类辅助调用所使用。它可将 `(provider, model)` 元组映射为 `(api_mode, api_key, base_url)` 的格式，并支持 18 种以上的提供商、OAuth 认证流程、凭证池管理以及别名解析功能。  

→ [提供商运行时解析](./provider-runtime.md)

### 工具系统

拥有中央工具注册表（`tools/registry.py`），目前共注册了来自约 28 组工具集的 70 多种工具。每个工具文件在导入时会自动完成注册。该注册表负责处理工具结构信息的收集、调度、可用性检查以及错误处理。终端工具支持 7 种后端环境（本地、Docker、SSH、Daytona、Modal、Singularity、Vercel Sandbox）。  

→ [工具运行时](./tools-runtime.md)

### 会话持久化

基于 SQLite 的会话存储系统，配备 FTS5 全文搜索功能。该系统支持会话关联追踪（处理压缩后的父子会话关系）、按平台隔离存储，同时还具备带冲突处理的原子写入能力。  

→ [会话存储](./session-storage.md)

### 消息网关

支持长期运行的进程，集成25种以上的平台适配器（内置及捆绑插件），具备统一的会话路由功能、用户授权机制（白名单与私信配对）、斜杠命令分发系统、钩子系统、定时任务调度以及后台维护功能。

→ [Gateway 内部机制](./gateway-internals.md)

### 插件系统

提供三种插件发现路径：`~/.hermes/plugins/`（用户级）、`.hermes/plugins/`（项目级）以及 pip 包入口。插件可通过上下文 API 注册工具、钩子函数及 CLI 命令。目前存在两种专用插件类型：内存提供器（`plugins/memory/`）和上下文引擎（`plugins/context_engine/`）。这两种类型均为单选机制，同一时间仅能启用其中一个，可通过 `hermes plugins` 或 `config.yaml` 进行配置。

→ [插件指南](/developer-guide/plugins)，[内存提供器插件](./memory-provider-plugin.md)

### 定时任务调度

支持作为一等级的智能体任务执行（而非 shell 任务）。任务以 JSON 格式存储，兼容多种调度格式，可附加技能与脚本，并能发送至任意平台。

→ [定时任务内部机制](./cron-internals.md)

### ACP 集成

通过 stdio/JSON-RPC 接口，将 Hermes 作为编辑器原生的智能体集成到 VS Code、Zed 以及 JetBrains 等工具中。

→ [ACP 内部机制](./acp-internals.md)

### 轨迹生成

能够从智能体会话中生成 ShareGPT 格式的轨迹数据，用于训练数据构建。

→ [轨迹格式与训练指南](./trajectory-format.md)

## 设计原则

| 原则 | 实际应用意义 |
|-----------|----------------|
| **提示词稳定性** | 对话过程中系统提示词不会发生变化。除非用户主动执行 `/model` 指令，否则不会发生破坏缓存的变更。 |
| **可观测的执行过程** | 每次工具调用都会通过回调机制向用户展示执行状态。CLI界面和网关会以进度指示器及聊天消息的形式反馈处理进度。 |
| **可中断性** | 用户可通过输入指令或发送信号，在API调用及工具执行过程中随时中止操作。 |
| **与平台无关的核心架构** | 一个 AIAgent 类即可同时服务于 CLI、网关、ACP、批处理任务以及 API 服务器。不同平台之间的差异仅体现在入口点上，而非代理本身。 |
| **松耦合设计** | 可选子系统（如 MCP、插件、内存提供器、强化学习环境等）通过注册表机制和 check_fn 筛选功能进行连接，而非依赖硬编码的绑定关系。 |
| **配置隔离** | 每个配置文件（`hermes -p <name>`）拥有独立的 HERMES_HOME、配置文件、内存数据、会话记录以及网关进程标识符。多个配置文件可同时运行。 |

## 文件依赖链

```text
tools/registry.py  (no deps — imported by all tool files)
       ↑
tools/*.py  (each calls registry.register() at import time)
       ↑
model_tools.py  (imports tools/registry + triggers tool discovery)
       ↑
run_agent.py, cli.py, batch_runner.py, environments/
```

该工作流意味着工具注册会在导入阶段完成，即在创建任何代理实例之前。凡是包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会被自动识别——无需手动指定导入列表。
