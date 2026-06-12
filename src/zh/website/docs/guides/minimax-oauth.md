---
sidebar_position: 15
title: "MiniMax OAuth"
description: "Log into MiniMax via browser OAuth and use MiniMax-M2.7 models in Hermes Agent — no API key required"
---

# MiniMax OAuth 认证方式

Hermes Agent 支持通过基于浏览器的 OAuth 登录流程来使用 **MiniMax** 服务，其认证凭证与 [MiniMax 平台](https://www.minimax.io) 完全一致。无需 API 密钥或信用卡信息——只需登录一次，Hermes 就会自动续期您的会话。

该传输层复用了 `anthropic_messages` 适配器（MiniMax 在 `/anthropic` 接口上提供了兼容 Anthropic Messages 的功能），因此所有现有的工具调用、流式处理及上下文管理功能均无需进行任何适配器修改即可正常使用。

## 概览

| 项目 | 值 |
|------|------|
| 提供商 ID | `minimax-oauth` |
| 显示名称 | MiniMax (OAuth) |
| 认证类型 | 浏览器 OAuth（PKCE 导流流程） |
| 传输层 | 兼容 Anthropic Messages 的 (`anthropic_messages`) |
| 支持的模型 | `MiniMax-M2.7`、`MiniMax-M2.7-highspeed` |
| 全球端点 | `https://api.minimax.io/anthropic` |
| 中国地区端点 | `https://api.minimaxi.com/anthropic` |
| 是否需要环境变量 | 否（此提供商不使用 `MINIMAX_API_KEY`） |

## 前提条件

- Python 3.9 及以上版本
- 已安装 Hermes Agent
- 在 [minimax.io](https://www.minimax.io)（全球版）或 [minimaxi.com](https://www.minimaxi.com)（中国版）注册的 MiniMax 账户
- 本地计算机上需安装浏览器（如需远程会话，可使用 `--no-browser` 参数） 

## 快速入门指南

```bash
# Launch the provider and model picker
hermes model
# → Select "MiniMax (OAuth)" from the provider list
# → Hermes opens your browser to the MiniMax authorization page
# → Approve access in the browser
# → Select a model (MiniMax-M2.7 or MiniMax-M2.7-highspeed)
# → Start chatting

hermes
```

首次登录后，凭证将会存储在 `~/.hermes/auth.json` 文件中，并且会在每个会话开始前自动刷新。

## 手动登录

您无需通过模型选择器即可直接触发登录操作：

```bash
hermes auth add minimax-oauth
```

### 中国地区

如果您的账户位于中国平台（`minimaxi.com`），请改用基于 API 密钥的 `minimax-cn` 提供商——该提供商仅支持 `auth_type="api_key"` 的认证方式（不支持 OAuth 流程）。您可以直接配置 `MINIMAX_CN_API_KEY`（可选地也可配置 `MINIMAX_CN_BASE_URL`）：

```bash
echo 'MINIMAX_CN_API_KEY=your-key' >> ~/.hermes/.env
```

### 远程/无头会话

在无法运行浏览器的服务器或容器环境中：

```bash
hermes auth add minimax-oauth --no-browser
```

Hermes会生成验证URL和用户代码——请在任何设备上打开该URL，并在系统提示时输入相应代码。

## OAuth流程

Hermes基于MiniMax OAuth接口，采用了PKCE浏览器OAuth流程来实现授权：

1. Hermes首先生成一对PKCE验证器/挑战值以及一个随机状态值。
2. 然后向`{base_url}/oauth/code`发送包含挑战值的请求，从而获取`user_code`和`verification_uri`。
3. 您的浏览器会自动打开`verification_uri`，系统提示时请输入`user_code`。
4. Hermes会持续轮询`{base_url}/oauth/token`，直到获得访问令牌（或超过截止时间）。
5. 所获得的令牌（`access_token`、`refresh_token`及过期时间）会被保存在`~/.hermes/auth.json`文件中的`minimax-oauth`键值下。

当访问令牌的剩余有效期在60秒以内时，系统会在每次会话启动时自动执行令牌刷新操作（即标准的OAuth `refresh_token`授权流程）。

## 查询登录状态

```bash
hermes doctor
```

“◆ 认证提供方”部分将显示：

```
✓ MiniMax OAuth  (logged in, region=global)
```

或者，如果未登录：

```
⚠ MiniMax OAuth  (not logged in)
```

## 模型切换

```bash
hermes model
# → Select "MiniMax (OAuth)"
# → Pick from the model list
```

或者直接设置模型：

```bash
hermes config set model.default MiniMax-M2.7
hermes config set model.provider minimax-oauth
```

## 配置参考

登录后，`~/.hermes/config.yaml` 文件中将包含类似如下的配置项：

```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-oauth
  base_url: https://api.minimax.io/anthropic
```

### 地区端点

| 提供商 ID | 入口网站 | 推理端点 |
|-----------|--------|----------|
| `minimax-oauth`（全球） | `https://api.minimax.io` | `https://api.minimax.io/anthropic` |
| `minimax-cn`（中国） | `https://api.minimaxi.com` | `https://api.minimaxi.com/anthropic` |

### 提供商别名

以下所有别名均指向 `minimax-oauth`：

```bash
hermes --provider minimax-oauth    # canonical
hermes --provider minimax-portal   # alias
hermes --provider minimax-global   # alias
hermes --provider minimax_oauth    # alias (underscore form)
```

## 环境变量

`minimax-oauth` 提供商**不使用** `MINIMAX_API_KEY` 或 `MINIMAX_BASE_URL` 这两个变量。它们仅适用于基于 API 密钥的 `minimax` 和 `minimax-cn` 提供商。

| 变量 | 效果 |
|------|------|
| `MINIMAX_API_KEY` | 仅被 `minimax` 提供商使用——`minimax-oauth` 会忽略该变量 |
| `MINIMAX_CN_API_KEY` | 仅被 `minimax-cn` 提供商使用——`minimax-oauth` 会忽略该变量 |

若要将 `minimax-oauth` 设为默认提供商，请在 `config.yaml` 中设置 `model.provider: minimax-oauth`（可通过 `hermes setup` 进行引导式配置），或针对单次调用使用 `--provider minimax-oauth` 参数。

```bash
hermes --provider minimax-oauth
```

## 模型

| 模型 | 适用场景 |
|-------|----------|
| `MiniMax-M2.7` | 长上下文推理、复杂工具调用 |
| `MiniMax-M2.7-highspeed` | 更低的延迟、轻量级任务及辅助调用 |

这两种模型均支持最多 200,000 个标记的上下文长度。

当使用 `minimax-oauth` 作为主要提供方时，`MiniMax-M2.7-highspeed` 会自动被用作视觉处理和任务委托任务的辅助模型。

## 故障排除

### 令牌已过期——未自动重新登录

如果令牌在过期前 60 秒内，Hermes 会在每次会话启动时刷新它。若访问令牌已经过期（例如长时间离线后），则会在下一次请求时自动刷新。如果刷新过程中出现 `refresh_token_reused` 或 `invalid_grant` 等错误，Hermes 会标记该会话需要重新登录。

当刷新失败为最终性错误（如 HTTP 4xx 错误、`invalid_grant`、授权被撤销等）时，Hermes 会将该刷新令牌标记为无效，并在本地将其隔离，以避免重复执行失败的请求。此时智能体只会显示一条“需要重新认证”的提示信息，直到您再次登录为止。

**解决方法：** 重新运行 `hermes auth add minimax-oauth` 以开始新的登录流程。下次成功完成请求后，该隔离状态就会被解除。

### 授权超时

设备码授权流程具有固定的过期时间窗口。如果您未能及时批准登录，Hermes 会报出超时错误。

**解决方法：** 重新运行 `hermes auth add minimax-oauth`（或 `hermes model`），从而重新开始授权流程。

### 状态不一致（可能是 CSRF 攻击）

Hermes 检测到授权服务器返回的 `state` 值与它之前发送的值不一致。

**解决方法：** 重新进行登录尝试。如果问题仍然存在，请检查是否有代理或重定向机制正在修改 OAuth 响应内容。

### 从远程服务器登录

如果 `hermes` 无法打开浏览器窗口，可使用 `--no-browser` 参数：

```bash
hermes auth add minimax-oauth --no-browser
```

Hermes 会打印出对应的 URL 和代码。请在任何设备上打开该 URL，并在相应界面完成流程。

### 运行时出现“未登录 MiniMax OAuth”的错误

认证存储中不存在 `minimax-oauth` 的凭证。可能是您尚未登录，或是凭证文件已被删除。

**解决方法：** 运行 `hermes model` 并选择 MiniMax（OAuth）选项，或执行 `hermes auth add minimax-oauth` 命令。

## 登出

如需移除已存储的 MiniMax OAuth 凭证：

```bash
hermes auth remove minimax-oauth
```

## 相关文档

- [AI 提供商参考](../integrations/providers.md)
- [环境变量](../reference/environment-variables.md)
- [配置设置](../user-guide/configuration.md)
- [hermes doctor 工具](../reference/cli-commands.md)
