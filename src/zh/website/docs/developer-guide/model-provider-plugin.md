---
sidebar_position: 10
title: "Model Provider Plugins"
description: "How to build a model provider (inference backend) plugin for Hermes Agent"
---

# 构建模型提供者插件

模型提供者插件用于指定推理后端——即兼容 OpenAI 的接口、Anthropic Messages 服务器、Codex 风格的 Responses API，或是 Bedrock 原生界面——Hermes 可通过这些后端来路由 `AIAgent` 调用。所有内置提供者（OpenRouter、Anthropic、GMI、DeepSeek、Nvidia 等）均以此类插件的形式存在。第三方开发者只需在 `$HERMES_HOME/plugins/model-providers/` 目录下添加相应文件夹，而无需对代码库进行任何修改，即可自行创建插件。

:::提示
模型提供者插件属于第三种**提供者插件**。另外两种分别是[内存提供者插件](/developer-guide/memory-provider-plugin)（用于跨会话知识传递）和[上下文引擎插件](/developer-guide/context-engine-plugin)（用于上下文压缩策略）。这三种插件均遵循相同的构建模式：只需添加文件夹、定义配置文件，无需修改代码库。
:::

## 发现机制的工作原理

每当有代码调用 `get_provider_profile()` 或 `list_providers()` 时，`providers/__init__.py._discover_providers()` 函数才会被延迟加载并执行。插件发现顺序如下：

1. **内置插件** — `<repo>/plugins/model-providers/<name>/` — 随 Hermes 一同提供  
2. **用户自定义插件** — `$HERMES_HOME/plugins/model-providers/<name>/` — 可放置于任意目录；后续会话无需重启即可使用  
3. **已安装插件** — `$HERMES_HOME/plugins/<name>/`（通过 `hermes plugins install owner/repo` 命令克隆的插件所在位置）——仅当 `plugin.yaml` 中声明 `kind: model-provider` 时才会被导入；其余类型的插件均属于通用的 PluginManager 管理  
4. **旧版单文件格式** — `<repo>/providers/<name>.py` — 为树外可编辑安装方式提供兼容支持  

由于 `register_provider()` 采用“最后写入者胜出”的规则，**用户自定义插件会覆盖同名内置插件**。只需将 `$HERMES_HOME/plugins/model-providers/gmi/` 目录放入对应位置，即可在不修改源代码仓库的情况下替换内置的 GMI 配置文件。  

## 目录结构

```
plugins/model-providers/my-provider/
├── __init__.py       # Calls register_provider(profile) at module-level
├── plugin.yaml       # kind: model-provider + metadata (optional but recommended)
└── README.md         # Setup instructions (optional)
```

唯一必需的文件是 `__init__.py`。`plugin.yaml` 会被 `hermes plugins` 用于元数据查询，同时也会被通用的 PluginManager 用来将插件路由至相应的加载器；若没有该文件，通用加载器将会退而采用基于源文本的启发式方法进行处理。

## 最简示例——一个简单的 API 密钥提供器

```python
# plugins/model-providers/acme-inference/__init__.py
from providers import register_provider
from providers.base import ProviderProfile

acme = ProviderProfile(
    name="acme-inference",
    aliases=("acme",),
    display_name="Acme Inference",
    description="Acme — OpenAI-compatible direct API",
    signup_url="https://acme.example.com/keys",
    env_vars=("ACME_API_KEY", "ACME_BASE_URL"),
    base_url="https://api.acme.example.com/v1",
    auth_type="api_key",
    default_aux_model="acme-small-fast",
    fallback_models=(
        "acme-large-v3",
        "acme-medium-v3",
        "acme-small-fast",
    ),
)

register_provider(acme)
```

```yaml
# plugins/model-providers/acme-inference/plugin.yaml
name: acme-inference
kind: model-provider
version: 1.0.0
description: Acme Inference — OpenAI-compatible direct API
author: Your Name
```

就这样。上传这两个文件后，无需其他任何修改即可实现以下**自动关联**：

| 集成功能 | 所在文件 | 获取的内容 |
|---|---|---|
| 凭据解析 | `hermes_cli/auth.py` | 从配置文件中读取并填充 `PROVIDER_REGISTRY["acme-inference"]` |
| `--provider` CLI 参数 | `hermes_cli/main.py` | 支持接受 `acme-inference` 作为参数 |
| Hermes 模型选择器 | `hermes_cli/models.py` | 该提供者会出现在 `CANONICAL_PROVIDERS` 列表中，模型列表则从 `{base_url}/models` 获取 |
| Hermes 诊断工具 | `hermes_cli/doctor.py` | 对 `ACME_API_KEY` 进行健康检查，并探测 `{base_url}/models` 的可用性 |
| Hermes 设置向导 | `hermes_cli/config.py` | `ACME_API_KEY` 会被添加到 `OPTIONAL_ENV_VARS` 中，同时用于设置向导功能 |
| URL 反向映射 | `agent/model_metadata.py` | 实现主机名与提供者名称的自动匹配以实现快速识别 |
| 辅助模型处理 | `agent/auxiliary_client.py` | 使用 `default_aux_model` 进行内容压缩或摘要生成 |
| 运行时解析 | `hermes_cli/runtime_provider.py` | 返回正确的 `base_url`、`api_key` 及 `api_mode` 参数 |
| 传输层处理 | `agent/transports/chat_completions.py` | 通过 `prepare_messages`、`build_extra_body` 和 `build_api_kwargs_extras` 等函数根据配置文件生成相应的参数字典 |

## ProviderProfile 字段说明

完整定义见 `providers/base.py`。其中最常用的字段包括：

| 字段 | 类型 | 用途 |
|---|---|---|
| `name` | str | 标准标识符——与 `config.yaml` 中的 `model.provider` 以及 `--provider` 参数对应 |
| `aliases` | `tuple[str, ...]` | 由 `get_provider_profile()` 解析出的备用名称（例如 `grok` → `xai`） |
| `api_mode` | str | `chat_completions` \| `codex_responses` \| `anthropic_messages` \| `bedrock_converse` |
| `display_name` | str | 在 “Hermes 模型选择器” 中显示的文本标签 |
| `description` | str | 选择器下的说明文字 |
| `signup_url` | str | 首次设置时显示的链接（“在此获取 API 密钥”） |
| `env_vars` | `tuple[str, ...]` | 按优先级排列的 API 密钥相关环境变量；最后的 `*_BASE_URL` 项将用作用户自定义的基础 URL 替代值 |
| `base_url` | str | 默认推理接口地址 |
| `models_url` | str | 显式的模型目录地址（若未指定则回退至 `{base_url}/models`） |
| `auth_type` | str | `api_key` \| `oauth_device_code` \| `oauth_external` \| `copilot` \| `aws_sdk` \| `external_process` |
| `fallback_models` | `tuple[str, ...]` | 当无法从实时目录获取模型时显示的精选列表 |
| `default_headers` | `dict[str, str]` | 每次请求都会发送的头部信息（例如 Copilot 的 `Editor-Version`） |
| `fixed_temperature` | 任意类型 | `None` 表示使用调用方的温度值；`OMIT_TEMPERATURE` 特殊值表示完全不发送温度参数（Kimi 支持） |
| `default_max_tokens` | `int \| None` | 提供商设定的最大 token 数限制（Nvidia 的限制为 16384） |
| `default_aux_model` | str | 用于辅助任务（压缩、图像处理、摘要生成等）的廉价模型 |

## 可覆盖的钩子函数

针对那些具有特殊要求的场景，可继承 `ProviderProfile` 子类：

```python
from typing import Any
from providers.base import ProviderProfile

class AcmeProfile(ProviderProfile):
    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Provider-specific message preprocessing. Runs after codex
        sanitization, before developer-role swap. Default: pass-through."""
        # Example: Qwen normalizes plain-text content to a list-of-parts
        # array and injects cache_control; Kimi rewrites tool-call JSON
        return messages

    def build_extra_body(self, *, session_id=None, **context) -> dict:
        """Provider-specific extra_body fields merged into the API call.
        Context includes: session_id, provider_preferences, model, base_url,
        reasoning_config. Default: empty dict."""
        # Example: OpenRouter's provider-preferences block,
        # Gemini's thinking_config translation.
        return {}

    def build_api_kwargs_extras(self, *, reasoning_config=None, **context):
        """Returns (extra_body_additions, top_level_kwargs). Needed when some
        fields go top-level (Kimi's reasoning_effort, OpenRouter's verbosity for
        adaptive Anthropic models) and some go in extra_body (OpenRouter's
        reasoning dict). Default: ({}, {})."""
        return {}, {}

    def fetch_models(self, *, api_key=None, base_url=None, timeout=8.0) -> list[str] | None:
        """Live catalog fetch. Default hits {models_url or base_url}/models with
        Bearer auth. Override for: custom auth (Anthropic), no REST endpoint
        (Bedrock → None), or public/unauthenticated catalogs (OpenRouter)."""
        return super().fetch_models(api_key=api_key, base_url=base_url, timeout=timeout)

    def create_client(self, **client_kwargs):
        """Supply your own client object instead of the shared openai.OpenAI.
        Default returns None (= use the standard client). Override when the
        wire protocol is not OpenAI-over-HTTP — e.g. an ACP subprocess shim.
        client_kwargs is what the core would have passed to openai.OpenAI
        (api_key, base_url, command, args, timeouts, headers…); accept **kwargs
        and pick what you need. A raise is logged and falls back to the
        standard client."""
        return None
```

## 外部进程（ACP）提供者

通过标准输入/输出驱动的智能体 CLI 并非 HTTP 接口。只需设置 `auth_type="external_process"`，说明如何启动该二进制文件，并通过 `create_client` 提供给客户端即可。无需对核心代码进行任何修改——`hermes -m <name>`、/model 功能、凭证解析、运行时解析以及辅助客户端（压缩、视觉处理等功能）均依赖于 `auth_type` 的设置，而非提供者名称。`plugins/model-providers/copilot-acp/` 中提供了内置示例。

| 字段 | 用途 |
|---|---|
| `process_command` | 默认二进制文件名，例如 `"copilot"` |
| `process_args` | 默认的命令行参数尾部，例如 `("--acp", "--stdio")` |
| `process_command_env_vars` | 用于覆盖二进制文件行为的环境变量，按顺序依次生效 |
| `process_args_env_var` | 用于覆盖命令行参数的环境变量（采用 shlex-split 方式处理） |

`create_client` 返回的客户端会在 `client_kwargs` 中获取 `command` 和 `args` 参数。如果该客户端本身已具备完整性且支持异步操作，可将其类属性设置为 `HERMES_SKIP_TRANSPORT_WRAP = True` / `HERMES_SKIP_ASYNC_WRAP = True`，从而避免辅助客户端通过 HTTP 传输适配器再次处理该请求。

## 钩子参考示例

可参考这些内置插件中的常用实现方式。

| 插件 | 查看理由 |
|---|---|
| `plugins/model-providers/openrouter/` | 支持插件偏好设置及公共模型目录的聚合工具 |
| `plugins/model-providers/gemini/` | `thinking_config` 参数的翻译功能（原生格式与兼容 OpenAI 的嵌套表单） |
| `plugins/model-providers/kimi-coding/` | `OMIT_TEMPERATURE`、`extra_body.thinking` 以及顶层 `reasoning_effort` 参数 |
| `plugins/model-providers/qwen-oauth/` | 消息规范化处理、`cache_control` 参数注入以及超高分辨率图像支持 |
| `plugins/model-providers/nous/` | 附加来源标注标签，以及“禁用时省略推理过程”功能 |
| `plugins/model-providers/custom/` | 解决 Ollama 的 `num_ctx` 参数及 `think: false` 设置带来的特殊问题 |
| `plugins/model-providers/bedrock/` | `api_mode="bedrock_converse"` 设置，以及由于缺乏 REST 接口导致 `fetch_models` 方法返回 None 的情况 |

## 用户自定义配置——无需修改代码库即可替换内置插件

假设您希望将 `gmi` 指向私有的测试环境端点。只需创建 `~/.hermes/plugins/model-providers/gmi/__init__.py` 文件即可：

```python
from providers import register_provider
from providers.base import ProviderProfile

register_provider(ProviderProfile(
    name="gmi",
    aliases=("gmi-cloud", "gmicloud"),
    env_vars=("GMI_API_KEY",),
    base_url="https://gmi-staging.internal.example.com/v1",
    auth_type="api_key",
    default_aux_model="google/gemini-3.1-flash-lite-preview",
))
```

在后续会话中，`get_provider_profile("gmi").base_url` 会返回测试环境地址。无需对代码库进行修补，也无需重新构建。由于用户自定义插件会在内置插件之后被加载，因此用户调用的 `register_provider()` 方法会优先生效。

## api_mode 的选择方式

系统支持四种取值方式，Hermes 会根据以下规则选择其中一种：

1. 用户显式指定（当设置了 `config.yaml` 中的 `model.api_mode` 时）
2. OpenCode 根据模型类型进行的自动分配（Zen 和 Go 模型使用 `opencode_model_api_mode`）
3. URL 自动识别——以 `/anthropic` 结尾则对应 `anthropic_messages`，以 `api.openai.com` 结尾则对应 `codex_responses`，以 `api.x.ai` 结尾同样对应 `codex_responses`，Kimi 域名下的 `/coding` 路径则对应 `chat_completions`
4. 若 URL 识别无果，则退而使用配置文件中的 `api_mode` 设置
5. 默认值为 `chat_completions`

建议将 `profile.api_mode` 设置为对应您所使用的服务提供商默认的值，这可作为参考。不过用户通过 URL 指定的设置仍会优先生效。

## 认证类型

| `auth_type` | 含义 | 使用场景 |
|---|---|---|
| `api_key` | 通过单个环境变量传递静态 API 密钥 | 大多数服务提供商 |
| `oauth_device_code` | 基于设备码的 OAuth 流程 | — |
| `oauth_external` | 用户在其他平台登录，令牌存储在 `auth.json` 中 | Anthropic OAuth、MiniMax OAuth、Qwen Portal、Nous Portal |
| `copilot` | GitHub Copilot 令牌的刷新机制 | 仅适用于 `copilot` 插件 |
| `aws_sdk` | 基于 AWS SDK 的身份凭证体系（IAM 角色、配置文件及环境变量） | 仅适用于 `bedrock` 插件 |
| `external_process` | 由智能体启动的子进程负责处理认证逻辑（详见[外部进程型服务提供商](#external-process-acp-providers)） | `copilot-acp` 插件以及非树形结构的 ACP 插件 |
`auth_type` 用于指定哪些代码路径会将您的提供者视为“简单 API 密钥提供者”——即便该值为其他值而非 `api_key`，PluginManager 仍会记录相关清单，但 Hermes 的 CLI 级自动化功能（如健康检查、`--provider` 参数以及设置向导的委托处理）可能会跳过对该提供者的操作。

## 发现时机

提供者的发现采用**延迟触发**机制——仅在进程中的首次调用 `get_provider_profile()` 或 `list_providers()` 时才会启动。实际上，这一过程会在启动阶段尽早执行（`auth.py` 模块的加载会立即扩展 `PROVIDER_REGISTRY`）。若需确认您的插件已成功加载，请运行以下命令：

```bash
hermes doctor
```

— 成功的 `auth_type="api_key"` 配置文件会显示在“Provider Connectivity”部分，并附带一个 `/models` 探测项。

如需通过程序进行检测：

```python
from providers import list_providers
for p in list_providers():
    print(p.name, p.base_url, p.api_mode)
```

## 测试您的插件

请将 `HERMES_HOME` 指向一个临时目录，以避免污染您的实际配置文件：

```bash
export HERMES_HOME=/tmp/hermes-plugin-test
mkdir -p $HERMES_HOME/plugins/model-providers/my-provider
cat > $HERMES_HOME/plugins/model-providers/my-provider/__init__.py <<'EOF'
from providers import register_provider
from providers.base import ProviderProfile
register_provider(ProviderProfile(
    name="my-provider",
    env_vars=("MY_API_KEY",),
    base_url="https://api.my-provider.example.com/v1",
    auth_type="api_key",
))
EOF

export MY_API_KEY=your-test-key
hermes -z "hello" --provider my-provider -m some-model
```

## 通用 PluginManager 集成方式

通用的 `PluginManager`（即 `hermes plugins` 所操作的组件）**能够识别**模型提供者插件，但并不会直接导入它们——其生命周期由 `providers/__init__.py` 负责管理。该管理器会记录插件的元数据以便后续查看，并根据 `kind: model-provider` 对其进行分类。当用户将未标记的自定义插件放入 `$HERMES_HOME/plugins/` 目录中，且该插件恰好调用了带有 `ProviderProfile` 参数的 `register_provider` 函数时，管理器会通过源代码特征自动将其归类为 `kind: model-provider`——这样一来，即便没有 `plugin.yaml` 文件，插件也能被正确路由。

## 通过 pip 分发

模型提供者可以作为 pip 包进行分发。只需在 `pyproject.toml` 文件的 `hermes_agent.plugins` 组中指定入口点即可：

```toml
[project.entry-points."hermes_agent.plugins"]
acme-inference = "acme_hermes_plugin:register"
```

目标可以是以下两种形式之一：

- 一个**可调用对象**（`module:func`）——无需参数即可被调用；该对象应调用 `register_provider(profile)` 方法；
- 一个**独立模块**（`module`）——因其模块级的 `register_provider(...)` 效果而被导入，这一机制与目录插件中的 `__init__.py` 规范类似。

`providers/__init__.py` 会自行发现这些入口点——通用的 `PluginManager` 永不会为 pip 包触发提供程序注册操作（其入口点路径针对的是由 `plugins.enabled` 控制的、采用 `register(ctx)` 风格的通用插件），因此提供程序注册机制会自行进行扫描。在此过程中需遵循两条规则：

- **必须主动启用。** 此次扫描同样受 `config.yaml` 中定义的 `plugins.enabled` 允许列表（以及 `plugins.disabled` 禁止列表）约束。仅因某个 pip 包已安装，并不会自动触发其导入操作——用户必须将该入口点名称添加到 `plugins.enabled` 中：

  ```yaml
  plugins:
    enabled:
      - acme-inference
  ```

- **优先级最低。** 入口点插件会在文件系统插件之前被检测到：由于`register_provider()`采用“最后写入者胜出”的机制，同名且通过打包方式或` $HERMES_HOME`配置文件引入的插件，总会覆盖通过pip安装的版本。虽然pip包可以添加全新的提供程序，但无法悄无声息地占用原生提供程序的名称。

需要参数的目标（即普通插件中的`register(ctx)`函数）会被提供程序扫描机制跳过——因为它们属于`PluginManager`的管辖范围。出现故障的入口点会被隔离处理：系统仅会以警告级别记录该错误并跳过该入口点，而不会影响其他提供程序的检测。

如需了解完整的入口点配置方法，请参阅[构建Hermes插件](/developer-guide/plugins#distribute-via-pip)。

## 相关页面

- [提供程序运行时](/developer-guide/provider-runtime) —— 解决方案优先级规则以及各层级读取配置文件的位置
- [添加提供程序](/developer-guide/adding-providers) —— 新推理后端的全流程操作指南（涵盖快速插件路径以及完整的CLI/身份验证集成）
- [内存提供程序插件](/developer-guide/memory-provider-plugin)
- [上下文引擎插件](/developer-guide/context-engine-plugin)
- [构建Hermes插件](/developer-guide/plugins) —— 插件开发通用指南
