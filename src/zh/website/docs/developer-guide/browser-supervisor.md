---
sidebar_position: 18
title: "Browser CDP Supervisor"
description: "How Hermes detects and responds to native JS dialogs and interacts with cross-origin iframes via a persistent CDP connection."
---

# 浏览器 CDP 监控器

CDP 监控器填补了 Hermes 浏览器工具链中的两个长期存在的缺陷：

1. **原生 JS 对话框**（如 `alert`/`confirm`/`prompt`/`beforeunload`）会阻塞页面的 JS 线程。在没有监控机制的情况下，代理无法得知对话框已打开——后续的工具调用将会挂起或抛出难以理解的错误。
2. **跨域 iframe（OOPIF）** 对顶层的 `Runtime.evaluate` 来说是不可见的。代理虽然能在 DOM 快照中看到 iframe 节点，但若没有为子目标建立 CDP 会话，就无法在其中进行点击、输入操作或执行代码。

该监控器通过为每个浏览器任务与后端的 CDP 接口保持持续的 WebSocket 连接，将待处理的对话框和框架结构呈现到 `browser_snapshot` 中，并提供 `browser_dialog` 工具以便进行显式响应，从而解决了上述两个问题。

## 后端支持情况

| 后端 | 对话框检测 | 对话框响应 | 框架树结构 | 通过 `browser_cdp(frame_id=...)` 执行 OOPIF 的 `Runtime.evaluate` |
|---|---|---|---|---|
| 本地 Chrome（使用 `--remote-debugging-port`）/ `/browser connect` | ✓ | ✓ 完整流程支持 | ✓ | ✓ |
| Browserbase | ✓（通过桥接实现） | ✓ 完整流程支持（通过桥接实现） | ✓ | ✓ |
| Camofox | ✗ 无 CDP 功能（仅支持 REST） | ✗ | 仅能通过 DOM 快照获取部分信息 | ✗ |

**Browserbase 的特殊之处。** Browserbase 的 CDP 代理在内部使用 Playwright，且会自动在约 10 毫秒内关闭原生对话框，因此 `Page.handleJavaScriptDialog` 无法跟上其节奏。监控器会通过 `Page.addScriptToEvaluateOnNewDocument` 注入一个桥接脚本，该脚本会将 `window.alert`/`confirm`/`prompt` 替换为向特定主机（`hermes-dialog-bridge.invalid`）发起的同步 XHR 请求。`Fetch.enable` 会在这些请求离开网络之前进行拦截——此时对话框会转化为一个 `Fetch.requestPaused` 事件，由监控器捕获，随后通过 `Fetch.fulfillRequest` 并结合注入脚本解码后的 JSON 数据来执行响应。

从页面的角度来看，`prompt()` 函数仍然会返回代理提供的字符串。而从代理的角度来看，无论哪种情况都是使用相同的 `browser_dialog(action=...)` API。

Camofox 不受支持——因为它没有 CDP 接口，仅支持 REST 协议。

## 架构设计

### CDPSupervisor

为每个 Hermes `task_id` 在后台守护线程中运行一个 `asyncio.Task`。该组件与后端的 CDP 接口保持持续的 WebSocket 连接，并维护以下数据结构：

- **对话框队列** —— 一个 `List[PendingDialog]` 列表，包含 `{id, type, message, default_prompt, session_id, opened_at}` 等字段。
- **框架树结构** —— 一个 `Dict[frame_id, FrameInfo]` 字典，记录各帧的父子关系、URL、源地址以及是否为跨域子会话。
- **会话映射表** —— 一个 `Dict[session_id, SessionInfo]` 字典，便于交互工具为 OOPIF 操作定位到正确的关联会话。
- **近期控制台错误记录** —— 最近 50 条错误的环形缓冲区，用于诊断问题。

在会话附加时，该组件会订阅以下事件：

- `Page.enable` —— `javascriptDialogOpening`、`frameAttached`、`frameNavigated`、`frameDetached`
- `Runtime.enable` —— `executionContextCreated`、`consoleAPICalled`、`exceptionThrown`
- `Target.setAutoAttach {autoAttach: true, flatten: true}` —— 用于暴露子 OOPIF 目标；监控器会为每个这样的目标启用 `Page` 和 `Runtime` 功能。

通过快照锁实现线程安全的状态访问；工具处理程序（同步模式）无需等待即可读取已冻结的快照数据。

### 生命周期

- **启动**：`SupervisorRegistry.get_or_start(task_id, cdp_url)` —— 由 `browser_navigate`、Browserbase 会话创建以及 `/browser connect` 操作触发。该操作是幂等的。
- **停止**：当会话被销毁或执行 `/browser disconnect` 操作时，该组件会取消对应的 asyncio 任务，关闭 WebSocket 连接，并丢弃所有状态数据。
- **重新绑定**：如果 CDP 地址发生变化（例如用户重新连接到另一台 Chrome 浏览器），旧的监控器会被停止，然后启动一个新的——不同端点之间的状态数据绝不会被重复使用。

### 对话框处理策略

该策略可通过 `config.yaml` 中的 `browser.dialog_policy` 配置项进行设置：

- **`must_respond`**（默认值）—— 捕获对话框，将其呈现到 `browser_snapshot` 中，然后等待用户通过 `browser_dialog(action=...)` 发出显式响应。如果在 300 秒的超时时间内仍未收到响应，系统会自动关闭对话框并记录日志。此策略可防止存在缺陷的代理无限期地挂起。
- `auto_dismiss` —— 立即记录并对对话框进行关闭；代理只能通过 `browser_snapshot` 中的 `browser_state` 信息在事后查看该对话框。
- `auto_accept` —— 立即记录并对对话框进行确认（适用于 `beforeunload` 情况，因为此时流程需要干净地跳转离开页面）。

该策略是针对每个任务而言的，不支持针对单个对话框的单独配置。

## 代理端的接口

### `browser_dialog` 工具

```
browser_dialog(action, prompt_text=None, dialog_id=None)
```

- `action="accept"` / `"dismiss"` → 用于响应指定的或唯一的待处理对话框（必需）
- `prompt_text=...` → 将要输入到 `prompt()` 对话框中的文本
- `dialog_id=...` → 当有多个对话框排队时用于区分（较少使用）

该工具仅负责返回响应。在调用相关函数之前，智能体会先从 `browser_snapshot` 输出中读取待处理的对话框内容。

### `browser_snapshot` 扩展功能

当附加了监控器时，该扩展会在现有的快照输出中添加三个可选字段：

```json
{
  "pending_dialogs": [
    {"id": "d-1", "type": "alert", "message": "Hello", "opened_at": 1650000000.0}
  ],
  "recent_dialogs": [
    {"id": "d-1", "type": "alert", "message": "...", "opened_at": 1650000000.0,
     "closed_at": 1650000000.1, "closed_by": "remote"}
  ],
  "frame_tree": {
    "top": {"frame_id": "FRAME_A", "url": "https://example.com/", "origin": "https://example.com"},
    "children": [
      {"frame_id": "FRAME_B", "url": "about:srcdoc", "is_oopif": false},
      {"frame_id": "FRAME_C", "url": "https://ads.example.net/", "is_oopif": true, "session_id": "SID_C"}
    ],
    "truncated": false
  }
}
```

- **`pending_dialogs`** — 当前正在阻塞页面 JS 线程的对话框。智能体必须调用 `browser_dialog(action=...)` 来进行响应。在 Browserbase 平台上该字段为空，因为其 CDP 代理会在约 10 毫秒内自动关闭这些对话框。

- **`recent_dialogs`** — 最近关闭的最多 20 个对话框的环形缓冲区，每个对话框都带有 `closed_by` 标签，其值可能为：`"agent"`（由智能体响应）、`"auto_policy"`（本地自动关闭/自动接受）、`"watchdog"`（因必须响应的超时而被关闭），或 `"remote"`（由浏览器/后端在智能体不知情的情况下关闭，例如在 Browserbase 平台上）。正是通过这一机制，Browserbase 上的智能体仍能了解所发生的情况。

- **`frame_tree`** — 包含跨源（OOPIF）子元素的框架结构。为控制内容繁杂的页面上的快照大小，其条目数上限为 30 个，且 OOPIF 的嵌套深度限制为 2 层。当达到上限时，该字段会显示 `truncated: true`；需要完整框架结构的智能体可以使用 `browser_cdp` 中的 `Page.getFrameTree` 方法来获取。

对于这些字段，并不会新增任何工具架构——智能体只需读取其已请求的快照即可。

### 可用性控制

上述所有接口均以 `_browser_cdp_check` 作为可用性判断条件（只有当能够访问 CDP 接口时，监管器才能运行）。在 Camofox 或无后端会话模式下，对话框相关工具会被隐藏，快照也会省略这些新字段，从而避免架构臃肿。

## 跨源 iframe 交互

`browser_cdp(frame_id=...)` 会通过监管器已建立的 WebSocket 连接，并利用 OOPIF 的子元素 `sessionId`，来转发 CDP 请求（尤其是 `Runtime.evaluate` 请求）。智能体从 `browser_snapshot.frame_tree.children[]` 中筛选出 `is_oopif=true` 的 `frame_id`，并将其传递给 `browser_cdp`。对于同源 iframe（没有专用的 CDP 会话），智能体会改用顶层 `Runtime.evaluate` 中的 `contentWindow`/`contentDocument` 方法——当 `frame_id` 不属于 OOPIF 类型时，监管器会返回错误信息，提示使用该备用方案。

在 Browserbase 平台上，这是进行 iframe 交互的唯一可靠方式——无状态的 CDP 连接（每次通过 `browser_cdp` 调用才建立）会因签名 URL 的过期而失效，而监管器的长期有效连接则能维持有效的会话状态。

## 文件结构

- `tools/browser_supervisor.py` — 包含 `CDPSupervisor`、`SupervisorRegistry`、`PendingDialog`、`FrameInfo` 等类
- `tools/browser_dialog_tool.py` — 负责处理 `browser_dialog` 工具
- `tools/browser_tool.py` — 包含 `browser_navigate` 的启动钩子、`browser_snapshot` 的合并逻辑、`/browser connect` 的重新连接功能以及 `_cleanup_browser_session` 的会话清理逻辑
- `toolsets.py` — 负责在 `browser`、`hermes-acp`、`hermes-api-server` 以及核心工具集中注册 `browser_dialog` 工具（其可用性取决于是否能访问 CDP 接口）
- `hermes_cli/config.py` — 定义了 `browser.dialog_policy` 和 `browser.dialog_timeout_s` 的默认值

## 当前未实现的功能

- Camofox 平台上的检测/交互功能（存在上游技术限制，正在单独处理）
- 将对话框/框架事件实时流式传输给用户（需要开发网关相关功能）
- 在不同会话之间持久保存对话框历史记录（目前仅支持内存存储）
- 为每个 iframe 设置独立的对话框策略（智能体可通过 `dialog_id` 来实现这一需求）
- 替代 `browser_cdp` — 由于仍有许多特殊情况（如 Cookie、视口设置、网络限速等）需要处理，`browser_cdp` 仍将是必要的备用方案

## 测试

单元测试（位于 `tests/tools/test_browser_supervisor.py`）使用基于 asyncio 的模拟 CDP 服务器，该服务器能够模拟足够的协议行为，以测试所有状态转换场景：连接建立、功能启用、页面导航、对话框触发、对话框关闭、框架附加/分离、子元素目标附加以及会话清理。而基于真实后端的端到端测试（在 Browserbase 平台及本地 Chromium 系列浏览器上进行）则需手动操作——通过 `/browser connect` 连接到实时的 Chromium 系列浏览器，然后运行上述提到的对话框/框架相关测试用例。
