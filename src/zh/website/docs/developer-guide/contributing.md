---
sidebar_position: 4
title: "Contributing"
description: "How to contribute to Hermes Agent — dev setup, code style, PR process"
---

# 贡献指南

感谢您为 Hermes Agent 做出贡献！本指南将为您介绍如何搭建开发环境、理解代码库以及如何提交并合并您的 Pull Request。

## 贡献优先级

我们按照以下顺序优先处理各类贡献：

1. **错误修复** — 程序崩溃、异常行为、数据丢失等问题
2. **跨平台兼容性** — macOS、不同 Linux 发行版及 WSL2 环境下的兼容性优化
3. **安全性强化** — 防止Shell注入、命令注入及路径遍历攻击
4. **性能与稳定性提升** — 重试机制、错误处理以及优雅降级功能
5. **新技能开发** — 具有广泛实用价值的技能（详见 [创建技能](creating-skills.md)）
6. **新工具开发** — 这类需求较为少见，大多数功能应通过技能实现
7. **文档完善** — 对现有文档的修正、补充说明及新示例添加

## 常见贡献方向

- 若希望在不修改 Hermes 核心代码的情况下构建自定义或本地工具？请从 [构建 Hermes 插件](../developer-guide/plugins/index.md) 开始
- 若希望为 Hermes 本身开发新的内置核心工具？请从 [添加工具](./adding-tools.md) 开始
- 若希望开发新技能？请从 [创建技能](./creating-skills.md) 开始
- 若希望开发新的推理提供者？请从 [添加提供者](./adding-providers.md) 开始

## 开发环境准备

### 先决条件

| 需求条件          | 备注                                                                                         |
| -------------------- | --------------------------------------------------------------------------------------------- |
| **Git**              | 需已安装 `git-lfs` 扩展                                                              |
| **Python 3.11–3.13** | 若缺失，uv 会自动进行安装                                                                 |
| **uv**               | 快速的 Python 包管理工具（[安装指南](https://docs.astral.sh/uv/)）                           |
| **Node.js 26+**      | 非必需——仅用于浏览器工具及 WhatsApp 桥接功能，其版本需与根目录下的 `package.json` 中指定的引擎版本一致 |

### 使用标准安装程序进行安装

对于大多数贡献者而言，最便捷的开发启动方式与普通用户相同：运行标准安装程序，随后在克隆的代码仓库中进行开发。该安装程序会创建 Hermes 虚拟环境，配置 `hermes` 命令，标记 `hermes update` 的安装方式，并将完整的 Git 项目克隆到 `$HERMES_HOME/hermes-agent` 目录中（通常为 `~/.hermes/hermes-agent`）。这样一来，您的开发环境就能保持与 CLI、更新工具、延迟依赖安装器、网关及文档所预设的相同结构。

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

您还可以运行一个完全隔离的 Hermes 实例（通过设置临时的 HERMES_HOME、独立的 Electron userData 以及不同的 Electron 应用名称，从而避免单实例锁定问题）：

```bash
scripts/dev-sandbox.sh python -m hermes_cli.main
scripts/dev-sandbox.sh --persistent python -m hermes_cli.main desktop  # state survives restarts, but lives in the worktree :)
```

### 手动克隆作为备用方案

仅当您明确不想使用 Hermes 的托管安装结构时才应采用此方式（例如在容器或 CI 任务中使用的临时克隆项目）。若选择这种方式安装，请务必从该虚拟环境运行 `hermes` 入口程序；直接使用系统命令 `python3 -m hermes_cli.main` 可能会引入与当前项目无关的系统 Python 包。

请在**已克隆的源代码目录之外**创建虚拟环境。如果虚拟环境位于代理程序运行的目录内，代理程序可能会对其自身checkout的路径执行相对路径命令（如 `rm -rf venv`、`uv venv venv` 等），从而悄无声息地破坏正在运行的运行时环境，导致会话中断。将虚拟环境置于目录之外，可确保工作区中的任何相对路径都无法指向它。

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

如果您使用了手动克隆的备用方案，请从代码检出目录运行 `./hermes`，或明确地创建该克隆版本的虚拟环境符号链接：

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
```

### 运行测试

```bash
scripts/run_tests.sh
```

## 代码风格

- 遵循 **PEP 8** 规范，但可适当放宽限制（无需严格限制行长度）
- **注释**：仅用于解释那些不直观的设计意图、权衡方案或 API 的特殊行为
- **错误处理**：应捕获特定的异常。对于意外出现的错误，可使用 `logger.warning()`/`logger.error()` 并设置 `exc_info=True` 参数
- **跨平台兼容性**：切勿默认代码仅在 Unix 系统上运行（详见下文）
- **配置文件安全路径**：严禁硬编码 `~/.hermes` 路径——在编写代码时应使用 `hermes_constants` 模块中的 `get_hermes_home()` 函数获取路径，而在面向用户的提示中则可使用 `display_hermes_home()` 函数。完整规则请参阅 [AGENTS.md](https://github.com/NousResearch/hermes-agent/blob/main/AGENTS.md#profiles-multi-instance-support) 文档。

## 跨平台兼容性

详情请参见 **[平台支持](../getting-started/platform-support.md)**。在原生 Windows 环境下，shell 命令需通过 [Git for Windows](https://git-scm.com/download/win) 提供的 Git Bash 工具来执行。部分功能依赖于 POSIX 内核接口，因此仅在支持此类接口的系统上可用：例如，控制面板中的嵌入式 PTY 终端面板（位于 `/chat` 标签页）需要 POSIX PTY 环境（Linux、macOS 或 WSL2）。如果主要在 Windows 环境下进行开发，建议在提交代码前运行 Windows 版的代码检查工具 `scripts/check-windows-footguns.py`。

在贡献代码时，请务必牢记以上规则：

- **请勿直接使用未加保护的 `signal.SIGKILL` 引用**。该信号在 Windows 系统中并不存在。应通过 `gateway.status.terminate_pid(pid, force=True)` 来实现（该函数会在 Windows 上执行 `taskkill /T /F` 指令，在 POSIX 系统上则使用 SIGKILL 信号），或者采用兜底方案 `getattr(signal, "SIGKILL", signal.SIGTERM)`。

- **在调用 `os.kill(pid, 0)` 时，需同时捕获 `OSError` 和 `ProcessLookupError`**。对于已经不存在的进程 ID，Windows 系统会抛出 `OSError`（错误代码 WinError 87，提示“参数不正确”），而非 `ProcessLookupError`。

- **切勿强制让终端遵循 POSIX 规范**。函数 `os.setsid`、`os.killpg`、`os.getpgid` 和 `os.fork` 在 Windows 上都会抛出异常，应通过 `if sys.platform != "win32":` 或 `if os.name != "nt":` 进行条件限制。

- **以显式的 `encoding="utf-8"` 参数打开文件**。Windows 系统下 Python 的默认编码为系统区域设置编码（通常为 cp1252），这种编码在处理非拉丁文字时会导致乱码或程序崩溃。

- **请使用 `pathlib.Path` 或 `os.path.join` 构建路径——切勿手动用 `/` 连接字符串**。这一要求对于操作系统返回的字符串而言重要性较低，但对于我们自行构造并传递给子进程的字符串则至关重要。

**关键处理模式：**

### 1. 文件编码

某些环境可能会以非 UTF-8 编码保存 `.env` 文件：

```python
try:
    load_dotenv(env_path)
except UnicodeDecodeError:
    load_dotenv(env_path, encoding="latin-1")
```

### 2. 进程管理

不同平台上，`os.setsid()`、`os.killpg()`以及信号处理功能的实现方式存在差异：

```python
import platform
if platform.system() != "Windows":
    kwargs["preexec_fn"] = os.setsid
```

### 3. 路径分隔符

请使用 `pathlib.Path`，而非通过 `/` 进行字符串拼接。

## 安全注意事项

Hermes 具有终端访问权限，因此安全问题至关重要。

### 现有的防护措施

| 防护层级                           | 实现方式                                                                 |
| ---------------------------------- | -------------------------------------------------------------------------- |
| **Sudo 密码传递保护**             | 使用 `shlex.quote()` 函数以防止shell注入攻击                             |
| **危险命令检测**                   | 在 `tools/approval.py` 中通过正则表达式配合用户审批流程进行识别         |
| **Cron 提示注入防护**               | 扫描器会拦截试图覆盖指令的模式                                             |
| **写入禁止列表**                     | 通过 `os.path.realpath()` 解析受保护路径，防止通过符号链接绕过限制       |
| **技能模块安全防护**                 | 对集成在 Hub 中的技能模块运行安全扫描器                                   |
| **代码执行沙箱**                     | 子进程运行时会被移除 API 密钥，从而避免安全风险                           |
| **容器加固**                       | Docker 环境下：禁用所有特权能力，防止权限提升，并设置 PID 限制           |

### 贡献涉及安全敏感性的代码时需注意的事项

- 在将用户输入嵌入Shell命令时，务必使用`shlex.quote()`函数进行处理  
- 在执行访问控制检查之前，先通过`os.path.realpath()`函数解析符号链接  
- 绝不对敏感信息进行日志记录  
- 在工具执行过程中捕获广义异常  
- 若您的修改涉及文件路径或进程，请在所有平台上进行测试  

## Pull Request提交流程

### 分支命名规则

```
fix/description        # Bug fixes
feat/description       # New features
docs/description       # Documentation
test/description       # Tests
refactor/description   # Code restructuring
```

### 提交之前

1. **运行测试**：为确保与 CI 环境一致，请使用 `scripts/run_tests.sh`。仅在无法使用封装脚本，或您有意在封装脚本外部进行调试时，才直接使用 `python -m pytest ...`。
2. **手动测试**：启动 `hermes` 并执行您所修改的代码路径。
3. **检查跨平台兼容性**：需考虑 macOS、Linux、WSL2 以及原生 Windows 环境。如果您修改了文件 I/O、进程管理、终端处理、子进程或信号相关功能，请运行 `scripts/check-windows-footguns.py`。
4. **确保 PR 内容聚焦**：每个 PR 应仅包含一个逻辑上的更改。

### PR 描述

需包含以下内容：

- **具体更改了什么**以及**原因**
- **如何测试**这些更改
- 您在哪些**平台上**进行了测试
- 参考任何相关的 Issues

### 提交信息

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 标准：

```
<type>(<scope>): <description>
```

| 类型       | 用途                         |
| ---------- | ----------------------------- |
| `fix`      | 错误修复                     |
| `feat`     | 新功能开发                   |
| `docs`     | 文档编写                     |
| `test`     | 测试任务                     |
| `refactor` | 代码重构                     |
| `chore`    | 构建、持续集成及依赖项更新   |

适用范围：`cli`、`gateway`、`tools`、`skills`、`agent`、`install`、`whatsapp`、`security`

示例：

```
fix(cli): prevent crash in save_config_value when model is a string
feat(gateway): add WhatsApp multi-user session isolation
fix(security): prevent shell injection in sudo password piping
```

### 仓库本地审查检查清单：`.agents/checks/*.md`

基于Hermes构建的项目，或由Hermes进行审查的项目，可将审查人员的检查清单存储在仓库中的`.agents/checks/`目录下。每个文件都是一个结构清晰的纯Markdown格式检查清单，Agent在审查涉及对应功能区域的代码变更之前会加载这些清单：

```
.agents/
  checks/
    security.md        # e.g. "grep the diff for shell interpolation; check subprocess calls quote args"
    migrations.md      # e.g. "every schema change ships a backfill and a rollback note"
    public-api.md      # e.g. "exported signatures changed? flag for semver review"
```

确保这些检查机制有效运行的通用准则：

- **每个文件专注一个检查项**，并以该检查项的名称命名。较小的文件会被完整读取，而庞大的 `checklist.md` 文件则仅会被粗略浏览。
- **将检查项编写为可验证的操作步骤**（如“执行 X 并确认 Y”），而非模糊的期望值（如“代码应当是安全的”）。
- **在文件顶部明确说明触发条件**——即该检查清单适用于哪些路径或变更类型——这样智能体（或人类）就能快速跳过无关内容。
- 将这些检查清单与它们所保护的代码一同存放在版本控制系统中：它们会随代码库一起演进，因此修改规则的 Pull Request 也会同步更新检查清单，所有变更都会体现在同一个差异对比中。

当您让 Hermes 审核包含 `.agents/checks/` 目录的仓库中的 Pull Request 时，请告知它（或通过技能教给它）先读取相关的检查清单并依据这些清单给出反馈。这样，审核智能体就能获得针对特定项目的评估标准，而通用的审核提示则无法做到这一点。

## 问题报告

- 请使用 [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues) 进行报告。
- 报告时需包含：操作系统、Python 版本、Hermes 版本（通过 `hermes --version` 查看）、完整的错误堆栈信息。
- 需附上问题复现步骤。
- 创建新问题前请先查看现有问题，避免重复提交。
- 若发现安全漏洞，请私下报告。

## 社区交流

- **Discord**：[discord.gg/NousResearch](https://discord.gg/NousResearch)
- **GitHub Discussions**：用于讨论设计方案和架构问题。
- **Skills Hub**：可用于上传专业技能并与社区共享。

## 许可证

通过贡献代码，即表示您同意您的贡献内容将依据 [MIT 许可证](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE) 进行授权。
