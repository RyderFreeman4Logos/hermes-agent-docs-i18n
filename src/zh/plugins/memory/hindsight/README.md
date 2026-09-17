# Hindsight Memory Provider

具备知识图谱、实体解析以及多策略检索功能的长期记忆系统。支持云端、本地嵌入式及本地外部三种运行模式。

## 需求条件

- **云端模式：** 需从 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 获取 API 密钥。
- **本地嵌入式模式：** 需拥有受支持的 LLM 服务提供商的 API 密钥（如 OpenAI、Anthropic、Gemini、Groq、OpenRouter、MiniMax、Ollama，或任何兼容 OpenAI 的接口）。嵌入生成与重排序操作均在本地完成，无需额外 API 密钥。
- **本地外部模式：** 需有一个可通过 HTTP 访问的正在运行的 Hindsight 实例（无论是基于 Docker 还是自托管方式）。

## 设置指南

```bash
hermes memory setup    # select "hindsight"
```

设置向导会通过 `uv` 自动安装依赖项，引导您完成配置，并提供**入门记忆模板**作为初始数据（该模板为常见智能体角色精心整理的一组设定/指令）——您可以选择跳过此步骤，而在尝试覆盖已配置的数据时，系统也会提前发出警告。

或者也可以手动操作（采用默认的云模式）：
```bash
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

### 云端模式

用于连接 Hindsight 云 API。需要从 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 获取 API 密钥。

### 本地嵌入模式

Hermes 会启动一个内置 PostgreSQL 的本地 Hindsight 守护进程。进行记忆提取与合成操作时需要 LLM API 密钥。该守护进程在首次使用时会在后台自动启动，若 5 分钟内无操作则会停止运行。

支持所有兼容 OpenAI 的 LLM 接口（如 llama.cpp、vLLM、LM Studio 等）——只需将提供者类型设置为 `openai_compatible` 并输入对应的基础 URL 即可。

守护进程启动日志：`~/.hermes/logs/hindsight-embed.log`
守护进程运行日志：`~/.hindsight/profiles/<profile>.log`

如需打开 Hindsight 网页界面（仅限本地嵌入模式）：
```bash
hindsight-embed -p hermes ui start
```

### 本地外部模式

该模式将插件指向您已运行的现有 Hindsight 实例（无论是 Docker 安装还是自托管版本等）。无需管理后台进程——只需提供 URL 及可选的 API 密钥即可。

## 配置文件

配置文件路径：`~/.hermes/hindsight/config.json`

### 连接设置

| 键值 | 默认值 | 说明 |
|-----|---------|-------------|
| `mode` | `cloud` | 可取值为 `cloud`、`local_embedded` 或 `local_external` |
| `api_url` | `https://api.hindsight.vectorize.io` | API 地址（适用于 cloud 和 local_external 模式） |

### 内存库设置

| 键值 | 默认值 | 说明 |
|-----|---------|-------------|
| `bank_id` | `hermes` | 内存库名称；当 `bank_id_template` 未设置或解析结果为空时，将使用此静态默认值 |
| `bank_id_template` | — | 用于动态生成内存库名称的可选模板。支持占位符：`{profile}`、`{workspace}`、`{platform}`、`{user}`、`{session}`。例如：`hermes-{profile}` 可按当前活跃的 Hermes 配置文件隔离不同内存库。若所有占位符均为空，则最终名称为 `hermes` |
| `bank_mission` | — | 用于指定推理时的任务类型（身份/框架设定）。通过 Banks API 实现相关功能 |
| `bank_retain_mission` | — | 决定哪些信息会被保留。同样通过 Banks API 控制其应用逻辑 |

### 回调设置

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `recall_budget` | `mid` | 回忆的全面程度：`low` / `mid` / `high` |
| `recall_prefetch_method` | `recall` | 自动回忆方式：`recall`（原始事实）或 `reflect`（LLM合成） |
| `recall_max_tokens` | `4096` | 回忆结果的最大token数 |
| `recall_max_input_chars` | `800` | 自动回忆时的最大输入查询长度 |
| `recall_prompt_preamble` | — | 用于为上下文中的回忆内容添加的自定义前缀 |
| `recall_tags` | — | 用于筛选记忆内容的标签 |
| `recall_tags_match` | `any` | 标签匹配模式：`any` / `all` / `any_strict` / `all_strict` |
| `recall_types` | `observation` | 回忆过程中呈现的事实类型（包括自动回忆及 `hindsight_recall` 工具生成的内容）。支持逗号分隔的字符串或JSON列表。**默认值已限制为仅 `observation`**（详见下文的“行为变更”部分）。若需同时包含原始事实，可设置为 `observation,world,experience` |
| `auto_recall` | `true` | 在每轮对话开始前自动回忆记忆内容 |
| `recall_sync` | `false` | 每轮对话时针对*当前*消息同步进行回忆（相关性更高，但会增加回忆延迟）。默认值为关闭：回忆在后台执行，并在下一轮对话时注入。 |
| `recall_indicator` | `true` | 当自动回忆功能注入记忆内容时，显示 `👁️ Hindsight — recalled N memories` 状态行。面向客户的智能体可将其关闭。 |

> **行为变更——`recall_types` 的默认值现已仅设为 `observation`。**
>
> 以往，召回功能会返回所有三种类型的事实。而现在它仅返回观察结果。
>
> 根据 [Hindsight 的文档](https://hindsight.vectorize.io/developer/observations) 的说明，观察结果 merupakan Hindsight 在原始事实之上构建的**整合型**知识层：这些基于证据且经过去重处理的信念会随着新事实的出现而不断优化，并附带证据数量与新鲜度指示。而原始的 `world` / `experience` 事实则是为这些观察结果提供支持的独立证据。在每轮对话中注入上下文时，观察结果能以更高的信息密度呈现每个标记的内容，同时避免了向模型输入已被单个观察结果概括的多个原始事实。
>
> 如需恢复更广泛的召回能力，可在 `~/.hermes/hindsight/config.json` 中将 `"recall_types"` 设置为 `"observation,world,experience"`（字符串或 JSON 列表形式）。此设置同时适用于**自动召回功能**和 `hindsight_recall` 工具——因为两者都会读取相同的 `recall_types` 设置（该工具的架构中不存在针对单次调用的 `types` 参数），因此限制默认值就会同时影响这两种功能。

### 保留

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `auto_retain` | `true` | 自动保留对话轮次 |
| `retain_async` | `true` | 在 Hindsight 服务器上异步处理保留操作 |
| `retain_every_n_turns` | `1` | 每 N 轮保留一次内容（1 表示每轮都保留） |
| `retain_context` | `Hermes Agent 与用户之间的对话` | 用于标识被保留内容的上下文标签 |
| `retain_tags` | — | 应用于被保留内容的默认标签；会与每次调用的工具标签合并 |
| `retain_source` | — | 可选字段，用于为被保留内容添加 `metadata.source` 标签（用于标识存储该内容的客户端，例如 `hermes`）。默认为空——除非手动设置，否则不会添加归属标签 |
| `retain_indicator` | `true` | 在保存对话轮次时显示 `👁️ Hindsight — 正在保存到内存中…` 的状态提示行。面向客户的智能体可关闭此功能 |
| `retain_user_prefix` | `User` | 自动保留的转录文本中用户发言前的标签 |
| `retain_assistant_prefix` | `Assistant` | 自动保留的转录文本中智能体发言前的标签 |

### 集成方式

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `memory_mode` | `hybrid` | 内存内容整合到智能体中的方式 |

**memory_mode 的取值：**
- `hybrid` — 自动注入上下文 + 向大语言模型提供相应工具
- `context` — 仅自动注入上下文，不提供任何工具
- `tools` — 仅提供工具，不自动注入上下文

### 本地嵌入式大语言模型 |

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `llm_provider` | `openai` | 可选值包括 `openai`、`anthropic`、`gemini`、`groq`、`openrouter`、`minimax`、`ollama`、`lmstudio`、`openai_compatible` |
| `llm_model` | 各提供商对应值 | 模型名称（例如 `gpt-4o-mini`、`qwen/qwen3.5-9b`） |
| `llm_base_url` | — | `openai_compatible` 模式下的接口地址（例如 `http://192.168.1.10:8080/v1`） |

LLM API 密钥以 `HINDSIGHT_LLM_API_KEY` 的形式存储在 `~/.hermes/.env` 文件中。

## 工具

在 `hybrid` 和 `tools` 两种内存模式下均可使用：

| 工具 | 描述 |
|------|-------------|
| `hindsight_retain` | 支持自动实体提取并存储信息；可可选地为每次调用设置 `tags` 标签 |
| `hindsight_recall` | 采用多种搜索策略（语义搜索 + 实体图搜索） |
| `hindsight_reflect` | 基于 LLM 的跨内存信息综合功能 |

## 环境变量

| 变量名 | 描述 |
|----------|-------------|
| `HINDSIGHT_API_KEY` | Hindsight Cloud 服务的 API 密钥 |
| `HINDSIGHT_LLM_API_KEY` | 本地模式下的 LLM API 密钥 |
| `HINDSIGHT_API_LLM_BASE_URL` | 本地模式下的 LLM 接口地址（例如 OpenRouter） |
| `HINDSIGHT_API_URL` | 可自定义的 API 接口地址 |
| `HINDSIGHT_BANK_ID` | 可自定义的数据库名称 |
| `HINDSIGHT_BUDGET` | 可自定义的检索预算 |
| `HINDSIGHT_MODE` | 可自定义的模式（`cloud`、`local_embedded`、`local_external`） |

## 客户端版本

需使用版本号不低于 `0.6.1` 的 `hindsight-client`。若检测到旧版本，插件会在会话启动时自动升级。
