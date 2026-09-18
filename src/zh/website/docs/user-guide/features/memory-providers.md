---
sidebar_position: 4
title: "Memory Providers"
description: "External memory provider plugins — Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory"
---

# 内存提供器

Hermes Agent 自带 8 个外部内存提供器插件，这些插件能为代理提供持久化的、跨会话的知识存储能力，补充内置的 MEMORY.md 和 USER.md 的功能。同一时间**仅能**启用一个外部提供器——内置内存则会始终与其并行运行。

## 快速入门

```bash
hermes memory setup      # interactive picker + configuration
hermes memory status     # check what's active
hermes memory off        # disable external provider
```

您也可以通过 `hermes plugins` → Provider Plugins → Memory Provider 来选择当前激活的内存提供器。或者直接在 `~/.hermes/config.yaml` 文件中手动设置：

```yaml
memory:
  provider: openviking   # or honcho, mem0, hindsight, holographic, retaindb, byterover, supermemory
```

## 工作原理

当内存提供器处于激活状态时，Hermes会自动执行以下操作：

1. **将提供器上下文**注入系统提示词中（即提供器所掌握的信息）；
2. 在每次对话轮次开始前**预加载相关记忆内容**（后台执行，不会阻塞当前流程）；
3. 在每次响应之后将**对话轮次信息同步**给对应提供器；
4. 在会话结束时**提取记忆内容**（针对支持该功能的提供器）；
5. 将内置内存的修改操作**同步到外部提供器**；
6. **添加提供器专用工具**，以便智能体能够搜索、存储和管理记忆内容。

内置内存（MEMORY.md / USER.md）的功能依然保持不变，而外部提供器则起到补充作用。

## 可用的提供器

### Honcho

这是一种专为人工智能设计的跨会话用户建模方案，具备辩证推理、会话级上下文注入、语义搜索以及持久化结论生成等功能。当前的基础上下文除了包含用户信息与同伴卡片外，还加入了会话摘要，从而使智能体能够了解之前讨论过的内容。

| | |
|---|---|
| **最佳适用场景** | 需要跨会话上下文传递及实现用户与智能体对齐的多智能体系统 |
| **所需条件** | 安装 `pip install honcho-ai` 并获取 [API密钥](https://app.honcho.dev)，或部署自托管实例 |
| **数据存储** | Honcho云服务或自托管服务器 |
| **成本** | Honcho云服务按定价收费 / 自托管版本免费 |
**工具（5个）：** `honcho_profile`（读取/更新同伴卡片），`honcho_search`（语义搜索），`honcho_context`（会话上下文——包括摘要、表示形式、卡片及消息），`honcho_reasoning`（由大语言模型生成），`honcho_conclude`（创建/删除结论）。

**架构设计：** 采用双层上下文注入机制——底层包含会话摘要、表示形式及同伴卡片，按`contextCadence`间隔刷新；上层则为辩证补充层，包含大语言模型的推理内容，按`dialecticCadence`间隔刷新。该辩证层会根据是否存在底层上下文，自动选择冷启动提示词（通用用户信息）或热启动提示词（会话相关上下文）。

**三个相互独立的配置参数**可分别控制成本与推理深度：**

- `contextCadence`——底层上下文的刷新频率（即API调用频率）
- `dialecticCadence`——辩证层大语言模型的触发频率（即大语言模型调用频率）
- `dialecticDepth`——每次辩证层调用时进行的`.chat()`调用次数（1–3次，代表推理深度）

自动注入的辩证层还会根据查询长度动态调整推理层级（查询越长，推理越深入，最高上限为`reasoningLevelCap`）；详情请参阅[查询自适应推理层级](./honcho.md#query-adaptive-reasoning-level)。

**设置向导：**
```bash
hermes memory setup        # select "honcho" — runs the Honcho-specific post-setup
```

旧的 `hermes honcho setup` 命令仍然可用（目前它会重定向到 `hermes memory setup`），但仅在选择 Honcho 作为默认内存提供者之后才会被注册。

**无界面/远程机器**：对于没有浏览器但需要通过云方式认证的机器（如 SSH 连接的远程虚拟机），请在向导的认证方式提示处选择 **device**。CLI 会输出一个短代码及验证链接，只需在其他机器上的浏览器中打开该链接并确认即可完成设置，无需手动复制粘贴 API 密钥。当检测到本地没有可用的浏览器时，向导会自动选择此选项。

**配置文件**：分别为 `$HERMES_HOME/honcho.json`（本地配置文件）和 `~/.honcho/config.json`（全局配置文件）。配置文件的优先级为：`$/HERMES_HOME/honcho.json` > `~/.hermes/honcho.json` > `~/.honcho/config.json`。更多详情请参阅 [配置参考文档](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/honcho/README.md) 以及 [Honcho 集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

<details>
<summary>完整配置参考</summary>

| Key | Default | Description |
|-----|---------|-------------|
| `apiKey` | -- | API key from [app.honcho.dev](https://app.honcho.dev) |
| `baseUrl` | -- | Base URL for self-hosted Honcho |
| `peerName` | -- | User peer identity |
| `aiPeer` | host key | AI peer identity (one per profile) |
| `workspace` | host key | Shared workspace ID |
| `contextTokens` | `null` (uncapped) | Token budget for auto-injected context per turn. Truncates at word boundaries |
| `contextCadence` | `1` | Minimum turns between `context()` API calls (base layer refresh) |
| `dialecticCadence` | `2` | Minimum turns between `peer.chat()` LLM calls. Recommended 1–5. Only applies to `hybrid`/`context` modes |
| `dialecticDepth` | `1` | Number of `.chat()` passes per dialectic invocation. Clamped 1–3. Pass 0: cold/warm prompt, pass 1: self-audit, pass 2: reconciliation |
| `dialecticDepthLevels` | `null` | Optional array of reasoning levels per pass, e.g. `["minimal", "low", "medium"]`. Overrides proportional defaults |
| `dialecticReasoningLevel` | `'low'` | Base reasoning level: `minimal`, `low`, `medium`, `high`, `max` |
| `dialecticDynamic` | `true` | When `true`, model can override reasoning level per-call via tool param |
| `dialecticMaxChars` | `600` | Max chars of dialectic result injected into system prompt |
| `recallMode` | `'hybrid'` | `hybrid` (auto-inject + tools), `context` (inject only), `tools` (tools only) |
| `writeFrequency` | `'async'` | When to flush messages: `async` (background thread), `turn` (sync), `session` (batch on end), or integer N |
| `saveMessages` | `true` | Whether to persist messages to Honcho API |
| `observationMode` | `'directional'` | `directional` (all on) or `unified` (shared pool). Override with `observation` object |
| `messageMaxChars` | `25000` | Max chars per message (chunked if exceeded) |
| `dialecticMaxInputChars` | `10000` | Max chars for dialectic query input to `peer.chat()` |
| `sessionStrategy` | `'per-directory'` | `per-directory`, `per-repo`, `per-session`, `global` |
| `pinUserPeer` | `false` | Gateway only. When `true`, every non-agent gateway user collapses to `peerName`; the pin overrides all aliases |
| `userPeerAliases` | `{}` | Gateway only. Maps runtime IDs to peers (`{"7654321": "alice"}`). Many-to-one |
| `runtimePeerPrefix` | `""` | Gateway only. Namespaces unknown runtime IDs (`telegram_7654321`) when no alias matches |

</details>

<details>
<summary>最简版 honcho.json（云端环境）</summary>

```json
{
  "apiKey": "your-key-from-app.honcho.dev",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "peerName": "your-name",
      "workspace": "hermes"
    }
  }
}
```

</details>

<details>
<summary>最简版 honcho.json（自托管场景）</summary>

```json
{
  "baseUrl": "http://localhost:8000",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "peerName": "your-name",
      "workspace": "hermes"
    }
  }
}
```

</details>

:::提示 从 `hermes honcho` 迁移
如果您之前使用过 `hermes honcho setup`，您的配置及所有服务器端数据都将保持不变。只需再次通过设置向导启用该功能，或手动设置 `memory.provider: honcho`，即可在新系统中重新激活。
:::

**多对等节点设置：**

Honcho 将对话视为对等节点之间的消息交流——每个 Hermes 配置文件对应一个用户对等节点和一个 AI 对等节点，它们共同共享一个工作空间。该工作空间即为共享环境：用户对等节点在所有配置文件中都是通用的，而每个 AI 对等节点则拥有独立的身份。每个 AI 对等节点都会根据自身的观察结果生成独立的表示/卡片，因此对于同一用户而言，`coder` 配置文件会保持以代码为中心的特质，而 `writer` 配置文件则会侧重内容编辑功能。

对应关系如下：

| 概念 | 含义 |
|---------|------|
| **工作空间** | 共享环境。属于同一工作空间的所有 Hermes 配置文件都会看到相同的用户身份。 |
| **用户对等节点** (`peerName`) | 即人类用户。在工作空间内的所有配置文件中都是通用的。 |
| **AI 对等节点** (`aiPeer`) | 每个 Hermes 配置文件对应一个。主机密钥为 `hermes`（默认值）；其他配置文件的密钥则为 `hermes.<profile>`。 |
| **观察结果** | 各对等节点间的开关机制，用于控制 Honcho 应该从哪些消息中提取信息。可选 `directional`（默认值，四种模式全部启用）或 `unified`（单一观察者池模式）。 |

### 新配置文件，全新的 Honcho 对等节点

```bash
hermes profile create coder --clone
```

`--clone` 选项会在 `honcho.json` 中创建一个 `hermes.coder` 类型的主机配置块，其参数包括 `aiPeer: "coder"`、共享的 `workspace`，以及继承自父配置的 `peerName`、`recallMode`、`writeFrequency`、`observation` 等属性。该 AI 对等体会在 Honcho 中立即被创建，因此早在第一条消息处理之前就已存在。

### 对于已有的配置文件，可回填 Honcho 对等体信息

```bash
hermes honcho sync
```

它会扫描所有的 Hermes 配置文件，为那些尚未配置主机块的配置文件创建相应的主机块，同时从默认的 `hermes` 块中继承相关设置，并迅速创建新的 AI 对等体。该操作具有幂等性——对于已经存在主机块的配置文件会直接跳过处理。

### 每个配置文件的独立观测功能

每个主机块均可独立覆盖观测配置。例如，在以代码处理为主的配置文件中，AI 对等体会对用户进行观测，但不会对自己进行建模：

```json
"hermes.coder": {
  "aiPeer": "coder",
  "observation": {
    "user": { "observeMe": true, "observeOthers": true },
    "ai":   { "observeMe": false, "observeOthers": true }
  }
}
```

**观察模式切换（每个对等节点对应一组设置）：**

| 切换项 | 效果 |
|--------|------|
| `observeMe` | Honcho 会根据该节点发送的消息构建其对应的模型表示 |
| `observeOthers` | 该节点会观察另一节点发送的消息（从而实现跨节点推理） |

通过 `observationMode` 可预设以下模式：

- **`"directional"`**（默认值）——四个开关全部开启。实现完全的相互观察，支持跨节点辩证推理。
- **`"unified"`**——用户启用 `observeMe: true`，AI 启用 `observeOthers: true`，其余开关关闭。采用单一观察者机制：AI 仅能建模用户而非自身，用户则仅能对自己的对等节点进行建模。

通过 [Honcho 控制面板](https://app.honcho.dev) 设置的服务器端切换选项会优先于本地默认设置，并在会话启动时同步回本地。

如需完整的观察模式参考信息，请参阅 [Honcho 文档页面](./honcho.md#observation-directional-vs-unified)。

### 网关身份映射

上述对等节点模型适用于 CLI、TUI 以及桌面端会话，在这些场景中，每次对话最终都会关联到 `peerName`。而 [网关](../../developer-guide/gateway-internals.md) 则引入了第二个维度：用户会携带平台原生的运行时标识（如 Telegram UID、Discord snowflake、Slack 用户 ID），随后通过三个关键参数来确定每个标识对应哪个对等节点。

| 键值 | 效果 |
|-----|------|
| `pinUserPeer: true` | 所有非代理类型的网关用户都会被简化为 `peerName`。该设置会优先于其他别名生效，因此仅当无需为特定用户身份单独配置对等体时才应使用它 |
| `userPeerAliases` | 将特定的运行时 ID 映射到对应的对等体（例如 `{"7654321": "alice"}`）。该配置用于处理不同的身份标识——包括那些各自拥有独立对等体的代理节点 |
| `runtimePeerPrefix` | 为所有未映射的运行时 ID 添加前缀（如 `telegram_7654321`），从而避免具有相同结构 ID 的不同平台之间发生冲突 |

在网关外部，这些键值不会产生任何作用。`hermes memory setup` 命令仅在检测到已连接的网关平台时才会提示用户输入这些参数。有关解析规则及配置流程的详细信息，请参阅 [Honcho 页面](./honcho.md#gateway-identity-mapping)。

<details>
<summary>完整的 honcho.json 示例（多配置文件）</summary>

```json
{
  "apiKey": "your-key",
  "workspace": "hermes",
  "peerName": "eri",
  "hosts": {
    "hermes": {
      "enabled": true,
      "aiPeer": "hermes",
      "workspace": "hermes",
      "peerName": "eri",
      "recallMode": "hybrid",
      "writeFrequency": "async",
      "sessionStrategy": "per-directory",
      "observation": {
        "user": { "observeMe": true, "observeOthers": true },
        "ai": { "observeMe": true, "observeOthers": true }
      },
      "dialecticReasoningLevel": "low",
      "dialecticDynamic": true,
      "dialecticCadence": 2,
      "dialecticDepth": 1,
      "dialecticMaxChars": 600,
      "contextCadence": 1,
      "messageMaxChars": 25000,
      "saveMessages": true
    },
    "hermes.coder": {
      "enabled": true,
      "aiPeer": "coder",
      "workspace": "hermes",
      "peerName": "eri",
      "recallMode": "tools",
      "observation": {
        "user": { "observeMe": true, "observeOthers": false },
        "ai": { "observeMe": true, "observeOthers": true }
      }
    },
    "hermes.writer": {
      "enabled": true,
      "aiPeer": "writer",
      "workspace": "hermes",
      "peerName": "eri"
    }
  },
  "sessions": {
    "/home/user/myproject": "myproject-main"
  }
}
```

</details>

请参阅[配置参考文档](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/honcho/README.md)以及[Honcho集成指南](https://docs.honcho.dev/v3/guides/integrations/hermes)。

---

### OpenViking

由字节跳动旗下Volcengine开发的上下文数据库，具备类似文件系统的知识层级结构、分层检索功能，并能自动将记忆内容分类为6个类别。

| | |
|---|---|
| **最佳适用场景** | 需要结构化浏览功能的自托管知识管理系统 |
| **前置要求** | OpenViking已初始化、验证并通过，且处于运行状态 |
| **数据存储** | 自托管（本地或云端） |
| **成本** | 免费（开源，AGPL-3.0许可证） |

**工具（6个）：** `viking_search`（语义搜索）、`viking_read`（分层读取：概要/概述/完整内容）、`viking_browse`（文件系统导航）、`viking_remember`（存储事实信息）、`viking_forget`（通过精确的`viking://` URI删除记忆文件）、`viking_add_resource`（导入URL或文档）**

**设置步骤：**
```bash
# Prepare OpenViking first
openviking-server init
openviking-server doctor
openviking-server

# Then configure Hermes
hermes memory setup    # select "openviking"
# Or manually:
hermes config set memory.provider openviking
```

`hermes memory setup`功能允许重复使用或复制`~/.openviking/ovcli.conf`中的连接参数值。手动设置时，则会使用当前激活配置文件的`.env`文件；默认配置文件的路径为`~/.hermes/.env`，而对于自定义配置文件，则需使用`~/.hermes/profiles/<profile>/.env`。

```text
OPENVIKING_ENDPOINT=http://127.0.0.1:1933
# OPENVIKING_API_KEY=...
# OPENVIKING_ACCOUNT=default
# OPENVIKING_USER=default
```

OpenViking服务器的配置保存在`ov.conf`文件中（可通过`--config`、`OPENVIKING_CONFIG_FILE`或`~/.openviking/ov.conf`路径访问）。客户端连接相关设置则存储在`ovcli.conf`文件中（通过`OPENVIKING_CLI_CONFIG_FILE`或`~/.openviking/ovcli.conf`路径访问）。

**主要特性：**
- 分层上下文加载：L0层（约100个标记）→ L1层（约2000个标记）→ L2层（完整上下文）
- 会话保存时自动提取内存数据，包括用户配置、偏好设置、实体信息、事件记录、案例数据及模式规则
- 支持使用`viking://` URI方案实现分层知识浏览

在本地/可信模式下，系统会使用`OPENVIKING_ACCOUNT`和`OPENVIKING_USER`参数。虽然可以指定对等方身份，但默认情况下Hermes不会发送对等方ID，而是将内存数据直接写入`viking://user/<用户名>/memories/...`路径下。设置过程中也不会要求输入对等方ID。若需为不同助手创建独立的上下文，可在`config.yaml`文件中设置`memory.openviking.agent: work-assistant`。

已存在的非空对等方配置将保留其针对该对等方的写入数据及检索功能。这包括在关联的OpenViking配置文件中设置的`OPENVIKING_AGENT`、`actor_peer_id`或旧版的`agent_id`。现有内存数据不会被移动或删除。在没有指定对等方ID的情况下，系统默认会搜索当前用户的内存数据以及同一OpenViking账户下的其他对等方内存数据。内存数据的排序规则和返回数量限制将决定最终展示哪些数据。若要恢复旧的对等方级写入功能，可设置`memory.openviking.agent: hermes`。在此变更之前以用户级别写入的内存数据仍将保留在原处并可被检索，该设置仅影响后续的新数据写入，不会改变现有内存的数据位置。

在通过 OpenViking 发送请求时，Hermes 会设置 `User-Agent: openviking-memory-hermes/<version>`。这一标准的工具标识符不包含任何与特定用户相关的信息，也不会因此产生额外的请求。

---

### Mem0

一种基于服务器端的大型语言模型事实提取工具，具备语义搜索、重排序及自动去重功能。提供三种连接模式：**平台模式**（Mem0 云服务）、**自托管控制台模式**（通过 Docker 运行的 Mem0 服务器），以及 **OSS 模式**（在您自己的大型语言模型与向量存储系统中集成 Mem0 功能）。

| | |
|---|---|
| **适用场景** | 无需手动管理记忆数据——Mem0 可自动完成事实提取工作 |
| **所需条件** | `pip install mem0ai` + API 密钥（平台模式），正在运行的 Mem0 服务器（自托管控制台模式），或大型语言模型与向量存储系统（OSS 模式） |
| **数据存储位置** | Mem0 云服务（平台模式）、您自己的 Mem0 服务器（自托管控制台模式），或程序内部内存（OSS 模式） |
| **成本** | 遵循 Mem0 的定价标准（平台模式）/ 免费（自托管或 OSS 模式） |

**工具（4个）：** `mem0_search`（语义搜索；平台模式下可选重排序功能，默认关闭）、`mem0_add`（存储原始事实数据）、`mem0_update`（通过 ID 进行更新）、`mem0_delete`（通过 ID 进行删除）

**平台模式设置步骤：**
```bash
hermes memory setup    # select "mem0" → "Platform"
# Or manually:
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

**设置（OSS）：**
```bash
hermes memory setup    # select "mem0" → "Open Source (self-hosted)"
# Or via flags:
hermes memory setup mem0 --mode oss --oss-llm openai --oss-llm-key sk-... --oss-vector qdrant
```

无需写入文件即可预览：
```bash
hermes memory setup mem0 --mode oss --oss-llm-key sk-... --dry-run
```

**设置（自托管控制面板）：** 连接到您通过 Docker 运行的 Mem0 服务器（即该控制面板的 REST API）：

```bash
hermes memory setup    # select "mem0" → "Self-hosted server"
# Or via flags:
hermes memory setup mem0 --mode selfhosted --host http://localhost:8888 --api-key your-admin-api-key
```

或者手动配置——可通过环境变量来实现：

```bash
echo "MEM0_HOST=http://localhost:8888" >> ~/.hermes/.env
echo "MEM0_API_KEY=your-admin-api-key" >> ~/.hermes/.env
```

或在 `mem0.json` 中：

```json
{ "host": "http://localhost:8888", "api_key": "your-admin-api-key" }
```

该插件通过 `X-API-Key` 进行身份验证，并使用服务器的 `/search` 和 `/memories` 接口。`api_key` 参数为可选项（仅当服务器设置为 `AUTH_DISABLED` 时才可省略）。请勿设置 `mode: oss` —— 因为其优先级高于 `host` 参数。

**配置文件：** `$HERMES_HOME/mem0.json`（用于设置行为参数）。仅有密钥 `MEM0_API_KEY` 需存储在 `~/.hermes/.env` 文件中。

| 键值 | 默认值 | 说明 |
|-----|---------|-------------|
| `mode` | `platform` | `platform`（Mem0 Cloud）或 `oss`（自主管理、进程内运行） |
| `host` | — | 自托管 Mem0 服务器的 URL（来自 Docker 控制面板）。通过 HTTP 并结合 `X-API-Key` 发送请求；不可与 `mode: oss` 同时使用 |
| `user_id` | `hermes-user` | 用户标识符 |
| `agent_id` | `hermes` | Agent 标识符 |
| `rerank` | `false` | 重新排序搜索结果以提高相关性（仅适用于 `platform` 模式） |
| `sync_max_chars` | `450` | 在每次发送消息进行事实提取之前，对单条消息的字符数进行的限制，截断点位于最后一个句子结尾。默认值适用于 512 令牌的嵌入模型（如 Ollama 的 `bge-small-zh-v1.5`、`all-minilm`）；若使用 8k 令牌的嵌入模型（如 `text-embedding-3-small`、`jina-embeddings-v3` 或 `bge-m3`），建议将此值调高（例如设为 `6000`） |

**OSS 支持的提供方：**

| 组件 | 提供方 |
|-----------|---------|
| 大语言模型 | openai、ollama |
| 嵌入模型 | openai、ollama |
| 向量存储 | qdrant（本地/服务器版）、pgvector |

**切换模式：** 重新运行命令 `hermes memory setup mem0 --mode <platform|selfhosted|oss>`，或直接编辑 `mem0.json` 文件。

---

### 后见之明

具备知识图谱、实体解析以及多策略检索功能的长期记忆系统。`hindsight_reflect` 工具可实现其他任何提供商都无法提供的跨内存信息整合功能。该系统通过会话级文档跟踪，自动保留完整的对话记录（包括工具调用信息）。

| | |
|---|---|
| **最佳适用场景** | 基于知识图谱的检索及实体关系分析 |
| **所需条件** | 云端：来自 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 的 API 密钥；本地：LLM API 密钥（如 OpenAI、Groq、OpenRouter 等） |
| **数据存储** | Hindsight Cloud 或本地嵌入式 PostgreSQL |
| **成本** | 遵循 Hindsight 的云端定价标准，本地部署则免费 |

**相关工具：** `hindsight_retain`（结合实体提取功能进行存储）、`hindsight_recall`（多策略搜索）、`hindsight_reflect`（跨内存信息整合）

**设置方式：**
```bash
hermes memory setup    # select "hindsight"
# Or manually:
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

设置向导会自动安装所需依赖项，且仅安装所选模式所需的组件（云端模式使用 `hindsight-client`，本地模式使用 `hindsight-all`）。系统要求 `hindsight-client` 版本至少为 0.4.22；若版本过旧，将在会话启动时自动升级。

**本地模式界面启动方式：** `hindsight-embed -p hermes ui start`

**配置文件路径：** `$HERMES_HOME/hindsight/config.json`

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `mode` | `cloud` | 模式，可选 `cloud` 或 `local` |
| `bank_id` | `hermes` | 内存库标识符 |
| `recall_budget` | `mid` | 回忆详细程度：`low` / `mid` / `high` |
| `memory_mode` | `hybrid` | 内存处理模式，可选 `hybrid`（上下文+工具）、`context`（仅自动注入）或 `tools`（仅工具） |
| `auto_retain` | `true` | 是否自动保留对话轮次 |
| `auto_recall` | `true` | 是否在每轮对话前自动回忆记忆内容 |
| `retain_async` | `true` | 是否在服务器端异步处理保留操作 |
| `retain_context` | `Hermes Agent与用户之间的对话` | 保留记忆内容的上下文标签 |
| `retain_tags` | — | 应用于保留记忆内容的默认标签；会与每次调用时使用的工具标签合并 |
| `retain_source` | — | 可选字段，用于为保留的记忆内容添加 `metadata.source` 标签 |
| `retain_user_prefix` | `用户` | 自动保留的对话记录中用户发言前的标签 |
| `retain_assistant_prefix` | `助手` | 自动保留的对话记录中助手发言前的标签 |
| `recall_tags` | — | 用于筛选需要回忆的记忆内容的标签 |
如需完整的配置参考，请参阅[插件README](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/hindsight/README.md)。

---

### Holographic

基于本地SQLite的事实存储引擎，支持FTS5全文搜索、信任度评分功能，以及用于组合代数查询的HRR（Holographic Reduced Representations）技术。

| | |
|---|---|
| **适用场景** | 仅需本地内存且需高级检索功能，无外部依赖 |
| **依赖要求** | 无需额外依赖（SQLite始终可用）。如需使用HRR代数功能，可选装NumPy。 |
| **数据存储** | 本地SQLite |
| **成本** | 免费 |

**工具功能：** `fact_store`（9种操作：添加、搜索、查询关联信息、推理、矛盾检测、更新、删除、列表展示）；`fact_feedback`（用于评估信息是否有用，进而训练信任度评分）

**配置步骤：**
```bash
hermes memory setup    # select "holographic"
# Or manually:
hermes config set memory.provider holographic
```

**配置文件：** 位于 `plugins.hermes-memory-store` 下的 `config.yaml`

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite 数据库路径 |
| `auto_extract` | `false` | 会话结束时自动提取事实 |
| `default_trust` | `0.5` | 默认信任度分数（范围：0.0–1.0） |

**独特功能：**
- `probe` — 针对特定实体的代数检索（获取关于某人/某物的所有事实）
- `reason` — 跨多个实体的组合式 AND 查询
- `contradict` — 自动检测矛盾事实
- 基于非对称反馈的信任度评分（有帮助则 +0.05，无帮助则 -0.10）

---

### RetainDB

一款支持混合搜索（向量检索 + BM25 + 重排序）的云内存 API，提供 7 种内存类型及增量压缩功能。

| | |
|---|---|
| **适用场景** | 已在使用 RetainDB 基础设施的团队 |
| **所需条件** | RetainDB 账户 + API 密钥 |
| **数据存储** | RetainDB 云平台 |
| **费用** | 每月 20 美元 |

**工具（10 个）：** `retaindb_profile`（用户配置文件）、`retaindb_search`（语义搜索）、`retaindb_context`（与任务相关的上下文）、`retaindb_remember`（按类型和重要性存储信息）、`retaindb_forget`（删除记忆），以及文件操作工具：`retaindb_upload_file`、`retaindb_list_files`、`retaindb_read_file`、`retaindb_ingest_file`、`retaindb_delete_file`

**设置方式：**
```bash
hermes memory setup    # select "retaindb"
# Or manually:
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```

### ByteRover

通过 `brv` CLI 实现持久化内存功能——采用分层知识树结构，并支持多级检索（从模糊文本到基于大语言模型的搜索）。以本地存储为主，同时可选云同步功能。

| | |
|---|---|
| **适用人群** | 希望通过 CLI 获得便携式、以本地存储为主的记忆系统的开发者 |
| **所需条件** | ByteRover CLI（可通过 `npm install -g byterover-cli` 安装，或访问[安装脚本](https://byterover.dev)） |
| **数据存储** | 本地存储（默认），或 ByteRover 云存储（可选同步） |
| **成本** | 本地使用免费，云服务需按 ByteRover 的定价标准收费 |

**常用工具：** `brv_query`（检索知识树）、`brv_curate`（存储事实、决策规则及模式）、`brv_status`（显示 CLI 版本信息及知识树统计数据）

**设置方法：**
```bash
# Install the CLI first
curl -fsSL https://byterover.dev/install.sh | sh

# Then configure Hermes
hermes memory setup    # select "byterover"
# Or manually:
hermes config set memory.provider byterover
```

**核心功能：**  
- 自动预压缩提取（在上下文压缩导致信息丢失之前保存关键洞察）  
- 知识树存储于 `$HERMES_HOME/byterover/` 目录下（基于用户配置文件）  
- 支持经过 SOC2 Type II 认证的云同步功能（可选）  

---

### Supermemory  

这是一种具备语义长期记忆功能的工具，支持通过用户配置文件进行语义检索、提供显性记忆管理工具，并可通过 Supermemory 图形 API 实现会话结束后的对话导入功能。  

| | |  
|---|---|  
| **最佳适用场景** | 基于用户配置文件的语义检索及会话级图形结构构建 |  
| **所需条件** | 需安装 `pip install supermemory`，并获取 [云 API 密钥](http://app.supermemory.ai/integrations?connect=hermes)，或部署 [自托管服务器](https://supermemory.ai/docs/self-hosting/overview) |  
| **数据存储方式** | Supermemory 云端存储或自托管存储 |  
| **成本** | 遵循 Supermemory 的云服务定价标准 / 自托管版本免费 |  

**相关工具：**  
- `supermemory_store`（用于保存显性记忆）  
- `supermemory_search`（基于语义相似度的检索功能）  
- `supermemory_forget`（可通过 ID 或最匹配查询来删除记忆）  
- `supermemory_profile`（持久化用户配置文件及近期上下文信息）  

**设置方式：**
```bash
hermes memory setup    # select "supermemory"
# Or manually:
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

自托管部署：

```bash
npx supermemory local
```

在运行 `hermes memory setup` 之前，请先在 `$HERMES_HOME/supermemory.json` 文件中设置 `base_url`：

```json
{
  "base_url": "http://localhost:6767"
}
```

接着运行 `hermes memory setup`，并输入本地服务器输出的 API 密钥。首先配置端点可确保连接探测也保持在本地进行。

**配置文件路径：** `$HERMES_HOME/supermemory.json`

| 键值 | 默认值 | 说明 |
|-----|---------|-------------|
| `base_url` | `https://api.supermemory.ai` | 托管版或自托管版 Supermemory 的 API 端点。其优先级高于 `SUPERMEMORY_BASE_URL`。 |
| `container_tag` | `hermes` | 用于搜索和写入的容器标签。支持使用 `{identity}` 模板来设置基于用户身份的标签。 |
| `auto_recall` | `true` | 在每轮对话开始前自动注入相关的记忆上下文。 |
| `auto_capture` | `true` | 在每次响应后保存经过处理的用户与助手的对话内容。 |
| `max_recall_results` | `10` | 最多可提取并整合到上下文中的项目数量。 |
| `profile_frequency` | `50` | 在第一轮对话以及之后每隔 N 轮对话时，插入用户档案信息。 |
| `capture_mode` | `all` | 默认情况下会跳过那些内容简短或无关紧要的对话轮次。 |
| `search_mode` | `hybrid` | 搜索模式：`hybrid`、`memories` 或 `documents`。 |
| `api_timeout` | `5.0` | SDK 操作以及数据导入请求的超时时间。 |

**环境变量：** `SUPERMEMORY_API_KEY`（必需）、`SUPERMEMORY_BASE_URL`（当未配置 `base_url` 时的兼容性备选值）、`SUPERMEMORY_CONTAINER_TAG`（可覆盖配置文件中的设置）。

端点的优先级顺序为：`supermemory.json` → `SUPERMEMORY_BASE_URL` → `https://api.supermemory.ai`。SDK 操作、设置/状态探测以及对话数据导入都会使用最终确定的端点。

**主要功能：**
- 自动上下文隔离——从已记录的对话轮次中移除相关记忆，避免记忆污染的递归发生  
- 全会话一次性上传——在会话结束时将整个对话内容一次性发送  
- 会话结束后的对话上传功能（发送至 `/v4/conversations`），便于在 Supermemory 中构建更完善的用户画像及关联图谱  
- 端到端自托管路由——SDK、探测请求以及对话上传请求均使用相同配置的端点  
- 在首次对话轮次及按可配置间隔向用户画像中注入相关数据  
- **基于用户画像的容器隔离**——在 `container_tag` 中使用 `{identity}` 标识（例如 `hermes-{identity}` → `hermes-coder`），实现针对不同 Hermes 用户画像的记忆隔离  
- **多容器模式**——通过启用 `enable_custom_container_tags` 并指定 `custom_containers` 列表，允许智能体在多个命名容器之间进行读写操作；自动处理功能则仍运行在主容器上  

<details>  
<summary>多容器模式示例</summary>  
</details>

```json
{
  "container_tag": "hermes",
  "enable_custom_container_tags": true,
  "custom_containers": ["project-alpha", "shared-knowledge"],
  "custom_container_instructions": "Use project-alpha for coding context."
}
```

</details>

**支持渠道：** [Discord](https://supermemory.link/discord) · [support@supermemory.com](mailto:support@supermemory.com)

### Memori

基于 Memori Cloud 构建的结构性长期记忆系统，具备上下文自动捕获功能、工具感知的对话上下文支持，以及用于调取事实、摘要、使用额度、注册信息及反馈的专用工具。

| | |
|---|---|
| **适用场景** | 支持由智能体控制的信息调取，并具备结构化的任务与会话归属标识 |
| **依赖项** | `pip install hermes-memori` + `hermes-memori install` + [Memori API密钥](https://app.memorilabs.ai/signup) |
| **数据存储** | Memori Cloud |
| **费用** | 见 Memori 定价说明 |

**相关工具：** `memori_recall`（检索长期记忆内容）、`memori_recall_summary`（生成摘要式上下文）、`memori_quota`（查询使用额度/限额）、`memori_signup`（请求发送注册邮件）、`memori_feedback`（提交集成使用反馈）

**设置方式：**
```bash
pip install hermes-memori
hermes-memori install
hermes config set memory.provider memori
hermes memory setup
```

## 提供商对比

| 提供商 | 存储方式 | 费用 | 工具数量 | 依赖项 | 独特功能 |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | 云端 | 付费 | 5 | `honcho-ai` | 辩证式用户建模 + 会话级上下文管理 |
| **OpenViking** | 自托管 | 免费 | 6 | `openviking` + 服务器 | 文件系统层级结构 + 分层加载机制 |
| **Mem0** | 云端/自托管 | 免费/付费 | 4 | `mem0ai` | 服务器端大语言模型提取功能 + 自托管/OSS运行模式 |
| **Hindsight** | 云端/本地 | 免费/付费 | 3 | `hindsight-client` | 知识图谱 + 反射式综合分析 |
| **Holographic** | 本地 | 免费 | 2 | 无 | HRR代数模型 + 可信度评分系统 |
| **RetainDB** | 云端 | 每月20美元 | 10 | `requests` | 差分压缩技术 |
| **ByteRover** | 本地/云端 | 免费/付费 | 3 | `brv` CLI | 预压缩提取功能 |
| **Supermemory** | 云端/自托管 | 免费/付费 | 4 | `supermemory` | 上下文隔离机制 + 会话图谱整合 + 多容器支持 |
| **Memori** | 云端 | 免费/付费 | 5 | `hermes-memori` | 具有工具感知能力的记忆系统 + 结构化信息检索 |

## 配置文件隔离

每个提供商的数据均通过[配置文件](/user-guide/profiles)实现独立隔离：

- **本地存储提供者**（如 Holographic、ByteRover）会使用 `$HERMES_HOME/` 路径，且该路径会因不同配置文件而有所差异。  
- **配置文件提供者**（如 Honcho、Mem0、Hindsight、Supermemory）会将配置信息存储在 `$HERMES_HOME/` 下，因此每个配置文件都能拥有独立的凭证。  
- **云存储提供者**（如 RetainDB）会自动生成与特定配置文件对应的项目名称。  
- **环境变量提供者**（如 OpenViking）则通过各配置文件对应的 `.env` 文件来进行配置。  

## 构建内存提供者  

如需了解如何创建自定义的内存提供者，请参阅[开发者指南：内存提供者插件](/developer-guide/memory-provider-plugin)。
