---
sidebar_position: 4
---

# 同时运行多个网关

可在单台机器上将多个[配置文件](./profiles.md)作为托管服务来运行——每个配置文件拥有独立的机器人令牌、会话及内存。本页面将介绍相关运营方面的注意事项：如何同时启动所有配置文件、查看跨配置文件的日志、防止主机进入睡眠状态，以及如何解决 launchd/systemd 系统中常见的异常问题。

如果您仅运行一个 Hermes 代理，则无需阅读本页面——基础内容请参阅[配置文件](./profiles.md)。

## 何时使用此方法

当您需要同时让两个或更多 Hermes 代理保持在线时，可采用此设置。常见应用场景包括：

- 在一个 Telegram 机器人上使用个人助手功能，在另一个机器人上使用编程代理功能
- 每位家庭成员或每个 Slack 工作空间对应一个代理
- 配置相同的沙箱环境与生产环境实例
- 研究用代理、写作用代理以及由 cron 脚本驱动的机器人——它们各自拥有独立的内存和技能

每个配置文件本身都已拥有针对相应平台的 LaunchAgent（`ai.hermes.gateway-<name>.plist`）或 systemd 用户服务（`hermes-gateway-<name>.service`）。本指南旨在提供集中管理这些服务的方案。

## 快速入门

```bash
# Create profiles (once)
hermes profile create coder
hermes profile create personal-bot
hermes profile create research

# Configure each
coder setup
personal-bot setup
research setup

# Install each gateway as a managed service
coder gateway install
personal-bot gateway install
research gateway install

# Start them all
coder gateway start
personal-bot gateway start
research gateway start
```

就是这样——三个独立的智能体，每个都在独立的进程中运行，一旦崩溃或用户登录就会自动重启。

## 另一种方案：为所有配置文件使用一个网关（多路复用）

上述方案是**为每个配置文件运行一个进程**。这是默认设置，也适用于大多数场景。但在拥有大量配置文件的服务器上——或者在使用容器部署且为每个配置文件单独运行进程会带来较大运营负担的情况下——你可以选择运行**一个单一的多路复用网关**：默认配置文件的网关将成为唯一的入口进程，负责处理该系统中*所有*配置文件的消息。

此功能为**可选设置，默认处于关闭状态**。当它处于关闭状态时，本页面的内容不会发生变化——以下所有功能都将处于无效状态。

### 何时选择多路复用方案

- 在容器/VPS部署环境中，管理N个监控单元、N个端口以及N个PID文件会带来很大负担。
- 存在许多流量较低的配置文件，每个都不值得单独运行一个完整进程。
- 您希望由单个组件来负责启动、监控和重启所有配置文件。

如果需要实现配置文件之间的严格进程级隔离（如独立的内存占用、独立的崩溃域，以及能够重启某个配置文件而不影响其他配置文件），则应继续使用“每个配置文件一个进程”的方案。

### 如何启用该功能

在**默认配置文件**上设置相关标志（该配置文件负责管理多路复用器），然后重启其网关即可：

```bash
hermes config set gateway.multiplex_profiles true
hermes gateway restart
```

或者，可在默认配置文件的 `~/.hermes/config.yaml` 中进行设置：

```yaml
gateway:
  multiplex_profiles: true
```

（为方便起见，该标志也可作为顶层参数 `multiplex_profiles: true` 使用。）在下次启动时，默认网关会枚举所有配置文件，使用每个配置文件自身的凭证来加载该文件下启用的平台，并将每条传入的消息路由到其所属的配置文件。每次处理都会加载该路由目标配置文件的配置、技能、内存、SOUL以及**提供程序密钥**——各配置文件之间的凭证绝不会被共享。

对于这些辅助配置文件，您无需再运行 `hermes gateway start` 命令——默认网关会负责为它们提供服务。具体变更内容请参见下方说明。

### 启用多路复用功能后会发生哪些变化？

启用该标志会改变部分功能的运作方式。一旦关闭该标志，所有这些变化都会恢复原状。

#### 1. 辅助配置文件不得自行启动网关

在多路复用器运行的情况下，使用带命名配置文件的 `hermes gateway start` / `run` 命令将会引发**严重错误**，系统会强制引导您使用多路复用器。

```
The default gateway is running as a profile multiplexer and already serves
profile 'coder'. ...
```

多路复用器是一个独立的入口进程；若再创建第二个配置文件网关，将会使该配置文件对应的所有平台陷入双重绑定状态。仅当您确实需要为该配置文件单独设置一个进程时才使用 `--force` 参数（在多路复用器正在运行时不建议这样做）。因此，在多路复用模式下**不会**使用本页前面提到的跨配置文件生命周期封装脚本——您只需管理默认网关即可。

#### 2. HTTP 入站平台通过 `/p/<profile>/` 的 URL 前缀访问

次要配置文件的 Webhook（以及其他 HTTP 入站）流量会通过配置文件前缀发送到默认监听器，而非使用第二个端口。

```
# default profile
POST http://host:8644/webhooks/<route>
# the "coder" profile, same listener
POST http://host:8644/p/coder/webhooks/<route>
```

前缀中存在未知或未配置的配置文件时，系统会返回 `404` 错误。由于共享的监听器已以此方式为所有配置文件提供服务，因此**辅助配置文件本身绝不能启用端口绑定功能**——否则将构成配置错误，导致网关无法启动，并会同时显示该配置文件名称与相关平台名称。

```
Profile 'coder' enables the port-binding platform 'webhook', but
gateway.multiplex_profiles is on. ... Remove platforms.webhook from profile
'coder's config.yaml (configure it only on the default profile).
```

本规则所涵盖的端口绑定平台包括：`webhook`、`api_server`、`msgraph_webhook`、`feishu`、`wecom_callback`、`bluebubbles`、`sms`。仅可在**默认配置文件**中为这些平台中的任意一个进行配置；每个配置文件均可通过其 `/p/<profile>/` 前缀访问。

#### 3. 每个凭据对应的平台仍需为每个配置文件配备独立令牌

轮询/连接型平台（如 Telegram、Discord、Slack、Matrix、Signal 等）支持多路复用，但为每个此类平台启用的配置文件都必须提供**独立的**机器人令牌——同一个令牌无法被两个配置文件同时使用。如果两个配置文件配置了相同的 `(platform, token)` 组合，系统会在启动时立即报错并指出这两个配置文件（详见[令牌冲突防护机制](#token-conflict-safety)——规则本身并未改变，只是现在在同一个进程内部进行强制管控）。

#### 4. 会话键以配置文件为命名空间

每个配置文件的会话都存储在 `agent:<profile>:…` 命名空间下，因此同一平台/聊天窗口中的两个配置文件的会话不会在共享的会话存储中发生冲突。**默认**配置文件会原封不动地保留原有的 `agent:main:…` 命名空间，因此基于默认配置文件的现有会话不会受到影响——无需迁移，也不会出现历史记录丢失的情况。

#### 5. 单一进程ID/锁机制及统一状态查询接口

整个系统仅存在一个进程级的进程ID和锁机制（即位于默认主目录下的多路复用器）。`hermes status` 命令可显示该多路复用器及其服务的所有配置文件；而 `hermes status -p <name>` 命令则可查看指定配置文件的状态。不过每个配置文件仍会在自己的目录下生成独立的 `runtime_status.json` 文件，因此现有的针对单个配置文件的状态查询工具仍可正常使用。

#### 未发生变更的内容

按配置文件隔离的 `.env` 凭据机制依然保留，甚至更为严格：每个配置文件中的键值只会在其自身作用域内解析，绝不会被合并到共享的环境中（这也意味着 MCP 服务器和看板工作进程等子进程只能访问其所在配置文件的机密信息）。看板功能、基于配置文件的技能/内存/SOUL 管理以及模型路由等功能，其行为方式都与使用独立网关时完全一致。

## 同时启动、停止或重启所有网关

CLI 已提供针对单个配置文件的生命周期管理命令。若需对所有配置文件执行相同操作，可将其封装在 Shell 循环中实现。请将以下代码保存到 `~/.local/bin/hermes-gateways` 文件中，并为其添加执行权限：

```sh
#!/bin/sh
set -eu

# Add or remove profile names here as you create / delete profiles.
profiles="default coder personal-bot research"

usage() {
  echo "Usage: hermes-gateways {start|stop|restart|status|list}"
}

run_for_profile() {
  profile="$1"
  action="$2"
  if [ "$profile" = "default" ]; then
    hermes gateway "$action"
  else
    hermes -p "$profile" gateway "$action"
  fi
}

action="${1:-}"
case "$action" in
  start|stop|restart|status)
    for profile in $profiles; do
      echo "==> $action $profile"
      run_for_profile "$profile" "$action"
    done
    ;;
  list)
    hermes gateway list
    ;;
  *)
    usage
    exit 2
    ;;
esac
```

接着：

```bash
hermes-gateways start      # start every configured profile
hermes-gateways stop       # stop every configured profile
hermes-gateways restart    # restart all
hermes-gateways status     # status across all
hermes-gateways list       # delegates to `hermes gateway list`
```

:::提示
使用 `hermes gateway <action>`（不带 `-p` 参数）即可调用 `default` 配置文件，而非 `hermes -p default gateway <action>`。上述封装脚本可兼容这两种调用方式。
:::

## 管理单个配置文件

每个配置文件都会自动安装的快捷命令：

```bash
coder gateway run        # foreground (Ctrl-C to stop)
coder gateway start      # start the managed service
coder gateway stop       # stop the managed service
coder gateway restart    # restart
coder gateway status     # status
coder gateway install    # create the LaunchAgent / systemd unit
coder gateway uninstall  # remove the service file
```

这些命令等同于 `hermes -p coder gateway <action>` —— 当配置文件别名未添加到 `PATH` 环境变量中，或需要从脚本中动态指定配置文件时，这些命令非常有用。

## 服务文件

每个配置文件都会安装一个具有唯一名称的服务，因此不同配置文件的安装不会发生冲突：

| 平台     | 路径                                                              |
| -------- | ----------------------------------------------------------------- |
| macOS    | `~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist`        |
| Linux    | `~/.config/systemd/user/hermes-gateway-<profile>.service`         |

默认配置文件会沿用原有的名称：`ai.hermes.gateway.plist` / `hermes-gateway.service`。

## 查看日志

每个配置文件都会将其日志写入独立的日志文件中：

```bash
# Default profile
tail -f ~/.hermes/logs/gateway.log
tail -f ~/.hermes/logs/gateway.error.log

# Named profile
tail -f ~/.hermes/profiles/<name>/logs/gateway.log
tail -f ~/.hermes/profiles/<name>/logs/gateway.error.log
```

同时流式传输每个配置文件的日志：

```bash
tail -f ~/.hermes/logs/gateway.log ~/.hermes/profiles/*/logs/gateway.log
```

该命令行工具还配备了结构化的日志查看器：

```bash
hermes logs -f                  # follow default profile
hermes -p coder logs -f         # follow one profile
hermes logs --help              # filters, levels, JSON output
```

## 查明实际正在运行的进程

```bash
hermes profile list             # profiles + model + gateway state
hermes-gateways status          # full status across every profile
launchctl list | grep hermes    # macOS — PIDs and labels
systemctl --user list-units 'hermes-gateway-*'   # Linux — units
```

## 编辑配置

每个配置文件都会将其配置保存在独立的目录中：

```
~/.hermes/profiles/<name>/
├── .env              # API keys, bot tokens (chmod 600)
├── config.yaml       # model, provider, toolsets, gateway settings
└── SOUL.md           # personality / system prompt
```

默认配置文件直接使用`~/.hermes/`目录下的那三个文件。

您可以使用任何编辑器或通过CLI来修改这些文件：

```bash
hermes config set model.model anthropic/claude-sonnet-4    # default profile
coder config set model.model openai/gpt-5                  # named profile
```

修改 `.env` 或 `config.yaml` 文件后，请重启受影响的网关：

```bash
coder gateway restart
# or, for everything:
hermes-gateways restart
```

## 保持主机处于唤醒状态

网关进程可以全天候运行，但操作系统在空闲时仍会尝试进入睡眠状态。为此有两种解决方案：

### macOS — `caffeinate`

`caffeinate` 是 macOS 自带的功能，可在其运行期间阻止系统进入睡眠状态，无需额外安装。

```bash
caffeinate -dis                    # block display, idle, and system sleep
caffeinate -dis -t 28800           # same, auto-exit after 8 hours
caffeinate -i -w $(cat ~/.hermes/gateway.pid) &   # awake while default gateway runs

# Persistent: run in background and forget
nohup caffeinate -dis >/dev/null 2>&1 &
disown

# Inspect / stop
pmset -g assertions | grep -iE 'caffeinate|prevent|user is active'
pkill caffeinate
```

| 标志   | 效果                                            |
| ------ | ------------------------------------------------- |
| `-d`   | 禁止显示器进入睡眠状态                           |
| `-i`   | 禁止系统空闲时进入睡眠状态（默认值）           |
| `-m`   | 禁止磁盘进入睡眠状态                             |
| `-s`   | 禁止系统进入睡眠状态（仅适用于交流电供电的 Mac）|
| `-u`   | 模拟用户操作活动（防止屏幕锁屏）                 |
| `-t N` | 运行 `N` 秒后自动退出                           |
| `-w P` | 当 PID 为 `P` 的进程退出时立即退出               |

:::warning 即使合上盖子，Mac 仍会进入睡眠状态
`caffeinate` 工具无法强制关闭 MacBook 上由硬件驱动的合盖睡眠功能。
如需在合上盖子时保持设备唤醒状态，请调整“节能设置”/“电池设置”，或使用第三方工具。
:::

### Linux — `systemd-inhibit` 或 `loginctl`

```bash
# Inhibit suspend while a command runs
systemd-inhibit --what=idle:sleep --who=hermes --why="gateways running" \
  sleep infinity &

# Allow user services to keep running after logout (recommended)
sudo loginctl enable-linger "$USER"
```

启用“持久运行”功能后，您的 systemd 用户单元（包括 `hermes-gateway-<profile>.service`）即便在 SSH 连接中断或系统重启的情况下仍会继续运行。

## 令牌冲突防护机制

每个配置文件都必须为不同的平台使用唯一的机器人令牌。如果两个配置文件使用了相同的 Telegram、Discord、Slack、WhatsApp 或 Signal 令牌，第二个网关将拒绝启动，并会提示出现冲突的配置文件名称作为错误信息。

审核方式：

```bash
grep -H 'TELEGRAM_BOT_TOKEN\|DISCORD_BOT_TOKEN' \
     ~/.hermes/.env ~/.hermes/profiles/*/.env
```

## 更新代码

`hermes update` 会一次性获取最新代码，并将新打包的技能同步到所有配置文件中：

```bash
hermes update
hermes-gateways restart
```

用户自定义的技能永远不会被覆盖。

## 故障排除

### “在域中找不到用户界面对应的服务：501 错误”

您在先执行了 `hermes gateway stop` 后又运行了 `hermes gateway start`。CLI 的 `stop` 命令会执行完整的 `launchctl unload` 操作，从而将该服务从 launchd 的注册表中移除。CLI 在执行 `start` 命令时会检测到此特定错误，并自动重新加载 plist 文件（显示“↻ launchd 任务已被卸载；正在重新加载服务定义”）。随后服务将正常启动，无需进行任何修复。

### 程序崩溃后的过期 PID

如果某个配置文件的网关状态显示为“未运行”，但实际上仍有进程在运行：

```bash
ps -ef | grep "hermes_cli.*-p <profile>"
cat ~/.hermes/profiles/<profile>/gateway.pid
kill -TERM <pid>          # graceful
kill -KILL <pid>          # if that fails after a few seconds
<profile> gateway start
```

### 强制对某项服务进行硬重置

```bash
# macOS
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist
launchctl load   ~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist

# Linux
systemctl --user restart hermes-gateway-<profile>.service
```

### 健康检查

```bash
hermes doctor                  # default profile
hermes -p <profile> doctor     # one profile
```
