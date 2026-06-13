---
sidebar_position: 4
title: "Tutorial: Team Telegram Assistant"
description: "Step-by-step guide to setting up a Telegram bot that your whole team can use for code help, research, system admin, and more"
---

# 设置团队专用 Telegram 助手

本教程将指导您搭建一个由 Hermes Agent 驱动的 Telegram 机器人，供团队成员共同使用。完成后，您的团队将拥有一个共享的 AI 助手，他们可以发送消息寻求代码编写、研究、系统管理等方面的帮助——同时通过用户级授权机制保障安全性。

## 我们要构建什么

这是一个具备以下功能的 Telegram 机器人：

- **任何经过授权的团队成员**均可私信寻求帮助——包括代码审查、研究支持、命令行操作、调试等；
- **运行在您的服务器上**，并拥有完整的工具访问权限——终端操作、文件编辑、网页搜索、代码执行等；
- **支持用户独立会话**——每位用户都有独立的对话上下文；
- **默认安全设置**——仅经过审批的用户才能与其交互，并提供两种授权方式；
- **可安排定时任务**——每日站会、系统健康检查以及提醒信息均可发送至团队频道。

---

## 前提条件

在开始之前，请确保您已具备以下条件：

- 在服务器或 VPS 上安装了 **Hermes Agent**（请勿安装在笔记本电脑上，因为机器人需要持续运行）。如果您尚未安装，请参考[安装指南](/getting-started/installation)；
- 拥有一个**个人 Telegram 账户**（即机器人所有者）；
- 已配置好**LLM 服务提供商**——至少需要在 `~/.hermes/.env` 文件中准备好 OpenAI、Anthropic 或其他受支持提供商的 API 密钥。

:::提示
每月 5 美元的 VPS 就足以运行该机器人。Hermes 本身体积很小——真正会产生费用的是 LLM API 调用，而这些调用都在远程完成。
:::

---

## 第一步：创建 Telegram 机器人

所有 Telegram 机器人都是从 **@BotFather** 开始的——这是 Telegram 用于创建机器人的官方机器人。

1. **打开 Telegram**，搜索 `@BotFather`，或直接访问 [t.me/BotFather](https://t.me/BotFather)；
2. 发送 `/newbot` 命令——BotFather 会询问您两个问题：
   - **显示名称**——即用户看到的名称（例如：`Team Hermes Assistant`）；
   - **用户名**——必须以 `bot` 结尾（例如：`myteam_hermes_bot`）；
3. **复制机器人令牌**——BotFather 会回复类似如下的内容：
   ```
   Use this token to access the HTTP API:
   7123456789:AAH1bGciOiJSUzI1NiIsInR5cCI6Ikp...
   ```
请保存此令牌——在下一步操作中会用到它。

4. **设置描述**（非必需，但建议操作）：
   ```
   /setdescription
   ```
选择您的机器人，然后输入类似如下的内容：
   ```
   Team AI assistant powered by Hermes Agent. DM me for help with code, research, debugging, and more.
   ```

5. **设置机器人命令**（可选——可为用户提供命令菜单）：
   ```
   /setcommands
   ```
选择您的机器人，然后粘贴内容：
   ```
   new - Start a fresh conversation
   model - Show or change the AI model
   status - Show session info
   help - Show available commands
   stop - Stop the current task
   ```

:::warning
请务必妥善保管您的机器人令牌，任何掌握该令牌的人都能控制您的机器人。若令牌泄露，请在 BotFather 中使用 `/revoke` 命令生成新的令牌。
:::

---

## 第 2 步：配置网关

您有两种选择：交互式设置向导（推荐）或手动配置。

### 方案 A：交互式设置（推荐）

```bash
hermes gateway setup
```

本指南将引导您通过方向键完成所有设置。请选择**Telegram**，粘贴您的机器人令牌，然后在提示时输入您的用户 ID。

### 方案 B：手动配置

在 `~/.hermes/.env` 文件中添加以下内容：

```bash
# Telegram bot token from BotFather
TELEGRAM_BOT_TOKEN=7123456789:AAH1bGciOiJSUzI1NiIsInR5cCI6Ikp...

# Your Telegram user ID (numeric)
TELEGRAM_ALLOWED_USERS=123456789
```

### 查找您的用户 ID

您的 Telegram 用户 ID 是一个数字值（而非用户名）。查找方法如下：

1. 在 Telegram 中发送消息给 [@userinfobot](https://t.me/userinfobot)
2. 该机器人会立即回复您的数字用户 ID
3. 将该数字复制到 `TELEGRAM_ALLOWED_USERS` 中

:::info
Telegram 用户 ID 是类似 `123456789` 这样的永久性数字，与可能发生变化的 `@username` 不同。在创建允许列表时，请始终使用数字 ID。
:::

---

## 第 3 步：启动网关

### 快速测试

首先在前台运行网关，以确保所有功能正常运行：

```bash
hermes gateway
```

您应该会看到如下输出：

```
[Gateway] Starting Hermes Gateway...
[Gateway] Telegram adapter connected
[Gateway] Cron scheduler started (tick every 60s)
```

打开 Telegram，找到您的机器人并发送消息给它。如果它回复了，那就说明一切正常。按 `Ctrl+C` 可以停止操作。

### 生产环境：以服务形式安装

如需实现可在重启后依然保持运行的持久部署：

```bash
hermes gateway install
sudo hermes gateway install --system   # Linux only: boot-time system service
```

此操作会创建一个后台服务：默认情况下为 Linux 系统上的用户级 **systemd** 服务，macOS 上则为 **launchd** 服务；如果指定了 `--system` 参数，则会生成 Linux 启动时的系统服务。

```bash
# Linux — manage the default user service
hermes gateway start
hermes gateway stop
hermes gateway status

# View live logs
journalctl --user -u hermes-gateway -f

# Keep running after SSH logout
sudo loginctl enable-linger $USER

# Linux servers — explicit system-service commands
sudo hermes gateway start --system
sudo hermes gateway status --system
journalctl -u hermes-gateway -f
```

```bash
# macOS — manage the service
hermes gateway start
hermes gateway stop
tail -f ~/.hermes/logs/gateway.log
```

:::提示 macOS的PATH设置
launchd plist会在安装时记录您的shell PATH，以便gateway的子进程能够找到Node.js和ffmpeg等工具。如果您之后安装了新工具，请重新运行`hermes gateway install`以更新该plist文件。
:::

### 验证其运行状态

```bash
hermes gateway status
```

接着，向你在 Telegram 上的机器人发送一条测试消息。你应该会在几秒钟内收到回复。

---

## 第 4 步：设置团队访问权限

现在我们来为你的团队成员授予访问权限。共有两种方法。

### 方法 A：静态白名单

收集每位团队成员的 Telegram 用户 ID（让他们给 [@userinfobot](https://t.me/userinfobot) 发消息），然后将这些 ID 以逗号分隔的形式列出：

```bash
# In ~/.hermes/.env
TELEGRAM_ALLOWED_USERS=123456789,987654321,555555555
```

完成更改后，请重启网关：

```bash
hermes gateway stop && hermes gateway start
```

### 方法 B：私信配对（团队推荐）

私信配对方式更为灵活——无需提前收集用户 ID。具体操作步骤如下：

1. **团队成员向机器人发送私信**——由于这些用户不在允许列表中，机器人会回复一个一次性使用的配对码：
   ```
   🔐 Pairing code: XKGH5N7P
   Send this code to the bot owner for approval.
   ```

2. **队友将代码发送给您**（可通过任何渠道——Slack、电子邮件或当面传递）。

3. **您在服务器上对其进行审批**：
   ```bash
   hermes pairing approve telegram XKGH5N7P
   ```

4. **已连接**——机器人会立即开始回复他们的消息。

**管理已配对用户：**

```bash
# See all pending and approved users
hermes pairing list

# Revoke someone's access
hermes pairing revoke telegram 987654321

# Clear expired pending codes
hermes pairing clear-pending
```

:::提示
对于团队而言，使用DM配对模式最为理想——添加新用户时无需重启网关，审批指令会立即生效。
:::

### 安全注意事项

- **切勿在具有终端访问权限的机器人上设置 `GATEWAY_ALLOW_ALL_USERS=true`**——任何找到该机器人的人都能在您的服务器上执行命令
- 配对码的有效期为**1小时**，且生成过程采用加密随机算法
- 通过速率限制可防范暴力攻击：每10分钟每位用户仅可发送1次请求，每个平台最多同时存在3个待处理配对码
- 若审批尝试失败5次，该平台将被锁定1小时
- 所有配对数据均以 `chmod 0600` 权限存储

---

## 第5步：配置机器人

### 设置主频道

**主频道**是机器人用于发送定时任务结果及主动通知的渠道。如果没有设置主频道，定时任务将无法输出结果。

**方案1：** 在机器人所属的任意Telegram群组或聊天室中使用 `/sethome` 命令。

**方案2：** 在 `~/.hermes/.env` 文件中手动设置：

```bash
TELEGRAM_HOME_CHANNEL=-1001234567890
TELEGRAM_HOME_CHANNEL_NAME="Team Updates"
```

若需获取频道 ID，可将 [@userinfobot](https://t.me/userinfobot) 添加到该群组中——它会告知该群组的聊天 ID。

### 配置工具进度显示

可控制机器人使用工具时显示的详细程度。在 `~/.hermes/config.yaml` 文件中进行设置：

```yaml
display:
  tool_progress: new    # off | new | all | verbose
```

| 模式 | 显示内容 |
|------|----------|
| `off` | 仅显示简洁的回复，不展示工具执行过程 |
| `new` | 每次调用新工具时显示简要状态（适用于消息交互场景） |
| `all` | 显示所有工具调用的详细信息 |
| `verbose` | 显示完整的工具输出，包括命令执行结果 |

用户也可以在聊天中通过 `/verbose` 命令随时更改当前会话的显示模式。

### 使用 SOUL.md 设置机器人个性

通过编辑 `~/.hermes/SOUL.md` 文件可自定义机器人的交流风格：

如需完整指南，请参阅 [在 Hermes 中使用 SOUL.md](/guides/use-soul-with-hermes)。

```markdown
# Soul
You are a helpful team assistant. Be concise and technical.
Use code blocks for any code. Skip pleasantries — the team
values directness. When debugging, always ask for error logs
before guessing at solutions.
```

### 添加项目上下文

如果您的团队负责特定项目，请创建上下文文件，以便机器人了解您所使用的技术栈：

```markdown
<!-- ~/.hermes/AGENTS.md -->
# Team Context
- We use Python 3.12 with FastAPI and SQLAlchemy
- Frontend is React with TypeScript
- CI/CD runs on GitHub Actions
- Production deploys to AWS ECS
- Always suggest writing tests for new code
```

:::info
上下文文件会被注入到每个会话的系统提示词中。请保持其简洁——每一个字符都会占用您的令牌额度。
:::

---

## 第 6 步：设置定时任务

在网关运行后，您可以安排定期任务，将结果发送至您的团队频道。

### 每日站会总结

在 Telegram 上向机器人发送消息即可：

```
Every weekday at 9am, check the GitHub repository at
github.com/myorg/myproject for:
1. Pull requests opened/merged in the last 24 hours
2. Issues created or closed
3. Any CI/CD failures on the main branch
Format as a brief standup-style summary.
```

该智能体会自动创建定时任务，并将处理结果发送至您指定的聊天窗口（或主频道）。 

### 服务器健康检查

```
Every 6 hours, check disk usage with 'df -h', memory with 'free -h',
and Docker container status with 'docker ps'. Report anything unusual —
partitions above 80%, containers that have restarted, or high memory usage.
```

### 定时任务管理

```bash
# From the CLI
hermes cron list          # View all scheduled jobs
hermes cron status        # Check if scheduler is running

# From Telegram chat
/cron list                # View jobs
/cron remove <job_id>     # Remove a job
```

:::warning
定时任务触发的提示语会在全新的会话中执行，且不会保留任何之前的对话记录。请确保每个提示语都包含智能体所需的所有上下文信息——包括文件路径、URL、服务器地址以及明确的操作指令。
:::

---

## 生产环境使用建议

### 为保障安全，请使用 Docker

在团队共享机器人上，建议将 Docker 作为终端后端，这样智能体命令便会在容器中运行，而非直接在主机上执行：

```bash
# In ~/.hermes/.env
TERMINAL_BACKEND=docker
TERMINAL_DOCKER_IMAGE=nikolaik/python-nodejs:python3.11-nodejs20
```

或者在 `~/.hermes/config.yaml` 中：

```yaml
terminal:
  backend: docker
  container_cpu: 1
  container_memory: 5120
  container_persistent: true
```

这样一来，即便有人要求机器人执行具有破坏性的操作，您的主机系统也能得到保护。

### 监控网关

```bash
# Check if the gateway is running
hermes gateway status

# Watch live logs (Linux)
journalctl --user -u hermes-gateway -f

# Watch live logs (macOS)
tail -f ~/.hermes/logs/gateway.log
```

### 保持 Hermes 最新状态

在 Telegram 中，向该机器人发送 `/update` 命令——它便会自动下载最新版本并重启。或者从服务器端操作：

```bash
hermes update
hermes gateway stop && hermes gateway start
```

### 日志位置

| 日志类型 | 存储位置 |
|----------|----------|
| 网关日志 | Linux系统：`journalctl --user -u hermes-gateway`；macOS系统：`~/.hermes/logs/gateway.log` |
| Cron任务输出 | `~/.hermes/cron/output/{job_id}/{timestamp}.md` |
| Cron任务配置 | `~/.hermes/cron/jobs.json` |
| 配对数据 | `~/.hermes/pairing/` |
| 会话历史 | `~/.hermes/sessions/` |

---

## 进一步学习

您已经成功搭建了一个可用的团队Telegram助手。以下是更多拓展方向：

- **[安全指南](/user-guide/security)** — 深入了解授权机制、容器隔离及命令审批流程
- **[消息网关](/user-guide/messaging)** — 关于网关架构、会话管理及聊天指令的完整参考资料
- **[Telegram配置](/user-guide/messaging/telegram)** — 包含语音消息和文本转语音功能的平台专属配置指南
- **[定时任务](/user-guide/features/cron)** — 支持多种交付选项与复杂cron表达式的进阶调度功能
- **[上下文文件](/user-guide/features/context-files)** — 用于存储项目相关知识的AGENTS.md、SOUL.md及.cursorrules文件
- **[个性设置](/user-guide/features/personality)** — 内置的个性预设选项及自定义角色定义方法
- **支持更多平台** — 同一网关可同时处理[Discord](/user-guide/messaging/discord)、[Slack](/user-guide/messaging/slack)和[WhatsApp](/user-guide/messaging/whatsapp)消息

---

*如有疑问或遇到问题？请在GitHub上创建 issue — 我们欢迎大家的贡献。*
