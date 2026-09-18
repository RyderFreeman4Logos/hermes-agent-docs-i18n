---
sidebar_position: 7
title: "Hermes Docker Setup"
description: "Running Hermes Agent in Docker and using Docker as a terminal backend"
---

# Hermes Docker 部署指南

Docker 与 Hermes Agent 的结合主要存在两种方式：

1. **在 Docker 中运行 Hermes**——即让 Agent 本身在容器内运行（本页主要介绍此方式）
2. **将 Docker 作为终端后端**——Agent 在主机上运行，但所有命令都在一个持久化的 Docker 沙箱容器中执行，该容器会在整个 Hermes 进程运行期间保持存在，从而支持工具调用、/new 指令以及子 Agent 的使用（详见[配置 → Docker 后端](./configuration.md#docker-backend)）

本页介绍第一种方式。容器会将所有用户数据（配置、API 密钥、会话信息、技能及记忆内容）存储在从主机挂载到的 `/opt/data` 目录中。该镜像本身是无状态的，只需拉取新版本即可升级，而不会丢失任何配置。

## 快速开始

如果您是首次运行 Hermes Agent，请先在主机上创建一个数据目录，然后以交互模式启动容器以运行设置向导：

:::caution 安装命令请避免使用基于浏览器的 VPS 控制台
部分 VPS 提供商（如 Hetzner Cloud 及其他几家）提供了用于管理主机的基于浏览器的控制台。这类控制台无法正确传输特殊字符——`:` 可能会被显示为 `;`，`@` 的显示也可能出错，非英语键盘布局的情况更为糟糕——这会导致 `-v ~/.hermes:/opt/data`、`-e KEY=value` 这类 `docker run` 参数以及粘贴的 API 密钥/令牌被悄悄篡改。

如需输入不会被自动截断的完整命令，建议通过 SSH 进行连接（即使用 `ssh root@<host>`）。若必须使用浏览器控制台，则请手动输入命令而非直接粘贴，并在按下回车键之前仔细核对结果中的每一个 `:`、`@`、`=` 和 `/` 符号。

```sh
mkdir -p ~/.hermes
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent setup
```

这将引导您进入设置向导，向导会提示您输入 API 密钥，并将其写入 `~/.hermes/.env` 文件中。此操作只需执行一次即可。强烈建议在此阶段就为网关配置好对应的聊天系统。

:::提示
在容器内部运行一次 `hermes setup --portal` 命令——刷新令牌会保存在挂载的 `~/.hermes` 卷中。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 以网关模式运行

配置完成后，可在后台运行该容器，将其作为持久化的网关使用（适用于 Telegram、Discord、Slack、WhatsApp 等平台）：

```sh
docker run -d \
  --name hermes \
  --restart unless-stopped \
  -v ~/.hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

端口 8642 用于暴露网关的 [兼容 OpenAI 的 API 服务器](./features/api-server.md)以及健康检查端点。如果您仅使用聊天平台（如 Telegram、Discord 等），该端口并非必需；但若希望仪表板或外部工具能够访问网关，则必须启用它。

:::提示 网关处于受监督运行状态
在官方 Docker 镜像中，`gateway run` 命令会**由 s6-overlay 自动进行监督**：一旦网关进程崩溃，系统会在几秒钟内自动重启该进程且不会导致容器丢失；同时，当设置了 `HERMES_DASHBOARD=1` 时，仪表板也会一同受到监督。`gateway run` 命令本身的作用是通过 `sleep infinity` 实现心跳检测，以维持容器运行状态，而实际的网关进程则由 s6 负责管理——因此即使执行 `docker stop`，所有服务也能干净地停止，且 `docker logs` 中会显示受监督运行的网关的输出信息。

在 `docker logs` 中可以看到一条简短的消息，用于确认升级已完成。如果您希望取消这种监督机制——并恢复传统的“网关为容器的主进程，容器退出即表示网关退出”的运行方式——可以传递 `--no-supervise` 参数，或设置 `HERMES_GATEWAY_NO_SUPERVISE=1`。对于那些需要容器随网关状态码一同退出的 CI 自动化测试而言，取消监督机制很有用；但在生产环境部署中，默认的受监督运行模式显然更为可靠。

此行为仅适用于基于 s6 的镜像。早期基于 tini 的镜像仍会将 `gateway run` 作为前台主进程来运行。
:::

:::note 网关日志的存储位置  
如需查看完整的日志路由路径（包括按配置文件划分的网关、控制面板、启动同步工具以及容器级的 `docker logs`），请参阅下方的[日志存储位置](#where-the-logs-go)部分。  
:::

:::note 无人值守网关的工具循环强制终止功能  
默认情况下，通过 `non_interactive_hard_stop_enabled` 参数，无人值守网关及定时任务会启用工具循环强制终止功能；而交互式 CLI、TUI、桌面端以及 ACP 会话则仅会发出警告。若要在配置文件的 `config.yaml` 中关闭此功能以适配无人值守部署，请进行相应设置：

```yaml
tool_loop_guardrails:
  non_interactive_hard_stop_enabled: false
```
:::

注意：API服务器的启用需满足`API_SERVER_ENABLED=true`这一条件。若希望让容器内的API服务能够被`127.0.0.1`之外的地址访问，还需设置`API_SERVER_HOST=0.0.0.0`以及`API_SERVER_KEY`（长度至少为8位——可使用`openssl rand -hex 32`命令生成）。示例如下：

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

在面向互联网的机器上开放任何端口都会带来安全风险。除非您充分了解相关风险，否则不应这么做。

## 运行控制面板

内置的网页控制面板会以受监督的 s6-rc 服务形式，在与网关相同的容器中运行。如需启动该控制面板，请设置 `HERMES_DASHBOARD=1`：

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

该控制面板由 s6 进行监控——如果其发生崩溃，`s6-supervise` 会在短暂的延迟后自动重启它。控制面板的标准输出/错误输出会被转发至 `docker logs <container>`（无需添加前缀）；而网关自身的输出则会被保存在针对每个配置文件的 s6-log 文件中——详情请参见下文的[日志存储位置](#where-the-logs-go)——这样一来，这两类输出就不会相互冲突。

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `HERMES_DASHBOARD` | 设置为 `1`（或 `true` / `yes`）可启用受监控的控制面板服务 | *(未设置——服务虽已注册但处于关闭状态)* |
| `HERMES_DASHBOARD_HOST` | 控制面板 HTTP 服务器的绑定地址 | `0.0.0.0` |
| `HERMES_DASHBOARD_PORT` | 控制面板 HTTP 服务器的端口号 | `9119` |
| `HERMES_DASHBOARD_INSECURE` | **已废弃/无实际作用。** 该参数曾用于绕过身份验证机制；但在 2026 年 6 月的安全强化措施之后，它已无法取消身份验证功能。非回环地址绑定始终需要配置身份验证提供程序 | *(会被忽略——请直接配置身份验证提供程序)* |

容器内的控制面板默认会绑定 `0.0.0.0` 地址——如果不这样设置，主机将无法访问通过 `-p 9119:9119` 暴露的端口。若希望将绑定限制在容器回环地址上（适用于 sidecar 或反向代理架构），请将 `HERMES_DASHBOARD_HOST` 设置为 `127.0.0.1`。

当同时满足以下两个条件时，控制面板的身份验证机制会自动启用：

1. 绑定地址为非回环地址（例如容器内的默认值 `0.0.0.0`），**且**
2. 已注册了 `DashboardAuthProvider` 插件。
共有三种内置方式可满足第二项要求：

- **用户名/密码**——适用于运行在受信任网络中或 VPN 后面的自托管、本地部署或家庭实验室环境中的容器：只需设置 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` 和 `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`（如需保持会话在重启后仍然有效，还需设置 `HERMES_DASHBOARD_BASIC_AUTH_SECRET`）。此方式不适用于直接暴露在公共互联网上的场景。
- **OAuth（Nous Portal）**——适用于托管或公开部署的场景：一旦设置了 `HERMES_DASHBOARD_OAUTH_CLIENT_ID`，`dashboard_auth/nous` 提供器便会自动启用。
- **自托管 OIDC**——通过标准的 OpenID Connect 协议与您自己的身份验证服务进行交互：当设置了 `HERMES_DASHBOARD_OIDC_ISSUER` 和 `HERMES_DASHBOARD_OIDC_CLIENT_ID` 后，`dashboard_auth/self_hosted` 提供器便会启动。

无论选择哪种方式，访问者在尝试进入任何受保护页面之前都会被重定向至登录页面。关于这三种提供器的详细信息，请参阅 [Web Dashboard → Authentication](features/web-dashboard.md#authentication-gated-mode) 文档。

如果在另一个容器中运行了 Traefik 或 nginx 等反向代理，其桥接网络地址默认是不会被信任的。您需要在挂载的 `config.yaml` 文件中设置仪表板的公共 URL，并仅信任该代理的确切 IP 地址，或是专为该代理网络指定的 CIDR 范围。

```yaml
dashboard:
  public_url: "https://dashboard.example.com"
  trusted_proxies:
    - "172.20.0.5"
    # Or, if the proxy address is dynamic on a dedicated network:
    # - "172.20.0.0/24"
```

该机制允许代理的 `X-Forwarded-Proto: https` 参数来控制安全的 OAuth Cookie，同时将来自其他节点的转发头部视为不可信。请勿使用 `*`、`0.0.0.0/0` 或 `::/0` 这类通配符表达式，因为 Hermes 会拒绝这些范围无限的配置。

如果未注册任何提供程序且绑定地址并非回环地址，控制台将在启动时直接报错，并明确指出缺失的环境变量。目前已不再支持通过公共绑定地址以未经认证的方式访问控制台：`HERMES_DASHBOARD_INSECURE=1` 已被弃用且无实际作用（仅会输出警告并被忽略）。建议配置合适的提供程序，或设置 `HERMES_DASHBOARD_HOST=127.0.0.1`，并通过 SSH 隧道或 Tailscale 来访问控制台。

:::warning 为何移除 `--insecure` 参数
2026 年 6 月发生的 MCP 配置持久化攻击事件，正是利用了未经认证的公共控制台作为入侵入口：网络扫描工具会找到暴露在外的控制台（以及 OpenAI API 服务器），进而迫使代理植入 SSH 密钥后门。因此，现在所有非回环地址的绑定都必须启用身份验证机制。对于可信的局域网或家庭实验室环境，内置的用户名/密码提供程序（`HERMES_DASHBOARD_BASIC_AUTH_USERNAME` + `_PASSWORD`）便是最简便的解决方案。
:::

只要该容器与主机共享 PID 及网络命名空间（例如采用 `network_mode: host` 模式，正如该仓库自身的 `docker-compose.yml` 中所设置的那样——可参考其中的 `dashboard` 服务），即支持将控制面板作为独立容器运行。不过，由于其网关存活检测功能需要与网关进程共享 PID 命名空间，因此这一限制仅适用于那些运行在隔离式桥接网络容器中且未共享 PID 命名空间的控制面板。

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
| `.env` | API 密钥与敏感信息 |
| `config.yaml` | 所有 Hermes 配置 |
| `SOUL.md` | Agent 的个性/身份设定 |
| `sessions/` | 对话历史记录 |
| `memories/` | 持久内存存储区 |
| `skills/` | 已安装的技能模块 |
| `home/` | 供 Hermes 工具子进程（如 `git`、`ssh`、`gh`、`npm` 及各类技能对应的 CLI 工具）使用的个性化 HOME 目录 |
| `cron/` | 定时任务定义 |
| `hooks/` | 事件钩子 |
| `logs/` | 运行时日志 |
| `skins/` | 自定义 CLI 外观主题 |

### 不可变的安装结构

在托管版及已发布的 Docker 镜像中，`/opt/hermes` 即为已安装的应用程序结构。该目录归 root 所有，且对运行时的 `hermes` 用户为只读模式，因此 Agent 的行为、网关会话、控制面板操作以及常规的 `docker exec hermes hermes ...` 命令均无法直接修改核心源代码、打包好的 `.venv` 环境、`node_modules` 依赖包或 TUI 组件。

所有可变的 Hermes 状态数据均存储在 `/opt/data` 下，包括配置文件、`.env` 文件、用户配置文件、技能模块、记忆数据、对话记录、日志文件、控制面板上传内容、插件以及其他由用户管理的文件。此外，该镜像还会禁止在运行时向 `/opt/hermes` 写入 `.pyc` 文件，以及自动安装延迟加载的依赖项；已发布镜像所需的可选平台依赖项应直接嵌入镜像中，或通过重新构建镜像的方式来安装。

在托管或已发布的镜像中，Agent的自我优化仅限于`/opt/data`目录下的技能、内存、插件及配置。而位于`/opt/hermes`中的核心代码是不可修改的；若需对核心部分进行更改，必须通过向代码仓库提交PR来实现，随后再通过更新镜像来应用变更，而非直接对正在运行的实例进行实时编辑。

如果操作员需要修复或检查`/opt/data`之外的文件，则应刻意使用rootShell。通常情况下，`hermes` shim会将`docker exec hermes hermes ...`命令的权限还原为运行时用户；只有当确实需要root权限功能时，才可设置`HERMES_DOCKER_EXEC_AS_ROOT=1`来实现一次性以root身份执行命令。

那些将凭证存储在`~`目录下的技能CLI，必须基于子进程的HOME目录进行初始化，而不仅仅是数据卷的根目录。例如，[xurl技能](./skills/bundled/social-media/social-media-xurl.md)会将OAuth状态信息存储在`~/.xurl`中；而在官方的Docker架构中，Hermes工具会将该路径视为`/opt/data/home/.xurl`，因此需使用`HOME=/opt/data/home`来手动执行xurl授权操作，并通过`HOME=/opt/data/home xurl auth status`来验证授权状态。

:::warning
切勿同时让两个Hermes **gateway**容器访问同一个数据目录——会话文件和内存存储机制并不支持并发写入操作。
:::

## 多配置文件支持

Hermes 支持[多个配置文件](../reference/profile-commands.md)——即独立的 `~/.hermes/` 子目录，允许您在同一个安装环境中运行多个独立的 Agent（拥有不同的 SOUL、技能、内存、会话及凭据）。在官方 Docker 镜像中，s6 监控系统会将每个配置文件视为一级受监控服务，因此推荐的部署方式是**使用一个容器来托管所有配置文件**。

通过 `hermes profile create <name>` 创建的每个配置文件都会获得以下功能：

- 位于 `/run/service/gateway-<name>/` 的专用 s6 服务槽位，该槽位由运行时动态注册——无需重新构建容器。
- 出现故障时可自动重启，由 `s6-supervise` 负责实现延迟重启机制。
- 每个配置文件都有独立的日志轮转机制，日志存储在 `${HERMES_HOME}/logs/gateways/<name>/current` 目录下（共保留 10 个归档文件，每个 1 MB）。
- 容器重启后状态仍可保持：启动时的状态同步工具会读取每个配置文件目录中的 `gateway_state.json` 文件，仅对上次记录状态为“运行中”的配置文件重新启动服务。只有通过 `hermes gateway stop` 显式停止的网关会在重启后保持关闭状态——而容器重启、镜像升级或意外退出都会使状态仍显示为“运行中”，因此网关会在下一次启动时自动恢复运行。

在主机上执行的生命周期管理命令，在容器内部同样可以正常使用。

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

在底层实现中，容器内的 `hermes gateway start/stop/restart` 命令会被拦截并路由至对应服务目录下的 `s6-svc`；因此您无需直接学习 s6 的命令。若需获取 supervisor 的原始状态，可使用命令 `/command/s6-svstat /run/service/gateway-<name>`（请注意，`/command/` 仅对 supervision 树生成的进程有效——从 `docker exec` 命令中调用时需使用绝对路径）。

### 从容器外部访问多个配置文件

从外部访问配置文件的网关有两种不同的途径，且其行为各异——切勿将二者混淆：

**Hermes 桌面端（以及网页控制面板）。** 桌面应用的 **远程网关** 连接实际上是与 `hermes dashboard` 后端进行通信（默认端口为 **9119**，可通过设置 `HERMES_DASHBOARD=1` 启用）——而非 OpenAI API 服务器。同一个仪表板后端可为所有处于同一位置的配置文件提供服务：应用中的配置文件切换器会在每次请求中传递目标配置文件信息，而后端则会在磁盘上打开该配置文件的 `HERMES_HOME` 目录。因此，对于桌面端而言，无需为每个配置文件单独设置端口或连接——通过切换器，单个 `:9119` 连接即可覆盖所有配置文件。

**兼容 OpenAI 的 API 客户端（如 Open WebUI、LobeChat、/v1/...）。** 这些客户端会与每个配置文件的 **API 服务器** 进行通信，而每个配置文件都会绑定 **端口 8642**（该端口值来自 `API_SERVER_PORT` 或 `platforms.api_server.extra.port` 的设置——系统不会自动分配端口，也不存在 `config.yaml` 或 `gateway.port` 相关键值）。如果希望某个客户端能够连接至*特定的另一个*配置文件，请在该配置文件自身的 `.env` 文件中为其指定独立的 `API_SERVER_PORT`；否则，其对应的网关也会尝试绑定端口 8642，从而导致与默认配置文件的冲突。

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

请将 `API_SERVER_PORT` 的配置保存在每个配置文件的**独立** `.env` 文件中，切勿放在整个容器的 `environment:` 块中——全局值会导致所有配置文件都使用同一个端口，从而引发冲突。在使用桥接网络时，需在 `docker-compose.yml` 中指定额外的端口映射（如 `- "8643:8643"`）；而当设置为 `network_mode: host` 模式时，该端口可直接在主机上访问。默认配置文件的 8642 端口连接方式则保持不变。

### 为何选择单个容器承载多个配置文件，而非多个容器？

在迁移到 s6 之前，由于容器内部没有可用于管理多个网关的监控进程，因此“一个配置文件对应一个容器”是被推荐的架构。但随着 s6 成为 PID 1 进程，这种情况已不再必要，而且单容器架构在几乎所有方面都更为简洁：

| 对比项 | 单容器多配置文件 | 一个配置文件一个容器 |
|---|---|---|
| 磁盘开销 | 一个镜像、一个打包好的虚拟环境、一个 Playwright 缓存 | N 个镜像 / N 个缓存 |
| 内存开销 | 共享 Python 解释器缓存及 node_modules 文件 | 每个容器都重复存储这些资源 |
| 配置文件创建 | 使用 `docker exec ... hermes profile create <name>`，耗时数秒 | 需要执行新的 `docker run` 命令，还需分配端口并挂载配置文件 |
| 配置文件故障恢复 | 由 `s6-supervise` 自动重启 | 依赖 Docker 的 `--restart unless-stopped` 参数（恢复速度较慢，且会终止其他正在运行的任务） |
| 日志管理 | 通过 `s6-log` 实现按配置文件分离的日志轮转，另附容器启动审计日志 | 需通过 `docker logs <name>` 查看每个容器的日志，且无内置轮转功能 |
| 备份操作 | 仅需备份一个 `~/.hermes` 目录 | 需协调管理 N 个目录 |
默认配置文件（`default`）会在首次启动时自动注册，因此新创建的容器会直接配备一个受监控的网关。其他配置文件则属于运行时的附加组件。

### 何时需要单独的容器

默认情况下，配置文件会嵌入到同一个容器中。只有出于特定原因时，才需为每个配置文件启动独立的容器：

- **按工作负载实现资源隔离**——例如，配置文件A中的浏览器工具进程失控时，不应影响配置文件B的正常运行。通过容器可为每个配置文件单独设置`--memory`/`--cpus`参数。
- **独立的镜像锁定**——不同工作负载可使用不同的上游镜像版本。
- **网络分段**——每个配置文件可拥有独立的Docker网络（例如一个用于面向客户，另一个用于内部使用）。
- **合规性要求/风险控制**——不同的配置文件应使用独立的凭证，且不会共享同一操作系统级别的进程树。

在这些情况下，应为每个配置文件定义一个服务，并为其指定不同的`container_name`、`volumes`和`ports`参数：

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

关于[持久卷](#persistent-volumes)的警告依然适用：切勿让两个容器同时指向同一个`~/.hermes`目录。每个容器内的s6管理器都会独立管理自身的配置文件集；跨容器共享数据卷会导致会话文件和内存存储损坏。

## 日志存储位置

s6容器拥有四种不同的日志输出方式，因此“为何在我的`docker logs`中看不到任何内容？”是一个常见的问题。具体对应关系如下表所示：

| 日志来源 | 存储位置 | 查看方法 |
|---|---|---|
| **按配置文件划分的网关**（通过`hermes gateway run`启动的网关以及s6管理下的各配置文件网关） | 同时输出到两个位置：<br>1. `docker logs <container>`（实时显示，无前缀）<br>2. `${HERMES_HOME}/logs/gateways/<profile>/current`（按时间轮转，采用ISO-8601格式标记时间，共保存10个版本，每个1MB） | 在主机上使用`docker logs -f hermes`或`tail -F ~/.hermes/logs/gateways/default/current`查看 |
| **控制面板**（当设置`HERMES_DASHBOARD=1`时） | `docker logs <container>`（无前缀） | 使用`docker logs -f hermes`查看，日志内容会与网关相关信息混排显示 |
| **启动同步器**（记录每次容器启动时恢复了哪些配置文件网关） | `${HERMES_HOME}/logs/container-boot.log`（只读审计日志） | 使用`tail -F ~/.hermes/logs/container-boot.log`查看 |
| **通用Hermes日志**（如`agent.log`、`errors.log`） | `${HERMES_HOME}/logs/`（会根据配置文件区分） | 使用命令`docker exec hermes hermes logs --follow [--level WARNING] [--session <id>]`查看 |

有两点实际注意事项值得了解：

- 位于 `logs/gateways/<profile>/current` 的文件内容会在容器重启后依然保留。而 `docker logs` 仅保存当前容器运行期间的输出信息（在执行 `docker rm` 后会被清除）；那些经过轮转的日志文件则会存储在绑定挂载的卷中。
- 启动协调器的审计日志格式为 `<iso-timestamp> profile=<name> prior_state=<state> action=<registered|started>`，因此只需执行 `grep profile=coder ~/.hermes/logs/container-boot.log`，即可快速查看某个配置文件上次被恢复的时间，以及 s6 是否自动启动了该配置文件。

## 环境变量传递

API 密钥会从容器内的 `/opt/data/.env` 文件中读取。您也可以直接传递环境变量：

```sh
docker run -it --rm \
  -v ~/.hermes:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/hermes-agent
```

直接使用 `-e` 参数可覆盖 `.env` 文件中的值。这在需要避免将敏感密钥保存在磁盘上的 CI/CD 或 Secrets Manager 集成场景中非常有用。

:::note 正在寻找以 Docker 作为**终端后端**？
本页面介绍的是在 Docker 中运行 Hermes 的方法。如果您希望让 Hermes 在 Docker 沙箱容器内执行代理的 `terminal` / `execute_code` 请求（即一个跨多个 Hermes 进程共享的长期运行的容器——参见问题 #20561），则需要使用单独的配置项：`terminal.backend: docker`，以及 `terminal.docker_image`、`terminal.docker_volumes`、`terminal.docker_forward_env`、`terminal.docker_env`、`terminal.docker_run_as_host_user`、`terminal.docker_extra_args`、`terminal.docker_persist_across_processes` 和 `terminal.docker_orphan_reaper`。完整的配置项及容器生命周期规则请参阅 [配置 → Docker 后端](configuration.md#docker-backend)。
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

首先运行 `docker compose up -d` 启动服务，然后使用 `docker compose logs -f` 查看日志。受监管网关的标准输出还会被同步到卷中的 `${HERMES_HOME}/logs/gateways/<profile>/current` 目录——完整的日志路由规则请参阅[日志存储位置](#where-the-logs-go)。

## 可选功能：Linux桌面音频桥接

在Docker环境中实现语音模式需要满足两个条件：必须允许Hermes探测容器内的音频设备，同时容器还需能够连接到主机的音频服务器。以下配置适用于那些提供PulseAudio兼容套接字的Linux桌面系统，同时也支持多种PipeWire架构。

:::caution
这仅是Linux桌面的临时解决方案，并非Docker Desktop的通用功能。当您的主机音频已正常工作，但希望在Hermes容器内使用CLI语音模式时，此方法十分有用。如果Hermes仍显示“正在Docker容器中运行——无音频设备”，请使用包含针对`PULSE_SERVER`/`PIPEWIRE_REMOTE`的Docker音频探测功能的构建版本。
:::

首先，在Compose文件旁创建一个ALSA配置文件：

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

接着，构建一个安装了 ALSA PulseAudio 插件的小型派生镜像：

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

请使用您的主机 UID/GID 启动该进程，以便容器内的程序能够访问针对用户的音频套接字：

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
| 磁盘空间（数据量） | 500 MB | 2+ GB（会随会话数/技能数量增加而增长） |

浏览器自动化功能（Playwright/Chromium）是内存消耗最大的部分。如果无需使用浏览器工具，1 GB 内存即可满足需求；若需启用浏览器工具，则至少需要分配 2 GB 内存。

在 Docker 中设置资源限制：

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

- Python 3.13 及其依赖项，这些依赖项通过 `uv sync --frozen --no-install-project` 命令从锁定文件中同步获取，用于支持各类预集成功能（如 `all`、`messaging`、Anthropic/Bedrock/Azure 身份验证、Hindsight、Matrix 等）；之后会进行无需额外依赖的可编辑安装，以便直接使用 Hermes 本身。
- Node.js 26 及 npm（用于浏览器自动化、WhatsApp 桥接功能、TUI/桌面应用打包以及工作区构建工具）。
- 带 Chromium 的 Playwright（通过 `npx playwright install --with-deps chromium --only-shell` 安装）。
- 作为系统工具的 ripgrep、ffmpeg、git 以及 `xz-utils`。
- **`docker-cli`** — 使在容器中运行的智能体能够控制宿主机的 Docker 守护进程（可通过绑定挂载 `/var/run/docker.sock` 启用该功能），从而执行 `docker build`、`docker run`、容器检查等操作。
- **`openssh-client`** — 允许在容器内部使用 [SSH 终端后端](/user-guide/configuration#ssh-backend)。该后端会调用系统自带的 `ssh` 工具；若缺少此组件，在容器化环境中安装时会静默失败。
- WhatsApp 桥接功能（位于 `scripts/whatsapp-bridge/` 目录中）。
- 作为 PID 1 进程的 **[`s6-overlay`](https://github.com/just-containers/s6-overlay) v3**（取代了旧版的 `tini`）——负责监控控制面板及各用户配置的网关，可在进程崩溃时自动重启、清理僵尸子进程并转发信号。
在运行时，该镜像将 `/opt/hermes` 视为不可修改的安装目录。那些需要在 Docker 环境中具备的可选 Python 扩展、Node 工作空间以及 TUI 资源，都必须在镜像构建阶段预先嵌入；由于禁用了运行时的延迟安装机制，因此监督网关及 `docker exec hermes …` 命令不会试图将依赖项文件写回该只读的源代码目录中。

容器的 `ENTRYPOINT` 是一个小型调度程序（`docker/entrypoint-dispatch.sh`）。在容器拥有 PID 1 的正常 Docker/Podman 环境下，它会执行 s6-overlay 的 `/init`，从而启用下文所述的完整监督机制。而当某个平台将自己的 PID-1 启动程序封装在镜像的入口点之上时（如 Fly.io Machines、`docker run --init`，以及某些 Nomad/Kubernetes 配置），/init 会因 “s6-overlay-suexec: fatal: can only run as pid 1” 而终止运行——此时调度程序会直接启动 stage2 启动流程，并跳过 s6 直接执行主封装程序。在这种备用路径下，用户请求的命令依然可以运行，但监督服务（如控制面板、各用户配置的网关）将无法使用。

在 PID 1 的正常路径下，/init 会：
1. 以 root 权限运行 `/etc/cont-init.d/01-hermes-setup`（即 `docker/stage2-hook.sh`）：可选项包括 UID/GID 重映射、修复卷所有权、在首次启动时生成 `.env`、`config.yaml` 和 `SOUL.md` 文件；除非设置了 `HERMES_SKIP_CONFIG_MIGRATION=1`，否则会自动执行非交互式的配置架构迁移，并同步已打包的技能。

2. 运行 `/etc/cont-init.d/02-reconcile-profiles`（即 `hermes_cli.container_boot`）：该脚本会遍历 `$HERMES_HOME/profiles/<name>/` 目录，在 `/run/service/gateway-<profile>/` 下为每个配置文件创建对应的 gateway s6 服务槽，并仅自动启动那些上次记录状态为“运行中”的服务（详情参见[按配置文件管理的网关监控](#per-profile-gateway-supervision)）。

3. 启动静态的 `main-hermes` 和 `dashboard` s6-rc 服务。

4. 以容器的 CMD 作为主程序执行（即 `/opt/hermes/docker/main-wrapper.sh`），该程序会处理用户通过 `docker run` 传递的参数：
   - 未传入参数 → 使用默认值 `hermes`
   - 第一个参数是 PATH 中的可执行文件（如 `sleep`、`bash`）→ 直接执行该命令
   - 其他情况 → 执行 `hermes <参数>`（即传递子命令）
   当此主程序退出时，容器也会随之退出，并携带其对应的退出码。
:::warning 版本变更与 s6 之前的镜像差异  
当前，容器的 ENTRYPOINT 已更改为 `entrypoint-dispatch.sh` 调度器（该调度器会在 PID 1 下调用 s6-overlay 的 `/init`），而非 `/usr/bin/tini`。所有五种文档中记载的 `docker run` 使用方式（无参数、`chat -q "…"`、`sleep infinity`、`bash`、`--tui`）在功能上与基于 tini 的镜像完全一致。如果您使用的下游封装工具依赖于 tini 特有的信号处理机制或硬编码了 `/usr/bin/tini --` 的调用方式，请继续使用旧版本的镜像标签。  
:::

:::warning 权限模型  
除非您在命令链中保留 `/init`（或等效的、会将控制权转交给 stage2 钩子的旧版 `docker/entrypoint.sh`），否则请勿覆盖镜像的 ENTRYPOINT。s6-overlay 的 `/init` 以 root 权限运行，因此可在首次启动时修改卷的所有权；之后，对于所有受监控的服务以及主程序，它都会通过 `s6-setuidgid` 降权为 `hermes` 用户。在官方镜像中，默认禁止以 root 权限启动 `hermes gateway run`，因为这可能会导致 `/opt/data` 目录下留下 root 所有的文件，进而影响后续仪表板或网关的启动。仅当您明确接受此类风险时，才可设置 `HERMES_ALLOW_ROOT_GATEWAY=1`。  
:::

### `docker exec` 会自动降权为 `hermes` 用户

`docker exec hermes <cmd>` 命令默认会在容器内以 root 权限运行，但该镜像在 `/opt/hermes/bin/hermes`（PATH 中的优先路径）处提供了一个精简的代理程序，它能检测到以 root 身份调用的操作，并通过 `s6-setuidgid hermes` 以透明方式重新执行相应命令。因此，诸如 `docker exec hermes login`、`docker exec hermes profile create …`、`docker exec hermes setup` 等命令无需额外使用 `--user` 参数，即可将文件写入 UID 为 10000 的用户所有——这样被监控的网关就能读取这些文件。而非 root 身份的调用者（即被监控的进程本身、通过 `docker exec --user hermes` 启动的进程，以及容器内的看板子代理）则会直接执行虚拟环境中的二进制文件，从而避免了在高频使用的路径上产生额外开销。

如果确实需要保持 root 权限行为的 `docker exec` 操作（例如进行诊断会话、查看仅 root 可访问的状态，或处理 root 所拥有的位于 `/opt/data` 之外的文件），则可在每次调用时手动关闭该功能。

```sh
docker exec -e HERMES_DOCKER_EXEC_AS_ROOT=1 hermes <cmd>
```

该桥接程序可识别 `1` / `true` / `yes`（不区分大小写）。任何其他输入——包括诸如 `=0` 这样的拼写错误——都会导致任务被直接丢弃，因此无法实现静默的退出选项。如果系统未安装 `s6-setuidgid`（即那些去除了 s6-overlay 功能的自定义构建版本），该桥接程序将拒绝以 root 权限运行，并返回代码 126，从而明确显示出权限模型的缺陷；而不会退回到旧有的糟糕状况，即在那种情况下，执行 `docker exec hermes login` 会将 `auth.json` 的权限设置为 `root:root`，进而破坏每个聊天平台消息的授权机制。

### 每个配置文件的网关监控

通过 `hermes profile create <name>` 创建的每个配置文件，都会自动在 `/run/service/gateway-<name>/` 下注册一个受 s6 监控的网关服务，且该服务能够在容器重启时保持状态并自动重启。有关面向用户的操作流程及生命周期管理命令，请参阅上文中的[多配置文件支持](#multi-profile-support)部分。

**相比旧版 s6 镜像，监控功能的优势在于：**

- 当网关崩溃后，`s6-supervise` 会在约1秒的延迟后自动重启它。  
- 若启用 `HERMES_DASHBOARD=1`，控制面板也会被纳入同一监控体系，并享有相同的自动重启机制。  
- 通过 `docker restart`、镜像升级（如 `docker compose up -d --force-recreate`）或意外退出等情况时，运行中的网关仍会保持在线状态：因为 cont-init 协调器会读取 `$HERMES_HOME/profiles/<name>/gateway_state.json`，如果上次记录的状态为“运行中”，则会自动重启该网关。只有通过显式执行 `hermes gateway stop` 才会将状态标记为“已停止”，从而使网关在重启后仍处于关闭状态；而在重启或升级过程中发送给容器或 s6 的 SIGTERM 信号会被视为“仍在运行”，网关会自动重新启动。  
- 每个配置文件的网关日志会保存在 `$HERMES_HOME/logs/gateways/<profile>/current` 目录下（由 `s6-log` 负责日志轮转），而协调器的操作记录则会每次启动时追加到 `$HERMES_HOME/logs/container-boot.log` 中。完整的日志路径映射请参见 [日志存储位置](#where-the-logs-go)。  
- 容器内的 `hermes status` 命令会显示 “Manager: s6 (container supervisor)”。如需查看原始的监控状态，可使用命令 `/command/s6-svstat /run/service/gateway-<name>`（请注意，/command/ 只对监控体系下的进程有效；从 `docker exec` 中调用该命令时需使用绝对路径）。  

## 升级

请拉取最新镜像并重新创建容器。您的数据目录将会被保留，且在启动网关之前，容器会针对已挂载的 `$HERMES_HOME/config.yaml` 文件执行非交互式的配置架构迁移。当需要执行迁移时，Hermes 会首先在 `config.yaml` 和 `.env` 文件旁生成带有时间戳的备份文件。

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

仅当您需要在让新镜像覆盖现有配置之前手动检查或迁移持久化配置时，才需设置 `HERMES_SKIP_CONFIG_MIGRATION=1`。

## 技能与凭证文件

当以 Docker 作为执行环境时（即不采用上述方法，而是让代理在 Docker 沙箱中运行命令——详见[配置 → Docker 后端](./configuration.md#docker-backend)），Hermes 会为所有工具调用复用同一个长期运行的容器，并自动将技能目录（`~/.hermes/skills/`）以及技能所指定的任何凭证文件以只读卷的形式挂载到该容器中。无需手动配置，技能脚本、模板及相关引用即可在沙箱内使用；由于该容器会持续存在直至 Hermes 进程结束，因此您安装的依赖项或生成的文件也会在后续的工具调用中依然可用。

SSH 和 Modal 后端也采用相同的同步机制——在每次执行命令之前，都会通过 rsync 或 Modal 挂载 API 将技能与凭证文件上传至容器中。

## 在容器中安装更多工具

官方镜像已预装了一组精选的实用工具（详见[Dockerfile 的功能](#what-the-dockerfile-does)），但并非代理可能需要的所有工具都已预置。根据所需的工作量和稳定性，共有五种推荐方案可供选择。

### 使用 npm 或 Python 工具——采用 `npx` 或 `uvx`

对于任何发布在 npm 或 PyPI 上的工具，可指示 Hermes 通过 `npx`（npm）或 `uvx`（Python）来运行该工具，并将其命令存储在持久内存中。如果该工具需要配置文件或凭据，则指示其将这些文件保存到 `/opt/data` 目录下（例如 `/opt/data/<tool>/config.yaml`）。

依赖项会根据需求动态获取，并在容器运行期间被缓存。保存在 `/opt/data` 下的配置文件由于存储在绑定挂载的主机目录中，因此能够跨容器重启而保留。虽然执行 `docker rm` 后包缓存会被重建，但下次运行该工具时，`npx` 和 `uvx` 会自动重新获取所需依赖。

### 其他工具（apt 包、二进制文件）——安装并记忆

对于那些不在 npm 或 PyPI 上的工具，比如 `apt` 包、预编译的二进制文件，或是镜像中尚未包含的语言运行时环境，需告知 Hermes 具体的安装方式（例如 `apt-get update && apt-get install -y <package>`），并让它记住该安装命令。这样，该工具就会在容器整个生命周期内持续存在；当容器重启后再次需要该工具时，Hermes 会自动重新执行安装命令。

这种方法非常适合那些安装快速且使用频率较低的工具。而对于需要频繁使用的工具，则建议采用以下方法。

### 持久化安装——构建衍生镜像

如果要求每个容器启动时都能立即使用某工具，且不能有重新安装的延迟，那么可以构建一个基于 `nousresearch/hermes-agent` 的新镜像，并将该工具作为独立层进行安装：

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

入口脚本以及 `/opt/data` 的使用规则保持不变，因此本页面的其余内容依然适用。在拉取更新版本的 upstream `nousresearch/hermes-agent` 时，请务必重新构建镜像。

### 复杂工具或多服务架构——运行侧车容器

对于那些自带服务（如数据库、Web服务器、消息队列、无头浏览器集群）或体积过大而无法嵌入Hermes容器中的工具，可将其作为独立容器运行在共享的Docker网络中。Hermes可通过容器名称来访问这些侧车容器，方式与访问本地推理服务器相同（详见[连接本地推理服务器](#connecting-to-local-inference-servers-vllm-ollama-etc)）。

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

在 Hermes 容器内部，可通过 `http://my-tool:<port>`（或该工具所使用的其他协议地址）访问 sidecar。这种架构能够让各个服务的生命周期、资源限制及升级频率保持独立，同时避免因某些工具仅需的依赖项而使 Hermes 镜像变得臃肿。

### 具有广泛实用价值的工具——提交问题或 pull request

如果某款工具可能对大多数 Hermes Agent 用户都有用，建议直接为官方项目做出贡献，而非将其封装在私有的衍生镜像中。请在 [hermes-agent 仓库](https://github.com/NousResearch/hermes-agent) 上提交问题或 pull request，详细介绍该工具及其应用场景。被纳入官方镜像的工具能让所有用户受益，同时也能避免维护下游分支所带来的额外工作量。

## 连接本地推理服务器（vLLM、Ollama 等）

当在 Docker 中运行 Hermes，而你的推理服务器（vLLM、Ollama、text-generation-inference 等）也在主机上或另一个容器中运行时，需要特别关注网络配置问题。

### Docker Compose（推荐方案）

将这两个服务置于同一个 Docker 网络中。这是最为可靠的做法：

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

接着在您的 `~/.hermes/config.yaml` 文件中，使用**容器名称**作为主机名。

```yaml
model:
  provider: custom
  model: my-model
  base_url: http://vllm:8000/v1
  api_key: "none"
```

:::提示 关键要点
- 请使用**容器名称**（`vllm`）作为主机名——而非 `localhost` 或 `127.0.0.1`，因为这些地址指的是 Hermes 容器本身。
- `model` 的值必须与您传递给 vLLM 的 `--served-model-name` 参数一致。
- 将 `api_key` 设置为任意非空字符串（vLLM 虽要求该字段存在，但默认不会对其进行验证）。
- `base_url` 后面**不要**加斜杠。
:::

### 独立运行 Docker 容器（无需 Compose）

如果您的推理服务器直接在主机上运行（而非在 Docker 容器中），则在 macOS/Windows 系统上使用 `host.docker.internal`，在 Linux 系统上使用 `--network host`：

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

:::warning 当使用 `--network host` 选项时，`-p` 参数将被忽略——所有容器端口都会直接在主机上暴露。
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

Ollama 的使用方式类似。如果 Ollama 在主机上运行，请使用 `host.docker.internal:11434`（macOS/Windows）或 `127.0.0.1:11434`（已启用 `--network host` 选项的 Linux 系统）。如果 Ollama 在同一 Docker 网络中的独立容器内运行：

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
- 若开启了端口暴露功能，则可能存在端口冲突

### “权限被拒绝”错误

容器中的 stage2 钩子会在每个受监控的服务中通过 `s6-setuidgid` 函数，将权限降至非 root 用户 `hermes`（UID 10000）。如果您的主机上的 `~/.hermes/` 目录属于其他 UID，建议设置 `HERMES_UID`/`HERMES_GID`——或与其对应的 `PUID`/`PGID` 别名——使其与 LinuxServer.io 及 NAS 镜像中的设置保持一致，从而确保权限匹配；或者确保数据目录具有写入权限：

```sh
chmod -R 755 ~/.hermes
```

在 NAS（如 UGOS、Synology、unRAID）上，数据目录通常采用**绑定挂载**方式，其所有权属于主机 UID，容器无法对其进行 `chown` 操作。因此请将 `PUID`/`PGID`（或 `HERMES_UID`/`HERMES_GID`）设置为该主机用户，这样运行时进程就会以挂载点的所有者身份执行，而非 UID 10000。

```sh
docker run -d \
  --name hermes \
  -e PUID=1000 -e PGID=10 \
  -v /volume1/docker/hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

`docker exec hermes <cmd>` 命令同样会自动切换到 UID 10000 用户——详情及针对单次调用的取消设置方法，请参阅[“docker exec”会自动切换到 “hermes” 用户](#docker-exec-automatically-drops-to-the-hermes-user)。

### 每次执行 `docker exec` 都出现“权限被拒绝”的错误（安装目录权限为 0700）

2026 年 8 月底之前构建的镜像存在一个缺陷：若将凭证文件直接保存在 `/opt/hermes` 目录下，该目录的权限会被设置为 `0700`，从而导致 “hermes” 用户（UID 10000）无法访问安装目录。这样一来，每次执行 `docker exec` 都会因“权限被拒绝”而失败。

通过拉取更新版本的镜像并重新创建容器，即可永久解决此问题（新版本的安装目录权限为 `0755`，且当前版本已不再对此进行限制）。如果需要在不重新创建容器的情况下恢复正在运行的容器：

```sh
docker exec -u root hermes chmod 0755 /opt/hermes
```

### 浏览器工具无法使用

Playwright 需要共享内存。请在您的 Docker 运行命令中添加 `--shm-size=1g`：

```sh
docker run -d \
  --name hermes \
  --shm-size=1g \
  -v ~/.hermes:/opt/data \
  nousresearch/hermes-agent gateway run
```

### 网络故障后网关无法重新连接

`--restart unless-stopped` 参数可解决大多数临时性故障。如果网关出现卡死情况，请重启该容器：

```sh
docker restart hermes
```

### 检查容器运行状态

```sh
docker logs --tail 50 hermes          # Recent logs
docker run -it --rm nousresearch/hermes-agent:latest version     # Verify version
docker stats hermes                    # Resource usage
```
