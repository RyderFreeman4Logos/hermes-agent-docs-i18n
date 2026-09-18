---
title: "Windows (Native) Guide"
description: "Run Hermes Agent natively on Windows 10 / 11 — install, feature matrix, UTF-8 console, Git Bash, gateway as a Scheduled Task, editor handling, PATH, uninstall, and common pitfalls"
sidebar_label: "Windows (Native)"
sidebar_position: 3
---

# Windows（原生版）使用指南

Hermes 可在 Windows 10 和 Windows 11 上以原生方式运行——无需 WSL、Cygwin 或 Docker。本页面将深入解析：哪些功能是原生支持的，哪些仅能在 WSL 环境下运行，安装程序实际执行了哪些操作，以及您可能需要调整的针对 Windows 的相关设置。

如果您只需进行安装，只需使用 [登录页](/) 或 [安装页面](../getting-started/installation#windows-native) 上提供的单行命令即可。若遇到任何意外情况，可返回此处查看说明。

:::提示 需要使用 WSL 吗？
如果您需要真正的 POSIX 环境（用于仪表板的嵌入式终端、`fork` 机制、Linux 风格的文件监控等功能），请参阅 **[Windows（WSL2）使用指南](./windows-wsl-quickstart.md)**。两种方式可以完美共存：原生版数据存储在 `%LOCALAPPDATA%\hermes` 目录下，而 WSL 版数据则存储在 `~/.hermes` 目录下。
:::

## 快速安装

打开 **PowerShell**（或 Windows Terminal），然后运行以下命令：

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

无需管理员权限。安装程序会将文件置于 `%LOCALAPPDATA%\hermes\` 目录中，并将 `hermes` 添加到您的**用户路径**中——安装完成后请打开一个新的终端窗口。

**安装程序选项**（需通过脚本块形式传递参数）：

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1))) -NoVenv -SkipSetup -Branch main
```

| 参数 | 默认值 | 用途 |
|---|---|---|
| `-Branch` | `main` | 克隆特定分支（适用于测试拉取请求） |
| `-Commit` | 未设置 | 将安装版本锁定到特定的提交 SHA 值（会覆盖 `-Branch` 参数） |
| `-Tag` | 未设置 | 将安装版本锁定到特定的 Git 标签（例如 `v0.14.0`） |
| `-NoVenv` | 关闭 | 跳过虚拟环境创建步骤（高级用法——需自行管理 Python 环境） |
| `-SkipSetup` | 关闭 | 跳过安装后的 `hermes setup` 设置向导 |
| `-HermesHome` | `%LOCALAPPDATA%\hermes` | 覆盖数据目录路径 |
| `-InstallDir` | `%LOCALAPPDATA%\hermes\hermes-agent` | 覆盖代码存放路径 |

安装程序会自动重试出现问题的 Git 数据获取操作，并会移除所有下载的 `install.ps1` 文件中的 BOM 标签，因此通过 HTTP 传输过程中附带的 UTF-8 BOM 标签不会再导致 `[scriptblock]::Create((irm ...))` 这种代码结构出错。

### 桌面版安装程序（可选）

此外还提供轻量级的 GUI 安装程序——如果您更喜欢双击 `.exe` 文件而非打开 PowerShell，那么这个选项非常实用。下载 Hermes Desktop 后运行安装程序，首次启动时 GUI 会底层调用 `install.ps1` 脚本来配置 Python（通过 `uv` 工具）、Node、PortableGit 以及下文所述的其余依赖项。首次运行之后，桌面应用程序与通过 PowerShell 安装的 `hermes` CLI 将共享同一个 `%LOCALAPPDATA%\hermes\hermes-agent` 安装目录和 `%LOCALAPPDATA%\hermes` 数据目录——您可以自由地在 GUI 和 CLI 之间切换使用。

如果您希望获得熟悉的 Windows 安装体验，或是将 Hermes 交给非开发人员使用，建议选用桌面版安装程序；而如果您已经在终端环境中，可直接使用 PowerShell 一键命令进行安装。

### 依赖项自动初始化（`dep_ensure`）

在首次启动时（或检测到缺失工具时），Hermes 会运行一个小型 Python 启动脚本——`hermes_cli/dep_ensure.py`——该脚本会检查并按需安装其所需的非 Python 依赖项。在 Windows 系统上，相关的依赖项包括：

| 依赖项 | Hermes 需要它的原因 |
|---|---|
| **PortableGit** | 为终端工具提供 `bash.exe`，并为会话内克隆操作提供 `git` 功能。该依赖项在安装时即被配置好，而非通过 `dep_ensure` 安装。 |
| **Node.js 26** | 浏览器工具（`agent-browser`）、TUI 的网页桥接组件以及 WhatsApp 桥接组件均需此版本。 |
| **ffmpeg** | 用于文本转语音/语音消息的音频格式转换。 |
| **ripgrep** | 快速搜索文件的功能；若该工具不可用，则会回退到 `grep`。 |
| **npm 包** | `agent-browser`、Playwright Chromium 以及各类工具集所需的 Node.js 依赖项，都将在首次使用浏览器工具时一次性安装。 |

每个依赖项都会经过类似 `shutil.which(...)` 的检查；如果某个二进制文件缺失且当前为交互式运行模式，`dep_ensure` 会提示用户进行安装（实际安装逻辑由 `scripts\install.ps1 -ensure <dep>` 负责处理）。在非交互式运行模式下（如网关、定时任务或无头桌面启动），系统不会弹出提示，而是直接显示“此功能需要 <dep>”的错误信息。

## 安装程序的实际功能

按从上到下的顺序，具体功能如下：

1. **启动 `uv`** —— Astral 提供的快速 Python 管理工具，安装路径为 `%USERPROFILE%\.local\bin`。  
2. **通过 `uv` 安装 Python 3.11**，无需预先安装任何 Python 版本。  
3. **安装 Node.js 26** —— 若系统支持则通过 winget 安装，否则会解压一个便携版 Node tarball 到 `%LOCALAPPDATA%\hermes\node` 目录。该版本用于浏览器工具及 WhatsApp 桥接功能。  
4. **安装便携版 Git** —— 若系统中已存在 PATH 路径下的 git，安装程序将直接使用；否则会从官方 `git-for-windows` 版本下载一个精简的独立版 **PortableGit**（大小约 45 MB），并保存至 `%LOCALAPPDATA%\hermes\git`。整个过程无需管理员权限，不会修改 Windows 安装程序注册表，也不会干扰系统中的其他程序。  
5. **将代码仓库克隆到 `%LOCALAPPDATA%\hermes\hermes-agent` 目录，并在其中创建一个虚拟环境**。  
6. **分级执行 `uv pip install` 操作** —— 首先尝试安装所有依赖 (`.[all]`)，若因 GitHub 限流导致某些 `git+https` 格式的依赖无法下载，则依次尝试安装规模更小的依赖组（`[messaging,dashboard,ext]` → `[messaging]` → `.`）。此机制可避免因单个依赖失败而导致整个系统只能以最基础状态运行的问题。  
7. **根据 `.env` 文件自动安装消息发送 SDK** —— 若文件中存在 `TELEGRAM_BOT_TOKEN`、`DISCORD_BOT_TOKEN`、`SLACK_BOT_TOKEN`、`SLACK_APP_TOKEN` 或 `WHATSAPP_ENABLED` 等变量，系统会先运行 `python -m ensurepip --upgrade` 升级 pip，再针对性地执行 `pip install` 命令，确保各平台的 SDK 都能正常被导入使用。  
8. **将 `HERMES_GIT_BASH_PATH` 设置为确定的 `bash.exe` 路径**，这样在每次启动新 shell 时，Hermes 都能准确找到该程序。
9. **将 `%LOCALAPPDATA%\hermes\bin` 添加到用户 PATH 环境变量，并设置 `HERMES_HOME=%LOCALAPPDATA%\hermes`**——这样在打开新终端后即可使用 `hermes` 命令（且该命令会指向你的数据目录）。只有 `hermes.exe` / `hermes-acp.exe` 启动程序会被复制到此 `bin` 目录中；而完整的 `venv\Scripts` 目录则被刻意**排除**在 PATH 之外，从而确保 Hermes 永远不会覆盖你本地的 `python` 命令。

10. **运行 `hermes setup`**——即常规的首次使用向导（用于配置模型、服务提供商及工具集）。如需跳过此步骤，可使用 `-SkipSetup` 参数。

:::提示：在 Windows 系统上跳过服务提供商查找流程
在 Windows 上，针对不同工具的 API 密钥配置（如 Firecrawl、FAL、浏览器使用功能、OpenAI TTS 等）是构建实用智能体的最大障碍。通过 [Nous Portal](/user-guide/features/tool-gateway) 订阅服务，只需一次 OAuth 登录即可同时管理模型及所有这些工具。安装程序完成后，运行 `hermes setup --portal` 即可完成全部配置。
:::

## 功能矩阵

除控制台内置的终端面板外，所有功能均在 Windows 系统上以原生方式运行。

| 功能 | 原生 Windows 环境 | WSL2 环境 |
|---|---|---|
| CLI（`hermes chat`、`hermes setup`、`hermes gateway` 等） | ✓ | ✓ |
| 交互式 TUI（`hermes --tui`） | ✓ | ✓ |
| 消息发送网关（Telegram、Discord、Slack、WhatsApp 及 15 种以上平台） | ✓ | ✓ |
| Cron 定时任务调度器 | ✓ | ✓ |
| 浏览器工具（通过 Node 运行 Chromium） | ✓ | ✓ |
| MCP 服务器（stdio 和 HTTP 协议） | ✓ | ✓ |
| 本地 Ollama / LM Studio / llama-server | ✓ | ✓（通过 WSL 网络连接） |
| Web 控制面板（会话管理、任务监控、指标展示及配置设置） | ✓ | ✓ |
| 控制面板的 `/chat` 标签页中的嵌入式终端窗格 | ✗（需要 POSIX PTY） | ✓ |
| 登录时自动启动 | ✓（使用 schtasks 工具） | ✓（使用 systemd 系统服务） |

控制面板的 `/chat` 标签页通过 POSIX PTY（`ptyprocess`）嵌入真实终端。原生 Windows 环境没有相应的底层机制；虽然可以使用 Python 的 `pywinpty` 或 Windows ConPTY 实现类似功能，但这属于独立的实现方案——暂计划在未来优化。**控制面板的其余功能在原生 Windows 环境下均可正常使用**，仅该标签页会显示“建议使用 WSL2”的提示。

## Hermes 在 Windows 上如何执行 Shell 命令

Hermes 的终端工具通过 **Git Bash** 来执行命令，这一方式与 Claude Code 的实现策略相同。这样无需为每个工具都重新编写代码，即可规避 POSIX 环境与 Windows 环境之间的差异。

`bash.exe` 的优先级解析顺序如下：

1. 若已设置，则使用 `HERMES_GIT_BASH_PATH` 环境变量。  
2. `%LOCALAPPDATA%\hermes\git\usr\bin\bash.exe`（由安装程序管理的 PortableGit）。  
3. `%LOCALAPPDATA%\hermes\git\bin\bash.exe`（旧版 Git-for-Windows 的路径结构）。  
4. 系统自带的 Git-for-Windows 安装版本（如 `%ProgramFiles%\Git\bin\bash.exe` 等）。  
5. 作为最后手段，可使用 MSYS2、Cygwin 或 PATH 中列出的任何 `bash.exe`。  

安装程序会明确设置 `HERMES_GIT_BASH_PATH`，这样新的 PowerShell 会话无需再次搜索。如果希望 Hermes 使用特定的 bash（例如系统自带的 Git Bash 或通过符号链接在 WSL 中运行的 bash），可自行覆盖该值。  

**注意事项：** MinGit 的路径结构与完整版的 Git-for-Windows 安装程序不同——其 bash 文件位于 `usr\bin\bash.exe` 而非 `bin\bash.exe`。Hermes 会同时检查这两个位置。如果手动解压 MinGit 的压缩包，请务必选择**不包含 busybox**的版本（即 `MinGit-*-64-bit.zip`，而非 `MinGit-*-busybox*.zip`）——基于 busybox 构建的版本会提供 `ash` 而非 `bash`，且大多缺少核心工具。  

## Windows 系统下的 UTF-8 控制台  

在 Windows 上，Python 的默认标准输入输出会使用控制台的当前代码页（通常为 cp1252 或 cp437）。而 Hermes 的标题栏、命令列表、工具信息、Rich 面板以及技能描述均包含 Unicode 字符。若不进行干预，这些内容将会因 `UnicodeEncodeError: 'charmap' codec can't encode character…` 错误而无法正常显示。  

解决此问题的方法在于 `hermes_cli/stdio.py::configure_windows_stdio()` 函数，该函数会在每个入口点（如 `cli.py::main`、`hermes_cli/main.py::main`、`gateway/run.py::main`）的早期被调用，其功能如下：

1. 通过 `kernel32.SetConsoleCP` / `SetConsoleOutputCP` 函数将控制台代码页切换为 CP_UTF8（65001）。  
2. 使用 `errors='replace'` 参数将 `sys.stdout` / `sys.stderr` / `sys.stdin` 重新配置为 UTF-8 编码。  
3. 通过 `setdefault` 设置 `PYTHONIOENCODING=utf-8` 和 `PYTHONUTF8=1`，确保子 Python 子进程也继承 UTF-8 编码（由于使用了 `setdefault`，用户的显式设置会优先生效）。  
4. 若未设置 `EDITOR` 或 `VISUAL`，则将 `EDITOR` 设置为 `notepad`（详情参见下文的编辑器部分）。  

该操作具有幂等性，在非 Windows 系统上不会产生任何影响。  

**可选禁用方式：** 在环境变量中设置 `HERMES_DISABLE_WINDOWS_UTF8=1`，即可恢复使用传统的 cp1252 输入输出方式。此设置有助于定位编码相关问题，但在正常使用情况下并不推荐启用。  

## 编辑器（`Ctrl-X Ctrl-E`、`/edit`）  

在版本 #21561 之前，Windows 系统上按下 `Ctrl-X Ctrl-E` 或输入 `/edit` 都不会产生任何反应。`prompt_toolkit` 使用硬编码的 POSIX 标准编辑器列表（如 `/usr/bin/nano`、`/usr/bin/pico`、`/usr/bin/vi` 等），即便已安装完整版的 Git for Windows，该列表在 Windows 上也始终无法被识别。  

Hermes 的 Windows 输入输出封装层现在默认将 `EDITOR` 设置为 `notepad`。Notepad 随每个 Windows 安装包一同提供，属于阻塞式编辑器——执行 `subprocess.call(["notepad", file])` 时会一直阻塞，直到窗口关闭为止。  

**用户的自定义设置仍会优先生效**（这些设置在 `setdefault` 之前就会被检查）：  

| 编辑器 | PowerShell 命令 |
|---|---|
| VS Code | `$env:EDITOR = "code --wait"` |
| Notepad++ | `$env:EDITOR = "'C:\Program Files\Notepad++\notepad++.exe' -multiInst -nosession"` |
| Neovim | `$env:EDITOR = "nvim"` |
| Helix | `$env:EDITOR = "hx"` |
VS Code 中的 `--wait` 参数至关重要——若不使用该参数，编辑器会立即返回，导致 Hermes 收到的是一个空的缓冲区。

请在您的 PowerShell 配置文件中永久设置该参数：

```powershell
# In $PROFILE
$env:EDITOR = "code --wait"
```

或者将其设置为系统设置中的用户环境变量，这样每个新启动的终端都会自动读取该设置。

## 在 CLI 中使用 `Ctrl+Enter` 作为换行键

Windows Terminal 会将 `Ctrl+Enter` 作为专用键序直接传递。Hermes 将其绑定为“插入换行符”的功能，因此你无需再通过 `Esc` 后再按 `Enter` 来编写多行命令提示符，从而在 CLI 中更便捷地操作。该功能适用于 Windows Terminal、VS Code 集成终端以及任何支持 VT 逃逸序列的现代 Windows 控制台程序。

在传统的 `cmd.exe` 控制台中，`Ctrl+Enter` 会简化为普通的 `Enter` 键——此时请使用 `Esc Enter` 组合键，或者升级到 Windows Terminal（它免费且已预装在 Windows 11 中）。

## 在 Windows 登录时运行网关

在 Windows 系统上执行 `hermes gateway install` 命令时，系统会通过“计划任务”功能实现自动启动，并提供启动文件夹作为备用方案——无需管理员权限。

### 安装

```powershell
hermes gateway install
```

底层工作原理：

1. 执行命令 `schtasks /Create /SC ONLOGON /RL LIMITED /TN Hermes_Gateway` —— 会注册一个在用户登录时运行的任务，该任务拥有标准权限（非管理员权限），且不会触发用户账户控制提示。
2. 若组策略阻止了使用 schtasks，系统则会退而求其次，在 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` 目录下创建一个名为 `Hermes_Gateway.vbs` 的小型启动脚本（通过 `wscript.exe` 以隐藏方式运行）。其效果与前述方法相同，但实现方式稍显粗糙。之所以选择 VBScript 而非 `cmd.exe` 快捷方式，是因为登录时分配的命令行窗口能够接收关闭事件，从而在网关启动完成之前将其终止。
3. 最终通过 `pythonw.exe`（而非 `python.exe`）以“分离进程”模式启动网关。`pythonw.exe` 没有关联任何命令行窗口，因此不会受到同级进程中发送的 `CTRL_C_EVENT` 信号的影响——这曾是一个实际问题，因为在同一进程组中按下 Ctrl+C 就会导致网关被强制关闭。

启动时使用的标志位包括：`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB`。

### 管理

```powershell
hermes gateway status      # Merged view: schtasks + Startup folder + running PID
hermes gateway start       # Starts the scheduled task now
hermes gateway stop        # Graceful SIGTERM equivalent (TerminateProcess via psutil)
hermes gateway restart
hermes gateway uninstall   # Removes schtasks entry, Startup shortcut, pid file
```

`hermes gateway status`命令是幂等的——即便连续调用上千次，也绝不会意外导致网关关闭。（在PR #21561之前，由于C层级的`os.kill(pid, 0)`操作与`CTRL_C_EVENT`信号发生冲突，该命令实际上会悄悄引发网关关闭；如需了解详细原因，请参阅下文的“进程管理机制”部分。）

### 为何不选择Windows服务？

Windows服务需要管理员权限才能安装，且会将网关的生命周期与机器启动绑定，而非用户登录状态。而普通Hermes用户希望的是：登录后网关立即可用，登出后网关立即消失。定时任务无需提升权限即可实现这一需求。如果确实需要使用服务，可以手动通过`nssm`或`sc create`命令来创建——但通常并无此必要。

## 数据结构

| 路径 | 内容 |
|---|---|
| `%LOCALAPPDATA%\hermes\hermes-agent\` | Git版本代码及虚拟环境。可安全地使用`Remove-Item -Recurse`命令删除后重新安装。 |
| `%LOCALAPPDATA%\hermes\git\` | PortableGit工具（仅当安装程序提供了该工具时存在）。 |
| `%LOCALAPPDATA%\hermes\node\` | 可移植版Node.js（仅当安装程序提供了该版本时存在）。 |
| `%LOCALAPPDATA%\hermes\bin\` | `hermes`/`hermes-acp`启动脚本，以及Hermes管理的`uv.exe`文件（用于更新操作的Python管理工具）。 |
| `%LOCALAPPDATA%\hermes\`（根目录） | 用户的配置文件、认证信息、技能设置、会话记录及日志文件（如`config.yaml`、`.env`、`skills\`、`sessions\`、`logs\`等）。**这些数据在重新安装后依然保留。** |
在原生 Windows 环境中，安装程序会将 `HERMES_HOME` 设置为 `%LOCALAPPDATA%\hermes`，因此您的数据文件与临时安装文件都存储在同一个 **%LOCALAPPDATA%\hermes** 目录下：安装/运行相关文件位于 `hermes-agent\`、`git\`、`node\` 和 `bin\` 这些子目录中，而您的数据文件则直接存放在 `%LOCALAPPDATA%\hermes` 中。重新安装时仅会替换 `hermes-agent\` 目录下的内容，因此您的数据依然保留——但由于两者共享同一个根目录，如果您希望保留数据，请勿使用 `Remove-Item -Recurse %LOCALAPPDATA%\hermes` 命令，而应直接删除 `hermes-agent\` 子目录。您的数据目录结构与 Linux 系统下的 `~/.hermes` 相同，因此可以在不同机器之间进行同步。

**覆盖 `HERMES_HOME` 变量：** 您可以设置该环境变量，指定不同的数据目录路径（例如设置为 `%USERPROFILE%\.hermes`，以匹配 Linux/WSL 的目录结构）。其使用方式与 Linux 系统相同。

## 浏览器工具

浏览器工具通过 `agent-browser`（一个 Node.js 辅助工具）来驱动 Chromium 引擎。在 Windows 环境下：

- 安装程序会通过 npm 将 `agent-browser` 添加到 PATH 环境变量中。
- `shutil.which("agent-browser", path=...)` 会自动定位到对应的 `.cmd` 包装脚本——由于 `CreateProcessW` 无法直接执行没有扩展名的脚本，因此 Hermes 会始终自动调用 `.CMD` 包装文件。请勿手动直接运行原始脚本，务必通过 `.cmd` 文件来启动程序。
- 首次运行时会自动安装 Playwright Chromium 版本（通过 `npx playwright install chromium` 命令完成）。如果安装失败，`hermes doctor` 工具会显示相关错误信息并给出解决方案建议。

## 在 Windows 上运行 Hermes —— 实用注意事项

### 安装后的 PATH 环境变量设置

安装程序会通过 `[Environment]::SetEnvironmentVariable` 函数将 `%LOCALAPPDATA%\hermes\bin` 添加到您的**用户 PATH** 环境变量中。现有的终端窗口不会自动识别该路径——请在安装完成后打开一个新的 PowerShell 窗口（或 Windows Terminal 标签页）。建议直接重新启动终端，除非您非常清楚自己在做什么，否则请勿手动执行 `$env:PATH += …` 这样的操作。

验证方法：

```powershell
Get-Command hermes        # should print C:\Users\<you>\AppData\Local\hermes\bin\hermes.exe
hermes --version
```

### 环境变量

Hermes 支持 `$env:X`（进程级）以及用户环境变量（永久性，可在“系统属性 → 环境变量”中设置）。通常的做法是将 API 密钥存储在 `%LOCALAPPDATA%\hermes\.env` 文件中（即您的 `HERMES_HOME` 目录），这一做法与 Linux 系统相同。

```
OPENROUTER_API_KEY=sk-or-...
TELEGRAM_BOT_TOKEN=...
```

除非您确实希望让所有 Windows 进程都能看到这些敏感信息，否则请勿将其放入用户环境变量中（这显然并非您想要的结果）。

### 仅适用于 Windows 的环境变量

这些变量仅影响原生 Windows 安装版本：

| 变量 | 效果 |
|---|---|
| `HERMES_GIT_BASH_PATH` | 覆盖 bash.exe 的自动检测功能。可指定任意版本的 bash——无论是完整的 Git-for-Windows、通过符号链接连接的 WSL bash、MSYS2 还是 Cygwin。安装程序会自动设置该变量。 |
| `HERMES_DISABLE_WINDOWS_UTF8` | 将其设置为 `1` 即可禁用 UTF-8 标准输入输出转换层，转而使用本地代码页。这对于定位编码相关错误非常有用。 |
| `EDITOR` / `VISUAL` | 用于指定执行 `/edit` 命令以及使用 `Ctrl-X Ctrl-E` 操作时的编辑器。如果这两个变量均未设置，Hermes 会默认使用 `notepad`。 |

## 卸载

通过 PowerShell：

```powershell
hermes uninstall
```

这就是彻底清除的方案——它会移除 schtasks 相关条目、启动文件夹中的快捷方式以及 `hermes.cmd` 伪装程序，同时删除 `%LOCALAPPDATA%\hermes\hermes-agent\` 目录，并修剪用户的 PATH 环境变量。此外，它还会保留 `%LOCALAPPDATA%\hermes\` 目录中的其他内容（如配置文件、认证信息、技能模块、会话记录及日志），以便日后重新安装时使用。

若要彻底清除所有内容：

```powershell
hermes uninstall
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes"
# Also remove a legacy CLI/WSL data dir if you ever used one:
Remove-Item -Recurse -Force "$env:USERPROFILE\.hermes"
```

`hermes uninstall` CLI子命令还能处理那种在旧版本安装中，任务项是以不同名称注册在`schtasks`中的情况——它会通过安装路径而非硬编码的任务名称来查找。

## 进程管理内部机制

这部分属于背景知识，除非你在调试“程序自动终止”之类的异常问题，否则可以跳过。

在Linux和macOS系统中，POSIX标准中的`os.kill(pid, 0)`实际上只是一种空操作，用于检查权限：“该进程ID对应的进程是否仍在运行？我是否有权限向它发送信号？”而在Windows系统中，Python的`os.kill`函数会将`sig=0`映射为`CTRL_C_EVENT`——由于整数值0存在冲突，该函数会通过`GenerateConsoleCtrlEvent(0, pid)`来发送Ctrl+C信号，进而影响包含目标进程ID的**整个控制台进程组**。这个问题最早出现在[bpo-14484](https://bugs.python.org/issue14484)中，至今仍未解决。因为修改这一机制可能会破坏那些依赖当前行为的脚本。

其后果是：在Windows系统中，任何通过`os.kill(pid, 0)`来“检查进程是否存活”的代码路径，实际上都在悄悄终止目标进程。Hermes已将所有这类代码（共14处，分布在11个文件中）替换为`gateway.status._pid_exists()`函数，该函数实际上调用的是`psutil.pid_exists()`——后者在Windows系统中通过`OpenProcess + GetExitCodeProcess`来实现进程状态检测，而不会发送任何信号。如果你正在编写插件或补丁，请直接使用`psutil.pid_exists()`或`gateway.status._pid_exists()`，切勿再使用`os.kill(pid, 0)`。

脚本 `scripts/check-windows-footguns.py` 会在持续集成流程中强制执行此规则：任何新的 `os.kill(pid, 0)` 调用都会导致“Windows 阻塞型脚枪检测”失败，除非该行带有 `# windows-footgun: ok — <reason>` 注解。

## 常见问题

**安装后立即出现“`hermes: command not found`”错误。**
请打开一个新的 PowerShell 窗口。安装程序已将 `%LOCALAPPDATA%\hermes\bin` 添加到用户的 PATH 环境变量中，但现有的终端窗口需要重新启动才能识别该路径。在此期间，您可以尝试运行 `& "$env:LOCALAPPDATA\hermes\bin\hermes.exe"`。

**运行工具时出现“`WinError 193: %1 is not a valid Win32 application`”错误。**
这是由于脚本中的命令行开头符被直接使用，从而绕过了 `.cmd` 适配层。Hermes 会通过 `shutil.which(cmd, path=local_bin)` 来解析命令，因此 PATH 环境变量的 PATHEXT 设置会优先识别 `.CMD` 扩展名——如果您是通过硬编码的路径来调用工具，请改用 `.cmd` 格式（例如使用 `npx.cmd` 而非 `npx`）。

**出现“`[scriptblock]::Create(...)` 失败：The assignment expression is not valid`”错误。**
您下载的 `install.ps1` 文件可能带有 UTF-8 BOM 标记。虽然 `irm | iex` 的执行方式会自动去除 BOM，但 `[scriptblock]::Create((irm ...))` 则不会。请重新使用简单的 `irm | iex` 方式执行，或者手动下载脚本，并通过 `[IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false))` 方法将其保存为不带 BOM 的格式。

**重启后网关无法持续运行。**  
请检查 `hermes gateway status` 命令——该命令会同时显示任务计划程序中的记录、启动文件夹中的快捷方式（如有使用）以及进程的实时 PID。如果任务计划程序已被注册但未处于运行状态，可能是组策略阻止了“登录时”触发。可运行 `schtasks /Query /TN Hermes_Gateway /V /FO LIST` 命令（若使用了命名配置文件，则为 `Hermes_Gateway_<profile>`）来查看任务失败的原因。只有当 `schtasks` 本身无法成功注册该任务时，才会自动启用启动文件夹作为备用方案；目前并无环境变量或开关可用于强制启用此功能。

**设置 `$env:EDITOR` 后，`/edit` 命令仍无反应。**  
该设置仅对当前进程有效；请关闭并重新打开终端，或是在“系统属性”→“环境变量”中将其设置为用户级变量。可在新的 PowerShell 窗口中运行 `echo $env:EDITOR` 命令进行验证。

**浏览器工具虽能启动，但相关操作会超时。**  
首次运行时会自动安装 Chromium。如果安装失败（可能是 GitHub 访问受限或 Playwright CDN 出现问题），请运行 `hermes doctor` 命令——该命令会指出缺失的 Chromium 并给出确切的 `npx playwright install chromium` 安装命令以便修复。

**`agent-browser` 因奇怪的 Node 版本错误而失败。**  
安装程序会将 Node 26 安装到 `%LOCALAPPDATA%\hermes\node` 目录中，但您的系统 PATH 可能会优先包含较旧版本的 Node 18。解决办法要么是将 Hermes 所在的 node 目录调整到 PATH 的更靠前位置，要么如果您在其他地方不使用 Node，则删除系统自带的 Node 安装版本。

**在 CLI 中，中文/日文/阿拉伯文字符会显示为 `?`。**
这是因为 UTF-8 标准输入输出封装模块并未被启用。请检查 `HERMES_DISABLE_WINDOWS_UTF8` 是否未被设置（可通过 `Get-ChildItem env:HERMES_DISABLE_WINDOWS_UTF8` 查看）。如果该变量为空但仍然出现 `?`，则可能是控制台主机（非常旧的 `cmd.exe`）完全不支持 UTF-8——建议切换到 Windows Terminal。

**网关无法发送 Telegram 图片——错误信息为“BadRequest: payload contains invalid characters”。**
此问题与 Windows 系统无关，但有时会首先在 Windows 环境中显现。这通常意味着 JSON 数据中的文件路径包含未转义的反斜杠。Telegram 应该接收的是 Hermes 已处理过的标准化路径，而非原始的 Windows 路径——如果在自定义插件中出现此问题，请确保传递的是 Hermes 提供的路径，而非用户输入通过 `str(Path(...))` 生成的路径。

**执行 `git pull` 后出现“在我的另一台机器上可以正常使用”的编码异常问题。**
如果您在 Windows 上使用非 UTF-8 编辑器（如旧版本 Windows 的记事本或某些中文输入法）编辑了 Hermes 配置文件或技能文件，该文件可能会带有 BOM 标记。Hermes 在读取大多数配置文件时能够容忍 `utf-8-sig` 标记，但若在折叠的 YAML 标量内容（如 `description: >`）中出现 BOM，则会悄悄导致 YAML 解析失败。请将文件重新保存为不含 BOM 的纯 UTF-8 格式。

## 接下来该做什么

- **[安装指南](../getting-started/installation.md)** — 完整的安装说明页面，涵盖 Linux/macOS/WSL2/Termux 环境。
- **[Windows (WSL2) 使用指南](./windows-wsl-quickstart.md)** — 适用于需要 POSIX 规范或控制台面板功能的用户。
- **[CLI 参考手册](../reference/cli-commands.md)** — 涵盖所有 `hermes` 子命令的详细说明。
- **[常见问题解答](../reference/faq.md)** — 针对非 Windows 环境的常见疑问。
- **[消息网关指南](./messaging/index.md)** — 在 Windows 上运行 Telegram/Discord/Slack 的相关说明。
