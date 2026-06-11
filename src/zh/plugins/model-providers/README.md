# 模型提供者插件

每个子目录都代表一个独立的提供者配置插件。其目录结构与 `plugins/platforms/` 相一致：

```
plugins/model-providers/
├── openrouter/
│   ├── __init__.py      # registers the ProviderProfile
│   └── plugin.yaml      # manifest: name, kind, version, description
├── anthropic/
│   ├── __init__.py
│   └── plugin.yaml
└── ...
```

## 发现机制的工作原理

每当有代码调用 `get_provider_profile()` 或 `list_providers()` 时，`providers/__init__.py._discover_providers()` 函数会首先扫描当前目录以及 `$HERMES_HOME/plugins/model-providers/` 目录。系统会导入每一个 `__init__.py` 文件，并要求其调用 `providers.register_provider(profile)` 函数。

位于 `$HERMES_HOME/plugins/model-providers/<name>/` 目录下的用户自定义插件会覆盖同名称的内置插件，在 `register_provider()` 的调用中遵循“后写入者胜出”的原则。只需将相应文件放入该目录，即可替换内置插件。

## 添加新的提供程序

1. 创建 `plugins/model-providers/<your_provider>/__init__.py` 文件：

   ```python
   from providers import register_provider
   from providers.base import ProviderProfile

   my_provider = ProviderProfile(
       name="your-provider",
       aliases=("alias1", "alias2"),
       display_name="Your Provider",
       description="One-line description shown in the setup picker",
       signup_url="https://your-provider.example.com/keys",
       env_vars=("YOUR_PROVIDER_API_KEY", "YOUR_PROVIDER_BASE_URL"),
       base_url="https://api.your-provider.example.com/v1",
       default_aux_model="your-cheap-model",
   )

   register_provider(my_provider)
   ```

2. 创建 `plugins/model-providers/<your_provider>/plugin.yaml` 文件：

   ```yaml
   name: your-provider-profile
   kind: model-provider
   version: 1.0.0
   description: Short sentence about the provider
   author: Your Name
   ```

无需进行其他任何更改。`auth.py`、`config.py`、`models.py`、`doctor.py`、`model_metadata.py`、`runtime_provider.py`以及chat_completions模块中的所有功能都会自动从注册表中获取配置。

## 复杂的配置文件

如需针对不同提供商的特殊需求，可在子类中重写`ProviderProfile`中的钩子函数——可参考`plugins/model-providers/openrouter/__init__.py`中的`build_extra_body`和`build_api_kwargs_extras`示例，以及`plugins/model-providers/gemini/__init__.py`中的`thinking_config`转换示例。
