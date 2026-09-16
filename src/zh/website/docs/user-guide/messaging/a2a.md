# A2A（智能体间通信）

[A2A](https://a2a-protocol.org) 是由 Linux Foundation 主导开发的开放型 Agent2Agent 协议（版本 1.0），用于不同独立 AI 智能体之间的通信。Hermes 的 A2A 插件支持**双向交互**：您的智能体可以将其他 A2A 智能体作为工具调用，同时其他智能体也可以通过 HTTP 向您的 Hermes 发送任务。

该协议可与任何符合 A2A 标准的智能体协同工作——无论是其他 Hermes、LangChain、CrewAI、Google ADK 智能体，还是基于官方 `a2a-sdk` 开发的各类应用。

## 何时使用 A2A

- **跨机器的 Hermes ↔ Hermes 通信**——让桌面端的智能体将任务分配给服务器上的 Hermes，反之亦然，两者各自拥有独立的记忆、工具和认证信息。
- **委托给专业智能体处理**——可以在对话过程中发现并调用那些在智能体卡片上标明具备 `web_search`/`research`/`coding` 等技能的智能体。
- **作为可被调用的服务**——开放您的 Hermes，让其他框架的智能体能够向其发送任务。

如果需要在**同一台机器**上运行多个智能体，建议使用[委托机制](../features/delegation.md)（进程内子智能体）或[看板功能](../features/kanban.md）（持久化多配置工作队列）——A2A 则适用于跨越进程、机器或框架边界的情况。

## 启用功能

```bash
hermes gateway setup      # pick A2A
```

或者可在 `~/.hermes/config.yaml` 中配置：

```yaml
gateway:
  platforms:
    a2a:
      enabled: true
      extra:
        port: 9900
```

这些出站客户端工具以 `a2a` 工具集的形式提供，**默认处于关闭状态**——需根据具体平台进行启用：

```bash
hermes tools enable a2a --platform cli        # CLI/TUI sessions
hermes tools enable a2a --platform telegram   # or any messaging platform
hermes tools enable a2a --platform a2a        # let inbound A2A tasks call peers (agent chaining)
```

这些工具适用于所有流程类型——CLI、TUI、网关以及定时任务——且无需启用入站平台。

## 出站：调用其他智能体

一旦启用了 `a2a` 工具集，智能体即可使用以下功能：

| 工具 | 功能说明 |
|---|---|
| `a2a_discover(url)` | 获取并汇总对应智能体的 Agent Card 信息 |
| `a2a_call(agent, message, context_id?)` | 发送任务并获取回复；可通过 `context_id` 实现多轮对话 |
| `a2a_list()` | 查看已配置的对应智能体、保存的对话记录以及相关指标 |
| `a2a_history(context_id)` | 调用之前保存的 A2A 对话记录 |
| `a2a_orchestrate(capability, message, mode?)` | 将任务分发给所有声明具备相应能力的智能体（可选模式：`all`/`first`/`best`） |

可在 `config.yaml` 中配置已知的对应智能体：

```yaml
a2a_agents:
  researcher:
    url: "http://research-box.local:9900"
    auth: { type: bearer, token: "..." }
    timeout: 120
    capabilities: [web_search, research]
```

只需这样请求即可：“让研究助手代理总结今天的arXiv上新论文。”直接提供URL也是可行的——`a2a_call`支持任何A2A接口地址。

## 接入端：可被调用性

在平台启用后，Hermes会提供以下接口：

- 通过`GET /.well-known/agent-card.json`获取**代理卡片**（标准v1.0路径；旧的`agent.json`也能响应）——用于展示代理的名称、技能（来自已启用的工具集）以及认证要求。
- 通过`POST /`提供**JSON-RPC 2.0**接口——包含标准的v1.0方法（如`SendMessage`、`SendStreamingMessage`、`GetTask`、`ListTasks`、`CancelTask`、`SubscribeToTask`以及推送通知配置的创建、读取、更新和删除操作），同时还支持v1.0之前的路径风格别名（如`message/send`等）。
- 对于`SendStreamingMessage`，还提供符合规范的**SSE流式传输**，数据以JSON-RPC格式封装。
- 针对长时间运行的任务，还提供经过HMAC-SHA256签名的**推送通知**（即webhook）。

接入端的任务会被注入到**实时网关会话**中——使用与处理其他渠道相同的代理、内存和工具——最终回复会作为任务结果返回给调用方。对话通过A2A的`contextId`进行标识，因此双方可以进行多轮交互。

互操作性将通过官方Python `a2a-sdk`进行验证（包括卡片解析、`SendMessage`功能以及流式传输功能）。

## 安全模型

默认处于安全状态；任何扩展功能的使用都会明确说明。

- **无令牌 ⇒ 仅限本地访问。** 服务器会绑定到 `127.0.0.1` 地址。如需远程访问，则必须同时提供承载令牌以及明确的 `A2A_HOST` 设置。
- **逐对令牌** — 通过设置 `A2A_PEER_TOKENS="alice:tok1,bob:tok2"`，可为每对通信方分配独立的认证凭证；用于身份识别的名称将决定速率限制、信任度判定及审计逻辑。
- **提示注入过滤** — 进入的文本会被过滤处理，并被视为来自不可信对方的输入。远程对方无法调用操作员相关的命令。
- **输出内容屏蔽** — 回复信息中的 API 密钥、JWT 令牌等凭证类字符串会被自动移除。
- **审计日志** — 所有的通信记录都会被追加到 `~/.hermes/a2a_audit.jsonl` 文件中。
- **防循环机制** — 基于上下文的轮次限制可防止两个智能体无限循环交互。

## 配置参考

| 环境变量 | 默认值 | 含义 |
|---|---|---|
| `A2A_PEER_TOKENS` | 未设置 | 对等方凭证，格式为 `name:token,…`（推荐） |
| `A2A_BEARER_TOKEN` | 未设置 | 共享令牌；若未设置，则使用调用方 IP 作为身份标识 |
| `A2A_HOST` | `127.0.0.1` | 绑定主机地址——仅当设置了令牌时才会改变 |
| `A2A_PORT` | `9900` | 入站端口 |
| `A2A_AGENT_NAME` | 由主机名生成 | Agent Card 上显示的名称 |
| `A2A_PUBLIC_URL` | 未设置 | 在 Agent Card 上展示的可访问 URL（适用于反向代理/K8s 环境） |
| `A2A_TRUSTED_PEERS` | 未设置 | 已通过认证的身份标识白名单 |
| `A2A_ALLOW_ALL_USERS` | `false` | 允许所有已认证的对等方访问（仅开发环境适用） |
| `A2A_RATE_LIMIT` | `60` | 每个身份标识每分钟的请求数上限 |
| `A2A_MAX_PINGPONG_TURNS` | `5` | 每个上下文中的防循环轮次限制（最大为 20 次） |
| `A2A_REPLY_TIMEOUT` | `300` | 等待代理响应的秒数 |
| `A2A_PUSH_SECRET` | 承载令牌 | 用于签名推送通知的 HMAC 密钥 |
| `A2A_ADVERTISED_TOOLSETS` | 所有已注册的技能 | 控制 Agent Card 上显示的技能列表 |

如果在反向代理或 Kubernetes Service 后面运行，需设置 `A2A_PUBLIC_URL`（或依赖 `X-Forwarded-Host`/`X-Forwarded-Proto`），以便 Agent Card 能展示对等方实际可以回调的 URL。

## 快速测试

```bash
# From another machine / agent:
curl http://your-host:9900/.well-known/agent-card.json

curl -X POST http://your-host:9900/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <token>' \
  -d '{"jsonrpc":"2.0","id":1,"method":"SendMessage",
       "params":{"message":{"messageId":"m1","role":"ROLE_USER",
                 "parts":[{"text":"What tools do you have?"}]}}}'
```

## 故障排除

- **对端无法访问卡片 URL** —— 该卡片当时使用的是您的绑定地址进行广播；请将 `A2A_PUBLIC_URL` 设置为可被外部访问的 URL。
- **出现 `401 Unauthorized` 错误** —— 令牌不匹配；请检查服务器端的 `A2A_PEER_TOKENS`/`A2A_BEARER_TOKEN` 以及对端配置中的 `auth:` 部分。
- **服务器拒绝绑定非本地主机地址** —— 这是设计如此：请先设置承载令牌，然后再将 `A2A_HOST` 设为 `0.0.0.0`。
- **长时间运行的任务导致响应超时** —— 请增加 `A2A_REPLY_TIMEOUT` 的值，或者让调用方配置推送通知功能，并定期调用 `GetTask` 方法查询任务状态。
