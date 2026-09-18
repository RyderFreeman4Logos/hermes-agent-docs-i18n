---
sidebar_position: 1
title: "Hermes Agent Quickstart"
description: "Your first conversation with Hermes Agent — from install to chatting in under 5 minutes"
---

# Hermes Agent 快速入门指南

本指南将帮助您从零开始搭建一个能够稳定运行的 Hermes 环境，以应对实际使用中的各种场景。您将学习如何进行安装、选择合适的提供方、验证聊天功能是否正常，以及当系统出现故障时该如何处理。

## 更喜欢观看视频？

**Onchain AI Garage** 提供了一期关于安装、配置及基本命令的完整教学课程——如果您更倾向于通过视频学习，这将是本页面的绝佳补充。更多内容请查看完整的 [Hermes Agent 教程与应用案例](https://www.youtube.com/playlist?list=PLmpUb_PWAkDxewld5ZYyKifuHxgIbiq2d) 播放列表。

<div style={{position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', maxWidth: '100%', marginBottom: '1.5rem'}}>
  <iframe
    style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%'}}
    src="https://www.youtube-nocookie.com/embed/R3YOGfTBcQg"
    title="Hermes Agent 教学课程：安装、配置与基本命令"
    frameBorder="0"
    allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen
  ></iframe>
</div>

## 适用人群

- 刚开始使用，希望最快搭建出可用系统的用户
- 需要更换提供方，且不想因配置错误浪费时间的用户
- 为团队、机器人或持续运行的工作流搭建 Hermes 环境的用户
- 对“已成功安装但仍然无法使用”这种情况感到困扰的用户

## 最快捷的解决方案

根据您的目标选择对应的方案：

| 目标 | 先执行此操作 | 再执行此操作 |
|---|---|---|
| 我只想让Hermes在我的机器上运行 | `hermes setup` | 进行实际对话并确认其能响应 |
| 我已经知道要使用的服务提供商 | `hermes model` | 保存配置，然后开始聊天 |
| 我想要构建机器人或始终在线的系统 | 在CLI功能正常后执行 `hermes gateway setup` | 连接Telegram、Discord、Slack或其他平台 |
| 我想要使用本地或自托管的模型 | `hermes model` → 自定义端点 | 验证端点地址、模型名称以及上下文长度 |
| 我需要多服务提供商容错机制 | 先执行 `hermes model` | 在基础聊天功能正常后，再添加路由和容错功能 |

**经验法则：** 如果Hermes无法完成正常对话，切勿急于添加更多功能。先确保能进行一次流畅的对话，之后再逐步添加网关、定时任务、技能、语音功能或路由功能。

---

## 1. 安装Hermes Agent
### 使用macOS或Windows上的Hermes Desktop安装程序（推荐）
如需轻松安装命令行工具和桌面应用，请从我们的网站[下载Hermes Desktop安装程序](https://hermes-agent.nousresearch.com/)并运行它。

### 不使用Hermes Desktop：
如仅需安装命令行工具而不需要桌面界面，可执行以下操作：

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
如果您要在手机上安装，请参阅专门的[Termux指南](./termux.md)，其中详细介绍了经过测试的手动安装步骤、支持的附加组件以及当前针对Android系统的限制。
:::

安装完成后，请重新加载您的shell：

```bash
source ~/.bashrc   # or source ~/.zshrc
```

如需了解详细的安装选项、前置条件及故障排除方法，请参阅[安装指南](./installation.md)。

## 2. 选择提供方

这是最重要的设置步骤。可使用 `hermes model` 以交互方式协助您完成选择：

```bash
hermes model
```

:::提示 最简便的途径：Nous Portal  
一个订阅即可使用300多种模型，同时还包含[工具网关](../user-guide/features/tool-gateway.md)（网页搜索、图像生成、文本转语音、云浏览器）等功能。在全新安装的情况下：

```bash
hermes setup --portal
```

该命令可一次性完成登录操作、将Nous设为你的服务提供商，并启用工具网关。
:::

:::info 设置模式
在全新安装时，`hermes setup` 提供三种设置模式：

- **快速设置（Nous Portal）** — 通过OAuth登录，无需管理API密钥；同时配置模型与工具网关相关功能，费用将计入你的[Nous Portal订阅套餐](/integrations/nous-portal)。这是推荐的快捷方案。
- **完整设置** — 你需要亲自逐一配置各类服务提供商、工具及选项（需自行准备密钥）。
- **空白启动** — 除运行代理所需的最低限度组件——**服务提供商与模型、文件操作工具集以及终端工具集**之外，其余所有功能均处于关闭状态。该模式下不支持网页、浏览器、代码执行、视觉处理、内存管理、任务委托、定时任务、技能功能、插件或MCP服务器，同时压缩功能、检查点机制、智能路由及内存捕获功能也会被禁用。在完成基础配置后，你可以选择两种路径之一：**从所有功能关闭的状态开始**（立即获得最简化的代理），或**逐步配置各项功能**（按需启用工具、技能、插件、MCP及消息功能）。当你希望创建一个经过完全控制的极简代理，并且只启用真正需要的功能时，可选择此模式。

“空白启动”模式会明确生成 `platform_toolsets.cli` 列表以及 `agent.disabled_toolsets` 文件，因此任何未主动选择的组件都不会被加载——即便在运行 `hermes update` 后也是如此。之后可通过 `hermes tools` 重新启用所需功能，使用 `hermes skills opt-in --sync` 添加技能，或通过 `hermes setup agent` 调整相关设置。
:::

合理的默认设置：

| Provider | What it is | How to set up |
|----------|-----------|---------------|
| **Nous Portal** | Subscription-based, zero-config | OAuth login via `hermes model` |
| **OpenAI Codex** | ChatGPT or Codex subscription, uses Codex models | Device code auth via `hermes model` → **ChatGPT or Codex Subscription** |
| **Anthropic** | Claude models directly — Max plan + extra usage credits (OAuth), or API key for pay-per-token | `hermes model` → OAuth login (requires Max + extra credits), or an Anthropic API key |
| **OpenRouter** | Multi-provider routing across many models | Enter your API key |
| **Fireworks AI** | Direct OpenAI-compatible model API | Set `FIREWORKS_API_KEY` |
| **Z.AI** | GLM / Zhipu-hosted models | Set `GLM_API_KEY` / `ZAI_API_KEY` (also accepts `Z_AI_API_KEY`) |
| **Kimi / Moonshot** | Moonshot-hosted coding and chat models | Set `KIMI_API_KEY` (or the Kimi-Coding-specific `KIMI_CODING_API_KEY`) |
| **Kimi / Moonshot China** | China-region Moonshot endpoint | Set `KIMI_CN_API_KEY` |
| **Arcee AI** | Trinity models | Set `ARCEEAI_API_KEY` |
| **GMI Cloud** | Multi-model direct API | Set `GMI_API_KEY` |
| **Actual Computer** | Your own hardware as a private inference cluster — hosted relay or local daemon | Set `ACTUAL_API_KEY` (relay) or `ACTUAL_BASE_URL=http://127.0.0.1:8080` (local, no key) |
| **MiniMax (OAuth)** | MiniMax frontier model via browser OAuth — no API key needed (model name in `hermes_cli/models.py` may change between releases) | `hermes model` → MiniMax (OAuth) |
| **MiniMax** | International MiniMax endpoint | Set `MINIMAX_API_KEY` |
| **MiniMax China** | China-region MiniMax endpoint | Set `MINIMAX_CN_API_KEY` |
| **Alibaba Cloud** | Qwen models via DashScope | Set `DASHSCOPE_API_KEY` (Qwen Coding Plan also accepts `ALIBABA_CODING_PLAN_API_KEY`) |
| **Hugging Face** | 20+ open models via unified router (Qwen, DeepSeek, Kimi, etc.) | Set `HF_TOKEN` |
| **AWS Bedrock** | Claude, Nova, Llama, DeepSeek via native Converse API | IAM role or `aws configure` ([guide](../guides/aws-bedrock.md)) |
| **Azure Foundry** | Azure AI Foundry-hosted models | Set `AZURE_FOUNDRY_API_KEY` + `AZURE_FOUNDRY_BASE_URL` |
| **Google AI Studio** | Gemini models via direct API | Set `GOOGLE_API_KEY` / `GEMINI_API_KEY` |
| **xAI** | Grok models via direct API | Set `XAI_API_KEY` |
| **xAI Grok OAuth** | SuperGrok / Premium+ subscription, no API key needed | `hermes model` → xAI Grok OAuth |
| **NovitaAI** | Multi-model API gateway | Set `NOVITA_API_KEY` |
| **Ramp Router** | Responses-native LLM gateway routing across OpenAI/Anthropic/xAI/... | Set `RAMP_ROUTER_API_KEY` |
| **Nebius Token Factory** | Open models on Nebius AI cloud | Set `NEBIUS_API_KEY` |
| **StepFun** | Step Plan models | Set `STEPFUN_API_KEY` |
| **Xiaomi MiMo** | Xiaomi-hosted models | Set `XIAOMI_API_KEY` |
| **Tencent TokenHub** | Tencent-hosted models | Set `TOKENHUB_API_KEY` |
| **Tencent TokenPlan** | Tencent Hy models via Anthropic-style endpoint | Set `TOKENPLAN_API_KEY` |
| **Ollama Cloud** | Managed Ollama-hosted models | Set `OLLAMA_API_KEY` |
| **LM Studio** | Local desktop app exposing an OpenAI-compatible API | Set `LM_API_KEY` (and `LM_BASE_URL` if non-default) |
| **Qwen OAuth** | Qwen Portal browser OAuth — no API key needed | `hermes model` → Qwen OAuth |
| **Kilo Code** | KiloCode-hosted models | Set `KILOCODE_API_KEY` |
| **OpenCode Zen** | Pay-as-you-go access to curated models | Set `OPENCODE_ZEN_API_KEY` |
| **OpenCode Go** | $10/month subscription for open models | Set `OPENCODE_GO_API_KEY` |
| **DeepSeek** | Direct DeepSeek API access | Set `DEEPSEEK_API_KEY` |
| **NVIDIA NIM** | Nemotron models via build.nvidia.com or local NIM | Set `NVIDIA_API_KEY` (optional: `NVIDIA_BASE_URL`) |
| **GitHub Copilot** | GitHub Copilot subscription (GPT-5.x, Claude, Gemini, etc.) | OAuth via `hermes model`, or `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` |
| **GitHub Copilot ACP** | Copilot ACP agent backend (spawns local `copilot` CLI) | `hermes model` (requires `copilot` CLI + `copilot login`) |
| **Vercel AI Gateway** | Vercel AI Gateway routing | Set `AI_GATEWAY_API_KEY` |
| **Custom Endpoint** | VLLM, SGLang, Ollama, or any OpenAI-compatible API | Set base URL + API key |

对于大多数首次使用的用户：请选择一个提供商，除非您知道为何要更改，默认设置即可。完整的提供商列表以及相关环境变量和配置步骤均可在 [Providers](../integrations/providers.md) 页面查看。

:::注意 最小上下文长度：64K 个标记  
Hermes Agent 需要支持至少 **64,000 个标记** 的上下文长度。上下文长度过短的模型无法为多步骤工具调用流程保留足够的工作内存，从而会在启动时被拒绝。大多数托管模型（如 Claude、GPT、Gemini、Qwen、DeepSeek）都轻松满足这一要求。如果您使用的是本地模型，请将其上下文大小设置为至少 64K（例如，对于 llama.cpp 使用 `--ctx-size 65536`，对于 Ollama 则使用 `-c 65536`）。  
:::

:::提示  
您可以通过 `hermes model` 命令随时更换提供商，无需受限于当前选择。如需查看所有支持的提供商及其详细配置信息，请参阅 [AI Providers](../integrations/providers.md)。  
:::

### 设置的存储方式  

Hermes 会将机密信息与普通配置分开存储：  

- **机密信息及令牌** → `~/.hermes/.env`  
- **非机密设置** → `~/.hermes/config.yaml`  

最简便的设置方式是通过命令行界面进行操作。

```bash
hermes config set model anthropic/claude-opus-4.6
hermes config set terminal.backend docker
hermes config set OPENROUTER_API_KEY sk-or-...
```

正确的数值会自动被写入对应的文件中。

## 3. 运行您的首次对话

```bash
hermes            # classic CLI
hermes --tui      # modern TUI (recommended)
```

您会看到一个欢迎横幅，其中显示了所使用的模型、可用工具以及技能。请使用具体且易于验证的提示词：

:::提示 选择合适的界面
Hermes 提供两种终端界面：传统的 `prompt_toolkit` 命令行界面，以及功能更先进的 [TUI](../user-guide/tui.md) 界面。后者具备模态覆盖层、鼠标选择功能以及非阻塞式输入能力。这两种界面共享相同的会话、斜杠命令和配置——您可以分别使用 `hermes` 和 `hermes --tui` 来体验它们。
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

**成功的表现：**

- 顶部横幅会显示您选择的模型/提供商
- Hermes 能够无误地回复
- 在需要时能够使用相应工具（终端、文件读取、网络搜索等）
- 对话可以正常进行多轮交流

如果以上都能实现，那就意味着您已经度过了最艰难的阶段。

## 4. 验证会话功能正常

在继续下一步之前，请先确认恢复会话的功能可用：

```bash
hermes --continue    # Resume the most recent session
hermes -c            # Short form
```

这样应该能让你回到刚才的会话。如果无法恢复，请检查你是否使用的是相同的配置文件，以及该会话是否已被成功保存。在后续需要同时操作多套环境或多台机器时，这一点尤为重要。

## 5. 体验核心功能

### 使用终端

```
❯ What's my disk usage? Show the top 5 largest directories.
```

该智能体会代表您执行终端命令并显示执行结果。

### 斜杠命令

输入 `/` 可查看所有命令的自动补全下拉列表：

| 命令 | 功能说明 |
|---------|-----------|
| `/help` | 显示所有可用命令 |
| `/tools` | 列出可用工具 |
| `/model` | 交互式切换模型 |
| `/personality pirate` | 尝试有趣的性格模式 |
| `/save` | 保存对话内容 |

### 多行输入

按 `Alt+Enter`、`Ctrl+J` 或 `Shift+Enter` 可添加新行。`Shift+Enter` 需要终端能够将其作为独立指令发送（默认支持 Kitty / foot / WezTerm / Ghostty；启用 Kitty 键盘协议后，iTerm2 / Alacritty / VS Code 终端也支持）。`Alt+Enter` 和 `Ctrl+J` 在所有终端中均有效。

### 中断智能体

如果智能体响应过慢，输入新消息后按 Enter 即可中断当前任务并切换到新指令。使用 `Ctrl+C` 也可实现相同效果。

## 6. 添加进阶功能层

需在基础聊天功能正常运行后才能使用。根据需求选择：

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

对于 Docker 沙箱环境，您还可以启用**出站凭证注入代理**，这样沙箱就永远无法看到您的真实 API 密钥——它只能看到那些仅在本地 TLS 拦截守护进程后才能使用的匿名代理令牌。详情请参阅[出站代理](../user-guide/egress/iron-proxy.md)。设置步骤为 `hermes egress setup && hermes egress start`；`hermes setup terminal` 也会为 Docker 用户提供相关指引。目前 Modal、SSH、Daytona 和 Singularity 这几种环境暂不支持该功能。

### 语音模式

```bash
# From the Hermes install directory (the curl installer placed it at
# ~/.hermes/hermes-agent on Linux/macOS or %LOCALAPPDATA%\hermes\hermes-agent on Windows):
cd ~/.hermes/hermes-agent
uv pip install --python ./venv/bin/python -e ".[voice]"
# Includes faster-whisper for free local speech-to-text
```

随后在命令行中输入：`/voice on`。按 `Ctrl+B` 即可开始录音。详情请参阅[语音模式](../user-guide/features/voice-mode.md)。

### 技能

技能是按需提供的指令文档，用于指导Hermes执行特定任务——例如部署到Kubernetes、提交GitHub PR、微调模型或搜索GIF。每项技能都对应一个 `SKILL.md` 文件，其中包含名称、描述以及分步操作指南。Hermes会先免费显示简短描述，只有在实际需要执行任务时才会加载该技能的完整内容，因此添加技能不会增加每次请求的负载。

Hermes默认已预装了一系列技能，存储在 `~/.hermes/skills/` 目录中。您可以从技能中心添加更多技能，或自行编写技能。

**从技能中心浏览并安装：**

```bash
hermes skills browse                      # list everything available
hermes skills search kubernetes           # find skills by keyword
hermes skills install openai/skills/k8s   # install one (runs a security scan first)
```

安装参数为来自中心的 `source/path` 标识符——例如 `openai/skills/k8s` 即表示 OpenAI 目录中的 `k8s` 技能。使用 `hermes skills browse` 可查看应使用的具体标识符。

**使用技能**——所有已安装的技能都会自动转换为斜杠命令：

```bash
/k8s deploy the staging manifest          # run the skill with a request
/k8s                                       # load it and let Hermes ask what you need
```

该功能在命令行界面以及任何已连接的消息平台中均可使用。您无需预先安装所有组件——当对话中的任务与某个技能匹配时，智能体会在正常交流过程中自动选择合适的预装技能。

如需了解如何创建自定义的外部技能目录以及完整的 Hub 源列表，请参阅[技能系统](../user-guide/features/skills.md)。

### MCP 服务器

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

标准版本的ACP已内置所有`[all]`附加功能，因此通过curl安装时便已包含该功能。只需执行以下命令即可：

```bash
hermes acp
```

（如果您在安装时未选择 `[all]`，请先运行 `cd ~/.hermes/hermes-agent && uv pip install -e ".[acp]"`。）

详情请参阅 [ACP 编辑器集成](../user-guide/features/acp.md)。

---

## 常见故障模式

以下是最容易耗费时间的常见问题：

| 症状 | 可能原因 | 解决方案 |
|---|---|---|
| Hermes 能启动，但回复为空或异常 | 提供商认证或模型选择有误 | 重新运行 `hermes model`，确认供应商、模型及认证信息 |
| 自定义端点“看似可用”，但返回无用内容 | 基础 URL、模型名称有误，或该端点实际上不兼容 OpenAI | 先在独立的客户端中测试该端点 |
| Gateway 已启动，但无人能向其发送消息 | 机器人令牌、允许列表或平台配置不完整 | 重新运行 `hermes gateway setup`，并查看 `hermes gateway status` 的状态 |
| `hermes --continue` 无法找到旧会话 | 切换了用户配置文件，或会话从未被保存 | 查看 `hermes sessions list`，确认当前使用的配置文件正确 |
| 模型不可用或出现异常的回退行为 | 提供商路由设置或回退策略过于严格 | 在基础供应商稳定之前，先关闭自动路由功能 |
| `hermes doctor` 检测到配置问题 | 配置值缺失或已过期 | 修正配置，在添加新功能前先测试普通聊天功能 |

## 恢复工具包

当系统出现异常时，请按以下顺序操作：

1. `hermes doctor`
2. `hermes model`
3. `hermes setup`
4. `hermes sessions list`
5. `hermes --continue`
6. `hermes gateway status`

通过这一系列步骤，您可以快速将系统从异常状态恢复到正常工作状态。

## 快速参考

| 命令 | 描述 |
|---------|-------------|
| `hermes` | 开始聊天 |
| `hermes model` | 选择对应的LLM服务提供商与模型 |
| `hermes tools` | 配置各平台可使用的工具 |
| `hermes setup` | 完整设置向导（一次性配置所有参数） |
| `hermes doctor` | 诊断问题 |
| `hermes update` | 升级到最新版本 |
| `hermes gateway` | 启动消息传递网关 |
| `hermes --continue` | 继续上一次的会话 |

## 后续步骤

- **[CLI指南](../user-guide/cli.md)** — 掌握终端界面操作
- **[配置设置](../user-guide/configuration.md)** — 自定义系统配置
- **[消息传递网关](../user-guide/messaging/index.md)** — 连接Telegram、Discord、Slack、WhatsApp、Signal、邮件、Home Assistant、Teams等平台
- **[工具与工具集](../user-guide/features/tools.md)** — 了解可用功能
- **[AI服务提供商](../integrations/providers.md)** — 完整的服务提供商列表及设置说明
- **[技能系统](../user-guide/features/skills.md)** — 可复用的工作流与知识库
- **[技巧与最佳实践](../guides/tips.md)** — 高级用户实用技巧
- **[迁移至其他设备](/reference/faq#exporting-hermes-to-another-machine)** — 使用`hermes backup`可迁移整个系统设置（或单个配置文件[/reference/faq#moving-a-single-profile-to-another-machine]），无需从头开始重新配置 |
