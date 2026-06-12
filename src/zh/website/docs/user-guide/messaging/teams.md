---
sidebar_position: 5
title: "Microsoft Teams"
description: "Set up Hermes Agent as a Microsoft Teams bot"
---

# Microsoft Teams 配置

将 Hermes Agent 作为机器人连接到 Microsoft Teams。与 Slack 的 Socket 模式不同，Teams 通过调用**公共 HTTPS webhook**来传递消息，因此您的实例需要一个可公开访问的端点——可以是开发环境隧道（本地调试），也可以是真实域名（生产环境）。

如果需要从 Microsoft Graph 事件中获取会议摘要，而非普通机器人对话内容，请使用专用配置页面：[Teams 会议](/user-guide/messaging/teams-meetings)。

> 运行 `hermes gateway setup` 并选择 **Microsoft Teams**，即可获得引导式配置步骤。

## 机器人的响应方式

| 场景 | 行为 |
|------|------|
| **个人聊天（私信）** | 机器人会回复每条消息，无需使用 @mention。 |
| **群组聊天** | 仅当被 @提及时，机器人才会回复。 |
| **频道聊天** | 仅当被 @提及时，机器人才会回复。 |

Teams 会将 @提及以带有 `<at>BotName</at>` 标签的普通消息形式发送，Hermes 会在处理消息前自动移除这些标签。

---

## 第 1 步：安装 Teams CLI

`@microsoft/teams.cli` 可自动化完成机器人注册流程——无需使用 Azure 门户。

```bash
npm install -g @microsoft/teams.cli@preview
teams login
```

为验证您的登录身份并查询您自己的 AAD 对象 ID（该 ID 是设置 `TEAMS_ALLOWED_USERS` 所需的）：

```bash
teams status --verbose
```

## 第 2 步：开放 Webhook 端口

Teams 无法向 `localhost` 发送消息。在本地开发时，需使用任意隧道工具来获取一个公开的 HTTPS 地址。默认端口为 `3978`，如有需要可通过 `TEAMS_PORT` 参数进行修改。

```bash
# devtunnel (Microsoft)
devtunnel create hermes-bot --allow-anonymous
devtunnel port create hermes-bot -p 3978 --protocol https  # replace 3978 with TEAMS_PORT if changed
devtunnel host hermes-bot

# ngrok
ngrok http 3978  # replace 3978 with TEAMS_PORT if changed

# cloudflared
cloudflared tunnel --url http://localhost:3978  # replace 3978 with TEAMS_PORT if changed
```

从输出结果中复制 `https://` 开头的网址——您将在下一步中使用它。在开发过程中请保持隧道处于运行状态。

对于生产环境，应将机器人的端点指向您服务器的公网域名（详见[生产环境部署](#production-deployment)）。

---

## 第3步：创建机器人

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

```bash
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d gateway
```

这将启动网关。默认的 Webhook 端口为 `3978`（可通过 `TEAMS_PORT` 参数进行覆盖）。请确认该服务正在运行：

```bash
curl http://localhost:3978/health   # should return: ok
docker logs -f hermes
```

请查找：
```
[teams] Webhook server listening on 0.0.0.0:3978/api/messages
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
| `TEAMS_HOME_CHANNEL_NAME` | 主页频道的显示名称 |
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

当智能体需要执行可能具有危险性的命令时，它会发送一张包含四个按钮的自适应卡片，而无需让用户输入 `/approve` 命令：

- **允许一次** — 仅批准当前该命令
- **允许本次会话** — 批准本次会话中该类型的命令
- **始终允许** — 永久批准该类型的命令
- **拒绝** — 拒绝执行该命令

点击任意按钮即可立即完成审批，并用审批结果替换原有卡片。

### 会议摘要发送（Teams 会议流程）

当启用 [Teams 会议流程插件](/user-guide/messaging/msgraph-webhook) 后，该适配器可统一处理会议摘要的发送工作——仅需一个 Teams 集成接口，而非两个。在会议记录被汇总后，系统会自动将摘要发布到您指定的 Teams 目标地址。

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

| 模式 | 适用场景 | 权衡点 |
|------|----------|--------|
| `incoming_webhook` | 简单的“将摘要发布到此频道”功能，使用 Teams 生成的静态 URL。 | 不支持回复串行化，不支持表情反应，内容将以 webhook 配置的标识显示。 |
| `graph` | 通过 Microsoft Graph 实现频道内的串行化帖子发布，或以机器人身份在一对一/群组聊天中发帖。 | 需要完成[Graph 应用注册](/guides/microsoft-graph-app-registration)，并申请 `ChannelMessage.Send`（频道）或 `Chat.ReadWrite.All`（聊天）应用权限。 |

如果未启用 `teams_pipeline` 插件，这些设置将处于无效状态——只有当管道运行时绑定到 Graph webhook 入口时，它们才会被激活。

---

## 生产环境部署

对于永久运行的服务器，请跳过 devtunnel，将您的机器人注册到服务器的公共 HTTPS 端点上：

```bash
teams app create \
  --name "Hermes" \
  --endpoint "https://your-domain.com/api/messages"
```

如果您已经创建了该机器人，仅需更新端点地址即可：

```bash
teams app update --id <teamsAppId> --endpoint "https://your-domain.com/api/messages"
```

请确保您配置的端口（`TEAMS_PORT`，默认值为 `3978`）可从互联网访问，同时您的 TLS 证书也必须有效——Teams 不支持自签名证书。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `health` 接口正常，但机器人无响应 | 检查隧道是否仍在运行，以及机器人的消息接收端点是否与隧道 URL 匹配 |
| 日志中出现 `KeyError: 'teams'` 错误 | 重启容器——当前版本已修复此问题 |
| 机器人返回身份验证错误 | 确认 `TEAMS_CLIENT_ID`、`TEAMS_CLIENT_SECRET` 和 `TEAMS_TENANT_ID` 均已正确设置 |
| 显示“未配置推理提供程序” | 检查 `~/.hermes/.env` 文件中是否已设置 `ANTHROPIC_API_KEY`（或其他提供程序密钥） |
| 机器人能接收消息但直接忽略 | 您的 AAD 对象 ID 可能未添加到 `TEAMS_ALLOWED_USERS` 中。请运行 `teams status --verbose` 查找该 ID |
| 重启后隧道 URL 发生变化 | 如果使用命名隧道（如 `devtunnel create hermes-bot`），devtunnel URL 是持久有效的。而 ngrok 和 cloudflared 除非您购买了付费套餐，否则每次运行都会生成新 URL——URL 变更时请通过 `teams app update` 更新机器人端点 |
| Teams 显示“该机器人无响应” | Webhook 返回了错误。请查看 `docker logs hermes` 以获取错误详情 |
| 日志中出现 `[teams] Failed to connect` 错误 | SDK 身份验证失败。请仔细核对您的凭证，确保租户 ID 与您在 `teams login` 中使用的账户一致 |

---

## 安全性

:::warning
**务必设置 `TEAMS_ALLOWED_USERS`**，并填入经授权用户的 AAD 对象 ID。如果不这样做，任何找到或安装了您机器人的用户都可能与其交互。

请将 `TEAMS_CLIENT_SECRET` 视为密码——建议通过 Azure 门户或 Teams CLI 定期更换它。
:::

- 将凭证存储在 `~/.hermes/.env` 文件中，并设置 `600` 权限（执行 `chmod 600 ~/.hermes/.env`）
- 机器人仅接受来自 `TEAMS_ALLOWED_USERS` 中用户的消息；未经授权的消息将被直接忽略
- 您的公共端点（`/api/messages`）由 Teams Bot Framework 进行身份验证——缺少有效 JWT 的请求将被拒绝

## 相关文档

- [Teams 会议功能](/user-guide/messaging/teams-meetings)
- [操作 Teams 会议流程](/guides/operate-teams-meeting-pipeline)
