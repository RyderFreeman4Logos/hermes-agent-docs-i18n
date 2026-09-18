---
sidebar_position: 3
---

# 模型配置

Hermes 使用两种类型的模型槽位：

- **主模型**——代理用于进行思考的核心模型。每条用户消息、每个工具调用循环以及所有流式响应都会经过该模型处理。
- **辅助模型**——代理用于处理的一些小型任务，如上下文压缩、视觉分析（图像处理）、网页摘要生成、审批评分、MCP工具路由、会话标题生成以及技能搜索等。每种辅助模型都有独立的槽位，且可以单独进行配置覆盖。

本页面介绍了如何通过控制面板配置这两种模型。如果您更喜欢使用配置文件或命令行界面，请跳转到文末的[其他配置方式](#alternative-methods)。若想在本地机器而非云服务提供商上运行模型，请参阅[本地模型](/user-guide/local-models)。

:::提示 最快捷方案：Nous Portal
[Nous Portal](/user-guide/features/tool-gateway) 允许用户通过一个订阅账户获取300多种模型。在首次安装时，只需运行 `hermes setup --portal` 即可一次性登录并设置Nous作为服务提供商。使用 `hermes portal info` 可以查看当前已配置的模型信息。

- 使用Portal订阅服务的用户还能享受**按令牌计费的服务提供商9折优惠**。
:::

:::note `model:` 结构 —— 空字符串与映射值
在全新安装的情况下，自带的默认配置中 `model` 的值为 `""`（即空字符串，表示“尚未配置”）。首次运行 `hermes setup` 或 `hermes model` 后，该键会立即升级为包含 `provider`、`default`、`base_url` 和 `api_mode` 子键的映射结构——这一结构在本页面以及 [`profiles.md`](./profiles.md) / [`configuration.md`](./configuration.md) 中均有展示。如果您在 `config.yaml` 中看到空字符串，只需运行 `hermes model`（或点击控制面板中的 **Change** 按钮），Hermes 便会自动将其转换为字典格式。
:::

## 模型页面

打开控制面板，点击侧边栏中的 **Models**。页面会显示两个部分：

1. **模型设置** —— 位于顶部面板，用于将模型分配到对应槽位。
2. **使用情况分析** —— 以排序后的卡片形式展示选定时间段内曾运行过会话的所有模型，同时显示令牌数量、成本以及能力标识。

![模型页面概览](/img/docs/dashboard-models/overview.png)

最顶端的卡片即为 **模型设置** 面板。主行始终显示代理在新建会话时会调用的模型。点击 **Change** 可打开选择器。

## 设置默认模型

点击“默认模型”行上的 **Change** 按钮：

![模型选择器对话框](/img/docs/dashboard-models/picker-dialog.png)

选择器包含两列内容：

- **左侧**——已通过认证的提供方。此处仅显示您已配置的提供方（即设置了 API 密钥、已完成 OAuth 认证，或被定义为自定义端点的那些）。如果某个提供方未显示，请前往 **Keys** 页面并添加其凭证。
- **右侧**——所选提供方的精选模型列表。这些是 Hermes 为该提供方推荐的智能体模型，而非原始的 `/models` 列表（在 OpenRouter 中，该列表包含 400 多种模型，涵盖文本转语音、图像生成以及重排序功能等）。

在过滤框中输入内容，即可按提供方名称、标识符或模型 ID 进行筛选。

选定一个模型后点击 **Switch**，Hermes 会将其写入 `~/.hermes/config.yaml` 文件的 `model` 部分。**此操作仅适用于新会话**——您已打开的任何聊天窗口将继续使用最初选定的模型。若要即时更换当前聊天的模型，可在该聊天窗口中使用 `/model` 命令。

### 会话中的模型切换与上下文警告

当您在**正在进行的会话中**切换模型时（通过 Herm TUI 模型选择器、`hermes` CLI，或 Telegram/Discord 上的 `/model` 命令），Hermes 会评估您的**下一条消息**是否需要针对新模型对应的上下文窗口进行**预处理压缩**。如果该会话的上下文压缩阈值已接近或超过该模型的阈值（详见 [上下文压缩](./configuration.md#context-compression)），系统会在切换回复中显示警告——该警告与针对高资源消耗模型发出的通知使用相同的 `warning_message` 路径。尽管如此，模型切换仍会立即生效；压缩操作会在模型回复之前、即**用户发送的第一条消息之后**执行。

:::warning 会话中途切换会重置提示词缓存  
提示词缓存是按照处理请求的模型来区分的，因此一旦在对话过程中更换模型——无论是通过显式的 `/model` 切换、[自动回退机制](./features/fallback-providers.md)，还是将[凭证池](./features/credential-pools.md)切换到其他账户——下一条消息就会以全额输入令牌费用重新读取整个对话历史，而无法使用缓存的（约优惠75–90%）费用。在长时间会话中，这种一次性重新读取的成本可能会超过两种模型之间每令牌的费用差异。可在必要时进行切换，但建议在对话初期或新会话开始后立即操作。  
:::

### 无人值守数据训练版本  

带有 `-contributor` 后缀的模型（例如 `muse-spark-1.2-contributor`、`muse-spark-1.3-contributor`）价格较低，因为供应商可能会利用您的提示词和回复内容来训练模型。交互式模型选择界面始终会显示确认提示。而像看板工作进程和定时任务代理这类非交互式启动方式则无法进行此类确认，因此会被直接拒绝。  

如果您同意让模型使用无人值守工作负载中的数据来进行训练，请留下明确的确认记录：

```bash
hermes config set security.allow_data_training_tiers_noninteractive true
```

每次在无人值守模式下启动时，Hermes 仍会显示完整的数据策略警告信息及确认密钥，因此工作节点日志中会保留审计追踪记录。此设置无法屏蔽与高成本模型或提供商路由相关的警告，也无法替代交互式确认提示。如需取消该功能，请使用命令 `hermes config unset security.allow_data_training_tiers_noninteractive`。

## 设置辅助模型

点击 **Show auxiliary** 可查看 11 个任务槽位：

![辅助面板展开状态](/img/docs/dashboard-models/auxiliary-expanded.png)

所有辅助任务的默认值为 `auto`，这意味着 Hermes 也会尝试使用您的主模型来处理该任务。如果该路径不可用或出现容量限制类故障，系统将依次按照任务特定的 `auxiliary.<task>.fallback_chain` 设置、主模型的 `fallback_providers`/`fallback_model` 设置，以及 Hermes 内置的辅助模型发现流程进行处理。若希望为某些次要任务选用成本更低或速度更快的模型，可对特定任务进行覆盖设置。

### 常见覆盖设置方式

| Task | When to override |
|---|---|
| **Title Gen** | When title latency or cost matters more than matching the main model. Pin a known-good flash model, or set `auxiliary.title_generation.prefer_fast_model: true` to let Hermes choose the provider's fast tier. |
| **Vision** | When your main model lacks vision support. Point it at `google/gemini-2.5-flash` or `gpt-4o-mini`. |
| **Compression** | When you're burning reasoning tokens on Opus/M2.7 just to summarize context. A fast chat model does the job at 1/50th the cost. |
| **Approval** | For `approval_mode: smart` — a fast/cheap model (haiku, flash, gpt-5-mini) decides whether to auto-approve low-risk commands. Expensive models here are waste. |
| **Web Extract** | When you use `web_extract` heavily. Same logic as compression — summarization doesn't need reasoning. |
| **Skills Hub** | `hermes skills search` uses this. Usually fine at `auto`. |
| **MCP** | MCP tool routing. Usually fine at `auto`. |
| **Triage Specifier** | Routes the Kanban triage specifier (`hermes kanban specify`) that expands a rough one-liner into a concrete spec. A cheap, capable model works well. |
| **Kanban Decomposer** | Routes Kanban task decomposition — splits a triage task into a graph of child tasks for specialist profiles. |
| **Profile Describer** | Routes profile-description generation (`hermes profile describe --auto` / the dashboard auto-generate button). Short, cheap call. |
| **Curator** | Routes the curator skill-usage review pass. Can run for minutes on reasoning models, so a cheaper aux model is often worthwhile. |

### 单任务覆盖设置

点击任意辅助任务行上的**更改**按钮。系统会打开相同的选项选择器，操作流程也一致——选择提供商和模型，然后点击切换按钮。该行内容将更新为显示`提供商 · 模型`，而非`auto (use main model)`。

### 将所有设置重置为自动模式

如果您进行了过度调整并希望重新开始，可点击辅助任务区域顶部的**将所有设置重置为自动模式**。此时所有任务都将恢复使用主模型。

## “用作”快捷功能

页面上的每个模型卡片都配有**用作**下拉菜单。这是一条快速路径——选择您在分析数据中看到的模型，点击**用作**，即可一键将其分配到主任务槽或任意特定的辅助任务中：

![Use as dropdown](/img/docs/dashboard-models/use-as-dropdown.png)

该下拉菜单包含以下选项：

- **主模型**——与直接点击主任务行上的更改按钮效果相同。
- **所有辅助任务**——将该模型同时分配到全部11个辅助任务槽中。当您希望所有辅助任务都使用成本较低的闪存模型时，此选项非常实用。
- **单个任务选项**——如视觉处理、网页提取、压缩等。每个任务当前所分配的模型会标有`current`字样。

当前已被分配了任务的卡片会显示`main`或`aux · <任务>`标签，这样您就能一目了然地看到历史模型分别被应用在了哪些任务中。

## 保存到`config.yaml`的内容

通过控制面板保存设置时，Hermes会将相关配置写入`~/.hermes/config.yaml`文件，具体内容如下：

**主模型：**
```yaml
model:
  provider: openrouter
  default: anthropic/claude-opus-4.7
  base_url: ''        # cleared on provider switch
  api_mode: chat_completions
```

**辅助功能覆盖（示例——在 Gemini-Flash 上使用视觉功能）：**
```yaml
auxiliary:
  vision:
    provider: openrouter
    model: google/gemini-2.5-flash
    base_url: ''
    api_key: ''
    timeout: 120
    extra_body: {}
    download_timeout: 30
```

**辅助功能：自动模式（默认值）：**
```yaml
auxiliary:
  compression:
    provider: auto
    model: ''
    base_url: ''
    # ... other fields unchanged
```

当同时设置 `provider: auto` 和 `model: ''` 时，Hermes 会使用该任务对应的默认模型来处理请求；不过，如果主路由无法处理相应的辅助调用，系统仍会遵循预设的回退策略。

针对特定任务的可选回退链则存储在同一个辅助任务目录下：

```yaml
auxiliary:
  title_generation:
    provider: auto
    model: ''
    fallback_chain:
      - provider: openrouter
        model: inclusionai/ring-2.6-1t:free
```

当未指定 `fallback_chain` 时，`auto` 模式会先使用顶层的 `fallback_providers` 链，然后再启用内置的辅助发现链。

## 各提供程序的请求选项

提供程序条目（位于 `providers:` 字典中的 `providers.<name>`，或旧版 `custom_providers` 列表中的项）支持一系列参数，用于控制 Hermes 与端点之间的通信方式：

**`extra_headers`** — 用于为发送至该提供程序基础 URL 的每个 LLM 请求添加额外的 HTTP 标头。这些标头会在 URL/配置文件默认值及用户自定义标头之后被应用，因此即便发生凭据更换或客户端重建，它们依然有效。该选项适用于 Cloudflare Access 服务令牌、代理认证或自定义承载方案等场景。

```yaml
providers:
  my-gateway:
    api: https://llm.internal.example.com/v1
    api_key: sk-...
    extra_headers:
      CF-Access-Client-Id: "xxxx.access"
      CF-Access-Client-Secret: "yyyy"
```

请求头中的值通常包含凭证信息——Hermes绝不会记录这些内容。`extra_headers`适用于兼容OpenAI的路由；而`anthropic_messages`和`bedrock_converse`这两种API模式则不使用该参数。

**`discover_models`** — 将其设置为`false`（默认值为`true`）即可跳过对端点 `/models` 页面的查询，仅使用在配置项中指定的模型。这对于那些模型列表加载缓慢、不可靠或存在大量干扰信息的网关来说非常实用：

```yaml
providers:
  my-gateway:
    api: https://llm.internal.example.com/v1
    discover_models: false
    models:
      - my-finetune-v2
      - my-finetune-v1
```

当关闭发现功能后，模型选择器（`hermes model`、`/model`）将显示已配置的模型列表，而非实时探测结果。

**`openai_native_compaction`** — 仅在对对话内容极为信任的 OpenAI 兼容端点上，才将该功能设置为 `true`。原生压缩机制会将数据负载发送至该服务提供商所配置的 `base_url` 地址：

```yaml
providers:
  trusted-proxy:
    api: https://llm.internal.example.com/v1
    capabilities:
      openai_native_compaction: true
```

对于那种仅在收到请求后才解析原始模型别名的网关，可通过针对每个模型的 `prompt_caching` 功能，将该别名标记为提示词缓存中的条目。

```yaml
providers:
  model-proxy:
    api: https://gateway.example.com/v1
    transport: openai_chat  # or anthropic_messages
    models:
      fable:
        context_length: 1000000
        prompt_caching: true
```

Hermes会将该声明直接匹配到对应的提供者路由及运行时模型ID，而不会重写别名，也不会根据提供者的名称、主机或模型系列来推断其支持能力。标记布局会遵循所配置的传输协议：`openai_chat`使用与OpenAI兼容的封装格式，而`anthropic_messages`则采用原生内部块格式。若将`prompt_caching: false`设置为值，即可明确禁用某个模型的缓存标记；若不设置该参数，Hermes则会继续执行常规的提供者及模型能力检测。

:::注意 旧格式
早期的配置文件会使用顶层的`custom_providers:`列表（其中使用`base_url`而非`api`）。这种格式仍然有效，并会在执行`hermes update`操作（配置版本v12及以上）时自动迁移为`providers:`字典格式。
:::

### Nous Portal：Claude通过哪种接口传输
Nous Portal通过两种路由来提供其`anthropic/*`模型：与OpenAI兼容的 `/v1/chat/completions`接口，以及Anthropic Messages原生的 `/v1/messages`接口。`nous.anthropic_wire`参数用于选择其中一种接口。

```yaml
nous:
  anthropic_wire: chat     # default. "native" = the Anthropic Messages wire; "auto" = decide per session
```

目前默认值为 `chat`。原生传输方式是更优的选择（带签名的思维块能原封不动地传递，同时还能保留原生的 `cache_control` 设置），但在 Portal 的 OpenRouter 提供的路径上，当并发工具调用形成循环时，有 14%–20% 的连续请求会重新写入上一轮的提示词缓存，这相当于整个请求量的 15%–20% 用于缓存写入操作；而在相同测试中，`chat` 路径的该数值为 0。若希望恢复使用原生传输方式（例如在 Portal 端的修复版本发布后），可将参数设置为 `native`。仅 `anthropic/*` 系列模型会受此影响，Nous 平台上的其他所有模型目前均已使用 `chat`/`completions` 机制。

`auto` 模式适用于 Portal 通过多个上游源提供相同模型的情况。会话初始以 `chat` 模式启动，Hermes 会识别是哪个上游响应了首次请求，只有当确认该上游能稳定使用原生传输方式时，才会将对应会话切换为原生模式——这种切换发生在两次请求之间，因此不会导致正在处理的响应丢失或现有缓存失效。目前尚无上游源被标记为“安全”，所以 `auto` 模式的表现与 `chat` 完全一致；设置该模式的目的是让切换决策基于实际测试数据而非手动配置。

## 何时生效？

- **CLI**（`hermes chat`）：下一次调用 `hermes chat` 时。
- **网关**（Telegram、Discord、Slack 等）：下一个*新*会话开始时。现有会话将继续使用原有的模型。如需强制所有会话立即应用更改，可重启网关（`hermes gateway restart`）。
- **控制面板聊天标签页**（`/chat`）：下一个新的实时文本对话窗口创建时。当前已打开的聊天窗口会保持原有模型——可在其中使用 `/model` 命令进行热切换。
在正在运行的会话中，更新模型并不会使提示词缓存失效。这是有意为之：若需在会话内更换主模型，则必须重置缓存（因为系统提示词中包含特定于模型的内容），而我们保留通过聊天界面中的 `/model` 命令来执行此项操作。

## 故障排除

### 选择器中显示“无已认证的提供方”

只有当提供方拥有有效的凭证时，Hermes才会将其列出来。请检查侧边栏中的 **Keys** —— 你应该能看到 API 密钥、成功的 OAuth 认证信息或自定义端点 URL 中的一种。如果所需提供方不在列表中，请运行 `hermes setup` 进行配置，或者前往 **Keys** 页面添加相应的环境变量。

### 正在使用的聊天窗口中的主模型并未改变

这是正常现象。控制面板会保存 `config.yaml` 文件，新启动的会话会读取该文件。而当前打开的聊天窗口属于实时代理进程，它会保持创建时的模型版本不变。若需为该特定会话热更模型，请在聊天界面中使用 `/model <模型名称>` 命令。

### 辅助模型的覆盖设置“未生效”

请检查以下三点：

1. **是否已启动新会话？** 已有的聊天窗口不会重新读取配置文件。
2. **`provider` 的值是否设置为除 `auto` 以外的其他选项？** 如果该字段显示为 `auto`，则任务仍在使用你的主模型。请点击 **Change** 并选择真实的提供方。
3. **该提供方是否已完成认证？** 如果你为某个任务指定了 `minimax`，但并未拥有 MiniMax API 密钥，那么该任务将会回退到 openrouter 的默认设置，并在 `agent.log` 文件中记录警告信息。

### 我已选择了模型，但 Hermes 仍自动更换了提供方

在 OpenRouter（或任何聚合平台）上，模型名称会首先在 해당聚合平台内部进行解析。因此，在 OpenRouter 上输入的 `claude-sonnet-4` 会被转换为 `anthropic/claude-sonnet-4.6`，并且仍保持通过 OpenRouter 进行身份认证。但如果在直接使用 Anthropic 身份认证的环境中输入 `claude-sonnet-4`，其名称则仍为 `claude-sonnet-4-6`。如果发现模型提供方意外发生变化，请确认当前使用的提供方确实符合预期——选择器总会将当前默认的提供方显示在对话框的顶部。

## 其他方法

### CLI 斜杠命令

在任何 `hermes chat` 会话中均可使用：

```
/model gpt-5.4 --provider openrouter             # session-only
/model gpt-5.4 --provider openrouter --global    # also persists to config.yaml
/model claude-opus-4.6 --once                    # next turn only, then auto-restores
```

`--global` 的作用与控制面板中的 **Change** 按钮相同，同时还能直接切换正在运行的会话。

`--once` 仅适用于单轮对话，在对话结束后（无论成功、出错还是被中断）都会恢复到之前的模型。所有设置都不会被保留：如果在某轮对话中途重启网关，系统会重新使用原来的模型。该选项适用于将某个复杂问题转交给更强大的模型处理（“仅此一次使用 Opus 模型”），或在对简单查询时使用成本较低的模型。

:::note 提示词缓存成本
单轮切换会导致两次打破提供方的提示词缓存前缀（即切换出去再切回来）。在基于缓存前缀的提供方（如 Anthropic、OpenAI）上进行的长时间会话中，下一轮对话需要重新支付全部的输入成本。因此，对于短时间会话或从低成本模型升级到高成本模型的场景，`--once` 更为合适；但在漫长的高成本会话中快速提出一个次要问题，其带来的成本可能反而高于节省的成本。
:::

### 自定义别名

为您经常使用的模型定义自定义简称，然后在运行中的会话中使用 `/model <alias>`，或在启动时使用 `hermes chat --model <alias>`。有两种等效的格式——请选择适合您工作流程的那种。

**标准格式（顶层 `model_aliases:`）**——可完全控制提供方及基础 URL：

```yaml
# ~/.hermes/config.yaml
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
```

指向自身端点的别名也可携带该端点的认证信息，认证信息可以是 `api_key`（直接值或 `"${VAR}"` 引用形式），也可以是 `key_env`（环境变量名称）。若同时设置了这两种方式，则以 `api_key` 的值为准。

```yaml
model_aliases:
  theta:
    model: theta-1
    provider: custom
    base_url: "https://theta.example.com/v1"
    key_env: THETA_API_KEY        # or: api_key: "${THETA_API_KEY}"
```

当别名未指定任一值时，该密钥将从别名中的 **host** 字段确定——对于 `ollama.com` 接口使用 `OLLAMA_API_KEY`，对于 `api.deepseek.com` 则使用 `DEEPSEEK_API_KEY`，依此类推。该密钥绝不会继承自切换前处于激活状态的提供方，因此切换别名无法将某个提供方的密钥发送到另一个提供方的服务器上。

**短字符串格式（`model.aliases.<名称>: provider/model`）**——在命令行中使用更为便捷，因为 `hermes config set` 命令既支持存储标量值，现在也支持解析内联列表/映射字面量；不过这种简写别名格式仍无法指定自定义的 `base_url`：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

`hermes config set` 命令也支持内联的**列表/映射字面量**（JSON/YAML 流式格式）。请为这些内容添加引号，以确保 shell 能将其原封不动地传递过去：

> ```bash
> hermes config set platform_toolsets.line '["clarify", "file", "web"]'
> hermes config set display.tool_progress_overrides '{"terminal": "off"}'
> ```

这两种方式都会将配置传递给同一个加载器（`hermes_cli/model_switch.py`）。在 `model_aliases:` 中声明的条目，会优先于 `model.aliases:` 中具有相同名称的条目。

之后可在聊天中使用 `/model fav` 或 `/model grok` 命令。用户自定义的别名会覆盖内置的简写名称（如 `sonnet`、`kimi`、`opus` 等）。详细参考信息请参阅 [自定义模型别名](/reference/slash-commands#custom-model-aliases)。

### `hermes model` 子命令

```bash
hermes model            # Interactive provider + model picker (the canonical way to switch defaults)
```

`hermes model` 会引导您完成选择提供商、进行身份验证（OAuth 流程会自动打开浏览器；而基于 API 密钥的提供商则会提示输入密钥），随后从该提供商精选的模型目录中挑选具体的模型。所选模型信息会被写入 `~/.hermes/config.yaml` 文件中的 `model.provider` 和 `model.default` 字段。

若不想启动选择界面即可查看所有提供商和模型，可使用控制面板或以下的 REST 接口。要查看 CLI 当前实际使用的配置，可执行 `hermes config get model --json` 以及 `hermes status` 命令。

### 直接编辑配置

可直接修改 `~/.hermes/config.yaml` 文件，然后重启读取该文件的程序。完整的配置结构请参考 [配置参考文档](./configuration.md)。

### REST API

控制面板使用了三个接口，非常适合用于脚本编写：

```bash
# List authenticated providers + curated model lists
curl -H "X-Hermes-Session-Token: $TOKEN" http://localhost:PORT/api/model/options

# Read current main + auxiliary assignments
curl -H "X-Hermes-Session-Token: $TOKEN" http://localhost:PORT/api/model/auxiliary

# Set the main model
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"main","provider":"openrouter","model":"anthropic/claude-opus-4.7"}' \
  http://localhost:PORT/api/model/set

# Override a single auxiliary task
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"vision","provider":"openrouter","model":"google/gemini-2.5-flash"}' \
  http://localhost:PORT/api/model/set

# Assign one model to every auxiliary task
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"","provider":"openrouter","model":"google/gemini-2.5-flash"}' \
  http://localhost:PORT/api/model/set

# Reset all auxiliary tasks to auto
curl -X POST -H "Content-Type: application/json" -H "X-Hermes-Session-Token: $TOKEN" \
  -d '{"scope":"auxiliary","task":"__reset__","provider":"","model":""}' \
  http://localhost:PORT/api/model/set
```

在系统启动时，会将该会话令牌注入到控制台页面的 HTML 代码中，并且在每次服务器重启时都会更新。如果您需要针对正在运行的控制台编写脚本，可以通过浏览器的开发者工具获取该令牌（位于 `window.__HERMES_SESSION_TOKEN__` 中）。
