# providers/

记录了Hermes所识别的所有推理提供者的注册表及ABC信息。

每个提供者都会以`ProviderProfile`的形式被定义一次。之后的其他处理环节——身份验证解析、传输参数配置、模型列表展示以及运行时路由——都将从这些配置文件中读取数据，而无需维护独立的对应数据结构。

---

## 结构布局

```
providers/
├── base.py         ProviderProfile dataclass + OMIT_TEMPERATURE sentinel
├── __init__.py     Registry: register_provider(), get_provider_profile(), list_providers()
└── README.md       This file
```

**配置文件本身**作为插件存储在 `plugins/model-providers/<名称>/`（包含于该仓库中）以及 `$HERMES_HOME/plugins/model-providers/<名称>/`（用户自定义覆盖版本）路径下。当有客户端首次调用 `get_provider_profile()` 或 `list_providers()` 方法时，`providers/__init__.py` 中的注册表会以延迟加载的方式自动发现这些配置文件。有关插件接口规范及示例，请参阅 `plugins/model-providers/README.md`。

---

## 其集成方式

注册表会在首次访问时被初始化。之后，所有下游层都会从该注册表中读取数据。

- `hermes_cli/auth.py` 会将检测到的每个 API 密钥配置文件添加到 `PROVIDER_REGISTRY` 中（但会跳过 `copilot`、`kimi-coding`、`kimi-coding-cn`、`zai`、`openrouter` 和 `custom` —— 这些类型需要特定的令牌解析机制）。
- `hermes_cli/models.py` 会扩展 `CANONICAL_PROVIDERS`，并在 `provider_model_ids()` 方法中调用 `profile.fetch_models()`。
- `hermes_cli/doctor.py` 会为每个 `auth_type="api_key"` 的配置文件添加一个 `/models` 健康检查接口。
- `hermes_cli/config.py` 会将所有的环境变量注入到 `OPTIONAL_ENV_VARS` 中，以便设置向导能够识别这些变量。
- 当 URL 识别无法确定时，`hermes_cli/runtime_provider.py` 会以 `profile.api_mode` 作为默认值。
- `agent/model_metadata.py` 通过调用 `profile.get_hostname()` 实现主机名与提供服务的供应商之间的映射。
- `agent/auxiliary_client.py` 会首先尝试读取 `profile.default_aux_model` 的配置，只有在无法找到时才会回退到旧版的硬编码字典。
- `agent/transports/chat_completions.py::_build_kwargs_from_profile()` 方法会在每次调用时依次执行 `profile.prepare_messages()`、`profile.build_extra_body()` 和 `profile.build_api_kwargs_extras()` 这些函数。
- `run_agent.py` 会传递 `provider_profile=<ProviderProfile>` 参数，这样传输层就会使用配置文件路径，而非旧版的标志位路径。

---

## 添加新的提供服务供应商

请参考 `plugins/model-providers/README.md` —— 可以在该目录下创建新文件夹（如果是私有插件，则可创建在 `$HERMES_HOME/plugins/model-providers/` 目录下）。

---

## 可以在 `ProviderProfile` 上覆盖的钩子函数

| Hook | 功能说明 |
|------|---------|
| `get_hostname()` | 基于 URL 的检测功能——默认值从 `base_url` 中获取。 |
| `prepare_messages(msgs)` | 针对不同提供方的消息预处理操作（Qwen 会将消息转换为分块列表，并添加 `cache_control` 参数）。 |
| `build_extra_body(**ctx)` | 为不同提供方生成特定的 `extra_body` 内容（OpenRouter 提供方需设置偏好参数，Gemini 则需要 `thinking_config`）。 |
| `build_api_kwargs_extras(**ctx)` | 用于生成 `(extra_body_additions, top_level_kwargs)` 参数对——Kimi 会将 `reasoning_effort` 参数置于顶层，而 Qwen 则会将 `enable_thinking`/`thinking_budget` 参数分开设置。 |
| `supported_reasoning_efforts(model)` | 为不同模型指定允许的推理强度等级，供那些在未知等级参数时会返回 400 错误的网关使用（Ramp Router 会从实时目录中读取该信息）。`None` 表示使用传输层的默认值，`()` 表示该模型不接受任何推理相关参数，元组形式则表示需要对参数值进行限制。该函数仅可在缓存阶段调用，即位于请求处理的主流程中。 |
| `fetch_models(*, api_key)` | 用于获取实时模型列表——默认会通过Bearer认证访问 `{models_url or base_url}/models` 目录。对于非 REST 协议的提供方（如 Bedrock）、基于 OAuth 的目录（如 Anthropic）或公共目录（如 OpenRouter），需自行实现该函数的替代版本。 |

---

## 配置字段

完整说明请参见 `providers/base.py` 文件中的数据类定义。
