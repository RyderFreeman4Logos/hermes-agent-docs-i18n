---
sidebar_position: 3
title: "FAQ & Troubleshooting"
description: "Frequently asked questions and solutions to common issues with Hermes Agent"
---

# 常见问题与故障排除

针对最常见的问题和故障，提供快速解答与解决方案。

---

## 常见问题

### 哪些大语言模型提供商可与 Hermes 兼容？

Hermes Agent 可与任何兼容 OpenAI 的 API 配合使用。目前支持的提供商包括：

- **[OpenRouter](https://openrouter.ai/)** — 通过一个 API 密钥即可访问数百种模型（灵活性最高，推荐使用）
- **[Nous Portal](/integrations/nous-portal)** — Nous Research 的订阅平台——通过一次 OAuth 登录即可使用 300 多种模型以及网页、图像、文本转语音和浏览器相关功能（新手推荐）
- **OpenAI** — GPT-5.4、GPT-5-codex、GPT-4.1、GPT-4o 等模型
- **Anthropic** — Claude 系列模型（可直接通过 API 调用，也可通过 `hermes auth add anthropic`、OpenRouter 或其他兼容代理进行 OAuth 认证）
- **Google** — Gemini 系列模型（可通过 `gemini` 提供商的直接 API、OpenRouter 或兼容代理调用）
- **z.ai / ZhipuAI** — GLM 系列模型
- **Kimi / Moonshot AI** — Kimi 系列模型
- **MiniMax** — 支持全球及中国地区的端点
- **本地模型** — 可通过 [Ollama](https://ollama.com/)、[vLLM](https://docs.vllm.ai/)、[llama.cpp](https://github.com/ggerganov/llama.cpp)、[SGLang](https://github.com/sgl-project/sglang) 或任何兼容 OpenAI 的服务器来加载

您可以通过 `hermes model` 命令或编辑 `~/.hermes/.env` 文件来设置对应的提供商。所有提供商的密钥信息请参考 [环境变量](./environment-variables.md) 文档。

### 它能在 Windows/Android/Termux 或我的平台上运行吗？
完整的平台支持情况请参见 **[平台支持情况](../getting-started/platform-support.md)**。

### 我在 WSL2 中运行 Hermes，如何最有效地控制 Windows 系统上的普通 Chrome 浏览器？

建议使用 MCP 桥接方式，而非 `/browser connect`。

推荐方案如下：
- 在 WSL2 内部运行 Hermes；
- 继续使用 Windows 上已登录的普通 Chrome 浏览器；
- 通过 `cmd.exe` 或 `powershell.exe` 添加 `chrome-devtools-mcp` 作为 MCP 服务器；
- 让 Hermes 使用由此生成的 MCP 浏览器工具。

相比强制让 Hermes 核心浏览器传输直接在 WSL2 与 Windows 之间建立连接，这种方式更为可靠。

相关文档：
- [在 Hermes 中使用 MCP](../guides/use-mcp-with-hermes.md#wsl2-bridge-hermes-in-wsl-to-windows-chrome)
- [浏览器自动化](../user-guide/features/browser.md#wsl2--windows-chrome-prefer-mcp-over-browser-connect)

### 我的数据会被发送到其他地方吗？

API 调用**仅会发送到你配置的 LLM 服务提供商处**（例如 OpenRouter 或你本地的 Ollama 实例）。Hermes Agent 不会收集任何遥测数据、使用情况数据或分析信息。你的对话记录、记忆内容及技能信息都会存储在 `~/.hermes/` 目录中。

### 我可以离线使用或搭配本地模型吗？

可以。运行 `hermes model`，选择**自定义端点**，然后输入你的服务器地址即可。

```bash
hermes model
# Select: Custom endpoint (enter URL manually)
# API base URL: http://localhost:11434/v1
# API key: ollama
# Model name: qwen3.5:27b
# Context length: 64000   ← Hermes minimum; set this to match your server's actual context window
```

或者直接在 `config.yaml` 中进行配置：

```yaml
model:
  default: qwen3.5:27b
  provider: custom
  base_url: http://localhost:11434/v1
```

Hermes会将端点、提供方以及基础URL存储在`config.yaml`文件中，这样在服务器重启后这些配置依然有效。如果您的本地服务器仅加载了一个模型，`/model custom`指令会自动识别该模型。您也可以在`config.yaml`中设置`provider: custom`——它是一种独立的提供方类型，而非其他类型的别名。

此功能适用于Ollama、vLLM、llama.cpp服务器、SGLang、LocalAI等平台。详情请参阅[配置指南](../user-guide/configuration.md)。

:::提示 Ollama用户
如果您在Ollama中设置了自定义的`num_ctx`值（例如`ollama run --num_ctx 64000`），请务必在Hermes中设置对应的上下文长度——Ollama的 `/api/show`接口显示的是模型的*最大*上下文长度，而非您实际配置的有效`num_ctx`值。
:::

:::提示 使用本地模型时的超时问题
Hermes会自动检测本地端点，并放宽流式处理的超时设置（读取超时时间从120秒延长至1800秒，同时关闭过时流检测功能）。如果处理超大上下文时仍出现超时问题，可在`.env`文件中设置`HERMES_STREAM_READ_TIMEOUT=1800`。详细信息请参阅[本地LLM指南](../guides/local-llm-on-mac.md#timeouts)。
:::

### 成本是多少？
Hermes Agent本身是**免费且开源的**（采用MIT许可证）。您只需为所选提供方的LLM API服务支付费用，而本地模型的运行则完全免费。

### 多人可以共享同一个实例吗？

可以。[消息网关](../user-guide/messaging/index.md)支持通过Telegram、Discord、Slack、WhatsApp或Home Assistant，让多名用户与同一个Hermes Agent实例进行交互。访问权限通过允许列表（特定用户ID）和私信配对机制（第一个发送消息的用户获得访问权）来控制。

### 内存与技能有何区别？

- **内存**用于存储**事实信息**——即智能体所了解的关于您、您的项目以及偏好设置的内容。系统会根据相关性自动检索这些信息。
- **技能**则用于存储**操作步骤**——即完成某项任务的详细指引。当智能体遇到类似任务时，会调用相应的技能。

这两种机制的数据都会在会话之间保留。如需了解更多详情，请参阅[内存](../user-guide/features/memory.md)和[技能](../user-guide/features/skills.md)相关文档。

### 我可以在自己的Python项目中使用它吗？

可以。只需导入`AIAgent`类，即可以编程方式使用Hermes。

```python
from run_agent import AIAgent

agent = AIAgent(model="anthropic/claude-opus-4.7")
response = agent.chat("Explain quantum computing briefly")
```

如需了解完整的 API 使用方法，请参阅 [Python 库指南](../user-guide/features/code-execution.md)。

---

## 故障排除

### 安装问题

#### 安装完成后出现 `hermes: command not found` 错误

**原因：** 您的 shell 未重新加载更新后的 PATH 环境变量。

**解决方案：**
```bash
# Reload your shell profile
source ~/.bashrc    # bash
source ~/.zshrc     # zsh

# Or start a new terminal session
```

如果仍然无法正常使用，请检查安装位置：
```bash
which hermes
ls ~/.local/bin/hermes
```

:::提示
安装程序会自动将 `~/.local/bin` 添加到您的 PATH 环境变量中。如果您使用的是非标准shell配置文件，则需要手动添加 `export PATH="$HOME/.local/bin:$PATH"`。
:::

#### Python版本过旧

**原因：** Hermes要求使用Python 3.11或更高版本。

**解决方案：**
```bash
python3 --version   # Check current version

# Install a newer Python
sudo apt install python3.12   # Ubuntu/Debian
brew install python@3.12      # macOS
```

安装程序会自动处理此问题——如果在手动安装时出现该错误，请先升级 Python。

#### 终端命令显示 `node: command not found`（或 `nvm`、`pyenv`、`asdf` 等）

**原因：** Hermes 在启动时会运行一次 `bash -l`，从而为当前会话生成环境快照。Bash 登录 shell 会读取 `/etc/profile`、`~/.bash_profile` 和 `~/.profile`，但**不会加载 `~/.bashrc`**——因此那些被安装到该文件中的工具（如 `nvm`、`asdf`、`pyenv`、`cargo` 以及自定义的 `PATH` 设置）就不会被快照识别。这种情况最常见于 Hermes 在 systemd 环境下运行，或是在没有预加载交互式 shell 配置文件的极简 shell 中运行时。

**解决方案：** Hermes 默认会自动加载 `~/.bashrc`。如果这仍无法解决问题——例如您使用的是 zsh，且 PATH 设置在 `~/.zshrc` 中，或者您是从独立文件中初始化 `nvm`——则可以在 `~/.hermes/config.yaml` 中列出需要额外加载的文件：

```yaml
terminal:
  shell_init_files:
    - ~/.zshrc                     # zsh users: pulls zsh-managed PATH into the bash snapshot
    - ~/.nvm/nvm.sh                # direct nvm init (works regardless of shell)
    - /etc/profile.d/cargo.sh      # system-wide rc files
  # When this list is set, the default ~/.bashrc auto-source is NOT added —
  # include it explicitly if you want both:
  #   - ~/.bashrc
  #   - ~/.zshrc
```

缺失的文件会被静默跳过。配置加载是在 bash 环境中进行的，因此那些依赖仅 zsh 才支持的语法的文件可能会引发错误——如果这是您所担心的问题，建议直接调用用于设置 PATH 的部分内容（例如 nvm 的 `nvm.sh` 文件），而非整个 rc 文件。

如需禁用自动加载功能（仅遵循严格的登录 shell 规则）：

```yaml
terminal:
  auto_source_bashrc: false
```

#### `uv: 命令未找到`

**原因：** 未安装 `uv` 包管理器，或其路径未添加到系统环境变量 PATH 中。

**解决方案：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

#### 安装过程中出现权限被拒绝的错误

**原因：** 没有足够的权限写入安装目录。

**解决方案：**
```bash
# Don't use sudo with the installer — it installs to ~/.local/bin
# If you previously installed with sudo, clean up:
sudo rm /usr/local/bin/hermes
# Then re-run the standard installer
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### 提供商与模型相关问题

#### 智能体称“Hermes策略”或“Hermes规范”拒绝了我的请求

模型无法准确说明拒绝请求的具体原因。如果仅在助手的文字描述中出现拒绝信息，那么其声称是隐藏的Hermes运行时策略导致的解释，很可能是错误推测，或是所选模型或供应商自行施加的限制。

Hermes的执行机制十分明确：被阻止的工具操作会返回明确标注被拒命令或路径的工具错误信息，而需要审批的操作则会显示审批提示。Hermes不会将这些执行控制隐秘地转化为通用的内容拒绝机制。在已配置的情况下，供应商层面的控制仍可能生效，例如Amazon Bedrock Guardrails。

为定位问题根源，请按以下步骤操作：

1. 运行 `/status` 命令，确认当前使用的模型和供应商。
2. 检查拒绝信息中是否包含真实的Hermes工具错误或审批提示。如果仅有文字描述，则不应将模型的说法视为运行时的实据。
3. 使用其他已配置的模型或供应商，在新会话中重新尝试。如果拒绝行为会随模型变化，那属于模型或供应商自身的行为，而非Hermes的执行控制。
4. 如果出现明确的工具错误信息，请在报告问题时使用其完整文本。

有关Hermes官方记录的执行控制规则，请参阅[安全性](/user-guide/security)文档；关于供应商配置的相关信息，请查看[供应商](/integrations/providers)章节。

#### `/model` 命令仅显示一个供应商 / 无法切换供应商

**原因：** 在聊天会话中，`/model` 仅能在你已**配置好的提供者**之间切换。如果你仅设置了 OpenRouter，那么 `/model` 就只会显示该提供者。

**解决方案：** 退出当前会话，然后通过终端使用 `hermes model` 命令来添加新的提供者。

```bash
# Exit the Hermes chat session first (Ctrl+C or /quit)

# Run the full provider setup wizard
hermes model

# This lets you: add providers, run OAuth, enter API keys, configure endpoints
```

通过 `hermes model` 添加新的提供者后，启动一个新的聊天会话——此时 `/model` 命令将显示所有已配置的提供者。

:::提示 快速参考
| 想要执行... | 使用命令 |
|-----------|---------|
| 添加新提供者 | `hermes model`（在终端中输入） |
| 输入/更改 API 密钥 | `hermes model`（在终端中输入） |
| 在会话中进行模型切换 | `/model <名称>`（在会话中输入） |
| 切换到不同的已配置提供者 | `/model provider:模型名`（在会话中输入） |
:::

#### API 密钥无效

**原因：** 密钥缺失、已过期、设置错误，或对应错误的提供者。

**解决方案：**
```bash
# Check your configuration
hermes config show

# Re-configure your provider
hermes model

# Or set directly
hermes config set OPENROUTER_API_KEY sk-or-v1-xxxxxxxxxxxx
```

:::warning
请确保密钥与对应的提供商匹配。OpenAI 密钥无法用于 OpenRouter，反之亦然。请检查 `~/.hermes/.env` 文件中是否存在冲突的配置项。
:::

#### 模型不可用 / 未找到模型

**原因：** 模型标识符有误，或该模型在您的提供商处不可用。

**解决方案：**
```bash
# List available models for your provider
hermes model

# Set a valid model
hermes config set model.default anthropic/claude-opus-4.7

# Or specify per-session
hermes chat --model openrouter/meta-llama/llama-3.1-70b-instruct
```

#### 速率限制（429错误）

**原因：** 您已超出所选服务提供商的速率限制。

**解决方案：** 稍等片刻后重试。若需持续使用，可考虑：
- 升级您的服务提供商套餐
- 更换为其他模型或服务提供商
- 使用 `hermes chat --provider <alternative>` 指定其他后端进行请求

#### 上下文长度超出限制

**原因：** 对话内容过长，超出了模型的上下文窗口容量，或者Hermes检测到的模型上下文长度有误。

**解决方案：**
```bash
# Compress the current session
/compress

# Or start a fresh session
hermes chat

# Use a model with a larger context window
hermes chat --model openrouter/google/gemini-3-flash-preview
```

如果在首次进行长对话时出现此问题，可能是Hermes为你的模型设置了错误的上下文长度。请查看其检测结果：

查看CLI启动行——上面会显示检测到的上下文长度（例如：`📊 Context limit: 128000 tokens`）。你也可以在会话过程中使用`/usage`命令进行查询。

**对于那些静默无响应而非报错的本地服务器（如llama.cpp、Ollama）**：当某个服务提供商因请求过大而拒绝处理时，Hermes会压缩对话内容并重新构建请求。在再次尝试之前，Hermes会重新测量*完整*的重建请求（包括系统提示词、工具结构及消息内容），如果仍超过阈值，则会进一步执行压缩操作。如果请求依然无法适配，对话将会以`Context length exceeded: compression could not reduce the rebuilt request below the safe threshold`这样的信息结束，而不会发送过大的请求导致llama.cpp静默截断（服务器日志中会显示`stop processing: n_tokens = 65535, truncated = 1`）。遇到此类情况时，解决方案几乎总是调整上述配置的`context_length`，使其与服务器实际的 `-c` / `--ctx-size` 参数保持一致。

若要修正上下文长度的检测问题，可直接手动设置该值：

```yaml
# In ~/.hermes/config.yaml
model:
  default: your-model-name
  context_length: 131072  # your model's actual context window
```

或者，对于自定义端点，可在对应提供者的条目中为每个模型单独添加。

```yaml
providers:
  my-server:
    api: "http://localhost:11434/v1"
    models:
      qwen3.5:27b:
        context_length: 64000
```

（旧配置使用传统的 `custom_providers:` 列表——该格式仍受支持，且会自动迁移为 `providers:`。）

如需了解自动检测的原理及所有覆盖选项，请参阅[上下文长度检测](../integrations/providers.md#context-length-detection)。

---

### 终端相关问题

#### 命令被判定为危险操作而被阻止

**原因：** Hermes检测到可能造成破坏的命令（例如 `rm -rf`、`DROP TABLE`）。这是出于安全考虑的机制。

**解决方案：** 当系统提示时，请仔细查看该命令，然后输入 `y` 表示批准。您还可以：
- 要求智能体使用更安全的替代方案
- 在[安全文档](../user-guide/security.md)中查看所有被标记为危险的操作模式列表

:::tip
这是按预期设计的——Hermes绝不会默默执行具有破坏性的命令。提示信息会明确显示即将执行的操作内容。
:::

#### 通过消息网关无法使用 `sudo`

**原因：** 消息网关在无交互式终端的环境下运行，因此无法提示输入密码。

**解决方案：**
- 避免在消息交互中使用 `sudo`——请让智能体寻找替代方案
- 如果必须使用 `sudo`，可在 `/etc/sudoers` 中为特定命令配置无密码 sudo权限
- 或者通过终端界面执行管理任务：`hermes chat`

#### Docker后端无法连接

**原因：** Docker守护进程未运行，或当前用户缺乏相应权限。

**解决方案：**
```bash
# Check Docker is running
docker info

# Add your user to the docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker run hello-world
```

### 消息传递问题

#### 机器人无响应消息

**原因：** 机器人未运行、未获得授权，或您的用户不在允许列表中。

**解决方案：**
```bash
# Check if the gateway is running
hermes gateway status

# Start the gateway
hermes gateway start

# Check logs for errors
cat ~/.hermes/logs/gateway.log | tail -50
```

#### 消息无法送达

**原因：** 网络问题、机器人令牌已过期，或平台 webhook 配置错误。

**解决方案：**
- 使用 `hermes gateway setup` 检查机器人令牌是否有效
- 查看网关日志：`cat ~/.hermes/logs/gateway.log | tail -50`
- 对于基于 webhook 的平台（如 Slack、WhatsApp），需确保您的服务器可被外部访问

#### 允许列表设置混乱——谁可以与机器人交互？

**原因：** 授权模式决定了哪些用户具有访问权限。

**解决方案：**

| 模式 | 工作原理 |
|------|----------|
| **允许列表** | 仅配置文件中列出的用户 ID 可以进行交互 |
| **私信配对** | 首个在私信中发送消息的用户将获得独占访问权 |
| **开放模式** | 任何人都可交互（不推荐用于生产环境） |

可在 `~/.hermes/config.yaml` 的网关设置部分进行配置。详情请参阅 [消息传递文档](../user-guide/messaging/index.md)。

#### 网关无法启动

**原因：** 缺少依赖项、端口冲突，或令牌配置错误。

**解决方案：**
```bash
# Install core messaging gateway dependencies
cd ~/.hermes/hermes-agent && uv pip install -e ".[messaging]"  # Telegram, Discord, Slack, and shared gateway deps

# Check for port conflicts
lsof -i :8080

# Verify configuration
hermes config show
```

#### WSL环境：网关频繁断开连接或`hermes gateway start`命令执行失败

**原因：** WSL对systemd的支持不够稳定。许多WSL2安装并未启用systemd，即便已启用，相关服务在WSL重启或Windows系统进入待机状态时也可能会丢失。

**解决方案：** 改为使用前台模式，而非依赖systemd服务：

```bash
# Option 1: Direct foreground (simplest)
hermes gateway run

# Option 2: Persistent via tmux (survives terminal close)
tmux new -s hermes 'hermes gateway run'
# Reattach later: tmux attach -t hermes

# Option 3: Background via nohup
nohup hermes gateway run > ~/.hermes/logs/gateway.log 2>&1 &
```

如果您仍想尝试使用 systemd，请确保其已启用：

1. 打开 `/etc/wsl.conf` 文件（如果不存在则创建该文件）
2. 添加以下内容：
   ```ini
   [boot]
   systemd=true
   ```
3. 通过 PowerShell 执行：`wsl --shutdown`  
4. 重新打开 WSL 终端  
5. 验证结果：`systemctl is-system-running` 的输出应为 “running” 或 “degraded”  

:::提示：实现 Windows 启动时自动启动  
为确保稳定自动启动，可利用 Windows 任务计划程序在用户登录时同时启动 WSL 及网关：  
1. 创建一个任务，执行命令 `wsl -d Ubuntu -- bash -lc 'hermes gateway run'`  
2. 将该任务设置为在用户登录时触发  
:::  

#### macOS：网关无法检测到 Node.js / ffmpeg 等工具  

**原因：** launchd 服务继承的路径环境变量（`/usr/bin:/bin:/usr/sbin:/sbin`）较为简略，其中不包含 Homebrew、nvm、cargo 以及其他用户安装的工具目录。这通常会导致 WhatsApp 集成功能失效（“未找到 node”）或语音转录功能异常（“未找到 ffmpeg”）。  

**解决方案：** 当您执行 `hermes gateway install` 时，网关会自动记录当前的 shell 路径环境变量。如果您在安装网关之后才安装了相关工具，请重新运行安装命令，以便网关能获取到更新后的路径信息：

```bash
hermes gateway install    # Re-snapshots your current PATH
hermes gateway start      # Detects the updated plist and reloads
```

您可以验证该 plist 文件中是否包含正确的 PATH：
```bash
/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:PATH" \
  ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

### 性能问题

#### 响应缓慢

**原因：** 模型规模过大、API服务器距离较远，或系统提示词过长且包含大量工具调用。

**解决方案：**
- 尝试使用更快/更小的模型：`hermes chat --model openrouter/meta-llama/llama-3.1-8b-instruct`
- 减少激活的工具集数量：`hermes chat -t "terminal"`
- 检查与服务提供商之间的网络延迟
- 对于本地模型，请确保拥有足够的GPU显存

#### 标记使用量过高

**原因：** 对话时间过长、系统提示词过于冗长，或大量工具调用不断累积上下文信息。

**解决方案：**
```bash
# See exactly what the fixed prompt costs — breakdown by block
# (system prompt, skills index, memory, tool schemas). Runs offline.
hermes prompt-size

# Compress the conversation to reduce tokens
/compress

# Check session token usage
/usage
```

如果在您尚未输入任何内容时，基准值就已经很高，那便是固定的提示词预算——即每次调用时都会发送的系统提示词以及工具结构。您可以运行 [`hermes prompt-size`](/reference/cli-commands#hermes-prompt-size) 命令来检测该数值，随后进行优化：禁用不使用的工具集（通过 `hermes tools` 命令），并卸载或禁用不必要的技能（通过 `hermes skills` 命令）。

:::提示
在长时间对话中，请定期使用 `/compress` 命令。它能够汇总对话历史，在保留上下文的同时显著减少Token使用量。
:::

#### 会话时长过长

**原因：** 过长的对话会积累大量消息和工具输出，从而接近上下文限制。

**解决方案：**
```bash
# Compress current session (preserves key context)
/compress

# Start a new session with a reference to the old one
hermes chat

# Resume a specific session later if needed
hermes chat --continue
```

### MCP 相关问题

#### MCP 服务器无法连接

**原因：** 未找到服务器二进制文件、命令路径错误，或缺少运行时环境。

**解决方案：**
```bash
# Ensure MCP dependencies are installed (already included in standard install)
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

# For npm-based servers, ensure Node.js is available
node --version
npx --version

# Test the server manually
npx -y @modelcontextprotocol/server-filesystem /tmp
```

请验证您的 `~/.hermes/config.yaml` 文件中的 MCP 配置：
```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"]
```

#### MCP服务器未显示工具

**原因：** 服务器已启动但工具发现失败，工具被配置文件过滤掉了，或者该服务器不支持您期望的MCP功能。

**解决方案：**
- 检查网关/代理日志中的MCP连接错误信息
- 确保服务器能够响应`tools/list` RPC方法
- 查看该服务器下的`tools.include`、`tools.exclude`、`tools.resources`、`tools.prompts`或`enabled`等配置项
- 请注意，资源/提示词类实用工具仅会在会话实际支持相应功能时才会被注册
- 修改配置后请使用 `/reload-mcp` 命令重新加载配置

```bash
# Verify MCP servers are configured
hermes config show | grep -A 12 mcp_servers

# Restart Hermes or reload MCP after config changes
hermes chat
```

相关参考：  
- [MCP（模型上下文协议）](/user-guide/features/mcp)  
- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)  
- [MCP 配置参考](/reference/mcp-config-reference)  

#### MCP 超时错误  

**原因：** MCP 服务器响应时间过长，或在执行过程中崩溃。  

**解决方案：**  
- 若支持，可在 MCP 服务器配置中增加超时时间；  
- 检查 MCP 服务器进程是否仍在运行；  
- 对于远程 HTTP MCP 服务器，需检查网络连接状况。  

:::warning  
如果 MCP 服务器在处理请求时崩溃，Hermes 会报告超时错误。请查看服务器自身的日志（而不仅仅是 Hermes 的日志），以定位根本原因。  
:::  

---

## 配置文件  

### 配置文件与直接设置 HERMES_HOME 有何不同？  

配置文件是建立在 `HERMES_HOME` 之上的管理层。虽然你可以在每次执行命令前手动设置 `HERMES_HOME=/some/path`，但配置文件会自动处理所有相关细节：创建目录结构、生成 Shell 别名（如 `hermes-work`）、在 `~/.hermes/active_profile` 中记录当前激活的配置文件，以及自动同步所有配置文件中的技能更新。此外，它们还与制表补全功能集成，让你无需记住路径。  

### 两个配置文件能否共享同一个机器人令牌？  

不能。每个消息平台（如 Telegram、Discord 等）都需要独占一个机器人令牌。如果两个配置文件同时尝试使用同一令牌，第二个通道将无法连接。建议为每个配置文件创建独立的机器人——对于 Telegram，可联系 [@BotFather](https://t.me/BotFather) 创建更多机器人。

### 配置文件之间会共享内存或会话吗？

不会。每个配置文件都有独立的内存存储、会话数据库以及技能目录，彼此完全隔离。如果您希望基于现有的内存和会话创建新配置文件，可以使用 `hermes profile create newname --clone-all` 命令复制当前配置文件中的所有内容；或者添加 `--clone-from <profile>` 参数来指定从某个特定配置文件进行复制。

正是由于这种隔离机制，才绝不能让两个代理同时操作*同一个*配置文件或Hermes主目录：因为它们会自动互相写入内存，且每个代理在会话启动时都会加载另一个代理的写入内容，从而导致存储状态在每次会话后逐渐恶化。建议每个配置文件仅对应一个代理；若需在多个代理之间实现真正的内存共享，请使用[外部内存提供器](/user-guide/features/memory-providers)。

### 运行 `hermes update` 时会发生什么？

`hermes update` 会一次性获取最新代码并重新安装依赖项（而非针对每个配置文件分别操作），随后自动将更新后的技能同步到所有配置文件中。您只需运行一次 `hermes update` 即可，它能够覆盖机器上的所有配置文件。

### 我可以运行多少个配置文件？

实际上并没有固定限制。每个配置文件只是 `~/.hermes/profiles/` 目录下的一个子目录。实际可用数量取决于您的磁盘空间以及系统能够处理的并发网关数量（每个网关都是一个轻量级的Python进程）。运行数十个配置文件完全没问题，因为每个空闲的配置文件都不会占用任何资源。

---

## 工作流与模式

### 为不同任务使用不同的模型（多模型工作流）

**场景：** 您日常主要使用 GPT-5.4 进行任务处理，但发现 Gemini 或 Grok 在生成社交媒体内容方面表现更佳。每次都要手动切换模型实在十分繁琐。

**解决方案：委托配置。** Hermes 可以自动将子智能体路由到不同的模型。您可以在 `~/.hermes/config.yaml` 中进行相应设置：

```yaml
delegation:
  model: "google/gemini-3-flash-preview"   # subagents use this model
  provider: "openrouter"                    # provider for subagents
```

现在，当您告诉Hermes“帮我写一篇关于X的Twitter连发帖文”时，它会生成一个`delegate_task`子智能体，该子智能体将在Gemini上运行，而非您的主模型。而您的主要对话仍会在GPT-5.4上进行。

您也可以在提示词中明确说明：“将撰写有关我们产品发布的社交媒体帖文的任务委托出去，实际写作工作由你的子智能体来完成。”这样，智能体就会使用`delegate_task`功能，并自动读取相应的委托配置。

若需在不进行任务委托的情况下临时切换模型，可在CLI中使用 `/model` 命令：

```bash
/model google/gemini-3-flash-preview    # switch for this session
# ... write your content ...
/model openai/gpt-5.4                   # switch back
```

:::warning
每次使用 `/model` 参数切换时，都会重置提示词缓存——由于缓存键中包含了模型信息，因此每次切换后的第一条消息都需要重新读取整个对话历史，从而产生全额的输入费用。在长时间对话中，建议采用子代理机制（子代理可拥有独立的上下文）或开启新会话，而非频繁切换。

:::

如需了解子代理机制的更多细节，请参阅 [子代理委托](../user-guide/features/delegation.md)。

### 在一个 WhatsApp 号码上运行多个代理（单聊天绑定）

**场景：** 在 OpenClaw 中，您可能将多个独立的代理绑定到不同的 WhatsApp 聊天群组——一个用于家庭购物清单群，另一个用于私人聊天。Hermes 能实现这一点吗？

**当前限制：** Hermes 的每个配置文件都需要独立的 WhatsApp 号码和会话。您无法将多个配置文件绑定到同一个 WhatsApp 号码下的不同聊天群组——因为 WhatsApp 桥接组件（Baileys）要求每个号码只能使用一个已认证的会话。

**解决方案：**

1. **使用支持角色切换的单一配置文件。** 创建不同的 `AGENTS.md` 上下文文件，或使用 `/personality` 命令根据不同对话调整智能体的行为。智能体能够识别当前所处的对话环境，并据此做出相应调整。

2. **利用定时任务处理特定任务。** 对于购物清单管理这类需求，可设置定时任务来监控特定对话并自动管理清单——无需单独的智能体。

3. **为每个配置文件分配独立号码。** 若需要完全独立的智能体，可为每个配置文件绑定独立的 WhatsApp 号码。Google Voice 等服务提供的虚拟号码也可用于此目的。

4. **改用 Telegram 或 Discord。** 这些平台更自然地支持按对话绑定功能——每个 Telegram 群组或 Discord 频道都会拥有独立的会话，且可在同一账户下运行多个机器人令牌（每个配置文件对应一个）。

更多详情请参阅 [配置文件](../user-guide/profiles.md) 与 [WhatsApp 设置](../user-guide/messaging/whatsapp.md)。

### 控制 Telegram 中显示的内容（隐藏日志与推理过程）

**场景：** 在 Telegram 中看到的不仅是最终结果，还有网关执行日志、Hermes 的推理过程以及工具调用详情。

**解决方案：** `config.yaml` 文件中的 `display.tool_progress` 设置可控制显示的工具活动程度：

```yaml
display:
  tool_progress: "off"   # options: off, new, all, verbose
```

- **`off`** — 仅显示最终回复。不进行任何工具调用，也不进行推理或记录日志。
- **`new`** — 实时展示新产生的工具调用（以简短的行形式呈现）。
- **`all`** — 显示包括结果在内的所有工具操作记录。
- **`verbose`** — 提供完整细节，涵盖工具参数及输出内容。

对于消息平台而言，通常选择 `off` 或 `new` 即可。修改 `config.yaml` 后，需重启网关才能使更改生效。

此外，若该功能已启用，还可通过 `/verbose` 命令在当前会话中切换显示模式：

```yaml
display:
  tool_progress_command: true   # enables /verbose in the gateway
```

### 在 Telegram 上管理技能（斜杠命令数量限制）

**场景：** Telegram 对斜杠命令的数量限制为 100 个，而您的技能数量已超出此限制。您希望禁用在 Telegram 上不需要的技能，但使用 `hermes skills config` 进行设置似乎并未生效。

**解决方案：** 使用 `hermes skills config` 按平台分别禁用技能。该操作会将相关设置写入 `config.yaml` 文件中：

```yaml
skills:
  disabled: []                    # globally disabled skills
  platform_disabled:
    telegram: [skill-a, skill-b]  # disabled only on telegram
```

修改完成后，**需要重启网关**（执行 `hermes gateway restart` 命令，或直接终止并重新启动）。Telegram 机器人会在启动时重新构建命令菜单。

:::提示
为确保不超过数据包大小限制，描述过长的技能在 Telegram 菜单中会被截断至40个字符以内。如果某些技能未显示，问题可能出在整体数据包大小上，而非100条命令的限制——禁用未使用的技能可同时解决这两个问题。
:::

### 共享线程会话（多用户，同一对话）

**场景：** 您拥有一个 Telegram 或 Discord 线程，其中有多人提及该机器人。您希望将该线程中的所有提及内容整合为同一个共享对话，而非为每位用户创建独立的会话。

**当前行为：** 在大多数平台上，Hermes 会根据用户 ID 创建会话，因此每位用户都会拥有独立的对话上下文。这是出于隐私保护和上下文隔离的考虑而设计的。

**解决方案：**

1. **使用 Slack。** Slack 的会话是基于线程而非用户来划分的。同一线程中的多名用户可共享同一个对话——这正是您所期望的效果。这也是最合适的方案。

2. **创建仅包含一名用户的群组聊天。** 如果指定某人为“操作员”负责转达问题，那么会话就能保持统一，其他人则可以查看对话内容。

3. **使用 Discord 频道。** Discord 的会话是基于频道来划分的，因此同一频道中的所有用户都能共享上下文。请为该共享对话创建专用频道。

### 将 Hermes 导出到另一台机器

**场景：** 您已在某台机器上构建了技能、定时任务以及记忆体，现在希望将所有内容迁移至一台新的专用 Linux 服务器上。

**解决方案：**

1. 在新机器上安装 Hermes Agent：
   ```bash
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```

2. 在**源机器**上创建完整备份：
   ```bash
   hermes backup
   ```
该操作会将您整个`~/.hermes/`目录中的所有内容——包括配置文件、API密钥、记忆数据、技能信息、会话记录以及用户配置——打包成一个压缩包，并存放在您的用户主目录下，文件名为`~/hermes-backup-<timestamp>.zip`。

3. 将该压缩包复制到新机器上并导入即可。
   ```bash
   # On the source machine
   scp ~/hermes-backup-<timestamp>.zip newmachine:~/

   # On the new machine
   hermes import ~/hermes-backup-<timestamp>.zip
   ```

4. 在新机器上运行 `hermes setup` 命令，以验证 API 密钥和提供商配置是否正常工作。

### 将单个配置文件迁移至另一台机器

**场景：** 您希望迁移或共享某个特定的配置文件，而非整个安装包。

```bash
# On the source machine
hermes profile export work ./work-backup.tar.gz

# Copy the file to the target machine, then:
hermes profile import ./work-backup.tar.gz work
```

导入的配置文件将包含导出版本中的所有配置、记忆数据、会话记录以及技能。如果新机器的设置有所不同，您可能需要更新路径或重新向服务提供商进行身份验证。

### `hermes backup` 与 `hermes profile export` 的区别

| 功能 | `hermes backup` | `hermes profile export` |
| :--- | :--- | :--- |
| **适用场景** | **整台机器迁移** | **移植/共享特定配置文件** |
| **覆盖范围** | 全局（整个 `~/.hermes` 目录） | 局部（单个配置文件目录） |
| **包含内容** | 所有配置文件、全局配置、API密钥、会话记录 | 单个配置文件：SOUL.md、记忆数据、会话记录、技能 |
| **凭证信息** | **包含**（`.env` 和 `auth.json` 文件） | **不包含**（为确保安全共享，这些文件会被移除） |
| **文件格式** | `.zip` | `.tar.gz` |

**手动备份方案（rsync）：** 如果您希望直接复制文件，可排除代码仓库目录：
```bash
rsync -av --exclude='hermes-agent' ~/.hermes/ newmachine:~/.hermes/
```

:::提示
即使Hermes正在运行中，`hermes backup`命令也能生成一致的快照。而恢复后的归档文件不会包含诸如`gateway.pid`和`cron.pid`这类本地运行时的文件。
:::

### 安装完成后重新加载shell时出现权限被拒绝的错误

**场景：** 运行完Hermes安装程序后，执行`source ~/.zshrc`时会收到权限被拒绝的错误提示。

**原因：** 通常是由于`~/.zshrc`（或`~/.bashrc`）的文件权限设置不正确，或者安装程序无法正常向该文件写入内容所导致的。这并非Hermes特有的问题，而是shell配置文件的权限问题。

**解决方案：**
```bash
# Check permissions
ls -la ~/.zshrc

# Fix if needed (should be -rw-r--r-- or 644)
chmod 644 ~/.zshrc

# Then reload
source ~/.zshrc

# Or just open a new terminal window — it picks up PATH changes automatically
```

如果安装程序已添加了PATH路径行，但权限设置有误，您可以手动进行添加：
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### 首次运行代理时出现 400 错误

**场景：** 设置过程顺利完成，但在首次尝试聊天时却因 HTTP 400 错误而失败。

**原因：** 通常是由于模型名称不匹配——所配置的模型在您的服务提供商处并不存在，或者 API 密钥没有访问该模型的权限。

**解决方案：**
```bash
# Check what model and provider are configured
hermes config show | head -20

# Re-run model selection
hermes model

# Or test with a known-good model
hermes chat -q "hello" --model anthropic/claude-opus-4.7
```

如果使用 OpenRouter，请确保您的 API 密钥拥有足够的额度。从 OpenRouter 返回的 400 错误通常意味着该模型需要付费套餐，或是模型 ID 存在拼写错误。

---

## 仍然无法解决？

如果您的问题未在此处得到解答：

1. **搜索现有问题：** [GitHub Issues](https://github.com/NousResearch/hermes-agent/issues)
2. **向社区寻求帮助：** [Nous Research Discord](https://discord.gg/nousresearch)
3. **提交错误报告：** 请附上您的操作系统版本、Python 版本（`python3 --version`）、Hermes 版本（`hermes --version`）以及完整的错误信息。
