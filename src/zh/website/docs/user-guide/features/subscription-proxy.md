---
sidebar_position: 15
title: "Subscription Proxy"
description: "Use your Nous Portal subscription (or other OAuth provider) as an OpenAI-compatible endpoint for external apps"
---

# 订阅代理

订阅代理是一个本地 HTTP 服务器，它允许外部应用——如 OpenViking、Karakeep、Open WebUI，以及任何支持 OpenAI 兼容聊天补全功能的应用——将您通过 Hermes 管理的提供商订阅作为其 LLM 接入点。该代理会自动附加正确的凭证（并定期刷新），因此应用无需使用静态 API 密钥。

它与 [API 服务器](./api-server.md) 不同：

| | API 服务器 | 订阅代理 |
|---|---|---|
| 提供的服务 | 您的智能体（完整的工具集、内存和技能） | 原始模型推理 |
| 使用场景 | “将 Hermes 作为聊天后端” | “在另一应用中使用我的 Portal 订阅” |
| 身份验证 | 您的 `API_SERVER_KEY` | 任意令牌（代理会附加真实凭证） |
| 工具调用 | 支持——智能体会执行工具操作 | 不支持——仅做直接转发 |

当您希望以**智能体**作为后端时，请使用 API 服务器；而当您仅希望通过订阅获取**模型**本身时，则应使用代理。

## 快速开始

### 1. 登录您的提供商（只需一次）

```bash
hermes portal
```

这将打开您的浏览器，进入 Nous Portal 的 OAuth 流程。Hermes 会将刷新令牌存储在 `~/.hermes/auth.json` 文件中——该文件也是所有 Hermes 提供商登录信息的存放位置。

### 2. 启动代理

```bash
hermes proxy start
```

```
Starting Hermes proxy for Nous Portal
  Listening on:  http://127.0.0.1:8645/v1
  Forwarding to: (resolved per-request from your subscription)
  Use any bearer token in the client — the proxy attaches your real credential.
```

请在前台保持该进程运行。若希望其在用户退出登录后仍继续运行，可使用 `tmux`、`nohup` 或 systemd 单元来实现。

### 3. 将您的应用指向该代理

所有兼容 OpenAI 的应用配置均采用相同的三元组结构：

```
Base URL:   http://127.0.0.1:8645/v1
API key:    anything (e.g. "sk-unused")
Model:      Hermes-4-70B    # or Hermes-4.3-36B, Hermes-4-405B
```

该代理会忽略应用程序发送的 `Authorization` 请求头，而是将您真实的 Portal 凭据附加到上游请求中。当令牌即将过期时，系统会自动触发刷新操作。

## 支持的提供商

```bash
hermes proxy providers
```

目前已正式推出的插件包括：`nous`（Nous Portal）和 `xai`（xAI / Grok）。如需添加更多 OAuth 提供商，只需在 `hermes_cli/proxy/adapters/` 目录下实现 `UpstreamAdapter` 接口即可。

## 查询状态

```bash
hermes proxy status
```

```
Hermes proxy upstream adapters

  [nous    ] Nous Portal — ready (bearer expires 2026-05-15T06:43:21Z)
```

如果看到“未登录”提示，请运行 `hermes portal`。若出现“凭证需要处理”的提示，说明您的刷新令牌已被撤销（这种情况较为罕见——通常发生在您从 Portal 网页界面退出后）——只需再次运行 `hermes portal` 即可。

## 允许的路径

代理仅会转发上游实际提供的路径。对于 Nous Portal：

| 路径 | 用途 |
|------|------|
| `/v1/chat/completions` | 聊天补全功能（流式与非流式） |
| `/v1/completions` | 传统文本补全功能 |
| `/v1/embeddings` | 嵌入模型输出 |
| `/v1/models` | 模型列表 |

其他路径（如 `/v1/images/generations`、`/v1/audio/speech` 等）会返回 404 错误，并明确指出允许的路径。这样可以防止异常客户端向上游发送错误的请求。

## 配置 OpenViking 使用 Portal

[OpenViking](https://github.com/volcengine/OpenViking) 是一种上下文数据库，其视觉/语言模型（用于提取记忆信息）和嵌入模型都需要相应的 LLM 提供方。通过该代理，您可以将 `vlm.api_base` 指向本地的代理服务器：

编辑 `~/.openviking/ov.conf` 文件：

```json
{
  "vlm": {
    "provider": "openai",
    "model": "Hermes-4-70B",
    "api_base": "http://127.0.0.1:8645/v1",
    "api_key": "unused-proxy-attaches-real-creds"
  }
}
```

接着在终端中与 `openviking-server` 一同启动您的代理服务：

```bash
# Terminal 1
hermes proxy start

# Terminal 2
openviking-server
```

现在，OpenViking的VLM功能已通过您的Portal订阅服务来调用。不过，嵌入模型部分仍需要独立的提供方——虽然Portal确实提供了`/v1/embeddings`接口，但可选择的模型取决于您的订阅层级支持的范围；详情请访问`portal.nousresearch.com/models`。

## 配置Karakeep（或任何书签/摘要生成工具）

[Karakeep](https://karakeep.app/)采用与OpenAI兼容的API来实现书签摘要生成功能。在其配置文件中：

```bash
# Karakeep .env
OPENAI_API_BASE_URL=http://127.0.0.1:8645/v1
OPENAI_API_KEY=any-non-empty-string
INFERENCE_TEXT_MODEL=Hermes-4-70B
```

对于 Open WebUI、LobeChat、NextChat 或其他任何兼容 OpenAI 的客户端，都适用相同的原理。

## 在局域网内暴露服务

默认情况下，该代理仅绑定 `127.0.0.1`（即本地主机）。若要让网络中的其他设备也能使用它：

```bash
hermes proxy start --host 0.0.0.0 --port 8645
```

⚠ **请注意：** 现在您网络中的任何用户都可以使用您的 Portal 订阅服务。该代理本身不具备身份验证功能——它会接受任何有效的访问令牌。如果需要将此服务暴露到可信网络之外，请务必使用具备适当身份验证功能的防火墙、VPN 或反向代理。

## 流量限制

您的 Portal 套餐所规定的 RPM/TPM 限制适用于整个代理系统。该代理不会对请求进行分流或资源池化处理——它只是一个拥有您完整订阅配额的单一访问节点。您可以在 [portal.nousresearch.com](https://portal.nousresearch.com) 上查看使用情况。

## 架构设计

该代理的设计力求极简。对于每个请求，其处理流程如下：

1. 接收来自您应用程序的 `POST /v1/chat/completions` 请求；
2. 查找适配器当前的凭证（如凭证即将过期则进行刷新）；
3. 原样转发请求体，并附加 `Authorization: Bearer <生成的令牌>` 头部信息；
4. 未经任何修改地返回响应内容（保留原始的 SSE 格式）。

该代理不会对请求内容进行任何处理，也不会记录请求体信息，更不存在代理循环机制。它本质上只是一个负责附加凭证的直通节点。

## 未来规划：更多 OAuth 提供商支持

该适配器系统具备可扩展性。若要添加新的提供商（例如 HuggingFace、GitHub Copilot 的聊天接口，或通过 OAuth 连接的 Anthropic），只需在 `hermes_cli/proxy/adapters/<provider>.py` 文件中实现 `UpstreamAdapter` 类，并在 `adapters/__init__.py` 中进行注册即可。对于那些在协议层面上不兼容 OpenAI 标准的提供商（例如 Anthropic Messages API），则可能需要额外的转换层，而这目前尚不在该代理的设计范围内。
