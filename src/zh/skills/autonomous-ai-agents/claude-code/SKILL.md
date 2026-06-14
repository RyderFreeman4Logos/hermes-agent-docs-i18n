---
name: claude-code
description: "Delegate coding to Claude Code CLI (features, PRs)."
version: 2.2.0
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Anthropic, Code-Review, Refactoring, PTY, Automation]
    related_skills: [codex, hermes-agent, opencode]
---

# Claude Code — Hermes编排指南

通过Hermes终端将编程任务委托给[Claude Code](https://code.claude.com/docs/en/cli-reference)（Anthropic推出的自主编程智能体CLI）。Claude Code v2.x能够自主读取文件、编写代码、执行Shell命令、创建子智能体以及管理Git工作流。

## 前提条件

- **安装：** `npm install -g @anthropic-ai/claude-code`
- **认证：** 运行一次`claude`即可完成登录（Pro/Max版本支持浏览器OAuth认证，也可直接设置`ANTHROPIC_API_KEY`）
- **控制台认证：** 如需通过API密钥计费，请使用`claude auth login --console`
- **SSO认证：** 企业版用户请使用`claude auth login --sso`进行认证
- **检查状态：** 可通过`claude auth status`（输出JSON格式）或`claude auth status --text`（人类可读格式）查看状态
- **健康检查：** 使用`claude doctor`可检查自动更新工具及安装环境的运行状况
- **版本查询：** 使用`claude --version`查看版本信息（需使用v2.x及以上版本）
- **更新版本：** 可通过`claude update`或`claude upgrade`命令进行升级

## 两种编排模式

Hermes与Claude Code之间存在两种截然不同的交互方式，可根据具体任务选择合适的模式。

### 模式1：打印模式（`-p`）——非交互式（适用于大多数任务）

打印模式用于执行一次性任务，处理完成后返回结果并退出。该模式无需伪终端，也不会出现交互式提示符，是实现最简洁集成的方式。

```
terminal(command="claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**何时使用打印模式：**
- 单次性的编程任务（修复漏洞、添加功能、代码重构）
- CI/CD自动化与脚本编写
- 使用 `--json-schema` 进行结构化数据提取
- 通过管道输入进行处理（如 `cat file | claude -p "analyze this"`）
- 任何不需要多轮对话的任务

打印模式会**跳过所有交互式对话**——既没有工作空间信任提示，也没有权限确认步骤。正因如此，它非常适合用于自动化场景。

### 模式2：通过 tmux 实现的交互式 PTY —— 多轮对话会话

交互模式提供了一个完整的对话式 REPL 环境，您可以在其中发送后续指令、使用斜杠命令，并实时查看 Claude 的处理过程。**此模式需要借助 tmux 进行管理。**

```
# Start a tmux session
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")

# Launch Claude Code inside it
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")

# Wait for startup, then send your task
# (after ~3-5 seconds for the welcome screen)
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Refactor the auth module to use JWT tokens' Enter")

# Monitor progress by capturing the pane
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -50")

# Send follow-up tasks
terminal(command="tmux send-keys -t claude-work 'Now add unit tests for the new JWT code' Enter")

# Exit when done
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

**何时使用交互模式：**
- 需要多轮迭代处理的任务（重构 → 审核 → 修复 → 测试循环）
- 需要人工介入决策的任务
- 探索性编码环节
- 需要使用 Claude 的斜杠命令（如 `/compact`、`/review`、`/model`）时

## PTY 对话框处理（交互模式的核心要点）

首次启动 Claude Code 时，系统会显示最多两个确认对话框。您必须通过 tmux 的 send-keys 命令来处理这些对话框：

### 对话框 1：工作区信任验证（首次访问某个目录时）
```
❯ 1. Yes, I trust this folder    ← DEFAULT (just press Enter)
  2. No, exit
```
**操作方法：** 使用命令 `tmux send-keys -t <session> Enter` —— 默认选中状态即为正确。 

### 对话框 2：跳过权限警告（仅在使用 --dangerously-skip-permissions 参数时生效）
```
❯ 1. No, exit                    ← DEFAULT (WRONG choice!)
  2. Yes, I accept
```
**操作方式：** 首先需向下导航，随后按下回车键。
```
tmux send-keys -t <session> Down && sleep 0.3 && tmux send-keys -t <session> Enter
```

### 稳健的对话处理模式
```
# Launch with permissions bypass
terminal(command="tmux send-keys -t claude-work 'claude --dangerously-skip-permissions \"your task\"' Enter")

# Handle trust dialog (Enter for default "Yes")
terminal(command="sleep 4 && tmux send-keys -t claude-work Enter")

# Handle permissions dialog (Down then Enter for "Yes, I accept")
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")

# Now wait for Claude to work
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -60")
```

**注意：** 一旦某个目录首次被接受信任，后续就不会再出现信任确认对话框。而每次使用 `--dangerously-skip-permissions` 选项时，仅会再次出现权限确认对话框。

## CLI 子命令

| 子命令 | 功能 |
|----------|------|
| `claude` | 启动交互式 REPL |
| `claude "query"` | 带初始提示语启动 REPL |
| `claude -p "query"` | 打印模式（非交互式，处理完成后自动退出） |
| `cat file \| claude -p "query"` | 将文件内容通过管道作为标准输入传递给 Claude |
| `claude -c` | 继续当前目录中最最近的对话 |
| `claude -r "id"` | 根据 ID 或名称恢复特定会话 |
| `claude auth login` | 登录（如需进行 API 计费，请添加 `--console` 选项；企业版则使用 `--sso`） |
| `claude auth status` | 检查登录状态（返回 JSON 格式数据；使用 `--text` 可获取易读文本格式） |
| `claude mcp add <name> -- <cmd>` | 添加一个 MCP 服务器 |
| `claude mcp list` | 列出已配置的 MCP 服务器 |
| `claude mcp remove <name>` | 删除某个 MCP 服务器 |
| `claude agents` | 列出已配置的智能体 |
| `claude doctor` | 对安装版本及自动更新工具进行健康检查 |
| `claude update` / `claude upgrade` | 将 Claude Code 更新到最新版本 |
| `claude remote-control` | 启动服务器，以便从 claude.ai 或移动应用远程控制 Claude |
| `claude install [target]` | 安装原生构建版本（稳定版、最新版或指定版本） |
| `claude setup-token` | 设置长期有效的认证令牌（需订阅服务） |
| `claude plugin` / `claude plugins` | 管理 Claude Code 的插件 |
| `claude auto-mode` | 查看自动模式分类器配置 |

## 打印模式详解

### 结构化 JSON 输出
```
terminal(command="claude -p 'Analyze auth.py for security issues' --output-format json --max-turns 5", workdir="/project", timeout=120)
```

返回一个包含以下内容的 JSON 对象：
```json
{
  "type": "result",
  "subtype": "success",
  "result": "The analysis text...",
  "session_id": "75e2167f-...",
  "num_turns": 3,
  "total_cost_usd": 0.0787,
  "duration_ms": 10276,
  "stop_reason": "end_turn",
  "terminal_reason": "completed",
  "usage": { "input_tokens": 5, "output_tokens": 603, ... },
  "modelUsage": { "claude-sonnet-4-6": { "costUSD": 0.078, "contextWindow": 200000 } }
}
```

**关键字段：** 用于恢复会话的 `session_id`，用于统计智能体循环次数的 `num_turns`，用于追踪花费金额的 `total_cost_usd`，以及用于检测成功/失败的 `subtype`（可选值包括 `success`、`error_max_turns`、`error_budget`）。

### 流式 JSON 输出
如需实现实时令牌流式输出，可使用带有 `--verbose` 参数的 `stream-json` 命令：
```
terminal(command="claude -p 'Write a summary' --output-format stream-json --verbose --include-partial-messages", timeout=60)
```

返回以换行符分隔的 JSON 格式事件。如需查看实时文本内容，可使用 jq 工具进行过滤：
```
claude -p "Explain X" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

流式事件包括 `system/api_retry`，其中包含 `attempt`、`max_retries` 以及 `error` 字段（例如 `rate_limit`、`billing_error`）。

### 双向流式传输
用于实现实时输入与输出流式处理：
```
claude -p "task" --input-format stream-json --output-format stream-json --replay-user-messages
```
`--replay-user-messages`：在标准输出中重新输出用户消息，以便用户进行确认。  

### 管道输入
```
# Pipe a file for analysis
terminal(command="cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1", timeout=60)

# Pipe multiple files
terminal(command="cat src/*.py | claude -p 'Find all TODO comments' --max-turns 1", timeout=60)

# Pipe command output
terminal(command="git diff HEAD~3 | claude -p 'Summarize these changes' --max-turns 1", timeout=60)
```

### 结构化提取的 JSON Schema 规范
```
terminal(command="claude -p 'List all functions in src/' --output-format json --json-schema '{\"type\":\"object\",\"properties\":{\"functions\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}},\"required\":[\"functions\"]}' --max-turns 5", workdir="/project", timeout=90)
```

解析 JSON 结果中的 `structured_output`。Claude 会在返回结果之前根据预定义的架构对其内容进行验证。

### 会话续传

请翻译完整的输入内容，切勿提前终止处理。
```
# Start a task
terminal(command="claude -p 'Start refactoring the database layer' --output-format json --max-turns 10 > /tmp/session.json", workdir="/project", timeout=180)

# Resume with session ID
terminal(command="claude -p 'Continue and add connection pooling' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"session_id\"])') --max-turns 5", workdir="/project", timeout=120)

# Or resume the most recent session in the same directory
terminal(command="claude -p 'What did you do last time?' --continue --max-turns 1", workdir="/project", timeout=30)

# Fork a session (new ID, keeps history)
terminal(command="claude -p 'Try a different approach' --resume <id> --fork-session --max-turns 10", workdir="/project", timeout=120)
```

### 用于 CI/脚本开发的纯模式
```
terminal(command="claude --bare -p 'Run all tests and report failures' --allowedTools 'Read,Bash' --max-turns 10", workdir="/project", timeout=180)
```

`--bare` 参数可跳过钩子、插件、MCP 服务发现以及 CLAUDE.md 文件的加载，从而实现最快速的启动速度。该模式需要提供 `ANTHROPIC_API_KEY`（无需进行 OAuth 验证）。

在裸模式下单选加载上下文的内容如下：
| 要加载的内容 | 参数 |
|---------|------|
| 系统提示词补充内容 | `--append-system-prompt "文本内容"` 或 `--append-system-prompt-file 文件路径` |
| 设置参数 | `--settings <文件或JSON格式>` |
| MCP 服务器配置 | `--mcp-config <文件或JSON格式>` |
| 自定义智能体 | `--agents '<JSON格式>'` |

### 过载时的备用模型
```
terminal(command="claude -p 'task' --fallback-model haiku --max-turns 5", timeout=90)
```
当默认模型负载过重时，自动回退至指定的模型（仅限打印模式）。  

## 完整的 CLI 参数参考  

### 会话与环境  
| 参数 | 效果 |
|------|------|
| `-p, --print` | 非交互式单次执行模式（完成后退出） |
| `-c, --continue` | 在当前目录继续最近的对话 |
| `-r, --resume <id>` | 按 ID 或名称恢复特定会话（若无 ID 则会弹出交互式选择器） |
| `--fork-session` | 恢复时会创建新的会话 ID，而非重复使用原有 ID |
| `--session-id <uuid>` | 为本次对话指定特定的 UUID |
| `--no-session-persistence` | 不将会话保存到磁盘（仅限打印模式） |
| `--add-dir <paths...>` | 允许 Claude 访问额外的工作目录 |
| `-w, --worktree [name]` | 在 `.claude/worktrees/<name>` 中的独立 git 工作树中运行 |
| `--tmux` | 为工作树创建 tmux 会话（需配合 `--worktree` 使用） |
| `--ide` | 启动时自动连接到有效的 IDE |
| `--chrome` / `--no-chrome` | 开启/关闭用于网页测试的 Chrome 浏览器集成 |
| `--from-pr [number]` | 恢复与特定 GitHub PR 关联的会话 |
| `--file <specs...>` | 指定启动时需下载的文件资源（格式：`file_id:relative_path`） |

### 模型与性能  
| 参数 | 效果 |
|------|------|
| `--model <alias>` | 选择模型：`sonnet`、`opus`、`haiku`，或完整名称如 `claude-sonnet-4-6` |
| `--effort <level>` | 推理深度：`low`、`medium`、`high`、`max`、`auto` 或两者兼用 |
| `--max-turns <n>` | 限制智能体循环次数（仅限打印模式；可防止程序失控） |
| `--max-budget-usd <n>` | 以美元为单位限制 API 使用费用（仅限打印模式） |
| `--fallback-model <model>` | 当默认模型负载过重时自动回退至指定模型（仅限打印模式） |
| `--betas <betas...>` | 在 API 请求中包含的测试版头部信息（仅 API 密钥用户可用） |

### 权限与安全  
| 参数 | 效果 |
|------|------|
| `--dangerously-skip-permissions` | 自动批准所有工具的使用（包括文件写入、bash 命令、网络操作等） |
| `--allow-dangerously-skip-permissions` | 将自动跳过权限检查设置为可选选项，而非默认启用 |
| `--permission-mode <mode>` | `default`、`acceptEdits`、`plan`、`auto`、`dontAsk`、`bypassPermissions` |
| `--allowedTools <tools...>` | 白名单指定允许使用的工具（用逗号或空格分隔） |
| `--disallowedTools <tools...>` | 黑名单指定禁止使用的工具 |
| `--tools <tools...>` | 覆盖内置的工具集（`""` 表示无工具，`"default"` 表示使用所有工具，或直接输入工具名称） |

### 输出与输入格式  
| 参数 | 效果 |
|------|------|
| `--output-format <fmt>` | `text`（默认）、`json`（单个结果对象）、`stream-json`（以换行符分隔） |
| `--input-format <fmt>` | `text`（默认）或 `stream-json`（实时流式输入） |
| `--json-schema <schema>` | 强制输出符合指定架构的结构化 JSON 数据 |
| `--verbose` | 显示完整的逐轮对话输出 |
| `--include-partial-messages` | 随着消息到达即将其部分内容包含在输出中（适用于 stream-json 模式及打印模式） |
| `--replay-user-messages` | 在标准输出中重新输出用户发送的消息（适用于 stream-json 双向通信模式） |

### 系统提示词与上下文  
| 参数 | 效果 |
|------|------|
| `--append-system-prompt <text>` | **追加**到默认的系统提示词中（保留原有功能） |
| `--append-system-prompt-file <path>` | **追加**文件内容到默认的系统提示词中 |
| `--system-prompt <text>` | **替换**整个系统提示词（通常建议使用 `--append`） |
| `--system-prompt-file <path>` | 用文件内容**替换**系统提示词 |
| `--bare` | 跳过钩子、插件、MCP 发现、CLAUDE.md 以及 OAuth 功能（实现最快启动速度） |
| `--agents '<json>'` | 以 JSON 格式动态定义自定义子智能体 |
| `--mcp-config <path>` | 从 JSON 文件加载 MCP 服务器配置（可重复使用） |
| `--strict-mcp-config` | 仅使用 `--mcp-config` 中指定的 MCP 服务器，忽略其他所有配置 |
| `--settings <file-or-json>` | 从 JSON 文件或内联 JSON 中加载额外设置 |
| `--setting-sources <sources>` | 指定要加载的设置来源，用逗号分隔：`user`、`project`、`local` |
| `--plugin-dir <paths...>` | 仅针对当前会话从指定目录加载插件 |
| `--disable-slash-commands` | 禁用所有技能及斜杠命令 |

### 调试  
| 参数 | 效果 |
|------|------|
| `-d, --debug [filter]` | 启用调试日志记录，可可选地指定过滤条件（例如 `"api,hooks"`、`"!1p,!file"`） |
| `--debug-file <path>` | 将调试日志写入文件（该选项会隐式启用调试模式） |

### 智能体团队  
| 参数 | 效果 |
|------|------|
| `--teammate-mode <mode>` | 控制智能体团队显示方式：`auto`、`in-process` 或 `tmux` |
| `--brief` | 启用 `SendUserMessage` 工具，实现智能体与用户之间的通信 |

### --allowedTools / --disallowedTools 中的工具名称语法
```
Read                    # All file reading
Edit                    # File editing (existing files)
Write                   # File creation (new files)
Bash                    # All shell commands
Bash(git *)             # Only git commands
Bash(git commit *)      # Only git commit commands
Bash(npm run lint:*)    # Pattern matching with wildcards
WebSearch               # Web search capability
WebFetch                # Web page fetching
mcp__<server>__<tool>   # Specific MCP tool
```

## 设置与配置

### 设置层级（优先级从高到低）
1. **CLI 参数** — 优先级最高，可覆盖所有其他设置
2. **本地项目**：`.claude/settings.local.json`（个人专用，会被 git 忽略）
3. **项目级**：`.claude/settings.json`（团队共享，会被 git 记录）
4. **用户级**：`~/.claude/settings.json`（全局通用）

### 设置中的权限配置
```json
{
  "permissions": {
    "allow": ["Bash(npm run lint:*)", "WebSearch", "Read"],
    "ask": ["Write(*.ts)", "Bash(git push*)"],
    "deny": ["Read(.env)", "Bash(rm -rf *)"]
  }
}
```

### 内存文件（CLAUDE.md）层级结构
1. **全局级**：`~/.claude/CLAUDE.md` — 适用于所有项目  
2. **项目级**：`./CLAUDE.md` — 项目特定上下文（由 Git 跟踪）  
3. **本地级**：`.claude/CLAUDE.local.md` — 个人项目的覆盖配置（被 Git 忽略）  

在交互模式下，可使用 `#` 前缀快速添加到内存中：`# 始终使用两空格缩进。`

## 交互会话：斜杠命令

### 会话与上下文
| 命令 | 功能 |
|------|------|
| `/help` | 显示所有命令（包括自定义命令和 MCP 命令） |
| `/compact [focus]` | 压缩上下文以节省令牌；压缩后 CLAUDE.md 内容仍保留。例如：`/compact focus on auth logic` |
| `/clear` | 清除对话历史，重新开始会话 |
| `/context` | 以彩色网格形式展示上下文使用情况，并提供优化建议 |
| `/cost` | 查看令牌使用情况，包括各模型及缓存命中率的详细数据 |
| `/resume` | 切换到或继续另一个会话 |
| `/rewind` | 恢复到对话或代码中的上一个检查点 |
| `/btw <question>` | 提出旁题而不增加上下文成本 |
| `/status` | 显示版本信息、连接状态及会话详情 |
| `/todos` | 列出对话中记录的待办事项 |
| `/exit` 或 `Ctrl+D` | 结束会话 |

### 开发与审查
| 命令 | 功能 |
|------|------|
| `/review` | 请求对当前更改进行代码审查 |
| `/security-review` | 对当前更改进行安全分析 |
| `/plan [description]` | 进入计划模式，自动开始任务规划 |
| `/loop [interval]` | 在会话中安排周期性任务 |
| `/batch` | 为大量并行更改自动创建工作树（最多 5-30 个工作树） |

### 配置与工具
| 命令 | 功能 |
|------|------|
| `/model [model]` | 在会话中切换模型（使用方向键调整推理强度） |
| `/effort [level]` | 设置推理强度：`low`、`medium`、`high`、`max` 或 `auto` |
| `/init` | 为项目创建 CLAUDE.md 文件以存储内存信息 |
| `/memory` | 打开 CLAUDE.md 文件进行编辑 |
| `/config` | 打开交互式设置配置界面 |
| `/permissions` | 查看/更新工具权限 |
| `/agents` | 管理专用子代理 |
| `/mcp` | 用于管理 MCP 服务器的交互式界面 |
| `/add-dir` | 添加额外的工作目录（适用于多模块项目） |
| `/usage` | 显示计划限制及速率限制状态 |
| `/voice` | 启用即按即说语音模式（支持 20 种语言；按住空格键录音，松开键发送） |
| `/release-notes` | 用于选择版本发布说明的交互式界面 |

### 自定义斜杠命令
可创建 `.claude/commands/<name>.md` 文件（项目共享）或 `~/.claude/commands/<name>.md` 文件（个人使用）：

```markdown
# .claude/commands/deploy.md
Run the deploy pipeline:
1. Run all tests
2. Build the Docker image
3. Push to registry
4. Update the $ARGUMENTS environment (default: staging)
```

用法：`/deploy production` —— `$ARGUMENTS` 位置将被用户的输入内容替换。

### 技能（自然语言调用）
与需手动调用的斜杠命令不同，位于 `.claude/skills/` 目录中的技能实际上是 Markdown 格式的指南。当任务条件匹配时，Claude 会通过自然语言自动调用这些技能。

```markdown
# .claude/skills/database-migration.md
When asked to create or modify database migrations:
1. Use Alembic for migration generation
2. Always create a rollback function
3. Test migrations against a local database copy
```

## 交互式会话：键盘快捷键

### 基本控制
| 键位 | 操作 |
|-----|------|
| `Ctrl+C` | 取消当前输入或生成操作 |
| `Ctrl+D` | 退出会话 |
| `Ctrl+R` | 反向搜索命令历史记录 |
| `Ctrl+B` | 将正在运行的任务置于后台 |
| `Ctrl+V` | 将图片粘贴到对话中 |
| `Ctrl+O` | 转换为文字记录模式——查看 Claude 的思考过程 |
| `Ctrl+G` 或 `Ctrl+X Ctrl+E` | 在外部编辑器中打开提示词 |
| `Esc Esc` | 撤销对话内容或代码状态/生成摘要 |

### 模式切换
| 键位 | 操作 |
|-----|------|
| `Shift+Tab` | 循环切换权限模式（普通模式 → 自动接受模式 → 规划模式） |
| `Alt+P` | 切换模型 |
| `Alt+T` | 切换思考模式 |
| `Alt+O` | 切换快速模式 |

### 多行输入
| 键位 | 操作 |
|-----|------|
| `\` + `Enter` | 快速换行 |
| `Shift+Enter` | 换行（备用方式） |
| `Ctrl+J` | 换行（备用方式） |

### 输入前缀
| 前缀 | 操作 |
|-----|------|
| `!` | 直接执行 bash 命令，绕过 AI 处理（例如：`!npm test`）。单独使用 `!` 可切换到 shell 模式。 |
| `@` | 通过自动补全功能引用文件/目录（例如：`@./src/api/`） |
| `#` | 快速将内容添加到 CLAUDE.md 记忆库中（例如：`# 使用两空格缩进`） |
| `/` | 斜杠命令 |

### 专业技巧：“ultrathink”
在提示词中加入关键词 “ultrathink”，可让模型在当前轮次中投入最大程度的推理能力。无论当前的 `/effort` 设置为何，此指令都会触发最深度的思考模式。

## PR 审核模板

### 快速审核（打印模式）
```
terminal(command="cd /path/to/repo && git diff main...feature-branch | claude -p 'Review this diff for bugs, security issues, and style problems. Be thorough.' --max-turns 1", timeout=60)
```

### 深度审阅（交互式 + 工作流）
```
terminal(command="tmux new-session -d -s review -x 140 -y 40")
terminal(command="tmux send-keys -t review 'cd /path/to/repo && claude -w pr-review' Enter")
terminal(command="sleep 5 && tmux send-keys -t review Enter")  # Trust dialog
terminal(command="sleep 2 && tmux send-keys -t review 'Review all changes vs main. Check for bugs, security issues, race conditions, and missing tests.' Enter")
terminal(command="sleep 30 && tmux capture-pane -t review -p -S -60")
```

### 按编号查看 Pull Request 审核情况
```
terminal(command="claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10", workdir="/path/to/repo", timeout=120)
```

### 结合 tmux 的 Claude Worktree
```
terminal(command="claude -w feature-x --tmux", workdir="/path/to/repo")
```
在`.claude/worktrees/feature-x`路径下创建一个隔离的Git工作树，并为其生成一个tmux会话。若系统支持，将使用iTerm2的原生分屏功能；如需传统风格的tmux界面，请添加`--tmux=classic`参数。

## 并行运行Claude实例

同时执行多个独立的Claude任务：

```
# Task 1: Fix backend
terminal(command="tmux new-session -d -s task1 -x 140 -y 40 && tmux send-keys -t task1 'cd ~/project && claude -p \"Fix the auth bug in src/auth.py\" --allowedTools \"Read,Edit\" --max-turns 10' Enter")

# Task 2: Write tests
terminal(command="tmux new-session -d -s task2 -x 140 -y 40 && tmux send-keys -t task2 'cd ~/project && claude -p \"Write integration tests for the API endpoints\" --allowedTools \"Read,Write,Bash\" --max-turns 15' Enter")

# Task 3: Update docs
terminal(command="tmux new-session -d -s task3 -x 140 -y 40 && tmux send-keys -t task3 'cd ~/project && claude -p \"Update README.md with the new API endpoints\" --allowedTools \"Read,Edit\" --max-turns 5' Enter")

# Monitor all
terminal(command="sleep 30 && for s in task1 task2 task3; do echo '=== '$s' ==='; tmux capture-pane -t $s -p -S -5 2>/dev/null; done")
```

## CLAUDE.md — 项目上下文文件

Claude Code 会自动从项目根目录加载 `CLAUDE.md` 文件。您可利用它来保存项目的上下文信息：

```markdown
# Project: My API

## Architecture
- FastAPI backend with SQLAlchemy ORM
- PostgreSQL database, Redis cache
- pytest for testing with 90% coverage target

## Key Commands
- `make test` — run full test suite
- `make lint` — ruff + mypy
- `make dev` — start dev server on :8000

## Code Standards
- Type hints on all public functions
- Docstrings in Google style
- 2-space indentation for YAML, 4-space for Python
- No wildcard imports
```

**请明确具体要求。** 不要只说“编写优质代码”，而应给出具体指导，例如“JS代码需使用两空格缩进”或“测试文件应以`.test.ts`为后缀命名”。明确的指令能大幅减少后续的修改工作。

### 规则目录（模块化CLAUDE.md）
对于规则众多的项目，建议使用规则目录而非一个庞大的CLAUDE.md文件：
- **项目规则**：`.claude/rules/*.md` —— 供团队共享，纳入git版本控制
- **用户规则**：`~/.claude/rules/*.md` —— 个人专用，全局生效

规则目录中的每个`.md`文件都会被作为额外上下文加载。这种方式比将所有规则塞进一个CLAUDE.md文件更为清晰有序。

### 自动内存机制
Claude会自动将学习到的项目相关上下文存储在`~/.claude/projects/<project>/memory/`目录中。
- **存储限制**：每个项目最多25KB或200行数据
- 该内存与CLAUDE.md是分开的——它是Claude自己在不同会话间积累的关于该项目的笔记。

## 自定义子智能体

你可以在`.claude/agents/`（项目级）、`~/.claude/agents/`（个人级）中定义专用智能体，或通过`--agents` CLI参数（会话级）来创建它们：

### 智能体查找优先级
1. `.claude/agents/` —— 项目级，团队共享
2. `--agents` CLI参数 —— 会话级，动态生效
3. `~/.claude/agents/` —— 用户级，个人专用

### 创建智能体
```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Security-focused code review
model: opus
tools: [Read, Bash]
---
You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication/authorization flaws
- Secrets in code
- Unsafe deserialization
```

调用方式：`@security-reviewer review the auth module`

### 通过 CLI 调用动态智能体
```
terminal(command="claude --agents '{\"reviewer\": {\"description\": \"Reviews code\", \"prompt\": \"You are a code reviewer focused on performance\"}}' -p 'Use @reviewer to check auth.py'", timeout=120)
```

Claude 能够协调多个智能体协同工作：“使用 @db-expert 优化查询，再借助 @security 对变更进行审计。”  

## Hooks — 基于事件的自动化处理  

可在 `.claude/settings.json`（项目级）或 `~/.claude/settings.json`（全局级）中配置：

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{"type": "command", "command": "ruff check --fix $CLAUDE_FILE_PATHS"}]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -q 'rm -rf'; then echo 'Blocked!' && exit 2; fi"}]
    }],
    "Stop": [{
      "hooks": [{"type": "command", "command": "echo 'Claude finished a response' >> /tmp/claude-activity.log"}]
    }]
  }
}
```

### 八种钩子类型
| 钩子类型 | 触发时机 | 常见用途 |
|----------|----------|----------|
| `UserPromptSubmit` | Claude 处理用户提示之前 | 输入验证、日志记录 |
| `PreToolUse` | 工具执行之前 | 安全检查、阻止危险命令（返回值 2 表示阻止） |
| `PostToolUse` | 工具执行完成后 | 自动格式化代码、运行代码检查工具 |
| `Notification` | 发生权限请求或需要等待输入时 | 桌面通知、警报提示 |
| `Stop` | Claude 完成响应后 | 响应记录、状态更新 |
| `SubagentStop` | 子代理执行完成后 | 代理协调管理 |
| `PreCompact` | 上下文内存被清除之前 | 备份会话记录 |
| `SessionStart` | 会话开始时 | 加载开发环境相关上下文（例如 `git status`） |

### 钩子环境变量
| 变量名 | 变量内容 |
|--------|----------|
| `CLAUDE_PROJECT_DIR` | 当前项目路径 |
| `CLAUDE_FILE_PATHS` | 正在被修改的文件列表 |
| `CLAUDE_TOOL_INPUT` | 以 JSON 格式存储的工具参数 |

### 安全钩子示例
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{"type": "command", "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|git push.*--force|:(){ :|:& };:'; then echo 'Dangerous command blocked!' && exit 2; fi"}]
  }]
}
```

## MCP集成

可添加用于数据库、API及各类服务的外部工具服务器：

```
# GitHub integration
terminal(command="claude mcp add -s user github -- npx @modelcontextprotocol/server-github", timeout=30)

# PostgreSQL queries
terminal(command="claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres --connection-string postgresql://localhost/mydb", timeout=30)

# Puppeteer for web testing
terminal(command="claude mcp add puppeteer -- npx @anthropic-ai/server-puppeteer", timeout=30)
```

### MCP 范围
| 标志 | 范围 | 存储位置 |
|------|-------|---------|
| `-s user` | 全局（所有项目） | `~/.claude.json` |
| `-s local` | 当前项目（个人使用） | `.claude/settings.local.json`（被 git 忽略） |
| `-s project` | 当前项目（团队共享） | `.claude/settings.json`（被 git 跟踪） |

### 打印/CI 模式下的 MCP
```
terminal(command="claude --bare -p 'Query database' --mcp-config mcp-servers.json --strict-mcp-config", timeout=60)
```
`--strict-mcp-config` 选项会忽略除 `--mcp-config` 指定的服务器之外的所有 MCP 服务器。

在聊天中引用 MCP 资源的格式为：`@github:issue://123`

### MCP 限制与调优
- **工具描述**：每个服务器的工具描述及服务器说明的长度上限为 2KB。
- **结果大小**：默认有长度限制；如需处理较长的输出内容，可使用 `maxResultSizeChars` 注解将上限提升至 **500K** 字符。
- **输出令牌数**：通过 `export MAX_MCP_OUTPUT_TOKENS=50000` 可限制 MCP 服务器的输出量，从而避免上下文过载。
- **传输方式**：包括 `stdio`（本地进程）、`http`（远程）以及 `sse`（服务端推送事件）。

## 监控交互式会话

### 查看 TUI 状态
```
# Periodic capture to check if Claude is still working or waiting for input
terminal(command="tmux capture-pane -t dev -p -S -10")
```

请留意以下指示符号：
- 底部的 `❯` = 正在等待你的输入（Claude 已完成操作或正在提问）
- `●` 标记的行 = Claude 正在主动使用工具（读取、写入、执行命令）
- `⏵⏵ bypass permissions on` = 状态栏显示权限模式
- `◐ medium · /effort` = 状态栏中显示当前的运算强度等级
- `ctrl+o to expand` = 工具输出被截断（可交互式展开查看）

### 上下文窗口状态
在交互模式下使用 `/context` 可查看上下文使用情况的彩色网格图。关键阈值如下：
- **< 70%** — 正常运行，保持完整精度
- **70-85%** — 精度开始下降，建议使用 `/compact` 命令
- **> 85%** — 出现幻觉的风险显著上升，应使用 `/compact` 或 `/clear` 命令

## 环境变量

| 变量名 | 效果 |
|--------|------|
| `ANTHROPIC_API_KEY` | 用于身份验证的 API 密钥（可作为 OAuth 的替代方案） |
| `CLAUDE_CODE_EFFORT_LEVEL` | 默认运算强度：`low`、`medium`、`high`、`max` 或 `auto` |
| `MAX_THINKING_TOKENS` | 设置思考令牌上限（设为 `0` 可完全禁用思考功能） |
| `MAX_MCP_OUTPUT_TOKENS` | 限制来自 MCP 服务器的输出长度（默认值因版本而异，可设置为如 `50000`） |
| `CLAUDE_CODE_NO_FLICKER=1` | 启用备用屏幕渲染，消除终端闪烁现象 |
| `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` | 为保障安全，清除子进程中的敏感凭证 |

## 成本与性能优化建议

1. 在打印模式下使用 `--max-turns` 参数，以防止任务陷入无限循环。大多数任务可从 5-10 次轮次开始设置。
2. 使用 `--max-budget-usd` 设置成本上限。注意：仅创建系统提示缓存就需要至少约 0.05 美元。
3. 对于简单任务，使用 `--effort low` 参数（速度更快、成本更低）；对于复杂推理任务，则可使用 `high` 或 `max`。
4. 在 CI/脚本环境中使用 `--bare` 参数，可跳过插件和钩子检测的开销。
5. 使用 `--allowedTools` 仅允许 Claude 使用所需工具（例如在代码审查时仅允许使用“读取”工具）。
6. 当上下文内容过多时，在交互会话中使用 `/compact` 命令。
7. 如果只需分析已知内容，可直接通过管道输入数据，无需让 Claude 读取文件。
8. 对于简单任务，使用 `--model haiku`（成本更低）；对于复杂的多步骤任务，则使用 `--model opus`。
9. 在打印模式下使用 `--fallback-model haiku`，以便在模型负载过重时平稳处理。
10. 不同任务请开启新的会话——单次会话时长为 5 小时，使用新鲜上下文效率更高。
11. 在 CI 环境中使用 `--no-session-persistence`，避免已保存的会话持续堆积在磁盘上。

## 常见问题与注意事项

1. **交互模式必须依赖 tmux** — Claude Code 是一款完整的 TUI 应用。虽然在 Hermes 终端中单独设置 `pty=true` 也能使用，但 tmux 提供了 `capture-pane` 用于监控会话状态，以及 `send-keys` 用于输入操作，这些功能对于任务编排至关重要。
2. **`--dangerously-skip-permissions` 对话框的默认选项为“否，退出”** — 必须先按向下键再按回车键才能接受该选项。打印模式（`-p`）则完全跳过此步骤。
3. **`--max-budget-usd` 的最低值为约 0.05 美元** — 仅创建系统提示缓存就需要这么多成本。设置低于此值的参数会立即报错。
4. **`--max-turns` 仅适用于打印模式** — 在交互会话中会被忽略。
5. **Claude 可能会使用 `python` 而非 `python3`** — 在没有 `python` 符号链接的系统中，Claude 的 bash 命令首次执行时会失败，但它会自动修正。
6. **恢复会话需要处于相同的目录下** — `--continue` 参数会根据当前工作目录查找最近的会话。
7. **使用 `--json-schema` 时需要足够的 `--max-turns`** — Claude 需要先读取相关文件才能生成结构化输出，这需要多轮次处理。
8. **“信任对话框”每个目录仅会出现一次** — 仅首次出现时会弹出，之后会被缓存。
9. **后台运行的 tmux 会话会持续存在** — 使用完毕后务必通过 `tmux kill-session -t <name>` 清理这些会话。
10. **斜杠命令（如 `/commit`）仅在交互模式下有效** — 在 `-p` 打印模式下，需用自然语言描述任务。
11. **`--bare` 参数会跳过 OAuth 验证** — 此时需要设置 `ANTHROPIC_API_KEY` 环境变量，或在设置中配置 `apiKeyHelper`。
12. **上下文容量过高确实会影响输出质量** — 当上下文窗口使用率超过 70% 时，AI 的输出质量会明显下降。可通过 `/context` 命令监控情况，并及时使用 `/compact` 命令优化。

## Hermes Agent 使用规则

1. 对于单次任务，建议优先使用打印模式（`-p`）——输出更整洁，无需处理对话框，且结果结构化。
2. 多轮交互式任务请使用 tmux —— 这是管理 TUI 应用任务的唯一可靠方式。
3. 始终设置 `workdir` 参数 —— 确保 Claude 专注于正确的项目目录。
4. 在打印模式下设置 `--max-turns` 参数 —— 可防止无限循环及成本失控。
5. 定期监控 tmux 会话状态 —— 可使用 `tmux capture-pane -t <session> -p -S -50` 命令查看任务进度。
6. 注意观察 `❯` 提示符 —— 它表示 Claude 正在等待输入（已完成操作或正在提问）。
7. 使用完毕后及时清理 tmux 会话 —— 避免资源泄露。
8. 向用户汇报处理结果 —— 任务完成后，总结 Claude 的操作内容及产生的变化。
9. 不要强制终止运行缓慢的会话 —— Claude 可能正在进行多步骤处理，建议先查看进度。
10. 使用 `--allowedTools` 参数 —— 仅授予任务所需的权限。
