---
name: antigravity-cli
description: "Operate the Antigravity CLI (agy): plugins, auth, sandbox."
version: 0.1.0
author: Tony Simons (asimons81), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Antigravity, CLI, Auth, Plugins, Sandbox]
    related_skills: [grok, codex, claude-code, hermes-agent]
---

# Antigravity CLI（`agy`）

Antigravity CLI 的操作指南，该工具的调用方式为 `agy`。所有 `agy` 命令均需通过 Hermes 的 `terminal` 工具执行；可使用 `read_file` 命令查看其配置文件与日志。该技能属于参考型加流程指导类——它并不封装任何网络 API，因此 Hermes 本身无需进行任何身份验证。

## 适用场景

- 安装、更新或对 `agy` 可执行文件进行功能测试  
- 执行非交互式的 `agy --print` / `agy -p` 单次命令  
- 调试 Antigravity 的身份认证、沙箱机制、权限设置或插件状态  
- 查看 Antigravity 的配置项、快捷键设置、对话记录或日志文件  

## 思维模型

Antigravity 具有两层结构——需明确区分这两层，否则指导信息将会出错：

1. **Shell 包装命令** — 如 `agy help`、`agy install`、`agy plugin`、`agy update`、`agy changelog`。这类命令需通过 `terminal` 工具执行。  
2. **交互式会话中的斜杠命令** — 如 `/config`、 `/permissions`、 `/skills`、 `/agents` 等。这类命令仅存在于正在运行的 `agy` 图形用户界面会话中，而非 Shell 包装层。

`agy help` 显示的是 Shell 包装层的命令列表，而非会话中的斜杠命令。

## 先决条件

- PATH 环境变量中已包含 `agy` 可执行文件。可通过 `terminal` 工具进行验证：
  `command -v agy && agy --version`。
- 该技能无需任何环境变量或 API 密钥——Antigravity 通过操作系统密钥管理器或浏览器登录机制自行处理身份认证（详见下文“身份认证”部分）。

## 执行方法

所有 `agy` 命令均需通过 `terminal` 工具来执行。示例如下：

```
terminal(command="agy --version")
terminal(command="agy help")
terminal(command="agy plugin list")
terminal(command="agy --print 'Summarize the repo in 3 bullets'", workdir="/path/to/project")
```

如需进行交互式的多轮 TUI 会话，可使用 `pty=true` 参数启动 `agy`（并结合 `tmux` 用于捕获或监控），这与 `codex`/`claude-code` 技能所采用的模式相同。而对于一次性功能测试或脚本化提示，建议使用非交互模式的 `agy --print`。

若要查看 Antigravity 自身的文件，请通过下方“核心路径”中的路径调用 `read_file` 命令读取，切勿直接通过终端使用 `cat` 命令查看。

## 核心路径

- 可执行文件/入口程序：`agy`
- 应用数据目录：`~/.gemini/antigravity-cli/`
- 设置文件：`~/.gemini/antigravity-cli/settings.json`
- 绑定配置文件：`~/.gemini/antigravity-cli/keybindings.json`
- 日志文件：`~/.gemini/antigravity-cli/log/cli-*.log`
- 对话记录：`~/.gemini/antigravity-cli/conversations/`
- 智能处理相关文件：`~/.gemini/antigravity-cli/brain/`
- 历史记录：`~/.gemini/antigravity-cli/history.jsonl`
- 插件暂存目录：`~/.gemini/antigravity-cli/plugins/<plugin_name>/`

## 快速参考

### 包装命令
- `agy changelog`
- `agy help`
- `agy install`
- `agy plugin` / `agy plugins`
- `agy update`

### 有用标志参数
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

### 插件子命令（通过 `agy plugin --help` 查看）
- `list`、`import [source]`、`install <target>`、`uninstall <name>`、
  `enable <name>`、`disable <name>`、`validate [path]`、`link <mp> <target>`、
  `help`

### 安装相关标志参数（通过 `agy install --help` 查看）
- `--dir`、`--skip-aliases`、`--skip-path`

### 会话中的斜杠命令
- **对话控制：** `/resume`（/switch）、/rewind（/undo）、
  /rename <name>、/clear、/fork、/reset、/new
- **设置与工具：** /config、/settings、/permissions、/model、
  /keybindings、/statusline、/tasks、/skills、/mcp、/open <path>、
  /usage、/logout、/agents
- **提示词辅助功能：** `@` 可自动补全路径；当未处于流式输入模式时，`esc esc` 可清除提示词；`!` 可直接执行终端命令；`?` 可打开帮助文档

## 设置与权限

### 常见设置键（位于 `settings.json` 中）
- `allowNonWorkspaceAccess`
- `colorScheme`
- `permissions.allow`
- `trustedWorkspaces`

### 权限模式
`request-review`、`always-proceed`、`strict`、`proceed-in-sandbox`。

### 沙箱模式行为
- `settings.json` 中的 `enableTerminalSandbox` 为布尔值，默认值为 `false`。
- 启动时的特殊参数（如 `--sandbox`、`--dangerously-skip-permissions`）可覆盖当前会话的持久设置。

## 认证机制

- CLI 会首先尝试使用操作系统的安全密钥环进行认证。
- 若未保存会话，则会回退到基于浏览器的 Google 登录方式。
- 在本地环境中会自动打开默认浏览器；通过 SSH 连接时，则会显示授权网址，并要求用户粘贴授权码。
- 使用 `/logout` 命令可删除已保存的凭据。

## 插件

- 插件存储在 `~/.gemini/antigravity-cli/plugins/<plugin_name>/` 目录下。
- 它们可以整合技能、智能体、规则、MCP 服务器以及各种钩子功能。
- 若 `agy plugin list` 命令未列出任何已导入的插件，这也属于正常状态。

## 常见问题与注意事项

- `agy help` 命令仅显示包装命令，而不包含会话中的斜杠命令。
- `agy --version` 是安全的非交互式版本检查方式；而 `agy version` 为交互式命令，若没有真正的终端设备则可能无法正常运行。
- 出现故障时首先应查看 `~/.gemini/antigravity-cli/log/cli-*.log` 文件（可使用 `read_file` 命令读取）。
- 不要将持久化的 JSON 设置与启动时的临时参数混淆。
- `~/.gemini/antigravity-cli/bin/agentapi` 实际上是 `agy agentapi` 的简化包装版本。
- 在 WSL 环境下，令牌存储采用文件形式，因此认证问题通常属于本地文件或会话状态问题，而非仅限于浏览器的问题。
- 工作空间身份可能取决于启动目录以及 `.antigravitycli` 项目标识符。

## 验证方法

可通过 `terminal` 工具（使用 `read_file` 命令读取文件）来确认安装是否成功且可用：

1. `terminal(command="command -v agy")`
2. `terminal(command="agy --version")`
3. `terminal(command="agy help")`
4. `terminal(command="agy plugin list")`
5. 读取 `~/.gemini/antigravity-cli/settings.json` 文件
6. 读取最新的 `~/.gemini/antigravity-cli/log/cli-*.log` 日志文件
7. 如有需要，也可读取 `~/.gemini/antigravity-cli/keybindings.json` 文件

## 支持文档

- `references/cli-docs.md` — 汇集了入门指南、使用说明及功能文档中的核心内容。
