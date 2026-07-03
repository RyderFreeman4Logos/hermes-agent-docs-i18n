---
sidebar_position: 16
title: "xAI Grok OAuth (SuperGrok / X Premium+)"
description: "Sign in with your SuperGrok or X Premium+ subscription to use Grok models in Hermes Agent — no API key required"
---

# xAI Grok OAuth（SuperGrok / X Premium+）

Hermes Agent 支持通过基于浏览器的 OAuth 设备码登录流程，借助 [accounts.x.ai](https://accounts.x.ai) 访问 xAI Grok，该流程适用于 **SuperGrok 订阅用户**（[grok.com](https://x.ai/grok)）或拥有 **X Premium+ 订阅**的账户（需关联 X 账户）。无需使用 `XAI_API_KEY`——只需登录一次，Hermes 就会自动在后台刷新您的会话。

当您使用已开通 Premium+ 功能的 X 账户登录时，xAI 会自动将订阅状态与您的 xAI 会话关联起来，因此其 OAuth 登录流程与直接使用 SuperGrok 订阅的用户完全一致。

该传输层复用了 `codex_responses` 适配器（xAI 提供了类似 Responses 风格的接口），因此推理、工具调用、流式处理以及提示词缓存等功能均无需进行任何适配器调整即可正常工作。

Hermes 中所有直接与 xAI 对接的功能——包括文本转语音、图像生成、视频生成以及文字转录——也都复用相同的 OAuth 承载令牌，因此只需登录一次即可同时使用这四项功能。

## 概览

| 项目 | 值 |
|------|------|
| 提供商 ID | `xai-oauth` |
| 显示名称 | xAI Grok OAuth（SuperGrok / X Premium+） |
| 认证类型 | 浏览器 OAuth 2.0 设备码认证 |
| 传输层 | xAI Responses API (`codex_responses`) |
| 默认模型 | `grok-build-0.1` |
| 接口地址 | `https://api.x.ai/v1` |
| 认证服务器 | `https://accounts.x.ai` |
| 是否需要环境变量 | 否（此提供商不使用 `XAI_API_KEY`） |
| 订阅要求 | [SuperGrok](https://x.ai/grok) 或 [X Premium+](https://x.com/i/premium_sign_up)——详见下方说明 |

## 先决条件

- Python 3.9 及以上版本
- 已安装 Hermes Agent
- 您的 xAI 账户拥有有效的 **SuperGrok** 订阅，**或**您用于登录的 X 账户拥有 **X Premium+** 订阅（xAI 会自动关联订阅信息）
- 可以打开打印出的验证 URL 的浏览器

:::warning xAI 可能会根据订阅层级限制 OAuth API 的访问权限
xAI 的后端会对 OAuth API 设置自身的允许列表，即便应用内的订阅处于有效状态，某些普通 SuperGrok 订阅用户仍可能被拒绝访问，返回 `HTTP 403` 错误（参见问题 [#26847](https://github.com/NousResearch/hermes-agent/issues/26847)）。如果通过浏览器完成 OAuth 登录后推理请求仍返回 403 错误，请设置 `XAI_API_KEY` 并切换到基于 API 密钥的接入方式（`provider: xai`）——目前该接入方式不受同样的访问限制。
:::

## 快速入门

```bash
# Launch the provider and model picker
hermes model
# → Select "xAI Grok OAuth (SuperGrok / X Premium+)" from the provider list
# → Hermes opens or prints an accounts.x.ai verification URL
# → Enter the displayed code if prompted, then approve access in the browser
# → Pick a model (grok-build-0.1 is at the top)
# → Start chatting

hermes
```

首次登录后，凭证会被存储在 `~/.hermes/auth.json` 文件中，并会在过期前自动刷新。

## 手动登录

您无需通过模型选择器即可直接触发登录操作：

```bash
hermes auth add xai-oauth
```

### 远程/无头会话

在服务器、容器、仅支持浏览器的控制台（如 Cloud Shell、Codespaces、EC2 Instance Connect），或是 Hermes 无法在本地启动浏览器的 SSH 会话中，Hermes 会自动输出 xAI 验证网址及用户代码。您只需在笔记本电脑或云控制台中的任意浏览器中打开该网址，根据提示输入代码，Hermes 将持续进行轮询，直到 xAI 批准登录。此类场景无需使用 SSH 隧道或本地回调监听器。

```bash
hermes auth add xai-oauth --no-browser
# Open the printed verification URL in your browser.
```

无论是通过网页控制台还是桌面应用登录，都遵循相同的设备码流程：Hermes会首先显示验证网址和用户代码，随后在后台持续轮询，直到您批准访问权限。

## 登录流程说明

1. Hermes向`auth.x.ai`请求设备码。
2. 您打开该验证网址进行登录，根据提示输入显示的代码，然后批准访问。
3. Hermes会不断向xAI发起轮询直至获得批准，随后将令牌保存至`~/.hermes/auth.json`文件中。
4. 之后，Hermes会持续在后台刷新访问令牌——只要您没有执行`hermes auth logout xai-oauth`命令或在其xAI账户设置中撤销权限，您的登录状态就会保持有效。

## 查看登录状态

```bash
hermes doctor
```

`◆ Auth Providers` 部分会显示包括 `xai-oauth` 在内的所有认证提供程序的当前状态。  

## 切换模型

```bash
hermes model
# → Select "xAI Grok OAuth (SuperGrok / X Premium+)"
# → Pick from the model list (grok-build-0.1 is pinned to the top)
```

或者直接设置模型：

```bash
hermes config set model.default grok-build-0.1
hermes config set model.provider xai-oauth
```

## 配置参考

登录后，`~/.hermes/config.yaml` 文件中将包含以下内容：

```yaml
model:
  default: grok-build-0.1
  provider: xai-oauth
  base_url: https://api.x.ai/v1
```

### 提供商别名

以下所有别名均对应 `xai-oauth`：

```bash
hermes --provider xai-oauth        # canonical
hermes --provider grok-oauth       # alias
hermes --provider x-ai-oauth       # alias
hermes --provider xai-grok-oauth   # alias
```

## 直连 xAI 工具（文本转语音 / 图像处理 / 视频处理 / 文本转写 / X 搜索）

通过 OAuth 登录后，所有直连 xAI 的工具都会自动复用同一个承载令牌——**无需额外配置**，除非您希望使用 API 密钥。

如需为每个工具选择后端：

```bash
hermes tools
# → Text-to-Speech       → "xAI TTS"
# → Image Generation     → "xAI Grok Imagine (image)"
# → Video Generation     → "xAI Grok Imagine"
# → X (Twitter) Search   → "xAI Grok OAuth (SuperGrok / X Premium+)"
```

如果已存储有 OAuth 令牌，选择器会确认该信息并跳过凭证输入步骤。若既未设置 OAuth 令牌也未设置 `XAI_API_KEY`，则选择器会提供三个选项：OAuth 登录、粘贴 API 密钥或直接跳过。

:::注意 视频生成功能默认处于关闭状态
`video_gen` 工具集默认是被禁用的。在智能体能够调用 `video_generate` 函数之前，需先通过 `hermes tools` → `🎬 Video Generation`（按空格键）将其启用。否则，智能体可能会回退到内置的 ComfyUI 技能，该技能同样具备视频生成功能。
:::

:::注意 当配置了 xAI 凭证时，X 搜索功能会自动启用
一旦配置了 xAI 凭证（即 SuperGrok/X Premium+ OAuth 令牌或 `XAI_API_KEY`），`x_search` 工具集就会自动启用。若不希望如此，可通过 `hermes tools` → `🐦 X (Twitter) Search`（按空格键）手动禁用它。该工具会通过 xAI 内置的 `x_search` Responses API 进行操作——无论使用 SuperGrok/X Premium+ OAuth 登录方式，还是付费的 `XAI_API_KEY`，它都能正常工作；当两者都配置时，系统会优先使用 OAuth 方式（从而消耗订阅额度而非 API 费用）。即使工具集处于启用状态，若未配置 xAI 凭证，模型也无法看到该工具的架构信息。
:::

### 模型

| 工具 | 模型 | 备注 |
|------|------|------|
| 聊天 | `grok-build-0.1` | 默认模型；通过 OAuth 登录时会自动选择 |
| 聊天 | `grok-4.3` | 之前的默认模型 |
| 聊天 | `grok-4.20-0309-reasoning` | 具有推理功能的版本 |
| 聊天 | `grok-4.20-0309-non-reasoning` | 不具备推理功能的版本 |
| 聊天 | `grok-4.20-multi-agent-0309` | 多智能体协作版本 |
| 图像生成 | `grok-imagine-image` | 默认模型；生成时间约为 5–10 秒 |
| 图像生成 | `grok-imagine-image-quality` | 图像质量更高；生成时间约为 10–20 秒 |
| 视频生成 | `grok-imagine-video` | 文本转视频功能 |
| 视频生成 | `grok-imagine-video-1.5-preview` | 图像转视频功能；旧名称为 `grok-imagine-video-1.5-2026-05-30` |
| 语音合成 | （默认语音） | 使用 xAI 的 `/v1/tts` 接口 |

聊天相关的模型列表会实时从磁盘上的 `models.dev` 缓存中获取；一旦该缓存更新，新的 xAI 版本就会自动出现。`grok-build-0.1` 模型始终会被固定在列表的最顶部。

## 环境变量

| 变量 | 效果 |
|----------|------|
| `XAI_BASE_URL` | 覆盖默认的 `https://api.x.ai/v1` 接口地址（很少需要使用）。 |

若要将 xAI 设为当前使用的服务提供商，请在 `config.yaml` 中设置 `model.provider: xai-oauth`（可使用 `hermes setup` 进行引导式设置），或针对单次调用通过参数 `--provider xai-oauth` 指定。

## 故障排除

### 令牌已过期——未自动重新登录
Hermes 会在每次会话开始前刷新令牌，一旦收到 401 错误也会主动重新刷新。如果刷新失败并返回 `invalid_grant` 错误（即刷新令牌已被撤销或账户信息已变更），Hermes 会显示一条带输入框的重新认证提示，而不会导致程序崩溃。

当刷新失败为不可恢复的情况时（如 HTTP 4xx 错误、`invalid_grant` 错误、令牌已被撤销等），Hermes 会将该刷新令牌标记为无效并在本地将其隔离——后续调用将跳过这次失败的刷新尝试，而不会反复出现同样的 401 错误。此时智能体只会显示一条“需要重新认证”的提示，直到你再次登录为止。

**解决方法：** 重新运行 `hermes auth add xai-oauth` 以启动新的登录流程。下次成功完成认证后，该被隔离的令牌就会被清除。

### 认证超时
设备码授权方式具有有限的有效期（xAI 会在设备码响应中设置 `expires_in` 参数，通常为数十分钟）。如果你未能在期限内批准登录，Hermes 就会抛出超时错误。

**解决方法：** 重新运行 `hermes auth add xai-oauth`（或 `hermes model`）即可，系统将重新开始认证流程。

### 从远程服务器登录
在 SSH 或容器环境中使用时，Hermes 会直接显示验证网址和用户码，而不会自动打开浏览器。你需要在笔记本的浏览器或云控制台中打开该网址——对于 xAI Grok OAuth 方式，无需进行 SSH 端口转发。

```bash
hermes auth add xai-oauth --no-browser
```

对于回环重定向型提供商（如 Spotify、MCP 服务器），请参阅 [通过 SSH/远程主机进行 OAuth 认证](./oauth-over-ssh.md)。

### 成功登录后出现 HTTP 403 错误（权限/资格问题）

在浏览器中完成 OAuth 认证并保存了令牌，但在执行推理或刷新令牌时却会返回 `HTTP 403` 错误，错误信息类似“调用者无权执行该操作”。

这**并非**令牌过期的问题——重新运行 `hermes model` 也无法解决该问题。有案例表明，即便应用内的订阅处于有效状态，xAI 的后端仍会限制特定 SuperGrok 级别用户访问 OAuth API（问题编号 [#26847](https://github.com/NousResearch/hermes-agent/issues/26847)）。

**解决方案：** 设置 `XAI_API_KEY` 并切换至基于 API 密钥的认证路径。

```bash
export XAI_API_KEY=xai-...
hermes config set model.provider xai
```

如果需要通过 OAuth 方式登录，则可在 [x.ai/grok](https://x.ai/grok) 上升级您的订阅套餐。

### 运行时出现“未找到 xAI 凭据”的错误

认证存储中不存在 `xai-oauth` 条目，且也未设置 `XAI_API_KEY`。这可能是由于您尚未登录，或是凭据文件已被删除。

**解决方法：** 运行 `hermes model` 并选择 xAI Grok OAuth 提供商，或执行 `hermes auth add xai-oauth` 命令。

## 注销登录

如需移除所有存储的 xAI Grok OAuth 凭据：

```bash
hermes auth logout xai-oauth
```

此操作会同时删除 `auth.json` 中的单例 OAuth 条目，以及与 `xai-oauth` 相关的所有凭证池记录。如果您只需移除某个特定的凭证池条目，请使用命令 `hermes auth remove xai-oauth <index|id|label>`（可通过运行 `hermes auth list xai-oauth` 查看这些条目）。

## 参考资料

- [通过 SSH/远程主机进行 OAuth 认证](./oauth-over-ssh.md) —— 用于循环重定向提供方（如 Spotify、MCP）的 SSH 隧道；而 xAI 使用设备代码，无需此类隧道
- [AI 提供方参考文档](../integrations/providers.md)
- [环境变量](../reference/environment-variables.md)
- [配置设置](../user-guide/configuration.md)
- [语音与文本转语音功能](../user-guide/features/tts.md)
