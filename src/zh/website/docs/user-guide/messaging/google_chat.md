---
sidebar_position: 12
title: "Google Chat"
description: "Set up Hermes Agent as a Google Chat bot using Cloud Pub/Sub"
---

# Google Chat 集成设置

将 Hermes Agent 作为机器人连接到 Google Chat。该集成利用 Cloud Pub/Sub 的拉式订阅机制来接收传入事件，同时通过 Chat REST API 发送消息。其工作原理类似于 Slack 的 Socket 模式或 Telegram 的长轮询模式：您的 Hermes 进程无需公共 URL、隧道或 TLS 证书，只需进行连接、身份验证并监听订阅——这与 Telegram 机器人通过令牌监听的方式相同。

> 运行 `hermes gateway setup` 命令，然后选择 **Google Chat** 即可获得逐步指导。

:::注意：仅限 Workspace 版本
Google Chat 是 Google Workspace 的组成部分。您可以使用此集成搭配个人 Workspace（通过 Google 注册的 `@yourdomain.com` 地址）或拥有应用发布权限的工作 Workspace。仅支持 Gmail 账户的用户无法托管 Chat 应用。
:::

## 概览

| 组件 | 值 |
|-----------|-------|
| **库** | `google-cloud-pubsub`、`google-api-python-client`、`google-auth` |
| **传入数据传输方式** | Cloud Pub/Sub 拉式订阅（无公共端点） |
| **传出数据传输方式** | Chat REST API (`chat.googleapis.com`) |
| **身份验证方式** | 包含 `roles/pubsub.subscriber` 权限的服务账户 JSON 文件 |
| **用户识别方式** | Chat 资源名称（`users/{id}`）+ 邮箱地址 |

---

## 第 1 步：创建或选择 GCP 项目

您需要一个 Google Cloud 项目来托管 Pub/Sub 主题。如果您还没有项目，请在 [console.cloud.google.com](https://console.cloud.google.com) 上创建一个——个人账户可享受免费套餐，足以满足机器人的流量需求。

请记下项目 ID（例如 `my-chat-bot-123`），后续所有步骤都会用到它。

---

## 第 2 步：启用两个 API

在控制台导航至 **APIs & Services → Library**，然后启用以下两项：

- **Google Chat API**
- **Cloud Pub/Sub API**

对于个人机器人产生的常规流量，使用这两项服务是免费的。

---

## 第 3 步：创建服务账户

进入 **IAM & Admin → Service Accounts → Create Service Account**。

- 名称：`hermes-chat-bot`
- 跳过“为该服务账户授予项目访问权限”这一步。只需在特定订阅层面配置 IAM 权限即可——**切勿**授予项目级的 Pub/Sub 角色。

创建完成后，打开该服务账户，进入 **Keys → Add Key → Create new key → JSON**，然后下载生成的文件。请将其保存在只有 Hermes 能读取的位置（例如 `~/.hermes/google-chat-sa.json`），并设置权限为 `chmod 600`）。

:::注意：不存在“Chat Bot Caller”角色
一个常见的错误是试图查找专门针对聊天功能的 IAM 角色并在项目层面授予该角色。实际上这样的角色并不存在。聊天机器人的权限来源于其在特定空间中的安装，而非 IAM 设置。您的服务账户只需拥有下一步中创建的订阅的 Pub/Sub 订阅者权限即可。
:::

---

## 第 4 步：创建 Pub/Sub 主题和订阅

进入 **Pub/Sub → Topics → Create topic**。

- 主题 ID：`hermes-chat-events`
- 其余选项均保持默认设置即可。
创建完成后，该主题的详情页面会显示一个**Subscriptions**选项卡。请创建一个订阅：

- 订阅 ID：`hermes-chat-events-sub`
- 传输类型：**Pull**
- 消息保留时间：**7天**（这样在Hermes重启后消息也不会丢失）
- 其余选项保持默认值即可。

---

## 第5步：为主题绑定IAM角色（非常重要）

在**主题**上（而非订阅）添加一个IAM主体：

- 主体：`chat-api-push@system.gserviceaccount.com`
- 角色：`Pub/Sub Publisher`

如果不这样做，Google Chat将无法向您的主题发布事件，您的机器人也就永远收不到任何消息。

---

## 第6步：为订阅绑定IAM角色

在**订阅**上，将您自己的服务账户添加为主体：

- 主体：`hermes-chat-bot@<your-project>.iam.gserviceaccount.com`
- 角色：`Pub/Sub Subscriber`

同时还需为该订阅授予`Pub/Sub Viewer`角色——因为Hermes在启动时会调用`subscription.get()`方法来检查连接是否正常。

---

## 第7步：配置Chat应用

进入**APIs & Services → Google Chat API → Configuration**页面。

- **应用名称**：可自行设定用户可见的名称（使用“Hermes”较为合适）。  
- **头像网址**：任何公开的 PNG 图片即可（Google 提供了默认选项）。  
- **描述**：显示在应用目录中的简短说明。  
- **功能选项**：需开启**接收一对一消息**以及**加入空间及群组对话**的功能。  
- **连接设置**：选择**Cloud Pub/Sub**，并输入主题名称 `projects/<your-project>/topics/hermes-chat-events`。  
- **可见范围**：建议限制在当前工作空间内（或特定用户范围内）——测试期间切勿向所有人公开。

保存设置。

---

## 第 8 步：在测试空间中安装该机器人

在浏览器中打开 Google Chat。通过 **+ 新建聊天** 菜单中的应用名称来发起私信交流。首次发送消息时，Google 会发送一个 `ADDED_TO_SPACE` 事件，Hermes 会利用该事件缓存机器人的自身 `users/{id}` 信息，以便实现消息过滤功能。

---

## 第 9 步：配置 Hermes

将 Google Chat 相关设置添加到 `~/.hermes/.env` 文件中：

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

项目 ID 会回退为 `GOOGLE_CLOUD_PROJECT`，而服务账户路径则会回退为 `GOOGLE_APPLICATION_CREDENTIALS`——您可以根据个人偏好选择其中任意一种约定。

在[多配置文件网关](../multi-profile-gateways.md)环境下，所有 `GOOGLE_CHAT_*` 类型的设置都会从对应路由配置文件自身的 `.env` 文件中读取；辅助配置文件绝不会继承默认配置文件中的项目、订阅或服务账户信息。如果某个配置文件未配置服务账户，而进程环境却包含了其他配置文件的服务账户信息，适配器将拒绝回退到“应用程序默认凭据”（因为那样会导致使用该其他配置文件的身份进行认证），而是会记录明确的错误信息——此时请在该配置文件的 `.env` 文件中添加 `GOOGLE_CHAT_SERVICE_ACCOUNT_JSON`。

您可以通过官方维护的安装工具来安装 Google Chat 适配器的依赖项。该工具会应用与运行时检查所使用的相同安全标准。

```bash
python -m plugins.platforms.google_chat.oauth --install-deps
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

在测试用的私信中发送“hola”。机器人会先发布一条“Hermes正在思考中…”的提示信息，随后直接用真实回复替换该消息——而不会留下“消息已删除”的标记。

### 自定义工作状态提示文本

该提示文本可通过`~/.hermes/config.yaml`文件中的`typing_status_text`参数进行配置——例如，对于名为Ada的小猫助手：

```yaml
platforms:
  google_chat:
    # Custom working-state marker text (default: "Hermes is thinking…").
    typing_status_text: "is pouncing… 🐾"
```

与 Slack 的临时状态行不同，这是一条**真正已发送的消息**，会随着回复内容实时更新——因此您在此处设置的任何内容都会以普通消息的形式显示在聊天中。如需完全禁用该标记，可设置 `typing_indicator: false`。

---

## 格式与功能

Google Chat 支持有限的 Markdown 格式：

| 支持 | 不支持 |
|------|--------|
| `*粗体*`、`_斜体_`、`~删除线~`、`` `代码` `` | 标题、列表 |
| 通过 URL 引用的内联图片 | 交互式卡片 v2 按钮（本网关的 v1 版本） |
| 原生文件附件（需在 `/setup-files` 后设置——参见步骤 10） | 原生语音便签/环形视频便签 |

智能体的系统提示中包含了针对 Google Chat 的特别说明，使其知晓这些限制并避免使用无法正确显示的格式。

消息大小限制：每条消息最多 4000 个字符。过长的智能体回复会自动拆分到多条消息中。

主题讨论支持：当用户在主题讨论中回复时，Hermes 会识别 `thread.name` 并将回复发布到同一主题中，因此每个主题都会对应一个独立的 Hermes 会话。

### 通过交互式卡片解答疑问

当智能体提出多项选择式的澄清问题时，适配器会将其转换为原生**Card v2**格式，每个选项对应一个按钮，此外还会添加一个**“其他/自定义答案”**按钮，而非普通的编号文本列表。点击任意按钮即可直接回答问题（`CARD_CLICKED`事件会将所选答案反馈至正在等待的会话）。如果卡片无法发送，或者问题没有固定的选项，适配器则会回退到标准的文本澄清方式。此过程无需任何配置。

---

## 第10步：原生附件传输（可选）

默认情况下，该机器人即可发布文本、通过URL嵌入图片，以及下载音频/视频/文档的卡片。若要传输**原生**聊天附件——即类似人类拖放文件时所看到的那种文件组件——则需让每位用户通过针对个人的OAuth流程对机器人进行一次授权。

### 为何需要单独的授权流程

Google Chat的`media.upload`接口会直接拒绝服务账户认证：

> 此方法不支持使用服务账户进行应用认证。请使用用户账户进行认证。

目前不存在能够解决此问题的IAM角色或权限范围，该接口仅接受用户凭证。因此，每当机器人上传文件时，都必须以*用户身份*操作——具体而言，就是以请求该文件的用户身份来操作。

### 仅需一次性设置（针对每个账号）

1. 进入同一 GCP 项目中的 **APIs & Services → Credentials** 页面。  
2. 选择 **Create credentials → OAuth client ID → Desktop app**。  
3. 下载生成的 JSON 文件，将其放到运行 Hermes 的主机上。  
4. 在 Hermes 中注册该客户端（需在希望限制其权限的配置文件下执行操作）。

```bash
# Default profile:
python -m plugins.platforms.google_chat.oauth \
    --client-secret /path/to/client_secret.json

# A named profile gets its own separate registration:
hermes -p <profile> python -m plugins.platforms.google_chat.oauth \
    --client-secret /path/to/client_secret.json
```

该操作会将客户端密钥写入当前激活配置文件的Hermes配置目录中（默认配置文件为`~/.hermes/google_chat_user_client_secret.json`）。此客户端密钥是**针对特定配置文件而言的，不会在不同配置文件之间共享**——每个配置文件都会单独注册自己的密钥。这是有意为之：配置文件代表了独立的身份验证边界，因此两个配置文件可以关联到不同的Google OAuth应用/账户。凡是需要发送Google Chat附件的用户，都需为各自对应的配置文件进行一次注册。

### 每用户独立授权（在聊天中）

每位用户都需要在自己的私信窗口中与机器人交互一次，完成以下流程：

1. 向机器人发送`/setup-files`指令，机器人会回复当前状态及下一步操作。
2. 发送`/setup-files start`指令，机器人会返回一个OAuth授权地址。
3. 打开该地址并点击“允许”，此时浏览器会尝试加载`http://localhost:1/?...&code=...`，但无法成功加载。这种失败是正常现象，因为授权码实际上位于网址栏中。
4. 复制该失败的网址（或直接复制`code=...`后的数值），然后将其以`/setup-files <复制的网址>`的形式粘贴回聊天窗口。机器人会将该信息转换为刷新令牌。

生成的令牌会被保存在`~/.hermes/google_chat_user_tokens/<处理过的邮箱地址>.json`文件中。此后，该用户在私信中发送文件请求时将使用**自己的令牌**，这样机器人就会以该用户的身份上传文件，消息也会显示在该用户的聊天空间中。

如需后续撤销授权，可发送`/setup-files revoke`指令，该操作仅会删除对应用户的令牌，其他用户的令牌则不会受到影响。

### 权限范围

该流程仅请求一个作用域：`chat.messages.create`。该作用域已同时涵盖`media.upload`操作，以及引用已上传`attachmentDataRef`的`messages.create`操作。系统不支持Drive功能，也不提供更广泛的Chat作用域——这是有意采用的最小权限原则。

### 多用户场景下的行为表现

当提问者尚未拥有针对单个用户的令牌时，机器人会回退到位于`~/.hermes/google_chat_user_token.json`处的旧版单用户令牌（前提是该文件存在于早期多用户模式安装留下的环境中）。若这两种令牌均不存在，机器人会发送一条清晰的文本提示，告知提问者执行 `/setup-files` 命令。

用户撤销授权仅会清除自身的缓存数据。某个用户令牌引发的401/403错误也只会影响该用户的缓存，不会干扰其他用户的使用。

---

## 故障排除

**发送“hola”后机器人无响应。**

1. 在控制台检查Pub/Sub订阅中是否存在未送达的消息。如果有，则说明Hermes尚未完成身份验证——请核实`GOOGLE_CHAT_SERVICE_ACCOUNT_JSON`文件的配置是否正确，以及该服务账户在订阅设置中是否被标记为`Pub/Sub Subscriber`。
2. 若订阅中没有任何消息，说明Google Chat并未发送数据。请仔细检查对应**主题**的IAM绑定设置：`chat-api-push@system.gserviceaccount.com`必须被设置为`Pub/Sub Publisher`角色。
3. 查看`hermes gateway`的日志，确认是否有`[GoogleChat] Connected`的记录。若出现`[GoogleChat] Config validation failed`的提示，错误信息会直接指出需要修正哪个环境变量。

**机器人虽会回复，但显示的是错误信息而非智能体的实际答案。**

请检查日志中是否出现“[GoogleChat] Pub/Sub stream died”的提示——如果此类错误频繁出现，可能是您的服务账户凭证已被更换或订阅已被删除。在尝试10次后，适配器会自动标记自身为故障状态。

**每条发送的消息都返回“403 Forbidden”错误。**

这通常表示该机器人已被从对应空间中移除，或者您已在Chat API控制台取消了其权限。请重新将该机器人添加到该空间中（下一次出现`ADDED_TO_SPACE`事件时，消息功能将自动恢复）。

**出现过多“达到速率限制”警告。**

Chat API的默认配额为每个空间每分钟允许发送60条消息。如果您的智能体生成的流式响应过长，超过了这一限制，适配器会通过指数退避策略进行重试——但用户仍会感受到明显的延迟。建议优化响应内容或通过GCP控制台提升配额。

**机器人持续发送“/setup-files”提示而非实际文件。**

这是因为提问者没有针对该用户的OAuth令牌，且系统中也没有旧的备用方案。请在他们的私信中执行`/setup-files`命令，然后按照步骤10操作。完成交互后，后续的文件请求将无需重启网关即可直接上传。

**执行“/setup-files start”时显示“未存储客户端凭证”。**

这说明尚未为*当前配置文件*完成一次性设置（客户端密钥是按配置文件划分的，因此在一个配置文件下完成的注册不会被另一个配置文件识别）。请在终端中，使用网关所使用的配置文件来执行该命令：

```bash
# Default profile:
python -m plugins.platforms.google_chat.oauth \
    --client-secret /path/to/client_secret.json

# Named profile:
hermes -p <profile> python -m plugins.platforms.google_chat.oauth \
    --client-secret /path/to/client_secret.json
```

请再次发送 `/setup-files start`。

**当执行 `/setup-files <PASTED_URL>` 时出现“Token exchange failed.”的错误信息。**

授权码为一次性使用且有效期较短（通常仅为几分钟）。请发送 ` /setup-files start ` 以获取新的 URL，然后重试。

---

## 安全注意事项

- **服务账户权限范围**：该适配器会请求 `chat.bot` 和 `pubsub` 权限范围。实际权限管控应通过 IAM 完成——仅为服务账户授予最必要的权限（即订阅时分配 `roles/pubsub.subscriber` 和 `roles/pubsub.viewer` 角色），而非项目级或组织级的 Pub/Sub 权限。
- **附件下载保护**：Hermes 仅会将服务账户的承载令牌附加到主机地址属于 Google 所有域名短列表的 URL 上（如 `googleapis.com`、`drive.google.com`、`lh[3-6].googleusercontent.com` 及其他几个域名）。对于任何其他主机地址，系统会在发起 HTTP 请求之前予以拒绝，以此防止通过构造恶意事件将承载令牌重定向到 GCE 元数据服务的 SSRF 攻击。
- **信息脱敏**：服务账户的电子邮件地址、订阅路径以及主题路径都会通过 `agent/redact.py` 脱敏处理，不会出现在日志输出中。启用调试级日志时（通过设置 `GOOGLE_CHAT_DEBUG_RAW=1`），日志信息也会经过相同的脱敏过滤。
- **合规性要求**：如果您计划将该机器人连接到受监管的工作空间（即那些有数据驻留或人工智能管理政策的工作空间），请在首次安装前获得相关审批。
- **用户 OAuth 权限范围**：针对单用户的附件上传流程，仅会请求 `chat.messages.create` 权限——这一最小权限已足以支持 `media.upload` 操作以及后续的 `messages.create` 操作。相应的访问令牌会以纯 JSON 格式存储在 `~/.hermes/google_chat_user_tokens/<脱敏后的邮箱>.json` 文件中（其安全性依赖于文件系统权限，与 SA 密钥文件的保护机制相同）。每个令牌仅归属于一名用户，且取消授权的操作也仅针对该用户生效。
