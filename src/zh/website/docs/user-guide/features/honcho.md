---
sidebar_position: 99
title: "Honcho Memory"
description: "AI-native persistent memory via Honcho — dialectic reasoning, multi-agent user modeling, and deep personalization"
---

# Honcho 内存系统

[Honcho](https://github.com/plastic-labs/honcho) 是一款专为人工智能设计的记忆后端，它在 Hermes 内置的记忆系统基础上，进一步实现了辩证推理与深度用户建模功能。与单纯的键值存储不同，Honcho 通过分析对话内容，持续构建关于用户的动态模型——包括其偏好、沟通风格、目标以及行为模式等。

:::info Honcho 是一种记忆提供者插件
Honcho 已集成到 [记忆提供者](./memory-providers.md) 系统中。以下所有功能均可通过统一的记忆提供者接口使用。
:::

## Honcho 的优势

| 功能 | 内置记忆系统 | Honcho |
|------|------------|--------|
| 跨会话持久化 | ✔ 基于文件的 MEMORY.md/USER.md | ✔ 通过 API 实现服务器端存储 |
| 用户档案 | ✔ 由人工手动整理 | ✔ 自动进行辩证推理 |
| 会话摘要 | — | ✔ 支持会话级上下文注入 |
| 多智能体隔离 | — | ✔ 每个智能体拥有独立的档案 |
| 观察模式 | — | ✔ 支持统一观察或定向观察 |
| 结论（推导出的洞察） | — | ✔ 服务器端对行为模式进行推理 |
| 历史记录搜索 | ✔ 使用 FTS5 进行会话搜索 | ✔ 基于结论的语义搜索 |

**辩证推理**：在每次对话轮次之后（由 `dialecticCadence` 参数控制频率），Honcho 会分析对话内容，从而推导出关于用户偏好、习惯和目标的洞察。这些洞察会随着时间不断积累，使智能体获得超越用户明确表述的深度理解。该功能支持多轮推理（1–3 轮），并能自动选择冷启动提示或热启动提示——冷启动查询侧重于获取用户的通用信息，而热启动查询则优先考虑会话中的相关上下文。

**会话级上下文**：现在的基础上下文除了包含用户画像和智能体卡片外，还加入了会话摘要。这使智能体能够了解当前会话中已经讨论过的内容，从而减少重复提问，保持对话连贯性。

**多智能体档案**：当多个 Hermes 实例与同一用户交互时（例如代码助手和个人助理），Honcho 会为每个智能体维护独立的“同伴”档案。这样，每个智能体只能看到自己的观察结果和结论，避免了上下文之间的相互干扰。

## 设置指南

```bash
hermes memory setup    # select "honcho" from the provider list
```

或手动进行配置：

```yaml
# ~/.hermes/config.yaml
memory:
  provider: honcho
```

```bash
echo 'HONCHO_API_KEY=***' >> ~/.hermes/.env
```

在 [honcho.dev](https://honcho.dev) 获取 API 密钥。

## 架构设计

### 两层上下文注入机制

在“混合模式”或“上下文模式”的每一轮对话中，Honcho 会构建两层上下文并注入系统提示词中：

1. **基础上下文**——会话摘要、用户信息、用户同伴卡片、AI 自我描述以及 AI 身份卡。该层会根据 `contextCadence` 设置的频率进行更新。它用于回答“这是谁”这类问题。
2. **辩证补充层**——由大语言模型根据用户的当前状态和需求生成的推理内容。该层会根据 `dialecticCadence` 的设置进行更新。它用于识别“当前最关键的是什么”。

这两层内容会被拼接在一起，然后根据设定的 `contextTokens` 预算进行截断。

### 冷启动与热会话提示策略选择

系统会自动在两种提示策略之间切换：

- **冷启动状态**（尚未生成基础上下文）：使用通用查询语句，例如“这是谁？他们的偏好、目标和工作风格是什么？”
- **热会话状态**（已存在基础上下文）：使用针对当前会话的查询语句，例如“结合本会话中已讨论的内容，关于该用户的哪些信息最为相关？”

这种切换会根据是否已生成基础上下文自动完成。

### 三个相互独立的配置参数

成本与深度由三个独立参数控制：

| 参数 | 控制功能 | 默认值 |
|------|----------|---------|
| `contextCadence` | 控制 `context()` API 调用的频率（即基础层更新的间隔） | `1` |
| `dialecticCadence` | 控制 `peer.chat()` 大语言模型调用的频率（即辩证层更新的间隔）。推荐值为 1–5 | `2` |
| `dialecticDepth` | 每次辩证推理调用时进行的 `.chat()` 调用次数（1–3 次） | `1` |

这三个参数是相互独立的——你可以选择高频更新上下文但低频进行辩证推理，或者选择低频但进行多次深度的辩证推理。例如：`contextCadence: 1, dialecticCadence: 5, dialecticDepth: 2` 表示每轮更新一次基础上下文，每 5 轮进行一次辩证推理，且每次辩证推理包含 2 次 `.chat()` 调用。

### 辩证推理的深度（多轮机制）

当 `dialecticDepth` 大于 1 时，每次辩证推理调用会执行多次 `.chat()` 调用：

- **第 0 轮**：使用冷启动或热会话提示（见上文）
- **第 1 轮**：自我审计——识别初始评估中的不足，并整合来自近期会话的证据
- **第 2 轮**：一致性校验——检查前几轮结果之间的矛盾，并生成最终的综合结论

每轮推理会使用不同强度的推理水平（前几轮强度较低，主轮使用基础强度）。你可以通过 `dialecticDepthLevels` 参数为每轮指定不同的强度级别，例如对于深度为 3 的情况，可设置为 `["minimal", "medium", "high"]`。

如果前一轮已经产生了较为明确的输出（长度较长且结构清晰），后续轮次会提前终止，因此深度为 3 并不意味着一定需要进行 3 次大语言模型调用。

### 会话启动时的预热处理

在会话开始时，Honcho 会在后台以配置的完整 `dialecticDepth` 深度执行一次辩证推理调用，并将结果直接用于第一轮的上下文构建。对于冷启动的同伴，单轮预热通常只能生成较简略的输出；而多轮预热则会在用户开口之前完成审计与校验流程。如果到第一轮时预热尚未完成，系统会回退到带有定时超时的同步调用方式。

### 根据查询长度自适应调整推理强度

系统会根据查询内容的长度自动调整辩证推理的强度：当查询长度≥120 个字符时，推理强度提升 1 级；≥400 个字符时再提升 2 级，最终强度会被限制在 `reasoningLevelCap`（默认值为“high”）以内。如果你希望强制所有自动调用都使用固定的推理强度，可以设置 `reasoningHeuristic: false`。可选的推理强度级别包括：`minimal`、`low`、`medium`、`high`、`max`。

## 配置选项

Honcho 的配置文件位于 `~/.honcho/config.json`（全局配置）或 `$HERMES_HOME/honcho.json`（个人配置文件）。设置向导可以帮你完成这些配置。

### 带身份验证的自托管 Honcho

当将 Hermes 指向自托管的 Honcho 服务器时，执行 `hermes honcho setup`（以及 `hermes memory setup`）命令后，系统会要求你输入基础 URL 之后的**本地 JWT/承载令牌**。请粘贴使用服务器的 `AUTH_JWT_SECRET`（即 Honcho compose 环境变量）签名的 JWT 以启用身份验证；如果服务器运行时设置了 `AUTH_USE_AUTH=false`，则该字段可留空。本地令牌会存储在 `honcho.json` 文件的 `hosts.<host>.apiKey` 块中，与任何云端的 `apiKey` 是分开存储的，因此之后你可以将“使用云端还是本地？”的选项改回“云端”，而不会丢失任何凭证。

### 完整配置参考

| 参数 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextTokens` | `null`（无上限） | 每轮对话中自动注入上下文的令牌预算。可设置为一个整数（如 1200）来设定上限。内容会在单词边界处被截断 |
| `contextCadence` | `1` | `context()` API 调用之间的最小间隔轮数（即基础层更新的间隔） |
| `dialecticCadence` | `2` | `peer.chat()` 大语言模型调用之间的最小间隔轮数（即辩证层更新的间隔）。推荐值为 1–5。在“工具模式”下此参数无效，因为模型会直接发起调用 |
| `dialecticDepth` | `1` | 每次辩证推理调用时进行的 `.chat()` 调用次数。该值会被限制在 1–3 之间 |
| `dialecticDepthLevels` | `null` | 可选参数，用于指定每轮推理的强度级别数组，例如 `["minimal", "low", "medium"]`。可用于覆盖默认的比例式设置 |
| `dialecticReasoningLevel` | `'low'` | 基础推理强度：`minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 当该参数为 `true` 时，模型可以通过工具参数在每次调用中动态调整推理强度 |
| `dialecticMaxChars` | `600` | 注入系统提示词中的辩证推理结果的最大字符数 |
| `recallMode` | `'hybrid'` | `hybrid`（自动注入上下文 + 提供工具）、`context`（仅自动注入上下文）、`tools`（仅使用工具） |
| `writeFrequency` | `'async'` | 消息刷新的时机：`async`（后台线程处理）、`turn`（同步处理）、`session`（在会话结束时批量处理），或指定整数 N |
| `saveMessages` | `true` | 是否将消息持久化到 Honcho API 中 |
| `observationMode` | `'directional'` | `directional`（全部开启）或 `unified`（共享池）。可通过 `observation` 对象进行更细粒度的控制 |
| `messageMaxChars` | `25000` | 通过 `add_messages()` 发送的每条消息的最大字符数。超过该限制时会进行分片处理 |
| `dialecticMaxInputChars` | `10000` | 用于向 `peer.chat()` 发送辩证推理查询输入的最大字符数 |
| `sessionStrategy` | `'per-directory'` | `per-directory`（按工作目录）、`per-repo`（按代码仓库）、`per-session`（按会话）或 `global`（全局统一） |
| `pinUserPeer` | `false` | 仅适用于网关模式。当该参数为 `true` 时，所有平台用户都会被映射到同一个同伴名称 |
| `userPeerAliases` | `{}` | 仅适用于网关模式。这是一个将运行时 ID 映射到同伴名称的映射表（例如 `{"7654321": "alice"}`），为多对一关系 |
| `runtimePeerPrefix` | `""` | 仅适用于网关模式。当没有匹配的别名时，用于为未知的运行时 ID 添加前缀，格式为 `telegram_7654321` |

**会话策略**决定了 Honcho 会话如何与你的工作内容对应：
- `per-session`——每次运行 `hermes` 都会创建一个全新的会话。适合新用户使用，可借助工具实现记忆延续。
- `per-directory`——每个工作目录对应一个 Honcho 会话。上下文会在多次运行之间逐步积累。
- `per-repo`——每个 Git 代码仓库对应一个会话。
- `global`——所有目录共享同一个会话。

**回忆模式**决定了记忆信息如何融入对话流程：
- `hybrid`——既自动将上下文注入系统提示词，也提供工具供使用（模型自行决定何时发起查询）。
- `context`——仅自动注入上下文，工具不可用。
- `tools`——仅使用工具，不进行自动上下文注入。此时智能体必须显式调用 `honcho_reasoning`、`honcho_search` 等函数。

**不同回忆模式下的设置差异：**

| 设置项 | `hybrid` 模式 | `context` 模式 | `tools` 模式 |
|--------|--------------|----------------|--------------|
| `writeFrequency` | 刷新消息 | 刷新消息 | 刷新消息 |
| `contextCadence` | 控制基础上下文更新 | 控制基础上下文更新 | 无效——无自动注入 |
| `dialecticCadence` | 控制自动大语言模型调用 | 控制自动大语言模型调用 | 无效——模型会直接发起调用 |
| `dialecticDepth` | 每次调用进行多轮推理 | 每次调用进行多轮推理 | 无效——模型会直接发起调用 |
| `contextTokens` | 限制注入上下文的字符数 | 限制注入上下文的字符数 | 无效——无自动注入 |
| `dialecticDynamic` | 控制模型是否可动态调整强度 | 无此功能（无工具） | 控制模型是否可动态调整强度 |

在“工具模式”下，模型拥有完全的控制权——它可以根据自己的意愿，在任意选定的推理强度下调用 `honcho_reasoning` 函数。节奏与预算相关设置仅适用于那些包含自动上下文注入模式的类型（即 `hybrid` 和 `context` 模式）。

## 网关身份映射

这些设置仅在运行 [Hermes 网关](../../developer-guide/gateway-internals.md) 时才起作用——这是用户通过平台原生运行时 ID（如 Telegram UID、Discord snowflake、Slack 用户名）进入系统的入口点。CLI、TUI 和桌面端会话没有运行时 ID，因此总是会被映射为 `peerName`，所以在网关外部这些键值没有任何作用。

设置向导会检测是否有网关平台连接，如果没有则直接跳过此步骤。当执行设置向导时，它会询问一个问题——“谁与这个网关交互？”——并据此生成相应的键值：

| 回答内容 | 生成的键值 |
|----------|------------|
| **只有我** | `pinUserPeer: true`——所有非智能体的网关用户都会被映射到你的同伴名称。此设置会覆盖所有别名，因此仅在没有用户端身份需要独立同伴名称时才选择此选项。如果有多个智能体访问网关且每个都需要独立的同伴名称，则不要选择此选项，应保持 `pinUserPeer: false`，并通过 `userPeerAliases`（即 `[e]` 编辑器）来为它们建立映射 |
| **我和其他人**（共享历史） | `pinUserPeer: false` + `userPeerAliases`，用于将你的运行时 ID 映射到 `peerName`——你保留自己的历史记录，其他人则拥有独立的同伴名称 |
| **只有其他人** | `pinUserPeer: false`，可选参数 `runtimePeerPrefix`——每个用户都会拥有独立的同伴名称 |

如果希望直接设置这三个键值，可以在提示时选择 `[e]`。

解析器会从上到下尝试这些键值，第一个匹配到的即生效：`pinUserPeer` → `userPeerAliases[id]` → `runtimePeerPrefix + id` → 原始运行时 ID → `peerName` → 最后作为会话键的备用选项。

:::warning 取消绑定可能导致共享记忆丢失
将 `pinUserPeer` 从 `true` 改为 `false` 并不会迁移已有数据——那些存储在 `peerName` 下的记忆会保留原样，而平台用户则会被映射为全新的、空的同伴名称。为了保持自己的历史记录连续性，建议选择“共享历史”路径，这样你的运行时 ID 仍可以映射回 `peerName`。当设置向导检测到这种切换时，会自动为你推荐此选项。
:::

:::note 已废弃的键值
`pinPeerName` 是 `pinUserPeer` 的旧别名——目前仍会被读取以保持向后兼容性（当两个键值都设置时，`pinUserPeer` 优先生效），但不会被写入。重新运行设置向导会将该参数迁移为标准键值。
:::

## 观察模式（定向与统一）

Honcho 将对话视为同伴之间交换消息的过程。每个同伴都有两个观察开关，它们与 Honcho 的 `SessionPeerConfig` 设置是一一对应的：

| 开关 | 效果 |
|------|------|
| `observeMe` | Honcho 会根据该同伴发送的消息来构建关于它的描述 |
| `observeOthers` | 该同伴可以查看其他同伴发送的消息，从而支持跨同伴的推理 |

两个同伴 × 两个开关 = 四个标志位。`observationMode` 是一个简化的预设选项：| 预设值 | 用户标识标志 | AI标识标志 | 语义模式 |
|--------|-----------|----------|-----------|
| `"directional"`（默认值） | 我：开启，他人：开启 | 我：开启，他人：开启 | 完全双向观察模式。支持跨用户对话分析——即“基于用户的话语及AI的回复，AI能够了解用户哪些信息”。 |
| `"unified"` | 我：开启，他人：关闭 | 我：关闭，他人：开启 | 共享池语义模式——AI仅观察用户的消息，而用户仅对自己的模型进行建模。属于单观察者池模式。 |

如需实现针对单个用户的精细控制，可通过显式的`observation`块来覆盖预设值：

```json
"observation": {
  "user": { "observeMe": true,  "observeOthers": true },
  "ai":   { "observeMe": true,  "observeOthers": false }
}
```

## 常见模式

| 意图 | 配置参数 |
|------|----------|
| 完整观察（大多数用户） | `"observationMode": "directional"` |
| AI不应根据自身回复重新构建用户画像 | `"ai": {"observeMe": true, "observeOthers": false}` |
| 要求AI保持固定角色，禁止通过自我观察进行调整 | `"ai": {"observeMe": false, "observeOthers": true}` |

通过 [Honcho 控制面板](https://app.honcho.dev) 设置的服务器端参数会覆盖本地默认设置——Hermes会在会话启动时将这些参数同步回来。

## 工具

当Honcho作为内存提供者启用时，会有五种工具可供使用：

| 工具 | 用途 |
|------|------|
| `honcho_profile` | 读取或更新对方信息卡片——如需更新可传入`card`（事实列表），无需传入则用于读取 |
| `honcho_search` | 对上下文进行语义搜索——仅返回原始片段，不经过大语言模型生成内容 |
| `honcho_context` | 提供完整的会话上下文——包括摘要、结构化表示、信息卡片以及近期消息 |
| `honcho_reasoning` | 基于Honcho的大语言模型生成综合答案——可通过`reasoning_level`（minimal/low/medium/high/max）控制回答的深度 |
| `honcho_conclude` | 创建或删除结论——传入`conclusion`参数用于创建，传入`delete_id`参数用于删除（仅限个人身份信息） |

## CLI命令

`hermes honcho`子命令**仅在Honcho作为激活的内存提供者时才会被注册**（即`config.yaml`中配置了`memory.provider: honcho`）。在首次安装后，可通过`hermes memory setup honcho`直接配置Honcho（或运行`hermes memory setup`后从列表中选择）；之后再次调用命令时，`hermes honcho`子命令就会出现。

```bash
hermes memory setup honcho    # Configure Honcho directly (works before activation)
hermes honcho status          # Connection status, config, and key settings
hermes honcho setup           # Redirects to `hermes memory setup` (post-activation alias)
hermes honcho strategy        # Show or set session strategy (per-session/per-directory/per-repo/global)
hermes honcho peer            # Show or update peer names + dialectic reasoning level
hermes honcho mode            # Show or set recall mode (hybrid/context/tools)
hermes honcho tokens          # Show or set token budget for context and dialectic
hermes honcho identity        # Seed or show the AI peer's Honcho identity
hermes honcho sync            # Sync Honcho config to all existing profiles
hermes honcho peers           # Show peer identities across all profiles
hermes honcho sessions        # List known Honcho session mappings
hermes honcho map             # Map current directory to a Honcho session name
hermes honcho enable          # Enable Honcho for the active profile
hermes honcho disable         # Disable Honcho for the active profile
hermes honcho migrate         # Step-by-step migration guide from openclaw-honcho
```

## 从 `hermes honcho` 迁移

如果您之前使用的是独立的 `hermes honcho setup`：

1. 您现有的配置文件（`honcho.json` 或 `~/.honcho/config.json`）将保持不变  
2. 服务器端数据（记忆内容、推理结果、用户档案等）也将完整保留  
3. 只需在 config.yaml 中设置 `memory.provider: honcho` 即可重新启用该功能  

无需重新登录或重新配置。运行 `hermes memory setup` 并选择 “honcho”，向导会自动检测到您现有的配置。

## 完整文档

如需完整参考信息，请查看 [内存提供者 — Honcho](./memory-providers.md#honcho)。
