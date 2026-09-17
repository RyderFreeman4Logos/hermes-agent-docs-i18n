---
sidebar_position: 23
title: "Microsoft Graph Webhook Listener"
description: "Receive Microsoft Graph change notifications (meetings, calendar, chat, etc.) in Hermes"
---

# Microsoft Graph Webhook 监听器

`msgraph_webhook` 网关平台是一种入站事件监听器。通过它，Hermes 能够接收来自 Microsoft Graph 的**变更通知**——例如“某个 Teams 会议已结束”、“该聊天窗口中有新消息到达”、“某个日历事件已被更新”等。与用户主动输入指令的 `teams` 平台不同，这种机制是 M365 向 Hermes 发送事件通知，而非由人工操作。

目前，该监听器的主要应用场景是 Teams 会议摘要生成流程：当会议生成文字记录时，Microsoft Graph 会发出通知，相应流程会获取这些记录，随后 Hermes 会将摘要重新发布到 Teams 中。其他 Microsoft Graph 资源（如 `/chats/.../messages`、`/users/.../events`）也使用相同的监听器——不过这些资源的处理流程会有各自的实现方式。

## 先决条件

- Microsoft Graph 应用程序凭据——[注册 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration)
- 一个 Microsoft Graph 可以访问的**公开 HTTPS 地址**（Graph 不会调用私有端点）。开发测试时可以使用开发隧道，而正式环境则需要具备有效证书的真实域名。
- 一个强密码作为 `clientState` 值。可通过 `openssl rand -hex 32` 生成该密码，并将其以 `MSGRAPH_WEBHOOK_CLIENT_STATE` 的形式保存在 `~/.hermes/.env` 文件中。

## 快速入门

最简版的 `~/.hermes/config.yaml` 配置如下：

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

注意：绑定主机地址将从 `config.yaml` 文件中的 `extra.host` 字段读取（参见上文示例）；不存在可覆盖该值的 `MSGRAPH_WEBHOOK_HOST` 环境变量。

启动网关命令为：`hermes gateway run`。该网关会暴露以下接口：

- `POST /msgraph/webhook` —— 接收来自 Graph 的变更通知
- `GET /msgraph/webhook?validationToken=...` —— 进行 Graph 订阅验证
- `GET /health` —— 提供就绪状态检查，同时显示已处理和重复的请求数

您需要通过反向代理、开发隧道或入口网关等方式将此监听接口公开展开。用于 Graph 订阅的通知地址即为您的公共 HTTPS 域名加上 `/msgraph/webhook` 路径。

```
https://ops.example.com/msgraph/webhook
```

## 配置

所有设置均位于 `platforms.msgraph_webhook.extra` 下：

| 设置项 | 默认值 | 描述 |
|--------|--------|------|
| `host` | 未设置（双栈模式：所有接口，IPv4+IPv6） | HTTP 监听器的绑定地址。非回环地址绑定需要 `allowed_source_cidrs`；回环地址（`127.0.0.1` / `::1`）最便于搭建开发隧道或反向代理。 |
| `port` | `8646` | 绑定端口。 |
| `webhook_path` | `/msgraph/webhook` | Graph 发送 POST 请求的 URL 路径。 |
| `health_path` | `/health` | 健康检查端点。 |
| `client_state` | — | Graph 会在每条通知中回显的共享密钥。建议与 `hmac.compare_digest` 结合使用——可通过 `openssl rand -hex 32` 生成该密钥。 |
| `accepted_resources` | `[]`（接受所有） | 允许的 Graph 资源路径/模式列表。末尾的 `*` 表示前缀匹配，开头的 `/` 也可被接受。示例：`["communications/onlineMeetings", "chats/*/messages"]`。 |
| `max_seen_receipts` | `5000` | 用于去重通知 ID 的缓存大小上限。达到该限制后，最旧的条目将被移除。 |
| `allowed_source_cidrs` | `[]` | 非回环地址绑定时必需。仅当监听器绑定在回环地址上且由本地隧道或反向代理代理时，方可留空。 |

大多数设置还对应有环境变量（`MSGRAPH_WEBHOOK_*`），这些变量会在网关启动时合并到配置中（`host` 除外，它仅通过配置设置——详见上文说明）——更多信息请参阅[环境变量参考](/reference/environment-variables#microsoft-graph-teams-meetings)。

## 安全强化措施

### clientState 是主要的身份验证依据

每条 Graph 通知都会包含您的订阅所注册的 `clientState` 字符串。监听器会通过时间安全的比较方式，拒绝任何 `clientState` 不匹配的通知。这是微软官方文档中规定的机制——应将该值视为高度机密的共享密钥。

如果未设置 `client_state`，监听器将拒绝启动。

### 源 IP 允许列表（生产环境部署）

在生产环境中，建议将监听器的访问范围限制在微软公布的 Graph webhook 源 IP 范围内。微软在 [Office 365 IP 地址和 URL Web 服务](https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges) 文档中详细介绍了这些出站 IP 范围。请按照该文档配置相应的限制规则：

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

如果在启动时未设置 `allowed_source_cidrs`，则无法将主机绑定到非回环地址，如 `0.0.0.0`、`::` 或局域网 IP。若在同一台机器上使用了开发隧道或反向代理，请将 Hermes 绑定到 `127.0.0.1` 或 `::1`，并保持允许列表为空。无效的 CIDR 字符串会仅生成警告信息并被忽略。**请每季度查看一次 Microsoft 的 IP 列表**，因为该列表会定期更新。

### HTTPS 终止处理

监听器仅支持传输原始 HTTP 流量。应在反向代理（如 Caddy、Nginx、Cloudflare Tunnel、AWS ALB）处完成 TLS 终止处理，再通过本地网络将请求转发给监听器。Graph 不会向非 HTTPS 端点发送数据，因此加密前的流量无法直接从 Graph 传达到您的服务器。

### 响应规范

操作成功时，监听器会返回状态码 `202 Accepted`，且响应体为空——内部计数信息不会包含在网络响应中。管理员可通过 `/health` 接口查看相关计数，该接口同样遵循与 webhook 路径相同的源 IP 校验规则。

状态码对照表：

| 结果 | 状态码 |
|------|--------|
| 通知已被接收或去重 | 202 |
| 验证握手（带有 `validationToken` 的 GET 请求） | 200（返回该令牌） |
| 批量处理中的所有项均出现 clientState 错误 | 403 |
| JSON 格式错误 / 缺少 `value` 数组 / 资源不存在 | 400 |
| 源 IP 不在允许列表中 | 403 |
| 仅发送不含 `validationToken` 的 GET 请求 | 400 |

## 故障排除

| 问题 | 检查项 |
|---------|--------|
| Graph 订阅验证失败 | 公开 URL 可访问，`/msgraph/webhook` 路径匹配，使用 `validationToken` 发送 GET 请求后，应在 10 秒内以 `text/plain` 格式原样返回该令牌。 |
| 已发送通知 POST 请求但无数据被接收 | `client_state` 值需与注册订阅时的一致。如果该值发生变动，请重新运行 `openssl rand -hex 32` 并创建新的订阅。同时确认 `accepted_resources` 中包含 Graph 发送的资源路径。 |
| 每条通知都会返回 403 错误 | `clientState` 值不匹配（可能是被篡改，或是订阅时使用了不同的值）。请使用 `hermes teams-pipeline subscribe --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE" ...` 重新创建订阅（该命令随 pipeline runtime PR 一同提供）。 |
| 监听器拒绝在 `0.0.0.0` 地址上启动 | 将 `allowed_source_cidrs` 设置为 Microsoft 当前的 webhook 出站地址范围，或通过隧道/反向代理将 Hermes 绑定到 `127.0.0.1` / `::1` 地址。 |
| 监听器已启动，但执行 `curl http://localhost:8646/health` 会挂起 | 端口绑定冲突。请运行 `ss -tlnp \| grep 8646` 检查，并在必要时更改端口号。 |
| 来自 Microsoft 的 Real Graph 请求被拒绝访问 | 源 IP 允许列表过窄。需扩大列表范围，纳入 Microsoft 当前的出站地址范围。如果仍在验证隧道路径，可将 Hermes 绑定到回环地址，由隧道负责处理对外访问。 |

## 相关文档

- [注册 Microsoft Graph 应用程序](/guides/microsoft-graph-app-registration) — Azure 应用注册的先决条件  
- [环境变量 → Microsoft Graph](/reference/environment-variables#microsoft-graph-teams-meetings) — 完整的环境变量列表  
- [Microsoft Teams 机器人设置](/user-guide/messaging/teams) — 支持用户在 Teams 中与 Hermes 聊天的不同平台
