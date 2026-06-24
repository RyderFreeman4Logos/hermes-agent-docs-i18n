---
sidebar_position: 9
title: "Matrix"
description: "Set up Hermes Agent as a Matrix bot"
---

# Matrix 设置

Hermes Agent 能够与开源的联邦式消息协议 Matrix 相集成。通过 Matrix，你可以自行搭建服务器，或使用像 matrix.org 这样的公共服务器——无论哪种方式，你都能掌控自己的通信内容。该机器人通过 `mautrix` Python SDK 进行连接，通过 Hermes Agent 的处理流程（包括工具调用、内存管理及推理功能）来处理消息，并实现实时响应。它支持文本、文件附件、图片、音频、视频传输，同时还提供可选的端到端加密（E2EE）功能。

Hermes Agent 可与任何 Matrix 服务器配合使用——无论是 Synapse、Conduit、Dendrite，还是 matrix.org。

在开始设置之前，这里有大多数人最关心的问题：即 Hermes Agent 连接后会有怎样的表现。

## Hermes Agent 的运行行为

| 场景 | 行为表现 |
|------|----------|
| **私信** | Hermes Agent 会回复每一条消息，无需使用 `@mention` 指定。每条私信都会拥有独立的对话会话。若希望当机器人在私信中被 `@提及` 时自动开启话题串，可设置 `MATRIX_DM_MENTION_THREADS=true`。 |
| **群组** | 默认情况下，Hermes Agent 需要通过 `@mention` 才会回复消息。如需允许无需提及即可回复，可设置 `MATRIX_REQUIRE_MENTION=false`，或将为自由回复群组添加对应的群组 ID 到 `MATRIX_FREE_RESPONSE_ROOMS` 中。群组邀请将自动被接受。 |
| **话题串** | Hermes Agent 支持 Matrix 的话题串功能（MSC3440 标准）。如果你在话题串中回复消息，Hermes Agent 会将该话题串的上下文与主群组的消息流分开处理。对于机器人已经参与过的话题串，无需再次提及即可回复。 |
| **自动创建话题串** | 默认情况下，Hermes Agent 会在群组中为每条回复消息自动创建一个独立的话题串，从而保持对话的隔离性。如需关闭此功能，可设置 `MATRIX_AUTO_THREAD=false`。若同时希望为私信消息也自动创建话题串（该功能与仅在私信中被提及时才创建话题串的 `MATRIX_DM_MENTION_THREADS` 不同），可设置 `MATRIX_DM_AUTO_THREAD=true`（默认值为 false）。 |
| **命令处理** | 当你的 Matrix 客户端发送常规的 `/commands` 命令时，Hermes Agent 会予以响应。如果你的客户端将 `/` 符号预留用于本地命令，可使用 `!commands` 代替；Hermes Agent 会将已知的 `!command` 别名自动转换为 `/command` 格式。 |
| **交互式控制** | 对危险命令的审批以及 `/model` 模型选择功能均可通过 Matrix 反应功能实现。审批相关的反应仅限于发起该操作的用户可见。 |
| **思考过程与工具使用状态显示** | 当启用网关进度显示功能时，Matrix 会使用带分隔线的可编辑面板来展示机器人的思考过程及工具使用状态，这样就不会让主群组消息流被大量更新信息淹没。 |
| **多用户共享群组** | 默认情况下，Hermes Agent 会为群组内的每位用户单独维护对话历史记录。除非你明确禁用此功能，否则同群组内的不同用户之间不会共享对话记录。 |

:::提示
只需将机器人的 Matrix 用户邀请到任意群组中，它就会自动加入并开始响应消息。
:::

## 功能矩阵

该表格基于 Matrix 适配器的功能声明及测试覆盖率编制。端到端加密功能的启用状态取决于部署方式：可能是完全禁用、按需启用，或是强制要求使用。

| 功能 | Matrix 支持情况 |
|------|----------------|
| 文本消息 | 支持 |
| 话题串 | 支持 |
| 反应功能 | 支持 |
| 审批功能 | 支持 |
| 模型选择器 | 支持 |
| 思考过程显示面板 | 支持 |
| 图片传输 | 支持 |
| 多张图片传输 | 支持 |
| 文件上传 | 支持 |
| 语音/音频传输 | 支持 |
| 视频传输 | 支持 |
| 端到端加密 | 关闭 / 可选 / 强制要求 |
| 诊断功能 | 支持 |

### Matrix 中的会话模型

默认设置下：
- 每条私信拥有独立的对话会话
- 每个话题串拥有独立的会话命名空间
- 共享群组中的每位用户在该群组内也拥有独立的会话

这些设置可通过 `config.yaml` 文件进行配置：

```yaml
group_sessions_per_user: true
```

仅当您明确希望为整个房间设置单一的共享对话时，才将其设置为 `false`：

```yaml
group_sessions_per_user: false
```

共享会话虽有利于协作交流，但同时也存在以下问题：

- 用户需共同承担上下文存储空间的增长及令牌成本
- 某人执行的长时间、依赖大量工具的任务可能会占用其他所有人的上下文空间
- 同一房间内，某人正在运行的任务可能会干扰另一人的后续操作

### 提及与主题自动划分配置

您可以通过环境变量或 `config.yaml` 文件来配置提及功能及自动主题划分的行为：

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
将 `MATRIX_REACTIONS=false` 设置后，机器人便不会在收到的消息上添加处理流程相关的表情反应（👀/✅/❌）。这对于那些表情反应信息过多，或并非所有参与客户端都支持该功能的房间尤为有用。  
:::

:::提示 全房间提及  
Hermes 会为带有明确 Matrix 用户 ID 的内容（如 `@alice:example.org`）发送结构化的 Matrix 用户提及信息。默认情况下，全房间范围的 `@room` 通知是被禁用的；仅当允许机器人向所有成员发送通知时，才需将 `MATRIX_ALLOW_ROOM_MENTIONS=true` 设置为 true。  
:::

:::注意  
如果您是从未包含 `MATRIX_REQUIRE_MENTION` 该参数的版本升级而来，之前的机器人会回应房间中的所有消息。如需保持此行为，请将 `MATRIX_REQUIRE_MENTION=false` 设置为 true。  
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
| `room` | 非线程形式的房间消息会保留在同一个稳定的房间会话中，而真实的 Matrix 线程则仍沿用其所属的线程根节点。 |
| `thread` | 非线程形式的房间消息会根据触发事件的 ID 生成一个新的线程/会话。 |

Hermes 现在会在智能体提示信息中包含当前的 Matrix 房间名称、房间 ID、主题、消息 ID，以及与房间边界相关的信息。通过 `/status` 命令也可查看当前的 Matrix 房间/会话范围；而 `/resume` 命令不会自动从另一个 Matrix 房间恢复已命名的会话，除非你明确使用 ` /resume --cross-room <session name>` 参数。

`MATRIX_SESSION_SCOPE=room` 用于控制房间/线程的通道划分。原有的 `group_sessions_per_user` 设置依然决定该房间内的用户是否共享同一通道。当 `group_sessions_per_user: true`（默认值）时，Alice 和 Bob 将拥有独立的 Project B 会话；而当 `group_sessions_per_user: false` 时，整个房间将共享同一个 Project B 记录。

本指南将引导你完成从创建机器人账户到发送第一条消息的完整设置流程。

## 第一步：创建机器人账户

你需要为机器人配置一个 Matrix 用户账户。实现这一目标有多种方法：

### 方案 A：在自建主机上注册（推荐）

如果你拥有自己的主机服务器（如 Synapse、Conduit、Dendrite）：

1. 使用管理 API 或注册工具创建一个新的用户：

```bash
# Synapse example
register_new_matrix_user -c /etc/synapse/homeserver.yaml http://localhost:8008
```

2. 选择一个用户名，例如 `hermes`——完整的用户 ID 将为 `@hermes:your-server.org`。

### 方案 B：使用 matrix.org 或其他公共主服务器

1. 访问 [Element Web](https://app.element.io) 并创建一个新账户。
2. 为您的机器人选择一个用户名（例如 `hermes-bot`）。

### 方案 C：使用您自己的账户

您也可以以自己的用户身份运行 Hermes。这意味着机器人将代表您发布消息——非常适合用于个人助手。

## 第 2 步：获取访问令牌

Hermes 需要访问令牌才能与主服务器进行身份验证。您有两种选择：

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
该访问令牌可让您完全控制机器人的 Matrix 账户。切勿将其公开分享或提交到 Git 中。如果令牌泄露，请通过退出该用户的所有会话来撤销其权限。
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
Matrix用户ID始终以`@`开头，其后包含一个冒号以及服务器名称。例如：`@alice:matrix.org`、`@bob:your-server.com`。
:::

## 第4步：配置Hermes Agent

### 方案A：交互式设置（推荐）

运行引导式设置命令：

```bash
hermes gateway setup
```

系统提示时请选择 **Matrix**，随后在要求输入信息时提供您的主服务器地址、访问令牌（或用户 ID 加密码），以及允许访问的用户 ID。

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

## 私有环境部署加固

对于私有 Matrix 部署，需同时设置用户白名单和房间白名单。如果未设置 `MATRIX_ALLOWED_USERS`，则任何能够在已加入的房间中联系到该机器人的发送者均可触发代理响应。而若未设置 `MATRIX_ALLOWED_ROOMS`，机器人所加入的任何房间都可能触发代理响应。为确保部署安全，应同时配置这两项设置。

```bash
MATRIX_ALLOWED_USERS=@alice:matrix.example.org,@bob:matrix.example.org
MATRIX_ALLOWED_ROOMS=!ops:matrix.example.org,!dmroom:matrix.example.org
```

桥接节点与 AppService 类型的部署需要额外的循环保护机制。默认情况下，Hermes 会忽略自身的事件、本地部分以“_”开头的 Matrix AppService 风格用户发送的事件、重复的事件 ID、旧的启动事件、编辑替换事件以及 `m.notice` 类型的事件。如果您的桥接节点采用了不同的命名规则，则需要添加针对该部署的专用桥接节点过滤模式：

```bash
MATRIX_IGNORE_USER_PATTERNS='^@telegram_,^@slack_,^@whatsapp_'
```

仅当可信的人工工作流真正发送了 `m.notice` 时，才启用通知功能：

```bash
MATRIX_PROCESS_NOTICES=true
```

默认情况下，向整个房间发送通知的功能处于禁用状态。除非明确允许该机器人使用`@room`指令唤醒整个房间，否则请保持`MATRIX_ALLOW_ROOM_MENTIONS=false`的设置。

诊断与调试相关的数据包会对Matrix访问令牌、恢复密钥、设备标识符以及消息内容进行遮蔽处理。媒体文件下载仅限于Matrix格式的`mxc://`内容URI，且当文件大小超过`MATRIX_MAX_MEDIA_BYTES`限制时将被拒绝。应将联合房间及不可信的本地服务器视为不可信输入：严格管理房间白名单，对于需要使用大量工具的任务，优先选择私信或私人房间进行操作；同时避免将桥接机器人或AppService傀儡授权为允许用户。

在`~/.hermes/config.yaml`中可配置以下可选行为设置：

```yaml
group_sessions_per_user: true
```

- `group_sessions_per_user: true` 可确保在共享房间中，每位参与者的上下文彼此隔离。

### 启动网关

配置完成后，即可启动 Matrix 网关：

```bash
hermes gateway
```

该机器人应能在几秒钟内连接到您的家庭服务器并开始同步。您可以通过私信或在其加入的频道中发送消息来对其进行测试。

:::提示
为确保持续运行，您可以将 `hermes gateway` 在后台运行或作为 systemd 服务启动。详情请参阅部署指南。
:::

## 端到端加密 (E2EE)

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

`MATRIX_E2EE_MODE` 支持以下取值：

| 模式 | 行为说明 |
|------|----------|
| `off` | 不初始化 Matrix E2EE 功能。 |
| `optional` | 在具备相关依赖条件时尝试启用 E2EE，但如果加密功能无法初始化，则仍允许使用未加密的房间。 |
| `required` | 若缺少 E2EE 相关依赖或加密设置，则直接终止运行。 |

在加密设置不可用时，`optional` 模式会回退到非 E2EE 模式运行；而 `required` 模式则不会默默降级，而是直接终止运行。

为保持向后兼容性，即使设置 `MATRIX_ENCRYPTION=true`，也会启用 `required` 模式的 E2EE 行为。

当启用 E2EE 后，Hermes 会：  
- 将加密密钥存储在 `~/.hermes/platforms/matrix/store/` 目录中（旧版本安装路径为 `~/.hermes/matrix/store/`）；  
- 在首次连接时上传设备密钥；  
- 自动解密接收到的消息并加密发送的消息；  
- 接到邀请时自动加入加密房间。  

### Matrix 工具与控制功能

在 Matrix 对话中，Hermes 会向智能体提供针对 Matrix 的专用工具：  
- `matrix_send_reaction`  
- `matrix_redact_message`  
- `matrix_create_room`  
- `matrix_invite_user`  
- `matrix_fetch_history`  
- `matrix_set_presence`  

这些工具仅适用于 Matrix 场景，在非 Matrix 工具集中不可用。管理类工具默认处于禁用状态：需要启用内容屏蔽功能则需设置 `MATRIX_TOOLS_ALLOW_REDACTION=true`，需要发送邀请则需设置 `MATRIX_TOOLS_ALLOW_INVITES=true`，需要创建房间则需设置 `MATRIX_TOOLS_ALLOW_ROOM_CREATE=true`。创建公共房间还需额外设置 `MATRIX_ALLOW_PUBLIC_ROOMS=true`。  
默认情况下，Matrix 工具仅能作用于当前房间。若需明确指定跨房间操作目标，则需设置 `MATRIX_TOOLS_ALLOW_CROSS_ROOM=true`；而内容屏蔽及类似邀请的跨房间操作还需额外设置 `MATRIX_TOOLS_ALLOW_CROSS_ROOM_DESTRUCTIVE=true`。如果设置了 `MATRIX_ALLOWED_ROOMS`，Matrix 工具则只能作用于那些被允许的房间。  

表情反应控制功能支持以下选项：  
- ✅ 仅批准一次  
- ♾️ 始终批准  
- ❌ 拒绝  
- 对 `/model` 选项支持数量型表情反应  

如果希望允许房间内的任何授权 Matrix 用户来操作审批或模型选择功能，可设置 `MATRIX_APPROVAL_REQUIRE_SENDER=false`。默认情况下，只要 Hermes 知道是谁提出了该操作请求，审批权限就仅限于该请求者。  

### 媒体文件大小限制

Hermes 通过 Matrix 媒体 API 来上传和下载图像、文件、音频及视频等媒体内容。多个生成的图像会作为一个有序的逻辑批次发送，从而在批次之间保留字幕和对话上下文信息。  

默认情况下，超过 100 MB 的 Matrix 媒体文件在上传/下载前会被拒绝。如需更改此限制，可进行相应配置：

```bash
MATRIX_MAX_MEDIA_BYTES=104857600
```

传入的媒体内容必须使用 Matrix 的 `mxc://` 格式内容 URI。为避免将联合房间转变为无限制的下载工具，Hermes 会拒绝在 Matrix 消息中出现的任意 HTTP(S) 媒体 URL。

## Synapse 集成测试

Hermes 提供了可选的 Synapse 测试框架，用于进行本地验证：

```bash
docker compose -f tests/e2e/matrix_synapse_gateway/docker-compose.yml up -d
HERMES_MATRIX_SYNAPSE_INTEGRATION=1 \
  scripts/run_tests.sh -m "integration and matrix_synapse" \
  tests/e2e/matrix_synapse_gateway/test_gateway.py
docker compose -f tests/e2e/matrix_synapse_gateway/docker-compose.yml down -v
```

该代理通过 Synapse 共享密钥注册机制创建临时用户，支持私密房间内的发送/接收、命名房间的邀请/加入、媒体文件的上传/下载、机器人响应的传递，以及启动时的旧事件过滤功能。端到端加密相关的测试用例会以 `matrix_e2ee` 的标记单独标识，从而确保开发人员可在其设备上自主选择是否启用该功能。

### 交叉签名验证（推荐）

如果您的 Matrix 账户已开启交叉签名功能（Element 默认即已开启），请设置恢复密钥，以便机器人在启动时能够对自身设备进行自签名。若未设置此功能，在设备密钥更换后，其他 Matrix 客户端可能会拒绝与该机器人共享加密会话。

```bash
MATRIX_RECOVERY_KEY=EsT... your recovery key here
```

**查找位置：** 在 Element 中，进入 **Settings** → **Security & Privacy** → **Encryption**，即可找到您的恢复密钥（也称为“安全密钥”）。这正是您在首次设置交叉签名功能时被要求保存的密钥。

每次启动时，如果已设置 `MATRIX_RECOVERY_KEY`，Hermes 会从主服务器的安全密钥存储中导入交叉签名密钥，并对当前设备进行签名。该操作具有幂等性，因此可以永久保持启用状态而无需担心安全问题。

若 Hermes 生成了新的 Matrix 恢复密钥，它绝不会记录原始密钥的内容。您可以在启动前设置 `MATRIX_RECOVERY_KEY_OUTPUT_FILE=/secure/path/matrix-recovery-key.txt`，以文件权限 `0600` 将生成的密钥写入该文件；如果该文件已存在，则不会被覆盖。

:::warning[删除加密存储库]
如果您删除了 `~/.hermes/platforms/matrix/store/crypto.db`，该机器人将失去其加密身份。仅使用相同的设备 ID 重新启动是无法完全恢复功能的——主服务器仍保存着用旧身份密钥签名的一次性密钥，因此其他节点无法建立新的 Olm 会话。

Hermes 在启动时会检测到这种情况，并拒绝启用端到端加密，同时会记录如下信息：`device XXXX has stale one-time keys on the server signed with a previous identity key`。

**最简单的恢复方法：生成新的访问令牌**（这样会获得一个全新的设备 ID，且没有过期的密钥记录）。请参阅下文的“从旧版本带有端到端加密功能的系统升级”部分。这是最可靠的解决方案，且无需修改主服务器的数据库。

**手动恢复**（较复杂——需保留原有的设备 ID）：

1. 停止 Synapse 进程，并从其数据库中删除旧设备记录：
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
或者通过 Synapse 管理员 API 实现（注意用户 ID 需要进行 URL 编码）：
   ```bash
   curl -X DELETE -H "Authorization: Bearer ADMIN_TOKEN" \
     'https://your-server/_synapse/admin/v2/users/%40hermes%3Ayour-server/devices/DEVICE_ID'
   ```
注意：通过管理 API 删除设备也可能会导致关联的访问令牌失效，此时您可能需要重新生成新的令牌。

2. 删除本地加密存储并重启 Hermes：
   ```bash
   rm -f ~/.hermes/platforms/matrix/store/crypto.db*
   # restart hermes
   ```

其他 Matrix 客户端（如 Element、matrix-commander）可能会缓存旧的设备密钥。恢复后，在 Element 中输入 `/discardsession` 即可强制与机器人建立新的加密会话。
:::

:::info
如果未安装 `mautrix[encryption]` 或缺少 `libolm`，机器人将自动回退到普通（未加密）客户端。您会在日志中看到相关警告。
:::

## 主房间

您可以指定一个“主房间”，机器人会向该房间发送主动消息（如定时任务输出、提醒和通知）。设置方法有两种：

### 使用斜杠命令

在机器人所在的任意 Matrix 房间中输入 `/sethome`，该房间即成为主房间。
如果您的 Matrix 客户端拦截了斜杠命令，则请使用 `!sethome`。

### 手动配置

在您的 `~/.hermes/.env` 文件中添加以下内容：

```bash
MATRIX_HOME_ROOM=!abc123def456:matrix.example.org
```

## 房间白名单（`allowed_rooms`）

可将机器人限制在特定的 Matrix 房间范围内。启用该设置后，机器人**仅**会在列表中列出的房间内响应消息——来自其他任何房间的消息都将被直接忽略，即便提到了该机器人也是如此。

**私信对话室**不受此过滤规则限制，因此授权用户始终可以与机器人进行一对一交流。

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
- 应使用房间的**内部 ID**（`!abc...:server`），而非其别名（`#room:server`）。你可以在 Element 中通过“房间”→“设置”→“高级”选项找到房间的内部 ID。

另请参阅：[管理员/用户斜杠命令分离](../../reference/slash-commands.md#permissions-and-adminuser-split)。

:::提示
查找房间 ID 的方法：在 Element 中进入该房间 → **设置** → **高级**，即可看到**内部房间 ID**（以 `!` 开头）。
:::

## Matrix 中的命令

Hermes 支持与其它消息平台相同的 Matrix 网关命令，包括 `/commands`、`/model`、`/stop`、`/queue`、`/steer`、`/goal`、`/subgoal`、`/background`、`/bg`、`/btw`、`/tasks` 以及 `/yolo`。

某些 Matrix 客户端会将开头的 `/` 保留给本地客户端命令，因此可能不会将未知的斜杠命令发送到房间。在这种情况下，可使用 `!` 作为符合 Matrix 规范的别名：

```text
!commands
!model
!model gpt-5.5 --provider openrouter
!queue continue with the next task
!stop
```

Hermes 仅会在命令为网关所识别的命令、已注册的插件命令或已安装的技能命令时，才会将其转换为标准格式。而诸如 `!important` 这样的普通感叹号标记则仍会被视为普通聊天消息。

## 故障排除

### 机器人未响应消息

**原因**：机器人尚未加入该房间，`MATRIX_ALLOWED_USERS` 列表中未包含您的用户 ID，`MATRIX_ALLOWED_ROOMS` 列表中未包含该房间，或者房间内的消息中未提及该机器人。

**解决方法**：将机器人邀请至该房间——收到邀请后它会自动加入。请确认您的用户 ID 已添加到 `MATRIX_ALLOWED_USERS` 中（需使用完整的 `@user:server` 格式），并且如果已配置允许列表，还需确保房间 ID 已添加到 `MATRIX_ALLOWED_ROOMS` 中。在房间内提及该机器人，或将该房间添加到 `MATRIX_FREE_RESPONSE_ROOMS` 中。最后重启网关。

### 机器人虽加入房间但会静默丢弃所有消息（时钟偏差问题）

**原因**：主机系统的时钟设置得比实际时间快。Matrix 适配器会应用一个 5 秒的启动缓冲过滤规则（`event_ts < startup_ts - 5`），用于忽略初始同步后重放的事件。当系统时钟偏快时，所有传入的事件都会被视为“早于启动时间”，从而在到达消息处理程序之前就被丢弃——此时机器人看似已连接，但实际上不会回复。详见 [#12614](https://github.com/NousResearch/hermes-agent/issues/12614)。

**症状**：网关日志中会显示“Matrix：启动 30 秒后因事件‘过旧’而丢弃了 N 个实时事件”。

**解决方法**：使用 NTP 同步主机时钟，然后重启机器人。

```bash
# Debian/Ubuntu
sudo timedatectl set-ntp true
timedatectl status   # confirm "System clock synchronized: yes"

# macOS
sudo sntp -sS time.apple.com
```

### 启动时出现“认证失败”/“whoami命令执行失败”

**原因**：访问令牌或主服务器地址不正确。

**解决方法**：确认 `MATRIX_HOMESERVER` 的值指向您的主服务器（需包含 `https://`，且末尾不能有斜杠）。同时检查 `MATRIX_ACCESS_TOKEN` 是否有效——可使用 curl 命令进行测试：

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

或者使用 Hermes 的附加功能：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[matrix]"
```

### 加密错误 / “无法解密消息”

**原因**：缺少加密密钥、未安装 `libolm`，或机器人的设备未被信任。

**解决方案**：
1. 确认系统中已安装 `libolm`（参见上文中的端到端加密部分）。
2. 确保在 `.env` 文件中设置了 `MATRIX_ENCRYPTION=true`。
3. 在您的 Matrix 客户端（Element）中，进入机器人的个人资料 -> 会话 -> 信任该机器人的设备。
4. 如果机器人刚刚加入一个加密房间，它只能解密其加入后发送的消息，之前的消息则无法读取。

### 从旧版本升级到支持端到端加密的版本

:::提示
如果您还手动删除了 `crypto.db` 文件，请参阅上文端到端加密部分中的“删除加密存储”相关警告——此时还需要额外步骤来清除主服务器中过期的临时密钥。
:::

如果您之前使用 Hermes 时已设置 `MATRIX_ENCRYPTION=true`，现在要升级到采用新 SQLite 基础加密存储的版本，那么机器人的加密身份将会发生变化。您的 Matrix 客户端（Element）可能会缓存旧的设备密钥，从而拒绝与该机器人共享加密会话。

**症状**：机器人成功连接，日志中也显示“已启用端到端加密”，但所有消息都显示“无法解密消息”，且机器人始终不回复。

**原因**：旧版本的加密状态（来自之前的 `matrix-nio` 或基于序列化的 `mautrix` 后端）与新的 SQLite 加密存储不兼容。虽然机器人会生成新的加密身份，但您的 Matrix 客户端仍保留着旧的密钥缓存，因此不会与密钥已变更的设备共享房间的加密会话。这是 Matrix 的一项安全机制——客户端会将同一设备的身份密钥变更视为异常行为。

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

3. **设置恢复密钥**（如果您使用交叉签名机制——大多数 Element 用户都会采用此方式）。请将其添加到 `~/.hermes/.env` 文件中：

   ```bash
   MATRIX_RECOVERY_KEY=EsT... your recovery key here
   ```

这样就能让机器人在上电时使用交叉签名密钥进行自我签名，从而使 Element 立即信任该新设备。若没有这一机制，Element 可能会将新设备视为未经验证的设备，并拒绝建立加密会话。您可以在 Element 的 **设置** → **安全与隐私** → **加密** 中找到您的恢复密钥。

4. **强制您的 Matrix 客户端更换加密会话**。在 Element 中，进入与该机器人的私信房间，然后输入 `/discardsession`。这将强制 Element 创建一个新的加密会话，并将其分享给机器人的新设备。

5. **重启网关**：

   ```bash
   hermes gateway run
   ```

如果已设置 `MATRIX_RECOVERY_KEY`，则应在日志中看到“Matrix：通过恢复密钥完成交叉签名验证”这样的提示。

6. **发送新消息**。机器人应解密该消息并正常回复。

:::note
升级完成后，*在升级之前*发送的消息将无法被解密——因为旧的加密密钥已不复存在。这仅会影响过渡阶段，新发送的消息则能正常工作。
:::

:::tip
**新安装的系统不受影响。**只有当您在使用旧版本的 Hermes 时已建立了正常的端到端加密功能，现在需要升级时，才需要进行此次迁移。

**为何需要新的访问令牌？**每个 Matrix 访问令牌都与特定的设备 ID 相关联。若使用相同的设备 ID 但搭配新的加密密钥，会导致其他 Matrix 客户端对该设备产生不信任（它们会将变更后的身份密钥视为潜在的安全风险）。而新的访问令牌会获得一个没有旧密钥记录的新设备 ID，因此其他客户端会立即对其信任。
:::

## 代理模式（macOS 上的端到端加密）

Matrix 端到端加密功能需要 `libolm` 库，但该库无法在 macOS ARM64（Apple Silicon）架构上编译。因此 `hermes-agent[matrix]` 这一扩展仅适用于 Linux 系统。如果您使用的是 macOS，代理模式允许您在 Linux 虚拟机中的 Docker 容器中运行端到端加密功能，而实际的代理程序则可在 macOS 上以原生方式运行，同时拥有对本地文件、内存及技能的完全访问权限。

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

该 Docker 容器仅负责处理 Matrix 协议及端到端加密功能。当有消息到达时，它会解密消息，并通过标准的 HTTP 请求将文本内容转发给主机。主机上运行着代理程序，该程序会调用相关工具生成响应，然后将其流式发送回容器。容器则会对响应进行加密，再将其发送至 Matrix 平台。所有会话都是统一管理的——无论是通过 CLI、Matrix、Telegram，还是其他任何平台，都能共享相同的内存和对话历史记录。

### 第 1 步：配置主机（macOS）

需启用 API 服务器，以便主机能够接收来自 Docker 容器的请求。

请在 `~/.hermes/.env` 文件中添加相应配置：

```bash
API_SERVER_ENABLED=true
API_SERVER_KEY=your-secret-key-here
API_SERVER_HOST=0.0.0.0
```

- 设置 `API_SERVER_HOST=0.0.0.0` 可使服务绑定到所有网络接口，从而确保 Docker 容器能够访问该服务。
- 若需绑定到非回环地址，则必须设置 `API_SERVER_KEY`，建议选用一个强度较高的随机字符串。
- API 服务器默认运行在端口 8642 上（如需更改，可使用 `API_SERVER_PORT` 参数进行设置）。

现在启动网关即可：

```bash
hermes gateway
```

您应该会看到 API 服务器与您配置的其他平台一同启动。请在虚拟机中验证是否能够访问该服务器：

```bash
# From the Linux VM
curl http://<mac-ip>:8642/health
```

### 第 2 步：配置 Docker 容器（Linux 虚拟机）

该容器需要 Matrix 认证信息以及代理服务器地址，无需 LLM API 密钥。

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

这就是整个容器。其中不包含 OpenRouter、Anthropic 或任何推理服务提供商的 API 密钥。

### 第 3 步：同时启动两者

1. 首先启动主机网关：
   ```bash
   hermes gateway
   ```

2. 启动 Docker 容器：
   ```bash
   docker compose up -d
   ```

3. 在加密的 Matrix 房间中发送消息。容器会先解密该消息，再将其转发给主机，最后将响应流式传回。

### 配置参考

代理模式在**容器端**（即轻量级网关）进行配置：

| 设置项 | 描述 |
|--------|------|
| `GATEWAY_PROXY_URL` | 远程 Hermes API 服务器的 URL（例如：`http://192.168.1.100:8642`） |
| `GATEWAY_PROXY_KEY` | 用于身份验证的令牌（必须与主机上的 `API_SERVER_KEY` 相匹配） |
| `gateway.proxy_url` | 在 `config.yaml` 文件中，其含义与 `GATEWAY_PROXY_URL` 相同 |

主机端则需要配置以下内容：

| 设置项 | 描述 |
|--------|------|
| `API_SERVER_ENABLED` | 设为 `true` |
| `API_SERVER_KEY` | 令牌（需与容器端共享） |
| `API_SERVER_HOST` | 设为 `0.0.0.0` 以实现网络访问 |
| `API_SERVER_PORT` | 端口编号（默认值为 `8642`） |

### 适用于任何平台

代理模式不仅限于 Matrix。任何平台适配器均可使用该功能——只需在任意网关实例上设置 `GATEWAY_PROXY_URL`，它就会将请求转发至远程代理，而无需在本地运行代理。这对于那些需要将平台适配器部署在与代理不同环境中的场景非常有用（如网络隔离、端到端加密需求、资源限制等）。

:::tip
通过 `X-Hermes-Session-Id` 标头可保持会话连续性。主机的 API 服务器会依据此 ID 来跟踪会话，因此消息之间的对话能够像使用本地代理时一样持续保留。
:::

:::note
**v1 版本的局限性**：远程代理发送的工具处理进度信息不会被传回——用户只能看到最终流式返回的响应，而无法查看各个工具调用的详细过程。危险的命令确认提示也会在主机端处理，而不会转发给 Matrix 用户。这些问题将在未来的版本中得到解决。
:::

### 机器人可连接并发送消息，但忽略传入消息

**原因**：Matrix 事件处理程序仅在通过 mautrix 的 `handle_sync()` 机制发送同步数据包时才会触发。如果直接使用 `client.sync()` 进行轮询且从未调用 `handle_sync()`，则适配器虽然处于连接状态（能够发送消息），但传入的消息却无法到达 `_on_room_message` 处理函数。

**解决方案**：Hermes 使用了显式的同步循环，在初始同步以及每次增量同步响应时都会调用 `client.handle_sync()`。这一做法与上游问题 #7914 的诊断结果及已关闭的 PR #37807 一致，同时还能让 Hermes 自行处理各种后台维护任务（如已加入房间的跟踪、邀请处理、端到端加密密钥共享等），而无需将整个生命周期都委托给 `client.start()`。如果重启网关后传入消息问题依然存在，请确认在首次同步之前已正确注册了事件处理程序，并检查日志中是否有“同步事件发送错误”的记录。

### 同步问题/机器人响应延迟

**原因**：耗时较长的工具执行过程可能会延迟同步循环，或者服务器性能较差。

**解决方案**：同步循环会在出现错误时自动每 5 秒重试一次。请查看 Hermes 的日志以获取与同步相关的警告信息。如果机器人持续响应延迟，请确保您的服务器拥有足够的资源。

### 机器人处于离线状态

**原因**：Hermes 网关未运行，或未能成功建立连接。

**解决方案**：请检查 `hermes gateway` 是否正在运行，并查看终端输出中的错误信息。常见原因包括：服务器 URL 错误、访问令牌已过期、无法连接到服务器等。

### 显示“用户未被授权”/机器人忽略您

**原因**：您的用户 ID 不在 `MATRIX_ALLOWED_USERS` 列表中。

**解决方案**：请在 `~/.hermes/.env` 文件中将您的用户 ID 添加到 `MATRIX_ALLOWED_USERS` 中，然后重启网关。请使用完整的 `@user:server` 格式。

### 机器人忽略整个房间

**原因**：虽然设置了 `MATRIX_ALLOWED_ROOMS`，但当前房间 ID 并未列入其中；或者该房间要求被提及，而发送的消息中并未提及机器人。

**解决方案**：请将对应的房间 ID 添加到 `MATRIX_ALLOWED_ROOMS` 中；如果是个人部署，则可删除该房间允许列表。要在 Element 中查找房间 ID，可打开房间设置并查看 **高级** 选项。

### 桥接消息出现循环或回声现象

**原因**：桥接组件或 appservice 守护进程将机器人的输出作为新的用户消息再次转发，或者桥接使用了非标准的“幽灵用户 ID”。

**解决方案**：请勿将桥接使用的幽灵用户放入 `MATRIX_ALLOWED_USERS` 列表中，同时添加相应的 `MATRIX_IGNORE_USER_PATTERNS` 条目。除非这些通知属于可信的工作流程，否则请保持 `MATRIX_PROCESS_NOTICES=false` 的设置。

## 安全性

:::warning
务必设置 `MATRIX_ALLOWED_USERS`，对于共享或私有部署环境，还需设置 `MATRIX_ALLOWED_ROOMS`。如果不设置这些配置，任何能够在机器人所在房间内发送消息的人都有可能触发代理功能。请仅授权您信任的用户和房间——经过授权的用户可完全使用代理的所有功能，包括调用工具及访问系统资源。
:::

如需了解更多关于保障 Hermes Agent 部署安全的信息，请参阅 [安全指南](../security.md)。

## 备注

- **支持任意服务器**：可与 Synapse、Conduit、Dendrite、matrix.org 以及任何符合规范的 Matrix 服务器配合使用，无需特定服务器软件。
- **联盟功能**：如果您使用的是联盟型服务器，机器人便可以与来自其他服务器的用户进行通信——只需将他们的完整 `@user:server` ID 添加到 `MATRIX_ALLOWED_USERS` 中即可。
- **自动加入房间**：机器人会自动接受并加入房间邀请，加入后立即开始响应消息。
- **媒体支持**：Hermes 支持发送和接收图片、音频、视频以及文件附件。这些媒体内容会通过 Matrix 内容存储库 API 上传到您的服务器。
- **原生语音消息（MSC3245）**：Matrix 适配器会自动为发送的语音消息添加 `org.matrix.msc3245.voice` 标签。这意味着文本转语音的响应以及语音音频会在 Element 及其他支持 MSC3245 的客户端中以**原生语音气泡**的形式呈现，而非普通的音频文件附件。带有 MSC3245 标签的传入语音消息也会被正确识别并转送至语音转文字功能。无需任何额外配置，该功能可自动生效。
