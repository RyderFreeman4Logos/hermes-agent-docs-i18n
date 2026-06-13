---
sidebar_position: 16
title: "xAI Grok OAuth (SuperGrok / X Premium+)"
description: "Sign in with your SuperGrok or X Premium+ subscription to use Grok models in Hermes Agent — no API key required"
---

# xAI Grok OAuth（SuperGrok / X Premium+）

Hermes Agent 支持通过基于浏览器的 OAuth 登录流程接入 [accounts.x.ai](https://accounts.x.ai) 的 xAI Grok 服务，该流程适用于 **SuperGrok 订阅用户**（[grok.com](https://x.ai/grok)）或拥有 **X Premium+ 订阅**的账户（关联的 X 账户）。无需设置 `XAI_API_KEY`——只需登录一次，Hermes 就会自动在后台刷新您的会话。

当您使用拥有 Premium+ 订阅的 X 账户登录时，xAI 会自动将订阅状态与您的 xAI 会话关联起来，因此其 OAuth 登录流程与直接使用 SuperGrok 订阅的用户完全相同。

该传输层复用了 `codex_responses` 适配器（xAI 提供了类似 Responses 风格的接口），因此推理、工具调用、流式处理以及提示词缓存等功能均无需修改适配器即可正常工作。

Hermes 中所有直接与 xAI 对接的功能——包括文本转语音、图像生成、视频生成以及文字转录——也都复用同一个 OAuth 承载令牌，因此只需登录一次即可同时使用这四项功能。

## 概览

| 项目 | 值 |
|------|------|
| 提供商 ID | `xai-oauth` |
| 显示名称 | xAI Grok OAuth（SuperGrok / X Premium+） |
| 认证类型 | 浏览器 OAuth 2.0 PKCE（回环回调） |
| 传输层 | xAI Responses API（`codex_responses`） |
| 默认模型 | `grok-4.3` |
| 接口地址 | `https://api.x.ai/v1` |
| 认证服务器 | `https://accounts.x.ai` |
| 是否需要环境变量 | 否（此提供商**不**使用 `XAI_API_KEY`） |
| 订阅要求 | [SuperGrok](https://x.ai/grok) 或 [X Premium+](https://x.com/i/premium_sign_up)——详见下方说明 |

## 先决条件

- Python 3.9 及以上版本
- 已安装 Hermes Agent
- 您的 xAI 账户拥有有效的 **SuperGrok** 订阅，**或**您用于登录的 X 账户拥有 **X Premium+** 订阅（xAI 会自动关联订阅信息）
- 本地机器上需安装浏览器（如需远程会话，可使用 `--no-browser` 参数）

:::warning xAI 可能会根据用户等级限制 OAuth API 的访问权限
xAI 的后端会对 OAuth API 设置自身的允许列表，即便应用内的订阅处于有效状态，某些普通 SuperGrok 订阅用户仍可能被拒绝访问，返回 `HTTP 403` 错误（参见问题 [#26847](https://github.com/NousResearch/hermes-agent/issues/26847)）。如果通过浏览器成功完成 OAuth 登录，但推理请求仍返回 403 错误，可设置 `XAI_API_KEY` 并切换到基于 API 密钥的接入方式（`provider: xai`）——目前该方式不受同样的访问限制。:::

## 快速入门

```bash
# Launch the provider and model picker
hermes model
# → Select "xAI Grok OAuth (SuperGrok / X Premium+)" from the provider list
# → Hermes opens your browser to accounts.x.ai
# → Approve access in the browser
# → Pick a model (grok-4.3 is at the top)
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

在服务器、容器或没有浏览器可用的SSH会话中，Hermes能够识别出远程环境，因此会直接显示授权URL，而无需打开浏览器。

**重要提示：** 回环监听器仍会在远程机器的`127.0.0.1:56121`地址上运行。xAI重定向请求必须能够连接到该监听器，因此如果在您的笔记本电脑上直接打开该URL将会失败（显示“无法建立连接。我们无法访问您的应用。”）。除非您先转发端口，否则问题无法解决。

```bash
# In a separate terminal on your local machine:
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# Then in your SSH session on the remote machine:
hermes auth add xai-oauth --no-browser
# Open the printed authorize URL in your local browser.
```

通过跳转框/堡垒机连接时：请添加参数 `-J jump-user@jump-host`。

如需包含 ProxyJump 链、mosh/tmux 以及 ControlMaster 相关注意事项的完整分步指南，请参阅 [基于 SSH/远程主机的 OAuth 认证](./oauth-over-ssh.md)。

### 仅支持浏览器的远程连接方式（Cloud Shell、Codespaces、EC2 Instance Connect）

如果您没有常规的 SSH 客户端（例如在 GCP Cloud Shell、GitHub Codespaces、AWS EC2 Instance Connect、Gitpod 或其他基于浏览器的控制台环境中运行 Hermes），则无法使用上述 `ssh -L` 方法。此时请改用 `--manual-paste` 参数——Hermes 会跳过回环监听器，允许您直接从浏览器中粘贴失败的回调 URL：

```bash
hermes auth add xai-oauth --manual-paste
# Or via the model picker:
hermes model --manual-paste
```

如需完整的操作指南，请参阅[通过 SSH/远程主机进行 OAuth 认证](./oauth-over-ssh.md#browser-only-remote-cloud-shell--codespaces--ec2-instance-connect)。此版本还修复了 [#26923](https://github.com/NousResearch/hermes-agent/issues/26923) 中的回归问题。

如果授权页面直接在页面上显示授权码（这是 xAI 在基于浏览器的控制台中的当前行为），而非跳转至您的 `127.0.0.1:56121/callback` 地址，请在“回调地址：”输入框中仅粘贴**纯代码值**——Hermes 可以接受完整的 URL、仅包含 `?code=...&state=...` 的查询片段，或是纯代码形式，三者均可互换使用。

## 登录流程说明

1. Hermes 会打开您的浏览器，导航至 `accounts.x.ai`。
2. 您进行登录（或确认现有会话）并授权访问。
3. xAI 会将用户重定向回 Hermes，相应的令牌会被保存到 `~/.hermes/auth.json` 文件中。
4. 从那时起，Hermes 会在后台自动刷新访问令牌——只要您没有执行 `hermes auth remove xai-oauth` 命令或在 xAI 账户设置中撤销授权，您的账户就会保持登录状态。

## 检查登录状态

```bash
hermes doctor
```

`◆ Auth Providers`部分会显示包括`xai-oauth`在内的所有认证提供程序的当前状态。

```bash
hermes model
# → Select "xAI Grok OAuth (SuperGrok / X Premium+)"
# → Pick from the model list (grok-4.3 is pinned to the top)
```

或者直接设置模型：

```bash
hermes config set model.default grok-4.3
hermes config set model.provider xai-oauth
```

## 配置参考

登录后，`~/.hermes/config.yaml` 文件中将包含以下内容：

```yaml
model:
  default: grok-4.3
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

如果已存储有 OAuth 令牌，选择器会确认该信息并跳过凭证输入步骤。若既未设置 OAuth 令牌也未设置 `XAI_API_KEY`，选择器会提供三个选项：OAuth 登录、粘贴 API 密钥或直接跳过。

:::注意 视频生成功能默认处于关闭状态
`video_gen` 工具集默认是禁用的。在智能体能够调用 `video_generate` 功能之前，需先通过 `hermes tools` → `🎬 Video Generation`（按空格键）将其启用。否则，智能体可能会回退到内置的 ComfyUI 技能，该技能同样具备视频生成功能。
:::

:::注意 当配置了 xAI 凭证时，X 搜索功能会自动启用
一旦配置了 xAI 凭证（SuperGrok / X Premium+ OAuth 令牌或 `XAI_API_KEY`），`x_search` 工具集就会自动启用。如不希望如此，可通过 `hermes tools` → `🐦 X (Twitter) Search`（按空格键）手动禁用它。该工具会通过 xAI 内置的 `x_search` Responses API 运行——无论使用 SuperGrok / X Premium+ OAuth 登录方式还是付费的 `XAI_API_KEY` 都能正常工作；当两种方式都配置时，系统会优先使用 OAuth 方式（从而消耗订阅额度而非 API 费用）。即使工具集处于启用状态，若未配置 xAI 凭证，模型也无法看到该工具的架构信息。
:::

### 模型

| 工具 | 模型 | 备注 |
|------|------|------|
| 聊天 | `grok-4.3` | 默认模型；通过 OAuth 登录时会自动选择 |
| 聊天 | `grok-4.20-0309-reasoning` | 具有推理功能的版本 |
| 聊天 | `grok-4.20-0309-non-reasoning` | 不具备推理功能的版本 |
| 聊天 | `grok-4.20-multi-agent-0309` | 多智能体协作版本 |
| 图像生成 | `grok-imagine-image` | 默认模型；处理时间约 5–10 秒 |
| 图像生成 | `grok-imagine-image-quality` | 图像质量更高；处理时间约 10–20 秒 |
| 视频生成 | `grok-imagine-video` | 文本转视频功能 |
| 视频生成 | `grok-imagine-video-1.5-preview` | 图像转视频功能；旧版本别名为 `grok-imagine-video-1.5-2026-05-30` |
| 语音合成 | （默认语音） | 使用 xAI 的 `/v1/tts` 接口 |

聊天相关的模型列表会实时从磁盘上的 `models.dev` 缓存中获取；一旦该缓存更新，新的 xAI 版本就会自动出现。`grok-4.3` 模型始终位于列表顶部。

## 环境变量

| 变量 | 效果 |
|----------|------|
| `XAI_BASE_URL` | 覆盖默认的 `https://api.x.ai/v1` 接口地址（很少需要使用）。 |

若要将 xAI 设为默认提供方，请在 `config.yaml` 中设置 `model.provider: xai-oauth`（可使用 `hermes setup` 进行引导式配置），或为单次调用添加参数 `--provider xai-oauth`。

## 故障排除

### 令牌过期——未自动重新登录
Hermes 会在每次会话开始前刷新令牌，遇到 401 错误时也会主动进行刷新。如果刷新因 `invalid_grant` 错误失败（即刷新令牌已被撤销或账户信息已变更），Hermes 会显示一条带输入框的重新认证提示，而不会崩溃。

当刷新彻底失败时（如出现 HTTP 4xx 错误、`invalid_grant` 错误、令牌被撤销等），Hermes 会将该刷新令牌标记为无效并在本地将其隔离——后续调用会跳过这次失败的刷新尝试，避免反复出现相同的 401 错误。此时智能体只会显示一条“需要重新认证”的提示，直到你再次登录为止。

**解决方法：** 重新运行 `hermes auth add xai-oauth` 以开始新的登录流程。下次成功完成交互后，该被隔离的令牌就会被清除。

### 认证超时
回环监听器的有效时间有限（默认为 180 秒）。如果你未能及时确认登录，Hermes 会抛出超时错误。

**解决方法：** 重新运行 `hermes auth add xai-oauth`（或 `hermes model`），系统将重新开始登录流程。

### 状态不一致（可能是 CSRF 攻击）
Hermes 检测到认证服务器返回的 `state` 值与自己发送的值不一致。

**解决方法：** 重新进行登录操作。如果问题依旧存在，请检查是否有代理或重定向机制正在修改 OAuth 响应内容。

### 从远程服务器登录
在 SSH 或容器环境中运行时，Hermes 会直接输出认证地址，而不会自动打开浏览器。由于远程主机上的回环回调监听器仍绑定在 `127.0.0.1:56121` 地址，因此没有通过 SSH 局部转发的话，你的笔记本浏览器是无法访问该地址的。

```bash
# Local machine, separate terminal:
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# Remote machine:
hermes auth add xai-oauth --no-browser
```

完整操作指南（跳转框、mosh/tmux、端口冲突）：[通过 SSH 进行 OAuth 认证 / 远程主机](./oauth-over-ssh.md)。

### 成功登录后出现 HTTP 403 错误（权限/资格问题）

在浏览器中完成 OAuth 认证并保存了令牌，但在执行推理或刷新令牌时却返回 `HTTP 403` 错误，错误信息类似“调用者无权执行该操作”。

这**并非**令牌过期的问题——重新运行 `hermes model` 也无法解决该问题。有反馈指出，即便应用内的订阅处于有效状态，xAI 的后端仍会限制特定 SuperGrok 套餐用户使用 OAuth API（问题编号 [#26847](https://github.com/NousResearch/hermes-agent/issues/26847)）。

**解决方案：** 设置 `XAI_API_KEY` 并切换至基于 API 密钥的访问路径。

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

该操作会同时删除 `auth.json` 中的单例 OAuth 条目，以及与 `xai-oauth` 相关的所有凭证池记录。如果您只想移除某个特定的凭证池条目，请使用命令 `hermes auth remove xai-oauth <index|id|label>`（可通过运行 `hermes auth list xai-oauth` 查看这些条目）。

## 参考资料

- [通过 SSH/远程主机进行 OAuth 认证](./oauth-over-ssh.md) —— 若 Hermes 运行在不同于浏览器的机器上，此文档为必读内容
- [AI 提供商参考手册](../integrations/providers.md)
- [环境变量](../reference/environment-variables.md)
- [配置设置](../user-guide/configuration.md)
- [语音与文本转语音功能](../user-guide/features/tts.md)
