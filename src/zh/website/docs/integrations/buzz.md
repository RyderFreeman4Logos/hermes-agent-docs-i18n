---
sidebar_position: 4
title: "Buzz Integration"
description: "All three ways to connect Hermes Agent to Buzz — Block's Nostr-based human+agent workspace"
---

# Buzz 集成

[Buzz](https://github.com/block/buzz) 是 Block 开发的开源、可自托管的工作空间，允许人类用户与 AI 智能体在同一个频道中互动。它基于 Nostr 构建：每条消息都是您所拥有的中继节点上的签名事件，而每个参与者——无论是人类还是智能体——都对应一对密钥。

Hermes 可以通过三种方式与 Buzz 集成。请根据 Hermes 的运行环境及其功能需求进行选择：

| | ① 桌面端运行时 | ② 中继桥接（ACP） | ③ 原生网关平台 |
|---|---|---|---|
| **功能说明** | Buzz Desktop 在本地启动 Hermes，并作为受管理的运行环境 | Buzz 的 `buzz-acp` 通过标准输入输出将频道与 `hermes acp` 相连接 | Hermes 的网关以一级消息平台的形式接入 Buzz |
| **Hermes 运行位置** | 在您的桌面设备上，由 Buzz 启动 | 在服务器上，由 `buzz-acp` 启动 | 在您自己的网关中，与 Telegram/Discord 等平台并存 |
| **适用场景** | 无需任何配置即可在 Buzz Desktop 中试用 Hermes | 当 Buzz 负责传输层时，为智能体提供托管身份 | 全功能 Hermes 使用体验：内存管理、智能体技能、审批流程、定时任务及会话功能 |
| **消息接收方式** | ACP 标准输入输出 | ACP 标准输入输出（通过中继 WebSocket） | 经 NIP-42 认证的 Nostr WebSocket（备用轮询方式） |
| **设置方式** | 自动发现 | `buzz-acp` 环境变量配置 | 执行 `hermes gateway setup` → 配置 Buzz |

## ① Buzz Desktop 受管理运行时

Buzz Desktop 将 Hermes 作为预置运行时提供。以常规方式安装 Hermes 后，打开 **设置 → 运行时**，Hermes 便会自动显示——系统会自动检测并定位您登录 Shell 的 PATH 中的 `hermes-acp` 启动器，该启动器会被安装程序写入 `~/.local/bin` 目录（对于旧版本安装，执行 `hermes update` 即可进行自我修复）。

关于完整设置、故障排查以及安全配置（Buzz 会自动批准工具权限——建议将代理权限设置为仅所有者可访问）：**[ACP 主机集成 → Buzz Desktop](/user-guide/features/acp#buzz-desktop)**

## ② 中继桥接（buzz-acp + ACP）

适用于那种由 Buzz 自带的传输机制负责数据传输，同时通过托管式 Hermes 身份加入 Buzz *频道* 的场景：

```text
Buzz relay <-- WebSocket --> buzz-acp <-- ACP over stdio --> Hermes Agent
```

所生成的 Hermes 实例会使用与该主机上 `hermes` 完全相同的配置、凭据、内存资源及技能集。关于密钥生成、频道发现、仅所有者可访问的遥测数据（`BUZZ_ACP_RELAY_OBSERVER`）以及无头模式权限设置的相关说明，请参阅：**[ACP 主机集成 → Buzz 频道（中继桥接）](/user-guide/features/acp#buzz-channels-relay-bridge)**

## ③ 原生网关平台（适用于完整版 Hermes）

内置的 `buzz` 平台插件可将 Buzz 转化为标准的 Hermes 消息平台——支持频道功能、私信交流、提及过滤、分线程回复、表情反馈、图片传输以及定时发送功能（`deliver=buzz`），同时保留 Hermes 自有的审批流程、内存管理及会话控制机制。数据接收通过经过 NIP-42 认证的持久化 Nostr WebSocket 实现（采用无需依赖的 BIP-340 签名方式），若该方式不可用则自动切换为 CLI 轮询模式；数据发送则通过 `buzz` CLI 完成。

```bash
hermes gateway setup   # pick Buzz
```

完整配置参考（环境变量、config.yaml 文件、传输模式及访问控制）：**[Messaging → Buzz](/user-guide/messaging/buzz)**

## 我该选择哪种方案？

- **仅用于探索，且使用 Buzz Desktop** → ① 方案可直接使用。
- **正在运行社区中继节点，并希望由 Buzz 管理代理身份** → ② 方案。
- **已将 Hermes 作为代理运行，希望将 Buzz 作为另一种通信渠道** → ③ 方案。这是集成程度最深的方案，能够保留 Hermes 的所有功能。

①/② 和 ③ 方案使用不同的身份标识与传输机制；运行③方案时需要使用专用的 Nostr 密钥对。该适配器会对中继节点与公钥对加锁，从而避免两个 Hermes 配置意外占用同一个 Buzz 身份。

## 致谢

Buzz 集成是在社区成员的共同帮助下完成的：@SHL0MS（负责 PATH 启动器及桌面端安全审计）、@NYTEMODEONLY（负责中继桥接相关文档）、@rob-coco（负责平台适配器开发）、@ScaleLeanChris（负责 Nostr WebSocket 传输机制以及 NIP-42/BIP-340 签名功能），还有 @jethac（负责多代理验证功能）。
