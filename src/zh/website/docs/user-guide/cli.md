---
sidebar_position: 1
title: "CLI Interface"
description: "Master the Hermes Agent terminal interface — commands, keybindings, personalities, and more"
---

# CLI 接口

Hermes Agent 的 CLI 是一种完整的终端用户界面（TUI），而非网页界面。它具备多行编辑、斜杠命令自动补全、对话历史记录、中断与重定向功能，以及工具输出的实时流式显示能力，专为习惯在终端中操作的用户设计。

:::提示 首次设置
只需执行一条命令 `hermes setup --portal`，即可开始使用 `hermes chat` 功能。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

:::提示
Hermes 还提供了一个功能先进的 TUI，支持模态覆盖层、鼠标选择以及非阻塞式输入。可通过 `hermes --tui` 命令启动该界面，更多说明请参考 [TUI](tui.md) 文档。
:::

## 运行 CLI

```bash
# Start an interactive session (default)
hermes

# Single query mode (non-interactive)
hermes chat -q "Hello"

# With a specific model
hermes chat --model "anthropic/claude-sonnet-4"

# With a specific provider
hermes chat --provider nous        # Use Nous Portal
hermes chat --provider openrouter  # Force OpenRouter

# With specific toolsets
hermes chat --toolsets "web,terminal,skills"

# Start with one or more skills preloaded
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -q "open a draft PR"

# Resume previous sessions
hermes --continue             # Resume the most recent CLI session (-c)
hermes --resume <session_id>  # Resume a specific session by ID (-r)

# Verbose mode (debug output)
hermes chat --verbose

# Isolated git worktree (for running multiple agents in parallel)
hermes -w                         # Interactive mode in worktree
hermes -w -z "Fix issue #123"     # Single query in worktree
```

## 界面布局

<img className="docs-terminal-figure" src="/docs/img/docs/cli-layout.svg" alt="Hermes CLI界面风格化预览图，展示了标题栏、对话区域以及固定输入提示框。" />
<p className="docs-figure-caption">Hermes CLI的标题栏、对话流以及固定输入提示框均以稳定的图表形式呈现，而非易损坏的文本艺术效果。</p>

欢迎标题栏可让您一目了然地查看所使用的模型、终端后端、工作目录、可用工具以及已安装的技能。

### 状态栏

状态栏始终显示在输入区域上方，并会实时更新内容：

```
 ⚕ claude-sonnet-4-20250514 │ 12.4K/200K │ [██████░░░░] 6% │ $0.06 │ 15m
```

| 元素 | 描述 |
|---------|-------------|
| 模型名称 | 当前使用的模型（若超过26个字符则会被截断显示） |
| 令牌计数 | 已使用的上下文令牌数 / 最大上下文窗口大小 |
| 上下文条 | 带有颜色编码阈值指示的可视化填充条 |
| 成本 | 会话预估费用（对于未知或免费模型则显示为 `n/a`） |
| 🗜️ N | **上下文压缩次数** — 表示当前会话已被自动压缩的次数。首次发生压缩时会显示该数值。 |
| ▶ N | **正在运行的后台任务数** — 表示当前会话中仍有多少个 `/background` 提示正在处理中。只要存在至少一个正在运行的任务，就会显示此数值。 |
| 时长 | 会话已持续的时间 |
| ⚠ YOLO | **YOLO模式警告** — 每当 `HERMES_YOLO_MODE` 被启用时（无论是在启动时使用 `hermes --yolo`，还是在会话进行中切换为 `/yolo`）都会显示此警告。该提示与顶部的横幅警告相同，旨在提醒用户当前处于自动批准模式。 |

该条状图会根据终端宽度自动调整布局：在≥76列的终端上显示完整信息，在52–75列的终端上显示紧凑版，在小于52列的终端上则仅显示最基本的信息（模型名称、时长，以及处于YOLO模式时的专用标识）。

**上下文颜色编码规则：**

| 颜色 | 阈值 | 含义 |
|-------|------|------|
| 绿色 | < 50% | 上下文空间充足 |
| 黄色 | 50–80% | 接近满载 |
| 橙色 | 80–95% | 接近上限 |
| 红色 | ≥ 95% | 几乎溢出 — 建议使用 `/compress` 进行压缩 |

如需查看包括各类别成本（输入令牌与输出令牌）在内的详细数据，可使用 `/usage` 命令。在 `openai-codex` 提供商上，`/usage` 还会显示 ChatGPT 账户中已累积的用量限额重置次数（“您已累积 N 次重置机会 — 请使用 /usage reset 来激活”）。`/usage reset` 命令可消耗一次累积的重置机会，从而完全恢复5小时及每周的用量限制。当您的用量尚未用尽时，Hermes 会拒绝允许用户使用重置功能（因为累积的重置机会可恢复全部额度，提前使用只会造成浪费）——如需强制使用，可输入 `/usage reset --force`。

### 会话续接显示功能

当恢复之前的会话时（使用 `hermes -c` 或 `hermes --resume <id>`），在顶部横幅与输入提示之间会出现一个“历史对话”面板，简要概括对话记录。详细信息及相关配置请参阅 [会话 — 会话续接时的对话摘要](sessions.md#conversation-recap-on-resume)。

## 快捷键

| 键 | 功能 |
|-----|------|
| `Enter` | 发送消息 |
| `Alt+Enter`、`Ctrl+J` 或 `Shift+Enter` | 换行（多行输入）。`Shift+Enter` 需要终端能够将其与 `Enter` 区分开来 — 具体要求见下文。在 Windows Terminal 中，`Alt+Enter` 被终端用于切换全屏模式；此时请使用 `Ctrl+Enter` 或 `Ctrl+J`。 |
| `Alt+V` | 在终端支持的情况下，从剪贴板粘贴图片 |
| `Ctrl+V` | 粘贴文本，并在合适时机附上剪贴板中的图片 |
| `Ctrl+B` | 当语音模式已启用时，开始/停止语音录音（语音录音的默认快捷键为 `ctrl+b`） |
| `Ctrl+G` | 在 `$EDITOR`（如 vim/nvim/nano/VS Code 等）中打开当前的输入缓冲区。保存并退出后，编辑后的文本将作为下一个提示发送出去 — 这对于较长、包含多段文字的提示尤为实用。 |
| `Ctrl+X Ctrl+E` | 用于外部编辑器的 Emacs 风格替代快捷键，功能与 `Ctrl+G` 相同。 |
| `Ctrl+C` | 中断代理运行（在2秒内再次按下可强制退出） |
| `Ctrl+D` | 退出程序 |
| `Ctrl+Z` | 将 Hermes 暂停到后台（仅适用于 Unix 系统）。可在终端中输入 `fg` 来恢复其运行状态。 |
| `Tab` | 接受自动建议（即虚线显示的文本）或自动补全的斜杠命令 |

**多行粘贴预览功能。** 当您粘贴多行内容时，CLI 会显示一个简洁的单行预览信息（`[已粘贴：47行，1,842个字符 — 按Enter键发送]`），而不会将全部内容直接显示在滚动历史中。实际发送的内容仍是完整的多行文本，这只是为了提升显示效果。

**最终回复中的 Markdown 格式去除功能。** CLI 会从代理的最终回复中移除较为繁琐的 Markdown 包裹结构以及 `**粗体**` / `*斜体*` 格式标记，从而使回复以易于在终端中阅读的纯文本形式呈现，而非原始的 Markdown 代码。代码块和列表格式则会被保留。此功能不会影响网关平台或工具生成的回复 — 它们会保留原有的 Markdown 格式以便直接渲染。

## 斜杠命令

输入 `/` 即可查看自动补全下拉菜单。Hermes 支持大量 CLI 斜杠命令、动态技能命令以及用户自定义的快捷命令。

常见示例：

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示命令帮助信息 |
| `/model` | 查看或更改当前使用的模型 |
| `/tools` | 列出当前可用的工具 |
| `/skills browse` | 浏览技能中心及官方提供的可选技能 |
| `/background <prompt>` | 在独立的后台会话中运行指定的提示 |
| `/skin` | 查看或切换当前激活的 CLI 界面主题 |
| `/voice on` | 启用 CLI 语音模式（按 `Ctrl+B` 开始录音） |
| `/voice tts` | 切换 Hermes 回复的语音播放功能 |
| `/reasoning high` | 提高推理强度 |
| `/title My Session` | 为当前会话命名 |
| `/status` | 显示会话相关信息 — 包括模型、用户配置、令牌数量、会话时长 — 后跟一个本地的 **会话摘要** 区块（显示最近的对话轮次数、最常使用的工具、处理过的文件，以及最新的用户提示和助手回复）。该功能完全在本地计算完成，不会调用大型语言模型。 |
| `/sessions` | 在传统的 CLI 界面中打开交互式会话选择器（与 TUI 使用的界面相同）。可通过输入文字进行筛选，使用方向键导航，按 Enter 键继续会话。 |

如需查看所有内置的 CLI 命令和消息相关命令的完整列表，请参阅 [斜杠命令参考手册](../reference/slash-commands.md)。

关于设置、提供商选择、静音调节以及消息发送/Discord 语音功能的使用方法，可参阅 [语音模式](features/voice-mode.md) 文档。

:::tip
命令不区分大小写 — `/HELP` 与 `/help` 具有相同功能。已安装的技能也会自动转换为斜杠命令。
:::

## 快捷指令

您可以定义自定义指令，这些指令能够在不调用大型语言模型的情况下立即执行shell命令。此类指令既可在CLI环境中使用，也可在消息平台（如Telegram、Discord等）中使用。

```yaml
# ~/.hermes/config.yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
  restart:
    type: alias
    target: /gateway restart
```

随后在任意聊天窗口中输入 `/status`、`/gpu` 或 `/restart` 即可。更多示例请参阅[配置指南](/user-guide/configuration#quick-commands)。

## 启动时预加载技能

如果您已确定本次会话需要启用的技能，可在启动时直接指定它们：

```bash
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -s github-auth
```

在首次对话开始之前，Hermes 会将每个已命名的技能加载到会话提示语中。该机制在交互模式和单次查询模式下均适用。

## 技能斜杠命令

位于 `~/.hermes/skills/` 目录中的所有已安装技能都会自动被注册为斜杠命令，该技能的名称即成为对应的命令：

```
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor

# Just the skill name loads it and lets the agent ask what you need:
/excalidraw
```

## 人格设定

设置预定义的人格模式，以改变智能体的语气：

```
/personality pirate
/personality kawaii
/personality concise
```

内置的对话风格包括：`helpful`、`concise`、`technical`、`creative`、`teacher`、`kawaii`、`catgirl`、`pirate`、`shakespeare`、`surfer`、`noir`、`uwu`、`philosopher` 和 `hype`。您还可以在 `~/.hermes/config.yaml` 文件中定义自定义的对话风格：

```yaml
personalities:
  helpful: "You are a helpful, friendly AI assistant."
  kawaii: "You are a kawaii assistant! Use cute expressions..."
  pirate: "Arrr! Ye be talkin' to Captain Hermes..."
  # Add your own!
```

## 多行输入

输入多行消息有两种方式：

1. **`Alt+Enter`、`Ctrl+J` 或 `Shift+Enter`** —— 用于插入新行
2. **反斜杠续行** —— 在行尾使用 `\` 来继续输入内容：

```
❯ Write a function that:\
  1. Takes a list of numbers\
  2. Returns the sum
```

:::info  
支持粘贴多行文本——可使用上述任意换行键，或直接粘贴内容。  
:::

### Shift+Enter 兼容性  

默认情况下，大多数终端对 `Enter` 和 `Shift+Enter` 发送相同的字节序列，因此应用程序无法区分二者。只有当终端通过 [Kitty 键盘协议](https://sw.kovidgoyal.net/kitty/keyboard-protocol/) 或 xterm 的 `modifyOtherKeys` 模式发送不同序列时，Hermes 才能识别 `Shift+Enter`。  

| 终端 | 状态 |
|---|---|
| Kitty、foot、WezTerm、Ghostty | 默认启用独立的 `Shift+Enter` 功能 |
| iTerm2（最新版本）、Alacritty、VS Code 终端、Warp | 在设置中启用 Kitty 协议后即可支持 |
| Windows Terminal Preview 1.25+ | 在设置中启用 Kitty 协议后即可支持 |
| macOS Terminal.app、稳定版的 Windows Terminal | 不支持——`Shift+Enter` 与 `Enter` 无法区分 |

在终端无法区分二者时，`Alt+Enter` 和 `Ctrl+J` 在所有环境中仍可正常使用。**特别地，在 Windows Terminal 中，`Alt+Enter` 会被终端捕获（用于切换全屏），而不会传递给 Hermes——如需换行，请使用 `Ctrl+Enter`（实际以 `Ctrl+J` 的形式发送）或直接使用 `Ctrl+J`。**

## 中断代理  

您可以在任何时候中断代理：  

- 在代理正在运行时**输入新消息后按 Enter**——这将中断当前操作并处理您的新指令  
- **`Ctrl+C`**——中断当前操作（2秒内连按两次可强制退出）  
- 正在执行的终端命令会立即被终止（先发送 SIGTERM，1秒后再发送 SIGKILL）  
- 中断过程中输入的多个消息会合并为一个提示符  

### 忙碌输入模式  

`display.busy_input_mode` 配置键用于控制当代理正在运行时您按 Enter 会发生什么：  

| 模式 | 行为 |
|------|--------|
| `"interrupt"`（默认） | 您的消息会中断当前操作，并立即被处理 |
| `"queue"` | 您的消息会被默默加入队列，待代理处理完当前任务后作为下一轮指令发送 |
| `"steer"` | 您的消息会通过 `/steer` 注入到当前运行流程中，在下一次工具调用之后送达代理——既不会中断当前操作，也不会开启新轮次 |

```yaml
# ~/.hermes/config.yaml
display:
  busy_input_mode: "steer"   # or "queue" or "interrupt" (default)
```

当您希望准备后续消息的同时避免意外中断正在处理的任务时，`"queue"` 模式非常有用。而当您希望在任务执行过程中对其进行引导——例如在智能体仍在编辑代码时要求其“其实还要检查一下测试用例”——而不造成中断时，`"steer"` 模式则更为适用。对于未知的输入值，系统会自动回退至 `"interrupt"` 模式。

`"steer"` 模式还有两种自动回退机制：如果智能体尚未开始执行任务，或者消息中附有图片，系统会自动切换为 `"queue"` 模式的工作方式，从而确保不会丢失任何信息。

您也可以通过 CLI 直接更改该模式：

```text
/busy queue
/busy steer
/busy interrupt
/busy status
```

:::提示 首次使用提示  
当 Hermes 正在运行时，您首次按下 Enter 键时，它会打印一条简短提示，解释 `/busy` 控制项的功能（`"(tip) 您的消息中断了当前正在运行的任务…"`）。此提示仅在程序安装后显示一次——`config.yaml` 文件中的 `onboarding.seen.busy_input_prompt` 设置会锁定该提示，若要再次看到提示，可删除该键值。  
:::

### 后台挂起  
在 Unix 系统上，按下 **`Ctrl+Z`** 即可将 Hermes 挂起到后台——操作方式与普通终端进程相同。此时shell会输出确认信息：

```
Hermes Agent has been suspended. Run `fg` to bring Hermes Agent back.
```

在命令行界面中输入 `fg` 即可从上次中断的位置继续会话。此功能在 Windows 系统上不受支持。

## 工具处理进度显示

在智能体执行任务时，命令行界面会提供动态反馈：

**思考动画**（在调用 API 期间）：
```
  ◜ (｡•́︿•̀｡) pondering... (1.2s)
  ◠ (⊙_⊙) contemplating... (2.4s)
  ✧٩(ˊᗜˋ*)و✧ got it! (3.1s)
```

**工具执行反馈流：**
```
  ┊ 💻 terminal `ls -la` (0.3s)
  ┊ 🔍 web_search (1.2s)
  ┊ 📄 web_extract (2.1s)
```

使用 `/verbose` 可循环切换显示模式：`off → new → all → verbose`。该命令也适用于消息平台——详情请参阅[配置指南](/user-guide/configuration#display-settings)。

### 工具预览长度

`display.tool_preview_length` 配置键用于控制工具调用预览行中显示的最大字符数（例如文件路径、终端命令）。其默认值为 `0`，表示无限制——将会完整显示路径和命令内容。

```yaml
# ~/.hermes/config.yaml
display:
  tool_preview_length: 80   # Truncate tool previews to 80 chars (0 = no limit)
```

在终端宽度有限，或工具参数包含过长的文件路径时，此功能尤为实用。

## 会话管理

### 恢复会话

当您退出 CLI 会话时，系统会输出一条恢复命令：

```
Resume this session with:
  hermes --resume 20260225_143052_a1b2c3

Session:        20260225_143052_a1b2c3
Duration:       12m 34s
Messages:       28 (5 user, 18 tool calls)
```

恢复选项：

```bash
hermes --continue                          # Resume the most recent CLI session
hermes -c                                  # Short form
hermes -c "my project"                     # Resume a named session (latest in lineage)
hermes --resume 20260225_143052_a1b2c3     # Resume a specific session by ID
hermes --resume "refactoring auth"         # Resume by title
hermes -r 20260225_143052_a1b2c3           # Short form
```

恢复功能会从 SQLite 数据库中读取完整的对话历史。智能体能够看到所有之前的消息、工具调用及回复，就像您从未离开过一样。

您可以在聊天界面中使用 `/title My Session Name` 为当前会话命名，或通过命令行执行 `hermes sessions rename <id> <title>` 来修改名称。若要查看过往的会话记录，则可使用 `hermes sessions list` 命令。

### 会话存储

CLI 会话存储在 Hermes 的 SQLite 状态数据库中，路径为 `~/.hermes/state.db`。该数据库会保存以下内容：

- 会话元数据（ID、标题、时间戳、令牌计数器）
- 消息历史记录
- 压缩会话与恢复会话之间的关联信息
- `session_search` 功能所使用的全文搜索索引

部分消息传输适配器还会在数据库之外保存针对不同平台的对话转录文件，但 CLI 本身始终从 SQLite 会话存储中恢复数据。

### 上下文压缩

当对话内容接近上下文限制时，系统会自动对长篇对话进行摘要处理：

```yaml
# In ~/.hermes/config.yaml
compression:
  enabled: true
  threshold: 0.50    # Compress at 50% of context limit by default

# Summarization model configured under auxiliary:
auxiliary:
  compression:
    model: ""  # Leave empty to use the main chat model (default). Or pin a cheap fast model, e.g. "google/gemini-3-flash-preview".
```

当触发压缩功能时，中间内容会被汇总，而最前3条及最后20条消息将始终被保留。

## 后台会话

可在独立的后台会话中运行提示语，同时继续使用CLI处理其他任务：

```
/background Analyze the logs in /var/log and summarize any errors from today
```

Hermes 立即确认该任务，并将提示语反馈给您：

```
🔄 Background task #1 started: "Analyze the logs in /var/log and summarize..."
   Task ID: bg_143022_a1b2c3
```

### 工作原理

每个 `/background` 提示词都会在一个后台线程中启动一个**完全独立的智能体会话**：

- **独立对话**——后台智能体不会知晓当前会话的历史记录，仅能接收您提供的提示词。
- **相同配置**——后台智能体会继承当前会话所使用的模型、服务提供商、工具集、推理设置以及备用模型。
- **非阻塞操作**——您的主线程会话仍可保持完全交互状态，您可以继续聊天、执行命令，甚至启动更多后台任务。
- **多任务处理**——您可以同时运行多个后台任务，每个任务都会获得一个编号标识。

### 结果展示

当某个后台任务完成时，其结果会以面板形式显示在您的终端中：

```
╭─ ⚕ Hermes (background #1) ──────────────────────────────────╮
│ Found 3 errors in syslog from today:                         │
│ 1. OOM killer invoked at 03:22 — killed process nginx        │
│ 2. Disk I/O error on /dev/sda1 at 07:15                      │
│ 3. Failed SSH login attempts from 192.168.1.50 at 14:30      │
╰──────────────────────────────────────────────────────────────╯
```

如果任务执行失败，您将看到错误提示。如果在配置中启用了 `display.bell_on_complete`，则任务完成后终端会发出铃声。

### 使用场景

- **长时间的研究工作**——在编写代码时，可输入“/background research the latest developments in quantum error correction”来后台执行研究；
- **文件处理**——在继续对话的同时，可输入“/background analyze all Python files in this repo and list any security issues”来后台分析所有 Python 文件并识别安全问题；
- **并行调查**——启动多个后台任务，同时从不同角度展开探索。

:::info
后台会话不会显示在您的主要对话历史中。它们是独立的会话，拥有各自的任务编号（例如 `bg_143022_a1b2c3`）。
:::

## 静默模式

默认情况下，CLI 以静默模式运行，其特点包括：
- 抑制工具的冗长日志输出；
- 提供可爱风格的动画反馈；
- 保持输出简洁且易于阅读。

如需查看调试信息：
```bash
hermes chat --verbose
```
