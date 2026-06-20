# Hindsight Memory Provider

具备知识图谱、实体解析以及多策略检索功能的长期记忆系统。支持云端、本地嵌入式及本地外部三种使用模式。

## 需求条件

- **云端模式：** 需从 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 获取 API 密钥。
- **本地嵌入式模式：** 需拥有受支持的 LLM 服务提供商的 API 密钥（如 OpenAI、Anthropic、Gemini、Groq、OpenRouter、MiniMax、Ollama 或任何兼容 OpenAI 的接口）。嵌入生成与重排排序操作均在本地完成，无需额外 API 密钥。
- **本地外部模式：** 需有一台正在运行且可通过 HTTP 访问的 Hindsight 实例（基于 Docker 或自行托管）。

## 设置指南

```bash
hermes memory setup    # select "hindsight"
```

设置向导会通过 `uv` 自动安装依赖项，并引导您完成配置流程。

或者也可以手动操作（采用默认值的云模式）：
```bash
hermes config set memory.provider hindsight
echo "HINDSIGHT_API_KEY=your-key" >> ~/.hermes/.env
```

### 云端模式

用于连接 Hindsight 云 API。需要从 [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io) 获取 API 密钥。

### 本地嵌入模式

Hermes 会启动一个内置 PostgreSQL 的本地 Hindsight 守护进程。进行内存提取与合成操作时需要相应的 LLM API 密钥。该守护进程在首次使用时会在后台自动启动，若 5 分钟内无操作则会停止运行。

支持所有兼容 OpenAI 的 LLM 接口（如 llama.cpp、vLLM、LM Studio 等）——只需将提供者类型设置为 `openai_compatible` 并输入对应的基础地址即可。

守护进程启动日志路径：`~/.hermes/logs/hindsight-embed.log`
守护进程运行日志路径：`~/.hindsight/profiles/<profile>.log`

如需打开 Hindsight Web UI（仅限本地嵌入模式）：
```bash
hindsight-embed -p hermes ui start
```

### 本地外部模式

该模式将插件指向您已运行的现有 Hindsight 实例（无论是基于 Docker 还是自托管部署）。无需管理后台服务——只需提供 URL 及可选的 API 密钥即可。

## 配置文件

配置文件路径：`~/.hermes/hindsight/config.json`

### 连接设置

| 键值 | 默认值 | 描述 |
|------|--------|------|
| `mode` | `cloud` | 模式选择，可选值为 `cloud`、`local_embedded` 或 `local_external` |
| `api_url` | `https://api.hindsight.vectorize.io` | API 地址（适用于 `cloud` 和 `local_external` 模式） |

### 内存库设置

| 键值 | 默认值 | 描述 |
|------|--------|------|
| `bank_id` | `hermes` | 内存库名称；若未设置 `bank_id_template` 或其返回空值，则使用此静态默认名称 |
| `bank_id_template` | — | 用于动态生成内存库名称的模板。支持占位符：`{profile}`、`{workspace}`、`{platform}`、`{user}`、`{session}`。例如：`hermes-{profile}` 可按当前活跃的 Hermes 配置文件隔离不同内存库。若所有占位符均为空，则名称简化为 `hermes`。<br/>`bank_mission` | — | 用于指定推理任务（即用于“反思”推理的身份/框架），通过 Banks API 实现。<br/>`bank_retain_mission` | — | 决定哪些信息会被保留，同样通过 Banks API 控制。 |

### 回忆功能设置

| 键值 | 默认值 | 描述 |
|------|--------|------|
| `recall_budget` | `mid` | 回忆的详尽程度，可选值为 `low`、`mid`、`high` |
| `recall_prefetch_method` | `recall` | 自动回忆方式，可选值为 `recall`（直接返回原始事实）或 `reflect`（通过大语言模型进行综合生成） |
| `recall_max_tokens` | `4096` | 回忆结果的最大Token数 |
| `recall_max_input_chars` | `800` | 自动回忆时输入查询的最大字符数 |
| `recall_prompt_preamble` | — | 为回忆出的内容添加的定制前缀 |
| `recall_tags` | — | 用于筛选记忆内容的标签 |
| `recall_tags_match` | `any` | 标签匹配模式，可选值为 `any`、`all`、`any_strict`、`all_strict` |
| `recall_types` | `observation` | 回忆功能可展示的事实类型（包括自动回忆及 `hindsight_recall` 工具）。支持以逗号分隔的字符串或 JSON 列表形式。**默认值已限制为仅 `observation` 类型**（详见下文“行为变化”）。若需同时包含原始事实，可设置为 `observation,world,experience`。<br/>`auto_recall` | `true` | 在每轮对话开始前自动回忆相关记忆 |

> **行为变化 —— `recall_types` 的默认值现已改为仅 `observation`。**
>
> 旧版本中，回忆功能会返回全部三种类型的事实；现在则仅返回观察结果。
>
> 根据 [Hindsight 的文档](https://hindsight.vectorize.io/developer/observations)，观察结果是指 Hindsight 在原始事实基础上构建的**整合型**知识层：这些知识基于证据去重后形成，会随着新事实的出现而不断优化，并附带证据数量和新鲜度指示。而原始的 `world`/`experience` 类型事实则是构成观察结果的各个独立证据。在每轮对话中注入上下文时，观察结果每 Token 所承载的信息更密集，且无需向模型提供已被单个观察结果概括的多个原始事实。
>
> 如需恢复全面的回忆功能，可在 `~/.hermes/hindsight/config.json` 中将 `recall_types` 设置为 `"observation,world,experience"`（字符串或 JSON 列表形式）。此设置同时适用于自动回忆功能及 `hindsight_recall` 工具——因为两者读取的均为相同的 `recall_types` 设置（该工具的架构中不存在针对单次调用的 `types` 参数），因此默认值的限制会同时影响这两种方式。

### 保留设置

| 键值 | 默认值 | 描述 |
|------|--------|------|
| `auto_retain` | `true` | 自动保留对话轮次记录 |
| `retain_async` | `true` | 在 Hindsight 服务器上异步处理保留操作 |
| `retain_every_n_turns` | `1` | 每 N 轮对话后保留一次记录（1 表示每轮都保留） |
| `retain_context` | `Hermes Agent与用户之间的对话` | 保留记忆内容的上下文标签 |
| `retain_tags` | — | 默认应用于保留记忆的标签，会与每次调用工具时添加的标签合并 |
| `retain_source` | — | 可选字段，用于为保留的记忆附加 `metadata.source` 标识 |
| `retain_user_prefix` | `User` | 自动保留的对话记录中用户发言前的标签 |
| `retain_assistant_prefix` | `Assistant` | 自动保留的对话记录中助手发言前的标签 |

### 集成方式设置

| 键值 | 默认值 | 描述 |
|------|--------|------|
| `memory_mode` | `hybrid` | 内存如何融入智能体工作流程 |

**`memory_mode` 的可选值：**
- `hybrid` —— 同时实现自动上下文注入，并向大语言模型提供专用工具
- `context` —— 仅自动注入上下文，不提供任何工具
- `tools` —— 仅提供专用工具，不进行自动上下文注入

### 本地嵌入式大语言模型设置

| 键值 | 默认值 | 描述 |
|------|--------|------|
| `llm_provider` | `openai` | 支持的模型提供商，可选值为 `openai`、`anthropic`、`gemini`、`groq`、`openrouter`、`minimax`、`ollama`、`lmstudio`、`openai_compatible` |
| `llm_model` | 各提供商对应值 | 具体模型名称，例如 `gpt-4o-mini`、`qwen/qwen3.5-9b` |
| `llm_base_url` | — | 适用于 `openai_compatible` 类型提供商的端点地址，例如 `http://192.168.1.10:8080/v1` |

大语言模型的 API 密钥存储在 `~/.hermes/.env` 文件中，键名为 `HINDSIGHT_LLM_API_KEY`。

## 工具功能

在 `hybrid` 和 `tools` 两种内存模式下均可使用以下工具：

| 工具名称 | 描述 |
|----------|------|
| `hindsight_retain` | 支持自动实体提取的功能，可用于存储信息；同时允许为每次调用指定自定义标签 |
| `hindsight_recall` | 采用多策略搜索方式（语义搜索 + 实体图搜索） |
| `hindsight_reflect` | 基于大语言模型的跨内存库综合生成功能 |

## 环境变量

| 变量名 | 描述 |
|--------|------|
| `HINDSIGHT_API_KEY` | Hindsight Cloud 服务的 API 密钥 |
| `HINDSIGHT_LLM_API_KEY` | 本地模式所需的大语言模型 API 密钥 |
| `HINDSIGHT_API_LLM_BASE_URL` | 本地模式下大语言模型的基础地址（如 OpenRouter 的地址） |
| `HINDSIGHT_API_URL` | 可用于覆盖默认的 API 端点地址 |
| `HINDSIGHT_BANK_ID` | 可用于覆盖默认的内存库名称 |
| `HINDSIGHT_BUDGET` | 可用于覆盖默认的回忆功能详细程度设置 |
| `HINDSIGHT_MODE` | 可用于覆盖默认的模式选择（`cloud`、`local_embedded`、`local_external`） |

## 客户端版本要求

该插件需要 `hindsight-client >= 0.6.1` 版本。若检测到版本过低，插件会在会话启动时自动升级。
