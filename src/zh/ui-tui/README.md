# Hermes TUI

专为Hermes打造的基于React与Ink的终端用户界面。屏幕渲染由TypeScript负责，而会话管理、工具操作、模型调用以及大部分命令逻辑则由Python处理。

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

`src/app.tsx` 是用户界面的核心所在。复杂的逻辑被拆分到 `src/app/` 目录下：

- `createGatewayEventHandler.ts` —— 将网关事件映射为状态更新
- `createSlashHandler.ts` —— 处理本地斜杠命令的路由
- `useComposerState.ts` —— 处理草稿、多行缓冲区及队列编辑功能
- `useInputHandlers.ts` —— 负责按键处理逻辑
- `useTurnState.ts` —— 管理智能体对话轮次的全生命周期
- `overlayStore.ts` / `uiStore.ts` —— 用于存储覆盖层状态和界面状态的 nanostores
- `gatewayContext.tsx` —— 为网关客户端提供的 React context
- `constants.ts`, `helpers.ts`, `interfaces.ts`

顶层的 `app.tsx` 会将这些组件整合成 Ink 树结构，从而呈现包含“静态”对话记录、实时流式助手行、提示覆盖层、队列预览、状态规则、输入行以及补全列表的界面。

在顶层管理的状态包括：

- 对话记录与流式输出状态
- 队列中的消息及输入历史记录
- 会话生命周期状态
- 工具处理进度与推理文本
- 用于审批、澄清、特殊权限请求及敏感信息输入的提示流程
- 斜杠命令的路由逻辑
- Tab 补全与路径补全功能
- 来自网关主题数据的主题状态

最终界面会以标准的 Ink 树形式呈现，包含“静态”对话记录、实时流式助手行、提示覆盖层、队列预览、状态规则、输入行以及补全列表。

欢迎面板的内容由 `session.info` 提供，并通过 `branding.tsx` 进行渲染。

## 快捷键与交互操作

当前的输入行为由 `app.tsx`、`components/textInput.tsx` 以及各种提示/选择器组件共同负责处理。

### 主要聊天输入操作

| 键位                             | 功能描述                                                                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Enter`                         | 提交当前草稿内容                                                                                                                                |
| 连按两次空 `Enter`             | 若队列中有消息且智能体正在处理任务，则中断当前运行；若队列中有消息且智能体处于空闲状态，则发送队列中的下一条消息 |
| `Shift+Enter` / `Alt+Enter`     | 在当前草稿中插入换行符                                                                                                                   |
| `\` + `Enter`                   | 将该行内容添加到多行缓冲区中（适用于不支持修饰键的终端）                                                               |
| `Ctrl+C`                        | 中断当前运行，或清除当前草稿，若没有待处理任务则直接退出                                                                         |
| `Ctrl+D`                        | 退出程序                                                                                                                                                    |
| `Cmd/Ctrl+G` / `Alt+G`          | 使用当前草稿内容打开 `$EDITOR` 编辑器（在 VSCode/Cursor 中可使用 `Alt+G`——因为这些工具将主键绑定为“查找下一个”功能）                                     |
| `Ctrl+L`                        | 开启新会话（功能与 `/clear` 相同）                                                                                                                          |
| `Ctrl+V` / `Alt+V`              | 先粘贴文本，若适用则自动尝试插入图片或路径附件                                                                               |
| `Tab`                           | 应用当前选中的补全内容                                                                                                                             |
| `Up/Down`                       | 若补全列表已打开，则在选项间切换；否则先编辑队列中的消息，再查看输入历史记录                                         |
| `Left/Right`                    | 移动光标位置                                                                                                                                         |
| 按下修饰键后使用 `Left/Right`           | 当终端同时发送 `Ctrl` 或 `Meta` 键与方向键时，按词移动光标                                                                                |
| `Home` / `Ctrl+A`               | 移动到行首                                                                                                                                           |
| `End` / `Ctrl+E`                | 移动到行尾                                                                                                                                             |
| `Backspace`                     | 删除光标左侧的字符                                                                                                          |
| `Delete`                        | 删除光标右侧的字符                                                                                                         |
| 按下修饰键后使用 `Backspace`            | 删除上一个单词                                                                                                                                |
| 按下修饰键后使用 `Delete`               | 删除下一个单词                                                                                                                                    |
| `Ctrl+W`                        | 删除上一个单词                                                                                                                                |
| `Ctrl+U`                        | 从光标位置向左删除直至行首                                                                                                    |
| `Ctrl+K`                        | 从光标位置向右删除直至行尾                                                                                                           |
| `Meta+B` / `Meta+F`             | 按词移动光标                                                                                                                                            |
| `!cmd`                          | 通过网关执行Shell命令                                                                                                                 |
| `{!cmd}`                        | 在发送消息前进行内联Shell插值处理；队列中的草稿内容在发送前会保持原始文本形式                                                            |

注意事项：

- 仅当存在补全选项且未处于多行输入模式时，`Tab` 键才会生效。
- 队列/历史记录导航功能也仅在非多行模式下可用。
- `PgUp` / `PgDn` 功能由终端模拟器处理，TUI 不会支持这些操作。

### 提示与选择器模式

| 使用场景                     | 键位                | 功能描述                                          |
| --------------------------- | ------------------- | ------------------------------------------------- |
| 审批提示                     | `Up/Down`, `Enter`  | 在选项间切换并确认所选审批选项                     |
| 审批提示                     | `o`, `s`, `a`, `d`  | 快速选择“仅一次”、“当前会话”、“始终允许”、“拒绝”     |
| 审批提示                     | `Esc`, `Ctrl+C`     | 拒绝请求                                              |
| 带选项的澄清提示             | `Up/Down`, `Enter`  | 在选项间切换并确认所选选项              |
| 带选项的澄清提示             | 数字键              | 快速选择对应编号的选项                         |
| 带选项的澄清提示             | 输入“Other”后按 `Enter` | 切换到自由文本输入模式                       |
| 自由文本澄清模式             | 按 `Enter`          | 提交输入的答案                               |
| 特殊权限/敏感信息提示        | 按 `Enter`          | 提交输入的值                                |
| 特殊权限/敏感信息提示        | 按 `Ctrl+C`          | 通过发送空响应来取消操作                       |
| 继续选择器操作               | `Up/Down`, `Enter`  | 在已选会话间切换并继续操作                      |
| 继续选择器操作               | `1-9`               | 快速选择前九个可见的会话之一                 |
| 继续选择器操作               | `Esc`, `Ctrl+C`     | 关闭选择器                                  |

注意事项：

- 自由文本澄清模式及带掩码的提示框均使用 `ink-text-input` 组件，因此其文本编辑功能遵循该组件的默认绑定规则，而非 `components/textInput.tsx` 的规则。
- 当有阻塞性提示窗口打开时，主要的聊天输入快捷键会被禁用。
- 目前版本的客户端中，澄清模式没有专用的取消快捷键。特殊权限和敏感信息提示仅支持通过应用层的阻塞处理函数使用 `Ctrl+C` 进行取消。

### 交互规则

- 当智能体正在处理任务时输入的纯文本会进入队列，而不会立即发送。
- 斜杠命令和 `!cmd` 语句不会进入队列，即使智能体正在运行也会立即执行。
- 每次智能体回复后，队列中的内容会自动清除，除非当前正在编辑某个队列项。
- `Up/Down` 键的优先级高于历史记录编辑功能，只有当没有队列项需要编辑时，历史记录功能才会启用。
- 在编辑队列中的草稿时，其原有的 `!cmd` 和 `{!cmd}` 格式内容会保留不变。只有当该队列项真正被发送时，Shell命令和插值功能才会生效。
- 如果将队列中的某项内容加载到输入框并再次输入纯文本，该队列项将被替换，从队列预览中移除，并提升到优先发送位置。如果智能体仍处于忙碌状态，编辑后的内容会被移到队列最前端，在当前任务处理完成后发送。
- 补全请求的触发会有 60 毫秒的延迟处理。以 `/` 开头的输入会使用 `complete.slash` 函数处理；以 `./`、`../`、`~/`、`/` 或 `@` 开头的后缀 token 会使用 `complete.path` 函数处理。
- 粘贴的文本会直接作为内联内容插入到草稿中，不会被自动换行处理。
- `Cmd/Ctrl+G`（在 VSCode/Cursor 中则为 `Alt+G`，因为这些工具会拦截“查找下一个”功能的主键）会将当前草稿内容，包括多行缓冲区中的内容，写入临时文件，暂停 Ink 框架的运行，启动 `$EDITOR` 编辑器；如果编辑器正常关闭，则恢复 TUI 界面并提交已保存的文本。
- 输入历史记录会存储在 `~/.hermes/.hermes_history` 文件中，或 `HERMES_HOME` 指定的路径下。

## 渲染方式

智能体的输出通过以下两种方式之一进行渲染：

- 如果消息内容本身已包含 ANSI 格式，`messageLine.tsx` 会直接将其打印出来；
- 否则，`components/markdown.tsx` 会将简化的 Markdown 语法转换为 Ink 组件形式进行渲染。

该 Markdown 渲染器能够处理标题、列表、块引文、表格、代码块、差异高亮显示、内联代码、强调文本、链接以及普通网址等内容。

工具/状态相关的活动信息会显示在实时的活动栏中，而对话记录行则始终聚焦于用户与智能体的对话轮次。

## 提示流程Python网关可以暂停主循环并请求结构化输入：

- `approval.request`：允许一次、允许当前会话、始终允许或拒绝
- `clarify.request`：从选项中选择或输入自定义答案
- `sudo.request`：遮蔽式密码输入
- `secret.request`：为指定环境变量输入遮蔽值
- `session.list`：供`SessionPicker`用于恢复会话

这些都是`app.tsx`中的状态型UI分支，并非独立的界面。

## 命令

本地斜杠处理程序负责处理那些需要直接客户端操作的内置命令：

- `/help`
- `/quit`, `/exit`, `/q`
- `/clear`
- `/new`
- `/compact`
- `/resume`
- `/copy`
- `/paste`
- `/details`
- `/logs`
- `/statusbar`, `/sb`
- `/queue`
- `/undo`
- `/retry`

注意事项：

- `/copy`通过OSC 52发送选中的助手回复。
- 不带参数的`/paste`会请求网关附上剪贴板内容图像。
- 文本粘贴仍为内联格式；在需要使用`/paste`之前，`Cmd+V` / `Ctrl+V`会优先处理分层文本/OSC52/图像格式。
- `/details [hidden|collapsed|expanded|cycle]`用于控制思考过程及工具详情的显示状态。
- `/statusbar`用于切换状态栏的开启与关闭。

其他所有请求都会依次传递给：

1. `slash.exec`
2. `command.dispatch`

这样一来，Python即可拥有自己的别名、插件、技能以及基于注册表的命令，而无需在TUI中重复实现相同逻辑。

## 事件体系

目前客户端处理的主要事件类型如下：

| 事件类型                  | 数据内容                                         |
| ------------------------- | ----------------------------------------------- |
| `gateway.ready`          | `{ skin? }`                                     |
| `session.info`           | 用于标题栏及工具/技能面板的会话元数据             |
| `message.start`          | 启动助手流式响应                                 |
| `message.delta`          | `{ text, rendered? }`                           |
| `message.complete`       | `{ text, rendered?, usage, status }`            |
| `thinking.delta`         | `{ text }`                                      |
| `reasoning.delta`        | `{ text }`                                      |
| `reasoning.available`    | `{ text }`                                      |
| `status.update`          | `{ kind, text }`                                |
| `tool.start`             | `{ tool_id, name, context? }`                   |
| `tool.progress`          | `{ name, preview }`                             |
| `tool.complete`          | `{ tool_id, name }`                             |
| `clarify.request`        | `{ question, choices?, request_id }`            |
| `approval.request`       | `{ command, description }`                      |
| `sudo.request`           | `{ request_id }`                                |
| `secret.request`         | `{ prompt, env_var, request_id }`               |
| `background.complete`    | `{ task_id, text }`                             |
| `error`                  | `{ message }`                                   |
| `gateway.stderr`         | 由子进程的错误输出汇总而成                     |
| `gateway.protocol_error` | 由格式错误的标准输出汇总而成                   |

## 主题模型

客户端初始使用`theme.ts`中的`DEFAULT_THEME`作为主题，随后再合并`gateway.ready`中传来的网关界面配置数据。

当前可覆盖的品牌元素包括：

- 助手名称
- 提示符符号
- 欢迎语
- 告别语

当前可覆盖的颜色包括：

- 标题栏标题、强调色、边框色、背景色、暗化效果
- 标签、确定按钮、错误提示、警告提示的颜色

`branding.tsx`会利用这些值来设置日志图标、会话面板以及更新通知的样式。

## 文件结构图

```text
ui-tui/
  packages/hermes-ink/   forked Ink renderer (local dep)
  src/
    entry.tsx            TTY gate + render()
    app.tsx              top-level Ink tree, composes src/app/*
    gatewayClient.ts     child process + JSON-RPC bridge
    theme.ts             default palette + skin merge
    constants.ts         display constants, hotkeys, tool labels
    types.ts             shared client-side types
    banner.ts            ASCII art data

    app/
      createGatewayEventHandler.ts  event → state mapping
      createSlashHandler.ts         local slash dispatch
      useComposerState.ts           draft + multiline + queue editing
      useInputHandlers.ts           keypress routing
      useTurnState.ts               agent turn lifecycle
      overlayStore.ts               nanostores for overlays
      uiStore.ts                    nanostores for UI flags
      gatewayContext.tsx             React context for gateway client
      constants.ts                  app-level constants
      helpers.ts                    pure helpers
      interfaces.ts                 internal interfaces

    components/
      appChrome.tsx      status bar, input row, completions
      appLayout.tsx      top-level layout composition
      appOverlays.tsx    overlay routing (pickers, prompts)
      branding.tsx       banner + session summary
      markdown.tsx       Markdown-to-Ink renderer
      maskedPrompt.tsx   masked input for sudo / secrets
      messageLine.tsx    transcript rows
      modelPicker.tsx    model switch picker
      prompts.tsx        approval + clarify flows
      queuedMessages.tsx queued input preview
      sessionPicker.tsx  session resume picker
      textInput.tsx      custom line editor
      thinking.tsx       spinner, reasoning, tool activity

    hooks/
      useCompletion.ts   tab completion (slash + path)
      useInputHistory.ts persistent history navigation
      useQueue.ts        queued message management
      useVirtualHistory.ts in-memory history for pickers

    lib/
      history.ts         persistent input history
      messages.ts        message formatting helpers
      osc52.ts           OSC 52 clipboard copy
      rpc.ts             JSON-RPC type helpers
      text.ts            text helpers, ANSI detection, previews

    types/
      hermes-ink.d.ts    type declarations for @hermes/ink

    __tests__/           vitest suite
```

相关的 Python 方面：

```text
tui_gateway/
  entry.py               stdio entrypoint
  server.py              RPC handlers and session logic
  render.py              optional rich/ANSI bridge
  slash_worker.py        persistent HermesCLI subprocess for slash commands
```
