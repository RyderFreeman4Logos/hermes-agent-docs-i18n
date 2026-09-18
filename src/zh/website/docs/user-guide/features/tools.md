---
sidebar_position: 1
title: "Tools & Toolsets"
description: "Overview of Hermes Agent's tools — what's available, how toolsets work, and terminal backends"
---

# 工具与工具集

工具是用于扩展智能体功能的函数，它们被整理为逻辑上的**工具集**，并且可以根据不同平台进行启用或禁用。

## 可用工具

Hermes 搭载了丰富的内置工具注册表，涵盖网页搜索、浏览器自动化、终端执行、文件编辑、内存管理、任务委托、定时任务、Home Assistant 等功能。

:::note
**Honcho 跨会话内存**作为内存提供插件（位于 `plugins/memory/honcho/` 目录）提供，而非内置工具集。有关安装方法，请参阅 [插件](./plugins.md)。
:::

高级分类：

| 类别 | 示例 | 描述 |
|------|------|------|
| **网页** | `web_search`, `web_extract` | 在网页上搜索并提取页面内容。 |
| **X 搜索** | `x_search` | 通过 xAI 内置的 `x_search` Responses 工具搜索 X（Twitter）上的帖文与主题串——该功能需使用 xAI 凭证（SuperGrok OAuth 或 `XAI_API_KEY`）才能启用；默认处于关闭状态，可通过 `hermes tools` → 🐦 X（Twitter）搜索来开启。 |
| **终端与文件** | `terminal`, `process`, `read_file`, `patch` | 执行命令并操作文件。 |
| **浏览器** | `browser_navigate`, `browser_snapshot`, `browser_vision` | 支持文本处理与视觉识别的交互式浏览器自动化功能。 |
| **媒体** | `vision_analyze`, `image_generate`, `text_to_speech` | 多模态分析与生成功能。 |
| **智能体编排** | `todo`, `clarify`, `execute_code`, `delegate_task` | 用于任务规划、信息澄清、代码执行以及子智能体任务分配。 |
| **记忆与检索** | `memory`, `session_search` | 提供持久化记忆功能及会话内容检索。 |
| **自动化** | `cronjob` | 支持创建、列表查看、更新、暂停、恢复、运行及删除等操作的定时任务。任务结果将通过 cron 自带的发送机制、`hermes send` CLI 以及网关通知器进行传递，而非通过智能体可调用的工具。 |
| **集成功能** | `ha_*`, MCP server tools | Home Assistant、MCP 以及其他集成方案。 |

如需查看权威的代码生成型工具清单，请参阅 [内置工具参考](/reference/tools-reference) 和 [工具集参考](/reference/toolsets-reference)。

:::提示 Nous 工具网关  
已订阅付费版 [Nous Portal](https://portal.nousresearch.com) 的用户可通过 **[工具网关](tool-gateway.md)** 使用网页搜索、图像生成、文本转语音以及浏览器自动化功能——无需额外的 API 密钥。运行 `hermes model` 即可启用该功能，或使用 `hermes tools` 对各个工具进行单独配置。  
:::

## 使用工具集

```bash
# Use specific toolsets
hermes chat --toolsets "web,terminal"

# See all available tools
hermes tools

# Configure tools per platform (interactive)
hermes tools
```

常见的工具集包括 `web`、`search`、`terminal`、`file`、`browser`、`vision`、`image_gen`、`skills`、`tts`、`todo`、`memory`、`session_search`、`cronjob`、`code_execution`、`delegation`、`clarify`、`homeassistant`、`messaging`、`spotify`、`discord`、`discord_admin`、`debugging` 以及 `safe`。

如需查看完整的工具集列表，包括诸如 `hermes-cli`、`hermes-telegram` 这样的平台预设，以及 `mcp-<server>` 这类动态 MCP 工具集，请参阅 [工具集参考文档](/reference/toolsets-reference)。

## 工具结果标注

在阅读智能体对话记录时，有几种工具行为是需要了解的：

- **对信号导致的进程终止进行了详细说明。** 当终端命令因信号而被强制终止时，系统会给出易于理解的文字描述，而不仅仅是单纯的数字代码——例如，退出码 `-9`/`137` 会显示为“由信号 9：SIGKILL 终止——通常是由于内存耗尽触发的内核 OOM 销毁机制，或是人为发出的 kill -9 命令”；类似地，段错误、程序中止、SIGTERM 信号、管道故障以及 CPU/文件大小限制等情况也会以相同方式标注。对于负数代码（子进程相关语义），文档会给出明确解释；而针对 shell 中 `128+signum` 的编码规则，则使用了“通常”一词进行限定，因为应用程序完全有可能使用这些代码正常退出。
- **UTF-16 文本文件会被转码处理，而不会被直接拒绝。** `read_file` 功能能够识别 UTF-16 格式的文件（通过 BOM 或字节模式特征判断，同时支持两种字节序——这在 Windows 记事本生成的文件以及 PowerShell 的 `>` 重定向输出中很常见），并将其转换为 UTF-8 格式以便显示，而不会将该文件标记为二进制文件。结果显示中会附带说明已进行转换的信息；通过 `patch`/`write_file` 进行的编辑操作也会将内容重新编码为 UTF-8。不过，大小超过 10 MB 的文件以及真正的二进制文件仍会遭到拒绝处理。

## 终端后端

该终端工具能够在不同的环境中执行命令：

| 后端类型 | 描述 | 使用场景 |
|---------|-------------|----------|
| `local` | 在您的本地机器上运行（默认值） | 开发工作，处理可信任务 |
| `docker` | 孤立式容器环境 | 确保安全性，实现结果可复现 |
| `ssh` | 远程服务器 | 沙箱隔离，防止代理程序访问自身代码 |
| `singularity` | 高性能计算专用容器 | 集群计算，无根运行模式 |
| `modal` | 云端执行环境 | 无服务器架构，支持弹性扩展 |
| `daytona` | 云端沙箱工作空间 | 提供持久化的远程开发环境 |
| `vercel_sandbox` | Vercel Sandbox云微虚拟机 | 基于快照机制实现文件系统持久化的云端执行 |

### 配置选项

```yaml
# In ~/.hermes/config.yaml
terminal:
  backend: local    # or: docker, ssh, singularity, modal, daytona, vercel_sandbox
  cwd: "."          # Working directory
  timeout: 180      # Command timeout in seconds
```

### Shell启动文件与非交互式命令

Agent终端调用会以**非交互式方式**运行您的shell——此时不存在TTY，也没有人在命令提示符前操作。那些在普通终端中几乎不会被察觉的复杂或交互式的shell初始化过程，可能会破坏Agent运行的每个命令，或使其运行速度大幅下降：

- **缓慢的初始化过程（如`nvm`、版本管理工具以及需要网络连接的命令）**：常见的`nvm.sh`加载机制会在每次shell启动时带来明显的延迟，而Agent需要启动多个shell。那些耗时数秒的rc脚本甚至会让简单的`git status`命令也面临超时的风险。
- **依赖TTY的指令**：`.bashrc`/`.zshrc`文件中任何会提示用户操作、启动`tmux`/`screen`会话、调用`read`函数或显示菜单的指令，都可能导致非交互式shell挂起——这类命令看似会无限运行，最终导致超时。
- **无条件输出**：那些通过`echo`输出提示信息的rc脚本，会污染Agent需要解析的每个命令的输出结果。

解决此问题的方法是采用大多数发行版已在`.bashrc`顶部提供的标准防护机制：当检测到shell为非交互式模式时立即返回，而将所有复杂或交互式的指令放在其下方。

```bash
# ~/.bashrc — keep this guard near the top
case $- in
  *i*) ;;      # interactive: continue
  *) return;;  # non-interactive: stop here
esac

# heavy/interactive init goes BELOW the guard
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

Zsh 用户：请将仅用于登录时的配置放在 `.zprofile` 文件中，将仅用于交互式会话的配置放在 `.zshrc` 文件中；同时尽量简化 `.zshenv` 的内容，因为它会在包括非交互式会话在内的所有 shell 启动时都被加载。如果该代理确实需要某个仅通过您的 rc 文件添加到 `PATH` 中的工具，可在相关保护代码*之上*导出 `PATH` 变量（路径导出操作的开销极低），或者将该二进制文件创建符号链接至 `~/.local/bin` 目录中。

如果该代理在您的终端中运行正常，但在其他终端中立即卡住或超时，首先应检查您的 shell 初始化脚本。

### Docker 后端

```yaml
terminal:
  backend: docker
  docker_image: python:3.11-slim
```

**单个持久化容器，贯穿整个流程。** Hermes在首次使用时会启动一个长期运行的容器（`docker run -d ... sleep infinity`），并通过`docker exec`将所有的终端操作、文件操作以及`execute_code`调用都引导至同一个容器中。无论是在不同的工具调用之间，还是在 `/new`、`/reset` 和 `delegate_task` 子代理之间，工作目录的更改、已安装的包、环境配置的调整，以及写入 `/workspace` 的文件，都会在Hermes进程的整个生命周期内保持一致。当进程关闭时，该容器也会被停止并移除。

这意味着Docker后端的行为类似于一个持久化的沙箱虚拟机，而非每次命令执行都创建一个全新的容器。一旦您执行了 `pip install foo`，该包就会在整个会话期间一直存在。如果您执行了 `cd /workspace/project`，后续的 `ls` 操作就能看到该目录。有关完整的生命周期详情，以及用于控制 `/workspace` 和 `/root` 是否能在Hermes重启后依然保留的 `container_persistent` 标志，请参阅 [配置 → Docker后端](../configuration.md#docker-backend)。

### SSH后端

出于安全考虑推荐使用此方式——代理无法修改自身的代码：

```yaml
terminal:
  backend: ssh
```
```bash
# Set credentials in ~/.hermes/.env
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=myuser
TERMINAL_SSH_KEY=~/.ssh/id_rsa
```

### Singularity/Apptainer

```bash
# Pre-build SIF for parallel workers
apptainer build ~/python.sif docker://python:3.11-slim

# Configure
hermes config set terminal.backend singularity
hermes config set terminal.singularity_image ~/python.sif
```

### 模态（无服务器云）

```bash
uv pip install modal
modal setup
hermes config set terminal.backend modal
```

### Vercel 沙箱环境

```bash
pip install 'hermes-agent[vercel]'
hermes config set terminal.backend vercel_sandbox
hermes config set terminal.vercel_runtime node24
```

需同时使用 `VERCEL_TOKEN`、`VERCEL_PROJECT_ID` 和 `VERCEL_TEAM_ID` 三种凭证进行身份验证。这种访问令牌配置是 Render、Railway、Docker 以及类似平台上执行部署任务及常规长时间运行的 Hermes 进程所支持的方案。目前支持的运行时环境为 `node24`、`node22` 和 `python3.13`；Hermes 默认将 `/vercel/sandbox` 设为远程工作区的根目录。

对于一次性本地开发场景，Hermes 也支持使用有效期较短的 Vercel OIDC 令牌：

```bash
VERCEL_OIDC_TOKEN="$(vc project token <project-name>)" hermes chat
```

从关联的 Vercel 项目目录中：

```bash
VERCEL_OIDC_TOKEN="$(vc project token)" hermes chat
```

当设置 `container_persistent: true` 时，Hermes 会利用 Vercel 快照功能，在重复创建相同任务的沙箱环境时保留文件系统状态。这些状态包括通过 Hermes 同步到的凭证、技能以及沙箱内的缓存文件。不过，快照无法保留正在运行的进程、PID 空间或相同的沙箱身份。

在沙箱运行期间，后台终端命令会通过常规的进程管理工具来执行启动、轮询、等待、记录日志和终止进程等操作；但在进行清理或重启后，Hermes 并不提供原生的 Vercel 分离进程恢复功能。

请将 `container_disk` 保持未设置状态或使用默认值 `51200`；Vercel 沙箱不支持自定义磁盘大小设置，否则会导致诊断失败及后端创建失败。

### 容器资源

可配置所有容器后端的 CPU、内存、磁盘以及持久化相关参数：

```yaml
terminal:
  backend: docker  # or singularity, modal, daytona, vercel_sandbox
  container_cpu: 1              # CPU cores (default: 1)
  container_memory: 5120        # Memory in MB (default: 5GB)
  container_disk: 51200         # Disk in MB (default: 50GB)
  container_persistent: true    # Persist filesystem across sessions (default: true)
```

当设置 `container_persistent: true` 时，已安装的软件包、文件及配置信息将在不同会话之间保持不变。

### 容器安全机制

所有容器后端均采用强化安全措施运行：

- 只读根文件系统（Docker）
- 禁用所有 Linux 权限能力
- 防止权限提升
- 进程ID限制（最多256个进程）
- 完整的命名空间隔离
- 通过卷实现持久化工作空间，而非使用可写根层

Docker可通过 `terminal.docker_forward_env` 参数接收明确的允许环境变量列表，但被转发的变量对容器内的命令是可见的，应视为该会话中已公开的变量。

## 后台进程管理

启动后台进程并对其进行管理：

```python
terminal(command="pytest -v tests/", background=true)
# Returns: {"session_id": "proc_abc123", "pid": 12345}

# Then manage with the process tool:
process(action="list")       # Show all running processes
process(action="poll", session_id="proc_abc123")   # Check status
process(action="wait", session_id="proc_abc123")   # Block until done
process(action="log", session_id="proc_abc123")    # Full output
process(action="kill", session_id="proc_abc123")   # Terminate
process(action="write", session_id="proc_abc123", data="y")  # Send input
```

PTY 模式（`pty=true`）可支持 Codex 和 Claude Code 等交互式 CLI 工具的运行。

已完成的背景命令会在当前配置文件中保留其退出状态及捕获的输出内容。您可以恢复触发该命令的对话（或其压缩后的延续部分），然后使用原有的 `session_id`，通过 `process(action="log")` 获取输出信息，再通过 `process(action="poll")` 查询退出状态。对于没有关联会话约束的无关对话和请求，即便拥有完全相同的进程标识，也无法读取这些保留的记录。`process(action="list")` 还能显示当前任务或对话的保留结果。

Hermes 会在配置文件所在目录下的 `logs/process-results/` 中保存最新的 **64 个已完成结果**，保存时长最长为完成后的 **7 天**。每条记录最多包含最近 **200,000 个字符**的输出内容，并且始终会应用终端敏感信息屏蔽规则，即便已禁用实时输出屏蔽功能也是如此。这些记录会在后续的读取或写入操作时失效。恢复功能不会重新运行命令或重播完成通知，它仅用于保留在父进程仍在运行时已完成的工作；对于因超时或崩溃而未完成的子进程，则不会继续保留其状态。

## Sudo 支持

在交互式父会话中，受支持的 sudo 命令会使用经过遮蔽的密码提示符（该提示符会在当前会话中缓存）。这包括完整的绝对路径或带引号的可执行文件路径，以及包含常规选项和赋值的 `env` 前缀，例如 `env -u UNUSED /usr/bin/sudo id`。无密码 sudo 操作则无需显示提示符。您也可以在代理机器上的配置文件 `.env` 中设置 `SUDO_PASSWORD`。

诸如 `bash -c 'sudo id'`、`env -S` 这类 Shell 载荷，以及被拆分的字符串、动态生成的可执行文件路径和未被识别的 `env` 选项，均不会被密码重写工具解析。如需交互式提示符，请直接调用 sudo 命令。此类处理方式不会改变审批规则，也不会影响针对代理提供的 sudo 密码的防护机制。

委托的子代理无法显示密码提示符：因为它们的并行操作没有串行化的人类密码输入通道。建议在父会话中执行命令，或在本地设置 `SUDO_PASSWORD`。消息传递型/无界面会话不具备安全的密码回复通道，切勿在聊天中发送密码。

:::warning
在消息平台上，如果 sudo 操作失败，系统会提示可在 `~/.hermes/.env` 文件中添加 `SUDO_PASSWORD`。
:::
