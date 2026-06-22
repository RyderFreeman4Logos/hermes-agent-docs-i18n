---
sidebar_position: 1
title: "Quickstart"
description: "Your first conversation with Hermes Agent — from install to chatting in under 5 minutes"
---

# 快速入门

本指南将指导您从零开始搭建一个能够稳定运行的Hermes环境。您将学会如何进行安装、选择服务提供商、验证聊天功能，以及了解出现问题时该如何处理。

## 更喜欢观看视频？

**Onchain AI Garage**制作了一期关于安装、配置及基本命令的完整教程视频——如果您更喜欢通过视频学习，这将是本页面的绝佳补充。更多内容请查看完整的[Hermes Agent教程与应用案例](https://www.youtube.com/playlist?list=PLmpUb_PWAkDxewld5ZYyKifuHxgIbiq2d)播放列表。

<div style={{position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', maxWidth: '100%', marginBottom: '1.5rem'}}>
  <iframe
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%'}}
    src="https://www.youtube-nocookie.com/embed/R3YOGfTBcQg"
    title="Hermes Agent大师课：安装、配置与基本命令"
    frameBorder="0"
    allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen
  ></iframe>
</div>

## 适用人群

- 完全新手，希望最快搭建出可用的系统
- 正在更换服务提供商，不想因配置错误浪费时间
- 为团队、机器人或持续运行的工作流搭建Hermes环境
- 遇到“已安装但仍然无法使用”的问题

## 最快捷的路径

根据您的目标选择对应的步骤：

| 目标 | 第一步操作 | 后续操作 |
|---|---|---|
| 只想在本地机器上让Hermes运行 | 执行 `hermes setup` | 进行实际聊天并验证其响应功能 |
| 已经确定要使用的服务提供商 | 执行 `hermes model` | 保存配置后开始聊天 |
| 希望建立机器人或持续运行的系统 | 在CLI功能正常后执行 `hermes gateway setup` | 连接Telegram、Discord、Slack或其他平台 |
| 希望使用本地或自托管模型 | 执行 `hermes model` → 设置自定义端点 | 验证端点地址、模型名称及上下文长度 |
| 希望实现多服务提供商备用机制 | 先执行 `hermes model` | 在基础聊天功能正常后再添加路由与备用方案 |

**经验法则：** 如果Hermes无法完成常规聊天，暂不要添加更多功能。先确保能进行一次正常的对话，之后再逐步添加网关、定时任务、技能、语音功能或路由机制。

---

## 1. 安装Hermes Agent
### 使用macOS或Windows上的Hermes Desktop安装程序（推荐）
如需轻松安装命令行工具和桌面应用，请从我们的网站[下载Hermes Desktop安装程序](https://hermes-agent.nousresearch.com/)并运行它。

### 不使用Hermes Desktop：
如需仅安装命令行工具而不使用Hermes Desktop，请执行以下操作：

#### Linux / macOS / WSL2 / Android（Termux）
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

#### Windows（原生版）

在 PowerShell 中运行：
```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1) 
```

:::提示 Android / Termux
如果您在手机上安装，请参阅专门的[Termux指南](./termux.md)，其中详细介绍了经过测试的手动安装步骤、支持的附加组件以及当前针对Android系统的限制。
:::

安装完成后，请重新加载您的shell：

```bash
source ~/.bashrc   # or source ~/.zshrc
```

如需了解详细的安装选项、前置条件及故障排除方法，请参阅[安装指南](./installation.md)。

## 2. 选择提供商

这是最为重要的设置步骤。您可以使用 `hermes model` 命令以交互方式协助完成选择过程：

```bash
hermes model
```

:::提示 最简便的途径：Nous Portal  
一个订阅即可使用300多种模型，同时还包含[工具网关](../user-guide/features/tool-gateway.md)（网页搜索、图像生成、文本转语音、云浏览器）功能。在全新安装的情况下：

```bash
hermes setup --portal
```

该命令可一次性完成登录操作、将Nous设为服务提供商，并启用工具网关。
:::

:::info 设置模式
在全新安装时，`hermes setup` 提供三种设置模式：

- **快速设置（Nous Portal）**——支持免费OAuth登录，无需API密钥；可同时设置模型及工具网关相关功能。这是推荐的快速路径。
- **完整设置**——需手动配置每个服务提供商、工具及各项选项（需自行准备密钥）。
- **空白起步模式**——除运行智能体所需的最低必要组件外，其余所有功能均处于关闭状态：即服务提供商与模型、文件操作工具集以及终端工具集。该模式下不支持网页访问、浏览器功能、代码执行、视觉处理、内存管理、任务委托、定时任务、技能调用、插件使用或MCP服务器，同时压缩功能、检查点机制、智能路由及内存捕获功能也会被禁用。在完成这些基础配置后，可选择两种路径之一：要么从完全关闭所有功能的状态开始（立即获得最简版的智能体），要么逐步启用各项配置（按需开启工具、技能、插件、MCP及消息功能）。当您希望创建一个经过严格控制的极简智能体，并且只启用真正需要的功能时，可选用此模式。

“空白起步模式”会明确生成 `platform_toolsets.cli` 列表以及 `agent.disabled_toolsets` 文件，因此任何未选中的功能都不会被加载——即便在运行 `hermes update` 后也不会改变。如需后续重新启用某项功能，可使用 `hermes tools` 命令；若要添加技能，可使用 `hermes skills opt-in --sync` 命令；调整设置则可通过 `hermes setup agent` 完成。
:::

推荐的默认设置如下：

| 服务提供商 | 类型 | 设置方式 |
|----------|------|----------|
| **Nous Portal** | 订阅制，无需额外配置 | 通过 `hermes model` 进行OAuth登录 |
| **OpenAI Codex** | 基于ChatGPT的OAuth接口，使用Codex模型 | 通过 `hermes model` 进行设备代码认证 |
| **Anthropic** | 直接使用Claude系列模型——支持Max套餐及额外使用额度（通过OAuth认证），也可使用API密钥按令牌付费 | 通过 `hermes model` 进行OAuth登录（需拥有Max套餐及额外额度），或输入Anthropic API密钥 |
| **OpenRouter** | 支持跨多种模型进行多服务提供商路由 | 输入对应API密钥 |
| **Z.AI** | 由GLM/Zhipu提供的模型 | 设置 `GLM_API_KEY` / `ZAI_API_KEY`（也支持 `Z_AI_API_KEY`） |
| **Kimi / Moonshot** | 由Moonshot提供的编程及聊天模型 | 设置 `KIMI_API_KEY`（或专为Kimi编程功能设计的 `KIMI_CODING_API_KEY`） |
| **Kimi / Moonshot China** | 中国地区的Moonshot接口 | 设置 `KIMI_CN_API_KEY` |
| **Arcee AI** | Trinity系列模型 | 设置 `ARCEEAI_API_KEY` |
| **GMI Cloud** | 支持多种模型的直接API访问 | 设置 `GMI_API_KEY` |
| **MiniMax (OAuth)** | 通过浏览器OAuth访问Minimax前沿模型——无需API密钥（`hermes_cli/models.py` 文件中的模型名称在不同版本中可能会发生变化） | 通过 `hermes model` 选择MiniMax（OAuth）模式 |
| **MiniMax** | 国际版的Minimax接口 | 设置 `MINIMAX_API_KEY` |
| **MiniMax China** | 中国地区的Minimax接口 | 设置 `MINIMAX_CN_API_KEY` |
| **Alibaba Cloud** | 通过DashScope访问Qwen系列模型 | 设置 `DASHSCOPE_API_KEY`（Qwen编程套餐也支持 `ALIBABA_CODING_PLAN_API_KEY`） |
| **Hugging Face** | 通过统一路由器访问20多种开源模型（包括Qwen、DeepSeek、Kimi等） | 设置 `HF_TOKEN` |
| **AWS Bedrock** | 通过原生Converse API访问Claude、Nova、Llama、DeepSeek等模型 | 使用IAM角色或通过 `aws configure` 配置（详见[指南](../guides/aws-bedrock.md)） |
| **Azure Foundry** | 由Azure AI Foundry提供的模型 | 设置 `AZURE_FOUNDRY_API_KEY` 及 `AZURE_FOUNDRY_BASE_URL` |
| **Google AI Studio** | 通过直接API访问Gemini系列模型 | 设置 `GOOGLE_API_KEY` / `GEMINI_API_KEY` |
| **xAI** | 通过直接API访问Grok系列模型 | 设置 `XAI_API_KEY` |
| **xAI Grok OAuth** | SuperGrok/Premium+套餐用户，无需API密钥 | 通过 `hermes model` 选择xAI Grok OAuth模式 |
| **NovitaAI** | 多模型API网关 | 设置 `NOVITA_API_KEY` |
| **StepFun** | Step Plan系列模型 | 设置 `STEPFUN_API_KEY` |
| **Xiaomi MiMo** | 由小米提供的模型 | 设置 `XIAOMI_API_KEY` |
| **Tencent TokenHub** | 由腾讯提供的模型 | 设置 `TOKENHUB_API_KEY` |
| **Ollama Cloud** | 由托管服务提供的Ollama模型 | 设置 `OLLAMA_API_KEY` |
| **LM Studio** | 本地桌面应用，提供兼容OpenAI的API接口 | 设置 `LM_API_KEY`（如非默认地址，则还需设置 `LM_BASE_URL`） |
| **Qwen OAuth** | 通过Qwen Portal的浏览器OAuth功能访问——无需API密钥 | 通过 `hermes model` 选择Qwen OAuth模式 |
| **Kilo Code** | 由KiloCode提供的模型 | 设置 `KILOCODE_API_KEY` |
| **OpenCode Zen** | 支持按需付费使用精选模型 | 设置 `OPENCODE_ZEN_API_KEY` |
| **OpenCode Go** | 以每月10美元的价格订阅使用开源模型 | 设置 `OPENCODE_GO_API_KEY` |
| **DeepSeek** | 直接访问DeepSeek的API | 设置 `DEEPSEEK_API_KEY` |
| **NVIDIA NIM** | 通过build.nvidia.com或本地NIM环境访问Nemotron模型 | 设置 `NVIDIA_API_KEY`（可选：设置 `NVIDIA_BASE_URL`） |
| **GitHub Copilot** | GitHub Copilot订阅服务（支持GPT-5.x、Claude、Gemini等模型） | 通过 `hermes model` 进行OAuth登录，或直接使用 `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` |
| **GitHub Copilot ACP** | Copilot ACP智能体后端（会生成本地的 `copilot` CLI工具） | 需先通过 `hermes model` 配置，并确保已安装 `copilot` CLI并完成登录 |
| **自定义接口** | VLLM、SGLang、Ollama或任何兼容OpenAI的API | 设置基础URL及API密钥 |

对于大多数首次使用用户而言：选择一种服务提供商后，除非有特殊需求，否则直接接受默认设置即可。完整的供应商列表、环境变量设置及配置步骤均可在 [Providers](../integrations/providers.md) 页面查看。
:::caution 最小上下文长度：64K tokens
Hermes Agent要求模型至少具备**64,000 tokens**的上下文容量。上下文长度过短的模型无法为多步骤工具调用流程保留足够的工作内存，因此在启动时会被拒绝。大多数托管模型（如Claude、GPT、Gemini、Qwen、DeepSeek）都很容易满足这一要求。如果使用本地模型，则需将其上下文大小设置为至少64K（例如，对于llama.cpp可使用 `--ctx-size 65536`，对于Ollama则可使用 `-c 65536`）。
:::

:::tip
您可以通过 `hermes model` 命令随时更换服务提供商，无需担心被绑定。如需查看所有受支持的服务提供商列表及详细配置信息，请参阅 [AI Providers](../integrations/providers.md) 页面。
:::

### 设置值的存储方式
Hermes会将敏感信息与普通配置分开存储：

- **敏感信息及令牌** → `~/.hermes/.env`
- **非敏感设置** → `~/.hermes/config.yaml`

最简便的设置方式是通过CLI命令来完成：

```bash
hermes config set model anthropic/claude-opus-4.6
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...
```

正确的值会自动被写入对应的文件中。

## 3. 运行您的首次对话

```bash
hermes            # classic CLI
hermes --tui      # modern TUI (recommended)
```

您会看到一个欢迎横幅，其中显示了所使用的模型、可用工具以及技能。请使用具体且易于验证的提示词：

:::提示 选择合适的界面
Hermes 提供两种终端界面：传统的 `prompt_toolkit` 命令行界面，以及功能更先进的 [TUI](../user-guide/tui.md) 界面——后者具备模态覆盖层、鼠标选择功能以及非阻塞式输入能力。这两种界面共享相同的会话、斜杠命令及配置文件，您可以通过 `hermes` 和 `hermes --tui` 分别尝试使用它们。
:::

```
Summarize this repo in 5 bullets and tell me what the main entrypoint is.
```

```
Check my current directory and tell me what looks like the main project file.
```

```
Help me set up a clean GitHub PR workflow for this codebase.
```

**成功的标志：**

- 顶部横幅会显示您选择的模型/提供方
- Hermes 能够无误地回复
- 在需要时能够调用工具（终端、文件读取、网络搜索等）
- 对话可以正常进行多轮交流

如果达到以上条件，那就意味着您已经克服了最困难的部分。

## 4. 验证会话功能正常

在继续下一步之前，请先确认恢复会话的功能可用：

```bash
hermes --continue    # Resume the most recent session
hermes -c            # Short form
```

这样应该能让你返回到刚才的会话。如果无法实现，建议检查你是否使用的是同一个配置文件，以及该会话是否已成功保存。当你需要同时管理多个环境或设备时，这一点尤为重要。

## 5. 体验核心功能

### 使用终端

```
❯ What's my disk usage? Show the top 5 largest directories.
```

该智能体会代表您执行终端命令并显示执行结果。

### 斜杠命令

输入 `/` 即可查看所有命令的自动补全下拉列表：

| 命令 | 功能说明 |
|---------|----------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试有趣的性格模式 |
| `/save` | 保存对话内容 |

### 多行输入

按 `Alt+Enter`、`Ctrl+J` 或 `Shift+Enter` 可添加新行。`Shift+Enter` 需要终端能够将其作为独立指令发送（默认支持 Kitty / foot / WezTerm / Ghostty；启用 Kitty 键盘协议后，iTerm2 / Alacritty / VS Code 终端也支持）。`Alt+Enter` 和 `Ctrl+J` 在所有终端中均有效。

### 中断智能体

如果智能体执行速度过慢，输入新消息后按 Enter 即可中断当前任务并切换到新的指令。使用 `Ctrl+C` 也能达到相同效果。

## 6. 添加进阶功能层

需在基础聊天功能正常运行后才能使用。请选择所需功能：

### 聊天机器人或共享助手

```bash
hermes gateway setup    # Interactive platform configuration
```

可连接 [Telegram](/user-guide/messaging/telegram)、[Discord](/user-guide/messaging/discord)、[Slack](/user-guide/messaging/slack)、[WhatsApp](/user-guide/messaging/whatsapp)、[Signal](/user-guide/messaging/signal)、[Email](/user-guide/messaging/email)、[Home Assistant](/user-guide/messaging/homeassistant) 或 [Microsoft Teams](/user-guide/messaging/teams)。

### 自动化与工具

- `hermes tools` — 根据不同平台调整工具访问权限  
- `hermes skills` — 浏览并安装可重复使用的流程模板  
- Cron — 仅在您的机器人或 CLI 设置稳定后使用  

### 沙箱终端

为确保安全，建议在 Docker 容器或远程服务器上运行该智能体：

```bash
hermes config set terminal.backend docker    # Docker isolation
hermes config set terminal.backend ssh       # Remote server
```

### 语音模式

```bash
# From the Hermes install directory (the curl installer placed it at
# ~/.hermes/hermes-agent on Linux/macOS or %LOCALAPPDATA%\hermes\hermes-agent on Windows):
cd ~/.hermes/hermes-agent
uv pip install -e ".[voice]"
# Includes faster-whisper for free local speech-to-text
```

随后在命令行中输入：`/voice on`。按 `Ctrl+B` 即可开始录音。详情请参阅[语音模式](../user-guide/features/voice-mode.md)。

### 技能

技能是一种按需提供的指令文档，用于指导Hermes执行特定任务——如部署到Kubernetes、提交GitHub PR、微调模型或搜索GIF图片。每项技能都对应一个 `SKILL.md` 文件，其中包含名称、描述以及分步操作指南。Hermes会先免费显示简短描述，只有当实际任务需要时才会加载完整内容，因此添加技能不会增加每次请求的负载。

Hermes默认已预装了一系列技能，存储在 `~/.hermes/skills/` 目录中。您可以从技能中心添加更多技能，或自行编写技能。

**从技能中心浏览并安装：**

```bash
hermes skills browse                      # list everything available
hermes skills search kubernetes           # find skills by keyword
hermes skills install openai/skills/k8s   # install one (runs a security scan first)
```

安装参数为来自中心的 `source/path` 标识符——例如 `openai/skills/k8s` 即表示 OpenAI 目录中的 `k8s` 技能。执行 `hermes skills browse` 命令即可查看可用的具体标识符。

**使用技能**——所有已安装的技能都会自动转换为斜杠命令形式：

```bash
/k8s deploy the staging manifest          # run the skill with a request
/k8s                                       # load it and let Hermes ask what you need
```

该功能在命令行界面以及所有已连接的消息平台上均可用。您无需预先安装所有组件——当对话中的任务与某项技能匹配时，智能体会在正常交流过程中自动选择合适的组合技能。

如需了解如何创建自定义的外部技能目录以及完整的中心节点源列表，请参阅[技能系统](../user-guide/features/skills.md)。

### MCP服务器

```yaml
# Add to ~/.hermes/config.yaml
mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```

### 编辑器集成（ACP）

标准版ACP已内置所有`[all]`扩展功能，因此通过curl安装工具即可直接使用该功能。只需运行以下命令即可：

```bash
hermes acp
```

(如果您在安装时未选择 `[all]`，请先运行 `cd ~/.hermes/hermes-agent && uv pip install -e ".[acp]"`。)

详情请参阅 [ACP 编辑器集成](../user-guide/features/acp.md)。

---

## 常见故障模式

以下是最容易耗费时间解决的问题：

| 症状 | 可能原因 | 解决方案 |
|---|---|---|
| Hermes 能启动，但回复为空或格式错误 | 提供商认证或模型选择有误 | 重新运行 `hermes model`，确认供应商、模型及认证信息 |
| 自定义端点“看似可用”，但返回乱码 | 基础 URL、模型名称有误，或该端点实际上不兼容 OpenAI | 先在独立的客户端中测试该端点 |
| 网关已启动，但无人能向其发送消息 | 机器人令牌、白名单或平台配置不完整 | 重新运行 `hermes gateway setup`，并查看 `hermes gateway status` |
| `hermes --continue` 无法找到旧会话 | 切换了用户配置文件，或会话从未被保存 | 查看 `hermes sessions list`，确认当前处于正确的配置文件中 |
| 模型不可用或出现异常的回退行为 | 提供商路由设置或回退策略过于严格 | 在基础供应商稳定之前，暂时关闭自动路由功能 |
| `hermes doctor` 检测到配置问题 | 配置值缺失或已过期 | 修正配置，在添加新功能前先测试普通对话功能 |

## 恢复工具包

当系统出现异常时，请按以下顺序操作：

1. `hermes doctor`
2. `hermes model`
3. `hermes setup`
4. `hermes sessions list`
5. `hermes --continue`
6. `hermes gateway status`

通过这一系列操作，您可以快速将系统从异常状态恢复到正常工作状态。

---

## 快速参考

| 命令 | 功能说明 |
|---------|-----------|
| `hermes` | 开始对话 |
| `hermes model` | 选择所需的 LLM 提供商和模型 |
| `hermes tools` | 配置各平台支持的工具 |
| `hermes setup` | 完整的设置向导（一次性配置所有参数） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 升级到最新版本 |
| `hermes gateway` | 启动消息传递网关 |
| `hermes --continue` | 继续上一次的会话 |

## 后续步骤

- **[CLI 指南](../user-guide/cli.md)** — 掌握终端界面操作
- **[配置指南](../user-guide/configuration.md)** — 自定义系统设置
- **[消息传递网关](../user-guide/messaging/index.md)** — 连接 Telegram、Discord、Slack、WhatsApp、Signal、Email、Home Assistant、Teams 等平台
- **[工具与工具集](../user-guide/features/tools.md)** — 了解所有可用功能
- **[AI 提供商列表](../integrations/providers.md)** — 完整的供应商列表及配置说明
- **[技能系统](../user-guide/features/skills.md)** — 可复用的工作流与知识库
- **[技巧与最佳实践](../guides/tips.md)** — 高级用户实用技巧 |
