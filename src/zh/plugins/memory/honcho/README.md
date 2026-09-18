# Honcho Memory Provider

这是一种专为人工智能设计的跨会话用户建模方案，具备多轮辩证推理、会话摘要生成、双向交互工具以及持久化结论存储等功能。

> **Honcho 文档：** <https://docs.honcho.dev/v3/guides/integrations/hermes>

## 前提条件

- 安装 `pip install honcho-ai`
- 拥有一个 Honcho Cloud 账户——可通过 OAuth 登录或从 [app.honcho.dev](https://app.honcho.dev) 获取的 API 密钥进行连接——或者使用自托管实例

## 设置步骤

```bash
hermes memory setup honcho   # configure Honcho directly (works on a fresh install)
hermes memory setup          # generic picker, choose Honcho from the list
```

在云环境模式下，向导会要求输入**OAuth、设备码或API密钥**。采用OAuth方式时，系统会引导用户通过浏览器登录，并自动保存授权信息——无需手动复制任何内容，令牌也会自动刷新。对于SSH或无界面机器，则请选择**设备码**模式：命令行界面会输出一段短代码以及一个链接，您只需在其他机器上的浏览器中打开该链接，完成确认即可完成设置。桌面应用程序则会在内存提供程序下拉菜单旁提供一个**连接**链接，供用户通过浏览器完成登录。

或者也可以手动操作：
```bash
hermes config set memory.provider honcho
echo "HONCHO_API_KEY=***" >> ~/.hermes/.env
```

> 使用 `hermes honcho setup` 也可以，但前提是 **在** Honcho 成为当前活跃的内存提供者之后——因为 `honcho` 子命令仅针对当前活跃的提供者生效。在全新安装的情况下，请使用 `hermes memory setup honcho`。

## 架构概览

### 双层上下文注入机制

为保留提示词缓存，上下文会在 API 调用时注入到**用户消息**中（而非系统提示语）中。只有静态模式的相关头部信息会被加入系统提示语中。注入的上下文内容会被包裹在 `<memory-context>` 标签内，并附有系统说明，明确指出其为背景数据而非新的用户输入。

该机制包含两个独立层次，各自按照不同的节奏更新：

**第一层 — 基础上下文**（每 `contextCadence` 时间间隔刷新一次）：
1. **会话摘要**——来自 `session.context(summary=True)`，置于最前端
2. **用户画像**——Honcho 对用户的动态建模结果
3. **用户信息卡片**——关键事实的快照
4. **AI 自我描述**——Honcho 对 AI 对手的建模结果
5. **AI 身份卡片**——AI 对手的相关信息

**第二层 — 辩证补充内容**（每 `dialecticCadence` 时间间隔生成一次）：
针对用户进行多轮 `.chat()` 推理，随后附加在基础上下文之后。

这两层内容会合并在一起，然后通过 `_truncate_to_budget` 函数根据 `contextTokens` 限制进行截断处理（每个标记计4个字符，且保留词边界）。

### 当前查询回溯功能（可选）

可在 `$HERMES_HOME/honcho.json` 文件中（位于根目录或 `hosts.hermes` 子目录下）将 `"recallSync"` 设置为 `true`，亦可在内存设置或 `hermes honcho setup` 中启用**当前查询召回功能**。若在主机层级明确设置为 `false`，则会覆盖根层级设定的 `true` 值。

在 `context` 模式和 `hybrid` 模式下，基础检索与辩证检索均会在推理前使用当前用户的查询内容。从会话初始化、可选的查询重写到多轮辩证处理，整个等待过程的时间上限由 `timeout`/`requestTimeout` 参数指定，若未设置该参数，则默认为 5 秒；若参数值为零、负数或非有限值，则等待时间无限制。而第一轮响应的等待设置仅适用于默认的异步模式。

当出现超时、错误、工作节点繁忙或处理节奏出现间隙时，系统会放弃再次调用，而不会重用其他查询的上下文。超时的工作节点会一直占用其对应资源直至退出，但其延迟返回的结果将被丢弃。基础检索与辩证式检索各自保持独立的处理节奏以及推理/深度设置。成功的空查询会消耗其对应的处理节奏，而失败、超时或被替代的操作则不会推进任何处理节奏。辩证式检索产生的空结果还会进一步增加现有的延迟时间。对于空查询范围内的检索，系统不会使用之前的查询缓存，也不会采用通用的用户表示形式或卡片作为替代方案。无论是会话切换、服务关闭，还是新轮次开始，正在处理中的结果都会被丢弃，即便轮次编号重复也是如此。等待截止时间并不会取消SDK的HTTP调用；已占用的工作节点资源会一直保留，直到该调用返回为止。将`injectionFrequency: "first-turn"`设置为该值仅能抑制后续的基础检索操作。每次辩证式处理都会包含当前请求，即便在禁用重写功能或查询结果为空的情况下也是如此。通用的预热检索和轮次后的自动检索功能已被关闭，但消息写入功能仍可正常运行。`tools`模式保持不变。

默认值为`false`，此设置可确保在不同轮次之间依然能够进行后台检索及缓存复用。

### 最新消息查询重写功能（可选）

当 `queryRewrite: true` 时，第一轮辩证处理会首先使用共享的 `memory_query_rewrite` 辅助任务，将最新消息转化为一个简洁的记忆检索问题。该经过重写的查询会被用于后续的辩证请求；而基础上下文检索则仍会直接使用原始消息作为搜索查询。如果重写操作超时或返回无效结果，插件将会回退到下方的现有冷启动/热启动提示语。启用此标志后，通用的辩证预热步骤将被跳过，从而避免其干扰用户的初始消息。

**默认值为关闭**——重写操作在每个辩证循环中仅触发一次辅助模型调用（而非每轮处理都调用）。请在 `hermes model` -> auxiliary models -> **Memory query rewrite** 中选择一款快速且成本低廉的模型；其在配置文件 `config.yaml` 中的请求超时时间由 `auxiliary.memory_query_rewrite.timeout` 指定（默认为 8 秒）。该任务及对应模块（`plugins/memory/query_rewrite.py`）与具体的记忆提供方无关，任何记忆提供方均可重新使用它们。此外，`dialecticCadence` 依然控制着辩证循环的运行频率。

### 冷启动提示语与热会话提示语

当无法对最新消息进行重写时，第一轮辩证处理会根据会话状态自动选择相应的回退提示语：

- **冷启动模式**（未缓存基础上下文）：“这个人是谁？他的偏好、目标及工作风格是什么？重点关注那些能帮助人工智能助手立即发挥作用的事实。”
- **热启动模式**（已存在基础上下文）：“结合本次对话中已讨论的内容，关于该用户的哪些信息与当前对话最为相关？相较于个人履历类信息，应优先考虑当前对话中的有效上下文。”

此参数不可配置，由系统自动确定。

### 辩证推理深度（多轮推理）

`dialecticDepth`（取值范围为1–3，会进行限制）用于控制每个辩证循环中触发多少次`.chat()`调用：

| 深度 | 推理轮数 | 行为说明 |
|------|----------|----------|
| 1 | 单次`.chat()`调用 | 仅发送基础查询（无论是冷启动还是热启动提示） |
| 2 | 审核与综合 | 第0轮会对结果进行自我审核；第1轮则进行针对性综合。若第0轮返回的内容信息量较大（超过300字符，或以项目符号/分段形式呈现且每段超过100字符），则可选择提前终止该轮推理 |
| 3 | 审核、综合与矛盾协调 | 第2轮会将前几轮中的矛盾点进行协调，从而形成最终的综合结果 |

### 成比例推理级别

当未设置`dialecticDepthLevels`时，每轮推理都会根据“基准”值`dialecticReasoningLevel`采用相应的成比例级别：

| 深度 | 推理级别 |
|------|----------|
| 1 | [基准级] |
| 2 | [最低级，基准级] |
| 3 | [最低级，基准级，低级] |

也可通过`dialecticDepthLevels`参数进行覆盖，即明确指定每轮推理应使用的级别字符串数组。

### 查询自适应推理级别

系统会根据查询长度自动调整辩证推理的层级：当查询长度达到或超过120个字符时，层级上升1级；达到或超过400个字符时，再上升2级，最终层级不会超过`reasoningLevelCap`的限制值（默认为“high”）。若设置`reasoningHeuristic: false`，则可强制所有自动调用的辩证推理层级固定为`dialecticReasoningLevel`。

### 三个相互独立的辩证推理控制参数

| 参数名 | 控制功能 | 数据类型 |
|--------|----------|----------|
| `dialecticCadence` | 控制触发频率——即每次启动辩证推理之间的最小间隔次数 | 整数 |
| `dialecticDepth` | 控制推理深度——每次触发时的迭代次数（1–3次） | 整数 |
| `dialecticReasoningLevel` | 控制推理强度——每次`.chat()`调用允许的推理上限 | 字符串 |

### 输入数据净化处理

在处理用户输入之前，`run_conversation`功能会先移除其中泄露的 `<memory-context>` 内容块。但如果`saveMessages`功能保存了包含这些注入内容的对话轮次，这些内容块仍可能通过消息历史记录出现在后续的对话中。该净化机制可清除 `<memory-context>` 块以及相关的系统注释。

## 工具模块

共有五种双向交互工具，所有工具均支持可选的`peer`参数（值为“user”或“ai”，默认为“user”）。

| 工具 | 是否调用LLM？ | 描述 |
|------|-----------|------|
| `honcho_profile` | 否 | 对等卡——关键信息概览 |
| `honcho_search` | 否 | 跨会话消息搜索（混合语义分析与关键词匹配，返回按相关性排序的摘录；默认长度为800个token，最大2000个） |
| `honcho_context` | 否 | 完整会话上下文：摘要、结构化表示、卡片及所有消息 |
| `honcho_reasoning` | 是 | 通过`.chat()`对话机制由LLM生成答案 |
| `honcho_conclude` | 否 | 编写、列出或删除持久性结论（列表中会显示需要删除的条目ID） |

工具的可见性取决于`recallMode`设置：在`context`模式下隐藏，而在`tools`及`hybrid`模式下始终显示。

## 配置解析规则

配置将从第一个存在的文件中读取：

| 优先级 | 路径 | 作用范围 |
|----------|------|---------|
| 1 | `$HERMES_HOME/honcho.json` | 个人配置文件专用（独立运行的Hermes实例） |
| 2 | `~/.hermes/honcho.json` | 默认配置文件（共享主机环境使用） |
| 3 | `~/.honcho/config.json` | 全局配置文件（跨应用交互使用） |

主机键由当前激活的Hermes配置文件决定：默认为`hermes`，或为`hermes_<配置文件名>`。

对于每个配置项，其解析顺序为：**主机配置 > 根目录配置 > 环境变量 > 默认值**。

## 完整配置参考文档

### 身份认证与连接设置

| 键名 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `apiKey` | 字符串 | — | API密钥。若未提供，则回退使用`HONCHO_API_KEY`环境变量。通过OAuth连接时，该字段将存储自动刷新的访问令牌。 | 
| `oauth` | 对象 | — | OAuth授权相关配置（刷新令牌、有效期、客户端信息及令牌端点）。这些配置由连接/登录流程自动生成并自动轮换，无需手动编辑。可选：仅提供API密钥也可正常使用。 | 
| `baseUrl` | 字符串 | — | 自托管Honcho服务的基地址。本地地址会自动跳过API密钥认证流程。 | 
| `environment` | 字符串 | `"production"` | SDK运行环境映射配置。 | 
| `enabled` | 布尔值 | 自动 | 主开关功能。当存在`apiKey`或`baseUrl`时，该功能将自动启用。 | 
| `workspace` | 字符串 | 主机密钥 | Honcho工作空间ID。属于共享环境——同一工作空间下的所有配置文件均可访问相同的用户身份及相关记忆数据。 | 
| `peerName` | 字符串 | — | 用户对等体身份标识。 | 
| `aiPeer` | 字符串 | 主机密钥 | AI对等体身份标识。 | 

### 身份映射（网关多用户模式）

在基于网关的部署场景中（如Telegram、Discord、Slack等），每位用户都会拥有平台自带的运行时标识（Telegram UID、Discord snowflake编号、Slack用户ID）。上述三个密钥用于控制如何将这些运行时标识映射为Honcho中的对等体身份。身份映射过程由配置文件驱动且具有确定性——不会进行自动合并或运行时推断。 |

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `pinUserPeer` | bool | `false` | 当值为 `true` 时，所有网关运行时用户都会被映射为 `peerName`。适用于希望所有平台（及其他用户）共享同一个对等端的单操作员部署场景。 |
| `userPeerAliases` | object | `{}` | 运行时 ID 与对等端 ID 的映射关系（例如 `{"7654321": "alice"}`）。推荐采用多对一的模式，即将所有运行时 ID 映射到同一个对等端名称。不支持一对一模式，一个运行时 ID 只能对应一个对等端。 |
| `runtimePeerPrefix` | string | `""` | 用于为未知的运行时 ID 添加前缀以实现命名空间隔离（例如 `"telegram_"` → `telegram_7654321`）。仅在没有匹配的别名时使用，可避免运行时 ID 形式相同的平台之间发生冲突。 |

> **已废弃**：`pinPeerName` 是 `pinUserPeer` 的旧版别名，目前仍被保留以兼容旧版本（当两者同时设置时，`pinUserPeer` 的优先级更高）。`hermes honcho setup` 会在检测到该参数时自动将其转换为 `pinUserPeer`，且不会再写入该旧格式的值。

**解析器优先级顺序**（首次匹配生效）：

```
1. pinUserPeer / pinPeerName=true → return peerName (ignore runtime ID)
2. userPeerAliases[runtime_id]   → return aliased peer
3. userPeerAliases[runtime_id_alt] → check alt-ID too (Telegram UID + username, etc.)
4. runtimePeerPrefix + runtime_id → namespaced peer, with sha256 collision escalation
5. raw sanitized runtime_id      → fallback peer
6. peerName                      → no runtime ID at all (CLI/TUI)
7. session-key fallback          → no config either
```

**为何没有 `pinAiPeer`？** 从设计上来看，AI 对端已被固定——`aiPeer` 是唯一的 AI 端身份设置，且解析器绝不会对其进行覆盖。只有用户端对端才存在运行时与配置之间的冲突，而 `pinUserPeer` 正是用于解决这一问题的。

**主机与根级的语义差异。** 这三个键在根级以及 `hosts.<host>` 子层级都是有效的，但主机级设置会优先生效。对于映射和前缀而言，主机级设置会整体替换根级值（而非合并），因此主机可以主动定义自身的身份体系，或通过 `userPeerAliases: {}` / `runtimePeerPrefix: ""` 将其清除。

**配置——网关身份树。** 当检测到已连接的网关平台时，`hermes honcho setup` 才会询问身份映射相关设置（它会检查网关配置；在非网关环境下则会跳过此步骤，因为在没有运行时用户 ID 的情况下这些键毫无作用）。执行该命令时，系统会询问“谁与这个网关通信？”，进而推导出相应的键值。

- **仅我一人** → 设置 `pinUserPeer: true`。所有非代理类型的网关用户都会被统一视为 `peerName`；此设置会覆盖所有别名，因此仅当无需为每个用户身份单独分配对应节点时才应使用该选项。适用于将 Hermes 连接到个人 Telegram/Discord 等平台的场景。如果有多个独立代理接入网关且每个代理都需要独立的节点，则不应启用此功能——请保持 `pinUserPeer: false` 的状态，并通过 `[e]` 编辑器中的 `userPeerAliases` 来进行映射。
- **我与其他人，合并处理** → 设置 `pinUserPeer: false`，并使用 `userPeerAliases` 将运行时 ID 映射到 `peerName`。所有消息将保留在共享历史记录中，而其他用户则各自拥有独立的节点。
- **我与其他人 / 仅其他人** → 设置 `pinUserPeer: false`，可选择是否设置 `runtimePeerPrefix`。每位运行时用户都将拥有独立的节点。适用于为大量人类用户提供服务的机器人。

在提示框中选择 **[e]** 即可直接设置这三个键值，而无需通过层级菜单操作。

**取消固定（从单一节点变为按用户分配）**。将 `pinUserPeer` 的值从 `true` 改为 `false` 不会迁移任何数据。在固定模式下存储在 `peerName` 下的记录仍会保留；此时运行时用户将对应到全新的、空白的节点。为确保自身对话的连贯性，建议选择**合并处理**模式——将运行时 ID 重新映射回 `peerName`，这样你的消息仍会显示在共享历史记录中，而其他用户则继续使用各自的节点。当向导检测到你正在取消固定之前已固定的配置时，会自动推荐此方案。

### 内存与回忆功能

| 键值 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `recallMode` | 字符串 | `"hybrid"` | 可选值为 `"hybrid"`（自动注入内容 + 工具）、`"context"`（仅自动注入内容，隐藏工具）以及 `"tools"`（仅使用工具，不进行内容注入）。旧版本的 `"auto"` 值已映射为 `"hybrid"` |
| `recallSync` | 布尔值 | `false` | 在 `timeout`/`requestTimeout` 时间内等待针对当前查询的自动内容回溯（若未设置或值无效，则默认为 5 秒）；忽略延迟返回或正在处理中的结果。该功能仅适用于 `context` 和 `hybrid` 模式 |
| `observationMode` | 字符串 | `"directional"` | 预设值为 `"directional"`（全部开启）或 `"unified"`（用户观察自身，AI 观察他人）。如需更精细的控制，可使用 `observation` 对象 |
| `observation` | 对象 | — | 用于配置对等方之间的观察行为（详见“观察功能”部分） |

### 写入行为

| 键值 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `writeFrequency` | 字符串/整数 | `"async"` | 可选值为 `"async"`（在后台异步写入）、`"turn"`（每轮对话同步写入）、`"session"`（在会话结束时批量写入），或整数 N（每隔 N 轮写入一次） |
| `saveMessages` | 布尔值 | `true` | 是否将对话内容持久保存至 Honcho API。若设置为 `false`，则所有自动写入操作都将被跳过——包括原始对话内容（`sync_turn`）、结论同步功能（`on_memory_write`）以及会话结束或系统关闭时的数据刷新——不过读取功能和工具调用仍可正常使用 |

### 会话处理机制 |

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `sessionStrategy` | 字符串 | `"per-directory"` | `"per-directory"`, `"per-session"`, `"per-repo"`（git 根目录）, `"global"` |
| `sessionPeerPrefix` | 布尔值 | `false` | 是否在会话键前添加对端名称 |
| `sessions` | 对象 | `{}` | 手动指定的目录与会话名称映射关系 |

#### 会话名称解析

Hermes 的会话名称决定了对话数据将存储在哪个内存桶中。解析过程遵循优先级顺序——最先匹配到的规则生效：

| 优先级 | 来源 | 示例会话名称 |
|----------|------|---------------------|
| 1 | 手动映射（`sessions` 配置） | `"myproject-main"` |
| 2 | `/title` 命令（会话进行中重命名） | `"refactor-auth"` |
| 3 | 网关会话键（Telegram、Discord 等） | `"agent-main-telegram-dm-8439114563"` |
| 4 | `per-session` 策略 | Hermes 会话 ID（`20260415_a3f2b1`） |
| 5 | `per-repo` 策略 | Git 根目录名称（`hermes-agent`） |
| 6 | `per-directory` 策略 | 当前目录的基名（`src`） |
| 7 | `global` 策略 | 工作区名称（`hermes`） |

无论 `sessionStrategy` 设置为何值，网关平台始终按优先级 3 进行解析（即实现每条聊天的独立存储）。该策略设置仅影响 CLI 会话。

如果 `sessionPeerPrefix` 设为 `true`，则会在会话键前添加对端名称：`alice-hermes-agent`。

#### 各策略的生成结果 |

- **`per-directory`** — `$PWD` 的基名。在 `~/code/myapp` 和 `~/code/other` 两个目录中分别启动 Hermes 会生成两个独立的会话；若处于同一目录，则多次运行之间会保持同一个会话。
- **`per-repo`** — git 仓库的根目录名称。同一个仓库内的所有子目录共享同一个会话；若不在 git 仓库中，则默认采用 `per-directory` 模式。
- **`per-session`** — Hermes 会话 ID（时间戳 + 十六进制字符串）。每次调用 `hermes` 命令都会启动一个全新的 Honcho 会话；若无法获取会话 ID，则默认采用 `per-directory` 模式。
- **`global`** — 工作空间名称。所有内容共享同一个会话，内存会在所有目录及多次运行中持续累积。

### 多配置文件模式

多个 Hermes 配置文件可以共享同一个工作空间，同时保持各自独立的 AI 身份。配置解析的优先级为 **主机块 > 根块 > 环境变量 > 默认值**——主机块会继承根块的设置，因此共享的配置只需声明一次即可：

```json
{
  "apiKey": "***",
  "workspace": "hermes",
  "peerName": "yourname",
  "hosts": {
    "hermes": {
      "aiPeer": "hermes",
      "recallMode": "hybrid",
      "sessionStrategy": "per-directory"
    },
    "hermes_coder": {
      "aiPeer": "coder",
      "recallMode": "tools",
      "sessionStrategy": "per-repo"
    }
  }
}
```

在同一个共享环境（`hermes`）中，这两种配置文件都会看到相同的用户（`yourname`），但每个 AI 对等体都会独立形成自身的观察结果、结论以及行为模式。编码者的记忆侧重于代码相关内容，而主智能体的记忆则更为广泛。

主机密钥源自当前激活的 Hermes 配置文件：默认为 `hermes`，或是 `hermes_<profile>` 格式（例如 `hermes -p coder` 生成的主机密钥为 `hermes_coder`）。为保持兼容性，系统仍会读取旧版本的 `hermes.<profile>` 格式主机配置块；而当 CLI 写入针对特定配置文件的 Honcho 配置时，这些旧配置将会被迁移替换。

### 辩证推理

| 键值 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `dialecticDepth` | int | `1` | 每个辩证循环的迭代次数（范围为1–3，会进行限制）。1表示单次查询，2表示审核+综合分析，3表示审核+综合分析+对齐处理 |
| `dialecticDepthLevels` | array | — | 可选的数组，用于指定每次迭代的推理层级字符串。该参数可覆盖按比例计算的默认值。示例：`["minimal", "low", "medium"]` |
| `dialecticReasoningLevel` | string | `"low"` | `.chat()`函数的基础推理层级：`"minimal"`、`"low"`、`"medium"`、`"high"`、`"max"` |
| `dialecticDynamic` | bool | `true` | 当该参数为`true`时，模型可通过`honcho_reasoning`工具在每次调用时覆盖推理层级。当为`false`时，则始终使用`dialecticReasoningLevel`指定的层级 |
| `dialecticMaxChars` | int | `600` | 自动注入的辩证补充内容的最大字符数。此限制仅适用于自动注入的内容——通过`honcho_reasoning`工具明确生成的输出将完整返回 |
| `dialecticMaxInputChars` | int | `10000` | 传递给`.chat()`函数的辩证查询输入的最大字符数。Honcho云服务的上限也为10k |
| `reasoningHeuristic` | bool | `true` | 根据查询内容动态调整：会根据查询长度自动提升自动注入的辩证内容的层级（查询长度≥120字符时层级+1，≥400字符时层级+2），最终层级不会超过`reasoningLevelCap`设定的上限。当该参数为`false`时，所有自动调用都将固定使用`dialecticReasoningLevel`指定的层级 |
| `reasoningLevelCap` | string | `"high"` | `reasoningHeuristic`动态调整机制的上限值：`"minimal"`、`"low"`、`"medium"`、`"high"`、`"max"` |

### 令牌预算

| 键名 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `contextTokens` | int | SDK默认值 | 用于`context()` API调用的令牌预算。同时用于控制预取内容的截断长度（令牌数 × 4个字符） |
| `messageMaxChars` | int | `25000` | 通过`add_messages()`发送的每条消息的最大字符数。超过此限制将触发分块处理，并添加`[continued]`标记。Honcho云服务的上限也为25,000字符 |

### 节奏控制（成本管理）

| 键名 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `contextCadence` | int | `1` | 基础上下文刷新之间的最小轮次间隔（包括会话摘要、模型表示及卡片信息） |
| `dialecticCadence` | int | `1` | 对话式`.chat()`调用之间的最小轮次间隔 |
| `injectionFrequency` | string | `"every-turn"` | 可设置为`"every-turn"`或`"first-turn"`：前者在用户的每一条消息都会注入基础上下文；后者仅在第一条消息时注入，而对话式补充内容则保持其自身的节奏 |
| `queryRewrite` | bool | `false` | 在进行对话式处理之前，将最新消息重写为检索查询（每轮次会多调用一次辅助LLM） |
| `firstTurnBaseWait` | float | `3.0` | 第一轮等待基础上下文/会话初始化的最长时间。设置为`0`则取消等待（完全异步处理；上下文会在后续轮次中提供）。第2轮及以后的轮次不会因初始化延迟而等待 |
| `firstTurnDialecticWait` | float | `2.0` | 第一轮等待对话式处理结果的最长时间。设置为`0`则取消等待 |

### 观测功能（精细控制）

该配置与Honcho的每对端`SessionPeerConfig`实现了一一对应关系。当该配置存在时，将覆盖`observationMode`预设值。

```json
"observation": {
  "user": { "observeMe": true, "observeOthers": true },
  "ai":   { "observeMe": true, "observeOthers": true }
}
```

| 字段 | 默认值 | 描述 |
|-------|---------|-------------|
| `user.observeMe` | `true` | 用户端自我观察（Honcho 用于构建用户画像） |
| `user.observeOthers` | `true` | 用户端观察 AI 发送的消息 |
| `ai.observeMe` | `true` | AI 端自我观察（Honcho 用于构建 AI 画像） |
| `ai.observeOthers` | `true` | AI 端观察用户发送的消息（支持跨端对话交互） |

预设值：
- `"directional"`（默认）：四个值均为 `true`
- `"unified"`：用户端 `observeMe=true`，AI 端 `observeOthers=true`，其余值为 `false`

### 固定限制

| 限制项 | 值 |
|-------|-----|
| 搜索工具最大token数 | 2000（上限），800（默认值） |
| 获取对方信息所需token数 | 200 |

## 环境变量

| 变量 | 替代值 |
|----------|--------|
| `HONCHO_API_KEY` | `apiKey` |
| `HONCHO_BASE_URL` | `baseUrl` |
| `HONCHO_ENVIRONMENT` | `environment` |
| `HERMES_HONCHO_HOST` | 主机地址覆盖值 |
| `HONCHO_OAUTH_DASHBOARD` | OAuth授权地址（默认为云端控制台；本地开发环境为 `localhost:3000`） |
| `HONCHO_OAUTH_AUTHORIZE_URL` | 完整的授权URL（可覆盖控制台指定的地址） |
| `HONCHO_OAUTH_TOKEN_URL` | Token获取接口地址（默认为云端API；本地开发环境为 `localhost:8000`） |
| `HONCHO_OAUTH_DEVICE_AUTH_URL` | 设备授权接口地址（默认由Token URL推导得出） |
| `HONCHO_OAUTH_CLIENT_ID` | OAuth客户端标识（默认为 `hermes-agent`） |
| `HONCHO_OAUTH_SCOPE` | 请求的权限范围（默认为 `write`） |

## CLI命令

| 命令 | 描述 |
|---------|-------------|
| `hermes memory setup honcho` | 直接配置 Honcho — 适用于全新安装环境 |
| `hermes honcho setup` | 交互式设置向导（仅当 Honcho 成为默认提供者后需注册一次；随后会跳转至 `hermes memory setup`） |
| `hermes honcho status` | 显示当前激活配置文件的已解析配置 |
| `hermes honcho enable` / `disable` | 切换当前激活配置文件中对 Honcho 的启用/禁用状态 |
| `hermes honcho mode <mode>` | 更改回忆模式或观察模式 |
| `hermes honcho peer --user <name>` | 更新用户端点名称 |
| `hermes honcho peer --ai <name>` | 更新 AI 端点名称 |
| `hermes honcho tokens --context <N>` | 设置上下文令牌预算 |
| `hermes honcho tokens --dialectic <N>` | 设置辩证法最大字符数 |
| `hermes honcho map <name>` | 将当前目录映射为会话名称 |
| `hermes honcho sync` | 为所有 Hermes 配置文件创建主机块 |

## 示例配置

```json
{
  "apiKey": "***",
  "workspace": "hermes",
  "peerName": "username",
  "contextCadence": 2,
  "dialecticCadence": 3,
  "dialecticDepth": 2,
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "recallMode": "hybrid",
      "observation": {
        "user": { "observeMe": true, "observeOthers": true },
        "ai": { "observeMe": true, "observeOthers": true }
      },
      "writeFrequency": "async",
      "sessionStrategy": "per-directory",
      "dialecticReasoningLevel": "low",
      "dialecticDepth": 2,
      "dialecticMaxChars": 600,
      "saveMessages": true
    },
    "hermes_coder": {
      "enabled": true,
      "aiPeer": "coder",
      "sessionStrategy": "per-repo",
      "dialecticDepth": 1,
      "dialecticDepthLevels": ["low"],
      "observation": {
        "user": { "observeMe": true, "observeOthers": false },
        "ai": { "observeMe": true, "observeOthers": true }
      }
    }
  },
  "sessions": {
    "/home/user/myproject": "myproject-main"
  }
}
```
