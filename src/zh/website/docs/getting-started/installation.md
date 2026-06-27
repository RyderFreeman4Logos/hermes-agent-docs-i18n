---
sidebar_position: 2
title: "Installation"
description: "Install Hermes Agent on Linux, macOS, WSL2, native Windows, or Android via Termux"
---

# 安装

只需两分钟，即可让 Hermes Agent 开始运行！

:::提示 平台支持情况
如需查看完整的平台支持列表（包括支持的操作系统、分发方式以及平台限制功能），请参阅 **[平台支持](./platform-support.md)**。
:::

## 快速安装
### 使用 macOS 或 Windows 系统上的 Hermes Desktop 安装程序（推荐）
如需轻松安装命令行工具和桌面应用程序，请从我们的网站 [下载 Hermes Desktop 安装程序](https://hermes-agent.nousresearch.com/) 并运行它。

### 不使用 Hermes Desktop：
如仅需安装命令行版本而无需桌面应用程序，可执行以下操作：

#### Linux / macOS / WSL2 / Android（Termux）
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

#### Windows（原生版）

在 PowerShell 中运行：
```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1) 
```

如果在仅通过命令行完成安装后想要进一步安装并运行 Hermes Desktop，只需直接运行相应命令即可。
```bash
hermes desktop
```

### 安装程序的功能

安装程序会自动处理所有相关事项——包括所有依赖项（Python、Node.js、ripgrep、ffmpeg）、代码库克隆、虚拟环境创建、全局 `hermes` 命令配置以及大语言模型提供者设置。一切准备就绪后，您即可开始对话。

#### 安装路径布局

安装程序将各类文件放置的位置取决于您是以普通用户身份还是以root权限进行安装：

| 安装方式                     | 代码存储位置               | `hermes` 可执行文件                   | 数据目录                         |
|------------------------------|----------------------------|---------------------------------------|----------------------------------|
| 按用户安装（git安装方式）     | `~/.hermes/hermes-agent/`   | `~/.local/bin/hermes`（符号链接）       | `~/.hermes/`                      |
| 以root模式安装（`sudo curl … \| sudo bash`） | `/usr/local/lib/hermes-agent/` | `/usr/local/bin/hermes`                | `/root/.hermes/`（或 `$HERMES_HOME`） |

以root模式安装时采用的**FHS路径规范**（`/usr/local/lib/…`、`/usr/local/bin/hermes`）与Linux系统中其他系统级开发工具的存储位置一致。这种方式非常适合需要在多用户共享的机器上部署的场景，因为只需进行一次系统级安装即可满足所有用户的需求。而与身份相关的配置（认证信息、技能设置、会话数据）仍会存储在每个用户的 `~/.hermes/` 目录下，或用户指定的 `HERMES_HOME` 路径中。

### 安装完成后的操作

请重新加载Shell环境，然后即可开始对话：

```bash
source ~/.bashrc   # or: source ~/.zshrc
hermes             # Start chatting!
```

如需日后重新配置各项设置，请使用专用命令：

```bash
hermes model          # Choose your LLM provider and model
hermes tools          # Configure which tools are enabled
hermes gateway setup  # Set up messaging platforms
hermes config set     # Set individual config values
hermes setup          # Or run the full setup wizard to configure everything at once
```

:::提示 最快捷途径：Nous Portal  
一个订阅即可使用300多种模型，同时还包含[工具网关](/user-guide/features/tool-gateway)（网页搜索、图像生成、文本转语音、云浏览器）功能。无需再为不同工具分别管理密钥！

```bash
hermes setup --portal
```

该命令可一次性完成登录操作、将Nous设置为您的服务提供商，并启用Tool Gateway。
:::

---

## 先决条件

**安装程序：**在非Windows系统上，唯一的先决条件是**Git**。在Linux系统中，还需确保已安装`curl`和`xz-utils`（因为安装程序会将Node.js以`.tar.xz`格式下载）。桌面应用还需要`g++`（或在Debian/Ubuntu系统中使用`build-essential`）来编译原生模块。其余所有依赖项都会由安装程序自动处理：

- **uv**（高效的Python包管理器）
- **Python 3.11**（通过uv安装，无需使用sudo）
- **Node.js v22**（用于浏览器自动化和WhatsApp桥接功能）
- **ripgrep**（快速文件搜索工具）
- **ffmpeg**（用于文本转语音的音频格式转换）

:::info
您无需手动安装Python、Node.js、ripgrep或ffmpeg。安装程序会自动检测缺失的组件并为您完成安装。只需确保已安装`git`（可通过`git --version`查看）。在Linux系统中，还需确保已安装`curl`和`xz-utils`（在Debian/Ubuntu系统中可使用`sudo apt install curl xz-utils`命令安装）。对于桌面应用，还需安装`build-essential`（使用`sudo apt install build-essential`命令安装）。
:::

:::tip Nix用户提示
Nix**已不再作为官方支持的安装方式**（仅提供有限支持）。如果您已经在使用Nix（无论是在NixOS、macOS还是Linux系统上），可通过专门的配置方式来实现安装，该方式包含Nix flake文件、声明式NixOS模块以及可选的容器模式。详情请参阅**[Nix与NixOS安装指南](./nix-setup.md)**。
:::

---

## 手动/开发者安装

如果您希望克隆仓库并从源代码进行安装——例如为了贡献代码、在特定分支上运行程序，或希望对虚拟环境拥有完全控制权——请参阅《贡献指南》中的[开发环境配置](../developer-guide/contributing.md#development-setup)部分。

---

## 无需sudo/以系统服务用户身份安装

支持以专用且无特殊权限的用户身份运行Hermes（例如`hermes` systemd服务账户，或任何没有`sudo`权限的用户）。在整个安装过程中，真正需要root权限的仅是Playwright的`--with-deps`步骤，该步骤会通过`apt`安装Chromium所依赖的共享库（如`libnss3`、`libxkbcommon`等）。安装程序会自动检测是否具备sudo权限，若无法使用sudo则会自动降级处理——它会将Chromium二进制文件安装到服务用户自身的Playwright缓存目录中，并输出管理员需要单独执行的精确命令。

**Debian/Ubuntu系统的推荐安装步骤：**

1. **仅需一次**，以拥有sudo权限的管理员身份，安装Chromium所需的系统库：
   ```bash
   sudo npx playwright install-deps chromium
   ```
（您可以在任何位置运行此命令——`npx` 会自动下载 Playwright。）

2. **以无特殊权限的服务用户身份**运行常规安装程序。该程序会检测到缺少 sudo 权限，从而跳过 `--with-deps` 参数，并将 Chromium 安装到用户的本地 Playwright 缓存中：
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```

如果您希望完全跳过 Playwright 步骤——例如因为是在无头模式下运行且无需浏览器自动化功能——请使用 `--skip-browser` 参数：
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser
   ```

3. **让服务用户的 shell 能够调用 `hermes`。** 安装程序会将启动器写入 `~/.local/bin/hermes` 文件中。系统服务账户的 PATH 环境变量通常较为简短，其中并不包含 `~/.local/bin` 目录。因此，要么将该目录添加到用户的环境变量中，要么将该启动器创建符号链接至系统路径下的合适位置：
   ```bash
   # Option A — add to the service user's profile
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

   # Option B — symlink system-wide (run as an admin)
   sudo ln -s /home/hermes/.hermes/hermes-agent/venv/bin/hermes /usr/local/bin/hermes
   ```

4. **验证：** 现在运行 `hermes doctor` 应该能够正常执行。如果出现 `ModuleNotFoundError: No module named 'dotenv'` 的错误，说明您使用的是系统 Python 而非虚拟环境启动器（`~/.hermes/hermes-agent/venv/bin/hermes`）来调用仓库中的 `hermes` 文件（`~/.hermes/hermes-agent/hermes`）——请按照第 3 步进行修正。

在 Arch（其安装程序采用带有相同 sudo 检测逻辑的 pacman）、Fedora/RHEL 以及 openSUSE 系统上，原理也是一样的——这些发行版根本不支持 `--with-deps` 参数，因此管理员总是需要单独安装系统库。安装程序会自动输出相应的 `dnf`/`zypper` 命令。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `hermes: command not found` | 重新加载 shell 配置文件（`source ~/.bashrc`）或检查 PATH 环境变量 |
| `API key not set` | 运行 `hermes model` 命令来配置提供商，或执行 `hermes config set OPENROUTER_API_KEY your_key` |
| 更新后配置丢失 | 先运行 `hermes config check`，再执行 `hermes config migrate` |

如需更详细的诊断信息，可运行 `hermes doctor`——它会明确指出缺失了哪些内容以及如何修复。

## 安装方式自动检测

Hermes 能够自动识别它是通过 `pip`、git 安装器、Homebrew 还是 NixOS 安装的，随后 `hermes update` 会针对该安装路径输出相应的更新命令。无需设置任何环境变量——检测依据是安装时的文件结构（Python 的 site-packages 目录、`~/.hermes/hermes-agent/` 目录、Homebrew 安装路径或 Nix 存储路径）。`hermes doctor` 也会在环境概览中显示检测到的安装方式。
