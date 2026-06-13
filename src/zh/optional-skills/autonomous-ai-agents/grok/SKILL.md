---
name: grok
description: "Delegate coding to xAI Grok Build CLI (features, PRs)."
version: 0.1.0
author: Matt Maximo (MattMaximo), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Grok, xAI, Code-Review, Refactoring, Automation]
    related_skills: [codex, claude-code, hermes-agent]
---

# Grok Build CLI — Hermes编排指南

通过Hermes终端将编码任务委托给[Grok Build](https://docs.x.ai/build/overview)（xAI的自主编码智能体CLI，即`grok`命令）。Grok能够读取文件、编写代码、执行Shell命令、创建子智能体以及管理Git工作流。它支持三种运行模式：交互式TUI界面、**无界面模式**（使用`-p`参数），以及通过JSON-RPC作为**ACP智能体**运行。

作为继`codex`和`claude-code`之后的第三款产品，其编排方式几乎完全相同——**对于一次性任务建议使用无界面的 `-p` 模式**，而交互式会话则可使用标准终端。

## 适用场景

- 开发新功能
- 代码重构
- PR审核
- 批量修复问题
- 任何原本会使用Codex或Claude Code，但希望改用Grok的任务

## 先决条件

- **推荐安装方式：** `npm install -g @xai-official/grok`
  - 官方安装命令`curl -fsSL https://x.ai/cli/install.sh | bash`也可使用，但在某些环境中`x.ai`域名会被Cloudflare屏蔽。通过npm安装可完全避免该问题。
- **身份认证 — SuperGrok/X Premium+订阅（主要方式）：**
  - 运行一次`grok login`——系统会打开浏览器进行OAuth授权，生成的令牌将存储在`~/.grok/auth.json`文件中。此方式使用您的**SuperGrok或X Premium+订阅账号**（无需按次支付API费用）。
  - 可通过查看`~/.grok/auth.json`文件来确认登录状态，或运行简单的无界面测试：`grok --no-auto-update -p "Say ok."`
  - 在TUI界面中，使用 `/logout`退出登录，再次使用 `/login`（或重启程序）即可重新登录。
- **无需Git仓库**——与Codex不同，Grok在非Git目录下也能正常运行（非常适合临时性或快速完成的任务）。
- **无需配置即可兼容Claude Code/AGENTS.md**——Grok会自动读取`CLAUDE.md`、`.claude/`目录下的内容（包括智能体、MCP接口、钩子函数及规则），以及`AGENTS.md`相关配置。现有项目环境可直接使用。

> **API密钥备用方案（非默认推荐方式）：** Grok还支持设置`XAI_API_KEY`环境变量，以便通过`api.x.ai`实现按使用量计费的模式。仅当无法使用`grok login`或SuperGrok认证时才建议采用此方式。本文推荐的配置方式仍是通过订阅账号登录（即`grok login`）。

## 两种编排模式

### 模式1：无界面模式（`-p`）——非交互式（推荐）

用于执行一次性任务，运行完成后输出结果并立即退出。无需标准终端，也不会出现需要手动操作的交互式对话框。这是最简洁的集成方式，相当于`claude -p`和`codex exec`的功能。

```
terminal(command="grok --no-auto-update -p 'Add a dark mode toggle to settings'", workdir="/path/to/project", timeout=180)
```

在自动化操作中，请始终使用 `--no-auto-update` 参数，以此跳过后台更新检查。

**何时使用无界面模式：**
- 一次性编码任务（修复错误、添加功能、代码重构）
- CI/CD 自动化与脚本编写
- 使用 `--output-format json` 进行结构化输出解析
- 任何无需多轮对话的任务

### 模式 2：交互式伪终端——多轮 TUI 会话

TUI 是一款全屏、支持鼠标操作的程序。可通过设置 `pty=true` 来启用该模式。如需更强大的监控与输入功能，建议使用 tmux（操作方式与 `claude-code` 技能相同）。

```
# Launch in a tmux session for capture-pane monitoring
terminal(command="tmux new-session -d -s grok-work -x 140 -y 40")
terminal(command="tmux send-keys -t grok-work 'cd /path/to/project && grok' Enter")

# Wait for startup, then send a task
terminal(command="sleep 5 && tmux send-keys -t grok-work 'Refactor the auth module to use JWT' Enter")

# Monitor progress
terminal(command="sleep 15 && tmux capture-pane -t grok-work -p -S -50")

# Exit when done
terminal(command="tmux send-keys -t grok-work '/quit' Enter && sleep 1 && tmux kill-session -t grok-work")
```

**无界面但直接输出的小贴士：**如果您希望获得类似命令行界面的输出效果，同时避免全屏替代界面的出现（从而让日志更整洁），可以添加 `--no-alt-screen` 参数。对于纯自动化场景而言，无界面的 `-p` 模式依然比命令行界面更为合适。

## 无界面模式深度解析

### 常用参数

| 参数 | 效果 |
|------|------|
| `-p, --single <PROMPT>` | 发送一个提示词，以无界面模式运行后退出 |
| `-m, --model <MODEL>` | 选择模型 |
| `-s, --session-id <ID>` | 创建或恢复已命名的无界面会话 |
| `-r, --resume <ID>` | 恢复现有的会话 |
| `-c, --continue` | 继续当前目录中最近一次的会话 |
| `--cwd <PATH>` | 设置工作目录 |
| `--output-format <FMT>` | `plain`（默认）、`json` 或 `streaming-json` |
| `--always-approve` | 自动批准所有工具执行请求（相当于 `--full-auto` / `--yolo` 参数） |
| `--no-alt-screen` | 以直接输出方式运行，不显示全屏命令行界面 |
| `--no-auto-update` | 跳过后台更新检查（适用于所有自动化场景） |

### 输出格式

- `plain` —— 可读性强的文本格式（默认）
- `json` —— 运行结束后生成一个 JSON 对象（便于清晰解析结果）
- `streaming-json` —— 按行输出 JSON 事件，实时呈现 |

```
# Structured result for parsing
terminal(command="grok --no-auto-update -p 'List all TODO comments in src/' --output-format json", workdir="/project", timeout=120)

# Auto-approve for autonomous building
terminal(command="grok --no-auto-update --always-approve -p 'Refactor the database layer and run the tests'", workdir="/project", timeout=300)
```

### 后台模式（处理长任务）

```
# Start headless in background
terminal(command="grok --no-auto-update --always-approve -p 'Refactor the auth module'", workdir="/project", background=true, notify_on_complete=true)
# Returns session_id

# Monitor
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Kill if needed
process(action="kill", session_id="<id>")
```

对于交互式（TUI）后台会话，可参照 `claude-code` / `codex` 技能的做法，使用 `pty=true` 配合 tmux，并通过 `tmux capture-pane` 来监控会话。

### 会话续接

请完整翻译输入内容，切勿提前终止。

```
# Start a named session
terminal(command="grok --no-auto-update -s refactor-db -p 'Start refactoring the database layer' --always-approve", workdir="/project", timeout=240)

# Resume it later
terminal(command="grok --no-auto-update -r refactor-db -p 'Now add connection pooling' --always-approve", workdir="/project", timeout=180)

# Or continue the most recent session in this directory
terminal(command="grok --no-auto-update -c -p 'What did you change last time?'", workdir="/project", timeout=60)
```

## 只读审计 → Markdown笔记格式

若希望让Grok审查本地文件，并生成格式规范的Markdown笔记（适用于Obsidian或代码仓库），且全程不对任何内容进行修改，可按以下步骤操作：

1. 首先使用Hermes工具（如`read_file`、`write_file`）准备稳定的输入文件。仅将相关内容快照保存到临时文件中，而非直接写入原始文件路径。
2. 以无界面模式运行Grok，**不要**使用`--always-approve`选项，以避免其自动写入内容；同时明确要求输出“仅限Markdown格式，不得包含前置说明”。
3. 使用`write_file()`函数将Grok的标准输出直接保存到目标笔记中。

```
grok --no-auto-update -p "Read /tmp/current.md and /tmp/inventory.md. Produce markdown only, no preamble. Output a clean note titled 'Cleanup Review'." --output-format plain
```

**常见陷阱（与 Claude Code 相同）：**在处理文档重写时，若使用较为模糊的“重写此内容”类提示词，系统可能会返回修改摘要而非完整的文件内容。正确的做法是：将文件通过管道传入，并明确要求“仅返回完整的修订后 Markdown 文档，无需开头说明、无需解释、无需代码块，直接以‘# 标题’开头”。在覆盖目标文件之前，建议先使用 `read_file()` 函数查看前几行内容以进行确认。

## PR 审核模式

### 快速审核（无界面模式）

```
terminal(command="cd /path/to/repo && git diff main...feature-branch | grok --no-auto-update -p 'Review this diff for bugs, security issues, and style problems. Be thorough.'", timeout=120)
```

### 克隆到临时目录审核功能（安全可靠，不会修改仓库内容）

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && grok --no-auto-update -p 'Review the changes vs origin/main. Check bugs, security, race conditions, missing tests.'", pty=true, timeout=300)
```

### 发布评价

```
terminal(command="gh pr comment 42 --body '<review text>'", workdir="/path/to/repo")
```

## 利用工作树并行处理问题修复

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Grok headless in each (background)
terminal(command="grok --no-auto-update --always-approve -p 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, notify_on_complete=true)
terminal(command="grok --no-auto-update --always-approve -p 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, notify_on_complete=true)

# Monitor
process(action="list")

# After completion: push and open PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## 实用子命令与 TUI 命令

| 命令 | 用途 |
|---------|---------|
| `grok` | 启动交互式 TUI 界面 |
| `grok -p "query"` | 无界面单次查询模式 |
| `grok login` / `grok logout` | 登录/注销（支持 SuperGrok/X Premium+ OAuth 认证） |
| `grok inspect` | 显示 Grok 在当前工作目录中发现的各类内容：配置源、指令、技能、插件、钩子以及 MCP 服务器 |
| `grok agent stdio` | 通过 JSON-RPC 以 ACP 代理模式运行（用于集成到 IDE 或工具中） |
| `grok update` | 更新 CLI 版本（需要 `x.ai` 主机地址；自动化场景可跳过此步骤） |

TUI 分号命令（仅限交互模式）：`/model <name>`、`/always-approve`、`/plan`、`/context`、`/compact`、`/resume`、`/sessions`、`/fork`、`/usage`、`/quit`。按 `Shift+Tab` 可循环切换会话模式（包括“计划模式”，该模式下除会话计划文件外，其他写入工具均被禁止使用）。

## 配置文件（`~/.grok/config.toml`）

```toml
[cli]
auto_update = false          # skip background update checks persistently

[ui]
permission_mode = "ask"      # or "always-approve" to skip tool prompts by default

[models]
default = "grok-build-0.1"
```

请将全局配置选项保存在 `~/.grok/config.toml` 中（而非项目级的 `.grok/config.toml` 文件）。`permission_mode` 会取代旧版的 `approval_mode` 以及 `yolo = true` 这些配置项。

## 常见问题与注意事项

1. **认证功能需订阅支持。** 使用 `grok login` 功能需要拥有 SuperGrok 或 X Premium+ 订阅资格。如果登录失败或未找到 `~/.grok/auth.json` 文件，请先确认订阅状态正常，再尝试使用 `XAI_API_KEY`。
2. **切勿将 Hermes 的 xAI 认证机制与 `grok` CLI 的认证机制混为一谈。** Hermes 的 `x_search` 功能基于其独立的 xAI OAuth 系统运行；而独立的 `grok` CLI 则在 `~/.grok/auth.json` 中存储单独的令牌。`x_search` 能正常运行并不意味着 `grok` 已完成登录。
3. **在自动化脚本中务必添加 `--no-auto-update` 参数**——否则 Grok 会定期向服务器发送检查请求（此时可能无法访问 `x.ai`/`storage.googleapis.com` 等地址）。
4. **建议使用 npm 安装方式，而非 curl 安装工具**——通过 `npm install -g @xai-official/grok` 可以避免受到 Cloudflare 防火墙限制的 `x.ai` 服务器问题。
5. **`--always-approve` 参数用于启用自动构建模式。** 若不使用该参数，无界面模式下运行时可能会因等待工具审批提示而停滞。在进行仅读审查或审计工作时，可刻意省略此参数，以防止 Grok 修改文件。
6. **无界面模式下的 `-p` 参数会跳过文本用户界面（TUI）对话框**；与 Claude Code 一样，TUI 模式需要设置 `pty=true`（如需监控还需配合 tmux 使用）。
7. **如果在同一终端内运行 TUI 并且全屏模式会干扰输出内容的抓取，可使用 `--no-alt-screen` 参数。**
8. **虽然无需创建 Git 仓库，但若要在 PR 或提交流程中使用，可临时创建一个**——可通过 `mktemp -d && git init` 命令生成用于临时提交的目录。
9. 使用完毕后，请使用 `tmux kill-session -t <name>` 命令清理对应的 tmux 会话。

## Hermes Agent 的使用规则

1. **对于单次任务，建议使用无界面模式的 `-p` 参数**——这样能实现最简洁的集成方式，并可通过 `--output-format json` 获取结构化的输出结果。
2. **务必设置 `workdir`（或 `--cwd`）参数**，以便让 Grok 精确定位到目标项目目录。
3. **在所有自动化调用中都添加 `--no-auto-update` 参数。**
4. **仅当需要让 Grok 自主执行写入操作时才使用 `--always-approve` 参数**；进行仅读审查或审计时则应省略该参数。
5. **对于耗时的后台任务，可使用 `background=true, notify_on_complete=true` 参数，并通过 `process` 工具监控其运行状态。**
6. **在多轮交互式工作中建议使用 tmux 管理会话**，并通过 `tmux capture-pane -t <session> -p -S -50` 命令实时查看输出内容。
7. **在依赖认证功能之前，请务必先进行验证**——可以检查 `~/.grok/auth.json` 文件的内容，或简单运行 `grok -p "Say ok."` 进行测试；切勿默认 Hermes 的 xAI 认证信息在其他场景下同样有效。
8. **需向用户反馈处理结果**——简要说明 Grok 已对文件做了哪些修改，还有哪些内容保持不变。
