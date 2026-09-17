---
sidebar_position: 17
title: "LINE"
description: "Set up Hermes Agent as a LINE Messaging API bot"
---

# LINE 设置

通过官方的 LINE 消息传递 API，将 Hermes Agent 作为 [LINE](https://line.me/) 机器人运行。该适配器以平台插件形式打包在 `plugins/platforms/line/` 目录下——无需对核心代码进行修改，只需像使用其他平台一样启用它即可。

LINE 是日本、台湾和泰国市场上占据主导地位的消息应用。如果您的用户身处这些地区，他们将通过此方式与您取得联系。

> 运行 `hermes gateway setup` 并选择 **LINE**，即可获得逐步指导。

## 机器人的响应方式

| 场景 | 行为 |
|---------|--------|
| **1:1 聊天**（`U` 类型 ID） | 对每条消息均作出回应 |
| **群组聊天**（`C` 类型 ID） | 仅当群组在允许列表中时才响应 |
| **多用户房间**（`R` 类型 ID） | 仅当房间在允许列表中时才响应 |

系统可处理传入的文本、图片、音频、视频、文件、贴纸以及位置信息。对于传出文本，会首先使用**免费回复令牌**（一次性使用，有效期约60秒）；一旦令牌过期，则会转而使用按量计费的 Push API。

---

## 第一步：创建 LINE 消息传递 API 频道

1. 访问 [LINE 开发者控制台](https://developers.line.biz/console/)。
2. 创建一个 Provider，然后在其中创建一个 **消息传递 API** 频道。
3. 在频道的 **基本设置** 选项卡中，复制 **频道密钥**。
4. 在 **消息传递 API** 选项卡中，找到 **长期有效的频道访问令牌** 并点击 **生成**，随后复制该令牌。
5. 同样在 **消息传递 API** 选项卡中，禁用 **自动回复消息** 和 **欢迎消息**，以避免其与您的机器人回复产生冲突。

---

## 第二步：开放 webhook 端口

LINE通过公共HTTPS接口发送Webhook。默认端口为`8646`，如有需要，可通过`LINE_PORT`参数进行自定义设置。

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

复制 `https://...` 这个网址——您稍后将将其设置为 webhook 地址。在测试期间，请保持隧道处于运行状态。对于正式环境，建议配置一个固定的 Cloudflare 名称隧道，以避免重启后 webhook 地址发生变化。

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

这样就够了——`gateway/config.py` 中的 bundled-plugin 扫描功能会自动识别 `plugins/platforms/line/` 目录。无需修改 `Platform.LINE` 枚举，也无需进行 `_create_adapter` 的注册。

---

## 第 4 步：设置 webhook URL

返回 LINE 控制台：

1. 打开您的频道 → 进入 **Messaging API** 选项卡。
2. 在 **Webhook settings** 下方找到 **Webhook URL**，粘贴 `https://<your-tunnel>/line/webhook`（请注意路径中的 `/line/webhook` —— 适配器即在此处监听请求）。
3. 点击 **Verify**。LINE 会向该 URL 发送测试请求，您应能看到 200 的响应。
4. 将 **Use webhook** 的开关设置为 **On**。

---

## 第 5 步：运行网关

```bash
hermes gateway
```

代理日志显示：

```
LINE: webhook listening on * (all interfaces, IPv4+IPv6):8646/line/webhook (public: https://my-tunnel.example.com)
```

首先在LINE应用中将该机器人添加为好友（扫描频道**Messaging API**标签页中的二维码），随后向其发送消息即可。

---

## 大语言模型响应延迟

LINE的回复令牌为一次性使用，通常在收到请求后约60秒便会失效。若大语言模型处理速度较慢，将无法及时回复，此时通常需要通过付费的Push API来获取响应。

当大语言模型的运行时间超过`LINE_SLOW_RESPONSE_THRESHOLD`秒（默认值为45秒）时，适配器会使用原有的回复令牌来显示一个**模板按钮**气泡：

> 🤔 正在思考中。点击下方按钮，待答案准备好后即可获取。
>
> [ 获取答案 ]

用户可在方便时点击**获取答案**——该操作会返回一个新的回复令牌，适配器便能利用该令牌发送已缓存的答案（依然无需付费）。

状态机流程为：`PENDING → READY → DELIVERED`，此外还会出现表示任务被取消的`ERROR`状态（在执行 `/stop` 指令后，处于悬而未决的PENDING状态会自动转为“任务在完成前被中断”，从而避免按钮持续循环显示）。

如需禁用该回复按钮并始终使用Push方式作为备用方案：

```env
LINE_SLOW_RESPONSE_THRESHOLD=0
```

为确保回传流程能够稳定触发，需抑制那些会在达到阈值之前耗尽回复令牌的冗余消息。

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

那些通过 `deliver: line` 路由将消息发送至 `LINE_HOME_CHANNEL` 的定时任务。该适配器提供了一个独立的仅支持推送的消息发送器，因此即便定时任务在与网关不同的进程中运行，依然能够正常工作。

---

## 环境变量参考

| 参数名 | 是否必填 | 默认值 | 说明 |
|---|---|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | 是 | — | 长有效期频道访问令牌 |
| `LINE_CHANNEL_SECRET` | 是 | — | 频道密钥（用于HMAC-SHA256 webhook验证） |
| `LINE_HOST` | 否 | 未设置（双栈模式：所有接口，IPv4+IPv6） | Webhook绑定主机地址 |
| `LINE_PORT` | 否 | `8646` | Webhook绑定端口 |
| `LINE_PUBLIC_URL` | 仅用于媒体传输 | — | 公共HTTPS基础URL；发送图片、语音或视频时必需 |
| `LINE_ALLOWED_USERS` | 以下选项之一 | — | 用逗号分隔的用户ID（以U开头） |
| `LINE_ALLOWED_GROUPS` | 以下选项之一 | — | 用逗号分隔的群组ID（以C开头） |
| `LINE_ALLOWED_ROOMS` | 以下选项之一 | — | 用逗号分隔的房间ID（以R开头） |
| `LINE_ALLOW_ALL_USERS` | 仅限开发环境 | `false` | 完全跳过允许列表检查 |
| `LINE_HOME_CHANNEL` | 否 | — | 默认的定时任务/通知发送目标频道 |
| `LINE_SLOW_RESPONSE_THRESHOLD` | 否 | `45` | 触发回传按钮前的秒数（`0`表示禁用） |
| `LINE_PENDING_TEXT` | 否 | "🤔 Still thinking…" | 显示在回传按钮旁的提示文字 |
| `LINE_BUTTON_LABEL` | 否 | "Get answer" | 按钮标签文本 |
| `LINE_DELIVERED_TEXT` | 否 | "Already replied ✅" | 再次点击已发送过的回复按钮时的提示文字 |
| `LINE_INTERRUPTED_TEXT` | 否 | "Run was interrupted before completion." | 点击/stop异常按钮时的回复文字 |
| `LINE_EXPIRED_TEXT` | 否 | "That request has expired — send your message again." | 点击已过期缓存回复的按钮时的提示文字 |

## 故障排除

**Webhook 验证时出现“无效签名”错误。** 可能是 `Channel secret` 复制有误，或者您的隧道对请求体进行了修改。请先使用 `curl -i https://<tunnel>/line/webhook/health` 进行验证——该命令应返回 `{"status":"ok","platform":"line"}`。

**机器人无法在群组中接收消息。** 请检查 `LINE_ALLOWED_GROUPS` 是否已包含相应的 `C...` 群组 ID。若需查找群组 ID，可发送测试消息，然后在 `~/.hermes/logs/gateway.log` 文件中搜索 `LINE: rejecting unauthorized source`，被拒绝的来源信息中即包含相关 ID。

**使用 `send_image` 时出现“必须设置 LINE_PUBLIC_URL”错误。** LINE 的消息传递 API 不支持二进制文件上传——图片、音频和视频都必须是可通过 HTTPS 访问的网址。请将 `LINE_PUBLIC_URL` 设置为隧道的公共主机名，这样适配器就会自动从 `/line/media/<token>/<filename>` 路径提供文件。

**回传按钮始终不出现。** 可能是因为大语言模型的响应速度超过了 `LINE_SLOW_RESPONSE_THRESHOLD` 的阈值，或是其他界面元素（如工具进度条、流式内容）抢先使用了回复令牌。详情请参阅“大语言模型响应过慢”章节中的相关说明。

**出现“已被其他配置使用”的错误。** 同一个频道访问令牌已被绑定到另一个正在运行的 Hermes 配置中。请停止该另一个网关，或使用独立的频道。

---

## 局限性

* **消息气泡长度限制。** 每个LINE文本气泡的最大字符数为5000。对于过长的回复，系统会将其智能分割为约4500字符的多个部分，每次回复/推送最多包含5个气泡，并尽可能在语义分隔处进行拆分。
* **不支持直接编辑消息。** LINE没有提供消息编辑接口——流式回复始终会生成新的消息气泡，而无法修改之前的内容。
* **不支持Markdown格式渲染。** 加粗（`**`）、斜体（`*`）、代码块以及标题等格式都会以原始字符形式呈现。适配器会在发送前移除这些格式；不过URL地址会被保留（例如 `[label](url)` 会变为 `label (url)`）。
* **加载指示器仅适用于私聊。** LINE不支持在群组或频道中使用聊天/加载相关API，因此输入中正在输入的指示器仅会在1对1私聊中显示。
