---
sidebar_position: 8
title: "Security"
description: "Security model, dangerous command approval, user authorization, container isolation, and production deployment best practices"
---

# 安全性

Hermes Agent 采用纵深防御型安全模型设计。本页面涵盖了从命令审批、容器隔离到消息平台用户授权等各个安全层面。

## 概述

该安全模型包含七层防护机制：

1. **用户授权** — 确定谁有权与智能体交互（白名单机制、私信配对）
2. **危险命令审批** — 对具有破坏性的操作进行人工干预审核
3. **容器隔离** — 通过 Docker/Singularity/Modal 沙箱技术及强化配置实现隔离
4. **MCP 凭证过滤** — 为 MCP 子进程设置独立的环境变量隔离机制
5. **上下文文件扫描** — 检测项目文件中的提示注入风险
6. **会话间隔离** — 各会话之间无法访问彼此的数据或状态；定时任务存储路径经过特殊处理，可抵御路径遍历攻击
7. **输入净化** — 对终端工具后端的工作目录参数进行白名单验证，防止 shell 注入攻击

## 危险命令审批

在执行任何命令之前，Hermes 会先将其与预定义的危险模式列表进行比对。若检测到匹配项，用户必须手动进行批准。

### 审批模式

审批系统支持三种模式，可通过 `~/.hermes/config.yaml` 文件中的 `approvals.mode` 参数进行配置：

```yaml
approvals:
  mode: smart                     # smart | manual | off
  timeout: 60                     # seconds to wait for user response (default: 60)
  cron_mode: deny                 # deny | approve — what cron jobs do when they hit a dangerous command
  mcp_reload_confirm: true        # /reload-mcp asks before invalidating the MCP tool cache
  destructive_slash_confirm: true # /clear, /new, /reset, /undo prompt before discarding state
```

完整键值设置如下：

| 键名 | 默认值 | 控制功能 |
|---|---|---|
| `mode` | `smart` | 危险 shell 命令的审批策略——详见下表。 |
| `timeout` | `60` | Hermes 在超时前等待用户审批回复的时间（秒）。 |
| `cron_mode` | `deny` | 当 [定时任务](./features/cron.md) 触发危险命令提示时，无界面模式下的处理方式。`deny` 会阻止该命令执行（Agent 需寻找其他解决方案）；`approve` 则自动批准定时任务中的所有命令。 |
| `mcp_reload_confirm` | `true` | 当此值为 `true` 时，执行 `/reload-mcp` 命令时会先询问用户是否确认重新构建 MCP 工具集。重新构建会清除提供程序提示缓存（工具结构定义存储在系统提示中），因此后续消息会重新发送完整的输入令牌。选择“始终批准”的用户可将此键值改为 `false`。 |
| `destructive_slash_confirm` | `true` | 当此值为 `true` 时，用于清除对话状态的破坏性命令（如 `/clear`、/new`、/reset`、/undo`）在执行前会先提示用户确认。系统会通过 Telegram、Discord 和 Slack 的原生是/否按钮呈现三选一对话框（一次性批准 / 始终批准 / 取消），其他平台则显示文本选项。选择“始终批准”的用户可将此键值改为 `false`。TUI 模式则使用自身的模态覆盖界面（可通过设置 `HERMES_TUI_NO_CONFIRM=1` 关闭此确认功能）。 |

| 模式 | 行为表现 |
|------|----------|
| **smart**（默认） | 使用辅助大语言模型来评估风险。低风险命令（例如 `python -c "print('hello')"`）仅针对该命令自动获得批准，而真正危险的命令则会直接被拒绝。对于不确定的命令，则会提交给人工审核。 |
| **manual** | 对于危险命令，始终要求用户手动确认后再执行。 |
| **off** | 禁用所有审批检查——相当于以 `--yolo` 参数运行。所有命令都无需提示即可执行。 |

:::warning
将 `approvals.mode` 设置为 `off` 会禁用所有安全提示。仅可在可信环境（如 CI/CD、容器等）中使用。
:::

### YOLO 模式

YOLO 模式可绕过当前会话中**所有**危险命令的审批提示。可通过以下三种方式启用该模式：

1. **CLI 参数**：使用 `hermes --yolo` 或 `hermes chat --yolo` 启动会话。
2. **斜杠命令**：在会话中进行时输入 `/yolo` 即可切换开启/关闭状态。
3. **环境变量**：设置 `HERMES_YOLO_MODE=1`。

`/yolo` 命令为**切换型**指令——每次使用都会改变模式状态，即开启或关闭。

```
> /yolo
  ⚡ YOLO mode ON — all commands auto-approved. Use with caution.

> /yolo
  ⚠ YOLO mode OFF — dangerous commands will require approval.
```

YOLO 模式在 CLI 会话和网关会话中均可用。在内部，该模式会设置 `HERMES_YOLO_MODE` 环境变量，每次执行命令前都会检查此变量。

当 YOLO 模式处于激活状态时，Hermes 会显示两个永久性的视觉提示，以便用户不会忘记当前正在绕过所有审批提示：

- 若 YOLO 已处于激活状态，在会话开始时会显示一条红色横幅：`⚠ YOLO 模式 —— 所有审批提示均被绕过`。当 YOLO 关闭时，此提示会隐藏，从而保持默认横幅的整洁。
- 在状态栏中会出现 `⚠ YOLO` 字样，其宽度可自适应不同界面层级，并且会在您开启或关闭 YOLO 模式时实时更新（支持富文本显示，同时也会提供纯文本版本）。

:::danger
YOLO 模式会为当前会话**禁用所有**危险命令的安全检查——**硬性禁止列表除外**（详见下文）。仅应在您完全信任所执行的命令时使用该模式（例如，在一次性环境中运行的经过充分测试的自动化脚本）。
:::

对于那些具有破坏性的会话级命令（如 `/clear`、`/new` / `/reset`、`/undo`、`/quit --delete`——`/exit --delete` 是其别名），CLI 在执行这些命令前也会要求用户确认。详情请参阅 [Slash Commands — 破坏性命令的确认提示](../reference/slash-commands.md#confirmation-prompts-for-destructive-commands)。

### 硬性禁止列表（最低安全底线）

某些命令的危害极其严重——比如不可逆的文件系统清除、分叉炸弹攻击、直接对块设备进行写入操作——因此无论以下哪种情况存在，Hermes 都会拒绝执行这些命令：

- `--yolo` / `/yolo` 已被开启
- `approvals.mode: off` 已设置
- 在无界面模式的 Cron 作业中运行
- 用户明确选择了“始终允许”

该禁止列表是位于 `--yolo` 之下的最低安全底线。它在审批机制甚至看到相关命令之前就会触发拦截，且不存在任何可绕过的标志。目前涵盖的规则模式如下（并非全部；内容会与 `tools/approval.py::UNRECOVERABLE_BLOCKLIST` 保持同步）：

| 规则模式 | 被列为硬性禁止的原因 |
|---|---|
| `rm -rf /` 及其明显变体 | 会清除整个文件系统根目录 |
| `rm -rf --no-preserve-root /` | 明确指定要清除根目录的变体 |
| `:(){ :\|:& };:`（bash 分叉炸弹） | 会占用主机资源直至重启 |
| 对已挂载的根设备使用 `mkfs.*` 命令 | 会格式化正在运行的系统 |
| `dd if=/dev/zero of=/dev/sd*` | 会将物理磁盘全部清零 |
| 在根目录层级将不可信的 URL 通过管道传递给 `sh` 命令 | 属于远程代码执行攻击，风险过高，无法允许 |

如果尝试执行被禁止的命令，工具调用会向代理返回说明性错误信息，相关命令不会被执行。如果某个合法的工作流确实需要使用这些命令（例如，您是负责系统清除与重装流程的操作人员），则应在代理外部直接执行这些命令。

### 用户自定义拒绝规则 (`approvals.deny`)

硬性禁止列表是固定不变的，并已嵌入代码中。而 `approvals.deny` 则是供用户编辑的对应机制：它是一组通配符模式列表，可在**无需考虑 `--yolo`、 `/yolo` 或 `approvals.mode: off` 设置**的情况下，无条件拦截匹配的终端命令。您可以使用该功能实现“有例外情况的 YOLO 模式”：即“让代理执行所有操作，除了这些特定的命令之外”。

```yaml
approvals:
  deny:
    - "git push --force*"
    - "*curl*|*sh*"
    - "dd if=* of=/dev/*"
```

详细说明：

- 模式为 [fnmatch](https://docs.python.org/3/library/fnmatch.html) 类型的通配符（`*`、`?`、`[...]`），会**忽略大小写**地与整个命令文本进行匹配。例如，`git push --force*` 能匹配 `git push --force origin main`，但无法匹配 `git push origin main`。
- 匹配过程会使用危险模式检测器所用的相同标准化/去混淆后的命令版本，因此简单的引号技巧（如 `git pu""sh --force`）无法绕过规则。
- **YAML 引用规范**：始终需为模式添加引号。单独出现的开头 `*` 是 YAML 别名，会导致解析失败；`{`、`!` 和 `: ` 在 YAML 中有特定含义。对于类 shell 的内容，单引号是最安全的选择。
- 拒绝规则适用于可访问主机的后端（本地、SSH、主机挂载的 Docker）。而隔离容器后端则完全无需这些防护机制，因为其运行的任何程序都无法接触到主机。
- 被拒绝的命令会向代理返回 `BLOCKED` 错误，指示其不得重试或重新构造命令。此类命令将不会被执行。

与其余审批配置一样，更改会立即生效（配置缓存以修改时间作为键值），无需重启会话。

:::note 威胁模型
拒绝规则旨在防范那些行为诚实但判断有误的代理，其威胁模型与危险模式检测器相同。它们并非用于抵御恶意攻击进程的沙箱——对于此类场景，应使用隔离后端（如 Docker、Modal）或限制出站访问的环境。
:::

### 审批超时时间

当出现危险命令提示时，用户有可配置的时间窗口来作出响应。若在超时时间内未收到任何响应，默认情况下该命令将被**拒绝**（即直接失败）。

可在 `~/.hermes/config.yaml` 中配置超时时间：

```yaml
approvals:
  timeout: 60  # seconds (default: 60)
```

### 什么会触发审批

以下模式会触发审批提示（定义在 `tools/approval.py` 中）：

| 模式 | 描述 |
|---------|-------------|
| `rm -r` / `rm --recursive` | 递归删除 |
| `rm ... /` | 在根路径下删除文件 |
| `chmod 777/666` / `o+w` / `a+w` | 设置世界级/其他用户可写权限 |
| 带有危险权限的 `chmod --recursive` | 递归设置世界级/其他用户可写权限（使用长选项） |
| `chown -R root` / `chown --recursive root` | 递归将所有权更改为 root |
| `mkfs` | 格式化文件系统 |
| `dd if=` | 磁盘复制 |
| `> /dev/sd` | 向块设备写入数据 |
| `DROP TABLE/DATABASE` | SQL 删除表/数据库 |
| `DELETE FROM`（无 WHERE 子句） | 无条件执行的 SQL 删除操作 |
| `TRUNCATE TABLE` | SQL 清空表操作 |
| `> /etc/` | 覆盖系统配置文件 |
| `systemctl stop/restart/disable/mask` | 停止/重启/禁用系统服务 |
| `kill -9 -1` | 杀死所有进程 |
| `pkill -9` | 强制终止进程 |
| 分裂炸弹模式 | 分裂炸弹攻击 |
| `bash -c` / `sh -c` / `zsh -c` / `ksh -c` | 通过 `-c` 选项执行 shell 命令（包括 `-lc` 等组合选项） |
| `python -e` / `perl -e` / `ruby -e` / `node -c` | 通过 `-e`/`-c` 选项执行脚本 |
| `curl ... \| sh` / `wget ... \| sh` | 将远程内容通过管道传递给 shell |
| `bash <(curl ...)` / `sh <(wget ...)` | 通过进程替换执行远程脚本 |
| 将内容写入 `/etc/`、`~/.ssh/`、`~/.hermes/.env` 的 `tee` 命令 | 使用 tee 命令覆盖敏感文件 |
| 通过重定向将内容写入 `/etc/`、`~/.ssh/`、`~/.hermes/.env` 的 `>` / `>>` 命令 | 通过重定向覆盖敏感文件 |
| `xargs rm` | 结合 xargs 和 rm 使用的命令 |
| `find -exec rm` / `find -delete` | 使用 find 命令并配合破坏性操作 |
| 将文件复制/移动到 `/etc/` 的 `cp`/`mv`/`install` 命令 | 将文件复制或移动到系统配置目录 |
| 对 `/etc/` 文件使用 `sed -i` / `sed --in-place` 的命令 | 直接修改系统配置文件内容 |
| `pkill`/`killall hermes/gateway` 命令 | 防止程序自动终止 |
| 使用 `&`/`disown`/`nohup`/`setsid` 运行 `gateway run` 的命令 | 防止在服务管理器之外启动网关 |

:::info
**容器绕过机制**：在 `docker`、`singularity`、`modal` 或 `daytona` 容器环境中运行时，由于容器本身即构成了安全边界，因此会**跳过**危险命令检测。容器内的破坏性命令无法对主机造成影响。
:::

### 审批流程（CLI）

在交互式 CLI 中，危险命令会直接显示内联审批提示：

```
  ⚠️  DANGEROUS COMMAND: recursive delete
      rm -rf /tmp/old-project

      [o]nce  |  [s]ession  |  [a]lways  |  [d]eny

      Choice [o/s/a/D]:
```

四种选项如下：

- **once** — 仅允许本次执行
- **session** — 在当前会话的剩余时间内允许该操作模式
- **always** — 添加到永久允许列表中（保存至 `config.yaml` 文件）
- **deny**（默认值）——阻止该命令执行

### 审批流程（网关/消息传递方式）

在消息平台模式下，智能体会将危险命令的详细信息发送到聊天界面，并等待用户回复：

- 回复 **yes**、**y**、**approve**、**ok** 或 **go** 表示批准
- 回复 **no**、**n**、**deny** 或 **cancel** 表示拒绝

运行网关时，系统会自动设置 `HERMES_EXEC_ASK=1` 环境变量。

### 永久允许列表

被标记为“always”的命令会被保存到 `~/.hermes/config.yaml` 文件中：

```yaml
# Permanently allowed dangerous command patterns
command_allowlist:
  - rm
  - systemctl
```

这些模式会在启动时被加载，并在后续的所有会话中自动生效。

:::提示
使用 `hermes config edit` 可以查看或从永久允许列表中移除相关模式。
:::

## 用户授权（网关）

在运行消息网关时，Hermes 通过分层授权机制来控制谁能够与机器人交互。

### 授权检查顺序

 `_is_user_authorized()` 方法会按以下顺序进行检查：

1. **平台级的全允许标志**（例如：`DISCORD_ALLOW_ALL_USERS=true`）
2. **私信配对已批准列表**（通过配对码获批的用户）
3. **平台特定的允许列表**（例如：`TELEGRAM_ALLOWED_USERS=12345,67890`）
4. **全局允许列表**（`GATEWAY_ALLOWED_USERS=12345,67890`）
5. **全局全允许设置**（`GATEWAY_ALLOW_ALL_USERS=true`）
6. **默认值：拒绝**

### 平台允许列表

在 `~/.hermes/.env` 文件中以逗号分隔的形式设置允许的用户 ID：

```bash
# Platform-specific allowlists
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=111222333444555666
WHATSAPP_ALLOWED_USERS=15551234567
SLACK_ALLOWED_USERS=U01ABC123

# Cross-platform allowlist (checked for all platforms)
GATEWAY_ALLOWED_USERS=123456789

# Per-platform allow-all (use with caution)
DISCORD_ALLOW_ALL_USERS=true

# Global allow-all (use with extreme caution)
GATEWAY_ALLOW_ALL_USERS=true
```

:::warning
如果**未配置任何允许列表**且未设置 `GATEWAY_ALLOW_ALL_USERS`，则**所有用户都将被拒绝访问**。网关在启动时会记录一条警告信息：

```
No user allowlists configured. All unauthorized users will be denied.
Set GATEWAY_ALLOW_ALL_USERS=true in ~/.hermes/.env to allow open access,
or configure platform allowlists (e.g., TELEGRAM_ALLOWED_USERS=your_id).
```
:::

### 私信配对系统

为实现更灵活的授权机制，Hermes 提供了基于代码的配对系统。该系统无需预先获取用户 ID，未知用户会收到一个一次性配对码，由机器人所有者通过 CLI 进行审批。

**工作流程如下：**

1. 未知用户向机器人发送私信
2. 机器人回复一个包含 8 位字符的配对码
3. 机器人所有者通过 CLI 执行命令 `hermes pairing approve <platform> <code>` 
4. 该用户即被永久授权使用该平台

您可以在 `~/.hermes/config.yaml` 中配置如何处理未经授权的私信：

```yaml
unauthorized_dm_behavior: pair

whatsapp:
  unauthorized_dm_behavior: ignore
```

- 对于聊天式私信平台，默认行为为`pair`：对于未经授权的私信，系统会回复一个配对码。
- `ignore`模式则会静默忽略所有未经授权的私信。
- 除非设置了`platforms.email.unauthorized_dm_behavior: pair`，否则邮件的默认处理方式也是`ignore`，因为收件箱中可能包含许多无关的未读邮件。
- 各平台的特定设置可覆盖全局默认值，因此您可以在Telegram上保持配对功能，而在WhatsApp上选择静默处理。

**安全特性**（基于OWASP及NIST SP 800-63-4标准）：

| 特性 | 详情 |
|------|------|
| 密码格式 | 从32个字符的独特字母表中选取8位字符，且不含0、O、1、I |
| 随机性 | 采用加密级随机生成方式（`secrets.choice()`） |
| 密码有效期 | 1小时后过期 |
| 请求频率限制 | 每用户每10分钟仅允许1次请求 |
| 待处理密码数量限制 | 每个平台最多保留3个待处理密码 |
| 冒用防护 | 若连续5次审批失败，账户将被锁定1小时 |
| 文件安全 | 所有配对数据文件均采用`chmod 0600`权限设置 |
| 日志记录 | 密码信息绝不会被记录到标准输出中 |

**配对相关的CLI命令：**

```bash
# List pending and approved users
hermes pairing list

# Approve a pairing code
hermes pairing approve telegram ABC12DEF

# Revoke a user's access
hermes pairing revoke telegram 123456789

# Clear all pending codes
hermes pairing clear-pending
```

:::提示 Docker 用户：请以 `hermes` 用户身份运行配对命令  
官方 Docker 镜像会通过 `gosu` 工具，以无特殊权限的 `hermes` 用户（uid 10000）身份来运行网关，但 `docker exec` 命令默认以 root 用户身份执行。由 root 创建的审批文件其权限模式为 `0600 root:root`，导致网关无法读取这些文件——此类审批请求将会被默默忽略（[#10270][i10270]）。  
请始终使用 `-u hermes` 参数：

```bash
docker exec -u hermes hermes-agent hermes pairing approve telegram ABC12DEF
```

如果您已以 root 权限运行了该命令，但用户仍未获得授权，请重新启动容器——下次启动时，入口点将会修正文件所有权问题。

[i10270]: https://github.com/NousResearch/hermes-agent/issues/10270
:::

**存储：** 配对数据存储在 `~/.hermes/pairing/` 目录下，采用针对不同平台的 JSON 文件形式：
- `{platform}-pending.json` — 待处理的配对请求
- `{platform}-approved.json` — 已通过验证的用户
- `_rate_limits.json` — 流量限制与禁用状态记录

## 容器隔离

在使用 `docker` 终端后端时，Hermes 会对每个容器实施严格的安全加固措施。

### Docker 安全标志位

每个容器都会以这些标志位运行（定义于 `tools/environments/docker.py` 文件中）：

```python
_BASE_SECURITY_ARGS = [
    "--cap-drop", "ALL",                          # Drop ALL Linux capabilities
    "--cap-add", "DAC_OVERRIDE",                  # Root can write to bind-mounted dirs
    "--cap-add", "CHOWN",                         # Package managers need file ownership
    "--cap-add", "FOWNER",                        # Package managers need file ownership
    "--security-opt", "no-new-privileges",         # Block privilege escalation
    "--pids-limit", "256",                         # Limit process count
    "--tmpfs", "/tmp:rw,nosuid,size=512m",         # Size-limited /tmp
    "--tmpfs", "/var/tmp:rw,noexec,nosuid,size=256m",  # No-exec /var/tmp
]
```

`SETUID`/`SETGID` **并不**包含在基础列表中——只有当容器以 root 权限启动且需要通过 init/入口点来降低权限时（即遵循 s6 的权限降级机制），才会条件性地将其添加进去。而如果容器已通过 `--user` 参数以非 root 权限运行，则会跳过这些指令。此外，`/run` tmpfs 也被从基础列表中分离出来，并根据每个镜像进行单独挂载（默认设置为严格的 `noexec` 模式，仅对于从 `/run` 目录启动的 s6-overlay 镜像才允许 `exec` 模式）。

### 资源限制

容器的资源限制可在 `~/.hermes/config.yaml` 文件中进行配置：

```yaml
terminal:
  backend: docker
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_forward_env: []  # Explicit allowlist only; empty keeps secrets out of the container
  container_cpu: 1        # CPU cores
  container_memory: 5120  # MB (default 5GB)
  container_disk: 51200   # MB (default 50GB, requires overlay2 on XFS)
  container_persistent: true  # Persist filesystem across sessions
```

### 文件系统持久化

- **持久模式**（`container_persistent: true`）：将 `~/.hermes/sandboxes/docker/<task_id>/` 目录下的 `/workspace` 和 `/root` 进行绑定挂载。
- **临时模式**（`container_persistent: false`）：工作区使用 tmpfs 存储——清理时会丢失所有数据。

:::tip
对于生产环境中的网关部署，建议使用 `docker`、`modal` 或 `daytona` 后端，将 Agent 命令与主机系统隔离开来。这样无需再进行危险的命令审批操作。
:::

:::warning
如果在 `terminal.docker_forward_env` 中添加变量名，这些变量将会被直接注入到用于终端命令的容器中。这对于 `GITHUB_TOKEN` 等任务专用凭证非常有用，但同时也意味着容器内的代码可以读取并窃取这些凭证。
:::

## 终端后端安全性对比

| 后端 | 隔离程度 | 危险命令检测 | 最佳适用场景 |
|---------|-----------|-------------------|----------|
| **local** | 无——在主机上运行 | ✅ 是 | 开发环境及可信用户 |
| **ssh** | 远程机器 | ✅ 是 | 在独立服务器上运行 |
| **docker** | 容器级别 | ❌ 被跳过（容器本身即隔离边界） | 生产环境网关 |
| **singularity** | 容器级别 | ❌ 被跳过 | 高性能计算环境 |
| **modal** | 云沙箱 | ❌ 被跳过 | 需要可扩展云隔离的场景 |
| **daytona** | 云沙箱 | ❌ 被跳过 | 需要持久化云工作区的场景 |

## 环境变量传递 {#environment-variable-passthrough}

`execute_code` 和 `terminal` 功能都会从子进程中移除敏感的环境变量，以防止由大语言模型生成的代码窃取凭证。不过，那些声明了 `required_environment_variables` 的技能确实需要访问这些变量。

### 工作原理

有两种机制可用于让特定变量穿透沙箱过滤机制：

**1. 技能级自动传递**

当某个技能被加载（通过 `skill_view` 命令或 `/skill` 命令）并指定了 `required_environment_variables` 后，环境中实际已设置的这些变量将会自动被标记为可传递的变量。而那些尚未设置（仍处于“需要配置”状态）的变量则不会被标记。


```yaml
# In a skill's SKILL.md frontmatter
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
```

加载该技能后，`TENOR_API_KEY` 将自动传递给 `execute_code`、本地终端以及远程后端（Docker、Modal），无需手动配置。

:::info Docker与Modal
在 v0.5.1 版本之前，Docker 的 `forward_env` 功能与技能参数传递机制是相互独立的。如今两者已合并——通过技能声明的环境变量会自动被传输到 Docker 容器及 Modal 沙箱中，无需再手动添加到 `docker_forward_env` 中。
:::

**2. 基于配置的参数传递（手动方式）**

对于未被任何技能声明的环境变量，可将其添加到 `config.yaml` 文件中的 `terminal.env_passthrough` 字段里：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

### 凭证文件传递（OAuth 令牌等）{#credential-file-passthrough}

某些智能体需要在沙箱环境中使用**文件**（而不仅仅是环境变量）——例如，Google Workspace会将OAuth令牌以`google_token.json`的形式存储在当前活跃配置文件的`HERMES_HOME`目录下。智能体可通过前置内容来指定这些文件。

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials
```

在加载时，Hermes 会检查当前激活配置文件中的 `HERMES_HOME` 目录中是否存在这些文件，并将其注册以便挂载：

- **Docker**：使用只读绑定挂载（`-v host:container:ro`）
- **Modal**：在创建沙箱时即进行挂载，并在每条命令执行前同步数据（可处理会话期间的 OAuth 设置）
- **本地环境**：无需任何操作（文件已可直接访问）

您也可以在 `config.yaml` 文件中手动列出凭证文件：

```yaml
terminal:
  credential_files:
    - google_token.json
    - my_custom_oauth_token.json
```

路径是相对于 `~/.hermes/` 的。文件会被挂载到容器内的 `/root/.hermes/` 目录中。`tools/credential_files.py`（即 `terminal.credential_files`）会读取这份列表——它位于 `terminal:` 块下，但由凭证文件模块加载，而非核心终端后端，因此不会被包含在预置的 `DEFAULT_CONFIG` 配置快照中。

### 各沙箱的过滤规则

| 沙箱 | 默认过滤规则 | 透传覆盖规则 |
|-----|-------------|------------|
| **execute_code** | 阻止名称中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD`、`AUTH` 等字样的变量；仅允许带有安全前缀的变量通过 | ✅ 透传变量可绕过这两项检查 |
| **terminal**（本地模式） | 阻止所有明确的 Hermes 基础设施相关变量（如提供程序密钥、网关令牌、工具 API 密钥） | ✅ 透传变量可绕过该黑名单 |
| **terminal**（Docker 模式） | 默认不传递任何主机环境变量 | ✅ 透传变量以及通过 `-e` 参数传递的 `docker_forward_env` 变量会被包含 |
| **terminal**（Modal 模式） | 默认不传递任何主机环境变量或文件 | ✅ 凭证文件会被挂载；环境变量可通过同步方式透传 |
| **MCP** | 除了安全的系统变量以及明确配置的 `env` 变量外，其余所有变量均被阻止 | ❌ 透传功能对其无效（应使用 MCP 的 `env` 配置选项） |

### 安全注意事项

- 透传功能仅影响您或您的技能明确声明的变量——对于由大型语言模型生成的任意代码，其默认的安全策略保持不变。
- 凭证文件会被以**只读**方式挂载到 Docker 容器中。
- Skills Guard 会在技能安装前扫描其内容，检测是否存在可疑的环境变量访问模式。
- 未定义或未被设置的变量永远不会被注册（不存在的变量自然无法泄露）。
- Hermes 的基础设施密钥（如提供程序 API 密钥、网关令牌）绝不应被添加到 `env_passthrough` 中——它们有专门的处理机制。

## MCP 凭证管理

MCP（模型上下文协议）服务器子进程会接收到一个**已过滤过的环境变量集**，以此防止凭证意外泄露。

### 安全的环境变量

仅以下变量会被从主机传递到 MCP 的标准输入/输出子进程：

```
PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR
```

此外还包括所有 `XDG_*` 变量。其他所有的环境变量（如 API 密钥、令牌、机密信息等）都会被**移除**。

在 MCP 服务器的 `env` 配置中明确定义的变量则会原样传递：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."  # Only this is passed
```

### 凭证脱敏处理

MCP 工具返回给大语言模型的错误信息在传递前会经过净化处理。以下格式的凭证内容将被替换为 `[REDACTED]`：

- GitHub PATs（`ghp_...`）
- OpenAI 风格的密钥（`sk-...`）
- 承载令牌
- `token=`、`key=`、`API_KEY=`、`password=`、`secret=` 等参数

### 网站访问策略

您可以通过代理的网页及浏览器工具来限制其可访问的网站范围。此功能有助于防止代理访问内部服务、管理面板或其他敏感网址。

```yaml
# In ~/.hermes/config.yaml
security:
  website_blocklist:
    enabled: true
    domains:
      - "*.internal.company.com"
      - "admin.example.com"
    shared_files:
      - "/etc/hermes/blocked-sites.txt"
```

当请求被屏蔽的网址时，该工具会返回错误信息，说明该域名因策略限制而被屏蔽。此屏蔽列表适用于 `web_search`、`web_extract`、`browser_navigate` 以及所有支持处理网址的工具。

如需详细信息，请参阅配置指南中的[网站屏蔽列表](/user-guide/configuration#website-blocklist)。

### SSRF防护机制

所有支持处理网址的工具（网络搜索、网页提取、视觉分析、浏览器功能）在获取网址之前都会对其进行检查，以此防止服务器端请求伪造（SSRF）攻击。被屏蔽的地址包括：

- **私有网络**（RFC 1918标准）：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- **回环地址**：`127.0.0.0/8`、`::1`
- **链路本地地址**：`169.254.0.0/16`（包括地址为 `169.254.169.254` 的云元数据地址）
- **CGNAT/共享地址空间**（RFC 6598标准）：`100.64.0.0/10`（适用于Tailscale、WireGuard VPN）
- **云元数据主机名**：`metadata.google.internal`、`metadata.goog`
- **预留地址、多播地址及未指定地址**

对于面向互联网的场景，SSRF防护机制始终处于激活状态，且DNS请求失败会被视为被屏蔽（采用“失败即关闭”策略）。为防止通过重定向绕过防护，每次跳转时都会重新验证重定向路径。

#### 有意允许访问私有网址

在某些情况下，确实需要访问私有或内部网址——例如将 `home.arpa` 解析为RFC 1918地址段的家庭网络、仅限局域网使用的Ollama/llama.cpp服务端点、内部维基站点、云元数据调试等。针对这类场景，提供了全局禁用选项：

```yaml
security:
  allow_private_urls: true   # default: false
```

开启该功能后，Web工具、浏览器、视觉URL获取以及网关媒体下载将不再拒绝RFC 1918、回环地址、链路本地地址、CGNAT及云元数据类型的目标地址。**这是一种有意设置的信任边界**——仅应在那些能够承受代理程序向本地网络发送任意注入式URL所带来的风险的设备上启用此功能。面向公网的网关则应保持该功能关闭状态。

无论是否启用此设置，主机子串防护机制（即便底层IP为公网地址，也能有效阻止类似Unicode域名的欺骗手段）仍将持续运行。

### Tirith预执行安全扫描

Hermes集成了[tirith](https://github.com/sheeki03/tirith)工具，可在命令执行前进行内容级扫描。Tirith能够检测出仅靠模式匹配无法发现的威胁，包括：

- 同形异义字URL欺骗（国际化域名攻击）
- 从管道传递至解释器的指令模式（如`curl | bash`、`wget | sh`）
- 终端注入攻击

首次使用时，Tirith会通过SHA-256校验和验证从GitHub发布的版本自动进行安装；如果支持联合签名功能，还会对来源进行联合签名验证。

```yaml
# In ~/.hermes/config.yaml
security:
  tirith_enabled: true       # Enable/disable tirith scanning (default: true)
  tirith_path: "tirith"      # Path to tirith binary (default: PATH lookup)
  tirith_timeout: 5          # Subprocess timeout in seconds
  tirith_fail_open: true     # Allow execution when tirith is unavailable (default: true)
```

当 `tirith_fail_open` 设为 `true`（默认值）时，即便未安装 tirith 或操作超时，命令仍会继续执行。在高度安全的环境中，可将其设置为 `false`，以便在 tirith 不可用时阻止命令执行。

Tirith 提供了针对 Linux（x86_64 / aarch64）和 macOS（x86_64 / arm64）预编译的二进制文件。对于没有预编译二进制文件的平台（如 Windows），tirith 会静默跳过——模式匹配检测仍会运行，且 CLI 不会显示“不可用”提示。若要在 Windows 上使用 tirith，可在 WSL 环境下运行 Hermes。

Tirith 的检测结果会与审批流程集成：安全命令可直接通过，而可疑命令和被阻止的命令则会触发用户审批，并同步显示完整的检测信息，包括严重程度、标题、描述以及更安全的替代方案。用户可以选择批准或拒绝——为保障无人值守场景的安全，默认选项为拒绝。

### 上下文文件注入防护

在将上下文文件（AGENTS.md、.cursorrules、SOUL.md）纳入系统提示之前，系统会对其进行提示注入检测。检测内容包括：

- 要求忽略/ disregard 之前指令的指示
- 包含可疑关键词的隐藏 HTML 注释
- 尝试读取机密信息（如 `.env`、`credentials`、`.netrc` 文件）
- 通过 `curl` 实现的凭证窃取行为
- 隐形的 Unicode 字符（零宽空格、双向替换字符）

被阻止的文件会显示警告提示：

```
[BLOCKED: AGENTS.md contained potential prompt injection (prompt_injection). Content not loaded.]
```

## 生产环境部署的最佳实践

### 网关部署检查清单

1. **设置明确的允许列表** —— 在生产环境中绝不要使用 `GATEWAY_ALLOW_ALL_USERS=true`
2. **采用容器后端** —— 在 config.yaml 中设置 `terminal.backend: docker`
3. **限制资源使用上限** —— 设置合理的 CPU、内存和磁盘使用限制
4. **安全存储机密信息** —— 将 API 密钥保存在 `~/.hermes/.env` 文件中，并设置适当的文件权限
5. **启用私信配对功能** —— 尽可能使用配对码而非硬编码用户 ID
6. **定期审查命令允许列表** —— 常态化检查 config.yaml 中的 `command_allowlist`
7. **设置 `terminal.cwd` 参数** —— 防止智能体在敏感目录中运行
8. **以非根用户身份运行** —— 绝不可以 root 权限运行网关
9. **监控日志信息** —— 定期查看 `~/.hermes/logs/` 文件，排查未经授权的访问尝试
10. **保持版本更新** —— 定期执行 `hermes update` 以获取安全补丁

### API 密钥的安全保护措施

```bash
# Set proper permissions on the .env file
chmod 600 ~/.hermes/.env

# Keep separate keys for different services
# Never commit .env files to version control
```

### 网络隔离

为确保最高安全级别，建议将网关部署在独立的机器或虚拟机上。在 `config.yaml` 文件中设置 `terminal.backend: ssh`，随后通过 `~/.hermes/.env` 文件中的环境变量来指定主机详细信息：

```yaml
# ~/.hermes/config.yaml
terminal:
  backend: ssh
```

```bash
# ~/.hermes/.env
TERMINAL_SSH_HOST=agent-worker.local
TERMINAL_SSH_USER=hermes
TERMINAL_SSH_KEY=~/.ssh/hermes_agent_key
```

SSH 连接详情存储在 `.env` 文件中（而非 `config.yaml`），因此不会随配置导出一起被提交或共享。这样一来，网关的消息传输连接便能与代理的命令执行流程相互分离。

## 供应链安全建议检查

Hermes 内置了安全建议扫描器，能够识别当前虚拟环境中与已知受损版本列表匹配的 Python 包（例如 2026 年 5 月出现的 `mistralai 2.4.6` 毒害事件等供应链攻击）。该功能的实现代码位于 `hermes_cli/security_advisories.py` 文件中。

其运行机制如下：

- **CLI 启动提示。** 若检测到匹配的安全建议，系统会打印一行警告信息，并提供 `hermes doctor` 命令以获取完整的修复方案。
- **`hermes doctor` 命令。** 会列出所有当前存在的安全建议，同时显示具体版本信息以及 2-4 步的修复指导。
- **网关启动时。** 相关日志会被记录到 `gateway.log` 文件中；在首次交互式消息中还会显示简短的操作提示。

每条安全建议都有一个唯一的稳定标识符。一旦您已阅读并采取了相应措施，即可永久将其标记为已处理。

```bash
hermes doctor --ack <advisory-id>
```

确认信息会被持久存储在 `config.security.acked_advisories` 中，因此即使重启也不会丢失。旧的安全警告并不会被刻意从目录中移除——将其保留原位可以确保新安装的用户能够收到关于可能仍缓存在私有镜像站中的旧版有害版本的警告。

该检查仅依赖标准库，且针对每个安全警告会执行一次 `importlib.metadata.version()` 查询，因此可以在每次启动时安全地运行。

### 可选依赖的延迟安装

许多功能（如 Mistral TTS、ElevenLabs、Honcho 内存功能、Bedrock、Slack、Matrix 等）都依赖于并非所有用户都需要的 Python 包。Hermes 会在首次使用时**延迟**安装这些包，而非在 `hermes-agent[all]` 配置下立即安装。相关实现位于 `tools/lazy_deps.py` 文件中。

这种机制解决了以下问题：

- **稳定性问题**：如果某个额外功能的间接依赖在 PyPI 上无法获取（被标记为恶意软件、已被下架或上传失败），整个 `[all]` 组的依赖解析就会失败，新安装的用户将被迫降级到精简版本——这样一来，10 多个无关的额外功能会同时失效。而延迟安装机制将各个后端功能隔离开来，避免某个有问题的依赖破坏其他功能。
- **臃肿问题**：那些仅使用单一服务提供商的用户，再也不用下载数百个他们根本不会使用的包。

其工作原理如下：

1. 某个后端模块在其首次被导入的路径开头调用 `ensure("feature.name")`。
2. 如果所需依赖缺失，`ensure` 函数会检查 `config.yaml` 中的 `security.allow_lazy_installs` 设置（默认值为 `true`），然后为允许安装的依赖项在当前虚拟环境中执行 `pip install` 操作。
3. 如果安装失败或用户已禁用延迟安装功能，该函数会抛出 `FeatureUnavailable` 异常，同时附带实际的 pip 错误信息以及指向 `hermes tools` 的路径。

`tools/lazy_deps.py` 所提供的安全保障包括：

| 安全保障 | 含义 |
|---|---|
| 仅限虚拟环境范围 | 包仅安装在当前活跃虚拟环境中的 `sys.executable` 环境中，绝不会影响系统级 Python |
| 仅支持通过名称从 PyPI 安装 | 依赖规格仅接受 `"package>=1.0,<2"` 这样的语法格式。不允许使用 `--index-url`、`git+https://` 或文件路径——这样恶意修改的 `config.yaml` 就无法引导安装到错误位置 |
| 允许列表机制 | 只有出现在内置 `LAZY_DEPS` 映表中的依赖项才能通过此路径安装。功能名称拼写错误不会导致意外安装 |
| 可选择禁用 | 设置 `security.allow_lazy_installs: false` 即可完全禁用运行时安装功能。适用于受限网络或要求严格安全策略的环境 |
| 无隐性重试机制 | 安装失败会以 `FeatureUnavailable` 的形式直接显示——不会缓存错误状态，也不会出现频繁重试的情况 |

如需禁用运行时安装功能：

```yaml
# ~/.hermes/config.yaml
security:
  allow_lazy_installs: false
```

当该功能被禁用时，那些需要可选依赖的后端会提示用户手动执行安装操作（`pip install …`），或通过 `hermes tools` 选择其他后端。
