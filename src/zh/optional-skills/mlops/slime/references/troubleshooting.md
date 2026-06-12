# slime 故障排除指南

## 常见问题及解决方案

### SGLang 相关问题

#### 问题：SGLang 引擎崩溃

**症状**：推理引擎在训练过程中突然停止运行，出现连接错误

**解决方案**：

1. **启用容错功能**：
```bash
--use-fault-tolerance
```

2. **增加内存分配**：
```bash
--sglang-mem-fraction-static 0.85  # Increase from 0.8
```

3. **减小批次大小**：
```bash
--rollout-batch-size 16  # Reduce from 32
```

4. **禁用 CUDA 图形**（用于调试）：
```bash
--sglang-disable-cuda-graph
```

#### 问题：SGLang 路由器负载不均衡

**症状**：部分 SGLang 引擎负载过重，而其他引擎则处于空闲状态

**解决方案**：

1. **调整路由策略**：
```bash
--sglang-router-strategy round_robin
```

2. **增加引擎数量**：
```bash
--rollout-num-gpus-per-engine 1  # More engines, less GPUs each
```

### 权重同步问题

#### 问题：权重同步超时

**症状**：模型部署后训练进程挂起，出现超时错误

**解决方案**：

1. **增加同步间隔**（异步模式）：
```bash
--update-weights-interval 5  # Increase from 2
```

2. **使用同置模式**（可避免网络传输）：
```bash
--colocate
```

3. **检查网络带宽**：
```bash
# Verify InfiniBand is enabled
ibstat
```

#### 问题：多节点环境下的权重同步失败

**症状**：各节点无法接收到更新后的权重值

**解决方案**：

1. **配置 NCCL 环境**：
```bash
export NCCL_DEBUG=INFO
export NCCL_SOCKET_IFNAME=eth0
export NCCL_IB_DISABLE=0
```

2. **延长超时时间**：
```bash
export NCCL_TIMEOUT=1800
```

### 内存相关问题

#### 问题：训练过程中出现内存溢出

**症状**：在反向传播阶段出现 CUDA 内存溢出

**解决方案**：

1. **启用梯度检查点机制**：
```bash
--recompute-activations
```

2. **减小微批次大小**：
```bash
--micro-batch-size 1
```

3. **启用序列并行处理**：
```bash
--sequence-parallel
```

4. **降低全局批次大小**：
```bash
--global-batch-size 128  # Reduce from 256
```

#### 问题：同主机模式下的内存溢出

**症状**：在相同 GPU 上同时进行训练和推理时出现内存溢出。

**解决方案**：

1. **减少 SGLang 内存占用**：
```bash
--sglang-mem-fraction-static 0.4  # Reduce from 0.8
```

2. **启用卸载功能**：
```bash
--offload-optimizer-states
```

3. **使用更短的序列长度**：
```bash
--seq-length 2048  # Reduce from 4096
```

### 数据加载问题

#### 问题：数据加载速度过慢

**症状**：在数据获取过程中GPU处于空闲状态，GPU利用率较低

**解决方案**：

1. **增加数据处理任务数**：
```bash
--num-data-workers 4
```

2. **使用流式数据集**：
```bash
--streaming-data
```

3. **预分词处理数据**：
```python
# Pre-process data offline
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("model_path")
# Save tokenized data
```

#### 问题：数据格式错误

**症状**：KeyError异常、字段缺失、解析失败

**解决方案**：

1. **验证数据格式**：
```python
import json
with open("data.jsonl") as f:
    for line in f:
        data = json.loads(line)
        assert "prompt" in data, "Missing prompt field"
        assert "label" in data, "Missing label field"
```

2. **检查密钥名称**：
```bash
--input-key prompt  # Must match your data
--label-key label   # Must match your data
```

### 训练稳定性问题

#### 问题：损失值激增/出现 NaN 值

**症状**：损失值变为 NaN 或出现剧烈波动

**解决方案**：

1. **降低学习率**：
```bash
--lr 1e-6  # Reduce from 5e-6
```

2. **启用梯度裁剪功能**：
```bash
--clip-grad 1.0
```

3. **检查数据问题**：
```python
# Verify no empty prompts or responses
for sample in dataset:
    assert len(sample["prompt"]) > 0
```

4. **改用 BF16 而非 FP16**：
```bash
--bf16  # More numerically stable
```

#### 问题：奖励值骤降

**症状**：奖励值降至零，模型输出内容无意义

**解决方案**：

1. **增加KL惩罚项**：
```bash
--kl-loss-coef 0.01  # Increase from 0.001
```

2. **减少样本数量**：
```bash
--n-samples-per-prompt 4  # Reduce from 8
```

3. **验证奖励函数**：
```python
# Test reward function independently
from custom_rm import reward_func
sample = Sample(prompt="test", response="test response")
reward = reward_func(args, sample)
print(f"Reward: {reward}")  # Should be reasonable
```

### 异步训练相关问题

#### 问题：Colocate模式不支持异步训练

**症状**：在使用 `train_async.py` 时搭配 `--colocate` 参数会出现错误。

**解决方案**：异步训练不支持Colocate模式。请使用独立的GPU：
```bash
# Remove --colocate flag
python train_async.py \
    --actor-num-gpus-per-node 4 \
    --rollout-num-gpus 4 \
    # No --colocate
```

#### 问题：异步模式下的过时权重问题

**症状**：策略偏差、行为不一致

**解决方案**：

1. **减小异步缓冲区大小**：
```bash
--async-buffer-size 2  # Reduce from 4
```

2. **提高权重更新频率**：
```bash
--update-weights-interval 1  # Sync every rollout
```

### 多轮训练相关问题

#### 问题：损失函数中包含了工具响应内容

**症状**：模型会学会原封不动地输出工具的响应内容

**解决方案**：在自定义生成函数中正确设置损失掩码：
```python
def build_loss_mask(sample):
    """Create loss mask that excludes tool responses."""
    mask = []
    for i, token in enumerate(sample.tokens):
        if is_tool_response(token, sample.metadata):
            mask.append(0)  # Don't compute loss
        else:
            mask.append(1)  # Compute loss
    return mask
```

#### 问题：多轮对话上下文过长

**症状**：在多轮对话中出现内存溢出或内容被截断的情况

**解决方案**：

1. **限制对话历史记录的长度**：
```python
# In custom generate function
conversation = sample.prompt[-10:]  # Keep last 10 turns
```

2. **增加上下文长度**：
```bash
--sglang-context-length 16384
```

### 检查点相关问题

#### 问题：检查点加载失败

**症状**：无法加载已保存的检查点

**解决方案**：

1. **验证检查点路径**：
```bash
ls -la /path/to/checkpoint/
```

2. **检查并行度是否匹配**：
```bash
# Checkpoint was saved with TP=2, must load with TP=2
--tensor-model-parallel-size 2
```

3. **如需转换，可将 HuggingFace 模型转换为 Megatron 模型**：
```bash
python tools/convert_hf_to_megatron.py \
    --hf_model_path /path/to/hf/model \
    --save_path /path/to/megatron/checkpoint
```

### 调试技巧

#### 启用详细日志记录

```bash
--log-level DEBUG
export SLIME_DEBUG=1
```

#### 检查 GPU 使用率

```bash
watch -n 1 nvidia-smi
```

#### 监控训练过程

```bash
tensorboard --logdir outputs/
```

#### 独立测试自定义函数

```python
# Test reward function
import asyncio
from custom_rm import reward_func

async def test():
    sample = Sample(prompt="test", response="test", label="expected")
    reward = await reward_func(args, sample)
    print(f"Reward: {reward}")

asyncio.run(test())
```

## 约束参考

需牢记的关键约束：

```
rollout_batch_size × n_samples_per_prompt = global_batch_size × num_steps_per_rollout
```

示例：`32 × 8 = 256 × 1`

## 资源

- GitHub 问题反馈：https://github.com/THUDM/slime/issues
- 文档说明：https://thudm.github.io/slime/
- 示例代码：`examples/` 目录
