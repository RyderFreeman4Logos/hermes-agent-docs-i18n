---
sidebar_position: 7
title: "Docker"
description: "Running Hermes Agent in Docker and using Docker as a terminal backend"
---

# Hermes Agent — Docker

Docker 与 Hermes Agent 的结合方式主要有两种：

1. **在 Docker 中运行 Hermes**——即让 Agent 本身在容器内部运行（本页主要介绍的内容）
2. **将 Docker 作为终端后端**——Agent 在主机上运行，但所有命令都在一个持久化的 Docker 沙箱容器中执行，该容器会在整个 Hermes 进程运行期间保持存在，从而跨越不同的工具调用、/new 操作以及子 Agent（详见 [配置 → Docker 后端](./configuration.md#docker-backend)）

本页介绍的是第一种方式。容器会将所有用户数据（配置、API 密钥、会话信息、技能及记忆内容）存储在从主机挂载到的 `/opt/data` 目录中。该镜像本身是无状态的，只需拉取新版本即可升级，而不会丢失任何配置。

## 快速开始

如果您是初次运行 Hermes Agent，请在主机上创建一个数据目录，然后以交互模式启动容器以运行设置向导：

:::caution 安装命令请避免使用基于浏览器的 VPS 控制台
某些 VPS 提供商（如 Hetzner Cloud 及其他几家）提供了用于管理主机的基于浏览器的控制台。这类控制台无法正确传输特殊字符——`:` 可能会被显示为 `;`，`@` 也可能出现显示错误，而非英语键盘布局的情况更为糟糕——这会导致 `-v ~/.hermes:/opt/data`、`-e KEY=value` 这类 `docker run` 命令参数以及粘贴的 API 密钥/令牌被悄悄破坏。

**建议通过 SSH 连接**（`ssh root@<host>`），这样可以安全地复制粘贴命令。如果必须使用浏览器控制台，请手动输入命令而非粘贴，并在按下回车键之前仔细检查结果中的每一个 `:`、`@`、`=` 和 `/`。
:::

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup
```

这将引导您进入设置向导，向导会要求您输入 API 密钥，并将其写入 `~/.hermes/.env` 文件中。此操作只需执行一次即可。强烈建议在此阶段为网关配置一个聊天系统，以便其正常工作。

:::提示
在容器内部运行一次 `hermes setup --portal` 命令——刷新令牌会保存在挂载的 `~/.hermes` 卷中。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 以网关模式运行

配置完成后，可在后台运行该容器，将其作为持久化网关使用（适用于 Telegram、Discord、Slack、WhatsApp 等平台）：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

端口 8642 用于暴露网关的 [兼容 OpenAI 的 API 服务器](./features/api-server.md)以及健康检查端点。如果您仅使用聊天平台（如 Telegram、Discord 等），则该端口为可选配置；但若希望仪表板或外部工具能够访问网关，则必须启用它。

:::提示 网关处于受监督运行状态
在官方 Docker 镜像中，`gateway run` 命令会**由 s6-overlay 自动进行监督**：一旦网关进程崩溃，系统会在几秒钟内自动重启该进程，且不会导致容器丢失。同时，当设置了 `HERMES_DASHBOARD=1` 时，仪表板也会一并受到监督。`gateway run` 命令本身的执行过程实际上是一个 `sleep infinity` 心跳机制，用于保持容器运行状态，而真正的网关进程则由 s6 来管理——因此即使执行 `docker stop`，所有服务也能干净地停止，且 `docker logs` 中仍会显示受监督运行的网关输出信息。

在 `docker logs` 中，您会看到一条确认升级完成的一行提示信息。如需取消此监督模式——并恢复“网关为容器的主进程，容器退出即表示网关退出”的传统运行逻辑——可以传递 `--no-supervise` 参数，或设置 `HERMES_GATEWAY_NO_SUPERVISE=1`。对于那些希望容器随网关的状态码一同退出的 CI 自动化测试而言，取消监督模式十分有用；但在生产环境部署中，默认的受监督运行模式显然更为稳妥。

此行为仅适用于基于 s6 的镜像。早期基于 tini 的镜像仍会将 `gateway run` 作为前台主进程来运行。
:::

:::注意 网关日志的存储位置
有关完整的日志路由规则（包括按配置文件划分的网关、仪表板、启动同步器以及整个容器的 `docker logs` 输出），请参阅下方的[日志存储位置](#where-the-logs-go)部分。
:::

:::注意 无人值守网关的工具调用循环强制终止功能
`tool_loop_guardrails.hard_stop_enabled` 的默认值为 `false`，这对于交互式 CLI 和 TUI 会话来说是合理的，因为用户可以直观地看到重复的工具调用警告。但在无人值守的网关或服务器部署中，仅靠警告可能无法阻止陷入工具调用循环的智能体。若需要具备断路器功能，操作人员应在配置文件的 `config.yaml` 中明确启用强制终止功能：

```yaml
tool_loop_guardrails:
  hard_stop_enabled: true
  hard_stop_after:
    exact_failure: 5
    idempotent_no_progress: 5
```
:::

注意：API服务器的运行需以`API_SERVER_ENABLED=true`为前提。若希望让容器内的该服务可被`127.0.0.1`之外的地址访问，还需设置`API_SERVER_HOST=0.0.0.0`以及`API_SERVER_KEY`（长度至少为8位——可通过`openssl rand -hex 32`命令生成）。示例如下：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  -e API_SERVER_ENABLED=true \
  -e API_SERVER_HOST=0.0.0.0 \
  -e API_SERVER_KEY="$(openssl rand -hex 32)" \
  -e API_SERVER_CORS_ORIGINS='*' \
  nousresearch/hermes-agent gateway run
```

在面向互联网的机器上开放任何端口都会带来安全风险。除非您充分了解相关风险，否则应避免这么做。

## 运行控制面板

内置的网页控制面板会以受监督的 s6-rc 服务形式运行，与网关一同存在于同一个容器中。如需启动该控制面板，请设置 `HERMES_DASHBOARD=1`：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  -p 9119:9119 \
  -e HERMES_DASHBOARD=1 \
  nousresearch/hermes-agent gateway run
```

该控制面板由 s6 进行监控——一旦其崩溃，`s6-supervise` 会在短暂的延迟后自动重启它。控制面板的标准输出/错误输出会被转发至 `docker logs <container>`（无需添加前缀；而网关自身的输出则存储在每个配置文件的 s6-log 文件中——详见下文的[日志存储位置](#where-the-logs-go)——因此这两类流不会相互冲突）。

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `HERMES_DASHBOARD` | 设置为 `1`（或 `true` / `yes`）可启用受监控的控制面板服务 | *(未设置——服务虽已注册但处于关闭状态)* |
| `HERMES_DASHBOARD_HOST` | 控制面板 HTTP 服务器的绑定地址 | `0.0.0.0` |
| `HERMES_DASHBOARD_PORT` | 控制面板 HTTP 服务器的端口 | `9119` |
| `HERMES_DASHBOARD_INSECURE` | **已废弃/无作用。** 该选项曾用于绕过认证机制；在2026年6月的安全强化措施之后，它已无法禁用身份验证。非回环绑定方式始终需要配置认证提供器 | *(会被忽略——请直接配置认证提供器)* |

容器内的控制面板默认绑定地址为 `0.0.0.0`——若不设置此值，则通过主机无法访问所公开的 `-p 9119:9119` 端口。如需将绑定限制在容器回环地址（适用于 sidecar 或反向代理架构），请设置 `HERMES_DASHBOARD_HOST=127.0.0.1`。

当同时满足以下两个条件时，控制面板的认证机制会自动启用：

1. 绑定地址为非回环地址（例如容器内的默认值 `0.0.0.0`），**且**
2. 已注册 `DashboardAuthProvider` 插件。

有三种内置方式可满足第二个条件：

- **用户名/密码**——对于运行在可信网络中或处于 VPN 后面的自托管/本地/家庭实验室容器而言，这是最简单的方式：设置 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` 和 `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`（如需确保会话在重启后仍保持有效，还需设置 `HERMES_DASHBOARD_BASIC_AUTH_SECRET`）。此方式不适用于直接暴露在公共互联网上的场景。
- **OAuth（Nous Portal）**——适用于托管型/公开部署场景：一旦设置了 `HERMES_DASHBOARD_OAUTH_CLIENT_ID`，`dashboard_auth/nous` 提供器就会自动启用。
- **自托管 OIDC**——通过标准的 OpenID Connect 方式使用您自己的身份提供器进行认证：当设置了 `HERMES_DASHBOARD_OIDC_ISSUER` 和 `HERMES_DASHBOARD_OIDC_CLIENT_ID` 时，`dashboard_auth/self_hosted` 提供器就会自动启用。

无论选择哪种方式，该认证机制都会在访问者尝试进入任何受保护页面之前将其重定向至登录页面。关于这三种提供器的详细信息，请参阅[Web 控制面板 → 认证](features/web-dashboard.md#authentication-gated-mode)。

如果未注册任何提供器且绑定地址为非回环地址，控制面板将在启动时直接失败，并显示指出缺失环境变量的具体错误信息。如今已不再存在允许在公共绑定地址下无认证访问控制面板的方案：`HERMES_DASHBOARD_INSECURE=1` 已被废弃且无实际作用（仅会记录警告并被忽略）。请配置相应的认证提供器，或设置 `HERMES_DASHBOARD_HOST=127.0.0.1`，然后通过 SSH 隧道或 Tailscale 来访问控制面板。

:::warning 为何移除 `--insecure` 参数
在2026年6月的 MCP配置持久化攻击事件中，未经认证的公共控制面板正是攻击者进入系统的入口：攻击者通过扫描公开的控制面板（以及 OpenAI API 服务器），迫使代理程序植入 SSH 密钥后门。如今，对于所有非回环绑定方式，认证机制已是强制要求。对于处于可信局域网或家庭实验室环境中的系统，内置的用户名/密码提供器（`HERMES_DASHBOARD_BASIC_AUTH_USERNAME` + `_PASSWORD`）则是无需额外配置即可满足该要求的方案。
:::

当控制面板在单独的容器中运行，且该容器与主机共享进程 ID 和网络命名空间时，也是支持的（例如使用 `network_mode: host` 模式，正如该项目的 `docker-compose.yml` 文件中所做的那样——可参考其中的 `dashboard` 服务）。由于网关的存活检测需要与网关进程共享进程 ID 命名空间，因此这一限制仅适用于那些运行在隔离的桥接网络容器中且未共享进程 ID 命名空间的控制面板。

## 交互式运行（CLI 聊天模式）

要针对正在运行的数据目录开启交互式聊天会话：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent
```

或者，如果您已经在正在运行的容器中打开了终端（例如通过 Docker Desktop），只需执行以下命令即可：

```sh
/opt/hermes/.venv/bin/hermes
```

## 持久卷

`/opt/data` 卷是所有 Hermes 状态的唯一真实来源。它对应于宿主机的 `~/.hermes/` 目录，其中包含以下内容：

| 路径 | 内容 |
|------|------|
| `.env` | API 密钥和敏感信息 |
| `config.yaml` | 所有 Hermes 配置 |
| `SOUL.md` | Agent 的个性/身份设定 |
| `sessions/` | 对话历史记录 |
| `memories/` | 持久内存存储区 |
| `skills/` | 已安装的技能 |
| `home/` | 供 Hermes 工具子进程（如 `git`、`ssh`、`gh`、`npm` 及各类技能 CLI）使用的独立用户目录 |
| `cron/` | 定时任务定义 |
| `hooks/` | 事件钩子 |
| `logs/` | 运行时日志 |
| `skins/` | 自定义 CLI 外观皮肤 |

### 不可修改的安装结构

在托管版及发布的 Docker 镜像中，`/opt/hermes` 是已安装的应用程序结构。该目录归 root 所有，且对运行时的 `hermes` 用户为只读模式，因此 Agent 的行为、网关会话、控制台操作以及常规的 `docker exec hermes hermes ...` 命令都无法直接修改核心源代码、打包好的 `.venv`、`node_modules` 文件或 TUI 组件。

所有可修改的 Hermes 状态都存储在 `/opt/data` 下：包括配置文件、`.env`、用户配置文件、技能、内存数据、会话记录、日志、控制台上传内容、插件以及其他由用户管理的文件。该镜像还会禁止在运行时向 `/opt/hermes` 写入 `.pyc` 文件或进行懒加载依赖安装；发布版镜像所需的可选平台依赖项应直接嵌入镜像中，或通过重新构建镜像来安装。

在托管版/发布的镜像中，Agent 的自我优化仅限于 `/opt/data` 下的技能、内存、插件及配置文件。而 `/opt/hermes` 中已安装的核心源代码是不可修改的；核心功能的更改需通过向仓库提交 PR 并更新镜像来实现，而非直接对正在运行的实例进行实时编辑。

如果操作员需要修复或检查 `/opt/data` 之外的文件，则必须手动使用 root shell。通常情况下，`hermes` shim 会将 `docker exec hermes hermes ...` 的命令转交回运行时用户；只有在确实需要 root 权限时，才可通过设置 `HERMES_DOCKER_EXEC_AS_ROOT=1` 来实现一次性以 root 身份执行命令。

那些将凭证存储在 `~` 目录下的技能 CLI，必须基于子进程的独立用户目录进行初始化，而不仅仅是数据卷的根目录。例如，[xurl 技能](./skills/bundled/social-media/social-media-xurl.md) 会将 OAuth 状态信息存储在 `~/.xurl` 中；在官方 Docker 镜像中，Hermes 工具读取该路径时会视为 `/opt/data/home/.xurl`，因此需使用 `HOME=/opt/data/home` 参数手动执行 xurl 认证，并通过 `HOME=/opt/data/home xurl auth status` 查看认证状态。

:::warning
切勿同时让两个 Hermes **网关** 容器访问同一个数据目录——会话文件和内存存储区并非为并发写入设计。
:::

## 多配置文件支持

Hermes 支持[多个配置文件](../reference/profile-commands.md)，即通过创建多个 `~/.hermes/` 子目录，从而让单个安装实例能够运行多个独立的 Agent（拥有不同的 SOUL 设置、技能、内存数据、会话记录及凭证）。**在官方 Docker 镜像中，s6 监控系统会将每个配置文件视为独立的受监控服务**，因此推荐的部署方式是**使用一个容器来承载所有配置文件**。

通过 `hermes profile create <name>` 创建的每个配置文件都会获得：

- 一个位于 `/run/service/gateway-<name>/` 的专用 s6 服务槽位，该槽位由运行时动态注册——无需重新构建容器。
- 出现故障时自动重启，由 `s6-supervise` 负责实现延迟重启机制。
- 每个配置文件都有独立的轮转日志，存储路径为 `${HERMES_HOME}/logs/gateways/<name>/current`（共保留 10 个归档文件，每个 1 MB）。
- 容器重启后状态依然保持：启动时，状态同步工具会读取每个配置文件目录中的 `gateway_state.json` 文件，仅对上次记录状态为 `running` 的配置文件重新启动其服务槽位。只有通过 `hermes gateway stop` 显式停止的网关才会在重启后保持关闭状态——而容器重启、镜像升级或意外退出都会使状态仍显示为 `running`，因此网关会在下一次启动时自动恢复运行。

在宿主机上使用的生命周期管理命令，在容器内部同样可以正常使用。

```sh
# Create a profile — registers the gateway-<name> s6 slot.
docker exec hermes hermes profile create coder

# Start / stop / restart — dispatches s6-svc; the gateway lifecycle survives docker restart.
docker exec hermes hermes -p coder gateway start
docker exec hermes hermes -p coder gateway stop
docker exec hermes hermes -p coder gateway restart

# Status — reports `Manager: s6 (container supervisor)` inside the container.
docker exec hermes hermes -p coder gateway status

# Remove a profile — tears down the s6 slot too.
docker exec hermes hermes profile delete coder
```

在底层实现中，容器内的 `hermes gateway start/stop/restart` 命令会被拦截并路由至对应服务目录下的 `s6-svc`；因此您无需直接学习 s6 的命令。若需查看 supervisor 的原始状态，可使用命令 `/command/s6-svstat /run/service/gateway-<name>`（请注意，/command/ 仅存在于 supervision 树生成的进程的 PATH 中——通过 `docker exec` 调用时需使用绝对路径）。

### 从容器外部访问多个配置文件

从外部访问配置文件的网关有两种不同途径，且其行为各异——请勿混淆二者：

**Hermes 桌面端（以及网页控制面板）。** 桌面应用的 **远程网关** 连接实际上是与 `hermes dashboard` 后端进行通信（默认端口为 **9119**，可通过 `HERMES_DASHBOARD=1` 启用）——而非 OpenAI API 服务器。同一个控制面板后端可为所有共存的配置文件提供服务：应用中的配置文件切换器会在每次请求中传递目标配置文件信息，而后端则会在磁盘上打开该配置文件的 `HERMES_HOME` 目录。因此，对于桌面端而言，无需为每个配置文件单独设置端口或连接——一个 `:9119` 的连接即可通过切换器覆盖所有配置文件。

**兼容 OpenAI 的 API 客户端（如 Open WebUI、LobeChat、/v1/...）。** 这类客户端会与每个配置文件的 **API 服务器** 进行通信，而每个配置文件的 API 服务器都会绑定 **8642 端口**（该端口值由 `API_SERVER_PORT` 或 `platforms.api_server.extra.port` 决定——系统不会自动分配端口，也不存在 `config.yaml`/`gateway.port` 相关设置）。如果您希望某个客户端能够访问特定的第二个配置文件，需在该配置文件自身的 `.env` 文件中为其指定独立的 `API_SERVER_PORT`；否则，该配置文件的网关也会尝试绑定 8642 端口，从而与默认配置文件产生冲突。

```sh
# Create the profile (registers its gateway-<name> s6 slot)
docker exec hermes hermes profile create work

# Point its API server at a free port (write to the profile's own .env)
cat >> /opt/data/profiles/work/.env <<'EOF'
API_SERVER_ENABLED=true
API_SERVER_PORT=8643
EOF

docker exec hermes hermes -p work gateway restart
```

请将 `API_SERVER_PORT` 设置在每个配置文件的**独立** `.env` 文件中，切勿放在整个容器的 `environment:` 块中——全局值会导致所有配置文件都使用同一个端口，从而引发冲突。在使用桥接网络时，需在 `docker-compose.yml` 中指定额外的端口（如 `- "8643:8643"`）；而当设置为 `network_mode: host` 模式时，该端口可直接在主机上访问。默认配置文件的 8642 端口连接则保持不变。

### 为何选择单个容器承载多个配置文件，而非多个容器

在迁移到 s6 之前，由于容器内没有可用于管理多个网关的监督进程，“一个配置文件对应一个容器”是推荐的架构模式。但随着 s6 成为 PID 1，这种做法已不再必要，且单容器架构在几乎所有方面都更为简洁：

| | 单容器多配置文件 | 每个配置文件一个容器 |
|---|---|---|
| 磁盘开销 | 一个镜像、一个打包好的虚拟环境、一个 Playwright 缓存 | N 个镜像 / N 个缓存 |
| 内存开销 | 共享 Python 解释器缓存及 node_modules 文件 | 每个容器都复制这些资源 |
| 配置文件创建 | 使用 `docker exec ... hermes profile create <name>`（仅需数秒） | 需要新的 `docker run` 命令，还需分配端口并挂载配置文件 |
| 配置文件崩溃后的恢复 | 由 `s6-supervise` 自动重启 | 依赖 Docker 的 `--restart unless-stopped` 参数（恢复速度较慢，且会终止其他正在运行的进程） |
| 日志管理 | 通过 `s6-log` 实现按配置文件分区的日志轮转，另还有容器启动审计日志 | 需通过 `docker logs <name>` 查看每个容器的日志，且无内置轮转功能 |
| 备份操作 | 仅需一个 `~/.hermes` 目录 | 需协调管理 N 个目录 |

默认配置文件（`default`）会在首次启动时自动注册，因此新创建的容器会直接配备一个受监督管理的网关。其他配置文件则属于运行时的附加组件。

### 何时确实需要单独的容器

将配置文件置于容器内是默认做法。只有出于特定原因时，才应为每个配置文件启动独立的容器：
- **按工作负载实现资源隔离**——例如，配置文件 A 中失控的浏览器工具进程不应占用配置文件 B 的内存。容器可让每个配置文件拥有独立的 `--memory`/`--cpus` 参数设置。
- **独立的镜像版本控制**——不同工作负载可使用不同的上游镜像标签。
- **网络隔离**——为每个配置文件创建独立的 Docker 网络（例如一个用于面向客户的流量，另一个用于内部通信）。
- **合规性要求/降低影响范围**——不同的凭据绝不会共享同一套操作系统级别的进程树。

在这些情况下，应为每个配置文件定义一个服务，为其指定不同的 `container_name`、`volumes` 和 `ports` 参数。

```yaml
services:
  hermes-work:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-work
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes-work:/opt/data

  hermes-personal:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-personal
    restart: unless-stopped
    command: gateway run
    ports:
      - "8643:8642"
    volumes:
      - ~/.hermes-personal:/opt/data
```

关于[持久卷](#persistent-volumes)的警告依然有效：切勿同时让两个容器指向同一个`~/.hermes`目录。每个容器内的s6监管进程会独立管理自身的配置文件集；跨容器共享数据卷会导致会话文件和内存存储损坏。

## 日志存储位置

s6容器拥有四种不同的日志输出方式，因此“为何在我的`docker logs`中看不到任何内容？”是一个常见的问题。具体对应关系如下表所示：

| 日志来源 | 存储位置 | 查看方法 |
|---|---|---|
| **按配置文件划分的网关**（通过`hermes gateway run`启动的网关以及s6管理的各配置文件网关） | 同时写入两个位置：`docker logs <容器名>`（实时输出，无前缀）**以及**`${HERMES_HOME}/logs/gateways/<配置文件名>/current`（按规则轮转，附带ISO-8601时间戳，共保存10个版本，每个1 MB） | 在主机上使用`docker logs -f hermes`或`tail -F ~/.hermes/logs/gateways/default/current`查看 |
| **控制面板**（当设置`HERMES_DASHBOARD=1`时） | `docker logs <容器名>`（无前缀） | 使用`docker logs -f hermes`查看，日志内容会与网关相关输出混排在一起 |
| **启动同步器**（记录每次容器启动时恢复了哪些配置文件网关） | `${HERMES_HOME}/logs/container-boot.log`（只读审计日志） | 使用`tail -F ~/.hermes/logs/container-boot.log`查看 |
| **通用Hermes日志**（如`agent.log`、`errors.log`） | `${HERMES_HOME}/logs/`（会根据配置文件区分） | 使用命令`docker exec hermes hermes logs --follow [--level WARNING] [--session <ID>]`查看 |

有两个值得注意的实际要点：

- 位于`logs/gateways/<配置文件名>/current`处的文件会在容器重启后依然保留。而`docker logs`仅保存当前容器运行期间的输出内容（在执行`docker rm`时会清除），那些经过轮转的日志文件则会保留在绑定挂载的卷上。
- 启动同步器的审计日志格式为`<ISO时间戳> profile=<配置文件名> prior_state=<之前的状态> action=<已注册|已启动>`，因此只需执行快速命令`grep profile=coder ~/.hermes/logs/container-boot.log`，即可查看某配置文件最后一次被恢复的时间，以及s6是否自动启动了它。

## 环境变量传递

API密钥会从容器内的 `/opt/data/.env` 文件中读取。您也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接使用 `-e` 标志可覆盖 `.env` 文件中的值。这在 CI/CD 或集成密钥管理工具的场景中非常有用，因为这些场景不希望将敏感密钥存储在磁盘上。

:::note 寻找基于 Docker 的**终端后端**？
本页面介绍的是在 Docker 中运行 Hermes 的方法。如果您希望让 Hermes 在 Docker 沙箱容器中执行代理的 `terminal`/`execute_code` 请求（即一个在多个 Hermes 进程间共享的长期运行的容器——参见问题 #20561），则需要使用单独的配置项：`terminal.backend: docker`，以及 `terminal.docker_image`、`terminal.docker_volumes`、`terminal.docker_forward_env`、`terminal.docker_env`、`terminal.docker_run_as_host_user`、`terminal.docker_extra_args`、`terminal.docker_persist_across_processes` 和 `terminal.docker_orphan_reaper`。完整的配置项及容器生命周期规则请参见 [配置 → Docker 后端](configuration.md#docker-backend)。
:::

## Docker Compose 示例

若需同时持久化部署网关和控制面板，使用 `docker-compose.yaml` 会更为便捷：

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"   # gateway API
      - "9119:9119"   # dashboard (only reached when HERMES_DASHBOARD=1)
    volumes:
      - ~/.hermes:/opt/data
    environment:
      - HERMES_DASHBOARD=1
      # Uncomment to forward specific env vars instead of using .env file:
      # - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      # - OPENAI_API_KEY=${OPENAI_API_KEY}
      # - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"
```

首先运行 `docker compose up -d` 启动服务，然后使用 `docker compose logs -f` 查看日志。受监管网关的标准输出还会被同时写入卷中的 `${HERMES_HOME}/logs/gateways/<profile>/current` 文件——有关完整的日志路由规则，请参阅 [日志存储位置](#where-the-logs-go)。

## 可选功能：Linux 桌面音频桥接

在 Docker 环境中实现语音功能需要满足两个条件：必须允许 Hermes 探测容器内的音频设备，同时容器还需能够连接到宿主机的音频服务器。以下配置适用于那些提供 PulseAudio 兼容套接字的 Linux 桌面系统，同时也支持多种 PipeWire 配置。

:::caution
这仅是 Linux 桌面的临时解决方案，并非 Docker Desktop 的通用功能。当您的主机音频已正常工作，但希望在 Hermes 容器内使用命令行语音模式时，此方法十分有用。如果 Hermes 仍显示“正在 Docker 容器中运行——无音频设备”，请使用包含针对 `PULSE_SERVER` / `PIPEWIRE_REMOTE` 的 Docker 音频探测支持的构建版本。
:::

首先，在您的 Compose 文件旁创建一个 ALSA 配置文件：

```conf title="asound.conf"
pcm.!default {
    type pulse
    hint {
        show on
        description "Default ALSA Output (PulseAudio)"
    }
}

pcm.pulse {
    type pulse
}

ctl.!default {
    type pulse
}
```

接着，构建一个已安装 ALSA PulseAudio 插件的小型派生镜像：

```dockerfile title="Dockerfile.audio"
FROM nousresearch/hermes-agent:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends libasound2-plugins \
    && rm -rf /var/lib/apt/lists/*
```

在 Compose 中使用该图像，并传递主机用户的 PulseAudio 套接字与 Cookie：

```yaml
services:
  hermes:
    build:
      context: .
      dockerfile: Dockerfile.audio
    image: hermes-agent-audio
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    volumes:
      - ~/.hermes:/opt/data
      - /run/user/${HERMES_UID}/pulse:/run/user/${HERMES_UID}/pulse
      - ~/.config/pulse/cookie:/tmp/pulse-cookie:ro
      - ./asound.conf:/etc/asound.conf:ro
    environment:
      - HERMES_UID=${HERMES_UID}
      - HERMES_GID=${HERMES_GID}
      - XDG_RUNTIME_DIR=/run/user/${HERMES_UID}
      - PULSE_SERVER=unix:/run/user/${HERMES_UID}/pulse/native
      - PULSE_COOKIE=/tmp/pulse-cookie
```

请使用您的主机 UID/GID 启动该进程，这样容器内的程序便能访问针对用户的音频套接字。

```sh
export HERMES_UID="$(id -u)"
export HERMES_GID="$(id -g)"
docker compose up -d --build
```

要验证 PortAudio 在容器内部所检测到的内容：

```sh
docker exec hermes /opt/hermes/.venv/bin/python -c "import sounddevice as sd; print(sd.query_devices())"
```

## 资源限制

Hermes 容器需要适量的资源。建议的最低配置如下：

| 资源类型 | 最低要求 | 推荐配置 |
|----------|---------|-----------|
| 内存 | 1 GB | 2–4 GB |
| CPU | 1 核心 | 2 核心 |
| 磁盘空间（数据量） | 500 MB | 2+ GB（会随会话数和技能数量增加而增长） |

浏览器自动化功能（Playwright/Chromium）是内存消耗最大的部分。如果无需使用浏览器工具，1 GB 内存即可满足需求；若需启用浏览器工具，则至少需要分配 2 GB 内存。

可在 Docker 中设置资源限制：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  --memory=4g --cpus=2 \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

## Dockerfile 的功能

官方镜像基于 `debian:13.4` 构建，包含以下组件：

- Python 3.13 及其依赖项，这些依赖项通过 `uv sync --frozen --no-install-project` 从锁定文件中同步而来，用于预置各类扩展功能（如 `all`、`messaging`、Anthropic/Bedrock/Azure 身份验证、Hindsight、Matrix 等），之后再以无需额外依赖的可编辑方式安装 Hermes 本身。
- Node.js 22 + npm（用于浏览器自动化、WhatsApp 桥接、TUI/桌面版打包以及工作区构建工具）。
- 带 Chromium 的 Playwright（通过 `npx playwright install --with-deps chromium --only-shell` 安装）。
- 作为系统工具的 ripgrep、ffmpeg、git 和 `xz-utils`。
- **`docker-cli`**——使容器内的 Agent 能够控制宿主机的 Docker 守护进程（可通过绑定挂载 `/var/run/docker.sock` 启用），从而执行 `docker build`、`docker run`、容器检查等操作。
- **`openssh-client`**——允许在容器内部使用 [SSH 终端后端](/user-guide/configuration#ssh-backend)。该后端会调用系统自带的 `ssh` 工具；若缺少此组件，容器化安装时会静默失败。
- WhatsApp 桥接工具（位于 `scripts/whatsapp-bridge/` 目录）。
- 作为 PID 1 进程的 **[`s6-overlay`](https://github.com/just-containers/s6-overlay) v3**（取代了旧版的 `tini`）——负责监控仪表板和各用户配置的网关，可在进程崩溃时自动重启、清理僵尸子进程并转发信号。

该镜像在运行时会将 `/opt/hermes` 视为不可修改的安装目录。所有需要在 Docker 内部使用的可选 Python 扩展、Node 工作区以及 TUI 资源都必须在镜像构建阶段预置；运行时不会进行延迟安装，以避免受监控的网关及 `docker exec hermes …` 命令试图将依赖文件写回只读的源代码目录中。

容器的 `ENTRYPOINT` 为 s6-overlay 的 `/init`。启动时，它会执行以下操作：
1. 以 root 权限运行 `/etc/cont-init.d/01-hermes-setup`（即 `docker/stage2-hook.sh`）：可选地重新映射 UID/GID、修复卷的所有权、在首次启动时生成 `.env`、`config.yaml` 和 `SOUL.md` 文件、在未设置 `HERMES_SKIP_CONFIG_MIGRATION=1` 时自动执行非交互式的配置架构迁移，同时同步预置的技能。
2. 运行 `/etc/cont-init.d/02-reconcile-profiles`（即 `hermes_cli.container_boot`）：遍历 `$HERMES_HOME/profiles/<name>/` 目录，在 `/run/service/gateway-<profile>/` 下重新创建对应用户配置的网关 s6 服务槽，并仅自动启动那些上次记录状态为 `running` 的服务（详见[用户配置网关监控](#per-profile-gateway-supervision)）。
3. 启动静态的 `main-hermes` 和 `dashboard` s6-rc 服务。
4. 以容器内的 CMD 作为主程序执行（即 `/opt/hermes/docker/main-wrapper.sh`），该脚本会处理用户通过 `docker run` 传递的参数：
   - 无参数 → 默认启动 `hermes`。
   - 第一个参数是 PATH 中的可执行文件（如 `sleep`、`bash`）→ 直接执行该文件。
   - 其他参数 → 以 `hermes <args>` 的形式传递给 Hermes（实现子命令直接传递）。
   容器会随着主程序的退出而终止，其退出码也会随之确定。

:::warning 与 s6 之前的镜像相比的变更
当前容器的 ENTRYPOINT 已改为 `/init`（即 s6-overlay），而非 `/usr/bin/tini`。所有五种已记录的 `docker run` 调用方式（无参数、`chat -q "…"`、`sleep infinity`、`bash`、`--tui`）在行为上与基于 tini 的镜像完全一致。如果您有依赖 tini 特定信号处理机制或硬编码了 `/usr/bin/tini --` 调用方式的下游封装工具，请继续使用旧版本的镜像标签。
:::

:::warning 权限模型
除非您在命令链中保留 `/init`（或等效的、用于转发到 stage2 钩子的旧版 `docker/entrypoint.sh`），否则请勿覆盖镜像的入口点。s6-overlay 的 `/init` 以 root 权限运行，因此可在首次启动时修改卷的所有权；之后，它会通过 `s6-setuidgid` 将权限转换为 `hermes` 用户，这一机制既适用于所有受监控的服务，也适用于主程序。在官方镜像中，默认会拒绝以 root 权限启动 `hermes gateway run`，因为这可能会导致 `/opt/data` 目录中出现 root 所有的文件，进而影响后续仪表板或网关的启动。只有当您明确接受此类风险时，才可设置 `HERMES_ALLOW_ROOT_GATEWAY=1`。
:::

### `docker exec` 会自动切换到 `hermes` 用户权限

`docker exec hermes <cmd>` 默认会在容器内以 root 权限运行，但镜像中在 `/opt/hermes/bin/hermes`（PATH 中的最早路径）处提供了一个轻量级的封装脚本，该脚本能够检测到以 root 身份调用的情况，并通过 `s6-setuidgid hermes` 透明地重新执行命令。因此，无论是 `docker exec hermes login`、`docker exec hermes profile create …`、`docker exec hermes setup` 还是其他类似命令，都会以 UID 10000 所拥有的权限创建文件——即受监控的网关能够读取这些文件——而无需额外使用 `--user` 参数。非 root 用户（即受监控的进程本身、通过 `docker exec --user hermes` 调用的用户，以及容器内的看板子 Agent）则会直接执行虚拟环境中的二进制文件，从而避免在高频调用的路径上产生额外开销。

如果您确实需要保持 root 权限的 `docker exec` 行为（例如用于诊断会话、检查仅 root 可访问的状态、操作 root 所拥有的 `/opt/data` 之外的文件），则可以在每次调用时手动取消此自动转换。

```sh
docker exec -e HERMES_DOCKER_EXEC_AS_ROOT=1 hermes <cmd>
```

该适配层会识别 `1` / `true` / `yes`（不区分大小写）作为有效值。任何其他输入——包括诸如 `=0` 这样的拼写错误——都会导致任务被直接丢弃，因此无法实现静默的退出选项。如果系统中没有 `s6-setuidgid` 功能（即那些去除了 s6-overlay 组件的自定义构建版本），该适配层将拒绝以 root 权限运行，并返回代码 126，从而明确暴露出权限模型存在的缺陷；而不会退回到旧有的糟糕做法——即使用 `docker exec hermes login` 时将 `auth.json` 的权限设置为 `root:root`，进而导致在每个聊天平台的消息处理过程中都会破坏受监管网关的认证机制。

### 按配置文件划分的网关监管机制

通过 `hermes profile create <name>` 创建的每个配置文件，都会自动在 `/run/service/gateway-<name>/` 下注册一个 s6 监管型网关服务，且该服务具备跨容器重启的状态持久化自动重启功能。有关面向用户的操作流程及生命周期管理命令，请参阅上文中的[多配置文件支持](#multi-profile-support)部分。

**相比使用旧版 s6 镜像，该监管机制的优势包括：**

- 当网关发生崩溃时，`s6-supervise` 会在大约 1 秒的延迟后自动重启它。
- 若启用了 `HERMES_DASHBOARD=1`，控制面板也会被纳入同一监管体系，享受相同的自动重启功能。
- 通过 `docker restart`、镜像升级（如 `docker compose up -d --force-recreate`）或意外退出等情况时，正在运行的网关仍能保持正常状态：cont-init 协调器会读取 `$HERMES_HOME/profiles/<name>/gateway_state.json` 文件，若上次记录的状态为“运行中”，则会立即重启该网关。只有通过明确的 `hermes gateway stop` 命令将状态标记为“已停止”时，网关在重启后才会保持关闭状态；而在重启或升级过程中发送给容器或 s6 的 SIGTERM 信号会被视为“仍在运行”状态，网关会自动重新启动。
- 每个配置文件对应的网关日志会保存在 `$HERMES_HOME/logs/gateways/<profile>/current` 目录下（由 `s6-log` 负责日志轮转），而协调器的操作记录则会每次启动时追加到 `$HERMES_HOME/logs/container-boot.log` 文件中。完整的日志路由规则请参阅[日志存储位置](#where-the-logs-go)部分。

在容器内部执行 `hermes status` 命令，会显示“Manager: s6 (container supervisor)”的字样。如需查看监管系统的原始状态信息，可运行 `/command/s6-svstat /run/service/gateway-<name>` 命令（请注意，/command/ 目录仅对监管体系下的进程有效；从 `docker exec` 命令中调用时需使用绝对路径）。

## 升级操作

只需拉取最新版本的镜像并重新创建容器即可。您的数据目录将会被保留，且容器在启动网关之前，会先针对已挂载的 `$HERMES_HOME/config.yaml` 文件执行非交互式的配置架构迁移。当需要执行迁移时，Hermes 会首先在 `config.yaml` 和 `.env` 文件旁边生成带有时间戳的备份文件。

```sh
docker pull nousresearch/hermes-agent:latest
docker rm -f hermes
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

或者使用 Docker Compose：

```sh
docker compose pull
docker compose up -d
```

仅当您需要在让新镜像覆盖之前手动检查或迁移持久化配置时，才需设置 `HERMES_SKIP_CONFIG_MIGRATION=1`。

## 技能与凭证文件

当以 Docker 作为执行环境时（即并非使用上述方法，而是让代理在 Docker 沙箱中运行命令——详见 [配置 → Docker 后端](./configuration.md#docker-backend)），Hermes 会为所有工具调用复用同一个长期运行的容器，并自动将技能目录（`~/.hermes/skills/`）以及技能所指定的任何凭证文件以只读卷的形式绑定到该容器中。无需手动配置，技能脚本、模板及引用即可在沙箱中使用；由于该容器会伴随 Hermes 进程的整个生命周期而存在，因此您安装的任何依赖项或编写的文件都会在后续的工具调用中依然保留。

SSH 和 Modal 后端也采用相同的同步机制——在每条命令执行之前，技能文件和凭证文件会通过 rsync 或 Modal 的挂载 API 被上传到容器中。

## 在容器中安装更多工具

官方镜像已预装了一组精选的实用工具（详见 [Dockerfile 的功能](#what-the-dockerfile-does)），但并非代理可能需要的所有工具都已预先安装。这里有五种推荐方案，按所需工作量和持久性从低到高排序。

### npm 或 Python 工具——使用 `npx` 或 `uvx`

对于任何发布在 npm 或 PyPI 上的工具，可指示 Hermes 通过 `npx`（npm）或 `uvx`（Python）来运行它，并将该命令保存在其持久内存中。如果该工具需要配置文件或凭证，可指定将其保存在 `/opt/data` 目录下（例如 `/opt/data/<tool>/config.yaml`）。

依赖项会按需获取并在容器生命周期内缓存。保存在 `/opt/data` 下的配置文件由于存储在绑定挂载的主机目录中，因此能够在容器重启后依然存在。虽然 `docker rm` 操作会清除包缓存，但下次运行该工具时，`npx` 和 `uvx` 会自动重新获取所需依赖。

### 其他工具（apt 包、二进制文件）——安装并记住

对于那些不在 npm 或 PyPI 上的工具——如 `apt` 包、预编译的二进制文件，或是镜像中未包含的语言运行时——需告知 Hermes 如何安装它们（例如 `apt-get update && apt-get install -y <package>`），并让它记住该安装命令。这样，该工具就会在容器整个生命周期内一直存在，而当容器重启后 Hermes 下次需要该工具时，它会自动重新执行安装命令。

这种方法适用于那些安装快速且使用频率较低的工具。对于需要频繁使用的工具，则建议采用以下方案。

### 高持久性安装——构建衍生镜像

当某工具必须在每次容器启动时立即可用，且不能有任何重新安装的延迟时，可以构建一个基于 `nousresearch/hermes-agent` 的新镜像，并在镜像的某个层中安装该工具：

```dockerfile
FROM nousresearch/hermes-agent:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends <your-package> \
    && rm -rf /var/lib/apt/lists/*
USER hermes
```

构建该版本并使用它来替代官方镜像：

```sh
docker build -t my-hermes:latest .
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  my-hermes:latest gateway run
```

入口脚本以及 `/opt/data` 的功能机制保持不变，因此本页的其他说明依然适用。在拉取更新版的 upstream `nousresearch/hermes-agent` 时，请务必重新构建镜像。

### 复杂工具或多服务架构——运行侧车容器

对于那些自带服务（如数据库、Web服务器、消息队列、无头浏览器集群）或体积过大而无法置于Hermes容器内的工具，可将其作为独立容器运行在共享的Docker网络中。Hermes可通过容器名称来访问这些侧车容器，方式与访问本地推理服务器相同（详见[连接本地推理服务器](#connecting-to-local-inference-servers-vllm-ollama-etc)）。

```yaml
services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes:/opt/data
    networks:
      - hermes-net

  my-tool:
    image: example/my-tool:latest
    container_name: my-tool
    restart: unless-stopped
    networks:
      - hermes-net

networks:
  hermes-net:
    driver: bridge
```

在 Hermes 容器内部，可以通过 `http://my-tool:<port>`（或该工具所使用的其他协议地址）访问 sidecar 服务。这种设计方式能够让各个服务的生命周期、资源限制及升级频率相互独立，同时避免因某些工具仅需的依赖项而使 Hermes 镜像变得臃肿。

### 具有广泛实用价值的工具——提交问题或 Pull Request

如果某款工具可能对大多数 Hermes Agent 用户都有用，建议直接为上游项目做出贡献，而非将其封装在私有的衍生镜像中。请在 [hermes-agent 仓库](https://github.com/NousResearch/hermes-agent) 上提交问题或 Pull Request，详细介绍该工具及其应用场景。被整合到官方镜像中的工具能让所有用户受益，同时也能避免维护下游分支所带来的额外工作量。

## 连接本地推理服务器（vLLM、Ollama 等）

当在 Docker 中运行 Hermes，而你的推理服务器（vLLM、Ollama、text-generation-inference 等）也在主机上或另一个容器中运行时，网络配置需要特别留意。

### Docker Compose（推荐方案）

将这两个服务置于同一个 Docker 网络中。这是最可靠的做法：

```yaml
services:
  vllm:
    image: vllm/vllm-openai:latest
    container_name: vllm
    command: >
      --model Qwen/Qwen2.5-7B-Instruct
      --served-model-name my-model
      --host 0.0.0.0
      --port 8000
    ports:
      - "8000:8000"
    networks:
      - hermes-net
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    command: gateway run
    ports:
      - "8642:8642"
    volumes:
      - ~/.hermes:/opt/data
    networks:
      - hermes-net

networks:
  hermes-net:
    driver: bridge
```

接着在您的 `~/.hermes/config.yaml` 文件中，使用**容器名称**作为主机名：

```yaml
model:
  provider: custom
  model: my-model
  base_url: http://vllm:8000/v1
  api_key: "none"
```

:::提示 关键要点
- 请使用**容器名称**（`vllm`）作为主机名——而非`localhost`或`127.0.0.1`，因为这些地址指的是Hermes容器本身。
- `model`值必须与传递给vLLM的`--served-model-name`参数一致。
- 将`api_key`设置为任意非空字符串（vLLM要求该字段存在，但默认不会对其进行验证）。
- `base_url`后**不得**添加斜杠。
:::

### 独立运行Docker容器（无需Compose）

如果您的推理服务器直接在主机上运行（而非在Docker容器中），则在macOS/Windows系统上使用`host.docker.internal`，在Linux系统上使用`--network host`：

**macOS / Windows:**

```sh
docker run -d \
  --name hermes \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

```yaml
# config.yaml
model:
  provider: custom
  model: my-model
  base_url: http://host.docker.internal:8000/v1
  api_key: "none"
```

**Linux（主机网络）：**

```sh
docker run -d \
  --name hermes \
  --network host \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

```yaml
# config.yaml
model:
  provider: custom
  model: my-model
  base_url: http://127.0.0.1:8000/v1
  api_key: "none"
```

:::warning 当使用 `--network host` 选项时，`-p` 参数将被忽略——所有容器端口都将直接在主机上暴露。
:::

### 验证连接性

在 Hermes 容器内部，确认可以访问推理服务器：

```sh
docker exec hermes curl -s http://vllm:8000/v1/models
```

您应该会看到一个列出已部署模型的 JSON 响应。如果操作失败，请检查以下内容：

1. 两个容器是否处于同一个 Docker 网络中（可使用 `docker network inspect hermes-net` 查看）；
2. 推理服务器是否在 `0.0.0.0` 上监听，而非 `127.0.0.1`；
3. 端口编号是否一致。

### Ollama

Ollama 的使用方式类似。如果 Ollama 在主机上运行，请使用 `host.docker.internal:11434`（macOS/Windows）或 `127.0.0.1:11434`（已启用 `--network host` 选项的 Linux 系统）。如果 Ollama 在同一个 Docker 网络中的独立容器内运行：

```yaml
model:
  provider: custom
  model: llama3
  base_url: http://ollama:11434/v1
  api_key: "none"
```

## 故障排除

### 容器立即退出

请检查日志：`docker logs hermes`。常见原因包括：
- 缺少或无效的 `.env` 文件——建议先以交互模式运行以完成配置
- 启用暴露端口时出现端口冲突

### “权限被拒绝”错误

容器中的 stage2 钩子会在每个受监控的服务中通过 `s6-setuidgid` 功能，将权限降级为非根用户 `hermes`（UID 10000）。如果您的主机上的 `~/.hermes/` 目录由其他 UID 所拥有，请设置 `HERMES_UID`/`HERMES_GID`——或与其对应的 `PUID`/`PGID` 别名——使其与 LinuxServer.io 及 NAS 镜像保持一致，从而匹配您的主机用户；或者确保数据目录具有写入权限：

```sh
chmod -R 755 ~/.hermes
```

在 NAS（如 UGOS、Synology、unRAID）上，数据目录通常采用**绑定挂载**方式，其所有权归属于主机 UID，容器无法对其执行 `chown` 操作。因此，请将 `PUID`/`PGID`（或 `HERMES_UID`/`HERMES_GID`）设置为该主机用户对应的值，这样运行时进程就会以挂载点的所有者身份而非 UID 10000 来运行。

```sh
docker run -d \
  --name hermes \
  -e PUID=1000 -e PGID=10 \
  -v /volume1/docker/hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

`docker exec hermes <cmd>` 命令同样会自动切换到 UID 10000 用户——详情及针对单次调用的禁用选项，请参阅[“docker exec”命令会自动切换到“hermes”用户](#docker-exec-automatically-drops-to-the-hermes-user)。

### 浏览器工具无法使用

Playwright 需要共享内存。请在 Docker 运行命令中添加 `--shm-size=1g` 参数：

```sh
docker run -d \
  --name hermes \
  --shm-size=1g \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

### 网络故障后网关无法重新连接

`--restart unless-stopped` 参数可解决大多数短暂性故障。如果网关出现卡死情况，请重启该容器：

```sh
docker restart hermes
```

### 检查容器运行状态

```sh
docker logs --tail 50 hermes          # Recent logs
docker run -it --rm nousresearch/hermes-agent:latest version     # Verify version
docker stats hermes                    # Resource usage
```
