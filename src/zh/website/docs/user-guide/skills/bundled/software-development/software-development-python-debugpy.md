---
title: "Python Debugpy — Debug Python: pdb REPL + debugpy remote (DAP)"
sidebar_label: "Python Debugpy"
description: "Debug Python: pdb REPL + debugpy remote (DAP)"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Python Debugpy

调试 Python：pdb REPL + debugpy 远程调试（DAP）。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/software-development/python-debugpy` |
| 版本 | `1.0.0` |
| 创建者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos |
| 标签 | `调试`, `python`, `pdb`, `debugpy`, `断点`, `dap`, `事后分析` |
| 相关技能 | [`系统化调试`](/docs/user-guide/skills/bundled/software-development/software-development-systematic-debugging), [`node-inspect-debugger`](/docs/user-guide/skills/bundled/software-development/software-development-node-inspect-debugger), `debugging-hermes-tui-commands` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 加载的完整技能定义。技能处于激活状态时，Agent 会看到这些指令作为操作指南。
:::

# Python 调试工具（pdb + debugpy）

## 概述

根据不同场景选择三种工具：

| 工具 | 适用场景 |
|---|---|
| **`breakpoint()` + pdb** | 本地使用，交互式，最简单。在源代码中添加 `breakpoint()`，正常运行后会在对应行进入 REPL 环境。 |
| **`python -m pdb`** | 不修改源代码即可将现有脚本在 pdb 环境下运行，适合快速测试。 |
| **`debugpy`** | 用于远程/无界面调试，或“附加到已运行的进程”进行调试。支持 DAP 协议，可通过终端编写脚本，适用于长时间运行的进程（如网关、守护进程、PTY 子进程）。 |

**建议从 `breakpoint()` 开始使用**，这是最简单且有效的方案。

## 使用场景

- 测试失败但堆栈跟踪信息无法说明变量值出错的原因
- 需要逐行执行函数并观察数据集合的变化
- 长时间运行的进程（如 hermes gateway、tui_gateway）出现异常且无法重启
- 事后分析：在类似生产环境的代码中发生异常，需要查看崩溃时的局部变量
- 实际故障发生在子进程/子任务中（如 Python `_SlashWorker`、PTY 桥接工作进程）

**不推荐用于**：那些通过 `print()` / `logging.debug` 即可在一分钟内解决的问题，或 `pytest -vv --tb=long --showlocals` 已能显示信息的场景。

## pdb 快速参考

在任何 pdb 提示符（`(Pdb)`）下：

| 命令 | 功能 |
|---|---|
| `h` / `h cmd` | 显示帮助信息 |
| `n` | 下一行（跳过当前行） |
| `s` | 进入函数内部 |
| `r` | 从当前函数返回 |
| `c` | 继续执行 |
| `unt N` | 继续执行直到第 N 行 |
| `j N` | 跳转到第 N 行（仅限同一函数内） |
| `l` / `ll` | 查看当前行周围的源代码/整个函数的代码内容 |
| `w` | 显示堆栈跟踪信息 |
| `u` / `d` | 在堆栈中向上/向下移动 |
| `a` | 打印当前函数的参数 |
| `p expr` / `pp expr` | 打印/格式化打印表达式 |
| `display expr` | 每次暂停时自动打印表达式值 |
| `b file:line` | 设置断点 |
| `b func` | 在函数入口处设置断点 |
| `b file:line, cond` | 条件断点 |
| `cl N` | 删除第 N 个断点 |
| `tbreak file:line` | 一次性断点 |
| `!stmt` | 执行任意 Python 代码（包括赋值语句） |
| `interact` | 进入当前作用域下的完整 Python REPL 环境（按 Ctrl+D 退出） |
| `q` | 退出 |

`interact` 命令功能最为强大——你可以导入任何模块，检查复杂对象，甚至调用会修改状态的方法。默认情况下局部变量为只读状态；若需修改变量，可在 `(Pdb)` 提示符下使用 `!x = 42` 的命令。

## 方法一：本地断点

最简单的方式。直接编辑对应文件即可：

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # <-- drops into pdb here
    return result + y
```

正常运行代码即可。程序会执行到 `breakpoint()` 这一行，此时你可以完整访问所有局部变量。

**在提交代码之前别忘了删除 `breakpoint()` 语句。** 可以使用 `git diff` 或预提交检查工具 grep 来完成此项操作：
```bash
rg -n 'breakpoint\(\)' --type py
```

## 方案 2：在 pdb 环境下运行脚本（无需修改源代码）

```bash
python -m pdb path/to/script.py arg1 arg2
# Lands at first line of script
(Pdb) b path/to/script.py:42
(Pdb) c
```

## 方案 3：调试 pytest 测试

Hermes 测试运行器和 pytest 均支持此功能：

```bash
# Drop to pdb on failure (or on any raised exception):
scripts/run_tests.sh tests/path/to/test_file.py::test_name --pdb

# Drop to pdb at the START of the test:
scripts/run_tests.sh tests/path/to/test_file.py::test_name --trace

# Show locals in tracebacks without pdb:
scripts/run_tests.sh tests/path/to/test_file.py --showlocals --tb=long
```

注意：`scripts/run_tests.sh` 默认会使用 xdist（参数为 `-n 4`），而 pdb 在 xdist 环境下无法正常运行。请添加 `-p no:xdist` 参数，或使用 `-n 0` 参数来单独运行某项测试。

```bash
scripts/run_tests.sh tests/foo_test.py::test_bar --pdb -p no:xdist
# or
source .venv/bin/activate
python -m pytest tests/foo_test.py::test_bar --pdb
```

此方式会绕过 hermetic-env 所提供的各种保障机制——虽便于调试，但在推送代码之前，仍需在封装层下重新运行以进行确认。

## 方案 4：对任何异常进行事后分析

```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

或者将整个脚本封装起来：

```bash
python -m pdb -c continue script.py
# When it crashes, pdb catches it and you're in the frame of the exception
```

或者可在 REPL/Jupyter 中设置全局钩子：

```python
import sys
def excepthook(etype, value, tb):
    import pdb; pdb.post_mortem(tb)
sys.excepthook = excepthook
```

## 方案 5：使用 debugpy 进行远程调试（附加到正在运行的进程）

适用于长时间运行的进程：Hermes gateway、tui_gateway、守护进程，以及那些已出现异常且无法正常重启的进程。

### 设置步骤

```bash
source /home/bb/hermes-agent/.venv/bin/activate
pip install debugpy
```

### 模式A：源码编辑——进程在启动时等待调试器

在入口点附近（或您希望调试的函数内部）添加如下代码：

```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
print("debugpy listening on 5678, waiting for client...", flush=True)
debugpy.wait_for_client()
debugpy.breakpoint()       # optional: pause immediately once attached
```

启动该流程，它会停留在 `wait_for_client()` 步骤处无法继续。

### 方案 B：无需修改源代码——使用 `-m debugpy` 参数启动

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py arg1
```

模块入口的等效配置：

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m your.module
```

### 模式 C：附加到正在运行的进程

要求目标环境的系统中已预装 PID 及 debugpy：

```bash
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
# debugpy injects itself into the process. Then attach a client as below.
```

某些内核或安全配置会阻止基于 ptrace 的注入功能（即 `/proc/sys/kernel/yama/ptrace_scope` 设置）。可通过以下方式解决该问题：
```bash
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

### 通过终端连接客户端

最简单的终端端 DAP 客户端是 VS Code CLI 或简单的脚本。在 Hermes 内部，您有两种实用的选择：

**选项 1：`debugpy` 自带的 CLI REPL**——虽非官方功能，但也是一个小巧的 DAP 客户端脚本：

```python
# /tmp/dap_client.py
import socket, json, itertools, time, sys

HOST, PORT = "127.0.0.1", 5678
s = socket.create_connection((HOST, PORT))
seq = itertools.count(1)

def send(msg):
    msg["seq"] = next(seq)
    body = json.dumps(msg).encode()
    s.sendall(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)

def recv():
    header = b""
    while b"\r\n\r\n" not in header:
        header += s.recv(1)
    length = int(header.decode().split("Content-Length:")[1].split("\r\n")[0].strip())
    body = b""
    while len(body) < length:
        body += s.recv(length - len(body))
    return json.loads(body)

send({"type": "request", "command": "initialize", "arguments": {"adapterID": "python"}})
print(recv())
send({"type": "request", "command": "attach", "arguments": {}})
print(recv())
send({"type": "request", "command": "setBreakpoints",
      "arguments": {"source": {"path": sys.argv[1]},
                    "breakpoints": [{"line": int(sys.argv[2])}]}})
print(recv())
send({"type": "request", "command": "configurationDone"})
# ... loop reading events and sending continue/stepIn/etc.
```

这种方式适用于一次性自动化任务，但作为交互式用户体验而言却十分糟糕。

**选项 2：从 VS Code / Cursor / Zed 中附加**——如果用户已打开这些工具，他们可以添加一个 `launch.json` 文件：

```json
{
  "name": "Attach to Hermes",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "127.0.0.1", "port": 5678 },
  "justMyCode": false,
  "pathMappings": [
    { "localRoot": "${workspaceFolder}", "remoteRoot": "/home/bb/hermes-agent" }
  ]
}
```

**选项 3：放弃 DAP，改用 `remote-pdb`**——这通常正是终端型智能体所能满足您的需求：

```bash
pip install remote-pdb
```

在您的代码中：
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)   # blocks until connection
```

接着在终端中执行：
```bash
nc 127.0.0.1 4444
# You get a (Pdb) prompt exactly as if debugging locally.
```

当 `debugpy` 的 DAP 协议功能过于强大时，`remote-pdb` 是最简洁且对 Agent 友好的选择。只有在实际需要与 IDE 集成时才使用 `debugpy`。

## 调试 Hermes 特有进程

### 测试
请参考方案 3。务必添加 `-p no:xdist` 参数，或直接运行无需 xdist 的单个测试。

### `run_agent.py` / CLI —— 单次执行
最简单的方法：在疑似出问题的代码行附近调用 `breakpoint()`，然后正常运行 `hermes`。程序会在暂停点返回到终端控制台。

### `tui_gateway` 子进程（由 `hermes --tui` 启动）
该网关作为 Node TUI 的子进程运行。可选配置如下：

**A. 直接在源代码中编辑网关：**
```python
# tui_gateway/server.py near the top of serve()
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()
```
启动 `hermes --tui` 命令。此时图形用户界面会显得处于冻结状态（其后台正在等待中）。连接一个客户端后，输入 `continue` 即可恢复执行。

**B. 在特定处理器上使用 `remote-pdb`：**
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)   # in the RPC handler you want to trap
```
首先通过 TUI 触发对应的斜杠命令，然后在另一个终端中执行 `nc 127.0.0.1 4444`。

### `_SlashWorker` 子进程
其工作原理相同——在 worker 的 `exec` 路径中使用 `remote-pdb` 并结合 `set_trace()`。该 worker 在多个斜杠命令之间会保持状态，因此首次触发时会阻塞直到用户建立连接；之后的斜杠命令会正常执行，除非你再次手动启动它。

### 网关（`gateway/run.py`）
该组件为长期运行的进程。可在处理程序中使用 `remote-pdb`，或者如果在重启网关的话，则可使用带有 `--wait-for-client` 参数的 `debugpy`。

## 常见问题

1. **在 pytest-xdist 环境下，pdb 会静默无响应。**你不会看到提示符，测试进程只会挂起。务必使用 `-p no:xdist` 或 `-n 0` 参数。

2. **在 CI 环境或非 TTY 环境中调用 `breakpoint()` 会导致进程挂起。**该功能在本地是安全的，切勿将其提交到代码仓库。可添加预提交检查（grep）作为安全保障。

3. **设置 `PYTHONBREAKPOINT=0`** 可禁用所有 `breakpoint()` 调用。如果断点无法触发，请检查当前环境变量。
   ```bash
   echo $PYTHONBREAKPOINT
   ```

4. **只有同时调用 `wait_for_client()` 时，`debugpy.listen` 才会阻塞执行。** 若不调用该函数，程序将继续运行，从而导致在客户端连接之前就触发第一个断点。

5. **在强化安全的内核上无法通过 PID 进行调试。** Ubuntu 的默认设置 `ptrace_scope=1` 仅允许对同一用户的子进程进行 ptrace 操作。解决方法：执行 `echo 0 > /proc/sys/kernel/yama/ptrace_scope`（需 root 权限），或从一开始就在 `debugpy` 环境下启动程序。

6. **线程问题。** `pdb` 仅能调试当前线程。对于多线程代码，应使用支持线程的调试工具 `debugpy`，或为每个线程分别调用 `threading.settrace()`。

7. **asyncio 模式。** `pdb` 可以在协程中工作，但在 `pdb` 内部使用 `await` 需要 Python 3.13 及以上版本；在较低版本中，则需通过 `interact` 模式来实现 `await` 功能。对于 Python 3.11/3.12 版本，可利用 `asyncio.run_coroutine_threadsafe` 方法，或通过 `asyncio.ensure_future` 结合 `!stmt` 语句来实现 `await`。

8. **`scripts/run_tests.sh` 会移除敏感凭证，并将 `HOME` 环境变量设置为 `<tmpdir>`。** 如果你的故障与用户配置或真实的 API 密钥有关，那么在该脚本封装的环境下将无法复现问题。建议先使用原始的 `pytest` 工具进行调试以复现问题，然后再在该脚本环境下进行确认。

9. **进程分叉/多进程场景。** `pdb` 无法跟踪进程分叉后的子进程，因此每个子进程都需要单独设置 `breakpoint()` 或 `set_trace()`。对于 Hermes 子代理，需逐个进程进行调试。

## 验证清单

- [ ] 安装 `debugpy` 后，请确认版本信息：`python -c "import debugpy; print(debugpy.__version__)"`
- [ ] 对于远程调试，需确认目标端口确实在监听中：`ss -tlnp | grep 5678`
- [ ] 确认第一个断点能够正常触发（若无法触发，可能是由于设置了 `PYTHONBREAKPOINT=0`、正在使用 xdist 工具，或程序在连接之前就已执行完毕）
- [ ] `where` / `w` 命令显示的调用栈与预期一致
- [ ] 调试完成后进行清理，确保最终提交的代码中不存在多余的 `breakpoint()` / `set_trace()` 语句
  ```bash
  rg -n 'breakpoint\(\)|set_trace\(|debugpy\.listen' --type py
  ```

## 单次任务配方

**“为什么这个字典缺少某个键？”**
```python
# add above the KeyError site
breakpoint()
# then in pdb:
(Pdb) pp d
(Pdb) pp list(d.keys())
(Pdb) w                # how did we get here
```

“该测试单独运行时能够通过，但在测试套件中却会失败。”
```bash
scripts/run_tests.sh tests/the_test.py --pdb -p no:xdist
# But if it only fails WITH other tests:
source .venv/bin/activate
python -m pytest tests/ -x --pdb -p no:xdist
# Now it pdb-traps at the exact failing test after state accumulated.
```

**“我的异步处理程序出现了死锁。”**
```python
# Add at handler entry
import remote_pdb; remote_pdb.set_trace(host="127.0.0.1", port=4444)
```
触发处理程序。首先执行 `nc 127.0.0.1 4444`，接着使用 `w` 命令查看被挂起的帧；若要了解还有哪些任务处于待处理状态，则可运行 `!import asyncio; asyncio.all_tasks()`。

**“对 Ink 子进程/子任务发生崩溃后的故障分析。”**
```bash
PYTHONFAULTHANDLER=1 python -m pdb -c continue path/to/entrypoint.py
# On crash, pdb lands at the frame of the exception with full locals
```
