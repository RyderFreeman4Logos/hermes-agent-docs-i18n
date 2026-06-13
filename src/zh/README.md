<p align="center">
  <img src="assets/banner.png" alt="Hermes Agent" width="100%">
</p>

# Hermes Agent ☤
<p align="center">
  <a href="https://hermes-agent.nousresearch.com/">Hermes Agent</a> | <a href="https://hermes-agent.nousresearch.com/">Hermes Desktop</a>
</p>
<p align="center">
  <a href="https://hermes-agent.nousresearch.com/docs/"><img src="https://img.shields.io/badge/Docs-hermes--agent.nousresearch.com-FFD700?style=for-the-badge" alt="文档"></a>
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://github.com/NousResearch/hermes-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="许可证：MIT"></a>
  <a href="https://nousresearch.com"><img src="https://img.shields.io/badge/Built%20by-Nous%20Research-blueviolet?style=for-the-badge" alt="由 Nous Research 开发"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文文档"></a>
  <a href="README.ur-pk.md"><img src="https://img.shields.io/badge/Lang-اردو-green?style=for-the-badge" alt="乌尔都语文档"></a>
</p>

**这是一款由 [Nous Research](https://nousresearch.com) 开发的自我进化型 AI 智能体。**它是唯一具备内置学习循环的智能体——它能够从经验中创建技能，在使用过程中不断优化这些技能，主动保持知识记忆，检索过往对话记录，并在多次会话之间逐步构建对用户特征的深入理解。您可以在价值 5 美元的 VPS、GPU 集群，或是闲置时成本几乎为零的无服务器基础设施上运行它。它并不局限于您的笔记本电脑——即使智能体运行在云虚拟机上，您也可以通过 Telegram 与其交互。

您可以使用任何想要的模型——[Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)（200 多种模型）、[NovitaAI](https://novita.ai）（提供 Model API、Agent Sandbox 和 GPU Cloud 的原生 AI 云平台）、[NVIDIA NIM](https://build.nvidia.com)（Nemotron 框架）、[Xiaomi MiMo](https://platform.xiaomimimo.com)、[z.ai/GLM](https://z.ai)、[Kimi/Moonshot](https://platform.moonshot.ai)、[MiniMax](https://www.minimax.io)、[Hugging Face](https://huggingface.co)、OpenAI，或是您自己的模型端点。只需使用 `hermes model` 命令即可切换模型——无需修改代码，也不会受到绑定限制。

<table>
<tr><td><b>真正的终端界面</b></td><td>具备多行编辑、斜杠命令自动补全、对话历史记录、中断与重定向功能，以及工具输出流式显示的完整 TUI 界面。</td></tr>
<tr><td><b>随您所在之处而存在</b></td><td>通过单个网关进程即可连接 Telegram、Discord、Slack、WhatsApp、Signal 以及 CLI 等平台。还支持语音备忘录转录以及跨平台对话连续性功能。</td></tr>
<tr><td><b>闭环学习机制</b></td><td>智能体会自主筛选记忆内容并定期进行优化。完成复杂任务后可自动创建新技能，这些技能在使用过程中还会持续改进。通过 FTS5 实现会话间搜索，并借助大语言模型进行总结，从而方便跨会话调用信息。<a href="https://github.com/plastic-labs/honcho">Honcho</a>式的辩证用户建模技术，同时兼容 <a href="https://agentskills.io">agentskills.io</a> 开放标准。</td></tr>
<tr><td><b>定时自动化任务</b></td><td>内置 cron 定时调度器，可将任务发送到任意平台。每日报告、夜间备份、每周审计——所有操作均可用自然语言描述，且可在无人值守情况下自动执行。</td></tr>
<tr><td><b>任务委派与并行处理</b></td><td>可创建独立的子智能体以并行处理不同任务流。您还可以编写 Python 脚本，通过 RPC 接口调用各种工具，将多步骤流程简化为无需额外上下文开销的快速操作。</td></tr>
<tr><td><b>可在任何地方运行，不仅限于笔记本</b></td><td>支持六种终端后端——本地、Docker、SSH、Singularity、Modal 以及 Daytona。Daytona 和 Modal 提供无服务器持久化功能：智能体的环境在闲置时会进入休眠状态，需要时再唤醒，因此在不同会话之间的运行成本几乎为零。您可以在价值 5 美元的 VPS 或 GPU 集群上运行它。</td></tr>
<tr><td><b>适合研究用途</b></td><td>支持批量轨迹生成及轨迹压缩功能，可用于训练下一代工具调用模型。</td></tr>
</table>

---

## 快速安装

### Linux、macOS、WSL2、Termux

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### Windows（原生版，PowerShell）

> **重要提示：** Windows原生环境可在无需WSL的情况下运行Hermes——其CLI、网关、TUI及各类工具均以原生方式运行。如果您更倾向于使用WSL2，上述适用于Linux/macOS的命令同样可以在该环境中使用。发现漏洞？请[提交问题报告](https://github.com/NousResearch/hermes-agent/issues)。

在PowerShell中执行以下命令：

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

安装程序会自动处理所有相关配置：包括 uv、Python 3.11、Node.js、ripgrep、ffmpeg，以及一个便携式的 Git Bash（即 MinGit，会被解压到 `%LOCALAPPDATA%\hermes\git` 目录中——无需管理员权限，且与系统自带的 Git 完全隔离）。Hermes 会使用这个内置的 Git Bash 来执行 shell 命令。

如果您已经安装了 Git，安装程序会自动检测并使用它。否则，您只需下载约 45MB 的 MinGit 即可——它不会影响系统自带的 Git。

> **Android / Termux：** 经过测试的手动安装路径详见 [Termux 使用指南](https://hermes-agent.nousresearch.com/docs/getting-started/termux)。在 Termux 环境中，Hermes 会安装一个精选过的 `.[termux]` 插件包，因为完整的 `.[all]` 插件包会包含与 Android 不兼容的语音相关依赖项。

> **Windows：** 原生 Windows 环境得到了全面支持——上述的 PowerShell 一键命令即可完成所有安装。如果您更愿意使用 WSL2，Linux 版本的命令同样适用。原生 Windows 安装文件存放在 `%LOCALAPPDATA%\hermes` 目录下；而 WSL2 环境下的安装文件则与 Linux 一样，存放在 `~/.hermes` 目录中。

安装完成后：

```bash
source ~/.bashrc    # reload shell (or: source ~/.zshrc)
hermes              # start chatting!
```

## 入门指南

```bash
hermes              # Interactive CLI — start a conversation
hermes model        # Choose your LLM provider and model
hermes tools        # Configure which tools are enabled
hermes config set   # Set individual config values
hermes gateway      # Start the messaging gateway (Telegram, Discord, etc.)
hermes setup        # Run the full setup wizard (configures everything at once)
hermes claw migrate # Migrate from OpenClaw (if coming from OpenClaw)
hermes update       # Update to the latest version
hermes doctor       # Diagnose any issues
```

📖 **[完整文档 →](https://hermes-agent.nousresearch.com/docs/)**

---

## 无需收集 API 密钥——Nous Portal

Hermes 可以与您选择的任何服务提供商配合使用，这一点不会改变。但如果您不想分别为模型、网络搜索、图像生成、文本转语音以及云浏览器收集五组不同的 API 密钥，**[Nous Portal](https://portal.nousresearch.com)** 即可通过一个订阅套餐整合所有功能：

- **300 多种模型**——通过 `/model <名称>` 即可选用任意模型；
- **工具网关**——网络搜索（Firecrawl）、图像生成（FAL）、文本转语音（OpenAI）、云浏览器（Browser Use），所有功能均通过您的订阅套餐统一处理，无需额外账户。

首次安装后仅需一条命令即可使用：

```bash
hermes setup --portal
```

该操作会通过 OAuth 进行登录，将 Nous 设定为您的服务提供方，并启用工具网关。您随时可以使用 `hermes portal info` 查看当前已连接的配置。更多详细信息请参阅[工具网关文档页面](https://hermes-agent.nousresearch.com/docs/user-guide/features/tool-gateway)。

您仍然可以随时为不同的工具自行配置密钥——该网关是按后端独立运行的，并非全有或全无的模式。

---

## CLI 与消息平台快速参考

Hermes 提供两种使用方式：通过 `hermes` 启动终端界面，或运行网关后从 Telegram、Discord、Slack、WhatsApp、Signal 或邮件与其交互。一旦进入对话模式，许多斜杠命令在两种界面中都是通用的。

| 操作                         | CLI                                           | 消息平台                                                              |
| ------------------------------ | --------------------------------------------- | -------------------------------------------------------------------------------- |
| 开始聊天                     | `hermes`                                      | 先运行 `hermes gateway setup` + `hermes gateway start`，然后向机器人发送消息 |
| 开启新对话                   | `/new` 或 `/reset`                            | `/new` 或 `/reset`                                                               |
| 更换模型                     | `/model [provider:model]`                     | `/model [provider:model]`                                                        |
| 设置人格特征                 | `/personality [name]`                         | `/personality [name]`                                                            |
| 重试或撤销上一步操作         | `/retry`, `/undo`                             | `/retry`, `/undo`                                                                |
| 压缩上下文/查看使用情况       | `/compress`, `/usage`, `/insights [--days N]` | `/compress`, `/usage`, `/insights [days]`                                        |
| 浏览技能                     | `/skills` 或 `/<skill-name>`                  | `/<skill-name>`                                                                  |
| 中断当前操作                 | `Ctrl+C` 或发送新消息                        | `/stop` 或发送新消息                                                    |
| 平台专属状态信息             | `/platforms`                                  | `/status`, `/sethome`                                                            |

完整的命令列表请参阅[CLI 指南](https://hermes-agent.nousresearch.com/docs/user-guide/cli)和[消息网关指南](https://hermes-agent.nousresearch.com/docs/user-guide/messaging)。

---

## 文档资源

所有文档均位于 **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**：

| 类别                                                                                             | 内容涵盖                                                 |
| --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| [快速入门](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart)                 | 2分钟内完成安装→配置→首次对话                           |
| [CLI 使用指南](https://hermes-agent.nousresearch.com/docs/user-guide/cli)                              | 命令、快捷键、人格设置、会话管理                         |
| [配置指南](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)                | 配置文件、服务提供方、模型及所有选项                     |
| [消息网关指南](https://hermes-agent.nousresearch.com/docs/user-guide/messaging)                | Telegram、Discord、Slack、WhatsApp、Signal、Home Assistant支持 |
| [安全指南](https://hermes-agent.nousresearch.com/docs/user-guide/security)                          | 命令审批、私信配对、容器隔离机制                         |
| [工具与工具集](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools)            | 40多种工具、工具集系统、终端后端支持                     |
| [技能系统指南](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)              | 程序化记忆、技能中心、技能创建方法                         |
| [内存管理指南](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)                     | 持久化内存、用户资料、最佳实践                           |
| [MCP 集成指南](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp)               | 连接任意 MCP 服务器以扩展功能                             |
| [定时任务指南](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)              | 基于平台的定时任务调度                                     |
| [上下文文件指南](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files)       | 影响每段对话的项目上下文设置                             |
| [架构指南](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture)             | 项目结构、智能体运行循环、核心类设计                         |
| [贡献指南](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing)             | 开发环境配置、PR流程、代码风格规范                           |
| [CLI 参考手册](https://hermes-agent.nousresearch.com/docs/reference/cli-commands)                  | 所有命令及参数说明                                         |
| [环境变量指南](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | 完整的环境变量参考列表                                     |

---

## 从 OpenClaw 迁移

如果您原本使用的是 OpenClaw，Hermes 可以自动导入您的设置、记忆内容、技能及 API 密钥。

**首次设置时：** 设置向导（`hermes setup`）会自动检测 `~/.openclaw` 文件，并在配置开始前提供迁移选项。

**安装后的任何时间：**

```bash
hermes claw migrate              # Interactive migration (full preset)
hermes claw migrate --dry-run    # Preview what would be migrated
hermes claw migrate --preset user-data   # Migrate without secrets
hermes claw migrate --overwrite  # Overwrite existing conflicts
```

将被导入的内容包括：

- **SOUL.md** — 人物设定文件  
- **Memories** — MEMORY.md 与 USER.md 中的记录  
- **Skills** — 用户自定义的技能 → `~/.hermes/skills/openclaw-imports/`  
- **命令白名单** — 审批规则配置  
- **消息设置** — 平台配置、允许通信的用户列表及工作目录  
- **API密钥** — 已列入白名单的密钥（Telegram、OpenRouter、OpenAI、Anthropic、ElevenLabs）  
- **TTS资源** — 工作空间内的音频文件  
- **工作空间说明** — AGENTS.md 文件（需使用 `--workspace-target` 参数）  

如需查看所有选项，请参阅 `hermes claw migrate --help`；若希望通过交互式引导完成迁移并预览效果，可使用 `openclaw-migration` 技能。

---

## 贡献指南

我们欢迎大家贡献代码！请参阅[贡献指南](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing)，了解开发环境配置、代码风格规范及提交请求流程。  

对于希望快速入门的贡献者，可直接克隆项目并运行 `setup-hermes.sh` 进行初始化：

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # installs uv, creates venv, installs .[all], symlinks ~/.local/bin/hermes
./hermes              # auto-detects the venv, no need to `source` first
```

手动路径（与上述路径功能相同）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

## 社区资源

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [问题反馈](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — 专为 Hermes 及其他 MCP 主机设计的 Linux 桌面控制 MCP 服务器，支持 AT-SPI 辅助功能树、Wayland/X11 输入操作、截图以及合成器窗口控制。
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — 社区微信桥接工具：允许在同一个微信账号上同时运行 Hermes Agent 和 OpenClaw。

---

## 许可协议

采用 MIT 许可协议 — 详情请参阅 [LICENSE](LICENSE) 文件。

本项目由 [Nous Research](https://nousresearch.com) 开发。
