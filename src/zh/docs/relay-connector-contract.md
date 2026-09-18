# 中继 ↔ 连接器接口规范（v1，实验性版本）

> **状态：** 实验性版本。在至少有两个一级平台（Discord + Telegram）对其完成验证之前，该接口规范可能会随时变更，而无需经历废弃周期。在实验阶段，接口的演进仅限于**增量式修改**，且需通过 `contract_version` 进行控制；若发生破坏性变更，则需同步更新两个代码库。

本文档定义了 **Hermes 网关**（Python，位于 `gateway/relay/` 目录）与 **连接器**（Node/TypeScript，位于 `NousResearch/gateway-gateway` 目录）之间的正式接口。连接器实现者首先需要阅读此文件。

网关会运行一个通用的 `RelayAdapter`，该适配器负责向连接器发起连接，在握手阶段接收 `CapabilityDescriptor`，随后通过每轮双向 WebSocket 交换标准化的 `MessageEvent`（入站消息）及操作指令（出站指令）。网关无需知晓自身所对接的具体平台类型；所有与特定平台相关的套接字处理及身份识别逻辑均由连接器负责。

---

## 1. 握手流程

1. 网关建立传输连接（调用 `connect` 方法）。
2. 网关调用 `handshake()` 方法，连接器则返回一个 `CapabilityDescriptor`（见第2节），用于描述该适配器实例所支持的平台功能。
3. 网关根据该描述文件配置适配器的相关参数（如字符限制、长度单位以及草稿/编辑/线程/Markdown等功能），并注册入站消息处理函数。
4. 此后，连接器负责流式传输入站事件，并接收网关发送的出站操作指令。
描述符中会包含`contract_version`（当前值为`1`）字段。网关会忽略未知的描述符字段（以确保向后兼容），并使用默认值填充缺失的可选字段。

---

## 2. CapabilityDescriptor（握手数据包）

JSON格式对象。其定义来源为：`gateway/relay/descriptor.py`。

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `contract_version` | int | yes | Contract version (additive-only within a version). |
| `platform` | string | yes | Platform name (e.g. `"discord"`, `"telegram"`). |
| `label` | string | yes | Human-readable label. |
| `max_message_length` | int | yes | Char limit; gateway exposes as `MAX_MESSAGE_LENGTH`. 0 → treat as 4096. |
| `supports_draft_streaming` | bool | yes | Native draft-streaming preview support. |
| `supports_edit` | bool | yes | Edit-based streaming possible; if false, consumer degrades to one-message-per-segment. |
| `supports_threads` | bool | yes | `create_handoff_thread` capability. |
| `markdown_dialect` | string | yes | `"plain"`, `"markdown_v2"`, `"discord"`, … (drives `supports_code_blocks`). |
| `len_unit` | string | yes | `"chars"` (builtin len) or `"utf16"` (Telegram UTF-16 code units). |
| `emoji` | string | no | Display emoji (default 🔌). |
| `platform_hint` | string | no | System-prompt platform hint. |
| `pii_safe` | bool | no | Redact PII in session descriptions. |
| `supports_context` | bool | no | Whether the connector can supply surrounding channel/group **context** for an addressed turn on this platform (Model A on-demand history fetch — Discord/Slack/Matrix; Model B passive buffer — Telegram/Signal/WhatsApp). Default false ⇒ no `context` is attached to inbound events. See §3. |
| `supports_inchannel_continuable` | bool | no | Whether the platform can host a **flat continuable cron surface** (native Slack's `cron_continuable_surface: in_channel`): the brief posts top-level in the channel/DM and a plain reply continues the job via the flat `(platform, chat_id, None)` session. Default false ⇒ the gateway's scheduler fails safe to thread mode (D6 gate), so an older connector keeps today's thread behavior. |
| `supports_block_formatting` | bool | no | Whether this platform's sender renders **block-level formatting** from raw markdown when the gateway stamps `metadata.format_hints` on `send`/`edit` frames (Slack: native `markdown` block for tables/lists/code, mrkdwn text kept as fallback). Default false ⇒ the gateway never stamps hints, so an older connector never receives the metadata. |
| `supported_ops` | string[] | no | Op-level capability discovery: the outbound op names the connector's sender for this platform actually implements (e.g. `["send", "edit", "typing", "follow_up", "get_chat_info"]`). Absent/empty ⇒ the connector predates the field and the gateway assumes the legacy op set (`send`/`edit`/`typing`/`follow_up`); a NEW op is used only when explicitly advertised. |

大多数字段均为网关现有 `PlatformEntry` 对象的映射结果；而仅在运行时有效的字段（如 `len_unit`、`supports_*`、`markdown_dialect`）则来自实时平台适配器的能力方法。

---

## 3. 入站数据：`MessageEvent` 封装结构

该连接器会将每个来自不同平台的消息事件标准化为 `MessageEvent` 对象（位于 `gateway/platforms/base.py` 中），并将其发送给网关。入站数据是通过网关的 OUTBOUND `/relay` WebSocket 传输的（详见下文的传输说明）——连接器会通过网关已建立的连接通道推送 `inbound` 数据帧。网关会利用内置的 `SessionSource` 中的 `build_session_key()` 方法为该会话生成密钥，因此正确设置相关标识符是连接器最核心且最重要的职责。

### 入站传输方式（基于 WebSocket 通道，而非 HTTP）

网关会**主动向外**连接连接器的 `/relay` WebSocket，用于执行握手、发送出站数据（见第4节）以及自身的 `/stop` 停止指令（见第5节）。入站数据则通过同一连接通道的相反方向传输：连接器会将 `inbound` 数据帧（以及第5节中所需的 `interrupt_inbound` 指令）推送至网关的出站 WebSocket。**网关端不存在任何入站 HTTP 接口**——网关无需（且在托管环境中也无法）开放任何入站端口，所有数据流均通过其主动建立的连接进行传输。

**多实例路由机制。**负责管理平台套接字（从而生成入站事件）的连接器实例，通常**并非**网关用于发起出站WS连接的那个实例。因此，生成事件的实例会将该事件发布到连接器内部的**中继总线**上（基于Redis的发布/订阅机制；在`src/core/relayBus.ts`中定义为`RelayBus`），并以租户作为键值进行标识。每个连接器实例都会订阅该总线，并将每条消息路由至对应租户的**本地会话**中（通过`RelayServer.routeBusMessage`函数实现）；实际持有网关套接字的那个实例会负责传递消息，而那些没有该租户本地会话的实例则不会执行任何操作。因此，跨实例的消息传递实际上是通过集群内的Redis跳转完成的，而非通过公共HTTP调用。

帧结构（连接器 → 网关，通过WS传输）：

- `{"type":"inbound", "event": <MessageEvent>, "bufferId"?}`
- `{"type":"interrupt_inbound", "session_key", "chat_id"}`（见§5）
- `{"type":"passthrough_forward", "forward": <PassthroughForward>, "bufferId"?}`（见§5.1）

**入站消息的通道上下文（relay-channel-context设计）。**当源平台描述信息中声明支持上下文功能（见§2），且聊天为多方对话时（即`chat_type`属于group/channel/thread/forum类型，绝非`dm`类型），连接器可以在入站的`MessageEvent`中添加两个可选的、用于补充信息的字段：

- `context`：一个只读的周边消息数组（来自同一频道，按从旧到新的顺序排列）——即连接器获取的（模型A）或缓存的（模型B）附近未针对特定对象发送的聊天内容。此字段仅作参考之用：它不会触发智能体响应（触发决策早已在连接器端仅基于目标事件完成）。网关会将其转换为`MessageEvent.channel_context`（该格式与用于历史回填的只读注入路径相同）。
- `context_error`：布尔值，当平台具备处理上下文的功能，但获取/缓存操作失败且连接器以空`context`状态异常启动时为真（属于可观测性标记；可通过交付跨度在连接器端显示）。

若这两个字段均不存在，则表示与今日的数据完全一致。那些从不发送这些字段的连接器、私信场景，或是不支持上下文功能的平台，都不会生成`channel_context`。

`PassthroughForward` 是转发的直通平面请求的原始格式（适用于 Class-2/3 Webhook —— 如 Discord 交互、Twilio 操作）：`{platform, botId, method, path, headers: [[k,v],…], bodyB64, profile?}`。`profile` 为可选字段——当 NAS 为团队网关交互解析目标配置文件时，连接器会自动添加该字段；对于仅支持单一配置文件的网关，省略该字段可保持原有的路由机制，继续使用默认的 `agent:main` 会话命名空间，这一做法与 `inbound` 框架中 `SessionSource` 字段已包含的 `profile` 信息一致（参见 #60586）。请求体采用 Base64 编码，以便在以换行符分隔的 JSON 格式传输过程中仍能保留原始字节；网关会对其进行 Base64 解码，还原为连接器转发的原始字节——连接器已在边缘环节验证了提供方的签名并去除了任何共享身份凭证（见 §6），因此网关只需处理经过净化、不含令牌的请求体，再通过无需令牌的 `follow_up` 路径对其进行处理。详情请参见 §3.1。

**信任机制。** WS 升级过程通过网关专用的密钥进行身份验证（见 §6.1），因此整个通道具备端到端的信任性——入站帧无需再单独进行 HMAC 签名（已通过身份验证的套接字已具备了旧 HTTP 方式所需的每次传输来源验证功能）。中继总线传输过程处于连接器的信任域内（与该连接器的租约/缓冲区/能力存储处于同一安全域）。

在早期版本的协议中，数据通过带签名的**HTTP POST**请求发送至`gatewayEndpoint`（即`HttpGatewayDelivery`与网关端的`inbound_receiver`组合），并使用针对每个租户的传输密钥进行HMAC签名。这要求每个网关都必须提供一个可访问的入站URL——而对于没有公网IP的托管网关而言，这是无法实现的。上述基于WS的回传通道取代了这一机制；为保持向后兼容性，仍会保留针对每个租户的传输密钥，但已不再用于数据入站传输。而**直通通道**（如Discord交互/Twilio等第二类/第三类Webhook）在过去仍在其ACK响应后的数据转发过程中使用`gatewayEndpoint`；第5阶段第5.1节规定，该转发功能也将迁移至WS通道（即上述的`passthrough_forward`帧），因此托管网关无需具备任何公网入站接口，而在过渡完成后，`gatewayEndpoint`也将被彻底废弃。

### 3.1 直通通道的数据转发（§5.1）

透传层会在连接器边缘节点及时响应提供方对延迟敏感的确认信号（例如 Discord 在约 3 秒内返回的延迟交互响应），随后通过 **一次性的转发** 将真实请求发送至网关。由于该转发无需等待回复（因为提供方已收到响应），因此它会借助 `passthrough_forward` 数据帧，而非 HTTP POST 请求，沿着与“入站”请求相同的出站 WebSocket 流进行传输。网关会通过常规的代理处理路径来解析该请求（Discord 的交互请求会被解析为 `MessageEvent` 并作为普通消息处理；回复则通过出站/“后续响应”路径发送）。当请求被缓存时（第 5 阶段 §5.3 节中关于仅缓存模式的说明），会包含 `bufferId` 字段，且网关会在完成持久化移交后对其予以确认。

### SessionSource 字段（网络传输层）

数据来源：`gateway/session.py` 文件中的 `SessionSource.to_dict()` 方法。这些字段涵盖了网关在网络传输中接收的所有键值。`platform`、`chat_id`、`chat_type`、`user_id`、`user_name`、`thread_id`、`chat_name` 和 `chat_topic` 这些字段始终存在（可能值为 `null`）；其余字段则仅在被设置时才会包含在内。

| Field | Type | Always sent | Meaning |
| --- | --- | --- | --- |
| `platform` | string | yes | Platform name (matches the descriptor's `platform`). |
| `chat_id` | string | yes | Primary conversation id (channel/chat). Session-key discriminator. |
| `chat_type` | string | yes | `dm` / `group` / `channel` / `thread` / `forum`. |
| `chat_name` | string\|null | yes | Human-readable chat name. |
| `user_id` | string\|null | yes | Message author id. Session-key discriminator. |
| `user_name` | string\|null | yes | Author display name. |
| `thread_id` | string\|null | yes | Thread/forum-topic id when in a thread. Session-key discriminator. |
| `chat_topic` | string\|null | yes | Channel topic/description (Discord, Slack). |
| `user_id_alt` | string | no | Platform-specific stable alt id (Signal UUID, Feishu union_id). |
| `chat_id_alt` | string | no | Alternate chat id (e.g. Signal group internal id). |
| `scope_id` | string | no | Platform-neutral **scope** discriminator: Discord guild / Slack workspace / Matrix server. **REQUIRED for Discord/Slack scope isolation.** Session-key discriminator. (Canonical name as of the D-Q2.5 wire migration.) |
| `guild_id` | string | no | **Legacy alias, no longer read by the connector.** As of D-Q2.5c the connector reads and writes only `scope_id`; the gateway's agent-wide `SessionSource.to_dict()` still emits `guild_id` (mirrored to `scope_id`) for non-relay session persistence, so it may still appear on the wire but the connector ignores it. Do not depend on it. |
| `parent_chat_id` | string | no | Parent channel when `chat_id` refers to a thread. |
| `message_id` | string | no | Id of the triggering message (for pin/reply/react). |

> 在网关端的数据类中存在 `is_bot`（用于区分作者是否为机器人/ webhook分类）字段，但在 v1 版本中**刻意未将其包含在传输数据中**——它也不属于 `to_dict()` 的输出内容。在首先将其添加到此处以及 `to_dict()` 中之前，请勿将其加入连接器的 `SessionSource` 中（后续版本会逐步补充）。

### 各平台的 SessionSource 标识字段

| 平台 | chat_id | chat_type | user_id | thread_id | scope_id |
| --- | --- | --- | --- | --- | --- |
| **Discord** | 频道 ID | `dm`/`group`/`thread` | 作者 ID | 线程频道 ID（用于线程） | **服务器 ID**（实现服务器隔离的必需字段） |
| **Telegram** | 聊天 ID | `dm`/`group`/`forum` | 发送方 ID | 论坛主题 ID（用于论坛） | — |

**若获取 Discord 的 `guild_id` 出错，两个服务器可能会被合并到同一个会话中。** 这是严重程度最高的风险点。网关的 `build_session_key()` 函数是判断标准：对于给定的 `SessionSource`，连接器进行的标准化处理必须生成与 Python 适配器相同的密钥。（第一阶段的测试用例会验证已知输入能对应出已知密钥。）

### 机器人身份与租户概念（单机器人多租户整合，附录 A）

消息包中会携带**独立的机器人身份字段**，该字段与租户概念是分开的。租户信息是从事件本身的标识字段中确定的（Discord 的 `guild_id`、Telegram 的 `chat_id`、webhook 路径/子域名）——**绝不会**根据传递消息的令牌、套接字或进程来判定。这样一来，同一个共享机器人便能在不占用现有字段容量的情况下，为多个租户提供服务（第六阶段）。

### 以作者优先的解析方式 + 账户关联路径（私信场景，第七阶段）

第7阶段新增了**面向用户的自助式共享机器人入门功能**，该功能改变了路由进站消息时用于确定实例的判定规则——同时为用户提供了绑定自己账户的管理路径。

**以发件人为主的解析机制（多租户公会规则，D-7.2）**。一个Discord公会可容纳**多个**租户——不同成员各自关联着独立的智能体。因此，在消息传递过程中，连接器会通过**已认证的发件人绑定信息**（即`user_instance_binding`，其键为`(tenant, platform, platform_user_id)`，并通过`resolveByUser`函数进行解析）来确定目标实例，而非依据公会→实例的路由方式。具体而言：

- 由**已关联**用户发送的路由消息只会送达**该用户自己的**智能体实例——即便同一公会中的另一位已关联用户由不同的智能体处理，消息也仅会发送给对应用户的实例。
- 由**未关联**用户发送的消息将无法解析出任何实例，会被直接丢弃（采用“失败即终止”机制，不会广播给公会的其他租户）。
- 所使用的发件人ID为**实际事件中记录的`user_id`**，也就是上文提到的`SessionSource.user_id`——绝非网关指定的值或管理帧中携带的信息。

这正是连接器在`WsGatewayDelivery`模块中实施的、基于每个`user_id`的仅所有者可访问的路由机制（而网关侧的多租户公会端到端驱动程序`gateway_multitenant_guild_driver.py`则作为跨仓库的参考实现）。

**账户关联（私信）路径。** 用户可通过一次性验证码将自身账户与某个实例绑定，该验证码是通过向共享机器人发送私信来获取的：

1. 账户所有者通过门户网站（或自托管的 CLI）触发关联流程。连接器会为已通过身份验证的实例生成一个有效期短暂的**链接码**（调用接口为 `POST /manage/link`；`instanceId` 来源于发起请求方的身份凭证——即由 NAS 签名的、包含 `aud=agent:{instanceId}` 字段的令牌，或是该实例自身的网关专用密钥——**绝不会**来自请求正文）。
2. 用户从希望绑定的账户出发，向共享机器人发送包含 `/link <code>` 内容的**私信**。
3. 连接器的入站监听器会**接收**该私信（不会将其路由至任何代理），并利用私信事件中记录的已验证**`user_id`**来创建 `user_instance_binding` 记录。此后，基于发件人优先的路由规则，该用户的消息将直接发送到已绑定的实例。

**取消关联由连接器决定。** 当某个实例被停用时（调用接口为 `POST /manage/deprovision`），不仅会解除与该实例的账户绑定关系（从而使相关用户不再将其作为消息接收目标），还会撤销该实例的网关专用密钥（导致其套接字无法再进行身份验证——下一次 WebSocket 连接升级将会被以 **4401** 错误拒绝）。如果某个网关在之前已成功建立连接后却收到 **4401** 错误，它会将此视为最终性的授权撤销：立即停止重连，并将该中继平台标记为**已禁用**状态（不属于可重试的错误）。而在任何成功建立连接之前出现的 4401 错误则仍属于可重试范畴（属于启动失败或实例尚未准备就绪的情况，而非授权撤销）。

### 3.2 Going-idle / buffered-flip 原语（§5.3）

这是一种将流量归零的原语（并非用于控制机器进入睡眠或暂停状态的行为——此类决策由后续的工作流负责处理；这些帧会被后续工作流使用）。该原语通过为对应连接实例创建缓冲区，并在重新连接时回放这些数据，从而使网关能够在进入空闲状态的同时，不会丢失其在空闲期间接收到的入站数据。

这三个帧均以该连接的**已验证**实例标识符作为键值——该标识符来自 WebSocket 升级过程中存储的密钥记录，且不会在任何帧中直接体现。

- `{"type":"going_idle"}`（网关 → 连接器）——作为网关现有“数据流终止”转换过程的一部分而发出（适配器在关闭套接字之前会发送该消息）。该消息要求连接器将当前实例切换为**仅缓冲模式**。
- `{"type":"going_idle_ack"}`（连接器 → 网关）——连接器已完成切换：实时传输已停止，此后针对该实例的入站数据将持久存储在缓冲区中。网关会**持续提供服务，直至收到此确认消息**（因此，在切换窗口内到达的事件仍能实现实时传输而不会丢失——这与消息总线的“先订阅后服务”原则一致）。只有在收到确认消息后，才能安全地关闭连接。
- `{"type":"inbound_ack", "bufferId"}`（网关 → 连接器）——表示已成功持久接收一个经过缓冲处理的入站数据（该数据包含对应的`bufferId`），在重新连接时会重新传输这些数据。连接器仅在收到此确认后才会对相应缓冲条目予以确认，从而在**数据传输环节实现无重复传输**：如果在数据流终止过程中实例发生故障，系统会重新传输所有尚未被确认的剩余数据；而已被确认的条目则不会再被重复传输。
**缓冲与清空机制。** 当处于翻转状态时，连接器会将传入的数据追加到每个实例专用的持久性传输缓冲区（`delivery:<instanceId>`）中，而非立即进行实时传输。当网关发生**重新连接**时（即在意外断开后通过全新的重连循环进行重新拨号与握手），新的握手请求会促使连接器按照顺序、通过确认机制将缓冲区中的积压数据通过新建立的套接字清空，之后再解除翻转状态，从而恢复实时传输。这一机制实际上复用了Discord→连接器传输路径中所使用的`drainWithoutDup`功能，只是将其应用到了连接器→网关的传输路径上。在整个过程中，连接器拥有绝对控制权：网关仅能对自己所属的实例执行翻转/清空操作。

> 不在当前范围之内（属于延迟处理的行为）：决定何时进行数据清空的自主空闲计时器、实际的设备挂起机制，以及NAS系统的挂起状态检测模型。其基本原则是“当网关完成数据清空后，中继节点即切换至缓冲模式，并在重新连接时重新播放数据，且不会造成数据丢失或重复”；而究竟是什么触发了数据清空操作，则不在当前讨论范围内。

### 3.3 唤醒机制（§5.2）

睡眠/唤醒循环的另一半：处于挂起状态的网关如何得知有缓冲数据待处理。这属于一种基础机制——此处并无任何功能会直接导致设备挂起；它只是建立了唤醒信号机制，以便未来的零负载扩展处理层能够依据“缓冲数据存在 ⇒ 触发唤醒”这一逻辑来运作。

- **注册。** 网关会在注册/配置阶段指定一个**唤醒 URL**——即连接器可通过 GET 请求来唤醒它的任何可访问地址（例如 Fly 自动启动主机地址或控制面板主机地址）。对于自托管场景，可使用命令 `hermes gateway enroll --wake-url <url>`（或配置参数 `GATEWAY_RELAY_WAKE_URL` / `gateway.relay_wake_url`）进行设置；而对于托管型/NAS 型服务，该地址会与 `GATEWAY_RELAY_URL` 一同被写入容器环境变量中。在 `/relay/provision` 的请求体中，该地址会以 `wakeUrl` 的形式被传递，并以实例为单位存储在连接器的密钥记录中（该地址由网关确认，但具有严格的访问范围限制——其安全级别与 `instanceId` 相同；由于组织/租户身份始终通过令牌进行验证，因此每个网关仅能为自身的实例注册唤醒目标）。需要注意的是，这与已废弃的 `gatewayEndpoint` 不同，后者是用于数据传输的目标地址，而非用于唤醒操作的目标地址。
- **唤醒操作**。当仅处于缓冲状态（进入空闲模式）的目标设备接收到首个缓冲事件时，连接器会**直接**向该设备已注册的 `wakeUrl` 发送一个**不包含有效载荷且无签名**的 GET 请求（并非通过 NAS 中转——因此该过程完全独立于 NAS）。此请求不携带任何租户数据，也不涉及任何入站通信，仅传递“你有待处理的缓冲任务，请重新连接”的信息。当网关再次发起连接时（即经过身份验证的 WS 升级过程），租户授权会以常规方式重新建立；因此，即便 `wakeUrl` 被泄露或被猜测到，最多也只会导致该设备自身发生不必要的重新连接。该操作会对每个设备设置速率限制（在每个冷却周期内仅可触发一次唤醒，而非每次事件都触发），且为尽力而为型——如果唤醒请求失败，系统也会忽略它；网关仍会在下次自动重新连接时继续尝试。此外，此唤醒操作并非通过新的数据帧实现，而是一种带外 HTTP GET 请求，不属于 WS 中转消息的范畴（因为此时套接字处于关闭状态，这正是该设计的初衷）。

> **不在当前功能范围之内**（属于延迟实现的功能）：设备的实际暂停操作（可通过 Fly 的 `autostop:"suspend"` 参数实现），以及决定设备进入睡眠状态的自动空闲计时器。其基本原理是“针对处于睡眠状态的设备触发缓冲事件，进而对其 `wakeUrl` 进行唤醒”；而决定设备何时进入睡眠状态（以及何时醒来开始工作）的，则是由行为层来控制的。

### 3.4 未来实现零资源占用行为层时应满足的要求

§3.2和§3.3部分定义了**基础功能模块**；本节则规定了**独立的“零负载扩展”工作流为安全使用这些功能模块所必须遵循的契约**。该工作流负责做出暂停决策、执行实际的机器暂停操作，以及管理平台与健康状态模型——尽管这些功能本身并不位于此处——但它必须确保满足以下各项保障条件，而这些条件正是基础功能模块所依赖的：

1. **在实例被暂停之前，必须先注册`wakeUrl`。** 若某个已暂停的实例未注册`wakeUrl`，它就会变成一个“黑洞”：进入缓冲区的入站请求永远无法触发唤醒操作，因此该实例会一直处于休眠状态，直到有其他机制重新连接它。行为层必须确保在允许暂停之前，已注册一个可访问的唤醒目标地址（自托管环境可使用`--wake-url`参数指定；托管环境则由系统自动处理），否则等同于未设置唤醒地址。
2. **在断开套接字或暂停实例之前，必须先通过`going_idle`状态完成数据清理，再等待`going_idle_ack`确认。** 绝不允许在处于“正在切换状态”且尚未收到确认响应的情况下就暂停实例。该确认信号表示连接器已确认该实例的请求当前仅被缓存，尚未实际处理；如果在发送`going_idle`信号后但在收到确认响应之前就暂停实例，那些快速到达的入站请求将会丢失。网关本身已根据确认响应来控制套接字的断开操作（参见Q-5.3c条款）；因此暂停操作必须是在完成完整的数据清理之后才能执行，绝不能与之并行。
3. **暂停功能的前提是保持NET-NEW重连循环处于活跃状态。**其工作流程为：“触发唤醒信号→网关重新拨号→连接器在重连握手过程中完成数据传输。”如果关闭了重连循环，当唤醒信号发送到某台设备后，该设备将不再尝试重新拨号，从而导致数据缓冲区出现堵塞。行为层绝不能暂停那些在唤醒后无法重新建立连接的实例。

4. **在健康状态模型中，应将“暂停状态”视为与“故障状态”不同（参见Q-5.3b）。**处于暂停状态的实例只是处于“健康休眠”状态，并非发生故障。健康/监控层必须能够区分这两种状态（例如通过平台上的机器状态信息），从而避免对暂停实例进行重启、触发警报或判定为不健康状态——否则就会违背暂停功能的初衷，还可能与唤醒/数据传输流程产生冲突。

5. **唤醒信号的发送属于尽力而为且带有速率限制——切勿假设其一定会被准确发送或立即触发唤醒效果。**每个实例在每个冷却周期内最多只能收到一次唤醒信号，且失败的唤醒尝试会被忽略。行为层不应将唤醒信号视为一种可靠或即时的触发信号；系统的正确性依然取决于“网关在下次重新连接时便会完成数据传输”这一原则。采用多重保障机制来确保唤醒功能正常运行（例如结合定时任务与自动重连功能），这是由行为层来决定的，而非底层接口的功能要求。
6. **仅在实际处于空闲状态时才暂停运行——且这种空闲状态需由连接器直接检测，而非由网关推测。** 何为空闲状态（无正在处理的请求，且连续 N 分钟无新进请求）由行为层的相关策略决定，但该策略必须与现有的资源释放机制协同工作（即当 `gateway_state` 处于运行状态时才开始释放资源），而不能另设一条仅通过中继器实现的并行空闲处理路径——这与第 3.2 节中对 `going_idle` 所规定的集成约束相同。

这些是行为层应当为底层组件提供的保障；而底层组件仅需履行第 3.2 节和第 3.3 节中已明确规定的义务（在进入空闲状态时触发相应操作、为每个实例提供持久化缓冲区并配合确认机制进行重连处理，以及在对缓冲区中的首个事件进行处理时针对已切换为空闲状态的实例采取相应动作）。

---

## 4. 出站：操作集

网关会通过操作字典来调用传输层相关功能。相关定义位于 `gateway/relay/transport.py` 和 `gateway/relay/adapter.py` 文件中。

| `op` | 字段 | 返回结果 |
| --- | --- | --- |
| `send` | `chat_id`, `content`, `reply_to?`, `metadata?` | `{success: 布尔值, message_id?, error?}` |
| `edit` | `chat_id`, `message_id`, `content`, `metadata?` | `{success: 布尔值, error?}` |
| `typing` | `chat_id`, `content?`, `metadata?` | `{success: 布尔值}` |
| `follow_up` | `session_key`, `kind`, `content`, `metadata?` | `{success: 布尔值, message_id?, error?}` |
| `send_media` | `chat_id`, `media_kind`, `source_url`, `content?`（标题），`filename?`, `reply_to?`, `metadata?` | `{success: 布尔值, message_id?, error?}` |
| `prompt` | `chat_id`, `prompt_kind`, `prompt_id`, `content`（问题内容），`options[]{id,label,style?}`, `timeout_s?`, `reply_to?`, `metadata?` | `{success: 布尔值, message_id?, error?}` |
| `react` | `chat_id`, `message_id`, `emoji`, `remove?`, `metadata?` | `{success: 布尔值, error?}` |
| `thread_create` | `chat_id`（父聊天ID），`thread_name`（线程名称），`message_id?`（锚定消息ID），`metadata?` | `{success: 布尔值, thread_id?, error?}` |
| `thread_rename` | `chat_id`（父聊天ID），`message_id`（线程ID），`thread_name`（新线程名称），`only_if_current_name?`, `metadata?` | `{success: 布尔值, error?}` |

`get_chat_info(chat_id)` 是一个独立的代理调用，至少会返回 `{name, type}`。

**`send_media`（第二阶段媒体输出功能）**。媒体数据是以引用方式传输的：
`source_url` 可以是 (a) 由网关先前通过 `POST {connector}/relay/media` 上传的**连接器重新托管地址**（原始字节数据作为请求体，包含 `Content-Type` 头部以及可选的 `X-Media-Filename` 头部，采用与 WS 升级相同的 HMAC 承载机制；响应内容为 `{id, size}`，对应的引用地址为 `{connector}/relay/media/{id}`），或者是 (b) **公共 http(s) URL**（例如 fal.media 生成的地址），连接器可直接从该地址下载媒体。`media_kind` 的取值为 `image` / `voice` / `audio` / `video` / `document`，用于确定平台原生的上传方式（如 Telegram 的 `sendPhoto`/`sendVoice` 等功能、Discord 的多部分附件上传、Slack 的外部上传功能、WhatsApp 的媒体上传及媒体消息功能）。标题信息会嵌入在 `content` 中，并通过平台的常规 Markdown 渲染机制显示；对于不支持原生标题功能的平台，连接器会另行发送文本信息。这两种传输路径以及该操作均受 `supported_ops` 中是否包含 `send_media` 项的限制——旧版连接器将无法使用此功能（此时网关的媒体传输会降级为之前的纯文本备用方案）。媒体文件大小上限为 25 MB（由连接器的 `mediaStore.ts` 中的 MEDIA_MAX_BYTES 参数定义；超过此限制的上传请求将会被返回 413 错误）。

**入站媒体（第二阶段媒体接入）**。入站事件中的 `media_urls` 会包含可获取的引用地址：那些通过平台公共 URL 传输的媒体会直接使用 Discord CDN；而那些需要身份验证或存在时效限制的平台 URL（如 Telegram 文件 API、Slack 的 `url_private`、WhatsApp Graph media）则由连接器端使用平台凭证进行下载，之后以 `{connector}/relay/media/{id}` 的格式重新托管——平台凭证绝不会在网络传输过程中泄露。这些重新托管后的引用地址可以被任何已通过身份验证的网关读取（遵循 capability-URL 规范：标识符为 128 位随机数，且早已发送给所有被授权的接收方）；网关会使用自身特有的访问凭证下载每个引用地址，并向智能体提供本地文件路径，其工作方式与原生适配器类似。重新托管的媒体具有时效限制（生存时间约为 1 小时），需在收到消息时立即下载，而非延迟处理。此外，还有一个结构相同的 `media` 数组，其中包含了 `kind`、`mime`、`size`、`filename`、`caption` 等元数据；`message_type` 则用于标识第一个附件的类型（`image`/`audio`/`document`）。

**`prompt`（第三阶段交互模式）。** 该功能通过一个平台抽象操作，利用原生控件来实现网关中最为关键的交互场景——如审批流程、命令确认以及选项澄清等。这些原生控件包括 Discord 按钮组件、Telegram 内置键盘、Slack Block Kit 动作，以及 WhatsApp 的按钮消息（最多3个选项）/列表消息（4–10个选项；超过10个选项则退化为带编号的文本形式）。`prompt_kind`（`approval`/`clarify`/`choice`）仅用于样式提示。`prompt_id` 由网关生成，连接器无法获取其具体值；每个选项的回调数据中都会包含 `hp1:<prompt_id>:<option_id>` 这一令牌（长度限制为≤64字节——由于 Telegram 的 `callback_data` 长度限制，所有通道均受此约束；选项编号由 `[A-Za-z0-9_.-]` 组成，长度不超过32字符）。网关会在同一字符集与长度限制范围内，将 `prompt_id` 生成为 `<per-process nonce>.<8 hex>` 的格式。与普通消息仅会发送给允许的实例集不同，连接器会将此信息原封不动地转发给租户的所有活跃网关会话，因此该随机数正是网关用来区分自身生成的提示与其它实例生成的提示的关键依据。`style` 参数用于指定不同平台下的样式类型（如 primary/success/danger/secondary）。`timeout_s` 仅作为传输层上的建议值——实际超时控制由网关端执行（待处理提示注册表会自动删除过期条目，相应的网关随后会发送简短的“已停止等待”通知）。

**`prompt_response`（第三阶段入站消息）。** 用户的操作反馈会以常规的入站 MessageEvent 形式返回，其中包含 `prompt_response: {prompt_id, option_id, label?, prompt_message_id?}` 的字段——绝不会是单纯的平台自定义 ID。该事件的`text`字段会使用`/{option_id}`格式，并设置`message_type: "command"`，这样一来，那些尚未支持该字段的网关就会将用户的输入视为结构化回复而非直接丢弃。而能够识别该字段的网关则会直接处理该输入：因为该输入所对应的提示ID并非由当前网关生成，而是来自同一消息分发路径中的其他网关，若让`/{option_id}`格式的文本进入聊天通道，就会导致所有相关网关都在同一条确认消息下回复“未知命令”。消息的来源是真正执行了点击操作的用户（根据连接器检测结果，分别为Telegram的`callback_query.from`、Slack的`block_actions.user`、WhatsApp的`messages[].from`以及Discord的交互成员/用户），因此网关端的授权机制对按钮点击操作的处理方式与对手动输入的`/approve`命令完全一致。数据接收渠道包括：Telegram的`callback_query`（采用轮询模式，允许处理的更新类型更广泛；使用尽力而为模式的`answerCallbackQuery`则会有加载指示器）；Slack的`POST /slack/interactions`（以原始字节形式传输，并带有HMAC加密及重放防护机制，处理方式与`/slack/commands`相同）；WhatsApp的交互式`button_reply`/`list_reply`（通过Webhook进行标准化处理）；以及Discord的类型3组件交互（按照§5.1条的规定进行净化后转发；由于类型3交互的边缘确认值为`DEFERRED_UPDATE`，因此不会显示“思考中…”的回复状态）。来自其他集成系统的按钮点击载荷永远不会被转换为提示事件：Telegram、Slack和WhatsApp会在连接器层面直接丢弃这类载荷；而Discord的类型3转发则仍会保持传统的以文本形式呈现自定义ID的方式。

**`react`（第三阶段确认生命周期）**：用于在指定`message_id`上添加或移除机器人自身的表情符号反应——通过中继服务器恢复原生适配器所使用的👀→✅/❌处理流程。该功能支持传输Unicode表情符号；Slack发送方会将其映射为Slack内置的名称词汇（如`eyes`、`white_check_mark`等），并将`already_reacted`/`no_reaction`状态视为成功操作（即具备幂等性）。Telegram则使用`setMessageReaction`方法实现（空集合表示移除反应；由于Telegram对表情符号有严格限制，某些字符可能会被拒绝传输——此类失败属于结构化错误，且网关会将其视为仅用于美化界面的功能）。WhatsApp则是通过发送专门的反应消息来实现相应功能（空表情符号同样表示移除反应）。根据协议约定，反应功能的传输为尽力而为模式：`react`操作失败绝不能导致当前轮次处理中断。

**`thread_create` / `thread_rename`（第4阶段线程生命周期）。** 有一对平台抽象接口分别用于处理线程传递、Telegram私信/论坛主题以及LLM标题的语义重命名功能。`thread_create`：Discord会在设置`message_id`时创建频道线程（类型11）或以消息为锚点的线程；Telegram则调用`createForumTopic`方法并返回主题ID；Slack则会发布一条带名称的种子根消息，并返回其时间戳`ts`（该平台的线程均以消息为锚点——系统会原样返回指定的`message_id`作为锚点）。所创建的线程ID会通过`SendResult.thread_id`字段传递。`thread_rename`：Discord通过PATCH请求修改线程频道；Telegram则调用`editForumTopic`方法。**`only_if_current_name`防覆盖保护机制**体现了各原生适配器中“仅当当前名称存在时才允许重命名”的逻辑，该规则由CONNECTOR层强制执行：Discord会首先读取当前名称，若不一致则直接不执行操作并返回结构化的`success:false`响应；由于Telegram不提供主题名称读取功能，因此受此保护的重命名操作将无法实现，系统会采取安全策略确保操作失败（未经保护的重命名仍可继续执行）。Slack则不支持`thread_rename`功能（其根消息的内容为文本而非名称），WhatsApp同样不支持该功能（因为它本身不支持线程功能）。

**自动线程标记与网关声明的命令清单（第4阶段：数据接收/握手流程）**。当连接器的自动线程输出策略创建一个Discord线程后，后续来自该线程的入站事件会携带`source.auto_thread_created: true`及`source.auto_thread_initial_name`这些字段——这些都是连接器检测到的关键证据，用于触发网关的语义重命名机制（LLM会通过受保护的`thread_rename`操作来重命名线程；该机制基于实例级内存，因此在多实例环境中一旦出现错误，便不会触发重命名）。此外，网关还可以在Discord的`hello`消息中声明其slash命令集（格式为`command_manifest: [{name, description, options?}]`）；连接器则会将Discord全局应用程序命令注册信息与网关声明的清单进行比对（通过GET获取差异后进行批量PUT覆盖操作；该过程具有幂等性、防抖功能，且为尽力而为模式——注册失败不会影响握手流程）。命令仍会像以往一样通过直通通道发送；而命令清单的作用仅在于让Discord的注册信息与网关调度器处理的命令保持同步。

**入站 `reply_to` 信息补充（第 4 阶段）**。平台回复除了包含 `reply_to_message_id`（即用户所引用的消息 ID）外，还可能携带 `reply_to: {text?, author?, is_own?}` —— 这些数据仅来源于连接器已有的信息（如 Discord 的内联 `referenced_message`、Telegram 的内联 `reply_to_message`、WhatsApp 的 `context.from`，以及针对每条入站文本的有限缓存）。若某字段缺失，则表示平台未提供该数据，此时不会触发额外的平台 API 调用。`is_own` 的含义是：被引用的消息由前置机器人所发送（其判定依据与 `is_reply_to_bot` 标记相同）。网关会将这些信息映射为原生适配器所填充的相同 MessageEvent 回复上下文字段。

**`typing` 的 `content?` 参数（用于清除 Slack 状态）**。通常情况下，`typing` 消息不会包含 `content` 字段——连接器会直接显示对应平台的忙碌状态指示（如 Slack 上的 “正在输入…” Assistant 状态，其他平台则显示单次输入提示）。而**空字符串**形式的 `content` 则表示明确的清除请求：在 Slack 上，连接器会将 Assistant 线程的状态设置为 `""`，从而将其隐藏。网关仅会向 Slack（具有持久状态的功能）发送清除指令，其他一次性使用的平台则不会收到该信号。该功能在 `contract_version` 1 中已被添加，但需注意部署顺序：若连接器早于网关版本 #154 被部署，则它会忽略 `content` 参数，并在清除消息时仍显示 “正在输入…” 状态——因此应先部署连接器。

**`follow_up`（A2能力操作）**。某些传入的负载会携带用于操作**共享**机器人身份的凭证（例如Discord交互后续令牌）。根据第6条规定，连接器会在边缘层移除该凭证，并将其存储在以会话为键的能力存储库中；该凭证**绝不会传递到网关**。若要使用此功能，网关需发出`follow_up`指令，其中需指定**当前所处的会话**（`session_key`）以及能力类型`kind`（例如`discord.interaction_token`）——**绝不能是令牌本身**。连接器会从其存储库中获取实际值，验证租户匹配性（租户B绝无法使用租户A的能力），之后再将数据发送出去。当对应能力缺失/过期或租户不匹配时，响应将为`success: false`——按设计，网关此时并无内容可重试（泄露的网关不会持有任何能力相关数据）。相关代码来源：`gateway/relay/transport.py`（`send_follow_up`函数）及`gateway/relay/adapter.py`。

---

## 5. 中断（`/stop`）路由机制

- **网关 → 连接器**：通过出站 WS 发送 `send_interrupt(session_key, reason?)` 指令，以中途 `/stop` 的形式中断当前对话。根据路由不变性，连接器必须将该指令转发给正在处理该 `session_key` 的网关实例。
- **连接器 → 网关**：针对某个 `session_key` 的入站中断指令会以 `interrupt_inbound` 数据帧的形式通过网关的出站 WS 传递（参见§3传输说明）——通过中继总线在各个实例之间路由，直至到达持有对应套接字的实例——随后由适配器的 `on_interrupt(session_key, chat_id)` 函数将其接入现有的会话级中断机制，从而精确地取消当前对话轮次（其他对话不受影响）。

两种通信方向均依托网关的出站 WS：网关→连接器的 `/stop` 指令通过该通道发送，而连接器→网关的中断指令则作为标准化事件，通过相同的“入站”回传通道传输。

---

## 6. 信任边界与签名数据处理（A2）

**连接器是唯一的加密/身份验证边界，网关不会对任何内容进行重新验证。**

Webhook签名（Discord的ed25519、Twilio的HMAC、WeCom的BizMsgCrypt）是基于原始字节直接计算的，且部分数据负载会使用共享密钥进行*加密*处理。连接器为多个租户托管同一个公共机器人，并保存所有租户的平台密钥，因此它：

- **在边缘端进行验证/解密**（即密钥仅存储于此位置），  
- 将有效载荷**标准化**为特定租户范围的 `MessageEvent` 对象（见第3节），  
- **移除有效载荷中的任何共享身份相关功能**，并将其存储在以会话为键的专用能力保险库中（参见第4节“后续处理”），  
- **仅转发经过处理的 `MessageEvent` 对象**——绝不会传输原始的签名内容。  

因此，网关在数据中转路径上**不会**执行任何平台级的签名或加密验证操作，而是直接信任已标准化的事件数据。这是网关端强制遵循的不变原则（参见 `tests/gateway/relay/test_relay_sheds_crypto.py`：该中转模块不会导入或调用任何平台级加密功能）。  

**为何不采用“逐字节转发签名后的内容以便网关重新验证”的方式？**  
在不可信任且可被丢弃的租户网关环境下，这种方案存在根本性问题：  
- 要重新验证 Twilio HMAC 或 WeCom 的加密内容，就必须将**共享签名密钥**交给网关——而这本身就意味着信息泄露；而在共享机器人场景下，甚至会导致*跨租户*的信息泄露。  
- WeCom 的有效载荷是使用共享密钥加密的；连接器仅为了路由目的才需要在边缘端解密，因此若转发加密后的数据，同样必须将密钥交给网关。  
- Discord 的交互令牌就**包含在签名后的 JSON 数据中**——你无法既保留这些字节数据又同时移除凭证信息，因为二者其实是同一组字节。
因此，系统会刻意放弃字节级保真机制：连接器会对经过清理的事件进行重新序列化，而后网关会信任该序列化后的数据。这样一来，直通模式与中转模式便实现了统一——两者均遵循“在边缘端进行验证 → 发送标准化事件”的流程，仅传输方式有所不同。有关A2设计理念的详细说明以及连接器端的加密机制，请参阅 `docs/capability-trust-boundary.md`（连接器代码库位于 `gateway-gateway`）。

### 6.1 通道认证（连接器与网关之间的连接）

在A2架构中，平台密钥由连接器单独保管，而网关则可能由客户自行管理且需暴露在互联网上，因此连接器与网关之间的通道本身也需要经过认证。网关会持有由注册或配置流程生成的**针对单个网关的专用密钥**（可通过 `hermes gateway enroll` 命令传递给连接器端的 `/relay/enroll` 接口，或通过自主配置功能传递至 `/relay/provision` 接口），该密钥用于对其发出的WS升级请求进行身份验证。认证机制采用HMAC-SHA256算法，并配有多密钥轮换校验列表（网关端位于 `gateway/relay/auth.py`，连接器端位于 `src/core/relayAuthToken.ts`）。

| 方向 | 凭证 | 验证机制 |
|-----|-----------|---------|
| 网关 → 连接器 WS 升级 | 每个网关独立的密钥 | 在 `/relay` 升级请求中添加 `Authorization` 承载头。该令牌的格式为 `base64url(payload:exp:sig)`，其中 `payload = gatewayId`，`sig = HMAC(payload:exp, secret)`。连接器会检查令牌的有效性，若发现匹配错误、缺失或已被撤销，则拒绝升级请求并返回 **4401 错误码**。经过认证的租户信息来自连接器的存储，而非 `hello` 数据帧。 |
| 连接器 → 网关入站消息（`inbound` / `interrupt_inbound` 数据帧） | —（利用已认证的 WS 连接）| 入站消息会通过网关已认证的出站套接字传输（见 §3），因此无需为每条消息单独签名。虽然在注册/配置阶段仍会生成**每个租户专属的传输密钥**以保持向后兼容性，但该密钥不再用于入站消息的签名。 |

这就是所谓的**通道级**认证机制——它与平台级的加密方式不同，后者在中转路径中仍会被完全忽略（见 §6）。网关本身不存储任何平台级密钥；每个网关独立的密钥仅用于验证与连接器的连接。完整的威胁模型以及注册、密钥轮换和紧急断开功能的设计方案可见：`docs/connector-gateway-auth-design.md`（位于连接器代码仓库中）。

---

## 7. 单实例传输与管理平面（第 6 阶段）

第1至5阶段将连接器视为单租户架构的前端：针对某租户的入站事件会被分发至该租户对应的网关套接字。**第6阶段则实现了按实例进行消息投递**——同一个共享机器人可以在一个租户内为多名用户/智能体提供服务（如一个Discord群组或一个Telegram机器人），且不会发生跨用户投递的情况——同时还新增了一个小型**管理平面**，供智能体（或托管的门户）用来指定谁可以查看什么内容以及哪些内容是相关的。所有这些功能都位于**连接器端**；网关唯一需要新增的任务就是在启动时**声明自身的相关性策略**（见§7.3节）。

### 7.1 投递网关（连接器端，仅用于信息说明）

对于每一条入站事件，连接器会通过组合三个“与”逻辑的过滤条件来确定由哪些实例来接收该事件。这些过滤条件并非由网关实现——它们在连接器端运行——但它们定义了网关所依赖的消息投递规则：

| 层级 | 判断标准 | 权威信息来源 |
| --- | --- | --- |
| **所有者/范围 ∧ 主体** | 该实例是否有权*查看*此消息的发送者？ | 每用户的`user_id → instance`绑定关系（即所有者权限）+ 每个实例的`(群组, 频道)`范围授权 + `仅所有者可见`/`允许列表`/`任意主体`等策略。 |
| **可见性限制** | 该实例的所有者是否真的能在Discord中`查看该频道`？ | 实时的Discord访问控制列表（有效权限），采用“失败即拒绝”原则。用于缩小过宽的范围授权范围。 |
| **相关性判断** | 在满足查看条件的前提下，智能体是否应该处理该消息？ | 依据§7.3节中声明的相关性策略（如地址过滤/自由回复/允许机器人参与等）。 |
该组合机制只会**缩小**消息的投递范围（`deliver ⇔ authorized ∧ visible ∧ relevant`）；**消息所有者可直接绕过相关性过滤层**——作者自己的消息总会送达其自身的实例（因为无需@提及自己的智能体）。而由未绑定用户发送的消息则无法送达任何实例，系统会直接判定为传输失败。完整的设计方案及约束条件均保存在连接器代码库中（`NousResearch/gateway-gateway`），本节内容则为面向网关的使用概要。

### 7.2 管理接口路径（连接器端，需身份验证）

连接器会配置经过身份验证的管理接口路径。这些接口与WS升级流程采用**相同的双重认证机制**：要么使用由受管NAS签发的、包含`aud=agent:{instanceId}`字段的RS256 JWT，**要么**使用网关自身为每个网关生成的专用密钥令牌（参见§6.1节`make_upgrade_token`）。在两种情况下，连接器都会从其**存储的记录**中获取权威的`{tenant, instanceId}`信息——**绝不会**从请求正文中获取（请求正文中声明的`instanceId`将被忽略）。

| 路径 | 用途 |
| --- | --- |
| `POST /manage/link` | 生成临时代码，用于将平台账户与已认证的实例绑定（即 `/link <code>` 流程；连接器会从传入的事件中读取已认证的 `user_id`）。 |
| `POST /manage/scope`, `/manage/scope/release` | 为已认证的实例声明/释放 `(guild, channel)` 范围。一个频道最多只能属于一个实例（非重叠性是主键约束）。 |
| `POST /manage/principal` | 设置实例的主体策略（`owner-only` \| `allow-list` \| `any`）。 |
| `POST /manage/dm-default` | 设置用户的默认私信实例（当用户绑定多个实例时的私信判定规则）。 |
| `POST /relay/policy` | 声明实例的**相关性策略**（§7.3）。 |

这些接口由连接器管理（管理平面并不属于网关的代理路径）；网关仅会调用 `POST /relay/policy`（§7.3）。其余接口则由受管理的 Portal 或 `hermes` CLI 来驱动。

### 7.3 相关性策略声明（网关的职责）

相关性层（§7.1）负责为网关自身的行为参数（如 `require_mention`、`free_response_channels`、`{PLATFORM}_ALLOW_BOTS`）实现跨租户一致性。因此，用于中继传输的规则也完全相同，网关会将这些参数转化为**与平台无关**的策略，并在启动时（在确定每个网关的密钥后）将其通过 `POST /relay/policy` 发送出去。

相关代码位于（`gateway/relay/__init__.py` 中的 `relay_relevance_policy()` → `send_relay_policy()` 函数）：

| 字段 | 类型 | 来源 | 含义 |
| --- | --- | --- | --- |
| `platform` | 字符串 | `relay_platform_identity` | 该策略适用的平台。 |
| `requireAddress` | 布尔值 | `require_mention` | 非所有者发送的消息必须@提及或回复机器人，才被视为有效内容。 |
| `freeResponseScopes` | 字符串数组 | `free_response_channels` | 可免除`requireAddress`要求的范围（频道）ID。其范围词汇与§7.1中规定的权限范围相同。 |
| `allowOtherBots` | 布尔值 | `{PLATFORM}_ALLOW_BOTS ∈ {mentions, all}` | 是否允许机器人发送的消息通过（默认为关闭）。 |

认证信息为每个网关专用的升级令牌（参见§6.1），因此连接器会将该策略附加到已通过认证的实例上。网关是**唯一真实的数据来源**，并在每次启动时重新声明策略（即完全替换策略，方式与配置阶段对`routeKeys`的更新类似，具备自我修复功能）。当策略默认值为全部开启时，网关不会发送任何数据（因为连接器的缺失行默认设置已与之匹配）。该POST操作采用**软失败机制**：出现故障时会记录日志，然后继续启动流程——相关性判断是在授权环节之上叠加的一层优化措施（参见§7.1），并非启动流程的必要条件。此机制**不会新增网关接入接口**，也**无需新的凭证**——它直接复用每个网关的专用密钥以及与 `/relay/provision` 相同的服务器。

> 相关性判断会在连接器唤醒已缩减至零数量的智能体之前执行（即第5阶段），因此被排除的聊天内容永远不会触发智能体的启动——相关性既是实现智能体数量缩减的主要手段，也是一种内容正确性过滤机制。

## 8. 网关端平台行为控制（企业版）

在企业级部署中，平台行为是在网关端通过 `platforms.relay.extra.<platform>` 选项进行配置的，这些选项为对应平台原生选项中的部分支持项。中转通道不会读取原生的平台配置块（例如 `platforms.slack`）；连接器会以帧元数据的形式（参见第4节）接收这些控制措施的*执行结果*，并直接按照既定规则执行操作——它本身并不具备任何平台行为策略。

```yaml
platforms:
  relay:
    extra:
      slack:
        reply_in_thread: true   # default
```

解决方案：嵌套的 `extra.<platform>` 对象优先生效；若不存在此类嵌套结构，则采用旧式的扁平键值形式作为备选，最终仍为默认设置。权威数据来源为 `RelayAdapter._effective_reply_in_thread`（位于 `gateway/relay/adapter.py` 文件中）。其数值处理规则与原生 Slack 适配器完全一致——`1/true/yes/on`（不区分大小写且去除空白字符）均视为“开启”状态，其余所有值均视为“关闭”状态；因此，用 YAML 引号包裹的 `"false"` 也会被当作关闭指令处理，而不会被视为真值字符串。

当前 Slack 的控制参数如下：

| 键名 | 默认值 | 效果 |
| --- | --- | --- |
| `reply_in_thread` | `true` | `true`：每条消息独立成线程——每条顶级私信消息都会创建属于自己的线程（状态、进度、提示信息及最终回复均会携带该 `metadata.thread_id`）。`false`：扁平式连续私信——发送的帧不会包含线程标识（并非被省略，而是被移除），所有私信共享同一个会话。 |
| `dm_top_level_threads_as_sessions` | `true` | 用于保持与原生系统的兼容性（该参数与 `platforms.slack.extra.dm_top_level_threads_as_sessions` 功能相同）。`true`：在每条消息独立成线程的模式下，每条顶级私信消息都会对应一个独立的会话，从而使多条消息并行处理。`false`：保留线程式回复功能，但跳过会话标识——仅维持一个连续的私信会话（即旧式的串行/队列处理方式）。在扁平模式下此参数无任何效果，因为该模式始终只维持一个连续会话。 |
当已知触发时间戳时，消息帧和状态帧始终会携带该时间戳锚点（两种模式下状态更新均为强制性的）：Slack的状态行是按聊天线程划分的；而在扁平模式下，发送端的锚点处理机制可确保状态锚点不会混入回复内容中。关于该内置键的详细语义，请参阅 `website/docs/user-guide/messaging/slack.md`。

线程锚点解析通过同一个核心处理节点（`RelayAdapter._apply_slack_thread_anchor`）应用于所有类型的发送通道——无论是文本消息（`send`）还是媒体消息（`send_media`）。媒体帧同样通过连接器端的Slack发送器传输，且仅会在消息元数据中添加 `thread_id` 字段，因此附件的锚点解析方式与文本回复一致：在“每条消息独立成线程”模式下会被嵌入元数据中，而在扁平模式下则会被移除。

这些更改需在网关重启后才会生效，无需涉及连接器层面。

---

## 9. 版本控制策略

- `contract_version` 为整数类型；仅在实验阶段进行功能扩展时（如新增可选字段或操作指令）才需升级该版本号。
- 若出现破坏性变更（如字段重命名/删除、语义改变），则必须同步更新两个代码库并提升版本号。
- 连接器的第一个 Pull Request 应注明其所依据的该文件的提交 SHA 值。
