---
title: "Imessage — Send and receive iMessages/SMS via the imsg CLI on macOS"
sidebar_label: "Imessage"
description: "Send and receive iMessages/SMS via the imsg CLI on macOS"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# iMessage

通过 macOS 上的 imsg CLI 发送和接收 iMessage/SMS 消息。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/apple/imessage` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | macos |
| 标签 | `iMessage`, `SMS`, `消息传递`, `macOS`, `Apple` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# iMessage

使用 `imsg` 命令通过 macOS 的 Messages.app 应用读取和发送 iMessage/SMS 消息。

## 先决条件

- 已登录 Messages.app 的 **macOS** 系统
- 安装对应工具：`brew install steipete/tap/imsg`
- 为终端授予“全盘访问”权限（系统设置 → 隐私 → 全盘访问）
- 根据提示为 Messages.app 授予自动化权限

## 适用场景

- 用户要求发送 iMessage 或短信
- 查看 iMessage 对话历史记录
| 查看最近的 Messages.app 聊天记录
- 向电话号码或 Apple ID 发送消息

## 不适用场景

- Telegram/Discord/Slack/WhatsApp 消息 → 请使用相应的网关通道
- 群组聊天管理（添加/移除成员）→ 不支持
- 批量发送消息 → 必须先获得用户确认

## 快速参考

### 列出聊天记录

```bash
imsg chats --limit 10 --json
```

### 查看历史记录

```bash
# By chat ID
imsg history --chat-id 1 --limit 20 --json

# With attachments info
imsg history --chat-id 1 --limit 20 --attachments --json
```

### 发送消息

```bash
# Text only
imsg send --to "+14155551212" --text "Hello!"

# With attachment
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# Force iMessage or SMS
imsg send --to "+14155551212" --text "Hi" --service imessage
imsg send --to "+14155551212" --text "Hi" --service sms
```

### 关注新消息

```bash
imsg watch --chat-id 1 --attachments
```

## 服务选项

- `--service imessage` — 强制使用 iMessage（要求收件人支持 iMessage）
- `--service sms` — 强制发送短信（绿色气泡图标）
- `--service auto` — 由 Messages.app 自动决定（默认值）

## 规则

1. 发送消息前务必确认收件人及消息内容
2. 未经用户明确授权，不得向未知号码发送消息
3. 附加文件前需确认文件路径存在
4. 禁止刷屏——请控制发送频率

## 典型使用流程

用户：“给妈妈发消息，告诉她我会晚到”

```bash
# 1. Find mom's chat
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. Confirm with user: "Found Mom at +1555123456. Send 'I'll be late' via iMessage?"

# 3. Send after confirmation
imsg send --to "+1555123456" --text "I'll be late"
```
