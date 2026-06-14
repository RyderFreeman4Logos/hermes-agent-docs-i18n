---
sidebar_position: 3
title: "Built-in Tools Reference"
description: "Authoritative reference for Hermes built-in tools, grouped by toolset"
---

# 内置工具参考

本页面按工具组对Hermes的内置工具进行了文档说明。具体可用工具会因平台、凭证以及已启用的工具组而有所不同。

**当前注册工具总数：**约71种——包括10种浏览器工具（核心功能）+2种需通过CDP授权的浏览器工具，4种文件处理工具，4种Home Assistant相关工具，2种终端工具，2种网页工具，5种飞书工具，7种Spotify工具（由内置的`spotify`插件注册），5种元宝工具，9种看板工具（在看板调度器启动Agent时自动注册），2种Discord工具，以及少量独立工具（`memory`、`clarify`、`delegate_task`、`execute_code`、`cronjob`、`session_search`、`skill_view`/`skill_manage`/`skills_list`、`text_to_speech`、`image_generate`、`video_generate`、`vision_analyze`、`mixture_of_agents`、`send_message`、`todo`、`computer_use`、`process`）。

:::提示 MCP工具
除了内置工具外，Hermes还能从MCP服务器动态加载工具。这类工具的前缀为`mcp_<server>_`（例如，针对`github` MCP服务器的工具名为`mcp_github_create_issue`）。有关配置方法，请参阅[MCP集成](/user-guide/features/mcp)。
:::

## `browser`工具组

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `browser_back` | 在浏览器历史记录中返回上一页。需先调用`browser_navigate`。 | — |
| `browser_click` | 点击快照中通过ref ID标识的元素（例如`@e5`）。这些ref ID会以方括号形式显示在快照输出中。需先调用`browser_navigate`和`browser_snapshot`。 | — |
| `browser_console` | 获取当前页面的浏览器控制台输出及JavaScript错误信息。会返回`console.log/warn/error/info`消息以及未被捕获的JS异常。可用于检测隐性的JavaScript错误、失败的API调用以及应用程序警告。需先… | — |
| `browser_get_images` | 获取当前页面上所有图片的列表，包括其URL和替代文本。有助于找到需要用视觉分析工具处理的图片。需先调用`browser_navigate`。 | — |
| `browser_navigate` | 在浏览器中导航至指定URL。该操作会初始化会话并加载页面。必须在其他浏览器工具之前调用。对于简单的信息检索，建议使用`web_search`或`web_extract`（速度更快且成本更低）。仅在需要…时才使用浏览器工具。 | — |
| `browser_press` | 按下键盘上的某个键。可用于提交表单（Enter键）、导航（Tab键）或执行快捷键操作。需先调用`browser_navigate`。 | — |
| `browser_scroll` | 按指定方向滚动页面。可用于查看当前视口下方或上方的更多内容。需先调用`browser_navigate`。 | — |
| `browser_snapshot` | 获取当前页面无障碍结构树的文本格式快照。会返回带有ref ID的交互式元素（如`@e1`、`@e2`），以便后续使用`browser_click`和`browser_type`功能。`full=false`（默认值）：显示包含交互元素的紧凑视图；`full=true`：显示完整视图… | — |
| `browser_type` | 在通过ref ID标识的输入框中输入文本。该操作会先清空输入框，然后再输入新内容。需先调用`browser_navigate`和`browser_snapshot`。 | — |
| `browser_vision` | 对当前页面进行截图，并使用视觉AI对其进行分析。当需要直观了解页面内容时——尤其是处理验证码、视觉验证任务、复杂布局，或文本提取失败的情况时——可使用此工具。 | — |

## `browser`工具组（CDP授权工具）

这两个工具属于`browser`工具组，但仅在会话启动时能够通过 `/browser connect`、`browser.cdp_url`配置、Browserbase会话或Camofox访问到Chrome DevTools Protocol端点时才会被注册。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `browser_cdp` | 发送原始的Chrome DevTools Protocol命令。它是针对那些未被高级`browser_*`工具覆盖的浏览器操作提供的备用方案。详情请参阅https://chromedevtools.github.io/devtools-protocol/ | CDP端点 |
| `browser_dialog` | 响应原生JavaScript对话框（alert / confirm / prompt / beforeunload）。需先调用`browser_snapshot`——待处理的对话框会显示在其`pending_dialogs`字段中。之后再调用`browser_dialog(action='accept'\|'dismiss')`。 | CDP端点 |

## `clarify`工具组

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `clarify` | 当需要进一步澄清信息、获取反馈或在做决定前需要用户输入意见时，可使用此工具提出问题。支持两种模式：1. **多项选择**——最多提供4个选项。用户可选择其中一个选项，或通过第5个“其他”选项输入自定义答案。2.… | — |

## `code_execution`工具组

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `execute_code` | 运行能够以编程方式调用Hermes工具的Python脚本。当需要执行3次及以上工具调用，并且这些调用之间需要处理逻辑，或在工具输出进入上下文之前需要对其进行过滤/简化，或需要条件分支处理时，可使用此工具。… | — |

## `cronjob`工具组

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `cronjob` | 统一的定时任务管理器。可通过`action="create"`、`"list"`、`"update"`、`"pause"`、`"resume"`、`"run"`或`"remove"`来管理任务。支持由一个或多个技能驱动的任务，若在更新时设置`skills=[]`则可清除已附加的技能。Cron任务的执行会在没有当前聊天上下文的新的会话中进行。 | — |

## `delegation`工具组

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `delegate_task` | 启动一个或多个子Agent在独立的上下文中处理任务。每个子Agent都会拥有自己的对话窗口、终端会话以及工具集。最终只会返回汇总结果——中间阶段的工具处理结果不会进入你的上下文窗口。有两种… | — |

## `feishu_doc`工具组

该工具组专为飞书文档评论智能回复处理器（`gateway/platforms/feishu_comment.py`）设计，不会在`hermes-cli`或常规飞书聊天适配器中提供。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `feishu_doc_read` | 根据文件类型和令牌，读取飞书/企业微信文档（Docx、Doc或Sheet格式）的完整文本内容。 | 飞书应用凭证 |

## `feishu_drive`工具组

该工具组专为飞书文档评论处理器设计，用于对驱动器中的文件进行评论的读写操作。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `feishu_drive_add_comment` | 在飞书/企业微信文档或文件上添加顶层评论。 | 飞书应用凭证 |
| `feishu_drive_list_comments` | 按时间顺序列出飞书/企业微信文件中的所有文档级评论。 | 飞书应用凭证 |
| `feishu_drive_list_comment_replies` | 列出特定飞书评论主题下的所有回复（可以是整个文档的回复，也可以是局部选中的内容）。 | 飞书应用凭证 |
| `feishu_drive_reply_comment` | 在飞书评论主题下发布回复，可选择是否使用`@`来提及他人。 | 飞书应用凭证 |

## `file`工具组

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `patch` | 对文件进行精准的查找并替换编辑。可在终端中替代sed/awk使用。该工具采用模糊匹配算法（共有9种策略），因此细微的空白或缩进差异不会影响其正常运行。它会返回统一的差异对比结果，并在编辑完成后自动进行语法检查… | — |
| `read_file` | 以带行号且支持分页的方式读取文本文件。可在终端中替代cat/head/tail使用。输出格式为“LINE_NUM\|CONTENT”。如果未找到目标文件，会推荐相似的文件名。处理大文件时可使用offset和limit参数。注意：该工具无法读取图片… | — |
| `search_files` | 搜索文件内容或按名称查找文件。可在终端中替代grep/rg/find/ls使用。该工具基于Ripgrep实现，速度优于Shell中的同类命令。支持内容搜索（target='content'）：可在文件内部进行正则表达式搜索。输出模式包括包含完整匹配结果的行… | — |
| `write_file` | 将内容写入文件，会完全替换文件中的现有内容。可在终端中替代echo/cat heredoc使用。该工具会自动创建所需的父目录。该操作会覆盖整个文件——如需进行精准编辑，请使用`patch`工具。 | — |

## `homeassistant`工具组

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `ha_call_service` | 调用Home Assistant中的服务以控制设备。可使用`ha_list_services`来查看各领域中可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个Home Assistant实体的详细状态，包括所有属性（亮度、颜色、温度设定值、传感器读数等）。 | — |
| `ha_list_entities` | 列出Home Assistant中的所有实体。可选择按领域（灯光、开关、温控设备、传感器、二进制传感器、遮光装置、风扇等）或按区域名称（客厅、厨房、卧室等）进行过滤。 | — |
| `ha_list_services` | 列出Home Assistant中可用于控制设备的所有服务（操作）。会显示每种设备类型支持的操作以及它们所接受的参数。可通过此功能了解如何控制通过`ha_list_entities`找到的设备。 | — |

## `computer_use`工具组

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `computer_use` | 通过cua-driver在macOS后台控制桌面操作——包括截图（SOM / vision / AX模式）、点击/拖动/滚动/输入文本/按键/等待、列出应用程序、将焦点切换到指定应用等。该工具不会窃取用户的光标或键盘焦点，适用于任何具备工具处理能力的模型，仅支持macOS系统。需在`$| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `kanban_show` | 显示分配给当前工人的正在处理的看板任务信息（标题、描述、评论、依赖关系）。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_list` | 带过滤条件的看板任务列表。仅限调度器使用；对由调度器创建的任务工人不可见。 | 配置了 `kanban` 工具集的账号 |
| `kanban_complete` | 通过结构化的交接数据标记当前任务已完成（包含结果、输出物及后续行动项）。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_block` | 因问题暂时阻塞当前任务——调度器会暂停任务并显示相关问题，待人工回复后再继续处理。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_heartbeat` | 在长时间运行的操作中发送进度心跳信号，让调度器知晓工人仍在工作。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_comment` | 在任务讨论线程中添加评论而不改变任务状态——适用于分享中间处理结果。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_create` | 从当前任务派生出子任务。由调度器及负责后续任务的工人使用。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_link` | 通过父子依赖关系连接多个任务。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_unblock` | 将被阻塞的任务恢复为“待处理”状态。仅限调度器使用；对由调度器创建的任务工人不可见。 | 配置了 `kanban` 工具集的账号 |

## `memory` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `memory` | 将重要信息保存到会话间仍可保留的持久内存中。在每次会话开始时，这些记忆内容会显示在系统提示词中——这样你就能在多次对话之间记住关于用户及环境的信息。何时使用…… | — |

## `messaging` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `send_message` | 向已连接的消息平台发送消息，或列出可用的目标平台。重要提示：当用户要求发送到特定频道或个人（而非仅平台名称）时，应先调用 `send_message(action='list')` 查看可用目标…… | — |

## `moa` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `mixture_of_agents` | 通过多个前沿大语言模型协同处理复杂问题。该工具会发起最多5次API调用（4个参考模型+1个聚合器），并投入最大程度的推理能力——仅适用于真正棘手的难题。最适合处理：复杂数学题、高级算法…… | `OPENROUTER_API_KEY` |

## `session_search` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `session_search` | 搜索存储在本地会话数据库中的过往会话，或在其中滚动查看内容。基于FTS5检索技术；直接从数据库返回实际消息内容（无需调用大语言模型）。提供三种使用方式：查询搜索（传入`query`参数）、滚动浏览（传入`session_id`和`around_message_id`参数）、目录式浏览（无需参数）。 | — |

## `skills` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能相当于你的程序化记忆——为重复出现的任务类型提供可复用的处理方案。新技能会保存在`~/.hermes/skills/`目录下；现有技能则可在其所在位置进行修改。可用操作：创建（需完整的SKILL.m……文件） | — |
| `skill_view` | 技能可用于加载关于特定任务及工作流程的信息，以及相关的脚本和模板。可加载技能的完整内容，或访问其关联的文件（参考资料、模板、脚本等）。首次调用时会返回SKILL.md文件的内容以及…… | — |
| `skills_list` | 列出所有可用技能（名称及描述）。可使用`skill_view(name)`来加载完整内容。 | — |

## `terminal` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `process` | 管理通过`terminal(background=true)`启动的后台进程。可用操作包括：‘list’（列出所有进程）、‘poll’（检查状态及新输出）、‘log’（分页显示完整输出）、‘wait’（阻塞等待直到进程完成或超时）、‘kill’（终止进程）、‘write’（向进程写入内容）…… | — |
| `terminal` | 在Linux环境中执行Shell命令。文件系统状态在多次调用之间保持不变。如需运行长时间运行的服务，可设置`background=true`。若同时设置`notify_on_complete=true`（配合`background=true`使用），则进程完成后会自动发送通知——无需手动轮询。请勿使用`cat/head/tail`命令，应改用`read_file`；也请勿使用`grep/rg/find`命令，应改用`search_files`。 | — |

## `todo` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `todo` | 管理当前会话中的任务列表。适用于包含3个以上步骤的复杂任务，或用户提供了多项任务时的情况。不传参数即可读取当前任务列表。进行任务操作时：需提供‘todos’数组来创建/更新任务项；可使用`merge=`参数实现任务合并…… | — |

## `vision` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `vision_analyze` | 利用人工智能视觉功能分析图片。在具备视觉处理能力的主模型上，该工具会将原始图像像素作为多模态结果返回，以便模型在后续处理时直接使用这些像素数据；而在仅支持文本处理的主模型上，则会调用辅助视觉模型对图片进行描述，并以文本形式返回描述结果。无论哪种情况，该工具的接口格式保持一致。 | — |

## `video` 工具集

这是一个可选工具集（默认的`hermes-cli`版本中未包含）。可通过`--toolsets video`参数添加，或在其`toolsets:`配置中明确列出`video`。 

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `video_analyze` | 分析来自URL或文件路径的视频内容——可提取字幕、场景分解信息、关键时间点以及视觉描述。 | — |

## `video_gen` 工具集

这也是一个可选工具集（默认的`hermes-cli`版本中未包含）。可通过`--toolsets video_gen`参数添加，或通过“hermes tools” → “Video Generation”选项进行启用，该选项还会指导用户选择合适的后端服务。

各类后端服务均作为插件存在于`plugins/video_gen/<name>/`目录下：

- **xAI Grok-Imagine** —— 支持文本转视频和图片转视频功能（需要SuperGrok OAuth授权或`XAI_API_KEY`）。
- **FAL.ai** —— 支持Veo 3.1、Pixverse v6、Kling O3模型（需要`FAL_KEY`）。

统一的`video_generate`工具可同时处理这两种转换类型——若要为静态图片添加动画效果，需传入`image_url`参数；若仅基于文本生成视频，则无需传入该参数。系统会自动将请求路由到对应的后端接口。该工具的描述会在每次会话开始时重新生成，以反映当前所选后端的实际功能能力（支持的格式类型、宽高比、分辨率、时长范围、最大参考图片数量、音频支持情况等）。如需了解如何自行开发后端插件，请参阅[视频生成后端插件指南](/developer-guide/video-gen-provider-plugin)。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `video_generate` | 根据文本提示词生成视频（文本转视频），或为静态图片添加动画效果（图片转视频），具体使用用户配置的视频生成后端。如需为图片添加动画，需传入`image_url`参数；仅基于文本生成视频则无需该参数。系统会自动将请求路由到对应的后端接口。该工具会通过`video`字段返回HTTP网址或绝对文件路径。 | 已启用的`video_gen`插件及其认证凭证（如`XAI_API_KEY`、`FAL_KEY`） |

## `web` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `web_search` | 在网络上搜索信息。默认返回最多5条结果，包含标题、网址及描述信息。该工具支持传入可选的`limit`参数（数值范围为1-100，默认值为5）。查询语句会传递给已配置的后端服务，因此只要后端支持，诸如`site:domain`、`filetype:pdf`、`intitle:word`、`-term`以及`"exact phrase"`之类的查询条件都可以使用。 | `EXA_API_KEY` 或 `PARALLEL_API_KEY` 或 `FIRECRAWL_API_KEY` 或 `TAVILY_API_KEY` |
| `web_extract` | 从网页URL中提取内容。以Markdown格式返回页面内容。该工具也支持处理PDF文件——直接传入PDF链接即可，系统会将其转换为Markdown文本。内容长度在5000字符以内的页面会完整输出Markdown格式；长度更长的页面则会被大语言模型总结后呈现。 | `EXA_API_KEY` 或 `PARALLEL_API_KEY` 或 `FIRECRAWL_API_KEY` 或 `TAVILY_API_KEY` |

## `x_search` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `x_search` | 使用xAI内置的`x_search` Responses工具，搜索X（Twitter）上的帖子、账号资料及话题讨论。该工具适用于查看X平台上的实时讨论、用户反应或相关声明，而非普通网页内容。该功能默认处于关闭状态——需通过“hermes tools” → 🐦 X (Twitter) Search选项手动启用。只有当配置了xAI认证凭证后，该工具的接口结构才会被注册（受`check_fn-gated`机制限制）。 | `XAI_API_KEY` **或** xAI Grok OAuth授权（SuperGrok / Premium+账号） |

## `tts` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `text_to_speech` | 将文本转换为语音音频。该工具会返回一个MEDIA:类型的路径，平台会通过该路径将语音消息发送出去。在Telegram中，转换后的内容会以语音气泡形式呈现；在Discord/WhatsApp中则作为音频附件发送。在CLI模式下，转换结果会保存到`~/voice-memos/`目录中。关于语音处理及相关服务提供商的更多信息…… | — |

## `discord` 工具集

该工具集已注册在`hermes-discord`平台工具集中（仅支持网关模式）。其使用的机器人令牌与消息传输适配器相同。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord` | 读取并参与Discord服务器中的活动。可用操作包括`search_members`（搜索成员）、`fetch_messages`（获取消息）、`send_message`（发送消息）、`react`（对消息作出反应）、`fetch_channel`（获取频道信息）、`list_channels`（列出所有频道）等。 | `DISCORD_BOT_TOKEN` |

## `discord_admin` 工具集

该工具集同样已注册在`hermes-discord`平台工具集中。执行管理操作时，机器人必须拥有相应的Discord权限。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord_admin` | 通过REST API管理Discord服务器：列出服务器、频道及角色信息；创建、编辑或删除频道；管理角色的权限设置、超时规则、成员踢出操作以及封禁功能。 | `DISCORD_BOT_TOKEN` + 机器人所需权限 |

## `spotify` 工具集

该工具集由自带的`spotify`插件提供。使用时需要OAuth授权令牌——只需运行一次`hermes spotify setup`命令即可完成授权。| 工具 | 描述 | 所需环境 |
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


