# A2A平台插件——设计说明

该方案将整个A2A（智能体间交互）功能模块（#514及相关任务）整合为**一个插件**，且**无需对核心代码进行任何修改**，完全基于现有代码库已提供的功能实现。该插件遵循**A2A协议v1.0**标准（基于JSON-RPC接口）。

## 为何选择插件而非直接添加核心功能

早期的A2A相关尝试（#4135、#4948、#4952、#11025）是通过新增独立的服务器包（`a2a_adapter/`）以及/或修改`gateway/run.py`和`gateway/config.py`文件来实现的。此后，代码库又新增了`ctx.register_platform()`函数（用于插件与平台适配器之间的交互，被irc、line、teams、ntfy、simplex等工具使用）以及`ctx.register_tool()`函数。正因如此，才确立了以下原则：**插件绝不能修改核心文件**。目前，A2A功能全部集中在`plugins/platforms/a2a/`目录下。

## 两种实现方向

### 出发方向——客户端工具（`a2a`工具集）
- `a2a_discover(url)` — 获取并汇总对端 Agent Card 的信息（v1.0版本，支持`supportedInterfaces`参数，最多可处理0.3张Card）。  
- `a2a_call(agent, message, context_id?)` — 向对端发送JSON-RPC格式的`message/send`请求，并返回回复。可通过`context_id`实现多轮对话（该参数按v1.0规范嵌入消息中）。该方法会设置`TASK_STATE_INPUT_REQUIRED`状态，提示模型需要回复并延续对话上下文。  
- `a2a_list()` — 显示已配置的对端、已保存的对话记录以及相关指标。  
- `a2a_history(context_id, limit?)` — 检索已保存的对话记录（该功能为持久化层在正式环境中的调用接口）。  
- `a2a_orchestrate(capability, message, mode?)` — 将任务分发至所有具备相应能力的已配置对端。支持三种模式：`all`（接收所有回复）、`first`（获取首个成功回复）、`best`（选择最长有效回复时间——这是一种较为粗略的策略；错误回复不会被选中，全错误情况下会直接报告所有失败情况而非挑选一个）。  

对端信息可从`config.yaml`文件中的`a2a_agents`字段获取，或直接通过URL指定。  

### 接入端 — 平台适配层  
- 使用标准库的`http.server`在后台线程中运行（在`register()`阶段无需使用asyncio循环，从而避免了在某些分支版本中因“在循环外部注册”导致的a2a_fleet功能故障，该故障曾导致接入服务无法正常工作）。请求处理器为模块级类`A2ARequestHandler`，可通过`server.adapter`访问；因此无需依赖HTTP环境即可对RPC处理器进行单元测试。
- 通过 `GET /.well-known/agent-card.json` 获取 Agent 卡片（标准路径为 v1.0；旧的 `agent.json` 也能提供该信息）（v1.0 版本包含 `supportedInterfaces[]`、`provider` 以及 `capabilities.extendedAgentCard` 字段）。**动态生成**：技能信息会在服务端启动时根据实时工具注册表动态构建（`A2A_ADVERTISED_TOOLSETS` 和 `extra.advertised_toolsets` 可用于限制可用技能）。
- JSON-RPC 方法包括：`message/send`、`message/stream`（SSE 协议）、`tasks/get`、`tasks/list`、`tasks/cancel`、`tasks/subscribe`，以及 `tasks/pushNotificationConfig/create`（也支持旧的 `set` 命名方式）。
- **实时会话注入机制（源自 #11025 号建议）**：传入的任务会通过常规的 `MessageEvent` → `handle_message` 处理路径进行路由，该路径以 A2A `contextId` 作为标识，因此处理任务的智能体即为正在服务用户的同一智能体——能够访问完整的内存和上下文信息，而非副本。回复内容则通过 `adapter.send()` 返回，该机制会处理 HTTP 请求所阻塞的每个**任务**对应的待处理 `Future` 对象（采用基于上下文的 FIFO 顺序，因此同一上下文下的并发请求无法相互干扰）；`on_processing_complete` 事件可及时处理失败或取消的情况。
- **任务存储机制**：所有任务（包括终端任务，最多保留最近 500 个）均可通过 `tasks/get` 和 `tasks/list` 进行查询，而 `tasks/subscribe` 则可通过存储监视器重新连接到正在运行的任务的流中。如果监视器失效，超过 5 分钟未处理的任务将被标记为孤立状态（该机制具备幂等性，不会在指标统计中造成重复计数）。
- **需要输入信息**：当平台提示代理需要进一步确认信息时，会要求其以 `[INPUT_REQUIRED]` 作为回复的开头；适配器会将此指令转换为 `TASK_STATE_INPUT_REQUIRED` 状态，并将相关问题放入 `status.message` 中。  
- **推送通知**：配置既可通过 `message/send` 方法直接传入（字段为 `configuration.taskPushNotificationConfig`），也可通过创建接口设置（该方法会返回 `configId` 和 `createdAt`）。在终端切换时，回调函数会收到经过 HMAC-SHA256 签名的 v1.0 版本 `StreamResponse`（类型为 `statusUpdate`），签名字段为 `X-A2A-Signature`，密钥为 `A2A_PUSH_SECRET`，若该密钥不可用则会使用承载令牌；同时，回调 URL 还会经过 SSRF 防护处理。  

## v1.0 接口数据格式说明
- 任务状态/角色采用全大写蛇形命名法（TASK_STATE_*、ROLE_*）。  
- 各部分元素均支持成员在线状态识别，不存在“kind”字段。系统支持三种类型的元素：文本型（text + mediaType）、文件型（url|raw + 文件名 + mediaType）以及数据型（data + mediaType）。extract_text功能会将文件型/数据型元素转换为文本流形式呈现给智能体——文件型以URL+文件名为格式，数据型则以JSON格式呈现；同时该功能也兼容旧版本系统中使用的v0.3版“kind”字段及v0.3之前的“type”字段格式。输出回复仍为纯文本形式，因为智能体仅能生成文本，而文件型/数据型元素则用于丰富输入内容。  
- 推送通知配置支持完整的CRUD操作：创建（可通过消息内嵌方式、通过configuration.taskPushNotificationConfig参数，或通过create方法实现）、获取、列表查询及删除。每项配置均包含configId和createdAt字段。每个任务对应一个配置项（v1.0版本允许多个配置，但当前版本仅保留一个）。  
- SSE事件为StreamResponse对象，其成员包括statusUpdate和artifactUpdate；当流关闭时即表示任务已进入最终状态，此时不会包含final字段。  
- contextId信息存储在消息内部（旧版系统允许将其作为顶层字段接收）。  
- 时间戳采用ISO 8601格式，精度达毫秒级；任务对象会包含createdAt和lastModified字段。  
- 错误代码：仅允许使用A2A标准预留的错误代码，并且必须遵循其规定的含义（如`-32001`表示任务未找到，`-32002`表示任务无法取消）；自定义错误代码则位于`-32050..-32052`范围内，分别对应未授权、速率限制及来源不可信等场景。  

## 安全性（默认处于开启状态）
- **绑定安全机制**：若未配置令牌（`A2A_BEARER_TOKEN` 或 `A2A_PEER_TOKENS`），则仅允许绑定 `127.0.0.1`。单独的令牌无法扩大绑定范围；若需允许远程访问，必须同时提供令牌以及明确的 `A2A_HOST`。
- **对等方身份识别**：当设置 `A2A_PEER_TOKENS="alice:tok1,bob:tok2"` 时，每个对等方都将拥有独立的认证凭证；用于速率限制、信任校验、消息格式化及审计的认证身份即为对应的名称。若使用共享的 `A2A_BEARER_TOKEN`，则认证身份为 `ip:<addr>`。请求正文中任何内容均无法用于声明身份，且所有身份比对均为恒定时间复杂度。
- **信任校验机制**：通过 `A2A_TRUSTED_PEERS`（或配置项 `a2a.trusted_peers`），可可选地限制哪些已认证的身份有权执行任务。
- **注入过滤功能**：所有传入的文本内容（包括以 `/` 开头的指令——因为远程对等方根本无法访问操作员专用斜杠命令）都会被进行脱毒处理（如 ChatML、角色前缀及覆盖模式会被替换为 `[filtered]`），同时会添加隐私前缀，标明其为来自不可信对等方的输入。
- **输出内容过滤**：在任何数据发送之前，会先删除那些可能包含敏感凭证的字符串（如 `sk-…`、`ghp_…`、JWT、承载令牌及电子邮件地址）。
- **速率限制机制**：针对每个已认证的身份，采用滑动窗口算法进行限制（单位为分钟，由 `A2A_RATE_LIMIT` 指定）。
- **防止循环机制**：通过设置每个上下文中的轮次上限（`A2A_MAX_PINGPONG_TURNS`，默认值为 5，最大值为 20），可阻止代理之间出现无止境的来回通信循环（在 v1.0 版本中会以 `TASK_STATE_REJECTED` 的形式拒绝此类请求）；调用 `tasks/cancel` 可重置该任务上下文中的计数器。
- **审计日志**：系统会为每一次交互生成只读的 `~/.hermes/a2a_audit.jsonl` 日志文件，用于记录所有操作痕迹。
## 状态存储位置
任务存储、对话跟踪器以及速率限制器均为**适配器实例**对象（位于 `protocol.py` 文件中）。而指标计数器则采用模块单例模式，因为它需要在入站适配器与出站客户端工具之间进行共享（`/metrics` 和 `a2a_list` 功能均支持双向数据统计）。

## 持久性存储（可抵御数据压缩）
A2A 对话内容会被保存在 `~/.hermes/a2a_conversations/<context>.jsonl` 文件中，该路径位于对话数据压缩处理流程之外——因此即使进行数据压缩或服务重启，这些对话记录也不会丢失（这正是需求 #11025 的要求）。`a2a_history` 工具可通过上下文标识来检索这些对话记录。

## 与集群相关的需求

| 来源编号 | 需求内容 | 实现位置 |
|---|---|---|
| #514, #23871, #4135 | 智能体卡片发现功能 | `protocol.build_agent_card`、适配器 GET 接口 |
| #4135, #14559, #8948 | 客户端：发现智能体/调用智能体/列出智能体 | `tools.py` 文件 |
| #11025 | 实时会话注入功能（非克隆方式） | `adapter._prepare_task` 方法 |
| #11025 | 隐私过滤、输出内容屏蔽及审计功能 | `security.py` 文件 |
| #11025 | 在数据压缩流程之外保存对话记录 | `protocol.persist_message`、`a2a_history` 函数 |
| #514, #11025 | 认证功能及本地主机默认设置 | `security.authenticate`、`resolve_bind_host` 函数 |
| #56434 | 可信对等方审批机制 | `security.is_trusted_peer` 函数 |
| #56435 | 任务完成通知功能 | 推送通知功能（`_send_push_notification` 方法） |
| #25176, #689 | 不同机器之间的智能体间消息传递 | 客户端工具及入站适配器 |
| #7517 及其他相关需求 | 多对等方协同调度功能 | `a2a_orchestrate` 函数 |
## 故意排除在当前版本范围之外（未来计划，非本次迭代内容）
- **a2a-sdk / gRPC + HTTP+JSON 接口绑定。** 目前仅提供 JSONRPC 接口绑定，相关文档中也明确说明了这一点。
- **`tenant` 字段、扩展型 Agent Card 以及 `stateTransitionHistory` 功能。**
- **真正的任务中止功能：** 虽然 `tasks/cancel` 命令可标记任务已取消并停止响应，但无法中止当前正在进行的会话轮次。
- **DID / Ed25519 身份认证、OAuth2 权限范围以及 x402 微支付功能**（#14559 bindu）——这些功能较为复杂且适用场景有限，只有在实际需求出现时才会重新考虑加入。

## 文件列表
```
plugins/platforms/a2a/
├── plugin.yaml      # manifest (kind: platform)
├── __init__.py      # register(): platform adapter + client tools
├── adapter.py       # inbound A2A v1.0 server (stdlib http.server)
├── tools.py         # outbound client tools
├── protocol.py      # Agent Card, JSON-RPC framing, task store, persistence
├── security.py      # auth/identity, injection filters, redaction, audit
├── DESIGN.md
└── README.md
```
