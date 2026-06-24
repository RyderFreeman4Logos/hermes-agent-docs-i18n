---
sidebar_position: 3
title: "Updating & Uninstalling"
description: "How to update Hermes Agent to the latest version or uninstall it"
---

# 更新与卸载

## 更新

仅需一条命令即可升级到最新版本：

```bash
hermes update
```

该命令会从 `main` 分支拉取最新代码，更新依赖项，并提示您配置自上次更新后新增的选项。

:::tip
`hermes update` 会自动检测新的配置选项并提示您添加它们。如果您忽略了相关提示，可以手动运行 `hermes config check` 查看缺失的选项，然后再使用 `hermes config migrate` 以交互方式将其添加。
:::

### 更新过程中会发生什么

当您运行 `hermes update` 时，将依次执行以下步骤：

1. **配对数据快照**——会保存一个轻量级的更新前状态快照（涵盖 `~/.hermes/pairing/`、飞书评论规则以及运行时会被修改的其他状态文件）。您可以通过 [快照与回滚](../user-guide/checkpoints-and-rollback.md) 中介绍的快照恢复流程来恢复该状态，或者直接提取 Hermes 存放在 `~/.hermes/` 目录旁的最新快速快照压缩包。
2. **Git 拉取**——从 `main` 分支拉取最新代码并更新子模块。
3. **拉取后的语法验证 + 自动回滚**——拉取完成后，Hermes 会编译每次启动时 `hermes` 命令所调用的八个关键文件。如果其中有任何文件无法解析（例如存在孤立的合并冲突标记、文件被意外截断等），Hermes 会执行 `git reset --hard <pre-pull-sha>` 将安装状态回滚，以确保您的 shell 能够正常启动。待上游代码修复完成后，再重新运行 `hermes update` 即可。
4. **依赖项安装**——运行 `uv pip install -e ".[all]"` 以安装新添加或已变更的依赖项。
5. **配置迁移**——检测自您当前版本之后新增的配置选项，并提示您进行设置。
6. **网关自动重启**——更新完成后，正在运行的网关会得到刷新，从而使新代码立即生效。由系统管理的网关（Linux 系统中的 systemd，macOS 系统中的 launchd）会通过相应的服务管理器重启；而手动创建的网关则会在 Hermes 能够将当前运行进程 ID 对应到相应配置文件后自动重新启动。

### 基于非默认分支进行更新：`--branch`

默认情况下，`hermes update` 会跟踪 `origin/main` 分支。如果您需要基于其他分支进行更新，可以传递 `--branch <name>` 参数——这对于测试渠道、功能分支或候选版本测试非常有用：

```bash
hermes update --branch release-candidate
hermes update --check --branch experimental   # preview behindness only
```

如果您的本地检出分支与目标分支不同，Hermes会自动暂存所有未提交的更改，将HEAD指针切换到目标分支，然后再执行拉取操作。对于本地不存在的分支，系统会自动从`origin/<名称>`中追踪该分支（可通过`git checkout -B <名称> origin/<名称>`实现）。而对于完全不存在的分支，系统会确保流程干净利落地终止——在退出前会恢复您暂存的更改，避免您陷入异常状态。对于非`main`分支，系统会自动跳过仅针对`main`分支的同步逻辑。

### 非交互式更新时的本地更改处理

当您在终端中运行`hermes update`命令时，Hermes会先暂存所有未提交的源代码更改，随后执行拉取操作，最后**询问**您是否要恢复这些更改——这一流程与以往完全一致。对于交互式更新而言，则没有变化。

当更新在**非终端环境**中运行时——比如通过桌面端/聊天应用中的“更新”按钮或由网关触发的更新——系统不会出现询问提示。此时，`updates.non_interactive_local_changes`设置将决定您暂存的更改该如何处理：

```yaml
# ~/.hermes/config.yaml
updates:
  non_interactive_local_changes: stash   # default: keep + auto-restore
  # non_interactive_local_changes: discard  # throw local source edits away
```

- `stash`（默认值）——自动将您的更改暂存，然后拉取最新代码，最后再自动恢复这些更改。这样不会丢失任何内容；如果恢复过程中出现冲突，这些冲突会被保存在 Git 暂存区中，以便您手动处理。
- `discard`——在拉取代码后自动暂存更改，随后立即丢弃该暂存内容，确保更新后的代码库始终处于干净状态。仅建议在那些无需保留 Hermes 源代码本地修改的机器上使用此选项。它采用暂存后丢弃的方式（而非 `git reset --hard` + `git clean -fd`），因此不会触碰 `node_modules`、`venv` 以及构建输出等被忽略的目录。

在桌面应用程序中，该选项位于 **设置 → 高级设置 → 应用内更新本地更改**。

### 仅预览功能：`hermes update --check`

想在拉取代码之前先确认是否有可用更新？可以运行 `hermes update --check` ——该命令会获取最新代码并与 `origin/main` 进行比对。此操作不会修改任何文件，也不会重启网关。非常适合用于那些需要根据“是否有更新”来决定是否执行的脚本和定时任务中。

### 完整的更新前备份：`--backup`

对于那些价值较高的配置（如生产环境网关、团队共享安装环境），您可以选择在拉取代码之前对 `HERMES_HOME` 目录进行完整备份，内容包括配置文件、认证信息、会话数据、技能信息以及配对关系等。

```bash
hermes update --backup
```

或者将其设置为每次运行的默认值：

```yaml
# ~/.hermes/config.yaml
updates:
  pre_update_backup: true
```

在早期版本中，`--backup` 功能处于始终开启状态，但由于它会增加大型家庭环境每次更新的耗时，因此现在改为可选启用。而上述轻量级的配对数据快照仍会无条件执行。

### Windows：正在运行另一个 `hermes.exe` 进程

在 Windows 系统上，如果检测到有其他 `hermes.exe` 进程正在占用虚拟环境的入口点可执行文件，`hermes update` 命令将拒绝执行——这类进程通常包括 Hermes Desktop 应用生成的底层服务、其他终端中正在运行的 `hermes` REPL，或是正在运行的网关程序：

```
$ hermes update
✗ Another hermes.exe is running:
    PID 12345  hermes.exe

  Updating now would fail to overwrite ...\venv\Scripts\hermes.exe because
  Windows blocks REPLACE on a running executable.

  Close Hermes Desktop, exit any open `hermes` REPLs, and
  stop the gateway (`hermes gateway stop`) before retrying.
  Override with `hermes update --force` if you've already
  confirmed those processes will not write to the venv.
```

请关闭列出的进程后重新运行。如果您确定这些并发进程不会造成干扰（这种情况较为罕见——通常仅在杀毒程序的拦截机制出现错误时才有用），可传递 `--force` 参数以跳过该检查。即便如此，更新工具仍会以指数退避策略尝试重命名 `.exe` 文件；对于顽固的锁定问题，则会通过 `MoveFileEx(MOVEFILE_DELAY_UNTIL_REBOOT)` 函数将文件替换操作安排在下次重启时执行，从而确保更新能够顺利完成。

预期输出如下所示：

```
$ hermes update
Updating Hermes Agent...
📥 Pulling latest code...
Already up to date.  (or: Updating abc1234..def5678)
📦 Updating dependencies...
✅ Dependencies updated
🔍 Checking for new config options...
✅ Config is up to date  (or: Found 2 new options — running migration...)
🔄 Restarting gateways...
✅ Gateway restarted
✅ Hermes Agent updated successfully!
```

### 建议的更新后验证步骤

虽然 `hermes update` 已能完成主要的更新流程，但进行快速验证可确保一切正常：

1. `git status --short` —— 若工作区状态异常，建议先检查问题再继续操作
2. `hermes doctor` —— 检查配置、依赖项以及服务运行状态
3. `hermes --version` —— 确认版本号已如预期升级
4. 若使用了网关，请执行 `hermes gateway status`
5. 若 `doctor` 检测到 npm 安全审计问题，请在对应目录中运行 `npm audit fix`

:::warning 更新后工作区状态异常
如果在执行 `hermes update` 后，`git status --short` 显示有意外变更，建议暂停并检查这些变更，切勿继续。这通常意味着本地修改内容被重新应用到了已更新的代码之上，或是某个依赖项更新过程刷新了锁文件。
:::

### 若在更新过程中终端断开连接

`hermes update` 具备防止终端意外丢失的保护机制：

- 该工具会忽略 `SIGHUP` 信号，因此关闭 SSH 连接或终端窗口不会导致更新过程中断。`pip` 和 `git` 子进程也享有同样的保护机制，避免因连接中断而导致 Python 环境处于半安装状态。
- 在更新过程中，所有输出信息都会同步记录到 `~/.hermes/logs/update.log` 文件中。如果终端突然消失，重新连接后可通过查看该日志来判断更新是否已完成，以及网关重启是否成功：

```bash
tail -f ~/.hermes/logs/update.log
```

- `Ctrl-C`（SIGINT信号）及系统关机（SIGTERM信号）仍然有效——这些都属于主动的取消操作，而非意外情况。

您不再需要将 `hermes update` 嵌入 `screen` 或 `tmux` 中，从而避免因终端中断而影响操作。

### 查看当前版本

```bash
hermes version
```

请访问 [GitHub 发布页面](https://github.com/NousResearch/hermes-agent/releases)，将当前版本与最新发布版本进行对比。

### 通过消息平台进行更新

您也可以直接通过 Telegram、Discord、Slack、WhatsApp 或 Teams 发送相应指令来完成更新：

```
/update
```

该操作会拉取最新代码、更新依赖项，并重启正在运行的网关。在重启过程中，机器人将会短暂离线（通常为5至15秒），之后便会恢复正常运行。

### 手动更新

如果您是手动安装的（而非通过快速安装程序）：

```bash
cd /path/to/hermes-agent
export VIRTUAL_ENV="$(pwd)/venv"

# Pull latest code
git pull origin main

# Reinstall (picks up new dependencies)
uv pip install -e ".[all]"

# Check for new config options
hermes config check
hermes config migrate   # Interactively add any missing options
```

### 回滚说明

如果某次更新引发了问题，您可以回退到之前的版本：

```bash
cd /path/to/hermes-agent

# List recent versions
git log --oneline -10

# Roll back to a specific commit
git checkout <commit-hash>
uv pip install -e ".[all]"

# Restart the gateway if running
hermes gateway restart
```

如需回滚到特定的版本标签（请替换为您之前的标签——例如最近的版本 `v2026.5.16`，或是通过 `git tag --sort=-version:refname` 查看的更早版本标签）：

```bash
git checkout vX.Y.Z
uv pip install -e ".[all]"
```

:::warning
如果新增了配置选项，回滚操作可能会导致配置不兼容。请在回滚后运行 `hermes config check`，若出现错误，请从 `config.yaml` 中删除所有未被识别的选项。
:::

### 面向 Nix 用户的说明

如果您是通过 Nix flake 安装的，更新将通过 Nix 包管理器来处理：

```bash
# Update the flake input
nix flake update hermes-agent

# Or rebuild with the latest
nix profile upgrade hermes-agent
```

Nix 的安装结果是不可变的——回滚操作由 Nix 的生成系统来处理：

```bash
nix profile rollback
```

如需了解更多详细信息，请参阅 [Nix 设置](./nix-setup.md)。

```bash
hermes uninstall
```

卸载程序会为您提供一个选项，允许您保留配置文件（位于 `~/.hermes/` 目录中），以便日后重新安装时使用。

### 手动卸载

```bash
rm -f ~/.local/bin/hermes
rm -rf /path/to/hermes-agent
rm -rf ~/.hermes            # Optional — keep if you plan to reinstall
```

:::info
如果您是以系统服务的方式安装了网关，请先停止并禁用该服务：
```bash
hermes gateway stop
# Linux: systemctl --user disable hermes-gateway
# macOS: launchctl remove ai.hermes.gateway
```
:::
