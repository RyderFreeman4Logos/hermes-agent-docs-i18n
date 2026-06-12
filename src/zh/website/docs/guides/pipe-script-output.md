---
sidebar_position: 12
title: "Pipe Script Output to Messaging Platforms"
description: "Send text from any shell script, cron job, CI hook, or monitoring daemon to Telegram, Discord, Slack, Signal, and other platforms using `hermes send`."
---

# 将脚本输出发送至消息平台

`hermes send` 是一个轻量级且支持脚本编写的命令行工具，可用于将消息推送到已为 Hermes 配置的任何消息平台。可将其视为跨平台的通知用 `curl` —— 无需运行中的网关，无需大型语言模型，也无需在每个脚本中重复粘贴机器人令牌。

适用场景包括：

- 系统监控（内存、磁盘、GPU温度以及长时间运行的任务完成情况）
- CI/CD 通知（部署完成、测试失败等）
- 需要将结果发送给用户的 Cron 脚本
- 从终端快速发送一次性消息
- 将任何工具的输出转发到任意目标（例如 `make | hermes send --to slack:#builds`）

该命令会复用 `hermes gateway` 已有的凭证和平台适配器，因此无需额外维护配置项。

---

## 快速入门

```bash
# Plain text to the home channel for a platform
hermes send --to telegram "deploy finished"

# Pipe in stdout from anything
echo "RAM 92%" | hermes send --to telegram:-1001234567890

# Send a file
hermes send --to discord:#ops --file /tmp/report.md

# Attach a subject/header line
hermes send --to slack:#eng --subject "[CI] build.log" --file build.log

# Thread target (Telegram topic, Discord thread)
hermes send --to telegram:-1001234567890:17585 "threaded reply"

# List every configured target
hermes send --list

# Filter by platform
hermes send --list telegram
```

## 参数说明

| 标志 | 描述 |
|------|-------------|
| `-t, --to TARGET` | 目标地址。详见[目标格式](#target-formats)。 |
| `message`（位置参数） | 消息内容。如省略则从`--file`指定文件或标准输入读取。 |
| `-f, --file PATH` | 从文件读取消息内容。使用`--file -`则强制从标准输入读取。 |
| `-s, --subject LINE` | 在消息内容前添加标题行/主题行。 |
| `-l, --list` | 列出所有可用的目标地址。可选的位置参数，用于筛选平台。 |
| `-q, --quiet` | 成功时不输出标准输出（仅返回退出码——非常适合脚本使用）。 |
| `--json` | 以原始JSON格式输出发送结果。 |
| `-h, --help` | 显示内置帮助文本。 |

### 目标格式

| 格式 | 示例 | 含义 |
|------|---------|------|
| `platform` | `telegram` | 发送到该平台配置的主频道 |
| `platform:chat_id` | `telegram:-1001234567890` | 指定特定的数字聊天室、群组或用户 |
| `platform:chat_id:thread_id` | `telegram:-1001234567890:17585` | 指定特定的讨论串或Telegram论坛主题 |
| `platform:#channel` | `discord:#ops` | 以易读的频道名称形式（会自动从频道目录中解析） |
| `platform:+E164` | `signal:+15551234567` | 适用于手机号码格式的平台：Signal、SMS、WhatsApp |

Hermes为以下所有平台提供了适配器，可作为目标地址使用：
`telegram`、`discord`、`slack`、`signal`、`sms`、`whatsapp`、`matrix`、
`mattermost`、`feishu`、`dingtalk`、`wecom`、`weixin`、`email`以及其他平台。

### 退出码

| 代码 | 含义 |
|------|------|
| `0` | 发送（或列表查询）操作成功 |
| `1` | 在平台层面发送失败（如认证问题、权限不足或网络故障） |
| `2` | 使用方式/参数/配置错误 |

这些退出码遵循标准的Unix规范，因此您的脚本可以像处理`curl`或`grep`的退出码一样对其进行判断。

---

## 消息内容解析顺序

`hermes send`会按照以下顺序解析消息内容：

1. **位置参数** — `hermes send --to telegram "hi"`
2. **`--file PATH`参数** — `hermes send --to telegram --file msg.txt`
3. **通过管道传入的标准输入** — `echo hi | hermes send --to telegram`

当标准输入来自TTY设备（而非管道）时，Hermes不会等待用户输入——此时会直接返回明确的错误信息。这样做可避免因脚本意外遗漏消息内容而导致程序挂起。

---

## 实际应用示例

### 监控：内存/磁盘使用情况警报

只需用一行通用的命令，即可替代原有监控脚本中零散的`curl https://api.telegram.org/...`调用：

```bash
#!/usr/bin/env bash
ram_pct=$(free | awk '/^Mem:/ {printf "%d", $3 * 100 / $2}')
if [ "$ram_pct" -ge 85 ]; then
  hermes send --to telegram --subject "⚠ MEMORY WARNING" \
    "RAM ${ram_pct}% on $(hostname)"
fi
```

由于 `hermes send` 会复用您已配置的 Hermes 设置，因此相同的脚本即可在任何安装了 Hermes 的主机上运行——无需手动将机器人令牌导出到每台机器的环境中。

:::提示：避免向网关发送自身相关警报
对于那些可能在网关本身出现故障时触发的监控警报（如内存溢出警报、磁盘空间不足警报），建议继续使用最简化的 `curl` 调用方式，而非 `hermes send`。即便由于系统运行异常导致 Python 解释器无法加载，您依然希望相关警报能够正常发送出去。
:::

### CI / CD：构建与测试结果

```bash
# In .github/workflows/deploy.yml or any CI script
if ./scripts/deploy.sh; then
  hermes send --to slack:#deploys "✅ ${CI_COMMIT_SHA:0:7} deployed"
else
  tail -n 100 deploy.log | hermes send \
    --to slack:#deploys --subject "❌ deploy failed"
  exit 1
fi
```

### Cron：每日报告

```bash
# Crontab entry
0 9 * * * /usr/local/bin/generate-metrics.sh \
  | /home/me/.hermes/bin/hermes send \
      --to telegram --subject "Daily metrics $(date +%Y-%m-%d)"
```

### 长时间运行的任务：任务完成时发送 Ping 消息

```bash
./train.py --epochs 200 && \
  hermes send --to telegram "training done" || \
  hermes send --to telegram "training failed (exit $?)"
```

### 使用 `--json` 和 `--quiet` 参数进行脚本化操作

```bash
# Hard-fail a script if delivery fails; don't clutter logs on success
hermes send --to telegram --quiet "keepalive" || {
  echo "Telegram delivery failed" >&2
  exit 1
}

# Capture the message ID for later editing / threading
msg_id=$(hermes send --to discord:#ops --json "build started" \
  | jq -r .message_id)
```

---

## `hermes send` 需要运行网关吗？

**通常不需要。** 对于任何机器人令牌平台——Telegram、Discord、Slack、Signal、SMS、WhatsApp Cloud API以及大多数其他平台——`hermes send`都会直接使用`~/.hermes/.env`和`~/.hermes/config.yaml`中的凭证来调用该平台的REST接口。它是一个独立的子进程，一旦消息发送完成便会立即退出。

只有那些依赖持久适配器连接的**插件平台**才需要运行网关（例如，那些会保持长时间开启WebSocket连接的自定义插件）。在这种情况下，系统会给出明确的错误提示，指出问题出在网关上；请使用`hermes gateway start`启动网关后再试。

---

## 列出与发现目标

在向特定频道发送消息之前，您可以先查看有哪些可用的目标。

```bash
# Every target across every configured platform
hermes send --list

# Just Telegram targets
hermes send --list telegram

# Machine-readable
hermes send --list --json
```

该频道列表是根据 `~/.hermes/channel_directory.json` 生成的，而网关在运行过程中会每隔几分钟刷新一次该文件。如果看到“尚未发现频道”的提示，请先启动一次网关（执行 `hermes gateway start`），以便其填充缓存。

在发送消息时，系统会依据此缓存将易于识别的名称（如 `discord:#ops`、`slack:#engineering`）转换为对应的实际标识，因此您无需记住那些数字编号。

---

## 与其他方法的对比

| 方法 | 多平台支持 | 是否复用 Hermes 凭证 | 是否需要网关 | 最适合的场景 |
|------|------------|---------------------|--------------|------------|
| `hermes send` | ✅ | ✅ | 否（使用机器人令牌） | 以上所有场景 |
| 直接对每个平台使用 `curl` 命令 | 需分别为每个平台编写脚本 | 手动操作 | 否 | 需要实时监控的场景 |
| 使用 `cron` 任务配合 `--deliver` 参数 | ✅ | ✅ | 否 | 需要定时执行的代理任务 |
| `send_message` 代理工具 | ✅ | ✅ | 否 | 在代理循环内部使用 |

`hermes send` 被刻意设计为最简洁的接口。如果需要由代理来决定发送内容，可在聊天界面或 `cron` 任务中使用 `send_message` 工具。若需定时执行并生成基于大语言模型的内容，可使用 `cronjob(action='create', prompt=...)` 并配合 `deliver='telegram:...'` 参数。而只需传输原始字符串时，直接使用 `hermes send` 即可。

---

## 相关内容

- [利用 Cron 自动化各类任务](/guides/automate-with-cron) ——
  可将输出自动发送到任意平台的定时任务。
- [网关内部机制](/developer-guide/gateway-internals) ——
  `hermes send` 与 `cron` 任务所共用的消息传递路由系统。
- [消息平台配置指南](/user-guide/messaging/) ——
  针对每个平台的单次配置说明。
