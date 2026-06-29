---
sidebar_position: 1
title: "Tools & Toolsets"
description: "Overview of Hermes Agent's tools — what's available, how toolsets work, and terminal backends"
---

# 工具与工具集

工具是用于扩展智能体功能的函数，它们被整理成逻辑上独立的**工具集**，可根据不同平台进行启用或禁用。

## 可用工具

Hermes 搭载了丰富的内置工具注册表，涵盖网页搜索、浏览器自动化、终端执行、文件编辑、内存管理、任务委托、定时任务、Home Assistant 集成等功能。

:::note
**Honcho 跨会话内存**作为内存提供插件提供（位于 `plugins/memory/honcho/` 目录），并非内置工具集。如需安装，请参阅 [插件](./plugins.md) 文档。
:::

按功能分类的概览：

| 类别 | 示例 | 描述 |
|------|------|------|
| **网页** | `web_search`, `web_extract` | 在网页上搜索并提取页面内容。 |
| **X 平台搜索** | `x_search` | 通过 xAI 内置的 `x_search` 响应工具在 X（Twitter）上搜索帖子和主题——该功能需使用 xAI 凭证（SuperGrok OAuth 或 `XAI_API_KEY`）才能启用；默认处于关闭状态，可通过 `hermes tools` → 🐦 X（Twitter）搜索来开启。 |
| **终端与文件** | `terminal`, `process`, `read_file`, `patch` | 执行命令及操作文件。 |
| **浏览器** | `browser_navigate`, `browser_snapshot`, `browser_vision` | 支持文本处理和视觉识别的交互式浏览器自动化功能。 |
| **多媒体** | `vision_analyze`, `image_generate`, `text_to_speech` | 多模态分析与生成功能。 |
| **智能体编排** | `todo`, `clarify`, `execute_code`, `delegate_task` | 用于任务规划、需求澄清、代码执行以及子智能体委托。 |
| **内存与检索** | `memory`, `session_search` | 实现持久化内存管理及会话内容检索。 |
| **自动化** | `cronjob` | 支持创建、列表查看、更新、暂停、恢复、运行和删除等操作的定时任务。任务发送功能由 cron 自带的发送机制、`hermes send` CLI 以及网关通知器处理，而非通过智能体可调用的工具实现。 |
| **集成服务** | `ha_*`, MCP 服务器工具 | Home Assistant、MCP 及其他集成服务。 |

如需查看基于代码生成的权威工具列表，请参阅 [内置工具参考](/reference/tools-reference) 和 [工具集参考](/reference/toolsets-reference)。

:::tip Nous 工具网关
已订阅付费版 [Nous Portal](https://portal.nousresearch.com) 的用户可通过 **[工具网关](tool-gateway.md)** 使用网页搜索、图像生成、文本转语音及浏览器自动化功能——无需单独的 API 密钥。运行 `hermes model` 即可启用该功能，或通过 `hermes tools` 配置特定工具。
:::

## 工具集的使用方法

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

## 终端后端

终端工具能够在不同的环境中执行命令：

| 后端 | 描述 | 使用场景 |
|---------|-------------|----------|
| `local` | 在您的本地机器上运行（默认） | 开发、需要高度信任的任务 |
| `docker` | 孤立式容器 | 确保安全性与任务可重复性 |
| `ssh` | 远程服务器 | 沙箱环境，防止智能体直接访问自身代码 |
| `singularity` | 高性能计算容器 | 集群计算、无根运行环境 |
| `modal` | 云端执行 | 无服务器架构、弹性扩展 |
| `daytona` | 云端沙箱工作区 | 持久的远程开发环境 |

### 配置选项

```yaml
# In ~/.hermes/config.yaml
terminal:
  backend: local    # or: docker, ssh, singularity, modal, daytona
  cwd: "."          # Working directory
  timeout: 180      # Command timeout in seconds
```

### Docker 后端

```yaml
terminal:
  backend: docker
  docker_image: python:3.11-slim
```

**单个持久化容器，贯穿整个流程。** Hermes在首次使用时会启动一个长期运行的容器（通过`docker run -d ... sleep 2h`实现），并将所有终端操作、文件操作以及`execute_code`调用均通过`docker exec`指令路由至同一个容器中。在工作目录切换、已安装的包、环境配置调整，以及写入 `/workspace` 的文件等内容，都会在Hermes进程的整个运行期间，在不同的工具调用之间、以及通过 `/new`、`/reset` 和 `delegate_task` 子代理之间保持一致。当进程关闭时，该容器也会被停止并移除。

这意味着Docker后端的行为类似于一个持久化的沙箱虚拟机，而非每次命令执行都创建新的容器。一旦您执行了`pip install foo`命令，该包就会在整个会话期间一直存在。如果您执行了`cd /workspace/project`命令，后续的`ls`命令就能看到该目录。有关完整的生命周期管理细节，以及用于控制 `/workspace` 和 `/root` 目录在Hermes重启后是否依然存在的`container_persistent`标志，请参阅[配置 → Docker后端](../configuration.md#docker-backend)。

### SSH后端

出于安全考虑推荐使用此方式——代理程序无法修改自身的代码：

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

### 容器资源

为所有容器后端配置CPU、内存、磁盘以及持久化存储参数：

```yaml
terminal:
  backend: docker  # or singularity, modal, daytona
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
- 通过卷实现持久化工作空间，而非可写根层

Docker可通过 `terminal.docker_forward_env` 参数接收显式的环境变量允许列表，但被转发的变量对容器内的命令是可见的，应视为已暴露于当前会话中。

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

## Sudo 支持

当某个命令需要使用 sudo 权限时，系统会提示您输入密码（该密码会在当前会话中缓存）。或者，您也可以在 `~/.hermes/.env` 文件中设置 `SUDO_PASSWORD`。

:::warning
在消息平台环境中，如果使用 sudo 失败，系统会给出提示，建议将 `SUDO_PASSWORD` 设置在 `~/.hermes/.env` 文件中。
:::
