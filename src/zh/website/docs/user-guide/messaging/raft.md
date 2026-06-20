---
sidebar_position: 19
title: "Raft"
description: "Connect Hermes Agent to Raft as an external agent via wake-channel bridge"
---

# Raft 设置

Hermes 通过本地的 wake-channel bridge 作为外部代理与 [Raft](https://raft.build) 相连。该适配器会启动一个回环 HTTP 端点，用于接收来自桥接器的无内容唤醒提示，随后将其注入 Hermes 网关的会话处理流程中。代理则通过 Raft CLI 读取并发送消息——适配器从不直接处理消息内容或传输状态。

:::info 分工协作
- **桥接器**负责：唤醒提示的接收、去重、重试机制、重新连接、至少一次交付以及日志记录。
- **Hermes 适配器**负责：维护本地的唤醒端点，以及向代理上下文注入简短通知。
- **代理**负责：通过 CLI 拉取消息（`raft message check`）、发送回复（`raft message send`）以及执行所有其他与 Raft 的交互操作。

适配器不持有任何 Raft 凭证——仅拥有用于桥接器与端点之间本地认证的会话级共享令牌。
:::

---

## 先决条件

- 一个可创建外部代理的 **Raft 工作空间**
- 已安装 **Raft CLI**，并且已使用该外部代理账号登录
- **aiohttp** — Python 包（包含在 Hermes 的 `[all]` 额外组件中）

在 Raft 中，打开“Agents”菜单，创建一个外部代理，然后按照设置向导安装 Raft CLI 并登录代理账号。创建完成后，Raft 会显示一份 Hermes 设置指南，其中列出了启动网关所需的环境变量和配置参数。

---

## 设置步骤

在 `~/.hermes/.env` 文件中添加以下内容：

```bash
RAFT_PROFILE=your-agent-profile
```

就这样——一旦设置了 `RAFT_PROFILE`，适配器便会自动启用。它会在每个会话中生成一个桥接令牌，选定一个临时端口，并在网关启动时自动创建相应的桥接子进程。

---

## 工作原理

```
Raft Server → Bridge (wake-hints SSE) → POST /wake → Hermes Adapter → Agent context
Agent → raft message check → Raft Server (message bodies)
Agent → raft message send → Raft Server (replies)
```

1. Raft服务器通过SSE向桥接进程发送唤醒提示。  
2. 桥接进程会将每个提示作为`POST /wake`请求转发至适配器的回环接口地址。  
3. 适配器会验证桥接令牌，确认载荷中不包含实际内容，随后将唤醒通知注入Hermes会话中。  
4. Agent收到唤醒通知后，即可使用Raft CLI读取消息并作出回复。  

根据协议规定，唤醒载荷**不得包含任何实际内容**——它们仅携带元数据（如事件ID、消息ID、时间戳），绝不会包含消息正文、频道名称或发送者身份信息。若载荷中存在类似`text`、`body`、`content`、`messages`等用于存储内容的字段，适配器将会拒绝该载荷。  

---

## 桥接进程

适配器会自动以子进程形式启动`raft agent bridge`，并传入接口地址与令牌。该桥接进程会使用配置好的配置文件连接到Raft服务器，开始转发唤醒提示。当网关关闭时，桥接进程也会随之终止。  

---

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `RAFT_PROFILE` | Raft Agent的配置文件标识符——设置该变量即可自动启用适配器 | _(必需)_ |
