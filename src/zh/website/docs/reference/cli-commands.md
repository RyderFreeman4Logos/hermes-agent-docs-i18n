---
sidebar_position: 1
title: "CLI Commands Reference"
description: "Authoritative reference for Hermes terminal commands and command families"
---

# CLI 命令参考

本页面介绍了您在终端中可使用的**命令行指令**。

有关聊天界面内的斜杠命令，请参阅 [斜杠命令参考](./slash-commands.md)。

## 全局入口点

```bash
hermes [global-options] <command> [subcommand/options]
```

### 全局选项

| 选项 | 描述 |
|------|------|
| `--version`, `-V` | 显示版本信息后退出。 |
| `--profile <name>`, `-p <name>` | 指定本次调用使用的 Hermes 配置文件。会覆盖由 `hermes profile use` 设置的默认值。 |
| `--resume <session>`, `-r <session>` | 根据会话 ID 或标题恢复之前的会话。 |
| `--continue [name]`, `-c [name]` | 恢复最近的会话，或与指定标题匹配的最新会话。 |
| `--worktree`, `-w` | 为并行 Agent 工作流在独立的 git worktree 中启动。 |
| `--yolo` | 跳过危险命令的确认提示。 |
| `--pass-session-id` | 在 Agent 的系统提示中显示会话 ID。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml` 文件，使用内置默认设置。不过 `.env` 文件中的凭据仍会被加载。 |
| `--ignore-rules` | 跳过自动注入的 `AGENTS.md`、`SOUL.md`、`.cursorrules`、内存内容以及预加载的技能。 |
| `--tui` | 启动 [TUI](../user-guide/tui.md) 而非传统的 CLI 界面。相当于设置 `HERMES_TUI=1`。该选项始终优先于 `display.interface` 的设置。 |
| `--cli` | 强制使用传统的 prompt_toolkit REPL。可在单次调用时覆盖 `display.interface: tui` 的设置。 |
| `--dev` | 与 `--tui` 结合使用时：直接通过 `tsx` 运行 TypeScript 源代码，而非预编译的打包文件（适用于 TUI 开发者）。 |

## 顶层命令

| 命令 | 用途 |
|------|------|
| `hermes chat` | 与 Agent 进行交互式或一次性聊天。 |
| `hermes model` | 交互式选择默认的提供商和模型。 |
| `hermes moa` | 配置可在模型选择器中选择的命名型混合 Agent 预设。 |
| `hermes fallback` | 管理在主模型出现错误时尝试使用的备用提供商。 |
| `hermes gateway` | 运行或管理消息传递网关服务。 |
| `hermes proxy` | 本地兼容 OpenAI 的代理，用于附加 OAuth 提供商的凭据。详见 [订阅代理](../user-guide/features/subscription-proxy.md)。 |
| `hermes lsp` | 管理语言服务器协议集成（为 write_file/patch 操作提供语义诊断功能）。 |
| `hermes setup` | 用于全部或部分配置的交互式设置向导。 |
| `hermes whatsapp` | 配置并关联 WhatsApp 桥接服务。 |
| `hermes whatsapp-cloud` | 配置官方的 Meta WhatsApp Business Cloud API 适配器（需要企业账户及公共 webhook）。与 `hermes whatsapp`（Baileys 的个人账户桥接）不同。 |
| `hermes slack` | Slack 相关工具（目前功能为：每个命令都会生成一个作为原生 slash 命令的应用清单）。 |
| `hermes auth` | 管理凭据——添加、列出、删除、重置、查看状态及登出。支持 Codex/Nous/Anthropic 的 OAuth 流程。 |
| `hermes login` / `logout` | **已废弃**——请改用 `hermes auth`。 |
| `hermes send` | 向已配置的消息平台（Telegram、Discord、Slack、Signal、短信等）发送一次性消息。适用于 shell 脚本、cron 作业、CI 钩子以及监控进程——无需 Agent 循环，也不涉及大语言模型。 |
| `hermes secrets` | 管理外部密钥源（目前为 Bitwarden Secrets Manager），以便在进程启动时从这些来源获取 API 密钥，而非从 `~/.hermes/.env` 文件读取。 |
| `hermes migrate` | 诊断并（可选）重写 `config.yaml` 文件，替换已废弃模型或过时设置的相关引用（例如 `migrate xai`）。 |
| `hermes status` | 显示 Agent、认证及平台的状态信息。 |
| `hermes cron` | 查看并管理 cron 定时任务调度器。 |
| `hermes kanban` | 多配置文件协作看板（用于管理任务、链接及任务分配者）。 |
| `hermes project` | 管理带名称的多文件夹工作空间（即项目）。它可固定桌面会话分组，且当与看板关联时，还能为任务设定固定的 worktree 结构和分支命名规则。状态信息按配置文件独立存储。 |
| `hermes webhook` | 管理用于事件驱动激活的动态 webhook 订阅。 |
| `hermes hooks` | 查看、批准或删除在 `config.yaml` 中声明的 shell 脚本钩子。 |
| `hermes doctor` | 诊断配置及依赖问题。 |
| `hermes security audit` | 对虚拟环境、插件需求以及固定的 MCP 服务器进行按需的供应链审计（由 OSV.dev 提供服务）。 |
| `hermes dump` | 生成可复制粘贴的设置摘要，便于获取支持或进行调试。 |
| `hermes prompt-size` | 显示系统提示语及工具架构（技能索引、内存、配置文件）的字节占用情况。可在离线环境下运行。 |
| `hermes debug` | 调试工具——上传日志和系统信息以寻求技术支持。 |
| `hermes backup` | 将 Hermes 的主目录备份为 zip 文件。 |
| `hermes checkpoints` | 查看、清理或删除 `~/.hermes/checkpoints/` 目录中的内容（该目录是 `/rollback` 功能使用的隐藏存储空间）。不带参数运行可查看整体状态。 |
| `hermes import` | 从 zip 文件恢复 Hermes 备份数据。 |
| `hermes logs` | 查看、查看日志尾部内容及过滤 Agent/网关/错误日志文件。 |
| `hermes config` | 显示、编辑、迁移及查询配置文件。 |
| `hermes pairing` | 批准或撤销消息传递配对码。 |
| `hermes skills` | 浏览、安装、发布、审计及配置技能。 |
| `hermes bundles` | 将多个技能整合到单个 `/<name>` 形式的命令下。详见 [技能包](../user-guide/features/skills.md#skill-bundles)。 |
| `hermes curator` | 在后台维护技能——可查看状态、运行、暂停或固定技能。详见 [Curator](../user-guide/features/curator.md)。 |
| `hermes memory` | 配置外部内存提供商。当对应的提供商处于激活状态时，特定插件会自动注册相应的子命令（例如 `hermes honcho`）。 |
| `hermes acp` | 将 Hermes 作为 ACP 服务器运行，以实现与编辑器的集成。 |
| `hermes mcp` | 管理 MCP 服务器配置，并将 Hermes 运行为 MCP 服务器。 |
| `hermes plugins` | 管理 Hermes Agent 插件（安装、启用、禁用、删除）。 |
| `hermes portal` | 显示 Nous Portal 的状态、订阅链接以及工具网关的路由信息。详见 [工具网关](../user-guide/features/tool-gateway.md)。 |
| `hermes tools` | 按平台配置已启用的工具。 |
| `hermes computer-use` | 安装或检查 cua-driver 后端（用于 macOS 的“计算机使用”功能）。 |
| `hermes pets` | 浏览、安装并选择可在 CLI、TUI 以及桌面应用中查看的 [petdex](../user-guide/features/pets.md) 动画宠物。相关子命令包括：`list`、`install`、`select`、`show`、`off`、`scale`、`remove`、`doctor`。 |
| `hermes sessions` | 浏览、导出、清理、重命名及删除会话。 |
| `hermes insights` | 显示令牌使用量/成本/活动统计信息。 |
| `hermes claw` | OpenClaw 迁移辅助工具。 |
| `hermes dashboard` | 启动用于管理配置、API 密钥及会话的网页控制面板。 |
| `hermes desktop`（别名 `gui`） | 构建并启动原生的 Electron 桌面应用。 |
| `hermes profile` | 管理多个独立的 Hermes 实例，即不同的配置文件。 |
| `hermes completion` | 输出 shell 自动补全脚本（支持 bash/zsh/fish）。 |
| `hermes version` | 显示版本信息。 |
| `hermes update` | 下载最新代码并重新安装依赖项。`--check` 选项可预览更新内容而无需实际安装；`--backup` 选项会在更新前创建 `HERMES_HOME` 的快照。 |
| `hermes uninstall` | 从系统中移除 Hermes。 |

## `hermes chat`

```bash
hermes chat [options]
```

常用选项：

| 选项 | 描述 |
|------|------|
| `-q`, `--query "..."` | 单次使用的非交互式提示。 |
| `-m`, `--model <model>` | 覆盖本次运行的模型。 |
| `-t`, `--toolsets <csv>` | 启用以逗号分隔的工具集列表。 |
| `--provider <provider>` | 强制指定提供方：`auto`、`openrouter`、`nous`、`openai-codex`、`copilot-acp`、`copilot`、`anthropic`、`gemini`、`huggingface`、`novita`（别名 `novita-ai`、`novitaai`）、`openai-api`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`kilocode`、`xiaomi`、`arcee`、`gmi`、`upstage`（别名 `solar`）、`alibaba`、`alibaba-coding-plan`（别名 `alibaba_coding`）、`deepseek`、`nvidia`、`ollama-cloud`、`xai`（别名 `grok`）、`xai-oauth`（别名 `grok-oauth`）、`qwen-oauth`、`bedrock`、`opencode-zen`、`opencode-go`、`azure-foundry`、`lmstudio`、`stepfun`、`tencent-tokenhub`（别名 `tencent`、`tokenhub`）。 |
| `-s`, `--skills <name>` | 为当前会话预加载一个或多个技能（可重复指定或用逗号分隔）。 |
| `-v`, `--verbose` | 显示详细输出。 |
| `-Q`, `--quiet` | 程序化模式：隐藏横幅、加载指示器及工具预览。 |
| `--image <path>` | 为单个查询附加本地图片。 |
| `--resume <session>` / `--continue [name]` | 直接从 `chat` 模式恢复会话。 |
| `--worktree` | 为本次运行创建独立的 Git 工作树。 |
| `--checkpoints` | 在进行可能破坏文件的更改之前启用文件系统检查点。 |
| `--yolo` | 跳过审批提示。 |
| `--pass-session-id` | 将会话 ID 传递到系统提示中。 |
| `--ignore-user-config` | 忽略 `~/.hermes/config.yaml` 文件，使用内置默认设置。不过 `.env` 文件中的凭据仍会被加载。此选项适用于独立的 CI 运行、可复现的错误报告以及第三方集成场景。 |
| `--ignore-rules` | 跳过自动注入的 `AGENTS.md`、`SOUL.md`、`.cursorrules`、持久化内存及预加载的技能。可与 `--ignore-user-config` 结合使用，实现完全隔离的运行环境。 |
| `--safe-mode` | 故障排查模式：禁用所有自定义设置——包括用户配置、规则/内存注入、插件、Shell 钩子以及 MCP 服务器（该模式会自动启用 `--ignore-user-config` 和 `--ignore-rules`）。可用于判断问题源于用户设置还是 Hermes 本身。 |
| `--source <tag>` | 用于过滤的会话来源标签（默认值为 `cli`）。对于不应出现在用户会话列表中的第三方集成，可使用 `tool` 标签。 |
| `--max-turns <N>` | 每次对话轮次中最多允许的工具调用次数（默认值为 90，或配置文件中的 `agent.max_turns` 设置值）。 |

示例：

```bash
hermes
hermes chat -q "Summarize the latest PRs"
hermes chat --provider openrouter --model anthropic/claude-sonnet-4.6
hermes chat --toolsets web,terminal,skills
hermes chat --quiet -q "Return only JSON"
hermes chat --worktree -q "Review this repo and open a PR"
hermes chat --ignore-user-config --ignore-rules -q "Repro without my personal setup"
hermes chat --safe-mode -q "Is this bug mine or Hermes'?"
```

### `hermes -z <prompt>` — 脚本化单次调用模式

对于通过程序方式调用的用户（如Shell脚本、CI系统、cron作业，或是向代理传递提示语的父进程），`hermes -z` 是最纯粹的单次调用入口：**输入一个提示语，即可得到最终响应文本，标准输出和标准错误均不会输出其他内容**。没有欢迎横幅、没有加载指示器、没有工具预览信息，也没有`Session:`行——仅有以纯文本形式呈现的代理最终回复。

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
| `--provider <provider>` | _(无)_ | 覆盖本次运行的提供方 |

```bash
hermes -z "…" --provider openrouter --model openai/gpt-5.5
# or:
HERMES_INFERENCE_MODEL=anthropic/claude-sonnet-4.6 hermes -z "…"
```

相同的智能体、相同的工具、相同的技能——仅去除了所有交互式及界面装饰层。如果需要在对话记录中同时显示工具的输出结果，请改用 `hermes chat -q` 命令；而 `-z` 明确用于表示“我只想要最终答案”。

## `hermes model`

交互式提供者与模型选择器。**该命令用于添加新的提供者、配置 API 密钥以及执行 OAuth 流程。** 应在终端中运行此命令，而非在正在进行的 Hermes 对话会话内部执行。

```bash
hermes model
```

在以下情况下请使用此功能：
- **添加新的提供方**（如 OpenRouter、Anthropic、Copilot、DeepSeek 或自定义提供方等）
- 登录基于 OAuth 的提供方（如 Anthropic、Copilot、Codex、Nous Portal）
- 输入或更新 API 密钥
- 从特定提供方的模型列表中选择
- 配置自定义/自托管的端点
- 将新默认设置保存到配置文件中

:::warning hermes model 与 /model 的区别 —— 请务必了解
**`hermes model`**（在终端中运行，独立于任何 Hermes 会话）是**完整的提供方设置向导**。它能够添加新的提供方、执行 OAuth 流程、提示输入 API 密钥以及配置端点。

而 **`/model`**（在正在运行的 Hermes 聊天会话中输入）仅能**在您已设置的提供方和模型之间切换**，无法添加新提供方、执行 OAuth 流程或提示输入 API 密钥。

**如果您需要添加新的提供方**：请先退出当前的 Hermes 会话（使用 `Ctrl+C` 或 `/quit`），然后在终端命令行中运行 `hermes model`。
:::

### `/model` 斜杠命令（会话进行中）

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

默认情况下，对 `/model` 的更改**仅适用于当前会话**。若要将该更改永久保存到 `config.yaml` 中，请添加 `--global` 参数：

```
/model claude-sonnet-4 --global     # Switch and save as new default
```

:::info 如果我只看到 OpenRouter 模型怎么办？
如果您仅配置了 OpenRouter，那么 `/model` 命令将只会显示 OpenRouter 的模型。若要添加其他提供商（如 Anthropic、DeepSeek、Copilot 等），请退出当前会话，然后通过终端运行 `hermes model` 命令。
:::

提供商及基础 URL 的更改会自动保存到 `config.yaml` 文件中。当切换离开自定义端点时，旧的基准 URL 会被清除，以避免其影响其他提供商的连接。

## `hermes gateway`

```bash
hermes gateway <subcommand>
```

子命令：

| 子命令 | 描述 |
|----------|------|
| `run` | 在前台运行网关。推荐用于 WSL、Docker 和 Termux 环境。 |
| `start` | 启动已安装的 systemd/launchd 后台服务。 |
| `stop` | 停止该服务（或前台进程）。 |
| `restart` | 重启该服务。 |
| `status` | 显示服务状态。 |
| `list` | 列出**所有配置文件**，以及每个配置文件的网关当前是否正在运行（如有 PID 也会一并显示）。当您同时运行多个配置文件并希望获得整体概览时非常实用。 |
| `install` | 作为 systemd（Linux）或 launchd（macOS）后台服务进行安装。 |
| `uninstall` | 卸载已安装的服务。 |
| `setup` | 交互式消息平台设置。 |
| `migrate-legacy` | 删除因早期版本安装而遗留的旧版 `hermes.service` 单元文件。配置文件单元文件（`hermes-gateway-<profile>.service`）及无关服务不会受到影响。可选参数：`--dry-run`、`-y`/`--yes`。 |
| `enroll` | 实验性功能：将此网关注册到中继连接器，并为基于连接器的平台保存中继凭据。 |

选项：

| 选项 | 描述 |
|------|------|
| `--all` | 在 `start` / `restart` / `stop` 操作时，会对**所有配置文件**的网关生效，而不仅限于当前激活的 `HERMES_HOME`。如果您同时运行多个配置文件，并希望在执行 `hermes update` 后同时重启它们，此选项非常有用。 |
| `--no-supervise` | 在 `run` 操作时，对于使用 s6-overlay Docker 镜像的场景，可取消自动监控功能，采用 s6 之前的前台进程运行模式——网关将以容器的主进程形式运行且不会自动重启。在非 s6 镜像环境下此选项无效。其效果等同于设置 `HERMES_GATEWAY_NO_SUPERVISE=1`。 |

`hermes gateway enroll` 命令支持 `--token`、`--connector-url`、`--gateway-id` 和 `--wake-url` 参数。它会将注册令牌与连接器进行交换，然后将生成的 `GATEWAY_RELAY_ID`、`GATEWAY_RELAY_SECRET`、`GATEWAY_RELAY_DELIVERY_KEY`、可选的 `GATEWAY_RELAY_URL`，以及当提供了 `--wake-url` 时的 `GATEWAY_RELAY_WAKE_URL` 值写入当前激活配置文件的 `.env` 文件中。

:::提示 WSL 用户
建议使用 `hermes gateway run` 而非 `hermes gateway start`——WSL 环境的 systemd 支持并不可靠。为确保设置持久化，可将其封装在 tmux 中运行：`tmux new -s hermes 'hermes gateway run'`。更多详情请参阅 [WSL 常见问题](/reference/faq#wsl-gateway-keeps-disconnecting-or-hermes-gateway-start-fails)。
:::

## `hermes lsp`

```bash
hermes lsp <subcommand>
```

用于管理语言服务器协议集成。LSP会在后台运行真正的语言服务器（如pyright、gopls、rust-analyzer等），并将这些服务器提供的诊断信息传递给`write_file`和`patch`函数所使用的写后检查功能。该功能的启用以检测是否处于Git工作区为条件——仅当当前工作目录或正在编辑的文件位于Git工作树中时，LSP才会启动。

子命令：

| 子命令 | 描述 |
|----------|------|
| `status` | 显示服务状态、已配置的语言服务器以及安装状态。 |
| `list` | 列出所有受支持的语言服务器。可使用`--installed-only`选项跳过那些未安装的服务器。 |
| `install <id>` | 立即安装指定语言服务器的二进制文件。 |
| `install-all` | 安装所有有自动安装方案的支持语言服务器。 |
| `restart` | 销毁正在运行的客户端，以便在下一次编辑时重新启动相关服务。 |
| `which <id>` | 显示指定语言服务器的最终二进制文件路径。 |

如需完整指南、支持的语言列表以及各类配置选项，请参阅[LSP — 语义诊断](/user-guide/features/lsp)。

## `hermes setup`

```bash
hermes setup [model|tts|terminal|gateway|tools|agent] [--non-interactive] [--reset] [--quick] [--reconfigure] [--portal]
```

**最简便的路径：** 使用命令 `hermes setup --portal` — 通过 OAuth 登录 Nous Portal，即可一次性完成配置并启用[工具网关](../user-guide/features/tool-gateway.md)。

**首次运行时：** 程序会启动首次配置向导。

**已配置过的用户：** 直接进入完整的重新配置向导 — 每个提示项都会以当前设置值作为默认值，按回车键即可保留该值，或输入新值。无需菜单导航。

如需直接跳转至特定配置板块而非完整向导：

| 板块 | 描述 |
|---------|-------------|
| `model` | 提供商与模型配置。 |
| `terminal` | 终端后端及沙箱环境配置。 |
| `gateway` | 消息传递平台配置。 |
| `tools` | 按平台启用或禁用各类工具。 |
| `agent` | 智能体行为设置。 |

可选参数：

| 参数 | 描述 |
|--------|-------------|
| `--quick` | 用于已配置用户：仅询问缺失或未设置的项，跳过已配置好的选项。 |
| `--non-interactive` | 直接使用默认值或环境变量，无需任何提示。 |
| `--reset` | 在开始配置前将所有设置重置为默认值。 |
| `--reconfigure` | 兼容旧版本的别名 — 现在在已安装的环境中直接执行 `hermes setup` 即会默认执行此操作。 |
| `--portal` | 一次性完成 Nous Portal 配置：通过 OAuth 登录，将 Nous 设定为推理提供商，并启用[工具网关](../user-guide/features/tool-gateway.md)，跳过其余配置步骤。 |

## `hermes portal`

```bash
hermes portal [status|open|tools]
```

可检查 Nous Portal 的认证状态、Tool Gateway 的路由情况，并跳转至订阅页面。若不指定子命令，则会执行 `status` 操作。

| 子命令 | 描述 |
|----------|------|
| `status`（默认值） | 显示 Portal 的认证状态以及各工具对应的 Tool Gateway 路由汇总信息。未指定子命令时也会显示该内容。 |
| `open` | 在您的默认浏览器中打开 `portal.nousresearch.com/manage-subscription` 页面。 |
| `tools` | 列出所有 Tool Gateway 合作伙伴（Firecrawl、FAL、OpenAI TTS、Browser Use、Modal），以及通过 Nous 进行路由的工具。 |

如需配置 Gateway 本身，请参阅 [Tool Gateway](../user-guide/features/tool-gateway.md)。关于一次性设置流程，请参考上文中的 `hermes setup --portal` 命令。

## `hermes whatsapp`

```bash
hermes whatsapp
```

执行 WhatsApp 配对/设置流程，包括模式选择与二维码配对功能。  

## `hermes slack`

```bash
hermes slack manifest              # print manifest to stdout
hermes slack manifest --write      # write to ~/.hermes/slack-manifest.json
hermes slack manifest --slashes-only  # just the features.slash_commands array
```

该工具会生成一个 Slack 应用清单文件，将 `COMMAND_REGISTRY` 中的所有网关命令（如 `/btw`、`/stop`、`/model` 等）都注册为一级 Slack 斜杠命令——从而实现与 Discord 和 Telegram 的功能对等。只需将生成的输出内容粘贴到您的 Slack 应用配置页面：[https://api.slack.com/apps](https://api.slack.com/apps) → 所选应用 → **Features → App Manifest → Edit**，最后点击 **Save** 即可。如果权限范围或斜杠命令发生变更，Slack 会提示您重新安装应用。

| 参数 | 默认值 | 用途 |
|------|---------|------|
| `--write [路径]` | stdout | 将输出写入文件而非标准输出。仅使用 `--write` 时，内容将保存至 `$HERMES_HOME/slack-manifest.json`。 |
| `--name 名称` | `Hermes` | 机器人在 Slack 中显示的名称。 |
| `--description 描述` | 默认文本 | 显示在 Slack 应用目录中的机器人描述。 |
| `--slashes-only` | 关闭 | 仅输出 `features.slash_commands`，以便用于手动维护的清单文件中。 |

在执行 `hermes update` 后，建议再次运行 `hermes slack manifest --write`，以便获取新增的命令。

## `hermes send`

```bash
hermes send --to <target> "message text"
hermes send --to <target> --file <path>
echo "message" | hermes send --to <target>
hermes send --list [platform]
```

无需启动代理或网关循环，即可向已配置的消息平台发送一次性消息。该功能会复用网关中已配置的凭证（`~/.hermes/.env` 和 `~/.hermes/config.yaml`），因此操作脚本、定时任务、CI 钩子以及监控进程都无需为每个平台重新实现 REST 客户端，即可发送状态更新。

对于基于机器人令牌的平台（Telegram、Discord、Slack、Signal、短信、WhatsApp-CloudAPI），无需运行网关——`hermes send` 直接与这些平台的 REST 接口通信。而那些需要持久适配器的插件平台则仍需运行中的网关。

| 选项 | 描述 |
|------|------|
| `-t`, `--to <TARGET>` | 消息发送目标。格式包括：`platform`（使用主频道）、`platform:chat_id`、`platform:chat_id:thread_id` 或 `platform:#channel-name`。示例：`telegram`、`telegram:-1001234567890`、`discord:#ops`、`slack:C0123ABCD`、`signal:+15551234567`。 |
| `-f`, `--file <PATH>` | 从指定路径读取消息内容（仅支持文本文件，如日志、报告、Markdown 文件）。若要强制从标准输入读取，可使用 `-`。若需发送图片或其他二进制文件，请使用 `MEDIA:<path>`（见下文）。 |
| `-s`, `--subject <LINE>` | 在消息内容前添加主题行/标题行。 |
| `-l`, `--list [platform]` | 列出所有平台上已配置的目标（或仅列出指定平台的目标）。 |
| `-q`, `--quiet` | 成功时抑制标准输出——在脚本中使用非常方便（只需依赖退出码即可）。 |
| `--json` | 输出原始 JSON 格式的结果，而非可读文本。 |

如果既未提供位置参数 `message`，也未使用 `--file`，则当输入端不是 TTY 时，`hermes send` 会从标准输入读取内容。退出码含义：`0` 表示成功，`1` 表示发送或后端处理失败，`2` 表示用法错误。

### 发送图片及其他媒体文件

`--file` 仅用于文本类型的消息内容。若要将图片、文档、视频或音频文件作为平台原生附件发送，可在消息文本中使用 `MEDIA:<本地路径>` 指令来引用该文件：

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


## `hermes secrets`

```bash
hermes secrets bitwarden <subcommand>
hermes secrets bw <subcommand>          # short alias
```

在进程启动时，可从外部密钥管理器获取 API 密钥，而无需将其存储在 `~/.hermes/.env` 文件中。目前支持 **Bitwarden Secrets Manager**。完整指南请参阅：[Bitwarden 集成](../user-guide/secrets/bitwarden.md)。

`bitwarden`（别名 `bw`）子命令：

| 子命令 | 描述 |
|----------|------|
| `setup` | 交互式向导：安装指定的 `bws` 可执行文件，存储访问令牌，并选择项目。如需非交互式使用，可指定 `--project-id`、`--access-token` 和 `--server-url` 参数。 |
| `status` | 显示当前的配置信息、可执行文件路径/版本以及上次获取数据的时间。 |
| `sync` | 立即获取密钥并说明有哪些变化。添加 `--apply` 参数即可将密钥实际导出到当前 Shell 的环境变量中（默认为仅模拟操作）。 |
| `install` | 下载并验证指定的 `bws` 可执行文件。即使已存在托管版本，使用 `--force` 参数仍会重新下载。 |
| `disable` | 关闭 Bitwarden 集成功能。 |


## `hermes migrate`

```bash
hermes migrate <type>
```

诊断当前有效的 `config.yaml` 文件，并（可选地）重新编写该文件，以替换那些已停止使用的模型或过时的设置。在进行任何重写操作之前，系统会先创建原始 `config.yaml` 的带时间戳备份（如需跳过此步骤，请使用 `--no-backup` 参数）。

| 子命令 | 描述 |
|----------|------|
| `xai` | 扫描 `config.yaml` 文件，找出那些计划在 2026 年 5 月 15 日停止使用的 xAI 模型的引用；如使用 `--apply` 参数，则会根据 xAI 迁移指南将这些引用直接替换为官方推荐的替代模型。默认为仅进行模拟操作。 |

迁移子命令的常用参数：

| 参数 | 描述 |
|------|------|
| `--apply` | 直接在原位置重写 `config.yaml` 文件（默认为仅模拟操作，不进行实际写入）。 |
| `--no-backup` | 在执行重写操作时跳过创建 `config.yaml` 的带时间戳备份。 |

> 请注意，此命令与 `hermes claw migrate`（将 OpenClaw 配置一次性导入 Hermes）不同——`hermes migrate` 才是用于重写配置文件的高级命令。

## `hermes proxy`

```bash
hermes proxy <subcommand>
```

运行一个本地版的 OpenAI 兼容 HTTP 服务器，该服务器可将请求转发至经过 OAuth 认证的上游服务提供商（例如 Nous Portal、xAI）。外部应用可使用任意承载令牌指向此代理；在数据传出时，代理会自动附加您的真实 OAuth 凭证。详细指南请参阅 [订阅代理](../user-guide/features/subscription-proxy.md)。

| 子命令 | 描述 |
|----------|------|
| `start` | 在前台运行代理。可选参数：`--provider <nous\|xai>`（默认为 `nous`），`--host <addr>`（默认为 `127.0.0.1`；若需在局域网中暴露，则使用 `0.0.0.0`），`--port <int>`（默认为 `8645`）。 |
| `status` | 显示哪些代理上游服务已准备就绪（即凭证存在且 OAuth 验证通过）。 |
| `providers` | 列出所有可用的代理上游服务提供商。 |


## `hermes security`

```bash
hermes security <subcommand>
```

可针对 [OSV.dev](https://osv.dev) 执行按需漏洞扫描。扫描范围包括 Hermes 虚拟环境（通过 PyPI 安装的版本）、位于 `~/.hermes/plugins/` 下由插件声明的 Python 依赖项，以及 `config.yaml` 中指定的固定 `npx`/`uvx` MCP 服务器。不会扫描全局安装的包或编辑器/浏览器扩展程序。

| 子命令 | 描述 |
|----------|------|
| `audit` | 执行一次性的供应链安全审计。 |

`audit` 的标志选项：

| 标志 | 默认值 | 描述 |
|------|---------|------|
| `--json` | 关闭 | 以机器可读的 JSON 格式输出结果，而非人类可读的文本。 |
| `--fail-on <严重级别>` | `critical` | 若发现任何严重级别为 `low`、`moderate`、`high` 或 `critical` 的问题，则以非零状态退出。 |
| `--skip-venv` | 关闭 | 跳过对 Hermes Python 虚拟环境的扫描。 |
| `--skip-plugins` | 关闭 | 跳过对插件依赖文件的扫描。 |
| `--skip-mcp` | 关闭 | 跳过对 `config.yaml` 中指定的固定 MCP 服务器的扫描。 |


## `hermes login` / `hermes logout` *(已废弃)*

:::caution
`hermes login` 已被移除。如需管理 OAuth 凭证，请使用 `hermes auth`；选择提供方则可使用 `hermes model`；如需进行完整交互式设置，则可使用 `hermes setup`。
:::

## `hermes auth`

用于管理同一提供方的凭证池以实现密钥轮换。详细文档请参阅 [凭证池](/user-guide/features/credential-pools)。

```bash
hermes auth                                              # Interactive wizard
hermes auth list                                         # Show all pools
hermes auth list openrouter                              # Show specific provider
hermes auth add openrouter --api-key sk-or-v1-xxx        # Add API key
hermes auth add anthropic --type oauth                   # Add OAuth credential
hermes auth remove openrouter 2                          # Remove by index
hermes auth reset openrouter                             # Clear cooldowns
hermes auth status anthropic                             # Show auth status for a provider
hermes auth logout anthropic                             # Log out and clear stored auth state
hermes auth spotify                                      # Authenticate Hermes with Spotify via PKCE
```

子命令包括：`add`、`list`、`remove`、`reset`、`status`、`logout`、`spotify`。若未指定任何子命令，则会启动交互式管理向导。

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
hermes cron <list|create|edit|pause|resume|run|remove|status|tick>
```

| 子命令 | 描述 |
|----------|------|
| `list` | 显示已安排的作业。 |
| `create` / `add` | 根据提示创建定时作业，可通过多次使用 `--skill` 选项附加一个或多个技能。 |
| `edit` | 更新作业的调度时间、提示语、名称、交付方式、重复次数或附加的技能。支持 `--clear-skills`、`--add-skill` 和 `--remove-skill` 参数。 |
| `pause` | 暂停作业而不删除它。 |
| `resume` | 恢复被暂停的作业，并计算其下一次运行时间。 |
| `run` | 在下一个调度周期触发该作业执行。 |
| `remove` | 删除已安排的作业。 |
| `status` | 检查 cron 调度器是否正在运行。 |
| `tick` | 执行到期的作业一次后退出。 |

Cron **触发器**可通过 `cron.provider` 配置键进行插件化扩展。保持该值为空（即默认值）时，将使用内置的进程内计时器。若将其设置为 `chronos`（一种由 NAS 管理、适用于零扩展规模托管网关的提供者），则需通过 `cron.chronos.*` 相关键值（如 `portal_url`、`callback_url`、`expected_audience`、`nas_jwks_url`）进行配置；或者可以在 `plugins/cron/<名称>/` 或 `$HERMES_HOME/plugins/<名称>/` 下自定义提供者名称。如果指定的提供者未知或不可用，系统会回退到内置触发器，因此始终不会出现没有触发器的状况。详情请参阅 [Cron 内部机制](../developer-guide/cron-internals.md#gateway-integration) 文档。

## `hermes kanban`

```bash
hermes kanban [--board <slug>] <action> [options]
```

支持多配置文件、多项目的协作看板功能。每次安装均可创建多个看板（每个项目、仓库或域名对应一个看板）；每个看板均为独立的队列，拥有自己的 SQLite 数据库及调度器作用域。新安装时会自动生成一个名为 `default` 的看板，为兼容旧版本，其数据库位于 `~/.hermes/kanban.db`；其他看板的数据库则存放在 `~/.hermes/kanban/boards/<slug>/kanban.db` 中。内置在网关中的调度器会定期遍历所有看板。

**全局标志（适用于以下所有操作）：**

| 标志 | 用途 |
|------|------|
| `--board <slug>` | 对指定看板执行操作。默认为当前看板（可通过 `hermes kanban boards switch`、环境变量 `HERMES_KANBAN_BOARD` 或 `default` 设置）。 |

**这是供人类操作或脚本使用的接口。** 由调度器生成的 Agent 工作进程会通过专用的 `kanban_*` [工具集](/user-guide/features/kanban#how-workers-interact-with-the-board)（如 `kanban_show`、`kanban_complete`、`kanban_block`、`kanban_create`、`kanban_link`、`kanban_comment`、`kanban_heartbeat`；编排型配置文件还包含 `kanban_list` 和 `kanban_unblock`）来操作看板，而无需直接调用 `hermes kanban` 命令。这些工作进程的环境中会固定设置 `HERMES_KANBAN_BOARD`，因此它们无法看到其他看板。

| 操作 | 用途 |
|------|------|
| `init` | 若缺失则创建 `kanban.db` 文件。该操作是幂等的。 |
| `boards list` / `boards ls` | 列出所有看板及其任务数量。可添加 `--json`、`--all`（包含已归档的看板）选项。 |
| `boards create <slug>` | 创建新看板。支持参数：`--name`、`--description`、`--icon`、`--color`、`--switch`（设为当前活动看板）。Slug 名称采用 kebab-case 格式，且会自动转为小写。 |
| `boards switch <slug>` / `boards use` | 将 `<slug>` 设为当前活动看板（会将该设置写入 `~/.hermes/kanban/current` 文件）。 |
| `boards show` / `boards current` | 输出当前活动看板的名称、数据库路径及任务数量。 |
| `boards rename <slug> "<name>"` | 更改看板的显示名称。Slug 名称不可修改。 |
| `boards rm <slug>` | 将看板归档（默认操作）或彻底删除。使用 `--delete` 可跳过归档步骤。已归档的看板会移至 `boards/_archived/<slug>-<ts>/` 目录下。`default` 看板不可执行此操作。 |
| `create "<title>"` | 在当前活动看板上创建新任务。支持参数：`--body`、`--assignee`、`--parent`（可重复指定）、`--workspace scratch\|worktree\|dir:<path>`、`--tenant`、`--priority`、`--triage`、`--idempotency-key`、`--max-runtime`、`--max-retries`、`--skill`（可重复指定）。 |
| `list` / `ls` | 列出当前活动看板上的所有任务。可通过 `--mine`、`--assignee`、`--status`、`--tenant`、`--archived`、`--json` 进行过滤。 |
| `show <id>` | 显示包含评论和事件信息的任务详情。可使用 `--json` 选项获取机器可读的输出格式。 |
| `assign <id> <profile>` | 为任务分配或重新分配处理者。使用 `none` 可取消分配。任务正在运行时无法执行此操作。 |
| `link <parent> <child>` | 添加任务依赖关系。系统会检测循环依赖，且两个任务必须位于同一个看板中。 |
| `unlink <parent> <child>` | 移除任务之间的依赖关系。 |
| `claim <id>` | 原子性地处理已完成的任务，并输出对应的处理路径。 |
| `comment <id> "<text>"` | 为任务添加评论。下一个处理该任务的 Worker 会在其 `kanban_show()` 的响应中读取到这条评论。 |
| `complete <id>` | 标记任务为已完成。支持参数：`--result`、`--summary`、`--metadata`。 |
| `block <id> "<reason>"` | 将任务标记为需要人工处理，并附上原因作为评论。 |
| `schedule <id> "<reason>"` | 将需延迟处理或后续跟进的任务移至 `scheduled` 状态，从而不会显示为人工阻塞原因。 |
| `unblock <id>` | 将被阻塞或处于调度状态的任务恢复为待处理状态（如果仍有未解决的依赖关系，则保持为 `todo` 状态）。 |
| `archive <id>` | 隐藏该任务，不显示在默认列表中。系统还会自动清理与已归档任务相关的临时工作空间。 |
| `tail <id>` | 跟踪任务的事件流。 |
| `dispatch` | 对当前活动看板执行一次调度器处理。支持参数：`--dry-run`、`--max N`、`--failure-limit N`、`--json`。 |
| `context <id>` | 输出工作进程所能看到的完整任务上下文（包括标题、内容、父任务结果及评论）。 |
| `specify <id>` / `specify --all` | 通过辅助 LLM 将分类列中的任务细化为具体的任务描述（包含目标、执行方案及验收标准），并将其状态提升为 `todo`。支持参数：`--tenant`（当使用 `--all` 时仅限某个租户）、`--author`、`--json`。可在 `config.yaml` 的 `auxiliary.triage_specifier` 中配置对应模型。 |
| `decompose <id>` / `decompose --all` | 将分类列中的任务拆解为多个子任务，根据任务描述将这些子任务分配给相应的专业型配置文件处理。如果 LLM 判断该任务无需拆分，则会退化为使用 `specify` 方式直接提升任务状态。支持参数与 `specify` 相同。可在 `config.yaml` 的 `auxiliary.kanban_decomposer` 中配置拆解模型；`kanban.orchestrator_profile` 仅用于控制拆分后的根任务或编排任务的负责人。当设置 `kanban.auto_decompose: true`（默认值）时，该功能会在每次调度器循环中自动执行。详情请参阅 [自动编排与手动编排](/user-guide/features/kanban#auto-vs-manual-orchestration)。 |
| `gc` | 清理已归档任务对应的临时工作空间。 |

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

看板决议顺序（优先级从高到低）为：`--board <slug>` 参数 → `HERMES_KANBAN_BOARD` 环境变量 → `~/.hermes/kanban/current` 文件 → 默认值。

所有操作均可在网关中以斜杠命令的形式执行（如 `/kanban …`），支持的参数完全一致——包括 `boards` 子命令以及 `--board` 参数。

有关完整设计细节，包括与 Cline Kanban / Paperclip / NanoClaw / Gemini Enterprise 的对比、八种协作模式、四种用户场景以及并发正确性证明，可查阅仓库中的 `docs/hermes-kanban-v1-spec.pdf` 文件或 [看板用户指南](/user-guide/features/kanban)。

## `hermes project`

```bash
hermes project <create|list|show|add-folder|remove-folder|rename|set-primary|use|archive|restore|bind-board>
```

项目是由用户命名的工作空间，可涵盖多个文件夹或代码仓库。它们是桌面会话分组的基准，而当与看板绑定后，还能为任务提供规范的工作树结构与分支命名规则。项目状态会针对不同用户配置独立保存。

| 子命令 | 描述 |
|----------|------|
| `create` | 创建新项目。 |
| `list`（别名 `ls`） | 列出所有项目。 |
| `show` | 显示项目的详细信息。 |
| `add-folder` | 向项目中添加文件夹或代码仓库。 |
| `remove-folder` | 从项目中移除文件夹。 |
| `rename` | 重命名项目。 |
| `set-primary` | 设置主文件夹。 |
| `use` | 设置当前活跃项目。 |
| `archive` | 将项目归档（可恢复）。 |
| `restore` | 恢复已归档的项目。 |
| `bind-board` | 将看板绑定到该项目。 |

## `hermes webhook`

```bash
hermes webhook <subscribe|list|remove|test>
```

用于管理基于事件驱动的智能体激活所需的动态 Webhook 订阅功能。首先需要在配置中启用 Webhook 功能——若未配置，则会输出相应的设置指引。

| 子命令 | 描述 |
|----------|------|
| `subscribe` / `add` | 创建一个 Webhook 路由，并返回可在您的服务端配置的 URL 和 HMAC 密钥。 |
| `list` / `ls` | 显示所有由智能体创建的订阅项。 |
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
| `--description` | 供人类阅读的描述文字。 |
| `--skills` | 运行代理时需加载的技能名称，以逗号分隔。 |
| `--deliver` | 消息发送目标：`log`（默认值）、`telegram`、`discord`、`slack`、`github_comment`。 |
| `--deliver-chat-id` | 跨平台发送时的目标聊天室/频道 ID。 |
| `--secret` | 自定义 HMAC 密钥。如未指定则自动生成。 |
| `--deliver-only` | 跳过代理处理，直接将处理后的 `--prompt` 内容作为原始消息发送。无需调用大型语言模型，发送速度可达亚秒级。此模式要求 `--deliver` 指定有效的目标（不能为 `log`）。 |
| `--script` | 来自 `~/.hermes/scripts/` 目录的过滤/转换脚本。Webhook 的请求数据会以 JSON 格式通过标准输入传递；标准输出中的 JSON 内容将替代原始请求数据，若标准输出为空、为 `[SILENT]` 格式或退出码非零，则忽略该 Webhook 请求。详情请参阅 [脚本过滤与转换](../user-guide/messaging/webhooks.md#script-filters-and-transforms)。 |

订阅信息会保存在 `~/.hermes/webhook_subscriptions.json` 文件中，Webhook 适配器可无需重启网关即可实现热加载。

## `hermes doctor`

```bash
hermes doctor [--fix]
```

| 选项 | 描述 |
|------|------|
| `--fix` | 在可能的情况下尝试自动修复。 |

## `hermes dump`

```bash
hermes dump [--show-keys]
```

会输出关于您整个Hermes配置的简洁纯文本摘要。该格式专为在Discord、GitHub问题帖或Telegram中寻求帮助时复制粘贴而设计——不包含ANSI颜色，也无特殊格式，仅有原始数据。

| 选项 | 描述 |
|--------|--------|
| `--show-keys` | 显示经过脱敏处理的API密钥前缀（首尾各4个字符），而不仅仅是“已设置”/“未设置”。 |

### 包含的内容

| 类别 | 详情 |
|------|------|
| **标题信息** | Hermes版本、发布日期及git提交哈希值 |
| **环境信息** | 操作系统、Python版本、OpenAI SDK版本 |
| **身份信息** | 当前激活的配置文件名称、HERMES_HOME路径 |
| **模型信息** | 已配置的默认模型及提供方 |
| **终端信息** | 后端类型（本地、Docker、SSH等） |
| **API密钥信息** | 所有22个提供方/工具API密钥的存在状态检查结果 |
| **功能信息** | 已启用的工具集、MCP服务器数量、内存提供方情况 |
| **服务信息** | 网关状态、已配置的消息平台 |
| **工作负载信息** | Cron作业数量、已安装的技能数量 |
| **配置覆盖信息** | 任何与默认值不同的配置值 |

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

将调试报告（系统信息+近期日志）上传至粘贴服务后，即可获取一个可分享的链接。此功能非常适合快速提交支持请求——报告中包含了辅助人员诊断问题所需的所有信息。

| 选项 | 描述 |
|------|------|
| `--lines <N>` | 每个日志文件需包含的行数（默认：200）。 |
| `--expire <days>` | 粘贴内容的有效期，以天为单位（默认：7）。 |
| `--nous` | 上传至Nous内部的诊断存储系统，而非公共粘贴服务。当Nous支持团队要求获取私有诊断数据包时，请使用此选项。 |
| `--local` | 在本地打印报告，而非上传。 |
| `--no-redact` | 禁用上传时的敏感信息遮蔽功能。默认情况下，上传内容会进行遮蔽处理。 |

该报告包含系统信息（操作系统、Python版本、Hermes版本），以及近期来自代理、网关、GUI/控制台和桌面端的日志（每个文件大小上限为512 KB），还会显示经过遮蔽处理的API密钥状态。默认情况下，上传内容会进行遮蔽处理，以避免包含敏感信息。

默认情况下，系统会按顺序尝试使用公共粘贴服务：paste.rs、dpaste.com。而使用`--nous`选项时，会将相同的调试数据包上传至Nous私有的诊断存储系统中；此时返回的查看链接仅供Nous团队使用，并且在14天后会自动删除。

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

将您的 Hermes 配置、技能、会话及数据打包为 ZIP 压缩文件。此备份不会包含 hermes-agent 代码库本身。

| 选项 | 描述 |
|------|------|
| `-o`, `--output <路径>` | ZIP 文件的输出路径（默认值：`~/hermes-backup-<时间戳>.zip`）。 |
| `-q`, `--quick` | 快速快照：仅备份关键状态文件（config.yaml、state.db、.env、auth、cron 任务）。速度远快于完整备份。 |
| `-l`, `--label <名称>` | 为快照添加标签（仅与 `--quick` 选项一起使用）。 |

该备份采用 SQLite 的 `backup()` API 进行安全复制，因此即使在 Hermes 正在运行时也能正常工作（支持 WAL 模式下的安全操作）。

**ZIP 文件中不包含的内容：**

- `*.db-wal`、`*.db-shm`、`*.db-journal` — SQLite 的 WAL/共享内存/日志辅助文件。`*.db` 文件已通过 `sqlite3.backup()` 生成了完整快照；若同时传输这些实时辅助文件，恢复时可能会导致状态不完整。
- `checkpoints/` — 每个会话的轨迹缓存。这些缓存以哈希值标识，并且会随会话重新生成；无论如何也无法干净地移植到其他安装环境中。
- `hermes-agent` 代码本身（这是用户数据备份，而非代码库快照）。

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

您可以查看并管理位于 `~/.hermes/checkpoints/` 的影子 Git 存储空间——该空间是会话内 `/rollback` 命令背后的存储层。随时均可运行此命令，且无需 Agent 正在运行。

| 子命令 | 描述 |
|----------|------|
| `status`（默认） | 显示总大小、项目数量以及各项目的详细使用情况。直接输入 `hermes checkpoints` 也可达到相同效果。 |
| `list` | `status` 的别名。 |
| `prune` | 强制执行清理操作——删除孤立且过时的项目，对存储空间进行垃圾回收，并确保其大小不超过限制。此命令会忽略 24 小时的重复执行标记。 |
| `clear` | 删除整个检查点存储库。该操作不可撤销；除非使用 `-f` 参数，否则系统会要求用户确认。 |
| `clear-legacy` | 仅删除由 v1 版本向 v2 版本升级时生成的 `legacy-<timestamp>/` 归档文件。 |

### 选项

| 选项 | 子命令 | 描述 |
|------|----------|------|
| `--limit N` | `status`, `list` | 要列出的最大项目数量（默认为 20）。 |
| `--retention-days N` | `prune` | 删除那些 `last_touch` 时间早于 N 天的项目（默认为 7 天）。 |
| `--max-size-mb N` | `prune` | 在完成孤立/过时项目清理后，继续删除每个项目中最旧的提交记录，直至存储空间总大小不超过 N MB（默认为 500 MB）。 |
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

有关完整的架构说明及会话内可用命令的详细内容，请参阅[检查点与/回滚](../user-guide/checkpoints-and-rollback.md)。

## `hermes import`

```bash
hermes import <zipfile> [options]
```

将之前创建的 Hermes 备份恢复到您的 Hermes 主目录中。归档文件中的所有内容都会覆盖主目录中已有的文件；而 `--force` 选项仅用于跳过在目标目录已存在 Hermes 安装时的确认提示。

| 选项 | 描述 |
|------|------|
| `-f`, `--force` | 跳过关于目标目录已存在安装的确认提示。 |

:::warning
在导入之前请先停止网关，以避免与正在运行的进程发生冲突。
:::

### 示例
```bash
hermes import ~/hermes-backup-20260423.zip           # Prompts before overwriting existing config
hermes import ~/hermes-backup-20260423.zip --force   # Overwrite without prompting
```

## `hermes logs` 命令

```bash
hermes logs [log_name] [options]
```

查看、跟踪并筛选 Hermes 日志文件。所有日志均存储在 `~/.hermes/logs/` 目录中（非默认配置文件的日志则存储在 `<profile>/logs/` 目录中）。

### 日志文件

| 名称 | 文件路径 | 记录内容 |
|------|----------|----------|
| `agent`（默认） | `agent.log` | 所有的代理程序活动——API 调用、工具调度、会话生命周期信息（INFO 级及以上） |
| `errors` | `errors.log` | 仅记录警告和错误信息——即从 `agent.log` 中筛选出的部分内容 |
| `gateway` | `gateway.log` | 消息网关的活动记录——平台连接、消息调度、Webhook 事件 |
| `gui` | `gui.log` | 控制面板/TUI 网关/PTY 桥接/WebSocket 事件 |
| `desktop` | `desktop.log` | Electron 桌面应用程序的相关日志——启动信息、后台进程输出以及最近的 Python 异常堆栈 |

### 参数选项

| 参数 | 说明 |
|------|------|
| `log_name` | 指定要查看的日志类型：`agent`（默认）、`errors`、`gateway`；或输入 `list` 以查看包含文件大小信息的所有可用日志文件。 |
| `-n`, `--lines <N>` | 显示的行数（默认为 50 行）。 |
| `-f`, `--follow` | 实时跟踪日志内容，功能类似 `tail -f`。按 Ctrl+C 可停止跟踪。 |
| `--level <LEVEL>` | 指定要显示的最低日志级别：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`。 |
| `--session <ID>` | 筛选包含特定会话 ID 子串的日志行。 |
| `--since <TIME>` | 显示指定时间范围内的日志行，例如 `30m`、`1h`、`2d` 等。支持 `s`（秒）、`m`（分钟）、`h`（小时）、`d`（天）等时间单位。 |
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

多个过滤规则可以组合使用。当有多个过滤规则生效时，只有同时满足**所有**规则的日志行才会被显示出来：

```bash
# WARNING+ lines from the last 2 hours containing session "tg-12345"
hermes logs --level WARNING --since 2h --session tg-12345
```

当启用 `--since` 参数时，即使行中不存在可解析的时间戳，该行也会被包含在内（这些行可能是多行日志条目的延续部分）；而当启用 `--level` 参数时，即使行中无法识别日志级别，该行同样会被纳入统计。

### 日志轮转

Hermes 使用 Python 的 `RotatingFileHandler` 功能来实现自动日志轮转——系统中会生成诸如 `agent.log.1`、`agent.log.2` 等格式的旧日志文件。通过 `hermes logs list` 子命令即可查看所有日志文件，包括已轮转过的那些。

## `hermes prompt-size`

```bash
hermes prompt-size [--platform <name>] [--json]
```

该功能会显示新会话的固定提示词预算，即在任何对话内容之前、每次API调用时都会发送的提示词内容。当下游适配器或代理的提示词预算低于模型的上下文窗口大小时，或者您想了解哪些部分（技能索引、内存、用户档案）占据了最大比例时，此功能非常有用。

它会生成与智能体所使用的完全相同的系统提示词，然后对其进行分析拆解：

- **系统提示词总量**——完整的组合提示词（包括身份信息、使用指南、技能索引、上下文文件、内存数据、用户档案以及时间戳）。
- **技能索引**——即`<available_skills>`部分。当安装了众多技能时，这部分通常会是占比最大的单一模块。
- **内存数据**与**用户档案**——对应您的`MEMORY.md`/`USER.md`文件中的内容快照。
- **提示词层级**——稳定型/上下文型/易变型，反映了Hermes为优化缓存性能而对提示词进行的层次划分。
- **工具结构定义**——所有已启用工具的JSON格式描述（即每次调用时固定传输内容的另一半）。

该功能完全在离线状态下运行，无需进行任何API调用，也无需配置任何凭证信息。

```bash
# Human-readable breakdown for the CLI platform (default)
hermes prompt-size

# Simulate a messaging platform's prompt (different platform hint)
hermes prompt-size --platform telegram

# Machine-readable output for scripts
hermes prompt-size --json
```

:::提示
技能指数与工具结构体规模会随着您启用的技能和工具数量而变化。若希望缩小提示词长度，可禁用未使用的工具集（`hermes tools`），或卸载不需要的技能（`hermes skills`）。当前目录下的上下文文件（如 AGENTS.md、.cursorrules）也会计入总规模中。
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
| `set <key> <value>` | 设置配置值。 |
| `path` | 输出配置文件的路径。 |
| `env-path` | 输出 `.env` 文件的路径。 |
| `check` | 检查是否存在缺失或过时的配置。 |
| `migrate` | 以交互方式添加新引入的选项。 |

## `hermes pairing`

```bash
hermes pairing <list|approve|revoke|clear-pending>
```

| 子命令 | 描述 |
|----------|------|
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
| `inspect` | 在不安装的情况下预览技能。 |
| `list` | 列出已安装的技能。 |
| `check` | 检查已安装的 Hub 技能是否有上游更新。 |
| `update` | 当有可用上游更新时，重新安装包含这些更新的 Hub 技能。 |
| `audit` | 重新扫描已安装的 Hub 技能。 |
| `uninstall` | 卸载由 Hub 安装的技能。 |
| `reset` | 通过清除其清单条目，移除被标记为 `user_modified` 的捆绑技能。若使用 `--restore` 参数，还会将用户自定义版本替换为捆绑版本。 |
| `opt-out` | 阻止捆绑技能被植入活跃配置文件中。该命令会写入 `.no-bundled-skills` 标记，从而使安装工具、`hermes update` 以及任何同步操作跳过捆绑技能的植入过程。默认情况下是安全的——不会修改磁盘上的任何内容。若使用 `--remove` 参数，还会删除那些**未被修改**的已存在捆绑技能（用户编辑过的、由 Hub 安装的以及手动编写的技能永远不会被删除；系统会先进行预览并确认，输入 `--yes` 才会跳过此步骤）。 |
| `opt-in` | 通过移除 `.no-bundled-skills` 标记来撤销 `opt-out` 设置，从而使捆绑技能在下次执行 `hermes update` 时再次被植入。若使用 `--sync` 参数，则会立即重新植入。 |
| `publish` | 将某个技能发布到注册表中。 |
| `snapshot` | 导出/导入技能配置。 |
| `tap` | 管理自定义技能源。 |
| `config` | 按平台交互式地启用/禁用技能功能。 |

常见示例：

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
- `--source browse-sh` 会从 [browse.sh](https://browse.sh) 的目录中查找 200 多种针对特定网站的浏览器自动化技能，其标识符格式为 `browse-sh/airbnb.com/search-listings-ddgioa`。  
- 如果传递 `http(s)://…/*.md` 格式的 URL，系统会将 `SKILL.md` 文件以及其中明确引用的文件安装到 `references/`、`templates/`、`scripts/`、`assets/` 和 `examples/` 目录下。若前端元数据中未指定 `name:` 且该 URL 的标识符无效，交互式终端会提示用户输入名称；而非交互式使用场景（如 TUI 内的 `/skills install` 命令或网关平台）则需使用 `--name <x>` 参数指定名称。  

## `hermes bundles`

```bash
hermes bundles <subcommand>
```

技能包将多个技能整合在同一个 `/<bundle-name>` 格式的命令下。调用该技能包时，所有关联的技能都会被合并到一条统一的用户消息中。存储路径为：`~/.hermes/skill-bundles/<slug>.yaml`。有关 YAML 结构及相关行为说明，请参阅 [技能包](../user-guide/features/skills.md#skill-bundles)。

子命令：

| 子命令 | 描述 |
|----------|------|
| `list` | 列出已安装的技能包（未指定子命令时默认执行此操作） |
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

Curator是一个辅助模型后台任务，它会定期检查由Agent生成的技能，删除过时的技能，合并重复的技能，并将不再使用的技能归档。已打包或通过Hub安装的技能则不会被触碰。归档的技能可以恢复，绝不会被自动删除。

| 子命令 | 描述 |
|----------|------|
| `status` | 显示Curator的状态及技能统计信息 |
| `run` | 立即触发Curator的检查流程（会阻塞直到LLM处理完成） |
| `run --background` | 在后台线程中启动LLM处理，并立即返回 |
| `run --dry-run` | 仅进行预览——生成检查报告但不做任何修改 |
| `backup` | 手动创建`~/.hermes/skills/`目录的tar.gz备份文件（Curator在每次实际执行前也会自动创建备份） |
| `rollback` | 从备份文件中恢复`~/.hermes/skills/`目录的内容（默认恢复最新的备份） |
| `rollback --list` | 列出所有可用的备份文件 |
| `rollback --id <ts>` | 根据编号恢复特定的备份文件 |
| `rollback -y` | 跳过确认提示 |
| `pause` | 暂停Curator的运行，直到手动恢复 |
| `resume` | 恢复已暂停的Curator运行 |
| `pin <skill>` | 固定某个技能，使其不会被Curator自动移除 |
| `unpin <skill>` | 取消固定某个技能 |
| `restore <skill>` | 恢复已被归档的技能 |
| `archive <skill>` | 手动将某个技能归档 |
| `prune` | 手动删除Curator通常会处理的过时技能 |
| `list-archived` | 列出所有已归档的技能（可通过`restore`命令恢复） |

在首次安装后，第一次 scheduled的检查任务会延迟一个完整的`interval_hours`时间（默认为7天）——在执行`hermes update`后的第一个计时周期内，Gateway不会立即进行技能检查。建议在此之前使用`hermes curator run --dry-run`来预览功能。

有关其行为及配置详情，请参阅[Curator](../user-guide/features/curator.md)文档。

## `hermes moa`

用于配置命名化的Mixture of Agents预设。这些预设会作为可选模型显示在每个模型选择器中的“Mixture of Agents”提供者下；使用`/moa <prompt>`命令则可通过默认预设处理对应提示词。

```bash
hermes moa list
hermes moa configure [name]
hermes moa delete <name>
```

`hermes moa configure` 会复用 Hermes 的提供者→模型选择器，用于处理各个参考模型以及聚合器。预设仅属于执行模式配置，并非核心模型或提供者。

## `hermes fallback`

```bash
hermes fallback <subcommand>
```

管理备用提供者链。当主模型因速率限制、过载或连接错误而失效时，系统会按顺序尝试这些备用提供者。

| 子命令 | 描述 |
|----------|------|
| `list`（别名：`ls`） | 显示当前的备用提供者链（未指定子命令时的默认操作） |
| `add` | 选择某个提供者及模型（与 `hermes model` 的选择界面相同），并将其添加到链中 |
| `remove`（别名：`rm`） | 选择要从链中删除的条目 |
| `clear` | 删除所有备用提供者条目 |

详情请参阅 [备用提供者](../user-guide/features/fallback-providers.md)。

## `hermes hooks`

```bash
hermes hooks <subcommand>
```

检查 `~/.hermes/config.yaml` 中声明的 shell 脚本钩子，使用合成测试载荷对它们进行测试，并在 `~/.hermes/shell-hooks-allowlist.json` 中管理首次使用授权白名单。

| 子命令 | 描述 |
|----------|------|
| `list`（别名：`ls`） | 列出已配置的钩子，包括匹配规则、超时设置以及授权状态 |
| `test <event>` | 对每个匹配 `<event>` 的钩子使用合成测试载荷进行触发测试 |
| `revoke`（别名：`remove`、`rm`） | 删除某条命令的白名单条目（下次重启后生效） |
| `doctor` | 检查每个已配置的钩子：执行权限、白名单设置、修改时间偏差、JSON 格式有效性以及合成测试的执行时间 |

有关事件签名和载荷格式的详细信息，请参阅 [Hooks](../user-guide/features/hooks.md)。

## `hermes memory`

```bash
hermes memory <subcommand>
```

设置并管理外部内存提供程序插件。目前支持的提供程序包括：honcho、openviking、mem0、hindsight、holographic、retaindb、byterover、supermemory。同一时间仅能有一个外部提供程序处于激活状态，而内置内存（MEMORY.md/USER.md）则始终处于激活状态。

子命令：

| 子命令 | 描述 |
|----------|------|
| `setup` | 交互式选择并配置提供程序。 |
| `status` | 显示当前内存提供程序的配置信息。 |
| `off` | 禁用外部提供程序（仅适用于内置内存）。 |

:::info 提供程序专属子命令
当某个外部内存提供程序处于激活状态时，它可能会注册自己的顶级 `hermes <provider>` 命令，以便进行针对该提供程序的专用管理操作（例如在 Honcho 处于激活状态时使用 `hermes honcho`）。未激活的提供程序则不会显示其子命令。运行 `hermes --help` 可查看当前已配置的提供程序。
:::

## `hermes acp`

```bash
hermes acp
```

以 ACP（Agent Client Protocol）标准输入输出服务器模式启动 Hermes，从而实现与编辑器的集成。

相关入口点：

```bash
hermes-acp
python -m acp_adapter
```

请先安装支持组件：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e '.[acp]'
```

请参阅 [ACP 编辑器集成](../user-guide/features/acp.md) 以及 [ACP 内部机制](../developer-guide/acp-internals.md)。

## `hermes mcp`

```bash
hermes mcp <subcommand>
```

管理 MCP（模型上下文协议）服务器配置，并将 Hermes 作为 MCP 服务器运行。

| 子命令 | 描述 |
|----------|------|
| *(无)* 或 `picker` | 交互式目录选择器——浏览经 Nous 批准的 MCP，并进行安装/启用/禁用操作。 |
| `catalog` | 列出经 Nous 批准的 MCP（以纯文本形式呈现，可脚本化处理）。 |
| `install <name>` | 安装某个目录条目（例如：`hermes mcp install n8n`）。 |
| `serve [-v\|--verbose]` | 将 Hermes 作为 MCP 服务器运行——向其他智能体公开对话内容。 |
| `add <name> [--url URL] [--command CMD] [--auth oauth\|header] [--args ...]` | 添加支持自动工具发现的自定义 MCP 服务器。`--args` 用于将剩余的命令行参数传递给目标命令，因此应将其放在最后。 |
| `remove <name>`（别名：`rm`） | 从配置中移除某个 MCP 服务器。 |
| `list`（别名：`ls`） | 列出已配置的 MCP 服务器。 |
| `test <name>` | 测试与某个 MCP 服务器的连接是否正常。 |
| `configure <name>`（别名：`config`） | 切换某服务器的工具选择模式。 |
| `login <name>` | 强制对基于 OAuth 的 MCP 服务器重新进行身份验证。 |

更多详情请参阅 [MCP 配置参考](./mcp-config-reference.md)、[在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md) 以及 [MCP 服务器模式](../user-guide/features/mcp.md#running-hermes-as-an-mcp-server)。

## `hermes plugins`

```bash
hermes plugins [subcommand]
```

统一的插件管理功能——所有通用插件、内存提供器以及上下文引擎均集中于此。运行 `hermes plugins` 且不指定子命令时，会打开一个包含两个区域的综合交互界面：

- **通用插件**——通过多选复选框来启用或禁用已安装的插件；
- **提供器插件**——针对内存提供器和上下文引擎提供单选配置。在某一类别上按下 ENTER 键即可打开单选下拉菜单。

| 子命令 | 描述 |
|----------|------|
| *(无)* | 综合交互式用户界面——包含通用插件开关控制及提供器插件配置功能。 |
| `install <identifier> [--force]` | 从 Git URL 或 `owner/repo` 地址安装插件。 |
| `update <name>` | 获取已安装插件的最新更新。 |
| `remove <name>`（别名：`rm`, `uninstall`） | 卸载已安装的插件。 |
| `enable <name>` | 启用被禁用的插件。 |
| `disable <name>` | 禁用插件而不将其删除。 |
| `list`（别名：`ls`） | 列出所有已安装插件的启用/禁用状态。 |

提供器插件的选择结果会保存在 `config.yaml` 文件中：
- `memory.provider`——当前使用的内存提供器（留空则表示仅使用内置提供器）；
- `context.engine`——当前使用的上下文引擎（`"compressor"` 表示默认内置引擎）。

通用插件的禁用列表则存储在 `config.yaml` 的 `plugins.disabled` 字段中。

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
| `status` | 输出 `cua-driver` 是否存在于 `$PATH` 中以及当前安装的版本号。 |

`hermes computer-use install` 是安装 `computer_use` 工具集所使用的 [cua-driver](https://github.com/trycua/cua) 二进制文件的稳定入口命令。它使用的正是你在首次启用“计算机使用”功能时 `hermes tools` 所调用的上游安装程序，因此即便工具集开关未触发安装流程（例如在用户重新登录后），使用该命令重新安装也是安全的。

如果 cua-driver 已存在于 PATH 环境变量中，`hermes update` 会在更新过程结束时自动重新运行上游安装程序，因此大多数用户无需手动调用 `--upgrade` 参数。当上游版本发布了你急需的修复补丁，而你不想等待下一次 Hermes 更新时，可使用此命令。

## `hermes pets`

```bash
hermes pets <list|install|select|show|off|scale|remove|doctor>
```

[Petdex](https://github.com/crafter-station/petdex) 是一个面向编程智能体的动画精灵宠物公共展示库。安装任意一个宠物后，Hermes 就能在 CLI、TUI 以及桌面应用中展示该宠物对智能体操作的响应。

| 子命令 | 描述 |
|----------|------|
| `list` | 浏览 Petdex 展示库中的内容。 |
| `install` | 从展示库中安装一个宠物。 |
| `select` | 设置当前活动的宠物（会修改 `display.pet.*` 的值）。 |
| `show` | 在终端中播放当前活动宠物的动画。 |
| `off` | 禁用宠物显示功能。 |
| `scale` | 调整所有位置上宠物图像的尺寸（通过 `display.pet.scale` 实现）。 |
| `remove` | 删除已安装的宠物。 |
| `doctor` | 检查宠物设置及终端的图形渲染支持情况。 |

您还可以使用 `/hatch` 命令，根据文本描述生成全新的宠物。详情请参阅 [Pets](../user-guide/features/pets.md) 文档。

## `hermes sessions`

```bash
hermes sessions <subcommand>
```

子命令：

| 子命令 | 描述 |
|----------|------|
| `list` | 列出最近的会话。 |
| `browse` | 支持搜索和继续操作的交互式会话选择器。 |
| `export <output> [--session-id ID]` | 将会话导出为 JSONL 格式。 |
| `delete <session-id>` | 删除某个会话。 |
| `prune` | 根据以下条件删除会话：时间范围 `--older-than`/`--newer-than`/`--before`/`--after`（支持 `5h`/`2d` 等时长表示、纯数字天数或 ISO 时间戳）；属性 `--source`、`--title`、`--model`、`--provider`、`--branch`、`--end-reason`、`--user`、`--chat-id`、`--chat-type`、`--cwd`；数值范围 `--min/--max-messages`、`--min/--max-tokens`、`--min/--max-cost`、`--min/--max-tool-calls`；此外还包括 `--include-archived`、`--dry-run`、`--yes` 参数。默认条件为超过 90 天的会话。 |
| `archive` | 对符合与 `prune` 相同筛选条件的会话进行批量归档（仅隐藏，不会删除）。至少需要一个筛选条件。 |
| `stats` | 显示会话存储的统计信息。 |
| `rename <session-id> <title>` | 设置或更改会话标题。 |

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
| `--preset <name>` | 指定迁移预设：`full`（导入所有兼容设置）或 `user-data`（仅导入用户数据，排除基础设施相关配置）。两种预设均不会导入密钥——如需导入密钥，请显式使用 `--migrate-secrets` 选项。 |
| `--overwrite` | 在遇到冲突时覆盖现有的 Hermes 文件（默认情况下，若存在冲突会拒绝应用迁移计划）。 |
| `--migrate-secrets` | 在迁移过程中包含 API 密钥。即使使用 `--preset full` 预设，也必须此选项。 |
| `--no-backup` | 跳过对 `~/.hermes/` 的迁移前压缩备份（默认情况下，在应用迁移前会先在 `~/.hermes/backups/pre-migration-*.zip` 中生成一个恢复点档案，可通过 `hermes import` 命令恢复）。 |
| `--source <path>` | 自定义的 OpenClaw 目录路径（默认为 `~/.openclaw`）。 |
| `--workspace-target <path>` | 工作空间配置文件（AGENTS.md）的目标目录。 |
| `--skill-conflict <mode>` | 处理技能名称冲突的方式：`skip`（默认值）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过确认提示。 |

### 有哪些内容会被迁移？

此次迁移涵盖角色设定、记忆功能、技能、模型提供方、消息平台、智能体行为、会话策略、MCP 服务器、文本转语音等功能，共涉及 30 多个类别。相关配置要么**直接导入**到 Hermes 的对应组件中，要么被**归档**以便人工审核。

**直接导入的内容包括：** SOUL.md、MEMORY.md、USER.md、AGENTS.md、各类技能配置（来自 4 个源目录）、默认模型、自定义模型提供方、MCP 服务器、消息平台的相关令牌及允许列表（Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost）、智能体默认参数（推理耗时、压缩设置、人工响应延迟、时区、沙箱模式）、会话重置规则、审批规则、文本转语音配置、浏览器设置、工具设置、命令执行超时时间、命令允许列表、网关配置，以及来自 3 个来源的 API 密钥。

**被归档以供人工审核的内容包括：** 定时任务脚本、插件、钩子/Webhook 配置、记忆功能后端（QMD）、技能注册表配置、用户界面/身份相关设置、日志记录功能、多智能体配置、频道绑定设置、IDENTITY.md、TOOLS.md、HEARTBEAT.md、BOOTSTRAP.md 等文件。

**API 密钥解析**会按优先级依次检查三个来源：配置文件中的值 → `~/.openclaw/.env` 文件 → `auth-profiles.json` 文件。所有令牌字段都支持普通字符串、环境变量模板（`${VAR}`）以及 SecretRef 对象。

如需查看完整的配置键映射表、SecretRef 处理细节以及迁移后的检查清单，请参阅 **[完整迁移指南](../guides/migrate-from-openclaw.md)**。

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

## `hermes serve` 命令

```bash
hermes serve [options]
```

启动 Hermes **后端服务器**——即 [桌面应用](/user-guide/desktop) 与远程客户端所连接的 JSON-RPC/WebSocket 网关。该服务器与 `hermes dashboard` 运行的服务器相同，但为**无界面模式**：不会打开任何浏览器界面。桌面应用会自行启动其自身的 `hermes serve` 后端；若希望在远程主机上使用无界面后端，则可直接使用此命令。它支持与下方 `hermes dashboard` 相同的 `--host` / `--port` / `--insecure` / `--skip-build` / `--stop` / `--status` 参数（非回环绑定会启用相同的认证机制）。该命令需要安装 `[web]` 插件；而在 POSIX 系统主机上，内置的聊天套接字还需额外配置 `[pty]`。

## `hermes dashboard`

```bash
hermes dashboard [options]
```

启动 Web 控制面板——这是一个基于浏览器的用户界面，用于管理配置、API 密钥以及监控会话。（对于没有浏览器界面的无头后端环境，例如桌面应用程序启动的后端，可使用上文提到的 [`hermes serve`](#hermes-serve) 命令。）使用该功能需要执行 `cd ~/.hermes/hermes-agent && uv pip install -e ".[web]"`（基于 FastAPI 和 Uvicorn）。内置的浏览器聊天标签页始终可用，但还需额外安装 `pty` 组件（需执行 `cd ~/.hermes/hermes-agent && uv pip install -e ".[web,pty]"》），并且要求操作系统具备 POSIX PTY 环境，如 Linux、macOS 或 WSL2。详细文档请参阅 [Web 控制面板](/user-guide/features/web-dashboard)。

| 选项 | 默认值 | 描述 |
|------|--------|------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--insecure` | off | **已废弃/无作用。** 旧版本中用于在非回环绑定地址上绕过身份验证。自 2026 年 6 月的安全加固措施实施后，公开绑定地址*必须*使用身份验证提供方（密码或 OAuth）进行保护。如需保持本地运行，可绑定 `127.0.0.1` 并通过隧道传输。 |
| `--skip-build` | off | 跳过 Web 用户界面的构建步骤，直接提供现有的 `dist` 文件。适用于无法使用 npm 的非交互式环境（如 Windows 计划任务、CI 环境）。建议先执行 `cd web && npm run build` 进行预构建。 |
| `--isolated` | off | 当从命名配置文件（如“工作节点控制面板”）启动时，为每个配置文件单独运行服务器，而非路由到全局控制面板。 |
| `--stop` | — | 停止运行 `hermes dashboard` 相关进程并退出。 |
| `--status` | — | 列出正在运行的 `hermes dashboard` 进程后退出。 |

### `hermes dashboard register`

将该安装项注册为您 Nous Portal 账户下的自托管控制面板。该命令会创建一个 OAuth 客户端，将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 写入 `~/.hermes/.env` 文件，并说明如何接入登录验证流程。使用时需已登录账户（需先执行 `hermes setup`）。

| 选项 | 描述 |
|------|------|
| `--name` | 控制面板的可读标签名（默认为自动生成）。 |
| `--redirect-uri` | 公开的 HTTPS OAuth 重定向地址（例如 `https://hermes.example.com/auth/callback`）。仅在本地使用时可省略该参数。 |
| `--portal-url` | 覆盖用于注册的 Nous Portal 基础网址（默认为当前登录的门户地址）。也可通过 `HERMES_DASHBOARD_PORTAL_URL` 参数进行设置。 |

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

管理配置文件——支持多个独立的 Hermes 实例，每个实例拥有独立的配置、会话、技能及主目录。

| 子命令 | 描述 |
|----------|------|
| `list` | 列出所有配置文件。 |
| `use <name>` | 设置默认的固定配置文件。 |
| `create <name> [--clone] [--clone-all] [--clone-from <source>] [--no-alias]` | 创建新配置文件。<br>`--clone` 会从当前激活的配置文件复制配置、`.env` 文件、`SOUL.md` 以及技能。<br>`--clone-all` 会复制所有状态数据。<br>`--clone-from` 指定源配置文件，若未搭配 `--clone-all` 使用，则仅复制配置。 |
| `delete <name> [-y]` | 删除配置文件。 |
| `show <name>` | 显示配置文件详情（如主目录、配置内容等）。 |
| `alias <name> [--remove] [--name NAME]` | 管理用于快速访问配置文件的封装脚本。 |
| `rename <old> <new>` | 重命名配置文件。 |
| `export <name> [-o FILE]` | 将配置文件导出为 `.tar.gz` 压缩包（用于本地备份）。 |
| `import <archive> [--name NAME]` | 从 `.tar.gz` 压缩包中导入配置文件（用于本地恢复）。 |
| `install <source> [--name N] [--alias] [--force] [-y]` | 从 git 地址或本地目录安装配置文件版本。 |
| `update <name> [--force-config] [-y]` | 重新拉取配置文件版本；保留用户数据（如记忆内容、会话信息、认证信息）。 |
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
hermes update [--gateway] [--check] [--no-backup] [--backup] [--yes]
```

该命令会获取最新的 `hermes-agent` 代码，并在管理的虚拟环境中重新安装依赖项，随后再次运行安装后的钩子程序（如 MCP 服务器、技能同步及补全功能安装）。即便在已实际安装的环境中运行也安全。若想在不进行实际安装的情况下查看当前版本是否落后于 `origin/main`，可使用 `--check` 参数。

`hermes update` 会获取配置好的更新分支（默认为 `main`）。如果当前检出代码位于其他分支，Hermes 可能会在拉取之前先切换到该更新分支。若希望将某些分支上的修改排除在自动更新流程之外，建议在更新前先提交这些修改。

| 参数 | 描述 |
|------|------|
| `--gateway` | 用于消息传递 `/update` 命令的内部模式。该模式通过基于文件的进程间通信方式来传输提示信息及进度状态，而非从终端标准输入读取数据。此参数并非用于重启网关的标志。 |
| `--check` | 在不进行拉取、安装依赖或重启任何服务的情况下，检查是否有可用更新。 |
| `--no-backup` | 即使在 `config.yaml` 中启用了 `updates.pre_update_backup` 功能，也跳过本次运行前的预更新备份操作。 |
| `--backup` | 在拉取代码之前，创建一个带有标签的 `HERMES_HOME` 预更新快照（包含配置、认证信息、会话数据、技能及配对数据等）。默认值为关闭——之前的“始终备份”模式会导致大型项目每次更新时都需要花费数分钟时间。如需永久启用该功能，可在 `config.yaml` 中将 `updates.pre_update_backup` 设置为 `true`。 |
| `--yes`, `-y` | 对于配置迁移、缓存恢复等交互式提示，直接默认选择“是”。此时不会询问 API 密钥信息；如需单独处理 API 密钥相关操作，请运行 `hermes config migrate` 命令。 |

其他相关行为：

- **网关重启**：成功完成更新后，Hermes 会自动尝试重启所有正在运行的网关实例，以便它们能使用到最新代码。若仅需重启网关而不进行更新，可使用 `hermes gateway restart` 命令。
- **本地源代码变更**：对于通过 git 安装的项目，在切换分支或拉取代码之前，系统会自动将已修改但未暂存的文件以及未被跟踪的文件暂存起来（使用 `git stash push --include-untracked` 命令）。交互式终端更新会在恢复暂存内容前询问用户确认；非交互式更新则默认直接恢复暂存内容。仅在管理型安装环境中，且希望在拉取成功后丢弃所有本地修改时，才可将 `updates.non_interactive_local_changes` 设置为 `discard`。如果恢复暂存时出现冲突或拉取失败，暂存内容将保持原样，以便用户手动处理。
- **npm lockfile 变更清理**：在暂存代码或切换分支之前，Hermes 会尽力清理由 npm install/build 过程产生的已跟踪 `package-lock.json` 文件的差异内容。在运行 `hermes update` 命令之前，请先将有意修改的 lockfile 内容提交或手动暂存。
- **配对数据快照**：即使关闭了 `--backup` 参数，`hermes update` 也会在执行 `git pull` 之前，对 `~/.hermes/pairing/` 目录以及飞书评论规则生成轻量级的快照。如果拉取操作覆盖了您正在编辑的文件，可使用 `hermes backup restore --state pre-update` 命令将其恢复。
- **旧版 `hermes.service` 警告**：如果 Hermes 检测到系统上存在更名前的 `hermes.service` systemd 单元（而非当前的 `hermes-gateway.service`），它会一次性提示用户进行迁移操作，以避免出现循环问题。
- **退出码说明**：成功时返回 `0`；拉取、安装或安装后步骤出错时返回 `1`；工作目录发生意外变化导致无法执行 `git pull` 时返回 `2`。

## 维护命令

| 命令 | 描述 |
|------|------|
| `hermes version` | 显示版本信息。 |
| `hermes update` | 拉取最新更改并重新安装依赖项。 |
| `hermes postinstall` | 内部引导程序。在安装脚本完成 Hermes 的初始化之后（或执行 `hermes update` 之后），该命令会运行一次，用于安装 pip 无法提供的非 Python 类型依赖项，如 Node.js 运行时、无头浏览器、ripgrep、ffmpeg 等；如果相关配置文件尚未设置，还会触发 `hermes setup` 命令。该命令可重复安全运行，具有幂等性。 |
| `hermes uninstall [--full] [--gui] [--yes]` | 卸载 Hermes，可选择是否同时删除所有配置文件和数据。`--gui` 仅删除桌面端的聊天 GUI，保留代理程序本身；`--full` 会同时删除配置文件和数据；`--yes` 会跳过所有确认提示。 |

## 参见

- [Slash 命令参考](./slash-commands.md)
- [CLI 接口](../user-guide/cli.md)
- [会话管理](../user-guide/sessions.md)
- [技能系统](../user-guide/features/skills.md)
- [皮肤与主题](../user-guide/features/skins.md)
