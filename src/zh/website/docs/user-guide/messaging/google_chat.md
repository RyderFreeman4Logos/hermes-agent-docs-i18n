---
sidebar_position: 12
title: "Google Chat"
description: "Set up Hermes Agent as a Google Chat bot using Cloud Pub/Sub"
---

# Google Chat 集成设置

将 Hermes Agent 作为机器人连接到 Google Chat。该集成使用 Cloud Pub/Sub 的拉取订阅机制来接收传入事件，同时借助 Chat REST API 发送消息。其工作原理与 Slack 的 Socket 模式或 Telegram 的长轮询模式类似：您的 Hermes 进程无需公共 URL、隧道或 TLS 证书，只需通过订阅进行连接、身份验证并监听消息——这与 Telegram 机器人通过令牌监听消息的方式相同。

> 运行 `hermes gateway setup` 并选择 **Google Chat**，即可获得逐步指导。

:::注意 Workspace 版本
Google Chat 是 Google Workspace 的组成部分。您可以使用此集成搭配个人 Workspace（通过 Google 注册的 `@yourdomain.com` 域名）或拥有应用发布权限的工作 Workspace。仅支持 Gmail 的账户无法托管 Chat 应用。
:::

## 概览

| 组件 | 值 |
|------|-----|
| **库** | `google-cloud-pubsub`、`google-api-python-client`、`google-auth` |
| **传入消息传输方式** | Cloud Pub/Sub 拉取订阅（无公共端点） |
| **传出消息传输方式** | Chat REST API (`chat.googleapis.com`) |
| **身份验证方式** | 具有 `roles/pubsub.subscriber` 权限的服务账户 JSON 文件 |
| **用户识别方式** | Chat 资源名称 (`users/{id}`) + 邮箱地址 |

---

## 第 1 步：创建或选择 GCP 项目

您需要一个 Google Cloud 项目来托管 Pub/Sub 主题。如果尚未创建，请访问 [console.cloud.google.com](https://console.cloud.google.com) 进行创建——个人账户可享受免费套餐，足以满足机器人的流量需求。

记下项目 ID（例如 `my-chat-bot-123`），后续所有步骤都将用到它。

---

## 第 2 步：启用两个 API

在控制台导航至 **APIs & Services → Library**，然后启用以下 API：

- **Google Chat API**
- **Cloud Pub/Sub API**

对于个人机器人产生的常规流量，这两个 API 均为免费服务。

---

## 第 3 步：创建服务账户

进入 **IAM & Admin → Service Accounts → Create Service Account**。

- 名称：`hermes-chat-bot`
- 跳过“授予此服务账户项目访问权限”步骤。只需为特定订阅配置 IAM 权限即可——切勿授予项目级的 Pub/Sub 角色。

创建完成后，打开该服务账户，进入 **Keys → Add Key → Create new key → JSON**，下载生成的文件。将其保存在只有 Hermes 能读取的位置（例如 `~/.hermes/google-chat-sa.json`，并设置权限为 `chmod 600`）。

:::警告 不存在“Chat Bot Caller”角色
常见的错误是试图寻找特定的 Chat IAM 角色并在项目级别授予该权限。实际上这样的角色并不存在。Chat 机器人的权限来源于其在特定空间中的安装，而非 IAM 设置。您的服务账户只需在下一步创建的订阅中拥有 Pub/Sub 订阅者权限即可。
:::

---

## 第 4 步：创建 Pub/Sub 主题和订阅

进入 **Pub/Sub → Topics → Create topic**。

- 主题 ID：`hermes-chat-events`
- 其他选项保持默认值。

创建完成后，主题详情页会显示 **Subscriptions** 选项卡。在此创建一个订阅：

- 订阅 ID：`hermes-chat-events-sub`
- 传输类型：**Pull**
- 消息保留时间：**7 天**（这样在 Hermes 重启后消息不会丢失）
- 其他选项保持默认值。

---

## 第 5 步：为主题配置 IAM 绑定（非常重要）

在**主题**层面（而非订阅层面）添加一个 IAM 主体：

- 主体：`chat-api-push@system.gserviceaccount.com`
- 角色：`Pub/Sub Publisher`

如果没有此配置，Google Chat 将无法向您的主题发布事件，您的机器人也就无法收到任何消息。

---

## 第 6 步：为订阅配置 IAM 绑定

在**订阅**层面，将您自己的服务账户添加为主体：

- 主体：`hermes-chat-bot@<your-project>.iam.gserviceaccount.com`
- 角色：`Pub/Sub Subscriber`

同时为该订阅授予 `Pub/Sub Viewer` 权限——Hermes 在启动时会调用 `subscription.get()` 方法来检查连接是否正常。

---

## 第 7 步：配置 Chat 应用

进入 **APIs & Services → Google Chat API → Configuration**。

- **应用名称**：您希望用户看到的名称（使用 “Hermes” 作为名称较为合适）。
- **头像 URL**：任何公开的 PNG 图片（Google 提供了一些默认图片）。
- **描述**：显示在应用目录中的简短说明。
- **功能选项**：启用 **接收一对一消息** 以及 **加入空间并参与群组对话**。
- **连接设置**：选择 **Cloud Pub/Sub**，然后输入主题名称 `projects/<your-project>/topics/hermes-chat-events`。
- **可见性**：限制在您的 Workspace 内部（或特定用户范围内）——测试期间请勿向所有人公开发布消息。

保存设置。

---

## 第 8 步：在测试空间中安装机器人

在浏览器中打开 Google Chat。通过 **+ New Chat** 菜单搜索您的应用名称，开始与其进行私信交流。首次发送消息时，Google 会发送一个 `ADDED_TO_SPACE` 事件，Hermes 会利用该事件缓存机器人的 `users/{id}` 信息，以便实现自我消息过滤功能。

---

## 第 9 步：配置 Hermes

在 `~/.hermes/.env` 文件中添加 Google Chat 相关的配置内容：

```bash
# Required
GOOGLE_CHAT_PROJECT_ID=my-chat-bot-123
GOOGLE_CHAT_SUBSCRIPTION_NAME=projects/my-chat-bot-123/subscriptions/hermes-chat-events-sub
GOOGLE_CHAT_SERVICE_ACCOUNT_JSON=/home/you/.hermes/google-chat-sa.json

# Authorization — paste the emails of people allowed to talk to the bot
GOOGLE_CHAT_ALLOWED_USERS=you@yourdomain.com,coworker@yourdomain.com

# Optional
GOOGLE_CHAT_HOME_CHANNEL=spaces/AAAA...         # default delivery destination for cron jobs
GOOGLE_CHAT_MAX_MESSAGES=1                      # Pub/Sub FlowControl; 1 serializes commands per session
GOOGLE_CHAT_MAX_BYTES=16777216                  # 16 MiB — cap on in-flight message bytes
```

项目 ID 会回退为 `GOOGLE_CLOUD_PROJECT`，而 SA 路径则会回退为 `GOOGLE_APPLICATION_CREDENTIALS`——您可以根据个人偏好选择使用其中任意一种约定。

请安装 Google Chat 适配器所需的依赖项（目前暂未发布专门的 Hermes 相关依赖，可直接安装这些依赖）：

```bash
pip install google-cloud-pubsub google-api-python-client google-auth google-auth-oauthlib
```

启动网关：

```bash
hermes gateway
```

您应该会看到类似如下的日志行：

```
[GoogleChat] Connected; project=my-chat-bot-123, subscription=<redacted>,
             bot_user_id=users/XXXX, flow_control(msgs=1, bytes=16777216)
```

在测试私信中发送“hola”。机器人会先发布一个“Hermes正在思考中…”的提示，随后直接用真实回复替换该消息——不会出现“消息已删除”的标记。

---

## 格式与功能

Google Chat仅支持部分Markdown格式：

| 支持 | 不支持 |
|------|--------|
| `*加粗*`、`_斜体_`、`~删除线~`、`` `代码` `` | 标题、列表 |
| 通过URL插入内联图片 | 交互式卡片v2按钮（该网关的v1版本） |
| 原生文件附件（需在 `/setup-files` 步骤之后操作——见第10步） | 原生语音笔记/环形视频笔记 |

机器人的系统提示中包含针对Google Chat的说明，使其知晓这些限制并避免使用无法显示的格式。

消息大小限制：每条消息最多4000个字符。过长的机器人回复会自动拆分到多条消息中。

主题串支持：当用户在主题串内回复时，Hermes会识别`thread.name`并将回复发布到同一主题串中，因此每个主题串都会拥有独立的Hermes会话。

---

## 第10步：原生附件传输（可选）

默认情况下，机器人可以发送文本、通过URL插入内联图片，以及下载音频/视频/文档的卡片。若要传输**原生**Chat附件——即类似用户直接拖放文件时出现的那种文件组件——则需让每位用户通过针对个人的OAuth流程对机器人进行一次授权。

### 为何需要单独的授权流程

Google Chat的`media.upload`接口会直接拒绝服务账户认证：

> 此方法不支持使用服务账户进行应用认证。请使用用户账户进行认证。

目前不存在可解决此问题的IAM角色或权限范围，该接口仅接受用户凭证。因此，机器人每次上传文件时都必须*以用户身份*操作——具体而言，就是以请求该文件的用户身份。

### 一次性设置（每个账号需执行一次）

1. 进入同一GCP项目中的**APIs & Services → Credentials**。
2. 选择**Create credentials → OAuth client ID → Desktop app**。
3. 下载JSON文件，并将其放置到运行Hermes的服务器上。
4. 在Hermes中注册该客户端（需在指定权限范围的账号下运行）：

```bash
# Default profile:
python -m plugins.platforms.google_chat.oauth \
    --client-secret /path/to/client_secret.json

# A named profile gets its own separate registration:
hermes -p <profile> python -m plugins.platforms.google_chat.oauth \
    --client-secret /path/to/client_secret.json
```

该操作会将客户端密钥写入当前激活配置文件的Hermes配置目录中（例如，默认配置文件为`~/.hermes/google_chat_user_client_secret.json`）。此客户端密钥是**针对特定配置文件生成的，不会在不同配置文件之间共享**——每个配置文件都需要单独注册。这是有意为之：配置文件代表了独立的身份验证边界，因此两个配置文件可以对应不同的Google OAuth应用/账户。凡是需要发送Google Chat附件的用户，都需为各自对应的配置文件进行一次注册。

### 每用户独立授权（在聊天中）

每位用户需在自己的私信窗口中与机器人交互一次，完成以下流程：

1. 向机器人发送`/setup-files`指令，机器人会回复当前状态及下一步操作。
2. 发送`/setup-files start`指令，机器人将返回一个OAuth授权地址。
3. 打开该地址并点击“允许”，随后会看到浏览器无法加载`http://localhost:1/?...&code=...`的页面。出现此情况属于正常现象——授权码实际上就在网址栏中。
4. 复制失败的网址（或直接复制`code=...`后的数值），再将其作为`/setup-files <复制的网址>`的格式粘贴回聊天窗口。机器人会用该信息换取刷新令牌。

生成的令牌会被保存在`~/.hermes/google_chat_user_tokens/<经过脱敏处理的邮箱>.json`文件中。此后，该用户在私信中发送文件请求时将使用**自己的令牌**，这样文件就会以该用户的身份上传，并显示在其个人聊天空间中。

如需后续撤销授权，可发送`/setup-files revoke`指令，该操作仅会删除对应用户的令牌，其他用户的令牌不会受到影响。

### 权限范围

此流程仅请求一个权限范围：`chat.messages.create`。该权限已同时涵盖`media.upload`功能以及需要引用已上传`attachmentDataRef`的`messages.create`操作。系统不会授予任何与Google Drive相关的权限，也不会开放更广泛的Chat权限——这是出于最小权限原则的刻意设计。

### 多用户环境下的行为

如果发起请求的用户尚未拥有针对个人的令牌，机器人会回退到旧版的单用户令牌（位于`~/.hermes/google_chat_user_token.json`文件中，仅在前多用户模式安装时才会存在）。如果这两种令牌都不存在，机器人会发送一条文字通知，提示用户执行`/setup-files`指令。

用户自行撤销授权时，仅会清除自己的令牌。若某个用户的令牌导致出现401/403错误，也只会清除该用户的缓存数据，其他用户的正常使用不会受到影响。

---

## 故障排除

**发送“hola”后机器人无响应。**

1. 检查控制台中的Pub/Sub订阅是否有未处理的消息。如果有，则说明Hermes尚未完成身份验证——请核实`GOOGLE_CHAT_SERVICE_ACCOUNT_JSON`文件的配置是否正确，以及该服务账户是否在订阅设置中被标记为“Pub/Sub Subscriber”。
2. 如果订阅中没有任何消息，说明Google Chat并未发送数据。请仔细检查对应**主题**的IAM绑定设置：`chat-api-push@system.gserviceaccount.com`必须被设置为“Pub/Sub Publisher”角色。
3. 查看`hermes gateway`的日志，确认是否有`[GoogleChat] Connected`的记录。如果出现`[GoogleChat] Config validation failed`的错误信息，错误提示会明确指出需要修改哪个环境变量。

**机器人有回复，但显示的是错误信息而非智能体的实际答复。**

检查日志中是否出现`[GoogleChat] Pub/Sub stream died`的记录——如果此类错误频繁出现，可能是服务账户的凭证已被更换，或者相关订阅已被删除。在尝试10次后，适配器会自动标记自身为故障状态。

**每次发送消息都会出现“403 Forbidden”错误。**

可能是机器人已被从对应聊天空间中移除，或者您已在Chat API控制台取消了其权限。请重新将该机器人添加到该空间中（下次出现`ADDED_TO_SPACE`事件时，系统会自动恢复消息发送功能）。

**频繁出现“达到速率限制”警告。**

Chat API的默认配额为每个空间每分钟允许发送60条消息。如果您的智能体生成的响应内容过长，超过了此限制，适配器会采用指数退避策略进行重试——但用户仍会感受到明显的延迟。建议优化响应内容的简洁性，或通过GCP控制台提升配额限制。

**机器人一直发送`/setup-files`提示信息，而未上传文件。**

这是因为发起请求的用户尚未拥有个人OAuth令牌，且系统中也没有旧版的备用令牌。请在其私信窗口中执行`/setup-files`指令，并按照步骤10操作。完成令牌交换后，后续的文件请求即可直接上传，无需重启网关。

**执行`/setup-files start`时显示“未存储客户端凭证”。**

说明尚未为**当前配置文件**完成一次性设置流程（由于客户端密钥是针对特定配置文件生成的，因此在一个配置文件下完成的注册操作不会被其他配置文件识别）。请在终端中，使用网关所使用的配置文件来执行相关设置命令。

```bash
# Default profile:
python -m plugins.platforms.google_chat.oauth \
    --client-secret /path/to/client_secret.json

# Named profile:
hermes -p <profile> python -m plugins.platforms.google_chat.oauth \
    --client-secret /path/to/client_secret.json
```

请再次发送 `/setup-files start` 命令。

**当执行 `/setup-files <PASTED_URL>` 时出现“Token exchange failed.”的错误信息。**

授权码为一次性使用且有效期较短（通常仅为几分钟）。请发送 `/setup-files start` 以获取新的 URL，然后重试。

---

## 安全注意事项

- **服务账户权限范围**：该适配器会请求 `chat.bot` 和 `pubsub` 权限范围。实际权限管控应通过 IAM 完成——仅需为服务账户授予最少的必要权限（即订阅时分配 `roles/pubsub.subscriber` 和 `roles/pubsub.viewer` 角色），无需使用项目级或组织级的 Pub/Sub 权限。
- **附件下载保护**：Hermes 仅会将服务账户的承载令牌附加到主机地址属于 Google 所有域名短列表中的 URL 上（如 `googleapis.com`、`drive.google.com`、`lh[3-6].googleusercontent.com` 及其他几个域名）。对于任何其他主机地址，HTTP 请求都会在发送前被拒绝，以此防止通过构造特殊事件将承载令牌重定向到 GCE 元数据服务的 SSRF 攻击。
- **信息脱敏**：服务账户的邮箱地址、订阅路径以及主题路径都会通过 `agent/redact.py` 脱敏处理，不会出现在日志输出中。启用调试模式下的完整日志输出（通过设置 `GOOGLE_CHAT_DEBUG_RAW=1`）也会经过相同的脱敏过滤，并仅记录 DEBUG 级别的信息。
- **合规性要求**：如果您计划将该机器人连接到受监管的工作环境（即那些有数据驻留或 AI 管理政策的环境），请在首次安装前获得相关批准。
- **用户级 OAuth 权限范围**：针对单个用户的附件上传流程仅请求 `chat.messages.create` 权限——这一最小权限已足以支持 `media.upload` 操作以及后续的 `messages.create` 操作。生成的令牌会以纯 JSON 格式保存在 `~/.hermes/google_chat_user_tokens/<sanitized_email>.json` 文件中（文件系统权限起到保护作用，其安全机制与服务账户密钥文件相同）。每个令牌仅归属于一名用户，撤销授权也仅针对该用户有效。
