---
sidebar_position: 1
title: "Architecture"
description: "Hermes Agent internals — major subsystems, execution paths, data flow, and where to read next"
---

# 架构

本页面是Hermes Agent内部结构的顶层概览图。借助它可快速了解代码库的整体架构，随后可深入查看各子系统的文档以获取具体实现细节。

## 系统概述

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
│ (SQLite + FTS5)   │              │ Terminal (6 backends) │
│ hermes_state.py   │              │ Browser (5 backends)  │
│ gateway/session.py│              │ Web (4 backends)      │
└───────────────────┘              │ MCP (dynamic)         │
                                   │ File, Vision, etc.    │
                                   └──────────────────────┘
```

## 目录结构

```text
hermes-agent/
├── run_agent.py              # AIAgent — core conversation loop (large file)
├── cli.py                    # HermesCLI — interactive terminal UI (large file)
├── model_tools.py            # Tool discovery, schema collection, dispatch
├── toolsets.py               # Tool groupings and platform presets
├── hermes_state.py           # SQLite session/state database with FTS5
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
│   ├── main.py               # Entry point — all `hermes` subcommands (large file)
│   ├── config.py             # DEFAULT_CONFIG, OPTIONAL_ENV_VARS, migration
│   ├── commands.py           # COMMAND_REGISTRY — central slash command definitions
│   ├── auth.py               # PROVIDER_REGISTRY, credential resolution
│   ├── runtime_provider.py   # Provider → api_mode + credentials
│   ├── models.py             # Model catalog, provider model lists
│   ├── model_switch.py       # /model command logic (CLI + gateway shared)
│   ├── setup.py              # Interactive setup wizard (large file)
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
│   ├── browser_tool.py       # 10 browser automation tools
│   ├── code_execution_tool.py # execute_code sandbox
│   ├── delegate_tool.py      # Subagent delegation
│   ├── mcp_tool.py           # MCP client (large file)
│   ├── credential_files.py   # File-based credential passthrough
│   ├── env_passthrough.py    # Env var passthrough for sandboxes
│   ├── ansi_strip.py         # ANSI escape stripping
│   └── environments/         # Terminal backends (local, docker, ssh, modal, daytona, singularity)
│
├── gateway/                  # Messaging platform gateway
│   ├── run.py                # GatewayRunner — message dispatch (large file)
│   ├── session.py            # SessionStore — conversation persistence
│   ├── delivery.py           # Outbound message delivery
│   ├── pairing.py            # DM pairing authorization
│   ├── hooks.py              # Hook discovery and lifecycle events
│   ├── mirror.py             # Cross-session message mirroring
│   ├── status.py             # Token locks, profile-scoped process tracking
│   ├── builtin_hooks/        # Extension point for always-registered hooks (none shipped)
│   └── platforms/            # 20 adapters: telegram, discord, slack, whatsapp,
│                             #   signal, matrix, mattermost, email, sms,
│                             #   dingtalk, feishu, wecom, wecom_callback, weixin,
│                             #   bluebubbles, qqbot, homeassistant, webhook, api_server,
│                             #   yuanbao
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

如果您是初次接触该代码库：

1. **本页面** — 了解整体架构
2. **[Agent Loop Internals](./agent-loop.md)** — AIAgent 的工作原理
3. **[Prompt Assembly](./prompt-assembly.md)** — 系统提示词的构建方式
4. **[Provider Runtime Resolution](./provider-runtime.md)** — 提供者的选择机制
5. **[Adding Providers](./adding-providers.md)** — 添加新提供者的实用指南
6. **[Tools Runtime](./tools-runtime.md)** — 工具注册表、调度机制与运行环境
7. **[Session Storage](./session-storage.md)** — SQLite 数据结构、FTS5 全文搜索及会话追溯功能
8. **[Gateway Internals](./gateway-internals.md)** — 消息平台网关详解
9. **[Context Compression & Prompt Caching](./context-compression-and-caching.md)** — 上下文压缩与提示词缓存技术
10. **[ACP Internals](./acp-internals.md)** — IDE 集成功能

## 主要子系统

### Agent Loop

同步协调引擎（位于 `run_agent.py` 中的 `AIAgent`）。负责处理提供者选择、提示词构建、工具执行、重试机制、回退策略、回调处理、数据压缩及持久化存储。针对不同的提供者后端，支持三种 API 模式。

→ [Agent Loop Internals](./agent-loop.md)

### 提示词系统

贯穿整个对话生命周期的提示词构建与维护机制：

- **`system_prompt.py` + `prompt_builder.py`** — 按固定顺序组装系统提示词层级（`stable` → `context` → `volatile`）：包括身份/工具指引/技能信息、上下文文件，以及内存/个人资料/时间戳相关内容
- **`prompt_caching.py`** — 应用 Anthropic 的缓存断点机制实现前缀级缓存
- **`context_compressor.py`** — 当上下文长度超过阈值时，对中间对话内容进行摘要处理

→ [Prompt Assembly](./prompt-assembly.md), [Context Compression & Prompt Caching](./context-compression-and-caching.md)

### 提供者解析模块

被 CLI、网关、定时任务、ACP 以及各类辅助调用所共享的运行时解析器。它将 `(provider, model)` 元组映射为 `(api_mode, api_key, base_url)` 的格式。该模块可支持 18 种以上的提供者，同时处理 OAuth 认证流程、凭证池管理及别名解析功能。

→ [Provider Runtime Resolution](./provider-runtime.md)

### 工具系统

中央工具注册表（位于 `tools/registry.py`），目前已有超过 70 种工具注册在约 28 个工具集中。每个工具文件在导入时会自动完成注册。该注册表负责处理工具结构信息的收集、调度、可用性检查以及错误封装。终端工具支持 6 种运行后端：本地模式、Docker 模式、SSH 模式、Daytona 模式、Modal 模式和 Singularity 模式。

→ [Tools Runtime](./tools-runtime.md)

### 会话持久化

基于 SQLite 的会话存储机制，同时集成 FTS5 全文搜索功能。该系统具备会话追溯能力（可追踪压缩操作前后的父子会话关系）、平台隔离功能，以及带有冲突处理机制的原子写操作。

→ [Session Storage](./session-storage.md)

### 消息网关

作为一个长期运行的进程，该网关拥有 20 种平台适配器，可实现统一的会话路由、用户授权管理（基于白名单与私信配对机制）、斜杠命令调度、钩子系统功能、定时任务触发以及后台维护操作。

→ [Gateway Internals](./gateway-internals.md)

### 插件系统

插件来源共有三种：`~/.hermes/plugins/`（用户自定义插件）、`.hermes/plugins/`（项目级插件）以及 pip 安装的插件。插件可通过上下文 API 注册工具、钩子函数及 CLI 命令。目前存在两种专用插件类型：内存提供者插件（位于 `plugins/memory/` 目录）和上下文引擎插件（位于 `plugins/context_engine/` 目录）。这两种插件均为单选机制——同一时间仅能启用其中一个，可通过 `hermes plugins` 命令或 `config.yaml` 文件进行配置。

→ [Plugin Guide](/guides/build-a-hermes-plugin), [Memory Provider Plugin](./memory-provider-plugin.md)

### 定时任务系统

支持高级别的智能体任务处理（而非普通的 shell 脚本任务）。定时任务以 JSON 格式存储，支持多种调度格式，可附加技能函数与脚本代码，并能被发送到任意支持的平台上执行。

→ [Cron Internals](./cron-internals.md)

### ACP 集成

通过 stdio/JSON-RPC 接口，将 Hermes 作为编辑器原生的智能体功能集成到 VS Code、Zed 以及 JetBrains 系列软件中。

→ [ACP Internals](./acp-internals.md)

### 轨迹数据生成

可从智能体会话中生成 ShareGPT 格式的轨迹数据，用于后续训练数据的创建。

→ [Trajectories & Training Format](./trajectory-format.md)

## 设计原则

| 原则 | 实际应用意义 |
|------|--------------|
| **提示词稳定性** | 对话过程中系统提示词不会发生变更。除非用户主动执行 `/model` 指令，否则不会触发任何可能破坏缓存的结构变动。 |
| **执行过程可观测性** | 每次工具调用都会通过回调机制向用户展示执行状态。CLI 端会显示进度指示器，而网关端则会通过聊天消息反馈执行进度。 |
| **可中断性** | 用户可通过输入指令或发送特定信号，随时取消正在进行的 API 调用或工具执行任务。 |
| **平台无关的核心架构** | 一个 AIAgent 类即可同时服务于 CLI、网关、ACP、批处理任务以及 API 服务器。不同平台之间的差异仅体现在入口点上，而非智能体本身。 |
| **松耦合设计** | 各种可选子系统（如 MCP、插件、内存提供者、强化学习环境等）均采用注册表模式和检查函数机制进行控制，而非硬编码依赖关系。 |
| **个人资料隔离** | 每个个人资料（通过 `hermes -p <name>` 命令创建）都会拥有独立的 HERMES_HOME 目录、配置文件、内存数据、会话记录以及网关进程标识符。多个个人资料可同时并行运行。 |

## 文件依赖关系链

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
