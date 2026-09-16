---
title: "Codebase Ownership Map"
description: "Which directories belong to which subsystem, and where the right docs entry point lives for each"
---

# 代码库归属映射表

Hermes 是一个规模庞大的代码仓库，大多数贡献仅涉及其中一个子系统。本页面将每个子系统与其对应的源代码目录以及修改前需查阅的文档入口进行了对应标注。您可以通过它快速找到合适的起始文档、修改代码的位置以及相应的测试目录（测试文件与源代码结构保持一致：位于 `tools/` 目录中的代码会在 `tests/tools/` 中进行测试，插件则位于 `tests/plugins/<类型>/` 中，以此类推）。

| Subsystem | Source directories | Docs entry point |
|-----------|-------------------|------------------|
| Agent core (loop, transports, compression) | `agent/`, `run_agent.py` | [Agent Loop](agent-loop.md), [Context Compression & Caching](context-compression-and-caching.md) |
| Prompt assembly | `agent/prompt_builder.py`, `agent/system_prompt.py` | [Prompt Assembly](prompt-assembly.md) |
| Model providers & transports | `agent/transports/`, `plugins/model-providers/`, `hermes_cli/models.py` | [Adding Providers](adding-providers.md), [Model Provider Plugins](model-provider-plugin.md), [Provider Runtime](provider-runtime.md) |
| Built-in tools | `tools/` | [Adding Tools](adding-tools.md), [Tools Runtime](tools-runtime.md) |
| Messaging gateway | `gateway/`, `plugins/platforms/` | [Gateway Internals](gateway-internals.md), [Adding Platform Adapters](adding-platform-adapters.md) |
| CLI | `hermes_cli/` | [Extending the CLI](extending-the-cli.md) |
| Plugins system | `plugins/` | [Build a Hermes Plugin](plugins/index.md) |
| Skills (bundled & optional) | `skills/`, `optional-skills/` | [Creating Skills](creating-skills.md) |
| Cron / scheduled jobs | `cron/` | [Cron Internals](cron-internals.md) |
| Session storage | `hermes_state.py`, `hermes_state_*.py` | [Session Storage](session-storage.md) |
| Browser stack | `tools/browser_tool.py`, `tools/browser_supervisor.py`, `tools/browser_cdp_tool.py` | [Browser Supervisor](browser-supervisor.md) |
| Egress firewall | `agent/proxy_sources/iron_proxy.py` | [Egress Internals](egress-internals.md) |
| ACP (IDE integration) | `acp_adapter/` | [ACP Internals](acp-internals.md) |
| Desktop app | `apps/desktop/` | [Desktop Plugin SDK](desktop-plugin-sdk.md), [Worktree UI Development](worktree-ui-dev.md) |
| TUI | `ui-tui/`, `tui_gateway/` | [Worktree UI Development](worktree-ui-dev.md) |
| Docs site | `website/` | [Contributing](contributing.md) |
| Tests | `tests/`, `tests-js/` | [Contributing → Before Submitting](contributing.md#before-submitting) |

与此规范相关的几项重要原则如下：

- **修改应局限于各自的子系统内部。** 若某个插件需要直接编辑核心文件，即属于设计缺陷——此时应考虑扩展通用插件的功能接口（详情请参阅仓库中 `AGENTS.md` 文件里的贡献指南）。
- **对于你修改的每一个源代码目录，都必须确保其对应的测试目录也能通过测试。** 对 `plugins/platforms/telegram/` 目录所做的修改，必须能保证 `tests/plugins/platforms/` 目录下的所有测试用例均通过，而不仅仅是你随手选择的某个测试文件。
- **当涉及两个子系统时，变更应由范围更小的那个子系统来处理。** 相较于在代理核心代码中创建分支，优先通过适配器或插件来实现修复；因为核心代码的灵活性较差，任何新增功能都会在每次 API 调用时带来性能损耗。
