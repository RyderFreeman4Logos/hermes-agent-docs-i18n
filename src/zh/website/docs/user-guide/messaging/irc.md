# IRC

IRC适配器可将Hermes与任意IRC服务器相连，从而在IRC频道（或私信）与智能体之间传递消息。它通过Python标准库中的`asyncio`实现IRC协议通信——**无需任何外部依赖、无需SDK，也不需要后台进程**。该适配器既支持像[Libera.Chat](https://libera.chat/)这样的公共网络，也适用于任何自托管的ircd服务器。

IRC为纯文本格式：不支持语音、图片、文件、主题讨论、表情反应、输入状态显示或流媒体功能——回复以`PRIVMSG`指令行形式发送，较长的消息会自动拆分以符合IRC的行长度限制。

> 运行`hermes gateway setup`命令，选择**IRC**选项即可获得逐步指导。

## 先决条件

- 一个可连接的IRC服务器（例如`irc.libera.chat`）
- 一个要加入的频道（例如`#hermes`）——如需同时加入多个频道，请用逗号分隔
- 机器人的昵称（默认为`hermes-bot`）
- 可选：如果您的网络要求身份验证，则需要已注册的昵称及NickServ密码

## 配置Hermes

您可以通过两种方式配置IRC功能：通过环境变量进行快速设置，或通过`~/.hermes/gateway-config.yaml`文件中的`gateway`块进行配置。

### 方案A — gateway-config.yaml

```yaml
gateway:
  platforms:
    irc:
      enabled: true
      extra:
        server: irc.libera.chat
        port: 6697
        nickname: hermes-bot
        channel: "#hermes"
        use_tls: true
        server_password: ""       # optional server password
        nickserv_password: ""     # optional NickServ identification
        allowed_users: []         # empty = allow all, or list of nicks
        max_message_length: 450   # IRC line limit (safe default)
```

### 方案 B — 环境变量

| 变量 | 是否必填 | 说明 |
|------:|--------:|------|
| `IRC_SERVER` | ✅ | IRC 服务器主机名（例如：`irc.libera.chat`） |
| `IRC_CHANNEL` | ✅ | 需加入的频道——多个频道用逗号分隔 |
| `IRC_NICKNAME` | ✅ | 机器人昵称（默认值：`hermes-bot`） |
| `IRC_PORT` | — | 服务器端口（默认值：使用 TLS 时为 `6697`，不使用 TLS 时为 `6667`） |
| `IRC_USE_TLS` | — | 是否使用 TLS（`true`/`false`；在端口 `6697` 上默认为 `true`） |
| `IRC_SERVER_PASSWORD` | — | 用于 `PASS` 命令的服务器密码 |
| `IRC_NICKSERV_PASSWORD` | — | 连接时自动进行 IDENTIFY 操作所需的 NickServ 密码 |
| `IRC_ALLOWED_USERS` | — | 允许与机器人交流的昵称，以逗号分隔 |
| `IRC_ALLOW_ALL_USERS` | — | 允许频道中的任何用户与机器人交流（仅开发者使用） |
| `IRC_HOME_CHANNEL` | — | 用于发送定时任务及通知的频道（默认值为 `IRC_CHANNEL`） |

## 访问控制

默认情况下，只有列在 `allowed_users`（或 `IRC_ALLOWED_USERS`）中的昵称才能与机器人交流。若将列表留空并同时设置 `IRC_ALLOW_ALL_USERS=true`，则允许频道中的任何用户与 Hermes 进行聊天——这便于测试，但由于除非网络启用了 NickServ，否则 IRC 昵称并未经过身份验证，因此不推荐在公共网络中使用此设置。

如果您的网络会对昵称进行注册，请设置 `IRC_NICKSERV_PASSWORD`（或 `nickserv_password`），以便机器人在连接时向 NickServ 进行身份认证，并保留其已注册的昵称。

## 频道交流与私信交流

- 在已加入的频道中发送的消息被视为**群组**对话。
- 发送给机器人的私人消息则视为**直接消息**。

定时任务和通知将会发送到**默认频道**——即 `IRC_HOME_CHANNEL`（若已设置），否则为第一个 `IRC_CHANNEL`。

## 运行网关

```bash
hermes gateway start
```

可通过 `hermes gateway status` 命令查看状态——该命令会显示 IRC 连接状态，包括仅使用环境配置的场景。

## 备注

- 为避免超出 IRC 消息长度限制（扣除协议开销后的默认最大值为 450 字节），过长的代理回复会自动拆分为多条 `PRIVMSG` 消息。
- 该适配器会为每个服务器加昵称组合获取独立的身份凭证锁，因此不同的 Hermes 配置文件不会争夺同一个 IRC 账号。
