---
sidebar_position: 1
title: "Nous Portal"
description: "One subscription, 300+ frontier models, the Tool Gateway, and Nous Chat — the recommended way to run Hermes Agent"
---

# Nous Portal

[Nous Portal](https://portal.nousresearch.com) 是 Nous Research 提供的统一订阅入口，也是**运行 Hermes Agent 的推荐方式**。通过一次 OAuth 登录，即可替代以往需要在每个模型实验室、搜索 API、图像生成工具以及浏览器提供商之间手动配置多个独立账户、API 密钥及计费关系的繁琐流程。

如果您只能花时间设置一件事，那就选择它——这是最快捷的路径：

```bash
hermes setup --portal
```

这条命令可同时启动Portal的OAuth认证流程、让你选择合适的Nous模型、在`config.yaml`中设置Nous作为推理提供方，并开启工具网关。执行完成后，你即可立即使用`hermes chat`。

尚未订阅？请访问[portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription)完成注册，随后再回来运行上述命令。

## 订阅包含哪些服务

### 300多种前沿模型，统一计费

Portal会代理来自整个生态系统的精选智能体模型目录——所有费用均从你的Nous订阅账户中扣除，无需为每个实验室单独管理额度。

| 品牌 | 模型 |
|------|------|
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
| **腾讯** | Hunyuan 3 Preview |
| **小米** | MiMo V2.5 Pro |
| **StepFun** | Step 3.5 Flash |
| **Hermes** | Hermes-4-70B、Hermes-4-405B（适用于聊天，详见下方[关于Hermes 4的说明](#a-note-on-hermes-4)） |
| **+ 其他模型** | 还有280多种模型，涵盖全部前沿智能体模型 |

底层通过OpenRouter进行路由，因此模型可用性和故障切换机制与使用OpenRouter密钥时一致——只是费用从你的Nous订阅中扣除。你可以在会话进行中通过`/model`指令在代码处理用Claude Sonnet 4.6和需要长上下文处理的Gemini 3 Pro之间切换，无需重新输入凭证、充值，也不会出现余额不足的意外情况。

### Nous工具网关

同一订阅还可解锁[工具网关](/user-guide/features/tool-gateway)，它可将Hermes Agent的工具调用通过Nous管理的基础设施进行路由。五种后端，一个登录账号即可：

| 工具 | 合作方 | 功能说明 |
|------|--------|----------|
| **网页搜索与内容提取** | Firecrawl | 提供代理级搜索和整页内容提取功能，无需Firecrawl API密钥，也无需担心速率限制问题。 |
| **图像生成** | FAL | 通过一个接口即可使用九种模型：FLUX 2 Klein 9B、FLUX 2 Pro、Z-Image Turbo、Nano Banana Pro（Gemini 3 Pro图像模型）、GPT Image 1.5、GPT Image 2、Ideogram V3、Recraft V4 Pro、Qwen Image。 |
| **文本转语音** | OpenAI TTS | 支持高质量文本转语音功能，无需单独的OpenAI密钥，还可在各类消息平台中使用[语音模式](/user-guide/features/voice-mode)。 |
| **云浏览器自动化** | Browser Use | 为`browser_navigate`、`browser_click`、`browser_type`、`browser_vision`等操作提供无头Chromium会话，无需注册Browserbase账户。 |
| **云终端沙箱** | Modal | 提供无服务器终端沙箱环境，可用于代码执行（可选附加功能）。 |

如果没有工具网关，要使用这些功能就需要分别注册Firecrawl、FAL、Browser Use账号，获取OpenAI密钥和Modal账号——需要五次独立注册、五个独立控制面板以及五次单独充值流程。而通过工具网关，所有功能均可通过同一订阅统一处理。

你也可以仅启用特定的工具网关功能（例如仅使用网页搜索，而不使用图像生成）——详情请参见下方的[将工具网关与自定义后端结合使用](#mixing-the-gateway-with-your-own-backends)。

### Nous Chat

你的Portal账户还包含[Nous Research的网站聊天界面](https://chat.nousresearch.com)，该界面拥有与Portal相同的模型目录。当你不在终端前，或需要进行非智能体对话时，这个功能非常实用。

### 无需在配置文件中存储凭证

由于所有操作都通过一次OAuth认证的Portal会话完成，因此你无需创建包含大量长期有效API密钥的`.env`文件。磁盘上仅存在`~/.hermes/auth.json`中的刷新令牌作为唯一凭证，Hermes会根据每次请求从中生成短期的JWT令牌——详情请参见下方的[令牌处理机制](#token-handling)。

### 跨平台一致性

在[原生Windows系统](/user-guide/windows-native)上，为每个工具单独配置API密钥是最大的麻烦——要在Windows上安装Firecrawl、FAL、Browser Use账号以及OpenAI密钥，是搭建实用智能体的最繁琐步骤。而Portal订阅则解决了这一问题：一个OAuth认证即可同时管理模型和所有工具网关功能，因此Windows用户无需手动配置四种后端，就能获得与macOS/Linux相同的体验。

## 关于Hermes 4的说明

Nous Research自研的**Hermes 4系列模型**（Hermes-4-70B、Hermes-4-405B）可通过Portal以大幅折扣的价格获取。这些是**具备混合推理能力的前沿聊天模型**，在数学、科学、指令遵循、模式匹配、角色扮演以及长文写作方面表现优异。

不过，**不建议在Hermes Agent中使用它们**。Hermes 4是为聊天和推理任务优化的，而智能体需要的是快速连续的工具调用机制。你可以将它们用于[Nous Chat](https://chat.nousresearch.com)、研究工作，或通过[订阅代理功能](/user-guide/features/subscription-proxy)与其他工具结合使用——但若需用于智能体功能，建议从模型目录中选择其他前沿智能体模型。

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

该操作可一次性完成全部设置流程：

1. 打开浏览器，访问 portal.nousresearch.com 进行 OAuth 登录；
2. 将刷新令牌保存至 `~/.hermes/auth.json` 文件中；
3. 允许您从精选列表中选择一款 Nous 模型（或直接保留当前使用的模型）；
4. 在您选定模型后，会将 Nous 设置为 `~/.hermes/config.yaml` 中的推理提供方；
5. 启用工具网关功能（包括网页处理、图像处理、文本转语音以及浏览器路由功能）；
6. 最后将您带回终端界面，即可开始使用 `hermes chat`。

如果您尚未订阅服务，请先访问 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription) 进行注册。

### 已有安装——在其他提供方旁添加 Portal

如果您已经使用 OpenRouter、Anthropic 或其他任何提供方配置好了 Hermes，且希望在此基础上再添加 Portal：

```bash
hermes model
# pick "Nous Portal" from the provider list
# browser opens, sign in, done
```

您现有的提供者配置将保持不变。您可以在会话进行中通过 `/model` 命令在它们之间切换，或在不同会话之间使用 `hermes model` 命令切换——此时 Portal 会成为您可用的提供者之一，而非唯一的提供者。

### 无界面模式 / SSH / 远程设置

OAuth 需要浏览器，但回调处理会在运行 Hermes 的机器上执行。对于远程主机，请参考 [通过 SSH/远程主机进行 OAuth 认证](/guides/oauth-over-ssh)——Portal 与其他基于 OAuth 的提供者采用相同的配置方式（如 `ssh -L` 端口转发，以及针对 Cloud Shell / Codespaces 等仅支持浏览器的环境使用的 `--manual-paste` 参数）。

### 配置文件设置

如果您使用 [Hermes 配置文件](/user-guide/profiles)，Portal 的刷新令牌会通过共享令牌存储机制自动同步到所有配置文件中。只需在任何一个配置文件中登录一次，其余配置文件便会自动获取该令牌——无需为每个配置文件重复执行 OAuth 认证流程。

## 日常使用 Portal

### 查看已连接的组件

```bash
hermes portal            # log in to Nous Portal + set it up (one-shot onboarding)
hermes portal info       # login status, subscription info, model + gateway routing
hermes portal status     # alias for `portal info`
hermes portal tools      # detailed Tool Gateway catalog with per-tool routing
hermes portal open       # open the subscription management page in your browser
```

`hermes portal`（不带子命令）是 `hermes auth add nous --type oauth` 的可读别名——该命令可帮助您登录，让您选择合适的 Nous 模型，将 Nous 设置为推理提供方，同时还会提供工具网关的启用选项（其功能与 `hermes setup --portal` 完全相同，且推理流程也与首次快速设置时一致）。

`hermes portal info` 则能为您提供高级概览信息：

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

如果您已拥有某个账户（例如 Browserbase），同时希望在通过 Nous 进行网络搜索和图像生成时继续使用该账户，这是完全支持的。您可以使用 `hermes tools` 为不同工具指定各自对应的后端。

```bash
hermes tools
# → Web search       → "Nous Subscription"
# → Image generation → "Nous Subscription"
# → Browser          → "Browserbase"  (your existing key)
# → TTS              → "Nous Subscription"
```

工具网关是针对每个工具单独启用的，而非全有或全无的模式。无论您是否已登录 Nous Portal，管理型后端都会显示在 `hermes tools` 中——如果您在身份验证前选择了“Nous Subscription”，Hermes 会直接在当前页面进行 Portal 登录（这不会更改您的推理提供方，也不会影响其他工具）。如需查看针对每个工具的完整配置矩阵，请参阅[工具网关文档](/user-guide/features/tool-gateway)。

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

工具网关的设置位于各对应工具的板块下：

```yaml
web:
  backend: nous       # web search/extract routes through Tool Gateway

image_gen:
  provider: nous

tts:
  provider: nous

browser:
  backend: nous
```

OAuth 刷新令牌会单独存储在 `~/.hermes/auth.json` 文件中（而非 `config.yaml` 中——按照设计，凭证与配置是分开存放的）。

## 令牌处理机制

Hermes 会在每次推理调用时，基于您存储的 Portal 刷新令牌生成一个短效的 JWT，而不会重复使用长期有效的 API 密钥。整个令牌生命周期都是全自动管理的——包括刷新、重新生成令牌，以及针对临时性 401 错误的自动重试——您无需手动干预。

如果 Portal 终止了该刷新令牌的有效性（如密码更改、手动撤销或会话过期），无效的刷新令牌会被**在本地隔离**，这样 Hermes 就不会再使用它，您也就不会看到一连串相同的 401 错误。下一次调用时，系统会明确提示“需要重新认证”。您可以运行 `hermes auth add nous` 重新登录；一旦下次登录成功，该隔离状态就会被解除。

## 故障排除

### `hermes portal info` 显示“未登录”

这可能是由于您尚未完成 OAuth 认证流程，或者您的刷新令牌已被清除。请执行以下操作：

```bash
hermes portal
```

或者使用 `hermes model` 命令并重新选择 Nous Portal。

### 在会话进行中收到“需要重新认证”的提示

您的 Portal 刷新令牌已失效（可能是由于密码更改、手动撤销或会话过期）。请运行 `hermes auth add nous`，后续请求将使用新的凭证。成功重新登录后，旧令牌的任何限制都会自动解除。

### 希望使用 Portal 未提供的特定提供方模型

Portal 通过 OpenRouter 进行代理，因此 OpenRouter 支持的任何模型通常都可以使用。如果某个特定模型未出现在 `/model` 目录中，可直接尝试使用 OpenRouter 风格的标识符：

```bash
/model anthropic/claude-opus-4.6
```

如果某个模型确实不存在，请[提交问题](https://github.com/NousResearch/hermes-agent/issues)——我们会将 Portal 的模型目录同步至 Hermes，而出现缺失通常意味着路由配置需要更新。

### 为何我的 Portal 账户中看不到账单？

请先执行 `hermes portal info` 命令——如果显示您使用的是其他提供商（例如显示“Model: currently openrouter”而非“using Nous as inference provider”），则表示您的本地配置出现了偏差。请运行 `hermes model` 并选择 Nous Portal，后续请求就会通过您的订阅服务进行路由。

## 相关内容

- **[工具网关](/user-guide/features/tool-gateway)** — 详细介绍各类网关工具、各工具的配置选项及定价信息
- **[订阅代理](/user-guide/features/subscription-proxy)** — 允许在非 Hermes 工具（其他智能体、脚本、第三方客户端）中使用 Portal 订阅服务
- **[语音模式](/user-guide/features/voice-mode)** — 利用 Portal 的 OpenAI TTS 实现语音对话
- **[AI 提供商](/integrations/providers)** — 完整的提供商目录，方便您对比不同选项
- **[通过 SSH 进行 OAuth 认证](/guides/oauth-over-ssh)** — 支持从远程主机或仅支持浏览器的环境登录
- **[配置文件](/user-guide/profiles)** — 允许使用同一 Portal 登录账户管理多个 Hermes 配置
