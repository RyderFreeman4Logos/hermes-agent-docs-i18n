---
sidebar_position: 23
title: "Microsoft Graph Webhook Listener"
description: "Receive Microsoft Graph change notifications (meetings, calendar, chat, etc.) in Hermes"
---

# Microsoft Graph Webhook 监听器

`msgraph_webhook` 网关平台是一种入站事件监听器。它负责让 Hermes 接收来自 Microsoft Graph 的**变更通知**——例如“某个 Teams 会议已结束”、“此聊天中出现了新消息”、“该日历事件已被更新”等。与用户主动输入指令的 `teams` 平台不同，这种机制是 M365 主动向 Hermes 报告发生了某些事件，而非由人工操作。

目前，该监听器的主要使用者是 Teams 会议摘要处理流程：当会议生成文字记录时，Microsoft Graph 会发出通知，处理流程随即获取这些记录，随后 Hermes 会将摘要发布回 Teams。其他 Microsoft Graph 资源（如 `/chats/.../messages`、`/users/.../events`）也使用相同的监听器——不过相应的处理流程会有各自的 Pull Request。

## 先决条件

- Microsoft Graph 应用程序凭据——[注册 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration)
- 一个 Microsoft Graph 能够访问的**公共 HTTPS 地址**（Graph 不会调用私有端点）。开发测试时可使用开发隧道，而正式环境则需要具备有效证书的真实域名。
- 一个强加密的共享密钥，用作 `clientState` 值。可通过 `openssl rand -hex 32` 生成该密钥，并将其作为 `MSGRAPH_WEBHOOK_CLIENT_STATE` 的值保存在 `~/.hermes/.env` 文件中。

## 快速入门

最简版的 `~/.hermes/config.yaml` 文件如下：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8646
      client_state: "replace-with-a-strong-secret"
      accepted_resources:
        - "communications/onlineMeetings"
```

或者通过 `~/.hermes/.env` 文件中的环境变量设置（在启动时自动合并）：

```bash
MSGRAPH_WEBHOOK_ENABLED=true
MSGRAPH_WEBHOOK_PORT=8646
MSGRAPH_WEBHOOK_CLIENT_STATE=<generate-with-openssl-rand-hex-32>
MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES=communications/onlineMeetings
```

注意：绑定主机地址取自 `config.yaml` 文件中的 `extra.host` 参数（参见上文示例）；目前不支持通过 `MSGRAPH_WEBHOOK_HOST` 环境变量来覆盖该设置。

启动网关命令为：`hermes gateway run`。该网关会暴露以下接口：

- `POST /msgraph/webhook` —— 接收来自 Graph 的变更通知
- `GET /msgraph/webhook?validationToken=...` —— 进行 Graph 订阅验证
- `GET /health` —— 提供健康检查接口，同时显示已处理和重复的请求数

您需要通过反向代理、开发隧道或入口网关等方式将上述监听端口公开。用于 Graph 订阅的通知地址即为您的公共 HTTPS 地址后加上 `/msgraph/webhook` 路径。

```
https://ops.example.com/msgraph/webhook
```

## 配置

所有设置均位于 `platforms.msgraph_webhook.extra` 下：

| 设置项 | 默认值 | 描述 |
|--------|--------|------|
| `host` | `0.0.0.0` | HTTP 监听器的绑定地址。非回环绑定需要设置 `allowed_source_cidrs`；使用回环地址（`127.0.0.1` / `::1`）可最简便地搭建开发隧道或反向代理。 |
| `port` | `8646` | 绑定端口。 |
| `webhook_path` | `/msgraph/webhook` | Graph 发送 POST 请求的 URL 路径。 |
| `health_path` | `/health` | 可用性检查端点。 |
| `client_state` | — | Graph 会在每条通知中回显的共享密钥。建议使用与 `hmac.compare_digest` 相同的方法生成，即通过 `openssl rand -hex 32` 生成。 |
| `accepted_resources` | `[]`（接受所有） | 允许的 Graph 资源路径/模式列表。末尾的 `*` 表示前缀匹配，开头的 `/` 也可被接受。示例：`["communications/onlineMeetings", "chats/*/messages"]`。 |
| `max_seen_receipts` | `5000` | 用于去重通知 ID 的缓存大小。达到上限时，最旧的条目将被移除。 |
| `allowed_source_cidrs` | `[]` | 非回环绑定时必需。仅当监听器绑定到回环地址且由本地隧道/反向代理代理时，方可留空。 |

大多数设置还对应有环境变量（`MSGRAPH_WEBHOOK_*`），这些变量会在网关启动时合并到配置中（`host` 除外，它仅通过配置设置——详见上文说明）——更多信息请参阅[环境变量参考](/reference/environment-variables#microsoft-graph-teams-meetings)。

## 安全强化措施

### `clientState` 是主要的身份验证机制

每条 Graph 通知都会包含您的订阅所注册的 `clientState` 字符串。监听器会通过时间安全的比较方式，拒绝任何 `clientState` 不匹配的通知。这是微软官方规定的机制——应将该值视为强共享密钥。

如果未设置 `client_state`，监听器将拒绝启动。

### 源 IP 允许列表（生产环境部署）

在生产环境中，建议将监听器的访问范围限制在微软公布的 Graph webhook 允许的源 IP 范围内。微软在[Office 365 IP 地址和 URL Web 服务](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges)中列出了这些允许的 IP 范围。配置方法如下：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      host: 0.0.0.0
      client_state: "..."
      allowed_source_cidrs:
        - "52.96.0.0/14"
        - "52.104.0.0/14"
        # ...add the current Microsoft 365 "Common" + "Teams" category egress ranges
```

或者作为环境变量设置：

```bash
MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS="52.96.0.0/14,52.104.0.0/14"
```

如果在启动时未设置 `allowed_source_cidrs`，则无法将 Hermes 绑定到诸如 `0.0.0.0`、`::` 或局域网 IP 这类非回环地址上。若在同一台机器上使用了开发隧道或反向代理，请将 Hermes 绑定到 `127.0.0.1` 或 `::1`，并保持允许列表为空。无效的 CIDR 字符串仅会记录警告信息并被忽略。**请每季度查看一次 Microsoft 的 IP 列表**，因为该列表会定期更新。

### HTTPS 终止处理

监听器仅支持传输纯 HTTP 流量。应在反向代理（如 Caddy、Nginx、Cloudflare Tunnel、AWS ALB）处完成 TLS 终止处理，再通过本地网络将请求转发给监听器。Graph 服务不会向非 HTTPS 端点发送数据，因此加密流量无法直接从 Graph 本身到达您的服务器。

### 响应格式规范

成功处理请求时，监听器会返回状态码 `202 Accepted`，且响应体为空——内部计数信息不会包含在网络响应中。操作人员可通过 `/health` 接口查看相关计数，该接口同样受与 webhook 路径相同的源 IP 规则限制。

状态码对照表：

| 结果 | 状态码 |
|------|--------|
| 通知已被接收或去重 | 202 |
| 验证握手（携带 `validationToken` 的 GET 请求） | 200（原样返回该令牌） |
| 批量处理中的所有项均因 `clientState` 错误而失败 | 403 |
| JSON 格式错误 / 缺少 `value` 数组 / 资源不存在 | 400 |
| 源 IP 不在允许列表中 | 403 |
| 无 `validationToken` 的纯 GET 请求 | 400 |

## 故障排查

| 问题 | 检查项 |
|------|--------|
| Graph 订阅验证失败 | 公开 URL 是否可访问，`/msgraph/webhook` 路径是否正确，携带 `validationToken` 的 GET 请求是否能在 10 秒内以 `text/plain` 格式原样返回该令牌。 |
| 已发送通知但无数据被接收 | `client_state` 是否与注册订阅时使用的值一致。如果该值发生变动，请重新运行 `openssl rand -hex 32` 并创建新的订阅。同时检查 `accepted_resources` 是否包含 Graph 发送的资源路径。 |
| 所有通知均返回 403 错误 | `clientState` 不匹配（可能是被篡改，或订阅时使用了不同的值）。请使用 `hermes teams-pipeline subscribe --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE" ...` 命令重新创建订阅（该命令随 pipeline 运行时代码一起提供）。 |
| 监听器拒绝在 `0.0.0.0` 上启动 | 将 `allowed_source_cidrs` 设置为 Microsoft 当前的 webhook 出站 IP 范围，或将在隧道/反向代理之后的 Hermes 绑定到 `127.0.0.1` / `::1`。 |
| 监听器已启动，但执行 `curl http://localhost:8646/health` 会挂起 | 可能存在端口绑定冲突。请运行 `ss -tlnp \| grep 8646` 检查，并在需要时更改端口号。 |
| 来自 Microsoft 的真实 Graph 请求被拒绝 | 源 IP 允许列表范围过窄。请扩大列表范围，纳入 Microsoft 当前的出站 IP 范围。如果您仍在测试隧道路径，可将 Hermes 绑定到回环地址，由隧道负责处理对外访问。 |

## 相关文档

- [注册 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration) — Azure 应用注册的先决条件
- [环境变量 → Microsoft Graph](/reference/environment-variables#microsoft-graph-teams-meetings) — 完整的环境变量列表
- [Microsoft Teams 机器人设置](/user-guide/messaging/teams) — 允许用户在 Teams 中与 Hermes 聊天的不同平台
