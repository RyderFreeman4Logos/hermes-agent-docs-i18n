---
sidebar_position: 8
title: "Security"
description: "Security model, dangerous command approval, user authorization, container isolation, and production deployment best practices"
---

# 安全性

Hermes Agent 采用了多层防御的安全架构。本页面涵盖了从命令审批、容器隔离到消息平台用户授权等所有安全层面。

## 概述

该安全模型包含八层防护机制：

1. **用户授权** — 确定谁有权与智能体交互（白名单、私信配对）
2. **危险命令审批** — 对具有破坏性的操作进行人工干预审核
3. **文件写入保护** — 为 `write_file`/`patch` 操作设置黑名单及可选的写入沙箱
4. **容器隔离** — 使用 Docker/Singularity/Modal 并配置强化安全参数的沙箱环境
5. **MCP 凭证过滤** — 为 MCP 子进程实现环境变量隔离
6. **上下文文件扫描** — 检测项目文件中的命令注入风险
7. **会话间隔离** — 各会话无法访问彼此的数据或状态；定时任务存储路径经过特殊处理以防止路径遍历攻击
8. **输入净化** — 对终端工具后端的当前工作目录参数进行白名单验证，防止 Shell 注入攻击

## 危险命令审批

在执行任何命令之前，Hermes 会先将其与预设的危险模式列表进行比对。若检测到匹配项，用户必须手动批准该命令才能继续执行。

### 审批模式

审批系统支持三种模式，可通过 `~/.hermes/config.yaml` 文件中的 `approvals.mode` 参数进行配置：

```yaml
approvals:
  mode: smart                     # smart | manual | off
  timeout: 300                    # seconds to wait for user response (default: 300)
  cron_mode: deny                 # deny | approve — what cron jobs do when they hit a dangerous command
  single_query_mode: deny         # deny | approve — what single-query (-q) sessions do on a dangerous command
  unattended_mode: deny           # deny | approve — what webhook/API sessions do on a dangerous command
  mcp_reload_confirm: true        # /reload-mcp asks before invalidating the MCP tool cache
  destructive_slash_confirm: true # /clear, /new, /reset, /undo prompt before discarding state
```

完整的密钥集合：

| Key | Default | What it controls |
|---|---|---|
| `mode` | `smart` | Approval policy for dangerous shell commands — see the table below. |
| `timeout` | `300` | Seconds Hermes waits for an approval reply before timing out. |
| `cron_mode` | `deny` | How [cron jobs](./features/cron.md) behave headlessly when they trigger a dangerous-command prompt. `deny` blocks the command (the agent must find another path); `approve` auto-approves everything in cron context. |
| `single_query_mode` | `deny` | How one-shot [`hermes chat -q`](./cli.md) sessions behave when they trigger a dangerous-command prompt. A `-q` session runs a single turn and exits with no user waiting to answer prompts; `deny` blocks the command (the agent must find another path), `approve` auto-approves everything in single-query context. Mirrors `cron_mode`. |
| `unattended_mode` | `deny` | How sessions on unattended programmatic platforms (webhook, msgraph_webhook, api_server) behave when they trigger a dangerous-command prompt. These surfaces have no human who can answer `/approve`, so instead of blocking for the full approval timeout, `deny` blocks the command instantly (the agent must find another path) and `approve` auto-approves everything in unattended context. Mirrors `cron_mode`. |
| `mcp_reload_confirm` | `true` | When true, `/reload-mcp` asks before rebuilding the MCP tool set. Rebuilding invalidates the provider prompt cache (tool schemas live in the system prompt), so the next message re-sends full input tokens. Users who click **Always Approve** flip this key to `false`. |
| `destructive_slash_confirm` | `true` | When true, destructive session slash commands (`/clear`, `/new`, `/reset`, `/undo`) prompt before discarding conversation state. Three-option dialog (Approve Once / Always Approve / Cancel) routed through native yes/no buttons on Telegram, Discord, and Slack; text fallback elsewhere. Users who click **Always Approve** flip this key to `false`. The TUI also honors this setting for its `/clear`, `/new`, and `/reset` modal; `HERMES_TUI_NO_CONFIRM=1` force-skips that modal regardless of the configured value. |

| 模式 | 行为 |
|------|------|
| **smart**（默认） | 使用辅助大语言模型来评估风险。低风险命令（例如 `python -c "print('hello')"`）将仅针对该命令自动获得批准；真正危险的命令则会自动被拒绝。对于不确定的命令，则会升级为人工审核流程。 |
| **manual** | 对于危险命令，始终要求用户进行手动确认。 |
| **off** | 禁用所有审批检查——相当于以 `--yolo` 参数运行。所有命令都可在无需提示的情况下执行。 |

:::warning
将 `approvals.mode` 设置为 `off` 会关闭所有安全提示。仅可在可信环境（如 CI/CD、容器等）中使用。
:::

### YOLO 模式

YOLO 模式可绕过当前会话中**所有**危险命令的审批提示。可通过以下三种方式启用该模式：

1. **CLI 参数**：使用 `hermes --yolo` 或 `hermes chat --yolo` 启动会话。
2. **斜杠命令**：在会话期间输入 `/yolo` 即可切换该模式的开启与关闭状态。
3. **环境变量**：设置 `HERMES_YOLO_MODE=1`。

`/yolo` 命令为**切换型**命令——每次使用都会改变该模式的开关状态：

```
> /yolo
  ⚡ YOLO mode ON — all commands auto-approved. Use with caution.

> /yolo
  ⚠ YOLO mode OFF — dangerous commands will require approval.
```

YOLO 模式在 CLI 会话和网关会话中均可用。在内部，该模式会设置 `HERMES_YOLO_MODE` 环境变量，每次执行命令前都会检查此变量。

当 YOLO 模式处于激活状态时，Hermes 会显示两个永久性的视觉提示，以便用户不会忘记当前已跳过了所有审批提示：

- 若 YOLO 模式已开启，在会话开始时会显示一条红色横幅：`⚠ YOLO 模式 —— 所有审批提示均已跳过`。当 YOLO 模式关闭时，此横幅会隐藏，从而保持默认界面整洁。
- 在状态栏中会显示 `⚠ YOLO` 字样，其宽度可适应不同界面层级，并且会在您开启或关闭 YOLO 模式时实时更新（支持富文本渲染及纯文本备选显示）。

:::danger
YOLO 模式会为当前会话**禁用所有**危险命令的安全检查——**硬性屏蔽列表中的命令除外**（详见下文）。仅应在您完全信任所执行的命令时使用该模式（例如，在一次性环境中运行的经过充分测试的自动化脚本）。
:::

对于具有破坏性的会话级命令（如 `/clear`、`/new` / `/reset`、`/undo`、`/quit --delete`，其中 `/exit --delete` 是其别名），CLI 在执行这些命令前也会要求用户确认。详情请参阅[斜杠命令 —— 破坏性命令的确认提示](../reference/slash-commands.md#confirmation-prompts-for-destructive-commands)。

### 受监督网关的生命周期限制

该终端工具具备独立的、不可绕过的保护机制，用于防止在其自身的监管进程内部停止或重启网关。若尝试自动重启，可能会导致工具在运行完成前即终止，进而引发监管进程与自动恢复功能的循环。用户授权、YOLO模式以及`force=True`参数均无法绕过这一保护机制。

在 macOS 系统中，无论任务标签为何，执行 `launchctl submit` 和 `launchctl bootstrap` 命令都会受到限制。这是一种较为严格的注册限制措施，旨在拦截那些标签看似中立但实际上用于间接重启的工具，而非对目标 plist 文件内容进行实际检查。此外，该系统还会拒绝那些设置了 `RunAtLoad=false` 且不包含 `KeepAlive` 键的独立定时任务；但此类拒绝并不代表该任务一定使用了 KeepAlive 功能或能够控制 Hermes 系统。

如需对 LaunchAgent 进行授权后的维护操作，应使用运行中的网关之外的独立 shell。目前有一些独立的 `load`/`unload` 命令能够通过基于标签的检查，但这既不属于经过目标验证的豁免情况，也不是规避 `bootstrap` 拒绝机制的可行方法。仅具有只读权限的 `launchctl print` 命令并不属于生命周期操作。在完成外部维护后，需区分磁盘上的 plist 文件与已加载的任务：在报告任务已激活之前，应先验证 plist 文件的内容，并重新读取已加载的任务调度信息。

当工具被拒绝时，意味着相关命令并未通过该工具进行执行。而助手拒绝发起调用则属于模型层面的独立决策；更换模型并不会改变终端工具的保护策略。

### 硬性拦截列表（始终生效）

某些命令的危害极其严重——诸如不可逆的文件系统清除、分叉炸弹攻击、直接对块设备进行写入等——以至于无论是否满足以下条件，Hermes 都会拒绝执行这些命令：

- 是否启用了 `--yolo` / `/yolo` 参数  
- `approvals.mode` 是否设置为 `off`  
- Cron 作业是否在无界面模式下的 `approve` 模式下运行  
- 用户是否明确选择了“始终允许”  

该阻止列表位于 `--yolo` 参数之下，甚至在审批层看到命令之前就会触发拦截，且不存在任何可绕过的标志。目前覆盖的规则模式如下（并非全部；内容会与 `tools/approval.py::UNRECOVERABLE_BLOCKLIST` 保持同步）：

| 规则模式 | 需要严格禁止的原因 |
|---|---|
| `rm -rf /` 及其明显变体 | 会清除整个文件系统根目录 |
| `rm -rf --no-preserve-root /` | 明确指定要清除根目录的命令 |
| `:(){ :\|:& };:`（bash 分叉炸弹） | 会导致主机陷入死循环直至重启 |
| 对已挂载的根设备使用 `mkfs.*` 命令 | 会格式化正在运行的系统 |
| `dd if=/dev/zero of=/dev/sd*` | 会将物理磁盘全部清零 |
| 在根文件系统顶层将不可信 URL 传递给 `sh` 命令 | 这种远程代码执行攻击方式风险过高，无法批准 |

一旦命令被列入阻止列表，工具调用会向代理返回说明性错误信息，且该命令不会被执行。如果某些合法的工作流确实需要使用这些命令（例如，作为负责系统清除与重装流程的操作员），则应在代理外部直接执行这些命令。

### 用户自定义禁止规则（`approvals.deny`）

硬性屏蔽列表是固定不变的，并已直接嵌入代码中。而 `approvals.deny` 则是供用户自行编辑的对应配置：它包含一系列通配符模式，能够在查询 `--yolo`、`/yolo` 以及 `approvals.mode: off` 的设置之前，无条件地屏蔽匹配到的终端命令。你可以利用这一功能来实现“除特定操作外允许代理执行所有操作”的使用场景。

```yaml
approvals:
  deny:
    - "git push --force*"
    - "*curl*|*sh*"
    - "dd if=* of=/dev/*"
```

详细说明：

- 模式为 [fnmatch](https://docs.python.org/3/library/fnmatch.html) 类型的通配符（如 `*`、`?`、`[...]`），会以**不区分大小写**的方式匹配整个命令文本以及各个候选的可执行命令。例如，`git push --force*` 能匹配 `git push --force origin main`，但无法匹配 `git push origin main`。
- 匹配过程会使用危险模式检测器所采用的相同标准化/去混淆后的命令版本，因此简单的引号技巧（如 `git pu""sh --force`）也无法逃过规则检测。
- 候选的可执行命令不仅保留其完整路径，还会根据其基名进行匹配：`sudo *` 能同时匹配 `/usr/bin/sudo -n id` 和 `./sudo -n id`。而像 `/usr/bin/sudo *` 这样针对特定路径的规则，则不会自动适用于所有名为 `sudo` 的二进制文件。
- 基于引号识别的解析功能能够识别赋值操作后的命令、重定向指令、`;`、`&&`、`||`等运算符、管道结构、分组操作、命令替换以及常规的`if`/`then`/`else`/`do`逻辑结构。支持的启动命令包括`sudo`、`env`、`command`、`exec`、`nohup`、`setsid`、`time`、`nice`、`timeout`、`stdbuf`、`ionice`、`chrt`、`taskset`和`chroot`。已知的选项参数会被直接跳过；而`command -v`/`-V`这类用于查询信息的操作不会被视为实际命令执行。对于通过`shell -c`传递的命令内容，系统会进行递归解析。在`env -S`或`--split-string`指令中，纯文本形式的可执行文件名与参数字符串会遵循GNU引号及转义规则（包括使用`\_`作为单词分隔符以及`\c`表示字符串结束），其余命令参数则会直接追加在后面；这些参数中的shell语法标记仅在被真正的`shell -c`指令处理时才会被解析为实际命令，否则仍保留为原始数据。`env -a`或`--argv0`指令返回的值属于参数范畴，而非可执行文件名。shell语法或GNU字符串分割规则中的注释内容不会被视为潜在的可执行命令。

- 在其他潜在的可执行命令候选项中，单词之间的空白会被合并，但带引号的参数内容及其路径信息则会被完整保留。因此，像`git status`这样的精确匹配规则同样适用于`env git\tstatus; echo done`（其中`\t`代表制表符）这类表达式。而诸如`echo 'sudo -n id'`这类被引号包裹的指令内容则不会被提升为独立命令。现有的全匹配模式，如`*sudo*`，仍会按设计匹配到任何位置出现的对应指令。

- **YAML引号规则：**所有模式都必须使用引号括起。单独出现的开头星号`*`在YAML中属于别名，会导致解析失败；`{`、`!`和`:`具有各自的YAML专用含义。对于类似shell的语法内容，使用单引号是最为安全的做法。
- 在任何针对特定后端的审批快捷方式生效之前，用户自定义的拒绝规则会先应用于所有终端后端，包括隔离容器。  
- 被拒绝的命令会向智能体返回“BLOCKED”错误信息，提示其无需重试或重新表述命令，此时该命令将不会被执行。  

与其余审批配置一样，更改会立即生效（配置缓存以修改时间作为键值），无需重启会话。  

:::note 威胁模型  
拒绝规则仅是一种shell命令策略，并非完整的shell解释器或操作系统能力沙箱。标准化处理无法解析任意变量（包括GNU `env -S`中的`${NAME}`变量展开）、别名、函数、重命名的二进制文件、脚本、解释器程序，以及各种shell/启动器语法（例如大小写模式语法、分组启动器选项或嵌入在`env -S`字符串中的选项）。切勿将基于文件名的拒绝规则视为能够确保某项能力无法通过其他途径被访问的保障。如需实现隔离，应使用操作系统权限以及具有适当限制的挂载点、凭据和网络访问权限的隔离后端。此匹配行为不会改变已配置的审批模式或默认的“空拒绝列表”设置。  
:::  

### 审批超时时间  

当出现危险命令提示时，用户有可配置的时间窗口来作出响应。若在超时时间内未收到任何响应，默认情况下该命令将被**拒绝**（即直接终止）。  

可在`~/.hermes/config.yaml`中配置超时时间：

```yaml
approvals:
  timeout: 300  # seconds (default: 300)
```

### 什么情况会触发审批流程

以下模式会触发审批提示（定义于 `tools/approval.py` 中）：

| Pattern | Description |
|---------|-------------|
| `rm -r` / `rm --recursive` | Recursive delete |
| `rm ... /` | Delete in root path |
| `chmod 777/666` / `o+w` / `a+w` | World/other-writable permissions |
| `chmod --recursive` with unsafe perms | Recursive world/other-writable (long flag) |
| `chown -R root` / `chown --recursive root` | Recursive chown to root |
| `mkfs` | Format filesystem |
| `dd if=` | Disk copy |
| `> /dev/sd` | Write to block device |
| `DROP TABLE/DATABASE` | SQL DROP |
| `DELETE FROM` (without WHERE) | SQL DELETE without WHERE |
| `TRUNCATE TABLE` | SQL TRUNCATE |
| `> /etc/` | Overwrite system config |
| `systemctl stop/restart/disable/mask` | Stop/restart/disable system services |
| `kill -9 -1` | Kill all processes |
| `pkill -9` | Force kill processes |
| Fork bomb patterns | Fork bombs |
| `bash -c` / `sh -c` / `zsh -c` / `ksh -c` | Shell command execution via `-c` flag (including combined flags like `-lc`) |
| `python -e` / `perl -e` / `ruby -e` / `node -c` | Script execution via `-e`/`-c` flag |
| `curl ... \| sh` / `wget ... \| sh` | Pipe remote content to shell |
| `bash <(curl ...)` / `sh <(wget ...)` | Execute remote script via process substitution |
| `tee` to `/etc/`, `~/.ssh/`, `~/.hermes/.env` | Overwrite sensitive file via tee |
| `>` / `>>` to `/etc/`, `~/.ssh/`, `~/.hermes/.env` | Overwrite sensitive file via redirection |
| `xargs rm` | xargs with rm |
| `find -exec rm` / `find -delete` | Find with destructive actions |
| `cp`/`mv`/`install` to `/etc/` | Copy/move file into system config |
| `sed -i` / `sed --in-place` on `/etc/` | In-place edit of system config |
| `pkill`/`killall` hermes/gateway | Self-termination prevention |
| `gateway run` with `&`/`disown`/`nohup`/`setsid` | Prevents starting gateway outside service manager |
| `docker stop/kill/restart`, `docker compose down/stop/kill/restart` | Container lifecycle (also catches global flags and `docker-compose`) |
| `docker -H`/`--host`/`--context`, `DOCKER_HOST=`/`DOCKER_CONTEXT=` | Docker daemon redirect — the command targets a different (often remote) daemon |
| `docker context use` | Switches the default daemon for all future docker commands |
| `podman --remote`/`-r`/`--url`/`--connection`/`--identity`, `CONTAINER_HOST=` | Podman remote daemon redirect |

:::info
**容器绕过机制**：在基于 `docker`、`singularity`、`modal`、`daytona` 或 `vercel_sandbox` 的后端环境中运行时，由于容器本身即构成了安全边界，因此会**跳过**对危险命令的检测。容器内的破坏性命令无法对主机造成损害。
:::

### 审批流程（CLI）

在交互式 CLI 中，危险命令会显示内嵌的审批提示：

```
  ⚠️  DANGEROUS COMMAND: recursive delete
      rm -rf /tmp/old-project

      [o]nce  |  [s]ession  |  [a]lways  |  [d]eny

      Choice [o/s/a/D]:
```

四种选项如下：

- **once** — 仅允许本次执行
- **session** — 在当前会话剩余时间内允许该操作模式
- **always** — 添加到永久允许列表中（保存至 `config.yaml` 文件）
- **deny**（默认值）— 拒绝执行该命令

### 审批流程（网关/消息传递方式）

在基于消息传递的平台中，智能体会将危险命令的详细信息发送到聊天界面，并等待用户回复：

- 回复 **yes**、**y**、**approve**、**ok** 或 **go** 表示批准
- 回复 **no**、**n**、**deny** 或 **cancel** 表示拒绝

在运行网关时，系统会自动设置 `HERMES_EXEC_ASK=1` 环境变量。

### 永久允许列表

被标记为“always”的命令将会保存到 `~/.hermes/config.yaml` 文件中：

```yaml
# Permanently allowed dangerous command patterns
command_allowlist:
  - rm
  - systemctl
```

这些模式会在启动时被加载，并在后续的所有会话中自动获得批准。

该设置必须为字符串列表形式。对于那些将列表存储为带引号的 YAML/JSON 字符串的旧版本安装，系统会在加载时恢复该列表，并输出警告提示用户使用 `hermes config edit` 命令重新保存。其他格式错误的值也会被忽略并伴随警告信息，且永远不会被视为针对单个字符的批准规则。此加载过程不会修改您的配置文件。

:::提示
请使用 `hermes config edit` 命令来查看或删除您永久允许列表中的模式。
:::

### 分析批准历史记录（`hermes approvals suggest`）

无需在每次会话中都重复回答相同的问题，您可以将过去的批准决策提取出来，作为生成允许列表建议的依据：

```bash
hermes approvals suggest            # dry run — prints a numbered proposal
hermes approvals suggest --apply 1,3  # merge picks into command_allowlist
hermes approvals suggest --json     # machine-readable output
```

该命令会扫描会话数据库（`~/.hermes/state.db`），查找那些实际已被执行的、被标记为危险级别的命令——也就是您已授权的命令，然后将它们汇总为特定模式（如 `git push *`，或是复合命令对应的危险级别标识），最后根据被授权的频率对这些命令进行排序。

```
Proposed command_allowlist additions (from approval history, last 90 days):

  1. git push *    — approved 14x
  2. docker restart/stop/kill (container lifecycle)    — approved 9x (class key)
```

安全规则：

- **任何操作都不会自动执行**——默认模式下仅以只读方式运行；
  只有明确使用 `--apply N[,M...]` 参数时，才会向 `config.yaml` 写入内容。
- **绝不会提议使用具有破坏性的操作**，无论此类操作曾被批准过多少次：递归删除、`sudo` 命令、磁盘/设备写入、凭证及系统配置修改、管道转 Shell 命令、SQL 的 DROP/TRUNCATE 操作、进程终止，以及所有高风险操作类别均会被直接排除。即便某条 `rm -rf build/` 命令被批准了 100 次，也绝不会生成对应的 `rm` 条目。
- 若某个操作已包含在您现有的 `command_allowlist` 允许列表中，则会直接跳过。

常用参数：`--days N`（历史记录查询周期，默认为 90 天）、`--min-count N`（达到该数量才视为有效批准，默认为 2 次）、`--limit N` 以及 `--db PATH`。

## 文件写入安全 {#file-write-safety}

在 `write_file` 或 `patch` 函数尝试写入磁盘之前，Hermes 会先将目标路径与禁止列表及可选的沙箱环境进行比对。若检测到禁止操作，会立即向代理返回错误信息——**不会出现批准提示**，也无法通过聊天界面进行覆盖。模型仍可能声称编辑操作已成功；当启用 `display.file_mutation_verifier`（默认开启）时，应优先相信[文件变更验证器说明](./configuration.md#file-mutation-verifier)，而非助手的总结内容。

### 总是会被禁止的路径

即使未设置 `HERMES_WRITE_SAFE_ROOT`，以下类别的路径也始终会被拒绝写入：

| 类别 | 示例 |
|------|------|
| 操作系统凭证存储路径 | `~/.ssh/`（密钥、`authorized_keys`文件）、`~/.aws/`、`~/.kube/`、`/etc/sudoers`、`~/.netrc` |
| Hermes 系统凭证存储路径 | `auth.json`、`.env`、`.anthropic_oauth.json`，以及位于 HERMES_HOME 目录下的 `mcp-tokens/` 和 `pairing/` 文件（包含当前激活的配置文件及全局根配置） |
| 项目级密钥文件 | 磁盘上任意位置的 `.env`、`.env.local`、`.env.production`、`.envrc` 文件 |

即使是在安全根目录内的敏感路径仍会被屏蔽——将 `HERMES_WRITE_SAFE_ROOT` 设置为 `$HOME` 也无法写入 `~/.ssh/id_rsa` 文件。

若尝试访问被禁止的路径，系统会返回错误信息：“写入被拒绝：‘…’位于 HERMES_WRITE_SAFE_ROOT（…）范围之外。”而对于凭证相关路径的访问，错误提示则为：“写入被拒绝：‘…’是受保护的系统/凭证文件。”

**例外情况——`~/.ssh/config` 文件需经过审批才能修改，而非直接被屏蔽。** 该 SSH *客户端配置文件* 不包含任何私钥信息，且对其进行的编辑操作（如主机别名设置、`ProxyJump` 配置、VS Code Remote-SSH 目标地址等）属于常规操作。因此，`write_file`/`patch` 功能会通过终端工具中用于处理 `~/.ssh` 文件写入操作的相同审批流程来执行操作——而非以往那种直接拒绝的方式。该文件仍可包含用于运行命令的 `ProxyCommand`/`Match exec` 指令，故写入操作不会完全无声无息。非交互式调用方式（如 ACP 文件桥接、无人工交互的后台任务）将会被直接拒绝。而私钥、`authorized_keys` 文件以及 `~/.ssh/` 目录下的其他所有文件依然处于严格屏蔽状态。

### HERMES_WRITE_SAFE_ROOT（可选沙箱功能）

一旦设置，`write_file` 和 `patch` 命令仅能作用于所指定目录前缀内的路径。任何位于该范围之外的路径都将被**严格禁止**——不会经过危险命令审批流程。

- 在[官方 Docker 镜像](https://github.com/NousResearch/hermes-agent)中会自动设置该值（`HERMES_WRITE_SAFE_ROOT=/opt/data`）
- 在 Unix 系统上可使用 `:` 分隔多个根目录，在 Windows 系统上则使用 `;`
- **请勿随意在 `~/.hermes/.env` 文件中修改此值。** 若将其设置为项目目录，代理将无法写入 `~/.hermes/cron/jobs.json`、配置文件中的技能信息，以及该前缀之外的其他 Hermes 状态数据。

如需同时允许使用工作区目录和 Hermes 主目录：

```bash
export HERMES_WRITE_SAFE_ROOT=/path/to/project:/home/you/.hermes
```

将该变量重置为默认值即可恢复无限制写入功能（但仍受受保护路径的拒绝列表约束）。完整参考文档：[HERMES_WRITE_SAFE_ROOT](../reference/environment-variables.md#hermes_write_safe_root)。

### Cron及其他Hermes状态文件

请勿直接要求智能体`patch` `~/.hermes/cron/jobs.json`文件。应使用`cronjob`工具、[`hermes cron`](./features/cron.md)或 `/cron`命令——它们会通过官方支持的API来更新任务存储。当写入保护机制禁止直接编辑时，其他Hermes控制文件也应遵循相同原则。

:::注意：这是多层防御策略，并非绝对隔离
写入保护仅适用于`write_file`和`patch`操作。`terminal`工具以相同的操作系统用户身份运行，仍可通过Shell命令读取或覆盖被禁止的路径。拒绝列表旨在减少意外损害并为模型提供明确的停止信号，但它并不能将恶意或已被攻破的智能体完全隔离在沙箱中。
:::

## 用户授权（网关）

在运行消息网关时，Hermes通过分层授权系统来控制谁可以与机器人交互。

### 授权检查顺序

 `_is_user_authorized()`方法会按以下顺序进行验证：

1. **平台级全允许标志**（例如 `DISCORD_ALLOW_ALL_USERS=true`）
2. **私信配对授权列表**（通过配对码获得授权的用户）
3. **平台特定允许列表**（例如 `TELEGRAM_ALLOWED_USERS=12345,67890`）
4. **全局允许列表**（`GATEWAY_ALLOWED_USERS=12345,67890`）
5. **全局全允许设置**（`GATEWAY_ALLOW_ALL_USERS=true`）
6. **默认值：拒绝**

### 平台允许列表

在 `~/.hermes/.env` 文件中，以逗号分隔的形式设置允许使用的用户 ID：

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

为实现更灵活的授权机制，Hermes 提供了基于代码的配对系统。该系统无需预先获取用户 ID，未知用户会收到一个一次性配对码，由机器人所有者通过 CLI 进行批准。

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
- 除非设置了`platforms.email.unauthorized_dm_behavior: pair`，否则电子邮件的默认处理方式也是`ignore`，因为收件箱中可能包含大量无关的未读邮件。
- 各平台的特定设置可覆盖全局默认值，因此您可以在Telegram上保持配对功能，而对WhatsApp则设置为静默忽略。

**安全特性**（基于OWASP及NIST SP 800-63-4标准）：

| 特性 | 详情 |
|------|------|
| 密码格式 | 从32个字符的专用字母表中选取8位字符，且不含0、O、1、I |
| 随机性 | 采用加密级随机生成方式（`secrets.choice()`） |
| 密码有效期 | 1小时后过期 |
| 请求频率限制 | 每名用户每10分钟仅可发起1次请求 |
| 待处理代码上限 | 每个平台最多有3个待处理配对码 |
| 冒用防护 | 若连续5次审批失败，账户将被锁定1小时 |
| 文件安全 | 所有配对数据文件均执行`chmod 0600`权限设置 |
| 日志记录 | 配对码绝不会被记录到标准输出中 |

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
官方 Docker 镜像会通过 `gosu` 工具，以无特殊权限的 `hermes` 用户（UID 10000）身份来运行网关，但 `docker exec` 命令默认以 root 用户身份执行。由 root 用户创建的审批文件会被设置为 `0600 root:root` 的权限模式，导致网关无法读取这些文件——此时审批请求将会被 silently 忽略（[#10270][i10270]）。  
请始终使用 `-u hermes` 参数来执行命令：

```bash
docker exec -u hermes hermes-agent hermes pairing approve telegram ABC12DEF
```

如果您已以 root 权限运行了该命令，但用户仍未被授权，请重新启动容器——下次启动时，入口点将会自动修正文件所有权问题。

[i10270]: https://github.com/NousResearch/hermes-agent/issues/10270
:::

**存储：** 配对数据存储在 `~/.hermes/pairing/` 目录下，采用针对不同平台的 JSON 文件形式：
- `{platform}-pending.json` — 待处理的配对请求
- `{platform}-approved.json` — 已通过验证的用户
- `_rate_limits.json` — 流量限制与封禁状态记录

## 容器隔离

在使用 `docker` 终端后端时，Hermes 会对每个容器实施严格的安全加固措施。

### Docker 安全标志位

每个容器均会以这些标志位运行（定义于 `tools/environments/docker.py` 文件中）：

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

`SETUID`/`SETGID` **并不**包含在基础列表中——只有当容器以 root 权限启动且需要通过 init/入口点来降低权限时（即遵循 s6 的权限降级机制），才会条件性地将其加入。如果容器已通过 `--user` 参数以非 root 权限运行，则会跳过这些指令。此外，`/run` tmpfs 也独立于基础列表，会根据每个镜像进行单独挂载（默认设置为强制禁止执行的 `noexec` 模式，仅对于从 `/run` 目录执行操作的 s6-overlay 镜像才允许使用 `exec` 模式）。

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
- **临时模式**（`container_persistent: false`）：工作区使用 tmpfs 存储——清理时所有数据都会丢失。

:::tip
对于生产环境中的网关部署，建议使用 `docker`、`modal`、`daytona` 或 `vercel_sandbox` 作为后端，以此将 Agent 命令与主机系统隔离开来。这样一来就完全无需进行危险的命令审批流程了。
:::

:::warning
如果在 `terminal.docker_forward_env` 中添加变量名，这些变量将会被直接注入到用于终端命令的容器中。这对于处理任务专用的凭证（如 `GITHUB_TOKEN`）非常有用，但同时也意味着容器中的代码能够读取并窃取这些凭证。
:::

## 终端后端安全性对比

| 后端 | 隔离程度 | 危险命令检查 | 最佳适用场景 |
|---------|-----------|-------------------|--------------|
| **local** | 无——在主机上运行 | ✅ 有 | 开发环境及可信用户 |
| **ssh** | 远程机器 | ✅ 有 | 在独立服务器上运行 |
| **docker** | 容器级别 | ❌ 跳过（容器本身即构成隔离边界） | 生产环境网关 |
| **singularity** | 容器级别 | ❌ 跳过 | 高性能计算环境 |
| **modal** | 云沙箱 | ❌ 跳过 | 需要高度可扩展的云隔离场景 |
| **daytona** | 云沙箱 | ❌ 跳过 | 需要持久化云工作区的场景 |
| **vercel_sandbox** | 云微虚拟机 | ❌ 跳过 | 支持快照持久化的云执行环境 |
## 环境变量传递 {#environment-variable-passthrough}

`execute_code` 和 `terminal` 功能都会从子进程中移除敏感的环境变量，以防止由大语言模型生成的代码窃取凭证。不过，那些明确声明了 `required_environment_variables` 的技能确实需要访问这些变量。

Buzz 消息平台所使用的第一方平台凭证——即 `BUZZ_*` 变量——**仅当会话实际以 Buzz Agent 的身份运行时**，才会被传递给 `terminal` 的子进程（包括前台进程和后台/PTY 子进程）：也就是说，该进程必须是 Buzz-ACP 管理的 Agent（由 Buzz Desktop 工具设置 `BUZZ_MANAGED_AGENT` 标志），或者实时网关会话的平台类型为 `buzz`。这样一来，Buzz 平台 Agent 就能够通过终端工具调用其平台要求的 CLI 命令（如 `buzz`），而同一主机上的 Telegram/CLI/cron 会话则仍会保持这些变量被移除的状态。由于 `_sanitize_subprocess_env` 函数还会为搜索工作进程（如 ddgs 网页搜索子进程）、计算机使用驱动程序二进制文件以及用户脚本执行器（如 `!` 命令、快速命令、cron 脚本、webhook 过滤脚本）提供环境变量，因此从 Buzz 会话中启动的这些子进程也能获取到这些变量。但这种传递机制**仅限于终端环境**：它不适用于 `execute_code` 功能、浏览器/TUI 环境下的子进程（通过 `hermes_subprocess_env` 传递）、Docker/Modal 环境下的子进程，以及通过 `env_passthrough` 注册的子进程，后几类进程的变量仍会被严格隔离。

### 工作原理

有两种机制可用于让特定的变量穿透沙箱过滤机制：

**1. 基于技能范围的自动透传功能**

当某个技能通过 `skill_view` 命令或 `/skill` 命令被加载，并且指定了 `required_environment_variables` 时，环境中实际已设置的任意变量都会自动被注册为透传变量。而那些尚未设置（仍处于需要配置状态）的变量则**不会**被注册。

```yaml
# In a skill's SKILL.md frontmatter
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
```

加载该技能后，`TENOR_API_KEY` 将自动传递给 `execute_code`、本地终端以及远程后端（Docker、Modal），无需进行任何手动配置。

:::info Docker与Modal
在 v0.5.1 版本之前，Docker 的 `forward_env` 功能与技能参数传递机制是相互独立的。如今二者已实现整合——通过技能声明的环境变量会自动被传输到 Docker 容器及 Modal 沙箱中，无需再手动添加到 `docker_forward_env` 中。
:::

**2. 基于配置的参数传递（手动方式）**

对于未被任何技能声明的环境变量，可将其添加到 `config.yaml` 文件中的 `terminal.env_passthrough` 字段中：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

### 凭证文件传递（OAuth 令牌等）{#credential-file-passthrough}

某些智能体在沙箱环境中需要**文件**（而不仅仅是环境变量）——例如，Google Workspace会将OAuth令牌存储在当前活跃配置文件的`HERMES_HOME`目录下的`google_token.json`文件中。智能体可通过前置信息来声明这些所需文件：

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials
```

在加载时，Hermes 会检查当前激活配置文件中的 `HERMES_HOME` 目录中是否存在这些文件，并对它们进行挂载处理：

- **Docker**：使用只读绑定挂载（`-v host:container:ro`）
- **Modal**：在创建沙箱时即进行挂载，并在每条命令执行前同步数据（可处理会话进行中的 OAuth 设置）
- **本地环境**：无需任何操作（文件已可直接访问）

您也可以在 `config.yaml` 文件中手动列出凭证文件：

```yaml
terminal:
  credential_files:
    - google_token.json
    - my_custom_oauth_token.json
```

路径是相对于 `~/.hermes/` 的。文件会被挂载到容器内的 `/root/.hermes/` 目录中。`tools/credential_files.py`（即 `terminal.credential_files`）会读取该列表——它位于 `terminal:` 块下，但由凭证文件模块加载，而非核心终端后端，因此不会被包含在预打包的 `DEFAULT_CONFIG` 配置快照中。

### 各沙箱的过滤规则

| 沙箱类型 | 默认过滤规则 | 传递覆盖规则 |
|---------|---------------|----------------|
| **execute_code** | 阻止名称中包含 `KEY`、`TOKEN`、`SECRET`、`PASSWORD`、`CREDENTIAL`、`PASSWD`、`AUTH` 等字样的变量；仅允许带有安全前缀的变量通过 | ✅ 通过传递规则的变量可绕过这两项检查 |
| **terminal**（本地） | 阻止所有明确的 Hermes 基础设施相关变量（如提供程序密钥、网关令牌、工具 API 密钥） | ✅ 通过传递规则的变量可绕过该阻止列表 |
| **terminal**（Docker） | 默认不传递任何主机环境变量 | ✅ 通过传递规则的变量，以及通过 `-e` 参数传递的 `docker_forward_env` 变量可被传输 |
| **terminal**（SSH） | 默认不传递任何主机环境变量 | ✅ 通过 `SendEnv` 功能传递的变量可被传输；远程端的 `sshd_config` 文件需配置相应的 `AcceptEnv` 选项（详见[SSH 后端](configuration.md#ssh-backend)） |
| **terminal**（Modal） | 默认不传递任何主机环境变量或文件 | ✅ 凭证文件会被挂载；环境变量可通过同步方式传递 |
| **MCP** | 除安全的系统变量及明确配置的 `env` 变量外，其余所有内容均被阻止 | ❌ 不受传递规则影响（请使用 MCP 的 `env` 配置选项） |

### 安全注意事项

- 仅您或您的技能明确声明的变量才会被传递，对于由大语言模型生成的任意代码，其默认安全策略保持不变。  
- 凭证文件会以**只读**方式挂载到 Docker 容器中。  
- Skills Guard 会在技能安装前扫描其内容，检测是否存在异常的环境访问模式。  
- 缺失或未设置的变量不会被注册——既然不存在，自然也就无法泄露。  
- Hermes 的基础设施机密信息（如提供程序 API 密钥、网关令牌）绝不应添加到 `env_passthrough` 中，因为已有专门的机制来处理这些信息。  

## MCP 凭证处理机制  

为防止凭证意外泄露，MCP（模型上下文协议）服务器的子进程会接收一个**经过过滤的环境变量集**。  

### 安全的环境变量  

仅有以下变量会从主机传递给 MCP 的标准输入/输出子进程：

```
PATH, HOME, USER, LANG, LC_ALL, TERM, SHELL, TMPDIR
```

此外还包括所有的 `XDG_*` 变量。所有其他环境变量（如 API 密钥、令牌及机密信息）均会被**移除**。

在 MCP 服务器的 `env` 配置中明确定义的变量则会被原样传递：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."  # Only this is passed
```

### 凭证遮蔽处理

MCP 工具返回给大型语言模型的错误信息在传递之前会经过净化处理。以下格式的内容将被替换为 `[REDACTED]`：

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

所有支持处理网址的工具（网络搜索、网页提取、视觉分析、浏览器功能）在获取网址之前都会对其进行检查，以防止服务器端请求伪造（SSRF）攻击。被屏蔽的地址包括：

- **私有网络**（RFC 1918标准）：`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- **回环地址**：`127.0.0.0/8`、`::1`
- **链路本地地址**：`169.254.0.0/16`（包括位于 `169.254.169.254` 的云元数据地址）
- **CGNAT/共享地址空间**（RFC 6598标准）：`100.64.0.0/10`（适用于Tailscale、WireGuard VPN）
- **云元数据主机名**：`metadata.google.internal`、`metadata.goog`
- **预留地址、多播地址及未指定地址**

对于面向互联网的应用，SSRF防护机制始终处于激活状态，且DNS请求失败会被视为被屏蔽（采取立即拒绝策略）。为防止通过重定向绕过限制，每个重定向环节都会再次进行验证。

#### 有意识地允许访问私有网址

某些场景确实需要访问私有或内部网址——例如将 `home.arpa` 解析为RFC 1918地址段的家庭网络、仅限局域网使用的Ollama/llama.cpp服务端、内部Wiki、云元数据调试等。针对这类情况，提供了全局禁用选项：

```yaml
security:
  allow_private_urls: true   # default: false
```

启用该功能后，Web工具、浏览器、视觉URL获取以及网关媒体下载将不再拒绝来自RFC 1918地址、回环地址、链路本地地址、CGNAT地址及云元数据地址的请求。**这是一项有意设置的信任边界**——仅应在那些能够承受Agent向本地网络发送任意注入式URL所带来的风险的设备上启用该功能。面向公网的网关则应保持该功能关闭状态。

无论是否启用此设置，主机子串防护机制（即便底层IP为公网地址，也能有效阻止类似Unicode域名的欺骗手段）仍将持续运行。

### Tirith预执行安全扫描

Hermes集成了[tirith](https://github.com/sheeki03/tirith)工具，可在命令执行前进行内容级扫描。Tirith能够检测出仅靠模式匹配无法发现的威胁，包括：

- 同形异义字URL欺骗（国际化域名攻击）
- 从管道传递到解释器的指令模式（如`curl | bash`、`wget | sh`）
- 终端注入攻击

首次使用时，Tirith会通过SHA-256校验和验证（若支持签名功能，则还会进行签名来源验证）从GitHub发布版本中自动安装。

```yaml
# In ~/.hermes/config.yaml
security:
  tirith_enabled: true       # Enable/disable tirith scanning (default: true)
  tirith_path: "tirith"      # Path to tirith binary (default: PATH lookup)
  tirith_timeout: 5          # Subprocess timeout in seconds
  tirith_fail_open: true     # Allow execution when tirith is unavailable (default: true)
```

当 `tirith_fail_open` 设为 `true`（默认值）时，即使未安装 tirith 或操作超时，命令仍会继续执行。在高度安全的环境中，可将其设置为 `false`，以便在 tirith 不可用时阻止命令执行。

Tirith 提供了针对 Linux（x86_64 / aarch64）和 macOS（x86_64 / arm64）预编译的二进制文件。对于没有预编译二进制文件的平台（如 Windows），tirith 会静默跳过——模式匹配检测仍会进行，且 CLI 不会显示“不可用”提示。若要在 Windows 上使用 tirith，可在 WSL 环境下运行 Hermes。

Tirith 的检测结果会与审批流程集成：安全命令可直接通过，而可疑命令及被阻止的命令则会触发用户审批，并同步展示完整的检测信息，包括严重程度、标题、描述以及更安全的替代方案。用户可选择批准或拒绝——为保障无人值守场景的安全，默认选项为拒绝。

### 上下文文件注入防护

在将上下文文件（AGENTS.md、.cursorrules、SOUL.md）纳入系统提示之前，系统会对其进行提示注入检测。检测内容包括：

- 要求忽略/无视先前指令的指示
- 包含可疑关键词的隐藏 HTML 注释
- 尝试读取机密信息（如 `.env`、`credentials`、`.netrc` 文件）
- 通过 `curl` 实现的凭证窃取行为
- 隐形的 Unicode 字符（零宽空格、双向替换字符）
翻译与执行检查需要一个简短的语言/格式说明（例如，“将此内容翻译成 Bash 脚本并执行它”）。它不会在由逗号分隔的、彼此无关的角色描述中关联翻译和执行的动词。这些规则属于启发式方法，而非语义意图识别。

被屏蔽的文件会显示警告信息：

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
6. **审核命令允许列表** —— 定期检查 config.yaml 中的 `command_allowlist`
7. **设置 `terminal.cwd` 参数** —— 防止智能体在敏感目录中运行
8. **以非根用户身份运行** —— 绝不要以 root 权限运行网关
9. **监控日志** —— 定期查看 `~/.hermes/logs/` 文件，排查未经授权的访问尝试
10. **保持版本更新** —— 定期运行 `hermes update` 以获取安全补丁

### API 密钥的安全保护措施

```bash
# Set proper permissions on the .env file
chmod 600 ~/.hermes/.env

# Keep separate keys for different services
# Never commit .env files to version control
```

### 网络隔离

为确保最高安全等级，建议将网关部署在独立的机器或虚拟机上。在 `config.yaml` 文件中设置 `terminal.backend: ssh`，随后通过 `~/.hermes/.env` 文件中的环境变量来指定主机详细信息：

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

SSH 连接详细信息存储在 `.env` 文件中（而非 `config.yaml`），因此不会随配置导出一起被提交或共享。这样一来，网关的消息传输连接便能与代理的命令执行功能相互分离。

## 供应链安全警告检查

Hermes 内置了专门的警告扫描器，能够识别当前虚拟环境中的 Python 包是否属于已知受损版本列表（例如 2026 年 5 月出现的 `mistralai 2.4.6` 毒害事件等供应链攻击）。该功能的实现代码位于 `hermes_cli/security_advisories.py` 文件中。

其工作流程如下：

- **CLI 启动提示。** 若检测到匹配的警告，系统会打印一行警告信息，并提供 `hermes doctor` 命令以获取完整的修复方案。
- **`hermes doctor` 命令。** 会列出所有当前的警告信息，包括具体版本号以及 2-4 步的修复指导。
- **网关启动时。** 相关日志会被记录到 `gateway.log` 文件中；在首次交互消息中还会显示简短的操作提示。

每条警告信息都配有唯一的稳定标识符。一旦您已阅读并采取了相应措施，即可永久将其标记为已处理。

```bash
hermes doctor --ack <advisory-id>
```

确认信息会被持久保存在 `config.security.acked_advisories` 中，因此即使重启也不会丢失。系统故意**不会**从列表中移除旧的建议项——将它们保留原位可以确保新安装的用户能够收到警告，提醒他们私服缓存中可能仍存在已受污染的旧版本。

该检查仅依赖标准库，且针对每个建议项只会执行一次 `importlib.metadata.version()` 查询，因此可在每次启动时安全运行。

### 可选依赖的延迟加载

许多功能（如 Mistral TTS、ElevenLabs、Honcho 内存功能、Bedrock、Slack、Matrix 等）依赖于并非所有用户都需要的 Python 包。Hermes 会在首次使用时**延迟加载**这些包，而非在 `hermes-agent[all]` 配置下立即加载。相关实现位于 `tools/lazy_deps.py` 文件中。

这种机制解决了以下问题：

- **脆弱性**：如果某个额外组件的间接依赖在 PyPI 上不可用（被标记为恶意软件、被下架或上传失败），整个 `[all]` 组的依赖解析就会失败，新安装的用户将自动降级到精简版本——导致 10 多个无关的额外功能同时失效。而延迟加载机制能够隔离各个后端，避免某个受污染的依赖破坏其他功能。
- **臃肿问题**：那些仅使用单一服务提供商的用户，再也不用下载数百个他们根本不会使用的包。

其工作原理如下：

1. 后端模块会在其首次导入路径的开头调用 `ensure("feature.name")`。
2. 若所需依赖缺失，`ensure` 函数会检查 `config.yaml` 中的 `security.allow_lazy_installs` 设置（默认值为 `true`），并为已列出的依赖项在当前虚拟环境中执行 `pip install` 操作。
3. 如果安装失败或用户已禁用延迟安装功能，该调用将抛出 `FeatureUnavailable` 异常，同时附带实际的 pip 错误信息以及指向 `hermes tools` 的引用。

`tools/lazy_deps.py` 所提供的安全保障措施如下：

| 安全保障 | 含义说明 |
|---|---|
| 仅限虚拟环境操作 | 依赖项将安装到当前活跃虚拟环境中的 `sys.executable`，而绝不会影响系统级的 Python 环境 |
| 仅支持通过包名安装 | 依赖规格仅接受 `"package>=1.0,<2"` 这类格式的指定。不允许使用 `--index-url`、`git+https://` 或文件路径等形式——恶意修改的 `config.yaml` 无法改变安装目标 |
| 白名单机制 | 仅允许那些出现在项目内部 `LAZY_DEPS` 映表中的依赖项通过此路径进行安装。即使功能名称拼写有误，也不会触发自动安装行为 |
| 可选择性禁用 | 将 `security.allow_lazy_installs` 设置为 `false` 即可完全禁止运行时安装功能。此设置适用于网络受限或安全要求极高的环境 |
| 无隐式重试机制 | 安装失败会直接以 `FeatureUnavailable` 的形式体现——不会缓存错误状态，也不会发生重复尝试带来的冲击 |

如需禁用运行时安装功能：

```yaml
# ~/.hermes/config.yaml
security:
  allow_lazy_installs: false
```

当该功能被禁用时，那些需要可选依赖的后端会提示用户手动执行安装操作（`pip install …`），或通过 `hermes tools` 选择其他后端。
