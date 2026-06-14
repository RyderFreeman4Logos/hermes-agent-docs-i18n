---
title: "Windows (Native) Guide"
description: "Run Hermes Agent natively on Windows 10 / 11 — install, feature matrix, UTF-8 console, Git Bash, gateway as a Scheduled Task, editor handling, PATH, uninstall, and common pitfalls"
sidebar_label: "Windows (Native)"
sidebar_position: 3
---

# Windows（原生版）使用指南

Hermes 可在 Windows 10 和 Windows 11 上以原生方式运行——无需 WSL、Cygwin 或 Docker。本页面将深入解析：哪些功能可原生运行，哪些功能仅能在 WSL 环境下使用，安装程序具体执行了哪些操作，以及您可能需要调整的针对 Windows 的相关设置。

如果您只是想进行安装，只需使用 [登录页](/) 或 [安装页面](../getting-started/installation#windows-native-powershell) 上提供的简短命令即可。如果遇到任何意外情况，欢迎返回此处查阅。

:::提示 需要使用 WSL 吗？
如果您需要真正的 POSIX 环境（用于仪表板的嵌入式终端、`fork` 机制、Linux 风格的文件监控等功能），请参阅 **[Windows（WSL2）使用指南](./windows-wsl-quickstart.md)**。两种方式可以共存且互不干扰：原生版数据存储在 `%LOCALAPPDATA%\hermes` 目录下，而 WSL 版数据则存储在 `~/.hermes` 目录下。
:::

## 快速安装

打开 **PowerShell**（或 Windows Terminal），然后运行以下命令：

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

无需管理员权限。安装程序会将文件放置到 `%LOCALAPPDATA%\hermes\` 目录中，并将 `hermes` 添加到您的**用户路径**中——安装完成后请打开一个新的终端窗口。

**安装程序选项**（需通过脚本块形式传递参数）：

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1))) -NoVenv -SkipSetup -Branch main
```

| 参数 | 默认值 | 用途 |
|---|---|---|
| `-Branch` | `main` | 克隆指定分支（适用于测试 Pull Request） |
| `-Commit` | 未设置 | 将安装固定到特定的提交 SHA 值（会覆盖 `-Branch` 参数） |
| `-Tag` | 未设置 | 将安装固定到特定的 Git 标签（例如 `v0.14.0`） |
| `-NoVenv` | 关闭 | 跳过虚拟环境创建步骤（高级用法——需自行管理 Python 环境） |
| `-SkipSetup` | 关闭 | 跳过安装后的 `hermes setup` 向导 |
| `-HermesHome` | `%LOCALAPPDATA%\hermes` | 覆盖数据目录路径 |
| `-InstallDir` | `%LOCALAPPDATA%\hermes\hermes-agent` | 覆盖代码安装路径 |

安装程序会自动重试可能失败的 git 获取操作，并移除任何下载的 `install.ps1` 文件中的 BOM 标签，因此通过 HTTP 传输时附带的 UTF-8 BOM 再也不会导致 `[scriptblock]::Create((irm ...))` 语句出错。

### 桌面版安装程序（可选）

还提供了一个轻量级的 GUI 安装程序——如果您更愿意双击 `.exe` 文件而非打开 PowerShell，那么这个选项非常实用。下载 Hermes Desktop 后运行安装程序，首次启动时 GUI 会底层调用 `install.ps1` 脚本来安装 Python（通过 `uv` 工具）、Node、PortableGit 以及下文所述的其余依赖项。首次运行之后，桌面应用与通过 PowerShell 安装的 `hermes` CLI 将共享同一个 `%LOCALAPPDATA%\hermes\hermes-agent` 安装目录和 `%LOCALAPPDATA%\hermes` 数据目录——您可以自由地在 GUI 和 CLI 之间切换。

当您希望获得熟悉的 Windows 安装体验，或需将 Hermes 授予非开发者使用时，请使用桌面版安装程序；而如果您已经在终端环境中操作，则可直接使用 PowerShell 一键命令安装。

### 依赖项自动初始化（`dep_ensure`）

在首次启动时（或在检测到缺失工具时），Hermes 会运行一个小型 Python 启动脚本——`hermes_cli/dep_ensure.py`——该脚本会检查并按需安装所需的非 Python 依赖项。在 Windows 系统上，相关的依赖项包括：

| 依赖项 | Hermes 需要它的原因 |
|---|---|
| **PortableGit** | 为终端工具提供 `bash.exe`，并为即时克隆操作提供 `git` 命令。该工具在安装时即被安装，而非通过 `dep_ensure` 自动安装。 |
| **Node.js 22** | 浏览器工具（`agent-browser`）、TUI 的网页桥接组件以及 WhatsApp 桥接功能均需此版本。 |
| **ffmpeg** | 用于文本转语音/语音消息的音频格式转换。 |
| **ripgrep** | 快速文件搜索工具——若该工具不可用，则会回退到 `grep`。 |
| **npm 包** | `agent-browser`、Playwright Chromium 以及各类工具集所需的 Node 依赖项，都将在首次使用浏览器工具时一次性安装。 |

每个依赖项都会经过类似 `shutil.which(...)` 的检查；如果某个二进制文件缺失且当前为交互式运行模式，`dep_ensure` 会提示用户进行安装（实际安装逻辑则由 `scripts\install.ps1 -ensure <dep>` 负责）。非交互式运行模式（如网关服务、定时任务、无界面桌面启动）则会跳过提示，直接显示“此功能需要 <dep>”的错误信息。

## 安装程序的实际执行流程

按顺序依次执行以下步骤：

1. **初始化 `uv`**——Astral 开发的快速 Python 管理工具。该工具会被安装到 `%USERPROFILE%\.local\bin` 目录下。
2. 通过 `uv` 安装 Python 3.11。无需预先安装 Python。
3. 安装 Node.js 22（优先使用 winget 安装，若不可用则解压便携版 Node tarball 到 `%LOCALAPPDATA%\hermes\node` 目录）。该版本用于浏览器工具和 WhatsApp 桥接功能。
4. 安装便携版 Git——如果系统中已有 `git` 可用，安装程序会直接使用它；否则会下载一个精简版的自包含 **PortableGit**（约 45 MB，来自官方的 `git-for-windows` 发行版），并安装到 `%LOCALAPPDATA%\hermes\git` 目录。整个安装过程无需管理员权限，也不会修改 Windows 安装程序注册表，更不会干扰系统中的其他组件。
5. 将代码仓库克隆到 `%LOCALAPPDATA%\hermes\hermes-agent` 目录，并在其中创建一个虚拟环境。
6. 分层执行 `uv pip install` 操作——首先尝试安装所有依赖项（`.[all]`），如果通过 `git+https` 方式获取的依赖项在 GitHub 限流时出现问题，会依次尝试更小的依赖集（`[messaging,dashboard,ext]` → `[messaging]` → `.`）。这种设计可避免因单个依赖问题导致整个安装失败。
7. 根据 `.env` 文件中的配置自动安装消息发送 SDK——如果文件中存在 `TELEGRAM_BOT_TOKEN` / `DISCORD_BOT_TOKEN` / `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` / `WHATSAPP_ENABLED` 等变量，程序会运行 `python -m ensurepip --upgrade` 以及针对性的 `pip install` 命令，确保各平台的 SDK 都能被正确导入。
8. 将 `HERMES_GIT_BASH_PATH` 设置为已确定的 `bash.exe` 路径，这样在新建的 PowerShell shell 中，Hermes 总能准确找到该程序。
9. 将 `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts` 添加到用户 PATH 环境变量中，并设置 `HERMES_HOME=%LOCALAPPDATA%\hermes`——这样在打开新终端后，即可使用 `hermes` 命令，并且该命令会指向您指定的数据目录。
10. 运行 `hermes setup` ——即常规的首次运行向导，用于配置模型、服务提供商及工具集。如需跳过此步骤，可使用 `-SkipSetup` 参数。

:::提示：在 Windows 上跳过服务提供商配置
在 Windows 系统上，为各类工具配置 API 密钥（如 Firecrawl、FAL、浏览器功能、OpenAI TTS 等）是构建可用智能体的最大障碍。通过 [Nous Portal](/user-guide/features/tool-gateway) 订阅服务，只需一次 OAuth 登录即可同时使用模型及所有这些工具。安装程序完成后，运行 `hermes setup --portal` 即可完成所有配置。
:::

## 功能矩阵

除仪表板内置的终端面板外，所有功能均在 Windows 上原生运行。

| 功能 | 原生 Windows 版 | WSL2 版 |
|---|---|---|
| CLI 命令（如 `hermes chat`、`hermes setup`、`hermes gateway` 等） | ✓ | ✓ |
| 交互式 TUI（通过 `hermes --tui` 启动） | ✓ | ✓ |
| 消息发送网关（支持 Telegram、Discord、Slack、WhatsApp 及 15 种以上平台） | ✓ | ✓ |
| 定时任务调度器 | ✓ | ✓ |
| 浏览器工具（通过 Node 运行 Chromium） | ✓ | ✓ |
| MCP 服务器（支持标准输入/输出及 HTTP 协议） | ✓ | ✓ |
| 本地 Ollama / LM Studio / llama-server 等模型 | ✓ | ✓（通过 WSL 网络访问） |
| Web 仪表板（用于查看会话、任务、指标及配置信息） | ✓ | ✓ |
| 仪表板中的 `/chat` 内置终端面板 | ✗（需要 POSIX 类型的终端设备） | ✓ |
| 登录时自动启动 | ✓（通过 schtasks 定时任务实现） | ✓（通过 systemd 系统服务实现） |

仪表板的 `/chat` 标签页通过 POSIX 类型的终端设备（`ptyprocess`）嵌入真实终端。原生 Windows 并没有类似的底层机制；虽然可以使用 Python 的 `pywinpty` 或 Windows ConPTY 实现类似功能，但属于独立实现方案——目前仍在开发中。**除该标签页外，仪表板的其余功能均在 Windows 上原生运行**，仅会在该标签页显示“建议使用 WSL2”的提示。

## Hermes 在 Windows 上如何执行 Shell 命令

Hermes 的终端工具通过 **Git Bash** 来执行命令，这一方式与 Claude Code 的实现策略相同。这样无需为每个工具都重新编写代码，即可解决 POSIX 系统与 Windows 系统之间的兼容性问题。

查找 `bash.exe` 的优先级顺序如下：

1. 若已设置 `HERMES_GIT_BASH_PATH` 环境变量，则优先使用该路径指定的路径。
2. 安装程序自带的 PortableGit 所在路径：`%LOCALAPPDATA%\hermes\git\usr\bin\bash.exe`。
3. 旧版 Git-for-Windows 的安装路径：`%LOCALAPPDATA%\hermes\git\bin\bash.exe`。
4. 系统自带的 Git-for-Windows 安装路径（如 `%ProgramFiles%\Git\bin\bash.exe` 等）。
5. 最后才尝试 PATH 环境变量中列出的 MSYS2、Cygwin 或其他版本的 `bash.exe`。

安装程序会明确设置 `HERMES_GIT_BASH_PATH`，这样新创建的 PowerShell shell 就无需再次搜索。如果希望 Hermes 使用特定的 bash 版本，也可以自行覆盖该环境变量——例如，可以使用系统自带的 Git Bash，或通过符号链接指向 WSL 中的 bash 版本。

**需要注意的一点是**：MinGit 的目录结构与完整版的 Git-for-Windows 不同——其 `bash.exe` 位于 `usr\bin\bash.exe` 而非 `bin\bash.exe`。Hermes 会同时检查这两个路径。如果您手动解压 MinGit 的压缩包，请确保选择**不包含 busybox**的版本（即 `MinGit-*-64-bit.zip`，而非 `MinGit-*-busybox*.zip`）——因为带有 busybox 的版本会提供 `ash` 而非 `bash`，且缺少大部分核心工具。

## Windows 系统下的 UTF-8 控制台问题

在 Windows 上，Python 的默认标准输入/输出使用的是控制台的当前代码页（通常为 cp1252 或 cp437）。而 Hermes 的标题栏、命令行列表、工具信息、Rich 面板以及技能描述等内容均包含 Unicode 字符。如果不进行特殊处理，这些内容会因编码问题导致 `UnicodeEncodeError: 'charmap' codec can't encode character…` 错误。

解决该问题的代码位于 `hermes_cli/stdio.py::configure_windows_stdio()` 函数中，该函数会在每个程序入口点（如 `cli.py::main`、`hermes_cli/main.py::main`、`gateway/run.py::main`）的早期被调用。它的功能包括：

1. 通过 `kernel32.SetConsoleCP` / `SetConsoleOutputCP` 函数将控制台代码页更改为 CP_UTF8（即 65001 编码）。
2. 将 `sys.stdout`、`sys.stderr` 和 `sys.stdin` 的编码方式设置为 UTF-8，并启用 `errors='replace'` 错误处理策略。
3. 设置 `PYTHONIOENCODING=utf-8` 和 `PYTHONUTF8=1`（通过 `setdefault` 函数设置，因此用户手动指定的值会优先生效），确保子进程中的 Python 也使用 UTF-8 编码。
4. 如果未设置 `EDITOR` 或 `VISUAL` 环境变量，则将 `EDITOR` 设置为 `notepad`（具体设置方式见下文的编辑器部分）。

该函数是可重复安全的——在非 Windows 系统上不会产生任何影响。

**可选关闭此功能**：在环境变量中设置 `HERMES_DISABLE_WINDOWS_UTF8=1`，即可恢复使用旧的 cp1252 编码方式。此设置适用于排查编码问题，但在正常使用情况下不建议启用。

## 编辑器选择（通过 `Ctrl-X Ctrl-E` 或 `/edit` 命令）

在版本 #21561 之前，Windows 系统上按下 `Ctrl-X Ctrl-E` 或输入 `/edit` 命令均不会产生任何效果。`prompt_toolkit` 库内置了硬编码的 POSIX 风格命令行编辑器列表（如 `/usr/bin/nano`、`/usr/bin/pico`、`/usr/bin/vi` 等），但这些命令在 Windows 上根本无法使用——即便已安装完整的 Git for Windows 也是如此。

Hermes 的 Windows 版标准输入/输出适配层现在默认将 `EDITOR` 设置为 `notepad`。Notepad 是所有 Windows 安装版都自带的编辑器，属于阻塞式编辑器——调用 `subprocess.call(["notepad", file])` 会一直阻塞，直到该窗口被关闭为止。

**用户自定义的编辑器设置仍然有效**（这些设置会在使用 `setdefault` 之前被优先处理）：

| 编辑器 | PowerShell 命令 |
|---|---|
| VS Code | `$env:EDITOR = "code --wait"` |
| Notepad++ | `$env:EDITOR = "'C:\Program Files\Notepad++\notepad++.exe' -multiInst -nosession"` |
| Neovim | `$env:EDITOR = "nvim"` |
| Helix | `$env:EDITOR = "hx"` |

VS Code 中的 `--wait` 参数非常重要——如果没有该参数，编辑器会立即返回，导致 Hermes 收到空的缓冲区内容。

您可以在自己的 PowerShell 配置文件中永久设置该值：

```powershell
# In $PROFILE
$env:EDITOR = "code --wait"
```

或者将其设置为系统设置中的用户环境变量，这样每个新启动的终端都会自动读取该设置。

## 在 CLI 中使用 `Ctrl+Enter` 作为换行键

Windows Terminal 会将 `Ctrl+Enter` 作为专用的键序直接传递。Hermes 将其绑定为“插入换行符”的功能，因此你无需再通过先按 `Esc` 再按 `Enter` 的方式来编写多行命令提示符。该功能在 Windows Terminal、VS Code 集成终端以及任何支持 VT 逃逸序列的现代 Windows 控制台环境中均可使用。

在传统的 `cmd.exe` 控制台中，`Ctrl+Enter` 会简化为普通的 `Enter` 键——此时请使用 `Esc Enter` 组合键，或者升级到 Windows Terminal（它免费且已预装在 Windows 11 系统中）。

## 在 Windows 登录时运行网关

在 Windows 上执行 `hermes gateway install` 命令时会利用**计划任务**功能，并默认使用启动文件夹作为备用方案——无需管理员权限。

### 安装

```powershell
hermes gateway install
```

底层工作原理：

1. `schtasks /Create /SC ONLOGON /RL LIMITED /TN HermesGateway` —— 会注册一个在用户登录时运行的任务，该任务拥有标准权限（非管理员权限），且不会触发用户账户控制提示。
2. 若组策略阻止了使用 `schtasks`，则会回退为将快捷方式 `start /min cmd.exe /d /c <wrapper>` 写入 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` 目录。效果相同，但实现方式较为粗糙。
3. 通过 `pythonw.exe`（而非 `python.exe`）以**分离模式**启动网关。`pythonw.exe` 没有附加控制台，因此能够避免受到同级进程发送的 `CTRL_C_EVENT` 信号影响（这曾是一个实际问题，当在同一进程组中按下 Ctrl+C 时会导致网关崩溃）。

启动时使用的标志：`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW | CREATE_BREAKAWAY_FROM_JOB`。

### 管理

```powershell
hermes gateway status      # Merged view: schtasks + Startup folder + running PID
hermes gateway start       # Starts the scheduled task now
hermes gateway stop        # Graceful SIGTERM equivalent (TerminateProcess via psutil)
hermes gateway restart
hermes gateway uninstall   # Removes schtasks entry, Startup shortcut, pid file
```

`hermes gateway status` 是幂等操作——即便连续调用上千次，也绝不会意外导致网关关闭。（在 PR #21561 之前，由于 C 层的 `os.kill(pid, 0)` 与 `CTRL_C_EVENT` 发生冲突，该命令实际上会悄悄引发网关关闭；如想了解详细情况，请参阅下文的“进程管理内部机制”部分。）

### 为何不使用 Windows 服务？

服务需要管理员权限才能安装，且会将网关的生命周期绑定到机器启动而非用户登录事件。而典型的 Hermes 用户希望实现的是：登录后网关立即可用，登出后网关立即消失。计划任务无需提升权限即可实现这一功能。如果确实需要使用服务，可以手动通过 `nssm` 或 `sc create` 来创建——但通常没这个必要。

## 数据结构

| 路径 | 内容 |
|---|---|
| `%LOCALAPPDATA%\hermes\hermes-agent\` | Git 检出代码及虚拟环境。`venv\Scripts\hermes.exe` 是被添加到用户 PATH 中的可执行文件。可以安全地使用 `Remove-Item -Recurse` 命令删除后重新安装。 |
| `%LOCALAPPDATA%\hermes\git\` | PortableGit（仅当安装程序提供了该工具时存在）。 |
| `%LOCALAPPDATA%\hermes\node\` | Portable Node.js（仅当安装程序提供了该工具时存在）。 |
| `%LOCALAPPDATA%\hermes\bin\` | Hermes 自带的 `uv.exe`（用于更新操作的 Python 管理工具）。 |
| `%LOCALAPPDATA%\hermes\`（根目录） | 包含用户的配置文件、认证信息、技能模块、会话记录及日志文件（如 `config.yaml`、`.env`、`skills\`、`sessions\`、`logs\` 等）。**即使重新安装也不会丢失。** |

在原生 Windows 环境下，安装程序会将 `HERMES_HOME` 设置为 `%LOCALAPPDATA%\hermes`，因此用户数据与临时安装文件都存储在同一个 **%LOCALAPPDATA%\hermes** 根目录下：安装/运行相关的文件位于 `hermes-agent\`、`git\`、`node\` 和 `bin\` 子目录中，而用户数据文件则直接存放在 `%LOCALAPPDATA%\hermes` 中。重新安装时只会替换 `hermes-agent\` 目录下的代码，因此用户数据依然保留——但由于两者共享同一个根目录，若希望保留数据，请勿使用 `Remove-Item -Recurse %LOCALAPPDATA%\hermes` 命令，而应直接删除 `hermes-agent\` 子目录。该数据目录的结构与 Linux 系统下的 `~/.hermes` 相同，因此可以在不同机器之间同步数据。

**覆盖 `HERMES_HOME` 变量：** 可将此环境变量设置为指向其他数据目录（例如 `%USERPROFILE%\.hermes`，以匹配 Linux/WSL 的目录结构）。其使用方式与 Linux 系统相同。

## 浏览器工具

浏览器工具通过 `agent-browser`（一个 Node.js 辅助工具）来驱动 Chromium 引擎。在 Windows 环境下：

- 安装程序会通过 npm 将 `agent-browser` 添加到 PATH 中。
- `shutil.which("agent-browser", path=...)` 会自动定位到对应的 `.cmd` 包装脚本——由于 `CreateProcessW` 无法直接执行没有扩展名的脚本文件，因此 Hermes 总是会找到 `.CMD` 包装版本。请勿手动调用原始脚本，始终通过 `.cmd` 文件来启动工具。
- 首次运行时会自动安装 Playwright Chromium 版本的 Chromium 引擎（通过 `npx playwright install chromium` 命令）。如果安装失败，`hermes doctor` 工具会提示问题并给出解决方案。

## 在 Windows 上运行 Hermes —— 实用注意事项

### 安装后的 PATH 设置

安装程序会通过 `[Environment]::SetEnvironmentVariable` 方法将 `%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts` 添加到用户的 **用户 PATH** 中。现有的终端窗口不会自动识别这一变化——建议在安装完成后打开一个新的 PowerShell 窗口（或 Windows Terminal 标签页）。只需重新打开终端即可，无需手动执行 `$env:PATH += …` 这类操作，除非你确定自己知道正在做什么。

验证方法：

```powershell
Get-Command hermes        # should print C:\Users\<you>\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe
hermes --version
```

### 环境变量

Hermes 支持 `$env:X`（进程级）以及用户环境变量（永久性，可在“系统属性 → 环境变量”中设置）。通常的做法是将 API 密钥存储在 `%LOCALAPPDATA%\hermes\.env` 文件中（即您的 `HERMES_HOME` 目录），这一方式与 Linux 系统相同。

```
OPENROUTER_API_KEY=sk-or-...
TELEGRAM_BOT_TOKEN=...
```

除非您确实希望让所有 Windows 进程都能看到这些敏感信息，否则请勿将其放入用户环境变量中（这显然并非您想要的结果）。

### 仅适用于 Windows 的环境变量

这些变量仅影响原生 Windows 安装版本：

| 变量名 | 效果 |
|---|---|
| `HERMES_GIT_BASH_PATH` | 覆盖 bash.exe 的自动检测机制。可指定任意版本的 bash——无论是完整的 Git-for-Windows、通过符号链接连接的 WSL bash、MSYS2 还是 Cygwin。安装程序会自动设置该变量。 |
| `HERMES_DISABLE_WINDOWS_UTF8` | 设置为 `1` 即可禁用 UTF-8 标准输入输出支持，转而使用本地代码页。这对于定位编码相关故障非常有用。 |
| `EDITOR` / `VISUAL` | 用于指定执行 `/edit` 命令以及使用 `Ctrl-X Ctrl-E` 操作时的编辑器。如果这两个变量均未设置，Hermes 将默认使用 `notepad`。 |

## 卸载

通过 PowerShell：

```powershell
hermes uninstall
```

这就是彻底清理的方式——它会移除 schtasks 相关条目、启动文件夹中的快捷方式以及 `hermes.cmd` 伪程序，删除 `%LOCALAPPDATA%\hermes\hermes-agent\` 目录，并修剪用户的 PATH 环境变量。同时，它会保留 `%LOCALAPPDATA%\hermes\` 目录中的其他内容（如配置文件、认证信息、技能模块、会话记录及日志），以便日后重新安装时使用。

若要彻底清除所有痕迹：

```powershell
hermes uninstall
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes"
# Also remove a legacy CLI/WSL data dir if you ever used one:
Remove-Item -Recurse -Force "$env:USERPROFILE\.hermes"
```

`hermes uninstall` CLI子命令还能处理那种在旧版本安装中，任务条目是以不同名称注册在`schtasks`中的情况——它会通过安装路径而非硬编码的任务名称来查找。

## 进程管理内部机制

这部分属于背景知识——除非你在调试“程序自动崩溃”之类的异常问题，否则可以跳过。

在Linux和macOS系统中，POSIX标准中的`os.kill(pid, 0)`实际上只是一种无实际作用的权限检查：“该进程ID对应的进程是否仍在运行？我是否有权限向它发送信号？”而在Windows系统中，Python的`os.kill`函数会将`sig=0`映射为`CTRL_C_EVENT`——由于整数0被重复使用，这就导致了冲突——随后会通过`GenerateConsoleCtrlEvent(0, pid)`函数将Ctrl+C信号广播到包含目标进程ID的**整个控制台进程组**。这个问题最早出现在[ bpo-14484](https://bugs.python.org/issue14484)中，至今已有20年的历史。由于修改这一机制会破坏那些依赖当前行为的脚本，因此它至今仍未得到修复。

其后果是：在Windows系统中，任何通过`os.kill(pid, 0)`来“检查进程是否存活”的代码路径，实际上都在悄悄地终止目标进程。Hermes已将所有这类代码（共14处，分布在11个文件中）替换为`gateway.status._pid_exists()`函数，该函数会调用`psutil.pid_exists()`——而后者在Windows系统中则是通过`OpenProcess + GetExitCodeProcess`来实现，不会发送任何信号。如果你正在编写插件或补丁，请直接使用`psutil.pid_exists()`或`gateway.status._pid_exists()`，绝对不要使用`os.kill(pid, 0)`。

`scripts/check-windows-footguns.py`文件在持续集成流程中会对这一规则进行强制检查：任何新的`os.kill(pid, 0)`调用都会导致“Windows致命错误（阻塞型）”检测失败，除非该行代码前有`# windows-footgun: ok — <reason>`这样的注释标记。

## 常见问题

**安装完成后立即出现“`hermes: command not found`”错误。**
请打开一个新的PowerShell窗口。安装程序虽然已将`%LOCALAPPDATA%\hermes\bin`路径添加到了用户的PATH环境变量中，但现有的命令壳需要重新启动才能识别该路径。在此期间，你可以直接运行`& "$env:LOCALAPPDATA\hermes\bin\hermes.cmd"`来启动Hermes。

**运行某个工具时出现“`WinError 193: %1 is not a valid Win32 application`”错误。**
这是因为你调用的脚本使用了shebang行，从而绕过了`.cmd`封装脚本。Hermes是通过`shutil.which(cmd, path=local_bin)`来解析命令的，因此PATH环境变量中的PATHEXT设置会识别`.CMD`扩展名——如果你直接使用硬编码的路径来调用工具，请改用带有`.cmd`扩展名的版本（例如使用`npx.cmd`而非`npx`）。

**出现“`[scriptblock]::Create(...)`失败，提示‘The assignment expression is not valid’”错误。**
你下载的`install.ps1`脚本可能带有UTF-8字节顺序标记（BOM）。虽然`irm | iex`这种调用方式会自动去除BOM，但`[scriptblock]::Create((irm ...))`则不会。请重新使用简单的`irm | iex`方式来执行脚本，或者手动下载脚本，并通过`[IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false))`将文件保存为不带BOM的格式。

**重启后Gateway服务无法继续运行。**
请运行`hermes gateway status`命令查看状态——该命令会综合显示`schtasks`中的任务记录、启动文件夹中的快捷方式（如果使用了的话）以及当前进程的PID信息。如果`schtasks`中已注册了任务但服务并未启动，可能是组策略阻止了“ONLOGON”触发事件。你可以运行`schtasks /Query /TN HermesGateway /V /FO LIST`来查看任务失败的原因，或者通过设置`HERMES_GATEWAY_FORCE_STARTUP=1`参数，以重新安装的方式强制让服务在启动时立即运行。

**设置了`$
