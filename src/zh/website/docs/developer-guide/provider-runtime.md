---
sidebar_position: 4
title: "Provider Runtime Resolution"
description: "How Hermes resolves providers, credentials, API modes, and auxiliary models at runtime"
---

# 提供商运行时解析机制

Hermes 使用统一的提供商运行时解析器，该解析器被应用于以下场景：

- CLI
- 网关
- 定时任务（Cron jobs）
- ACP
- 辅助模型调用

主要实现文件包括：

- `hermes_cli/runtime_provider.py` — 负责凭据解析及 `_resolve_custom_runtime()` 函数
- `hermes_cli/auth.py` — 管理提供商注册表及 `resolve_provider()` 函数
- `hermes_cli/model_switch.py` — 实现 CLI 和网关共用的 `/model` 切换流程
- `agent/auxiliary_client.py` — 负责辅助模型的路由处理
- `providers/` — 包含 ABC 抽象类及注册表入口函数（如 `ProviderProfile`、`register_provider`、`get_provider_profile`、`list_providers`）
- `plugins/model-providers/<name>/` — 每个提供商对应的插件包，其中会声明 `api_mode`、`base_url`、`env_vars`、`fallback_models` 等参数，并在首次被访问时自动注册到注册表中。用户自定义的插件可存放在 `$HERMES_HOME/plugins/model-providers/<name>/` 目录下，这类插件会优先于同名的内置插件生效。

`providers/` 目录中的 `get_provider_profile()` 函数可根据指定的提供商 ID 返回对应的 `ProviderProfile` 对象。`runtime_provider.py` 在需要解析信息时会调用此函数，从而直接获取标准的 `base_url`、环境变量优先级列表、`api_mode` 以及 `fallback_models` 等配置，无需在多个文件中重复存储这些数据。只需在 `plugins/model-providers/<your-provider>/`（或 `$HERMES_HOME/plugins/model-providers/<your-provider>/`）目录下创建一个调用 `register_provider()` 函数的新插件，`runtime_provider.py` 就会自动识别它——无需在解析器本身中添加分支逻辑。

如果您打算添加一个新的顶级推理提供商，请同时阅读 [添加提供商](./adding-providers.md) 以及 [模型提供商插件指南](./model-provider-plugin.md)。

## 解析优先级

总体而言，提供商的解析顺序如下：

1. 显式的 CLI/运行时请求
2. `config.yaml` 中配置的模型/提供商设置
3. 环境变量
4. 各提供商默认配置或自动解析结果

这种顺序设计非常重要，因为 Hermes 会将已保存的模型/提供商选择视为正常运行时的权威配置来源。这样可以避免过期的 Shell 导出值悄悄覆盖用户上次在 `hermes model` 中选择的接口地址。

## 支持的提供商

目前支持的提供商系列包括（完整的内置插件列表请参见 `plugins/model-providers/`）：

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
- 自定义提供商（`provider: custom`）——适用于任何兼容 OpenAI 的接口的顶级提供商
- 命名自定义提供商（`config.yaml` 中的 `custom_providers` 列表）

## 运行时解析的输出结果

运行时解析器会返回以下类型的数据：

- `provider`：当前使用的提供商名称
- `api_mode`：API 模式
- `base_url`：接口基础地址
- `api_key`：API 密钥
- `source`：配置来源
- 各提供商特有的元数据，如过期时间、刷新信息等

## 为何这一机制如此重要

正是得益于这一解析器，Hermes 才能实现以下组件之间的认证与运行时逻辑共享：

- `hermes chat`
- 网关消息处理模块
- 在新会话中运行的定时任务
- ACP 编辑器会话
- 辅助模型任务

## OpenRouter 与自定义 OpenAI 兼容接口地址的处理机制

当系统中存在多个提供商密钥时（例如 `OPENROUTER_API_KEY` 和 `OPENAI_API_KEY`），Hermes 内置逻辑可避免将错误的 API 密钥传递给目标接口。

每个提供商的 API 密钥仅适用于其对应的专属基础地址：

- `OPENROUTER_API_KEY` 仅用于发送到 `openrouter.ai` 接口
- `OPENAI_API_KEY` 既可用于自定义接口，也可作为备用密钥

此外，Hermes 还能区分以下两种情况：

- 用户手动选择的真实自定义接口
- 未配置自定义接口时使用的 OpenRouter 备用路径

这种区分对于以下场景尤为重要：

- 本地模型服务器
- 非 OpenRouter 类型的 OpenAI 兼容 API
- 无需重新执行设置即可切换提供商的场景
- 即使当前 Shell 环境中未导出 `OPENAI_BASE_URL`，仍需保持正常工作的配置式自定义接口

## Anthropic 原生接口路径

Anthropic 已不再仅通过 OpenRouter 提供服务。

当提供商解析结果为 `anthropic` 时，Hermes 会采用以下机制：

- `api_mode = anthropic_messages`
- 直接使用 Anthropic 的原生 Messages API
- 通过 `agent/anthropic_adapter.py` 处理数据转换

对于原生 Anthropic，当前凭据解析逻辑在同时存在可刷新的 Claude Code 凭据和手动设置的环境变量 Token 时，会优先使用可刷新的 Claude Code 凭据。具体表现为：

- 若 Claude Code 凭据文件中包含可刷新的认证信息，则会被视为首选来源
- 手动设置的 `ANTHROPIC_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN` 值仍可作为显式覆盖值使用
- Hermes 会在调用原生 Messages API 之前先尝试刷新 Anthropic 凭据
- 若调用失败返回 401 错误，Hermes 仍会作为备用方案重新尝试一次

## OpenAI Codex 接口路径

Codex 使用独立的 Responses API 路径：

- `api_mode = codex_responses`
- 提供专用的凭据解析机制及认证存储支持

## 辅助模型的路由机制

以下辅助任务可以使用独立的提供商/模型路由机制，而无需依赖主对话模型：

- 视觉处理任务
- 网页内容提取与摘要生成
- 上下文压缩与摘要生成
- Skills Hub 操作
- MCP 辅助操作
- 内存清除操作

当辅助任务被配置为使用 `main` 提供商时，Hermes 会通过与普通对话相同的统一运行时路径来处理该请求。实际效果包括：

- 基于环境变量配置的自定义接口仍可正常使用
- 通过 `hermes model` 或 `config.yaml` 保存的自定义接口也能正常工作
- 辅助模型路由机制能够区分真实保存的自定义接口与 OpenRouter 备用路径

## 备用模型机制

Hermes 支持配置备用提供商链——即当主模型出现错误时，会按顺序尝试列表中的 `(provider, model)` 组合。为保持向后兼容性，系统仍接受传统的单对 `fallback_model` 字典格式（首次写入时会自动迁移）。

### 内部工作原理

1. **存储**：在 `AIAgent.__init__` 方法中，系统会存储 `fallback_model` 字典，并将 `_fallback_activated` 设置为 `False`。

2. **触发条件**：在 `run_agent.py` 中的主重试循环的三个位置会调用 `_try_activate_fallback()` 函数：
   - 在对无效 API 响应（如无有效选项、内容缺失）进行最大次数重试后
   - 遇到无法通过重试解决的客户端错误时（如 HTTP 401、403、404 错误）
   - 对临时性错误（如 HTTP 429、500、502、503 错误）进行最大次数重试后

3. **激活流程**（`_try_activate_fallback` 函数）：
   - 若已启用备用模式或未配置备用提供商，则立即返回 `False`
   - 调用 `auxiliary_client.py` 中的 `resolve_provider_client()` 函数，生成带有正确认证信息的新的客户端实例
   - 确定对应的 `api_mode`：对于 OpenAI Codex 使用 `codex_responses`，对于 Anthropic 使用 `anthropic_messages`，其余情况使用 `chat_completions`
   - 直接替换当前对象的多个属性：`self.model`、`self.provider`、`self.base_url`、`self.api_mode`、`self.client`、`self._client_kwargs`
   - 对于 Anthropic 备用模式，会生成原生 Anthropic 客户端而非兼容 OpenAI 的客户端
   - 重新评估提示词缓存机制（针对在 OpenRouter 上运行的 Claude 模型）
   - 将 `_fallback_activated` 设置为 `True`，防止再次触发备用模式
   - 将重试计数器重置为 0，继续执行循环

4. **配置加载流程**：
   - CLI 环境：`cli.py` 会读取 `CLI_CONFIG["fallback_model"]` 的值，然后传递给 `AIAgent(fallback_model=...)` 构造函数
   - 网关环境：`gateway/run.py._load_fallback_model()` 会读取 `config.yaml` 中的配置，再传递给 `AIAgent` 构造函数
   - 配置验证：`provider` 和 `model` 两个键都必须非空，否则备用模式将被禁用

### 不支持备用模式的场景

- **子代理委托机制**（`tools/delegate_tool.py`）：子代理会继承父代理的提供商，但不会继承其备用配置
- **辅助任务**：这类任务会使用独立的自动检测机制来选择提供商（详见上文“辅助模型路由机制”）

需要注意的是，定时任务**支持**备用模式：`run_job()` 函数会从 `config.yaml` 中读取 `fallback_providers`（或传统的 `fallback_model`）配置，然后将其传递给 `AIAgent(fallback_model=...)`，其逻辑与网关中的 `_load_fallback_model()` 函数类似。更多细节请参阅 [定时任务内部机制](./cron-internals.md)。

### 测试覆盖情况

备用模式的功能已通过多组测试进行验证：

- `tests/run_agent/test_fallback_credential_isolation.py` —— 验证主提供商与备用提供商之间的凭据隔离效果
- `tests/hermes_cli/test_fallback_cmd.py` —— 测试 `/fallback` CLI 命令的功能
- `tests/gateway/test_fallback_eviction.py` —— 验证网关在检测到故障提供商时的替换机制

## 相关文档

- [Agent 循环内部机制](./agent-loop.md)
- [ACP 内部机制](./acp-internals.md)
- [上下文压缩与提示词缓存机制](./context-compression-and-caching.md)
