---
sidebar_position: 3
title: "Built-in Tools Reference"
description: "Authoritative reference for Hermes built-in tools, grouped by toolset"
---

# 内置工具参考

本页面按工具集对Hermes的内置工具进行了说明。具体可用性会因平台、凭证以及已启用的工具集而有所不同。

**当前注册库中的工具数量：**约86种——10种浏览器工具（核心功能）+2种需CDP授权的浏览器工具，4种文件处理工具，4种Home Assistant相关工具，2种终端工具（`terminal`、`process`），12种桌面GUI工具（`read_terminal`、`close_terminal`、`open_preview`、`close_preview`、`read_preview`、`drive_preview`、`annotate_preview`、`read_window_below`、`focus_pane`、`react_to_message`、`tour`、`tip`——仅适用于桌面应用会话），2种网络工具，5种飞书相关工具，7种Spotify相关工具（由内置的`spotify`插件注册），5种元宝相关工具，12种看板工具（在看板调度器启动代理时自动注册），3种项目管理工具（适用于桌面/GUI会话），2种Discord相关工具，3种视频处理工具（`video_generate`、`xai_video_edit`、`xai_video_extend`），以及少量独立工具（`memory`、`clarify`、`delegate_task`、`execute_code`、`cronjob`、`session_search`、`skill_view`/`skill_manage`/`skills_list`、`text_to_speech`、`image_generate`、`vision_analyze`、`video_analyze`、`todo`、`computer_use`、`x_search`）。

:::提示 MCP工具
除了内置工具外，Hermes还可以从MCP服务器动态加载工具。这类工具的前缀为`mcp__<server>__`（例如，`github` MCP服务器对应的工具为`mcp__github__create_issue`）。有关配置方法，请参阅[MCP集成指南](/user-guide/features/mcp)。
:::

## `browser`工具集

| Tool | Description | Requires environment |
|------|-------------|----------------------|
| `browser_back` | Navigate back to the previous page in browser history. Requires browser_navigate to be called first. | — |
| `browser_click` | Click on an element identified by its ref ID from the snapshot (e.g., '@e5'). The ref IDs are shown in square brackets in the snapshot output. Requires browser_navigate and browser_snapshot to be called first. | — |
| `browser_console` | Get browser console output and JavaScript errors from the current page. Returns console.log/warn/error/info messages and uncaught JS exceptions. Use this to detect silent JavaScript errors, failed API calls, and application warnings. Requi… | — |
| `browser_get_images` | Get a list of all images on the current page with their URLs and alt text. Useful for finding images to analyze with the vision tool. Requires browser_navigate to be called first. | — |
| `browser_navigate` | Navigate to a URL in the browser. Initializes the session and loads the page. Must be called before other browser tools. For simple information retrieval, prefer web_search or web_extract (faster, cheaper). Use browser tools when you need… | — |
| `browser_press` | Press a keyboard key. Useful for submitting forms (Enter), navigating (Tab), or keyboard shortcuts. Requires browser_navigate to be called first. | — |
| `browser_scroll` | Scroll the page in a direction. Use this to reveal more content that may be below or above the current viewport. Requires browser_navigate to be called first. | — |
| `browser_snapshot` | Get a text-based snapshot of the current page's accessibility tree. Returns interactive elements with ref IDs (like @e1, @e2) for browser_click and browser_type. full=false (default): compact view with interactive elements. full=true: comp… | — |
| `browser_type` | Type text into an input field identified by its ref ID. Clears the field first, then types the new text. Requires browser_navigate and browser_snapshot to be called first. | — |
| `browser_vision` | Take a screenshot of the current page so you can inspect it visually. Use this when you need to understand what the page looks like — especially for CAPTCHAs, visual verification challenges, complex layouts, or cases where the text snapshot misses important visual information. On native-vision models the screenshot is attached directly; otherwise falls back to an auxiliary vision mo… | — |

## `browser` 工具集（需 CDP 支持的工具）

这两个工具属于 `browser` 工具集，但仅在会话开始时能够通过 `/browser connect`、`browser.cdp_url` 配置、Browserbase 会话或 Camofox 访问 Chrome DevTools Protocol 端点时才会被激活。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `browser_cdp` | 发送原始的 Chrome DevTools Protocol 命令。用于处理那些未被更高层级的 `browser_*` 工具覆盖的浏览器操作。详情请参阅 https://chromedevtools.github.io/devtools-protocol/ | CDP 端点 |
| `browser_dialog` | 响应原生 JavaScript 对话框（如 alert / confirm / prompt / beforeunload）。首先需调用 `browser_snapshot`——待处理的对话框会显示在其 `pending_dialogs` 字段中，之后再调用 `browser_dialog(action='accept'\|'dismiss')`。 | CDP 端点 |

## `clarify` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `clarify` | 在需要进一步澄清、反馈或决策后再继续操作时，向用户提出问题。支持三种模式：<br>1. **单选多项选择** — 最多提供4个选项；用户可选择其中一个，或通过第5个“其他”选项输入自定义答案。<br>2. **多选多项选择** — 设置`multi_select=true`后会显示复选框，并返回已选选项的列表。<br>3. **开放式回答** — 无预设选项；用户可自由输入回复。选项会按优选顺序排列，因此第一个选项在所有界面都会标记为`(推荐)`并默认高亮显示；该标签仅用于展示，Agent读取答案时不会包含它。在传统CLI界面中，使用空格键切换复选框状态；在没有原生复选框界面的消息平台中，用户需用逗号/空格分隔的数字（如“1, 3”）或选项文本进行回复。 | — |

### 同时提出多个问题

`clarify`工具还支持接收`questions`数组（包含2–5个独立问题，每个问题都有自己的`choices`和`multi_select`设置），这样Agent就可以将多项澄清需求整合到单个提示中，而无需依次提问。返回结果为按相同顺序排列的`responses`数组，同时会原样返回每个问题的`id`（如有提供）。

不同界面的行为表现：

- **桌面端**会将所有问题显示在一张卡片上。用户可在本地逐题选择答案并输入，待所有题目都得到回答后，会出现一个“确认并继续”按钮，点击即可提交全部答案。在这些答案被确认之前，用户仍可对其进行修改；而“跳过”按钮则会取消整个提交流程。
- **文本用户界面与命令行界面**会以简洁的状态列表形式展示问题（`✓` 已回答 / `▸` 正在处理 / `·` 待处理），仅展开当前正在处理的题目选项。输入键可锁定当前答案并跳至下一个未回答的题目；Tab键可用于按任意顺序切换题目进行回答；Esc键则可取消整个提交流程。
- **消息平台**（如 Telegram、Discord 等）会退而采用传统的单题提问方式依次询问问题。如果用户停止回复，后续的问题将不会被发送。

若提问过程在半途超时，用户已锁定的答案将会保留：工具结果中会包含这些答案以及 `"timed_out": true` 的标识，未回答的题目则保持空白，这样智能体就能区分是用户故意跳过还是因未在线而无法回复。

## `code_execution` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `execute_code` | 运行能够以编程方式调用 Hermes 工具的 Python 脚本。当您需要执行 3 次及以上工具调用，并且需要在这些调用之间加入处理逻辑，或在答案进入上下文之前对其进行过滤/简化，或需要实现条件分支时，可使用此工具。| — |

## `cronjob` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `cronjob` | 统一的定时任务管理工具。可通过 `action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"` 或 `"remove"` 等指令来管理任务。它支持基于技能的任务处理，即一个任务可关联一个或多个技能；在执行更新操作时若设置 `skills=[]`，则可清除所有关联的技能。Cron 任务的执行会在全新的会话中完成，不会保留当前对话的上下文。 | — |

## `delegation` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `delegate_task` | 在独立的上下文中创建子智能体；每个子智能体拥有独立的对话界面、终端会话及工具集，最终仅会将处理结果汇总后返回给您。可指定单个任务的 ‘goal’，或为批量任务指定 ‘tasks’（包含数量限制与嵌套规则等）… | — |

## `feishu_doc` 工具集

该工具集专用于 Feishu 文档/评论智能回复处理模块（`gateway/platforms/feishu_comment.py`），并未在 `hermes-cli` 或常规的 Feishu 聊天适配器中提供。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `feishu_doc_read` | 根据文件类型与访问令牌，读取 Feishu/Lark 文档（Docx、Doc 或 Sheet 格式）的完整文本内容。 | Feishu 应用凭证 |

## `feishu_drive` 工具集

该工具集同样专用于 Feishu 文档/评论处理模块，用于实现对驱动器中文件的评论读写操作。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `feishu_drive_add_comment` | 在飞书/企微的文档或文件上添加顶层评论。 | 飞书应用凭证 |
| `feishu_drive_list_comments` | 按最新顺序列出飞书/企微文件中的全部文档评论。 | 飞书应用凭证 |
| `feishu_drive_list_comment_replies` | 列出特定飞书评论主题下的回复内容（支持整个文档或局部选中区域）。 | 飞书应用凭证 |
| `feishu_drive_reply_comment` | 在飞书评论主题下发布回复，可选择性添加@提及。 | 飞书应用凭证 |

## `file` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `patch` | 对文件进行精准的查找并替换编辑。可在终端中替代 sed/awk 使用。采用模糊匹配技术（支持9种策略），因此细微的空白或缩进差异不会影响其正常运行。会返回统一格式的差异对比结果。编辑完成后会自动执行语法检查…… | — |
| `read_file` | 以带行号且可分页的方式读取文本文件。可在终端中替代 cat/head/tail 使用。输出格式为“行号\|内容”。若未找到目标文件，会推荐相似名称的文件。处理大文件时可使用偏移量和限制值。长度超过约10万字符的文件会在行边界处被截断，并返回下一个可读取的偏移量。支持读取 Jupyter 笔记本（.ipynb）、Word 文档（.docx）以及 Excel 工作簿（.xlsx）等格式…… | — |
| `search_files` | 搜索文件内容或按名称查找文件。可在终端中替代 grep/rg/find/ls 使用。基于 Ripgrep 技术，速度优于终端中的同类命令。支持内容搜索（目标选项为‘content’）：可在文件内部进行正则表达式搜索。输出模式包括包含完整匹配内容的行…… | — |
| `write_file` | 将内容写入文件，完全替换原有内容。可在终端中替代 echo/cat heredoc 使用。会自动创建所需的父目录。该工具会直接覆盖整个文件——如需精准编辑，请使用 `patch` 工具。对于 .py/.json/.yaml/.toml 等需要代码检查的语言，会自动执行语法检查；仅会显示此次写入操作引入的新错误。 | — |

## `homeassistant` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `ha_call_service` | 调用 Home Assistant 的服务以控制设备。可使用 `ha_list_services` 查看各领域中可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个 Home Assistant 实体的详细状态，包括所有属性（亮度、颜色、温度设定值、传感器读数等）。 | — |
| `ha_list_entities` | 列出 Home Assistant 中的所有实体。可选择按领域（灯光、开关、温控、传感器、二进制传感器、遮光装置、风扇等）或区域名称（客厅、厨房、卧室等）进行筛选。 | — |
| `ha_list_services` | 列出用于设备控制的可用 Home Assistant 服务（操作）。显示每种设备类型可执行的操作及其接受的参数。可通过此工具了解如何控制通过 `ha_list_entities` 找到的设备。 | — |

## `computer_use` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `computer_use` | 通过 cua-driver 实现后台桌面控制——支持截图（SOM / vision / AX）、点击/拖动/滚动/输入/按键/等待操作，以及列出应用、聚焦应用等功能。不会窃取用户的光标或键盘焦点。适用于所有具备工具功能的型号，支持 macOS、Windows 和 Linux 系统。 | `$PATH` 路径下已安装 `cua-driver`（可通过 `hermes tools` 安装）。 |


:::note
**Honcho 工具**（`honcho_profile`、`honcho_search`、`honcho_context`、`honcho_reasoning`、`honcho_conclude`）已不再作为内置功能提供。这些工具可通过位于 `plugins/memory/honcho/` 的 Honcho 内存提供者插件来使用。有关安装与使用方法，请参阅 [内存提供者](../user-guide/features/memory-providers.md)。
:::

## `image_gen` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `image_generate` | 根据文本提示生成图像（文本转图像），或通过用户配置的后端服务（FAL.ai、OpenAI、OpenAI Codex 认证、xAI、Krea）对现有图像进行编辑或转换。如需编辑图像，请传入 `image_url`；如需参考风格，则传入 `reference_image_urls`；进行文本转图像时则无需传入这两项参数。模型由用户自行配置，代理无法选择。该工具会返回一个图像的 URL 或本地路径。 | FAL_KEY / OPENAI_API_KEY / Codex OAuth / xAI OAuth / KREA_API_KEY |

## `kanban` 工具集

当代理由以下任一方式启动时，该工具集会被自动注册：(a) 通过看板调度器生成（设置了 `HERMES_KANBAN_TASK` 环境变量）；或 (b) 在明确启用了 `kanban` 工具集的配置文件中运行。针对特定任务的工作者会使用与该任务相关的生命周期工具；而协调者配置文件则还会拥有诸如 `kanban_list` 和 `kanban_unblock` 这样的看板路由工具。有关完整的工作流程，请参阅 [Kanban 多代理系统](/user-guide/features/kanban)。

| Tool | Description | Requires environment |
|------|-------------|----------------------|
| `kanban_show` | Show the active kanban task assigned to this worker (title, description, comments, dependencies). | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_list` | List board tasks with filters. Orchestrator-only; hidden from dispatcher-spawned task workers. | profile with `kanban` toolset |
| `kanban_complete` | Mark the current task done with a structured handoff payload (results, artifacts, follow-ups). | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_block` | Block the current task on a question for the user — the dispatcher pauses, surfaces the question, and resumes once a human replies. | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_request_review` | Hand the implementation to a reviewer with `summary`, optional structured `metadata`, and an optional reviewer profile. Moves the same task to `review`; it is not a block and does not affect block-loop accounting. | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_request_changes` | Reviewer verdict for an actively claimed review run. Closes the review run, reapplies parent gating, and routes the task back to the original implementer without using a block. | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_heartbeat` | Send a progress heartbeat during a long-running operation so the dispatcher knows the worker is still alive. | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_comment` | Add a comment to the task thread without changing its state — useful for surfacing intermediate findings. | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_create` | Fan out child tasks from the current task. Used by orchestrators and follow-up-spawning workers. | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_link` | Link tasks with a parent → child dependency edge. | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_unblock` | Move a blocked task to `ready` when all parents are done, or `todo` while any parent remains open. Orchestrator-only; hidden from dispatcher-spawned task workers. | profile with `kanban` toolset |
| `kanban_attach` | Attach a file to a task by passing its bytes inline (base64). Stored as a real attachment under the task's attachments dir, capped at 25 MB. | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_attach_url` | Attach a file to a task by URL — Hermes downloads it server-side and stores it as a real attachment (capped at 25 MB). Only http/https URLs. | `HERMES_KANBAN_TASK` or `kanban` toolset |
| `kanban_attachments` | List the files attached to a task: id, filename, content_type, size, uploader, and the absolute on-disk path. | `HERMES_KANBAN_TASK` or `kanban` toolset |

## `project` 工具集

用于管理桌面端[项目](../user-guide/cli.md)——即带有名称的多文件夹工作空间。当启用 `project` 工具集时（主要在桌面应用/控制台界面中）即可使用这些工具。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `project_create` | 创建一个桌面端项目（即带名称的工作空间），并将当前聊天窗口切换至该项目。可通过传递 `path` 参数将项目绑定到特定的代码库或文件夹。 | — |
| `project_list` | 列出所有桌面端项目以及当前处于活动状态的项目。 | — |
| `project_switch` | 根据项目名称、唯一标识符或编号将当前聊天窗口切换至现有项目；同时会将会话工作空间移至该项目的主文件夹中。 | — |

## `memory` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `memory` | 将重要信息保存到会话之间依然存在的持久内存中。在每次会话开始时，这些存储的信息会显示在系统提示语中——借此可以在不同对话之间记住有关用户及当前环境的信息。何时使用该工具…… | — |

## `session_search` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `session_search` | 搜索存储在本地会话数据库中的历史会话，或在这些会话内容中进行滚动查看。该功能基于 FTS5 技术实现检索，直接从数据库中返回实际消息内容（无需调用大型语言模型）。提供四种使用方式：探索模式（传递 `query` 参数）、滚动模式（传递 `session_id` 和 `around_message_id` 参数）、阅读模式（仅传递 `session_id` 参数）、浏览模式（无需传递任何参数）。 | — |

## `skills` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能相当于你的程序化记忆——用于处理重复性任务的可用方案。新创建的技能会存储在 ~/.hermes/skills/ 目录下；现有技能则可修改其所在位置的任意文件。操作包括：创建（完整的 SKILL.m… | — |
| `skill_view` | 技能可用于加载特定任务及工作流的相关信息，以及脚本和模板。可以加载技能的完整内容，或访问其关联的文件（引用、模板、脚本等）。首次调用会返回 SKILL.md 的内容以及更多信息… | — |
| `skills_list` | 列出所有可用技能（名称+描述）。可使用 skill_view(name) 命令来加载完整的技能内容。 | — |

## `terminal` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `process` | 管理通过 terminal(background=true) 启动的后台进程。支持的操作包括：'list'（显示所有进程）、'poll'（检查状态及新输出）、'log'（分页显示完整输出）、'wait'（阻塞等待进程完成或超时）、'kill'（终止进程）、'write'（向进程写入数据）… | — |
| `terminal` | 在 Linux 环境中执行 shell 命令。每次调用之间文件系统状态会保持不变。对于需要长时间运行的服务器，可设置 `background=true`。若同时设置 `notify_on_complete=true`（配合 `background=true` 使用），则进程完成后会自动发送通知——无需手动轮询。请勿使用 cat/head/tail 命令，应改用 read_file；也请勿使用 grep/rg/find 命令，应改用 search_files。 | — |

## `desktop_ui` 工具集

对于源自 Hermes 桌面应用程序的会话，无论其连接的是哪种后端（本地、SSH、URL 或 Hermes Cloud），该功能均支持启用。但在 CLI、TUI、消息传递以及 cron 会话中则不可用。

| Tool | Description | Requires environment |
|------|-------------|----------------------|
| `read_terminal` | Read what's currently shown in the in-app terminal pane of the Hermes desktop GUI (the embedded shell beside this chat). | — |
| `close_terminal` | Close the read-only terminal tab for a background process in the Hermes desktop GUI. Does NOT kill the process — only drops the tab/view; use process(action='kill') to stop it. | — |
| `open_preview` | Open a web URL, localhost dev-server URL, or file path in the preview pane beside the chat in the Hermes desktop app. | — |
| `close_preview` | Close the preview pane beside the chat, or one tab inside it. Omit `url` to close the whole pane; pass a URL or file path to close that tab. | — |
| `read_preview` | Read what's currently shown in the preview pane of the Hermes desktop GUI — the in-app Browser's page text (URL + title + rendered text, pageable with `start`/`count`), or a file/artifact tab's identity. | — |
| `drive_preview` | Interact with the page open in the in-app browser: `elements` inventories what's clickable and typable (each with a ref that names it, like `btn-sign-in` or `inp-email`, plus role, label, and value), then `click`, `hover`, `type`, `scroll`, and `press` act on a ref, and `back`/`forward`/`reload` drive the pane's history. The pointer and keyboard are real input, so hover menus open. A ref lasts until the page navigates, including across a re-render that rebuilds the element, so after the first inventory every action answers with just a delta — what was added, removed, changed, or rebound — instead of the whole page again. | — |
| `annotate_preview` | Outline an element in the in-app browser and leave the mark up until it's removed — the deliberate counterpart to the transient cues `drive_preview` draws as it works. `add` marks a ref with an optional short label, `remove` takes one down, `clear` takes them all. Marks follow their element and vanish with it, so a navigation clears them. | — |
| `read_window_below` | Identify the OS window directly underneath the Hermes desktop window — app name, title, bounds (metadata only, never pixels). On macOS, other apps' titles appear only when Screen Recording is already granted; the tool never prompts for it. | — |
| `focus_pane` | Reveal and focus a pane in the Hermes desktop app (chat, files, terminal, review, sessions). | — |
| `react_to_message` | React to a message with a single emoji, iMessage-tapback style. Opt-in via Settings → Appearance (`display.message_reactions`). | — |
| `tour` | Give a live guided tour: dim the screen, highlight an element, and attach a narrated popover (driver.js). Works on the Hermes app's own UI and on any page open in the preview pane; `targets` discovers what's on screen, `show` narrates step-by-step, `start` hands the user Next/Prev controls. | — |
| `tip` | Point at one element with a small accent bubble and an arrow — the quiet sibling of `tour`, with no dimming, no spotlight, and no Next/Prev. Same `data-tour` handles and the same `tour(action='targets')` discovery call. | — |

### 导览功能

`tour` 工具能够自动识别目标元素——只需调用 `action='targets'`，它就会返回屏幕上所有可定位的元素，并附带选择器、标签以及 `stable` 标志。稳定的选择器基于元素的唯一标识（如 `data-tour`、`id`、`data-testid`、`aria-label`）生成，且在页面重新渲染后依然有效；而基于位置的选择器 `nth-child` 则不具备此特性，因此应优先使用稳定的选择器。

若想为某个元素创建一个持久且专属的标识，可通过以下方式对其进行标记：

```html
<div data-tour="composer">…</div>
```

处理标识是应用在**基础元素**层面，而非调用位置，因此只需进行一次修改即可为所有实例命名。现有的处理标识如下：

| 处理标识 | 所对应的对象 |
|---|---|
| `overlay-nav` | 任意路由覆盖页面的左侧导航栏（包括设置、定时任务、配置文件、代理等） |
| `nav-<id>` | 该导航栏中的某一行——如 `nav-models`、`nav-appearance` 等 |
| `field-<schemaKey>` | 根据配置键确定的某一行设置项——如 `field-model`、`field-provider` 等 |
| `page-tabs` | 任意 `PageSearchShell` 页面上的筛选标签页（用于管理成果物、技能等） |
| `artifact-card` | 网格布局中的单个成果物卡片 |

在添加新界面时，应采用相同方式为对应的基础元素添加标签，而非逐个为屏幕添加标签——这样既能保持导览词汇表的简洁性，还能避免选择器失效。

桌面应用中经过精心设计的（非代理型）导览也基于同一引擎实现，因此各类功能都可以自行生成对应的操作指引：

```ts
import { startTour, showTourStep, stopTour } from '@/lib/tour'

startTour([
  { selector: '[data-tour="composer"]', title: 'Composer', text: 'Type here.' },
  { selector: '[data-tour="files"]', title: 'Files', text: 'Browse your project.' }
])
```

某一步骤也可以将应用移动到目标所在的位置，而导览在结束后会将相关内容恢复原位：

```ts
startTour([
  { navigate: '/artifacts', selector: '[data-tour="page-tabs"]', title: 'Filters', text: '…' },
  { pane: 'sessions', selector: '[data-slot="sidebar"]', title: 'Sessions', text: '…' }
])
```

`navigate`函数接受路径字符串，而`pane`函数则接收桌面分面名称。在输入对应指令后，系统会立即执行操作，同时等待那些稍后才加载的目标元素；无论通过何种方式——包括按下Esc键——终止导览流程，都会返回到起始点。

若将第二个参数设置为`'preview'`，则会在预览分面中的页面而非实际应用中执行该操作。

### 提示功能

提示功能指的是简化版的导览步骤：仅包含一个信息框和一个箭头，没有背景遮罩，也不需要逐页切换。这种形式非常适合用于那些需要直接点明对象的句子——比如“模型名称位于某个按钮上”——而无需通过暗化整个应用来实现。

`tip`工具使用的选择器与`tour(action='targets')`功能相同，因此两种功能只需一次调用即可完成目标定位；此外，持久化的`data-tour`机制还能为两者统一管理目标元素。屏幕上同一时间仅显示一个提示，新的提示会替换掉旧的那个。

该应用还可以自行展示内置的功能介绍，按照特定顺序依次呈现，其呈现方式更类似于游戏加载界面中的提示，而非普通通知：最早在应用启动几分钟后出现，之后最多每六小时出现一次，且仅在应用真正处于空闲状态时显示。Hermes的提示功能也会遵循同样的间隔规则，从而让用户免受频繁提示的干扰，享受六小时的安静使用时间。通过点击✕按钮关闭某个提示后，该提示将永久消失，而设置栏则可重新启用这些提示。

提示和引导功能默认处于开启状态，可在“设置 → 外观”中关闭（对应参数为`display.in_app_tips`和`display.in_app_tours`）。关闭该功能会影响Hermes本身以及应用程序：此设置会同步到连接的网关配置中，同时工具也会脱离模型的架构定义，因此智能体永远不会被告知存在其未被允许使用的功能界面。与所有架构变更一样，这一更改会在下一个会话中生效——正在进行的对话会保留初始使用的工具集，而在此期间应用程序会拒绝接收新通话。

## `todo` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `todo` | 管理当前会话的任务列表。适用于包含3个以上步骤的复杂任务，或用户同时提交多个任务的情况。不带参数调用即可查看当前任务列表。任务项可嵌套：某个任务项可选的`parent`字段可指向另一个任务项的ID，从而将其设为子任务——界面会以缩进形式展示该任务树结构。 | — |

## `vision` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `vision_analyze` | 利用人工智能视觉功能分析图像。在具备视觉处理能力的主模型上，该工具会将原始图像像素作为多模态结果返回，以便模型在下一轮处理时直接使用这些像素数据。在仅支持文本处理的主模型上，则会回退到辅助的视觉模型来描述图像，并以文本形式返回描述内容。两种情况下的工具接口定义保持一致。 | — |

## `video` 工具集

可选工具集（默认的 `hermes-cli` 集合中不包含该工具集）。可通过 `--toolsets video` 参数添加，或是在 `toolsets:` 配置中直接列出 `video`。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `video_analyze` | 分析来自 URL 或文件路径的视频内容——包括字幕、场景拆分、关键时间戳以及视觉描述。 | — |

## `video_gen` 工具集

可选工具集（默认的 `hermes-cli` 集合中不包含该工具集）。可通过 `--toolsets video_gen` 参数添加，或是在 `hermes tools` → Video Generation 中启用该功能，该界面还会指导用户选择后端服务。

各类后端服务均以插件形式存在于 `plugins/video_gen/<name>/` 目录下：

- **xAI Grok-Imagine** — 文本转视频及图像转视频功能（需使用 SuperGrok OAuth 或 `XAI_API_KEY`）。
- **FAL.ai** — Veo 3.1、Pixverse v6、Kling O3（需提供 `FAL_KEY`）。

单个 `video_generate` 工具即可支持这两种转换模式：若传入 `image_url` 则可对静态图像进行动画处理，若不传入该参数则可直接根据文本生成视频。系统会自动将请求路由至当前启用的后端接口。该工具的描述会在会话启动时重新生成，以反映当前后端的实际功能特性（支持的模式、宽高比、分辨率、时长范围、最大参考图片数量以及音频支持情况）。如需自行开发后端服务，请参阅 [视频生成提供方插件指南](/developer-guide/video-gen-provider-plugin)。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `video_generate` | 使用用户配置的视频生成后端，根据文本提示生成视频（文本转视频），或为静态图片添加动画效果（图片转视频）。如需为图片添加动画，请传入 `image_url`；仅根据文本生成时则无需该参数。后端会自动选择对应的接口地址。该工具会在 `video` 字段中返回 HTTP URL 或绝对文件路径。 | 已激活的 `video_gen` 插件及其凭证（如 `XAI_API_KEY`、`FAL_KEY`） |
| `xai_video_edit` | 使用 xAI Imagine 对现有视频进行编辑。此功能为特定提供商提供（与 `video_generate` 独立）。`video_url` 必须是之前通过 Imagine 生成后的公开 HTTPS MP4 链接。 | xAI Imagine 凭证（SuperGrok OAuth 或 `XAI_API_KEY`） |
| `xai_video_extend` | 使用 xAI Imagine 对现有视频进行扩展。此功能为特定提供商提供（与 `video_generate` 独立）。`video_url` 必须是之前通过 Imagine 生成后的公开 HTTPS MP4 链接。 | xAI Imagine 凭证（SuperGrok OAuth 或 `XAI_API_KEY`） |

## `web` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `web_search` | 在网络上搜索信息。默认返回最多5条结果，包含标题、URL及描述。可可选设置`limit`参数（范围1-100，默认为5）。查询内容会传递给已配置的后端，因此只要后端支持，诸如`site:domain`、`filetype:pdf`、`intitle:word`、`-term`以及`"exact phrase"`之类的搜索操作符即可使用。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY 或 PERPLEXITY_API_KEY 或 KEENABLE_API_KEY |
| `web_extract` | 从网页URL中提取内容。以markdown或文本格式返回纯净的页面内容（无需LLM总结，速度更快）。同时也支持PDF URL（如arxiv论文、文档）——可直接传入PDF链接。在字符限制范围内（默认15000字符）的页面会完整返回内容；对于较长的页面，则会返回开头和结尾的部分内容，并附上指向磁盘上完整文本的链接。每次调用最多支持5个URL。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY 或 PERPLEXITY_API_KEY 或 KEENABLE_API_KEY |

## `x_search` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `x_search` | 使用 xAI 内置的 `x_search` Responses 工具来搜索 X（Twitter）上的帖子、个人主页及话题串。仅能读取公开内容，用于查看当前在 X 上的讨论、点赞反馈或相关声明（不包括普通网页内容）。该工具无法发布内容、回复消息、点赞、发送私信、上传媒体文件、删除内容，也无法查看已认证的 X 账户信息——这些操作需要通过独立的已认证 X API 接口实现（例如 `xurl` 工具）。默认处于关闭状态，可通过 `hermes tools` → 🐦 X（Twitter）搜索来启用。仅当配置了 xAI 凭据时才会注册该接口（受 check_fn 限制）。 | XAI_API_KEY **或** xAI Grok OAuth 登录（SuperGrok / Premium+ 计划用户） |

## `tts` 工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `text_to_speech` | 将文本转换为语音音频。该工具会返回一个 MEDIA: 路径，平台会通过该路径将语音消息发送出去。在 Telegram 中，语音消息会以语音气泡形式呈现；在 Discord/WhatsApp 中则作为音频附件发送。在 CLI 模式下，语音文件会被保存到 ~/voice-memos/ 目录中。涉及语音处理及相关服务提供商…… | — |

## `discord` 工具集

该工具集已注册在 `hermes-discord` 平台工具集中（仅支持网关模式）。其使用的机器人令牌与消息传递适配器相同。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `discord` | 用于读取 Discord 服务器的内容并参与其中。可执行的操作包括 `search_members`、`fetch_messages`、`send_message`、`react`、`fetch_channel`、`list_channels` 等。 | `DISCORD_BOT_TOKEN` |
## `discord_admin` 工具集

该工具集已注册在 `hermes-discord` 平台工具集中。执行管理操作时，机器人需拥有相应的 Discord 权限。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord_admin` | 通过 REST API 管理 Discord 服务器：列出服务器/频道/角色，创建、编辑或删除频道，管理角色权限、超时设置、踢出用户及封禁操作。 | `DISCORD_BOT_TOKEN` + 机器人权限 |

## `spotify` 工具集

该工具集由内置的 `spotify` 插件提供。使用时需要 OAuth 令牌——请先运行 `hermes auth spotify` 进行授权。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `spotify_playback` | 控制 Spotify 播放，查看当前播放状态，或获取最近播放过的曲目。 | Spotify OAuth |
| `spotify_devices` | 列出 Spotify Connect 设备，或将播放内容切换到其他设备。 | Spotify OAuth |
| `spotify_queue` | 查看用户的 Spotify 播放队列，或向其中添加曲目。 | Spotify OAuth |
| `spotify_search` | 在 Spotify 目录中搜索曲目、专辑、艺术家、播放列表、节目或剧集。 | Spotify OAuth |
| `spotify_playlists` | 列出、查看、创建、更新及修改 Spotify 播放列表。 | Spotify OAuth |
| `spotify_albums` | 获取 Spotify 专辑的元数据或专辑曲目信息。 | Spotify OAuth |
| `spotify_library` | 列出、保存或删除用户已保存的 Spotify 曲目或专辑。 | Spotify OAuth |

## `hermes-yuanbao` 工具集

这些工具仅可在 `hermes-yuanbao` 平台工具集中注册使用。Yuanbao 是腾讯推出的聊天应用，而这些工具则用于驱动该应用的私信、群组及贴图相关 API。

| 工具名称 | 功能描述 | 所需环境 |
|----------|----------|----------|
| `yb_query_group_info` | 查询群组的基本信息（在应用中称为“派/Pai”）：群名、群主以及成员数量。 | Yuanbao 认证凭证 |
| `yb_query_group_members` | 查询群组内的成员信息（用于 `@` 提及用户、按名称查找用户以及列出机器人）。 | Yuanbao 认证凭证 |
| `yb_send_dm` | 向群组中的用户发送私信/直接消息，可可选地附上媒体文件。 | Yuanbao 认证凭证 |
| `yb_search_sticker` | 根据关键词搜索内置的 Yuanbao 贴图（TIM 表情）库。 | Yuanbao 认证凭证 |
| `yb_send_sticker` | 向当前的 Yuanbao 聊天窗口发送内置贴图。 | Yuanbao 认证凭证 |


