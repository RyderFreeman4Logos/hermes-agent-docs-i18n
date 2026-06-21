---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.2.0
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent 是 Nous Research 开发的开源 AI 智能体框架，可在终端、消息平台及集成开发环境（IDE）中运行。它与 Claude Code（Anthropic）、Codex（OpenAI）、OpenClaw 属于同一类别——这类自主编程与任务执行型智能体通过调用工具与用户的系统进行交互。Hermes 能与各类大语言模型提供商配合使用（包括 OpenRouter、Anthropic、OpenAI、DeepSeek、本地模型以及另外15种以上选项），并在 Linux、macOS 和 WSL 环境中运行。

Hermes 的独特优势：

- **通过技能实现自我提升**——Hermes 能从经验中学习，将可重复使用的操作流程保存为“技能”。当它解决复杂问题、发现新的工作流程或得到纠正后，会将这些知识以技能文档的形式保存下来，供后续会话调用。随着时间的积累，这些技能会让智能体更擅长处理用户的特定任务及适应相应环境。
- **跨会话持久记忆**——能够记住用户身份、偏好设置、环境详情以及以往的经验教训。通过可插拔的记忆后端（内置选项、Honcho、Mem0 等），用户可自行决定记忆的存储方式。
- **多平台接入能力**——同一个智能体可在 Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Email 以及另外10多种平台上运行，不仅能进行聊天，还能完全访问系统工具。
- **与模型提供商无关**——在任务执行过程中可随时更换模型和提供商，而无需调整其他配置。凭证池会自动在多个 API 密钥之间切换。
- **多实例配置功能**——支持运行多个独立的 Hermes 实例，每个实例拥有独立的配置、会话、技能和记忆数据。
- **高度可扩展**——支持插件、MCP 服务器、自定义工具、Webhook 触发器、定时任务以及完整的 Python 生态系统。

人们将 Hermes 应用于软件开发、科学研究、系统管理、数据分析、内容创作、家庭自动化等领域，凡是能从具备持久上下文和完整系统访问权限的 AI 智能体中受益的场景，都能用到它。

**本技能旨在帮助您高效使用 Hermes Agent**——涵盖其设置安装、功能配置、启动额外智能体实例、故障排查、查找相关命令与设置，以及在需要扩展或贡献代码时理解系统运作原理等内容。

**文档链接：** https://hermes-agent.nousresearch.com/docs/

## 范围与验证说明

本技能仅为简明的操作指南，并非所有 Hermes 功能的完整权威参考。如果某项功能、命令或设置未在此提及，也请勿直接认为其不存在。在给出否定答复之前，请务必查看官方仓库及完整文档。

推荐的验证来源包括：

- 命令行工具：`hermes --help`、`hermes <command> --help` 以及 `hermes_cli/main.py`
- 用户文档：https://hermes-agent.nousresearch.com/docs/
- 源代码仓库：https://github.com/NousResearch/hermes-agent

## 快速入门

```bash
# Install
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

## CLI 参考手册

### 全局标志位

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

没有子命令的默认值为 `chat`。

### 聊天功能

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### 配置

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes auth                 Interactive credential manager
hermes auth add PROVIDER    Add OAuth or API-key credential (e.g. nous, openai-codex, qwen-oauth)
hermes auth list            List stored credentials
hermes auth remove PROVIDER Remove a stored credential
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### 工具与技能

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (ID can be a hub identifier OR a direct https://…/SKILL.md URL; pass --name to override when frontmatter has no name)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP 服务器

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

内置的MCP客户端如何连接服务器（stdio/HTTP）并自动发现其工具，再将这些工具作为一等工具提供；此外还支持通过目录安装功能（`hermes mcp install <name>`）：`skill_view(name="hermes-agent", file_path="references/native-mcp.md")`。

### 网关（消息平台）

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

支持的平台：Telegram、Discord、Slack、WhatsApp、Signal、电子邮件、短信、Matrix、Mattermost、Home Assistant、钉钉、飞书、企业微信、BlueBubbles（iMessage）、微信，以及 API 服务器和 Webhooks。Open WebUI 通过 API 服务器适配器进行连接。

平台文档：https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### 会话

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### 定时任务

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks 接口

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

完整配置、路由设置、载荷模板化，以及基于事件的智能体运行模式：`skill_view(name="hermes-agent", file_path="references/webhooks.md")`。

### 配置文件

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### 凭证池

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### 其他

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

## 斜杠命令（会话内使用）

在交互式聊天会话中输入这些命令。新的命令会频繁添加；如果下方内容显得过时，可在会话中输入 `/help` 以获取最新列表，或查看[实时斜杠命令参考文档](https://hermes-agent.nousresearch.com/docs/reference/slash-commands)。官方的命令注册表位于 `hermes_cli/commands.py` —— 所有的使用方（自动补全功能、Telegram 菜单、Slack 映射以及 `/help` 命令）均以此为依据。

### 会话控制
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/snapshot [sub]      Create or restore state snapshots of Hermes config/state (CLI)
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/steer <prompt>      Inject a message after the next tool call without interrupting
/agents (/tasks)     Show active agents and running tasks
/resume [name]       Resume a named session
/goal [text|sub]     Set a standing goal Hermes works on across turns until achieved
                     (subcommands: status, pause, resume, clear)
/redraw              Force a full UI repaint (CLI)
```

### 配置
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/busy [sub]          Control what Enter does while Hermes is working (CLI)
                     (subcommands: queue, steer, interrupt, status)
/indicator [style]   Pick the TUI busy-indicator style (CLI)
                     (styles: kaomoji, emoji, unicode, ascii)
/footer [on|off]     Toggle gateway runtime-metadata footer on final replies
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### 工具与技能
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/reload-skills       Re-scan ~/.hermes/skills/ for added/removed skills
/reload              Reload .env variables into the running session (CLI)
/reload-mcp          Reload MCP servers
/cron                Manage cron jobs (CLI)
/curator [sub]       Background skill maintenance (status, run, pin, archive, …)
/kanban [sub]        Multi-profile collaboration board (tasks, links, comments)
/plugins             List plugins (CLI)
```

### 网关
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/topic [sub]         Enable or inspect Telegram DM topic sessions (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### 实用工具
```
/branch (/fork)      Branch the current session
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/copy [N]            Copy the last assistant response to clipboard (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### 信息
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/gquota              Show Google Gemini Code Assist quota usage (CLI)
/status              Session info (gateway)
/profile             Active profile info
/debug               Upload debug report (system info + logs) and get shareable links
```

### 退出
```
/quit (/exit, /q)    Exit CLI
```

## 主要路径与配置

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets (under $HERMES_HOME if set)
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Gateway routing index, request dumps, *.jsonl transcripts (and optional per-session JSON snapshots when sessions.write_json_snapshots: true)
~/.hermes/state.db          Canonical session store (SQLite + FTS5)
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

配置文件采用相同的结构，存储路径为 `~/.hermes/profiles/<name>/`。

### 配置章节

可通过 `hermes config edit` 或 `hermes config set section.key value` 命令进行编辑。

| 章节 | 可配置选项 |
|---------|-------------|
| `model` | `default`、`provider`、`base_url`、`api_key`、`context_length` |
| `agent` | `max_turns`（90）、`tool_use_enforcement` |
| `terminal` | `backend`（local/docker/ssh/modal）、`cwd`、`timeout`（180） |
| `compression` | `enabled`、`threshold`（0.50）、`target_ratio`（0.20） |
| `display` | `skin`、`tool_progress`、`show_reasoning`、`show_cost` |
| `stt` | `enabled`、`provider`（local/groq/openai/mistral） |
| `tts` | `provider`（edge/elevenlabs/openai/minimax/mistral/neutts） |
| `memory` | `memory_enabled`、`user_profile_enabled`、`provider` |
| `security` | `tirith_enabled`、`website_blocklist` |
| `delegation` | `model`、`provider`、`base_url`、`api_key`、`max_iterations`（50）、`reasoning_effort` |
| `checkpoints` | `enabled`、`max_snapshots`（50） |

完整配置参考：https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### 提供商支持

目前支持20多种提供商，可通过 `hermes model` 或 `hermes setup` 命令进行配置。

| 提供商 | 认证方式 | 对应环境变量 |
|----------|------|-------------|
| OpenRouter | API密钥 | `OPENROUTER_API_KEY` |
| Anthropic | API密钥 | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth认证 | `hermes auth` |
| OpenAI Codex | OAuth认证 | `hermes auth` |
| GitHub Copilot | 令牌 | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API密钥 | `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` |
| DeepSeek | API密钥 | `DEEPSEEK_API_KEY` |
| xAI / Grok | API密钥 | `XAI_API_KEY` |
| Hugging Face | 令牌 | `HF_TOKEN` |
| Z.AI / GLM | API密钥 | `GLM_API_KEY` |
| MiniMax | API密钥 | `MINIMAX_API_KEY` |
| MiniMax CN | API密钥 | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API密钥 | `KIMI_API_KEY` |
| Alibaba / DashScope | API密钥 | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API密钥 | `XIAOMI_API_KEY` |
| Kilo Code | API密钥 | `KILOCODE_API_KEY` |
| OpenCode Zen | API密钥 | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API密钥 | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth认证 | `hermes auth add qwen-oauth` |
| 自定义接口端点 | 配置文件 | 在 config.yaml 中设置 `model.base_url` 和 `model.api_key` |
| GitHub Copilot ACP | 外部工具 | `COPILOT_CLI_PATH` 或 Copilot CLI |

完整提供商文档：https://hermes-agent.nousresearch.com/docs/integrations/providers

### 工具集

可通过 `hermes tools`（交互式命令）或 `hermes tools enable/disable NAME` 命令启用/禁用工具集。

| 工具集 | 功能说明 |
|---------|----------|
| `web` | 网页搜索与内容提取 |
| `search` | 仅支持网页搜索（属于 `web` 的子集） |
| `browser` | 浏览器自动化操作（支持 Browserbase、Camofox 或本地 Chromium） |
| `terminal` | Shell命令执行与进程管理 |
| `file` | 文件读写、搜索与修补操作 |
| `code_execution` | 沙箱环境下的 Python 代码执行 |
| `vision` | 图像分析功能 |
| `image_gen` | AI图像生成功能 |
| `video` | 视频分析与生成功能 |
| `tts` | 文本转语音功能 |
| `skills` | 技能浏览与管理工作 |
| `memory` | 跨会话持久化内存功能 |
| `session_search` | 搜索历史对话内容 |
| `delegation` | 向子智能体分配任务 |
| `cronjob` | 定时任务管理功能 |
| `clarify` | 向用户提问以获取更多信息 |
| `messaging` | 跨平台消息发送功能 |
| `todo` | 会话内任务规划与跟踪功能 |
| `kanban` | 多智能体工作队列工具（仅对工作节点开放） |
| `debugging` | 额外的调试与检查工具（默认关闭） |
| `safe` | 为受限会话设计的简易、低风险工具集 |
| `spotify` | Spotify 播放与播放列表控制功能 |
| `homeassistant` | 智能家居控制功能（默认关闭） |
| `discord` | Discord 集成工具 |
| `discord_admin` | Discord 管理与审核工具 |
| `feishu_doc` | Feishu（Lark）文档处理工具 |
| `feishu_drive` | Feishu（Lark）云盘操作工具 |
| `yuanbao` | Yuanbao 集成工具 |
| `rl` | 强化学习相关工具（默认关闭） |
| `moa` | 混合智能体技术相关工具（默认关闭） |

所有工具集的完整列表存储在 `toolsets.py` 文件中的 `TOOLSETS` 字典中；`_HERMES_CORE_TOOLS` 是大多数平台默认使用的工具组合。

对工具的更改需通过 `/reset` 命令启动新会话后才会生效。为保留提示词缓存，这些更改不会在当前对话进行中生效。

---

## 项目上下文文件

Hermes 会从工作目录读取上下文文件，将项目级配置指令注入系统提示词中。文件的加载遵循**首次匹配原则**——每个会话仅加载一个项目上下文来源。

| 文件（按优先级顺序） | 加载方式 | 适用场景 |
|---|---|---|
| `.hermes.md` / `HERMES.md` | 从当前目录向上遍历至 Git 根目录，仅在 Git 根目录停止 | 需要分层项目规则配置（根目录规则及各包的覆盖规则） |
| `AGENTS.md` / `agents.md` | **仅考虑当前工作目录**——子目录及父目录的副本将被忽略 | 需要编写可在 Hermes、Claude Code、Codex 等工具中通用的语法简洁的智能体配置 |
| `CLAUDE.md` / `claude.md` | 仅考虑当前工作目录 | 与 `AGENTS.md` 功能类似，但针对 Claude 工具优化 |
| `.cursorrules` / `.cursor/rules/*.mdc` | 仅考虑当前工作目录 | 从 Cursor 平台迁移过来的用户使用 |

位于 `$HERMES_HOME` 目录下的 `SOUL.md` 文件独立存在，只要存在就会始终被加载——它用于设置智能体的身份信息，而非项目规则。

### 如何选择合适的文件

- **选择 `.hermes.md`**：当需要定义适用于整个项目（包括根目录及所有子目录）的、针对 Hermes 的特殊规则，或希望规则能从父目录继承时使用。由于遍历会在 Git 根目录停止，因此位于用户主目录下的 `.hermes.md` 文件不会影响其他项目（Git 仓库的根目录即为分隔边界）。
- **选择 `AGENTS.md`**：当同一项目还需要由其他智能体工具（如 Codex、Claude Code、OpenCode）处理时使用。这些工具对 `AGENTS.md` 都有各自的格式规范，而“仅考虑当前工作目录”的设计使得该文件具备跨平台兼容性。
- **不要将项目规则放在 `~/.hermes/AGENTS.md`（或其他用户主目录下的位置）**。当 Hermes 以该目录作为当前工作目录运行时，虽然该文件会被加载，但仅对该目录有效。如需实现跨项目上下文共享，可使用位于 `$HERMES_HOME` 的 `SOUL.md` 文件（仅用于设置身份信息），或通过 `hermes skills install` 命令安装技能。

### 文件大小与截断处理

每个上下文文件的字符上限为20,000个。超过此限制的文件会被**截取开头和结尾部分**（中间内容将被删除，并显示 `[...truncated...]` 标记）。对于内容较多的项目规则，建议将其拆分为多个独立技能，而非试图将所有内容塞入一个文件中。

### 安全性

所有上下文文件在进入系统提示词之前都会经过威胁模式扫描器检测。凡是匹配到提示词注入或恶意提示词技术的内容，都会被替换为 `[BLOCKED: ...]` 占位符。这意味着，即使 `AGENTS.md` 文件中包含明显的注入尝试，相关内容也不会传递给模型——扫描器会拦截内容本身，而不会阻止整个文件的加载。

### 临时禁用上下文加载

可通过 `hermes --ignore-rules` 命令跳过所有项目上下文文件（`.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`.cursorrules`）以及 `SOUL.md` 中的身份信息，同时还会忽略用户自定义配置、插件和 MCP 服务器。该命令可用于判断问题出在用户设置还是 Hermes 本身。

### 示例：一个简短的 `.hermes.md` 文件

```markdown
# My Project

Hermes: when working in this repo, follow these rules.

## Build
- Always run `make test` before declaring a change done.
- Use `uv run` for Python, not `pip install`.

## Style
- Prefer `pathlib.Path` over `os.path`.
- No `print()` in production code — use the `logger`.
```

当 Hermes 在 `/home/me/projects/myrepo` 的任意子目录中运行时，会自动加载位于 `/home/me/projects/myrepo/.hermes.md` 的该文件；但若在 `/home/me/other-project` 中运行，则不会加载。

## 安全与隐私相关开关

常见的一些“为何 Hermes 会对我的输出、工具调用或命令执行特定操作？”类开关，以及用于修改它们的具体命令。由于这些设置仅在启动时读取一次，因此大多数情况下需要重新启动会话（在聊天界面中使用 `/reset` 命令，或重新调用 `hermes`）才能生效。

### 工具输出中的机密信息遮蔽

机密信息遮蔽功能**默认处于开启状态**——在工具输出（终端标准输出、`read_file` 的返回内容、网页内容、子代理的总结信息等）进入对话上下文及日志之前，系统会自动扫描其中可能包含的 API 密钥、令牌和机密字符串。在正常使用情况下建议保持该功能开启：

```bash
hermes config set security.redact_secrets true       # keep enabled globally
```

**需要重启。** `security.redact_secrets` 会在导入时被创建快照——在会话进行中通过某些方式（例如通过工具调用执行 `export HERMES_REDACT_SECRETS=false`）来切换该设置，不会对正在运行的进程产生任何影响。请告知用户需通过终端在配置文件中修改该设置，然后再启动新的会话。这样做是有意为之，旨在防止大型语言模型在处理任务过程中自行改变该设置。

仅在确实需要原始的凭证类字符串用于调试或编辑器开发时，才应关闭此功能：
```bash
hermes config set security.redact_secrets false
```

### 网关消息中的个人身份信息脱敏

此功能与机密信息脱敏相互独立。启用该功能后，网关会在会话上下文数据传递给模型之前，先对用户 ID 进行哈希处理，并删除其中的电话号码：

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### 命令审批提示

默认情况下（`approvals.mode: manual`），Hermes 会在执行被标记为具有破坏性作用的 shell 命令（如 `rm -rf`、`git reset --hard` 等）之前向用户发起确认提示。可选的模式如下：

- `manual` — 始终进行提示（默认值）
- `smart` — 利用辅助大型语言模型自动批准低风险命令，仅对高风险命令进行提示
- `off` — 跳过所有审批提示（相当于 `--yolo`）

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

无需修改配置即可实现每次调用时绕过限制：
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

注意：YOLO模式或`approvals.mode: off`设置并不会关闭机密信息遮蔽功能，二者是相互独立的。

### Shell钩子允许列表

某些Shell钩子集成在触发前需要明确列出允许的项。该列表通过`~/.hermes/shell-hooks-allowlist.json`文件进行管理——首次有钩子试图运行时会交互式提示设置。

### 禁用Web/浏览器/图像生成工具

若希望让模型完全不使用网络或媒体相关工具，可打开“hermes tools”并针对不同平台进行开关设置。更改将在下次会话时生效（可使用`/reset`重置）。详情请参阅上文“工具与技能”部分。

---

## 语音与转录

### STT（语音转文本）

来自消息平台的语音消息会自动被转录。

提供方优先级（系统自动检测）：
1. **本地faster-whisper** — 免费，无需API密钥：`pip install faster-whisper`
2. **Groq Whisper** — 免费套餐：需设置`GROQ_API_KEY`
3. **OpenAI Whisper** — 付费服务：需设置`VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — 需设置`MISTRAL_API_KEY`

配置选项：
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### 文本转语音（Text → Voice）

| 提供商 | 环境变量 | 是否免费？ |
|--------|---------|----------|
| Edge TTS | 无 | 是（默认） |
| ElevenLabs | `ELEVENLABS_API_KEY` | 免费套餐 |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | 需付费 |
| MiniMax | `MINIMAX_API_KEY` | 需付费 |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | 需付费 |
| NeuTTS（本地版） | 无（需执行 `pip install neutts[all]` 并搭配 `espeak-ng`） | 免费 |

语音指令：`/voice on`（语音对语音），`/voice tts`（始终使用语音），`/voice off`。

---

## 启动额外的 Hermes 实例

以完全独立的子进程形式运行多个 Hermes 进程——拥有独立的会话、工具及环境。

### 何时使用此方法而非 delegate_task

| | `delegate_task` | 启动 `hermes` 进程 |
|-|-----------------|------------------|
| 隔离性 | 独立对话，共享进程 | 完全独立的进程 |
| 运行时长 | 几分钟（受父进程循环限制） | 数小时/数天 |
| 工具访问权限 | 仅能使用父进程的部分工具 | 可使用所有工具 |
| 交互性 | 不支持 | 支持（PTY 模式） |
| 适用场景 | 快速处理的并行子任务 | 长时间自主运行的任务 |

### 单次执行模式

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### 交互式 PTY 模式（通过 tmux 实现）

Hermes 使用 prompt_toolkit，而该库需要真实的终端环境。建议使用 tmux 来实现交互式进程启动：

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### 多智能体协同

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### 会话恢复

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### 小贴士

- **处理快速子任务时优先使用 `delegate_task`**——相比启动完整进程，其开销更小。
- 在启动用于编辑代码的智能体时，请使用 `-w`（工作树模式）——可避免 Git 冲突。
- 为一次性模式设置超时时间——复杂任务可能需要 5-10 分钟才能完成。
- 若需“发送即忘”的使用方式，可使用 `hermes chat -q`——无需伪终端。
- 交互式会话建议使用 tmux——原始伪终端模式会导致 prompt_toolkit 出现 `\r` 与 `\n` 的兼容问题。
- 对于定时任务，建议使用 `cronjob` 工具而非直接启动智能体——它能自动处理任务交付与重试机制。

---

## 持久化与后台系统

有四个系统与主对话循环并行运行。此处为简要参考；完整的开发者文档见 `AGENTS.md`，面向用户的文档则在 `website/docs/user-guide/features/` 下。

### 任务委派（`delegate_task`）

同步启动子智能体——父智能体会等待子智能体的总结结果后再继续自己的循环。子智能体拥有独立的上下文与终端会话。

- **单任务模式：** `delegate_task(goal, context, toolsets)`。
- **批量模式：** `delegate_task(tasks=[{goal, ...}, ...])` 会并行启动多个子任务，其并发数量受 `delegation.max_concurrent_children`（默认为 3）限制。
- **角色划分：** `leaf` 角色（默认；不可再次委派）与 `orchestrator` 角色（可自行启动工作进程，其嵌套深度受 `delegation.max_spawn_depth` 限制）。
- **非持久化机制。** 若父智能体被中断，子智能体也会被取消。对于需要持续运行的任务，请使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。

配置项位于 `config.yaml` 的 `delegation.*` 部分。

### 定时任务（Cron）

这是一种持久化调度器——由 `cron/jobs.py` 和 `cron/scheduler.py` 组成。可通过 `cronjob` 工具、`hermes cron` CLI（提供 `list`、`add`、`edit`、`pause`、`resume`、`run`、`remove` 等命令）或 `/cron` 斜杠命令来操作。

- **调度规则：** 可设置持续时间（如 `"30m"`、`"2h"`）、周期表达式（如 `"every monday 9am"`）、五字段 Cron 表达式（如 `"0 9 * * *"`）或 ISO 时间戳。
- **任务级配置选项：** 可指定技能集、覆盖模型/提供者设置、预运行脚本（用于数据收集；若设置 `no_agent=True`，则脚本即构成整个任务）、从其他任务获取上下文的功能、工作目录（在指定目录中运行并加载该目录下的 `AGENTS.md`/`CLAUDE.md` 文件），以及跨平台任务交付功能。
- **固有限制：** 每次运行最多允许 3 分钟的强制中断；`.tick.lock` 文件可防止不同进程之间出现重复触发；Cron 会话默认设置 `skip_memory=True`；此外，Cron 任务的输出会以标题/页脚形式呈现，而不会被直接映射到目标网关会话中（从而保持角色切换的完整性）。

用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

### 技能生命周期管理器（Curator）

用于对智能体创建的技能进行后台维护。它可追踪技能使用情况，标记闲置技能为过期，归档过期的技能，并保留预运行时的 tar.gz 备份，确保数据不会丢失。

- **CLI 命令：** `hermes curator <动词>`——包括 `status`、`run`、`pause`、`resume`、`pin`、`unpin`、`archive`、`restore`、`prune`、`backup`、`rollback`。
- **斜杠命令：** `/curator <子命令>` 功能与 CLI 相同。
- **作用范围：** 仅处理来源为 `created_by: "agent"` 的技能。预装或通过中心节点安装的技能不在其管理范围内。该工具**绝不会删除**任何技能——最严厉的操作仅为归档。被标记为固定的技能可免于所有自动转换及大型语言模型审核流程。
- **监控数据：** 在 `~/.hermes/skills/.usage.json` 文件中会存储每个技能的 `use_count`、`view_count`、`patch_count`、`last_activity_at`、`state` 以及是否被固定等信息。

配置项位于 `curator.*`（包括 `enabled`、`interval_hours`、`min_idle_hours`、`stale_after_days`、`archive_after_days`、`backup.*` 等）。  
用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/curator

### 看板系统（Kanban）

这是一个基于 SQLite 的持久化看板系统，适用于多账号/多工作进程的协作场景。用户可通过 `hermes kanban <动词>` 来操作它；由调度器启动的工作进程会看到受 `HERMES_KANBAN_TASK` 限制的 `kanban_*` 技能集，而编排型账号则可以选择使用更全面的 `kanban` 技能集。除非特别配置，普通会话不会生成任何 `kanban_*` 结构。

- **常用 CLI 命令：** `init`、`create`、`list`（别名为 `ls`）、`show`、`assign`、`link`、`unlink`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`。较少使用的命令包括 `watch`、`stats`、`runs`、`log`、`dispatch`、`daemon`、`gc`。
- **工作进程/编排型账号的技能集：** 包括 `kanban_show`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link`；那些在非调度器任务中明确启用了 `kanban` 技能集的账号，还可使用 `kanban_list` 和 `kanban_unblock` 命令来操作看板。
- **调度器**默认在网关内部运行（`kanban.dispatch_in_gateway: true`），负责回收过期的任务声明、提升已准备就绪的任务优先级、以原子方式获取任务，并启动对应的账号。若连续出现 `failure_limit` 次启动失败（默认为 2 次，可通过 `kanban.failure_limit` 或每任务的 `max_retries` 参数进行配置），调度器会自动将该任务标记为阻塞状态。
- **隔离机制：** 看板本身是严格的边界（工作进程的环境中会固定包含 `HERMES_KANBAN_BOARD` 变量）；而“租户”则是看板内的一个软命名空间，用于实现工作路径与内存键的隔离。

用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban

---

## Windows 系统特有问题

Hermes 可在 Windows 系统上直接运行（支持 PowerShell、cmd、Windows Terminal、git-bash、mintty 以及 VS Code 的集成终端）。大部分功能都能正常使用，但由于 Win32 与 POSIX 环境存在一些差异，我们遇到了一些问题——请在发现新问题时在此处记录下来，以便后续人员或会话无需重复摸索。

### 输入/快捷键

**Alt+Enter 不会插入换行符。** Windows Terminal 会在终端层拦截 Alt+Enter 键，用于切换全屏模式——该按键根本无法传递给 prompt_toolkit。建议使用 **Ctrl+Enter** 代替。Windows Terminal 会将 Ctrl+Enter 解释为 LF 键（对应 `c-j`），这与普通的 Enter 键（对应 `c-m`/CR）不同；CLI 仅在 Win32 环境中将 `c-j` 绑定到插入换行符的功能（详见 `cli.py` 文件中的 `_bind_prompt_submit_keys` 以及仅适用于 Windows 的 `c-j` 绑定）。附带的一个副作用是：在 Windows 上，原始的 Ctrl+J 键也会插入换行符——这是不可避免的，因为 Windows Terminal 在 Win32 控制台 API 层将 Ctrl+Enter 与 Ctrl+J 映射为相同的键码。由于 Windows 上原本就不存在与 Ctrl+J 冲突的绑定，因此这一副作用并无危害。

mintty 和 git-bash 的行为也是如此（Alt+Enter 会切换全屏），除非你在“选项 → 键盘”中禁用 Alt+Fn 快捷键。直接使用 Ctrl+Enter 更为方便。

**诊断快捷键问题。** 可在项目根目录下运行 `python scripts/keystroke_diagnostic.py`，即可查看 prompt_toolkit 是如何识别当前终端中的每个按键的。该工具可以回答诸如“Shift+Enter 是否会被视为独立的按键？”（几乎不会——大多数终端都会将其合并为普通 Enter 键）或“我的终端在发送 Ctrl+Enter 时使用的是哪种字节序列？”之类的问题。正是通过该工具，我们确认了 Ctrl+Enter 实际对应 `c-j` 键这一事实。

### 配置/文件

**首次运行时会出现 HTTP 400 “未提供模型”错误。** 这是因为 `config.yaml` 文件是以带 UTF-8 BOM 格式保存的（Windows 应用程序在保存时经常会这样处理）。请将其重新保存为不带 BOM 的 UTF-8 格式。`hermes config edit` 命令会在保存时自动去掉 BOM；而使用记事本手动编辑文件则往往是导致该问题的原因。

### `execute_code`/沙箱环境

在沙箱子进程中可能会出现 **WinError 10106** 错误（提示“无法加载或初始化请求的服务提供者”）——这是因为子进程无法创建 `AF_INET` 套接字，从而导致回环 TCP RPC 备用方案在调用 `connect()` 之前就失败了。其根本原因通常并非 Winsock LSP 出现故障，而是 Hermes 自带的环境清理机制移除了子进程中的 `SYSTEMROOT`、`WINDIR` 和 `COMSPEC` 等路径。Python 的 `socket` 模块需要 `SYSTEMROOT` 路径才能找到 `mswsock.dll` 文件。该问题可通过在 `tools/code_execution_tool.py` 文件中设置 `_WINDOWS_ESSENTIAL_ENV_VARS` 允许列表来解决。如果问题依然存在，可在 `execute_code` 块中输出 `os.environ` 的内容，以确认 `SYSTEMROOT` 变量是否已被正确设置。完整的诊断步骤请参阅 `references/execute-code-sandbox-env-windows.md` 文件。

### 测试/贡献代码

**`scripts/run_tests.sh` 在 Windows 上无法直接使用**——因为它期望的是 POSIX 风格的虚拟环境结构（即 `.venv/bin/activate`）。Hermes 安装的虚拟环境位于 `venv/Scripts/` 目录下，该环境中也没有安装 pip 或 pytest（为缩小安装体积而进行了精简）。解决方法是在系统级的 Python 3.11 用户目录中安装 `pytest + pytest-xdist + pyyaml`，然后通过设置 `PYTHONPATH` 直接调用 pytest 命令来运行测试。

```bash
"/c/Program Files/Python311/python" -m pip install --user pytest pytest-xdist pyyaml
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/foo/test_bar.py -v --tb=short -n 0
```

请使用 `-n 0` 而非 `-n 4`——因为 `pyproject.toml` 中的默认 `addopts` 选项已包含 `-n`，且该封装工具的 CI 兼容性保障并不适用于非 POSIX 环境。

**仅适用于 POSIX 的测试需要添加跳过机制。**代码库中已有的常用标记包括：
- 符号链接——在 Windows 系统上需要更高权限
- `0o600` 文件权限模式——NTFS 文件系统默认不会强制应用 POSIX 的权限位
- `signal.SIGALRM`——仅适用于 Unix 系统（参见 `tests/conftest.py::_enforce_test_timeout`）
- Winsock/Windows 特有的回归问题——可使用 `@pytest.mark.skipif(sys.platform != "win32", ...)` 进行标记

建议采用现有的跳过模式写法（如 `sys.platform == "win32"` 或 `sys.platform.startswith("win")`），以保持与其余测试用例的一致性。

### 路径/文件系统

**行尾格式。**Git 可能会提示“下次处理该文件时，LF 格式将被替换为 CRLF”。这只是视觉问题，仓库的 `.gitattributes` 文件可对其进行统一处理。请勿让编辑器自动将已提交的 POSIX 行尾格式文件转换为 CRLF。

**几乎所有地方都支持正斜杠。**`C:/Users/...` 这种路径格式能被所有 Hermes 工具以及大多数 Windows API 接受。在代码和日志中建议使用正斜杠，这样可以避免在 bash 中出现需要转义的反斜杠。

---

## 故障排除

### 语音功能无法使用
1. 检查 `config.yaml` 文件中是否设置了 `stt.enabled: true`
2. 确认对应服务提供方已安装：执行 `pip install faster-whisper`，或设置 API 密钥
3. 在网关端执行 `/restart` 命令；在命令行界面中则需退出后重新启动程序

### 某工具不可用
1. 运行 `hermes tools` 查看当前平台是否已启用该工具集
2. 部分工具需要环境变量（请检查 `.env` 文件）
3. 启用相关工具后执行 `/reset` 命令

### 模型/服务提供方相关问题
1. 运行 `hermes doctor` 检查配置及依赖项状态
2. 执行 `hermes auth` 重新认证 OAuth 服务提供方（或使用 `hermes auth add <provider>` 命令添加）
3. 确认 `.env` 文件中包含正确的 API 密钥
4. **Copilot 403 错误**：`gh auth login` 生成的令牌无法用于 Copilot API。必须通过 `hermes model` → GitHub Copilot 的专用 OAuth 设备代码流程来获取授权

### 修改未生效
- **工具/技能问题**：执行 `/reset` 可以启动包含更新后工具集的新会话
- **配置更改问题**：在网关端执行 `/restart` 命令；在命令行界面中则需退出后重新启动程序
- **代码更改问题**：重启命令行界面或网关进程

### 技能项未显示
1. 运行 `hermes skills list` 查看已安装的技能项
2. 执行 `hermes skills config` 检查平台是否已启用相应技能
3. 如需手动加载特定技能，可执行 `/skill name` 命令或使用 `hermes -s name` 参数

### 网关相关问题
首先请检查日志文件：
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

常见网关问题：
- **SSH登出时网关崩溃**：启用延迟退出功能：`sudo loginctl enable-linger $USER`
- **关闭WSL2时网关崩溃**：WSL2要求在`/etc/wsl.conf`中设置`systemd=true`，以便systemd服务正常运行。若未设置此参数，网关将回退到`nohup`模式（会随会话关闭而终止）。
- **网关陷入崩溃循环**：重置故障状态：`systemctl --user reset-failed hermes-gateway`

### 各平台特有问题
- **Discord机器人无响应**：需在机器人的“特权网关意图”设置中启用**消息内容意图**。
- **Slack机器人仅在私信中正常工作**：必须订阅`message.channels`事件。否则，机器人将忽略公共频道。
- **Windows系统特有问题**（如`Alt+Enter`换行、WinError 10106错误、UTF-8 BOM配置、测试套件及行尾格式等），请参阅上文专门的**Windows系统特有问题**部分。

### 辅助模型无法使用
如果视觉处理、压缩、会话搜索等`auxiliary`任务 silently 失败，`auto`提供程序将无法找到对应的后端服务。此时需设置`OPENROUTER_API_KEY`或`GOOGLE_API_KEY`，或为每个辅助任务单独配置相应的提供程序：
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

## 如何查找相关内容

| 需要查找的内容 | 查找位置 |
|----------------|----------|
| 配置选项 | `hermes config edit` 或 [配置文档](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| 可用工具 | `hermes tools list` 或 [工具参考手册](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| 斜杠命令 | 会话中输入 `/help` 或 [斜杠命令参考手册](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| 技能目录 | `hermes skills browse` 或 [技能目录](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| 提供商配置 | `hermes model` 或 [提供商指南](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| 平台配置 | `hermes gateway setup` 或 [消息传递文档](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP 服务器 | `hermes mcp list` 或 [MCP 指南](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| 配置文件 | `hermes profile list` 或 [配置文件文档](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| 定时任务 | `hermes cron list` 或 [定时任务文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| 内存状态 | `hermes memory status` 或 [内存相关文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| 环境变量 | `hermes config env-path` 或 [环境变量参考手册](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI 命令 | `hermes --help` 或 [CLI 参考手册](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| 网关日志 | `~/.hermes/logs/gateway.log` |
| 会话文件 | `hermes sessions browse`（读取 state.db 文件） |
| 源代码 | `~/.hermes/hermes-agent/` |

---

## 贡献者快速参考指南

专为偶尔参与贡献或提交 PR 的用户准备。完整开发者文档请访问：https://hermes-agent.nousresearch.com/docs/developer-guide/

### 项目结构

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

配置文件：`~/.hermes/config.yaml`（用于存储设置），`~/.hermes/.env`（用于存储 API 密钥）——若已设置 `$HERMES_HOME`，则这两个文件均位于该路径下。

### 添加工具（需3个文件）

**1. 创建 `tools/your_tool.py` 文件：**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. 添加到 `toolsets.py`** → `_HERMES_CORE_TOOLS` 列表中。  
系统会自动检测：凡是包含顶层 `registry.register()` 调用的 `tools/*.py` 文件都会被自动导入，无需手动编写列表。  
所有处理函数都必须返回 JSON 字符串。请使用 `get_hermes_home()` 获取路径，切勿硬编码 `~/.hermes`。

### 添加斜杠命令

1. 在 `hermes_cli/commands.py` 中的 `COMMAND_REGISTRY` 中添加 `CommandDef` 定义；  
2. 在 `cli.py` 中的 `process_command()` 函数中编写对应的处理逻辑；  
3. （可选）在 `gateway/run.py` 中添加网关处理函数。  
所有相关功能（帮助文本、自动补全、Telegram 菜单、Slack 映射等）都会自动从中央注册表中获取配置。

### Agent 循环（概述）

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### 测试

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- 测试会自动将 `HERMES_HOME` 重定向至临时目录——绝不会修改真实的 `~/.hermes/` 目录。  
- 在提交任何更改之前，务必先运行完整的测试套件。  
- 使用 `-o 'addopts='` 参数可清除所有预置的 pytest 标志。  

**Windows 用户注意：** 目前的 `scripts/run_tests.sh` 脚本仅支持 POSIX 风格的虚拟环境（如 `.venv/bin/activate` 或 `venv/bin/activate`），对于 Windows 系统中采用 `venv/Scripts/activate` 及 `python.exe` 结构的环境会报错。此外，Hermes 安装的虚拟环境位于 `venv/Scripts/` 目录下，其中也不包含 `pip` 或 `pytest` 工具——这是为控制最终安装包大小而刻意移除的。解决方法是将 pytest、pytest-xdist 和 pyyaml 安装到系统 Python 3.11 的用户目录中（可通过命令 `/c/Program Files/Python311/python -m pip install --user pytest pytest-xdist pyyaml` 完成），之后即可直接运行测试。

```bash
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/tools/test_foo.py -v --tb=short -n 0
```

请使用 `-n 0`（而非 `-n 4`），因为 `pyproject.toml` 中的默认 `addopts` 选项已包含 `-n` 参数，且该封装工具的 CI 兼容性要求并不适用于非 POSIX 环境。

**跨平台测试保护机制：** 需要使用仅支持 POSIX 系统调用的测试应添加跳过标记。代码库中已存在的常见标记如下：
- 创建符号链接 → `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")`（参见 `tests/cron/test_cron_script.py`）
- POSIX 文件权限模式（如 0o600 等）→ `@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX mode bits not enforced on Windows")`（参见 `tests/hermes_cli/test_auth_toctou_file_modes.py`）
- `signal.SIGALRM` → 仅适用于 Unix 系统（参见 `tests/conftest.py::_enforce_test_timeout`）
- 实时 Winsock 功能/针对 Windows 的回归测试 → `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`

如果被测试代码同时调用了 `platform.system()`、`platform.release()` 或 `platform.mac_ver()` 函数，仅修改 `sys.platform` 是不够的。因为这些函数会独立读取真实的操作系统信息，因此在 Windows 环境下将 `sys.platform` 设置为 "linux" 的测试仍会返回 `platform.system() == "Windows"`，从而执行对应的 Windows 分支逻辑。此时需同时修改这三个函数的返回值。

```python
monkeypatch.setattr(sys, "platform", "linux")
monkeypatch.setattr(platform, "system", lambda: "Linux")
monkeypatch.setattr(platform, "release", lambda: "6.8.0-generic")
```

如需示例代码，请参阅 `tests/agent/test_prompt_builder.py::TestEnvironmentHints`。

### 扩展系统提示中的执行环境模块

关于主机操作系统、用户主目录、当前工作目录、终端后端以及 Shell（Windows 系统为 bash 或 PowerShell）的详细信息，均由 `agent/prompt_builder.py::build_environment_hints()` 函数生成。该函数同时还负责处理 WSL 相关提示及针对不同后端的检测逻辑。具体规则如下：

- **本地终端后端** → 输出主机信息（操作系统、`$

```
type: concise subject line

Optional body.
```

类型：`fix:`、`feat:`、`refactor:`、`docs:`、`chore:`

### 核心规则

- **严禁破坏提示词缓存** —— 严禁在对话过程中更改上下文、工具或系统提示词
- **消息角色交替发送** —— 严禁连续出现两条助手消息或两条用户消息
- 所有路径均需使用 `hermes_constants` 中的 `get_hermes_home()` 函数（确保配置安全）
- 配置值应存放在 `config.yaml` 中，敏感信息则需保存在 `.env` 文件中
- 新工具必须配备 `check_fn`，以便仅在满足特定条件时才会显示
