---
title: "Hermes S6 Container Supervision"
sidebar_label: "Hermes S6 Container Supervision"
description: "Modify, debug, or extend the s6-overlay supervision tree inside the Hermes Agent Docker image — adding new services, debugging profile gateways, understandin..."
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Hermes S6 容器监控功能

在 Hermes Agent Docker 镜像中修改、调试或扩展 s6-overlay 监控架构——包括添加新服务、调试配置文件网关，以及了解 Architecture B 主程序模式。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/devops/hermes-s6-container-supervision` 安装 |
| 路径 | `optional-skills/devops/hermes-s6-container-supervision` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent |
| 许可协议 | MIT |
| 支持平台 | linux |
| 标签 | `docker`, `s6`, `supervision`, `gateway`, `profiles` |
| 相关技能 | [`hermes-agent`](/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-hermes-agent), `hermes-agent-dev` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 加载的完整技能定义。技能处于激活状态时，Agent 就会看到这些指令作为操作指南。
:::

# Hermes s6-overlay 容器监控功能

## 何时使用此技能

在处理以下任务时，请加载此技能：
- 在 Hermes Docker 镜像中添加或删除静态服务（即那些应在每个容器启动时都进行监控的服务，例如控制面板）
- 排查为何某个基于配置文件的网关无法启动、重启失败，或在执行 `docker restart` 后仍无法正常运行
- 了解为何容器的 CMD 命令为 `/opt/hermes/docker/main-wrapper.sh`，以及参数是如何传递给用户程序的
- 修改 `cont-init.d` 启动脚本（如 UID 重映射、卷初始化、配置文件同步）
- 更改基于配置文件的网关所使用的运行脚本（第 4 阶段）

如果您只是运行 Hermes Agent 并希望使用 Docker，建议参阅 `website/docs/user-guide/docker.md`。

## 架构概览

<!-- ascii-guard-ignore -->
```
/init                                  ← PID 1 (s6-overlay v3.2.3.0)
├── cont-init.d                        ← oneshot setup, runs as root
│   ├── 01-hermes-setup                ← docker/stage2-hook.sh
│   │   ├── UID/GID remap
│   │   ├── chown /opt/data
│   │   ├── chown /opt/data/profiles (every boot)
│   │   ├── seed .env / config.yaml / SOUL.md
│   │   └── skills_sync.py
│   └── 02-reconcile-profiles          ← hermes_cli.container_boot
│       ├── chown /run/service (hermes-writable for runtime register)
│       └── walk $HERMES_HOME/profiles/<name>/gateway_state.json
│           → recreate /run/service/gateway-<name>/
│           → auto-start only those with prior_state == "running"
│
├── s6-rc.d (static services, in /etc/s6-overlay/s6-rc.d/)
│   ├── main-hermes/run                ← exec sleep infinity (no-op slot)
│   └── dashboard/run                  ← if HERMES_DASHBOARD=1, runs `hermes dashboard`
│
├── /run/service (s6-svscan watches; tmpfs)
│   ├── gateway-coder/                 ← runtime-registered per-profile
│   │   ├── type        ("longrun")
│   │   ├── run         ("#!/command/with-contenv sh ... exec s6-setuidgid hermes hermes -p coder gateway run")
│   │   ├── down        (marker — present means "registered but don't auto-start")
│   │   └── log/run     (s6-log → $HERMES_HOME/logs/gateways/coder/current)
│   └── ...
│
└── CMD ("main program")               ← /opt/hermes/docker/main-wrapper.sh
    └── routes user args: bare exec | hermes subcommand | hermes (no args)
        — exec'd by /init with stdin/stdout/stderr inherited (TTY for --tui)
```
## 核心文件

| 路径 | 功能 |
|---|---|
| `Dockerfile` | 配置 s6-overlay 安装、cont-init.d 脚本连接，以及设置 `ENTRYPOINT ["/init", "/opt/hermes/docker/main-wrapper.sh"]` |
| `docker/stage2-hook.sh` | 用于执行“旧版入口点逻辑”——包括 UID 重映射、文件所有权修改、初始化操作以及技能同步。该脚本以 cont-init.d/01-hermes-setup 的身份运行。 |
| `docker/cont-init.d/02-reconcile-profiles` | 每次容器启动时都会调用 `hermes_cli.container_boot`，从持久化存储中恢复配置文件网关槽位信息。 |
| `docker/main-wrapper.sh` | 容器的 CMD 文件。它负责处理用户传入的参数，通过 `s6-setuidgid` 调用 hermes，随后执行用户指定的程序。 |
| `docker/s6-rc.d/main-hermes/run` | 该脚本仅执行 `sleep infinity` 操作——由于存在对应的槽位，s6-rc 用户模块便有效；主 hermes 进程以 CMD 方式运行，而非作为受监督的服务运行。 |
| `docker/s6-rc.d/dashboard/run` | 带条件控制的服务——除非 `HERMES_DASHBOARD` 的值为真，否则会执行 `exec sleep infinity`。 |
| `docker/entrypoint.sh` | 为兼容旧版本设计的过渡脚本，通过 `exec` 调用 stage2 钩子脚本。那些硬编码了旧版入口点路径的外部脚本仍可正常使用。 |
| `hermes_cli/service_manager.py` | 包含 `S6ServiceManager` 类，提供 `register_profile_gateway`、`unregister_profile_gateway`、`start/stop/restart/is_running`、`list_profile_gateways` 等功能。 |
| `hermes_cli/container_boot.py` | 包含 `reconcile_profile_gateways()` 函数，用于遍历持久化配置文件，重新生成 s6 槽位，并将相关日志记录到 `container-boot.log` 中。 |
| `hermes_cli/gateway.py::_dispatch_via_service_manager_if_s6` | 用于拦截在容器环境中运行的 `hermes gateway start/stop/restart` 操作，将其路由至 s6 系统处理。 |

## 为何选择架构 B（以 CMD 作为主程序，而非由 s6 监督）

最初的方案（v1–v3）打算让主 hermes 作为受 s6-rc 监督的服务运行。但 s6-overlay v3 的两项机制阻碍了这一设计：

1. **cont-init.d 脚本无法接收 CMD 参数**——因此 stage2 钩子脚本无法解析 `docker run <image> chat -q "hi"` 这样的命令，从而无法为后续的 “run” 脚本设置 `HERMES_ARGS` 参数。
2. **`/run/s6/basedir/bin/halt` 不会传递写入到 `/run/s6-linux-init-container-results/exitcode` 的退出码**。无论如何，容器始终以 143（SIGTERM）代码退出。s6 的创建者 skarnet 在 [issue #477](https://github.com/just-containers/s6-overlay/issues/477) 中也证实了这一点：_“如果希望容器正常关闭，要么让 CMD 进程先退出，要么在没有 CMD 的情况下，手动设置所需的容器退出码，然后再调用 halt 命令”_。

因此，我们采用了 s6-overlay 原生的 CMD 设计模式：`ENTRYPOINT ["/init", "/opt/hermes/docker/main-wrapper.sh"]`。/init 会自动在用户参数前添加该包装脚本——这样一来，`docker run <image> --version` 这样的命令就会被转换为 `/init main-wrapper.sh --version`，而 `--version` 参数不会被 /init 的 POSIX shell 拦截。该包装脚本通过 `s6-setuidgid` 调用 hermes，随后执行用户指定的程序。该程序的退出码将直接成为容器的退出码，这与 s6 出现之前的 tini 架构行为完全一致。

相应的权衡是：在 s6 环境下，主 hermes 无法被监督。但这恰恰与它在 tini（即 s6 出现之前的镜像）环境中的行为相同。唯一新增的保障机制是对仪表板功能的监督——而存储在 `/run/service/` 目录下的各配置文件网关则享有完全的监督功能。

## 快速操作指南

### 验证运行中的容器中 PID 1 是否为 s6 进程

```sh
docker exec <c> sh -c 'cat /proc/1/comm; readlink /proc/1/exe'
# Expect: s6-svscan or init / /package/admin/s6/.../s6-svscan
```

### 检查配置文件网关服务

```sh
# /command/ isn't on docker-exec PATH — use absolute path
docker exec <c> /command/s6-svstat /run/service/gateway-<name>
# "up (pid …) … seconds"            → running
# "down (exitcode N) … seconds, normally up, want up, …" → s6 wants it up but the process keeps exiting (crash loop)
# "down … normally up, ready …"     → user stopped it
```

### 手动启动/停止服务

```sh
docker exec <c> /command/s6-svc -u /run/service/gateway-<name>   # up
docker exec <c> /command/s6-svc -d /run/service/gateway-<name>   # down
docker exec <c> /command/s6-svc -t /run/service/gateway-<name>   # SIGTERM (restart)
```

### 查看 cont-init 一致性检查器日志

```sh
docker exec <c> tail -n 50 /opt/data/logs/container-boot.log
# 2026-05-21T06:18:05+0000 profile=coder prior_state=running action=started
# 2026-05-21T06:18:05+0000 profile=writer prior_state=stopped action=registered
```

### 添加新的静态服务

1. 创建文件 `docker/s6-rc.d/<name>/type`，内容为 `longrun\n`；同时创建文件 `docker/s6-rc.d/<name>/run`（内容应为 `#!/command/with-contenv sh` 加上 `# shellcheck shell=sh`）。
2. 在服务运行脚本的开头使用命令 `s6-setuidgid hermes` 将权限设置为用户态（除非您确实需要以 root 权限运行）。
3. 创建空文件 `docker/s6-rc.d/<name>/dependencies.d/base`，以便该服务能够等待基础包的加载。
4. 创建空文件 `docker/s6-rc.d/user/contents.d/<name>`，以便该服务能够加入用户相关包组。
5. Dockerfile 中的 `COPY docker/s6-rc.d/` 指令会自动处理这些文件——无需其他修改。

### 更改针对不同配置文件的网关运行命令

请编辑 `hermes_cli/service_manager.py` 文件中的 `S6ServiceManager._render_run_script` 函数。在系统启动时进行服务同步的过程中，`hermes_cli/container_boot.py::_register_service` 也会调用该函数，因此它是配置信息的唯一来源。同时，请更新 `tests/hermes_cli/test_service_manager.py::test_s6_register_creates_service_dir_and_triggers_scan` 测试文件中的相应断言。

### 运行 Docker 测试套件

```sh
docker build -t hermes-agent-harness:latest .
HERMES_TEST_IMAGE=hermes-agent-harness:latest scripts/run_tests.sh tests/docker/ -v
# Expect 19 passed, 0 xfailed against the s6 image
```

该测试 harness 位于 `tests/docker/` 目录中，当未安装 Docker 时会自动跳过。每个测试的超时时间已被延长至 180 秒（详见 `tests/docker/conftest.py`）。

## 常见问题

### 使用 `docker exec` 时出现“命令未找到”的错误

`s6-overlay` 会将其二进制文件放置在 `/command/` 目录中，但该路径仅对监督树启动的进程有效——即服务、cont-init.d 和 main-wrapper.sh。执行 `docker exec <c> s6-svstat …` 时会因“命令未找到”而失败；此时应始终使用绝对路径 `/command/s6-svstat`。Hermes 可以正常运行，是因为 Dockerfile 将 `/opt/hermes/.venv/bin` 添加到了运行时的 `ENV PATH` 环境变量中。

### Profile 目录的所有权问题

cont-init 重置工具以 hermes 用户身份运行（见 `02-reconcile-profiles` 中的 `s6-setuidgid hermes`）。如果某个 Profile 目录最终由 root 所有（例如因默认以 root 身份执行了 `docker exec <c> hermes profile create …`），则重置工具将无法读取 SOUL.md 文件，并引发 `PermissionError` 错误。解决办法：`stage2-hook.sh` 会在**每次**系统启动时，以幂等方式将 `$HERMES_HOME/profiles` 目录的所有权转移给 hermes 用户。请勿删除该脚本块。

### 通过 `docker exec` 创建的文件归 root 所有

`docker exec` 的默认运行用户为 root。要么显式传递 `--user hermes` 参数，要么等待下一次启动时由 stage2 脚本处理所有权转移。切勿以 root 身份手动在 `$HERMES_HOME/profiles/<name>/` 目录下创建文件——虽然下一次重置操作会处理这些文件，但正在进行的操作仍可能因权限问题失败。

### 服务槽存在，但 s6-svstat 显示“s6-supervise 未运行”

服务目录位于 tmpfs 上，因此在容器重启时会被清空。这可能是由于 cont-init 重置工具尚未运行（在 `docker restart` 后稍等片刻即可），或是该工具执行失败了。可查看 `docker logs <c> | grep '02-reconcile'` 来确认情况。

### Gateway 启动后立即退出（svstat 中显示“down (exitcode 1)”）

很可能是该 Profile 未配置模型或认证信息。服务槽本身是正确的，问题出在 Gateway 未被正确配置。首先应运行 `hermes -p <profile> setup` 命令。s6 监控器会不断尝试重启它，这是预期行为——一旦配置问题得到解决，下一次尝试就会成功，Gateway 也会保持运行状态。

### 重置工具跳过了某个 Profile

该重置工具以 **是否存在 `SOUL.md` 文件** 作为判断“真实 Profile”的依据。执行 `hermes profile create` 命令时总会自动创建该文件。如果某个 Profile 目录中不存在 SOUL.md 文件（可能是误删的目录、恢复不完整或正处于备份过程中），重置工具会故意跳过它。如需重新处理该 Profile，可添加一个空的 `SOUL.md` 文件。

### “出错了，容器以 143 号代码退出！”

请检查是否有程序调用了 `s6-svscanctl -t` 或 `/run/s6/basedir/bin/halt` 命令——这两个命令都会触发 /init 进入第三阶段关闭流程，但会返回 143（SIGTERM 信号）而非预期的正常退出码。这是从架构版本 A 向版本 B 过渡时出现的现象。若希望容器以正常的退出码关闭，必须让 CMD 脚本（即 main-wrapper.sh）正常执行结束；切勿试图通过结束脚本来强制控制退出。

## 相关技能

- `hermes-agent-dev`：用于浏览 Hermès Agent 的整体代码库
- `hermes-tool-quirks`：针对 Hermes 工具的特殊解决方案（如 sed/grep 等命令的使用技巧）——在调试 s6 组件与 Hermès 内置工具的交互时可用该技能。
