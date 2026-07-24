---
title: "Agentmail — Give the agent its own inbox: send and receive email"
sidebar_label: "Agentmail"
description: "Give the agent its own inbox: send and receive email"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Agentmail

为智能体配置专属邮箱：实现邮件的发送与接收功能。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/email/agentmail` 安装 |
| 路径 | `optional-skills/email/agentmail` |
| 版本 | `1.0.0` |
| 支持平台 | linux、macos、windows |
| 标签 | `email`、`communication`、`agentmail`、`mcp` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。智能体在技能处于激活状态时，看到的指令即为此内容。
:::

# AgentMail — 智能体专属邮箱

## 前提条件

- **AgentMail API 密钥**（必需）——请访问 https://console.agentmail.to 注册（免费套餐：3 个邮箱账户，每月 3,000 封邮件；付费套餐起价每月 20 美元）
- Node.js 18+（用于 MCP 服务器）

## 适用场景
当您需要以下功能时，可使用此技能：
- 为智能体配置专属的电子邮件地址
- 代表智能体自动发送邮件
- 接收并阅读 incoming 邮件
- 管理邮件对话与线程
- 通过邮箱注册服务或完成身份验证
- 通过邮件与其他智能体或人类进行沟通

请注意：此功能**不用于读取用户的个人邮件**（此类需求请使用 himalaya 或 Gmail）。AgentMail 能为智能体提供独立的身份标识和专属邮箱。

## 设置步骤

### 1. 获取 API 密钥
- 访问 https://console.agentmail.to
- 创建账户并生成 API 密钥（密钥以 `am_` 开头）

### 2. 配置 MCP 服务器
在 `~/.hermes/config.yaml` 文件中添加相关配置（请直接粘贴您的实际 API 密钥——MCP 环境变量不会从 .env 文件中读取）：
```yaml
mcp_servers:
  agentmail:
    command: "npx"
    args: ["-y", "agentmail-mcp"]
    env:
      AGENTMAIL_API_KEY: "am_your_key_here"
```

### 3. 重启 Hermes Agent
```bash
hermes
```
目前，全部11种AgentMail工具均已实现自动可用。

## 可用工具（通过MCP接口）

| 工具 | 描述 |
|------|------|
| `list_inboxes` | 列出所有代理收件箱 |
| `get_inbox` | 获取特定收件箱的详细信息 |
| `create_inbox` | 创建新收件箱（需获取真实电子邮件地址） |
| `delete_inbox` | 删除收件箱 |
| `list_threads` | 列出收件箱中的邮件线程 |
| `get_thread` | 获取特定的邮件线程 |
| `send_message` | 发送新邮件 |
| `reply_to_message` | 回复现有邮件 |
| `forward_message` | 转发邮件 |
| `update_message` | 更新邮件标签/状态 |
| `get_attachment` | 下载邮件附件 |

## 操作步骤

### 创建收件箱并发送邮件
1. 创建专用收件箱：
   - 使用`create_inbox`函数并指定用户名（例如`hermes-agent`）
   - 代理将获得如下地址：`hermes-agent@agentmail.to`
2. 发送邮件：
   - 使用`send_message`函数，传入`inbox_id`、`to`、`subject`和`text`参数
3. 查看回复：
   - 使用`list_threads`查看即将到来的对话
   - 使用`get_thread`读取特定线程的内容

### 查看收到的邮件
1. 使用`list_inboxes`查找您的收件箱ID
2. 使用该收件箱ID搭配`list_threads`查看相关对话
3. 使用`get_thread`阅读某个线程及其所有邮件内容

### 回复邮件
1. 使用`get_thread`获取目标邮件线程
2. 使用`reply_to_message`函数，传入邮件ID及您的回复内容

## 实际应用案例

**注册服务：**
```
1. create_inbox (username: "signup-bot")
2. Use the inbox address to register on the service
3. list_threads to check for verification email
4. get_thread to read the verification code
```

**智能体与人类的交互功能：**
```
1. create_inbox (username: "hermes-outreach")
2. send_message (to: user@example.com, subject: "Hello", text: "...")
3. list_threads to check for replies
```

## 常见问题
- 免费套餐仅支持3个收件箱以及每月3,000封邮件处理量
- 免费套餐下的邮件均来自`@agentmail.to`域名（付费套餐则可使用自定义域名）
- MCP服务器需使用Node.js 18及以上版本运行（可通过`npx -y agentmail-mcp`命令安装）
- 必须安装Python的`mcp`包：`pip install mcp`
- 若需实时接收邮件（通过Webhook），则需要一台公网服务器；个人使用时可改用通过cronjob定时执行`list_threads`命令的方式

## 验证
设置完成后，可通过以下方式进行测试：
```
hermes --toolsets mcp -q "Create an AgentMail inbox called test-agent and tell me its email address"
```
您应该会看到返回的新收件箱地址。 

## 参考资料
- AgentMail 文档：https://docs.agentmail.to/
- AgentMail 控制台：https://console.agentmail.to
- AgentMail MCP 代码库：https://github.com/agentmail-to/agentmail-mcp
- 定价信息：https://www.agentmail.to/pricing
