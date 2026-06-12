# 分布式评估

本指南介绍如何利用数据并行、张量并行和流水线并行技术在多块 GPU 上执行评估。

## 概述

分布式评估可通过以下方式加快基准测试速度：
- **数据并行**：将评估样本分配到不同 GPU 上处理（每块 GPU 都拥有完整的模型副本）
- **张量并行**：将模型权重分配到不同 GPU 上处理（适用于大型模型）
- **流水线并行**：将模型层分配到不同 GPU 上处理（适用于超大型模型）

**适用场景**：
- 数据并行：模型能够加载到单块 GPU 中，且希望加快评估速度
- 张量/流水线并行：模型过大，无法容纳在单块 GPU 中

## HuggingFace 模型 (`hf`)

### 数据并行（推荐方案）

每块 GPU 都加载完整的模型副本，并处理部分评估数据。

**单节点（8块 GPU）**：
```bash
accelerate launch --multi_gpu --num_processes 8 \
  -m lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,dtype=bfloat16 \
  --tasks mmlu,gsm8k,hellaswag \
  --batch_size 16
```

**加速效果**：近乎线性提升（8块GPU可实现约8倍的速度提升）

**内存需求**：每块GPU需存储完整模型参数（70亿参数模型约需14GB/块，8块GPU总计约112GB）

### 张量并行（模型分片）

针对体积过大而无法单块GPU承载的模型，通过将模型权重分配到多块GPU上进行处理。

**未使用accelerate启动器时**：
```bash
lm_eval --model hf \
  --model_args \
    pretrained=meta-llama/Llama-2-70b-hf,\
    parallelize=True,\
    dtype=bfloat16 \
  --tasks mmlu,gsm8k \
  --batch_size 8
```

**配备8块GPU时**：700亿参数模型（140GB）/ 8 = 每块GPU分配17.5GB ✅

**高级分片功能**：
```bash
lm_eval --model hf \
  --model_args \
    pretrained=meta-llama/Llama-2-70b-hf,\
    parallelize=True,\
    device_map_option=auto,\
    max_memory_per_gpu=40GB,\
    max_cpu_memory=100GB,\
    dtype=bfloat16 \
  --tasks mmlu
```

**选项**：
- `device_map_option`：默认值为 `"auto"`，可选值为 `"balanced"` 或 `"balanced_low_0"`。
- `max_memory_per_gpu`：每块 GPU 的最大内存容量（例如 `"40GB"`）。
- `max_cpu_memory`：用于任务卸载的 CPU 最大内存容量。
- `offload_folder`：磁盘卸载目录。

### 综合数据分配与张量并行

针对超大模型，可同时使用这两种方式。

**示例：在 16 块 GPU 上运行 70B 模型（模型副本数为 2，每组 8 块 GPU）**：
```bash
accelerate launch --multi_gpu --num_processes 2 \
  -m lm_eval --model hf \
  --model_args \
    pretrained=meta-llama/Llama-2-70b-hf,\
    parallelize=True,\
    dtype=bfloat16 \
  --tasks mmlu \
  --batch_size 8
```

**结果**：得益于数据并行技术，处理速度提升2倍；通过张量并行技术，可支持700亿参数规模的模型。 

### 使用 `accelerate config` 进行配置

创建文件 `~/.cache/huggingface/accelerate/default_config.yaml`：
```yaml
compute_environment: LOCAL_MACHINE
distributed_type: MULTI_GPU
num_machines: 1
num_processes: 8
gpu_ids: all
mixed_precision: bf16
```

**接着运行**：
```bash
accelerate launch -m lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu
```

## vLLM 模型（`vllm`）

vLLM 提供了高度优化的分布式推理功能。

### 张量并行

**单节点（4块GPU）**：
```bash
lm_eval --model vllm \
  --model_args \
    pretrained=meta-llama/Llama-2-70b-hf,\
    tensor_parallel_size=4,\
    dtype=auto,\
    gpu_memory_utilization=0.9 \
  --tasks mmlu,gsm8k \
  --batch_size auto
```

**内存**：70B参数模型分布在4块GPU上，即每块GPU约占用35GB内存。

### 数据并行架构

**多个模型副本**：
```bash
lm_eval --model vllm \
  --model_args \
    pretrained=meta-llama/Llama-2-7b-hf,\
    data_parallel_size=4,\
    dtype=auto,\
    gpu_memory_utilization=0.8 \
  --tasks hellaswag,arc_challenge \
  --batch_size auto
```

**结果**：4个模型副本 = 4倍的吞吐量

### 合并张量并行与数据并行

**示例：8块GPU = 4个TP × 2个DP**：
```bash
lm_eval --model vllm \
  --model_args \
    pretrained=meta-llama/Llama-2-70b-hf,\
    tensor_parallel_size=4,\
    data_parallel_size=2,\
    dtype=auto,\
    gpu_memory_utilization=0.85 \
  --tasks mmlu \
  --batch_size auto
```

**结果**：70B模型可正常运行（正确预测数=4），速度提升2倍（精度损失为2级）

### 多节点vLLM

vLLM本身不支持多节点架构。建议使用Ray来实现：

```bash
# Start Ray cluster
ray start --head --port=6379

# Run evaluation
lm_eval --model vllm \
  --model_args \
    pretrained=meta-llama/Llama-2-70b-hf,\
    tensor_parallel_size=8,\
    dtype=auto \
  --tasks mmlu
```

## NVIDIA NeMo 模型（`nemo_lm`）

### 数据复制

**在 8 块 GPU 上创建 8 个副本**：
```bash
torchrun --nproc-per-node=8 --no-python \
  lm_eval --model nemo_lm \
  --model_args \
    path=/path/to/model.nemo,\
    devices=8 \
  --tasks hellaswag,arc_challenge \
  --batch_size 32
```

**加速效果**：近乎线性提升（快8倍）

### 张量并行

**四路张量并行**：
```bash
torchrun --nproc-per-node=4 --no-python \
  lm_eval --model nemo_lm \
  --model_args \
    path=/path/to/70b_model.nemo,\
    devices=4,\
    tensor_model_parallel_size=4 \
  --tasks mmlu,gsm8k \
  --batch_size 16
```

### 流水线并行性

**4块GPU上的2个TP×2个PP配置**：
```bash
torchrun --nproc-per-node=4 --no-python \
  lm_eval --model nemo_lm \
  --model_args \
    path=/path/to/model.nemo,\
    devices=4,\
    tensor_model_parallel_size=2,\
    pipeline_model_parallel_size=2 \
  --tasks mmlu \
  --batch_size 8
```

**约束条件**：`devices = TP × PP`

### 多节点 NeMo

目前 lm-evaluation-harness 不支持该功能。

## SGLang 模型（`sglang`）

### 张量并行化

```bash
lm_eval --model sglang \
  --model_args \
    pretrained=meta-llama/Llama-2-70b-hf,\
    tp_size=4,\
    dtype=auto \
  --tasks gsm8k \
  --batch_size auto
```

### 数据并行（已废弃）

**注意**：SGLang 正逐步废弃数据并行功能，建议改用张量并行方式。

```bash
lm_eval --model sglang \
  --model_args \
    pretrained=meta-llama/Llama-2-7b-hf,\
    dp_size=4,\
    dtype=auto \
  --tasks mmlu
```

## 性能对比

### 70B 模型评估（MMLU，5次抽样）

| 方法 | GPU 数量 | 所需时间 | 每张 GPU 内存占用 | 备注 |
|------|----------|----------|------------------|-------|
| HuggingFace（无并行处理） | 1 | 8 小时 | 140GB（内存溢出） | 内存不足 |
| HuggingFace（批处理大小=8） | 8 | 2 小时 | 17.5GB | 速度较慢，但内存足够 |
| HuggingFace（精度=8） | 8 | 1 小时 | 140GB（内存溢出） | 内存不足 |
| vLLM（批处理大小=4） | 4 | 30 分钟 | 35GB | 速度极快！ |
| vLLM（批处理大小=4，精度=2） | 8 | 15 分钟 | 35GB | 速度最快 |

### 7B 模型评估（多任务）

| 方法 | GPU 数量 | 所需时间 | 加速比 |
|------|----------|----------|--------|
| HuggingFace（单任务） | 1 | 4 小时 | 1× |
| HuggingFace（精度=4） | 4 | 1 小时 | 4× |
| HuggingFace（精度=8） | 8 | 30 分钟 | 8× |
| vLLM（精度=8） | 8 | 15 分钟 | 16× |

**结论**：在推理性能方面，vLLM 的速度明显快于 HuggingFace。

## 选择并行策略

### 决策树

```
Model fits on single GPU?
├─ YES: Use data parallelism
│   ├─ HF: accelerate launch --multi_gpu --num_processes N
│   └─ vLLM: data_parallel_size=N (fastest)
│
└─ NO: Use tensor/pipeline parallelism
    ├─ Model < 70B:
    │   └─ vLLM: tensor_parallel_size=4
    ├─ Model 70-175B:
    │   ├─ vLLM: tensor_parallel_size=8
    │   └─ Or HF: parallelize=True
    └─ Model > 175B:
        └─ Contact framework authors
```

### 内存估算

**经验法则**：
```
Memory (GB) = Parameters (B) × Precision (bytes) × 1.2 (overhead)
```

**示例**：
- 70亿参数 FP16格式：7 × 2 × 1.2 = 168GB ✅ 可适配A100 40GB显卡
- 130亿参数 FP16格式：13 × 2 × 1.2 = 31.2GB ✅ 可适配A100 40GB显卡
- 700亿参数 FP16格式：700 × 2 × 1.2 = 1680GB ❌ 需要TP=4或TP=8配置
- 700亿参数 BF16格式：700 × 2 × 1.2 = 1680GB（与FP16格式所需显存相同）

**采用张量并行技术时**：
```
Memory per GPU = Total Memory / TP
```

- 在4张GPU上运行70B模型：168GB ÷ 4 = 每张GPU 42GB ✅
- 在8张GPU上运行70B模型：168GB ÷ 8 = 每张GPU 21GB ✅

## 多节点评估

### 使用SLURM的HuggingFace

**提交任务**：
```bash
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --gpus-per-node=8
#SBATCH --ntasks-per-node=1

srun accelerate launch --multi_gpu \
  --num_processes $((SLURM_NNODES * 8)) \
  -m lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag \
  --batch_size 16
```

**提交**：
```bash
sbatch eval_job.sh
```

### 手动多节点部署指南

**在每个节点上执行**：
```bash
accelerate launch \
  --multi_gpu \
  --num_machines 4 \
  --num_processes 32 \
  --main_process_ip $MASTER_IP \
  --main_process_port 29500 \
  --machine_rank $NODE_RANK \
  -m lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu
```

**环境变量**：
- `MASTER_IP`：等级为 0 的节点的 IP 地址
- `NODE_RANK`：每个节点对应的数值，取值为 0、1、2 或 3

## 最佳实践

### 1. 从小规模开始

先在小型样本上进行测试：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-70b-hf,parallelize=True \
  --tasks mmlu \
  --limit 100  # Just 100 samples
```

### 2. 监控 GPU 使用情况

```bash
# Terminal 1: Run evaluation
lm_eval --model hf ...

# Terminal 2: Monitor
watch -n 1 nvidia-smi
```

请关注以下指标：
- GPU利用率 > 90%
- 内存使用情况保持稳定
- 所有GPU均处于活跃状态

### 3. 优化批量大小

```bash
# Auto batch size (recommended)
--batch_size auto

# Or tune manually
--batch_size 16  # Start here
--batch_size 32  # Increase if memory allows
```

### 4. 使用混合精度计算

```bash
--model_args dtype=bfloat16  # Faster, less memory
```

### 5. 检查通信情况

对于数据并行模式，请检查网络带宽：
```bash
# Should see InfiniBand or high-speed network
nvidia-smi topo -m
```

## 故障排除

### “CUDA 内存不足”

**解决方案**：
1. 增加张量并行度：
   ```bash
   --model_args tensor_parallel_size=8  # Was 4
   ```

2. 减小批次大小：
   ```bash
   --batch_size 4  # Was 16
   ```

3. 精度较低：
   ```bash
   --model_args dtype=int8  # Quantization
   ```

### “NCCL错误”或程序挂起

**检查事项**：
1. 所有GPU是否可见：`nvidia-smi`
2. NCCL是否已安装：`python -c "import torch; print(torch.cuda.nccl.version())"`
3. 节点之间的网络连接状态

**解决方案**：
```bash
export NCCL_DEBUG=INFO  # Enable debug logging
export NCCL_IB_DISABLE=0  # Use InfiniBand if available
```

### 评估速度过慢

**可能原因**：
1. **数据加载瓶颈**：对数据集进行预处理
2. **GPU利用率低**：增大批量大小
3. **通信开销过大**：降低并行度

**性能分析**：
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu \
  --limit 100 \
  --log_samples  # Check timing
```

### GPU资源分配不均衡

**症状**：GPU 0的使用率为100%，而其他GPU的使用率为50%

**解决方案**：使用`device_map_option=balanced`参数：
```bash
--model_args parallelize=True,device_map_option=balanced
```

## 示例配置

### 小模型（7B）——快速评估

```bash
# 8 A100s, data parallel
accelerate launch --multi_gpu --num_processes 8 \
  -m lm_eval --model hf \
  --model_args \
    pretrained=meta-llama/Llama-2-7b-hf,\
    dtype=bfloat16 \
  --tasks mmlu,gsm8k,hellaswag,arc_challenge \
  --num_fewshot 5 \
  --batch_size 32

# Time: ~30 minutes
```

### 大模型（700亿参数）——vLLM

```bash
# 8 H100s, tensor parallel
lm_eval --model vllm \
  --model_args \
    pretrained=meta-llama/Llama-2-70b-hf,\
    tensor_parallel_size=8,\
    dtype=auto,\
    gpu_memory_utilization=0.9 \
  --tasks mmlu,gsm8k,humaneval \
  --num_fewshot 5 \
  --batch_size auto

# Time: ~1 hour
```

### 超大模型（175B+）

**需要专门的配置——请联系框架维护者**

## 参考资料

- HuggingFace Accelerate：https://huggingface.co/docs/accelerate/
- vLLM 文档：https://docs.vllm.ai/
- NeMo 文档：https://docs.nvidia.com/nemo-framework/
- lm-eval 分布式训练指南：`docs/model_guide.md`
