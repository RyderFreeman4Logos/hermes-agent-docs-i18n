---
sidebar_position: 6
title: "WhatsApp Business (Cloud API)"
description: "Set up Hermes Agent as a WhatsApp bot via Meta's official Business Cloud API"
---

# WhatsApp Business Cloud API 设置指南

Hermes 可通过 Meta 的**官方**WhatsApp Business Cloud API 与 WhatsApp 进行连接。这是生产级解决方案：无需 Node.js 中间进程，无需二维码，也不会存在账号被封的风险。

但相应地，您需要满足以下条件：
- 您必须拥有**Meta 商业账户**（而非个人 WhatsApp 账号）；
- 机器人将运行在专用的企业电话号码上，而非您的个人号码；
- Hermes 网关需要一个**公开的 HTTPS 地址**，以便 Meta 通过 webhook 发送传入消息；
- 若在用户最后发送消息后超过 24 小时才回复，则必须使用预先审批好的**回复模板**（这是 Meta 的“客户服务时间窗口”规定，并非 Hermes 的限制）。

如果这些要求不符合您的使用场景，[Baileys 中间件集成方案](./whatsapp.md)可作为替代选择——该方案允许使用个人账号且无需公开 URL，但属于非官方方案，存在账号被封的风险。

:::提示 我该选择哪种方案？
- **Cloud API（本指南所述方案）**——适合运行真正的企业级机器人，追求稳定性，愿意接受 Meta 的账号验证及模板审批流程；
- **[Baileys 中间件](./whatsapp.md)**——适用于个人项目、快速演示或单用户场景，但需承担机器人电话号码被封的风险。
:::

---

## 快速入门

```bash
hermes whatsapp-cloud
```

向导会逐步引导您填写每项凭证，在您输入时对每一项进行验证（可避免最常见的设置错误——将电话号码粘贴到“电话号码ID”字段中），并为那些需要在向导之外完成的操作提供明确的后续说明（如启动 Cloudflare Tunnel、配置 Meta 的 webhook 仪表板）。

本页面的其余部分则为手动参考文档。

---

## 先决条件

1. **一个 Meta 商业账户**。请在 [business.facebook.com](https://business.facebook.com/) 上创建。
2. **一个已启用 WhatsApp 功能的 Meta 应用**。详情请参见下文的“创建 Meta 应用”部分。
3. **一种能够通过 HTTPS 将本地端口暴露到公共互联网的方法**。推荐使用 Cloudflare Tunnel（`cloudflared`）——免费、无需端口转发、也不需要域名。ngrok、带有反向代理和 TLS 的自定义域名，或是将网关直接绑定到公网 IP 的 VPS 也都可以。
4. **非必需但建议配置**：确保 `PATH` 环境变量中包含 ffmpeg，这样发送的语音消息就会以 WhatsApp 原生的语音消息气泡形式（绿色波形）呈现，而非 MP3 音频附件。若未安装 ffmpeg，Hermes 仍可正常运行，但功能会受限。

---

## 创建 Meta 应用

1. 访问 [developers.facebook.com/apps](https://developers.facebook.com/apps)，然后点击**创建应用**。
2. 选择使用场景：**“通过 WhatsApp 与客户建立联系”**，接着点击**下一步**。
3. 选择或创建一个商业档案。仔细阅读发布要求，确认后点击**创建应用**。
4. 创建完成后，您将进入**自定义使用场景 → 通过 WhatsApp 建立联系 → 快速入门**页面。点击**开始使用 API**，即可进入**API 设置**页面。
5. 确保已关联一个 WhatsApp 商业账户（WABA）。如果您在步骤 3 中创建了新的商业档案，系统会自动创建一个 WABA。请在 API 设置页面中进行确认。

您需要从仪表板中获取以下信息——向导会按此顺序提示您填写：

| 参数 | 位于仪表板的位置 | 字段类型 | 备注 |
|---|---|---|---|
| **电话号码ID** | 应用仪表板 → WhatsApp → API 设置 → “发件人”下拉菜单下方 | 数字，15-17位 | **不是**电话号码本身。最常见的设置错误就是将实际电话号码粘贴到这里。 |
| **访问令牌** | 应用仪表板 → WhatsApp → API 设置 → “生成访问令牌” | 以 `EAA` 开头，长度超过100字符 | 临时令牌的有效期为24小时——如需用于生产环境，请参见下文的“永久令牌”。 |
| **应用密钥** | 应用仪表板 → 设置 → 基本信息 → 点击“显示”按钮 | 32位小写十六进制字符串 | 用于验证传入的 webhook 签名。若缺少此密钥，接收到的消息将被拒绝，返回503错误。 |
| **应用ID**（可选） | 应用仪表板 → 设置 → 基本信息 | 数字，15-16位 | 发送消息时并非必需，但可用于分析数据。 |
| **WABA ID**（可选） | 应用仪表板 → WhatsApp → API设置 → 顶部附近 | 数字，15位以上 | 发送消息时并非必需，但可用于分析数据。 |

---

## 永久令牌（用于生产环境）

临时访问令牌的有效期为**24小时**，这意味着今天生成的令牌次日就会失效。对于生产环境部署，建议使用**系统用户永久令牌**：

1. 访问 [business.facebook.com/latest/settings](https://business.facebook.com/latest/settings)，然后点击左侧栏的**系统用户**。
2. 点击**添加**，输入名称（例如 `hermes-bot`），角色选择**管理员**。
3. 选中新创建的用户，然后点击**分配资产**：
   - 选择您的应用，在“完全控制”选项下勾选**管理应用**。
   - 选择您的 WhatsApp 账户，在“完全控制”选项下勾选**管理 WhatsApp 商业账户**。
   - 点击**分配资产**。
4. 使用以下权限**生成令牌**：
   - `business_management`
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
5. 将**令牌过期时间**设置为**永不过期**。
6. 复制该令牌，将其值更新到 `~/.hermes/.env` 文件中的 `WHATSAPP_CLOUD_ACCESS_TOKEN` 字段中，最后重启网关。

除非您主动撤销，否则系统用户令牌不会过期。

---

## 将 Hermes 暴露到互联网

Cloud API 会通过 HTTPS POST 请求将接收到的消息发送到您的 webhook 地址——这意味着 Hermes 网关必须能够被 Meta 的服务器访问。有以下三种常见方法：

### Cloudflare Tunnel（推荐）

免费、无需端口转发，适用于 Windows / macOS / Linux 系统。它作为独立进程与网关一同运行。

**安装步骤：**

```bash
# Windows
winget install Cloudflare.cloudflared

# macOS
brew install cloudflared

# Linux
# Download the binary from https://github.com/cloudflare/cloudflared/releases
```

**快速创建隧道**（无需 Cloudflare 账户——将会生成一个 `https://<随机字符串>.trycloudflare.com` 的网址）：

```bash
cloudflared tunnel --url http://localhost:8090
```

请记下显示的URL——这就是您需要提供给Meta的地址。

:::warning 快速隧道会定期更换
每次重启`cloudflared`后，免费的快速隧道URL都会发生变化。若需使用稳定的URL，请通过`cloudflared tunnel login`登录并创建一个命名隧道。免费Cloudflare账户可创建无限数量的命名隧道——有关命名隧道的详细操作流程，请参阅[Cloudflare官方文档](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/)。
:::

### ngrok

```bash
ngrok http 8090
```

免费套餐在每次重启后都会显示不同的网址，而付费套餐则能为您提供稳定的子域名。

### 自有域名 + 反向代理

如果您已拥有配备 TLS 证书的服务器（如 Caddy、nginx 等），只需将路由指向 `localhost:8090` 即可。这是用于生产环境的最稳定方案，但需要预先具备相关基础设施。

---

## 在 Meta 端配置 webhook

当您的隧道开始运行后：

1. 记下隧道输出的公共网址——例如 `https://abc123.trycloudflare.com`。
2. 生成一个**验证令牌**——向导会通过 `secrets.token_urlsafe(32)` 自动完成此操作；如果您选择手动配置，则需执行相应命令：
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
在 `~/.hermes/.env` 文件中，将其保存为 `WHATSAPP_CLOUD_VERIFY_TOKEN`。
3. 启动 Hermes 网关：执行命令 `hermes gateway`。
4. 进入 Meta 应用控制面板 → **WhatsApp → Configuration**（根据界面版本不同，也可能为 **Use cases → Customize → Configuration**）→ 点击 Webhook 区域的 **Edit** 按钮。
5. 填写以下内容：
   - **Callback URL**：`https://abc123.trycloudflare.com/whatsapp/webhook`
   - **Verify Token**：第 2 步中生成的字符串（必须完全一致）
6. 点击 **Verify and save**。Meta 会通过 GET 请求访问您的 URL，网关会回传验证挑战信息，随后 Meta 会将该 Webhook 标记为已验证。
7. 在 **Webhook fields** 下方，点击 **Manage** → 订阅 **messages** 字段。这样即可告知 Meta 将接收到的消息实际发送到您的 Webhook。

**如需手动验证该流程**（可在第三个终端中操作）：

```bash
TUNNEL="https://abc123.trycloudflare.com"
VERIFY="<your verify token>"

# Should print HTTP 200 with body "hello"
curl -i "$TUNNEL/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=$VERIFY&hub.challenge=hello"

# Health endpoint — should show verify_token_configured: true and app_secret_configured: true
curl "$TUNNEL/health"
```

## 收件人白名单（Meta端）

在开发模式下（即您的应用尚未通过应用审核之前），Meta会限制机器人可以发送消息的号码范围：

1. 进入“应用控制面板”→“WhatsApp”→“API设置”→**收件人**下拉菜单。
2. 点击**管理手机号码列表**。
3. 添加您希望向其发送消息的手机号码（包括您自己的、团队的以及合作测试人员的号码）。Meta会通过短信或WhatsApp向每个号码发送一个6位数的验证码。

在开发模式下最多可添加5个号码。一旦应用进入审核流程，此限制将被取消。

---

## 允许列表（Hermes端）

除了Meta的收件人白名单之外，Hermes还拥有针对不同平台的独立允许列表，用于控制**机器人应处理哪些 incoming消息**。请在`~/.hermes/.env`文件中添加相关配置：

```bash
# Comma-separated phone numbers, country code, no '+' / spaces / dashes
WHATSAPP_CLOUD_ALLOWED_USERS=15551234567,15557654321

# Or allow everyone (only safe in combination with Meta's recipient whitelist)
# WHATSAPP_CLOUD_ALLOW_ALL_USERS=true
```

在设置向导的第6步中即可完成此项配置。若未设置允许列表，**所有传入的消息都将被拒绝**——这是有意为之，旨在防止在接收者白名单放宽后被随机号码调用机器人。

---

## 完善机器人的 WhatsApp 个人资料

WhatsApp 会在聊天界面标题和联系人列表中显示机器人的**名称和头像**。这些内容无法通过 Cloud API 设置，需在 Meta 的 Business Manager 中配置。

当机器人正常运行后，请访问 **[business.facebook.com/wa/manage/phone-numbers](https://business.facebook.com/wa/manage/phone-numbers/)**，点击对应的电话号码，即可看到以下设置项：

| 设置项 | 位置 | 备注 |
|---|---|---|
| **显示名称** | 电话号码页面顶部 | 修改后需经过 Meta 的名称审核流程（约24–48小时）。 |
| **头像** | 电话号码页面顶部 | 需为正方形图片，建议尺寸≥640×640像素，修改后会立即生效。 |
| **简介/描述/网站/邮箱/服务时间/类别** | “编辑个人资料”按钮 | 用户点击机器人名称时，这些信息会显示在信息窗格中，仅用于美化展示。 |
| **已验证徽章**（绿色对勾） | Business Manager → 安全中心 → 开始验证 | 需经过 Meta 独立的商家验证流程。 |

`hermes whatsapp-cloud` 设置向导会在配置完成后输出这些链接。虽然这些设置并非机器人运行的必需条件，但能提升用户在看到机器人时的体验。

---

## 配置参考

所有设置均保存在 `~/.hermes/.env` 文件中。必填值以**粗体**标出。

| 变量 | 默认值 | 描述 |
|---|---|---|
| **`WHATSAPP_CLOUD_PHONE_NUMBER_ID`** | — | 来自 API 设置的15–17位数字标识，**并非**电话号码本身。 |
| **`WHATSAPP_CLOUD_ACCESS_TOKEN`** | — | Meta 访问令牌（以 `EAA` 开头），临时令牌有效期为24小时，系统用户令牌为永久有效。 |
| **`WHATSAPP_CLOUD_APP_SECRET`** | — | 来自“设置 → 基本信息”的32位十六进制字符串，缺少该值会导致传入消息被以503错误拒绝。 |
| **`WHATSAPP_CLOUD_VERIFY_TOKEN`** | — | 用于 GET 请求握手的共享密钥，由设置向导自动生成。 |
| **`WHATSAPP_CLOUD_ALLOWED_USERS`** | — | 用逗号分隔的允许向机器人发送消息的 wa_ids 列表。 |
| `WHATSAPP_CLOUD_ALLOW_ALL_USERS` | `false` | 设置为 `true` 可绕过允许列表限制。 |
| **`WHATSAPP_CLOUD_APP_ID`** | — | 可选，用于未来集成分析功能。 |
| **`WHATSAPP_CLOUD_WABA_ID`** | — | 可选，用于未来集成分析功能。 |
| **`WHATSAPP_CLOUD_WEBHOOK_HOST`** | `0.0.0.0` | Webhook 服务器绑定的接口地址。 |
| **`WHATSAPP_CLOUD_WEBHOOK_PORT`** | `8090` | Webhook 服务器绑定的端口，需与隧道转发的端口一致。 |
| **`WHATSAPP_CLOUD_WEBHOOK_PATH`** | `/whatsapp/webhook` | Meta 发送消息的 URL 路径。 |
| **`WHATSAPP_CLOUD_API_VERSION`** | `v20.0` | Meta Graph API 版本，仅当 Meta 文档推荐使用更高版本时才需修改。 |
| **`WHATSAPP_CLOUD_HOME_CHANNEL`** | — | 用作机器人主通道的 wa_id（用于定时任务等）。 |

你可以同时启用 Baileys（`whatsapp`）和 Cloud（`whatsapp_cloud`）两种适配器，针对不同的电话号码分别使用。

---

## 功能特性

### 接收消息

- **文本消息**——直接传递给智能体。
- **图片**——自动下载并附加到智能体的输入内容中。具备原生视觉功能的模型（如 Claude、GPT-4o、Gemini 等）可直接读取图片；非视觉模型则会收到自动生成的文本描述。
- **语音留言**——自动下载为 `.ogg` 格式，通过你配置的 STT 服务（如本地的 faster-whisper、OpenAI/Nous、Groq 等）进行转录，之后以文本形式传递给智能体。
- **文档**——自动下载。大小不超过100KB、可读取文本的文件（如 `.txt`、`.md`、`.json`、`.py`、`.csv` 等）会直接嵌入智能体的输入内容中，使其无需调用额外工具即可读取；较大文件则会缓存到本地，供智能体的其他工具使用。
- **按钮点击**——当用户点击机器人之前发送的按钮（用于明确选择、确认命令或确认斜杠命令）时，该点击操作会直接路由到对应的处理函数。过期的按钮点击将默认视为普通文本输入。
- **回复上下文**——当用户回复机器人的历史消息时，智能体可将原始消息作为上下文信息获取。

### 发送消息

- **文本**——Markdown 格式会自动转换为 WhatsApp 的特定语法（`**粗体**` → `*粗体*`，`~~删除线~~` → `~删除线~`，标题自动变为粗体，`[链接](url)` → `链接 (url)`）。过长消息会按每4096个字符拆分发送。
- **图片**——支持智能体生成的图片和本地图片文件，均以原生照片附件的形式发送。
- **语音消息**——文本转语音输出会通过 ffmpeg 转换为 WhatsApp 原生的语音留言气泡（绿色波形图）。若未安装 ffmpeg，则会降级为 MP3 音频附件。详情请参见下文“语音消息”部分。
- **视频/文档**——两者均支持，以原生附件形式发送。

### 交互式用户体验

当智能体触发这些交互流程时，Hermes 会使用 WhatsApp 原生的交互式消息功能——即点击式回复按钮，而非要求用户输入数字回复：

- **`clarify` 工具**——多选题会以快速回复按钮（1–3个选项）或点击展开的列表形式（4个以上选项）呈现。选择“✏️ 其他”后，用户可输入自由文本答案，智能体将此内容作为最终处理结果。
- **危险命令审批**——当智能体的终端/代码执行遇到受限命令时，用户会看到 `✅ 批准` / `❌ 拒绝` 按钮，无需手动输入 `/approve` 或 `/deny`。
- **斜杠命令确认**——如 `/reload-mcp` 这类高级命令会显示 `✅ 仅批准一次` / `🔒 始终允许` / `❌ 取消` 按钮。

如果按钮无法正常显示（例如在旧版 WhatsApp 客户端上），所有交互式提示都会自动降级为普通文本，确保功能不受影响。

### 已读回执和正在输入指示

Hermes 会立即确认收到传入消息：

- 你的消息一旦被网关接收，就会显示**蓝色双对勾**。
- 当智能体正在准备回复时，WhatsApp 聊天界面中的机器人名称旁会显示“**正在输入…**”。
- 一旦机器人发出首条回复消息，正在输入指示会自动消失。

这样就能清楚地分辨出机器人何时已看到你的消息，以及何时仍在处理回复。

### 语音消息

WhatsApp 区分“语音留言”（绿色波形图气泡）和普通音频文件附件。两者的区别仅在于编码格式：语音留言需为采用 `opus` 编码的 `audio/ogg` 格式。

Hermes 的文本转语音功能生成的是 MP3 格式。有两种处理方式：

- **系统路径中已安装 ffmpeg**（推荐）——输出的语音消息会经过转换，呈现为标准的语音留言格式。安装方法如下：
  - Windows：`winget install Gyan.FFmpeg`
  - macOS：`brew install ffmpeg`
  - Linux：通过对应包管理器安装
- **未安装 ffmpeg**——输出的语音消息将以 MP3 音频附件形式发送。虽然可以正常播放，但外观上并非语音留言格式。网关日志会记录一次警告信息，以便你知晓。

你可以通过健康检查端点查看网关是否检测到 ffmpeg 的存在：

```bash
curl http://localhost:8090/health
# look for "ffmpeg_present": true
```

## 已知限制

### 24小时对话窗口

Meta仅允许在用户最后一条消息发送后的24小时内发送**自由格式消息**。超出该时间范围后，Meta的API仅接受预先审批过的**消息模板**。

**实际应用中的含义：**

- 反向聊天模式（用户发送私信 → 机器人在24小时内回复 → 用户再次回复……）可永久使用，这涵盖了95%以上的常规机器人使用场景。
- 若通过Cron作业在超过24小时的间隔后向WhatsApp发送消息，将会因Graph错误代码`131047`（“重新互动消息”）而失败。
- 需要超过24小时才能返回结果的**长时间运行的`delegate_task`异步操作**也会出现相同问题。
- 当用户近期未向机器人发送私信时，将外部事件路由至WhatsApp的**Webhook订阅者**也会失败。

Hermes会在其系统提示中向代理发出关于此时间限制的警告，因此模型在安排延迟发送的消息时会主动提及这一点。

目前Hermes尚未实现消息模板支持功能（即用于处理超时发送的替代方案）。如果您需要该功能，请[提交问题](https://github.com/NousResearch/hermes-agent/issues)——该功能已有规划，但仍在等待明确的用户需求信号。

### 群组聊天

Cloud API对群组聊天的支持较为有限（具体能力由Meta控制）。Hermes的`whatsapp_cloud`适配器在v1版本中仅支持**私信聊天**。如果您需要处理群组聊天，请使用Baileys桥接方案。

### 出站消息速率限制

Meta的默认吞吐量为**每个企业电话号码每秒80条消息**，也可选择升级服务。目前Hermes并未在客户端侧强制执行此限制，但极高频率的发送仍可能触及Meta的限制。

---

## 故障排除

### 在Meta控制台中出现“设置验证失败（‘URL无法验证’）”错误

通常由以下原因之一导致：

- **隧道URL错误或已过期**——cloudflared的快速隧道会定期更换。请获取新的URL，并同时更新`.env`文件及Meta控制台中的配置。
- **验证令牌不匹配**——`~/.hermes/.env`文件中`WHATSAPP_CLOUD_VERIFY_TOKEN`字段的值必须与在Meta控制台中输入的值完全一致。请先运行上述curl探测命令，确认本地网关的验证流程能够正常工作。
- **网关未运行**——请检查`hermes gateway`服务是否处于启动状态。
- **未设置应用密钥**——如果没有设置应用密钥，Hermes会以503错误拒绝接收入站POST请求，Meta则会将其解读为“无法验证”。

### `graph error 100`：编号为‘...’的对象不存在

您可能将电话号码（10-11位）误填入了`WHATSAPP_CLOUD_PHONE_NUMBER_ID`字段，而非Meta系统使用的电话号码ID（15-17位内部编号）。请重新检查API设置页面——电话号码ID显示在“发件人”下拉菜单的下方。

虽然现在的向导已包含相关验证功能，但如果您是手动配置的话，了解这一点仍很有帮助。

### `graph error 190`：认证错误

您的访问令牌无效。可能的子代码包括：

- `subcode 463`——令牌已过期。临时令牌的有效期为24小时，请重新生成令牌，或切换为系统用户的永久令牌（参见上文）。
- `subcode 467`——令牌已被撤销或密码已更改，导致其失效。
- 其他190开头的错误——表示生成的令牌缺乏必要的权限。请确保已选中全部三项权限：`business_management`、`whatsapp_business_messaging`和`whatsapp_business_management`。

### `graph error 131047`：重新互动消息

24小时的对话窗口已过期（参见“已知限制”部分）。您可以：

- 要求用户先向机器人发送私信，以重新开启对话窗口；
- 等待Hermes实现消息模板支持功能。

### 接收到的消息出现“媒体元数据获取失败（状态=401）”错误

该错误的根本原因与出站消息相同（`graph error 190`），即访问令牌无效或已过期。请修复令牌问题。

### 机器人的回复显示为原始JSON格式/工具调用信息泄露

常见原因在于为`whatsapp_cloud`配置的工具集缺少代理需要调用的工具。请查看`hermes tools list`，确认平台使用的工具集是否为`hermes-whatsapp`（这是默认的Cloud适配器工具集，与Baileys的相同）。

如果模型输出的文本呈现为工具调用格式而非结构化调用形式，通常说明工具集实际上为空。有关平台与默认工具集的对应关系，请查看`hermes_cli/platforms.py`文件。

### 语音转文字（STT）功能返回空内容/“无法转录”

默认的`stt.provider: local`配置需要先安装`faster-whisper`库。如果您是Nous的订阅用户，可以通过Meta管理的音频网关来实现语音转文字功能：

```bash
hermes config set stt.provider openai
hermes config set stt.use_gateway true
hermes gateway restart
```

该方案使用您的 Nous Portal 访问令牌，无需单独的 OpenAI 密钥。

---

## 安全注意事项

- **将应用密钥视为密码处理**——任何获取到该密钥的人都可以伪造 webhook 请求内容，而 Hermes 会将其误认为是合法请求。
- **验证令牌属于共享密钥**——虽然其泄露造成的危害相对较小（最坏情况下只是有人将自己的 Meta webhook 重新指向其他网址），但仍需避免将其泄露。
- **访问令牌是您机器人的身份标识**——系统用户令牌相当于长期有效的 API 密钥。如果部署环境遭到入侵，应立即更换该令牌。
- **当设置了 `WHATSAPP_CLOUD_APP_SECRET` 时，webhook 接口仅接受已签名请求**——即使在开发阶段也请保持该设置。若未设置，网关会以 HTTP 503 错误拒绝接收请求。
- **`/health` 接口无需身份验证**——由于它仅返回配置是否存在的相关布尔值，而非具体配置内容，因此公开该接口是安全的。不过如果您不想暴露它，也可在反向代理或隧道层进行访问限制。

---

## 与 Baileys 桥接方案的对比

| 对比项 | Baileys（`hermes whatsapp`） | Cloud API（`hermes whatsapp-cloud`） |
|---|---|---|
| 账户类型 | 个人账户 | 商业账户 |
| 设置方式 | 扫描二维码 | 需要 Meta 应用 + WABA + 令牌 |
| 依赖环境 | Node.js + npm | 纯 Python（httpx + aiohttp） |
| 处理流程 | 由 Node 进程管理 | 使用 aiohttp 运行 webhook 服务器 |
| 是否需要公开网址 | 不需要 | 需要 |
| 账户被封风险 | 存在（非官方 API） | 无（官方支持） |
| 数据接收方式 | 通过 Node 桥接轮询 | 通过 Meta 发送 webhook POST 请求 |
| 数据发送方式 | 本地桥接 → Baileys | 通过 HTTPS 发送到 graph.facebook.com |
| 群组支持 | 完全支持 | 仅支持私信（v1版本） |
| 24小时发送限制 | 无限制 | 有严格限制——之后必须使用模板 |
| 语音消息发送 | 原生支持 | 原生支持，否则会回退为 ffmpeg 转换的 MP3格式 |
| 已读回执 | 不支持 | 支持（显示蓝色双对勾） |
| 输入中状态指示 | 不支持 | 支持（收到回复后会自动消失） |
| 交互式按钮 | 仅支持文本选项 | 原生支持（确认、批准、斜杠命令等功能） |
| 生产环境使用 | 存在风险（可能被 Meta 封禁） | 专为生产环境设计 |

大多数用于个人项目的 Hermes 用户更倾向于使用 Baileys。而那些需要构建面向客户的机器人的用户，则更常选择 Cloud API。

---

## 相关资源

- [Meta 官方 WhatsApp Business Cloud API 文档](https://developers.facebook.com/documentation/business-messaging/whatsapp/)——涵盖底层平台、定价策略、应用审核以及 Meta 端的速率限制等权威信息。
- [WhatsApp（Baileys 桥接）设置指南](whatsapp.md)——适用于个人项目的另一种集成方案。
- [消息平台概览](index.md)——一站式了解所有消息集成方式。
