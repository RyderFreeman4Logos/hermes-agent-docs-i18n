---
sidebar_position: 9
title: "Matrix"
description: "Set up Hermes Agent as a Matrix bot"
---

# Matrix 设置

Hermes Agent 能与开源的联邦式消息协议 Matrix 相集成。使用 Matrix，你可以自行搭建本地服务器，或使用 matrix.org 等公共服务器——无论哪种方式，你都能掌控自己的通信内容。该机器人通过 `mautrix` Python SDK 与 Matrix 连接，通过 Hermes Agent 的处理流程（包括工具调用、内存管理及推理功能）来处理消息，并实现实时回复。它支持文本、文件附件、图片、音频、视频传输，同时还提供可选的端到端加密（E2EE）功能。

Hermes Agent 兼容所有类型的 Matrix 服务器——无论是 Synapse、Conduit、Dendrite，还是 matrix.org。

在开始设置之前，这里有大多数人最关心的问题：一旦连接成功，Hermes 的表现如何？

## Hermes 的运行方式

| Context | Behavior |
|---------|----------|
| **DMs** | Hermes responds to every message. No `@mention` needed. Each DM has its own session. Set `MATRIX_DM_MENTION_THREADS=true` to start a thread when the bot is `@mentioned` in a DM. |
| **Rooms** | By default, Hermes requires an `@mention` to respond. Set `MATRIX_REQUIRE_MENTION=false` or add room IDs to `MATRIX_FREE_RESPONSE_ROOMS` for free-response rooms. Room invites are auto-accepted. |
| **Threads** | Hermes supports Matrix threads (MSC3440). If you reply in a thread, Hermes keeps the thread context isolated from the main room timeline. Threads where the bot has already participated do not require a mention. |
| **Auto-threading** | By default, Hermes auto-creates a thread for each message it responds to in a room. This keeps conversations isolated. Set `MATRIX_AUTO_THREAD=false` to disable. Set `MATRIX_DM_AUTO_THREAD=true` (default false) to also auto-create threads for DM messages — this is distinct from `MATRIX_DM_MENTION_THREADS`, which only starts a thread when the bot is `@mentioned` in a DM. |
| **Commands** | Hermes accepts normal `/commands` when your Matrix client sends them. If your client reserves `/` for local commands, use `!commands` instead; Hermes normalizes known `!command` aliases to `/command`. |
| **Interactive controls** | Dangerous-command approval and `/model` selection can use Matrix reactions. Approval reactions can be limited to the user who requested the action. |
| **Thinking and tool activity** | Matrix uses threaded, editable thinking/tool-activity panes when gateway progress is enabled, so updates do not flood the main room timeline. |
| **Shared rooms with multiple users** | By default, Hermes isolates session history per user inside the room. Two people talking in the same room do not share one transcript unless you explicitly disable that. |
| **LaTeX math** | `$...$` (inline) and `$$...$$` (display) in replies are sent as Element `data-mx-maths` markup, so clients with **Settings → Labs → Render LaTeX maths in messages** typeset them with KaTeX. Unpaired dollars (`$5 or $10`) stay literal, and the plain-text `body` keeps the raw TeX for other clients. |

:::提示
该机器人会在收到邀请时自动加入对应房间。只需将机器人的Matrix用户邀请至任意房间，它就会立即加入并开始响应。
:::

## 功能矩阵

本表格的数据来源于Matrix适配器功能声明及Matrix测试覆盖率。端到端加密功能是根据部署模式来确定的，因为不同的部署方式会选择禁用加密房间、采用随机加密或强制要求加密。

| 功能 | Matrix支持情况 |
|------|--------------|
| 文本消息 | 支持 |
| 线程消息 | 支持 |
| 反应功能 | 支持 |
| 审批功能 | 支持 |
| 模型选择器 | 支持 |
| 思考面板 | 支持 |
| 图片发送 | 支持 |
| 多张图片发送 | 支持 |
| 文件上传 | 支持 |
| 语音/音频传输 | 支持 |
| 视频传输 | 支持 |
| 端到端加密 | 关闭 / 可选 / 强制要求 |
| 诊断功能 | 支持 |

### Matrix中的会话模型

默认情况下：

- 每条私信都会拥有独立的会话
- 每个线程消息都会拥有独立的会话命名空间
- 共享房间中的每位用户在该房间内也会拥有独立的会话

这些设置可通过`config.yaml`文件进行配置：

```yaml
group_sessions_per_user: true
```

仅当您明确希望为整个房间设置单一共享对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话虽有助于实现协作式工作环境，但同时也存在以下问题：

- 用户需共同承担上下文存储空间的增长及令牌成本
- 某人执行的耗时且涉及大量工具的任务可能会占用其他所有人的上下文空间
- 某人正在运行的任务可能会干扰同一房间内其他人的后续操作

### 提及与自动分线程配置

您可以通过环境变量或 `config.yaml` 文件来配置提及功能及自动分线程行为：

```yaml
matrix:
  require_mention: true           # Require @mention in rooms (default: true)
  allowed_users:                  # Matrix users allowed to trigger agent turns
    - "@alice:matrix.org"
  allowed_rooms:                  # Matrix rooms allowed to trigger agent turns
    - "!abc123:matrix.org"
  free_response_rooms:            # Rooms exempt from mention requirement
    - "!abc123:matrix.org"
  ignore_user_patterns:           # Bridge/appservice ghost users to ignore
    - "^@telegram_"
    - "^@whatsapp_"
  process_notices: false          # Ignore m.notice by default
  session_scope: room             # auto|room|thread; room is recommended for project rooms
  auto_thread: true               # Auto-create threads for responses (default: true)
  dm_mention_threads: false       # Create thread when @mentioned in DM (default: false)
  max_message_length: 16000       # Outbound chunk size in chars (default: 16000, max: 65535)
```

或者通过环境变量设置：

```bash
MATRIX_REQUIRE_MENTION=true
MATRIX_ALLOWED_USERS=@alice:matrix.org
MATRIX_ALLOWED_ROOMS=!abc123:matrix.org
MATRIX_FREE_RESPONSE_ROOMS=!abc123:matrix.org,!def456:matrix.org
MATRIX_IGNORE_USER_PATTERNS='^@telegram_,^@whatsapp_'
MATRIX_PROCESS_NOTICES=false
MATRIX_SESSION_SCOPE=room       # recommended for stable project-room context
MATRIX_AUTO_THREAD=true
MATRIX_DM_MENTION_THREADS=false
MATRIX_REACTIONS=true          # default: true — emoji reactions during processing
MATRIX_ALLOW_ROOM_MENTIONS=false
```

:::提示 禁用表情反应  
将 `MATRIX_REACTIONS=false` 设定后，机器人便不会在收到的消息上添加处理流程相关的表情反应（👀/✅/❌）。这对于那些表情反应信息过多，或并非所有参与客户端都支持该功能的房间尤为有用。  
:::

:::提示 全房间提及  
Hermes 会为带有明确 Matrix 用户 ID 的内容（如 `@alice:example.org`）发送结构化的 Matrix 用户提及信息。默认情况下，全房间的 `@room` 通知是被禁用的；仅当允许机器人向所有成员发送通知时，才将 `MATRIX_ALLOW_ROOM_MENTIONS=true` 设定为有效值。  
:::

:::注意  
如果您是从未包含 `MATRIX_REQUIRE_MENTION` 参数的版本升级而来，那么之前的机器人会响应房间中的所有消息。若希望保持此行为，请将 `MATRIX_REQUIRE_MENTION=false` 设定。  
:::

### 项目房间隔离功能  

如果在多个项目房间中使用同一个 Matrix 机器人，建议配置稳定的房间级会话：

```bash
MATRIX_SESSION_SCOPE=room
MATRIX_AUTO_THREAD=false
```

`MATRIX_SESSION_SCOPE` 支持以下取值：

| 取值 | 行为说明 |
|-------|----------|
| `auto` | 兼容旧版本的默认值。原有的 `MATRIX_AUTO_THREAD` 行为用于控制合成线程。 |
| `room` | 非线程形式的房间消息会保留在同一个稳定的房间会话中，而真实的 Matrix 线程则仍沿用其对应的线程根节点。 |
| `thread` | 非线程形式的房间消息会根据触发事件的 ID 生成一个新的线程/会话。 |

Hermes 现在会在智能体提示信息中包含当前的 Matrix 房间名称、房间 ID、主题、消息 ID，以及与房间边界相关的信息。执行 `/status` 命令也可查看当前的 Matrix 房间/会话范围；而执行 `/resume` 命令时，除非明确使用 `/resume --cross-room <session name>`，否则不会自动从另一个 Matrix 房间继续已命名的会话。

`MATRIX_SESSION_SCOPE=room` 用于控制房间/线程的通道划分。原有的 `group_sessions_per_user` 设置仍决定该房间内的用户是否共享同一通道。当 `group_sessions_per_user: true`（默认值）时，Alice 和 Bob 将拥有独立的 Project B 会话；而当 `group_sessions_per_user: false` 时，整个房间将共享同一个 Project B 记录。

本指南将引导您完成从创建机器人账户到发送第一条消息的完整设置流程。

## 第一步：创建机器人账户

机器人需要一个 Matrix 用户账户，实现方式有以下几种：

### 方案 A：在您的自建服务器上注册（推荐）

如果您拥有自己的自建服务器（如 Synapse、Conduit、Dendrite）：

1. 使用管理 API 或注册工具创建一个新用户：

```bash
# Synapse example
register_new_matrix_user -c /etc/synapse/homeserver.yaml http://localhost:8008
```

2. 选择一个用户名，例如 `hermes`——完整的用户标识将为 `@hermes:your-server.org`。

### 方案 B：使用 matrix.org 或其他公共主服务器

1. 访问 [Element Web](https://app.element.io) 并创建一个新账户。
2. 为你的机器人选择一个用户名（例如 `hermes-bot`）。

### 方案 C：使用你自己的账户

你也可以以自己的用户身份运行 Hermes。这意味着机器人将代表你发送消息——非常适合用于个人助手。

## 第 2 步：获取访问令牌

Hermes 需要访问令牌才能与主服务器进行身份验证。你有两种选择：

### 方案 A：访问令牌（推荐）

获取令牌最可靠的方法：

**通过 Element：**
1. 使用机器人账户登录 [Element](https://app.element.io)。
2. 进入 **设置** → **帮助与关于**。
3. 向下滚动并展开 **高级选项**——访问令牌会显示在那里。
4. **立即复制它。**

**通过 API：**

```bash
curl -X POST https://your-server/_matrix/client/v3/login \
  -H "Content-Type: application/json" \
  -d '{
    "type": "m.login.password",
    "user": "@hermes:your-server.org",
    "password": "your-password"
  }'
```

响应中包含一个 `access_token` 字段——请将其复制下来。

:::warning[妥善保管您的访问令牌]
该访问令牌可让您完全控制机器人的 Matrix 账户。切勿将其公开分享或提交到 Git 中。一旦令牌泄露，请通过注销该用户的所有会话来撤销其权限。
:::

### 方案 B：密码登录

您也可以无需提供访问令牌，而是将机器人的用户 ID 和密码告知 Hermes。这样 Hermes 在启动时会自动登录。虽然更为简单，但意味着密码会被存储在您的 `.env` 文件中。

```bash
MATRIX_USER_ID=@hermes:your-server.org
MATRIX_PASSWORD=your-password
```

## 第3步：查找您的Matrix用户ID

Hermes Agent会使用您的Matrix用户ID来控制哪些用户可以与该机器人交互。Matrix用户ID的格式为`@用户名:服务器名`。

要查找您的用户ID：

1. 打开[Element](https://app.element.io)（或您常用的Matrix客户端）。
2. 点击您的头像 → **设置**。
3. 您的用户ID会显示在个人资料顶部（例如：`@alice:matrix.org`）。

:::提示
Matrix用户ID始终以`@`开头，其后跟随一个冒号以及服务器名称。例如：`@alice:matrix.org`、`@bob:your-server.com`。
:::

## 第4步：配置Hermes Agent

### 方案A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

当系统提示时，请选择 **Matrix**，随后在相应字段中输入您的主服务器地址、访问令牌（或用户 ID 加密码），以及允许的用户名列表。

### 方案 B：手动配置

在您的 `~/.hermes/.env` 文件中添加以下内容：

**使用访问令牌：**

```bash
# Required
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_ACCESS_TOKEN=***

# Optional: user ID (auto-detected from token if omitted)
# MATRIX_USER_ID=@hermes:matrix.example.org

# Security: restrict who can interact with the bot
MATRIX_ALLOWED_USERS=@alice:matrix.example.org

# Optional: restrict which rooms can trigger the bot
MATRIX_ALLOWED_ROOMS=!abc123:matrix.example.org

# Multiple allowed users (comma-separated)
# MATRIX_ALLOWED_USERS=@alice:matrix.example.org,@bob:matrix.example.org
```

**使用密码登录：**

```bash
# Required
MATRIX_HOMESERVER=https://matrix.example.org
MATRIX_USER_ID=@hermes:matrix.example.org
MATRIX_PASSWORD=***

# Security
MATRIX_ALLOWED_USERS=@alice:matrix.example.org
```

## 私有环境部署加固方案

对于私有 Matrix 部署环境，需同时设置用户白名单和房间白名单。如果未配置 `MATRIX_ALLOWED_USERS`，则任何能够在已加入的房间中联系到该机器人的发送者都可能触发机器人执行对应操作。而若未设置 `MATRIX_ALLOWED_ROOMS`，机器人所加入的任何房间都可能引发同样的操作。为确保部署环境的安全性，应同时配置这两项设置。

```bash
MATRIX_ALLOWED_USERS=@alice:matrix.example.org,@bob:matrix.example.org
MATRIX_ALLOWED_ROOMS=!ops:matrix.example.org,!dmroom:matrix.example.org
```

桥接节点与 AppService 型部署需要额外的循环保护机制。Hermes 会默认忽略自身的事件、本地标识以“_”开头的 Matrix AppService 风格用户发送的事件、重复的事件 ID、旧的启动事件、编辑替换事件以及 `m.notice` 类型的事件。如果您的桥接节点采用了不同的命名规则，还需添加针对该部署的特定桥接节点过滤模式：

```bash
MATRIX_IGNORE_USER_PATTERNS='^@telegram_,^@slack_,^@whatsapp_'
```

仅当可信的人工工作流真正发送了 `m.notice` 时，才启用通知功能：

```bash
MATRIX_PROCESS_NOTICES=true
```

默认情况下，向整个房间发送通知的功能处于禁用状态。除非明确允许该机器人使用`@room`指令唤醒整个房间，否则请保持`MATRIX_ALLOW_ROOM_MENTIONS=false`的设置。

诊断与调试相关的数据包会隐藏Matrix访问令牌、恢复密钥、设备标识符以及消息内容。媒体文件下载仅限于Matrix格式的`mxc://`内容URI，且当文件大小超过`MATRIX_MAX_MEDIA_BYTES`限制时将被拒绝。应将联合房间及不可信的服务器视为不可信输入：严格管理房间白名单，对于需要使用大量工具的任务，优先选择私信或私人房间处理，同时避免将桥接账号或AppService傀儡账户设置为允许用户。

在`~/.hermes/config.yaml`中可配置以下可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 可确保在共享房间中每位参与者的上下文相互隔离。

### 启动网关

配置完成后，即可启动 Matrix 网关：

```bash
hermes gateway
```

该机器人应能在几秒钟内连接到您的主服务器并开始同步。您可以通过私信或在其加入的频道中发送消息来对其进行测试。

:::提示
为确保持续运行，您可以将 `hermes gateway` 在后台运行或作为 systemd 服务来部署。详情请参阅部署指南。
:::

## 端到端加密（E2EE）

Hermes 支持 Matrix 端到端加密功能，因此您可以在加密频道中与您的机器人进行聊天。

### 需求条件

实现端到端加密需要包含加密扩展功能的 `mautrix` 库以及 `libolm` C 库：

```bash
# Install mautrix with E2EE support
pip install 'mautrix[encryption]'

# Or install with hermes extras
cd ~/.hermes/hermes-agent && uv pip install -e ".[matrix]"
```

您的系统上还需安装 `libolm`：

```bash
# Debian/Ubuntu
sudo apt install libolm-dev

# macOS
brew install libolm

# Fedora
sudo dnf install libolm-devel
```

### 启用端到端加密

在您的 `~/.hermes/.env` 文件中添加以下内容：

```bash
MATRIX_E2EE_MODE=required
```

`MATRIX_E2EE_MODE` 支持以下模式：

| 模式 | 行为说明 |
|------|----------|
| `off` | 不初始化 Matrix 加密功能。 |
| `optional` | 在具备相关依赖条件时尝试启用加密功能；若无法初始化加密模块，则仍允许使用未加密的聊天室。 |
| `required` | 若缺少加密功能所需的依赖或加密设置，直接终止服务。 |

在加密设置不可用时，`optional` 模式会回退到非加密模式运行。而 `required` 模式则会直接终止服务，而不会默默降级为非加密模式。

为保持向后兼容性，即使设置 `MATRIX_ENCRYPTION=true`，也会启用强制性的加密功能。

启用加密功能后，Hermes 会： 
- 将加密密钥存储在 `~/.hermes/platforms/matrix/store/` 目录中（旧版本安装路径为 `~/.hermes/matrix/store/`）；
- 在首次连接时上传设备密钥；
- 自动解密接收到的消息并加密发送的消息；
- 接到加密聊天室邀请时自动加入。

### Matrix 工具与控制功能

在 Matrix 对话中，Hermes 会向智能体提供针对 Matrix 的专用工具：
- `matrix_send_reaction`：发送表情反应
- `matrix_redact_message`：隐藏消息内容
- `matrix_create_room`：创建聊天室
- `matrix_invite_user`：邀请用户加入
- `matrix_fetch_history`：获取消息历史记录
- `matrix_set_presence`：设置在线状态
这些工具仅适用于 Matrix 环境，不会出现在非 Matrix 工具集中。管理类工具默认处于禁用状态：要启用内容屏蔽功能需设置 `MATRIX_TOOLS_ALLOW_REDACTION=true`，要启用邀请功能需设置 `MATRIX_TOOLS_ALLOW_INVITES=true`，而要创建房间则需设置 `MATRIX_TOOLS_ALLOW_ROOM_CREATE=true`。此外，创建公共房间还需满足 `MATRIX_ALLOW_PUBLIC_ROOMS=true` 的条件。
如果设置了 `MATRIX_ALLOWED_ROOMS`，Matrix 工具将仅能操作那些被允许的房间。

反应控制选项包括：
- ✅ 仅批准一次
- ♾️ 始终批准
- ❌ 拒绝
- 针对 `/model` 选项的数字型反应

如果您希望房间内的任何授权 Matrix 用户都能使用审批/模型选择功能，请将 `MATRIX_APPROVAL_REQUIRE_SENDER=false` 设为有效值。在 Hermes 已知晓操作请求者身份的情况下，其默认行为是仅允许请求者执行该操作。

### 媒体大小限制

Hermes 通过 Matrix 媒体 API 来上传和下载图像、文件、音频及视频等媒体内容。多个生成的图像会作为一个有序的逻辑批次发送，从而在批次间保留字幕及对话上下文信息。

默认情况下，超过 100 MB 的 Matrix 媒体在上传/下载前会被拒绝。如需更改此限制，请通过以下方式设置：

```bash
MATRIX_MAX_MEDIA_BYTES=104857600
```

传入的媒体内容必须使用 Matrix 的 `mxc://` 格式内容 URI。为避免将联合室变成一个无限制的下载工具，Hermes 会拒绝在 Matrix 消息中包含任意格式的 HTTP(S) 媒体地址。

### 交叉签名验证（推荐）

如果您的 Matrix 账户已启用交叉签名功能（Element 默认已开启），请设置恢复密钥，以便机器人能在启动时对自身设备进行自我签名。否则，在设备密钥更换后，其他 Matrix 客户端可能会拒绝与该机器人共享加密会话。

```bash
MATRIX_RECOVERY_KEY=EsT... your recovery key here
```

**查找位置：** 在 Element 中，进入 **设置** → **安全与隐私** → **加密**，即可看到您的恢复密钥（也称为“安全密钥”）。这正是您在首次设置交叉签名功能时被要求保存的密钥。

每次启动时，如果已设置 `MATRIX_RECOVERY_KEY`，Hermes 会从主服务器的安全密钥存储中读取交叉签名密钥，并对当前设备进行签名。该操作具有幂等性，因此可以永久保持启用状态而无需担心安全问题。

若 Hermes 生成了新的 Matrix 恢复密钥，它绝不会记录原始密钥内容。您可以在启动前设置 `MATRIX_RECOVERY_KEY_OUTPUT_FILE=/secure/path/matrix-recovery-key.txt`，以文件权限 `0600` 将生成的密钥写入该文件；如果该文件已存在，则不会被覆盖。

:::warning[删除加密存储库]
如果您删除了 `~/.hermes/platforms/matrix/store/crypto.db`，机器人将失去其加密身份。仅使用相同的设备 ID 重新启动是无法完全恢复的——主服务器仍保留着用旧身份密钥签名的一次性密钥，因此其他节点无法建立新的 Olm 会话。

Hermes 在启动时会检测到这种情况，并拒绝启用端到端加密，同时会记录如下信息：`设备 XXXX 在服务器上持有使用旧身份密钥签名的一次性密钥，这些密钥已过期`。

**最简单的恢复方法：生成新的访问令牌**（这将获得一个全新的设备 ID，且没有过期的密钥记录）。请参阅下文的“从旧版本升级到支持端到端加密的系统”部分。这是最可靠的解决方案，且无需修改主服务器的数据库。

**手动恢复**（较为复杂——需保持原有的设备 ID）：

1. 停止 Synapse 的运行，并从其数据库中删除旧设备：
   ```bash
   sudo systemctl stop matrix-synapse
   sudo sqlite3 /var/lib/matrix-synapse/homeserver.db "
     DELETE FROM e2e_device_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM e2e_one_time_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM e2e_fallback_keys_json WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
     DELETE FROM devices WHERE device_id = 'DEVICE_ID' AND user_id = '@hermes:your-server';
   "
   sudo systemctl start matrix-synapse
   ```
或者通过 Synapse 管理员 API 实现（请注意用户 ID 需进行 URL 编码）：
   ```bash
   curl -X DELETE -H "Authorization: Bearer ADMIN_TOKEN" \
     'https://your-server/_synapse/admin/v2/users/%40hermes%3Ayour-server/devices/DEVICE_ID'
   ```
注意：通过管理 API 删除设备也可能会使对应的访问令牌失效，此时您可能需要重新生成新的令牌。

2. 删除本地加密存储并重启 Hermes：
   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db*
   # restart hermes
   ```

其他 Matrix 客户端（如 Element、matrix-commander）可能会缓存旧的设备密钥。恢复后，在 Element 中输入 `/discardsession` 即可强制与机器人建立新的加密会话。
:::

:::info
如果未安装 `mautrix[encryption]` 或缺少 `libolm`，机器人将自动回退到普通的（未加密的）客户端。您会在日志中看到相关警告。
:::

## 主房间

您可以指定一个“主房间”，让机器人在此发送主动消息（如定时任务输出、提醒和通知）。设置方法有两种：

### 使用斜杠命令

在机器人所在的任意 Matrix 房间中输入 `/sethome`，该房间即成为主房间。
如果您的 Matrix 客户端拦截了斜杠命令，则请使用 `!sethome`。

### 手动配置

在您的 `~/.hermes/.env` 文件中添加以下内容：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

## 房间白名单（`allowed_rooms`）

可将机器人限制在特定的 Matrix 房间范围内。启用该设置后，机器人**仅**会在列表中所列的房间内响应消息——来自其他任何房间的消息都将被直接忽略，即便提到了该机器人也是如此。

**私信对话室不受此限制**，因此授权用户始终可以与机器人进行一对一交流。

```yaml
matrix:
  allowed_rooms:
    - "!abc123def456:matrix.example.org"
    - "!opsroom789:matrix.example.org"
```

或通过环境变量（以逗号分隔）：

```bash
MATRIX_ALLOWED_ROOMS="!abc123def456:matrix.example.org,!opsroom789:matrix.example.org"
```

行为规则：

- 空值/未设置 → 无限制（默认值）。
- 非空值 → 房间 ID 必须存在于列表中。此检查会在其他任何限制条件（如提及要求、发送者白名单等）之前执行。
- 应使用房间的**内部 ID**（`!abc...:server`），而非其别名（`#room:server`）。您可以在 Element 中通过“房间”→“设置”→“高级”选项找到房间的内部 ID。

另请参阅：[管理员/用户斜杠命令分离](../../reference/slash-commands.md#permissions-and-adminuser-split)。

:::提示
查找房间 ID 的方法：在 Element 中进入该房间 → **设置** → **高级**，即可看到**内部房间 ID**（以 `!` 开头）。
:::

## Matrix 中的命令

Hermes 支持与其它消息平台相同的 Matrix 网关命令，包括 `/commands`、`/model`、`/stop`、`/queue`、`/steer`、`/goal`、`/subgoal`、`/bg`、`/btw`、`/tasks` 以及 `/yolo`。

部分 Matrix 客户端会将开头的 `/` 保留给本地客户端命令，因此可能不会将未知的斜杠命令发送到房间。在这种情况下，可使用 `!` 作为符合 Matrix 规范的别名：

```text
!commands
!model
!model gpt-5.5 --provider openrouter
!queue continue with the next task
!stop
```

Hermes仅会在命令为网关所识别的命令、已注册的插件命令或已安装的技能命令时，才会将其转换为标准格式。而像`!important`这样的普通感叹号则仍会作为普通聊天消息处理。

## 故障排除

### 机器人无响应消息

**原因**：机器人未加入该房间，`MATRIX_ALLOWED_USERS`列表中未包含您的用户ID，`MATRIX_ALLOWED_ROOMS`列表中未包含该房间，或者房间内的消息未提及该机器人。

**解决方法**：将机器人邀请至该房间——它收到邀请后会自动加入。请确认您的用户ID已列入`MATRIX_ALLOWED_USERS`（需使用完整的`@user:server`格式），如果配置了允许列表，还需确保房间ID也在其中。在房间内提及该机器人，或将该房间添加到`MATRIX_FREE_RESPONSE_ROOMS`列表中。最后重启网关。

### 机器人虽加入房间但会静默丢弃所有消息（时钟偏差问题）

**原因**：主机系统时钟设置得比实际时间快。Matrix适配器会应用一个5秒的启动缓冲过滤规则（`event_ts < startup_ts - 5`），以忽略初始同步后重放的事件。当系统时钟偏快时，所有传入的事件都会被视为“早于启动时间”，从而在到达消息处理程序之前就被丢弃——因此机器人看似已连接，却从不回复。详见[#12614](https://github.com/NousResearch/hermes-agent/issues/12614)。

**症状**：网关日志中会显示“Matrix：在启动30秒后，因事件‘过旧’而丢弃了N个实时事件”。

**解决方法**：使用NTP同步主机时钟，然后重启机器人。

```bash
# Debian/Ubuntu
sudo timedatectl set-ntp true
timedatectl status   # confirm "System clock synchronized: yes"

# macOS
sudo sntp -sS time.apple.com
```

### 启动时出现“认证失败”/“whoami命令执行失败”的错误

**原因**：访问令牌或主服务器地址不正确。

**解决方法**：确认 `MATRIX_HOMESERVER` 的值指向您的主服务器（需包含 `https://`，且不能带有尾随斜杠）。同时检查 `MATRIX_ACCESS_TOKEN` 是否有效——可通过 curl 命令进行测试：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-server/_matrix/client/v3/account/whoami
```

如果返回的是您的用户信息，说明该令牌有效；若返回错误，则需要生成新的令牌。

### “未安装 mautrix”错误

**原因**：未安装 `mautrix` Python 包。

**解决方法**：请先安装该包：

```bash
pip install 'mautrix[encryption]'
```

或者通过 Hermes 的附加功能实现：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[matrix]"
```

### 加密错误 / “无法解密消息”

**原因**：缺少加密密钥、未安装 `libolm`，或机器人的设备未被信任。

**解决方案**：
1. 确认系统中已安装 `libolm`（请参阅上述端到端加密部分）。
2. 确保在 `.env` 文件中设置了 `MATRIX_ENCRYPTION=true`。
3. 在您的 Matrix 客户端（Element）中，进入机器人的个人资料 -> 会话，然后验证/信任该机器人的设备。
4. 如果机器人刚刚加入一个加密房间，它只能解密其加入后发送的消息，此前的消息则无法读取。

### 从旧版本升级到支持端到端加密的版本

:::提示
如果您还手动删除了 `crypto.db` 文件，请参阅上述端到端加密部分中的“删除加密存储”相关警告——此时还需要额外步骤来清除主服务器中过期的临时密钥。
:::

如果您之前使用 Hermes 时已设置 `MATRIX_ENCRYPTION=true`，现在要升级到采用基于 SQLite 的新加密存储的版本，那么机器人的加密身份将会发生变化。您的 Matrix 客户端（Element）可能会缓存旧的设备密钥，从而拒绝与该机器人建立加密会话。

**表现症状**：机器人能够连接成功，日志中也显示“已启用端到端加密”，但所有消息都会出现“无法解密消息”的错误，且机器人不会做出任何响应。

**问题原因**：旧的加密状态（来自之前的 `matrix-nio` 或基于序列化的 `mautrix` 后端）与新的 SQLite 加密存储机制不兼容。机器人会生成全新的加密身份，但您的 Matrix 客户端仍缓存着旧钥匙，因此不会与钥匙已变更的设备共享房间的加密会话。这是 Matrix 的安全设计机制——客户端会将同一设备的身份钥匙变更视为异常行为。

**解决方案**（一次性迁移）：

1. **生成新的访问令牌**以获取全新的设备 ID。最简单的方法是：

   ```bash
   curl -X POST https://your-server/_matrix/client/v3/login \
     -H "Content-Type: application/json" \
     -d '{
       "type": "m.login.password",
       "identifier": {"type": "m.id.user", "user": "@hermes:your-server.org"},
       "password": "***",
       "initial_device_display_name": "Hermes Agent"
     }'
   ```

复制新的 `access_token`，并更新 `~/.hermes/.env` 文件中的 `MATRIX_ACCESS_TOKEN` 值。

2. **删除旧的加密状态**：

   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db
   rm -f ~/.hermes/platforms/matrix/store/crypto_store.*
   ```

3. **设置恢复密钥**（如果您使用交叉签名机制——大多数 Element 用户都会采用该方式）。请将其添加到 `~/.hermes/.env` 文件中：

   ```bash
   MATRIX_RECOVERY_KEY=EsT... your recovery key here
   ```

这样就能让机器人 在启动时使用交叉签名密钥进行自我签名，从而使 Element 立即信任该新设备。若没有此功能，Element 可能会将新设备视为未经验证的设备，并拒绝建立加密会话。您可以在 Element 的 **设置** → **安全与隐私** → **加密** 中找到您的恢复密钥。

4. **强制您的 Matrix 客户端更换加密会话**。在 Element 中，
打开与该机器人的私信聊天室，然后输入 `/discardsession`。这样就能迫使 Element 创建一个新的加密会话，并将其分享给机器人的新设备。

5. **重启网关**：

   ```bash
   hermes gateway run
   ```

如果已设置 `MATRIX_RECOVERY_KEY`，则应在日志中看到“Matrix：通过恢复密钥完成交叉签名验证”这样的提示。

6. **发送新消息**。机器人应解密该消息并正常回复。

:::note
升级完成后，*在升级之前*发送的消息将无法被解密——因为旧的加密密钥已不存在。这仅会影响过渡阶段，新发送的消息则能正常工作。
:::

:::tip
**新安装的系统不受影响。**只有当您在使用旧版本的 Hermes 时已配置了有效的端到端加密功能并打算进行升级时，才需要进行此次迁移。

**为何需要新的访问令牌？**每个 Matrix 访问令牌都与特定的设备 ID 相关联。若使用相同的设备 ID 但搭配新的加密密钥，其他 Matrix 客户端会因识别出身份密钥的变化而怀疑该设备的安全性（认为可能存在安全漏洞）。而新的访问令牌会获得全新的设备 ID，且没有过期的密钥记录，因此其他客户端会立即信任它。
:::

## 代理模式（macOS 上的端到端加密）

Matrix 端到端加密功能需要 `libolm` 库，而该库无法在 macOS ARM64（Apple Silicon）架构上编译。因此 `hermes-agent[matrix]` 这一扩展仅适用于 Linux 系统。如果您使用的是 macOS，可通过代理模式在 Linux 虚拟机中的 Docker 容器中运行端到端加密功能，而实际的代理程序则可在 macOS 上以原生方式运行，同时拥有对本地文件、内存及各种技能的完全访问权限。

### 工作原理

```
macOS (Host):
  └─ hermes gateway
       ├─ api_server adapter ← listens on 0.0.0.0:8642
       ├─ AIAgent ← single source of truth
       ├─ Sessions, memory, skills
       └─ Local file access (Obsidian, projects, etc.)

Linux VM (Docker):
  └─ hermes gateway (proxy mode)
       ├─ Matrix adapter ← E2EE decryption/encryption
       └─ HTTP forward → macOS:8642/v1/chat/completions
           (no LLM API keys, no agent, no inference)
```

该 Docker 容器仅负责处理 Matrix 协议及端到端加密功能。当有消息到达时，它会先解密消息，再通过标准的 HTTP 请求将文本内容转发给主机。主机上运行着代理程序，该程序会调用相关工具生成响应，并将其以流式方式传回。容器则会对响应进行加密后发送至 Matrix 平台。所有会话都是统一管理的——无论是通过 CLI、Matrix、Telegram，还是其他任何平台，都能共享相同的内存和对话历史记录。

### 第 1 步：配置主机（macOS）

需启用 API 服务器，以便主机能够接收来自 Docker 容器的请求。

在 `~/.hermes/.env` 文件中添加以下内容：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=your-secret-key-here
API_SERVER_HOST=0.0.0.0
```

- 设置 `API_SERVER_HOST=0.0.0.0` 可让 Docker 容器通过所有网络接口访问该服务。
- 若需进行非回环绑定，必须设置 `API_SERVER_KEY`，建议选择一段强度较高的随机字符串。
- API 服务器默认运行在 8642 端口（如有需要，可通过 `API_SERVER_PORT` 进行修改）。

现在启动网关即可：

```bash
hermes gateway
```

您应该会看到 API 服务器与您配置的其他平台一同启动。请验证从虚拟机中是否能够访问该服务器：

```bash
# From the Linux VM
curl http://<mac-ip>:8642/health
```

### 第 2 步：配置 Docker 容器（Linux 虚拟机）

该容器需要 Matrix 认证信息以及代理地址，无需 LLM API 密钥。

**`docker-compose.yml`：**

```yaml
services:
  hermes-matrix:
    build: .
    environment:
      # Matrix credentials
      MATRIX_HOMESERVER: "https://matrix.example.org"
      MATRIX_ACCESS_TOKEN: "syt_..."
      MATRIX_ALLOWED_USERS: "@you:matrix.example.org"
      MATRIX_ENCRYPTION: "true"
      MATRIX_DEVICE_ID: "HERMES_BOT"

      # Proxy mode — forward to host agent
      GATEWAY_PROXY_URL: "http://192.168.1.100:8642"
      GATEWAY_PROXY_KEY: "your-secret-key-here"
    volumes:
      - ./matrix-store:/root/.hermes/platforms/matrix/store
```

**`Dockerfile`：**

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y libolm-dev && rm -rf /var/lib/apt/lists/*
RUN cd ~/.hermes/hermes-agent && uv pip install -e ".[matrix]"

CMD ["hermes", "gateway"]
```

这就是整个容器内容。其中不包含 OpenRouter、Anthropic 或任何推理服务提供商的 API 密钥。

### 第 3 步：同时启动两者

1. 首先启动主机网关：
   ```bash
   hermes gateway
   ```

2. 启动 Docker 容器：
   ```bash
   docker compose up -d
   ```

3. 在加密的 Matrix 房间中发送消息。容器会对消息进行解密，然后将其转发给主机，并将回复流式传回。

### 配置参考

代理模式是在**容器端**（即轻量级网关）进行配置的：

| 设置项 | 描述 |
|--------|------|
| `GATEWAY_PROXY_URL` | 远程 Hermes API 服务器的 URL（例如：`http://192.168.1.100:8642`） |
| `GATEWAY_PROXY_KEY` | 用于身份验证的承载令牌（必须与主机上的 `API_SERVER_KEY` 相匹配） |
| `gateway.proxy_url` | 在 `config.yaml` 文件中对应的设置，含义与 `GATEWAY_PROXY_URL` 相同 |

主机端则需要配置以下参数：

| 设置项 | 描述 |
|--------|------|
| `API_SERVER_ENABLED` | 设置为 `true` |
| `API_SERVER_KEY` | 承载令牌（需与容器共享） |
| `API_SERVER_HOST` | 设置为 `0.0.0.0` 以实现网络访问 |
| `API_SERVER_PORT` | 端口编号（默认值为 `8642`） |

### 适用于任何平台

代理模式不仅限于 Matrix 平台。任何平台适配器均可使用该功能——只需在任何网关实例上设置 `GATEWAY_PROXY_URL`，它就会将请求转发给远程代理，而无需在本地运行代理。这对于那些需要将平台适配器与代理运行在不同环境中的部署场景非常有用（如网络隔离、端到端加密需求或资源限制等）。

:::tip
通过 `X-Hermes-Session-Id` 请求头可保持会话连续性。主机的 API 服务器会通过该 ID 来跟踪会话，因此消息之间的对话能够像使用本地代理时一样持续保留。
:::

:::note
**v1版本的局限性：** 远程智能体的工具执行进度信息不会被反馈回来——用户只能看到最终的流式响应，而无法查看各个工具调用的详细情况。危险命令的确认提示会在主机端处理，而不会传递给Matrix用户。这些问题将在后续版本中得到解决。
:::

### 智能体已连接并能够发送消息，但忽略接收到的消息

**原因**：Matrix事件处理器仅在通过mautrix的`handle_sync()`机制发送同步数据时才会被触发。如果直接使用`client.sync()`进行轮询且从未调用`handle_sync()`，虽然智能体仍保持连接状态（能够发送消息），但接收到的消息却永远无法到达 `_on_room_message` 处理函数。

**解决方案**：Hermes采用了显式的同步循环机制，在初始同步以及每次增量同步响应时都会调用`client.handle_sync()`。这一设计与上游问题#7914的诊断结果以及已关闭的PR #37807一致，同时还能让Hermes独立处理自身的后台维护任务（如已加入房间的跟踪、邀请处理、端到端加密密钥共享等），而无需将整个生命周期都委托给`client.start()`。如果重启网关后接收消息的问题依然存在，请确认在首次同步之前事件处理器已正确注册，并检查日志中是否有“同步事件发送错误”的记录。

### 同步问题/智能体响应延迟

**原因**：耗时较长的工具执行可能会拖慢同步循环的进度，或者是因为主服务器性能不足。

**解决方案**：同步循环会在出现错误时自动每5秒尝试重试一次。请查看Hermes的日志以查找与同步相关的警告信息。如果智能体持续出现响应延迟的情况，请确保您的主服务器拥有足够的资源。

### 机器人处于离线状态

**原因**：Hermes 网关未运行，或连接失败。

**解决方法**：检查 `hermes gateway` 是否正在运行，并查看终端输出中的错误信息。常见问题包括：homeserver URL 错误、访问令牌已过期、无法连接到 homeserver。

### 出现“用户未被授权”/机器人忽略您

**原因**：您的用户 ID 不在 `MATRIX_ALLOWED_USERS` 列表中。

**解决方法**：将您的用户 ID 添加到 `~/.hermes/.env` 文件中的 `MATRIX_ALLOWED_USERS` 列表中，然后重启网关。请使用完整的 `@user:server` 格式。

### 机器人忽略整个房间

**原因**：已设置了 `MATRIX_ALLOWED_ROOMS`，但当前房间 ID 未列入其中；或者该房间要求被提及，而消息中并未提及机器人。

**解决方法**：将相应房间 ID 添加到 `MATRIX_ALLOWED_ROOMS` 中；如果是个人部署，则可删除该房间的允许列表。在 Element 中查找房间 ID，可进入房间设置并查看 **Advanced** 选项。

### 桥接消息出现循环或回声现象

**原因**：桥接组件或 appservice 的 puppet 正以新用户消息的形式转发机器人的输出；或者桥接使用了非标准的虚拟用户 ID。

**解决方法**：避免将桥接使用的虚拟用户纳入 `MATRIX_ALLOWED_USERS`，添加相应的 `MATRIX_IGNORE_USER_PATTERNS` 条目；除非通知属于可信工作流程的一部分，否则请保持 `MATRIX_PROCESS_NOTICES=false` 的设置。

## 安全性

:::warning
务必设置 `MATRIX_ALLOWED_USERS`，在共享或私有部署环境中还需设置 `MATRIX_ALLOWED_ROOMS`。若不设置这些参数，任何能够在所加入的聊天室中向机器人发送消息的用户都可能触发该智能体。请仅授权您信任的人员和聊天室——获得授权的用户将拥有该智能体全部功能的使用权限，包括工具调用和系统访问权限。
:::

如需了解有关保障 Hermes Agent 部署安全的更多信息，请参阅 [安全指南](../security.md)。

## 备注

- **任意家园服务器**：可兼容 Synapse、Conduit、Dendrite、matrix.org 以及所有符合规范的 Matrix 家园服务器，无需特定服务器软件。  
- **联盟功能**：若使用联盟型家园服务器，该机器人即可与其他服务器的用户进行通信——只需将他们的完整 `@user:server` 用户标识添加到 `MATRIX_ALLOWED_USERS` 中即可。  
- **自动加入房间**：机器人会自动接受房间邀请并加入，加入后立即开始响应。  
- **媒体支持**：Hermes 能够发送和接收图片、音频、视频以及文件附件。这些媒体内容会通过 Matrix 内容存储库 API 上传至您的家园服务器。  
- **原生语音消息（MSC3245）**：Matrix 适配器会自动为发送的语音消息添加 `org.matrix.msc3245.voice` 标签。这样一来，文本转语音回复及语音音频将在 Element 及其他支持 MSC3245 的客户端中以**原生语音气泡**形式呈现，而非普通的音频文件附件。带有 MSC3245 标签的接收语音消息也会被正确识别并转送至语音转文字功能。此功能无需任何配置，可自动生效。
