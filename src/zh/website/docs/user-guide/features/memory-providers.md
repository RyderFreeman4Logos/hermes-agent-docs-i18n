---
sidebar_position: 4
title: "Memory Providers"
description: "External memory provider plugins — Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory"
---

# 内存提供器

Hermes Agent 自带 8 个外部内存提供器插件，这些插件能够在内置的 MEMORY.md 和 USER.md 之外，为智能体提供持久化的、跨会话的知识存储能力。同一时间仅能启用**一个**外部提供器——内置内存会始终与其并行运行。

## 快速入门

```bash
hermes memory setup      # interactive picker + configuration
hermes memory status     # check what's active
hermes memory off        # disable external provider
```

您也可以通过 `hermes plugins` → Provider Plugins → Memory Provider 来选择当前活跃的内存提供器。或者直接在 `~/.hermes/config.yaml` 文件中手动设置：

```yaml
memory:
  provider: openviking   # or honcho, mem0, hindsight, holographic, retaindb, byterover, supermemory
```

## 工作原理

当内存提供器处于激活状态时，Hermes会自动执行以下操作：

1. **将提供器上下文**注入系统提示词中（即提供器所掌握的信息）
2. 在每个对话轮次开始前**预加载相关记忆内容**（后台进行，不会阻塞当前流程）
3. 在每次响应后**将对话轮次信息同步给提供器**
4. 在会话结束时**提取记忆内容**（针对支持该功能的提供器）
5. **将内置记忆的修改内容同步到外部提供器**
6. **添加提供器专用工具**，以便智能体能够搜索、存储和管理记忆

内置记忆（MEMORY.md / USER.md）将继续以与之前完全相同的方式运行。外部提供器则起到补充作用。

## 可用的提供器

### Honcho

这是一种原生支持跨会话用户建模的AI技术，具备辩证推理、会话级上下文注入、语义搜索以及持久化结论生成功能。当前的基础上下文除了包含用户信息与同伴卡片外，还加入了会话摘要，从而使智能体能够了解此前已讨论的内容。

| | |
|---|---|
| **最适合用于** | 需要跨会话上下文及实现用户-智能体对齐的多智能体系统 |
| **所需条件** | 安装 `pip install honcho-ai` 并获取[API密钥](https://app.honcho.dev)，或使用自托管实例 |
| **数据存储** | Honcho云服务或自托管方式 |
| **成本** | Honcho云服务按定价收费 / 自托管版本免费 |

**提供的工具（5个）：** `honcho_profile`（读取/更新同伴卡片）、`honcho_search`（语义搜索）、`honcho_context`（会话上下文——包括摘要、用户信息、同伴卡片及对话记录）、`honcho_reasoning`（由LLM生成的推理内容）、`honcho_conclude`（创建/删除结论）

**架构设计：** 采用双层上下文注入机制——基础层包含会话摘要、用户信息及同伴卡片，每隔 `contextCadence` 时间刷新一次；此外还有一层辩证补充层，用于生成LLM推理内容，每隔 `dialecticCadence` 时间刷新一次。该辩证层会根据是否存在基础上下文，自动选择适合冷启动阶段的提示词（通用用户信息）或基于会话上下文的提示词。

**三个相互独立的配置参数**可分别控制成本与推理深度：**

- `contextCadence`——基础层刷新的频率（即API调用频率）
- `dialecticCadence`——辩证层LLM运行的频率（即LLM调用频率）
- `dialecticDepth`——每次辩证层调用时进行的`.chat()`调用次数（1–3次，代表推理深度）

**设置向导：**
```bash
hermes memory setup        # select "honcho" — runs the Honcho-specific post-setup
```

旧的 `hermes honcho setup` 命令仍然可用（现在它会重定向到 `hermes memory setup`），但仅在选择 Honcho 作为活跃内存提供者之后才会被注册。

**配置文件位置：** `$HERMES_HOME/honcho.json`（针对特定配置文件）或 `~/.honcho/config.json`（全局配置）。配置文件的优先级顺序为：`$

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
<summary>最简版 honcho.json（自托管模式）</summary>

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
如果您之前使用过 `hermes honcho setup`，您的配置及所有服务器端数据都将保持完整。只需再次通过设置向导启用该功能，或手动设置 `memory.provider: honcho`，即可通过新系统重新激活。
:::

**多对等节点设置：**

Honcho 将对话视为对等节点之间的消息交换——每个 Hermes 配置文件对应一个用户对等节点和一个 AI 对等节点，所有节点共享同一个工作空间。该工作空间即为共享环境：用户对等节点在所有配置文件中都是通用的，而每个 AI 对等节点则拥有独立的身份。每个 AI 对等节点都会根据自身的观察结果生成独立的表示/卡片，因此对于同一用户而言，`coder` 配置文件会保持以代码为中心的特性，而 `writer` 配置文件则会侧重内容编辑功能。

对应关系如下：

| 概念 | 含义 |
|---------|------|
| **工作空间** | 共享环境。属于同一工作空间的所有 Hermes 配置文件都会看到相同的用户身份。 |
| **用户对等节点** (`peerName`) | 即人类用户。在工作空间内的所有配置文件中都是通用的。 |
| **AI 对等节点** (`aiPeer`) | 每个 Hermes 配置文件对应一个。主机密钥默认为 `hermes`；其他配置文件的密钥则为 `hermes.<profile>`。 |
| **观察结果** | 各对等节点间的开关机制，用于控制 Honcho 应该从哪些消息中提取信息。模式包括 `directional`（默认，四种模式均启用）或 `unified`（单一观察者池）。 |

### 新配置文件，全新的 Honcho 对等节点

```bash
hermes profile create coder --clone
```

`--clone` 选项会在 `honcho.json` 中创建一个 `hermes.coder` 类型的主机块，其配置包括 `aiPeer: "coder"`、共享的 `workspace`，以及继承自父节点的 `peerName`、`recallMode`、`writeFrequency`、`observation` 等参数。该 AI 对等体会在 Honcho 中立即被创建，因此早在第一条消息发送之前就已经存在。

### 对于已有的配置文件，可回填 Honcho 对等体信息

```bash
hermes honcho sync
```

它会扫描所有的 Hermes 配置文件，为那些尚未配置主机块的配置文件创建相应的主机块，同时从默认的 `hermes` 块中继承相关设置，并快速生成新的 AI 对等体。该操作具有幂等性——对于已存在主机块的配置文件会直接跳过处理。

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
| `observeMe` | Honcho 会根据该节点发送的消息构建其对应的表示模型 |
| `observeOthers` | 该节点会监听另一节点发送的消息（从而实现跨节点推理） |

通过 `observationMode` 可预设以下模式：

- **`"directional"`**（默认值）——四个开关均处于开启状态。实现完全的相互观察，支持跨节点对话式推理。
- **`"unified"`**——用户设置 `observeMe: true`，AI 设置 `observeOthers: true`，其余开关关闭。采用单一观察者机制；AI 仅能模拟用户行为而无法模拟自身，用户则仅能模拟自身行为。

通过 [Honcho 控制面板](https://app.honcho.dev) 设置的服务器端参数会覆盖本地默认设置，并在会话启动时同步回本地。

如需了解完整的观察模式参考信息，请参阅 [Honcho 文档页](./honcho.md#observation-directional-vs-unified)。

### 网关身份映射

上述对等节点模型适用于 CLI、TUI 以及桌面端会话，在这些场景中，每次对话最终都会对应到 `peerName`。而 [网关](../../developer-guide/gateway-internals.md) 则引入了第二个维度：用户会携带平台原生运行时 ID（如 Telegram UID、Discord snowflake、Slack 用户 ID），随后通过三个键来确定每个 ID 对应哪个对等节点。

| 键值 | 效果 |
|-----|------|
| `pinUserPeer: true` | 所有非智能代理类型的网关用户都会被统一映射为 `peerName`。此设置会优先生效，因此可覆盖所有其他别名——仅当无需为某个用户身份单独创建对等节点时才启用该选项 |
| `userPeerAliases` | 用于将特定的运行时 ID 映射到对应对等节点（例如 `{"7654321": "alice"}`）。该配置是处理不同身份标识的依据，包括那些拥有独立对等节点的智能代理 |
| `runtimePeerPrefix` | 为所有未映射的运行时 ID 添加前缀（如 `telegram_7654321`），以避免具有相同结构 ID 的不同平台之间发生冲突 |

在网关外部，这些键值不会产生任何影响。`hermes memory setup` 功能仅在检测到已连接的网关平台时才会提示用户输入这些参数。关于具体的解析规则及配置流程，请参阅 [Honcho 文档页](./honcho.md#gateway-identity-mapping)。

<details>
<summary>完整的 honcho.json 示例（多配置文件场景）</summary>

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

由字节跳动旗下Volcengine开发的上下文数据库，具备类似文件系统的知识层级结构、分层检索功能，还能自动将信息分类存储到6个不同类别中。

| | |
|---|---|
| **最佳适用场景** | 需要结构化浏览功能的自托管知识管理系统 |
| **依赖环境** | 需先执行 `pip install openviking`，并运行相应服务器 |
| **数据存储** | 支持自托管（本地或云端） |
| **成本** | 免费（开源项目，遵循AGPL-3.0许可证） |

**常用工具：** `viking_search`（语义搜索）、`viking_read`（分层展示：概要/概述/完整内容）、`viking_browse`（类似文件系统的导航功能）、`viking_remember`（存储事实信息）、`viking_add_resource`（导入URL或文档）

**设置方法：**
```bash
# Start the OpenViking server first
pip install openviking
openviking-server

# Then configure Hermes
hermes memory setup    # select "openviking"
# Or manually:
hermes config set memory.provider openviking
echo "OPENVIKING_ENDPOINT=http://localhost:1933" >> ~/.hermes/.env
# Authenticated servers should use a user/admin API key:
echo "OPENVIKING_API_KEY=..." >> ~/.hermes/.env
```

**核心特性：**  
- 分层上下文加载：L0（约100个标记）→ L1（约2000个标记）→ L2（完整上下文）  
- 会话保存时自动提取内存信息（包括配置文件、偏好设置、实体、事件、案例及模式）  
- 支持使用 `viking://` URI方案实现分层知识浏览  

在本地/可信模式下，需使用 `OPENVIKING_ACCOUNT` 和 `OPENVIKING_USER`；而 `OPENVIKING_AGENT` 则是Hermes在OpenViking中的对等体标识，用于实现基于对等体的内存共享。  

---

### Mem0  

基于服务器端的LLM事实提取工具，具备语义搜索、重排序及自动去重功能。  

| | |  
|---|---|  
| **最佳适用场景** | 无需手动管理内存——Mem0可自动完成数据提取 |  
| **所需条件** | 安装 `pip install mem0ai` 及API密钥 |  
| **数据存储** | Mem0云服务 |  
| **费用** | 按Mem0官方定价收费 |  

**相关工具：**  
- `mem0_profile`：查看所有已存储的内存数据  
- `mem0_search`：支持语义搜索与结果重排序  
- `mem0_conclude`：存储原始事实内容  

**配置方法：**
```bash
hermes memory setup    # select "mem0"
# Or manually:
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

**配置文件路径：** `$HERMES_HOME/mem0.json`

| 键值 | 默认值 | 说明 |
|-----|---------|-------------|
| `user_id` | `hermes-user` | 用户标识符 |
| `agent_id` | `hermes` | 智能体标识符 |

---

### Hindsight

具备知识图谱、实体解析及多策略检索功能的长期记忆系统。`hindsight_reflect` 工具可实现其他任何提供商都无法提供的跨内存信息整合功能，同时通过会话级文档跟踪自动保留完整的对话内容（包括工具调用记录）。

| | |
|---|---|
| **最佳适用场景** | 基于知识图谱的检索及实体关系分析 |
| **所需资源** | 云端：来自 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 的 API 密钥；本地：LLM API 密钥（如 OpenAI、Groq、OpenRouter 等） |
| **数据存储** | Hindsight 云服务或本地嵌入式 PostgreSQL |
| **成本** | 遵循 Hindsight 的云端定价标准，本地版本免费 |

**相关工具：** `hindsight_retain`（带实体提取功能的存储）、`hindsight_recall`（多策略搜索）、`hindsight_reflect`（跨内存信息整合）

**设置方法：**
```bash
hermes memory setup    # select "hindsight"
# Or manually:
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

设置向导会自动安装依赖项，且仅安装所选模式所需的组件（云端模式使用 `hindsight-client`，本地模式使用 `hindsight-all`）。系统要求 `hindsight-client >= 0.4.22`，若版本过旧，会在会话启动时自动升级。

**本地模式界面：** `hindsight-embed -p hermes ui start`

**配置文件路径：** `$HERMES_HOME/hindsight/config.json`

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `mode` | `cloud` | `cloud` 或 `local` |
| `bank_id` | `hermes` | 内存库标识符 |
| `recall_budget` | `mid` | 回忆详细程度：`low` / `mid` / `high` |
| `memory_mode` | `hybrid` | `hybrid`（上下文+工具）、`context`（仅自动注入上下文）、`tools`（仅工具） |
| `auto_retain` | `true` | 自动保留对话轮次 |
| `auto_recall` | `true` | 在每轮对话前自动回忆记忆内容 |
| `retain_async` | `true` | 在服务器端异步处理记忆保留操作 |
| `retain_context` | `Hermes Agent与用户之间的对话` | 保留记忆的上下文标签 |
| `retain_tags` | — | 应用于保留记忆的默认标签；会与每次调用时使用的工具标签合并 |
| `retain_source` | — | 可选，用于为保留记忆附加 `metadata.source` 元数据 |
| `retain_user_prefix` | `用户` | 自动保留的对话记录中用户发言前的标签 |
| `retain_assistant_prefix` | `助手` | 自动保留的对话记录中助手发言前的标签 |
| `recall_tags` | — | 用于筛选需要回忆的记忆的标签 |

如需完整的配置参考，请参阅 [插件README](https://github.com/NousResearch/hermes-agent/blob/main/plugins/memory/hindsight/README.md)。

---

### Holographic

基于本地SQLite事实存储库，支持FTS5全文本搜索、信任度评分功能，以及用于复合代数查询的HRR（Holographic Reduced Representations）技术。

| | |
|---|---|
| **适用场景** | 仅需本地内存存储且需高级检索功能，无需外部依赖 |
| **系统要求** | 无特殊要求（SQLite始终可用）。如需使用HRR代数功能，可选用NumPy库。 |
| **数据存储方式** | 本地SQLite |
| **成本** | 免费 |

**提供的工具：** `fact_store`（包含9种操作：添加、搜索、查询关联信息、推理、矛盾判断、更新、删除、列出），`fact_feedback`（用于评估信息是否有用，进而训练信任度评分）

**设置方式：**
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
- `reason` — 对多个实体进行组合式 AND 查询
- `contradict` — 自动检测矛盾事实
- 基于非对称反馈的信任度评分（有帮助则 +0.05，无帮助则 -0.10）

---

### RetainDB

一款具备混合搜索功能（向量检索 + BM25 + 重排）的云内存 API，支持 7 种内存类型，并采用增量压缩技术。

| | |
|---|---|
| **适用场景** | 已在使用 RetainDB 基础设施的团队 |
| **所需条件** | RetainDB 账户及 API 密钥 |
| **数据存储** | RetainDB 云平台 |
| **费用** | 每月 20 美元 |

**相关工具：** `retaindb_profile`（用户档案）、`retaindb_search`（语义搜索）、`retaindb_context`（与任务相关的上下文信息）、`retaindb_remember`（按类型和重要性存储记忆）、`retaindb_forget`（删除记忆）

**设置方式：**
```bash
hermes memory setup    # select "retaindb"
# Or manually:
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```

### ByteRover

通过 `brv` CLI 实现持久化内存功能——具备分层检索机制的层级化知识树（从模糊文本检索到基于大语言模型的搜索）。以本地存储为主，同时支持可选的云同步功能。

| | |
|---|---|
| **适用人群** | 希望通过 CLI 获得便携式、以本地存储为主的记忆系统的开发者 |
| **所需条件** | ByteRover CLI（可通过 `npm install -g byterover-cli` 安装，或访问[安装脚本](https://byterover.dev)） |
| **数据存储** | 本地存储（默认），或 ByteRover 云存储（可选同步） |
| **成本** | 本地使用免费，云服务需按 ByteRover 的定价标准收费 |

**常用工具：** `brv_query`（检索知识树）、`brv_curate`（存储事实、决策规则及模式）、`brv_status`（显示 CLI 版本信息及知识树统计数据）

**设置步骤：**
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
- 支持通过 SOC2 Type II 认证的云同步功能（可选）  

---

### Supermemory  

这是一种具备语义长期记忆功能的工具，支持通过用户配置文件进行语义检索、显性记忆管理，还可通过 Supermemory 图形 API 实现会话结束后的对话数据导入。  

| | |  
|---|---|  
| **最佳适用场景** | 基于用户配置文件的语义检索及会话级图形结构构建 |  
| **所需条件** | 安装 `pip install supermemory` + 获取 [API 密钥](https://supermemory.ai) |  
| **数据存储** | Supermemory 云平台 |  
| **费用** | 参见 Supermemory 的定价标准 |  

**相关工具：**  
- `supermemory_store`（用于保存显性记忆）  
- `supermemory_search`（基于语义相似度的检索功能）  
- `supermemory_forget`（可通过 ID 或最匹配查询来删除记忆）  
- `supermemory_profile`（用于维护持久化用户配置文件及近期上下文信息）  

**设置方法：**
```bash
hermes memory setup    # select "supermemory"
# Or manually:
hermes config set memory.provider supermemory
echo 'SUPERMEMORY_API_KEY=***' >> ~/.hermes/.env
```

**配置文件路径：** `$HERMES_HOME/supermemory.json`

| 键值 | 默认值 | 说明 |
|-----|---------|-------------|
| `container_tag` | `hermes` | 用于搜索和写入的容器标签。支持使用 `{identity}` 模板来设置基于用户身份的标签。 |
| `auto_recall` | `true` | 在每次对话轮次之前自动注入相关的记忆上下文。 |
| `auto_capture` | `true` | 在每次响应后保存经过处理的用户与助手的对话内容。 |
| `max_recall_results` | `10` | 最多可召回并整合到上下文中的条目数量。 |
| `profile_frequency` | `50` | 在首次对话轮次以及之后每隔 N 轮次插入用户档案信息。 |
| `capture_mode` | `all` | 默认情况下会跳过那些内容简短或无关紧要的对话轮次。 |
| `search_mode` | `hybrid` | 搜索模式：`hybrid`、`memories` 或 `documents`。 |
| `api_timeout` | `5.0` | SDK 请求及数据同步请求的超时时间。 |

**环境变量：** `SUPERMEMORY_API_KEY`（必需），`SUPERMEMORY_CONTAINER_TAG`（可覆盖配置文件中的值）。

**主要功能：**
- 自动上下文隔离——从捕获的对话内容中剔除已召回的记忆，从而避免记忆内容的递归污染。
- 全会话数据同步——在会话结束时一次性上传整个对话记录。
- 会话结束后的对话上传功能（上传至 `/v4/conversations`），以便在 Supermemory 中构建更完善的用户档案和知识图谱。
- 在首次对话轮次以及按设定间隔自动插入用户档案信息。
- **基于用户身份的容器隔离**——可在 `container_tag` 中使用 `{identity}` 格式（例如 `hermes-{identity}` → `hermes-coder`），从而为不同的 Hermes 用户档案独立管理记忆内容。
- **多容器模式**——通过启用 `enable_custom_container_tags` 并指定 `custom_containers` 列表，可使智能体在多个命名容器之间进行读写操作；不过自动执行的任务仍会在主容器上完成。

<details>
<summary>多容器模式示例</summary>

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

基于 Memori Cloud 构建的结构化长期记忆系统，具备上下文自动捕获功能、工具感知的对话上下文管理能力，同时还提供用于调取事实、摘要、使用额度、注册信息及反馈的专用工具。

| | |
|---|---|
| **最佳适用场景** | 支持由智能体控制的信息调取，同时可实现项目与会话的结构化归属管理 |
| **所需依赖** | `pip install hermes-memori` + `hermes-memori install` + [Memori API 密钥](https://app.memorilabs.ai/signup) |
| **数据存储** | Memori Cloud |
| **费用说明** | 见 Memori 定价方案 |

**相关工具：** `memori_recall`（检索长期记忆中的信息）、`memori_recall_summary`（获取摘要化上下文）、`memori_quota`（查询使用额度/配额）、`memori_signup`（请求发送注册邮件）、`memori_feedback`（提交集成相关反馈）

**设置步骤：**
```bash
pip install hermes-memori
hermes-memori install
hermes config set memory.provider memori
hermes memory setup
```

## 提供商对比

| 提供商 | 存储方式 | 费用 | 工具数量 | 依赖项 | 独特功能 |
|----------|---------|------|-------|-------------|----------------|
| **Honcho** | 云存储 | 付费 | 5 | `honcho-ai` | 对话式用户建模 + 会话级上下文管理 |
| **OpenViking** | 自托管 | 免费 | 5 | `openviking` + 服务器 | 文件系统层级结构 + 分层加载机制 |
| **Mem0** | 云存储 | 付费 | 3 | `mem0ai` | 服务器端大语言模型提取功能 |
| **Hindsight** | 云存储/本地存储 | 免费/付费 | 3 | `hindsight-client` | 知识图谱 + 反向合成技术 |
| **Holographic** | 本地存储 | 免费 | 2 | 无 | HRR代数模型 + 可信度评分系统 |
| **RetainDB** | 云存储 | 每月20美元 | 5 | `requests` | 差分压缩技术 |
| **ByteRover** | 本地存储/云存储 | 免费/付费 | 3 | `brv` CLI工具 | 预压缩提取功能 |
| **Supermemory** | 云存储 | 付费 | 4 | `supermemory` | 上下文隔离机制 + 会话图谱整合 + 多容器支持 |
| **Memori** | 云存储 | 免费/付费 | 5 | `hermes-memori` | 具有工具识别能力的记忆系统 + 结构化信息检索功能 |

## 配置文件隔离

每个提供商的数据都会根据[配置文件](/user-guide/profiles)实现隔离：

- **本地存储型提供商**（Holographic、ByteRover）会使用 `$HERMES_HOME/` 目录路径，且不同配置文件对应不同的路径
- **配置文件型提供商**（Honcho、Mem0、Hindsight、Supermemory）会将配置信息存储在 `$HERMES_HOME/` 目录下，因此每个配置文件拥有独立的凭证信息
- **云存储型提供商**（RetainDB）会自动根据配置文件生成对应的项目名称
- **环境变量型提供商**（OpenViking）则通过每个配置文件对应的 `.env` 文件来进行配置

## 自定义内存提供商的构建方法

如需了解如何创建自定义的内存提供商，请参阅[开发者指南：内存提供商插件](/developer-guide/memory-provider-plugin)。
