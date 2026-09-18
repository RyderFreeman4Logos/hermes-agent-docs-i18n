---
sidebar_position: 2
title: "TUI"
description: "Launch the modern terminal UI for Hermes — mouse-friendly, rich overlays, and non-blocking input."
---

# TUI

TUI 是 Hermes 的现代化前端界面——它是一种终端式用户界面，与 [经典 CLI](cli.md) 使用相同的 Python 运行时。同样的 Agent、同样的会话、同样的斜杠命令；只是为与之交互提供了更为简洁且响应更快的操作体验。

这是推荐用于交互式运行 Hermes 的方式。

## 启动

```bash
# Launch the TUI
hermes --tui

# Resume the latest TUI session (falls back to the latest classic session)
hermes --tui -c
hermes --tui --continue
hermes --tui --resume latest

# Resume a specific session by ID or title
hermes --tui -r 20260409_000000_aa11bb
hermes --tui --resume "my t0p session"

# Resume the latest session for a specific project directory
hermes --tui --resume latest --in ./my-project

# Run source directly — skips the prebuild step (for TUI contributors)
hermes --tui --dev
```

您也可以通过环境变量来启用它：

```bash
export HERMES_TUI=1
hermes          # now uses the TUI
hermes chat     # same
```

或者将其设置为 `~/.hermes/config.yaml` 中的永久默认值：

```yaml
display:
  interface: tui   # "cli" (default) or "tui"
```

当设置 `display.interface: tui` 后，基础版的 `hermes`（以及 `hermes chat`）将会启动文本用户界面模式。显式指定的参数始终具有优先级——若希望单次调用时切换回传统的命令行交互模式，可运行 `hermes --cli`；而当配置默认值为 `cli` 时，若想强制使用 TUI 模式，则可使用 `hermes --tui` 或 `HERMES_TUI=1`。

传统命令行界面仍是预装的默认模式。所有在 [CLI 接口文档](cli.md) 中提及的功能——斜杠命令、快捷命令、技能预加载、角色设置、多行输入、中断处理等——在 TUI 模式下均能以完全相同的方式正常工作。

## 为何选择 TUI 模式？

- **即时显示首屏**：应用尚未完全加载完毕，界面标题栏就已出现，因此 Hermes 启动过程中终端不会出现卡顿现象。
- **非阻塞式输入**：可在会话准备就绪之前先输入并排队消息，代理上线后立即就能看到提示符。
- **丰富的叠加界面**：模型选择器、会话选择器以及确认与澄清提示等元素均以模态面板的形式呈现，而非内联流程。
- **实时会话面板**：各类工具和技能会在初始化过程中逐步显示出来。
- **便于鼠标操作的选择功能**：可通过拖动来高亮内容，且采用统一背景色，无需依赖 SGR 反转效果；复制操作也可使用终端常规的复制手势。
- **多屏幕适配显示**：差分更新机制确保流式传输时无闪烁现象，退出后也不会留下多余的滚动记录。
- **强大的文本编辑功能**：支持长文本片段的行内折叠、通过 `Cmd+V` / `Ctrl+V` 进行文本粘贴（同时提供剪贴板图片作为备用）、安全括号粘贴功能，以及图像/文件路径的标准化附加功能。
相同的[皮肤](features/skins.md)和[性格设定](features/personality.md)规则同样适用。您可以使用`/skin ares`或`/personality pirate`在会话进行中切换，界面会实时重新渲染。如需了解所有可自定义的参数以及哪些参数适用于经典模式与TUI模式，请参阅[皮肤与主题](features/skins.md)——TUI模式会保留横幅配色、界面颜色、提示符符号/颜色、会话显示、补全菜单、选中项背景色、`tool_prefix`和`help_header`等设置。

### 可折叠的横幅区域

TUI启动时的横幅会将运行时信息分为四个可折叠的区域，每个区域标题旁都有一个`▸`/`▾`箭头：

| 区域 | 默认状态 |
|---------|---------------|
| 工具 | 展开 |
| 技能 | 折叠 |
| 系统提示符 | 折叠 |
| MCP服务器 | 折叠 |

点击任意区域标题（或其箭头）即可切换其展开与折叠状态。由于工具列表是会话启动时最常被查看的区域，因此默认处于展开状态；而技能、系统提示符和MCP服务器默认处于折叠状态，这样即便您安装了数十种技能或连接了众多MCP服务器，横幅依然保持简洁。这些状态仅针对当前横幅实例有效，下次启动时会恢复为默认设置。

## 系统要求

- **Node.js** ≥ 20——TUI作为从Python CLI启动的子进程运行，`hermes doctor`工具可用于检测该版本是否符合要求。
- **TTY终端**——与经典CLI类似，若通过标准输入管道传递数据或在非交互式环境中运行，系统将自动切换为单次查询模式。
首次启动时，Hermes 会将 TUI 所需的 Node 依赖项安装到 `ui-tui/node_modules` 目录中（此操作仅执行一次，耗时几秒）。后续启动则会变得非常迅速。如果您升级了 Hermes 版本，且源代码比已编译的版本更新，TUI 包将会自动重新生成。

:::提示：如何在 git worktree 环境下使用？
那些从多个 worktree 运行 `hermes --tui --dev` 命令的贡献者，无需在每个工作目录都单独安装依赖，而是可以共享同一个 `node_modules` 目录——详情请参阅[从 Worktree 使用 TUI 和桌面界面](../developer-guide/worktree-ui-dev.md)。
:::

### 外部预编译版本

那些提供预编译包的发行版（如 Nix、系统包）可以让 Hermes 直接使用这些预编译版本：

```bash
export HERMES_TUI_DIR=/path/to/prebuilt/ui-tui
hermes --tui
```

该目录中必须包含 `dist/entry.js` 文件。

## 绑定键

其绑定键与 [经典 CLI](cli.md#keybindings) 完全一致。唯一的行为差异在于：

- **`Ctrl+T`** 可将自动显示的实时子代理面板展开为全高度的 `/agents` 列表。选中某个工作节点后，按 **Enter**（或 **`t`**）可查看其实时转录内容，按 **`d`** 可查看详细信息，按 **`e`** 可对其进行控制，按 **`x`** 可停止该工作节点。面板会根据终端高度自动调整行数，并保留您的内容编辑草稿。更多详情请参阅 [监控子代理](/user-guide/features/delegation#monitoring-running-subagents-agents)。
- **`F7`** 可在默认预览模式与仅显示一行摘要的模式之间切换。此操作不会打开监控界面，也不会改变内容编辑器的焦点；该设置仅在当前 TUI 过程中有效，且不会修改配置文件。
- **鼠标拖动** 可以用统一的选中背景高亮显示文本。
- **`Cmd+V` / `Ctrl+V`** 首先尝试常规文本粘贴，若失败则尝试从 OSC52/系统剪贴板读取内容；最后，如果剪贴板内容或要粘贴的数据为图片，则会尝试附加图片。
- **`/terminal-setup`** 会安装适用于本地 VS Code、Cursor 和 Windsurf 终端的应用程序绑定，从而在 macOS 上实现更优的 **Cmd+Enter** 操作以及更完善的撤销/重做功能。
- **斜杠自动补全** 会以带说明的浮动面板形式显示，而非内联下拉菜单。
- **`Ctrl+X`** 可打开实时会话切换器。当有排队消息被高亮显示时（即在该代理仍在运行时发送的消息），系统仍会删除该排队消息。按 **`Esc`** 可取消编辑并取消高亮显示，但不会删除内容。
- **`Ctrl+G` / `Ctrl+X Ctrl+E`** — 会在 `$EDITOR` 中打开当前输入缓冲区，便于输入多行或较长的提示语；执行“保存并退出”操作后，这些内容将作为新的提示语被发送出去。
## 斜杠命令

所有斜杠命令均保持原有功能不变。其中部分命令由 TUI 管理——它们会生成更丰富的输出，或以覆盖层形式显示而非内联面板：

| 命令 | TUI 行为 |
|---------|----------|
| `/help` | 以分类形式的覆盖层展示命令，可通过方向键导航 |
| `/sessions`（别名 `/switch`） | 实时会话切换器——列出所有打开的 TUI 会话，可在其间切换、关闭会话或新建会话 |
| `/model` | 按提供方分类的模态模型选择器，同时显示成本提示 |
| `/skin` | 实时预览——在浏览过程中即可应用主题更改 |
| `/details` | 切换工具调用的详细信息显示模式（全局或针对特定部分） |
| `/usage` | 丰富的令牌/成本/上下文面板 |
| `/agents`（别名 `/tasks`） | 可观测性覆盖层——显示实时的子代理树结构，具备终止/暂停控制功能，同时提供各分支的成本/令牌/文件汇总信息以及逐步执行历史记录 |
| `/reload` | 重新将 `~/.hermes/.env` 文件内容加载到正在运行的 TUI 进程中，从而无需重启即可使新添加的 API 密钥生效 |
| `/mouse [on\|off\|toggle\|wheel\|buttons\|all]` | 运行时选择鼠标跟踪预设（该设置也会保存到 `config.yaml` 文件中的 `display.mouse_tracking` 选项中）。`wheel`（1000+1006）模式可保持滚轮滚动功能，同时避免因悬停事件导致 tmux 在提示行上方频繁显示“剪贴板中没有图像”；`buttons` 模式支持拖动选择；默认值为 `all`，即采用基于悬停的界面交互方式。 |
其他所有斜杠命令（包括已安装的技能、快捷命令以及个性设置切换功能）的使用方式都与传统 CLI 完全一致。详情请参阅[斜杠命令参考文档](../reference/slash-commands.md)。

## 实时会话切换器

当您希望一个终端充当多个 TUI 会话的调度器时，可使用实时会话切换器。该工具仅显示当前在此 TUI 进程中处于活跃状态的会话；已关闭的会话仍会保留记录，可通过 `/resume` 或 `hermes --tui --resume <id-or-title>` 重新打开。

您可以通过以下任意方式打开它：

- 在 TUI 中按下 `Ctrl+X`。
- 输入 `/sessions` 或 `/switch`。
- 输入 `/sessions new` 立即创建一个新的活跃会话。
- 点击状态行中的“N 个活跃会话”计数。

<img alt="包含一个活跃会话及一个新建选项行的 Hermes TUI 会话调度器" src="/docs/img/docs/tui-session-orchestrator/session-orchestrator.png" />

<video controls muted loop playsInline src="/docs/img/docs/tui-session-orchestrator/session-orchestrator-demo.mp4" title="Hermes TUI 会话调度器演示" style={{maxWidth: '100%'}}></video>

在切换器界面中：

- 使用 `↑` / `↓` 键切换选择项；点击鼠标也可选中对应行。
- 按下 `Enter` 键可切换到选中的活跃会话。
- 按下 `Ctrl+D` 键可关闭选中的活跃会话。
- 按下 `Ctrl+N` 键可启动一个空的活跃会话。
- 按下 `Ctrl+R` 键可刷新活跃会话列表。
- 按下 `Esc` 键可关闭切换器。
- 选择 `+new`，输入提示语后按 `Enter` 键即可调度一个新的活跃会话。如果希望为该新会话指定特定模型，可先按 `Tab` 键进行选择。
## LaTeX 数学公式渲染

TUI 的 Markdown 处理流程会将 LaTeX 数学公式以内联形式渲染：`$,E = mc^2$,` 和 `$$\frac{a}{b}$$` 会以 Unicode 格式的数学公式呈现，而非原始的 TeX 源代码。该功能同时支持内联公式和块级公式；对于不支持的格式，则会将其以代码块的形式显示，从而确保内容仍可复制。

此功能始终处于开启状态，无需任何配置。传统 CLI 版本则会保留原始的 TeX 格式。

## 轻量终端检测

TUI 会自动检测终端类型，并据此切换到相应的浅色主题。检测过程分为三层：

1. `HERMES_TUI_THEME` 环境变量——优先级最高。其取值包括 `light`、`dark`，或直接输入 6 位十六进制颜色代码（例如 `ffffff`、`1a1a2e`）。
2. `COLORFGBG` 环境变量——即 xterm 系列终端常用的“我的背景色是什么？”提示功能。
3. 通过 OSC 11 探测终端背景色——适用于未设置 `COLORFGBG` 的现代终端（如 Ghostty、Warp、iTerm2、WezTerm、Kitty）。

如果您希望无论终端类型如何都始终使用浅色主题：

```bash
export HERMES_TUI_THEME=light
```

## 忙碌状态指示器样式

状态栏中的忙碌状态指示器支持自定义——默认情况下，当智能体正在工作时，会每2.5秒切换一次Hermes的可爱表情主题。您可以通过配置文件或`/indicator`命令来选择其他样式：

```yaml
display:
  tui_status_indicator: kaomoji   # kaomoji | emoji | unicode | ascii
```

或者可以在会话中直接使用：`/indicator emoji`（等等）。这些样式均配有匹配的符号宽度，因此状态栏在旋转时不会出现抖动。

## 自动恢复

默认情况下，`hermes --tui` 每次启动都会开启一个全新的会话。若希望自动重新连接到最近的 TUI 会话（适用于终端或 SSH 连接意外中断的情况），可启用该功能：

```bash
export HERMES_TUI_RESUME=1          # most-recent TUI session
# or:
export HERMES_TUI_RESUME=<session-id>   # specific session
```

如需取消设置该变量，可直接传递 `--resume <id>` 参数，以便在每次启动时进行覆盖。

## 状态行

TUI 的状态行会实时显示代理的状态：

为会话命名后，其标题会以高亮颜色的徽章形式显示在状态行的最右侧。该标题会替代工作区标签，且在终端宽度较窄时会自动截断。

| 状态 | 含义 |
|--------|---------|
| `starting agent…` | 会话 ID 已激活，各类工具和技能仍在加载中。此时您可以输入内容——消息会在准备好后进入队列并发送。 |
| `ready` | 代理处于空闲状态，可接收输入。 |
| `thinking…` / `running…` | 代理正在推理或运行某个工具。 |
| `interrupted` | 当前轮次已被取消；请按 Enter 键重新发送。 |
| `forging session…` / `resuming…` | 正在建立初始连接或执行 `--resume` 重连操作。 |

不同主题下的状态栏颜色及阈值与传统 CLI 保持一致——如需自定义设置，请参阅 [主题](features/skins.md) 文档。

状态行还会显示：

- **包含 Git 分支的工作目录** — `~/projects/hermes-agent (docs/two-week-gap-sweep)`。当在侧边终端执行 `git checkout` 操作时（基于 mtime 缓存），分支后缀会随之更新，这样文本用户界面就能反映您当前实际使用的分支，而非启动时的分支状态。
- **每次提示符的耗时** — 在对话进行中显示为 `⏱ 12s/3m 45s`（实时显示），对话结束后则固定为 `⏲ 32s / 3m 45s`。第一个数字表示距离上次用户发送消息的时间，第二个数字表示整个会话的总时长。每次出现新提示符时，这些数值都会重置。
- **`🗜️ N`** — 当前会话被自动压缩的次数。在首次发生压缩时会显示该标识。
- **`▶ N`** — 当前会话中正在运行的 `/bg` 任务数量。只要存在至少一个正在处理的任务，就会显示此标识。
- **`⚠ YOLO`** — 每当启用 YOLO 模式时（通过 `hermes --yolo`、`/yolo` 或 `HERMES_YOLO_MODE=1`）都会出现此警告标识。同样的标识也会出现在启动横幅中，因此您不可能在未注意到该提示的情况下启动自动批准模式的会话。

## 配置

文本用户界面支持所有标准的 Hermes 配置：`~/.hermes/config.yaml`、配置文件、角色设定、皮肤样式、快捷命令、凭证池、内存提供器以及工具/技能的启用设置。目前并不存在专门针对文本用户界面的配置文件。

另有几项键值可用于具体调整文本用户界面的显示效果：

```yaml
display:
  skin: default              # any built-in or custom skin
  personality: helpful
  details_mode: collapsed    # hidden | collapsed | expanded — global accordion default
  sections:                  # optional: per-section overrides (any subset)
    thinking: expanded       # always open
    tools: expanded          # always open
    activity: collapsed      # opt back IN to the activity panel (hidden by default)
  mouse_tracking: all        # off | wheel | buttons | all (or true/false for back-compat).
                             #   wheel   — 1000+1006 (scroll + click; no drag, no hover —
                             #             recommended inside tmux to silence the prompt-row
                             #             "No image in clipboard" spam from hover events)
                             #   buttons — adds 1002 for terminal-side drag selection
                             #   all     — adds 1003 for hover (scrollbar paginate-on-hover,
                             #             link mouseenter, etc.)
```

运行时切换选项：

- `/details [hidden|collapsed|expanded|cycle]` — 设置全局显示模式  
- `/details <section> [hidden|collapsed|expanded|reset]` — 覆盖单个板块的显示设置  
  （可选板块：`thinking`、`tools`、`subagents`、`activity`）

**默认显示设置**

该 TUI 为各个板块预置了合理的默认值，会将对话流程以实时文字记录的形式呈现，而非仅显示一排箭头符号：

- `thinking` — **展开状态**。模型在推理过程中会即时显示推理内容。  
- `tools` — **展开状态**。工具调用及其结果会完整展示。  
- `subagents` — 采用全局的 `details_mode` 设置（默认情况下以箭头形式折叠显示——只有在实际分配子任务时才会显示内容）。  
- `activity` — **隐藏状态**。大多数日常使用场景中，那些环境相关的元信息（如网关提示、终端格式提示、后台通知等）都属于干扰信息。不过，工具调用失败时，对应行的信息仍会直接显示；当所有面板均被隐藏时，这些环境错误或警告则会通过浮动警报形式呈现。

针对单个板块的覆盖设置优先于该板块的默认值以及全局的 `details_mode`。如需调整布局，可使用以下命令：

- `display.sections.thinking: collapsed` — 将推理内容重新置于箭头符号下方显示  
- `display.sections.tools: collapsed` — 将工具调用内容重新置于箭头符号下方显示  
- `display.sections.activity: collapsed` — 重新显示活动面板  
- 运行时使用 `/details <section> <mode>` 命令  

只要在 `display.sections` 中明确设置了相关选项，其优先级将高于默认值，因此现有的配置无需修改即可继续正常使用。

## 会话管理

TUI与传统CLI之间会共享会话——二者都会向同一个`~/.hermes/state.db`文件写入数据。你可以在其中一个界面中启动会话，然后在另一个界面中继续使用该会话。会话选择器会显示来自这两种来源的会话，并标注其来源类型。

有关会话的生命周期管理、搜索、压缩及导出功能，请参阅[会话](sessions.md)文档。

## TUI如何与其网关通信

默认情况下，TUI会自行创建一个进程内的网关，因此每个TUI实例都是独立运行的——无需进行任何配置。

你可能在代码库或日志中看到`HERMES_TUI_GATEWAY_URL`这个环境变量。这实际上是**网页控制台内部的连接细节**，而非面向用户的外部远程连接选项。当你打开控制台的“聊天”标签页（通过`hermes dashboard`命令进入 `/chat`路径）时，控制台的Web服务器会启动一个嵌入式的TUI子进程，并注入`HERMES_TUI_GATEWAY_URL`地址，使得该子进程能够通过回环WebSocket连接（`/api/ws`）与控制台自身的进程内`tui_gateway`进行通信。`/api/ws`接口仅存在于控制台服务器（`hermes_cli/web_server.py`）中，其存在时间与权限均与该进程绑定。

目前并不存在“将任意TUI连接到任意独立网关端口”的通用模式。尤其是兼容OpenAI的API服务器（`hermes gateway`或`api_server`平台）根本不会提供`/api/ws`接口——它仅负责处理模型相关的请求（如`/v1/chat/completions`、`/v1/models`等），并且刻意不暴露TUI的JSON-RPC控制通道。若将`HERMES_TUI_GATEWAY_URL`设置为该端口，将会出现404错误。

如果希望多个界面共享同一组会话，可使用共享的 `~/.hermes/state.db` 文件（详见 [会话管理](sessions.md)），或利用网页控制台内置的聊天功能（详见 [网页控制台](features/web-dashboard.md#chat)）——而非手动设置网关地址。

## 恢复使用传统 CLI

直接运行 `hermes` 命令（不加 `--tui` 参数）时，默认会使用传统 CLI。若希望某台机器优先使用 TUI，可在 `~/.hermes/config.yaml` 中设置 `display.interface: tui`（此设置持久有效），或在 shell 配置文件中设置 `HERMES_TUI=1`（仅对当前 shell 生效）。如需恢复传统 CLI，可设置 `interface: cli` 或取消该环境变量，或临时使用 `hermes --cli` 命令。

若 TUI 无法启动（如缺少 Node 环境、缺失依赖包或存在 TTY 问题），Hermes 会输出诊断信息并自动切换回传统模式，而不会让用户陷入困境。

## 相关内容

- [CLI 接口](cli.md)——完整的命令及快捷键参考（所有界面通用）
- [会话管理](sessions.md)——会话恢复、分支切换及历史记录功能
- [皮肤与主题](features/skins.md)——自定义标题栏、状态栏及覆盖层主题
- [语音模式](features/voice-mode.md)——两种界面均支持
- [配置设置](configuration.md)——所有配置键说明
