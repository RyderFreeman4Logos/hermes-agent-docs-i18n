---
title: "Windows (WSL2) Guide"
description: "Run Hermes Agent on Windows via WSL2 — setup, filesystem access between Windows and Linux, networking, and common pitfalls"
sidebar_label: "Windows (WSL2)"
sidebar_position: 2
---

# Windows（WSL2）使用指南

Hermes Agent 现已同时支持原生 Windows 环境和 WSL2 环境。本页面介绍 WSL2 的安装与使用方法；如需了解原生 PowerShell 安装方式，请参阅专门的 **[Windows（原生）指南](./windows-native.md)**。

**何时选择 WSL2 而非原生环境：**
- 您希望使用仪表板内置的终端（/chat 标签页）——该终端需要 POSIX PTY 支持，仅适用于 WSL2 环境。
- 您从事大量基于 POSIX 的开发工作，希望 Hermes 会话能与您的开发工具共享相同的文件系统及路径。
- 您已拥有 WSL2 环境，不想再维护第二个安装版本。

**何时选择原生环境更合适：**
- 交互式聊天、网关（Telegram/Discord 等）、cron 定时任务、浏览器工具、MCP 服务器以及大多数 Hermes 功能均在 Windows 原生环境中运行。
- 您不想每次引用文件或打开网址时都考虑在 WSL 与 Windows 之间切换。

在 WSL2 环境中，实际上相当于有两台计算机：一台是您的 Windows 主机，另一台是由 WSL 管理的 Linux 虚拟机。很多人会感到困惑，原因就在于不清楚自己当前处于哪台系统中。

本指南将重点介绍与 Hermes 相关的这部分内容：WSL2 的安装、在 Windows 与 Linux 之间传输文件、双向网络配置，以及用户在实际使用中常遇到的问题。

:::info 简体中文
同一页面上还提供了简体中文版的最低配置安装步骤说明——请通过右上角的**语言**菜单选择**简体中文**即可查看。
:::

## 为何选择 WSL2（而非原生 Windows）

原生 Windows 安装方式直接在 Windows 系统中运行：使用 Windows 终端（PowerShell、Windows Terminal 等）、Windows 文件系统路径（`C:\Users\…`）以及 Windows 进程。Hermes 通过 Git Bash 来执行 shell 命令，这也是 Claude Code 及其他当前用于 Windows 的智能体所采用的方式——无需彻底重写代码，即可解决 POSIX 与 Windows 环境之间的兼容问题。

WSL2 则在轻量级虚拟机中运行真正的 Linux 内核，因此其中的 Hermes 实际上与在 Ubuntu 上运行时的表现几乎完全一致。当您需要真正的 POSIX 环境时，这一点尤为重要：比如 `fork`、`/tmp`、UNIX 套接字、信号处理机制、基于 PTY 的终端、`bash`/`zsh` 等 shell，以及 `rg`、`git`、`ffmpeg` 等在 Linux 上具有相同行为的工具。

WSL2 的实际影响包括：
- Hermes CLI、网关、会话、内存管理、技能功能以及工具运行时均位于 Linux 虚拟机内部。
- Windows 程序（浏览器、原生应用、带有已登录配置文件的 Chrome）则运行在虚拟机外部。
- 每当您希望这两者之间进行交互——如共享文件、打开网址、控制 Chrome、连接本地模型服务器，或将 Hermes 网关接入手机——都需要跨越这一边界。本指南正是围绕这些边界展开的。

## 安装 WSL2

在**管理员权限的 PowerShell**或 Windows Terminal 中执行以下操作：

```powershell
wsl --install
```

在全新的 Windows 10 22H2 及更高版本或 Windows 11 系统上，该程序会安装 WSL2 内核、虚拟机平台功能以及预装的 Ubuntu 发行版。系统会提示您重新启动，请照做。重启后 Ubuntu 将自动启动，并要求输入 Linux 用户名和密码——这是一个**全新的 Linux 用户账户**，与您的 Windows 账户无关。

请确认当前确实处于 WSL2 环境中（而非旧版的 WSL1）：

```powershell
wsl --list --verbose
```

您应该会看到“VERSION 2”字样。如果某个发行版显示的是“VERSION 1”，则需要对其进行转换：

```powershell
wsl --set-version Ubuntu 2
wsl --set-default-version 2
```

Hermes 在 WSL1 环境下无法稳定运行——WSL1 会实时转换 Linux 系统调用，导致某些功能（如 procfs、信号处理及网络功能）与真正的 Linux 系统存在差异。

### 操作系统选择

我们以 Ubuntu（LTS 版本）作为测试基准。Debian 也可正常使用。对于愿意尝试的用户，Arch 和 NixOS 也同样可行，不过其一键安装程序假定系统已配置基于 Debian 的 `apt` 包管理器——如需相关配置方法，请参阅 [Nix 安装指南](/getting-started/nix-setup)。

### 启用 systemd（推荐）

使用 systemd 可更便捷地管理 hermes 网关及其他需要持续运行的服务。在现代 WSL 环境中，只需在对应操作系统中启用 systemd 即可：

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true

[interop]
enabled=true
appendWindowsPath=true

[automount]
options = "metadata,umask=22,fmask=11"
EOF
```

接着在 PowerShell 中执行：

```powershell
wsl --shutdown
```

重新打开您的 WSL 终端。执行 `ps -p 1 -o comm=` 命令后，输出结果应显示为 `systemd`。

上述的 `metadata` 挂载选项非常重要——如果没有它，/mnt/c/... 目录下的文件将无法存储真实的 Linux 权限位，从而导致在 Windows 路径下的脚本无法执行 `chmod +x` 等操作。

### 在 WSL 中安装 Hermes

打开 WSL2 shell 后：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
hermes
```

安装程序将WSL2视为普通的Linux系统——无需任何针对WSL的特殊设置。完整步骤请参阅[安装指南](/getting-started/installation)。

## 文件系统：跨越Windows ↔ WSL2边界

这是最容易让使用者困惑的部分。系统中存在**两种文件系统**，文件的存放位置至关重要——它会影响性能、数据准确性以及哪些工具能够访问这些文件。

### 两个方向的路径规则

| 方向 | 内部路径 | 使用路径 |
|---|---|---|
| 从WSL视角看到的Windows磁盘 | `C:\Users\you\Documents` | `/mnt/c/Users/you/Documents` |
| 从Windows视角看到的WSL磁盘 | `/home/you/code` | `\\wsl$\Ubuntu\home\you\code`（在较新版本中也可使用 `\\wsl.localhost\Ubuntu\...`） |

这两种路径都是真实存在的且功能正常，但**并非同一个文件系统**——它们实际上是通过底层的9P网络协议相互连接的。这会带来实际的性能和语义层面的影响。

### Hermes及项目的存放位置建议

**通用原则：所有类似Linux的文件都应存储在Linux文件系统中。**

- Hermes安装目录（`~/.hermes/`）——位于Linux侧。安装程序已自动完成此操作。
- 你在WSL中操作的Git仓库——也应在Linux侧（如 `~/code/...`、`~/projects/...`）。
- 模型文件、数据集及虚拟环境——同样存储在Linux侧。

遵循此原则的优势包括：

- **快速I/O操作**。对 `/mnt/c/...` 的操作需通过9P协议传输，速度比原生ext4慢10到100倍。在 `~/code` 下操作包含1万个文件的仓库时，`git status` 可能瞬间完成；而在 `/mnt/c` 下则可能需要15秒以上。
- **正确的权限设置**。/mnt/c上仅能尽力模拟Linux的权限机制。因此经常会出现 `ssh` 因“权限错误”拒绝密钥，或 `chmod +x` 操作默默失败的情况。
- **可靠的文件监控功能**。通过9P协议实现的inotify监控往往不可靠，开发服务器和测试工具常常无法及时检测到 `/mnt/c` 上的文件变动。
- **避免大小写敏感问题**。Windows路径默认不区分大小写，而Linux是区分大小写的。如果项目同时存在 `Readme.md` 和 `README.md` 两种文件，不同系统下的行为会有所差异。

只有当**确实需要**将文件保存在Windows侧时，才将其放在 `/mnt/c` 下——例如你需要通过Windows图形界面应用打开该文件，或者Windows Chrome的DevTools MCP要求当前目录为Windows可访问路径。

### 文件的传输方式

**从Windows传输到WSL**：最简单的方法是打开资源管理器，在地址栏输入 `\\wsl.localhost\Ubuntu`，然后直接将文件拖放到 `\home\<你>\...` 目录中。也可以通过PowerShell实现：

```powershell
wsl cp /mnt/c/Users/you/Downloads/file.pdf ~/incoming/
```

**从 WSL 进入 Windows 环境：** 将文件复制到 `/mnt/c/Users/<你用户名>/...` 目录中，即可在 Windows 资源管理器中立即看到该文件。

```bash
cp ~/reports/output.pdf /mnt/c/Users/you/Desktop/
```

在 Windows 应用程序中（如 GUI 编辑器、浏览器等）打开 WSL 文件：可使用 `explorer.exe` 或 `wslview`：

```bash
sudo apt install wslu     # once — gives you wslview, wslpath, wslopen, etc.
wslview ~/reports/output.pdf    # opens with the Windows default handler
explorer.exe .                  # opens the current WSL dir in Windows Explorer
```

**在两个系统之间转换路径：**

```bash
wslpath -w ~/code/project        # → \\wsl.localhost\Ubuntu\home\you\code\project
wslpath -u 'C:\Users\you'        # → /mnt/c/Users/you
```

### 行尾字符、BOM 以及 Git

如果在 Windows 系统上使用 Windows 编辑器编辑文件，这些文件可能会带有 `CRLF` 行尾格式。当 Linux 系统上的 `bash` 或 Python 读取这些文件时，shell 脚本会因“错误的解释器：/bin/bash^M”而无法运行；而 Python 在处理带有 BOM 的 `.env` 文件时也可能会出现错误。

解决此问题的方法是在 WSL 内部（而非 Windows 系统上）正确配置 git 参数。

```bash
git config --global core.autocrlf input
git config --global core.eol lf
```

对于已包含 CRLF 格式的文件：

```bash
sudo apt install dos2unix
dos2unix path/to/script.sh
```

### “在 WSL 内部克隆，还是放在 `/mnt/c` 上？”

建议始终在 WSL 内部进行克隆，除非你有特殊原因不这么做。对于典型的 Hermes 工作流（如 `hermes chat`、使用 `rg`/`ripgrep` 查询代码库的工具、文件监控功能以及后台网关），相比使用 `/mnt/c/Users/you/myrepo`，基于 `~/code/myrepo` 的操作速度会快得多，稳定性也更高。

唯一例外是：**那些需要启动 Windows 可执行文件的 MCP 桥接方案**。如果你是通过 `cmd.exe` 使用 `chrome-devtools-mcp`（详见 [MCP 使用指南：WSL → Windows Chrome](/guides/use-mcp-with-hermes#wsl2-bridge-hermes-in-wsl-to-windows-chrome)），如果 Hermes 的当前工作目录为 `~`，Windows 可能会因 `UNC` 路径问题发出警告。这种情况下，应从 `/mnt/c/` 目录下的某个位置启动 Hermes，这样 Windows 进程就会拥有一个带驱动器字母的当前工作目录。

## 网络连接：WSL ↔ Windows

WSL2 运行在拥有独立网络栈的轻量级虚拟机中。这意味着从网络视角来看，WSL 内部的 `localhost` **与** Windows 上的 `localhost` 并不相同——它们是两个独立的主机。你需要为每项服务确定数据流的传输方向，并选择合适的桥接方案。

通常会出现两种情况。

### 情况 1 — WSL 中的 Hermes 需要与 Windows 上的服务通信

这是最常见的情况：你在 Windows 上运行了 **Ollama、LM Studio 或 llama-server**，而位于 WSL 内部的 Hermes 需要与之交互。

相关的标准操作指南可见于提供商指南：**[WSL2 本地模型网络配置指南 →](/integrations/providers#wsl2-networking-windows-users)**

简述如下：

- **Windows 11 22H2 及更高版本**：开启镜像网络模式（在 `%USERPROFILE%\.wslconfig` 中设置 `networkingMode=mirrored`，然后执行 `wsl --shutdown`）。这样 `localhost` 在双向通信中都能正常使用。
- **Windows 10 或更早版本**：使用 Windows 主机的 IP 地址（即 WSL 虚拟网络的默认网关），并确保 Windows 上的服务器绑定到 `0.0.0.0`，而不仅仅是 `127.0.0.1`。通常还需要在 Windows 防火墙中为相应端口添加规则。

如需完整的配置表（包括 Ollama / LM Studio / vLLM / SGLang 的绑定地址、防火墙规则示例、动态 IP 获取工具以及 Hyper-V 防火墙的解决方案），请点击上述链接查看，无需重复查询。

### 情况 2 — Windows 上的设备（或局域网中的设备）需要与 WSL 中的 Hermes 通信

这是反向的通信场景，相关文档相对较少，但以下情况就需要使用此配置：

- 从 Windows 浏览器访问 Hermes 的 **Web 控制面板**。
- 从 Windows 端的工具调用 **兼容 OpenAI 的 API 服务器**（当 `API_SERVER_ENABLED=true` 时由 `hermes gateway` 提供）。详情请参阅 [API 服务器功能页面](/user-guide/features/api-server)。
- 测试 **消息网关**（如 Telegram、Discord 等），这类平台通常会向本地的 webhook URL 发送请求——此时一般建议使用 `cloudflared`/`ngrok` 而非直接端口转发。

#### 子情况 2a：从 Windows 主机本身发起请求

在 **已开启镜像模式的 Windows 11 22H2+** 系统上，无需额外操作。在 WSL 中绑定到 `0.0.0.0:8080`（或 `127.0.0.1:8080`）的进程，可以通过 Windows 浏览器通过 `http://localhost:8080` 访问。WSL 会自动将此绑定地址广播回主机。

在 **NAT 模式**下（Windows 10 或旧版 Windows 11），WSL2 的默认“localhost 转发”功能通常会将 Linux 端的 `127.0.0.1` 绑定请求转发到 Windows 的 `localhost`，因此使用 `--host 127.0.0.1` 启动的 Hermes 服务通常可以通过 `http://localhost:PORT` 从 Windows 访问。如果无法访问：

- 在 WSL 内部明确指定绑定到 `0.0.0.0`。
- 使用命令 `ip -4 addr show eth0 | grep inet` 查找 WSL 虚拟机的 IP 地址，然后从 Windows 端通过该地址进行访问。

#### 子情况 2b：从局域网中的其他设备（手机、平板或其他电脑）发起请求

这是最棘手的场景。数据流为 **局域网设备 → Windows 主机 → WSL 虚拟机**，你需要分别配置这两段连接：

1. **在 WSL 内部的所有网络接口上绑定监听**。仅在 `127.0.0.1` 上监听的进程无法从虚拟机外部访问，必须使用 `0.0.0.0` 进行绑定。

2. **实现 Windows → WSL 虚拟机的端口转发**。在镜像模式下此步骤会自动完成。而在 NAT 模式下，则需要你在管理员权限的 PowerShell 中为每个端口手动设置端口转发规则。

   ```powershell
   # Grab the WSL VM's current IP (it changes on every WSL restart under NAT)
   $wslIp = (wsl hostname -I).Trim().Split(' ')[0]

   # Forward Windows port 8080 → WSL:8080
   netsh interface portproxy add v4tov4 `
     listenaddress=0.0.0.0 listenport=8080 `
     connectaddress=$wslIp connectport=8080

   # Allow it through Windows Firewall
   New-NetFirewallRule -DisplayName "Hermes WSL 8080" `
     -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
   ```

稍后可通过命令 `netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=8080` 进行删除。

3. **将局域网设备指向 `http://<windows-lan-ip>:8080`。**

由于在 NAT 模式下，WSL 虚拟机的 IP 地址会在每次重启后发生变化，因此一次性设置的规则仅能持续到下一次执行 `wsl --shutdown` 命令为止。若需要永久生效的配置，建议使用镜像模式，或将端口代理设置放入在 Windows 登录时自动运行的脚本中。

对于来自云消息服务提供商的 webhook（如 Telegram 的 `setWebhook`、Slack 事件等），无需强行使用端口转发功能，可直接利用 `cloudflared` 隧道。详情请参阅 [webhooks 指南](/user-guide/messaging/webhooks)。

## 在 Windows 上长期运行 Hermes 服务

Hermes 的 [Tool Gateway](/user-guide/features/tool-gateway) 和 API 服务器均为长期运行的进程。在 WSL2 环境中，有几种方法可以保持这些服务的持续运行。

### 用于快速打开 Hermes 的桌面快捷方式

如果您只需一个双击即可启动交互式 Hermes shell 的快捷方式，可以在 Windows 端创建该快捷方式，使其自动切换到 WSL 环境中：

1. 在 Windows 桌面右键点击，选择 **新建 -> 快捷方式**。
2. 在目标路径处填写您的发行版名称（如需更改可替换为 `Ubuntu`）：

   ```text
   wt.exe -w 0 -p "Ubuntu" wsl.exe -d Ubuntu --cd ~ -- bash -ic "hermes"
   ```

3. 给它起一个显而易见的名称，比如 `Hermes`。

这样即可打开 Windows Terminal，启动你的 WSL 发行版，将你带到 Linux 的主目录中，随后启动 Hermes。如果 `hermes` 尚未加入 PATH 环境变量，可手动打开一次 WSL 并运行 `source ~/.bashrc`；或者直接在项目目录中使用 `uv run hermes` 代替该命令。

可选优化项：

- **自定义图标**：打开 **属性 -> 更改图标**，选择对应的 `.ico` 文件，例如仓库中的 Hermes 徽标。
- **固定启动器**：一旦快捷方式能够正常使用，可将其固定在“开始”菜单或任务栏上，这样就无需再次寻找了。

### 使用 systemd 的 WSL 环境（推荐）

如果你已按照上述设置步骤启用了 systemd，那么 `hermes gateway` 以及 API 服务器的运行方式将与普通 Linux 机器一致。此时可使用网关配置向导进行设置：

```bash
hermes gateway setup
```

它将会建议安装一个 systemd 用户单元，这样在 WSL 启动时网关就能自动启动。

### 实现 Windows 登录时自动启动 WSL

WSL 虚拟机只有在被使用时才会保持运行状态。若不想打开终端窗口仍能访问网关，可通过任务计划程序在 Windows 登录时启动一个 WSL 进程：

- **触发条件：** 用户登录时。
- **操作：** 启动程序
  - 程序路径：`C:\Windows\System32\wsl.exe`
  - 参数：`-d Ubuntu --exec /bin/sh -c "sleep infinity"`

这样就能让虚拟机持续运行，从而使由 systemd 管理的网关保持启动状态。在 Windows 11 上， newer 的 `wsl --install --no-launch` + 自动启动方案也同样适用；而 `sleep infinity` 方法则是更通用的解决方案。

## GPU 直通（本地模型）

自 WSL 内核 5.10.43 及更高版本起，WSL2 已原生支持 **NVIDIA** GPU——只需在 Windows 上安装标准版 NVIDIA 驱动程序（切勿在 WSL 内部安装 Linux 版 NVIDIA 驱动），然后在 WSL 中运行 `nvidia-smi` 即可检测到该 GPU。之后，CUDA 工具包、`torch`、`vllm`、`sglang` 以及 `llama-server` 等程序均可像平常一样基于真实 GPU 进行构建。

WSL2 对 AMD ROCm 和 Intel Arc 的支持仍在发展中，且不在 Hermes 的测试范围内——虽然当前驱动可能已具备相应功能，但我们暂无法提供具体的配置方案。

如果你正在运行通过 Windows 驱动直接使用 GPU 的**原生 Windows 本地模型服务器**（如 Ollama for Windows、LM Studio），则完全无需使用 WSL 的 GPU 直通功能——只需按照上述第一种方法操作，再从 WSL 通过网络访问该服务器即可。

## 常见问题

**“连接到我基于 Windows 运行的 Ollama/LM Studio 时被拒绝”**
请参阅 [WSL2 网络设置](/integrations/providers#wsl2-networking-windows-users)。90% 的情况下，原因是服务器绑定在了 `127.0.0.1` 地址，而应设置为 `0.0.0.0`（Ollama 中需设置 `OLLAMA_HOST=0.0.0.0`），或者是你遗漏了防火墙规则。

**在代码仓库中执行 `git status`/`hermes chat` 时速度极慢**
很可能是因为你当前的工作目录位于 `/mnt/c/...`。请将代码仓库移至 Linux 系统下的 `~/code/...` 目录，这样速度会快很多。

**脚本中出现“bad interpreter: /bin/bash^M”错误**
这是由于 Windows 编辑器生成的 CRLF 行尾格式所致。可使用 `dos2unix script.sh` 命令转换文件格式，并在 WSL 的 git 配置中设置 `core.autocrlf input`。

**通过 MCP 启动的 Windows 可执行文件出现“UNC 路径不受支持”的警告**
这是因为 Hermes 的当前工作目录位于 Linux 文件系统中，而 Windows 的 `cmd.exe` 不知晓如何处理此类路径。对于此类场景，可在该会话中从 `/mnt/c/...` 路径启动 Hermes，或者使用一个在调用 Windows 可执行文件之前先切换到 Windows 可访问路径的封装工具。

**睡眠/休眠唤醒后时间出现偏差**
主机从睡眠状态恢复后，WSL2 的时钟可能会滞后数分钟，从而导致依赖证书验证的功能（如 OAuth、HTTPS API）失效。可根据需要手动修复此问题：

```bash
sudo hwclock -s
```

或者安装 `ntpdate`，并在登录时运行它。

**启用镜像模式或连接 VPN 后，DNS 功能失效。**
镜像模式会将主机的网络设置代理到 WSL 中——如果 Windows 的 DNS 出现问题（如 VPN 分流传输、企业级解析服务器），WSL 也会继承这些问题。解决办法是手动覆盖 `resolv.conf`（在 `/etc/wsl.conf` 中设置 `generateResolvConf=false`，然后自行编写包含 `1.1.1.1` 或 VPN DNS 地址的 `/etc/resolv.conf` 文件）。

**运行安装程序后找不到 `hermes`。**
安装程序会通过 `~/.bashrc` 将 `~/.local/bin` 添加到 shell 的 PATH 环境变量中。需执行 `source ~/.bashrc`（或打开新终端），才能让该设置在当前会话中生效。

**Windows Defender 对 WSL 文件的扫描速度较慢。**
当从 Windows 访问 WSL 文件时，Defender 会通过 9P 桥接技术进行扫描，这会导致类似 `/mnt/c` 风格的跨边界访问更加缓慢。如果仅在 WSL 内部操作文件，则不会受到影响。但若频繁使用 Windows 工具操作 `\\wsl$\...` 路径下的文件，建议将 WSL 发行版路径从实时扫描中排除。

**磁盘空间不足。**
WSL2 会将虚拟机磁盘以稀疏 VHDX 格式存储在 `%LOCALAPPDATA%\Packages\...` 目录下。虽然该磁盘会持续增长，但删除文件后不会自动缩小。若要释放空间，可先执行 `wsl --shutdown`，然后在管理员权限的 PowerShell 中运行 `Optimize-VHD -Path <path-to-ext4.vhdx> -Mode Full` 命令（需要 Hyper-V 工具）；或者使用 WSL 文档中推荐的更简单的 `diskpart` 方法。

## 接下来该去哪里

- **[安装](/getting-started/installation)** —— 实际的安装步骤（Linux、WSL2 和 Termux 均使用相同的安装程序）。
- **[集成 → 提供商 → WSL2 网络](/integrations/providers#wsl2-networking-windows-users)** —— 针对本地模型服务器的深度网络配置指南。
- **[MCP 指南 → WSL → Windows Chrome](/guides/use-mcp-with-hermes#wsl2-bridge-hermes-in-wsl-to-windows-chrome)** —— 在 WSL 中通过 Hermes 控制已登录的 Windows Chrome 浏览器。
- **[工具网关](/user-guide/features/tool-gateway)** 与 **[Web 控制面板](/user-guide/features/web-dashboard)** —— 这些长期运行的服务通常是您希望从 WSL 向网络其他设备暴露的内容。
