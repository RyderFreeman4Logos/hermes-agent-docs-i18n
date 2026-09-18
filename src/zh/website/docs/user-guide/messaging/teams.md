---
sidebar_position: 5
title: "Microsoft Teams"
description: "Set up Hermes Agent as a Microsoft Teams bot"
---

# Microsoft Teams 设置

需将 Hermes Agent 作为机器人连接到 Microsoft Teams。与 Slack 的 Socket 模式不同，Teams 通过调用**公共 HTTPS webhook**来传递消息，因此您的实例需要一个可公开访问的端点——可以是开发隧道（本地测试环境），也可以是真实域名（生产环境）。

如果需要从 Microsoft Graph 事件中获取会议摘要而非普通机器人对话内容，请使用专用设置页面：[Teams 会议](/user-guide/messaging/teams-meetings)。

> 运行 `hermes gateway setup` 并选择 **Microsoft Teams**，即可获得引导式设置步骤。

## 机器人的响应方式

| 场景 | 行为 |
|------|------|
| **个人聊天（私信）** | 机器人会回复每条消息，无需使用 @mention。 |
| **群组聊天** | 仅当被 @提及时，机器人才会回复。 |
| **频道聊天** | 仅当被 @提及时，机器人才会回复。 |

Teams 会将 @提及以带有 `<at>BotName</at>` 标签的普通消息形式发送，Hermes 会在处理前自动移除这些标签。

---

对于源码安装或本地安装版本，需包含 Teams 相关组件，以便打包的适配器能够导入 Microsoft Teams SDK：

```bash
uv sync --extra teams
# or, for editable installs:
uv pip install -e ".[teams]"
```

## 第一步：安装 Teams CLI

`@microsoft/teams.cli` 可自动完成机器人注册流程——无需使用 Azure 门户。

```bash
npm install -g @microsoft/teams.cli@preview
teams login
```

为验证您的登录身份并查询您自己的 AAD 对象 ID（`TEAMS_ALLOWED_USERS` 功能所需）：

```bash
teams status --verbose
```

## 第 2 步：开放 Webhook 端口

Teams 无法向 `localhost` 发送消息。在本地开发时，需使用任意隧道工具来获取一个公开的 HTTPS 地址。默认端口为 `3978`，如有需要，可通过 `TEAMS_PORT` 参数进行修改。

```bash
# devtunnel (Microsoft)
devtunnel create hermes-bot --allow-anonymous
devtunnel port create hermes-bot -p 3978 --protocol http  # replace 3978 with TEAMS_PORT if changed
devtunnel host hermes-bot

# ngrok
ngrok http 3978  # replace 3978 with TEAMS_PORT if changed

# cloudflared
cloudflared tunnel --url http://localhost:3978  # replace 3978 with TEAMS_PORT if changed
```

从输出结果中复制 `https://` 开头的网址——您将在下一步中使用它。在开发过程中请保持隧道处于运行状态。

公共隧道的网址使用 HTTPS 协议，但 Hermes 的本地 webhook 监听器则使用普通的 HTTP 协议。该隧道会终止 TLS 加密并将 HTTP 请求转发到端口 `3978`；因此请勿将本地隧道的端口配置为 HTTPS。

在正式部署时，请将机器人的端点指向您服务器的公共域名（详见[生产环境部署](#production-deployment)部分）。

---

## 第 3 步：创建机器人

```bash
teams app create \
  --name "Hermes" \
  --endpoint "https://<your-tunnel-url>/api/messages"
```

CLI会输出您的`CLIENT_ID`、`CLIENT_SECRET`和`TENANT_ID`，同时还会提供第6步的安装链接。请务必保存好客户端密钥，因为它不会再显示一次。

---

## 第4步：配置环境变量

在`~/.hermes/.env`文件中添加以下内容：

```bash
# Required
TEAMS_CLIENT_ID=<your-client-id>
TEAMS_CLIENT_SECRET=<your-client-secret>
TEAMS_TENANT_ID=<your-tenant-id>

# Restrict access to specific users (recommended)
# Use AAD object IDs from `teams status --verbose`
TEAMS_ALLOWED_USERS=<your-aad-object-id>
```

## 第 5 步：启动网关

**Docker**（必须从包含 `docker-compose.yml` 的目录中运行——通常是您克隆的 `hermes-agent` 代码库，而非 `~` 目录）：

```bash
cd /path/to/hermes-agent
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d gateway
```

**原生安装/Systemd安装**（通常为在 `~/.hermes/hermes-agent` 目录下执行的简短 `hermes` 安装命令）：

```bash
hermes gateway restart
# or foreground: hermes gateway run
```

Teams SDK属于可选组件；当启用Teams功能后，网关会在首次启动时自动将其懒加载到Hermes自身的虚拟环境中（请勿在Ubuntu 24.04系统上使用`pip install`命令进行安装——该操作会违反PEP 668中关于“外部管理环境”的规定）。如需手动将其安装到Hermes的虚拟环境中：

```bash
~/.hermes/hermes-agent/venv/bin/pip install microsoft-teams-apps aiohttp
# or from a clone of the agent: uv sync --extra teams
```

默认的 Webhook 端口为 `3978`（可通过 `TEAMS_PORT` 参数进行覆盖）。请确认该端口正在运行中：

```bash
curl http://localhost:3978/health   # should return: ok
# Docker:
docker logs -f hermes
# Native:
hermes gateway status -l
```

请查找：
```
[teams] Webhook server listening on * (all interfaces, IPv4+IPv6):3978/api/messages
```

## 第 6 步：在 Teams 中安装该应用

```bash
teams app get <teamsAppId> --install-link
```

在浏览器中打开该打印出的链接——它将直接在 Teams 客户端中打开。安装完成后，向您的机器人发送私信即可，此时机器人已准备就绪。

---

## 配置参考

### 环境变量

| 变量 | 描述 |
|------|------|
| `TEAMS_CLIENT_ID` | Azure AD 应用（客户端）ID |
| `TEAMS_CLIENT_SECRET` | Azure AD 客户端密钥 |
| `TEAMS_TENANT_ID` | Azure AD 租户 ID |
| `TEAMS_ALLOWED_USERS` | 以逗号分隔的、允许使用该机器人的 AAD 对象 ID |
| `TEAMS_ALLOW_ALL_USERS` | 设置为 `true` 可跳过白名单，允许任何人使用 |
| `TEAMS_HOME_CHANNEL` | 用于定时/主动发送消息的对话 ID |
| `TEAMS_HOME_CHANNEL_NAME` | 主页通道的显示名称 |
| `TEAMS_PORT` | Webhook 端口（默认值：`3978`） |

### config.yaml

或者，也可以通过 `~/.hermes/config.yaml` 进行配置：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      client_id: "your-client-id"
      client_secret: "your-secret"
      tenant_id: "your-tenant-id"
      port: 3978
```

## 功能特性

### 交互式审批卡片

当智能体需要执行可能具有风险的命令时，它会发送一张包含四个按钮的自适应卡片，而无需让您手动输入 `/approve` 命令：

- **允许一次** — 仅批准当前该命令
- **允许本次会话** — 批准该命令模式在本次会话中的后续使用
- **始终允许** — 永久批准该命令模式
- **拒绝** — 拒绝执行该命令

点击任意按钮即可即时完成审批，并用审批结果替换原有卡片。

### 会议摘要发送（Teams 会议流程）

当启用 [Teams 会议流程插件](/user-guide/messaging/msgraph-webhook) 后，此适配器可统一处理会议摘要的发送工作——仅需一个 Teams 集成接口，而非两个。在会议记录被汇总后，系统会自动将摘要发布到您指定的 Teams 目标地址。

会议摘要发送功能可在 `teams` 平台配置项下与机器人配置一同设置：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      # existing bot config (client_id, client_secret, tenant_id, port) ...

      # Meeting summary delivery (only used when the teams_pipeline plugin is enabled)
      delivery_mode: "graph"       # or "incoming_webhook"
      # For delivery_mode: graph — pick ONE of:
      chat_id: "19:meeting_..."    # post into a Teams chat
      # team_id: "..."             # OR post into a channel
      # channel_id: "..."
      # access_token: "..."        # optional; falls back to MSGRAPH_* app credentials
      # For delivery_mode: incoming_webhook:
      # incoming_webhook_url: "https://outlook.office.com/webhook/..."
```

| 模式 | 适用场景 | 权衡取舍 |
|------|----------|---------|
| `incoming_webhook` | 简单的“将摘要发布到此频道”功能，使用Teams自动生成的静态URL。 | 不支持回复线程、无表情符号功能，内容会以webhook配置的身份显示。 |
| `graph` | 通过Microsoft Graph以线程形式在频道中发布内容，或以机器人身份在1:1/群组聊天中发送消息。 | 需要完成[Graph应用注册](/guides/microsoft-graph-app-registration)，并申请`ChannelMessage.Send`（频道）或`Chat.ReadWrite.All`（聊天）应用权限。 |

如果未启用`teams_pipeline`插件，这些设置将处于无效状态——只有当管道运行时绑定到Graph webhook入口时，它们才会被激活。

---

## 生产环境部署

对于永久运行的服务器，应在反向代理层终止TLS加密，然后将请求转发至普通的HTTP Hermes监听器，通常地址为`http://127.0.0.1:3978`。需将代理的公共HTTPS端点注册到Teams中：

```bash
teams app create \
  --name "Hermes" \
  --endpoint "https://your-domain.com/api/messages"
```

如果您已经创建了该机器人，仅需更新端点地址即可：

```bash
teams app update --id <teamsAppId> --endpoint "https://your-domain.com/api/messages"
```

请确保该公共 HTTPS 端点可从互联网访问，并且使用了有效的 TLS 证书。Teams 不支持自签名证书。请将 Hermes 监听器置于代理服务器之后；端口 `3978` 本身并不提供 HTTPS 服务。

---

## 故障排除

| Problem | Solution |
|---------|----------|
| `Can't find a suitable configuration file` from `docker compose` | You are not in the repo that has `docker-compose.yml`, or you are on a native install — use `hermes gateway restart` instead, or `cd` into the clone first |
| `requirements not met` / `Teams SDK missing` / `No adapter available for teams` | Restart gateway so lazy-install can run, or install into the **Hermes venv**: `~/.hermes/hermes-agent/venv/bin/pip install microsoft-teams-apps aiohttp`. System `pip` fails on Ubuntu 24.04 (PEP 668) and would not affect the service anyway |
| `health` endpoint works but bot doesn't respond | Check that your tunnel is still running and the bot's messaging endpoint matches the tunnel URL |
| Logs show `"UNKNOWN / HTTP/1.0" 400` when Teams sends a message | The tunnel or reverse proxy is forwarding HTTPS to Hermes' plain HTTP listener. Terminate TLS at the proxy and forward HTTP to port `3978` |
| `KeyError: 'teams'` in logs | Restart the container — this is fixed in the current version |
| Bot responds with auth errors | Verify `TEAMS_CLIENT_ID`, `TEAMS_CLIENT_SECRET`, and `TEAMS_TENANT_ID` are all set correctly |
| `No inference provider configured` | Check that `ANTHROPIC_API_KEY` (or another provider key) is set in `~/.hermes/.env` |
| Bot receives messages but ignores them | Your AAD object ID may not be in `TEAMS_ALLOWED_USERS`. Run `teams status --verbose` to find it |
| Tunnel URL changes on restart | devtunnel URLs are persistent if you use a named tunnel (`devtunnel create hermes-bot`). ngrok and cloudflared generate a new URL each run unless you have a paid plan — update the bot endpoint with `teams app update` when it changes |
| Teams shows "This bot is not responding" | The webhook returned an error. Check `docker logs hermes` / `hermes gateway status -l` for tracebacks |
| `[teams] Failed to connect` in logs | The SDK failed to authenticate. Double-check your credentials and that the tenant ID matches the account you used in `teams login` |

## 安全性

:::warning
**务必设置 `TEAMS_ALLOWED_USERS`，并填入已授权用户的 AAD 对象 ID。** 如果不这样做，任何能够找到或安装您的机器人的用户都可能与其进行交互。

请将 `TEAMS_CLIENT_SECRET` 视为密码——需通过 Azure 门户或 Teams CLI 定期更换。
:::

- 将凭证存储在 `~/.hermes/.env` 文件中，并设置权限为 `600`（执行 `chmod 600 ~/.hermes/.env` 命令）
- 该机器人仅接受来自 `TEAMS_ALLOWED_USERS` 中用户的消息；未经授权的消息将被直接忽略
- 您的公共端点（`/api/messages`）由 Teams Bot Framework 进行身份验证——缺少有效 JWT 的请求将被拒绝

## 相关文档

- [Teams 会议功能](/user-guide/messaging/teams-meetings)
- [操作 Teams 会议流程](/guides/operate-teams-meeting-pipeline)
