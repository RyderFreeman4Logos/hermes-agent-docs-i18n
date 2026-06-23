# Honcho Memory Provider

这是一种专为人工智能设计的跨会话用户建模方案，具备多轮辩证推理、会话摘要生成、双向交互工具以及持久化结论存储等功能。

> **Honcho文档：** <https://docs.honcho.dev/v3/guides/integrations/hermes>

## 前提条件

- 安装 `pip install honcho-ai`
- 拥有一个Honcho Cloud账户——可通过OAuth登录或使用来自 [app.honcho.dev](https://app.honcho.dev) 的API密钥进行连接——或者使用自托管实例

## 设置步骤

```bash
hermes memory setup honcho   # configure Honcho directly (works on a fresh install)
hermes memory setup          # generic picker, choose Honcho from the list
```

在云环境模式下，向导会询问您需要使用**OAuth授权**还是**API密钥**。采用OAuth方式时，系统会引导您通过浏览器登录，并自动保存授权信息——无需手动复制任何内容，且令牌会自动刷新。桌面应用则会在内存提供方下拉菜单旁提供一个**连接**链接，实现相同的操作流程。

或者也可以手动操作：
```bash
hermes config set memory.provider honcho
echo "HONCHO_API_KEY=***" >> ~/.hermes/.env
```

> 使用 `hermes honcho setup` 也可以，但必须在 Honcho 成为当前活跃的内存提供者之后才能使用——因为 `honcho` 子命令仅针对当前活跃的提供者注册。在全新安装时，请使用 `hermes memory setup honcho`。

## 架构概览

### 双层上下文注入机制

为保留提示词缓存，上下文会在 API 调用时注入到**用户消息**中（而非系统提示语）中。只有静态模式头部信息会被放入系统提示语中。注入的上下文块会被包裹在 `<memory-context>` 标签中，并附有系统说明，表明其为背景数据而非新的用户输入。

该机制包含两个独立层级，各自按照不同的节奏更新：

**第一层——基础上下文**（每 `contextCadence` 次刷新）：
1. **会话摘要**——来自 `session.context(summary=True)`，置于最前端
2. **用户画像**——Honcho 对用户的动态建模结果
3. **用户信息卡片**——关键事实的快照
4. **AI 对手画像**——Honcho 对 AI 对手的建模结果
5. **AI 身份卡**——AI 对手的相关事实

**第二层——辩证补充内容**（每 `dialecticCadence` 次触发）：
通过对用户进行多轮 `.chat()` 推理，将结果附加在基础上下文之后。

这两层内容会合并在一起，随后通过 `_truncate_to_budget` 函数根据 `contextTokens` 限制进行截断处理（按字符数计算，每字符4个单位，且不会破坏词边界）。

### 冷启动会话提示语与热会话提示语的区别

辩证推理的第0轮会自动根据会话状态选择对应的提示语：

- **冷启动状态**（未缓存基础上下文）： “这个人是谁？他们的偏好、目标和工作风格是什么？请提供有助于 AI 助手立即发挥作用的事实信息。”
- **热会话状态**（已存在基础上下文）： “结合本次会话中已讨论的内容，哪些关于该用户的背景信息与当前对话最为相关？请优先考虑当前相关的上下文，而非仅介绍个人履历。”

此设置不可配置，由系统自动决定。

### 辩证推理深度（多轮推理机制）

`dialecticDepth` 参数（取值范围为1–3，会进行限制）用于控制每个辩证周期内触发多少次 `.chat()` 调用：

| 深度 | 循环次数 | 行为特点 |
|------|----------|----------|
| 1 | 单次 `.chat()` 调用 | 仅执行基础查询（无论处于冷启动还是热会话状态） |
| 2 | 审核 + 综合 | 第0轮的结果会先经过自我审核，第1轮则进行针对性综合。如果第0轮返回的信息量较大（超过300字符，或以项目符号/分节形式呈现且长度超过100字符），则会自动跳过此轮 |
| 3 | 审核 + 综合 + 协调 | 第2轮会协调前几轮中的矛盾点，最终形成综合结果 |

### 比例式推理层级

当未设置 `dialecticDepthLevels` 时，每轮推理的复杂度会根据 `dialecticReasoningLevel`（即“基础”层级）按比例确定：

| 深度 | 各轮对应的推理层级 |
|------|-------------------|
| 1 | [基础] |
| 2 | [最低级, 基础级] |
| 3 | [最低级, 基础级, 低级] |

可通过 `dialecticDepthLevels` 参数进行覆盖，即明确指定每轮对应的推理层级字符串数组。

### 根据查询长度自适应调整的推理层级

系统会依据查询长度自动调整辩证推理的复杂度：当查询长度≥120字符时提升1个层级，≥400字符时再提升1个层级，最终层级不会超过 `reasoningLevelCap` 的限制（默认值为“高级”）。若设置 `reasoningHeuristic: false`，则可强制所有自动调用的推理层级固定为 `dialecticReasoningLevel`。

### 三个相互独立的辩证控制参数

| 参数名 | 控制内容 | 类型 |
|--------|----------|------|
| `dialecticCadence` | 触发频率——两次辩证推理之间的最小轮次间隔 | 整数 |
| `dialecticDepth` | 循环次数——每次触发时进行的推理轮数（1–3） | 整数 |
| `dialecticReasoningLevel` | 推理强度——每次 `.chat()` 调用的最大推理复杂度 | 字符串 |

### 输入内容净化处理

`run_conversation` 函数会在处理用户输入之前，先移除其中泄露的 `<memory-context>` 块。如果 `saveMessages` 功能将包含注入上下文的对话轮次保存下来，这些上下文块可能会通过消息历史记录再次出现在后续对话中。净化函数会同时移除 `<memory-context>` 块及其相关的系统说明文字。

## 工具类

共有五种双向交互工具，所有工具都支持可选的 `peer` 参数（取值为 `"user"` 或 `"ai"`，默认为 `"user"`）。

| 工具名称 | 是否调用 LLM？ | 功能描述 |
|----------|--------------|----------|
| `honcho_profile` | 否 | 生成用户信息卡片——即关键事实的快照 |
| `honcho_search` | 否 | 对已存储的上下文进行语义搜索（默认搜索长度为800个token，最大为2000个token） |
| `honcho_context` | 否 | 提供完整的会话上下文：包括摘要、用户画像、信息卡片以及所有对话记录 |
| `honcho_reasoning` | 是 | 通过多轮辩证式的 `.chat()` 调用，由 LLM 生成综合答案 |
| `honcho_conclude` | 否 | 写入关于该用户的永久性事实或结论 |

工具的可见性取决于 `recallMode` 参数：在 `context` 模式下这些工具不可见，而在 `tools` 模式和 `hybrid` 模式下始终可见。

## 配置文件解析规则

系统会按顺序读取第一个存在的配置文件：

| 优先级 | 文件路径 | 适用范围 |
|--------|----------|----------|
| 1 | `$HERMES_HOME/honcho.json` | 仅适用于特定配置文件的独立 Hermes 实例 |
| 2 | `~/.hermes/honcho.json` | 默认配置文件，适用于共享主机环境 |
| 3 | `~/.honcho/config.json` | 全局配置文件，适用于跨应用交互场景 |

主机标识符是根据当前激活的 Hermes 配置文件确定的：默认为 `hermes`，或者为 `hermes_<profile>` 的形式。

对于每个配置键，其解析顺序为：**主机配置块 > 根级配置 > 环境变量值 > 默认值**。

## 完整配置参考文档

### 身份与连接设置

| 键名 | 类型 | 默认值 | 功能描述 |
|------|------|---------|----------|
| `apiKey` | 字符串 | — | API 密钥。若未提供，则会回退使用 `HONCHO_API_KEY` 环境变量中的值。通过 OAuth 连接时，该字段将存储自动刷新的访问令牌 |
| `oauth` | 对象 | — | 包含 OAuth 授权相关信息（如刷新令牌、过期时间、客户端信息以及令牌获取端点）。这些信息由连接/登录流程自动生成并自动轮换，无需手动修改。注意：即使不设置此参数，仅使用 API 密钥也能正常工作 |
| `baseUrl` | 字符串 | — | 自托管 Honcho 服务的基地址。如果输入的是本地路径，则无需进行 API 密钥验证 |
| `environment` | 字符串 | `"production"` | SDK 环境映射标识 |
| `enabled` | 布尔值 | 自动判断 | 总开关。只要存在 `apiKey` 或 `baseUrl`，该选项就会自动设置为开启状态 |
| `workspace` | 字符串 | 主机标识符 | Honcho 工作空间 ID。所有处于同一工作空间中的配置文件可以共享相同的用户身份及相关记忆信息 |
| `peerName` | 字符串 | — | 用户侧的对手标识 |
| `aiPeer` | 字符串 | 主机标识符 | AI 对手侧的标识 |

### 身份映射（网关多用户场景）

在基于网关的部署环境中（如 Telegram、Discord、Slack 等平台），每个用户都会拥有该平台自带的运行时 ID（如 Telegram 的 UID、Discord 的 snowflake ID、Slack 的用户 ID）。上述三个键用于控制如何将这些运行时 ID 映射到 Honcho 中的用户对象。映射规则由配置文件决定，且具有确定性——系统不会自动合并不同平台的用户信息，也不会根据运行时 ID 进行推断。

| 键名 | 类型 | 默认值 | 功能描述 |
|------|------|---------|----------|
| `pinUserPeer` | 布尔值 | `false` | 当该参数设置为 `true` 时，所有通过网关接入的用户都会被统一映射到 `peerName` 所指定的用户对象。适用于需要让所有平台用户以及其他用户共享同一个对手对象的单一操作员部署场景 |
| `userPeerAliases` | 对象 | `{}` | 用于将运行时 ID 映射到对应用户对象的映射表（格式为 `{"7654321": "alice"}`）。推荐的使用模式是一对多关系，即将所有运行时 ID 都映射到同一个用户对象名称。系统不支持一对一映射关系——每个运行时 ID 只能对应一个用户对象 |
| `runtimePeerPrefix` | 字符串 | `""` | 用于为那些没有匹配到别名的运行时 ID 前缀加上特定前缀，以实现命名空间隔离（例如添加前缀 `"telegram_"` 后，ID `7654321` 将变为 `telegram_7654321`）。此参数仅在无法通过别名匹配时使用，旨在避免那些运行时 ID 结构相似的不同平台之间出现冲突 |

> **已废弃**：`pinPeerName` 是 `pinUserPeer` 的旧名称，目前仍会被读取以保持向后兼容性（当两个参数同时设置时，`pinUserPeer` 的优先级更高）。`hermes honcho setup` 工具在首次使用时会将该参数的值自动转换为 `pinUserPeer`，并且之后不会再写入任何相关数据。

**解析优先级顺序**：首先匹配到的配置项即生效。

```
1. pinUserPeer / pinPeerName=true → return peerName (ignore runtime ID)
2. userPeerAliases[runtime_id]   → return aliased peer
3. userPeerAliases[runtime_id_alt] → check alt-ID too (Telegram UID + username, etc.)
4. runtimePeerPrefix + runtime_id → namespaced peer, with sha256 collision escalation
5. raw sanitized runtime_id      → fallback peer
6. peerName                      → no runtime ID at all (CLI/TUI)
7. session-key fallback          → no config either
```

**为何没有 `pinAiPeer`？** 从设计上来看，AI 对端本身就是固定绑定的——`aiPeer` 是唯一的 AI 端身份设置，且解析器绝不会覆盖它。只有用户端对端才存在运行时与配置之间的冲突，而 `pinUserPeer` 正是用于解决这类冲突的。

**主机与根级的语义区别。** 这三个键在根级以及 `hosts.<host>` 子层级都是有效的，但主机级设置会优先生效。对于映射表和前缀而言，主机级设置会整体替换根级值（而非合并），因此用户可以主动定义自己的身份空间，或通过 `userPeerAliases: {}` / `runtimePeerPrefix: ""` 将其清空。

**配置——网关身份树结构。** 当检测到已连接的网关平台时，`hermes honcho setup` 才会询问身份映射相关问题（它会检查网关配置；在非网关环境下此步骤会被跳过，因为没有运行时用户 ID，这些键将不起作用）。执行该命令时，系统会询问“谁与这个网关交互？”，并据此生成相应键值：
- **仅我一人** → `pinUserPeer: true`。所有非智能体类型的网关用户都会被简化为 `peerName`；此固定绑定会覆盖所有别名，因此仅当不需要为每个用户端身份单独设置对端时才选择此选项。适用于将 Hermes 连接到个人 Telegram/Discord 等平台的场景。如果有多个智能体访问同一个网关，且每个都需要独立的对端，则不要使用固定绑定——保持 `pinUserPeer: false`，并通过 `[e]` 编辑器通过 `userPeerAliases` 进行映射。
- **我与其他人，合并处理** → `pinUserPeer: false`，并结合 `userPeerAliases` 将运行时 ID 映射到 `peerName`。所有交互将记录在共享的历史记录中，其他用户则拥有各自的独立对端。
- **我与其他人/仅其他人** → `pinUserPeer: false`，可选设置 `runtimePeerPrefix`。每个运行时用户都会拥有独立的对端。适用于为多名人类用户提供服务的机器人。

在提示界面选择 **[e]** 即可直接设置这三个键，而无需依次配置整个树结构。

**取消固定绑定（从全局 → 每用户独立）。** 将 `pinUserPeer` 的值从 `true` 改为 `false` 不会迁移任何数据。在固定绑定状态下存储在 `peerName` 下的记忆会保留原样；此时运行时用户将对应到全新的、空的对端。为保持自身对话的连贯性，建议选择“合并处理”路径——将运行时 ID 重新映射回 `peerName`，这样你的发言仍会记录在共享历史中，而其他用户则拥有独立对端。当检测到你要取消对已固定绑定的配置文件的绑定时，向导会自动提供此建议。

### 记忆与回忆功能

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `recallMode` | 字符串 | `"hybrid"` | `"hybrid"`（自动注入 + 工具），`"context"`（仅自动注入，隐藏工具），`"tools"`（仅工具，无自动注入）。旧版本的 `"auto"` 已被替换为 `"hybrid"` |
| `observationMode` | 字符串 | `"directional"` | 预设值为 `"directional"`（全部开启）或 `"unified"`（用户观察自身，AI观察他人）。如需更精细的控制，可使用 `observation` 对象 |
| `observation` | 对象 | — | 每个对端的观察配置（详见“观察功能”部分） |

### 写入行为设置

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `writeFrequency` | 字符串/整数 | `"async"` | `"async"`（后台异步写入），`"turn"`（每轮对话同步写入），`"session"`（会话结束时批量写入），或整数 N（每 N 轮写入一次） |
| `saveMessages` | 布尔值 | `true` | 是否将消息持久保存到 Honcho API 中 |

### 会话解析规则

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `sessionStrategy` | 字符串 | `"per-directory"` | `"per-directory"`（按目录）、`"per-session"`（按会话）、`"per-repo"`（按 Git 根目录）、`"global"`（全局） |
| `sessionPeerPrefix` | 布尔值 | `false` | 是否在会话键前添加对端名称前缀 |
| `sessions` | 对象 | `{}` | 手动定义的目录与会话名称之间的映射关系 |

#### 会话名称解析方式

Honcho 的会话名称决定了对话记忆将存储到哪个对应的存储桶中。解析遵循优先级顺序——首先匹配到的规则生效：

| 优先级 | 来源 | 示例会话名称 |
|----------|------|---------------------|
| 1 | 手动映射（`sessions` 配置） | `"myproject-main"` |
| 2 | `/title` 命令（会话进行中重命名） | `"refactor-auth"` |
| 3 | 网关会话键（Telegram、Discord 等） | `"agent-main-telegram-dm-8439114563"` |
| 4 | `per-session` 策略 | Hermes 会话 ID（如 `20260415_a3f2b1`） |
| 5 | `per-repo` 策略 | Git 根目录名称（如 `hermes-agent`） |
| 6 | `per-directory` 策略 | 当前目录的基名（如 `src`） |
| 7 | `global` 策略 | 工作空间名称（如 `hermes`） |

无论 `sessionStrategy` 设置为何，网关平台始终优先按第 3 种方式解析（即每个聊天独立存储），该策略设置仅影响 CLI 会话。

如果 `sessionPeerPrefix` 设为 `true`，则会在会话键前添加对端名称前缀，格式为 `alice-hermes-agent`。

#### 各策略的具体效果

- **`per-directory`** —— 使用 `$PWD` 的基名作为会话名称。在 `~/code/myapp` 和 `~/code/other` 两个目录中分别启动 Hermes，将会生成两个独立的会话。只要处于同一目录，多次运行时仍属于同一个会话。
- **`per-repo`** —— 使用 Git 根目录的名称作为会话名称。同一个仓库内的所有子目录共享同一个会话。如果不在 Git 仓库中，则回退到 `per-directory` 策略。
- **`per-session`** —— 使用 Hermes 会话 ID（时间戳 + 十六进制字符串）作为会话名称。每次调用 `hermes` 命令都会启动一个全新的 Honcho 会话。如果没有可用的会话 ID，则回退到 `per-directory` 策略。
- **`global`** —— 使用工作空间名称作为会话名称。所有内容都存储在同一个会话中，记忆会累积在所有目录和多次运行过程中。

### 多配置文件模式

多个 Hermes 配置文件可以共享同一个工作空间，同时保持独立的 AI 身份。配置解析的优先级为 **主机块 > 根级设置 > 环境变量 > 默认值**——主机块会继承根级设置，因此共享配置只需声明一次即可：

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

在同一个共享环境（`hermes`）中，这两种配置文件均会使用相同的用户（`yourname`），但每个 AI 对等体都会独立生成自身的观察结果、结论及行为模式。程序员的记忆侧重于代码相关内容，而主代理的记忆则更为广泛。

主机密钥取决于当前激活的 Hermes 配置文件：默认为 `hermes`，或者为 `hermes_<profile>`（例如 `hermes -p coder` 时，主机密钥为 `hermes_coder`）。为保持兼容性，系统仍会读取旧版本的 `hermes.<profile>` 主机配置文件；而当 CLI 写入针对特定配置文件的 Honcho 配置后，这些旧配置将会被迁移。

### 辩证推理机制

| 键名 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `dialecticDepth` | int | `1` | 每个辩证循环的迭代次数（范围为 1–3，会进行限制）。1 表示单次查询，2 表示审核+综合分析，3 表示审核+综合分析+对齐验证 |
| `dialecticDepthLevels` | array | — | 每次迭代的推理级别字符串数组，为可选配置。可覆盖按比例确定的默认值。示例：`["minimal", "low", "medium"]` |
| `dialecticReasoningLevel` | string | `"low"` | `.chat()` 函数的基准推理级别：`"minimal"`、`"low"`、`"medium"`、`"high"`、`"max"` |
| `dialecticDynamic` | bool | `true` | 当该值为 `true` 时，模型可通过 `honcho_reasoning` 工具在每次调用时覆盖推理级别；当为 `false` 时，则始终使用 `dialecticReasoningLevel` 所指定的级别 |
| `dialecticMaxChars` | int | `600` | 可注入系统提示语中的辩证推理结果的最大字符数 |
| `dialecticMaxInputChars` | int | `10000` | 传递给 `.chat()` 函数的辩证推理查询输入的最大字符数。Honcho 云服务的限制也为 10k |
| `reasoningHeuristic` | bool | `true` | 根据查询内容自动调整：会根据查询长度动态提升自动注入的辩证推理级别——查询长度≥120 字符时提升 1 级，≥400 字符时提升 2 级，最终数值会受 `reasoningLevelCap` 的限制。若该值为 `false`，则所有自动调用都将固定使用 `dialecticReasoningLevel` 所指定的级别 |
| `reasoningLevelCap` | string | `"high"` | `reasoningHeuristic` 机制的级别上限：`"minimal"`、`"low"`、`"medium"`、`"high"`、`"max"` |

### 令牌预算

| 键名 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `contextTokens` | int | SDK 默认值 | 用于 `context()` API 调用的令牌预算。同时也可用于控制预取内容的截断长度（按令牌数乘以 4 字符计算） |
| `messageMaxChars` | int | `25000` | 通过 `add_messages()` 发送的每条消息的最大字符数。超过此限制后，消息将被分割并添加 `[continued]` 标记。Honcho 云服务的限制也为 25k |

### 使用频率控制（成本管控）

| 键名 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `contextCadence` | int | `1` | 基础上下文刷新的最小间隔轮次数（包括会话摘要、内容表示及卡片信息） |
| `dialecticCadence` | int | `1` | 执行辩证推理型 `.chat()` 调用的最小间隔轮次数 |
| `injectionFrequency` | string | `"every-turn"` | 可设置为 `"every-turn"` 或 `"first-turn"`：前者表示在每一轮对话中都注入上下文，后者则仅在用户的第一条消息时注入上下文，从第二轮开始跳过 |

### 细粒度观察功能

该功能与 Honcho 的每个对等体对应的 `SessionPeerConfig` 一一对应。当该配置存在时，会覆盖原有的 `observationMode` 预设值。

```json
"observation": {
  "user": { "observeMe": true, "observeOthers": true },
  "ai":   { "observeMe": true, "observeOthers": true }
}
```

| 字段 | 默认值 | 描述 |
|-------|---------|-------------|
| `user.observeMe` | `true` | 用户端自我观察（Honcho会构建用户画像） |
| `user.observeOthers` | `true` | 用户端观察AI发送的消息 |
| `ai.observeMe` | `true` | AI端自我观察（Honcho会构建AI画像） |
| `ai.observeOthers` | `true` | AI端观察用户发送的消息（支持跨端对话交互） |

预设值：
- `"directional"`（默认）：四个字段均为`true`
- `"unified"`：用户端`observeMe=true`，AI端`observeOthers=true`，其余为`false`

### 硬编码限制

| 限制项 | 值 |
|-------|-----|
| 搜索工具最大令牌数 | 2000（上限），800（默认值） |
| 获取对方信息所需令牌数 | 200 |

## 环境变量

| 变量 | 备用变量 |
|----------|----------|
| `HONCHO_API_KEY` | `apiKey` |
| `HONCHO_BASE_URL` | `baseUrl` |
| `HONCHO_ENVIRONMENT` | `environment` |
| `HERMES_HONCHO_HOST` | 主机地址覆盖值 |
| `HONCHO_OAUTH_DASHBOARD` | OAuth授权地址（默认为云端控制台；本地开发环境为`localhost:3000`） |
| `HONCHO_OAUTH_AUTHORIZE_URL` | 完整的授权URL（可覆盖控制台地址） |
| `HONCHO_OAUTH_TOKEN_URL` | 令牌获取端点（默认为云端API；本地开发环境为`localhost:8000`） |
| `HONCHO_OAUTH_CLIENT_ID` | OAuth客户端标识（默认为`hermes-agent`） |
| `HONCHO_OAUTH_SCOPE` | 请求的权限范围（默认为`write`） |

## CLI命令

| 命令 | 描述 |
|---------|-------------|
| `hermes memory setup honcho` | 直接配置Honcho——适用于全新安装场景 |
| `hermes honcho setup` | 交互式设置向导（仅在Honcho成为激活提供者后注册一次；会跳转至`hermes memory setup`命令） |
| `hermes honcho status` | 显示当前激活配置文件的已解析配置 |
| `hermes honcho enable` / `disable` | 切换当前激活配置文件中是否启用Honcho |
| `hermes honcho mode <mode>` | 更改回忆或观察模式 |
| `hermes honcho peer --user <name>` | 更新用户端名称 |
| `hermes honcho peer --ai <name>` | 更新AI端名称 |
| `hermes honcho tokens --context <N>` | 设置上下文令牌预算 |
| `hermes honcho tokens --dialectic <N>` | 设置对话交互的最大字符数 |
| `hermes honcho map <name>` | 将当前目录映射为会话名称 |
| `hermes honcho sync` | 为所有Hermes配置文件创建主机块 |

## 配置示例

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
