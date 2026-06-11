# Antigravity CLI文档精简版

已查阅的源页面：
- `/docs/cli-getting-started`
- `/docs/cli-using`
- `/docs/cli-features`

## 安装
- macOS/Linux：`curl -fsSL https://antigravity.google/cli/install.sh | bash`
- Windows PowerShell：`irm https://antigravity.google/cli/install.ps1 | iex`
- Windows CMD：`curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && install.cmd && del install.cmd`

## 认证
- 首先尝试使用安全密钥环进行认证。
- 若未保存会话，则回退到基于浏览器的Google登录方式。
- 本地机器：自动打开默认浏览器。
- SSH/远程环境：会显示一个安全的授权URL，随后需要用户粘贴授权码。
- 使用`/logout`可删除已保存的凭证。

## 配置与文件
- 设置文件：`~/.gemini/antigravity-cli/settings.json`
- 绑定配置：`~/.gemini/antigravity-cli/keybindings.json`
- 插件目录：`~/.gemini/antigravity-cli/plugins/<plugin_name>/`

## 常用命令
- `/config`, `/settings`
- `/permissions`
- `/resume` / `/switch`
- `/rewind` / `/undo`
- `/rename <name>`
- `/model`
- `/keybindings`
- `/statusline`
- `/tasks`
- `/skills`
- `/mcp`
- `/open <path>`
- `/usage`
- `/logout`
- `/agents`

## 提示符辅助功能
- `@`：路径自动补全
- `esc esc`：非流式模式下清除提示符
- `!`：执行终端命令
- `?`：显示帮助信息或命令列表

## 权限与沙箱机制
- 权限模式：`request-review`、`always-proceed`、`strict`、`proceed-in-sandbox`
- 启动时覆盖选项：`--sandbox`、`--dangerously-skip-permissions`
- 沙箱设置：在`settings.json`中配置`enableTerminalSandbox`（默认值为`false`）

## 插件
- 插件可整合技能、智能体、规则、MCP服务器及钩子功能。
- 它们会先存储在本地，安装完成后会自动被识别。

## 子智能体
- 使用`/agents`可查看正在运行或已完成的子智能体。
- 子智能体可并行执行，并能请求批准。

## 绑定配置
- 配置文件位于`~/.gemini/antigravity-cli/keybindings.json`
- 若JSON格式错误，无法执行的操作将回退到默认设置。
- 文档中列出了“clear”、“submit”、“cancel”、“exit”、“suspend”、“editor”、“approval yes/no”、“navigation”、“clipboard”、“undo/redo”以及“换行插入”等操作的默认绑定配置。
