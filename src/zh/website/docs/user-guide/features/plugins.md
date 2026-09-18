---
sidebar_position: 11
sidebar_label: "Plugins"
title: "Plugins"
description: "Extend Hermes with custom tools, hooks, and integrations via the plugin system"
---

# 插件

Hermes 拥有插件系统，允许用户在无需修改核心代码的情况下添加自定义工具、钩子以及集成功能。

如果您想为自己、团队或某个项目创建自定义工具，这通常是最佳途径。开发者指南中的[添加工具](/developer-guide/adding-tools)页面介绍了位于 `tools/` 目录及 `toolsets.py` 文件中的内置 Hermes 核心工具。

**→ [构建 Hermes 插件](/developer-guide/plugins)** — 提供包含完整可运行示例的分步指导。

## 快速概览

只需将一个包含 `plugin.yaml` 配置文件及 Python 代码的目录放入 `~/.hermes/plugins/` 即可：

```
~/.hermes/plugins/my-plugin/
├── plugin.yaml      # manifest
├── __init__.py      # register() — wires schemas to handlers
├── schemas.py       # tool schemas (what the LLM sees)
└── tools.py         # tool handlers (what runs when called)
```

启动 Hermes 后，您的自定义工具会与内置工具一同显示，模型可以立即调用这些工具。

### 最简可用示例

以下是一个完整的插件示例，它新增了一个 `hello_world` 工具，并通过钩子功能记录每一次工具调用。

**`~/.hermes/plugins/hello-world/plugin.yaml`**

```yaml
name: hello-world
version: "1.0"
description: A minimal example plugin
```

**`~/.hermes/plugins/hello-world/__init__.py`**

```python
"""Minimal Hermes plugin — registers a tool and a hook."""

import json


def register(ctx):
    # --- Tool: hello_world ---
    schema = {
        "name": "hello_world",
        "description": "Returns a friendly greeting for the given name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet",
                }
            },
            "required": ["name"],
        },
    }

    def handle_hello(params, **kwargs):
        del kwargs
        name = params.get("name", "World")
        return json.dumps({"success": True, "greeting": f"Hello, {name}!"})

    ctx.register_tool(
        name="hello_world",
        toolset="hello_world",
        schema=schema,
        handler=handle_hello,
    )

    # --- Hook: log every tool call ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] tool called: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入`~/.hermes/plugins/hello-world/`目录中，重启Hermes后，模型即可立即调用`hello_world`函数。每次工具被调用时，该钩子都会输出一条日志记录。

面向模型的工具描述应放在`schema["description"]`字段中。可选的`ctx.register_tool(description=...)`参数属于独立的`ToolEntry`注册表元数据：若未提供该参数，则默认使用架构描述中的内容；但对于缺少`description`字段的架构，Hermes不会将其复制回去。建议将相关描述统一定义在架构中。如果同时提供了这两个值，需确保它们保持一致，因为模型最终会使用架构中的描述。

位于`./.hermes/plugins/`目录下的项目级插件默认处于禁用状态。仅对于可信的代码库，才可在启动Hermes之前通过设置`HERMES_ENABLE_PROJECT_PLUGINS=true`来启用它们。

## 插件能实现的功能

下面列出的所有`ctx.*` API都可以在插件的`register(ctx)`函数中使用。

| Capability | How |
|-----------|-----|
| Add tools | `ctx.register_tool(name=..., toolset=..., schema=..., handler=...)` |
| Add hooks | `ctx.register_hook("post_tool_call", callback)` |
| Add slash commands | `ctx.register_command(name, handler, description)` — adds `/name` in CLI and gateway sessions |
| Dispatch tools from commands | `ctx.dispatch_tool(name, args)` — invokes a registered tool with parent-agent context auto-wired |
| Add CLI commands | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` — adds `hermes <plugin> <subcommand>` |
| Inject messages | `ctx.inject_message(content, role="user", session_key=...)` - see [Injecting Messages](#injecting-messages) |
| Ship data files | `Path(__file__).parent / "data" / "file.yaml"` |
| Bundle skills | `ctx.register_skill(name, path)` — namespaced as `plugin:skill`, loaded via `skill_view("plugin:skill")` |
| Gate on env vars | `requires_env: [API_KEY]` in plugin.yaml — prompted during `hermes plugins install` |
| Distribute via pip | `[project.entry-points."hermes_agent.plugins"]` |
| Register a gateway platform (Discord, Telegram, IRC, …) | `ctx.register_platform(name, label, adapter_factory, check_fn, ...)` — see [Adding Platform Adapters](/developer-guide/adding-platform-adapters) |
| Register an image-generation backend | `ctx.register_image_gen_provider(provider)` — see [Image Generation Provider Plugins](/developer-guide/image-gen-provider-plugin) |
| Register a video-generation backend | `ctx.register_video_gen_provider(provider)` — see [Video Generation Provider Plugins](/developer-guide/video-gen-provider-plugin) |
| Register a context-compression engine | `ctx.register_context_engine(engine)` — see [Context Engine Plugins](/developer-guide/context-engine-plugin) |
| Register a terminal execution backend (cloud sandbox) | `ctx.register_terminal_environment_provider(provider)` — see [Terminal Environment Plugins](/developer-guide/terminal-environment-plugin) |
| Route human approval prompts | `ctx.register_approval_transport(name, present_fn)` — see [Approval transports](#approval-transports) |
| Register a memory backend | Subclass `MemoryProvider` in `plugins/memory/<name>/__init__.py` — see [Memory Provider Plugins](/developer-guide/memory-provider-plugin) (uses a separate discovery system) |
| Run a host-owned LLM call | `ctx.llm.complete(...)` / `ctx.llm.complete_structured(...)` — borrow the user's active model + auth for a one-shot completion with optional JSON schema validation. See [Plugin LLM Access](/developer-guide/plugin-llm-access) |
| Call an MCP tool (capability-gated) | `ctx.call_mcp(server, tool, arguments, timeout=30)` — see [Calling MCP servers from plugins](#calling-mcp-servers-from-plugins) |
| Register an inference backend (LLM provider) | `register_provider(ProviderProfile(...))` in `plugins/model-providers/<name>/__init__.py` — see [Model Provider Plugins](/developer-guide/model-provider-plugin) (uses a separate discovery system) |

## 插件发现

| 来源 | 路径 | 适用场景 |
|------|------|----------|
| 内置 | `<repo>/plugins/` | 随 Hermes 一同提供——详见[内置插件](/user-guide/features/built-in-plugins) |
| 用户自定义 | `~/.hermes/plugins/` | 个人自定义插件 |
| 项目专用 | `.hermes/plugins/` | 项目特定的插件（需设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip | `hermes_agent.plugins` entry_points | 分布式安装的包 |
| Nix | `services.hermes-agent.extraPlugins` / `extraPythonPackages` | NixOS 声明式安装——详见[Nix 设置](/getting-started/nix-setup#plugins) |

当插件名称冲突时，后续来源的设置会覆盖之前的设置，因此与内置插件同名的用户自定义插件将会取代该内置插件。

### 插件子类别

在每种来源中，Hermes 还能识别子类别目录，这些目录可将插件引导至专门的发现系统：

| 子目录 | 包含内容 | 发现机制 |
|---|---|---|
| `plugins/`（根目录） | 通用插件——包括工具、钩子、斜杠命令、CLI命令以及预集成技能 | `PluginManager`（类型为 `standalone` 或 `backend`） |
| `plugins/platforms/<名称>/` | 网关通道适配器（通过 `ctx.register_platform()` 注册） | `PluginManager`（类型为 `platform`，层级更深一层） |
| `plugins/image_gen/<名称>/` | 图像生成后端（通过 `ctx.register_image_gen_provider()` 注册） | `PluginManager`（类型为 `backend`，层级更深一层） |
| `plugins/memory/<名称>/` | 内存提供器（`MemoryProvider` 的子类） | `plugins/memory/__init__.py` 中的**专用加载器**（类型为 `exclusive`——同一时间仅允许一个处于激活状态） |
| `plugins/context_engine/<名称>/` | 上下文压缩引擎（通过 `ctx.register_context_engine()` 注册） | `plugins/context_engine/__init__.py` 中的**专用加载器**（同一时间仅允许一个处于激活状态） |
| `plugins/model-providers/<名称>/` | 大语言模型提供器配置文件（通过 `register_provider(ProviderProfile(...))` 注册） | `providers/__init__.py` 中的**专用加载器**（在首次调用 `get_provider_profile()` 时才会延迟扫描） |
位于 `~/.hermes/plugins/model-providers/<name>/` 目录下的用户自定义插件会覆盖同名称的默认模型提供程序（在 `register_provider()` 函数中遵循“后写入者胜出”的规则），因此无需修改任何代码仓库即可替换内置的提供程序配置。而内存提供程序则适用相反的规则：对于位于 `~/.hermes/plugins/memory/<name>/` 的自定义插件，在名称冲突时**默认提供的程序会优先生效**（顺序为：默认提供程序 → 用户自定义提供程序 → 项目级提供程序 → 启动点；最先出现的配置生效），因此用户自定义的内存提供程序必须拥有唯一的名称。

## 插件为可选启用状态（少数情况除外）

**常规插件以及用户安装的后端服务默认处于禁用状态**——系统虽能检测到它们（因此它们会显示在 `hermes plugins` 和 `/plugins` 列表中），但除非你在 `~/.hermes/config.yaml` 文件的 `plugins.enabled` 设置中加入该插件的名称，否则不会加载其相关的钩子或工具功能。这样一来，未经用户明确授权，第三方代码便无法运行。

```yaml
plugins:
  enabled:
    - my-tool-plugin
    - disk-cleanup
  disabled:       # optional deny-list — always wins if a name appears in both
    - noisy-plugin
  # Optional: wall-clock cap (seconds) for timeout-bounded in-process Python
  # plugin hook callbacks (hot-path observers + pre_tool_call). Default 30;
  # set 0 to disable; values above 600 are clamped. Timed-out pre_tool_call
  # callbacks fail closed (block the tool). Caller-thread hooks such as
  # subagent_stop are never moved onto a timeout worker.
  # Shell hooks keep their own per-entry timeout under the top-level hooks: key.
  hook_callback_timeout: 30
```

三种改变状态的方式：

```bash
hermes plugins                    # interactive toggle (space to check/uncheck)
hermes plugins enable <name>      # add to allow-list
hermes plugins disable <name>     # remove from allow-list + add to disabled
```

执行 `hermes plugins install owner/repo` 命令后，系统会询问“现在启用 ‘name’ 功能吗？[y/N]”——默认答案为否。若通过 `--enable` 或 `--no-enable` 参数进行脚本化安装，则可跳过此提示。

为确保安装结果可复现，需指定一个完整的不可变提交版本（标签、分支以及简写形式的 SHA 值均不可接受）：

```bash
hermes plugins install owner/repo --ref 0123456789abcdef0123456789abcdef01234567
```

Hermes 会检出该独立的提交，确认 `HEAD` 值与指定的 SHA 完全一致，随后将标准源地址、已安装的版本号以及固定状态记录在当前配置文件中。`hermes plugins update` 命令不会移动已被固定的插件；若需更换版本，需使用 `hermes plugins install <source> --force --ref <new-commit>` 明确指定新的提交地址。配置文件中的本地安装元数据不包含任何配置值、环境变量、机密信息或权限授予内容。

### 从私有仓库安装插件

`hermes plugins install` 以非交互模式执行克隆操作（不会询问用户名或密码），因此私有仓库需要提供 Hermes 能够自行获取的认证凭证。对于 `https://` 协议的源地址，Hermes 会按以下顺序尝试获取凭证：

1. 来自 `.env` 文件的 `GITHUB_TOKEN` 或 `GH_TOKEN`（仅适用于 GitHub 仓库）。
2. `gh` CLI 的登录功能（`gh auth login`），同样仅支持 GitHub 仓库。
3. 该托管平台的 git 凭证助手功能（`git credential fill`）——若已存储相应凭证，则可适用于 GitLab、Bitbucket 以及自托管服务器。

这些凭证仅作为一次性 HTTP 请求头在安装或更新操作中使用，绝不会被写入插件的 `.git/config` 文件或安装元数据中。对于 SSH 协议的源地址（`git@host:owner/repo.git`），认证过程仍会像以往一样通过 ssh-agent 完成。`hermes plugins update` 命令、从 git 仓库获取的 MCP 插件安装内容，以及从 git URL 下载的配置文件分发，均遵循相同的凭证获取逻辑。

### 允许列表不管控的内容

有多种类型的插件可绕过 `plugins.enabled` 的限制——它们属于 Hermes 的内置功能，若默认被禁用将会导致基本功能无法正常使用：

| 插件类型 | 启用方式 |
|---|---|
| **内置平台插件**（位于 `plugins/platforms/` 下的 IRC、Teams 等） | 会自动加载，从而确保所有已打包的网关通道均可使用。具体某个通道的启用则通过 `config.yaml` 中的 `gateway.platforms.<名称>.enabled` 来控制。 |
| **内置后端**（位于 `plugins/image_gen/` 下的图像生成提供商等） | 会自动加载，从而使默认后端能够直接正常工作。后端的选取则通过 `config.yaml` 中的 `<类别>.provider` 来实现（例如 `image_gen.provider: openai`）。 |
| **内存提供商**（位于 `plugins/memory/` 下） | 系统会自动发现所有此类提供商，且仅有一个处于激活状态，具体由 `config.yaml` 中的 `memory.provider` 指定。 |
| **上下文引擎**（位于 `plugins/context_engine/` 下） | 系统会自动发现所有此类引擎，且仅有一个处于激活状态，具体由 `config.yaml` 中的 `context.engine` 指定。 |
| **模型提供商**（位于 `plugins/model-providers/` 下） | 该目录下的所有内置提供商都将在首次调用 `get_provider_profile()` 时被自动发现并注册。用户可通过 `--provider` 参数或 `config.yaml` 逐个选择所需的提供商。 |
| **通过 Pip 安装的 `backend` 插件** | 需通过 `plugins.enabled` 手动启用（与普通插件规则相同）。 |
| **用户自行安装的平台**（位于 `~/.hermes/plugins/platforms/` 下） | 同样需要通过 `plugins.enabled` 手动启用——第三方网关适配器则必须获得明确授权才能使用。 |
简而言之：**预置的“始终可用”基础设施会自动加载；第三方通用插件则需手动启用。** `plugins.enabled` 允许列表专门用于管控用户放入 `~/.hermes/plugins/` 目录中的任意代码。

### 审批传输方式

审批传输方式用于改变用户**查看及回复**现有 Hermes 工具审批请求的途径。它并不决定某个命令是否需要审批，也不属于授权策略 API。

```python
def present(request):
    # Deliver request.command and request.description to your UI, wait for
    # its authenticated human response, then return a request-bound decision.
    choice = send_to_my_ui_and_wait(request)  # once/session/always/deny
    return request.respond(choice)


def register(ctx):
    ctx.register_approval_transport("my-ui", present)
```

`present` 操作可以是同步的，也可以是异步的。Hermes 会在受限的工作线程上执行该操作，并强制遵循标准的 `approvals.timeout` 时间限制，即便插件本身并未设定此类限制。请求内容是不可更改的，其中包含经过脱敏处理的显示文本、请求发起端的呈现类型（`cli` 或 `gateway`）、端点超时时间、允许的选择选项，以及一个不可见的请求 ID/哈希值。插件需返回 `request.respond(choice)` 的执行结果；若传入的是无限制结构的字典，或是过时或已被修改的请求 ID/哈希值，该请求将被拒绝。此外，插件不得返回请求发起端未允许的作用域（例如，在仅允许执行一次的请求中却使用 `always` 作用域）。

仅完成注册操作是远远不够的。要启用插件并明确指定其传输方式，还需要分别进行同意操作：

```yaml
plugins:
  enabled: [my-approval-plugin]

security:
  approval:
    transport: my-ui
    transport_fallback: deny     # default
```

默认情况下，传输异常、超时、注册不可用、无效选项以及过期的响应都会被拒绝。若希望在所选传输方式失败时，在常规的 CLI/TUI/gateway/ACP 界面上刻意显示提示信息，可设置 `transport_fallback: builtin`。若未明确启用此选项，Hermes 绝不会在其他界面显示该提示。

Hermes 仍保留着硬性限制模块、sudo-stdin 保护机制、用户拒绝规则、请求绑定功能、允许的操作范围、数据持久化功能、钩子机制以及最终授权流程。在任何传输回调之前，硬性限制命令都会被阻止。该接口**刻意不设置插件审批策略、自动允许回调的功能，以及必需的 `pre_tool_call` 策略**。未来的审批策略功能或许会采用插件能力同意模型，但传输方式的选择并不会赋予此类功能。

### 现有用户的迁移方案

当您升级到支持可选插件的 Hermes 版本（配置架构 v21+）时，那些已安装在 `~/.hermes/plugins/` 目录下且未被列入 `plugins.disabled` 文件中的用户插件，将会**自动继承原有设置并纳入 `plugins.enabled` 列表**，您的现有配置依然可以正常使用。而预装的独立插件则不会自动继承——即便是现有用户也必须手动进行启用操作。（由于从一开始就不受限制，预装的平台/后端插件从来无需进行此类继承处理。）

## 可用的钩子功能

插件可以注册目前 `hermes_cli.plugins.VALID_HOOKS` 所支持的 26 种生命周期事件。关于这些事件的精确触发时机、返回值处理方式、数据字段以及隐私相关说明，**[事件钩子目录](/user-guide/features/hooks#shipped-plugin-hook-catalog)** 是权威参考。

| 描述性类别 | 已提供的钩子 |
|---|---|
| **指令/控制** | `pre_tool_call`、`pre_llm_call`、`pre_verify`、`pre_gateway_dispatch` |
| **转换** | `transform_tool_result`、`transform_terminal_output`、`transform_llm_output`、`pre_transcription` |
| **观察者** | `post_tool_call`、`post_llm_call`、`pre_api_request`、`post_api_request`、`api_request_error`、`on_stream_start`、`on_stream_delta`、`on_stream_end`、`on_interim_message`、`on_session_start`、`on_session_end`、`on_session_finalize`、`on_session_reset`、`on_skill_lifecycle`、`subagent_start`、`subagent_stop`、`pre_approval_request`、`post_approval_response`、`pre_command`、`kanban_task_claimed`、`kanban_task_completed`、`kanban_task_blocked` |

上述类别仅用于描述当前的行为规范，并不构成未来命名规则的依据。插件中间件仍属于独立的注册系统/接口。
## 插件类型

Hermes 支持四种类型的插件：

| 类型 | 功能 | 选择方式 | 所在路径 |
|------|------|----------|----------|
| **通用插件** | 添加工具、钩子、斜杠命令及 CLI 命令 | 多选（启用/禁用） | `~/.hermes/plugins/` |
| **内存提供器** | 替换或扩展内置内存功能 | 单选（仅一个处于激活状态） | `plugins/memory/` |
| **上下文引擎** | 替换内置的上下文压缩器 | 单选（仅一个处于激活状态） | `plugins/context_engine/` |
| **模型提供器** | 指定推理后端（如 OpenRouter、Anthropic 等） | 多注册，通过 `--provider` 或 `config.yaml` 选择 | `plugins/model-providers/` |

内存提供器和上下文引擎属于**提供器插件**——同一类型中只能有一个处于激活状态。模型提供器也是插件，但可以同时加载多个；用户需通过 `--provider` 或 `config.yaml` 逐个进行选择。通用插件则可以以任意组合方式启用。

## 可插拔接口——各类型对应文档位置

上表列出了四种插件类别，但在“通用插件”中，`PluginContext` 还提供了多个独立的扩展点——此外，Hermes 还支持 Python 插件系统之外的扩展方式（如配置驱动的后端、shell 钩子命令、外部服务器等）。请使用此表格查找与您想要开发的功能相匹配的文档：

| Want to add… | How | Authoring guide |
|---|---|---|
| A **tool** the LLM can call | Python plugin — `ctx.register_tool()` | [Build a Hermes Plugin](/developer-guide/plugins) · [Adding Tools](/developer-guide/adding-tools) |
| A **lifecycle hook** (pre/post LLM, session start/end, tool filter) | Python plugin — `ctx.register_hook()` | [Hooks reference](/user-guide/features/hooks) · [Build a Hermes Plugin](/developer-guide/plugins) |
| A **slash command** for the CLI / gateway | Python plugin — `ctx.register_command()` | [Build a Hermes Plugin](/developer-guide/plugins) · [Extending the CLI](/developer-guide/extending-the-cli) |
| A **subcommand** for `hermes <thing>` | Python plugin — `ctx.register_cli_command()` | [Extending the CLI](/developer-guide/extending-the-cli) |
| A bundled **skill** that your plugin ships | Python plugin — `ctx.register_skill()` | [Creating Skills](/developer-guide/creating-skills) |
| An **inference backend** (LLM provider: OpenAI-compat, Codex, Anthropic-Messages, Bedrock) | Provider plugin — `register_provider(ProviderProfile(...))` in `plugins/model-providers/<name>/` | **[Model Provider Plugins](/developer-guide/model-provider-plugin)** · [Adding Providers](/developer-guide/adding-providers) |
| A **gateway channel** (Discord / Telegram / IRC / Teams / etc.) | Platform plugin — `ctx.register_platform()` in `plugins/platforms/<name>/` | [Adding Platform Adapters](/developer-guide/adding-platform-adapters) |
| A **memory backend** (Honcho, Mem0, Supermemory, …) | Memory plugin — subclass `MemoryProvider` in `plugins/memory/<name>/` | [Memory Provider Plugins](/developer-guide/memory-provider-plugin) |
| A **context-compression strategy** | Context-engine plugin — `ctx.register_context_engine()` | [Context Engine Plugins](/developer-guide/context-engine-plugin) |
| An **image-generation backend** (DALL·E, SDXL, …) | Backend plugin — `ctx.register_image_gen_provider()` | [Image Generation Provider Plugins](/developer-guide/image-gen-provider-plugin) |
| A **video-generation backend** (Veo, Kling, Pixverse, Grok-Imagine, Runway, …) | Backend plugin — `ctx.register_video_gen_provider()` | [Video Generation Provider Plugins](/developer-guide/video-gen-provider-plugin) |
| A **TTS backend** (any CLI — Piper, VoxCPM, Kokoro, xtts, voice-cloning scripts, …) | Config-driven (recommended) — declare under `tts.providers.<name>` with `type: command` in `config.yaml`. OR Python backend plugin — `ctx.register_tts_provider()` for Python-SDK / streaming engines that need more than a shell template. | [TTS Setup](/user-guide/features/tts#custom-command-providers) · [Python plugin guide](/user-guide/features/tts#python-plugin-providers) |
| An **STT backend** (any CLI — whisper.cpp, custom whisper binary, local ASR CLI) | Config-driven (recommended) — declare under `stt.providers.<name>` with `type: command` in `config.yaml`, or set `HERMES_LOCAL_STT_COMMAND` for the legacy single-command escape hatch. OR Python backend plugin — `ctx.register_transcription_provider()` for Python-SDK engines (OpenRouter, SenseAudio, Gemini-STT, etc.). | [STT Setup](/user-guide/features/tts#stt-custom-command-providers) · [Python plugin guide](/user-guide/features/tts#python-plugin-providers-stt) |
| **External tools via MCP** (filesystem, GitHub, Linear, Notion, any MCP server) | Config-driven — declare `mcp_servers.<name>` with `command:` / `url:` in `config.yaml`. Hermes auto-discovers the server's tools and registers them alongside built-ins. | [MCP](/user-guide/features/mcp) |
| **Additional skill sources** (custom GitHub repos, private skill indexes) | CLI — `hermes skills tap add <repo>` | [Skills Hub](/user-guide/features/skills#skills-hub) · [Publishing a custom tap](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| **Gateway event hooks** (fire on `gateway:startup`, `session:start`, `agent:end`, `command:*`) | Drop `HOOK.yaml` + `handler.py` into `~/.hermes/hooks/<name>/` | [Event Hooks](/user-guide/features/hooks#gateway-event-hooks) |
| **Shell hooks** (run a shell command on events — notifications, audit logs, desktop alerts) | Config-driven — declare under `hooks:` in `config.yaml` | [Shell Hooks](/user-guide/features/hooks#shell-hooks) |

:::note
并非所有插件都是 Python 插件。某些扩展接口会刻意使用**基于配置的 Shell 命令**（如文本转语音、语音转文本功能以及 Shell 钩子），这样一来，您现有的任何 CLI 工具都无需编写 Python 代码即可成为插件。还有些则是**外部服务器**（MCP），智能体可连接到这些服务器并自动注册其中的工具。另外也有一些是采用自有清单格式的**直接替换目录**（网关钩子）。请根据您的应用场景选择合适的集成方式；上表中的开发指南分别介绍了占位符设置、工具发现方法及示例代码。
:::

## NixOS 声明式插件

在 NixOS 环境中，可以通过模块选项以声明式方式安装插件——无需使用 `hermes plugins install` 命令。详细信息请参阅**[Nix 设置指南](/getting-started/nix-setup#plugins)**。

```nix
services.hermes-agent = {
  # Directory plugin (source tree with plugin.yaml)
  extraPlugins = [ (pkgs.fetchFromGitHub { ... }) ];
  # Entry-point plugin (pip package)
  extraPythonPackages = [ (pkgs.python312Packages.buildPythonPackage { ... }) ];
  # Enable in config
  settings.plugins.enabled = [ "my-plugin" ];
};
```

声明式插件会以 `nix-managed-` 作为前缀进行链接——它们与手动安装的插件共存，且当从 Nix 配置中移除时会被自动清理。

## 插件管理

```bash
hermes plugins                               # unified interactive UI
hermes plugins list                          # table: enabled / disabled / not enabled
hermes plugins search <term>                 # search the Hermes plugin catalog
hermes plugins install <name>                # install a catalog entry (repo @ reviewed pinned SHA)
hermes plugins install user/repo             # install from Git, then prompt Enable? [y/N]
hermes plugins install user/repo --enable    # install AND enable (no prompt)
hermes plugins install user/repo --no-enable # install but leave disabled (no prompt)
hermes plugins update my-plugin              # pull latest (local edits are autostashed and re-applied)
hermes plugins remove my-plugin              # uninstall
hermes plugins enable my-plugin              # add to allow-list
hermes plugins disable my-plugin             # remove from allow-list + add to disabled
hermes plugins capabilities [my-plugin]      # declared vs granted capabilities
```

### 一键安装链接（桌面端）

Hermes Desktop 已注册了 `hermes://` URL 协议，因此网站、README 文件或聊天消息均可直接链接到插件的安装页面：

```
hermes://plugin/install?repo=owner/repo            # main install link
hermes://plugin/install?repo=owner/repo&enable=1   # enable the agent plugin after install
hermes://plugin/install?repo=owner/repo&force=1    # replace an existing install
```

点击该链接后，Hermes会启动并显示一个**确认对话框**，其中包含仓库ID、“安装前须知”以及GitHub的浏览和克隆链接。随后系统会对该仓库进行浅层克隆，以确定其中包含哪些组件（即**代理插件**——后端Python代码，**桌面插件**——应用程序界面，或两者皆有）。用户可通过复选框选择所需组件并确认。在用户确认之前，任何组件都不会被安装；深度链接永远不会自动触发安装，而代理插件的安装流程也与`hermes plugins install`遵循相同的[安装时安全扫描](#install-time-security-scanning)机制。

混合型仓库（同一个仓库中同时包含代理插件和桌面插件）仅需要一个链接和一个对话框。即便没有链接，也可以通过**设置 → 插件 → 从Git安装**进入同一对话框。传统的`hermes://plugin-agent/…`和`hermes://plugin-desktop/…`URL格式也会被引导至同一个对话框。在开发版本（`npm run dev`）中，协议格式则为`hermes-dev://`。

对于网页应用而言，无需任何SDK——使用普通的锚点链接即可实现相同功能。

```html
<a href="hermes://plugin/install?repo=owner/repo&enable=1">Install in Hermes</a>
```

MCP 服务器也提供了相应的链接形式——详情请参阅
[添加到 Hermes 链接](/reference/mcp-config-reference#add-to-hermes-link)。

### 插件功能与权限授权

插件可以在其 `plugin.yaml` 文件中声明所需的特权主机接口：

```yaml
name: my-plugin
capabilities:
  - tools.override        # replace built-in tools
  - llm.model_override    # pick the model for host-owned LLM calls
```

当某个插件声明了自身具备的功能时，`hermes plugins install`（以及 `hermes plugins enable`）会显示该列表，并附上一行风险描述，同时仅询问一次用户是否同意。若用户同意，相关权限就会被记录在 `plugins.entries.<id>.granted_capabilities` 中，同时还会附带同意操作的哈希值与时间戳。如果用户拒绝，插件虽仍处于启用状态，但这些功能将被禁用——一个行为良好的插件会通过 `ctx.has_capability()` 方法进行检测，并以优雅的方式降级运行。

**更新后的重新授权机制：** 如果插件更新后声明了您尚未授权的新功能，`hermes plugins update` 会显示这些新增功能，并再次询问用户是否同意。在您明确同意之前，这些新功能仍处于禁用状态——插件更新绝不能悄悄扩大其访问权限。

**非交互式会话将直接终止操作：** 在没有 TTY 的环境下进行安装或更新时，虽然安装过程会完成，但声明的功能并不会被授予。若需后续授予这些权限，请以交互模式运行 `hermes plugins enable <id>` 命令。

您可以随时查看当前的状态：

```bash
hermes plugins capabilities             # all plugins with declared/granted capabilities
hermes plugins capabilities my-plugin   # one plugin, declared vs granted
```

能力标识与旧式的按功能配置门控机制是一一对应的，这些旧机制虽然仍可正常使用，但已被**弃用**，取而代之的是基于用户同意的流程：

| 能力 | 旧键值（`plugins.entries.<id>.…`） |
|---|---|
| `tools.override` | `allow_tool_override` |
| `llm.provider_override` | `llm.allow_provider_override` |
| `llm.model_override` | `llm.allow_model_override` |
| `llm.agent_id_override` | `llm.allow_agent_id_override` |
| `llm.profile_override` | `llm.allow_profile_override` |
| `llm.task_override` | `llm.allow_task_override` |
| `gateway.platform_actions` | `allow_platform_actions` |

只要该能力已被授予权限，或旧键值已被设置，对应的门控就会处于开放状态——现有的配置将保持不变，继续正常工作。

:::警告：非沙箱环境
这些能力机制属于**同意与审计层面**的功能，而非隔离功能。插件以常规的进程内 Python 程序形式运行，因此恶意插件可以无视所有此类门控限制。授予某项能力意味着用户对插件开发者的信任，但这并不等同于代码审计，Hermes 也未对插件代码进行过审查。请仅从您信任的来源安装插件。
:::

### 平台操作

`ctx.platform_actions` 为插件提供了一组最基础的、基于权限控制的操作指令集，使得插件能够通过实时网关适配器注册表在已连接的聊天平台上执行操作——这是替代直接修改适配器代码的官方推荐方式。**该功能默认处于关闭状态**：每次调用都会重新检查 `gateway.platform_actions` 权限（旧键名为 `plugins.entries.<id>.allow_platform_actions`），若未获得授权，调用将返回结构化的错误信息而非实际执行操作。

v1 版本的操作指令（均为异步调用，均返回普通字典，且不会触发钩子调度）：

```python
result = await ctx.platform_actions.add_reaction(
    platform="telegram", chat_id="-100123", message_id="456", emoji="👍",
)
result = await ctx.platform_actions.set_thread_title(
    platform="discord", chat_id="123", thread_id="456", title="New title",
)
if not result["ok"]:
    print(result["error"], result.get("detail"))
```

成功响应的格式为 `{"ok": True, "action": <动词>}`。失败响应则为 `{"ok": False, "error": <错误代码>, "detail": <错误描述>}`，常用的错误代码包括：`capability_not_granted`、`invalid_argument`、`gateway_unavailable`、`unknown_platform`、`adapter_not_registered`、`adapter_disconnected`、`unsupported_platform_action`、`action_failed`。在执行操作之前，系统会先验证目标适配器是否存在且处于连接状态；若适配器已断开或不存在，系统会返回结构化的错误信息，而不会抛出异常。

v1版本支持的平台为Telegram和Discord。在Telegram中，`add_reaction`命令用于**设置**机器人的表情反应（Bot API会替换之前的表情反应，而非叠加多个）。无论操作是否被允许，系统都会将操作记录到日志中，其中包含插件ID、动词、平台信息以及操作结果。

:::warning 安全提示
平台操作属于“以机器人形式进行消息处理”的功能：一旦获得授权，插件即可在网关机器人能够访问的任何聊天中设置表情反应或重命名主题，而不仅限于触发该功能的聊天。请仅将`gateway.platform_actions`权限授予您信任的插件，并优先选择那些会明确说明其可执行操作的插件。按照#64176号设计修正案的规划，直接访问平台的原始SDK数据/处理功能**并不属于当前接口范围**——该功能需要单独的权限`gateway.raw_events`，且带有“无稳定性保障”的标签，同时拥有独立的设计方案，目前尚未正式上线。
:::

### 发现插件——Hermes插件目录

`hermes plugins search <term>` 用于查询**Hermes 插件目录**——该目录由 hermes-agent 仓库（位于 `plugin-catalog/`）中维护，经过精心筛选并通过 SHA 值锁定版本。搜索结果会涵盖插件名称、描述以及所声明的工具信息。

```bash
hermes plugins search telegram    # search the catalog
hermes plugins browse             # browse every entry
hermes plugins info <name>        # full details for one entry
```

找到插件后，可直接使用其名称进行安装——该名称会指向对应条目在**固定提交SHA值**下的仓库地址，同时系统的目录来源信息也会被记录下来。这样一来，即便目录位置发生变动，执行 `hermes plugins update` 命令时仍可重新固定该插件的位置。

```bash
hermes plugins install <catalog-name>
```

明确的 `owner/repo` 或 Git-URL 标识符不会被纳入目录管理，而是会被标记为自定义（未经审核）的来源。而通过明确的 `--ref <40字符的提交SHA>` 参数，则可固定使用某个自定义安装版本。

有关完整的信任模型、准入 CI 流程以及提交工作流，请参阅 [插件目录](./plugin-catalog.md)。

:::warning 已收录 ≠ 已审核
目录中的条目仅表示该条目的元数据及声明的功能已在准入阶段经过审核——**这并不等同于代码审计**。安装过程仍需遵循常规的同意流程（插件默认处于禁用状态，启用需手动操作，且工具覆盖权限还需单独授权）。在启用某个插件之前，请先查看其源代码。
:::

### 插件包

**插件包**是一种声明式的、可共享的 YAML 文件（`hermes-pack.yaml`），用于固定一组插件——类似于分享游戏模组包。安装插件包后，实际上只是将其中的插件作为普通固定安装项进行部署；在运行时并不会生成任何新内容。

```yaml
name: voice-assistant-pack
description: STT + streaming TTS + approval relay
author: hyper
version: 1.0.0
plugins:
  - name: hermes-telegram-business       # bare plugin-catalog name…
    ref: e905f3bc5eeaa5a9dab9bc5155601b3ebec75757
  - repo: owner/approval-relay           # …or explicit owner/repo (or git URL)
    ref: 8f3c2d1a9b4e5f6071829304a5b6c7d8e9f00112
    subdir: plugins/relay                # optional monorepo path
config:                                  # optional, non-secret seeds only
  hermes-media-studio:
    default_model: flux-3
skills: []                               # declared list only (not auto-installed yet)
```

```bash
hermes plugins pack show ./hermes-pack.yaml     # dry-run review
hermes plugins pack install ./hermes-pack.yaml  # review → confirm → install
hermes plugins pack export > hermes-pack.yaml   # snapshot the current install
hermes plugins pack export --enabled-only       # only plugins.enabled
```

**供应链状态监控。** 每个条目的 `ref` 必须为长度恰好为 40 位的提交 SHA 值——标签和分支名称将被拒绝，并会显示与插件目录相同的错误提示。通过 `hermes plugins install --ref <sha>` 安装的插件会使用完全相同的固定安装路径，同时在 `plugins/.install-metadata.json` 中记录相同的来源信息，因此同一包的两次安装结果将完全一致。这些插件是基于[manifest v2 的字段](/developer-guide/plugins)（如 `manifest_version`、`api_version`、`requires_plugins`）构建的——不过每个插件自身的清单仍会通过常规安装流程进行验证。

**同意操作绝不会以批量方式执行。** `pack install` 会先显示一个强制审核界面，列明所有插件、来源、固定的引用地址以及它们声明的功能能力，随后仅针对整个包的内容请求**一次**确认。之后，每个插件声明的功能能力将按照常规的逐个插件处理流程进行同意提示——这与单独执行 `hermes plugins install` 的方式完全相同。该命令不支持 `--yes` 选项，且非交互式会话也无法安装插件包。

**密钥绝不会随插件包一同传输。** `config:` 配置值仅限于非敏感的 `plugins.entries.<id>` 键——任何具有密钥特征的键名（如 `*token*`、`*key*`、`*password*` 等）、功能能力授权以及已废弃的 `allow_*` 信任机制都将在安装时被拒绝，且在导出时会被移除。需要使用密钥的插件需在自身的 `requires_env` 中进行声明，系统会在安装时按常规流程提示用户输入。`plugins.entries.<id>` 中已存在的用户自定义值始终会优先于插件包中的配置值。

**部分失败。** 各插件均为独立安装的；系统会针对每个插件报告故障情况，其余插件仍会继续运行。若有任何插件安装失败，命令将以非零状态退出。

**导出注意事项。** `pack export` 命令仅包含那些具有已知 Git 来源的插件（即通过 `hermes plugins install` 安装的插件）。仅能在本地运行的插件会在生成的 YAML 文件中以警告注释的形式列出，而不会作为可安装项出现。

`skills:` 列表会在安装时被解析并显示，但此时并不会自动安装这些技能——目前需要手动进行安装（使用命令 `hermes skills`）。将 skill-hub ID 集成到 pack install 功能中是后续计划中的改进内容。

### 安装时的安全扫描

每次执行 `hermes plugins install` 和 `hermes plugins update` 命令时，系统都会在激活插件之前对其执行静态安全扫描（该机制借鉴了 Claude Cowork 的技能与插件安全扫描功能）。扫描器会使用与 [Skills Hub 安全防护](/user-guide/features/skills) 相同的威胁模式引擎，用于检测凭证存储外泄、反向shell攻击、破坏性命令、持久化机制、代码混淆执行以及文档文件中的命令注入等风险。同时，该引擎也针对插件特性设置了例外规则：例如，从环境变量中读取**自身**API密钥的提供者插件（即符合文档中规定的 `requires_env` 模式的插件）不会被标记为异常。

扫描结果分为三种，与 Claude Cowork 的通过/警告/失败标准一致：

| 评估结果 | 行为表现 |
|---|---|
| **安全** | 正常安装，无额外输出 |
| **谨慎** | 会显示检测结果；需确认“仍要安装？[y/N]”（或使用 `--force` 参数） |
| **危险** | 安装将被阻止。`--force` 参数无法绕过此限制 |

当执行 `hermes plugins update` 命令时，若检测到的插件树存在危险评估结果，则该插件将会被禁用，直到您查看相关检测结果并重新启用它为止。

扫描功能默认处于开启状态；如需关闭，可在 `config.yaml` 文件中进行设置：

```yaml
plugins:
  scan_on_install: false
```

### 交互式用户界面

无需任何参数即可运行 `hermes plugins` 命令，这将打开一个综合性的交互式界面：

```
Plugins
  ↑↓ navigate  SPACE toggle  ENTER configure/confirm  ESC done

  General Plugins
 → [✓] my-tool-plugin — Custom search tool
   [ ] webhook-notifier — Event hooks
   [ ] disk-cleanup — Auto-cleanup of ephemeral files [bundled]

  Provider Plugins
     Memory Provider          ▸ honcho
     Context Engine           ▸ compressor
```

- **通用插件部分** — 支持复选框操作，可使用空格键切换状态。选中状态表示该插件被纳入 `plugins.enabled` 列表，未选中则表示被列入 `plugins.disabled` 列表（即明确禁用）。
- **提供商插件部分** — 会显示当前的选择情况。按下回车键可进入单选按钮界面，从中选择要启用的提供商。
- 打包在一起的插件会在同一列表中以 `[bundled]` 标签标示。

所选的提供商插件信息会被保存到 `config.yaml` 文件中：

```yaml
memory:
  provider: "honcho"      # empty string = built-in only

context:
  engine: "compressor"    # default built-in compressor
```

### 已启用、已禁用与未启用状态

插件存在以下三种状态之一：

| 状态 | 含义 | 是否在 `plugins.enabled` 中？ | 是否在 `plugins.disabled` 中？ |
|---|---|---|---|
| `enabled` | 在下一个会话中加载 | 是 | 否 |
| `disabled` | 明确禁用——即使处于 `enabled` 状态也不会加载 | （无关） | 是 |
| `not enabled` | 已被检测到但未被手动启用 | 否 | 否 |

新安装或随包提供的插件默认处于 `not enabled` 状态。使用 `hermes plugins list` 可查看这三种不同状态，从而区分哪些是明确被禁用的，哪些只是等待启用。

在正在运行的会话中，通过 `/plugins` 可查看当前已加载的插件列表。

## 注入消息

插件可通过 `ctx.inject_message()` 将消息注入到 CLI 对话或已知的网关会话中：

```python
# Active CLI conversation
ctx.inject_message("New data arrived from the webhook", role="user")

# Existing gateway conversation
ctx.inject_message(
    "New data arrived from the webhook",
    role="user",
    session_key="agent:main:telegram:dm:123456789",
)
```

**签名：** `ctx.inject_message(content: str, role: str = "user", *, session_key: str | None = None) -> bool`

在 CLI 模式下：

- 若智能体处于**空闲状态**（正在等待用户输入），该消息将被排队作为下一条输入，从而开启一个新的对话轮次。
- 若智能体正处于**对话进行中**（正在执行任务），该消息会中断当前操作——其效果等同于用户输入新消息后按下回车键。
- 对于非 `"user"` 角色的消息，内容前会加上 `[role]` 前缀（例如 `[system] ...`）。
- 若消息成功排队，则返回 `True`。

在网关模式下：

- `session_key` 是必需参数，且必须用于标识已存在的网关会话。它代表的是稳定的路由键，而非 CLI 会话 ID。  
- Hermes 会重用该会话中存储的平台信息、聊天记录、对话线程、用户资料以及历史对话内容。插件无法通过此 API 创建新的聊天路由。  
- 在发起处理之前，Hermes 会再次根据网关当前的授权规则校验已存储的路由。  
- 仅依赖适配器端或上游授权决策的路由将被拒绝，除非 Hermes 能够通过当前的核心允许列表、配对设置或显式的“全部允许”配置来重新验证这些路由。  
- 注入的文本始终被视为对话输入，无法用于调用斜杠命令、批准工具，也无法处理待处理的确认或澄清提示。  
- 在请求处理过程中，对应的路由和对话会被固定不变。如果主题变化导致路由改变，或在处理开始前会话发生切换，Hermes 会丢弃该请求。  
- 该请求会进入平台适配器的常规消息处理流程。正在使用的会话会直接使用现有的繁忙会话队列，而不会启动新的处理轮次。  
- 当实时网关接受请求以进行异步处理时，该函数会返回 `True`。但这并不表示代理的响应或平台的消息传递已经完成。  
- 若未提供 `session_key`、权限未被授予，或没有实时网关能够接收该请求，该函数将返回 `False`。在异步处理被接受后发现的未知或无法路由的 `session_key` 会被记录到网关日志中。
这使得遥控查看器、消息桥接工具或 Webhook 接收器等插件能够从外部来源向对话中发送消息。网关注入功能可将智能体的回复发送至外部消息平台。该功能默认对所有插件均处于禁用状态，您可以在 `config.yaml` 文件中为特定插件单独开启此功能：

```yaml
plugins:
  entries:
    my-plugin:
      allow_gateway_injection: true
```

:::warning
请仅将网关注入功能授予您信任的插件。Hermes 会检查该主机的 API 权限，并将其限制在现有的会话路由范围内，但由于 Python 插件是在进程内部运行的，因此此设置并不具备沙箱隔离功能。
:::

:::note
该插件 API 不会为外部进程提供公共 HTTP 端点或 CLI 命令。插件必须已知晓目标网关的 `session_key`，例如通过其自身的可信配置或先前保存的会话状态来获取该信息。
:::

## 从插件调用 MCP 服务器

`ctx.call_mcp()` 允许插件从任何钩子或工具处理程序中，以同步方式调用用户配置的 MCP 服务器上的工具。调用过程会通过 Hermes 内置的 MCP 客户端进行路由处理（该客户端具备与模型调用的 MCP 工具相同的连接机制、信任层级管控、断路器功能以及重连逻辑；绝不会使用并行客户端）。

```python
result = ctx.call_mcp(
    "knowledge_rag",            # server name from mcp.servers
    "query_knowledge",          # tool on that server
    {"query": "deploy runbook"},
    timeout=30,                 # seconds; clamped to 1–600
)
if result["ok"]:
    print(result["result"])
else:
    print("MCP error:", result["error"])
```

**签名：** `ctx.call_mcp(server: str, tool: str, arguments: dict | None = None, timeout: float = 30) -> dict`

该方法会返回一个结构稳定的响应格式：`{"ok": True, "result": ...}`（若服务器提供，则还会包含 `structuredContent` 字段），或者 `{"ok": False, "error": "..."}`。当响应数据大小超过 64 KB 时，系统会对其截断处理，并在响应中标记 `"truncated": True`。

### 安全性：默认禁用，按服务器单独授权

插件**默认情况下无权访问 MCP**。操作员需在 `config.yaml` 文件中为每个服务器单独授予访问权限：

```yaml
plugins:
  entries:
    my-plugin:
      mcp_allowlist: ["knowledge_rag", "github"]
```

- 若尝试调用列表之外的服务器，将会抛出 `PermissionError` 异常，并明确指出需要设置的配置键。
- 权限仅针对特定服务器和插件生效——不会赋予对所有已配置服务器的通用访问权限，同时也不支持使用 `"*"` 通配符。
- 每次调用都会受到强制超时限制（默认为30秒），从而防止挂起的MCP服务器阻塞调用它的钩子或工具处理流程。
- MCP服务器返回的内容是不可信的。请将 `result` 视为普通数据而非指令——在未经验证的情况下，切勿将其用于需要高权限的决策（如审批、命令执行）中。

:::warning
授予 `mcp_allowlist` 权限后，插件将获得与模型相同的该MCP服务器访问权限——包括服务器提供的所有具备写入功能的工具（但需受服务器的 `trust` 等级限制）。请仅授予插件确实需要的服务器访问权。
:::

如需了解处理程序契约、架构格式、钩子行为、错误处理以及常见错误等详细信息，请参阅**[完整指南](/developer-guide/plugins)**。
