---
title: "Teams Meeting Pipeline — Teams meeting summaries, job replay, Graph subscriptions"
sidebar_label: "Teams Meeting Pipeline"
description: "Teams meeting summaries, job replay, Graph subscriptions"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Teams 会议处理流程

用于生成 Teams 会议摘要、作业回放功能以及 Microsoft Graph 订阅管理。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/productivity/teams-meeting-pipeline` |
| 版本 | `1.1.0` |
| 开发者 | Hermes Agent + Teknium |
| 许可证 | MIT |
| 标签 | `Teams`、`Microsoft Graph`、`Meetings`、`Productivity`、`Operations` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，Agent 就会依据这些内容执行操作。
:::

# Teams 会议处理流程

每当用户询问有关 Microsoft Teams 会议摘要、文字记录、录像文件、行动项、Graph 订阅，或与 Teams 会议处理流程相关的任何运营问题时，均可使用此技能。该技能支持多种语言——以下触发条件仅为示例，并非完整列表。

所有面向操作人员的功能均通过终端工具的 `hermes teams-pipeline` 子命令来实现。该处理流程没有新的模型工具，CLI 是其交互界面。

## 何时使用此技能

当用户需要执行以下操作时，可使用此技能：
- 汇总 Teams 会议内容 / 提取行动项 / 获取会议笔记
- 查看处理流程状态、检查已存储的会议作业，或查看近期会议记录
- 回放/重新运行失败或需要重新生成摘要的已存储作业
- 在更改环境或配置后验证 Microsoft Graph 的设置
- 排查“会议摘要未送达”或“无新会议被导入”的问题
- 管理 Graph Webhook 订阅（创建、续订、删除、查看状态）
- 设置自动订阅续订功能（详见下方注意事项）

多语言触发条件示例（非完整列表）：
- 英语："summarize the Teams meeting"、"pipeline status"、"replay job X"
- 土耳其语："Teams meeting özetle"、"action item çıkar"、"toplantı notu"、"pipeline durumu"、"replay job"

## 先决条件

在使用该处理流程之前，请先确认 `${HERMES_HOME:-~/.hermes}/.env` 文件中已设置以下内容：

```bash
MSGRAPH_TENANT_ID=...
MSGRAPH_CLIENT_ID=...
MSGRAPH_CLIENT_SECRET=...
```

如果缺少任何必要配置，请引导用户前往地址为 `/docs/guides/microsoft-graph-app-registration` 的 Azure 应用注册指南——在流水线能够正常运行之前，必须先完成 Azure AD 应用注册，并授予具有管理员同意权限的 Graph 应用权限。

## 命令参考

### 状态查询与检查（从这里开始）

```bash
hermes teams-pipeline validate              # config snapshot — run first after any change
hermes teams-pipeline token-health          # Graph token status
hermes teams-pipeline token-health --force-refresh   # force a fresh token acquisition
hermes teams-pipeline list                  # recent meeting jobs
hermes teams-pipeline list --status failed  # only failed jobs
hermes teams-pipeline show <job-id>         # full detail of one job
hermes teams-pipeline subscriptions         # current Graph webhook subscriptions
```

### 重新运行 / 调试

```bash
hermes teams-pipeline run <job-id>          # replay a stored job (re-summarize, re-deliver)
hermes teams-pipeline fetch --meeting-id <id>   # dry-run: resolve meeting + transcript without persisting
hermes teams-pipeline fetch --join-web-url "<url>"   # dry-run by join URL
```

### 订阅管理

```bash
hermes teams-pipeline subscribe \
  --resource communications/onlineMeetings/getAllTranscripts \
  --notification-url https://<your-public-host>/msgraph/webhook \
  --client-state "$MSGRAPH_WEBHOOK_CLIENT_STATE"

hermes teams-pipeline renew-subscription <sub-id> --expiration <iso-8601>
hermes teams-pipeline delete-subscription <sub-id>
hermes teams-pipeline maintain-subscriptions            # renew near-expiry ones
hermes teams-pipeline maintain-subscriptions --dry-run  # show what would be renewed
```

## 常见问题的决策树

- 用户询问“为何没有收到今日会议的摘要？”→ 首先执行 `list --status failed`，然后查看对应行的 `show <job-id>`。如果该任务根本不存在，则检查 `subscriptions`——可能是 webhook 已过期（详见下文注意事项）。
- 用户询问“设置是否正常工作？”→ 先执行 `validate`，再执行 `token-health`，最后检查 `subscriptions`。若这三项均通过，则安排一次测试会议，并通过 `list` 查看是否有新生成的记录。
- 用户询问“重新生成会议 X 的摘要”→ 先使用 `list` 查找任务 ID，再执行 `run <job-id>` 重新处理。如果仍失败，则执行 `show <job-id>` 查看错误信息，并使用 `fetch --meeting-id` 进行模拟处理以验证结果。
- 用户询问“将会议 X 添加到流程中”→ 通常无需如此操作——该流程是基于订阅驱动的，而非针对单次会议。如果用户希望对某个历史会议生成摘要，可先使用 `fetch` 获取会议记录，待任务创建后再执行 `run`。

## 重要注意事项：Microsoft Graph 订阅有效期为 72 小时

Microsoft Graph 对 webhook 订阅设置了 72 小时的时间限制，且**不会自动续期**。如果未安排 `maintain-subscriptions` 任务，任何手动创建的订阅在 3 天后就会停止发送通知。

当用户反馈“昨天流程还能正常工作，今天却没有收到通知”时：
1. 运行 `hermes teams-pipeline subscriptions`——如果列表为空或所有条目的 `expirationDateTime` 都已过去，即为原因所在。
2. 按上述方法使用 `subscribe` 重新创建订阅。
3. 立即通过 `hermes cron add`、systemd 定时器或普通 crontab **设置自动续期机制**。文档 `/docs/guides/operate-teams-meeting-pipeline#automating-subscription-renewal-required-for-production` 中介绍了这三种方法，建议设置 12 小时的间隔（这样还有 6 倍的余量，足以覆盖 72 小时的限制）。

## 其他常见问题

- **会议记录尚未生成**。Teams 需要在会议结束后一段时间才能生成会议记录。对刚结束的会议执行 `fetch --meeting-id` 可能会返回空结果。建议等待 2–5 分钟后再尝试，或让 Graph webhook 自动完成数据同步。
- **传输模式不匹配**。即使摘要已生成（`list` 显示任务成功），但内容仍未出现在 Teams 中，需检查 `platforms.teams.extra.delivery_mode` 以及对应的目标配置（`incoming_webhook_url`、`chat_id` 或 `team_id`+`channel_id`）。生成工具会从 config.yaml 文件或 `TEAMS_*` 环境变量中读取这些配置。
- **Graph 应用权限问题**。虽然令牌获取成功（`token-health` 显示正常），但由于在添加权限后未重新获得管理员同意，Graph API 调用仍会返回 401/403 错误。此时需让用户再次登录 Azure 门户，进入应用注册页面并点击“授予管理员同意”。

## 相关文档

当用户需要更深入的了解相关内容时，可引导他们查看以下文档：
- Azure 应用注册指南：`/docs/guides/microsoft-graph-app-registration`
- 完整的流程设置指南：`/docs/user-guide/messaging/teams-meetings`
- 操作员操作手册（包含自动续期、故障排除及上线检查清单）：`/docs/guides/operate-teams-meeting-pipeline`
- Webhook 监听器设置指南：`/docs/user-guide/messaging/msgraph-webhook`
