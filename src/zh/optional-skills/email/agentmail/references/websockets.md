# AgentMail WebSocket接口

当本地代理进程需要实时接收邮件时，可使用WebSocket接口。事件到达后，可通过CLI工具来处理收件、发送、回复、标记邮件及处理附件等操作。

## Python版本

该Python示例需要单独的AgentMail Python SDK，而非CLI工具：

```bash
pip install agentmail
```

`AgentMail()` 会从环境变量中读取 `AGENTMAIL_API_KEY`。如果该 SDK 不可用，则可改用下方的 `Raw` WebSocket 方式。

```python
from agentmail import AgentMail, MessageReceivedEvent, Subscribe

client = AgentMail()

with client.websockets.connect() as socket:
    socket.send_subscribe(Subscribe(
        inbox_ids=["agent@agentmail.to"],
        event_types=["message.received"],
    ))
    for event in socket:
        if isinstance(event, MessageReceivedEvent):
            print(event.message.subject, event.message.from_)
```

## 原始数据

```text
wss://ws.agentmail.to/v0?api_key=$AGENTMAIL_API_KEY
```

欧盟地区：

```text
wss://ws.agentmail.eu/v0?api_key=$AGENTMAIL_API_KEY
```

订阅框架：

```json
{ "type": "subscribe", "event_types": ["message.received"], "inbox_ids": ["agent@agentmail.to"] }
```

在 API 密钥的作用范围内，可省略 `inbox_ids` 和 `pod_ids` 参数。  

## 循环规则

- 按 `event_id` 对每个事件进行去重处理。
- 以延迟策略尝试重新连接，并在连接成功后再次订阅。
