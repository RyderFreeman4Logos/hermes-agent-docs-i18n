---
sidebar_position: 7
title: "Gateway Internals"
description: "How the messaging gateway boots, authorizes users, routes sessions, and delivers messages"
---

# 网关内部结构

消息网关是一个长期运行的进程，它通过统一的架构将 Hermes 与 20 多种外部消息平台连接起来。

## 关键文件

| 文件 | 功能 |
|------|------|
| `gateway/run.py` | `GatewayRunner` —— 主循环处理、斜杠命令解析以及消息分发（文件体积较大；具体行数请查看 Git 代码） |
| `gateway/session.py` | `SessionStore` —— 负责对话数据的持久化存储及会话密钥的生成 |
| `gateway/delivery.py` | 将消息发送到目标平台或渠道 |
| `gateway/pairing.py` | 处理用户授权所需的私信配对流程 |
| `gateway/channel_directory.py` | 将聊天 ID 映射为便于识别的名称，以便定时任务发送消息 |
| `gateway/hooks.py` | 负责钩子的发现、加载以及生命周期事件的触发 |
| `gateway/mirror.py` | 实现 `send_message` 功能的跨会话消息同步 |
| `gateway/status.py` | 管理针对特定用户配置的网关实例的令牌锁定机制 |
| `gateway/builtin_hooks/` | 用于添加始终注册的钩子的扩展点（目前尚未提供任何预置钩子） |
| `gateway/platforms/` | 各消息平台的适配器（每个平台对应一个文件） |

## 架构概览

```text
┌─────────────────────────────────────────────────┐
│                  GatewayRunner                  │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Telegram │  │ Discord  │  │  Slack   │       │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │
│       └─────────────┼─────────────┘             │
│                     ▼                           │
│              _handle_message()                  │
│                     │                           │
│         ┌───────────┼───────────┐               │
│         ▼           ▼           ▼               │
│  Slash command   AIAgent    Queue/BG            │
│    dispatch      creation   sessions            │
│                     │                           │
│                     ▼                           │
│                 SessionStore                    │
│              (SQLite persistence)               │
└───────┴─────────────┴─────────────┴─────────────┘
```

## 消息流转流程

当有消息从任意平台传来时，处理流程如下：

1. **平台适配器**接收原始事件，并将其标准化为 `MessageEvent` 对象。
2. **基础适配器**会检查当前会话状态：
   - 若该会话对应的智能体正在运行 → 将消息放入队列并设置中断事件；
   - 若为 `/approve`、`/deny`、`/stop` 类型的指令 → 直接跳过状态检查并立即处理。
3. **GatewayRunner._handle_message()**函数接收该事件后，执行以下操作：
   - 通过 `_session_key_for_source()` 函数获取会话密钥（格式为：`agent:main:{platform}:{chat_type}:{chat_id}`）；
   - 进行权限验证（详见下文“授权机制”）；
   - 若为斜杠命令 → 将其转发给命令处理模块；
   - 若智能体已处于运行状态 → 拦截如 `/stop`、`/status` 等命令；
   - 其余情况 → 创建 `AIAgent` 实例并开始对话处理。
4. 最终响应会通过平台适配器传回。

### 会话密钥格式

会话密钥用于编码完整的路由上下文信息：

```
agent:main:{platform}:{chat_type}:{chat_id}
```

例如：`agent:main:telegram:private:123456789`。支持线程功能的平台（如 Telegram 论坛主题、Discord 线程、Slack 线程）可能会在 `chat_id` 中包含线程 ID。**切勿手动生成会话密钥**，应始终使用 `gateway/session.py` 中的 `build_session_key()` 函数来生成。

### 两级消息过滤机制

当智能体正在运行时，传入的消息需依次经过两级过滤机制：

1. **第一级——基础适配器**（`gateway/platforms/base.py`）：会检查 `_active_sessions`。如果该会话处于活跃状态，便会将消息放入 `_pending_messages` 队列中，并设置中断事件。这样就能在消息到达网关运行器之前将其拦截。

2. **第二级——网关运行器**（`gateway/run.py`）：会检查 `_running_agents`。它会拦截特定的命令（如 `/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`），并对其进行相应处理。其余所有消息都会触发 `running_agent.interrupt()` 函数。

对于那些必须在智能体被阻塞时仍需送达运行器的命令（例如 `/approve`），会通过 `await self._message_handler(event)` 以**直接方式**进行处理——这样做可以绕过后台任务系统，从而避免竞态条件。

## 权限控制

网关采用多层权限验证机制，按顺序依次进行判断：

1. **各平台的“允许所有用户”标志**（如 `TELEGRAM_ALLOW_ALL_USERS`）：如果该标志被设置，那么该平台上的所有用户均具有访问权限。
2. **平台白名单**（如 `TELEGRAM_ALLOWED_USERS`）：以逗号分隔的用户 ID 列表。
3. **私信配对功能**：已认证的用户可通过配对码引导新用户加入。
4. **全局“允许所有用户”设置**（`GATEWAY_ALLOW_ALL_USERS`）：如果该设置被启用，那么所有平台上的所有用户均具有访问权限。
5. **默认策略：拒绝访问**：未获得授权的用户将被拒绝接入。

### 私信配对流程

```text
Admin: /pair
Gateway: "Pairing code: ABC123. Share with the user."
New user: ABC123
Gateway: "Paired! You're now authorized."
```

配对状态会保存在 `gateway/pairing.py` 文件中，因此即使在重启后也能保留。

## Slash命令分发机制

网关中的所有Slash命令都会经过相同的解析流程：

1. `hermes_cli/commands.py` 中的 `resolve_command()` 函数会将输入映射为标准名称（同时支持别名和前缀匹配处理）
2. 该标准名称会与 `GATEWAY_KNOWN_COMMANDS` 列表进行比对
3. `_handle_message()` 函数中的处理器会根据标准名称来选择对应的处理逻辑
4. 部分命令的可用性还受配置限制（通过 `CommandDef` 中的 `gateway_config_gate` 参数控制）

### 运行中代理保护机制

那些在代理正在处理任务时绝不能执行的命令会被提前拒绝：

```python
if _quick_key in self._running_agents:
    if canonical == "model":
        return "⏳ Agent is running — wait for it to finish or /stop first."
```

跳过命令（`/stop`、`/new`、`/approve`、`/deny`、`/queue`、`/status`）会经过特殊处理。

## 配置来源

网关从多个来源读取配置：

| 来源 | 提供的内容 |
|------|------------|
| `~/.hermes/.env` | API密钥、机器人令牌以及平台凭证 |
| `~/.hermes/config.yaml` | 模型设置、工具配置以及显示选项 |
| 环境变量 | 可用于覆盖上述任意配置 |

与CLI（使用带有硬编码默认值的`load_cli_config()`函数）不同，网关会通过YAML加载器直接读取`config.yaml`文件。因此，那些存在于CLI默认值字典中但未出现在用户配置文件中的配置项，在CLI和网关中的行为可能会有所差异。

## 平台适配器

大多数消息平台以插件适配器的形式存在，位于`plugins/platforms/<name>/adapter.py`路径下；少数旧版适配器则直接存放在`gateway/platforms/`目录中。所有这些适配器都继承自`gateway/platforms/base.py`中的`BasePlatformAdapter`类：

```text
plugins/platforms/                  # plugin-packaged adapters (one dir each)
├── telegram/adapter.py     # Telegram Bot API (long polling or webhook)
├── discord/adapter.py      # Discord bot via discord.py
├── slack/adapter.py        # Slack Socket Mode
├── whatsapp/adapter.py     # WhatsApp Business Cloud API
├── matrix/adapter.py       # Matrix via mautrix (optional E2EE)
├── mattermost/adapter.py   # Mattermost WebSocket API
├── email/adapter.py        # Email via IMAP/SMTP
├── sms/adapter.py          # SMS via Twilio
├── dingtalk/adapter.py     # DingTalk WebSocket
├── feishu/adapter.py       # Feishu/Lark WebSocket or webhook
├── wecom/adapter.py        # WeCom (WeChat Work) callback
├── line/adapter.py         # LINE Messaging API
├── teams/adapter.py        # Microsoft Teams
├── irc/adapter.py          # IRC (canonical scoped-lock example)
├── homeassistant/adapter.py # Home Assistant conversation integration
└── …                       # google_chat, ntfy, photon, raft, simplex, …

gateway/platforms/                  # core base + legacy direct adapters
├── base.py              # BasePlatformAdapter — shared logic for all platforms
├── signal.py            # Signal via signal-cli REST API
├── weixin.py            # Weixin (personal WeChat) via iLink Bot API
├── bluebubbles.py       # Apple iMessage via BlueBubbles macOS server
├── qqbot/               # QQ Bot (Tencent QQ) via Official API v2 (sub-package)
├── yuanbao.py           # Yuanbao (Tencent) DM/group adapter
├── msgraph_webhook.py   # Microsoft Graph change-notification webhook (Teams, Outlook, etc.)
├── webhook.py           # Inbound/outbound webhook adapter
└── api_server.py        # REST API server adapter
```

实验性的连接器支持平台会使用 `gateway/relay/` 目录下的通用中继适配器，而非直接使用平台模块。当配置了 `GATEWAY_RELAY_URL` 或 `gateway.relay_url` 后，网关会注册该 `relay` 平台，通过出站 WebSocket 连接到连接器，并通过同一个套接字接收 `descriptor`、`inbound` 以及 `interrupt_inbound` 数据帧。连接器会发布 `CapabilityDescriptor`；Hermes 可以通过该中继发送常规的出站回复、无需令牌的 `follow_up` 操作以及中断数据帧。相关的接口定义文档位于 [`docs/relay-connector-contract.md`](https://github.com/NousResearch/hermes-agent/blob/main/docs/relay-connector-contract.md)。

各类适配器均需实现以下通用接口：
- `connect()` / `disconnect()` —— 生命周期管理
- `send_message()` —— 发送出站消息
- `on_message()` —— 对入站消息进行标准化处理，生成 `MessageEvent` 对象

### 令牌锁定机制

使用唯一凭证进行连接的适配器需在 `connect()` 方法中调用 `acquire_scoped_lock()`，并在 `disconnect()` 方法中调用 `release_scoped_lock()`。此机制可防止两个不同的配置文件同时使用同一个机器人令牌。

## 消息传递路径

出站消息传递功能（位于 `gateway/delivery.py`）负责处理以下场景：
- **直接回复** —— 将响应发送回原始聊天窗口
- **主频道发送** —— 将定时任务输出及后台处理结果发送到已配置的主频道
- **指定目标发送** —— 使用 `send_message` 工具并指定目标地址，如 `telegram:-1001234567890`；或者为 Shell 脚本编写封装该工具的 [`hermes send` CLI`](/guides/pipe-script-output)
- **跨平台发送** —— 将消息发送到与原始消息不同的平台

定时任务生成的消息不会被记录在网关的会话历史中，仅存在于相应的定时任务会话中。这是出于刻意的设计考量，旨在避免出现消息顺序混乱的问题。

## 钩子机制

网关钩子是用于响应各种生命周期事件的 Python 模块：

### 网关钩子事件

| 事件名称 | 触发时机 |
|---------|----------|
| `gateway:startup` | 网关进程启动时 |
| `session:start` | 新的对话会话开始时 |
| `session:end` | 会话结束或超时时 |
| `session:reset` | 用户通过 `/new` 命令重置会话时 |
| `agent:start` | 智能体开始处理消息时 |
| `agent:step` | 智能体完成一次工具调用后 |
| `agent:end` | 智能体处理完毕并返回响应时 |
| `command:*` | 任何斜杠命令被执行时 |

钩子模块可从 `gateway/builtin_hooks/`（一个扩展点——当前发布的版本中该目录为空；`_register_builtin_hooks()` 仅为空操作占位函数）以及用户自定义的 `~/.hermes/hooks/` 目录中找到。每个钩子都包含一个包含 `HOOK.yaml` 配置文件和 `handler.py` 处理程序的目录结构。

## 内存提供器集成

当启用了内存提供器插件（例如 Honcho）后，系统会按以下流程工作：
1. 网关为每条消息创建一个包含会话 ID 的 `AIAgent` 对象
2. `MemoryManager` 会使用会话上下文来初始化对应的内存提供器
3. 提供器的各类工具（如 `honcho_profile`、`viking_search`）将通过该内存提供器进行调用处理

```text
AIAgent._invoke_tool()
  → self._memory_manager.handle_tool_call(name, args)
    → provider.handle_tool_call(name, args)
```

4. 在会话结束/重置时，`on_session_end()` 会被触发，用于执行清理操作并完成最终数据刷新。

### 内存刷新生命周期

当会话被重置、恢复或过期时：
1. 内置内存会被刷新到磁盘上
2. 内存提供方的 `on_session_end()` 回调函数会被触发
3. 一个临时的 `AIAgent` 会执行仅基于内存的对话轮次
4. 随后，相关上下文会被丢弃或归档

## 后台维护

网关在处理消息的同时还会定期进行维护工作：

- **定时任务调度**——检查任务计划并触发到期的任务
- **会话过期处理**——在超时后清理被废弃的会话
- **内存主动刷新**——在会话过期前主动刷新内存
- **缓存更新**——更新模型列表及提供方状态信息

## 进程管理

网关作为长期运行的进程进行管理，可通过以下方式控制：
- `hermes gateway start` / `hermes gateway stop`——手动控制
- `systemctl`（Linux）或 `launchctl`（macOS）——服务管理
- 位于 `~/.hermes/gateway.pid` 的 PID 文件——基于配置文件的进程跟踪

**配置文件级与全局级**：`start_gateway()` 使用配置文件级的 PID 文件。`hermes gateway stop` 仅会停止当前配置文件对应的网关。而 `hermes gateway stop --all` 则会通过全局的 `ps aux` 查询来终止所有网关进程（通常在更新期间使用）。

## 相关文档

- [会话存储](./session-storage.md)
- [Cron 内部机制](./cron-internals.md)
- [ACP 内部机制](./acp-internals.md)
- [Agent 循环内部机制](./agent-loop.md)
- [消息网关（用户指南）](/user-guide/messaging)
