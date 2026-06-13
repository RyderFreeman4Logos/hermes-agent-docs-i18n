---
sidebar_position: 5
title: "Adding Providers"
description: "How to add a new inference provider to Hermes Agent — auth, runtime resolution, CLI flows, adapters, tests, and docs"
---

# 添加 Provider

通过自定义 Provider 路径，Hermes 已能够与任何兼容 OpenAI 的接口端点进行通信。除非您希望为该服务提供一流的用户体验，否则无需添加内置 Provider，因为内置 Provider 需要满足以下条件：

- 支持针对特定 Provider 的身份验证或令牌刷新机制
- 提供精选的模型目录
- 包含设置选项及 `hermes model` 菜单项
- 支持 `provider:model` 语法下的别名配置
- 需要适配器的非 OpenAI API 格式

如果该 Provider 仅仅是“另一个兼容 OpenAI 的基础 URL 和 API 密钥”，那么一个命名的自定义 Provider 可能就足够了。

## 工作原理

内置 Provider 需要在多个层面保持一致：

1. `hermes_cli/auth.py` 负责确定凭证的获取方式。
2. `hermes_cli/runtime_provider.py` 将这些信息转换为运行时数据，包括：
   - `provider`
   - `api_mode`
   - `base_url`
   - `api_key`
   - `source`
3. `run_agent.py` 根据 `api_mode` 决定如何构建并发送请求。
4. `hermes_cli/models.py` 和 `hermes_cli/main.py` 负责在 CLI 中显示该 Provider。（`hermes_cli/setup.py` 会自动调用 `main.py`，无需进行任何修改。）
5. `agent/auxiliary_client.py` 和 `agent/model_metadata.py` 负责处理辅助任务及令牌预算管理。

其中最重要的抽象概念就是 `api_mode`：

- 大多数 Provider 使用 `chat_completions` 模式。
- Codex 使用 `codex_responses` 模式。
- Anthropic 使用 `anthropic_messages` 模式。
- 对于新的非 OpenAI 协议，通常需要添加新的适配器以及对应的 `api_mode` 分支。

## 先选择实现路径

### 路径 A — 兼容 OpenAI 的 Provider

当该 Provider 支持标准的聊天完成式请求时，可选择此路径。

典型工作内容包括：

- 添加身份验证相关配置
- 添加模型目录及别名
- 实现运行时解析逻辑
- 配置 CLI 菜单选项
- 设置辅助模型的默认值
- 编写测试用例及用户文档

通常无需创建新的适配器或 `api_mode`。

### 路径 B — 原生 Provider

当该 Provider 的行为与 OpenAI 的聊天完成式请求不同步时，可选择此路径。

当前项目中已有的示例包括：

- `codex_responses`
- `anthropic_messages`

此路径除了包含路径 A 的所有内容外，还需补充：

- 位于 `agent/` 目录下的 Provider 适配器
- `run_agent.py` 中用于请求构建、分发、使用情况提取、中断处理及响应标准化的相关分支
- 适配器测试用例

## 文件清单

### 所有内置 Provider 都需包含的文件

1. `hermes_cli/auth.py`
2. `hermes_cli/models.py`
3. `hermes_cli/runtime_provider.py`
4. `hermes_cli/main.py`
5. `agent/auxiliary_client.py`
6. `agent/model_metadata.py`
7. 测试文件
8. 位于 `website/docs/` 目录下的用户文档

:::提示
`hermes_cli/setup.py` 无需进行任何修改。设置向导会将 Provider/模型选择任务委托给 `main.py` 中的 `select_provider_and_model()` 函数——在此处添加的任何 Provider 都会自动在 `hermes setup` 中可用。
:::

### 原生/非 OpenAI Provider 还需额外包含的文件

10. `agent/<provider>_adapter.py`
11. `run_agent.py`
12. 如果该 Provider 需要 SDK，还需添加 `pyproject.toml` 文件

## 简化路径：简单的 API 密钥型 Provider

如果您的 Provider 仅仅是兼容 OpenAI 的接口端点，并且仅通过单个 API 密钥进行身份验证，那么无需修改 `auth.py`、`runtime_provider.py`、`main.py` 或下面完整清单中的其他任何文件。

您只需完成以下操作：

1. 在 `plugins/model-providers/<your-provider>/` 目录下创建插件目录，其中需包含：
   - `__init__.py` 文件——在模块级别调用 `register_provider(profile)` 函数
   - `plugin.yaml` 文件——用于定义插件信息（名称、类型：model-provider、版本号、描述）
2. 就这样完成了。每当有代码调用 `get_provider_profile()` 或 `list_providers()` 时，这些 Provider 插件会自动加载——无论是项目自带的插件（即当前仓库中的插件），还是用户自定义的插件（位于 `$HERMES_HOME/plugins/model-providers/` 目录下），都会被识别并使用。

当您添加一个插件并且它调用了 `register_provider()` 函数后，以下功能会自动配置完成：

1. 在 `auth.py` 中创建 `PROVIDER_REGISTRY` 条目——用于处理凭证获取及环境变量查询
2. 将 `api_mode` 设置为 `chat_completions`
3. 从配置文件或指定的环境变量中获取 `base_url`
4. 按优先级顺序检查环境变量以获取 API 密钥
5. 为该 Provider 注册 `fallback_models` 列表
6. CLI 中的 `--provider` 参数可接受 Provider 的标识符
7. `hermes model` 菜单中会显示该 Provider
8. `hermes setup` 设置向导会自动调用 `main.py`
9. 支持 `provider:model` 这种别名语法
10. 运行时解析器会返回正确的 `base_url` 和 `api_key`
11. CLI 中的 `--provider <name>` 参数也可接受 Provider 的标识符
12. 可以通过该机制无缝切换到备用的模型

位于 `$HERMES_HOME/plugins/model-providers/<name>/` 目录下的用户自定义插件可以覆盖同名的项目自带插件（在 `register_provider()` 函数中遵循“后写入者胜”的原则）——因此第三方无需修改项目代码，即可对任何内置的 Provider 配置进行修改。

您可以参考 `plugins/model-providers/nvidia/` 或 `plugins/model-providers/gmi/` 目录中的示例，同时查阅完整的[模型 Provider 插件指南](/developer-guide/model-provider-plugin)，以了解相关配置方式、钩子用法及端到端示例。

## 完整路径：需要 OAuth 认证或功能更复杂的 Provider

当您的 Provider 需要满足以下任一条件时，请使用下面的完整清单：

- 需要 OAuth 认证或令牌刷新功能（如 Nous Portal、Codex、Google Gemini、Qwen Portal、Copilot）
- 需要适配器的非 OpenAI API 格式（如 Anthropic Messages、Codex Responses）
- 需要进行自定义端点检测或多区域探测（如 z.ai、Kimi）
- 需要精选的静态模型目录或实时从 `/models` 获取模型列表
- 需要针对该 Provider 的自定义 `hermes model` 菜单项及专属身份验证流程

## 第一步：选择一个标准的 Provider 标识符

请选择一个唯一的 Provider 标识符，并在所有地方统一使用它。

项目中的示例标识符包括：

- `openai-codex`
- `kimi-coding`
- `minimax-cn`

该标识符应同时出现在以下位置：

- `hermes_cli/auth.py` 文件中的 `PROVIDER_REGISTRY` 列表中
- `hermes_cli/models.py` 文件中的 `_PROVIDER_LABELS` 列表中
- `hermes_cli/auth.py` 和 `hermes_cli/models.py` 两个文件中的 `_PROVIDER_ALIASES` 列表中
- `hermes_cli/main.py` 文件中的 CLI `--provider` 参数选项中
- 设置及模型选择相关的分支代码中
- 辅助模型的默认配置中
- 测试用例中

如果这些文件中的标识符不一致，该 Provider 的功能将会出现异常：虽然身份验证可能正常工作，但 `/model`、设置相关功能或运行时解析功能却可能无法识别该 Provider。

## 第二步：在 `hermes_cli/auth.py` 中添加身份验证相关配置

对于基于 API 密钥的 Provider，需在 `PROVIDER_REGISTRY` 中添加一个 `ProviderConfig` 条目，其中应包含以下信息：

- `id`：标识符
- `name`：名称
- `auth_type="api_key"`：身份验证类型
- `inference_base_url`：推理请求的基础 URL
- `api_key_env_vars`：用于存储 API 密钥的环境变量列表
- 可选字段 `base_url_env_var`：用于存储基础 URL 的环境变量

同时还需在 `_PROVIDER_ALIASES` 列表中添加该 Provider 的别名。

您可以参考现有的 Provider 作为模板：

- 简单的 API 密钥型 Provider：Z.AI、MiniMax
- 需要端点检测的 API 密钥型 Provider：Kimi、Z.AI
- 需要原生令牌解析功能的 Provider：Anthropic
- 需要 OAuth 或认证存储服务的 Provider：Nous、OpenAI Codex

在此步骤中需要回答的问题包括：

- Hermes 应该检查哪些环境变量，以及检查的优先级顺序是什么？
- 该 Provider 是否需要基础 URL 的覆盖配置？
- 是否需要进行端点探测或令牌刷新操作？
- 当凭证缺失时，身份验证错误信息应如何显示？

如果该 Provider 的功能不仅仅是“查找 API 密钥”，那么建议创建专门的凭证解析模块，而非将相关逻辑硬编码到其他无关的分支中。

## 第三步：在 `hermes_cli/models.py` 中添加模型目录及别名

需更新 Provider 目录结构，以便该 Provider 能在菜单中显示，同时也能通过 `provider:model` 语法被调用。

常见的修改内容包括：

- `_PROVIDER_MODELS` 列表：存储该 Provider 支持的模型信息
- `_PROVIDER_LABELS` 列表：用于显示该 Provider 的名称标签
- `_PROVIDER_ALIASES` 列表：包含该 Provider 的别名
- `list_available_providers()` 函数中定义该 Provider 在列表中的显示顺序
- 如果该 Provider 支持从 `/models` 实时获取模型列表，则需实现 `provider_model_ids()` 函数

如果该 Provider 提供实时的模型列表，建议优先使用该实时列表，而将 `_PROVIDER_MODELS` 作为静态的备用列表。

正是通过这个文件，类似以下的输入方式才能正常工作：

```text
anthropic:claude-sonnet-4-6
kimi:model-name
```

如果此处缺少别名，提供程序虽能成功完成身份验证，但在解析 `/model` 时仍会失败。

## 第4步：在 `hermes_cli/runtime_provider.py` 中处理运行时数据

`resolve_runtime_provider()` 是 CLI、网关、cron、ACP以及辅助客户端所共用的函数路径。

需添加一个分支，该分支至少返回一个包含以下内容的字典：

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

如果该提供商兼容 OpenAI，那么 `api_mode` 通常应保持为 `chat_completions`。

需注意 API 密钥的优先级设置。Hermes 已内置相关逻辑，可防止 OpenRouter 密钥泄露到无关的接口。新的提供商也应明确指定哪个密钥对应哪个基础 URL。

## 第 5 步：在 `hermes_cli/main.py` 中集成 CLI 功能

只有当某个提供商出现在交互式的 `hermes model` 流程中时，才能被识别。

请更新 `hermes_cli/main.py` 中的以下内容：

- `provider_labels` 字典
- `select_provider_and_model()` 函数中的 `providers` 列表
- 提供商调度逻辑（如 `if selected_provider == ...`）
- `--provider` 参数的选项设置
- 若该提供商支持登录/注销功能，则需添加相应的选项
- 一个 `_model_flow_<provider>()` 函数；若适用，也可复用 `_model_flow_api_key_provider()` 函数

:::提示
无需修改 `hermes_cli/setup.py` —— 它会从 `main.py` 调用 `select_provider_and_model()`，因此您新增的提供商会自动同时出现在 `hermes model` 和 `hermes setup` 流程中。
:::

## 第 6 步：确保辅助功能正常运行

此处有两个关键文件需要关注：

### `agent/auxiliary_client.py`

如果该提供商是直接基于 API 密钥的类型，需在 `_API_KEY_PROVIDER_AUX_MODELS` 中添加一个轻量且快速的默认辅助模型。

辅助任务包括以下几类：

- 视觉内容总结
- 网页内容提取与总结
- 上下文压缩总结
- 会话搜索总结
- 内存清除操作

如果该提供商没有合适的默认辅助模型，相关辅助任务可能会失效，或意外使用性能较高的主模型。

### `agent/model_metadata.py`

需为该提供商的模型添加上下文长度信息，以便合理控制令牌预算、压缩阈值及使用限制。

## 第 7 步：如果是原生提供商，需添加适配器及 `run_agent.py` 支持

如果该提供商并非单纯的对话完成型服务，需将与其相关的逻辑封装在 `agent/<provider>_adapter.py` 文件中。

应让 `run_agent.py` 专注于整体流程编排，它应调用适配器提供的辅助函数，而非在文件中直接编写各种提供商特定的请求格式代码。

对于原生提供商，通常需要在以下方面进行修改：

### 新的适配器文件

典型职责包括：

- 构建 SDK/HTTP 客户端
- 处理令牌相关逻辑
- 将 OpenAI 风格的对话消息转换为该提供商所需的请求格式
- 如有需要，转换工具结构定义
- 将提供商返回的结果标准化为 `run_agent.py` 能识别的格式
- 提取使用情况及任务完成原因等相关数据

### `run_agent.py`

需查找 `api_mode` 相关代码，并逐一检查所有逻辑分支。至少要确认以下几点：

- `__init__` 函数已正确设置新的 `api_mode`
- 客户端构建逻辑能适配该提供商
- `_build_api_kwargs()` 函数能正确格式化请求
- `_interruptible_api_call()` 函数能将请求正确发送到对应的客户端
- 中断处理及客户端重建路径正常工作
- 响应验证逻辑能识别该提供商返回的数据格式
- 任务完成原因的提取逻辑正确
- 令牌使用情况的提取逻辑正确
- 备用模型的切换功能能平滑过渡到新提供商
- 总结生成及内存清除功能仍能正常运行

同时，还需在 `run_agent.py` 中查找所有包含 `self.client.` 的代码路径。任何假设存在标准 OpenAI 客户端的代码路径，都可能在原生提供商使用不同的客户端对象或将 `self.client = None` 时出现故障。

### 提示词缓存及提供商特定的请求字段

提示词缓存功能以及提供商特定的配置参数很容易导致功能异常。

现有示例包括：

- Anthropic 支持原生的提示词缓存功能
- OpenRouter 支持提供商路由相关字段
- 并非所有提供商都需要接收所有的请求端选项

在添加新的原生提供商时，务必确认 Hermes 只会发送该提供商真正能理解的字段。

## 第 8 步：测试

至少要检查那些与提供商集成相关的测试用例。

常见测试文件包括：

- `tests/hermes_cli/test_runtime_provider_resolution.py`
- `tests/cli/test_cli_provider_resolution.py`
- `tests/hermes_cli/test_model_switch_custom_providers.py`（以及相关的 `tests/hermes_cli/test_model_switch_*.py` 文件）
- `tests/hermes_cli/test_setup_model_provider.py`
- `tests/run_agent/test_provider_parity.py`
- `tests/run_agent/test_run_agent.py`
- 对于原生提供商，还需检查 `tests/test_<provider>_adapter.py` 文件

对于仅用于文档说明的示例，具体的测试文件列表可能有所不同。关键是要覆盖以下方面：

- 认证流程的解析
- CLI 菜单及提供商选择功能
- 运行时的提供商识别逻辑
- 智能体执行流程
- 提供商与模型的解析逻辑
- 任何适配器特有的消息转换逻辑

测试时请禁用 xdist 工具：

```bash
source venv/bin/activate
python -m pytest tests/hermes_cli/test_runtime_provider_resolution.py tests/cli/test_cli_provider_resolution.py tests/hermes_cli/test_setup_model_provider.py tests/run_agent/test_provider_parity.py -n0 -q
```

如需进行更深入的修改，请在推送之前先运行完整套件：

```bash
source venv/bin/activate
python -m pytest tests/ -n0 -q
```

## 第9步：实时验证

完成测试后，执行一次真实的冒烟测试。

```bash
source venv/bin/activate
python -m hermes_cli.main chat -q "Say hello" --provider your-provider --model your-model
```

如果您修改了菜单，请同时测试相关的交互流程。

```bash
source venv/bin/activate
python -m hermes_cli.main model
python -m hermes_cli.main setup
```

对于原生提供商，除了检查纯文本响应外，还需确认至少有一个工具调用已被正确执行。

## 第10步：更新面向用户的文档

如果该提供商计划作为首选选项推出，还需同步更新用户文档，包括：
- `website/docs/getting-started/quickstart.md`
- `website/docs/user-guide/configuration.md`
- `website/docs/reference/environment-variables.md`

即便开发者已完美实现了该提供商的集成，若用户无法找到所需的环境变量或设置流程，依然会造成使用障碍。

## OpenAI兼容型提供商检查清单

适用于标准聊天补全功能的提供商：
- [ ] 在 `hermes_cli/auth.py` 中添加了 `ProviderConfig`
- [ ] 在 `hermes_cli/auth.py` 和 `hermes_cli/models.py` 中添加了别名
- [ ] 在 `hermes_cli/models.py` 中添加了模型目录
- [ ] 在 `hermes_cli/runtime_provider.py` 中添加了运行时分支
- [ ] 在 `hermes_cli/main.py` 中完成了CLI集成（`setup.py` 会自动继承相关配置）
- [ ] 在 `agent/auxiliary_client.py` 中添加了辅助模型
- [ ] 在 `agent/model_metadata.py` 中定义了上下文长度限制
- [ ] 已更新运行时及CLI测试用例
- [ ] 已更新用户文档

## 原生提供商检查清单

适用于需要自定义协议路径的提供商：
- [ ] 完成上述OpenAI兼容型检查清单中的所有项
- [ ] 在 `agent/<provider>_adapter.py` 中添加了适配器
- [ ] 在 `run_agent.py` 中支持新的 `api_mode`
- [ ] 中断/重建流程能够正常工作
- [ ] 能够正确提取使用情况及结束原因
- [ ] 备用路径能够正常运行
- [ ] 已添加适配器相关测试用例
- [ ] 实时冒烟测试通过

## 常见问题

### 1. 仅将提供商添加到认证模块，未加入模型解析流程

这会导致凭据能正确解析，但 `/model` 及 `provider:model` 类型的输入却无法正常处理。

### 2. 忘记 `config["model"]` 可能是字符串形式或字典形式

许多提供商选择相关的代码都需要能够处理这两种数据格式。

### 3. 误以为必须使用内置提供商

如果相关服务仅支持OpenAI格式，自定义提供商往往能以更低的维护成本解决用户需求。

### 4. 忘记处理辅助功能路径

虽然主聊天流程可能正常工作，但由于未更新辅助功能路由，摘要生成、内存清除或视觉辅助功能可能会失效。

### 5. `run_agent.py` 中隐藏了原生提供商的相关代码

请搜索 `api_mode` 和 `self.client.` 等关键字，切勿以为只有显而易见的请求路径才是有效路径。

### 6. 向其他不支持OpenRouter的提供商发送相关参数

诸如提供商路由之类的字段仅应出现在支持该功能的提供商中。

### 7. 仅更新了 `hermes model`，未更新 `hermes setup`

这两种流程都需要知晓该提供商的存在。

## 开发过程中的有效搜索关键词

若需查找提供商涉及的所有相关代码位置，可尝试搜索以下标识符：
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

- [提供商运行时解析机制](./provider-runtime.md)
- [系统架构](./architecture.md)
- [贡献指南](./contributing.md)
