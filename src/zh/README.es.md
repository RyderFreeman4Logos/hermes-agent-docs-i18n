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
  <a href="https://github.com/NousResearch/hermes-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/Licencia-MIT-green?style=for-the-badge" alt="许可证：MIT"></a>
  <a href="https://nousresearch.com"><img src="https://img.shields.io/badge/Creado%20por-Nous%20Research-blueviolet?style=for-the-badge" alt="由 Nous Research 开发"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-English-blue?style=for-the-badge" alt="英文版"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文版"></a>
  <a href="README.ur-pk.md"><img src="https://img.shields.io/badge/Lang-اردو-green?style=for-the-badge" alt="乌尔都语版"></a>
</p>

**这是由 [Nous Research](https://nousresearch.com) 开发的持续进化的 AI 智能体。** 它是唯一拥有内置学习循环的智能体：能够从使用经验中创造新技能，在使用过程中不断优化这些技能，自动推动知识留存，检索过往对话记录，并在多轮会话中逐步构建出更深入的“你”的模型画像。你只需花费 5 美元租用一台 VPS、GPU 集群，或是选择在空闲时几乎无需成本的服务器less 架构即可运行它。它不受笔记本电脑限制——即便你在云端虚拟机中工作，也能通过 Telegram 与它交流。

你可以使用任何想要的模型——[Nous Portal](https://portal.nousresearch.com)、[OpenRouter](https://openrouter.ai)（提供 200 多种模型）、[NovitaAI](https://novita.ai)、[NVIDIA NIM](https://build.nvidia.com)（Nemotron）、[Xiaomi MiMo](https://platform.xiaomimimo.com)、[z.ai/GLM](https://z.ai)、[Kimi/Moonshot](https://platform.moonshot.ai)、[MiniMax](https://www.minimax.io)、[Hugging Face](https://huggingface.co)、OpenAI，或是你自己的模型端点。只需通过 `hermes model` 命令即可切换模型——无需修改代码，也无需额外依赖。

<table>
<tr><td><b>真正的终端界面</b></td><td>具备多行编辑、命令自动补全、对话历史记录、中断与重定向功能，以及工具输出流式显示的完整 TUI 界面。</td></tr>
<tr><td><b>无处不在的使用体验</b></td><td>通过 Telegram、Discord、Slack、WhatsApp、Signal 以及 CLI 等方式均可与之交互——所有功能都由同一个网关进程处理。支持语音笔记转录，实现跨平台对话连续性。</td></tr>
<tr><td><b>闭环学习机制</b></td><td>智能体会定期进行自我提醒并维护记忆库。在完成复杂任务后能自主创建新技能，且这些技能会在使用过程中持续优化。采用 FTS5 算法检索会话记录，并通过 LLM 生成摘要，从而实现会话间的知识延续。支持 <a href="https://github.com/plastic-labs/honcho">Honcho</a> 式的对话式用户建模，同时兼容 <a href="https://agentskills.io">agentskills.io</a> 开放标准。</td></tr>
<tr><td><b>可编程自动化任务</b></td><td>内置 cron 计划器，可将任务部署到任意平台。支持每日报告、夜间备份、每周审计——所有操作均可通过自然语言指令完成，并自动执行。</td></tr>
<tr><td><b>任务委派与并行处理</b></td><td>可启动独立的子智能体以并行处理不同工作流。你可以编写 Python 脚本，通过 RPC 调用各类工具，将多步骤流程转化为零上下文开销的连续处理任务。</td></tr>
<tr><b>不仅限于笔记本电脑，随时随地可用</b></td><td>支持六种终端后端——本地、Docker、SSH、Singularity、Modal 以及 Daytona。Daytona 和 Modal 支持服务器less 持久化存储：智能体环境在空闲时会进入休眠状态，需要时再被唤醒，因此在不同会话之间的成本几乎为零。你可以在 5 美元的 VPS 或 GPU 集群上运行它。</td></tr>
<tr><td><b>专为研究设计</b></td><td>支持批量生成任务轨迹，还可对轨迹进行压缩，用于训练下一代工具调用模型。</td></tr>
</table>

---

## 快速安装

### Linux、macOS、WSL2、Termux

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### Windows（原生环境，PowerShell）

> **注意：**在Windows原生环境中，Hermes无需WSL即可运行——其CLI、网关、TUI及各类工具均以原生方式工作。如果您更愿意使用WSL2，上述Linux/macOS版本的命令同样适用于该环境。若遇到错误，请[提交问题报告](https://github.com/NousResearch/hermes-agent/issues)。

请在PowerShell中执行以下命令：

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

安装程序会处理所有相关事项：uv、Python 3.11、Node.js、ripgrep、ffmpeg，以及一个**便携式 Git Bash**（即 MinGit，解压后位于 `%LOCALAPPDATA%\hermes\git` —— 无需管理员权限，且与系统中的任何 Git 安装完全隔离）。Hermes 会使用内置的此 Git Bash 来执行 shell 命令。

如果您已安装了 Git，安装程序会自动检测并使用它。否则，您只需下载约 45MB 的 MinGit 即可——它不会触及或干扰系统中的任何 Git 安装。

> **Android / Termux：** 经过验证的手动配置路径记载在 [Termux 使用指南](https://hermes-agent.nousresearch.com/docs/getting-started/termux) 中。在 Termux 环境中，Hermes 会安装经过筛选的 `.[termux]` 插件，因为目前完整的 `.[all]` 插件包含与 Android 不兼容的语音相关依赖项。

> **Windows：** 原生 Windows 环境完全兼容——上述 PowerShell 命令即可完成所有安装。如果您更愿意使用 WSL2，Linux 版本的命令同样适用。原生 Windows 安装路径为 `%LOCALAPPDATA%\hermes`；而 WSL2 的安装路径则与 Linux 一致，为 `~/.hermes`。

安装完成后：

```bash
source ~/.bashrc    # recargar shell (o: source ~/.zshrc)
hermes              # ¡empieza a chatear!
```

## 第一步：入门指南

```bash
hermes              # CLI interactiva — inicia una conversación
hermes model        # Elige tu proveedor y modelo LLM
hermes tools        # Configura qué herramientas están habilitadas
hermes config set   # Establece valores de configuración individuales
hermes gateway      # Inicia el gateway de mensajería (Telegram, Discord, etc.)
hermes setup        # Ejecuta el asistente de configuración completo
hermes claw migrate # Migra desde OpenClaw (si vienes de OpenClaw)
hermes update       # Actualiza a la última versión
hermes doctor       # Diagnostica cualquier problema
```

📖 **[完整文档 →](https://hermes-agent.nousresearch.com/docs/)**

---

## 避免收集多个 API 密钥 — Nous Portal

Hermes 可以与您选择的任何提供商配合使用——这一点不会改变。但如果您不想为模型、网页搜索、图像生成、文本转语音以及云浏览器分别收集五个独立的 API 密钥，**[Nous Portal](https://portal.nousresearch.com)** 即可通过单一订阅满足所有需求：

- **超过 300 种模型**——通过 `/model <名称>` 即可轻松选择任意模型；
- **Tool Gateway**——涵盖网页搜索（Firecrawl）、图像生成（FAL）、文本转语音（OpenAI）以及云浏览器（Browser Use）等功能，所有服务均通过您的订阅统一处理，无需额外账户。

在新安装的环境中只需执行一条命令即可：

```bash
hermes setup --portal
```

该操作将通过 OAuth 进行身份验证，将 Nous 设定为你的提供方，并激活 Tool Gateway。你可以随时使用 `hermes portal info` 查看当前已连接的设备。更多详细信息请参阅 [Tool Gateway 文档页面](https://hermes-agent.nousresearch.com/docs/user-guide/features/tool-gateway)。

你需要时仍可继续为不同工具使用各自的密钥——该网关仅作用于后端，无需“全开或全关”。

---

## 快速参考：CLI 与消息平台

Hermes 提供两种接入方式：可通过 `hermes` 启动终端界面，或启动网关后通过 Telegram、Discord、Slack、WhatsApp、Signal 或 Email 与之交互。一旦进入对话模式，许多命令在两种界面之间都是通用的。

| 操作                              | CLI                                           | 消息平台                                                         |
| ----------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------- |
| 开始聊天                           | `hermes`                                      | 先执行 `hermes gateway setup` + `hermes gateway start`，然后向机器人发送消息 |
| 新建对话                           | `/new` 或 `/reset`                             | `/new` 或 `/reset`                                                                 |
| 切换模型                           | `/model [提供方:模型名]`                   | `/model [提供方:模型名]`                                                       |
| 设置人格                           | `/personality [名称]`                       | `/personality [名称]`                                                           |
| 重试或撤销上一步操作               | `/retry`, `/undo`                             | `/retry`, `/undo`                                                                 |
| 压缩上下文 / 查看使用情况           | `/compress`, `/usage`, `/insights [--days N]` | `/compress`, `/usage`, `/insights [days]`                                         |
| 浏览技能                           | `/skills` 或 `/<技能名称>`             | `/<技能名称>`                                                             |
| 中断当前任务                       | `Ctrl+C` 或发送新消息                        | `/stop` 或发送新消息                                                 |
| 查看特定平台的状态                 | `/platforms`                                  | `/status`, `/sethome`                                                             |

如需查看完整的命令列表，请参阅 [CLI 指南](https://hermes-agent.nousresearch.com/docs/user-guide/cli) 和 [消息平台网关指南](https://hermes-agent.nousresearch.com/docs/user-guide/messaging)。

---

## 文档资源

所有文档均位于 **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**：

| 类别                                                                                             | 内容概述                                                    |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| [快速入门](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart)              | 2分钟内完成安装 → 配置 → 首次对话                           |
| [CLI 使用指南](https://hermes-agent.nousresearch.com/docs/user-guide/cli)                             | 命令、快捷键、人格设置、会话管理                              |
| [配置指南](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)               | 配置文件、提供方、模型及所有选项设置                          |
| [消息平台网关](https://hermes-agent.nousresearch.com/docs/user-guide/messaging)           | 支持的平台：Telegram、Discord、Slack、WhatsApp、Signal、Home Assistant |
| [安全指南](https://hermes-agent.nousresearch.com/docs/user-guide/security)                        | 命令审批、私信配对、容器隔离机制                              |
| [工具与 Toolset 系统](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools)   | 40多种工具、Toolset 系统、终端后端功能                        |
| [技能系统](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)   | 程序记忆机制、Skills Hub、技能创建功能                        |
| [内存管理](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)                   | 持久化内存、用户配置文件及最佳实践                              |
| [MCP 集成](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp)              | 连接任意 MCP 服务器以实现扩展功能                              |
| [Cron 定时任务](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)           | 支持定时任务并将结果发送至对应平台                            |
| [上下文文件](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | 用于定义每段对话的项目上下文                                      |
| [架构设计](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture)            | 项目结构、代理循环逻辑及核心类设计                                |
| [贡献指南](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing)              | 开发环境配置、PR 提交流程及代码风格规范                          |
| [CLI 参考手册](https://hermes-agent.nousresearch.com/docs/reference/cli-commands)             | 所有命令及参数说明                                              |
| [环境变量参考](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | 完整的环境变量参考手册                                          |

---

## 从 OpenClaw 迁移

如果你原本使用的是 OpenClaw，Hermes 可以自动导入你的配置、记忆数据、技能及 API 密钥。

**在初始配置阶段：** 配置向导 (`hermes setup`) 会自动检测 `~/.openclaw` 文件，并在配置开始前提供迁移选项。

**安装完成后随时均可进行迁移：**

```bash
hermes claw migrate              # Migración interactiva (preset completo)
hermes claw migrate --dry-run    # Vista previa de qué se migraría
hermes claw migrate --preset user-data   # Migrar sin secretos
hermes claw migrate --overwrite  # Sobreescribir conflictos existentes
```

需要导入的内容包括：

- **SOUL.md** — 个性配置文件  
- **记忆内容** — MEMORY.md 和 USER.md 中的条目  
- **技能** — 用户自定义的技能 → `~/.hermes/skills/openclaw-imports/`  
- **允许使用的命令列表** — 审核规则模式  
- **消息传递设置** — 平台配置、允许的用户列表以及工作目录  
- **API 密钥** — 已列入白名单的密钥（适用于 Telegram、OpenRouter、OpenAI、Anthropic、ElevenLabs）  
- **TTS 资源** — 工作目录中的音频文件  
- **工作空间说明** — AGENTS.md 文件（通过 `--workspace-target` 参数指定）

如需查看所有选项，请运行 `hermes claw migrate --help`；或者使用 `openclaw-migration` 技能，让智能体引导您完成迁移，并提供试运行预览。

---

## 贡献指南

我们欢迎大家贡献代码！请参阅 [贡献指南](CONTRIBUTING.es.md)，了解开发环境配置、代码风格要求以及 Pull Request 提交流程。

对于希望快速参与的协作者，可通过克隆项目并运行 `setup-hermes.sh` 来开始使用：

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # instala uv, crea venv, instala .[all], enlaza ~/.local/bin/hermes
./hermes              # detecta automáticamente el venv, no necesitas hacer `source` primero
```

手动路径（与上述方式相同）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

## 社区

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [问题反馈](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — 专为 Hermes 及其他 MCP 主机设计的 Linux 桌面控制 MCP 服务器，支持 AT-SPI 辅助功能树、Wayland/X11 输入、屏幕截图以及合成器窗口定位功能。
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — 社区开发的微信桥接工具：可在同一个微信账号上同时运行 Hermes Agent 和 OpenClaw。

---

## 许可证

MIT 许可证 — 详情请参阅 [LICENSE](LICENSE) 文件。

由 [Nous Research](https://nousresearch.com) 创建。
