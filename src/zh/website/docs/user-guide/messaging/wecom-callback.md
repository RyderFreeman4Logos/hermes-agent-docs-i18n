---
sidebar_position: 15
---

# WeCom 回调（自建应用）

通过回调/Webhook 模式，将 Hermes 作为自建企业应用连接到 WeCom（企业微信）。

:::info WeCom 机器人与 WeCom 回调的差异
Hermes 支持两种 WeCom 集成方式：
- **[WeCom 机器人](wecom.md)** — 采用机器人模式，通过 WebSocket 连接。设置更简单，可在群聊中使用。
- **WeCom 回调**（本页面） — 自建应用，接收加密的 XML 回调信息。会在用户的 WeCom 侧边栏中以独立应用的形式显示，并支持多企业路由。
:::

如需了解机器人模式的集成方式，请参阅：[WeCom 机器人](./wecom.md)。

> 运行 `hermes gateway setup` 并选择 **WeCom 回调**，即可获得逐步指导。

## 工作原理

1. 在 WeCom 管理控制台注册自建应用
2. WeCom 将加密的 XML 数据推送到您的 HTTP 回调端点
3. Hermes 解密该消息并将其放入队列，等待智能体处理
4. 立即发送确认反馈（无显式提示，用户不会看到任何内容）
5. 智能体处理请求（通常需要 3–30 分钟）
6. 通过 WeCom 的 `message/send` API 主动发送回复

## 前提条件

- 具有管理权限的 WeCom 企业账号
- Python 包 `aiohttp` 和 `httpx`（默认安装已包含）
- 用于回调 URL 的可公开访问服务器（或 ngrok 等隧道服务）

## 设置步骤

### 1. 在 WeCom 中创建自建应用

1. 访问 [WeCom 管理控制台](https://work.weixin.qq.com/) → **Applications** → **Create App**。
2. 记下管理控制台顶部显示的 **Corp ID**。
3. 在应用设置中创建一个 **Corp Secret**。
4. 从应用的概览页面中记下 **Agent ID**。
5. 在 **Receive Messages** 选项下配置回调 URL：
   - URL：`http://YOUR_PUBLIC_IP:8645/wecom/callback`
   - Token：生成一个随机令牌（WeCom 也会提供）。
   - EncodingAESKey：生成一个密钥（WeCom 也会提供）。

### 2. 配置环境变量

在您的 `.env` 文件中添加以下内容：

```bash
WECOM_CALLBACK_CORP_ID=your-corp-id
WECOM_CALLBACK_CORP_SECRET=your-corp-secret
WECOM_CALLBACK_AGENT_ID=1000002
WECOM_CALLBACK_TOKEN=your-callback-token
WECOM_CALLBACK_ENCODING_AES_KEY=your-43-char-aes-key

# Optional
# WECOM_CALLBACK_HOST=  # optional pin; unset = dual-stack (all interfaces, IPv4+IPv6)
WECOM_CALLBACK_PORT=8645
WECOM_CALLBACK_ALLOWED_USERS=user1,user2
```

### 3. 启动网关

```bash
hermes gateway
```

（请仅在 `hermes gateway install` 成功注册 systemd/launchd 服务之后，再使用 `hermes gateway start` 命令。）

回调适配器会在配置的端口上启动一个 HTTP 服务器。WeCom 会先通过 GET 请求验证回调 URL，随后再通过 POST 请求开始发送消息。

## 配置参考

可在 `config.yaml` 的 `platforms.wecom_callback.extra` 下设置这些参数，也可使用环境变量：

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `corp_id` | — | WeCom 企业 Corp ID（必填） |
| `corp_secret` | — | 自建应用的企业密钥（必填） |
| `agent_id` | — | 自建应用的 Agent ID（必填） |
| `token` | — | 回调验证令牌（必填） |
| `encoding_aes_key` | — | 用于回调加密的 43 位 AES 密钥（必填） |
| `host` | 未设置（双栈模式：所有接口，IPv4+IPv6） | HTTP 回调服务器的绑定地址 |
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

为避免不同企业间的数据冲突，系统会通过 `corp_id:user_id` 对用户进行范围限定。当用户发送消息时，适配器会记录该用户所属的应用（企业），并利用对应应用的访问令牌来转发回复。

## 访问控制

限制可与该应用交互的用户范围：

```bash
# Allowlist specific users
WECOM_CALLBACK_ALLOWED_USERS=zhangsan,lisi,wangwu

# Or allow all users
WECOM_CALLBACK_ALLOW_ALL_USERS=true
```

## 接口端点

该适配器提供以下接口：

| 方法 | 路径 | 用途 |
|------|------|---------|
| GET | `/wecom/callback` | URL验证握手（WeCom在初始化时发送此请求） |
| POST | `/wecom/callback` | 加密消息回调（WeCom会将用户消息发送至此） |
| GET | `/health` | 健康检查——返回`{"status": "ok"}` |

## 加密机制

所有回调数据均使用EncodingAESKey通过AES-CBC算法进行加密。适配器负责处理以下流程：

- **接收端**：解密XML格式的数据，并验证SHA1签名
- **发送端**：回复消息通过主动API发送（而非加密的回调响应）

该加密实现与腾讯官方的WXBizMsgCrypt SDK兼容。

## 局限性

- **不支持流式传输**——回复会在智能体处理完成后以完整消息形式送达
- **不支持输入状态指示**——当前回调机制不支持显示输入中状态
- **仅支持文本输入**——目前仅支持文本消息作为输入；图片、文件及语音输入功能尚未实现。智能体可通过WeCom平台的提示信息了解外部媒体类型（图片、文档、视频、语音）
- **响应延迟**——智能体处理过程需要3至30分钟，用户将在处理完成后看到回复

## 故障排除

**签名验证失败。**  
WeCom会使用您在管理控制台注册的**Token**对每个请求进行签名。最常见的原因在于Hermes中配置的Token与管理控制台所期望的Token不一致。请重新从管理控制台复制**Token**和**EncodingAESKey**——这两个值很容易被截断。此外，`~/.hermes/.env`文件中`=`号两侧的空白字符也会导致签名验证失败。修复这些问题后，请重新启动`hermes gateway run`。

**回调URL无法访问/验证步骤失败。**  
WeCom会向您注册的公共URL发起请求。请确认以下几点：  
1. 您的反向代理/隧道能够将 `/wecom/callback` 请求转发到网关的端口。  
2. 管理控制台中的URL必须是HTTPS格式（WeCom不接受普通的HTTP请求）。  
3. 从您的网络外部使用 `curl -i https://<your-domain>/wecom/callback` 命令发起请求时，不应出现超时错误（没有查询参数的4xx错误是正常的——这只是说明监听器可以访问）。

**端口无法访问/监听器未绑定。**  
请查看`hermes gateway run`的输出日志，确认绑定的主机和端口信息。如果适配器绑定在`127.0.0.1`上，就必须通过反向代理或隧道来转发请求——因为WeCom的服务器无法访问回环地址。您可以保持`extra.host`未被设置，这样就会启用默认的双栈绑定模式（同时监听所有接口，包括IPv4和IPv6）；或者是在`config.yaml`中指定具体的接口（如果需要直接暴露服务，则还需设置`allowed_source_cidrs`）；又或者保留回环地址，但使用Cloudflare Tunnel或nginx等隧道工具来建立连接。
