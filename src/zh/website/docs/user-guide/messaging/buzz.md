# Buzz

Buzz适配器可将Hermes与[Buzz](https://github.com/block/buzz)社区相连——这是Block基于Nostr协议开发的开源人机协作平台——并负责在Buzz频道（或私信）与智能体之间传递消息。向外发送的消息会通过`buzz` CLI二进制文件处理（“输入为JSON，输出也为JSON”）；而接收消息则采用原生的Nostr WebSocket订阅方式（通过已内置的`websockets`包实现），同时以CLI轮询作为备用方案。**无需额外安装任何Python包**，仅需`buzz`二进制文件即可。

Buzz支持渲染Markdown格式，因此智能体的回复能够保持原有的排版样式。图片既可以以上传文件（本地文件）的形式发送，也可以通过链接（URL）传输。回复可以通过目标消息的事件ID与其关联。若启用了进度或状态更新功能，这些消息会以触发它们的Buzz事件作为回复的锚点，而不会作为无关的顶层频道帖子出现。

发送**给**智能体的文件会通过中继服务器，使用智能体的认证身份取回并缓存到本地，这样相关工具就能获得真实的文件路径，而非匿名请求无法访问的 `/media/…` 格式的URL。该适配器可处理图片、音频、视频以及文档（如PDF等）等各类文件。

默认情况下，入站消息会通过经过 NIP-42 认证的持久 Nostr WebSocket 订阅通道送达（几乎可实现即时传输）；若无法建立 WebSocket 连接，则会自动回退至 CLI 轮询方式。出站消息始终需通过 `buzz` CLI 发送。您可以使用 `transport` / `BUZZ_TRANSPORT` 参数来控制传输方式：`auto`（默认值）、`websocket`（必须使用 WS，否则失败）或 `poll`。如果您的中继节点使用了 NIP-OA 持有者认证机制，则需将 `BUZZ_AUTH_TAG` 设置为对应的四字符串认证标签 JSON。

> 运行 `hermes gateway setup` 并选择 **Buzz** 选项，即可获得逐步指导。

## 先决条件

- `PATH` 环境变量中已包含 `buzz` CLI 可执行文件（或手动设置 `BUZZ_CLI_PATH` 指向该文件）——可通过 [Buzz 仓库](https://github.com/block/buzz) 使用 `cargo build --release -p buzz-cli` 命令进行构建
- 一个 Buzz 社区中继节点地址（例如 `https://mycommunity.communities.buzz.xyz`）
- 一个 Nostr 私钥（nsec 或十六进制格式），且该私钥对应的身份已为该社区的**成员**

## 配置 Hermes

您可以通过两种方式配置 Buzz：在 `config.yaml` 文件中的 `gateway` 块进行配置（推荐方式），或通过环境变量配置（环境变量会覆盖文件中的设置）。私钥属于**敏感信息**，必须存储在 `~/.hermes/.env` 文件中。

### 方案 A — config.yaml 配置

```yaml
gateway:
  platforms:
    buzz:
      enabled: true
      extra:
        relay_url: https://mycommunity.communities.buzz.xyz
        attachment_hosts: []         # additional exact HTTPS host[:port] origins for inbound files
        channels:                  # channel UUIDs to watch (empty = all joined)
          - ccc2bc1a-7a82-5a8f-8c4e-57a070cbe7cd
        home_channel: ccc2bc1a-7a82-5a8f-8c4e-57a070cbe7cd
        poll_interval: 4           # seconds between inbound poll sweeps
        cli_path: ""               # buzz binary (default: PATH, then ~/bin/buzz)
        credentials_file: ""       # JSON file with the nsec (BUZZ_PRIVATE_KEY fallback)
        allowed_users: []          # empty = allow all; hex pubkeys or npubs
```

此外，在 `~/.hermes/.env` 文件中：

```
BUZZ_PRIVATE_KEY=nsec1...
```

### 方案 B — 环境变量

| 变量 | 是否必填 | 描述 |
|------:|--------:|-------------|
| `BUZZ_RELAY_URL` | ✅ | 社区中继的基准 URL |
| `BUZZ_PRIVATE_KEY` | ✅ | Nostr 私钥（nsec 或十六进制格式）——唯一的机密信息 |
| `BUZZ_CHANNELS` | — | 需要监控的频道 UUID，以逗号分隔（默认：所有已加入的频道） |
| `BUZZ_HOME_CHANNEL` | — | 用于定时任务/通知发送的频道 UUID（默认为第一个被监控的频道） |
| `BUZZ_ALLOWED_USERS` | — | 允许与代理通信的 npubs 或十六进制公钥，以逗号分隔 |
| `BUZZ_ALLOW_ALL_USERS` | — | 允许任何社区成员与代理通信 |
| `BUZZ_POLL_INTERVAL` | — | 接收消息轮询之间的间隔时间（秒，默认：4） |
| `BUZZ_CLI_PATH` | — | `buzz` 可执行文件的路径（默认：PATH 中的 `buzz`，其次为 `~/bin/buzz`） |
| `BUZZ_CREDENTIALS_FILE` | — | 包含 nsec 格式私钥的 JSON 凭证文件，当未设置 `BUZZ_PRIVATE_KEY` 时使用 |

## 推荐的默认设置

在配置 Buzz 时，建议在 `config.yaml` 中设置这些默认值，这样可以保持频道信息的整洁，同时让代理专注于最终结果，而非内部工具的执行日志。这些设置与 Telegram 和邮件平台的处理方式一致，后者也会隐藏中间工具的输出内容。

```yaml
display:
  platforms:
    buzz:
      interim_assistant_messages: false   # suppress intermediate tool results, reasoning comments, and progress updates — only the final response reaches the channel
      tool_progress: off                  # suppress tool progress bubbles (e.g., "Running terminal command...", "Reading file...")
gateway:
  platforms:
    buzz:
      enabled: true
      extra:
        relay_url: https://mycommunity.communities.buzz.xyz
        attachment_hosts: []         # additional exact HTTPS host[:port] origins for inbound files
        channels:                         # channel UUIDs to watch (empty = all joined)
          - ccc2bc1a-7a82-5a8f-8c4e-57a070cbe7cd
        home_channel: ccc2bc1a-7a82-5a8f-8c4e-57a070cbe7cd
        poll_interval: 4                  # seconds between inbound poll sweeps (default 4 — balances latency vs. relay load)
        cli_path: ""                      # buzz binary (default: PATH, then ~/bin/buzz)
        credentials_file: ""              # JSON file with the nsec (BUZZ_PRIVATE_KEY fallback)
        allowed_users: []                 # empty = allow all if allow_all_users is true; otherwise restrict to listed npubs/hex pubkeys
        require_mention: true             # in channels: only respond when addressed (@name, npub, or hex pubkey); DMs always dispatch regardless
        allow_all_users: false            # set true for community mode (everyone can chat, only owner is admin); false for private mode (only allowed_users)
```

**为何采用这些默认设置：**

- `interim_assistant_messages: false` —— 防止将工具的中间处理结果、推理过程及进度更新以独立消息的形式发送到频道中。只有最终响应会被发送至频道。
- `tool_progress: off` —— 关闭工具进度提示（如“正在运行终端命令...”、“正在读取文件...”）。这样能确保频道内容聚焦于实际结果，而非处理流程。
- `poll_interval: 4` —— 在接收消息的延迟（最多4秒）与中继服务器负载之间取得平衡。数值越低，轮询频率越高；数值越高，轮询频率越低。
- `allowed_users: []` + `allow_all_users: false` —— 默认为私密模式，仅允许列出的用户进行交互。若需开启全员可聊的社区模式，请将 `allow_all_users: true` 设为 true，但管理员权限仍仅限于频道所有者。
- `require_mention: true` —— 在频道中，只有被提及时智能体才会响应。而私信则始终会触发响应，不受此设置影响。

**设计理念：** 频道用于展示最终结果和对话内容，而非智能体内部的工具执行日志。用户看到的应是最终答案，而非获取该答案的步骤。这一设定与 Telegram 和电子邮件平台的默认行为一致。

**例外情况：** 如果希望让用户查看工具处理进度（例如在处理耗时较长的操作时），可将 `tool_progress` 设为 `all` —— 但 `interim_assistant_messages` 仍应保持为 `false`，以避免因每次工具处理结果都会被发送而导致信息过载。

## 提及、频道与私信

- 在共享频道中，只有当有人**直接提及**该智能体时——通过 `@name`、其公钥或十六进制公钥——它才会做出回应，其他所有内容都会被忽略。
- 直接消息总会送达智能体，无需任何提及。
- 智能体自身的消息绝不会被发回给自身（通过公钥实现自回声抑制），并且每个事件都会根据频道内的历史记录通过事件ID进行去重处理。

## 回复的线程化机制

默认情况下，回复会以线程形式呈现：智能体的答复（以及任何已启用的进度/状态信息）都会绑定在触发它的消息上。此机制支持 NIP-10 标准——如果触发消息本身就已经处于某个线程中，智能体就会回复到该线程的*根节点*，从而使答复加入现有线程，而不会在每次回应时都创建一个新的单消息子线程。

如需在频道层面以扁平形式发布回复，可设置以下任意一个选项（二者功能相同；`reply_in_thread` 与 Slack 使用的键名一致）：

```yaml
gateway:
  platforms:
    buzz:
      reply_to_mode: off          # PlatformConfig-level, like Discord/Telegram
      extra:
        reply_in_thread: false    # Slack-style key; env: BUZZ_REPLY_IN_THREAD
```

此拒绝机制适用于**所有**消息发送路径——包括最终答案、流式更新、中间评论、工具进度提示，以及进程外定时任务推送（`deliver=buzz`）。

## 访问控制

默认情况下，允许列表为空，这意味着只有当 `BUZZ_ALLOW_ALL_USERS=true` 时，任何提及该智能体的社区成员才能收到回复；否则需通过在 `BUZZ_ALLOWED_USERS`（或 config.yaml 中的 `allowed_users`）中列出特定公钥来限制访问权限。社区成员身份由中继节点负责验证——仅有成员才能发布内容。

允许列表还用于控制**传入附件**：中继节点会使用智能体自身的 Buzz 凭据获取媒体文件，因此只有经过网关明确授权的发送者才能实现下载。若授权被拒绝、缺失或失败，消息文本将保持不变，且不会发起任何带凭据的请求。

定时任务及通知（`deliver=buzz`）会被发送到**主频道**——若设置了 `BUZZ_HOME_CHANNEL` 则发送至该频道，否则发送至第一个被关注的频道——即便定时任务在网关进程之外运行，也能正常工作。

## 传入附件

带有原生 NIP-94 `imeta` 标签的 Buzz 消息可以将图片、音频、视频和文档传递给智能体。Hermes 仅在消息通过自回显、地址验证及发送者授权检查后才会下载附件。每个文件都必须使用 HTTPS 协议，并需明确标注字节大小与 SHA-256 哈希值；重定向、URL 凭据、片段化数据、过大的数据包以及完整性不匹配的情况均会被拒绝。

中继服务器自身的 HTTPS 来源地址会自动被信任。如果某个社区将媒体文件存储在其他的公共地址上，则需将其确切的 `host` 或 `host:port` 地址添加到 `gateway.platforms.buzz.extra` 下的 `attachment_hosts` 中。非默认端口必须明确列出。对于那些需要通过 Buzz CLI 进行身份验证才能获取的受保护媒体文件，此基于公共 URL 的路径无法处理。

## 启动网关

```bash
hermes gateway start
```

可使用 `hermes gateway status` 命令查看状态——该命令会显示 Buzz 连接状态，包括仅使用环境配置的场景。

## 注意事项与限制

- **对于 Buzz 会话，终端工具的子进程可访问 `BUZZ_*` 环境变量**——由于当会话平台为 Buzz 或进程为 Buzz Desktop 管理的代理（`BUZZ_MANAGED_AGENT`）时，`BUZZ_PRIVATE_KEY`、`BUZZ_AUTH_TAG`、`BUZZ_RELAY_URL` 以及其他 `BUZZ_*` 变量会被传递给终端子进程，因此代理可直接调用 `buzz` CLI（例如 `buzz messages send ...`）。而同一主机上的非 Buzz 会话、`execute_code` 命令以及其他非终端生成的进程则无法访问这些变量。
- **消息接收为轮询模式，而非流式传输**。由于 `buzz` CLI 采用请求/响应机制，适配器会每隔 `poll_interval` 秒（默认为 4 秒）对每个关注的频道执行一次 `buzz messages get` 查询。因此，接收到的消息可能存在最多一个间隔的延迟。未来的优化方向是采用 WebSocket 传输方式（Buzz 项目已提供 `buzz-ws-client` 以实现真正的流式传输）。
- 在重新连接时，适配器会以最新事件作为基准来设置数据读取上限，从而避免向代理重复发送历史消息。
- 新的私信对话会自动被检测到（每隔几次轮询即可发现）。
- 私钥是通过子进程环境传递给 CLI 的——它不会出现在命令行参数或日志中。
