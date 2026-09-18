# Hermes TUI

专为Hermes设计的基于React与Ink的终端用户界面。屏幕渲染由TypeScript负责，而会话管理、工具操作、模型调用以及大部分命令逻辑则由Python处理。

```bash
hermes --tui
```

## 运行机制

客户端入口文件为 `src/entry.tsx`。如果 `stdin` 不是终端设备，该文件会立即退出；随后会启动 `GatewayClient`，最后渲染 `App` 组件。

`GatewayClient` 会创建：

```text
python -m tui_gateway.entry
```

解释器的解析顺序为：`HERMES_PYTHON` → `PYTHON` → `$VIRTUAL_ENV/bin/python` → `./.venv/bin/python` → `./venv/bin/python` → `python3`（在 Windows 系统上则为 `python`）。

数据传输方式是通过标准输入输出以换行符分隔的 JSON-RPC 格式。

```text
ui-tui/src                  tui_gateway/
-----------                 -------------
entry.tsx                   entry.py
  -> GatewayClient            -> request loop
  -> App                      -> server.py RPC handlers

stdin/stdout: JSON-RPC requests, responses, events
stderr: captured into an in-memory log ring
```

格式错误的标准输出行会被视为协议噪声，并以 `gateway.protocol_error` 的形式呈现。而标准错误行则会被标记为 `gateway.stderr`。这两种信息均不会直接输出到终端中。

## 运行方式

从代码仓库的根目录出发，常规的运行路径为：

```bash
hermes --tui
```

该命令行工具要求必须存在 `ui-tui/dist/entry.js` 文件，或者具备完整的源代码，以便执行 `npm install` 和 `npm run dev` 指令。

```bash
cd ui-tui
npm install
```

本地包命令：

```bash
npm run dev
npm start
npm run build
npm run lint
npm run fmt
npm run fix
```

测试采用 vitest 工具进行：

```bash
npm test         # single run
npm run test:watch
```

## 实时代理

当子任务正在运行时，Composer 上方会自动显示控制栏。该控栏会展示实时的子任务数量、任务名称、耗时以及最新操作状态。在终端宽度较窄的情况下，其显示行数会相应减少；已完成的任务会保存在现有的 `/agents`/`/replay` 历史记录中，而不会持续占用 Composer 的空间。异步完成的任务单元不会被计入额外的代理数量。

- **Ctrl+T**：展开代理列表且不会清除当前草稿；**Esc**：返回上一页。
- **↑/↓**：选择某个代理，**Enter**：查看该代理的详细信息（工具、输出、文件及使用情况）。
- **t**：查看该代理的实时对话记录尾部；**g/G**：切换到记录顶部/底部。
- **e**：打开单独的引导表单。**Enter**：将引导指令加入队列，**Esc**：返回上一页。“已入队”仅表示该指令已被接收，等待进入下一个工具处理阶段，并不代表已确认执行。
- **x**：请求停止所选子任务；**X**：请求停止整个子树下的所有任务。
原有的排序/过滤、暂停/继续生成、时间轴显示以及回放控制功能依然可用。

该代理列表会通过会话范围的 `subagent.list` RPC 请求以及流式事件动态更新内容。仅“实时对话记录尾部”视图会定期查询 `subagent.tail` 数据，而引导功能则使用现有的 `subagent.steer` RPC 接口。模型工具的架构及提示词缓存机制均保持不变。

## 应用模型

`src/app.tsx` 是用户界面的核心文件。复杂的逻辑功能被拆分到 `src/app/` 目录下：

- `src/app/createGatewayEventHandler.ts`：负责将网关事件映射为状态更新。
- `src/app/createSlashHandler.ts`：用于处理本地的斜杠命令调度。
- `src/app/useComposerState.ts` — 草稿模式、多行缓冲区以及队列编辑功能  
- `src/app/useInputHandlers.ts` — 按键处理逻辑  
- `src/app/useMainApp.ts` — 顶层组合钩子：连接所有子钩子，管理对话记录历史、会话轮询，并为 `app.tsx` 提供所需属性  
- `src/app/useSessionLifecycle.ts` — 处理会话的创建/恢复/激活/关闭操作以及可见历史记录的重置  
- `src/app/useSubmission.ts` — 负责消息发送、命令执行（`!cmd`）、内联插值（`{!cmd}`），以及忙碌输入模式的管理（队列/引导/中断）  
- `src/app/turnController.ts` — 一个带状态管理的类，用于控制对话轮次流程：缓存流式数据变化，管理工具与推理状态，处理中断及消息完成状态切换  
- `src/app/turnStore.ts` — 用于存储对话轮次相关状态的纳米存储库（包括流式文本、工具信息、推理过程、子智能体状态、待办事项及操作轨迹）  
- `src/app/useConfigSync.ts` — 在会话启动时获取完整配置信息，并每5秒检查配置文件的修改时间；根据配置变化应用显示设置并触发MCP重新加载  
- `src/app/useLongRunToolCharms.ts` — 当工具运行时间超过8秒时，触发相关活动提示信息  
- `src/app/overlayStore.ts` / `src/app/uiStore.ts` — 用于存储覆盖层及用户界面状态的纳米存储库  
- `src/app/delegationStore.ts` — 用于管理子智能体生成数量上限以及覆盖层折叠状态的纳米存储库  
- `src/app/spawnHistoryStore.ts` — 内存中的环形缓存（最多保存最近10条），用于存储已完成的子智能体运行快照，可在需要回放时使用这些数据
- `src/app/inputSelectionStore.ts` — 用于暴露当前文本输入选择区域的 nanostore  
- `src/app/gatewayContext.tsx` — 用于 gateway 客户端的 React context  
- `src/app/gatewayRecovery.ts` — 一个纯函数，用于在 gateway 发生故障后决定是否重新启动并继续运行，允许最多尝试 3 次，每次间隔 60 秒  
- `src/app/setupHandoff.ts` — 启动外部 `hermes setup` 工具，在其运行期间暂停 Ink 的功能，成功后开启新会话  
- `src/app/scroll.ts` — 在滚动视口的同时保持文本选择位置的同步  
- `src/app/interfaces.ts` — 内部接口（如 ComposerActions、GatewayRpc 等）  

### Slash 命令子系统（`src/app/slash/`）  

- `types.ts` — `SlashCommand` 接口以及 `SlashRunCtx` 执行上下文（包含 gateway rpc、转录辅助功能、会话引用及过时检测机制）  
- `registry.ts` — 按注册顺序从所有命令文件中汇总出 `SLASH_COMMANDS`（依次为核心功能 → 计费功能 → 信用额度管理 → 会话管理 → 操作管理 → 设置功能 → 调试功能），并提供 `findSlashCommand(name)` 方法以实现不区分大小写的查询  
- `commands/core.ts` — 通用 TUI 命令  
- `commands/billing.ts` — `/billing`：管理 Nous 的远程支出——购买信用额度、自动充值及设置限额  
- `commands/credits.ts` — `/credits`  
- `commands/session.ts` — 会话及智能体相关命令  
- `commands/ops.ts` — 操作类命令  
- `commands/setup.ts` — `/setup`  
- `commands/debug.ts` — `/heapdump`、 `/mem`
顶层 `app.tsx` 负责将这些组件整合为 Ink 树结构，其中包含“静态”对话记录输出、实时流式助手行、提示语覆盖层、队列预览、状态规则、输入行以及补全列表。

在顶层管理的状态包括：

- 对话记录与流式处理状态
- 队列中的消息及输入历史记录
- 会话生命周期状态
- 工具处理进度及推理文本
- 用于确认、澄清、授权执行及输入敏感信息的提示流程
- 斜杠命令路由逻辑
- Tab 键补全与路径补全功能
- 来自网关主题数据的主题状态

用户界面将以常规的 Ink 树形式呈现，包含“静态”对话记录输出、实时流式助手行、提示语覆盖层、队列预览、状态规则、输入行以及补全列表。

欢迎面板的内容由 `session.info` 提供，并通过 `branding.tsx` 进行渲染。

## 快捷键与交互操作

当前的输入功能由 `app.tsx`、`components/textInput.tsx` 以及各类提示语/选择器组件共同实现。

### 主要聊天输入功能

| Key                             | Behavior                                                                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Enter`                         | Submit the current draft                                                                                                                                |
| empty `Enter` twice             | If queued messages exist and the agent is busy, interrupt the current run. If queued messages exist and the agent is idle, send the next queued message |
| `Shift+Enter` / `Alt+Enter`     | Insert a newline in the current draft                                                                                                                   |
| `\` + `Enter`                   | Append the line to the multiline buffer (fallback for terminals without modifier support)                                                               |
| `Ctrl+C`                        | Interrupt active run, or clear the current draft, or exit if nothing is pending                                                                         |
| `Ctrl+D`                        | Exit                                                                                                                                                    |
| `Cmd/Ctrl+G` / `Alt+G`          | Open `$EDITOR` with the current draft (use `Alt+G` in VSCode/Cursor — they bind the primary keystroke to Find Next)                                     |
| `Ctrl+L`                        | New session (same as `/clear`)                                                                                                                          |
| `Ctrl+V` / `Alt+V`              | Paste text first, then fall back to image/path attachment when applicable                                                                               |
| `Tab`                           | Apply the active completion                                                                                                                             |
| `Up/Down`                       | Cycle completions if the completion list is open; otherwise edit queued messages first, then walk input history                                         |
| `Left/Right`                    | Move the cursor                                                                                                                                         |
| modified `Left/Right`           | Move by word when the terminal sends `Ctrl` or `Meta` with the arrow key                                                                                |
| `Home` / `Ctrl+A`               | Start of line                                                                                                                                           |
| `End` / `Ctrl+E`                | End of line                                                                                                                                             |
| `Backspace`                     | Delete the character to the left of the cursor                                                                                                          |
| `Delete`                        | Delete the character to the right of the cursor                                                                                                         |
| modified `Backspace`            | Delete the previous word                                                                                                                                |
| modified `Delete`               | Delete the next word                                                                                                                                    |
| `Ctrl+W`                        | Delete the previous word                                                                                                                                |
| `Ctrl+U`                        | Delete from the cursor back to the start of the line                                                                                                    |
| `Ctrl+K`                        | Delete from the cursor to the end of the line                                                                                                           |
| `Meta+B` / `Meta+F`             | Move by word                                                                                                                                            |
| `!cmd`                          | Run a shell command through the gateway                                                                                                                 |
| `{!cmd}`                        | Inline shell interpolation before send; queued drafts keep the raw text until they are sent                                                            |

备注：

- 仅当存在补全选项且未处于多行模式时，`Tab` 键才会触发补全功能。
- 队列/历史记录导航功能也仅在非多行模式下可用。
- `PgUp` / `PgDn` 键的功能由终端模拟器处理，TUI 不支持这些操作。

### 提示词模式与选择器模式

| 场景                     | 按键                | 行为描述                                          |
| --------------------------- | ------------------- | ------------------------------------------------- |
| 审批提示框                 | `Up/Down`, `Enter`  | 移动并确认所选的审批选项                         |
| 审批提示框                 | `o`, `s`, `a`, `d`  | 快速选择“仅一次”、“当前会话”、“始终允许”、“拒绝”   |
| 审批提示框                 | `Esc`, `Ctrl+C`     | 拒绝审批                                          |
| 带选项的澄清提示框         | `Up/Down`, `Enter`  | 移动并确认所选的选项                             |
| 带选项的澄清提示框         | 单位数              | 快速选择对应的编号选项                         |
| 带选项的澄清提示框         | 输入“Other”后按 `Enter` | 切换到自由文本输入模式                         |
| 进入自由文本输入模式       | `Enter`             | 提交输入的答案                                   |
| sudo/密钥提示框            | `Enter`             | 提交输入的值                                     |
| sudo/密钥提示框            | `Ctrl+C`            | 通过发送空响应取消操作                         |
| 会话选择器恢复功能         | `Up/Down`, `Enter`  | 移动并继续选择已选会话                           |
| 会话选择器恢复功能         | `1-9`               | 快速选择前九个可见会话中的任意一个             |
| 会话选择器恢复功能         | `Esc`, `Ctrl+C`     | 关闭会话选择器                                   |

备注：

- 要区分自由文本模式与掩码提示，请使用 `ink-text-input`，此时文本编辑将遵循该库的默认绑定规则，而非 `components/textInput.tsx` 的规则。
- 当处于阻塞提示状态时，主聊天输入的热键功能将被暂时禁用。
- 需说明的是，当前客户端中该模式并未配备专用的取消快捷键；对于超级用户令牌和密钥相关的提示，仅能通过应用层级的阻塞处理程序提供 `Ctrl+C` 这一取消方式。

### 交互规则

- 当智能体正在处理任务时输入的纯文本会被放入队列中，而非立即发送。
- 斜杠命令以及 `!cmd` 格式的指令不会进入队列，即便在智能体正在运行时也会立即执行。
- 每次智能体回复后队列内容会自动清空，除非当前有正在编辑的队列项。
- `Up/Down` 键会优先处理队列中的消息编辑，而历史记录仅在没有待编辑的队列项时才会显示。
- 在编辑队列中的草稿时，其原有的 `!cmd` 和 `{!cmd}` 格式文本会保持不变。shell 命令及插值功能则会在该队列项实际被发送时才执行。
- 如果将队列中的某项内容复制到输入框并重新输入纯文本，该队列项将被替换，从队列预览中移除，并提升为下一个待发送项。如果智能体仍在处理任务，经过编辑的项会移到队列最前端，在当前任务完成后再被发送。
- 补全请求的延迟时间为 60 毫秒。以 `/` 开头的输入会使用 `complete.slash` 补全机制；以 `./`、`../`、`~/`、`/` 或 `@` 开头的尾随标识符则会使用 `complete.path` 补全机制。
- 粘贴的文本会直接插入草稿中，不会被换行符拆分。
- 按下 `Cmd/Ctrl+G`（在 VSCode/Cursor 中为 `Alt+G`，该键会拦截“查找下一个”功能的主键输入）会将当前草稿，包括多行缓冲区内容，写入临时文件，暂停 Ink 工具，启动 `$EDITOR` 编辑器；如果编辑器正常退出，则恢复 TUI 界面并发送已保存的文本。
- 输入历史记录存储在 `~/.hermes/.hermes_history` 文件中，或位于 `HERMES_HOME` 目录下。

## 输出渲染

智能体的输出可以通过两种方式之一进行呈现：

- 如果消息内容已包含 ANSI 格式，`messageLine.tsx` 会直接将其显示出来；  
- 否则，`components/markdown.tsx` 会将简化的 Markdown 内容转换为 Ink 组件进行渲染。  

该 Markdown 渲染器能够处理标题、列表、块引文、表格、代码块、差异高亮显示、内联代码、强调文本、链接以及普通 URL。  

工具/状态相关的操作会显示在实时活动栏中，而对话记录则仅展示用户与助手的轮次内容。  

## 提示词流程  

Python 网关可以暂停主循环并请求结构化输入：  
- `approval.request`：允许一次、仅限当前会话允许、始终允许或拒绝；  
- `clarify.request`：从预设选项中选择或输入自定义答案；  
- `sudo.request`：以掩码形式输入密码；  
- `secret.request`：以掩码形式输入指定环境变量的值；  
- `session.list`：供 `SessionPicker` 在 `/resume` 功能中使用。  

这些均为 `app.tsx` 中的状态型 UI 分支，而非独立的界面页面。  

## 命令  

以下命令由 TUI 客户端直接处理；无法识别的命令则通过 `slash.exec` 和 `command.dispatch` 传递给 Python 网关。  

### 核心命令（`core.ts`）  
`/help`、`/quit`（别名 `/exit`）、`/update`、`/clear`（别名 `/new`）、  
`/density`、`/copy`、`/paste`、`/details`（别名 `/detail`）、  
`/statusbar`（别名 `/sb`）、`/queue`（别名 `/q`）、`/logs`、`/history`、  
`/save`、`/undo`、`/retry`、`/steer`、`/mouse`（别名 `/scroll`）、  
`/status`、`/title`、`/fortune`、`/redraw`、`/terminal-setup`  

### 计费相关命令（`billing.ts`）  
`/billing` —— 管理 Nous 的远程支出，包括购买额度、自动充值及设置限额。

### 会话 (`session.ts`)
`/model`、`/sessions`（别名：`/switch`、`/session`、`/resume`），
`/bg`、`/btw`、`/image`、`/personality`，
`/compress`、`/branch`（别名：`/fork`）、`/voice`、`/skin`，
`/indicator`、`/yolo`、`/reasoning`、`/fast`、`/busy`、`/verbose`、`/usage`

### 操作 (`ops.ts`)
`/stop`、`/reload-mcp`（别名：`/reload_mcp`）、`/reload`、`/browser`，
`/rollback`、`/agents`（别名：`/tasks`）、`/replay`、`/replay-diff`，
`/skills`、`/reload-skills`（别名：`/reload_skills`）、`/plugins`、`/tools`

### 余额 (`credits.ts`)
`/credits` — 查看 Nous 信用余额及浏览器充值情况

### 设置 (`setup.ts`)
`/setup` — 启动外部 `hermes setup` 向导，运行期间暂停 Ink 功能

### 调试 (`debug.ts`)
`/heapdump`、`/mem` — V8 内存诊断工具

---

以上未涵盖的请求将依次通过以下处理方式：
1. `slash.exec`
2. `command.dispatch`

这样，Python 即可管理别名、插件、技能以及基于注册表的命令，而无需在 TUI 中重复实现相关逻辑。

## 事件接口

客户端当前支持的主要事件类型：

| Event                      | Payload                                                                     |
| -------------------------- | --------------------------------------------------------------------------- |
| `gateway.ready`            | `{ skin? }`                                                                 |
| `skin.changed`             | `{ skin }`                                                                  |
| `session.info`             | session metadata for banner + tool/skill panels                             |
| `message.start`            | start assistant streaming                                                   |
| `message.delta`            | `{ text, rendered? }`                                                       |
| `message.complete`         | `{ text, rendered?, usage, status }`                                        |
| `thinking.delta`           | `{ text }`                                                                  |
| `reasoning.delta`          | `{ text, verbose? }`                                                        |
| `reasoning.available`      | `{ text, verbose? }`                                                        |
| `status.update`            | `{ kind, text }`                                                            |
| `notification.show`        | `{ id, key, kind, level, text, ttl_ms? }`                                   |
| `notification.clear`       | `{ key }`                                                                   |
| `tool.start`               | `{ tool_id, name, context?, args_text? }`                                   |
| `tool.generating`          | `{ name }`                                                                  |
| `tool.progress`            | `{ name, preview }`                                                         |
| `tool.complete`            | `{ tool_id, name, error?, summary?, duration_s?, inline_diff?, todos? }`    |
| `clarify.request`          | `{ question, choices?, request_id }`                                        |
| `approval.request`         | `{ command, description, allow_permanent? }`                                |
| `sudo.request`             | `{ request_id }`                                                            |
| `sudo.expire`              | `{ request_id }` clears a timed-out sudo prompt                             |
| `secret.request`           | `{ prompt, env_var, request_id }`                                           |
| `secret.expire`            | `{ request_id }` clears a timed-out secret prompt                           |
| `background.complete`      | `{ task_id, text }`                                                         |
| `billing.step_up.verification` | `{ verification_url, user_code }`                                       |
| `review.summary`           | `{ text }`                                                                  |
| `browser.progress`         | `{ message }`                                                               |
| `voice.status`             | `{ state }`                                                                 |
| `voice.transcript`         | `{ text, no_speech_limit? }`                                                |
| `subagent.spawn_requested` | `{ subagent_id?, task_index, goal?, depth?, parent_id? }`                   |
| `subagent.start`           | `{ subagent_id?, task_index, goal?, depth?, parent_id? }`                   |
| `subagent.thinking`        | `{ text }`                                                                  |
| `subagent.tool`            | `{ tool_name?, tool_preview?, text? }`                                      |
| `subagent.progress`        | `{ text }`                                                                  |
| `subagent.complete`        | `{ status, summary?, text?, duration_seconds? }`                            |
| `error`                    | `{ message }`                                                               |
| `gateway.stderr`           | synthesized from child stderr                                               |
| `gateway.protocol_error`   | synthesized from malformed stdout                                           |
| `gateway.start_timeout`    | `{ cwd?, python?, stderr_tail? }`                                           |

## 主题模型

客户端首先使用 `theme.ts` 中定义的 `DEFAULT_THEME` 作为基础主题，随后再合并来自 `gateway.ready` 的网关界面皮肤数据。

当前可覆盖的品牌元素包括：

- 代理名称
- 提示符号
- 欢迎文本
- 告别文本

当前可覆盖的颜色设置包括：

- 标题栏、强调色、边框、内容区域及背景色
- 标签、确认按钮、错误提示及警告提示的颜色

`branding.tsx` 会利用这些值来渲染徽标、会话面板以及更新通知。  

## 文件结构图

```text
ui-tui/
  packages/hermes-ink/   forked Ink renderer (local dep)
  src/
    entry.tsx            TTY gate + render()
    app.tsx              top-level Ink tree, composes src/app/*
    gatewayClient.ts     child process + JSON-RPC bridge
    gatewayTypes.ts      gateway event and RPC response type definitions
    theme.ts             theme colors and skin merge
    banner.ts            ASCII art renderer (parses Rich color tags)
    types.ts             shared client-side types (ActiveTool, Msg, etc.)

    app/
      createGatewayEventHandler.ts  event → state mapping
      createSlashHandler.ts         local slash dispatch
      delegationStore.ts            nanostore for subagent spawning caps and overlay accordion state
      gatewayContext.tsx            React context for gateway client
      gatewayRecovery.ts            crash-recovery budget: respawn+resume capped to 3 attempts / 60 s
      inputSelectionStore.ts        nanostore exposing the active text-input selection handle
      interfaces.ts                 internal interfaces (ComposerActions, GatewayRpc, etc.)
      overlayStore.ts               nanostores for overlay state
      scroll.ts                     viewport scroll with text-selection anchor sync
      setupHandoff.ts               launches external hermes setup, suspends Ink while it runs
      spawnHistoryStore.ts          ring buffer of finished subagent fan-out snapshots
      turnController.ts             stateful turn lifecycle driver (streaming, tools, reasoning)
      turnStore.ts                  nanostore for turn state (streaming, tools, reasoning, subagents)
      uiStore.ts                    nanostores for UI flags (busy, sid, mouseTracking, etc.)
      useComposerState.ts           draft + multiline buffer + queue editing
      useConfigSync.ts              config polling and MCP reload on mtime change
      useInputHandlers.ts           keypress routing
      useLongRunToolCharms.ts       ambient activity messages for tools running longer than 8 s
      useMainApp.ts                 top-level composition hook
      useSessionLifecycle.ts        session create / resume / activate / close
      useSubmission.ts              message send, shell exec, interpolation, busy-input-mode dispatch

      slash/
        types.ts                    SlashCommand interface and SlashRunCtx execution context
        registry.ts                 SLASH_COMMANDS assembly and findSlashCommand lookup
        commands/
          billing.ts                /billing — manage Nous remote spending
          core.ts                   general TUI commands
          credits.ts                /credits
          debug.ts                  /heapdump, /mem
          ops.ts                    operations commands
          session.ts                session and agent commands
          setup.ts                  /setup wizard

    components/
      activeSessionSwitcher.tsx  active session switch overlay
      agentsOverlay.tsx          subagent delegation overlay
      appChrome.tsx              status bar, input row, completions
      appLayout.tsx              top-level layout composition
      appOverlays.tsx            overlay routing (pickers, prompts)
      billingOverlay.tsx         billing overlay
      branding.tsx               banner + session summary
      fpsOverlay.tsx             FPS debug overlay
      helpHint.tsx               contextual help hint
      markdown.tsx               Markdown-to-Ink renderer
      maskedPrompt.tsx           masked input for sudo / secrets
      messageLine.tsx            transcript rows
      modelPicker.tsx            model switch picker
      overlayControls.tsx        shared overlay control buttons
      pluginsHub.tsx             plugins hub overlay
      prompts.tsx                approval + clarify flows
      queuedMessages.tsx         queued input preview
      skillsHub.tsx              skills hub overlay
      streamingAssistant.tsx     live streaming assistant row
      streamingMarkdown.tsx      streaming Markdown renderer
      textInput.tsx              custom line editor
      themed.tsx                 theme-aware wrapper
      thinking.tsx               spinner, reasoning, tool activity
      todoPanel.tsx              todo list panel

    config/
      env.ts                     environment variable resolution and Termux/mouse defaults
      limits.ts                  paste size, live-render and history limits
      timing.ts                  streaming batch and debounce timing constants

    content/
      charms.ts                  ambient activity strings for long-running tools
      faces.ts                   agent face / kaomoji pool
      fortunes.ts                /fortune quote pool
      hotkeys.ts                 platform-aware hotkey display strings
      placeholders.ts            rotating input placeholder strings
      setup.ts                   setup-required panel content
      verbs.ts                   tool activity verb map (browser → browsing, etc.)

    domain/
      blockLayout.ts             block layout and lead-gap helpers
      details.ts                 details visibility mode resolution (hidden/collapsed/expanded)
      messages.ts                message formatting and transcript helpers
      paths.ts                   cwd shortening and path display helpers
      providers.ts               provider display name helpers
      roles.ts                   message role color and label helpers
      slash.ts                   slash command parsing and TUI session model flag
      usage.ts                   token usage zero value and helpers
      viewport.ts                viewport height estimation helpers

    hooks/
      useCompletion.ts           tab completion (slash + path)
      useGitBranch.ts            current git branch via child_process execFile
      useInputHistory.ts         persistent history navigation
      useQueue.ts                queued message management
      useVirtualHistory.ts       virtual list scroll and height tracking

    lib/
      circularBuffer.ts          fixed-size generic ring buffer
      clipboard.ts               clipboard read / write via child_process
      editor.ts                  $EDITOR launch, PATH resolution, and Ink suspend
      emoji.ts                   emoji and variation selector width helpers
      externalCli.ts             external CLI subprocess launcher
      externalLink.ts            open URLs in the system browser
      forceTruecolor.ts          24-bit truecolor override before chalk imports
      fpsStore.ts                Ink frame FPS tracker nanostore
      fuzzy.ts                   lightweight fuzzy subsequence scorer
      gracefulExit.ts            clean shutdown with failsafe timeout
      history.ts                 persistent input history (read/append to disk)
      inputMetrics.ts            input width and wrap metrics
      liveProgress.ts            todo helpers and tool-shelf message assembly
      mathUnicode.ts             best-effort LaTeX → Unicode for inline math
      memory.ts                  V8 heap snapshot and diagnostics helpers
      memoryMonitor.ts           automatic heap-dump trigger on high usage
      messages.ts                transcript message append helpers
      openExternalUrl.ts         platform-aware URL opener (macOS/Linux/Windows)
      osc52.ts                   OSC 52 terminal clipboard copy sequence
      parentLog.ts               append-only log to ~/.hermes/tui-parent.log
      perfPane.tsx               FPS / render perf overlay pane
      platform.ts                platform-aware keybinding and SSH detection helpers
      precisionWheel.ts          high-precision scroll wheel with sticky-frame budget
      prompt.ts                  composer prompt text helpers (Termux-safe)
      reasoning.ts               reasoning tag detection and split helpers
      rpc.ts                     JSON-RPC result and command dispatch helpers
      subagentTree.ts            subagent tree flattening and aggregate helpers
      syntax.ts                  syntax token types and theme-aware highlighting
      terminalModes.ts           terminal mode reset sequences (kitty, mouse, etc.)
      terminalParity.ts          VSCode-like terminal detection and hint helpers
      terminalSetup.ts           IDE keybinding config file install helpers
      termux.ts                  Termux platform detection helpers
      text.ts                    text helpers, ANSI detection, tool trail builders
      todo.ts                    todo item tone and display helpers
      viewportStore.ts           viewport height nanostore via ScrollBoxHandle
      virtualHeights.ts          virtual list row height estimation
      wheelAccel.ts              scroll wheel acceleration state machine

    protocol/
      interpolation.ts           {!cmd} inline shell interpolation regex and helpers
      paste.ts                   bracketed paste snippet token regex

    types/
      hermes-ink.d.ts            type declarations for @hermes/ink

    __tests__/                   vitest suite
```

相关的 Python 方面：

```text
tui_gateway/
  entry.py               stdio entrypoint
  server.py              RPC handlers and session logic
  render.py              optional rich/ANSI bridge
  slash_worker.py        persistent HermesCLI subprocess for slash commands
```
