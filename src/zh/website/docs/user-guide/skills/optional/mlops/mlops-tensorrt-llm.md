---
title: "Tensorrt Llm — High-throughput LLM inference on NVIDIA GPUs"
sidebar_label: "Tensorrt Llm"
description: "High-throughput LLM inference on NVIDIA GPUs"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Tensorrt Llm

在 NVIDIA GPU 上实现高吞吐量的大语言模型推理。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/tensorrt-llm` 安装 |
| 路径 | `optional-skills/mlops/tensorrt-llm` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `tensorrt-llm`, `torch` |
| 支持平台 | linux, macos |
| 标签 | `推理服务`, `TensorRT-LLM`, `NVIDIA`, `推理优化`, `高吞吐量`, `低延迟`, `生产环境`, `FP8`, `INT4`, `动态批处理`, `多GPU` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，Agent 就会看到这些指令作为操作指南。
:::

# TensorRT-LLM

NVIDIA 开发的开源库，可在 NVIDIA GPU 上以最先进的性能优化大语言模型推理。

## 何时使用 TensorRT-LLM

**以下情况建议使用 TensorRT-LLM：**
- 在 NVIDIA GPU（A100、H100、GB200）上部署模型
- 需要极高的吞吐量（Llama 3 每秒可处理 24,000 个以上token）
- 实时应用对低延迟有严格要求
- 处理量化后的模型（FP8、INT4、FP4）
- 在多 GPU 或多节点环境中扩展部署

**以下情况建议改用 vLLM：**
- 需要更简单的设置及以 Python 为主的 API
- 希望使用 PagedAttention 且无需进行 TensorRT 编译
- 在 AMD GPU 或非 NVIDIA 硬件上运行

**以下情况建议改用 llama.cpp：**
- 在 CPU 或 Apple Silicon 平台上部署模型
- 需要在没有 NVIDIA GPU 的边缘设备上运行
- 希望使用更简单的 GGUF 量化格式

## 快速入门

### 安装

```bash
# Docker (recommended)
docker pull nvidia/tensorrt_llm:latest

# pip install
pip install tensorrt_llm==1.2.0rc3

# Requires CUDA 13.0.0, TensorRT 10.13.2, Python 3.10-3.12
```

### 基本推理

```python
from tensorrt_llm import LLM, SamplingParams

# Initialize model
llm = LLM(model="meta-llama/Meta-Llama-3-8B")

# Configure sampling
sampling_params = SamplingParams(
    max_tokens=100,
    temperature=0.7,
    top_p=0.9
)

# Generate
prompts = ["Explain quantum computing"]
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(output.text)
```

### 使用 trtllm-serve 进行服务部署

```bash
# Start server (automatic model download and compilation)
trtllm-serve meta-llama/Meta-Llama-3-8B \
    --tp_size 4 \              # Tensor parallelism (4 GPUs)
    --max_batch_size 256 \
    --max_num_tokens 4096

# Client request
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3-8B",
    "messages": [{"role": "user", "content": "Hello!"}],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

## 核心特性

### 性能优化
- **传输中批量处理**：在生成过程中实现动态批量化
- **分页键值缓存**：高效的内存管理机制
- **Flash Attention**：优化的注意力计算内核
- **量化技术**：支持FP8、INT4、FP4格式，提升推理速度2-4倍
- **CUDA图优化**：降低内核启动开销

### 并行处理能力
- **张量并行（TP）**：将模型任务分配到多块GPU上处理
- **流水线并行（PP）**：按层级分配计算任务
- **专家并行**：专为混合专家模型设计
- **多节点部署**：突破单机限制实现大规模扩展

### 高级功能
- **推测解码**：利用草稿模型加快生成速度
- **LoRA服务**：高效的多适配器部署方案
- **分离式服务架构**：将预填充与生成过程独立处理

## 常见应用场景

### 量化模型（FP8格式）

```python
from tensorrt_llm import LLM

# Load FP8 quantized model (2× faster, 50% memory)
llm = LLM(
    model="meta-llama/Meta-Llama-3-70B",
    dtype="fp8",
    max_num_tokens=8192
)

# Inference same as before
outputs = llm.generate(["Summarize this article..."])
```

### 多 GPU 部署

```python
# Tensor parallelism across 8 GPUs
llm = LLM(
    model="meta-llama/Meta-Llama-3-405B",
    tensor_parallel_size=8,
    dtype="fp8"
)
```

### 批量推理

```python
# Process 100 prompts efficiently
prompts = [f"Question {i}: ..." for i in range(100)]

outputs = llm.generate(
    prompts,
    sampling_params=SamplingParams(max_tokens=200)
)

# Automatic in-flight batching for maximum throughput
```

## 性能基准测试

**Meta Llama 3-8B**（H100 GPU）：
- 处理速度：24,000 个标记/秒
- 延迟：每个标记约 10 毫秒
- 相较于 PyTorch：**速度快 100 倍**

**Llama 3-70B**（8× A100 80GB）：
- FP8 量化格式下的处理速度是 FP16 的 2 倍
- 使用 FP8 后内存占用可减少 50%

## 支持的模型

- **LLaMA 系列**：Llama 2、Llama 3、CodeLlama
- **GPT 系列**：GPT-2、GPT-J、GPT-NeoX
- **Qwen 系列**：Qwen、Qwen2、QwQ
- **DeepSeek 系列**：DeepSeek-V2、DeepSeek-V3
- **Mixtral 系列**：Mixtral-8x7B、Mixtral-8x22B
- **视觉模型**：LLaVA、Phi-3-vision
- HuggingFace 上的 **100 多种模型**

## 参考资料

- **[优化指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/optimization.md)** – 量化处理、批量处理、KV 缓存优化
- **[多 GPU 部署指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/multi-gpu.md)** – Tensor/流水线并行处理、多节点部署
- **[服务部署指南](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/tensorrt-llm/references/serving.md)** – 生产环境部署、监控与自动扩缩容

## 相关资源

- **文档**：https://nvidia.github.io/TensorRT-LLM/
- **GitHub 仓库**：https://github.com/NVIDIA/TensorRT-LLM
- **模型列表**：https://huggingface.co/models?library=tensorrt_llm
