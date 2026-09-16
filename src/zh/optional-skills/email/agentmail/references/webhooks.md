# AgentMail Webhook 功能

当需要通过公共 HTTPS 服务器接收 AgentMail 事件时，可使用 Webhook。对于没有公共 URL 的本地进程，请参考 [websockets.md](websockets.md) 文档。

## 创建 Webhook

```bash
agentmail webhooks create \
  --url https://your-app.example.com/webhooks/agentmail \
  --event-type message.received \
  --inbox-id support@agentmail.to \
  --client-id support-agentmail-webhook \
  --format json
```

请立即存储返回的 `secret` 值。

## 处理流程

请求头：`svix-id`、`svix-timestamp`、`svix-signature`。

1. 使用 webhook 密钥验证原始请求体。
2. 根据 `svix-id` 或 `event_id` 进行去重处理。
3. 迅速返回 `200` 状态码。
4. 以异步方式处理该请求。
5. 对于 `message.received` 类型的消息，可使用 CLI 加载对应对话线程，并在必要时进行回复。

仅需处理 `message.received` 类型的消息。若将 `message.sent` 或传输相关事件视为需要处理的入站任务，将会导致循环问题。
