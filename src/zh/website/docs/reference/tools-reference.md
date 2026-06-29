---
sidebar_position: 3
title: "Built-in Tools Reference"
description: "Authoritative reference for Hermes built-in tools, grouped by toolset"
---

# 内置工具参考

本页面按工具集对Hermes的内置工具进行说明。实际可用工具会因平台、凭证以及已启用的工具集而有所不同。

**当前注册工具总数：**约73种——10种浏览器工具（核心功能）+2种需CDP授权的浏览器工具，4种文件处理工具，4种Home Assistant相关工具，3种终端工具（`terminal`、`process`、`read_terminal`），2种网页工具，5种飞书工具，7种Spotify相关工具（由内置的`spotify`插件注册），5种元宝工具，9种看板工具（在看板调度器启动代理时自动注册），3种项目相关工具（桌面/GUI会话），2种Discord相关工具，以及若干独立工具（`memory`、`clarify`、`delegate_task`、`execute_code`、`cronjob`、`session_search`、`skill_view`/`skill_manage`/`skills_list`、`text_to_speech`、`image_generate`、`video_generate`、`vision_analyze`、`todo`、`computer_use`）。

:::提示 MCP工具
除了内置工具外，Hermes还可以从MCP服务器动态加载工具。这类工具的前缀为`mcp_<server>_`（例如，针对`github` MCP服务器的工具名为`mcp_github_create_issue`）。有关配置方法，请参阅[MCP集成](/user-guide/features/mcp)。
:::

## `browser`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `browser_back` | 在浏览器历史记录中返回上一页。需先调用`browser_navigate`。 | — |
| `browser_click` | 点击快照中通过ref ID标识的元素（例如`@e5`）。这些ref ID会以方括号形式显示在快照输出中。需先调用`browser_navigate`和`browser_snapshot`。 | — |
| `browser_console` | 获取当前页面的浏览器控制台输出及JavaScript错误信息。会返回`console.log/warn/error/info`消息以及未被捕获的JS异常。可用于检测隐性的JavaScript错误、失败的API调用以及应用程序警告。需先… | — |
| `browser_get_images` | 获取当前页面上所有图片的列表，包括其URL和替代文本。有助于找出需要用视觉分析工具处理的图片。需先调用`browser_navigate`。 | — |
| `browser_navigate` | 在浏览器中导航至指定URL。该操作会初始化会话并加载页面。必须在其他浏览器工具之前调用。对于简单的信息检索，建议使用`web_search`或`web_extract`（速度更快、成本更低）。仅在需要…时才使用浏览器工具。 | — |
| `browser_press` | 按下键盘上的某个键。可用于提交表单（回车键）、导航（Tab键）或执行快捷键操作。需先调用`browser_navigate`。 | — |
| `browser_scroll` | 按指定方向滚动页面。可用于查看当前视口下方或上方的更多内容。需先调用`browser_navigate`。 | — |
| `browser_snapshot` | 获取当前页面无障碍访问结构的文本格式快照。会返回带有ref ID的交互式元素（如`@e1`、`@e2`），以便后续使用`browser_click`和`browser_type`功能。`full=false`（默认值）：显示简洁的交互式元素视图；`full=true`：显示完整视图… | — |
| `browser_type` | 在通过ref ID标识的输入框中输入文本。该操作会先清空输入框，然后再输入新内容。需先调用`browser_navigate`和`browser_snapshot`。 | — |
| `browser_vision` | 对当前页面进行截图，并使用视觉AI对其进行分析。当需要直观了解页面内容时非常有用——尤其适用于验证码、视觉验证任务、复杂布局，或文本无法准确识别等情况。 | — |

## `browser`工具集（CDP授权工具）

这两个工具属于`browser`工具集，但仅在会话启动时能够通过 `/browser connect`、`browser.cdp_url`配置、Browserbase会话或Camofox访问到Chrome DevTools Protocol端点时才会注册。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `browser_cdp` | 发送原始的Chrome DevTools Protocol命令。作为高级`browser_*`工具无法处理的一些浏览器操作的替代方案。详情请参阅https://chromedevtools.github.io/devtools-protocol/ | CDP端点 |
| `browser_dialog` | 对原生JavaScript对话框（如alert / confirm / prompt / beforeunload）作出响应。需先调用`browser_snapshot`——待处理的对话框会显示在其`pending_dialogs`字段中。之后再调用`browser_dialog(action='accept'\|'dismiss')`。 | CDP端点 |

## `clarify`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `clarify` | 在需要进一步澄清、获取反馈或做出决策时向用户提问。支持两种模式：1. **多项选择**——最多提供4个选项。用户可选择其中一个，或通过第5个“其他”选项输入自定义答案。2.… | — |

## `code_execution`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `execute_code` | 运行能够以编程方式调用Hermes工具的Python脚本。当需要在多次工具调用之间添加处理逻辑、在内容进入上下文之前对其进行过滤/简化，或实现条件分支时，可使用此工具。… | — |

## `cronjob`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `cronjob` | 统一的定时任务管理器。可通过`action="create"`、"`list"`、"`update"`、"`pause"`、"`resume"`、"`run"`或`"remove"`来管理任务。支持由一个或多个技能驱动的任务，若在更新时设置`skills=[]`则可清除关联的技能。定时任务会在没有当前聊天上下文的新的会话中执行。 | — |

## `delegation`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `delegate_task` | 启动一个或多个子代理，在独立的上下文中处理任务。每个子代理都有自己独立的对话、终端会话和工具集。最终只会返回总结结果——中间阶段的工具处理结果不会进入你的上下文窗口。有两种… | — |

## `feishu_doc`工具集

该工具集专为飞书文档评论智能回复处理器（`gateway/platforms/feishu_comment.py`）设计。不会在`hermes-cli`或常规飞书聊天适配器中提供。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `feishu_doc_read` | 根据文件类型和令牌，读取飞书/企业微信文档（Docx、Doc或Sheet格式）的完整文本内容。 | 飞书应用凭证 |

## `feishu_drive`工具集

该工具集专为飞书文档评论处理器设计，用于对云盘文件进行评论的读写操作。

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `feishu_drive_add_comment` | 在飞书/企业微信文档或文件上添加顶层评论。 | 飞书应用凭证 |
| `feishu_drive_list_comments` | 按时间顺序列出飞书/企业微信文件中的所有文档级评论。 | 飞书应用凭证 |
| `feishu_drive_list_comment_replies` | 列出特定飞书评论主题下的所有回复（可针对整个文档或局部选中的内容）。 | 飞书应用凭证 |
| `feishu_drive_reply_comment` | 在飞书评论主题下发布回复，可选择是否使用`@`提及他人。 | 飞书应用凭证 |

## `file`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `patch` | 对文件进行精准的查找替换编辑。可在终端中替代sed/awk使用。该工具采用模糊匹配算法（共9种策略），因此细微的空白或缩进差异不会影响其正常运行。会返回统一格式的差异对比结果。编辑完成后还会自动进行语法检查… | — |
| `read_file` | 以带行号且支持分页的方式读取文本文件。可在终端中替代cat/head/tail使用。输出格式为“行号\|内容”。如果未找到对应文件，会推荐相似名称的文件。处理大文件时建议使用偏移量和限制值。注意：无法读取图片… | — |
| `search_files` | 搜索文件内容或按名称查找文件。可在终端中替代grep/rg/find/ls使用。基于Ripgrep引擎，速度优于传统shell命令。支持内容搜索（target='content'）：可在文件内部进行正则表达式搜索。输出模式包括包含完整匹配内容的行… | — |
| `write_file` | 将内容写入文件，会完全替换文件中的现有内容。可在终端中替代echo/cat heredoc使用。该工具会自动创建所需的父目录。操作为直接覆盖整个文件——如需精准编辑，请使用`patch`工具。 | — |

## `homeassistant`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `ha_call_service` | 调用Home Assistant中的服务以控制设备。可使用`ha_list_services`查看各领域中可用的服务及其参数。 | — |
| `ha_get_state` | 获取单个Home Assistant实体的详细状态，包括所有属性（亮度、颜色、温度设定值、传感器读数等）。 | — |
| `ha_list_entities` | 列出Home Assistant中的所有实体。可选择按领域（灯光、开关、温控设备、传感器、二进制传感器、遮光装置、风扇等）或区域名称（客厅、厨房、卧室等）进行过滤。 | — |
| `ha_list_services` | 列出Home Assistant中可用于控制设备的所有服务（操作）。会显示每种设备类型支持的操作及其参数。可通过此功能了解如何控制通过`ha_list_entities`找到的设备。 | — |

## `computer_use`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `computer_use` | 通过cua-driver实现后台桌面控制功能——包括截图（SOM / vision / AX）、点击/拖动/滚动/输入/按键/等待、列出应用程序、将焦点切换到指定应用等。该功能不会窃取用户的光标或键盘焦点。适用于任何具备工具处理能力的模型，支持macOS、Windows和Linux系统。 | `$PATH`路径下需安装`cua-driver`（可通过`hermes tools`命令安装）。 |


:::注意
**Honcho工具**（`honcho_profile`、`honcho_search`、`honcho_context`、`honcho_reasoning`、`honcho_conclude`）已不再属于内置工具。它们可通过Honcho内存提供者插件在`plugins/memory/honcho/`路径下使用。有关安装和使用方法，请参阅[内存提供者](../user-guide/features/memory-providers.md)。
:::

## `image_gen`工具集

| 工具 | 描述 | 所需环境 |
|------|-------------|----------|
| `image_generate` | 根据文本提示生成图像（文本转图像），或通过用户自定义的后端（FAL.ai、OpenAI、xAI、Krea）对现有图像进行编辑/转换（图像转图像）。如需编辑图像，请传入`image_url`；如需参考风格，请传入`reference_image_urls`；如仅需进行文本转图像，则无需传入这两个参数。模型由用户自行配置，代理无法选择。该工具会返回一个图像的URL或本地路径。 | FAL_KEY / OPENAI_API_KEY / xAI OAuth / KREA_API_KEY |

## `kanban`工具集 |当代理由以下任一方式启动时，便会注册这些工具：(a) 通过看板调度器生成（设置了 `HERMES_KANBAN_TASK` 环境变量）；或 (b) 在明确启用了 `kanban` 工具集的配置文件中运行。任务级工作节点会为其分配的任务使用生命周期管理工具；而协调器配置文件则还会拥有诸如 `kanban_list` 和 `kanban_unblock` 这样的看板路由工具。完整的流程请参阅 [Kanban 多代理功能](/user-guide/features/kanban)。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `kanban_show` | 显示分配给当前工作节点的活跃看板任务信息（标题、描述、评论及依赖关系）。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_list` | 带有过滤条件的看板任务列表。仅限协调器使用；对由调度器生成的任务工作节点不可见。 | 启用了 `kanban` 工具集的配置文件 |
| `kanban_complete` | 使用结构化的交接数据（结果、输出物及后续行动项）将当前任务标记为已完成。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_block` | 因用户提出问题而暂停当前任务——调度器会暂停流程，展示该问题，待有人回复后再继续。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_heartbeat` | 在长时间运行的操作过程中发送进度心跳信号，以便调度器知晓工作节点仍在运行。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_comment` | 在任务讨论线程中添加评论而不改变其状态——适用于展示中间处理结果。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_create` | 从当前任务派生出子任务。由协调器及负责后续任务生成的工作节点使用。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_link` | 通过父子依赖关系连接任务。 | `HERMES_KANBAN_TASK` 或 `kanban` 工具集 |
| `kanban_unblock` | 将被阻塞的任务恢复为“准备就绪”状态。仅限协调器使用；对由调度器生成的任务工作节点不可见。 | 启用了 `kanban` 工具集的配置文件 |

## `project` 工具集

用于管理桌面端的 [项目](../user-guide/cli.md)——即带有名称的多文件夹工作空间。当启用了 `project` 工具集时（主要在桌面应用/控制台界面中）便会注册这些工具。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `project_create` | 创建一个桌面项目（即带名称的工作空间），并将当前聊天窗口切换到该项目中。可通过传递 `path` 参数将其绑定到某个代码库或文件夹。 | — |
| `project_list` | 列出所有桌面项目以及当前处于活动状态的项目。 | — |
| `project_switch` | 将当前聊天窗口切换到已存在的某个项目（可通过名称、唯一标识符或 ID 来指定）；同时会将会话的工作空间移至该项目的主文件夹中。 | — |

## `memory` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `memory` | 将重要信息保存到可跨会话持续存在的持久内存中。在每次会话开始时，这些记忆内容会显示在系统提示语中——这便是你在不同对话之间记住用户及相关环境信息的方式。何时使用…… | — |

## `session_search` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `session_search` | 搜索存储在本地会话数据库中的过往会话，或在其中滚动查看内容。基于 FTS5 技术进行检索；直接从数据库返回实际消息内容（无需调用大型语言模型）。共有三种使用方式：发现模式（传递 `query` 参数）、滚动模式（传递 `session_id` 和 `around_message_id` 参数）、浏览模式（无需参数）。 | — |

## `skills` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `skill_manage` | 管理技能（创建、更新、删除）。技能相当于你的程序化记忆——针对重复出现的任务类型，可重复使用的处理方法。新技能会存储在 ~/.hermes/skills/ 目录下；现有技能则可在其所在位置进行修改。可用操作包括：创建（完整的 SKILL.m… 文件格式）。 | — |
| `skill_view` | 技能可用于加载关于特定任务及工作流程的信息，以及脚本和模板。可加载技能的完整内容，或访问其关联的文件（参考资料、模板、脚本等）。首次调用时会返回 SKILL.md 文件的内容以及……相关信息。 | — |
| `skills_list` | 列出所有可用技能（包括名称和描述）。可通过调用 skill_view(name) 来加载完整的技能内容。 | — |

## `terminal` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `process` | 管理通过终端命令以 `background=true` 参数启动的后台进程。可用操作包括：'list'（列出所有进程）、'poll'（检查状态及新输出）、'log'（分页显示完整输出）、'wait'（阻塞等待直至进程完成或超时）、'kill'（终止进程）、'write'（向进程写入内容）……等。 | — |
| `terminal` | 在 Linux 环境中执行 shell 命令。文件系统状态会在多次调用之间保持不变。如需运行长时间运行的服务，可设置 `background=true` 参数。若同时设置 `notify_on_complete=true`（配合 `background=true` 使用），则进程完成后会自动发送通知——无需手动轮询。请勿使用 cat/head/tail 命令，应改用 read_file；也请勿使用 grep/rg/find 命令，应改用 search_files。 | — |
| `read_terminal` | 读取 Hermes 桌面 GUI 中内置终端面板当前显示的内容（即位于该聊天窗口旁边的嵌入式shell）。仅适用于桌面应用。 | — |

## `todo` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `todo` | 管理当前会话中的任务列表。适用于包含3个以上步骤的复杂任务，或用户同时提供了多个任务的情况。无需传递参数即可读取当前任务列表。进行任务操作时：- 可通过提供 'todos' 数组来创建或更新任务项 - 还可使用 merge=… 参数进行合并操作。 | — |

## `vision` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `vision_analyze` | 利用人工智能视觉技术分析图像。在具备视觉处理能力的主模型上，该工具会将原始图像像素作为多模态结果返回，以便模型在后续处理时直接使用这些像素数据。而在仅支持文本处理的主模型上，则会回退到辅助的视觉模型，由该模型描述图像内容并以文本形式返回描述结果。无论哪种情况，该工具的接口格式保持一致。 | — |

## `video` 工具集

这是一个可选工具集（默认的 `hermes-cli` 安装版本中不包含）。可通过 `--toolsets video` 参数添加，或是在 `toolsets:` 配置项中明确列出 `video`。 

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `video_analyze` | 分析来自 URL 或文件路径的视频内容——可提取字幕、场景分解信息、关键时间戳以及视觉描述等内容。 | — |

## `video_gen` 工具集

这也是一个可选工具集（默认的 `hermes-cli` 安装版本中不包含）。可通过 `--toolsets video_gen` 参数添加，或是在 `hermes tools` → Video Generation 中启用，该界面还会指导用户选择合适的后端服务。

各类后端服务均以插件形式存在，路径为 `plugins/video_gen/<name>/`：

- **xAI Grok-Imagine** —— 支持文本转视频及图像转视频功能（需使用 SuperGrok OAuth 或 `XAI_API_KEY` 认证）。
- **FAL.ai** —— 支持 Veo 3.1、Pixverse v6、Kling O3 等模型（需提供 `FAL_KEY` 认证）。

单个 `video_generate` 工具即可同时处理这两种转换类型——若要为静态图像添加动画效果，可传递 `image_url` 参数；若仅需根据文本生成视频，则无需传递该参数。系统会自动将请求路由到对应的后端接口。该工具的描述内容会在每次会话开始时重新生成，以反映当前所选后端的实际功能能力（支持的格式类型、宽高比、分辨率、时长范围、最大参考图像数量以及音频支持情况等）。如需了解如何开发自定义的后端插件，请参阅 [视频生成后端插件指南](/developer-guide/video-gen-provider-plugin)。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `video_generate` | 根据文本提示词生成视频（文本转视频），或为静态图像添加动画效果（图像转视频），具体功能取决于用户所配置的视频生成后端。若要为图像添加动画，可传递 `image_url` 参数；仅根据文本生成视频则无需传递该参数。系统会自动将请求路由到对应的后端接口。该工具会返回一个 HTTP URL，或在 `video` 字段中返回完整的文件路径。 | 已启用的 `video_gen` 插件及其对应的认证凭证（如 `XAI_API_KEY`、`FAL_KEY` 等） |

## `web` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `web_search` | 在网络上搜索信息。默认最多返回5条结果，每条结果均包含标题、URL及描述信息。该工具支持可选的 `limit` 参数（取值范围为1-100，默认值为5）。查询语句会被传递给已配置的后端服务，因此只要后端支持相应操作符，如 `site:domain`、`filetype:pdf`、`intitle:word`、`-term` 以及 `"exact phrase"` 等，均可正常使用。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |
| `web_extract` | 从网页 URL 中提取内容。以 Markdown 格式返回页面内容。该工具也支持处理 PDF 文件的 URL——直接传递 PDF 链接即可，系统会将其转换为 Markdown 文本。字符数在5000字以内的页面会完整输出 Markdown 内容；字符数更多的页面则会被大型语言模型进行摘要处理。 | EXA_API_KEY 或 PARALLEL_API_KEY 或 FIRECRAWL_API_KEY 或 TAVILY_API_KEY |

## `x_search` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `x_search` | 利用 xAI 内置的 `x_search` Responses 工具，搜索 X（Twitter）上的帖子、用户主页及讨论串。该工具适用于查询 X 平台上的当前讨论内容、用户反应或相关声明，而非普通的网页信息。该功能默认处于关闭状态——需通过 `hermes tools` → 🐦 X (Twitter) Search 选项手动启用。只有当配置了 xAI 认证凭证后，该工具的架构才会被注册（受 check_fn-gated 机制限制）。 | XAI_API_KEY **或** xAI Grok OAuth（SuperGrok / Premium+ 认证方式） |

## `tts` 工具集

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `text_to_speech` | 将文本转换为语音音频。该工具会返回一个 MEDIA: 类型的路径，平台会通过该路径将语音消息发送出去。在 Telegram 中，该语音消息会以语音气泡形式呈现；在 Discord/WhatsApp 中则作为音频附件发送。在 CLI 模式下，转换后的音频文件会被保存到 ~/voice-memos/ 目录中。 | — |

## `discord` 工具集

该工具集会在 `hermes-discord` 平台工具集中注册（仅限于网关层使用）。它使用的机器人令牌与消息传递适配器相同。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord` | 读取并参与 Discord 服务器中的交流。可用功能包括 `search_members`（搜索成员）、`fetch_messages`（获取消息）、`send_message`（发送消息）、`react`（发表情反应）、`fetch_channel`（获取频道信息）、`list_channels`（列出所有频道）等。 | `DISCORD_BOT_TOKEN` |

## `discord_admin` 工具集

该工具集同样在 `hermes-discord` 平台工具集中注册。执行管理操作时，机器人必须拥有相应的 Discord 权限。

| 工具 | 描述 | 所需环境 |
|------|------|----------|
| `discord_admin` | 通过 REST API 管理 Discord 服务器：可列出服务器、频道及角色信息，创建、编辑或删除频道，管理角色的权限设置、超时时间、成员踢出操作以及封禁功能等。 | `DISCORD_BOT_TOKEN` 及机器人所需的相应权限 |

## `spotify` 工具集

该工具集由自带的 `spotify` 插件负责注册。使用时需要一个 OAuth 令牌——只需运行一次 `hermes spotify setup` 命令进行授权即可。| 工具 | 描述 | 所需环境 |
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


