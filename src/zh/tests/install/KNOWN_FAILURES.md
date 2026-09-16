# 已确认的历史升级限制

此类故障无法通过更改更新目标来修复：出问题的代码早已从初始版本中被加载。工作流仍会沿用原有的每个更新路径执行。只有当起始提交、方法组合、失败的断言以及日志签名完全匹配时，才会生成非红色的“已知故障”记录；其他错误依然会导致失败。结果表中，匹配的案例会显示为 `known [n]`，详细说明和证据则放在底部的脚注中。这些案例不会计入成功的升级次数。

`e2e-assets/known-failures.json` 文件中的机器可读规则负责故障匹配并生成脚注文本。本文档介绍了这些规则的历史依据。由于每次尝试前都会轮换日志，因此先前的故障无法被用来判定后续的故障。

## Windows启动器自锁问题

分类：**在当前已发布的 `hermes.exe update` 路径的更新目标中无法修复**。

| 初始版本 | 发布提交哈希 | 安装 → 更新 | 已验证的失败任务 |
|---|---|---|---|
| `v2026.3.12` | `a370ab8391ca5f8de7ebbc449f05cb0df36ade7c` | `installer-script` → `hermes-update` | [101514756800](https://github.com/ethernet8023/hermes-agent/actions/runs/34043635705/job/101514756800) |
| `v2026.4.8` | `86960cdbb0148145890e2ee90b4e157fa899f6e1` | `installer-script` → `hermes-update` | [101514755527](https://github.com/ethernet8023/hermes-agent/actions/runs/34043635705/job/101514755527) |
正在运行的控制台启动器会保持 `venv/Scripts/hermes.exe` 处于打开状态。旧版更新工具会先下载新的版本，然后在可编辑安装过程中请求 uv 替换该可执行文件。但 Windows 系统会以“访问被拒绝。（操作系统错误 5）”的提示拒绝此次替换。旧版更新工具的 ZIP 备用方案虽会重新安装依赖项，却仍会遇到同样的锁定问题。

判定依据包括：CLI 更新阶段失败；错误堆栈信息指向正在运行的 `hermes.exe/__main__.py` 文件；以及 uv 报告称因操作系统错误 5 无法移除该版本下的 `Scripts/hermes.exe` 文件。若为其他文件出现的普通访问被拒绝错误，则不符合判定标准。

3 月版本的对应代码位于已发布的 `hermes_cli/main.py:1678-1683`，而 ZIP 备用方案的代码则在 `1571-1576`。4 月版本使用了 `_install_python_dependencies_with_optional_fallback` 函数，其已发布的实现代码位于 `3295-3321`，该函数可在无需启动器隔离的情况下执行安装操作。这些函数对象是在版本下载完成之前就被加载的。5 月版本的 CLI 更新测试通过，因此不应根据此记录将其归类为问题版本。

重新运行安装程序属于另一条经过测试的升级路径。通过 venv 环境中的 Python 调用旧版 CLI 也是一种可能的恢复方式，但并不能替代控制台启动器路径下的安装流程。

## 7 月版本的 Windows 应用仅支持手动更新脚本安装

分类结果：**在对应已发布应用按钮路径的更新目标中无法修复**。

起始版本：`v2026.7.1`，提交哈希值 `7c1a029553d87c43ecff8a3821336bc95872213b`。

| 安装 → 更新 | 已验证的失败任务 |
|---|---|
| `installer-script` → `hermes-desktop-app-update` | [101514755236](https://github.com/ethernet8023/hermes-agent/actions/runs/34043635705/job/101514755236) |
| `installer-script+desktop` → `hermes-desktop-app-update` | [101514760893](https://github.com/ethernet8023/hermes-agent/actions/runs/34043635705/job/101514760893) |
| `installer-script+desktop` → `open-app-update` | [101514756508](https://github.com/ethernet8023/hermes-agent/actions/runs/34043635705/job/101514756508) |

这些脚本安装版本并未使用分阶段更新机制。已发布的 Electron 代码（`apps/desktop/electron/main.cjs:2212-2214`）会输出“no staged updater; surfacing manual”信息，并返回 `{ ok: true, manual: true, command }`，而不会启动更新流程。每个任务的 `logs/desktop.log` 中都会记录该分支信息，随后出现 `[updates] manual: hermes update` 的提示，但不会出现目标代码检出或更新完成的信号。

所需证据：来自该已发布版本的 app-update 相关代码，以及上述明确显示手动更新过程的日志记录。若未出现手动更新提示却出现了任务超时情况，则不属于此限制范畴。桌面版安装程序采用不同的分阶段更新路径，因此不在本分类范围内。

## 未被判定为无法修复

7月出现的桌面版安装程序→应用更新失败问题，实际上是由驱动程序的生命周期缺陷导致的，并非已发布更新版本中的异常情况。该驱动程序将本应正常的页面关闭操作误判为故障，因此在Playwright完成启动流程之前便提前退出了。在Windows系统中，继承管道机制甚至会在启动流程以代码0成功退出后，依然延迟触发`close`事件。随后Playwright会执行其树形终止清理操作。现在的驱动程序已能够独立于正在关闭的页面进行等待，在进程退出后会释放对应的管道句柄，并在收到`close`信号后才最终退出。[7月的实际修复过程](https://github.com/ethernet8023/hermes-agent/actions/runs/34075042380/job/101599434616)已成功应用到目标版本，清除了更新标记，通过了CLI检查，随后重新启动了应用程序。

至于应用启动时的点击失败、缩放偏差、系统级权限对话框问题、AutoHotkey窗口等待故障、过期的更新标记、自动存储冲突、网络连接问题以及各类超时错误，在得到诊断之前仍属于待处理状态或未分类状态。这些问题不应因发生在旧版本上就被赋予历史标签。
