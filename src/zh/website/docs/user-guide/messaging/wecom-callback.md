---
sidebar_position: 15
---

# WeCom 回调（自建应用）

通过回调/Webhook 模式，将 Hermes 作为自建企业应用连接到 WeCom（企业微信）。

:::info WeCom 机器人与 WeCom 回调的差异
Hermes 支持两种 WeCom 集成方式：
- **[WeCom 机器人](wecom.md)** — 采用机器人模式，通过 WebSocket 连接。设置更简单，可在群聊中使用。
- **WeCom 回调**（本页面介绍）——自建应用，接收加密的 XML 回调信息。会在用户的 WeCom 侧边栏中以独立应用的形式显示，并支持多企业路由。
:::

如需了解机器人模式的集成方式，请参阅：[WeCom 机器人](./wecom.md)。

> 运行 `hermes gateway setup` 并选择 **WeCom 回调**，即可获得逐步指导。

## 工作原理

1. 在 WeCom 管理控制台注册自建应用
2. WeCom 将加密的 XML 数据推送到您的 HTTP 回调端点
3. Hermes 解密该消息并将其放入代理队列中
4. 立即发送确认响应（静默处理——不会向用户显示任何内容）
5. 代理处理请求（通常需要 3–30 分钟）
6. 通过 WeCom 的 `message/send` API 主动发送回复

## 前提条件

- 具有管理权限的 WeCom 企业账户
- Python 包 `aiohttp` 和 `httpx`（默认安装已包含）
- 用于回调 URL 的可公开访问服务器（或 ngrok 等隧道工具）

## 设置步骤

### 1. 在 WeCom 中创建自建应用

1. 访问 [WeCom 管理控制台](https://work.weixin.qq.com/) → **应用程序** → **创建应用**
2. 记下**企业 ID**（显示在管理控制台顶部）
3. 在应用设置中创建**企业密钥**
4. 记下应用概览页面中的**代理 ID**
5. 在**接收消息**选项中配置回调 URL：
   - URL：`http://YOUR_PUBLIC_IP:8645/wecom/callback`
   - Token：生成随机令牌（WeCom 也会提供）
   - EncodingAESKey：生成密钥（WeCom 也会提供）

### 2. 配置环境变量

在您的 `.env` 文件中添加以下内容：

```bash
WECOM_CALLBACK_CORP_ID=your-corp-id
WECOM_CALLBACK_CORP_SECRET=your-corp-secret
WECOM_CALLBACK_AGENT_ID=1000002
WECOM_CALLBACK_TOKEN=your-callback-token
WECOM_CALLBACK_ENCODING_AES_KEY=your-43-char-aes-key

# Optional
WECOM_CALLBACK_HOST=0.0.0.0
WECOM_CALLBACK_PORT=8645
WECOM_CALLBACK_ALLOWED_USERS=user1,user2
```

### 3. 启动网关

```bash
hermes gateway
```

（请务必在 `hermes gateway install` 成功注册 systemd/launchd 服务之后，再使用 `hermes gateway start` 命令。）

回调适配器会在配置的端口上启动一个 HTTP 服务器。WeCom 会通过 GET 请求验证回调 URL，随后再通过 POST 请求开始发送消息。

## 配置参考

可在 `config.yaml` 的 `platforms.wecom_callback.extra` 下设置这些参数，也可使用环境变量：

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `corp_id` | — | WeCom 企业 Corp ID（必填） |
| `corp_secret` | — | 自建应用的企密钥（必填） |
| `agent_id` | — | 自建应用的 Agent ID（必填） |
| `token` | — | 回调验证令牌（必填） |
| `encoding_aes_key` | — | 用于回调加密的 43 位 AES 密钥（必填） |
| `host` | `0.0.0.0` | HTTP 回调服务器的绑定地址 |
| `port` | `8645` | HTTP 回调服务器的端口 |
| `path` | `/wecom/callback` | 回调端点的 URL 路径 |

## 多应用路由

对于需要运行多个自建应用的企业（例如不同部门或子公司），可在 `config.yaml` 中配置 `apps` 列表：

```yaml
platforms:
  wecom_callback:
    enabled: true
    extra:
      host: "0.0.0.0"
      port: 8645
      apps:
        - name: "dept-a"
          corp_id: "ww_corp_a"
          corp_secret: "secret-a"
          agent_id: "1000002"
          token: "token-a"
          encoding_aes_key: "key-a-43-chars..."
        - name: "dept-b"
          corp_id: "ww_corp_b"
          corp_secret: "secret-b"
          agent_id: "1000003"
          token: "token-b"
          encoding_aes_key: "key-b-43-chars..."
```

为避免不同企业间的用户数据冲突，系统会通过 `corp_id:user_id` 对用户进行范围限定。当用户发送消息时，适配器会记录该用户所属的应用（企业），并利用对应应用的访问令牌来转发回复。

## 访问控制

限制可与该应用交互的用户范围：

```bash
# Allowlist specific users
WECOM_CALLBACK_ALLOWED_USERS=zhangsan,lisi,wangwu

# Or allow all users
WECOM_CALLBACK_ALLOW_ALL_USERS=true
```

## 接口端点

该适配器提供了以下接口：

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/wecom/callback` | URL 验证握手（WeCom 在初始化时发送此请求） |
| POST | `/wecom/callback` | 加密消息回调（WeCom 会在此处发送用户消息） |
| GET | `/health` | 健康检查——返回 `{"status": "ok"}` |

## 加密机制

所有回调数据均使用 AES-CBC 算法及 EncodingAESKey 进行加密。适配器负责处理以下流程：

- **接收端**：解密 XML 格式的数据，并验证 SHA1 签名
- **发送端**：通过主动 API 发送回复（并非通过加密的回调响应）

该加密实现与腾讯官方的 WXBizMsgCrypt SDK 兼容。

## 局限性

- **不支持流式传输**——回复会在智能体处理完成后以完整消息的形式送达
- **不支持输入状态指示**——当前回调机制不支持显示输入中状态
- **仅支持文本输入**——目前仅支持文本消息作为输入；图片、文件及语音输入功能暂未实现。智能体可通过 WeCom 平台的提示信息了解外部媒体类型（图片、文档、视频、语音）
- **响应延迟**——智能体处理任务需要 3 到 30 分钟，用户将在处理完成后看到回复

## 故障排除

**签名验证失败**
WeCom 会使用你在管理控制台注册的 **Token** 对每个请求进行签名。最常见的原因是 Hermes 中配置的 Token 与管理控制台要求的 Token 不一致。请重新从管理控制台复制 **Token** 和 **EncodingAESKey**——这些值很容易被截断。`~/.hermes/.env` 文件中 `=` 号周围的空格也会导致签名验证失败。修复问题后，请重新运行 `hermes gateway run`。

**回调 URL 无法访问/验证步骤失败**
WeCom 会访问你注册的公开 URL。请确认以下几点：
1. 你的反向代理或隧道服务能够将 `/wecom/callback` 请求转发到网关的端口
2. 管理控制台中的 URL 必须是 HTTPS 协议（WeCom 不接受普通 HTTP 请求）
3. 从网络外部使用 `curl -i https://<your-domain>/wecom/callback` 命令测试时，不应出现超时错误（没有查询参数的 4xx 错误属于正常现象，仅表示监听器可访问）

**端口无法访问/监听器未绑定**
请查看 `hermes gateway run` 的日志以确认绑定的主机和端口信息。如果适配器绑定在 `127.0.0.1` 上，就必须通过反向代理或隧道服务作为前置节点——WeCom 的服务器无法访问回环地址。你可以在 `config.yaml` 文件中设置 `extra.host: 0.0.0.0`（如果直接公开访问还需设置 `allowed_source_cidrs`），或者保留回环地址并使用 Cloudflare Tunnel 或 nginx 等隧道服务。
