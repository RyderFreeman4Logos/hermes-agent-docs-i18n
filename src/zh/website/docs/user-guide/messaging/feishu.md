---
sidebar_position: 11
title: "Feishu / Lark"
description: "Set up Hermes Agent as a Feishu or Lark bot"
---

# 飞书 / 钉钉集成设置

Hermes Agent 以功能完备的机器人形式与飞书和钉钉深度集成。完成连接后，您既可以通过私信或群聊与该机器人交流，也能在个人聊天界面获取定时任务执行结果；同时还能通过常规网关流程发送文本、图片、音频及文件附件。

该集成支持以下两种连接模式：

- `websocket` —— 推荐模式；由 Hermes 主动建立出站连接，您无需配置公共 webhook 端点
- `webhook` —— 适用于希望飞书/钉钉通过 HTTP 将事件推送到您网关的场景

## Hermes 的响应机制

| 对话场景 | 响应行为 |
|---------|----------|
| 私信 | Hermes 会回复每一条消息。 |
| 群聊 | 仅当群聊中提及该机器人时，Hermes 才会作出回应。 |
| 共享群聊 | 默认情况下，共享群聊内的每个用户拥有独立的会话历史记录。 |

此共享群聊的配置规则可通过 `config.yaml` 文件进行控制：

```yaml
group_sessions_per_user: true
```

仅当您明确希望每个聊天窗口只保留一个共享对话时，才将其设置为 `false`。

## 第一步：创建飞书/企业微信应用

### 推荐方式：扫描创建（仅需一条命令）

```bash
hermes gateway setup
```

选择**飞书 / 钉钉**，然后使用飞书或钉钉手机应用扫描二维码。Hermes将自动创建一个具备相应权限的机器人应用，并保存相关凭证。

### 备选方案：手动设置

如果无法通过扫描创建，向导会切换为手动输入方式：

1. 打开飞书或钉钉开发者控制台：
   - 飞书：[https://open.feishu.cn/](https://open.feishu.cn/)
   - 钉钉：[https://open.larksuite.com/](https://open.larksuite.com/)
2. 创建一个新应用。
3. 在**凭证与基本信息**页面，复制**应用ID**和**应用密钥**。
4. 为该应用开启**机器人**功能。
5. 运行 `hermes gateway setup` 命令，选择**飞书 / 钉钉**，并在提示时输入相应凭证。

:::warning
请务必妥善保管应用密钥，任何获取到该密钥的人都可以冒充您的应用。
:::

### 配置权限

在飞书开发者控制台中，进入**权限管理**页面并添加以下权限范围。您也可以在权限管理页面批量导入这些权限。

**必需的权限：**

| 权限范围 | 用途 |
|---------|------|
| `im:message` | 接收并读取消息 |
| `im:message:send_as_bot` | 以机器人身份发送消息 |
| `im:resource` | 访问用户发送的图片、文件和音频 |
| `im:chat` | 访问聊天/群组元数据 |
| `im:chat:readonly` | 读取聊天列表及成员信息 |

**推荐使用的权限（以实现完整功能）：**

| 权限范围 | 用途 |
|---------|------|
| `im:message.reactions:readonly` | 接收表情反应事件 |
| `admin:app.info:readonly` | 自动识别@提及时的机器人身份 |
| `contact:user.id:readonly` | 解析用户ID以便进行白名单匹配 |

### 配置事件

在**事件与回调**页面中：

1. 将连接模式设置为**长连接（WebSocket，推荐）**，或配置Webhook地址。
2. 在**事件配置**部分，订阅以下事件：
   - `im.message.receive_v1` —— 接收消息所必需。

### 发布应用

配置完权限和事件后，前往**版本管理**页面发布应用的新版本。只有当版本被发布并通过审核后，权限才会生效（对于企业版应用，可能还需要管理员批准）。

## 第2步：选择连接模式

### 推荐方案：WebSocket模式

当Hermes运行在您的笔记本电脑、工作站或私有服务器上时，建议使用WebSocket模式。此模式下无需公共URL，官方钉钉SDK会自动建立并维持持久的出站WebSocket连接，并具备自动重连功能。

```bash
FEISHU_CONNECTION_MODE=websocket
```

**要求：** 必须安装 `websockets` Python 包。SDK 会内部处理连接生命周期、心跳检测以及自动重连功能。

**工作原理：** 该适配器会在后台执行线程中运行 Lark SDK 的 WebSocket 客户端。接收到的事件（消息、表情反应、卡片操作等）会被发送到主 asyncio 循环中。当连接断开时，SDK 会尝试自动重新连接。

### 可选功能：Webhook 模式

仅当您已在可访问的 HTTP 端点后运行 Hermes 时，才可使用 Webhook 模式。

```bash
FEISHU_CONNECTION_MODE=webhook
```

在 Webhook 模式下，Hermes 会通过 `aiohttp` 启动一个 HTTP 服务器，并在以下地址提供飞书接口服务：

```text
/feishu/webhook
```

**要求：** 必须已安装 Python 包 `aiohttp`。

您可以自定义 webhook 服务器的绑定地址和路径：

```bash
FEISHU_WEBHOOK_HOST=127.0.0.1   # default: 127.0.0.1
FEISHU_WEBHOOK_PORT=8765         # default: 8765
FEISHU_WEBHOOK_PATH=/feishu/webhook  # default: /feishu/webhook
```

当飞书发送 URL 验证挑战请求（`type: url_verification`）时，Webhook 会自动响应，从而让您在飞书开发者控制台完成订阅配置。若设置了 `FEISHU_VERIFICATION_TOKEN`，则挑战请求必须基于该令牌才能通过——缺少或不匹配令牌的请求将被拒绝，这样未经身份验证的远程方就无法通过回显攻击者控制的挑战数据来证明其对端点的控制权。

## 第 3 步：配置 Hermes

### 方案 A：交互式设置

```bash
hermes gateway setup
```

选择**飞书 / 雨露**，然后填写提示词。

### 方案 B：手动配置

在 `~/.hermes/.env` 文件中添加以下内容：

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=secret_xxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket

# Optional but strongly recommended
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
FEISHU_HOME_CHANNEL=oc_xxx
```

`FEISHU_DOMAIN` 支持以下值：

- `feishu`，用于飞书中国版
- `lark`，用于飞书国际版

## 第 4 步：启动网关

```bash
hermes gateway
```

随后，通过飞书或企业微信中的机器人发送消息，以确认连接已正常建立。

## 主聊天频道

在飞书或企业微信的聊天窗口中使用 `/set-home` 命令，即可将其设为用于存储定时任务结果及跨平台通知的主频道。

您也可以预先进行配置：

```bash
FEISHU_HOME_CHANNEL=oc_xxx
```

## 安全性

### 用户白名单

在正式环境中使用时，需设置飞书开放ID的白名单：

```bash
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy
```

如果将允许列表留空，任何能够访问该机器人的用户都可能使用它。在群组聊天中，系统会在处理消息之前，先根据发送者的 open_id 来核对允许列表。

### Webhook 加密密钥

在以 Webhook 模式运行时，应设置一个加密密钥，以便对传入的 Webhook 数据进行签名验证：

```bash
FEISHU_ENCRYPT_KEY=your-encrypt-key
```

该密钥位于飞书应用配置的**事件订阅**板块中。设置该密钥后，适配器会使用签名算法对每一条 Webhook 请求进行验证：

```
SHA256(timestamp + nonce + encrypt_key + body)
```

系统会通过时间安全型比较方式，将计算出的哈希值与 `x-lark-signature` 标头进行比对。对于签名无效或缺失的请求，系统会返回 HTTP 401 错误码予以拒绝。

:::提示
在 WebSocket 模式下，签名验证由 SDK 自身完成，因此 `FEISHU_ENCRYPT_KEY` 是可选的。而在 Webhook 模式下，为了确保生产环境的安全性，强烈建议使用该密钥。
:::

### 验证令牌

这是一种额外的认证机制，用于检查 Webhook 请求载荷中的 `token` 字段：

```bash
FEISHU_VERIFICATION_TOKEN=your-verification-token
```

该令牌也存在于您飞书应用中的**事件订阅**板块中。一旦设置，所有传入的 webhook 数据包在其 `header` 对象中都必须包含对应的 `token`。若令牌不匹配，系统将返回 HTTP 401 错误并拒绝处理。

为增强安全性，可同时使用 `FEISHU_ENCRYPT_KEY` 和 `FEISHU_VERIFICATION_TOKEN` 这两项配置。

## 群聊消息策略

`FEISHU_GROUP_POLICY` 环境变量用于控制 Hermes 在群聊中的响应行为及方式：

```bash
FEISHU_GROUP_POLICY=allowlist   # default
```

| 值 | 行为 |
|-------|----------|
| `open` | Hermes 会响应任何群组中任意用户发送的@提及。 |
| `allowlist` | Hermes 仅响应 `FEISHU_ALLOWED_USERS` 中列出的用户发送的@提及。 |
| `disabled` | Hermes 完全忽略所有群组消息。 |

在所有模式下，消息被处理之前，必须先在群组中明确@提及（或@所有人）该机器人。而私信则始终无需经过此步骤。

如需让Hermes无需@提及即可读取所有群组消息，可设置 `FEISHU_REQUIRE_MENTION=false`：

```bash
FEISHU_REQUIRE_MENTION=false
```

如需实现单次对话级别的控制，可在 `group_rules` 条目中设置 `require_mention` 参数——详情请参阅下文的[按群组访问控制](#per-group-access-control)。

### 机器人身份信息

Hermes 会在启动时自动检测机器人的 `open_id` 和显示名称。仅在自动检测无法连接到飞书 API，或您的应用使用租户级用户 ID 时，才需要手动设置这些信息：

```bash
FEISHU_BOT_OPEN_ID=ou_xxx     # only when auto-detection fails
FEISHU_BOT_USER_ID=xxx        # required if your app uses sender_id_type=user_id
FEISHU_BOT_NAME=MyBot         # only when auto-detection fails
```

## 机器人间消息传递

默认情况下，Hermes 会忽略其他机器人发送的消息。当您希望 Hermes 参与应用到应用之间的流程编排，或接收同一组内其他机器人发送的通知时，需启用机器人间消息传递功能。

```bash
FEISHU_ALLOW_BOTS=mentions   # default: none
```

| 值 | 行为 |
|-------|----------|
| `none` | 忽略来自其他机器人的所有消息（默认值）。 |
| `mentions` | 仅当对方机器人@提及Hermes时才接受消息。 |
| `all` | 接受所有对方机器人的消息。 |

该设置也可通过`config.yaml`中的`feishu.allow_bots`进行配置（若两者均设置，则以环境变量值为准）。

对方机器人无需添加到`FEISHU_ALLOWED_USERS`列表中——该允许列表仅适用于人类发送者。

如需显示对方机器人的名称，需授予`application:bot.basic_info:read`权限；即便没有此权限，对方机器人仍能正常路由消息，但会以它们的`open_id`形式显示。  

## 交互式卡片操作

当用户点击按钮或与机器人发送的交互式卡片进行互动时，适配器会将这些操作转换为合成的`/card`命令事件：

- 按钮点击会被转换为：`/card button {"key": "value", ...}`  
- 卡片定义中的操作`value`载荷会以JSON格式包含在内。  
- 为防止重复处理，卡片操作会在15分钟的时间窗口内去重。

由网关驱动的更新提示会使用Feishu原生的“是”/“否”卡片，而不会回退到纯文本回复。当`hermes update --gateway`需要用户确认时，适配器会将用户选择的答案记录在Hermes的`.update_response`文件中，并用确定的处理状态替换卡片内容。

卡片操作事件以`MessageType.COMMAND`类型发送，因此会经过正常的命令处理流程。

**命令审批**也是通过相同机制实现的——当智能体需要执行危险命令时，它会发送一张包含“仅允许一次”/“会话有效”/“始终允许”/“拒绝”按钮的交互式卡片。用户点击某个按钮后，卡片操作回调会将审批结果反馈给智能体。  

### Feishu应用所需的配置

在Feishu开发者控制台中，交互式卡片需要完成**三个**配置步骤。若缺少任意一步，当用户点击卡片按钮时都会出现**200340**错误。

1. **订阅卡片操作事件：**  
   在“事件订阅”中，将`card.action.trigger`添加到您已订阅的事件列表中。

2. **启用交互式卡片功能：**  
   在“应用功能 > 机器人”中，确保已开启“交互式卡片”开关。这告诉Feishu您的应用可以接收卡片操作回调。

3. **配置卡片请求URL（仅限Webhook模式）：**  
   在“应用功能 > 机器人 > 消息卡片请求URL”中，将URL设置为与事件Webhook相同的端点（例如`https://your-server:8765/feishu/webhook`）。在WebSocket模式下，SDK会自动处理此功能。

:::warning
若未完成以上三个步骤，Feishu虽能成功*发送*交互式卡片（仅发送操作需要`im:message:send`权限），但点击任何按钮都会返回200340错误。卡片看似可以正常使用——只有在用户与其互动时才会出现错误。
:::

## 文档评论智能回复

除了聊天功能外，该适配器还能回复留在**Feishu/Lark文档**中的`@`提及。当用户在文档上添加评论（无论是选中部分文本还是对整篇文档发表评论）并@提及机器人时，Hermes会读取该文档及相关的评论线程，然后在评论线程中直接生成LLM生成的回复。

该功能基于`drive.notice.comment_add_v1`事件实现，处理流程如下：

- 同步获取文档内容和评论时间线（整篇文档的评论线程最多20条，部分文本选中的评论线程最多12条）。
- 使用仅针对该评论会话的`feishu_doc` + `feishu_drive`工具集来运行智能体。
- 将回复内容按4000字符为单位分块，并以带有序列号的回复形式返回。
- 每个文档的会话记录会被缓存1小时，最多保存50条评论，以便对同一文档的后续评论保持上下文连贯性。  

### 三级访问控制

文档评论回复采用**显式授权**机制——不存在默认允许所有操作的模式。权限按以下顺序判定（优先匹配项生效，按字段逐一检查）：

1. **精确匹配文档**——针对特定文档令牌的规则。  
2. **通配符匹配**——匹配特定文档模式的规则。  
3. **顶层规则**——工作空间的默认规则。  

每条规则支持两种策略：

- **`allowlist`**——静态的用户/租户列表。  
- **`pairing`**——静态列表与运行时审批列表的结合。适用于需要管理员实时授权的场景。

规则存储在`~/.hermes/feishu_comment_rules.json`文件中（`pairing`类型的授权规则则存储在`~/.hermes/feishu_comment_pairing.json`文件中），并采用基于修改时间戳的热重载机制——只需对文件进行编辑，下次有评论事件时即可生效，无需重启网关。

CLI：

```bash
# Inspect current rules and pairing state
python -m gateway.platforms.feishu_comment_rules status

# Simulate an access check for a specific doc + user
python -m gateway.platforms.feishu_comment_rules check <fileType:fileToken> <user_open_id>

# Manage pairing grants at runtime
python -m gateway.platforms.feishu_comment_rules pairing list
python -m gateway.platforms.feishu_comment_rules pairing add <user_open_id>
python -m gateway.platforms.feishu_comment_rules pairing remove <user_open_id>
```

### 必需的飞书应用配置

在已授予的聊天/卡片权限基础上，还需添加驱动器评论事件：

- 在**事件订阅**中订阅 `drive.notice.comment_add_v1`。
- 授予 `docs:doc:readonly` 和 `drive:drive:readonly` 权限，以便处理程序能够读取文档内容。

## 会议邀请事件

您可以像邀请人类参与者一样，将 Hermes Feishu/Lark 机器人邀请到视频会议中。当机器人收到会议邀请事件后，Hermes 可以自动启动一个代理轮次，尝试加入该会议。

该功能基于 `vc.bot.meeting_invited_v1` 事件实现，处理流程如下：

- 用户将机器人邀请至 Feishu/Lark 视频会议。
- Feishu/Lark 向 Hermes 发送会议邀请事件。
- Hermes 提取邀请人、会议主题及会议编号。
- 如果该邀请人已在常规网关白名单或配对策略中获得授权，代理将获取会议编号并尝试自动加入。
- 如果邀请格式错误或代理无法加入，Hermes 会忽略该事件，或向邀请人发送简短说明。

缺少邀请人和 `meeting_no` 的无效邀请将被忽略。

### 必需的飞书应用配置

在已授予的聊天/卡片权限基础上，还需添加视频会议邀请事件：

- 在**事件订阅**中订阅 `vc.bot.meeting_invited_v1`。
- 启用 Feishu/Lark 开发者控制台为该事件提示的视频会议权限范围。
- 保持 `im:message` 和 `im:message:send_as_bot` 启用状态，以便 Hermes 能够向邀请人回复。
- 确保网关用户白名单或配对策略已授权该邀请人。会议邀请不会绕过常规的网关访问检查。

## 媒体支持

### 接收端

适配器可接收并缓存用户发送的以下媒体类型：

| 类型 | 扩展名 | 处理方式 |
|------|--------|----------|
| **图片** | .jpg、.jpeg、.png、.gif、.webp、.bmp | 通过飞书 API 下载并本地缓存 |
| **音频** | .ogg、.mp3、.wav、.m4a、.aac、.flac、.opus、.webm | 下载并缓存；小型文本文件会自动提取 |
| **视频** | .mp4、.mov、.avi、.mkv、.webm、.m4v、.3gp | 作为文档下载并缓存 |
| **文件** | .pdf、.doc、.docx、.xls、.xlsx、.ppt、.pptx 等 | 作为文档下载并缓存 |

富文本（帖子）消息中的媒体，包括内嵌图片和文件附件，也会被提取并缓存。

对于小型纯文本文档（.txt、.md），其内容会自动嵌入到消息文本中，这样代理无需额外工具即可直接读取。

### 发送端

| 方法 | 发送内容 |
|------|----------|
| `send` | 文本或富文本帖子消息（根据 Markdown 内容自动识别） |
| `send_image` / `send_image_file` | 将图片上传至飞书，然后以原生图片气泡形式发送（可附带可选标题） |
| `send_document` | 将文件上传至飞书 API，然后作为文件附件发送 |
| `send_voice` | 将音频文件作为飞书文件附件上传 |
| `send_video` | 上传视频并以原生媒体消息形式发送 |
| `send_animation` | GIF 图像会被降级为文件附件（飞书不支持原生 GIF 气泡） |

文件上传会根据扩展名自动路由：

- `.ogg`、`.opus` → 作为 `opus` 音频上传
- `.mp4`、.mov`、.avi`、.m4v` → 作为 `mp4` 媒体上传
- `.pdf`、.doc(x)`、.xls(x)`、.ppt(x)` → 按其文档类型上传
- 其他所有类型 → 作为通用流式文件上传

## Markdown 渲染与回退机制

当发送的文本包含 Markdown 格式（标题、加粗、列表、代码块、链接等）时，适配器会自动将其作为带有嵌入 `md` 标签的飞书**帖子**消息发送，而非纯文本。这样可在飞书客户端实现丰富的内容渲染。

如果飞书 API 拒绝处理该帖子内容（例如由于不支持的 Markdown 结构），适配器会自动回退为发送已去除 Markdown 格式的纯文本。这种两阶段回退机制可确保消息始终能被送达。

未检测到 Markdown 格式的纯文本消息，则以简单的 `text` 消息类型发送。

## 处理状态反应

在代理处理消息时，机器人会在您的消息上显示“正在输入”反应。当回复到达后，该反应会被清除；如果处理失败，则会替换为“叉号”反应。

如需关闭此功能，可设置 `FEISHU_REACTIONS=false`。

## 流量突发保护与批量处理

适配器具备防抖功能，可应对大量消息的快速发送，避免给代理带来过重负担：

### 文本批量处理

当用户连续发送多条文本消息时，这些消息会在被发送之前合并为一个事件：

| 设置项 | 环境变量 | 默认值 |
|--------|----------|--------|
| 静默间隔时间 | `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | 0.6秒 |
| 每批最大消息数 | `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | 8条 |
| 每批最大字符数 | `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | 4000字符 |

### 媒体批量处理

连续快速发送的多个媒体附件（例如拖动上传多张图片）也会被合并为一个事件：

| 设置项 | 环境变量 | 默认值 |
|--------|----------|--------|
| 静默间隔时间 | `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | 0.8秒 |

### 单聊串行处理

为保持对话连贯性，同一聊天中的消息会按顺序逐条处理。每个聊天都有独立的处理锁，因此不同聊天的消息可以同时处理。

## 频率限制（Webhook 模式）

在 Webhook 模式下，适配器会实施基于 IP 的频率限制，以防止滥用：

- **时间窗口**：60秒滑动窗口
- **限制值**：每个（app_id、路径、IP）组合在每个窗口内的请求次数为120次
- **跟踪上限**：最多可跟踪4096个唯一键值，以避免内存无限增长

超过限制的请求会收到 HTTP 429（请求过多）响应。

### Webhook 异常检测

适配器会记录每个 IP 地址连续出现的错误响应次数。如果在6小时窗口内同一 IP 连续出现25次错误，系统会记录警告信息。这有助于识别配置错误的客户端或探测行为。

其他 Webhook 安全措施包括：
- **请求体大小限制**：最大1 MB
- **请求体读取超时时间**：30秒
- **Content-Type 强制要求**：仅接受 `application/json` 格式

## WebSocket 调优

在使用 `websocket` 模式时，您可以自定义重新连接和心跳检测的行为：

```yaml
platforms:
  feishu:
    extra:
      ws_reconnect_interval: 120   # Seconds between reconnect attempts (default: 120)
      ws_ping_interval: 30         # Seconds between WebSocket pings (optional; SDK default if unset)
```

| 设置项 | 配置键 | 默认值 | 描述 |
|---------|-----------|---------|-------------|
| 重连间隔 | `ws_reconnect_interval` | 120秒 | 每次尝试重连之间的等待时间 |
| Ping间隔 | `ws_ping_interval` | _(SDK默认值)_ | WebSocket保持连接的Ping发送频率 |

## 按群组访问控制

除了全局的`FEISHU_GROUP_POLICY`之外，您还可以通过config.yaml中的`group_rules`为每个群聊设置更细粒度的规则：

```yaml
platforms:
  feishu:
    extra:
      default_group_policy: "open"     # Default for groups not in group_rules
      admins:                          # Users who can manage bot settings
        - "ou_admin_open_id"
      group_rules:
        "oc_group_chat_id_1":
          policy: "allowlist"          # open | allowlist | blacklist | admin_only | disabled
          allowlist:
            - "ou_user_open_id_1"
            - "ou_user_open_id_2"
        "oc_group_chat_id_2":
          policy: "admin_only"
        "oc_group_chat_id_3":
          policy: "blacklist"
          blacklist:
            - "ou_blocked_user"
        "oc_free_chat":
          policy: "open"
          require_mention: false       # overrides FEISHU_REQUIRE_MENTION for this chat
```

| 策略 | 描述 |
|------|------|
| `open` | 组内的任何人都可以使用该机器人 |
| `allowlist` | 仅组内`allowlist`列表中的用户可以使用该机器人 |
| `blacklist` | 除组内`blacklist`列表中的用户外，其他所有人均可使用该机器人 |
| `admin_only` | 仅全局`admins`列表中的用户才能在此组中使用该机器人 |
| `disabled` | 机器人会忽略该组内的所有消息 |

在`group_rules`条目中设置`require_mention: false`，即可免去该特定聊天场景下的@提及要求。若未设置此参数，则该聊天会沿用全局的`FEISHU_REQUIRE_MENTION`值。

未在`group_rules`中列出的群组将默认采用`default_group_policy`（其值为`FEISHU_GROUP_POLICY`的默认值）。

## 去重机制

系统通过具有24小时有效期的消息ID来实现传入消息的去重。去重状态会持久保存在`~/.hermes/feishu_seen_message_ids.json`文件中，以便在重启后继续使用。

| 参数 | 环境变量 | 默认值 |
|------|----------|--------|
| 缓存大小 | `HERMES_FEISHU_DEDUP_CACHE_SIZE` | 2048条记录 |

## 所有环境变量

| 变量 | 是否必填 | 默认值 | 描述 |
|------|----------|--------|------|
| `FEISHU_APP_ID` | ✅ | — | Feishu/Lark应用ID |
| `FEISHU_APP_SECRET` | ✅ | — | Feishu/Lark应用密钥 |
| `FEISHU_DOMAIN` | — | `feishu` | `feishu`（中国区）或`lark`（国际版） |
| `FEISHU_CONNECTION_MODE` | — | `websocket` | `websocket`或`webhook` |
| `FEISHU_ALLOWED_USERS` | — | _(空)_ | 用于用户白名单的、以逗号分隔的open_id列表 |
| `FEISHU_ALLOW_BOTS` | — | `none` | 是否接受其他机器人的消息：`none`、`mentions`或`all` |
| `FEISHU_REQUIRE_MENTION` | — | `true` | 群组消息是否必须@提及该机器人 |
| `FEISHU_HOME_CHANNEL` | — | — | 用于定时任务/通知输出的聊天ID |
| `FEISHU_ENCRYPT_KEY` | — | _(空)_ | 用于验证Webhook签名 的加密密钥 |
| `FEISHU_VERIFICATION_TOKEN` | — | _(空)_ | 用于验证Webhook请求内容的令牌 |
| `FEISHU_GROUP_POLICY` | — | `allowlist` | 群组消息策略：`open`、`allowlist`、`disabled` |
| `FEISHU_BOT_OPEN_ID` | — | _(空)_ | 机器人的open_id（用于@提及检测） |
| `FEISHU_BOT_USER_ID` | — | _(空)_ | 机器人的user_id（用于@提及检测） |
| `FEISHU_BOT_NAME` | — | _(空)_ | 机器人的显示名称（用于@提及检测） |
| `FEISHU_WEBHOOK_HOST` | — | `127.0.0.1` | Webhook服务器绑定地址 |
| `FEISHU_WEBHOOK_PORT` | — | `8765` | Webhook服务器端口 |
| `FEISHU_WEBHOOK_PATH` | — | `/feishu/webhook` | Webhook端点路径 |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | — | `2048` | 最大需跟踪的去重消息ID数量 |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` | — | `0.6` | 文本批量发送的防抖间隔时间 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_MESSAGES` | — | `8` | 每个文本批次允许合并的最大消息数 |
| `HERMES_FEISHU_TEXT_BATCH_MAX_CHARS` | — | `4000` | 每个文本批次允许合并的最大字符数 |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | — | `0.8` | 媒体文件批量发送的防抖间隔时间 |

WebSocket及针对各群组的访问控制设置，可通过`config.yaml`文件中的`platforms.feishu.extra`部分进行配置（详情参见上文[WebSocket调优](#websocket-tuning)与[按群组访问控制](#per-group-access-control)章节）。

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `lark-oapi未安装` | 安装相应SDK：`pip install lark-oapi` |
| `websockets未安装；无法使用websocket模式` | 安装websockets库：`pip install websockets` |
| `aiohttp未安装；无法使用webhook模式` | 安装aiohttp库：`pip install aiohttp` |
| `FEISHU_APP_ID或FEISHU_APP_SECRET未设置` | 设置这两个环境变量，或通过`hermes gateway setup`进行配置 |
| `已有其他本地Hermes网关正在使用该Feishu应用ID` | 一次只能有一个Hermes实例使用同一个应用ID，请先停止其他实例 |
| 机器人在群组中无响应 | 确保已对机器人进行@提及，检查`FEISHU_GROUP_POLICY`设置；若策略为`allowlist`，还需确认发送者已在`FEISHU_ALLOWED_USERS`列表中 |
| `Webhook被拒绝：验证令牌无效` | 确保`FEISHU_VERIFICATION_TOKEN`与你在Feishu应用的事件订阅配置中的令牌一致 |
| `Webhook被拒绝：签名无效` | 确保`FEISHU_ENCRYPT_KEY`与Feishu应用配置中的加密密钥一致 |
| 发送的消息显示为纯文本 | 说明Feishu API拒绝了该发送内容，这是正常的回退机制，可查看日志获取详细信息 |
| 机器人未收到图片/文件 | 需为你的Feishu应用授予`im:message`和`im:resource`权限范围 |
| 无法自动检测到机器人身份 | 通常是由于网络问题导致无法访问Feishu的机器人信息接口，可临时手动设置`FEISHU_BOT_OPEN_ID`和`FEISHU_BOT_NAME`作为解决方案 |
| 启用`FEISHU_ALLOW_BOTS`后仍忽略其他机器人的消息 | 当前Hermes尚未能识别自身身份，需设置`FEISHU_BOT_OPEN_ID`（如果你的应用使用`sender_id_type=user_id`，还需设置`FEISHU_BOT_USER_ID`） |
| 其他机器人显示为`ou_xxxxxx`而非名称形式 | 需为应用授予`application:bot.basic_info:read`权限范围 |
| 点击审批按钮时出现错误200340 | 需在Feishu开发者控制台启用**交互式卡片**功能，并配置**卡片请求URL**，详情参见上文[必需的Feishu应用配置](#required-feishu-app-configuration) |
| `Webhook请求速率限制被触发` | 同一IP地址的请求频率超过每分钟120次，这通常是由于配置错误或存在循环请求导致的 |

## 工具集

Feishu / Lark使用`hermes-feishu`平台预设，该预设包含与Telegram及其他基于网关的消息平台相同的核心功能工具。
