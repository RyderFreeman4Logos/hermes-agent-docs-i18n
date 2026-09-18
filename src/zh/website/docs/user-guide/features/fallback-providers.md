---
title: Fallback Providers
description: Configure automatic failover to backup LLM providers when your primary model is unavailable.
sidebar_label: Fallback Providers
sidebar_position: 8
---

# 备用提供商机制

Hermes Agent 具有三层容错机制，可在提供商出现故障时确保会话正常运行：

1. **[凭证池](./credential-pools.md)** — 对*同一*提供商的多个 API 密钥进行轮换使用（优先尝试）
2. **主模型备用机制** — 当主模型发生故障时，自动切换到*不同的*提供商及模型
3. **辅助任务备用机制** — 为视觉处理、压缩等辅助任务提供独立的提供商解决方案

凭证池用于实现同一提供商下的密钥轮换（例如多个 OpenRouter 密钥）。本页面介绍跨提供商的备用机制。这两种机制均为可选配置，且可独立运行。

## 主模型备用机制

当您的主 LLM 提供商出现错误——如速率限制、服务器过载、认证失败或连接中断——Hermes 能在会话进行中自动切换到备用的提供商及模型组合，从而避免丢失对话内容。

### 配置方式

最简便的方法是通过交互式管理界面进行配置：

```bash
hermes fallback
```

`hermes fallback` 功能会复用 `hermes model` 中的提供者选择器——即相同的提供者列表、相同的凭证输入提示以及相同的验证机制。您可以通过 `add`、`list`（别名 `ls`）、`remove`（别名 `rm`）和 `clear` 这些子命令来管理该提供者链。相关设置会存储在 `config.yaml` 文件顶层的 `fallback_providers:` 列表中。

如果您希望直接编辑 YAML 文件，可在 `~/.hermes/config.yaml` 中添加一个顶级的 `fallback_providers` 列表：

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

每条配置项都必须同时包含 `provider` 和 `model` 字段。缺少任一字段的配置项将被忽略。

用于 Gemini 的回退配置项支持 `gemini`、`google`、`google-gemini` 以及 `google-ai-studio` 这些值。在调用 Google 的原生 API 端点时，所有配置都会使用原生的 Gemini 客户端，包括其 `generationConfig.thinkingConfig` 相关设置。而若使用了自定义的兼容 OpenAI 的基础 URL，则依然会采用相应的兼容客户端。

:::注意 `fallback_model` 与 `fallback_providers` 的区别
`fallback_providers`（复数形式，以列表形式呈现）是当前的配置格式，支持按顺序尝试多种回退方案。`fallback_model`（单数形式）则是旧版的单一回退配置键——Hermes 为保持向后兼容仍会识别该键，但 `hermes fallback` 功能在写入配置时会使用新的 `fallback_providers` 键，并在写入时迁移旧版配置。当两者同时被设置时，`fallback_providers` 的优先级更高。
:::

### 支持的提供方

| Provider | Value | Requirements |
|----------|-------|-------------|
| AI Gateway | `ai-gateway` | `AI_GATEWAY_API_KEY` |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` |
| Nous Portal | `nous` | `hermes setup --portal` (fresh) or `hermes auth add nous` (OAuth) |
| OpenAI Codex | `openai-codex` | `hermes model` → **ChatGPT or Codex Subscription** (ChatGPT OAuth) |
| GitHub Copilot | `copilot` | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, or `GITHUB_TOKEN` |
| GitHub Copilot ACP | `copilot-acp` | External process (editor integration) |
| Anthropic | `anthropic` | `ANTHROPIC_API_KEY` or Claude Code credentials |
| z.ai / GLM | `zai` | `GLM_API_KEY` |
| Kimi / Moonshot | `kimi-coding` | `KIMI_API_KEY` |
| MiniMax | `minimax` | `MINIMAX_API_KEY` |
| MiniMax (China) | `minimax-cn` | `MINIMAX_CN_API_KEY` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| NVIDIA NIM | `nvidia` | `NVIDIA_API_KEY` (optional: `NVIDIA_BASE_URL`) |
| GMI Cloud | `gmi` | `GMI_API_KEY` (optional: `GMI_BASE_URL`) |
| Upstage Solar | `upstage` (alias `solar`) | `UPSTAGE_API_KEY` (optional: `UPSTAGE_BASE_URL`) |
| StepFun | `stepfun` | `STEPFUN_API_KEY` (optional: `STEPFUN_BASE_URL`) |
| Ollama Cloud | `ollama-cloud` | `OLLAMA_API_KEY` |
| Google AI Studio | `gemini` | `GOOGLE_API_KEY` (alias: `GEMINI_API_KEY`) |
| xAI (Grok) | `xai` (alias `grok`) | `XAI_API_KEY` (optional: `XAI_BASE_URL`) |
| xAI Grok OAuth (SuperGrok) | `xai-oauth` (alias `grok-oauth`) | `hermes model` → xAI Grok OAuth (browser login; SuperGrok subscription) |
| AWS Bedrock | `bedrock` | Standard boto3 auth (`AWS_REGION` + `AWS_PROFILE` or `AWS_ACCESS_KEY_ID`) |
| Qwen Portal (OAuth) | `qwen-oauth` | `hermes model` (Qwen Portal OAuth; optional: `HERMES_QWEN_BASE_URL`) |
| MiniMax (OAuth) | `minimax-oauth` | `hermes model` (MiniMax portal OAuth) |
| OpenCode Zen | `opencode-zen` | `OPENCODE_ZEN_API_KEY` |
| CommandCode | `commandcode` (alias `commandcode-chat`; Claude via `commandcode-anthropic`) | `COMMANDCODE_API_KEY` |
| OpenCode Go | `opencode-go` | `OPENCODE_GO_API_KEY` |
| OpenCode Free | `opencode-free` | — (keyless, no credential) |
| Kilo Code | `kilocode` | `KILOCODE_API_KEY` |
| Ramp Router | `router` | `RAMP_ROUTER_API_KEY` |
| Xiaomi MiMo | `xiaomi` | `XIAOMI_API_KEY` |
| Arcee AI | `arcee` | `ARCEEAI_API_KEY` |
| GMI Cloud | `gmi` | `GMI_API_KEY` |
| Nebius Token Factory | `nebius-token-factory` | `NEBIUS_API_KEY` |
| Alibaba / DashScope | `alibaba` | `DASHSCOPE_API_KEY` |
| Alibaba Coding Plan | `alibaba-coding-plan` | `ALIBABA_CODING_PLAN_API_KEY` (falls back to `DASHSCOPE_API_KEY`) |
| Kimi / Moonshot (China) | `kimi-coding-cn` | `KIMI_CN_API_KEY` |
| StepFun | `stepfun` | `STEPFUN_API_KEY` |
| Tencent TokenHub | `tencent-tokenhub` | `TOKENHUB_API_KEY` |
| Tencent TokenPlan | `tencent-tokenplan` | `TOKENPLAN_API_KEY` |
| Microsoft Foundry | `azure-foundry` | `AZURE_FOUNDRY_API_KEY` + `AZURE_FOUNDRY_BASE_URL` |
| LM Studio (local) | `lmstudio` | `LM_API_KEY` (or none for local) + `LM_BASE_URL` |
| Hugging Face | `huggingface` | `HF_TOKEN` |
| Custom endpoint | `custom` | `base_url` + `key_env` (see below) |

### 自定义端点回退机制

对于自定义的兼容 OpenAI 的端点，需添加 `base_url` 参数，可选地还可添加 `key_env` 参数：

```yaml
fallback_providers:
  - provider: custom
    model: my-local-model
    base_url: http://localhost:8000/v1
    key_env: MY_LOCAL_KEY            # env var name containing the API key
```

### 何时触发回退机制

当主模型出现以下故障时，回退机制会自动启动：

- **速率限制**（HTTP 429）——在所有重试尝试均失败后
- **服务器错误**（HTTP 500、502、503）——在所有重试尝试均失败后
- **认证失败**（HTTP 401、403）——立即触发（无需再尝试重试）
- **资源未找到**（HTTP 404）——立即触发
- **无效响应**——当 API 持续返回格式错误或空响应时

触发回退机制后，Hermes 会执行以下操作：

1. 获取回退提供方的凭据信息（包括通过 `key_cmd` 定义的自定义提供方）
2. 构建新的 API 客户端，确保在超时或客户端重建过程中仍能使用动态凭据源
3. 直接替换模型、提供方及客户端
4. 重置重试计数器并继续对话

该切换过程极为流畅——用户的对话历史、工具调用记录以及上下文信息都会被完整保留。智能体将从之前的中断点继续工作，只是使用了不同的模型而已。

:::warning 回退机制会重置提示词缓存  
提示词缓存是按照处理请求的模型（在大多数服务提供商处，还会根据账户信息）来区分的。当触发回退机制时，新的服务提供商和模型没有该对话的缓存内容，因此后续请求需要以全价读取全部历史记录，而无法享受约75–90%折扣的缓存读取价格。当当前模型恢复后对话再次开始时，情况也是如此——首次使用恢复后的模型时同样需要重新完整读取历史记录（除非该模型的缓存有效期尚未结束）。这是不可避免的，因为这是确保服务在故障期间仍能正常运行的代价；但这也解释了为何在多个服务提供商之间频繁切换的长时间会话，其成本会明显高于始终使用同一模型的会话。  

:::info 每次对话轮次独立计算，而非整个会话  
回退机制是**按对话轮次**运作的：每条新的用户消息都会以恢复后的主模型作为起始点。如果主模型在当前轮次中发生故障，仅该轮次会触发回退机制。收到下一条消息后，Hermes会再次尝试使用主模型。在单个对话轮次内，回退机制最多只会触发一次；如果回退也失败，系统将进入常规错误处理流程（先尝试重试，再显示错误信息）。这样一来，既能避免在单次对话轮次中出现连续的故障切换，又能让主模型在每个轮次都有机会重新正常工作。

每次轮次的重试功能具备**重置时间感知能力**：当主提供方的身份验证信息显示限制重置时间尚未到来时（例如 Claude Pro/Max 的 5 小时订阅时段，或 Codex 的每周使用限额，这些限制都会以小时或天为单位标注），Hermes 会跳过这次注定失败的重试，继续使用备用提供方，直到限制重置完成——从而避免每轮次出现两次不必要的提供方切换（以及两次提示词缓存失效）。当限制时间到期后，主提供方即可再次尝试重试，但系统并不会自动安排重试或保证一定能恢复服务。对于没有明确重置时间的临时 429 错误，则会采用指数退避机制。

当触发提供方切换并启动退避计时后，系统会在备用状态提示中显示剩余的大致时间，例如：`主提供方约 60 秒后可再次尝试重试；无法保证一定能恢复服务。`而非由速率限制引起的切换，或是从已处于激活状态的跨提供方备用模式切换时，则不会显示新的主提供方退避计时。
:::

### 示例

**将 OpenRouter 作为 Anthropic 原生服务的备用提供方：**
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
| 子代理委托 | ✔（若设置了 `delegation.fallback_providers` 则支持；否则仅未取消绑定的子代理会继承父代理的回退链；值为 `[]` 时则禁用该功能） |
| Cron 任务 | ✔（Cron 代理会继承已配置的回退提供者） |
| `provider: auto` 模式下的辅助任务 | ✔（首先尝试针对单个任务的回退机制，若失败则依次使用主回退链，最后才进行内置辅助任务检测） |

:::提示
主回退链没有对应的环境变量——必须通过 `config.yaml` 或 `hermes fallback` 进行配置。这是有意为之：回退配置属于重要设置，不应被过时的 Shell 导出值所覆盖。
:::

---

## 辅助任务的回退机制

Hermes 为各类辅助任务使用了独立的轻量级模型。每个任务都拥有自己的提供者解析链，该链即作为内置的回退系统。

### 具有独立提供者解析功能的任务

| 任务 | 功能说明 | 配置键 |
|------|----------|--------|
| Vision | 图像分析、浏览器截图处理 | `auxiliary.vision` |
| Compression | 上下文压缩摘要生成 | `auxiliary.compression` |
| Skills Hub | 技能搜索与发现 | `auxiliary.skills_hub` |
| MCP | MCP辅助操作 | `auxiliary.mcp` |
| Approval | 智能命令审批分类 | `auxiliary.approval` |
| Title Generation | 会话标题摘要生成 | `auxiliary.title_generation` |
| Review | `/review`审核子代理（完整代理，而非单次LLM调用） | `auxiliary.review` |
| Triage Specifier | `hermes kanban specify` / 控制面板✨按钮——将简短的分类任务细化为完整的任务规范 | `auxiliary.triage_specifier` |

### 自动检测链

当任务的提供者被设置为默认值“auto”时，Hermes会首先尝试使用该辅助任务的主提供者及主模型。如果该路径不可用或随后出现容量相关错误，Hermes会优先遵循用户配置的回退策略，再启用内置的发现链：

```text
Main provider + main model → auxiliary.<task>.fallback_chain →
fallback_providers / fallback_model → built-in auxiliary discovery chain
```

计费或配额异常仅会隔离出现问题的自定义端点，使其进入辅助健康检查冷却状态，而不会影响所有标记为“custom”的路由。那些基础 URL 不同但运行正常的本地端点仍可参与回退机制以及后续的自动路由处理。同一自定义端点的各个别名会共享其健康状态；而内置提供程序则继续保持其共享账户的健康检查机制。

针对特定任务的链规则最为精确，一旦存在就会优先被采用。顶层的 `fallback_providers` 链与主代理所使用的策略相同，因此仅免费方案或同提供程序的回退规则也适用于处于“auto”模式下的辅助任务。

**内置文本提取链（包括压缩处理、网页内容提取、标题生成等功能）：**

```text
OpenRouter → Nous Portal → Custom endpoint → Codex OAuth →
API-key providers (z.ai, Kimi, MiniMax, Xiaomi MiMo, Hugging Face, Anthropic) → give up
```

**内置视觉检测链：**

```text
Main provider (if vision-capable) → OpenRouter → Nous Portal →
Codex OAuth → Anthropic → Custom endpoint → give up
```

对于那些尚未定义特定任务或主备用策略的用户而言，这些内置的链式处理机制可作为一种便捷的备用方案。

### 配置辅助提供者

每个任务都可以在 `config.yaml` 中进行独立配置：

```yaml
auxiliary:
  vision:
    provider: "auto"              # auto | openrouter | nous | codex | main | anthropic
    model: ""                     # e.g. "openai/gpt-4o"
    base_url: ""                  # direct endpoint (takes precedence over provider)
    api_key: ""                   # API key for base_url

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

而主要的回退链则使用：

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
    # base_url: http://localhost:8000/v1             # Optional custom endpoint
```

辅助功能、压缩处理以及回退机制三者的工作原理完全相同：通过设置 `provider` 来指定负责处理请求的提供方，通过设置 `model` 来选择对应的模型，而 `base_url` 则用于指定自定义端点（该值会覆盖 `provider` 的设置）。

### 辅助任务的提供方选项

这些选项仅适用于 `auxiliary:`、`compression:` 以及 `fallback_providers:` 这些配置项——对于顶层 `model.provider` 而言，`"main"` 并非有效的值。若需使用自定义端点，可在 `model:` 部分中设置 `provider: custom`（详情请参阅[AI 提供方](/integrations/providers)）。

| 提供方 | 描述 | 要求 |
|--------|------|------|
| `"auto"` | 按顺序尝试各个提供方，直到有一个可用为止（默认值） | 需至少配置一个提供方 |
| `"openrouter"` | 强制使用 OpenRouter | 需提供 `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal | 需进行 `hermes auth` 认证 |
| `"codex"` | 强制使用 Codex OAuth | 需配置 `hermes model` 为 ChatGPT 或拥有 Codex 订阅资格 |
| `"main"` | 使用主代理所使用的提供方（仅适用于辅助任务） | 需已配置有效的主提供方 |
| `"anthropic"` | 强制使用 Anthropic 原生服务 | 需提供 `ANTHROPIC_API_KEY` 或 Claude Code 凭证 |

### 直接指定端点

对于任何辅助任务，只要设置 `base_url`，即可完全绕过提供方选择流程，直接将请求发送至该指定端点：

```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`。Hermes 会使用配置好的 `api_key` 进行身份验证，若未设置则默认使用 `OPENAI_API_KEY`。对于自定义接口，它**不会**重复使用 `OPENROUTER_API_KEY`。  

---

## 辅助能力错误时的回退机制

当您明确指定辅助提供者（例如 `auxiliary.vision.provider: glm`）时，Hermes 会将其视为您的首选方案——但如果该提供者因**能力限制错误**（如 HTTP 402 需要支付、HTTP 429 日度配额耗尽、连接失败）而无法处理请求，Hermes 会通过分层的回退机制来处理，而不会默默失败：  

1. **主要辅助提供者**——即您所配置的提供者（始终优先尝试）  
2. **`auxiliary.<task>.fallback_chain`**——如果您自定义了该列表，则按任务顺序依次尝试  
3. **主代理提供者及模型**——最后的保障措施（即使您未设置回退链，也会始终尝试）  
4. **警告并重新抛出错误**——如果所有层级都失败，Hermes 会以 WARNING 级别记录 `Auxiliary <task>: ... 所有回退方式均已用尽`，然后重新抛出原始错误  

短暂的 HTTP 429 速率限制（带有 `Retry-After: ...` 头信息）被视为请求限制而非能力问题——它们会尊重您指定的提供者，**不会**触发回退机制。只有日度/月度配额耗尽、支付错误以及连接失败等情况，才会绕过明确指定的提供者机制。

对于使用 `provider: auto`（未指定辅助提供方）的用户，系统会直接运行现有的自动检测流程来替代第2步和第3步。该流程的第一步即为主代理模型，因此这类用户无需进行任何配置即可获得相同的结果。

### 可选：按任务定制的回退流程

如果您希望采用不同于“先使用主代理模型”的回退顺序，可以手动配置 `fallback_chain`。每个配置项至少需要包含 `provider`；`model`、`base_url` 和 `api_key` 则为可选字段。

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
        timeout: 240            # optional — this candidate's own deadline (seconds)
```

您无需配置 `fallback_chain` 即可实现回退机制——主代理的安全防护机制始终会运行。仅当您明确希望采用不同于默认的顺序时，才使用该配置。

每个 `fallback_chain` 条目还可以自行指定 `timeout` 值（单位：秒）。若未指定，则该回退候选项将继承任务级的超时设置——该设置可能是为主要服务提供商优化的。通过为每个条目指定独立的超时时间，那些处理速度较慢但更可靠的回退方案（例如大上下文摘要工具）就能获得其实际所需的处理时间，而不会因主服务的超时限制而中断工作。

### 触发回退的提供商配额错误

Hermes 将以下错误视为相当于 402 状态码的配额耗尽错误（并非临时性速率限制）：
- Bedrock / LiteLLM：`Too many tokens per day`、`daily limit`、`tokens per day`
- Vertex AI / GCP：`quota exceeded`、`resource exhausted`、`RESOURCE_EXHAUSTED`
- 通用类型：`daily quota`、`quota_exceeded`

如果您的服务提供商对配额耗尽情况使用了其他表述，而 Hermes 仍未触发回退，则属于缺陷——请附上完整的错误信息提交问题报告。

---

## 上下文压缩回退机制

上下文压缩功能通过 `auxiliary.compression` 配置块来决定由哪个模型和服务提供商负责执行摘要生成任务：

```yaml
auxiliary:
  compression:
    provider: "auto"                              # auto | openrouter | nous | main
    model: "google/gemini-3-flash-preview"
```

:::info 旧版本迁移
对于包含 `compression.summary_model` / `compression.summary_provider` / `compression.summary_base_url` 的旧配置，在首次加载时（配置版本为17）会自动迁移到 `auxiliary.compression.*` 格式。

:::

如果找不到可用于压缩的提供者，Hermes 会直接跳过中间对话轮次而不会生成摘要，而非导致会话失败。

---

## 委派提供者覆盖机制

通过 `delegate_task` 生成的子代理会继承父代理的主备提供者链。您仍然可以将这些子代理路由到不同的主提供者/模型组合，以实现成本优化：

```yaml
delegation:
  provider: "openrouter"                      # override provider for all subagents
  model: "google/gemini-3-flash-preview"      # override model
  # base_url: "http://localhost:1234/v1"      # or use a direct endpoint
  # api_key: "local-key"
```

如需了解完整的配置详情，请参阅[子代理委托](/user-guide/features/delegation)。

---

## Cron作业提供者

Cron作业在创建代理时，会继承您所配置的`fallback_providers`链（或旧版的`fallback_model`）。若希望为某个Cron作业使用不同的主提供者，则需在该Cron作业本身上配置`provider`和`model`的覆盖值：

```python
cronjob(
    action="create",
    schedule="every 2h",
    prompt="Check server status",
    provider="openrouter",
    model="google/gemini-3-flash-preview"
)
```

如需完整的配置详情，请参阅[定时任务（Cron）](/user-guide/features/cron)。

| 功能模块 | 回退机制 | 配置位置 |
|---------|-------------------|----------------|
| 主代理模型 | 在 config.yaml 中的 `fallback_providers` —— 出现错误时进行逐轮切换（每轮恢复主模型） | `fallback_providers:`（顶层列表） |
| 辅助任务（任意类型）——自动选择提供方 | 当出现容量不足错误时，会依次执行完整的自动检测流程（先尝试主代理模型，再尝试提供方链） | `auxiliary.<task>.provider: auto` |
| 辅助任务（任意类型）——指定提供方 | 仅在出现容量不足错误时，按 `fallback_chain`（如已设置）的顺序依次尝试 → 主代理模型 → 发出警告并抛出异常 | `auxiliary.<task>.fallback_chain` |
| 视觉处理功能 | 分层处理机制（参见上文）+ 内部 OpenRouter 重试机制 | `auxiliary.vision` |
| 上下文压缩功能 | 分层处理机制（参见上文）；若所有层级均不可用，则降级为不生成摘要 | `auxiliary.compression` |
| 技能中心功能 | 分层处理机制（参见上文） | `auxiliary.skills_hub` |
| MCP 辅助工具 | 分层处理机制（参见上文） | `auxiliary.mcp` |
| 审批分类功能 | 分层处理机制（参见上文） | `auxiliary.approval` |
| 标题生成功能 | 分层处理机制（参见上文） | `auxiliary.title_generation` |
| 任务优先级划分功能 | 分层处理机制（参见上文） | `auxiliary.triage_specifier` |
| 任务委派功能 | 若已声明，则使用 `delegation.fallback_providers`；否则仅未解绑的子任务会继承父任务的配置链 | `delegation.provider` / `delegation.model` / `delegation.fallback_providers` |
| 定时任务功能 | 继承已配置的 `fallback_providers` 配置链；也可为每个任务单独指定提供方 | 每个任务的 `provider` / `model` 设置 |
