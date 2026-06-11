# TensorRT-LLM 优化指南

关于如何使用 TensorRT-LLM 对大语言模型推理进行优化的完整指南。

## 量化

### FP8 量化（推荐用于 H100）

**优势**：
- 推理速度提升 2 倍
- 内存占用减少 50%
- 准确度损失极小（困惑度下降不足 1%）

**使用方法**：
```python
from tensorrt_llm import LLM

# Automatic FP8 quantization
llm = LLM(
    model="meta-llama/Meta-Llama-3-70B",
    dtype="fp8",
    quantization="fp8"
)
```

**性能表现**（基于8块H100芯片的Llama 3-70B模型）：
- FP16格式：5,000个标记/秒
- FP8格式：**10,000个标记/秒**（速度提升2倍）
- 内存占用：从140GB降至70GB

### INT4量化格式（极致压缩效果）

**优势**：
- 内存占用减少4倍
- 推理速度提升3-4倍
- 可在相同硬件上运行更大的模型

**使用方法**：
```python
# INT4 with AWQ calibration
llm = LLM(
    model="meta-llama/Meta-Llama-3-405B",
    dtype="int4_awq",
    quantization="awq"
)

# INT4 with GPTQ calibration
llm = LLM(
    model="meta-llama/Meta-Llama-3-405B",
    dtype="int4_gptq",
    quantization="gptq"
)
```

**权衡因素**：
- 精度：困惑度增加 1-3%
- 速度：比 FP16 快 3-4 倍
- 适用场景：内存资源极为紧张的情况

## 在线批处理

**功能说明**：在生成过程中动态对请求进行批处理，而无需等待所有序列处理完成。

**配置选项**：
```python
# Server configuration
trtllm-serve meta-llama/Meta-Llama-3-8B \
    --max_batch_size 256 \           # Maximum concurrent sequences
    --max_num_tokens 4096 \           # Total tokens in batch
    --enable_chunked_context \        # Split long prompts
    --scheduler_policy max_utilization
```

**性能表现**：
- 吞吐量：相比静态批量处理，提升 **4-8倍** 
- 延迟：在混合工作负载场景下，P50/P99值更低
- GPU利用率：可达80-95%，而静态批量处理仅为40-60%

## 分页KV缓存

**功能说明**：类似操作系统管理虚拟内存的方式，对KV缓存内存进行分页管理。

**优势**：
- 吞吐量提升40-60%
- 无内存碎片问题
- 能支持更长的序列处理

**配置选项**：
```python
# Automatic paged KV cache (default)
llm = LLM(
    model="meta-llama/Meta-Llama-3-8B",
    kv_cache_free_gpu_mem_fraction=0.9,  # Use 90% GPU mem for cache
    enable_prefix_caching=True            # Cache common prefixes
)
```

## 推测解码

**功能说明**：利用小型草案模型预测多个标记，再由目标模型同步进行验证。

**加速效果**：在长文本生成场景下，速度可提升2-3倍。

**使用方式**：
```python
from tensorrt_llm import LLM

# Target model (Llama 3-70B)
llm = LLM(
    model="meta-llama/Meta-Llama-3-70B",
    speculative_model="meta-llama/Meta-Llama-3-8B",  # Draft model
    num_speculative_tokens=5                          # Tokens to predict ahead
)

# Same API, 2-3× faster
outputs = llm.generate(prompts)
```

**最适合用于草稿生成的模型**：
- 输入模型：Llama 3-70B → 输出模型：Llama 3-8B
- 输入模型：Qwen2-72B → 输出模型：Qwen2-7B
- 同系列模型，规模缩小8-10倍

## CUDA Graphs

**功能说明**：通过记录GPU操作来降低内核启动的开销。

**优势**：
- 延迟降低10-20%
- P99延迟更加稳定
- 更适合处理小批量数据

**配置选项**（默认为自动配置）：
```python
llm = LLM(
    model="meta-llama/Meta-Llama-3-8B",
    enable_cuda_graph=True,  # Default: True
    cuda_graph_cache_size=2  # Cache 2 graph variants
)
```

## 分块上下文

**功能说明**：将过长的提示语拆分为多个分块，从而降低内存占用峰值。

**适用场景**：提示语长度超过8K个标记，且GPU内存资源有限的情况。

**配置选项**：
```bash
trtllm-serve meta-llama/Meta-Llama-3-8B \
    --max_num_tokens 4096 \
    --enable_chunked_context \
    --max_chunked_prefill_length 2048  # Process 2K tokens at a time
```

## 重叠调度

**功能说明**：同时执行计算与内存操作。

**优势**：
- 吞吐量提升15-25%
- GPU利用率更高
- v1.2.0+版本默认启用

**无需配置**——系统会自动开启该功能。

## 量化方案对比表

| 方案 | 内存占用 | 计算速度 | 精度损失 | 适用场景 |
|------|----------|----------|----------|----------|
| FP16 | 1倍（基准值） | 1倍 | 最高精度 | 需要极高精度的场景 |
| FP8 | 0.5倍 | 2倍 | 准确率下降0.5% | **H100默认方案** |
| INT4 AWQ | 0.25倍 | 3-4倍 | 准确率下降1.5% | 内存资源极为紧张的场景 |
| INT4 GPTQ | 0.25倍 | 3-4倍 | 准确率下降2% | 需要最高计算速度的场景 |

## 调优流程

1. **从默认设置开始**：
   ```python
   llm = LLM(model="meta-llama/Meta-Llama-3-70B")
   ```

2. **启用 FP8 模式**（如使用 H100 硬件）：
   ```python
   llm = LLM(model="...", dtype="fp8")
   ```

3. **调整批量大小**：
   ```python
   # Increase until OOM, then reduce 20%
   trtllm-serve ... --max_batch_size 256
   ```

4. **启用分块上下文功能**（适用于较长的提示词）：
   ```bash
   --enable_chunked_context --max_chunked_prefill_length 2048
   ```

5. **尝试推测性解码**（在延迟要求极高的情况下）：
   ```python
   llm = LLM(model="...", speculative_model="...")
   ```

## 性能基准测试

```bash
# Install benchmark tool
pip install tensorrt_llm[benchmark]

# Run benchmark
python benchmarks/python/benchmark.py \
    --model meta-llama/Meta-Llama-3-8B \
    --batch_size 64 \
    --input_len 128 \
    --output_len 256 \
    --dtype fp8
```

**需监控的指标**：
- 处理吞吐量（token/秒）
- 延迟 P50/P90/P99（毫秒）
- GPU 内存使用量（GB）
- GPU 利用率（%）

## 常见问题

**内存不足错误**：
- 减小 `max_batch_size` 的值
- 降低 `max_num_tokens` 的数值
- 启用 INT4 量化功能
- 提高 `tensor_parallel_size` 的值

**处理吞吐量低**：
- 增大 `max_batch_size` 的值
- 启用传输中批量处理功能
- 确认已启用 CUDA 图形优化
- 检查 GPU 利用率情况

**延迟过高**：
- 尝试使用推测解码技术
- 减小 `max_batch_size` 的值以减少排队时间
- 使用 FP8 格式而非 FP16 格式
