---
sidebar_position: 17
title: "OAuth over SSH / Remote Hosts"
description: "How to complete browser-based OAuth (Spotify, MCP servers) when Hermes runs on a remote machine, container, or behind a jump box"
---

# 通过 SSH/远程主机进行 OAuth 认证

某些 Hermes 提供商——**Spotify**以及**远程 MCP 服务器**（如 Linear、Sentry、Atlassian、Asana、Figma 等）——采用*回环重定向*型 OAuth 流程。认证服务器会将你的浏览器重定向至 `http://127.0.0.1:<port>/callback`，这样 Hermes 启动的微型 HTTP 监听器就能获取授权码。

当 Hermes 和浏览器位于同一台机器上时，此方式运行完美。但一旦它们不在同一台机器上，就会出现问题：你的笔记本浏览器试图连接到**本机**的 `127.0.0.1`，而监听器实际上绑定在**远程服务器**上的 `127.0.0.1`。

解决方法是使用一行 SSH 本地转发命令。对于运行在交互式终端中的 MCP 服务器，通常可以直接将重定向地址粘贴回去（无需建立隧道）。

**xAI Grok OAuth（`xai-oauth`）采用 OAuth 设备码**机制，而非回环回调方式——只需在任何浏览器中打开打印出的验证地址，Hermes 便会持续轮询直至获得授权。该方式无需 SSH 隧道。详情请参阅 [xAI Grok OAuth](./xai-grok-oauth.md)。

## 总结

```bash
# On your local machine (laptop), in a separate terminal:
ssh -N -L 43827:127.0.0.1:43827 user@remote-host

# In your existing SSH session on the remote machine:
hermes auth spotify --no-browser
# → Hermes prints an authorize URL. Open it in a browser on your laptop.
# → Your browser redirects to 127.0.0.1:43827/callback, the tunnel forwards
#   the request to the remote listener, login completes.
```

Hermes会在“Waiting for callback on ...”这一行显示其绑定的确切端口——请从该行复制该端口。Spotify的默认端口为`43827`。

## 哪些服务提供商需要此设置

| 服务提供商 | 回环端口 | 是否需要隧道？ |
|----------|---------------|----------------|
| Spotify | `43827`（默认值） | 是，当Hermes处于远程模式时需要 |
| MCP服务器（`auth: oauth`类型） | 每个服务器自动确定 | 是，当Hermes处于远程模式时需要（或需粘贴重定向URL） |
| `xai-oauth`（Grok SuperGrok） | 无 | 不需要——采用设备代码流程 |
| `anthropic`（Claude Pro/Max） | 无 | 不需要——采用代码粘贴流程 |
| `openai-codex`（ChatGPT Plus/Pro） | 无 | 不需要——采用设备代码流程 |
| `minimax`、`nous-portal` | 无 | 不需要——采用设备代码流程 |

如果您的服务提供商未列在表格中，则无需使用隧道。

## MCP服务器

**桌面端技能 → MCP**：该原生应用会在您的电脑上接收回调信号，并将其转发至选定的连接和配置文件，因此此流程不需要SSH回调隧道或`dashboard.public_url`。令牌将保留在对应的后端配置文件中。离开MCP选项卡或更改其作用范围会导致正在进行的登录过程取消。如果桌面端应用要求您更新后端，请先完成更新后再尝试操作；它不会自动切换到远程HTTP回调方式。以下的终端工作流保持不变。

远程 MCP 服务器（如 Linear、Sentry、Atlassian、Asana、Figma 等）均采用相同的回环重定向流程。Hermes 会为每个服务器自动选择一个空闲端口，并在 OAuth 流程启动时输出授权 URL——这可能发生在程序启动时（即当有新服务器被添加到 `mcp_servers:` 配置中时），也可能在你运行 `hermes mcp login <server>` 命令时。

从远程主机完成授权有两种方式：

**方案 1：将重定向 URL 粘贴回本地（无需额外设置，可在任何地方使用）。** 在交互式终端中，Hermes 会在启动本地监听器的同时提示你粘贴重定向 URL。在浏览器中完成授权后，虽然会跳转至 `http://127.0.0.1:<port>/callback`，但会出现连接错误——这是正常现象。请复制**浏览器地址栏中的完整 URL**，然后将其粘贴到 Hermes 的提示框中即可。

```
  MCP OAuth: authorization required.
  Open this URL in your browser:

    https://mcp.linear.app/authorize?response_type=code&...

  Or paste the redirect URL here (or the ?code=...&state=... portion) and press Enter:
> https://mcp.linear.app/callback?code=abc123&state=xyz
  Got authorization code from paste — completing flow.
```

仅包含 `?code=...&state=...` 的查询字符串也是可接受的。此方法适用于所有采用 `auth: oauth` 认证方式的 MCP 服务器，且无需对 SSH 配置进行任何修改。

**方案 2 — SSH 端口转发（与 Spotify 方法相同）。** Hermes 会在 SSH 会话提示信息中显示其绑定的具体端口。请在笔记本电脑上打开另一个终端：

```bash
ssh -N -L <port>:127.0.0.1:<port> user@remote-host
```

接着在浏览器中正常打开授权 URL 即可；重定向请求会通过隧道传输，随后监听器会捕获该请求。当需要让流程在无人干预的情况下完成时（例如无法交互式粘贴的脚本化重新授权场景），可使用此方法。

**注意事项——30 秒的配置重载时间限制。** 如果在正在运行的 Hermes 会话中编辑 `~/.hermes/config.yaml` 以添加 OAuth MCP 服务器，CLI 会以 30 秒为超时时间自动重载 MCP 连接。这个时间不足以完成交互式的 OAuth 流程，因此重载操作会提前终止。此时应改在全新的终端中执行 `hermes mcp login <server>` 命令——该命令没有此类时间限制，会持续等待长达 5 分钟，直到你输入响应内容。

## 为何监听器不能直接绑定 0.0.0.0

Spotify 以及大多数 MCP OAuth 服务器都会根据允许列表来验证 `redirect_uri` 参数。这两种服务器都要求使用回环地址格式（`http://127.0.0.1:<确切端口>/callback`）。如果将监听器绑定到 `0.0.0.0` 或其他端口，认证服务器会因 redirect_uri 不匹配而拒绝请求。SSH 隧道能够确保整个传输过程中回环地址的完整性。

## 分步指南：单次 SSH 跳转

### 1. 在本地机器上启动隧道

```bash
# Spotify (port 43827)
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

`-N` 的含义是“无需打开远程 Shell，只需保持隧道处于开启状态”。在登录期间，请让此终端持续运行。

### 2. 在另一个 SSH 会话中，执行认证命令

```bash
ssh user@remote-host
hermes auth spotify --no-browser
```

Hermes会检测到SSH会话，从而跳过浏览器的自动打开流程，并输出授权URL以及一行“Waiting for callback on http://127.0.0.1:<port>/callback”的提示信息。

### 3. 在本地浏览器中打开该URL

从远程终端复制授权URL，然后粘贴到笔记本电脑上的浏览器中。同意权限授予页面上的要求后，认证服务器会将用户重定向至`http://127.0.0.1:<port>/callback`地址。此时浏览器会通过隧道发送请求，该请求会被转发给远程监听器，随后Hermes会显示“Login successful!”的提示。

一旦看到成功提示，即可关闭该隧道（在第一个终端中按下Ctrl+C）。

## 分步指南：通过跳板机操作

如果您是通过堡垒机/跳板主机访问Hermes的，请使用SSH内置的 `-J`（ProxyJump）选项来实现连接。

```bash
ssh -N -L 43827:127.0.0.1:43827 -J jump-user@jump-host user@final-host
```

该功能通过跳板主机建立 SSH 连接，而无需在跳板主机上配置回环端口。您笔记本电脑上的本地地址 `127.0.0.1:43827` 会直接与最终远程主机上的 `127.0.0.1:43827` 建立隧道连接。

对于不支持 `-J` 参数的旧版 OpenSSH，其完整用法为：

```bash
ssh -N \
    -o "ProxyCommand=ssh -W %h:%p jump-user@jump-host" \
    -L 43827:127.0.0.1:43827 \
    user@final-host
```

## Mosh、tmux 与 ssh ControlMaster

该隧道实际上属于底层的 SSH 连接。如果您在基于 mosh 会话的 `tmux` 环境中运行 Hermes，那么 mosh 的漫游功能不会自动携带 `-L` 转发功能。请为 `-L` 隧道**单独**开启一个普通的 SSH 会话——正是这个连接需要在身份验证过程中保持活跃状态。而您的交互式 mosh/tmux 会话则可以继续正常运行 Hermes。

如果您使用 `ssh -o ControlMaster=auto`，则在多路复用连接上的端口转发功能会共享主连接的生命周期。如果隧道无法建立，请重新启动主连接。

```bash
ssh -O exit user@remote-host
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

## 故障排除

### `bind [127.0.0.1]:43827: Address already in use`

您的笔记本电脑上已有程序正在使用该端口。可能是之前的隧道未正常关闭，或者还有其他本地 Hermes 实例也在监听该端口。请找到并终止导致问题的进程：

```bash
# macOS / Linux
lsof -iTCP:43827 -sTCP:LISTEN
kill <PID>
```

请重新执行 `ssh -L` 命令。

### 等待本地回调时授权超时

重定向请求未能返回到远程监听器。请检查隧道是否仍然处于活跃状态（使用 `ssh -N` 无输出时，请查看启动该命令的终端），确认所使用的端口与“正在等待……的回调”信息中的端口一致（如果首选端口已被占用，Hermes 可能会自动更换端口），必要时重新建立隧道，然后再执行授权命令。

### Token 存放在错误的 `~/.hermes` 目录中

Token 会被写入执行 `hermes auth add ...` 命令的 Linux 用户的目录下。如果您的网关或 systemd 服务是以其他用户身份运行的（例如 `root` 或专用的 `hermes` 用户），则需以**该用户**身份进行授权，这样 Token 才会存储在其 `~/.hermes/auth.json` 文件中。可使用 `sudo -u hermes -i` 或类似命令来实现。

## 相关文档

- [xAI Grok OAuth](./xai-grok-oauth.md) —— 设备码模式；无需 SSH 隧道
- [Spotify（通过 SSH 连接）](../user-guide/features/spotify.md#running-over-ssh--in-a-headless-environment)
- [原生 MCP 客户端（OAuth 部分）](../user-guide/features/mcp.md#oauth-authenticated-http-servers)
- [SSH `-J` / ProxyJump（手册页）](https://man.openbsd.org/ssh#J)
