---
sidebar_position: 1
title: "CLI Commands Reference"
description: "Authoritative reference for Hermes terminal commands and command families"
---

# CLI 命令参考手册

本页面介绍了您在终端中可使用的**命令行指令**。

有关聊天界面内的斜杠命令，请参阅 [斜杠命令参考手册](./slash-commands.md)。

## 全局入口点

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项

| Option | Description |
|--------|-------------|
| `--version`, `-V` | Show version and exit. |
| `--profile <name>`, `-p <name>` | Select which Hermes profile to use for this invocation. Overrides the sticky default set by `hermes profile use`. |
| `--resume <session>`, `-r <session>` | Resume a previous session by ID or title. The keyword `latest` resumes the most recent session (workspace-scoped, same lookup as `-c`). |
| `--continue [name]`, `-c [name]` | Resume the most recent session, or the most recent session matching a title. |
| `--in <dir>` | Change into `<dir>` before starting or resuming. Scopes `--resume latest` / `-c` lookups to that directory's workspace and keeps the session there (skips the recorded-cwd restore). |
| `--worktree`, `-w` | Start in an isolated git worktree for parallel-agent workflows. |
| `--yolo` | Bypass dangerous-command approval prompts. |
| `--pass-session-id` | Include the session ID in the agent's system prompt. |
| `--ignore-user-config` | Ignore `~/.hermes/config.yaml` and fall back to built-in defaults. Credentials in `.env` are still loaded. |
| `--ignore-rules` | Skip auto-injection of `AGENTS.md`, `SOUL.md`, `.cursorrules`, memory, and preloaded skills. |
| `--tui` | Launch the [TUI](../user-guide/tui.md) instead of the classic CLI. Equivalent to `HERMES_TUI=1`. Always wins over `display.interface`. |
| `--cli` | Force the classic prompt_toolkit REPL. Use this to override `display.interface: tui` for a single invocation. |
| `--dev` | With `--tui`: run the TypeScript sources directly via `tsx` instead of the prebuilt bundle (for TUI contributors). |

## 最上层命令

| Command | Purpose |
|---------|---------|
| `hermes chat` | Interactive or one-shot chat with the agent. |
| `hermes model` | Interactively choose the default provider and model. |
| `hermes moa` | Configure named Mixture of Agents presets selectable from the model picker. |
| `hermes fallback` | Manage fallback providers tried when the primary model errors. |
| `hermes gateway` | Run or manage the messaging gateway service. |
| `hermes proxy` | Local OpenAI-compatible proxy that attaches OAuth provider credentials. See [Subscription Proxy](../user-guide/features/subscription-proxy.md). |
| `hermes egress` | Outbound credential-injection firewall for remote terminal sandboxes (iron-proxy). Disabled by default. See [Egress proxy](../user-guide/egress/iron-proxy.md). |
| `hermes lsp` | Manage Language Server Protocol integration (semantic diagnostics for write_file/patch). |
| `hermes setup` | Interactive setup wizard for all or part of the configuration. |
| `hermes whatsapp` | Configure and pair the WhatsApp bridge. |
| `hermes whatsapp-cloud` | Configure the official Meta WhatsApp Business Cloud API adapter (Business account + public webhook required). Distinct from `hermes whatsapp` (Baileys personal-account bridge). |
| `hermes slack` | Slack helpers (currently: generate the app manifest with every command as a native slash). |
| `hermes auth` | Manage credentials — add, list, remove, reset, status, logout. Handles OAuth flows for Codex/Nous/Anthropic. |
| `hermes login` / `logout` | **Deprecated** — use `hermes auth` instead. |
| `hermes send` | Send a one-shot message to a configured messaging platform (Telegram, Discord, Slack, Signal, SMS, …). Useful from shell scripts, cron jobs, CI hooks, and monitoring daemons — no agent loop, no LLM. |
| `hermes peer` | Register peer Hermes gateways on other machines and DM their agents' canonical Bot Chats (`hermes peer dm <peer>[/<agent>] "…"`). The transport behind cross-machine bot-to-bot messaging. |
| `hermes secrets` | Manage external secret sources (currently Bitwarden Secrets Manager) for pulling API keys at process startup instead of from `~/.hermes/.env`. |
| `hermes migrate` | Diagnose and (optionally) rewrite `config.yaml` to replace references to retired models or deprecated settings (e.g. `migrate xai`). |
| `hermes status` | Show agent, auth, and platform status. |
| `hermes cron` | Inspect and tick the cron scheduler. |
| `hermes kanban` | Multi-profile collaboration board (tasks, links, dispatcher). |
| `hermes project` | Manage named, multi-folder workspaces (projects). Anchors desktop session grouping and, when bound to a kanban board, gives tasks a deterministic worktree + branch convention. State is per-profile. |
| `hermes webhook` | Manage dynamic webhook subscriptions for event-driven activation. |
| `hermes hooks` | Inspect, approve, or remove shell-script hooks declared in `config.yaml`. |
| `hermes doctor` | Diagnose config and dependency issues. |
| `hermes security audit` | On-demand supply-chain audit (OSV.dev) for the venv, plugin requirements, and pinned MCP servers. |
| `hermes approvals` | Approval-prompt tools — mine approval history into allowlist proposals. |
| `hermes dump` | Copy-pasteable setup summary for support/debugging. |
| `hermes prompt-size` | Show a byte breakdown of the system prompt + tool schemas (skills index, memory, profile). Runs offline. |
| `hermes debug` | Debug tools — upload logs and system info for support. |
| `hermes backup` | Back up Hermes home directory to a zip file. |
| `hermes checkpoints` | Inspect / prune / clear `~/.hermes/checkpoints/` (the shadow store used by `/rollback`). Run with no args for a status overview. |
| `hermes import` | Restore a Hermes backup from a zip file. |
| `hermes logs` | View, tail, and filter agent/gateway/error log files. |
| `hermes config` | Show, edit, migrate, and query configuration files. |
| `hermes skin` | List, switch, and tweak display skins. |
| `hermes console` | Open the safe Hermes command console. |
| `hermes pairing` | Approve or revoke messaging pairing codes. |
| `hermes skills` | Browse, install, publish, audit, and configure skills. |
| `hermes bundles` | Group several skills under a single `/<name>` slash command. See [Skill Bundles](../user-guide/features/skills.md#skill-bundles). |
| `hermes curator` | Background skill maintenance — status, run, pause, pin. See [Curator](../user-guide/features/curator.md). |
| `hermes journey` (aliases `learning`, `memory-graph`) | Timeline of learned skills + memories over time. |
| `hermes memory` | Configure external memory provider. Plugin-specific subcommands (e.g. `hermes honcho`) register automatically when their provider is active. |
| `hermes acp` | Run Hermes as an ACP server for editor integration. |
| `hermes mcp` | Manage MCP server configurations and run Hermes as an MCP server. |
| `hermes plugins` | Manage Hermes Agent plugins (install, enable, disable, remove). |
| `hermes portal` | Nous Portal status, subscription link, and Tool Gateway routing. See [Tool Gateway](../user-guide/features/tool-gateway.md). |
| `hermes tools` | Configure enabled tools per platform. |
| `hermes computer-use` | Install or check the Computer Use (cua-driver) backend (macOS/Windows/Linux). |
| `hermes pets` | Browse, install, and select [petdex](../user-guide/features/pets.md) animated pets shown across the CLI, TUI, and desktop app. Subcommands: `list`, `install`, `select`, `show`, `off`, `scale`, `remove`, `doctor`. |
| `hermes sessions` | Browse, export, prune, rename, and delete sessions. |
| `hermes insights` | Show token/cost/activity analytics. |
| `hermes claw` | OpenClaw migration helpers. |
| `hermes import-agent` | Import a Claude Code (`~/.claude`) or Codex CLI (`~/.codex`) setup. |
| `hermes dashboard` | Launch the web dashboard for managing config, API keys, and sessions. |
| `hermes serve` | Start the Hermes backend server (headless; powers the desktop app and remote backends). |
| `hermes desktop` (alias `gui`) | Build and launch the native Electron desktop app. |
| `hermes profile` | Manage profiles — multiple isolated Hermes instances. |
| `hermes completion` | Print shell completion scripts (bash/zsh/fish). |
| `hermes --version` | Show version information. |
| `hermes update` | Pull latest code and reinstall dependencies. `--check` previews without installing; `--backup` takes a pre-pull `HERMES_HOME` snapshot. |
| `hermes uninstall` | Remove Hermes from the system. |

## `hermes chat` 命令

```bash
hermes chat [options]
```

常用选项：

| Option | Description |
|--------|-------------|
| `-q`, `--query "..."` | Seed the session with a prompt. On a real TTY the prompt is submitted **literally** as the first turn of a normal interactive session (it is never parsed as a slash command or `!` shell escape) and the session stays open — ideal for OS launchers and desktop integrations. With `--oneshot`, `-Q`, or non-TTY stdio it answers and exits. |
| `--query-file PATH` | Read the query from a file (`-` = stdin). Nothing is shell-interpreted, so quotes, `$(...)`, and backticks arrive verbatim — use this for programmatic or untrusted message bodies (Bot Mode teammate DMs use it). Mutually exclusive with `-q`. |
| `--oneshot` | With `-q`/`--query-file`: answer the query and exit (the pre-0.21 single-query behavior) instead of seeding an interactive session. Implied on non-TTY stdio and by `-Q`. |
| `-m`, `--model <model>` | Override the model for this run. |
| `-t`, `--toolsets <csv>` | Enable a comma-separated set of toolsets. |
| `--provider <provider>` | Force a provider: `auto`, `openrouter`, `nous`, `openai-codex`, `copilot-acp`, `copilot`, `anthropic`, `gemini`, `huggingface`, `novita` (aliases `novita-ai`, `novitaai`), `openai-api`, `zai`, `kimi-coding`, `kimi-coding-cn`, `minimax`, `minimax-cn`, `minimax-oauth`, `kilocode`, `xiaomi`, `arcee`, `gmi`, `upstage` (alias `solar`), `alibaba`, `alibaba-cn`, `alibaba-coding-plan` (alias `alibaba_coding`), `alibaba-coding-plan-cn`, `alibaba-token-plan`, `alibaba-token-plan-cn`, `deepseek`, `nvidia`, `ollama-cloud`, `xai` (alias `grok`), `xai-oauth` (alias `grok-oauth`), `qwen-oauth`, `bedrock`, `opencode-zen`, `opencode-go`, `opencode-free` (aliases `free`, `opencode_free`; keyless), `commandcode`, `commandcode-anthropic`, `ai-gateway`, `azure-foundry`, `lmstudio`, `stepfun`, `tencent-tokenhub` (alias `tencent`, `tokenhub`), `router` (aliases `ramp-router`, `ramp`), `nebius-token-factory` (aliases `nebius`, `nebius-tf`, `tokenfactory`), `tencent-tokenplan` (aliases `tokenplan`, `tencent-lkeap`). |
| `-s`, `--skills <name>` | Preload one or more skills for the session (can be repeated or comma-separated). |
| `-v`, `--verbose` | Verbose output. |
| `-Q`, `--quiet` | Programmatic mode: suppress banner/spinner/tool previews. |
| `--image <path>` | Attach a local image to a single query. |
| `--resume <session>` / `--continue [name]` | Resume a session directly from `chat`. |
| `--worktree` | Create an isolated git worktree for this run. |
| `--checkpoints` | Enable filesystem checkpoints before destructive file changes. |
| `--yolo` | Skip approval prompts. |
| `--pass-session-id` | Pass the session ID into the system prompt. |
| `--ignore-user-config` | Ignore `~/.hermes/config.yaml` and use built-in defaults. Credentials in `.env` are still loaded. Useful for isolated CI runs, reproducible bug reports, and third-party integrations. |
| `--ignore-rules` | Skip auto-injection of `AGENTS.md`, `SOUL.md`, `.cursorrules`, persistent memory, and preloaded skills. Combine with `--ignore-user-config` for a fully isolated run. |
| `--safe-mode` | Troubleshooting mode: disable ALL customizations — user config, rules/memory injection, plugins, shell hooks, and MCP servers (implies `--ignore-user-config` and `--ignore-rules`). Use to isolate whether a problem comes from your setup or from Hermes itself. |
| `--source <tag>` | Session source tag for filtering (default: `cli`). Use `tool` for third-party integrations that should not appear in user session lists. |
| `--max-turns <N>` | Maximum tool-calling iterations per conversation turn (default: 500, or `agent.max_turns` in config). |

示例：

```bash
hermes
hermes chat -q "Summarize the latest PRs"          # seeds an interactive session
hermes chat --oneshot -q "Summarize the latest PRs"  # answer and exit
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "Return only JSON"
hermes chat --worktree -q "Review this repo and open a PR"
hermes chat --ignore-user-config --ignore-rules -q "Repro without my personal setup"
hermes chat --safe-mode -q "Is this bug mine or Hermes'?"
```

### `hermes -z <prompt>` — 脚本化单次调用模式

对于通过程序方式调用的用户（如Shell脚本、CI系统、cron作业，或是将提示语通过管道传递给代理的父进程），`hermes -z` 是最纯粹的单次调用入口：**输入一个提示语，即可得到最终响应文本，标准输出和标准错误中不会出现任何其他内容**。没有欢迎横幅、没有加载指示器、没有工具预览信息，也没有 `Session:` 行——仅有以纯文本形式呈现的代理最终回复。

```bash
hermes -z "What's the capital of France?"
# → Paris.

# Parent scripts can cleanly capture the response:
answer=$(hermes -z "summarize this" < /path/to/file.txt)
```

单次运行覆盖设置（不会修改 `~/.hermes/config.yaml` 文件）：

| 参数 | 对应的环境变量 | 用途 |
|---|---|---|
| `-m` / `--model <model>` | `HERMES_INFERENCE_MODEL` | 覆盖本次运行的模型 |
| `--provider <provider>` | _（无）_ | 覆盖本次运行的提供方 |
| `--usage-file <path>` | _（无）_ | 在运行结束后生成 JSON 格式的使用报告（详见下文） |

```bash
hermes -z "…" --provider openrouter --model openai/gpt-5.5
# or:
HERMES_INFERENCE_MODEL=anthropic/claude-sonnet-4.6 hermes -z "…"
```

同样的智能体、同样的工具、同样的能力——只不过去除了所有交互式及界面装饰层。如果还需要在输出文本中包含工具的运行结果，请改用 `hermes chat --oneshot -q` 命令；而 `-z` 选项则是专门用于表示“我只想要最终答案”。

#### `--usage-file` — 用于记录流水线使用情况的 JSON 报告

通过命令 `hermes -z "…" --usage-file /path/report.json`，系统会在运行结束后生成一份机器可读的使用情况报告，其中包含 `estimated_cost_usd`、`input_tokens` / `output_tokens` / `cache_read_tokens` / `cache_write_tokens` / `reasoning_tokens` / `total_tokens`、`api_calls`、`model`、`provider`、`session_id`、`service_tier` 以及 `completed` / `failed` 等字段信息。即便运行失败，该报告也会被生成，因此批量流水线始终能够准确掌握成本支出情况。此选项仅在 `-z`/`--oneshot` 模式下有效，且即使报告生成失败，也不会影响运行本身的结果。

```bash
hermes -z "summarize this repo" --usage-file /tmp/usage.json
jq .estimated_cost_usd /tmp/usage.json
```

## `hermes model`

交互式提供程序与模型选择器。**该命令用于添加新的提供程序、配置 API 密钥以及执行 OAuth 流程。** 请在终端中运行此命令，而非在正在进行的 Hermes 聊天会话中执行。

```bash
hermes model
```

在以下情况下请使用此功能：
- **添加新的提供方**（OpenRouter、Anthropic、Copilot、DeepSeek、自定义等）
- 登录基于 OAuth 的提供方账户（Anthropic、Copilot、Codex、Nous Portal）
- 输入或更新 API 密钥
- 从特定提供方的模型列表中选择
- 配置自定义/自托管的端点
- 将新的默认设置保存到配置文件中

:::warning hermes model 与 /model 的区别——需加以区分
**`hermes model`**（在终端中运行，独立于任何 Hermes 会话）是**完整的提供方设置向导**。它能够添加新提供方、执行 OAuth 流程、提示输入 API 密钥以及配置端点。

而 **`/model`**（在活跃的 Hermes 聊天会话中输入）仅能**在您已设置的提供方和模型之间切换**，无法添加新提供方、执行 OAuth 流程或提示输入 API 密钥。

**如果您需要添加新的提供方**：请先退出当前的 Hermes 会话（使用 `Ctrl+C` 或 `/quit`），然后在终端命令行中运行 `hermes model`。
:::

### `/model` 斜杠命令（会话进行中使用）

无需离开当前会话，即可在已配置的模型之间切换：

```
/model                              # Show current model and available options
/model claude-sonnet-4              # Switch model (auto-detects provider)
/model zai:glm-5                    # Switch provider and model
/model custom:qwen-2.5              # Use model on your custom endpoint
/model custom                       # Auto-detect model from custom endpoint
/model custom:local:qwen-2.5        # Use a named custom provider
/model openrouter:anthropic/claude-sonnet-4  # Switch back to cloud
```

默认情况下，对 `/model` 的更改**仅适用于当前会话**。若要将该更改永久保存到 `config.yaml` 中，请添加 `--global` 参数（或者将 `model.persist_switch_by_default: true` 设置为真，以便使所有更改都得以持久化）：

```
/model claude-sonnet-4 --global     # Switch and save as new default
```

:::info 为何我只看到 OpenRouter 模型？
如果您仅配置了 OpenRouter，/model 组件将只会显示 OpenRouter 相关的模型。若要添加其他提供商（如 Anthropic、DeepSeek、Copilot 等），请先退出当前会话，然后通过终端运行 `hermes model` 命令。
:::

当使用 `--global` 参数时，提供商及基础 URL 的更改会与模型信息一同被保存到 `config.yaml` 文件中。一旦切换回默认端点，旧的基准 URL 会被清除，从而避免其影响其他提供商的连接。

## `hermes gateway`

```bash
hermes gateway <subcommand>
```

子命令：

| 子命令 | 描述 |
|----------|------|
| `run` | 在前台运行网关。适用于 WSL、Docker 和 Termux 环境。 |
| `start` | 启动已安装的 systemd/launchd 后台服务。 |
| `stop` | 停止该服务（或前台进程）。 |
| `restart` | 重启该服务。 |
| `status` | 显示服务状态。 |
| `list` | 列出**所有配置文件**，以及每个配置文件的网关当前是否正在运行（如有 PID 也会一并显示）。当您同时运行多个配置文件并希望获得整体概览时，此功能非常实用。 |
| `install` | 作为 systemd（Linux）或 launchd（macOS）后台服务进行安装。 |
| `uninstall` | 卸载已安装的服务。 |
| `setup` | 交互式消息平台设置。 |
| `migrate-legacy` | 删除因早期版本安装而遗留的旧版 `hermes.service` 单元文件。配置文件对应的单元文件（`hermes-gateway-<profile>.service`）以及无关服务不会受到影响。可用参数：`--dry-run`、`-y`/`--yes`。 |
| `enroll` | 实验性功能：将此网关与中继连接器关联，并为基于连接器的平台保存中继凭据。详情请参阅 [Hermes Relay](/user-guide/messaging/relay)。 |

选项：

| 选项 | 描述 |
|------|------|
| `--all` | 在 `start` / `restart` / `stop` 模式下：会对**所有配置文件**对应的网关生效，而不仅限于当前激活的 `HERMES_HOME`。如果您同时运行多个配置文件，并希望在执行 `hermes update` 后同时重启它们，此选项非常有用。 |
| `--no-supervise` | 在 `run` 模式下：在 s6-overlay Docker 镜像内部，取消自动监控功能，采用 pre-s6 的前台进程机制——网关作为容器的主进程运行，且不会自动重启。在 s6 镜像外部则无作用。该选项等同于设置 `HERMES_GATEWAY_NO_SUPERVISE=1`。 |
| `--external-supervisor` | 在 `run` 模式下：指定由外部进程管理器来负责管理前台网关。当使用 `sudo`、`env -i` 或其他封装工具移除了 launchd/systemd 的原生环境标记时，可使用此选项。此时，通过聊天界面发起的重启或更新操作会将控制权交还给该外部管理器，而非生成一个新的独立进程来替代原网关。 |

`--external-supervisor` 实际上是一种重启策略约定：通过聊天界面发起的重启或服务重启操作会以状态码 `75` 结束，因此外部管理器的监控组件必须在该非零退出码之后重新启动网关。对于 systemd，应使用 `Restart=on-failure` 或 `Restart=always`，并且不要在 `RestartPreventExitStatus` 中包含 `75`；而对于 launchd，则需配置 `KeepAlive` 参数，以便在重启失败后自动重新启动网关。若未设置此类策略，即便请求重启，网关也会保持停止状态。

`hermes gateway enroll` 命令支持 `--token`、`--connector-url`、`--gateway-id` 和 `--wake-url` 参数。该命令会将注册令牌与连接器进行交换，然后将生成的 `GATEWAY_RELAY_ID`、`GATEWAY_RELAY_SECRET`、`GATEWAY_RELAY_DELIVERY_KEY`、可选的 `GATEWAY_RELAY_URL`，以及在使用 `--wake-url` 时生成的 `GATEWAY_RELAY_WAKE_URL` 值写入当前活跃配置文件的 `.env` 文件中。

:::提示 WSL 用户
建议使用 `hermes gateway run` 而非 `hermes gateway start`——WSL 对 systemd 的支持并不可靠。为确保任务持久运行，可将其封装在 tmux 中：`tmux new -s hermes 'hermes gateway run'`。详情请参阅 [WSL 常见问题](/reference/faq#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails)。
:::

## `hermes lsp`

```bash
hermes lsp <subcommand>
```

用于管理 Language Server Protocol 集成功能。LSP 会在后台运行真正的语言服务器（如 pyright、gopls、rust-analyzer 等），并将这些服务器生成的诊断信息传递给 `write_file` 和 `patch` 函数所使用的写入后检查机制。该功能的启用以检测是否处于 Git 工作区为条件——仅当当前工作目录或正在编辑的文件位于 Git 工作树中时，LSP 才会启动。

子命令：

| 子命令 | 描述 |
|----------|------|
| `status` | 显示服务状态、已配置的语言服务器以及安装状态。 |
| `list` | 列出所有受支持的语言服务器。若需跳过未安装的服务器，可使用 `--installed-only` 参数。 |
| `install <id>` | 立即安装指定语言服务器的二进制文件。 |
| `install-all` | 安装所有有已知自动安装方案的语言服务器。 |
| `restart` | 销毁正在运行的客户端，以便下次编辑时重新启动相应服务。 |
| `which <id>` | 显示指定语言服务器的最终二进制文件路径。 |

如需完整指南、支持的语言列表以及相关配置选项，请参阅 [LSP — 语义诊断](/user-guide/features/lsp)。

## `hermes setup`

```bash
hermes setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset] [--quick] [--reconfigure] [--portal]
```

**最简便的方式：** 使用命令 `hermes setup --portal` —— 通过 OAuth 登录 Nous Portal，即可一次性完成配置并启用[工具网关](../user-guide/features/tool-gateway.md)。

**首次运行时：** 程序会启动首次配置向导。

**已配置过的用户：** 直接进入完整的重新配置向导——每个提示项都会以当前设置的值作为默认值，按回车键即可保留该值，或输入新值。无需菜单导航。

如需直接跳转至特定配置部分，而非完整走完向导，可参考下表：

| 部分 | 描述 |
|---------|-------------|
| `model` | 提供商与模型配置。 |
| `terminal` | 终端后端及沙箱环境配置。 |
| `gateway` | 消息传递平台配置。 |
| `tools` | 按平台启用或禁用各类工具。 |
| `agent` | 智能体行为设置。 |

可选参数：

| 参数 | 描述 |
|--------|-------------|
| `--quick` | 适用于已配置过的用户：仅询问缺失或未设置的选项，已配置的项将直接跳过。 |
| `--non-interactive` | 不显示提示，直接使用默认值或环境变量中的值。 |
| `--reset` | 在开始配置前将所有设置重置为默认值。 |
| `--reconfigure` | 兼容旧版本的别名——在已安装的环境中直接执行 `hermes setup` 即会默认执行此操作。 |
| `--portal` | 一次性完成 Nous Portal 配置：通过 OAuth 登录，将 Nous 设定为推理提供商，并启用[工具网关](../user-guide/features/tool-gateway.md)，跳过其余配置步骤。 |

## `hermes portal`

```bash
hermes portal [status|open|tools]
```

可检查 Nous Portal 的认证状态、Tool Gateway 的路由情况，并跳转至订阅页面。若不指定子命令，则会执行 `status` 操作。

| 子命令 | 描述 |
|----------|------|
| `status`（默认值） | 显示 Portal 的认证状态以及各工具对应的 Tool Gateway 路由汇总信息。未指定子命令时也会显示该内容。 |
| `open` | 在您默认的浏览器中打开 `portal.nousresearch.com/manage-subscription` 页面。 |
| `tools` | 列出所有 Tool Gateway 合作伙伴（Firecrawl、FAL、OpenAI TTS、Browser Use、Modal），以及哪些工具是通过 Nous 进行路由的。 |

如需配置 Gateway 本身，请参阅 [Tool Gateway](../user-guide/features/tool-gateway.md)。关于一次性设置流程，请参考上文中的 `hermes setup --portal` 命令。

## `hermes whatsapp`

```bash
hermes whatsapp
```

执行 WhatsApp 配对/设置流程，包括模式选择与二维码配对操作。  

## `hermes slack`

```bash
hermes slack manifest              # print manifest to stdout
hermes slack manifest --write      # write to ~/.hermes/slack-manifest.json
hermes slack manifest --long-description-file AGENTS.md --write
hermes slack manifest --slashes-only  # just the features.slash_commands array
```

该工具会生成一个 Slack 应用清单文件，将 `COMMAND_REGISTRY` 中的所有网关命令（如 `/btw`、`/stop`、`/model` 等）都注册为一级 Slack 斜杠命令——从而实现与 Discord 和 Telegram 的功能对等。只需将生成的输出内容粘贴到您的 Slack 应用配置页面：[https://api.slack.com/apps](https://api.slack.com/apps) → 所选应用 → **Features → App Manifest → Edit**，最后点击 **Save** 即可。如果权限范围或斜杠命令发生变更，Slack 会提示您重新安装应用。

| 参数 | 默认值 | 用途 |
|------|---------|------|
| `--write [路径]` | stdout | 将输出写入文件而非标准输出。仅使用 `--write` 时，内容将写入 `$HERMES_HOME/slack-manifest.json` 文件。 |
| `--name NAME` | `Hermes` | 机器人在 Slack 中显示的名称。 |
| `--description DESC` | 默认描述文本 | 显示在 Slack 应用目录中的机器人描述。 |
| `--long-description TEXT` | 未设置 | 直接设置 `display_information.long_description` 的内容（长度需在 175 至 4,000 字符之间）。该参数与 `--slashes-only` 不兼容。 |
| `--long-description-file PATH` | 未设置 | 从 UTF-8 格式的文本文件中读取长描述内容，并保持其原有格式。该参数与 `--long-description` 互斥，且与 `--slashes-only` 不兼容。 |
| `--slashes-only` | 关闭 | 仅输出 `features.slash_commands` 部分，以便用于手动维护的清单文件中。 |

在执行 `hermes update` 后，建议再次运行 `hermes slack manifest --write`，以便将新增的命令纳入清单。

## `hermes send`

```bash
hermes send --to <target> "message text"
hermes send --to <target> --file <path>
echo "message" | hermes send --to <target>
hermes send --list [platform]
```

无需启动代理或网关循环，即可向已配置的消息平台发送一次性消息。该功能会复用网关中预先配置的凭证（`~/.hermes/.env` 和 `~/.hermes/config.yaml`），因此运维脚本、定时任务、CI 钩子以及监控进程都无需为每个平台重新实现 REST 客户端，即可发送状态更新信息。

对于基于机器人令牌的平台（如 Telegram、Discord、Slack、Signal、短信及 WhatsApp-CloudAPI），无需运行网关——`hermes send` 会直接与这些平台的 REST 接口通信。而那些需要持久适配器的插件平台，则仍需运行中的网关。

| 选项 | 描述 |
|------|------|
| `-t`, `--to <TARGET>` | 消息发送目标。支持格式：`platform`（使用主频道）、`platform:chat_id`、`platform:chat_id:thread_id` 或 `platform:#channel-name`。示例：`telegram`、`telegram:-1001234567890`、`discord:#ops`、`slack:C0123ABCD`、`signal:+15551234567`。 |
| `-f`, `--file <PATH>` | 从指定路径读取消息内容（仅支持文本文件，如日志、报告或 Markdown 文件）。若需从标准输入读取内容，可使用 `-`。若要发送图片或其他二进制文件，请使用 `MEDIA:<path>`（见下文）。 |
| `-s`, `--subject <LINE>` | 在消息内容前添加主题行/标题行。 |
| `-l`, `--list [platform]` | 列出所有平台中已配置的发送目标（或仅列出指定平台的目标）。 |
| `-q`, `--quiet` | 成功时抑制标准输出——在脚本中使用非常方便（只需依赖退出码即可）。 |
| `--json` | 以原始 JSON 格式输出结果，而非可读文本格式。 |
如果既未提供位置参数形式的 `message`，也未使用 `--file` 选项，当输入端不是终端设备时，`hermes send` 将从标准输入读取数据。退出码含义如下：成功时为 `0`，传输或后端处理失败时为 `1`，使用错误时为 `2`。

### 发送图片及其他媒体文件

`--file` 选项仅适用于*文本*类型的内容。若要将图片、文档、视频或音频文件作为平台原生附件发送，需在消息文本中使用 `MEDIA:<本地路径>` 指令来引用该文件：

```bash
hermes send --to telegram "MEDIA:/tmp/screenshot.png"
hermes send --to telegram "Build chart for today MEDIA:/tmp/chart.png"   # with caption
hermes send --to discord:#ops "MEDIA:/tmp/report.pdf"
```

默认情况下，图片文件会以照片形式发送（如 Telegram 等平台会对这些图片进行重新压缩）。若希望以未压缩的文件附件形式发送，可在消息中添加 `[[as_document]]` 标签。

```bash
hermes send --to telegram "[[as_document]] MEDIA:/tmp/screenshot.png"
```

示例：

```bash
hermes send --to telegram "deploy finished"
echo "RAM 92%" | hermes send --to telegram:-1001234567890
hermes send --to discord:#ops --file /tmp/report.md
hermes send --to slack:#eng --subject "[CI]" --file build.log
hermes send --list                  # all platforms
hermes send --list telegram         # filter by platform
```



## `hermes peer` 命令

```bash
hermes peer add <name> --url http://host:port --key <API_SERVER_KEY>
hermes peer list
hermes peer dm <peer>[/<agent>] "message"
hermes peer run <peer>[/<agent>] --idempotency-key <key> "message"
hermes peer status <peer>[/<agent>] <run_id>
hermes peer stop <peer>[/<agent>] <run_id>
hermes peer remove <name>
```

可在不同机器之间实现机器人间的私信通信。你可以将另一个 Hermes 网关（任何运行 `api_server` 平台的机器）注册为*对等节点*，然后向其代理发送消息：使用命令 `hermes peer dm` 即可通过该对等节点的 API 服务器找到远程代理的标准化**机器人聊天**会话，让该代理先执行一轮对话，随后将回复输出到标准输出中——这实际上就是本地命令 `hermes -p <bot> chat --in ~ -c "Bot Chat" …` 的跨机器版本。

仅使用 `<peer>` 可直接联系对等节点网关的主代理；而使用 `<peer>/<agent>` 则可以定位多路复用型对等节点上指定名称的代理（该代理通过其 `/p/<profile>/` 接口被访问）。

| 子命令 | 描述 |
|--------|-------------|
| `add <名称> --url <URL> [--key <密钥>] [--note TEXT]` | 注册或更新一个对等节点。该 URL 会被保存到 `config.yaml` 的 `bot_peers` 字段中；而密钥则作为 `HERMES_PEER_<名称>_KEY` 存储在 `~/.hermes/.env` 文件中。 |
| `list` | 列出所有对等节点以及每个节点的密钥配置情况。 |
| `dm <对等节点>[/<智能体>] [消息内容]` | 向对应智能体的标准 Bot Chat 发送消息并显示回复内容（使用 `--json` 可获得机器可读的输出格式；默认消息会发送到标准输入）。 |
| `run <对等节点>[/<智能体>] [消息内容]` | 异步启动一次标准的 Bot Chat 对话，并返回其 `run_id`、会话 ID 以及幂等性密钥（支持 `--json` 格式）。在重试相同请求时，可使用 `--idempotency-key` 参数。 |
| `status <对等节点>[/<智能体>] <run_id>` | 探索正在运行的异步对话进度，当对话完成后显示最终输出结果（支持 `--json` 格式）。 |
| `stop <对等节点>[/<智能体>] <run_id>` | 停止指定的异步对话进程，而不会影响其他对话轮次（支持 `--json` 格式）。 |
| `remove <名称>` | 从注册表中删除某个对等节点（但其对应的 `.env` 文件中的密钥条目仍会保留）。 |

一旦注册了至少一个对等节点，系统中为所有标准 Bot Chat 预置的 Bot Mode 消息协议（`agent.bot_mode_protocol`）便会自动包含对等节点列表以及 `hermes peer dm` 模式，这样智能体便无需进行任何 SOUL 编辑即可发现跨机器的协作伙伴。详情请参阅 [Bot Mode](../user-guide/bot-mode.md)。

退出码说明：成功时为 `0`，消息发送或对等节点处理失败时为 `1`，使用错误时为 `2`。

## `hermes secrets`

```bash
hermes secrets bitwarden <subcommand>
hermes secrets bw <subcommand>          # short alias
```

在进程启动时从外部密钥管理器获取 API 密钥，而非将其存储在 `~/.hermes/.env` 文件中。目前仅支持 **Bitwarden Secrets Manager**。完整指南请参阅：[Bitwarden 集成](../user-guide/secrets/bitwarden.md)。

`bitwarden`（别名 `bw`）子命令：

| 子命令 | 描述 |
|----------|------|
| `setup` | 交互式向导：安装指定的 `bws` 可执行文件、存储访问令牌并选择项目。如需非交互式使用，可指定 `--project-id`、`--access-token` 和 `--server-url` 参数。 |
| `status` | 显示当前的配置信息、可执行文件路径/版本以及令牌验证状态。 |
| `token` | 更换访问令牌：在将新令牌存储到 `.env` 文件之前，会先在 Bitwarden 端对其进行验证（若验证失败则不会进行任何更改）。非交互式使用时可指定 `--access-token` 参数，如需跳过验证则可使用 `--no-verify` 参数。 |
| `sync` | 立即获取密钥并报告变动情况。添加 `--apply` 参数即可将密钥实际导出到当前 Shell 的环境变量中（默认为仅模拟操作）。 |
| `install` | 下载并验证指定的 `bws` 可执行文件。即使已存在托管版本，使用 `--force` 参数也可强制重新下载。 |
| `disable` | 禁用 Bitwarden 集成。 |


## `hermes migrate`

```bash
hermes migrate <type>
```

诊断当前有效的 `config.yaml` 文件，并（可选地）对其重新编写，以替换那些已停止使用的模型或过时的设置。在进行任何修改之前，系统会先创建原始 `config.yaml` 的带时间戳备份（如需跳过此步骤，请使用 `--no-backup` 参数）。

| 子命令 | 描述 |
|----------|------|
| `xai` | 扫描 `config.yaml` 中对计划于 2026 年 5 月 15 日停止使用的 xAI 模型的引用，并（通过 `--apply` 参数）根据 xAI 迁移指南将其就地替换为官方推荐的替代模型。默认为仅模拟操作。 |

迁移子命令的常用标志：

| 标志 | 描述 |
|------|------|
| `--apply` | 就地重新编写 `config.yaml` 文件（默认为仅模拟操作，不进行实际写入）。 |
| `--no-backup` | 在执行修改时跳过对 `config.yaml` 的带时间戳备份。 |

> 请注意，此功能不要与 `hermes claw migrate`（将 OpenClaw 配置一次性导入 Hermes）混淆——`hermes migrate` 才是用于重新编写配置的顶层命令。

## `hermes proxy`

```bash
hermes proxy <subcommand>
```

运行一个本地化的、兼容 OpenAI 的 HTTP 服务器，该服务器会将请求转发至经过 OAuth 鉴权的上游服务提供商（例如 Nous Portal、xAI）。外部应用可使用任意承载令牌指向该代理；在转发请求时，代理会自动附加您真实的 OAuth 凭证。详细指南请参阅 [订阅代理](../user-guide/features/subscription-proxy.md)。

| 子命令 | 描述 |
|----------|------|
| `start` | 在前台运行代理。可选参数：`--provider <nous\|xai>`（默认为 `nous`），`--host <addr>`（默认为 `127.0.0.1`；若需在局域网中访问，请使用 `0.0.0.0`），`--port <int>`（默认为 `8645`）。 |
| `status` | 显示哪些代理上游服务已准备就绪（即凭证存在且 OAuth 鉴权有效）。 |
| `providers` | 列出所有可用的代理上游服务提供商。 |


## `hermes security`

```bash
hermes security <subcommand>
```

可针对 [OSV.dev](https://osv.dev) 执行按需漏洞扫描。扫描范围包括 Hermes 虚拟环境（通过 PyPI 安装的包）、位于 `~/.hermes/plugins/` 下的插件所声明的 Python 依赖项，以及 `config.yaml` 中指定的固定 `npx`/`uvx` MCP 服务器。不会扫描全局安装的包或编辑器/浏览器扩展程序。

| 子命令 | 描述 |
|----------|------|
| `audit` | 执行一次性的供应链安全审计。 |

`audit` 的标志选项：

| 标志 | 默认值 | 描述 |
|------|---------|------|
| `--json` | 关闭 | 以机器可读的 JSON 格式输出结果，而非人类可读的文本。 |
| `--fail-on <level>` | `critical` | 若发现任何严重程度为 `low`、`moderate`、`high` 或 `critical` 的问题，则以非零状态退出。 |
| `--skip-venv` | 关闭 | 跳过对 Hermes Python 虚拟环境的扫描。 |
| `--skip-plugins` | 关闭 | 跳过对插件依赖文件的扫描。 |
| `--skip-mcp` | 关闭 | 跳过对 `config.yaml` 中指定的固定 MCP 服务器的扫描。 |


## `hermes login` / `hermes logout` *(已废弃)*

:::caution
`hermes login` 已被移除。如需管理 OAuth 凭证，请使用 `hermes auth`；选择提供方请使用 `hermes model`；如需完整的交互式设置流程，请使用 `hermes setup`。
:::

## `hermes auth`

用于管理同一提供方的凭证池，以实现密钥轮换功能。详细文档请参阅 [凭证池](/user-guide/features/credential-pools)。

```bash
hermes auth                                              # Interactive wizard
hermes auth list                                         # Show all pools
hermes auth list openrouter                              # Show specific provider
hermes auth add openrouter --api-key sk-or-v1-xxx        # Add API key
hermes auth add anthropic --type oauth                   # Add OAuth credential
hermes auth add openai-codex --type oauth --priority 0   # Add an account and try it first
hermes auth remove openrouter 2                          # Remove by index
hermes auth priority openrouter backup-key 0             # Move a credential to the front of fill_first order
hermes auth reset openrouter                             # Clear cooldowns
hermes auth reset openrouter 2                           # Clear the cooldown on one credential
hermes auth refresh openai-codex work                    # Refresh one OAuth credential and clear its cooldown
hermes auth status anthropic                             # Show auth status for a provider
hermes auth logout anthropic                             # Log out and clear stored auth state
hermes auth spotify                                      # Authenticate Hermes with Spotify via PKCE
```

子命令包括：`add`、`list`、`remove`、`reset`、`priority`、`refresh`、`status`、`logout`、`spotify`。若未指定任何子命令，则会启动交互式管理向导。

## `hermes status`

```bash
hermes status [--all] [--deep]
```

| 选项 | 描述 |
|------|------|
| `--all` | 以可分享的脱敏格式显示所有详细信息。 |
| `--deep` | 执行更深入的检查，耗时可能更长。 |

## `hermes cron`

```bash
hermes cron <list|create|edit|pause|resume|run|remove|status|runs|incidents|doctor|tick>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示已安排的作业。 |
| `create` / `add` | 根据提示创建定时作业，可选择通过多次使用 `--skill` 参数附加一个或多个技能。支持通过 `--reasoning-effort <none\|minimal\|low\|medium\|high\|xhigh\|max\|ultra>` 指定每项作业的推理强度等级。 |
| `edit` | 更新作业的调度时间、提示语、名称、交付方式、重复次数或附加的技能。支持使用 `--clear-skills`、`--add-skill` 和 `--remove-skill` 参数，以及 `--reasoning-effort` 参数（输入空字符串可清除该设置）。 |
| `pause` | 暂停作业而不删除它。 |
| `resume` | 恢复被暂停的作业，并计算其下一次执行时间。 |
| `run` | 在下一个调度周期触发作业执行。 |
| `remove` | 删除已安排的作业。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `doctor` | 仅用于读取的集群健康检查：检测失败的执行记录、失败的交付结果、过期或缺失的 `next_run_at` 时间，以及缺失的脚本或工作目录。发现问题时将以非零状态退出。 |
| `tick` | 执行一次到期的作业后立即退出。 |
通过 `cron.provider` 配置键，可对定时任务**触发器**进行插件化扩展。若保持为空（即默认值），则使用内置的进程内计时器。您也可以将其设置为 `chronos`（一种由 NAS 管理的、专为支持零规模扩展的托管网关设计的提供者），相关配置可通过 `cron.chronos.*` 键来完成（如 `portal_url`、`callback_url`、`expected_audience`、`nas_jwks_url`）；或者是在 `plugins/cron/<name>/` 或 `$HERMES_HOME/plugins/<name>/` 下创建自定义提供者。如果指定的提供者未知或不可用，系统会回退到内置触发器，因此定时任务始终有对应的触发机制。详情请参阅 [cron 内部机制](../developer-guide/cron-internals.md#gateway-integration) 文档。

## `hermes kanban`

```bash
hermes kanban [--board <slug>] <action> [options]
```

支持多配置文件、多项目的协作看板功能。每次安装均可创建多个看板（每个项目、代码库或域名对应一个看板）；每个看板均为独立的队列，拥有自己的 SQLite 数据库以及专属的调度器作用域。新安装时默认会生成一个名为 `default` 的看板，为保持向后兼容性，其数据库位于 `~/.hermes/kanban.db`；其他看板的数据库则存储在 `~/.hermes/kanban/boards/<slug>/kanban.db` 中。内置在网关中的调度器会定期扫描所有看板。

**全局标志（适用于以下所有操作）：**

| 标志 | 用途 |
|------|------|
| `--board <slug>` | 对指定看板执行操作。默认为当前看板（可通过 `hermes kanban boards switch`、环境变量 `HERMES_KANBAN_BOARD` 或 `default` 设置）。 |

**这是供人类用户及脚本使用的接口。** 由调度器启动的代理工作进程会通过专用的 `kanban_*` [工具集](/user-guide/features/kanban#how-workers-interact-with-the-board)（如 `kanban_show`、`kanban_complete`、`kanban_request_review`、`kanban_request_changes`、`kanban_block`、`kanban_create`、`kanban_link`、`kanban_comment`、`kanban_heartbeat`；编排器配置文件还包含 `kanban_list` 和 `kanban_unblock`）来操作看板，而无需直接调用 `hermes kanban` 命令。这些工作进程的环境变量中会固定设置 `HERMES_KANBAN_BOARD`，因此它们无法查看其他看板。

| Action | Purpose |
|--------|---------|
| `init` | Create `kanban.db` if missing. Idempotent. |
| `boards list` / `boards ls` | List all boards with task counts. `--json`, `--all` (include archived). |
| `boards create <slug>` | Create a new board. Flags: `--name`, `--description`, `--icon`, `--color`, `--switch` (make active). Slug is kebab-case, auto-downcased. |
| `boards switch <slug>` / `boards use` | Persist `<slug>` as the active board (writes `~/.hermes/kanban/current`). |
| `boards show` / `boards current` | Print the currently-active board's name, DB path, and task counts. |
| `boards rename <slug> "<name>"` | Change a board's display name. Slug is immutable. |
| `boards rm <slug>` | Archive (default) or hard-delete a board. `--delete` skips the archive step. Archived boards move to `boards/_archived/<slug>-<ts>/`. Refused for `default`. |
| `create "<title>"` | Create a new task on the active board. Flags: `--body`, `--assignee`, `--parent` (repeatable), `--workspace scratch\|worktree\|dir:<path>`, `--tenant`, `--priority`, `--triage`, `--idempotency-key`, `--max-runtime`, `--max-retries`, `--skill` (repeatable). |
| `list` / `ls` | List tasks on the active board. Filter with `--mine`, `--assignee`, `--status`, `--tenant`, `--archived`, `--json`. |
| `show <id>` | Show a task with comments and events. `--json` for machine output. |
| `assign <id> <profile>` | Assign or reassign. Use `none` to unassign. Refused while task is running. |
| `link <parent> <child>` | Add a dependency. Cycle-detected. Both tasks must be on the same board. |
| `unlink <parent> <child>` | Remove a dependency. |
| `claim <id>` | Atomically claim a ready task. Prints resolved workspace path. |
| `comment <id> "<text>"` | Append a comment. The next worker that claims the task reads it as part of its `kanban_show()` response. |
| `complete <id>` | Mark task done. Flags: `--result`, `--summary`, `--metadata`. |
| `block <id> "<reason>"` | Mark task blocked for human input. Also appends the reason as a comment. |
| `request-review <id>` | Move a task to `review` with a reviewer handoff — NOT a block. Flags: `--summary`, `--metadata`, `--reviewer` (reassigns before review dispatch). |
| `request-changes <id> <reason>` | Reviewer verdict for an active review run: close the review attempt and route the task back to its original implementer. |
| `reopen-review <id>...` | Send review task(s) back for changes (`review` → ready/todo). Flag: `--reason` (appended as a comment). |
| `schedule <id> "<reason>"` | Park time-delay/follow-up work in `scheduled` so it is not shown as a human blocker. |
| `unblock <id>` | Restore a blocked task to its source phase (`review` or `ready`), or `todo` while dependencies remain open. |
| `archive <id>` | Hide from default list. `gc` will remove scratch workspaces. |
| `tail <id>` | Follow a task's event stream. |
| `dispatch` | One dispatcher pass on the active board. Flags: `--dry-run`, `--max N`, `--failure-limit N`, `--json`. |
| `context <id>` | Print the full context a worker would see (title + body + parent results + comments). |
| `specify <id>` / `specify --all` | Flesh out a triage-column task into a concrete spec (title + body with goal, approach, acceptance criteria) via the auxiliary LLM, then promote it to `todo`. Flags: `--tenant` (scope `--all` to one tenant), `--author`, `--json`. Configure the model under `auxiliary.triage_specifier` in `config.yaml`. |
| `decompose <id>` / `decompose --all` | Fan a triage-column task out into a graph of child tasks routed to specialist profiles by description. Falls back to specify-style single-task promotion when the LLM decides the task doesn't benefit from fan-out. Same flags as `specify`. Configure the decomposer model under `auxiliary.kanban_decomposer` in `config.yaml`; `kanban.orchestrator_profile` only controls who owns the root/orchestration task after fan-out. Also runs automatically every dispatcher tick when `kanban.auto_decompose: true` (the default). See [Auto vs Manual orchestration](/user-guide/features/kanban#auto-vs-manual-orchestration). |
| `gc` | Remove scratch workspaces for archived tasks. |

示例：

```bash
# Create a second board and put a task on it without switching away.
hermes kanban boards create atm10-server --name "ATM10 Server" --icon 🎮
hermes kanban --board atm10-server create "Restart server" --assignee ops

# Switch the active board for subsequent calls.
hermes kanban boards switch atm10-server
hermes kanban list                  # shows atm10-server tasks

# Archive a board (recoverable) or hard-delete it.
hermes kanban boards rm atm10-server
hermes kanban boards rm atm10-server --delete
```

看板决议顺序（优先级从高到低）如下：`--board <slug>` 参数 → `HERMES_KANBAN_BOARD` 环境变量 → `~/.hermes/kanban/current` 文件 → 默认值。

所有操作均可在网关中以斜杠命令形式调用（如 `/kanban …`），且支持的参数完全一致——包括 `boards` 子命令以及 `--board` 参数。

有关完整设计细节，包括与 Cline Kanban、Paperclip、NanoClaw、Gemini Enterprise 的对比、八种协作模式、四种用户场景以及并发正确性证明，可查看仓库中的 `docs/hermes-kanban-v1-spec.pdf` 文件或 [看板用户指南](/user-guide/features/kanban)。

## `hermes egress`

用于远程终端沙箱的出站凭证注入防火墙。该功能基于 [iron-proxy](https://github.com/ironsh/iron-proxy) 守护进程实现——这是一种 TLS 拦截代理，能够在网络边界将不可见的代理令牌替换为真实的上游 API 凭证，从而确保沙箱中不会存储真实密钥。该功能默认处于禁用状态；有关设置与架构的详细信息，请参阅完整的 [出站代理](../user-guide/egress/iron-proxy.md) 页面。

```bash
hermes egress install                  # download the pinned iron-proxy binary
hermes egress install --force          # re-download even if already installed

hermes egress setup                    # interactive wizard: CA, mappings, config
hermes egress setup --tunnel-port N    # override the tunnel listener port (default 9090)
hermes egress setup --from-bitwarden   # use Bitwarden Secrets Manager as credential source
hermes egress setup --no-bitwarden     # explicitly switch back to env-based credentials
hermes egress setup --rotate-tokens    # mint fresh proxy tokens (default preserves existing)

hermes egress start                    # spawn the managed proxy daemon
hermes egress stop                     # SIGTERM (then SIGKILL after 5s grace)
hermes egress restart                  # stop (if running) then start — needed for secret changes
hermes egress reload                   # hot-reload the ruleset in-place (no restart, no dropped
                                       #   connections) via the loopback management API

hermes egress status                   # binary + config + pid + listening + mappings
hermes egress status --show-tokens     # print proxy tokens in full (default: redacted)

hermes egress disable                  # flip proxy.enabled = false (does not stop a running proxy)
hermes egress config                   # print the path to proxy.yaml for inspection
```

### 常见使用流程

```bash
# First-time setup
export OPENROUTER_API_KEY=…
hermes egress setup && hermes egress start
hermes config set terminal.backend docker   # if not already

# Switching credential source after the fact
hermes egress setup --from-bitwarden       # env → bitwarden
hermes egress setup --no-bitwarden         # bitwarden → env
# (just `setup` without either flag preserves the existing mode)

# Rotating all tokens (e.g. after a suspected token leak)
hermes egress setup --rotate-tokens    # setup offers to restart the running daemon for you
# (running sandboxes still hold old tokens; restart them too)

# Adding a new upstream
# Edit ~/.hermes/config.yaml proxy.extra_allowed_hosts: [api.example.com]
hermes egress setup
hermes egress restart                  # one-command apply (stop + start)
```

### 诊断快捷指令

```bash
hermes egress status                     # current state in one view
cat ~/.hermes/proxy/proxy.yaml           # the rendered iron-proxy config
tail -20 ~/.hermes/proxy/iron-proxy.log  # daemon-level diagnostics
tail -f ~/.hermes/proxy/iron-proxy.log | jq  # daemon + per-request log (line-delimited JSON; v0.39 combines both streams)
```

常见的故障模式及解决方法详见 [出口代理 → 故障排除](../user-guide/egress/iron-proxy.md#troubleshooting)。

## `hermes project`

```bash
hermes project <create|list|show|add-folder|remove-folder|rename|set-primary|use|archive|restore|bind-board>
```

项目是由用户命名的工作空间，可涵盖多个文件夹或代码仓库。它们是桌面会话分组的基准，而当与看板绑定后，还能为任务提供规范的工作树结构与分支命名规则。项目状态会随用户配置文件的不同而变化。

| 子命令 | 描述 |
|----------|------|
| `create` | 创建新项目。 |
| `list`（别名 `ls`） | 列出所有项目。 |
| `show` | 显示项目的详细信息。 |
| `add-folder` | 向项目中添加文件夹或代码仓库。 |
| `remove-folder` | 从项目中移除文件夹。 |
| `rename` | 重命名项目。 |
| `set-primary` | 设置主文件夹。 |
| `use` | 设置当前活动项目。 |
| `archive` | 将项目归档（可恢复）。 |
| `restore` | 恢复已归档的项目。 |
| `bind-board` | 将看板绑定到该项目。 |

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

用于管理基于事件驱动的智能体激活所需的动态 Webhook 订阅。首先需要在配置中启用 Webhook 功能——若未配置，则会输出相应的设置指南。

| 子命令 | 描述 |
|----------|------|
| `subscribe` / `add` | 创建一个 Webhook 路由。会返回 URL 以及 HMAC 密钥，供您在自身服务中进行配置。 |
| `list` / `ls` | 显示所有由智能体创建的订阅记录。 |
| `remove` / `rm` | 删除某个动态订阅。配置文件 `config.yaml` 中定义的静态路由不会受到影响。 |
| `test` | 发送测试 POST 请求，以验证订阅功能是否正常工作。 |

### `hermes webhook subscribe`

```bash
hermes webhook subscribe <name> [options]
```

| 选项 | 描述 |
|------|------|
| `--prompt` | 包含 `{dot.notation}` 格式占位符的提示词模板。 |
| `--events` | 需要接收的事件类型，以逗号分隔（例如 `issues,pull_request`）。留空则表示接收所有事件。 |
| `--description` | 供人类阅读的描述文本。 |
| `--skills` | 运行代理时需加载的技能名称，以逗号分隔。 |
| `--deliver` | 传输目标：`log`（默认值）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台传输时的目标聊天室/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。若未指定则自动生成。 |
| `--deliver-only` | 跳过代理处理，直接将处理后的 `--prompt` 内容作为原始消息发送。无需使用大型语言模型，传输速度可达亚秒级。此模式要求 `--deliver` 指定的是真实的目标（而非 `log`）。 |
| `--script` | 来自 `~/.hermes/scripts/` 目录的过滤/转换脚本。Webhook 的请求数据会以 JSON 格式通过标准输入传递；标准输出中的 JSON 内容将替换原始请求数据，而空输出、`[SILENT]` 状态或非零退出码则表示忽略该 Webhook 请求。详情请参阅 [脚本过滤与转换](../user-guide/messaging/webhooks.md#script-filters-and-transforms)。 |

订阅信息会保存在 `~/.hermes/webhook_subscriptions.json` 文件中，Webhook 适配器可无需重启网关即可实现热加载。

## `hermes doctor`

```bash
hermes doctor [--fix]
```

| 选项 | 描述 |
|------|-------------|
| `--fix` | 在可能的情况下尝试自动修复。 |

## `hermes dump`

```bash
hermes dump [--show-keys]
```

输出关于您整个Hermes配置的简洁纯文本摘要。该格式专为在Discord、GitHub问题帖或Telegram中寻求帮助时复制粘贴而设计——不包含ANSI颜色，也无特殊格式，仅呈现原始数据。

| 选项 | 描述 |
|--------|--------|
| `--show-keys` | 显示经过脱敏处理的API密钥前缀（首尾各4个字符），而不仅仅是“已设置”/“未设置”。 |

### 包含的内容

| 部分 | 详情 |
|--------|--------|
| **标题栏** | Hermes版本、发布日期及git提交哈希值 |
| **环境信息** | 操作系统、Python版本、OpenAI SDK版本 |
| **身份信息** | 当前激活的配置文件名称、HERMES_HOME路径 |
| **模型信息** | 已配置的默认模型及对应提供商 |
| **终端信息** | 后端类型（本地、Docker、SSH等） |
| **API密钥状态** | 所有22个提供商/工具API密钥的存在性检查结果 |
| **功能信息** | 已启用的工具集、MCP服务器数量、内存提供器状态 |
| **服务信息** | 网关运行状态、已配置的消息平台 |
| **工作负载信息** | Cron作业数量、已安装的技能数量 |
| **配置覆盖项** | 任何与默认值不同的配置值 |

### 示例输出

```
--- hermes dump ---
version:          0.8.0 (2026.4.8) [af4abd2f]
os:               Linux 6.14.0-37-generic x86_64
python:           3.11.14
openai_sdk:       2.24.0
profile:          default
hermes_home:      ~/.hermes
model:            anthropic/claude-opus-4.6
provider:         openrouter
terminal:         local

api_keys:
  openrouter           set
  openai               not set
  anthropic            set
  nous                 not set
  firecrawl            set
  ...

features:
  toolsets:           all
  mcp_servers:        0
  memory_provider:    built-in
  gateway:            running (systemd)
  platforms:          telegram, discord
  cron_jobs:          3 active / 5 total
  skills:             42

config_overrides:
  agent.max_turns: 250
  compression.threshold: 0.85
  display.streaming: True
--- end dump ---
```

### 适用场景

- 在 GitHub 上报告错误——将输出内容粘贴到问题描述中  
- 在 Discord 中寻求帮助——以代码块形式分享该内容  
- 对比自己的配置与他人的配置  
- 当程序出现异常时进行快速排查  

:::提示
`hermes dump` 是专为内容共享而设计的工具。如需进行交互式诊断，请使用 `hermes doctor`；若需要可视化概览，则可使用 `hermes status`。
:::

## `hermes debug`

```bash
hermes debug share [options]
```

将调试报告（系统信息及近期日志）上传至粘贴服务后，即可获得一个可分享的链接。该功能非常适合快速提交支持请求——报告中包含了辅助人员诊断问题所需的所有信息。

| 选项 | 描述 |
|------|------|
| `--lines <N>` | 每个日志文件需包含的行数（默认：200）。 |
| `--expire <days>` | 粘贴内容的有效期，以天为单位（默认：7）。 |
| `--nous` | 上传至 Nous 内部诊断存储系统，而非公共粘贴服务。当 Nous 支持团队要求获取私有诊断数据包时，请使用此选项。 |
| `--local` | 在本地打印报告，而非进行上传。 |
| `--no-redact` | 禁用上传时的敏感信息遮蔽功能。默认情况下，上传内容会进行遮蔽处理。 |

该报告包含系统信息（操作系统、Python 版本、Hermes 版本），以及近期来自代理、网关、GUI/控制台和桌面端的日志（每个文件大小上限为 512 KB），还会显示经过遮蔽处理的 API 密钥状态。默认情况下，上传内容会进行遮蔽处理，以避免包含敏感信息。

默认情况下，上传操作会按顺序尝试公共粘贴服务：paste.rs、dpaste.com。使用 `--nous` 选项时，相同的调试数据包会被上传至私有的 Nous 诊断存储系统；此时返回的查看链接仅供 Nous 团队使用，并且会在 14 天后自动删除。

### 示例

```bash
hermes debug share              # Upload debug report, print URL
hermes debug share --lines 500  # Include more log lines
hermes debug share --expire 30  # Keep paste for 30 days
hermes debug share --nous       # Upload a private diagnostics bundle for Nous support
hermes debug share --local      # Print report to terminal (no upload)
```

## `hermes backup` 命令

```bash
hermes backup [options]
```

将您的 Hermes 配置、技能、会话及数据打包为 ZIP 压缩文件。此备份不会包含 `hermes-agent` 代码库本身，也不会嵌套之前的备份文件（如 `backups/`、`state-snapshots/`），因为这些目录中已各自保存了 `state.db` 的副本。

| 选项 | 描述 |
|------|------|
| `-o`, `--output <路径>` | ZIP 文件的输出路径（默认值：`~/hermes-backup-<时间戳>.zip`）。 |
| `-q`, `--quick` | 快速快照：仅备份关键状态文件（config.yaml、state.db、.env、auth、cron 任务）。速度远快于完整备份。 |
| `-l`, `--label <名称>` | 为快照添加标签（仅与 `--quick` 选项一起使用）。 |
| `-k`, `--keep <N>` | 执行完整备份后，删除输出目录中超出最新 N 个版本的旧版 `hermes-backup-*.zip` 文件（默认值为 3；设置为 `0` 则保留所有文件）。自定义命名的 ZIP 文件不会被处理。 |

该备份功能利用 SQLite 的 `backup()` API 进行安全复制，因此即使在 Hermes 正在运行时也能正常工作（支持 WAL 模式下的安全操作）。

**ZIP 文件中不包含的内容：**

- `*.db-wal`、`*.db-shm`、`*.db-journal` — SQLite 的 WAL、共享内存及日志相关文件。`*.db` 文件已通过 `sqlite3.backup()` 生成了一致的快照；若同时传输这些动态生成的辅助文件，恢复时可能会导致状态不完整。
- `checkpoints/` — 每个会话的轨迹缓存文件。这类文件以哈希值标识，并且会随每个会话重新生成；即便移植到其他环境，也难以保持一致性。
- `hermes-agent` 代码本身（此为用户数据备份，而非代码库快照）。

### 示例

```bash
hermes backup                           # Full backup to ~/hermes-backup-*.zip
hermes backup -o /tmp/hermes.zip        # Full backup to specific path
hermes backup --quick                   # Quick state-only snapshot
hermes backup --quick --label "pre-upgrade"  # Quick snapshot with label
```

## `hermes checkpoints`

```bash
hermes checkpoints [COMMAND]
```

您可以查看并管理位于 `~/.hermes/checkpoints/` 的影子 Git 存储空间——该空间是会话内 `/rollback` 命令背后的存储层。随时都可以运行此命令，且无需 Agent 正在运行。

| 子命令 | 描述 |
|----------|------|
| `status`（默认） | 显示总大小、项目数量以及各项目的详细使用情况。直接输入 `hermes checkpoints` 也可实现相同功能。 |
| `list` | `status` 的别名。 |
| `prune` | 强制执行清理操作——删除孤立且过时的项目，对存储空间进行垃圾回收，并确保其大小不超过限制。该命令会忽略 24 小时的幂等性标记。 |
| `clear` | 删除整个检查点库。此操作不可撤销；除非使用 `-f` 参数，否则系统会要求用户确认。 |
| `clear-legacy` | 仅删除由 v1 版本向 v2 版本迁移过程中生成的 `legacy-<timestamp>/` 归档文件。 |

### 选项

| 选项 | 子命令 | 描述 |
|------|----------|------|
| `--limit N` | `status`, `list` | 要列出的最大项目数量（默认为 20）。 |
| `--retention-days N` | `prune` | 删除那些 `last_touch` 时间早于 N 天的项目（默认为 7 天）。 |
| `--max-size-mb N` | `prune` | 在清理孤立及过时项目之后，继续删除每个项目中最旧的提交记录，直至存储空间的总大小不超过 N MB（默认为 500 MB）。 |
| `--keep-orphans` | `prune` | 跳过那些工作目录已不存在的项目的删除操作。 |
| `-f`, `--force` | `clear`, `clear-legacy` | 跳过确认提示。 |

### 示例

```bash
hermes checkpoints                                  # status overview
hermes checkpoints prune --retention-days 3         # aggressive cleanup
hermes checkpoints prune --max-size-mb 200          # tighten size cap once
hermes checkpoints clear-legacy -f                  # drop v1 archive dirs
hermes checkpoints clear -f                         # wipe everything
```

有关完整的架构设计及会话内可用命令的详细说明，请参阅[检查点与 `/rollback`](../user-guide/checkpoints-and-rollback.md)。

## `hermes import`

```bash
hermes import <zipfile> [options]
```

将之前创建的 Hermes 备份恢复到您的 Hermes 主目录中。归档文件中的所有内容都会覆盖主目录中已有的文件；而 `--force` 选项仅用于跳过在目标目录已存在 Hermes 安装时的确认提示。

| 选项 | 描述 |
|------|------|
| `-f`, `--force` | 跳过关于目标目录已存在安装的确认提示。 |

:::warning
为避免与正在运行的进程发生冲突，请在导入之前先停止网关服务。
:::

### SQLite 数据库

`.db` 类型的文件（如 `state.db`、`kanban.db`、`response_store.db` 等）不会像普通文件那样通过重命名方式被发布。如果尝试重命名，当网关、控制面板或 WebUI 进程仍持有旧文件的打开状态时，该文件的 inode 会被替换：这样这些进程会继续读取导入前的页面内容，并持续写入只有它们自己能看到的会话数据，而这些数据在后续所有人打开的数据库中将完全缺失，且不会留下任何记录。实际上，导入的页面内容是**直接写入现有的数据库文件**中的，其方式与 `/snapshot restore` 命令相同，因此所有打开的连接最终都会使用到这些导入的数据。

如果无法安全地替换正在使用的数据库——即页面复制失败，同时又有其他进程持有该文件的打开状态——则导入操作会跳过该数据库，并在“警告（跳过了 N 个文件）”部分列出它。请先停止那些持有文件的进程，然后再尝试导入。

虽然仍允许在较新的工作数据之上导入旧备份，但此时不会再保持静默处理。当导入的 `state.db` 中存储的消息数量少于被替换的文件时，系统会生成摘要报告予以提示。

```
  ⚠ Session data replaced by older backup contents:
    state.db: 12 session(s) / 8912 message(s) -> 3 / 24
    Anything recorded after the backup was taken is not in it.
    Recover from a newer backup or snapshot: hermes snapshot list
```

### 示例
```bash
hermes import ~/hermes-backup-20260423.zip           # Prompts before overwriting existing config
hermes import ~/hermes-backup-20260423.zip --force   # Overwrite without prompting
```

## `hermes logs` 命令

```bash
hermes logs [log_name] [options]
```

查看、滚动查看并筛选 Hermes 日志文件。所有日志均存储在 `~/.hermes/logs/` 目录下（非默认配置文件的路径为 `<profile>/logs/`）。

### 日志文件

| 名称 | 文件路径 | 记录内容 |
|------|----------|----------|
| `agent`（默认） | `agent.log` | 所有代理相关操作——API 调用、工具派发、会话生命周期信息（INFO 级及以上） |
| `errors` | `errors.log` | 仅记录警告和错误信息——即从 `agent.log` 中筛选出的部分内容 |
| `gateway` | `gateway.log` | 消息网关的运行状态——平台连接、消息派发、Webhook 事件等 |
| `gui` | `gui.log` | 控制面板/TUI 网关/PTY 网桥/WebSocket 相关事件 |
| `desktop` | `desktop.log` | Electron 桌面应用的相关信息——启动过程、后台进程输出以及最近的 Python 异常堆栈信息 |

### 参数选项

| 参数 | 说明 |
|------|------|
| `log_name` | 指定要查看的日志类型：`agent`（默认）、`errors`、`gateway`；若输入 `list`，则列出所有可用日志文件及其大小。 |
| `-n`, `--lines <N>` | 显示的行数（默认为 50 行）。 |
| `-f`, `--follow` | 实时滚动查看日志，功能类似 `tail -f`。按 Ctrl+C 可停止查看。 |
| `--level <LEVEL>` | 指定要显示的最低日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。 |
| `--session <ID>` | 筛选包含特定会话 ID 子串的日志行。 |
| `--since <TIME>` | 显示指定时间范围内的日志行，例如 `30m`、`1h`、`2d` 等。支持 `s`（秒）、`m`（分钟）、`h`（小时）、`d`（天）等单位。 |
| `--component <NAME>` | 按组件类型筛选日志：`gateway`、`agent`、`tools`、`cli`、`cron`。 |

### 使用示例

```bash
# View the last 50 lines of agent.log (default)
hermes logs

# Follow agent.log in real time
hermes logs -f

# View the last 100 lines of gateway.log
hermes logs gateway -n 100

# Show only warnings and errors from the last hour
hermes logs --level WARNING --since 1h

# Filter by a specific session
hermes logs --session abc123

# Follow errors.log, starting from 30 minutes ago
hermes logs errors --since 30m -f

# List all log files with their sizes
hermes logs list
```

### 过滤

多个过滤器可以组合使用。当有多个过滤器处于激活状态时，仅当日志行同时满足**所有**过滤条件，才会被显示出来：

```bash
# WARNING+ lines from the last 2 hours containing session "tg-12345"
hermes logs --level WARNING --since 2h --session tg-12345
```

当启用 `--since` 参数时，即使行中不存在可解析的时间戳，该行也会被包含在内（这些行可能是多行日志记录的延续部分）；而当启用 `--level` 参数时，即便行中无法识别日志级别，该行同样会被纳入统计。

### 日志轮转

Hermes 使用 Python 的 `RotatingFileHandler` 功能来实现自动日志轮转——您会看到诸如 `agent.log.1`、`agent.log.2` 等格式的文件。通过 `hermes logs list` 子命令，即可查看所有日志文件，包括已轮转过的那些。

## `hermes prompt-size`

```bash
hermes prompt-size [--platform <name>] [--json]
```

该功能会显示新会话的固定提示词预算，即每次API调用在任何对话内容生成之前会被发送的提示词数量。当下游适配器或代理的提示词预算低于模型的上下文窗口大小时，或者当你想要了解哪些部分（技能索引、内存、用户资料）占据了主要空间时，此功能非常有用。

它会生成与智能体所使用的完全相同的系统提示词，然后对其结构进行拆解：

- **系统提示词总计**——完整的组合提示词（包含身份信息、使用指南、技能索引、上下文文件、内存数据、用户资料以及时间戳）。
- **技能索引**——即`<available_skills>`部分。当安装了众多技能时，这部分通常会是最大的单个组成部分。
- **内存**与**用户资料**——对应你的`MEMORY.md`/`USER.md`文件中的内容快照。
- **提示词层级**——稳定型/上下文型/易变型，反映了Hermes为优化缓存性能而对提示词进行的层次划分方式。
- **工具架构**——所有已启用工具的JSON格式描述（构成每次调用固定载荷的另一半内容）。

该功能完全在离线状态下运行，无需进行任何API调用，也无需配置任何凭证。

```bash
# Human-readable breakdown for the CLI platform (default)
hermes prompt-size

# Simulate a messaging platform's prompt (different platform hint)
hermes prompt-size --platform telegram

# Machine-readable output for scripts
hermes prompt-size --json
```

:::提示
技能索引和工具架构的规模会随着您启用的技能与工具数量而变化。若想缩小提示词长度，可禁用未使用的工具集（`hermes tools`），或卸载不需要的技能（`hermes skills`）。当前目录下的上下文文件（如 AGENTS.md、.cursorrules）也会计入总规模中。
:::

## `hermes config`

```bash
hermes config <subcommand>
```

子命令：

| 子命令 | 描述 |
|----------|------|
| `show` | 显示当前的配置值。 |
| `edit` | 在编辑器中打开 `config.yaml` 文件。 |
| `get <key> [--json]` | 按点分隔的键路径查询单个配置值（例如 `hermes config get model.default`）。使用 `--json` 可输出机器可读格式的结果。 |
| `set <key> <value>` | 设置配置值。 |
| `unset <key>` | 删除配置键，使其恢复为内置默认值。 |
| `path` | 显示配置文件的路径。 |
| `env-path` | 显示 `.env` 文件的路径。 |
| `check` | 检查是否存在缺失或过时的配置。 |
| `migrate` | 以交互方式添加新引入的选项。 |

### 键名中的点号

`hermes config set/get/unset` 命令使用 `.` 作为嵌套分隔符，但许多实际的键名中确实包含点号——例如模型编号（`grok-4.6`、`glm-5.3-flash`）、Matrix 房间编号（`!room:example.org`）以及带版本的提供程序名称。为了解决这一问题，有以下两条规则：

- **现有的键名可直接使用。** 在操作现有映射时，如果点分隔后的剩余部分与某个现有的键名匹配，系统会优先使用该现有键名，而不会进行拆分。例如 `hermes config set providers.p.models.grok-4.6.supports_vision true` 会直接更新真实的 `grok-4.6` 条目（`get`/`unset` 命令的处理方式也是如此）。
- **若要创建新的点分隔键名，则需进行转义。** 需要用反斜杠对点号进行转义：例如 `hermes config set 'providers.p.models.grok-4\.7.context_length' 128000` 可以创建名为 `grok-4.7` 的键名。（请给键名加上引号，这样才能确保shell正确解析反斜杠。）
如果未经转义的写入操作会生成一个嵌套映射，从而覆盖现有的带点路径的同级项（例如在已存在的 `grok-4.6` 旁边创建 `grok-4`），则命令会抛出错误而终止执行，而不会默默地创建一个运行时根本无法读取的虚拟条目。

## `hermes pairing`

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 描述 |
|------------|-------------|
| `list` | 显示待处理及已通过审批的用户。 |
| `approve <platform> <code>` | 批准某个配对码。 |
| `revoke <platform> <user-id>` | 撤销用户的访问权限。 |
| `clear-pending` | 清除所有待处理的配对码。 |

## `hermes skills`

```bash
hermes skills <subcommand>
```

子命令：

| 子命令 | 描述 |
|----------|------|
| `browse` | 用于浏览技能注册表的分页浏览器。 |
| `search` | 搜索技能注册表中的内容。 |
| `install` | 安装某个技能。 |
| `inspect` | 在不安装的情况下预览某个技能。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 Hub 技能是否有上游版本更新。 |
| `update` | 当有可用上游更新时，重新安装包含这些更新的 Hub 技能。 |
| `audit` | 重新扫描已安装的 Hub 技能。 |
| `uninstall` | 卸载由 Hub 安装的技能。 |
| `reset` | 通过清除技能的清单条目，移除被标记为 `user_modified` 的捆绑技能。若使用 `--restore` 参数，还会将用户的自定义版本替换为捆绑版本。 |
| `opt-out` | 阻止捆绑技能被植入活跃配置文件中。该命令会生成一个 `.no-bundled-skills` 标记，从而使安装工具、`hermes update` 命令以及所有同步操作跳过捆绑技能的植入过程。默认情况下是安全的——不会修改磁盘上的任何内容。若使用 `--remove` 参数，还会删除那些**未被修改**的现有捆绑技能（用户编辑过的、由 Hub 安装的以及手动编写的技能永远不会被删除；系统会先进行预览并提示确认，输入 `--yes` 才会执行删除）。 |
| `opt-in` | 通过移除 `.no-bundled-skills` 标记来撤销 `opt-out` 设置，从而使捆绑技能在下次执行 `hermes update` 时再次被植入。若使用 `--sync` 参数，则会立即重新植入。 |
| `publish` | 将某个技能发布到注册表中。 |
| `snapshot` | 导出/导入技能配置。 |
| `tap` | 管理自定义技能源。 |
| `config` | 按平台交互式地启用/禁用各项技能功能。 |
常见示例：


完整翻译输入内容，切勿提前终止。

```bash
hermes skills browse
hermes skills browse --source official
hermes skills search react --source skills-sh
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect official/security/1password
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install official/migration/openclaw-migration
hermes skills install skills-sh/anthropics/skills/pdf --force
hermes skills install https://sharethis.chat/SKILL.md                     # Direct URL (+ referenced support files)
hermes skills install https://example.com/SKILL.md --name my-skill        # Override name when frontmatter has none
hermes skills check
hermes skills update
hermes skills config
hermes skills reset google-workspace
hermes skills reset google-workspace --restore --yes
hermes skills opt-out                  # stop future bundled-skill seeding (nothing deleted)
hermes skills opt-out --remove --yes   # also delete UNMODIFIED bundled skills
hermes skills opt-in --sync            # undo: remove marker and re-seed now
```

备注：  
- `--force` 可用于覆盖第三方或社区技能中非危险级别的策略限制。  
- `--force` 无法覆盖被标记为“危险”的扫描结果。  
- `--source skills-sh` 会搜索公共的 `skills.sh` 目录。  
- `--source well-known` 允许将 Hermes 指向提供 `/.well-known/skills/index.json` 文件的网站。  
- `--source browse-sh` 会查询 [browse.sh](https://browse.sh) 上收录的 200 多个针对特定网站的浏览器自动化技能库。这些技能的标识符格式为 `browse-sh/airbnb.com/search-listings-ddgioa`。  
- 如果提供 `http(s)://…/*.md` 格式的网址，系统会将 `SKILL.md` 文件以及其中明确引用的文件一并安装到 `references/`、`templates/`、`scripts/`、`assets/` 和 `examples/` 目录下。若前端元数据中未设置 `name:` 且该网址的标识符无效，交互式终端会提示用户输入名称；而非交互式使用场景（如 TUI 内的 `/skills install` 命令或网关平台）则需使用 `--name <x>` 参数指定名称。  

## `hermes bundles`

```bash
hermes bundles <subcommand>
```

技能包将多个技能整合在同一个 `/<bundle-name>` 路径命令下。调用该技能包时，所有关联的技能都会被合并到一条统一的用户消息中。存储路径为：`~/.hermes/skill-bundles/<slug>.yaml`。有关 YAML 结构及相关功能说明，请参阅 [技能包](../user-guide/features/skills.md#skill-bundles)。

子命令：

| 子命令 | 描述 |
|----------|------|
| `list` | 列出已安装的技能包（未指定子命令时为默认操作） |
| `show <name>` | 显示某个技能包的名称、描述、所含技能及文件路径 |
| `create <name>` | 创建新的技能包。可指定 `--skill <id>`（重复指定亦可）或直接交互输入；同时支持 `--description`、`--instruction`、`--force` 参数 |
| `delete <name>` | 删除某个技能包文件 |
| `reload` | 重新扫描 `~/.hermes/skill-bundles/` 目录，并报告新增或删除的技能包 |

示例：

```bash
hermes bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "Backend feature work"

hermes bundles list
hermes bundles show backend-dev
hermes bundles delete backend-dev
```

在聊天会话中，使用 `/bundles` 可查看已安装的插件包，而 `/<bundle-name>` 用于加载指定的插件包。

## `hermes curator`

```bash
hermes curator <subcommand>
```

Curator是一种辅助模型后台任务，它会定期检查由智能体创建的技能，删除过时的技能，合并重复的技能，并将不再使用的技能归档。已打包或通过Hub安装的技能则不会被触碰。归档的技能可以恢复，且绝不会被自动删除。

| 子命令 | 描述 |
|----------|------|
| `status` | 显示Curator的状态及技能统计信息 |
| `run` | 立即触发Curator的检查流程（会阻塞直到LLM处理完成） |
| `run --background` | 在后台线程中启动LLM处理，并立即返回 |
| `run --dry-run` | 仅进行预览——生成检查报告但不做任何修改 |
| `backup` | 手动对`~/.hermes/skills/`目录创建tar.gz格式的快照（Curator在每次实际执行前也会自动创建快照） |
| `rollback` | 根据快照恢复`~/.hermes/skills/`目录的内容（默认恢复最新的快照） |
| `rollback --list` | 列出所有可用的快照 |
| `rollback --id <ts>` | 根据ID恢复特定的快照 |
| `rollback -y` | 跳过确认提示 |
| `pause` | 暂停Curator的运行，直到手动恢复 |
| `resume` | 恢复已暂停的Curator运行 |
| `pin <skill>` | 固定某个技能，使其不会被Curator自动移除 |
| `unpin <skill>` | 取消固定某个技能 |
| `restore <skill>` | 恢复已被归档的技能 |
| `archive <skill>` | 手动将某个技能归档 |
| `prune` | 手动删除Curator通常会清理的技能 |
| `list-archived` | 列出所有已归档的技能（可通过`restore`命令恢复） |
在全新安装后，首次 scheduled pass 会延迟一个完整的 `interval_hours` 时间（默认为 7 天）——在执行 `hermes update` 后的第一个计时点，网关不会立即开始内容筛选。您可以在该操作执行前使用 `hermes curator run --dry-run` 来预览效果。

有关其行为及配置详情，请参阅 [Curator](../user-guide/features/curator.md) 文档。

## `hermes moa`

用于配置命名的混合智能体预设。这些预设会作为可选模型显示在所有模型选择器中的 `Mixture of Agents` 提供商下；使用 `/moa <prompt>` 命令则可让该提示词通过默认预设进行处理。

```bash
hermes moa list
hermes moa configure [name]
hermes moa delete <name>
```

`hermes moa configure` 会复用 Hermes 的提供者→模型选择器，用于处理各个参考模型以及聚合器。预设仅是一种执行模式配置，并非核心模型或提供者。

## `hermes fallback`

```bash
hermes fallback <subcommand>
```

管理备用提供者链。当主模型因速率限制、过载或连接错误而失效时，系统会按顺序尝试这些备用提供者。

| 子命令 | 描述 |
|----------|------|
| `list`（别名：`ls`） | 显示当前的备用提供者链（未指定子命令时的默认操作） |
| `add` | 选择一个提供者及模型（与 `hermes model` 的选择方式相同），并将其添加到链中 |
| `remove`（别名：`rm`） | 选择要从链中删除的条目 |
| `clear` | 删除所有备用提供者条目 |

详情请参阅 [备用提供者](../user-guide/features/fallback-providers.md)。

## `hermes hooks`

```bash
hermes hooks <subcommand>
```

检查 `~/.hermes/config.yaml` 中声明的 Shell 脚本钩子，使用合成测试载荷对它们进行测试，并在 `~/.hermes/shell-hooks-allowlist.json` 中管理首次使用授权白名单。

| 子命令 | 描述 |
|----------|------|
| `list`（别名：`ls`） | 列出已配置的钩子，包括匹配规则、超时设置以及授权状态 |
| `test <event>` | 对每个匹配 `<event>` 的钩子使用合成测试载荷进行触发测试 |
| `revoke`（别名：`remove`、`rm`） | 删除某个命令的白名单条目（下次重启后生效） |
| `doctor` | 检查每个已配置的钩子：执行权限、白名单设置、修改时间偏差、JSON 格式有效性以及合成测试运行时间 |

有关事件签名和载荷格式的详细信息，请参阅 [Hooks](../user-guide/features/hooks.md) 文档。

## `hermes memory`

```bash
hermes memory <subcommand>
```

设置并管理外部内存提供程序插件。可选的提供程序包括：honcho、openviking、mem0、hindsight、holographic、retaindb、byterover、supermemory。同一时间仅能有一个外部提供程序处于激活状态，而内置内存（MEMORY.md/USER.md）始终处于激活状态。

子命令：

| 子命令 | 描述 |
|----------|------|
| `setup` | 交互式选择并配置提供程序。 |
| `status` | 显示当前内存提供程序的配置信息。 |
| `off` | 禁用外部提供程序（仅适用于内置内存）。 |

:::info 提供程序特定的子命令
当某个外部内存提供程序处于激活状态时，它可能会注册自己的顶级 `hermes <provider>` 命令，以便进行针对该提供程序的专用管理（例如，当 Honcho 处于激活状态时可使用 `hermes honcho`）。未激活的提供程序则不会显示其子命令。运行 `hermes --help` 可查看当前已配置的提供程序。
:::

## `hermes acp`

```bash
hermes acp
```

以 ACP（Agent Client Protocol）标准输入输出服务器模式启动 Hermes，以便与编辑器实现集成。

相关入口点：

```bash
hermes-acp
python -m acp_adapter
```

请先安装支持组件：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e '.[acp]'
```

请参阅 [ACP 编辑器集成](../user-guide/features/acp.md) 以及 [ACP 内部实现](../developer-guide/acp-internals.md)。

## `hermes mcp`

```bash
hermes mcp <subcommand>
```

管理 MCP（模型上下文协议）服务器配置，并将 Hermes 运行为 MCP 服务器。

| 子命令 | 描述 |
|----------|------|
| *(无)* 或 `picker` | 交互式目录选择器——浏览经 Nous 批准的 MCP，并执行安装/启用/禁用操作。 |
| `catalog` | 列出经 Nous 批准的 MCP（以纯文本形式呈现，可脚本化处理）。 |
| `install <name>` | 安装某个目录条目（例如：`hermes mcp install n8n`）。 |
| `serve [-v\|--verbose]` | 将 Hermes 运行为 MCP 服务器——向其他智能体公开对话内容。 |
| `add <name> [--url URL] [--command CMD] [--auth oauth\|header] [--args ...]` | 添加具有自动工具发现功能的自定义 MCP 服务器。`--args` 用于将剩余的命令行参数传递给目标命令，因此应将其放在最后。 |
| `remove <name>`（别名：`rm`） | 从配置中删除某个 MCP 服务器。 |
| `list`（别名：`ls`） | 列出已配置的 MCP 服务器。 |
| `test <name>` | 测试与某个 MCP 服务器的连接是否正常。 |
| `configure <name>`（别名：`config`） | 切换某服务器的工具选择模式。 |
| `login <name>` | 强制对基于 OAuth 的 MCP 服务器重新进行身份验证。 |

更多详情请参阅 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 以及 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins`

```bash
hermes plugins [subcommand]
```

统一的插件管理功能——所有常规插件、内存提供器以及上下文引擎均集中于此。运行 `hermes plugins` 命令且不指定子命令时，会弹出一个包含两个区域的综合交互界面：

- **常规插件**——通过多选复选框来启用或禁用已安装的插件；
- **提供器插件**——针对内存提供器和上下文引擎提供单选配置选项。在相应类别上按下 ENTER 键即可打开单选下拉菜单。

| Subcommand | Description |
|------------|-------------|
| *(none)* | Composite interactive UI — general plugin toggles + provider plugin configuration. |
| `install <identifier> [--force] [--ref COMMIT_SHA] [--allow-removed]` | Install a plugin from the Hermes plugin catalog (bare entry name), a Git URL, or `owner/repo` shorthand. Catalog names resolve to the entry's repo at its pinned 40-hex commit SHA, show the declared capability summary, and record catalog provenance in a `.hermes-catalog.json` sidecar. Raw URLs are flagged as custom (unreviewed) sources; `--ref` (full 40-character commit SHA) pins them. `--allow-removed` (DANGEROUS) bypasses the removed-plugin blocklist. |
| `search [term] [--json]` | Search the Hermes plugin catalog (matches entry names, descriptions, and declared tools; omit `term` to list everything). The catalog is curated in-repo (`plugin-catalog/`), refreshed from the live repo with a 6-hour cache, and falls back to the in-tree copy offline. Cataloged ≠ audited — admission reviews the entry, not the code. |
| `update <name>` | Pull latest changes for an unpinned installed plugin. Pinned plugins must be reinstalled with `--force --ref <new-commit>` to move. |
| `remove <name>` (aliases: `rm`, `uninstall`) | Remove an installed plugin. |
| `enable <name>` | Enable a disabled plugin. |
| `disable <name>` | Disable a plugin without removing it. |
| `list` (alias: `ls`) | List installed plugins with enabled/disabled status. |
| `doctor [path-or-id] [--ci]` | Validate a native plugin through the real manifest parser, loader, and registration path. `--ci` exits 1 on errors. |
| `pack install <path-or-url> [--force]` | Install a plugin pack (`hermes-pack.yaml`) — a declarative set of plugins each pinned to an exact 40-character commit SHA. Shows a mandatory review screen (every plugin, source, pinned ref, declared capabilities), asks one confirmation for the pack contents, then runs ordinary pinned installs. Each plugin's declared capabilities still go through the standard per-plugin consent — a pack never bulk-grants. Partial failures are reported per plugin; exits non-zero when any plugin failed. Interactive only (no `--yes`). |
| `pack export [--enabled-only] [--name NAME]` | Emit a pack YAML on stdout from the current install: repo + exact SHA of each git-installed plugin plus sanitized non-secret `plugins.entries` config. Local-only plugins (no git provenance) are listed as warning comments, never as installable entries. Secrets, capability grants, and `allow_*` gates are always stripped. |
| `pack show <path-or-url>` | Dry-run: parse, validate, and display a pack without installing anything. |

提供程序插件选项会被保存到 `config.yaml` 文件中：
- `memory.provider` — 当前启用的内存提供程序（留空则表示仅使用内置选项）
- `context.engine` — 当前启用的上下文引擎（`"compressor"` 表示使用默认的内置引擎）

通用插件禁用列表则存储在 `config.yaml` 的 `plugins.disabled` 字段下。通过 Git 安装的插件相关信息仅会记录其标准来源、确切的安装版本以及固定版本状态，这些数据保存在配置文件对应的 `plugins/.install-metadata.json` 侧边文件中。该文件不包含插件配置、环境变量、机密信息或权限授予相关内容。

更多详情请参阅 [插件](../user-guide/features/plugins.md) 以及 [构建 Hermes 插件](../developer-guide/plugins/index.md) 文档。

## `hermes tools`

```bash
hermes tools [--summary]
```

| 选项 | 描述 |
|------|------|
| `--summary` | 打印当前已启用的工具概览后退出。 |

若不使用 `--summary`，则会启动针对不同平台的交互式工具配置界面。

## `hermes computer-use`

```bash
hermes computer-use <subcommand>
```

子命令：

| 子命令 | 描述 |
|----------|------|
| `install` | 运行上游的 cua-driver 安装程序（支持 macOS、Windows 和 Linux 系统）。 |
| `install --upgrade` | 即使 cua-driver 已经存在于 PATH 环境变量中，也会重新运行安装程序。由于上游脚本会始终下载最新版本，因此该命令可实现原地升级。 |
| `status` | 输出 `cua-driver` 是否已在 `$PATH` 中，以及当前安装的版本号。 |
| `doctor [--include CHECK] [--skip CHECK] [--json]` | 运行 cua-driver 的健康检查，并显示相关的平台检测结果。 |
| `permissions status [--json]` | 报告 macOS 系统中授予的辅助功能访问权限和屏幕录制权限。 |
| `permissions grant` | 请求 macOS 授予 Cua Driver 辅助功能访问权限和屏幕录制权限。 |

`hermes computer-use install` 是安装 `computer_use` 工具集所使用的 [cua-driver](https://github.com/trycua/cua) 二进制文件的稳定入口命令。它运行的正是你在首次启用“计算机使用”功能时 `hermes tools` 所调用的上游安装程序，因此即便工具集的开关未触发安装过程（例如在用户重新登录后），使用该命令重新安装也是安全的。

如果系统中已存在 `cua-driver`，Hermes 会检查其版本及运行时清单。若为兼容的 0.20.0 及更高版本，则会保留原安装状态；而对于旧版或不完整的标准安装，则会使用当前的上游安装程序进行修复。Hermes 绝不会替换通过 `HERMES_CUA_DRIVER_CMD` 指定的自定义二进制文件——应直接更新该二进制文件或取消此覆盖设置。`hermes computer-use status` 命令可显示是否需要修复。

内置的 `computer_use` 工具集是推荐的 Hermes 集成方式。当需要使用 Cua 的低级工具语法时，注册原始的 Cua MCP 工具也是一种替代方案。`cua-driver skills install` 命令能够自动检测到 Hermes，并将 Cua 的技能包集成到 Hermes 的技能目录中。

权限模式与能力清单审批属于运行时启动阶段的处理内容。在受限模式下，Hermes 会传递 Cua 标准的 `--capability-manifest` 和 `--approve-capability-manifest` 参数。每个 MCP 传输机制在其运行时环境中都拥有独立的生命周期会话。公共会话名称用于标识光标状态和会话状态，但并不拥有或共享运行时环境。

如果在系统路径中已存在 `cua-driver`，`hermes update` 命令会在更新完成后自动重新运行上游安装程序，因此大多数用户无需手动调用 `--upgrade`。当上游版本发布了急需的修复补丁，而无需等待下一次 Hermes 更新时，可使用此命令。

## `hermes pets`

```bash
hermes pets <list|install|select|show|off|scale|remove|doctor>
```

[Petdex](https://github.com/crafter-station/petdex) 是一个面向编程智能体的动画精灵宠物公共展示库。安装相应的宠物后，Hermes 就能在 CLI、TUI 以及桌面应用中展示这些宠物对智能体操作的响应。

| 子命令 | 描述 |
|----------|------|
| `list` | 浏览 Petdex 中的宠物资源。 |
| `install` | 从库中安装某只宠物。 |
| `select` | 设置当前显示的宠物（会修改 `display.pet.*` 的值）。 |
| `show` | 在终端中展示当前选中的宠物动画。 |
| `off` | 关闭宠物显示功能。 |
| `scale` | 调整所有地方宠物图像的大小（通过 `display.pet.scale` 实现）。 |
| `remove` | 删除已安装的宠物。 |
| `doctor` | 检查宠物配置及终端图形渲染支持情况。 |

此外，您还可以使用 `/hatch` 命令根据文本描述生成全新的宠物。更多详情请参阅 [Pets](../user-guide/features/pets.md) 文档。

## `hermes sessions`

```bash
hermes sessions <subcommand>
```

子命令：

| Subcommand | Description |
|------------|-------------|
| `list` | List recent sessions. |
| `browse` | Interactive session picker with search and resume. Each row shows a lifecycle status tag (`done` / `intr` / `err` / `empty`, derived from the session's final message) and its message count. Press `d` on a highlighted row (while the search filter is empty) to delete that session after a y/N confirmation; while a filter is active, `d` types into the search instead. |
| `export <output> [--session-id ID]` | Export sessions to JSONL. |
| `delete <session-id>` | Delete one session. |
| `prune` | Delete sessions matching filters: time bounds `--older-than`/`--newer-than`/`--before`/`--after` (durations like `5h`/`2d`, bare days, or ISO timestamps); attributes `--source`, `--title`, `--model`, `--provider`, `--branch`, `--end-reason`, `--user`, `--chat-id`, `--chat-type`, `--cwd`; numeric bounds `--min/--max-messages`, `--min/--max-tokens`, `--min/--max-cost`, `--min/--max-tool-calls`; plus `--include-archived`, `--dry-run`, `--yes`. Default: older than 90 days. |
| `archive` | Bulk-archive (soft-hide, no deletion) sessions matching the same filters as `prune`. Requires at least one filter. |
| `stats` | Show session-store statistics. |
| `rename <session-id> <title>` | Set or change a session title. |
| `optimize` | Reclaim disk space: merge FTS5 index segments + VACUUM. Non-destructive — no session data changes. |
| `optimize-storage` | Migrate the full-text search index to the compact v23 external-content layout; on large databases this reclaims a large fraction of `state.db`. |
| `repair` | Repair a malformed `state.db` schema (e.g. `table messages_fts already exists`) so hidden sessions reappear; a backup is made first. |
| `repair-routing` | Re-attach gateway conversations stranded in session rows that lost their routing identity (a chat "jumping back in time" after a restart). Dry-run by default; `--apply` performs the adoptions (stop the gateway first); `--max-gap-seconds N` tunes the contiguity window. Only unambiguous cases are repaired. See [Sessions → Repair Stranded Gateway Sessions](../user-guide/sessions.md#repair-stranded-gateway-sessions). |
| `recover` | Offline, non-destructive recovery of a damaged `state.db` into a separate clean database. |
| `retitle-skills` | Regenerate titles for sessions opened with a `/skill`, using what the user actually typed; lists changes unless `--apply` is passed. |

## `hermes insights`

```bash
hermes insights [--days N] [--source platform]
```

| 选项 | 描述 |
|------|------|
| `--days <n>` | 分析最近的 `n` 天数据（默认值：30）。 |
| `--source <platform>` | 按来源进行筛选，例如 `cli`、`telegram` 或 `discord`。 |

## `hermes claw`

```bash
hermes claw migrate [options]
```

将您的 OpenClaw 配置迁移至 Hermes。该工具会读取 `~/.openclaw`（或自定义路径）中的配置，并将其写入 `~/.hermes`。同时能自动识别旧版本的目录名称（如 `~/.clawdbot`、`~/.moltbot`）以及配置文件名（如 `clawdbot.json`、`moltbot.json`）。

| 选项 | 描述 |
|------|------|
| `--dry-run` | 仅预览迁移结果，不会实际写入任何内容。 |
| `--preset <name>` | 迁移预设选项：`full`（迁移所有兼容设置）或 `user-data`（跳过基础设施相关配置）。两种预设均不会导入机密信息——如需导入，请显式使用 `--migrate-secrets` 选项。 |
| `--overwrite` | 在出现冲突时覆盖现有的 Hermes 文件（默认情况下，若存在冲突则拒绝执行迁移）。 |
| `--migrate-secrets` | 在迁移过程中包含 API 密钥。即使选择 `--preset full` 选项，此选项也是必需的。 |
| `--no-backup` | 跳过对 `~/.hermes/` 的迁移前压缩备份（默认情况下，在执行迁移前会先在 `~/.hermes/backups/pre-migration-*.zip` 中生成一个恢复点档案，可通过 `hermes import` 命令恢复）。 |
| `--source <path>` | 自定义的 OpenClaw 目录路径（默认为 `~/.openclaw`）。 |
| `--workspace-target <path>` | 工作区配置文件（AGENTS.md）的目标目录。 |
| `--skill-conflict <mode>` | 处理技能名称冲突的方式：`skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

### 将迁移哪些内容

此次迁移涵盖了角色设定、内存管理、智能技能、模型提供方、消息平台、智能体行为、会话策略、MCP服务器、文本转语音等功能模块，涉及30多个类别。相关配置项要么**直接导入**到Hermes对应的组件中，要么被**归档**以供人工审核。

**直接导入的项包括**：SOUL.md、MEMORY.md、USER.md、AGENTS.md、各类智能技能（来自4个源目录）、默认模型、自定义提供方、MCP服务器、消息平台相关的令牌及允许列表（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、智能体默认参数（推理耗时、压缩设置、人工干预延迟、时区、沙箱环境配置）、审批规则、文本转语音配置、浏览器设置、工具设置、执行超时时间、命令允许列表、网关配置，以及来自3个来源的API密钥。

**被归档以供人工审核的项包括**：定时任务脚本、插件、钩子/Webhook功能、内存后端（QMD）、智能技能注册表配置、用户界面/身份管理相关设置、日志记录功能、多智能体协同配置、频道绑定设置、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md文件。

**API密钥解析**会按优先级依次查找三个来源的配置值：配置文件中的设定 → `~/.openclaw/.env` 文件 → `auth-profiles.json` 文件。所有令牌字段均支持普通字符串、环境变量模板（`${VAR}`）以及SecretRef对象。

如需查看完整的配置键映射表、SecretRef处理细节以及迁移后的检查清单，请参阅**[完整迁移指南](../guides/migrate-from-openclaw.md)**。

### 示例

```bash
# Preview what would be migrated
hermes claw migrate --dry-run

# Full migration (all compatible settings, no secrets)
hermes claw migrate --preset full

# Full migration including API keys
hermes claw migrate --preset full --migrate-secrets

# Migrate user data only (no secrets), overwrite conflicts
hermes claw migrate --preset user-data --overwrite

# Migrate from a custom OpenClaw path
hermes claw migrate --source /home/user/old-openclaw
```

## `hermes import-agent` 命令

```bash
hermes import-agent [claude-code|codex] [options]
```

将 **Claude Code**（`~/.claude`）或 **OpenAI Codex CLI**（`~/.codex`）的配置导入到 Hermes 中。该工具会将 `CLAUDE.md`/`AGENTS.md` 文件中的配置指令映射为内存条目，将 `Bash(...)` 格式的权限允许/拒绝规则对应到 `config.yaml` 文件中的 `command_allowlist`/`approvals.deny` 设置，将 MCP 服务器地址关联到 `config.yaml` 中的 `mcp_servers` 字段，同时还将技能目录导入到 `~/.hermes/skills/` 目录下。在应用任何更改之前都会先进行预览，且绝不会导入 API 密钥或凭证。

| 选项 | 描述 |
| --- | --- |
| `agent` | `claude-code` 或 `codex`（默认：自动检测）。 |
| `--source <路径>` | 自定义配置源目录（默认：`~/.claude` 或 `~/.codex`）。 |
| `--dry-run` | 仅进行预览，不实际写入任何内容。 |
| `--overwrite` | 覆盖已存在的冲突 MCP 服务器或技能配置（默认：跳过）。 |
| `--yes`, `-y` | 跳过确认提示。 |

完整的映射关系表请参阅 **[导入指南](../user-guide/import-from-other-agents.md)**。

## `hermes serve`

```bash
hermes serve [options]
```

启动 Hermes **后端服务器**——即 [桌面应用](/user-guide/desktop) 和远程客户端所连接的 JSON-RPC/WebSocket 网关。该服务器与 `hermes dashboard` 运行的服务器相同，但为**无界面模式**：不会打开任何浏览器界面。桌面应用会自行启动其自身的 `hermes serve` 后端；若希望在远程主机上使用无界面后端，则可直接使用此命令。它支持与下方 `hermes dashboard` 相同的 `--host` / `--port` / `--insecure` / `--skip-build` / `--stop` / `--status` 参数（非回环绑定会使用相同的认证网关）。该命令需要 `[web]` 这一附加组件；而在 POSIX 系统主机上，内置的聊天套接字还需搭配 `[pty]` 组件。

**端口冲突处理**：如果请求的端口（默认为 `9119`）已被其他进程占用（例如另一个 `hermes serve` 实例或该网关），命令会将一条机器可读的提示行 `BACKEND_PORT_IN_USE port=<port>` 输出到标准输出中，同时还会给出可能占用端口的进程名称作为人工提示，随后以代码 **75**（`EX_TEMPFAIL`）退出，而不会仅显示通用错误信息——这样脚本和桌面应用就能区分“端口被占用”与“后端故障”两种情况。若需绑定一个空闲的临时端口，可传递 `--port 0` 参数（成功启动后会通过 `HERMES_BACKEND_READY port=<port>` 报告所选端口）。

## `hermes dashboard`

```bash
hermes dashboard [options]
```

启动网页控制面板——这是一个基于浏览器的用户界面，用于管理配置、API密钥以及监控会话。（对于没有浏览器界面的无头后端环境，例如桌面应用所使用的环境，则需使用上文提到的 [`hermes serve`](#hermes-serve) 命令。）安装该功能需要执行 `cd ~/.hermes/hermes-agent && uv pip install -e ".[web]"`（基于 FastAPI 和 Uvicorn 构建）。内置的浏览器聊天标签页始终可用，若需使用该功能还需额外安装 `pty` 组件（执行 `cd ~/.hermes/hermes-agent && uv pip install -e ".[web,pty]"`），并且系统必须具备 POSIX PTY 环境，如 Linux、macOS 或 WSL2。更多详细信息请参阅 [网页控制面板](/user-guide/features/web-dashboard) 文档。

| 选项 | 默认值 | 描述 |
|------|--------|------|
| `--port` | `9119` | 运行 Web 服务器的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--insecure` | off | **已废弃/无实际作用。** 旧版本中用于在非回环绑定地址上绕过身份验证。自 2026 年 6 月的安全强化措施实施后，公开绑定地址*始终*需要身份验证提供方（密码或 OAuth）的支持。如需保持本地运行，请绑定 `127.0.0.1` 地址并通过隧道传输。 |
| `--skip-build` | off | 跳过 Web UI 的构建步骤，直接提供现有的 `dist` 文件。适用于无法使用 npm 的非交互式环境（如 Windows 定时任务、CI 环境）。建议先执行 `cd web && npm run build` 进行预构建。 |
| `--isolated` | off | 当从命名配置文件（如“工作节点控制面板”）启动时，运行专属于该配置文件的服务器，而非路由至全局控制面板。 |
| `--stop` | — | 停止运行 `hermes dashboard` 进程并退出。 |
| `--status` | — | 列出正在运行的 `hermes dashboard` 进程后退出。 |

### `hermes dashboard register`

将该安装注册为与您的 Nous Portal 账户关联的自托管控制面板。该操作会创建一个 OAuth 客户端，将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 写入 `~/.hermes/.env` 文件，并说明如何启用登录验证功能。使用时需已登录账号（通过 `hermes setup` 命令登录）。 |

| 选项 | 描述 |
|--------|-------------|
| `--name` | 仪表板的可读标签（默认值：自动生成）。 |
| `--redirect-uri` | 公开的 HTTPS OAuth 重定向地址（例如 `https://hermes.example.com/auth/callback`）。仅在本地运行时可省略该选项。 |
| `--portal-url` | 覆盖用于注册的 Nous Portal 基础网址（默认值：您当前登录的门户地址）。也可通过 `HERMES_DASHBOARD_PORTAL_URL` 参数进行设置。 |

```bash
# Default — opens browser to http://127.0.0.1:9119
hermes dashboard

# Custom port, no browser
hermes dashboard --port 8080 --no-open

# From a profile alias — routes to the machine dashboard with the
# profile preselected in the sidebar switcher (attach if running)
worker dashboard
```

## `hermes profile`

```bash
hermes profile <subcommand>
```

管理配置文件——支持多个相互隔离的 Hermes 实例，每个实例拥有独立的配置、会话、技能及主目录。

| 子命令 | 描述 |
|----------|------|
| `list` | 列出所有配置文件。 |
| `use <name>` | 设置默认的固定配置文件。 |
| `create <name> [--clone] [--clone-all] [--clone-from <source>] [--no-alias]` | 创建新配置文件。`--clone` 会从当前激活的配置文件复制配置、`.env` 文件、`SOUL.md` 以及技能；`--clone-all` 会复制所有状态数据；`--clone-from` 指定源配置文件，若未搭配 `--clone-all` 使用，则仅复制配置。 |
| `delete <name> [-y]` | 删除配置文件。 |
| `show <name>` | 显示配置文件详情（如主目录、配置内容等）。 |
| `alias <name> [--remove] [--name NAME]` | 管理用于快速访问配置文件的封装脚本。 |
| `rename <old> <new>` | 重命名配置文件。 |
| `export <name> [-o FILE]` | 将配置文件导出为 `.tar.gz` 压缩包（用于本地备份）。 |
| `import <archive> [--name NAME]` | 从 `.tar.gz` 压缩包中导入配置文件（用于本地恢复）。 |
| `install <source> [--name N] [--alias] [--force] [-y]` | 从 git 地址或本地目录安装配置文件版本。 |
| `update <name> [--force-config] [-y]` | 重新拉取配置文件版本；保留用户数据（如记忆内容、会话信息、认证状态）。 |
| `info <name>` | 显示配置文件的版本信息、依赖项及来源。 |

示例：

```bash
hermes profile list
hermes profile create work --clone
hermes profile use work
hermes profile alias work --name h-work
hermes profile export work -o work-backup.tar.gz
hermes profile import work-backup.tar.gz --name restored
hermes profile install github.com/user/my-distro --alias
hermes profile update work
hermes -p work chat -q "Hello from work profile"
```

## `hermes completion` 功能

```bash
hermes completion [bash|zsh|fish]
```

将 Shell 自动补全脚本输出到标准输出。将该输出引入您的 Shell 配置文件中，即可实现对 Hermes 命令、子命令以及配置文件名称的 Tab 键自动补全。

示例：

```bash
# Bash
hermes completion bash >> ~/.bashrc

# Zsh
hermes completion zsh >> ~/.zshrc

# Fish
hermes completion fish > ~/.config/fish/completions/hermes.fish
```

## `hermes update` 命令

```bash
hermes update [--gateway] [--check] [--plan] [--no-backup] [--backup] [--yes]
```

该命令会拉取最新的 `hermes-agent` 源代码，并在管理的虚拟环境中重新安装所有依赖项，随后再次运行安装后的钩子程序（如 MCP 服务器启动、技能同步以及补全功能安装等）。因此可在实际生产环境中的安装环境中安全使用。若想在不进行实际安装的情况下查看当前代码版本是否落后于 `origin/main`，可使用 `--check` 参数。

`hermes update` 命令会获取配置好的更新分支（默认为 `main`）。如果当前代码位于其他分支上，Hermes 可能会在拉取代码之前先切换到该更新分支。若希望将特定分支上的修改保留下来，避免被自动纳入更新流程，建议在执行更新操作前先提交这些修改。

| 选项 | 描述 |
|------|-------------|
| `--gateway` | 用于消息传递 `/update` 命令的内部模式。该模式通过基于文件的进程间通信来传输提示信息和进度更新，而非从终端标准输入读取数据。此选项并非用于重启网关的标志。 |
| `--check` | 在不下载内容、安装依赖项或重启任何服务的情况下，检查是否有可用的更新。 |
| `--plan` | 输出更新计划并直接退出，不会对系统进行任何更改：包括安装方式（git/Docker/Nix/apt）、所有配置文件中正在运行的 Hermes 服务及其管理工具和当前代码版本，以及各自的重启方式。对于通过镜像或包管理的安装环境，该选项会输出相应的外部更新命令。此为只读选项。 |
| `--no-backup` | 跳过本次运行前的所有预更新备份（包括快速状态快照和完整压缩包），无论 `updates.pre_update_backup` 的设置为何。 |
| `--backup` | 强制为本次运行创建**完整**的预更新备份：即快速状态快照，再加上 `HERMES_HOME` 目录下的全部内容压缩包（包含配置文件、认证信息、会话数据、技能信息及配对数据）。默认模式为 `quick`，仅生成轻量级的状态快照。可通过在 `config.yaml` 中设置 `updates.pre_update_backup: quick | full | off` 来指定永久模式。 |
| `--yes`, `-y` | 对于配置迁移和暂存恢复等交互式提示，直接默认选择“是”。此选项会跳过 API 密钥的输入，如需处理相关操作，请单独运行 `hermes config migrate` 命令。 |

其他行为：

- **网关重启**。在更新成功后，Hermes会自动尝试重启所有正在运行的网关配置，以便它们能够加载新的代码。若您希望在不进行更新的情况下重启网关，则可使用`hermes gateway restart`命令。
- **重启阶段恢复**。在导入新获取的代码树时，如果进程内的重启阶段意外中断，受系统监控的网关配置将会通过一个全新的Python进程重新尝试重启。只有经过systemd确认已成功重启的配置（通过`systemctl --user is-active`命令检测）才会被标记为“已验证”；而仅以代码执行状态0结束的重启操作则会被记录为“已尝试重启”，出于谨慎考虑，此类操作仍会导致更新失败。未经特别授权，手动管理的网关以及服务器/控制台运行环境绝不会被强制终止，它们会被记录为“已跳过”，并附上具体原因，同时连同完整的重启命令一起保留在更新失败的报告中。
- **更新记录与集群版本检查**。每次运行都会在`~/.hermes/logs/update_receipts/`目录下生成一份机器可读的记录文件，内容包括更新前的集群计划、操作步骤、跳过原因以及重启结果；其中`latest.json`文件指向最新的记录。在重启阶段结束后，更新工具会将每个正在运行的网关的代码版本与更新后的版本进行比对，并输出针对每个配置的版本矩阵；如果某个网关仍在使用更新前的代码，则更新会失败（返回状态1），报告中也会注明具体的重启命令。
- **本地代码变更处理。** 对于通过 git 安装的版本，Hermes 会在检出分支或执行 pull 操作之前，自动将已跟踪的脏文件以及未跟踪的文件暂存起来（`git stash push --include-untracked`）。在交互式终端模式下，恢复暂存内容时会先询问用户确认；而非交互式更新则会默认恢复暂存内容。仅在对本地代码修改要求在成功 pull 后被丢弃的托管安装环境中，才可将 `updates.non_interactive_local_changes` 设置为 `discard`。如果恢复暂存内容时出现冲突或 pull 操作失败，暂存内容将保持原状，以便用户手动处理。
- **npm lockfile 变更清理。** 在暂存内容或切换分支之前，Hermes 会尽力清理由 npm install/build 步骤产生的已跟踪的 `package-lock.json` 差异文件。在运行 `hermes update` 前，请先将有意修改的 lockfile 内容提交或手动暂存。
- **配对数据快照功能。** 即使未开启 `--backup` 参数，`hermes update` 也会在执行 `git pull` 之前，对 `~/.hermes/pairing/` 目录以及飞书评论规则生成轻量级的快照。如果 pull 操作覆盖了您正在编辑的文件，可通过 `hermes backup restore --state pre-update` 将其恢复到之前的状态。
- **旧版 `hermes.service` 警告提示。** 如果 Hermes 检测到系统存在重命名前的 `hermes.service` systemd 单元（而非当前的 `hermes-gateway.service`），它会一次性输出迁移提示，帮助用户避免出现循环问题。
- **退出码说明。** 操作成功时返回 `0`；在 pull、安装或安装后出现错误时返回 `1`；因工作区出现意外变更而无法执行 `git pull` 时返回 `2`。

## 维护命令

| 命令 | 描述 |
|---------|-------------|
| `hermes --version` | 显示版本信息。 |
| `hermes update` | 下载最新更新并重新安装依赖项。 |

| `hermes uninstall [--full] [--gui] [--dry-run] [--yes]` | 卸载 Hermes，可选择是否同时删除所有配置文件和数据。`--gui` 仅删除桌面端聊天界面，保留 Agent 功能；`--full` 会同时删除配置文件和数据；`--dry-run` 仅显示将要删除的内容而不会实际执行任何操作；`--yes` 跳过确认提示。 |

## 参见

- [Slash Commands 参考文档](./slash-commands.md)
- [CLI 接口](../user-guide/cli.md)
- [会话管理](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)
