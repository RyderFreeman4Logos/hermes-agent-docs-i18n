---
sidebar_position: 10
title: "Model Provider Plugins"
description: "How to build a model provider (inference backend) plugin for Hermes Agent"
---

# 构建模型提供者插件

模型提供者插件用于指定推理后端——可以是兼容 OpenAI 的接口、Anthropic Messages 服务器、Codex 风格的 Responses API，或是 Bedrock 原生界面——Hermes 可通过这些后端来路由 `AIAgent` 调用。所有内置提供者（如 OpenRouter、Anthropic、GMI、DeepSeek、Nvidia 等）均以此类插件的形式提供。第三方开发者只需在 `$HERMES_HOME/plugins/model-providers/` 目录下创建相应文件夹，而无需对代码库进行任何修改，即可添加自己的插件。

:::提示
模型提供者插件属于第三种**提供者插件**。另外两种分别是[内存提供者插件](/developer-guide/memory-provider-plugin)（用于跨会话知识传递）和[上下文引擎插件](/developer-guide/context-engine-plugin)（用于上下文压缩策略）。这三种插件均遵循相同的实现方式：只需创建文件夹、定义配置文件，无需修改代码库。
:::

## 发现机制的工作原理

每当有代码调用 `get_provider_profile()` 或 `list_providers()` 时，`providers/__init__.py._discover_providers()` 函数才会被延迟加载执行。插件发现顺序如下：

1. **内置插件**——位于 `<repo>/plugins/model-providers/<name>/` 目录中，随 Hermes 一起提供
2. **用户自定义插件**——放置于 `$HERMES_HOME/plugins/model-providers/<name>/` 目录下，可放入任意位置；后续会话无需重启即可使用
3. **旧版单文件插件**——位于 `<repo>/providers/<name>.py` 目录中，为非代码库内编辑的安装方式提供兼容支持

由于 `register_provider()` 函数遵循“最后写入者胜出”的原则，用户自定义插件会覆盖同名内置插件。因此，只需在 `$HERMES_HOME/plugins/model-providers/gmi/` 目录下创建新文件夹，即可替换内置的 GMI 配置文件，而无需修改代码库。

## 目录结构

```
plugins/model-providers/my-provider/
├── __init__.py       # Calls register_provider(profile) at module-level
├── plugin.yaml       # kind: model-provider + metadata (optional but recommended)
└── README.md         # Setup instructions (optional)
```

唯一必需的文件是 `__init__.py`。`plugin.yaml` 会被 `hermes plugins` 用于元数据解析，同时也会被通用的 PluginManager 使用，以便将插件路由至对应的加载器；若没有该文件，通用加载器则会退而采用基于源文本的启发式方法进行加载。

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

就这样。放入这两个文件后，无需其他修改即可实现以下**自动关联**：

| 集成功能 | 所在文件 | 获取的内容 |
|---|---|---|
| 凭据解析 | `hermes_cli/auth.py` | 根据配置文件填充 `PROVIDER_REGISTRY["acme-inference"]` |
| `--provider` CLI 参数 | `hermes_cli/main.py` | 支持接受 `acme-inference` |
| Hermes 模型选择器 | `hermes_cli/models.py` | 显示在 `CANONICAL_PROVIDERS` 中，模型列表从 `{base_url}/models` 获取 |
| Hermes health 检查工具 | `hermes_cli/doctor.py` | 对 `ACME_API_KEY` 进行健康检查，并探测 `{base_url}/models` 的可用性 |
| Hermes 设置向导 | `hermes_cli/config.py` | 将 `ACME_API_KEY` 添加到 `OPTIONAL_ENV_VARS` 中，并用于设置向导 |
| URL 反向映射 | `agent/model_metadata.py` | 实现主机名到提供者名称的自动映射以便识别 |
| 辅助模型功能 | `agent/auxiliary_client.py` | 使用 `default_aux_model` 进行压缩/摘要处理 |
| 运行时解析 | `hermes_cli/runtime_provider.py` | 返回正确的 `base_url`、`api_key` 和 `api_mode` 值 |
| 传输层处理 | `agent/transports/chat_completions.py` | 通过 `prepare_messages`、`build_extra_body` 和 `build_api_kwargs_extras` 函数根据配置文件生成相关参数 |

## ProviderProfile 字段

完整定义见 `providers/base.py`，其中最常用的字段如下：

| 字段 | 类型 | 用途 |
|---|---|---|
| `name` | str | 标准标识符——与 `config.yaml` 中的 `model.provider` 及 `--provider` 参数对应 |
| `aliases` | `tuple[str, ...]` | 由 `get_provider_profile()` 解析出的别名（例如 `grok` → `xai`） |
| `api_mode` | str | `chat_completions` \| `codex_responses` \| `anthropic_messages` \| `bedrock_converse` |
| `display_name` | str | 在 Hermes 模型选择器中显示的友好名称 |
| `description` | str | 选择器下的描述文字 |
| `signup_url` | str | 首次运行设置时显示的链接（“在此获取 API 密钥”） |
| `env_vars` | `tuple[str, ...]` | 按优先级排列的 API 密钥相关环境变量；最后的 `*_BASE_URL` 项可作为用户自定义基础 URL 的替代值 |
| `base_url` | str | 默认推理接口地址 |
| `models_url` | str | 显式的模型目录地址（若未指定则回退到 `{base_url}/models`） |
| `auth_type` | str | `api_key` \| `oauth_device_code` \| `oauth_external` \| `copilot` \| `aws_sdk` \| `external_process` |
| `fallback_models` | `tuple[str, ...]` | 当无法从在线目录获取模型时显示的精选列表 |
| `default_headers` | `dict[str, str]` | 每次请求都会发送的头部信息（例如 Copilot 的 `Editor-Version`） |
| `fixed_temperature` | 任意类型 | `None` 表示使用调用方的温度值；`OMIT_TEMPERATURE` 表示完全不发送温度参数（如 Kimi） |
| `default_max_tokens` | `int \| None` | 提供者级别的最大 token 数限制（Nvidia 的默认值为 16384） |
| `default_aux_model` | str | 用于辅助任务（压缩、图像处理、摘要生成等）的廉价模型 |

## 可覆盖的钩子函数

如需处理特殊需求，可对 `ProviderProfile` 进行子类化：

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

    def fetch_models(self, *, api_key=None, timeout=8.0) -> list[str] | None:
        """Live catalog fetch. Default hits {models_url or base_url}/models with
        Bearer auth. Override for: custom auth (Anthropic), no REST endpoint
        (Bedrock → None), or public/unauthenticated catalogs (OpenRouter)."""
        return super().fetch_models(api_key=api_key, timeout=timeout)
```

## Hook 参考示例

以下是些用于处理常用表达的插件示例：

| 插件 | 查看原因 |
|---|---|
| `plugins/model-providers/openrouter/` | 支持配置提供者偏好及公共模型目录的聚合器 |
| `plugins/model-providers/gemini/` | 支持 `thinking_config` 的自定义设置（包含原生格式与兼容 OpenAI 的嵌套表单） |
| `plugins/model-providers/kimi-coding/` | 支持 `OMIT_TEMPERATURE`、`extra_body.thinking` 以及顶层 `reasoning_effort` 参数 |
| `plugins/model-providers/qwen-oauth/` | 负责消息规范化处理、注入 `cache_control` 设置，以及支持超高清输出 |
| `plugins/model-providers/nous/` | 提供归属标签功能，以及“禁用时省略推理过程”的选项 |
| `plugins/model-providers/custom/` | 解决 Ollama 模型中 `num_ctx` 参数及 `think: false` 设置带来的特殊问题 |
| `plugins/model-providers/bedrock/` | 支持 `api_mode="bedrock_converse"`，且由于缺乏 REST 接口，`fetch_models` 方法会返回 None |

## 用户自定义设置——无需修改代码库即可替换内置插件

假设您希望将 `gmi` 指向自己的私有测试环境端点。只需创建文件 `~/.hermes/plugins/model-providers/gmi/__init__.py` 即可：

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

在下一个会话中，`get_provider_profile("gmi").base_url` 会返回测试环境地址。无需修改代码库，也无需重新构建。由于用户插件是在内置插件之后被检测到的，因此用户调用的 `register_provider()` 会优先生效。

## api_mode 选择

系统支持四种值，Hermes会根据以下规则进行选择：

1. 用户显式指定（在 `config.yaml` 中设置 `model.api_mode`）
2. OpenCode 根据模型类型进行的判定（Zen 和 Go 模型使用 `opencode_model_api_mode`）
3. URL 自动检测——以 `/anthropic` 结尾则对应 `anthropic_messages`，以 `api.openai.com` 结尾则对应 `codex_responses`，以 `api.x.ai` 结尾同样对应 `codex_responses`，Kimi 域名中的 `/coding` 路径则对应 `chat_completions`
4. 当 URL 检测无结果时，作为备用方案使用配置文件中的 `api_mode` 设置
5. 默认值为 `chat_completions`

请将 `profile.api_mode` 设置为与您所使用的服务提供商默认值一致，这可作为参考。不过用户通过 URL 指定的设置仍会优先生效。

## 认证类型

| `auth_type` | 含义 | 使用场景 |
|---|---|---|
| `api_key` | 通过单个环境变量传递静态 API 密钥 | 大多数服务提供商 |
| `oauth_device_code` | 设备码 OAuth 流程 | — |
| `oauth_external` | 用户在其他平台登录，令牌存储在 `auth.json` 中 | Anthropic OAuth、MiniMax OAuth、Gemini Cloud Code、Qwen Portal、Nous Portal |
| `copilot` | GitHub Copilot 令牌刷新机制 | 仅适用于 `copilot` 插件 |
| `aws_sdk` | AWS SDK 凭据链（IAM 角色、配置文件及环境变量） | 仅适用于 `bedrock` 插件 |
| `external_process` | 由代理程序启动的子进程负责处理认证 | 仅适用于 `copilot-acp` 插件 |

`auth_type` 决定了哪些代码路径会将您的服务提供商视为“简单 API 密钥提供商”——即便不是 `api_key` 类型，PluginManager 仍会记录其配置信息，但 Hermes 的 CLI 级自动化功能（如检查流程、`--provider` 参数以及设置向导）可能会跳过对该提供商的处理。

## 检测时机

服务提供商的检测是**延迟触发**的——仅在进程中出现首次 `get_provider_profile()` 或 `list_providers()` 调用时才会进行。实际上，这一检测通常在启动阶段较早完成（`auth.py` 模块加载时会立即扩展 `PROVIDER_REGISTRY`）。如果您需要确认自己的插件已成功加载，可以运行相应命令：

```bash
hermes doctor
```

——若认证方式 `auth_type="api_key"` 设置成功，则会在“Provider Connectivity”部分显示相应的配置，并包含一个 `/models` 探测项。

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

## 通用的 PluginManager 集成方式

通用的 `PluginManager`（即 `hermes plugins` 所操作的组件）**能够识别**模型提供者插件，但并不会直接导入它们——其生命周期由 `providers/__init__.py` 负责管理。该管理器会记录插件的元数据以便后续查询，并根据 `kind: model-provider` 对其进行分类。当您将一个未标记的用户插件放入 `$HERMES_HOME/plugins/` 目录中，且该插件恰好调用了带有 `ProviderProfile` 参数的 `register_provider` 函数时，管理器会通过源代码特征自动将其归类为 `kind: model-provider`——这样一来，即便没有 `plugin.yaml` 文件，插件仍能被正确路由。

## 通过 pip 分发

与普通的 Hermes 插件一样，模型提供者也可以以 pip 包的形式分发。只需在您的 `pyproject.toml` 文件中添加一个入口点即可：

```toml
[project.entry-points."hermes_agent.plugins"]
acme-inference = "acme_hermes_plugin:register"
```

……其中 `acme_hermes_plugin:register` 是一个调用 `register_provider(profile)` 的函数。通用的 PluginManager 会在 `discover_and_load()` 阶段加载入口插件。对于类型为 `model-provider` 的 pip 插件，仍需在清单中明确指定该类型（或依赖源文本分析机制）。

如需了解完整的入口点配置方式，请参阅 [构建 Hermes 插件](/guides/build-a-hermes-plugin#distribute-via-pip)。

## 相关页面

- [Provider 运行时](/developer-guide/provider-runtime) —— 解析优先级及各层级读取配置文件的位置
- [添加 Provider](/developer-guide/adding-providers) —— 新推理后端的端到端操作清单（涵盖快速插件路径以及完整的 CLI/身份验证集成）
- [内存 Provider 插件](/developer-guide/memory-provider-plugin)
- [上下文引擎插件](/developer-guide/context-engine-plugin)
- [构建 Hermes 插件](/guides/build-a-hermes-plugin) —— 通用插件开发指南
