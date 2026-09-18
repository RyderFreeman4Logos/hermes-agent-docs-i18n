---
sidebar_position: 2
---

# 配置文件：运行多个 Agent

在同一台机器上运行多个独立的 Hermes Agent——每个 Agent 都拥有独立的配置、API 密钥、内存、会话、技能以及网关状态。

## 什么是配置文件？

配置文件实际上是一个独立的 Hermes 主目录。每个配置文件都会拥有自己的目录，其中包含对应的 `config.yaml`、`.env`、`SOUL.md` 文件，以及内存数据、会话记录、技能模块、定时任务和状态数据库。通过配置文件，你可以为不同的用途运行独立的 Agent——比如代码助手、个人智能机器人或研究专用 Agent——而不会导致 Hermes 的状态相互混淆。

:::caution 为每个 Agent 创建独立的配置文件
切勿让两个 Agent 进程指向同一个配置文件（即同一个 Hermes 主目录）。由于两者都会自动写入内存，且在会话开始时会将对方的写入内容加载到自身的系统提示词中，因此在一个主目录下存在两个写入进程会导致它们的状态不断叠加，最终完全偏离初始设定。配置文件的存在正是为了解决这一问题；需要共享内存的 Agent 应该使用[外部内存提供器](/user-guide/features/memory-providers)。
:::

创建配置文件后，它就会自动成为一个独立的命令。例如，如果你创建了一个名为 `coder` 的配置文件，那么就可以直接使用 `coder chat`、`coder setup`、`coder gateway start` 等命令来操作它。

## 快速入门

```bash
hermes profile create coder       # creates profile + "coder" command alias
coder setup                       # configure API keys and model
coder chat                        # start chatting
```

就是这样。现在，`coder` 已成为一个独立的 Hermes 配置文件，拥有自己的配置、内存和状态。

## 创建配置文件

:::tip
最快捷的设置方式：在新配置文件中运行 `hermes setup --portal`，即可一次性连接模型与工具。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

### 空配置文件

```bash
hermes profile create mybot
```

该操作会创建一个已预置了相关技能的新配置文件。请运行 `mybot setup` 命令来设置 API 密钥、模型以及网关令牌。

如果您打算将此配置文件用作看板任务执行者（或希望看板调度器能将任务分配给它），请在创建时添加 `--description "<角色名>"` 参数，以便调度器了解其擅长的功能。

```bash
hermes profile create researcher --description "Reads source code and external docs, writes findings."
```

您也可以稍后使用 `hermes profile describe` 命令来设置或自动生成描述——有关完整的路由模型信息，请参阅 [Kanban 指南](./features/kanban#auto-vs-manual-orchestration)。 

### 仅克隆配置（`--clone`）

```bash
hermes profile create work --clone
```

将当前配置文件中的 `config.yaml`、`.env`、`SOUL.md` 以及技能复制到新配置文件中。虽然 API 密钥、模型及功能保持不变，但会生成全新的会话状态与内存记录。如需使用不同的 API 密钥，请编辑 `~/.hermes/profiles/work/.env` 文件；如需改变智能体性格，则可修改 `~/.hermes/profiles/work/SOUL.md` 文件。

### 全量克隆（`--clone-all`）

```bash
hermes profile create backup --clone-all
```

会复制**所有内容**——配置文件、API密钥、角色设定、所有记忆、技能以及插件，形成一份完整的可用快照。但各个人工智能配置文件对应的独立历史记录将被排除在外（如会话历史、`state.db`、`backups/`、`state-snapshots/`、`checkpoints/`），因为这些数据属于原配置文件，其体积可能高达数十GB。**定时任务也不会被复制**：这类任务是与原配置文件及其分发渠道绑定在一起的调度任务，若克隆后也继承了这些任务，会导致每个任务被执行两次（因为存在两个网关，但任务ID相同）。新创建的配置文件初始时`cron/`目录是空的。如需进行包含历史记录和定时任务的完整备份，请使用`hermes profile export`或`hermes backup`命令。

:::注意 OAuth登录信息是共享而非复制
Anthropic（Claude Pro/Max）、OpenAI Codex以及xAI的OAuth登录方式使用的是**一次性刷新令牌**——复制一份令牌并不等同于获得第二组凭证，它实际上仍是同一组凭证，只是拥有者增加了。一旦第一个配置文件对令牌进行刷新，就会使其他所有副本的令牌失效。因此，`--clone-all`选项（以及控制面板中的凭证同步功能）会从克隆结果中删除这些OAuth相关的记录。新配置文件仍会从根目录`~/.hermes/auth.json`中读取登录信息，且在任何配置文件内进行的令牌刷新操作都会被写回根目录，从而确保所有配置文件都能保持登录状态。静态API密钥则如常会被复制。若希望某个配置文件拥有独立的OAuth登录账号，可在该配置文件内部运行命令`hermes -p <name> auth add <provider>`。
:::

### 从特定配置文件克隆

```bash
hermes profile create work --clone-from coder
```

`--clone-from <source>` 用于直接选择源配置文件，同时会同步克隆其配置、技能及 SOUL 数据。若需完整复制该源配置文件的内容，可将其与 `--clone-all` 选项一起使用：

```bash
hermes profile create work-backup --clone-from coder --clone-all
```

:::提示 Honcho 内存管理与配置文件
启用 Honcho 后，克隆操作会自动为新配置文件创建一个专用的 AI 对等体，同时共享相同的用户工作空间。每个配置文件都会构建属于自己的观测数据与身份标识。详情请参阅 [Honcho -- 多智能体/配置文件](./features/memory-providers.md#honcho)。
:::

## 使用配置文件

### 命令别名
每个配置文件都会在 `~/.local/bin/<名称>` 目录下自动生成一个命令别名：

```bash
coder chat                    # chat with the coder agent
coder setup                   # configure coder's settings
coder gateway start           # start coder's gateway
coder doctor                  # check coder's health
coder skills list             # list coder's skills
coder config set model.default anthropic/claude-sonnet-4
```

该别名适用于所有 Hermès 子命令——实际上其底层实现就是 `hermes -p <name>`。

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

设置默认值后，普通的 `hermes` 命令将针对该配置文件运行，其作用类似于 `kubectl config use-context`。

### 了解当前所处的环境

CLI 会始终显示当前激活的配置文件：

- **提示符**：显示为 `coder ❯`，而非普通的 `❯`
- **启动横幅**：在程序启动时会显示 `Profile: coder`
- **`hermes profile` 命令**：可显示当前配置文件的名称、路径、模型信息以及网关状态

## 配置文件、工作空间与沙箱机制的区别

配置文件常被误认为是工作空间或沙箱，但实际上它们是不同的概念：

- **配置文件**为 Hermes 提供独立的状态存储目录，用于保存 `config.yaml`、`.env`、`SOUL.md` 文件、会话记录、内存数据、日志信息、定时任务以及网关状态。
- **工作空间**或**当前工作目录**是终端命令的起始点，这一设置通过 `terminal.cwd` 参数独立控制。
- **沙箱机制**用于限制对文件系统的访问权限，而配置文件本身并不具备对智能体的沙箱隔离功能。

在默认的 `local` 终端后端中，智能体仍拥有与用户账户相同的文件系统访问权限。配置文件无法阻止其访问配置文件目录之外的文件夹。

如果希望让智能体在特定的项目文件夹中启动，可在该配置文件的 `config.yaml` 中明确设置绝对路径形式的 `terminal.cwd`：

```yaml
terminal:
  backend: local
  cwd: /absolute/path/to/project
```

在本地后端中使用 `cwd: "."` 指的是“Hermes 启动时的目录”，而非“配置文件目录”。

另请注意：

- `SOUL.md` 可以为模型提供指导，但无法强制界定工作空间边界。
- 对 `SOUL.md` 的修改会在新会话中立即生效，而现有会话可能仍使用旧的提示词状态。
- 询问模型“你当前处于哪个目录？”并非一种可靠的隔离测试方法。若需为工具设定可预测的起始目录，请显式设置 `terminal.cwd`。

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

如果两个账号配置意外使用了相同的机器人令牌，第二个通道将会被阻断，并显示明确错误信息指出存在冲突的账号配置。该功能支持 Telegram、Discord、Slack、WhatsApp 以及 Signal 平台。

### 持久化服务

```bash
coder gateway install         # creates hermes-gateway-coder systemd/launchd service
assistant gateway install     # creates hermes-gateway-assistant service
```

每个配置文件都有独立的服务名称，且这些服务会独立运行。

:::note 在官方 Docker 镜像中
针对不同配置文件的网关由 [s6-overlay](https://github.com/just-containers/s6-overlay)（容器中的 PID 1）进行监控。因此，执行 `hermes profile create <name>` 命令时，系统会自动在 `/run/service/gateway-<name>/` 下创建一个 s6 服务实例。而使用 `hermes -p <name> gateway start/stop/restart` 命令时，系统会调用 `s6-svc` 工具而非直接启动新进程——如此一来，即便出现故障也能自动重启；同时执行 `docker restart` 命令也能保留之前正在运行的网关集合。详情请参阅 [针对不同配置文件的网关监控机制](/user-guide/docker#per-profile-gateway-supervision)。
:::

## 配置文件设置

每个配置文件都包含以下独立文件：

- **`config.yaml`** — 模型、提供者、工具集以及所有相关设置
- **`.env`** — API 密钥、机器人令牌
- **`SOUL.md`** — 个性设定与操作指令

```bash
coder config set model.default anthropic/claude-sonnet-4
echo "You are a focused coding assistant." > ~/.hermes/profiles/coder/SOUL.md
```

如果希望该配置文件在特定项目中默认生效，还需为其设置独立的 `terminal.cwd` 值：

```bash
coder config set terminal.cwd /absolute/path/to/project
```

### 通过控制面板操作

[Web 控制面板](features/web-dashboard.md#managing-multiple-profiles)是一个机器级界面，用户可通过侧边栏中的配置文件切换器来管理**任意**配置文件下的配置、API密钥、技能、MCP以及模型——无需为每个配置文件单独设置控制面板。`coder dashboard`会自动跳转至已预选`coder`配置文件的机器级控制面板。控制面板的“聊天”标签页也会随切换器同步，在所选配置文件的首页下开启对话窗口。

注意：控制面板“配置文件”页面上的“设为活动状态”功能会作为默认设置保留，适用于**后续的 CLI/gateway 运行**（其效果与`hermes profile use`相同）——若需从控制面板编辑配置文件，请使用切换器。

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
hermes profile export coder   # pack into coder.tar.gz (shareable; keys stripped)
hermes profile import coder.tar.gz   # install an archive as a new profile
```

在聊天界面中，对应的操作为 `/export` 和 `/import`；而在桌面应用中，则可通过 **⌘K → Export/Import profile…** 来执行。详情请参阅[共享配置文件](#sharing-a-profile)。

### 默认配置文件的命名

默认配置文件的内部标识始终为 `default`——由于 `~/.hermes` 是安装根目录，因此无法真正更改其名称。实际上，重命名操作只是设置一个**显示名称**，UI界面会使用该名称来替代原始的标识符：

```bash
hermes profile rename default Harumesu   # Unicode fine: 小助手
```

显示名称会出现在 `hermes profile list`/`show` 命令、`/profile chat` 命令、控制面板以及桌面应用程序中（包括机器人模式的人员列表）。该名称仅用于展示目的：在 `-p default` 模式下，服务名称、定时任务以及其他所有引用仍会使用标准的 `default` ID。该显示名称存储在 `~/.hermes/profile.yaml` 文件的 `display_name` 字段中；若要恢复原状，只需删除该行即可。带有名称的配置文件也可以设置 `display_name`（这样在真正重命名时该名称依然保留），但使用 `rename` 命令时仍会直接修改配置文件本身的名称。

## 删除配置文件

```bash
hermes profile delete coder
```

此操作将停止网关服务，移除 systemd/launchd 后台服务，删除命令别名，并清除所有配置文件数据。系统会要求您输入配置文件名称以确认操作。

如需跳过确认步骤，可使用 `--yes` 参数：`hermes profile delete coder --yes`

:::note
您无法删除默认配置文件（`~/.hermes`）。若要彻底清除所有内容，请使用 `hermes uninstall` 命令。
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

配置文件会使用 `HERMES_HOME` 环境变量。当您运行 `coder chat` 时，封装脚本会在启动 hermes 之前将 `HERMES_HOME` 设置为 `~/.hermes/profiles/coder`。由于代码库中的 119 个以上文件均通过 `get_hermes_home()` 函数来确定路径，因此 hermes 的状态会自动限定在对应配置文件的目录内——包括配置、会话、内存、技能、状态数据库、网关进程 ID、日志以及定时任务。

这一机制与终端工作目录是相互独立的。工具的执行起始点为 `terminal.cwd`（在本地后端中则为主启动目录），而非直接从 `HERMES_HOME` 开始。

在主机安装模式下，工具的子进程默认会保留您真实的操作系统用户 `HOME` 目录，因此 `~` 目录下的现有 CLI 凭据可在不同配置文件之间正常使用。配置文件数据是通过 `HERMES_HOME` 实现隔离的，而非通过修改 `HOME`。容器后端仍会使用 `{HERMES_HOME}/home` 作为工具状态的持久化存储位置；而对于需要严格实现每个配置文件独立工具配置的主机用户，则可通过设置 `terminal.home_mode: profile` 来启用该功能。

这就引出了两个容易混淆的概念：

- `HERMES_HOME` 是配置文件的边界，用于管理 Hermes 的配置文件、`.env` 文件、内存设置、会话信息、技能模块、日志记录、定时任务、网关状态以及其他相关数据。  
- `HOME` 则是外部 CLI 工具所期望的操作系统/用户主目录。在主机安装模式下，Hermes 会默认将其设置为真实用户的主目录，这样像 `git`、`ssh`、`gh`、`az`、`npm`、Claude Code 和 Codex 这样的工具就能使用与常规终端相同的凭据。

不过这种设计的代价是：默认情况下，不同配置文件会共享普通用户级别的 CLI 状态。如果需要为每个配置文件设置独立的 CLI 身份，可在该配置文件的 `config.yaml` 中设置 `terminal.home_mode: profile`。在此模式下，Hermes 会以 `HOME={HERMES_HOME}/home` 作为参数来启动工具子进程；此时就需要在该配置文件对应的主目录中创建或关联特定于该配置文件的 `~/.ssh`、`~/.gitconfig`、`~/.config/gh` 文件，以及云服务 CLI 认证信息、Claude/Codex 认证信息、npm 状态等相关文件。

此外，Hermes 还会向子进程暴露 `HERMES_REAL_HOME` 变量，这样在启用 `home_mode: profile` 模式时，脚本仍能获取到真实的用户主目录路径。

默认的配置文件即为 `~/.hermes` 本身，无需进行任何迁移操作——现有安装方式完全不受影响。

## 共享配置文件

在某台机器上创建的配置文件可以复制到其他设备上，比如自己的工作站、同事的笔记本电脑或社区共享平台。有两种实现方式：

**发送文件。** `/export` 命令会将配置文件及其相关内容打包成一个 `.tar.gz` 文件，其中包含技能模块、内存设置、角色设定、定时任务、插件、各种设置，以及（从桌面环境获取的）主题和布局信息。API 密钥则会被移除。接收方只需运行 `/import` 命令即可导入该配置文件。

```bash
# In chat, run /export, hand over the file, and they run /import on it
hermes profile export coder
hermes profile import ./coder.tar.gz --name coder
```

**发布分发包。** 将该配置文件打包为 **git 仓库**，这样接收方只需一条命令即可完成安装，之后还能随时拉取带版本号的更新内容。该仓库中包含 SOUL、配置文件、智能技能、定时任务以及 MCP 连接信息；而凭证、记忆数据及会话状态则仍保留在每台机器上。

```bash
# Install a whole agent from a git repo
hermes profile install github.com/you/research-bot --alias

# Update later when the author ships a new version (keeps your memories + .env)
hermes profile update research-bot
```

如需一次性移交或迁移代理，可使用导出文件；而对于需要持续推送的代理，则应使用分发功能。关于这两种方式的详细信息——包括对比表、创建流程、发布机制、更新规则以及安全模型——请参阅 **[Profile Distributions: 共享整个代理](./profile-distributions.md)**。
