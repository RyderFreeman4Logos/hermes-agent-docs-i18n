---
sidebar_position: 16
title: "Manage Hermes Cloud with MCP"
description: "Connect Hermes Agent to the Nous Portal MCP server so your local agent can list, start, stop, and manage your Hermes Cloud instances conversationally"
---

# 使用 MCP 管理 Hermes Cloud

[Hermes Cloud](https://portal.nousresearch.com/cloud) 会为您托管 Hermes Agent 实例。通常，您可以通过 [Nous Portal](/integrations/nous-portal) 中的 `/agents` 页面来管理这些实例。本指南旨在将您的**本地**Hermes Agent 与 Portal 的 MCP 服务器相连，这样您无需离开终端，只需通过简单指令——如“列出我的云端代理”、“重启已停止的代理”、“查询使用成本是多少”——即可管理这些云端实例。

该服务器是由 Nous Research 托管的标准 [MCP](/user-guide/features/mcp) 服务器，采用与您在 Portal 中相同的 OAuth 登录方式进行身份验证。连接成功后，Hermes 就能获得两个可代表其调用的工具。

## 可实现的功能

连接成功后，模型即可针对您的 Hermes Cloud 组织调用以下功能：

| 指令内容 | 底层接口 |
|----------|----------|
| “列出我的云端代理” | `agents` (list) |
| “`<name>` 的当前状态如何？” | `agents` (get / status) |
| “该实例的大致成本是多少？” | `agents` (cost_estimate) |
| “启动/停止/重启 `<name>`” | `agent` (start / stop / restart) |
| “创建一个名为 `<name>` 的新实例” | `agent` (create) |
| “销毁 `<name>`” | `agent` (destroy) |
| “更新 `<name>` 的环境/镜像” | `agent` (update_env / update_image) |

所有调用均会以您的 Portal 账户身份在**您的**组织内执行，且每次调用都会重新验证权限——该连接仅能操作您通过网页界面已控制的实例。

## 先决条件

- 一个可访问 [Hermes Cloud](https://portal.nousresearch.com/cloud) 的 [Nous Portal](/integrations/nous-portal) 账户（至少拥有一个实例，或具备创建实例的能力）。  
- 已安装 MCP 支持功能。若您使用的是标准安装脚本，则该功能已内置；否则需手动安装。

  ```bash
  cd ~/.hermes/hermes-agent
  uv pip install -e ".[mcp]"
  ```

您无需单独的 API 密钥或客户端密钥——服务器采用基于 PKCE 的 OAuth 认证机制，登录过程仅需在浏览器中完成一次往返请求即可。  

## 第一步：添加服务器

```bash
hermes mcp add --url https://portal.nousresearch.com/mcp --auth oauth hermes-cloud
```

`--auth oauth` 用于告知 Hermes 这是一个受 OAuth 保护的 HTTP 服务器。首次连接时，Hermes 会执行以下操作：

1. 自动识别服务器的 OAuth 端点（基于 RFC 9728 / 8414 元数据）。
2. 按照 RFC 7591 规范以客户端身份进行注册——无需复制任何密钥。
3. 打开浏览器进入门户网站，让您登录并授权。
4. 将生成的令牌存储在 `~/.hermes/mcp-tokens/` 目录下，并自动重复使用该令牌（支持自动刷新）。

### 选择组织

如果您的门户账户隶属于**多个组织**，在授权过程中浏览器会显示一个**组织选择器**——请选定此次连接应管理的组织。此选择只需在浏览器中完成一次，无需在命令行中传递任何参数。仅属于单个组织的账户则无需经过此步骤，会自动绑定。

若需将连接指向其他组织，需先移除再重新添加该服务器（执行 `hermes mcp remove hermes-cloud`，然后再运行 `add` 命令），随后在浏览器中选择目标组织。

## 第 2 步：验证连接是否成功

```bash
hermes mcp test hermes-cloud
```

接着启动（或重新加载）会话：

```bash
hermes chat
```

```text
/reload-mcp
```

提出一个只读查询，以确认相关工具已正常运行：

```text
List my Hermes Cloud agents and their current status.
```

您应该能够获取到与门户网站 `/agents` 页面上显示的完全相同的实例。

## 第 3 步：使用它

只读查询始终是安全的：

```text
Which of my cloud agents is currently running, and roughly what is each one costing?
```

生命周期操作对应于普通请求：

```text
Restart the instance called research-bot.
```

```text
Create a new Hermes Cloud instance named scratch, then tell me when it's ready.
```

Hermes 会反馈每个工具返回的结果——包括实例列表、新状态以及所创建实例的详细信息——这样您就能确认操作已成功执行。

## 配置

执行 `hermes mcp add` 后，相关配置将存储在 `~/.hermes/config.yaml` 文件中：

```yaml
mcp_servers:
  hermes-cloud:
    url: "https://portal.nousresearch.com/mcp"
    auth: oauth
```

请勿在 `config.yaml` 中填写任何凭证——OAuth 令牌会单独存储在 `~/.hermes/mcp-tokens/` 目录下，就如同 Portal 的刷新令牌也不会出现在配置文件中一样。

### 限制可使用的工具范围

服务器同时提供了用于读取信息（`agents`）和修改数据（`agent`）的工具。若希望建立**只读**连接——即仅能列出和查看信息，而无法启动、停止、创建或销毁任何对象——则应将其限制为仅使用 `agents` 工具：

```yaml
mcp_servers:
  hermes-cloud:
    url: "https://portal.nousresearch.com/mcp"
    auth: oauth
    tools:
      include: [agents]
```

修改配置后，请运行 `/reload-mcp` 命令。如需了解完整的过滤模型设置（包括 `include`/`exclude`、`prompts`、`resources` 等参数），请参阅 [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes) 文档。

## 故障排除

### 浏览器显示组织选择器，但我不确定该选哪个

如果您属于多个 Portal 组织，请选择您希望通过此连接来管理的 Hermes Cloud 实例所在的组织。如果拿不准，可参考 Portal 的 `/agents` 页面上显示的实例所属组织。之后您也可以通过移除并重新添加服务器来更改选择。

### 连接时出现 “invalid_client” 或 “unknown client” 错误

存储的客户端注册信息已与服务器不匹配（例如，您之前连接的是其他环境）。请清除该服务器的缓存的 OAuth 状态，然后重新添加它：

```bash
hermes mcp remove hermes-cloud
rm -f ~/.hermes/mcp-tokens/hermes-cloud.*
hermes mcp add --url https://portal.nousresearch.com/mcp --auth oauth hermes-cloud
```

### 添加服务器后工具未显示

请在会话中重新加载MCP，然后再次检查：

```text
/reload-mcp
```

```text
Tell me which MCP-backed tools are available right now.
```

如果这些信息仍然缺失，可以运行 `hermes mcp test hermes-cloud`，直接查看连接错误信息。

### 系统要求我重新登录

OAuth 令牌会自动刷新，但如果门户网站使您的会话失效（如密码更改、令牌撤销或过期），下一次调用时系统就会要求您重新授权。请再次运行 `hermes mcp add` 命令，浏览器流程将重新生成令牌。

### 无头模式 / SSH / 远程主机

OAuth 浏览器回调操作会在运行 Hermes 的机器上执行。在远程主机上，需通过 SSH 转发回环端口——其原理与其他 OAuth 登录方式相同。详情请参阅 [通过 SSH/远程主机进行 OAuth 登录](/guides/oauth-over-ssh)。

## 相关内容

- **[Nous Portal](/integrations/nous-portal)** — 同一登录机制背后的订阅服务、模型以及工具网关
- **[在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)** — 通用意义上的 MCP 服务器连接与筛选方法
- **[MCP 功能概览](/user-guide/features/mcp)** — 什么是 MCP 以及 Hermes 如何使用它
- **[MCP 配置参考](/reference/mcp-config-reference)** — 所有的 `mcp_servers` 字段，包括 `auth: oauth` 的设置方式
- **[通过 SSH 进行 OAuth 登录](/guides/oauth-over-ssh)** — 在远程环境或仅支持浏览器的环境中登录
