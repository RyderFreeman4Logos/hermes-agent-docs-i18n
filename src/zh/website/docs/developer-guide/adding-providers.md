---
sidebar_position: 5
title: "Adding Providers"
description: "How to add a new inference provider to Hermes Agent — auth, runtime resolution, CLI flows, adapters, tests, and docs"
---

# 添加 Provider

通过自定义 Provider 路径，Hermes 已经能够与任何兼容 OpenAI 的接口端点进行通信。除非您希望为该服务提供一流的用户体验，否则无需添加内置 Provider，因为内置 Provider 需要满足以下条件：

- 专属的认证机制或令牌刷新功能
- 精心筛选的模型目录
- 设置相关选项及 `hermes model` 菜单项
- 支持 `provider:model` 语法的别名设置
- 非 OpenAI 格式的 API，且需要适配器转换

如果某个 Provider 仅仅是“另一个兼容 OpenAI 的基础 URL 和 API 密钥”，那么创建一个带名称的自定义 Provider 可能就已足够。

## 内部工作原理

内置 Provider 需要在多个层面保持一致：

1. `hermes_cli/auth.py` 负责确定凭证的获取方式。
2. `hermes_cli/runtime_provider.py` 将这些凭证转换为运行时所需的数据，包括：
   - `provider`
   - `api_mode`
   - `base_url`
   - `api_key`
   - `source`
3. `run_agent.py` 根据 `api_mode` 的设置来决定如何构建和发送请求。
4. `hermes_cli/models.py` 与 `hermes_cli/main.py` 负责在 CLI 中显示该 Provider。（`hermes_cli/setup.py` 会自动调用 `main.py`，无需对此进行修改。）
5. `agent/auxiliary_client.py` 和 `agent/model_metadata.py` 负责处理辅助任务及令牌使用量管理。

其中最重要的抽象概念就是 `api_mode`。

- 大多数提供商使用 `chat_completions` 格式。  
- Codex与Meta Model API（`api.meta.ai` — Muse Spark）则采用 `codex_responses` 格式（会自动设置 `prompt_cache_retention: 24h` 以实现提示词缓存；而 `api.meta.ai` 仅在 `/v1/responses` 接口上就能达到93–99%的缓存命中率）。  
- Ramp Router（`api.router.com`）同样使用 `codex_responses` 格式——其响应数据为路由器自身的原生格式（`/v1/chat/completions` 仅作为最低限度的兼容性过渡接口），并且会针对不同模型验证 `reasoning.effort` 参数，这一功能由路由器配置文件通过指定实时目录中各模型的词汇表来实现（`ProviderProfile.supported_reasoning_efforts`）。  
- Anthropic则使用 `anthropic_messages` 格式。  
- 对于非OpenAI协议的新实现，通常需要额外添加新的适配器以及对应的 `api_mode` 分支。

### 工具调用数据格式

Hermes在内部以OpenAI的chat-completions格式存储对话历史，因此 `chat_completions`传输方式中的 `convert_messages` / `convert_tools` 函数（位于 `agent/transports/chat_completions.py` 文件中）几乎保持一致，而其他传输方式则负责将该格式转换为各自的原生协议。该格式的规范参考标准包括：带有JSON-schema `parameters` 的 `tools` 定义、包含字符串化 `function.arguments` 的助手 `tool_calls` 条目，以及以 `tool_call_id` 为键的、角色标识为 `tool` 的响应消息——相关详细内容可参见[OpenAI chat completions API参考文档](https://platform.openai.com/docs/api-reference/chat/create)。在编写原生适配器时，该页面定义了转换过程中的输入格式要求，而你的提供商文档则负责规定输出格式。

## 首先选择实现路径

### 路径 A — 兼容 OpenAI 的提供者

当该提供者能够处理标准的对话补全类请求时，可使用此路径。

典型工作内容包括：
- 添加身份验证元数据
- 添加模型目录/别名
- 实现运行时解析功能
- 配置 CLI 菜单接口
- 设置辅助模型的默认参数
- 编写测试用例及用户文档

通常无需创建新的适配器或新的 `api_mode`。

### 路径 B — 原生提供者

当该提供者的行为不符合 OpenAI 的对话补全模式时，可使用此路径。

目前支持的示例包括：
- `codex_responses`（OpenAI Codex、xAI Grok、通过 `api.meta.ai` 连接的 Meta Muse Spark——后者会自动设置 `prompt_cache_retention: 24h`——以及通过 `api.router.com` 连接的 Ramp Router）
- `anthropic_messages`

此路径包含路径 A 的所有内容，此外还需：
- 放置在 `agent/` 目录下的提供者适配器
- 用于请求构建、分发、使用情况提取、中断处理及响应规范化的 `run_agent.py` 分支代码
- 适配器测试用例

## 文件清单

### 所有内置提供者都需包含的文件

1. `hermes_cli/auth.py`
2. `hermes_cli/models.py`
3. `hermes_cli/runtime_provider.py`
4. `hermes_cli/main.py`
5. `agent/auxiliary_client.py`
6. `agent/model_metadata.py`
7. 测试文件
8. 位于 `website/docs/` 目录下的用户文档

:::提示
无需修改 `hermes_cli/setup.py` 文件。设置向导会将提供者/模型选择任务委托给 `main.py` 中的 `select_provider_and_model()` 函数——在此处添加的任何提供者都会自动在 `hermes setup` 中可用。
:::

### 原生/非 OpenAI 提供者还需额外准备的文件

10. `agent/<provider>_adapter.py`  
11. `run_agent.py`  
12. 若需要对应提供商的 SDK，则还需 `pyproject.toml`  

## 简化路径：仅使用 API 密钥的提供商  

如果您的提供商只是支持通过单个 API 密钥进行身份验证的 OpenAI 兼容接口，那么您无需修改 `auth.py`、`runtime_provider.py`、`main.py` 以及下文中列出的其他任何文件。  

您只需完成以下操作：  

1. 在 `plugins/model-providers/<your-provider>/` 目录下创建插件目录，其中需包含：  
   - `__init__.py` — 在模块级别调用 `register_provider(profile)`  
   - `plugin.yaml` — 插件配置文件（包含名称、类型：model-provider、版本号及描述信息）  
2. 就这样就可以了。每当有代码调用 `get_provider_profile()` 或 `list_providers()` 时，提供商插件会自动加载——无论是内置插件（即本仓库中的插件），还是位于 `$HERMES_HOME/plugins/model-providers/` 目录下的用户自定义插件，都会被识别并加载。  

当您添加一个插件且该插件调用了 `register_provider()` 后，相关的功能将会自动连接起来。

1. `auth.py` 文件中的 `PROVIDER_REGISTRY` 键（用于凭证解析与环境变量查找）  
2. 将 `api_mode` 设置为 `chat_completions`  
3. `base_url` 值从配置文件或指定的环境变量中获取  
4. 按优先级顺序检查各 `env_vars` 中的 API 密钥  
5. 为该提供程序注册 `fallback_models` 列表  
6. `--provider` 命令行参数用于指定提供程序标识  
7. `hermes model` 菜单中会显示该提供程序  
8. `hermes setup` 向导会自动调用 `main.py` 处理相关操作  
9. `provider:model` 别名语法有效  
10. 运行时解析器可返回正确的 `base_url` 和 `api_key`  
11. `--provider <name>` 命令行参数用于指定提供程序标识  
12. 可通过备用模型机制实现平滑切换至对应提供程序  

位于 `$HERMES_HOME/plugins/model-providers/<name>/` 目录下的用户自定义插件可覆盖同名内置插件（在 `register_provider()` 函数中遵循“后写入者胜出”原则）——因此第三方无需修改源代码即可对任何内置配置进行修改或替换。  

您可以参考 `plugins/model-providers/nvidia/` 或 `plugins/model-providers/gmi/` 目录作为模板，同时查阅完整的[模型提供程序插件指南](/developer-guide/model-provider-plugin)，以获取字段参考、钩子用法及端到端示例。  

## 完整路径：OAuth 与复杂提供程序  

当您的提供程序需要满足以下任一条件时，请使用下方的完整检查清单：

- OAuth 或令牌刷新机制（Nous Portal、Codex、Qwen Portal、Copilot）  
- 非 OpenAI 格式的 API，需额外适配器支持（Anthropic Messages、Codex Responses）  
- 自定义端点检测或多区域探测功能（z.ai、Kimi）  
- 精选静态模型目录或实时加载 `/models` 中的模型  
- 具有定制化认证流程的供应商专用 `hermes model` 菜单项  

## 第一步：选定一个标准供应商 ID  

请选择一个供应商 ID，并在所有相关位置统一使用该 ID。  

代码库中的示例包括：  
- `openai-codex`  
- `kimi-coding`  
- `minimax-cn`  

该 ID 应同时出现在以下文件中：  
- `hermes_cli/auth.py` 中的 `PROVIDER_REGISTRY`  
- 由 `hermes_cli/models.py` 导出的 `hermes_cli/models_catalog_static.py` 中的 `_PROVIDER_LABELS`  
- `hermes_cli/auth.py` 和 `hermes_cli/models_catalog_static.py` 中的 `_PROVIDER_ALIASES`  
- `hermes_cli/main.py` 中的 CLI `--provider` 选项  
- 设置/模型选择相关分支  
- 辅助模型的默认配置  
- 测试文件  

如果这些文件中的 ID 不一致，该供应商的功能将出现异常：虽然认证可能正常工作，但 `/model` 加载、设置流程或运行时识别功能却会 silently 忽略该供应商。  

## 第二步：在 `hermes_cli/auth.py` 中添加认证元数据  

对于基于 API 密钥的供应商，需在 `PROVIDER_REGISTRY` 中添加一个 `ProviderConfig` 条目，其中应包含以下字段：  
- `id`  
- `name`  
- `auth_type="api_key"`  
- `inference_base_url`  
- `api_key_env_vars`  
- 可选的 `base_url_env_var`  

同时还需在 `_PROVIDER_ALIASES` 中添加对应的别名。  

可参考现有供应商的配置作为模板。

- 简单的 API 密钥路径：Z.AI、MiniMax  
- 支持端点检测的 API 密钥路径：Kimi、Z.AI  
- 原生令牌解析方式：Anthropic  
- OAuth/认证存储路径：Nous、OpenAI Codex  

需解答的问题：  
- Hermes 应检查哪些环境变量，以及应按何种优先级检查？  
- 该服务提供方是否需要基础 URL 的覆盖配置？  
- 是否需要进行端点探测或令牌刷新操作？  
- 当缺少凭证时，认证错误信息应如何提示？  

如果服务提供方所需的功能不仅仅是“查找 API 密钥”，则应为其添加专用的凭证解析模块，而非将相关逻辑硬编码到无关的代码分支中。  

## 第 3 步：在 `hermes_cli/models.py` 中添加模型目录及别名  

需更新服务提供方目录，以便其在菜单界面以及 `provider:model` 语法中正常使用。常见的修改内容包括：  
- `_PROVIDER_MODELS`  
- `_PROVIDER_LABELS`  
- `_PROVIDER_ALIASES`  
- `list_available_providers()` 函数中的服务提供方显示顺序  
- 若该服务提供方支持实时获取模型列表，则还需实现 `provider_model_ids()` 函数  

如果服务提供方提供了实时的模型列表，应优先使用该功能，同时将 `_PROVIDER_MODELS` 作为静态备选方案。  

此文件也是实现如下功能的基础：

```text
anthropic:claude-sonnet-4-6
kimi:model-name
```

如果此处缺少别名，提供商虽然能够成功完成身份验证，但在解析 `/model` 部分时仍会失败。

## 第 4 步：在 `hermes_cli/runtime_provider.py` 中处理运行时数据

`resolve_runtime_provider()` 是 CLI、网关、cron、ACP 以及辅助客户端所共用的函数路径。

需添加一个分支，该分支至少要返回一个包含以下内容的字典：

```python
{
    "provider": "your-provider",
    "api_mode": "chat_completions",  # or your native mode
    "base_url": "https://...",
    "api_key": "...",
    "source": "env|portal|auth-store|explicit",
    "requested_provider": requested_provider,
}
```

如果该提供方兼容 OpenAI，`api_mode` 通常应保持为 `chat_completions`。

需特别注意 API 密钥的优先级设置。Hermes 已内置相关逻辑，可防止 OpenRouter 密钥泄露至无关接口。新的提供方也应明确指定哪个密钥对应哪个基础 URL。

## 第 5 步：在 `hermes_cli/main.py` 中集成 CLI 功能

只有当某个提供方出现在交互式的 `hermes model` 流程中时，才能被识别。

请更新 `hermes_cli/main.py` 中的以下内容：

- `provider_labels` 字典
- `select_provider_and_model()` 函数中的 `providers` 列表
- 提供方调度逻辑（如 `if selected_provider == ...`）
- `--provider` 参数的选项
- 若该提供方支持相关功能，则添加登录/注销选项
- 一个 `_model_flow_<provider>()` 函数；若适用，也可复用 `_model_flow_api_key_provider()` 函数

:::提示
无需修改 `hermes_cli/setup.py` —— 该文件会从 `main.py` 调用 `select_provider_and_model()`，因此您的新提供方会自动同时出现在 `hermes model` 和 `hermes setup` 中。
:::

## 第 6 步：确保辅助调用功能正常运行

此处有两个关键文件需要关注：

### `agent/auxiliary_client.py`

如果该提供方是直接基于 API 密钥的类型，可在 `_API_KEY_PROVIDER_AUX_MODELS` 中添加一个成本低、响应快的默认辅助模型。

辅助任务包括以下几类：

- 视觉内容总结
- 网页提取内容总结
- 上下文压缩总结
- 会话搜索总结
- 内存清除操作

如果该提供方没有合适的默认辅助模型，相关辅助任务可能会出现异常表现，或意外使用性能较高的主模型。

### `agent/model_metadata.py`

为提供商的模型设置上下文长度，从而确保令牌预算、压缩阈值及限制值处于合理范围。

## 第7步：若该提供商为原生类型，则需添加适配器及对 `run_agent.py` 的支持

如果该提供商并非普通的对话补全功能，应将针对该提供商的特定逻辑封装在 `agent/<provider>_adapter.py` 文件中。

让 `run_agent.py` 专注于任务协调工作。它应调用适配器提供的辅助函数，而非在整个文件中直接编写用于处理该提供商数据的代码。

对于原生类型的提供商，通常需要在以下方面进行优化：

### 新的适配器文件

典型职责包括：
- 构建 SDK/HTTP 客户端
- 处理令牌相关逻辑
- 将 OpenAI 风格的对话消息转换为该提供商所需的请求格式
- 如有需要，转换工具结构体
- 将提供商返回的结果标准化为 `run_agent.py` 能识别的格式
- 提取使用情况及任务完成原因相关数据

### `run_agent.py`

查找 `api_mode` 相关代码，并逐一检查所有逻辑分支。至少需确认以下几点：
- `__init__` 函数能正确选择新的 `api_mode`
- 客户端构建功能适用于该提供商
- `_build_api_kwargs()` 函数知晓如何格式化请求
- `_interruptible_api_call()` 函数能将请求正确发送至对应客户端
- 中断处理及客户端重建路径正常运作
- 响应验证功能能识别该提供商返回的数据格式
- 任务完成原因的提取准确无误
- 令牌使用情况的提取准确无误
- 备用模型的切换能够平滑过渡到新提供商
- 摘要生成及内存清除相关功能仍可正常运行
同时，在 `run_agent.py` 中搜索 `self.client.`。任何假设存在标准 OpenAI 客户端的代码路径，都可能在原生提供商使用不同的客户端对象或将 `self.client = None` 时出现故障。

### 提示词缓存与提供商特定的请求字段

提示词缓存以及针对不同提供商的配置参数很容易导致功能退化。

示例已包含在代码库中：
- Anthropic 拥有独立的提示词缓存机制
- OpenRouter 能获取与提供商相关的路由信息
- 并非所有提供商都需要支持所有的请求端选项

在添加新的原生提供商时，请务必确认 Hermes 只会发送该提供商能够理解的字段。

## 第 8 步：测试

至少要检查那些负责处理提供商连接的测试用例。

常见测试文件位置：
- `tests/hermes_cli/test_runtime_provider_resolution.py`
- `tests/cli/test_cli_provider_resolution.py`
- `tests/hermes_cli/test_model_switch_custom_providers.py`（以及相关的 `tests/hermes_cli/test_model_switch_*.py` 文件）
- `tests/hermes_cli/test_setup_model_provider.py`
- `tests/run_agent/test_provider_parity.py`
- `tests/run_agent/test_run_agent.py`
- 针对原生提供商的 `tests/test_<provider>_adapter.py` 文件

对于仅包含文档示例的情况，具体的测试文件可能有所不同。关键是要覆盖以下方面：
- 认证处理
- CLI 菜单/提供商选择
- 运行时提供商识别
- 智能体执行流程
- 提供商与模型的解析
- 任何特定于适配器的消息转换

运行相应的测试用例（或使用 `scripts/run_tests.sh`，该脚本会以独立子进程的方式运行每个测试文件）：

```bash
source venv/bin/activate
python -m pytest tests/hermes_cli/test_runtime_provider_resolution.py tests/cli/test_cli_provider_resolution.py tests/hermes_cli/test_setup_model_provider.py tests/run_agent/test_provider_parity.py -q
```

如需进行更深入的修改，请在推送之前先运行完整测试套件：

```bash
source venv/bin/activate
python -m pytest tests/ -n0 -q
```

## 第 9 步：实时验证

完成测试后，运行一次真实的冒烟测试。

```bash
source venv/bin/activate
python -m hermes_cli.main chat -q "Say hello" --provider your-provider --model your-model
```

如果对菜单进行了修改，也请测试相应的交互流程。

```bash
source venv/bin/activate
python -m hermes_cli.main model
python -m hermes_cli.main setup
```

对于原生提供商，除了纯文本响应外，还需验证至少一次工具调用是否正常执行。

## 第10步：更新面向用户的文档

如果该提供商计划作为首选选项推出，还需同步更新用户文档，包括以下文件：
- `website/docs/getting-started/quickstart.md`
- `website/docs/user-guide/configuration.md`
- `website/docs/reference/environment-variables.md`

即便开发者已完美实现了该提供商的集成，仍可能因用户无法找到所需的环境变量或配置流程而导致使用障碍。

## OpenAI兼容型提供商检查清单

适用于标准聊天补全类提供商：
- [ ] 在 `hermes_cli/auth.py` 中添加 `ProviderConfig`
- [ ] 在 `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中添加别名
- [ ] 在 `hermes_cli/models.py` 中添加模型目录信息
- [ ] 在 `hermes_cli/runtime_provider.py` 中添加运行时分支
- [ ] 在 `hermes_cli/main.py` 中完成CLI集成（`setup.py` 会自动继承相关配置）
- [ ] 在 `agent/auxiliary_client.py` 中添加辅助模型
- [ ] 在 `agent/model_metadata.py` 中指定上下文长度限制
- [ ] 更新运行时及CLI测试用例
- [ ] 更新用户文档

## 原生提供商检查清单

适用于需要自定义协议路径的提供商：
- [ ] 完成上述OpenAI兼容型检查清单中的所有要求
- [ ] 在 `agent/<provider>_adapter.py` 中添加适配器代码
- [ ] 在 `run_agent.py` 中支持新的 `api_mode`
- [ ] 确保中断/重建流程能够正常运行
- [ ] 能够正确提取使用情况及任务结束原因
- [ ] 备用路径能够正常生效
- [ ] 添加适配器相关测试用例
- [ ] 确保实时烟雾测试通过

## 常见问题与陷阱

### 1. 仅将提供者添加到认证流程，而未纳入模型解析流程

这样一来，凭据能够正确解析，但 `/model` 及 `provider:model` 这类输入方式则会失效。

### 2. 忘记了 `config["model"]` 既可以是字符串也可以是字典

许多用于选择提供者的代码都需要对这两种形式进行统一处理。

### 3. 误以为必须使用内置提供者

如果相关服务仅兼容 OpenAI，自定义提供者往往能以更低的维护成本解决用户需求。

### 4. 忘记了辅助路径的存在

由于未更新辅助路由配置，主聊天流程可能正常运行，但摘要生成、内存清除或视觉辅助功能则会失效。

### 5. `run_agent.py` 中隐藏的本地提供者相关代码

请搜索 `api_mode` 和 `self.client.`。切勿认为显而易见的请求路径是唯一的路径。

### 6. 将仅适用于 OpenRouter 的配置参数发送给其他提供者

诸如提供者路由之类的字段，仅应存在于支持它们的提供者中。

### 7. 仅更新了 `hermes model`，而未更新 `hermes setup`

这两种流程都需要知晓所使用的提供者信息。

## 开发时的有效搜索关键词

若要查找提供者涉及的所有相关位置，可搜索以下标识符：

- `PROVIDER_REGISTRY`
- `_PROVIDER_ALIASES`
- `_PROVIDER_MODELS`
- `resolve_runtime_provider`
- `_model_flow_`
- `select_provider_and_model`
- `api_mode`
- `_API_KEY_PROVIDER_AUX_MODELS`
- `self.client.`

## 相关文档

- [提供者运行时解析](./provider-runtime.md)
- [架构设计](./architecture.md)
- [贡献指南](./contributing.md)
