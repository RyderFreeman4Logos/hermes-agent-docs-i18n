# PyTorch Lightning 分布式训练

## 分布式策略

Lightning 仅通过修改一个参数即可支持多种分布式策略。

### 1. DDP（DistributedDataParallel）

**多 GPU 的默认策略**：

```python
# Automatic DDP on all available GPUs
trainer = L.Trainer(accelerator='gpu', devices=4, strategy='ddp')

# Or auto-detect
trainer = L.Trainer(accelerator='gpu', devices='auto')
```

**DDP的工作原理**：
- 在每块GPU上复制模型
- 每块GPU处理不同的数据批次
- 在各GPU之间进行梯度聚合
- 同步模型权重

**启动方式**：
```bash
# Lightning handles spawning processes automatically
python train.py
```

**DDP 配置**：
```python
from lightning.pytorch.strategies import DDPStrategy

strategy = DDPStrategy(
    find_unused_parameters=False,  # Set True if model has unused params
    gradient_as_bucket_view=True,  # Memory optimization
    static_graph=False,  # Set True if graph doesn't change
)

trainer = L.Trainer(strategy=strategy)
```

### 2. FSDP（完全分片数据并行）

**适用于大型模型（参数量≥70亿）**：

```python
from lightning.pytorch.strategies import FSDPStrategy

strategy = FSDPStrategy(
    sharding_strategy="FULL_SHARD",  # ZeRO-3 equivalent
    activation_checkpointing=None,   # Or specify layer types
    cpu_offload=False,               # CPU offload for memory
)

trainer = L.Trainer(
    accelerator='gpu',
    devices=8,
    strategy=strategy,
    precision='bf16'  # Recommended with FSDP
)

trainer.fit(model, train_loader)
```

**FSDP分片策略**：
```python
# FULL_SHARD (most memory efficient, equivalent to ZeRO-3)
strategy = FSDPStrategy(sharding_strategy="FULL_SHARD")

# SHARD_GRAD_OP (less memory efficient, equivalent to ZeRO-2)
strategy = FSDPStrategy(sharding_strategy="SHARD_GRAD_OP")

# NO_SHARD (no sharding, like DDP)
strategy = FSDPStrategy(sharding_strategy="NO_SHARD")
```

**自动换行策略**（用于换行Transformer块）：
```python
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
from transformers.models.gpt2.modeling_gpt2 import GPT2Block
import functools

auto_wrap_policy = functools.partial(
    transformer_auto_wrap_policy,
    transformer_layer_cls={GPT2Block}
)

strategy = FSDPStrategy(
    auto_wrap_policy=auto_wrap_policy,
    activation_checkpointing_policy={GPT2Block}  # Checkpoint these blocks
)
```

### 3. DeepSpeed

**适用于超大模型（参数量≥700亿）**：

```python
from lightning.pytorch.strategies import DeepSpeedStrategy

# DeepSpeed ZeRO-3 with CPU offload
strategy = DeepSpeedStrategy(
    stage=3,                       # ZeRO-3
    offload_optimizer=True,        # CPU offload optimizer
    offload_parameters=True,       # CPU offload parameters
    cpu_checkpointing=True,        # Checkpoint to CPU
)

trainer = L.Trainer(
    accelerator='gpu',
    devices=8,
    strategy=strategy,
    precision='bf16'
)

trainer.fit(model, train_loader)
```

**DeepSpeed 配置文件**：
```json
{
  "train_batch_size": "auto",
  "train_micro_batch_size_per_gpu": "auto",
  "gradient_accumulation_steps": "auto",
  "zero_optimization": {
    "stage": 3,
    "offload_optimizer": {
      "device": "cpu",
      "pin_memory": true
    },
    "offload_param": {
      "device": "cpu",
      "pin_memory": true
    },
    "overlap_comm": true,
    "contiguous_gradients": true,
    "reduce_bucket_size": 5e8,
    "stage3_prefetch_bucket_size": 5e8,
    "stage3_param_persistence_threshold": 1e6
  },
  "bf16": {
    "enabled": true
  }
}
```

**使用配置文件**：
```python
strategy = DeepSpeedStrategy(config='deepspeed_config.json')
trainer = L.Trainer(strategy=strategy)
```

### 4. DDD 启动

**兼容 Windows 的 DDP**：

```python
# Use when DDP doesn't work (e.g., Windows, Jupyter)
trainer = L.Trainer(
    accelerator='gpu',
    devices=2,
    strategy='ddp_spawn'  # Spawns new processes
)
```

**注意**：由于进程创建的开销，其速度会比 DDP 慢。

## 多节点训练

### 设置多节点集群

**节点 0（主节点）**：
```bash
export MASTER_ADDR=192.168.1.100
export MASTER_PORT=12355
export WORLD_SIZE=16  # 2 nodes × 8 GPUs
export NODE_RANK=0

python train.py
```

**节点 1（工作节点）**：
```bash
export MASTER_ADDR=192.168.1.100
export MASTER_PORT=12355
export WORLD_SIZE=16
export NODE_RANK=1

python train.py
```

**训练脚本**：
```python
trainer = L.Trainer(
    accelerator='gpu',
    devices=8,              # GPUs per node
    num_nodes=2,            # Total nodes
    strategy='ddp'
)

trainer.fit(model, train_loader)
```

### SLURM集成

**SLURM作业脚本**：
```bash
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=8
#SBATCH --gres=gpu:8
#SBATCH --time=24:00:00

# Lightning auto-detects SLURM environment
srun python train.py
```

**训练脚本**（无需修改）：
```python
# Lightning automatically reads SLURM environment variables
trainer = L.Trainer(
    accelerator='gpu',
    devices=8,
    num_nodes=4,  # From SBATCH --nodes
    strategy='ddp'
)
```

### Kubernetes（KubeFlow）

**训练脚本**：
```python
import os

# Lightning auto-detects Kubernetes
trainer = L.Trainer(
    accelerator='gpu',
    devices=int(os.getenv('WORLD_SIZE', 1)),
    strategy='ddp'
)
```

## 混合精度训练

### BF16（A100/H100）

```python
trainer = L.Trainer(
    precision='bf16',  # Or 'bf16-mixed'
    accelerator='gpu'
)
```

**优势**：  
- 无需梯度缩放器  
- 动态范围与 FP32 相同  
- 性能提升 2 倍，内存占用减少 50%  

### FP16（V100 及更早型号的 GPU）

```python
trainer = L.Trainer(
    precision='16-mixed',  # Or just '16'
    accelerator='gpu'
)
```

由 Lightning 实现的**自动梯度缩放**功能

### FP8（H100）

```python
# Requires transformer_engine
# pip install transformer-engine[pytorch]

trainer = L.Trainer(
    precision='transformer-engine',
    accelerator='gpu'
)
```

**优势**：在 H100 上的运行速度是 BF16 的两倍

## 梯度累积

**模拟更大的批量大小**：

```python
trainer = L.Trainer(
    accumulate_grad_batches=4,  # Accumulate 4 batches
    precision='bf16'
)

# Effective batch = batch_size × accumulate_grad_batches × num_gpus
# Example: 32 × 4 × 8 = 1024
```

**动态累积**：
```python
# Accumulate more early in training
trainer = L.Trainer(
    accumulate_grad_batches={
        0: 8,   # Epochs 0-4: accumulate 8
        5: 4,   # Epochs 5-9: accumulate 4
        10: 2   # Epochs 10+: accumulate 2
    }
)
```

## 分布式环境中的检查点功能

### 保存检查点

```python
from lightning.pytorch.callbacks import ModelCheckpoint

# Only rank 0 saves by default
checkpoint = ModelCheckpoint(
    dirpath='checkpoints/',
    filename='model-{epoch:02d}',
    save_top_k=3
)

trainer = L.Trainer(callbacks=[checkpoint], strategy='ddp')
trainer.fit(model, train_loader)
```

**手动保存**：
```python
class MyModel(L.LightningModule):
    def training_step(self, batch, batch_idx):
        # Training...
        loss = ...

        # Save every 1000 steps (only rank 0)
        if batch_idx % 1000 == 0 and self.trainer.is_global_zero:
            self.trainer.save_checkpoint(f'checkpoint_step_{batch_idx}.ckpt')

        return loss
```

### 加载检查点

```python
# Resume training
trainer = L.Trainer(strategy='ddp')
trainer.fit(model, train_loader, ckpt_path='checkpoints/last.ckpt')

# Load for inference
model = MyModel.load_from_checkpoint('checkpoints/best.ckpt')
model.eval()
```

## 策略对比

| 策略 | 内存效率 | 速度 | 适用场景 |
|----------|------------------|-------|----------|
| DDP | 低 | 快 | 小型模型（<7B），单节点环境 |
| FSDP | 高 | 中等 | 大型模型（7-70B） |
| DeepSpeed ZeRO-2 | 中等 | 快 | 中型模型（1-13B） |
| DeepSpeed ZeRO-3 | 极高 | 较慢 | 超大型模型（70B+） |
| DDP Spawn | 低 | 慢 | Windows系统，调试场景 |

## 最佳实践

### 1. 正确选择策略

```python
# Model size guide
if model_params < 1e9:  # <1B
    strategy = 'ddp'
elif model_params < 7e9:  # 1-7B
    strategy = 'ddp' or DeepSpeedStrategy(stage=2)
elif model_params < 70e9:  # 7-70B
    strategy = FSDPStrategy(sharding_strategy="FULL_SHARD")
else:  # 70B+
    strategy = DeepSpeedStrategy(stage=3, offload_optimizer=True)

trainer = L.Trainer(strategy=strategy)
```

### 2. 避免同步问题

```python
class MyModel(L.LightningModule):
    def training_step(self, batch, batch_idx):
        # WRONG: This runs on all GPUs independently
        if batch_idx % 100 == 0:
            self.log_something()  # Logged 8 times on 8 GPUs!

        # CORRECT: Use is_global_zero
        if batch_idx % 100 == 0 and self.trainer.is_global_zero:
            self.log_something()  # Logged once

        loss = ...
        return loss
```

### 3. 高效的数据加载

```python
from torch.utils.data import DataLoader, DistributedSampler

# Lightning handles DistributedSampler automatically
train_loader = DataLoader(
    dataset,
    batch_size=32,
    num_workers=4,  # 4 workers per GPU
    pin_memory=True,
    persistent_workers=True
)

# Lightning automatically wraps with DistributedSampler in DDP
trainer.fit(model, train_loader)
```

### 4. 降低通信开销

```python
from lightning.pytorch.strategies import DDPStrategy

strategy = DDPStrategy(
    gradient_as_bucket_view=True,  # Reduce memory copies
    static_graph=True,  # If model graph doesn't change (faster)
)

trainer = L.Trainer(strategy=strategy)
```

## 常见问题

### 问题：NCCL 超时

**症状**：训练过程因 `NCCL timeout` 错误而挂起

**解决方案 1**：增加超时时间
```bash
export NCCL_TIMEOUT=3600  # 1 hour
python train.py
```

**解决方案 2**：检查网络连接。
```bash
# Test inter-node communication
nvidia-smi nvlink -s

# Verify all nodes can ping each other
ping <node-2-ip>
```

### 问题：使用 FSDP 时出现内存溢出

**解决方案**：启用 CPU 卸载功能
```python
strategy = FSDPStrategy(
    sharding_strategy="FULL_SHARD",
    cpu_offload=True  # Offload to CPU
)
```

### 问题：使用 DDP 时结果不一致

**原因**：不同 GPU 使用的随机种子不同

**解决方案**：在 LightningModule 中设置种子值
```python
class MyModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        L.seed_everything(42, workers=True)  # Same seed everywhere
```

### 问题：DeepSpeed 配置错误

**解决方案**：使用 Lightning 的自动配置功能
```python
strategy = DeepSpeedStrategy(
    stage=3,
    # Don't specify config file, Lightning generates automatically
)
```

## 资源参考

- 分布式训练策略：https://lightning.ai/docs/pytorch/stable/accelerators/gpu_intermediate.html
- FSDP 使用指南：https://lightning.ai/docs/pytorch/stable/advanced/model_parallel/fsdp.html
- DeepSpeed：https://lightning.ai/docs/pytorch/stable/advanced/model_parallel/deepspeed.html
- 多节点部署：https://lightning.ai/docs/pytorch/stable/clouds/cluster.html
