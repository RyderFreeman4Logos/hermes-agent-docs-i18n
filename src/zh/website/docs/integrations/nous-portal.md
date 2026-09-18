---
sidebar_position: 1
title: "Nous Portal"
description: "One subscription, 300+ frontier models, and the Tool Gateway — the recommended way to run Hermes Agent"
---

# Nous Portal

[Nous Portal](https://portal.nousresearch.com) 是 Nous Research 提供的统一订阅入口，也是**运行 Hermes Agent 的推荐方式**。通过一次 OAuth 登录，即可替代以往需要手动为每个模型实验室、搜索 API、图像生成工具以及浏览器提供商分别配置独立账户、API 密钥和计费关系的繁琐流程。

如果您只能花时间设置一件事，那就请设置它——这是最快捷的路径：

```bash
hermes setup --portal
```

该命令可同时启动Portal OAuth认证流程、允许您选择合适的Nous模型、在`config.yaml`中将Nous设置为推理服务提供商，并开启工具网关。执行完成后，您即可立即使用`hermes chat`功能。

尚未拥有订阅账户？请访问[portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription)完成注册，随后再回来运行上述命令。

## 订阅服务包含哪些内容

### 300多种前沿模型，统一计费

Portal汇集了来自整个生态系统的精选智能体模型库——所有费用均从您的Nous订阅账户中扣除，无需为每个实验室单独计算额度。

| 品牌系列 | 模型名称 |
|--------|--------|
| **Anthropic Claude** | Opus 4.7、Opus 4.6、Sonnet 4.6、Haiku 4.5 |
| **OpenAI** | GPT-5.5、GPT-5.5 Pro、GPT-5.4 Mini、GPT-5.4 Nano、GPT-5.3 Codex |
| **Google Gemini** | Gemini 3 Pro Preview、Gemini 3 Flash Preview、Gemini 3.1 Pro Preview、Gemini 3.1 Flash Lite Preview |
| **DeepSeek** | DeepSeek V4 Pro |
| **Qwen** | Qwen3.7-Max、Qwen3.6-35B-A3B |
| **Kimi / Moonshot** | Kimi K2.6 |
| **GLM / Zhipu** | GLM-5.1 |
| **MiniMax** | MiniMax M2.7 |
| **xAI** | Grok 4.3 |
| **NVIDIA** | Nemotron-3 Super 120B-A12B |
| **Tencent** | Hunyuan 3 Preview |
| **Xiaomi** | MiMo V2.5 Pro |
| **StepFun** | Step 3.5 Flash |
| **Hermes** | Hermes-4-70B、Hermes-4-405B（支持聊天功能，详见下方说明[#a-note-on-hermes-4]） |
| **+ 其他所有模型** | 还有280多种其他模型，涵盖完整的智能体技术前沿成果 |
在底层架构中，Portal会根据不同模型特性将其路由至最合适的后端——部分模型通过OpenRouter处理，另一些则通过专用或备用提供商处理，且同一模型的路由方式可能会随时间发生变化。无论哪种情况，所有费用都会从您的Nous订阅账户中扣除。您可以在会话进行中通过`/model`指令在适用于代码处理的Claude Sonnet 4.6与适合处理长上下文内容的Gemini 3 Pro之间切换——无需新的凭证，无需充值，也不会出现余额不足的意外情况。

:::note
由于路由是针对特定模型进行的，并不总是通过OpenRouter，因此那些专为OpenRouter设计的请求扩展功能（如`provider`路由偏好设置、`session_id`粘性路由机制或顶层的`cache_control`指令）并不属于Portal的API规范范围，具体实现可能会因处理该模型的后端不同而有所差异。
:::

### Nous工具网关

同样的订阅方案还可让您使用[工具网关](/user-guide/features/tool-gateway)，该功能可通过Nous管理的基础设施来路由Hermes Agent的工具调用。仅需一次登录，即可使用五种不同的后端服务。

| 工具 | 合作伙伴 | 功能说明 |
|------|---------|----------|
| **网页搜索与内容提取** | Firecrawl | 具有代理级性能的搜索功能及全页内容提取能力。无需Firecrawl API密钥，也无需担心速率限制问题。 |
| **图像生成** | FAL | 通过一个接口即可调用九种模型：FLUX 2 Klein 9B、FLUX 2 Pro、Z-Image Turbo、Nano Banana Pro（Gemini 3 Pro Image）、GPT Image 1.5、GPT Image 2、Ideogram V3、Recraft V4 Pro以及Qwen Image。 |
| **文本转语音** | OpenAI TTS | 提供高质量的语音合成功能，且无需单独的OpenAI密钥。支持在各类消息平台上使用[语音模式](/user-guide/features/voice-mode)。 |
| **云浏览器自动化** | Browser Use | 为`browser_navigate`、`browser_click`、`browser_type`、`browser_vision`等操作提供无头Chromium会话支持。无需注册Browserbase账户。 |
| **云终端沙箱** | Modal | 提供无服务器终端沙箱环境，可用于代码执行（为可选附加功能）。 |

若不使用网关，要使用上述各项功能，则需分别注册Firecrawl、FAL、Browser Use账号，获取OpenAI密钥并注册Modal账户——共计五次独立注册、五个独立控制面板以及五套独立的充值流程。而借助网关，所有功能均可通过同一订阅服务统一处理。

您也可以仅启用特定的网关工具（例如仅使用网页搜索功能，而不使用图像生成功能）——详情请参阅下文[将网关与自定义后端结合使用](#mixing-the-gateway-with-your-own-backends)。

### 无需在配置文件中存储凭证

由于所有操作都通过同一个经过 OAuth 认证的 Portal 会话进行，因此无需存储包含大量长期有效 API 密钥的 `.env` 文件。磁盘上仅存有 `~/.hermes/auth.json` 中的刷新令牌，Hermes 会根据每次请求从中生成短期的 JWT — 详情请参见下文的[令牌处理](#token-handling)部分。

### 跨平台一致性

[原生 Windows 版](/user-guide/windows-native)在为不同工具配置 API 密钥时存在一定不便 — 从 Windows 系统安装 Firecrawl 账户、FAL 账户、Browser Use 账户以及 OpenAI 密钥，是构建实用智能体的最大障碍。而 Portal 订阅则解决了这一问题：一个 OAuth 认证即可同时覆盖模型及所有网关工具，因此 Windows 用户无需手动配置四种后端，就能获得与 macOS/Linux 相同的使用体验。

## 关于 Hermes 4 的说明

Nous Research 自主研发的**Hermes 4**系列模型（Hermes-4-70B、Hermes-4-405B）可通过 Portal 以大幅折扣的价格获取。这些属于**前沿的混合推理聊天模型**，在数学、科学、指令遵循、模式匹配、角色扮演以及长文写作方面表现优异。

不过，**不建议在 Hermes Agent 中使用它们**。Hermes 4 是为聊天和推理任务优化的，并非为智能体所依赖的快速连续调用工具的流程而设计。若需将其用于研究工作，可通过[订阅代理](/user-guide/features/subscription-proxy)与其他工具结合使用 — 但对于智能体应用，建议从模型目录中选择其他前沿的智能体模型：

```bash
/model anthropic/claude-sonnet-4.6     # best general-purpose agentic model
/model openai/gpt-5.5-pro              # strong reasoning + tool calling
/model google/gemini-3-pro-preview     # huge context window
/model deepseek/deepseek-v4-pro        # cost-effective coder
```

Portal 自带的 [模型信息页面](https://portal.nousresearch.com/info)也给出了同样的警告，因此这并非 Hermes 方面的观点，而是 Nous Research 的官方指引。

## 设置

### 新安装——仅需一条命令

```bash
hermes setup --portal
```

该流程可一次性完成全部设置：

1. 打开浏览器访问 portal.nousresearch.com 进行 OAuth 登录；
2. 将刷新令牌保存至 `~/.hermes/auth.json`；
3. 允许您从精选列表中选择 Nous 模型（或直接保留当前使用的模型）；
4. 在您选定模型后，会将 Nous 设置为 `~/.hermes/config.yaml` 中的推理提供方；
5. 启用工具网关功能（包括网页处理、图像处理、文本转语音以及浏览器路由功能）；
6. 最后将您带回终端，即可开始使用 `hermes chat`。

如果您尚未订阅，请先访问 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription) 进行注册。

### 已有安装——在其他提供方旁添加 Portal

如果您已经使用 OpenRouter、Anthropic 或其他任何提供方配置好了 Hermes，现在希望同时添加 Portal：

```bash
hermes model
# pick "Nous Portal" from the provider list
# browser opens, sign in, done
```

您现有的提供商配置将保持不变。您可以在会话进行中通过 `/model` 命令在它们之间切换，或在不同会话间使用 `hermes model` 命令切换——此时 Portal 会成为您的可用提供商之一，而非唯一的提供商。

### 无界面模式 / SSH / 远程设置

OAuth 需要浏览器，但回环回调会在运行 Hermes 的机器上执行。对于远程主机，请参考 [通过 SSH/远程主机进行 OAuth 认证](/guides/oauth-over-ssh)——Portal 与其他基于 OAuth 的提供商采用相同的配置方式（即通过 `ssh -L` 实现端口转发）。

### 配置文件设置

如果您使用 [Hermes 配置文件](/user-guide/profiles)，Portal 的刷新令牌会通过共享令牌存储自动在所有配置文件之间同步。只需在任何配置文件中登录一次，其余配置文件便会自动获取该令牌，无需为每个配置文件重复执行 OAuth 认证流程。

## 日常使用 Portal

### 查看已连接的组件

```bash
hermes portal            # log in to Nous Portal + set it up (one-shot onboarding)
hermes portal info       # login status, subscription info, model + gateway routing
hermes portal status     # alias for `portal info`
hermes portal tools      # detailed Tool Gateway catalog with per-tool routing
hermes portal open       # open the subscription management page in your browser
```

`hermes portal`（无子命令）是`hermes auth add nous --type oauth`的易读别名——该命令可帮助您登录，让您选择相应的Nous模型，将Nous设置为推理提供方，同时还会提供Tool Gateway的启用选项（其功能与`hermes setup --portal`相同，且推理流程也与首次快速设置时一致）。

`hermes portal info`则能为您提供高级概览信息：

```
  Nous Portal
  ───────────
  Auth:    ✓ logged in
  Portal:  https://portal.nousresearch.com
  Model:   ✓ using Nous as inference provider

  Tool Gateway
  ────────────
  Web search & extract  via Nous Portal
  Image generation      via Nous Portal
  Text-to-speech        via Nous Portal
  Browser automation    via Nous Portal
  Cloud terminal        not configured
```

### 切换模型

在会话进行中：

```bash
/model anthropic/claude-sonnet-4.6
/model openai/gpt-5.5-pro
/model google/gemini-3-pro-preview
```

或者打开选择器：

```bash
/model
# arrow keys, enter to select
```

在会话之外（完整的设置向导，适用于添加新的提供程序时）：

```bash
hermes model
```

### 将网关与自定义后端结合使用

如果您已拥有某个账户（例如 Browserbase），同时希望在通过 Nous 进行网络搜索和图像生成时继续使用该账户，这是完全支持的。您可以使用 `hermes tools` 为不同的工具指定各自对应的后端。

```bash
hermes tools
# → Web search       → "Nous Subscription"
# → Image generation → "Nous Subscription"
# → Browser          → "Browserbase"  (your existing key)
# → TTS              → "Nous Subscription"
```

工具网关是针对每个工具单独启用的，而非全有或全无的模式。无论您是否已登录 Nous Portal，托管后的后端都会显示在 `hermes tools` 中——如果您在身份验证前选择“Nous Subscription”，Hermes 会直接在内嵌界面中完成 Portal 登录（这不会更改您的推理提供方，也不会影响其他工具）。如需查看针对每个工具的完整配置矩阵，请参阅[工具网关文档](/user-guide/features/tool-gateway)。

### 订阅管理

您可以随时管理套餐、查看使用情况或进行升级/取消操作：

- **网页端：** [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription)
- **CLI 快捷命令：** `hermes portal open`（将在您的默认浏览器中打开同一页面）

## 配置参考

执行 `hermes setup --portal` 后，`~/.hermes/config.yaml` 的内容将如下所示：

```yaml
model:
  provider: nous
  default: anthropic/claude-sonnet-4.6     # or whatever model you picked
  base_url: https://inference-api.nousresearch.com/v1
```

工具网关的设置位于对应的工具分类下——每个类别仅有一个可选键，若在 `hermes tools`（或 `hermes setup --portal`）中选择 **Nous Subscription**，则该设置的值将为 `nous`。

```yaml
web:
  backend: nous          # web search/extract routes through Tool Gateway

image_gen:
  provider: nous

tts:
  provider: nous

browser:
  cloud_provider: nous
```

运行时始终遵循已存储的设置——当类别被设置为 `nous` 时，`.env` 文件中直接留下的 API 密钥将被忽略；此外，若选择直接提供商（例如 `image_gen.provider: fal`）却未提供对应密钥，系统会直接抛出明确错误，而不会默默地通过网关进行路由。（旧配置使用的是过时的 `use_gateway: true` 标志；该标志会被视为等同于 `nous`，但现已不再被采用。）

OAuth 刷新令牌会单独存储在 `~/.hermes/auth.json` 文件中（而非 `config.yaml` 中——出于设计考虑，凭证与配置是分开存储的）。

## 令牌处理机制

Hermes 在每次推理调用时，都会基于您存储的 Portal 刷新令牌生成一个短生命周期的 JWT，而非重复使用长期有效的 API 密钥。整个令牌生命周期管理是完全自动化的——包括刷新、重新生成令牌，以及在出现临时性 401 错误时自动重试——您无需手动干预。

此外，长时间运行的网关和仪表板进程还会运行后台保持连接机制，在令牌过期前自动进行刷新，这样处于空闲状态的智能体在每个凭证生命周期的第一次请求时，就不会因 401 错误而产生不必要的往返请求。该保持连接机制的触发频率由 Portal 实际分配的令牌有效期决定（每个有效期可触发多次），且存在上限限制：

```yaml
nous:
  keepalive_interval_seconds: 900   # upper bound on the tick; 0 disables the keepalive
```

如果 Portal 使刷新令牌失效（如密码更改、手动撤销或会话过期），该无效的刷新令牌将会**在本地被隔离**，这样 Hermes 就不会再使用它，您也就不会看到一连串相同的 401 错误。下一次调用时，系统会明确显示“需要重新认证”的提示。请运行 `hermes auth add nous` 重新登录；在下次成功登录后，该隔离状态就会解除。

## 故障排除

### `hermes portal info` 显示“未登录”

可能是因为您尚未完成 OAuth 认证流程，或者您的刷新令牌已被清除。请执行以下操作：

```bash
hermes portal
```

或者使用 `hermes model` 命令并重新选择 Nous Portal。

### 在会话进行中收到“需要重新认证”的提示

您的 Portal 刷新令牌已失效（可能是由于密码更改、手动撤销或会话过期所致）。请运行 `hermes auth add nous`，后续请求将使用新的凭证。成功重新登录后，旧令牌的任何限制都会自动解除。

### 希望使用 Portal 未提供的特定提供商模型

Portal 会将每个模型路由到合适的后端——有些通过 OpenRouter，有些则通过专有或备用提供商——因此 OpenRouter 支持的大多数模型通常都是可用的。如果某个特定模型没有出现在 `/model` 目录中，可以直接尝试使用 OpenRouter 风格的标识符：

```bash
/model anthropic/claude-opus-4.6
```

如果某个模型确实不存在，请[提交问题](https://github.com/NousResearch/hermes-agent/issues)——我们会将 Portal 的模型目录同步至 Hermes，而模型缺失通常意味着只需更新路由配置即可解决。

### 为什么我的 Portal 账户中看不到账单？

请先运行 `hermes portal info` 命令查看——如果显示您正在使用其他提供商（例如显示“Model: currently openrouter”而非“using Nous as inference provider”），则表示您的本地配置出现了偏差。此时请运行 `hermes model` 并选择 Nous Portal，后续请求就会通过您的订阅服务进行路由。

## 相关内容

- **[工具网关](/user-guide/features/tool-gateway)** — 详细了解各类网关工具、各工具的配置选项及定价信息
- **[订阅代理](/user-guide/features/subscription-proxy)** — 在非 Hermes 工具（其他智能体、脚本、第三方客户端）中调用您的 Portal 订阅服务
- **[语音模式](/user-guide/features/voice-mode)** — 利用 Portal 的 OpenAI TTS 实现语音对话
- **[AI 提供商](/integrations/providers)** — 完整的提供商目录，便于您对比不同选项
- **[通过 SSH 进行 OAuth 登录](/guides/oauth-over-ssh)** — 从远程主机或仅支持浏览器的环境中登录
- **[配置文件](/user-guide/profiles)** — 允许多个 Hermes 配置共享同一个 Portal 登录账号
