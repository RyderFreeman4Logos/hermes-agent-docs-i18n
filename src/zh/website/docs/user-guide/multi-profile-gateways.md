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

就这样——三个独立的 Agent，每个都在独立的进程中运行，遇到故障或用户登录时都会自动重启。

## 同时启动、停止或重启所有网关

CLI 提供了针对单个配置文件的生命周期管理命令。若需对所有配置文件执行相应操作，可将其封装在 shell 循环中。请将以下代码片段保存到 `~/.local/bin/hermes-gateways` 文件中，并赋予执行权限 `chmod +x`：

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
