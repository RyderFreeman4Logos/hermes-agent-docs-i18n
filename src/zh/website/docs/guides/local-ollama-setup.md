---
sidebar_position: 9
title: "Run Hermes Locally with Ollama — Zero API Cost"
description: "Step-by-step guide to running Hermes Agent entirely on your own machine with Ollama and open-weight models like Gemma 4, no cloud API keys or paid subscriptions needed"
---

# 使用 Ollama 在本地运行 Hermes —— 零 API 费用

:::提示 桌面端用户：有一键操作方式  
在 Hermes 桌面应用中，通过 **设置 → 提供商 → 本地模型** 即可自动为您安装并管理本地 llama.cpp 服务器——包括模型下载、内存适配以及上下文长度调整等功能。详情请参阅 [本地模型](/user-guide/local-models)。本指南适用于手动配置场景：即使用 Ollama、以命令行为主的工作流，或您希望自行运行的服务器。  
:::

## 问题所在

云端大型语言模型 API 按令牌收费。一次复杂的编程任务可能需要支付 5 到 20 美元不等的费用。对于个人项目、学习或涉及隐私的工作而言，这些成本会不断累积——而且所有对话内容都会被发送给第三方。

## 本指南的解决方案

您将使用 [Ollama](https://ollama.com) 作为模型后端，在自己的硬件上完整搭建 Hermes Agent 环境。无需 API 密钥，无需订阅服务，数据也不会离开您的设备。配置完成后，Hermes 的功能与在 OpenRouter 或 Anthropic 上使用时完全一致——支持终端命令操作、文件编辑、网页浏览以及任务委托——只不过模型是在本地运行的。

完成设置后，您将获得：

- 由 Ollama 提供的一个或多个开源模型  
- 将 Hermes 连接到 Ollama 的自定义端点  
- 可执行文件编辑、运行命令及浏览网页的本地智能体  
- 可选功能：完全基于您自身硬件运行的 Telegram/Discord 机器人  

## 所需准备

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| **内存** | 8 GB（用于30亿参数模型） | 32 GB以上（用于270亿参数及以上模型） |
| **存储空间** | 剩余5 GB可用空间 | 30 GB以上（用于部署多个模型） |
| **CPU** | 4核 | 8核以上（推荐AMD EPYC、Ryzen或Intel Xeon系列处理器） |
| **GPU** | 不需要 | 配备8 GB以上显存的NVIDIA GPU可显著提升运行速度 |

:::提示 仅使用CPU也能运行，但响应速度会较慢
Ollama可在纯CPU服务器上运行。在现代8核CPU上，90亿参数模型的生成速度约为10个token/秒；而310亿参数模型在CPU上的生成速度则更慢（约2–5个token/秒），每次响应需要30–120秒，但依然可以正常使用。GPU能极大提升运行效率。对于纯CPU环境，可通过环境变量延长API超时时间（该参数不在`config.yaml`文件中）：

```bash
# ~/.hermes/.env
HERMES_API_TIMEOUT=1800   # 30 minutes — generous for slow local models
```
:::

## 第一步：安装 Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

验证其是否正在运行：

```bash
ollama --version
curl http://localhost:11434/api/tags   # Should return {"models":[]}
```

## 第2步：拉取模型

请根据您的硬件配置进行选择：

| 模型 | 磁盘大小 | 所需RAM | 是否支持工具调用 | 最佳适用场景 |
|-------|---------|----------|------------------|------------|
| `gemma4:31b` | 约20 GB | 24+ GB | 是 | 最高质量——强大的工具使用能力和推理能力 |
| `gemma2:27b` | 约16 GB | 20+ GB | 否 | 对话任务，不支持工具调用 |
| `gemma2:9b` | 约5 GB | 8+ GB | 否 | 快速聊天、问答——无法调用工具 |
| `llama3.2:3b` | 约2 GB | 4+ GB | 否 | 轻量级快速回复功能 |

:::警告 工具调用至关重要
Hermes是一款**智能代理型**助手——它能够通过工具调用来编辑文件、执行命令以及浏览网页。不支持工具调用的模型仅能进行对话，无法执行任何操作。若要获得完整的Hermes体验，请使用支持工具调用的模型（如`gemma4:31b`）。
:::

拉取您选定的模型：

```bash
ollama pull gemma4:31b
```

:::info 多模型支持
您可以通过 `/model` 命令在 Hermes 中加载多个模型，并随时在它们之间切换。Ollama 会根据需求将当前使用的模型加载到内存中，同时自动卸载处于闲置状态的模型。
:::

验证模型是否正常工作：

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:31b",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 50
  }'
```

您应该会看到一个包含模型回复的 JSON 响应。

## 第 3 步：配置 Hermes

运行 Hermes 配置向导：

```bash
hermes setup
```

当系统提示输入提供者信息时，请选择**自定义端点**，并填写以下内容：

- **基础 URL：** `http://localhost:11434/v1`
- **API 密钥：** 保持空白或输入 `no-key`（Ollama 不需要该密钥）
- **模型：** `gemma4:31b`（或您下载的任意其他模型）

或者，您也可以直接编辑 `~/.hermes/config.yaml` 文件：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"
```

## 第 4 步：开始使用 Hermes

```bash
hermes
```

就这样。现在您正在运行一个完全在本地运行的智能体。快试一试吧：

```
You: List all Python files in this directory and count the lines of code in each

You: Read the README.md and summarize what this project does

You: Create a Python script that fetches the weather for Ho Chi Minh City
```

Hermes将利用终端工具、文件操作以及您本地的模型来完成任务——无需调用云端服务。

## 第5步：为任务选择合适的模型

并非所有任务都需要最强大的模型。以下是实用指南：

| 任务类型 | 推荐模型 | 原因 |
|----------|----------|------|
| 文件编辑、代码处理、终端命令执行 | `gemma4:31b` | 唯一具备稳定工具调用功能的模型 |
| 快速问答（无需使用工具） | `gemma2:9b` | 能够快速响应对话类需求 |
| 轻量级聊天 | `llama3.2:3b` | 响应速度最快，但功能较为有限 |

:::note
对于需要完整代理功能的任务（如文件编辑、命令执行、网页浏览），目前`gemma4:31b`仍是支持工具调用的最佳本地模型选择。您可以查看[Ollama的模型库](https://ollama.com/library)以获取更新型的模型——工具调用功能正在快速扩展中。
:::

您可以在会话进行中随时切换模型：

```
/model gemma2:9b
```

## 第6步：优化速度表现

### 扩大Ollama的上下文窗口大小

默认情况下，Ollama使用的上下文长度为2048个标记。而Hermes在配合工具执行智能体任务时，至少需要64,000个标记的上下文空间：

```bash
# Create a Modelfile that extends context
cat > /tmp/Modelfile << 'EOF'
FROM gemma4:31b
PARAMETER num_ctx 64000
EOF

ollama create gemma4-64k -f /tmp/Modelfile
```

随后，请更新您的 Hermes 配置，将模型名称设置为 `gemma4-64k`。

### 保持模型加载状态

默认情况下，Ollama 会在模型 5 分钟未使用时自动卸载它。若要让网关机器人持续运行，需保持模型处于加载状态：

```bash
# Set keep-alive to 24 hours
curl http://localhost:11434/api/generate \
  -d '{"model": "gemma4:31b", "keep_alive": "24h"}'
```

或者在 Ollama 的环境中进行全局设置：

```bash
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_KEEP_ALIVE=24h"
```

### 使用 GPU 卸载功能（如可用）

如果您拥有 NVIDIA GPU，Ollama 会自动将模型层卸载到该 GPU 上。具体操作方式请查看：

```bash
ollama ps   # Shows which model is loaded and how many GPU layers
```

在配备 12 GB GPU 的设备上运行 31B 模型时，虽然只能实现部分卸载（约 40 层在 GPU 上处理，其余在 CPU 上处理），但仍能显著提升速度。

## 第 7 步：以网关机器人的形式运行（可选）

当 Hermes 能在本地 CLI 环境中正常运行后，您还可以将其作为 Telegram 或 Discord 机器人对外提供服务——所有运算依然在您的硬件上完成。

### Telegram

1. 通过 [@BotFather](https://t.me/BotFather) 创建一个机器人并获取其令牌
2. 将相关配置添加到您的 `~/.hermes/config.yaml` 文件中：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"

platforms:
  telegram:
    enabled: true
    token: "YOUR_TELEGRAM_BOT_TOKEN"
```

3. 启动网关：

```bash
hermes gateway
```

现在就可以在 Telegram 上向你的机器人发送消息——它将使用你本地的模型进行回复。

### Discord

1. 在 [discord.com/developers](https://discord.com/developers/applications) 创建一个 Discord 应用程序
2. 将其添加到配置文件中：

```yaml
platforms:
  discord:
    enabled: true
    token: "YOUR_DISCORD_BOT_TOKEN"
```

3. 启动命令：`hermes gateway`

## 第8步：配置备用方案（可选）

本地模型在处理复杂任务时可能会遇到困难。您可以设置一个云端备用方案，仅在本地模型无法正常工作时启用：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"

fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

这样一来，您90%的使用量都可以免费（在本地处理），只有那些复杂的任务才会调用付费的API。

## 故障排除

### 启动时出现“连接被拒绝”的错误

说明Ollama尚未运行。请先启动它：

```bash
sudo systemctl start ollama
# or
ollama serve
```

### 响应速度缓慢

- **检查模型大小与内存占用：** 如果模型的内存需求超过可用内存，系统会将数据切换到磁盘存储。建议选择更小的模型或增加内存。
- **查看 `ollama ps` 输出：** 如果没有将 GPU 层卸载，响应速度将受 CPU 性能限制。这在仅配备 CPU 的服务器上是正常现象。
- **减少上下文长度：** 过长的对话会降低推理速度。建议定期使用 `/compress` 命令进行压缩，或在配置中设置更低的压缩阈值。

### 首次响应缓慢（预填充阶段）

Hermes 在每次 API 调用时都会先发送固定内容——包括系统提示词以及所有已启用工具的架构信息——然后再处理用户的对话内容。在仅使用 CPU 或内存较小的设备上，处理这些提示词（即预填充阶段）会占据首轮响应的大部分时间：模型可能需要数分钟时间来解析提示词，之后才会以正常速度生成回复。这是正常现象，并非程序卡住。[Mac 环境本地 LLM 使用指南](./local-llm-on-mac.md#timeouts)中也提到了类似情况——在处理较长上下文的预填充阶段，本地模型可能需要数分钟时间来处理提示词而不会产生任何输出——为此 Hermes 会自动将本地端点的流读取超时时间从 120 秒延长至 1800 秒（通过 `HERMES_STREAM_READ_TIMEOUT` 参数设置）。

以下方法可帮助改善问题：

- **保持模型加载状态** — Ollama会在5分钟后自动卸载闲置的模型，并在下次预填充前进行完整重新加载。可设置`OLLAMA_KEEP_ALIVE=24h`（详见[步骤6](#keep-the-model-loaded)）。
- **延长API超时时间** — 在`~/.hermes/.env`文件中设置`HERMES_API_TIMEOUT=1800`（详见[所需准备](#what-you-need)）。
- **检测并精简固定提示词** — 运行`hermes prompt-size`可查看系统提示词及工具结构的字节分布情况，随后通过`hermes tools`禁用未使用的工具集，再通过`hermes skills`卸载不需要的技能。
- **启用GPU卸载功能** — 即使仅部分卸载也能显著提升速度（详见[步骤6](#use-gpu-offloading-if-available)）。

### 模型无法响应工具调用

不支持工具调用的模型会生成纯文本，而非结构化的函数调用。解决方案包括：

- **使用支持工具调用的模型** — 在上述模型中，仅`gemma4:31b`具备可靠的工具调用功能。
- **Hermes具备自动修复功能** — 它能检测到格式错误的工具调用并尝试自动修正。
- **设置备用方案** — 若本地模型连续失败3次，Hermes会自动切换至云服务提供商。
如果模型在回复中直接输出类似 `{"name": "web_search", ...}` 的原始 JSON 数据，而并未真正调用对应工具，这通常是由于*服务器*配置问题，而非模型本身的问题——可能是工具调用功能未被启用，或是工具调用格式未能被正确解析。有关具体解决方案，请参阅文档 [“工具调用以文本形式呈现而非实际执行”](/integrations/providers#tool-calls-appear-as-text-instead-of-executing) 中的服务器级修复方案表（llama.cpp 需要使用 `--jinja` 参数，vLLM 需要使用 `--enable-auto-tool-choice --tool-call-parser hermes` 等参数）。

### 上下文窗口限制问题

默认的 Ollama 上下文长度为 2048 个令牌，对于代理式任务来说过于有限。如需增加上下文长度，请参阅 [第 6 步](#step-6-optimize-for-speed)。

## 成本对比

基于典型的编程任务（输入约 10 万令牌，输出约 2 万令牌），在本地运行相较于使用云 API 可节省的成本如下：

| 提供商 | 每次任务成本 | 每月成本（每日使用） |
|--------|--------------|-------------------|
| Anthropic Claude Sonnet | 约 0.80 美元 | 约 24 美元 |
| OpenRouter (GPT-4o) | 约 0.60 美元 | 约 18 美元 |
| **Ollama（本地运行）** | **0 美元** | **0 美元** |

您唯一的成本便是电力消耗——根据硬件配置不同，每次任务的成本大约在 0.01 至 0.05 美元之间。

## 本地运行的优势

- **文件编辑与代码生成**——90亿参数以上的模型可轻松应对此类任务  
- **终端命令执行**——无论使用何种模型，Hermes都会对命令进行封装、执行并读取输出结果  
- **网页浏览**——浏览器工具负责数据获取，模型仅负责解析返回内容  
- **定时任务与计划任务**——其运行方式与云端环境完全一致  
- **多平台兼容**——Telegram、Discord、Slack等平台均可与本地模型配合使用  

## 为何云端模型更具优势  

- **高度复杂的多步骤推理**——700亿参数以上或类似Claude Opus的云端模型表现更为出色  
- **更长的上下文窗口**——云端模型可支持10万至100万个标记的上下文长度；而本地运行环境默认值通常低于Hermes规定的64千标记最低标准，除非用户自行配置  
- **处理长文本时的速度**——对于需要生成长篇内容的场景，云端推理速度优于仅依赖CPU的本地方案  

最佳实践是：日常任务使用本地模型，而对于复杂任务则配置云端作为备用方案。
