---
name: huggingface-accelerate
description: Simplest distributed training API. 4 lines to add distributed support to any PyTorch script. Unified API for DeepSpeed/FSDP/Megatron/DDP. Automatic device placement, mixed precision (FP16/BF16/FP8). Interactive config, single launch command. HuggingFace ecosystem standard.
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [accelerate, torch, transformers]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Distributed Training, HuggingFace, Accelerate, DeepSpeed, FSDP, Mixed Precision, PyTorch, DDP, Unified API, Simple]

---

# HuggingFace Accelerate——统一的分布式训练解决方案

## 快速入门

Accelerate 将分布式训练的实现简化为仅 4 行代码。

**安装**：
```bash
pip install accelerate
```

**转换 PyTorch 脚本**（4 行）：
```python
import torch
+ from accelerate import Accelerator

+ accelerator = Accelerator()

  model = torch.nn.Transformer()
  optimizer = torch.optim.Adam(model.parameters())
  dataloader = torch.utils.data.DataLoader(dataset)

+ model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)

  for batch in dataloader:
      optimizer.zero_grad()
      loss = model(batch)
-     loss.backward()
+     accelerator.backward(loss)
      optimizer.step()
```

**运行**（单条命令）：
```bash
accelerate launch train.py
```

## 常见工作流

### 工作流 1：从单 GPU 过渡到多 GPU

**原始脚本**：
```python
# train.py
import torch

model = torch.nn.Linear(10, 2).to('cuda')
optimizer = torch.optim.Adam(model.parameters())
dataloader = torch.utils.data.DataLoader(dataset, batch_size=32)

for epoch in range(10):
    for batch in dataloader:
        batch = batch.to('cuda')
        optimizer.zero_grad()
        loss = model(batch).mean()
        loss.backward()
        optimizer.step()
```

**启用 Accelerate 功能**（新增 4 行）：
```python
# train.py
import torch
from accelerate import Accelerator  # +1

accelerator = Accelerator()  # +2

model = torch.nn.Linear(10, 2)
optimizer = torch.optim.Adam(model.parameters())
dataloader = torch.utils.data.DataLoader(dataset, batch_size=32)

model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)  # +3

for epoch in range(10):
    for batch in dataloader:
        # No .to('cuda') needed - automatic!
        optimizer.zero_grad()
        loss = model(batch).mean()
        accelerator.backward(loss)  # +4
        optimizer.step()
```

**配置**（交互模式）：
```bash
accelerate config
```

**问题选项**：
- 使用哪种计算设备？（单 GPU/多 GPU/TPU/CPU）
- 需要多少台设备？（1 台）
- 是否使用混合精度？（否/fp16/bf16/fp8）
- 是否启用 DeepSpeed？（否/是）

**启动操作**（适用于所有配置环境）：
```bash
# Single GPU
accelerate launch train.py

# Multi-GPU (8 GPUs)
accelerate launch --multi_gpu --num_processes 8 train.py

# Multi-node
accelerate launch --multi_gpu --num_processes 16 \
  --num_machines 2 --machine_rank 0 \
  --main_process_ip $MASTER_ADDR \
  train.py
```

### 工作流 2：混合精度训练

**启用 FP16/BF16**：
```python
from accelerate import Accelerator

# FP16 (with gradient scaling)
accelerator = Accelerator(mixed_precision='fp16')

# BF16 (no scaling, more stable)
accelerator = Accelerator(mixed_precision='bf16')

# FP8 (H100+)
accelerator = Accelerator(mixed_precision='fp8')

model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)

# Everything else is automatic!
for batch in dataloader:
    with accelerator.autocast():  # Optional, done automatically
        loss = model(batch)
    accelerator.backward(loss)
```

### 工作流 3：DeepSpeed ZeRO 集成

**启用 DeepSpeed ZeRO-2**：
```python
from accelerate import Accelerator

accelerator = Accelerator(
    mixed_precision='bf16',
    deepspeed_plugin={
        "zero_stage": 2,  # ZeRO-2
        "offload_optimizer": False,
        "gradient_accumulation_steps": 4
    }
)

# Same code as before!
model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)
```

**或通过配置文件**：
```bash
accelerate config
# Select: DeepSpeed → ZeRO-2
```

**deepspeed_config.json**：
深度速度配置文件：
```json
{
    "fp16": {"enabled": false},
    "bf16": {"enabled": true},
    "zero_optimization": {
        "stage": 2,
        "offload_optimizer": {"device": "cpu"},
        "allgather_bucket_size": 5e8,
        "reduce_bucket_size": 5e8
    }
}
```

**启动**：
```bash
accelerate launch --config_file deepspeed_config.json train.py
```

### 工作流 4：FSDP（完全分片数据并行）

**启用 FSDP**：
```python
from accelerate import Accelerator, FullyShardedDataParallelPlugin

fsdp_plugin = FullyShardedDataParallelPlugin(
    sharding_strategy="FULL_SHARD",  # ZeRO-3 equivalent
    auto_wrap_policy="TRANSFORMER_AUTO_WRAP",
    cpu_offload=False
)

accelerator = Accelerator(
    mixed_precision='bf16',
    fsdp_plugin=fsdp_plugin
)

model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)
```

**或通过配置文件**：
```bash
accelerate config
# Select: FSDP → Full Shard → No CPU Offload
```

### 工作流 5：梯度累积

**累积梯度**：
```python
from accelerate import Accelerator

accelerator = Accelerator(gradient_accumulation_steps=4)

model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)

for batch in dataloader:
    with accelerator.accumulate(model):  # Handles accumulation
        optimizer.zero_grad()
        loss = model(batch)
        accelerator.backward(loss)
        optimizer.step()
```

**有效批量大小**：`batch_size * num_gpus * gradient_accumulation_steps`

## 何时使用 Accelerate 及其替代方案

**应在以下情况使用 Accelerate**：
- 需要最简单的分布式训练方式
- 需要适用于任何硬件的单脚本解决方案
- 使用 HuggingFace 生态系统
- 追求灵活性（DDP/DeepSpeed/FSDP/Megatron）
- 需要快速进行原型开发

**主要优势**：
- **仅需 4 行代码**：几乎无需修改现有代码
- **统一 API**：DDP、DeepSpeed、FSDP、Megatron 均可使用相同代码
- **自动处理**：设备分配、混合精度计算及数据分片
- **交互式配置**：无需手动设置启动程序
- **单次启动**：可在任何环境中运行

**应选择以下替代方案的情况**：
- **PyTorch Lightning**：需要回调函数及高级抽象层功能
- **Ray Train**：需要进行多节点调度及超参数调优
- **DeepSpeed**：需要直接控制 API 及使用高级功能
- **原始 DDP**：需要最大程度的控制，且不希望过多抽象层

## 常见问题

**问题：设备分配错误**

请勿手动将数据移动到目标设备：
```python
# WRONG
batch = batch.to('cuda')

# CORRECT
# Accelerate handles it automatically after prepare()
```

**问题：梯度累积功能无法正常使用**

请使用上下文管理器：
```python
# CORRECT
with accelerator.accumulate(model):
    optimizer.zero_grad()
    accelerator.backward(loss)
    optimizer.step()
```

**问题：分布式环境下的检查点功能**

请使用加速器方法：
```python
# Save only on main process
if accelerator.is_main_process:
    accelerator.save_state('checkpoint/')

# Load on all processes
accelerator.load_state('checkpoint/')
```

**问题：使用 FSDP 时结果不一致**

请确保随机种子相同：
```python
from accelerate.utils import set_seed
set_seed(42)
```

## 高级主题

**Megatron集成**：如需了解张量并行、流水线并行及序列并行配置的方法，请参阅[references/megatron-integration.md](references/megatron-integration.md)。

**自定义插件**：若要创建自定义分布式插件并进行高级配置，请参考[references/custom-plugins.md](references/custom-plugins.md)。

**性能调优**：有关性能分析、内存优化及最佳实践的内容，请查阅[references/performance.md](references/performance.md)。

## 硬件要求

- **CPU**：可运行（速度较慢）
- **单块GPU**：可运行
- **多块GPU**：支持DDP（默认）、DeepSpeed或FSDP
- **多节点架构**：支持DDP、DeepSpeed、FSDP及Megatron
- **TPU**：受支持
- **Apple MPS**：受支持

**启动器要求**：
- **DDP**：使用`torch.distributed.run`（内置功能）
- **DeepSpeed**：需安装`deepspeed`（通过pip命令安装）
- **FSDP**：需PyTorch 1.12及以上版本（内置功能）
- **Megatron**：需自定义配置

## 相关资源

- 文档：https://huggingface.co/docs/accelerate
- GitHub仓库：https://github.com/huggingface/accelerate
- 版本：1.11.0及以上
- 教程：“加速你的脚本开发”
- 示例代码：https://github.com/huggingface/accelerate/tree/main/examples
- 被以下工具采用：HuggingFace Transformers、TRL、PEFT以及所有HuggingFace相关库



