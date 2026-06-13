---
sidebar_position: 2
---

# 配置文件：运行多个 Agent

可在同一台机器上运行多个独立的 Hermes Agent——每个 Agent 都拥有独立的配置、API 密钥、内存、会话、技能以及网关状态。

## 什么是配置文件？

配置文件实际上是一个独立的 Hermes 主目录。每个配置文件都会拥有自己的目录，其中包含对应的 `config.yaml`、`.env`、`SOUL.md` 文件，以及内存数据、会话记录、技能模块、定时任务和状态数据库。通过配置文件，你可以为不同用途运行独立的 Agent——比如代码助手、个人智能助手或研究专用 Agent——而不会导致 Hermes 的状态相互混淆。

创建配置文件后，它便会自动成为一个独立的命令。例如，如果你创建了一个名为 `coder` 的配置文件，那么就可以直接使用 `coder chat`、`coder setup`、`coder gateway start` 等命令来操作它。

## 快速入门

```bash
hermes profile create coder       # creates profile + "coder" command alias
coder setup                       # configure API keys and model
coder chat                        # start chatting
```

就这样。`coder` 现在已拥有独立的 Hermes 配置文件，具备专属的配置、内存和状态。

## 创建配置文件

:::tip
最快捷的设置方式：在新配置文件中运行 `hermes setup --portal`，即可一次性连接模型与工具。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

### 空配置文件

```bash
hermes profile create mybot
```

它会创建一个包含预置技能的全新配置文件。请运行 `mybot setup` 命令来设置 API 密钥、模型以及网关令牌。

如果您打算将此配置文件用作看板任务执行者（或希望看板调度器能将任务分配给它），请在创建时添加 `--description "<角色名>"` 参数，以便调度器了解它的功能特点。

```bash
hermes profile create researcher --description "Reads source code and external docs, writes findings."
```

您也可以稍后使用 `hermes profile describe` 命令来设置或自动生成描述——有关完整的路由模型说明，请参阅 [Kanban 指南](./features/kanban#auto-vs-manual-orchestration)。 

### 仅克隆配置 (`--clone`)

```bash
hermes profile create work --clone
```

将当前配置文件中的 `config.yaml`、`.env` 以及 `SOUL.md` 复制到新配置文件中。API 密钥和模型保持不变，但会生成全新的会话状态与内存环境。如需更换 API 密钥，请编辑 `~/.hermes/profiles/work/.env` 文件；如需调整智能体性格，则需修改 `~/.hermes/profiles/work/SOUL.md` 文件。

### 全量克隆（`--clone-all`）

```bash
hermes profile create backup --clone-all
```

会复制**所有内容**——配置文件、API密钥、角色设定、所有记忆数据、技能、定时任务以及插件，相当于一个完整可用的快照。但各个人物档案的独立历史记录将被排除在外（如会话历史、`state.db`、`backups/`、`state-snapshots/`、`checkpoints/`），因为这些属于原始人物档案，其大小可能高达数十GB。若需包含历史记录的完整备份，请使用 `hermes profile export` 或 `hermes backup` 命令。 

### 从特定人物档案克隆

```bash
hermes profile create work --clone --clone-from coder
```

:::提示 Honcho 内存管理与配置文件功能  
当启用 Honcho 后，`--clone` 选项会自动为新配置文件创建一个专用的 AI 对等体，同时共享相同的用户工作空间。每个配置文件都会独立构建自身的观察结果与身份标识。详情请参阅 [Honcho -- 多智能体/配置文件功能](./features/memory-providers.md#honcho)。  
:::

## 配置文件的使用方法

### 命令别名  
每个配置文件都会在 `~/.local/bin/<名称>` 路径下自动生成一个命令别名：

```bash
coder chat                    # chat with the coder agent
coder setup                   # configure coder's settings
coder gateway start           # start coder's gateway
coder doctor                  # check coder's health
coder skills list             # list coder's skills
coder config set model.default anthropic/claude-sonnet-4
```

该别名适用于所有 Hermes 子命令——实际上其底层实现就是 `hermes -p <name>`。

### `-p` 标志

您也可以在任何命令中直接指定要使用的配置文件：

```bash
hermes -p coder chat
hermes --profile=coder doctor
hermes chat -p coder -q "hello"    # works in any position
```

### 固定默认设置（`hermes profile use`）

```bash
hermes profile use coder
hermes chat                   # now targets coder
hermes tools                  # configures coder's tools
hermes profile use default    # switch back
```

设置默认值后，普通的 `hermes` 命令就会以该配置文件为目标。其用法类似于 `kubectl config use-context`。

### 了解当前所处的配置环境

CLI 会始终显示当前激活的配置文件：

- **提示符**：显示为 `coder ❯`，而非普通的 `❯`
- **启动横幅**：在程序启动时会显示 `Profile: coder`
- **`hermes profile` 命令**：可显示当前配置文件的名称、路径、模型信息以及网关状态

## 配置文件、工作空间与沙箱机制的区别

配置文件常被误认为是工作空间或沙箱，但实际上它们是不同的概念：

- **配置文件**为 Hermes 提供独立的状态存储目录，用于保存 `config.yaml`、`.env`、`SOUL.md` 文件、会话记录、内存数据、日志信息、定时任务以及网关状态。
- **工作空间**或**当前工作目录**是终端命令的起始点，这一设置通过 `terminal.cwd` 参数独立控制。
- **沙箱机制**用于限制对文件系统的访问权限，而配置文件本身并不具备对智能体的沙箱隔离功能。

在默认的 `local` 终端后端中，智能体仍拥有与用户账户相同的文件系统访问权限。配置文件无法阻止其访问配置目录之外的文件夹。

如果希望让智能体在特定的项目文件夹中启动，可在该配置文件的 `config.yaml` 中明确设置绝对路径形式的 `terminal.cwd`：

```yaml
terminal:
  backend: local
  cwd: /absolute/path/to/project
```

在本地后端中使用 `cwd: "."` 指的是“Hermes 启动所在的目录”，而非“配置文件目录”。

还需注意以下几点：

- `SOUL.md` 可以为模型提供指导，但无法界定工作空间的边界。
- 对 `SOUL.md` 的修改会在新会话中立即生效，而现有会话可能仍使用旧的提示词状态。
- 询问模型“你当前位于哪个目录？”并非一种可靠的隔离测试方法。若需为工具设定可预测的起始目录，请显式设置 `terminal.cwd`。

## 运行网关

每个配置文件都会以独立进程的形式运行自己的网关，并拥有专属的机器人令牌：

```bash
coder gateway start           # starts coder's gateway
assistant gateway start       # starts assistant's gateway (separate process)
```

### 不同的机器人令牌

每个配置文件都拥有独立的 `.env` 文件。请在各自的文件中配置不同的 Telegram/Discord/Slack 机器人令牌。

```bash
# Edit coder's tokens
nano ~/.hermes/profiles/coder/.env

# Edit assistant's tokens
nano ~/.hermes/profiles/assistant/.env
```

### 安全性：令牌锁定机制

如果两个账号配置意外使用了相同的机器人令牌，第二个通道将会被阻断，并显示明确提示说明存在冲突的账号配置。该功能支持 Telegram、Discord、Slack、WhatsApp 和 Signal 平台。

### 持久化服务

```bash
coder gateway install         # creates hermes-gateway-coder systemd/launchd service
assistant gateway install     # creates hermes-gateway-assistant service
```

每个配置文件都会拥有独立的服務名称，并且以独立的方式运行。

:::note 在官方 Docker 镜像中
针对不同配置文件的网关由 [s6-overlay](https://github.com/just-containers/s6-overlay)（容器中的 PID 1）进行监控。因此，执行 `hermes profile create <name>` 命令时，系统会自动在 `/run/service/gateway-<name>/` 下创建一个 s6 服務槽位。而 `hermes -p <name> gateway start/stop/restart` 命令则会调用 `s6-svc`，而不会直接启动独立进程——如此一来，即便程序出现崩溃也会自动重启，同时 `docker restart` 命令也能保留之前正在运行的网关集合。详情请参阅 [针对不同配置文件的网关监控](/user-guide/docker#per-profile-gateway-supervision)。
:::

## 配置配置文件

每个配置文件都包含以下独立文件：

- **`config.yaml`** — 模型、提供方、工具集以及所有设置
- **`.env`** — API 密钥、机器人令牌
- **`SOUL.md`** — 个性设定与操作指令

```bash
coder config set model.default anthropic/claude-sonnet-4
echo "You are a focused coding assistant." > ~/.hermes/profiles/coder/SOUL.md
```

如果您希望该配置文件在特定项目中默认生效，还需为其设置独立的 `terminal.cwd` 值：

```bash
coder config set terminal.cwd /absolute/path/to/project
```

### 通过控制面板操作

[Web 控制面板](features/web-dashboard.md#managing-multiple-profiles)是一个机器级界面，可通过侧边栏中的配置文件切换器来管理**任意**配置文件下的配置、API密钥、技能、MCP 以及模型——无需为每个配置文件单独设置控制面板。`coder dashboard`会自动跳转至已预选 `coder` 配置文件的机器级控制面板。控制面板的“聊天”标签页也会随切换器同步，在所选配置文件的首页下开启对话窗口。

注意：控制面板“配置文件”页面上的“设为活动状态”功能会作为默认值保留，适用于**后续的 CLI/gateway 运行**（其效果与 `hermes profile use` 相同）——若需通过控制面板编辑配置文件，请使用切换器。

## 更新操作

`hermes update`会一次性下载共享代码，并自动将新打包的技能同步到**所有**配置文件中：

```bash
hermes update
# → Code updated (12 commits)
# → Skills synced: default (up to date), coder (+2 new), assistant (+2 new)
```

用户自定义的技能绝不会被覆盖。

## 管理配置文件

```bash
hermes profile list           # show all profiles with status
hermes profile show coder     # detailed info for one profile
hermes profile rename coder dev-bot   # rename (updates alias + service)
hermes profile export coder   # export to coder.tar.gz
hermes profile import coder.tar.gz   # import from archive
```

## 删除配置文件

```bash
hermes profile delete coder
```

此操作将停止网关服务，移除 systemd/launchd 相关服务，删除命令别名，并清除所有配置文件数据。系统会要求您输入配置文件名称以确认操作。

如需跳过确认步骤，可使用 `--yes` 参数：`hermes profile delete coder --yes`

:::note
您无法删除默认配置文件（`~/.hermes`）。如需彻底清除所有内容，请使用 `hermes uninstall` 命令。
:::

## Tab自动补全功能

```bash
# Bash
eval "$(hermes completion bash)"

# Zsh
eval "$(hermes completion zsh)"
```

为实现持久化补全功能，请将该行添加到您的 `~/.bashrc` 或 `~/.zshrc` 文件中。该功能可自动补全 `-p` 后的配置文件名、配置文件下的子命令以及顶级命令。

## 工作原理

配置文件会使用 `HERMES_HOME` 环境变量。当您运行 `coder chat` 时，封装脚本会在启动 hermes 之前将 `HERMES_HOME` 设置为 `~/.hermes/profiles/coder`。由于代码库中的 119 个以上文件均通过 `get_hermes_home()` 函数来确定路径，因此 Hermes 的状态会自动限定在该配置文件的目录内——包括配置、会话、内存、技能、状态数据库、网关进程 ID、日志以及定时任务。

需要注意的是，这与终端的工作目录是分开的。工具的执行是从 `terminal.cwd`（或在本地后端中设置 `cwd: "."` 时的启动目录）开始的，而非自动从 `HERMES_HOME` 开始。

默认的配置文件即为 `~/.hermes` 本身。无需进行任何迁移操作——现有安装方式将保持完全一致。

## 以分发包的形式共享配置文件

您在一台机器上构建的配置文件可以打包为 **git 仓库**，然后通过一条命令即可在另一台机器上安装——无论是您自己的工作站、同事的笔记本电脑，还是社区用户的环境。该共享包中包含了 SOUL、配置、技能、定时任务以及 MCP 连接信息。而凭证、记忆内容及会话数据则仍保留在每台机器上。

```bash
# Install a whole agent from a git repo
hermes profile install github.com/you/research-bot --alias

# Update later when the author ships a new version (keeps your memories + .env)
hermes profile update research-bot
```

如需了解关于创建、发布、更新机制、安全模型以及应用场景的完整指南，请参阅**[Profile Distributions：共享整个 Agent](./profile-distributions.md)**。
