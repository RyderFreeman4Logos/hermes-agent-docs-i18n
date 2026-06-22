---
title: Fallback Providers
description: Configure automatic failover to backup LLM providers when your primary model is unavailable.
sidebar_label: Fallback Providers
sidebar_position: 8
---

# 备用提供者机制

Hermes Agent 具有三层容错机制，可在提供者出现故障时确保会话持续运行：

1. **[凭证池](./credential-pools.md)** — 对*同一*提供者使用多个 API 密钥进行轮换（优先尝试）
2. **主模型备用** — 当主模型发生故障时，自动切换到*不同的*提供者与模型组合
3. **辅助任务备用** — 为视觉处理、压缩及网页提取等辅助任务提供独立的提供者解决方案

凭证池用于同一提供者内的密钥轮换（例如多个 OpenRouter 密钥）。本页面介绍跨提供者的备用机制。这两种机制均为可选功能，且可独立运行。

## 主模型备用机制

当您的主大语言模型提供者出现错误——如速率限制、服务器过载、认证失败或连接中断——Hermes 能在会话进行中自动切换到备用的提供者与模型组合，从而避免丢失对话内容。

### 配置方式

最简便的方法是通过交互式管理器进行配置：

```bash
hermes fallback
```

`hermes fallback` 功能会复用 `hermes model` 中的提供者选择器——即相同的提供者列表、相同的凭据输入提示以及相同的验证机制。您可以使用 `add`、`list`（别名 `ls`）、`remove`（别名 `rm`）和 `clear` 这些子命令来管理该提供者链。相关设置会存储在 `config.yaml` 文件顶层的 `fallback_providers:` 列表中。

如果您希望直接编辑 YAML 文件，可在 `~/.hermes/config.yaml` 中添加一个顶级的 `fallback_providers` 列表：

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

每条配置项都必须同时包含 `provider` 和 `model` 字段。缺少任一字段的配置项将被忽略。

:::note `fallback_model` 与 `fallback_providers` 的区别
`fallback_providers`（复数形式，以列表呈现）是当前的配置格式，支持按顺序尝试多个备用选项。而 `fallback_model`（单数形式）则是旧版的单一备用键——Hermes 为保持向后兼容仍会支持该键，但当使用 `hermes fallback` 命令写入配置时，系统会使用新的 `fallback_providers` 键，并在写入时迁移旧版配置。若同时设置了这两个键，则 `fallback_providers` 具有优先级。
:::

### 支持的提供商

| 提供商 | 值 | 需求条件 |
|--------|------|----------|
| OpenRouter | `openrouter` | 需提供 `OPENROUTER_API_KEY` |
| Nous Portal | `nous` | 需先执行 `hermes setup --portal`（全新配置）或通过 `hermes auth add nous` 进行 OAuth 认证 |
| OpenAI Codex | `openai-codex` | 需通过 `hermes model` 命令配置 ChatGPT 的 OAuth 访问权限 |
| GitHub Copilot | `copilot` | 需提供 `COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `GITHUB_TOKEN` |
| GitHub Copilot ACP | `copilot-acp` | 需通过外部进程实现（与编辑器集成） |
| Anthropic | `anthropic` | 需提供 `ANTHROPIC_API_KEY` 或 Claude Code 的认证信息 |
| z.ai / GLM | `zai` | 需提供 `GLM_API_KEY` |
| Kimi / Moonshot | `kimi-coding` | 需提供 `KIMI_API_KEY` |
| MiniMax | `minimax` | 需提供 `MINIMAX_API_KEY` |
| MiniMax（中国版） | `minimax-cn` | 需提供 `MINIMAX_CN_API_KEY` |
| DeepSeek | `deepseek` | 需提供 `DEEPSEEK_API_KEY` |
| NVIDIA NIM | `nvidia` | 需提供 `NVIDIA_API_KEY`（可选：`NVIDIA_BASE_URL`） |
| GMI Cloud | `gmi` | 需提供 `GMI_API_KEY`（可选：`GMI_BASE_URL`） |
| StepFun | `stepfun` | 需提供 `STEPFUN_API_KEY`（可选：`STEPFUN_BASE_URL`） |
| Ollama Cloud | `ollama-cloud` | 需提供 `OLLAMA_API_KEY` |
| Google AI Studio | `gemini` | 需提供 `GOOGLE_API_KEY`（别名：`GEMINI_API_KEY`） |
| xAI (Grok) | `xai`（别名：`grok`） | 需提供 `XAI_API_KEY`（可选：`XAI_BASE_URL`） |
| xAI Grok OAuth（SuperGrok） | `xai-oauth`（别名：`grok-oauth`） | 需通过 `hermes model` 命令配置 xAI Grok OAuth 访问权限（通过浏览器登录，需订阅 SuperGrok 服务） |
| AWS Bedrock | `bedrock` | 需使用标准的 boto3 认证方式（提供 `AWS_REGION`、`AWS_PROFILE` 或 `AWS_ACCESS_KEY_ID`） |
| Qwen Portal（OAuth） | `qwen-oauth` | 需通过 `hermes model` 命令配置 Qwen Portal 的 OAuth 访问权限（可选：提供 `HERMES_QWEN_BASE_URL`） |
| MiniMax（OAuth） | `minimax-oauth` | 需通过 `hermes model` 命令配置 MiniMax 平台的 OAuth 访问权限 |
| OpenCode Zen | `opencode-zen` | 需提供 `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | `opencode-go` | 需提供 `OPENCODE_GO_API_KEY` |
| Kilo Code | `kilocode` | 需提供 `KILOCODE_API_KEY` |
| Xiaomi MiMo | `xiaomi` | 需提供 `XIAOMI_API_KEY` |
| Arcee AI | `arcee` | 需提供 `ARCEEAI_API_KEY` |
| GMI Cloud | `gmi` | 需提供 `GMI_API_KEY` |
| Alibaba / DashScope | `alibaba` | 需提供 `DASHSCOPE_API_KEY` |
| Alibaba Coding Plan | `alibaba-coding-plan` | 需提供 `ALIBABA_CODING_PLAN_API_KEY`（若未提供则自动回退至 `DASHSCOPE_API_KEY`） |
| Kimi / Moonshot（中国版） | `kimi-coding-cn` | 需提供 `KIMI_CN_API_KEY` |
| StepFun | `stepfun` | 需提供 `STEPFUN_API_KEY` |
| Tencent TokenHub | `tencent-tokenhub` | 需提供 `TOKENHUB_API_KEY` |
| Microsoft Foundry | `azure-foundry` | 需提供 `AZURE_FOUNDRY_API_KEY` 及 `AZURE_FOUNDRY_BASE_URL` |
| LM Studio（本地版） | `lmstudio` | 需提供 `LM_API_KEY`（本地运行时可无需该参数）及 `LM_BASE_URL` |
| Hugging Face | `huggingface` | 需提供 `HF_TOKEN` |
| 自定义端点 | `custom` | 需提供 `base_url` 及可选的 `key_env` 参数（详情见下文） |

### 自定义端点回退机制

对于自定义的兼容 OpenAI 的端点，只需添加 `base_url`，如需额外配置则可补充 `key_env` 参数：

```yaml
fallback_providers:
  - provider: custom
    model: my-local-model
    base_url: http://localhost:8000/v1
    key_env: MY_LOCAL_KEY            # env var name containing the API key
```

### 回退机制的触发条件

当主模型出现以下故障时，回退机制会自动启动：

- **速率限制**（HTTP 429）——在所有重试尝试均失败后
- **服务器错误**（HTTP 500、502、503）——在所有重试尝试均失败后
- **认证失败**（HTTP 401、403）——立即触发（无需再尝试重试）
- **资源未找到**（HTTP 404）——立即触发
- **无效响应**——当 API 持续返回格式错误或空响应时

触发回退机制后，Hermes 会执行以下操作：

1. 获取回退提供方的凭证
2. 构建新的 API 客户端
3. 直接替换模型、提供方及客户端
4. 重置重试计数器并继续对话

该切换过程无缝衔接——用户的对话历史、工具调用记录及上下文信息都将得以保留。智能体将从上次停止的位置继续工作，只是使用了不同的模型。

:::info 每轮次触发，而非整个会话
回退机制是**按轮次生效的**：每次新的用户消息发送时，主模型都会恢复使用。如果在当前轮次中主模型再次出现故障，仅该轮次会触发回退。在下一条消息发送时，Hermes 会再次尝试使用主模型。在单次轮次内，回退机制最多触发一次；如果回退也失败，则会进入常规错误处理流程（先尝试重试，再显示错误信息）。这样既能避免在单次轮次中出现连续的故障切换，又能确保主模型在每轮次都有重新工作的机会。
:::

### 示例

**以 OpenRouter 作为 Anthropic 原生模型的回退选项：**
```yaml
model:
  provider: anthropic
  default: claude-sonnet-4-6

fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

**作为 OpenRouter 备用方案的 Nous Portal：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4

fallback_providers:
  - provider: nous
    model: nous-hermes-3
```

**以本地模型作为云端服务的备用方案：**
```yaml
fallback_providers:
  - provider: custom
    model: llama-3.1-70b
    base_url: http://localhost:8000/v1
    key_env: LOCAL_API_KEY
```

**备用方案：Codex OAuth**
```yaml
fallback_providers:
  - provider: openai-codex
    model: gpt-5.3-codex
```

### 回退机制的适用场景

| 使用场景 | 是否支持回退 |
|---------|--------------|
| CLI 会话 | ✔ |
| 消息通道（Telegram、Discord 等） | ✔ |
| 子代理委托 | ✔（子代理会继承父代理的回退链） |
| Cron 任务 | ✔（Cron 代理会继承已配置的回退提供方） |
| `provider: auto` 模式下的辅助任务 | ✔（先尝试针对该任务的独立回退机制，若失败则使用主回退链，之后才会触发内置的辅助任务发现机制） |

:::tip
主回退链没有对应的环境变量——必须通过 `config.yaml` 或 `hermes fallback` 进行配置。这是有意为之：回退配置属于关键设置，不应被过时的 shell 导出值覆盖。
:::

---

## 辅助任务回退机制

Hermes 为各类辅助任务配备了独立的轻量级模型。每个任务都拥有专属的提供方解析链，该链即作为内置的回退系统。

### 具有独立提供方解析能力的任务

| 任务类型 | 功能描述 | 配置键 |
|----------|----------|--------|
| Vision | 图像分析、浏览器截图处理 | `auxiliary.vision` |
| Web Extract | 网页内容摘要生成 | `auxiliary.web_extract` |
| Compression | 上下文压缩摘要生成 | `auxiliary.compression` |
| Skills Hub | 技能搜索与发现 | `auxiliary.skills_hub` |
| MCP | MCP 辅助操作处理 | `auxiliary.mcp` |
| Approval | 智能命令审批分类 | `auxiliary.approval` |
| Title Generation | 会话标题摘要生成 | `auxiliary.title_generation` |
| Triage Specifier | `hermes kanban specify` / 仪表板✨按钮——可将简短的分类任务扩展为完整的任务规范 | `auxiliary.triage_specifier` |

### 自动检测回退链

当任务的提供方被设置为 `"auto"`（默认值）时，Hermes 首先会尝试使用该辅助任务的主提供方及主模型。如果该路径不可用或随后出现资源不足类的错误，Hermes 会优先采用用户配置的回退策略，而非使用内置的发现链：

```text
Main provider + main model → auxiliary.<task>.fallback_chain →
fallback_providers / fallback_model → built-in auxiliary discovery chain
```

当存在任务专用链时，其精度最高且表现最优。顶层的 `fallback_providers` 链与主智能体所使用的策略相同，因此针对 `auto` 模式下的辅助任务，同样适用仅免费资源或同提供商的回退规则。

**内置文本提取链（压缩处理、网页提取、标题生成等功能）：**

```text
OpenRouter → Nous Portal → Custom endpoint → Codex OAuth →
API-key providers (z.ai, Kimi, MiniMax, Xiaomi MiMo, Hugging Face, Anthropic) → give up
```

**内置视觉检测链：**

```text
Main provider (if vision-capable) → OpenRouter → Nous Portal →
Codex OAuth → Anthropic → Custom endpoint → give up
```

对于那些尚未定义特定任务或主备用策略的用户而言，这些内置的链便是一种便捷的备用方案。

### 配置辅助提供者

可以在 `config.yaml` 中为每个任务单独进行配置：

```yaml
auxiliary:
  vision:
    provider: "auto"              # auto | openrouter | nous | codex | main | anthropic
    model: ""                     # e.g. "openai/gpt-4o"
    base_url: ""                  # direct endpoint (takes precedence over provider)
    api_key: ""                   # API key for base_url

  web_extract:
    provider: "auto"
    model: ""

  compression:
    provider: "auto"
    model: ""
    fallback_chain:              # optional, task-specific fallback policy
      - provider: openrouter
        model: inclusionai/ring-2.6-1t:free

  skills_hub:
    provider: "auto"
    model: ""

  mcp:
    provider: "auto"
    model: ""
```

上述所有任务均遵循相同的 **provider / model / base_url** 结构模式。每个任务还可以自行定义 `fallback_chain`；若未指定，则 `provider: auto` 会优先使用顶层的 `fallback_providers` 链，然后再调用 Hermes 内置的辅助发现链。

上下文压缩功能则通过 `auxiliary.compression` 参数进行配置：

```yaml
auxiliary:
  compression:
    provider: main                                    # Same provider options as other auxiliary tasks
    model: google/gemini-3-flash-preview
    base_url: null                                    # Custom OpenAI-compatible endpoint
```

而主回退链所使用的是：

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
    # base_url: http://localhost:8000/v1             # Optional custom endpoint
```

辅助任务、压缩处理以及回退机制的运作方式完全相同：通过设置 `provider` 来指定负责处理请求的服务，通过设置 `model` 来选择对应的模型，而 `base_url` 用于指定自定义端点（该设置会覆盖 `provider` 的配置）。

### 辅助任务的提供者选项

这些选项仅适用于 `auxiliary:`、`compression:` 以及 `fallback_providers:` 这些配置项——对于顶层 `model.provider` 而言，`"main"` 并非有效值。若需使用自定义端点，可在 `model:` 部分中设置 `provider: custom`（详情请参阅[AI 提供者](/integrations/providers)）。

| 提供者 | 描述 | 要求 |
|--------|------|------|
| `"auto"` | 按顺序尝试各提供者，直到有之一能够正常工作（默认值） | 需至少配置一个提供者 |
| `"openrouter"` | 强制使用 OpenRouter | 需提供 `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | 需进行 `hermes auth` 认证 |
| `"codex"` | 强制使用 Codex OAuth | 需将模型配置为 `hermes model` → Codex |
| `"main"` | 使用主代理所使用的提供者（仅适用于辅助任务） | 需已配置有效的主提供者 |
| `"anthropic"` | 强制使用 Anthropic 原生服务 | 需提供 `ANTHROPIC_API_KEY` 或 Claude Code 凭证 |

### 直接指定端点

对于任何辅助任务，只要设置 `base_url`，即可完全绕过提供者筛选机制，直接将请求发送至该指定端点：

```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`。Hermes 会使用配置好的 `api_key` 进行身份验证，若未设置该键则会回退到 `OPENAI_API_KEY`。对于自定义接口，它**不会**重复使用 `OPENROUTER_API_KEY`。

---

## 辅助能力错误时的回退机制

当您明确指定辅助提供者（例如 `auxiliary.vision.provider: glm`）时，Hermes 会将其视为您的优先选择——但如果该提供者因**能力限制错误**（如 HTTP 402 需要支付、HTTP 429 每日额度耗尽、连接失败）而确实无法处理请求，Hermes 会通过分层回退机制来处理，而不会静默失败：

1. **主要辅助提供者**——即您所配置的提供者（始终优先尝试）
2. **`auxiliary.<task>.fallback_chain`**——如果您自定义了该列表，则按此顺序尝试
3. **主代理提供者及模型**——最后的安全保障措施（即使您未设置回退链，也会始终尝试）
4. **发出警告并重新抛出错误**——如果所有层级都失败，Hermes 会以 WARNING 级别记录日志 `Auxiliary <task>: ... 所有回退方式均已用尽`，然后重新抛出原始错误

短暂的 HTTP 429 速率限制（带有 `Retry-After: ...` 头信息）被视为请求约束而非能力问题——它们会尊重您指定的提供者，**不会**触发回退机制。只有每日/每月额度耗尽、支付错误以及连接失败等情况才会绕过指定提供者的限制。

对于使用 `provider: auto`（未指定辅助提供者）的用户，系统会自动运行现有的自动检测流程来替代第 2–3 步。该流程的第一步即为主代理模型，因此这类用户无需任何配置即可获得相同的结果。

### 可选：按任务定制的回退链

如果您希望采用不同于“先尝试主代理模型”的回退顺序，可以明确配置 `fallback_chain`。每个条目至少需要指定 `provider`；`model`、`base_url` 和 `api_key` 则为可选字段。

```yaml
auxiliary:
  vision:
    provider: glm
    model: glm-4v-flash
    fallback_chain:
      - provider: openrouter
        model: google/gemini-3-flash-preview
      - provider: nous
        model: anthropic/claude-sonnet-4

  compression:
    provider: openrouter
    fallback_chain:
      - provider: openai
        model: gpt-4o-mini
```

您无需配置 `fallback_chain` 即可实现回退机制——主代理的安全防护机制依然会正常运行。仅当您明确希望采用不同于默认的顺序时，才使用该配置。

### 会触发回退的提供商配额错误

Hermes 将以下错误视为与 402 信用耗尽具有同等严重程度的状况（不属于临时性速率限制）：

- Bedrock / LiteLLM：`Too many tokens per day`、`daily limit`、`tokens per day`
- Vertex AI / GCP：`quota exceeded`、`resource exhausted`、`RESOURCE_EXHAUSTED`
- 通用类型：`daily quota`、`quota_exceeded`

如果您的提供商对配额耗尽情况使用了不同的错误描述，而 Hermes 仍未触发回退机制，则属于缺陷——请附上完整的错误信息提交问题报告。

---

## 上下文压缩回退机制

上下文压缩功能通过 `auxiliary.compression` 配置块来指定由哪个模型及提供商负责执行摘要生成：

```yaml
auxiliary:
  compression:
    provider: "auto"                              # auto | openrouter | nous | main
    model: "google/gemini-3-flash-preview"
```

:::info 旧版本迁移
对于包含 `compression.summary_model` / `compression.summary_provider` / `compression.summary_base_url` 参数的旧配置，在首次加载时（配置版本为17）会自动迁移为 `auxiliary.compression.*` 格式。

:::

如果无法找到用于压缩的提供者，Hermes 会直接跳过中间对话轮次而不会生成摘要，从而避免会话失败。

---

## 委派提供者覆盖机制

通过 `delegate_task` 生成的子代理会继承父代理的主备提供者链。您仍然可以将这些子代理路由到不同的主提供者与模型组合，以实现成本优化：

```yaml
delegation:
  provider: "openrouter"                      # override provider for all subagents
  model: "google/gemini-3-flash-preview"      # override model
  # base_url: "http://localhost:1234/v1"      # or use a direct endpoint
  # api_key: "local-key"
```

如需完整的配置详情，请参阅[子代理委托](/user-guide/features/delegation)。

---

## Cron作业提供者

当Cron作业创建代理时，它会继承您已配置的`fallback_providers`链（或旧的`fallback_model`）。若希望为某个Cron作业使用不同的主提供者，则需在该Cron作业本身上配置`provider`和`model`的覆盖值：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

如需了解完整的配置详情，请参阅[定时任务（Cron）](/user-guide/features/cron)。
