---
title: "LLM and Model Providers"
sidebar_label: "AI Providers"
sidebar_position: 1
---

# 大语言模型与模型提供者

本页面介绍了如何为 Hermes Agent 配置推理提供者——涵盖从 OpenRouter、Anthropic 等云 API，到 Ollama、vLLM 等自托管端点，以及高级路由与回退配置等多种方案。要使用 Hermes，至少需要配置一个提供者。

## 推理提供者

您至少需要一种方式来连接大语言模型。可以通过 `hermes model` 命令交互式地切换提供者和模型，也可直接进行配置：

| Provider | Setup |
|----------|-------|
| **Nous Portal** | `hermes model` (OAuth, subscription-based) |
| **OpenAI Codex** | `hermes model` → **ChatGPT or Codex Subscription** (ChatGPT OAuth, uses Codex models) |
| **GitHub Copilot** | `hermes model` (OAuth device code flow, `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, or `gh auth token`) |
| **GitHub Copilot ACP** | `hermes model` (spawns local `copilot --acp --stdio`) |
| **Anthropic** | `hermes model` (Claude Max + extra usage credits via OAuth; also supports Anthropic API key or manual setup-token — see note below) |
| **OpenRouter** | `OPENROUTER_API_KEY` in `~/.hermes/.env` |
| **Ramp Router** | `RAMP_ROUTER_API_KEY` in `~/.hermes/.env` (provider: `router`; aliases: `ramp-router`, `ramp`, `router.com`; Responses-native gateway, live account-scoped catalog) |
| **Fireworks AI** | `FIREWORKS_API_KEY` in `~/.hermes/.env` (provider: `fireworks`; aliases: `fireworks-ai`, `fw`) |
| **NovitaAI** | `NOVITA_API_KEY` in `~/.hermes/.env` (provider: `novita`, 200+ models, Model API, Agent Sandbox, GPU Cloud) |
| **AI Gateway** | `AI_GATEWAY_API_KEY` in `~/.hermes/.env` (provider: `ai-gateway`) |
| **z.ai / GLM** | `GLM_API_KEY` in `~/.hermes/.env` (provider: `zai`) |
| **Kimi / Moonshot** | `KIMI_API_KEY` in `~/.hermes/.env` (provider: `kimi-coding`) |
| **Kimi / Moonshot (China)** | `KIMI_CN_API_KEY` in `~/.hermes/.env` (provider: `kimi-coding-cn`; aliases: `kimi-cn`, `moonshot-cn`) |
| **Arcee AI** | `ARCEEAI_API_KEY` in `~/.hermes/.env` (provider: `arcee`; aliases: `arcee-ai`, `arceeai`) |
| **GMI Cloud** | `GMI_API_KEY` in `~/.hermes/.env` (provider: `gmi`; aliases: `gmi-cloud`, `gmicloud`) |
| **Nebius Token Factory** | `NEBIUS_API_KEY` in `~/.hermes/.env` (provider: `nebius-token-factory`; aliases: `nebius`, `nebius-tf`, `tokenfactory`) |
| **Actual Computer** | `ACTUAL_API_KEY` in `~/.hermes/.env` for the hosted relay, or `ACTUAL_BASE_URL=http://127.0.0.1:8080` for the local daemon — no key needed on loopback (provider: `actual`; aliases: `actual-computer`, `actualcomputer`, `aci`) |
| **MiniMax** | `MINIMAX_API_KEY` in `~/.hermes/.env` (provider: `minimax`) |
| **MiniMax China** | `MINIMAX_CN_API_KEY` in `~/.hermes/.env` (provider: `minimax-cn`) |
| **xAI (Grok) — Responses API** | `XAI_API_KEY` in `~/.hermes/.env` (provider: `xai`) |
| **xAI Grok OAuth (SuperGrok)** | `hermes model` → "xAI Grok OAuth (SuperGrok / Premium+)" — browser login, no API key. See [guide](../guides/xai-grok-oauth.md) |
| **Qwen Cloud (Alibaba DashScope)** | `DASHSCOPE_API_KEY` in `~/.hermes/.env` (provider: `alibaba`; mainland-China endpoint: `alibaba-cn`) |
| **Alibaba Cloud (Coding Plan)** | `ALIBABA_CODING_PLAN_API_KEY` (falls back to `DASHSCOPE_API_KEY`) (provider: `alibaba-coding-plan`, alias: `alibaba_coding`; mainland-China endpoint: `alibaba-coding-plan-cn` with `ALIBABA_CODING_PLAN_CN_API_KEY`, falling back to the shared keys) — separate billing SKU, different endpoint |
| **Alibaba Cloud (Token Plan)** | `ALIBABA_TOKEN_PLAN_API_KEY` in `~/.hermes/.env` (provider: `alibaba-token-plan`; mainland-China endpoint: `alibaba-token-plan-cn` with `ALIBABA_TOKEN_PLAN_CN_API_KEY`, falling back to the shared key) — Model Studio flat-token tier |
| **Kilo Code** | `KILOCODE_API_KEY` in `~/.hermes/.env` (provider: `kilocode`) |
| **Xiaomi MiMo** | `XIAOMI_API_KEY` in `~/.hermes/.env` (provider: `xiaomi`, aliases: `mimo`, `xiaomi-mimo`) |
| **Tencent TokenHub** | `TOKENHUB_API_KEY` in `~/.hermes/.env` (provider: `tencent-tokenhub`, aliases: `tencent`, `tokenhub`, `tencentmaas`) |
| **Tencent TokenPlan** | `TOKENPLAN_API_KEY` in `~/.hermes/.env` (provider: `tencent-tokenplan`, aliases: `tokenplan`, `tencent-lkeap`; Anthropic Messages endpoint) |
| **OpenCode Zen** | `OPENCODE_ZEN_API_KEY` in `~/.hermes/.env` (provider: `opencode-zen`) |
| **CommandCode** | `COMMANDCODE_API_KEY` in `~/.hermes/.env` (provider: `commandcode`, alias: `commandcode-chat`; Claude models via `commandcode-anthropic`, alias: `commandcode-claude`). Works with GOAT/Pro/Max/Provider plans (not the $1 Go plan — no API access). |
| **OpenCode Go** | `OPENCODE_GO_API_KEY` in `~/.hermes/.env` (provider: `opencode-go`) |
| **OpenCode Free** | Keyless — no API key or account needed (provider: `opencode-free`, aliases: `free`, `opencode_free`). Select via `hermes model` or `/model free`; requests are sent anonymously. The model list refreshes automatically from OpenCode's live catalog, so rotating free promotions appear (and delisted ones disappear) without a Hermes update |
| **DeepSeek** | `DEEPSEEK_API_KEY` in `~/.hermes/.env` (provider: `deepseek`) |
| **Hugging Face** | `HF_TOKEN` in `~/.hermes/.env` (provider: `huggingface`, aliases: `hf`) |
| **Google / Gemini** | `GOOGLE_API_KEY` (or `GEMINI_API_KEY`) in `~/.hermes/.env` (provider: `gemini`) |
| **Google Vertex AI** | `hermes model` → "Google Vertex AI" (provider: `vertex`; OAuth2 via service-account JSON or ADC, GCP billing) |
| **OpenAI API (direct)** | `OPENAI_API_KEY` in `~/.hermes/.env` (provider: `openai-api`, optional `OPENAI_BASE_URL`) |
| **Azure AI Foundry** | `hermes model` → "Azure AI Foundry" (provider: `azure-foundry`; uses Azure OpenAI / Foundry endpoint and key) |
| **AWS Bedrock** | `hermes model` → "AWS Bedrock" (provider: `bedrock`; standard AWS credentials chain via boto3) |
| **NVIDIA Build** | `NVIDIA_API_KEY` in `~/.hermes/.env` (provider: `nvidia`; NIM-hosted models on build.nvidia.com) |
| **Ollama Cloud** | `hermes model` → "Ollama Cloud" (provider: `ollama-cloud`; cloud-hosted Ollama API) |
| **Qwen OAuth** | `hermes model` → "Qwen OAuth" (provider: `qwen-oauth`; browser PKCE login) |
| **MiniMax OAuth** | `hermes model` → "MiniMax (OAuth)" (provider: `minimax-oauth`; browser PKCE login) |
| **StepFun** | `STEPFUN_API_KEY` in `~/.hermes/.env` (provider: `stepfun`) |
| **LM Studio** | `hermes model` → "LM Studio" (provider: `lmstudio`, optional `LM_API_KEY`) |
| **Custom Endpoint** | `hermes model` → choose "Custom endpoint" (saved in `config.yaml`) |

所有三种 OpenCode 提供商都会在每次请求中（包括主轮次的所有传输操作以及压缩、标题生成等辅助调用）添加一个不可见的、针对单次对话的 `x-opencode-session` 标头。OpenCode 利用该标头将特定对话绑定到某个后端，从而保持提示词缓存的热度；该标头的值源自 Hermes 会话 ID，不包含任何个人数据。

关于官方 API 密钥的相关信息，请参阅专门的 [Google Gemini 指南](/guides/google-gemini)。

:::提示 模型键别名
在 `model:` 配置部分，您可以使用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 的效果是完全相同的。
:::

### Nous Portal

[Nous Portal](https://portal.nousresearch.com) 是 Nous Research 提供的统一订阅门户，也是**运行 Hermes Agent 的推荐方式**。通过一次 OAuth 登录，您即可使用 300 多种前沿智能体模型（如 Claude、GPT、Gemini、DeepSeek、Qwen、Kimi、GLM、MiniMax、Grok 等），同时还能使用 [工具网关](/user-guide/features/tool-gateway)（网页搜索、图像生成、文本转语音、浏览器自动化功能）。相关费用将计入您的 Nous 订阅账单，而无需为每个提供商单独开户。

```bash
hermes setup --portal     # fresh install — OAuth + provider + gateway in one command
hermes model              # existing install — pick "Nous Portal" from the list
hermes portal info        # inspect login + routing at any time
```

尚未拥有订阅账号？请访问 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription) 进行申请。

**详细信息请参阅：** 专门的 [Nous Portal集成页面](/integrations/nous-portal)（涵盖订阅内容、模型目录及故障排除指南），以及分步指导的 [使用Nous Portal运行Hermes Agent指南](/guides/run-hermes-with-nous-portal)。

**客户端标识。** Hermes Agent发送至Portal的每个请求都会自动携带`client=hermes-client-v<版本号>`标签（例如`client=hermes-client-v0.13.0`），该版本号与您安装的版本保持一致。此标签会出现在所有Portal交互路径中——包括主聊天循环、辅助调用、压缩摘要生成以及网页提取功能——从而帮助Portal端的监控系统区分Hermes Agent的请求与其他客户端。无需任何配置，当您执行`hermes update`命令时，该标签会自动更新。

**JWT认证（自动处理）。** Hermes Agent优先使用带有限定范围的`inference:invoke`类型JWT进行Portal请求，若传统的不透明会话密钥方式不可用，则会自动回退至该方式。无需额外配置——凭证由OAuth流程统一管理，并会自动定期更换。已被撤销的刷新令牌会被隔离处理，以避免出现重放攻击。

:::info Codex说明
OpenAI Codex提供商通过设备码进行身份验证（需打开指定网址并输入代码）。Hermes Agent会将生成的凭证存储在`~/.hermes/auth.json`目录下的专属认证存储中；如果存在`~/.codex/auth.json`文件，它还可以导入该文件中的现有Codex CLI凭证。使用此功能无需安装Codex CLI。

如果令牌刷新因终端错误（如 HTTP 4xx 错误、`invalid_grant`、授权已被撤销等）而失败，Hermes 会将该刷新令牌标记为无效，并停止重复使用它，从而避免出现大量相同的认证失败提示。此时，后续请求将会显示需要重新输入凭据的提示信息。您可以通过运行 `hermes auth add openai-codex`（或通过“hermes model” → **ChatGPT 或 Codex 订阅**）来启动新的设备码登录流程；一旦下次登录成功，该令牌的隔离状态就会解除。

在某些情况下，设备登录也可能会因为 `[SSL: UNEXPECTED_EOF_WHILE_READING]` 错误，或是 Python/OpenSSL 3.5+ 版本中中间节点拒绝使用 X25519MLKEM768 等后量子加密群组而导致的 TLS 握手超时问题而失败（不过此时使用 curl 可能仍能正常工作）。Hermes 并不会更改默认的 TLS 策略。您可以在运行 `hermes model` 命令之前，将 `OPENSSL_CONF` 指向一个将可用加密群组限制为传统曲线的配置文件，或者尝试使用 TLS 1.2 协议进行诊断。

```ini
openssl_conf = openssl_init

[openssl_init]
ssl_conf = ssl_sect

[ssl_sect]
system_default = system_default_sect

[system_default_sect]
Groups = x25519:secp256r1:secp384r1:x448
```
:::

:::warning
即便使用 Nous Portal、Codex 或自定义端点，某些工具（如视觉处理、网页摘要生成、MoA 模型）仍会调用独立的“辅助”模型。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 会将这些任务路由至您的**主聊天模型**——即您在 `hermes model` 中选择的那个模型。您也可以为每个任务单独设置路由，将其指向成本更低或响应更快的模型（例如 OpenRouter 上的 Gemini Flash）——详情请参阅[辅助模型](/user-guide/configuration#auxiliary-models)。
:::

:::tip Nous 工具网关
已订阅付费版 Nous Portal 的用户还可以使用**[工具网关](/user-guide/features/tool-gateway)**——该功能可让您通过订阅服务直接进行网页搜索、图像生成、文本转语音以及浏览器自动化操作，无需额外 API 密钥。在全新安装时，执行 `hermes setup --portal` 即可通过一条命令完成登录、设置 Nous 作为服务提供商并启用该网关。现有用户则可以通过 `hermes model` 或针对特定工具使用 `hermes tools` 来启用该功能。随时可使用 `hermes portal info` 查看任务路由情况。
:::

### 用于模型管理的两个命令

Hermes 提供了**两个**用于管理模型的命令，它们各自承担不同的功能：

| 命令 | 执行位置 | 功能说明 |
|---------|----------|----------|
| **`hermes model`** | 终端（在任何会话之外） | 完整的设置向导——用于添加服务提供商、执行 OAuth 认证、输入 API 密钥以及配置端点 |
| **`/model`** | Hermes 聊天会话内部 | 快速在**已配置好的**服务提供商和模型之间切换 |
如果您打算切换到尚未配置的提供商（例如，目前仅配置了 OpenRouter，而希望使用 Anthropic），则应使用 `hermes model` 命令，而非 `/model`。请先退出当前会话（通过 `Ctrl+C` 或 `/quit`），接着运行 `hermes model` 完成提供商的配置，最后再启动新的会话。

### 订阅方案：您的套餐包含哪些服务

部分提供商允许您使用**消费者订阅套餐**（如 Claude Max、ChatGPT、SuperGrok / X Premium+ 等）而非 API 密钥来登录 Hermes。不过，不同提供商的订阅内容各有差异，这往往是产生账单意外的最主要原因。下表为简要说明，各提供商的详细信息请参阅其专属章节。

> 标有 *目前未在文档中说明* 的项即表示 Hermes 文档尚未明确该功能的行为。切勿自行推测，应查看对应提供商的账单面板，将这些内容视为待确认的问题。

| Plan / path | Can Hermes use it? | What gets consumed | What does NOT get consumed | Common surprise |
|---|---|---|---|---|
| **Anthropic — Claude Max + OAuth** | ✅ Yes — `hermes model` → Anthropic OAuth. Requires Max **and** purchased extra usage credits | The **extra/overage credits** you've added on top of the Max plan | The **base Max plan allowance** (the usage included in Claude Code by default) | All Hermes usage bills as "extra usage" even while your included Max allowance sits untouched |
| **Anthropic — Claude Pro** | ❌ No — Pro subscribers cannot use the OAuth path | Nothing (path unavailable) | Your Pro subscription | Pro looks like it should work; it doesn't. Use an `ANTHROPIC_API_KEY` instead (pay-per-token, independent of any Claude subscription) |
| **OpenAI Codex — ChatGPT plan OAuth** | ✅ Yes — `hermes model` → **ChatGPT or Codex Subscription** (ChatGPT OAuth device-code login, uses Codex models) | *Not currently documented* | *Not currently documented* | Docs cover auth and token refresh only; plan-quota semantics are not yet documented |
| **xAI — SuperGrok / X Premium+ OAuth** | ✅ Yes — browser OAuth, no API key needed | Your **subscription quota** (documented explicitly for X Search: OAuth is preferred over an API key and "uses your subscription quota instead of API spend"). Inference quota semantics beyond that: *not currently documented* | `XAI_API_KEY` / pay-per-token API spend, when OAuth credentials are configured and preferred | `HTTP 403` after a successful login — xAI has restricted OAuth API access to specific SuperGrok tiers despite an active in-app subscription |
| **Google — Gemini consumer plan (Google AI Pro / Ultra)** | ❌ No documented path — the `gemini` provider is API-key only (`GOOGLE_API_KEY` / `GEMINI_API_KEY`); Vertex AI uses GCP billing | Your **API key's quota** (free tier or billing-enabled Google Cloud project) — *consumer-plan consumption not currently documented* | *Not currently documented* | Free-tier keys can be exhausted after a handful of agent turns, because Hermes may make several model calls per user turn |

**Anthropic。** 该OAuth认证路径会将Claude Code视为您的Anthropic账户进行连接，且**仅适用于购买了额外使用额度的Claude Max套餐**——Hermes不会消耗Max套餐的基础额度，仅会使用额外的超额额度。Claude Pro订阅用户无法使用此路径；可行的替代方案是使用`ANTHROPIC_API_KEY`，按标准API定价根据该密钥对应的组织进行按令牌计费。详情请参见下文的[Anthropic（原生集成）](#anthropic-native)。

**OpenAI Codex。** Hermes通过ChatGPT的device-code OAuth方式进行身份验证，将凭证存储在`~/.hermes/auth.json`文件中，并能从`~/.codex/auth.json`导入现有的Codex CLI凭证。目前**尚未有文档说明哪些ChatGPT套餐层级支持该功能，以及Hermes的使用量如何计入您套餐的Codex使用限额**——[Nous Portal](#nous-portal)下的Codex相关说明仅涵盖了身份验证和令牌刷新机制。

**xAI（SuperGrok / X Premium+）。** 浏览器OAuth支持已激活的SuperGrok订阅或关联X账户中的X Premium+订阅，直接用于xAI工具（文本转语音、图像生成、视频生成、转录、X搜索）的承载令牌也可复用。如果登录成功后推理请求仍返回`HTTP 403`错误，那通常是xAI端的套餐层级或权限限制所致，而非令牌过期——解决方法是改用`XAI_API_KEY`。详情请参见下文的[xAI（Grok）](#xai-grok--responses-api--prompt-caching)以及[xAI Grok OAuth指南](../guides/xai-grok-oauth.md)。

**Google Gemini。** 目前无法使用面向普通用户的 Gemini 订阅来登录 Hermes——`gemini` 提供商需要 API 密钥，且费用将由 [Google Vertex AI](#google-vertex-ai) 计入您的 GCP 项目账单。建议为使用 Agent 配置已开启计费的 Google Cloud 项目，因为免费套餐的配额对于长时间运行的 Agent 会话来说过于有限。详情请参阅 [Google Gemini 指南](/guides/google-gemini)。

:::提示：一个订阅替代五个
如果您完全不想理会不同提供商的计划差异，[Nous Portal](#nous-portal) 支持通过一次 OAuth 登录即可使用涵盖 300 多种模型的功能。
:::

### Anthropic（原生版）

可直接通过 Anthropic API 使用 Claude 模型——无需 OpenRouter 代理。该版本支持三种认证方式：

当未选择明确的环境凭证时，凭证池中 Hermes 自有的 OAuth 授权将优先于借用的 Claude Code 登录信息。若没有自有的 OAuth 授权可用，借用来的登录信息将作为备用方案。辅助认证恢复功能会刷新失败请求所使用的凭证，而非无关的通用登录信息；否则，轮换借用来的登录信息可能会使原持有者的刷新令牌失效。

:::警告 需要 Claude Max 的“额外使用额度”积分  
当您通过 `hermes model` → Anthropic OAuth（或通过 `hermes auth add anthropic --type oauth`）进行身份验证时，Hermes 会以 Claude Code 的形式连接到您的 Anthropic 账户。**此功能仅适用于购买了额外使用额度的 Claude Max 套餐用户。** Hermes 不会消耗 Claude Max 基础套餐的默认使用额度——只有您额外购买的额度才会被使用。Claude Pro 订阅用户无法使用此方式。

如果您没有 Claude Max 套餐及额外额度，请改用 `ANTHROPIC_API_KEY` —— 此时请求将按照该密钥所属组织的标准 API 定价（与 Claude 订阅无关）按令牌数量计费。

```bash
# With an API key (pay-per-token)
export ANTHROPIC_API_KEY=***
hermes chat --provider anthropic --model claude-sonnet-4-6

# Preferred: authenticate through `hermes model`
# Hermes will use Claude Code's credential store directly when available
hermes model

# Manual override with a setup-token (fallback / legacy)
export ANTHROPIC_TOKEN=***  # setup-token or manual OAuth token
hermes chat --provider anthropic

# Auto-detect Claude Code credentials (if you already use Claude Code)
hermes chat --provider anthropic  # reads Claude Code credential files automatically
```

当您通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 会优先使用 Claude Code 自带的凭据存储机制，而非将令牌复制到 `~/.hermes/.env` 文件中。这样就能确保可续期的 Claude 凭据始终处于有效状态。

或者也可以将其设置为永久有效：
```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

:::提示：别名用法
`--provider claude` 和 `--provider claude-code` 也可作为 `--provider anthropic` 的简写形式使用。
:::

### GitHub Copilot

Hermes 将 GitHub Copilot 视为一等重要的模型提供方，并支持两种使用模式：

**`copilot` — 直接调用 Copilot API**（推荐）。该模式会利用您的 GitHub Copilot 订阅权限，通过 Copilot API 调用 GPT-5.x、Claude、Gemini 等模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

**身份验证选项**（按以下顺序进行检测）：

1. `COPILOT_GITHUB_TOKEN` 环境变量  
2. `GH_TOKEN` 环境变量  
3. `GITHUB_TOKEN` 环境变量  
4. 作为最后手段的 `gh auth token` CLI 命令  

如果未找到任何有效令牌，`hermes model` 会提供**OAuth 设备码登录**功能——该流程与 Copilot CLI 及 opencode 所使用的机制相同。

:::warning 令牌类型  
Copilot API **不支持**传统的个人访问令牌（`ghp_*`）。支持的令牌类型如下：

| 类型 | 前缀 | 获取方式 |
|------|------|----------|
| OAuth 令牌 | `gho_` | 通过 `hermes model` → GitHub Copilot → 使用 GitHub 登录 |
| 细粒度 PAT 令牌 | `github_pat_` | 进入 GitHub 设置 → 开发者设置 → 细粒度令牌（需具备 **Copilot Requests** 权限） |
| GitHub 应用令牌 | `ghu_` | 通过安装 GitHub 应用来获取 |

如果 `gh auth token` 返回的是 `ghp_*` 类型的令牌，请改用 `hermes model` 通过 OAuth 方式进行身份验证。
:::

:::info Hermes 中的 Copilot 身份验证机制  
Hermes 会将支持的 GitHub 令牌（`gho_*`、`github_pat_*` 或 `ghu_*`）直接发送至 `api.githubcopilot.com`，同时附带 Copilot 特有的请求头（`Editor-Version`、`Copilot-Integration-Id`、`Openai-Intent`、`x-initiator`）。

当遇到 HTTP 401 错误时，Hermes 会在尝试其他方案之前先进行一次临时的凭证恢复操作：

1. 按照常规优先级顺序重新查找令牌（`COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` → `gh auth token`）  
2. 使用更新后的请求头重新构建共享的 OpenAI 客户端  
3. 再次尝试发送请求
部分较旧的社区代理会使用 `api.github.com/copilot_internal/v2/token` 这一交换流程。对于某些账户类型，该接口可能无法访问（会返回 404 错误）。因此，Hermes 将直接令牌认证作为主要方案，并通过运行时凭证刷新与重试机制来提升系统稳定性。
:::

**API 路由**：GPT-5 及更高版本模型（`gpt-5-mini` 除外）会自动使用 Responses API；其余所有模型（如 GPT-4o、Claude、Gemini 等）则使用 Chat Completions。模型类型会从实时的 Copilot 目录中自动识别。

**`copilot-acp` — Copilot ACP 智能体后端**：该组件会以子进程的形式启动本地的 Copilot CLI：

```bash
hermes chat --provider copilot-acp --model copilot-acp
# Requires the GitHub Copilot CLI in PATH and an existing `copilot login` session
```

**永久配置：**
```yaml
model:
  provider: "copilot"
  default: "gpt-5.4"
```

| 环境变量 | 描述 |
|---------------------|-------------|
| `COPILOT_GITHUB_TOKEN` | 用于 Copilot API 的 GitHub 令牌（优先级最高） |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot CLI 可执行文件的路径（默认值：`copilot`） |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 ACP 参数（默认值：`--acp --stdio`） |

### 一流的 API 密钥提供方

这些提供方拥有专用的提供方 ID，并具备内置支持功能。您可以设置 API 密钥，再通过 `--provider` 参数来选择对应的提供方：

```bash
# Fireworks AI
hermes chat --provider fireworks --model accounts/fireworks/models/kimi-k2p6
# Requires: FIREWORKS_API_KEY in ~/.hermes/.env

# NovitaAI Model API
hermes chat --provider novita --model moonshotai/kimi-k2.5
# Requires: NOVITA_API_KEY in ~/.hermes/.env

# Ramp Router (model IDs come from your account's live catalog)
hermes chat --provider router --model gpt-5.4-mini
# Requires: RAMP_ROUTER_API_KEY in ~/.hermes/.env

# z.ai / ZhipuAI GLM
hermes chat --provider zai --model glm-5
# Requires: GLM_API_KEY in ~/.hermes/.env

# Kimi / Moonshot AI (international: api.moonshot.ai)
hermes chat --provider kimi-coding --model kimi-for-coding
# Requires: KIMI_API_KEY in ~/.hermes/.env

# Kimi / Moonshot AI (China: api.moonshot.cn)
hermes chat --provider kimi-coding-cn --model kimi-k2.5
# Requires: KIMI_CN_API_KEY in ~/.hermes/.env

# MiniMax (global endpoint)
hermes chat --provider minimax --model MiniMax-M2.7
# Requires: MINIMAX_API_KEY in ~/.hermes/.env

# MiniMax (China endpoint)
hermes chat --provider minimax-cn --model MiniMax-M2.7
# Requires: MINIMAX_CN_API_KEY in ~/.hermes/.env

# Qwen Cloud / DashScope (Qwen models)
hermes chat --provider alibaba --model qwen3.5-plus
# Requires: DASHSCOPE_API_KEY in ~/.hermes/.env

# Xiaomi MiMo
hermes chat --provider xiaomi --model mimo-v2-pro
# Requires: XIAOMI_API_KEY in ~/.hermes/.env

# Tencent TokenHub (Hy4 preview)
hermes chat --provider tencent-tokenhub --model hy4-preview
# Requires: TOKENHUB_API_KEY in ~/.hermes/.env

# Tencent TokenPlan (Hy4 preview via Anthropic Messages endpoint)
hermes chat --provider tencent-tokenplan --model hy4-preview
# Requires: TOKENPLAN_API_KEY in ~/.hermes/.env

# Arcee AI (Trinity models)
hermes chat --provider arcee --model trinity-large-thinking
# Requires: ARCEEAI_API_KEY in ~/.hermes/.env

# Meta Model API (Muse Spark family)
hermes chat --provider meta-ai --model muse-spark-1.2
# Requires: MODEL_API_KEY in ~/.hermes/.env

# GMI Cloud
# Use the exact model ID returned by GMI's /v1/models endpoint.
hermes chat --provider gmi --model zai-org/GLM-5.1-FP8
# Requires: GMI_API_KEY in ~/.hermes/.env

# Nebius Token Factory
hermes chat --provider nebius --model deepseek-ai/DeepSeek-V4-Pro
# Requires: NEBIUS_API_KEY in ~/.hermes/.env
```

Fireworks 使用其固有的斜杠格式的模型目录编号，例如 `accounts/fireworks/models/kimi-k2p6`。运行 `hermes model` 命令后选择 **Fireworks AI**，即可从实时目录中选取模型，或直接输入其他 Fireworks 模型编号。默认端点为 `https://api.fireworks.ai/inference/v1`；如需更改端点，请通过 `config.yaml` 文件中的 `model.base_url` 进行配置，而非 `.env` 文件。

或者，您也可以在 `config.yaml` 中永久设置该服务提供商：
```yaml
model:
  provider: "gmi"
  default: "zai-org/GLM-5.1-FP8"
```

基础 URL 可通过 `NOVITA_BASE_URL`、`GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL`、`DASHSCOPE_BASE_URL`、`XIAOMI_BASE_URL`、`GMI_BASE_URL`、`META_BASE_URL` 或 `TOKENHUB_BASE_URL` 这些环境变量进行覆盖。

:::note Meta 贡献者等级
`muse-spark-1.2-contributor` 和 `muse-spark-1.3-contributor` 是 Meta 设定的贡献者等级——Meta 可能会使用您的提示词及回复内容进行模型训练，因此在使用这些等级的模型时，[交互式模型选择界面会要求您确认](../user-guide/configuring-models.md)。如需了解当前的定价与速率限制，请参阅 [Meta Model API 定价与速率限制](https://dev.meta.ai/docs/pricing-rate-limits/)。对于需要保密的工作，建议使用标准的 `muse-spark-1.2` / `muse-spark-1.3` 版本（不会进行训练）。
:::

:::note Z.AI 端点自动检测
在使用 Z.AI / GLM 提供商时，Hermes 会自动探测多个端点（全球端点、中国端点以及不同编程语言版本端点），以找到能够识别您 API 密钥的端点。您无需手动设置 `GLM_BASE_URL`——系统会自动检测并缓存可用的端点。
:::

### xAI (Grok) — 响应 API + 提示词缓存
xAI 通过响应 API（`codex_responses` 传输协议）与 Grok 4 模型相连，从而为其提供自动推理功能——无需设置 `reasoning_effort` 参数，服务器会默认执行推理操作。您只需在 `~/.hermes/.env` 文件中设置 `XAI_API_KEY`，并在“Hermes 模型”选项中选择 xAI；或者直接在 `/model grok-4-fast-reasoning` 中将 `grok` 作为快捷方式使用即可。

SuperGrok及X Premium+订阅用户无需使用API密钥，即可通过浏览器OAuth方式进行登录——可在“hermes model”中选择**xAI Grok OAuth (SuperGrok / Premium+)**，或执行`hermes auth add xai-oauth`命令。对于直接调用xAI的工具（如文本转语音、图像生成、视频生成、语音转文字功能），系统会自动复用相同的OAuth令牌。如需了解完整操作流程，请参阅[xAI Grok OAuth指南](../guides/xai-grok-oauth.md)；若Hermes运行在远程主机上，还需参考[通过SSH/远程主机实现OAuth连接](../guides/oauth-over-ssh.md)，了解所需的`ssh -L`隧道配置方法。

当将xAI作为服务提供商使用时（即任何包含`x.ai`字样的基础URL），Hermes会在每次API请求中自动添加`x-grok-conv-id`请求头，从而启用提示词缓存功能。这样一来，同一对话会话中的请求就会被路由至同一服务器，使xAI的基础设施能够重复使用已缓存的系统提示词和对话历史记录。

该功能无需任何额外配置——一旦检测到xAI接口且存在会话ID，缓存便会自动启用。这有助于降低多轮对话的延迟并节省成本。

xAI还提供了专用的文本转语音接口（`/v1/tts`）。可在“hermes tools”→“语音与文本转语音”选项中选择**xAI TTS**，或访问[语音与文本转语音功能页面](../user-guide/features/tts.md#text-to-speech)查看相关配置信息。

**已停用的xAI模型迁移（2026年5月15日）：** xAI将于2026年5月15日停止支持`grok-4*`、`grok-3`、`grok-code-fast-1`以及`grok-imagine-image-pro`这些模型。无论是在启动`hermes doctor`还是`hermes chat`时，系统都会检测是否存在仍指向已停用模型的配置，并提示推荐的替代方案。如需一次性重写配置，可使用`hermes migrate xai`命令——该命令默认会进行试运行，如需实际应用更改，请添加`--apply`参数（之前的配置文件会先以带时间戳的形式保存在`backups/config/`目录中）。

```bash
hermes migrate xai          # preview replacements
hermes migrate xai --apply  # rewrite ~/.hermes/config.yaml in place
```

**xAI 网页搜索后端。** 当启用[网页搜索](../user-guide/features/web-search.md)工具集时，`web.backend: xai`会使用相同的`XAI_API_KEY`/OAuth凭据，将搜索请求路由至xAI托管的搜索端点。如果xAI已作为提供方配置完成，则无需额外设置。

### NovitaAI

[NovitaAI](https://novita.ai)是为开发者与智能体打造的原生AI云平台。该平台通过一个统一界面提供三大产品线：涵盖200多种模型的Model API、用于构建和运行智能体的Agent Sandbox，以及支持可扩展计算的GPU Cloud。

```bash
# Use any available model
hermes chat --provider novita --model moonshotai/kimi-k2.5
# Requires: NOVITA_API_KEY in ~/.hermes/.env

# Short alias
hermes chat --provider novita-ai --model deepseek/deepseek-v3-0324
```

或者直接在 `config.yaml` 中将其永久设置：
```yaml
model:
  provider: "novita"
  default: "moonshotai/kimi-k2.5"
  base_url: "https://api.novita.ai/openai/v1"
```

您可以在 [novita.ai/settings/key-management](https://novita.ai/settings/key-management) 获取 API 密钥。也可通过 `NOVITA_BASE_URL` 参数来指定自定义的基础网址。

### Ollama Cloud — 托管版 Ollama 模型、OAuth 与 API 密钥

[Ollama Cloud](https://ollama.com/cloud) 提供与本地版 Ollama 相同的开放模型库，且无需 GPU 支持。在 `hermes model` 中选择 **Ollama Cloud**，粘贴从 [ollama.com/settings/keys](https://ollama.com/settings/keys) 获取的 API 密钥，Hermes 即会自动识别可用的模型。

```bash
hermes model
# → pick "Ollama Cloud"
# → paste your OLLAMA_API_KEY
# → select from discovered models (gpt-oss:120b, glm-4.6:cloud, qwen3-coder:480b-cloud, etc.)
```

或者直接使用 `config.yaml`：
```yaml
model:
  provider: "ollama-cloud"
  default: "gpt-oss:120b"
```

模型目录会从 `ollama.com/v1/models` 动态获取并缓存一小时。`model:tag` 格式（例如 `qwen3-coder:480b-cloud`）在处理过程中会被保留原样——请勿使用连字符。

:::提示 Ollama Cloud 与本地 Ollama 的区别
两者均支持相同的 OpenAI 兼容 API。Ollama Cloud 是一种一级提供商（需使用 `--provider ollama-cloud` 及 `OLLAMA_API_KEY` 参数）；而本地 Ollama 则通过自定义端点方式连接（基础网址为 `http://localhost:11434/v1`，无需密钥）。对于那些无法在本地运行的大型模型，建议使用云服务；若注重隐私或需离线工作，则可选择本地版本。
:::

### AWS Bedrock
通过 AWS Bedrock 可调用 Anthropic Claude、Amazon Nova、DeepSeek v3.2、Meta Llama 4 等其他模型。该方案采用 AWS SDK (`boto3`) 的身份验证机制——无需 API 密钥，仅需标准的 AWS 认证信息即可。

```bash
# Simplest — named profile in ~/.aws/credentials
hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6

# Or with explicit env vars
AWS_PROFILE=myprofile AWS_REGION=us-east-1 hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6
```

或者永久性地配置在 `config.yaml` 中：
```yaml
model:
  provider: "bedrock"
  default: "us.anthropic.claude-sonnet-4-6"
bedrock:
  region: "us-east-1"          # or set AWS_REGION
  # profile: "myprofile"       # or set AWS_PROFILE
  # discovery: true            # auto-discover region from IAM
  # guardrail:                 # optional Bedrock Guardrails
  #   guardrail_identifier: "your-guardrail-id"
  #   guardrail_version: "DRAFT"
```

认证过程采用标准的 boto3 认证机制：可直接指定 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`，或从 `~/.aws/credentials` 文件中读取 `AWS_PROFILE`；也可通过 EC2/ECS/Lambda 上的 IAM 角色、IMDS，或是 SSO 方式进行认证。若您已使用 AWS CLI 完成认证，则无需设置任何环境变量。

Bedrock 在底层实际上使用了 **Converse API**——所有请求都会被转换为与模型类型无关的格式，因此相同的配置即可适用于 Claude、Nova、DeepSeek 以及 Llama 等模型。仅当您需要调用非默认区域端点时，才需设置 `BEDROCK_BASE_URL`。

如需了解 IAM 设置、区域选择以及跨区域推理的详细操作指南，请参阅 [AWS Bedrock 指南](/guides/aws-bedrock)。

### Google Vertex AI

通过 Vertex AI 提供的兼容 OpenAI 的端点，在 Google Cloud 上运行 Gemini 模型。其认证方式采用 **OAuth2**，系统会基于服务账户 JSON 文件或应用程序默认凭据（ADC）生成有效期较短（约 1 小时）的访问令牌。该平台**不存在静态 API 密钥**，Hermes 会自动为您生成并刷新令牌，甚至在会话过程中出现 `401` 错误时也会重新生成令牌。

```bash
# Service account JSON (recommended for servers / gateways)
echo "VERTEX_CREDENTIALS_PATH=/path/to/service-account.json" >> ~/.hermes/.env
# or Application Default Credentials
gcloud auth application-default login

hermes model   # → "Google Vertex AI" → project → region → model
```

或者通过 `config.yaml` 配置（项目名和区域信息不属于敏感内容，会存储在此文件中；而凭证路径则仍保留在 `.env` 文件中）：
```yaml
model:
  provider: "vertex"
  default: "google/gemini-3-flash-preview"   # Vertex requires the google/ prefix
vertex:
  project_id: "my-gcp-project"   # blank → use the project embedded in the credentials
  region: "global"               # required for the Gemini 3.x previews
```

`VERTEX_PROJECT_ID` / `VERTEX_REGION` 环境变量会覆盖 `config.yaml` 中的对应值。Hermes 会在首次使用时延迟安装 `google-auth`；如果需要修复已有的托管安装，可运行 `hermes setup` 命令。如需完整的操作指南，请参阅 [Google Vertex AI 指南](/guides/google-vertex)；若想使用静态 API 密钥的 AI Studio 方式，则可参考 [Google Gemini 指南](/guides/google-gemini)。

### Qwen Portal（OAuth）

基于浏览器的 OAuth 登录方式的阿里巴巴 Qwen Portal。在 `hermes model` 中选择 **Qwen OAuth (Portal)**，通过浏览器完成登录，Hermes 会自动保存刷新令牌。

```bash
hermes model
# → pick "Qwen OAuth (Portal)"
# → browser opens; sign in with your Alibaba account
# → confirm — credentials are saved to ~/.hermes/auth.json

hermes chat   # uses portal.qwen.ai/v1 endpoint
```

或者配置 `config.yaml` 文件：
```yaml
model:
  provider: "qwen-oauth"
  default: "qwen3-coder-plus"
```

仅当门户端点地址发生变更时，才需设置 `HERMES_QWEN_BASE_URL`（默认值为 `https://portal.qwen.ai/v1`）。

:::提示 Qwen OAuth 与 Qwen Cloud（阿里云 DashScope）的区别
`qwen-oauth` 方式使用面向用户的 Qwen Portal 并通过 OAuth 进行登录，非常适合个人用户使用。而 `alibaba` 提供商则基于 Qwen Cloud（阿里云 DashScope）并使用 `DASHSCOPE_API_KEY`，更适用于自动化或生产环境中的任务。虽然两者最终都会调用 Qwen 系列模型，但其端点地址有所不同。
:::

### 阿里云 Coding Plan

如果您订阅了阿里云的 **Coding Plan**（这是一种与标准 DashScope API 访问不同的计费方案），Hermes 会将其作为一个独立的顶级提供商来支持，即 `alibaba-coding-plan`。其端点地址为 `https://coding-intl.dashscope.aliyuncs.com/v1`。该提供商与常规的 `alibaba` 提供商一样兼容 OpenAI，但基础 URL 及计费方式有所不同。

```yaml
model:
  provider: alibaba_coding     # alias for alibaba-coding-plan
  model: qwen3-coder-plus
```

或者通过 CLI 命令：

```bash
hermes chat --provider alibaba_coding --model qwen3-coder-plus
```

`alibaba_coding` 使用与 `alibaba` 配置项已有的相同 `DASHSCOPE_API_KEY`——无需单独的密钥，仅需不同的路由目标即可。在注册该提供程序之前，那些在 `config.yaml` 中设置 `provider: alibaba_coding` 的用户会自动被路由至 OpenRouter。

对于中国内地端点（`alibaba-coding-plan-cn`，地址为 `https://coding.dashscope.aliyuncs.com/v1`），需设置 `ALIBABA_CODING_PLAN_CN_API_KEY`。虽然中国内地的该提供程序仍会回退使用 `ALIBABA_CODING_PLAN_API_KEY` / `DASHSCOPE_API_KEY`，但若仅设置了共享密钥，则 `/model` 选择器只会显示国际版选项；此时需设置中国内地的专用密钥（或在 `config.yaml` 中指定 `provider: alibaba-coding-plan-cn`），才能查看对应的中国内地选项。`alibaba-token-plan-cn` 同样如此，需使用 `ALIBABA_TOKEN_PLAN_CN_API_KEY`。

### MiniMax（OAuth）

通过浏览器 OAuth 登录即可使用 MiniMax-M2.7——无需 API 密钥。在 `hermes model` 中选择 **MiniMax (OAuth)**，通过浏览器完成登录，Hermes 会自动保存访问令牌和刷新令牌。该功能在底层实际上使用的是与 Anthropic Messages 兼容的端点（`/anthropic`）。

```bash
hermes model
# → pick "MiniMax (OAuth)"
# → browser opens; sign in with your MiniMax account (global or CN region)
# → confirm — credentials are saved to ~/.hermes/auth.json

hermes chat   # uses api.minimax.io/anthropic endpoint
```

或者配置 `config.yaml` 文件：
```yaml
model:
  provider: "minimax-oauth"
  default: "MiniMax-M2.7"
```

支持的模型包括：`MiniMax-M2.7`（主模型）以及默认以有线连接方式作为辅助模型的 `MiniMax-M2.7-highspeed`。在通过 OAuth 进行授权时，系统会忽略 `MINIMAX_API_KEY` / `MINIMAX_BASE_URL` 这两个参数。

:::提示 MiniMax OAuth 与 API 密钥的区别
`minimax-oauth` 方式通过 MiniMax 提供的面向用户的门户网站进行 OAuth 登录，无需进行任何账单设置。而 `minimax` 及 `minimax-cn` 这两类提供程序则使用 `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY` 来实现程序化访问。如需详细操作指南，请参阅 [MiniMax OAuth 使用指南](/guides/minimax-oauth)。
:::

### NVIDIA NIM

可通过 [build.nvidia.com](https://build.nvidia.com)（免费 API 密钥）或本地的 NIM 接口来使用 Nemotron 及其他开源模型。

```bash
# Cloud (build.nvidia.com)
hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
# Requires: NVIDIA_API_KEY in ~/.hermes/.env

# Local NIM endpoint — override base URL
NVIDIA_BASE_URL=http://localhost:8000/v1 hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b
```

或者直接在 `config.yaml` 中将其永久设置：
```yaml
model:
  provider: "nvidia"
  default: "nvidia/nemotron-3-super-120b-a12b"
```

:::提示：本地 NIM
对于本地部署环境（DGX Spark、本地 GPU），请将 `NVIDIA_BASE_URL` 设置为 `http://localhost:8000/v1`。NIM 提供与 build.nvidia.com 完全一致的 OpenAI 兼容型聊天补全 API，因此只需修改一行环境变量即可实现云端与本地的切换。
:::

Hermes 会自动在发送至 `build.nvidia.com` 的每个请求中添加 NIM 计费来源标识头——无需任何额外配置。这样一来，NVIDIA 的计费面板就能准确统计相应的使用量。
### GMI 云服务
可通过 [GMI Cloud](https://www.gmicloud.ai/) 使用开放模型与推理模型——该服务支持 OpenAI 兼容 API，并采用 API 密钥进行身份验证。

```bash
# GMI Cloud
hermes chat --provider gmi --model deepseek-ai/DeepSeek-V3.2
# Requires: GMI_API_KEY in ~/.hermes/.env
```

或者可在 `config.yaml` 中将其永久设置：
```yaml
model:
  provider: "gmi"
  default: "deepseek-ai/DeepSeek-V3.2"
```

基础 URL 可通过 `GMI_BASE_URL` 参数进行覆盖（默认值为 `https://api.gmi-serving.com/v1`）。

### 实际计算机模式

您可以通过 [Actual Computer](https://actual.inc) 将自己的硬件搭建为私有推理集群。该模式提供两种兼容 OpenAI 的服务方式（Hermes 均使用 Responses API 进行数据传输）：

- **托管中继模式** — 使用 `https://api.actual.inc`，采用端到端加密技术，将请求路由至*您的*集群。需使用从 [actual.inc/user/keys](https://actual.inc/user/keys) 获取的 `ac_` 类型推理密钥进行身份验证。
- **本地守护进程模式** — 在设备上运行于 `http://127.0.0.1:8080`，完全离线运行。无需 API 密钥：Hermes 会自动检测回环基础 URL，并使用内置的占位符进行身份验证。

```bash
# Hosted relay (ACTUAL_API_KEY in ~/.hermes/.env)
hermes chat --provider actual --model <model-id-from-your-cluster>

# Local daemon (ACTUAL_BASE_URL=http://127.0.0.1:8080 in ~/.hermes/.env, no key)
hermes chat --provider actual --model <installed-model-name>
```

或者直接在 `config.yaml` 中永久设置该值：
```yaml
model:
  provider: "actual"
  default: "<model-id>"
```

备注：  
- 模型编号来自您集群的 `GET /v1/models` 接口——可通过 `hermes model` 命令或 `curl -s https://api.actual.inc/v1/models -H "Authorization: Bearer $ACTUAL_API_KEY"` 查询获取。  
- 纯主机地址会自动标准化：例如 `ACTUAL_BASE_URL=http://127.0.0.1:8080` 会自动转换为 `http://127.0.0.1:8080/v1`。  
- 推理难度会被限制在 Actual 支持的范围内（`none/low/medium/high/max`）——全局设置的 `xhigh`/`ultra` 等级别不会导致 400 错误。  
- 小型本地模型：Hermes 的完整默认工具集加上系统提示词可能会超出 32k 的上下文窗口限制，从而导致 llama.cpp 系列服务器返回空流错误。此时可限制使用的工具集（如 `-t file,web`），或为模型加载更大的上下文窗口。可选的 `actual-setup` 技能（可通过 `hermes skills install official/devops/actual-setup` 安装）可提供详细的设置与故障排除指南。  
- 别名：`actual-computer`、`actualcomputer`、`aci`。  

### StepFun  

通过 [StepFun](https://platform.stepfun.com) 提供的 Step 系列模型——采用与 OpenAI 兼容的 API，支持 API 密钥认证。

```bash
# StepFun
hermes chat --provider stepfun --model step-3.5-flash
# Requires: STEPFUN_API_KEY in ~/.hermes/.env
```

或者直接在 `config.yaml` 中永久设置该值：
```yaml
model:
  provider: "stepfun"
  default: "step-3.5-flash"
```

基础 URL 可通过 `STEPFUN_BASE_URL` 参数进行覆盖（默认值为 `https://api.stepfun.com/v1`）。

### Hugging Face 推理提供商

[Hugging Face 推理提供商](https://huggingface.co/docs/inference-providers) 能够通过统一的 OpenAI 兼容接口 (`router.huggingface.co/v1`) 调用 20 多种开源模型。系统会自动将请求路由至当前最快的可用后端（如 Groq、Together、SambaNova 等），并具备自动故障转移功能。

```bash
# Use any available model
hermes chat --provider huggingface --model Qwen/Qwen3.5-397B-A17B
# Requires: HF_TOKEN in ~/.hermes/.env

# Short alias
hermes chat --provider hf --model deepseek-ai/DeepSeek-V3.2
```

或者直接在 `config.yaml` 中永久设置该值：
```yaml
model:
  provider: "huggingface"
  default: "Qwen/Qwen3.5-397B-A17B"
```

请在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 处获取您的令牌——务必启用“Make calls to Inference Providers”权限。该服务包含免费套餐（每月提供0.10美元额度，且不会在提供商费用基础上加价）。

您可以在模型名称后添加路由后缀：`:fastest`（默认值）、`:cheapest` 或 `:provider_name`，以此强制使用特定的后端。

您也可以通过 `HF_BASE_URL` 变量来覆盖基础网址。

## 自定义及自托管的LLM提供商

Hermes Agent可兼容**任何符合OpenAI标准的API接口**。只要服务器实现了 `/v1/chat/completions` 接口，您就可以让Hermes与之连接。这意味着您可以使用本地模型、GPU推理服务器、多提供商路由器，或是任何第三方API。

### 基本配置

配置自定义接口有三种方式：

**交互式设置（推荐）：**
```bash
hermes model
# Select "Custom endpoint (self-hosted / VLLM / etc.)"
# Enter: API base URL, API key, Model name
```

**手动配置（`config.yaml`）：**
```yaml
# In ~/.hermes/config.yaml
model:
  default: your-model-name
  provider: custom
  base_url: http://localhost:8000/v1
  api_key: your-key-or-leave-empty-for-local
```

:::warning 旧版环境变量
`.env` 文件中的 `LLM_MODEL` 已**被移除**——模型及端点配置的唯一权威来源现为 `config.yaml`。`OPENAI_BASE_URL` 仍然有效，但**仅适用于 `openai-api` 提供商**（它会覆盖 OpenAI 端点，以便直接通过 API 密钥访问）。对于其他提供商及自定义端点，请使用 `hermes model` 命令，或直接在 `config.yaml` 中设置 `model.base_url`。如果您的 `.env` 文件中存在过时的配置项，它们会在下次执行 `hermes setup` 或配置迁移时被自动清除。
:::

这两种方式都会将配置保存到 `config.yaml` 中，而该文件正是模型、提供商及基础 URL 的权威配置源。

### 使用 `/model` 切换模型

:::warning `hermes model` 与 `/model` 的区别
**`hermes model`**（在终端中运行，无需处于任何聊天会话中）是**完整的提供商设置向导**。可通过它添加新提供商、执行 OAuth 流程、输入 API 密钥以及配置自定义端点。

**`/model`**（在正在进行的 Hermes 聊天会话中输入）仅能**在您已设置的提供商和模型之间切换**。它无法添加新提供商、执行 OAuth 流程或要求输入 API 密钥。如果您仅配置了一个提供商（例如 OpenRouter），则 `/model` 只会显示该提供商对应的模型。

**如需添加新提供商**：请退出当前会话（使用 `Ctrl+C` 或 `/quit`），然后运行 `hermes model` 设置新提供商，之后再启动新的会话。
:::

一旦您配置了至少一个自定义端点，即可在会话进行中切换模型：

```
/model custom:qwen-2.5          # Switch to a model on your custom endpoint
/model custom                    # Auto-detect the model from the endpoint
/model openrouter:claude-sonnet-4 # Switch back to a cloud provider
```

如果您已配置了**带名称的自定义 Provider**（见下文），请使用三重语法：

```
/model custom:local:qwen-2.5    # Use the "local" custom provider with model qwen-2.5
/model custom:work:llama3       # Use the "work" custom provider with llama3
```

在切换提供方时，Hermes 会将基础 URL 和提供方信息保存在配置中，从而确保这些设置在重启后依然有效。当从自定义端点切换为内置提供方时，过时的基础 URL 会自动被清除。

:::提示
使用 ` /model custom`（不指定模型名称）可查询您的端点对应的 `/models` API，如果已加载的模型恰好只有一个，系统会自动选择该模型。这非常适合运行单个模型的本地服务器。
:::

以下所有内容均遵循相同的模式——只需更改 URL、键值以及模型名称即可。

---

### Ollama — 本地模型，零配置部署

[Ollama](https://ollama.com/) 只需一条命令即可在本地运行开源模型。最适合用于：快速的本地实验、对隐私要求较高的场景以及离线使用。它还支持通过兼容 OpenAI 的 API 调用各类工具。

```bash
# Install and run a model
ollama pull qwen2.5-coder:32b
ollama serve   # Starts on port 11434
```

接下来配置 Hermes：

```bash
hermes model
# Select "Custom endpoint (self-hosted / VLLM / etc.)"
# Enter URL: http://localhost:11434/v1
# Skip API key (Ollama doesn't need one)
# Enter model name (e.g. qwen2.5-coder:32b)
```

或者直接配置 `config.yaml` 文件：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 64000   # See warning below
```

:::警告 Ollama 的默认上下文长度非常短  
Ollama 默认不会使用模型全部的上下文窗口。根据您的显存大小，默认值如下：  

| 可用显存 | 默认上下文长度 |
|----------|----------------|
| 小于 24 GB | **4,096 个标记** |
| 24–48 GB | 32,768 个标记 |
| 48 GB及以上 | 256,000 个标记 |

Hermes Agent 在使用工具时需要至少 **64,000 个标记** 的上下文长度。如果上下文窗口过小，系统在启动时会拒绝运行，因为系统提示、工具结构以及对话状态都需要足够的空间来支持可靠的多步骤工作流程。  

**如何增加上下文长度**（请选择一种方法）：

```bash
# Option 1: Set server-wide via environment variable (recommended)
OLLAMA_CONTEXT_LENGTH=64000 ollama serve

# Option 2: For systemd-managed Ollama
sudo systemctl edit ollama.service
# Add: Environment="OLLAMA_CONTEXT_LENGTH=64000"
# Then: sudo systemctl daemon-reload && sudo systemctl restart ollama

# Option 3: Bake it into a custom model (persistent per-model)
echo -e "FROM qwen2.5-coder:32b\nPARAMETER num_ctx 64000" > Modelfile
ollama create qwen2.5-coder-64k -f Modelfile
```

**无法通过兼容 OpenAI 的 API（`/v1/chat/completions`）来设置上下文长度**。该参数必须通过服务器端配置或通过 Modelfile 来设定。这正是将 Ollama 与 Hermes 等工具集成时最容易引发混淆的问题所在。
:::

**请确认您的上下文设置正确：**

```bash
ollama ps
# Look at the CONTEXT column — it should show your configured value
```

:::提示
使用 `ollama list` 可以查看可用的模型列表。通过 `ollama pull <model>` 即可从 [Ollama 模型库](https://ollama.com/library) 中下载任意模型。Ollama 会自动处理 GPU 负载转移功能——在大多数配置下无需额外设置即可正常工作。
:::

---

### vLLM — 高性能 GPU 推理引擎

[vLLM](https://docs.vllm.ai/) 是用于生产环境 LLM 服务的标准方案。其优势在于：能在 GPU 硬件上实现最高吞吐量、支持大型模型处理以及连续批处理功能。

```bash
pip install vllm
vllm serve meta-llama/Llama-3.1-70B-Instruct \
  --port 8000 \
  --max-model-len 65536 \
  --tensor-parallel-size 2 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes
```

接下来配置 Hermes：

```bash
hermes model
# Select "Custom endpoint (self-hosted / VLLM / etc.)"
# Enter URL: http://localhost:8000/v1
# Skip API key (or enter one if you configured vLLM with --api-key)
# Enter model name: meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** vLLM 默认会读取模型设定的 `max_position_embeddings` 值。如果该数值超过了 GPU 的内存容量，系统就会报错，并要求用户将 `--max-model-len` 的值调低。您也可以使用 `--max-model-len auto` 选项，让系统自动查找合适的最大长度。若希望将更多上下文加载到 VRAM 中，可设置 `--gpu-memory-utilization 0.95`（默认值为 0.9）。

**调用工具时需要指定特定参数：**

| 参数 | 用途 |
|------|------|
| `--enable-auto-tool-choice` | 当 `tool_choice: "auto"`（即 Hermes 的默认设置）时必须使用此参数 |
| `--tool-call-parser <name>` | 用于解析模型所使用的工具调用格式的解析器 |

支持的解析器包括：`hermes`（适用于 Qwen 2.5、Hermes 2/3）、`llama3_json`（适用于 Llama 3.x）、`mistral`、`deepseek_v3`、`deepseek_v31`、`xlam`、`pythonic`。若未指定这些参数，工具调用功能将无法正常工作——模型只会以文本形式输出工具调用指令。

**Qwen 推理解析器：** 当兼容 OpenAI 的服务器返回结构化的推理元数据（如 `reasoning`、`reasoning_content` 以及流式推理增量数据）时，Hermes 会保留这些数据。这类元数据被视为推理/思考过程的相关记录，而非助手最终呈现的答案替代品。对于通过 vLLM 提供服务的 Qwen 推理模型，请确保最终呈现给用户的响应仍包含在 `content` 字段中。如果在您的部署环境中使用 `--reasoning-parser qwen3` 后导致 `content` 为空，要么禁用该解析器，要么通过 `extra_body` 传递服务器支持的请求选项，例如 `chat_template_kwargs.enable_thinking: false`。

:::提示
vLLM 支持人类易于理解的容量单位：`--max-model-len 64k`（小写 k 表示 1000，大写 K 表示 1024）。
:::

---

### SGLang — 基于 RadixAttention 的快速服务引擎

[SGLang](https://github.com/sgl-project/sglang) 是 vLLM 的替代方案，它采用 RadixAttention 技术来实现 KV 缓存的重用。该引擎尤其适用于：多轮对话（前缀缓存）、受限解码以及结构化输出场景。

```bash
pip install "sglang[all]"
python -m sglang.launch_server \
  --model meta-llama/Llama-3.1-70B-Instruct \
  --port 30000 \
  --context-length 65536 \
  --tp 2 \
  --tool-call-parser qwen
```

接下来配置 Hermes：

```bash
hermes model
# Select "Custom endpoint (self-hosted / VLLM / etc.)"
# Enter URL: http://localhost:30000/v1
# Enter model name: meta-llama/Llama-3.1-70B-Instruct
```

**上下文长度：** SGLang 默认会从模型的配置文件中读取该值。如需更改，可使用 `--context-length` 参数进行覆盖。若需超出模型规定的最大上下文长度，可设置 `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。

**工具调用功能：** 需使用 `--tool-call-parser` 参数，并搭配对应模型系列的解析器，例如：`qwen`（Qwen 2.5）、`llama3`、`llama4`、`deepseekv3`、`mistral`、`glm`。若未设置此参数，工具调用结果将以纯文本形式返回。

:::注意 SGLang 的默认最大输出token数为128
如果响应内容似乎被截断，可检查服务器端的生成默认设置，并在服务器端进行相应配置（例如 SGLang 的 `--default-max-tokens` 参数）。Hermes 并未提供输出token数的限制设置。
:::

---

### llama.cpp / llama-server — CPU与Metal推理

[llama.cpp](https://github.com/ggml-org/llama.cpp) 能在CPU、Apple Silicon（Metal）以及消费级GPU上运行量化后的模型。非常适合以下场景：在没有数据中心级GPU的环境下运行模型、Mac用户使用，以及边缘设备部署。

```bash
# Build and start llama-server
cmake -B build && cmake --build build --config Release
./build/bin/llama-server \
  --jinja -fa \
  -c 64000 \
  -ngl 99 \
  -m models/qwen2.5-coder-32b-instruct-Q4_K_M.gguf \
  --port 8080 --host 0.0.0.0
```

**上下文长度（`-c`）：** 最新版本的默认值为 `0`，此时会从 GGUF 元数据中读取模型的训练上下文。对于训练上下文超过 128k 的模型，若尝试为整个 KV 缓存分配内存，可能会导致内存不足。建议为 Hermes 显式设置 `-c` 参数，其值至少应为 64,000 个标记。如果使用了并行任务槽（`-np`），则总上下文长度会分配到各个任务槽中——例如在 `--c 64000 --np 4` 的配置下，每个任务槽仅能获得 16k 的上下文长度，这低于 Hermes 对单个活跃会话的最低要求。

随后需将 Hermes 配置为指向该值：

```bash
hermes model
# Select "Custom endpoint (self-hosted / VLLM / etc.)"
# Enter URL: http://localhost:8080/v1
# Skip API key (local servers don't need one)
# Enter model name — or leave blank to auto-detect if only one model is loaded
```

该操作会将端点保存到 `config.yaml` 文件中，从而确保其在不同会话之间保持不变。

:::caution 调用工具时必须使用 `--jinja` 参数
若未使用 `--jinja`，llama-server 会完全忽略 `tools` 参数。模型会试图在响应文本中写入 JSON 来调用工具，但 Hermes 无法将其识别为工具调用——您将看到类似 `{"name": "web_search", ...}` 的原始 JSON 内容被直接作为普通消息输出，而无法实现实际搜索功能。

原生工具调用支持（性能最佳）：Llama 3.x、Qwen 2.5（含 Coder 版本）、Hermes 2/3、Mistral、DeepSeek、Functionary。其他所有模型则使用通用处理机制，虽然也能正常工作，但效率可能稍低。完整列表请参阅 [llama.cpp 函数调用文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)。

您可以通过访问 `http://localhost:8080/props` 来确认工具调用功能是否已启用——该页面应包含 `chat_template` 字段。
:::

:::tip
您可以从 [Hugging Face](https://huggingface.co/models?library=gguf) 下载 GGUF 格式的模型。Q4_K_M 量化格式能在模型质量与内存占用之间实现最佳平衡。
:::

---

### LM Studio — 支持本地模型的桌面应用

[LM Studio](https://lmstudio.ai/) 是一款带有图形用户界面的桌面应用，可用于运行本地模型。非常适合：偏好可视化界面的用户、需要快速测试模型的用户，以及 macOS/Windows/Linux 系统上的开发者。

您可以通过 LM Studio 应用启动服务器（点击“开发者”选项卡 → “启动服务器”），或直接使用命令行工具：

```bash
lms server start                        # Starts on port 1234
lms load qwen2.5-coder --context-length 64000
```

接下来配置 Hermes：

```bash
hermes model
# Select "LM Studio"
# Press Enter to use http://localhost:1234/v1
# Pick one of the discovered models
# If LM Studio server auth is enabled, enter LM_API_KEY when prompted
```

Hermes 会保留已加载的 LM Studio 实例的上下文信息。对于处于默认显式模式且未被加载的模型，除非您在 Hermes 中进行了配置，否则 Hermes 会省略 `context_length` 参数，这样 LM Studio 就可以应用其自身的模型设置。随后，Hermes 仅会使用 LM Studio 加载完成后报告的上下文长度。

若要在 LM Studio 中更改上下文长度，请执行以下操作：

1. 点击模型选择器旁边的齿轮图标；
2. 为获得更流畅的体验，将“上下文长度”设置为至少 64000；
3. 重新加载模型以使更改生效；
4. 如果您的设备无法容纳 64000 的上下文长度，可考虑使用上下文长度更大的较小模型。

或者，您也可以通过 CLI 命令来实现：`lms load model-name --context-length 64000`

您还可以使用 CLI 命令来预估模型是否能够适应该设置：`lms load model-name --context-length 64000 --estimate-only`

如需为每个模型设置永久性默认值，请进入“我的模型”选项卡，点击对应模型的齿轮图标，然后设置上下文大小。
:::

如果您使用了 LM Studio 的即时加载/自动驱逐功能，并希望让 LM Studio 在常规聊天请求中自动管理模型的加载与卸载，那么可以跳过 Hermes 的显式预加载步骤：

```bash
hermes config set model.lmstudio_load_mode jit
```

可通过以下命令将其恢复为默认的显式预加载行为：

```bash
hermes config set model.lmstudio_load_mode explicit
```

**工具调用功能：** 自 LM Studio 0.3.6 版本起支持。经过原生工具调用训练的模型（如 Qwen 2.5、Llama 3.x、Mistral、Hermes）会自动被识别，并显示相应的工具标识。其他模型则需使用通用的备用方案，其可靠性可能较低。

---

### WSL2 网络配置（Windows 用户）

由于 Hermes Agent 需要 Unix 环境，Windows 用户需在 WSL2 中运行该代理。如果您的模型服务器（如 Ollama、LM Studio 等）运行在**Windows 主机**上，就需要建立网络连接——WSL2 使用带有独立子网的虚拟网络适配器，因此 WSL2 内部的 `localhost` 指的是 Linux 虚拟机，而非 Windows 主机。

:::提示：两者都在 WSL2 中？无需担心。
如果您的模型服务器也运行在 WSL2 中（vLLM、SGLang 和 llama-server 通常如此），则 `localhost` 可以正常使用——因为它们共享同一个网络命名空间。可直接跳过本节。
:::

#### 方案 1：镜像网络模式（推荐）

该功能适用于**Windows 11 22H2 及更高版本**。通过镜像模式，可以让 Windows 和 WSL2 之间的 `localhost` 实现双向通信——这是最简单的解决方案。

1. 创建或编辑 `%USERPROFILE%\.wslconfig` 文件（例如：`C:\Users\YourName\.wslconfig`）：
   ```ini
   [wsl2]
   networkingMode=mirrored
   ```

2. 通过 PowerShell 重启 WSL：
   ```powershell
   wsl --shutdown
   ```

3. 重新打开您的 WSL2 终端。此时，“localhost”即可访问 Windows 服务：
   ```bash
   curl http://localhost:11434/v1/models   # Ollama on Windows — works
   ```

:::note Hyper-V防火墙
在某些Windows 11版本中，Hyper-V防火墙默认会阻止镜像连接。如果在启用镜像模式后`localhost`仍然无法使用，请在**管理员权限的PowerShell**中运行以下命令：
```powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
```
:::

#### 方案 2：使用 Windows 主机 IP（Windows 10 及更早版本）

如果无法使用镜像模式，可在 WSL2 内部查找 Windows 主机 IP，并将其用于替代 `localhost`：

```bash
# Get the Windows host IP (the default gateway of WSL2's virtual network)
ip route show | grep -i default | awk '{ print $3 }'
# Example output: 172.29.192.1
```

在您的 Hermes 配置文件中使用该 IP 地址：

```yaml
model:
  default: qwen2.5-coder:32b
  provider: custom
  base_url: http://172.29.192.1:11434/v1   # Windows host IP, not localhost
```

:::提示 动态辅助工具  
在重启 WSL2 后，主机 IP 可能会发生变化。您可以在 Shell 中通过动态方式获取该 IP 地址：
```bash
export WSL_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
echo "Windows host at: $WSL_HOST"
curl http://$WSL_HOST:11434/v1/models   # Test Ollama
```

或者使用您机器的 mDNS 名称（在 WSL2 环境中需要安装 `libnss-mdns`）：
```bash
sudo apt install libnss-mdns
curl http://$(hostname).local:11434/v1/models
```
:::

#### 服务器绑定地址（NAT模式必需）

如果您选择**方案2**（使用主机IP的NAT模式），Windows上的模型服务器必须能够接收来自`127.0.0.1`之外的连接。默认情况下，大多数服务器仅监听本机地址——而NAT模式下的WSL2连接来自不同的虚拟子网，因此会被拒绝。在镜像模式下，`localhost`会直接映射，因此默认的`127.0.0.1`绑定方式可以正常使用。

| 服务器 | 默认绑定地址 | 解决方法 |
|--------|-------------|----------|
| **Ollama** | `127.0.0.1` | 在启动Ollama之前设置`OLLAMA_HOST=0.0.0.0`环境变量（Windows中可在“系统设置”→“环境变量”中进行设置，或直接编辑Ollama服务） |
| **LM Studio** | `127.0.0.1` | 在“开发者”选项卡→“服务器设置”中启用**“在网络上提供服务”**功能 |
| **llama-server** | `127.0.0.1` | 在启动命令中添加`--host 0.0.0.0`参数 |
| **vLLM** | `0.0.0.0` | 默认已绑定到所有网络接口 |
| **SGLang** | `127.0.0.1` | 在启动命令中添加`--host 0.0.0.0`参数 |

**Windows上的Ollama（详细说明）：** Ollama作为Windows服务运行。要设置`OLLAMA_HOST`：
1. 打开**系统属性**→**环境变量**
2. 添加一个新的**系统变量**：`OLLAMA_HOST` = `0.0.0.0`
3. 重启Ollama服务（或重新启动电脑）

#### Windows防火墙

无论处于NAT模式还是镜像模式，Windows防火墙都会将WSL2视为独立的网络。如果按照上述步骤操作后连接仍然失败，请为模型服务器的端口添加防火墙规则：

```powershell
# Run in Admin PowerShell — replace PORT with your server's port
New-NetFirewallRule -DisplayName "Allow WSL2 to Model Server" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
```

常用端口：Ollama为`11434`，vLLM为`8000`，SGLang为`30000`，llama-server为`8080`，LM Studio为`1234`。

#### 快速验证

在WSL2环境中，测试是否能连接到模型服务器：

```bash
# Replace URL with your server's address and port
curl http://localhost:11434/v1/models          # Mirrored mode
curl http://172.29.192.1:11434/v1/models       # NAT mode (use your actual host IP)
```

如果返回的响应是包含你所使用模型的 JSON 数据，那就说明一切正常。请将该 URL 作为 Hermes 配置中的 `base_url` 使用。

---

### 本地模型的故障排查

当与 Hermes 搭配使用时，以下问题会影响**所有**本地推理服务器。

#### WSL2 无法连接到 Windows 环境下的模型服务器，出现“连接被拒绝”错误

如果你在 WSL2 中运行 Hermes，而模型服务器位于 Windows 主机上，在 WSL2 的默认 NAT 网络模式下，`http://localhost:<port>` 这种地址格式将无法使用。请参考上文[WSL2 网络设置](#wsl2-networking-windows-users)了解解决方案。

#### 工具调用仅以文本形式出现，而未实际执行

模型会以消息形式输出类似 `{"name": "web_search", "arguments": {...}}` 的内容，而非真正调用对应工具。

**原因：** 你的服务器未开启工具调用功能，或者该模型通过服务器的工具调用实现机制不支持此功能。

| 服务器 | 解决方案 |
|--------|----------|
| **llama.cpp** | 在启动命令中添加 `--jinja` 参数 |
| **vLLM** | 添加 `--enable-auto-tool-choice --tool-call-parser hermes` 参数 |
| **SGLang** | 添加 `--tool-call-parser qwen`（或其他合适的解析器）参数 |
| **Ollama** | 工具调用功能默认已开启——请确保你的模型支持该功能（可通过 `ollama show model-name` 查验） |
| **LM Studio** | 升级到 0.3.6 及更高版本，并使用具备原生工具支持功能的模型 |

#### 模型似乎会遗忘上下文，或给出逻辑混乱的响应 |

**原因：** 上下文窗口过小。当对话内容超出上下文限制时，大多数服务器会默默丢弃较早的消息。仅Hermes的系统提示语和工具架构就可能需要4千到8千个标记空间。

**诊断方法：**

```bash
# Check what Hermes thinks the context is
# Look at startup line: "Context limit: X tokens"

# Check your server's actual context
# Ollama: ollama ps (CONTEXT column)
# llama.cpp: curl http://localhost:8080/props | jq '.default_generation_settings.n_ctx'
# vLLM: check --max-model-len in startup args
```

**解决方案：** 为智能体使用设置至少 **64,000 个标记** 的上下文长度。具体参数请参阅上文各服务器的相关说明。

#### 启动时出现“上下文限制：2048 个标记”的错误

Hermes 会自动从服务器的 `/v1/models` 接口获取上下文长度信息。如果服务器返回的值较低（或根本未返回），Hermes 将使用模型本身声明的限制值，而这很可能并不准确。

**解决方案：** 在 `config.yaml` 文件中明确指定该数值：

```yaml
model:
  default: your-model
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 64000
```

#### 响应在句子中间被截断

**可能原因：**
1. **服务器端的输出限制较低** —— 需调整服务器的默认生成参数（例如 SGLang 的 `--default-max-tokens`）。Hermes 并未提供输出token上限的配置选项。响应长度与对话的上下文窗口（`context_length`）是不同的概念。
2. **上下文耗尽** —— 模型已用满其上下文窗口。可增加 `model.context_length` 的值，或是在 Hermes 中启用[上下文压缩](/user-guide/configuration#context-compression)功能。

---

### LiteLLM Proxy — 多提供商网关

[LiteLLM](https://docs.litellm.ai/) 是一款兼容 OpenAI 的代理工具，能够将 100 多种大型语言模型提供商统一在单个 API 后面。其优势在于：无需修改配置即可在不同提供商之间切换、实现负载均衡、设置备用方案以及控制使用预算。

```bash
# Install and start
pip install "litellm[proxy]"
litellm --model anthropic/claude-sonnet-4 --port 4000

# Or with a config file for multiple models:
litellm --config litellm_config.yaml --port 4000
```

接着通过 `hermes model` → Custom endpoint → `http://localhost:4000/v1` 的方式来配置 Hermes。以下是一个包含备用端点的 `litellm_config.yaml` 示例：
```yaml
model_list:
  - model_name: "best"
    litellm_params:
      model: anthropic/claude-sonnet-4
      api_key: sk-ant-...
  - model_name: "best"
    litellm_params:
      model: openai/gpt-4o
      api_key: sk-...
router_settings:
  routing_strategy: "latency-based-routing"
```

### ClawRouter — 成本优化型路由方案

BlockRunAI 开发的 [ClawRouter](https://github.com/BlockRunAI/ClawRouter) 是一款本地路由代理工具，能够根据查询的复杂度自动选择合适的模型。它通过 14 个维度对请求进行分类，并将请求路由至最能高效处理该任务的低成本模型。该服务采用 USDC 加密货币进行支付，无需 API 密钥。

```bash
# Install and start
npx @blockrun/clawrouter    # Starts on port 8402
```

接着通过 `hermes model` → Custom endpoint → `http://localhost:8402/v1` 的步骤配置 Hermes，模型名称设为 `blockrun/auto`。

路由配置文件：
| 配置文件 | 策略 | 节省比例 |
|---------|--------|----------|
| `blockrun/auto` | 平衡质量与成本 | 74-100% |
| `blockrun/eco` | 尽可能降低成本 | 95-100% |
| `blockrun/premium` | 最优质的模型 | 0% |
| `blockrun/free` | 仅使用免费模型 | 100% |
| `blockrun/agentic` | 针对工具使用优化 | 不固定 |

:::note
ClawRouter 需要在 Base 或 Solana 网络上拥有一个存储 USDC 的钱包用于支付。所有请求均通过 BlockRun 的后端 API 进行路由。可运行 `npx @blockrun/clawrouter doctor` 命令来检查钱包状态。
:::

---

### 其他兼容的提供商

任何具备 OpenAI 兼容 API 的服务均可使用。以下是一些常见的选择：

| 提供商 | 基础 URL | 备注 |
|--------|----------|------|
| [Together AI](https://together.ai) | `https://api.together.xyz/v1` | 云端托管的开放模型 |
| [Groq](https://groq.com) | `https://api.groq.com/openai/v1` | 极速推理性能 |
| [DeepSeek](https://deepseek.com) | `https://api.deepseek.com/v1` | DeepSeek 模型 |
| [Fireworks AI](https://fireworks.ai) | `https://api.fireworks.ai/inference/v1` | 快速的开放模型托管服务 |
| [GMI Cloud](https://www.gmicloud.ai/) | `https://api.gmi-serving.com/v1` | 可管理、兼容 OpenAI 的推理服务 |
| [Actual Computer](https://actual.inc) | `https://api.actual.inc/v1` | 连接到您自有集群的私有中继；本地守护进程地址为 `http://127.0.0.1:8080/v1` |
| [Cerebras](https://cerebras.ai) | `https://api.cerebras.ai/v1` | 瓷片级芯片推理技术 |
| [Mistral AI](https://mistral.ai) | `https://api.mistral.ai/v1` | Mistral 模型 |
| [OpenAI](https://openai.com) | `https://api.openai.com/v1` | 直接访问 OpenAI 平台 |
| [Azure OpenAI](https://azure.microsoft.com) | `https://YOUR.openai.azure.com/` | 企业级 OpenAI 服务 |
| [LocalAI](https://localai.io) | `http://localhost:8080/v1` | 自主托管的多模型系统 |
| [Jan](https://jan.ai) | `http://localhost:1337/v1` | 支持本地模型的桌面应用 |

您可以通过 `hermes model` → Custom endpoint 命令，或直接在 `config.yaml` 文件中配置上述任意提供商的参数。

```yaml
model:
  default: meta-llama/Llama-3.1-70B-Instruct-Turbo
  provider: custom
  base_url: https://api.together.xyz/v1
  api_key: your-together-key
```

### 上下文长度检测

:::note 上下文窗口与输出限制是不同的概念  
**`context_length`** 指的是**总上下文窗口大小**，即输入 token 与输出 token 的总量上限（例如 Claude Opus 4.6 的上限为 200,000）。Hermes 会依据这一数值来决定何时压缩对话历史记录，以及如何验证 API 请求的合法性。  

输出限制仅适用于单次生成的响应，而不涉及整个对话历史。  
Hermes 已不再读取 `model.max_tokens`、`HERMES_MAX_TOKENS`、提供商设定的输出上限参数，或是 `model_overrides.*.*.max_output_tokens` 这些旧版设置。建议将其移除。  

对于兼容 OpenAI 的自定义端点，系统不会自动施加与官方目录相同的输出上限限制，而是遵循该端点服务器的默认设置——这些默认值可能低于模型本身的最大输出限制。  

对于原生 Anthropic 消息格式（包括原生 Anthropic Bedrock 协议），需要指定 `max_tokens` 参数，因此 Hermes 会为其提供内部预设值。而 Bedrock Converse 采用独立的协议规范：其可选的 `inferenceConfig.maxTokens` 参数默认会被省略，[AWS 文档将其视为模型的最大输出限制](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InferenceConfiguration.html)。至于内置的有限任务处理机制以及特定提供商的协议要求，则属于实现细节，省略该参数并不一定意味着采用模型的最大输出限制。  

当自动检测结果出现误差时，可手动设置 `context_length` 值。  

:::  

Hermes 会通过多源解析机制，来准确确定您的模型及所使用提供商对应的正确上下文窗口大小：

1. **配置覆盖** — 通过 config.yaml 中的 `model.context_length` 设置（优先级最高）  
2. **按模型定制提供商设置** — 使用 `providers.<名称>.models.<ID>.context_length`  
3. **持久化缓存** — 之前已检测到的数值会保留（重启后依然有效）  
4. **/models 接口** — 调用服务器的 API（支持本地或自定义接口）  
5. **Anthropic 的 /v1/models 接口** — 通过 Anthropic 的 API 查询 `max_input_tokens` 值（仅限拥有 API 密钥的用户使用）  
6. **OpenRouter API** — 获取来自 OpenRouter 的实时模型元数据  
7. **Nous Portal** — 根据模型 ID 的后缀与 OpenRouter 的元数据进行匹配  
8. **[models.dev](https://models.dev)** — 由社区维护的注册平台，收录了 100 多家提供商提供的 3800 多种模型的特定上下文长度信息  
9. **默认回退值** — 根据模型类别自动设定通用值（默认为 128K）  

在大多数配置下，系统可直接正常使用。该系统具备提供商识别功能——同一模型在不同提供商处可能会有不同的上下文长度限制（例如，`claude-opus-4.6` 在 Anthropic 官方平台上的上下文长度为 100 万token，而在 GitHub Copilot 上则为 128K）。  

如需明确指定上下文长度，可在模型配置中添加 `context_length` 参数。

```yaml
model:
  default: "qwen3.5:9b"
  base_url: "http://localhost:8080/v1"
  context_length: 131072  # tokens
```

对于自定义端点，您还可以为每个模型设置上下文长度限制：

```yaml
providers:
  my-local-llm:
    api: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 64000
      deepseek-r1:70b:
        context_length: 65536
```

在配置自定义端点时，`hermes model` 会提示输入上下文长度。若留空，则系统将自动检测。

:::提示：何时需要手动设置该值
- 您使用的是 Ollama，且其自定义的 `num_ctx` 值低于模型支持的最大值
- 您希望将上下文长度限制在模型最大值之下（例如，为节省显存，将 128k 容量的模型限制在 8k）
- 您的运行环境位于不公开 `/v1/models` 接口的代理服务器后端

:::

---

### 带名称的自定义提供者

如果您需要使用多个自定义端点（例如本地开发服务器和远程 GPU 服务器），可以在 `config.yaml` 文件的 `providers:` 字典中，按照提供者名称为键来定义这些带名称的自定义提供者：

```yaml
providers:
  local:
    api: http://localhost:8080/v1
    # api_key omitted — Hermes uses "no-key-required" for keyless local servers
  work:
    api: https://gpu-server.internal.corp/v1
    key_env: CORP_API_KEY
    transport: chat_completions   # set explicitly by `hermes model` → Custom Endpoint wizard; auto-detection still happens as a fallback
  anthropic-proxy:
    api: https://proxy.example.com/anthropic
    key_env: ANTHROPIC_PROXY_KEY
    transport: anthropic_messages  # for Anthropic-compatible proxies
```

每个条目可包含以下参数：`api`（端点基础URL，`base_url`/`url`也是其别名）、`name`（可选的显示名称；默认为字典键名）、`key_env`或内联的`api_key`/`key_cmd`（详见下文）、`transport`（`chat_completions` / `anthropic_messages` / `codex_responses`）、`default_model`、`models`、`context_length`、`discover_models`、`extra_body`、`extra_headers`、`ssl_ca_cert`/`ssl_verify`，以及用于在不删除条目的情况下将其隐藏的`enabled: false`。

#### 通过命令生成的凭证（`key_cmd`）

视觉处理、思维能力检测以及本地模型功能检测在构建认证请求头之前，会使用与聊天功能相同的可调用凭证。这些功能会复用命令令牌缓存，而不会替换聊天客户端中的可调用对象。如果某个命令无法生成字符串形式的令牌，这些“尽力而为”的检测机制将不会发送任何令牌，而非使用对象表示形式或优先级较低的已配置凭证。对于本地模型检测，在显式调用的操作失败时，它会移除继承来的Authorization头，但会保留其他无关的已配置请求头。聊天功能则保持其常规的错误处理机制。

企业网关通常会生成短期有效的令牌（如SSO/OIDC代理、云IAM服务、内部认证代理），而非静态API密钥。因此，若将此类令牌复制到`.env`文件中，其在会话进行到一半时就会失效，从而导致请求返回401错误。`key_cmd`用于指定一个用于*打印*令牌的命令；Hermes会执行该命令并将结果缓存起来，直到令牌即将过期前，这样长时运行的会话便无需重启即可继续正常工作。

```yaml
providers:
  my-gateway:
    base_url: "https://gateway.internal.example.com/v1"
    api_mode: chat_completions
    key_cmd: "my-auth-cli print-token --profile prod"
```

该功能可与任何能够输出令牌的辅助工具配合使用，包括 `databricks auth token`、`gcloud auth print-access-token`、`az account get-access-token`、`vault read`，以及 Claude Code 风格的 `apiKeyHelper` 脚本。

此类命令必须**仅**在标准输出中打印令牌——既可以是原始格式，也可以是包含 `access_token` 字段的 JSON 格式（系统会识别 `expires_in` 参数，同时也会接受绝对的 ISO 时间戳格式 `expiry`/`expiresOn`）。系统不会尝试猜测多行输出的内容，而是直接拒绝此类输入。如果未指定令牌有效期，则会在设定的时间窗口内重新生成令牌。

优先级规则为：显式的 `--api-key` 参数始终具有最高优先级；否则，在同一配置项中，`key_cmd` 的优先级高于静态的 `api_key`/`key_env` 设置。所生成的凭证既适用于主代理的当前任务，也适用于各类辅助任务（如标题生成、压缩、图像处理、嵌入功能等）。

在模型发现功能中，无论是 `providers:` 配置项还是传统的 `custom_providers:` 配置项，包括 `hermes model` 设置，都会优先遵循 `key_cmd` 的指定。辅助工具仅在实际需要通过已认证的实时目录探针进行查询时才会被启动：关闭发现功能或读取热缓存时不会生成令牌。目录的权限范围与命令执行身份绑定，因此更换令牌持有者并不会使目录失效。探针辅助工具会使用自己短期的令牌源，而非推理客户端的令牌缓存；生成的令牌绝不会被保存到 `config.yaml` 文件中。如果某个辅助工具出现故障，系统会回退到已配置的模型，而不会显示该辅助工具的输出结果。

请注意，它与 `secrets.command` 不同——后者仅在启动时运行一次辅助功能，用于为整个进程设置环境变量。若需使用密钥库助手来返回多个机密信息，请选用该选项；而当需要在会话进行过程中重新生成某个提供者的凭证时，则应使用 `key_cmd`。

:::note 旧格式说明
早期的配置文件会使用顶层的 `custom_providers:` 列表来实现相同功能。这种格式依然有效——Hermes 可以识别两种格式——并且 `hermes update` 命令会自动将其迁移为 `providers:` 字典格式（配置版本 v12）。在字典格式中，字段名称略有不同：旧格式中的 `model` 对应 `default_model`，旧格式中的 `api_mode` 对应 `transport`。
:::

某些兼容 OpenAI 的接口需要特定提供者所要求的请求体字段。只需在对应的自定义提供者中添加一个 `extra_body` 映射表，Hermes 就会将其合并到该接口的每个聊天完成请求中：

```yaml
providers:
  gemma-local:
    api: http://localhost:8080/v1
    default_model: google/gemma-4-31b-it
    extra_body:
      enable_thinking: true
      reasoning_effort: high
```

请使用与您的服务器文档中规定的格式一致。例如，vLLM Gemma部署环境以及某些NVIDIA NIM端点要求在`chat_template_kwargs`下设置`enable_thinking`参数，而非将其作为顶层的`extra_body`字段。

```yaml
extra_body:
  chat_template_kwargs:
    enable_thinking: true
```

对于由 vLLM 提供服务的 Qwen 推理模型，当推理解析器将所有生成的文本分离到推理字段中，并使助手的 `content` 字段保持为空时，同样可以使用这种格式来禁用思考功能。

```yaml
extra_body:
  chat_template_kwargs:
    enable_thinking: false
```

配置好的 `extra_body` 会伴随整个请求流程：它在智能体构建阶段就会被合并进去，**能够穿越每一个网关节点**（即便在某些节点上使用了 `/fast` 层的 `service_tier`/`speed` 覆盖规则——这类规则会与您的 `extra_body` 合并而非直接替换它）；同时，在切换 `/model` 时也会重新生成该内容——切换到指定的自定义提供方时，其对应的 `extra_body` 会被应用，而切换离开则会清除该内容，从而避免其泄露到其他提供方。

现在的 “Hermes 模型” → “自定义端点” 向导会明确询问 API 模式，并将您的选择保存到 `config.yaml` 文件中（以提供方条目中的 `transport` 字段形式存储）。如果未填写该字段，系统仍会以基于 URL 的自动检测作为备用方案（例如，以 `/anthropic` 开头的路径会被识别为 `anthropic_messages` 格式）。

**针对自定义提供方模型的原生视觉处理功能。** 如果您的自定义端点用于调用 models.dev 上未收录的具备视觉处理能力的模型，请将 `model.supports_vision: true` 设为 true，这样 Hermes 就能直接将附带的图像作为 `image_url` 部分进行传输，而无需先通过 `vision_analyze` 进行预处理。只需设置这一个参数即可，无需再额外设置 `agent.image_input_mode: native`。

```yaml
model:
  provider: custom
  base_url: http://localhost:8080/v1
  default: qwen3.6-35b-a3b
  supports_vision: true   # send images natively; otherwise vision_analyze pre-describes them
```

在按提供者命名的模型中（即 `providers.<name>.models.<id>.supports_vision`），该键的规则同样适用，且支持标准的 YAML 布尔值格式（`true/false/yes/no/on/off/1/0`）。

您可以通过三重语法在会话进行过程中切换不同的配置模式：

```
/model custom:local:qwen-2.5       # Use the "local" endpoint with qwen-2.5
/model custom:work:llama3-70b      # Use the "work" endpoint with llama3-70b
/model custom:anthropic-proxy:claude-sonnet-4  # Use the proxy
```

您还可以从交互式的 `hermes model` 菜单中选择已命名的自定义服务提供商。

---

### 实用指南：Together AI、Groq、Perplexity

[其他兼容服务提供商](#other-compatible-providers)中列出的云服务提供商均支持 OpenAI 的 REST 接口规范，因此在 `providers:` 字典中的配置方式完全一致。以下是三种经过验证的有效配置方案。只需将相关配置内容添加到 `~/.hermes/config.yaml` 文件中，再将对应的 API 密钥放入 `~/.hermes/.env` 文件即可。

#### Together AI

该平台提供开源模型（如 Llama、MiniMax、Gemma、DeepSeek、Qwen），其使用成本远低于官方 API。是构建多模型系统的理想默认选择。

```yaml
# ~/.hermes/config.yaml
providers:
  together:
    api: https://api.together.xyz/v1
    key_env: TOGETHER_API_KEY
    # transport: chat_completions  # default — no need to set

model:
  default: MiniMaxAI/MiniMax-M2.7   # or any model from together.ai/models
  provider: custom:together
```

```bash
# ~/.hermes/.env
TOGETHER_API_KEY=your-together-key
```

在会话进行中切换模型：

```
/model custom:together:meta-llama/Llama-3.3-70B-Instruct-Turbo
/model custom:together:google/gemma-4-31b-it
/model custom:together:deepseek-ai/DeepSeek-V3
```

Together提供的`/v1/models`接口功能正常，因此`hermes model`能够自动发现可用的模型。

#### Groq

具备极快的推理速度（在Llama-3.3-70B模型上可达约500个token/秒）。虽然模型库规模较小，但非常适合对延迟敏感的交互式应用场景。

```yaml
# ~/.hermes/config.yaml
providers:
  groq:
    api: https://api.groq.com/openai/v1
    key_env: GROQ_API_KEY

model:
  default: llama-3.3-70b-versatile
  provider: custom:groq
```

```bash
# ~/.hermes/.env
GROQ_API_KEY=your-groq-key
```

#### Perplexity

当您需要一个能够自动进行实时网络搜索并标注引用来源的模型时，该服务非常实用。其支持的模型列表有严格限制——请访问 [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) 查看当前可用的模型列表。

```yaml
# ~/.hermes/config.yaml
providers:
  perplexity:
    api: https://api.perplexity.ai
    key_env: PERPLEXITY_API_KEY

model:
  default: sonar
  provider: custom:perplexity
```

```bash
# ~/.hermes/.env
PERPLEXITY_API_KEY=your-perplexity-key
```

#### 在单个配置中使用多个提供者

这三个配方可组合使用——将它们全部一同启用，并通过 `/model custom:<名称>:<模型>` 每轮切换不同的模型：

```yaml
providers:
  together:
    api: https://api.together.xyz/v1
    key_env: TOGETHER_API_KEY
  groq:
    api: https://api.groq.com/openai/v1
    key_env: GROQ_API_KEY
  perplexity:
    api: https://api.perplexity.ai
    key_env: PERPLEXITY_API_KEY

model:
  default: MiniMaxAI/MiniMax-M2.7
  provider: custom:together      # boot to Together; switch freely after
```

:::提示 故障排除
- 在 #15083 号补丁完成 CLI 验证器优化后，使用 `hermes doctor` 检查时，针对上述任意提供商名称均不应出现“未知提供商”的警告信息。
- 若某个提供商的 `/v1/models` 接口无法访问（Perplexity 是常见案例），`hermes model` 命令会发出警告并保留该模型，而不会直接拒绝——详情参见 #15136。
- 如需完全跳过指定提供商，直接使用 `provider: custom` 并结合 `CUSTOM_BASE_URL` 环境变量，可参考 #15103。
:::

---

### 选择合适的设置方案

| 使用场景 | 推荐方案 |
|----------|----------|
| **仅需功能正常运行** | OpenRouter（默认）或 Nous Portal |
| **本地模型，部署简单** | Ollama |
| **生产环境 GPU 服务** | vLLM 或 SGLang |
| **Mac 电脑/无 GPU 环境** | Ollama 或 llama.cpp |
| **多提供商路由** | LiteLLM Proxy 或 OpenRouter |
| **成本优化** | ClawRouter 或配置了 `sort: "price"` 参数的 OpenRouter |
| **最高隐私保护** | Ollama、vLLM 或 llama.cpp（完全本地运行） |
| **企业环境/Azure 平台** | 配置了自定义端点的 Azure OpenAI |
| **中文 AI 模型** | z.ai（GLM）、Kimi/Moonshot（`kimi-coding` 或 `kimi-coding-cn`）、MiniMax、小米 MiMo，或腾讯 TokenHub（优质提供商） |

:::提示
您可以通过 `hermes model` 命令随时切换使用的提供商，无需重启系统。无论使用哪种提供商，您的对话历史、上下文记忆及技能信息都会保持不变。
:::

## 可选 API 密钥

| 功能 | 提供方 | 环境变量 |
|---------|--------|----------|
| 网页抓取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`, `FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级文本转语音音色 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI 文本转语音及语音转写功能 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| Mistral 文本转语音及语音转写功能 | [Mistral](https://console.mistral.ai/) | `MISTRAL_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |
| 语义长期记忆功能 | [Supermemory](https://supermemory.ai) | `SUPERMEMORY_API_KEY` |

### 自主托管 Firecrawl

默认情况下，Hermes 会使用 [Firecrawl 云 API](https://firecrawl.dev/) 来进行网页搜索和抓取操作。如果您希望在本地运行 Firecrawl，也可以让 Hermes 连接到自托管的实例。完整的设置指南请参阅 Firecrawl 的 [SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) 文档。

**优势：** 无需 API 密钥，无速率限制，无每页费用，数据完全由您掌控。

**会失去的功能：** 云版本采用 Firecrawl 的专有“Fire-engine”技术，能够实现更强大的反机器人检测绕过功能（可应对 Cloudflare、验证码及 IP 轮换等防护）。而自托管版本仅使用基础的 fetch 请求与 Playwright 工具，因此可能无法访问某些受保护的网站。此外，搜索功能将使用 DuckDuckGo 而非 Google。

**设置步骤：**

1. 克隆并启动 Firecrawl Docker 集群（包含 5 个容器：API、Playwright、Redis、RabbitMQ、PostgreSQL——需约 4-8 GB 内存）：
   ```bash
   git clone https://github.com/firecrawl/firecrawl
   cd firecrawl
   # In .env, set: USE_DB_AUTHENTICATION=false, HOST=0.0.0.0, PORT=3002
   docker compose up -d
   ```

2. 将 Hermes 指向您的实例（无需 API 密钥）：
   ```bash
   hermes config set FIRECRAWL_API_URL http://localhost:3002
   ```

如果您的自托管实例启用了身份验证功能，您还可以同时设置 `FIRECRAWL_API_KEY` 和 `FIRECRAWL_API_URL`。

## OpenRouter 提供商路由功能

在使用 OpenRouter 时，您可以控制请求在各个提供商之间的路由方式。只需在 `~/.hermes/config.yaml` 文件中添加 `provider_routing` 部分即可：

```yaml
provider_routing:
  sort: "throughput"          # "price" (default), "throughput", or "latency"
  # only: ["anthropic"]      # Only use these providers
  # ignore: ["deepinfra"]    # Skip these providers
  # order: ["anthropic", "google"]  # Try providers in this order
  # require_parameters: true  # Only use providers that support all request params
  # data_collection: "deny"   # Exclude providers that may store/train on data
  # models:                   # Per-model pins (same keys; unset keys fall through)
  #   "openai/gpt-6-astra": {only: ["openai"]}
  #   "anthropic/claude-fable-5.1": {only: ["anthropic"]}
```

**快捷指令：** 在任意模型名称后添加 `:nitro` 即可按吞吐量进行排序（例如 `anthropic/claude-sonnet-4:nitro`），添加 `:floor` 则可按价格排序。各模型的详细信息请参阅：[Provider Routing](/user-guide/features/provider-routing#per-model-overrides-models)。

## OpenRouter Pareto Code Router

OpenRouter 提供了一个名为 `openrouter/pareto-code` 的实验性编程模型路由器，它能自动将请求路由至符合编程质量标准且价格最低的模型（该质量标准由 [Artificial Analysis](https://artificialanalysis.ai/) 打分）。选择该模型后，只需在 `~/.hermes/config.yaml` 文件中调整 `min_coding_score` 参数即可：

```yaml
model:
  provider: openrouter
  model: openrouter/pareto-code

openrouter:
  min_coding_score: 0.65   # 0.0–1.0; higher = stronger (more expensive) coders. Default 0.65.
```

备注：

- 仅当 `model.model` 的值为 `openrouter/pareto-code` 时，才会发送 `min_coding_score`。对于其他模型，该参数将不起任何作用。
- 若将其设置为空字符串（或删除该行），则由 OpenRouter 自动选择性能最强的编码器——这是在未指定插件列表时的默认行为。
- 在特定日期内，选择结果会根据评分呈确定性，但随着帕累托前沿的变化（新模型的出现、基准测试的更新），实际选用的模型也可能会改变。
- 如需了解路由器的完整行为，请参阅 OpenRouter 的 [Pareto Router 文档](https://openrouter.ai/docs/guides/routing/routers/pareto-router)。
- 若希望将 Pareto Code 路由器用于特定的**辅助任务**（如压缩、图像处理等），而非作为主代理使用，可在相应任务下设置 `extra_body.plugins`——详情请参见 [辅助模型 → OpenRouter 路由及用于辅助任务的 Pareto Code](/user-guide/configuration#openrouter-routing--pareto-code-for-auxiliary-tasks)。

## 备用提供者

当主模型出现故障（如速率限制、服务器错误、认证失败）时，可配置一系列备用提供者，Hermes 会按顺序尝试这些提供者。标准的配置格式是在顶层设置 `fallback_providers:` 列表：

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
  - provider: anthropic
    model: claude-sonnet-4
    # base_url: http://localhost:8000/v1    # optional, for custom endpoints
    # api_mode: chat_completions           # optional override
```

为保持向后兼容，旧式的单对键 `fallback_model:` 字典仍被支持。

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

启用该功能后，Fallback机制会在会话进行过程中动态切换模型与服务提供商，而不会导致当前对话丢失。系统会按顺序逐一尝试不同的链式配置；每个会话中仅可触发一次激活操作。

支持的提供商包括：`openrouter`、`nous`、`novita`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`qwen-oauth`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`bedrock`、`ai-gateway`、`azure-foundry`、`opencode-zen`、`opencode-go`、`commandcode`、`commandcode-anthropic`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`actual`、`stepfun`、`lmstudio`、`alibaba`、`alibaba-coding-plan`、`tencent-tokenhub`、`tencent-tokenplan`、`nebius-token-factory`、`router`以及`custom`。

:::提示
Fallback功能的配置仅能通过`config.yaml`文件完成，也可通过`hermes fallback`命令以交互方式设置。如需详细了解其触发条件、链式处理的流程，以及其与辅助任务和委托机制的交互方式，请参阅[Fallback Providers](/user-guide/features/fallback-providers)文档。
:::

---

## 相关内容

- [配置](/user-guide/configuration) —— 基本配置说明（目录结构、配置优先级、终端后端、内存设置、压缩功能等）
- [环境变量](/reference/environment-variables) —— 所有环境变量的完整参考列表
