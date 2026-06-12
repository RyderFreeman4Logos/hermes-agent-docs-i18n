---
sidebar_position: 2
title: "Run Local LLMs on Mac"
description: "Set up a local OpenAI-compatible LLM server on macOS with llama.cpp or MLX, including model selection, memory optimization, and real benchmarks on Apple Silicon"
---

# 在 Mac 上运行本地大语言模型

本指南将指导您在 macOS 上使用兼容 OpenAI 的 API 运行本地大语言模型服务器。这样不仅能确保数据完全隐私、无需支付 API 费用，而且在 Apple Silicon 平台上还能获得令人惊喜的出色性能。

我们将介绍两种后端方案：

| 后端 | 安装方式 | 最佳优势 | 数据格式 |
|---------|---------|---------|--------|
| **llama.cpp** | `brew install llama.cpp` | 达到首个输出token的速度最快，支持量化 KV 缓存以降低内存占用 | GGUF |
| **omlx** | [omlx.ai](https://omlx.ai) | 生成 token 的速度最快，具备原生 Metal 优化功能 | MLX (safetensors) |

这两种后端都提供了兼容 OpenAI 的 `/v1/chat/completions` 接口。Hermes 可以与任意一种后端配合使用——只需将其配置为指向 `http://localhost:8080` 或 `http://localhost:8000` 即可。

:::info 仅适用于 Apple Silicon 平台
本指南针对配备 Apple Silicon（M1 及更高版本）的 Mac 设备编写。Intel Mac 虽然也可以使用 llama.cpp，但由于没有 GPU 加速，性能会大幅下降。
:::

---

## 选择模型

作为入门推荐，我们建议使用 **Qwen3.5-9B** —— 这是一款出色的推理模型，经过量化处理后可在 8GB 及以上的统一内存中顺利运行。

| 变体 | 磁盘大小 | 所需 RAM（128K 上下文长度） | 后端 |
|---------|-----------|---------------------------|---------|
| Qwen3.5-9B-Q4_K_M (GGUF) | 5.3 GB | 带量化 KV 缓存时约 10 GB | llama.cpp |
| Qwen3.5-9B-mlx-lm-mxfp4 (MLX) | 约 5 GB | 约 12 GB | omlx |

**内存估算经验法则：** 模型大小 + KV 缓存大小。一个 9B 的 Q4 量化模型本身约占 5 GB，而 128K 上下文长度下的量化 KV 缓存还会额外占用约 4-5 GB。如果使用默认的 (f16) 格式 KV 缓存，内存需求则会上升到约 16 GB。在内存有限的系统中，llama.cpp 中的量化 KV 缓存选项正是节省内存的关键技巧。

对于规模更大的模型（27B、35B），则需要 32 GB 及以上的统一内存。而 9B 模型则是 8-16 GB 内存配置设备的最佳选择。

---

## 方案 A：llama.cpp

llama.cpp 是最通用的本地大语言模型运行时框架。在 macOS 上，它可直接利用 Metal 实现 GPU 加速。

### 安装

```bash
brew install llama.cpp
```

这将为您全局提供 `llama-server` 命令。

### 下载模型

您需要 GGUF 格式的模型。最便捷的获取途径是通过 `huggingface-cli` 访问 Hugging Face 平台：

```bash
brew install huggingface-cli
```

接下来请下载：

```bash
huggingface-cli download unsloth/Qwen3.5-9B-GGUF Qwen3.5-9B-Q4_K_M.gguf --local-dir ~/models
```

:::提示：受访问限制的模型
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
| `-np 1` | 并行槽位数。单用户使用时请保持为 1——更多的槽位会占用更多内存预算。 |
| `-fa on` | 闪存注意力机制。可减少内存使用量，并加快长上下文推理速度。 |
| `--cache-type-k q4_0` | 将键缓存量化为 4 位。**这是节省内存的关键手段。** |
| `--cache-type-v q4_0` | 将值缓存量化为 4 位。结合上述设置，与使用 f16 格式相比，可减少约 75% 的 KV 缓存内存占用。 |
| `--host 0.0.0.0` | 在所有网络接口上监听。如无需网络访问，可使用 `127.0.0.1`。 |

当出现以下提示时，即表示服务器已准备就绪：

```
main: server is listening on http://0.0.0.0:8080
srv  update_slots: all slots are idle
```

### 面向内存受限系统的性能优化

对于内存资源有限的系统而言，`--cache-type-k q4_0 --cache-type-v q4_0` 这两个参数是至关重要的优化手段。以下是在 128K 上下文长度下的内存占用情况：

| KV 缓存类型 | KV 缓存内存占用（128K 上下文，9B 模型） |
|---------------|--------------------------------------|
| f16（默认值） | 约 16 GB |
| q8_0 | 约 8 GB |
| **q4_0** | **约 4 GB** |

在 8 GB 内存的 Mac 设备上，建议使用 `q4_0` 类型的 KV 缓存，并选择体积更小的模型，同时确保该模型能满足 Hermes 最低 64K 的上下文长度要求。在 16 GB 内存环境下，可以轻松支持 128K 的上下文长度；而 32 GB 及以上内存则可运行更大规模的模型或开启多个并行处理槽位。

如果依然出现内存不足的问题，请仅在保证上下文长度不低于 Hermes 最低要求的 64K 的前提下减少上下文长度；否则，可以考虑更换为体积更小的模型，或选择量化等级更低的格式（如从 Q4_K_M 改为 Q3_K_M）。

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

### 获取模型名称

如果您忘记了模型名称，可以查询模型端点：

```bash
curl -s http://localhost:8080/v1/models | jq '.data[].id'
```

## 方案 B：通过 omlx 使用 MLX

[omlx](https://omlx.ai) 是一款专为 macOS 设计的应用程序，用于管理和提供 MLX 模型。MLX 是苹果公司自研的机器学习框架，专为 Apple Silicon 的统一内存架构进行了优化。

### 安装

从 [omlx.ai](https://omlx.ai) 下载并安装该应用。它提供了模型管理的图形界面以及内置服务器功能。

### 下载模型

使用 omlx 应用程序浏览并下载模型。搜索 `Qwen3.5-9B-mlx-lm-mxfp4` 并将其下载。模型会存储在本地（通常位于 `~/.omlx/models/` 目录下）。

### 启动服务器

omlx 默认在 `http://127.0.0.1:8000` 地址上提供模型服务。您可以通过应用程序的界面启动服务，或者在使用 CLI 的情况下通过命令行启动。

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

omlx能够同时加载多个模型进行服务：

```bash
curl -s http://127.0.0.1:8000/v1/models | jq '.data[].id'
```

## 性能基准测试：llama.cpp vs MLX

两项测试均在同一台设备（Apple M5 Max，128 GB统一内存）上展开，使用相同的模型（Qwen3.5-9B），并在相近的量化级别下进行测试（GGUF格式为Q4_K_M，MLX格式为mxfp4）。共使用了五种不同的提示词，每种提示词运行三次，且按顺序测试不同后端以避免资源竞争。

### 测试结果

| 指标 | llama.cpp (Q4_K_M) | MLX (mxfp4) | 胜出者 |
|------|-------------------|-------------|--------|
| **TTFT（平均值）** | **67 毫秒** | 289 毫秒 | llama.cpp（快4.3倍） |
| **TTFT（p50值）** | **66 毫秒** | 286 毫秒 | llama.cpp（快4.3倍） |
| **生成速度（平均值）** | 70 个token/秒 | **96 个token/秒** | MLX（快37%） |
| **生成速度（p50值）** | 70 个token/秒 | **96 个token/秒** | MLX（快37%） |
| **生成512个token的总时间** | 7.3秒 | **5.5秒** | MLX（快25%） |

### 结果解读

- **llama.cpp**在提示词处理方面表现优异——其闪存注意力机制加上量化的KV缓存架构，能让第一个token在约66毫秒内生成。对于那些对响应速度要求较高的交互式应用（如聊天机器人、自动补全功能），这一优势尤为显著。

- **MLX**在开始生成内容后，其token生成速度可快37%。对于批量处理、长文本生成，或是那些更看重整体完成时间而非初始延迟的任务，MLX能更快地完成任务。

- 两种后端的测试结果**极其稳定**——不同次测试之间的差异可以忽略不计，因此这些数据具有很高的参考价值。

### 应该选择哪一个？

| 使用场景 | 推荐方案 |
|----------|----------|
| 交互式聊天、低延迟工具 | llama.cpp |
| 长文本生成、批量处理 | MLX（omlx） |
| 内存受限环境（8-16 GB） | llama.cpp（其量化的KV缓存优势明显） |
| 需要同时加载多个模型 | omlx（内置多模型支持） |
| 最高兼容性需求（包括Linux系统） | llama.cpp |

---

## 连接Hermes

当您的本地服务器启动后：

```bash
hermes model
```

选择**自定义端点**，然后按照提示操作。系统会要求输入基础 URL 和模型名称——请使用您在上一步中配置的后端对应的值。

---

## 超时设置

Hermes 会自动识别本地端点（如 localhost、局域网 IP），并相应延长其流式传输的超时时间。对于大多数配置而言，无需进行额外设置。

如果您仍然遇到超时错误（例如在性能较弱的硬件上处理过大的上下文数据），可以手动覆盖流式读取的超时时间：

```bash
# In your .env — raise from the 120s default to 30 minutes
HERMES_STREAM_READ_TIMEOUT=1800
```

| 超时时间 | 默认值 | 本地自动调整 | 环境变量覆盖 |
|---------|--------|----------------|--------------|
| 流式读取（套接字层） | 120秒 | 提高至1800秒 | `HERMES_STREAM_READ_TIMEOUT` |
| 过期流检测 | 180秒 | 完全禁用 | `HERMES_STREAM_STALE_TIMEOUT` |
| API调用（非流式） | 1800秒 | 无需调整 | `HERMES_API_TIMEOUT` |

其中，流式读取超时最容易引发问题——它代表了在套接字层接收下一组数据的截止时间。在处理大型上下文时的预填充阶段，本地模型可能在处理提示语的数分钟内不会产生任何输出。自动检测功能可隐式地解决这一问题。
