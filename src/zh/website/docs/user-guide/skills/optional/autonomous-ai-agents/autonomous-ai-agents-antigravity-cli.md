---
title: "Antigravity Cli — Operate the Antigravity CLI (agy): plugins, auth, sandbox"
sidebar_label: "Antigravity Cli"
description: "Operate the Antigravity CLI (agy): plugins, auth, sandbox"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据该技能的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Antigravity CLI

操作 Antigravity CLI（agy）：插件、身份认证与沙箱环境。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/autonomous-ai-agents/antigravity-cli` 安装 |
| 路径 | `optional-skills/autonomous-ai-agents\antigravity-cli` |
| 版本 | `0.2.0` |
| 开发者 | Tony Simons (asimons81)、Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Coding-Agent`、`Antigravity`、`CLI`、`Auth`、`Plugins`、`Sandbox` |
| 相关技能 | [`grok`](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-grok)、[`codex`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-codex)、[`claude-code`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code)、[`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，智能体看到的指令即为内容。
:::

# Antigravity CLI（`agy`）

Antigravity CLI 的操作指南，该 CLI 的调用命令为 `agy`。所有 `agy` 命令均需通过 Hermes 的 `terminal` 工具来执行；可使用 `read_file` 命令查看其配置文件与日志。该技能属于参考型加流程指导类——它并不封装任何网络 API，因此 Hermes 本身无需进行任何身份验证。

## 适用场景

- 安装、更新或对 `agy` 可执行文件进行功能测试  
- 执行非交互式的 `agy --print` / `agy -p` 单次命令  
- 调试 Antigravity 的身份认证、沙箱环境、权限设置或插件状态  
- 查看 Antigravity 的配置项、快捷键设置、对话记录或日志文件  

## 思维模型

Antigravity 具有双层结构——需明确区分这两层，否则指导信息将会出错：

1. **Shell 包装命令** — 如 `agy help`、`agy install`、`agy plugin`、`agy update`、`agy changelog`。这类命令需通过 `terminal` 工具执行。  
2. **交互式会话中的斜杠命令** — 如 `/config`、 `/permissions`、 `/skills`、 `/agents` 等。这类命令仅存在于正在运行的 `agy` 图形用户界面会话中，而非 Shell 包装层。

`agy help` 显示的是 Shell 包装层的命令列表，而非会话中的斜杠命令。

## 先决条件

- PATH 环境变量中已包含 `agy` 可执行文件。可通过 `terminal` 工具进行验证：
  `command -v agy && agy --version`  
- 该技能无需任何环境变量或 API 密钥——Antigravity 通过操作系统密钥管理器或浏览器登录功能来实现自身身份认证（详见下文“身份认证”部分）。

## 执行方法

所有 `agy` 命令均需通过 `terminal` 工具来执行。示例如下：

```
terminal(command="agy --version")
terminal(command="agy help")
terminal(command="agy plugin list")
terminal(command="agy --print 'Summarize the repo in 3 bullets'", workdir="/path/to/project")
```

若需进行交互式的多轮文本用户界面对话，可像 `codex` / `claude-code` 技能那样，使用 `pty=true` 参数启动 `agy`（同时配合 `tmux` 用于内容捕获与监控）。而对于一次性功能测试或脚本化提问，则建议使用非交互模式的 `agy --print`。

若要查看 Antigravity 自身的文件，请通过下方“核心路径”中的地址使用 `read_file` 命令读取，切勿直接通过终端使用 `cat` 命令查看。

## 授权模式

`agy` 与 `codex` / `claude-code` 同属一类编程智能体后端，因此适用相同的授权机制。在需要将实际工作（如功能开发、缺陷修复、代码审查、专家意见征求）交由 Antigravity 处理时，而非仅进行简单测试时，应采用这些授权模式。

### 一次性模式（适用于脚本化提问及寻求专家意见）

```
terminal(command="agy -p 'Review this diff for bugs and security issues' --model 'Gemini 3.1 Pro (High)'", workdir="/path/to/repo", timeout=300)
```

`-p` 模式为非交互式：它会显示提示语后立即退出。可通过 `--model` 参数选择模型（运行 `agy models` 可查看具体的显示文本，例如 `'Gemini 3.1 Pro (High)'`、`'Claude Opus 4.6 (Thinking)'`）。若需添加额外的上下文路径，可使用可重复使用的 `--add-dir` 参数。

### 长时间/有时间限制的运行任务（测试、构建、多文件修改）

可与 `codex` 技能相同，将其置于后台运行并在任务完成时收到通知：

```
terminal(command="agy -p 'Implement the change described in TASK.md and run the tests' --dangerously-skip-permissions", workdir="/path/to/repo", background=true, notify_on_complete=true)
# then: process(action="poll"/"log"/"wait", session_id=<id>)
```

### 交互式多轮对话（PTY + tmux）

对于对话式会话，可在 `pty=true` 的环境下运行 `agy -i`（或直接使用 `agy`），并结合 tmux 的 `capture-pane`/`send-keys` 功能，其用法与 `codex`/`claude-code` 技能文档中的描述完全一致。之后可通过 `--continue`/-c 或指定的 `--conversation <id>` 参数继续对话。

### 并行实例（批量子任务/工作树扩展）

为每个任务创建一个 Git 工作树，并在每个工作树下独立启动一个 `agy -p` 实例（在后台运行），随后收集结果——这与 `codex` 技能用于批量问题修复时的工作树扩展方式相同。请根据机器性能及您的审核能力限制并行实例的数量。

### 输出格式及相关注意事项（与 Claude Code 不同）

- `agy -p` 仅返回**纯文本**——不存在 `--output-format json` 参数，也不会生成包含 `session_id`/成本/轮次数的结果封装结构。需直接解析标准输出，无需期望得到 JSON 对象。
- **没有 `--max-turns` 参数**。单次运行的时长受 `--print-timeout`（默认为 5 分钟）限制。对于耗时较长的任务，可将其值调大，例如设置为 `--print-timeout 20m`。同时请在终端中使用 `timeout=` 参数，以避免外部调用提前终止运行。

### 编排调度边界

Antigravity属于**任务执行后端或第三方审核工具**——其执行细节由负责运行任务的智能体/账号掌控，而非一级编排原语。切勿在看板中将`agy`单独设为一张卡片，也不应将其视为协调层；应通过常规任务图来分配工作，由被指定的执行者自行选择使用`agy`（而非Codex、Claude-Code或直接工具）作为执行方式。仅当用户有明确要求、某执行者被配置为使用该工具，或是需要借助Gemini系列模型对其他智能体的计划或差异结果进行交叉验证时，才应显式调用它。

## 核心路径

- 可执行文件/入口点：`agy`
- 应用数据目录：`~/.gemini/antigravity-cli/`
- 配置文件：`~/.gemini/antigravity-cli/settings.json`
- 绑定配置文件：`~/.gemini/antigravity-cli/keybindings.json`
- 日志文件：`~/.gemini/antigravity-cli/log/cli-*.log`
- 对话记录：`~/.gemini/antigravity-cli/conversations/`
- 智能体处理中间产物：`~/.gemini/antigravity-cli/brain/`
- 历史记录：`~/.gemini/antigravity-cli/history.jsonl`
- 插件暂存目录：`~/.gemini/antigravity-cli/plugins/<plugin_name>/`

## 快速参考

### 包装器命令
- `agy changelog`
- `agy help`
- `agy install`
- `agy plugin` / `agy plugins`
- `agy update`

### 常用标志参数
- `--add-dir`
- `--continue` / `-c`
- `--conversation`
- `--dangerously-skip-permissions`
- `--print` / `-p`
- `--print-timeout`
- `--prompt`
- `--prompt-interactive` / `-i`
- `--sandbox`
- `--log-file`
- `--version`

### 插件子命令（`agy plugin --help`）
- `list`、`import [source]`、`install <target>`、`uninstall <name>`、  
  `enable <name>`、`disable <name>`、`validate [path]`、`link <mp> <target>`、  
  `help`

### 安装参数（`agy install --help`）
- `--dir`、`--skip-aliases`、`--skip-path`

### 会话中的斜杠命令
- **对话控制：** `/resume`（`/switch`）、`/rewind`（`/undo`）、  
  `/rename <name>`、`/clear`、`/fork`、`/reset`、`/new`
- **设置与工具：** `/config`、`/settings`、`/permissions`、`/model`、  
  `/keybindings`、`/statusline`、`/tasks`、`/skills`、`/mcp`、`/open <path>`、  
  `/usage`、`/logout`、`/agents`
- **提示词辅助功能：** `@` 可自动补全路径，`esc esc` 可清除提示词（非流式模式下使用），  
  `!` 可直接执行终端命令，`?` 可打开帮助文档

## 设置与权限

### 常见设置键（`settings.json`）
- `allowNonWorkspaceAccess`
- `colorScheme`
- `permissions.allow`
- `trustedWorkspaces`

### 权限模式
`request-review`、`always-proceed`、`strict`、`proceed-in-sandbox`。

### 沙箱模式行为
- `settings.json` 中的 `enableTerminalSandbox` 为布尔值，默认值为 `false`。
- 启动时指定的参数（`--sandbox`、`--dangerously-skip-permissions`）可覆盖当前会话的持久设置。

## 认证行为

- CLI 会首先尝试使用操作系统的安全密钥环进行认证。
- 若未保存会话，则回退到基于浏览器的 Google 登录方式。
- 在本地环境中会打开默认浏览器；通过 SSH 连接时则会显示授权 URL，并等待用户粘贴授权码。
- `/logout` 命令可删除已保存的凭据。

## 插件

- 插件存储在 `~/.gemini/antigravity-cli/plugins/<plugin_name>/` 目录下。
- 它们可以打包技能、智能体、规则、MCP 服务器以及钩子功能。
- 若 `agy plugin list` 的输出中未显示任何已导入的插件，这也属于正常的空状态。

## 常见问题

- `agy help` 会显示封装后的命令，而非交互式的斜杠命令。
- `agy --version` 是安全的非交互式版本检查方式；而 `agy version` 为交互式命令，若没有真实的 TTY 则可能无法正常运行。
- 查找故障的首选位置是 `~/.gemini/antigravity-cli/log/cli-*.log`（可使用 `read_file` 命令读取）。
- 不要将持久化的 JSON 配置与启动时的临时覆盖设置混淆。
- `~/.gemini/antigravity-cli/bin/agentapi` 实际上是 `agy agentapi` 的简化封装版本。
- 在 WSL 环境中，令牌存储采用文件形式，因此认证问题通常属于本地文件或会话状态问题，而非仅限于浏览器的问题。
- 工作空间身份可能取决于启动目录以及 `.antigravitycli` 项目标记。
- `agy -p` 命令仅输出纯文本——不支持 `--output-format json` 参数，也不会生成结果封装结构。请勿尝试从中解析 JSON 对象（这与 `claude-code` 不同）。
- 打印操作受 `--print-timeout`（默认值为 5 分钟）参数控制，而非 `--max-turns` 参数（`agy` 中并不存在该参数）。

## 验证

可通过 `terminal` 工具确认安装是否成功且可用（使用 `read_file` 命令读取文件）：

1. `terminal(command="command -v agy")`
2. `terminal(command="agy --version")`
3. `terminal(command="agy help")`
4. `terminal(command="agy plugin list")`
5. 读取 `~/.gemini/antigravity-cli/settings.json` 文件中的内容
6. 读取最新的 `~/.gemini/antigravity-cli/log/cli-*.log` 文件中的内容
7. 如有需要，可读取 `~/.gemini/antigravity-cli/keybindings.json` 文件中的内容

## 支持文件

- `references/cli-docs.md` — 汇集自入门指南、使用说明及功能文档的精简要点。
