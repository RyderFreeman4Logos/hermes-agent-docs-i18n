# Windows 系统特有的问题

Hermes 可在 Windows 系统上直接运行（支持 PowerShell、cmd、Windows Terminal、git-bash、mintty 以及 VS Code 的集成终端）。大多数功能都能正常使用，但由于 Win32 与 POSIX 系统之间存在一些差异，导致了一些问题——请在遇到新问题时在此处记录下来，这样后续的使用者或同一会话中的其他人就不必重复摸索了。

### 输入 / 键绑定

**Alt+Enter 不会插入换行符**——Windows Terminal（以及 mintty）会在 prompt_toolkit 检测到该按键之前将其用于全屏模式。请改用 **Ctrl+Enter**（在 Windows 上，CLI 将其映射为换行操作；直接使用 Ctrl+J 也会产生相同效果，且不会造成任何问题）。若想查看终端如何处理按键输入，可从项目根目录运行 `python scripts/keystroke_diagnostic.py`。

### 配置 / 文件

**首次运行时会出现 HTTP 400 “未提供模型”错误**——这是因为 `config.yaml` 文件是以包含 UTF-8 BOM 格式保存的（Notepad 编辑器会生成此类格式）。请将其重新保存为不含 BOM 的 UTF-8 格式；使用 `hermes config edit` 命令即可正确保存配置。

### `execute_code` / 沙箱环境

**沙箱子进程会抛出 WinError 10106 错误**——原因是该进程无法创建 `AF_INET` 类型的套接字。根本原因通常是 Hermes 的环境清理机制移除了 `SYSTEMROOT`/`WINDIR`/`COMSPEC` 等路径（Python 的 `socket` 模块需要这些路径才能找到 `mswsock.dll` 文件），而非 Winsock LSP 存在故障。《tools/code_execution_tool.py` 文件中的 `_WINDOWS_ESSENTIAL_ENV_VARS` 允许列表可解决此问题；如果仍然出现该错误，可在 `execute_code` 代码块中输出 `os.environ` 的内容，以确认 `SYSTEMROOT` 变量是否已正确设置。

### 在 Windows 上进行测试

`scripts/run_tests.sh` 脚本仅适用于 POSIX 系统（要求先运行 `.venv/bin/activate` 命令）；Hermes 安装后的 `venv/Scripts/` 目录中未包含 pip/pytest 工具（为控制体积大小而省略）。建议在系统级的 Python 环境中安装 pytest，然后直接使用 `-n 0` 参数运行测试（`pyproject.toml` 文件中的 `addopts` 配置已自动设置了该参数）。

```bash
"/c/Program Files/Python311/python" -m pip install --user pytest pytest-xdist pyyaml
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/foo/test_bar.py -v --tb=short -n 0
```

（仅适用于 POSIX 环境的测试需要添加跳过保护机制——具体信息请参见 `references/contributor-guide.md` 中的跨平台保护列表。）

### 路径 / 文件系统

**行尾格式。** Git 可能会提示“LF 将被替换为 CRLF”。这只是外观上的差异，因为仓库中的 `.gitattributes` 文件会对此进行标准化处理。请勿让编辑器自动将已提交的采用 POSIX 行尾格式的文件转换为 CRLF 格式。

**正斜杠在几乎所有地方都适用。** 所有的 Hermes 工具以及大多数 Windows API 都支持 `C:/Users/...` 这种路径格式。在代码和日志中建议使用正斜杠，这样可以避免在 bash 中出现需要转义的反斜杠。

