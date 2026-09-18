---
sidebar_position: 1
title: "Run Hermes Agent with Nous Portal"
description: "Start-to-finish walkthrough: subscribe, set up, switch models, enable gateway tools, and verify routing"
---

# 在 Nous Portal 上运行 Hermes Agent

本指南将全程指导您在 [Nous Portal](https://portal.nousresearch.com) 订阅环境中运行 Hermes Agent——从注册开始，到验证所有工具都能正确路由。如果您只需了解该门户的功能及订阅内容概览，请参阅 [Nous Portal 集成页面](/integrations/nous-portal)。该页面即为任务脚本。

## 先决条件

- 已安装 Hermes Agent（[快速入门](/getting-started/quickstart)）
- 在要配置的机器上准备好网页浏览器（或通过 SSH 端口转发——参见 [通过 SSH 进行 OAuth 认证](/guides/oauth-over-ssh)）
- 大约 5 分钟时间

您**无需**准备 OpenAI 密钥、Anthropic 密钥、Firecrawl 账户、FAL 账户、Browser Use 账户，或其他任何特定供应商的认证凭证。这正是该方案的优势所在。

## 1. 获取订阅资格

打开 [portal.nousresearch.com/manage-subscription](https://portal.nousresearch.com/manage-subscription) 进行注册，并选择合适的套餐。

已经订阅？可直接跳至第 2 步。

## 2. 执行一次性设置

```bash
hermes setup --portal
```

这条命令可完成五项操作：

1. 打开浏览器，跳转至 portal.nousresearch.com 进行 OAuth 登录；
2. 将刷新令牌保存至 `~/.hermes/auth.json` 文件中；
3. 在 `~/.hermes/config.yaml` 中设置 `model.provider: nous`；
4. 选择默认的智能体模型（如 `anthropic/claude-sonnet-4.6` 或类似版本）；
5. 启用用于网络搜索、图像生成、文本转语音以及浏览器自动化的工具网关。

操作完成后，您将返回终端，随时可以开始对话。

### 如果我是通过 SSH 连接到服务器怎么办？

OAuth 功能需要浏览器，但回调处理会在运行 Hermes 的机器上执行。此时有两种解决方案：

```bash
# Option A: SSH port forwarding (preferred)
ssh -N -L 8642:127.0.0.1:8642 user@remote-host    # in a local terminal
hermes setup --portal                              # on the remote, open the printed URL in your local browser

# Option B: device-code login (works from Cloud Shell, Codespaces, EC2 Instance Connect)
hermes auth add nous --type oauth
# Then re-run `hermes setup --portal` to wire the provider + gateway
```

如需包含 ProxyJump 链路、mosh/tmux 以及 ControlMaster 使用中的注意事项在内的完整操作指南，请参阅 [通过 SSH/远程主机实现 OAuth](/guides/oauth-over-ssh)。

## 3. 验证功能是否正常运行

```bash
hermes portal info
```

您应该会看到：

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
```

如果有任何一行显示的内容并非“via Nous Portal”，或者认证行显示“未登录”，请跳转至下方的[故障排除](#troubleshooting)部分。

## 4. 进行首次对话测试

```bash
hermes chat
```

试试既能锻炼模型能力，又能测试工具网关功能的操作吧：

```
Hey, search the web for "Hermes Agent release notes" and summarize the top 3 hits.
```

您应该会看到Hermes通过网关调用基于Firecrawl的`web_search`功能，并返回搜索结果摘要。如果搜索成功且返回的内容合乎逻辑，那就表示一切就绪——此时Portal已实现端到端的连接。

## 5. 选择您实际需要的模型

虽然可以通过`hermes setup --portal`在设置阶段选定模型，但订阅服务的核心优势在于能够访问完整的模型库——您还可以在会话进行过程中随时使用`/model`命令切换模型：

```bash
/model anthropic/claude-sonnet-4.6     # best general-purpose agentic
/model openai/gpt-5.4                  # strong reasoning + tool calling
/model google/gemini-2.5-pro           # huge context window
/model deepseek/deepseek-v3.2          # cost-effective coder
/model anthropic/claude-opus-4.6       # heavyweight for hard problems
```

或者点击选择器进行浏览：

```bash
/model
```

永久选择其他默认值：

```bash
# in your terminal, outside any session
hermes config set model.default anthropic/claude-sonnet-4.6
```

### 不建议在智能体任务中使用 Hermes-4

Portal 上以极低价格提供了 Hermes-4-70B 和 Hermes-4-405B 模型，但它们属于**聊天/推理模型**，并未针对工具调用进行优化。因此它们在处理多步骤的智能体循环任务时会表现不佳。若需用于对话或研究工作，可通过 [订阅代理](/user-guide/features/subscription-proxy) 将非智能体工具的功能接入。对于 Hermes Agent 本身，则建议继续使用上述先进的智能体模型。

Portal 自带的 [信息页面](https://portal.nousresearch.com/info) 也发布了相同警告——这是 Nous 的官方指引，而非仅代表 Hermes 方面的观点。

## 6. （可选）自定义工具网关路由

网关功能是针对单个工具可选启用的，并非全有或全无。如果您已拥有 Browserbase 账户，同时希望在通过 Nous 执行网页搜索和图像生成任务时继续使用该账户，这是完全支持的：

```bash
hermes tools
# → Web search       → "Nous Subscription"     (recommended)
# → Image generation → "Nous Subscription"     (recommended)
# → Browser          → "Browserbase"           (your existing key)
# → TTS              → "Nous Subscription"     (recommended)
```

即便您尚未登录 Nous Portal，这些行也会出现在 `hermes tools` 中——如果您在未处于活跃会话状态的情况下选择“Nous Subscription”，Hermes 会直接启动 Portal 登录流程（而不会更改您的推理提供商或其他工具）。

```bash
hermes portal tools
```

您将看到针对不同工具的路由方式——通过订阅服务路由的工具会显示“via Nous Portal”，而使用您自己密钥的工具则会显示对应合作伙伴的名称（如 `browserbase`、`firecrawl` 等）。

## 7. （可选）启用语音模式

由于 Tool Gateway 内置了 OpenAI TTS，因此[语音模式](/user-guide/features/voice-mode)无需额外的 OpenAI 密钥即可使用：

```bash
hermes setup tts
# → pick "Nous Subscription" for TTS
# → pick a speech-to-text backend (local faster-whisper is free, no setup)
```

随后，在任何消息平台会话中（如 Telegram、Discord、Signal 等）发送语音消息，Hermes 将自动对其进行转录、生成回复，并以合成的语音形式予以回应——所有这些功能均可在您的 Portal 订阅套餐的支持下实现。

## 8. （可选）Cron 任务与全天候工作流

Portal 订阅套餐对于 [Cron 任务](/user-guide/features/cron)和[批量处理](/user-guide/features/batch-processing)的支持方式与交互式聊天相同：OAuth 刷新令牌会自动重复使用。无需额外设置，只需安排好 Cron 任务，相关费用就会从您的订阅套餐中扣除。

```bash
hermes cron create "0 9 * * *" \
  "Search the web for top AI news and summarize the 5 most important stories" \
  --name "Daily AI news"
```

该定时任务会自动运行，通过您的 Portal 订阅服务来调用模型、进行网络搜索并生成摘要。

## 配置文件与多用户设置

如果您使用 [Hermes 配置文件](/user-guide/profiles)（例如为每个项目单独配置），Portal 刷新令牌会通过共享的令牌存储库自动在所有配置文件之间共享。只需在任何一个配置文件中登录一次，其余配置文件便会自动获取该令牌。

对于多人共用同一台机器的团队环境，每位用户都应拥有独立的 Portal 账户——各自的家目录中会保存独立的 `~/.hermes/auth.json` 文件——因此不会在用户之间共享令牌。这才是合理的设置方式。

## 故障排除

### 执行 `hermes setup --portal` 后，`hermes portal info` 显示“未登录”

说明 OAuth 流程尚未完成。请重新运行该命令：

```bash
hermes portal
```

如果您的浏览器无法打开或回调失败，很可能是您正在使用远程/无头主机——请参阅[通过 SSH 实现 OAuth](/guides/oauth-over-ssh)，了解端口转发的相关解决方案。

### 显示“Model: currently openrouter”（或其他某个提供商）而非“using Nous as inference provider”

这说明您的本地配置出现了偏差。虽然 OAuth 认证成功，但`model.provider`仍指向了其他提供商。解决方法如下：

```bash
hermes config set model.provider nous
```

或者以交互方式操作：

```bash
hermes model
# pick Nous Portal
```

请使用 `hermes portal info` 命令进行重新验证。

### 工具网关中显示合作伙伴名称而非“通过 Nous Portal”

各工具的独立配置正在覆盖网关设置。请执行以下命令：

```bash
hermes tools
# pick "Nous Subscription" for any tool you want gateway-routed
```

有些用户会故意混用配置——例如通过 Nous 路由网页请求，但却使用自己专属的 Browserbase 密钥来处理浏览器相关操作。如果是出于刻意为之的目的，那就无需干预；若非如此，此命令即可解决问题。

### 会话进行中出现“需要重新认证”的提示

您的门户刷新令牌已失效（可能是由于密码更改、手动撤销或会话过期所致）。该令牌现已被本地隔离，以防止 Hermes 不断重复使用它。只需再次登录即可：

```bash
hermes auth add nous
```

一旦成功重新登录，隔离状态将自动解除。

### 我想要的模型不在 `/model` 选择器中

Portal 的模型目录包含了 OpenRouter 提供的 300 多种模型，以及通过专用供应商或次要供应商提供的模型。如果某个模型无法显示，可以尝试直接输入符合 OpenRouter 格式的模型标识符：

```bash
/model anthropic/claude-opus-4.6
/model openai/o1-2025-12-17
```

如果某个模型确实无法使用，请[提交问题](https://github.com/NousResearch/hermes-agent/issues)——大多数情况都是路由配置的问题，我们可以通过更新配置来解决。

### 为何我的门户账户中看不到计费信息？

运行 `hermes portal info` 命令即可查看当前请求究竟是通过该门户处理的，还是通过其他提供商处理的。常见原因包括：

- `model.provider` 的值被设置为 `openrouter`/`anthropic` 等而非 `nous`
- OAuth刷新失败，系统自动切换到了其他已配置的提供商
- 您使用了多个Hermes配置文件，但选错了那个（可运行 `hermes profile list` 查看）

### 希望彻底撤销并重新开始

```bash
hermes auth logout nous       # wipes the local refresh token
# Then re-run setup or remove the subscription from the Portal web UI
```

## 用数据直观呈现您的收益

| 不使用 Portal | 使用 Portal |
|----------------|-------------|
| `.env` 文件中包含 1 组 OpenRouter / Anthropic / OpenAI 密钥 | 1 个 OAuth 刷新令牌，无需 `.env` 密钥 |
| 1 组用于网页的 Firecrawl 密钥 | 网页请求通过网关路由 |
| 1 组用于图像生成的 FAL 密钥 | 图像生成请求通过网关路由 |
| 1 组用于浏览器的 Browser Use / Browserbase 密钥 | 浏览器请求通过网关路由 |
| 1 组用于 TTS/语音模式的 OpenAI 密钥 | TTS 请求通过网关路由 |
| 5 个独立的控制面板、充值及账单 | 1 份订阅套餐，1 张账单 |
| 跨机器使用：需复制全部 5 组密钥 | 跨机器使用：仅需重新进行一次 OAuth 认证 |

以上即为全部优势。如果您实际使用的后端服务超过两种，这份订阅套餐的价值便已体现。

## 相关内容

- **[Nous Portal 集成页面](/integrations/nous-portal)** — 订阅套餐包含的功能概览
- **[工具网关](/user-guide/features/tool-gateway)** — 所有通过网关路由的工具的详细信息
- **[订阅代理](/user-guide/features/subscription-proxy)** — 在非 Hermes 工具中使用 Portal 订阅套餐
- **[语音模式](/user-guide/features/voice-mode)** — 在 Portal 订阅套餐上设置语音对话功能
- **[通过 SSH 实现 OAuth 登录](/guides/oauth-over-ssh)** — 远程/无头登录方案
- **[用户配置文件](/user-guide/profiles)** — 在多个 Hermes 配置之间共享同一 Portal 登录账号
