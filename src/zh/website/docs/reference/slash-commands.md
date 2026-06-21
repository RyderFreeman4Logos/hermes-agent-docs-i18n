---
sidebar_position: 2
title: "Slash Commands Reference"
description: "Complete reference for interactive CLI and messaging slash commands"
---

# 斜杠命令参考

Hermes 提供两种斜杠命令接口，二者均通过 `hermes_cli/commands.py` 中的中央 `COMMAND_REGISTRY` 进行控制：

- **交互式 CLI 斜杠命令**——由 `cli.py` 调用，并从注册表中获取自动补全功能；
- **消息传递型斜杠命令**——由 `gateway/run.py` 调用，帮助文本及平台菜单同样来自该注册表。

已安装的技能也会作为动态斜杠命令在这两种接口中呈现。其中包括像 `/plan` 这样的内置技能，它能打开计划模式，并将 Markdown 格式的计划内容保存到与当前工作空间/后端工作目录相对的 `.hermes/plans/` 文件夹中。

## 权限管理与管理员/用户区分

所有支持按用户设置允许列表的消息平台（Telegram、Discord、Slack、Matrix、Mattermost、Signal 等）都支持两级斜杠命令权限控制：**管理员**可以使用所有已注册的命令，而**普通用户**仅能使用在 `user_allowed_commands` 中列出的命令名称（此外还有始终允许的 `/help` 和 `/whoami` 命令）。你可以在 `~/.hermes/gateway-config.yaml` 文件的 platform 部分的 `extra:` 块中配置 `allow_admin_from` 和 `user_allowed_commands`（以及针对群组的对应配置 `group_allow_admin_from` / `group_user_allowed_commands`）。

具体示例可参考各平台的文档——各平台的结构完全一致：

- [Telegram](../user-guide/messaging/telegram.md#slash-command-access-control)
- [Discord](../user-guide/messaging/discord.md)
- [Slack](../user-guide/messaging/slack.md)
- [Matrix](../user-guide/messaging/matrix.md)
- [Mattermost](../user-guide/messaging/mattermost.md)
- [Signal](../user-guide/messaging/signal.md)

如果某个范围未设置 `allow_admin_from`，则该范围将保持无限制的向后兼容模式——所有允许的用户都可以使用所有命令。

## 交互式 CLI 斜杠命令

在 CLI 中输入 `/` 即可打开自动补全菜单。内置命令不区分大小写。

### 会话管理

| 命令 | 描述 |
|------|------|
| `/new [name]`（别名：/reset） | 启动新会话（生成新的会话 ID 和历史记录）。可选的 `[name]` 参数可用于设置初始会话标题——例如，输入 `/new my-experiment` 可以立即创建一个标题为 `my-experiment` 的新会话，便于后续通过 `/resume` 或 `/sessions` 查找。若要跳过确认弹窗，可添加 `now`、`--yes` 或 `-y` 参数，如 `/reset now`、/new --yes my-experiment`。 |
| `/clear` | 清空屏幕并启动新会话 |
| `/history` | 显示对话历史记录 |
| `/save` | 保存当前对话内容 |
| `/retry` | 重新发送上一条消息给智能体 |
| `/undo` | 删除上一次用户与智能体之间的交互内容 |
| `/title` | 为当前会话设置标题（用法：/title 我的会话名称） |
| `/compress [here [N] \| focus topic]` | 手动压缩对话上下文（清空记忆并生成摘要）。`/compress here [N]` 会保留除最近 N 条交互内容外的所有内容并原样呈现——你可以自行设定压缩边界。指定“聚焦主题”则可缩小完整摘要所包含的内容范围。 |
| `/rollback` | 列出或恢复文件系统检查点（用法：/rollback [编号]） |
| `/snapshot [create\|restore <id>\|prune]`（别名：/snap） | 创建或恢复 Hermes 配置/状态的快照。`create [标签]` 用于保存快照，`restore <id>` 用于恢复到该快照状态，`prune [N]` 用于删除旧快照，不带参数则可列出所有快照。 |
| `/stop` | 终止所有正在运行的后台进程 |
| `/queue <prompt>`（别名：/q） | 将提示语排队，等待下次轮到智能体处理（不会中断当前智能体的响应）。 |
| `/steer <prompt>` | 在当前工具调用之后向智能体插入一条临时备注——不会中断当前流程，也不会触发新的用户轮次。当前工具处理完成后，该文本会追加到上一个工具的响应内容中，从而为智能体提供新上下文，同时不会打断当前的工具调用循环。可用于在任务执行过程中引导智能体的工作方向（例如，在智能体运行测试时要求其“专注于认证模块”）。 |
| `/goal <text>` | 设置一个长期目标，Hermes 会在多轮对话中持续朝着该目标努力——这相当于我们实现的 Ralph 循环。每轮对话结束后，一个辅助判断模型会判定该目标是否已完成；若未完成，Hermes 会自动继续处理。子命令包括：/goal status、/goal pause、/goal resume、/goal clear。默认目标轮次数为 20 轮（由 `goals.max_turns` 控制）；任何真实用户的消息都会中断该循环，而状态信息可通过 `/resume` 恢复。完整使用指南请参阅 [持久化目标](/user-guide/features/goals)。 |
| `/subgoal <text>` | 在当前循环中为已有目标添加用户自定义的判定标准。后续的提示语会原样将所有子目标呈现给智能体，判断模型会在综合所有子目标后给出“已完成”或“继续”的结论——只有当原始目标以及所有子目标都达成时，该目标才会被标记为已完成。子命令包括：/subgoal（列出子目标）、/subgoal remove <N>（删除指定数量的子目标）、/subgoal clear（清除所有子目标）。此命令需在已有 `/goal` 状态下使用。 |
| `/resume [name]` | 恢复之前命名的会话 |
| `/sessions`（TUI 别名：/switch） | 传统 CLI 模式：通过交互式选择器浏览并恢复之前的会话。TUI 模式：打开当前打开的 TUI 会话的实时切换界面。在 TUI 中可使用 `/sessions new` 立即启动另一个实时会话。 |
| `/redraw` | 强制重新绘制整个用户界面（可解决 tmux 调整大小、鼠标选择异常等问题导致的界面错位）。 |
| `/status` | 显示会话相关信息——包括使用的模型、提供方、用户配置文件、会话 ID、工作目录、标题、创建/更新时间戳、令牌总量以及智能体运行状态——随后还会显示一个本地的 **会话摘要** 区块（包含近期用户与智能体的交互次数、工具响应数量、最常用的工具、最近操作的文件、最新的用户提示语以及最新的智能体回复）。该摘要是根据内存中的对话内容在本地计算得出的，不会调用大型语言模型，也不会影响提示语缓存。 |
| `/agents`（别名：/tasks） | 显示当前会话中正在运行的智能体及任务列表。 |
| `/background <prompt>`（别名：/bg、/btw） | 在独立的后台会话中运行提示语。智能体会独立处理你的提示语，而你的当前会话仍可用于其他操作。任务完成后，结果会以面板形式显示。更多详情请参阅 [CLI 后台会话](/user-guide/cli#background-sessions)。 |
| `/branch [name]`（别名：/fork） | 创建当前会话的分支（探索不同的处理路径）。 |
| `/handoff <platform>` | **仅限 CLI 使用。** 将当前会话转移到某个消息平台（Telegram、Discord、Slack、WhatsApp、Signal、Matrix）。网关会立即接管该会话，在支持线程的消息平台上创建新的线程（如 Telegram 的主题、Discord 的文本频道线程、Slack 的消息锚定线程），并将目标平台的会话 ID 与你的 CLI 会话 ID 关联起来，从而实现包含角色信息的完整对话回放。同时系统还会生成一个模拟的用户轮次，让智能体确认自己已在新平台正常工作。操作成功后 CLI 会给出 `/resume` 的提示并正常退出；你可以随时使用 `/resume <标题>` 在本地恢复会话。若在当前轮次中执行此命令则会被拒绝。该功能要求网关正在运行，且目标平台已配置了主频道（可通过目标平台的聊天窗口执行 `/sethome` 命令设置）。更多信息请参阅 [跨平台会话转移](/user-guide/sessions#cross-platform-handoff)。 |

### 配置管理

| 命令 | 描述 |
|------|------|
| `/config` | 显示当前配置信息 |
| `/model [model-name]` | 显示或更改当前使用的模型。支持以下命令：/model claude-sonnet-4、/model provider:model（切换提供方）、/model custom:model（自定义端点）、/model custom:name:model（命名自定义提供方）、/model custom（根据端点自动检测模型），以及用户自定义的别名（/model fav、/model grok——详见 [自定义模型别名](#custom-model-aliases)）。使用 `--global` 参数可将更改永久保存到 config.yaml 文件中。**注意：** /model 命令仅能在已配置的提供方之间切换。若要添加新的提供方，需先退出当前会话，再在终端中运行 `hermes model` 命令。 |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | 切换 OpenAI/Codex 模型所使用的可选 [Codex 应用服务器运行时](../user-guide/features/codex-app-server-runtime)。默认值为 `auto`，此时会使用 Hermes 的标准聊天补全功能；设置为 `codex_app_server` 后，会将轮次交给 `codex app-server` 子进程来处理原生 shell 命令、apply_patch 功能、ChatGPT 订阅认证以及已迁移的 Codex 插件。此设置会在下次会话中生效。 |
| `/personality` | 设置预定义的性格模式 |
| `/verbose` | 切换工具处理进度的显示方式：关闭 → 新消息时显示 → 显示所有进度 → 详细显示。也可通过配置为 [消息传递场景启用](#notes) 此功能。 |
| `/fast [normal\|fast\|status]` | 切换快速模式——相当于 OpenAI 的优先处理模式或 Anthropic 的快速模式。可选值包括：normal、fast、status。 |
| `/reasoning` | 管理推理强度及显示方式（用法：/reasoning [level\|show\|hide]） |
| `/skin` | 显示或更改界面皮肤/主题 |
| `/statusbar`（别名：/sb） | 切换上下文/模型状态栏的显示与隐藏 |
| `/voice [on\|off\|tts\|status]` | 切换 CLI 的语音模式及语音播放功能。录音时使用的按键为 `voice.record_key`（默认为 `Ctrl+B`）。 |
| `/yolo` | 切换 YOLO 模式——跳过所有危险命令的审批提示。 |
| `/footer [on\|off\|status]` | 切换最终回复中是否显示网关运行时元数据页脚（包含使用的模型、上下文占比及当前工作目录信息）。 |
| `/busy [queue\|steer\|interrupt\|status]` | 仅限 CLI 使用：控制在 Hermes 处理任务时按回车键的默认行为——将新消息排队、在当前轮次中插入临时指令，或立即中断当前操作。 |
| `/indicator [kaomoji\|emoji\|unicode\|ascii]` | 仅限 CLI 使用：选择 TUI 中的忙碌状态指示器样式。 |

### 工具与技能| 命令 | 描述 |
|------|------|
| `/tools [list\|disable\|enable] [name...]` | 管理工具：列出可用工具，或为当前会话禁用/启用特定工具。禁用工具会将其从智能体的工具集中移除，并触发会话重置。 |
| `/toolsets` | 列出所有可用的工具集 |
| `/browser [connect\|disconnect\|status]` | 管理本地的 Chromium 系列 CDP 连接。`connect` 会将浏览器工具连接到正在运行的 Chrome、Brave、Chromium 或 Edge 实例（默认地址：`http://127.0.0.1:9222`）。`disconnect` 用于断开连接。`status` 可查看当前连接状态。若未检测到调试器，系统会自动启动支持的 Chromium 系列浏览器。 |
| `/skills` | 从在线注册表中搜索、安装、查看或管理技能。同时也可用于查看技能写入审批流程的相关信息：`/skills pending`、`/skills diff <id>`、`/skills approve <id>`、`/skills reject <id>`、`/skills approval on\|off`。详见 [智能体技能写入审批机制](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval)。 |
| `/memory [pending\|approve\|reject\|approval]` | 查看由写入审批机制（`memory.write_approval`）暂存的待处理内存写入记录，并切换该审批状态。详见 [内存写入控制](/user-guide/features/memory#controlling-memory-writes-write_approval)。 |
| `/bundles` | 列出已配置的技能包——即通过 `/<name>` 这种斜杠别名一次性预加载多个技能的配置。可在 `~/.hermes/config.yaml` 文件的 `bundles:` 部分进行配置。详见 [技能包](/user-guide/features/skills#skill-bundles)。 |
| `/cron` | 管理定时任务（列出、添加/创建、编辑、暂停、恢复、运行、删除） |
| `/suggestions [accept\|dismiss N\|catalog\|clear]`（别名：`/suggest`） | 查看系统推荐的自动化脚本。使用 `/suggestions` 可列出待处理的建议，`/suggestions accept <id>` 可创建所推荐的自动化脚本，`/suggestions dismiss <id>` 可拒绝某项建议，`/suggestions catalog` 可添加精选的入门级自动化脚本，`/suggestions clear` 可清除已处理的建议记录。被采纳的自动化脚本会以当前界面作为执行起点。 |
| `/blueprint [name] [slot=value ...]`（别名：`/bp`） | 根据蓝图模板创建自动化脚本。仅输入 `/blueprint` 可查看所有可用蓝图；`/blueprint <name>` 会在下一个智能体响应轮次启动引导式字段填充流程；`/blueprint <name> slot=value ...` 可直接创建自动化脚本。 |
| `/curator` | 在后台维护技能——支持执行 `status`、`run`、`pin`、`archive` 等操作。详见 [Curator 功能](/user-guide/features/curator)。 |
| `/kanban <action>` | 无需离开聊天界面即可操作多项目、多角色的协作看板。完整的 `/hermes kanban` 命令集如下：`/kanban list`、`/kanban show t_abc`、`/kanban create "标题" --assignee X`、`/kanban comment t_abc "文本"`、`/kanban unblock t_abc`、`/kanban dispatch` 等。还支持多看板管理：`/kanban boards list`、`/kanban boards create <slug>`、`/kanban boards switch <slug>`、`/kanban --board <slug> <action>`。详见 [Kanban 斜杠命令](/user-guide/features/kanban#kanban-slash-command)。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 从 `config.yaml` 文件重新加载 MCP 服务器配置 |
| `/reload-skills`（别名：`/reload_skills`） | 重新扫描 `~/.hermes/skills/` 目录，检测是否有新安装或已移除的技能 |
| `/reload` | 将 `.env` 变量重新加载到当前运行会话中（无需重启即可获取新的 API 密钥） |
| `/plugins` | 列出已安装的插件及其状态 |

### 信息查询命令

| 命令 | 描述 |
|------|------|
| `/help` | 显示此帮助信息 |
| `/version` | 显示 Hermes Agent 的版本、构建编号及运行环境信息 |
| `/usage` | 显示令牌使用情况、费用明细、会话时长；若当前使用的服务提供商支持，还会显示 **账户限额** 信息，包括从提供商 API 实时获取的剩余配额/积分/套餐使用情况 |
| `/credits` | 显示您的 Nous 积分余额及充值链接 |
| `/billing` | 用于 Nous 的命令行终端计费功能——可查看余额、购买积分，以及管理自动续费/月度限额设置 |
| `/insights` | 显示过去 30 天内的使用情况分析数据 |
| `/platforms`（别名：`/gateway`） | 显示网关/消息平台的状态（仅提供命令行概览视图） |
| `/paste` | 上传剪贴板中的内容 |
| `/copy [number]` | 将助手的最近一次回复复制到剪贴板（可指定数字获取倒数第 N 次回复）。此功能仅支持在命令行中使用 |
| `/image <path>` | 上传本地图片文件，以便在后续提示中使用 |
| `/debug` | 上传调试报告（包含系统信息及日志），并生成可分享的链接。该功能在消息交互中也可用 |
| `/profile` | 显示当前激活的配置文件名称及对应的主目录路径 |
| `/gquota` | 显示 Google Gemini Code Assist 的配额使用情况，并以进度条形式展示进度（仅当 `google-gemini-cli` 服务提供商处于激活状态时可用） |

### 退出命令

| 命令 | 描述 |
|------|------|
| `/quit` | 退出命令行界面（也可使用 `/exit`） |

### 动态斜杠命令

| 命令 | 描述 |
|------|------|
| `/<skill-name>` | 将任何已安装的技能作为按需调用的命令使用。例如：`/gif-search`、`/github-pr-workflow`、`/excalidraw` |
| `/skills ...` | 从注册表及官方可选技能目录中搜索、浏览、查看、安装、审计、发布及配置各类技能 |

### 快速命令

用户自定义的快速命令可将简短的斜杠命令映射为 shell 命令或另一条斜杠命令。可在 `~/.hermes/config.yaml` 文件中进行配置：

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  deploy:
    type: exec
    command: scripts/deploy.sh
  inbox:
    type: alias
    target: /gmail unread
```

接着在 CLI 或消息平台中输入 `/status`、`/deploy` 或 `/inbox`。这些快捷命令会在指令发送时立即被解析，因此可能不会出现在所有的内置自动补全/帮助列表中。

仅包含字符串的提示语无法作为快捷命令使用。较长且可重复使用的提示语应放入某个技能中，或者使用 `type: alias` 指向现有的斜杠命令。

### 自定义模型别名

为常用的模型定义自定义简称，之后便可通过 CLI 或任何消息平台中的 `/model <alias>` 命令来调用它们。无论是在会话级（默认）模式还是使用 `--global` 参数的模式下，这些别名都能以相同方式生效。

系统支持两种配置格式：

**完整格式**——指定确切的模型、提供方，以及可选的基础 URL。可将该配置放入 `~/.hermes/config.yaml` 文件中：

```yaml
model_aliases:
  fav:
    model: claude-sonnet-4.6
    provider: anthropic
  grok:
    model: grok-4
    provider: x-ai
  ollama-qwen:
    model: qwen3-coder:30b
    provider: custom
    base_url: http://localhost:11434/v1
```

**简写形式**——将 `provider/model` 组合为一条字符串。无需编辑 YAML 即可在命令行中直接设置：

```bash
hermes config set model.aliases.fav anthropic/claude-opus-4.6
hermes config set model.aliases.grok x-ai/grok-4
```

随后在聊天界面中：

```
/model fav            # session-only
/model grok --global  # also persists current-model change to config.yaml
```

用户自定义别名会优先于内置简称，因此将别名命名为 `sonnet`、`kimi`、`opus` 等即可覆盖内置简称。别名名称不区分大小写。

### 别名解析

命令支持前缀匹配：输入 `/h` 会对应 `/help`，输入 `/mod` 会对应 `/model`。当某个前缀存在歧义（可匹配多个命令）时，注册顺序中第一个匹配的命令优先生效。完整命令名称及已注册的别名始终优先于前缀匹配结果。

## 消息传递斜杠命令

消息网关在 Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant 以及 Teams 聊天中支持以下内置命令：

| 命令 | 描述 |
|------|------|
| `/start` | 平台协议命令。许多聊天平台（如 Telegram、Discord 等）会在用户首次与机器人对话时自动发送 `/start`。Hermes 会默默响应此请求——不会返回机器人回复，也不会消耗会话次数——因此初次交互无需浪费轮次。您也可以主动发送该命令以确认网关可访问。 |
| `/new` | 开始新的对话。 |
| `/reset` | 重置对话历史记录。 |
| `/status` | 显示会话信息，随后是本地的**会话摘要**板块（包括最近的轮次数、最常使用的工具、处理过的文件以及最新的提示词与回复）。 |
| `/stop` | 终止所有正在运行的后台进程，并中断当前正在工作的机器人。 |
| `/model [provider:model]` | 显示或更改模型。支持切换提供商（如 `/model zai:glm-5`）、自定义端点（如 `/model custom:model`）、命名自定义提供商（如 `/model custom:local:qwen`）、自动检测（如 `/model custom`）以及用户自定义别名（如 `/model fav`、`/model grok`——详见[自定义模型别名](#custom-model-aliases)）。使用 `--global` 可将更改持久化到 `config.yaml` 中。**注意：** `/model` 仅能在已配置的提供商之间切换。若要添加新提供商或设置 API 密钥，请在终端（聊天会话之外）中使用 `hermes model` 命令。 |
| `/codex-runtime [auto\|codex_app_server\|on\|off]` | 切换可选的[Codex 应用服务器运行时](../user-guide/features/codex-app-server-runtime)。该设置会保存到 `config.yaml` 中的 `model.openai_runtime` 字段，并清除缓存中的机器人实例，以便下一条消息能使用新的运行时。更改将在下次会话中生效。 |
| `/personality [name]` | 为当前会话设置个性特征叠加层。 |
| `/fast [normal\|fast\|status]` | 切换快速模式——即 OpenAI 的优先处理模式或 Anthropic 的快速模式。 |
| `/retry` | 重新发送上一条消息。 |
| `/undo` | 删除上一次的用户与机器人交互记录。 |
| `/sethome`（别名：`/set-home`） | 将当前聊天标记为平台上的主频道，用于后续消息发送。 |
| `/compress [here [N] \| focus topic]` | 手动压缩对话上下文。`/compress here [N]` 会保留最近的 N 条交互记录（默认为 2 条）的原文内容，并对其余内容进行总结。指定关注主题可进一步缩小完整总结所保留的内容范围。 |
| `/topic [off\|help\|session-id]` | **仅适用于 Telegram 私信。**用于管理用户自定义的多会话主题模式。`/topic` 可启用该模式或查看其状态；`/topic off` 可禁用该模式并清除所有绑定；`/topic help` 可查看使用方法；在已有主题模式下输入 `/topic <session-id>` 可恢复之前的会话。详见[多会话私信模式](/user-guide/messaging/telegram#multi-session-dm-mode-topic)。 |
| `/title [name]` | 设置或显示会话标题。 |
| `/resume [name]` | 恢复之前命名的会话。 |
| `/usage` | 显示令牌使用情况、预估成本构成（输入/输出）、上下文窗口状态、会话时长，以及——若当前提供商支持——一个**账户限额**板块，其中会实时显示从提供商 API 获取的剩余配额/积分。 |
| `/credits` | 显示您的 Nous 积分余额，并提供充值链接，点击后可打开浏览器中的计费页面。 |
| `/insights [days]` | 显示使用情况分析数据。 |
| `/reasoning [level\|show\|hide]` | 更改推理强度或切换推理结果的显示方式。 |
| `/voice [on\|off\|tts\|join\|channel\|leave\|status]` | 控制聊天中的语音回复功能。`join`/`channel`/`leave` 用于管理 Discord 的语音频道模式。 |
| `/rollback [number]` | 列出或恢复文件系统检查点。 |
| `/background <prompt>` | 在独立的后台会话中运行某个提示词。任务完成后，结果会返回到同一聊天窗口。详见[消息传递后台会话](/user-guide/messaging/#background-sessions)。 |
| `/queue <prompt>`（别名：`/q`） | 将某个提示词排队，等待在当前轮次之后处理，而不会中断当前正在处理的任务。 |
| `/steer <prompt>` | 在下一次工具调用之后插入一条消息，且不会中断当前流程——模型会在下一次迭代时处理该消息，而非视为新的轮次。 |
| `/goal <text>` | 设置一个长期目标，Hermes 会在多轮对话中持续努力实现该目标——这相当于我们实现的 Ralph 循环。每次轮次结束后，会有一个判断模型进行检查；如果目标尚未完成，Hermes 会自动继续尝试，直到目标达成、您暂停/清除该目标，或达到轮次预算上限（默认为 20）。子命令包括：`/goal status`、`/goal pause`、`/goal resume`、`/goal clear`。在机器人运行过程中可安全地使用这些子命令来查看状态、暂停或清除目标；若要设置新目标，则需先执行 `/stop`。详见[持久目标](/user-guide/features/goals)。 |
| `/footer [on\|off\|status]` | 切换最终回复中是否显示运行时元数据页脚（包含模型名称、上下文占比及当前工作目录等信息）。 |
| `/curator [status\|run\|pin\|archive]` | 控制后台技能的维护操作。 |
| `/suggestions [accept\|dismiss N\|catalog\|clear]` | 直接在聊天中查看建议的自动化脚本。`/suggestions` 可列出待处理的建议，`catalog` 可添加精选的入门级自动化脚本，`clear` 可清除已处理的建议记录。被接受的建议会将当前聊天/线程设为任务交付的起始点。 |
| `/blueprint [name] [slot=value ...]` | 浏览 Cron 蓝图，开始引导式地填写参数，或直接创建蓝图任务。直接创建的任务结果会返回到当前的聊天/线程中。 |
| `/memory [pending\|approve\|reject\|approval]` | 查看由写入审批机制（`memory.write_approval`）暂存的待处理内存写入记录——可直接在聊天中批准或拒绝它们——同时可通过 `/memory approval on\|off` 切换该审批机制的开启状态。详见[控制内存写入](/user-guide/features/memory#controlling-memory-writes-write_approval)。 |
| `/skills [pending\|approve\|reject\|diff\|approval]` | 查看由写入审批机制（`skills.write_approval`）暂存的待处理**技能**写入记录。每条待处理的写入记录都会以一行简短摘要的形式显示；在聊天界面中 `/skills diff <id>` 的显示内容会被截断——完整差异信息可在 CLI 或 `~/.hermes/pending/skills/<id>.json` 文件中查看。该功能仅在审批机制开启或仍有待处理写入记录时才会显示；搜索/安装功能仍仅通过 CLI 实现。 |
| `/kanban <action>` | 通过聊天界面操作多角色、多项目的协作看板——其参数形式与 CLI 完全一致。由于绕过了正在运行的机器人限制，因此诸如 `/kanban unblock t_abc`、`/kanban comment t_abc "…"`、`/kanban list --mine`、`/kanban boards switch <slug>` 等命令都可在当前轮次中直接使用。`/kanban create …` 会自动将发起聊天的渠道订阅到新任务的终端事件中。详见[看板斜杠命令](/user-guide/features/kanban#kanban-slash-command)。 |
| `/platform <list\|pause\|resume> [name]` | 直接在聊天界面操作正在运行的网关平台。`/platform list` 可显示所有适配器及其状态（运行中、因故障暂停、手动暂停）；`/platform pause <name>` 会停止向该适配器发送新消息，但不会卸载它；`/platform resume <name>` 会重新启用该适配器，并在上游服务恢复正常后解除断路器保护。 |
| `/reload-mcp`（别名：`/reload_mcp`） | 根据配置文件重新加载 MCP 服务器。 |
| `/yolo` | 切换 YOLO 模式——跳过所有危险命令的审批提示。 |
| `/commands [page]` | 分页浏览所有命令和技能。 |
| `/approve [session\|always]` | 批准并执行某个待处理的危险命令。`session` 仅针对当前会话进行批准；`always` 会将该命令加入永久允许列表。 |
| `/deny` | 拒绝某个待处理的危险命令。 |
| `/update` | 将 Hermes Agent 更新到最新版本。 |
| `/restart` | 在终止所有正在运行的任务后，优雅地重启网关。当网关重新上线后，它会向请求者的聊天/线程发送确认信息。 |
| `/debug` | 上传调试报告（包含系统信息及日志），并获取可分享的链接。 |
| `/help` | 显示消息传递相关的帮助信息。 |
| `/<skill-name>` | 按名称调用任何已安装的技能。 |

## 备注

- `/skin`、`/snapshot`、`/gquota`、`/reload`、`/tools`、`/toolsets`、`/browser`、`/config`、`/cron`、`/platforms`、`/paste`、`/image`、`/statusbar`、`/plugins`、`/busy`、`/indicator`、`/redraw`、`/clear`、`/history`、`/save`、`/copy`、`/handoff`、`/billing` 以及 `/quit` 均为**仅适用于 CLI**的命令。  
- `/skills` **仅用于在 CLI 中搜索/浏览/安装**；其写入审批相关的子命令（`pending`、`approve`、`reject`、`diff`、`approval`）在 `skills.write_approval` 机制开启时，也可在消息传递平台中使用。`/memory` 命令则在这两种场景下均有效。  
- `/verbose` 默认**仅适用于 CLI**，但若在 `config.yaml` 中设置 `display.tool_progress_command: true`，则可在消息传递平台上启用该功能。启用后，它会循环切换 `display.tool_progress` 的显示模式，并将设置保存到配置文件中。  
- `/sethome`、`/update`、`/restart`、`/approve`、`/deny`、`/topic`、`/platform` 以及 `/commands` 均为**仅适用于消息传递平台**的命令。  
- `/status`、`/version`、`/background`、`/queue`、`/steer`、`/voice`、`/reload-mcp`、`/reload-skills`、`/rollback`、`/debug`、`/fast`、`/footer`、`/curator`、`/kanban`、`/credits`、`/suggestions`、`/blueprint`、`/sessions` 以及 `/yolo` 命令在**CLI 和消息传递网关**中均可用。  
- `/voice join`、`/voice channel` 以及 `/voice leave` 命令仅在 Discord 中有意义。  
- 在 TUI 界面中，`/sessions` 会显示当前 TUI 进程中的活跃会话。若需查看已保存或已关闭的对话记录，请使用 `/resume [name]` 或 `hermes --tui --resume <id-or-title>` 命令。  

## 破坏性命令的确认提示

在运行那些会丢弃未保存会话状态的斜杠命令之前，CLI 会显示确认提示。目前属于破坏性命令的包括：

| 命令 | 会删除的内容 |
|------|--------------|
| `/clear` | 清空屏幕并开始新的会话——当前的会话 ID 及内存中的历史记录都会被清除。 |
| `/new` / `/reset` | 开始新的会话（新的会话 ID + 空的历史记录）。 |
| `/undo` | 从历史记录中删除上一次用户与机器人的交互内容。 |
| `/exit --delete` / `/quit --delete` | 退出程序，并**永久删除**当前会话的 SQLite 历史记录及磁盘上的对话记录。 |

对于上述每条命令，CLI 都会弹出三选一的确认模态框：**仅本次批准**（本次执行该命令，但不会将此次操作记录为永久允许），**始终批准**（本次执行并设置 `approvals.destructive_slash_confirm: false`，以便后续的破坏性命令无需再次提示），或**取消**。**直接跳过提示**：在命令后附加 `now`、`--yes` 或 `-y`，即可一次性绕过确认弹窗——例如 `/reset now`、`/new --yes my-session`、`/clear -y`、`/undo -y`。当终端无法正确显示该确认弹窗时（有关 Windows PowerShell 的问题可参见 [issue #30768](https://github.com/NousResearch/hermes-agent/issues/30768)），或需要在脚本中调用 CLI 时，此功能尤为实用。

如需全局禁用这些确认提示，可在 `~/.hermes/config.yaml` 中将 `approvals.destructive_slash_confirm` 的值设置为 `false`；若要重新启用，则将其改回 `true`。相关详细信息请参阅 [安全机制——破坏性斜杠命令的确认流程](../user-guide/security.md#dangerous-command-approval)。
