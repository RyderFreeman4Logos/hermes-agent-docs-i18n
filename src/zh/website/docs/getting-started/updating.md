---
sidebar_position: 3
title: "Updating & Uninstalling"
description: "How to update Hermes Agent to the latest version or uninstall it"
---

# 更新与卸载

## 更新

只需一条命令即可升级到最新版本：

```bash
hermes update
```

该命令会从 `main` 分支获取最新代码，更新依赖项，并提示您配置自上次更新后新增的选项。

:::提示
`hermes update` 会自动检测新的配置选项并提示您添加它们。如果您忽略了相关提示，可以手动运行 `hermes config check` 查看缺失的选项，然后再使用 `hermes config migrate` 以交互方式将其添加。
:::

### 被动更新通知

已固定或非交互式的安装方式可禁用对 CLI 版本及版本信息横幅的被动检查：

```bash
hermes config set updates.check false
```

此设置可同时抑制缓存中的更新通知以及被动进行的更新检查网络请求。默认值为 `true`。明确使用 `hermes update --check` 和 `hermes update` 命令仍然有效；该设置并不控制桌面应用程序的更新器。

### 更新过程中的操作

当您运行 `hermes update` 时，会依次执行以下步骤：

1. **更新前快照生成**——默认情况下会保存一个轻量级的状态快照（涵盖配对数据、定时任务、`config.yaml`、`.env`、`auth.json` 以及运行时会被修改的其他状态文件；单个文件大小超过 1 GiB 的会被跳过，以避免庞大的会话数据库影响更新速度）。由于代码替换和网关重启会涉及所有配置文件，因此系统会为安装后的**每个配置文件**生成相同的快照——每个快照都保存在独立的 `state-snapshots/` 目录中——更新后的定时任务还会通过对比每个配置文件与其对应的快照来确保系统稳定。该功能的开启状态由 `updates.pre_update_backup` 控制（默认为 `quick` 模式，即仅生成快照；`full` 模式则会对整个 `HERMES_HOME` 目录进行压缩备份；`off` 表示禁用此功能）。可通过 [快照与回滚](../user-guide/checkpoints-and-rollback.md) 中描述的流程恢复快照。快速快照仅用于恢复文件丢失的情况，无法实现代码层面的回滚——如需进行精确到某一时间点的回滚，请使用 `--backup` 参数（全量备份模式）。
2. **Git 拉取**——从 `main` 分支拉取最新代码，并更新子模块。
3. **拉取后的语法验证与自动回滚**——在完成拉取操作后，Hermes会针对每次启动时`hermes`命令所调用的九个关键文件进行编译。如果其中有任何文件无法解析（例如存在异常的合并冲突标记，或文件被意外截断），Hermes会立即执行`git reset --hard <pre-pull-sha>`命令将安装状态回滚到拉取之前的版本，从而确保Shell环境仍能正常启动。待上游代码修复完成后，只需再次运行`hermes update`即可。

4. **依赖项安装**——通过执行`uv pip install -e ".[all]"`命令来获取新增或已变更的依赖项。

5. **配置文件迁移**——检测自当前版本之后新增的配置选项，并提示用户进行相应设置。

6. **桌面应用重建（分阶段替换机制）**——如果Hermes桌面应用是基于当前代码分支构建的，系统会对其重新编译，以使图形界面与最新代码保持一致。重建过程会先将新版本应用打包到`apps/desktop/release/`目录旁边的临时文件夹中，对打包后的应用进行验证，确认无误后才会将其替换为之前的版本。如果在任何环节出现错误——比如Electron下载失败、缺少依赖项或磁盘空间不足——系统都会保留原有的可用应用版本；此时更新过程会显示“⚠ 更新部分完成”，随后`hermes desktop`会自动重新尝试重建。
7. **网关自动重启** —— 更新完成后，正在运行的网关会立即刷新，从而使新代码立即生效。由服务管理的网关（Linux系统中的systemd，macOS系统中的launchd）会通过相应的服务管理器进行重启。而对于手动启动的网关，一旦Hermes能够将当前的进程ID重新映射到对应的配置文件中，它也会自动重新启动。同样地，手动运行的`hermes serve`/`hermes dashboard`后端（例如用于支持远程桌面的网络绑定服务）也会按照相同机制处理：每个后端在启动时都会将自己的绑定地址记录到安装过程中的进程生成日志中，因此更新会在代码替换之前暂停该后端的运行，之后会在**同一台主机和端口**上重新启动它——这样，指向该端点的远程桌面就能重新连接，而不会中断使用。那些由正在运行的桌面应用程序管理的后端，则由其应用程序自行负责重启。 

### 缺失的Windows更新文件

如果维护用的更新脚本丢失（例如因杀毒软件隔离所致），传统更新转发器将会失效，而不会报告成功移交的信号。在重新尝试之前，请先修复安装问题并查看杀毒软件的隔离报告，同时切勿关闭杀毒保护功能。在确认成功之前，维护用的更新工具会检查 CLI 导入内容、Windows 可执行文件头信息、ASAR 头信息以及打包后的主入口文件、包含本地模块条目的可读渲染器 HTML 文件、初始模块文件以及当前的构建时间戳。这些仅是最基本的文件检查，并非完整的依赖项审计或应用程序/后端启动测试。在等待桌面环境关闭之前，系统就会先检测到 Python 缺失的情况；不过更新过程中仍允许进行依赖项修复。当存在相应的布局结构时，Electron 会在停止后端服务之前检查所有必要的移交前提条件；由于仍然支持传统的 flat 更新器布局，因此并非所有缺失的更新文件都会在停止后端服务之前被检测到。

在 Windows 系统中，在打包过程中重新打开的桌面环境会在阶段化构建被提交之前立即被再次关闭。此清理操作仅限于该版本桌面发布目录中的可执行文件，与当前操作无关的其他安装程序则不会受到影响。如果仍存在锁定状态，阶段化构建将会失败，而无法绕过重命名错误。

### 基于非默认分支进行更新：`--branch`

默认情况下，`hermes update` 会跟踪 `origin/main` 分支。若需基于其他分支进行更新——例如在质量检测渠道、功能分支或候选版本测试中使用——可传递 `--branch <name>` 参数。

```bash
hermes update --branch release-candidate
hermes update --check --branch experimental   # preview behindness only
```

如果您的本地检出位于另一个分支上，Hermes会自动暂存所有未提交的更改，将HEAD切换到目标分支，随后执行拉取操作。对于本地不存在的分支，系统会自动从`origin/<名称>`中追踪该分支（可通过`git checkout -B <名称> origin/<名称>`实现）。而对于完全不存在于任何地方的分支，系统会确保流程干净利落地终止——在退出前会恢复您暂存的更改，避免您陷入异常状态。对于非`main`分支，系统会自动跳过仅针对`main`分支的同步逻辑。

### 检出位于功能分支上

如果源代码检出被留在了某个功能分支上（可能是由于工具设置、工作树实验或手动操作所致），只要工作树处于干净状态，`hermes update`就会自动将其切换回更新目标分支：

- **分支已完全合并**（所有提交均已包含在`origin/main`中——`git cherry`显示无未合并内容）：系统会明确提示“检出曾位于‘<分支>’（已完全合并）——现已切换回main”，之后会一直保持在`main`分支上。
- **分支存在未合并的提交，但工作树干净**：系统仍会切换到`main`分支以便继续更新——这是非交互式调用方式（如桌面端更新按钮、网关 `/update`、定时任务）所依赖的机制，因为这些方式无法处理跳过操作。您的提交内容不会被删除：`git checkout`绝不会丢弃已提交的更改，系统还会输出醒目的提示，说明所在分支及提交数量，并给出`git checkout <分支>`命令，方便您稍后继续处理这些工作。
如果您*有意*使用自定义分支（即在 main 分支基础上进行的本地修改），请在 `config.yaml` 中设置 `updates.parked_branch_strategy: update_in_place`。这样一来，更新操作会将 `origin/main` 的内容**合并到**您的分支中，而不会切换离开当前分支——检出路径保持不变，您的提交记录依然保留，同时运行代码也能得到更新。尽可能采用快进模式；一旦出现分支分歧，则会在 `pre-update-<stamp>` 安全标签后执行真正的合并操作，若发生冲突则会干净地停止（不会产生任何变化）。使用 `hermes update --switch-branch` 可临时恢复到切换模式，适用于那些不能积累由更新引发的合并提交的深层功能分支。

当该待处理分支存在**未提交的更改**（即脏树状态）时，Hermes 会**不对其进行任何操作**。此时代码更新会被标记为**已跳过**，并伴随醒目的警告信息，说明具体是哪个分支、它落后于 `origin/main` 多远，以及解决该问题的确切命令——而不会假装更新已成功完成。完成状态行总会显示实际的分支名和 HEAD 地址（如 `✓ Update complete! [main @ 30fcf9580]`），便于您一目了然地掌握分支偏移情况。若要完全禁用自动切换功能，请在 `config.yaml` 中设置 `updates.auto_switch_parked_branch: false`（此时仍会显示跳过警告）。

### 非交互式更新时的本地更改

当您在终端中运行 `hermes update` 时，Hermes 会先暂存所有未提交的源代码更改并拉取最新内容，随后**询问**您是否要恢复这些更改——这一操作方式与以往完全一致。对于交互式更新而言，则没有变化。

当在**无需终端**的情况下执行更新时——例如通过桌面端/聊天应用中的“更新”按钮，或是由网关触发的更新——系统不会提示用户进行确认。`updates.non_interactive_local_changes` 设置则决定了那些已暂存的用户修改内容将如何处理：

```yaml
# ~/.hermes/config.yaml
updates:
  non_interactive_local_changes: stash   # default: keep + auto-restore
  # non_interactive_local_changes: discard  # throw local source edits away
```

- `stash`（默认值）——自动将您的修改暂存，然后拉取最新代码，最后再自动恢复这些修改。这样不会丢失任何内容；如果恢复过程中出现冲突，这些冲突会被保存在 git 暂存区中，以便您手动处理。
- `discard`——在拉取代码后自动暂存修改，随后立即丢弃该暂存内容，从而确保更新后的代码库始终处于干净状态。仅建议在那些无需保留 Hermes 源代码本地修改的机器上使用此选项。该选项采用暂存后丢弃的方式（而非 `git reset --hard` + `git clean -fd`），因此不会触及 `node_modules`、`venv` 等被忽略的目录以及构建输出文件。

在桌面应用程序中，该设置位于 **设置 → 高级 → 应用内更新本地修改**。

**桌面端更新永远不会自动恢复本地修改。** 桌面端更新工具会调用 `hermes update --keep-stash` 命令：本地源代码的修改仍会被暂存以便继续进行更新，但之后**不会**被重新应用——它们会一直保留在 `git stash` 中，更新日志还会显示用于恢复这些修改的准确命令 `git stash apply <ref>`。这样就能避免本地修改在桌面端更新过程中被悄悄带入，进而破坏刚刚更新完成的程序。（如果您选择了“丢弃”选项，则 `non_interactive_local_changes: discard` 的设置仍会生效。）如需手动恢复这些暂存的修改：

```bash
cd ~/.hermes/hermes-agent   # or your install root
git stash list --format='%gd %H %s'   # find the hermes-update-autostash entry
git stash apply stash@{0}
```

如果您希望以交互方式实现“永不重新应用”的效果，也可以在终端中执行 `hermes update` 时加上 `--keep-stash` 参数。

### 仅预览功能：`hermes update --check`

想在拉取更新之前先确认是否有可用更新？请运行 `hermes update --check` —— 它会获取最新版本并与其在 `origin/main` 上的版本进行比对。此操作不会修改任何文件，也不会重启网关，非常适合用于那些需要根据“是否有更新”来决定是否执行的脚本和定时任务中。

### Fleet 预览功能：`hermes update --plan`

在更新运行有多个配置文件或服务的机器之前，`hermes update --plan` 会先输出完整的更新计划，而不会实际进行任何更改。该计划会显示安装方式（git 检出、Docker 镜像、Nix/apt 管理）、所有配置文件中正在运行的 Hermes 服务及其对应的监控进程（systemd、launchd 或手动启动），以及这些服务当前实际使用的代码版本，还会说明每个服务将采用的重启机制。此外，那些通过手动方式启动的 `hermes serve`/`hermes dashboard` 后端也会被列出（来自启动记录），并显示其绑定的端点地址，以及“在更换代码前先停止服务，然后使用记录的启动参数重新启动”的重启机制。对于通过镜像或包管理方式安装的系统，该计划会指出此类安装无法直接更新，并推荐相应的更新命令。在实时运行的 Fleet 环境中，此功能为只读模式，十分安全。

每次实际更新完成后，相关的更新记录都会保存在 `~/.hermes/logs/update_receipts/` 目录下，因此您可以通过对比更新器检测到的信息与实际执行的内容，了解更新的具体情况。

### 更新记录与 Fleet 版本检查

每次执行 `hermes update` 操作时，系统都会在 `~/.hermes/logs/update_receipts/` 目录中生成一份机器可读的记录文件（最多保留最近20份，`latest.json` 文件始终指向最新的记录）：其中包含更新前的集群配置、执行的每一步操作、被跳过的操作及其原因、网关重启的结果，以及最终的集群版本矩阵。在重启阶段结束后，更新工具会将每个正在运行的网关的当前代码与最新更新的代码进行比对，并输出针对每个配置文件的对比结果——那些仍在使用旧版代码的网关会以醒目的方式被标记出来，同时还会显示具体的重启命令，且更新过程将以非零状态退出，因此自动化系统绝不会将存在版本混用的集群视为正常状态。无论是通过 `--plan` 参数还是集群检查功能，都会在条件允许的情况下直接通过每个运行中的网关的本地控制套接字（即配置文件数据目录中的 `gateway.sock`，在 Windows 系统上为命名管道）向网关发起请求，从而获取其版本信息和监管程序信息；而旧版本的网关则仍会像以前一样通过其状态文件被识别出来。

### 被中断的网关重启操作

如果之前的更新已下载了代码但未能完成整个集群的重启，那么即使当前版本已是最新的，下一次执行 `hermes update` 时仍会尝试重新启动。空白的进程扫描结果并不能证明系统已恢复：失败的 systemd 单元以及已安装的 launchd 任务可能没有正在运行的 PID。如果监督进程发现失败、重启操作失败，或请求的服务无法被确认为处于运行状态，那么“待重启”标记将会保留。此时更新过程将以非零状态退出，并列出受影响的服务；请使用打印出的命令恢复这些服务，然后再尝试执行 `hermes update`。

历史接收记录失败本身并不能证明网关版本仍然过时。在根据仅基于接收记录的重启要求采取行动之前，系统会先检查当前实际运行的集群状态，同时还会发出关于启动过程和网关状态的警告，并进行更新补齐操作。每个已记录的网关配置都必须在当前版本中拥有一个正在运行的后续配置；一个无关的当前运行中的网关无法替代那些缺失、故障、版本未知或并非网关类型的运行时环境。因此，手动重启网关即可消除警告，而无需将失败的更新强行标记为成功。此外，独立的“待处理”标记依然具有权威性，因为它可能来自某个更新的、被中断的更新，其相关配置信息始终未能被成功接收。

### 完整的更新前备份：`--backup`

对于那些价值较高的配置（如生产环境网关、团队共享的安装环境），您可以选择对 `HERMES_HOME` 目录进行完整的更新前备份，内容包括配置文件、认证信息、会话数据、技能信息以及配对设置等：

```bash
hermes update --backup
```

或者将其设置为每次运行的默认值：

```yaml
# ~/.hermes/config.yaml
updates:
  pre_update_backup: full
```

`updates.pre_update_backup` 是一个具有三种模式的单一控制选项：`quick`（默认值——即上文所述的轻量级状态快照）、`full`（在快速快照的基础上再附加完整的 `HERMES_HOME` zip 文件；对于大型项目，此模式可能需要更多时间）以及 `off`（完全不进行更新前的备份——单次运行时使用 `--no-backup` 可达到相同效果）。传统的布尔值表示方式仍然有效：`true` 对应 `full`，`false` 对应 `off`。

:::提示：想要迁移到新机器上吗？
更新备份功能可用于保护原位更新过程。如果您打算将整个环境迁移到其他硬件上，建议使用 `hermes backup` 和 `hermes import` ——详情请参阅[将 Hermes 导出到另一台机器](/reference/faq#exporting-hermes-to-another-machine)以及[`hermes backup` 与 `hermes profile export` 的区别](/reference/faq#hermes-backup-vs-hermes-profile-export)。
:::

### Windows：有另一个 `hermes.exe` 正在运行
在 Windows 系统中，如果检测到有其他 `hermes.exe` 进程正在占用虚拟环境的入口点可执行文件，`hermes update` 将拒绝运行——这类进程通常包括 Hermes Desktop 应用生成的底层程序、其他终端中正在运行的 `hermes` REPL，或是正在运行的网关程序：

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

请关闭列出的进程后重新运行。如果您确定这些并发进程不会造成干扰（这种情况较为罕见，通常仅在杀毒程序错误识别文件时才有用），可传递 `--force` 参数以跳过检查。即便如此，更新工具仍会以指数退避策略尝试重命名 `.exe` 文件；而对于顽固的锁定情况，则会通过 `MoveFileEx(MOVEFILE_DELAY_UNTIL_REBOOT)` 将替换操作安排在下次重启时执行，从而确保更新能够完成。

另一项独立的保护机制会禁止在 Python 解释器（即桌面应用程序的后端、网关或 Python REPL）正在运行的任何进程存在时修改虚拟环境。这些进程会锁定原生扩展文件（`.pyd`），而如果在访问被拒的情况下依赖项同步过程中断，就会导致安装程序陷入版本混乱状态。此保护机制**不会**被 `--force` 参数绕过；如果您确定检测到的占用进程属于误报，可使用明确的命令 `hermes update --force-venv`。

#### Windows 虚拟环境的重建是事务性操作

当 Windows 安装程序需要重新创建现有的虚拟环境时，它会首先将旧目录重命名为唯一的 `venv.stale.*` 格式，然后再创建新的虚拟环境并对其进行验证。只有在依赖项安装完成且新环境中的基础导入测试通过后，旧目录才会被删除——在此之前，它仍会作为回滚源被保存在 `venv.pending-backup` 中。

如果迁移无法完成，安装程序将会停止运行，并保持现有的 `venv` 环境不受影响。若 `uv` 命令执行失败，或虽报告成功但未生成解释器，所有部分替换的文件将被移至 `venv.failed.*` 目录中，同时之前的虚拟环境将会被恢复。这样一来，即便安装失败，相关的健康状态检查与障碍检测功能依然可以正常使用。

当仍有其他进程持有文件句柄时，`venv.stale.*` 或 `venv.failed.*` 目录可能会残留。请先关闭 Hermes Desktop、相关网关以及用于安装的 Python 进程，然后再尝试进行安装或更新；在成功重建虚拟环境后，系统会尽力清理这些残留目录。

预期的输出如下所示：

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

虽然 `hermes update` 已能处理主要的更新流程，但进行快速验证可确保一切正常完成：

1. `git status --short` —— 若工作区状态异常，建议先检查问题再继续操作
2. `hermes doctor` —— 检查配置、依赖项及服务运行状态
3. `hermes --version` —— 确认版本号已如预期升级
4. 若使用了网关，则执行 `hermes gateway status`
5. 若 `doctor` 检测到 npm 安全审计问题，请在对应目录中运行 `npm audit fix`

:::warning 更新后工作区状态异常
如果执行 `hermes update` 后 `git status --short` 显示有意外变更，建议暂停并检查这些变更，然后再继续。这通常意味着本地修改内容被重新应用到了已更新的代码之上，或是某个依赖项更新过程刷新了锁文件。
:::

### 若在更新过程中终端断开连接

`hermes update` 具备防止终端意外中断的保护机制：

- 更新过程会忽略 `SIGHUP` 信号，因此关闭 SSH 连接或终端窗口不会导致更新过程中途终止。`pip` 和 `git` 子进程也享有此保护机制，从而避免因连接中断而导致 Python 环境处于半安装状态。
- 在更新执行期间，所有输出信息都会同步记录到 `~/.hermes/logs/update.log` 文件中。如果终端意外断开，重新连接后可通过查看该日志来判断更新是否已完成，以及网关重启是否成功：

```bash
tail -f ~/.hermes/logs/update.log
```

- `Ctrl-C`（SIGINT）信号及系统关机信号（SIGTERM）依然有效——这些都属于有意发起的取消操作，而非意外情况。

您无需再将 `hermes update` 嵌入 `screen` 或 `tmux` 中，即可避免因终端意外关闭而导致操作中断。

### 查看当前版本信息

```bash
hermes --version
```

请在 [GitHub 发布页面](https://github.com/NousResearch/hermes-agent/releases) 上查看与最新版本的对比情况。

### 通过消息平台进行更新

您也可以直接通过 Telegram、Discord、Slack、WhatsApp 或 Teams 发送指令来执行更新：

```
/update
```

该操作会拉取最新代码、更新依赖项，并重启正在运行的网关。在重启过程中，机器人将会短暂离线（通常为5至15秒），之后便会恢复运行。

### 手动更新

如果您是手动安装的（而非通过快速安装程序）：

```bash
cd /path/to/hermes-agent
# Activate the venv you created during install (outside the source tree)
export VIRTUAL_ENV="$HOME/.hermes/venvs/hermes-dev"
export PATH="$VIRTUAL_ENV/bin:$PATH"

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
如果新增了配置选项，回滚操作可能会导致配置不兼容。请在回滚后运行 `hermes config check`，若遇到错误，请从 `config.yaml` 中删除所有未被识别的选项。
:::

### 基于镜像的安装方式（Docker）：来源标记机制

已发布的 Docker 镜像会包含一个小型只读标记文件 `/etc/hermes/image-provenance.json`，用于明确标识该文件系统是由镜像管理的。在执行 `hermes update`、`hermes update --check` 操作或点击控制面板中的“更新”按钮之前，系统都会先读取该标记文件：对于基于镜像管理的安装环境，这些操作会直接拒绝执行（返回代码为 2），同时输出实际的更新命令（如 `docker pull nousresearch/hermes-agent:latest`），并生成一条“拒绝”记录，以便集群管理工具知晓该尝试已经发生。即便源代码是通过绑定挂载方式导入容器的，该标记机制依然有效——拒绝决策是基于当前运行中的文件系统实际状态，而非其表面形式。即使标记文件已损坏，系统仍会拒绝执行（采用失败即终止的策略）。基于 Nix 和 apt 的安装方式则通过现有的检测机制遵循相同的拒绝逻辑。

### 面向 Nix 用户的说明

Nix 已不再属于明确支持的安装路径（仅提供尽力支持），详情请参阅 [Nix 设置指南](./nix-setup.md)。如果您是通过 Nix flake 进行安装的，更新操作将通过 Nix 包管理器来处理：

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

---

## 卸载

```bash
hermes uninstall
```

卸载工具会为您提供一个选项，允许您保留配置文件（位于 `~/.hermes/` 目录中），以便日后重新安装时使用。

:::提示：不想删除现有设置，而是要更换机器？
在删除任何内容之前，请先备份您的设置：`hermes backup` 可以完整备份整个 `~/.hermes` 目录，包括凭证信息；而 `hermes profile export` 则仅导出单个配置文件，且按设计不会包含凭证信息（因此单独使用该命令并不构成完整备份）。详情请参阅 [`hermes backup` 与 `hermes profile export` 的区别](/reference/faq#hermes-backup-vs-hermes-profile-export)。
:::

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
