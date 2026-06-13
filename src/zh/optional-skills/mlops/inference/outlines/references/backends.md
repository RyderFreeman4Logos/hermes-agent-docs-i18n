# 后端配置指南

关于如何使用不同模型后端配置 Outlines 的完整指南。

## 目录
- 本地模型（Transformers、llama.cpp、vLLM）
- API 模型（OpenAI）
- 性能对比
- 配置示例
- 生产环境部署

## Transformers（Hugging Face）

### 基本设置

```python
import outlines

# Load model from Hugging Face
model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")

# Use with generator
generator = outlines.generate.json(model, YourModel)
result = generator("Your prompt")
```

### GPU配置

```python
# Use CUDA GPU
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda"
)

# Use specific GPU
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda:0"  # GPU 0
)

# Use CPU
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cpu"
)

# Use Apple Silicon MPS
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="mps"
)
```

### 高级配置

```python
# FP16 for faster inference
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda",
    model_kwargs={
        "torch_dtype": "float16"
    }
)

# 8-bit quantization (less memory)
model = outlines.models.transformers(
    "microsoft/Phi-3-mini-4k-instruct",
    device="cuda",
    model_kwargs={
        "load_in_8bit": True,
        "device_map": "auto"
    }
)

# 4-bit quantization (even less memory)
model = outlines.models.transformers(
    "meta-llama/Llama-3.1-70B-Instruct",
    device="cuda",
    model_kwargs={
        "load_in_4bit": True,
        "device_map": "auto",
        "bnb_4bit_compute_dtype": "float16"
    }
)

# Multi-GPU
model = outlines.models.transformers(
    "meta-llama/Llama-3.1-70B-Instruct",
    device="cuda",
    model_kwargs={
        "device_map": "auto",  # Automatic GPU distribution
        "max_memory": {0: "40GB", 1: "40GB"}  # Per-GPU limits
    }
)
```

### 热门模型

```python
# Phi-4 (Microsoft)
model = outlines.models.transformers("microsoft/Phi-4-mini-instruct")
model = outlines.models.transformers("microsoft/Phi-3-medium-4k-instruct")

# Llama 3.1 (Meta)
model = outlines.models.transformers("meta-llama/Llama-3.1-8B-Instruct")
model = outlines.models.transformers("meta-llama/Llama-3.1-70B-Instruct")
model = outlines.models.transformers("meta-llama/Llama-3.1-405B-Instruct")

# Mistral (Mistral AI)
model = outlines.models.transformers("mistralai/Mistral-7B-Instruct-v0.3")
model = outlines.models.transformers("mistralai/Mixtral-8x7B-Instruct-v0.1")
model = outlines.models.transformers("mistralai/Mixtral-8x22B-Instruct-v0.1")

# Qwen (Alibaba)
model = outlines.models.transformers("Qwen/Qwen2.5-7B-Instruct")
model = outlines.models.transformers("Qwen/Qwen2.5-14B-Instruct")
model = outlines.models.transformers("Qwen/Qwen2.5-72B-Instruct")

# Gemma (Google)
model = outlines.models.transformers("google/gemma-2-9b-it")
model = outlines.models.transformers("google/gemma-2-27b-it")

# Llava (Vision)
model = outlines.models.transformers("llava-hf/llava-v1.6-mistral-7b-hf")
```

### 自定义模型加载

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import outlines

# Load model manually
tokenizer = AutoTokenizer.from_pretrained("your-model")
model_hf = AutoModelForCausalLM.from_pretrained(
    "your-model",
    device_map="auto",
    torch_dtype="float16"
)

# Use with Outlines
model = outlines.models.transformers(
    model=model_hf,
    tokenizer=tokenizer
)
```

## llama.cpp

### 基本设置

```python
import outlines

# Load GGUF model
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b-instruct.Q4_K_M.gguf",
    n_ctx=4096  # Context window
)

# Use with generator
generator = outlines.generate.json(model, YourModel)
```

### GPU配置

```python
# CPU only
model = outlines.models.llamacpp(
    "./models/model.gguf",
    n_ctx=4096,
    n_threads=8  # Use 8 CPU threads
)

# GPU offload (partial)
model = outlines.models.llamacpp(
    "./models/model.gguf",
    n_ctx=4096,
    n_gpu_layers=35,  # Offload 35 layers to GPU
    n_threads=4       # CPU threads for remaining layers
)

# Full GPU offload
model = outlines.models.llamacpp(
    "./models/model.gguf",
    n_ctx=8192,
    n_gpu_layers=-1  # All layers on GPU
)
```

### 高级配置

```python
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b.Q4_K_M.gguf",
    n_ctx=8192,          # Context window (tokens)
    n_gpu_layers=35,     # GPU layers
    n_threads=8,         # CPU threads
    n_batch=512,         # Batch size for prompt processing
    use_mmap=True,       # Memory-map model file (faster loading)
    use_mlock=False,     # Lock model in RAM (prevents swapping)
    seed=42,             # Random seed for reproducibility
    verbose=False        # Suppress verbose output
)
```

### 量化格式

```python
# Q4_K_M (4-bit, recommended for most cases)
# - Size: ~4.5GB for 7B model
# - Quality: Good
# - Speed: Fast
model = outlines.models.llamacpp("./models/model.Q4_K_M.gguf")

# Q5_K_M (5-bit, better quality)
# - Size: ~5.5GB for 7B model
# - Quality: Very good
# - Speed: Slightly slower than Q4
model = outlines.models.llamacpp("./models/model.Q5_K_M.gguf")

# Q6_K (6-bit, high quality)
# - Size: ~6.5GB for 7B model
# - Quality: Excellent
# - Speed: Slower than Q5
model = outlines.models.llamacpp("./models/model.Q6_K.gguf")

# Q8_0 (8-bit, near-original quality)
# - Size: ~8GB for 7B model
# - Quality: Near FP16
# - Speed: Slower than Q6
model = outlines.models.llamacpp("./models/model.Q8_0.gguf")

# F16 (16-bit float, original quality)
# - Size: ~14GB for 7B model
# - Quality: Original
# - Speed: Slowest
model = outlines.models.llamacpp("./models/model.F16.gguf")
```

### 热门 GGUF 模型

```python
# Llama 3.1
model = outlines.models.llamacpp("llama-3.1-8b-instruct.Q4_K_M.gguf")
model = outlines.models.llamacpp("llama-3.1-70b-instruct.Q4_K_M.gguf")

# Mistral
model = outlines.models.llamacpp("mistral-7b-instruct-v0.3.Q4_K_M.gguf")

# Phi-4
model = outlines.models.llamacpp("phi-4-mini-instruct.Q4_K_M.gguf")

# Qwen
model = outlines.models.llamacpp("qwen2.5-7b-instruct.Q4_K_M.gguf")
```

### Apple Silicon架构优化

```python
# Optimized for M1/M2/M3 Macs
model = outlines.models.llamacpp(
    "./models/llama-3.1-8b.Q4_K_M.gguf",
    n_ctx=4096,
    n_gpu_layers=-1,  # Use Metal GPU acceleration
    use_mmap=True,    # Efficient memory mapping
    n_threads=8       # Use performance cores
)
```

## vLLM（生产环境）

### 基本配置

```python
import outlines

# Load model with vLLM
model = outlines.models.vllm("meta-llama/Llama-3.1-8B-Instruct")

# Use with generator
generator = outlines.generate.json(model, YourModel)
```

### 单个 GPU

```python
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    gpu_memory_utilization=0.9,  # Use 90% of GPU memory
    max_model_len=4096          # Max sequence length
)
```

### 多 GPU 支持

```python
# Tensor parallelism (split model across GPUs)
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=4,  # Use 4 GPUs
    gpu_memory_utilization=0.9
)

# Pipeline parallelism (rare, for very large models)
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-405B-Instruct",
    pipeline_parallel_size=8,  # 8-GPU pipeline
    tensor_parallel_size=4     # 4-GPU tensor split
    # Total: 32 GPUs
)
```

### 量化处理

```python
# AWQ quantization (4-bit)
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization="awq",
    dtype="float16"
)

# GPTQ quantization (4-bit)
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization="gptq"
)

# SqueezeLLM quantization
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization="squeezellm"
)
```

### 高级配置

```python
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=1,
    gpu_memory_utilization=0.9,
    max_model_len=8192,
    max_num_seqs=256,           # Max concurrent sequences
    max_num_batched_tokens=8192, # Max tokens per batch
    dtype="float16",
    trust_remote_code=True,
    enforce_eager=False,        # Use CUDA graphs (faster)
    swap_space=4                # CPU swap space (GB)
)
```

### 批量处理

```python
# vLLM optimized for high-throughput batch processing
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    max_num_seqs=128  # Process 128 sequences in parallel
)

generator = outlines.generate.json(model, YourModel)

# Process many prompts efficiently
prompts = ["prompt1", "prompt2", ..., "prompt100"]
results = [generator(p) for p in prompts]
# vLLM automatically batches and optimizes
```

## OpenAI（支持有限）

### 基本设置

```python
import outlines

# Basic OpenAI support
model = outlines.models.openai("gpt-4o-mini", api_key="your-api-key")

# Use with generator
generator = outlines.generate.json(model, YourModel)
result = generator("Your prompt")
```

### 配置

```python
model = outlines.models.openai(
    "gpt-4o-mini",
    api_key="your-api-key",  # Or set OPENAI_API_KEY env var
    max_tokens=2048,
    temperature=0.7
)
```

### 可用模型

```python
# GPT-4o (latest)
model = outlines.models.openai("gpt-4o")

# GPT-4o Mini (cost-effective)
model = outlines.models.openai("gpt-4o-mini")

# GPT-4 Turbo
model = outlines.models.openai("gpt-4-turbo")

# GPT-3.5 Turbo
model = outlines.models.openai("gpt-3.5-turbo")
```

**注意**：与本地模型相比，OpenAI 的支持功能较为有限，某些高级特性可能无法使用。

## 后端方案对比

### 功能矩阵

| 功能 | Transformers | llama.cpp | vLLM | OpenAI |
|---------|-------------|-----------|------|--------|
| 结构化生成 | ✅ 完全支持 | ✅ 完全支持 | ✅ 完全支持 | ⚠️ 支持有限 |
| FSM 优化 | ✅ 支持 | ✅ 支持 | ✅ 支持 | ❌ 不支持 |
| GPU 支持 | ✅ 支持 | ✅ 支持 | ✅ 支持 | 不适用 |
| 多 GPU 支持 | ✅ 支持 | ✅ 支持 | ✅ 支持 | 不适用 |
| 量化处理 | ✅ 支持 | ✅ 支持 | ✅ 支持 | 不适用 |
| 高吞吐量 | ⚠️ 中等 | ⚠️ 中等 | ✅ 极佳 | ⚠️ 受 API 限制 |
| 设置难度 | 简单 | 中等 | 中等 | 简单 |
| 成本 | 硬件成本 | 硬件成本 | 硬件成本 | API 使用费用 |

### 性能特点

**Transformers：**
- **延迟**：50-200 毫秒（单次请求，GPU环境）
- **吞吐量**：10-50 个令牌/秒（取决于硬件配置）
- **内存占用**：每 10 亿参数约 2-4 GB（FP16格式）
- **最佳适用场景**：开发测试、小规模部署、高灵活性需求

**llama.cpp：**
- **延迟**：30-150 毫秒（单次请求）
- **吞吐量**：20-150 个令牌/秒（取决于量化级别）
- **内存占用**：每 10 亿参数约 0.5-2 GB（Q4-Q8量化级别）
- **最佳适用场景**：CPU推理、Apple Silicon芯片、边缘设备部署、低内存环境

**vLLM：**
- **延迟**：30-100 毫秒（单次请求）
- **吞吐量**：100-1000+ 个令牌/秒（批量处理模式）
- **内存占用**：每 10 亿参数约 2-4 GB（FP16格式）
- **最佳适用场景**：生产环境部署、高吞吐量处理、批量任务处理、服务端应用

**OpenAI：**
- **延迟**：200-500 毫秒（API调用延迟）
- **吞吐量**：受API调用速率限制
- **内存占用**：无（基于云端服务）
- **最佳适用场景**：快速原型开发、无需自行搭建基础设施的场景

### 内存需求

**70亿参数模型：**
- FP16格式：约14 GB
- 8位量化：约7 GB
- 4位量化：约4 GB
- Q4_K_M格式（GGUF文件）：约4.5 GB

**130亿参数模型：**
- FP16格式：约26 GB
- 8位量化：约13 GB
- 4位量化：约7 GB
- Q4_K_M格式（GGUF文件）：约8 GB

**700亿参数模型：**
- FP16格式：多GPU环境下约140 GB
- 8位量化：多GPU环境下约70 GB
- 4位量化：单台A100/H100芯片上约35 GB
- Q4_K_M格式（GGUF文件）：约40 GB

## 性能调优

### Transformers优化方案

```python
# Use FP16
model = outlines.models.transformers(
    "meta-llama/Llama-3.1-8B-Instruct",
    device="cuda",
    model_kwargs={"torch_dtype": "float16"}
)

# Use flash attention (2-4x faster)
model = outlines.models.transformers(
    "meta-llama/Llama-3.1-8B-Instruct",
    device="cuda",
    model_kwargs={
        "torch_dtype": "float16",
        "use_flash_attention_2": True
    }
)

# Use 8-bit quantization (2x less memory)
model = outlines.models.transformers(
    "meta-llama/Llama-3.1-8B-Instruct",
    device="cuda",
    model_kwargs={
        "load_in_8bit": True,
        "device_map": "auto"
    }
)
```

### llama.cpp 优化方案

```python
# Maximize GPU usage
model = outlines.models.llamacpp(
    "./models/model.Q4_K_M.gguf",
    n_gpu_layers=-1,  # All layers on GPU
    n_ctx=8192,
    n_batch=512       # Larger batch = faster
)

# Optimize for CPU (Apple Silicon)
model = outlines.models.llamacpp(
    "./models/model.Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=8,      # Use all performance cores
    use_mmap=True
)
```

### vLLM 优化功能

```python
# High throughput
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-8B-Instruct",
    gpu_memory_utilization=0.95,  # Use 95% of GPU
    max_num_seqs=256,             # High concurrency
    enforce_eager=False           # Use CUDA graphs
)

# Multi-GPU
model = outlines.models.vllm(
    "meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=4,  # 4 GPUs
    gpu_memory_utilization=0.9
)
```

## 生产环境部署

### 使用 vLLM 的 Docker 部署方式

```dockerfile
FROM vllm/vllm-openai:latest

# Install outlines
RUN pip install outlines

# Copy your code
COPY app.py /app/

# Run
CMD ["python", "/app/app.py"]
```

### 环境变量

```bash
# Transformers cache
export HF_HOME="/path/to/cache"
export TRANSFORMERS_CACHE="/path/to/cache"

# GPU selection
export CUDA_VISIBLE_DEVICES=0,1,2,3

# OpenAI API key
export OPENAI_API_KEY="sk-..."

# Disable tokenizers parallelism warning
export TOKENIZERS_PARALLELISM=false
```

### 模型服务

```python
# Simple HTTP server with vLLM
import outlines
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Load model once at startup
model = outlines.models.vllm("meta-llama/Llama-3.1-8B-Instruct")

class User(BaseModel):
    name: str
    age: int
    email: str

generator = outlines.generate.json(model, User)

@app.post("/extract")
def extract(text: str):
    result = generator(f"Extract user from: {text}")
    return result.model_dump()
```

## 资源参考

- **Transformers**：https://huggingface.co/docs/transformers  
- **llama.cpp**：https://github.com/ggerganov/llama.cpp  
- **vLLM**：https://docs.vllm.ai  
- **Outlines**：https://github.com/outlines-dev/outlines
