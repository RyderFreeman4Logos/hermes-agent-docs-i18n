---
sidebar_position: 4
title: "Provider Runtime Resolution"
description: "How Hermes resolves providers, credentials, API modes, and auxiliary models at runtime"
---

# 提供商运行时解析机制

Hermes 使用统一的提供商运行时解析器，该解析器被应用于以下组件中：

- CLI
- gateway
- 定时任务（cron jobs）
- ACP
- 辅助模型调用

主要实现文件包括：

- `hermes_cli/runtime_provider.py` — 用于处理凭证解析以及自定义端点的运行时解析
- `hermes_cli/auth.py` — 负责管理提供商注册表，并提供 `resolve_provider()` 函数
- `hermes_cli/model_switch.py` — 实现通用的 `/model` 切换流程（适用于 CLI 和 gateway）
- `agent/auxiliary_client.py` — 负责辅助模型的路由功能
- `providers/` — 包含抽象基类（ABC）以及注册表相关接口（如 `ProviderProfile`、`register_provider`、`get_provider_profile`、`list_providers`）
- `plugins/model-providers/<name>/` — 每个提供商对应的插件目录，这些插件会声明 `api_mode`、`base_url`、`env_vars`、`fallback_models` 等参数，并在首次被调用时自动注册到注册表中。位于 `$HERMES_HOME/plugins/model-providers/<name>/` 的用户自定义插件可覆盖同名内置插件。

`providers/` 目录中的 `get_provider_profile()` 函数会根据指定的提供商 ID 返回对应的 `ProviderProfile` 对象。`runtime_provider.py` 在进行解析时会调用此函数，从而直接获取标准的 `base_url`、`env_vars` 优先级列表、`api_mode` 以及 `fallback_models` 等信息，无需在多个文件中重复存储这些数据。只需在 `plugins/model-providers/<your-provider>/`（或 `$HERMES_HOME/plugins/model-providers/<your-provider>/`）目录下创建一个调用 `register_provider()` 函数的新插件，`runtime_provider.py` 就会自动识别它——无需在解析器本身中添加额外分支逻辑。

如果您打算添加新的顶级推理提供方，请同时阅读[添加提供方](./adding-providers.md)以及本页面附带的[模型提供方插件指南](./model-provider-plugin.md)。

## 聊天补全推理结构

兼容 OpenAI 的中继节点可以将 `reasoning` 或 `reasoning_content` 以字符串、文本片段字典，或文本片段与字符串碎片的列表形式返回。Hermes 会在主流处理、中继记录、同步及异步辅助流处理，以及补全响应推理提取之前，先对这些字段进行扁平化处理。各个片段会保留其原有的空白字符；标准化处理不会在字段内部添加分隔符。主流处理与中继记录会保留完整的粗体推理标题之间的现有段落分隔。推理内容会与最终显示的答案分开呈现。

## 解决方案优先级

从宏观层面来看，提供方选择遵循以下顺序：

1. 显式的 CLI/运行时请求
2. `config.yaml` 中的模型/提供方配置
3. 环境变量
4. 各提供方特定的默认值或自动识别机制

这种顺序十分重要，因为 Hermes 会将已保存的模型/提供方选择视为正常运行时的权威依据。这样可以避免过时的 shell 导出设置悄悄覆盖用户在 `hermes model` 命令中最后选择的端点。

## 提供方

目前支持的提供方系列包括（完整列表请参见 `plugins/model-providers/`）：

- AI Gateway（Vercel）  
- OpenRouter  
- Nous Portal  
- OpenAI Codex  
- Copilot / Copilot ACP  
- Anthropic（原生支持）  
- Google / Gemini（`gemini`）  
- Alibaba / DashScope（`alibaba`、`alibaba-coding-plan`）  
- DeepSeek  
- Z.AI  
- Kimi / Moonshot（`kimi-coding`、`kimi-coding-cn`）  
- MiniMax（`minimax`、`minimax-cn`、`minimax-oauth`）  
- Kilo Code  
- Hugging Face  
- OpenCode Zen / OpenCode Go  
- AWS Bedrock  
- Azure Foundry  
- NVIDIA NIM  
- xAI（Grok）  
- Arcee  
- GMI Cloud  
- StepFun  
- Qwen OAuth  
- Xiaomi  
- Ollama Cloud  
- LM Studio  
- Tencent TokenHub  
- 自定义提供商（`provider: custom`）——适用于所有兼容 OpenAI 的端点的顶级提供商  
- 命名自定义提供商（在 `config.yaml` 中使用 `providers:` 字典定义；为保持向后兼容性，仍会读取旧版的 `custom_providers` 列表）  

## 运行时解析结果  

运行时解析器会返回以下数据：  

- `provider`  
- `api_mode`  
- `base_url`  
- `api_key`  
- `source`  
- 与特定提供商相关的元数据，如有效期/刷新信息等  

## 为何这一点很重要  

正是得益于该解析器，Hermes 才能在以下场景之间实现身份验证和运行时逻辑的共享：  

- `hermes chat`  
- 网关消息处理功能  
- 在新会话中运行的定时任务  
- ACP 编辑器会话  
- 辅助模型任务  

## AI Gateway  

在 `~/.hermes/.env` 文件中设置 `AI_GATEWAY_API_KEY`，然后使用 `--provider ai-gateway` 参数启动 Hermes。Hermes 会从该网关的 `/models` 端点获取可用模型，并筛选出支持工具调用的语言模型。  

## OpenRouter、AI Gateway 以及自定义的兼容 OpenAI 的基础地址

Hermes 内置了相关逻辑，旨在当存在多个提供商密钥（例如 `OPENROUTER_API_KEY`、`AI_GATEWAY_API_KEY` 和 `OPENAI_API_KEY`）时，防止错误的 API 密钥被传递给自定义端点。

每个提供商的 API 密钥都仅作用于其对应的基准 URL：

- `OPENROUTER_API_KEY` 仅会发送到 `openrouter.ai` 的端点
- `AI_GATEWAY_API_KEY` 仅会发送到 `ai-gateway.vercel.sh` 的端点
- `OPENAI_API_KEY` 既可用于自定义端点，也可作为备用方案

此外，Hermes 还能区分以下两种情况：

- 用户手动选择的实际自定义端点
- 未配置自定义端点时使用的 OpenRouter 备用路径

这种区分对于以下场景尤为重要：

- 本地模型服务器
- 非 OpenRouter/非 AI Gateway 但兼容 OpenAI 的 API
- 无需重新执行设置即可切换提供商
- 即使当前 shell 中未导出 `OPENAI_BASE_URL`，仍需保持正常运行的已保存自定义端点

## 原生 Anthropic 路径

Anthropic 已不再仅通过 OpenRouter 访问。

当提供商解析选中 `anthropic` 时，Hermes 会使用：

- `api_mode = anthropic_messages`
- 原生的 Anthropic Messages API
- `agent/anthropic_adapter.py` 用于内容转换

在同时存在可刷新的 Claude Code 凭证和复制的环境变量令牌时，Hermes 现在会更优先使用可刷新的 Claude Code 凭证而非环境变量令牌来获取原生 Anthropic 的访问权限。实际应用中的意义在于：

- 当 Claude Code 的凭证文件包含可刷新的认证信息时，系统会优先使用这些凭证作为授权来源；
- 手动设置的 `ANTHROPIC_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` 值仍可作为显式覆盖值有效；
- Hermes 会在调用原生 Messages API 之前先尝试刷新 Anthropic 的凭证；
- 作为备用方案，若在重新构建 Anthropic 客户端后仍出现 401 错误，Hermes 仍会尝试重试一次。

## OpenAI Codex 路径

Codex 使用独立的 Responses API 路径：

- `api_mode = codex_responses`
- 提供专门的凭证解析与认证存储支持。

## 辅助模型路由

以下辅助任务可使用独立的提供者/模型路由机制，而无需依赖主对话模型：

- 视觉处理
- 网页内容提取与总结
- 上下文压缩总结
- Skills Hub 操作
- MCP 辅助工具操作
- 内存清除操作

当某项辅助任务被配置为使用 `main` 提供者时，Hermes 会通过与常规聊天相同的共享运行时路径来处理该任务。实际应用中这意味着：

- 基于环境变量配置的自定义端点依然可用；
- 通过 `hermes model` / `config.yaml` 保存的自定义端点也同样有效；
- 辅助路由机制能够区分真正保存的自定义端点与 OpenRouter 的备用端点。

## 备用模型

Hermes 支持配置自定义的备用提供者链——即当主模型出现故障时，系统会按顺序尝试列表中的各组 `(提供者, 模型)` 配置。为保持向后兼容性，旧的单一键值对形式的 `fallback_model` 字典仍被支持（并在首次写入时自动迁移）。

### 内部工作原理

1. **存储机制**：`AIAgent.__init__`方法会存储`fallback_model`字典，并将 `_fallback_activated`设置为`False`。

2. **触发条件**：在每个轮次处理过程中，有三个位置会调用`_try_activate_fallback()`函数（该函数实际上调用了`agent/chat_completion_helpers.py`中的`try_activate_fallback()`）——它们分别位于`agent/turn_api_error.py`、`agent/turn_response_check.py`和`agent/turn_recovery.py`文件中：
   - 在对无效的API响应进行最大次数的重试后（例如返回`None`或缺少必要内容）；
   - 遇到无法重试的客户端错误时（如HTTP 401、403、404状态码）；
   - 对临时性错误进行最大次数的重试后（如HTTP 429、500、502、503状态码）。

3. **激活流程**（`_try_activate_fallback`函数）：
   - 若该备用模型已处于激活状态或未被配置，则立即返回`False`；
   - 调用`auxiliary_client.py`中的`resolve_provider_client()`函数，以构建具有正确认证信息的新客户端；
   - 确定`api_mode`模式：对于openai-codex模型使用`codex_responses`模式，对于anthropic模型使用`anthropic_messages`模式，其余模型则使用`chat_completions`模式；
   - 直接替换相关属性值：`self.model`、`self.provider`、`self.base_url`、`self.api_mode`、`self.client`以及`self._client_kwargs`；
   - 对于anthropic平台的备用模型，会专门构建兼容Anthropic平台的客户端而非OpenAI格式的客户端；
   - 重新评估提示词缓存机制（在OpenRouter上运行Claude模型时该功能处于启用状态）；
   - 将 `_fallback_activated`设置为`True`，从而防止再次触发备用模式；
   - 将重试次数重置为0，然后继续执行后续循环。

4. **配置方式**：
   - 通过命令行界面：通过`hermes_cli/fallback_config.get_fallback_chain()`函数读取备用模型链配置，随后将其传递给`AIAgent(fallback_model=...)`构造函数。
- **网关层**：`gateway/run_config_loaders.py._load_fallback_model()` 会读取 `config.yaml` 中的配置，然后将其传递给 `AIAgent`。
- **验证机制**：`provider` 和 `model` 两个键都必须非空，否则将禁用回退功能。

### 不支持回退功能的场景

- **子代理委托**（`tools/delegate_tool.py`）：子代理会继承父代理的 provider，但不会继承回退配置。
- **辅助任务**：这类任务会使用自己独立的 provider 自动检测机制（详情请参见上文关于辅助模型路由的内容）。

**定时任务**则支持回退功能：`run_job()` 会从 `config.yaml` 中读取 `fallback_providers`（或旧版的 `fallback_model`）配置，并将其传递给 `AIAgent(fallback_model=...)`，其处理方式与网关层的 `_load_fallback_model()` 函数类似。详情请参阅 [定时任务内部机制](./cron-internals.md)。

### 测试覆盖情况

回退功能已在多个测试套件中得到验证：

- `tests/run_agent/test_fallback_credential_isolation.py` —— 验证主代理与回退代理之间的凭证隔离机制。
- `tests/hermes_cli/test_fallback_cmd.py` —— 测试 `/fallback` 这一 CLI 命令的功能。
- `tests/gateway/test fallback_eviction.py` —— 验证网关层如何移除失效的 provider。

## 相关文档

- [代理循环内部机制](./agent-loop.md)
- [ACP 内部机制](./acp-internals.md)
- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
