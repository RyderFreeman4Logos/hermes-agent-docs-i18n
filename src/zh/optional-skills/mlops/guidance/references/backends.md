# 后端配置指南

关于如何使用不同的大型语言模型后端来配置 Guidance 的完整指南。

## 目录
- 基于 API 的模型（Anthropic、OpenAI）
- 本地模型（Transformers、llama.cpp）
- 各后端对比
- 性能调优
- 高级配置

## 基于 API 的模型

### Anthropic Claude

#### 基本设置

```python
from guidance import models

# Using environment variable
lm = models.Anthropic("claude-sonnet-4-5-20250929")
# Reads ANTHROPIC_API_KEY from environment

# Explicit API key
lm = models.Anthropic(
    model="claude-sonnet-4-5-20250929",
    api_key="your-api-key-here"
)
```

#### 可用模型

```python
# Claude 3.5 Sonnet (Latest, recommended)
lm = models.Anthropic("claude-sonnet-4-5-20250929")

# Claude 3.7 Sonnet (Fast, cost-effective)
lm = models.Anthropic("claude-sonnet-3.7-20250219")

# Claude 3 Opus (Most capable)
lm = models.Anthropic("claude-3-opus-20240229")

# Claude 3.5 Haiku (Fastest, cheapest)
lm = models.Anthropic("claude-3-5-haiku-20241022")
```

#### 配置选项

```python
lm = models.Anthropic(
    model="claude-sonnet-4-5-20250929",
    api_key="your-api-key",
    max_tokens=4096,           # Max tokens to generate
    temperature=0.7,            # Sampling temperature (0-1)
    top_p=0.9,                  # Nucleus sampling
    timeout=30,                 # Request timeout (seconds)
    max_retries=3              # Retry failed requests
)
```

#### 结合上下文管理器使用

```python
from guidance import models, system, user, assistant, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

with system():
    lm += "You are a helpful assistant."

with user():
    lm += "What is the capital of France?"

with assistant():
    lm += gen(max_tokens=50)

print(lm)
```

### OpenAI

#### 基本配置

```python
from guidance import models

# Using environment variable
lm = models.OpenAI("gpt-4o")
# Reads OPENAI_API_KEY from environment

# Explicit API key
lm = models.OpenAI(
    model="gpt-4o",
    api_key="your-api-key-here"
)
```

#### 可用模型

```python
# GPT-4o (Latest, multimodal)
lm = models.OpenAI("gpt-4o")

# GPT-4o Mini (Fast, cost-effective)
lm = models.OpenAI("gpt-4o-mini")

# GPT-4 Turbo
lm = models.OpenAI("gpt-4-turbo")

# GPT-3.5 Turbo (Cheapest)
lm = models.OpenAI("gpt-3.5-turbo")
```

#### 配置选项

```python
lm = models.OpenAI(
    model="gpt-4o-mini",
    api_key="your-api-key",
    max_tokens=2048,
    temperature=0.7,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    timeout=30
)
```

#### 聊天格式

```python
from guidance import models, gen

lm = models.OpenAI("gpt-4o-mini")

# OpenAI uses chat format
lm += [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"}
]

# Generate response
lm += gen(max_tokens=50)
```

### Azure OpenAI

```python
from guidance import models

lm = models.AzureOpenAI(
    model="gpt-4o",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-azure-api-key",
    api_version="2024-02-15-preview",
    deployment_name="your-deployment-name"
)
```

## 本地模型

### Transformer 模型（Hugging Face）

#### 基本配置

```python
from guidance.models import Transformers

# Load model from Hugging Face
lm = Transformers("microsoft/Phi-4-mini-instruct")
```

#### GPU配置

```python
# Use GPU
lm = Transformers(
    "microsoft/Phi-4-mini-instruct",
    device="cuda"
)

# Use specific GPU
lm = Transformers(
    "microsoft/Phi-4-mini-instruct",
    device="cuda:0"  # GPU 0
)

# Use CPU
lm = Transformers(
    "microsoft/Phi-4-mini-instruct",
    device="cpu"
)
```

#### 高级配置

```python
lm = Transformers(
    "microsoft/Phi-4-mini-instruct",
    device="cuda",
    torch_dtype="float16",      # Use FP16 (faster, less memory)
    load_in_8bit=True,          # 8-bit quantization
    max_memory={0: "20GB"},     # GPU memory limit
    offload_folder="./offload"  # Offload to disk if needed
)
```

#### 热门模型

```python
# Phi-4 (Microsoft)
lm = Transformers("microsoft/Phi-4-mini-instruct")
lm = Transformers("microsoft/Phi-3-medium-4k-instruct")

# Llama 3 (Meta)
lm = Transformers("meta-llama/Llama-3.1-8B-Instruct")
lm = Transformers("meta-llama/Llama-3.1-70B-Instruct")

# Mistral (Mistral AI)
lm = Transformers("mistralai/Mistral-7B-Instruct-v0.3")
lm = Transformers("mistralai/Mixtral-8x7B-Instruct-v0.1")

# Qwen (Alibaba)
lm = Transformers("Qwen/Qwen2.5-7B-Instruct")

# Gemma (Google)
lm = Transformers("google/gemma-2-9b-it")
```

#### 生成配置

```python
lm = Transformers(
    "microsoft/Phi-4-mini-instruct",
    device="cuda"
)

# Configure generation
from guidance import gen

result = lm + gen(
    max_tokens=100,
    temperature=0.7,
    top_p=0.9,
    top_k=50,
    repetition_penalty=1.1
)
```

### llama.cpp

#### 基本设置

```python
from guidance.models import LlamaCpp

# Load GGUF model
lm = LlamaCpp(
    model_path="/path/to/model.gguf",
    n_ctx=4096  # Context window
)
```

#### GPU配置

```python
# Use GPU acceleration
lm = LlamaCpp(
    model_path="/path/to/model.gguf",
    n_ctx=4096,
    n_gpu_layers=35,  # Offload 35 layers to GPU
    n_threads=8       # CPU threads for remaining layers
)

# Full GPU offload
lm = LlamaCpp(
    model_path="/path/to/model.gguf",
    n_ctx=4096,
    n_gpu_layers=-1  # Offload all layers
)
```

#### 高级配置

```python
lm = LlamaCpp(
    model_path="/path/to/llama-3.1-8b-instruct.Q4_K_M.gguf",
    n_ctx=8192,          # Context window (tokens)
    n_gpu_layers=35,     # GPU layers
    n_threads=8,         # CPU threads
    n_batch=512,         # Batch size for prompt processing
    use_mmap=True,       # Memory-map the model file
    use_mlock=False,     # Lock model in RAM
    seed=42,             # Random seed
    verbose=False        # Suppress verbose output
)
```

#### 量化模型

```python
# Q4_K_M (4-bit, recommended for most cases)
lm = LlamaCpp("/path/to/model.Q4_K_M.gguf")

# Q5_K_M (5-bit, better quality)
lm = LlamaCpp("/path/to/model.Q5_K_M.gguf")

# Q8_0 (8-bit, high quality)
lm = LlamaCpp("/path/to/model.Q8_0.gguf")

# F16 (16-bit float, highest quality)
lm = LlamaCpp("/path/to/model.F16.gguf")
```

#### 热门 GGUF 模型

```python
# Llama 3.1
lm = LlamaCpp("llama-3.1-8b-instruct.Q4_K_M.gguf")

# Mistral
lm = LlamaCpp("mistral-7b-instruct-v0.3.Q4_K_M.gguf")

# Phi-4
lm = LlamaCpp("phi-4-mini-instruct.Q4_K_M.gguf")
```

## 后端方案对比

### 功能矩阵

| 功能 | Anthropic | OpenAI | Transformers | llama.cpp |
|---------|-----------|--------|--------------|-----------|
| 受限生成 | ✅ 完全支持 | ✅ 完全支持 | ✅ 完全支持 | ✅ 完全支持 |
| 令牌修复 | ✅ 支持 | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| 流式处理 | ✅ 支持 | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| GPU支持 | 不适用 | 不适用 | ✅ 支持 | ✅ 支持 |
| 量化功能 | 不适用 | 不适用 | ✅ 支持 | ✅ 支持 |
| 成本 | $$$ | $$$ | 免费 | 免费 |
| 延迟时间 | 低 | 低 | 中等 | 低 |
| 部署难度 | 简单 | 简单 | 中等 | 中等 |

### 性能特点

**Anthropic Claude：**
- **延迟时间**：200-500毫秒（每次API调用）
- **处理能力**：受API调用频率限制
- **成本**：每100万输入令牌需3-15美元
- **适用场景**：生产环境、高质量输出需求

**OpenAI：**
- **延迟时间**：200-400毫秒（每次API调用）
- **处理能力**：受API调用频率限制
- **成本**：每100万输入令牌需0.15-30美元
- **适用场景**：对成本敏感的生产环境，以及gpt-4o-mini模型

**Transformers：**
- **延迟时间**：50-200毫秒（本地推理）
- **处理能力**：取决于GPU性能，约为10-100令牌/秒
- **成本**：仅硬件成本
- **适用场景**：注重隐私保护、大规模处理任务及实验场景

**llama.cpp：**
- **延迟时间**：30-150毫秒（本地推理）
- **处理能力**：取决于硬件性能，约为20-150令牌/秒
- **成本**：仅硬件成本
- **适用场景**：边缘设备部署、Apple Silicon芯片以及CPU推理场景

### 内存需求

**Transformers（FP16格式）：**
- 70亿参数模型：约需140GB GPU显存（多GPU架构）
- 130亿参数模型：约需260GB GPU显存
- 700亿参数模型：约需1400GB GPU显存（多GPU架构）

**llama.cpp（Q4_K_M量化格式）：**
- 70亿参数模型：约需4.5GB内存
- 130亿参数模型：约需8GB内存
- 700亿参数模型：约需40GB内存

**优化建议：**
- 使用量化后的模型（Q4_K_M格式）以降低内存占用
- 通过GPU卸载技术提升推理速度
- 对参数量较小的模型（<70亿参数），可使用CPU进行推理

## 性能调优

### API接口方案（Anthropic、OpenAI）

#### 降低延迟方法

```python
from guidance import models, gen

lm = models.Anthropic("claude-sonnet-4-5-20250929")

# Use lower max_tokens (faster response)
lm += gen(max_tokens=100)  # Instead of 1000

# Use streaming (perceived latency reduction)
for chunk in lm.stream(gen(max_tokens=500)):
    print(chunk, end="", flush=True)
```

#### 降低成本

```python
# Use cheaper models
lm = models.Anthropic("claude-3-5-haiku-20241022")  # vs Sonnet
lm = models.OpenAI("gpt-4o-mini")  # vs gpt-4o

# Reduce context size
# - Keep prompts concise
# - Avoid large few-shot examples
# - Use max_tokens limits
```

### 本地模型（Transformer、llama.cpp）

#### 优化GPU使用效率

```python
from guidance.models import Transformers

# Use FP16 for 2x speedup
lm = Transformers(
    "meta-llama/Llama-3.1-8B-Instruct",
    device="cuda",
    torch_dtype="float16"
)

# Use 8-bit quantization for 4x memory reduction
lm = Transformers(
    "meta-llama/Llama-3.1-8B-Instruct",
    device="cuda",
    load_in_8bit=True
)

# Use flash attention (requires flash-attn package)
lm = Transformers(
    "meta-llama/Llama-3.1-8B-Instruct",
    device="cuda",
    use_flash_attention_2=True
)
```

#### 优化 llama.cpp 性能

```python
from guidance.models import LlamaCpp

# Maximize GPU layers
lm = LlamaCpp(
    model_path="/path/to/model.Q4_K_M.gguf",
    n_gpu_layers=-1  # All layers on GPU
)

# Optimize batch size
lm = LlamaCpp(
    model_path="/path/to/model.Q4_K_M.gguf",
    n_batch=512,     # Larger batch = faster prompt processing
    n_gpu_layers=-1
)

# Use Metal (Apple Silicon)
lm = LlamaCpp(
    model_path="/path/to/model.Q4_K_M.gguf",
    n_gpu_layers=-1,  # Use Metal GPU acceleration
    use_mmap=True
)
```

#### 批量处理

```python
# Process multiple requests efficiently
requests = [
    "What is 2+2?",
    "What is the capital of France?",
    "What is photosynthesis?"
]

# Bad: Sequential processing
for req in requests:
    lm = Transformers("microsoft/Phi-4-mini-instruct")
    lm += req + gen(max_tokens=50)

# Good: Reuse loaded model
lm = Transformers("microsoft/Phi-4-mini-instruct")
for req in requests:
    lm += req + gen(max_tokens=50)
```

## 高级配置

### 自定义模型配置

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from guidance.models import Transformers

# Load custom model
tokenizer = AutoTokenizer.from_pretrained("your-model")
model = AutoModelForCausalLM.from_pretrained(
    "your-model",
    device_map="auto",
    torch_dtype="float16"
)

# Use with Guidance
lm = Transformers(model=model, tokenizer=tokenizer)
```

### 环境变量

```bash
# API keys
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# Transformers cache
export HF_HOME="/path/to/cache"
export TRANSFORMERS_CACHE="/path/to/cache"

# GPU selection
export CUDA_VISIBLE_DEVICES=0,1  # Use GPU 0 and 1
```

### 调试

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check backend info
lm = models.Anthropic("claude-sonnet-4-5-20250929")
print(f"Model: {lm.model_name}")
print(f"Backend: {lm.backend}")

# Check GPU usage (Transformers)
lm = Transformers("microsoft/Phi-4-mini-instruct", device="cuda")
print(f"Device: {lm.device}")
print(f"Memory allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
```

## 资源参考

- **Anthropic 文档**：https://docs.anthropic.com  
- **OpenAI 文档**：https://platform.openai.com/docs  
- **Hugging Face 模型库**：https://huggingface.co/models  
- **llama.cpp**：https://github.com/ggerganov/llama.cpp  
- **GGUF 模型格式**：https://huggingface.co/models?library=gguf
