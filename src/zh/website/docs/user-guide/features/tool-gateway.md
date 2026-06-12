---
title: "Nous Tool Gateway"
description: "One subscription, every tool. Web search, image generation, TTS, and cloud browsers — all routed through Nous Portal with no extra API keys."
sidebar_label: "Tool Gateway"
sidebar_position: 2
---

# Nous 工具网关

**一个订阅，涵盖所有内置工具**

所有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅均包含工具网关。该网关能够通过 Nous 已有的基础设施来路由 Hermes 的各类工具调用——包括网络搜索、图像生成、文本转语音以及云浏览器自动化功能——因此您无需为让智能体具备实用功能而额外注册 Firecrawl、FAL、OpenAI、Browser Use 或其他任何服务。

<div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap', margin: '1.5rem 0'}}>
  <a href="https://portal.nousresearch.com/manage-subscription" style={{background: 'var(--ifm-color-primary)', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '6px', textDecoration: 'none', fontWeight: 'bold'}}>开始或管理订阅 →</a>
</div>

## 包含的功能

| | 工具 | 功能说明 |
|---|---|---|
| 🔍 | **网络搜索与信息提取** | 通过 Firecrawl 实现智能体级的网络搜索及整页内容提取功能。无需担心速率限制——网关会自动处理扩展需求。 |
| 🎨 | **图像生成** | 通过一个接口即可调用九种模型：**FLUX 2 Klein 9B**、**FLUX 2 Pro**、**Z-Image Turbo**、**Nano Banana Pro**（Gemini 3 Pro Image）、**GPT Image 1.5**、**GPT Image 2**、**Ideogram V3**、**Recraft V4 Pro**、**Qwen Image**。您可以通过参数指定要使用的模型，或让 Hermes 默认使用 FLUX 2 Klein。 |
| 🔊 | **文本转语音** | OpenAI 的 TTS 语音功能已集成到 `text_to_speech` 工具中。您可以将其用于向 Telegram 发送语音消息、为流程生成音频，或是为任何内容添加旁白。 |
| 🌐 | **云浏览器自动化** | 通过 Browser Use 提供无头 Chromium 会话功能。包括 `browser_navigate`、`browser_click`、`browser_type`、`browser_vision` 等智能体所需的各类操作指令，且无需注册 Browserbase 账户。 |

以上四项功能均采用按使用量计费的模式，费用从您的 Nous 订阅账户中扣除。您可以根据需求自由组合使用方式——例如使用网关处理网络搜索和图像生成任务，同时自行保留 ElevenLabs 的 TTS 密钥；或者将所有操作都通过 Nous 网关来处理。

## 为何需要它？

要构建一个真正能“执行任务”的智能体，往往需要同时订阅 5 种以上的 API 服务，每种服务都有独立的注册流程、速率限制、计费方式以及特殊要求。而工具网关将这一切整合到了一个账户中：

- **一份账单**：只需向 Nous 支付费用，其余工作由我们负责。
- **一次注册**：无需管理 Firecrawl、FAL、Browser Use 或 OpenAI 语音相关的多个账户。
- **一个密钥**：您的 Nous Portal OAuth 认证即可覆盖所有工具。
- **相同质量**：使用与直接调用 API 相同的后端服务，只是由我们提供统一接口。

您也可以随时自行添加其他密钥——针对不同工具按需配置。工具网关并非束缚，而是一条快捷路径。

## 开始使用

共有三种接入方式，请选择最适合您当前情况的那一种：

```bash
hermes setup --portal     # Fresh install: Nous OAuth + set Nous as provider + turn on the Tool Gateway in one go
```

```bash
hermes model              # Switch your inference provider to Nous Portal — Hermes then offers to turn on the gateway for all tools
```

```bash
hermes tools              # Enable the gateway per-tool — pick "Nous Subscription" for any tool you want
```

`hermes setup --portal` 和 `hermes model` 是一次性配置路径：只需登录一次，即可选择将所有工具切换至网关模式。而 `hermes tools` 则是按需启用路径——你可以一次只开启所需的功能。

**无需先进行登录。** 使用 `hermes tools` 时，即使你从未登录过 Nous Portal，由 Nous 管理的后端服务（网页搜索、图像处理、视频处理、文本转语音、浏览器功能）也会始终显示在列表中。选中某项后，若你尚未完成身份验证，Hermes 会立即引导你登录 Portal——无需事先运行 `hermes model`。如果你的 Nous OAuth 已处于激活状态，选中对应后端即可立即启用，无需额外提示。此路径仅负责登录并开启你所选择的功能——它不会切换推理提供方，也不会要求你为其他功能启用网关模式。

随时可查看当前处于激活状态的功能：

```bash
hermes portal info        # Portal auth + Tool Gateway routing summary
hermes portal tools       # Gateway catalog with current routing per tool
hermes status             # Full system status (Tool Gateway is one section)
```

`hermes portal info` 的显示内容包含如下板块：

```
◆ Nous Tool Gateway
  Nous Portal     ✓ managed tools available
  Web tools       ✓ active via Nous subscription
  Image gen       ✓ active via Nous subscription
  TTS             ✓ active via Nous subscription
  Browser         ○ active via Browser Use key
```

标记为“通过Nous订阅激活”的工具会经过网关处理，而其他工具则直接使用您自己的密钥。

## 使用资格

Tool Gateway是一项**需付费订阅**的功能。免费级别的Nous账户虽然可以使用Portal进行推理，但不包含托管工具——请[升级您的套餐](https://portal.nousresearch.com/manage-subscription)以启用网关功能。

部分账户还可享受**免费工具池**服务——即在无需付费订阅的情况下，可使用少量托管工具来调用网关功能。当有可用免费资源时，网关会自动显示相关选项，并在首次使用时提示您进行设置，以便您立即开始使用托管工具。

## 自由组合

网关功能是针对单个工具单独启用的。您可以根据需求选择性地开启：
- **所有工具均通过Nous处理**——最为简单，只需一个订阅即可。
- **Web和图像处理使用网关，文本转语音自行提供**——保留您使用的ElevenLabs语音，其余任务由Nous处理。
- **仅对那些没有对应密钥的工具使用网关**——例如“我已经为Browserbase付费，但不想创建Firecrawl账户”的情况也完全适用。

您可以通过以下方式随时切换不同的工具：

```bash
hermes tools          # Interactive picker for each tool category
```

选择对应的工具，将提供方设置为**Nous Subscription**（或您偏好的任何直接提供方）。无需编辑任何配置。如果您尚未登录Nous Portal，选择**Nous Subscription**后会直接跳转至Portal登录页面——无需先通过`hermes model`进行身份验证。

## 使用单个图像模型

为追求速度，图像生成默认使用FLUX 2 Klein 9B模型。如需针对每次调用进行自定义设置，可向`image_generate`工具传递模型ID：

| 模型 | ID | 适用场景 |
|---|---|---|
| FLUX 2 Klein 9B | `fal-ai/flux-2/klein/9b` | 速度快，优秀的默认选择 |
| FLUX 2 Pro | `fal-ai/flux-2-pro` | 更高精度的FLUX模型 |
| Z-Image Turbo | `fal-ai/z-image/turbo` | 具有风格化特点且生成速度快 |
| Nano Banana Pro | `fal-ai/nano-banana-pro` | 类似Google Gemini 3 Pro的图像生成能力 |
| GPT Image 1.5 | `fal-ai/gpt-image-1.5` | OpenAI图像生成，支持文本+图像输入 |
| GPT Image 2 | `fal-ai/gpt-image-2` | OpenAI最新版本模型 |
| Ideogram V3 | `fal-ai/ideogram/v3` | 能较好遵循提示词要求，同时具备出色的排版能力 |
| Recraft V4 Pro | `fal-ai/recraft/v4/pro/text-to-image` | 向量风格，适用于平面设计 |
| Qwen Image | `fal-ai/qwen-image` | 阿里巴巴推出的多模态模型 |

该列表会持续更新——访问`hermes tools` → Image Generation即可查看最新的可用模型列表。

---

## 配置参考

大多数用户无需触碰此部分——`hermes model`和`hermes tools`已能以交互方式覆盖所有工作流程。本部分内容适用于需要直接编写config.yaml文件或通过脚本进行配置的场景。

### 各工具的`use_gateway`标志位

每个工具的配置块都包含一个`use_gateway`布尔值：

```yaml
web:
  backend: firecrawl
  use_gateway: true

image_gen:
  use_gateway: true

tts:
  provider: openai
  use_gateway: true

browser:
  cloud_provider: browser-use
  use_gateway: true
```

优先级规则：当 `use_gateway: true` 时，无论 `.env` 文件中是否存在直接配置键，都会通过 Nous 进行路由处理。而当 `use_gateway: false`（或未设置该参数）时，系统会优先使用现有的直接配置键；只有在没有此类配置时，才会回退到使用网关。 

### 禁用网关功能

```yaml
web:
  use_gateway: false   # Hermes now uses FIRECRAWL_API_KEY from .env
```

当您选择非网关类型的提供者时，`hermes tools` 会自动清除该标志，因此这种情况通常不会发生在您身上。

### 自托管网关（高级用法）

正在运行自定义的 Nos 兼容网关？可在 `~/.hermes/.env` 文件中覆盖端点设置：

```bash
TOOL_GATEWAY_DOMAIN=your-domain.example.com
TOOL_GATEWAY_SCHEME=https
TOOL_GATEWAY_USER_TOKEN=your-token        # normally auto-populated from Portal login
FIRECRAWL_GATEWAY_URL=https://...         # override one endpoint specifically
```

这些设置项专为自定义基础设施环境（企业级部署、开发环境）设计，普通订阅用户无需进行配置。

## 常见问题

### 它支持 Telegram / Discord 及其他消息传递渠道吗？

支持。Tool Gateway 运行在工具执行层，而非 CLI 层。任何能够调用工具的接口——无论是 CLI、Telegram、Discord、Slack、IRC、Teams、API 服务器，还是其他任何方式——都能透明地享受到其功能。

### 如果我的订阅到期了会怎样？

通过该网关调用的工具将无法正常使用，直到您续订订阅或通过 `hermes tools` 更换为直接 API 密钥。Hermes 会显示明确的错误提示，指引您前往相关管理页面处理。

### 我可以查看每款工具的使用情况或费用吗？

可以——[Nous Portal 控制面板](https://portal.nousresearch.com) 可以按工具分类展示使用数据，帮助您了解费用产生的原因。

### Modal（无服务器终端）包含在内吗？

Modal 是通过 Nous 订阅提供的**可选附加组件**，并不属于默认的 Tool Gateway 套装。如果您需要用于远程 Shell 执行的沙箱环境，可以通过 `hermes setup terminal` 或直接在 `config.yaml` 中进行配置。

### 启用网关后需要删除现有的 API 密钥吗？

无需删除——请将它们保留在 `.env` 文件中。当 `use_gateway: true` 时，Hermes 会跳过直接使用的密钥，转而通过网关调用工具。若将该参数改回 `false`，您的密钥又会重新成为调用来源。因此，该网关并不会造成使用锁定。
