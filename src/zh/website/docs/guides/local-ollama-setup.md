---
sidebar_position: 9
title: "Run Hermes Locally with Ollama — Zero API Cost"
description: "Step-by-step guide to running Hermes Agent entirely on your own machine with Ollama and open-weight models like Gemma 4, no cloud API keys or paid subscriptions needed"
---

# 使用 Ollama 在本地运行 Hermes —— 零 API 费用

## 问题所在

云端的 LLM API 按令牌收费。一次长时间的编码任务可能就需要花费 5 到 20 美元。对于个人项目、学习或涉及隐私的工作而言，这些费用会不断累积——而且所有对话内容都会被发送给第三方。

## 本指南的解决方案

你将能够完全在自己的硬件上搭建 Hermes Agent，以 [Ollama](https://ollama.com) 作为模型后端。无需 API 密钥，无需订阅服务，数据也不会离开你的机器。配置完成后，Hermes 的使用方式与在 OpenRouter 或 Anthropic 上一致——支持终端命令、文件编辑、网页浏览、任务委托等功能——只不过模型是在本地运行的。

完成设置后，你将拥有：

- 由 Ollama 提供的一个或多个开源模型
- 将 Hermes 连接到 Ollama 作为自定义端点
- 一个可正常工作的本地智能体，能够编辑文件、执行命令并浏览网页
- 可选：一个完全由你的硬件驱动的 Telegram/Discord 机器人

## 所需条件

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| **内存** | 8 GB（用于 30 亿参数模型） | 32 GB以上（用于 270 亿参数及以上模型） |
| **存储空间** | 5 GB 空闲空间 | 30 GB以上（用于部署多个模型） |
| **CPU** | 4 核心 | 8 核心以上（推荐 AMD EPYC、Ryzen 或 Intel Xeon 系列） |
| **GPU** | 不需要 | 配备 8 GB 以上显存的 NVIDIA GPU 能显著提升性能 |

:::提示 仅使用 CPU 也可以运行，但响应速度会较慢
Ollama 支持在仅配备 CPU 的服务器上运行。在现代 8 核 CPU 上，90 亿参数模型的处理速度约为每秒 10 个令牌；而 310 亿参数模型在 CPU 上的速度更慢（约每秒 2–5 个令牌），每次响应需要 30–120 秒，但仍然可以正常使用。GPU 能极大提升性能。对于仅使用 CPU 的场景，可通过环境变量延长 API 超时时间（该参数不在 `config.yaml` 文件中）：

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

| 模型 | 磁盘大小 | 所需内存 | 是否支持工具调用 | 最佳适用场景 |
|-------|---------|----------|----------------|------------|
| `gemma4:31b` | 约20 GB | 24+ GB | 是 | 最高质量——强大的工具使用能力和推理能力 |
| `gemma2:27b` | 约16 GB | 20+ GB | 否 | 对话任务，不支持工具调用 |
| `gemma2:9b` | 约5 GB | 8+ GB | 否 | 快速聊天、问答——无法调用工具 |
| `llama3.2:3b` | 约2 GB | 4+ GB | 否 | 轻量级快速回复场景 |

:::警告 工具调用至关重要
Hermes是一款**智能代理型**助手——它能够通过工具调用来编辑文件、执行命令以及浏览网页。不支持工具调用的模型仅能进行对话，无法执行实际操作。若要获得完整的Hermes体验，请选用支持工具调用的模型（如`gemma4:31b`）。
:::

现在拉取您选定的模型：

```bash
ollama pull gemma4:31b
```

:::info 多模型支持  
您可以使用 `/model` 命令在 Hermes 中加载多个模型，并随时在它们之间切换。Ollama 会根据需求将当前使用的模型加载到内存中，同时自动释放闲置模型。  
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

就是这样。现在您正在运行一个完全在本地运行的智能体。快试试看吧：

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
对于需要完整代理功能的任务（如文件编辑、命令执行、网页浏览），目前支持工具调用的最佳本地模型仍是`gemma4:31b`。您可以查看[Ollama的模型库](https://ollama.com/library)以获取更多最新模型——支持工具调用的功能正在迅速扩展。
:::

您可以在会话进行中随时切换模型：

```
/model gemma2:9b
```

## 第6步：优化性能以提升速度

### 扩大Ollama的上下文窗口大小

默认情况下，Ollama使用的上下文长度为2048个标记。而Hermes在通过工具执行智能体任务时，至少需要64,000个标记的上下文容量：

```bash
# Create a Modelfile that extends context
cat > /tmp/Modelfile << 'EOF'
FROM gemma4:31b
PARAMETER num_ctx 64000
EOF

ollama create gemma4-64k -f /tmp/Modelfile
```

接着，请更新您的 Hermes 配置，将模型名称设置为 `gemma4-64k`。

### 保持模型加载状态

默认情况下，Ollama 会在模型 5 分钟无操作后自动卸载它。对于需要持续运行的网关机器人，请确保其模型保持加载状态：

```bash
# Set keep-alive to 24 hours
curl http://localhost:11434/api/generate \
  -d '{"model": "gemma4:31b", "keep_alive": "24h"}'
```

或者可在 Ollama 的环境中进行全局设置：

```bash
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_KEEP_ALIVE=24h"
```

### 使用 GPU 卸载功能（如可用）

如果您配备了 NVIDIA GPU，Ollama 会自动将模型层卸载到该显卡上。具体操作方式请查阅：

```bash
ollama ps   # Shows which model is loaded and how many GPU layers
```

在配备 12 GB GPU 的设备上运行 31B 模型时，虽然只能实现部分卸载（约 40 层在 GPU 上处理，其余在 CPU 上处理），但仍能显著提升速度。

## 第 7 步：以网关机器人形式运行（可选）

当 Hermes 能在本地 CLI 环境中正常运行后，你可以将其作为 Telegram 或 Discord 机器人对外提供服务——所有运算依然在你的硬件上完成。

### Telegram

1. 通过 [@BotFather](https://t.me/BotFather) 创建一个机器人并获取其令牌
2. 将相关配置添加到你的 `~/.hermes/config.yaml` 文件中：

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

现在就可以在 Telegram 上向你的机器人发送消息——它将使用你本地的模型来回复。

### Discord

1. 在 [discord.com/developers](https://discord.com/developers/applications) 创建一个 Discord 应用程序
2. 将其添加到配置中：

```yaml
platforms:
  discord:
    enabled: true
    token: "YOUR_DISCORD_BOT_TOKEN"
```

3. 启动命令：`hermes gateway`

## 第8步：设置备用方案（可选）

本地模型在处理复杂任务时可能会遇到困难。可以配置一个云端备用方案，仅在本地模型无法正常工作时启用：

```yaml
model:
  default: "gemma4:31b"
  provider: "custom"
  base_url: "http://localhost:11434/v1"

fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

如此一来，您90%的使用量均可免费（在本地完成），仅那些复杂任务才会调用付费API。

## 故障排除

### 启动时出现“连接被拒绝”错误

说明Ollama尚未运行。请先启动它：

```bash
sudo systemctl start ollama
# or
ollama serve
```

### 响应速度过慢

- **检查模型大小与内存容量：** 如果模型的内存需求超过可用内存，它会将数据切换到磁盘存储。此时可考虑使用更小的模型或增加内存。
- **查看 `ollama ps` 输出：** 如果没有 GPU 层被卸载，响应速度将受 CPU 性能限制。对于仅配备 CPU 的服务器，这是正常现象。
- **减少上下文长度：** 过长的对话会降低推理速度。建议定期使用 `/compress` 命令压缩上下文，或在配置中设置更低的压缩阈值。

### 模型不执行工具调用

较小的模型（3B、7B）有时会忽略工具调用指令，仅生成纯文本而非结构化的函数调用。解决方案包括：

- **使用更大的模型**——`gemma4:31b` 或 `gemma2:27b` 在处理工具调用方面表现远优于 3B/7B 模型。
- **Hermes 具备自动修复功能**——它能检测到格式错误的工具调用并尝试自动修正。
- **设置备用方案**——如果本地模型连续失败 3 次，Hermes 会自动切换到云服务提供商。

### 上下文窗口错误

Ollama 的默认上下文长度为 2048 个标记，对于智能体任务来说过于有限。可参考[步骤 6](#step-6-optimize-for-speed)了解如何增加上下文长度。

## 成本对比

基于典型的编程任务（输入约 10 万标记，输出约 2 万标记），在本地运行相较于使用云 API 能节省的成本如下：

| 服务提供商 | 每次任务成本 | 每月成本（每日使用） |
|----------|-----------------|---------------------|
| Anthropic Claude Sonnet | 约 0.80 美元 | 约 24 美元 |
| OpenRouter (GPT-4o) | 约 0.60 美元 | 约 18 美元 |
| **Ollama（本地运行）** | **0 美元** | **0 美元** |

您唯一的成本是电力消耗——根据硬件不同，每次任务的成本大约在 0.01–0.05 美元之间。

## 本地运行的优势场景

- **文件编辑与代码生成**——9B 及以上规模的模型能很好地处理这类任务。
- **终端命令执行**——无论使用何种模型，Hermes 都会封装命令、执行并读取输出结果。
- **网页浏览**——浏览器工具负责获取网页内容，模型仅负责解析结果。
- **定时任务与计划任务**——运行方式与云环境完全相同。
- **多平台接入**——Telegram、Discord、Slack 等平台均可与本地模型配合使用。

## 云模型的优势场景

- **极其复杂的多步骤推理**——70B 及以上规模或 Claude Opus 等云模型在处理这类任务时表现更出色。
- **更长的上下文窗口**——云模型可支持 10 万至 100 万标记的上下文长度；除非进行特殊配置，否则本地运行环境的默认值通常低于 Hermes 的 64K 最低要求。
- **长文本响应的速度**——对于较长的生成内容，云端的推理速度优于仅依赖 CPU 的本地环境。

最佳实践是：日常任务使用本地模型，而面对复杂任务则启用云服务作为备用方案。
