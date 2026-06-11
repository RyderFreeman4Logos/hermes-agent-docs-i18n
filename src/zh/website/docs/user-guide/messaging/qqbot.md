# QQ机器人

通过**官方QQ机器人API（v2）**将Hermes与QQ连接——支持私聊（C2C）、群组@提及、公会交流，以及带有语音转写的即时消息功能。

## 概述

QQ机器人适配器利用[官方QQ机器人API](https://bot.q.qq.com/wiki/develop/api-v2/)来实现以下功能：

- 通过与QQ网关的持久**WebSocket**连接接收消息
- 通过**REST API**发送文本及Markdown格式的回复
- 下载并处理图片、语音消息及文件附件
- 使用腾讯内置的ASR技术或可配置的STT服务对语音消息进行转写

## 前提条件

1. **QQ机器人应用**——需在[q.qq.com](https://q.qq.com)注册：
   - 创建新应用并记下**应用ID**和**应用密钥**
- 启用所需功能：C2C消息、群组@消息、公会消息
- 可选择在沙箱模式下配置机器人以进行测试，或发布到正式环境使用

2. **依赖库**——该适配器需要`aiohttp`和`httpx`这两个库：
   ```bash
   pip install aiohttp httpx
   ```

## 配置

### 交互式设置

```bash
hermes gateway setup
```

从平台列表中选择**QQ Bot**，然后按照提示操作。

### 手动配置

在`~/.hermes/.env`文件中设置所需的环境变量：

```bash
QQ_APP_ID=your-app-id
QQ_CLIENT_SECRET=your-app-secret
```

## 环境变量

| 变量名 | 描述 | 默认值 |
|---|---|---|
| `QQ_APP_ID` | QQ机器人应用ID（必需） | — |
| `QQ_CLIENT_SECRET` | QQ机器人应用密钥（必需） | — |
| `QQBOT_HOME_CHANNEL` | 用于定时任务/通知发送的OpenID | — |
| `QQBOT_HOME_CHANNEL_NAME` | 主通道的显示名称 | `Home` |
| `QQ_ALLOWED_USERS` | 允许私信发送的用户OpenID列表，以逗号分隔 | open（所有用户） |
| `QQ_GROUP_ALLOWED_USERS` | 允许群聊访问的群组OpenID列表，以逗号分隔 | — |
| `QQ_ALLOW_ALL_USERS` | 设置为`true`时可允许所有用户的私信 | `false` |
| `QQ_PORTAL_HOST` | 覆盖QQ门户主机地址（如需沙箱路由，请设置为`sandbox.q.qq.com`） | `q.qq.com` |
| `QQ_STT_API_KEY` | 语音转文本服务提供商的API密钥 | — |
| `QQ_STT_BASE_URL` | （不会被直接读取——请在`config.yaml`中设置`platforms.qqbot.extra.stt.baseUrl`） | 无 |
| `QQ_STT_MODEL` | 语音转文本模型名称 | `glm-asr` |

## 高级配置

如需更精细的控制，可将平台相关设置添加到`~/.hermes/config.yaml`文件中：

```yaml
platforms:
  qqbot:
    enabled: true
    extra:
      app_id: "your-app-id"
      client_secret: "your-secret"
      markdown_support: true       # enable QQ markdown (msg_type 2). Config-only; no env-var equivalent.
      dm_policy: "open"          # open | allowlist | disabled
      allow_from:
        - "user_openid_1"
      group_policy: "open"       # open | allowlist | disabled
      group_allow_from:
        - "group_openid_1"
      stt:
        provider: "zai"          # zai (GLM-ASR), openai (Whisper), etc.
        baseUrl: "https://open.bigmodel.cn/api/coding/paas/v4"
        apiKey: "your-stt-key"
        model: "glm-asr"
```

## 语音消息（文本转语音）

语音转写功能分为两个阶段：

1. **QQ内置ASR**（免费，系统会优先尝试）——QQ会在语音消息附件中提供`asr_refer_text`字段，该功能采用腾讯自研的语音识别技术。
2. **自定义文本转语音服务**（备用方案）——若QQ的ASR无法生成文本，适配器将会调用兼容OpenAI标准的文本转语音API：

   - **Zhipu/GLM (zai)**：默认选择的服务，使用`glm-asr`模型；
   - **OpenAI Whisper**：需设置`QQ_STT_BASE_URL`与`QQ_STT_MODEL`参数；
   - 任何其他兼容OpenAI标准的文本转语音接口。

## 故障排除

### 机器人立即断开连接（快速断开）

这通常由以下原因导致：
- **应用ID/密钥无效**——请在q.qq.com上仔细核对您的凭证信息；
- **权限不足**——确保机器人已启用所需的意图功能；
- **处于沙箱模式**——若机器人处于沙箱模式，它仅能接收来自QQ沙箱测试通道的消息。

### 语音消息无法被转写

1. 检查附件数据中是否包含QQ内置的`asr_refer_text`字段；
2. 若使用自定义文本转语音服务，请确认`QQ_STT_API_KEY`已正确设置；
3. 查看网关日志中的文本转语音相关错误信息。

### 消息无法送达

- 确认在q.qq.com上已启用机器人的相应**意图功能**；
- 若私信发送受到限制，请检查`QQ_ALLOWED_USERS`设置；
- 对于群组消息，需确保机器人已被**@提及**（群组规则可能要求将其加入允许列表）；
- 检查`QQBOT_HOME_CHANNEL`参数，确认定时任务/通知发送功能是否正常。

### 连接错误

- 确保已安装`aiohttp`和`httpx`库：`pip install aiohttp httpx`；
- 检查与`api.sgroup.qq.com`及WebSocket网关的网络连接状况；
- 查看网关日志中的详细错误信息以及系统的重连机制。
