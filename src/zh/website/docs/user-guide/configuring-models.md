---
sidebar_position: 3
---

# 模型配置

Hermes 使用两种类型的模型槽位：

- **主模型**——代理用于思考的核心模型。每条用户消息、每次工具调用循环以及所有流式响应都会经过该模型处理。
- **辅助模型**——代理用于分流处理的小型任务，包括上下文压缩、视觉处理（图像分析）、网页摘要生成、审批评分、MCP 工具路由、会话标题生成以及技能搜索等。每种辅助模型都有独立的槽位，可单独进行覆盖配置。

本页面介绍如何通过控制面板配置这两种模型。如果您更喜欢使用配置文件或命令行工具，请跳转到文末的[其他方法](#alternative-methods)。

:::提示 最快捷方式：Nous Portal
[Nous Portal](/user-guide/features/tool-gateway)允许用户在同一订阅套餐下使用300多种模型。在首次安装时，运行 `hermes setup --portal` 即可一键登录并将Nous设置为您的服务提供商。使用 `hermes portal info` 可查看当前已配置的模型情况。

- 使用Portal订阅的用户还可享受**按令牌计费的服务提供商9折优惠**。
:::

:::注意 `model:` 结构——空字符串与映射格式
在全新安装时，默认配置中的值为 `model: ""`（即空字符串，表示“尚未配置”）。首次运行 `hermes setup` 或 `hermes model` 后，该键会立即升级为包含 `provider`、`default`、`base_url` 和 `api_mode` 子键的映射格式——这与本页面以及 [`profiles.md`](./profiles.md) / [`configuration.md`](./configuration.md) 中所示的结构一致。如果您在 `config.yaml` 中看到空字符串，只需运行 `hermes model`（或点击控制面板中的**更改**按钮），Hermes便会自动将其转换为映射格式。
:::

## 模型页面

打开控制面板，点击侧边栏中的**模型**选项。页面将显示两个部分：

1. **模型设置**——顶部面板，用于将模型分配到各槽位。
2. **使用分析**——以卡片形式展示选定时间段内参与过会话的所有模型，同时显示令牌消耗量、成本以及功能标签。

![模型页面概览](/img/docs/dashboard-models/overview.png)

最顶部的卡片即为**模型设置**面板。主行始终显示代理在新建会话时会使用的模型。点击**更改**可打开模型选择器。

## 设置主模型

点击主模型行上的**更改**按钮：

![模型选择器对话框](/img/docs/dashboard-models/picker-dialog.png)

选择器包含两列内容：

- **左侧**——已认证的服务提供商。此处仅显示您已配置的服务提供商（已设置API密钥、完成OAuth验证或定义为自定义端点的提供商）。如果某个提供商未显示，请前往**密钥**选项添加其凭证。
- **右侧**——所选提供商的精选模型列表。这些是Hermes为该提供商推荐的代理模型，而非原始的 `/models` 列表（在OpenRouter中该列表包含400多种模型，涵盖文本转语音、图像生成及重排序等功能）。

在过滤框中输入内容，可按提供商名称、标识符或模型ID进行筛选。

选定模型后点击**切换**，Hermes会将该模型信息写入 `~/.hermes/config.yaml` 文件的 `model` 部分。**此操作仅适用于新建会话**——您已打开的任何聊天窗口将继续使用初始设置的模型。若要即时更换当前聊天的模型，可在该聊天窗口中使用 `/model` 命令。

### 会话进行中的模型切换与上下文警告

当您在**正在进行的会话中**切换模型时（通过Herm TUI模型选择器、`hermes`命令行工具，或Telegram/Discord上的 `/model` 命令），Hermes会评估您的**下一条消息**是否需要针对新模型对应的上下文窗口执行预处理压缩操作。如果会话的上下文复杂度已接近或超过该模型的压缩阈值（详见[上下文压缩](./configuration.md#context-compression)部分），切换回复中会包含警告信息——与高成本模型相关的警告使用的是相同的 `warning_message` 路径。尽管如此，模型切换仍会立即生效；压缩操作会在模型响应之前、用户的**第一条消息发送后**执行。

## 设置辅助模型

点击**显示辅助模型**可查看11个任务槽位：

![辅助模型面板展开视图](/img/docs/dashboard-models/auxiliary-expanded.png)

所有辅助任务的默认值为 `auto`——这意味着Hermes也会尝试使用主模型来处理这些任务。如果该路径不可用或出现容量限制类故障，系统会依次尝试任务特定的 `auxiliary.<task>.fallback_chain` 配置、主模型的 `fallback_providers` / `fallback_model` 配置，最后再使用Hermes内置的辅助模型发现机制。如果您希望为某些辅助任务使用成本更低或速度更快的模型，可手动覆盖这些配置。

### 常见覆盖配置模式

| 任务类型 | 何时需要覆盖配置 |
|---|---|
| **标题生成** | 几乎总是需要。有一种成本仅为0.10美元/分钟的快速模型，既能生成Opus格式的会话标题，也能完成标题生成功能。在OpenRouter中，默认配置为此模型：`google/gemini-3-flash-preview`。 |
| **视觉处理** | 当主模型不支持视觉处理功能时。可选用 `google/gemini-2.5-flash` 或 `gpt-4o-mini` 等模型。 |
| **上下文压缩** | 当您仅为了总结上下文而耗费大量推理令牌在Opus/M2.7模型上时。使用快速聊天模型即可完成相同任务，且成本仅为前者的1/50。 |
| **审批功能** | 对于 `approval_mode: smart` 模式——使用快速且低成本的模型（如haiku、flash、gpt-5-mini）自动判断是否批准低风险指令。使用高成本模型在此场景下属于浪费。 |
| **网页提取** | 当您频繁使用 `web_extract` 功能时。逻辑与上下文压缩类似——摘要生成无需复杂推理。 |
| **技能中心** | `hermes skills search` 功能会使用此模型。通常保持默认的 `auto` 设置即可。 |
| **MCP功能** | 用于MCP工具路由。通常保持默认的 `auto` 设置即可。 |
| **任务分类指定器** | 用于处理Kanban任务分类功能（`hermes kanban specify`），可将简略的描述转换为具体的任务规范。使用低成本且功能强大的模型效果良好。 |
| **Kanban任务分解器** | 用于分解Kanban任务——将分类后的任务拆解为适合不同专业角色的子任务结构。 |
| **角色描述生成器** | 用于生成角色描述内容（`hermes profile describe --auto` 或控制面板的自动生成按钮）。属于短时间、低成本的调用操作。 |
| **模型审核器** | 用于执行模型使用情况审核功能。在基于推理的模型上运行此功能可能需要数分钟，因此使用成本较低的辅助模型通常更为合适。 |

### 单个任务覆盖配置

点击任意辅助模型行上的**更改**按钮。系统会打开相同的模型选择器，操作流程一致：选择服务提供商和模型后点击**切换**。该行将更新为显示 `provider · model` 的格式，而非之前的 `auto (使用主模型)`。

### 将所有设置恢复为自动模式

如果您进行了过度调整并希望重新恢复默认设置，可点击辅助模型部分顶部的**将所有设置恢复为自动模式**按钮。此时所有槽位都将重新使用主模型。

## “用作”快捷选项

页面上的每个模型卡片都配有**“用作”**下拉菜单。这是最快捷的配置方式——只需选择在分析数据中出现的模型，点击**“用作”**，即可一键将其分配到主模型槽位或任意特定的辅助任务中：

![“用作”下拉菜单](/img/docs/dashboard-models/use-as-dropdown.png)

下拉菜单包含以下选项：

- **主模型**——与直接点击主模型行上的**更改**按钮功能相同。
- **所有辅助任务**——将该模型同时分配到11个辅助槽位。当您希望所有辅助任务都使用相同的低成本快速模型时，此选项非常实用。
- **单个任务选项**——包括视觉处理、网页提取、上下文压缩等任务类型。当前已分配给各任务的模型会标记为 `current`。

当前被分配了模型的卡片会显示 `main` 或 `aux · <任务类型>` 标签，这样您就能一目了然地看出历史配置中哪些模型被分配到了哪些槽位。

## 保存到 `config.yaml` 的内容

通过控制面板保存配置时，Hermes会将以下内容写入 `~/.hermes/config.yaml` 文件：

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
```

`--global` 的功能与控制面板中的**更改**按钮相同，同时还能直接切换正在运行的会话。

### 自定义别名

为经常使用的模型定义自定义简称，之后即可在 CLI 或任何消息平台中使用 `/model <alias>` 来调用它们。共有两种等效的格式——请选择最适合您工作流程的那种。

**标准格式（顶层 `model_aliases:`）**——可完全控制提供方及基础网址：

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

`hermes model` 会引导您完成以下步骤：选择服务提供商、进行身份验证（OAuth 流程会自动打开浏览器；而使用 API 密钥的服务提供商则会提示输入密钥），随后从该提供商提供的模型目录中挑选特定的模型。所选模型的信息会被写入 `~/.hermes/config.yaml` 文件中的 `model.provider` 和 `model.model` 字段。

若不想启动选择界面即可查看所有服务提供商及模型，可使用控制面板或以下的 REST 接口。要查看 CLI 当前实际使用的模型信息，可运行 `hermes config show | grep '^model\.'` 以及 `hermes status` 命令。

### 直接编辑配置文件

直接修改 `~/.hermes/config.yaml` 文件，然后重启读取该文件的程序。完整的配置结构规范请参考 [配置参考文档](./configuration.md)。

### REST API

控制面板使用了三个接口。这些接口非常适合用于编写脚本：

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
