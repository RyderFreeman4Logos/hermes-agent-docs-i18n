# A2A — Hermes的代理间通信协议

通过开放的 **[A2A协议](https://a2a-protocol.org) v1.0**，实现与其他代理的交互，同时也能让其他代理与您进行沟通。该协议可与任何符合A2A标准的系统协同工作（如其他Hermes、LangChain、CrewAI、Google ADK、OpenClaw等）。仅需标准库支持，无需依赖`a2a-sdk`。

## 启用

```bash
hermes gateway setup      # pick A2A, or:
```

```yaml
# ~/.hermes/config.yaml
gateway:
  platforms:
    a2a:
      enabled: true
      extra:
        port: 9900

# peers you want to call (outbound):
a2a_agents:
  researcher:
    url: "http://localhost:9999"
    auth: { type: bearer, token: "sk-..." }
    timeout: 120
    capabilities: [web_search, research]
```

## 出站通信——调用其他智能体

该智能体可使用五种工具：

- `a2a_discover(url)` — 了解该智能体具备哪些功能；
- `a2a_call(agent, message, context_id?)` — 向目标智能体发送任务并获取回复；
- `a2a_list()` — 查看已配置的对接智能体、保存的对话记录以及相关指标；
- `a2a_history(context_id)` — 调用之前保存的智能体间对话记录；
- `a2a_orchestrate(capability, message, mode?)` — 将任务分发给所有声明具备相应功能的对接智能体（支持 `all`/`first`/`best` 模式）。

## 入站通信——被其他智能体调用

当启用了 `a2a` 平台后，Hermes 会在 `http://<host>:<port>/.well-known/agent-card.json` 地址提供 v1.0 版本的智能体卡片（针对低于 1.0 版本的客户端，也会返回旧版的 `/ .well-known/agent.json` 路径），并支持接收 JSON-RPC 格式的 `message/send`、`message/stream`（SSE 协议）、`tasks/get|list|cancel|subscribe` 请求，以及推送通知配置（可直接嵌入消息，或通过 `tasks/pushNotificationConfig/create` 接口设置）。传入的任务会被注入到您当前**正在运行的**智能体会话中——即那个正在与您交互的智能体，且保留其全部内存状态——随后回复会通过 A2A 机制返回。已完成的任务可通过 `tasks/get` 接口查询。

## 安全性

- **无令牌 ⇒ 仅限本地访问**。服务器会绑定 `127.0.0.1` 地址，除非您同时配置了令牌并设置了 `A2A_HOST`，否则不会允许连接扩展到其他地址。
- **逐对令牌**：通过设置 `A2A_PEER_TOKENS="alice:tok1,bob:tok2"` 可为每个远程代理分配独立的认证凭证；正是这些经过认证的名称（而非请求正文中的任何内容）用于控制速率限制、确定信任级别以及进行审计。
- 所有传入的文本——包括以 `/` 开头的文本——都会经过注入检测过滤器处理，并被视为不可信的对方输入；因此远程端无法调用以操作符 `/` 开头的命令。
- 发出的文本会经过过滤，移除任何类似凭证格式的字符串。
- 推送回调功能具有 SSRF 防护机制，并采用 HMAC-SHA256 签名（通过 `X-A2A-Signature` 标识）。
- 每次交互都会被记录到 `~/.hermes/a2a_audit.jsonl` 文件中。
- 对话内容会保存在 `~/.hermes/a2a_conversations/` 目录下，即便进行上下文压缩或重启操作也能保留（可通过 `a2a_history` 功能调出这些对话）。

## 环境变量

| 参数 | 默认值 | 含义 |
|---|---|---|
| `A2A_PEER_TOKENS` | 未设置 | 对等节点认证凭据，格式为 `name:token,…`（推荐使用）。 |
| `A2A_BEARER_TOKEN` | 未设置 | 共享令牌；此时身份验证将回退至调用方 IP。 |
| `A2A_HOST` | `127.0.0.1` | 绑定主机地址。仅在设置了令牌后才会生效。 |
| `A2A_PORT` | `9900` | 入站端口。 |
| `A2A_AGENT_NAME` | 由主机名生成 | Agent Card 上显示的名称。 |
| `A2A_PUBLIC_URL` | 未设置 | 在 Agent Card 上展示的可路由 URL（用于反向代理）。 |
| `A2A_TRUSTED_PEERS` | 未设置 | 已通过认证的身份地址白名单。 |
| `A2A_ALLOW_ALL_USERS` | `false` | 允许所有已认证的对等节点访问（仅开发环境适用）。 |
| `A2A_RATE_LIMIT` | `60` | 每个身份每分钟的请求次数上限。 |
| `A2A_MAX_PINGPONG_TURNS` | `5` | 每个上下文中的防循环轮次限制（最大值为 20）。 |
| `A2A_REPLY_TIMEOUT` | `300` | 等待代理回复的时间间隔（秒）。 |
| `A2A_PUSH_SECRET` | 承载令牌 | 用于签名推送消息的 HMAC 密钥。 |
| `A2A_ADVERTISED_TOOLSETS` | 所有已注册的技能集 | 限制 Agent Card 上显示的技能范围。 |

有关架构设计及需求追踪表的内容，请参阅 `DESIGN.md` 文件。
