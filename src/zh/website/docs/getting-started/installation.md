---
sidebar_position: 2
title: "Installation"
description: "Install Hermes Agent on Linux, macOS, WSL2, native Windows, or Android via Termux"
---

# 安装

只需两分钟即可让 Hermes Agent 开始运行！

:::提示 平台支持情况
如需查看完整的平台支持列表（包括支持的操作系统、分发方式以及平台限定功能），请参阅 **[平台支持](./platform-support.md)**。
:::

## 快速安装
### 使用 macOS 或 Windows 版的 Hermes Desktop 安装程序（推荐）
如需轻松安装命令行工具和桌面应用程序，请从我们的网站 [下载 Hermes Desktop 安装程序](https://hermes-agent.nousresearch.com/) 并运行它。

### 不使用 Hermes Desktop：
如需仅安装命令行版本而无需 Hermes Desktop，请执行以下操作：

#### Linux / macOS / WSL2 / Android (Termux)
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

#### Windows（原生版）

在 PowerShell 中运行：
```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1) 
```

如果在仅通过命令行完成安装后想要继续安装并运行 Hermes Desktop，只需直接运行相应命令即可。
```bash
hermes desktop
```

### 安装程序的功能

安装程序会自动处理所有相关任务——包括所有依赖项（Python、Node.js、ripgrep、ffmpeg）、代码库克隆、虚拟环境创建、全局 `hermes` 命令配置，以及大语言模型提供者的设置。一切准备就绪后，您即可开始对话。

#### 安装路径布局

安装程序将各种文件放置的位置取决于您是以普通用户身份还是以 root 身份进行安装：

| 安装方式                     | 代码存储位置                  | `hermes` 可执行文件                     | 数据目录                           |
| ---------------------------- | ------------------------------ | --------------------------------------- | ------------------------------------ |
| 按用户配置（git 安装方式）     | `~/.hermes/hermes-agent/`      | `~/.local/bin/hermes`（符号链接）         | `~/.hermes/`                         |
| root 模式（使用 `sudo curl … \| sudo bash`） | `/usr/local/lib/hermes-agent/` | `/usr/local/bin/hermes`                 | `/root/.hermes/`（或 `$HERMES_HOME`） |

root 模式采用的 **FHS 路径布局**（`/usr/local/lib/…`、`/usr/local/bin/hermes`）与 Linux 系统中其他全局开发者工具的存储位置一致。这种做法适用于需要为所有用户提供统一系统安装的共享机器部署场景。而与身份相关的配置（认证信息、技能、会话等）仍保存在每个用户的 `~/.hermes/` 目录下，或用户指定的 `HERMES_HOME` 路径中。

### 安装完成后

请重新加载Shell环境，然后即可开始对话：

```bash
source ~/.bashrc   # or: source ~/.zshrc
hermes             # Start chatting!
```

如需日后重新配置各项设置，可使用专用命令：

```bash
hermes model          # Choose your LLM provider and model
hermes tools          # Configure which tools are enabled
hermes gateway setup  # Set up messaging platforms
hermes config set     # Set individual config values
hermes config get     # Inspect individual config values
hermes setup          # Or run the full setup wizard to configure everything at once
```

:::提示 最快捷的途径：Nous Portal  
一个订阅即可使用300多种模型，同时还包含[工具网关](/user-guide/features/tool-gateway)（网页搜索、图像生成、文本转语音、云浏览器）功能。无需再为不同工具分别管理密钥了：

```bash
hermes setup --portal
```

该命令可一次性完成登录操作、将Nous设为你的服务提供商，并启用工具网关。
:::

:::提示：已经在另一台机器上运行Hermes了吗？
无需从头开始重新配置。你可以使用`hermes import`命令恢复完整备份（详见[将Hermes导出到另一台机器](/reference/faq#exporting-hermes-to-another-machine)），或通过`hermes profile import`导入单个代理配置（详见[将单个配置迁移到另一台机器](/reference/faq#moving-a-single-profile-to-another-machine)）。需要注意的是，按设计要求，配置导出时会排除凭证信息，因此仅靠导出文件并不足以构成完整备份——[“hermes backup”与“hermes profile export”的区别](/reference/faq#hermes-backup-vs-hermes-profile-export)介绍了应选择哪种方式。
:::

---

## 先决条件

**安装程序：**在非Windows平台上，唯一的先决条件是**Git**。在Linux系统中，还需确保已安装`curl`和`xz-utils`（因为安装程序会以`.tar.xz`格式下载Node.js）。桌面版应用还需要`g++`（Debian/Ubuntu系统则为`build-essential`），用于编译本地模块。其余所有依赖项都会由安装程序自动处理，包括：
- **uv**（高效的Python包管理工具）
- **Python 3.11**（通过uv安装，无需使用sudo权限）
- **Node.js v26**（用于浏览器自动化及WhatsApp桥接功能；系统已安装的Node 22.22+、24.11+或26+版本可直接使用）
- **ripgrep**（高效的文件搜索工具）
- **ffmpeg**（用于文本转语音功能的音频格式转换）
:::info
您**无需**手动安装 Python、Node.js、ripgrep 或 ffmpeg。安装程序会自动检测缺失的组件并为您完成安装。只需确保系统已安装 `git`（可通过 `git --version` 查验）。在 Linux 系统上，还需确保已安装 `curl` 和 `xz-utils`（Debian/Ubuntu 系统可使用 `sudo apt install curl xz-utils` 安装）。若需使用桌面版应用，还需安装 `build-essential`（可通过 `sudo apt install build-essential` 安装）。
:::

:::tip Nix 用户
Nix **不再作为官方支持的安装方式**（仅提供尽力支持）。如果您已经在使用 Nix（无论是在 NixOS、macOS 还是 Linux 系统上），可通过专门的配置路径进行安装，该路径包含 Nix flake、声明式 NixOS 模块以及可选的容器模式。详情请参阅 **[Nix & NixOS 安装指南](./nix-setup.md)**。
:::

---

## 手动/开发者安装

如果您希望克隆代码库并从源代码进行安装——无论是为了贡献代码、在特定分支上运行程序，还是需要对虚拟环境拥有完全控制权——请参阅《贡献指南》中的 [开发环境配置](../developer-guide/contributing.md#development-setup) 部分。
:::

## 无需 sudo 权限/以系统服务用户身份安装

Hermes 支持以专用的非特权用户身份运行（例如 `hermes` systemd 服务账户，或任何没有 `sudo` 权限的用户）。在安装过程中，唯一真正需要 root 权限的是 Playwright 的 `--with-deps` 安装步骤，该步骤会通过 `apt` 安装 Chromium 所使用的共享库（如 `libnss3`、`libxkbcommon` 等）。安装程序会自动检测是否存在 sudo 权限，若没有则会以兼容模式继续运行——它会将 Chromium 可执行文件安装到服务用户自身的 Playwright 缓存目录中，并输出管理员需要单独执行的精确命令。

**Debian/Ubuntu 的推荐安装步骤：**

1. **首次安装时，需以拥有 sudo 权限的管理员身份**，先安装 Chromium 所需要的系统库：
   ```bash
   sudo npx playwright install-deps chromium
   ```
（您可以在任何地方运行此命令——`npx` 会自动下载 Playwright。）

2. **以无特殊权限的服务用户身份**运行常规安装程序。该程序会检测到缺少 sudo 权限，从而跳过 `--with-deps` 参数，并将 Chromium 安装到用户的本地 Playwright 缓存中：
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```

如果您希望完全跳过 Playwright 步骤——例如因为您正在以无头模式运行且无需浏览器自动化功能——请使用 `--skip-browser` 参数：
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser
   ```

安装程序还会预装[`cua-driver`](../user-guide/features/computer-use.md)，这样一旦启用“计算机使用”工具集，它就能立即正常工作；如需跳过此步骤，请使用`--skip-computer-use`参数（这样该组件将在您实际启用相应工具时才被动态安装）。

3. **让服务用户的shell能够调用`hermes`。** 安装程序会将启动脚本写入`~/.local/bin/hermes`目录。系统服务账户的PATH环境变量通常较为简短，其中并不包含`~/.local/bin`路径。您可以将其添加到用户的自定义环境变量中，或者将该启动脚本创建为符号链接并置于系统目录下：
   ```bash
   # Option A — add to the service user's profile
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

   # Option B — symlink system-wide (run as an admin)
   sudo ln -s /home/hermes/.hermes/hermes-agent/venv/bin/hermes /usr/local/bin/hermes
   ```

4. **验证：** 现在运行 `hermes doctor` 应该能够顺利执行。如果出现 `ModuleNotFoundError: No module named 'dotenv'` 的错误，说明您是使用系统 Python 而非虚拟环境启动工具（`~/.hermes/hermes-agent/venv/bin/hermes`）来调用仓库中的 `hermes` 文件（`~/.hermes/hermes-agent/hermes`）——请按照第3步进行修正。

5. **打算从该账户运行消息网关吗？** 用户级服务在用户登出后会停止运行，且除非为该服务用户启用“持续运行”功能，否则在系统启动时也不会自动启动。

   ```bash
   sudo loginctl enable-linger <service-user>
   ```

有关服务配置的详细信息，请参阅 [消息网关](/user-guide/messaging/)。

Arch 系统也采用相同的安装方式（安装程序使用带有相同 sudo 检测逻辑的 pacman），Fedora/RHEL 和 openSUSE 也是如此——这些发行版完全不支持 `--with-deps` 参数，因此管理员总是需要单独安装系统库。安装程序会自动输出相应的 `dnf`/`zypper` 命令。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `hermes: command not found` | 重新加载 shell（执行 `source ~/.bashrc`）或检查 PATH 环境变量 |
| `API key not set` | 运行 `hermes model` 命令配置提供商信息，或执行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后配置丢失 | 先运行 `hermes config check`，再执行 `hermes config migrate` |

如需更详细的诊断信息，可运行 `hermes doctor` —— 它会明确指出缺失了什么以及如何修复。

### 符号链接的首页目录与外部存储

Hermes 支持对 `HERMES_HOME` 及其子目录（包括 `hooks`、`skills`、`sessions` 和 `logs`）使用符号链接。在初始化首页目录时，现有的目录链接会被保留，而链接目录及其子目录（如 `logs/curator`）的权限则保持原样，由对应所有者控制。

如果链接目标缺失、无法访问或并非目录，初始化过程将会因存储错误而中止，并显示出具体的路径与链接目标信息。Hermes**不会**自动替换该链接或创建其缺失的目标——因为这样做可能会在外部存储设备或 NAS 卷未挂载的情况下向本地磁盘写入数据。请先检查报告的链接问题，恢复设备挂载状态或修正目标路径，确认访问权限正常后，再尝试重新初始化。如果是刻意创建新的点文件目标，也务必在确认目标存储空间已可用之后再自行创建。

`hermes doctor` 会将这类故障归类为存储问题，而非无效的 YAML 文件。请保留现有的 `config.yaml` 文件；运行 `hermes setup` 并不能解决目录不可用的问题。该工具仅用于检查目录是否可用，而非监控挂载状态——因为现有目录本身无法证明目标存储卷已成功挂载。

## 安装方式自动检测

Hermes 能够自动识别它是通过 git 安装器、Docker 还是 NixOS 安装的，随后 `hermes update` 会输出对应该安装方式的更新命令。无需设置任何环境变量——检测依据为安装路径（如 `~/.hermes/hermes-agent/` 目录结构、Docker 镜像版本号或 Nix 存储路径）。`hermes doctor` 也会在环境概览中显示检测到的安装方式。
