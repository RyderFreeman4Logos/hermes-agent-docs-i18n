# providers/

此处记录了Hermes所识别的所有推理提供者的注册表信息及ABC定义。

每个提供者仅需以`ProviderProfile`的形式声明一次。之后的各个处理环节——身份验证解析、传输参数配置、模型列表展示以及运行时路由——都将从这些配置文件中获取数据，而无需各自维护独立的数据结构。

---

## 结构布局

```
providers/
├── base.py         ProviderProfile dataclass + OMIT_TEMPERATURE sentinel
├── __init__.py     Registry: register_provider(), get_provider_profile(), list_providers()
└── README.md       This file
```

这些**配置文件本身**作为插件存在于 `plugins/model-providers/<name>/`（该仓库中自带）以及 `$HERMES_HOME/plugins/model-providers/<name>/`（用户自定义覆盖版本）路径下。当有任何消费者首次调用 `get_provider_profile()` 或 `list_providers()` 时，`providers/__init__.py` 中的注册表会以延迟加载的方式自动发现这些插件。有关插件接口规范及示例，请参阅 `plugins/model-providers/README.md`。

---

## 工作集成方式

注册表会在首次访问时被填充数据。此后，所有下游模块都会从中读取信息：

- `hermes_cli/auth.py` 会将其发现的每一个 API 密钥配置文件添加到 `PROVIDER_REGISTRY` 中（但会跳过 `copilot`、`kimi-coding`、`kimi-coding-cn`、`zai`、`openrouter`、`custom` 这几类需要特殊令牌解析方式的配置）。
- `hermes_cli/models.py` 会扩展 `CANONICAL_PROVIDERS` 列表，并在 `provider_model_ids()` 函数中调用 `profile.fetch_models()` 方法。
- `hermes_cli/doctor.py` 会为每个 `auth_type="api_key"` 类型的配置文件添加一个 `/models` 健康检查接口。
- `hermes_cli/config.py` 会将所有的环境变量注入到 `OPTIONAL_ENV_VARS` 中，以便设置向导能够识别这些变量。
- 当 URL 检测无法确定相关配置时，`hermes_cli/runtime_provider.py` 会以 `profile.api_mode` 作为备用值。
- `agent/model_metadata.py` 通过调用 `profile.get_hostname()` 方法实现主机名与提供服务的提供商之间的映射。
- `agent/auxiliary_client.py` 会优先读取 `profile.default_aux_model` 的配置，只有在无法找到该配置时才会回退到旧版的硬编码字典。
- `agent/transports/chat_completions.py::_build_kwargs_from_profile()` 方法会在每次调用时依次执行 `profile.prepare_messages()`、`profile.build_extra_body()` 以及 `profile.build_api_kwargs_extras()` 这三个函数。
- `run_agent.py` 会传递 `provider_profile=<ProviderProfile>` 参数，这样传输层就会使用配置文件路径而非旧版的标志位路径。

---

## 添加新的提供服务

请参考 `plugins/model-providers/README.md` —— 可以在该目录下新建一个文件夹（如需创建私有插件，则可放在 `$HERMES_HOME/plugins/model-providers/` 目录下）。

---

## 可在 `ProviderProfile` 上覆盖的钩子函数

| 钩子函数 | 功能说明 |
|----------|----------|
| `get_hostname()` | 基于 URL 的检测功能 —— 默认值会从 `base_url` 中获取。 |
| `prepare_messages(msgs)` | 提供服务特定的消息预处理功能（例如 Qwen 会将消息转换为分块列表，并添加 `cache_control` 头信息）。 |
| `build_extra_body(**ctx)` | 用于生成提供服务特有的 `extra_body` 内容（如 OpenRouter 提供服务的偏好设置，Gemini 的 `thinking_config` 配置等）。 |
| `build_api_kwargs_extras(**ctx)` | 用于返回 `(extra_body_additions, top_level_kwargs)` 两组数据 —— Kimi 会将 `reasoning_effort` 参数置于顶层，而 Qwen 则会将 `enable_thinking`/`thinking_budget` 参数分开设置。 |
| `fetch_models(*, api_key)` | 用于从实时目录中获取模型列表 —— 默认情况下会通过Bearer认证访问 `{models_url or base_url}/models` 路径。对于不支持 REST 接口的提供服务（如 Bedrock）、基于 OAuth 的目录服务（如 Anthropic），或是公共目录服务（如 OpenRouter），则需要自行实现该函数的覆盖版本。 |

---

## 配置字段说明

完整的配置字段定义可见于 `providers/base.py` 文件中的数据类描述。
