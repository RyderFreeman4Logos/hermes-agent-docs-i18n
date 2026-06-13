# 加速性能调优

## 性能分析

### 基本性能分析

```python
from accelerate import Accelerator
import time

accelerator = Accelerator()

# Warmup
for _ in range(10):
    batch = next(iter(dataloader))
    outputs = model(**batch)
    loss = outputs.loss
    accelerator.backward(loss)
    optimizer.step()
    optimizer.zero_grad()

# Profile training loop
start = time.time()
total_batches = 100

for i, batch in enumerate(dataloader):
    if i >= total_batches:
        break

    outputs = model(**batch)
    loss = outputs.loss
    accelerator.backward(loss)
    optimizer.step()
    optimizer.zero_grad()

accelerator.wait_for_everyone()  # Sync all processes
elapsed = time.time() - start

# Metrics
batches_per_sec = total_batches / elapsed
samples_per_sec = (total_batches * batch_size * accelerator.num_processes) / elapsed

print(f"Throughput: {samples_per_sec:.2f} samples/sec")
print(f"Batches/sec: {batches_per_sec:.2f}")
```

### PyTorch Profiler集成功能

```python
from torch.profiler import profile, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True,
    with_stack=True
) as prof:
    for i, batch in enumerate(dataloader):
        if i >= 10:  # Profile first 10 batches
            break

        outputs = model(**batch)
        loss = outputs.loss
        accelerator.backward(loss)
        optimizer.step()
        optimizer.zero_grad()

# Print profiling results
print(prof.key_averages().table(
    sort_by="cuda_time_total", row_limit=20
))

# Export to Chrome tracing
prof.export_chrome_trace("trace.json")
# View at chrome://tracing
```

## 内存优化

### 1. 梯度累积

**问题**：过大的批次大小会导致内存溢出

**解决方案**：在多个小批次中累积梯度

```python
accelerator = Accelerator(gradient_accumulation_steps=8)

# Effective batch = batch_size × accumulation_steps × num_gpus
# Example: 4 × 8 × 8 = 256

for batch in dataloader:
    with accelerator.accumulate(model):  # Handles accumulation logic
        outputs = model(**batch)
        loss = outputs.loss
        accelerator.backward(loss)
        optimizer.step()
        optimizer.zero_grad()
```

**内存节省**：在采用8步累积机制的情况下，激活内存占用可减少8倍。  

### 2. 梯度检查点技术  

**在模型中启用**：

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    use_cache=False  # Required for gradient checkpointing
)

# Enable checkpointing
model.gradient_checkpointing_enable()

# Prepare with Accelerate
model = accelerator.prepare(model)
```

**内存节省效果**：可节省 30-50%，但性能会有 10-15% 的下降。

### 3. 混合精度

**BF16（A100/H100）**：
```python
accelerator = Accelerator(mixed_precision='bf16')

# Automatic mixed precision
for batch in dataloader:
    outputs = model(**batch)  # Forward in BF16
    loss = outputs.loss
    accelerator.backward(loss)  # Backward in FP32
    optimizer.step()
```

**FP16（V100及更早版本的GPU）**：
```python
from accelerate.utils import GradScalerKwargs

scaler_kwargs = GradScalerKwargs(
    init_scale=2.**16,
    growth_interval=2000
)

accelerator = Accelerator(
    mixed_precision='fp16',
    kwargs_handlers=[scaler_kwargs]
)
```

**内存占用降低**：相比 FP32 算法可节省 50% 的内存。 

### 4. CPU 卸载功能（DeepSpeed）

```python
from accelerate.utils import DeepSpeedPlugin

ds_plugin = DeepSpeedPlugin(
    zero_stage=3,
    offload_optimizer_device="cpu",  # Offload optimizer to CPU
    offload_param_device="cpu",      # Offload parameters to CPU
)

accelerator = Accelerator(
    deepspeed_plugin=ds_plugin,
    mixed_precision='bf16'
)
```

**内存节省效果**：优化器状态可节省10-20倍内存，参数则可节省5-10倍内存。

**权衡因素**：由于需要在CPU与GPU之间进行数据传输，处理速度会降低20-30%。

### 5. Flash Attention

```python
# Install flash-attn
# pip install flash-attn

from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    attn_implementation="flash_attention_2"  # Enable Flash Attention 2
)

model = accelerator.prepare(model)
```

**内存节省效果**：注意力机制相关内存减少50%，处理速度提升2倍。

**系统要求**：需使用A100/H100芯片，序列长度须为128的整数倍。

## 通信优化

### 1. 梯度分桶技术（DDP）

```python
from accelerate.utils import DistributedDataParallelKwargs

ddp_kwargs = DistributedDataParallelKwargs(
    bucket_cap_mb=25,  # Bucket size for gradient reduction
    gradient_as_bucket_view=True,  # Reduce memory copies
    static_graph=False  # Set True if model doesn't change
)

accelerator = Accelerator(kwargs_handlers=[ddp_kwargs])
```

**推荐的存储桶大小**：
- 小型模型（<10亿参数）：25 MB
- 中型模型（1-100亿参数）：50-100 MB
- 大型模型（>100亿参数）：100-200 MB

### 2. 查找未使用的参数

```python
# Only enable if model has unused parameters (slower!)
ddp_kwargs = DistributedDataParallelKwargs(
    find_unused_parameters=True
)
```

**应用场景**：包含条件分支的模型（例如专家混合模型）

**成本影响**：性能降低10-20%

### 3. NCCL参数调优

```bash
# Set environment variables before launch
export NCCL_DEBUG=INFO           # Debug info
export NCCL_IB_DISABLE=0         # Enable InfiniBand
export NCCL_SOCKET_IFNAME=eth0   # Network interface
export NCCL_P2P_LEVEL=NVL        # Use NVLink

accelerate launch train.py
```

**NCCL_P2P_LEVEL 参数选项**：
- `NVL`：NVLink（最快，节点内部传输）
- `PIX`：PCIe（较快，节点内部传输）
- `PHB`：PCIe主机桥接器（较慢，跨节点传输）

## 数据加载优化

### 1. DataLoader工作进程

```python
from torch.utils.data import DataLoader

train_loader = DataLoader(
    dataset,
    batch_size=32,
    num_workers=4,      # Parallel data loading
    pin_memory=True,    # Pin memory for faster GPU transfer
    prefetch_factor=2,  # Prefetch batches per worker
    persistent_workers=True  # Keep workers alive between epochs
)

train_loader = accelerator.prepare(train_loader)
```

**推荐参数**：
- `num_workers`：每张 GPU 配置 2-4 个进程（8 张 GPU 时对应 16-32 个进程）
- `pin_memory`：在 GPU 训练模式下始终设置为 True
- `prefetch_factor`：数值范围为 2-4（数据加载速度较慢时可适当调高该值）

### 2. 数据预处理

```python
from datasets import load_dataset

# Bad: Preprocess during training (slow)
dataset = load_dataset("openwebtext")

for batch in dataset:
    tokens = tokenizer(batch['text'])  # Slow!
    ...

# Good: Preprocess once, save
dataset = load_dataset("openwebtext")
tokenized = dataset.map(
    lambda x: tokenizer(x['text']),
    batched=True,
    num_proc=8,  # Parallel preprocessing
    remove_columns=['text']
)
tokenized.save_to_disk("preprocessed_data")

# Load preprocessed
dataset = load_from_disk("preprocessed_data")
```

### 3. 更快速的令牌化处理

```python
import os

# Enable Rust-based tokenizers (10× faster)
os.environ["TOKENIZERS_PARALLELISM"] = "true"

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "gpt2",
    use_fast=True  # Use fast Rust tokenizer
)
```

## 编译（PyTorch 2.0+）

### 模型编译

```python
import torch

# Compile model for faster execution
model = torch.compile(
    model,
    mode="reduce-overhead",  # Options: default, reduce-overhead, max-autotune
    fullgraph=False,         # Compile entire graph (stricter)
    dynamic=True             # Support dynamic shapes
)

model = accelerator.prepare(model)
```

**加速效果**：根据模型不同，加速幅度为 10% 至 50% 不等。

**编译模式**：
- `default`：均衡模式（适用于大多数场景）
- `reduce-overhead`：最小开销模式（适合处理小批量数据）
- `max-autotune`：最大性能模式（编译速度较慢，但最适合生产环境使用）

### 编译最佳实践

```python
# Bad: Compile after prepare (won't work)
model = accelerator.prepare(model)
model = torch.compile(model)  # Error!

# Good: Compile before prepare
model = torch.compile(model)
model = accelerator.prepare(model)

# Training loop
for batch in dataloader:
    # First iteration: slow (compilation)
    # Subsequent iterations: fast (compiled)
    outputs = model(**batch)
    ...
```

## 不同策略的基准测试

### 脚本模板

```python
import time
import torch
from accelerate import Accelerator

def benchmark_strategy(strategy_name, accelerator_kwargs):
    """Benchmark a specific training strategy."""
    accelerator = Accelerator(**accelerator_kwargs)

    # Setup
    model = create_model()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    dataloader = create_dataloader()

    model, optimizer, dataloader = accelerator.prepare(
        model, optimizer, dataloader
    )

    # Warmup
    for i, batch in enumerate(dataloader):
        if i >= 10:
            break
        outputs = model(**batch)
        loss = outputs.loss
        accelerator.backward(loss)
        optimizer.step()
        optimizer.zero_grad()

    # Benchmark
    accelerator.wait_for_everyone()
    torch.cuda.synchronize()
    start = time.time()

    num_batches = 100
    for i, batch in enumerate(dataloader):
        if i >= num_batches:
            break

        outputs = model(**batch)
        loss = outputs.loss
        accelerator.backward(loss)
        optimizer.step()
        optimizer.zero_grad()

    accelerator.wait_for_everyone()
    torch.cuda.synchronize()
    elapsed = time.time() - start

    # Metrics
    throughput = (num_batches * batch_size * accelerator.num_processes) / elapsed
    memory_used = torch.cuda.max_memory_allocated() / 1e9  # GB

    if accelerator.is_main_process:
        print(f"\n{strategy_name}:")
        print(f"  Throughput: {throughput:.2f} samples/sec")
        print(f"  Memory: {memory_used:.2f} GB")
        print(f"  Time: {elapsed:.2f} sec")

    torch.cuda.reset_peak_memory_stats()

# Benchmark different strategies
strategies = [
    ("DDP + FP32", {}),
    ("DDP + BF16", {"mixed_precision": "bf16"}),
    ("DDP + BF16 + GradAccum", {"mixed_precision": "bf16", "gradient_accumulation_steps": 4}),
    ("FSDP", {"fsdp_plugin": fsdp_plugin}),
    ("DeepSpeed ZeRO-2", {"deepspeed_plugin": ds_plugin_stage2}),
    ("DeepSpeed ZeRO-3", {"deepspeed_plugin": ds_plugin_stage3}),
]

for name, kwargs in strategies:
    benchmark_strategy(name, kwargs)
```

## 性能检查清单

**训练前**：
- [ ] 使用 BF16/FP16 混合精度格式
- [ ] 启用梯度检查点机制（若出现内存不足情况）
- [ ] 设置合适的 `num_workers` 值（每块 GPU 2-4 个）
- [ ] 设置 `pin_memory=True`
- [ ] 仅预处理一次数据，而非在训练过程中重复处理
- [ ] 使用 `torch.compile` 编译模型（需 PyTorch 2.0 及以上版本）

**针对大型模型**：
- [ ] 使用 FSDP 或 DeepSpeed ZeRO-3
- [ ] 启用 CPU 卸载功能（若仍存在内存不足问题）
- [ ] 使用 Flash Attention 技术
- [ ] 增加梯度累积次数

**多节点部署场景**：
- [ ] 检查网络拓扑结构（优先选择 InfiniBand，次选以太网）
- [ ] 调整 NCCL 相关设置
- [ ] 为 DDP 模型使用更大的缓冲区大小
- [ ] 确认支持张量并行计算的 NVLink 功能已正常启用

**性能分析**：
- [ ] 对前 10-100 个训练批次进行性能分析
- [ ] 查看 GPU 使用率（可使用 `nvidia-smi dmon` 工具）
- [ ] 检查数据加载时间（应不超过单次迭代时间的 5%）
- [ ] 识别通信过程中的瓶颈问题

## 常见性能问题

### 问题：GPU 使用率偏低（<80%）

**原因 1**：数据加载环节存在瓶颈
```python
# Solution: Increase workers and prefetch
num_workers=8
prefetch_factor=4
```

**原因 2**：批次大小过小
```python
# Solution: Increase batch size or use gradient accumulation
batch_size=32  # Increase
gradient_accumulation_steps=4  # Or accumulate
```

### 问题：内存占用过高

**解决方案 1**：梯度检查点技术
```python
model.gradient_checkpointing_enable()
```

**解决方案 2**：减小批次大小，增加累积次数。
```python
batch_size=8  # Reduce from 32
gradient_accumulation_steps=16  # Maintain effective batch
```

**解决方案 3**：使用 FSDP 或 DeepSpeed ZeRO-3
```python
accelerator = Accelerator(fsdp_plugin=fsdp_plugin)
```

### 问题：多 GPU 训练速度过慢

**原因**：通信瓶颈

**检查项 1**：梯度桶大小
```python
ddp_kwargs = DistributedDataParallelKwargs(bucket_cap_mb=100)
```

**检查项2**：NCCL配置设置
```bash
export NCCL_DEBUG=INFO
# Check for "Using NVLS" (good) vs "Using PHB" (bad)
```

**检查项3**：网络带宽
```bash
# Test inter-GPU bandwidth
nvidia-smi nvlink -s
```

## 资源参考

- 提升性能：https://huggingface.co/docs/accelerate/usage_guides/performance
- PyTorch Profiler 工具：https://pytorch.org/tutorials/recipes/recipes/profiler_recipe.html
- NCCL 参数调优指南：https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html
- Flash Attention 技术：https://github.com/Dao-AILab/flash-attention
