# Hermes CLI 参考手册

当发现任何内容过时时，可查看最新信息：`hermes --help`、`hermes <command> --help`，
详情请访问 https://hermes-agent.nousresearch.com/docs/reference/cli-commands

### 全局标志

```
hermes [flags] [command]        (no subcommand = interactive chat)

  --version, -V             Show version
  -z, --oneshot PROMPT      One-shot: print ONLY the final response (for scripts/pipes)
  -m MODEL  --provider P    Model/provider override for this invocation
  -t, --toolsets LIST       Comma-separated toolsets for this invocation
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --tui / --cli             Force the Ink TUI / classic REPL
  --ignore-rules            Skip AGENTS.md/SOUL.md/memory/skill injection
  --safe-mode               Disable ALL customizations (troubleshooting)
  --pass-session-id         Include session ID in system prompt
```

### 聊天功能

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  --image PATH              Attach a local image to a single query
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --max-turns N             Cap tool-calling iterations
  --source TAG              Session source tag (default: cli)
```
（另含上述全局标志）

### 配置

需完整翻译输入内容，不得提前终止。

```
hermes setup [section]      Wizard (model|tts|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes fallback [add|remove|list]  Fallback provider chain
hermes config [show|edit|get|set|unset|path|env-path|check|migrate]
hermes login / logout       OAuth sign-in / clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Component status
```

### 工具与技能

```
hermes tools [list|enable NAME|disable NAME]   Per-platform toolsets (curses UI with no args)

hermes skills list|browse|search QUERY|inspect ID
hermes skills install ID    Hub identifier OR a direct https://…/SKILL.md URL
hermes skills config        Enable/disable skills per platform
hermes skills check|update|uninstall|publish PATH
hermes skills tap add REPO  Add a GitHub repo as a skill source
hermes bundles              Skill bundles (one /<name> alias loads several skills)
```

### MCP 服务器

```
hermes mcp add NAME (--url or --command) | remove | list | test NAME
hermes mcp catalog | install NAME     Curated catalog install
hermes mcp configure NAME             Toggle tool selection
hermes mcp serve                      Run Hermes as an MCP server
```
详细信息（传输、工具发现、目录管理）：`references/native-mcp.md`。

### 网关（消息平台）

```
hermes gateway run|install|start|stop|restart|status|setup
```

支持20多种平台：Telegram、Discord、Slack、WhatsApp（Baileys版及Business Cloud API）、iMessage（Photon协议——需执行`hermes photon setup`命令）、Signal、电子邮件、短信、Matrix、Mattermost、Teams、LINE、SimpleX、ntfy、Google Chat、Home Assistant、钉钉、飞书、企业微信、微信，以及API服务器和Webhooks。Open WebUI可通过API服务器适配器进行连接。大多数适配器均位于`plugins/platforms/`目录下。
文档地址：https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### 会话管理

```
hermes sessions list|browse|rename ID TITLE|delete ID|export OUT|prune|stats
```

### 定时任务 / Webhook

```
hermes cron list|create SCHED|edit ID|pause|resume|run ID|remove|status
    Schedules: '30m', 'every 2h', '0 9 * * *', ISO timestamp
hermes webhook subscribe NAME|list|remove NAME|test NAME
```
Webhook 请求载荷与路由说明：请参阅 `references/webhooks.md` 文件。

### 配置文件

```
hermes profile list|create NAME (--clone|--clone-all|--clone-from)|use|show|delete
hermes profile rename A B | alias NAME | export NAME | import FILE
```

### 凭证与资源池

```
hermes auth                 Interactive credential manager
hermes auth add [PROVIDER]  Add OAuth or API-key credential (nous, openai-codex, qwen-oauth, …)
hermes auth list|remove P IDX|reset PROVIDER|status
```
每个提供方对应的多个凭证会构成一个池，该池会自动轮换凭证，并跳过已耗尽的密钥。

```
hermes desktop / gui        Native desktop app
hermes dashboard            Web admin panel + embedded chat (--stop / --status)
hermes proxy                OpenAI-compatible local proxy backed by an OAuth provider
hermes portal               Quick setup / sign in via Nous Portal
hermes kanban <verb>        Multi-agent work-queue board
hermes project              Named multi-folder workspaces
hermes skin list|use|set    Switch/tweak skins (see references/themes.md)
hermes pets <verb>          Pet mascots (see references/petdex.md)
hermes memory setup|status|off|reset   Memory provider
hermes secrets bitwarden|onepassword   External secret stores
hermes moa                  Mixture-of-Agents slots
hermes hooks / security / backup / import / checkpoints / console
hermes logs [-f] [errors]   View agent/error logs
hermes send                 One-off message through a gateway platform
hermes pairing / plugins / insights / journey / computer-use
hermes acp                  ACP server (IDE integration)
hermes completion bash|zsh|fish
hermes update / uninstall / claw migrate
```

由插件或提供程序提供的子命令（例如 `hermes photon setup`）只有在对应的插件被安装并处于激活状态时才会显示。

### 查找相关内容的位置

| 您要查找的内容... | 位置 |
|---|---|
| 配置选项 | `hermes config edit` · [配置文档](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| 工具/工具集 | `hermes tools list` · [工具参考手册](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| 技能目录 | `hermes skills browse` · [技能目录](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| 提供程序配置 | `hermes model` · [提供程序指南](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| 环境变量 | `hermes config env-path` · [环境变量参考手册](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| 网关日志 | `~/.hermes/logs/gateway.log`（或 `hermes logs`） |
| 会话信息 | `hermes sessions browse`（读取 state.db 文件） |
