# Megatron 与 Accelerate 的集成

## 概述

Accelerate 支持利用张量并行与流水线并行技术，为大规模模型训练提供 Megatron-LM 的支持。

**Megatron 的功能特性**：
- **张量并行（TP）**：在多块 GPU 之间分配层结构
- **流水线并行（PP）**：在多块 GPU 之间分配模型深度
- **数据并行（DP）**：在 GPU 组之间复制模型
- **序列并行**：针对长上下文对序列进行拆分

## 设置步骤

### 安装 Megatron-LM

```bash
# Clone Megatron-LM repository
git clone https://github.com/NVIDIA/Megatron-LM.git
cd Megatron-LM
pip install -e .

# Install Apex (NVIDIA optimizations)
git clone https://github.com/NVIDIA/apex
cd apex
pip install -v --disable-pip-version-check --no-cache-dir --no-build-isolation \
  --config-settings "--build-option=--cpp_ext" --config-settings "--build-option=--cuda_ext" ./
```

### 加速配置流程

```bash
accelerate config
```

**问题**：
```
In which compute environment are you running?
> This machine

Which type of machine are you using?
> Multi-GPU

How many different machines will you use?
> 1

Do you want to use DeepSpeed/FSDP?
> No

Do you want to use Megatron-LM?
> Yes

What is the Tensor Parallelism degree? [1-8]
> 2

Do you want to enable Sequence Parallelism?
> No

What is the Pipeline Parallelism degree? [1-8]
> 2

What is the Data Parallelism degree? [1-8]
> 2

Where to perform activation checkpointing? ['SELECTIVE', 'FULL', 'NONE']
> SELECTIVE

Where to perform activation partitioning? ['SEQUENTIAL', 'UNIFORM']
> SEQUENTIAL
```

**生成的配置文件**（`~/.cache/huggingface/accelerate/default_config.yaml`）：
```yaml
compute_environment: LOCAL_MACHINE
distributed_type: MEGATRON_LM
downcast_bf16: 'no'
machine_rank: 0
main_training_function: main
megatron_lm_config:
  megatron_lm_gradient_clipping: 1.0
  megatron_lm_learning_rate_decay_iters: 320000
  megatron_lm_num_micro_batches: 1
  megatron_lm_pp_degree: 2
  megatron_lm_recompute_activations: true
  megatron_lm_sequence_parallelism: false
  megatron_lm_tp_degree: 2
mixed_precision: bf16
num_machines: 1
num_processes: 8
rdzv_backend: static
same_network: true
tpu_env: []
tpu_use_cluster: false
tpu_use_sudo: false
use_cpu: false
```

## 并行策略

### 张量并行（TP）

**将每个Transformer层分配到不同的GPU上**：

```python
# Layer split across 2 GPUs
# GPU 0: First half of attention heads
# GPU 1: Second half of attention heads

# Each GPU computes partial outputs
# All-reduce combines results
```

**张量并行度建议**：
- **TP=1**：无张量并行（每层使用单块 GPU）
- **TP=2**：每层使用 2 块 GPU（适用于 7-13B 参数模型）
- **TP=4**：每层使用 4 块 GPU（适用于 20-40B 参数模型）
- **TP=8**：每层使用 8 块 GPU（适用于 70B 及以上参数模型）

**优势**：
- 降低每块 GPU 的内存需求
- 支持全连接通信（传输速度快）

**缺点**：
- 需要较高的 GPU 间带宽（如 NVLink）
- 每层都会产生通信开销

### 管道并行（PP）

**将模型深度分配到多块 GPU 上**：

```python
# 12-layer model, PP=4
# GPU 0: Layers 0-2
# GPU 1: Layers 3-5
# GPU 2: Layers 6-8
# GPU 3: Layers 9-11
```

**流水线并行度建议**：
- **PP=1**：无流水线并行
- **PP=2**：2个流水线阶段（适用于20-40B模型）
- **PP=4**：4个流水线阶段（适用于70B及以上模型）
- **PP=8**：8个流水线阶段（适用于175B及以上模型）

**优势**：
- 内存占用呈线性降低（PP值每增加4倍，内存使用量减少4倍）
- 支持跨节点运行（网络传输延迟较高亦可接受）

**缺点**：
- 会出现流水线空闲时间
- 需要采用微批处理技术

### 数据并行（DP）

**在多个GPU组之间复制模型**：

```python
# 8 GPUs, TP=2, PP=2, DP=2
# Group 0 (GPUs 0-3): Full model replica
# Group 1 (GPUs 4-7): Full model replica
```

**DP等级**：
- `DP = total_gpus / (TP × PP)`
- 示例：8块GPU，TP=2，PP=2 → DP=2

**优势**：
- 提高吞吐量
- 支持扩大批次大小

### 序列并行处理

**将长序列分配到多块GPU上处理**（从而增加TP值）：

```python
# 8K sequence, TP=2, Sequence Parallel=True
# GPU 0: Tokens 0-4095
# GPU 1: Tokens 4096-8191
```

**优势**：
- 支持处理极长的序列（10万以上标记）
- 减少激活内存占用

**要求**：
- 必须搭配 TP > 1 的配置使用
- RoPE/ALiBi 位置编码效果最佳

## 加速代码示例

### 基本设置

```python
from accelerate import Accelerator
from accelerate.utils import MegatronLMPlugin

# Configure Megatron
megatron_plugin = MegatronLMPlugin(
    tp_degree=2,              # Tensor parallelism degree
    pp_degree=2,              # Pipeline parallelism degree
    num_micro_batches=4,      # Micro-batches for pipeline
    gradient_clipping=1.0,    # Gradient clipping value
    sequence_parallelism=False,  # Enable sequence parallelism
    recompute_activations=True,  # Activation checkpointing
    use_distributed_optimizer=True,  # Distributed optimizer
    custom_prepare_model_function=None,  # Custom model prep
)

# Initialize accelerator
accelerator = Accelerator(
    mixed_precision='bf16',
    megatron_lm_plugin=megatron_plugin
)

# Prepare model and optimizer
model, optimizer, train_dataloader = accelerator.prepare(
    model, optimizer, train_dataloader
)

# Training loop (same as DDP!)
for batch in train_dataloader:
    optimizer.zero_grad()
    outputs = model(**batch)
    loss = outputs.loss
    accelerator.backward(loss)
    optimizer.step()
```

### 完整训练脚本

```python
import torch
from accelerate import Accelerator
from accelerate.utils import MegatronLMPlugin
from transformers import GPT2Config, GPT2LMHeadModel

def main():
    # Megatron configuration
    megatron_plugin = MegatronLMPlugin(
        tp_degree=2,
        pp_degree=2,
        num_micro_batches=4,
        gradient_clipping=1.0,
    )

    accelerator = Accelerator(
        mixed_precision='bf16',
        gradient_accumulation_steps=8,
        megatron_lm_plugin=megatron_plugin
    )

    # Model
    config = GPT2Config(
        n_layer=24,
        n_head=16,
        n_embd=1024,
    )
    model = GPT2LMHeadModel(config)

    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=6e-4)

    # Prepare
    model, optimizer, train_loader = accelerator.prepare(
        model, optimizer, train_loader
    )

    # Training loop
    for epoch in range(num_epochs):
        for batch in train_loader:
            with accelerator.accumulate(model):
                outputs = model(**batch)
                loss = outputs.loss
                accelerator.backward(loss)
                optimizer.step()
                optimizer.zero_grad()

        # Save checkpoint
        accelerator.wait_for_everyone()
        accelerator.save_state(f'checkpoint-epoch-{epoch}')

if __name__ == '__main__':
    main()
```

### 启动命令

```bash
# 8 GPUs, TP=2, PP=2, DP=2
accelerate launch --multi_gpu --num_processes 8 train.py

# Multi-node (2 nodes, 8 GPUs each)
# Node 0
accelerate launch --multi_gpu --num_processes 16 \
  --num_machines 2 --machine_rank 0 \
  --main_process_ip $MASTER_ADDR \
  --main_process_port 29500 \
  train.py

# Node 1
accelerate launch --multi_gpu --num_processes 16 \
  --num_machines 2 --machine_rank 1 \
  --main_process_ip $MASTER_ADDR \
  --main_process_port 29500 \
  train.py
```

## 激活值检查点机制

**通过重新计算激活值来降低内存占用**：

```python
megatron_plugin = MegatronLMPlugin(
    recompute_activations=True,      # Enable checkpointing
    checkpoint_num_layers=1,         # Checkpoint every N layers
    distribute_checkpointed_activations=True,  # Distribute across TP
    partition_activations=True,      # Partition in PP
    check_for_nan_in_loss_and_grad=True,  # Stability check
)
```

**策略**：
- `SELECTIVE`：仅对Transformer块进行检查点保存
- `FULL`：对所有层进行检查点保存
- `NONE`：不进行任何检查点保存

**内存节省效果**：可节省30-50%的内存，但性能会下降10-15%。

## 分布式优化器

**在多个DP节点间分配优化器状态**：

```python
megatron_plugin = MegatronLMPlugin(
    use_distributed_optimizer=True,  # Enable sharded optimizer
)
```

**优势**：
- 根据差分隐私阶数减少优化器内存占用
- 示例：当差分隐私阶数为 4 时，每张 GPU 的优化器内存占用可降低 4 倍

**兼容算法**：
- AdamW、Adam、SGD
- 混合精度训练

## 性能调优

### 小批量大小

```python
# Pipeline parallelism requires micro-batching
megatron_plugin = MegatronLMPlugin(
    pp_degree=4,
    num_micro_batches=16,  # 16 micro-batches per pipeline
)

# Effective batch = num_micro_batches × micro_batch_size × DP
# Example: 16 × 2 × 4 = 128
```

**推荐设置**：
- 增加微批次数量 → 减少流水线延迟
- 典型数值：4-16个微批次

### 序列长度

```python
# For long sequences, enable sequence parallelism
megatron_plugin = MegatronLMPlugin(
    tp_degree=4,
    sequence_parallelism=True,  # Required: TP > 1
)

# Enables sequences up to TP × normal limit
# Example: TP=4, 8K normal → 32K with sequence parallel
```

### GPU拓扑结构

**TP功能需启用NVLink**：
```bash
# Check NVLink topology
nvidia-smi topo -m

# Good topology (NVLink between all GPUs)
# GPU0 - GPU1: NV12 (fast)
# GPU0 - GPU2: NV12 (fast)

# Bad topology (PCIe only)
# GPU0 - GPU4: PHB (slow, avoid TP across these)
```

**推荐配置**：
- **TP**：同一节点内（支持 NVLink）
- **PP**：跨节点之间（允许较慢的互连速度）
- **DP**：任意拓扑结构

## 模型规模指南

| 模型规模 | GPU 数量 | TP | PP | DP | 微批次大小 |
|----------|----------|----|----|----|------------|
| 7B       | 8        | 1  | 1  | 8  | 1          |
| 13B      | 8        | 2  | 1  | 4  | 1          |
| 20B      | 16       | 4  | 1  | 4  | 1          |
| 40B      | 32       | 4  | 2  | 4  | 4          |
| 70B      | 64       | 8  | 2  | 4  | 8          |
| 175B     | 128      | 8  | 4  | 4  | 16         |

**假设条件**：BF16 编码格式，序列长度为 2K，使用 A100 80GB 显卡

## 检查点保存

### 保存检查点

```python
# Save full model state
accelerator.save_state('checkpoint-1000')

# Megatron saves separate files per rank
# checkpoint-1000/
#   pytorch_model_tp_0_pp_0.bin
#   pytorch_model_tp_0_pp_1.bin
#   pytorch_model_tp_1_pp_0.bin
#   pytorch_model_tp_1_pp_1.bin
#   optimizer_tp_0_pp_0.bin
#   ...
```

### 加载检查点

```python
# Resume training
accelerator.load_state('checkpoint-1000')

# Automatically loads correct shard per rank
```

### 转换为标准 PyTorch 格式

```bash
# Merge Megatron checkpoint to single file
python merge_megatron_checkpoint.py \
  --checkpoint-dir checkpoint-1000 \
  --output pytorch_model.bin
```

## 常见问题

### 问题：管道并行处理时出现内存不足（OOM）现象

**解决方案**：增加微批次大小
```python
megatron_plugin = MegatronLMPlugin(
    pp_degree=4,
    num_micro_batches=16,  # Increase from 4
)
```

### 问题：训练速度过慢

**检查项 1**：管道气泡现象（PP值过高）
```python
# Reduce PP, increase TP
tp_degree=4  # Increase
pp_degree=2  # Decrease
```

**检查项2**：微批次大小过小
```python
num_micro_batches=8  # Increase
```

### 问题：未检测到 NVLink

```bash
# Verify NVLink
nvidia-smi nvlink -s

# If no NVLink, avoid TP > 1
# Use PP or DP instead
```

## 资源参考

- Megatron-LM：https://github.com/NVIDIA/Megatron-LM  
- Accelerate Megatron 使用文档：https://huggingface.co/docs/accelerate/usage_guides/megatron_lm  
- 相关论文：《Megatron-LM：利用模型并行技术训练数十亿参数级语言模型》  
- NVIDIA Apex：https://github.com/NVIDIA/apex
