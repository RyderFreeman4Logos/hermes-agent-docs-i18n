---
title: "Serving Llms Vllm — vLLM: high-throughput LLM serving, OpenAI API, quantization"
sidebar_label: "Serving Llms Vllm"
description: "vLLM: high-throughput LLM serving, OpenAI API, quantization"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# 提供 Llms vLLM 服务

vLLM：高效能的 LLM 服务框架，支持 OpenAI API 及量化技术。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/mlops/inference/vllm` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `vllm`、`torch`、`transformers` |
| 支持平台 | linux、macos |
| 标签 | `vLLM`、`推理服务`、`分页注意力机制`、`连续批处理`、`高吞吐量`、`生产环境`、`OpenAI API`、`量化`、`张量并行` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容执行操作。
:::

# vLLM – 高性能 LLM 服务框架

## 适用场景

适用于部署生产级 LLM API、优化推理延迟/吞吐量，或为 GPU 内存有限的场景提供模型服务。该框架支持与 OpenAI 兼容的接口、量化技术（GPTQ/AWQ/FP8）以及张量并行处理。

## 快速入门

通过分页注意力机制（基于块的 KV 缓存）和连续批处理技术（混合预填充请求与解码请求），vLLM 的吞吐量可达到标准 transformers 框架的 24 倍。

**安装方式**：
```bash
pip install vllm
```

**基础离线推理**：
```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3-8B-Instruct")
sampling = SamplingParams(temperature=0.7, max_tokens=256)

outputs = llm.generate(["Explain quantum computing"], sampling)
print(outputs[0].outputs[0].text)
```

**兼容 OpenAI 的服务器**：
```bash
vllm serve meta-llama/Llama-3-8B-Instruct

# Query with OpenAI SDK
python -c "
from openai import OpenAI
client = OpenAI(base_url='http://localhost:8000/v1', api_key='EMPTY')
print(client.chat.completions.create(
    model='meta-llama/Llama-3-8B-Instruct',
    messages=[{'role': 'user', 'content': 'Hello!'}]
).choices[0].message.content)
"
```

## 常见工作流程

### 工作流程 1：生产环境 API 部署

复制此清单并跟踪进度：

```
Deployment Progress:
- [ ] Step 1: Configure server settings
- [ ] Step 2: Test with limited traffic
- [ ] Step 3: Enable monitoring
- [ ] Step 4: Deploy to production
- [ ] Step 5: Verify performance metrics
```

**步骤 1：配置服务器设置**

根据模型规模选择相应的配置方案：

```bash
# For 7B-13B models on single GPU
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 \
  --port 8000

# For 30B-70B models with tensor parallelism
vllm serve meta-llama/Llama-2-70b-hf \
  --tensor-parallel-size 4 \
  --gpu-memory-utilization 0.9 \
  --quantization awq \
  --port 8000

# For production with caching and metrics
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching \
  --enable-metrics \
  --metrics-port 9090 \
  --port 8000 \
  --host 0.0.0.0
```

**步骤 2：在有限流量下进行测试**

在生产环境部署之前，先运行负载测试：

```bash
# Install load testing tool
pip install locust

# Create test_load.py with sample requests
# Run: locust -f test_load.py --host http://localhost:8000
```

请确保首次生成令牌的时间（TTFT）小于 500 毫秒，且吞吐量大于 100 请求/秒。

**步骤 3：启用监控功能**

vLLM 会在 9090 端口上暴露 Prometheus 指标：

```bash
curl http://localhost:9090/metrics | grep vllm
```

需要监控的关键指标：
- `vllm:time_to_first_token_seconds` —— 延迟时间
- `vllm:num_requests_running` —— 正在处理的请求数量
- `vllm:gpu_cache_usage_perc` —— KV缓存使用率

**第4步：部署到生产环境**

建议使用Docker以确保部署的一致性：

```bash
# Run vLLM in Docker
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching
```

**第5步：验证性能指标**

确认部署结果是否符合预期目标：
- TTFT < 500毫秒（针对短文本提示）
- 吞吐量 > 预设的请求/秒数
- GPU利用率 > 80%
- 日志中无内存不足错误

### 工作流程2：离线批量推理

用于在无需服务器开销的情况下处理大型数据集。

复制此检查清单：

```
Batch Processing:
- [ ] Step 1: Prepare input data
- [ ] Step 2: Configure LLM engine
- [ ] Step 3: Run batch inference
- [ ] Step 4: Process results
```

**步骤 1：准备输入数据**

```python
# Load prompts from file
prompts = []
with open("prompts.txt") as f:
    prompts = [line.strip() for line in f]

print(f"Loaded {len(prompts)} prompts")
```

**步骤 2：配置大语言模型引擎**

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3-8B-Instruct",
    tensor_parallel_size=2,  # Use 2 GPUs
    gpu_memory_utilization=0.9,
    max_model_len=4096
)

sampling = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=512,
    stop=["</s>", "\n\n"]
)
```

**步骤 3：执行批量推理**

为提升效率，vLLM 会自动对请求进行批量处理：

```python
# Process all prompts in one call
outputs = llm.generate(prompts, sampling)

# vLLM handles batching internally
# No need to manually chunk prompts
```

**第4步：处理结果**

```python
# Extract generated text
results = []
for output in outputs:
    prompt = output.prompt
    generated = output.outputs[0].text
    results.append({
        "prompt": prompt,
        "generated": generated,
        "tokens": len(output.outputs[0].token_ids)
    })

# Save to file
import json
with open("results.jsonl", "w") as f:
    for result in results:
        f.write(json.dumps(result) + "\n")

print(f"Processed {len(results)} prompts")
```

### 工作流 3：量化模型服务

在有限的 GPU 内存中部署大型模型。

```
Quantization Setup:
- [ ] Step 1: Choose quantization method
- [ ] Step 2: Find or create quantized model
- [ ] Step 3: Launch with quantization flag
- [ ] Step 4: Verify accuracy
```

**步骤 1：选择量化方法**

- **AWQ**：最适合 70B 模型，精度损失最小  
- **GPTQ**：支持多种模型类型，压缩效果优异  
- **FP8**：在 H100 GPU 上运行速度最快  

**步骤 2：查找或创建量化后的模型**

可使用 HuggingFace 提供的预量化模型：

```bash
# Search for AWQ models
# Example: TheBloke/Llama-2-70B-AWQ
```

**步骤 3：使用量化标志启动**

```bash
# Using pre-quantized model
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.95

# Results: 70B model in ~40GB VRAM
```

**第4步：验证准确性**

检查输出结果是否符合预期质量标准：

```python
# Compare quantized vs non-quantized responses
# Verify task-specific performance unchanged
```

## 何时使用 vLLM 及其替代方案

**适合使用 vLLM 的场景：**
- 部署生产级 LLM API（每秒请求量超过 100 次）
- 提供兼容 OpenAI 的接口
- GPU 内存有限但需要运行大型模型
- 多用户应用（聊天机器人、智能助手）
- 需要低延迟与高吞吐量的处理能力

**建议选择替代方案的情况：**
- **llama.cpp**：适用于 CPU/边缘设备推理，单用户使用
- **HuggingFace transformers**：适合研究、原型开发以及一次性文本生成任务
- **TensorRT-LLM**：仅支持 NVIDIA 硬件，需追求极致性能时使用
- **Text-Generation-Inference**：已集成在 HuggingFace 生态系统中

## 常见问题

**问题：加载模型时内存不足**

降低内存占用：
```bash
vllm serve MODEL \
  --gpu-memory-utilization 0.7 \
  --max-model-len 4096
```

或者使用量化功能：
```bash
vllm serve MODEL --quantization awq
```

**问题：首个令牌生成速度过慢（TTFT超过1秒）**

为重复发送的提示语启用前缀缓存功能：
```bash
vllm serve MODEL --enable-prefix-caching
```

对于较长的提示词，请启用分块预填充功能：
```bash
vllm serve MODEL --enable-chunked-prefill
```

**问题：模型未找到错误**

如需使用自定义模型，请使用 `--trust-remote-code` 参数：
```bash
vllm serve MODEL --trust-remote-code
```

**问题：吞吐量过低（＜50 次请求/秒）**

增加并发序列数：
```bash
vllm serve MODEL --max-num-seqs 512
```

使用 `nvidia-smi` 工具检查 GPU 的利用率——该数值应大于 80%。

**问题：推理速度低于预期**

请确认张量并行化已使用 2 的幂次方数量的 GPU：
```bash
vllm serve MODEL --tensor-parallel-size 4  # Not 3
```

启用推测解码以提升生成速度：
```bash
vllm serve MODEL --speculative-model DRAFT_MODEL
```

## 高级主题

**服务器部署方案**：如需了解 Docker、Kubernetes 及负载均衡的配置方式，请参阅 [references/server-deployment.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/server-deployment.md)。

**性能优化**：关于 PagedAttention 调优、连续批处理详解以及基准测试结果，可查看 [references/optimization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/optimization.md)。

**量化指南**：涉及 AWQ/GPTQ/FP8 的配置、模型准备及精度对比等内容，请参考 [references/quantization.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/quantization.md)。

**故障排查**：详细的错误信息、调试步骤以及性能诊断方法，均可在 [references/troubleshooting.md](https://github.com/NousResearch/hermes-agent/blob/main/skills/mlops/inference/vllm/references/troubleshooting.md) 中找到。

## 硬件要求

- **小型模型（7B-13B）**：1块 A10（24GB）或 A100（40GB）显卡
- **中型模型（30B-40B）**：2块支持张量并行的 A100（40GB）显卡
- **大型模型（70B+）**：4块 A100（40GB）显卡或2块 A100（80GB）显卡，建议使用 AWQ/GPTQ 技术

支持的硬件平台：NVIDIA（主要支持）、AMD ROCm、Intel GPU及 TPU。

## 相关资源

- 官方文档：https://docs.vllm.ai
- GitHub 仓库：https://github.com/vllm-project/vllm
- 学术论文：《利用 PagedAttention 实现大型语言模型服务的高效内存管理》（SOSP 2023）
- 社区论坛：https://discuss.vllm.ai
