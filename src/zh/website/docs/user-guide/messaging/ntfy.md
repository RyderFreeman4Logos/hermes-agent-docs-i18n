# ntfy

[ntfy](https://ntfy.sh/) 是一款基于 HTTP 的简易发布/订阅通知服务。它既可以使用免费的公共服务器 `ntfy.sh`，也可以部署自托管实例，同时支持任何能够发送 HTTP 请求的客户端——手机、浏览器、脚本以及智能手表等。

对于 Hermes 来说，ntfy 是一款出色的轻量级推送通道：您可以通过 [ntfy 移动应用](https://ntfy.sh/docs/subscribe/phone/) 订阅某个主题，向该主题发送消息与 Agent 进行交互，随后即可在手机上收到回复。

> 运行 `hermes gateway setup` 并选择 **ntfy**，即可获得逐步指导。

## 先决条件

- 一个主题名称（任意唯一字符串——`hermes-myname-2026` 即可）
- 已安装 [ntfy 移动应用](https://ntfy.sh/docs/subscribe/phone/) 并订阅了该主题
- 可选：自托管的 ntfy 服务器，或用于私有/专用主题的 `ntfy.sh` 账户令牌

仅此而已。无需 SDK、无需后台进程，也无需 Node.js。该适配器使用了已作为 Hermes 依赖项存在的 `httpx` 库。

## 配置 Hermes

### 通过设置向导完成

```bash
hermes gateway setup
```

选择 **ntfy**，然后按照提示操作。

### 通过环境变量设置

将这些内容添加到 `~/.hermes/.env` 文件中：

```
NTFY_TOPIC=hermes-myname-2026
NTFY_ALLOWED_USERS=hermes-myname-2026
NTFY_HOME_CHANNEL=hermes-myname-2026
```

| 参数 | 是否必填 | 说明 |
|---|---|---|
| `NTFY_TOPIC` | 是 | 需订阅的主题（用于接收消息） |
| `NTFY_SERVER_URL` | 否 | 服务器地址（默认值：`https://ntfy.sh`）——如需保障隐私，可指向自托管的 ntfy 服务 |
| `NTFY_TOKEN` | 否 | 承载令牌（例如 `tk_xyz`），或用于基本认证的 `user:pass` 格式 |
| `NTFY_PUBLISH_TOPIC` | 否 | 用于发送回复的不同主题（默认值为 `NTFY_TOPIC`） |
| `NTFY_MARKDOWN` | 否 | 设置为 `true` 可在回复中添加 `X-Markdown: true` 标头 |
| `NTFY_ALLOWED_USERS` | 建议使用 | 以逗号分隔的允许访问的主题名称（视为用户 ID；详见下文） |
| `NTFY_ALLOW_ALL_USERS` | 否 | 设置为 `true` 可允许所有发布者——仅适用于拥有读取权限的私有主题 |
| `NTFY_HOME_CHANNEL` | 否 | 用于定时任务/通知发送的默认主题 |
| `NTFY_HOME_CHANNEL_NAME` | 否 | 该默认主题的直观名称 |

## 身份模型——部署前请先了解

ntfy 并不具备原生身份认证功能。已发布消息中的 `title` 字段由**发布者自行控制**，发送方可以设置任意内容。Hermes 适配器不会使用 `title` 进行授权——否则任何知晓该主题的发布者都可能冒充被允许的用户。

实际上，**主题名称本身就代表了身份**。发布到该主题的每条消息都被视为来自同一个逻辑用户（即该主题）。因此，`NTFY_ALLOWED_USERS` 通常只需填写主题名称本身——即一个单条目的白名单，用于控制整个频道。

这意味着**任何知晓该主题的人都可以与该智能体交互**。若要建立真正的信任边界，可采取以下措施：

- **自托管 ntfy 服务**，并通过[访问控制](https://docs.ntfy.sh/config/#access-control)限制对该主题的访问。只有拥有读写权限的授权客户端才能发布消息。
- 或者在 [ntfy.sh 上创建私有主题](https://docs.ntfy.sh/publish/#reserved-topics)，此类主题需要账户才能使用，并通过 `NTFY_TOKEN` 进行保护。
- 或者**选择一个长度较长、难以猜测的主题名称**（如 `hermes-7d4f9c8b-2026`），并将其视为共享密钥。这种方式的设置最为简单，但主题名称可能会通过任何日志或截图泄露。

无论采用哪种方式，除非底层主题已设置访问控制，否则都不要通过 ntfy 传输敏感数据。

## 快速入门——用手机与智能体交互

1. 选择一个主题名称：`hermes-myname-2026`
2. 在手机上：安装 [ntfy 应用](https://ntfy.sh/docs/subscribe/phone/)，点击 **+**，输入 `hermes-myname-2026`
3. 在主机端：
   ```bash
   echo 'NTFY_TOPIC=hermes-myname-2026' >> ~/.hermes/.env
   echo 'NTFY_ALLOWED_USERS=hermes-myname-2026' >> ~/.hermes/.env
   hermes gateway restart
   ```
4. 通过 ntfy 应用向该主题发送消息，代理的回复会以推送通知的形式送达。

## 将 ntfy 与定时任务结合使用

设置好 `NTFY_HOME_CHANNEL` 后，即可通过定时任务将消息发送至 ntfy：

```python
cronjob(
    action="create",
    schedule="every 1h",
    deliver="ntfy",          # uses NTFY_HOME_CHANNEL
    prompt="Check for alerts and summarise."
)
```

或者直接指定某个特定主题：

```python
send_message(target="ntfy:alerts-channel", message="Done!")
```

即便 cron 任务是通过网关在进程外运行的，此功能依然有效——该插件会注册一个 `standalone_sender_fn`，从而自行建立 HTTP 连接。

## 自主托管 ntfy

如需完全掌控系统：

```bash
# Docker
docker run -p 80:80 -it binwiederhier/ntfy serve

# Native
go install heckel.io/ntfy/v2@latest
ntfy serve
```

接着将 Hermes 指向该目标：

```
NTFY_SERVER_URL=https://ntfy.mydomain.com
NTFY_TOPIC=hermes
NTFY_TOKEN=tk_abc123  # if you've set up access control
```

自托管模式可让您实现主题访问控制、消息持久化策略、附件支持以及表情符号标签功能。详情请参阅 [ntfy 服务器文档](https://docs.ntfy.sh/install/)。

## Markdown 格式

当发布者设置 `X-Markdown: true` 头部标识时，ntfy 客户端即可渲染 Markdown 内容。如需在 Hermes 的回复中启用该功能：

```
NTFY_MARKDOWN=true
```

或在 `config.yaml` 中：

```yaml
platforms:
  ntfy:
    extra:
      markdown: true
```

该移动应用支持 CommonMark 的部分格式——加粗、斜体、列表、链接以及代码块。具体支持的格式列表请参阅 [ntfy 的 Markdown 文档](https://docs.ntfy.sh/publish/#markdown-formatting)。

## 仅发送模式设置（仅推送通知，不接收消息）

如果您希望 Hermes 仅向 ntfy *推送* 通知（如定时汇总信息、警报等），而绝不接收任何回传消息，只需将 `NTFY_TOPIC` 和 `NTFY_PUBLISH_TOPIC` 设置为相同的值，并完全省略 `NTFY_ALLOWED_USERS` 参数。由于没有允许列表，该智能体不会响应任何入站消息——您的手机虽会收到推送通知，但通信过程为单向的。

## 限制事项

- **消息长度**：ntfy 将消息正文长度上限设定为 4096 个字符。一旦超过此限制，Hermes 会截断内容并发出警告。
- **无输入状态指示**：该协议不提供输入状态指示功能；`send_typing` 命令实际上不起任何作用。
- **不支持对话线程及附件**：ntfy 仅提供纯推送通知功能。较长的回复内容会保留在消息正文中，无法形成对话线程。
- **无原生用户身份标识**：详情请参见上文关于身份模型的说明。

## 故障排除

**认证失败 / 401 错误**——可能是 `NTFY_TOKEN` 错误，或者该令牌不具备针对该主题的发布/订阅权限。遇到 401 错误时，适配器会停止重连循环，网关运行状态将显示 `fatal: ntfy_unauthorized`。请修正令牌并重启网关。

**主题不存在 / 404 错误**——配置的服务器上不存在 `NTFY_TOPIC`。对于 ntfy.sh 平台，主题会在首次发布时自动创建，因此出现 404 错误通常意味着您配置的是自托管服务器，且该服务器上尚未创建对应主题。此时适配器会停止重连循环，并显示 `fatal: ntfy_topic_not_found`。

**已连接但无消息**——请检查 `NTFY_ALLOWED_USERS` 是否包含了该主题名称本身。根据 ntfy 的身份模型，主题本身即代表用户；若允许列表为空，则会拒绝所有消息。

**每 60 秒自动重连**——流式连接的保持活跃默认时间为 55 秒；ntfy 可能会出现间歇性网络问题。适配器会采用指数退避策略逐步延长重试间隔（2 → 5 → 10 → 30 → 60 秒），而一旦连接保持活跃时间达到或超过 60 秒，间隔将重置为 0。
