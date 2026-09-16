# 性能优化

## 目录
- PagedAttention 详解
- 连续批处理机制
- 前缀缓存策略
- 推测解码配置
- 测试结果与对比分析
- 性能调优指南

## PagedAttention 详解

**传统注意力机制的问题**：
- KV 缓存存储在连续内存中
- 由于内存碎片化问题，会浪费约 50% 的 GPU 内存
- 无法根据不同的序列长度动态重新分配内存

**PagedAttention 的解决方案**：
- 将 KV 缓存划分为固定大小的块（类似操作系统的虚拟内存）
- 从空闲块队列中动态分配内存
- 在不同序列之间共享这些内存块（用于前缀缓存）

**内存节省示例**：
```
Traditional: 70B model needs 160GB KV cache → OOM on 8x A100
PagedAttention: 70B model needs 80GB KV cache → Fits on 4x A100
```

**配置**：
```bash
# Block size (default: 16 tokens)
vllm serve MODEL --block-size 16

# Number of GPU blocks (auto-calculated)
# Controlled by --gpu-memory-utilization
vllm serve MODEL --gpu-memory-utilization 0.9
```

## 持续批处理机制

**传统批处理**：
- 等待批次中的所有序列处理完成
- 在等待最耗时的序列时，GPU处于空闲状态
- GPU利用率较低（约40-60%）

**持续批处理**：
- 随着可用资源出现，立即添加新请求
- 在同一批次中同时处理预填充任务（新请求）与解码任务（正在处理的请求）
- GPU利用率极高（超过90%）

**吞吐量提升**：
```
Traditional batching: 50 req/sec @ 50% GPU util
Continuous batching: 200 req/sec @ 90% GPU util
= 4x throughput improvement
```

**调优参数**：
```bash
# Max concurrent sequences (higher = more batching)
vllm serve MODEL --max-num-seqs 256

# Prefill/decode schedule (auto-balanced by default)
# No manual tuning needed
```

## 前缀缓存策略

针对常见的提示前缀，重复使用已计算好的 KV 缓存。

**适用场景**：
- 在多个请求中重复出现的系统提示
- 每个提示中都包含的少样本示例
- 包含重叠片段的 RAG 上下文

**可实现的节省效果**：
```
Prompt: [System: 500 tokens] + [User: 100 tokens]

Without caching: Compute 600 tokens every request
With caching: Compute 500 tokens once, then 100 tokens/request
= 83% faster TTFT
```

**启用前缀缓存**：
```bash
vllm serve MODEL --enable-prefix-caching
```

**自动前缀检测**：
- vLLM 能自动识别常见前缀
- 无需修改任何代码
- 支持与 OpenAI 兼容的 API

**缓存命中率监控**：
```bash
curl http://localhost:9090/metrics | grep cache_hit
# vllm_cache_hit_rate: 0.75  (75% hit rate)
```

## 推测解码配置

使用较小的“草稿”模型来生成候选标记，再利用更大的模型进行验证。

**性能提升**：
```
Standard: Generate 1 token per forward pass
Speculative: Generate 3-5 tokens per forward pass
= 2-3x faster generation
```

**工作原理**：
1. 草稿模型快速生成 K 个令牌；
2. 目标模型并行验证这 K 个令牌（仅需一次遍历）；
3. 接受已验证的令牌，从首次被拒绝的位置重新开始。

**使用独立草稿模型的配置方式**：
```bash
vllm serve meta-llama/Llama-3-70B-Instruct \
  --speculative-model TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
  --num-speculative-tokens 5
```

**使用n-gram草稿模式进行设置**（无需单独的模型）：
```bash
vllm serve MODEL \
  --speculative-method ngram \
  --num-speculative-tokens 3
```

**适用场景**：
- 输出长度超过 100 个 token
- 草稿模型的大小为目标模型的 1/5 至 1/10
- 可接受 2-3% 的精度损失

## 基准测试结果

**vLLM 对比 HuggingFace Transformers**（Llama 3 8B，A100）：
```
Metric                  | HF Transformers | vLLM   | Improvement
------------------------|-----------------|--------|------------
Throughput (req/sec)    | 12              | 280    | 23x
TTFT (ms)              | 850             | 120    | 7x
Tokens/sec             | 45              | 2,100  | 47x
GPU Memory (GB)        | 28              | 16     | 1.75x less
```

**vLLM 与 TensorRT-LLM 的对比**（Llama 2 70B，4块A100显卡）：
```
Metric                  | TensorRT-LLM | vLLM   | Notes
------------------------|--------------|--------|------------------
Throughput (req/sec)    | 320          | 285    | TRT 12% faster
Setup complexity        | High         | Low    | vLLM much easier
NVIDIA-only            | Yes          | No     | vLLM multi-platform
Quantization support    | FP8, INT8    | AWQ/GPTQ/FP8 | vLLM more options
```

## 性能调优指南

**步骤 1：测量基准值**

```bash
# Install benchmarking tool
pip install locust

# Run baseline benchmark
vllm bench throughput \
  --model MODEL \
  --input-tokens 128 \
  --output-tokens 256 \
  --num-prompts 1000

# Record: throughput, TTFT, tokens/sec
```

**步骤 2：优化内存使用率**

```bash
# Try different values: 0.7, 0.85, 0.9, 0.95
vllm serve MODEL --gpu-memory-utilization 0.9
```

数值越高，批量处理能力越强，吞吐量也就越大，但同时也存在内存溢出的风险。

**第3步：调整并发度**

```bash
# Try values: 128, 256, 512, 1024
vllm serve MODEL --max-num-seqs 256
```

数值越高，批量处理的机会就越多，但同时也可能增加延迟。

**第4步：启用优化功能**

```bash
vllm serve MODEL \
  --enable-prefix-caching \     # For repeated prompts
  --enable-chunked-prefill \    # For long prompts
  --gpu-memory-utilization 0.9 \
  --max-num-seqs 512
```

**第5步：重新进行基准测试并对比分析**

预期提升目标：
- 吞吐量：提升30%-100%
- 平均响应时间：缩短20%-50%
- GPU利用率：保持在85%以上

**常见性能问题**：

**吞吐量过低（<50次请求/秒）**：
- 增加`--max-num-seqs`参数值
- 启用`--enable-prefix-caching`功能
- 检查GPU利用率（应高于80%）

**平均响应时间过长（>1秒）**：
- 启用`--enable-chunked-prefill`功能
- 在可能的情况下降低`--max-model-len`参数值
- 检查模型大小是否超过了GPU的处理能力

**内存不足错误**：
- 将`--gpu-memory-utilization`参数值设为0.7
- 减小`--max-model-len`参数值
- 使用量化技术（如`--quantization awq`）
