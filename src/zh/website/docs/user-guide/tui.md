---
sidebar_position: 2
title: "TUI"
description: "Launch the modern terminal UI for Hermes — mouse-friendly, rich overlays, and non-blocking input."
---

# TUI

TUI 是 Hermes 的现代化前端界面——它是一种终端用户界面，与 [经典 CLI](cli.md) 使用相同的 Python 运行时。同样的智能体、相同的会话、相同的斜杠命令；仅为与它们交互提供了更简洁、响应更迅速的体验。

这是交互式运行 Hermes 的推荐方式。

## 启动

```bash
# Launch the TUI
hermes --tui

# Resume the latest TUI session (falls back to the latest classic session)
hermes --tui -c
hermes --tui --continue

# Resume a specific session by ID or title
hermes --tui -r 20260409_000000_aa11bb
hermes --tui --resume "my t0p session"

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

当设置 `display.interface: tui` 后，基础版的 `hermes`（以及 `hermes chat`）将会启动 TUI 模式。显式的命令参数始终具有优先级——若只需单次使用传统 REPL 模式，可运行 `hermes --cli`；而当配置默认值为 `cli` 时，若想强制启用 TUI，则可使用 `hermes --tui` 或 `HERMES_TUI=1`。

传统 CLI 仍是默认模式。所有在 [CLI 接口文档](cli.md) 中说明的功能——如斜杠命令、快速命令、技能预加载、角色设定、多行输入、中断处理等——在 TUI 模式下均可正常使用。

## 为何选择 TUI 模式

- **即时显示首屏**：应用尚未完全加载时，标题栏就已呈现，因此 Hermes 启动过程中终端不会出现卡顿。
- **非阻塞式输入**：可在会话就绪前直接输入并排队发送消息。代理上线后，您的第一条提示语会立即被发送。
- **丰富的叠加界面**：模型选择器、会话选择器以及确认与澄清提示均以模态面板形式显示，而非内联流程。
- **实时会话面板**：各类工具和技能会在初始化过程中逐步显示出来。
- **鼠标友好型选择**：可通过拖动高亮选中内容，背景颜色统一，无需依赖 SGR 反色效果；复制操作可使用终端常规的复制手势。
- **跨屏幕渲染优化**：差异更新机制确保流式传输时无闪烁现象，退出后也不会留下滚动历史记录的杂乱内容。
- **强大的文本编辑功能**：支持长文本片段的内联折叠、`Cmd+V` / `Ctrl+V` 的文本粘贴（同时支持剪贴板中的图片作为备选）、括号包裹式粘贴保护，以及图像/文件路径的标准化附加。

原有的 [皮肤样式](features/skins.md) 和 [角色设定](features/personality.md) 功能同样适用。您可以在会话进行中通过 `/skin ares`、`/personality pirate` 等命令切换样式，界面会实时重新渲染。有关所有可自定义参数的完整列表，以及哪些参数适用于传统 CLI 模式、哪些适用于 TUI 模式，请参阅 [皮肤与主题](features/skins.md)——TUI 模式会继承标题栏配色、界面颜色、提示符符号/颜色、会话显示内容、补全菜单、选中区域背景、`tool_prefix` 以及 `help_header` 等设置。

### 可折叠的标题栏区域

TUI 启动时的标题栏会将运行时信息分为四个可折叠的区域，每个区域标题旁都有一个 `▸` / `▾` 的箭头：

| 区域 | 默认状态 |
|------|----------|
| 工具 | 展开 |
| 技能 | 折叠 |
| 系统提示符 | 折叠 |
| MCP 服务器 | 折叠 |

点击任意区域标题（或其箭头）即可切换该区域的显示状态。工具列表默认处于展开状态，因为它是会话启动时最常被查看的区域；而技能、系统提示符和 MCP 服务器默认处于折叠状态，这样即便您安装了数十种技能或配置了大量 MCP 服务器，标题栏也能保持简洁。这些状态仅作用于当前标题栏实例，因此下次启动时会恢复为默认设置。

## 系统要求

- **Node.js** ≥ 20——TUI 作为从 Python CLI 启动的子进程运行。可使用 `hermes doctor` 命令检测版本是否符合要求。
- **TTY 环境**——与传统 CLI 一样，若通过标准输入管道传递数据或运行在非交互式环境中，系统会自动切换为单次查询模式。

首次启动时，Hermes 会将 TUI 所需的 Node.js 依赖包安装到 `ui-tui/node_modules` 目录中（此操作仅执行一次，耗时几秒）。后续启动速度会很快。如果您升级了 Hermes 版本，只要源代码比已发布的版本更新，TUI 相关包会自动重新构建。

:::提示：如何在多个 git worktree 环境下使用？
那些在多个 worktree 中运行 `hermes --tui --dev` 的开发者，可以共享同一个 `node_modules` 目录，而无需在每个工作树中单独安装依赖——详情请参阅 [从 Worktree 运行 TUI 与桌面界面](../developer-guide/worktree-ui-dev.md)。
:::

### 外部预构建版本

那些预编译了 TUI 包的发行版（如 Nix 包或系统包），可以让 Hermes 直接使用这些预编译版本：

```bash
export HERMES_TUI_DIR=/path/to/prebuilt/ui-tui
hermes --tui
```

该目录中必须包含 `dist/entry.js` 文件。

## 绑定键

其绑定键与 [Classic CLI](cli.md#keybindings) 完全一致。唯一的行为差异如下：

- **鼠标拖动** 时，文本会被高亮显示，并带有统一的选中背景。
- **`Cmd+V` / `Ctrl+V`** 会首先尝试常规文本粘贴，若失败则尝试读取 OSC52 或系统原生剪贴板内容；当剪贴板或粘贴的内容为图片时，最终会以图片形式附加。
- **`/terminal-setup`** 会安装适用于本地 VS Code、Cursor 和 Windsurf 终端的绑定键，从而在 macOS 上实现更完善的 `Cmd+Enter` 操作以及撤销/重做功能。
- **斜杠命令自动补全** 会以带说明的浮动面板形式显示，而非内联下拉菜单。
- **`Ctrl+X`** 会打开实时会话切换器。当有排队消息被高亮显示（即在智能体仍在运行时发送的消息）时，该命令仍会删除该排队消息。**`Esc`** 则会取消编辑操作，取消高亮显示但不会删除内容。
- **`Ctrl+G` / `Ctrl+X Ctrl+E`** — 会在 `$EDITOR` 中打开当前输入缓冲区，便于编写多行或较长的提示语；保存后退出时，这些内容会被作为新的提示语发送出去。

## 斜杠命令

所有斜杠命令均保持原有功能不变。其中部分命令由 TUI 所控制——它们会生成更丰富的输出，或以覆盖层形式显示，而非内联面板：

| 命令 | TUI 行为 |
|------|----------|
| `/help` | 以分类形式的覆盖层展示命令列表，可使用方向键导航 |
| `/sessions`（别名 `/switch`） | 实时会话切换器——列出所有正在运行的 TUI 会话，可在其间切换、关闭会话或启动新会话 |
| `/model` | 按提供方分类的模态模型选择器，同时显示成本提示 |
| `/skin` | 实时预览功能——在浏览主题时即可立即应用更改 |
| `/details` | 切换工具调用的详细信息显示模式（全局或针对特定部分） |
| `/usage` | 显示丰富的令牌、成本及上下文信息面板 |
| `/agents`（别名 `/tasks`） | 可视化监控覆盖层——展示实时的子智能体树结构，提供终止/暂停控制功能，以及各分支的成本、令牌和文件使用统计，还会记录逐步执行历史 |
| `/reload` | 重新读取 `~/.hermes/.env` 文件并加载到正在运行的 TUI 进程中，这样新增的 API 密钥无需重启即可生效 |
| `/mouse [on\|off\|toggle\|wheel\|buttons\|all]` | 允许在运行时选择鼠标跟踪预设（该设置也会保存到 `config.yaml` 文件中的 `display.mouse_tracking` 字段）。`wheel`（1000+1006）模式可保持滚轮滚动功能，同时避免因悬停事件导致 tmux 在提示行上方频繁显示“剪贴板中没有图片”的提示；`buttons` 模式则支持拖动选择；默认值为 `all`，即采用基于悬停的 UI 方式。 |

其他所有斜杠命令（包括已安装的技能、快捷命令以及个性设置切换功能）的运行方式都与 Classic CLI 完全相同。详情请参阅 [斜杠命令参考文档](../reference/slash-commands.md)。

## 实时会话切换器

当您希望使用一个终端作为多个 TUI 会话的调度器时，可使用实时会话切换器。该工具仅列出当前在该 TUI 进程中正在运行的会话；已关闭的会话仍会以记录形式保存，可通过 `/resume` 命令或 `hermes --tui --resume <id-or-title>` 重新打开。

可通过以下任意方式打开该切换器：

- 在 TUI 中按下 `Ctrl+X`。
- 输入 `/sessions` 或 `/switch`。
- 输入 `/sessions new` 立即创建一个新的实时会话。
- 点击状态行中的 “N 个实时会话” 数字。

<img alt="包含一个正在运行的会话及“+新建”选项行的 Hermes TUI 会话调度器" src="/docs/img/docs/tui-session-orchestrator/session-orchestrator.png" />

<video controls muted loop playsInline src="/docs/img/docs/tui-session-orchestrator/session-orchestrator-demo.mp4" title="Hermes TUI 会话调度器演示" style={{maxWidth: '100%'}}></video>

在切换器内部：

- 使用 `↑` / `↓` 键移动选择项；鼠标点击也可选中对应行。
- 按下 `Enter` 键可切换到选中的实时会话。
- 按下 `Ctrl+D` 键可关闭选中的实时会话。
- 按下 `Ctrl+N` 键可启动一个空的实时会话。
- 按下 `Ctrl+R` 键可刷新实时会话列表。
- 按下 `Esc` 键可关闭切换器。
- 选择 `+new`，输入提示语后按 `Enter` 即可启动一个新的实时会话。如果希望仅为该新会话指定特定模型，可先按 `Tab` 键进行选择。

## LaTeX 数学公式渲染

TUI 的 Markdown 处理流程会将 LaTeX 数学公式以内联形式渲染：`$

```bash
export HERMES_TUI_THEME=light
```

## 忙碌状态指示器样式

状态栏中的忙碌状态指示器是可配置的——默认情况下，当智能体正在工作时，它会每隔2.5秒切换一次Hermes的可爱表情主题。您可以通过配置文件或`/indicator`命令来选择其他样式：

```yaml
display:
  tui_status_indicator: kaomoji   # kaomoji | emoji | unicode | ascii
```

或者可在会话中直接使用：`/indicator emoji`（等等）。这些样式均配备了匹配的符号宽度，因此状态栏在旋转时不会出现抖动。

## 自动恢复

默认情况下，`hermes --tui` 每次启动都会开启一个全新的会话。若希望自动重新连接到最近的 TUI 会话（在终端或 SSH 连接意外中断时非常有用），可启用该功能：

```bash
export HERMES_TUI_RESUME=1          # most-recent TUI session
# or:
export HERMES_TUI_RESUME=<session-id>   # specific session
```

如需取消设置该变量，可直接传递 `--resume <id>` 参数，以便在每次启动时进行覆盖。

## 状态行

TUI 的状态行会实时显示智能体的运行状态：

| 状态 | 含义 |
|------|------|
| `starting agent…` | 会话 ID 已激活，各类工具和技能仍在加载中。此时可输入内容——消息会在准备好后被发送。 |
| `ready` | 智能体处于空闲状态，可接收输入。 |
| `thinking…` / `running…` | 智能体正在推理或运行某个工具。 |
| `interrupted` | 当前轮次已被取消；请按 Enter 键重新发送。 |
| `forging session…` / `resuming…` | 正在建立初始连接或执行 `--resume` 重连操作。 |

不同主题下的状态栏颜色及阈值与传统 CLI 保持一致——如需自定义，可参阅 [主题](features/skins.md) 文档。

状态行还会显示以下信息：

- **包含 git 分支的工作目录** —— 例如 `~/projects/hermes-agent (docs/two-week-gap-sweep)`。当在侧边终端执行 `git checkout` 操作时（基于修改时间缓存），分支后缀会随之更新，这样 TUI 显示的便是您当前实际使用的分支，而非启动时的分支。
- **每个提示符对应的耗时** —— 在轮次进行中时会显示为 `⏱ 12s/3m 45s`，轮次结束后则固定为 `⏲ 32s / 3m 45s`。第一个数值表示自上次用户发送消息以来的时间，第二个数值表示整个会话的总时长。每次出现新提示符时，这些数值都会重置。
- **`🗜️ N`** —— 当前会话被自动压缩的次数。在首次发生压缩时会显示该标识。
- **`▶ N`** —— 当前会话中正在运行的 `/background` 任务数量。只要存在至少一个正在运行的任务，就会显示此标识。
- **`⚠ YOLO`** —— 每当启用 YOLO 模式（通过 `hermes --yolo`、`/yolo` 或 `HERMES_YOLO_MODE=1`）时，此处都会显示警告标识。启动横幅中也会出现相同的图标，因此您无论如何都无法在不注意的情况下启动自动批准模式的会话。

## 配置

TUI 支持所有标准的 Hermes 配置项：`~/.hermes/config.yaml`、配置文件、人格设置、主题、快捷命令、凭证池、内存提供器以及工具/技能的启用选项。目前并未存在专门针对 TUI 的配置文件。

另有几组键用于专门调整 TUI 的界面显示效果：

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

**运行时切换选项：**

- `/details [hidden|collapsed|expanded|cycle]` — 设置全局模式  
- `/details <section> [hidden|collapsed|expanded|reset]` — 覆盖单个区域  
  （可选区域：`thinking`、`tools`、`subagents`、`activity`）

**默认显示设置**

该 TUI 预设了针对各区域的默认配置，会将对话流程以实时文本形式呈现，而非一整行箭头符号：

- `thinking` — **展开状态**。模型生成推理过程时会即时显示在相应位置。  
- `tools` — **展开状态**。工具调用及其结果会完整展示。  
- `subagents` — 采用全局 `details_mode` 设置（默认情况下以箭头符号隐藏，直到实际发起子任务才会显示内容）。  
- `activity` — **隐藏状态**。大多数日常使用场景中，诸如网关提示、终端格式相关提示以及背景通知等辅助信息都属于冗余内容。不过，工具调用失败时仍会在对应行直接显示错误信息；当所有面板均被隐藏时，系统会通过浮动警报来提示异常或警告。

针对单个区域的自定义设置会优先于该区域的默认配置以及全局 `details_mode`。如需调整布局，可使用以下命令：

- `display.sections.thinking: collapsed` — 将思考过程重新显示在箭头符号下方  
- `display.sections.tools: collapsed` — 将工具调用信息重新隐藏在箭头符号后  
- `display.sections.activity: collapsed` — 再次隐藏活动面板  
- 运行时使用 `/details <section> <mode>` 命令  

只要在 `display.sections` 中明确指定某项设置，该设置就会覆盖默认值，因此现有配置无需修改即可继续正常使用。

## 会话管理

TUI 与传统 CLI 之间会共享会话数据——二者都会写入同一个 `~/.hermes/state.db` 文件。你可以在其中一个界面中启动会话，然后在另一个界面中继续使用该会话。会话选择器会同时显示来自两个来源的会话，并标注其来源类型。

有关会话的生命周期管理、搜索功能、压缩处理及导出方法，请参阅 [Sessions](sessions.md) 文档。

## TUI 如何与网关通信

默认情况下，TUI 会自行启动一个进程内网关，因此每个 TUI 实例都是独立运行的，无需额外配置。

你可能在代码库或日志中看到 `HERMES_TUI_GATEWAY_URL` 这一环境变量。实际上，这只是**网页控制台内部的连接细节**，并非面向用户的远程连接选项。当你打开控制台的“聊天”标签页（通过 `hermes dashboard` → `/chat`）时，控制台的 Web 服务器会启动一个嵌入式的 TUI 子进程，并注入 `HERMES_TUI_GATEWAY_URL`，使得该子进程能够通过回环 WebSocket 接口（`/api/ws`）连接到控制台自身的进程内 `tui_gateway`。`/api/ws` 接口仅存在于控制台服务器（`hermes_cli/web_server.py`）中，其生命周期及权限认证均与该服务器绑定。

目前并不存在“将任意 TUI 连接到任意独立网关端口”的通用模式。尤其是兼容 OpenAI 的 API 服务器（`hermes gateway` 或 `api_server` 平台）并不提供 `/api/ws` 接口——它仅用于处理模型相关请求（如 `/v1/chat/completions`、`/v1/models` 等），并且刻意不暴露 TUI 所使用的 JSON-RPC 控制通道。若将 `HERMES_TUI_GATEWAY_URL` 设置为该端口，将会出现 404 错误。

如果你希望多个界面共享同一组会话，应使用共享的 `~/.hermes/state.db` 文件（详见 [Sessions](sessions.md)），或利用控制台内置的聊天功能（参见 [Web Dashboard](features/web-dashboard.md#chat)），而非手动指定网关地址。

## 恢复到传统 CLI 模式

直接运行 `hermes` 命令（不加上 `--tui` 参数）时，默认仍会使用传统 CLI。若希望让系统优先使用 TUI，可在 `~/.hermes/config.yaml` 文件中设置 `display.interface: tui`（此设置持久有效），或在 shell 配置文件中设置 `HERMES_TUI=1`（仅对当前 shell 有效）。如需恢复传统模式，可设置 `interface: cli`、删除该环境变量，或临时使用 `hermes --cli` 命令。

如果 TUI 启动失败（例如缺少 Node 环境、缺失依赖包或存在 TTY 相关问题），Hermes 会输出诊断信息并自动回退到传统模式，避免用户陷入困境。

## 参考资料

- [CLI 接口](cli.md) — 完整的命令行参数及快捷键参考（两者共享）  
- [会话管理](sessions.md) — 会话恢复、分支处理及历史记录功能  
- [皮肤与主题](features/skins.md) — 自定义标题栏、状态栏及覆盖层的外观  
- [语音模式](features/voice-mode.md) — 两种界面均支持该功能  
- [配置选项](configuration.md) — 所有配置键的说明
