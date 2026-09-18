---
sidebar_position: 1
title: "CLI Interface"
description: "Master the Hermes Agent terminal interface — commands, keybindings, personalities, and more"
---

# CLI 接口

Hermes Agent 的 CLI 是一种完整的终端用户界面（TUI），而非网页界面。它具备多行编辑、斜杠命令自动补全、对话历史记录、中断与重定向功能，以及工具输出的流式显示能力，专为习惯在终端中操作的用户设计。

:::提示 首次设置
只需执行一条命令 `hermes setup --portal`，即可开始使用 `hermes chat` 功能。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

:::提示
Hermes 还提供了功能先进的 TUI，支持模态覆盖层、鼠标选择以及非阻塞式输入。可通过 `hermes --tui` 命令启动该界面，更多信息请参考 [TUI](tui.md) 文档。
:::

## 运行 CLI

```bash
# Start an interactive session (default)
hermes

# Single query mode (non-interactive)
hermes chat -q "Hello"

# Single query from a file or stdin — nothing is shell-interpreted, so
# arbitrary text (quotes, $(...), backticks) arrives verbatim
hermes chat --query-file prompt.txt
hermes chat --query-file - < prompt.txt

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
hermes --resume latest        # Resume the most recent session (same as -c)
hermes --resume latest --in ./dir  # Resume ./dir's latest session, staying in ./dir

# Verbose mode (debug output)
hermes chat --verbose

# Isolated git worktree (for running multiple agents in parallel)
hermes -w                         # Interactive mode in worktree
hermes -w -z "Fix issue #123"     # Single query in worktree
```

### 清理工作树

`hermes -w` 会话会在 `<repo>/.worktrees/` 目录下创建临时工作树。
系统会在启动时自动运行一个保守型的清理程序（仅移除已达到年龄阈值、状态正常且已完成完全合并的临时工作树），但在高负载的机器上，这些被保留的工作树以及已合并的本地分支仍会不断积累。如需清理它们，请手动执行相应操作：

```bash
hermes worktree list              # audit: age, size, verdict, reason per tree
hermes worktree prune             # remove safe trees + delete merged branches
hermes worktree prune --dry-run   # show the plan without changing anything
hermes worktree prune --trees-only     # leave local branches alone
hermes worktree prune --branches-only  # leave worktrees alone
```

在会话进行期间，执行 `/worktree prune [--dry-run]` 命令也能达到相同效果（且绝不会改动当前会话正在使用的代码树）。

安全保障机制（适用于所有模式及所有历史版本）：

- 未提交的**已跟踪**更改永远不会被删除。
- **唯一且未被推送的提交**也不会被删除——那些通过 `git cherry` 的补丁等价性检测到已在上游被 rebase 或 squash-merge 的提交会被视为已合并，从而避免“合并 PR 后代码树永久保留”这一误区带来的数据丢失。
- **已推送的开放 PR 对应的代码树会在不丢失任何内容的情况下被释放磁盘空间**：当某个状态干净的代码分支的头部信息与 `origin` 上的内容完全一致时（每次扫描都会通过一次 `git ls-remote` 进行验证），该分支的检出操作就变得多余了——此时代码树会被删除，但其**分支引用仍会被保留**，因此只需执行一次 `git worktree add .worktrees/<名称> <分支名>` 即可恢复该分支。如果无法连接到远程仓库，则该代码树会被保留。
- **正在被 Hermes 会话使用的代码树绝不会被改动**。
- 仅存在于**未跟踪区域**的临时文件（如 PR 正文草稿、备注等）在代码树被删除之前会被存档到 `~/.hermes/archive/worktree-prune/` 目录中，而不会被彻底销毁。
- 分支删除是基于内容而非名称来判定的：只要某个本地分支的所有提交都已在上游完成，就可以安全地删除；而那些包含独特代码、正处于检出状态的分支，以及 `main`/`master`/`develop` 等主分支则始终会被保留。
同样的保守型修剪程序也会通过 cron 定时任务运行（最多每 6 小时一次，在后台执行），因此那些数日之内都无人启动 `hermes -w` 命令的仅包含网关的机器，便不会再在多次 CLI 会话之间积累已合并的临时树。

当 `.worktrees/` 目录中的树的数量超过 10 棵或大小达到 5 GB 时，系统启动时会打印一条提示信息，指引用户使用相关命令处理。

### 插件管理

`hermes plugins` 命令通过相同的可选启用工作流，来管理原生 Hermes 插件以及便携式 Agent 插件 v1 包。

```bash
hermes plugins install owner/repository --no-enable
hermes plugins list
hermes plugins enable <plugin-name>
hermes plugins disable <plugin-name>
hermes plugins update <plugin-name>
hermes plugins remove <plugin-name>
```

便携式包在未被显式启用之前会保持禁用状态。Hermes 目前仅加载便携式 Agent Skills 以及 stdio MCP 条目。有关具体支持的组件范围及信任边界，请参阅[插件开发者指南](/developer-guide/plugins#portable-agent-plugins-v1-packages)。

## 界面布局

<img className="docs-terminal-figure" src="/docs/img/docs/cli-layout.svg" alt="Hermes CLI 排版的风格化预览图，展示了标题栏、对话区域以及固定输入提示符。" />
<p className="docs-figure-caption">Hermes CLI 的标题栏、对话流以及固定输入提示符以稳定的图片形式呈现，而非易损的文字艺术效果。</p>

欢迎横幅可让您一目了然地查看所使用的模型、终端后端、工作目录、可用工具以及已安装的技能。

### 状态栏

状态栏始终位于输入区域上方，并会实时更新内容：

```
 ⚕ claude-sonnet-4-20250514 │ 12.4K/200K │ [██████░░░░] 6% │ $0.06 │ 15m
```

| 元素 | 描述 |
|---------|-------------|
| 模型名称 | 当前使用的模型（若超过26个字符则会被截断显示） |
| Token数量 | 已使用的上下文Token数/最大上下文窗口大小；`~`表示估算值 |
| 上下文条 | 带有颜色编码阈值指示的可视化填充条 |
| 费用 | 会话预估费用（对于未知或免费模型则显示为`n/a`） |
| 🗜️ N | **上下文压缩次数**——当前会话被自动压缩的次数。首次发生压缩时即显示该数值。 |
| ▶ N | **正在运行的后台任务数**——当前会话中仍有多少个`/bg`指令在后台执行。只要存在至少一个正在运行的任务，就会显示此数值。 |
| 会话时长 | 已经持续的会话时间 |
| 会话标题 | 当会话设置了标题后，它会以金色徽章的形式显示在最右侧。过长的标题会在挤占重要模型和上下文字段显示空间之前被截断。 |
| ⚠ YOLO | **YOLO模式警告**——当`HERMES_YOLO_MODE`处于开启状态时（即在启动时使用`hermes --yolo`指令，或是在会话进行中切换到`/yolo`模式）就会显示此警告。该提示与顶部横幅警告内容一致，旨在提醒用户当前处于自动批准模式。 |
上下文使用量或百分比前的 `~` 符号表示其中已包含本地估算值。这一规则同样适用于网关的 `/status` 和 `/context` 接口、TUI 界面以及桌面端的上下文状态指示器。若提供商使用量未发生变化，则不会显示 `~` 符号；而当存在提供商基准值加上尚未计费的新消息时，则会显示该符号。`/context` 接口用于显示当前选定的消息来源。至于类别、可用空间、技能及工具集等方面的细分数据，即便整体使用率是基于提供商使用量得出的，也始终为本地估算值。这些显示标签不会影响内容压缩决策，也不会主动发起额外的提供商请求。

状态栏会根据终端宽度自动调整布局：终端列数≥76时为完整显示模式，52–75列时为紧凑模式，低于52列时则仅显示模型名称、处理时长，以及处于激活状态时的 YOLO 标识。

**上下文颜色编码规则：**

| 颜色 | 阈值 | 含义 |
|------|-------|------|
| 绿色 | < 50% | 空间充足 |
| 黄色 | 50–80% | 接近饱和 |
| 橙色 | 80–95% | 接近使用上限 |
| 红色 | ≥ 95% | 几近溢出——建议考虑使用 `/compress` 压缩内容 |

如需查看包含各类别成本（输入与输出 token 数量）的详细使用情况，可使用 `/usage` 接口。

在 `openai-codex` 提供商上，`/usage` 接口还会显示您在 ChatGPT 账户中已积累的可用额度重置次数（“您还有 N 次重置额度——可使用 /usage reset 来激活”）。`/usage reset` 命令可消耗一次累计的重置额度，从而完全恢复您5小时及每周的总使用限制。Hermes 会在您的使用限额尚未用尽时拒绝自动触发重置（因为累计的额度可完全恢复原有限制，提前使用反而会造成浪费）——如需强制执行重置，可使用 `/usage reset --force` 命令。

### 会话续接显示功能

在恢复之前的会话时（使用 `hermes -c` 或 `hermes --resume <id>` 命令），横幅与输入提示符之间会显示一个“历史对话”面板，简要概括对话记录。有关详细信息及配置方式，请参阅 [会话 —— 恢复时的对话概览](sessions.md#conversation-recap-on-resume)。

## 快捷键绑定

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Alt+Enter`, `Ctrl+J`, or `Shift+Enter` | New line (multi-line input). `Shift+Enter` requires a terminal that distinguishes it from `Enter` — see below. On Windows Terminal, `Alt+Enter` is captured by the terminal (fullscreen toggle); use `Ctrl+Enter` or `Ctrl+J` instead. |
| `Alt+V` | Paste an image from the clipboard when supported by the terminal |
| `Ctrl+V` | Paste text and opportunistically attach clipboard images |
| `Ctrl+B` | Start/stop voice recording when voice mode is enabled (`voice.record_key`, default: `ctrl+b`) |
| `Ctrl+G` | Open the current input buffer in `$EDITOR` (vim/nvim/nano/VS Code/etc.). Save and quit to send the edited text as the next prompt — ideal for long, multi-paragraph prompts. |
| `Ctrl+X Ctrl+E` | Emacs-style alternate binding for the external editor (same behavior as `Ctrl+G`). |
| `Ctrl+S` | **Stash the prompt.** Parks the current draft and clears the composer so you can send something else first. Press `Ctrl+S` again on an empty composer to bring the draft back (cursor at the end, attached images restored). Repeated presses build a stack rather than overwriting, so an earlier draft is never silently lost — with two or more stashed, `Ctrl+S` opens a browse panel (`↑`/`↓` to navigate, `Enter` to restore, `D` to discard, `Esc` or `Ctrl+S` to close). A `📌 N` badge in the status bar shows how many drafts are parked. Multi-line drafts round-trip exactly, including blank lines. The stash lives in memory for the session only — nothing is written to disk, since drafts often contain secrets. |
| `Ctrl+C` | Interrupt agent (double-press within 2s to force exit) |
| `Ctrl+T` / `F6` | Open the full-screen live subagent monitor without losing the composer draft. The live dock appears automatically above the status bar; arrows select a worker, `Enter` shows its recent log, `s` steers, and `x` requests stop with confirmation. See [Monitoring subagents](/user-guide/features/delegation#monitoring-running-subagents-agents). |
| `F7` | Toggle the live subagent dock between its multi-row preview and a single summary line without moving composer focus. |
| `Ctrl+D` | Exit |
| `Ctrl+Z` | Suspend Hermes to background (Unix only). Run `fg` in the shell to resume. |
| `Tab` | Accept auto-suggestion (ghost text) or autocomplete slash commands |
| `!<command>` | **Shell mode** — run a shell command yourself without spending a model turn (e.g. `!git status`, `!pytest -x`). See below. |

**多行粘贴预览功能。** 当您粘贴多行内容时，CLI会显示一个简洁的单行预览信息（如 `[已粘贴：47 行，1,842 个字符 — 按 Enter 键发送]`），而不会将全部内容直接显示在滚动区域中。实际上发送的仍是完整内容，这只是为了提升显示效果。

### `!` Shell 模式

在命令行开头加上 `!`，即可将该命令作为Shell指令执行，而非发送给代理程序：

```
> !git status
> !ls -la
> !pytest -x tests/cli
```

- **零成本。** 该模型根本不会被调用——无需 API 调用、无需令牌，也不存在延迟问题。  
- **对话内容保持纯净。** 命令及其输出不会被记录到对话历史中，因此您的上下文信息始终清晰，提示词缓存也不会受到影响。  
- **与智能体的 `terminal` 工具运行环境一致。** 它会使用当前会话的工作目录，因此 `!pwd` 的输出与智能体实际看到的内容一致。  
- **仍需遵循审批流程。** 危险命令（如 `rm -rf`、修改 `~/.hermes/config.yaml` 等）仍需经过与智能体的 `terminal` 工具相同的审批提示。`!` 仅是用于节省成本和减少延迟的快捷指令，并非安全绕过手段。  
- **失败命令会显示退出状态。** 执行失败的命令会在输出后显示 `! exited <code>` 的提示。  
- **单独输入 `!` 会显示使用说明。**

Shell 模式仅适用于 CLI 环境。Discord、Telegram、Slack 等网关平台以及定时任务均不支持该模式——这些用户已有自己的 Shell 环境。

**最终响应中的 Markdown 格式会被简化。** CLI 会自动移除智能体最终回复中过于复杂的 Markdown 包裹以及 `**粗体**` / `*斜体*` 格式，使其以可读的终端文本形式呈现，而非原始代码格式。代码块和列表则会被保留。此功能不会影响网关平台或工具的输出——它们会保持原有的 Markdown 格式以便直接渲染。

## 斜杠命令

输入 `/` 即可查看自动补全下拉菜单。Hermes 支持大量 CLI 斜杠命令、动态技能命令以及用户自定义的快捷命令。

常见示例：

| 命令 | 描述 |
|---------|-------------|
| `/help` | 显示命令帮助信息 |
| `/model` | 查看或切换当前使用的模型 |
| `/tools` | 列出当前可用的工具 |
| `/skills browse` | 浏览技能中心及官方提供的可选技能 |
| `/bg <prompt>` | 在独立的后台会话中运行指定提示词 |
| `/btw <question>` | 提出与当前对话相关的问题，且不会中断原有对话流程 |
| `/skin` | 查看或切换当前激活的 CLI 界面主题 |
| `/voice on` | 启用 CLI 语音模式（按 `Ctrl+B` 可进行录音） |
| `/voice tts` | 切换 Hermes 回复的语音播放功能 |
| `/reasoning high` | 提高推理强度 |
| `/title My Session` | 为当前会话命名 |
| `/status` | 显示会话信息——包括模型、配置文件、Token 数量及会话时长——随后还会展示本地的**会话概览**板块（最近的对话轮次数、最常使用的工具、处理过的文件，以及最新的用户提示词和助手回复）。该功能仅基于本地计算，不会调用大型语言模型。 |
| `/context [all]` | 以可视化方式展示上下文使用情况——包括符号块网格以及按类别划分的 Token 使用表（系统提示词/工具/技能/记忆内容/对话历史/剩余空间）。输入 `/context all` 可查看每项技能和每组工具对应的 Token 耗用情况。 |
| `/sessions` | 在传统 CLI 界面内直接打开交互式会话选择器（与 TUI 使用的界面相同）。可通过输入文字进行筛选，使用方向键导航，按 Enter 键继续操作。 |

如需查看完整的内置 CLI 命令及消息功能列表，请参阅 [Slash Commands 参考文档](../reference/slash-commands.md)。

关于设置、提供商配置、静音调节以及消息发送/Discord语音功能的使用方法，请参阅[语音模式](features/voice-mode.md)文档。

:::提示
命令不区分大小写——`/HELP`与`/help`具有相同的功能。已安装的技能也会自动转换为斜杠命令。
:::

## 快速命令

您可以定义自定义命令，这些命令能够直接执行Shell命令而无需调用大型语言模型。此类命令既可在命令行界面中使用，也适用于各类消息平台（如Telegram、Discord等）。

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

接着在任意聊天窗口中输入 `/status`、`/gpu` 或 `/restart` 即可。更多示例请参阅[配置指南](/user-guide/configuration#quick-commands)。

## 启动时预加载技能

如果您已确定本次会话需要启用的技能，可在启动时直接指定它们：

```bash
hermes -s hermes-agent-dev,github-auth
hermes chat -s github-pr-workflow -s github-auth
```

在首个对话轮次开始之前，Hermes会将每个已命名的技能加载到会话提示词中。该机制在交互模式和单查询模式下均适用。

## 技能斜杠命令

位于 `~/.hermes/skills/` 目录中的所有已安装技能都会自动注册为斜杠命令，其技能名称即作为该命令的名称。

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

内置的个性风格包括：`helpful`、`concise`、`technical`、`creative`、`teacher`、`kawaii`、`catgirl`、`pirate`、`shakespeare`、`surfer`、`noir`、`uwu`、`philosopher` 和 `hype`。

若要恢复为默认状态（无叠加效果），可使用命令 `/personality none`，`default` 和 `neutral` 也可达到相同效果。

您还可以在 `~/.hermes/config.yaml` 文件中定义自定义的个性风格：

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

默认情况下，`Ctrl+J` 与反斜杠续行功能已被启用，其用法与 Claude Code、Codex 以及 OpenCode 的多行输入快捷键一致。在 iTerm2 等支持该功能的终端上，Hermes 还会请求开启扩展键报告功能，从而使 `Shift+Enter` 被视为独立的换行键。如果您的终端在普通 `Enter` 操作时发送的是 LF 符号，且您需要使用传统的 `Ctrl+J` 作为提交替代方案，则可以选择关闭该功能。

```yaml
# ~/.hermes/config.yaml
display:
  cli_multiline_shortcuts: false
```

:::info  
支持粘贴多行文本——可使用上述任意换行键，或直接粘贴内容。  

在采用 Kitty 键盘协议的终端中，数字小键盘上的 `Alt+Enter` 也可插入换行符，即便是在已折叠的粘贴内容旁边同样有效。经过修改的键盘导航键功能与普通键盘上的对应键一致。  
:::

### Shift+Enter 兼容性  

默认情况下，大多数终端会为 `Enter` 和 `Shift+Enter` 发送相同的字节序列，因此应用程序无法区分二者。只有当终端通过 [Kitty 键盘协议](https://sw.kovidgoyal.net/kitty/keyboard-protocol/) 或 xterm 的 `modifyOtherKeys` 模式发送不同序列时，Hermes 才能识别 `Shift+Enter`。  

| 终端 | 状态 |
|---|---|
| Kitty、foot、WezTerm、Ghostty | 默认已启用独立的 `Shift+Enter` 功能 |
| iTerm2（最新版本）、Alacritty、VS Code 终端、Warp | 在设置中启用 Kitty 协议后即可支持 |
| Windows Terminal Preview 1.25+ | 在设置中启用 Kitty 协议后即可支持 |
| macOS Terminal.app、稳定版的 Windows Terminal | 不支持——`Shift+Enter` 与 `Enter` 无法区分 |

在终端无法区分二者时，`Alt+Enter` 和 `Ctrl+J` 仍会正常生效。**特别说明的是，在 Windows Terminal 中，`Alt+Enter` 会被终端截获（用于切换全屏模式），而无法传递给 Hermes——如需插入换行符，请使用 `Ctrl+Enter`（实际以 `Ctrl+J` 的形式传递）或直接使用 `Ctrl+J`。**

## 在对话进行中重定向 Agent

在智能体正在运行时，您无需开启新的对话轮次即可发送修正内容：

- **输入新消息后按回车键**——将当前对话轮次切换为您的修正内容
- **`Ctrl+C`**——中断当前操作（2秒内连按两次可强制退出）
- 已完成的工具处理结果及推理过程会保留在上下文中
- 在修正内容应用之前，正在运行的工具会先达到其安全终止条件

### 忙碌输入模式

`display.busy_input_mode` 配置键用于控制当智能体正在运行时按下回车键后的行为：

| 模式 | 行为说明 |
|------|----------|
| `"interrupt"`（默认值） | 您的消息会替换当前对话轮次的内容。模型生成将重新开始，同时保留已展示的推理过程和已完成的工作。正在运行的前台终端命令会被移至后台（不会被终止——您会收到完成通知），以便您的消息能立即被读取；其他正在运行的工具则会先完成处理 |
| `"queue"` | 您的消息会被静默地排队，等待智能体处理完毕后再作为下一轮对话发送 |
| `"steer"` | 您的消息会通过 `/steer` 接口注入到当前运行流程中，在下一次工具调用之后传递给智能体——既不会中断当前操作，也不会开启新的对话轮次 |

```yaml
# ~/.hermes/config.yaml
display:
  busy_input_mode: "steer"   # or "queue" or "interrupt" (default)
```

“queue”模式会为后续交互预留单独的轮次。“steer”模式则会始终等待下一个工具响应的结束。默认的“interrupt”模式会在模型生成过程中更快地做出响应，同时避免中断正在运行的工具；对于那些耗时的前台终端命令（如构建操作或轮询任务），系统会将其转至后台处理，这样智能体就能立即看到您的消息，而无需等待命令执行完毕。若需取消当前轮次及其相关的前台任务，可使用 `/stop` 命令。对于未知的配置值，系统会自动回退到“interrupt”模式。

“steer”模式还有两种自动回退机制：如果智能体尚未开始运行，或者消息中附有图片，系统会自动切换为“queue”模式，以确保信息不会丢失。

您也可以在CLI界面中手动更改该设置：

```text
/busy queue
/busy steer
/busy interrupt
/busy status
```

:::提示 首次使用提示  
当 Hermes 正在运行时，您首次按下回车键，它会输出一条简短提示，解释 `/busy` 控制项的功能。该提示在每次安装后仅显示一次；`config.yaml` 文件中的 `onboarding.seen.busy_input_prompt` 键用于记录该提示是否已展示。如需再次查看提示，可删除该键。  
:::

### 暂停至后台  

在 Unix 系统上，按 **`Ctrl+Z`** 即可将 Hermes 暂停至后台——操作方式与普通终端进程相同。此时shell会输出确认信息：

```
Hermes Agent has been suspended. Run `fg` to bring Hermes Agent back.
```

在终端中输入 `fg` 即可从上次中断的位置继续执行会话。此功能在 Windows 系统上不受支持。

## 工具处理进度显示

在智能体运行过程中，CLI 会提供动态反馈：

**思考动画**（在调用 API 时）：
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

`display.tool_preview_length` 配置键用于控制工具调用预览行中显示的最大字符数（例如文件路径、终端命令）。其默认值为 `0`，表示无限制——会完整显示路径和命令内容。

```yaml
# ~/.hermes/config.yaml
display:
  tool_preview_length: 80   # Truncate tool previews to 80 chars (0 = no limit)
```

在终端宽度较窄，或工具参数包含过长的文件路径时，此功能尤为实用。

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

继续选项：

```bash
hermes --continue                          # Resume the most recent CLI session
hermes -c                                  # Short form
hermes -c "my project"                     # Resume a named session (latest in lineage)
hermes --resume 20260225_143052_a1b2c3     # Resume a specific session by ID
hermes --resume "refactoring auth"         # Resume by title
hermes --resume latest                     # Resume the most recent session (same as -c)
hermes --resume latest --in ./my-project   # Latest session for ./my-project's workspace
hermes -r 20260225_143052_a1b2c3           # Short form
```

恢复操作会从 SQLite 数据库中读取完整的对话历史。智能体能够看到所有之前的消息、工具调用及回复，就像您从未离开过一样。

您可以在聊天界面中使用 `/title My Session Name` 为当前会话命名，或通过命令行执行 `hermes sessions rename <id> <title>`。如需查看过往的会话记录，可使用 `hermes sessions list` 命令。

### 会话存储

CLI 会话存储在 Hermes 的 SQLite 状态数据库中，路径为 `~/.hermes/state.db`。该数据库包含以下内容：

- 会话元数据（ID、标题、时间戳、令牌计数器）
- 消息历史记录
- 压缩会话与恢复会话之间的关联信息
- `session_search` 功能所使用的全文搜索索引

部分消息传输适配器还会在数据库之外保存针对不同平台的转录文件，但 CLI 本身则是从 SQLite 会话存储中恢复数据的。

### 上下文压缩

当对话内容接近上下文限制时，系统会自动对长对话进行摘要处理：

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

当触发压缩功能时，中间内容会被汇总，而最前面的3条消息以及最后面的20条消息将始终被保留。

## 后台会话

您可以在一个独立的后台会话中运行提示语，同时继续使用CLI处理其他任务：

```
/bg Analyze the logs in /var/log and summarize any errors from today
```

Hermes会立即确认该任务，并将提示语反馈给您：

```
🔄 Background task #1 started: "Analyze the logs in /var/log and summarize..."
   Task ID: bg_143022_a1b2c3
```

### 工作原理

每个 `/bg` 提示词都会在后台线程中启动一个**完全独立的智能体会话**：

- **独立对话**——后台智能体无法知晓当前会话的历史记录，它仅能接收您输入的提示词。
- **相同配置**——后台智能体会继承当前会话所使用的模型、服务提供商、工具集、推理设置以及备用模型。
- **非阻塞操作**——您的主线程会话仍可保持完全交互状态，您可以继续聊天、执行命令，甚至启动更多后台任务。
- **多任务处理**——您可以同时运行多个后台任务，每个任务都会被赋予一个编号标识。

### 结果展示

当某个后台任务完成时，其结果会以面板形式显示在终端中：

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

- **长时间的研究工作** — 在编写代码时，可执行 `/bg research the latest developments in quantum error correction`；
- **文件处理** — 在继续对话的同时，可执行 `/bg analyze all Python files in this repo and list any security issues`；
- **并行调查** — 同时启动多个后台任务，从不同角度展开研究。

:::info
后台会话不会显示在您的主要对话历史中。它们是独立的会话，拥有各自的任务编号（例如 `bg_143022_a1b2c3`）。
:::

## 静音模式

默认情况下，CLI以静音模式运行，其特点包括：
- 抑制工具的详细日志输出；
- 提供可爱的动画式反馈效果；
- 保持输出简洁且易于理解。

如需查看调试信息：
```bash
hermes chat --verbose
```
