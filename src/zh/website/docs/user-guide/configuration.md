---
sidebar_position: 2
title: "Configuration"
description: "Configure Hermes Agent — config.yaml, providers, models, API keys, and more"
---

# 配置

所有设置均存储在 `~/.hermes/` 目录中，便于随时访问。

:::提示 如何最便捷地创建可用的 `config.yaml` 文件
运行 `hermes setup --portal` 即可——只需完成一次 OAuth 认证，即可获得模型提供方以及四种 Tool Gateway 工具，无需手动编辑 YAML 文件。Portal 用户在使用按令牌计费的提供方服务时还可享受 10% 的折扣。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 目录结构

```text
~/.hermes/
├── config.yaml     # Settings (model, terminal, TTS, compression, etc.)
├── .env            # API keys and secrets
├── auth.json       # OAuth provider credentials (Nous Portal, etc.)
├── SOUL.md         # Primary agent identity (slot #1 in system prompt)
├── memories/       # Persistent memory (MEMORY.md, USER.md)
├── skills/         # Agent-created skills (managed via skill_manage tool)
├── cron/           # Scheduled jobs
├── sessions/       # Gateway sessions
└── logs/           # Logs (errors.log, gateway.log — secrets auto-redacted)
```

## 配置管理

```bash
hermes config              # View current configuration
hermes config edit         # Open config.yaml in your editor
hermes config set KEY VAL  # Set a specific value
hermes config check        # Check for missing options (after updates)
hermes config migrate      # Interactively add missing options

# Examples:
hermes config set model anthropic/claude-opus-4
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...  # Saves to .env
```

:::提示  
`hermes config set` 命令会自动将配置值路由到正确的文件中——API 密钥会被保存到 `.env` 文件中，而其他所有配置则存储在 `config.yaml` 中。  
:::

## 配置优先级  

配置项的解析顺序如下（优先级从高到低）：  

1. **CLI 参数**——例如 `hermes chat --model anthropic/claude-sonnet-4`（每次调用时可覆盖现有设置）  
2. **`~/.hermes/config.yaml`**——所有非敏感配置的主要存储文件  
3. **`~/.hermes/.env`**——环境变量的备用存储位置；对于敏感信息（如 API 密钥、令牌、密码）则**必须**使用此文件  
4. **内置默认值**——当未设置任何其他配置时，将使用硬编码的安全默认值  

:::信息提示  
敏感信息（如 API 密钥、机器人令牌、密码）应存储在 `.env` 文件中；其余配置（如模型类型、终端后端、压缩设置、内存限制、工具集等）则应存放在 `config.yaml` 中。若两者都进行了配置，对于非敏感项，则以 `config.yaml` 中的设置为准。  
:::

:::提示 组织级部署  
管理员可通过系统级管理目录，锁定某些特定的配置和敏感值，防止普通用户对其进行覆盖。详情请参阅[管理范围](/user-guide/managed-scope)。  
:::

## 环境变量替换  

您可以在 `config.yaml` 中使用 `${VAR_NAME}` 语法来引用环境变量：

```yaml
auxiliary:
  vision:
    api_key: ${GOOGLE_API_KEY}
    base_url: ${CUSTOM_VISION_URL}

delegation:
  api_key: ${DELEGATION_KEY}
```

单个值中可包含多个引用，格式如下：`url: "${HOST}:${PORT}"`。若被引用的变量未设置，则该占位符将保持原样（例如 `${UNDEFINED_VAR}` 仍为原始形式）。仅支持 `${VAR}` 这种语法——单独的 `$VAR` 格式不会被解析。

关于 AI 提供商的配置（包括 OpenRouter、Anthropic、Copilot、自定义端点、自托管大语言模型以及备用模型等），请参阅 [AI 提供商](/integrations/providers) 部分。

### 提供商超时设置

您可以为整个提供商设置全局请求超时时间，即 `providers.<id>.request_timeout_seconds`；同时也可为特定模型设置单独的超时值，即 `providers.<id>.models.<model>.timeout_seconds`。此设置适用于所有传输方式下的主轮询客户端（包括 OpenAI-wire、原生 Anthropic 接口及兼容 Anthropic 的接口）、备用请求链、凭据更换后的模型重建过程，以及（针对 OpenAI-wire）每个请求的超时参数——因此配置的值会优先于旧的 `HERMES_API_TIMEOUT` 环境变量。

此外，您还可以为非流式旧请求检测器设置超时时间，即 `providers.<id>.stale_timeout_seconds`；并为特定模型设置单独的超时值，即 `providers.<id>.models.<model>.stale_timeout_seconds`。此设置同样会优先于旧的 `HERMES_API_CALL_STALE_TIMEOUT` 环境变量。

若未对这些参数进行配置，则会沿用旧有的默认值（`HERMES_API_TIMEOUT=1800` 秒，`HERMES_API_CALL_STALE_TIMEOUT=300` 秒，原生 Anthropic 为 900 秒左右）。目前 AWS Bedrock 并不支持此功能（无论是 `bedrock_converse` 还是 AnthropicBedrock SDK，均使用带有独立超时配置的 boto3 库）。相关示例可见 [`cli-config.yaml.example`](https://github.com/NousResearch/hermes-agent/blob/main/cli-config.yaml.example) 文件中的注释说明。

## 更新行为

`hermes update` 的相关设置位于 `config.yaml` 文件的 `updates` 部分：

```yaml
updates:
  pre_update_backup: false       # Create a full HERMES_HOME zip before every update
  backup_keep: 5                 # Keep this many pre-update backup zips
  non_interactive_local_changes: stash  # stash | discard
```

在通过 Git 安装的情况下，Hermes 会在检出更新分支或拉取代码之前，自动将已跟踪的修改文件以及未跟踪的文件暂存起来。在恢复这些暂存内容之前，交互式终端会先给出确认提示。而非交互式更新方式（如桌面/聊天应用、网关，或使用 `--yes` 参数）则会使用 `updates.non_interactive_local_changes` 参数：若选择 `stash`，则会在成功拉取代码后恢复本地的代码修改；若选择 `discard`，则会在成功拉取后直接丢弃此次更新所产生的暂存内容。仅限于那些本地代码修改根本无需保留的托管式安装环境中才应使用 `discard`。

在执行暂存操作之前，Hermes 还会恢复因 npm install/build 操作而产生的已跟踪的 `package-lock.json` 差异文件。在进行更新之前，请先将有意进行的锁文件修改提交或手动暂存。

## 终端后端配置

Hermes 支持六种终端后端。每种后端都决定了代理的 Shell 命令实际在何处执行——可以是您的本地机器、Docker 容器、通过 SSH 连接的远程服务器、Modal 云沙箱（直接连接或通过 Nous 管理的网关）、Daytona 工作空间，或是 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | singularity
  cwd: "."          # Gateway/cron working directory (CLI always uses launch dir)
  timeout: 180      # Per-command timeout in seconds
  home_mode: auto   # auto | real | profile — subprocess HOME policy
  env_passthrough: []  # Env var names to forward to sandboxed execution (terminal + execute_code)
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Container image for Singularity backend
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Container image for Modal backend
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Container image for Daytona backend
```

对于 Modal 和 Daytona 等云沙箱环境，`container_persistent: true` 的含义是 Hermes 会尝试在重新创建沙箱时保留文件系统状态。但该设置并不能保证后续仍然运行着相同的实时沙箱、进程 ID 空间或后台进程。

### 后端概述

| 后端类型 | 命令执行位置 | 隔离级别 | 最佳适用场景 |
|---------|-------------------|-----------|----------|
| **本地** | 直接在您的机器上运行 | 无隔离 | 开发、个人使用 |
| **Docker** | 单个持久化 Docker 容器（跨会话、/new 模式及子代理共享） | 完全隔离（命名空间、权限限制） | 安全的沙箱环境、CI/CD 流水线 |
| **SSH** | 通过 SSH 连接的远程服务器 | 网络级隔离 | 远程开发、高性能硬件环境 |
| **Modal** | Modal 云沙箱 | 完全隔离（云虚拟机） | 临时性云计算任务、代码评估 |
| **Daytona** | Daytona 工作空间 | 完全隔离（云容器） | 受管理的云开发环境 |
| **Singularity** | Singularity/Apptainer 容器 | 命名空间隔离（--containall 参数） | 高性能计算集群、共享机器环境 |

### 本地后端

为默认后端类型。命令直接在您的机器上运行，且不进行任何隔离处理。无需特殊配置即可使用。

```yaml
terminal:
  backend: local
```

默认情况下，本地工具的子进程会保留您真实操作系统用户的主目录 `HOME`。这样一来，诸如 `git`、`ssh`、`gh`、`az`、`npm`、Claude Code 以及 Codex 等外部 CLI 就能使用其在常规终端中已有的凭证和配置。Hermes 的状态仍通过 `HERMES_HOME` 按配置文件进行管理；而 `HOME` 并非配置文件选择配置、内存、会话或技能的依据。

Hermes **不会**更改您系统级的主目录 `HOME`、shell 启动文件或操作系统账户的主目录。该设置仅用于控制通过 `terminal`、后台终端进程、`execute_code` 以及 ACP 辅助进程等工具所启动的子进程所接收的环境。

#### `terminal.home_mode`

| 模式 | 主机环境 | 容器环境 | 权衡点 |
|---|---|---|---|
| `auto` | 保留真实操作系统用户的主目录 `HOME` | 使用 `{HERMES_HOME}/home` | 推荐的默认模式。主机 CLI 可继续正常工作，且容器状态也能得以保留。 |
| `real` | 强制使用真实操作系统用户的主目录 `HOME` | 若可见则强制使用真实操作系统用户的主目录 `HOME` | 当父进程意外以指向配置文件主目录的 `HOME` 值启动时，此模式非常有用。 |
| `profile` | 若存在则使用 `{HERMES_HOME}/home` | 若存在则使用 `{HERMES_HOME}/home` | 能实现严格的按配置文件隔离 CLI 配置，但除非在配置文件主目录内进行初始化或关联，否则常规的 `~/.ssh`、`~/.gitconfig`、`~/.azure`、`~/.config/gh`、Claude/Codex 认证信息、npm 状态等将不可见。 |

默认模式的缺点在于，不同配置文件会共享位于 `~` 下的相同用户级 CLI 凭证和配置。如果您需要为某个配置文件设置独立的 git 身份、SSH 密钥、GitHub CLI 登录信息、npm 配置或云服务 CLI 登录信息，建议使用 `home_mode: profile` 并在该配置文件主目录内主动初始化这些工具。

如果您确实需要严格的按配置文件隔离工具配置，可设置为：

```yaml
terminal:
  home_mode: profile
```

在该模式下，工具的子进程会将 `{HERMES_HOME}/home` 作为 `HOME` 环境变量使用。Hermes 还会设置 `HERMES_REAL_HOME`，以便脚本在需要时仍能找到真正的用户主目录。在“自动”模式下，容器后端依然会使用 `{HERMES_HOME}/home`，因为该目录位于持久化的 Hermes 数据卷中。

那些需要区分配置文件所在位置与真实用户主目录的脚本，建议将 Hermes 数据存储路径设为 `HERMES_HOME`，而将账户主目录路径设为 `HERMES_REAL_HOME`。

```python
from pathlib import Path
import os

hermes_home = Path(os.environ["HERMES_HOME"])
real_home = Path(os.environ.get("HERMES_REAL_HOME", os.environ["HOME"]))
```

:::warning
该智能体拥有与您的用户账户相同的文件系统访问权限。如需禁用不需要的工具，可使用 `hermes tools`；若希望实现沙箱隔离，则可切换至 Docker 环境。
:::

### Docker 后端

命令将在经过安全加固的 Docker 容器中执行（所有特殊权限均已移除，不存在权限提升风险，同时设置了 PID 限制）。

**采用单个持久化容器，供 Hermes 的所有进程共享。** Hermes 在首次使用时会启动一个长期运行的容器，随后所有的终端操作、文件操作以及 `execute_code` 调用，都会通过 `docker exec` 命令指向同一个容器——无论是在不同会话之间、使用 `/new`、`/reset` 或 `delegate_task` 子智能体时皆是如此。工作目录、已安装的软件包、/workspace 目录中的文件以及**后台进程**，都会在连续的命令调用之间以及不同的 Hermes 进程之间保持一致。当您关闭 TUI 会话、运行 `/quit` 命令或启动新的 `hermes` 实例时，该容器仍会继续运行，下一个 Hermes 进程会通过标签查找机制重新使用它。具体的容器销毁规则请参见下文的“容器生命周期”部分。

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # Mount launch dir into /workspace
  docker_run_as_host_user: false   # See "Running container as host user" below
  docker_forward_env:              # Host env vars to forward into container
    - "GITHUB_TOKEN"
  docker_env:                      # Literal env vars to inject (KEY=value)
    DEBUG: "1"
    PYTHONUNBUFFERED: "1"
  docker_volumes:                  # Host directory mounts
    - "/home/user/projects:/workspace/projects"
    - "/home/user/data:/data:ro"   # :ro for read-only
  docker_extra_args:               # Extra flags appended verbatim to `docker run`
    - "--gpus=all"
    - "--network=host"

  # Resource limits
  container_cpu: 1                 # CPU cores (0 = unlimited)
  container_memory: 5120           # MB (0 = unlimited)
  container_disk: 51200            # MB (requires overlay2 on XFS+pquota)
  container_persistent: true       # Persist /workspace and /root bind-mount dirs

  # Cross-process container reuse (defaults match the "one long-lived
  # container shared across sessions" contract — see Container lifecycle).
  docker_persist_across_processes: true   # Reuse container across Hermes restarts
  docker_orphan_reaper: true              # Sweep abandoned Exited containers at startup

  # Cross-backend lifecycle settings (apply to docker as well)
  timeout: 180                     # Per-command timeout in seconds
  lifetime_seconds: 300            # Idle-reaper window; also feeds 2× orphan-reaper threshold
```

**`docker_env`** 与 **`docker_forward_env`** 的区别：前者会直接注入你在配置中指定的 `KEY=value` 对（这些值来自 `config.yaml`，或通过 `TERMINAL_DOCKER_ENV='{"DEBUG":"1"}'` 以 JSON 字典形式传递）。后者则从你的 shell 或 `~/.hermes/.env` 中读取值，因此敏感信息永远不会出现在配置文件中。对于令牌类凭证，请使用 `docker_forward_env`；而对于容器所需的静态参数，则可使用 `docker_env`。

**`terminal.docker_extra_args`**（也可通过 `TERMINAL_DOCKER_EXTRA_ARGS='["--gpus=all"]'` 覆盖）允许你传递那些 Hermes 未将其作为标准键项提供的任意 `docker run` 参数——如 `--gpus`、`--network`、`--add-host`，以及自定义的 `--security-opt` 设置等。每个参数都必须是字符串形式，该参数列表会被追加到最终生成的 `docker run` 命令中，从而在必要时覆盖 Hermes 的默认设置。请谨慎使用此类参数——任何与沙箱安全机制相冲突的选项（如权限降级、`--user` 设置、工作区绑定挂载等）都可能悄悄降低隔离强度。

**系统要求：** 需要已安装并正在运行的 Docker Desktop 或 Docker Engine。Hermes 会扫描 `$PATH` 及 macOS 上常见的 Docker 安装路径（如 `/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用程序包）。Podman 也支持直接使用：若系统中同时安装了 Docker 和 Podman，可设置 `HERMES_DOCKER_BINARY=podman`（或完整路径）来强制使用 Podman。

#### 容器生命周期

每个由 Hermes 管理的容器都会被添加三个标签，以便后续进程及孤儿清理进程能够识别它：

- `hermes-agent=1` — 标记该容器为 Hermes 管理；
- `hermes-task-id=<经过过滤的任务ID>` — 用于标识每个任务的重复使用情况；
- `hermes-profile=<经过过滤的配置文件名>` — 将重复使用和清理操作限制在当前活跃的 Hermes 配置文件范围内。

启动时，Hermes 会执行 `docker ps --filter label=hermes-task-id=<id> --filter label=hermes-profile=<profile>` 命令，一旦找到对应的容器就会**直接附加到该容器上**。如果容器已“退出”（例如因 Docker 守护进程重启），Hermes 会重新启动它并继续使用——文件系统状态及已安装的软件包会保留，但容器内的后台进程则不会。

当某个 Hermes 进程退出——无论是通过 `/quit` 命令、关闭 TUI 会话、网关关闭，还是收到 SIGKILL 信号——在默认模式下，**容器本身不会被清理**，而是继续运行。下一个 Hermes 进程会通过标签检测在几毫秒内重新附加到该容器上。这正是“跨会话共享一个长期运行的容器”这一设计理念所要求的：只有这样，后台进程（如 npm 监听器、开发服务器、长时间运行的 pytest 等）才能在会话切换后依然存活。

**只有在以下情况下，容器才会被终止（即先停止，再执行 `docker rm -f` 命令删除）：**

| 触发条件 | 触发时机 |
|---|---|
| `docker_persist_across_processes: false` | 显式要求进程级隔离。此时每个 `cleanup()` 函数都会执行 `stop` + `rm -f` 操作，行为与版本 #20561 发布前的设置一致。 |
| 孤儿清理进程（基于 `lifetime_seconds`，默认为 300 秒） | 仅当环境变量 `persist_across_processes=false` 时才会触发。处于持久模式下的容器不会被清理，可顺利度过空闲期。 |
| 下次启动时的孤儿清理进程 | 会清理所有标记为 hermes、且已“退出”且年龄超过 `2 × lifetime_seconds`（默认为 600 秒，即 10 分钟）的容器，清理范围仅限于当前配置文件。**正在运行的容器绝不会被清理**，这是为了确保进程间的安全性。如需禁用此功能，可设置 `docker_orphan_reaper: false`。 |
| 用户直接操作 | 执行 `docker rm -f`、`docker system prune` 命令，或重启 Docker Desktop。由于我们没有设置 `--restart=always`，因此主机重启后容器会处于“已退出”状态（其写时复制层仍会保留，并在下次启动时被重新使用，但后台进程已消失）。 |

一些值得注意的边缘情况：

- 若容器内的 PID 1 进程因内存不足被系统杀死，容器状态会变为“已退出”。下次重复使用时，Hermes 会重新启动该容器；文件系统状态仍可保留，但后台进程已不复存在。
- **切换配置文件**会导致容器之间相互隔离——标记为 `hermes-profile=work` 的容器对正在运行在 `hermes-profile=research` 配置文件下的 Hermes 进程来说是不可见的。孤儿清理进程也以配置文件为单位工作，因此跨配置文件的容器不会被意外清理，但除非你在原有配置文件下重新启动 Hermes，否则它们也不会被自动清理。

通过 `delegate_task(tasks=[...])` 生成的并行子代理会共享同一个容器——因此同时进行的 `cd` 操作、环境变量修改以及对同一路径的写入都可能发生冲突。如果某个子代理需要独立的沙箱环境，就必须通过 `register_task_env_overrides()` 方法注册针对该任务的镜像覆盖配置，而强化学习及基准测试环境（如 TerminalBench2、HermesSweEnv 等）则会自动为其每个任务对应的 Docker 镜像完成此类配置。

**安全加固措施：**
- 使用 `--cap-drop ALL`，仅恢复 `DAC_OVERRIDE`、`CHOWN`、`FOWNER` 这三项权限；
- 设置 `--security-opt no-new-privileges`；
- 限制进程数量为 256 个；
- 为 `/tmp`（512MB）、`/var/tmp`（256MB）、`/run`（64MB）设置大小限制的临时文件系统。

**凭证传递机制：** 列在 `docker_forward_env` 中的环境变量会首先从你的 shell 环境中获取值，若未找到则从 `~/.hermes/.env` 中读取。技能模块也可以声明 `required_environment_variables`，这些变量也会被自动合并进来。

#### 环境变量覆盖方式

`terminal:` 下的每个键都有一个形式为 `TERMINAL_<KEY_UPPERCASE>` 的环境变量覆盖项。对于 Docker 后端而言，最常用的覆盖项如下：

| 环境变量 | 对应的配置项 | 说明 |
|---|---|---|
| `TERMINAL_DOCKER_IMAGE` | `docker_image` | 基础镜像 |
| `TERMINAL_DOCKER_FORWARD_ENV` | `docker_forward_env` | JSON 数组形式，例如 `'["GITHUB_TOKEN","OPENAI_API_KEY"]'` |
| `TERMINAL_DOCKER_ENV` | `docker_env` | JSON 字典形式，例如 `'{"DEBUG":"1"}'` |
| `TERMINAL_DOCKER_VOLUMES` | `docker_volumes` | JSON 数组，元素为 `"host:container[:ro]"` 格式的字符串 |
| `TERMINAL_DOCKER_EXTRA_ARGS` | `docker_extra_args` | JSON 数组 |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | `docker_mount_cwd_to_workspace` | 值可为 `true` 或 `false` |
| `TERMINAL_DOCKER_RUN_AS_HOST_USER` | `docker_run_as_host_user` | 值可为 `true` 或 `false` |
| `TERMINAL_DOCKER_PERSIST_ACROSS_PROCESSES` | `docker_persist_across_processes` | 值可为 `true` 或 `false`，默认值为 `true` |
| `TERMINAL_DOCKER_ORPHAN_REAPER` | `docker_orphan_reaper` | 值可为 `true` 或 `false`，默认值为 `true` |
| `TERMINAL_CONTAINER_CPU` | `container_cpu` | 指定的 CPU 核心数 |
| `TERMINAL_CONTAINER_MEMORY` | `container_memory` | 指定的内存大小，单位为 MB |
| `TERMINAL_CONTAINER_DISK` | `container_disk` | 指定的磁盘空间大小，单位为 MB |
| `TERMINAL_CONTAINER_PERSISTENT` | `container_persistent` | 值可为 `true` 或 `false`，用于控制工作区目录的绑定挂载，与 `docker_persist_across_processes` 功能不同 |
| `TERMINAL_LIFETIME_SECONDS` | `lifetime_seconds` | 孤儿清理进程的空闲等待时间 |
| `TERMINAL_TIMEOUT` | `timeout` | 每条命令的执行超时时间 |
| `HERMES_DOCKER_BINARY` | 无对应配置项 | 用于强制指定特定的 docker 或 podman 可执行文件路径 |

### SSH 后端

通过 SSH 在远程服务器上执行命令。该后端使用 ControlMaster 实现连接复用，具备 5 分钟的空闲保持机制。默认情况下会启用持久化 shell——这样命令执行间的状态（如当前工作目录、环境变量等）都会被保留下来。

```yaml
terminal:
  backend: ssh
  persistent_shell: true           # Keep a long-lived bash session (default: true)
```

**必需的环境变量：**

```bash
TERMINAL_SSH_HOST=my-server.example.com
TERMINAL_SSH_USER=ubuntu
```

**可选参数：**

| 参数名 | 默认值 | 说明 |
|--------|--------|------|
| `TERMINAL_SSH_PORT` | `22` | SSH 端口 |
| `TERMINAL_SSH_KEY` | （系统默认值） | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | `true` | 启用持久化 shell |

**工作原理：** 在初始化时以 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 的参数建立连接。持久化 shell 会在远程主机上保持一个 `bash -l` 进程运行，通过临时文件进行通信。需要 `stdin_data` 或 `sudo` 权限的命令会自动切换为一次性执行模式。

### Modal 后端

在 [Modal](https://modal.com) 云沙箱中执行命令。每个任务都会获得一个独立的虚拟机，其 CPU、内存和磁盘资源均可配置。文件系统支持在不同会话之间进行快照创建与恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU cores
  container_memory: 5120           # MB (5GB)
  container_disk: 51200            # MB (50GB)
  container_persistent: true       # Snapshot/restore filesystem
```

**必需项：** 要么提供 `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` 环境变量，要么提供 `~/.modal.toml` 配置文件。

**状态持久化：** 开启该功能后，沙箱文件系统会在清理时生成快照，并在下次会话时恢复。这些快照会存储在 `~/.hermes/modal_snapshots.json` 文件中。此功能可保留文件系统状态，但无法保存正在运行的进程、PID 空间或后台任务。

**凭证文件：** 会自动从 `~/.hermes/` 目录加载凭证文件（如 OAuth 令牌等），并在执行每个命令之前进行同步。

### Daytona 后端

在 [Daytona](https://daytona.io) 管理的工作空间中运行命令。支持暂停/继续操作以实现状态持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU cores
  container_memory: 5120           # MB → converted to GiB
  container_disk: 10240            # MB → converted to GiB (max 10 GiB)
  container_persistent: true       # Stop/resume instead of delete
```

**必需：** `DAYTONA_API_KEY` 环境变量。

**持久性：** 当该功能启用时，沙箱会在清理时被暂停（而非删除），并在下次会话时重新启动。沙箱的名称遵循 `hermes-{task_id}` 的格式。

**磁盘限制：** Daytona 设定的最大磁盘使用量为 10 GiB。超过此限制的请求将会被限制并同时发出警告。

### Singularity/Apptainer 后端

在 [Singularity/Apptainer](https://apptainer.org) 容器中执行命令。该后端专为那些无法使用 Docker 的高性能计算集群及共享机器设计。

```yaml
terminal:
  backend: singularity
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"
  container_cpu: 1                 # CPU cores
  container_memory: 5120           # MB
  container_persistent: true       # Writable overlay persists across sessions
```

**系统要求：** `$PATH` 环境变量中需包含 `apptainer` 或 `singularity` 可执行文件。

**镜像处理：** Docker 链接（`docker://...`）会自动转换为 SIF 格式文件并予以缓存；现有的 `.sif` 文件则可直接使用。

**临时存储目录：** 优先级顺序如下：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent`（适用于高性能计算环境）→ `~/.hermes/sandboxes/singularity`。

**隔离机制：** 通过 `--containall --no-home` 参数实现完整的命名空间隔离，同时避免挂载主机用户主目录。

### 常见终端后端问题

如果终端命令立即失败，或系统提示终端工具不可用：

- **本地模式（Local）** — 无特殊要求，是入门时的最安全默认选项。
- **Docker模式** — 运行 `docker version` 命令确认 Docker 正常运行。若失败，请修复 Docker 环境，或通过 `hermes config set terminal.backend local` 强制使用本地模式。
- **SSH模式** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER` 参数。缺少任一参数时，Hermes 会输出明确的错误信息。
- **Modal模式** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml` 配置文件。可通过运行 `hermes doctor` 命令进行检查。
- **Daytona模式** — 需要 `DAYTONA_API_KEY`。Daytona SDK 负责处理服务器地址的配置。
- **Singularity模式** — 需要 `$PATH` 中包含 `apptainer` 或 `singularity` 可执行文件，此模式在高性能计算集群中较为常见。

如有疑问，可先将 `terminal.backend` 设置回 `local` 模式，确认命令在该模式下能正常运行。

### 会话关闭时的远程到主机文件同步

对于 **SSH**、**Modal** 和 **Daytona** 后端（即代理的工作目录位于与运行 Hermes 的主机不同的机器上），Hermes 会跟踪代理在远程沙箱中修改过的文件。在会话关闭或沙箱清理时，这些被修改的文件会**同步回主机**，存储路径为 `~/.hermes/cache/remote-syncs/<session-id>/`。

- 触发条件包括：会话关闭、执行 `/new` 或 `/reset` 命令、网关消息超时，以及子代理使用远程后端完成 `delegate_task` 任务时。
- 同步范围涵盖代理修改过的所有文件，而不仅限于其明确打开的文件；文件的添加、修改和删除操作都会被记录下来。
- 等您查看时，远程沙箱可能已被销毁，此时本地的 `~/.hermes/cache/remote-syncs/…` 文件才是反映代理实际修改内容的权威记录。
- 对于体积较大的二进制输出文件（如模型检查点、原始数据集），同步时会根据 `file_sync_max_mb`（默认值为 100 MB）设置大小上限。如果预计会有更大的文件被同步回来，可调整该阈值。

```yaml
terminal:
  file_sync_max_mb: 100     # default — sync files up to 100 MB each
  file_sync_enabled: true   # default — set false to skip the sync entirely
```

如此即可从会在会话结束后被销毁的临时云沙箱中恢复数据，而无需每次都明确指示智能体使用 `scp` 或 `modal volume put` 命令来传输各个文件。

### Docker卷挂载

在使用Docker后端时，`docker_volumes`功能可让你将主机目录与容器共享。每条配置项均采用标准的Docker `-v`语法：`host_path:container_path[:options]`。

```yaml
terminal:
  backend: docker
  docker_volumes:
    - "/home/user/projects:/workspace/projects"   # Read-write (default)
    - "/home/user/datasets:/data:ro"              # Read-only
    - "/home/user/.hermes/cache/documents:/output" # Gateway-visible exports
```

此功能适用于以下场景：  
- **向智能体提供文件**（数据集、配置文件、参考代码）；  
- **从智能体接收文件**（生成的代码、报告、导出结果）；  
- **共享工作空间**，让您与智能体能够访问相同的文件。  

如果您使用消息网关，并希望让智能体通过 `MEDIA:/...` 发送生成的文件，建议使用主机可访问的专用导出挂载路径，例如 `/home/user/.hermes/cache/documents:/output`。  
- 在 Docker 容器中，将文件写入 `/output/...`；  
- 在 `MEDIA:` 中指定**主机路径**，例如：`MEDIA:/home/user/.hermes/cache/documents/report.txt`；  
- 除非网关进程在主机上确实存在该路径，否则请勿使用 `/workspace/...` 或 `/output/...`。  

:::warning  
YAML 文件中重复的键会自动覆盖之前的值。如果您已存在 `docker_volumes:` 块，请将新的挂载项合并到同一列表中，而不要在文件后部再添加另一个 `docker_volumes:` 键。  
:::  

该设置也可通过环境变量配置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组格式）。  

### Docker 凭证转发  

默认情况下，Docker 终端会话不会继承主机的任意凭据。如果您需要在容器内使用特定令牌，请将其添加到 `terminal.docker_forward_env` 中。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 会首先从您当前的 shell 中解析列出的各个变量，如果这些变量是通过 `hermes config set` 保存的，则会回退到 `~/.hermes/.env` 文件中查找。

:::warning
在 `docker_forward_env` 中列出的任何内容都会被容器内的命令所读取。请仅转发那些您愿意在终端会话中公开的凭据。
:::

### 以主机用户身份运行容器

默认情况下，Docker 容器是以 `root`（UID 0）用户身份运行的。在 `/workspace` 或其他绑定挂载目录中创建的文件，其所有权最终属于主机上的 root 用户。因此，在结束会话后，您需要先使用 `sudo chown` 命令更改文件所有权，才能通过主机上的编辑器对其进行修改。`terminal.docker_run_as_host_user` 参数可解决这一问题：

```yaml
terminal:
  backend: docker
  docker_run_as_host_user: true   # default: false
```

启用该功能后，Hermes 会在 `docker run` 命令中添加 `--user $(id -u):$(id -g)` 参数，这样一来，写入绑定挂载目录（如 `/workspace`、`/root` 以及 `docker_volumes` 中的任何目录）的文件将归属于宿主机用户而非 root 用户。相应的代价是：容器将无法再执行 `apt install` 操作，也无法向 root 所拥有的路径（如 `/root/.npm`）写入数据。如果需要同时满足这两点需求，可使用 `HOME` 目录归属于非 root 用户的基础镜像（或是在构建镜像时自行添加所需的工具）。

若希望保持向后兼容性，可将其保持为默认值 `false`。只有当您的工作流程主要以“编辑宿主机挂载的文件”为主，且厌倦了频繁使用 `sudo chown -R` 命令时，才建议启用此功能。

### 可选：将启动目录挂载到 `/workspace`

默认情况下，Docker 沙箱是相互隔离的。除非您明确选择，否则 Hermes 不会将当前宿主机的工作目录传递给容器。

可在 `config.yaml` 中启用该功能：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用该功能时：
- 若从 `~/projects/my-app` 启动 Hermes，该主机目录将会被绑定挂载到 `/workspace`；
- Docker 后端将在 `/workspace` 中启动；
- 文件操作工具与终端命令都能访问同一个已挂载的项目目录。

若禁用该功能，则 `/workspace` 仍由沙箱环境拥有，除非通过 `docker_volumes` 显式挂载其他目录。

相关的安全权衡如下：
- 设置为 `false` 可保持沙箱隔离边界；
- 设置为 `true` 则允许沙箱直接访问用于启动 Hermes 的目录。

仅当您确实希望容器能够操作宿主机上的实时文件时，才应启用此功能。

### 持久化 Shell

默认情况下，每个终端命令都在独立的子进程中运行——工作目录、环境变量以及 shell 变量会在不同命令之间重置。当启用**持久化 Shell**后，一个长期运行的 bash 进程会在多次 `execute()` 调用之间保持活跃，从而使命令间的状态得以保留。

这一功能对于**SSH 后端**尤为实用，因为它还能消除每次命令执行时的连接开销。SSH 后端默认启用持久化 Shell，而本地后端则默认禁用该功能。

```yaml
terminal:
  persistent_shell: true   # default — enables persistent shell for SSH
```

如需禁用：

```bash
hermes config set terminal.persistent_shell false
```

**跨命令持续有效的内容：**
- 工作目录（执行 `cd /tmp` 后，该设置会在后续命令中保持不变）
- 导出的环境变量（如 `export FOO=bar`）
- Shell 变量（如 `MY_VAR=hello`）

**优先级规则：**

| 级别 | 变量名 | 默认值 |
|-------|--------|---------|
| 配置文件 | `terminal.persistent_shell` | `true` |
| SSH 覆盖值 | `TERMINAL_SSH_PERSISTENT` | 以配置文件中的值为准 |
| 本地覆盖值 | `TERMINAL_LOCAL_PERSISTENT` | `false` |

后端特定的环境变量具有最高优先级。若希望在本地后端也实现持久化 Shell 环境，可进行相应设置：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
由于持久化shell的stdin已被IPC协议占用，因此那些需要`stdin_data`参数或sudo权限的命令会自动切换为单次执行模式。
:::

如需了解各后端的详细信息，请参阅[代码执行功能](features/code-execution.md)以及[README中的终端相关章节](features/tools.md)。

## 技能设置

技能可通过其SKILL.md前置内容自行定义配置选项。这些非敏感值（如路径、偏好设置、域名配置等）会被存储在`config.yaml`文件中的`skills.config`命名空间下。

```yaml
skills:
  config:
    myplugin:
      path: ~/myplugin-data   # Example — each skill defines its own keys
```

**技能设置的工作原理：**

- `hermes config migrate` 会扫描所有已启用的技能，找出未配置的设置，并提示您进行输入。
- `hermes config show` 会在“技能设置”栏目下显示所有技能设置及其所属的技能名称。
- 当某个技能加载时，其解析后的配置值会自动注入到该技能的上下文中。

**手动设置值：**

```bash
hermes config set skills.config.myplugin.path ~/myplugin-data
```

如需了解在自定义技能中声明配置设置的详细信息，请参阅[创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

### 对智能体创建的技能内容的写入进行防护

当智能体使用 `skill_manage` 功能来创建、编辑、修改或删除某个技能时，Hermes 可以选择性地扫描新生成或已更新的内容，以检测是否存在危险的关键词模式（如凭证窃取、明显的提示词注入、数据外传指令等）。该扫描功能**默认处于关闭状态**——因为那些确实需要访问 `~/.ssh/` 目录或包含 `$OPENAI_API_KEY` 的真实智能体工作流，常常会误触发该检测机制。如果您希望在智能体写入技能内容之前收到提醒，可以重新开启此功能：

```yaml
skills:
  guard_agent_created: true   # default: false
```

当该功能开启后，所有被标记为 `skill_manage` 类型的写入操作都会以审批提示的形式出现，并附带扫描器给出的理由。获批准的写入操作会成功执行；而被拒绝的写入操作则会向智能体返回说明性的错误信息。

### 对技能写入操作的审批机制

独立于上述内容扫描器之外，`skills.write_approval` 会要求对**所有**智能体技能相关的写入操作（创建、编辑、修补、删除及相关文件）进行手动批准——其审批/拒绝机制与处理危险命令的机制完全相同。

```yaml
skills:
  write_approval: false   # false = write freely (default) | true = stage every write for review
```

当该功能处于开启状态时，技能写入操作会被暂存于 `~/.hermes/pending/skills/` 目录中，随后可通过 CLI 或任何消息平台，使用 `/skills pending`、`/skills diff <id>`、`/skills approve <id>`、`/skills reject <id>` 等命令对其进行审核。也可在运行时通过 `/skills approval on|off` 来切换此功能状态。内存相关操作同样遵循相同的审批机制（即下文的 `memory.write_approval`）。完整操作指南请参阅：[对代理技能写入操作进行管控](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval)。

## 内存配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
  write_approval: false     # true = require approval before any memory write
```

当设置 `memory.write_approval: true` 时，所有内存写入操作在生效前都需要经过您的确认：交互式 CLI 会直接在提示语中显示相关选项；而对于消息交流会话及后台自我优化阶段，则会将写入内容暂存为 `/memory pending`，随后进入 `/memory approve <id>` / `/memory reject <id>` 的审核流程。您可以在运行时通过 `/memory approval on|off` 来切换此功能。详情请参阅[控制内存写入](/user-guide/features/memory#controlling-memory-writes-write_approval)。

## 上下文文件截断设置

该选项用于控制 Hermes 在对上下文文件进行开头/结尾截断处理之前，会加载多少内容。这一设置适用于注入系统提示语中的各类文件，例如 `SOUL.md`、`.hermes.md`、`AGENTS.md`、`CLAUDE.md` 以及 `.cursorrules`。需要注意的是，它**不会**影响 `read_file` 工具的功能。

```yaml
context_file_max_chars: 20000  # default
```

当您有意保留较大的身份信息或项目上下文文件，并使用具有足够上下文窗口的模型来处理这些数据时，应设置该参数。

```yaml
context_file_max_chars: 25000
```

## 文件读取安全性

该机制用于控制单次 `read_file` 调用可返回的内容量。超出限制的读取请求将会被拒绝，并给出错误提示，建议智能体使用 `offset` 和 `limit` 参数来指定更小的读取范围。这样即可避免一次性读取压缩后的 JS 包或大型数据文件导致上下文窗口被过度占用。

```yaml
file_read_max_chars: 100000  # default — ~25-35K tokens
```

如果您使用的是上下文窗口较大的模型且经常需要读取大型文件，请将其数值调高。而对于上下文窗口较小的模型，则建议降低该数值，以提升读取效率。

```yaml
# Large context model (200K+)
file_read_max_chars: 200000

# Small local model (16K context)
file_read_max_chars: 30000
```

该智能体还会自动实现文件读取的去重处理——如果同一文件区域被读取了两次且文件内容并未发生变化，它将返回一个轻量级的占位内容，而无需重新发送实际文件内容。当上下文被压缩后，这一机制会重置，从而使智能体能够在文件内容被汇总后再次读取这些文件。

## 工具输出截断限制

有三个相关的上限参数用于控制工具在Hermes进行截断之前可以返回的原始输出长度：

```yaml
tool_output:
  max_bytes: 50000        # terminal output cap (chars)
  max_lines: 2000         # read_file pagination cap
  max_line_length: 2000   # per-line cap in read_file's line-numbered view
```

- **`max_bytes`** — 当某个 `terminal` 命令输出的 stdout 和 stderr 合计字符数超过此值时，Hermes 会保留前 40% 和后 60% 的内容，并在两者之间添加 `[OUTPUT TRUNCATED]` 的提示。默认值为 50000（使用常见分词器处理后约相当于 12,000–15,000 个标记）。
- **`max_lines`** — 单次 `read_file` 调用中 `limit` 参数的上限值。超过此限制的请求会被限制，以避免单次读取操作占用过大的上下文窗口空间。默认值为 2000。
- **`max_line_length`** — 当 `read_file` 以带行号的形式输出内容时，每行内容的最大长度限制。超过此长度的行会被截断，仅保留指定数量的字符，其后附加 `... [truncated]` 的提示。默认值为 2000。

对于那些具备较大上下文窗口、且每次调用能够处理更多原始输出数据的模型，可适当提高这些限制值；而对于上下文窗口较小的模型，则应降低这些限制，以保持工具输出结果的简洁性。

```yaml
# Large context model (200K+)
tool_output:
  max_bytes: 150000
  max_lines: 5000

# Small local model (16K context)
tool_output:
  max_bytes: 20000
  max_lines: 500
```

## 全局工具集禁用

若需在单个位置禁止 CLI 及所有网关平台中使用特定的工具集，只需在 `agent.disabled_toolsets` 下列出这些工具集的名称即可：

```yaml
agent:
  disabled_toolsets:
    - memory       # hide memory tools + MEMORY_GUIDANCE injection
    - web          # no web_search / web_extract anywhere
```

该配置会在各平台工具设置（由 `hermes tools` 生成的 `platform_toolsets`）之后生效，因此此处列出的工具集将会被移除——即便该平台的已保存配置中仍保留有相关设置。当您希望通过一个简单的开关来“在所有地方关闭X功能”，而无需在 `hermes tools` 的界面中编辑15行以上的平台配置时，可使用此方法。

若将列表留空或省略该键，则不会产生任何效果。

## Git工作树隔离

启用Git工作树隔离功能，即可在同一个仓库上并行运行多个Agent。

```yaml
worktree: true    # Always create a worktree (same as hermes -w)
# worktree: false # Default — only when -w flag is passed
```

启用该功能后，每个 CLI 会话都将在 `.worktrees/` 目录下创建一个包含独立分支的新工作树。各 Agent 可以独立编辑文件、执行提交、推送操作以及创建 Pull Request，而互不干扰。退出时会自动删除已清理的工作树；尚未处理的工作树则会被保留，以便手动恢复。

您还可以在仓库根目录中使用 `.worktreeinclude` 指定需要复制到工作树中的 gitignored 文件列表：

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩功能

Hermes 会自动对较长的对话内容进行压缩，以确保其长度在模型上下文窗口的限制之内。该压缩功能通过独立的 LLM 调用实现——您可以选择将其连接到任何提供商或接口端点。

所有压缩相关设置均保存在 `config.yaml` 文件中（无需使用环境变量）。

### 完整参考文档

```yaml
compression:
  enabled: true                                     # Toggle compression on/off
  threshold: 0.50                                   # Compress at this % of context limit
  target_ratio: 0.20                                # Fraction of threshold to preserve as recent tail
  protect_last_n: 20                                # Min recent messages to keep uncompressed
  protect_first_n: 3                                # Non-system head messages pinned across compactions (0 = pin nothing)
  hygiene_hard_message_limit: 400                   # Gateway safety valve — see below

# The summarization model/provider is configured under auxiliary:
auxiliary:
  compression:
    model: ""                                       # Empty = use main chat model. Override with e.g. "google/gemini-3-flash-preview" for cheaper/faster compression.
    provider: "auto"                                # Provider: "auto", "openrouter", "nous", "codex", "main", etc.
    base_url: null                                  # Custom OpenAI-compatible endpoint (overrides provider)
```

:::info 旧配置迁移
包含 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 的旧配置，在首次加载时（配置版本 17）会自动迁移到 `auxiliary.compression.*` 格式，无需手动操作。
:::

`hygiene_hard_message_limit` 是仅适用于网关的**预压缩安全机制**。在某些情况下，大量消息的快速堆积可能会在达到常规上下文比例阈值之前就耗尽模型上下文容量；一旦消息数量超出此限制，Hermes 会强制进行压缩，而无需考虑当前token的使用情况。其默认值为 `400`——对于那些通常会有超长对话场景的平台，可适当提高该值；若希望更积极地实施压缩，则可降低该值。在正在运行的网关上修改此值后，变更将在处理下一条消息时生效（详见下文）。

`protect_first_n` 用于控制每次压缩过程中会保留多少**非系统**的初始消息。默认值为 `3`——即最初的用户与助手之间的对话内容会在每次摘要生成过程中都被保留，从而确保原始目标始终可见。在那些持续时间较长且初始对话已不再相关的滚动压缩场景中，可将 `protect_first_n` 设置为 `0`，这样仅会保留系统提示、摘要及最后几条消息。无论此设置如何，系统提示本身始终会被保留。

:::tip 网关上压缩参数与上下文长度的热重载
在最新版本中，只需在正在运行的网关上的 `config.yaml` 文件中修改 `model.context_length` 或任何 `compression.*` 相关键值，变更即会在处理下一条消息时生效——无需重启网关、无需执行 `/reset` 操作，也无需重新启动会话。由于缓存中的代理签名已包含这些关键值，因此网关在检测到变化时会自动重建代理实例。而 API 密钥以及工具/技能相关配置仍需通过常规的重载方式来应用。
:::

### 常见配置方案

**默认（自动检测）——无需任何配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
该功能会使用您配置的主提供商与主模型。如果您希望在使用成本低于主聊天模型的情况下实现压缩功能，可针对特定任务进行覆盖设置（例如：`auxiliary.compression.provider: openrouter` + `model: google/gemini-2.5-flash`）。

**强制指定提供商**（基于 OAuth 或 API 密钥）：
```yaml
auxiliary:
  compression:
    provider: nous
    model: gemini-3-flash
```
可兼容各类提供商：`nous`、`openrouter`、`codex`、`anthropic`、`main` 等。

**自定义端点**（自托管环境、Ollama、zai、DeepSeek 等）：
```yaml
auxiliary:
  compression:
    model: glm-4.7
    base_url: https://api.z.ai/api/coding/paas/v4
```
指向自定义的 OpenAI 兼容端点。认证时使用 `OPENAI_API_KEY`。

### 三个参数的交互方式

| `auxiliary.compression.provider` | `auxiliary.compression.base_url` | 最终效果 |
|---------------------|---------------------|--------|
| `auto`（默认值） | 未设置 | 自动检测最优的可用提供方 |
| `nous` / `openrouter` 等 | 未设置 | 强制使用指定提供方，并采用其认证方式 |
| 任意值 | 已设置 | 直接使用自定义端点（忽略提供方设置） |

:::warning 摘要模型上下文长度要求
摘要模型**必须**拥有至少与主智能体模型相同大小的上下文窗口。压缩器会将对话的中间完整部分发送给摘要模型——如果该模型的上下文窗口小于主模型，摘要生成操作将会因上下文长度不足而失败。出现这种情况时，中间的对话内容将被直接丢弃且不会生成摘要，从而导致对话上下文在无声无息中丢失。如果您自行指定模型，请务必确认其上下文长度不低于主模型。
:::

## 上下文引擎

上下文引擎用于控制在接近模型令牌限制时如何管理对话。内置的 `compressor` 引擎采用有损摘要技术（详见[上下文压缩](/developer-guide/context-compression-and-caching)）。插件引擎则可以替换它，采用其他策略来实现相同功能。

```yaml
context:
  engine: "compressor"    # default — built-in lossy summarization
```

若要使用插件引擎（例如用于实现无损上下文管理的 LCM）：

```yaml
context:
  engine: "lcm"          # must match the plugin's name
```

插件引擎**绝不会自动激活**——您必须明确将 `context.engine` 设置为插件名称。可通过 `hermes plugins` → Provider Plugins → Context Engine 来查看并选择可用的引擎。

有关内存插件对应的单选系统，请参阅 [Memory Providers](/user-guide/features/memory-providers) 文档。

## 迭代预算压力

当智能体正在处理需要多次调用工具的复杂任务时，它可能会在不知不觉中耗尽迭代预算（默认为 90 次轮次）。当预算接近临界值时，系统会自动向模型发出警告：

| 阈值 | 等级 | 模型显示的内容 |
|------|------|----------------|
| **70%** | 警告 | `[BUDGET: 63/90. 27 iterations left. Start consolidating.]` |
| **90%** | 严重警告 | `[BUDGET WARNING: 81/90. Only 9 left. Respond NOW.]` |

这些警告会以 `_budget_warning` 字段的形式嵌入到最后一个工具响应的 JSON 中，而非作为单独的消息发送——这样既能保留提示词缓存，也不会破坏对话结构。

```yaml
agent:
  max_turns: 90                # Max iterations per conversation turn (default: 90)
  api_max_retries: 3           # Retries per provider before fallback engages (default: 3)
```

默认情况下，系统会启用预算限制机制。智能体会将警告视为工具输出的一部分，从而促使它整合工作内容，并在迭代次数耗尽前给出响应。

当迭代预算完全用尽时，CLI会向用户显示如下通知：`⚠ 迭代预算已达上限（90/90）——响应可能不完整`。如果在执行任务过程中预算就用完了，智能体会在停止之前生成一份已完成工作的总结。

`agent.api_max_retries`参数用于控制Hermes在出现临时性错误（如速率限制、连接中断、5xx错误）时，在切换备用提供者之前会重试多少次。默认值为`3`，即总共尝试4次。如果您已配置[备用提供者](/user-guide/features/fallback-providers)并希望更快地进行故障转移，可将该值设置为`0`，这样主提供者遇到首次临时错误时就会立即切换到备用提供者，而无需继续对出现问题的端点进行重试。

### API超时设置

Hermes为流式调用设置了独立的超时机制，同时针对非流式调用还配备了过时检测功能。只有当您不手动修改设置时，过时检测功能才会针对本地提供者自动调整参数。

| 超时类型 | 默认值 | 本地提供者 | 配置/环境变量 |
|---------|--------|------------|--------------|
| Socket读取超时 | 120秒 | 自动延长至1800秒 | `HERMES_STREAM_READ_TIMEOUT` |
| 流式数据过时检测 | 180秒 | 自动禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| 非流式数据过时检测 | 300秒 | 保持默认值即自动禁用 | `providers.<id>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT` |
| API调用（非流式） | 1800秒 | 不变 | `providers.<id>.request_timeout_seconds` / `timeout_seconds` 或 `HERMES_API_TIMEOUT` |

**Socket读取超时**决定了httpx等待从提供者处接收下一组数据的时长。对于本地LLM，由于需要先加载大量上下文才能生成第一个token，因此可能需要数分钟时间，Hermes在检测到是本地端点时会将此超时值设置为30分钟。如果您明确设置了`HERMES_STREAM_READ_TIMEOUT`，则无论是否检测到端点类型，都将始终使用该值。

**流式数据过时检测**用于断开那些收到SSE保持连接信号但未收到实际数据的连接。由于本地提供者在预加载阶段不会发送保持连接信号，因此此功能对本地提供者是完全禁用的。

**非流式数据过时检测**用于终止那些长时间没有响应的非流式调用。默认情况下，Hermes会在本地端点上禁用此功能，以避免在长时间预加载过程中出现误报。如果您明确设置了`providers.<id>.stale_timeout_seconds`、`providers.<id>.models.<model>.stale_timeout_seconds`或`HERMES_API_CALL_STALE_TIMEOUT`，则即使在本地端点上也会优先使用这些自定义值。

## 上下文压力警告

与迭代预算限制不同，上下文压力监控的是对话内容距离**压缩阈值**的接近程度——即触发上下文压缩以总结旧消息的临界点。这一功能有助于您和智能体了解对话何时变得过长。

| 进度 | 等级 | 后果 |
|------|------|------|
| 距离阈值**≥ 60%** | 信息提示 | CLI会显示青色进度条；网关也会发送一条提示信息 |
| 距离阈值**≥ 85%** | 警告提示 | CLI会显示加粗的黄色进度条；网关会警告即将进行上下文压缩 |

在CLI中，上下文压力会以进度条的形式显示在工具输出中：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台中，系统会发送一条纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果禁用了自动压缩功能，系统会发出警告，提示上下文内容可能会被截断。

上下文压力检测是自动进行的——无需任何配置。它仅作为面向用户的通知机制触发，不会修改消息流，也不会向模型的上下文中注入任何内容。

## 凭证池策略

当您为同一提供商拥有多个 API 密钥或 OAuth 令牌时，可配置相应的轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # cycle through keys evenly
  anthropic: least_used      # always pick the least-used key
```

选项包括：`fill_first`（默认值）、`round_robin`、`least_used`、`random`。详细文档请参阅[凭证池](/user-guide/features/credential-pools)。

## 提示词缓存

当当前使用的服务提供商支持时，Hermes会自动开启跨会话提示词缓存功能——无需用户进行任何配置。

对于运行在**原生Anthropic平台**、**OpenRouter**以及**Nous Portal**上的Claude，Hermes会在系统提示词及技能模块中添加`cache_control`缓存控制标记，设置1小时的过期时间（`ttl: "1h"`）。在当前小时内的首次发送将按全额输入费用计费；而在同一小时内的后续任何会话发送，则会从缓存中读取内容，按较低的缓存读取费率收费。这意味着系统提示词、加载的技能内容以及长上下文的前半部分，在最初的1小时内都可在不同的`hermes`会话之间，甚至在不同分支的子智能体之间重复使用。

Qwen Cloud（阿里达斯 Scope）上游服务的缓存过期时间被限制为5分钟，因此Hermes在该平台也会采用5分钟的缓存过期时间。其他通过第三方平台接入Claude的路径（如AWS Bedrock、Azure Foundry）则默认遵循对应服务提供商的缓存设置。xAI Grok则采用独立的会话绑定对话ID机制——详情请参阅[xAI提示词缓存](/integrations/providers#xai-grok--responses-api--prompt-caching)。

目前不存在关闭此功能的选项——缓存功能始终处于开启状态，即便在单轮对话中也能节省成本，因为仅系统提示词所占的输入token数量就已相当可观。

## 辅助模型

Hermes会使用“辅助”模型来处理各类辅助任务，如图像分析、网页摘要生成、浏览器截图分析、会话标题生成以及上下文压缩等。默认情况下（`auxiliary.*.provider: "auto"`），Hermes会将所有辅助任务路由到你的**主聊天模型**——即你在`hermes model`中选择的同一服务提供商/模型。开始使用无需进行任何配置，但需注意，对于那些计算成本较高的推理模型（如Opus、MiniMax M2.7等），执行辅助任务会带来额外的费用。如果你希望无论使用何种主模型，都能以低成本快速完成辅助任务，可以明确指定`auxiliary.<task>.provider`和`auxiliary.<task>.model`的参数（例如，在OpenRouter上使用Gemini Flash模型进行图像处理和网页信息提取）。

:::note 为何“auto”模式会使用主模型
在早期版本中，聚合平台用户（如OpenRouter、Nous Portal）会被默认分配到成本较低的供应商端模型。这一做法令许多用户感到意外——那些购买了聚合服务订阅的用户，其辅助任务却由不同的模型处理。现在，“auto”模式会对所有用户统一使用主模型，不过仍可通过`config.yaml`中的任务级覆盖设置来改变这一行为（详见下文的[完整辅助模型配置参考](#full-auxiliary-config-reference)）。
:::

### 交互式配置辅助模型

无需手动编辑YAML文件，只需运行`hermes model`，然后从菜单中选择**“配置辅助模型”**即可。系统会提供一个交互式的任务级选择界面：

```
$ hermes model
→ Configure auxiliary models

[ ] vision               currently: auto / main model
[ ] web_extract          currently: auto / main model
[ ] title_generation     currently: openrouter / google/gemini-3-flash-preview
[ ] tts_audio_tags       currently: auto / main model
[ ] compression          currently: auto / main model
[ ] approval             currently: auto / main model
[ ] triage_specifier     currently: auto / main model
[ ] kanban_decomposer    currently: auto / main model
[ ] profile_describer    currently: auto / main model
```

选择任务，挑选提供方（OAuth流程会自动打开浏览器；使用API密钥的提供方则会弹出提示），再选定模型。这些设置将会保存到`config.yaml`文件中的`auxiliary.<task>.*`路径下。其操作逻辑与选择主模型的方式相同——无需学习额外的语法。

### 视频教程

<div style={{position: 'relative', width: '100%', aspectRatio: '16 / 9', marginBottom: '1.5rem'}}>
  <iframe
    src="https://www.youtube.com/embed/NoF-YajElIM"
    title="Hermes Agent — 辅助模型教程"
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0}}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

### 通用的配置模式

Hermes中的所有模型槽位——无论是辅助任务、压缩处理还是备用方案——都使用相同的三个配置项：

| 键值 | 功能说明 | 默认值 |
|-----|-----------|---------|
| `provider` | 用于身份验证和请求路由的提供方 | `"auto"` |
| `model` | 需要调用的模型 | 对应提供方的默认模型 |
| `base_url` | 自定义的OpenAI兼容端点（可覆盖提供方设置） | 未设置 |

当设置了`base_url`后，Hermes会忽略指定的提供方，直接调用该端点（并通过`api_key`或`OPENAI_API_KEY`进行身份验证）。如果仅设置了`provider`，则Hermes会使用该提供方内置的身份验证机制及基础URL。

可用于辅助任务的提供方包括：`auto`、`main`，以及[提供方注册表](/reference/environment-variables)中的所有提供方——如`openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`google-gemini-cli`、`qwen-oauth`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`alibaba`、`bedrock`、`huggingface`、`arcee`、`xiaomi`、`kilocode`、`opencode-zen`、`opencode-go`、`azure-foundry`——或是您在`custom_providers`列表中自定义的任何提供方名称（例如`provider: "beans"`）。

:::提示 MiniMax OAuth
`minimax-oauth`通过浏览器OAuth方式登录（无需API密钥）。运行`hermes model`后选择**MiniMax (OAuth)**即可完成身份验证。辅助任务会自动使用`MiniMax-M2.7-highspeed`模型。详情请参阅[MiniMax OAuth指南](../guides/minimax-oauth.md)。
:::

:::提示 xAI Grok OAuth
`xai-oauth`为SuperGrok及X Premium+订阅用户提供浏览器OAuth登录功能（同样无需API密钥）。运行`hermes model`后选择**xAI Grok OAuth (SuperGrok / Premium+)**即可完成身份验证。同一个OAuth令牌可重复用于所有直接对接xAI平台的场景，包括聊天、辅助任务、文本转语音、图像生成、视频生成以及语音转文字功能。详情请参阅[xAI Grok OAuth指南](../guides/xai-grok-oauth.md)；如果Hermes运行在远程主机上，请参考[通过SSH/远程主机进行OAuth认证](../guides/oauth-over-ssh.md)。
:::

:::警告 `"main"`仅适用于辅助任务
`"main"`提供方选项的含义是“使用我的主智能体所使用的提供方”——该选项仅能在`auxiliary:`、`compression:`以及主要的备用方案条目（`fallback_providers:`或旧版的`fallback_model:`）中使用。它**不能**作为顶层`model.provider`设置的有效值。如果您使用自定义的OpenAI兼容端点，请在`model:`部分将`provider`设置为`custom`。所有主流模型提供方的选项详见[AI提供方列表](/integrations/providers)。
:::

### 辅助任务配置完整参考手册

```yaml
auxiliary:
  # Image analysis (vision_analyze tool + browser screenshots)
  vision:
    provider: "auto"           # "auto", "openrouter", "nous", "codex", "main", etc.
    model: ""                  # e.g. "openai/gpt-4o", "google/gemini-2.5-flash"
    base_url: ""               # Custom OpenAI-compatible endpoint (overrides provider)
    api_key: ""                # API key for base_url (falls back to OPENAI_API_KEY)
    timeout: 120               # seconds — LLM API call timeout; vision payloads need generous timeout
    download_timeout: 30       # seconds — image HTTP download; increase for slow connections

  # Web page summarization + browser page text extraction
  web_extract:
    provider: "auto"
    model: ""                  # e.g. "google/gemini-2.5-flash"
    base_url: ""
    api_key: ""
    timeout: 360               # seconds (6min) — per-attempt LLM summarization

  # Dangerous command approval classifier
  approval:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30                # seconds

  # Gemini 3.1 TTS hidden audio-tag insertion
  tts_audio_tags:
    provider: "auto"
    model: ""                  # empty = main chat model
    base_url: ""
    api_key: ""
    timeout: 30

  # Context compression timeout (separate from compression.* config)
  compression:
    timeout: 120               # seconds — compression summarizes long conversations, needs more time

  # Auto-generated session titles. Empty language follows the conversation;
  # set e.g. "English" or "Japanese" to pin titles to one language.
  title_generation:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
    language: ""

  # Skills hub — skill matching and search
  skills_hub:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # MCP tool dispatch
  mcp:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30

  # Kanban triage specifier — `hermes kanban specify <id>` (or the
  # dashboard's ✨ Specify button on Triage-column cards) uses this
  # slot to expand a one-liner into a concrete spec and promote the
  # task to `todo`. Cheap fast models work well here; spec expansion
  # is short and doesn't need reasoning depth.
  triage_specifier:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 120
```

:::tip
每个辅助任务都拥有可配置的`timeout`参数（单位：秒）。默认值分别为：视觉处理任务120秒，网页提取任务360秒，审批任务30秒，压缩任务120秒。如果使用的本地模型处理速度较慢，建议适当增加这些时间值。此外，视觉处理任务还包含一个独立的`download_timeout`参数（默认30秒），用于控制HTTP图像下载过程；在网络连接较慢或使用自托管图像服务器时，也应提高该值。
:::

:::info
上下文压缩功能拥有专门的`compression:`模块用于设置阈值，同时还设有`auxiliary.compression:`模块用于配置模型及提供方相关参数——详情请参阅上文[上下文压缩](#context-compression)部分。主回退链则通过顶级的`fallback_providers:`列表来实现回退机制——更多信息请参见[回退提供方](/integrations/providers#fallback-providers)。这三种功能均遵循相同的提供方/模型/base_url格式。
:::

### 辅助任务的OpenRouter路由与Pareto Code路由

当某个辅助任务通过显式指定或因主智能体运行在OpenRouter上而自动采用`provider: "main"`时，主智能体的`provider_routing`及`openrouter.min_coding_score`设置**不会被传递**——按设计，每个辅助任务都是独立运行的。若要为特定辅助任务设置OpenRouter提供方偏好，或使用[Pareto Code路由器](/integrations/providers#openrouter-pareto-code-router)，可通过`extra_body`参数针对该任务进行单独配置：

```yaml
auxiliary:
  compression:
    provider: openrouter
    model: openrouter/pareto-code         # use the Pareto Code router for this task
    extra_body:
      provider:                            # OpenRouter provider routing prefs
        order: [anthropic, google]         # try these providers in order
        sort: throughput                   # or "price" | "latency"
        # only: [anthropic]                # restrict to a specific provider
        # ignore: [deepinfra]              # exclude specific providers
      plugins:                             # OpenRouter Pareto Code router knob
        - id: pareto-router
          min_coding_score: 0.5            # 0.0–1.0; higher = stronger coders
```

其格式与 OpenRouter 在聊天补全请求体中接受的格式一致。Hermes 会原封不动地转发整个 `extra_body`，因此 [openrouter.ai/docs](https://openrouter.ai/docs) 中文档中提到的其他所有 OpenRouter 请求体字段也同样适用。

### 更改视觉模型

如需使用 GPT-4o 而非 Gemini Flash 进行图像分析：

```yaml
auxiliary:
  vision:
    model: "openai/gpt-4o"
```

或者通过环境变量（位于 `~/.hermes/.env` 中）：

```bash
AUXILIARY_VISION_MODEL=openai/gpt-4o
```

### 提供商选项

这些选项适用于**辅助任务配置**（`auxiliary:`、`compression:`）以及主要的备用提供商设置（`fallback_providers:` 或旧版的 `fallback_model:`），并不适用于主配置项 `model.provider`。

| 提供商 | 描述 | 要求 |
|----------|-------------|------|
| `"auto"` | 选择最佳可用选项（默认值）。系统会依次尝试 OpenRouter、Nous 和 Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter——可路由至任何模型（如 Gemini、GPT-4o、Claude 等）。 | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal。 | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth（需 ChatGPT 账户）。支持视觉处理功能（如 gpt-5.3-codex）。 | `hermes model` → Codex |
| `"minimax-oauth"` | 强制使用 MiniMax OAuth（通过浏览器登录，无需 API 密钥）。辅助任务会使用 MiniMax-M2.7-highspeed 模型。 | `hermes model` → MiniMax（OAuth） |
| `"xai-oauth"` | 强制使用 xAI Grok OAuth（SuperGrok 或 X Premium+ 用户可通过浏览器登录，无需 API 密钥）。同一 OAuth 令牌可同时用于聊天、文本转语音、图像处理、视频处理及文字转录等功能。 | `hermes model` → xAI Grok OAuth（SuperGrok / Premium+） |
| `"main"` | 使用您当前配置的自定义/主端点。该端点可以由 `OPENAI_BASE_URL` + `OPENAI_API_KEY` 指定，也可以通过 `hermes model` / `config.yaml` 保存的自定义端点指定。适用于 OpenAI、本地模型或任何兼容 OpenAI 的 API。**仅适用于辅助任务——不适用于 `model.provider`。** | 自定义端点的凭证及基础 URL |

当您希望某些辅助任务绕过默认的路由机制时，主提供商目录中的直接 API 密钥提供商也可在此处使用。一旦配置了 `GMI_API_KEY`，则 `"gmi"` 选项也可正常使用：

```yaml
auxiliary:
  compression:
    provider: "gmi"
    model: "anthropic/claude-opus-4.6"
```

对于 GMI 辅助路由功能，需使用 GMI 的 `/v1/models` 接口返回的精确模型编号。

### 常见配置方式

**使用自定义直接接口**（相较于 `provider: "main"`，这种方式在处理本地或自托管 API 时更为清晰）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`，因此这是将辅助任务路由至特定端点最明确的方式。对于直接的端点覆盖，Hermes 会使用已配置的 `api_key`，若无法使用则会回退到 `OPENAI_API_KEY`；它不会为该自定义端点重复使用 `OPENROUTER_API_KEY`。

**使用 OpenAI API key 处理视觉任务：**
```yaml
# In ~/.hermes/.env:
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_API_KEY=sk-...

auxiliary:
  vision:
    provider: "main"
    model: "gpt-4o"       # or "gpt-4o-mini" for cheaper
```

**使用 OpenRouter 进行视觉任务**（可路由至任意模型）：
```yaml
auxiliary:
  vision:
    provider: "openrouter"
    model: "openai/gpt-4o"      # or "google/gemini-2.5-flash", etc.
```

**使用 Codex OAuth**（适用于 ChatGPT Pro/Plus 账户——无需 API 密钥）：
```yaml
auxiliary:
  vision:
    provider: "codex"     # uses your ChatGPT OAuth token
    # model defaults to gpt-5.3-codex (supports vision)
```

**使用 MiniMax OAuth 登录**（通过浏览器登录，无需 API 密钥）：
```yaml
model:
  default: MiniMax-M2.7
  provider: minimax-oauth
  base_url: https://api.minimax.io/anthropic
```
运行 `hermes model` 命令，选择 **MiniMax (OAuth)** 方式登录即可自动完成设置。针对中国地区，基础网址为 `https://api.minimaxi.com/anthropic`。如需完整操作指南，请参阅 [MiniMax OAuth 使用指南](../guides/minimax-oauth.md)。

**使用本地/自托管模型：**
```yaml
auxiliary:
  vision:
    provider: "main"      # uses your active custom endpoint
    model: "my-local-model"
```

`provider: "main"` 会使用 Hermes 在常规聊天中使用的相同提供方——无论是自定义的命名提供方（如 `beans`）、内置提供方如 `openrouter`，还是传统的 `OPENAI_BASE_URL` 接口。

:::tip
如果您将 Codex OAuth 作为主要模型提供方，视觉功能将自动启用——无需额外配置。Codex 已被纳入视觉功能的自动检测流程中。
:::

:::warning
**视觉功能需要多模态模型。** 如果您设置了 `provider: "main"`，请确保您的接口支持多模态/视觉功能——否则图像分析将会失败。
:::

### 环境变量（旧版）

辅助模型也可以通过环境变量进行配置。不过，推荐使用 `config.yaml` 文件——它更易于管理，且能支持包括 `base_url` 和 `api_key` 在内的所有选项。

| 设置项 | 环境变量 |
|---------|---------------------|
| 视觉功能提供方 | `AUXILIARY_VISION_PROVIDER` |
| 视觉功能模型 | `AUXILIARY_VISION_MODEL` |
| 视觉功能接口地址 | `AUXILIARY_VISION_BASE_URL` |
| 视觉功能 API 密钥 | `AUXILIARY_VISION_API_KEY` |
| 网页提取功能提供方 | `AUXILIARY_WEB_EXTRACT_PROVIDER` |
| 网页提取功能模型 | `AUXILIARY_WEB_EXTRACT_MODEL` |
| 网页提取功能接口地址 | `AUXILIARY_WEB_EXTRACT_BASE_URL` |
| 网页提取功能 API 密钥 | `AUXILIARY_WEB_EXTRACT_API_KEY` |

压缩功能及备用模型设置仅可通过 `config.yaml` 进行配置。

:::tip
运行 `hermes config` 可查看当前的辅助模型设置。只有当配置值与默认值不同时，才会显示被覆盖的设置。
:::

## 推理耗时控制

可调节模型在回复前进行“思考”的时间长度：

```yaml
agent:
  reasoning_effort: ""   # empty = medium (default). Options: none, minimal, low, medium, high, xhigh (max)
```

当该参数未设置（即默认值）时，推理强度将默认为“medium”——这一平衡值适用于大多数任务。若手动设置数值，则会覆盖默认值：更高的推理强度虽能在复杂任务中提升结果质量，但会带来更多的Token消耗和延迟。

:::注意：基于OpenRouter的自适应思维模型（Claude 4.6+及Fable/Mythos系列）
这类模型采用*自适应*思维模式，不支持常规的`reasoning.effort`字段——OpenRouter会对这些模型忽略该字段。Hermes会自动将您的`reasoning_effort`参数映射为OpenRouter的`verbosity`参数（该参数对应Anthropic的`output_config.effort`），因此原有的“低”/“中”/“高”/“x高”选项依然有效，无需额外配置。若设置为`none`（或未设置），模型将沿用其自身的自适应默认值。（虽然协议层支持`max`值，但它并非可选择的`reasoning.effort`数值；`x高`则是可配置的最高强度值。）而原生的Anthropic提供程序可直接控制推理强度，因此不会受到影响。
:::

您还可以通过 `/reasoning` 命令在运行时更改推理强度：

```
/reasoning           # Show current effort level and display state
/reasoning high      # Set reasoning effort to high
/reasoning none      # Disable reasoning
/reasoning show      # Show model thinking above each response
/reasoning hide      # Hide model thinking
```

## 工具调用强制机制

部分模型有时会以文本形式描述其预期操作，而非真正调用相关工具（例如只说“我会运行测试……”而不实际调用终端）。工具调用强制机制通过系统提示进行引导，促使模型重新采用实际调用工具的方式来执行任务。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"`（默认值） | 对匹配的模型（如 `gpt`、`codex`、`gemini`、`gemma`、`grok`）启用该功能；对其他所有模型（如 Claude、DeepSeek、Qwen 等）则禁用。 |
| `true` | 无论使用何种模型，始终启用该功能。如果您发现当前模型只是描述操作步骤而非实际执行，可使用此设置。 |
| `false` | 无论使用何种模型，始终禁用该功能。 |
| `["gpt", "codex", "qwen", "llama"]` | 仅当模型名称包含列表中的任意子串时（不区分大小写）启用该功能。 |

### 它会注入什么内容

启用该功能后，系统提示语中可能会添加三层指导规则：

1. **通用工具使用强制要求**（适用于所有匹配的模型）——要求模型立即调用工具而非仅描述意图，持续处理任务直至完成，且不得以“稍后再做”作为回合结束的理由。 
   
2. **OpenAI 模型执行规范**（仅适用于 GPT 和 Codex 模型）——针对 GPT 特有的故障模式提供额外指导，包括因部分完成结果而放弃任务、跳过必要的信息查询、依赖幻觉而非工具输出，以及未经验证就宣布任务已完成。

3. **Google 模型操作指南**（仅适用于 Gemini 和 Gemma 模型）——要求内容简洁明了、使用绝对路径、并行调用工具，并遵循“先验证再修改”的处理方式。

这些规则对用户是不可见的，仅影响系统提示语。那些已经能够稳定使用工具的模型（如 Claude）无需此类指导，这也是为何 `"auto"` 设置会将其排除在外。

### 何时启用该功能

如果您使用的模型不在默认的自动列表中，且发现它经常只是描述“应该做什么”而非真正执行操作，可以设置 `tool_use_enforcement: true`，或将该模型的子串添加到列表中。

```yaml
agent:
  tool_use_enforcement: ["gpt", "codex", "gemini", "grok", "my-custom-model"]
```

## 文本转语音配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts"
  speed: 1.0                    # Global speed multiplier (fallback for all providers)
  edge:
    voice: "en-US-AriaNeural"   # 322 voices, 74 languages
    speed: 1.0                  # Speed multiplier (converted to rate percentage, e.g. 1.5 → +50%)
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    speed: 1.0                  # Speed multiplier (clamped to 0.25–4.0 by the API)
    base_url: "https://api.openai.com/v1"  # Override for OpenAI-compatible TTS endpoints
  minimax:
    speed: 1.0                  # Speech speed multiplier
    # base_url: ""              # Optional: override for OpenAI-compatible TTS endpoints
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - Neutral (default)
  gemini:
    model: "gemini-2.5-flash-preview-tts"   # or gemini-3.1-flash-tts-preview
    voice: "Kore"               # 30 prebuilt voices: Zephyr, Puck, Kore, Enceladus, etc.
    audio_tags: false           # Hidden Gemini 3.1 TTS audio-tag insertion
    persona_prompt_file: ""      # Optional Markdown/text file with Gemini voice direction
  xai:
    voice_id: "eve"             # xAI TTS voice
    language: "en"              # ISO 639-1
    sample_rate: 24000
    bit_rate: 128000            # MP3 bitrate
    # base_url: "https://api.x.ai/v1"
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

该参数同时用于控制`text_to_speech`工具以及语音模式下的语音回复功能（在CLI或消息网关中可通过`/voice tts`指令调用）。

**语速回退层级：**特定提供商设置的语速（例如`tts.edge.speed`）→全局`tts.speed`设置→默认值`1.0`。如需为所有提供商统一设置语速，可调整全局`tts.speed`；如需更精细的控制，则可为各提供商单独设置语速。 

## 显示设置

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # Enable /verbose slash command in messaging gateway
  platforms: {}           # Per-platform display overrides (see below)
  tool_progress_overrides: {}  # DEPRECATED — use display.platforms instead
  interim_assistant_messages: true  # Gateway: send natural mid-turn assistant updates as separate messages
  skin: default           # Built-in or custom CLI skin (see user-guide/features/skins)
  personality: "kawaii"  # Legacy cosmetic field still surfaced in some summaries
  compact: false          # Compact output mode (less whitespace)
  resume_display: full    # full (show previous messages on resume) | minimal (one-liner only)
  bell_on_complete: false # Play terminal bell when agent finishes (great for long tasks)
  show_reasoning: false   # Show model reasoning/thinking above each response (toggle with /reasoning show|hide)
  streaming: false        # Stream tokens to terminal as they arrive (real-time output)
  show_cost: false        # Show estimated $ cost in the CLI status bar
  timestamps: false       # When true, prefixes user and assistant labels with [HH:MM] timestamps in the CLI / TUI transcript
  tool_preview_length: 0  # Max chars for tool call previews (0 = no limit, show full paths/commands)
  runtime_footer:         # Gateway: append a runtime-context footer to final replies
    enabled: false
    fields: ["model", "context_pct", "cwd"]
  file_mutation_verifier: true    # Append an advisory footer when write_file/patch calls failed this turn
  credits_notices: true   # Nous credits status-bar notices (usage bands, grant-spent, depleted). false = silence them; /usage still works
  language: en            # UI language for static messages (approval prompts, some gateway replies). en | zh | zh-hant | ja | de | es | fr | tr | uk | af | ko | it | ga | pt | ru | hu
```

### 文件修改验证器

当 `display.file_mutation_verifier` 设置为 `true`（默认值）时，如果在当前对话轮次中发生了 `write_file` 或 `patch` 操作失败，且同一路径后续并未出现成功的写入操作，Hermes 会在助手的最终回复中附加一行提示信息。这样一来，无需在每次编辑后都手动运行 `git status`，即可避免出现“批量并行应用补丁，部分操作悄然失败，模型却声称全部成功”之类的虚假反馈。 

示例提示内容：

```
⚠️ File-mutation verifier: 3 file(s) were NOT modified this turn despite any wording above that may suggest otherwise. Run `git status` or `read_file` to confirm.
  • concepts/automatic-organization.md — [patch] Could not find match for old_string
  • concepts/lora.md — [patch] Could not find match for old_string
  • concepts/rag-pipeline.md — [patch] Could not find match for old_string
```

将 `file_mutation_verifier: false`（或 `HERMES_FILE_MUTATION_VERIFIER=0`）设置为抑制页脚显示。该验证机制仅在回合结束时存在真正的错误时才会触发——如果在同一回合内模型重新尝试修复失败的任务并成功完成，则不会对该文件触发该验证。

### 静态消息的界面语言设置

`display.language` 设置用于翻译少量面向用户的静态消息，包括 CLI 的确认提示、若干网关斜杠命令的回复内容（如重启通知、“审批已过期”、“目标已完成”等）。该设置**不**用于翻译智能体的回复、日志行、工具输出、错误回溯信息或斜杠命令的描述——这些内容仍将保持英文。如果您希望智能体本身用其他语言回复，只需在提示词或系统消息中明确指定即可。

支持的值包括：`en`（默认）、`zh`（简体中文）、`zh-hant`（繁体中文）、`ja`（日语）、`de`（德语）、`es`（西班牙语）、`fr`（法语）、`tr`（土耳其语）、`uk`（乌克兰语）、`af`（南非荷兰语）、`ko`（韩语）、`it`（意大利语）、`ga`（爱尔兰语）、`pt`（葡萄牙语）、`ru`（俄语）、`hu`（匈牙利语）。对于未知的值，系统将默认回退为英文。

您也可以通过 `HERMES_LANGUAGE` 环境变量为当前会话单独设置该语言，该值会覆盖配置文件中的设定。

```yaml
display:
  language: zh   # CLI approval prompts appear in Chinese
```

| 模式 | 显示内容 |
|------|----------|
| `off` | 完全静默——仅显示最终响应 |
| `new` | 仅在工具状态发生变化时显示工具指示器 |
| `all` | 显示每次工具调用的简要预览（默认值） |
| `verbose` | 显示完整的参数、结果及调试日志 |

在 CLI 中，可使用 `/verbose` 在这些模式之间切换。若要在消息平台（如 Telegram、Discord、Slack 等）中使用 `/verbose`，需在上述 `display` 部分设置 `tool_progress_command: true`。这样该命令即可切换模式并将设置保存至配置文件中。

工具进度功能需要一个能够安全显示进度更新的网关适配器。对于不支持消息编辑功能的平台（包括 Signal），即便 `/verbose` 已将模式设置为非 `off` 状态，也会隐藏工具进度提示框。

### 运行时元数据页脚（仅限网关）

当 `display.runtime_footer.enabled: true` 时，Hermes 会在每次网关交互的**最终**消息中添加一个简短的运行时上下文页脚。当前页脚可显示模型类型、上下文窗口使用比例以及当前工作目录。该功能默认处于关闭状态；如果您的团队希望每条回复都包含这些信息，可针对特定网关手动启用。

```yaml
display:
  runtime_footer:
    enabled: true
    fields: ["model", "context_pct", "cwd"]   # supported fields: model, context_pct, cwd
```

`/footer` 接口命令可在任意会话的运行时切换此功能的状态。

以下是添加到 Telegram/Discord/Slack 回复中的示例页脚内容：

```
— claude-opus-4.7 · 12 tool calls · 2m 14s · $0.042
```

仅轮次中的**最终**消息会显示页脚信息，而中间的更新内容则保持简洁不变。

### 各平台的详细程度设置

不同平台对信息的详细程度要求各异。您可以使用 `display.platforms` 来为不同平台设置相应的显示模式：

```yaml
display:
  tool_progress: all          # global default
  platforms:
    signal:
      tool_progress: 'off'    # Signal cannot currently display tool-progress bubbles
    telegram:
      tool_progress: verbose  # detailed progress on Telegram
    slack:
      tool_progress: 'off'    # quiet in shared Slack workspace
```

若未进行自定义设置，各平台将自动采用全局的 `tool_progress` 值。有效的平台标识符包括：`telegram`、`discord`、`slack`、`signal`、`whatsapp`、`matrix`、`mattermost`、`email`、`sms`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot`。为保持向后兼容性，旧的 `display.tool_progress_overrides` 键仍会被加载，但该键现已过时，首次加载时会迁移至 `display.platforms` 中。

Signal 被列为有效的平台标识符，是因为其允许针对不同平台单独保存设置；不过目前的 Signal 适配器无法编辑已发送的消息，也无法显示工具进度提示框。因此建议将 Signal 的 `tool_progress` 设置为 `off`；若需实时查看每个工具调用的执行情况，请使用命令行工具或具备编辑功能的消息平台。

`interim_assistant_messages` 功能仅适用于网关。启用该功能后，Hermes 会将处理完成的对话中途助手更新内容以独立聊天消息的形式发送出去。此功能与 `tool_progress` 无关，也不需要网关进行流式传输。

## 隐私保护

```yaml
privacy:
  redact_pii: false  # Strip PII from LLM context (gateway only)
```

当 `redact_pii` 设置为 `true` 时，该网关会在将系统提示语发送到支持平台的大型语言模型之前，先对其进行个人身份信息脱敏处理：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 用户 ID） | 哈希处理为 `user_<12位sha256哈希值>` |
| 用户 ID | 哈希处理为 `user_<12位sha256哈希值>` |
| 聊天 ID | 数字部分进行哈希处理，保留平台前缀（格式为 `telegram:<哈希值>`） |
| 主频道 ID | 数字部分进行哈希处理 |
| 用户名 | **不受影响**（由用户自行设置，可公开显示） |

**平台支持情况：** 该脱敏功能适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 不在支持范围内，因为其提及系统（`<@user_id>`）需要在大型语言模型上下文中使用真实 ID。

哈希值具有确定性——同一用户始终对应相同的哈希值，因此模型仍能区分群组聊天中的不同用户。在内部路由与传输过程中则使用原始值。 

## 语音转文本（STT）

```yaml
stt:
  provider: "local"            # "local" | "groq" | "openai" | "mistral"
  local:
    model: "base"              # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe
  # model: "whisper-1"         # Legacy fallback key still respected
```

提供方运行机制：

- `local` 模式会使用在您的设备上运行的 `faster-whisper` 工具，需通过 `pip install faster-whisper` 单独进行安装。
- `groq` 模式则利用 Groq 提供的与 Whisper 兼容的接口，并读取 `GROQ_API_KEY` 配置键。
- `openai` 模式会调用 OpenAI 的语音 API，同时需要配置 `VOICE_TOOLS_OPENAI_KEY`。

当所请求的提供方不可用时，Hermes 会按照 `local` → `groq` → `openai` 的顺序自动切换备用方案。

Groq 和 OpenAI 模型的优先级设置由环境变量决定：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

## 语音模式（命令行界面）

```yaml
voice:
  record_key: "ctrl+b"         # Push-to-talk key inside the CLI
  max_recording_seconds: 120    # Hard stop for long recordings
  auto_tts: false               # Enable spoken replies automatically when /voice on
  beep_enabled: true            # Play record start/stop beeps in CLI voice mode
  silence_threshold: 200        # RMS threshold for speech detection
  silence_duration: 3.0         # Seconds of silence before auto-stop
```

在 CLI 中使用 `/voice on` 可启用麦克风模式，使用 `record_key` 可开始/停止录音，而 `/voice tts` 则用于切换语音回复功能。有关端到端设置及不同平台上的具体行为，请参阅 [语音模式](/user-guide/features/voice-mode) 文档。

## 流式传输

在令牌生成后立即将其传输至终端或消息平台，而无需等待完整响应。

### CLI 流式传输

```yaml
display:
  streaming: true         # Stream tokens to terminal in real-time
  show_reasoning: true    # Also stream reasoning/thinking tokens (optional)
```

启用该功能后，响应内容会以逐条消息的形式显示在流式框中。同时，工具调用仍会被默默记录下来。如果对应的提供方不支持流式输出，系统会自动切换为常规显示方式。

### 网关流式传输（Telegram、Discord、Slack）

```yaml
streaming:
  enabled: true           # Enable progressive message editing
  transport: edit         # "edit" (progressive message editing) or "off"
  edit_interval: 0.3      # Seconds between message edits
  buffer_threshold: 40    # Characters before forcing an edit flush
  cursor: " ▉"            # Cursor shown during streaming
  fresh_final_after_seconds: 0    # Opt in to fresh final (Telegram) when preview is this old
```

启用该功能后，机器人会在接收到第一个令牌时发送消息，随后随着更多令牌的到达逐步对消息进行编辑。对于不支持消息编辑的平台（如 Signal、Email、Home Assistant），系统会在首次尝试时自动识别，并优雅地禁用该会话的流式传输，从而避免消息大量涌入。

若希望在不进行逐令牌编辑的情况下单独发送中间阶段的助手更新，可设置 `display.interim_assistant_messages: true`。

**溢出处理：** 如果流式传输的文本超过了平台规定的消息长度限制（约 4096 字符），当前消息将会被最终确定，系统会自动开始发送新消息。

**Telegram 的“全新最终消息”功能：** Telegram 的 `editMessageText` 功能会保留原始消息的时间戳，因此即使流式回复已结束，其首个令牌对应的时间戳仍会保留。若希望将旧预览内容作为全新的最终消息发送，并尽力删除旧预览，可设置 `fresh_final_after_seconds > 0`。默认值为 `0`，此时流式回复会直接被最终确定，从而避免在同时显示两种操作的客户端出现短暂的重复消息或删除序列。

:::note 各平台的流式传输默认设置
全局的 `streaming.enabled` 开关默认值为 `false`——在将其设置为 `true` 之前，不会进行任何流式传输。一旦启用，流式传输功能会**按平台分别配置**：Telegram 的默认值为 `display.platforms.telegram.streaming: true`（支持流式传输），而 Discord 的默认值为 `display.platforms.discord.streaming: false`（不支持）。因此，在启用流式传输后，Telegram 会立即开始流式发送消息，而 Discord 则仍会以完整消息的形式回复，直到您更改其开关设置。您可以通过控制面板的 **Channels** 开关或直接在 `~/.hermes/config.yaml` 文件中调整这些按平台划分的开关设置。
:::

## 群聊会话隔离

限制通过 CLI、TUI/控制面板以及消息网关同时开启的活跃聊天会话数量：

```yaml
max_concurrent_sessions: null  # null/0 = unlimited; positive integer = active session cap
```

当达到上限时，Hermes 会针对新会话返回直接的限流提示信息，而现有的活跃会话则仍能保持正常运行。

标准配置键为顶层键 `max_concurrent_sessions`。虽然 Hermes 也会将 `gateway.max_concurrent_sessions` 作为备用值接受，但当两者同时被设置时，顶层键的配置优先生效。

该限流机制通过本地的运行时租约文件来实现，并采用尽力而为的方式：如果无法读取或锁定注册表，Hermes 仍会尝试让新会话建立，从而避免用户陷入困境。此机制适用于单个主机/配置文件的运行环境，不适用于在多台机器上共享的 `$HERMES_HOME` 目录。

可控制共享聊天是按房间维护一个对话，还是按参与者维护一个对话：

```yaml
group_sessions_per_user: true  # true = per-user isolation in groups/channels, false = one shared session per chat
```

- `true` 是默认且推荐的设置。在 Discord 频道、Telegram 群组、Slack 频道等类似共享环境中，只要平台能提供用户 ID，每位发送者都会拥有独立的会话。
- `false` 会恢复到旧的共享会话模式。如果您希望 Hermes 将某个频道视为一个统一的协作对话场景，此设置非常有用；但这也意味着所有用户会共享上下文、令牌成本以及消息中断状态。
- 直接消息不受影响。Hermes 仍会像往常一样根据聊天/直接消息 ID 对其进行标识。
- 无论采用哪种设置，子线程始终与父频道保持隔离；在 `true` 模式下，每个子线程的参与者也会拥有独立的会话。

如需了解相关行为细节和示例，请参阅 [会话](/user-guide/sessions) 文档以及 [Discord 使用指南](/user-guide/messaging/discord)。

## 未知用户发送直接消息时的处理方式

可控制当有未知用户发送直接消息时 Hermes 的响应行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- 默认值为 `pair`。Hermes 会拒绝访问，但会在私信中回复一个一次性配对码。
- `ignore` 模式会静默忽略未经授权的私信。
- 各平台的相关设置可覆盖全局默认值，因此您可以在保持整体配对功能开启的同时，让某个特定平台的消息通知更安静。

## 快速命令

您可以定义自定义命令，这些命令要么在不调用大型语言模型的情况下执行 Shell 命令，要么将一个斜杠命令别名为另一个命令。快速命令无需任何令牌即可使用，非常适合在 Telegram、Discord 等消息平台中用于快速检查服务器状态或运行实用脚本。

```yaml
quick_commands:
  status:
    type: exec
    command: systemctl status hermes-agent
  disk:
    type: exec
    command: df -h /
  update:
    type: exec
    command: cd ~/.hermes/hermes-agent && git pull && pip install -e .
  gpu:
    type: exec
    command: nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader
  restart:
    type: alias
    target: /gateway restart
```

使用方法：在命令行界面或任何消息平台中输入 `/status`、`/disk`、`/update`、`/gpu` 或 `/restart`。`exec` 命令会在主机上本地执行并直接返回结果——无需调用大型语言模型，也不会消耗任何令牌。`alias` 命令则用于将指令重定向至已配置的对应命令。

- **30秒超时机制**——运行时间过长的命令会触发错误信息并被终止  
- **优先级规则**——快速命令会优先于技能命令被处理，因此您可以覆盖原有的技能名称  
- **自动补全功能**——快速命令会在指令发送时立即解析，不会显示在内置的命令自动补全列表中  
- **支持的命令类型**——仅限 `exec` 和 `alias` 两种类型，其他类型将引发错误  
- **多平台兼容**——支持命令行界面、Telegram、Discord、Slack、WhatsApp、Signal、电子邮件以及 Home Assistant 等平台  

仅包含字符串的提示语无法作为有效快速命令使用。如需创建可重复使用的提示语工作流，请为现有的命令创建技能或别名。

## 人类化响应延迟

在消息平台中模拟类似人类的响应节奏：

```yaml
human_delay:
  mode: "off"                  # off | natural | custom
  min_ms: 800                  # Minimum delay (custom mode)
  max_ms: 2500                 # Maximum delay (custom mode)
```

## 代码执行

配置 `execute_code` 工具：

```yaml
code_execution:
  mode: project                # project (default) | strict
  timeout: 300                 # Max execution time in seconds
  max_tool_calls: 50           # Max tool calls within code execution
```

**`mode`** 参数用于控制脚本的工作目录及 Python 解释器：

- **`project`**（默认值）——脚本在会话的工作目录中运行，使用当前激活的虚拟环境/Conda 环境中的 Python。项目依赖项（如 `pandas`、`torch` 以及项目自带的包）和相对路径（如 `.env`、`./data.csv`）都能像在 `terminal()` 模式下一样被正确解析。
- **`strict`**——脚本在临时准备目录中运行，使用 `sys.executable`（即 Hermes 自带的 Python）。这种方式能确保最高的可重复性，但项目依赖项和相对路径将无法被解析。

两种模式下都会执行环境清理操作（移除包含 `*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_PASSWORD`、`*_CREDENTIAL`、`*_PASSWD`、`*_AUTH` 的内容），同时也会应用工具白名单机制——切换模式不会改变系统的安全设置。

## 网页搜索后端

`web_search` 和 `web_extract` 工具支持五种后端提供商。您可以通过 `config.yaml` 文件或 `hermes tools` 命令来配置后端。

```yaml
web:
  backend: firecrawl    # firecrawl | searxng | parallel | tavily | exa

  # Or use per-capability keys to mix providers (e.g. free search + paid extract):
  search_backend: "searxng"
  extract_backend: "firecrawl"
```

| 后端服务 | 环境变量 | 搜索功能 | 数据提取功能 |
|---------|---------|--------|---------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ |
| **SearXNG** | `SEARXNG_URL` | ✔ | — |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ |

**后端服务选择：** 如果未设置 `web.backend`，系统会自动从已配置的 API 密钥中检测合适的后端。仅设置了 `SEARXNG_URL` 时则使用 SearXNG；仅设置 `EXA_API_KEY` 时使用 Exa；仅设置 `TAVILY_API_KEY` 时使用 Tavily；仅设置 `PARALLEL_API_KEY` 时使用 Parallel。否则默认使用 Firecrawl。

**SearXNG** 是一款免费、可自托管且注重隐私的元搜索引擎，能够查询 70 多种搜索引擎。它无需 API 密钥——只需将 `SEARXNG_URL` 设置为你的服务器地址（例如 `http://localhost:8080`）即可。SearXNG 仅支持搜索功能；若需执行数据提取，则需要额外的提取服务提供商（可通过设置 `web.extract_backend` 来指定）。有关 Docker 部署指南，请参阅 [网络搜索设置指南](/user-guide/features/web-search)。

**自托管 Firecrawl：** 需将 `FIRECRAWL_API_URL` 设置为指向你自己的服务器地址。当指定了自定义 URL 后，API 密钥则变为可选项（如需禁用身份验证，可在服务器上设置 `USE_DB_AUTHENTICATION=***`）。

**并行搜索模式：** 可通过设置 `PARALLEL_SEARCH_MODE` 来控制搜索行为——可选值包括 `fast`、`one-shot` 或 `agentic`（默认值为 `agentic`）。

**Exa：** 将 `EXA_API_KEY` 设置在 `~/.hermes/.env` 文件中。该服务支持按 `category` 进行筛选（如 `company`、`research paper`、`news`、`people`、`personal site`、`pdf`），同时也支持按域名和日期进行筛选。

## 浏览器

配置浏览器自动化行为：

```yaml
browser:
  inactivity_timeout: 120        # Seconds before auto-closing idle sessions
  command_timeout: 30             # Timeout in seconds for browser commands (screenshot, navigate, etc.)
  record_sessions: false         # Auto-record browser sessions as WebM videos to ~/.hermes/browser_recordings/
  # Optional CDP override — when set, Hermes attaches directly to your own
  # Chromium-family browser (via /browser connect) rather than starting a headless browser.
  cdp_url: ""
  # Dialog supervisor — controls how native JS dialogs (alert / confirm / prompt)
  # are handled when a CDP backend is attached (Browserbase, local Chromium-family
  # browser via /browser connect). Ignored on Camofox and default local agent-browser mode.
  dialog_policy: must_respond    # must_respond | auto_dismiss | auto_accept
  dialog_timeout_s: 300          # Safety auto-dismiss under must_respond (seconds)
  camofox:
    managed_persistence: false   # When true, Camofox sessions persist cookies/logins across restarts
    user_id: ""                  # Optional externally managed Camofox userId
    session_key: ""              # Optional session key sent when Hermes creates a tab
    adopt_existing_tab: false    # Reuse an existing tab for this identity before creating one
```

**对话策略：**

- `must_respond`（默认值）——捕获对话内容，并将其显示在 `browser_snapshot.pending_dialogs` 中，同时等待智能体调用 `browser_dialog(action=...)`。如果在 `dialog_timeout_s` 秒内未收到响应，该对话将自动关闭，以避免页面的 JavaScript 线程无限阻塞。
- `auto_dismiss`——捕获对话后立即关闭。之后，智能体仍可在 `browser_snapshot.recent_dialogs` 中看到该对话记录，其状态标记为 `closed_by="auto_policy"`。
- `auto_accept`——捕获对话后立即接受。此策略适用于那些会频繁弹出 `beforeunload` 警告的页面。

如需了解完整的对话处理流程，请参阅 [浏览器功能页面](./features/browser.md#browser_dialog)。

该浏览器工具集支持多种数据提供方。有关 Browserbase、浏览器使用方式以及本地 Chromium 系列 CDP 的设置详情，请查看 [浏览器功能页面](/user-guide/features/browser)。

## 时区

可通过 IANA 时区字符串来覆盖服务器默认的时区设置。这会影响到日志中的时间戳、cron 定时任务以及系统提示语的时间显示。

```yaml
timezone: "America/New_York"   # IANA timezone (default: "" = server-local time)
```

支持的值：任何IANA时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。如需使用服务器本地时间，可留空或省略该参数。

## Discord

配置消息网关针对Discord的特殊行为：

```yaml
discord:
  require_mention: true          # Require @mention to respond in server channels
  free_response_channels: ""     # Comma-separated channel IDs where bot responds without @mention
  auto_thread: true              # Auto-create threads on @mention in channels
```

- `require_mention` — 当设置为 `true`（默认值）时，机器人仅在通过 `@BotName` 被提及时才会在服务器频道中响应；而在私信中则无需提及即可正常回复。
- `free_response_channels` — 以逗号分隔的频道 ID 列表，机器人会在这些频道中对所有消息自动回复，而无需任何提及。
- `auto_thread` — 当设置为 `true`（默认值）时，机器人会在频道中自动为提及内容创建对话线程，从而保持频道整洁（功能类似 Slack 的线程功能）。

## 安全性

执行前的安全扫描与敏感信息遮蔽：

```yaml
security:
  redact_secrets: true           # Redact API key patterns in tool output and logs (on by default)
  tirith_enabled: true           # Enable Tirith security scanning for terminal commands
  tirith_path: "tirith"          # Path to tirith binary (default: "tirith" in $PATH)
  tirith_timeout: 5              # Seconds to wait for tirith scan before timing out
  tirith_fail_open: true         # Allow command execution if tirith is unavailable
  website_blocklist:             # See Website Blocklist section below
    enabled: false
    domains: []
    shared_files: []
```

- `redact_secrets` — 当设置为 `true` 时，会在工具输出内容进入对话上下文及日志之前，自动识别并屏蔽类似 API 密钥、令牌和密码的字符串。**默认处于开启状态**。仅当您需要原始的凭证类字符串用于调试或屏蔽功能开发时，才应明确将其设置为 `false`。
- `tirith_enabled` — 当设置为 `true` 时，终端命令在执行前会由 [Tirith](https://github.com/sheeki03/tirith) 进行扫描，以检测可能存在危险的操作。
- `tirith_path` — Tirith 可执行文件的路径。如果该工具安装在非标准位置，则需设置此参数。
- `tirith_timeout` — 等待 Tirith 扫描的最大秒数。若扫描超时，命令仍会继续执行。
- `tirith_fail_open` — 当设置为 `true`（默认值）时，即便 Tirith 不可用或扫描失败，命令也允许执行。将其设置为 `false` 可在 Tirith 无法验证命令时阻止其执行。

## 网站黑名单

阻止智能体的网页及浏览器工具访问特定域名：

```yaml
security:
  website_blocklist:
    enabled: false               # Enable URL blocking (default: false)
    domains:                     # List of blocked domain patterns
      - "*.internal.company.com"
      - "admin.example.com"
      - "*.local"
    shared_files:                # Load additional rules from external files
      - "/etc/hermes/blocked-sites.txt"
```

启用该功能后，任何匹配到被阻止域名模式的URL都将在Web或浏览器工具执行之前被拒绝。这适用于`web_search`、`web_extract`、`browser_navigate`以及所有能够访问URL的工具。

域名规则支持以下格式：
- 精确域名：`admin.example.com`
- 通配符子域名：`*.internal.company.com`（会阻止所有子域名）
- Top-Level Domain通配符：`*.local`

共享文件中每行对应一条域名规则（空行和以`#`开头的注释将被忽略）。如果存在缺失或无法读取的文件，系统会记录警告，但不会因此禁用其他Web工具。

该策略会被缓存30秒，因此无需重启即可快速应用配置更改。

## 智能审批功能

可控制Hermes如何处理可能存在危险的命令：

```yaml
approvals:
  mode: manual   # manual | smart | off
```

| 模式 | 行为 |
|------|------|
| `manual`（默认值） | 在执行任何被标记的命令之前向用户发起提示。在 CLI 环境中会显示交互式确认对话框；在消息交互场景中则会将待处理的审批请求放入队列中。 |
| `smart` | 利用辅助大语言模型来判断被标记的命令是否真的具有危险性。低风险命令会自动获得批准，并在会话期间保持该状态；而真正具有风险的命令则会提交给用户进行决策。 |
| `off` | 跳过所有审批检查。此设置等同于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

Smart 模式对于减少重复审批带来的疲劳感尤为有效——它能让智能体在安全操作上更自主地工作，同时仍能拦截那些真正具有破坏性的命令。

:::warning
将 `approvals.mode` 设置为 `off` 会禁用终端命令的所有安全检查。仅可在受信任的沙箱环境中使用此设置。
:::

## 检查点

在执行可能破坏文件的操作之前，系统会自动创建文件系统快照。详情请参阅 [检查点与回滚](/user-guide/checkpoints-and-rollback) 文档。

```yaml
checkpoints:
  enabled: false                 # Enable automatic checkpoints (also: hermes chat --checkpoints). Default: false (opt-in).
  max_snapshots: 20              # Max checkpoints to keep per directory (default: 20)
```


## 委派功能

配置用于委派工具的子代理行为：

```yaml
delegation:
  # model: "google/gemini-3-flash-preview"  # Override model (empty = inherit parent)
  # provider: "openrouter"                  # Override provider (empty = inherit parent)
  # base_url: "http://localhost:1234/v1"    # Direct OpenAI-compatible endpoint (takes precedence over provider)
  # api_key: "local-key"                    # API key for base_url (falls back to OPENAI_API_KEY)
  # api_mode: ""                            # Wire protocol for base_url: "chat_completions", "codex_responses", or "anthropic_messages". Empty = auto-detect from URL (e.g. /anthropic suffix → anthropic_messages). Set explicitly for non-standard endpoints the heuristic can't detect.
  max_concurrent_children: 3                # Parallel children per batch (floor 1, no ceiling). Also via DELEGATION_MAX_CONCURRENT_CHILDREN env var.
  max_spawn_depth: 1                        # Delegation tree depth cap (1-3, clamped). 1 = flat (default): parent spawns leaves that cannot delegate. 2 = orchestrator children can spawn leaf grandchildren. 3 = three levels.
  orchestrator_enabled: true                # Global kill switch. When false, role="orchestrator" is ignored and every child is forced to leaf regardless of max_spawn_depth.
```

**子代理提供者与模型覆盖：** 默认情况下，子代理会继承父代理的提供者和模型。若需将子代理指向不同的提供者/模型组合，可设置 `delegation.provider` 和 `delegation.model`——例如，在主代理使用高成本推理模型的同时，为任务范围较窄的子任务选用低成本或高速度的模型。

**直接端点覆盖：** 若希望使用自定义端点路径，可设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这样会将子代理直接发送到该兼容 OpenAI 的端点，且其优先级高于 `delegation.provider` 设置。若未指定 `delegation.api_key`，Hermes 将仅回退使用 `OPENAI_API_KEY`。

**Wire 协议（`api_mode`）：** Hermes 会自动根据 `delegation.base_url` 判断 Wire 协议类型（例如以 `/anthropic` 结尾的路径对应 `anthropic_messages`；Codex、原生 Anthropic 或 Kimi-coding 主机则保持原有的检测方式）。对于算法无法识别的端点——比如基于 Anthropic 架构的 Azure AI Foundry、MiniMax、Zhipu GLM 或 LiteLLM 代理——需手动将 `delegation.api_mode` 设置为 `chat_completions`、`codex_responses` 或 `anthropic_messages` 中的一种。若保持为空（即默认值），则继续采用自动检测方式。

子代理的提供者会使用与 CLI/gateway 启动时相同的凭据解析机制。所有已配置的提供者均受支持，包括：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。一旦设置了提供者，系统会自动确定对应的基地址、API 密钥及 API 模式，无需手动配置凭据。

**优先级规则：** 配置中的 `delegation.base_url` → 配置中的 `delegation.provider` → 继承自父代理的提供者；配置中的 `delegation.model` → 继承自父代理的模型。仅设置 `model` 而未设置 `provider` 时，仅会更改模型名称，凭据仍沿用父代理的设置（适用于在相同提供者如 OpenRouter 内切换模型）。

**并行度与层级限制：** `max_concurrent_children` 用于限制每批处理中可并行运行的子代理数量（默认值为 3，下限为 1，无上限）。也可通过环境变量 `DELEGATION_MAX_CONCURRENT_CHILDREN` 进行设置。当提交的 `tasks` 数组长度超过此限制时，`delegate_task` 会返回说明限制的工具错误信息，而不会默许截断数据。`max_spawn_depth` 则控制委托树的层级深度（限制在 1-3 层之间）。默认值为 1 时，委托结构为扁平结构：子代理无法生成孙代理；若设置 `role="orchestrator"`，则该子代理会自动降级为叶节点。将此值设为 2 可让编排者子代理生成叶节点级的孙代理；设为 3 则可构建三层结构的委托树。代理可通过每次调用时设置 `role="orchestrator"` 来选择是否启用编排功能；若设置 `orchestrator_enabled: false`，则所有子代理无论如何都会降级为叶节点。成本呈倍数增长——当 `max_spawn_depth: 3` 且 `max_concurrent_children: 3` 时，委托树最多可同时存在 3×3×3 = 27 个叶节点级代理。更多使用场景请参阅 [子代理委托 → 深度限制与嵌套编排](features/delegation.md#depth-limit-and-nested-orchestration)。

## 明确化提示配置

用于设置明确化提示的行为：

```yaml
clarify:
  timeout: 120                 # Seconds to wait for user clarification response
```

## 上下文文件（SOUL.md、AGENTS.md）

Hermes 支持两种不同的上下文作用域：

| 文件 | 用途 | 作用域 |
|------|------|-------|
| `SOUL.md` | **代理的主要身份标识**——用于定义代理的身份（系统提示词中的第1个字段） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定的指令（优先级最高） | 从项目根目录开始查找 |
| `AGENTS.md` | 项目特定的指令及编码规范 | 递归扫描目录结构 |
| `CLAUDE.md` | Claude Code 的上下文文件（也会被识别） | 仅限当前工作目录 |
| `.cursorrules` | Cursor IDE 规则文件（也会被识别） | 仅限当前工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被识别） | 仅限当前工作目录 |

- **SOUL.md** 是代理的核心身份标识，它占据系统提示词中的第1个字段，会完全替代内置的默认身份。通过编辑该文件可完全自定义代理的身份。
- 如果不存在、内容为空或无法加载 `SOUL.md`，Hermes 会回退到内置的默认身份。
- **项目上下文文件采用优先级机制**——仅会加载其中一种类型（第一个匹配到的生效）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。而 `SOUL.md` 始终会独立加载。
- **AGENTS.md` 具有层级结构**：如果子目录中也存在 `AGENTS.md`，则所有内容会合并处理。
- 如果尚未创建默认的 `SOUL.md`，Hermes 会自动生成一个。
- 所有已加载的上下文文件的长度都受 `context_file_max_chars` 参数限制（默认为20,000字符），系统会自动进行智能截断处理。

相关文档：
- [个性设置与 SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)

## 工作目录

| 上下文类型 | 默认值 |
|----------|--------|
| **CLI（`hermes`命令）** | 运行命令时的当前目录 |
| **消息传递网关** | `~/.hermes/config.yaml` 文件中的 `terminal.cwd` 设置；若未设置，则为用户的主目录 `~` |
| **Docker / Singularity / Modal / SSH 环境** | 容器或远程机器内的用户主目录 |

如需更改工作目录，可进行相应配置：
```yaml
# In ~/.hermes/config.yaml:
terminal:
  cwd: /home/myuser/projects
```

`~/.hermes/.env` 文件中的 `MESSAGING_CWD` 以及直接的 `TERMINAL_CWD` 设置仅作为旧版本兼容性的回退选项。新的配置应使用 `terminal.cwd`。
