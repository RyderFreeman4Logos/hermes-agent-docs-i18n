---
sidebar_position: 17
title: "OAuth over SSH / Remote Hosts"
description: "How to complete browser-based OAuth (xAI, Spotify, MCP servers) when Hermes runs on a remote machine, container, or behind a jump box"
---

# 通过 SSH/远程主机实现 OAuth 认证

某些 Hermes 提供方——**xAI Grok OAuth**、**Spotify**以及**远程 MCP 服务器**（如 Linear、Sentry、Atlassian、Asana、Figma 等）——采用*回环重定向*型 OAuth 流程。认证服务器会将您的浏览器重定向至 `http://127.0.0.1:<port>/callback`，这样 Hermes 启动的微型 HTTP 监听器便可捕获授权码。

当 Hermes 与浏览器运行在同一台机器上时，此方式可以完美工作。但一旦它们位于不同机器，就会出问题：您笔记本电脑上的浏览器试图连接到**本机**的 `127.0.0.1`，而监听器实际上绑定在**远程服务器**的 `127.0.0.1` 上。

解决方法是使用一行 SSH 本地转发命令——或者，如果您没有传统的 SSH 客户端（如 GCP Cloud Shell、GitHub Codespaces、EC2 Instance Connect、Gitpod 以及基于浏览器的 Web IDE），也可以使用在 [#26923](https://github.com/NousResearch/hermes-agent/issues/26923) 中引入的 `--manual-paste` 参数来解决该问题。

## 简而言之

```bash
# On your local machine (laptop), in a separate terminal:
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# In your existing SSH session on the remote machine:
hermes auth add xai-oauth --no-browser
# → Hermes prints an authorize URL. Open it in a browser on your laptop.
# → Your browser redirects to 127.0.0.1:56121/callback, the tunnel forwards
#   the request to the remote listener, login completes.
```

xAI OAuth 使用的端口是 `56121`。对于 Spotify，则需将其替换为 `43827`。Hermes 会在“Waiting for callback on ...”这一行显示其绑定的确切端口，可直接从该处复制。

## 仅限浏览器的远程连接（Cloud Shell / Codespaces / EC2 Instance Connect）

如果您没有常规的 SSH 客户端——例如因为您是在 GCP Cloud Shell、GitHub Codespaces、AWS EC2 Instance Connect、Gitpod 或其他基于浏览器的控制台中运行 Hermes——则无法使用上述 SSH 隧道。此时请改用 `--manual-paste` 参数：

```bash
hermes auth add xai-oauth --manual-paste
# → Hermes prints an authorize URL. Open it in a browser on your laptop.
# → Approve in the browser. The redirect to 127.0.0.1:56121/callback fails
#   to load — that's expected.
# → Copy the FULL URL from the failed page's address bar.
# → Paste it back into the terminal at the "Callback URL:" prompt.
```

对于集成式模型选择器，相同的标志也适用于 `hermes model --manual-paste` 命令。Hermes 可以互相替代地接受三种回调粘贴格式：完整的 URL、仅包含 `?code=...&state=...` 的查询片段；或者——当上游授权页面在页面内直接显示授权码而非进行重定向时（这正是 xAI 在基于浏览器的控制台中的当前行为）——仅单独提供该授权码值。

Hermes 对这两种路径使用**相同的 PKCE 验证器、状态值和随机数**，因此上游的 OAuth 流程在字节级上是完全一致的。`--manual-paste` 仅仅改变了回调跳转时的传输方式，并不会导致安全性下降。

## 哪些提供商需要此功能

| 提供商 | 回环端口 | 是否需要隧道 |
|--------|----------|--------------|
| `xai-oauth`（Grok SuperGrok） | `56121` | 当 Hermes 运行在远程时需要 |
| Spotify | `43827` | 当 Hermes 运行在远程时需要 |
| MCP 服务器（`auth: oauth`） | 每个服务器自动选择端口 | 当 Hermes 运行在远程时需要 |
| `anthropic`（Claude Pro/Max） | 无 | 不需要——采用代码粘贴流程 |
| `openai-codex`（ChatGPT Plus/Pro） | 无 | 不需要——采用设备码流程 |
| `minimax`、`nous-portal` | 无 | 不需要——采用设备码流程 |

如果您的提供商不在列表中，则无需使用隧道。

## MCP 服务器

远程 MCP 服务器（如 Linear、Sentry、Atlassian、Asana、Figma 等）都采用相同的回环重定向流程。Hermes 会为每个服务器自动选择一个空闲端口，并在 OAuth 流程启动时输出授权 URL——既可以在启动时（当有新服务器出现在 `mcp_servers:` 设置中时），也可以在运行 `hermes mcp login <server>` 命令时输出。

从远程主机完成授权有两种方式：

**方式 1——将重定向 URL 粘贴回来（无需额外设置，任何地方均可使用）。** 在交互式终端中，Hermes 会在启动本地监听器的同时提示您粘贴重定向 URL。在浏览器中完成授权后，虽然会重定向到 `http://127.0.0.1:<port>/callback`，但会出现连接错误——这是正常现象。请复制**浏览器地址栏中的完整 URL**，然后将其粘贴到 Hermes 的提示框中即可。

```
  MCP OAuth: authorization required.
  Open this URL in your browser:

    https://mcp.linear.app/authorize?response_type=code&...

  Or paste the redirect URL here (or the ?code=...&state=... portion) and press Enter:
> https://mcp.linear.app/callback?code=abc123&state=xyz
  Got authorization code from paste — completing flow.
```

仅包含 `?code=...&state=...` 的查询字符串也是可以接受的。此方法适用于所有采用 `auth: oauth` 认证方式的 MCP 服务器，且无需对 SSH 配置进行任何修改。

**方案 2 — SSH 端口转发（与 xAI/Spotify 方法相同）。** Hermes 会在 SSH 会话提示中显示其绑定的具体端口。请在您的笔记本电脑上打开另一个终端：

```bash
ssh -N -L <port>:127.0.0.1:<port> user@remote-host
```

接着像平常一样在浏览器中打开授权 URL；请求会通过重定向隧道传输，随后监听器会捕获该请求。当需要让流程在无人干预的情况下完成时（例如无法交互式输入的脚本化重新授权场景），可使用此方法。

**常见陷阱——30秒的配置重载时间限制。** 如果在正在运行的 Hermes 会话中编辑 `~/.hermes/config.yaml` 以添加 OAuth MCP 服务器，CLI 会以30秒为超时时间自动重新加载 MCP 连接。这个时间不足以完成交互式的 OAuth 流程，因此重载操作会提前终止。建议改在新的终端中执行 `hermes mcp login <server>` 命令——它没有此类时间限制，会等待长达5分钟直到你输入响应。

## 为何监听器不能直接绑定到 0.0.0.0

xAI 和 Spotify 都会通过白名单机制来验证 `redirect_uri` 参数。两者都要求使用回环地址格式（`http://127.0.0.1:<确切端口>/callback`）。如果将监听器绑定到 `0.0.0.0` 或其他端口，认证服务器会因 redirect_uri 不匹配而拒绝请求。SSH 隧道能够确保回环地址在传输过程中保持完整。

## 分步指南：单次 SSH 跳转

### 1. 在本地机器启动隧道

```bash
# xAI Grok OAuth (port 56121)
ssh -N -L 56121:127.0.0.1:56121 user@remote-host

# Or for Spotify (port 43827)
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

`-N` 的含义是“无需打开远程Shell，仅保持隧道连接状态”。在登录期间，请让此终端持续运行。

### 2. 在另一个SSH会话中，执行auth命令

```bash
ssh user@remote-host
hermes auth add xai-oauth --no-browser
# or for Spotify:
# hermes auth add spotify --no-browser
```

Hermes会检测到SSH连接，跳过浏览器自动打开的步骤，并输出授权URL以及一行“Waiting for callback on http://127.0.0.1:<port>/callback”的提示信息。

### 3. 在本地浏览器中打开该URL

从远程终端复制授权URL，然后粘贴到笔记本电脑上的浏览器中。同意权限确认界面后，认证服务器会将用户重定向至`http://127.0.0.1:<port>/callback`地址。此时浏览器会通过隧道发送请求，该请求会被转发给远程监听器，随后Hermes会显示“Login successful!”的提示。

一旦看到成功提示，即可关闭该隧道（在第一个终端中按下Ctrl+C）。

## 分步指南：通过跳板机操作

如果您是通过堡垒机/跳板主机访问Hermes的，请使用SSH内置的 `-J`（ProxyJump）选项来实现连接。

```bash
ssh -N -L 56121:127.0.0.1:56121 -J jump-user@jump-host user@final-host
```

该功能通过跳板主机建立 SSH 连接，而无需在跳板主机上配置回环端口。您笔记本电脑上的本地地址 `127.0.0.1:56121` 会直接与最终远程主机上的 `127.0.0.1:56121` 建立隧道连接。

对于不支持 `-J` 参数的旧版 OpenSSH，其完整用法如下：

```bash
ssh -N \
    -o "ProxyCommand=ssh -W %h:%p jump-user@jump-host" \
    -L 56121:127.0.0.1:56121 \
    user@final-host
```

## Mosh、tmux 与 ssh ControlMaster 模式

该隧道实际上属于底层 SSH 连接的属性。如果在基于 mosh 会话的 `tmux` 环境中运行 Hermes，mosh 的漫游功能不会自动携带 `-L` 转发功能。请为 `-L` 隧道**单独**开启一个普通的 SSH 会话——正是这个连接需要在身份验证过程中保持活跃状态。而你的交互式 mosh/tmux 会话则可以继续正常运行 Hermes。

如果你使用 `ssh -o ControlMaster=auto`，多路复用连接中的端口转发功能将共享主连接的生命周期。如果隧道无法建立，请重新启动主连接。

```bash
ssh -O exit user@remote-host
ssh -N -L 56121:127.0.0.1:56121 user@remote-host
```

## 故障排除

### `bind [127.0.0.1]:56121: Address already in use`

您的笔记本电脑上已有程序正在使用该端口。要么是之前的隧道连接未能正常关闭，要么是有其他本地 Hermes 实例也在监听该端口。请找到并终止占用该端口的进程：

```bash
# macOS / Linux
lsof -iTCP:56121 -sTCP:LISTEN
kill <PID>
```

请重新执行 `ssh -L` 命令。

### “无法建立连接。我们无法连接到您的应用。”（xAI）

当 xAI 将用户重定向至 `127.0.0.1:<port>/callback` 时，若该地址没有对应的监听进程，其授权页面就会显示此错误信息。这通常是由于隧道未运行、端口号有误，或是您使用了 Hermes 在之前运行时指定的端口号所致——如果首选端口已被占用，系统会自动分配新的端口，请务必查看最新的 “正在等待来自……的回调” 相关提示。

### “xAI 授权过程在等待本地回调时超时”

原因与上述情况相同——重定向请求未能返回。请检查隧道是否仍在运行（执行 `ssh -N` 若无输出，可查看启动隧道的终端窗口），如有必要则重新启动隧道，然后再次运行 `hermes auth add xai-oauth --no-browser`。

### 令牌存储在错误的 `~/.hermes` 文件中

令牌会被保存在执行 `hermes auth add ...` 命令的 Linux 用户对应的目录下。如果您的网关或 systemd 服务是以其他用户身份运行的（例如 `root` 或专用的 `hermes` 用户），则需以**该用户身份**进行认证，这样令牌才会被存储在其 `~/.hermes/auth.json` 文件中。可使用 `sudo -u hermes -i` 或类似命令来实现。

## 相关文档

- [xAI Grok OAuth](./xai-grok-oauth.md)
- [Spotify（通过 SSH 连接）](../user-guide/features/spotify.md#running-over-ssh--in-a-headless-environment)
- [原生 MCP 客户端（OAuth 部分）](../user-guide/features/mcp.md#oauth-authenticated-http-servers)
- [SSH `-J` / ProxyJump（手册页）](https://man.openbsd.org/ssh#J)
