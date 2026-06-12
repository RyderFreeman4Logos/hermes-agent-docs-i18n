# 多 GPU 部署指南

关于如何在多 GPU 和多节点上扩展 TensorRT-LLM 的完整指南。

## 并行策略

### 张量并行（TP）

**功能**：将模型层在多个 GPU 之间水平分割。

**适用场景**：
- 模型大小可容纳在所有 GPU 的内存中，但无法放入单个 GPU
- 需要低延迟（单次前向传播）
- GPU 位于同一节点上（为获得最佳性能需使用 NVLink）

**示例**（在 4 块 A100 上运行 Llama 3-70B）：
```python
from tensorrt_llm import LLM

llm = LLM(
    model="meta-llama/Meta-Llama-3-70B",
    tensor_parallel_size=4,  # Split across 4 GPUs
    dtype="fp16"
)

# Model automatically sharded across GPUs
# Single forward pass, low latency
```

**性能表现**：
- 延迟：与单张 GPU 接近
- 吞吐量：高4倍（4张 GPU）
- 通信效率：高（每层参数均实现同步）

### 管道并行性（Pipeline Parallelism，PP）

**工作原理**：按层级将模型各层在多张 GPU之间进行垂直划分。

**适用场景**：
- 规模极大的模型（1750亿参数以上）
- 能够承受较高延迟
- 拥有多个节点上的 GPU

**示例**（在8张H100上运行Llama 3-405B模型）：
```python
llm = LLM(
    model="meta-llama/Meta-Llama-3-405B",
    tensor_parallel_size=4,   # TP=4 within nodes
    pipeline_parallel_size=2, # PP=2 across nodes
    dtype="fp8"
)

# Total: 8 GPUs (4×2)
# Layers 0-40: Node 1 (4 GPUs with TP)
# Layers 41-80: Node 2 (4 GPUs with TP)
```

**性能表现**：
- 延迟：较高（顺序处理整个流程）
- 吞吐量：采用微批处理时可达到较高水平
- 通信开销：低于TP模式

### 专家并行架构（EP）

**功能**：将MoE专家模型分配到多块GPU上运行。

**适用场景**：专家混合模型（如Mixtral、DeepSeek-V2）

**示例**（在8块A100上运行Mixtral-8x22B模型）：
```python
llm = LLM(
    model="mistralai/Mixtral-8x22B",
    tensor_parallel_size=4,
    expert_parallel_size=2,  # Distribute 8 experts across 2 groups
    dtype="fp8"
)
```

## 配置示例

### 小型模型（7-13B）——单块GPU

```python
# Llama 3-8B on 1× A100 80GB
llm = LLM(
    model="meta-llama/Meta-Llama-3-8B",
    dtype="fp16"  # or fp8 for H100
)
```

**资源配置**：
- GPU：1× A100 80GB
- 内存：模型约16GB + KV缓存30GB
- 处理速度：3,000–5,000个token/秒

### 中型模型（70B）——同一节点多GPU配置

```python
# Llama 3-70B on 4× A100 80GB (NVLink)
llm = LLM(
    model="meta-llama/Meta-Llama-3-70B",
    tensor_parallel_size=4,
    dtype="fp8"  # 70GB → 35GB per GPU
)
```

**资源配置**：
- GPU：4块配备NVLink接口的A100 80GB显卡
- 内存：每块GPU约35GB（FP8格式）
- 处理速度：10,000–15,000个令牌/秒
- 延迟：每个令牌15–20毫秒

### 大模型（405B）——多节点架构

```python
# Llama 3-405B on 2 nodes × 8 H100 = 16 GPUs
llm = LLM(
    model="meta-llama/Meta-Llama-3-405B",
    tensor_parallel_size=8,    # TP within each node
    pipeline_parallel_size=2,  # PP across 2 nodes
    dtype="fp8"
)
```

**资源要求**：
- GPU：2个节点，每节点配备8块80GB容量的H100显卡
- 内存：每块GPU约需25GB（支持FP8格式）
- 处理能力：每秒可处理20,000至30,000个token
- 网络：建议使用InfiniBand网络

## 服务器部署方案

### 单节点多GPU架构

```bash
# Llama 3-70B on 4 GPUs (automatic TP)
trtllm-serve meta-llama/Meta-Llama-3-70B \
    --tp_size 4 \
    --max_batch_size 256 \
    --dtype fp8

# Listens on http://localhost:8000
```

### 基于 Ray 的多节点架构

```bash
# Node 1 (head node)
ray start --head --port=6379

# Node 2 (worker)
ray start --address='node1:6379'

# Deploy across cluster
trtllm-serve meta-llama/Meta-Llama-3-405B \
    --tp_size 8 \
    --pp_size 2 \
    --num_workers 2 \  # 2 nodes
    --dtype fp8
```

### Kubernetes 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tensorrt-llm-llama3-70b
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: trtllm
        image: nvidia/tensorrt_llm:latest
        command:
          - trtllm-serve
          - meta-llama/Meta-Llama-3-70B
          - --tp_size=4
          - --max_batch_size=256
        resources:
          limits:
            nvidia.com/gpu: 4  # Request 4 GPUs
```

## 并行处理决策树

```
Model size < 20GB?
├─ YES: Single GPU (no parallelism)
└─ NO: Model size < 80GB?
    ├─ YES: TP=2 or TP=4 (same node)
    └─ NO: Model size < 320GB?
        ├─ YES: TP=4 or TP=8 (same node, NVLink required)
        └─ NO: TP=8 + PP=2 (multi-node)
```

## 通信优化

### NVLink 与 PCIe 的对比

**NVLink**（DGX A100、HGX H100）：
- 带宽：600 GB/s（A100），900 GB/s（H100）
- 非常适合需要大量通信的任务
- **推荐用于所有多 GPU 架构**

**PCIe**：
- 带宽：64 GB/s（PCIe 4.0 x16）
- 速度比 NVLink 慢 10 倍
- 应避免用于需要大量通信的任务，建议改用 PP 方式

### 多节点场景下的 InfiniBand

**HDR InfiniBand**（200 Gb/s）：
- 多节点任务或 PP 模式运行所必需
- 延迟：<1μs
- **对于 405B 及更大参数量的模型而言不可或缺**

## 多 GPU 监控

```python
# Monitor GPU utilization
nvidia-smi dmon -s u

# Monitor memory
nvidia-smi dmon -s m

# Monitor NVLink utilization
nvidia-smi nvlink --status

# TensorRT-LLM built-in metrics
curl http://localhost:8000/metrics
```

**关键指标**：
- GPU利用率：目标值为80%-95%
- 内存使用情况：各GPU之间的内存分配应保持均衡
- NVLink通信流量：TP模式下的流量较高，而PP模式下的流量较低
- 吞吐量：所有GPU的每秒token处理量

## 常见问题

### GPU内存分配不均

**现象**：GPU 0的内存使用率为90%，而GPU 3仅为40%

**解决方案**：
- 检查TP/PP配置
- 查看模型分片情况（各分片大小应相等）
- 重启服务器以重置系统状态

### NVLink利用率低

**现象**：在TP模式且数量为4的情况下，NVLink带宽低于100 GB/s

**解决方案**：
- 使用命令`nvidia-smi topo -m`检查NVLink拓扑结构
- 查看是否存在PCIe回退机制
- 确保所有GPU连接在同一块NVSwitch上

### 多GPU运行时出现内存不足问题

**解决方案**：
- 增加TP数量（即使用更多GPU）
- 减小批次大小
- 启用FP8量化技术
- 采用流水线并行处理方式

## 性能扩展方案

### TP模式下的性能扩展（Llama 3-70B，FP8格式）

| GPU数量 | TP数量 | 吞吐量 | 延迟时间 | 效率 |
|--------|--------|--------|----------|------|
| 1      | 1      | 内存不足 | -        | -    |
| 2      | 2      | 6,000 tok/s | 18ms     | 85%  |
| 4      | 4      | 11,000 tok/s | 16ms     | 78%  |
| 8      | 8      | 18,000 tok/s | 15ms     | 64%  |

**注意**：由于通信开销的增加，随着GPU数量的增多，效率会下降。

### PP模式下的性能扩展（Llama 3-405B，FP8格式）

| 节点数量 | TP数量 | PP数量 | 总GPU数量 | 吞吐量 |
|----------|--------|--------|------------|--------|
| 1        | 8      | 1      | 8          | 内存不足 |
| 2        | 8      | 2      | 16         | 25,000 tok/s |
| 4        | 8      | 4      | 32         | 45,000 tok/s |

## 最佳实践建议

1. 在可能的情况下优先选择TP模式（延迟更低）
2. 所有TP模式部署均应启用NVLink技术
3. 多节点部署时请使用InfiniBand网络
4. 先从能够将模型完整加载到内存中的最小TP数量开始测试
5. 定期监控各GPU的利用率，确保其使用情况大致均衡
6. 在正式投入生产前务必通过基准测试进行验证
7. 在H100硬件上使用FP8格式可实现2倍的速度提升
