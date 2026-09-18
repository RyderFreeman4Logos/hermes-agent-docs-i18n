---
title: "Nous Tool Gateway"
description: "One subscription, every tool. Web search, image generation, TTS, and cloud browsers — all routed through Nous Portal with no extra API keys."
sidebar_label: "Tool Gateway"
sidebar_position: 2
---

# Nous 工具网关

**仅需一份订阅，即可使用所有内置工具。**

每份付费的 [Nous Portal](https://portal.nousresearch.com) 订阅都包含工具网关功能。该网关能够通过 Nous 已经部署的基础设施来路由 Hermes 的各类工具调用——包括网页搜索、图像生成、文本转语音以及云浏览器自动化功能——因此您无需再分别注册 Firecrawl、FAL、OpenAI、Browser Use 或其他任何服务，即可让您的智能体发挥最大效用。

<div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap', margin: '1.5rem 0'}}>
  <a href="https://portal.nousresearch.com/manage-subscription" style={{background: 'var(--ifm-color-primary)', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '6px', textDecoration: 'none', fontWeight: 'bold'}}>开始订阅或管理订阅 →</a>
</div>

## 包含内容

| | 工具 | 功能亮点 |
|---|---|---|
| 🔍 | **网页搜索与内容提取** | 基于 Firecrawl 实现的代理级网页搜索及整页内容提取功能。无需担心速率限制——网关会自动处理扩展需求。 |
| 🎨 | **图像生成** | 通过一个接口即可调用九种模型：**FLUX 2 Klein 9B**、**FLUX 2 Pro**、**Z-Image Turbo**、**Nano Banana Pro**（Gemini 3 Pro Image）、**GPT Image 1.5**、**GPT Image 2**、**Ideogram V3**、**Recraft V4 Pro**、**Qwen Image**。可通过参数指定生成模型，也可让 Hermes 默认使用 FLUX 2 Klein。 |
| 🔊 | **文本转语音** | 集成了 OpenAI TTS 语音资源，可直接在 `text_to_speech` 工具中使用。可用于向 Telegram 发送语音消息、为流程生成音频，或是为任何内容添加旁白。 |
| 🌐 | **云浏览器自动化** | 通过 Browser Use 功能实现无头 Chromium 浏览器会话。提供 `browser_navigate`、`browser_click`、`browser_type`、`browser_vision` 等代理操作所需的基础功能，且无需注册 Browserbase 账户。 |

以上四项功能均采用按使用量计费模式，费用将从您的 Nous 订阅账户中扣除。您可以根据需求自由组合使用——例如让网关同时处理网页搜索和图像生成任务，而文本转语音则继续使用自己的 ElevenLabs 密钥；或者将所有功能统一通过 Nous 来处理。

## 为何需要它

要打造一个真正能“执行任务”的代理，往往需要整合5种以上的 API 订阅服务，每一种都有独立的注册流程、速率限制、计费方式及特殊要求。而该网关将这些复杂服务整合到一个账户中，大幅简化了管理流程。

- **一张账单**。只需向 Nous 支付费用，其余工作由我们处理。
- **一次注册**。无需管理 Firecrawl、FAL、浏览器使用权限或 OpenAI 音频账户。
- **一把密钥**。您的 Nous Portal OAuth 即可覆盖所有工具。
- **同等质量**。采用与直接密钥方式相同的后端技术——仅由我们提供界面支持。

您随时可以按需为不同工具单独配置密钥。该网关并非束缚，而是一条快捷路径。

## 开始使用

共有三种接入方式——请选择最适合您当前需求的方案：

```bash
hermes setup --portal     # Fresh install: Nous OAuth + set Nous as provider + turn on the Tool Gateway in one go
```

```bash
hermes model              # Switch your inference provider to Nous Portal — Hermes then offers to turn on the gateway for all tools
```

```bash
hermes tools              # Enable the gateway per-tool — pick "Nous Subscription" for any tool you want
```

`hermes setup --portal`与`hermes model`属于一次性设置路径：只需登录一次，即可选择将所有工具切换至网关模式。而`hermes tools`则是按需启用路径——你可以逐个开启自己需要的工具。

**无需先进行登录。** 使用`hermes tools`时，即便你从未登录过Nous Portal，由Nous管理的后端服务（网页搜索、图像处理、视频处理、文本转语音、浏览器功能）也会始终显示在列表中。选中某项后，若你尚未完成身份验证，Hermes会立即引导你登录Portal——无需事先运行`hermes model`。如果你的Nous OAuth认证已处于激活状态，选中对应后端即可立即启用，无需额外提示。此路径仅负责登录并开启你所选择的单个工具——它不会切换推理提供方，也不会要求你为其他工具启用网关模式。

随时可查看当前处于激活状态的工具：

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

工具网关是一项**需付费订阅**的功能。免费版的Nous账户虽然可以使用Portal进行推理，但不包含托管工具——请[升级您的套餐](https://portal.nousresearch.com/manage-subscription)以启用网关功能。

部分账户还可享受**免费工具池**服务——即在无需付费订阅的情况下，也可使用少量托管工具进行网关调用。当有可用免费工具池时，系统会在首次使用时显示相关提示，让您立即选择并开始使用这些托管工具。

## 启用检查清单

选择某个Nous模型（`hermes model`）后，系统会针对该模型提供一份网关后端的选择检查清单。其行为会尊重您现有的设置：

- 您明确指定使用其他后端的工具（例如 `web.backend: searxng`、`browser.cloud_provider: camofox`）**不会出现在列表中**——这样可避免您的选择被意外覆盖。
- 仅通过环境变量配置的工具（例如 `SEARXNG_URL`、`CAMOFOX_URL`）会以**未勾选**的状态出现，并标注为使用您自己的后端。
- 仅真正未进行任何配置的工具才会默认处于已勾选状态。
- 拒绝设置会永久生效：如果您提交检查清单时未勾选某个工具，后续更换Nous模型时该工具仍不会被自动勾选（相关记录存储在 `config.yaml` 的 `tool_gateway_declined_tools` 中；之后若重新勾选，则可取消拒绝状态）。

## 自由组合

网关功能是针对单个工具的，您只需为需要的工具开启该功能即可。

- **通过 Nous 使用所有工具**——最为便捷；只需一个订阅即可搞定。  
- **适用于网页与图片的网关，可自行接入 TTS 服务**——保留您使用的 ElevenLabs 语音，其余工作由 Nous 处理。  
- **仅适用于那些没有对应密钥的工具**——比如“我已经购买了 Browserbase 的服务，但不想创建 Firecrawl 账户”，这种情况也能完美适用。  

随时可通过以下方式切换工具：

```bash
hermes tools          # Interactive picker for each tool category
```

选择相应的工具，将提供商设置为**Nous Subscription**（或您选择的任何直接提供商）。无需编辑任何配置。如果您尚未登录 Nous Portal，选择**Nous Subscription**后会直接跳转至 Portal 登录页面——无需先通过 `hermes model` 进行身份验证。

## 使用单个图像模型

为追求速度，图像生成默认使用 FLUX 2 Klein 9B 模型。如需针对每次调用进行自定义设置，可向 `image_generate` 工具传递模型 ID：

| 模型 | ID | 最佳适用场景 |
|---|---|---|
| FLUX 2 Klein 9B | `fal-ai/flux-2/klein/9b` | 速度较快，适合日常使用 |
| FLUX 2 Pro | `fal-ai/flux-2-pro` | 更高精度的 FLUX 模型 |
| Z-Image Turbo | `fal-ai/z-image/turbo` | 具有独特风格且生成速度快 |
| Nano Banana Pro | `fal-ai/nano-banana-pro` | 类似 Google Gemini 3 Pro 的图像生成能力 |
| GPT Image 1.5 | `fal-ai/gpt-image-1.5` | OpenAI 图像生成，支持文本转图像 |
| GPT Image 2 | `fal-ai/gpt-image-2` | OpenAI 最新版本模型 |
| Ideogram V3 | `fal-ai/ideogram/v3` | 能很好地遵循提示词要求，且擅长处理排版 |
| Recraft V4 Pro | `fal-ai/recraft/v4/pro/text-to-image` | 适合生成矢量风格图像，用于平面设计 |
| Qwen Image | `fal-ai/qwen-image` | 阿里巴巴推出的多模态模型 |

该列表会不断更新——访问 `hermes tools` → Image Generation 即可查看最新的模型列表。

---

## 配置参考

大多数用户无需触碰此部分——`hermes model` 和 `hermes tools` 已能支持所有交互式工作流程。本部分内容适用于直接编写 config.yaml 文件或通过脚本进行设置。

### 每个工具类别仅设置一个选择键

每个工具类别都包含一个由 `hermes tools` 选择器（或桌面 GUI）生成的供应商选择键。若选择 **Nous Subscription** 选项，该键的值为 `nous`，这样该类别的内容就会通过托管式的 Tool Gateway 进行处理；而若选择自持密钥选项，则该键的值为相应的供应商名称（如 `fal`、`openai`、`firecrawl`、`browser-use` 等），此时内容将直接使用您自己的凭证进行传输。

```yaml
web:
  backend: nous          # web search/extract via the Tool Gateway

image_gen:
  provider: nous         # image generation via the Tool Gateway

tts:
  provider: nous         # TTS via the Tool Gateway

stt:
  provider: nous         # speech-to-text via the Tool Gateway

browser:
  cloud_provider: nous   # cloud browser via the Tool Gateway
```

运行时**始终会使用已存储的配置选项**——凭据的存在状况绝不会影响类别的选择或路由方式。若 `.env` 文件中存在 `FAL_KEY`，则该键会被忽略，此时即使设置了 `image_gen.provider: nous` 也是如此；相反，若设置了 `image_gen.provider: fal` 但未定义 `FAL_KEY`，系统会直接抛出明确的错误，而不会悄悄回退到默认网关。

```
image_gen is configured to use fal (set via hermes tools), but FAL_KEY is not set. Run 'hermes tools' to change it.
```

那些**从未配置过**的类别（即从未设置过任何选择键）会像之前一样，自动从现有的凭证中检测对应配置。但一旦已设置了选择键，向 `.env` 文件中添加新键并不会改变路由规则——唯有通过 `hermes tools` 命令或修改选择键才能实现更改。

### 恢复使用自定义键

```bash
hermes tools    # pick the tool → choose a direct provider (e.g. Firecrawl)
```

或者直接设置选择键：

```yaml
web:
  backend: firecrawl   # Hermes now uses FIRECRAWL_API_KEY from .env
```

### 旧版 `use_gateway` 标志（已废弃）

早期版本的 Hermes 使用针对每个工具的 `use_gateway: true` 布尔值来指定通过网关传输请求。该标志属于**旧版本功能**：如今已不再被使用，且 `hermes tools` 选择器在重写配置时也会将其从对应类别的配置中移除。那些仍包含 `use_gateway: true` 的旧配置在读取时会被视为选择了 `nous` 模式，因此现有设置依然可以正常运行。请勿在新配置中设置 `use_gateway` —— 应直接在 `hermes tools` 中选择相应的服务提供商。

### 自托管网关（高级功能）

正在运行兼容 Nous 协议的自建网关？可在 `~/.hermes/.env` 文件中覆盖端点设置：

```bash
TOOL_GATEWAY_DOMAIN=your-domain.example.com
TOOL_GATEWAY_SCHEME=https
TOOL_GATEWAY_USER_TOKEN=your-token        # normally auto-populated from Portal login
FIRECRAWL_GATEWAY_URL=https://...         # override one endpoint specifically
TOOL_GATEWAY_URL=http://127.0.0.1:3009    # pin the shared managed origin exactly
CONNECTOR_GATEWAY_URL=http://127.0.0.1:3009 # pin the connectors origin exactly
```

每个主机的名称均为 `{label}-gateway.<domain>`，`TOOL_GATEWAY_DOMAIN` / `TOOL_GATEWAY_SCHEME` 会统一处理**所有**此类主机；而 `{LABEL}_GATEWAY_URL` 则可直接指定某个特定主机，无需再进行推导：

- `{vendor}-gateway.<domain>` —— 针对不同供应商的直通配置（如 Firecrawl、BFL 等）。
- `tool-gateway.<domain>` —— 共享的管理型源端：包括部署在网关本身的供应商服务以及媒体上传功能。
- `connector-gateway.<domain>` —— 连接器 API（`/v1/connectors/*`），属于独立部署的组件。详情请参阅 [工具搜索 → 连接器](./tool-search.md#connectors-remote-tools)。

这些配置项专为自定义基础设施环境（企业级部署、开发环境）设计，普通订阅用户无需进行设置。

## 常见问题

### 它是否支持 Telegram / Discord 及其他消息传递网关？

是的。Tool Gateway 运行在工具执行层，而非 CLI 层。任何能够调用工具的接口——无论是 CLI、Telegram、Discord、Slack、IRC、Teams、API 服务器，还是其他任何方式——都能透明地从中受益。

### 如果我的订阅到期会怎样？

通过该网关路由的工具将会停止运行，直到您续订订阅或通过 `hermes tools` 直接输入 API 密钥。Hermes 会显示明确的错误提示，指引您前往相关门户处理。

### 我可以查看每款工具的使用情况或费用吗？

可以——[Nous Portal 控制面板](https://portal.nousresearch.com) 可按工具分类展示使用数据，帮助您了解账单产生的原因。

### 是否包含 Modal（无服务器终端）功能？

Modal 是通过 Nous 订阅服务提供的**可选附加组件**，并不包含在默认的 Tool Gateway 套装中。如果您需要用于远程沙箱环境中的 Shell 执行功能，可通过 `hermes setup terminal` 命令进行配置，或直接在 `config.yaml` 文件中进行设置。

### 启用该网关后需要删除现有的 API 密钥吗？

无需删除——只需将它们保留在 `.env` 文件中即可。当某个工具的来源被设置为 **Nous 订阅服务** 时，该工具对应的直接密钥将会被自动忽略。您只需在 `hermes tools` 命令中重新选择对应的直接服务提供商，您的密钥就会再次生效。因此，该网关并不会造成使用绑定。
