---
sidebar_position: 2
title: "Run Local LLMs on Mac"
description: "Set up a local OpenAI-compatible LLM server on macOS with llama.cpp or MLX, including model selection, memory optimization, and real benchmarks on Apple Silicon"
---

# 在 Mac 上运行本地大语言模型

:::提示 桌面端用户：有一步到位的方案  
在 Hermes 桌面应用中，通过 **设置 → 提供商 → 本地模型** 即可自动为您安装并管理本地 llama.cpp 服务器——包括模型下载、内存优化以及上下文长度调整等功能。详情请参阅 [本地模型](/user-guide/local-models)。本指南适用于需要手动配置的场景：如使用 MLX 格式、自定义构建，或自行运行的服务器。  
:::

本指南将指导您在 macOS 上运行具备 OpenAI 兼容 API 的本地大语言模型服务器。您将享有完全的隐私保护、零 API 费用，同时在 Apple Silicon 平台上还能获得出人意料的出色性能。

我们将介绍两种后端方案：

| 后端 | 安装方式 | 最佳适用场景 | 格式 |
|------|----------|--------------|------|
| **llama.cpp** | `brew install llama.cpp` | 最快的首次生成时间，支持量化 KV 缓存以节省内存 | GGUF |
| **omlx** | [omlx.ai](https://omlx.ai) | 最快的文本生成速度，具备原生 Metal 优化功能 | MLX（safetensors） |

这两种后端均提供兼容 OpenAI 的 `/v1/chat/completions` 接口。Hermes 支持任意一种后端——只需将其配置为指向 `http://localhost:8080` 或 `http://localhost:8000` 即可。  
:::信息 仅适用于 Apple Silicon 平台  
本指南针对搭载 Apple Silicon（M1 及更高版本）的 Mac 编写。Intel 架构的 Mac 可以使用 llama.cpp，但无法利用 GPU 加速，性能将会大幅下降。  
:::

---

## 选择模型

作为入门推荐，我们建议使用 **Qwen3.5-9B**——这是一款强大的推理模型，经过量化处理后可在 8GB 及以上的统一内存中流畅运行。

| 变体 | 磁盘占用大小 | 所需内存（128K上下文） | 后端引擎 |
|---------|-------------|---------------------------|---------|
| Qwen3.5-9B-Q4_K_M (GGUF) | 5.3 GB | 量化后的KV缓存约需10 GB | llama.cpp |
| Qwen3.5-9B-mlx-lm-mxfp4 (MLX) | 约5 GB | 约12 GB | omlx |

**内存估算规则：** 模型大小 + KV缓存。一个9B的Q4量化模型约占5 GB空间；在128K上下文条件下，Q4量化格式的KV缓存还会额外占用约4-5 GB。若使用默认的f16格式KV缓存，内存需求则会上升至约16 GB。在内存受限的系统上，llama.cpp中的量化KV缓存功能是节省内存的关键手段。

对于规模更大的模型（27B、35B），则需要32 GB及以上的统一内存。而对于8-16 GB内存配置的机器而言，9B模型则是最佳选择。

---

## 选项A：llama.cpp

llama.cpp是最具跨平台性的本地大语言模型运行时引擎。在macOS系统上，它可直接利用Metal技术实现GPU加速。

### 安装方式

```bash
brew install llama.cpp
```

这样你就可以全局使用 `llama-server` 命令了。

### 下载模型

你需要一个 GGUF 格式的模型。最便捷的获取方式是通过 `huggingface-cli` 从 Hugging Face 平台下载：

```bash
brew install huggingface-cli
```

接下来下载：

```bash
huggingface-cli download unsloth/Qwen3.5-9B-GGUF Qwen3.5-9B-Q4_K_M.gguf --local-dir ~/models
```

:::提示：受权限限制的模型
Hugging Face 上的部分模型需要身份验证。如果遇到 401 或 404 错误，请先运行 `huggingface-cli login`。
:::

### 启动服务器

```bash
llama-server -m ~/models/Qwen3.5-9B-Q4_K_M.gguf \
  -ngl 99 \
  -c 131072 \
  -np 1 \
  -fa on \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --host 0.0.0.0
```

以下是各参数的功能说明：

| 参数 | 用途 |
|------|---------|
| `-ngl 99` | 将所有层卸载到 GPU（Metal）上。建议设置较高的数值，以确保没有数据留在 CPU 上。 |
| `-c 131072` | 上下文窗口大小（128K 个标记）。如果内存不足，可降低此数值。 |
| `-np 1` | 并行槽位数。单用户使用时保持为 1 —— 槽位数越多，占用的内存预算就越分散。 |
| `-fa on` | 闪存注意力机制。该功能可减少内存占用，并提升长上下文推理速度。 |
| `--cache-type-k q4_0` | 将键缓存量化为 4 位格式。**这是节省内存的关键手段。** |
| `--cache-type-v q4_0` | 将值缓存量化为 4 位格式。结合上述设置，与使用 f16 格式相比，可减少约 75% 的 KV 缓存内存占用。 |
| `--host 0.0.0.0` | 在所有网络接口上监听请求。如无需网络访问，可使用 `127.0.0.1`。 |

当出现以下提示时，即表示服务器已准备就绪：

```
main: server is listening on http://0.0.0.0:8080
srv  update_slots: all slots are idle
```

### 面向内存受限系统的优化方案

对于内存有限的系统而言，`--cache-type-k q4_0 --cache-type-v q4_0` 这两个参数是至关重要的优化手段。以下是在 128K 上下文长度下的内存占用情况：

| KV 缓存类型 | KV 缓存内存占用（128K 上下文，9B 模型） |
|---------------|--------------------------------------|
| f16（默认值） | 约 16 GB |
| q8_0 | 约 8 GB |
| **q4_0** | **约 4 GB** |

在 8 GB 内存的 Mac 设备上，建议使用 `q4_0` 类型的 KV 缓存，并选择体积更小的模型，同时确保该模型能满足 Hermes 最低 64K 的上下文长度要求。在 16 GB 内存环境下，可轻松支持 128K 上下文长度；而 32 GB 及以上内存则足以运行更大规模的模型或启用多个并行处理槽位。

如果仍出现内存不足的问题，请仅在保证上下文长度不低于 Hermes 最低要求的 64K 的前提下减少上下文长度；否则，可考虑更换为体积更小的模型，或选择量化等级更低的格式（如从 Q4_K_M 改为 Q3_K_M）。

### 进行测试

```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-Q4_K_M.gguf",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }' | jq .choices[0].message.content
```

### 查询模型名称

如果您忘记了模型名称，可以查询模型端点：

```bash
curl -s http://localhost:8080/v1/models | jq '.data[].id'
```

## 方案 B：通过 omlx 使用 MLX

[omlx](https://omlx.ai) 是一款专为 macOS 设计的应用程序，用于管理和提供 MLX 模型。MLX 是苹果公司自研的机器学习框架，针对 Apple Silicon 的统一内存架构进行了优化。

### 安装

从 [omlx.ai](https://omlx.ai) 下载并安装该应用。它提供了模型管理的图形界面以及内置服务器。

### 下载模型

使用 omlx 应用程序浏览并下载模型。搜索 `Qwen3.5-9B-mlx-lm-mxfp4` 并将其下载。模型将存储在本地（通常位于 `~/.omlx/models/` 目录下）。

### 启动服务器

omlx 默认在 `http://127.0.0.1:8000` 地址上提供模型服务。您可以通过应用程序的界面启动服务，或在使用 CLI 的情况下通过命令行启动。

### 测试功能

```bash
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-mlx-lm-mxfp4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }' | jq .choices[0].message.content
```

### 列出可用模型

omlx能够同时加载多个模型进行运行：

```bash
curl -s http://127.0.0.1:8000/v1/models | jq '.data[].id'
```

## 性能基准测试：llama.cpp vs MLX

两项测试均在同一台设备（Apple M5 Max，128 GB统一内存）上展开，使用相同的模型（Qwen3.5-9B），并采用相近的量化级别（GGUF格式为Q4_K_M，MLX格式为mxfp4）。测试共使用了五种不同的提示语，每种提示语运行三次，且为了避免资源竞争，两种后端是依次进行测试的。

### 测试结果

| 指标 | llama.cpp（Q4_K_M） | MLX（mxfp4） | 胜出者 |
|------|-------------------|-------------|--------|
| **TTFT（平均值）** | **67 毫秒** | 289 毫秒 | llama.cpp（快4.3倍） |
| **TTFT（p50值）** | **66 毫秒** | 286 毫秒 | llama.cpp（快4.3倍） |
| **生成速度（平均值）** | 70 个标记/秒 | **96 个标记/秒** | MLX（快37%） |
| **生成速度（p50值）** | 70 个标记/秒 | **96 个标记/秒** | MLX（快37%） |
| **生成512个标记的总时间** | 7.3秒 | **5.5秒** | MLX（快25%） |

### 结果解读

- **llama.cpp**在提示语处理方面表现优异——其闪存注意力机制与量化后的KV缓存架构使得第一个标记的生成时间仅需约66毫秒。对于那些对响应速度要求较高的交互式应用（如聊天机器人、自动补全功能），这一优势尤为显著。

- **MLX**在开始生成后，标记的生成速度可快37%。对于批量处理任务、长文本生成，或是那些更注重整体完成时间而非初始延迟的场景，MLX能更快地完成任务。

- 两种后端的测试结果**极其稳定**——不同次测试之间的差异微乎其微，因此这些数据具有很高的参考价值。

### 应该选择哪一个？

| 使用场景 | 推荐方案 |
|----------|-----------|
| 实时聊天、低延迟工具 | llama.cpp |
| 长文本生成、批量处理 | MLX (omlx) |
| 内存受限环境（8-16 GB） | llama.cpp（量化后的KV缓存表现最佳） |
| 同时部署多个模型 | omlx（内置多模型支持） |
| 最高兼容性需求（包括Linux系统） | llama.cpp |

---

## 连接Hermes

当本地服务器启动后：

```bash
hermes model
```

请选择**自定义端点**，然后按照提示操作。系统会要求输入基础URL和模型名称——请使用您在上一步中配置的后端对应的值。

---

## 超时设置

Hermes能够自动识别本地端点（如localhost、局域网IP），并相应延长其流式处理的超时时间。对于大多数场景而言，无需进行额外配置。

如果您仍然遇到超时错误（例如在性能较弱的硬件上处理过大的上下文数据），可以手动调整流式读取的超时时间：

```bash
# In your .env — raise from the 120s default to 30 minutes
HERMES_STREAM_READ_TIMEOUT=1800
```

| 超时时间 | 默认值 | 本地自动调整 | 环境变量覆盖 |
|---------|--------|--------------|--------------|
| 流式读取（套接字层级） | 120秒 | 提高至1800秒 | `HERMES_STREAM_READ_TIMEOUT` |
| 过期流检测 | 180秒 | 完全禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| API调用（非流式） | 1800秒 | 无需调整 | `HERMES_API_TIMEOUT` |

其中，流式读取超时最容易引发问题——它决定了在套接字层级上接收下一组数据的时间限制。在处理大型上下文时的预填充阶段，本地模型可能在数分钟内都没有输出，正在处理用户提示语。自动检测功能能够透明地解决这一问题。

:::提示 首次无响应通常属于预填充现象，并非程序卡住
Hermes会在每次调用时发送系统提示语和工具结构信息，因此在性能较弱的硬件上，模型在生成响应前可能需要数分钟时间来处理这些提示语，从而导致首次响应时出现沉默。这正是预填充在起作用，并非会话挂起。有关缓解方法，可参阅Ollama指南中的[首次响应缓慢（预填充）](./local-ollama-setup.md#slow-first-response-prefill)，比如保持模型处于加载状态，或使用`hermes prompt-size`功能精简固定提示语长度。
:::
