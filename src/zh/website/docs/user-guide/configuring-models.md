---
sidebar_position: 3
---

# 模型配置

Hermes 使用两种类型的模型槽位：

- **主模型**——智能体用于思考的模型。每一条用户消息、每一次工具调用循环以及每一条流式响应都会经过该模型处理。
- **辅助模型**——智能体将部分任务分派给这些较小的模型来执行，例如上下文压缩、视觉处理（图像分析）、网页摘要生成、审批评分、MCP 工具路由、会话标题生成以及技能搜索等。每种辅助模型都有独立的槽位，且可以单独进行覆盖配置。

本页面介绍如何通过控制面板配置这两种模型。如果您更喜欢使用配置文件或命令行工具，请跳转到文末的[其他方法](#alternative-methods)。

:::提示 最快捷方式：Nous Portal
[Nous Portal](/user-guide/features/tool-gateway)允许用户通过一个订阅账户获取300多种模型。在全新安装后，只需运行 `hermes setup --portal` 即可登录，并通过一条命令将 Nous 设置为默认提供商。使用 `hermes portal info` 可以查看当前已配置的模型情况。

- 使用 Portal 订阅的用户还能享受**按令牌计费提供商10%的折扣**。
:::

:::注意 `model:` 结构——空字符串与映射格式
在全新安装时，默认配置文件中会包含 `model: ""`（一个表示“尚未配置”的空字符串）。首次运行 `hermes setup` 或 `hermes model` 后，该键会立即升级为包含 `provider`、`default`、`base_url` 和 `api_mode` 子键的映射格式——这与本页面以及 [`profiles.md`](./profiles.md) / [`configuration.md`](./configuration.md) 中所示的结构一致。如果您在 `config.yaml` 文件中看到空字符串，只需运行 `hermes model`（或点击控制面板中的**更改**按钮），Hermes 会自动将其转换为映射格式。
:::

## 模型页面

打开控制面板，点击侧边栏中的**模型**选项。页面会显示两个部分：

1. **模型设置**——顶部面板，用于将模型分配到各个槽位。
2. **使用情况分析**——以卡片形式展示选定时间段内参与过会话的所有模型，同时显示令牌消耗量、成本以及功能标签。

![模型页面概览](/img/docs/dashboard-models/overview.png)

最顶端的卡片即为**模型设置**面板。主行始终显示智能体在新建会话时会使用的模型。点击**更改**即可打开模型选择器。

## 设置主模型

点击主模型行上的**更改**按钮：

![模型选择器对话框](/img/docs/dashboard-models/picker-dialog.png)

选择器包含两列内容：

- **左侧**——已认证的提供商。此处仅显示您已配置的提供商（已设置API密钥、已完成OAuth认证或被定义为自定义端点的提供商）。如果某个提供商未显示，请前往**密钥**选项页添加相应的凭证。
- **右侧**——所选提供商的精选模型列表。这些是Hermes为该提供商推荐的智能体模型，而非 `/models` 目录中完整的模型列表（在OpenRouter平台上，该目录包含400多种模型，涵盖文本转语音、图像生成及重排序等功能）。

在过滤框中输入内容，即可按提供商名称、标识符或模型ID进行筛选。

选定某个模型后点击**切换**，Hermes会将其写入 `~/.hermes/config.yaml` 文件的 `model` 部分。**此操作仅适用于新建会话**——您已打开的任何聊天窗口将继续使用初始设置的模型。若要更换当前聊天窗口中的模型，可在该窗口内使用 `/model` 命令。
:::

## 会话进行中的模型切换与上下文警告

当您在**正在进行的会话中**切换模型时（通过Herm TUI模型选择器、`hermes`命令行工具，或在Telegram/Discord上使用 `/model` 命令），Hermes会评估您的**下一条消息**是否需要针对新模型对应的上下文窗口执行**预处理上下文压缩**操作。如果会话的上下文长度已接近或超过该模型的压缩阈值（详见[上下文压缩](./configuration.md#context-compression)部分），系统会在切换回复中发出警告——这与针对高成本模型的警告机制相同。尽管如此，模型切换仍会立即生效；压缩操作会在模型响应之前的**第一条用户消息**处执行。

:::警告 会话进行中的模型切换会重置提示词缓存
提示词缓存是按照处理请求的模型来区分的，因此无论是在对话过程中手动切换模型、使用[自动回退机制](./features/fallback-providers.md)还是通过[凭证池](./features/credential-pools.md)切换到其他账户，下一条消息都将以全额令牌费用重新读取整个对话历史，而无法使用缓存后的较低费用（通常可节省75–90%）。在长时间会话中，这种一次性重新读取的成本可能远高于两种模型之间的单令牌成本差异。建议在必要时再进行模型切换，最好是在对话初期或新建会话后立即操作。
:::

## 设置辅助模型

点击**显示辅助模型**即可查看11个任务槽位：

![辅助模型面板展开图](/img/docs/dashboard-models/auxiliary-expanded.png)

所有辅助任务的默认值为 `auto`——这意味着Hermes也会尝试使用主模型来处理这些任务。如果该路径不可用或出现容量限制类故障，系统会依次尝试任务特定的 `auxiliary.<task>.fallback_chain` 配置、主模型的 `fallback_providers` / `fallback_model` 回退链，最后再使用Hermes内置的辅助模型发现机制。如果您希望为某些辅助任务选择更便宜或更快速的模型，可以对其进行单独覆盖配置。

### 常见的覆盖配置方式

| 任务类型 | 何时进行覆盖配置 |
|---|---|
| **标题生成** | 几乎总是需要覆盖。有一些成本仅为0.10美元/百万次的快速模型，既能生成Opus格式的会话标题，也能生成其他格式的标题。在OpenRouter平台上，默认配置为此类模型为 `google/gemini-3-flash-preview`。 |
| **视觉处理** | 当主模型不支持视觉功能时。此时可选用 `google/gemini-2.5-flash` 或 `gpt-4o-mini` 等模型。 |
| **上下文压缩** | 当您在处理Opus/M2.7格式的上下文时消耗了大量推理令牌用于摘要生成时。使用快速聊天模型即可以1/50的成本完成相同任务。 |
| **审批功能** | 对于 `approval_mode: smart` 模式，可使用快速且低成本的模型（如haiku、flash、gpt-5-mini）来自动判断是否批准低风险指令。使用高成本模型在此场景下属于资源浪费。 |
| **网页提取** | 当您频繁使用 `web_extract` 功能时。其逻辑与上下文压缩类似——摘要生成无需复杂的推理过程。 |
| **技能中心** | `hermes skills search` 功能会使用此路径。通常保持默认的 `auto` 设置即可。 |
| **MCP工具路由** | 用于MCP工具的路由功能。通常保持默认的 `auto` 设置即可。 |
| **任务分类指定器** | 用于处理Kanban任务分类功能（即 `hermes kanban specify` 命令），可将简略的任务描述转换为具体的执行规范。使用低成本但功能完备的模型即可满足需求。 |
| **Kanban任务分解器** | 用于将Kanban任务分解为适合不同专业角色的子任务结构。 |
| **角色描述生成器** | 用于生成角色描述内容（即 `hermes profile describe --auto` 命令或控制面板中的自动生成按钮）。属于短时间、低成本的调用操作。 |
| **内容审核器** | 用于执行内容审核相关的技能使用检查功能。在基于推理能力的模型上运行此类任务可能需要数分钟，因此使用成本较低的辅助模型通常更为合适。 |

### 单个任务的覆盖配置

点击任意辅助任务行上的**更改**按钮。系统会打开相同的模型选择器，操作流程一致：选择提供商和模型后点击**切换**，该行就会显示为 `provider · model` 的格式，而不再显示 `auto (使用主模型)` 的提示。

### 将所有设置恢复为自动模式

如果您进行了过度的自定义配置并希望重新恢复默认设置，可点击辅助模型部分顶部的**将所有设置恢复为自动模式**按钮。这样所有槽位都会再次使用主模型。

## “用作”快捷功能

页面上的每个模型卡片都配有**“用作”**下拉菜单。这是一个快速配置方式——只需选择在分析报告中出现的某个模型，点击**“用作”**，即可一键将其分配到主模型槽位或任意特定的辅助任务中：

![“用作”下拉菜单](/img/docs/dashboard-models/use-as-dropdown.png)

该下拉菜单包含以下选项：

- **主模型**——与直接在主模型行上点击“更改”功能相同。
- **所有辅助任务**——可将该模型同时分配到全部11个辅助槽位。当您希望所有辅助任务都使用同一款低成本快速模型时，此选项非常实用。
- **单个任务选项**——包括视觉处理、网页提取、上下文压缩等任务类型。当前已分配给各任务的模型会标记为 `current`。

当前被分配了模型的卡片会显示 `main` 或 `aux · <任务类型>` 的标签，这样您就能一目了然地了解历史上哪些模型被配置在了哪些位置。

## 保存到 `config.yaml` 的内容

通过控制面板保存配置后，Hermes会将相关设置写入 `~/.hermes/config.yaml` 文件，具体内容如下：

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

**辅助功能：自动（默认值）：**
```yaml
auxiliary:
  compression:
    provider: auto
    model: ''
    base_url: ''
    # ... other fields unchanged
```

当同时设置 `provider: auto` 和 `model: ''` 时，Hermes 会使用该任务对应的主模型进行处理；即便主路由无法处理辅助调用，也会遵循预设的回退策略。

可选的、针对特定任务的回退链则位于同一个辅助任务之下：

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

## 何时生效？

- **CLI**（`hermes chat`）：下一次调用 `hermes chat` 时。
- **网关**（Telegram、Discord、Slack 等）：下一个*新*会话开始时。现有会话将保持原有的模型。如需强制所有会话都应用此更改，需重启网关（`hermes gateway restart`）。
- **控制面板聊天标签页**（`/chat`）：下一个新的伪终端连接建立时。当前已打开的聊天会保持原有模型——可在其中使用 `/model` 命令进行热切换。

这些更改不会影响正在运行的会话中的提示词缓存。这是有意为之：在会话中更换主模型需要重置缓存（系统提示词包含特定于模型的内容），而我们将其保留给聊天界面中的 `/model` 命令使用。

## 故障排除

### 选择器中显示“无已认证的提供方”

只有具备有效凭证的提供方才会被 Hermes 列出。请检查侧边栏中的 **Keys**——你应该能看到 API 密钥、成功的 OAuth 认证信息或自定义端点 URL。如果所需提供方不在列表中，可运行 `hermes setup` 进行配置，或前往 **Keys** 页面添加相应的环境变量。

### 正在运行的聊天中主模型未发生变化

这是正常现象。控制面板会保存 `config.yaml` 文件，新会话会读取该文件。而当前正在使用的聊天属于实时代理进程，会一直保留创建时的模型。若要为特定会话热切换模型，可在聊天界面中使用 `/model <名称>` 命令。

### 辅助模型覆盖设置“未生效”

需检查以下三点：

1. **是否已启动新会话？**现有聊天不会重新读取配置文件。
2. **`provider` 是否设置为除 `auto` 以外的值？**如果该字段显示为 `auto`，则任务仍在使用你的主模型。请点击 **Change** 并选择实际的提供方。
3. **该提供方是否已完成认证？**如果你为某个任务指定了 `minimax`，但并未拥有 MiniMax API 密钥，该任务将回退到 OpenRouter 的默认提供方，并在 `agent.log` 中记录警告信息。

### 我已选择了模型，但 Hermes 仍自动切换了提供方

在 OpenRouter（或任何聚合平台）上，纯模型名称会首先在聚合平台内部进行解析。因此，在 OpenRouter 上输入的 `claude-sonnet-4` 实际会被转换为 `anthropic/claude-sonnet-4.6`，并保持你的 OpenRouter 认证状态。但如果你在原生 Anthropic 认证环境中输入 `claude-sonnet-4`，它将保持为 `claude-sonnet-4-6` 的形式。如果出现意外的提供方切换，请确认当前使用的提供方是否符合预期——选择器始终会在对话框顶部显示当前的主模型。

## 其他方法

### CLI 斜杠命令

在任何 `hermes chat` 会话中均可使用：

```
/model gpt-5.4 --provider openrouter             # session-only
/model gpt-5.4 --provider openrouter --global    # also persists to config.yaml
/model claude-opus-4.6 --once                    # next turn only, then auto-restores
```

`--global` 的功能与控制面板的 **Change** 按钮相同，同时还能直接切换正在运行的会话。

`--once` 仅适用于单轮对话，在对话结束后无论成功、出错还是被中断，都会恢复到之前的模型。所有设置都不会被保留：如果在某轮对话中途重启网关，系统会重新使用原始模型。该选项适用于将某个复杂问题转交给高性能模型处理（“仅此一次使用 Opus”），或在对简单查询时切换到低成本模型。

:::note 提示词缓存成本
单轮切换会导致两次破坏提供方的提示词缓存前缀（即先切换出去再切回来）。在基于缓存前缀的提供方（如 Anthropic、OpenAI）上进行的长时间会话中，下一轮对话需要重新支付全部的输入成本。因此，对于短时间会话或从低成本模型升级到高性能模型的场景，`--once` 更为合适；但在长时间的昂贵模型会话中快速提出一个简单问题，其成本可能反而高于节省的费用。
:::

### 自定义别名

你可以为经常使用的模型定义自己的简写名称，然后在 CLI 或任何消息平台中使用 `/model <alias>` 来调用它们。有两种等效的格式——选择最适合你工作流程的那种即可。

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

**简短字符串格式（`model.aliases.<name>: provider/model`）**——在命令行中使用十分便捷，因为`hermes config set`仅能写入标量值，而无法设置自定义的`base_url`：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

这两条路径都会将指令传递给同一个加载器（`hermes_cli/model_switch.py`）。在 `model_aliases:` 中定义的模型别名，会优先于 `model.aliases:` 中具有相同名称的别名。

随后可在聊天中输入 `/model fav` 或 `/model grok`。用户自定义的别名会覆盖内置的简写名称（如 `sonnet`、`kimi`、`opus` 等）。更多详细信息请参阅 [自定义模型别名](/reference/slash-commands#custom-model-aliases)。

### `hermes model` 子命令

```bash
hermes model            # Interactive provider + model picker (the canonical way to switch defaults)
```

`hermes model` 会指导您选择提供商，完成身份验证（OAuth 流程会自动打开浏览器；而使用 API 密钥的提供商则会提示输入密钥），随后从该提供商提供的精选模型目录中挑选具体的模型。所选模型的信息会被写入 `~/.hermes/config.yaml` 文件中的 `model.provider` 和 `model.default` 字段。

若不想启动选择器即可查看所有提供商和模型，可使用控制面板或以下的 REST 接口。要查看 CLI 当前实际使用的设置，可执行 `hermes config get model --json` 和 `hermes status` 命令。

### 直接编辑配置

可直接修改 `~/.hermes/config.yaml` 文件，然后重启读取该文件的进程。完整的配置结构请参考 [配置参考文档](./configuration.md)。

### REST API

控制面板使用了三个接口，非常适合用于编写脚本：

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

在系统启动时，会将该会话令牌注入到控制台页面的 HTML 代码中，并且每次服务器重启后都会更换。如果您需要针对正在运行的控制台编写脚本，可以通过浏览器的开发者工具获取该令牌（地址为 `window.__HERMES_SESSION_TOKEN__`）。
