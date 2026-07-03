---
sidebar_position: 17
title: "OAuth over SSH / Remote Hosts"
description: "How to complete browser-based OAuth (Spotify, MCP servers) when Hermes runs on a remote machine, container, or behind a jump box"
---

# 通过 SSH/远程主机进行 OAuth 认证

某些 Hermes 提供方——**Spotify**以及**远程 MCP 服务器**（如 Linear、Sentry、Atlassian、Asana、Figma 等）——采用*回环重定向*式的 OAuth 流程。认证服务器会将你的浏览器重定向至 `http://127.0.0.1:<port>/callback`，这样 Hermes 启动的微型 HTTP 监听器便可获取授权码。

当 Hermes 与浏览器位于同一台机器上时，此方式运行正常。但一旦它们不在同一台机器上，就会出现问题：你的笔记本浏览器试图访问**本机**的 `127.0.0.1`，而监听器实际上绑定在**远程服务器**的 `127.0.0.1` 上。

解决方法是使用一行 SSH 本地转发命令。对于运行在交互式终端中的 MCP 服务器，通常可以直接将重定向地址粘贴回去（无需建立隧道）。

**xAI Grok OAuth (`xai-oauth`) 使用的是 OAuth 设备码**机制，而非回环回调方式——只需在任何浏览器中打开打印出的验证链接，Hermes 便会持续轮询直至获得授权。该方式无需 SSH 隧道。详情请参阅 [xAI Grok OAuth](./xai-grok-oauth.md)。

## 简而言之

```bash
# On your local machine (laptop), in a separate terminal:
ssh -N -L 43827:127.0.0.1:43827 user@remote-host

# In your existing SSH session on the remote machine:
hermes auth add spotify --no-browser
# → Hermes prints an authorize URL. Open it in a browser on your laptop.
# → Your browser redirects to 127.0.0.1:43827/callback, the tunnel forwards
#   the request to the remote listener, login completes.
```

Hermes会在“正在等待……的回调”这一行中显示其绑定的确切端口地址——请直接复制该地址。Spotify的默认端口为`43827`。

## 哪些服务提供商需要此功能

| 服务提供商 | 回环端口 | 是否需要隧道 |
|----------|---------------|----------------|
| Spotify | `43827`（默认值） | 是，当Hermes处于远程模式时 |
| MCP服务器（`auth: oauth`类型） | 每个服务器自动选择端口 | 是，当Hermes处于远程模式时（或需手动粘贴重定向URL） |
| `xai-oauth`（Grok SuperGrok） | 无 | 不需要——采用设备代码流程 |
| `anthropic`（Claude Pro/Max） | 无 | 不需要——采用代码粘贴流程 |
| `openai-codex`（ChatGPT Plus/Pro） | 无 | 不需要——采用设备代码流程 |
| `minimax`、`nous-portal` | 无 | 不需要——采用设备代码流程 |

如果您的服务提供商未列在表格中，则无需使用隧道。

## MCP服务器

远程MCP服务器（如Linear、Sentry、Atlassian、Asana、Figma等）也采用相同的回环重定向流程。Hermes会为每个服务器自动选择一个空闲端口，并在启动OAuth授权流程时显示授权URL——既可能在系统启动时（当有新服务器出现在`mcp_servers:`配置项中时），也可能在您运行`hermes mcp login <server>`命令时显示。

从远程主机完成授权有两种方式：

**方式1——直接粘贴重定向URL（无需额外设置，可在任何地方使用）。**在交互式终端中，Hermes会在启动本地监听器的同时提示您粘贴重定向URL。在浏览器中完成授权后，虽然会跳转至`http://127.0.0.1:<port>/callback`地址，但会出现连接错误——这是正常现象。请复制**浏览器地址栏中的完整URL**，然后将其粘贴到Hermes的提示框中即可：

```
  MCP OAuth: authorization required.
  Open this URL in your browser:

    https://mcp.linear.app/authorize?response_type=code&...

  Or paste the redirect URL here (or the ?code=...&state=... portion) and press Enter:
> https://mcp.linear.app/callback?code=abc123&state=xyz
  Got authorization code from paste — completing flow.
```

仅包含 `?code=...&state=...` 的查询字符串也是可接受的。此方法适用于所有采用 `auth: oauth` 认证方式的 MCP 服务器，且无需修改 SSH 配置。

**方案 2 — SSH 端口转发（与 Spotify 方式相同）。** Hermes 会在 SSH 会话提示中显示其绑定的具体端口。请在笔记本电脑上打开另一个终端：

```bash
ssh -N -L <port>:127.0.0.1:<port> user@remote-host
```

接着像平常一样在浏览器中打开授权地址；请求会通过重定向隧道传输，随后监听器会捕获该请求。当需要让流程在无人干预的情况下完成时（例如无法交互式粘贴的脚本化重新授权场景），可使用此方法。

**常见陷阱——30秒的配置重载时间限制。** 如果在正在运行的Hermes会话中编辑`~/.hermes/config.yaml`以添加OAuth MCP服务器，CLI会以30秒为超时时间自动重载MCP连接。这个时间不足以完成交互式的OAuth流程，因此重载操作会提前终止。建议改在新的终端中使用`hermes mcp login <server>`命令——它没有此类时间限制，会等待长达5分钟直到你输入响应内容。

## 为何监听器不能直接绑定0.0.0.0

Spotify及大多数MCP OAuth服务器都会将`redirect_uri`参数与允许列表进行比对。这两种服务器都要求使用回环地址格式（`http://127.0.0.1:<确切端口>/callback`）。若将监听器绑定到`0.0.0.0`或其他端口，认证服务器会因`redirect_uri`不匹配而拒绝请求。SSH隧道能确保整个传输过程中回环地址的完整性。

## 分步指南：单次SSH跳转

### 1. 在本地机器启动隧道

```bash
# Spotify (port 43827)
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

`-N` 的含义是“无需打开远程Shell，仅保持隧道连接状态”。在登录期间，请让此终端持续运行。

### 2. 在另一个SSH会话中，执行auth命令

```bash
ssh user@remote-host
hermes auth add spotify --no-browser
```

Hermes会检测到SSH连接，跳过浏览器自动打开的步骤，并输出授权URL以及一行“Waiting for callback on http://127.0.0.1:<port>/callback”的提示信息。

### 3. 在本地浏览器中打开该URL

从远程终端复制授权URL，然后粘贴到笔记本电脑上的浏览器中。同意权限确认界面后，认证服务器会将用户重定向至`http://127.0.0.1:<port>/callback`地址。此时浏览器会通过隧道发送请求，该请求会被转发给远程监听器，随后Hermes会显示“Login successful!”的提示。

一旦看到成功提示，即可关闭该隧道（在第一个终端中按下Ctrl+C）。

## 分步指南：通过跳板机操作

如果您是通过堡垒机/跳板主机访问Hermes的，请使用SSH内置的 `-J`（ProxyJump）选项来实现连接。

```bash
ssh -N -L 43827:127.0.0.1:43827 -J jump-user@jump-host user@final-host
```

该功能通过跳板主机建立 SSH 连接，而无需在跳板主机上配置回环端口。您笔记本电脑上的本地地址 `127.0.0.1:43827` 会直接隧穿至最终远程主机上的 `127.0.0.1:43827`。

对于不支持 `-J` 选项的旧版 OpenSSH，其完整用法为：

```bash
ssh -N \
    -o "ProxyCommand=ssh -W %h:%p jump-user@jump-host" \
    -L 43827:127.0.0.1:43827 \
    user@final-host
```

## Mosh、tmux 与 ssh ControlMaster 模式

该隧道实际上属于底层 SSH 连接的属性。如果在基于 mosh 会话的 `tmux` 环境中运行 Hermes，mosh 的漫游功能不会自动携带 `-L` 转发功能。请为 `-L` 隧道**单独**开启一个普通的 SSH 会话——正是这个连接需要在身份验证过程中保持活跃状态。而你的交互式 mosh/tmux 会话则可以继续正常运行 Hermes。

如果你使用 `ssh -o ControlMaster=auto`，多路复用连接中的端口转发功能将共享主连接的生命周期。如果隧道无法建立，请重新启动主连接。

```bash
ssh -O exit user@remote-host
ssh -N -L 43827:127.0.0.1:43827 user@remote-host
```

## 故障排除

### `bind [127.0.0.1]:43827: Address already in use`

您的笔记本电脑上已有程序正在使用该端口。可能是之前的隧道未正确关闭，或是本地运行的 Hermes 也在监听该端口。请找出并终止占用该端口的进程：

```bash
# macOS / Linux
lsof -iTCP:43827 -sTCP:LISTEN
kill <PID>
```

请重新执行 `ssh -L` 命令。

### 等待本地回调时授权超时

重定向请求未能返回到远程监听器。请检查隧道是否仍然处于活跃状态（使用 `ssh -N` 无法查看输出，可查看启动该命令的终端），确认使用的端口与“正在等待……的回调”信息中的端口一致（如果首选端口已被占用，Hermes 可能会自动更换端口），必要时重新建立隧道，然后再执行授权命令。

### Token 存放在了错误的 `~/.hermes` 目录中

Token 会被写入执行 `hermes auth add ...` 命令的 Linux 用户对应的目录下。如果您的网关或 systemd 服务是以其他用户身份运行的（例如 `root` 或专用的 `hermes` 用户），请以**该用户**身份进行授权，这样 Token 才会存储在其 `~/.hermes/auth.json` 文件中。可使用 `sudo -u hermes -i` 或类似的命令来实现。

## 相关内容

- [xAI Grok OAuth](./xai-grok-oauth.md) —— 设备码模式；无需 SSH 隧道
- [Spotify（通过 SSH 连接）](../user-guide/features/spotify.md#running-over-ssh--in-a-headless-environment)
- [原生 MCP 客户端（OAuth 部分）](../user-guide/features/mcp.md#oauth-authenticated-http-servers)
- [SSH `-J` / ProxyJump（手册页）](https://man.openbsd.org/ssh#J)
