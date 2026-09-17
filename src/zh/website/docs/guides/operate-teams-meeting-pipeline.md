---
title: "Operate the Teams Meeting Pipeline"
description: "Runbook, go-live checklist, and operator worksheet for the Microsoft Teams meeting pipeline"
---

# 操作 Teams 会议处理流程

请在您已从 [Teams Meetings](/user-guide/messaging/teams-meetings) 中启用该功能后使用本指南。

本页面涵盖以下内容：
- 运维人员 CLI 操作流程
- 定期订阅维护
- 故障排查
- 上线前检查
- 推广实施工作表

## 核心运维命令

### 验证配置快照

```bash
hermes teams-pipeline validate
```

在修改任何配置后，请首先使用此功能。

### 检查令牌状态

```bash
hermes teams-pipeline token-health
hermes teams-pipeline token-health --force-refresh
```

如果怀疑认证状态已过期，请使用 `--force-refresh` 参数。 

### 检查订阅情况

```bash
hermes teams-pipeline subscriptions
```

### 续订即将到期的订阅套餐

```bash
hermes teams-pipeline maintain-subscriptions
hermes teams-pipeline maintain-subscriptions --dry-run
```

### 自动化订阅续订（生产环境必须配置）

**Microsoft Graph 的订阅最多在 72 小时后过期。** 如果没有进行自动续订，会议通知将在 3 天后悄然停止，此时数据流转流程会显得“出现故障”。这是所有基于 Graph 的集成系统最常见的运行故障模式。

您必须定期运行 `maintain-subscriptions` 命令。请从以下三种选项中选择一种：

#### 选项 1：Hermes cron（如果您已经在使用 Hermes 网关，则推荐此方式）

Hermes 内置了 cron 计时调度器。使用 `--no-agent` 模式时，任务将以脚本形式执行（而非依赖大语言模型），且 `--script` 参数必须指向 `~/.hermes/scripts/` 目录下的文件。首先需要创建该脚本：

```bash
mkdir -p ~/.hermes/scripts
cat > ~/.hermes/scripts/maintain-teams-subscriptions.sh <<'EOF'
#!/usr/bin/env bash
exec hermes teams-pipeline maintain-subscriptions
EOF
chmod +x ~/.hermes/scripts/maintain-teams-subscriptions.sh
```

接着，注册一个每12小时执行一次的纯脚本型定时任务（这样在72小时的过期时限内还有6次执行机会）：

```bash
hermes cron create "0 */12 * * *" \
  --name "teams-pipeline-maintain-subscriptions" \
  --no-agent \
  --script maintain-teams-subscriptions.sh \
  --deliver local
```

确认其是否已成功注册，并查看下一次的运行时间：

```bash
hermes cron list
hermes cron status        # scheduler status
```

#### 方案 2：systemd 定时器（适用于 Linux 生产环境部署）

创建文件 `/etc/systemd/system/hermes-teams-pipeline-maintain.service`：

```ini
[Unit]
Description=Hermes Teams pipeline subscription maintenance
After=network-online.target

[Service]
Type=oneshot
User=hermes
EnvironmentFile=/etc/hermes/env
ExecStart=/usr/local/bin/hermes teams-pipeline maintain-subscriptions
```

还有 `/etc/systemd/system/hermes-teams-pipeline-maintain.timer`：

```ini
[Unit]
Description=Run Hermes Teams pipeline subscription maintenance every 12 hours

[Timer]
OnBootSec=5min
OnUnitActiveSec=12h
Persistent=true

[Install]
WantedBy=timers.target
```

启用：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-teams-pipeline-maintain.timer
systemctl list-timers hermes-teams-pipeline-maintain.timer
```

#### 第三种方案：普通 crontab 表格

```cron
0 */12 * * * /usr/local/bin/hermes teams-pipeline maintain-subscriptions >> /var/log/hermes/teams-pipeline-maintain.log 2>&1
```

请确保 Cron 运行环境已包含 `MSGRAPH_*` 类型的凭据。最简单的解决方法是：在 crontab 调用的封装脚本开头引入 `~/.hermes/.env` 文件。

#### 验证续订功能是否正常工作

设置好调度计划后，请在首次按计划执行之后，检查续订相关的操作是否正常进行：

```bash
hermes teams-pipeline subscriptions   # should show expirationDateTime advanced
hermes teams-pipeline maintain-subscriptions --dry-run   # should show "0 expiring soon" most of the time
```

如果发现您的 Graph webhook 在大约 72 小时后突然“停止工作”，首先应该检查的是这一点：续订任务是否真的已经执行？

### 查看最近的作业记录

```bash
hermes teams-pipeline list
hermes teams-pipeline list --status failed
hermes teams-pipeline show <job-id>
```

### 重放已存储的任务

```bash
hermes teams-pipeline run <job-id>
```

### 模拟会议资料获取功能

```bash
hermes teams-pipeline fetch --meeting-id <meeting-id>
hermes teams-pipeline fetch --join-web-url "<join-url>"
hermes teams-pipeline fetch --join-web-url "<join-url>" --organizer-user-id <entra-user-id>
```

请传递 `--organizer-user-id`（组织者的 Microsoft Entra 用户 ID），通过组织者范围内的 `/users/{id}/onlineMeetings` Graph 路径进行查询。这对于 Teams 的 `/meet/` 短链接而言是必需的，因为 Graph 会在 `/communications/onlineMeetings` 接口上拒绝此类请求。而基于 Webhook 的任务则会自动从通知中的 `@odata.id` 中获取组织者信息。

## 常规操作指南

### 首次设置完成后

请按以下顺序执行这些操作：

```bash
hermes teams-pipeline validate
hermes teams-pipeline token-health --force-refresh
hermes teams-pipeline subscriptions
```

随后触发或等待真实的会议事件发生，以此进行确认：

```bash
hermes teams-pipeline list
hermes teams-pipeline show <job-id>
```

### 日常或定期检查

- 运行命令 `hermes teams-pipeline maintain-subscriptions --dry-run`
- 查看状态为失败的订阅：`hermes teams-pipeline list --status failed`
- 确认 Teams 发送目标仍是正确的聊天窗口或频道

### 更改 webhook 地址或发送目标之前

- 更新公共通知地址或 Teams 目标配置
- 运行验证命令 `hermes teams-pipeline validate`
- 续订或重新创建受影响的订阅
- 确认新事件能正确发送到预定接收端

## 故障排查指南

### 未生成任何任务

请检查：
- 是否已启用 `msgraph_webhook` 功能
- 公共通知地址是否指向 `/msgraph/webhook`
- 订阅中的客户端状态是否与 `MSGRAPH_WEBHOOK_CLIENT_STATE` 匹配
- 远端是否存在有效且未过期的订阅

### 任务处于重试状态，或在汇总前即失败

请检查：
- 文本转录的权限及可用性
- 录制功能的权限及录制文件的可用性
- 若启用了录制回退功能，则需确认 `ffmpeg` 是否可用
- Graph 令牌的状态是否正常

### 汇总信息已生成但未发送到 Teams

请检查：
- 配置项 `platforms.teams.enabled` 是否设置为 `true`
- `delivery_mode` 的设置
- webhook 模式下的 `incoming_webhook_url` 地址
- Graph 模式下的 `chat_id`/`team_id` 及 `channel_id` 参数
- 若使用 Graph 发送方式，则需检查 Teams 认证配置

### 出现重复或异常的重播内容

请检查：
- 是否曾通过 `hermes teams-pipeline run` 手动重新执行过某项任务
- 该会议对应的接收端记录是否已存在
- 本地配置中是否有意开启了重新发送路径

## 上线前检查清单

- [ ] Graph凭据存在且正确  
- [ ] `msgraph_webhook`已启用，且可从公共互联网访问  
- [ ] `MSGRAPH_WEBHOOK_CLIENT_STATE`已设置，并与订阅配置匹配  
- [ ] 已创建转录内容订阅  
- [ ] 如需语音转文本备用功能，已创建录音订阅  
- [ ] 若启用了录音备用功能，已安装`ffmpeg`  
- [ ] Teams消息发送目标已配置并经过验证  
- [ ] 仅在实际需要时才配置Notion和Linear接收端  
- [ ] `hermes teams-pipeline validate`命令运行后返回“OK”状态  
- [ ] `hermes teams-pipeline token-health --force-refresh`命令执行成功  
- [ ] **已安排`maintain-subscriptions`任务**（可通过Hermes cron、systemd定时器或crontab实现——详见[自动化订阅续订](#automating-subscription-renewal-required-for-production)）。若未设置此任务，Graph订阅将在72小时内自动过期。  
- [ ] 已有真实的端到端会议事件生成了存储任务  
- [ ] 至少有一份摘要内容已送达预定的接收端  

## 传输模式选择指南

| 模式 | 适用场景 | 权衡点 |
|------|----------|--------|
| `incoming_webhook` | 仅需将内容简单发布到Teams中 | 设置最简单，但控制能力较弱 |
| `graph` | 需要通过Graph将内容发布到频道或聊天窗口 | 控制能力更强，但需要更多身份验证及目标配置工作 |

## 操作前检查清单

在正式部署前请填写此清单：

| 项目 | 值 |
|------|-------|
| 公开通知 URL | |
| Graph 租户 ID | |
| Graph 客户端 ID | |
| Webhook 客户端状态 | |
| 文本记录资源订阅 | |
| 录制资源订阅 | |
| Teams 传输模式 | |
| Teams 聊天 ID 或团队/频道 | |
| Notion 数据库 ID | |
| Linear 团队 ID | |
| 存储路径覆盖值（如有） | |
| 日常检查的负责人 | |

## 变更审核表

在更改部署配置之前请使用此表：

| 问题 | 答案 |
|----------|-------|
| 我们要更改公开 Webhook URL 吗？ | |
| 我们需要更换 Graph 凭证吗？ | |
| 我们要更改 Teams 传输模式吗？ | |
| 我们要切换到新的 Teams 聊天或频道吗？ | |
| 是否需要重新创建或续订订阅？ | |
| 是否需要进行全新的端到端验证？ | |

## 相关文档

- [Teams 会议设置](/user-guide/messaging/teams-meetings)
- [Microsoft Teams 机器人设置](/user-guide/messaging/teams)
