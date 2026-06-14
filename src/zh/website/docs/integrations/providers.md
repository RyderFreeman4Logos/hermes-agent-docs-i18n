---
title: "AI Providers"
sidebar_label: "AI Providers"
sidebar_position: 1
---

# AI 提供商

本页面介绍了如何为 Hermes Agent 配置推理供应商——涵盖从 OpenRouter 和 Anthropic 等云 API，到 Ollama 和 vLLM 等自托管端点，以及高级路由与回退配置等内容。要使用 Hermes，至少需要配置一个供应商。

## 推理供应商

您至少需要一种方式来连接大型语言模型。可以通过 `hermes model` 功能交互式地切换供应商和模型，也可以直接进行配置：

| 供应商 | 配置方式 |
|--------|----------|
| **Nous Portal** | 使用 `hermes model`（基于 OAuth，需订阅服务） |
| **OpenAI Codex** | 使用 `hermes model`（通过 ChatGPT OAuth 访问，使用 Codex 模型） |
| **GitHub Copilot** | 使用 `hermes model`（通过 OAuth 设备代码流程，需提供 `COPILOT_GITHUB_TOKEN`、`GH_TOKEN` 或 `gh auth token`） |
| **GitHub Copilot ACP** | 使用 `hermes model`（会在本地启动 `copilot --acp --stdio`） |
| **Anthropic** | 使用 `hermes model`（Claude Max 模型，可通过 OAuth 获取额外使用额度；也支持使用 Anthropic API 密钥或手动设置的令牌——详见下方说明） |
| **OpenRouter** | 在 `~/.hermes/.env` 文件中设置 `OPENROUTER_API_KEY` |
| **NovitaAI** | 在 `~/.hermes/.env` 文件中设置 `NOVITA_API_KEY`（供应商名称为 `novita`，提供 200 多种模型，还支持 Model API、Agent Sandbox 和 GPU Cloud 功能） |
| **z.ai / GLM** | 在 `~/.hermes/.env` 文件中设置 `GLM_API_KEY`（供应商名称为 `zai`） |
| **Kimi / Moonshot** | 在 `~/.hermes/.env` 文件中设置 `KIMI_API_KEY`（供应商名称为 `kimi-coding`） |
| **Kimi / Moonshot（中国版）** | 在 `~/.hermes/.env` 文件中设置 `KIMI_CN_API_KEY`（供应商名称为 `kimi-coding-cn`；别名包括 `kimi-cn`、`moonshot-cn`） |
| **Arcee AI** | 在 `~/.hermes/.env` 文件中设置 `ARCEEAI_API_KEY`（供应商名称为 `arcee`；别名包括 `arcee-ai`、`arceeai`） |
| **GMI Cloud** | 在 `~/.hermes/.env` 文件中设置 `GMI_API_KEY`（供应商名称为 `gmi`；别名包括 `gmi-cloud`、`gmicloud`） |
| **MiniMax** | 在 `~/.hermes/.env` 文件中设置 `MINIMAX_API_KEY`（供应商名称为 `minimax`） |
| **MiniMax 中国版** | 在 `~/.hermes/.env` 文件中设置 `MINIMAX_CN_API_KEY`（供应商名称为 `minimax-cn`） |
| **xAI (Grok) — Responses API** | 在 `~/.hermes/.env` 文件中设置 `XAI_API_KEY`（供应商名称为 `xai`） |
| **xAI Grok OAuth (SuperGrok)** | 通过 `hermes model` 选择“xAI Grok OAuth (SuperGrok / Premium+)”选项，使用浏览器登录，无需 API 密钥。详情请参阅 [指南](../guides/xai-grok-oauth.md) |
| **Qwen Cloud（阿里达斯 Scope）** | 在 `~/.hermes/.env` 文件中设置 `DASHSCOPE_API_KEY`（供应商名称为 `alibaba`） |
| **阿里云（编程套餐）** | 需设置 `DASHSCOPE_API_KEY`（供应商名称为 `alibaba-coding-plan`，别名为 `alibaba_coding`）——该套餐有独立的计费方式，使用不同的端点 |
| **Kilo Code** | 在 `~/.hermes/.env` 文件中设置 `KILOCODE_API_KEY`（供应商名称为 `kilocode`） |
| **小米 MiMo** | 在 `~/.hermes/.env` 文件中设置 `XIAOMI_API_KEY`（供应商名称为 `xiaomi`；别名包括 `mimo`、`xiaomi-mimo`） |
| **腾讯 TokenHub** | 在 `~/.hermes/.env` 文件中设置 `TOKENHUB_API_KEY`（供应商名称为 `tencent-tokenhub`；别名包括 `tencent`、`tokenhub`、`tencentmaas`） |
| **OpenCode Zen** | 在 `~/.hermes/.env` 文件中设置 `OPENCODE_ZEN_API_KEY`（供应商名称为 `opencode-zen`） |
| **OpenCode Go** | 在 `~/.hermes/.env` 文件中设置 `OPENCODE_GO_API_KEY`（供应商名称为 `opencode-go`） |
| **DeepSeek** | 在 `~/.hermes/.env` 文件中设置 `DEEPSEEK_API_KEY`（供应商名称为 `deepseek`） |
| **Hugging Face** | 在 `~/.hermes/.env` 文件中设置 `HF_TOKEN`（供应商名称为 `huggingface`；别名包括 `hf`） |
| **Google / Gemini** | 在 `~/.hermes/.env` 文件中设置 `GOOGLE_API_KEY`（或 `GEMINI_API_KEY`）（供应商名称为 `gemini`） |
| **Google Gemini（OAuth 方式）** | 通过 `hermes model` 选择“Google Gemini (OAuth)”选项（供应商名称为 `google-gemini-cli`，支持免费套餐，通过浏览器 PKCE 方式登录） |
| **OpenAI API（直接连接）** | 在 `~/.hermes/.env` 文件中设置 `OPENAI_API_KEY`（供应商名称为 `openai-api`，可可选地设置 `OPENAI_BASE_URL`） |
| **Azure AI Foundry** | 通过 `hermes model` 选择“Azure AI Foundry”选项（供应商名称为 `azure-foundry`；使用 Azure OpenAI / Foundry 的端点及密钥） |
| **AWS Bedrock** | 通过 `hermes model` 选择“AWS Bedrock”选项（供应商名称为 `bedrock`；通过 boto3 使用标准的 AWS 凭证链） |
| **NVIDIA Build** | 在 `~/.hermes/.env` 文件中设置 `NVIDIA_API_KEY`（供应商名称为 `nvidia`；在 build.nvidia.com 上托管 NIM 模型） |
| **Ollama Cloud** | 通过 `hermes model` 选择“Ollama Cloud”选项（供应商名称为 `ollama-cloud`；使用云端托管的 Ollama API） |
| **Qwen OAuth** | 通过 `hermes model` 选择“Qwen OAuth”选项（供应商名称为 `qwen-oauth`；通过浏览器 PKCE 方式登录） |
| **MiniMax OAuth** | 通过 `hermes model` 选择“MiniMax (OAuth)”选项（供应商名称为 `minimax-oauth`；通过浏览器 PKCE 方式登录） |
| **StepFun** | 在 `~/.hermes/.env` 文件中设置 `STEPFUN_API_KEY`（供应商名称为 `stepfun`） |
| **LM Studio** | 通过 `hermes model` 选择“LM Studio”选项（供应商名称为 `lmstudio`；可可选地设置 `LM_API_KEY`） |
| **自定义端点** | 通过 `hermes model` 选择“Custom endpoint”选项（相关配置保存在 `config.yaml` 文件中） |

关于官方 API 密钥的设置路径，可参阅专门的 [Google Gemini 指南](/guides/google-gemini)。

:::提示 模型密钥别名
在 `model:` 配置部分，您可以使用 `default:` 或 `model:` 作为模型 ID 的键名。`model: { default: my-model }` 和 `model: { model: my-model }` 的效果是完全相同的。
:::

### Nous Portal

[Nous Portal](https://portal.nousresearch.com) 是 Nous Research 提供的统一订阅门户，也是**运行 Hermes Agent 的推荐方式**。通过一次 OAuth 登录，即可使用 300 多种前沿智能体模型（如 Claude、GPT、Gemini、DeepSeek、Qwen、Kimi、GLM、MiniMax、Grok 等），同时还能使用 [Tool Gateway](/user-guide/features/tool-gateway)（支持网页搜索、图像生成、文本转语音、浏览器自动化功能）以及 [Nous Chat](https://chat.nousresearch.com)——所有服务均通过您的 Nous 订阅账户计费，无需为每个供应商单独开户。

```bash
hermes setup --portal     # fresh install — OAuth + provider + gateway in one command
hermes model              # existing install — pick "Nous Portal" from the list
hermes portal info        # inspect login + routing at any time
```

尚未订阅？请访问 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription) 进行订阅。

**详细信息请参阅：** 专门的 [Nous Portal集成页面](/integrations/nous-portal)（包含订阅内容、模型目录及故障排除指南），以及分步指导的 [使用Nous Portal运行Hermes Agent指南](/guides/run-hermes-with-nous-portal)。

**客户端标识。** Hermes Agent发出的所有Portal请求都会自动携带`client=hermes-client-v<版本号>`标签（例如`client=hermes-client-v0.13.0`），该版本号与您安装的版本保持一致。此标签会出现在所有Portal交互路径中——包括主聊天循环、辅助调用、压缩摘要生成以及网页提取功能——从而帮助Portal端的监控系统区分Hermes的请求与其他客户端。无需任何配置，当您执行`hermes update`命令时，该标签会自动更新。

**JWT认证（自动处理）。** Hermes优先使用带作用域的`inference:invoke`类型JWT处理Portal请求，若使用旧式的不可见会话密钥路径，则作为备用方案。无需额外配置——凭据由OAuth流程统一管理，并会自动轮换。已被撤销的刷新令牌会被隔离，以防止重复使用导致的循环问题。

:::info Codex说明
OpenAI Codex提供端通过设备码进行认证（需打开指定网址并输入验证码）。Hermes会将生成的凭据存储在`~/.hermes/auth.json`路径下的专属认证存储中；如果存在来自`~/.codex/auth.json`的现有Codex CLI凭据，Hermes也会自动导入。无需安装Codex CLI。

如果令牌刷新过程中出现终端错误（如HTTP 4xx错误、`invalid_grant`、授权已被撤销等），Hermes会将该刷新令牌标记为无效，并停止重复使用它，避免出现大量重复的认证失败。此时后续请求会显示需要重新输入凭据的提示。若需重新通过设备码登录，可执行`hermes auth add codex-oauth`（或通过`hermes model` → OpenAI Codex选项操作）；一旦下次请求成功，该被隔离的令牌就会被清除。
:::

:::warning
即便使用Nous Portal、Codex或自定义端点，某些工具（如视觉处理、网页摘要生成、MoA功能）仍会调用独立的“辅助”模型。默认情况下（`auxiliary.*.provider: "auto"`），Hermes会将这些任务路由到您在`hermes model`中选择的**主聊天模型**。您也可以为每个任务单独指定更便宜或更快速的模型（例如OpenRouter上的Gemini Flash模型）——详情请参阅[辅助模型](/user-guide/configuration#auxiliary-models)。
:::

:::tip Nous工具网关
已订阅付费版Nous Portal的用户还可以使用**[工具网关](/user-guide/features/tool-gateway)**——该功能可让您通过订阅服务使用网页搜索、图像生成、文本转语音以及浏览器自动化等功能，无需额外API密钥。在首次安装时，执行`hermes setup --portal`命令即可一次性完成登录、设置Nous作为服务提供方并启用工具网关。现有用户则可通过`hermes model`选项或针对特定工具通过`hermes tools`选项来启用该功能。随时可通过`hermes portal info`命令查看当前的路由情况。
:::

### 两种用于模型管理的命令

Hermes提供了**两种**模型管理命令，各自具有不同的用途：

| 命令 | 执行位置 | 功能说明 |
|---------|-----------|----------|
| **`hermes model`** | 终端终端（在任何会话之外） | 完整的设置向导——用于添加服务提供方、执行OAuth认证、输入API密钥以及配置接口地址 |
| **`/model`** | Hermes聊天会话内部 | 快速在**已配置好的**服务提供方和模型之间切换 |

如果您想切换到尚未配置的服务提供方（例如目前仅配置了OpenRouter，但希望使用Anthropic的模型），则需要使用`hermes model`命令，而非`/model`。请先退出当前会话（使用`Ctrl+C`或`/quit`命令），然后执行`hermes model`完成服务提供方的设置，之后再启动新的会话。

### Anthropic（原生支持）

可直接通过Anthropic API使用Claude模型——无需通过OpenRouter代理。该方式支持三种认证方法：

:::caution 需要Claude Max的“额外使用额度”
当您通过`hermes model` → Anthropic OAuth方式认证（或执行`hermes auth add anthropic --type oauth`命令）后，Hermes会以Claude Code的身份向您的Anthropic账户发起请求。**此功能仅适用于使用了Claude Max套餐且购买了额外使用额度的用户。** Claude Max基础套餐所包含的默认使用额度不会被Hermes消耗，只有您额外购买的额度才会被使用。Claude Pro订阅用户无法使用此方式。

如果您没有Claude Max套餐及额外额度，可使用`ANTHROPIC_API_KEY`密钥——此时请求将按照该密钥对应组织的标准API定价进行计费（价格与Claude订阅计划无关）。
:::

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

当您通过 `hermes model` 选择 Anthropic OAuth 时，Hermes 会优先使用 Claude Code 自带的凭据存储机制，而非将令牌复制到 `~/.hermes/.env` 文件中。这样即可确保可续期的 Claude 凭据始终处于有效状态。

或者也可将其设置为永久有效：
```yaml
model:
  provider: "anthropic"
  default: "claude-sonnet-4-6"
```

:::提示：别名
`--provider claude` 和 `--provider claude-code` 也可作为 `--provider anthropic` 的简写形式使用。
:::

### GitHub Copilot

Hermes 将 GitHub Copilot 视为一等供应商并支持其两种使用模式：

**`copilot` — 直接调用 Copilot API**（推荐）。该模式利用您的 GitHub Copilot 订阅权限，通过 Copilot API 访问 GPT-5.x、Claude、Gemini 等模型。

```bash
hermes chat --provider copilot --model gpt-5.4
```

**身份验证选项**（按以下顺序进行检查）：

1. `COPILOT_GITHUB_TOKEN` 环境变量  
2. `GH_TOKEN` 环境变量  
3. `GITHUB_TOKEN` 环境变量  
4. 作为备选方案的 `gh auth token` CLI 命令  

如果未找到任何令牌，`hermes model` 会提供**OAuth 设备码登录**功能——该流程与 Copilot CLI 及 opencode 所使用的流程相同。

:::warning 令牌类型  
Copilot API **不支持**传统的个人访问令牌（`ghp_*`）。支持的令牌类型如下：

| 类型 | 前缀 | 获取方式 |
|------|------|----------|
| OAuth 令牌 | `gho_` | 通过 `hermes model` → GitHub Copilot → 使用 GitHub 登录 |
| 细粒度 PAT 令牌 | `github_pat_` | 在 GitHub 设置中进入开发者设置，选择“细粒度令牌”（需具备 **Copilot Requests** 权限） |
| GitHub 应用令牌 | `ghu_` | 通过安装 GitHub 应用获取 |

如果 `gh auth token` 返回的是 `ghp_*` 类型的令牌，请改用 `hermes model` 通过 OAuth 进行身份验证。
:::

:::info Hermes 中的 Copilot 身份验证机制  
Hermes 会直接将支持的 GitHub 令牌（`gho_*`、`github_pat_*` 或 `ghu_*`）发送至 `api.githubcopilot.com`，同时附带 Copilot 特有的请求头（`Editor-Version`、`Copilot-Integration-Id`、`Openai-Intent`、`x-initiator`）。  

当遇到 HTTP 401 错误时，Hermes 会在尝试备用方案之前先进行一次身份凭证恢复操作：  
1. 按照常规优先级顺序重新获取令牌（`COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` → `gh auth token`）  
2. 使用更新后的请求头重新构建共享的 OpenAI 客户端  
3. 再次尝试发送请求  

某些旧版本的社区代理服务器会使用 `api.github.com/copilot_internal/v2/token` 这一令牌交换接口。对于某些账户类型，该接口可能不可用（会返回 404 错误）。因此，Hermes 将直接使用令牌进行身份验证作为主要方式，并通过运行时凭证刷新和重试机制来提升稳定性。
:::

**API 路由**：GPT-5 及更高版本模型（`gpt-5-mini` 除外）会自动使用 Responses API；其他所有模型（GPT-4o、Claude、Gemini 等）则使用 Chat Completions 接口。模型类型会从实时更新的 Copilot 目录中自动识别。

**`copilot-acp` — Copilot ACP 智能体后端**：该组件会以子进程的形式启动本地的 Copilot CLI。

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
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖 Copilot CLI 可执行文件的路径（默认值为 `copilot`） |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖 ACP 参数（默认值为 `--acp --stdio`） |

### 一级 API 密钥提供者

这类提供者具备内置支持，并拥有专属的提供者标识。设置 API 密钥后，可使用 `--provider` 参数进行选择：

```bash
# NovitaAI Model API
hermes chat --provider novita --model moonshotai/kimi-k2.5
# Requires: NOVITA_API_KEY in ~/.hermes/.env

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

# Tencent TokenHub (Hy3 Preview)
hermes chat --provider tencent-tokenhub --model hy3-preview
# Requires: TOKENHUB_API_KEY in ~/.hermes/.env

# Arcee AI (Trinity models)
hermes chat --provider arcee --model trinity-large-thinking
# Requires: ARCEEAI_API_KEY in ~/.hermes/.env

# GMI Cloud
# Use the exact model ID returned by GMI's /v1/models endpoint.
hermes chat --provider gmi --model zai-org/GLM-5.1-FP8
# Requires: GMI_API_KEY in ~/.hermes/.env
```

或者可在 `config.yaml` 中永久设置提供方：
```yaml
model:
  provider: "gmi"
  default: "zai-org/GLM-5.1-FP8"
```

可通过 `NOVITA_BASE_URL`、`GLM_BASE_URL`、`KIMI_BASE_URL`、`MINIMAX_BASE_URL`、`MINIMAX_CN_BASE_URL`、`DASHSCOPE_BASE_URL`、`XIAOMI_BASE_URL`、`GMI_BASE_URL` 或 `TOKENHUB_BASE_URL` 环境变量来覆盖基础 URL。

:::note Z.AI 端点自动检测
在使用 Z.AI / GLM 提供商时，Hermes 会自动探测多个端点（全球端点、中国端点以及不同编程语言版本对应的端点），以找到能够识别您 API 密钥的端点。您无需手动设置 `GLM_BASE_URL`——系统会自动检测出可用的端点并将其缓存起来。
:::

### xAI（Grok）——响应 API + 提示词缓存

xAI 通过响应 API（`codex_responses` 传输协议）与系统相连，从而为 Grok 4 模型提供自动推理功能——无需设置 `reasoning_effort` 参数，服务器会默认执行推理操作。您只需在 `~/.hermes/.env` 中设置 `XAI_API_KEY`，并在“Hermes 模型”选项中选择 xAI；或者直接在 `/model grok-4-fast-reasoning` 中使用 `grok` 作为快捷名称即可。

SuperGrok 及 X Premium+ 用户可通过浏览器 OAuth 方式登录，而无需使用 API 密钥——只需在“Hermes 模型”选项中选择 **xAI Grok OAuth (SuperGrok / Premium+)**，或运行 `hermes auth add xai-oauth` 即可。直接用于 xAI 的工具（文本转语音、图像生成、视频生成、文字转录等）会自动重用相同的 OAuth 承载令牌。如需了解完整操作流程，请参阅 [xAI Grok OAuth 指南](../guides/xai-grok-oauth.md)；如果 Hermes 运行在远程主机上，还需参考 [通过 SSH/远程主机进行 OAuth 认证](../guides/oauth-over-ssh.md)，了解所需的 `ssh -L` 隧道设置。

当将 xAI 作为提供商使用（即基础 URL 包含 `x.ai`）时，Hermes 会在每次 API 请求中添加 `x-grok-conv-id` 标头，从而自动启用提示词缓存功能。这样一来，同一对话会话中的请求都会被路由到同一台服务器，便于 xAI 的基础设施重复使用已缓存的系统提示词和对话历史记录。

无需任何额外配置——一旦检测到 xAI 端点且存在会话 ID，缓存功能就会自动启动。这有助于降低多轮对话的延迟并节省成本。

xAI 还提供了专用的文本转语音端点（`/v1/tts`）。您可以在“Hermes 工具”→“语音与文本转语音”选项中选择 **xAI TTS**，或访问 [语音与文本转语音](../user-guide/features/tts.md#text-to-speech) 页面查看相关配置信息。

**已停用的 xAI 模型迁移（2026 年 5 月 15 日）：** xAI 将在 2026 年 5 月 15 日停止支持 `grok-4*`、`grok-3`、`grok-code-fast-1` 和 `grok-imagine-image-pro` 这些模型。`hermes doctor` 和 `hermes chat` 在启动时都会检测是否存在仍指向已停用模型的配置，并提示推荐的替代方案。您可以使用 `hermes migrate xai` 命令一次性重写配置——默认为试运行模式，如需应用更改，请添加 `--apply` 参数（系统会自动创建一个带时间戳的 `config.yaml.bak-pre-migrate-xai-*` 备份文件）。

```bash
hermes migrate xai          # preview replacements
hermes migrate xai --apply  # rewrite ~/.hermes/config.yaml in place
```

**xAI网络搜索后端。** 当启用[网络搜索](../user-guide/features/web-search.md)功能集时，`web.backend: xai`会通过相同的`XAI_API_KEY`/OAuth认证信息，将搜索请求路由至xAI提供的搜索接口。如果xAI已作为服务提供商配置完成，则无需进行额外设置。

### NovitaAI

[NovitaAI](https://novita.ai)是为开发者与智能体打造的原生AI云平台。该平台通过一个统一界面提供三大产品线：涵盖200多种模型的Model API、用于构建和运行智能体的Agent Sandbox，以及支持大规模计算的GPU Cloud。

```bash
# Use any available model
hermes chat --provider novita --model moonshotai/kimi-k2.5
# Requires: NOVITA_API_KEY in ~/.hermes/.env

# Short alias
hermes chat --provider novita-ai --model deepseek/deepseek-v3-0324
```

或者可在 `config.yaml` 中将其永久设置：
```yaml
model:
  provider: "novita"
  default: "moonshotai/kimi-k2.5"
  base_url: "https://api.novita.ai/openai/v1"
```

您可以在 [novita.ai/settings/key-management](https://novita.ai/settings/key-management) 获取 API 密钥。也可以通过 `NOVITA_BASE_URL` 参数来指定自定义的基础网址。

### Ollama Cloud — 托管式 Ollama 模型、OAuth 与 API 密钥

[Ollama Cloud](https://ollama.com/cloud) 提供与本地 Ollama 相同的开放权重模型库，且无需配备 GPU。在 `hermes model` 中选择 **Ollama Cloud**，粘贴从 [ollama.com/settings/keys](https://ollama.com/settings/keys) 获取的 API 密钥，Hermes 即会自动识别可用的模型。

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

模型目录会从 `ollama.com/v1/models` 动态获取并缓存一小时。`model:tag` 格式（例如 `qwen3-coder:480b-cloud`）在处理过程中会保持不变——请勿使用连字符。

:::提示 Ollama Cloud 与本地 Ollama 的区别
两者均使用相同的 OpenAI 兼容 API。Ollama Cloud 是一类特殊的提供方（需使用 `--provider ollama-cloud` 及 `OLLAMA_API_KEY` 参数）；而本地 Ollama 则通过自定义端点方式连接（基础网址为 `http://localhost:11434/v1`，无需密钥）。对于那些无法在本地运行的大型模型，建议使用云服务；若注重隐私或需要在离线环境下工作，则可选择本地版本。
:::

### AWS Bedrock
通过 AWS Bedrock 可调用 Anthropic Claude、Amazon Nova、DeepSeek v3.2、Meta Llama 4 等其他模型。该方案依赖 AWS SDK (`boto3`) 的身份验证机制——无需 API 密钥，仅需标准的 AWS 认证信息即可。

```bash
# Simplest — named profile in ~/.aws/credentials
hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6

# Or with explicit env vars
AWS_PROFILE=myprofile AWS_REGION=us-east-1 hermes chat --provider bedrock --model us.anthropic.claude-sonnet-4-6
```

或永久设置在 `config.yaml` 中：
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

认证过程采用标准的 boto3 方式：可直接指定 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`，或从 `~/.aws/credentials` 中读取 `AWS_PROFILE`；也可通过 EC2/ECS/Lambda 上的 IAM 角色、IMDS 或 SSO 进行认证。若已使用 AWS CLI 完成认证，则无需设置任何环境变量。

Bedrock 在底层实际上使用了 **Converse API**——所有请求都会被转换为与具体模型无关的格式，因此相同的配置即可适用于 Claude、Nova、DeepSeek 和 Llama 等模型。仅当需要调用非默认区域端点时，才需设置 `BEDROCK_BASE_URL`。

如需了解 IAM 设置、区域选择以及跨区域推理的详细步骤，请参阅 [AWS Bedrock 指南](/guides/aws-bedrock)。

### Qwen Portal（OAuth）

阿里云的 Qwen Portal 支持基于浏览器的 OAuth 登录。在 “hermes model” 中选择 **Qwen OAuth (Portal)**，通过浏览器完成登录，Hermes 会自动保存刷新令牌。

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

:::提示 Qwen OAuth 与 Qwen Cloud（阿里巴巴 DashScope）的区别
`qwen-oauth` 方式使用面向用户的 Qwen Portal 并通过 OAuth 进行登录，非常适合个人用户使用。而 `alibaba` 提供商则依托 Qwen Cloud（阿里巴巴 DashScope），并需要使用 `DASHSCOPE_API_KEY`，更适用于自动化或生产环境中的任务处理。尽管两者最终都会调用 Qwen 系列模型，但其端点地址各不相同。
:::

### 阿里云（Coding Plan）

如果您订阅了阿里巴巴的 **Coding Plan**（这是一种与常规 DashScope API 访问不同的计费方案），Hermes 会将其作为一个独立的顶级提供商来呈现，即 `alibaba-coding-plan`。其端点地址为 `https://coding-intl.dashscope.aliyuncs.com/v1`。该提供商与普通的 `alibaba` 提供商一样兼容 OpenAI，但具有不同的基础 URL 和计费方式。

```yaml
model:
  provider: alibaba_coding     # alias for alibaba-coding-plan
  model: qwen3-coder-plus
```

或者通过 CLI：

```bash
hermes chat --provider alibaba_coding --model qwen3-coder-plus
```

`alibaba_coding` 使用的 `DASHSCOPE_API_KEY` 与您现有的 `alibaba` 配置所使用的密钥相同——无需额外的密钥，仅需不同的路由目标即可。在注册该提供程序之前，那些在 `config.yaml` 中设置 `provider: alibaba_coding` 的用户会自动被路由至 OpenRouter。

### MiniMax（OAuth）

通过浏览器 OAuth 登录即可使用 MiniMax-M2.7——无需 API 密钥。只需在 “Hermes model” 中选择 **MiniMax (OAuth)**，通过浏览器完成登录，Hermes 便会自动保存访问令牌和刷新令牌。该功能在底层实际上使用了与 Anthropic Messages 兼容的端点（`/anthropic`）。

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
`minimax-oauth` 方式通过 MiniMax 提供的面向用户的门户网站进行 OAuth 登录，无需进行任何计费设置。而 `minimax` 及 `minimax-cn` 这两种提供方式则使用 `MINIMAX_API_KEY` / `MINIMAX_CN_API_KEY`，用于程序化访问。如需详细操作指南，请参阅 [MiniMax OAuth 使用指南](/guides/minimax-oauth)。
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
对于本地部署环境（如 DGX Spark、本地 GPU），请将 `NVIDIA_BASE_URL` 设置为 `http://localhost:8000/v1`。NIM 提供与 build.nvidia.com 完全一致的 OpenAI 兼容型聊天补全 API，因此只需修改一行环境变量即可实现云端与本地的切换。  
:::

Hermes 会自动在发送至 `build.nvidia.com` 的每个请求中添加 NIM 计费来源标识头——无需任何额外配置。这样一来，NVIDIA 的计费面板就能准确统计相应的使用量。  

### GMI 云服务  
可通过 [GMI Cloud](https://www.gmicloud.ai/) 使用开放模型与推理模型——该服务采用 OpenAI 兼容的 API，并支持 API 密钥认证。

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

### StepFun

基于 [StepFun](https://platform.stepfun.com) 的步骤系列模型——该平台提供兼容 OpenAI 的 API，采用 API 密钥进行身份验证。

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

可以通过 `STEPFUN_BASE_URL` 参数来覆盖基础 URL（默认值为 `https://api.stepfun.com/v1`）。

### Hugging Face 推理提供者

[Hugging Face 推理提供者](https://huggingface.co/docs/inference-providers) 能够通过统一的 OpenAI 兼容接口 (`router.huggingface.co/v1`) 调用 20 多种开源模型。系统会自动将请求路由至当前响应速度最快的后端服务（如 Groq、Together、SambaNova 等），并具备自动故障转移功能。

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

请在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 处获取您的令牌——务必开启“允许调用推理服务提供商”的权限。该服务包含免费套餐（每月提供0.10美元的额度，且不会在服务提供商的收费基础上再加价）。

您可以在模型名称后添加路由后缀：`:fastest`（默认值）、`:cheapest` 或 `:provider_name`，以此强制使用特定的后端。

您也可以通过 `HF_BASE_URL` 变量来覆盖基础URL。

### 通过 OAuth 访问 Google Gemini（`google-gemini-cli`）

`google-gemini-cli` 服务提供商使用的是 Google 的 Cloud Code Assist 后端——这与 Google 自带的 `gemini-cli` 工具所使用的 API 完全相同。该方案同时支持**免费套餐**（个人账户享有较高的每日调用限额）以及**付费套餐**（通过 GCP 项目选择标准版/企业版）。

**快速开始：**

```bash
hermes model
# → pick "Google Gemini (OAuth)"
# → see policy warning, confirm
# → browser opens to accounts.google.com, sign in
# → done — Hermes auto-provisions your free tier on first request
```

Hermes 默认会使用 Google 提供的 **公开版** `gemini-cli` 桌面端 OAuth 客户端——该客户端与 Google 在其开源版本的 `gemini-cli` 中使用的凭据完全相同。桌面端 OAuth 客户端并不涉及保密信息（安全性由 PKCE 机制保障），因此您无需安装 `gemini-cli`，也无需自行注册 GCP OAuth 客户端。

**认证流程如下：**
- 针对 `accounts.google.com` 的 PKCE 授权码流程
- 浏览器回调地址为 `http://127.0.0.1:8085/oauth2callback`（若该端口被占用，则会自动切换到临时端口）
- 令牌存储在 `~/.hermes/auth/google_oauth.json` 文件中（文件权限设置为 0600，采用原子写操作，并通过跨进程 `fcntl` 机制实现锁定）
- 令牌在过期前 60 秒自动刷新
- 在无界面环境中（如通过 SSH 连接，且设置了 `HERMES_HEADLESS=1`）会自动切换到粘贴模式作为备用
- 支持请求过程中的重复检测，避免同时发起的两个请求导致重复刷新
- 若出现 `invalid_grant` 错误（即刷新令牌被撤销），系统会清除凭据文件并提示用户重新登录

**模型推理流程如下：**
- 请求会被发送至 `https://cloudcode-pa.googleapis.com/v1internal:generateContent`（如需流式响应，则使用 `:streamGenerateContent?alt=sse` 地址），而非需付费的 `v1beta/openai` 接口
- 请求体采用 `{project, model, user_prompt_id, request}` 的结构封装
- OpenAI 格式的 `messages[]`、`tools[]`、`tool_choice` 等字段会被转换为 Gemini 自有的 `contents[]`、`tools[].functionDeclarations`、`toolConfig` 格式
- 系统会将响应重新转换回 OpenAI 格式，从而确保 Hermes 的其他功能能够正常运行

**套餐层级与项目 ID：**

| 您的情况 | 操作建议 |
|---|---|
| 使用个人 Google 账户，希望使用免费套餐 | 无需额外操作——直接登录即可开始对话 |
| 使用工作空间版、标准版或企业版账户 | 需将 `HERMES_GEMINI_PROJECT_ID` 或 `GOOGLE_CLOUD_PROJECT` 设置为您的 GCP 项目 ID |
| 所属组织受 VPC-SC 保护 | Hermes 会检测到 `SECURITY_POLICY_VIOLATED` 错误，并自动强制使用标准套餐 |

首次使用时，免费套餐会自动创建一个由 Google 管理的项目，无需您进行任何 GCP 配置。

**配额监控：**

```
/gquota
```

以进度条显示每个模型剩余的代码辅助配额：

```
Gemini Code Assist quota  (project: 123-abc)

  gemini-2.5-pro                      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░   85%
  gemini-2.5-flash [input]            ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░   92%
```

:::警告 政策风险  
谷歌认为将 Gemini CLI OAuth 客户端与第三方软件结合使用属于违反政策的行为。已有部分用户因此遭遇账户受限的情况。为获得最低风险的使用体验，建议通过 `gemini` 提供商自行使用 API 密钥。Hermes 会提前发出警告，并在开始 OAuth 过程前要求用户明确确认。  
:::

**自定义 OAuth 客户端（可选）：**  
如果您希望注册自己的 Google OAuth 客户端——例如为了将配额和授权范围限制在您自己的 GCP 项目中——请进行如下设置：

```bash
HERMES_GEMINI_CLIENT_ID=your-client.apps.googleusercontent.com
HERMES_GEMINI_CLIENT_SECRET=...   # optional for Desktop clients
```

请在已启用生成语言 API 的
[console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
上注册 **桌面应用** OAuth 客户端。

## 自定义及自托管的 LLM 提供方

Hermes Agent 可与**任何兼容 OpenAI 的 API 端点**配合使用。只要某服务器实现了 `/v1/chat/completions` 接口，您就可以将 Hermes 指向该服务器。这意味着您可以使用本地模型、GPU 推理服务器、多提供方路由器，或任何第三方 API。

### 基本设置

配置自定义端点有三种方式：

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

:::warning 旧版环境变量提示
`.env` 文件中的 `LLM_MODEL` 已**被移除**——模型及端点配置的权威来源现为 `config.yaml`。`OPENAI_BASE_URL` 仍然有效，但**仅适用于 `openai-api` 提供商**（它会覆盖 OpenAI 端点，以便直接通过 API 密钥访问）。对于其他提供商及自定义端点，请使用 `hermes model` 命令，或直接在 `config.yaml` 中设置 `model.base_url`。如果您的 `.env` 文件中存在过时的配置项，它们会在下次执行 `hermes setup` 或配置迁移时被自动清除。
:::

这两种方式都会将配置保存到 `config.yaml` 中，而该文件正是模型、提供商及基础 URL 的权威配置源。

### 使用 `/model` 切换模型

:::warning `hermes model` 与 `/model` 的区别
**`hermes model`**（在终端中运行，无需进入任何聊天会话）是**完整的提供商设置向导**。可通过它添加新提供商、执行 OAuth 流程、输入 API 密钥以及配置自定义端点。

**`/model`**（在正在进行的 Hermes 聊天会话中输入）仅能**在您已设置的提供商和模型之间切换**。它无法添加新提供商、执行 OAuth 流程或要求输入 API 密钥。如果您仅配置了一个提供商（例如 OpenRouter），则 `/model` 只会显示该提供商对应的模型。

**如需添加新提供商**：请先退出当前会话（使用 `Ctrl+C` 或 `/quit`），然后运行 `hermes model` 设置新提供商，最后再启动新的会话。
:::

一旦配置了至少一个自定义端点，即可在会话进行中切换模型：

```
/model custom:qwen-2.5          # Switch to a model on your custom endpoint
/model custom                    # Auto-detect the model from the endpoint
/model openrouter:claude-sonnet-4 # Switch back to a cloud provider
```

如果您已配置了**带名称的自定义提供程序**（详见下文），请使用三重语法：

```
/model custom:local:qwen-2.5    # Use the "local" custom provider with model qwen-2.5
/model custom:work:llama3       # Use the "work" custom provider with llama3
```

在切换提供者时，Hermes 会将基础 URL 和提供者信息保存在配置中，从而确保这些设置在重启后依然有效。当从自定义端点切换为内置提供者时，过期的基础 URL 会自动被清除。

:::提示
使用 ` /model custom`（不指定模型名称）命令可查询您端点的 `/models` API，如果仅加载了一个模型，则会自动选中该模型。此方法非常适合运行单个模型的本地服务器。
:::

以下所有示例都遵循相同的模式——只需更换 URL、键值以及模型名称即可。

---

### Ollama — 本地模型，零配置部署

[Ollama](https://ollama.com/) 只需一条命令即可在本地运行开源模型。最适合用于：快速进行本地实验、处理涉及隐私的工作以及离线使用。它还支持通过兼容 OpenAI 的 API 调用各类工具。

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

Hermes Agent 在使用工具时需要至少 **64,000 个标记** 的上下文长度。如果上下文窗口过小，系统在启动时会拒绝运行，因为系统提示、工具结构以及对话状态都需要足够的空间来支持可靠的多步骤任务流程。  

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

**您无法通过兼容 OpenAI 的 API（`/v1/chat/completions`）来设置上下文长度**。该参数必须通过服务器端配置或通过 Modelfile 来设定。这正是将 Ollama 与 Hermes 等工具集成时最容易引发混淆的问题所在。
:::

**请确认您的上下文设置正确：**

```bash
ollama ps
# Look at the CONTEXT column — it should show your configured value
```

:::提示
使用 `ollama list` 可以查看可用的模型列表。通过 `ollama pull <model>` 即可从 [Ollama 模型库](https://ollama.com/library) 中下载任意模型。Ollama 会自动处理 GPU 赋能功能——在大多数配置下无需额外设置即可使用。
:::

---

### vLLM — 高性能 GPU 推理

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

**上下文长度：** vLLM 默认会读取模型中的 `max_position_embeddings` 参数值。如果该数值超过了 GPU 的内存容量，程序将会报错，并要求用户将 `--max-model-len` 的数值设置得更低。您也可以使用 `--max-model-len auto` 选项，让系统自动检测并确定合适的最大长度。若希望将更多上下文加载到 VRAM 中，可设置 `--gpu-memory-utilization 0.95`（默认值为 0.9）。

**调用工具时需要指定特定参数：**

| 参数 | 用途 |
|------|------|
| `--enable-auto-tool-choice` | 当 `tool_choice: "auto"`（即 Hermes 的默认设置）时必须使用此参数 |
| `--tool-call-parser <name>` | 用于解析模型所使用的工具调用格式的解析器 |

支持的解析器包括：`hermes`（适用于 Qwen 2.5、Hermes 2/3）、`llama3_json`（适用于 Llama 3.x）、`mistral`、`deepseek_v3`、`deepseek_v31`、`xlam`、`pythonic`。若未指定这些参数，工具调用功能将无法正常工作——模型只会以文本形式输出工具调用指令。

:::提示
vLLM 支持使用人类易读的尺寸单位：`--max-model-len 64k`（小写 k 表示 1000，大写 K 表示 1024）。
:::

---

### SGLang — 基于 RadixAttention 的快速服务方案

[SGLang](https://github.com/sgl-project/sglang) 是另一种基于 RadixAttention 技术实现 KV 缓存复用的 vLLM 替代方案。它尤其适用于多轮对话（前缀缓存）、受限解码以及结构化输出场景。

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

**上下文长度：** SGLang 默认会从模型的配置文件中读取该值。如需修改，可使用 `--context-length` 参数进行覆盖。若需超出模型规定的最大上下文长度，可设置 `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1`。

**工具调用：** 需根据所使用的模型系列选择对应的解析器，并搭配 `--tool-call-parser` 参数使用，例如：`qwen`（Qwen 2.5）、`llama3`、`llama4`、`deepseekv3`、`mistral`、`glm`。若不使用此参数，工具调用结果将以纯文本形式返回。

:::注意 SGLang 的默认最大输出token数为128
如果响应内容出现截断现象，可在请求中添加 `max_tokens` 参数，或是在服务器端设置 `--default-max-tokens` 参数。若请求中未指定该值，SGLang 的默认每条响应的最大token数仅为128。
:::

---

### llama.cpp / llama-server — CPU与Metal推理

[llama.cpp](https://github.com/ggml-org/llama.cpp) 能在CPU、Apple Silicon（Metal）以及消费级GPU上运行量化后的模型。非常适合以下场景：无需数据中心级GPU的环境、Mac用户以及边缘设备部署。

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

**上下文长度（`-c`）：** 最新版本的默认值为 `0`，此时会从 GGUF 元数据中读取模型的训练上下文。对于训练上下文超过 128k 的模型，若尝试分配完整的 KV 缓存，可能会导致内存不足。建议为 Hermes 显式设置 `-c` 参数，其值至少应为 64,000 个标记。如果使用了并行任务槽（`-np`），总上下文长度会分配到各个任务槽中——例如在 `--c 64000 --np 4` 的配置下，每个任务槽仅能获得 16k 的上下文长度，这低于 Hermes 对单个活跃会话设定的最低要求。

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
若未使用 `--jinja`，llama-server 会完全忽略 `tools` 参数。模型会尝试在响应文本中写入 JSON 来调用工具，但 Hermes 无法将其识别为工具调用——此时你只会看到类似 `{"name": "web_search", ...}` 的原始 JSON 内容被当作普通消息输出，而无法实现实际搜索功能。

原生工具调用支持（性能最佳）：Llama 3.x、Qwen 2.5（含 Coder 版本）、Hermes 2/3、Mistral、DeepSeek、Functionary。其他所有模型则使用通用处理机制，虽然也能正常工作，但效率可能稍低。完整列表请参阅 [llama.cpp 函数调用文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md)。

你可以通过访问 `http://localhost:8080/props` 来确认工具调用功能是否已启用——该页面应包含 `chat_template` 字段。
:::

:::tip
你可以从 [Hugging Face](https://huggingface.co/models?library=gguf) 下载 GGUF 格式的模型。Q4_K_M 量化格式能在模型质量与内存占用之间实现最佳平衡。
:::

---

### LM Studio — 支持本地模型的桌面应用

[LM Studio](https://lmstudio.ai/) 是一款具备图形用户界面的桌面应用，可用于运行本地模型。它非常适合：偏好可视化界面的用户、需要快速测试模型的用户，以及 macOS/Windows/Linux 系统上的开发者。

你可以通过 LM Studio 应用启动服务器（在“开发者”选项卡中选择“启动服务器”），或者直接使用命令行工具：

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

Hermes 会自动加载上下文长度为 64K 的 LM Studio 模型。

若要在 LM Studio 中更改上下文长度：

1. 点击模型选择器旁边的齿轮图标；
2. 将“上下文长度”设置为至少 64000，以确保流畅的使用体验；
3. 重新加载模型，使更改生效；
4. 如果您的设备无法支持 64000 的上下文长度，可考虑使用上下文长度较大但规模较小的模型。

或者，您也可以通过 CLI 命令实现：`lms load model-name --context-length 64000`

您还可以使用 CLI 来预估模型是否适用该配置：`lms load model-name --context-length 64000 --estimate-only`

如需为每个模型设置永久默认值：请进入“我的模型”选项卡 → 选择对应模型后的齿轮图标 → 设置上下文长度。
:::

**工具调用功能：** 自 LM Studio 0.3.6 版本起支持。经过原生工具调用训练的模型（如 Qwen 2.5、Llama 3.x、Mistral、Hermes）会自动被识别，并显示工具标识符；其他模型则使用通用替代方案，其可靠性可能较低。

---

### WSL2 网络设置（Windows 用户）

由于 Hermes Agent 需要 Unix 环境，Windows 用户需在 WSL2 中运行该代理。如果您的模型服务器（如 Ollama、LM Studio 等）运行在**Windows 主机**上，您就需要搭建网络桥接——WSL2 使用带有独立子网的虚拟网络适配器，因此 WSL2 内部的 `localhost` 指的是 Linux 虚拟机，而非 Windows 主机。

:::提示：如果模型服务器也在 WSL2 中运行（vLLM、SGLang 和 llama-server 通常如此），则 `localhost` 可正常使用——因为它们共享同一个网络命名空间，无需参考本节内容。
:::

#### 方案 1：镜像网络模式（推荐）

该功能适用于**Windows 11 22H2 及更高版本**。镜像模式可使 Windows 和 WSL2 之间的 `localhost` 实现双向通信，是最简单的解决方案。

1. 创建或编辑 `%USERPROFILE%\.wslconfig` 文件（例如：`C:\Users\YourName\.wslconfig`）：
   ```ini
   [wsl2]
   networkingMode=mirrored
   ```

2. 通过 PowerShell 重启 WSL：
   ```powershell
   wsl --shutdown
   ```

3. 重新打开您的 WSL2 终端。此时，“localhost”已能够访问 Windows 服务：
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

如果您无法使用镜像模式，可在 WSL2 内部查找 Windows 主机 IP，并将其代替 `localhost` 使用：

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
在 WSL2 重启后，主机 IP 可能会发生变化。您可以在 Shell 中动态获取该地址：
```bash
export WSL_HOST=$(ip route show | grep -i default | awk '{ print $3 }')
echo "Windows host at: $WSL_HOST"
curl http://$WSL_HOST:11434/v1/models   # Test Ollama
```

或者使用您机器的 mDNS 名称（在 WSL2 环境下需要安装 `libnss-mdns`）：
```bash
sudo apt install libnss-mdns
curl http://$(hostname).local:11434/v1/models
```
:::

#### 服务器绑定地址（NAT模式所需）

如果您选择**方案2**（使用主机IP的NAT模式），Windows上的模型服务器必须能够接收来自`127.0.0.1`之外的连接。默认情况下，大多数服务器仅监听本机地址——而NAT模式下的WSL2连接来自不同的虚拟子网，因此会被拒绝。在镜像模式下，`localhost`会直接映射，因此默认的`127.0.0.1`绑定方式可以正常使用。

| 服务器 | 默认绑定地址 | 解决方法 |
|--------|-------------|----------|
| **Ollama** | `127.0.0.1` | 在启动Ollama之前设置`OLLAMA_HOST=0.0.0.0`环境变量（Windows可在“系统设置”→“环境变量”中设置，或直接编辑Ollama服务） |
| **LM Studio** | `127.0.0.1` | 在“开发者”选项卡→“服务器设置”中启用**“在网络中提供服务”**功能 |
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

如果收到列出你所拥有模型的 JSON 响应，那就说明一切正常。请将该 URL 作为 Hermes 配置中的 `base_url` 使用。

---

### 本地模型的故障排查

当与 Hermes 结合使用时，以下问题会影响**所有**本地推理服务器。

#### WSL2 无法连接到 Windows 主机上的模型服务器，出现“连接被拒绝”错误

如果你在 WSL2 中运行 Hermes，而模型服务器位于 Windows 主机上，在 WSL2 的默认 NAT 网络模式下，`http://localhost:<port>` 这种地址格式将无法使用。请参考上文[WSL2 网络设置](#wsl2-networking-windows-users)了解解决方案。

#### 工具调用仅以文本形式出现，而未真正执行

模型会以消息形式输出类似 `{"name": "web_search", "arguments": {...}}` 的内容，而非实际调用对应工具。

**原因：** 你的服务器未开启工具调用功能，或者该模型通过服务器的工具调用实现方式不支持此项功能。

| 服务器 | 解决方案 |
|--------|----------|
| **llama.cpp** | 在启动命令中添加 `--jinja` 参数 |
| **vLLM** | 添加 `--enable-auto-tool-choice --tool-call-parser hermes` 参数 |
| **SGLang** | 添加 `--tool-call-parser qwen`（或其他合适的解析器）参数 |
| **Ollama** | 工具调用功能默认已开启——请确保你的模型支持该功能（可通过 `ollama show model-name` 查验） |
| **LM Studio** | 升级到 0.3.6 及更高版本，并使用原生支持工具调用的模型 |

#### 模型似乎会遗忘上下文或给出逻辑混乱的回复

**原因：** 上下文窗口大小过小。当对话内容超出上下文限制时，大多数服务器会自动丢弃较旧的消息。仅 Hermes 的系统提示语和工具结构就可能需要 4k–8k 个令牌。

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

Hermes 会自动从服务器的 `/v1/models` 接口获取上下文长度信息。如果服务器返回的值过低（或根本未返回），Hermes 将使用模型本身声明的限制值，而这很可能并不准确。

**解决方案：** 在 `config.yaml` 文件中明确指定该数值：

```yaml
model:
  default: your-model
  provider: custom
  base_url: http://localhost:11434/v1
  context_length: 64000
```

#### 响应在句子中途被截断

**可能原因：**
1. **服务器端的输出限制（`max_tokens`）过低** — SGLang 默认每条响应的限制为 128 个标记。可在服务器端设置 `--default-max-tokens` 参数，或通过 config.yaml 中的 `model.max_tokens` 选项来配置 Hermes。注意：`max_tokens` 仅控制响应长度，与对话历史记录的长度（即 `context_length`）无关。
2. **上下文耗尽** — 模型的上下文窗口已满。可增加 `model.context_length` 的值，或在 Hermes 中启用[上下文压缩功能](/user-guide/configuration#context-compression)。

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

接着通过 `hermes model` → Custom endpoint → `http://localhost:4000/v1` 的方式来配置 Hermes。以下是一个包含备用方案的 `litellm_config.yaml` 示例：
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

BlockRunAI 开发的 [ClawRouter](https://github.com/BlockRunAI/ClawRouter) 是一款本地路由代理工具，能够根据查询的复杂度自动选择合适的模型。它通过 14 个维度对请求进行分类，然后将请求路由至最能处理该任务的低成本模型。该服务采用 USDC 加密货币进行支付，无需 API 密钥。

```bash
# Install and start
npx @blockrun/clawrouter    # Starts on port 8402
```

接着通过 `hermes model` → Custom endpoint → `http://localhost:8402/v1` 的方式配置 Hermes，模型名称设置为 `blockrun/auto`。

路由配置文件：
| 配置文件 | 策略 | 节省比例 |
|---------|--------|----------|
| `blockrun/auto` | 平衡质量与成本 | 74-100% |
| `blockrun/eco` | 尽可能降低成本 | 95-100% |
| `blockrun/premium` | 最高质量的模型 | 0% |
| `blockrun/free` | 仅使用免费模型 | 100% |
| `blockrun/agentic` | 针对工具使用场景优化 | 比例不一 |

:::note
ClawRouter 需要在 Base 或 Solana 网络上拥有一个存储 USDC 的钱包用于支付。所有请求均通过 BlockRun 的后端 API 进行处理。可运行 `npx @blockrun/clawrouter doctor` 命令来检查钱包状态。
:::

---

### 其他兼容的提供商

任何具备 OpenAI 兼容 API 的服务均可使用。以下是一些热门选项：

| 提供商 | 基础 URL | 备注 |
|--------|----------|------|
| [Together AI](https://together.ai) | `https://api.together.xyz/v1` | 云端托管的开放模型 |
| [Groq](https://groq.com) | `https://api.groq.com/openai/v1` | 极速推理性能 |
| [DeepSeek](https://deepseek.com) | `https://api.deepseek.com/v1` | DeepSeek 模型 |
| [Fireworks AI](https://fireworks.ai) | `https://api.fireworks.ai/inference/v1` | 快速的开放模型托管服务 |
| [GMI Cloud](https://www.gmicloud.ai/) | `https://api.gmi-serving.com/v1` | 受管理的 OpenAI 兼容推理服务 |
| [Cerebras](https://cerebras.ai) | `https://api.cerebras.ai/v1` | 瓷片级芯片推理技术 |
| [Mistral AI](https://mistral.ai) | `https://api.mistral.ai/v1` | Mistral 模型 |
| [OpenAI](https://openai.com) | `https://api.openai.com/v1` | 直接接入 OpenAI 服务 |
| [Azure OpenAI](https://azure.microsoft.com) | `https://YOUR.openai.azure.com/` | 企业级 OpenAI 服务 |
| [LocalAI](https://localai.io) | `http://localhost:8080/v1` | 自托管的多模型系统 |
| [Jan](https://jan.ai) | `http://localhost:1337/v1` | 支持本地模型的桌面应用 |

可通过 `hermes model` → Custom endpoint 或在 `config.yaml` 文件中配置这些提供商。

```yaml
model:
  default: meta-llama/Llama-3.1-70B-Instruct-Turbo
  provider: custom
  base_url: https://api.together.xyz/v1
  api_key: your-together-key
```

### 上下文长度检测

:::注意：两个易混淆的设置
**`context_length`**表示**总上下文窗口大小**——即输入与输出令牌的总上限（例如，Claude Opus 4.6的值为200,000）。Hermes会利用这一数值来决定何时压缩对话历史记录，以及如何验证API请求。

**`model.max_tokens`**则代表**输出限制**——模型在*单次响应*中可生成的最多令牌数。它与对话历史的长度无关。由于行业通用名称为`max_tokens`，因此常常造成混淆；为便于理解，Anthropic的官方API现已将其更名为`max_output_tokens`。

当自动检测无法准确获取上下文窗口大小时，请设置`context_length`；
仅当需要限制单次响应的长度时，才需设置`model.max_tokens`。
:::

Hermes通过多源解析机制来确定适合您所用模型及服务提供商的正确上下文窗口大小：

1. **配置覆盖**——config.yaml中的`model.context_length`（优先级最高）
2. **模型专属的自定义服务提供商设置**——`custom_providers[].models.<id>.context_length`
3. **持久化缓存**——之前检测到的数值（重启后依然有效）
4. **端点 `/models`**——查询您服务器上的API（本地或自定义端点）
5. **Anthropic的 `/v1/models`**——向Anthropic的API查询`max_input_tokens`信息（仅限拥有API密钥的用户）
6. **OpenRouter API**——获取来自OpenRouter的实时模型元数据
7. **Nous Portal**——根据模型ID的后缀与OpenRouter的元数据进行匹配
8. **[models.dev](https://models.dev)**——由社区维护的注册表，收录了100多家服务提供商提供的3800多种模型的特定上下文长度参数
9. **备用默认值**——基于模型类别的通用默认值（默认为128K）

对于大多数使用场景，该机制可直接正常工作。系统具备服务提供商识别功能——同一模型在不同提供方那里的上下文限制可能有所不同（例如，`claude-opus-4.6`在Anthropic官方平台上的上下文限制为100万，而在GitHub Copilot上则为128K）。

如需手动设置上下文长度，请在模型配置中添加`context_length`字段：

```yaml
model:
  default: "qwen3.5:9b"
  base_url: "http://localhost:8080/v1"
  context_length: 131072  # tokens
```

对于自定义端点，您还可以为每个模型设置上下文长度：

```yaml
custom_providers:
  - name: "My Local LLM"
    base_url: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 64000
      deepseek-r1:70b:
        context_length: 65536
```

在配置自定义端点时，`hermes model` 会提示输入上下文长度。如需自动检测，可将其留空。

:::提示：何时需要手动设置该值
- 您使用的是 Ollama，且其自定义的 `num_ctx` 值低于模型支持的最大值
- 您希望将上下文长度限制在模型最大值之下（例如，为节省显存，将 128k 容量的模型限制在 8k）
- 您运行在无法访问 `/v1/models` 接口的代理服务器后端

:::

---

### 带名称的自定义提供者

如果您需要使用多个自定义端点（例如本地开发服务器和远程 GPU 服务器），可以在 `config.yaml` 中将它们定义为带名称的自定义提供者：

```yaml
custom_providers:
  - name: local
    base_url: http://localhost:8080/v1
    # api_key omitted — Hermes uses "no-key-required" for keyless local servers
  - name: work
    base_url: https://gpu-server.internal.corp/v1
    key_env: CORP_API_KEY
    api_mode: chat_completions   # set explicitly by `hermes model` → Custom Endpoint wizard; auto-detection still happens as a fallback
  - name: anthropic-proxy
    base_url: https://proxy.example.com/anthropic
    key_env: ANTHROPIC_PROXY_KEY
    api_mode: anthropic_messages  # for Anthropic-compatible proxies
```

某些兼容 OpenAI 的接口需要特定提供方的请求体字段。只需在对应的自定义提供方中添加一个 `extra_body` 映射表，Hermes 就会将其合并到该接口的每个聊天完成请求中：

```yaml
custom_providers:
  - name: gemma-local
    base_url: http://localhost:8080/v1
    model: google/gemma-4-31b-it
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

现在，“Hermes 模型”→“自定义端点”向导会明确要求用户输入 `api_mode` 值，并将该值保存到 `config.yaml` 文件中。如果该字段未被填写，系统仍会以 URL 自动检测作为备用方案（例如，以 `/anthropic` 开头的路径会被识别为 `anthropic_messages` 类型）。

**针对自定义提供者模型的原生视觉处理功能。** 如果您的自定义端点用于托管模型库中未收录的具备视觉处理能力的模型，请将 `model.supports_vision: true` 设为真值，这样 Hermes 就能直接将附带的图片作为 `image_url` 部分进行传输，而无需先通过 `vision_analyze` 功能对其进行预处理。只需设置这一个参数即可，无需再单独设置 `agent.image_input_mode: native`。

```yaml
model:
  provider: custom
  base_url: http://localhost:8080/v1
  default: qwen3.6-35b-a3b
  supports_vision: true   # send images natively; otherwise vision_analyze pre-describes them
```

在按提供者命名的模型中（如 `custom_providers[*].models[*].supports_vision`），也会优先使用该键，且该键支持标准的 YAML 布尔值格式（`true/false/yes/no/on/off/1/0`）。

您可以使用三重语法在会话进行过程中切换这些配置：

```
/model custom:local:qwen-2.5       # Use the "local" endpoint with qwen-2.5
/model custom:work:llama3-70b      # Use the "work" endpoint with llama3-70b
/model custom:anthropic-proxy:claude-sonnet-4  # Use the proxy
```

您还可以从交互式的 `hermes model` 菜单中选择已命名的自定义服务提供商。

---

### 实用指南：Together AI、Groq、Perplexity

[其他兼容服务提供商](#other-compatible-providers) 中列出的所有云服务提供商均支持 OpenAI 的 REST 接口规范，因此在 `custom_providers:` 配置下它们的使用方式完全一致。以下是三种经过验证的有效配置方案。只需将相关配置内容添加到 `~/.hermes/config.yaml` 文件中，再将对应的 API 密钥放入 `~/.hermes/.env` 文件即可。

#### Together AI

该平台提供开源模型（如 Llama、MiniMax、Gemma、DeepSeek、Qwen），其服务价格远低于官方 API 的收费水平，是构建多模型系统的理想选择。

```yaml
# ~/.hermes/config.yaml
custom_providers:
  - name: together
    base_url: https://api.together.xyz/v1
    key_env: TOGETHER_API_KEY
    # api_mode: chat_completions  # default — no need to set

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
custom_providers:
  - name: groq
    base_url: https://api.groq.com/openai/v1
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

当您需要一款能够自动进行实时网络搜索并标注引用来源的模型时，该服务非常实用。其支持的模型种类较为有限——请访问 [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) 查看当前支持的列表。

```yaml
# ~/.hermes/config.yaml
custom_providers:
  - name: perplexity
    base_url: https://api.perplexity.ai
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

这三个方案可组合使用——将它们全部一同启用，并通过 `/model custom:<名称>:<模型>` 在每轮对话中切换不同的模型：

```yaml
custom_providers:
  - name: together
    base_url: https://api.together.xyz/v1
    key_env: TOGETHER_API_KEY
  - name: groq
    base_url: https://api.groq.com/openai/v1
    key_env: GROQ_API_KEY
  - name: perplexity
    base_url: https://api.perplexity.ai
    key_env: PERPLEXITY_API_KEY

model:
  default: MiniMaxAI/MiniMax-M2.7
  provider: custom:together      # boot to Together; switch freely after
```

:::提示 故障排除
- 在#15083号补丁完成CLI验证器优化后，使用`hermes doctor`检查时，针对上述任何提供商名称均不应出现“未知提供商”的警告信息。
- 若某个提供商的 `/v1/models` 接口无法访问（以Perplexity为例），`hermes model`命令会先发出警告并保留该模型，而不会直接拒绝——详情参见#15136。
- 若希望完全省略`custom_providers:`配置，直接使用`provider: custom`并结合`CUSTOM_BASE_URL`环境变量，可参考#15103。
:::

---

### 选择合适的设置方案

| 使用场景 | 推荐方案 |
|----------|----------|
| **仅需确保功能正常运行** | OpenRouter（默认）或Nous Portal |
| **本地模型，部署简单** | Ollama |
| **生产环境GPU加速服务** | vLLM或SGLang |
| **Mac系统/无GPU** | Ollama或lama.cpp |
| **多提供商路由** | LiteLLM Proxy或OpenRouter |
| **成本优化** | ClawRouter或配置`sort: "price"`参数的OpenRouter |
| **最高隐私保护** | Ollama、vLLM或lama.cpp（完全本地运行） |
| **企业环境/Azure平台** | 配置自定义端点的Azure OpenAI |
| **中文AI模型** | z.ai（GLM）、Kimi/Moonshot（`kimi-coding`或`kimi-coding-cn`）、MiniMax、小米MiMo，或腾讯TokenHub（优质提供商） |

:::提示
您可以通过`hermes model`随时切换不同的提供商，无需重启服务。无论使用哪种提供商，您的对话历史、记忆内容及技能配置都会被保留。
:::

## 可选API密钥

| 功能 | 提供商 | 环境变量 |
|------|--------|----------|
| 网页抓取 | [Firecrawl](https://firecrawl.dev/) | `FIRECRAWL_API_KEY`、`FIRECRAWL_API_URL` |
| 浏览器自动化 | [Browserbase](https://browserbase.com/) | `BROWSERBASE_API_KEY`、`BROWSERBASE_PROJECT_ID` |
| 图像生成 | [FAL](https://fal.ai/) | `FAL_KEY` |
| 高级文本转语音音色 | [ElevenLabs](https://elevenlabs.io/) | `ELEVENLABS_API_KEY` |
| OpenAI文本转语音+语音转写 | [OpenAI](https://platform.openai.com/api-keys) | `VOICE_TOOLS_OPENAI_KEY` |
| Mistral文本转语音+语音转写 | [Mistral](https://console.mistral.ai/) | `MISTRAL_API_KEY` |
| 跨会话用户建模 | [Honcho](https://honcho.dev/) | `HONCHO_API_KEY` |
| 语义长期记忆功能 | [Supermemory](https://supermemory.ai) | `SUPERMEMORY_API_KEY` |

### 自主托管Firecrawl
默认情况下，Hermes会使用[Firecrawl云API](https://firecrawl.dev/)进行网页搜索和抓取操作。如果您希望本地运行Firecrawl，可让Hermes连接至自托管实例。完整的部署指南请参考Firecrawl的[SELF_HOST.md](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)文档。

**优势：**无需API密钥，无速率限制，无每页请求费用，数据完全由您掌控。
**局限：**云版本依托Firecrawl专有的“Fire-engine”技术，具备更强大的反爬机制（可绕过Cloudflare防护、验证码及IP轮换）。自托管版本仅使用基础fetch功能结合Playwright，因此部分受保护的网站可能无法访问。搜索引擎也会从Google切换为DuckDuckGo。

**部署步骤：**
1. 克隆并启动Firecrawl的Docker容器组（包含5个容器：API服务、Playwright浏览器、Redis缓存、RabbitMQ消息队列、PostgreSQL数据库——需约4-8GB内存）：
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
```

**快捷指令：** 在任意模型名称后添加 `:nitro` 即可按吞吐量进行排序（例如 `anthropic/claude-sonnet-4:nitro`），添加 `:floor` 则可按价格进行排序。

## OpenRouter Pareto Code Router

OpenRouter 提供了一个名为 `openrouter/pareto-code` 的实验性编程模型路由器，它能自动将请求路由到符合特定编程质量标准且价格最低的模型（该质量标准由 [Artificial Analysis](https://artificialanalysis.ai/) 评估）。选择该模型后，只需在 `~/.hermes/config.yaml` 文件中调整 `min_coding_score` 参数即可：

```yaml
model:
  provider: openrouter
  model: openrouter/pareto-code

openrouter:
  min_coding_score: 0.65   # 0.0–1.0; higher = stronger (more expensive) coders. Default 0.65.
```

备注：

- 仅当 `model.model` 为 `openrouter/pareto-code` 时，才会发送 `min_coding_score` 参数；对于其他模型，该参数将不起任何作用。
- 若将其设置为空字符串（或删除该行），则由 OpenRouter 自动选择性能最强的编码器——这正是当未指定插件列表时的默认行为。
- 在特定日期内，选择结果会根据评分以确定性方式确定，但随着帕累托前沿的变化（新模型的出现、基准测试的更新），实际选定的模型也可能会发生变化。
- 如需了解路由器的完整行为，请参阅 OpenRouter 的 [Pareto Router 文档](https://openrouter.ai/docs/guides/routing/routers/pareto-router)。
- 若希望将 Pareto Code 路由器用于特定的**辅助任务**（如压缩、图像处理等），而非作为主代理使用，可在对应任务下设置 `extra_body.plugins` 参数——详情请参阅 [辅助模型 → OpenRouter 路由及用于辅助任务的 Pareto Code](/user-guide/configuration#openrouter-routing--pareto-code-for-auxiliary-tasks)。

## 备用提供者

当主模型出现故障（如速率限制、服务器错误、认证失败）时，可配置一系列备用提供者，Hermes 会按顺序尝试这些提供者。标准的配置格式是在顶层添加 `fallback_providers:` 列表：

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
  - provider: anthropic
    model: claude-sonnet-4
    # base_url: http://localhost:8000/v1    # optional, for custom endpoints
    # api_mode: chat_completions           # optional override
```

为确保向后兼容，传统的单对键格式 `fallback_model:` 字典仍然被支持。

```yaml
fallback_model:
  provider: openrouter
  model: anthropic/claude-sonnet-4
```

启用该功能后，Fallback机制会在会话进行过程中无缝切换模型与提供方，从而确保您的对话内容不会丢失。系统会按顺序逐一尝试不同的链式模型；每个会话中仅可触发一次激活操作。

支持的提供方包括：`openrouter`、`nous`、`novita`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`huggingface`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`bedrock`、`azure-foundry`、`opencode-zen`、`opencode-go`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`stepfun`、`lmstudio`、`alibaba`、`alibaba-coding-plan`、`tencent-tokenhub`以及自定义提供方。

:::提示
Fallback功能的配置仅能通过`config.yaml`文件完成，也可通过`hermes fallback`命令以交互方式设置。如需详细了解其触发条件、链式模型的处理流程，以及其与辅助任务和委托机制的交互方式，请参阅[Fallback Providers](/user-guide/features/fallback-providers)文档。
:::

---

## 相关内容

- [配置](/user-guide/configuration) —— 基本配置设置（目录结构、配置优先级、终端后端、内存管理、压缩功能等）
- [环境变量](/reference/environment-variables) —— 所有环境变量的完整参考手册
