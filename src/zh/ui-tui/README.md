# Hermes TUI

专为Hermes打造的基于React与Ink的终端用户界面。屏幕渲染由TypeScript负责，而会话管理、工具操作、模型调用以及大部分命令逻辑则由Python处理。

```bash
hermes --tui
```

## 运行机制

客户端入口文件为 `src/entry.tsx`。如果 `stdin` 不是终端设备，该文件会立即退出；随后会启动 `GatewayClient`，最后渲染 `App` 组件。

`GatewayClient` 会创建：

```text
python -P -m tui_gateway.entry
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

格式错误的标准输出行会被视为协议噪声，并以 `gateway.protocol_error` 的形式呈现。而标准错误行则会被标记为 `gateway.stderr`。这两种输出都不会直接显示在终端上。

## 运行方式

从仓库根目录出发，常规的运行路径为：

```bash
hermes --tui
```

该命令行工具要求必须存在 `ui-tui/dist/entry.js` 文件，或者能够获取到完整的源代码，以便执行 `npm install` 和 `npm run dev` 操作。

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

## 应用模型

`src/app.tsx` 是用户界面的核心。复杂的逻辑被拆分到 `src/app/` 目录下：

- `src/app/createGatewayEventHandler.ts` —— 将网关事件映射为状态更新
- `src/app/createSlashHandler.ts` —— 处理本地斜杠命令的调度
- `src/app/useComposerState.ts` —— 负责草稿编辑、多行缓冲区以及队列编辑功能
- `src/app/useInputHandlers.ts` —— 负责按键事件的路由处理
- `src/app/useMainApp.ts` —— 顶层组合钩子：连接所有子钩子，管理对话记录历史、会话轮询，并为 `app.tsx` 提供所需属性
- `src/app/useSessionLifecycle.ts` —— 处理会话的创建、恢复、激活、关闭以及可见历史记录的重置
- `src/app/useSubmission.ts` —— 负责消息发送、Shell 命令执行（`!cmd`）、内联插值（`{!cmd}`），以及忙碌输入模式的管理（排队、引导、中断）
- `src/app/turnController.ts` —— 一个带状态管理的类，负责驱动对话轮次生命周期：缓冲流式数据变化，管理工具与推理状态，处理中断和消息完成后的状态转换
- `src/app/turnStore.ts` —— 用于存储对话轮次状态的 nanostore（包含流式文本、工具信息、推理内容、子智能体状态、待办事项及操作轨迹）
- `src/app/useConfigSync.ts` —— 在会话启动时获取 `config.get full` 的配置信息，并每5秒轮询一次配置的修改时间；应用显示设置并在配置发生变化时触发 MCP 重新加载
- `src/app/useLongRunToolCharms.ts` —— 当工具运行时间超过8秒时，触发相关活动提示消息
- `src/app/overlayStore.ts` / `src/app/uiStore.ts` —— 用于存储覆盖层和界面状态的 nanostore
- `src/app/delegationStore.ts` —— 用于存储子智能体生成数量上限以及覆盖层折叠状态的信息
- `src/app/spawnHistoryStore.ts` —— 内存中的环形存储结构（最多保存最近10条），用于记录已完成的子智能体输出快照；在对话轮次结束时为 `/replay` 功能填充数据
- `src/app/inputSelectionStore.ts` —— 用于存储当前活动文本输入选择范围的 nanostore
- `src/app/gatewayContext.tsx` —— 用于网关客户端的 React 上下文
- `src/app/gatewayRecovery.ts` —— 一个纯函数，用于在网关崩溃后决定是否重新启动并继续运行，最多尝试3次，每次间隔60秒
- `src/app/setupHandoff.ts` —— 启动外部 `hermes setup` 工具，在其运行期间暂停 Ink 应用，成功后会打开新的会话
- `src/app/scroll.ts` —— 滚动视口的同时保持文本选择位置同步
- `src/app/interfaces.ts` —— 内部接口定义（如 ComposerActions、GatewayRpc 等）

### 斜杠命令子系统（`src/app/slash/`）

- `types.ts` —— 定义 `SlashCommand` 接口以及 `SlashRunCtx` 执行上下文（包含网关 RPC 调用、对话记录辅助函数、会话引用及过时保护机制）
- `registry.ts` —— 按注册顺序从所有命令文件中汇总 `SLASH_COMMANDS`（按核心功能 → 计费功能 → 信用点管理 → 会话管理 → 操作管理 → 设置功能 → 调试功能的顺序），并提供 `findSlashCommand(name)` 方法以实现不区分大小写的查询
- `commands/core.ts` —— 通用 TUI 命令
- `commands/billing.ts` —— `/billing` 命令：管理 Nous 终端计费功能，包括购买信用点、自动重新加载以及额度设置
- `commands/credits.ts` —— `/credits` 命令
- `commands/session.ts` —— 会话及智能体相关命令
- `commands/ops.ts` —— 操作类命令
- `commands/setup.ts` —— `/setup` 命令
- `commands/debug.ts` —— `/heapdump`、`/mem` 调试命令

顶层 `app.tsx` 会将这些组件整合为 Ink 树结构，其中包含静态对话记录输出、实时流式助手行、提示覆盖层、队列预览、状态栏、输入行以及补全列表。

在顶层管理的状态包括：

- 对话记录与流式内容状态
- 队列中的消息及输入历史记录
- 会话生命周期状态
- 工具处理进度与推理文本
- 用于请求批准、澄清问题、提升权限及输入敏感信息的提示流程
- 斜杠命令的路由处理逻辑
- Tab 补全与路径补全功能
- 来自网关主题数据的主题状态

最终渲染出的界面为标准的 Ink 树结构，包含静态对话记录输出、实时流式助手行、提示覆盖层、队列预览、状态栏、输入行以及补全列表。

欢迎面板的内容由 `session.info` 提供，并通过 `branding.tsx` 文件进行渲染。

## 快捷键与交互操作

当前的输入行为由 `app.tsx`、`components/textInput.tsx` 以及各种提示/选择组件共同处理。

### 主要聊天输入操作

| 键位                         | 操作说明                                                                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Enter`                      | 提交当前的草稿内容                                                                                                                                |
| 连按两次空 `Enter`            | 若队列中有消息且智能体正在处理任务，则中断当前运行；若队列中有消息且智能体处于空闲状态，则发送队列中的下一条消息                         |
| `Shift+Enter` / `Alt+Enter`   | 在当前草稿中插入换行符                                                                                                                             |
| `\` + `Enter`                 | 将该行内容追加到多行缓冲区中（适用于不支持修饰键的终端作为备用方案）                                                                                               |
| `Ctrl+C`                     | 中断当前运行，或清除当前草稿，若没有待处理任务则直接退出应用                                                                                                 |
| `Ctrl+D`                     | 退出应用                                                                                                                                                |
| `Cmd/Ctrl+G` / `Alt+G`        | 使用当前草稿内容打开 `$EDITOR` 编辑器（在 VSCode/Cursor 中可使用 `Alt+G` —— 它们将主键绑定为“查找下一个”功能）                 |
| `Ctrl+L`                     | 打开新会话（功能与 `/clear` 相同）                                                                                                                          |
| `Ctrl+V` / `Alt+V`            | 先尝试粘贴文本，若不适用则回退为图片/路径附件的插入功能                                                                                                     |
| `Tab`                        | 应用当前选中的补全选项                                                                                                                             |
| `Up/Down`                    | 若补全列表已打开，则在候选项之间切换；否则先编辑队列中的消息，再查看输入历史记录                                                                                     |
| `Left/Right`                  | 移动光标位置                                                                ---------------------------------------------------------------------------- |
| 按住修饰键后使用 `Left/Right` | 当终端发送 `Ctrl` 或 `Meta` 键与方向键组合时，按住修饰键可逐词移动光标                                                                                         |
| `Home` / `Ctrl+A`               | 移动到行首                                                                ---------------------------------------------------------------------------- |
| `End` / `Ctrl+E`                | 移动到行尾                                                                ---------------------------------------------------------------------------- |
| `Backspace`                   | 删除光标左侧的字符                                                                ---------------------------------------------------------------- |
| `Delete`                     | 删除光标右侧的字符                                                                ---------------------------------------------------------------- |
| 按住修饰键后使用 `Backspace` | 删除上一个单词                                                                ---------------------------------------------------------------------------- |
| 按住修饰键后使用 `Delete`   | 删除下一个单词                                                                ---------------------------------------------------------------------------- |
| `Ctrl+W`                      | 删除上一个单词                                                                ---------------------------------------------------------------------------- |
| `Ctrl+U`                      | 从光标位置向左删除直到行首                                                                                                                            |
| `Ctrl+K`                      | 从光标位置向右删除直到行尾                                                                                                                            |
| `Meta+B` / `Meta+F`             | 逐词移动光标                                                                ---------------------------------------------------------------------------- |
| `!cmd`                        | 通过网关运行 Shell 命令                                                                ---------------------------------------------------------------- |
| `{!cmd}`                      | 在发送消息前进行内联 Shell 插值；队列中的草稿内容会以原始文本形式保留，直到实际发送为止                                                                                 |

注意事项：

- 仅当存在补全选项且未处于多行输入模式时，`Tab` 键才会触发补全功能。
- 队列/历史记录导航功能也仅在非多行输入模式下有效。
- `PgUp` / `PgDn` 操作由终端模拟器处理，TUI 层不支持这些功能。

### 提示与选择模式| 场景                         | 按键                | 行为描述                                         |
| ---------------------------- | ------------------- | ------------------------------------------------- |
| 审批提示框                   | `Up/Down`, `Enter`  | 移动并确认所选的审批选项                         |
| 审批提示框                   | `o`, `s`, `a`, `d`  | 快速选择“一次性”、“会话有效”、“始终允许”、“拒绝”   |
| 审批提示框                   | `Esc`, `Ctrl+C`     | 拒绝                                             |
| 带选项的澄清提示框           | `Up/Down`, `Enter`  | 移动并确认所选的选项                             |
| 带选项的澄清提示框           | 单位数              | 快速选择对应的编号选项                         |
| 带选项的澄清提示框           | 输入“Other”后按 `Enter` | 切换到自由文本输入模式                           |
| 进入自由文本模式             | `Enter`             | 提交输入的答案                                   |
| sudo/密钥提示框               | `Enter`             | 提交输入的值                                     |
| sudo/密钥提示框               | `Ctrl+C`            | 通过发送空响应取消                             |
| 恢复选择器功能               | `Up/Down`, `Enter`  | 移动并继续选择已选会话                           |
| 恢复选择器功能               | `1-9`               | 快速选择前九个可见会话中的任意一个                 |
| 恢复选择器功能               | `Esc`, `Ctrl+C`     | 关闭选择器                                       |

备注：

- 自由文本模式及带掩码的提示框均使用 `ink-text-input` 组件，因此文本编辑遵循该组件的默认绑定规则，而非 `components/textInput.tsx` 的规则。
- 当有阻塞性提示框打开时，主聊天输入的热键功能会被暂时禁用。
- 目前客户端中，澄清模式没有专用的取消快捷键。sudo和密钥提示框仅通过应用层的阻塞处理函数提供 `Ctrl+C` 取消功能。

### 交互规则

- 当智能体正在处理任务时输入的纯文本会被放入队列，而非立即发送。
- 斜杠命令及 `!cmd` 格式的指令不会被放入队列，即使在任务执行中也会立即执行。
- 每次智能体回复后队列内容会自动清空，除非当前有正在编辑的队列项。
- `Up/Down` 键优先用于编辑队列中的消息，而历史记录仅在无待编辑队列项时才会显示。
- 在编辑队列中的草稿时，其原有的 `!cmd` 和 `{!cmd}` 格式内容会被保留。只有当该队列项真正被发送时，Shell命令及插值功能才会生效。
- 如果将队列中的某项内容加载到输入框后再输入纯文本，该队列项将被替换，从队列预览中移除，并提升为下一个待发送项。如果智能体仍处于忙碌状态，编辑后的内容会被移到队列最前端，在当前任务完成后发送。
- 补全请求的延迟时间为60毫秒。以 `/` 开头的输入会使用 `complete.slash` 函数处理；以 `./`、`../`、`~/`、`/` 或 `@` 开头的尾部标记则使用 `complete.path` 函数处理。
- 粘贴的文本会直接插入到草稿中，不会被换行符拆分。
- `Cmd/Ctrl+G`（在VSCode/Cursor中为 `Alt+G`，该快捷键会拦截“查找下一个”功能的主键输入）会将当前草稿内容，包括多行缓冲区内容，写入临时文件，暂停Ink组件运行，启动 `$EDITOR` 编辑器；如果编辑器正常退出，则恢复TUI界面并提交保存的文本。
- 输入历史记录存储在 `~/.hermes/.hermes_history` 文件中，或 `HERMES_HOME` 指定的路径下。

## 渲染方式

智能体的输出通过以下两种方式之一进行渲染：

- 如果消息内容已包含ANSI格式，`messageLine.tsx` 会直接将其打印出来；
- 否则，`components/markdown.tsx` 会将简化的Markdown语法转换为Ink组件进行渲染。

该Markdown渲染器可处理标题、列表、块引文、表格、代码块、差异高亮显示、内联代码、强调文本、链接以及普通URL。

工具/状态相关的操作会显示在实时活动栏中，而对话记录行则始终聚焦在用户与智能体的交互轮次上。

## 提示流处理

Python网关可以暂停主循环并请求结构化输入：

- `approval.request`：允许“一次性”、“会话有效”、“始终允许”或“拒绝”；
- `clarify.request`：从选项中选择或输入自定义答案；
- `sudo.request`：输入带掩码的密码；
- `secret.request`：输入指定环境变量的带掩码值；
- `session.list`：供 `SessionPicker` 组件在调用 `/resume` 时使用。

这些均为 `app.tsx` 文件中的状态型UI分支，并非独立的页面。

## 命令

以下命令由TUI客户端直接处理。未被识别的命令会通过 `slash.exec` 和 `command.dispatch` 传递给Python网关处理。

### 核心命令（`core.ts`）
`/help`, `/quit`（别名 `/exit`）、`/update`、`/clear`（别名 `/new`）、
`/compact`、`/copy`、`/paste`、`/details`（别名 `/detail`）、
`/statusbar`（别名 `/sb`）、`/queue`（别名 `/q`）、`/logs`、`/history`、
`/save`、`/undo`、`/retry`、`/steer`、`/mouse`（别名 `/scroll`）、
`/status`、`/title`、`/fortune`、`/redraw`、`/terminal-setup`

### 计费相关命令（`billing.ts`）
`/billing` —— 管理Nous终端的计费功能，包括购买积分、自动充值及设置使用限额

### 会话相关命令（`session.ts`）
`/model`、`/sessions`（别名 `/switch`、`/session`、`/resume`）、
`/background`（别名 `/bg`、`/btw`）、`/image`、`/personality`、
`/compress`、`/branch`（别名 `/fork`）、`/voice`、`/skin`、
`/indicator`、`/yolo`、`/reasoning`、`/fast`、`/busy`、`/verbose`、`/usage`

### 操作管理命令（`ops.ts`）
`/stop`、`/reload-mcp`（别名 `/reload_mcp`）、`/reload`、`/browser`、
`/rollback`、`/agents`（别名 `/tasks`）、`/replay`、`/replay-diff`、
`/skills`、`/reload-skills`（别名 `/reload_skills`）、`/plugins`、`/tools`

### 积分相关命令（`credits.ts`）
`/credits` —— 查看Nous积分余额及为浏览器充值

### 设置相关命令（`setup.ts`）
`/setup` —— 启动外部 `hermes setup` 向导，该向导运行期间会暂停Ink组件的功能

### 调试相关命令（`debug.ts`）
`/heapdump`、`/mem` —— 提供V8内存诊断功能

---

以上未涵盖的指令都会依次传递给：

1. `slash.exec`
2. `command.dispatch`

这样一来，Python网关即可处理别名、插件、技能以及基于注册表的命令，而无需在TUI客户端中重复实现相同逻辑。

## 事件体系

客户端目前处理的常见事件类型如下：

| 事件类型                     | 数据内容                                                                     |
| ---------------------------- | --------------------------------------------------------------------------- |
| `gateway.ready`            | `{ skin? }`                                                                 |
| `skin.changed`             | `{ skin }`                                                                  |
| `session.info`             | 用于显示横幅以及工具/技能面板的会话元数据                         |
| `message.start`            | 开始智能体消息流输出                                             |
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
| `sudo.expire`              | `{ request_id }` 清除已超时的sudo提示框                             |
| `secret.request`           | `{ prompt, env_var, request_id }`                                           |
| `secret.expire`            | `{ request_id }` 清除已超时的密钥提示框                           |
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
| `gateway.stderr`           | 由子组件的标准错误流合成而来                                     |
| `gateway.protocol_error`   | 由格式错误的标准输出流合成而来                                     |
| `gateway.start_timeout`    | `{ cwd?, python?, stderr_tail? }`                                           |

## 主题模型

客户端初始使用 `theme.ts` 文件中的 `DEFAULT_THEME` 主题，随后会从 `gateway.ready` 事件中合并网关提供的主题数据。

当前可覆盖的品牌相关配置包括：

- 智能体名称
- 提示符符号
- 欢迎语
- 告别语

当前可覆盖的颜色相关配置包括：

- 横幅标题、强调色、边框颜色、背景色及透明度设置
- 标签、确定按钮、错误提示、警告提示的颜色设置

`branding.tsx` 文件会利用这些配置来生成Logo、会话面板以及更新通知等内容。

## 文件结构映射

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
          billing.ts                /billing — manage Nous terminal billing
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
