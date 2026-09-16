# Windows 系统特有的问题

Hermes 可以在 Windows 系统上直接运行（支持 PowerShell、cmd、Windows Terminal、git-bash、mintty 以及 VS Code 的集成终端）。大部分功能都能正常使用，但由于 Win32 与 POSIX 系统之间存在一些差异，我们遇到了一些问题——请在发现新问题时在此处记录下来，这样后续的使用者或新会话就能避免重复摸索。

### 输入 / 键绑定

**Alt+Enter 不会插入换行符**——Windows Terminal（以及 mintty）会在 prompt_toolkit 检测到该按键之前就将其用于全屏模式。建议改用 **Ctrl+Enter**（在 Windows 上，CLI 将其映射为换行操作；直接使用 Ctrl+J 也能达到相同效果且不会造成问题）。若想查看终端如何处理按键输入，可从项目根目录运行 `python scripts/keystroke_diagnostic.py` 脚本。

### 配置 / 文件

**首次运行时出现 HTTP 400 “未提供模型”错误**——这是因为 `config.yaml` 文件是以带有 UTF-8 BOM 格式保存的（Notepad 编辑器会生成此类格式）。请将其重新保存为不含 BOM 的 UTF-8 格式；使用 `hermes config edit` 命令即可正确写入配置。

### `execute_code` / 沙箱环境

**沙箱子进程会抛出 WinError 10106 错误**——原因是该进程无法创建 `AF_INET` 类型的套接字。根本原因通常是 Hermes 的环境清理机制移除了 `SYSTEMROOT`、`WINDIR` 和 `COMSPEC` 环境变量（Python 的 `socket` 模块需要 `SYSTEMROOT` 变量来定位 `mswsock.dll` 文件），而非 Winsock LSP 存在故障。《tools/code_execution_env.py` 文件中的 `_WINDOWS_ESSENTIAL_ENV_VARS` 允许列表已解决了该问题；如果仍然遇到此错误，可在 `execute_code` 代码块中输入 `echo os.environ`，以确认 `SYSTEMROOT` 变量是否已被正确设置。

### 在 Windows 上进行测试

`scripts/run_tests.sh` 仅兼容 POSIX 环境（需要先执行 `.venv/bin/activate`）；而 Hermes 安装的 `venv/Scripts/` 目录中未包含 pip/pytest 工具（为控制体积大小而刻意移除）。建议将 pytest 安装到系统 Python 环境中后直接运行（该仓库已不再使用 pytest-xdist；默认的运行器能够实现逐文件子进程隔离功能，这一功能也可由仅支持 POSIX 的脚本封装实现）。

```bash
"/c/Program Files/Python311/python" -m pip install --user pytest pyyaml
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/foo/test_bar.py -v --tb=short
```

（仅针对 POSIX 环境的测试需要添加跳过机制——相关跨平台保护规则请参见 `references/contributor-guide.md` 中的列表。）

### 路径 / 文件系统

**行尾格式。** Git 可能会发出“LF 将被替换为 CRLF”的警告，但这只是视觉上的差异，因为仓库中的 `.gitattributes` 文件会自动进行标准化处理。请勿让编辑器将已提交的、使用 POSIX 行尾格式的文件自动转换为 CRLF 格式。

**正斜杠在几乎所有地方都适用。** 所有的 Hermes 工具以及大多数 Windows API 都支持 `C:/Users/...` 这种路径格式。在代码和日志中建议使用正斜杠，这样可以避免在 bash 中出现需要转义的反斜杠。

