---
sidebar_position: 16
title: "Yuanbao"
description: "Connect Hermes Agent to the Yuanbao enterprise messaging platform via WebSocket gateway"
---

# Yuanbao

将 Hermes 与腾讯企业级消息平台 [Yuanbao](https://yuanbao.tencent.com/) 相连接。该适配器通过 WebSocket 网关实现实时消息传输，同时支持一对一（C2C）和群组对话。

:::info
Yuanbao 是主要在腾讯及企业环境中使用的企业级消息平台。它采用 WebSocket 技术实现实时通信，基于 HMAC 进行身份验证，并支持图片、文件和语音消息等富媒体内容。
:::

## 前提条件

- 拥有创建机器人权限的 Yuanbao 账号
- 从平台管理员处获取的 Yuanbao APP_ID 和 APP_SECRET
- Python 包：`websockets` 和 `httpx`
- 如需支持媒体文件传输，还需安装 `aiofiles` 包

请安装所需的依赖项：

```bash
pip install websockets httpx aiofiles
```

## 设置流程

### 1. 在元宝中创建机器人

1. 从 [https://yuanbao.tencent.com/](https://yuanbao.tencent.com/) 下载元宝应用。
2. 打开应用后，进入 **PAI → 我的机器人**，创建一个新的机器人。
3. 机器人创建完成后，复制 **APP_ID** 和 **APP_SECRET**。

### 2. 运行设置向导

配置元宝最简单的方法是通过交互式设置向导完成：

```bash
hermes gateway setup
```

在提示时选择**元宝**。向导将执行以下操作：

1. 要求您输入APP_ID
2. 要求您输入APP_SECRET
3. 自动保存配置信息

:::提示
WebSocket URL和API Domain已预设了合理的默认值。您只需提供APP_ID和APP_SECRET即可开始使用。
:::

### 3. 配置环境变量

完成初始设置后，请在`~/.hermes/.env`文件中检查这些变量：

```bash
# Required
YUANBAO_APP_ID=your-app-id
YUANBAO_APP_SECRET=your-app-secret
YUANBAO_WS_URL=wss://api.yuanbao.example.com/ws
YUANBAO_API_DOMAIN=https://api.yuanbao.example.com

# Optional: bot account ID (normally obtained automatically from sign-token)
# YUANBAO_BOT_ID=your-bot-id

# Optional: internal routing environment (e.g. test/staging/production)
# YUANBAO_ROUTE_ENV=production

# Optional: home channel for cron/notifications (format: direct:<account> or group:<group_code>)
YUANBAO_HOME_CHANNEL=direct:bot_account_id
YUANBAO_HOME_CHANNEL_NAME="Bot Notifications"

# Optional: restrict access (legacy, see Access Control below for fine-grained policies)
YUANBAO_ALLOWED_USERS=user_account_1,user_account_2
```

### 4. 启动网关

```bash
hermes gateway
```

该适配器将连接到元宝 WebSocket 网关，通过 HMAC 签名进行身份验证，随后开始处理消息。

## 功能特性

- **WebSocket 网关** — 支持实时双向通信
- **HMAC 身份验证** — 使用 APP_ID/APP_SECRET 对请求进行安全签名
- **点对点消息** — 实现用户与机器人的直接对话
- **群组消息** — 支持群聊中的交流
- **媒体文件支持** — 通过 COS（云对象存储）传输图片、文件及语音消息
- **Markdown 格式化** — 自动拆分消息内容，以符合元宝的尺寸限制
- **消息去重** — 防止同一消息被重复处理
- **心跳检测/保持连接** — 保障 WebSocket 连接的稳定性
- **输入状态指示** — 在机器人处理消息时显示“正在输入…”状态
- **自动重连** — 采用指数退避策略处理 WebSocket 连接断开问题
- **群组信息查询** — 可获取群组详情及成员列表
- **贴纸/表情符号支持** — 在对话中发送 TIMFaceElem 贴纸和表情符号
- **自动设置主频道** — 首个向机器人发送消息的用户将自动成为主频道所有者
- **响应延迟通知** — 当机器人处理时间超过预期时，会发送等待提示

## 配置选项

### 聊天 ID 格式

元宝会根据聊天类型使用不同的前缀标识符：

| 聊天类型 | 格式 | 示例 |
|---------|------|-------|
| 点对点消息 | `direct:<account>` | `direct:user123` |
| 群组消息 | `group:<group_code>` | `group:grp456` |

### 媒体文件上传

元宝适配器会自动通过 COS（腾讯云对象存储）处理媒体文件上传：

- **图片**：支持 JPEG、PNG、GIF、WebP 格式
- **文件**：支持所有常见文档类型
- **语音**：支持 WAV、MP3、OGG 格式

在上传之前，系统会自动验证并下载媒体文件的 URL，以防止 SSRF 攻击。

## 主频道

在任何元宝聊天窗口（私信或群组）中使用 `/sethome` 命令，即可将其指定为**主频道**。定时任务（cron 作业）会将执行结果发送到该频道。

:::提示 自动设置主频道
如果未配置主频道，首个向机器人发送消息的用户将自动成为主频道所有者。若当前主频道为群聊，则首个私信对话会将群聊升级为点对点频道。
:::

您也可以在 `~/.hermes/.env` 文件中手动进行设置：

```bash
YUANBAO_HOME_CHANNEL=direct:user_account_id
# or for a group:
# YUANBAO_HOME_CHANNEL=group:group_code
YUANBAO_HOME_CHANNEL_NAME="My Bot Updates"
```

### 示例：设置主频道

1. 在元宝中与该机器人开始对话
2. 发送命令：`/sethome`
3. 机器人会回复：“主频道已设置为名称为[chat_name]、ID为[chat_id]的频道。定时任务将发送到该频道。”
4. 今后的所有定时任务及通知都将发送至该频道

### 示例：定时任务的发送

创建一个定时任务：

```bash
/cron "0 9 * * *" Check server status
```

定时生成的内容将会在每天上午9点发送至您的元宝主频道。

## 使用技巧

### 开启对话

向元宝中的机器人发送任意消息即可：

```
hello
```

机器人会在同一对话线程中回复。

### 可用命令

所有标准的Hermes命令在Yuanbao中均可使用：

| 命令 | 描述 |
|---------|-------------|
| `/new` | 开启新的对话 |
| `/model [provider:model]` | 显示或更换模型 |
| `/sethome` | 将当前聊天设为主频道 |
| `/status` | 显示会话信息 |
| `/help` | 显示可用命令 |

### 发送文件

要将文件发送给机器人，只需直接在Yuanbao聊天窗口中附上该文件即可。机器人会自动下载并处理该附件。

您也可以在附件旁附上一条消息：

```
Please analyze this document
```

### 接收文件

当您要求机器人创建或导出文件时，它会将文件直接发送到您的元宝聊天界面。

## 故障排除

### 机器人在线但未响应消息

**原因**：WebSocket握手过程中认证失败。

**解决方法**：
1. 确认APP_ID和APP_SECRET正确无误
2. 检查WebSocket地址是否可访问
3. 确保机器人账号拥有相应权限
4. 查看网关日志：`tail -f ~/.hermes/logs/gateway.log`

### 出现“连接被拒绝”错误

**原因**：WebSocket地址不可达或格式不正确。

**解决方法**：
1. 确认WebSocket地址的格式（应以`wss://`开头）
2. 检查与元宝API域名的网络连接状况
3. 确认防火墙允许WebSocket连接
4. 使用以下命令测试地址：`curl -I https://[YUANBAO_API_DOMAIN]`

### 媒体文件上传失败

**原因**：COS凭证无效或媒体服务器不可达。

**解决方法**：
1. 确认API_DOMAIN地址正确
2. 检查机器人是否已开启媒体文件上传权限
3. 确保媒体文件可访问且未损坏
4. 与平台管理员确认COS存储桶的配置情况

### 消息未发送到主频道

**原因**：主频道ID格式不正确，或定时任务尚未触发。

**解决方法**：
1. 确认YUANBAO_HOME_CHANNEL的格式正确
2. 使用 `/sethome` 命令让系统自动检测正确格式
3. 使用 `/status` 命令查看定时任务的调度情况
4. 确认机器人在目标聊天界面拥有发送权限

### 频繁断开连接

**原因**：WebSocket连接不稳定或网络状况不佳。

**解决方法**：
1. 查看网关日志中的错误模式
2. 在连接设置中增加心跳超时时间
3. 确保与元宝API的网络连接稳定
4. 可考虑开启详细日志记录：`HERMES_LOG_LEVEL=debug`

## 权限控制

元宝支持对私信和群组对话进行细粒度的权限控制：

```bash
# DM policy: open (default) | allowlist | disabled
YUANBAO_DM_POLICY=open
# Comma-separated user IDs allowed to DM the bot (only used when DM_POLICY=allowlist)
YUANBAO_DM_ALLOW_FROM=user_id_1,user_id_2

# Group policy: open (default) | allowlist | disabled
YUANBAO_GROUP_POLICY=open
# Comma-separated group codes allowed (only used when GROUP_POLICY=allowlist)
YUANBAO_GROUP_ALLOW_FROM=group_code_1,group_code_2
```

这些参数也可以在 `config.yaml` 中进行设置：

```yaml
platforms:
  yuanbao:
    extra:
      dm_policy: allowlist
      dm_allow_from: "user1,user2"
      group_policy: open
      group_allow_from: ""
```

## 高级配置

### 消息分块

Yuanbao 对单条消息的长度有限制。Hermes 会自动对过长的响应进行分块处理，采用支持 Markdown 的分割方式（会保留代码块、表格及段落边界）。

### 连接参数

适配器中预置了以下连接参数及合理的默认值：

| 参数 | 默认值 | 描述 |
|-------|---------|------|
| WebSocket 连接超时时间 | 15 秒 | 等待 WS 握手完成的时长 |
| 心跳间隔 | 30 秒 | 保持连接活跃的 ping 发送频率 |
| 最大重连次数 | 100 次 | 允许的重连最大尝试次数 |
| 重连退避时间 | 1秒 → 60秒（指数增长） | 每次重连尝试之间的等待时间 |
| 回复心跳间隔 | 2 秒 | 发送 RUNNING 状态的频率 |
| 发送超时时间 | 30 秒 | 发送出站 WS 消息的超时时长 |

:::note
目前这些参数无法通过环境变量进行配置。它们是针对常见的 Yuanbao 部署场景进行优化的。
:::

### 详细日志记录

开启调试日志可帮助排查连接问题：

```bash
HERMES_LOG_LEVEL=debug hermes gateway
```

## 与其他功能的集成

### Cron作业

规划在元宝上运行的任务：

```
/cron "0 */4 * * *" Report system health
```

查询结果将会同步至您的主频道。

### 后台任务

执行耗时较长的操作，且不会阻塞当前对话流程：

```
/background Analyze all files in the archive
```

### 跨平台消息功能

通过 CLI 向元宝发送消息：

```bash
hermes chat -q "Send 'Hello from CLI' to yuanbao:group:group_code"
```

## 相关文档

- [消息网关概述](./index.md)
- [Slash 命令参考](/reference/slash-commands)
- [定时任务](/user-guide/features/cron)
- [后台会话](/user-guide/cli#background-sessions)