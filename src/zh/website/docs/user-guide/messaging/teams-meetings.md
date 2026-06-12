---
sidebar_position: 6
title: "Teams Meetings"
description: "Set up the Microsoft Teams meeting summary pipeline with Microsoft Graph webhooks"
---

# Microsoft Teams 会议功能

当您希望让 Hermes 处理 Microsoft Graph 会议事件、优先获取会议文字记录，在没有可用文字记录时再回退到视频录像与语音转文字技术，并将结构化摘要传递给下游系统时，可使用 Teams 会议处理流程。

前置条件：有关底层机器人/凭证的设置，请参阅 [Microsoft Teams](./teams.md) 文档。

> 运行 `hermes gateway setup` 命令，然后选择 **Teams Meetings** 选项以获取操作指南。

本页面主要介绍相关设置与启用步骤：
- Graph 凭证配置
- webhook 监听器设置
- Teams 会议交付模式
- 处理流程配置结构

关于后续运营、上线检查以及操作员工作指南，请参考专用文档：[操作 Teams 会议处理流程](/guides/operate-teams-meeting-pipeline)。

## 此功能的作用

该处理流程会执行以下操作：
1. 接收 Microsoft Graph 发送的 webhook 事件
2. 定位对应会议，并优先使用文字记录作为输出
3. 在无法获取可用文字记录时，回退到下载视频录像并结合语音转文字技术
4. 在本地存储持久的任务状态及下游系统记录
5. 能够将摘要内容写入 Notion、Linear 和 Microsoft Teams 等平台

操作员的相关操作仍通过 CLI 完成（`teams-pipeline` 子命令由 `teams_pipeline` 插件提供，可通过 `hermes plugins enable teams_pipeline` 命令启用该插件，或是在 `config.yaml` 文件中设置 `plugins.enabled: [teams_pipeline]`）。

```bash
hermes teams-pipeline validate
hermes teams-pipeline list
hermes teams-pipeline maintain-subscriptions
```

## 先决条件

在启用会议处理流程之前，请确保您已具备以下条件：

- 已正确安装的 Hermes 程序
- 若希望通过 Microsoft Teams 发送消息，则需已完成现有的 [Microsoft Teams 机器人设置](/user-guide/messaging/teams)
- 包含所需权限的 Microsoft Graph 应用程序凭据，这些权限对应您计划使用的会议相关资源
- 一个可供 Microsoft Graph 调用以实现 webhook 消息传递的公共 HTTPS 地址
- 若希望启用录音加语音转文字的备用功能，则需已安装 `ffmpeg` 工具

## 第一步：添加 Microsoft Graph 凭据

将仅适用于 Graph 应用的凭据添加到 `~/.hermes/.env` 文件中：

```bash
MSGRAPH_TENANT_ID=<tenant-id>
MSGRAPH_CLIENT_ID=<client-id>
MSGRAPH_CLIENT_SECRET=<client-secret>
```

这些凭据被以下组件使用：
- Graph客户端基础框架
- 订阅维护命令
- 会议记录解析及相关文件获取功能
- 在您未提供专用Teams访问令牌时的基于Graph的Teams消息发送功能

## 第2步：启用Graph Webhook监听器

Webhook监听器是一个名为`msgraph_webhook`的网关平台。首先需启用该平台，并设置一个客户端状态值：

```bash
MSGRAPH_WEBHOOK_ENABLED=true
MSGRAPH_WEBHOOK_HOST=127.0.0.1
MSGRAPH_WEBHOOK_PORT=8646
MSGRAPH_WEBHOOK_CLIENT_STATE=<random-shared-secret>
MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES=communications/onlineMeetings
```

该监听器提供以下接口：
- `/msgraph/webhook`，用于接收 Graph 通知
- `/health`，用于执行简单的健康检查

您需要将自身的公共 HTTPS 端点指向该监听器。例如，如果您的公共域名是 `https://ops.example.com`，那么对应的 Graph 通知地址通常为：

```text
https://ops.example.com/msgraph/webhook
```

## 第 3 步：配置团队消息传递与管道行为

会议处理管道会从现有的 `teams` 平台配置项中读取运行时配置。与特定管道相关的参数则存储在 `teams.extra.meeting_pipeline` 下。而团队向外发送消息的功能则仍遵循常规的 Teams 平台配置规则。

示例 `~/.hermes/config.yaml` 文件内容：

```yaml
platforms:
  msgraph_webhook:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8646
      client_state: "replace-me"
      accepted_resources:
        - "communications/onlineMeetings"

  teams:
    enabled: true
    extra:
      client_id: "your-teams-client-id"
      client_secret: "your-teams-client-secret"
      tenant_id: "your-teams-tenant-id"

      # outbound summary delivery
      delivery_mode: "graph" # or incoming_webhook
      team_id: "team-id"
      channel_id: "channel-id"
      # incoming_webhook_url: "https://..."

      meeting_pipeline:
        transcript_min_chars: 80
        transcript_required: false
        transcription_fallback: true
        ffmpeg_extract_audio: true
        notion:
          enabled: false
        linear:
          enabled: false
```

如果将监听器绑定到非回环地址的主机，例如 `0.0.0.0`，则必须同时将 `allowed_source_cidrs` 设置为 Microsoft 的 Webhook 出站地址范围。而回环地址绑定（`127.0.0.1` / `::1`）则是用于开发隧道及本地反向代理设置的默认选项。

## Teams 传输模式

该流水线在现有的 Teams 插件中支持两种 Teams 摘要传输模式。

### `incoming_webhook`

当您希望直接通过 Webhook 将数据发送到 Teams，而无需通过 Graph 创建频道消息时，可使用此模式。

所需配置：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      delivery_mode: "incoming_webhook"
      incoming_webhook_url: "https://..."
```

### `graph`

当您希望让 Hermes 通过 Microsoft Graph 将摘要发布到 Teams 聊天窗口或频道时，可使用此选项。

支持的目标地址：
- `chat_id`
- `team_id` + `channel_id`
- 为现有 Teams 平台准备的备用地址：`team_id` + `home_channel`

示例：

```yaml
platforms:
  teams:
    enabled: true
    extra:
      delivery_mode: "graph"
      team_id: "team-id"
      channel_id: "channel-id"
```

## 第 4 步：启动网关

更新配置后，即可正常启动 Hermes。

```bash
hermes gateway run
```

或者，如果您在 Docker 环境中运行 Hermes，只需以与常规部署相同的方式启动网关即可。

请检查监听器状态：

```bash
curl http://localhost:8646/health
```

## 第 5 步：创建图订阅

使用插件命令行工具来创建和查看订阅项。

示例：

```bash
hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllTranscripts \
  --notification-url https://ops.example.com/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"

hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllRecordings \
  --notification-url https://ops.example.com/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"
```

:::warning 图表订阅将在 72 小时后过期

Microsoft Graph 对 webhook 订阅设置了 72 小时的限制，且不会自动续订。在正式上线之前，您必须提前安排执行 `hermes teams-pipeline maintain-subscriptions` 命令，否则在任何手动创建订阅后的三天后，通知功能将自动停止。详情请参阅操作手册中的[自动续订订阅](/guides/operate-teams-meeting-pipeline#automating-subscription-renewal-required-for-production)，其中提供了三种方案：Hermes cron、systemd timer 以及普通 crontab。

:::

如需了解订阅维护及上线后的操作流程，请继续阅读指南：[运营 Teams 会议处理流程](/guides/operate-teams-meeting-pipeline)。

## 验证

运行内置的验证快照：

```bash
hermes teams-pipeline validate
```

实用的辅助检查功能：

```bash
hermes teams-pipeline token-health
hermes teams-pipeline subscriptions
```

## 故障排除

| 问题 | 检查项 |
|---------|--------|
| Graph webhook 验证失败 | 确认公共 URL 正确且可访问，同时确保 Graph 实际调用的路径为 `/msgraph/webhook` |
| 任务未出现在 `hermes teams-pipeline list` 中 | 确认 `msgraph_webhook` 已启用，且订阅配置指向正确的通知 URL |
| Transcript-first 模式始终失败 | 检查 Graph 对转录记录资源的权限，以及该会议是否已生成对应的转录文件 |
| 录制回退功能失败 | 确认已安装 `ffmpeg`，且 Graph 应用能够访问录制文件 |
| Teams 摘要发送失败 | 重新检查 `delivery_mode`、目标 ID 以及 Teams 认证配置 |

## 相关文档

- [Microsoft Teams 机器人设置](/user-guide/messaging/teams)
- [操作 Teams 会议处理流程](/guides/operate-teams-meeting-pipeline)
