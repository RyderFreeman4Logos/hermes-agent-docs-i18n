---
sidebar_position: 3
title: "Built-in Tools Reference"
description: "Authoritative reference for Hermes built-in tools, grouped by toolset"
---

# 内置工具参考

本页面按工具集对Hermes的内置工具进行了文档说明。实际可用工具会因平台、凭证以及已启用的工具集而有所不同。

**当前注册工具总数：**约71种——其中10种浏览器工具（核心功能）+2种需通过CDP授权的浏览器工具，4种文件处理工具，4种Home Assistant相关工具，2种终端工具，2种网页工具，5种飞书工具，7种Spotify工具（由内置的`spotify`插件注册），5种元宝工具，9种看板工具（在看板调度器启动代理时自动注册），2种Discord工具，以及少量独立工具（`memory`、`clarify`、`delegate_task`、`execute_code`、`cronjob`、`session_search`、`skill_view`/`skill_manage`/`skills_list`、`text_to_speech`、`image_generate`、`video_generate`、`vision_analyze`、`video_analyze`、`send_message`、`todo`、`computer_use`、`process`）。

:::提示 MCP工具
除了内置工具外，Hermes还能从MCP服务器动态加载工具。这类工具的前缀为`mcp_<server>_`（例如针对`github` MCP服务器的`mcp_github_create_issue`）。相关配置方法请参阅[MCP集成](/user-guide/features/mcp)。
:::

## `browser`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `browser_back` | 在浏览器历史记录中返回上一页。需先调用`browser_navigate`。 | — |
| `browser_click` | 点击快照中通过ref ID标识的元素（例如`@e5`）。这些ref ID会以方括号形式显示在快照输出中。需先调用`browser_navigate`和`browser_snapshot`。 | — |
| `browser_console` | 获取当前页面的浏览器控制台输出及JavaScript错误信息。会返回`console.log/warn/error/info`消息以及未被捕获的JS异常。可用于检测隐性的JavaScript错误、失败的API调用以及应用程序警告。需先… | — |
| `browser_get_images` | 获取当前页面上所有图片的列表，包括其URL和替代文本。有助于找出需要用视觉分析工具处理的图片。需先调用`browser_navigate`。 | — |
| `browser_navigate` | 在浏览器中导航至指定URL。该操作会初始化会话并加载页面。必须在其他浏览器工具之前调用。对于简单的信息检索，建议使用`web_search`或`web_extract`（速度更快、成本更低）。仅在需要…时才使用浏览器工具。 | — |
| `browser_press` | 按下键盘上的某个键。可用于提交表单（回车键）、导航（Tab键）或使用快捷键。需先调用`browser_navigate`。 | — |
| `browser_scroll` | 按指定方向滚动页面。可用于查看当前视口下方或上方的更多内容。需先调用`browser_navigate`。 | — |
| `browser_snapshot` | 获取当前页面无障碍访问结构的文本格式快照。会返回带有ref ID的交互元素（如`@e1`、`@e2`），以便后续使用`browser_click`和`browser_type`功能。`full=false`（默认值）：显示包含交互元素的简洁视图；`full=true`：显示完整视图… | — |
| `browser_type` | 在通过ref ID标识的输入框中输入文本。首先会清空该字段，然后再输入新内容。需先调用`browser_navigate`和`browser_snapshot`。 | — |
| `browser_vision` | 对当前页面进行截图，并利用视觉AI对其进行分析。当需要直观了解页面内容时非常有用——尤其适用于验证码、视觉验证任务、复杂布局，或文本无法准确识别等情况。 | — |

## `browser`工具集（CDP授权工具）

这两个工具属于`browser`工具集，但仅在会话启动时能够通过 `/browser connect`、`browser.cdp_url`配置、Browserbase会话或Camofox访问到Chrome DevTools Protocol端点时才会被注册。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `browser_cdp` | 发送原始的Chrome DevTools Protocol命令。作为高级`browser_*`工具未覆盖的浏览器操作时的备用方案。详情请参阅https://chromedevtools.github.io/devtools-protocol/ | CDP端点 |
| `browser_dialog` | 对原生JavaScript对话框（alert / confirm / prompt / beforeunload）作出响应。需先调用`browser_snapshot`——待处理的对话框会显示在其`pending_dialogs`字段中。之后再调用`browser_dialog(action='accept'\|'dismiss')`。 | CDP端点 |

## `clarify`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `clarify` | 在需要进一步澄清、获取反馈或做出决策后再继续执行任务时，向用户提出问题。支持两种模式：1. **多项选择**——最多提供4个选项。用户可选择其中一个选项，或通过第5个“其他”选项输入自定义答案。2.… | — |

## `code_execution`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `execute_code` | 运行能够以编程方式调用Hermes工具的Python脚本。当需要在多次工具调用之间添加处理逻辑、在内容进入上下文之前对其进行过滤/简化，或实现条件分支功能时，可使用此工具。… | — |

## `cronjob`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `cronjob` | 统一的定时任务管理器。可通过`action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"`或`"remove"`来管理任务。支持由一个或多个附加技能支持的技能型任务，若在更新时设置`skills=[]`则可清除所有附加技能。定时任务会在没有当前聊天上下文的新的会话中执行。 | — |

## `delegation`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `delegate_task` | 启动一个或多个子代理，在独立的上下文中处理任务。每个子代理都有属于自己的对话界面、终端会话和工具集。最终只会返回汇总结果——中间阶段的工具处理结果不会进入你的上下文窗口。有两种… | — |

## `feishu_doc`工具集

该工具集专用于飞书文档评论智能回复处理模块（`gateway/platforms/feishu_comment.py`）。在`hermes-cli`或常规飞书聊天适配器中不可用。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `feishu_doc_read` | 根据文件类型和令牌，读取飞书/企业微信文档（Docx、Doc或Sheet格式）的完整文本内容。 | 飞书应用凭证 |

## `feishu_drive`工具集

该工具集也专用于飞书文档评论处理模块，用于对云盘文件进行评论的读取和写入操作。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `feishu_drive_add_comment` | 在飞书/企业微信文档或文件上添加顶层评论。 | 飞书应用凭证 |
| `feishu_drive_list_comments` | 按时间顺序列出飞书/企业微信文件中的全部文档级评论。 | 飞书应用凭证 |
| `feishu_drive_list_comment_replies` | 列出特定飞书评论主题下的所有回复（可以是整个文档的回复，也可以是局部选中的内容）。 | 飞书应用凭证 |
| `feishu_drive_reply_comment` | 在飞书评论主题下发布回复，可选择性添加`@`提及。 | 飞书应用凭证 |

## `file`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `patch` | 对文件进行精准的查找替换编辑。可在终端中替代sed/awk使用。该工具采用模糊匹配算法（共9种策略），因此细微的空白或缩进差异不会影响其正常工作。会返回统一的差异对比结果。编辑完成后还会自动进行语法检查… | — |
| `read_file` | 以带行号且支持分页的方式读取文本文件。可在终端中替代cat/head/tail使用。输出格式为“LINE_NUM\|CONTENT”。如果未找到对应文件，会推荐相似的文件名。处理大文件时可使用offset和limit参数。注意：无法读取图片… | — |
| `search_files` | 搜索文件内容或按名称查找文件。可在终端中替代grep/rg/find/ls使用。基于Ripgrep引擎，速度优于shell命令。支持内容搜索（target='content'）：可在文件内部进行正则表达式搜索。输出模式包括包含完整匹配结果的行号… | — |
| `write_file` | 将内容写入文件，会完全替换文件中的现有内容。可在终端中替代echo/cat heredoc使用。该工具会自动创建所需的父目录。此功能会覆盖整个文件——如需精准编辑，请使用`patch`工具。 | — |

## `homeassistant`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `ha_call_service` | 调用Home Assistant中的服务以控制设备。可使用`ha_list_services`查询各设备类别下可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个Home Assistant实体的详细状态信息，包括所有属性（亮度、颜色、温度设定值、传感器读数等）。 | — |
| `ha_list_entities` | 列出Home Assistant中的所有实体。可选择按设备类别（灯光、开关、温控设备、传感器、二进制传感器、遮光装置、风扇等）或区域名称（客厅、厨房、卧室等）进行筛选。 | — |
| `ha_list_services` | 列出Home Assistant中可用于控制设备的所有服务（操作功能）。会显示每种设备类型支持的操作以及对应的参数。可通过此工具了解如何控制通过`ha_list_entities`找到的设备。 | — |

## `computer_use`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `computer_use` | 通过cua-driver实现后台桌面控制功能——包括截图（SOM / vision / AX）、点击/拖动/滚动/输入/按键/等待操作、列出应用程序、将焦点定位到指定应用等。该功能不会窃取用户的光标或键盘焦点，适用于任何具备工具调用能力的模型，支持macOS、Windows和Linux系统。要求`$当代理由以下任一方式启动时，便会注册该功能：(a) 通过看板调度器生成（设置了 `HERMES_KANBAN_TASK` 环境变量）；或 (b) 在明确启用了 `kanban` 工具集的配置文件中运行。任务级工作节点会为其分配的任务使用生命周期管理工具；而协调器配置文件则还会拥有诸如 `kanban_list` 和 `kanban_unblock` 这样的看板路由工具。完整的流程请参阅 [Kanban 多代理功能](/user-guide/features/kanban)。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `kanban_show` | 显示分配给当前工作节点的活跃看板任务信息（标题、描述、评论及依赖关系）。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_list` | 带有筛选条件的看板任务列表。仅限协调器使用；对由调度器生成的任务工作节点不可见。 | 启用了 `kanban` 工具集的配置文件 |
| `kanban_complete` | 使用结构化的交接数据（包括结果、产出物及后续行动项）将当前任务标记为已完成。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_block` | 因用户提出问题而暂停当前任务——调度器会暂停流程，展示该问题，待有人回复后再继续。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_heartbeat` | 在长时间运行的操作过程中发送进度心跳信号，让调度器知晓工作节点仍在运行。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_comment` | 在任务讨论线程中添加评论而不改变任务状态——适用于分享中间分析结果。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_create` | 从当前任务派生出子任务。由协调器及负责后续任务生成的工作节点使用。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_link` | 通过父子依赖关系链接多个任务。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_unblock` | 将被阻塞的任务恢复为“待处理”状态。仅限协调器使用；对由调度器生成的任务工作节点不可见。 | 启用了 `kanban` 工具集的配置文件 |

## `memory` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `memory` | 将重要信息保存到会跨会话持续存在的持久内存中。在每次会话开始时，这些记忆内容会显示在你的系统提示语中——这便是你在不同对话之间记住用户及环境相关信息的机制。何时使用…… | — |

## `messaging` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `send_message` | 向已连接的消息平台发送消息，或列出可用的目标平台。重要提示：当用户要求发送到特定频道或个人（而非仅平台名称）时，应先调用 `send_message(action='list')` 来查看可用的目标…… | — |

## `session_search` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `session_search` | 搜索存储在本地会话数据库中的过往会话，或在其中滚动查看内容。该功能基于 FTS5 进行检索；直接从数据库返回实际消息内容（无需调用大型语言模型）。共有三种使用方式：发现模式（传入 `query` 参数）、滚动模式（传入 `session_id` 和 `around_message_id` 参数）、浏览模式（不传参数）。 | — |

## `skills` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能相当于你的程序化记忆——为重复出现的任务类型提供可复用的处理方案。新技能会保存在 ~/.hermes/skills/ 目录下；现有技能则可在其所在位置进行修改。可用操作包括：创建（完整的 SKILL.m…… | — |
| `skill_view` | 技能可用于加载关于特定任务及工作流程的信息，以及相关的脚本和模板。可加载技能的完整内容，或访问其关联的文件（参考资料、模板、脚本等）。首次调用时会返回 SKILL.md 的内容以及…… | — |
| `skills_list` | 列出所有可用技能（名称及描述）。如需加载完整内容，可使用 `skill_view(name)`。 | — |

## `terminal` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `process` | 管理通过 `terminal(background=true)` 启动的后台进程。可用操作包括：'list'（显示所有进程）、'poll'（检查状态及新输出）、'log'（分页显示完整输出）、'wait'（阻塞等待直至进程完成或超时）、'kill'（终止进程）、'write'（向进程写入内容）…… | — |
| `terminal` | 在 Linux 环境中执行 shell 命令。文件系统状态会在多次调用之间保持不变。如需运行长时间运行的服务，可设置 `background=true`。若同时设置 `notify_on_complete=true`（配合 `background=true` 使用），则进程完成后会自动发送通知——无需手动轮询。请勿使用 `cat/head/tail` 命令，应改用 `read_file`；也请勿使用 `grep/rg/find` 命令，应改用 `search_files`。 | — |

## `todo` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `todo` | 管理当前会话中的任务列表。适用于包含 3 步及以上的复杂任务，或用户提供了多个任务的情况。不传参数即可读取当前任务列表。进行任务操作时：- 需提供 'todos' 数组来创建/更新任务项 - 可使用 merge=……参数 | — |

## `vision` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `vision_analyze` | 利用人工智能视觉功能分析图像。在具备视觉处理能力的主模型上，该工具会将原始图像像素作为多模态结果返回，以便模型在下一轮处理时直接识别这些像素；而在仅支持文本处理的主模型上，则会回退到辅助视觉模型，由该模型描述图像内容并以文本形式返回结果。无论哪种情况，该工具的接口格式保持一致。 | — |

## `video` 工具集

这是一个可选工具集（默认的 `hermes-cli` 版本中未包含）。可通过 `--toolsets video` 参数添加，或是在 `toolsets:` 配置中明确列出 `video`。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `video_analyze` | 分析来自 URL 或文件路径的视频内容——可提取字幕、场景分解信息、关键时间点以及视觉描述。 | — |

## `video_gen` 工具集

这也是一个可选工具集（默认的 `hermes-cli` 版本中未包含）。可通过 `--toolsets video_gen` 参数添加，或是在 `hermes tools` → Video Generation 中启用，该界面还会指导用户选择合适的后端服务。

各类后端服务均作为插件存在于 `plugins/video_gen/<name>/` 目录下：

- **xAI Grok-Imagine** — 支持文本转视频及图像转视频功能（需使用 SuperGrok OAuth 或 `XAI_API_KEY` 认证）。
- **FAL.ai** — 支持 Veo 3.1、Pixverse v6、Kling O3 等格式（需提供 `FAL_KEY` 认证）。

统一的 `video_generate` 工具可同时处理这两种视频生成模式——如需基于静态图像生成动画，可传入 `image_url` 参数；如仅需根据文本生成视频，则无需传入该参数。系统会自动将请求路由到对应的后端接口。该工具的描述会在每次会话开始时重新生成，以反映当前所选后端的实际功能（支持的模式、宽高比、分辨率、时长范围、最大参考图像数量以及音频支持情况）。如需了解如何自行开发后端插件，请参阅 [视频生成后端插件指南](/developer-guide/video-gen-provider-plugin)。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `video_generate` | 根据文本提示词生成视频（文本转视频），或基于用户配置的视频生成后端将静态图像转换为动画（图像转视频）。如需为静态图像添加动画效果，可传入 `image_url` 参数；仅根据文本生成视频则无需传入该参数。系统会自动将请求路由到对应的后端接口。该工具会通过 `video` 字段返回 HTTP URL 或绝对文件路径。 | 已启用的 `video_gen` 插件及其对应的认证凭证（如 `XAI_API_KEY`、`FAL_KEY`） |

## `web` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `web_search` | 在网络上搜索信息。默认返回最多 5 条结果，包含标题、URL 及描述信息。该工具支持可选的 `limit` 参数（取值范围为 1-100，默认值为 5）。查询语句会被传递给已配置的后端服务，因此只要后端支持相应操作符，如 `site:domain`、`filetype:pdf`、`intitle:word`、`-term` 以及 `"exact phrase"`，即可正常使用。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |
| `web_extract` | 从网页 URL 中提取内容。以 Markdown 格式返回页面内容。该工具也支持 PDF 链接——直接传入 PDF 链接即可，系统会将其转换为 Markdown 文本。字符数低于 5000 的页面会完整输出 Markdown 内容；字符数较多的页面则会被大型语言模型进行总结。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |

## `x_search` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `x_search` | 利用 xAI 内置的 `x_search` Responses 工具，搜索 X（Twitter）上的帖子、个人主页及讨论串。该工具适用于查询 X 平台上的实时讨论、用户反应或相关声明，而非普通网页内容。该功能默认处于关闭状态——需通过 `hermes tools` → 🐦 X (Twitter) Search 手动启用。只有当配置了 xAI 认证凭证后，该工具的架构才会被注册（受 check_fn-gated 机制限制）。 | XAI_API_KEY **或** xAI Grok OAuth（SuperGrok / Premium+ 认证方式） |

## `tts` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `text_to_speech` | 将文本转换为语音音频。该工具会返回一个 MEDIA: 类型的路径，平台会通过该路径将语音消息发送出去。在 Telegram 中，该语音消息会以语音气泡形式呈现；在 Discord/WhatsApp 中则作为音频附件发送。在 CLI 模式下，语音文件会被保存到 ~/voice-memos/ 目录中。关于语音处理及对应服务提供商的更多信息…… | — |

## `discord` 工具集

该工具集在 `hermes-discord` 平台工具集中注册（仅限网关模式使用）。它与消息适配器使用相同的机器人令牌。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord` | 读取并参与 Discord 服务器中的活动。可用操作包括 `search_members`、`fetch_messages`、`send_message`、`react`、`fetch_channel`、`list_channels` 等。 | `DISCORD_BOT_TOKEN` |

## `discord_admin` 工具集

该工具集同样在 `hermes-discord` 平台工具集中注册。执行管理操作时，机器人必须拥有相应的 Discord 权限。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord_admin` | 通过 REST API 管理 Discord 服务器：列出服务器、频道及角色；创建、编辑或删除频道；管理角色的权限设置、超时时间、踢出成员及封禁操作。 | `DISCORD_BOT_TOKEN` 及机器人所需权限 |

## `spotify` 工具集

该工具集由自带的 `spotify` 插件提供。使用时需要 OAuth 令牌——只需运行一次 `hermes spotify setup` 命令进行授权即可。| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `spotify_playback` | 控制 Spotify 播放功能，查看当前播放状态，或获取最近播放过的曲目。 | Spotify OAuth |
| `spotify_devices` | 列出 Spotify Connect 设备，或将播放内容切换到其他设备。 | Spotify OAuth |
| `spotify_queue` | 查看用户的 Spotify 播放队列，或向其中添加内容。 | Spotify OAuth |
| `spotify_search` | 在 Spotify 的曲目、专辑、艺术家、播放列表、节目或剧集目录中进行搜索。 | Spotify OAuth |
| `spotify_playlists` | 列出、查看、创建、更新及修改 Spotify 播放列表。 | Spotify OAuth |
| `spotify_albums` | 获取 Spotify 专辑的元数据或专辑内的曲目信息。 | Spotify OAuth |
| `spotify_library` | 列出、保存或删除用户已收藏的 Spotify 曲目或专辑。 | Spotify OAuth |

## `hermes-yuanbao` 工具集

仅注册于 `hermes-yuanbao` 平台的工具集。Yuanbao 是腾讯推出的聊天应用，这些工具用于驱动该应用的私信、群组及贴纸相关 API。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------------------|
| `yb_query_group_info` | 查询群组的基本信息（在应用中称为“派/Pai”）：名称、所有者及成员数量。 | Yuanbao 凭证 |
| `yb_query_group_members` | 查询群组成员信息（用于@提及、按名称查找用户，以及列出机器人）。 | Yuanbao 凭证 |
| `yb_send_dm` | 向群组中的用户发送私信/直接消息，可附带媒体文件。 | Yuanbao 凭证 |
| `yb_search_sticker` | 根据关键词搜索内置的 Yuanbao 贴纸（TIM 表情）目录。 | Yuanbao 凭证 |
| `yb_send_sticker` | 向当前的 Yuanbao 聊天窗口发送内置贴纸。 | Yuanbao 凭证 |


