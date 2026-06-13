# Honcho Memory Provider

一种专为人工智能设计的跨会话用户建模方案，具备多轮辩证推理、会话摘要生成、双向交互工具以及持久化结论存储功能。

> **Honcho 文档：** <https://docs.honcho.dev/v3/guides/integrations/hermes>

## 需求条件

- 安装 `pip install honcho-ai` 工具
- 获取来自 [app.honcho.dev](https://app.honcho.dev) 的 Honcho API 密钥，或使用自托管实例

## 设置步骤

```bash
hermes memory setup honcho   # configure Honcho directly (works on a fresh install)
hermes memory setup          # generic picker, choose Honcho from the list
```

或手动操作：
```bash
hermes config set memory.provider honcho
echo "HONCHO_API_KEY=***" >> ~/.hermes/.env
```

> 使用 `hermes honcho setup` 也可以，但必须在 Honcho 成为当前活跃的
> 内存提供者之后才能使用——因为 `honcho` 子命令仅针对当前活跃的提供者注册。在全新安装时，请使用 `hermes memory setup honcho`。

## 架构概览

### 双层上下文注入机制

为保留提示词缓存，上下文会在 API 调用时注入到**用户消息**中（而非系统提示语）中。只有静态模式的相关头部信息会被加入系统提示语。注入的上下文块会用 `<memory-context>` 标签包裹，并附有系统说明，指出其为背景数据而非新的用户输入。

该机制包含两个独立层级，各自按固定节奏更新：

**第一层——基础上下文**（每 `contextCadence` 次刷新）：
1. **会话摘要**——来自 `session.context(summary=True)`，置于最前端
2. **用户画像**——Honcho 对用户的动态建模结果
3. **用户信息卡**——关键事实的快照
4. **AI 对手自我描述**——Honcho 对 AI 对手的建模结果
5. **AI 身份卡**——AI 对手的相关事实

**第二层——辩证补充内容**（每 `dialecticCadence` 次生成）：
通过对用户进行多轮 `.chat()` 推理，将结果附加在基础上下文之后。

这两层内容会合并在一起，然后通过 `_truncate_to_budget` 函数根据 `contextTokens` 限制进行截断处理（每个字符计为4个令牌，且会考虑词边界）。

### 冷启动会话提示语与热会话提示语的区别

辩证推理的第0轮会自动根据会话状态选择对应的提示语：

- **冷启动状态**（未缓存基础上下文）： “这个人是谁？他们的偏好、目标和工作风格是什么？请提供有助于 AI 助手立即发挥作用的事实信息。”
- **热会话状态**（已存在基础上下文）： “结合本次会话中已讨论的内容，哪些关于该用户的背景信息与当前对话最相关？请优先考虑与当前对话相关的信息，而非仅展示生平事实。”

此设置不可配置，由系统自动决定。

### 辩证推理深度（多轮推理机制）

`dialecticDepth` 参数（取值范围1–3，会进行限制）用于控制每个辩证周期内触发多少次 `.chat()` 调用：

| 深度 | 循环次数 | 行为特点 |
|------|----------|----------|
| 1 | 单次 `.chat()` 调用 | 仅发送基础查询（无论处于冷启动还是热会话状态） |
| 2 | 审核 + 综合 | 第0轮的结果会先经过自我审核，第1轮则进行针对性综合。如果第0轮返回的信息量较大（超过300个字符，或以项目符号/分段形式呈现且每段超过100个字符），则会触发条件性中止流程 |
| 3 | 审核 + 综合 + 协调 | 第2轮会协调前几轮中的矛盾点，最终形成综合结果 |

### 比例式推理层级

当未设置 `dialecticDepthLevels` 时，每轮推理会使用相对于“基础”层级 `dialecticReasoningLevel` 的比例值：

| 深度 | 各轮使用的层级 |
|------|--------------|
| 1 | [基础] |
| 2 | [最低级, 基础级] |
| 3 | [最低级, 基础级, 低级] |

可通过 `dialecticDepthLevels` 参数进行覆盖，该参数为一个数组，明确指定每轮应使用的推理层级字符串。

### 三个相互独立的辩证控制参数

| 参数名 | 控制内容 | 类型 |
|--------|----------|------|
| `dialecticCadence` | 辩证推理的触发频率——两次触发之间的最小轮数 | 整数 |
| `dialecticDepth` | 每次触发时的循环次数（1–3） | 整数 |
| `dialecticReasoningLevel` | 每次 `.chat()` 调用的推理强度上限 | 字符串 |

### 输入内容净化处理

`run_conversation` 函数会在处理用户输入之前，先移除其中泄露的 `<memory-context>` 块。如果 `saveMessages` 函数保存了包含注入上下文的对话轮次，这些上下文块可能会通过消息历史记录在后续轮次中再次出现。净化函数会同时删除 `<memory-context>` 块及其相关的系统说明文字。

## 工具功能

共有五种双向交互工具。所有工具都支持可选的 `peer` 参数（取值为 `"user"` 或 `"ai"`，默认为 `"user"`）。

| 工具名称 | 是否调用大语言模型 | 功能描述 |
|----------|------------------|----------|
| `honcho_profile` | 否 | 生成用户信息卡——即关键事实的快照 |
| `honcho_search` | 否 | 对存储的上下文进行语义搜索（默认搜索量800个令牌，最大2000个） |
| `honcho_context` | 否 | 提供完整的会话上下文：摘要、用户画像、信息卡及所有对话记录 |
| `honcho_reasoning` | 是 | 通过多轮辩证式的 `.chat()` 调用，由大语言模型生成综合答案 |
| `honcho_conclude` | 否 | 记录关于该用户的永久性事实或结论 |

工具的显示方式取决于 `recallMode` 参数：在 `context` 模式下这些工具会被隐藏，而在 `tools` 模式和 `hybrid` 模式下则始终可见。

## 配置文件解析规则

系统会按顺序读取第一个存在的配置文件：

| 优先级 | 文件路径 | 适用范围 |
|--------|----------|----------|
| 1 | `$HERMES_HOME/honcho.json` | 仅适用于特定配置文件的独立 Hermes 实例 |
| 2 | `~/.hermes/honcho.json` | 默认配置文件，适用于共享主机环境 |
| 3 | `~/.honcho/config.json` | 全局配置文件，用于跨应用之间的交互 |

主机标识符由当前激活的 Hermes 配置文件决定：默认为 `hermes`，或者为 `hermes_<profile>` 的形式。

对于每一项配置键，其解析顺序为：**主机配置块 > 根级配置 > 环境变量值 > 默认值**。

## 完整配置参考文档

### 身份与连接设置

| 键名 | 类型 | 默认值 | 功能描述 |
|------|------|---------|----------|
| `apiKey` | 字符串 | — | API 密钥。若未提供，则自动使用 `HONCHO_API_KEY` 环境变量中的值 |
| `baseUrl` | 字符串 | — | 自托管 Honcho 服务的基准 URL。本地地址则无需进行 API 密钥验证 |
| `environment` | 字符串 | `"production"` | SDK 所处的运行环境标识 |
| `enabled` | 布尔值 | 自动设置 | 总开关。只要提供了 `apiKey` 或 `baseUrl`，该选项就会自动启用 |
| `workspace` | 字符串 | 主机标识符 | Honcho 的工作空间 ID。处于同一工作空间的所有配置文件可以共享相同的用户身份及相关记忆信息 |
| `peerName` | 字符串 | — | 用户端的对应实体标识 |
| `aiPeer` | 字符串 | 主机标识符 | AI 端的对应实体标识 |

### 身份映射（网关多用户场景）

在基于网关的部署环境中（如 Telegram、Discord、Slack 等），每个用户都会拥有平台自带的运行时标识符（如 Telegram 的 UID、Discord 的 snowflake ID、Slack 的用户ID）。上述三个键用于控制如何将这些运行时标识符映射到 Honcho 中的对应实体。该映射过程由配置文件决定，且具有确定性——系统不会自动合并或推断这些标识符之间的关系。

| 键名 | 类型 | 默认值 | 功能描述 |
|------|------|---------|----------|
| `pinUserPeer` | 布尔值 | `false` | 当该参数设置为 `true` 时，所有通过网关接入的用户都会被统一映射到 `peerName` 所标识的实体。适用于希望所有平台用户以及其他用户共享同一个对应实体的单操作员部署场景。该参数也可使用别名 `pinPeerName` |
| `pinPeerName` | 布尔值 | `false` | 与 `pinUserPeer` 功能相同，为该参数提供的别名 |
| `userPeerAliases` | 对象 | `{}` | 将运行时标识符映射到对应实体标识符的映射表（格式为 `{"86701400": "eri"}`）。推荐的使用模式是一对多关系——将所有运行时标识符都映射到同一个实体名称。系统不支持多对一的关系，即一个运行时标识符只能对应一个实体 |
| `runtimePeerPrefix` | 字符串 | `""` | 当没有匹配的别名时，会将该前缀附加到未知的运行时标识符前面，以此为它们命名（例如 `"telegram_"` → `telegram_86701400`）。此功能仅在没有匹配的别名时使用，旨在避免那些运行时标识符结构相似的不同平台之间出现冲突 |

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

**为何没有 `pinAiPeer`？** 由于设计原因，AI 对端已被固定——`aiPeer` 是唯一的 AI 端身份设置，且解析器绝不会覆盖它。仅有用户端对端才存在运行时与配置之间的冲突，而 `pinUserPeer` 正是用于解决这一问题。

**主机与根级的语义差异。** 这三个键在根级以及 `hosts.<host>` 子层级均被支持，但主机级设置具有优先权。对于映射和前缀而言，主机级设置会整体*替换*根级值（而非合并），因此主机可以自主决定其身份标识体系，或通过 `userPeerAliases: {}` / `runtimePeerPrefix: ""` 将其清空。

**部署模式**（`hermes memory setup honcho` 会通过一次提示来设置这些参数）：

- **单操作员模式** — `pinUserPeer: true`。所有网关用户均对应同一个 `peerName`。适用于将 Hermes 连接到个人 Telegram/Discord 等平台的个人使用场景。
- **多用户网关模式** — `pinUserPeer: false`，可选 `runtimePeerPrefix`。每位运行时用户拥有独立的对端。适用于为大量人类用户提供服务的机器人。
- **混合模式** — `pinUserPeer: false`，通过 `userPeerAliases` 将操作员的运行时 ID 映射到 `peerName`。在这种多用户网关模式下，只有你是被路由到的对象，其他用户则保持独立对端。

**从单操作员模式迁移至多用户模式。** 将 `pinUserPeer` 从 `true` 改为 `false` 并不会迁移数据。在固定模式下，`peerName` 下积累的记忆会保留原样；而新的运行时用户则会对应全新的、空的对端。为保持自身的对话连贯性，建议采用**混合模式**——将你的运行时 ID 再次映射回 `peerName`，这样你的发言仍会记录在共享的历史记录中，同时其他用户也能拥有独立的对端。当检测到从单操作员模式向多用户模式的切换时，设置向导会自动推荐此方案。

### 记忆与回忆功能

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `recallMode` | 字符串 | `"hybrid"` | `"hybrid"`（自动注入 + 工具），`"context"`（仅自动注入，隐藏工具），`"tools"`（仅工具，无自动注入）。旧版本的 `"auto"` 已被替换为 `"hybrid"` |
| `observationMode` | 字符串 | `"directional"` | 预设值：`"directional"`（全部开启）或 `"unified"`（共享记忆池）。如需精细控制，可使用 `observation` 对象 |
| `observation` | 对象 | — | 每个对端的观察配置（详见“观察功能”部分） |

### 写入行为

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `writeFrequency` | 字符串/整数 | `"async"` | `"async"`（后台异步写入），`"turn"`（每轮对话同步写入），`"session"`（会话结束时批量写入），或整数 N（每 N 轮写入一次） |
| `saveMessages` | 布尔值 | `true` | 是否将消息持久保存到 Honcho API 中 |

### 会话解析

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `sessionStrategy` | 字符串 | `"per-directory"` | `"per-directory"`（按目录）、`"per-session"`（按会话）、`"per-repo"`（按 Git 仓库根目录）、`"global"`（全局） |
| `sessionPeerPrefix` | 布尔值 | `false` | 是否在会话键前添加对端名称前缀 |
| `sessions` | 对象 | `{}` | 手动指定的目录与会话名称的映射关系 |

#### 会话名称解析

Honcho 的会话名称决定了记忆数据将存储到哪个对话容器中。解析遵循优先级顺序——首先匹配到的规则生效：

| 优先级 | 来源 | 示例会话名称 |
|----------|------|---------------------|
| 1 | 手动映射（`sessions` 配置） | `"myproject-main"` |
| 2 | `/title` 命令（会话中重命名） | `"refactor-auth"` |
| 3 | 网关会话键（Telegram、Discord 等） | `"agent-main-telegram-dm-8439114563"` |
| 4 | `per-session` 模式 | Hermes 会话 ID（如 `20260415_a3f2b1`） |
| 5 | `per-repo` 模式 | Git 仓库根目录名称（如 `hermes-agent`） |
| 6 | `per-directory` 模式 | 当前目录的基名（如 `src`） |
| 7 | `global` 模式 | 工作空间名称（如 `hermes`） |

无论 `sessionStrategy` 设置为何，网关平台始终优先采用第 3 种解析方式（即按聊天会话隔离），仅 CLI 会话才受策略设置影响。

如果 `sessionPeerPrefix` 设为 `true`，则会在会话键前添加对端名称前缀，例如：`eri-hermes-agent`。

#### 各种策略的生效效果

- **`per-directory`** — 使用 `$PWD` 的基名作为会话名称。在 `~/code/myapp` 和 `~/code/other` 两个目录中分别启动 Hermes，将会生成两个独立的会话。若处于同一目录，则多次运行仍属于同一个会话。
- **`per-repo`** — 使用 Git 仓库的根目录名称。仓库内的所有子目录共享同一个会话。若不在 Git 仓库中，则回退至 `per-directory` 模式。
- **`per-session`** — 使用 Hermes 会话 ID（时间戳 + 十六进制字符串）。每次调用 `hermes` 命令都会启动一个新的 Honcho 会话。若没有可用的会话 ID，则回退至 `per-directory` 模式。
- **`global`** — 使用工作空间名称。所有内容都归为一个会话，记忆数据会在所有目录和运行记录中累积。

### 多配置文件模式

多个 Hermes 配置文件可以共享同一个工作空间，同时保持独立的 AI 身份。配置解析的优先级为：**主机块 > 根级设置 > 环境变量 > 默认值**——主机块会继承根级设置，因此共享配置只需声明一次即可：

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

在同一个共享环境（`hermes`）中，这两种配置文件都会看到相同的用户（`yourname`），但每个 AI 对等体都会独立形成自身的观察结果、结论及行为模式。编码者的记忆侧重于代码相关内容，而主代理的记忆则更为广泛。

主机密钥取决于当前激活的 Hermes 配置文件：默认为 `hermes`，或者为 `hermes_<profile>`（例如 `hermes -p coder` 时，主机密钥为 `hermes_coder`）。为保持兼容性，系统仍会读取旧版本的 `hermes.<profile>` 主机配置块；而当 CLI 写入针对特定配置文件的 Honcho 配置后，这些旧配置块将会被迁移。

### 辩证推理机制

| 键名 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `dialecticDepth` | int | `1` | 每个辩证循环的迭代次数（范围为 1–3，会进行限制）。1 表示单次查询，2 表示审核+综合分析，3 表示审核+综合分析+对齐验证 |
| `dialecticDepthLevels` | array | — | 每次迭代的推理级别字符串数组，为可选配置。可覆盖默认的比例设置。示例：`["minimal", "low", "medium"]` |
| `dialecticReasoningLevel` | string | `"low"` | `.chat()` 函数的默认推理级别：`"minimal"`、`"low"`、`"medium"`、`"high"`、`"max"` |
| `dialecticDynamic` | bool | `true` | 当该值为 `true` 时，模型可通过 `honcho_reasoning` 工具在每次调用时覆盖推理级别；当为 `false` 时，则始终使用 `dialecticReasoningLevel` 所指定的级别 |
| `dialecticMaxChars` | int | `600` | 可注入系统提示语中的辩证推理结果的最大字符数 |
| `dialecticMaxInputChars` | int | `10000` | 传递给 `.chat()` 函数的辩证推理查询输入的最大字符数。Honcho 云服务的限制为 10,000 字符 |

### 令牌预算设置

| 键名 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `contextTokens` | int | SDK默认值 | 用于 `context()` API 调用的令牌预算。同时也可用于控制预取内容的截断长度（按字符数 × 4 计算） |
| `messageMaxChars` | int | `25000` | 通过 `add_messages()` 函数发送的每条消息的最大字符数。超过此限制后，消息将被分割并添加 `[continued]` 标记。Honcho 云服务的限制为 25,000 字符 |

### 调用频率控制（成本管控）

| 键名 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `contextCadence` | int | `1` | 基础上下文刷新之间的最小轮次间隔（包括会话摘要、内容呈现及卡片信息更新） |
| `dialecticCadence` | int | `1` | 执行辩证推理型 `.chat()` 调用之间的最小轮次间隔 |
| `injectionFrequency` | string | `"every-turn"` | 可设置为 `"every-turn"` 或 `"first-turn"`：前者表示在每一轮对话中都注入上下文，后者则仅在用户的第一条消息时注入上下文，从第二轮开始跳过 |
| `reasoningLevelCap` | string | — | 推理级别的硬性上限：`"minimal"`、`"low"`、`"medium"`、`"high"` |

### 细粒度观察功能

该功能与 Honcho 中针对每个对等体的 `SessionPeerConfig` 一一对应。当该配置存在时，会覆盖原有的 `observationMode` 预设值。

```json
"observation": {
  "user": { "observeMe": true, "observeOthers": true },
  "ai":   { "observeMe": true, "observeOthers": true }
}
```

| 字段 | 默认值 | 描述 |
|-------|---------|-------------|
| `user.observeMe` | `true` | 用户端自我观察（Honcho负责构建用户画像） |
| `user.observeOthers` | `true` | 用户端观察AI生成的消息 |
| `ai.observeMe` | `true` | AI端自我观察（Honcho负责构建AI画像） |
| `ai.observeOthers` | `true` | AI端观察用户发送的消息（支持跨端对话交互） |

预设配置：
- `"directional"`（默认）：四个值均为`true`
- `"unified"`：用户端`observeMe=true`，AI端`observeOthers=true`，其余为`false`

### 硬编码限制

| 限制项 | 值 |
|-------|-----|
| 搜索工具最大令牌数 | 2000（上限），800（默认值） |
| 获取对方信息所需令牌数 | 200 |

## 环境变量

| 变量 | 备用变量 |
|------|----------|
| `HONCHO_API_KEY` | `apiKey` |
| `HONCHO_BASE_URL` | `baseUrl` |
| `HONCHO_ENVIRONMENT` | `environment` |
| `HERMES_HONCHO_HOST` | 主机地址覆盖值 |

## CLI命令

| 命令 | 描述 |
|------|-------------|
| `hermes memory setup honcho` | 直接配置Honcho——适用于全新安装场景 |
| `hermes honcho setup` | 交互式配置向导（仅在Honcho成为默认提供者后注册一次；会跳转至`hermes memory setup`命令） |
| `hermes honcho status` | 显示当前激活配置文件的已应用设置 |
| `hermes honcho enable` / `disable` | 切换当前激活配置文件中对Honcho的启用/禁用状态 |
| `hermes honcho mode <mode>` | 更改回溯或观察模式 |
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
