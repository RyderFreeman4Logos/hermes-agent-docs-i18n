---
sidebar_label: "Build a Plugin"
slug: /developer-guide/plugins
title: "Build a Hermes Plugin"
description: "Step-by-step guide to building a complete Hermes plugin with tools, hooks, data files, and skills"
---

# 构建 Hermes 插件

本指南将引导您从零开始构建一个功能完备的 Hermes 插件。完成学习后，您将拥有一个具备多种工具、生命周期钩子、已打包的数据文件以及内置技能的可用插件——涵盖了插件系统支持的所有功能。

:::info 不确定需要哪份指南？
Hermes 提供了多种不同的可插接接口——有些使用 Python 的 `register_*` API，有些则基于配置文件或直接放入指定目录即可使用。建议您先参考此对照表：

| If you want to add… | Read |
|---|---|
| Custom tools, hooks, slash commands, skills, or CLI subcommands | **This guide** (the general plugin surface) |
| A **native desktop app** extension (panes, pages, status bar, palette, themes) | [Desktop Plugin SDK](/developer-guide/desktop-plugin-sdk) |
| A **web dashboard** extension (tabs, shell slots, themes) | [Extending the Dashboard](/user-guide/features/extending-the-dashboard) |
| An **LLM / inference backend** (new provider) | [Model Provider Plugins](/developer-guide/model-provider-plugin) |
| A **gateway channel** (Discord/Telegram/IRC/Teams/etc.) | [Adding Platform Adapters](/developer-guide/adding-platform-adapters) |
| A **memory backend** (Honcho/Mem0/Supermemory/etc.) | [Memory Provider Plugins](/developer-guide/memory-provider-plugin) |
| A **context-compression engine** | [Context Engine Plugins](/developer-guide/context-engine-plugin) |
| An **image-generation backend** | [Image Generation Provider Plugins](/developer-guide/image-gen-provider-plugin) |
| A **video-generation backend** | [Video Generation Provider Plugins](/developer-guide/video-gen-provider-plugin) |
| A **web-search / extract backend** | [Web Search Provider Plugins](/developer-guide/web-search-provider-plugin) |
| A **cloud browser backend** (Browserbase-style CDP session provider) | [Browser Provider Plugins](/developer-guide/browser-provider-plugin) |
| A **secret-manager backend** (vault / password manager / OS keystore) | [Secret Source Plugins](/developer-guide/secret-source-plugin) |
| A **dashboard OIDC/auth provider** | [Web Dashboard — custom providers](/user-guide/features/web-dashboard#custom-providers) — `ctx.register_dashboard_auth_provider()` |
| A **TTS backend** (any CLI — Piper, VoxCPM, Kokoro, voice cloning, …) | [TTS custom command providers](/user-guide/features/tts#custom-command-providers) — config-driven, no Python needed |
| An **STT backend** (custom whisper / ASR CLI) | [Voice Message Transcription](/user-guide/features/tts#voice-message-transcription-stt) — set `HERMES_LOCAL_STT_COMMAND` to an argv-tokenized template |
| **External tools via MCP** (filesystem, GitHub, Linear, any MCP server) | [MCP](/user-guide/features/mcp) — declare `mcp_servers.<name>` in `config.yaml` |
| **Gateway event hooks** (fire on startup, session events, commands) | [Event Hooks](/user-guide/features/hooks#gateway-event-hooks) — drop `HOOK.yaml` + `handler.py` into `~/.hermes/hooks/<name>/` |
| **Shell hooks** (run a shell command on events) | [Shell Hooks](/user-guide/features/hooks#shell-hooks) — declare under `hooks:` in `config.yaml` |
| **Additional skill sources** (custom GitHub repos, private skill indexes) | [Skills](/user-guide/features/skills) — `hermes skills tap add <repo>` · [Publishing a tap](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| A first-class **core** inference provider (not a plugin) | [Adding Providers](/developer-guide/adding-providers) |

如需查看包括配置驱动型（TTS、STT、MCP、shell hooks）以及即插即用型目录（gateway hooks）在内的所有扩展接口的完整列表，请参阅[可插件化接口表](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each)。
:::

:::注意 第三方产品插件以独立形式提供——不会被整合到核心代码库中
那些集成**其他方产品或项目**的插件——如可观测性/指标后端、供应商SaaS连接器、分析仪表板以及付费服务接口——均作为**独立的插件仓库**进行开发与分发，而不会被合并进`NousResearch/hermes-agent`中。用户可将这些插件安装到`~/.hermes/plugins/`目录中，或通过pip命令进行安装；本指南中的所有操作方式对独立仓库也同样适用。这一设计属于耦合度与维护性方面的考量（核心代码更新速度快，且我们并不掌控您的后端系统），而非质量标准——一个优秀的插件依然可以拥有独立的仓库。欢迎在Nous Research的Discord频道`#plugins-skills-and-skins`中推荐此类插件。具体政策请参阅[CONTRIBUTING.md](https://github.com/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md)。
:::

## 可移植Agent插件v1包

Hermes还可以安装和加载针对Agent设计的、采用插件v1.0.0格式的目录包。这类包实际上是为Hermes已有的可移植组件准备的兼容适配层，它并不能替代传统的`plugin.yaml`加上`register(ctx)`结构的插件。

```text
my-portable-plugin/
├── plugin.json
├── skills/
│   └── summarize/
│       ├── SKILL.md
│       └── references/
└── mcp.json
```

通过常规工作流程安装并激活便携式包：

```bash
hermes plugins install owner/repository --no-enable
hermes plugins list
hermes plugins enable <plugin-name>
```

安装完成后，除非您明确启用，否则便携式包将会被禁用。已启用的包会直接提供 `skills/*/SKILL.md` 目录以及根目录下的 `mcp.json` 中定义的 stdio MCP 服务器。这些技能为只读性质、具有命名空间，并通过 `skills_list` 和 `skill_view` 机制进行加载。MCP 命令会作为一个完整的可执行令牌传递，附带独立的参数列表，绝不会通过 shell 执行。您可以使用 `skills_list` 来获取完整的技能全限定名称。便携式技能的命名空间采用 `agent-plugin-<slug>-<hash>` 这一固定格式，该格式源自所检测到的插件键，因此经过处理后的名称不会发生冲突。

Hermes 会在本地对 `plugin.json`、Agent Skills 的前置信息、固定组件位置、`mcp.json`、解析后的路径以及符号链接内容进行验证。在加载包时，它不会主动获取 JSON 规范文件。即便存在无效的技能或 MCP 条目，只要其相邻的有效组件仍可加载，这些无效项也会在其所在边界处被跳过。`PLUGIN_ROOT` 指向已解析的包根目录，而 `PLUGIN_DATA` 则指向由 Hermes 管理的、具有用户配置上下文作用域的可写目录。在便携式 MCP 的 `env` 中声明的值属于可查看的包数据，并非用于存储机密信息的机制，请勿在 `mcp.json` 中存放任何凭证信息。

当前的可移植子集支持 stdio 以及 Streamable HTTP MCP 接口。对于可移植的 `streamable-http` 接口，系统会通过 Hermes 内置的原生远程 MCP 客户端来处理（该客户端与基于 URL 的 `mcp_servers` 配置所使用的运行时相同），并严格遵循 v1 版的规则：URL 必须为不含用户信息或片段标识的绝对 http(s) 地址，仅允许对 `localhost`/回环主机使用纯 HTTP 协议，且配置的请求头绝不会在跨域重定向过程中被转发。而旧版的 `sse` 接口则会被识别但直接跳过处理。Agent Plugins v1 版并未定义信任机制、权限设置、来源追溯功能或沙箱环境。启用某个软件包后，其指令及本地可执行文件将享有与其他已安装的 Hermes 插件相同的完全信任级别。

目前的[规范文档](https://agent-plugins.org/specification)将 v1.0.0 版标记为“工作草案”，而[版本化的规范仓库](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)则将其列为“已发布”状态。Hermes 的行为是基于标准的 v1.0.0 架构标识与规范文本来确定的，而非那些可变的状态标签。这属于明确支持的可移植子集，并不意味着该版本完全符合 Agent Plugins 的所有要求。

## 原生插件兼容性契约

原生 `plugin.yaml` 插件以及通过 `register(ctx)` 注册的插件均通过特定的行为机制来实现保护，而非依赖单一的全局插件 API 编号。Hermes 并不会暴露 `PLUGIN_API_VERSION`，也不要求在整个清单中统一指定 `api:` 参数，更不会为无关字段附加 API 版本信息。只要遵循既定行为规范开发的插件，在进行常规的 Hermes 升级后仍能正常运行。

其兼容性规则如下：

- **以增量方式演进**：已文档化的 `PluginContext` 方法既不会被移除也不会被重命名。新添加的参数为可选类型，且会提供默认值，同时仅以关键字形式存在。现有的返回字段既不会被移除，也不会被隐式更改类型。
- **钩子函数的载荷为关键字格式**：新的钩子数据将以关键字字段的形式添加，绝不会通过改变现有字段的含义或位置来实现。Hermes 会检查回调函数的签名：传统回调函数仅能接收其声明的字段，而使用 `**kwargs` 的回调函数则可以接收当前所有的载荷数据。新插件应支持 `**kwargs`，这样无需再次修改签名即可获取新增的数据。
- **清单结构支持扩展**：未知的 `plugin.yaml` 字段会被忽略。因此，旧版本的 Hermes 仍可加载那些清单中包含较新版本所引入元数据的插件，前提是该插件本身的代码使用了受支持的运行时行为机制。
- **提供程序接口通过默认值逐步扩展。**新的提供程序方法会拥有默认实现方式，而新的回调上下文则是可选的，仅当签名检查表明该提供程序支持时才会被传递。若要添加抽象方法或需无条件传递的参数，则需要设置迁移窗口，而非仅在某个特定版本中立即修改签名。
- **对跨边界使用的接口进行版本控制。**当某个功能定义了数据传输格式或持久化存储格式（例如观察者发送的数据或密钥源状态）时，该功能可拥有独立的架构版本。在此局部架构中，应确保各字段为可累加的类型。已持久化的插件状态与配置必须保持可读取性，否则需提供明确的迁移方案；同时，以旧格式保存的会话仍需能够被重新加载。切勿在无关的回调参数或上下文值中添加版本标识。

### 废弃策略

只有满足以下所有条件，文档中记载的原生插件行为方可被废弃：
1. 在插件指南及版本说明中提供替代方案及迁移指导；
2. 每个进程最多触发一次警告，明确指出替代方案以及最早取消该行为的版本；
3. 在至少两个后续的小版本中继续支持旧行为；
4. 在整个过渡期内，针对旧路径及替代路径均需确保行为层面的兼容性。

在过渡期结束后进行废弃时，必须处理所有与持久化数据或可恢复会话相关的迁移工作。在实际应用中，优先采用新增别名或适配器的方式，而非直接废弃原有功能。

Hermes 会通过从隔离的 `HERMES_HOME` 环境中发现的已冻结外部插件固定配置来强制执行这一契约。这些测试会通过 `PluginManager` 加载并调用插件，进而验证插件的实际注册情况与回调结果，而非内部符号列表或源代码结构。

### 2026年9月：模块拆分——旧导入路径将于2026-09-14停止使用

2026年9月，Hermes 的内部架构被拆分为 `<stem>_<topic>` 格式的独立模块（PR #102117）。上述插件契约中从未规定过内部导入路径，但许多插件仍在使用它们。在 **2026-09-14** 之前，所有被迁移的名称仍能从旧模块中解析；此后该兼容层将被移除。

- **检查您的插件：** 运行 `hermes plugins compat /path/to/your/plugin` 命令即可列出所有包含旧路径与新路径对应关系的 `file:line` 信息，若仍有匹配项存在则命令会以状态码1退出。仓库中的 `COMPAT_MANIFEST.md` 文件则提供了完整的映射关系。
- **用户可见提示：** 在 CLI 启动界面下方、`hermes doctor` 命令输出中以及 `hermes update` 操作完成后，都会显示相关提示信息；同时还会弹出一次性的桌面对话框标注插件名称。每次通过旧路径进行解析时，每个进程还会生成一条 `HermesPluginCompatWarning` 警告。
- **2026-09-14之后：** 仍使用旧导入路径的插件将**无法被加载**（`hermes plugins list` 命令会显示具体原因）。用户可通过设置 `plugins.allow_deprecated_imports: true` 强制加载这些插件，直到该兼容层真正被移除，届时旧路径将会引发 `ImportError` 错误。

## 您正在构建的内容

一个包含两种工具的**计算器**插件：
- `calculate` — 计算数学表达式（如 `2**16`、`sqrt(144)`、`pi * 5**2`）
- `unit_convert` — 实现单位转换（如 `100 F → 37.78 C`、`5 km → 3.11 mi`）

此外，该插件还包含一个用于记录每次工具调用的钩子函数，以及一个预置的技能文件。

## 第一步：创建插件目录

首先创建一个目录，然后继续执行第二步：

```bash
mkdir -p ~/.hermes/plugins/calculator
cd ~/.hermes/plugins/calculator
```

### 使用 Plugin Doctor 进行验证

`hermes plugins doctor [路径或标识符]` 会使用 Hermes 本身所采用的相同机制，包括目录扫描、清单解析、命名空间导入、`register(ctx)` 函数、钩子注册表以及工具注册表。该命令能够检测出无效的钩子名称、未接受 `**kwargs` 参数的回调函数、注册失败的情况，以及声明的工具/钩子与实际注册内容之间的不一致之处。如需在检测到错误时以非零状态退出，可添加 `--ci` 参数：

```bash
hermes plugins doctor . --ci
```

Doctor会使用一个临时的`HERMES_HOME`目录，在检查完成后恢复插件的注册状态，同时阻止直接的Python套接字连接，以避免在注册过程中发生意外的网络访问。需要注意的是，这并非沙箱环境：插件代码仍会在当前用户的权限下在进程内执行，并且能够创建子进程，因此请仅在您完全信任、愿意导入的代码上运行Doctor。

## 第2步：编写清单文件

创建`plugin.yaml`文件：

```yaml
name: calculator
version: 1.0.0
description: Math calculator — evaluate expressions and convert units
provides_tools:
  - calculate
  - unit_convert
provides_hooks:
  - post_tool_call
```

这向 Hermes 告诉它：“我是一个名为 calculator 的插件，可提供各类工具与钩子功能。”`provides_tools` 和 `provides_hooks` 字段分别列出了该插件所注册的工具和钩子。您还可以添加可选字段：
```yaml
author: Your Name
requires_env:          # gate loading on env vars; prompted during install
  - SOME_API_KEY       # simple format — plugin disabled if missing
  - name: OTHER_KEY    # rich format — shows description/url during install
    description: "Key for the Other service"
    url: "https://other.com/keys"
    secret: true
capabilities:          # privileged host surfaces you request (consent flow)
  - tools.override     # replace built-in tools (needs user consent)
  - llm.model_override # choose the model for host-owned LLM calls
```

### 声明功能能力

如果您的插件需要特殊的宿主权限——例如覆盖内置工具、为 `ctx.llm` 调用选择模型等——请在 `capabilities:` 中进行声明。在安装或启用时，用户会看到该功能列表并予以同意；若后续版本新增了某种功能能力，更新流程只会再次请求用户对新增项进行授权。未被声明或未获授权的功能能力将直接被禁用（即立即拒绝运行），因此**请在使用前先进行测试，并做好降级处理**：

```python
def register(ctx):
    if ctx.has_capability("tools.override"):
        ctx.register_tool(..., override=True)
    else:
        ctx.register_tool(...)   # register under a non-conflicting name
```

已知的 capability ID 包括：`tools.override`、`llm.provider_override`、`llm.model_override`、`llm.agent_id_override`、`llm.profile_override` 以及 `llm.task_override`（标准列表请参阅 `hermes_cli/plugin_capabilities.py`）。未知的 ID 将被忽略。虽然旧的逐个 capability 的配置键（如 `plugins.entries.<id>.allow_tool_override` 等）仍然有效，但已处于废弃状态——建议直接声明 capability，这样用户只需面对一个统一的、可审计的同意界面。Capability 用于实现同意管理及审计功能，**并非沙箱机制**：它仅用于控制主机 API 的访问权限，仅此而已。

**通过 Pip 分发的插件**在安装完成后不会包含 `plugin.yaml` 目录，因此需通过配套的 `hermes_agent.plugin_capabilities` 入口点组，在分发元数据中声明 capability。每条声明的名称格式为 `<plugin-id>.<capability-id>`，且指向的内容与 `hermes_agent.plugins` 入口点所指向的对象相同。

```toml
[project.entry-points."hermes_agent.plugins"]
calculator = "my_pkg:register"

[project.entry-points."hermes_agent.plugin_capabilities"]
"calculator.tools.override" = "my_pkg:register"
```

Hermes 会直接从已安装的元数据中读取这些信息，而无需导入您的代码，因此对于通过 pip 安装的插件而言，`hermes plugins capabilities` 的显示内容以及相关授权流程都能保持准确。

### Manifest v2 参考规范

`plugin.yaml` 还支持一种可扩展的 **v2 架构**（#64165）。所有字段均为可选项；若清单中未指定 `manifest_version`，则视为 v1 版本清单，且将永远获得完全支持。对于未知字段，系统不会因此导致加载失败——它们会被忽略并伴随警告信息（以实现向后兼容），而版本号高于当前版本的 `manifest_version`，Hermes 也能在发出警告的情况下继续加载。

| Field | Type | Meaning |
|---|---|---|
| `manifest_version` | int | Manifest **file-format** version. Absent = `1`. Current max: `2`. Independent from `api_version`. |
| `api_version` | int | Runtime **plugin API generation** the plugin targets (ctx surface / hook signatures). Deliberately a separate axis from `manifest_version` — an `api_version: 1` plugin can use a v2 manifest. |
| `requires_plugins` | list | Inter-plugin dependencies: `- id: other-plugin` with optional `version_range: ">=1.0,<2"`. **Advisory**: a missing dependency logs a clear warning but the plugin still loads — probe at runtime with `ctx.has_plugin("other-plugin")`. Load **order** honors these edges: when A requires B, B's `register()` runs before A's (topological sort, alphabetical tiebreak; cycles warn and fall back to alphabetical order). |
| `python_dependencies` | list of str | Declared pip requirements (e.g. `"requests>=2.0,<3"`). **Declaration seam only** — Hermes validates them, and `hermes plugins install` / `hermes plugins doctor` surface missing ones with a `pip install` hint, but Hermes **never auto-installs** them. Pin upper bounds. |
| `config_schema` | mapping | JSON-schema-ish description of keys under `plugins.entries.<id>.settings`: `api_url: {type: str, default: "", description: "...", required: false}`. Validated at load; mismatches log actionable warnings naming the key and expected type — never load failures. Types: `str`, `int`, `float`, `bool`, `list`, `dict` (plus JSON-schema aliases). |
| `license` | str | SPDX-style license id (e.g. `MIT`). |
| `homepage` | str | Project URL. |
| `tags` | list of str | Free-form discovery tags (e.g. `[gateway, telegram]`). |

```yaml
# plugin.yaml — manifest v2 example
name: my-plugin
version: 1.2.0
manifest_version: 2
api_version: 1
license: MIT
homepage: https://github.com/owner/my-plugin
tags: [gateway, demo]
requires_plugins:
  - id: other-plugin
    version_range: ">=1.0,<2"
python_dependencies:
  - "somepkg>=1.0,<2"     # surfaced, never auto-installed
config_schema:
  api_url: {type: str, default: "", description: "Service endpoint"}
```

:::注意：依赖项隔离功能暂未实现  
`python_dependencies` 仅被设计为用于声明和展示用途。将任意包安装到 Hermes 的共享虚拟环境中会导致冲突及供应链问题，因此针对安装过程的隔离设计（通过约束文件限制主机锁定、按插件划分独立虚拟环境，以及冲突检测与自动拒绝机制）目前被明确推迟处理——相关讨论可见 [#64165](https://github.com/NousResearch/hermes-agent/issues/64165) 和 [#15220](https://github.com/NousResearch/hermes-agent/issues/15220) 的第二轮评审。插件包的构建（#64166）将基于这些 v2 版的功能实现。  
:::

## 第3步：编写工具架构定义文件  

创建 `schemas.py` —— LLM 会读取该文件来决定何时调用您的工具：

```python
"""Tool schemas — what the LLM sees."""

CALCULATE = {
    "name": "calculate",
    "description": (
        "Evaluate a mathematical expression and return the result. "
        "Supports arithmetic (+, -, *, /, **), functions (sqrt, sin, cos, "
        "log, abs, round, floor, ceil), and constants (pi, e). "
        "Use this for any math the user asks about."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate (e.g., '2**10', 'sqrt(144)')",
            },
        },
        "required": ["expression"],
    },
}

UNIT_CONVERT = {
    "name": "unit_convert",
    "description": (
        "Convert a value between units. Supports length (m, km, mi, ft, in), "
        "weight (kg, lb, oz, g), temperature (C, F, K), data (B, KB, MB, GB, TB), "
        "and time (s, min, hr, day)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "The numeric value to convert",
            },
            "from_unit": {
                "type": "string",
                "description": "Source unit (e.g., 'km', 'lb', 'F', 'GB')",
            },
            "to_unit": {
                "type": "string",
                "description": "Target unit (e.g., 'mi', 'kg', 'C', 'MB')",
            },
        },
        "required": ["value", "from_unit", "to_unit"],
    },
}
```

**为何架构设计如此重要：** `description` 字段决定了大语言模型何时会调用您的工具。请清晰地描述该工具的功能及其适用场景。而 `parameters` 则用于指定大语言模型需要传递的参数。

## 第 4 步：编写工具处理函数

创建 `tools.py` 文件——当大语言模型调用您的工具时，正是这段代码被实际执行：

```python
"""Tool handlers — the code that runs when the LLM calls each tool."""

import json
import math

# Safe globals for expression evaluation — no file/network access
_SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "log": math.log, "log2": math.log2, "log10": math.log10,
    "floor": math.floor, "ceil": math.ceil,
    "pi": math.pi, "e": math.e,
    "factorial": math.factorial,
}


def calculate(args: dict, **kwargs) -> str:
    """Evaluate a math expression safely.

    Rules for handlers:
    1. Receive args (dict) — the parameters the LLM passed
    2. Do the work
    3. Return a JSON string — ALWAYS, even on error
    4. Accept **kwargs for forward compatibility
    """
    expression = args.get("expression", "").strip()
    if not expression:
        return json.dumps({"error": "No expression provided"})

    try:
        result = eval(expression, {"__builtins__": {}}, _SAFE_MATH)
        return json.dumps({"expression": expression, "result": result})
    except ZeroDivisionError:
        return json.dumps({"expression": expression, "error": "Division by zero"})
    except Exception as e:
        return json.dumps({"expression": expression, "error": f"Invalid: {e}"})


# Conversion tables — values are in base units
_LENGTH = {"m": 1, "km": 1000, "mi": 1609.34, "ft": 0.3048, "in": 0.0254, "cm": 0.01}
_WEIGHT = {"kg": 1, "g": 0.001, "lb": 0.453592, "oz": 0.0283495}
_DATA = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
_TIME = {"s": 1, "ms": 0.001, "min": 60, "hr": 3600, "day": 86400}


def _convert_temp(value, from_u, to_u):
    # Normalize to Celsius
    c = {"F": (value - 32) * 5/9, "K": value - 273.15}.get(from_u, value)
    # Convert to target
    return {"F": c * 9/5 + 32, "K": c + 273.15}.get(to_u, c)


def unit_convert(args: dict, **kwargs) -> str:
    """Convert between units."""
    value = args.get("value")
    from_unit = args.get("from_unit", "").strip()
    to_unit = args.get("to_unit", "").strip()

    if value is None or not from_unit or not to_unit:
        return json.dumps({"error": "Need value, from_unit, and to_unit"})

    try:
        # Temperature
        if from_unit.upper() in {"C","F","K"} and to_unit.upper() in {"C","F","K"}:
            result = _convert_temp(float(value), from_unit.upper(), to_unit.upper())
            return json.dumps({"input": f"{value} {from_unit}", "result": round(result, 4),
                             "output": f"{round(result, 4)} {to_unit}"})

        # Ratio-based conversions
        for table in (_LENGTH, _WEIGHT, _DATA, _TIME):
            lc = {k.lower(): v for k, v in table.items()}
            if from_unit.lower() in lc and to_unit.lower() in lc:
                result = float(value) * lc[from_unit.lower()] / lc[to_unit.lower()]
                return json.dumps({"input": f"{value} {from_unit}",
                                 "result": round(result, 6),
                                 "output": f"{round(result, 6)} {to_unit}"})

        return json.dumps({"error": f"Cannot convert {from_unit} → {to_unit}"})
    except Exception as e:
        return json.dumps({"error": f"Conversion failed: {e}"})
```

**处理程序的核心规则：**
1. **函数签名：** `def my_handler(args: dict, **kwargs) -> str`
2. **返回值：** 必须始终返回 JSON 字符串，无论是成功响应还是错误信息。
3. **禁止抛出异常：** 需捕获所有异常，并返回对应的错误 JSON。
4. **支持 `**kwargs` 参数：** Hermes 未来可能会传递额外的上下文信息。

## 第 5 步：编写注册代码

创建 `__init__.py` 文件——该文件用于将架构模式与处理程序关联起来：

```python
"""Calculator plugin — registration."""

import logging

from . import schemas, tools

logger = logging.getLogger(__name__)

# Track tool usage via hooks
_call_log = []

def _on_post_tool_call(tool_name, args, result, task_id, **kwargs):
    """Hook: runs after every tool call (not just ours)."""
    _call_log.append({"tool": tool_name, "session": task_id})
    if len(_call_log) > 100:
        _call_log.pop(0)
    logger.debug("Tool called: %s (session %s)", tool_name, task_id)


def register(ctx):
    """Wire schemas to handlers and register hooks."""
    ctx.register_tool(name="calculate",    toolset="calculator",
                      schema=schemas.CALCULATE,    handler=tools.calculate)
    ctx.register_tool(name="unit_convert", toolset="calculator",
                      schema=schemas.UNIT_CONVERT, handler=tools.unit_convert)

    # This hook fires for ALL tool calls, not just ours
    ctx.register_hook("post_tool_call", _on_post_tool_call)
```

**`register()` 的功能：**  
- 在启动时仅调用一次  
- `ctx.register_tool()` 会将您的工具注册到注册表中，模型可立即识别到它  
- `ctx.register_hook()` 用于订阅生命周期事件  
- `ctx.register_cli_command()` 用于注册 CLI 子命令（例如 `hermes my-plugin <subcommand>`）  
- `ctx.register_command()` 用于注册会话内的斜杠命令（例如在 CLI 或网关聊天中使用的 `/myplugin <args>`）——详情请参阅下文的[注册斜杠命令](#register-slash-commands)  
- `ctx.dispatch_tool(name, arguments)` —— 可以使用父代理的上下文（包括审批权限、凭证及 task_id）来调用任何其他工具（无论是内置工具还是来自其他插件的工具），实现自动关联。这对于需要像模型直接调用一样使用 `terminal`、`read_file` 或其他工具的斜杠命令处理程序非常有用。  
- `ctx.get_config()` / `ctx.set_config()` 仅能访问该插件自身的设置空间；`ctx.state` 则用于存储当前激活配置文件下属于该插件的运行时数据。  
- 若该函数发生崩溃，该插件将被禁用，但 Hermes 仍可正常运行。  

**`dispatch_tool` 示例——一个用于执行工具的斜杠命令：**

```python
def handle_scan(ctx, raw_args: str):
    """Implement /scan by invoking the terminal tool through the registry."""
    result = ctx.dispatch_tool("terminal", {"command": f"find . -name '{raw_args}'"})
    return result  # returned to the caller's chat UI

def register(ctx):
    # Handlers receive a single raw_args string; close over ctx via a lambda.
    ctx.register_command(
        "scan",
        lambda raw: handle_scan(ctx, raw),
        description="Find files matching a glob",
    )
```

被调用的工具会经过常规的审批、脱敏以及预算审核流程——这属于真正的工具调用，而非绕过这些流程的捷径。

### 商店设置与运行时状态

对于用户可见的行为配置，应使用基于插件的配置键。Hermes会在这类配置键位于`plugins.entries.<plugin-id>.settings`路径下进行解析，并拒绝全局配置、跨插件配置以及层级嵌套的配置路径：

```python
def register(ctx):
    endpoint = ctx.get_config("endpoint", default="https://example.invalid")
    retries = ctx.get_config("retry.attempts", default=3)

    ctx.set_config("endpoint", endpoint)
    ctx.set_config("retry.attempts", retries)
```

对于由插件管理的光标、缓存及去重数据，请使用 `ctx.state` 来存储，而非将相关的运行时记录放在 `config.yaml` 中。

```python
def register(ctx):
    cursor = ctx.state.get("cursor", default={"page": 0})
    ctx.state.set("cursor", {"page": cursor["page"] + 1})
```

状态数据具有配置文件作用域，会以原子方式被替换，可在多线程写入场景下保持安全，并且每个插件对应的状态大小上限为10 MiB。可移植包与其`PLUGIN_DATA`目录位于同一位置；而原生插件则拥有抗冲突、兼容Windows系统的命名空间。系统会报告并保留格式错误的现有状态数据。

配置与状态数据的归属不同：`config.yaml`中的设置是用户可见的行为配置，而状态数据则是存储在`<HERMES_HOME>/plugin-data/`下的、由相应插件管理的运行时数据。两种API均不会暴露其他插件的命名空间。

## 第6步：进行测试

启动Hermes：

```bash
hermes
```

在横幅显示的工具列表中，您应该能看到 `calculator: calculate, unit_convert` 这些选项。

可以尝试使用以下提示词：
```
What's 2 to the power of 16?
Convert 100 fahrenheit to celsius
What's the square root of 2 times pi?
How many gigabytes is 1.5 terabytes?
```

查看插件状态：
```
/plugins
```

输出：
```
Plugins (1):
  ✓ calculator v1.0.0 (2 tools, 1 hooks)
```

### 调试插件发现问题

如果您的插件未出现，或虽已出现但无法加载，请将 `HERMES_PLUGINS_DEBUG=1` 设置为该值，即可在标准错误流中获取详细的插件发现日志：

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```

对于每一个插件来源（已打包、用户自定义、项目自用以及入口点），您将看到以下信息：

- 已扫描的目录及其各自生成的清单数量；
- 每个清单的详细内容：解析后的键值、名称、类型、来源以及磁盘路径；
- 跳过该插件的原因：`通过配置禁用`、`配置中未启用`、`为专用插件`、`无plugin.yaml文件或达到深度限制`；
- 加载时的信息：正在导入的插件，以及`register(ctx)`函数所注册内容的简要总结（工具、钩子、斜杠命令、CLI命令）；
- 解析失败时的信息：异常的完整堆栈跟踪信息（如YAML解析错误等）；
- `register()`函数调用失败时的信息：指向`__init__.py`文件中引发错误的那一行的完整堆栈跟踪。

这些日志始终会被记录到`~/.hermes/logs/agent.log`文件中。默认情况下，错误信息以WARNING级别输出，而所有信息则在设置了环境变量时以DEBUG级别输出。因此，如果您无法通过设置环境变量来运行程序（例如在网关内部），可以直接查看该日志文件的内容。

```bash
hermes logs --level WARNING | grep -i plugin
```

插件未显示的常见原因：

- **配置中未启用**——插件为可选功能。请运行 `hermes plugins enable <name>` 命令（名称取自 `plugins list` 的输出结果，对于嵌套结构，格式可能为 `<category>/<plugin>`）。
- **目录结构错误**：原生插件包使用 `~/.hermes/plugins/<plugin-name>/plugin.yaml` 文件（扁平结构）或仅一个分类层级。可移植插件包则在同一位置使用根级的 `plugin.json` 文件，更深层的目录将被忽略。
- **缺少 `__init__.py` 文件**：原生插件包必须同时具备 `plugin.yaml` 文件以及包含 `register(ctx)` 函数的 `__init__.py` 文件。而可移植插件包无需导入 Python 代码，因此也不需要 `__init__.py` 文件。
- **`kind` 类型设置错误**——网关适配器在其清单文件中需指定 `kind: platform`。内存提供器则会自动被识别为 `kind: exclusive`，并通过 `memory.provider` 配置项进行路由，而非通过 `plugins.enabled` 选项。

## 您插件最终的目录结构

```
~/.hermes/plugins/calculator/
├── plugin.yaml      # "I'm calculator, I provide tools and hooks"
├── __init__.py      # Wiring: schemas → handlers, register hooks
├── schemas.py       # What the LLM reads (descriptions + parameter specs)
└── tools.py         # What runs (calculate, unit_convert functions)
```

四个文件，分工明确：
- **Manifest**用于说明插件的功能
- **Schemas**用于描述面向大语言模型的工具
- **Handlers**负责实现实际逻辑
- **Registration**则负责将各部分相互关联

## 插件还能实现哪些功能？

### 上传数据文件

只需将任意文件放入插件目录中，即在导入时自动读取这些文件：

```python
# In tools.py or __init__.py
from pathlib import Path

_PLUGIN_DIR = Path(__file__).parent
_DATA_FILE = _PLUGIN_DIR / "data" / "languages.yaml"

with open(_DATA_FILE) as f:
    _DATA = yaml.safe_load(f)
```

那指的是您*上传*的文件。而*编写*的文件则属于另一情况——详情请见下一节。

### 存储持久化状态

切勿将运行时状态写入插件目录：该目录属于安装树结构，当执行 `hermes plugins update` 或 `remove` 命令进行 Git 拉取或删除操作时，其中的数据将会一同丢失，导致用户数据也随之消失。正确的存储位置是每个插件专用的数据根目录，这类数据能够在这两种操作中得以保留，并会随当前激活的配置文件一同存在。

```python
from plugins.plugin_storage import plugin_data_dir, plugin_db

# <hermes home>/plugin-data/<name>/ — created on first use
state_file = plugin_data_dir("my-plugin") / "state.json"

# Or a SQLite database at <data dir>/data.db (WAL mode, thread-friendly)
conn = plugin_db("my-plugin")
conn.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY)")
```

每个插件对应一个目录，这样所有插件的数据都能在同一个易于查找的位置被查看。敏感信息不应存储于此——与其它地方一样，凭证读取操作会通过标准的 `.env` 或专用密钥管理路径来处理。

### 打包技能

插件可以提供技能文件，Agent 可通过 `skill_view("plugin:skill")` 来加载这些文件。请在您的 `__init__.py` 文件中对其进行注册：

```
~/.hermes/plugins/my-plugin/
├── __init__.py
├── plugin.yaml
└── skills/
    ├── my-workflow/
    │   └── SKILL.md
    └── my-checklist/
        └── SKILL.md
```

```python
from pathlib import Path

def register(ctx):
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)
```

该智能体现在能够使用命名空间名称来加载您的技能了：

```python
skill_view("my-plugin:my-workflow")   # → plugin's version
skill_view("my-workflow")              # → built-in version (unchanged)
```

**关键属性：**
- 插件技能为**只读**属性——它们不会被写入 `~/.hermes/skills/` 目录，也无法通过 `skill_manage` 命令进行编辑。
- 插件技能**不会**出现在系统提示中的 `<available_skills>` 列表中——它们需要通过显式方式手动加载。
- 纯技能名称不受影响——命名空间可避免其与内置技能发生冲突。
- 当智能体加载插件技能时，系统会在开头显示一个捆绑上下文标识，列出同一插件下的其他相关技能。

:::提示 传统模式
旧的 `shutil.copy2` 模式（即将技能复制到 `~/.hermes/skills/` 目录）仍然可用，但存在与内置技能名称冲突的风险。建议在新插件开发中优先使用 `ctx.register_skill()` 方法。
:::

### 基于环境变量的限制

如果您的插件需要 API 密钥：

```yaml
# plugin.yaml — simple format (backwards-compatible)
requires_env:
  - WEATHER_API_KEY
```

如果未设置 `WEATHER_API_KEY`，该插件将会被禁用，并同时显示明确的提示信息。代理程序不会崩溃也不会报错，只会显示“插件 weather 已禁用（缺少：WEATHER_API_KEY）”。

当用户运行 `hermes plugins install` 命令时，系统会**以交互方式**提示他们补充所有缺失的 `requires_env` 变量。这些值会自动保存到 `.env` 文件中。

为获得更佳的安装体验，建议使用包含描述和注册链接的富格式来配置插件。

```yaml
# plugin.yaml — rich format
requires_env:
  - name: WEATHER_API_KEY
    description: "API key for OpenWeather"
    url: "https://openweathermap.org/api"
    secret: true
```

| 字段 | 是否必填 | 描述 |
|-------|----------|-------------|
| `name` | 是 | 环境变量名称 |
| `description` | 否 | 安装提示时显示给用户的说明文字 |
| `url` | 否 | 获取凭证的地址 |
| `secret` | 否 | 若值为 `true`，输入内容将被隐藏（类似密码字段） |

同一个列表中可以混合使用这两种格式。已设置的变量将会被直接跳过，不会产生任何提示。

### 延迟安装可选的 Python 依赖项

如果您的插件封装了并非所有用户都会安装的 SDK（如第三方 SDK、大型机器学习库或平台专用包），则无需在模块顶部直接 `import` 它。应在工具处理函数中使用 `tools.lazy_deps.ensure(...)` 辅助函数——Hermes 会根据用户配置的 `security.allow_lazy_installs` 设置，在首次使用时自动安装该包。

```python
# tools.py
from tools.lazy_deps import ensure, FeatureUnavailable

def my_tool_handler(args, **kwargs):
    try:
        ensure("my-plugin.my-backend")   # key must be in LAZY_DEPS
    except FeatureUnavailable as exc:
        return {"error": str(exc)}

    import my_backend_sdk   # safe now
    ...
```

`tools/lazy_deps.py` 中安全模型规定的两条规则如下：

| 规则 | 原因 |
|---|---|
| 您的功能密钥必须出现在树内的 `LAZY_DEPS` 允许列表中 | 防止恶意配置诱使 Hermes 安装任意包——只有 Hermes 自身提供的依赖项才被允许 |
| 依赖项仅能通过 PyPI 名称指定 | 不支持使用 `--index-url`、`git+https://` 或文件路径。应在允许列表条目中使用 PEP 440 格式指定版本号（如 `"my-sdk>=1.2,<2"`） |

对于通过 pip 分发的第三方插件，可将可选依赖项作为 `[project.optional-dependencies]` 附加项声明在您自己的 `pyproject.toml` 文件中，并告知用户使用 `pip install your-plugin[backend]` 命令进行安装——该路径不会经过 `lazy_deps` 处理。延迟安装机制最适用于**已打包**的插件，因为若每次安装都附带硬依赖项，会增大 Hermes 的整体体积。

当全局设置为 `security.allow_lazy_installs: false` 时，`ensure()` 函数会立即抛出 `FeatureUnavailable` 异常，并附上解决方案提示——您的插件应捕获该异常并实现优雅降级（返回错误结果，而非导致工具循环崩溃）。

### 线程安全的延迟单例

插件通常会在首次使用时，通过模块级变量缓存一个成本较高的对象——如 SDK 客户端、HTTP 会话或连接池。

```python
_client = None

def get_client():
    global _client
    if _client is not None:
        return _client
    _client = ExpensiveClient(...)   # ← TOCTOU race
    return _client
```

这是一种“枪击式”问题。Hermes 在单个进程内运行多个线程（用于处理委托的工具调用、后台任务以及自我改进分支），因此两个线程都可能在 `_client` 被设置之前就调用了 `get_client()` 方法。这两个线程都会通过“非空值”检查，进而执行代价高昂的构建操作；最终，后执行的线程会覆盖先执行的线程，导致前者所打开的资源（连接、文件句柄或后台线程）被泄露。

切勿自行实现锁机制，请使用 `plugins/plugin_utils.py` 中提供的辅助函数：

```python
from plugins.plugin_utils import lazy_singleton, SingletonSlot

# Zero-arg accessor → decorate it:
@lazy_singleton
def get_client():
    return ExpensiveClient(load_config())   # runs exactly once

client = get_client()    # safe across threads
get_client.reset()       # drop the instance (tests / teardown)


# Accessor that takes a build argument → use a slot:
_slot: SingletonSlot = SingletonSlot()

def get_client(config=None):
    return _slot.get(lambda: ExpensiveClient(resolve(config)))

def reset_client():
    _slot.reset()
```

两者均会通过双重检查锁定机制来序列化首次并发调用，并且最多仅执行一次工厂函数。如果工厂函数抛出异常，则不会进行任何缓存处理，后续调用将会重新尝试。`honcho memory`插件（位于`plugins/memory/honcho/client.py`）即为参考实现。

> 经验法则：每当您写出类似`global _something`、随后进行`is None`检查并再执行构建操作的代码时，建议改用上述方案之一。

### 工具的条件可用性

对于那些依赖可选库的工具：

```python
ctx.register_tool(
    name="my_tool",
    schema={...},
    handler=my_handler,
    check_fn=lambda: _has_optional_lib(),  # False = tool hidden from model
)
```

### 覆盖内置工具

若希望用自定义实现替换内置工具（例如将默认的浏览器工具替换为基于 headed-Chrome CDP 的后端，或用自定义的企业索引替代 `web_search`），请传入 `override=True` 参数：

```python
def register(ctx):
    ctx.register_tool(
        name="browser_navigate",             # same name as the built-in
        toolset="plugin_my_browser",         # your own toolset namespace
        schema={...},
        handler=my_custom_navigate,
        override=True,                       # explicit opt-in
    )
```

若未设置 `override=True`，注册表会拒绝任何可能覆盖来自其他工具集的现有工具的注册操作——此举旨在防止意外覆盖。若要覆盖**内置**工具，操作员还必须在 `config.yaml` 中通过设置 `plugins.entries.<plugin_id>.allow_tool_override: true` 来进行授权；若未开启此选项，调用 `register_tool(override=True)` 将会引发 `PluginToolOverrideError` 错误。此类覆盖操作会被记录在 `~/.hermes/logs/agent.log` 文件中，便于审计。由于插件是在内置工具之后加载的，因此当前的注册顺序是正确的：您的处理程序将替换掉内置版本。

**非内置插件同样需要操作员的授权。** 对于那些并非随 Hermes 核心一起提供的插件（无论是用户级、项目级还是通过 pip 安装的插件），若要覆盖现有的内置工具并设置 `override=True`，还必须在 `config.yaml` 中为每个插件单独开启授权选项：

```yaml
plugins:
  entries:
    my-plugin:                    # the plugin's registry key from `hermes plugins list`
      allow_tool_override: true
```

若未授予相应权限，调用 `ctx.register_tool(..., override=True)` 会引发 `PluginToolOverrideError` 异常；由于 `register()` 方法抛出的异常会被加载器捕获，此时该插件将被禁用，而 Hermes 仍可继续运行。设置此限制是为了防止那些处于启用状态的插件偷偷替换诸如 `shell_exec` 或 `write_file` 这类具有特殊权限的内置功能，从而截获模型通过它传递的所有操作。预置的插件则不受此限制——是否允许对其进行覆盖由维护者自行决定。如果配置文件无法加载，该检查将直接失败。

通常情况下无需手动编辑此键值。执行 `hermes plugins enable <name>` 命令时，系统会询问是否在启用非预置插件时授予相应权限（默认为拒绝），而使用 `--allow-tool-override` 或 `--no-allow-tool-override` 参数则可在脚本化安装时跳过此提示。同样的权限控制也适用于 `deregister()` 方法：若未获得授权，插件便无法移除其并不拥有的工具（否则这将成为绕过权限检查的手段）。

### 注册多个钩子

```python
def register(ctx):
    ctx.register_hook("pre_tool_call", before_any_tool)
    ctx.register_hook("post_tool_call", after_any_tool)
    ctx.register_hook("pre_llm_call", inject_memory)
    ctx.register_hook("on_session_start", on_new_session)
    ctx.register_hook("on_session_end", on_session_end)
```

### 钩子参考文档

每一种钩子的详细信息都记载在**[事件钩子参考文档](/user-guide/features/hooks#plugin-hooks)**中，内容包括回调函数签名、参数表、触发时机以及示例代码。以下为概要介绍：

| Hook | Fires when | Callback signature | Returns |
|------|-----------|-------------------|---------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | Before any tool executes | `tool_name: str, args: dict, task_id: str` | optional directive: `{"action": "block", "message": ...}` vetoes the call; `{"action": "approve", "message": ...}` escalates to the human-approval gate |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | After any tool returns | `tool_name: str, args: dict, result: str, task_id: str, duration_ms: int` | ignored |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | Once per turn, before the tool-calling loop | `session_id: str, user_message: str, conversation_history: list, is_first_turn: bool, model: str, platform: str` | [context injection](#pre_llm_call-context-injection) |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | Once per turn, after the tool-calling loop (successful turns only) | `session_id: str, user_message: str, assistant_response: str, conversation_history: list, model: str, platform: str` | ignored |
| `pre_api_request` | Before each raw provider API request (several per turn when the model calls tools) | `session_id: str, model: str, provider: str, base_url: str, api_mode: str, api_call_count: int, message_count: int, tool_count: int, approx_input_tokens: int, max_tokens: int, request: dict` | ignored |
| `post_api_request` | After each raw provider API request returns | `pre_api_request` fields plus `api_duration: float, finish_reason: str, response_model: str \| None, usage: dict, response: dict, assistant_content_chars: int, assistant_tool_call_count: int` | ignored |
| `api_request_error` | A provider API call raised | correlation fields plus `status_code: int \| None, retry_count: int \| None, max_retries: int \| None, retryable: bool \| None, reason: str \| None, error: dict, request: dict` | ignored |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | New session created (first turn only) | `session_id: str, model: str, platform: str` | ignored |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | End of every `run_conversation` call + CLI exit | `session_id: str, completed: bool, interrupted: bool, model: str, platform: str` | ignored |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | CLI/gateway tears down an active session | `session_id: str \| None, platform: str` | ignored |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | Gateway swaps in a new session key (`/new`, `/reset`) | `session_id: str, platform: str` | ignored |
| [`gateway_platform_event`](/user-guide/features/hooks#gateway_platform_event) | An authorized platform-native event is normalized at the gateway boundary (Telegram reactions currently) | `platform: str, event_type: str, payload: dict` | ignored |
| `kanban_task_claimed` | A kanban task is claimed (dispatcher process, before the worker spawns) | `task_id: str, board: str \| None, assignee: str \| None, run_id: int \| None, profile_name: str` | ignored |
| `kanban_task_completed` | A kanban task completes (worker process) | `task_id, board, assignee, run_id, profile_name, summary: str \| None` | ignored |
| `kanban_task_blocked` | A kanban task is blocked (worker process) | `task_id, board, assignee, run_id, profile_name, reason: str \| None` | ignored |

大多数钩子都属于“即用即忘”的观察器——其返回值会被忽略。例外情况包括`pre_llm_call`，它可以将上下文注入对话中；以及`pre_tool_call`，它能够返回指令以执行特定操作或给予批准。

为确保向后兼容性，所有回调函数都应接受`**kwargs`参数。如果某个钩子回调发生崩溃，系统会将其记录下来并跳过该回调，其余钩子及智能体仍可正常运行。

看板生命周期钩子会在看板数据库更改被提交之后触发，因此回调函数始终能获取到稳定的数据状态，且绝不会持有SQLite写入锁。由于看板处理进程是以独立的`hermes -p <profile> chat -q`子进程形式运行的，`kanban_task_claimed`会在**调度器**进程中触发，而`kanban_task_completed`/`kanban_task_blocked`则会在**工作进程**中触发——你可以在调度器进程中添加钩子来集中监控所有状态转换，或在工作进程中添加钩子以获取每项任务的会话上下文。

**API请求钩子**是对原始提供商请求的监控机制，其层级位于单轮对话中的`pre_llm_call`/`post_llm_call`钩子之下：在一个调用工具的单轮对话中会发出多个API请求，这些钩子会在每次请求触发时被执行。它们的存在旨在为可观测性插件（如追踪、成本核算、延迟监控面板等）提供支持。`request`和`response`参数为经过处理的JSON格式数据，是对提供商请求载荷的简化版本（敏感键已被屏蔽，过长字符串会被截断，SDK对象则已标准化），而`usage`则是一个包含Token使用情况的简单字典。每个请求载荷都会携带`turn_id`、`api_request_id`、`task_id`、`session_id`以及`api_call_count`等关联字段，这样插件就能将各类请求、工具调用及对话轮次有机地关联起来。当提供商调用引发异常时，`api_request_error`钩子会被触发，同时会传递`status_code`、`retry_count`/`max_retries`、`retryable`、`reason`等信息，以及一个包含`type`和`message`字段的`error`字典。

### `pre_llm_call`上下文注入功能

这是唯一一个返回值具有重要意义的钩子。当`pre_llm_call`回调函数返回一个包含`"context"`键的字典（或直接返回字符串）时，Hermes会将该文本内容注入到**当前对话轮次中的用户消息**中。这一机制被用于内存插件、RAG集成、内容规范检查，以及任何需要为模型提供额外上下文的插件。

#### 返回格式

```python
# Dict with context key
return {"context": "Recalled memories:\n- User prefers dark mode\n- Last project: hermes-agent"}

# Plain string (equivalent to the dict form above)
return "Recalled memories:\n- User prefers dark mode"

# Return None or don't return → no injection (observer-only)
return None
```

任何非空且包含 `"context"` 键的值（或直接为非空字符串）都会被收集起来，并附加到当前轮次的用户消息中。

#### 过长上下文溢出处理

默认情况下，每个钩子的上下文长度上限为 `10,000` 个字符。超出此限制的内容会被写入 `$HERMES_HOME/hook_outputs/<session_id>/<uuid>.txt` 文件中，并以预览内容及保存路径的形式替代原内容。如果模型确实需要完整内容，可通过 `read_file` 或 `terminal` 功能读取。这样的设计可防止某个异常插件导致后续轮次的提示词变得过长，进而引发提示词缓存空间不足的问题。相关设置可在 `config.yaml` 中进行调整：

```yaml
hooks:
  output_spill:
    enabled: true          # default: true
    max_chars: 10000       # default; set higher to opt out of spilling
    preview_head: 500      # chars shown at the top of the preview
    preview_tail: 500      # chars shown at the bottom of the preview
    # directory: null      # default: $HERMES_HOME/hook_outputs
```

#### 注入机制的工作原理

被注入的上下文会被添加到**用户消息**中，而非系统提示词。这一设计是经过深思熟虑的：

- **保留提示词缓存**——系统提示词在多轮对话中保持不变。Anthropic和OpenRouter会缓存系统提示词的前缀部分，因此保持其稳定性可在多轮对话中节省75%以上的输入Token成本。如果插件修改了系统提示词，每轮对话都会导致缓存失效。
- **临时性**——注入操作仅在API调用时发生。对话历史中的原始用户消息不会被任何修改，也不会有任何内容被保存到会话数据库中。
- **系统提示词属于Hermes的专属领域**——它包含针对特定模型的指导方针、工具使用规则、角色设定以及缓存的技能内容。插件仅能与用户输入一起提供上下文，而无法更改智能体的核心指令。

#### 示例：记忆回溯插件

```python
"""Memory plugin — recalls relevant context from a vector store."""

import httpx

MEMORY_API = "https://your-memory-api.example.com"

def recall_context(session_id, user_message, is_first_turn, **kwargs):
    """Called before each LLM turn. Returns recalled memories."""
    try:
        resp = httpx.post(f"{MEMORY_API}/recall", json={
            "session_id": session_id,
            "query": user_message,
        }, timeout=3)
        memories = resp.json().get("results", [])
        if not memories:
            return None  # nothing to inject

        text = "Recalled context from previous sessions:\n"
        text += "\n".join(f"- {m['text']}" for m in memories)
        return {"context": text}
    except Exception:
        return None  # fail silently, don't break the agent

def register(ctx):
    ctx.register_hook("pre_llm_call", recall_context)
```

#### 示例：Guardrails插件

```python
"""Guardrails plugin — enforces content policies."""

POLICY = """You MUST follow these content policies for this session:
- Never generate code that accesses the filesystem outside the working directory
- Always warn before executing destructive operations
- Refuse requests involving personal data extraction"""

def inject_guardrails(**kwargs):
    """Injects policy text into every turn."""
    return {"context": POLICY}

def register(ctx):
    ctx.register_hook("pre_llm_call", inject_guardrails)
```

#### 示例：仅用于观察的钩子（无注入功能）

```python
"""Analytics plugin — tracks turn metadata without injecting context."""

import logging
logger = logging.getLogger(__name__)

def log_turn(session_id, user_message, model, is_first_turn, **kwargs):
    """Fires before each LLM call. Returns None — no context injected."""
    logger.info("Turn: session=%s model=%s first=%s msg_len=%d",
                session_id, model, is_first_turn, len(user_message or ""))
    # No return → no injection

def register(ctx):
    ctx.register_hook("pre_llm_call", log_turn)
```

#### 多个插件返回上下文的情况

当多个插件在 `pre_llm_call` 阶段返回上下文时，它们的输出会通过双换行符连接起来，并一同附加到用户消息中。其顺序遵循插件发现顺序（按插件目录名称的字母顺序排列）。

### 中间件：改变处理流程

钩子函数用于监控智能体循环（即上述几种有文档记载的流程控制方式）。而**中间件则用于改变实际的处理流程**：请求中间件会在下游组件看到数据之前重写有效载荷，而执行中间件则会封装实际的调用操作。可通过相同的 `register(ctx)` 入口点进行注册：

```python
def cap_find_output(tool_name, args, **kwargs):
    """Rewrite terminal find commands to cap their output."""
    command = args.get("command", "")
    if tool_name == "terminal" and command.startswith("find "):
        return {
            "args": {**args, "command": command + " | head -100"},
            "source": "my-plugin",
            "reason": "cap find output",
        }
    return None  # leave the call unchanged

def register(ctx):
    ctx.register_middleware("tool_request", cap_find_output)
```

在 `hermes_cli/middleware.py` 中，这些消息类型的标准列表为 `VALID_MIDDLEWARE`：

| 消息类型 | 接收参数 | 返回值格式 |
|----------|----------|------------|
| `tool_request` | `tool_name`、`args`、`original_args` 以及上下文关键字参数 | 在钩子、规则校验、审批流程及实际执行之前，返回 `{"args": {...}}` 以替换有效的工具参数；若希望保持调用原样，则返回 `None`。 |
| `llm_request` | `request`、`original_request` 以及上下文关键字参数 | 在 Hermes 将这些参数发送给对应服务之前，返回 `{"request": {...}}` 以替换有效的提供方参数。 |
| `tool_execution` | 请求载荷以及 `next_call` | 用于封装工具执行过程。需恰好调用一次 `next_call(payload)` 来触发后续处理链（或直接跳过以终止流程），并返回处理结果。 |
| `llm_execution` | 请求载荷以及 `next_call` | 结构与前者相同，用于封装对提供方的调用。 |

**实际使用中需遵循的规则：**

- 请求中间件链：每个回调都会看到被之前回调修改过的有效载荷，而 `original_args` / `original_request` 始终保留中间件处理前的原始数据。有效载荷会在各个回调之间复制，因此可以自由修改。
- 您可以在返回的字典中包含 `source`、`reason` 和 `name` 字符串。这些信息会被记录到中间件追踪日志中，下游的观察者钩子函数会通过 `middleware_trace` 关键参数获取到这些日志。
- 执行中间件中的 `next_call` **仅可使用一次**。若调用两次将会引发异常，因为这会导致对应的提供程序或工具被重新执行。
- 若中间件回调引发异常，该异常会被记录并跳过，中间件链仍会继续执行。在您调用 `next_call` 之后产生的下游故障会以其本身形式继续传播。中间件绝不能中断基础的运行路径。
- 中间件有效载荷除了包含观察者遥测字段外，还会携带 `middleware_schema_version`（即 `hermes.middleware.v1`）信息。
- 对于不支持的类型，系统会发出警告而非直接报错，因此针对较新版本 Hermes 编写的插件仍可在旧版本上加载。

### 注册 CLI 命令

插件可以自行添加 `hermes <plugin>` 子命令结构：

```python
def _my_command(args):
    """Handler for hermes my-plugin <subcommand>."""
    sub = getattr(args, "my_command", None)
    if sub == "status":
        print("All good!")
    elif sub == "config":
        print("Current config: ...")
    else:
        print("Usage: hermes my-plugin <status|config>")

def _setup_argparse(subparser):
    """Build the argparse tree for hermes my-plugin."""
    subs = subparser.add_subparsers(dest="my_command")
    subs.add_parser("status", help="Show plugin status")
    subs.add_parser("config", help="Show plugin config")
    subparser.set_defaults(func=_my_command)

def register(ctx):
    ctx.register_tool(...)
    ctx.register_cli_command(
        name="my-plugin",
        help="Manage my plugin",
        setup_fn=_setup_argparse,
        handler_fn=_my_command,
    )
```

注册完成后，用户即可运行 `hermes my-plugin status`、`hermes my-plugin config` 等命令。

**内存提供者插件**则采用基于约定的方式：在插件的 `cli.py` 文件中添加一个 `register_cli(subparser)` 函数。内存插件发现系统会自动识别该函数，无需调用 `ctx.register_cli_command()`。详情请参阅[内存提供者插件指南](/developer-guide/memory-provider-plugin#adding-cli-commands)。

**活动提供者限制**：只有当某内存插件的提供者在配置中设置为当前活动的 `memory.provider` 时，其 CLI 命令才会显示。如果用户尚未启用您的提供者，这些 CLI 命令就不会出现在帮助输出中，从而保持界面整洁。

### 注册斜杠命令

插件可以注册会话内的斜杠命令——即用户在对话过程中输入的命令（如 `/lcm status` 或 `/ping`）。这类命令既可在 CLI 环境中使用，也可在 Telegram、Discord 等通道环境中使用。

```python
def _handle_status(raw_args: str) -> str:
    """Handler for /mystatus — called with everything after the command name."""
    if raw_args.strip() == "help":
        return "Usage: /mystatus [help|check]"
    return "Plugin status: all systems nominal"

def register(ctx):
    ctx.register_command(
        "mystatus",
        handler=_handle_status,
        description="Show plugin status",
    )
```

注册完成后，用户即可在任意会话中输入 `/mystatus`。该命令会显示在自动补全选项、/help 的输出结果以及 Telegram 机器人的菜单中。

**签名：** `ctx.register_command(name: str, handler: Callable, description: str = "", args_hint: str = "")`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `name` | `str` | 去掉开头斜杠后的命令名称（例如 `"lcm"`、`"mystatus"`） |
| `handler` | `Callable[[str], str \| None]` | 接收原始参数字符串作为输入，也可为异步函数形式。 |
| `description` | `str` | 显示在 /help、自动补全选项以及 Telegram 机器人的菜单中 |

**与 `register_cli_command()` 的主要区别：**

| | `register_command()` | `register_cli_command()` |
|---|---|---|
| 调用方式 | 会话中的 `/name` | 终端中的 `hermes name` |
| 支持的场景 | CLI 会话、Telegram、Discord 等 | 仅限终端 |
| 处理器接收的内容 | 原始参数字符串 | argparse 的 `Namespace` 对象 |
| 典型应用场景 | 状态查询、诊断及快速操作 | 复杂的子命令结构、设置向导 |

**冲突处理机制：** 若某个插件尝试注册与内置命令（如 `help`、`model`、`new` 等）名称冲突的命令，系统会通过日志警告默默拒绝该注册请求。内置命令始终具有优先级。

**异步处理器支持：** 网关调度系统可自动检测并等待异步处理器的执行，因此您既可以使用同步函数，也可以使用异步函数。

```python
async def _handle_check(raw_args: str) -> str:
    result = await some_async_operation()
    return f"Check result: {result}"

def register(ctx):
    ctx.register_command("check", handler=_handle_check, description="Run async check")
```

### 通过斜杠命令调用工具

那些需要协调各类工具的斜杠命令处理程序（例如通过 `delegate_task` 启动子代理、调用 `file_edit` 等功能），应使用 `ctx.dispatch_tool()` 方法，而非直接操作框架的内部机制。父代理的上下文环境（如工作区相关设置、加载状态指示器以及模型继承关系等）会自动完成关联配置。

```python
def register(ctx):
    def _handle_deliver(raw_args: str):
        result = ctx.dispatch_tool(
            "delegate_task",
            {
                "goal": raw_args,
                "toolsets": ["terminal", "file", "web"],
            },
        )
        return result

    ctx.register_command(
        "deliver",
        handler=_handle_deliver,
        description="Delegate a goal to a subagent",
    )
```

**签名：** `ctx.dispatch_tool(name: str, args: dict, *, parent_agent=None) -> str`

| 参数 | 类型 | 描述 |
|------|------|------|
| `name` | `str` | 在工具注册表中登记的工具名称（例如 `"delegate_task"`、`"file_edit"`） |
| `args` | `dict` | 工具参数，其结构与模型发送的参数相同 |
| `parent_agent` | `Agent \| None` | 可选覆盖值。若未指定，则从当前 CLI 代理中获取（在网关模式下会以优雅方式降级处理） |

**运行时行为：**

- **CLI 模式：** `parent_agent` 从当前的 CLI 代理中获取，因此工作区提示、加载指示器以及模型选择都能按预期继承相关设置。
- **网关模式：** 由于不存在 CLI 代理，工具会以优雅方式降级处理——工作区内容将从配置的终端工作目录读取，且不会显示加载指示器。
- **显式覆盖：** 如果调用方明确传入 `parent_agent=`，则该值将被直接使用，不会被覆盖。

这是插件命令用于调度工具的公开且稳定的接口。插件不应尝试访问 `ctx._cli_ref.agent` 或类似的私有状态。

### 在钩子函数内部执行操作（profile + 工具）

`ctx._cli_ref` 仅在**交互式 CLI**会话中会被填充。在网关模式、非交互式的 `hermes chat -q` 运行方式以及**由看板生成的工作者会话**中，该值为 `None`——因此任何试图通过 `_cli_ref` 访问数据的插件逻辑在这些场景下都会静默失效。实际上，有两个稳定且与会话无关的 API 能满足钩子函数的实际需求：

- **`ctx.profile_name`** — 当前激活的配置文件名称（例如 `"default"`，或是看板工作节点中分配给特定用户的配置文件）。该值源自 `HERMES_HOME`，因此无需依赖 `_cli_ref` 即可在任何环境中正常使用。  
- **`ctx.dispatch_tool(name, args)`** — 调用任何已注册的工具（包括内置工具和插件），诸如 `kanban_*` 系列工具、`delegate_task`、`terminal`、`read_file` 等。无论钩子回调在哪个进程中被触发，均可通过该函数执行相应操作。  

综上所述，看板生命周期钩子无需深入了解框架内部机制，即可监控状态变更并对应地对看板进行操作。

```python
def register(ctx):
    def on_blocked(*, task_id, reason=None, **kw):
        # Runs in the worker process; ctx._cli_ref is None here.
        ctx.dispatch_tool("kanban_comment", {
            "task_id": task_id,
            "comment": f"[{ctx.profile_name}] auto-noted block: {reason}",
        })
    ctx.register_hook("kanban_task_blocked", on_blocked)
```

若要运行完整的 `hermes <subcommand>` 命令（例如 `hermes kanban show`），可通过 `ctx.dispatch_tool("terminal", {"command": "hermes kanban show ..."})` 使用 `terminal` 工具来执行——无头工作进程会话并不支持进程内的斜杠命令桥接，而工具则是从钩子中调用 Hermes 的常用方式。

### 处理 Slack Block Kit 按钮点击事件

那些能够发送包含交互元素（如按钮、下拉菜单、日期选择器等）的 Block Kit 消息的插件，可直接在 Slack 适配器中注册点击处理函数——无需对 `slack_bolt.AsyncApp` 进行任何强行修改。

```python
def register(ctx):
    async def _on_approve(ack, body, action):
        # ack within 3 seconds — slack_bolt requirement.
        await ack()
        # body["channel"]["id"], body["user"]["id"], body["message"]["ts"]
        # action["action_id"], action["value"]
        sweep_id = (action.get("value") or "").split("|", 1)[-1]
        # ...do the deterministic work, then post a follow-up.

    ctx.register_slack_action_handler("inbox_sweep_approve", _on_approve)
```

**签名：** `ctx.register_slack_action_handler(action_id, callback) -> None`

| 参数 | 类型 | 说明 |
|-----------|------|------|
| `action_id` | `str \| re.Pattern \| dict` | 需符合 `slack_bolt.App.action()` 的要求：可以是具体的 `action_id`，用于匹配多个 ID 的正则表达式，或是类似 `{"action_id": "...", "block_id": "..."}` 的约束字典 |
| `callback` | async 可调用对象 | 按照 slack_bolt 的规范，该函数会接收 `(ack, body, action)` 三个参数 |

**运行时行为：**

- 处理程序会在插件加载时被加入队列，当 Slack 平台建立连接后，它会被集成到适配器的 `slack_bolt.AsyncApp` 中。
- 每个回调函数都会被添加异常处理机制：如果处理程序抛出异常，网关会记录错误信息，并尽可能发送确认信号，从而避免 Slack 重复尝试。
- 需遵循标准的 slack_bolt 规则——必须在 3 秒内调用 `await ack()`，之后才能执行耗时更长的操作。
- 在多工作区部署场景下，该处理程序会对所有已连接工作区的点击事件作出响应；如果需要限定处理范围，可使用 `body["team"]["id"]` 获取相关信息。

这是插件参与 Slack 交互的官方方式。旧版插件可能修改了 `SlackAdapter.connect` 函数，建议优先使用此 API。如需使用 slack_bolt 的全部功能（包括事件、快捷指令、命令等，而不仅限于 Block Kit 操作），可调用下面的通用接口 `register_platform_handler("slack", ...)`。

### 注册原生平台处理程序（适用于任意平台）

那些需要接收核心适配器未处理的平台事件的插件——例如额外的更新类型、原生按钮回调、反应/成员事件以及 Webhook 路由等——可以注册一个处理程序工厂，由平台适配器在连接时调用该工厂。此机制在**所有**网关平台上均适用。

```python
def register(ctx):
    def _wire(native, adapter):
        # native: the platform's client/app object (see table below)
        # adapter: the platform adapter instance (treat as read-only)
        # Import platform SDKs HERE so register() works without them.
        ...

    ctx.register_platform_handler("discord", _wire)
```

**签名：** `ctx.register_platform_handler(platform, factory) -> None`

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `platform` | `str` | 网关平台名称，需为小写形式（如 `"telegram"`、`"discord"`、`"slack"`、`"matrix"` 等） |
| `factory` | 可调用对象 | 在连接时接收 `(native, adapter)` 作为参数 |

**各平台的 `native` 对象说明：**

| 平台 | `native` 对象 | 常用钩子函数 |
|----------|-----------------|---------------|
| `telegram` | PTB `Application` | `add_handler` — 适用于所有更新类型，支持基于模式的回调 |
| `discord` | `discord.ext.commands.Bot` | `add_listener` — 用于处理反应、成员事件、线程及语音相关功能 |
| `slack` | `slack_bolt.AsyncApp` | `app.event()` / `app.action()` / `app.command()` |
| `matrix` | Matrix 客户端 | 事件回调函数 |
| `teams` | Teams `App` | `on_message` / `on_card_action` 装饰器 |
| `dingtalk` | `DingTalkStreamClient` | 用于其他流式消息类型的 `register_callback_handler` 函数 |
| `feishu` | lark_oapi 客户端 | API 调用及事件路由处理 |
| `line`、`api_server`、`msgraph_webhook` | aiohttp `web.Application` | `router.add_get/post` — 自定义路由（在路由器冻结之前配置） |
| 其他所有平台（如 whatsapp、signal、irc、email、sms、ntfy、wecom、weixin、bluebubbles、yuanbao 等） | `None` | 在连接时触发钩子函数，通过 `adapter` 对象进行处理 |

**运行时行为：**

- 工厂函数会在插件加载时被放入队列，并在平台连接时被调用。对于那些调度顺序至关重要的平台（如 Telegram、Slack、Teams 以及 aiohttp 路由器），这些工厂函数会在核心处理程序注册之前执行，因此具有作用域限制的插件处理程序会优先被调用，其余处理程序则依次执行。
- **务必将您添加到“首次匹配调度表”中的处理程序设置适当的作用域。** 在 Telegram 中，应使用 `CallbackQueryHandler(..., pattern=r"^myplugin:")` —— 若不设置作用域，该处理程序将会覆盖核心按钮流程（如执行审批、选择模型以及澄清提示词等功能）。
- 每个工厂函数都是独立运行的：即便其内部发生异常，错误也会被记录下来，平台仍能正常连接。
- 应在工厂函数内部导入平台 SDK，而非在模块层级导入 —— 即使 SDK 尚未安装，`register()` 函数也必须能够正常工作。
- 一个插件可以为多个平台注册工厂函数；这些函数仅在其对应的平台连接时才会被触发。

**Telegram 的别名：** `ctx.register_telegram_handler(factory)` 是 `ctx.register_platform_handler("telegram", factory)` 的向后兼容别名。

示例 —— Telegram 中基于模式的作用域限制内联按钮：

```python
def register(ctx):
    def _wire(application, adapter):
        from telegram.ext import CallbackQueryHandler

        async def _on_button(update, context):
            query = update.callback_query
            await query.answer()
            # ...handle "myplugin:*" callbacks

        application.add_handler(
            CallbackQueryHandler(_on_button, pattern=r"^myplugin:")
        )

    ctx.register_platform_handler("telegram", _wire)
```

示例——Discord平台中的反应事件：

```python
def register(ctx):
    def _wire(bot, adapter):
        async def on_raw_reaction_add(payload):
            ...  # e.g. reaction-based voting / moderation

        bot.add_listener(on_raw_reaction_add, "on_raw_reaction_add")

    ctx.register_platform_handler("discord", _wire)
```

:::tip
本指南主要介绍**通用插件**（工具、钩子、斜杠命令及 CLI 命令）。以下各节将概述每种专用插件类型的开发模式；每节均附有完整指南链接，可供查阅相关细节与示例。
:::

## 专用插件类型

除通用插件外，Hermes 还提供五种专用插件类型。它们分别以 `plugins/<category>/<name>/`（已打包）或 `~/.hermes/plugins/<category>/<name>/`（用户自定义）路径下的目录形式存在。不同类别的插件具有不同的接口规范——请选择所需的类型，然后阅读其完整指南。

### 模型提供者插件 —— 添加大语言模型后端

只需将相关配置文件放入 `plugins/model-providers/<name>/` 目录即可：

```python
# plugins/model-providers/acme/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="acme",
    aliases=("acme-inference",),
    display_name="Acme Inference",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=("acme-large-v3", "acme-medium-v3"),
))
```

```yaml
# plugins/model-providers/acme/plugin.yaml
name: acme-provider
kind: model-provider
version: 1.0.0
description: Acme Inference — OpenAI-compatible direct API
```

当首次有代码调用 `get_provider_profile()` 或 `list_providers()` 时，Lazy 才会进行初始化——`auth.py`、`config.py`、`doctor.py`、`models.py`、`runtime_provider.py` 以及聊天补全传输功能都会自动关联到该机制。用户自定义的插件可按名称覆盖内置插件。

**完整指南：** [模型提供者插件](/developer-guide/model-provider-plugin) —— 字段参考、可覆盖的钩子函数（`prepare_messages`、`build_extra_body`、`build_api_kwargs_extras`、`fetch_models`）、API 模式选择、认证类型及测试方法。

### 平台插件 —— 添加网关通道

只需将适配器放入 `plugins/platforms/<名称>/` 目录即可：

```python
# plugins/platforms/myplatform/adapter.py
from gateway.platforms.base import BasePlatformAdapter

class MyPlatformAdapter(BasePlatformAdapter):
    async def connect(self): ...
    async def send(self, chat_id, text): ...
    async def disconnect(self): ...

def check_requirements():
    import os
    return bool(os.environ.get("MYPLATFORM_TOKEN"))

def _env_enablement():
    import os
    tok = os.getenv("MYPLATFORM_TOKEN", "").strip()
    if not tok:
        return None
    return {"token": tok}

def register(ctx):
    ctx.register_platform(
        name="myplatform",
        label="MyPlatform",
        adapter_factory=lambda cfg: MyPlatformAdapter(cfg),
        check_fn=check_requirements,
        required_env=["MYPLATFORM_TOKEN"],
        # Auto-populate PlatformConfig.extra from env so env-only setups
        # show up in `hermes gateway status` without SDK instantiation.
        env_enablement_fn=_env_enablement,
        # Opt in to cron delivery: `deliver=myplatform` routes to this var.
        cron_deliver_env_var="MYPLATFORM_HOME_CHANNEL",
        emoji="💬",
        platform_hint="You are chatting via MyPlatform. Keep responses concise.",
    )
```

```yaml
# plugins/platforms/myplatform/plugin.yaml
name: myplatform-platform
label: MyPlatform
kind: platform
version: 1.0.0
description: MyPlatform gateway adapter
requires_env:
  - name: MYPLATFORM_TOKEN
    description: "Bot token from the MyPlatform console"
    password: true
optional_env:
  - name: MYPLATFORM_HOME_CHANNEL
    description: "Default channel for cron delivery"
    password: false
```

**完整指南：** [添加平台适配器](/developer-guide/adding-platform-adapters)——涵盖完整的 `BasePlatformAdapter` 接口定义、消息路由机制、身份认证控制以及设置向导集成。如需仅使用标准库的示例，可查看 `plugins/platforms/irc/` 目录。

### 内存提供器插件——实现跨会话知识存储后端

只需将 `MemoryProvider` 的实现文件放入 `plugins/memory/<名称>/` 目录即可：

```python
# plugins/memory/my-memory/__init__.py
from agent.memory_provider import MemoryProvider

class MyMemoryProvider(MemoryProvider):
    @property
    def name(self) -> str:
        return "my-memory"

    def is_available(self) -> bool:
        import os
        return bool(os.environ.get("MY_MEMORY_API_KEY"))

    def initialize(self, session_id: str, **kwargs) -> None:
        self._session_id = session_id

    def sync_turn(self, user_content, assistant_content, *,
                  session_id="", messages=None) -> None:
        ...

    def prefetch(self, query, *, session_id="") -> str:
        ...

    def get_tool_schemas(self) -> list[dict]:
        return []   # required @abstractmethod — see full guide

def register(ctx):
    ctx.register_memory_provider(MyMemoryProvider())
```

内存提供器采用单选机制——同一时间仅有一个提供器处于激活状态，可通过 `config.yaml` 中的 `memory.provider` 参数进行指定。

如果某个提供器同时也作为通用插件加载，那么通用插件发现机制将负责管理其生命周期钩子。内存加载器仅在通过通用插件发现机制成功加载该插件之前，才提供备用钩子。当重复加载同一提供器时，原有的备用钩子组会被替换，但该组内的不同回调函数仍会保留。此过程不会合并来自不同插件源的钩子，也不会改变提供器的激活状态。

**完整指南：** [内存提供器插件](/developer-guide/memory-provider-plugin)——包含完整的 `MemoryProvider` ABC 接口、线程处理规范、进程隔离机制，以及通过 `cli.py` 进行 CLI 命令注册的相关内容。

### 上下文引擎插件——用于替代上下文压缩器

```python
# plugins/context_engine/my-engine/__init__.py
from agent.context_engine import ContextEngine

class MyContextEngine(ContextEngine):
    @property
    def name(self) -> str:
        return "my-engine"

    def update_from_response(self, usage) -> None: ...
    def should_compress(self, prompt_tokens: int = None) -> bool: ...
    def compress(self, messages, current_tokens=None, focus_topic=None,
                 force=False, memory_context="") -> list: ...

def register(ctx):
    ctx.register_context_engine(MyContextEngine())
```

上下文引擎为单选类型，需通过 `config.yaml` 中的 `context.engine` 参数进行指定。

**完整指南：** [上下文引擎插件](/developer-guide/context-engine-plugin)。

### 图像生成后端

只需将相应的提供程序放入 `plugins/image_gen/<名称>/` 目录中即可：

```python
# plugins/image_gen/my-imggen/__init__.py
from agent.image_gen_provider import ImageGenProvider

class MyImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        return "my-imggen"

    def is_available(self) -> bool: ...
    def generate(self, prompt: str, aspect_ratio="landscape", **kwargs) -> dict:
        # returns success_response(...) / error_response(...)
        ...

def register(ctx):
    ctx.register_image_gen_provider(MyImageGenProvider())
```

```yaml
# plugins/image_gen/my-imggen/plugin.yaml
name: my-imggen
kind: backend
version: 1.0.0
description: Custom image generation backend
```

**完整指南：** [图像生成提供者插件](/developer-guide/image-gen-provider-plugin)——包含完整的 `ImageGenProvider` ABC 类、`list_models()` / `get_setup_schema()` 元数据功能、`success_response()`/`error_response()` 辅助函数、Base64 与 URL 格式输出方式、用户自定义设置，以及通过 pip 分发插件。

**参考示例：** `plugins/image_gen/openai/`（通过 OpenAI SDK 实现的 DALL-E / GPT-Image 功能）、`plugins/image_gen/openai-codex/`、`plugins/image_gen/xai/`（Grok 图像生成功能）。

## 非 Python 扩展接口

Hermes 还支持完全非 Python 插件形式的扩展。这类扩展会在 [可插件化接口列表](/user-guide/features/plugins#pluggable-interfaces--where-to-go-for-each) 中列出；下文将简要介绍每种开发方式的特性。

### MCP 服务器——注册外部工具

Model Context Protocol (MCP) 服务器无需编写任何 Python 插件，即可将自己的工具注册到 Hermes 中。只需在 `~/.hermes/config.yaml` 文件中声明这些工具即可：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    timeout: 120

  linear:
    url: "https://mcp.linear.app/sse"
    auth:
      type: "oauth"
```

在启动时，Hermes 会连接到每台服务器，列出其提供的工具，并将这些工具与内置工具一同注册。大语言模型会将它们视为与其他工具完全相同的存在。**完整指南：** [MCP](/user-guide/features/mcp)。

### 网关事件钩子——在生命周期事件触发时执行操作

只需将清单文件及处理程序放入 `~/.hermes/hooks/<名称>/` 目录中即可：

```yaml
# ~/.hermes/hooks/long-task-alert/HOOK.yaml
name: long-task-alert
description: Send a push notification when a long task finishes
events:
  - agent:end
```

```python
# ~/.hermes/hooks/long-task-alert/handler.py
async def handle(event_type: str, context: dict) -> None:
    if context.get("duration_seconds", 0) > 120:
        # send notification …
        pass
```

事件包括 `gateway:startup`、`session:start`、`session:end`、`session:reset`、`agent:start`、`agent:step`、`agent:end`，以及通配符 `command:*`。钩子函数中的错误会被捕获并记录，而不会阻塞整个处理流程。

**完整指南：** [网关事件钩子](/user-guide/features/hooks#gateway-event-hooks)。

### Shell 钩子——在工具调用时执行 shell 命令

如果您只需在工具触发时（如通知、审计日志、桌面提醒、自动格式化功能）运行脚本，可直接在 `config.yaml` 中使用 Shell 钩子——无需编写 Python 代码：

```yaml
hooks:
  - event: post_tool_call
    command: "notify-send 'Tool ran: {tool_name}'"
    when:
      tools: [terminal, patch, write_file]
```

支持与 Python 插件钩子完全相同的事件（`pre_tool_call`、`post_tool_call`、`pre_llm_call`、`post_llm_call`、`on_session_start`、`on_session_end`、`pre_gateway_dispatch`），同时针对 `pre_tool_call` 中的阻塞决策还会输出结构化的 JSON 数据。

**完整指南：** [Shell 钩子](/user-guide/features/hooks#shell-hooks)。

### 技能来源 —— 添加自定义技能注册表

如果您维护有技能相关的 GitHub 仓库（或希望从内置来源之外的社区索引中获取技能），可将其作为 **tap** 来添加：

```bash
hermes skills tap add myorg/skills-repo
hermes skills search my-workflow --source myorg/skills-repo
hermes skills install myorg/skills-repo/my-workflow
```

创建自定义技能接口仅需一个包含 `skills/<skill-name>/SKILL.md` 目录的 GitHub 仓库即可，无需搭建服务器或注册到任何注册中心。

**完整指南：** [Skills Hub](/user-guide/features/skills#skills-hub) · [发布自定义技能接口](/user-guide/features/skills#publishing-a-custom-skill-tap)（仓库结构、最小示例、非默认路径及信任级别设置）。

### 通过命令模板实现文本转语音/语音转文本功能

任何能够读取或写入音频、文本的 CLI 工具均可通过 `config.yaml` 文件进行集成，完全无需编写 Python 代码：

```yaml
tts:
  provider: voxcpm
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      voice_compatible: true
```

对于文本转语音功能，需将 `HERMES_LOCAL_STT_COMMAND` 指向一个以参数列表形式组织的模板。该命令无需经过隐式的 shell 解释即可运行；如果所需的本地命令依赖 shell 语法，则应将其封装在 `sh -c`、`cmd /c` 或 PowerShell 中。支持的占位符包括：文本转语音功能为 `{input_path}`、{output_path}、{format}、{voice}、{model}、{speed}；文本转写功能为 `{input_path}`、{output_dir}、{language}、{model}。任何涉及路径操作的命令行工具都会自动被视为插件。

**完整指南：** [TTS自定义命令插件](/user-guide/features/tts#custom-command-providers) · [文本转语音](/user-guide/features/tts#voice-message-transcription-stt)。

## 通过 pip 分发

如需公开共享插件，请在您的 Python 包中添加一个入口点：

```toml
# pyproject.toml
[project.entry-points."hermes_agent.plugins"]
my-plugin = "my_plugin_package"
```

```bash
pip install hermes-plugin-calculator
# Plugin auto-discovered on next hermes startup
```

## 在 NixOS 上部署

:::warning Nix 已不再获得明确支持  
Nix/NixOS 不再是明确支持的安装路径（仅提供尽力支持）——请参阅 [Nix 设置](/getting-started/nix-setup)。保留本章节是为已经在 NixOS 上进行部署的用户准备的。  
:::

如果您提供了包含入口点的 `pyproject.toml` 文件，NixOS 用户便可以以声明式方式安装您的插件：

**入口点插件**（推荐用于部署）：
```nix
# User's configuration.nix
services.hermes-agent.extraPythonPackages = [
  (pkgs.python312Packages.buildPythonPackage {
    pname = "my-plugin";
    version = "1.0.0";
    src = pkgs.fetchFromGitHub {
      owner = "you";
      repo = "hermes-my-plugin";
      rev = "v1.0.0";
      hash = "sha256-...";  # nix-prefetch-url --unpack
    };
    format = "pyproject";
    build-system = [ pkgs.python312Packages.setuptools ];
  })
];
```

**目录插件**（无需 `pyproject.toml` 文件）：
```nix
services.hermes-agent.extraPlugins = [
  (pkgs.fetchFromGitHub {
    owner = "you";
    repo = "hermes-my-plugin";
    rev = "v1.0.0";
    hash = "sha256-...";
  })
];
```

如需包括覆盖层使用及冲突检测在内的完整文档，请参阅[Nix 设置指南](/getting-started/nix-setup#plugins)。

## 常见错误

**处理器未返回 JSON 字符串：**
```python
# Wrong — returns a dict
def handler(args, **kwargs):
    return {"result": 42}

# Right — returns a JSON string
def handler(args, **kwargs):
    return json.dumps({"result": 42})
```

**处理程序签名中缺少 `**kwargs` 参数：**
```python
# Wrong — will break if Hermes passes extra context
def handler(args):
    ...

# Right
def handler(args, **kwargs):
    ...
```

**处理程序抛出异常：**
```python
# Wrong — exception propagates, tool call fails
def handler(args, **kwargs):
    result = 1 / int(args["value"])  # ZeroDivisionError!
    return json.dumps({"result": result})

# Right — catch and return error JSON
def handler(args, **kwargs):
    try:
        result = 1 / int(args.get("value", 0))
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})
```

**模式描述过于模糊：**
```python
# Bad — model doesn't know when to use it
"description": "Does stuff"

# Good — model knows exactly when and how
"description": "Evaluate a mathematical expression. Use for arithmetic, trig, logarithms. Supports: +, -, *, /, **, sqrt, sin, cos, log, pi, e."
```
