---
sidebar_position: 17
title: "LINE"
description: "Set up Hermes Agent as a LINE Messaging API bot"
---

# LINE 设置

通过官方的 LINE 消息传递 API，将 Hermes Agent 作为 [LINE](https://line.me/) 机器人运行。该适配器以平台插件形式存在于 `plugins/platforms/line/` 目录下——无需对核心代码进行任何修改，只需像配置其他平台一样启用它即可。

LINE 是日本、台湾和泰国市场上占据主导地位的消息应用。如果您的用户位于这些地区，他们将通过此方式与您取得联系。

> 运行 `hermes gateway setup` 命令，然后选择 **LINE** 以获取逐步操作指南。

## 机器人的响应方式

| 场景 | 行为 |
|------|------|
| **一对一聊天**（`U` 类型账号） | 对每条消息均会回复 |
| **群组聊天**（`C` 类型账号） | 仅当群组在允许列表中时才会回复 |
| **多用户房间**（`R` 类型账号） | 仅当房间在允许列表中时才会回复 |

系统可处理传入的文本、图片、音频、视频、文件、贴图以及位置信息。对于传出文本，会优先使用**免费回复令牌**（一次性使用，有效期约60秒）；一旦令牌过期，则会转而使用按量计费的 Push API。

---

## 第1步：创建 LINE 消息传递 API 频道

1. 访问 [LINE 开发者控制台](https://developers.line.biz/console/)。
2. 创建一个 Provider，然后在其中创建一个 **消息传递 API** 频道。
3. 在频道的 **基本设置** 选项卡中，复制 **频道密钥**。
4. 在 **消息传递 API** 选项卡中，找到 **频道访问令牌（长期有效）**，点击 **生成** 并复制该令牌。
5. 同样在 **消息传递 API** 选项卡中，禁用 **自动回复消息** 和 **欢迎消息**，以避免其与您的机器人回复产生冲突。

---

## 第2步：开放 webhook 端口

LINE 通过公共 HTTPS 协议发送 webhook。默认端口为 `8646`——如有需要，可通过 `LINE_PORT` 变量进行自定义设置。

```bash
# Cloudflare Tunnel (recommended for production — fixed hostname)
cloudflared tunnel --url http://localhost:8646

# ngrok (good for dev)
ngrok http 8646

# devtunnel
devtunnel create hermes-line --allow-anonymous
devtunnel port create hermes-line -p 8646 --protocol https
devtunnel host hermes-line
```

复制 `https://...` 这个网址——您稍后将将其设置为 webhook 地址。在测试期间，请保持隧道处于运行状态。对于正式环境，建议配置一个固定的 Cloudflare 命名隧道，以避免重启后 webhook 地址发生变化。

---

## 第 3 步：配置 Hermes

在 `~/.hermes/.env` 文件中添加以下内容：

```env
LINE_CHANNEL_ACCESS_TOKEN=YOUR_LONG_LIVED_TOKEN
LINE_CHANNEL_SECRET=YOUR_CHANNEL_SECRET

# Allowlist — at least one of these (or LINE_ALLOW_ALL_USERS=true for dev)
LINE_ALLOWED_USERS=U1234567890abcdef...           # comma-separated U-prefixed IDs
LINE_ALLOWED_GROUPS=C1234567890abcdef...          # optional group IDs
LINE_ALLOWED_ROOMS=R1234567890abcdef...           # optional room IDs

# Required for image / audio / video sends — the public HTTPS base URL
# the tunnel resolves to.  Without it, send_image/voice/video will refuse.
LINE_PUBLIC_URL=https://my-tunnel.example.com
```

接着在 `~/.hermes/config.yaml` 文件中：

```yaml
gateway:
  platforms:
    line:
      enabled: true
```

到此为止——`gateway/config.py` 中的 bundled-plugin 扫描功能会自动识别 `plugins/platforms/line/` 目录下的插件。无需修改 `Platform.LINE` 枚举值，也无需进行 `_create_adapter` 的注册操作。

---

## 第 4 步：设置 webhook URL

返回 LINE 控制台：

1. 打开您的频道 → 进入 **Messaging API** 选项卡。
2. 在 **Webhook settings** 下方找到 **Webhook URL**，粘贴 `https://<your-tunnel>/line/webhook`（请注意路径中的 `/line/webhook` —— 适配器会在此处监听请求）。
3. 点击 **Verify**。LINE 会向该 URL 发送测试请求，您应能看到 200 的响应。
4. 将 **Use webhook** 的开关设置为 **On**。

---

## 第 5 步：运行网关

```bash
hermes gateway
```

代理日志显示：

```
LINE: webhook listening on 0.0.0.0:8646/line/webhook (public: https://my-tunnel.example.com)
```

请通过LINE应用将该机器人添加为好友（扫描频道**Messaging API**标签页中的二维码），然后向其发送消息。

---

## 大语言模型响应延迟

LINE的回复令牌为一次性使用，会在接收到请求后约60秒失效。若大语言模型处理速度较慢，将无法及时回复，此时通常需要调用付费的Push API。

当大语言模型的运行时间超过`LINE_SLOW_RESPONSE_THRESHOLD`秒（默认值为45秒）时，适配器会使用原有的回复令牌来发送一个**模板按钮**浮窗：

> 🤔 正在思考中。点击下方按钮，待答案准备好后获取结果。
>
> [ 获取答案 ]

用户可在方便时点击**获取答案**——该回调会提供一个全新的回复令牌，适配器便能使用它来发送已缓存的答案（仍为免费服务）。

状态机流程为：`PENDING → READY → DELIVERED`，此外对于被取消的运行任务还会出现`ERROR`状态（在执行 `/stop` 指令后，处于“待处理”状态的请求会自动转为“运行在完成前被中断”，从而避免按钮无限循环）。

如需禁用该回调按钮并始终使用Push方式作为备用方案：

```env
LINE_SLOW_RESPONSE_THRESHOLD=0
```

为确保回传流程能够稳定触发，需抑制那些会在达到阈值前耗尽回复令牌的无效请求。

```yaml
# ~/.hermes/config.yaml
display:
  interim_assistant_messages: false
  platforms:
    line:
      tool_progress: off
```

## 定时任务调度 / 通知发送

```env
LINE_HOME_CHANNEL=Uxxxxxxxxxxxxxxxxxxxx     # default delivery target
```

支持通过 `deliver: line` 路由将任务发送至 `LINE_HOME_CHANNEL` 的定时任务。该适配器提供了独立的仅推送型发送器，即便定时任务在与网关不同的进程中运行，也能正常工作。

---

## 环境变量参考

| 变量 | 是否必填 | 默认值 | 描述 |
|---|---|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | 是 | — | 长期有效的频道访问令牌 |
| `LINE_CHANNEL_SECRET` | 是 | — | 频道密钥（用于 HMAC-SHA256 webhook 验证） |
| `LINE_HOST` | 否 | `0.0.0.0` | Webhook 绑定主机 |
| `LINE_PORT` | 否 | `8646` | Webhook 绑定端口 |
| `LINE_PUBLIC_URL` | 仅用于媒体内容 | — | 公共 HTTPS 基址；发送图片、语音或视频时必需 |
| `LINE_ALLOWED_USERS` | 可选 | — | 以逗号分隔的用户 ID（以 U 开头） |
| `LINE_ALLOWED_GROUPS` | 可选 | — | 以逗号分隔的群组 ID（以 C 开头） |
| `LINE_ALLOWED_ROOMS` | 可选 | — | 以逗号分隔的房间 ID（以 R 开头） |
| `LINE_ALLOW_ALL_USERS` | 仅开发环境可用 | `false` | 完全忽略允许列表设置 |
| `LINE_HOME_CHANNEL` | 否 | — | 默认的定时任务/通知发送目标 |
| `LINE_SLOW_RESPONSE_THRESHOLD` | 否 | `45` | 回复按钮触发前的秒数（`0` 表示禁用） |
| `LINE_PENDING_TEXT` | 否 | "🤔 Still thinking…" | 显示在回复按钮旁的提示文本 |
| `LINE_BUTTON_LABEL` | 否 | "Get answer" | 按钮标签 |
| `LINE_DELIVERED_TEXT` | 否 | "Already replied ✅" | 再次点击已发送状态按钮时的回复内容 |
| `LINE_INTERRUPTED_TEXT` | 否 | "Run was interrupted before completion." | 点击 `/stop` 异常按钮时的回复内容 |

---

## 故障排除

**Webhook 验证时出现“无效签名”错误。** 可能是 `Channel secret` 复制有误，或是隧道服务修改了请求体。请先使用 `curl -i https://<tunnel>/line/webhook/health` 进行验证——正常情况下应返回 `{"status":"ok","platform":"line"}`。

**机器人在群组中无法收到任何消息。** 请检查 `LINE_ALLOWED_GROUPS` 是否已包含对应的 `C...` 开头的群组 ID。若需查找群组 ID，可发送测试消息，然后在 `~/.hermes/logs/gateway.log` 文件中搜索 `LINE: rejecting unauthorized source`，被拒绝的来源信息中即包含相关 ID。

**使用 `send_image` 时出现“必须设置 LINE_PUBLIC_URL”错误。** LINE 的消息 API 不支持二进制文件上传——图片、音频和视频必须为可访问的 HTTPS 地址。将 `LINE_PUBLIC_URL` 设置为隧道的公共主机名，适配器便会自动从 `/line/media/<token>/<filename>` 路径提供相应文件。

**回复按钮始终不显示。** 可能是大型语言模型的响应速度快于 `LINE_SLOW_RESPONSE_THRESHOLD` 所设定的阈值，或是其他提示气泡（如任务进度、流式响应等）先占用了回复令牌。可参考“大型语言模型响应过慢”章节中的相关说明。

**出现“该频道已被其他账号使用”的错误。** 同一频道访问令牌可能已绑定到其他正在运行的 Hermes 实例。请停止其他网关服务，或使用不同的频道。

---

## 局限性

* **提示气泡数量与长度限制。** 每个 LINE 文本提示气泡的最大字符数为 5000。较长的回复内容会被智能分割，每个回复/推送请求最多生成 5 个气泡，每个气泡的字符数约为 4500，分割时会尽可能选择自然断句点。
* **不支持直接编辑消息。** LINE 没有提供消息编辑 API——流式响应始终会生成新的提示气泡，而无法修改之前的内容。
* **不支持 Markdown 格式渲染。** 加粗（`**`）、斜体（`*`）、代码块以及标题等格式都会以原始字符形式显示。适配器在发送前会移除这些格式；URL 地址则会被保留（例如 `[标签](url)` 会变为 `标签 (url)`）。
* **加载指示器仅适用于私聊。** LINE 不支持在群组或房间中使用聊天/加载状态 API，因此打字中状态指示器仅会在一对一私聊中显示。
