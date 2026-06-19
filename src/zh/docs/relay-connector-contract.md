# 中继 ↔ 连接器合约（v1，实验性）

> **状态：** 实验性。在至少有两个一级平台（Discord + Telegram）对其完成验证之前，该合约**可能在不经过废弃周期的情况下发生变化**。实验阶段的演进仅允许**增量式**修改，且受 `contract_version` 控制。若发生破坏性变更，则需同步更新两个代码库。

本文档是 **Hermes 网关**（Python，`gateway/relay/`）与 **连接器**（Node/TypeScript，`NousResearch/gateway-gateway`）之间的正式接口。连接器实现者首先需要阅读此文件。

网关会运行一个通用的 `RelayAdapter`，该适配器会**向外**连接至连接器，在握手阶段接收 `CapabilityDescriptor`，随后通过每轮双向 WebSocket 交换标准化的 `MessageEvent`（入站消息）及操作指令（出站指令）。网关不会知晓自身所对接的具体平台；所有与平台相关的套接字/身份逻辑均由连接器负责处理。

---

## 1. 握手流程

1. 网关建立传输连接（`connect`）。
2. 网关调用 `handshake()` 方法；连接器返回一个 `CapabilityDescriptor`（见第2节），用于描述该适配器实例所支持的平台。
3. 网关根据描述符配置适配器的相关参数（如字符限制、长度单位、草稿/编辑/线程/Markdown功能等），并注册入站消息处理函数。
4. 此后，连接器开始流式传输入站事件，并接收网关发出的出站操作指令。

`contract_version`（当前为 `1`）会包含在描述符中。为保证向前兼容性，网关会忽略未知的描述符字段；对于缺失的可选字段，则会使用默认值填充。

---

## 2. CapabilityDescriptor（握手数据包内容）

为 JSON 对象。权威来源：`gateway/relay/descriptor.py`。

| 字段 | 类型 | 是否必填 | 含义 |
| --- | --- | --- | --- |
| `contract_version` | int | 是 | 合约版本（同一版本内仅支持增量式修改）。 |
| `platform` | string | 是 | 平台名称（例如 `"discord"`、`"telegram"`）。 |
| `label` | string | 是 | 便于人类理解的标签。 |
| `max_message_length` | int | 是 | 字符限制；网关会将其暴露为 `MAX_MESSAGE_LENGTH`。值为 0 时视为 4096。 |
| `supports_draft_streaming` | bool | 是 | 是否支持原生的草稿流预览功能。 |
| `supports_edit` | bool | 是 | 是否支持基于编辑的流式传输；若为 false，客户端将只能以每段一条消息的方式接收内容。 |
| `supports_threads` | bool | 是 | 是否具备 `create_handoff_thread` 功能。 |
| `markdown_dialect` | string | 是 | `"plain"`、`"markdown_v2"`、`"discord"` 等（该字段会影响 `supports_code_blocks` 的设置）。 |
| `len_unit` | string | 是 | `"chars"`（内置长度计算单位）或 `"utf16"`（Telegram 的 UTF-16 代码单元）。 |
| `emoji` | string | 否 | 显示用的表情符号（默认为 🔌）。 |
| `platform_hint` | string | 否 | 系统提示用的平台标识。 |
| `pii_safe` | bool | 否 | 是否会在会话描述中隐藏敏感个人信息。 |

大部分字段均源自网关现有的 `PlatformEntry` 结构；仅在运行时才需要的字段（如 `len_unit`、`supports_*`、`markdown_dialect`）则来自对应平台适配器的功能方法。

---

## 3. 入站消息：`MessageEvent` 数据结构

连接器会将每个平台的原始消息事件标准化为 `MessageEvent` 对象（定义位于 `gateway/platforms/base.py`），然后将其发送给网关。入站消息是通过网关的**出站方向 `/relay` WebSocket**传输的（详见下文的传输说明）——连接器会通过网关已建立的套接字，向下推送 `inbound` 类型的数据帧。网关会利用嵌入在 `SessionSource` 中的信息通过 `build_session_key()` 方法生成会话密钥；因此，正确设置各识别字段是连接器需承担的最重要的职责。

### 入站传输方式（WS 后通道，非 HTTP）

网关会**向外**连接至连接器的 `/relay` WebSocket，用于握手、发送出站操作指令（见第4节）以及自身的 `/stop` 停止请求（见第5节）。入站消息则通过同一套接字的**反向通道**传输：连接器会通过网关的出站 WebSocket 向下推送 `inbound` 类型的数据帧（以及用于第5节的 `interrupt_inbound` 指令）。网关**没有专门的入站 HTTP 接口**——托管式的网关无需（也无法）暴露任何入站端口；所有数据均通过其自身建立的连接进行传输。

**多实例路由机制。**负责处理某个平台消息的连接器实例（即生成入站事件的实例），通常**并非**网关建立出站 WebSocket 连接的目标实例。因此，该生成事件的实例会将消息发布到连接器内部的**中继总线**上（基于 Redis 的发布/订阅机制，位于 `src/core/relayBus.ts` 中），并使用租户标识作为键值。每个连接器实例都会订阅该总线，并将每条消息路由至该租户的**本地**会话中（通过 `RelayServer.routeBusMessage` 方法实现）；最终，实际持有网关套接字的那个实例才会处理该消息，而那些没有该租户本地会话的实例则不会执行任何操作。因此，跨实例的消息传递实际上只是在同一集群内的 Redis 通信，而非公共 HTTP 调用。

数据帧格式（连接器 → 网关，通过 WebSocket 传输）：

- `{"type":"inbound", "event": <MessageEvent>, "bufferId"?}`
- `{"type":"interrupt_inbound", "session_key", "chat_id"}`（用于第5节）

**信任机制。** WebSocket 升级过程会使用网关为每个网关单独配置的密钥进行身份验证（见第6.1节），因此整个通信通道是端到端可信的——入站数据帧无需再单独进行 HMAC 签名（因为经过身份验证的套接字本身已足以证明消息的来源，这正是旧版 HTTP 方式所依赖的机制）。而通过中继总线进行的传输则发生在连接器的信任域内（与该实例的租约、缓冲区及功能存储处于同一安全域）。

> 该合约的早期版本是通过带签名的**HTTP POST**请求将入站消息发送到 `gatewayEndpoint` 地址（即 `HttpGatewayDelivery` 机制，以及网关端的 `inbound_receiver` 接口），并使用针对每个租户的专用密钥进行 HMAC 签名。但这种方式要求每个网关都必须公开一个可访问的入站 URL——对于没有公网 IP 的托管式网关而言，这是不可行的。上述基于 WS 的后通道机制已取代了这种做法；为保持向前兼容性，仍会保留针对每个租户的专用密钥，但已不再用于入站消息传输。`gatewayEndpoint` 仅用于**直通通道**（如 Discord 交互、Twilio 等二级/三级 webhook），这是一种独立的同步转发路径，不属于本文档的讨论范围。

### SessionSource 字段（网络层传输数据）

权威来源：`gateway/session.py` 中的 `SessionSource.to_dict()` 方法。这些字段代表了网关在网络层接收到的所有数据键值对。`platform`、`chat_id`、`chat_type`、`user_id`、`user_name`、`thread_id`、`chat_name` 和 `chat_topic` 这些字段始终会被包含在传输数据中（可能值为 `null`）；其余字段则仅在被设置时才会出现在传输数据中。

| 字段 | 类型 | 是否始终传输 | 含义 |
| --- | --- | --- | --- |
| `platform` | string | 是 | 平台名称（与描述符中的 `platform` 字段一致）。 |
| `chat_id` | string | 是 | 对话的主要标识符（频道/聊天室）。也可用作会话密钥的识别字段。 |
| `chat_type` | string | 是 | 对话类型，包括 `dm`（私信）、`group`（群组）、`channel`（频道）、`thread`（线程）和 `forum`（论坛）。 |
| `chat_name` | string\|null | 是 | 便于人类理解的聊天室名称。 |
| `user_id` | string\|null | 是 | 消息发送者的标识符。也可用作会话密钥的识别字段。 |
| `user_name` | string\|null | 是 | 发送者的显示名称。 |
| `thread_id` | string\|null | 是 | 当消息位于线程中时，用于标识该线程或论坛主题的 ID。也可用作会话密钥的识别字段。 |
| `chat_topic` | string\|null | 是 | 频道的主题或描述信息（适用于 Discord、Slack 等平台）。 |
| `user_id_alt` | string | 否 | 平台特定的稳定备用标识符（如 Signal 的 UUID、飞书の union_id）。 |
| `chat_id_alt` | string | 否 | 备用聊天 ID（例如 Signal 群组的内部 ID）。 |
| `guild_id` | string | 否 | Discord 社群、Slack 工作空间或 Matrix 服务器的标识。**对于实现 Discord 服务器间的会话隔离而言，此字段是必需的**，也可用作会话密钥的识别字段。 |
| `parent_chat_id` | string | 否 | 当 `chat_id` 指向某个线程时，用于标识该线程所在的父频道。 |
| `message_id` | string | 否 | 触发当前操作的原始消息的 ID（用于固定消息、回复或互动操作）。 |

> `is_bot` 字段用于标识消息发送者是否为机器人/ webhook，该字段存在于网关端的数据结构中，但在 v1 版本中**有意未包含在网络层传输数据中**——它也不在 `to_dict()` 方法的返回结果中。在将该字段加入连接器端的 `SessionSource` 之前，必须先在网关端及 `to_dict()` 方法中添加该字段（属于增量式更新）。

### 各平台的 SessionSource 识别字段

| 平台 | chat_id | chat_type | user_id | thread_id | guild_id |
| --- | --- | --- | --- | --- | --- |
| **Discord** | 频道 ID | `dm`/`group`/`thread` | 消息发送者 ID | 线程所在频道的 ID（仅在线程中有效） | **社群 ID**（实现服务器间会话隔离所必需） |
| **Telegram** | 聊天 ID | `dm`/`group`/`forum` | 发件人 ID | 论坛主题 ID（仅适用于论坛） | — |

**若 Discord 的 `guild_id` 设置错误，会导致两个不同的服务器被合并到同一个会话中。** 这是当前最严重的风险之一。网关的 `build_session_key()` 方法是判断是否符合规范的依据：对于给定的 `SessionSource`，连接器进行的标准化处理必须能生成与 Python 适配器相同格式的密钥。（第一阶段的测试用例会确保输入固定时，生成的密钥也固定不变。）

### 机器人身份与租户的区分（单机器人服务多个租户，详见附录 A）

消息数据中会携带**发送机器人的身份信息**，该字段与租户信息是相互独立的。租户身份是通过消息本身的识别字段确定的（如 Discord 的 `guild_id`、Telegram 的 `chat_id`，以及 webhook 的路径/子域名），**绝不会**根据发送消息的令牌、套接字或进程信息来判断。这样一来，同一个机器人就可以同时为多个租户提供服务（即第六阶段的目标），而无需占用额外的字段。

---

## 4. 出站操作：操作指令集

网关会通过传输层发送包含操作指令的字典结构。权威来源：`gateway/relay/transport.py` 和 `gateway/relay/adapter.py`。

| 操作类型 | 所需字段 | 返回结果 |
| --- | --- | --- |
| `send` | `chat_id`、`content`、`reply_to?`、`metadata?` | `{success: bool, message_id?, error?}` |
| `edit` | `chat_id`、`message_id`、`content`、`metadata?` | `{success: bool, error?}` |
| `typing` | `chat_id` | `{success: bool}` |
| `follow_up` | `session_key`、`kind`、`content`、`metadata?` | `{success: bool, message_id?, error?}` |

`get_chat_info(chat_id)` 是另一个独立的代理调用，至少会返回 `{name, type}` 这两项信息。媒体相关操作也会采用相同的消息结构格式（具体细节将在后续的合约修订中确定，目前仍为增量式扩展）。

**`follow_up` 操作（属于 A2 能力范畴的操作）。**某些入站消息会携带用于操作**共享机器人身份**的凭证（例如 Discord 交互中的后续操作令牌）。根据第6节的规定，连接器会在边缘节点处移除这些凭证，并将其存储在以会话标识为键的专用存储库中；这些凭证**永远不会传递到网关端**。若要使用该功能，网关需要发送 `follow_up` 操作指令，同时指定**当前所处的会话标识**（即 `session_key`）以及对应的操作类型 `kind`（例如 `discord.interaction_token`）——注意，这里传递的并非令牌本身。连接器会从其存储库中获取真实的凭证值，检查该凭证是否属于当前租户（租户 B 绝不能使用租户 A 的凭证），之后再将凭证发送出去。如果该功能不存在、已过期或租户不匹配，返回的 `success` 值将为 `false`——按照设计，此时网关无需再尝试重新发送请求，因为泄露了网关权限的实例根本无法持有任何功能相关的凭证。权威来源：`gateway/relay/transport.py`（`send_follow_up` 方法）和 `gateway/relay/adapter.py`。

---

## 5. 中断操作（`/stop` 路由）- **网关 → 连接器**：通过出站 WS 发送 `send_interrupt(session_key, reason?)` 命令，以在对话进行中插入 `/stop` 指令。根据路由不变性，连接器**必须**将该指令转发给正在处理该 `session_key` 的网关实例。
- **连接器 → 网关**：针对某个 `session_key` 的入站中断指令会以 `interrupt_inbound` 数据帧的形式通过网关的出站 WS 传递（参见§3传输说明）——通过中继总线跨实例路由至持有该套接字的实例——随后由适配器的 `on_interrupt(session_key, chat_id)` 函数将其接入现有的会话级中断机制，从而精确终止当前对话轮次（其他对话轮次不受影响）。

两种方向的通信均依托网关的出站 WS：网关向连接器发送的 `/stop` 指令通过该通道发出，而连接器向网关发送的中断指令则作为标准化事件，通过同一条“入站”回传通道传输。

---

## 6. 信任边界与签名内容处理（A2）

**连接器是唯一的加密/身份验证边界。网关不会对任何内容进行重新验证。**

Webhook签名（Discord的ed25519、Twilio的HMAC、WeCom的BizMsgCrypt）是基于原始字节直接计算的，部分数据载荷还会使用共享密钥进行*加密*处理。连接器为多个租户托管一个**共享**的机器人，并存储所有租户的平台密钥，因此它需要：

- 在边缘端**验证/解密**（因为密钥仅存于此处）；
- 将数据载荷**标准化**为针对特定租户的 `MessageEvent` 格式（参见§3）；
- 从载荷中移除所有与共享身份相关的信息，并将其存储在以会话为键的密钥库中（详见§4的“后续处理”部分）；
- **仅转发经过净化的 `MessageEvent`**，而绝不传输原始的签名内容。

因此，网关在中继路径上不会对平台签名或加密内容进行任何验证，而是直接信任标准化后的事件。这是网关端强制遵循的不变性（参见 `tests/gateway/relay/test_relay_sheds_crypto.py`：中继模块不会导入或调用任何平台级加密功能）。

**为何不“逐字节转发签名内容以便网关重新验证”？**
在不可信且可被替换的租户网关环境下，这种方案存在根本性问题：

- 要重新验证Twilio的HMAC或WeCom的加密内容，就必须将**共享签名密钥**交给网关——而这本身就是安全漏洞；而在共享机器人上，这还会导致*跨租户*的信息泄露。
- WeCom的载荷是使用共享密钥加密的；连接器仅为路由目的需要在边缘端解密，因此若转发密文，同样需要将密钥交给网关。
- Discord的交互令牌就**包含在**签名的JSON载荷中——你无法既保留这些字节又移除凭证，因为它们本就是同一组数据。

因此，故意放弃了字节级保留的做法：连接器会对净化后的事件进行重新序列化，网关则信任该序列化后的数据。这种方式还将直通模式与中继模式统一起来——两者均为“在边缘端验证 → 发送标准化事件”，仅在传输方式上有所区别。完整的A2设计理念及连接器端的密钥库信息，请参阅 `docs/capability-trust-boundary.md`（连接器代码仓库：`gateway-gateway`）。

### 6.1 频道认证（连接器⇄网关连接本身）

由于A2方案规定连接器是平台密钥的唯一持有者，而网关可能由客户自行管理且暴露在互联网上，因此连接器与网关之间的连接通道本身也需要进行认证。网关会持有由注册或配置流程生成的**每个网关专用的密钥**（通过 `hermes gateway enroll` 命令传递给连接器，路径为 `/relay/enroll`；或通过管理型自动配置生成，路径为 `/relay/provision`），该密钥用于验证其出站WS升级请求。认证机制采用HMAC-SHA256算法，并配有多密钥轮换验证列表（网关端代码位于 `gateway/relay/auth.py`，连接器端代码位于 `src/core/relayAuthToken.ts`）。

| 通信方向 | 凭证 | 认证机制 |
|----------|------|----------|
| 网关 → 连接器WS升级请求 | 每个网关专用的密钥 | 在 `/relay` 升级请求中携带 `Authorization` 类型的Bearer头。该令牌的格式为 `base64url(payload:exp:sig)`，其中 `payload = gatewayId`，`sig = HMAC(payload:exp, secret)`。连接器会验证该令牌，若存在不匹配、缺失或已被撤销的情况，则拒绝升级请求并返回**4401错误码**。经过认证的租户信息来自连接器的存储，而非 `hello` 数据帧。 |
| 连接器 → 网关入站请求（`inbound`/`interrupt_inbound`数据帧） | 无（依托已认证的WS通道传输） | 入站请求通过网关已认证的出站套接字直接发送（参见§3），因此无需为每条消息单独签名。虽然注册或配置时仍会生成**每个租户专用的传输密钥**以保持向后兼容性，但该密钥不再用于对入站请求进行签名。 |

这就是所谓的**通道认证器**——它与平台级加密机制不同，后者的内容在中继路径上仍会被完全移除（参见§6）。网关不持有任何平台密钥；每个网关专用的密钥仅用于验证连接器之间的连接。完整的威胁模型以及注册、密钥轮换和紧急关闭机制的设计方案，请参阅 `docs/connector-gateway-auth-design.md`（连接器代码仓库）。

---

## 7. 版本控制策略

- `contract_version` 是一个整数；仅在实验阶段出现**增量式变更**时才进行版本升级（例如新增可选字段或新的操作类型）。
- 若出现破坏性变更（如字段重命名/删除、语义改变等），则需同时协调更新两个代码仓库，并相应提升版本号。
- 连接器的第一个拉取请求应注明其所基于的该文件的提交SHA值。
