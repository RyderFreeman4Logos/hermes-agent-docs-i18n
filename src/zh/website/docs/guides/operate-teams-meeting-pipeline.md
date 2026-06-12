---
title: "Operate the Teams Meeting Pipeline"
description: "Runbook, go-live checklist, and operator worksheet for the Microsoft Teams meeting pipeline"
---

# 操作 Teams 会议处理流程

请在您已从 [Teams Meetings](/user-guide/messaging/teams-meetings) 中启用该功能后，使用本指南。

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

在进行任何配置更改后，请首先使用此功能。

### 检查令牌状态

```bash
hermes teams-pipeline token-health
hermes teams-pipeline token-health --force-refresh
```

当怀疑认证状态已过期时，请使用 `--force-refresh` 参数。 

### 检查订阅信息

```bash
hermes teams-pipeline subscriptions
```

### 续订即将到期的订阅套餐

```bash
hermes teams-pipeline maintain-subscriptions
hermes teams-pipeline maintain-subscriptions --dry-run
```

### 自动化订阅续订（生产环境必须）

**Microsoft Graph 的订阅最多在 72 小时后过期。** 如果没有进行续订，会议通知将在 3 天后自动停止，此时数据流转流程会显得“出现故障”。这是所有基于 Graph 的集成中最常见的运行故障模式。

您必须定期执行 `maintain-subscriptions` 命令。请从以下三种选项中选择一种：

#### 选项 1：Hermes cron（如果您已经在使用 Hermes 网关，则推荐此方案）

Hermes 内置了 cron 计时调度器。使用 `--no-agent` 模式时，任务将以脚本形式运行（而非调用大型语言模型），且 `--script` 参数必须指向 `~/.hermes/scripts/` 目录下的文件。首先需要创建该脚本：

```bash
mkdir -p ~/.hermes/scripts
cat > ~/.hermes/scripts/maintain-teams-subscriptions.sh <<'EOF'
#!/usr/bin/env bash
exec hermes teams-pipeline maintain-subscriptions
EOF
chmod +x ~/.hermes/scripts/maintain-teams-subscriptions.sh
```

接着，注册一个每12小时执行一次的纯脚本型定时任务（这样在72小时的过期时间限制内还有6次执行余地）：

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

#### 第三种方案：普通 crontab 文件

```cron
0 */12 * * * /usr/local/bin/hermes teams-pipeline maintain-subscriptions >> /var/log/hermes/teams-pipeline-maintain.log 2>&1
```

请确保cron运行环境已配置`MSGRAPH_*`类凭据。最简单的解决方法是在crontab调用的封装脚本开头引入`~/.hermes/.env`文件。

#### 验证续订功能是否正常工作

设置好调度计划后，可在首次按计划执行任务之后，检查续订相关的操作情况：

```bash
hermes teams-pipeline subscriptions   # should show expirationDateTime advanced
hermes teams-pipeline maintain-subscriptions --dry-run   # should show "0 expiring soon" most of the time
```

如果您发现自己的 Graph webhook 在大约 72 小时后突然“停止工作”，首先应检查这一点：续订任务是否确实已执行？

### 检查最近的作业记录

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
```

## 常规运行手册

### 首次设置完成后

请按顺序执行以下操作：

```bash
hermes teams-pipeline validate
hermes teams-pipeline token-health --force-refresh
hermes teams-pipeline subscriptions
```

随后触发或等待真实的会议事件发生，进而进行确认：

```bash
hermes teams-pipeline list
hermes teams-pipeline show <job-id>
```

### 日常或定期检查

- 运行命令 `hermes teams-pipeline maintain-subscriptions --dry-run`
- 检查 `hermes teams-pipeline list --status failed` 的输出
- 确认 Teams 发送目标仍是正确的聊天室或频道

### 更改 webhook 地址或发送目标之前

- 更新公共通知地址或 Teams 目标配置
- 运行命令 `hermes teams-pipeline validate`
- 续订或重新创建受影响的订阅
- 确认新事件能被正确发送到预定接收端

## 故障排查指南

### 未生成任何任务

检查以下项：
- 是否已启用 `msgraph_webhook`
- 公共通知地址是否指向 `/msgraph/webhook`
- 订阅中的客户端状态是否与 `MSGRAPH_WEBHOOK_CLIENT_STATE` 匹配
- 远端是否存在有效且未过期的订阅

### 任务处于重试状态，或在汇总前失败

检查以下项：
- 文本转录的权限及可用性
- 录制功能的权限及记录文件的可用性
- 若启用了录制回退功能，则检查 `ffmpeg` 是否可用
- Graph 令牌的状态是否正常

### 汇总内容已生成但未发送到 Teams

检查以下项：
- 是否设置了 `platforms.teams.enabled: true`
- `delivery_mode` 的设置
- webhook 模式下的 `incoming_webhook_url` 设置
- Graph 模式下的 `chat_id` 或 `team_id` 以及 `channel_id` 设置
- 若使用 Graph 发送功能，则检查 Teams 认证配置

### 出现重复或异常的回放内容

检查以下项：
- 是否通过 `hermes teams-pipeline run` 手动重新执行了某项任务
- 该会议对应的接收端记录是否已存在
- 本地配置中是否有意启用了重新发送路径

## 上线前检查清单

- [ ] Graph 令牌信息完整且正确
- [ ] `msgraph_webhook` 已启用，且可从公共网络访问
- [ ] `MSGRAPH_WEBHOOK_CLIENT_STATE` 已设置，并与订阅配置一致
- [ ] 已创建文本转录相关的订阅
- [ ] 若需要语音转文字回退功能，已创建录制相关订阅
- [ ] 若启用了录制回退功能，已安装 `ffmpeg`
- [ ] Teams 外发目标已配置并经过验证
- [ ] 仅在实际需要时才配置 Notion 和 Linear 接收端
- [ ] `hermes teams-pipeline validate` 的检查结果为正常
- [ ] `hermes teams-pipeline token-health --force-refresh` 命令执行成功
- [ ] **已安排 `maintain-subscriptions` 任务**（可通过 Hermes cron、systemd timer 或 crontab 实现——详见[自动化订阅续订](#automating-subscription-renewal-required-for-production)）。否则 Graph 订阅将在 72 小时内自动过期。
- [ ] 已有真实的端到端会议事件生成了存储任务
- [ ] 至少有一份汇总内容已发送到预定接收端

## 发送模式选择指南

| 模式 | 适用场景 | 权衡点 |
|------|----------|--------|
| `incoming_webhook` | 仅需向 Teams 简单发布内容 | 设置最简单，但控制能力较弱 |
| `graph` | 需要通过 Graph 向频道或聊天室发布内容 | 控制能力更强，但需要配置更多认证及目标相关参数 |

## 操作人员准备工作表

在正式上线前请填写以下内容：

| 项目 | 值 |
|------|-----|
| 公共通知地址 | |
| Graph 租户 ID | |
| Graph 客户端 ID | |
| Webhook 客户端状态 | |
| 文本转录资源订阅信息 | |
| 录制资源订阅信息 | |
| Teams 发送模式 | |
| Teams 聊天室 ID 或团队/频道 ID | |
| Notion 数据库 ID | |
| Linear 团队 ID | |
| 是否需要覆盖存储路径 | |
| 负责日常检查的人员 | |

## 变更审查工作表

在更改部署配置之前请使用此表：

| 问题 | 答案 |
|------|------|
| 我们是否要更改公共 webhook 地址？ | |
| 我们是否要更换 Graph 令牌信息？ | |
| 我们是否要更改 Teams 发送模式？ | |
| 我们是否要切换到新的 Teams 聊天室或频道？ | |
| 是否需要重新创建或续订订阅？ | |
| 是否需要进行全新的端到端功能验证？ | |

## 相关文档

- [Teams 会议设置](/user-guide/messaging/teams-meetings)
- [Microsoft Teams 机器人设置](/user-guide/messaging/teams)
