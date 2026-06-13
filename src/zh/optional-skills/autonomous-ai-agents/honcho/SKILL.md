---
name: honcho
description: Configure and use Honcho memory with Hermes -- cross-session user modeling, multi-profile peer isolation, observation config, dialectic reasoning, session summaries, and context budget enforcement. Use when setting up Honcho, troubleshooting memory, managing profiles with Honcho peers, or tuning observation, recall, and dialectic settings.
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Honcho, Memory, Profiles, Observation, Dialectic, User-Modeling, Session-Summary]
    homepage: https://docs.honcho.dev
    related_skills: [hermes-agent]
prerequisites:
  pip: [honcho-ai]
---

# Hermes 的 Honcho Memory 功能

Honcho 提供基于人工智能的跨会话用户建模功能。它能够跨多次对话识别用户身份，为每个 Hermes 用户档案赋予独立的同伴标识，同时呈现统一的用户视图。

## 适用场景

- 部署 Honcho（云端或自托管）
- 排查记忆功能失效/同伴节点不同步的问题
- 构建多档案配置，使每个智能体拥有独立的 Honcho 同伴节点
- 调整观察范围、回忆能力、对话深度或输出频率等参数
- 了解五种 Honcho 工具的功能及其适用场景
- 配置上下文预算与会话摘要注入功能

## 设置指南

### 云端版本（app.honcho.dev）

```bash
hermes memory setup honcho
# select "cloud", paste API key from https://app.honcho.dev
```

### 自托管模式

```bash
hermes memory setup honcho
# select "local", enter base URL (e.g. http://localhost:8000)
```

参见：https://docs.honcho.dev/v3/guides/integrations/hermes#running-honcho-locally-with-hermes

### 验证

```bash
hermes honcho status    # shows resolved config, connection test, peer info
```

## 架构设计

### 基础上下文注入

当 Honcho 在系统提示语中注入上下文时（处于“混合模式”或“上下文检索模式”下），它会按以下顺序构建基础上下文模块：

1. **会话摘要**——对当前会话内容的简短总结（置于最前端，以便模型快速保持对话连贯性）
2. **用户画像**——Honcho 经过分析后形成的用户模型（包括偏好、事实及行为模式等信息）
3. **AI 对等体卡片**——该 Hermes 配置文件中 AI 对等体的身份标识

若存在历史会话，会话摘要会在每个对话轮次开始时由 Honcho 自动生成。这样无需重复展示完整历史记录，即可让模型快速进入工作状态。

### 冷启动/热启动提示语选择

Honcho 会自动在两种提示策略之间进行切换：

| 条件 | 策略 | 功能说明 |
|------|------|----------|
| 无历史会话或用户画像为空 | **冷启动** | 使用简化的引导提示语，跳过摘要注入环节，促使模型主动了解用户信息 |
| 已存在用户画像和/或会话历史 | **热启动** | 完整注入基础上下文（按摘要→用户画像→AI 对等体卡片的顺序），生成更丰富的系统提示语 |

无需手动配置此功能——系统会根据会话状态自动选择合适策略。

### 对等体机制

Honcho 将对话视为**对等体**之间的交互。每个会话中，Hermes 会创建两个对等体：

- **用户对等体**（`peerName`）：代表人类用户。Honcho 通过分析用户发送的消息来构建其用户画像。
- **AI 对等体**（`aiPeer`）：代表当前的 Hermes 实例。每个配置文件都会拥有独立的 AI 对等体，从而使智能体能够形成各自的独立认知。

### 观测功能

每个对等体都包含两个观测开关，用于控制 Honcho 应该学习哪些信息：

| 开关 | 功能说明 |
|------|----------|
| `observeMe` | 观测该对等体自身发送的消息（用于构建自我画像） |
| `observeOthers` | 观测其他对等体发送的消息（用于建立跨对等体间的理解） |

默认情况下，四个开关均为**开启**状态（实现完全的双向观测）。

可在 `honcho.json` 文件中为每个对等体单独配置这些参数：

```json
{
  "observation": {
    "user": { "observeMe": true, "observeOthers": true },
    "ai":   { "observeMe": true, "observeOthers": true }
  }
}
```

或者使用简写预设：

| 预设 | 用户 | AI | 使用场景 |
|--------|------|----|----------|
| `"directional"`（默认） | 我：开启，他人：开启 | 我：开启，他人：开启 | 多智能体模式，完整记忆保留 |
| `"unified"` | 我：开启，他人：关闭 | 我：关闭，他人：开启 | 单智能体模式，仅用户建模 |

在 [Honcho 控制面板](https://app.honcho.dev) 中进行的设置会在会话启动时同步回来——服务器端配置优先于本地默认设置。

### 会话

会话是消息和观察结果存储的作用范围。策略选项如下：

| 策略 | 行为 |
|--------|------|
| `per-directory`（默认） | 每个工作目录对应一个会话 |
| `per-repo` | 每个 Git 仓库根目录对应一个会话 |
| `per-session` | 每次运行 Hermes 都创建新的 Honcho 会话 |
| `global` | 所有目录共享同一个会话 |

可手动覆盖：`hermes honcho map my-project-name`

### 回忆模式

智能体访问 Honcho 内存的方式：

| 模式 | 是否自动注入上下文？ | 是否可用工具？ | 使用场景 |
|------|---------------------|-----------------|----------|
| `hybrid`（默认） | 是 | 是 | 由智能体决定何时使用工具而非自动上下文 |
| `context` | 是 | 否（隐藏） | 流量消耗极低，无需调用工具 |
| `tools` | 否 | 是 | 智能体可自主控制所有内存访问 |

## 三个相互独立的调节参数

Honcho 的辩证推理行为由三个独立维度控制。调整其中一个参数不会影响其他参数：

### 频率（何时）

控制辩证推理与上下文调用**发生的频率**。

| 参数键 | 默认值 | 描述 |
|-----|---------|-------------|
| `contextCadence` | `1` | 上下文 API 调用之间的最小轮次间隔 |
| `dialecticCadence` | `2` | 辩证推理 API 调用之间的最小轮次间隔，建议值为 1–5 |
| `injectionFrequency` | `every-turn` | 基础上下文注入方式为 `every-turn` 或 `first-turn` |

较高的频率值意味着辩证推理 LLM 的调用频率会降低。`dialecticCadence: 2` 表示每隔一轮才触发一次辩证推理；设置为 `1` 则每轮都会触发。

### 深度（多少轮）

控制 Honcho 对每个查询执行**多少轮**辩证推理。

| 参数键 | 默认值 | 范围 | 描述 |
|-----|---------|-------|-------------|
| `dialecticDepth` | `1` | 1-3 | 每个查询的辩证推理轮数 |
| `dialecticDepthLevels` | -- | 数组 | 可选参数，用于为每轮设置不同的深度级别（见下文） |

`dialecticDepth: 2` 表示 Honcho 会执行两轮辩证推理。第一轮生成初步答案，第二轮则对其进一步优化。

`dialecticDepthLevels` 允许您分别为每一轮设置独立的推理深度：

```json
{
  "dialecticDepth": 3,
  "dialecticDepthLevels": ["low", "medium", "high"]
}
```

如果未指定 `dialecticDepthLevels`，则各轮推理将采用基于 `dialecticReasoningLevel`（即基础级别）计算出的**按比例分配的深度层级**：

| 深度层级 | 迭代次数 |
|---------|----------|
| 1 | [基础] |
| 2 | [最小, 基础] |
| 3 | [最小, 基础, 低] |

这样一来，前几轮的推理成本较低，而最终合成阶段则会使用最大深度。

**会话启动时的深度设置。**在第一步输入之前，会话启动预热阶段会在后台执行完整配置的 `dialecticDepth` 次数。在对新的智能体进行单次迭代预热时，通常只能得到较为简略的输出——而多迭代预热则会在用户发出指令前完成多次审核/对齐流程。第一步会直接使用预热结果；如果预热未能及时完成，第一步则会回退为带有时间限制的同步调用。

### 级别（难度强度）

用于控制每轮辩证推理的**强度**。

| 参数键 | 默认值 | 描述 |
|-------|--------|------|
| `dialecticReasoningLevel` | `low` | 可选值为 `minimal`、`low`、`medium`、`high`、`max` |
| `dialecticDynamic` | `true` | 当设置为 `true` 时，模型可以将 `reasoning_level` 参数传递给 `honcho_reasoning`，从而覆盖每次调用的默认设置。设置为 `false` 时，则始终使用 `dialecticReasoningLevel`，模型设置的参数将被忽略 |

更高的级别能够生成更丰富的合成结果，但会在 Honcho 后端消耗更多计算资源。

## 多配置文件设置

每个 Hermes 配置文件都会拥有独立的 Honcho AI 智能体，同时共享同一个工作空间（用户上下文）。这意味着：

- 所有配置文件看到的都是相同的用户信息
- 每个配置文件会构建属于自己的 AI 身份及观察结果
- 一个配置文件生成的结论可通过共享工作空间被其他配置文件查看

### 创建带有 Honcho 智能体的配置文件

```bash
hermes profile create coder --clone
# creates host block hermes.coder, AI peer "coder", inherits config from default
```

`--clone` 参数在 Honcho 中的作用：
1. 在 `honcho.json` 文件中创建一个 `hermes.coder` 主机配置块；
2. 设置 `aiPeer: "coder"`（即对应的配置文件名称）；
3. 沿用默认值设置 `workspace`、`peerName`、`writeFrequency`、`recallMode` 等参数；
4. 立即在 Honcho 中创建该对应节点，确保在接收第一条消息之前该节点就已存在。

### 补充现有配置文件

```bash
hermes honcho sync    # creates host blocks for all profiles that don't have one yet
```

### 每个配置文件的独立设置

可覆盖主机块中的任何配置项：

```json
{
  "hosts": {
    "hermes.coder": {
      "aiPeer": "coder",
      "recallMode": "tools",
      "dialecticDepth": 2,
      "observation": {
        "user": { "observeMe": true, "observeOthers": false },
        "ai": { "observeMe": true, "observeOthers": true }
      }
    }
  }
}
```

## 工具

该智能体拥有 5 个双向 Honcho 工具（在“上下文回忆”模式下会隐藏）：

| 工具 | 是否调用 LLM？ | 成本 | 适用场景 |
|------|-------------|------|----------|
| `honcho_profile` | 否 | 极低 | 对话开始时快速获取事实概览，或快速查询姓名/角色/偏好设置 |
| `honcho_search` | 否 | 低 | 获取特定的历史事实以便自行推理——仅返回原始内容，不进行整合 |
| `honcho_context` | 否 | 低 | 完整的会话上下文快照：摘要、信息呈现形式、对方卡片以及最新消息 |
| `honcho_reasoning` | 是 | 中高 | 由 Honcho 的辩证推理引擎将自然语言问题转化为可处理的形式 | 
| `honcho_conclude` | 否 | 极低 | 编写或删除持久性结论；若需 AI 自我认知，可传入 `peer: "ai"` |

### `honcho_profile`
读取或更新对方卡片——即精心整理的关键信息（姓名、角色、偏好、沟通风格）。如需更新，请传入 `card: [...]`；如仅需读取则无需传入该参数。此操作不会调用 LLM。

### `honcho_search`
在存储的上下文中对特定对方进行语义搜索。返回按相关性排序的原始内容片段，不进行整合处理。默认长度为 800 个标记，最大为 2000 个。当您需要特定的历史事实以便自行推理而非获取整合后的答案时，此工具非常适用。

### `honcho_context`
来自 Honcho 的完整会话上下文快照——包括会话摘要、对方信息呈现形式、对方卡片以及最新消息。此操作不会调用 LLM。当您希望一次性查看 Honcho 对当前会话及对方的全部了解时，可使用此工具。

### `honcho_reasoning`
由 Honcho 的辩证推理引擎回答自然语言问题（在 Honcho 的后端调用 LLM）。成本较高，但输出质量更好。可通过传入 `reasoning_level` 参数控制推理深度：`minimal`（快速/低成本）→ `low` → `medium` → `high` → `max`（深入全面）。若不传入该参数，则使用默认设置（`low`）。此工具可用于深入理解用户的模式、目标或当前状态。

### `honcho_conclude`
编写或删除关于某方的持久性结论。如需创建结论，请传入 `conclusion: "..."`；如需删除结论（用于移除个人身份信息——Honcho 会逐步自动修正错误的结论，因此仅当涉及个人敏感信息时才需要手动删除），请传入 `delete_id: "..."`。必须恰好传入这两个参数中的一个。

### 双向对方目标指定

这 5 个工具均支持可选的 `peer` 参数：
- `peer: "user"`（默认值）——针对用户方对方操作
- `peer: "ai"` ——针对当前配置文件中的 AI 对方操作
- `peer: "<explicit-id>"` ——工作空间中的任意对方 ID

示例：
```
honcho_profile                        # read user's card
honcho_profile peer="ai"              # read AI peer's card
honcho_reasoning query="What does this user care about most?"
honcho_reasoning query="What are my interaction patterns?" peer="ai" reasoning_level="medium"
honcho_conclude conclusion="Prefers terse answers"
honcho_conclude conclusion="I tend to over-explain code" peer="ai"
honcho_conclude delete_id="abc123"    # PII removal
```

## Agent 使用模式

当 Honcho 内存处于激活状态时，Hermes 的使用指南。

### 对话开始时

```
1. honcho_profile                  → fast warmup, no LLM cost
2. If context looks thin → honcho_context  (full snapshot, still no LLM)
3. If deep synthesis needed → honcho_reasoning  (LLM call, use sparingly)
```

请勿在每个对话轮次都调用 `honcho_reasoning` 函数。自动注入机制已能负责持续更新上下文，只有当基础上下文无法提供所需的信息，且确实需要通过推理工具生成综合见解时，才应使用该功能。

### 当用户要求记住某些内容时

```
honcho_conclude conclusion="<specific, actionable fact>"
```

优秀结论示例：“更倾向于使用代码示例而非文字说明”，“截至2026年4月仍在从事Rust异步项目开发”  
较差结论示例：“用户提到了Rust”（过于模糊），“用户似乎具备技术背景”（这一信息已体现在用户画像中）

```
honcho_search query="<topic>"       → fast, no LLM, good for specific facts
honcho_context                       → full snapshot with summary + messages
honcho_reasoning query="<question>"  → synthesized answer, use when search isn't enough
```

### 何时使用 `peer: "ai"` 

可使用 AI 对等体功能来构建并查询智能体自身的自我认知信息：
- `honcho_conclude conclusion="I tend to be verbose when explaining architecture" peer="ai"` —— 自我修正
- `honcho_reasoning query="How do I typically handle ambiguous requests?" peer="ai"` —— 自我审计
- `honcho_profile peer="ai"` —— 查看自身的身份信息

### 何时不应调用工具 

在 `hybrid` 和 `context` 模式下，基础上下文（用户描述 + 身份卡 + 会话摘要）会在每个对话轮次之前自动注入。无需重新获取已注入的内容。仅在以下情况下才需调用工具：
- 需要基础上下文中未包含的信息
- 用户明确要求你调取或检查记忆内容
- 需要针对新内容撰写结论时

### 调用频率控制 

在工具端使用的 `honcho_reasoning` 功能与自动注入的推理过程具有相同的成本。在明确调用工具之后，自动注入的频率会重置——从而避免在同一轮次中重复计费。

## 配置参考 

配置文件路径：`$
