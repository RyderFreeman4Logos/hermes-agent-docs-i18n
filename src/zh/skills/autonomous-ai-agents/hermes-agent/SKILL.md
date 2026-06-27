---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.3.0
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

Hermes Agent 是 Nous Research 开发的开源 AI 智能体框架，可在终端、原生桌面应用、消息平台以及集成开发环境（IDE）中运行。它与 Claude Code（Anthropic）、Codex（OpenAI）、OpenClaw 属于同一类别——这类自主编程与任务执行型智能体均通过调用工具与用户系统进行交互。Hermes 能与任何大型语言模型提供商配合使用（包括 OpenRouter、Anthropic、OpenAI、Google、DeepSeek、xAI 以及本地模型等20多种），并且可在 Linux、macOS、Windows 和 WSL 系统上运行。

Hermes 的独特之处在于：

- **通过“技能”实现自我提升**——Hermes 能从经验中学习，将可重复使用的操作流程保存为“技能”。当它解决复杂问题、发现新的工作流程或得到纠正后，就能将这些知识以技能文档的形式保存下来，供后续会话使用。随着时间的推移，这些技能不断积累，使智能体更擅长处理特定任务及适应特定环境。
- **跨会话持久记忆**——能够记住用户身份、个人偏好、环境详情以及过往经验教训。通过可插拔的记忆后端（内置选项、Honcho、Mem0 等），用户可自主选择记忆的存储方式。
- **多平台接入能力**——同一个智能体可在 Telegram、Discord、Slack、WhatsApp、iMessage、Signal、Matrix、Teams、Email 以及十余种其他平台上运行，不仅能进行聊天，还能完整调用各类工具。
- **多种交互界面**——同一个智能体核心可驱动命令行界面（CLI）、Ink TUI、原生 Electron 桌面应用、网页控制面板，以及专为 IDE（如 VS Code / Zed / JetBrains）设计的 ACP 服务器。
- **与提供商无关**——在任务执行过程中可随时更换模型和提供商，而无需调整其他设置。凭证池会自动在多个 API 密钥之间切换。
- **多实例配置功能**——可运行多个独立的 Hermes 实例，每个实例拥有独立的配置、会话、技能和记忆数据。
- **高度可扩展**——支持插件、MCP 服务器、自定义工具、Webhook 触发器、定时任务调度，以及完整的 Python 生态系统。

人们将 Hermes 应用于软件开发、科学研究、系统管理、数据分析、内容创作、家庭自动化等领域，凡是需要具备持久上下文感知能力和完整系统访问权限的 AI 智能体的场景，都能从中受益。

**本技能旨在帮助您高效使用 Hermes Agent**——涵盖其设置安装、功能配置、启动多个智能体实例、故障排查、查找相关命令与设置，以及在需要扩展或贡献代码时理解系统运作原理等内容。

**文档链接：** https://hermes-agent.nousresearch.com/docs/

## 范围与验证说明

本技能仅为简明的操作指南，并非涵盖 Hermes 所有功能的完整参考资料。如果某项功能、命令或设置在此处未提及，也不意味着它不存在。在给出否定回答之前，请务必查阅官方代码仓库及完整文档。

推荐的验证来源包括：

- 命令行指令：`hermes --help`、`hermes <command> --help`，以及 `hermes_cli/main.py`
- 用户文档：https://hermes-agent.nousresearch.com/docs/
- 源代码仓库：https://github.com/NousResearch/hermes-agent

## 快速入门

```bash
# Install (shell installer — sets up uv, Python, the venv, and the launcher)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Or via PyPI (ships the TUI bundle + shell launcher)
pip install hermes-agent       # or: uv pip install hermes-agent

# Interactive chat (default surface; set display.interface: tui to launch the Ink TUI instead)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard  /  pick model+provider  /  health check
hermes setup
hermes model
hermes doctor

# Other surfaces
hermes desktop                 # launch the native desktop app (alias: hermes gui)
hermes dashboard               # web admin panel + embedded chat
hermes proxy                   # OpenAI-compatible local proxy backed by your OAuth provider
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
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

凭据（包括 OAuth 和 API 密钥，以及凭据池功能）均在 `hermes auth` 下进行管理——详情请参阅下方的“凭据与凭据池”部分。

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

支持的平台超过20种：Telegram、Discord、Slack、WhatsApp（通过Baileys bridge及官方Business Cloud API接入）、iMessage（基于Photon协议——可通过`hermes photon setup`命令配置，该协议为BlueBubbles的继任者且无需Mac中转）、Signal、电子邮件、短信、Matrix、Mattermost、Microsoft Teams、LINE、SimpleX、ntfy、Google Chat、Home Assistant、钉钉、飞书、企业微信、微信（WeChat）、Raft（代理网络）、API服务器以及Webhooks。Open WebUI可通过API服务器适配器进行连接。大多数适配器均存放在`plugins/platforms/`目录下，因此新增适配器时无需修改核心代码。

平台相关文档：https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### 会话管理

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

### 凭证与资源池

```
hermes auth                 Interactive credential manager
hermes auth add [PROVIDER]  Add OAuth or API-key credential
                            (e.g. nous, openai-codex, qwen-oauth, anthropic)
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

每个提供者对应的多个凭证会构成一个池，该池会自动轮换使用这些凭证，并自动跳过已用尽的密钥。

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes desktop / gui        Launch the native desktop app
hermes dashboard            Web admin panel + embedded chat
hermes proxy                OpenAI-compatible local proxy backed by an OAuth provider
hermes portal               Quick setup / sign in via Nous Portal
hermes kanban <verb>        Multi-agent work-queue board (init/create/list/show/assign/…)
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes secrets bitwarden …  External secret store (Bitwarden Secrets Manager)
hermes memory setup/status/off  Memory provider config
hermes send                 Send a one-off message through a gateway platform
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

如需查看完整且权威的命令列表，请运行 `hermes --help`（以及 `hermes <command> --help`）。由插件或提供程序生成的子命令（例如用于 iMessage 的 `hermes photon setup`）只有在相关插件被安装或启用后才会显示。

---

## 斜杠命令（会话内使用）

这些命令可在交互式聊天会话中输入。新命令会频繁添加；如果下方内容显得过时，可会在会话中输入 `/help` 以获取最新列表，或查阅[实时斜杠命令参考文档](https://hermes-agent.nousresearch.com/docs/reference/slash-commands)。权威的命令注册表位于 `hermes_cli/commands.py` —— 所有的命令使用场景（自动补全、Telegram 菜单、Slack 映射、/help）均以此为依据。

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
/handoff <platform>  Hand the live session off to a messaging platform (CLI)
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
| `display` | `skin`、`interface`（cli/tui）、`tool_progress`、`show_reasoning`、`show_cost`、`language` |
| `stt` | `enabled`、`provider`（local/groq/openai/mistral） |
| `tts` | `provider`（edge/elevenlabs/openai/minimax/mistral/neutts） |
| `memory` | `memory_enabled`、`user_profile_enabled`、`provider` |
| `security` | `tirith_enabled`、`website_blocklist` |
| `delegation` | `model`、`provider`、`base_url`、`api_key`、`max_iterations`（50）、`reasoning_effort` |
| `checkpoints` | `enabled`、`max_snapshots`（50） |
| `curator` | `enabled`、`consolidate`（false — 选择性合并辅助模型技能）、`interval_hours`、`stale_after_days` |

完整配置参考：https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### 提供商支持

目前支持20多种供应商，可通过 `hermes model` 或 `hermes setup` 命令进行配置。

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
| 自定义端点 | 配置文件 | 在config.yaml中设置 `model.base_url` 和 `model.api_key` |
| GitHub Copilot ACP | 外部工具 | `COPILOT_CLI_PATH` 或 Copilot CLI |

完整供应商文档：https://hermes-agent.nousresearch.com/docs/integrations/providers

### 工具集

可通过 `hermes tools`（交互式命令）或 `hermes tools enable/disable NAME` 命令启用/禁用工具集。

| 工具集 | 功能说明 |
|---------|----------|
| `web` | 网页搜索与内容提取 |
| `search` | 仅网页搜索（属于`web`的子集） |
| `browser` | 浏览器自动化（支持Browserbase、Camofox或本地Chromium） |
| `terminal` | Shell命令执行与进程管理 |
| `file` | 文件读写、搜索与修补操作 |
| `code_execution` | 沙箱化Python代码执行 |
| `vision` | 图像分析功能 |
| `image_gen` | AI图像生成及图像编辑功能 |
| `video` | 视频分析（`video_analyze`）与生成功能 |
| `x_search` | 首席级X（Twitter）搜索功能（需X OAuth认证或API密钥） |
| `tts` | 文本转语音功能 |
| `skills` | 技能浏览与管理功能 |
| `memory` | 跨会话持久化内存功能 |
| `session_search` | 搜索历史对话内容 |
| `delegation` | 子代理任务分配功能 |
| `cronjob` | 定时任务管理功能 |
| `clarify` | 向用户提问以获取更多信息 |
| `messaging` | 跨平台消息发送功能 |
| `todo` | 会话内任务规划与跟踪功能 |
| `kanban` | 多代理工作队列工具（仅对工作者开放） |
| `debugging` | 额外的自我诊断/调试工具（默认关闭） |
| `safe` | 为受限会话设计的极简低风险工具集 |
| `spotify` | Spotify播放与播放列表控制功能 |
| `homeassistant` | 智能家居控制功能（默认关闭） |
| `discord` | Discord集成工具 |
| `discord_admin` | Discord管理/审核工具 |
| `feishu_doc` | Feishu（Lark）文档处理工具 |
| `feishu_drive` | Feishu（Lark）云盘工具 |
| `yuanbao` | Yuanbao集成工具 |
| `rl` | 强化学习相关工具（默认关闭） |

所有工具集的完整列表存储在 `toolsets.py` 文件中的 `TOOLSETS` 字典中；`_HERMES_CORE_TOOLS` 是大多数平台默认使用的工具组合。

工具更改需通过 `/reset` 命令创建新会话后才会生效。为保留提示词缓存，这些更改不会在对话进行中应用。

---

## 项目上下文文件

Hermes会从工作目录读取上下文文件，将项目级指令注入系统提示词中。文件的加载遵循**先匹配者胜**原则——每个会话仅加载一个项目上下文来源。

| 文件（按优先级顺序） | 加载方式 | 适用场景 |
|---|---|---|
| `.hermes.md` / `HERMES.md` | 从当前目录向上遍历至git根目录，停在git根目录处 | 需要分层项目规则设置（根目录规则 + 各包的覆盖规则） |
| `AGENTS.md` / `agents.md` | **仅限当前工作目录**——子目录及父目录的副本将被忽略 | 需要可在Hermes、Claude Code、Codex等不同工具中通用且保持一致的代理指令 |
| `CLAUDE.md` / `claude.md` | 仅限当前工作目录 | 与AGENTS.md类似，但针对Claude优化 |
| `.cursorrules` / `.cursor/rules/*.mdc` | 仅限当前工作目录 | 从Cursor迁移过来的用户使用 |

位于 `$HERMES_HOME` 目录下的 `SOUL.md` 文件独立存在，只要存在就会始终被加载——它用于设置代理的身份信息，而非项目规则。

### 如何选择合适的文件

- **选择 `.hermes.md`**：当你需要Hermes特有的、适用于整个项目（根目录及所有子目录）的规则，或者希望规则能从父目录继承时使用。由于遍历会在git根目录停止，因此位于用户主目录下的 `.hermes.md` 文件不会影响其他项目（git仓库的根目录即为分隔边界）。
- **选择 `AGENTS.md`**：当同一个项目还需要由其他工具（如Codex、Claude Code、OpenCode）处理时使用。这些工具对 `AGENTS.md` 都有各自的格式要求，而“仅限当前工作目录”的设计保证了该文件的通用性。
- **不要将项目规则放在 `~/.hermes/AGENTS.md`**（或其他用户主目录下的位置）。当Hermes以该目录作为当前工作目录运行时，虽然该文件会被加载，但仅适用于当前目录。如需跨项目使用上下文，请使用 `SOUL.md`（位于 `$HERMES_HOME`，仅用于设置身份信息），或通过 `hermes skills install` 命令安装技能。

### 文件大小与截断处理

每个上下文文件的字符数上限为20,000个。超过此限制的文件会被**截取开头和结尾部分**（中间内容将被删除，并显示 `[...truncated...]` 标记）。对于内容较长的项目规则，建议将其拆分为多个技能，而非塞进一个文件中。

### 安全性

所有上下文文件在进入系统提示词之前都会经过威胁模式扫描。凡是检测到提示词注入或恶意提示词内容的模式，都会被替换为 `[BLOCKED: ...]` 占位符。这意味着，即使 `AGENTS.md` 文件中包含明显的注入尝试，内容也不会传递给模型——扫描器会拦截内容而非整个文件，因此文件的其余部分仍可正常加载。

### 临时禁用上下文加载

可使用 `hermes --ignore-rules` 命令，跳过所有项目上下文文件（`.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`.cursorrules`）以及 `SOUL.md` 中的身份信息，同时还会忽略用户自定义配置、插件和MCP服务器。该命令可用于判断问题出在用户设置还是Hermes本身。

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

### 实用提示

- **处理快速子任务时优先使用 `delegate_task`** —— 相比启动完整进程，其开销更小。
- **在启动用于编辑代码的智能体时使用 `-w`（工作树模式）** —— 可避免 Git 冲突。
- **为一次性模式设置超时时间** —— 复杂任务可能需要 5-10 分钟才能完成。
- **使用 `hermes chat -q` 进行“发完即忘”操作** —— 无需伪终端。
- **交互式会话请使用 tmux** —— 原始伪终端模式会导致 prompt_toolkit 在处理 `\r` 和 `\n` 时出现问题。
- **对于定时任务**，建议使用 `cronjob` 工具而非直接启动进程 —— 它能自动处理任务交付与重试机制。

---

## 持久化与后台系统

有四个系统与主对话循环并行运行。此处为快速参考；完整的开发者文档见 `AGENTS.md`，面向用户的文档则在 `website/docs/user-guide/features/` 下。

### 任务委托（`delegate_task`）

启动一个拥有独立上下文与终端会话的子智能体。

- **单任务模式**：`delegate_task(goal, context, toolsets)`。
- **批量模式**：`delegate_task(tasks=[{goal, ...}, ...])` 会并行执行多个子任务，其并发数量受 `delegation.max_concurrent_children`（默认为 3）限制。
- **后台模式**：`delegate_task(background=true)` 会立即返回一个处理句柄，同时让主循环继续运行；子任务完成后，其结果会作为新对话轮次重新加入对话。
- **角色类型**：`leaf`（默认，不可再次委托）与 `orchestrator`（可自行创建工作进程，受 `delegation.max_spawn_depth` 限制）。
- **非持久化**。后台运行的子任务仍属于进程级存在 —— 若父进程退出，子任务也会丢失。对于需要长期存在的任务，请使用 `cronjob` 或 `terminal(background=True, notify_on_complete=True)`。

配置项位于 `config.yaml` 的 `delegation.*` 部分。

### Cron（定时任务）

一种持久化调度器 —— 由 `cron/jobs.py` 和 `cron/scheduler.py` 组成。可通过 `cronjob` 工具、`hermes cron` CLI（支持 `list`、`add`、`edit`、`pause`、`resume`、`run`、`remove` 操作）或 `/cron` 接口来控制。

- **调度方式**：持续时间（如 `"30m"`、`"2h"`）、周期性表达式（如 `"every monday 9am"`）、五字段 Cron 表达式（如 `"0 9 * * *"`）或 ISO 时间戳。
- **任务级配置项**：`skills`、`model`/`provider` 的覆盖设置、`script`（任务执行前的数据收集脚本；若设置 `no_agent=True`，则该脚本即构成整个任务）、`context_from`（将任务 A 的输出传递给任务 B）、`workdir`（在指定目录中运行并加载该目录下的 `AGENTS.md` / `CLAUDE.md` 文件）、跨平台任务交付功能。
- **固有限制**：每次任务执行最多可被强制中断 3 分钟；`.tick.lock` 文件可防止不同进程重复触发调度；Cron 会话默认设置 `skip_memory=True`；Cron 任务的输出会以标题/页脚形式封装，而不会直接复制到目标网关会话中（从而保持角色切换的完整性）。

用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/cron

### 技能管理器（技能生命周期管理）

用于对智能体创建的技能进行后台维护。它可跟踪技能使用情况，标记闲置技能为过期，归档过期的技能，并生成预执行前的 tar.gz 备份，确保数据不会丢失。

- **CLI 命令**：`hermes curator <verb>` —— 支持 `status`、`run`、`pause`、`resume`、`pin`、`unpin`、`archive`、`restore`、`prune`、`backup`、`rollback` 等操作。
- **Slash 命令**：`/curator <subcommand>` 功能与 CLI 相同。
- **作用范围**：仅处理 `created_by: "agent"` 标识的技能。预装或通过中心节点安装的技能不在其管理范围内。**该工具绝不会删除技能** —— 最严重的操作仅为归档。被标记为“固定”的技能可免于所有自动转换及大型语言模型审查流程。
- **成本**：基于确定性的闲置检测与清理操作是免费的。辅助模型用于“将重叠技能整合为聚合技能”的功能默认处于关闭状态 —— 可通过设置 `curator.consolidate: true` 或使用 `hermes curator run --consolidate` 启用该功能。常规的后台维护操作不消耗任何令牌。
- **监控数据**：位于 `~/.hermes/skills/.usage.json` 的侧车文件会记录每个技能的 `use_count`、`view_count`、`patch_count`、`last_activity_at`、`state` 以及是否被固定等信息。

配置项位于 `curator.*` 部分（包括 `enabled`、`interval_hours`、`min_idle_hours`、`stale_after_days`、`archive_after_days`、`backup.*` 等）。  
用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/curator

### 看板系统（多智能体任务队列）

这是一个基于 SQLite 的持久化看板系统，适用于多账号/多工作进程的协作场景。用户可通过 `hermes kanban <verb>` 命令来操作它；由调度器创建的工作进程会看到受 `HERMES_KANBAN_TASK` 限制的专用 `kanban_*` 工具集，而编排型账号则可选择使用更全面的 `kanban` 工具集。除非另有配置，普通会话不会包含任何 `kanban_*` 结构。

- **常用 CLI 命令**：`init`、`create`、`list`（别名 `ls`）、`show`、`assign`、`link`、`unlink`、`comment`、`complete`、`block`、`unblock`、`archive`、`tail`。较少使用的命令包括 `watch`、`stats`、`runs`、`log`、`dispatch`、`daemon`、`gc`。
- **工作进程/编排型账号的工具集**：包含 `kanban_show`、`kanban_complete`、`kanban_block`、`kanban_heartbeat`、`kanban_comment`、`kanban_create`、`kanban_link` 等命令；那些在非调度器创建的任务中明确启用了 `kanban` 工具集的账号，还可使用 `kanban_list` 和 `kanban_unblock` 命令来管理看板中的任务流转。
- **调度器**默认在网关内部运行（通过 `kanban.dispatch_in_gateway: true` 参数启用） —— 它负责回收过期的任务请求、提升已准备就绪的任务优先级、以原子方式获取任务，并启动对应的账号。若连续出现 `failure_limit` 次启动失败（默认为 2 次，可通过 `kanban.failure_limit` 或每个任务的 `max_retries` 参数进行调整），调度器会自动将该任务标记为阻塞状态。
- **隔离机制**：看板本身是硬性隔离边界（工作进程的环境中会固定包含 `HERMES_KANBAN_BOARD` 环境变量）；而“租户”则是看板内的一个软性命名空间，用于实现工作路径与内存键值的隔离。

用户文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban

---

## 用户界面与其他功能

除了 CLI 和网关之外，还有以下几项值得了解的功能：

- **桌面应用**（`hermes desktop` / `hermes gui`）—— 专为 macOS/Linux/Windows 设计的原生 Electron 应用：支持流式聊天、会话列表、拖放及剪贴板粘贴文件功能、Cmd+K 快捷调色板、状态栏模型选择器、可自定义的快捷键、原生通知、实时子智能体监控窗口、VS Code Marketplace 主题，以及针对不同账号的远程网关登录功能（支持 OAuth 或用户名/密码认证），因此即便使用轻量级的本地 GUI，也能控制强大的远程智能体。
- **Web 控制面板**（`hermes dashboard`）—— 完整的管理员面板：可在浏览器中配置所有消息通道、MCP 目录、Webhook/钩子功能、内存设置，以及完整的账号构建器（包括模型、技能和 MCP 功能），同时还内置了 `hermes --tui` 聊天界面。该控制面板通过 OAuth/令牌机制进行访问保护。
- **兼容 OpenAI 的代理**（`hermes proxy`）—— 提供一个 `http://localhost:port` 地址的 OpenAI API 接口，其背后支持您当前登录的任何 OAuth 服务提供商（如 Claude Pro、ChatGPT Pro、SuperGrok）。您可以直接将 Codex CLI、Aider、Cline、Continue 或其他任意脚本指向该接口使用，无需提供 API 密钥。
- **自动化蓝图** —— 选择已命名的自动化流程后，Hermes 会询问您需要哪些功能（无需编写 Cron 语法）。一个自动化定义可同时生成控制面板表单、Slash 命令、智能体对话内容以及文档目录中的条目。
- **`memory` 工具的批量操作** —— 可传递一个包含添加/替换/删除操作的 `operations` 数组，这些操作会针对最终的字符预算以原子方式执行，因此即使单独执行添加操作会导致字符超出限制，通过批量操作仍可同时释放空间并添加新内容。
- **`session_search`** —— 基于 FTS5 算法实现，无需辅助大型语言模型，几乎可以视为免费功能。它仅提供一个工具，根据传入的参数不同会自动切换三种模式：检索模式（通过 `query` 参数）、滚动查找模式（通过 `session_id` 和 `around_message_id` 参数）、浏览模式（无参数）。
- **通过 SuperGrok OAuth 访问 xAI Grok** —— 使用您的 xAI 账号登录即可（无需 API 密钥）；该功能还支持 Cursor 的 `grok-composer-2.5-fast` 编程模型。

---

## Windows 系统特有问题

Hermes 在 Windows 系统上可直接运行（支持 PowerShell、cmd、Windows Terminal、git-bash mintty、VS Code 集成终端等）。大部分功能都能正常使用，但由于 Win32 与 POSIX 环境存在一些差异，我们遇到了一些问题 —— 请在发现新问题时在此处记录下来，以便后续使用者无需重复摸索。

### 输入/快捷键

**Alt+Enter 不会插入换行符** —— Windows Terminal（以及 mintty）会在 prompt_toolkit 接收到按键之前就将其用于全屏模式。建议改用 **Ctrl+Enter**（在 Windows 上 CLI 将其绑定为换行操作；原始的 Ctrl+J 也会产生相同效果，且不会造成问题）。若想查看终端是如何处理按键的，可从项目根目录运行 `python scripts/keystroke_diagnostic.py` 脚本。

### 配置/文件

**首次运行时会出现 HTTP 400 “未提供模型”错误** —— 原因是 `config.yaml` 文件被保存时带有 UTF-8 BOM 标记（Notepad 编辑器会自动添加此标记）。请将其重新保存为不带 BOM 的 UTF-8 格式；这样使用 `hermes config edit` 命令进行编辑时就能正常工作。

### `execute_code` / 沙箱环境

**沙箱子进程会抛出 WinError 10106 错误** —— 原因是该进程无法创建 `AF_INET` 类型的套接字。通常这是由于 Hermes 的环境清理机制移除了 `SYSTEMROOT`/`WINDIR`/`COMSPEC` 等路径（Python 的 `socket` 模块需要这些路径才能找到 `mswsock.dll` 文件），而非 Winsock LSP 存在问题。《tools/code_execution_tool.py` 文件中的 `_WINDOWS_ESSENTIAL_ENV_VARS` 允许列表可解决此问题；如果仍然出现该错误，可在 `execute_code` 块中输出 `os.environ` 的内容，确认 `SYSTEMROOT` 变量是否已被正确设置。

### 在 Windows 上进行测试

`scripts/run_tests.sh` 脚本仅支持 POSIX 环境（要求先运行 `.venv/bin/activate` 命令激活虚拟环境）；而 Hermes 安装目录下的 `venv/Scripts/` 目录中并未预装 pip/pytest 工具（为节省体积而未包含）。建议在系统级的 Python 环境中安装 pytest，然后直接使用 `-n 0` 参数运行测试（`pyproject.toml` 文件中的 `addopts` 部分已预先设置了 `-n` 参数）：

```bash
"/c/Program Files/Python311/python" -m pip install --user pytest pytest-xdist pyyaml
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/foo/test_bar.py -v --tb=short -n 0
```

（仅适用于 POSIX 环境的测试需要添加跳过机制——详情请参见下方“贡献者指南”中的跨平台保护列表。）

### 路径/文件系统

**行尾字符。** Git 可能会提示“LF 将被替换为 CRLF”，但这只是视觉上的差异——仓库中的 `.gitattributes` 文件会自动处理。请勿让编辑器将已提交的 POSIX 行尾格式的文件自动转换为 CRLF 格式。

**正斜杠在几乎所有地方都适用。** 所有的 Hermes 工具以及大多数 Windows API 都支持 `C:/Users/...` 这种路径格式。在代码和日志中建议使用正斜杠，这样可以避免在 bash 中出现需要转义的反斜杠。

---

## 故障排除

### 语音功能无法使用
1. 检查 config.yaml 文件中是否设置了 `stt.enabled: true`。
2. 确认对应的服务提供方已配置：可通过 `pip install faster-whisper` 安装相应组件，或设置 API 密钥。
3. 在网关端执行 `/restart` 命令；在 CLI 环境下则需退出程序后重新启动。

### 某工具不可用
1. 运行 `hermes tools` 命令，检查该平台是否已启用相应的工具集。
2. 部分工具需要环境变量（请查看 `.env` 文件）。
3. 启用工具后执行 `/reset` 命令重置配置。

### 模型/服务提供方相关问题
1. 运行 `hermes doctor` 命令，检查配置及依赖项是否正常。
2. 使用 `hermes auth` 命令重新认证 OAuth 服务提供方（或执行 `hermes auth add <provider>` 添加新提供方）。
3. 确认 `.env` 文件中包含正确的 API 密钥。
4. **Copilot 403 错误**：`gh auth login` 生成的令牌无法用于 Copilot API。必须通过 `hermes model` → GitHub Copilot 的专用 OAuth 设备码流程进行认证。

### 修改未生效
- **工具/技能问题**：执行 `/reset` 命令可启动带有更新后工具集的新会话。
- **配置更改问题**：在网关端执行 `/restart` 命令；在 CLI 环境下则需退出程序后重新启动。
- **代码更改问题**：重启 CLI 或网关进程。

### 技能未显示
1. 运行 `hermes skills list` 命令，确认相关技能已成功安装。
2. 使用 `hermes skills config` 命令检查该平台是否已启用相应技能。
3. 如需手动加载特定技能，可执行 `/skill name` 命令或使用 `hermes -s name` 参数。

### 网关相关问题
请先查看日志以定位问题：
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
├── tests/                # Extensive pytest suite (run via scripts/run_tests.sh)
└── website/              # Docusaurus docs site
```

配置文件：`~/.hermes/config.yaml`（用于设置参数），`~/.hermes/.env`（用于存储 API 密钥）——若已设置 `$HERMES_HOME`，则这两个文件均位于该路径下。

### 添加工具

需要准备两个文件。自动发现功能会导入任何包含顶层 `registry.register()` 调用的 `tools/*.py` 文件，但只有当某个工具的名称被加入工具集后，它才会向智能体*公开*可用。

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

**2. 将其集成到 `toolsets.py` 中的工具集中** —— 将该工具的名称添加到 `_HERMES_CORE_TOOLS`（所有平台通用）或特定的工具集中。

所有的处理函数都必须返回 JSON 字符串。在获取路径时请使用 `get_hermes_home()` 函数，切勿直接硬编码 `~/.hermes` 路径。对于仅限本地使用的自定义工具，建议在 `~/.hermes/plugins/` 目录下编写插件，而非修改核心代码 —— 详情请参阅开发者指南。

### 添加斜杠命令

1. 在 `hermes_cli/commands.py` 文件的 `COMMAND_REGISTRY` 中添加 `CommandDef` 定义；
2. 在 `cli.py` 文件中的 `process_command()` 函数中编写对应的处理逻辑；
3. （可选）在 `gateway/run.py` 文件中添加网关处理函数。

所有的相关组件（帮助文本、自动补全功能、Telegram 菜单、Slack 映射等）都会自动从这个中央注册表中获取对应信息。

### Agent 循环（概览）

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

请使用标准运行器——它能够确保与持续集成流程保持一致（隔离的运行环境、未设置的凭据、时区设置为 UTC、并行工作进程以及每项测试的独立子进程隔离）：

```bash
scripts/run_tests.sh                          # full suite
scripts/run_tests.sh tests/tools/             # one directory
scripts/run_tests.sh tests/tools/test_x.py    # one file
scripts/run_tests.sh -v --tb=long             # pass-through pytest flags
```

- 测试会自动将 `HERMES_HOME` 重定向至临时目录——绝不会修改真实的 `~/.hermes/` 目录。
- 脚本会依次检测 `.venv`、`venv`，以及共享工作区的虚拟环境。
- **Windows 系统**：该封装仅支持 POSIX 标准；如需使用直接调用 pytest 的解决方案，请参阅上文的“Windows 系统特有问题”部分。

**跨平台测试保护机制**：使用仅支持 POSIX 标准系统调用的测试需要添加跳过标记。代码库中已有的常见标记包括：
- 创建符号链接 → `@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require elevated privileges on Windows")`（参见 `tests/cron/test_cron_script.py`）
- POSIX 文件权限（如 0o600 等）→ `@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX mode bits not enforced on Windows")`（参见 `tests/hermes_cli/test_auth_toctou_file_modes.py`）
- `signal.SIGALRM` → 仅适用于 Unix 系统（参见 `tests/conftest.py::_enforce_test_timeout`）
- 实时 Winsock 相关功能/Windows 系统特有回归测试 → `@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific regression")`

如果被测试代码同时调用了 `platform.system()`、`platform.release()` 或 `platform.mac_ver()` 函数，仅修改 `sys.platform` 是不够的。因为这些函数会独立读取真实的操作系统信息，因此在 Windows 环境下将 `sys.platform` 设置为 `"linux"` 的测试仍会返回 `platform.system() == "Windows"`，从而执行 Windows 版本的逻辑。需同时修改这三个函数的值。

```python
monkeypatch.setattr(sys, "platform", "linux")
monkeypatch.setattr(platform, "system", lambda: "Linux")
monkeypatch.setattr(platform, "release", lambda: "6.8.0-generic")
```

如需示例代码，请参阅 `tests/agent/test_prompt_builder.py::TestEnvironmentHints`。

### 系统提示的运行环境部分

关于主机/后端的相关信息（操作系统、`$

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
