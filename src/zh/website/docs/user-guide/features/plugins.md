---
sidebar_position: 11
sidebar_label: "Plugins"
title: "Plugins"
description: "Extend Hermes with custom tools, hooks, and integrations via the plugin system"
---

# 插件

Hermes 拥有插件系统，允许用户在无需修改核心代码的情况下添加自定义工具、钩子功能以及集成方案。

如果您希望为自己、团队或某个项目创建自定义工具，这通常是最佳途径。开发者指南中的[添加工具](/developer-guide/adding-tools)页面介绍了位于 `tools/` 目录及 `toolsets.py` 文件中的内置 Hermes 核心工具。

**→ [构建 Hermes 插件](/guides/build-a-hermes-plugin)** —— 提供包含完整可运行示例的分步指导。

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
        description="Return a friendly greeting for the given name.",
    )

    # --- Hook: log every tool call ---
    def on_tool_call(tool_name, params, result):
        print(f"[hello-world] tool called: {tool_name}")

    ctx.register_hook("post_tool_call", on_tool_call)
```

将这两个文件放入 `~/.hermes/plugins/hello-world/` 目录中，重启 Hermes 后，模型即可立即调用 `hello_world` 函数。每次工具被调用时，该钩子都会打印一条日志。

位于 `./.hermes/plugins/` 下的项目级插件默认处于禁用状态。只有在信任的代码库中使用时，才需在启动 Hermes 之前设置 `HERMES_ENABLE_PROJECT_PLUGINS=true` 来启用它们。

## 插件能实现的功能

以下所有 `ctx.*` API 都可在插件的 `register(ctx)` 函数中使用。

| 功能 | 实现方式 |
|------|---------|
| 添加工具 | `ctx.register_tool(name=..., toolset=..., schema=..., handler=...)` |
| 添加钩子 | `ctx.register_hook("post_tool_call", callback)` |
| 添加斜杠命令 | `ctx.register_command(name, handler, description)` —— 会在 CLI 和网关会话中生成 `/name` 命令 |
| 从命令中调用工具 | `ctx.dispatch_tool(name, args)` —— 调用已注册的工具，并自动传递父代理的上下文信息 |
| 添加 CLI 命令 | `ctx.register_cli_command(name, help, setup_fn, handler_fn)` —— 生成 `hermes <plugin> <subcommand>` 命令格式 |
| 注入消息 | `ctx.inject_message(content, role="user")` —— 详见 [注入消息](#injecting-messages) |
| 上传数据文件 | `Path(__file__).parent / "data" / "file.yaml"` |
| 打包技能 | `ctx.register_skill(name, path)` —— 以 `plugin:skill` 的命名空间形式存在，可通过 `skill_view("plugin:skill")` 加载 |
| 根据环境变量进行限制 | 在 plugin.yaml 中设置 `requires_env: [API_KEY]` —— 在执行 `hermes plugins install` 时会提示相关要求 |
| 通过 pip 分发 | `[project.entry-points."hermes_agent.plugins"]` |
| 注册网关平台（Discord、Telegram、IRC 等） | `ctx.register_platform(name, label, adapter_factory, check_fn, ...)` —— 详见 [添加平台适配器](/developer-guide/adding-platform-adapters) |
| 注册图像生成后端 | `ctx.register_image_gen_provider(provider)` —— 详见 [图像生成提供者插件](/developer-guide/image-gen-provider-plugin) |
| 注册视频生成后端 | `ctx.register_video_gen_provider(provider)` —— 详见 [视频生成提供者插件](/developer-guide/video-gen-provider-plugin) |
| 注册上下文压缩引擎 | `ctx.register_context_engine(engine)` —— 详见 [上下文引擎插件](/developer-guide/context-engine-plugin) |
| 注册内存后端 | 在 `plugins/memory/<name>/__init__.py` 中继承 `MemoryProvider` 类 —— 详见 [内存提供者插件](/developer-guide/memory-provider-plugin)（采用独立的发现机制） |
| 执行主机自有的 LLM 调用 | `ctx.llm.complete(...)` / `ctx.llm.complete_structured(...)` —— 借用用户的当前模型及认证信息进行一次性响应，同时支持可选的 JSON 模式验证。详见 [插件访问 LLM](/developer-guide/plugin-llm-access) |
| 注册推理后端（LLM 提供者） | 在 `plugins/model-providers/<name>/__init__.py` 中调用 `register_provider(ProviderProfile(...))` —— 详见 [模型提供者插件](/developer-guide/model-provider-plugin)（采用独立的发现机制） |

## 插件发现机制

| 来源 | 路径 | 适用场景 |
|------|------|----------|
| 内置捆绑 | `<repo>/plugins/` | 随 Hermes 一同提供的插件 —— 详见 [内置插件](/user-guide/features/built-in-plugins) |
| 用户自定义 | `~/.hermes/plugins/` | 个人使用的插件 |
| 项目专用 | `.hermes/plugins/` | 项目特定的插件（需设置 `HERMES_ENABLE_PROJECT_PLUGINS=true`） |
| pip 安装 | `hermes_agent.plugins` entry_points | 通过包管理器分发的插件 |
| Nix 安装 | `services.hermes-agent.extraPlugins` / `extraPythonPackages` | NixOS 声明式安装方式 —— 详见 [Nix 配置](/getting-started/nix-setup#plugins) |

当插件名称冲突时，后加载的来源会覆盖先加载的来源。因此，若用户自定义插件与内置插件名称相同，后者将被替换。

### 插件子类别

对于每种来源，Hermes 还能识别用于将插件路由到相应发现系统的子目录：

| 子目录 | 包含内容 | 发现系统 |
|---|---|---|
| `plugins/`（根目录） | 通用插件 —— 工具、钩子、斜杠命令、CLI 命令、内置技能 | `PluginManager`（类型为 `standalone` 或 `backend`） |
| `plugins/platforms/<name>/` | 网关通道适配器（通过 `ctx.register_platform()` 注册） | `PluginManager`（类型为 `platform`，层级更深一层） |
| `plugins/image_gen/<name>/` | 图像生成后端（通过 `ctx.register_image_gen_provider()` 注册） | `PluginManager`（类型为 `backend`，层级更深一层） |
| `plugins/memory/<name>/` | 内存提供者（继承 `MemoryProvider` 类） | `plugins/memory/__init__.py` 中的专用加载器（类型为 `exclusive` —— 一次仅一个生效） |
| `plugins/context_engine/<name>/` | 上下文压缩引擎（通过 `ctx.register_context_engine()` 注册） | `plugins/context_engine/__init__.py` 中的专用加载器（一次仅一个生效） |
| `plugins/model-providers/<name>/` | LLM 提供者配置文件（通过 `register_provider(ProviderProfile(...))` 注册） | `providers/__init__.py` 中的专用加载器（在首次调用 `get_provider_profile()` 时才会懒加载） |

位于 `~/.hermes/plugins/model-providers/<name>/` 和 `~/.hermes/plugins/memory/<name>/` 的用户自定义插件会覆盖同名内置插件 —— 在 `register_provider()` / `register_memory_provider()` 中遵循“后写入者胜出”的原则。只需将相关目录放入指定位置，即可在无需修改任何代码库配置的情况下替换内置插件。

## 插件为可选功能（少数情况除外）

**通用插件及用户安装的后端默认处于禁用状态** —— 系统虽能发现它们（因此会显示在 `hermes plugins` 和 `/plugins` 中），但除非你在 `~/.hermes/config.yaml` 的 `plugins.enabled` 列表中添加该插件的名称，否则其包含的钩子或工具都不会被加载。这一设计旨在防止未经用户明确许可就运行第三方代码。

```yaml
plugins:
  enabled:
    - my-tool-plugin
    - disk-cleanup
  disabled:       # optional deny-list — always wins if a name appears in both
    - noisy-plugin
```

三种切换状态的方式：

```bash
hermes plugins                    # interactive toggle (space to check/uncheck)
hermes plugins enable <name>      # add to allow-list
hermes plugins disable <name>     # remove from allow-list + add to disabled
```

执行 `hermes plugins install owner/repo` 命令后，系统会询问“现在启用 ‘name’ 吗？[y/N]”——默认答案为“否”。若使用 `--enable` 或 `--no-enable` 参数进行脚本化安装，则可跳过此提示。

### allow-list 不管控的内容

有几类插件不受 `plugins.enabled` 的限制——它们属于 Hermes 的内置功能，若被默认禁用将会导致核心功能失效：

| 插件类型 | 启用方式 |
|---|---|
| **内置平台插件**（位于 `plugins/platforms/` 下的 IRC、Teams 等） | 会自动加载，从而确保所有预装的网关通道均可使用。具体通道的启用状态则通过 `config.yaml` 中的 `gateway.platforms.<name>.enabled` 来控制。 |
| **内置后端**（位于 `plugins/image_gen/` 下的图像生成提供商等） | 会自动加载，使默认后端能够直接使用。后端的选择则通过 `config.yaml` 中的 `<category>.provider` 来指定（例如 `image_gen.provider: openai`）。 |
| **内存提供器**（位于 `plugins/memory/` 下） | 系统会自动发现所有可用内存提供器，但仅允许一个处于活跃状态，具体由 `config.yaml` 中的 `memory.provider` 指定。 |
| **上下文引擎**（位于 `plugins/context_engine/` 下） | 系统会自动发现所有上下文引擎，但仅允许一个处于活跃状态，具体由 `config.yaml` 中的 `context.engine` 指定。 |
| **模型提供器**（位于 `plugins/model-providers/` 下） | 该目录下的所有内置提供器会在首次调用 `get_provider_profile()` 时自动被发现并注册。用户可通过 `--provider` 参数或 `config.yaml` 逐个选择使用。 |
| **通过 Pip 安装的 `backend` 插件** | 需通过 `plugins.enabled` 手动启用（与普通插件规则相同）。 |
| **用户自行安装的平台插件**（位于 `~/.hermes/plugins/platforms/` 下） | 需通过 `plugins.enabled` 手动启用——第三方网关适配器则必须获得明确授权才能使用。 |

简而言之：**那些“始终可用”的内置基础设施会自动加载；而第三方通用插件则需要手动启用。** `plugins.enabled` 的 allow-list 专门用于管控用户放入 `~/.hermes/plugins/` 目录中的任意自定义代码。

### 现有用户的迁移方案

当您升级到支持插件可选启用的 Hermes 版本（配置架构 v21 及以上）时，之前已安装在 `~/.hermes/plugins/` 目录下、且未被列入 `plugins.disabled` 的用户插件，将会**自动继承**为已启用状态，无需额外操作，您的现有设置仍可正常使用。而那些预装的独立插件则不会自动继承此设置——即便是现有用户也必须手动进行启用操作。（由于内置的平台/后端插件从来就没有被设为受限状态，因此无需进行此类迁移。）

## 可用的钩子函数

插件可以为这些生命周期事件注册回调函数。详细信息、回调签名及示例请参阅 **[事件钩子页面](/user-guide/features/hooks#plugin-hooks)**。

| 钩子函数 | 触发时机 |
|------|-----------|
| [`pre_tool_call`](/user-guide/features/hooks#pre_tool_call) | 任何工具执行之前 |
| [`post_tool_call`](/user-guide/features/hooks#post_tool_call) | 任何工具返回之后 |
| [`pre_llm_call`](/user-guide/features/hooks#pre_llm_call) | 每轮对话开始时，在 LLM 循环之前——可通过返回 `{"context": "..."}` 的方式将上下文注入用户消息中[/user-guide/features/hooks#pre_llm_call] |
| [`post_llm_call`](/user-guide/features/hooks#post_llm_call) | 每轮对话开始后、LLM 循环结束后（仅限成功完成的对话轮次） |
| [`on_session_start`](/user-guide/features/hooks#on_session_start) | 新会话创建时（仅第一轮对话） |
| [`on_session_end`](/user-guide/features/hooks#on_session_end) | 每次调用 `run_conversation` 后，以及 CLI 退出时 |
| [`on_session_finalize`](/user-guide/features/hooks#on_session_finalize) | 当 CLI 或网关终止当前活跃会话时（如执行 `/new`、强制清理会话、通过 CLI 退出等） |
| [`on_session_reset`](/user-guide/features/hooks#on_session_reset) | 当网关更换新的会话密钥时（如执行 `/new`、/reset、/clear 指令，或因闲置时间过长而触发会话轮换） |
| [`subagent_stop`](/user-guide/features/hooks#subagent_stop) | 每个子代理在完成 `delegate_task` 任务后触发一次 |
| [`pre_gateway_dispatch`](/user-guide/features/hooks#pre_gateway_dispatch) | 网关收到用户消息后、进行身份验证和任务分发之前。可通过返回 `{"action": "skip" \| "rewrite" \| "allow", ...}` 的方式来控制流程走向。 |

## 插件类型

Hermes 共有四种类型的插件：

| 类型 | 功能 | 选择方式 | 存放位置 |
|---|---|---|----------|
| **通用插件** | 添加工具、钩子函数、斜杠命令及 CLI 命令 | 多选式（可分别启用/禁用） | `~/.hermes/plugins/` |
| **内存提供器** | 替换或扩展内置内存功能 | 单选式（仅允许一个处于活跃状态） | `plugins/memory/` |
| **上下文引擎** | 替换内置的上下文压缩机制 | 单选式（仅允许一个处于活跃状态） | `plugins/context_engine/` |
| **模型提供器** | 指定推理后端（如 OpenRouter、Anthropic 等） | 多次注册，最终由 `--provider` 参数或 `config.yaml` 指定使用哪个后端 | `plugins/model-providers/` |

内存提供器和上下文引擎属于**提供器插件**——同一类型中只能有一个处于活跃状态。模型提供器也属于插件类别，但允许多个同时加载；用户可通过 `--provider` 参数或 `config.yaml` 逐个选择使用。通用插件则可以以任意组合方式被启用。

## 可扩展的接口——对应需求可查阅的文档

上表列出了四种插件类别，但在“通用插件”中，`PluginContext` 还提供了多个独立的扩展点；此外，Hermes 还支持在 Python 插件系统之外的方式实现扩展（如通过配置文件定义的后端、基于 shell 的命令、外部服务器等）。请参考下表，根据您的需求找到相应的文档：

| 您想添加的功能 | 实现方式 | 开发指南 |
|---|---|---|
| LLM 可调用的**工具** | Python 插件——使用 `ctx.register_tool()` 方法 | [构建 Hermes 插件](/guides/build-a-hermes-plugin) · [添加工具](/developer-guide/adding-tools) |
| **生命周期钩子函数**（LLM 执行前后、会话开始/结束、工具过滤等） | Python 插件——使用 `ctx.register_hook()` 方法 | [钩子函数参考文档](/user-guide/features/hooks) · [构建 Hermes 插件](/guides/build-a-hermes-plugin) |
| 用于 CLI 或网关的**斜杠命令** | Python 插件——使用 `ctx.register_command()` 方法 | [构建 Hermes 插件](/guides/build-a-hermes-plugin) · [扩展 CLI 功能](/developer-guide/extending-the-cli) |
| `hermes <thing>` 命令的**子命令** | Python 插件——使用 `ctx.register_cli_command()` 方法 | [扩展 CLI 功能](/developer-guide/extending-the-cli) |
| 您的插件所包含的**内置技能** | Python 插件——使用 `ctx.register_skill()` 方法 | [创建技能](/developer-guide/creating-skills) |
| **推理后端**（LLM 提供商：兼容 OpenAI 的服务、Codex、Anthropic-Messages、Bedrock 等） | 提供器插件——在 `plugins/model-providers/<name>/` 目录下使用 `register_provider(ProviderProfile(...))` 方法注册 | **[模型提供器插件文档](/developer-guide/model-provider-plugin)** · [添加提供器](/developer-guide/adding-providers) |
| **网关通道**（Discord、Telegram、IRC、Teams 等） | 平台插件——在 `plugins/platforms/<name>/` 目录下使用 `ctx.register_platform()` 方法注册 | [添加平台适配器](/developer-guide/adding-platform-adapters) |
| **内存后端**（Honcho、Mem0、Supermemory 等） | 内存插件——在 `plugins/memory/<name>/` 目录下创建继承自 `MemoryProvider` 的子类 | [内存提供器插件文档](/developer-guide/memory-provider-plugin) |
| **上下文压缩策略** | 上下文引擎插件——使用 `ctx.register_context_engine()` 方法注册 | [上下文引擎插件文档](/developer-guide/context-engine-plugin) |
| **图像生成后端**（DALL·E、SDXL 等） | 后端插件——使用 `ctx.register_image_gen_provider()` 方法注册 | [图像生成提供器插件文档](/developer-guide/image-gen-provider-plugin) |
| **视频生成后端**（Veo、Kling、Pixverse、Grok-Imagine、Runway 等） | 后端插件——使用 `ctx.register_video_gen_provider()` 方法注册 | [视频生成提供器插件文档](/developer-guide/video-gen-provider-plugin) |
| **文本转语音后端**（任何 CLI 工具——如 Piper、VoxCPM、Kokoro、xtts、语音克隆脚本等） | 推荐使用配置文件驱动方式——在 `config.yaml` 中的 `tts.providers.<name>` 下声明，并指定 `type: command`。或者使用 Python 后端插件——对于需要更复杂功能的 Python SDK 或流式处理引擎，可使用 `ctx.register_tts_provider()` 方法注册 | [文本转语音设置指南](/user-guide/features/tts#custom-command-providers) · [Python 插件指南](/user-guide/features/tts#python-plugin-providers) |
| **语音转文本后端**（任何 CLI 工具——如 whisper.cpp、自定义 whisper 可执行文件、本地 ASR CLI 等） | 推荐使用配置文件驱动方式——在 `config.yaml` 中的 `stt.providers.<name>` 下声明，并指定 `type: command`。或者为旧版单命令模式设置 `HERMES_LOCAL_STT_COMMAND` 环境变量。或者使用 Python 后端插件——对于基于 Python SDK 的引擎（如 OpenRouter、SenseAudio、Gemini-STT 等），可使用 `ctx.register_transcription_provider()` 方法注册 | [语音转文本设置指南](/user-guide/features/tts#stt-custom-command-providers) · [Python 插件指南](/user-guide/features/tts#python-plugin-providers-stt) |
| **通过 MCP 接入的第三方工具**（文件系统、GitHub、Linear、Notion 以及任何支持 MCP 的服务器） | 推荐使用配置文件驱动方式——在 `config.yaml` 中的 `mcp_servers.<name>` 下声明，并指定 `command:` 或 `url:` 参数。Hermes 会自动发现该服务器提供的工具，并将其与内置工具一同注册 | [MCP 功能指南](/user-guide/features/mcp) |
| **额外的技能来源**（自定义 GitHub 仓库、私有技能索引等） | 通过 CLI 命令实现——执行 `hermes skills tap add <repo>` | [技能中心功能指南](/user-guide/features/skills#skills-hub) · [发布自定义技能接入点](/user-guide/features/skills#publishing-a-custom-skill-tap) |
| **网关事件钩子函数**（在 `gateway:startup`、`session:start`、`agent:end`、`command:*` 等事件触发时执行） | 将 `HOOK.yaml` 文件和 `handler.py` 文件放入 `~/.hermes/hooks/<name>/` 目录中 | [事件钩子函数指南](/user-guide/features/hooks#gateway-event-hooks) |
| **Shell 钩子函数**（在特定事件发生时运行 Shell 命令——如通知发送、审计日志记录、桌面提醒等） | 推荐使用配置文件驱动方式——在 `config.yaml` 中的 `hooks:` 部分进行声明 | [Shell 钩子函数指南](/user-guide/features/hooks#shell-hooks) |

:::note
并非所有功能都必须通过 Python 插件实现。有些扩展功能刻意采用了**基于配置文件的 Shell 命令**方式（如文本转语音、语音转文本、Shell 钩子函数），这样用户现有的任何 CLI 工具都能直接作为插件使用，无需编写 Python 代码。还有一些功能是**外部服务器**（如 MCP），代理程序会连接到这些服务器并自动注册其提供的工具。此外还有一类是**可直接插入的目录结构**（如网关钩子函数），它们拥有自己独立的配置格式。请根据您的实际应用场景选择合适的扩展方式；上表中的开发指南分别介绍了相关占位符用法、发现机制及示例。
:::

## NixOS 声明式插件安装

在 NixOS 系统中，可以通过模块选项以声明式方式安装插件——无需再使用 `hermes plugins install` 命令。详细信息请参阅 **[NixOS 安装指南](/getting-started/nix-setup#plugins)**。

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
hermes plugins install user/repo             # install from Git, then prompt Enable? [y/N]
hermes plugins install user/repo --enable    # install AND enable (no prompt)
hermes plugins install user/repo --no-enable # install but leave disabled (no prompt)
hermes plugins update my-plugin              # pull latest
hermes plugins remove my-plugin              # uninstall
hermes plugins enable my-plugin              # add to allow-list
hermes plugins disable my-plugin             # remove from allow-list + add to disabled
```

### 交互式用户界面

运行 `hermes plugins` 且不指定任何参数时，将会打开一个综合性的交互式界面：

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

- **通用插件部分** — 支持复选框操作，可用空格键切换状态。选中状态表示该插件被包含在 `plugins.enabled` 中，未选中则表示被列入 `plugins.disabled`（即明确禁用）。
- **提供商插件部分** — 显示当前的选择状态。按下回车键可进入单选菜单，在其中选择要启用的提供商。
- 打包在一起的插件会以 `[bundled]` 标签显示在同一列表中。

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
| `not enabled` | 已被检测到但未手动启用 | 否 | 否 |

新安装或随包提供的插件默认处于 `not enabled` 状态。使用 `hermes plugins list` 可查看这三种不同状态，从而区分哪些是明确被禁用的，哪些只是待启用状态。

在正在运行的会话中，通过 `/plugins` 可查看当前已加载的插件列表。

## 注入消息

插件可通过 `ctx.inject_message()` 将消息注入到当前对话中：

```python
ctx.inject_message("New data arrived from the webhook", role="user")
```

**签名：** `ctx.inject_message(content: str, role: str = "user") -> bool`

工作原理：

- 若智能体处于**空闲状态**（正在等待用户输入），该消息将被加入队列作为下一条输入，从而开启新的对话轮次。
- 若智能体正处于**对话执行中**，该消息会中断当前操作——其效果等同于用户输入新消息后按下回车键。
- 对于非 `"user"` 角色的消息，内容前会加上 `[role]` 前缀（例如 `[system] ...`）。
- 若消息成功加入队列，则返回 `True`；若不存在 CLI 参考对象（如在网关模式下），则返回 `False`。

此功能使得远程控制查看器、消息桥接工具或 Webhook 接收器等插件能够从外部来源向对话中注入消息。

:::note
`inject_message` 仅在 CLI 模式下可用。在网关模式下没有 CLI 参考对象，因此该方法会返回 `False`。
:::

如需了解处理程序契约、架构格式、钩子行为、错误处理以及常见错误等内容，请参阅**[完整指南](/guides/build-a-hermes-plugin)**。
