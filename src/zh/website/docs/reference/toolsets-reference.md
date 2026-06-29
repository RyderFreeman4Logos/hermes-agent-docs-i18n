---
sidebar_position: 4
title: "Toolsets Reference"
description: "Reference for Hermes core, composite, platform, and dynamic toolsets"
---

# 工具集参考

工具集是一组按名称命名的工具集合，用于控制智能体能够执行的功能。它们是按平台、会话或任务配置工具可用性的主要机制。

## 工具集的工作原理

每个工具仅属于一个工具集。当您启用某个工具集后，该集合中的所有工具都会对智能体可用。工具集分为三种类型：

- **核心型**——由一组相关的工具构成的逻辑单元（例如，`file` 工具集包含 `read_file`、`write_file`、`patch`、`search_files` 等工具）
- **复合型**——为特定场景整合多个核心工具集（例如，`debugging` 工具集汇集了文件操作、终端操作和网页操作相关的工具）
- **平台专用型**——针对特定部署环境设计的完整工具配置（例如，交互式 CLI 会话的默认工具集为 `hermes-cli`）

## 配置工具集

### 按会话配置（CLI）

```bash
hermes chat --toolsets web,file,terminal
hermes chat --toolsets debugging        # composite — expands to file + terminal + web
hermes chat --toolsets all              # everything
```

### 各平台专用配置（config.yaml）

```yaml
toolsets:
  - hermes-cli          # default for CLI
  # - hermes-telegram   # override for Telegram gateway
```

### 交互式管理

```bash
hermes tools                            # curses UI to enable/disable per platform
```

或者通过会话方式：

```
/tools list
/tools disable browser
/tools enable homeassistant
```

## 核心工具集

| 工具集 | 工具 | 用途 |
|---------|------|------|
| `browser` | `browser_back`, `browser_cdp`, `browser_click`, `browser_console`, `browser_dialog`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `web_search` | 核心浏览器自动化功能。其中 `web_search` 用于快速查询作为备用方案。`browser_cdp` 和 `browser_dialog` 会在运行时动态启用——仅在会话启动时可通过 `/browser connect`、`browser.cdp_url` 配置、Browserbase 或 Camofox 获取 CDP 接口后才会注册。当连接了 CDP 监控节点后，`browser_snapshot` 会新增 `pending_dialogs` 和 `frame_tree` 字段，`browser_dialog` 会与这些字段协同工作。 |
| `clarify` | `clarify` | 当智能体需要进一步澄清信息时，向用户提问。 |
| `code_execution` | `execute_code` | 运行可程序化调用 Hermes 工具的 Python 脚本。 |
| `coding` | 复合工具集（包含 `file` + `terminal` + `search` + `web` + `skills` + `browser` + `todo` + `memory` + `session_search` + `clarify` + `code_execution` + `delegation` + `vision`） | 面向软件开发的工具包，涵盖文件编辑、终端操作、搜索、网页文档处理、技能调用、浏览器操作、任务委托以及代码执行等功能。 |
| `cronjob` | `cronjob` | 安排并管理周期性任务。 |
| `debugging` | 复合工具集（包含 `file` + `terminal` + `web`） | 调试工具包，提供文件操作、进程/终端管理以及网页内容提取与搜索功能。 |
| `delegation` | `delegate_task` | 创建独立的子智能体实例以实现并行处理。 |
| `discord` | `discord` | Discord 的核心文本/嵌入消息/私信操作功能（仅限网关模式）。属于 `hermes-discord` 工具集的一部分。 |
| `discord_admin` | `discord_admin` | Discord 管理功能，包括封禁用户、修改角色权限、管理频道等。同样属于 `hermes-discord` 工具集，要求智能体拥有相应的 Discord 权限。 |
| `feishu_doc` | `feishu_doc_read` | 读取飞书/企业微信文档内容，被飞书文档评论智能回复功能所使用。 |
| `feishu_drive` | `feishu_drive_add_comment`, `feishu_drive_list_comments`, `feishu_drive_list_comment_replies`, `feishu_drive_reply_comment` | 飞书/企业微信云盘评论操作功能，仅限于评论相关智能体使用，不会在 `hermes-cli` 或其他消息平台工具集中提供。 |
| `file` | `patch`, `read_file`, `search_files`, `write_file` | 文件的读取、写入、搜索及编辑功能。 |
| `homeassistant` | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` | 通过 Home Assistant 实现智能家居控制，仅在设置了 `HASS_TOKEN` 后可用。 |
| `computer_use` | `computer_use` | 通过 cua-driver 实现后台桌面控制，不会占用光标或焦点，适用于任何具备工具调用能力的模型，支持 macOS、Windows 和 Linux 系统，要求 `$PATH` 中已安装 `cua-driver`。 |
| `context_engine` | 不固定 | 由当前激活的上下文引擎插件提供的运行时工具（在插件填充内容前为空）。 |
| `image_gen` | `image_generate` | 通过 FAL.ai 实现文本转图像功能，可选支持 OpenAI / xAI 后端。 |
| `video_gen` | `video_generate` | 通过插件注册的后端实现文本转视频及图像转视频功能，可选后端包括 xAI Grok-Imagine、FAL.ai Veo 3.1 / Pixverse v6 / Kling O3。如需为图像添加动画效果，请传入 `image_url` 参数；如需直接生成视频，则无需该参数。 |
| `kanban` | `kanban_block`, `kanban_comment`, `kanban_complete`, `kanban_create`, `kanban_heartbeat`, `kanban_link`, `kanban_list`, `kanban_show`, `kanban_unblock` | 多智能体协调工具，为调度器生成的任务处理节点（类型为 `HERMES_KANBAN_TASK`）以及明确指定使用 `kanban` 工具集的配置文件所使用（`all`/`*` 通配符无法启用此功能）。任务处理节点可标记任务完成、阻塞、发送心跳、添加评论以及创建/关联后续任务；而调度器配置文件还可获得列表展示、解除阻塞等看板管理功能。 |
| `memory` | `memory` | 实现跨会话的持久化内存管理。 |
| `project` | `project_create`, `project_list`, `project_switch` | 创建及切换桌面端的 [项目](../user-guide/cli.md)，即带命名、多文件夹结构的workspace，仅适用于 GUI/桌面会话。 |
| `safe` | `image_generate`, `vision_analyze`, `web_extract`, `web_search`（通过 `includes` 选项启用） | 仅限读取与媒体生成功能，禁止文件写入、终端操作及代码执行。 |
| `search` | `web_search` | 仅支持网页搜索，不包含内容提取功能。 |
| `session_search` | `session_search` | 搜索过往的对话会话记录。 |
| `skills` | `skill_manage`, `skill_view`, `skills_list` | 技能的创建、读取及列表查询功能。 |
| `spotify` | `spotify_albums`, `spotify_devices`, `spotify_library`, `spotify_playback`, `spotify_playlists`, `spotify_queue`, `spotify_search` | 对 Spotify 的原生控制功能，包括播放、队列管理、搜索、播放列表、专辑及音乐库操作，由内置的 `spotify` 插件提供。 |
| `terminal` | `process`, `terminal` | Shell 命令执行及后台进程管理功能。 |
| `todo` | `todo` | 管理当前会话内的任务列表。 |
| `tts` | `text_to_speech` | 生成文本转语音音频。 |
| `vision` | `vision_analyze` | 利用具备视觉处理能力的模型进行图像分析。 |
| `video` | `video_analyze` | 视频分析及理解工具（为可选功能，不在默认工具集中，需通过 `--toolsets` 显式添加）。 |
| `web` | `web_extract`, `web_search` | 网页搜索及页面内容提取功能。 |
| `x_search` | `x_search` | 通过 xAI 内置的 `x_search` Responses 工具搜索 X（Twitter）上的帖子与主题串，默认为关闭状态，需通过 `hermes tools` 打开；仅当配置了 xAI 凭证（SuperGrok OAuth 或 `XAI_API_KEY`）后才会注册对应的架构。 |
| `yuanbao` | `yb_query_group_info`, `yb_query_group_members`, `yb_search_sticker`, `yb_send_dm`, `yb_send_sticker` | 腾讯元宝的私信/群组操作及贴图搜索功能，仅在 `hermes-yuanbao` 环境中可用。 |

## 平台工具集

平台工具集定义了特定部署目标所需的完整工具配置。大多数消息平台使用的工具集与 `hermes-cli` 相同：

| 工具集 | 与 `hermes-cli` 的差异 |
|---------|------------------------|
| `hermes-cli` | 完整的工具集，为交互式 CLI 会话的默认配置，包含文件操作、终端、网页、浏览器、内存、技能、视觉处理、图像生成、任务管理、文本转语音、任务委托、代码执行、定时任务、会话搜索以及澄清功能，同时还包含仅限读取的 `safe` 工具包。 |
| `hermes-acp` | 移除了 `clarify`、`cronjob`、`image_generate`、`text_to_speech` 以及所有四个与 Home Assistant 相关的工具，专注于在集成开发环境中的编程任务。 |
| `hermes-api-server` | 移除了 `clarify` 和 `text_to_speech`，保留其余所有功能，适用于无需用户交互的程序化访问场景。 |
| `hermes-cron` | 与 `hermes-cli` 完全相同。 |
| `hermes-telegram` | 与 `hermes-cli` 完全相同。 |
| `hermes-discord` | 在 `hermes-cli` 的基础上新增了 `discord` 和 `discord_admin` 功能。 |
| `hermes-slack` | 与 `hermes-cli` 完全相同。 |
| `hermes-whatsapp` | 与 `hermes-cli` 完全相同。 |
| `hermes-signal` | 与 `hermes-cli` 完全相同。 |
| `hermes-matrix` | 与 `hermes-cli` 完全相同。 |
| `hermes-mattermost` | 与 `hermes-cli` 完全相同。 |
| `hermes-email` | 与 `hermes-cli` 完全相同。 |
| `hermes-sms` | 与 `hermes-cli` 完全相同。 |
| `hermes-bluebubbles` | 与 `hermes-cli` 完全相同。 |
| `hermes-dingtalk` | 与 `hermes-cli` 完全相同。 |
| `hermes-feishu` | 新增了五个 `feishu_doc_*` / `feishu_drive_*` 工具，仅被文档评论处理功能使用，不会出现在常规聊天适配器中。 |
| `hermes-qqbot` | 与 `hermes-cli` 完全相同。 |
| `hermes-wecom` | 与 `hermes-cli` 完全相同。 |
| `hermes-wecom-callback` | 与 `hermes-cli` 完全相同。 |
| `hermes-weixin` | 与 `hermes-cli` 完全相同。 |
| `hermes-yuanbao` | 在 `hermes-cli` 的基础上新增了五个 `yb_*` 工具，用于私信、群组及贴图操作。 |
| `hermes-homeassistant` | 与 `hermes-cli` 完全相同（Home Assistant 相关工具默认已存在，设置 `HASS_TOKEN` 后即可启用）。 |
| `hermes-webhook` | 与 `hermes-cli` 完全相同。 |
| `hermes-gateway` | 内部网关协调工具集，汇集了所有 `hermes-<platform>` 工具集的功能，用于需要接收来自任意消息源的场景。 |

## 动态工具集

### MCP 服务器工具集

每个已配置的 MCP 服务器都会在运行时生成一个 `mcp-<server>` 工具集。例如，若配置了 `github` MCP 服务器，就会生成一个 `mcp-github` 工具集，其中包含该服务器提供的所有工具。

```yaml
# config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
```

这样即可创建一个 `mcp-github` 工具集，您可以在 `--toolsets` 参数或平台配置中引用它。

### 插件工具集

插件可在初始化阶段通过 `ctx.register_tool()` 方法注册自己的工具集。这些自定义工具集会与内置工具集一同显示，并且可以通过相同的方式进行启用或禁用。

### 自定义工具集

您可以在 `config.yaml` 中定义自定义工具集，从而创建针对特定项目的功能包：

```yaml
toolsets:
  - hermes-cli
custom_toolsets:
  data-science:
    - file
    - terminal
    - code_execution
    - web
    - vision
```

### 通配符

- `all` 或 `*` —— 表示启用所有已注册的工具集（内置工具、动态工具及插件工具）。

部分工具除了需要属于某个工具集外，还需满足额外的可用性检查条件，因此仅通过 `all`/`*` 无法将其启用：

- **能力限制型**工具（如浏览器、`computer_use`、`code_execution`、Feishu、Home Assistant、cronjob）只有在配置了相应的后端环境或凭据要求后才会显示。
- **工作流限制型**工具——即 `kanban` 工具集——属于主动启用模式。`all`/`*` 无法自动开启 kanban 功能，必须明确列出 `kanban`（或者作为由调度器生成的 Worker 且设置了 `HERMES_KANBAN_TASK` 参数）。由于 kanban 工具会修改共享看板状态，因此即使在 `all` 模式下也会默认保持关闭状态。

## 与 `hermes tools` 的关系

`hermes tools` 命令提供了一个基于 curses 的用户界面，可用于按平台单独开启或关闭各类工具。该功能在工具级别运作（比工具集更细致），且设置会保存在 `config.yaml` 文件中。即使某个工具所属的工具集已被启用，若该工具本身被禁用，仍会被过滤掉。

更多信息请参阅：[工具参考](./tools-reference.md)，其中列出了所有单独工具及其参数的完整清单。
