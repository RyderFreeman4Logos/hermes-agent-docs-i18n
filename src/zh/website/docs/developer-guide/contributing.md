---
sidebar_position: 4
title: "Contributing"
description: "How to contribute to Hermes Agent — dev setup, code style, PR process"
---

# 贡献指南

感谢您为 Hermes Agent 做出贡献！本指南将为您介绍如何搭建开发环境、理解代码库以及如何让您的 Pull Request 被合并。

## 贡献优先级

我们按照以下顺序重视各类贡献：

1. **错误修复** — 程序崩溃、异常行为、数据丢失问题
2. **跨平台兼容性** — macOS、不同 Linux 发行版及 WSL2 环境
3. **安全性强化** — 命令注入、提示符注入、路径遍历漏洞防护
4. **性能与稳定性** — 重试逻辑、错误处理机制以及优雅降级功能
5. **新技能开发** — 具有广泛实用价值的技能（详见 [创建技能](creating-skills.md)）
6. **新工具开发** — 这类需求较为少见，大多数功能应通过技能实现
7. **文档完善** — 错误修正、内容澄清以及新增示例

## 常见的贡献路径

- 若想构建自定义或本地工具且无需修改 Hermes 核心代码？请从 [构建 Hermes 插件](../guides/build-a-hermes-plugin.md) 开始
- 若想为 Hermes 本身开发新的内置核心工具？请从 [添加工具](./adding-tools.md) 开始
- 若想开发新技能？请从 [创建技能](./creating-skills.md) 开始
- 若想开发新的推理提供程序？请从 [添加提供程序](./adding-providers.md) 开始

## 开发环境搭建

### 先决条件

| 要求项 | 备注 |
|---------|------|
| **Git** | 需安装 `git-lfs` 扩展 |
| **Python 3.11+** | 若未安装，uv 工具会自动帮您安装 |
| **uv** | 快速的 Python 包管理工具（[安装指南](https://docs.astral.sh/uv/)） |
| **Node.js 20+** | 非必需——仅用于浏览器工具和 WhatsApp 桥接功能（需与根目录下的 `package.json` 中指定的版本匹配） |

### 使用标准安装程序进行安装

对于大多数贡献者而言，最便捷的开发环境搭建方式与普通用户相同：运行标准安装程序，然后在克隆的代码仓库中进行开发。该安装程序会创建 Hermes 虚拟环境，配置 `hermes` 命令入口，标记 `hermes update` 的安装方式，并将完整的 Git 项目克隆到 `$HERMES_HOME/hermes-agent` 目录中（通常为 `~/.hermes/hermes-agent`）。这样就能确保您的开发环境结构与 CLI 工具、更新程序、懒加载依赖安装器、网关以及文档所预设的格式保持一致。

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
cd "${HERMES_HOME:-$HOME/.hermes}/hermes-agent"

# Add dev/test extras on top of the standard install.
uv pip install -e ".[all,dev]"

# Optional: browser tools / docs site dependencies.
npm install
```

之后，创建分支，并在该分支上运行测试：

```bash
git checkout -b fix/description
scripts/run_tests.sh
```

### 手动克隆作为备用方案

仅当您明确不想使用 Hermes 的托管安装结构时才应采用此方式（例如在容器或 CI 任务中使用的临时克隆目录）。若选择这种方式安装，请务必从该虚拟环境运行 `hermes` 入口程序；直接使用系统命令 `python3 -m hermes_cli.main` 可能会引入与当前项目无关的系统级 Python 包。

请在**已克隆的源代码目录之外**创建虚拟环境。如果虚拟环境位于代理程序运行的目录内，代理程序可能会对其自身下载的代码执行相对路径指令（如 `rm -rf venv`、`uv venv venv` 等），从而直接删除该虚拟环境，导致正在运行的进程在会话中途意外终止。将虚拟环境置于源代码目录之外，可避免工作区中的任何相对路径指向它。

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# Create venv with Python 3.11, OUTSIDE the source tree
uv venv ~/.hermes/venvs/hermes-dev --python 3.11
export VIRTUAL_ENV="$HOME/.hermes/venvs/hermes-dev"
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Install with all extras (messaging, cron, CLI menus, dev tools)
uv pip install -e ".[all,dev]"

# Optional: browser tools
npm install
```

### 开发环境配置

```bash
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# Add at minimum an LLM provider key:
echo 'OPENROUTER_API_KEY=sk-or-v1-your-key' >> ~/.hermes/.env
```

### 运行

```bash
# The standard installer already put `hermes` on PATH.
hermes doctor
hermes chat -q "Hello"
```

如果您使用了手动克隆的备用方案，请从代码检出目录运行 `./hermes`，或明确地创建该克隆版本的虚拟环境链接：

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
```

### 运行测试

```bash
scripts/run_tests.sh
```

## 代码风格

- 遵循 **PEP 8** 规范，但允许适当例外（不强制限制行长度）
- **注释**：仅用于解释那些不直观的设计意图、权衡方案或 API 的特殊行为
- **错误处理**：捕获具体的异常。对于意外错误，使用 `logger.warning()`/`logger.error()` 并设置 `exc_info=True` 以记录异常详细信息
- **跨平台兼容性**：切勿假设代码仅在 Unix 系统上运行（详见下文）
- **配置文件安全路径**：绝不要硬编码 `~/.hermes` 路径。在编写代码时，请使用 `hermes_constants` 模块中的 `get_hermes_home()` 函数获取路径，而在向用户显示信息时则使用 `display_hermes_home()` 函数。完整规则请参阅 [AGENTS.md](https://github.com/NousResearch/hermes-agent/blob/main/AGENTS.md#profiles-multi-instance-support) 文档。

## 跨平台兼容性

详情请参见 **[平台支持](../getting-started/platform-support.md)**。在原生 Windows 环境下，Shell 命令需通过 [Git for Windows](https://git-scm.com/download/win) 提供的 Git Bash 来执行。部分功能依赖于 POSIX 内核接口，因此仅在特定平台上可用：例如，控制面板中的嵌入式 PTY 终端面板（位于 `/chat` 标签页）需要 POSIX PTY 环境（Linux、macOS 或 WSL2）。如果主要在 Windows 上进行开发，建议在提交代码前运行 Windows 版的代码检查工具 `scripts/check-windows-footguns.py`。

在贡献代码时，请牢记以下规则：

- **避免使用未经处理的 `signal.SIGKILL` 引用**。该信号在 Windows 上并不存在。应通过 `gateway.status.terminate_pid(pid, force=True)` 方法来处理（该函数会在 Windows 上执行 `taskkill /T /F` 指令，在 POSIX 系统上则发送 SIGKILL 信号），或者使用 `getattr(signal, "SIGKILL", signal.SIGTERM)` 作为替代方案。
- **在调用 `os.kill(pid, 0)` 进行检测时，需同时捕获 `OSError` 和 `ProcessLookupError`**。在 Windows 上，若目标进程已终止，系统会抛出 `OSError`（错误代码为 WinError 87，提示“参数不正确”），而非 `ProcessLookupError`。
- **不要强制终端遵循 POSIX 规范**。函数 `os.setsid`、`os.killpg`、`os.getpgid` 和 `os.fork` 在 Windows 上均会抛出异常，应通过 `if sys.platform != "win32":` 或 `if os.name != "nt":` 这样的条件语句来限制其使用。
- **以显式的 `encoding="utf-8"` 参数打开文件**。Windows 环境下 Python 的默认编码为系统区域设置编码（通常为 cp1252），这种编码在处理非拉丁文字时会导致乱码或程序崩溃。
- **始终使用 `pathlib.Path` / `os.path.join` 构建路径，切勿手动用 `/` 连接字符串**。这一规则对于操作系统返回的字符串影响较小，但对于我们主动构造并传递给子进程的字符串则非常重要。

常见处理模式：

### 1. `termios` 和 `fcntl` 仅适用于 Unix 系统

务必同时捕获 `ImportError` 和 `NotImplementedError` 异常：

```python
try:
    from simple_term_menu import TerminalMenu
    menu = TerminalMenu(options)
    idx = menu.show()
except (ImportError, NotImplementedError):
    # Fallback: numbered menu
    for i, opt in enumerate(options):
        print(f"  {i+1}. {opt}")
    idx = int(input("Choice: ")) - 1
```

### 2. 文件编码

某些环境可能会以非 UTF-8 编码格式保存 `.env` 文件：

```python
try:
    load_dotenv(env_path)
except UnicodeDecodeError:
    load_dotenv(env_path, encoding="latin-1")
```

### 3. 进程管理

不同平台上，`os.setsid()`、`os.killpg()`以及信号处理的功能存在差异：

```python
import platform
if platform.system() != "Windows":
    kwargs["preexec_fn"] = os.setsid
```

### 4. 路径分隔符

请使用 `pathlib.Path`，而非通过 `/` 进行字符串拼接。

## 安全考量

Hermes 具有终端访问权限，因此安全问题至关重要。

### 现有的防护措施

| 防护层级 | 实现方式 |
|---------|----------|
| **Sudo 密码传递保护** | 使用 `shlex.quote()` 防止命令注入攻击 |
| **危险命令检测** | 在 `tools/approval.py` 中通过正则表达式配合用户审批流程进行监控 |
| **Cron 提示符注入防护** | 扫描器可识别并阻止试图覆盖指令的模式 |
| **写入禁止列表** | 通过 `os.path.realpath()` 解析受保护路径，防止通过符号链接绕过限制 |
| **技能模块安全检查** | 对 Hub 中安装的技能模块进行安全扫描 |
| **代码执行沙箱** | 子进程运行时会被移除 API 密钥 |
| **容器加固措施** | Docker 环境下会禁用所有特殊权限，防止权限提升，并设置 PID 限制 |

### 贡献涉及安全敏感的代码时需注意的事项

- 在将用户输入整合到命令行中时，务必使用 `shlex.quote()` 进行处理
- 在执行访问控制检查之前，先通过 `os.path.realpath()` 解析符号链接
- 禁止记录任何敏感信息
- 在工具执行过程中需捕获通用异常
- 若您的修改涉及文件路径或进程操作，必须在所有平台上进行测试

## Pull Request 提交流程

### 分支命名规范

```
fix/description        # Bug fixes
feat/description       # New features
docs/description       # Documentation
test/description       # Tests
refactor/description   # Code restructuring
```

### 提交之前

1. **运行测试**：为确保与 CI 环境一致，请使用 `scripts/run_tests.sh`。仅在封装脚本不可用或您有意在封装脚本之外进行调试时，才直接使用 `python -m pytest ...`。
2. **手动测试**：启动 `hermes` 并执行您修改过的代码路径。
3. **检查跨平台兼容性**：需考虑 macOS、Linux、WSL2 以及原生 Windows 环境。如果您修改了文件 I/O、进程管理、终端处理、子进程或信号相关功能，请运行 `scripts/check-windows-footguns.py`。
4. **确保 PR 内容聚焦**：每个 PR 应仅包含一个逻辑上的变更。

### PR 描述

需包含以下内容：
- **具体修改了什么**以及**原因**
- **如何测试**这些更改
- 您在哪些**平台上**进行了测试
- 引用任何相关的 Issue

### 提交信息

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 标准：

```
<type>(<scope>): <description>
```

| 类型 | 用途 |
|------|------|
| `fix` | 错误修复 |
| `feat` | 新功能开发 |
| `docs` | 文档编写 |
| `test` | 测试相关任务 |
| `refactor` | 代码重构 |
| `chore` | 构建、持续集成及依赖项更新 |

适用范围：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security`

示例：
```
fix(cli): prevent crash in save_config_value when model is a string
feat(gateway): add WhatsApp multi-user session isolation
fix(security): prevent shell injection in sudo password piping
```

## 报告问题

- 请通过 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues) 提交问题
- 需提供以下信息：操作系统、Python版本、Hermes版本（使用 `hermes version` 命令查看）、完整的错误堆栈信息
- 同时需附上问题重现的步骤
- 在提交新问题前，请先查看是否有重复提交的问题
- 若发现安全漏洞，请通过私密渠道进行报告

## 社区交流

- **Discord**: [discord.gg/NousResearch](https://discord.gg/NousResearch)
- **GitHub Discussions**: 用于讨论设计方案及架构相关内容
- **Skills Hub**: 可在此上传专业技能模块并与社区成员共享

## 许可协议

通过贡献代码，即表示您同意您的贡献将遵循 [MIT许可证](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) 的条款。
