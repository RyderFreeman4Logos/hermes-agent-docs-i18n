---
name: distributed-llm-pretraining-torchtitan
description: Pretrain LLMs at scale with PyTorch 4D parallelism.
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [torch>=2.6.0, torchtitan>=0.2.0, torchao>=0.5.0]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Model Architecture, Distributed Training, TorchTitan, FSDP2, Tensor Parallel, Pipeline Parallel, Context Parallel, Float8, Llama, Pretraining]

---

# TorchTitan——PyTorch原生分布式大语言模型预训练框架

## 快速入门

TorchTitan是PyTorch官方推出的大规模大语言模型预训练平台，它支持可组合的4D并行计算技术（FSDP2、TP、PP、CP），在H100显卡上相较于基准方案可实现65%以上的速度提升。

**安装方式**：
```bash
# From PyPI (stable)
pip install torchtitan

# From source (latest features, requires PyTorch nightly)
git clone https://github.com/pytorch/torchtitan
cd torchtitan
pip install -r requirements.txt
```

**下载分词器**：
```bash
# Get HF token from https://huggingface.co/settings/tokens
python scripts/download_hf_assets.py --repo_id meta-llama/Llama-3.1-8B --assets tokenizer --hf_token=...
```

**在8块GPU上开始训练**：
```bash
CONFIG_FILE="./torchtitan/models/llama3/train_configs/llama3_8b.toml" ./run_train.sh
```

## 常见工作流程

### 工作流程 1：在单节点上预训练 Llama 3.1 8B 模型

复制此清单：

```
Single Node Pretraining:
- [ ] Step 1: Download tokenizer
- [ ] Step 2: Configure training
- [ ] Step 3: Launch training
- [ ] Step 4: Monitor and checkpoint
```

**步骤 1：下载分词器**

```bash
python scripts/download_hf_assets.py \
  --repo_id meta-llama/Llama-3.1-8B \
  --assets tokenizer \
  --hf_token=YOUR_HF_TOKEN
```

**步骤 2：配置训练参数**

编辑或创建一个 TOML 配置文件：

```toml
# llama3_8b_custom.toml
[job]
dump_folder = "./outputs"
description = "Llama 3.1 8B training"

[model]
name = "llama3"
flavor = "8B"
hf_assets_path = "./assets/hf/Llama-3.1-8B"

[optimizer]
name = "AdamW"
lr = 3e-4

[lr_scheduler]
warmup_steps = 200

[training]
local_batch_size = 2
seq_len = 8192
max_norm = 1.0
steps = 1000
dataset = "c4"

[parallelism]
data_parallel_shard_degree = -1  # Use all GPUs for FSDP

[activation_checkpoint]
mode = "selective"
selective_ac_option = "op"

[checkpoint]
enable = true
folder = "checkpoint"
interval = 500
```

**第3步：启动训练**

```bash
# 8 GPUs on single node
CONFIG_FILE="./llama3_8b_custom.toml" ./run_train.sh

# Or explicitly with torchrun
torchrun --nproc_per_node=8 \
  -m torchtitan.train \
  --job.config_file ./llama3_8b_custom.toml
```

**第4步：监控与检查点生成**

TensorBoard日志会被保存至 `./outputs/tb/` 目录中：
```bash
tensorboard --logdir ./outputs/tb
```

### 工作流 2：基于 SLURM 的多节点训练

```
Multi-Node Training:
- [ ] Step 1: Configure parallelism for scale
- [ ] Step 2: Set up SLURM script
- [ ] Step 3: Submit job
- [ ] Step 4: Resume from checkpoint
```

**步骤 1：配置并行度以实现扩展**

针对在 256 块 GPU（32 个节点）上运行的 700 亿参数模型：
```toml
[parallelism]
data_parallel_shard_degree = 32  # FSDP across 32 ranks
tensor_parallel_degree = 8        # TP within node
pipeline_parallel_degree = 1      # No PP for 70B
context_parallel_degree = 1       # Increase for long sequences
```

**步骤 2：配置 SLURM 脚本**

```bash
#!/bin/bash
#SBATCH --job-name=llama70b
#SBATCH --nodes=32
#SBATCH --ntasks-per-node=8
#SBATCH --gpus-per-node=8

srun torchrun \
  --nnodes=32 \
  --nproc_per_node=8 \
  --rdzv_backend=c10d \
  --rdzv_endpoint=$MASTER_ADDR:$MASTER_PORT \
  -m torchtitan.train \
  --job.config_file ./llama3_70b.toml
```

**步骤 3：提交任务**

```bash
sbatch multinode_trainer.slurm
```

**第4步：从检查点继续训练**

如果在配置的文件夹中存在检查点，训练将自动从中继续。

### 工作流程3：为H100显卡启用Float8训练模式

在H100 GPU上，使用Float8格式可将训练速度提升30-50%。

```
Float8 Training:
- [ ] Step 1: Install torchao
- [ ] Step 2: Configure Float8
- [ ] Step 3: Launch with compile
```

**步骤 1：安装 torchao**

```bash
USE_CPP=0 pip install git+https://github.com/pytorch/ao.git
```

**步骤 2：配置 Float8**

在您的 TOML 配置文件中添加以下内容：
```toml
[model]
converters = ["quantize.linear.float8"]

[quantize.linear.float8]
enable_fsdp_float8_all_gather = true
precompute_float8_dynamic_scale_for_fsdp = true
filter_fqns = ["output"]  # Exclude output layer

[compile]
enable = true
components = ["model", "loss"]
```

**步骤 3：通过编译方式启动**

```bash
CONFIG_FILE="./llama3_8b.toml" ./run_train.sh \
  --model.converters="quantize.linear.float8" \
  --quantize.linear.float8.enable_fsdp_float8_all_gather \
  --compile.enable
```

### 工作流 4：针对 405B 模型的 4D 并行处理方案

```
4D Parallelism (FSDP + TP + PP + CP):
- [ ] Step 1: Create seed checkpoint
- [ ] Step 2: Configure 4D parallelism
- [ ] Step 3: Launch on 512 GPUs
```

**步骤 1：创建种子检查点**

这是确保在多个 PP 阶段之间实现一致初始化所必需的。
```bash
NGPU=1 CONFIG_FILE=./llama3_405b.toml ./run_train.sh \
  --checkpoint.enable \
  --checkpoint.create_seed_checkpoint \
  --parallelism.data_parallel_shard_degree 1 \
  --parallelism.tensor_parallel_degree 1 \
  --parallelism.pipeline_parallel_degree 1
```

**步骤 2：配置 4D 并行处理**

```toml
[parallelism]
data_parallel_shard_degree = 8   # FSDP
tensor_parallel_degree = 8       # TP within node
pipeline_parallel_degree = 8     # PP across nodes
context_parallel_degree = 1      # CP for long sequences

[training]
local_batch_size = 32
seq_len = 8192
```

**步骤 3：在 512 块 GPU 上启动**

```bash
# 64 nodes x 8 GPUs = 512 GPUs
srun torchrun --nnodes=64 --nproc_per_node=8 \
  -m torchtitan.train \
  --job.config_file ./llama3_405b.toml
```

## 何时使用 TorchTitan 及其替代方案

**适合使用 TorchTitan 的场景：**
- 从零开始预训练大语言模型（8B 到 405B+ 参数量）
- 需要无需第三方依赖的纯 PyTorch 解决方案
- 需要可组合的 4D 并行计算能力（FSDP2、TP、PP、CP）
- 在支持 Float8 加速的 H100 硬件上进行训练
- 希望与 torchtune/HuggingFace 实现检查点互操作

**可选择的其他替代方案：**
- **Megatron-LM**：专为 NVIDIA 硬件部署设计，性能最优
- **DeepSpeed**：拥有更完善的 ZeRO 优化生态及推理支持功能
- **Axolotl/TRL**：适用于微调而非预训练场景
- **LitGPT**：用于教学目的的小规模训练

## 常见问题

**问题：大型模型导致内存不足**

请启用激活值检查点功能并减小批量大小：
```toml
[activation_checkpoint]
mode = "full"  # Instead of "selective"

[training]
local_batch_size = 1
```

或者使用梯度累积法：
```toml
[training]
local_batch_size = 1
global_batch_size = 32  # Accumulates gradients
```

**问题：异步集合操作会导致 TP 消耗大量内存**

设置环境变量：
```bash
export TORCH_NCCL_AVOID_RECORD_STREAMS=1
```

**问题：Float8训练并未带来更快的速度提升**

Float8的优势主要体现在大规模矩阵乘法操作上。对于包含小型层的模型，此优化方法并无显著效果：
```toml
[quantize.linear.float8]
filter_fqns = ["attention.wk", "attention.wv", "output", "auto_filter_small_kn"]
```

**问题：更改并行度后检查点加载失败**

请使用 DCP 的重新分片功能：
```bash
# Convert sharded checkpoint to single file
python -m torch.distributed.checkpoint.format_utils \
  dcp_to_torch checkpoint/step-1000 checkpoint.pt
```

**问题：流水线并行初始化**

请先创建种子检查点（参见工作流 4 的第 1 步）。

## 支持的模型

| 模型 | 参数量 | 状态 |
|-------|-------|--------|
| Llama 3.1 | 8B、70B、405B | 已投入生产使用 |
| Llama 4 | 多种规格 | 测试中 |
| DeepSeek V3 | 16B、236B、671B（混合精度版） | 测试中 |
| GPT-OSS | 20B、120B（混合精度版） | 测试中 |
| Qwen 3 | 多种规格 | 测试中 |
| Flux | 扩散模型 | 测试中 |

## 性能基准测试（H100）

| 模型 | GPU 数量 | 并行策略 | 每 GPU TPS | 优化技术 |
|-------|---------|-----------|------------|----------|
| Llama 8B | 8 | FSDP | 5,762 | 基准值 |
| Llama 8B | 8 | FSDP+编译+FP8 | 8,532 | 提升 48% |
| Llama 70B | 256 | FSDP+TP+异步 TP | 876 | 二维并行 |
| Llama 405B | 512 | FSDP+TP+PP | 128 | 三维并行 |

## 进阶主题

**FSDP2 配置**：有关 FSDP2 与 FSDP1 的详细对比以及 ZeRO 等效配置，可参阅 [references/fsdp.md](references/fsdp.md)。

**Float8 训练**：关于张量级缩放与行级缩放的实现方法，可参阅 [references/float8.md](references/float8.md)。

**检查点保存**：有关 HuggingFace 格式转换及异步检查点保存的详细信息，可参阅 [references/checkpoint.md](references/checkpoint.md)。

**添加自定义模型**：关于 TrainSpec 协议的用法，可参阅 [references/custom-models.md](references/custom-models.md)。

## 相关资源

- GitHub 仓库：https://github.com/pytorch/torchtitan
- 论文链接：https://arxiv.org/abs/2410.06511
- ICLR 2025 发表页面：https://iclr.cc/virtual/2025/poster/29620
- PyTorch 论坛讨论帖：https://discuss.pytorch.org/c/distributed/torchtitan/44

