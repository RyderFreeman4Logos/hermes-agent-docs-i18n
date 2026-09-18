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
| `gateway/run.py` | `GatewayRunner` 接口层——整合了 `gateway/run_*.py` 系列混合模块（包括启动、适配器、接收消息、轮询、忙碌状态处理、目标设置、通知发送、关闭等功能）以及 `gateway/slash_commands_*.py` 中的命令处理程序 |
| `gateway/session.py` | `SessionStore`——用于对话内容的持久化存储及会话键的生成 |
| `gateway/delivery.py` | 负责将消息发送到目标平台或频道 |
| `gateway/pairing.py` | 处理用户授权所需的私信配对流程 |
| `gateway/channel_directory.py` | 将聊天 ID 映射为易于识别的名称，以便定时任务发送消息 |
| `gateway/hooks.py` | 负责钩子的发现、加载以及生命周期事件的派发 |
| `gateway/mirror.py` | 实现跨会话的消息同步功能，用于 `send_message` 操作 |
| `gateway/status.py` | 管理针对特定用户配置的网关实例的令牌锁定机制 |
| `gateway/builtin_hooks/` | 用于注册常驻钩子的扩展点（目前暂无相关实现） |
| `gateway/platform_registry.py` | 包含适配器注册表、工厂函数，以及针对内置平台插件的延迟加载机制 |
| `plugins/platforms/<name>/` | 内置的消息传输适配器（大多数平台包含 `adapter.py` 和 `plugin.yaml` 文件） |
| `gateway/platforms/` | 共用的 `base.py` 文件，以及旧版或直接的适配器（如 Signal、API 服务器、Webhook 等） |

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

## 消息流程

当有消息从任意平台传来时：

1. **平台适配器**接收原始事件，并将其标准化为 `MessageEvent` 对象；
2. **基础适配器**会检查当前会话状态：
   - 若该会话的智能体正在运行 → 将消息放入队列并设置中断事件；
   - 若为 `/approve`、`/deny`、`/stop` 类型的指令 → 直接跳过状态检查并立即处理；
3. **GatewayRunner._handle_message()** 方法接收该事件后，会执行以下操作：
   - 通过 `_session_key_for_source()` 方法解析会话键（格式为 `agent:main:{platform}:{chat_type}:{chat_id}`）；
   - 检查授权状态（详见下文“授权机制”）；
   - 若为斜杠命令 → 将其转发给命令处理模块；
   - 若智能体已在运行 → 拦截如 `/stop`、`/status` 等命令；
   - 否则 → 创建 `AIAgent` 实例并开始对话处理；
4. 最终的**响应**会通过平台适配器传回。

### 会话键格式

会话键用于编码完整的路由上下文信息：

```
agent:main:{platform}:{chat_type}:{chat_id}
```

例如：`agent:main:telegram:private:123456789`

支持线程功能的平台（如 Telegram 论坛主题、Discord 线程、Slack 线程）可能会在 chat_id 部分包含线程 ID。**切勿手动生成会话密钥**——应始终使用 `gateway/session.py` 中的 `build_session_key()` 函数来生成。

### 两级消息过滤机制

当智能体正在运行时，传入的消息需依次通过两级过滤机制：

1. **第一级——基础适配器**（`gateway/platforms/base.py`）：该模块会检查 `_active_sessions` 的状态。如果会话处于活跃状态，它会将消息放入 `_pending_messages` 队列中，并设置中断事件。这样就能在消息到达网关运行器之前将其拦截。

2. **第二级——网关运行器**（`gateway/run_inbound.py`）：该模块会检查 `_running_agents` 的状态。它能够拦截特定的命令（如 `/stop`、`/new`、`/queue`、`/status`、`/approve`、`/deny`），并对其进行相应处理。其他所有消息则会触发 `running_agent.interrupt()` 函数。

对于那些必须在智能体被阻塞时仍需送达运行器的命令（例如 `/approve`），会通过 `await self._message_handler(event)` 以**直接方式**进行处理——这样做可以绕过后台任务系统，从而避免竞态条件。

## 权限验证

网关采用多层权限验证机制，这些验证会按顺序依次执行：

1. **平台级全允许标志**（例如 `TELEGRAM_ALLOW_ALL_USERS`）——若启用，该平台上的所有用户都将获得授权。  
2. **平台白名单**（例如 `TELEGRAM_ALLOWED_USERS`）——以逗号分隔的用户 ID 列表。  
3. **私信配对功能**——已验证身份的用户可通过配对码为新用户进行授权。  
4. **全局全允许设置**（`GATEWAY_ALLOW_ALL_USERS`）——若启用，所有平台上的所有用户都将获得授权。  
5. **默认策略：拒绝访问**——未获授权的用户将被拒绝接入。  

### 私信配对流程

```text
Admin: /pair
Gateway: "Pairing code: ABC123. Share with the user."
New user: ABC123
Gateway: "Paired! You're now authorized."
```

配对状态会保存在 `gateway/pairing.py` 中，因此可在重启后依然保留。

## 斜杠命令分发

网关中的所有斜杠命令都会经过相同的解析流程：

1. `hermes_cli/commands.py` 中的 `resolve_command()` 函数会将输入映射为标准名称（同时支持别名和前缀匹配）；
2. 该标准名称会与 `GATEWAY_KNOWN_COMMANDS` 列表进行比对；
3. `gateway/run_inbound.py` 中的 `_handle_message()` 函数会通过 `_command_handler_table`，根据标准名称在 `gateway/slash_commands_*.py` 文件中的 `_handle_<name>_command` 处理函数中进行查找；这一过程会遍历 `gateway/run_busy.py` 中定义的 `_IDLE_COMMANDS` 和 `_PLAIN_COMMANDS` 列表，而不会使用类似 `if canonical == ...` 的条件判断；
4. 部分命令的可用性受配置控制（通过 `CommandDef` 中的 `gateway_config_gate` 参数设定）。

### 运行中的代理保护机制

那些在代理正在处理任务时绝不能执行的命令会立即被拒绝：

当 `_quick_key in self._running_agents` 为真时，`gateway/run_busy.py` 中的 `_dispatch_busy_slash_command()` 函数会根据每个已识别命令的 `CommandDef.busy_policy` 和 `busy_handler` 来决定处理方式：如果存在针对运行中任务的专用处理函数（格式为 `_busy_<key>_command`），则使用该函数；若 `busy_policy` 允许，则使用常规处理函数；否则会返回拒绝消息（“⏳ 代理正在运行——当前无法在任务进行中执行 `/model` 命令……”）。

那些可以绕过此限制的命令（如 `/stop`、/new`、/approve`、/deny`、/queue`、/status`）拥有专门的处理函数，可直接被调度执行。

## 配置来源

网关会从多个来源读取配置信息：

| 来源文件 | 提供的内容 |
|--------|------------|
| `~/.hermes/.env` | API密钥、机器人令牌以及平台凭证 |
| `~/.hermes/config.yaml` | 模型设置、工具配置以及显示选项 |
| 环境变量 | 可用于覆盖上述任意配置 |

与使用硬编码默认值的 `load_cli_config()` 函数的命令行界面不同，网关会通过 YAML 加载器直接读取 `config.yaml` 文件。因此，那些存在于命令行界面默认值字典中但未出现在用户配置文件中的配置项，在命令行界面和网关中的行为可能会有所差异。

## 平台适配器

大多数消息平台都以插件适配器的形式存在于 `plugins/platforms/<名称>/adapter.py` 文件中；仍有少数旧版适配器直接位于 `gateway/platforms/` 目录下。所有这些适配器都继承自 `gateway/platforms/base.py` 中的 `BasePlatformAdapter` 类：

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

**延迟加载：** 打包为 `kind: platform` 类型的插件会在 `gateway/platform_registry.py`（通过 `hermes_cli/plugins.py`）中注册成本较低的 `register_deferred` 加载器，这样平台 SDK 仅会在网关启动、处理消息或执行设置/状态相关操作时才被导入，而不会在普通的 `hermes chat` 会话中加载。查询时会仅加载一个适配器；只有在需要使用所有平台的路径上，才会加载所有待处理的加载器。

基于实验性连接器实现的平台会使用 `gateway/relay/` 目录下的通用中继适配器，而非直接使用对应的平台模块。当配置了 `GATEWAY_RELAY_URL` 或 `gateway.relay_url` 后，网关会注册 `relay` 平台，通过出站 WebSocket 连接到连接器，并通过同一个套接字接收 `descriptor`、`inbound` 以及 `interrupt_inbound` 数据帧。连接器会发布 `CapabilityDescriptor`；Hermes 可以通过该中继发送常规的出站回复、无需令牌的 `follow_up` 操作以及中断数据帧。相关的接口规范文档可见 [`docs/relay-connector-contract.md`](https://github.com/NousResearch/hermes-agent/blob/main/docs/relay-connector-contract.md)。

各类适配器均需实现以下通用接口：
- `connect()` / `disconnect()` —— 用于管理生命周期
- `send()` —— 用于发送出站消息
- 入站事件会被标准化为 `MessageEvent`，并通过 `handle_message()` 方法进行转发
内部推送唤醒会使用 `gateway.wake.admit_internal_event`：公共的 `handle_message()` 函数仍会返回 `None`，而该事件的进程级 `_gateway_accepted` 状态仅在任务被调度或放入队列后才会被设置。缺少处理程序、显式会话密钥不匹配或队列容量耗尽均不属于成功接受的情况。那些覆盖接入逻辑的自定义适配器应将对内部事件的处理委托给 `BasePlatformAdapter.handle_message()`（或显式记录实际的接受状态），而不得将已被处理/丢弃的回调等同于成功接受。此状态与心跳检测机制无关，也不会绕过授权检查、紧急停止机制以及后续的启动前置条件。

### 令牌锁定

使用唯一凭证连接的适配器需在 `connect()` 方法中调用 `acquire_scoped_lock()`，并在 `disconnect()` 方法中调用 `release_scoped_lock()`。这样做可防止两个配置文件同时使用同一个机器人令牌。

当发生锁冲突时，系统会生成包含 `retryable=True` 属性的 `{scope}_lock` 错误信息，这样在**运行过程中**重新连接后，待原持有者退出后即可恢复正常。不过在**启动阶段**，如果有其他实例正在使用该令牌，则属于配置冲突：`gateway/restart.py::is_global_startup_conflict()` 函数能够识别出 `*_lock` 和 `lock_conflict` 类型的错误信息，此时启动路由器会直接终止平台运行，而不会将其放入重试队列。若没有其他实例连接，网关则会以状态码 `78`（`EX_CONFIG`，`gateway_state=startup_failed`）退出，进而促使监控进程停止尝试重新启动它；而在真正出现短暂性的对端故障时，网关仍会保持运行状态，仅由出问题的对端进行重试。

## 消息投递路径

出站消息投递功能（位于 `gateway/delivery.py`）支持以下方式：

- **直接回复**——将响应直接发送回原始聊天窗口  
- **主频道投递**——将定时任务输出及后台处理结果转发至已配置的主频道  
- **指定目标投递**——通过发送引擎指定目标地址，例如 `telegram:-1001234567890`；该功能可通过 [`hermes send` CLI](/guides/pipe-script-output) 为 Shell 脚本提供支持，也可通过 cron 的 `deliver:` 参数实现  
- **跨平台投递**——将消息发送至与原始消息不同的平台  

定时任务生成的消息不会被记录在网关会话历史中，仅存在于对应的定时任务会话中。这是出于避免消息顺序混乱而刻意设计的。

## 钩子功能

网关钩子是用于响应各种生命周期事件的 Python 模块：

### 网关钩子事件

| 事件 | 触发时机 |
|------|----------|
| `gateway:startup` | 网关进程启动时 |
| `session:start` | 新对话会话开始时 |
| `session:end` | 会话结束或超时时 |
| `session:reset` | 用户通过 `/new` 命令重置会话时 |
| `agent:start` | 智能体开始处理消息时 |
| `agent:step` | 智能体完成一次工具调用后 |
| `agent:end` | 智能体处理完毕并返回响应时 |
| `command:*` | 任何斜杠命令被执行时 |
钩子可从 `gateway/builtin_hooks/`（一个扩展点——在当前发布的版本中该目录为空；`_register_builtin_hooks()` 仅为空操作占位函数）以及用户安装的 `~/.hermes/hooks/` 中被发现。每个钩子都包含一个包含 `HOOK.yaml` 配置文件和 `handler.py` 文件的目录。

## 内存提供程序集成

当启用了内存提供程序插件（例如 Honcho）时：

1. Gateway 会为每条消息根据会话 ID 创建一个 `AIAgent` 实例；
2. `MemoryManager` 会利用会话上下文来初始化该提供程序；
3. 提供程序相关的工具（如 `honcho_profile`、`viking_search`）将通过相应路径被调用。

```text
AIAgent._invoke_tool()
  → self._memory_manager.handle_tool_call(name, args)
    → provider.handle_tool_call(name, args)
```

4. 会话结束/重置时，`on_session_end()` 会被触发，用于执行清理操作并完成最终数据刷新。

### 内存刷新生命周期

明确的对话边界（如 `/new`、`/reset` 或 `/resume`）会触发会话的刷新与关闭操作；而空闲时间或每日时间阈值则不会导致会话关闭。

仅基于资源限制的 TTL、LRU 算法以及内存压力驱逐机制，会在释放代理的客户端之前，将缓存的对话记录提交到已配置的内存存储模块中。此操作并不会关闭该持久对话：下一个对话轮次会重新加载相同的对话记录和身份信息。

## 后台维护

网关在处理消息的同时还会定期执行维护任务：

- **定时任务触发**——检查任务调度表并启动到期的任务  
- **会话清理**——回收缓存资源，但不会结束对话记录  
- **内存刷新**——在软缓存数据被驱逐之前，先将数据写入内存  
- **缓存更新**——刷新模型列表及存储提供方的状态信息  

## 进程管理

网关作为长期运行的进程进行管理，可通过以下方式控制：

- `hermes gateway start` / `hermes gateway stop`——手动控制  
- `systemctl`（Linux）或 `launchctl`（macOS）——服务管理  
- 位于 `~/.hermes/gateway.pid` 的 PID 文件——基于配置文件的进程跟踪  

**配置文件级与全局级**：`start_gateway()` 使用配置文件级的 PID 文件；`hermes gateway stop` 仅会停止当前配置文件对应的网关进程；而 `hermes gateway stop --all` 则会通过全局的 `ps aux` 命令查找并终止所有网关进程（通常在更新过程中使用）。

## 相关文档

- [会话存储](./session-storage.md)  
- [Cron 内部机制](./cron-internals.md)  
- [ACP 内部机制](./acp-internals.md)  
- [Agent 循环内部机制](./agent-loop.md)  
- [消息网关（用户指南）](/user-guide/messaging)
