# 中继 ↔ 连接器契约（v1，实验性版本）

> **状态：** 实验性版本。在至少有两个一级平台（Discord + Telegram）对其完成验证之前，该契约可能会在未经过废弃周期处理的情况下发生变更。实验阶段的演进仅允许**增量式**修改，且需通过 `contract_version` 进行控制。任何破坏性变更都将同步更新两个代码仓库。

本文档是 **Hermes 网关**（Python，位于 `gateway/relay/` 目录）与 **连接器**（Node/TypeScript，位于 `NousResearch/gateway-gateway` 目录）之间的正式接口规范。连接器实现者首先需要阅读此文件。

网关会运行一个通用的 `RelayAdapter`，该适配器会**向外**调用连接器，在握手阶段接收 `CapabilityDescriptor`，随后通过每轮双向 WebSocket 交换标准化的 `MessageEvent`（入站消息）及操作指令（出站指令）。网关永远不会知晓自己所对接的具体平台是哪一个；所有与特定平台相关的套接字/身份验证逻辑均由连接器负责处理。

---

## 1. 握手流程

1. 网关建立传输连接（`connect`）。
2. 网关调用 `handshake()` 方法，连接器则返回一个 `CapabilityDescriptor`（见第2节），其中描述了该适配器实例所支持的平台信息。
3. 网关根据该描述符配置适配器的相关参数（如字符限制、长度单位、草稿/编辑/线程/Markdown功能等），并注册入站消息处理函数。
4. 此后，连接器开始流式传输入站事件，并接收网关发出的出站操作指令。

`contract_version` 字段（当前值为 `1`）会包含在描述符中。为保持向前兼容性，网关会忽略未知的描述符字段，同时用默认值填充缺失的可选字段。

---

## 2. CapabilityDescriptor（握手数据载荷）

为 JSON 格式对象。其定义来源为 `gateway/relay/descriptor.py`。

| 字段 | 类型 | 是否必填 | 含义 |
| --- | --- | --- | --- |
| `contract_version` | int | 是 | 契约版本号（同一版本内仅支持增量式修改）。 |
| `platform` | string | 是 | 平台名称（例如 `"discord"`、`"telegram"`）。 |
| `label` | string | 是 | 便于人类理解的标签名称。 |
| `max_message_length` | int | 是 | 字符限制值；网关会将其暴露为 `MAX_MESSAGE_LENGTH`。若值为 0，则视为 4096 字符。 |
| `supports_draft_streaming` | bool | 是 | 是否支持原生草稿流预览功能。 |
| `supports_edit` | bool | 是 | 是否支持基于编辑的流式传输；若该值为 false，接收方将只能以每段一条消息的方式处理数据。 |
| `supports_threads` | bool | 是 | 是否具备 `create_handoff_thread` 功能。 |
| `markdown_dialect` | string | 是 | `"plain"`、`"markdown_v2"`、`"discord"` 等格式（该字段会影响 `supports_code_blocks` 的行为）。 |
| `len_unit` | string | 是 | 字符长度单位，可选值为 `"chars"`（使用内置长度函数）或 `"utf16"`（Telegram 使用的 UTF-16 代码单元）。 |
| `emoji` | string | 否 | 显示用的表情符号，默认为 🔌。 |
| `platform_hint` | string | 否 | 系统提示用的平台标识信息。 |
| `pii_safe` | bool | 否 | 是否会在会话描述中隐藏敏感个人信息。 |

大多数字段实际上都是从网关现有的 `PlatformEntry` 对象中提取而来的；而仅在运行时才需要的字段（如 `len_unit`、`supports_*`、`markdown_dialect`）则来自对应平台适配器的功能方法。

---

## 3. 入站消息：`MessageEvent` 数据结构

连接器会将每个平台发送的原始消息事件转换为标准的 `MessageEvent` 对象（定义位于 `gateway/platforms/base.py`），然后再将其传递给网关。**入站消息是通过带签名的 HTTP POST 请求传输的，而非通过出站的 `/relay` WebSocket 通道**（具体传输方式详见下文的说明）。网关会通过嵌入在消息中的 `SessionSource` 对象调用 `build_session_key()` 方法来生成会话密钥——因此，正确填写各类标识字段是连接器需要承担的最重要的职责。

### 入站消息的传输方式（带签名的 HTTP POST，而非出站 WebSocket）

对于握手、出站操作指令（见第4节）以及网关自身的 `/stop` 停止请求（见第5节），网关会**向外**调用连接器上的 `/relay` WebSocket 通道。然而，入站消息的传输方向则相反：连接器会将标准化后的事件通过 POST 请求发送到网关的入站接收端点——在连接器端为 `HttpGatewayDelivery`，在网关端为 `gateway/relay/inbound_receiver.py`。之所以如此设计，是因为通常情况下，负责处理某个平台消息并生成入站事件的连接器实例，并不是网关建立出站 WebSocket 连接所对应的那个实例；因此，入站消息必须发送到特定租户的端点（该端点可能由多个网关实例共同负载均衡处理），而非依赖某个单个网关的出站套接字。每次消息传输都会使用针对该租户的**专用传输密钥**进行 HMAC 签名（见第6.1节）；网关在接收消息之前，会先对原始字节数据进行签名验证。具体的 POST 请求目标地址如下：

- `POST {gatewayEndpoint}`            → `{"type":"message", "event": <MessageEvent>}`
- `POST {gatewayEndpoint}/interrupt`  → `{"type":"interrupt", "session_key", "reason"?}`（见第5节）

> 该契约的早期草案曾尝试通过 WebSocket 的 `inbound` 框架来传输入站消息。但这种方案仅适用于单实例场景，且出现于多实例套接字所有权及通道认证机制诞生之前；目前最终采用的方案即为上述基于带签名 HTTP 请求的传输方式。

### SessionSource 字段（消息的传输字段内容）

这些字段的定义来源为 `gateway/session.py` 中的 `SessionSource.to_dict()` 方法。它们代表了网关在接收消息时所接受的所有关键信息。`platform`、`chat_id`、`chat_type`、`user_id`、`user_name`、`thread_id`、`chat_name` 和 `chat_topic` 这些字段始终都会出现（可能值为 `null`）；其余字段则仅在对应值被设置时才会包含在消息中。

| 字段 | 类型 | 是否总是发送 | 含义 |
| --- | --- | --- | --- |
| `platform` | string | 是 | 平台名称，与描述符中的 `platform` 字段一致。 |
| `chat_id` | string | 是 | 对话的主要标识符（即频道或聊天室编号），同时也是用于生成会话密钥的标识字段。 |
| `chat_type` | string | 是 | 对话类型，可选值为 `dm`（私信）、`group`（群组）、`channel`（频道）、`thread`（线程）或 `forum`（论坛）。 |
| `chat_name` | string\|null | 是 | 便于人类理解的聊天室名称。 |
| `user_id` | string\|null | 是 | 消息发送者的标识符，同样用于生成会话密钥。 |
| `user_name` | string\|null | 是 | 发送者的显示名称。 |
| `thread_id` | string\|null | 是 | 当消息位于线程中时，用于标识该线程或论坛主题的编号，同样用于生成会话密钥。 |
| `chat_topic` | string\|null | 是 | 频道或聊天室的标题/描述信息（适用于 Discord、Slack 等平台）。 |
| `user_id_alt` | string | 否 | 平台特有的备用标识符，例如 Signal 的 UUID 或飞书平台的 union_id。 |
| `chat_id_alt` | string | 否 | 备用聊天标识符，例如 Signal 群组内部的编号。 |
| `guild_id` | string | 否 | Discord 社群、Slack 工作空间或 Matrix 服务器的层级标识。**对于实现 Discord 服务器间的隔离功能而言，该字段是必需的**，同样用于生成会话密钥。 |
| `parent_chat_id` | string | 否 | 当 `chat_id` 指向某个线程时，用于标识该线程所在的父频道编号。 |
| `message_id` | string | 否 | 触发当前操作的原始消息的编号（用于固定消息、回复或回应操作）。 |

> 在网关端的数据结构中确实存在 `is_bot` 字段，用于区分消息发送者是否为机器人或 webhook 请求；但在 v1 版本中，**该字段刻意未包含在传输数据中**，也不会被纳入 `to_dict()` 的输出结果中。在将该字段添加到连接器的 `SessionSource` 中之前，必须先在网关端将其加入对应结构并同步到 `to_dict()` 输出中，以避免版本冲突。

### 各平台的 SessionSource 标识字段对照表

| 平台 | chat_id | chat_type | user_id | thread_id | guild_id |
| --- | --- | --- | --- | --- | --- |
| **Discord** | 频道编号 | `dm`/`group`/`thread` | 消息发送者编号 | 线程所在频道编号（仅在线程中有效） | **社群编号**（实现服务器隔离功能所必需） |
| **Telegram** | 聊天室编号 | `dm`/`group`/`forum` | 发件人编号 | 论坛主题编号（仅适用于论坛） | — |

> 若错误地填写 Discord 平台的 `guild_id`，则会导致两个不同的服务器被错误地合并到同一个会话中。这是该系统存在的首个高严重性风险点。网关的 `build_session_key()` 方法是判断消息是否符合规范的依据：对于给定的 `SessionSource`，连接器进行的标准化处理必须能够生成与 Python 适配器所生成的密钥完全一致的密钥。（第一阶段的测试用例会确保输入相同则生成的密钥也相同。）

### 机器人身份与租户概念的区分（单机器人服务多租户模式，详见附录A）

消息数据结构中会单独设置一个字段，用于标识**发送消息的机器人身份**，该字段与租户概念是相互独立的。租户身份是通过消息本身携带的标识符来确定的，例如 Discord 的 `guild_id`、Telegram 的 `chat_id`，或是 webhook 的路径/子域名——**绝不会**根据发送消息所使用的令牌、套接字或进程来判定租户身份。这样的设计使得同一个共享机器人能够为多个租户提供服务（即第6阶段的目标），而无需占用额外的字段空间。

---

## 4. 出站操作：操作指令集

网关会通过传递包含操作指令的字典来向连接器发起请求。相关实现代码位于 `gateway/relay/transport.py` 和 `gateway/relay/adapter.py` 文件中。

| 操作类型 | 所需字段 | 返回结果 |
| --- | --- | --- |
| `send` | `chat_id`、`content`、`reply_to?`、`metadata?` | `{success: bool, message_id?, error?}` |
| `edit` | `chat_id`、`message_id`、`content`、`metadata?` | `{success: bool, error?}` |
| `typing` | `chat_id` | `{success: bool}` |
| `follow_up` | `session_key`、`kind`、`content`、`metadata?` | `{success: bool, message_id?, error?}` |

网关还会通过一个独立的代理调用方法 `get_chat_info(chat_id)` 来获取至少包含 `name` 和 `type` 信息的聊天信息。媒体类型相关的操作指令也会采用与上述相同的消息结构格式（该格式将在后续的契约修订中进一步完善，仍为增量式更新）。

**`follow_up` 操作属于 A2 级别的能力操作。**某些入站消息会携带用于操作**共享机器人身份**的凭证，例如 Discord 的交互式消息续传令牌。根据第6节的规定，连接器会在接收端直接移除这些凭证，并将其存储在以会话标识为键的专用存储库中；这些凭证**绝不会**传递给网关。若要使用此类功能，网关需要发起 `follow_up` 操作，同时指定当前所处的会话标识 `session_key` 以及对应的操作类型 `kind`（例如 `discord.interaction_token`）——**绝不能直接传递令牌本身**。连接器会从自己的存储库中获取真实的操作凭证，检查该凭证是否属于当前租户所有（租户 B 绝不可能使用租户 A 的操作权限），之后再将处理结果返回给网关。如果该操作能力不存在、已过期或租户不匹配，网关将返回 `success: false` 的结果——按照设计，一旦网关的密钥被泄露，它将不再拥有任何操作凭证。相关实现代码位于 `gateway/relay/transport.py`（`send_follow_up` 方法）和 `gateway/relay/adapter.py` 文件中。

---

## 5. 中断处理（`/stop` 请求路由机制）

- **网关 → 连接器：** 网关会通过出站的 WebSocket 通道发送 `send_interrupt(session_key, reason?)` 请求，以在当前消息处理轮次中途触发停止操作。根据路由规则，连接器**必须**将此请求转发给正在处理该 `session_key` 的网关实例。
- **连接器 → 网关：** 针对某个 `session_key` 的中断请求会以**带签名的 HTTP POST 请求**的形式发送到 `{gatewayEndpoint}/interrupt` 地址（具体传输方式详见第3节），随后由适配器中的 `on_interrupt(session_key, chat_id)` 方法将其接入现有的会话级中断处理机制，从而仅取消当前正在处理的那一轮消息处理，而不会影响其他轮次的消息处理。

网关向连接器发送的 `/stop` 停止请求是通过出站的 WebSocket 通道传输的；而连接器向网关发送的中断请求则与普通标准化消息一样，通过相同的带签名 HTTP 入站通道进行传输。

---

## 6. 信任边界与签名数据处理（A2级别要求）

**连接器是整个系统中的唯一加密/身份验证边界，网关不会对任何信息进行重新验证。**

Webhook 请求的签名算法包括 Discord 的 ed25519、Twilio 的 HMAC 以及 WeCom 的 BizMsgCrypt 等，这些算法都是基于原始字节数据进行计算的；此外，某些消息内容还会使用共享密钥进行**加密处理**。由于连接器需要为多个租户服务，并且要保管每个租户对应的平台密钥，因此它必须承担起相应的安全责任。- **在边缘端进行验证/解密**（即密钥存储的唯一位置）；  
- 将有效载荷**标准化**为特定租户范围的 `MessageEvent` 对象（见第3节）；  
- **移除有效载荷中的任何共享身份相关功能**，并将其存入以会话为键的权限保险库中（详见第4节“后续处理”）；  
- **仅转发经过清洗的 `MessageEvent` 对象**——绝不会传输原始的签名内容。  

因此，网关在数据中转路径上**不会**执行任何平台签名或加密验证操作，而是直接信任已标准化的事件数据。这是网关端强制遵循的不变原则（参见 `tests/gateway/relay/test_relay_sheds_crypto.py`：中转模块不会导入或调用任何平台级加密功能）。  

**为何不采用“逐字节转发签名内容以便网关重新验证”的方式？**  
在不可信且可被丢弃的租户网关环境下，这种方案存在根本性问题：  
- 若要重新验证 Twilio HMAC 或 WeCom 的加密内容，就必须将**共享签名密钥**交给网关——而这本身就会导致信息泄露；而在共享机器人场景下，甚至会引发**跨租户**的信息泄露。  
- WeCom 的有效载荷是使用共享密钥加密的；连接器仅为了路由目的需要在边缘端解密，因此若转发密文，同样需要将密钥交给网关。  
- Discord 的交互令牌就**包含在签名后的 JSON 内容中**——你无法既保留这些字节数据又同时移除凭证信息，因为二者其实是同一组字节。  

正因如此，系统刻意放弃了字节级保留的做法：连接器会对清洗后的事件数据进行重新序列化，而网关则直接信任该数据。这种方式还将直通模式与中转模式统一起来——两种模式的处理流程均为“在边缘端验证 → 生成标准化事件”，仅在传输方式上有所区别。完整的 A2 设计理念及连接器端的权限保险库实现详见 `docs/capability-trust-boundary.md`（连接器代码库位于 `gateway-gateway` 目录）。  

### 6.1 频道认证（连接器与网关之间的连接本身）  

在 A2 设计中，连接器成为平台密钥的唯一持有者，而网关则可能由客户自行管理且暴露于互联网上，因此连接器与网关之间的连接本身也需要进行认证。网关拥有两个通过注册流程生成的凭证（通过 `hermes gateway enroll` 命令生成，供连接器调用 `/relay/enroll` 接口使用）：一个**针对单个网关的密钥**，以及一个**针对特定租户的传输密钥**。这两种密钥均采用 HMAC-SHA256 算法，并配有多密钥轮换验证机制（网关端实现位于 `gateway/relay/auth.py`，连接器端实现位于 `src/core/relayAuthToken.ts` 和 `src/core/deliverySigning.ts`）。  

| 数据流向 | 凭证类型 | 认证机制 |
|----------|----------|----------|
| 网关 → 连接器 WebSocket 升级请求 | 单个网关密钥 | 在 `/relay` 升级请求中通过 `Authorization` 承载头传递该密钥。令牌格式为 `base64url(payload:exp:sig)`，其中 `payload = gatewayId`，`sig = HMAC(payload:exp, secret)`。连接器会验证该令牌，若存在不匹配、缺失或已被撤销的情况，则拒绝升级请求并返回 **4401** 错误码。经过认证的租户信息来自连接器的内部存储，而非 `hello` 框架中的数据。 |
| 连接器 → 网关的入站 POST 请求 | 特定租户的传输密钥 | 请求需包含两个头部字段：`x-relay-timestamp`（以秒为单位的 Unix 时间戳）和 `x-relay-signature`（十六进制格式的 `HMAC(ts.rawBody, deliveryKey)`）。网关会在 ±300 秒的重放窗口内，根据**原始字节内容**进行验证，只有通过验证才会接受该事件，否则返回 **401** 错误码。 |  

这就是用于连接认证的机制——它与平台级加密功能是相互独立的，因为数据中转路径仍会完全丢弃平台级加密内容（见第6节）。网关本身不持有任何平台级密钥，这两个密钥仅用于验证连接器与网关之间的连接。完整的威胁模型以及注册、密钥轮换和紧急关闭机制的设计方案详见 `docs/connector-gateway-auth-design.md`（连接器代码库）。  

---

## 7. 版本控制策略  

- `contract_version` 为整数类型；仅在实验阶段出现**增量式变更**时才升级版本（例如新增可选字段或操作类型）。  
- 若发生**破坏性变更**（如字段重命名/删除、语义改变等），则需同时协调更新两个代码库，并相应提升版本号。  
- 连接器的第一个 Pull Request 应注明其所依据的该文件的提交 SHA 值。
