---
sidebar_position: 2
title: "Hermes Agent Configuration"
description: "Configure Hermes Agent — config.yaml, providers, models, API keys, and more"
---

# Hermes Agent 配置

所有设置均存储在 `~/.hermes/` 目录中，便于随时访问。

:::提示 如何最便捷地生成可用的 `config.yaml` 文件
运行 `hermes setup --portal` 即可——只需完成一次 OAuth 认证，即可同时获得模型提供方以及四种 Tool Gateway 工具，而无需手动编辑 YAML 文件。Portal 用户还能享受按令牌计费的服务 10% 的折扣。详情请参阅 [Nous Portal](/integrations/nous-portal)。
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
hermes config get KEY      # Print a resolved value
hermes config set KEY VAL  # Set a specific value
hermes config unset KEY    # Remove a user-set value
hermes config check        # Check for missing options (after updates)
hermes config migrate      # Interactively add missing options

# Examples:
hermes config get model
hermes config set model anthropic/claude-opus-4
hermes config set terminal.backend docker
hermes config unset terminal.backend
hermes config set OPENROUTER_API_KEY sk-or-...  # Saves to .env
```

:::提示  
`hermes config set` 命令会自动将配置值路由到正确的文件中——API 密钥会被保存到 `.env` 文件中，而其他所有配置则保存到 `config.yaml` 中。  
:::

## 配置优先级  

配置项的解析顺序如下（优先级从高到低）：  

1. **CLI 参数**——例如 `hermes chat --model anthropic/claude-sonnet-4`（每次调用时均可覆盖现有设置）；  
2. **`~/.hermes/config.yaml`**——所有非敏感配置的主要配置文件；  
3. **`~/.hermes/.env`**——环境变量的备用存储位置；对于 API 密钥、令牌、密码等敏感信息，此文件是**必需的**；  
4. **内置默认值**——当未设置任何其他配置时，将使用硬编码的安全默认值。  

:::信息提示  
敏感信息（如 API 密钥、机器人令牌、密码）应存储在 `.env` 文件中；而模型类型、终端后端、压缩设置、内存限制、工具集等其他配置则应保存在 `config.yaml` 中。若两者都设置了相同配置，则非敏感配置以 `config.yaml` 中的值为准。  
:::

:::提示 组织级部署  
管理员可通过系统级托管目录，锁定某些特定的配置和敏感值，防止普通用户对其进行覆盖。详情请参阅[托管作用域](/user-guide/managed-scope)。  
:::

## 运行时限制  

对于长时间运行的 Hermes 服务器（包括网关以及通过 `hermes serve --isolated` 启动的实例），只要操作系统支持，其在启动时会应用所配置的 `RLIMIT_NOFILE` 软限制值。

```yaml
runtime:
  nofile_soft_limit: 4096
```

默认值为 `4096`。Hermes 会将该数值限制在操作系统的硬限制范围内，且不会降低那些已具有更高软限制的进程的值。如需禁用此调整功能，可将该值设置为 `0`、`false` 或 `null`。在 Windows 系统以及无法修改限制值的沙箱环境中，程序仍会继续启动，而不会更改该限制值。

## 数据库设置

`database:` 部分用于控制 Hermes 如何打开其 SQLite 状态数据库（即 `state.db`），该数据库用于存储会话信息、消息内容以及网关路由配置：

```yaml
database:
  # Journal mode for state.db: wal (default) or delete.
  # Use delete on filesystems where WAL is unsafe (network mounts, some
  # virtiofs setups). Note: an existing on-disk WAL database is never
  # live-downgraded — Hermes keeps WAL and logs an error telling you the
  # configured delete did not apply. To convert an existing database, stop
  # every process using it and run a one-time offline
  # `PRAGMA journal_mode=DELETE` on the file.
  journal_mode: wal

  # Durability level for every state.db connection: OFF, NORMAL, FULL,
  # EXTRA (or 0-3). Unset leaves SQLite's compile-time default, which
  # differs between interpreter builds. On macOS this is a floor, not a
  # pin: values below FULL are refused to protect against Darwin fsync
  # reordering; EXTRA is honored.
  # synchronous: FULL

  # Optional WAL sizing pragmas (integers). Unset = SQLite defaults.
  # wal_autocheckpoint: 1000     # pages between automatic checkpoints
  # journal_size_limit: 67108864 # cap the WAL/journal size in bytes
```

Hermes还会在每次进程启动、每次数据库连接时发出警告，提示现有数据库的磁盘日志模式在打开时被悄悄更改为WAL模式——例如操作员手动将某个数据库转换为`delete`模式的情况——并且指出`database.journal_mode`就是决定该设置生效的关键参数。

## 环境变量替换

您可以在`config.yaml`中使用`${VAR_NAME}`语法来引用环境变量：

```yaml
auxiliary:
  vision:
    api_key: ${GOOGLE_API_KEY}
    base_url: ${CUSTOM_VISION_URL}

delegation:
  api_key: ${DELEGATION_KEY}
```

单个值中可包含多个引用，格式如下：`url: "${HOST}:${PORT}"`。若引用的变量未被设置，占位符将保持原样（如`${UNDEFINED_VAR}`不会被替换），同时系统会记录警告。单独的 `$VAR` 格式则不会被展开。

在[多路复用多配置文件网关](/user-guide/multi-profile-gateways)环境下，配置文件 `config.yaml` 中的引用会针对**该配置文件自身**的 `.env` 文件（即其私有变量范围）进行解析，而非共享的进程环境——因此，除非配置文件 B 自身定义了该变量，否则其中的 `${MATRIX_ACCESS_TOKEN}` 将保持未解析状态。单配置文件运行模式则不受此影响。

系统也支持类似 Cursor 的 SecretRef 语法：`${env:VAR_NAME}` 的解析方式与 `${VAR_NAME}` 完全相同（`env:` 前缀会被省略），因此从 Cursor 或 Claude 配置中复制的 MCP 或提供程序代码片段，在 `config.yaml` 文件及 `mcp_servers` 块中均可直接使用且无需修改。其他类型的 SecretRef 来源（如 `${file:...}`、`${vault:...}`、`${bitwarden:...}`）则不会在代码行内被解析——外部密钥后端会在启动时通过 `secrets:` 块将对应值注入环境，因此应使用 `${env:NAME}` 的格式来引用这些变量；对于未知的前缀，系统仅会发出一次警告，随后仍会保持原样。

关于 AI 提供程序的设置（包括 OpenRouter、Anthropic、Copilot、自定义端点、自托管大型语言模型以及备用模型等），请参阅[AI 提供程序](/integrations/providers)章节。

### 提供程序超时设置

您可以为整个提供程序设置 `providers.<id>.request_timeout_seconds` 作为全局请求超时时间，同时为特定模型设置 `providers.<id>.models.<model>.timeout_seconds` 以实现覆盖。该配置适用于所有传输方式（OpenAI-wire、原生 Anthropic 及兼容 Anthropic 的接口）下的主轮询客户端、备用请求链、凭据更新后的重新构建过程，以及（针对 OpenAI-wire）的每个请求的超时参数——因此所配置的值将优先于旧的 `HERMES_API_TIMEOUT` 环境变量。

此外，您还可以为非流式过期调用检测器设置 `providers.<id>.stale_timeout_seconds`，并为特定模型设置 `providers.<id>.models.<model>.stale_timeout_seconds` 进行覆盖。此配置将优先于旧的 `HERMES_API_CALL_STALE_TIMEOUT` 环境变量。

若不设置这些参数，则会保留旧有的默认值（`HERMES_API_TIMEOUT=1800`、`HERMES_API_CALL_STALE_TIMEOUT=90`，原生 Anthropic 为 900）。当未显式指定时，本地端点会自动禁用非流式过期检测器；而对于非常大的上下文场景，该检测器的阈值可相应提高。目前该功能暂不支持 AWS Bedrock（无论是 `bedrock_converse` 还是 AnthropicBedrock SDK，均使用带有独立超时配置的 boto3）。相关示例请参见 [`cli-config.yaml.example`](https://github.com/NousResearch/hermes-agent/blob/main/cli-config.yaml.example) 文件中的注释说明。

## 更新行为

### 后台检查与 SSH 认证

启动时进行的更新检查会使用与网络请求相同的隔离式 Git 配置来读取源 URL。因此，全局的 `url.*.insteadOf` 重写规则无法让官方 SSH 远程地址在公共 HTTPS 检查中被隐藏。

Hermes 内部使用的隔离式 Git 命令默认设置为 `ssh -o BatchMode=yes`：遇到未知的主机密钥、密码或需要输入口令的加密密钥时，系统不会打开终端提示符，而是直接报错。而那些拥有有效密钥或已配置 SSH 代理的受信任主机则仍可正常完成身份验证。这一设置不会更改磁盘上的 Git 或 SSH 配置，也不会影响你在终端工具中运行的命令。

此内部默认设置会覆盖仓库中的 `core.sshCommand` 配置。不过，显式设置的 `GIT_SSH_COMMAND` 环境变量仍具有优先级，因此你可以在其中保留自定义的身份验证或传输命令。如果需要保持非交互模式，可在该自定义设置中加入 `-o BatchMode=yes`；而允许提示输入的覆盖设置仍可能中断正在运行的后台检查。

`hermes update` 的相关设置位于 `config.yaml` 文件的 `updates` 目录下：

```yaml
updates:
  pre_update_backup: quick       # quick (state snapshot, default) | full (snapshot + HERMES_HOME zip) | off
  backup_keep: 5                 # Keep this many full pre-update backup zips
  non_interactive_local_changes: stash  # stash | discard
  auto_switch_parked_branch: true       # auto-switch a clean, fully merged parked branch back to main
```

`pre_update_backup` 是唯一的预更新安全控制选项：`quick`（默认值）会将关键状态文件（配对数据、定时任务、配置文件、认证信息；超过 1 GiB 的文件将被跳过）快速快照到 `state-snapshots/` 目录中；`full` 模式除了执行快速快照外，还会将整个 `HERMES_HOME` 目录压缩并存入 `backups/` 目录，对于较大的目录而言，此模式可能需要更长的处理时间；`off` 则会关闭这两种功能。系统也会兼容旧的布尔值设置（`true` 对应 `full`，`false` 对应 `off`）。

`config.yaml` 文件本身的时间点副本——即在 `hermes setup` 重写该文件之前、`hermes migrate` 修改它之前，或是文件解析失败时生成的副本——会被保存到 `backups/config/config.yaml.<reason>.<timestamp>` 路径下。系统中会自动跳过重复的副本，仅保留每个原因对应的最新五个副本，因此这些副本不会在 `config.yaml` 旁边堆积过多。

对于通过 git 安装的版本，Hermes 会在检出更新分支或拉取代码之前，自动暂存已被跟踪的修改过的文件以及未被跟踪的文件。在交互式终端更新过程中，系统会在恢复这些暂存内容之前给出提示。而非交互式更新方式（如桌面/聊天应用、网关模式，或使用 `--yes` 参数）则会使用 `updates.non_interactive_local_changes` 参数：`stash` 模式会在成功拉取代码后恢复本地对源文件的修改；而 `discard` 模式则会在成功拉取后丢弃更新过程中产生的暂存内容。仅在使用那些不希望保留本地源文件修改记录的托管安装环境中才建议使用 `discard` 模式。

在执行暂存操作之前，Hermes 还会恢复因 npm install/build 操作而产生的已被跟踪的 `package-lock.json` 差异文件。在进行更新之前，请先提交或手动暂存那些有意对锁文件进行的修改。

Hermes 支持七种终端后端。每种后端都会决定智能体的 Shell 命令实际在何处执行——可以是您的本地机器、Docker 容器、通过 SSH 连接的远程服务器、Modal 云沙箱（直接连接或通过 Nous 管理的网关）、Daytona 工作空间、Vercel 沙箱，或是 Singularity/Apptainer 容器。

```yaml
terminal:
  backend: local    # local | docker | ssh | modal | daytona | vercel_sandbox | singularity
  cwd: "."          # Gateway/cron working directory (CLI always uses launch dir)
  temp_dir: ""      # Session temp root; empty = TMPDIR, else ~/.hermes/cache/terminal
  font_family: ""   # Desktop terminal font; e.g. "MesloLGS NF"
  timeout: 180      # Per-command timeout in seconds
  home_mode: auto   # auto | real | profile — subprocess HOME policy
  env_passthrough: []  # Env var names to forward to sandboxed execution (terminal + execute_code)
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"  # Container image for Singularity backend
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"                 # Container image for Modal backend
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"               # Container image for Daytona backend
```

`terminal.temp_dir` 用于控制 Hermes 在本地后端存储会话临时文件的路径——包括后台进程的日志、PID/退出文件、代码执行沙箱以及各种工具的运行结果。当该参数为空（即默认值）时，Hermes 会优先使用环境中指定的 `TMPDIR`/`TMP`/`TEMP` 路径；否则它会使用真实存储中的受管理目录 `~/.hermes/cache/terminal`，而非 `/tmp`。在许多发行版中（尤其是基于 Arch 的系统），`/tmp` 是一个由内存支持的小型 tmpfs 文件系统，在高负载情况下很容易被 Hermes 的会话临时文件占满。该受管理目录会自动清理：超过 72 小时的旧文件会由网关定期清除，而在仅通过 CLI 安装的系统中，则每个进程的旧文件也会被清除一次。若要将会话临时文件存储到其他位置，可设置 `temp_dir` 为现有的绝对路径；用户指定的路径不会被自动清理。

`terminal.font_family` 用于控制 Hermes Desktop 中内置终端的字体。该参数可以接受本地已安装的字体系列名称（例如 `MesloLGS NF`），也可以接受 CSS 字体堆栈格式。作为备用方案，Hermes 会自动添加其自带的 JetBrains Mono 字体堆栈；若该参数为空，则保持默认设置。您可以在 **设置 → 外观 → 终端字体** 中修改此同一配置项，无需下载 Google Fonts 字体或申请系统字体权限。

对于 Modal、Daytona 和 Vercel Sandbox 等云端沙箱环境，若设置 `container_persistent: true`，则表示 Hermes 会尝试在重新创建沙箱时保留文件系统状态。但请注意，这并不保证后续运行时仍会是同一个活跃的沙箱环境、相同的 PID 空间或原有的后台进程。

### 后端概述

| 后端类型 | 命令运行位置 | 隔离级别 | 最佳适用场景 |
|---------|-------------------|-----------|----------|
| **本地** | 直接在您的机器上运行 | 无隔离 | 开发及个人使用 |
| **Docker** | 单个持久化 Docker 容器（跨会话、/new 模式及子代理共享） | 完全隔离（通过命名空间与权限限制实现） | 安全的沙箱环境，CI/CD 流水线 |
| **SSH** | 通过 SSH 连接的远程服务器 | 网络层级隔离 | 远程开发，使用高性能硬件的情况 |
| **Modal** | Modal 云沙箱环境 | 完全隔离（基于云虚拟机） | 临时性云计算任务，代码评估 |
| **Daytona** | Daytona 工作空间 | 完全隔离（基于云容器） | 受管理的云开发环境 |
| **Vercel Sandbox** | Vercel Sandbox 平台 | 完全隔离（基于云微虚拟机） | 具有快照机制的文件系统持久化的云端执行环境 |
| **Singularity** | Singularity/Apptainer 容器 | 通过命名空间实现隔离（--containall 参数） | 高性能计算集群，共享式机器环境 |

### 本地后端

为默认后端选项。命令直接在您的机器上运行，且不进行任何隔离处理。无需特殊配置即可使用。

```yaml
terminal:
  backend: local
```

默认情况下，本地工具的子进程会保留您真实操作系统用户目录下的 `HOME`。这样一来，诸如 `git`、`ssh`、`gh`、`az`、`npm`、Claude Code 以及 Codex 等外部 CLI 就能找到其在常规终端中已使用的凭证与配置文件。Hermes 的状态仍通过 `HERMES_HOME` 来按配置文件进行管理；配置文件选择配置、内存、会话或技能时，并不会依据 `HOME` 来决定。

Hermes **不会**更改您系统级的 `HOME`、终端启动脚本，或是操作系统账户的主目录。该设置仅用于控制通过 `terminal` 等工具、后台终端进程、`execute_code` 功能以及 ACP 辅助进程所启动的子进程所接收的环境。

#### `terminal.home_mode`

| 模式 | 主机环境 | 容器环境 | 权衡点 |
|---|---|---|---|
| `auto` | 保留真实操作系统用户目录下的 `HOME` | 使用 `{HERMES_HOME}/home` | 推荐的默认模式。主机上的 CLI 可继续正常工作，同时容器的状态也能得以保留。 |
| `real` | 强制使用真实操作系统用户目录下的 `HOME` | 若可见则强制使用真实操作系统用户目录下的 `HOME` | 当父进程意外以指向配置文件主目录的 `HOME` 值启动时，此模式非常有用。 |
| `profile` | 若存在则使用 `{HERMES_HOME}/home` | 若存在则使用 `{HERMES_HOME}/home` | 能实现严格的按配置文件隔离 CLI 配置，但除非在配置文件主目录内进行初始化或关联，否则常规的 `~/.ssh`、`~/.gitconfig`、`~/.azure`、`~/.config/gh`、Claude/Codex 认证信息、npm 状态等文件将不可见。 |
默认设置的缺点在于，各主机配置文件会共享位于 `~` 目录下的相同普通用户级 CLI 凭据/配置。如果您需要为某个配置文件设置独立的 Git 身份、SSH 密钥、GitHub CLI 登录信息、npm 配置或云平台 CLI 登录信息，请使用 `home_mode: profile`，并有意将相关工具初始化到该配置文件的专用目录中。

如果您确实希望实现严格的按配置文件隔离的工具配置，可设置：

```yaml
terminal:
  home_mode: profile
```

在该模式下，工具的子进程会将 `{HERMES_HOME}/home` 作为 `HOME` 环境变量使用。Hermes 还会设置 `HERMES_REAL_HOME`，以便脚本在需要时仍能找到真正的用户主目录。而在“自动”模式下，容器后端仍会继续使用 `{HERMES_HOME}/home`，因为该目录位于持久化的 Hermes 数据卷中。那些需要区分配置文件所在位置与真实用户主目录的脚本，建议将 Hermes 数据路径设置为 `HERMES_HOME`，而将账户主目录路径设置为 `HERMES_REAL_HOME`。

```python
from pathlib import Path
import os

hermes_home = Path(os.environ["HERMES_HOME"])
real_home = Path(os.environ.get("HERMES_REAL_HOME", os.environ["HOME"]))
```

:::warning
该智能体拥有与您的用户账户相同的文件系统访问权限。如需禁用不需要的工具，可使用 `hermes tools` 命令；若需实现沙箱隔离，则可切换至 Docker 环境。
:::

### Docker 后端

在经过安全加固的 Docker 容器中执行命令（已移除所有特殊权限，杜绝权限提升风险，并设置了 PID 限制）。

**采用单个持久化容器，供所有 Hermes 进程共享。** Hermes 在首次使用时会启动一个长期运行的容器，随后通过 `docker exec` 命令将所有的终端操作、文件操作以及 `execute_code` 调用均引导至该容器中——这一机制适用于不同会话、/new 命令、/reset 命令以及 `delegate_task` 子智能体。工作目录变更、已安装的软件包、/workspace 目录中的文件以及**后台进程**，都会在多次工具调用之间以及不同的 Hermes 进程之间保持连续性。当您关闭 TUI 会话、执行 /quit 命令或启动新的 `hermes` 实例时，该容器仍会继续运行，下一个 Hermes 进程会通过标签查找机制重新使用它。具体的容器销毁规则请参见下文的“容器生命周期”部分。

**会话隔离模式（`container_persistent: false`）**。在 Docker 后端将 `container_persistent: false` 设为默认值后，系统会采用“**每个会话一个容器**”的机制：每一次聊天（桌面应用会话、网关对话、TUI 会话）都会在其首次调用终端或处理文件时创建一个全新的沙箱环境，而当该会话关闭或空闲时间超过 `lifetime_seconds` 设定的阈值后，该沙箱就会被销毁。不同会话之间完全互不关联——既不存在文件系统状态传递，也没有挂载点或后台进程的延续。若启用 `docker_mount_cwd_to_workspace: true`，则仅会将**当前会话所关联的**工作区挂载到 `/workspace` 目录下；而对于没有关联目录的新会话，则会生成一个空的工作区，而不会继承前一个会话的挂载设置。`delegate_task` 子代理仍会共享其父会话的容器。当需要将沙箱作为各次对话之间的安全隔离屏障时，可使用此模式；而若希望保持上文所述的长期运行的共享容器机制，则应继续使用默认的 `true` 值。

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: false  # Mount launch dir into /workspace
  docker_run_as_host_user: false   # See "Running container as host user" below
  docker_snap_compat: false        # See "Snap-packaged Docker (AppArmor)" below
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
  docker_network: true             # false = air-gap the container (--network=none)

  # Resource limits
  container_cpu: 1                 # CPU cores (0 = unlimited)
  container_memory: 5120           # MB (0 = unlimited)
  container_disk: 51200            # MB (requires overlay2 on XFS+pquota)
  container_persistent: true       # true = persist /workspace + /root, shared container; false = fresh container per session (see below)

  # Cross-process container reuse (defaults match the "one long-lived
  # container shared across sessions" contract — see Container lifecycle).
  docker_persist_across_processes: true   # Reuse container across Hermes restarts
  docker_shared_container_key: ""         # Opt in trusted profiles to one identity
  docker_orphan_reaper: true              # Sweep abandoned Exited containers at startup

  # Cross-backend lifecycle settings (apply to docker as well)
  timeout: 180                     # Per-command timeout in seconds
  lifetime_seconds: 300            # Idle-reaper window; also feeds 2× orphan-reaper threshold
```

**`docker_env`** 与 **`docker_forward_env`** 的区别在于：前者会直接注入你在配置中指定的 `KEY=value` 对（这些值来自 `config.yaml` 文件，或通过 `TERMINAL_DOCKER_ENV='{"DEBUG":"1"}'` 以 JSON 字典的形式传递）。而后者则从你的 shell 环境或 `~/.hermes/.env` 文件中读取数值，因此敏感信息永远不会出现在配置文件中。对于令牌类数据，建议使用 `docker_forward_env`；而对于容器所需的静态参数，则可使用 `docker_env`。

**`terminal.docker_extra_args`**（也可通过 `TERMINAL_DOCKER_EXTRA_ARGS='["--gpus=all"]'` 覆盖）允许你传递那些 Hermes 未将其作为标准键项提供的任意 `docker run` 参数，例如 `--gpus`、`--network`、`--add-host`，以及自定义的 `--security-opt` 设置等。每个参数值都必须为字符串形式，该参数列表会被追加到最终生成的 `docker run` 命令中，从而在必要时覆盖 Hermes 的默认设置。建议谨慎使用此类功能——那些与沙箱安全机制相冲突的参数（如权限降级、`--user` 设置、工作区绑定挂载等），都可能无形中削弱系统的隔离性。

**`terminal.docker_network`**（默认值为 `true`；环境变量：`TERMINAL_DOCKER_NETWORK`）——将其设置为 `false` 可使沙箱容器以 `--network=none` 的方式运行，从而切断代理命令的所有网络输出。此设置适用于 `terminal`、`execute_code` 以及各类文件处理工具所使用的执行容器。由于容器会在 Hermes 的不同进程间保持存在，因此在已有已联网的容器时将此值改为 `false` 会删除该容器并启动一个全新的隔离容器（系统会记录警告信息）；运行在旧容器中的后台进程也将丢失。相较于通过 `docker_extra_args` 传递 `--network=none`，建议使用此配置键。

**要求：** 需安装并运行 Docker Desktop 或 Docker Engine。Hermes 会扫描 `$PATH` 及 macOS 上常见的 Docker 安装路径（如 `/usr/local/bin/docker`、`/opt/homebrew/bin/docker`、Docker Desktop 应用程序包）。Podman 也支持直接使用：若系统中同时安装了两者，可设置 `HERMES_DOCKER_BINARY=podman`（或其完整路径）来强制使用 Podman。

#### 容器生命周期

每个由 Hermes 管理的容器都会被添加三个标签，以便后续进程及孤儿回收机制能够识别它：

- `hermes-agent=1` — 标识该容器为 Hermes 管理的容器
- `hermes-task-id=<经过处理的 task_id>` — 用于标识每个任务对应的重复使用检测机制
- `hermes-profile=<经过处理的 profile 名称>` — 默认情况下，该标签用于将重复使用及回收功能限制在当前活跃的 Hermes profile 范围内；若设置了 `docker_shared_container_key`，则将使用其经过处理后的值。
在启动时，Hermes会执行 `docker ps --filter label=hermes-task-id=<id> --filter label=hermes-profile=<identity>` 命令，一旦找到对应的容器便会**附加到该容器中**。除非通过 `docker_shared_container_key` 明确指定将多个受信任的配置文件合并为同一值，否则该 identity 即为当前活跃的配置文件。如果该容器已“退出”（例如在 Docker 守护进程重启后），系统会重新启动它并再次使用——文件系统状态及已安装的软件包会保留，但容器内的后台进程则不会。

当某个 Hermes 进程退出时——无论是通过 `/quit` 命令、关闭 TUI 会话、网关关闭，还是收到 SIGKILL 信号——在默认模式下，**该容器并不会被清理**，而是会继续运行。下一个 Hermes 进程会通过标签探测在几毫秒内便附加到该容器上。这正是“跨会话共享同一个长生命周期容器”这一设计要求所规定的行为：只有这样，后台进程（如 npm 监听器、开发服务器、长时间运行的 pytest 等）才能在多个会话之间持续运行。

**只有在以下情况下，该容器才会被终止（即先停止，然后再执行 `docker rm -f` 命令删除）：**

| 触发条件 | 触发时机 |
|---|---|
| `docker_persist_across_processes: false` | 启用显式的进程级隔离。每次调用 `cleanup()` 都会执行 `stop` + `rm -f` 操作，行为与 #20561 修复版本之前一致。 |
| 空闲回收机制（`lifetime_seconds`，默认 300 秒） | 仅当环境变量设置为 `persist_across_processes=false` 时生效。处于持久化模式的环境变量将不会被处理，容器可顺利度过空闲回收周期。 |
| 下次启动时的孤儿容器回收 | 会清理当前配置文件范围内、已标记为 hermes 且退出时间超过 `2 × lifetime_seconds`（默认 600 秒，即 10 分钟）的容器。**正在运行的容器绝不会被影响**，这体现了进程间的安全性。如需禁用此功能，可设置 `docker_orphan_reaper: false`。 |
| 用户直接操作 | 执行 `docker rm -f`、`docker system prune` 或重启 Docker Desktop 均可触发回收。由于我们未设置 `--restart=always`，因此主机重启后容器状态仍为“已退出”（其写时复制层会保留并在下次启动时被重新使用，但后台进程已消失）。 |

值得注意的边缘情况：

- 当容器内的 PID 1 因内存溢出而被强制终止时，该容器的状态会变为 `Exited`。下次重新启动时会通过 `docker start` 命令来启动它；此时文件系统状态得以保留，但后台进程则会被清除。
- **配置文件切换**功能能够实现容器间的隔离——标记为 `hermes-profile=work` 的容器，在运行于 `hermes-profile=research` 环境下的 Hermes 进程中是不可见的。孤儿进程清理机制同样受配置文件限制，因此跨配置文件的容器不会被意外清理，但除非在原有配置文件下重新启动 Hermes，否则它们也不会被自动处理。
- **显式跨配置文件共享**——对于需要在同一可信工作空间内协同工作的配置文件，可在 `terminal:` 配置项下设置相同的非空 `docker_shared_container_key`。此操作仅用于统一容器的标识标签，任务、数据输出及网络兼容性检查依然会正常执行。未设置该键的配置文件之间仍保持隔离状态。容器标识标签是由该键加上简短的哈希后缀生成的，因此外观相似的键（如 `team/workspace` 与 `team_workspace`）不会导致容器合并。**重要提示：共享容器仅会由最先启动它的配置文件创建一次**——该配置文件的 `docker_image`、卷设置、共享内存大小以及其他不可变的 Docker 配置将占据主导地位，后续启动的配置文件将直接基于这些设置进行连接；它们配置中的不同设置在容器被删除并重新创建之前均会被忽略。选择共享同一键的配置文件时，各方需就镜像及挂载项达成一致。
通过 `delegate_task(tasks=[...])` 生成的并行子代理会共享同一个容器——同时进行的 `cd` 操作、环境变量修改以及对同一路径的写入都可能引发冲突。如果某个子代理需要独立的沙箱环境，就必须通过 `register_task_env_overrides()` 注册针对该任务的镜像覆盖配置；而强化学习及基准测试环境（如 TerminalBench2、HermesSweEnv 等）则会为其各自的任务专用 Docker 镜像自动完成此项操作。

**安全加固措施：**
- 使用 `--cap-drop ALL`，仅保留 `DAC_OVERRIDE`、`CHOWN`、`FOWNER` 权限
- 设置 `--security-opt no-new-privileges`
- 限制进程数量为 256 个
- 为 `/tmp`（512MB）、`/var/tmp`（256MB）、`/run`（64MB）设置大小限制的临时文件系统

**凭证转发机制：** `docker_forward_env` 中列出的环境变量会首先从用户的 shell 环境中获取，其次再从 `~/.hermes/.env` 文件中读取。技能模块也可以声明 `required_environment_variables`，这些变量也会被自动合并。

#### 环境变量覆盖规则

`terminal:` 下的每个键值对都对应一个形式为 `TERMINAL_<KEY_UPPERCASE>` 的环境变量覆盖项。对于 Docker 后端而言，其中最有用的一些包括：

| Env var | Maps to | Notes |
|---|---|---|
| `TERMINAL_DOCKER_IMAGE` | `docker_image` | Base image |
| `TERMINAL_DOCKER_FORWARD_ENV` | `docker_forward_env` | JSON array: `'["GITHUB_TOKEN","OPENAI_API_KEY"]'` |
| `TERMINAL_DOCKER_ENV` | `docker_env` | JSON dict: `'{"DEBUG":"1"}'` |
| `TERMINAL_DOCKER_VOLUMES` | `docker_volumes` | JSON array of `"host:container[:ro]"` strings |
| `TERMINAL_DOCKER_EXTRA_ARGS` | `docker_extra_args` | JSON array |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | `docker_mount_cwd_to_workspace` | `true` / `false` |
| `TERMINAL_DOCKER_RUN_AS_HOST_USER` | `docker_run_as_host_user` | `true` / `false` |
| `TERMINAL_DOCKER_SNAP_COMPAT` | `docker_snap_compat` | `true` / `false` — default `false` |
| `TERMINAL_DOCKER_NETWORK` | `docker_network` | `true` / `false` — default `true`; `false` = `--network=none` |
| `TERMINAL_DOCKER_PERSIST_ACROSS_PROCESSES` | `docker_persist_across_processes` | `true` / `false` — default `true` |
| `TERMINAL_DOCKER_SHARED_CONTAINER_KEY` | `docker_shared_container_key` | Explicit shared identity for trusted profiles; empty by default |
| `TERMINAL_DOCKER_ORPHAN_REAPER` | `docker_orphan_reaper` | `true` / `false` — default `true` |
| `TERMINAL_CONTAINER_CPU` | `container_cpu` | CPU cores |
| `TERMINAL_CONTAINER_MEMORY` | `container_memory` | MB |
| `TERMINAL_CONTAINER_DISK` | `container_disk` | MB |
| `TERMINAL_CONTAINER_PERSISTENT` | `container_persistent` | `true` / `false` — controls the bind-mount workspace dirs, distinct from `docker_persist_across_processes` |
| `TERMINAL_LIFETIME_SECONDS` | `lifetime_seconds` | Idle reaper window |
| `TERMINAL_TEMP_DIR` | `temp_dir` | Session temp root (local backend) |
| `TERMINAL_TIMEOUT` | `timeout` | Per-command timeout |
| `HERMES_DOCKER_BINARY` | _none_ | Force a specific docker/podman binary path |

### SSH 后端

通过 SSH 在远程服务器上执行命令。该后端采用 ControlMaster 技术实现连接复用，并设置 5 分钟的空闲保持活跃机制。默认情况下已启用持久化Shell，因此命令执行间的工作目录及环境变量状态都会被保留。

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

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TERMINAL_SSH_PORT` | `22` | SSH 端口 |
| `TERMINAL_SSH_KEY` | （系统默认值） | SSH 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | `true` | 启用持久化 shell |

**工作原理：** 在初始化时会以 `BatchMode=yes` 和 `StrictHostKeyChecking=accept-new` 的参数建立连接。持久化 shell 会在远程主机上保持一个 `bash -l` 进程运行，通过临时文件进行通信。需要 `stdin_data` 或 `sudo` 权限的命令会自动切换到一次性执行模式。

**技能/配置环境变量传递：** 技能在 `required_environment_variables` 中声明的变量，或用户在 `terminal.env_passthrough` 中列出的变量，会通过 OpenSSH 的 `SendEnv` 功能进行传递——变量名会出现在 `ssh` 命令行中，而其值则通过客户端环境传递，绝不会出现在远程命令文本中。远程端的 `sshd` 必须能够接收这些变量；可在服务器上的 `/etc/ssh/sshd_config` 文件中进行相应配置，然后重新加载 sshd 服务：

```
AcceptEnv NEXTCLOUD_URL NEXTCLOUD_*      # or the names your skills need
```

若未指定对应的 `AcceptEnv`，服务器会静默忽略这些变量，从而导致远程 Shell 认为它们未被设置。即便在配置中列出了 Hermes 提供商的凭证（如 `OPENAI_API_KEY` 等），这些凭证也绝不会被转发。详情请参阅[环境变量传递机制](security.md#environment-variable-passthrough)。

### Modal 后端

在 [Modal](https://modal.com) 云沙箱中执行命令。每个任务都会获得一台独立的虚拟机，其 CPU、内存和磁盘资源均可自定义。此外，文件系统支持在不同会话之间进行快照创建与恢复。

```yaml
terminal:
  backend: modal
  container_cpu: 1                 # CPU cores
  container_memory: 5120           # MB (5GB)
  container_disk: 51200            # MB (50GB)
  container_persistent: true       # Snapshot/restore filesystem
```

**必需项：** 要么提供 `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` 环境变量，要么提供 `~/.modal.toml` 配置文件。

**状态持久化：** 开启该功能后，沙箱文件系统会在清理时生成快照，并在下次会话时恢复。这些快照会被记录在 `~/.hermes/modal_snapshots.json` 文件中。此功能可保留文件系统状态，但无法保存正在运行的进程、PID 空间或后台任务。

**凭证文件：** 会自动从 `~/.hermes/` 目录加载凭证文件（如 OAuth 令牌等），并在执行每个命令之前进行同步。

### Daytona 后端

在 [Daytona](https://daytona.io) 托管的工作空间中运行命令。支持暂停/继续操作以实现状态持久化。

```yaml
terminal:
  backend: daytona
  container_cpu: 1                 # CPU cores
  container_memory: 5120           # MB → converted to GiB
  container_disk: 10240            # MB → converted to GiB (max 10 GiB)
  container_persistent: true       # Stop/resume instead of delete
```

**必需项：** `DAYTONA_API_KEY` 环境变量。

**持久化设置：** 开启该功能后，沙箱在清理时会暂停运行（而非被删除），并在下次会话时自动恢复。沙箱的命名规则为 `hermes-{task_id}`。

**磁盘容量限制：** Daytona 设置的最大磁盘使用量为 10 GiB。超过此限制的请求将会被限制并同时发出警告。

### Vercel 沙箱后端

命令将在 [Vercel 沙箱](https://vercel.com/docs/vercel-sandbox) 这一云原生微虚拟机中执行。Hermes 会使用常规的终端和文件操作工具，不提供任何针对 Vercel 的专用模型交互工具。

```yaml
terminal:
  backend: vercel_sandbox
  vercel_runtime: node24          # node24 | node22 | python3.13
  cwd: /vercel/sandbox            # default workspace root
  container_persistent: true      # Snapshot/restore filesystem
  container_disk: 51200           # Shared default only; custom disk is unsupported
```

**必需的安装步骤：** 需要额外安装可选的 SDK。

```bash
pip install 'hermes-agent[vercel]'
```

**必需的认证方式：** 需要同时配置 `VERCEL_TOKEN`、`VERCEL_PROJECT_ID` 和 `VERCEL_TEAM_ID` 三种参数以实现访问令牌认证。这是在 Render、Railway、Docker 以及类似平台上进行应用部署及运行常规长时间运行的 Hermes 进程所支持的配置方式。

对于偶尔的本地开发场景，Hermes 也支持使用有效期较短的 Vercel OIDC 令牌：

```bash
VERCEL_OIDC_TOKEN="$(vc project token <project-name>)" hermes chat
```

若从关联的 Vercel 项目目录中调用，可省略项目名称：

```bash
VERCEL_OIDC_TOKEN="$(vc project token)" hermes chat
```

OIDC令牌的有效期较短，不应作为文档中规定的部署方式。

**运行时环境：** `terminal.vercel_runtime`支持`node24`、`node22`和`python3.13`。若未进行设置，Hermes将默认使用`node24`。

**数据持久性：** 当设置`container_persistent: true`时，Hermes会在清理过程中对沙箱文件系统创建快照，并从该快照中恢复同一任务后续使用的沙箱环境。快照内容可包含通过Hermes同步的凭证、技能以及被复制到沙箱中的缓存文件。此功能仅能保留文件系统状态，无法保留活跃沙箱的标识、进程ID空间、shell状态或正在运行的后台进程。

**后台命令：** `terminal(background=true)`会使用Hermes通用的非本地后台进程处理机制。在沙箱处于运行状态时，您可以通过常规进程管理工具来启动、轮询、等待、查看日志以及终止进程。不过，Hermes并不提供在清理或重启后恢复Vercel原生分离进程的功能。

**磁盘容量：** 目前Vercel Sandbox不支持Hermes的`container_disk`配置选项。请将`container_disk`保持未设置状态或使用默认值`51200`；非默认值会导致诊断失败及后端创建失败，而不会被静默忽略。

### Singularity/Apptainer后端

在[Singularity/Apptainer](https://apptainer.org)容器中执行命令。该后端专为那些无法使用Docker的高性能计算集群及共享机器设计。

```yaml
terminal:
  backend: singularity
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"
  container_cpu: 1                 # CPU cores
  container_memory: 5120           # MB
  container_persistent: true       # Writable overlay persists across sessions
```

**系统要求：** `$PATH` 环境变量中需包含 `apptainer` 或 `singularity` 可执行文件。

**镜像处理：** Docker 链接（`docker://...`）会自动转换为 SIF 文件并缓存起来；现有的 `.sif` 文件则可直接使用。

**临时目录路径：** 依次按照以下顺序确定：`TERMINAL_SCRATCH_DIR` → `TERMINAL_SANDBOX_DIR/singularity` → `/scratch/$USER/hermes-agent`（高性能计算领域的常用路径）→ `~/.hermes/sandboxes/singularity`。

**隔离机制：** 通过 `--containall --no-home` 参数实现完整的命名空间隔离，同时不会挂载主机上的用户主目录。

### 常见的终端后端问题

如果终端命令立即失败，或系统提示相关终端工具已禁用，则可能遇到以下问题：

- **本地模式（Local）** — 无特殊要求，是入门时最安全的默认选择。
- **Docker 模式** — 运行 `docker version` 命令以确认 Docker 正常运行。若命令失败，请修复 Docker 环境，或执行 `hermes config set terminal.backend local` 将后端切换回本地模式。
- **SSH 模式** — 必须同时设置 `TERMINAL_SSH_HOST` 和 `TERMINAL_SSH_USER` 参数。若缺少任意一个参数，Hermes 会输出明确的错误提示。
- **Modal 模式** — 需要 `MODAL_TOKEN_ID` 环境变量或 `~/.modal.toml` 配置文件。可运行 `hermes doctor` 命令进行检查。
- **Daytona 模式** — 需要 `DAYTONA_API_KEY`。Daytona SDK 会负责处理服务器地址的配置。
- **Singularity 模式** — `$PATH` 环境变量中需包含 `apptainer` 或 `singularity` 可执行文件，此模式在高性能计算集群中较为常见。

如有疑问，建议先将 `terminal.backend` 设置回 `local` 模式，确认命令在该模式下能够正常运行。

### 终止时实现远程端与主机端的状态同步

对于 **SSH**、**Modal** 和 **Daytona** 后端，Hermes 会在会话期间将用户位于 `~/.hermes/` 目录下的状态数据（包括凭证文件、技能模块及缓存内容）推送到远程沙箱中；而在会话结束时，则会将这些发生变动的状态文件**同步回**其原始所在位置。那些通过内容哈希校验后发现与最初推送的版本存在差异的文件会被重新应用到对应位置；而在已同步目录下新生成的远程文件（例如代理在远程端创建的技能模块），则会映射到相应的主机路径上。仅用于上传的凭证文件则绝不会被覆盖在主机上。

- 同步回放功能会最多尝试 3 次，并采用退避策略；同时，它不会尝试提取大小超过 2 GiB 的远程归档文件。
- Docker 和 Singularity 使用绑定挂载方式（即实时查看主机文件系统），因此无需此功能。
- 该机制仅适用于 Hermes 状态数据（`~/.hermes/` 目录下的内容），**不涵盖**沙箱内的任意其他工作目录文件——建议用户在销毁沙箱之前，通过 `scp` 或 `modal volume put` 等方式手动将重要文件复制出来。

### Docker 卷挂载

在使用 Docker 后端时，`docker_volumes` 功能允许用户将主机目录与容器共享。每个配置项均采用标准的 Docker `-v` 语法：`host_path:container_path[:options]`。

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
- **从智能体接收文件**（生成的代码、报告、导出内容）；  
- **共享工作空间**，使您与智能体能够访问相同的文件。  

如果您使用消息网关，并希望让智能体通过 `MEDIA:/...` 发送生成的文件，建议使用主机可访问的专用导出挂载路径，例如 `/home/user/.hermes/cache/documents:/output`。  
- 在 Docker 容器中，将文件写入 `/output/...`；  
- 在 `MEDIA:` 中指定**主机路径**，例如：`MEDIA:/home/user/.hermes/cache/documents/report.txt`；  
- 除非网关进程在主机上确实存在该路径，否则请勿使用 `/workspace/...` 或 `/output/...`。  

:::warning  
YAML 文件中重复的键会自动覆盖之前的值。如果您已存在 `docker_volumes:` 块，请将新的挂载项合并到同一列表中，而非在文件后添加另一个 `docker_volumes:` 键。  
:::  

该设置也可通过环境变量配置：`TERMINAL_DOCKER_VOLUMES='["/host:/container"]'`（JSON 数组格式）。  

### Docker 凭证转发  

默认情况下，Docker 终端会话不会继承主机的任意凭证。如果您需要在容器内使用特定令牌，请将其添加到 `terminal.docker_forward_env` 中。

```yaml
terminal:
  backend: docker
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
```

Hermes 首先会解析您当前 shell 中列出的各个变量，如果这些变量是通过 `hermes config set` 保存的，则会回退到 `~/.hermes/.env` 文件中查找。

:::warning
`docker_forward_env` 中列出的任何内容都会被容器内运行的命令所访问。请仅转发那些您愿意在终端会话中公开的凭据。
:::

### 以主机用户身份运行容器

默认情况下，Docker 容器是以 `root`（UID 0）身份运行的。在 `/workspace` 或其他绑定挂载目录中创建的文件，其所有权最终属于主机上的 root 用户。因此，在会话结束后，您需要先使用 `sudo chown` 命令更改文件所有权，才能通过主机上的编辑器对其进行修改。`terminal.docker_run_as_host_user` 参数可解决这一问题：

```yaml
terminal:
  backend: docker
  docker_run_as_host_user: true   # default: false
```

启用该功能后，Hermes 会在 `docker run` 命令中追加 `--user $(id -u):$(id -g)` 参数，这样写入绑定挂载目录（如 `/workspace`、`/root` 以及 `docker_volumes` 中的任何目录）的文件将归属于宿主机的用户而非 root 用户。不过这样做会带来一个弊端：容器将无法执行 `apt install` 操作，也无法向 root 所拥有的路径（如 `/root/.npm`）写入数据。如果需要同时满足这两点，可使用 `HOME` 目录归属于非 root 用户的基础镜像（或是在构建镜像时添加所需的工具）。

若希望保持向后兼容性，可将其保持为默认值 `false`。只有当您的工作流程主要是“编辑宿主机上的挂载文件”，并且已经厌倦了频繁使用 `sudo chown -R` 命令时，才建议启用此功能。

### Snap 包装的 Docker（AppArmor）

在通过 snap 方式安装 Docker 的主机上（常见于 Ubuntu 云镜像，例如 Azure 虚拟机），snap 的 AppArmor 约束机制会拒绝 sandbox 的两项强化配置选项，从而导致容器在启动时即崩溃：

```
exec /sbin/docker-init: operation not permitted     # --init
exec /usr/bin/sleep: operation not permitted        # --security-opt no-new-privileges
```

这是 Snapd 的固有限制（[LP#1908448](https://bugs.launchpad.net/snapd/+bug/1908448)），Hermes 无法对此进行干预。您可以选择从 Docker 的 apt 仓库安装 Docker 而非使用 Snap 版本（这是最佳方案，因为所有安全加固措施依然有效），或者选择启用相应功能：

```yaml
terminal:
  docker_snap_compat: true   # drops --init and no-new-privileges; cap-drop, tmpfs, PID limits stay
```

启用该功能后，沙箱内的僵尸进程将不会被 init 进程回收，且容器内的 setuid 二进制文件也能重新获取权限；容器启动时会记录一条警告信息。

### 可选：将启动目录挂载到 `/workspace`

Docker 沙箱默认处于隔离状态。除非您明确选择，否则 Hermes **不会**将主机上的当前工作目录传递给容器。

可在 `config.yaml` 中开启该功能：

```yaml
terminal:
  backend: docker
  docker_mount_cwd_to_workspace: true
```

启用该功能时：
- 若从 `~/projects/my-app` 启动 Hermes，该主机目录将会被绑定挂载到 `/workspace`；
- Docker 后端将在 `/workspace` 中启动；
- 文件操作工具与终端命令都能访问同一个已挂载的项目目录。

若禁用该功能，则 `/workspace` 仍由沙箱拥有，除非您通过 `docker_volumes` 显式挂载其他目录。

相应的安全权衡为：
- 设置为 `false` 可保持沙箱隔离边界；
- 设置为 `true` 则允许沙箱直接访问用于启动 Hermes 的目录。

仅当您确实希望容器能够操作宿主机上的实时文件时，才应启用此功能。

### 持久化 Shell

默认情况下，每个终端命令都在独立的子进程中运行——工作目录、环境变量及 shell 变量会在不同命令之间重置。当启用**持久化 Shell**后，一个长期运行的 bash 进程将在多次 `execute()` 调用之间保持存活，从而使命令间的状态得以保留。

这一功能对**SSH 后端**尤为有用，因为它还能消除每次命令执行时的连接开销。SSH 后端默认启用持久化 Shell，而本地后端则默认禁用该功能。

```yaml
terminal:
  persistent_shell: true   # default — enables persistent shell for SSH
```

如需禁用：

```bash
hermes config set terminal.persistent_shell false
```

**在多个命令之间保持不变的项：**
- 工作目录（执行 `cd /tmp` 后，该设置会在后续命令中依然有效）
- 导出的环境变量（如 `export FOO=bar`）
- Shell 变量（如 `MY_VAR=hello`）

**优先级规则：**

| 级别 | 变量名 | 默认值 |
|-------|--------|---------|
| 配置文件设置 | `terminal.persistent_shell` | `true` |
| SSH 覆盖设置 | `TERMINAL_SSH_PERSISTENT` | 以配置文件值为准 |
| 本地覆盖设置 | `TERMINAL_LOCAL_PERSISTENT` | `false` |

后端特定的环境变量具有最高优先级。如果您希望在本地后端也实现持久化 Shell 环境，可进行相应设置：

```bash
export TERMINAL_LOCAL_PERSISTENT=true
```

:::note
由于持久化 shell 的标准输入已被 IPC 协议占用，因此那些需要 `stdin_data` 或 sudo 权限的命令会自动切换到单次执行模式。
:::

如需了解各后端的详细信息，请参阅 [代码执行功能](features/code-execution.md) 以及 [README 中的终端相关部分](features/tools.md)。

## 技能设置

技能可通过其 SKILL.md 前置标记定义自身的配置选项。这些为非机密值（如路径、偏好设置、领域配置），会存储在 `config.yaml` 文件的 `skills.config` 命名空间下。

```yaml
skills:
  config:
    myplugin:
      path: ~/myplugin-data   # Example — each skill defines its own keys
```

**技能设置的工作原理：**

- `hermes config migrate` 会扫描所有已启用的技能，找出未配置的设置，并提示您进行设置。
- `hermes config show` 会在“技能设置”选项下显示所有技能设置及其所属的技能名称。
- 当某个技能加载时，其解析后的配置值会自动注入到该技能的上下文中。

**手动设置值：**

```bash
hermes config set skills.config.myplugin.path ~/myplugin-data
```

如需了解在自定义技能中声明配置设置的详细信息，请参阅[创建技能 — 配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

### 对智能体创建的技能内容的写入进行防护

当智能体使用 `skill_manage` 功能来创建、编辑、修改或删除某个技能时，Hermes 可以选择性地扫描新生成或更新的内容，以检测其中是否存在危险的关键词模式（如凭证窃取、明显的提示词注入、数据外传指令等）。该扫描功能**默认处于关闭状态**——因为那些确实需要访问 `~/.ssh/` 目录或包含 `$OPENAI_API_KEY` 的真实智能体工作流，常常会频繁触发误报。如果您希望在智能体写入技能内容之前收到警告，请将其重新开启：

```yaml
skills:
  guard_agent_created: true   # default: false
```

当该功能处于开启状态时，所有被标记为 `skill_manage` 类型的写入操作都会以包含扫描器分析理由的审批提示形式呈现。获批的写入操作将会成功执行，而被拒绝的写入操作则会向智能体返回说明性错误信息。

### 技能写入操作的审批机制

独立于上述内容扫描器之外，`skills.write_approval` 会要求对**所有**智能体技能相关的写入操作（创建、编辑、修补、删除及相关文件）进行手动审批——其审批/拒绝机制与处理危险命令的机制完全相同。

```yaml
skills:
  write_approval: false   # false = write freely (default) | true = stage every write for review
```

开启该功能后，技能写入操作将被暂存于 `~/.hermes/pending/skills/` 目录中，用户可通过 CLI 或任何消息平台，使用 `/skills pending`、`/skills diff <id>`、`/skills approve <id>`、`/skills reject <id>` 等命令对它们进行审核。运行时也可通过 `/skills approval on|off` 来切换此功能状态。内存相关的操作同样遵循相同的审批机制（即下文的 `memory.write_approval`）。完整操作指南请参阅：[限制技能写入操作](/user-guide/features/skills#gating-agent-skill-writes-skillswrite_approval)。

## 内存配置

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200   # ~800 tokens
  user_char_limit: 1375     # ~500 tokens
  write_approval: false     # true = require approval before any memory write
```

当设置 `memory.write_approval: true` 时，所有内存写入操作在生效前都需要经过您的批准：交互式 CLI 会直接在提示语中显示相关操作；而消息交流会话及后台自我优化阶段则会将写入内容暂存为 `/memory pending`，随后提交至 `/memory approve <id>` 或 `/memory reject <id>` 进行审批。您可以通过 `/memory approval on|off` 在运行时切换此功能。详情请参阅[控制内存写入](/user-guide/features/memory#controlling-memory-writes-write_approval)。

## 上下文文件截断设置

该选项用于控制 Hermes 在应用开头/结尾截断功能之前，从每个自动上下文文件中加载的内容量。此设置适用于注入到系统提示语中的文件，如 `SOUL.md`、`.hermes.md`、`AGENTS.md`、`CLAUDE.md` 以及 `.cursorrules`。它**不会**影响 `read_file` 工具。

```yaml
context_file_max_chars: null  # default — dynamic cap scaled to the model's context window (floor 20K, ceiling 500K chars)
```

设置一个正整数，即可固定上限而非采用动态调整机制：

```yaml
context_file_max_chars: 25000
```

每次读取的上下文文件也受到 `context_file_read_timeout`（单位：秒，默认值为 `5.0`）的限制。对于那些读取速度较慢的文件——通常是指存储在 iCloud Drive、OneDrive 或 NFS 等基于网络的文件系统中的文件——系统会发出警告并跳过该文件的读取，以确保系统的其余提示内容仍能正常加载。

```yaml
context_file_read_timeout: 5.0
```

## 文件读取安全性

用于控制单次 `read_file` 调用可返回的内容量。超出限制的读取请求将会被拒绝，并给出错误提示，建议智能体使用 `offset` 和 `limit` 参数来指定更小的读取范围。这样一来，就能避免一次性读取压缩后的 JS 包或大型数据文件导致上下文窗口被过度占用。

```yaml
file_read_max_chars: 100000  # default — ~25-35K tokens
```

如果您使用的是上下文窗口较大的模型且经常需要读取大型文件，请将其值调高。而对于上下文窗口较小的模型，为提升读取效率，建议将此值调低。

```yaml
# Large context model (200K+)
file_read_max_chars: 200000

# Small local model (16K context)
file_read_max_chars: 30000
```

该智能体还会自动对文件读取操作进行去重处理——如果同一个文件区域被读取了两次且文件内容并未发生变化，它就会返回一个轻量级的占位符，而无需重新发送实际内容。当上下文被压缩后，这一机制会重置，从而使智能体能够在文件内容被总结后再次读取这些文件。

## 工具输出截断限制

有三个相关的上限规则控制着工具在Hermes对其内容进行截断之前可以返回的原始输出量：

```yaml
tool_output:
  max_bytes: 50000        # terminal output cap (chars)
  max_lines: 2000         # read_file pagination cap
  max_line_length: 2000   # per-line cap in read_file's line-numbered view
```

- **`max_bytes`** — 当某个 `terminal` 命令生成的 stdout 和 stderr 合计字符数超过此值时，Hermes 会保留前 40% 和后 60% 的内容，并在两者之间插入 `[OUTPUT TRUNCATED]` 的提示。默认值为 50000（使用常见分词器时约相当于 12,000–15,000 个标记）。
- **`max_lines`** — 单次 `read_file` 调用中 `limit` 参数的上限值。超过此限制的请求会被限制，以防止单次读取操作占用过多的上下文窗口空间。默认值为 2000。
- **`max_line_length`** — 当 `read_file` 以带行号的形式输出内容时，每行内容的最大长度限制。超过此长度的行会被截断为指定字符数后加上 `... [truncated]` 的提示。默认值为 2000。

对于那些具备较大上下文窗口、且每次调用能够处理更多原始输出的数据模型，可适当提高这些限制值；而对于上下文窗口较小的模型，则应降低这些限制，以确保工具输出的结果更为精简。

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

### 工具结果溢出预算

除内容截断外，过大的工具*输出结果*会直接写入磁盘而非被截断：完整输出会保存在`$/HERMES_HOME/cache/spillover/`目录下，而上下文中的相关内容则会被预览信息及该文件的路径所替代（可通过`read_file`函数结合`offset`/`limit`参数读取，或使用`execute_code`函数进行处理）。默认的每条结果溢出阈值为100,000个字符，对于上下文容量较小的模型，该阈值会自动降低。

MCP工具的结果（名称为`mcp_*`的工具）的默认溢出阈值更为严格，为**50,000个字符**：由于MCP服务器通常会返回大量未分页的大体积数据（如工具发现目录、批量执行结果），这些数据原本可能处于通用阈值范围内，从而导致后续每次对话时上下文容量持续增加。不过所有数据都不会丢失——完整结果仍会保存在磁盘中。如需更改该阈值，可通过以下方式操作：

```yaml
tool_budget:
  mcp_result_size_chars: 50000   # per-result spillover threshold for mcp_* tools
```

MCP 的阈值始终受到（可能根据上下文动态调整的）通用单条结果阈值限制，因此即便提高该阈值，也不得超出当前模型上下文窗口允许的范围。

Hermes 还会标记**提供方端的截断现象**：当 MCP 或 Web 工具的结果中包含自身的截断标识（如“...还有 N 项”、“`"has_more": true`”以及“已保存至沙箱”之类的提示）时，系统会在结果后附加一行说明，警告用户当前显示的数据并不完整，在将任何列举视为完整之前需进行分页查询或进一步获取数据。

## 全局禁用工具集

若需在一处同时禁用 CLI 及所有网关平台上的特定工具集，只需在 `agent.disabled_toolsets` 下列出这些工具集的名称即可：

```yaml
agent:
  disabled_toolsets:
    - memory       # hide memory tools + MEMORY_GUIDANCE injection
    - web          # no web_search / web_extract anywhere
```

该配置会在各平台工具设置（由 `hermes tools` 生成的 `platform_toolsets`）之后生效，因此此处列出的工具集将会被移除——即便该平台的已保存配置中仍保留有相关设置。当您希望通过一个简单操作即可“在所有地方关闭X功能”，而无需在 `hermes tools` 的界面中编辑15行以上的平台配置时，可使用此方法。

若将列表留空或省略该键，则不会产生任何影响。

## Git工作树隔离

启用Git工作树隔离功能，即可在同一个仓库上并行运行多个Agent。

```yaml
worktree: true    # Always create a worktree (same as hermes -w)
# worktree: false # Default — only when -w flag is passed
```

启用该功能后，每个 CLI 会话都将在 `.worktrees/` 目录下创建一个包含独立分支的新工作树。各 Agent 可以独立编辑文件、执行提交、推送操作以及创建 Pull Request，而互不干扰。退出时会自动清除干净的工作树，而状态未同步的工作树则会保留以便后续手动恢复。

默认情况下，新工作树会从**最新拉取的远程分支尖端**（即当前分支的上游分支，若不存在则使用远程仓库的默认分支）创建分支，这样就能确保工作树与项目状态保持一致，而非基于本地克隆中可能已过时的 `HEAD` 分支。这样一来，Pull Request 的差异对比就能准确反映实际变更内容，而不会受到本地克隆滞后状态的干扰。如需以本地 `HEAD` 分支作为基础，可设置 `worktree_sync: false` —— 这在离线环境下或需要以克隆版本的精确当前状态为基准时非常有用。如果无法连接到远程仓库，系统会自动回退到使用本地 `HEAD` 分支。

```yaml
worktree_sync: true    # Default — branch from the fetched remote tip
# worktree_sync: false # Branch from local HEAD (offline / pinned base)
```

您还可以在仓库根目录中使用 `.worktreeinclude` 文件，列出需要复制到工作树中的被 Git 忽略的文件。

```
# .worktreeinclude
.env
.venv/
node_modules/
```

## 上下文压缩功能

Hermes 会自动对较长的对话内容进行压缩，以确保其长度在模型上下文窗口允许范围内。该压缩功能通过独立的 LLM 调用实现——您可以将它指向任意提供商或接口端点。

所有压缩相关设置均保存在 `config.yaml` 文件中（无需使用环境变量）。

### 完整参考文档

```yaml
compression:
  enabled: true                                     # Toggle compression on/off
  progress_notices: false                           # Opt-in: deliver routine compression progress notices to chat platforms — see below
  threshold: 0.50                                   # Compress at this % of context limit
  threshold_tokens: null                            # Absolute token cap (optional) — takes lower of ratio vs absolute
  target_ratio: 0.20                                # Fraction of threshold to preserve as recent tail
  tail_mode: lean                                   # Tail retention: "lean" (default — clamped 2.5% tail, 10K-25K, with a detailed session log + anchor index + session_search recovery pointers in the summary, all from ONE auxiliary summarizer call; ~3x fewer retained tokens after compaction) or "legacy" (0.20×threshold verbatim tail)
  protect_last_n: 20                                # Min recent messages to keep uncompressed
  protect_first_n: 3                                # Non-system head messages pinned across compactions (0 = pin nothing)
  in_place: true                                    # Compact on the same session id (no rotation) — see below
  idle_compact_after_seconds: 0                     # Opt-in idle compaction (0 = disabled) — see below
  hygiene_hard_message_limit: 5000                  # Gateway safety valve — see below
  hygiene_timeout_seconds: 30                       # Max seconds of NO summary-model output before hygiene compression is cut off
  hygiene_total_ceiling_seconds: 600                # Absolute cap on the hygiene wait even while tokens are still streaming
  hygiene_max_turn_hold_seconds: 10                 # Max wall-clock the incoming turn waits on hygiene compression before proceeding uncompressed — see below
  hygiene_failure_cooldown_seconds: 300             # First rung of the per-session hygiene-failure backoff (x1/x3/x9, capped at 1h)
  context_timeout_seconds: 120                      # Inactivity budget for in-agent compress_context (loop /compress / preflight) — see below
  context_total_ceiling_seconds: 600                # Absolute cap on the *pre-commit* in-agent compress_context wait even while tokens are still streaming (an already-started SessionDB commit is never abandoned; overruns are logged + surfaced)
  proactive_prune_tokens: 0                         # Opt-in tokens trigger for the no-LLM tool-result prune (0 = off; see below)
  proactive_prune_min_result_chars: 8000            # Prune's summarize pass only touches tool results larger than this (clamped >= 200)
  proactive_prune_min_reclaim_tokens: 4096          # Prune only commits when it reclaims at least this many tokens (0 = commit any)

# The summarization model/provider is configured under auxiliary:
auxiliary:
  compression:
    model: ""                                       # Empty = use main chat model. Override with e.g. "google/gemini-3-flash-preview" for cheaper/faster compression.
    provider: "auto"                                # Provider: "auto", "openrouter", "nous", "codex", "main", etc.
    base_url: null                                  # Custom OpenAI-compatible endpoint (overrides provider)
```

:::info 旧配置迁移说明  
对于包含 `compression.summary_model`、`compression.summary_provider` 和 `compression.summary_base_url` 字段的旧配置，在首次加载时（配置版本 17 及以上）会自动迁移为 `auxiliary.compression.*` 格式，无需手动操作。  

:::  
`progress_notices`（默认值为 `false`）用于控制是否在聊天平台（如 Telegram、Discord、Slack 等）上显示常规压缩进度状态。按照设计，自动压缩过程在聊天界面中不会产生任何提示——它仅在后台运行，并仅生成服务器端的日志记录。若将 `progress_notices` 设置为 `true`，即可在聊天平台上查看完整的压缩流程信息：包括“正在压缩上下文…”的启动提示、预处理/预 API 压缩触发信号、空闲状态下的压缩操作、重试进度提示（如“已压缩 30 → 12 条消息，正在重试…”）以及“上下文压缩完成”提示。该功能仅针对压缩状态生效——与压缩无关的其他操作信息（如辅助模型故障、服务提供商的速率限制或重试提示等）在任何情况下都不会显示。无论此设置如何，压缩**失败**提示以及手动执行的 `/compress` 操作反馈始终会显示。在正在运行的系统中修改此值，其效果将在处理下一条消息时体现。

`hygiene_hard_message_limit` 是一种仅适用于网关的**预压缩安全机制**。其存在旨在打破恶性循环：当会话规模过大导致 API 调用频繁中断时，网关将无法接收到令牌使用情况数据，因而基于令牌数量的阈值机制便无法触发，结果转录内容持续累积，连接中断问题也会愈发严重。该基于消息计数的阈值仅依据消息总数来判定（这一数值始终可知，不受 API 故障影响），以此强制启动压缩操作并恢复会话。默认值为 `5000`，远高于任何正常会话的需求，即便是那些需要处理数千条短轮次对话、且上下文长度达 100 万字符以上的大型模型，也早在达到该阈值之前就会因令牌限制而自动开始压缩。对于某些特殊平台，可适当提高该数值；若希望更积极地实施压缩，则可降低该值。在正在运行的网关上修改此值后，变更将于下一条消息开始时生效（详见下文）。

`hygiene_timeout_seconds` 则代表了网关在本次预压缩处理过程中的**无活动时间阈值**——并非一个固定的总时长上限。压缩摘要信息会以流式方式从模型端传输而来，每接收到一个令牌即视为一次进度推进：那些推理速度较慢但仍在持续生成内容的模型，会不断延长自身的处理截止时间，因此即便摘要生成速度缓慢但状态正常，也不会在生成过程中被强制中断。只有当摘要模型在指定时间内**完全不产生任何输出**（可能是后端故障、连接挂起或服务端无响应）时，网关才会向用户发出警告，继续接收未经过压缩的新消息，并将此次会话标记为临时故障状态，而非显示为卡住状态。

`hygiene_total_ceiling_seconds`（默认值为 `600`）用于限制总等待时间，即便在令牌仍在传输的过程中也会起到约束作用，从而防止流量极小的持续流无限期地占用处理轮次。该值至少会被限制在 `hygiene_timeout_seconds` 的水平。

`hygiene_max_turn_hold_seconds`（默认值为 `10`）则是网关的**轮次等待预算**——即进入的消息在等待卫生压缩处理时，网关允许其等待的最大时间长度，超过此时间后网关将停止等待并继续处理未压缩的转录内容。设置这一参数是因为仅依靠 `hygiene_total_ceiling_seconds`，可能会导致通信链路在远超聊天传输协议空闲超时的时间内保持沉默：由于持续生成摘要模型的令牌流会不断重置无活动状态计时，若没有轮次等待预算，等待时间可能会接近上限，而用户却收不到任何数据——此时 Telegram（及类似传输协议）会断开连接，导致该轮次看似被冻结。将轮次等待时间限制在此预算范围内（远低于通常约30秒的传输空闲超时），可确保消息能得到及时处理。**即使达到此预算上限，压缩处理也不会丢失**：工作进程会继续独立运行，且在其提交操作被水印机制保护时（使用会话数据库时的常规情况），其提交记录依然有效，因此完整的摘要会在下一个安全节点被采纳，而在等待被放弃后仍存在的轮次内容也会以原样作为并发尾部内容保留下来。对于**思考/推理总结模型**（如 DeepSeek、QwQ 等），这一点尤为重要——因为仅其推理阶段就可能耗尽预算限制，从而导致总结结果延迟生成一轮，而非完全无法生成。如果无法安全地设置预算限制，延迟生成的结果将会被丢弃（通过 `CompressionCommitFence` 机制），并且不能覆盖后续的回复。如果您希望在同一轮内完成压缩处理且您的传输系统能够承受等待时间，可提高预算限制；而对于响应速度极慢的后端，降低该限制则有助于更快恢复。

`hygiene_failure_cooldown_seconds` 用于控制每次卫生压缩超时或中断后，在单个会话内的冷却时间。在冷却期间，网关会跳过对同一超大会话的重复处理尝试，从而避免每条新消息都因同一个出问题的辅助后端而受阻。通过执行 `/compress`、`/reset` 操作或等待后续正常的回复，仍可恢复该会话。

该数值并非固定间隔，而是逐步递增机制中的**第一级阈值**：同一会话连续出现故障时，等待时间分别为该数值的 1 倍、3 倍，再到 9 倍，最终以一小时为上限。因此，当某个会话的总结模型永久损坏时，系统会停止按固定间隔无限重试，而是转为退避策略；而一旦有某次处理真正缩小了文本长度，系统又会将该数值重置为第一级。这种递增机制是针对单个会话及进程内部生效的——重启网关可将其重置为第一级，但冷却截止时间本身依然有效。

`context_timeout_seconds`（默认值为 `120`）与代理内的 `compress_context` 功能所使用的**空闲时间限制**相同——这一限制同样适用于对话循环、预处理压缩以及手动执行的 `/compress` 操作——从而避免因摘要模型卡住而导致会话无限期停滞。流式摘要生成会延长等待时间；只有处于静默状态的 Worker 才会被中断。超时后，Hermes 会针对 `auxiliary.compression.fallback_chain` 中的第一个条目重新尝试生成摘要（若该条目指定了自身超时时间，则会使用该时间值）——由于卡住的流程不会触发异常，因此辅助客户端自身的回退处理机制无法检测到这一问题。只有当此次尝试也失败，或未配置任何回退链时，Hermes 才会跳过压缩操作，保留现有消息，并向用户发出警告。将其设置为 `0` 即可禁用该功能。网关会话管理机制拥有独立的 `hygiene_timeout_seconds` 参数，不会被双重封装处理。

`context_total_ceiling_seconds`（默认值为 `600`）用于限制智能体在**预提交**阶段（即摘要生成/流式处理阶段）的等待时间，即便此时数据仍在传输中也是如此。该值至少会被限制在 `context_timeout_seconds` 的水平。具体保障机制为：**摘要生成阶段的时间会受到此上限约束；而若提交阶段耗时超过该上限，系统将会记录相关日志并予以显示。** 一旦工作进程进入压缩提交阶段且 SessionDB 的数据修改操作正在执行中，提交过程绝不会在半途中止——因为那样做可能会导致转录内容出现偏差——但此时系统不会再保持沉默：如果提交耗时超出上限，Hermes 会记录超时情况（首次为警告级别，多次发生则会升级为错误级别），并通过用户可见的警告渠道发送一次性提醒，随后以固定的时间间隔持续等待，直到提交完成。如果在摘要生成阶段该时间上限已到期，所有辅助通道（如 chat.completions、Codex Responses、Anthropic Messages）上的摘要生成流都会在瞬间被关闭——对于没有人在等待的连接，这种被中止的摘要生成不会产生任何费用，其会话租约也会被释放，以便后续再次尝试。

`protect_first_n` 用于控制每次压缩操作中会固定保留多少条**非系统**的对话开头消息。默认值为 `3`——即最初的用户与助手交流内容会在每次摘要生成过程中都被保留，从而确保原始目标始终可见。在那些持续时间较长的滚动压缩会话中，如果开头的对话内容已不再重要，可将 `protect_first_n` 设为 `0`，这样仅系统提示语、摘要以及对话结尾内容会被固定保留。无论此设置为何，系统提示语本身始终会被保留。

`in_place`（默认值为 `true`）用于控制压缩操作发生时会话标识的处理方式。当该值为 `true` 时，压缩操作会重写消息列表并重新生成系统提示语，但**不会更改会话标识**——整个对话在其生命周期内都将使用同一个稳定的标识（不存在 `parent_session_id` 链，也不会在会话列表中出现 `name #2`/`#3` 这类的重新编号）。这种压缩方式是非破坏性的：实时对话内容会被压缩，但压缩前的对话记录仍会以相同标识被软归档（标记为“已停用”或“已压缩”状态），依然可以通过 `session_search` 检索并恢复，而不会被删除。钩子函数可通过 `session:compress` 事件中的 `in_place` 字段获取该模式信息。若将 `in_place` 设为 `false`，则会恢复旧有的行为，即每次压缩后都会生成一个新的会话标识，并与旧标识保持关联。

`threshold_tokens`用于为压缩触发机制设置一个可选的**绝对token上限**。一旦启用，压缩操作将在这两个值中较小的那个达到时触发——即无论当前使用的是哪种模型，压缩都绝不会在超过用户设定的token数量时才执行。这一设计解决了因切换不同上下文窗口大小的模型（例如从100万token变为40万token）而导致触发阈值变动的问题。该上限会被限制在模型本身的上下文长度范围内，因此将其设置得高于模型支持的最大值也是安全的，系统会自动转而使用基于比例的阈值。默认值为`null`（已禁用，仅采用基于比例的阈值）。即便在模型切换或回退到备用模型时，此上限设置依然有效。

`idle_compact_after_seconds`则是一种**可选的、基于时间间隔的触发机制**，可作为基于大小的`threshold`的补充。默认值为`0`（已禁用）。当该值设置为大于0时，若会话在停止活动至少相应秒数后重新启动，系统会在首次回复之前先对累积的历史内容进行压缩处理。这样一来，那些长期运行的对话（例如数小时后才重新查看的Telegram聊天记录）就无需在后续每次回复时都重新读取全部过时的上下文信息。此外，当上下文长度已经达到或低于压缩目标值（`threshold × target_ratio`）时，该机制不会触发；同时它也遵循与其他自动压缩功能相同的故障冷却、防频繁触发以及会话级锁定保护机制。例如：若设置为`idle_compact_after_seconds: 1800`，则意味着在30分钟无活动后就会触发压缩。

`proactive_prune_tokens`功能可实现一种确定性的、无需依赖LLM的旧工具结果数据清理机制，且该操作独立于`threshold`参数运行。在支持大上下文窗口的模型中，由于`threshold`设定的压缩阈值（约等于窗口大小的50%）很少被触发，因此那些体积庞大的工具输出内容（如终端输出、文件读取结果、网页提取内容）会一直保留在历史记录中，并在后续的每一次对话轮次中被重复发送。当这些被重复发送的历史记录数量超过`proactive_prune_tokens`设定的阈值时（默认值为`0`，表示关闭该功能；可尝试设置为`48000`以启用），系统会自动对重复内容进行去重处理，对过大的旧结果进行摘要压缩，并截断过长的工具调用参数——同时会保留最新的`protect_last_n`条消息，且不会再次向模型发送数据。所有完整的输出内容仍可从会话存储中恢复。`proactive_prune_min_result_chars`参数（默认值为`8000`，最低限制为200字符）用于设定工具结果在低于此长度时将不会被清理。而`proactive_prune_min_reclaim_tokens`参数（默认值为`4096`）则确保只有在清理操作能回收至少这么多令牌时才会真正执行——因为一旦完成清理，就会重写已发送的历史记录，并使提供方的提示词缓存前缀失效，所以这一限制机制能让缓存失效的情况仅发生在特定的节点（如压缩边界处），而非每次工具调用时都会发生。该功能仅在内置的`compressor`引擎下生效；其他上下文引擎则只会执行无实际作用的操作。

:::提示：网关的压缩设置与上下文长度的热重载功能  
在最新版本中，无需重启网关、无需执行 `/reset` 操作，也无需切换会话，只需在正在运行的网关上修改 `config.yaml` 文件中的 `model.context_length` 或任何 `compression.*` 键值，更改即可在下一条消息处理时立即生效。由于缓存中的代理签名已包含这些键值，因此网关会在检测到变化时自动重新构建代理模型。而 API 密钥以及工具/技能相关配置仍需通过常规的重载方式来应用。  
:::

### 常见配置方案

**默认方案（自动检测）——无需任何配置：**
```yaml
compression:
  enabled: true
  threshold: 0.50
```
该功能会使用您指定的主提供商和主模型。如果您希望在成本较低的模型上实现压缩功能，而非使用主聊天模型，可针对特定任务进行覆盖设置（例如：`auxiliary.compression.provider: openrouter` + `model: google/gemini-2.5-flash`）。

**强制指定提供商**（基于 OAuth 或 API 密钥）：
```yaml
auxiliary:
  compression:
    provider: nous
    model: gemini-3-flash
```
可与任意提供商配合使用：`nous`、`openrouter`、`codex`、`anthropic`、`main` 等。

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
| `auto`（默认值） | 未设置 | 自动检测最优的可用服务提供商 |
| `nous` / `openrouter` 等 | 未设置 | 强制使用指定的服务提供商，并采用其认证方式 |
| 任意值 | 已设置 | 直接使用自定义端点（忽略服务提供商设置） |

:::warning 摘要模型上下文长度要求
摘要模型**必须**拥有至少与主智能体模型相当大的上下文窗口。压缩器会将对话的中间完整部分发送给摘要模型——如果该模型的上下文窗口小于主模型，摘要生成操作将会因上下文长度不足而失败。出现这种情况时，中间的对话内容会被直接丢弃而不会生成摘要，从而导致对话上下文在无声无息中丢失。如果您自行指定模型，请务必确认其上下文长度不低于主模型。
:::

## 网关轮次租约超时时间

网关会通过已确定的会话 ID 对各轮次进行序列化处理，因此两个路由键无法同时读取和写入相同的对话记录。请独立于常规的智能体无活动超时时间来配置最大租约等待时间：

```yaml
agent:
  gateway_turn_lease_timeout: 5
```

当该预算耗尽时，若仍有其他轮次持有会话租约，Hermes 将直接终止处理：它不会加载对话记录，也不会对等待中的消息运行模型。用户会收到拒绝通知，需重新发送消息。Hermes 不会自动重新将消息加入队列，因为在没有持久排序和幂等性保障的情况下这样做可能会导致消息被处理两次。非正数值将采用 5 秒的默认值。

## 会话停滞监视器

网关会运行一个仅用于通知的停滞监视器（参数为 `agent.session_stall_timeout`，默认值为 300 秒，值为 0 表示禁用）。当某个处于忙碌状态的会话存在**待处理的入站后续消息**，且该智能体的共享活动时钟已空闲至少此时长时，网关会记录一条警告信息，并向用户发送一次性通知：

```
⚠️ Agent session appears stalled (last activity N min ago). Try /new to reset.
```

语义说明：

- **仅发送通知。** 监控机制不会强制终止当前轮次——这与`agent.gateway_timeout`不同，后者会在长时间无响应后取消任务运行。停滞通知仅用于告知用户代理似乎出现了卡顿，由用户自行决定后续操作（如发送新指令、停止任务或继续等待）。
- **每次停滞事件仅触发一次通知。** 当待处理的请求处理完毕或代理恢复活动时，锁定状态即会被解除；因此，如果一个会话在恢复后又再次停滞，系统仍会再次发送通知。
- 进度信息仅通过共享的活动快照提供（如工具调用记录、API处理进度、压缩心跳信号）。待处理的请求仅用于触发通知，而非作为进度计时的依据。

```yaml
agent:
  session_stall_timeout: 300   # seconds; 0 disables the watchdog
```

## 关注度升级：重新连接处理机制

当平台适配器无法建立连接时（如网络中断、机器人令牌被撤销、Sidecar组件故障），网关会以指数退避策略无限次尝试重新连接——由于不会停止重试，因此临时性故障总能自动恢复，无需人工干预。但缺点是，*永久性*故障（如Telegram令牌被撤销、Discord缺少必要权限意图）也会表现为持续的“重试”状态，与临时故障无法区分。

有两种机制可用于识别永久性故障：

- **终端分类机制**：对于那些从异常类型上就能判断出无法自动恢复的故障——例如被拒绝或已撤销的令牌（`telegram_auth_error`、`discord_auth_error`、`email_auth_error`）、缺失的必要权限意图（`discord_intents_required`）、依赖项无法安装的Photon Sidecar组件（`SIDECAR_DEPS_MISSING`）或节点二进制文件缺失的情况（`SIDECAR_NODE_MISSING`）——系统会将其标记为致命故障，而非放入重试队列。该分类完全基于异常类型，对于含义模糊的错误则仍会持续尝试重试。
- **需要关注度升级机制**：如果某个平台在超过`agent.reconnect_attention_after`设定时间后（默认值为7200秒，即2小时；设为0则禁用此功能）仍持续处于重试队列中，网关会在运行状态信息（可通过`hermes status`命令查看）中标记该平台为“需要关注：true”，并记录下“开始重试的时间戳”，同时输出警告日志。此时重试行为不会改变——这只是一个提示信号，而非断路保护机制。一旦成功重新连接，该标记便会自动清除。

```yaml
agent:
  reconnect_attention_after: 7200   # seconds; 0 disables the escalation flag
```

## 网关代理缓存

网关会为每个对话会话保留一个代理实例，这样在对话进行过程中即可复用已缓存的提示前缀，而无需在每一轮对话中都重新生成系统提示。该缓存中的代理还会存储整个对话会话的完整记录——包括所有工具的输出内容；在包含上百次工具调用的会话中，这些数据的体积可达数十兆字节。因此，在繁忙的多平台网关系统中，缓存是占用内存最多的组件。

```yaml
agent:
  agent_cache:
    max_size: 128            # LRU entry cap
    idle_ttl_secs: 3600      # evict an agent idle this long
    memory_high_mb: auto     # anon-RSS budget; number, "auto", or 0/off
    max_evictions_per_pass: 16
    protect_recent: 8
```

`max_size`与`idle_ttl_secs`分别从数量和时间维度对缓存进行限制。由于这两种方式都无法掌握缓存中存储的字节数，因此`memory_high_mb`提供了第三种限制机制：一旦网关自身的匿名内存使用量超出设定阈值，它就会丢弃最近最少使用的转录内容，这些内容会在下次处理时从已存储的会话中重新加载。如果网关需要与其他服务共享内存，则应降低该值；而若希望保留所有转录内容，可提高该值（或将其设为`0`以关闭此功能）。

`auto`模式会根据网关实际运行的内存限制来确定阈值——对于容器而言是cgroup限制，对于systemd服务则是总RAM容量——因此无需再单独设置同步数值，系统便会自动遵循单元配置中的`MemoryMax`/`MemoryHigh`设置。

正在处理的会话、受`protect_recent`保护的最近期会话，以及转录内容尚未完全写入磁盘的会话，均不会被丢弃。发生内存淘汰时，系统会以WARNING级别记录相关日志，同时显示当前的实际内存使用量及被丢弃的会话信息。

```
Agent cache pressure: anon RSS 6802MB over budget 6656MB — evicting 5 LRU session(s): ...
```

## 上下文引擎

上下文引擎用于在对话接近模型token限制时，控制对话的管理方式。内置的 `compressor` 引擎采用有损摘要技术来实现这一功能（详见[上下文压缩](/developer-guide/context-compression-and-caching)）。插件引擎则可以选用其他策略来替代它。

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

## 迭代预算

当智能体处理需要多次工具调用的复杂任务时，其迭代预算（默认为 500 次轮次）可能会被耗尽。Hermes**不会**在任务进行过程中发出压力警告——早期版本会在预算使用达到 70%/90% 时向模型发出警告，但这会导致模型过早放弃复杂任务，该功能已于 2026 年 4 月被移除。

取而代之的是，当预算真正耗尽（500/500）时，Hermes 会发送一条消息要求模型完成当前任务，并允许其进行**一次补足调用**以输出最终响应。如果这次补足调用仍无法生成文本，系统会要求智能体总结其已完成的工作。

```yaml
agent:
  max_turns: none              # Iterations per conversation turn (default: none = unlimited)
                               # Set a positive integer to cap; "none"/"null"/
                               # "unlimited"/"inf"/"infinity"/"infinite"/0/-1 = no limit
  budget_warning_ratio: null   # Optional one-time checkpoint warning, e.g. 0.75
  api_max_retries: 3           # Retries per provider before fallback engages (default: 3)
```

默认情况下，`agent.max_turns` 的值是**无限制的**——设置轮次上限反而会引发更多问题（例如在任务执行过程中突然中断）。因此，Hermes 在启动时会一直持续对话，直到任务完成。若需设定上限，可输入一个正整数。若要明确表示“无限制”，可使用以下任意不区分大小写的写法：`"none"`、`"null"`、`"unlimited"`、`"infinite"`、`"infinity"`、`"inf"`、`0` 或 `-1`（这些值会对应 `sys.maxsize` 的特殊值，从而确保循环不会因达到轮次上限而终止）。

对于普通对话和委托对话，默认情况下 `agent.budget_warning_ratio` 是关闭状态。当该参数被设置为介于 `0` 和 `1` 之间的数值，并且同时指定了有限的 `max_turns` 值时，Hermes 会在达到阈值后，在最新的工具响应中添加一条模型可见的检查点提示。该提示会在每个对话轮次中重新触发，并消耗每个智能体自身的迭代预算。它只会添加到当前工具响应的末尾，而不会影响之前的轮次记录；同时也不会新增虚拟的用户/系统消息，也不会更改现有的超时处理机制。对于由调度器管理的看板工作节点，默认情况下在资源使用率达到 90% 时会收到完成检查点提示（可通过指定具体比例来调整该阈值），且此时相关工具仍可继续使用。该检查点要求提供已验证的完成状态或详细的进度说明，而非提前宣布任务成功。

`agent.api_max_retries` 用于控制 Hermes 在触发备用提供者切换之前，针对临时性错误（如速率限制、连接中断、5xx 错误）会重试调用提供者 API 多次。默认值为 `3`，即总共进行 4 次尝试。如果您已配置了[备用提供者](/user-guide/features/fallback-providers)并希望更快地实现故障转移，可将该值设为 `0`，这样主提供者遇到首次临时错误时就会立即切换到备用提供者，而无需继续向那个不稳定的接口发送重试请求。

## 实时运行时间预算

除了迭代预算之外，您还可以为每次对话运行设置可选的**实时运行时间预算**。该功能专为那些受到严格外部时间限制的一次性任务或评估任务设计（例如每项任务最多 900 秒）：如果不设置此预算，即使任务已基本完成，运行仍可能因超时而中断——要么无法生成最终答案，要么陷入某个挂起的提供者调用中无法退出。

```yaml
agent:
  run_budget_seconds: null     # Optional; unset/null = feature fully off (default)
```

或者通过 CLI 按每次调用来执行：

```bash
hermes chat --run-budget 850 -q "..."
```

当预算被设定后，将会发生以下两件事：

1. **达到80%时的结束提示。** 当预算使用量达到80%时，Hermes会发送一条**一次性**的提示信息（以缓存安全的方式传递，并附加在最新的工具响应结果中，类似 `/steer` 消息），告知模型停止新的探索或验证工作，基于当前已有的状态生成最终成果。该提示在每次运行过程中最多触发一次，其机制与现有的迭代预算结束逻辑一致——不会反复发出警告。

2. **按截止时间缩放的过期超时机制。** 那些默认为数分钟级的隐式非流式过期超时设置（以及推理模型的最低限制，例如DeepSeek推理模型为600秒），其上限会被设定为 `max(60, remaining_budget × 0.5)`。这样一来，单个长时间挂起的提供者调用就绝不会占用掉整个运行过程的剩余时间。该上限只会让超时时间变得更短，而不会延长；同时，明确配置的 `stale_timeout_seconds` 值（来自提供者或模型配置，或通过 `HERMES_API_CALL_STALE_TIMEOUT` 参数设置）始终会优先生效，不受影响。

预算是按每次“对话轮次”来计算的（每收到一条用户消息就会重置），而如果未设置该功能，则完全处于休眠状态——不会进行任何时间读取、不会发送任何提示，也不会调整超时时间。

## 停止时验证（代码验证）

一旦该功能被启用，当智能体在工作区中修改了代码，但却未能提供任何新的验证结果（如测试通过、构建成功、代码检查无错误等）时，Hermes 将拒绝接受其给出的最终答案。系统会自动插入一个虚拟的后续问题，要求智能体进行验证或解释为何无法完成验证。仅涉及文档、Markdown 内容或技能相关修改的情况不会触发此机制，且该循环设有上限，因此绝不会让智能体陷入无限循环之中。

```yaml
agent:
  verify_on_stop: false        # true | false | "auto" (surface-aware: on for CLI/TUI/desktop, off for messaging)
  verify_guidance: true        # Append creative-UI / clean-diff guidance to the missing-evidence nudge
  max_verify_nudges: 3         # Cap on consecutive continue nudges per turn (built-in + pre_verify hooks)
  coding_instructions: ""      # Standing project-wide coding rules appended to the coding brief
```

`verify_on_stop` 参数支持 `true`（始终启用）、`false`（关闭——默认值）或 `"auto"`（旧版的表面感知模式：对于交互式编码界面，如 CLI、TUI、桌面端以及通过编程方式调用的场景则保持启用；而对于 Telegram/Discord 等消息类平台，则会关闭该功能，因为在此类场景下进行验证信息提示会被视为聊天干扰）。默认情况下在所有场景下均为关闭状态：新安装的版本初始值为 `false`，而配置迁移也使得现有版本的该功能处于关闭状态，因此只有用户明确选择才会在其上启用该功能。若设置了 `HERMES_VERIFY_ON_STOP` 环境变量，其值将优先于配置文件中的设置。

用于触发此保护机制的相关证据——包括执行了哪些测试、lint 或构建命令，以及自上次之后修改了哪些文件——均存储在 `~/.hermes/verification_evidence.db` 文件中。该日志文件仅在保护机制处于启用状态时才会被创建或写入内容；当 `verify_on_stop` 设置为 `false` 时，不会记录任何信息，现有的文件也可以被随时删除。

若需在同一位置实现基于用户/插件策略的自定义检查以保持智能体持续运行，请参阅 [`pre_verify` 钩子](/user-guide/features/hooks#pre_verify)。

## 持续目标（`/goal`）

当某个持续目标处于激活状态时，Hermes 会逐一判断每个助手回复是否满足该目标。若不满足，则会将继续处理的提示语反馈至同一会话中，并持续工作，直到目标完成、对话轮次预算耗尽，或是用户暂停/清除该目标为止。实际上，对话轮次预算才是真正的保障机制——对于判定失败的案例，系统会选择“继续处理”而非终止当前流程，从而避免因某个不可靠的判定机制而阻碍整体进度。

```yaml
goals:
  max_turns: 20   # Max continuation turns before Hermes auto-pauses the goal (default: 20)
```

`max_turns` 参数用于限制目标在触发 Hermes 自动暂停并要求用户执行 `/goal resume` 前可进行的续传轮数。该设置旨在避免判定错误（即目标实际上已完成，但系统仍指示继续处理），同时防止模型在处理模糊或无法实现的目标时无限制地消耗资源。如需了解该功能的详细信息，请参阅 [目标管理](/user-guide/features/goals)。

### API 超时设置

Hermes 为流式请求提供了独立的超时机制，同时针对非流式请求设计了过期检测功能。仅当您将相关参数设置为默认值时，本地提供程序的过期检测功能才会自动生效并进行调整。

| 超时类型 | 默认值 | 本地提供程序 | 配置/环境变量 |
|---------|--------|----------------|--------------|
| 套接字读取超时 | 120秒 | 自动提升至1800秒 | `HERMES_STREAM_READ_TIMEOUT` |
| 流式数据过期检测 | 180秒 | 上限提升至900秒（`agent.local_stream_stale_timeout`） | `HERMES_STREAM_STALE_TIMEOUT` |
| 非流式数据过期检测 | 90秒 | 若保持默认值则自动禁用 | `providers.<id>.stale_timeout_seconds` 或 `HERMES_API_CALL_STALE_TIMEOUT` |
| API调用（非流式） | 1800秒 | 不变 | `providers.<id>.request_timeout_seconds` / `timeout_seconds` 或 `HERMES_API_TIMEOUT` |
**套接字读取超时时间**用于控制httpx等待来自服务提供商的下一批数据的时长。对于本地大型模型，其在预加载大量上下文后才能生成第一个token，这一过程可能需要数分钟，因此Hermes在检测到本地端点时会将此超时时间延长至30分钟。无论是否检测到端点类型，只要您显式设置了`HERMES_STREAM_READ_TIMEOUT`，系统将始终使用该值。

**过期流检测**功能会主动断开那些仅收到SSE保持连接信号却未接收到实际内容的连接。对于在预加载阶段不会发送保持连接信号的本地服务提供商，系统的默认超时时间将从180秒提升至900秒——您可以通过`agent.local_stream_stale_timeout`或环境变量`HERMES_LOCAL_STREAM_STALE_TIMEOUT`来调整这一数值。

**过期非流式请求检测**则用于终止那些长时间无响应的非流式调用。为避免在长时间预加载过程中出现误判，Hermes默认会在本地端点上关闭此功能。不过，如果您显式设置了`providers.<id>.stale_timeout_seconds`、`providers.<id>.models.<model>.stale_timeout_seconds`或`HERMES_API_CALL_STALE_TIMEOUT`，那么即便在本地端点上，系统也会优先使用您设定的超时时间。

上述各项超时限制共同构成了对所有非流式请求的管控机制。对于那些接收了请求却毫无响应的服务提供商——即连接保持开启状态，既无数据传输也无错误提示——系统会在达到对应过期超时时间后自动终止该连接并重新发起请求，而不会一直等待较长的套接字读取超时时间（或者，在无人监控的定时任务中，直到外部因素强制终止进程）。

只有在至少**60秒的静默状态**之后，才会出现周期性的提供者等待提示。Codex响应中的**等待状态**指的是静默时长，而非完整的生成时间——活跃的流事件（包括推理过程）会维持该状态的“静默”表现。一旦这些事件停止，系统会记录无流事件的时间，而不会判定没有收到任何响应；一旦事件恢复，该提示便会消失。当重新连接启动一个新的首个事件监视阶段时，等待状态也会随之变化。这种显示机制不会影响独立的实时时钟超时设置，也不会改变监视器的超时时间。同样地，聊天完成流在数据块恢复传输后也会立即消除静默警告，但不会替代本地的模型加载状态显示。

Cron作业和委托的子代理也会进行流式处理。它们会在自己的线程中直接处理请求（其他会话通过网关嵌套线程池中的中断工作线程来执行相关操作），但由于请求的`stream: true`属性，上述**陈旧流检测**规则依然适用于它们——每个令牌都会计入活跃度统计，因此即便推理模型需要数分钟才能完成计算，也不会被误认为是提供者卡住了，而那些会主动断开静默连接的边缘代理则仍能持续接收到数据字节。

### 禁用API流式传输

`model.streaming: false` 会强制整个会话中的所有请求——包括父代理和子代理——都采用非流式处理方式。对于那些自托管的、兼容 OpenAI 的服务器而言，这是解决 *流式* 工具调用路径出现故障时的应急方案（例如，使用 `--tool-call-parser qwen3_xml` 并搭配推理解析器的 vLLM 可能会将工具调用相关的标记泄露为纯文本，从而导致返回的 `tool_calls` 数量为零，进而使委派的任务无法正常执行）。其默认值为 `true`；除非遇到了此类故障，否则建议保持该默认设置，因为非流式调用会失去上述提到的实时性特性。需要注意的是，此参数与 `display.streaming` 是相互独立的，后者仅用于控制终端中的令牌显示方式。

```yaml
model:
  streaming: false
```

## 上下文压力警告

除了迭代预算压力之外，上下文压力还会监测对话距离**压缩阈值**的接近程度——即触发上下文压缩以总结旧消息的临界点。这有助于您和智能体及时了解对话何时变得过长。

| 进度 | 等级 | 后果 |
|----------|------|------|
| 距离阈值 **≥ 60%** | 信息提示 | CLI界面会显示青色进度条；网关会发送信息通知 |
| 距离阈值 **≥ 85%** | 警告 | CLI界面会显示加粗的黄色进度条；网关会警告即将进行上下文压缩 |

在CLI中，上下文压力会以进度条的形式显示在工具输出流中：

```
  ◐ context ████████████░░░░░░░░ 62% to compaction  48k threshold (50%) · approaching compaction
```

在消息平台中，系统会发送一条纯文本通知：

```
◐ Context: ████████████░░░░░░░░ 62% to compaction (threshold: 50% of window).
```

如果禁用了自动压缩功能，系统会发出警告，提示上下文内容可能会被截断。

上下文压力检测是自动进行的——无需任何配置。它仅作为面向用户的通知而触发，不会修改消息流，也不会向模型的上下文中注入任何内容。

## 凭证池策略

当您为同一提供方拥有多个 API 密钥或 OAuth 令牌时，可配置相应的轮换策略：

```yaml
credential_pool_strategies:
  openrouter: round_robin    # cycle through keys evenly
  anthropic: least_used      # always pick the least-used key
```

选项包括：`fill_first`（默认值）、`round_robin`、`least_used`、`random`。详细文档请参阅[凭证池](/user-guide/features/credential-pools)。

## 提示词缓存

当当前使用的提供方支持跨会话提示词缓存时，Hermes会自动启用该功能——无需用户进行任何配置。

对于运行在**原生Anthropic平台**、**OpenRouter**以及**Nous Portal**上的Claude，Hermes会在系统提示词及技能模块中添加`cache_control`缓存控制指令，设置1小时的过期时间（`ttl: "1h"`）。在当前小时内的首次发送将按正常费率计费；而在同一小时内不同会话间的后续发送则可从缓存中读取，享受较低的缓存读取费率。这意味着系统提示词、加载的技能内容以及长上下文对话的前半部分，在初始1小时内可在多个`hermes`会话之间，甚至在不同子代理之间重复使用。

Qwen Cloud（阿里达斯阔）上游平台的缓存过期时间被限制为5分钟，因此Hermes在该平台也会采用5分钟的缓存过期时间。其他通过第三方实现的Claude版本（如AWS Bedrock、Azure Foundry）则遵循相应提供方的默认缓存设置。xAI Grok则采用独立的会话绑定对话ID机制——详情请参见[xAI提示词缓存](/integrations/providers#xai-grok--responses-api--prompt-caching)。

目前不存在关闭此功能的选项——缓存功能始终处于开启状态，即便在单轮对话中也能节省成本，因为仅系统提示词所占的输入Token数量就已相当可观。

在基于 Anthropic 风格的断点设置中，Hermes 所请求的唯一一个明确可调整的参数，便是缓存 TTL 等级。

```yaml
prompt_caching:
  cache_ttl: "5m"   # "5m" or "1h" (Anthropic-supported tiers); other values are ignored
```

`cache_ttl` 用于指定 Hermes 通过原生 Anthropic API、OpenRouter 以及 Nous Portal 为 Claude 设置的断点缓存时间。仅支持 Anthropic 所认可的两种时间值（`"5m"` 和 `"1h"`），其他任何数值都将被忽略。那些有自身时间限制的服务提供商（例如最大缓存时间为 5 分钟的 Qwen Cloud）仍需遵循上游服务允许的时间设置。

## 辅助模型

Hermes 会使用“辅助”模型来处理诸如图像分析、浏览器截图分析、会话标题生成以及上下文压缩等辅助任务。默认情况下（`auxiliary.*.provider: "auto"`），Hermes 会将所有辅助任务转发给您的**主聊天模型**——即您在 `hermes model` 中选择的同一服务提供商/模型。起步时无需进行任何配置，但请注意，在那些计算成本较高的推理模型（如 Opus、MiniMax M2.7 等）上，执行辅助任务会显著增加费用。如果您希望无论使用何种主模型，都能以低成本快速完成辅助任务，可以明确指定 `auxiliary.<task>.provider` 和 `auxiliary.<task>.model` 的值（例如，可在 OpenRouter 上使用 Gemini Flash 处理图像相关任务）。（网页内容提取不属于辅助任务：`web_extract` 功能以及浏览器快照会以确定性的方式截取长文本内容，并将完整文本保留下来以便通过 `read_file` 功能分页查看——此过程不涉及大型语言模型。）

:::note 为何“auto”模式会使用主模型
在早期版本中，聚合器用户（OpenRouter、Nous Portal）会被分配到成本较低的默认提供方。这一做法令人费解——那些购买了聚合器订阅的用户，其辅助流量却由不同的模型处理。现在，“auto”模式会对所有用户统一使用主模型，不过仍可通过`config.yaml`中的任务级配置进行覆盖（详见下方的[完整辅助配置参考](#full-auxiliary-config-reference)）。
:::

### 交互式配置辅助模型
无需手动编辑YAML文件，只需运行`hermes model`，然后从菜单中选择**“配置辅助模型”**。系统会提供一个交互式的任务级选择界面：

```
$ hermes model
→ Configure auxiliary models

[ ] vision               currently: auto / main model
[ ] title_generation     currently: openrouter / google/gemini-3-flash-preview
[ ] tts_audio_tags       currently: auto / main model
[ ] compression          currently: auto / main model
[ ] approval             currently: auto / main model
[ ] triage_specifier     currently: auto / main model
[ ] kanban_decomposer    currently: auto / main model
[ ] profile_describer    currently: auto / main model
[ ] delegation           currently: auto / inherit main agent
```

选择任务后，接着挑选提供方（OAuth流程会自动打开浏览器；使用API密钥的提供方则会弹出提示），最后选定模型。这些设置将会保存到`config.yaml`文件中的`auxiliary.<task>.*`路径下。其操作方式与选择主模型的流程相同——无需学习额外的语法。

**Delegation**选项较为特殊：它用于指定`delegate_task`子代理所使用的模型，并将相关设置保存在顶层的`delegation.*`部分（即`delegation.provider`/`delegation.model`），而非`auxiliary.*`目录下。这是因为子代理属于独立的完整代理，而非简单的侧边LLM调用。其`auto`选项的含义为“继承父代理的提供方、模型及认证信息”。

如果您不希望Hermes在首次交互后自动生成标题，可设置`auxiliary.title_generation.enabled: false`。不过仍可通过`/title`命令或“hermes sessions rename”功能手动设置标题。

### 仅支持流式处理的端点

某些兼容OpenAI的端点会直接拒绝非流式聊天请求（例如Tencent Copilot会返回HTTP 400错误信息“当前不支持非流式聊天请求”）。虽然交互式聊天本身是流式处理，但辅助任务（如标题生成、压缩、图像处理等）使用的是非流式调用，因此每次尝试都会失败。Hermes始终将`copilot.tencent.com`视为仅支持流式处理的端点；对于其他类似的端点，则需在`auxiliary.stream_only_base_urls`下列出对应的URL子串：

```yaml
auxiliary:
  stream_only_base_urls:
    - "my-stream-only-proxy.example.com"
```

匹配到的辅助调用会通过 `stream=True` 的方式发送，且各数据块（包括工具调用差异信息）都将在客户端进行聚合处理——其他端点的相关行为保持不变。

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

Hermes 中的每一个模型槽位——无论是辅助任务、压缩处理还是备用方案——都使用相同的三个配置参数：

| 键值 | 功能说明 | 默认值 |
|-----|-------------|---------|
| `provider` | 用于身份验证和请求路由的提供方 | `"auto"` |
| `model` | 需要调用的模型 | 对应提供方的默认模型 |
| `base_url` | 自定义的兼容 OpenAI 的接口地址（可覆盖提供方设置） | 未设置 |

辅助任务模块还会额外包含一个 `reasoning_effort` 参数：

| 键值 | 功能说明 | 默认值 |
|-----|-------------|---------|
| `reasoning_effort` | 控制该任务对应的 LLM 调用思维强度：`none`、`minimal`、`low`、`medium`、`high`、`xhigh`、`max`、`ultra` | 未设置（采用提供方的默认值） |
该参数是全局 `agent.reasoning_effort` 的任务级对应设置：当您的主模型为计算成本较高的推理模型时，可通过将压缩级别设置为 `low` 或视觉处理功能设置为 `none`，从而降低辅助任务的延迟与成本，同时不会影响原有的对话行为。它适用于所有三种辅助消息格式（对话补全、Codex响应、Anthropic消息）中的各类辅助客户端任务，如 `vision`、`compression`、`title_generation` 和 `curator`。若同一任务中存在显式的 `extra_body.reasoning` 设置，则该设置将优先于上述简写形式。

**背景审查则有所不同**：基于同一模型的审查分支始终会继承父分支的推理设置。在这种情况下，`auxiliary.background_review.reasoning_effort` 会被忽略，即便明确选择了父节点的提供者或模型也不例外。这样的设计旨在保持推理参数、系统提示词、完整对话记录以及工具定义的完全一致，从而确保提示缓存的一致性；对于同一模型的审查任务，并不存在独立的推理强度切换选项。详情请参阅 [背景审查推理功能](/user-guide/features/memory#same-model-review-reasoning)。关于独立路由分支的推理设置问题，当前正在追踪处理，相关议题编号为 [#94825](https://github.com/NousResearch/hermes-agent/issues/94825)。

**MoA 采用不同的配置方式：**在 MoA 预设中，混合智能体架构的推理深度是针对每个任务槽单独配置的（位于 `moa.presets.<name>.reference_models[].reasoning_effort` / `aggregator.reasoning_effort` 参数中），而非在 `moa_reference`/`moa_aggregator` 辅助模块中进行设置——详情请参阅[混合智能体架构](/user-guide/features/mixture-of-agents)。

```yaml
auxiliary:
  compression:
    reasoning_effort: "low"    # summaries don't need deep thinking
  vision:
    reasoning_effort: "none"   # disable thinking for image description
```

当设置了 `base_url` 时，Hermes 会忽略指定的 provider，直接调用该端点（并通过 `api_key` 或 `OPENAI_API_KEY` 进行身份验证）。如果仅设置了 `provider`，Hermes 则会使用该 provider 内置的身份验证机制及基础 URL。

可用于辅助任务的 provider 包括：`auto`、`main`，以及 [provider registry](/reference/environment-variables) 中列出的所有 provider——如 `openrouter`、`nous`、`openai-codex`、`copilot`、`copilot-acp`、`anthropic`、`gemini`、`qwen-oauth`、`zai`、`kimi-coding`、`kimi-coding-cn`、`minimax`、`minimax-cn`、`minimax-oauth`、`deepseek`、`nvidia`、`xai`、`xai-oauth`、`ollama-cloud`、`alibaba`、`bedrock`、`huggingface`、`arcee`、`xiaomi`、`kilocode`、`opencode-zen`、`opencode-go`、`opencode-free`、`commandcode`、`commandcode-anthropic`、`ai-gateway`、`azure-foundry`——此外还包括您在 `providers:` 字典中自定义命名的任何 provider（例如 `provider: "beans"`）。

:::提示 MiniMax OAuth
`minimax-oauth` 通过浏览器 OAuth 方式登录（无需 API 密钥）。运行 `hermes model` 后选择 **MiniMax (OAuth)** 即可完成身份验证。辅助任务会自动使用 `MiniMax-M2.7-highspeed`。详情请参阅 [MiniMax OAuth 指南](../guides/minimax-oauth.md)。
:::

:::提示 xAI Grok OAuth认证方式  
对于SuperGrok及X Premium+订阅用户，可使用浏览器OAuth方式进行登录（无需API密钥）。运行`hermes model`命令后，选择**xAI Grok OAuth (SuperGrok / Premium+)**即可完成身份验证。该相同的OAuth令牌会被用于所有直接与xAI交互的功能，包括聊天、辅助任务、文本转语音、图像生成、视频生成以及语音转文字等功能。详情请参阅[xAI Grok OAuth指南](../guides/xai-grok-oauth.md)；若Hermes运行在远程主机上，则请参考[通过SSH/远程主机进行OAuth认证](../guides/oauth-over-ssh.md)。  
:::

:::警告 `"main"`仅适用于辅助任务  
`"main"`这一提供者选项的含义是“使用我的主智能体所使用的提供者”——它仅能在`auxiliary:`、`compression:`以及主要的备用配置项（`fallback_providers:`或旧版的`fallback_model:`）中使用。它**不**可作为顶层`model.provider`设置的有效值。如果您使用的是自定义的兼容OpenAI的接口端点，请在`model:`部分将`provider`设置为`custom`。所有主要的模型提供者选项详见[AI提供者指南](/integrations/providers)。  
:::

### 完整的辅助配置参考文档

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
    max_concurrency: 8         # max concurrent image encode/resize bursts across the process
                               # (default: host CPU core count, no ceiling) — bounds only the
                               # CPU-bound encode step so a video-frame fan-out can't saturate
                               # every core and starve the event loop; LLM calls stay fully
                               # concurrent. Minimum 1; values < 1 are ignored.

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
    # fallback_chain:           # Optional — providers to try on rate-limit / connectivity failure
    #   - provider: nous
    #     model: deepseek/deepseek-chat
    #   - provider: openrouter
    #     model: google/gemini-2.5-flash
    #     base_url: ""
    #     api_key: ""
    # max_concurrency: 2       # Optional: cap simultaneous compression LLM calls so
                               # multiple sessions don't pile retries on a degraded provider

  # Auto-generated session titles. Empty language follows the conversation;
  # set e.g. "English" or "Japanese" to pin titles to one language.
  title_generation:
    enabled: true              # set false to disable auto-title generation
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

  # Auto-generated short session titles after the first exchange
  title_generation:
    provider: "auto"
    model: ""
    base_url: ""
    api_key: ""
    timeout: 30
    # max_concurrency: 2       # Optional: cap simultaneous title-generation calls

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
每个辅助任务都配有可配置的`timeout`参数（以秒为单位）。默认值为：视觉处理任务120秒，审批任务30秒，压缩任务120秒。如果使用的本地模型处理速度较慢，建议适当增加这些时间值。此外，视觉处理任务还包含一个独立的`download_timeout`参数（默认30秒），用于控制HTTP图像下载的时间；在网络连接缓慢或使用自托管图像服务器时，也应提高该数值。
:::

:::info
上下文压缩功能拥有专用的`compression:`块用于设置阈值，同时还设有`auxiliary.compression:`块用于配置模型及提供方的相关参数——详情请参阅上文中的[上下文压缩](#context-compression)部分。主备用链则通过顶级的`fallback_providers:`列表来实现切换——相关内容可查看[备用提供方](/integrations/providers#fallback-providers)。这三种机制均遵循相同的提供方/模型/base_url格式。
:::

### 辅助任务的逐任务备用链配置

每个辅助任务均可选择性地定义`fallback_chain`——即一个提供方/模型条目列表，当主备用提供方因速率限制、连接问题或支付限制而无法正常工作时，Hermes会依次尝试这些备选方案：

```yaml
auxiliary:
  compression:
    provider: openrouter
    model: openai/gpt-4o-mini
    fallback_chain:
      - provider: nous
        model: deepseek/deepseek-chat
      - provider: openrouter
        model: google/gemini-2.5-flash
```

当主辅助提供者（如 `openrouter` / `openai/gpt-4o-mini`）返回速率限制、连接超时或需要付费的错误时，Hermes 会按顺序遍历 `fallback_chain` 列表。它会跳过那些提供者与已出错的提供者相同的条目，依次尝试剩余的条目，直到有某个条目成功运行或整个列表被遍历完毕。如果所有备用方案都失败，Hermes 会最终回退到主智能体模型作为最后的安全保障。

每个条目都支持与任何辅助任务配置相同的三个参数：

| 键值 | 描述 |
|-----|-------------|
| `provider` | 提供者名称（如 `nous`、`openrouter`、`anthropic`、`gemini`、`main` 等） |
| `model` | 对应提供者的模型名称 |
| `base_url` | （可选）自定义的兼容 OpenAI 的接口地址 |

`fallback_chain` 功能适用于所有类型的辅助任务——包括 `compression`、`vision`、`approval`、`skills_hub`、`mcp` 等。

### 限制辅助任务的并发数

`max_concurrency` 参数用于限制整个流程中类似 `compression` 和 `title_generation` 这类辅助任务的正在处理的 LLM 调用数量。不过 `auxiliary.vision.max_concurrency` 不受此限制，因为它仅控制视觉处理相关的 CPU 密集型图像编码/缩放任务，而不涉及 LLM 请求。在以下情况下该参数尤为有用：

- 多个会话可同时启动后台任务（如 Discord/Telegram 频道、多个终端）
- 某些提供者存在速率限制或正在出现故障，而重复尝试只会加剧请求量激增

默认值为无限制。通常建议将安全上限设置为 `2`：

```yaml
auxiliary:
  title_generation:
    max_concurrency: 2
  compression:
    max_concurrency: 2
```

该信号量会封装整个调用过程，包括重试和回退机制，因此单次耗时的调用仅会计入一次限制次数。

### 用于辅助任务的 OpenRouter 路由与 Pareto Code

当某个辅助任务被确定为使用 OpenRouter（无论是明确指定，还是在主代理已基于 OpenRouter 运行时通过 `provider: "main"` 指定），则主代理的 `provider_routing` 以及 `openrouter.min_coding_score` 设置**不会被传递**——这是出于设计考虑，因为每个辅助任务都是独立的。若要为特定辅助任务设置 OpenRouter 提供商偏好，或使用 [Pareto Code 路由器](/integrations/providers#openrouter-pareto-code-router)，可通过 `extra_body` 按任务单独进行配置：

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

其格式与 OpenRouter 在聊天补全请求体中接受的格式一致。Hermes 会原封不动地转发整个 `extra_body`，因此 [openrouter.ai/docs](https://openrouter.ai/docs) 中文档记载的 OpenRouter 请求体中的其他字段也同样适用。

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

这些选项适用于**辅助任务配置**（`auxiliary:`、`compression:`）以及主要的备用提供商设置（`fallback_providers:` 或旧版的 `fallback_model:`），并不作用于主要的 `model.provider` 设置。

| 提供商 | 描述 | 要求 |
|----------|-------------|------|
| `"auto"` | 选择最佳可用选项（默认值）。系统会依次尝试 OpenRouter、Nous 和 Codex。 | — |
| `"openrouter"` | 强制使用 OpenRouter——可连接任何模型（如 Gemini、GPT-4o、Claude 等）。 | `OPENROUTER_API_KEY` |
| `"nous"` | 强制使用 Nous Portal。 | `hermes auth` |
| `"codex"` | 强制使用 Codex OAuth（需 ChatGPT 账户）。支持视觉处理功能（如 gpt-5.3-codex）。 | 需已配置 `hermes model` → ChatGPT 或 Codex 订阅账号 |
| `"minimax-oauth"` | 强制使用 MiniMax OAuth（通过浏览器登录，无需 API 密钥）。辅助任务会使用 MiniMax-M2.7-highspeed 模型。 | 需已配置 `hermes model` → MiniMax（OAuth） |
| `"xai-oauth"` | 强制使用 xAI Grok OAuth（SuperGrok 或 X Premium+ 订阅用户可通过浏览器登录，无需 API 密钥）。同一 OAuth 令牌可用于聊天、文本转语音、图像处理、视频处理及转录功能。 | 需已配置 `hermes model` → xAI Grok OAuth（SuperGrok / Premium+） |
| `"main"` | 使用您当前启用的自定义/主要接口地址。该地址可来自 `OPENAI_BASE_URL` + `OPENAI_API_KEY`，也可来自通过 `hermes model` / `config.yaml` 保存的自定义接口。适用于 OpenAI、本地模型或任何兼容 OpenAI 的 API。**仅适用于辅助任务——不适用于 `model.provider` 设置。** | 需提供自定义接口的凭证及基础地址 |
当您希望让辅助任务绕过默认的路由器时，主提供商目录中的直接 API 密钥提供商在这里也同样适用。例如，一旦配置了 `GMI_API_KEY`，`gmi` 即可正常使用；而配置了 `FIREWORKS_API_KEY` 后，`fireworks` 也能正常运行。

```yaml
auxiliary:
  compression:
    provider: "gmi"
    model: "anthropic/claude-opus-4.6"
```

对于 GMI 辅助路由功能，需使用 GMI 的 `/v1/models` 接口返回的精确模型编号。而 Fireworks 模型的编号则采用对应提供方的标准斜杠格式，例如 `accounts/fireworks/models/glm-5p2`。

### 常见配置方式

**直接使用自定义接口**（相较于 `provider: "main"`，这种方式在本地或自托管 API 场景下更为清晰）：
```yaml
auxiliary:
  vision:
    base_url: "http://localhost:1234/v1"
    api_key: "local-key"
    model: "qwen2.5-vl"
```

`base_url` 的优先级高于 `provider`，因此这是将辅助任务路由到特定端点最明确的方式。对于直接的端点覆盖，Hermes 会使用已配置的 `api_key`，若未配置则会回退至 `OPENAI_API_KEY`；它不会将该自定义端点与 `OPENROUTER_API_KEY` 绑定使用。

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
运行 `hermes model` 命令，选择 **MiniMax (OAuth)** 方式登录即可自动完成设置。针对中国地区，基础 URL 为 `https://api.minimaxi.com/anthropic`。如需完整的操作指南，请参阅 [MiniMax OAuth 使用指南](../guides/minimax-oauth.md)。

**使用本地/自托管模型：**
```yaml
auxiliary:
  vision:
    provider: "main"      # uses your active custom endpoint
    model: "my-local-model"
```

`provider: "main"` 会使用 Hermes 在常规聊天中使用的相同提供方——无论是自定义的命名提供方（如 `beans`）、内置提供方如 `openrouter`，还是传统的 `OPENAI_BASE_URL` 接口。

:::提示
如果您将 Codex OAuth 作为主要模型提供方，视觉功能将自动启用——无需额外配置。Codex 已被纳入视觉功能的自动检测流程中。
:::

:::警告
**视觉功能需要多模态模型。** 如果您设置了 `provider: "main"`，请确保您的接口支持多模态/视觉功能——否则图像分析将会失败。
:::

### 环境变量（旧版）

辅助模型也可以通过环境变量进行配置。不过，`config.yaml` 是更推荐的方式——它更易于管理，且支持包括 `base_url` 和 `api_key` 在内的所有选项。

| 设置项 | 环境变量 |
|---------|---------------------|
| 视觉功能提供方 | `AUXILIARY_VISION_PROVIDER` |
| 视觉功能模型 | `AUXILIARY_VISION_MODEL` |
| 视觉功能接口地址 | `AUXILIARY_VISION_BASE_URL` |
| 视觉功能 API 密钥 | `AUXILIARY_VISION_API_KEY` |

压缩及备用模型相关设置仅能在 `config.yaml` 中配置。（`AUXILIARY_WEB_EXTRACT_*` 变量已过时——网页提取功能不再使用辅助大型语言模型。）

:::提示
运行 `hermes config` 即可查看当前的辅助模型设置。只有当配置值与默认值不同时，才会显示这些自定义设置。
:::

## 推理耗力控制

可调节模型在回复前进行“思考”的程度：

```yaml
agent:
  reasoning_effort: ""   # empty = medium. Options: none, minimal, low, medium, high, xhigh, max, ultra
```

当该参数未被设置（即保持默认值）时，推理强度默认为“中等”——这一平衡值适用于大多数任务。若手动设置数值，则会覆盖默认值：更高的推理强度虽能在复杂任务中提升结果质量，但也会导致更多Token消耗及更高的延迟。

:::注意：基于OpenRouter的自适应思维模型（Claude 4.6+、Fable/Mythos系列）
这类模型采用*自适应*思维方式，不支持常规的`reasoning.effort`字段——OpenRouter会忽略该字段。Hermes会自动将您的`reasoning_effort`参数映射为OpenRouter的`verbosity`参数（该参数对应Anthropic的`output_config.effort`），因此相同的强度调节机制仍可适用于所选模型支持的各等级别。若设置为`none`（或未设置），则模型将沿用其自身的自适应默认设置。而原生的Anthropic提供商可直接控制推理强度，因此不会受到影响。
:::

:::note OpenRouter 模型及支持的难度级别  
对于通过 OpenRouter 转发的其他模型，Hermes 会读取实时模型目录中的推理元数据（`supported_parameters` 以及各模型的 `reasoning.supported_efforts`），以此决定是否发送推理控制指令，并将您请求的难度级别限制在当前路由实际支持的最低级别（始终向下调整——例如，在仅支持 `high` 级别的路由上，`ultra` 级别会被降为 `high`，而不会自动升级）。具备推理功能的新供应商可无需等待 Hermes 更新即可自动启用；若无法访问模型目录或找不到相应模型，Hermes 会回退到内置的模型系列列表，并原封不动地传递您的难度请求。  
:::

您还可以使用 `/reasoning` 命令在运行时更改推理难度级别：

```
/reasoning                # Show current effort level and display state
/reasoning high           # Set reasoning effort to high (this session only)
/reasoning high --global  # Set effort and persist to config.yaml
/reasoning none           # Disable reasoning (this session only)
/reasoning show           # Show model thinking above each response
/reasoning hide           # Hide model thinking
```

默认情况下，推理难度设置是针对单个会话有效的；如需将新的难度级别设置为 `agent.reasoning_effort` 的默认值，请添加 `--global` 参数。

#### 每个模型的独立推理难度设置

您可以为不同的模型设定不同的推理难度级别。当您希望复杂模型采用高难度推理，而快速处理的模型则使用中等难度时，此功能非常实用：

```yaml
agent:
  reasoning_effort: "medium"       # global default
  reasoning_overrides:
    "openrouter/anthropic/claude-opus-4.5": "xhigh"
    "openai/gpt-5": "low"
    "claude-sonnet-4.6": "high"    # bare model name also works
```

关键词匹配具有**拼写容错性**——任何合理的拼写形式均可被识别：
- `claude-opus-4.5`、`claude-opus-4-5`、`claude-opus.4.5`（点号和连字符可互换）
- `anthropic/claude-opus-4.5`、`openrouter/anthropic/claude-opus-4.5`（提供者前缀可选）
- 完全一致的拼写形式将优先于变体形式被识别。

:::note
`hermes config set`命令不支持对`reasoning_overrides`键进行设置——需直接编辑YAML文件。这是因为模型名称通常包含点号（例如`claude-opus-4.5`），而这与CLI的点号键语法存在冲突。
:::

**优先级判定规则：**

1. 会话级覆盖：通过`/reasoning --session`指令设置（仅适用于网关）
2. 按模型设置的覆盖：通过`agent.reasoning_overrides`指定（支持拼写容错）
3. 全局设置：`agent.reasoning_effort`的值
4. 提供者默认设置

上述覆盖规则会在所有场景下自动生效，包括CLI启动时、消息网关处理、桌面端/TUI界面、定时任务、会话中通过`/model`指令切换模型，以及启用备用模型时。

## 快速模式

快速模式可要求提供者以更高成本加快输出速度：OpenAI的[优先处理服务](https://openai.com/api-priority-processing/)（`service_tier: priority`）、xAI在Grok 4.6上的优先处理功能，以及Anthropic的[快速模式](https://platform.claude.com/docs/en/build-with-claudia/fast-mode)（`speed: fast`，仅支持Opus 4.8/Opus 5版本）。该功能**默认处于关闭状态**。

```yaml
agent:
  service_tier: ""          # "" / normal | fast | auto | cold
  fast_auto_seconds: 60     # window for auto / cold
```

| 模式 | 快速参数发送时机 | 适用场景 |
|------|---------------------------|----------|
| `normal`（默认值，`""`） | 从不发送 | 成本最低；延迟为标准水平 |
| `fast` | 每次请求时 | 需要持续高速响应的长时间交互会话 |
| `auto` | **每轮**对话的前 `fast_auto_seconds` 时间内发送请求 | 能快速获得首次回复；若工具调用循环时间较长，则恢复为标准计费方式 |
| `cold` | 同一时间窗口内，但仅限会话的**第一轮**（无历史记录时） | 可快速生成入门级回复，后续则按标准计费 |

命令 `/fast normal|fast|auto|cold` 可切换当前会话的模式；添加 `--global` 参数可将其持久保存至 `config.yaml` 文件中。单独使用 `/fast` 命令可查看当前模式。

**费用说明：** 两种服务提供商均会对快速请求按标准费率的一定倍数收费（Anthropic 在 Opus 4.8 和 Opus 5 平台上，每输入/输出 1 MTok 的费用分别为 10 美元和 50 美元），该费用还会与提示词缓存相关费用叠加。`auto`/`cold` 模式仅将这部分额外费用限制在特定时间窗口内。快速参数仅会发送到支持该功能的原生端点（如 `api.openai.com`/Codex 订阅服务、`api.anthropic.com`、`api.x.ai`）；无论采用何种模式，OpenRouter、Nous Portal、Copilot、Azure、Bedrock 以及自定义的 `base_url` 路由均不会收到这些参数。不同请求之间仅参数会有所变化——系统提示词、工具列表及消息内容保持完全一致，因此提示词缓存可以跨越时间窗口继续有效使用。

## 工具使用强制规则

部分模型有时会以文本形式描述其打算执行的操作，而非直接调用工具（例如只会说“我会运行测试……”，而不会真正调用终端）。通过强制要求模型使用工具的功能，系统会提供相应的提示引导，促使模型重新采取实际调用工具的操作。

```yaml
agent:
  tool_use_enforcement: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"`（默认值） | 对匹配的模型启用该功能，这些模型包括：`gpt`、`codex`、`gemini`、`gemma`、`grok`、`glm`、`qwen`、`deepseek`、`muse`；其他所有模型（如 Claude）均禁用该功能。 |
| `true` | 无论使用何种模型，始终启用该功能。如果您发现当前模型仅描述操作步骤而未实际执行，可使用此设置。 |
| `false` | 无论使用何种模型，始终禁用该功能。 |
| `["gpt", "codex", "qwen", "llama"]` | 仅当模型名称包含列表中的任意子串时（不区分大小写）才启用该功能。 |

### 它会注入什么内容

启用该功能后，系统提示中可能会添加两层指导指令：

1. **通用工具使用强制要求**（适用于所有匹配的模型）——要求模型立即调用工具而非仅描述意图，持续执行任务直至完成，且不得以“稍后再做”作为回合结束的理由。
2. **Google 操作指南**（仅适用于 Gemini 和 Gemma 模型）——强调内容简洁性、使用绝对路径、并行调用工具，以及先验证再编辑的操作规范。

这些指令对用户是不可见的，仅影响系统提示。那些已经能够稳定使用工具的模型（如 Claude）无需此类指导，这也是为何 `"auto"` 设置会将其排除在外。

### 何时启用该功能

如果您使用的模型不在默认的自动列表中，且发现它经常只描述“将会做什么”而非真正执行操作，可设置 `tool_use_enforcement: true`，或将该模型的子串添加到列表中。

```yaml
agent:
  tool_use_enforcement: ["gpt", "codex", "gemini", "grok", "my-custom-model"]
```

## 执行规范指导

除了强制要求使用工具外，Hermes还会为那些在评估日志中表现出相同智能体故障模式的模型系列注入**执行规范**模块。这些故障模式包括：用文字而非代码进行算术运算、在外部数据写入后跳过回读验证、试图“修复”格式错误的标识符、在数量不一致时仍声称任务已完成，以及在没有验证所有验收标准的情况下就宣布任务结束。

```yaml
agent:
  execution_guidance: "auto"   # "auto" | true | false | ["model-substring", ...]
```

| 值 | 行为 |
|-------|----------|
| `"auto"`（默认值） | 仅对以下模型启用该功能：`gpt`、`codex`、`grok`、`deepseek`、`kimi`、`qwen`、`glm`、`minimax`、`mimo`、`mistral`、`muse`。 |
| `true` | 无论使用何种模型，始终启用该功能。 |
| `false` | 无论使用何种模型，始终禁用该功能。 |
| `["deepseek", "my-custom-model"]` | 仅当模型名称包含列出的任意子字符串时（不区分大小写）才启用该功能。 |

注入的模块功能包括：

- **工具调用持久化**——持续调用工具，直至任务完成并得到验证；若查询结果为空、不完整或过于局限，会尝试使用更宽泛或不同的查询重新执行，直至获得满意结果。
- **强制使用工具**——算术运算、哈希值计算、日期处理、系统状态查询以及文件信息获取，均必须通过工具完成，严禁依赖人工心算。
- **外部写入后的回读验证**——在对外部系统进行任何会改变状态的写入操作后，需先回读目标数据以确保其正确性（对于工具已确认正确的内部文件修改，则无需再次验证）。
- **计数一致性校验**——声明的总量（`total`、`reply_count`、`has_more`）属于强制约束条件；若实际数值与之不符，需通过程序自动重新获取数据或进行解析。
- **原始标识符保留**——对于不符合规定格式的标识符，绝不可进行标准化处理或“修复”；即便查询成功，也不代表来源 Token 的格式就是正确的。
- **基于验证的完成判定**——“任务完成”意味着所有规定的验收标准均已通过验证，而非仅满足部分看似合理的条件。
该网关功能与 `tool_use_enforcement` 互不关联——二者可以单独启用，无需同时开启。系统会在会话开始时根据模型名称选定相应的引导策略，从而确保在整个对话过程中系统提示词保持字节级稳定（且便于提示词缓存）。Gemini/Gemma 被排除在自动列表之外，因为它们会接收到更为具体的 Google 操作指南；Claude 也被排除在外，因为它不存在这些故障模式——如需启用特定模型，可使用 `true` 值或子字符串列表进行指定。

## 工具调用循环防护机制

Hermes 能够检测到智能体是否陷入了无效的工具调用循环——例如相同的工具调用反复失败、同一工具持续出现故障，或是幂等调用始终返回相同结果而毫无进展。默认情况下，系统会在工具调用结果中注入**警告信息**，促使模型自行纠正错误。对于交互式 CLI、TUI、桌面端及 ACP 会话，由于有人工干预的可能，系统仅会发出警告；而对于无人值守的网关会话和定时任务会话，则默认会立即强制终止。

对于无人值守部署场景，可禁用基于平台默认设置的防护机制；或者也可以在所有平台上明确启用强制终止功能。

```yaml
tool_loop_guardrails:
  warnings_enabled: true       # inject warnings into tool results (default: true)
  hard_stop_enabled: false     # also BLOCK the call past the hard-stop threshold (default: false)
  non_interactive_hard_stop_enabled: true  # default hard stops for gateway/cron
  warn_after:
    exact_failure: 2           # identical failing call repeated N times
    same_tool_failure: 3       # same tool failing N times (different args)
    idempotent_no_progress: 2  # same result, no progress, N times
  hard_stop_after:
    exact_failure: 5
    same_tool_failure: 8
    idempotent_no_progress: 5
  loop_caps:
    max_web_searches: 50       # max web_search calls per turn (0 = unlimited)
    max_subagents: 50          # max subagents spawned per turn (0 = unlimited)
```

`hard_stop_enabled` 会明确为所有平台启用强制停止功能。当该值为 `false` 时，`non_interactive_hard_stop_enabled` 仍会为无人值守的网关/定时任务式平台启用此功能，但对于 CLI、TUI、桌面端、ACP、子代理以及运行在 `api_server` 环境中的节点（即带有活跃父进程或客户端的受监督任务循环），则仅会发出警告而不会真正停止。如需取消无人值守部署，可将 `non_interactive_hard_stop_enabled` 设置为 `false`。更多相关信息请参阅 [Docker / 无人值守部署](docker.md)。

强制停止功能旨在拦截**重复执行**行为——即完全相同的调用在中间没有任何变化地再次被执行——而非正常的迭代过程：

- **“编辑 → 重新运行”绝不属于循环行为**。任何成功的操作调用（如 `write_file`、`patch`、绿色的“终端”/“执行代码”操作、浏览器操作，以及任务/消息/定时任务的更新），都会为所有仍在统计中的失败调用标记进度。下一次完全相同的重试（如在修复问题后重新运行红色标记的测试，或在点击操作后再次生成快照），都将开启一个新的计数周期，而不会累积到触发停止的条件。
- **不同的红色命令属于诊断信息，而非循环行为**。对于那些非零退出码即表示正常输出的工具（如“终端”工具、“执行代码”工具、进程监控工具、“浏览器导航”工具、“网页提取”工具），`same_tool_failure` 阈值仅会发出警告而不会停止运行。只有当调用参数完全一致且中间没有任何变化，或出现结果连续相同的情形时，才会触发停止。
- **停止仅结束当前轮次，而非整个会话**。代理会回复是哪条安全规则被触发以及原因；若回复“继续”，则将以全新的每轮计数器重新开始。
### 每轮循环次数上限

除了上述基于故障的阈值外，`loop_caps`还设置了严格的上限，限制单个智能体在每一轮中可发起的`web_search`调用次数以及生成的子智能体数量。这些计数器会在每轮开始时重置，因此正常的多轮对话不会受到影响——但若某一轮陷入无止境的搜索或委托循环，系统会立即终止该轮。无论`hard_stop_enabled`的设置如何，这些限制始终处于激活状态并会自动生效。单轮内就发起数十次网络搜索或生成数十个子智能体已属于异常情况，因此默认值设置得较低。一旦达到上限，相关的工具调用会被阻止，并附带说明信息，从而使该轮有序结束，避免浪费剩余资源。如需完全取消此限制，可将对应数值设置为`0`。

单个`delegate_task`批次中的每个任务都会计入`max_subagents`的统计范围内（例如3个任务的批次会占用3次额度），因此该上限实际上反映的是实际生成的子智能体数量，而非`delegate_task`调用的总次数。

这一设置与Claude Code版本2.1.212中的每会话WebSearch及子智能体上限机制相同，后者的默认值也为200，并会在执行 `/clear` 命令时重置。

### 运行时防停滞保护机制

作为对上述基于失败检测的防护机制的补充，`agent.stall_guards`（默认值为 `true`）提供了两种更为保守的运行时防护措施，旨在避免不必要的轮次消耗。首先是一种**重复调用中断机制**：当同一个工具连续被调用3次及以上，且传入的参数完全相同、返回的结果也一致时，系统会在该工具的返回结果后附加一条简短提示，告知模型无需再次调用该工具——在仅用于警告的会话模式下，此机制不会阻止调用；同时，那些确实需要重复调用的工具（如 `process`、`*_get_result`、`*_poll` 等）也不在其限制范围内。而在启用强制停止机制的情况下（即显式设置了 `hard_stop_enabled`，或是处于无人值守的网关/定时任务平台环境中），一旦连续相同参数的调用次数达到 `hard_stop_after.idempotent_no_progress` 次，这种重复调用模式就会触发强制停止——且该限制适用于**所有**工具，而不仅限于 `idempotent_no_progress` 防护机制所监控的只读工具——因此，即使模型试图重复执行相同的成功 `terminal` 或 `skill_view` 调用，也会被立即中断，而不会耗尽迭代次数预算（即通过 `identical_call_streak_halt` 机制实现）。其次是一种**继续执行意图恢复机制**：当模型在某个轮次中未调用任何工具，但其简短回复中提到了后续要执行的操作（例如“我现在来更新文件……”）时，Hermes会通过与意图确认恢复时相同的有限次续问机制，再次提示模型执行该操作（每个轮次最多可进行2次续问）。这两种机制均具备缓存安全性（提示信息会在结果生成时添加，绝不会事后补录），并且可以同时被禁用。

```yaml
agent:
  stall_guards: false
```

同一入口还支持**结果引用存根机制**：当重新发起的完全相同的工具调用返回内容完全一致的新结果时，重复的请求载荷会以简短的引用存根形式被纳入上下文，该存根仅指向之前的结果（包括工具名称、`tool_call_id`、参数摘要，以及——如果首次结果已保存到磁盘——其存储路径），而无需重复输出全部内容。由于工具仍会每次都被执行，因此轮询机制得以保留：任何发生变化的结果都会完整传递。长度小于512字符的结果、错误结果以及多模态结果均不会被转换为存根，而轮询请求则会被转换（即当请求未发生变化时，重复的载荷实际上不包含任何信息）。

### 对话轮活跃性监控机制

`agent.turn_liveness`参数用于设定对话轮在**无任何可见进展**的情况下，Hermes允许其持续存在的最长时间，超过该时限后系统将强制恢复对话流程。该监控机制会记录活动计时器（该计时器同样用于标记API等待时间、流令牌有效期以及工具心跳信号——租约续期时间则不计入在内），因此那些在处理过程中突然停滞的对话轮（如问题#95548中所描述的：无工具执行、无API调用、无错误，但会无限期地保持“忙碌”状态）会被及时识别并中断，从而作为可重试的异常对话轮被处理；而如果中断操作无法恢复对话流程，该对话轮的持久租约将停止续期，这样系统就可以清理过期的对话轮，避免会话一直挂起直至进程被终止。

```yaml
agent:
  turn_liveness:
    timeout_s: 600.0   # idle bound; <= 0 disables the watchdog
    poll_s: 15.0        # sampling interval (seconds)
```

正常情况下的缓慢处理过程不会受到惩罚：流式响应、工具运行期间的心跳检测（每30秒一次），以及等待审批的时间都会持续消耗计时器，因此只有当某个轮次在规定的时间内完全没有任何进展时，才会触发监视机制。无效值（如拼写错误、`NaN`、`Inf`，或是非正数的`poll_s`）仅会记录警告并自动回退到默认设置——这类情况绝不会导致启动失败，也不会暗中关闭监视机制。一旦触发中止操作，系统会在开始恢复进程时报告当前停滞状态，并且只有在中断真正生效之后，才会发布最终的中止或租约终止结果。

## TTS配置

```yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts" | "kittentts" | "piper" | "deepinfra"
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

**语速回退优先级：**特定提供商设置的语速（例如`tts.edge.speed`）→全局`tts.speed`设置→默认值`1.0`。如需为所有提供商统一设置语速，可调整全局`tts.speed`；如需更精细的控制，则可为各提供商单独设置语速。 

## 显示设置

```yaml
display:
  tool_progress: all      # off | new | all | verbose
  tool_progress_command: false  # Enable /verbose slash command in messaging gateway
  focus_view: false       # CLI focus view (/focus) — reduced output, display-only
  platforms: {}           # Per-platform display overrides (see below)
  interim_assistant_messages: true  # Gateway: send natural mid-turn assistant updates as separate messages
  show_commentary: true   # Codex models: deliver commentary-channel progress narration as visible mid-turn updates
  skin: default           # Built-in or custom CLI skin (see user-guide/features/skins)
  personality: ""         # Legacy cosmetic field still surfaced in some summaries
  compact: false          # Compact output mode (less whitespace)
  cli_multiline_shortcuts: true  # CLI: Ctrl+J, \ + Enter, and supported Shift+Enter insert newlines (false = legacy c-j submit fallback)
  resume_display: full    # full (show previous messages on resume) | minimal (one-liner only)
  bell_on_complete: false # Play terminal bell when agent finishes (great for long tasks)
  bell_on_prompt: false   # Play terminal bell when a blocking prompt opens (clarify, approval, sudo password, secret capture) — works over SSH
  # Both bell flags also emit an OSC 9 desktop notification (Ghostty, iTerm2, Kitty, WezTerm raise an OS
  # notification; other terminals ignore it) and, inside Warp (TERM_PROGRAM=WarpTerminal with the CLI-agent
  # protocol advertised), a warp://cli-agent OSC 777 event (`stop` on completion, `permission_request` on
  # blocking prompts) so Warp's tab status and notification mailbox track Hermes. No extra keys needed.
  show_reasoning: true    # Show model reasoning/thinking above each response (default: true; toggle with /reasoning show|hide)
  streaming: false        # Stream tokens to terminal as they arrive (real-time output)
  show_cost: false        # Show estimated $ cost in the CLI status bar
  timestamps: false       # When true, prefixes user and assistant labels with timestamps in the CLI / TUI transcript
  timestamp_format: "%H:%M"  # strftime format for those timestamps (e.g. "%b-%d %H:%M" for month-day)
  tool_preview_length: 0  # Max chars for tool call previews (0 = no limit, show full paths/commands)
  turn_summary: true      # CLI only: print a one-line post-turn accounting footer after each interactive turn
  spinner_token_flow: true # CLI only: append live cumulative turn tokens to the spinner timer
  runtime_footer:         # Gateway: append a runtime-context footer to final replies
    enabled: false
    fields: ["model", "context_pct", "cwd"]
  status_bar:             # CLI/TUI: choose which status-bar fields are visible
    fields: []            # empty = show the default set; see below
  file_mutation_verifier: true    # Append an advisory footer when write_file/patch calls failed this turn
  credits_notices: true   # Nous credits status-bar notices (usage bands, grant-spent, depleted). false = silence them; /usage still works
  cli_rebuild_scrollback_on_redraw: false  # Classic CLI: also wipe terminal scrollback (CSI 3J) on /redraw / Ctrl+L / width-change resize recovery. Enable when a terminal/tmux stack stamps stale prompt chrome into scrollback on maximize/restore.
  language: en            # UI language for static messages (approval prompts, some gateway replies). en | zh | zh-hant | ja | de | es | fr | tr | uk | af | ko | it | ga | pt | ru | hu
```

### 每轮摘要与 Spinner 令牌流转机制

`display.turn_summary`（默认值为 `true`）会在每次**交互式 CLI 轮次**结束后输出一行简洁的记录，概括该轮次实际完成的内容：

```
⋯ 12.4s · edited 2 files +18 -3 · read 4 files · ran 3 commands
```

该统计信息直接来源于 CLI 已接收的 tool-progress 数据流，因此无需额外成本。详情如下：

- “Wall time”表示当前轮次的实际耗时（超过一分钟的部分以`2m05s`等形式显示）。
- 工具调用会按动词类型（如`edited`、`read`、`ran`、`searched`等）进行分组，并采用正确的复数形式；那些没有明确动词类型的插件/MCP 工具则统一归类为“调用了 N 个工具”。
- 仅当工具返回结果中已包含差异信息（目前为`patch`类型）时，才会出现`+X -Y`形式的行级差异显示。Hermes 不会通过 git 进行计算，因此执行`write_file`操作时的修改不会显示差异值。
- **失败的工具调用不会被计入统计**——被拒绝的写入操作永远不会被视为成功的修改（相关警告信息可参见[文件变更验证器](#file-mutation-verifier)）。
- 长轮次的输出会被限制在四个动词片段加上`+N more`的结尾，以避免行数溢出。
- 若某轮次未使用任何工具调用，则不会输出任何内容。

`display.spinner_token_flow`（默认值为`true`）会将当前轮次累计产生的输出token数叠加到 CLI 的旋转加载指示器的实时计时器中：

```
  ⚡ Reading cli.py  (  2.3s · ↓ 1.2k tok)
```

计数是按轮次计算的（会话总计以轮次开始时为基准），并且会随着每轮中的每次 API 调用所报告的使用情况而实时更新。在首次使用情况报告送达之前，不会显示任何内容，因此您不会看到误导性的“↓ 0 tok”字样。

这两个键仅用于显示且仅适用于 CLI：在静默模式、`display.tool_progress` 设置为 `off` 时、单次查询/`-Q` 批量运行模式下，以及网关/消息界面中（这些界面会使用 `display.runtime_footer`），这些键都会被隐藏。如需关闭它们，可将对应的键值设置为 `false`。

### 文件变更验证器

当 `display.file_mutation_verifier` 设置为 `true`（默认值）时，如果在某轮中发生了 `write_file` 或 `patch` 调用失败，且同一路径后续又没有成功的写入操作来覆盖该错误，Hermes 会在助手的最终回复中追加一行提示信息。这样一来，无需在每次编辑后手动运行 `git status`，就能避免出现“批量并行应用补丁，部分操作虽未显式报错但模型却声称全部成功”之类的虚假反馈。

示例底部信息：

```
⚠️ File-mutation verifier: 3 file(s) were NOT modified this turn despite any wording above that may suggest otherwise. Run `git status` or `read_file` to confirm.
  • concepts/automatic-organization.md — [patch] Could not find match for old_string
  • concepts/lora.md — [patch] Could not find match for old_string
  • concepts/rag-pipeline.md — [patch] Could not find match for old_string
```

将 `file_mutation_verifier: false`（或 `HERMES_FILE_MUTATION_VERIFIER=0`）设置为抑制底部信息显示。该验证机制仅在轮次结束时出现真正故障时才会触发——如果在同一轮次内模型重新尝试修复并成功，则不会对该文件触发此验证。

**请优先相信验证结果而非模型的总结信息。** 即使助手的结束消息表示任务已完成，底部信息也表明所列文件在磁盘上并未被修改。常见原因包括：

- **写入被拒绝**——路径位于凭证拒绝列表中，或处于 `HERMES_WRITE_SAFE_ROOT` 范围之外（详见[文件写入安全机制](./security.md#file-write-safety)）
- **补丁不匹配**——`old_string` 与磁盘上的文件内容不一致
- **语法校验失败**——候选内容在写入前未能通过 JSON/YAML/TOML 格式验证

当写入操作被阻止时，底部信息会显示如下示例：

```
⚠️ File-mutation verifier: 2 file(s) were NOT modified this turn despite any wording above that may suggest otherwise. Run `git status` or `read_file` to confirm.
  • ~/.hermes/cron/jobs.json — [patch] Write denied: '…' is outside HERMES_WRITE_SAFE_ROOT (/path/to/project)
  • ~/.hermes/scripts/monitor.py — [write_file] Write denied: '…' is outside HERMES_WRITE_SAFE_ROOT (/path/to/project)
```

如果对 Hermes 状态的写入操作（如定时任务、技能，以及位于 `~/.hermes/` 目录下的脚本）出现失败，请检查您的环境中是否设置了 `HERMES_WRITE_SAFE_ROOT`。对于定时任务的修改，建议使用 `cronjob` 工具或 `hermes cron edit` 命令，而非直接修改 `jobs.json` 文件。

### 静态消息的界面语言设置

`display.language` 设置用于翻译少量面向用户的静态消息——包括 CLI 的审批提示、部分网关斜杠命令的回复内容（例如重启 draining 操作的通知、“审批已过期”、“目标已完成”等）。该设置**不会**翻译智能体响应、日志行、工具输出、错误回溯信息或斜杠命令的描述，这些内容仍将保持英文。如果您希望智能体本身用其他语言回复，只需在提示语或系统消息中明确指定即可。

支持的值包括：`en`（默认）、`zh`（简体中文）、`zh-hant`（繁体中文）、`ja`（日语）、`de`（德语）、`es`（西班牙语）、`fr`（法语）、`tr`（土耳其语）、`uk`（乌克兰语）、`af`（南非荷兰语）、`ko`（韩语）、`it`（意大利语）、`ga`（爱尔兰语）、`pt`（葡萄牙语）、`ru`（俄语）、`hu`（匈牙利语）。对于未知的值，系统将默认回退为英文。

您也可以通过 `HERMES_LANGUAGE` 环境变量为当前会话单独设置该值，该值会优先于配置文件中的设定。

```yaml
display:
  language: zh   # CLI approval prompts appear in Chinese
```

| 模式 | 显示内容 |
|------|----------|
| `off` | 静默模式——仅显示最终结果 |
| `new` | 仅在工具状态发生变化时显示工具指示器 |
| `all` | 显示所有工具调用，并附有简短预览（默认值） |
| `verbose` | 显示完整的参数、结果及调试日志 |

在 CLI 中，可使用 `/verbose` 在这些模式之间切换。若要在消息平台（如 Telegram、Discord、Slack 等）中使用 `/verbose`，需在上述 `display` 部分中将 `tool_progress_command: true` 设为真值。这样该命令即可切换模式并将设置保存至配置文件中。

工具进度功能需要一个能够安全显示进度更新的网关适配器。那些不支持消息编辑功能的平台，包括 Signal，即便 `/verbose` 已将模式设置为非 `off` 值，也会隐藏工具进度提示框。

`off` 模式仅会隐藏工具调用的界面元素。而那些在桌面应用和 TUI 中有独立显示界面的应用状态——如任务列表（`todo_list`）、子智能体进度、问题澄清界面以及 MCP 同意卡片——则不受此设置影响，会持续显示。

### 聚焦视图（`/focus`，CLI + TUI）

将 `display.focus_view: true` 设为真值即可启用**聚焦视图**——这是一种简化输出的显示模式，适用于仅需获取答案而非详细执行过程的场景。它实际上是在原有的 `tool_progress` 机制之上添加的一层简单封装，而非另一套独立的隐藏逻辑：

- 启用该模式会将 `tool_progress` 设为 `off`，并将您之前的模式保存在 `display.focus_saved_tool_progress` 中；  
- 使用 `/focus off` 即可恢复原有模式，因此即使执行了 `/verbose verbose` 设置，再次切换后模式依然保持不变；  
- 每次对话轮次结束后都会显示一条简短的提示行——`⋯ 7 条工具行已隐藏 · /focus off 可查看`——这些计数会基于*聚焦前的模式*进行统计，因此不会误将您已经关闭的行计为隐藏状态；  
- 状态栏（无论是 prompt_toolkit CLI 还是 Ink TUI）中都会持续显示 `◉ focus` 标记，确保简化模式始终可见；  
- 当处于手动聚焦模式时，循环切换 `/verbose` 命令即可将模式重新设置为 `/verbose`，同时清除该标记。  

聚焦视图仅用于**显示目的**。它不会修改对话历史、系统提示、工具结构或任何请求内容——被隐藏的细节仅在屏幕上隐藏，而不会被丢弃，且提示缓存功能完全不受影响。  

### 状态栏字段选择（CLI/TUI）  

CLI/TUI 底部的交互式状态栏会显示模型信息、上下文使用情况、压缩次数、后台活动计数器、计时器以及模式标记。`display.status_bar.fields` 用于控制哪些字段可见——这有助于创建极简状态栏（仅显示模型名称和时长），或显示需手动启用的会话令牌总数：

```yaml
display:
  status_bar:
    fields: ["model", "duration", "total_tokens"]   # visibility only; built-in order is preserved
```

支持的字段包括：`model`、`context_detail`（已使用/总令牌数）、`context_pct`（百分比与进度条显示）、`cache_hit`（提示词缓存命中率——在更换模型或进行压缩后会重置）、`latency`（最近10次调用的API延迟的滚动平均值）、`tps`（最近10次调用的输出令牌数/秒的滚动平均值）、`compressions`、`bg_tasks`、`bg_processes`、`bg_subagents`、`goal`、`duration`、`prompt_elapsed`、`idle_since`、`focus`、`yolo`、`stash`、`battery`、`title`（右对齐的会话标识）以及`total_tokens`（整个会话的令牌总数——需手动开启，默认不会显示）。

注意事项：

- 空列表（即默认设置）会保留标准字段集——除`total_tokens`之外的所有字段。
- 该配置仅控制字段的**显示与否，而不影响其排列顺序**；各字段仍会按照既定位置显示。
- 即使设置了相应配置，宽度较窄的终端仍会隐藏仅适用于宽屏模式的字段（`context_detail`、`cache_hit`、`latency`、`tps`、`prompt_elapsed`、`idle_since`）；不过在列数≥52的中等宽度终端上，`cache_hit`也会显示。
- 在有API调用记录之前（例如Codex应用服务器后端未报告任何延迟时），`latency`和`tps`会保持隐藏状态。
- `battery`和`title`的显示与否还需通过单独的切换指令控制（分别为`/battery`和 `/title`）——只有同时开启这两个指令，对应字段才会显示。
- 同一键值也用于筛选**Ink TUI**状态界面（通过`hermes tui`进入），在该界面中，`cache_hit`、`latency`和`tps`会分别以符合终端宽度限制的符号形式（◎ / ◷ / ↑）显示在列数≥96/104/110的终端上。
- 这些字段仅为显示用途，不会影响提示词缓存或请求数据的内容。相关更改需等到下一次会话开始时才会生效。
### 运行时元数据页脚（仅限网关）

当 `display.runtime_footer.enabled: true` 时，Hermes 会在每个网关轮次的**最终**消息中添加一段简短的运行时上下文页脚。该页脚可显示所使用的模型、上下文窗口使用比例以及当前工作目录。此功能默认处于关闭状态；如果您的团队希望每条回复都包含这些来源信息，可针对各个网关单独开启该功能。

```yaml
display:
  runtime_footer:
    enabled: true
    fields: ["model", "context_pct", "cwd"]   # order shown; drop any to hide
```

支持的字段：

| 字段 | 显示格式 | 示例 |
| --- | --- | --- |
| `model` | 仅显示模型编号，已移除供应商前缀 | `gpt-5.4` |
| `context_pct` | 上次请求的上下文占用比例（以百分比表示） | `5%` |
| `latency` | 单次响应的实时时长 | `22s`, `1m05s` |
| `cwd` | 相对于用户主目录的工作目录路径 | `~` |

默认字段集为 `["model", "context_pct", "cwd"]`。`latency` 字段为可选项——如需使用，需将其添加到 `fields` 列表中。若某个字段的数据不可用，系统会静默跳过该字段，而不会显示空值。

在任何会话中，均可通过 `/footer` 命令在运行时切换此设置。

以下为添加到 Telegram/Discord/Slack 回复中的示例页脚内容：

```
— claude-opus-4.7 · 12 tool calls · 2m 14s · $0.042
```

仅轮次中的**最终**消息会显示页脚信息，而中间更新内容则保持简洁无冗余。

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

通过 CLI，应使用标准路径：`hermes config set display.platforms.telegram.streaming false`。简写形式 `hermes config set platforms.telegram.streaming false` 也同样有效：由于针对各平台的*显示*设置（如 `streaming`、`show_reasoning`、`tool_progress` 等）始终仅从 `display.platforms` 中读取，因此 `config set`/`get`/`unset` 命令会将该简写转换为标准键值，并同时输出提示信息。而位于顶层 `platforms.<name>` 块下的连接相关键值（如 `token`、`enabled`、`reply_to_mode`、`extra`）则不会被转换。

未进行自定义设置的平台将会回退至全局的 `tool_progress` 值。有效的平台键包括：`telegram`、`discord`、`slack`、`signal`、`whatsapp`、`matrix`、`mattermost`、`email`、`sms`、`homeassistant`、`dingtalk`、`feishu`、`wecom`、`weixin`、`bluebubbles`、`qqbot`。为保持向后兼容性，旧的 `display.tool_progress_overrides` 键仍会被加载，但它已处于废弃状态，首次启动时会自动迁移至 `display.platforms` 中。

Signal 被列为有效的平台键，是因为其相关设置允许按平台单独保存；但目前版本的 Signal 适配器无法编辑已发送的消息，也无法显示工具进度提示框。因此建议将 Signal 的 `tool_progress` 设置为 `off`；若需实时查看每个工具调用的执行情况，则应使用 CLI 或具备编辑功能的消息平台。

`interim_assistant_messages` 功能仅适用于网关。启用该功能后，Hermes 会将已完成的中途助手更新内容以独立聊天消息的形式发送出去。此功能与 `tool_progress` 无关，也不需要依赖网关的流式传输功能。

`show_commentary`（默认值为 `true`）用于控制 Codex 响应模型中的注释通道——即这些模型在展示其内部推理过程的同时，还会生成的详细进度描述。启用该选项后，每条生成的注释消息都会作为可见的中间更新结果呈现出来（在网关端，这还需要开启 `interim_assistant_messages` 功能）。如果您觉得多余的描述令人困扰，可将其设置为 `false`：此时注释功能将退化为仅通过推理通道输出，且仅在启用了 `show_reasoning` 时才会显示。 

## 隐私保护

```yaml
privacy:
  redact_pii: false  # Strip PII from LLM context (gateway only)
```

当 `redact_pii` 设置为 `true` 时，该网关会在将系统提示语发送到支持平台的大型语言模型之前，先对其进行处理以隐藏其中的个人身份信息：

| 字段 | 处理方式 |
|-------|-----------|
| 电话号码（WhatsApp/Signal 用户 ID） | 哈希处理为 `user_<12位sha256哈希值>` |
| 用户 ID | 哈希处理为 `user_<12位sha256哈希值>` |
| 聊天 ID | 数字部分进行哈希处理，保留平台前缀（格式为 `telegram:<哈希值>`） |
| 主频道 ID | 数字部分进行哈希处理 |
| 用户名称 | **不受影响**（由用户自行设定，可公开显示） |

**平台支持情况：** 此功能适用于 WhatsApp、Signal 和 Telegram。Discord 和 Slack 不在支持范围内，因为它们的提及系统（`<@user_id>`）要求在大型语言模型上下文中使用真实 ID。

哈希值具有确定性——同一用户始终对应相同的哈希值，因此模型仍能区分群组聊天中的不同用户。在内部路由和数据传递过程中则使用原始值。

### OpenAI Codex 请求标识

OpenAI 要求第三方 Codex 工具必须标明自身身份。通过 ChatGPT 验证的请求在发送到官方 Codex 接口时，会自动附带 `originator: hermes-agent` 和 `User-Agent: HermesAgent/<版本号>` 参数。原有的 ChatGPT 账户标识头信息将保持不变，且不会发送额外的提示语内容或遥测数据。直接调用 OpenAI API 的请求以及自定义代理端点则保持原有设置不变。

## 语音转文本（STT）

```yaml
stt:
  enabled: true                # Auto-transcribe inbound voice messages (default: true)
  echo_transcripts: true       # Post raw transcripts back to the chat as 🎙️ "..." (default: true)
  provider: "local"            # "local" | "groq" | "openai" | "mistral" | "xai" | "elevenlabs" | "deepinfra" | ...
  language: "en"               # GLOBAL language hint for every provider (per-provider language wins); set "" for auto-detect
  cloud_trim_silence: true     # trim long pauses with ffmpeg before uploading to a cloud provider (default: true)
  cloud_trim_threshold_db: -40 # audio quieter than this counts as silence
  cloud_trim_keep_ms: 300      # how much of each pause survives the trim (keeps natural pacing)
  # prompt: "Hermes, Teknium, Nous Research, kanban"   # Static vocabulary hint (see below)
  local:
    model: "base"              # tiny, base, small, medium, large-v3
    language: ""               # per-provider override of stt.language
    initial_prompt: ""         # optional whisper prompt to bias vocabulary/script (e.g. Simplified Chinese)
    vad: true                  # Silero VAD filter (default on) — silence never reaches whisper; false = raw behavior (music/ambient)
    vad_min_silence_ms: 500    # min silence (ms) that splits speech chunks when vad is on
    no_speech_prob_threshold: 0.6  # drop a segment only when no_speech_prob > this...
    logprob_threshold: -1.0        # ...AND avg_logprob < this (both must hit — quiet real speech survives)
    unload_after_idle_seconds: 0   # 0=never unload (default); e.g. 300 = release the model after 5min idle
  groq:
    language: ""               # per-provider override of stt.language
  openai:
    model: "whisper-1"         # whisper-1 | gpt-4o-mini-transcribe | gpt-4o-transcribe | gpt-transcribe
    language: ""               # per-provider override of stt.language
  # model: "whisper-1"         # Legacy fallback key still respected
```

所有 STT 提供商（包括本地服务、groq、OpenAI、Mistral、XAI、ElevenLabs、DeepInfra，以及各类命令提供商和插件）在语言识别方面均遵循相同的规则：`stt.<provider>.language` → `stt.language` → `HERMES_LOCAL_STT_LANGUAGE` 环境变量 → 由提供商自动检测语言。默认值为 `stt.language: "en"`——Whisper 的自动检测功能往往无法准确识别较短或带有口音的音频片段，从而导致语音笔记被错误地转录成其他语言。非英语使用者应将其设置为对应的语言代码（如 `"es"`、`"zh"`、`"uk"`）；若需恢复多语言自动检测功能，则可将其设为 `""`。

当网关需要为智能体转录语音笔记，但又不得将原始转录内容回传至聊天界面时（例如面向客户的 WhatsApp 机器人），请将 `stt.echo_transcripts` 设置为 `false`。各提供商的行为表现如下：

- `local` 模式使用在用户本地运行的 `faster-whisper` 工具。需通过 `pip install faster-whisper` 单独进行安装。该模式默认已开启抑制幻觉的功能：Silero VAD 过滤器可防止静音或噪声传入 Whisper 模型，同时关闭了跨窗口条件判断机制，还会自动将模型识别为非语音的片段以及置信度较低的片段过滤掉。若需以原始模式转录非语音音频（如音乐、环境音），可设置 `stt.local.vad: false`。为实现低延迟转录，模型会在不同语音消息之间保留在内存中；可通过设置 `stt.local.unload_after_idle_seconds`（例如设置为 `300` 表示5分钟后）在模型处于空闲状态时自动释放它。这样可在使用 CUDA 的设备上释放 GPU 内存（这也是本地大语言模型共享 GPU 时的主要优势）；在 CPU 上，这些内存可被其他进程重新使用，不过在进程需要再次占用该内存之前，操作系统显示的内存占用情况可能不会发生变化。下一个语音消息到来时，模型会自动重新加载。

- `groq` 模式利用 Groq 提供的与 Whisper 兼容的接口，并读取 `GROQ_API_KEY` 密钥。通过设置 `stt.groq.language`（或全局环境变量 `HERMES_LOCAL_STT_LANGUAGE`）可跳过自动检测流程，从而降低延迟。

- `openai` 模式使用 OpenAI 的语音 API，并读取 `VOICE_TOOLS_OPENAI_KEY` 密钥。
当安装了 `ffmpeg` 时，各类云服务提供商（groq、openai、mistral、xai、elevenlabs、deepinfra）默认会启用**上传前静音裁剪**功能：在文件上传之前，语音笔记中的长停顿会在客户端被压缩处理，同时保留每个停顿的 `cloud_trim_keep_ms` 长度，从而确保语音节奏的自然流畅。较短的音频意味着更快的上传速度、更低的按分钟计费费用，还能减少远程模型产生的静音幻觉问题。长度小于12秒的音频片段将完全跳过裁剪步骤（此时节省空间已无意义，且部分提供商本身会按每次请求收取最低费用）。该裁剪功能为尽力而为型——如果未安装 `ffmpeg`、裁剪失败、音频片段以静音为主，或裁剪后节省的空间不足约10%，则原文件将原封不动地上传。如需始终上传原始文件（例如通过云服务提供商转录音乐或环境音），可设置 `stt.cloud_trim_silence: false`。命令型和服务插件型提供商的音频则永远不会被裁剪。

用户明确指定的 `stt.provider` 会得到严格优先处理——如果该提供商不可用，系统会提示出现转录错误，并建议使用 `hermes tools` 而非更换提供商。只有当从未选择过任何提供商时，Hermes才会按以下顺序自动检测：`local` → `groq` → `openai`。

Groq和OpenAI模型的优先级则由环境变量决定：

```bash
STT_GROQ_MODEL=whisper-large-v3-turbo
STT_OPENAI_MODEL=whisper-1
GROQ_BASE_URL=https://api.groq.com/openai/v1
STT_OPENAI_BASE_URL=https://api.openai.com/v1
```

### 语音转写提示（词汇提示）

`stt.prompt` 是一个可选的静态提示，用于传递给具备提示功能的语音转写后端。对于那些 Whisper 系列模型容易听错的专有名词、产品名称及专业术语，可借助该功能进行准确转写。

```yaml
stt:
  provider: "local"
  prompt: "Hermes, Teknium, Nous Research, kanban, Ollama"
```

**组合逻辑。** 配置值是基础内容。注册了 [`pre_transcription`](/user-guide/features/hooks#pre_transcription) 钩子的插件会在其基础上进行修改，每个字段采用“最后写入者胜出”的规则。多个插件的提示信息会以确定性的方式组合在一起：插件发现机制会按照插件 ID 的排序加载插件，而每个插件的回调函数则按其注册顺序执行，因此相同的插件组合始终会产生一致的最终提示语。如果某个钩子为 `prompt` 返回空字符串，则会清除该请求的配置提示语。钩子还可以覆盖 `language` 和 `model` 参数；`file_path` 为只读属性，任何试图修改它的尝试都会被记录并忽略。在没有注册任何钩子且未设置 `stt.prompt` 的情况下，生成的请求内容与之前的版本完全相同。

**提供商支持。**

| 提供商 | 提示参数 | 行为表现 |
|----------|-----------------|----------|
| `local` (faster-whisper) | `initial_prompt` | 原样传递给本地模型 |
| `openai` | `prompt` | 在转录请求中原样传递 |
| `groq` | `prompt` | 在转录请求中原样传递 |
| `mistral` | `prompt` | 在转录请求中原样传递 |
| `deepinfra` | `prompt` | 采用与 OpenAI 兼容的传输方式，原样传递 |
| `xai` | 不支持 | 以 DEBUG 级别记录日志，随后在没有提示参数的情况下继续处理请求 |
| `elevenlabs` | 不支持 | 以 DEBUG 级别记录日志，随后在没有提示参数的情况下继续处理请求 |
| `local_command` | 不支持 | 以 DEBUG 级别记录日志，随后在没有提示参数的情况下继续处理请求 |
| 类型为 `command` 的 `stt.providers.<name>` | 不支持 | 以 DEBUG 级别记录日志，随后在没有提示参数的情况下继续处理请求 |
| 插件注册的供应商 | `transcribe(**extra)` 参数中的 `prompt` | 仅当设置了提示参数时才会发送，因此早期版本的供应商将接收到未作修改的调用请求 |

**长度限制。** Whisper 系列模型仅考虑最后约 224 个提示词标记。对于 Whisper 系列的后端（`local`、`openai`、`groq`、`deepinfra`），Hermes 会在客户端强制执行此长度限制：如果最终提示词过长，系统会截取其后部分内容并记录警告日志——请求不会因提示词长度问题而出错。其他后端（`mistral` 及插件供应商）则会原样接收提示词，并由其自行进行验证。无论哪种情况，都建议保持提示词简短且具体。

:::warning 提示词会与音频一同上传
最终的提示词会连同音频文件一起发送给已配置的文本转语音服务提供商。请务必避免将敏感信息以及会话生成的上下文放入 `stt.prompt` 变量中，也不要让其出现在 `pre_transcription` 钩子函数返回的任何内容里，尤其是当所使用的服务提供商是托管型 API 而非本地的 `faster-whisper` 时。
:::

## 语音模式（CLI）

```yaml
voice:
  record_key: "ctrl+b"         # Push-to-talk key inside the CLI
  max_recording_seconds: 120    # Hard stop for long recordings
  auto_tts: false               # Enable spoken replies automatically when /voice on
  beep_enabled: true            # Play record start/stop beeps in CLI voice mode
  beep_volume: 0.3              # Beep amplitude (0.0-1.0); raise it on quiet systems / headphones
  silence_threshold: 200        # RMS threshold for speech detection
  silence_duration: 3.0         # Seconds of silence before auto-stop
```

在 CLI 中使用 `/voice on` 可启用麦克风模式，使用 `record_key` 可启动/停止录音，而 `/voice tts` 则用于切换语音回复功能。有关端到端设置及不同平台上的具体行为，请参阅 [语音模式](/user-guide/features/voice-mode) 文档。

## 流式传输

在令牌生成后立即将其传输至终端或消息平台，而无需等待完整响应。

### CLI 流式传输

```yaml
display:
  streaming: true         # Stream tokens to terminal in real-time
  show_reasoning: true    # Also stream reasoning/thinking tokens (optional)
```

启用该功能后，响应内容会以逐条消息的形式显示在流式框中。同时，工具调用仍会被默默记录下来。如果对应提供商不支持流式输出，系统会自动切换为常规显示模式。

### 网关流式传输（Telegram、Discord、Slack）

```yaml
streaming:
  enabled: true           # Enable progressive message editing (default: false)
  transport: auto         # "auto" (default) | "edit" (progressive message editing) | "off"
  edit_interval: 0.8      # Seconds between message edits (default: 0.8)
  buffer_threshold: 24    # Characters before forcing an edit flush (default: 24)
  cursor: " ▉"            # Cursor shown during streaming
  fresh_final_after_seconds: 0    # Opt in to fresh final (Telegram) when preview is this old
```

启用该功能后，机器人会在接收到第一个令牌时发送消息，随后随着更多令牌的到达逐步修改该消息。对于不支持消息编辑的平台（如 Signal、Email、Home Assistant），系统会在首次尝试时自动识别，并为该会话优雅地关闭流式发送功能，从而避免消息大量堆积。

若希望在不进行逐令牌编辑的情况下单独发送中间状态的消息更新，可设置 `display.interim_assistant_messages: true`。

**溢出处理：** 当流式发送的文本超过平台规定的消息长度限制（约 4096 字符）时，当前消息将会被定稿，系统会自动开始发送新消息。

**Telegram 的“全新定稿”功能：** Telegram 的 `editMessageText` 功能会保留原始消息的时间戳，因此长时间进行的流式回复在完成后仍会显示最初发送时的时间戳。如需将旧预览作为全新的定稿消息发送，并尽力删除旧预览，可设置 `fresh_final_after_seconds > 0`。默认值为 `0`，此时流式回复会直接在原位置定稿，从而避免在同时显示两种操作状态的客户端上出现短暂的重复消息或删除序列。

:::note 各平台的流式传输默认设置  
主配置项 `streaming.enabled` 的默认值为 `false`——在手动将其设置为 `true` 之前，不会进行任何流式传输。一旦启用流式传输，具体行为将**根据不同平台而定**：Telegram 的默认值为 `display.platforms.telegram.streaming: true`（支持流式传输），而 Discord 的默认值为 `display.platforms.discord.streaming: false`（不支持）。因此，在启用流式传输后，Telegram 会立即开始流式传输，而 Discord 则会保持仅发送完整消息的回复方式，直到你更改其相关设置。你可以通过控制面板中的 **Channels** 设置项，或直接在 `~/.hermes/config.yaml` 文件中调整这些针对不同平台的开关值。  
:::

## 群聊会话隔离功能  

限制通过 CLI、TUI/控制面板以及消息网关同时打开的活跃聊天会话数量：

```yaml
max_concurrent_sessions: null  # null/0 = unlimited; positive integer = active session cap
```

当会话进入**第一个轮次**时，相应的资源槽位就会被占用，而非在打开聊天窗口的瞬间。在发送消息之前，打开、恢复或重新连接聊天窗口都是免费的，因此处于空闲状态的桌面标签页（以及可能引发不稳定的 WebSocket 连接）不会导致共享同一配额的消息网关资源耗尽。

一旦达到该上限，Hermes 会直接返回一条限制信息，指出是哪些组件占用了这些槽位。现有的活跃会话仍会保持正常运行。执行 `hermes status` 命令即可查看当前的槽位使用情况以及所有占用者。

标准的配置键为顶层键 `max_concurrent_sessions`。虽然 Hermes 也会以 `gateway.max_concurrent_sessions` 作为备选值，但当两者同时被设置时，顶层键的配置优先生效。

该限制是通过本地的运行时租约文件来实现的，属于尽力而为的方式：如果无法读取或锁定该注册表，Hermes 也会尝试打开连接，以避免用户陷入困境。此机制适用于单个主机/配置文件的运行环境，而不适用于在多台机器上共享的 `$HERMES_HOME` 目录。

可控制共享聊天是按房间维护单次对话，还是按参与者维护单次对话：

```yaml
group_sessions_per_user: true  # true = per-user isolation in groups/channels, false = one shared session per chat
```

- `true` 是默认且推荐的设置。在 Discord 频道、Telegram 群组、Slack 频道等类似共享环境中，只要平台能提供用户 ID，每位发送者都会拥有独立的会话。
- `false` 会恢复到旧的共享会话模式。如果您希望 Hermes 将某个频道视为一个统一的对话场景，此设置非常有用；但这也意味着所有用户会共享上下文、令牌成本以及消息中断状态。
- 直接消息不受影响。Hermes 仍会像往常一样根据聊天/直接消息 ID 对其进行标识。
- 无论采用哪种设置，子线程始终与所属主频道相互隔离；当设置为 `true` 时，每个子线程中的参与者也会拥有独立的会话。

如需了解相关行为细节和示例，请参阅 [会话](/user-guide/sessions) 以及 [Discord 使用指南](/user-guide/messaging/discord)。

## 未知用户发送直接消息时的处理方式

可控制当有未知用户发送直接消息时 Hermes 的响应行为：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- 对于聊天式私信平台，默认设置为 `pair` 模式。Hermes 会拒绝访问此类请求，但会在私信中回复一个一次性配对码。
- `ignore` 模式则会静默忽略未经授权的私信。
- 对于电子邮件，除非设置了 `platforms.email.unauthorized_dm_behavior: pair`，否则默认行为为 `ignore`，因为收件箱中可能包含大量无关的未读邮件。
- 各平台的特定设置可覆盖全局默认值，因此您可以在保持整体配对功能开启的同时，让某个特定平台的私信通知更少。

## 快速命令

您可以定义自定义命令，这些命令要么在不调用大型语言模型的情况下执行 Shell 命令，要么将一个斜杠命令别名为另一个命令。快速命令无需任何标记即可使用，非常适合在 Telegram、Discord 等消息平台上用于快速检查服务器状态或运行实用脚本。

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
    command: cd ~/.hermes/hermes-agent && git pull && uv pip install -e .
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
- **跨平台兼容**——支持命令行界面、Telegram、Discord、Slack、WhatsApp、Signal、电子邮件以及 Home Assistant 等平台  

仅包含字符串的提示语无法作为有效的快速命令。如需创建可重复使用的提示语工作流，请为现有的命令创建技能或别名。

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

**`mode`** 参数用于控制脚本的运行工作目录及 Python 解释器：

- **`project`**（默认值）——脚本在会话的工作目录中运行，使用当前激活的虚拟环境/Conda 环境中的 Python。项目依赖项（如 `pandas`、`torch` 以及项目自带的包）和相对路径（如 `.env`、`./data.csv`）能够像在 `terminal()` 模式下一样被正确解析。
- **`strict`**——脚本在临时准备目录中运行，使用 `sys.executable`（即 Hermes 自带的 Python）。此模式可实现最高的可重复性，但项目依赖项和相对路径将无法被解析。

两种模式下都会执行环境清理操作（移除包含 `*_API_KEY`、`*_TOKEN`、`*_SECRET`、`*_PASSWORD`、`*_CREDENTIAL`、`*_PASSWD`、`*_AUTH` 的内容），同时也会应用工具白名单机制——切换模式不会改变系统的安全设置。

## 网页搜索后端

`web_search` 和 `web_extract` 工具支持五种后端提供商。您可以通过 `config.yaml` 文件或 `hermes tools` 命令来配置后端。

```yaml
web:
  backend: firecrawl    # firecrawl | searxng | parallel | tavily | perplexity | keenable | exa

  # Or use per-capability keys to mix providers (e.g. free search + paid extract):
  search_backend: "searxng"
  extract_backend: "firecrawl"

  # Keyless free-tier fallback (default: true). With no backend configured
  # and no API keys present, web tools rotate across the Exa/Parallel/
  # Firecrawl/Keenable free tiers. Set false to disable.
  keyless_fallback: true

  # One-shot keyless rescue (default: true). When the chosen/keyed backend
  # fails a call, that single call retries on the keyless ring; the next
  # call attempts the chosen backend again (never sticky).
  keyless_rescue: true

  # Pin Exa/Parallel to a tier (set by the hermes tools Free/Paid rows).
  # free = always the anonymous endpoint; paid = always the keyed SDK path;
  # unset = auto (key present -> paid, otherwise free).
  provider_tier:
    parallel: free
    exa: paid
```

| 后端服务 | 环境变量 | 搜索功能 | 提取功能 |
|---------|---------|--------|---------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ |
| **SearXNG** | `SEARXNG_URL` | ✔ | — |
| **Parallel** | `PARALLEL_API_KEY`（可选——无密钥即可享受免费套餐） | ✔ | ✔ |
| **Tavily** | `TAVILY_API_KEY`（可选——选定后无需密钥） | ✔ | ✔ |
| **Perplexity** | `PERPLEXITY_API_KEY` | ✔ | ✔（生成与查询相关的片段） |
| **Exa** | `EXA_API_KEY`（可选——无密钥即可享受免费套餐） | ✔ | ✔ |

**后端服务选择：** 运行时始终会使用预先设置的 `web.backend` 值（可通过 `hermes tools` 进行设置；而 `nous` 则通过托管的 Tool Gateway 来处理请求）。只有当从未选择过任何 Web 后端服务时，系统才会根据现有的 API 密钥自动检测合适的后端：若仅设置了 `SEARXNG_URL`，则使用 SearXNG；仅设置 `EXA_API_KEY` 则使用 Exa；仅设置 `TAVILY_API_KEY` 则使用 Tavily；仅设置 `PERPLEXITY_API_KEY` 则使用 Perplexity；仅设置 `PARALLEL_API_KEY` 则使用 Parallel；仅设置 `KEENABLE_API_KEY` 则使用 Keenable。如果在未做任何选择且没有任何密钥的情况下发起请求，系统会按循环顺序在无需密钥的免费套餐服务（Exa / Parallel / Firecrawl / Keenable）之间切换，并在遇到速率限制时自动切换到下一个服务——详情请参阅[Web 搜索指南](/user-guide/features/web-search)。一旦确定了后端服务，只需在 `.env` 文件中添加对应的密钥，也不会改变当前的路由设置。此外，在 `hermes tools` 中选择 Tavily、Firecrawl 或 Keenable 时，即便不提供密钥也能正常使用。

**SearXNG**是一款免费、可自托管且注重隐私的元搜索引擎，能够查询70多种搜索引擎。无需API密钥——只需将`SEARXNG_URL`设置为您的实例地址（例如`http://localhost:8080`）。SearXNG仅支持搜索功能；而`web_extract`功能则需要单独的提取服务提供商（需设置`web.extract_backend`）。有关Docker部署的详细说明，请参阅[网络搜索配置指南](/user-guide/features/web-search)。

**自托管版Firecrawl**：将`FIRECRAWL_API_URL`设置为指向您自己的实例地址。一旦指定了自定义URL，API密钥则变为可选（可在服务器上设置`USE_DB_AUTHENTICATION=***`以禁用身份验证）。

**并行搜索模式**：通过设置`PARALLEL_SEARCH_MODE`来控制搜索行为——可选择`fast`、`one-shot`或`agentic`模式（默认值为`agentic`）。

**Exa**：在`~/.hermes/.env`文件中设置`EXA_API_KEY`。该功能支持按`category`进行筛选（如`company`、`research paper`、`news`、`people`、`personal site`、`pdf`），同时也支持按域名和日期筛选。

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

- `must_respond`（默认值）——捕获对话内容，并将其显示在 `browser_snapshot.pending_dialogs` 中，同时等待智能体调用 `browser_dialog(action=...)`。若在 `dialog_timeout_s` 秒内未收到响应，该对话将自动关闭，以避免页面的 JavaScript 线程永久阻塞。
- `auto_dismiss`——捕获对话后立即关闭。之后，智能体仍可在 `browser_snapshot.recent_dialogs` 中看到该对话记录，其状态标记为 `closed_by="auto_policy"`。
- `auto_accept`——捕获对话后立即接受。此策略适用于那些会频繁弹出 `beforeunload` 警告的页面。

如需了解完整的对话处理流程，请参阅[浏览器功能页面](./features/browser.md#browser_dialog)。

该浏览器工具集支持多种数据提供方。有关 Browserbase、浏览器使用方式以及本地 Chromium 系列 CDP 的配置详情，请查看[浏览器功能页面](/user-guide/features/browser)。

## 时区

可通过 IANA 时区字符串来覆盖服务器默认时区。这将影响日志中的时间戳、cron 定时任务以及系统提示语的时间显示。

```yaml
timezone: "America/New_York"   # IANA timezone (default: "" = server-local time)
```

支持的值：任何IANA时区标识符（例如 `America/New_York`、`Europe/London`、`Asia/Kolkata`、`UTC`）。如需使用服务器本地时间，则可留空或省略该参数。

## Discord

配置消息网关针对Discord的特定行为：

```yaml
discord:
  require_mention: true          # Require @mention to respond in server channels
  free_response_channels: ""     # Comma-separated channel IDs where bot responds without @mention
  auto_thread: true              # Auto-create threads on @mention in channels
```

- `require_mention` — 当设置为 `true`（默认值）时，机器人仅在通过 `@BotName` 被提及时才会在服务器频道中回复；而在私信中则无需提及即可随时回复。
- `free_response_channels` — 以逗号分隔的频道 ID 列表，机器人可在这些频道中对所有消息直接回复，无需任何提及。
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

- `redact_secrets` — 当设置为 `true` 时，该功能会自动检测工具输出中类似 API 密钥、令牌和密码的字符串，并在它们进入对话上下文或日志之前将其遮蔽。**默认处于开启状态**。仅当您需要原始的凭证类字符串用于调试或遮蔽器开发时，才应明确将其设置为 `false`。
- `tirith_enabled` — 当设置为 `true` 时，终端命令在执行前会由 [Tirith](https://github.com/sheeki03/tirith) 进行扫描，以识别可能具有危险性的操作。
- `tirith_path` — Tirith 可执行文件的路径。如果 Tirith 安装在非标准位置，则需设置此参数。
- `tirith_timeout` — 等待 Tirith 扫描的最大秒数。若扫描超时，命令仍会继续执行。
- `tirith_fail_open` — 当设置为 `true`（默认值）时，即便 Tirith 不可用或扫描失败，命令也允许继续执行。将其设置为 `false` 可在 Tirith 无法验证命令时阻止其执行。

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

共享文件中每行对应一条域名规则（空行和以`#`开头的注释将被忽略）。若存在缺失或无法读取的文件，系统会记录警告，但不会因此禁用其他Web工具。

该策略会被缓存30秒，因此配置更改无需重启即可立即生效。

## 智能审批功能

可控制Hermes如何处理可能存在危险的命令：

```yaml
approvals:
  mode: smart   # smart | manual | off
```

| 模式 | 行为 |
|------|------|
| `smart`（默认值） | 使用辅助大语言模型来判断被标记的命令是否真的具有危险性。低风险命令将仅针对该命令自动获得批准；真正危险的命令则会被拒绝；若判断结果不确定，则会将问题提交给用户决策。 |
| `manual` | 在执行任何被标记的命令之前先向用户发起确认提示。在命令行界面中会显示交互式审批对话框；在消息交互模式下则会将待处理的审批请求放入队列中。 |
| `off` | 跳过所有审批检查。此设置等同于 `HERMES_YOLO_MODE=true`。**请谨慎使用。** |

智能模式对于减少审批疲劳尤为有效——它能让智能体在安全操作上更加自主地工作，同时仍能拦截真正具有破坏性的命令。

:::warning
将 `approvals.mode` 设置为 `off` 会禁用终端命令的所有安全检查。仅可在受信任的沙箱环境中使用此设置。
:::

### 拒绝断路器机制

`approvals.denial_breaker_threshold`（默认值为 `3`）用于防止智能体反复尝试那些经智能审批机制判定为危险的命令变体——每次尝试都会消耗一次辅助大语言模型的调用资源。当在单次会话中出现连续多次拒绝后，系统会发出强制停止指令，要求智能体立即停止操作、报告被拦截的操作，并请求用户手动执行或输入 `/approve` 进行批准。任何一次批准操作都会重置计数；如需禁用此功能，可将该值设置为 `0`：

```yaml
approvals:
  denial_breaker_threshold: 3   # 0 disables the breaker
```

### 拒绝规则

`approvals.deny` 是一个包含通配符模式的列表，可无条件阻止匹配相应的终端命令——即便在 `--yolo`、`/yolo` 或 `mode: off` 模式下也是如此。它相当于内置的固定黑名单，但可供用户自行编辑。

```yaml
approvals:
  deny:
    - "git push --force*"
    - "*curl*|*sh*"
```

模式为不区分大小写的 fnmatch 通配符，在 YAML 中必须用引号括起来（单独出现的开头星号会导致解析错误）。详情请参阅[安全性——用户自定义拒绝规则](/user-guide/security#user-defined-deny-rules-approvalsdeny)。

### 自定义智能审批策略

`approvals.smart_policy` 允许您在智能审批审核器的指令基础上添加自定义规则。一旦设置，这些规则就会被加入守护者 LLM 的系统提示词中（位于可信通道内，绝不会与不可信的命令文本混在一起），这样您无需修改代码即可根据实际环境调整其判断标准。

```yaml
approvals:
  smart_policy: |
    Always ESCALATE commands that modify anything under /etc.
    APPROVE docker compose restarts in ~/deploys — they are routine here.
```


## 检查点功能

在执行可能破坏文件的操作之前，自动创建文件系统快照。详情请参阅[检查点与回滚](/user-guide/checkpoints-and-rollback)文档。

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
  compression_threshold_tokens: 0          # Optional absolute cap on a subagent's compaction trigger (>= 16000); 0 = off, children use the ratio threshold
  # request_overrides:                      # Per-child request settings sent on every subagent API call (all resolution branches).
  #   extra_body:                           # Merged into the request's extra_body — e.g. OpenRouter routing hints:
  #     provider:
  #       sort: throughput
  max_concurrent_children: 3                # Parallel children per batch (floor 1, no ceiling). Also via DELEGATION_MAX_CONCURRENT_CHILDREN env var.
  worktree_isolation: false                 # Give each child its own git worktree branched from HEAD (local backend + git repos only; inspired by Muse Code). See Subagent Delegation → Worktree Isolation.
  max_spawn_depth: 1                        # Delegation tree depth cap (1-3, clamped). 1 = flat (default): parent spawns leaves that cannot delegate. 2 = orchestrator children can spawn leaf grandchildren. 3 = three levels.
  orchestrator_enabled: true                # Global kill switch. When false, role="orchestrator" is ignored and every child is forced to leaf regardless of max_spawn_depth.
```

**子代理提供者与模型覆盖：** 默认情况下，子代理会继承父代理的提供者与模型配置。若需将子代理指向不同的提供者-模型组合，可设置 `delegation.provider` 和 `delegation.model`——例如，在主代理使用成本高昂的推理模型处理复杂任务时，让子代理使用价格更低或响应更快的模型来处理范围较小的子任务。

**子代理回退链配置：** 通过设置 `delegation.fallback_providers`，可为各个工作节点指定独立的回退路径（其结构与顶层列表相同）。仅当某个子节点被明确指定（通过提供者、端点或模型标识）时，才会使用该独立的回退链；否则它将直接报错，而不会借用父代理的路由规则。对于未被明确指定的子节点，若未设置该参数或值为 `null`，则仍会沿用父代理的回退链。如需完全禁用子节点的回退功能，可在 `delegation:` 下设置 `fallback_providers: []`。

**直接端点覆盖：** 若希望使用自定义的端点路径，可直接设置 `delegation.base_url`、`delegation.api_key` 和 `delegation.model`。这样就能将子代理直接发送到该兼容 OpenAI 的端点，且该配置会优先于 `delegation.provider` 的设置。如果未指定 `delegation.api_key`，Hermes 将仅回退使用 `OPENAI_API_KEY`。即便同时设置了 `delegation.provider` 和 `delegation.base_url`，自定义的端点与密钥配置依然有效，不过该提供者的请求相关参数（如 `extra_body` 覆盖规则以及来自 `custom_providers` 的最大输出token数限制）仍会传递给子代理。

**每个子代理的请求设置（`request_overrides`）：** `delegation.request_overrides` 是一个字典，其中包含在每次子代理 API 调用时都会发送的请求设置。该字典的顶层键为 API 的关键字参数（例如 `service_tier`）；其中的 `extra_body` 子字典会合并到请求的 `extra_body` 中。这些设置会在**三种**解析路径中均被生效——直接使用 `base_url`、指定 `provider`，以及纯继承模式——因此该设置始终会起作用。优先级规则为：显式的 `request_overrides` 值会**覆盖**任何在运行时或由父级生成的覆盖值；顶层显式键的优先级最高，而 `extra_body` 会进行深度合并，因此运行时定义的 `extra_body` 键（例如某个 provider 的 `thinking: {type: disabled}` 个性设置）会保留下来，除非有对应的键对其进行了重新定义。其典型应用场景是为委托处理的子代理提供 OpenRouter 路由提示。

```yaml
delegation:
  model: "deepseek/deepseek-v4-flash-0731"
  base_url: "https://openrouter.ai/api/v1"
  api_key: "sk-or-..."
  request_overrides:
    extra_body:
      provider:
        sort: throughput   # route children to the fastest OpenRouter provider
```
**消息传输协议（`api_mode`）：** Hermes会自动根据`delegation.base_url`来识别消息传输协议（例如，以 `/anthropic` 结尾的路径对应 `anthropic_messages` 协议；而 Codex、原生 Anthropic 或 Kimi-coding 平台的域名则保持原有的识别方式）。对于那些无法通过规则判断的端点——比如基于 Anthropic 架构的 Azure AI Foundry、MiniMax、Zhipu GLM 或 LiteLLM 代理服务器——需要手动将 `delegation.api_mode` 设置为 `chat_completions`、`codex_responses` 或 `anthropic_messages` 中的某一值。若保持为空（即默认值），则系统将继续使用自动识别功能。

该委托机制所使用的凭证解析方式与 CLI/gateway 启动时的方式相同，支持所有已配置的提供方：`openrouter`、`nous`、`copilot`、`zai`、`kimi-coding`、`minimax`、`minimax-cn`。一旦指定了某个提供方，系统便会自动确定对应的基准 URL、API 密钥及 API 模式，无需手动配置凭证信息。

**优先级规则：** 首先优先考虑配置中的 `delegation.base_url`，其次是配置中的 `delegation.provider`，再者为继承自父级的提供方。配置中的 `delegation.model` 则会继承自父级模型。如果仅指定 `model` 而未指定 `provider`，则仅会更改模型名称，凭证信息仍会沿用父级设置（这有助于在相同提供方如 OpenRouter 内切换不同模型）。

**宽度与深度：** `max_concurrent_children` 用于限制每批次中可并行运行的子代理数量（默认值为 `3`，下限为 `1`，无上限）。该参数也可通过 `DELEGATION_MAX_CONCURRENT_CHILDREN` 环境变量进行设置。当模型提交的 `tasks` 数组超过此限制时，`delegate_task` 会返回说明该限制的工具错误信息，而不会默默地进行截断处理。`max_spawn_depth` 则用于控制委托树的结构深度（范围被限制在 `1` 至 `3` 之间）。在默认值 `1` 的情况下，委托结构为扁平型：子代理无法生成孙代理；若传入 `role="orchestrator"`，则该角色会自动降级为 `leaf` 类型。将此值设置为 `2` 可让调度器子代理能够生成 `leaf` 类型的孙代理；设置为 `3` 则可构建三层结构的委托树。代理会在每次调用时通过设置 `role="orchestrator"` 来选择是否启用调度功能；而若设置 `orchestrator_enabled: false`，则无论何种情况所有子代理都会被强制降级为 `leaf` 类型。计算成本呈倍数增长关系——在 `max_spawn_depth: 3` 且 `max_concurrent_children: 3` 的条件下，该委托树最多可同时运行 3×3×3 = 27 个 `leaf` 类型的代理。有关具体使用方式，请参阅 [子代理委托 → 深度限制与嵌套调度](features/delegation.md#depth-limit-and-nested-orchestration) 文档。

**子进程通知：** 由子代理启动的后台进程会将它们的完成状态或监控通知发送至父对话，但这些通知默认会在父对话中被**抑制**——最终呈现的结果仅为子进程的综合输出。如需显示这些通知（并标注出对应的子代理），请设置 `delegation.surface_child_process_notifications: true`。而委托处理的结果本身则永远不会被抑制。详情请参阅[子代理委托 → 子进程后台通知](features/delegation.md#child-background-process-notifications)。

## 澄清问题

用于配置网关在等待对澄清问题的回复时所等待的时间。标准键名为 `agent.clarify_timeout`（默认值为3600秒）；如果明确设置了旧版顶层键名 `clarify.timeout`，该值仍会被优先采用：

```yaml
agent:
  clarify_timeout: 3600        # Seconds to wait for user clarification response (0 or less = unlimited)
```

## 上下文文件（SOUL.md、AGENTS.md）

Hermes 支持两种不同的上下文作用域：

| 文件 | 用途 | 作用域 |
|------|------|-------|
| `SOUL.md` | **代理的主要身份标识**——用于定义该代理的身份（系统提示词中的第1个槽位） | `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md` |
| `.hermes.md` / `HERMES.md` | 项目特定的指令（优先级最高） | 从项目根目录开始查找 |
| `AGENTS.md` | 项目特定的指令及编码规范 | 递归遍历目录结构 |
| `CLAUDE.md` | Claude Code 的上下文文件（也会被识别） | 仅限当前工作目录 |
| `.cursorrules` | Cursor IDE 规则文件（也会被识别） | 仅限当前工作目录 |
| `.cursor/rules/*.mdc` | Cursor 规则文件（也会被识别） | 仅限当前工作目录 |

- **SOUL.md** 是代理的核心身份标识，它占据系统提示词中的第1个槽位，会完全替代内置的默认身份。通过编辑该文件即可完全自定义代理的身份。
- 如果不存在、内容为空或无法加载 `SOUL.md`，Hermes 会回退到内置的默认身份。
- **项目上下文文件采用优先级机制**——只会加载其中一种类型（第一个匹配到的生效）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。而 `SOUL.md` 始终会独立加载。
- **AGENS.md` 具有层级结构**：如果子目录中也存在 `AGENTS.md`，则所有内容会合并在一起。
- 如果系统中没有默认的 `SOUL.md`，Hermes 会自动创建一个。
- 所有被加载的上下文文件的长度都会受到 `context_file_max_chars` 参数的限制（默认为20,000字符），超过限制时会自动进行智能截断。

相关内容：
- [个性与灵魂设置.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)

## 工作目录

| 上下文来源 | 默认值 |
|---------|---------|
| **CLI（`hermes`）** | 运行命令的当前目录 |
| **消息网关** | `~/.hermes/config.yaml` 文件中的 `terminal.cwd`；若未设置，则为家目录 `~` |
| **Docker / Singularity / Modal / SSH** | 容器或远程机器内的用户家目录 |

可覆盖工作目录：
```yaml
# In ~/.hermes/config.yaml:
terminal:
  cwd: /home/myuser/projects
```

`~/.hermes/.env` 文件中的 `MESSAGING_CWD` 以及直接的 `TERMINAL_CWD` 设置仅作为旧版本兼容性的回退选项。新的配置应使用 `terminal.cwd`。

## 网络

用于解决向外发送 HTTP 请求时连接问题的变通方案：

```yaml
network:
  force_ipv4: false   # Force IPv4 for outbound connections (default: false)
```

`force_ipv4` — 对于那些 IPv6 功能异常或无法访问的服务器，Python 会首先尝试解析 AAAA 记录，且在触发完整的 TCP 超时之前可能一直处于等待状态，之后才会回退到 IPv4。将此参数设置为 `true` 即可完全跳过 IPv6，直接通过 IPv4 建立连接。

## 入门引导

提供首次使用的引导提示以及结构化的配置信息填写帮助：

```yaml
onboarding:
  profile_build: "ask"   # "ask" (default) | "off"
  seen: {}               # internal latch — leave empty
```

- `profile_build` — 控制在首个网关消息中展示的档案构建选项。默认值为 `"ask"`，即提议构建用户档案；该选项为**可选且需获得用户同意**——智能体会在执行任何查询前先征得用户许可，绝不会偷偷读取用户的关联账户信息。设置为 `"off"` 时则仅显示简单的介绍内容。该提议最多只会展示一次。
- `seen` — 内部状态。Hermes 会记录此处显示过的每一条提示，以避免其再次出现；档案构建提议在首次展示后也会被记录于此。请勿手动编辑此字段——若希望重新查看所有提示，可直接删除整个 `onboarding` 部分。

## 控制面板

用于配置[网页控制面板](/user-guide/features/web-dashboard)的参数，包括视觉主题、公开网址以及身份验证提供商。关于 OAuth、基本密码认证和 Drain 认证提供商的详细信息可在网页控制面板页面中找到，其配置格式即为 `config.yaml`。

```yaml
dashboard:
  theme: "default"            # "default" | "midnight" | "ember" | "mono" | "cyberpunk" | "rose"
  show_token_analytics: false # Re-enable the (local-estimate-only) token/cost analytics surfaces
  public_url: ""              # Full public authority for OAuth redirect_uri (env: HERMES_DASHBOARD_PUBLIC_URL)
  trusted_proxies: []         # Proxy IPs/CIDRs allowed to supply X-Forwarded-* headers
  oauth:                      # Portal OAuth gate (engaged with --host and not --insecure)
    client_id: ""             # agent:{instance_id} — Portal provisions this
    portal_url: ""            # blank → plugin default (production Portal)
  basic_auth:                 # Self-hosted username/password gate (dashboard_auth/basic plugin)
    username: ""              # blank → plugin no-op
    password_hash: ""         # scrypt$... (preferred — no plaintext at rest)
    password: ""              # plaintext fallback (hashed in-memory at load)
    secret: ""                # token-signing key; blank → random per-process
    session_ttl_seconds: 0    # 0 → plugin default (12h)
  drain_auth:                 # Drain-control service-credential gate (dashboard_auth/drain plugin)
    scope: "drain"            # capability label on the verified principal
    min_secret_chars: 43      # entropy bar (url-safe-b64 chars; 43 ≈ 256 bits)
  ws_ping_interval: 20.0      # Non-loopback WebSocket keepalive ping interval (seconds)
  ws_ping_timeout: 20.0       # Non-loopback WebSocket keepalive pong timeout (seconds)
  ws_orphan_reap_grace_s: 20.0 # Grace before a WS-detached session is reaped (seconds)
  ssh_isolated_idle_grace_s: 900.0 # Desktop-over-SSH backend exits after this long with no client and no running turn
  ws_orphan_activity_stale_s: 600.0 # Activity idle bound before a detached RUNNING turn is interrupted (seconds)
  startup_orphan_sweep: true  # Close session rows orphaned by a dead gateway process at boot
```

- `theme` — 仪表板视觉主题。  
- `show_token_analytics` — 默认值为关闭。分析页面以及代币使用量和成本数据仅为**本地下限估算值**（未包含辅助调用、重试操作、备用方案及缓存写入等），因此实际数值可能会远低于供应商的账单金额。仅在你明确知晓这些数据并不计入账单时，才将此选项设置为 `true`。  
- `public_url` — 设置该参数后，即可指定用于构建 OAuth `redirect_uri` 的完整地址格式（包括协议、主机及可选的路径前缀）。对于那些无法可靠转发 `X-Forwarded-*` 请求头的反向代理环境，建议设置此参数。若不设置，则系统会尝试通过代理请求头信息来重建地址。  
- `trusted_proxies` — 允许提供 `X-Forwarded-Proto` 和 `X-Forwarded-For` 参数的 IP 地址或限定范围的 CIDR 网络。回环接口始终会被自动视为可信。当 TLS 反向代理从其他容器或主机发起连接时，需配置此参数。建议使用代理的精确 IP 地址；仅在其地址动态变化时才可使用小型专用网络。通配符及 `/0` 形式的网络将被拒绝。  
- `oauth` / `basic_auth` / `drain_auth` — 由内置的仪表板认证插件读取的认证提供方配置。实际用于认证的密钥**并不**在此处设置，而是通过 `HERMES_DASHBOARD_DRAIN_SECRET` 环境变量来指定。有关完整的认证设置流程，请参阅 [Web 仪表板](/user-guide/features/web-dashboard) 文档。
- `ws_ping_interval` / `ws_ping_timeout` — 用于非回环地址绑定的 WebSocket 保持连接参数调整（回环连接无需发送探测信号）。在延迟较高的连接环境中（如 Tailscale 或远程 SSH 隧道），默认的 20 秒间隔可能会导致不必要的 1006 类断开错误，此时应适当提高这些数值。  
- `ssh_isolated_idle_grace_s`（默认值为 `900`）—— 通过 SSH 连接的、由桌面端管理的 `hermes serve --isolated` 后端会被刻意与 SSH 会话分离，这样在连接过程中笔记本进入睡眠状态时，该后端也不会被强制终止。此前，每次从低电量模式唤醒并重新连接时，都可能导致另一个后端继续持有 `state.db` 文件。现在，当没有客户端 WebSocket 连接且没有正在运行的任务轮次时，该后端会自动退出（任务轮次或无法读取的任务状态均可使其保持活跃）。如果需要让独立运行的后端在笔记本睡眠后继续处理长时间运行的任务，可适当提高此值。此类后端还会以较低的频率发送 WebSocket 探测信号（间隔 60 秒，超时时间为 10 分钟），以便及时发现半开放的隧道连接。  
- `ws_orphan_reap_grace_s` — WebSocket 连接断开后的会话在被“孤儿清理机制”回收之前等待的时间。如果客户端重新连接的速度较慢，可配合调整保持连接参数一同提高此值。系统还会定期对会话进行维护，自动清理已关闭的套接字，并重新启动失效的孤儿清理计时器，因此即使初始清理操作或计时器出现异常，独立的聊天会话也不会因此失去其占用状态。客户端重新连接后会取消该计时器；而正在处理的委托任务及正常运行的任务轮次仍会受到常规孤儿清理机制的保护。（`HERMES_TUI_WS_ORPHAN_REAP_GRACE_S` 保留作为内部覆盖参数使用。）
- `ws_orphan_activity_stale_s`（默认值为 `600`）——表示一个已断开的**正在运行**的轮次的活动计时器（即 `agent.turn_liveness` 监控机制所采集的数据来源：API 请求等待时间、流式消息令牌、工具心跳信号等）需要处于空闲状态多久后，才会被“孤儿清理机制”中断。对于那些虽无客户端连接但仍持续生成数据的轮次，会继续在离线状态下运行至结束——关闭笔记本电脑、将移动应用置于后台，或是进行桌面系统更新，都不会中断这些正常运行的长时轮次；只有真正陷入僵局的轮次才会被中断。将此值设置为 `0` 可以在任何时间点立即中断该轮次，无论其活动状态如何（即恢复旧有的行为）。
- `startup_orphan_sweep`（默认值为 `true`）——由于上述的 WS 孤儿清理定时器是在进程内部运行的，因此如果在它触发之前网关发生重启（如系统更新、崩溃或 systemd 事件），该会话记录将会永久保留——从而导致 `/resume` 页面及控制面板中出现虚假的“活跃”任务状态。在每次网关启动时——无论是标准输入 TUI 界面（`entry.main`）还是桌面/控制面板的 WebSocket 辅助进程（`handle_ws`）——那些来源为 `tui`、`desktop` 或 `subagent`，且其启动时间与最新消息时间均早于会话超时时间（`HERMES_TUI_SESSION_TTL_S`，默认值为 6 小时）的会话记录，都会被以 `end_reason: startup_orphan_reap` 作为原因予以关闭。基于消息平台的会话（如 Telegram、Discord 等）不会受到影响，已经恢复连接的实时内存会话也会被排除在外，而被清理的会话仍可重新恢复。
