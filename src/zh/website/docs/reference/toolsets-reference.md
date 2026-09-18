---
sidebar_position: 4
title: "Toolsets Reference"
description: "Reference for Hermes core, composite, platform, and dynamic toolsets"
---

# 工具集参考

工具集是由多个工具组成的命名包，用于控制智能体能够执行的功能。它是根据不同平台、会话或任务来配置工具可用性的主要机制。

## 工具集的工作原理

每个工具仅属于一个工具集。当您启用某个工具集后，该工具包中的所有工具都会对智能体可用。工具集共有三种类型：

- **核心型**——由一组相关的工具构成的逻辑单元（例如，`file` 工具集包含 `read_file`、`write_file`、`patch`、`search_files` 等工具）
- **复合型**——为特定场景组合多个核心工具集（例如，`debugging` 工具集汇集了文件操作、终端操作和网页操作工具）
- **平台专用型**——为特定的部署环境提供的完整工具配置（例如，交互式 CLI 会话的默认工具集为 `hermes-cli`）

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

或者，在会话进行中：

```
/tools list
/tools disable browser
/tools enable homeassistant
```

## 核心工具集

| Toolset | Tools | Purpose |
|---------|-------|---------|
| `browser` | `browser_back`, `browser_cdp`, `browser_click`, `browser_console`, `browser_dialog`, `browser_get_images`, `browser_navigate`, `browser_press`, `browser_scroll`, `browser_snapshot`, `browser_type`, `browser_vision`, `web_search` | Core browser automation. Includes `web_search` as a fallback for quick lookups. `browser_cdp` and `browser_dialog` are gated at runtime — registered only when a CDP endpoint is reachable at session start (via `/browser connect`, `browser.cdp_url` config, Browserbase, or Camofox). `browser_dialog` works together with the `pending_dialogs` and `frame_tree` fields that `browser_snapshot` adds when a CDP supervisor is attached. |
| `clarify` | `clarify` | Ask the user a question when the agent needs clarification. |
| `code_execution` | `execute_code` | Run Python scripts that call Hermes tools programmatically. |
| `coding` | composite (`file` + `terminal` + `search` + `web` + `skills` + `browser` + `todo` + `memory` + `session_search` + `clarify` + `code_execution` + `delegation` + `vision`) | Coding-focused bundle for software work: file editing, terminal, search, web docs, skills, browser, delegate, and code execution. |
| `cronjob` | `cronjob` | Schedule and manage recurring tasks. |
| `debugging` | composite (`file` + `terminal` + `web`) | Debug bundle — file, process/terminal, web extract/search. |
| `delegation` | `delegate_task` | Spawn isolated subagent instances for parallel work. |
| `discord` | `discord` | Core Discord text/embed/DM actions (gateway-only). Active on the `hermes-discord` toolset. |
| `discord_admin` | `discord_admin` | Discord moderation (bans, role changes, channel management). Active on the `hermes-discord` toolset; requires the bot to hold the relevant Discord permissions. |
| `feishu_doc` | `feishu_doc_read` | Read Feishu/Lark document content. Used by the Feishu document-comment intelligent-reply handler. |
| `feishu_drive` | `feishu_drive_add_comment`, `feishu_drive_list_comments`, `feishu_drive_list_comment_replies`, `feishu_drive_reply_comment` | Feishu/Lark drive comment operations. Scoped to the comment agent; not exposed on `hermes-cli` or other messaging toolsets. |
| `file` | `patch`, `read_file`, `search_files`, `write_file` | File reading, writing, searching, and editing. |
| `homeassistant` | `ha_call_service`, `ha_get_state`, `ha_list_entities`, `ha_list_services` | Smart home control via Home Assistant. Only available when `HASS_TOKEN` is set. |
| `computer_use` | `computer_use` | Background desktop control via cua-driver — does not steal cursor/focus. Works with any tool-capable model. macOS, Windows, and Linux; requires `cua-driver` on `$PATH`. |
| `context_engine` | (varies) | Runtime tools exposed by the active context-engine plugin (empty until a plugin populates it). |
| `image_gen` | `image_generate` | Text-to-image generation via FAL.ai (with opt-in OpenAI / xAI backends). |
| `video_gen` | `video_generate`, `xai_video_edit`, `xai_video_extend` | Text-to-video and image-to-video via plugin-registered backends (xAI Grok-Imagine, FAL.ai Veo 3.1 / Pixverse v6 / Kling O3). Pass `image_url` to animate an image; omit it for text-to-video. `xai_video_edit` / `xai_video_extend` are provider-specific edit/extend tools, gated on xAI Imagine credentials. |
| `kanban` | `kanban_attach`, `kanban_attach_url`, `kanban_attachments`, `kanban_block`, `kanban_comment`, `kanban_complete`, `kanban_create`, `kanban_heartbeat`, `kanban_link`, `kanban_list`, `kanban_request_changes`, `kanban_request_review`, `kanban_show`, `kanban_unblock` | Multi-agent coordination tools. Registered for dispatcher-spawned task workers (`HERMES_KANBAN_TASK`) and for profiles that explicitly list the `kanban` toolset by name (the `all`/`*` wildcard does **not** enable it). Workers mark tasks done, request first-class review, block, heartbeat, comment, and create/link follow-up tasks; orchestrator profiles additionally get board-routing tools like list/unblock. `delegate_task` children are not Kanban run owners: their schema strips/disables this toolset and runtime guards reject direct board mutations, even if parent `HERMES_KANBAN_*` env vars are present. |
| `memory` | `memory` | Persistent cross-session memory management. |
| `desktop_ui` | `annotate_preview`, `close_preview`, `close_terminal`, `drive_preview`, `focus_pane`, `open_preview`, `react_to_message`, `read_preview`, `read_terminal`, `read_window_below`, `tour` | Affordances that act on the Hermes desktop app itself — read/close the embedded terminal pane, open, read, close, interact with, and annotate the in-app browser, identify the OS window behind the app, reveal a pane, react to a message, run a guided tour (highlight + narrate UI elements in the app or the preview pane). Enabled for sessions whose source is the desktop app, whichever backend it's connected to (local, SSH, URL, or Hermes Cloud). Never present on CLI, TUI, messaging, or cron sessions. |
| `project` | `project_create`, `project_list`, `project_switch` | Create and switch desktop [Projects](../user-guide/cli.md) (named, multi-folder workspaces). GUI / desktop sessions only. |
| `safe` | `image_generate`, `vision_analyze`, `web_extract`, `web_search` (via `includes`) | Read-only research + media generation. No file writes, no terminal, no code execution. |
| `search` | `web_search` | Web search only (without extract). |
| `session_search` | `session_search` | Search past conversation sessions. |
| `skills` | `skill_manage`, `skill_view`, `skills_list` | Skill CRUD and browsing. |
| `spotify` | `spotify_albums`, `spotify_devices`, `spotify_library`, `spotify_playback`, `spotify_playlists`, `spotify_queue`, `spotify_search` | Native Spotify control (playback, queue, search, playlists, albums, library). Registered by the bundled `spotify` plugin. |
| `terminal` | `process`, `terminal` | Shell command execution and background process management. |
| `todo` | `todo` | Task list management within a session. |
| `tts` | `text_to_speech` | Text-to-speech audio generation. |
| `vision` | `vision_analyze` | Image analysis via vision-capable models. |
| `video` | `video_analyze` | Video analysis and understanding tools (opt-in, not in the default toolset — add explicitly via `--toolsets`). |
| `web` | `web_extract`, `web_search` | Web search and page content extraction. |
| `x_search` | `x_search` | Read-only public X discovery via xAI's built-in `x_search` Responses tool. Use the `xurl` skill for authenticated X API reads and account actions. Off by default; opt in via `hermes tools`. Schema only registered when xAI credentials (SuperGrok OAuth or `XAI_API_KEY`) are configured. |
| `yuanbao` | `yb_query_group_info`, `yb_query_group_members`, `yb_search_sticker`, `yb_send_dm`, `yb_send_sticker` | Yuanbao DM/group actions and sticker search. Registered only on `hermes-yuanbao`. |

## 平台工具集

平台工具集用于定义部署目标的完整工具配置。大多数消息传递平台所使用的工具集与 `hermes-cli` 完全相同：

| Toolset | Differences from `hermes-cli` |
|---------|-------------------------------|
| `hermes-cli` | Full toolset — the default for interactive CLI sessions. Includes file, terminal, web, browser, memory, skills, vision, image_gen, todo, tts, delegation, code_execution, cronjob, session_search, clarify, computer_use, Home Assistant, and the kanban tools (all check_fn-gated at runtime). |
| `hermes-acp` | Drops `clarify`, `cronjob`, `image_generate`, `text_to_speech`, `computer_use`, all four Home Assistant tools, and the kanban tools. Focused on coding tasks in IDE context. |
| `hermes-api-server` | Drops `clarify`, `text_to_speech`, `computer_use`, and the kanban tools. Keeps everything else — suitable for programmatic access where user interaction isn't possible. |
| `hermes-cron` | Same as `hermes-cli`. |
| `hermes-telegram` | Same as `hermes-cli`. |
| `hermes-discord` | Adds `discord` and `discord_admin` on top of `hermes-cli`. |
| `hermes-slack` | Same as `hermes-cli`. |
| `hermes-whatsapp` | Same as `hermes-cli`. |
| `hermes-signal` | Same as `hermes-cli`. |
| `hermes-matrix` | Same as `hermes-cli`. |
| `hermes-mattermost` | Same as `hermes-cli`. |
| `hermes-email` | Same as `hermes-cli`. |
| `hermes-sms` | Same as `hermes-cli`. |
| `hermes-bluebubbles` | Same as `hermes-cli`. |
| `hermes-dingtalk` | Same as `hermes-cli`. |
| `hermes-feishu` | Adds the five `feishu_doc_*` / `feishu_drive_*` tools (only used by the document-comment handler, not the regular chat adapter). |
| `hermes-qqbot` | Same as `hermes-cli`. |
| `hermes-wecom` | Same as `hermes-cli`. |
| `hermes-wecom-callback` | Same as `hermes-cli`. |
| `hermes-weixin` | Same as `hermes-cli`. |
| `hermes-yuanbao` | Adds the five `yb_*` tools (DM/group/sticker) on top of `hermes-cli`. |
| `hermes-homeassistant` | Same as `hermes-cli` (the Home Assistant tools are already present by default and activate when `HASS_TOKEN` is set). |
| `hermes-webhook` | Restricted safe subset — only `web_search`, `web_extract`, `vision_analyze`, and `clarify`. Webhook-triggered runs get no terminal, file, or browser access. |
| `hermes-gateway` | Internal gateway orchestrator toolset — union of every `hermes-<platform>` toolset; used when the gateway needs to accept any message source. |

## 动态工具集

### MCP 服务器工具集

每台已配置的 MCP 服务器都会在运行时生成一个 `mcp-<server>` 工具集。例如，如果您配置了 `github` MCP 服务器，系统就会创建一个名为 `mcp-github` 的工具集，其中包含该服务器所提供的所有工具。

```yaml
# config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
```

这样会生成一个名为 `mcp-github` 的工具集，您可以在 `--toolsets` 参数或平台配置中引用它。纯服务器名称（如 `github`）可被用作别名。如果服务器名称与内置工具集的名称相同（如 `homeassistant`、`browser`），则该名称会同时对应内置工具以及该服务器的 `mcp__<server>__*` 工具；两者之间不会产生覆盖关系。

### 插件工具集

插件可在初始化过程中通过 `ctx.register_tool()` 方法注册自己的工具集。这些自定义工具集会与内置工具集一同显示，且启用/禁用的方式也完全相同。

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

部分工具除了需要属于某个工具集外，还需满足额外的可用性检查，因此仅使用 `all`/`*` 无法将其启用：

- **能力限制型**工具（如浏览器、`computer_use`、`code_execution`、Feishu、Home Assistant、cronjob）只有在配置了相应的后端环境或凭据要求后才会显示。
- **工作流限制型**工具——即 `kanban` 工具集——是默认需要手动启用的。`all`/`*` 无法自动启用 `kanban`，必须显式列出 `kanban`（或者作为由调度器生成的工作者且设置了 `HERMES_KANBAN_TASK`）。由于 `kanban` 工具会修改共享看板状态，因此即使在 `all` 模式下也会保持禁用状态。

## 与 `hermes tools` 的关系

`hermes tools` 命令提供了一个基于 curses 的用户界面，可用于按平台单独开启或关闭各类工具。该命令在工具级别进行操作（比工具集更细致），并且设置会保存到 `config.yaml` 文件中。即使某个工具所属的工具集已被启用，若该工具本身被禁用，仍会被过滤掉。

更多信息：请参阅 [工具参考](./tools-reference.md)，了解所有单个工具及其参数的完整列表。
