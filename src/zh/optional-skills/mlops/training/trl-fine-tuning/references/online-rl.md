# 在线强化学习方法

介绍基于PPO、GRPO、RLOO和OnlineDPO的在线强化学习指南。

## 概述

在线强化学习会在训练过程中逐步生成完整策略，并根据奖励信号进行优化。

## PPO（近端策略优化）

用于大语言模型对齐的经典强化学习算法。

### 基本用法

```bash
python -m trl.scripts.ppo \
    --model_name_or_path Qwen/Qwen2.5-0.5B-Instruct \
    --reward_model_path reward-model \
    --dataset_name trl-internal-testing/descriptiveness-sentiment-trl-style \
    --output_dir model-ppo \
    --learning_rate 3e-6 \
    --per_device_train_batch_size 64 \
    --total_episodes 10000 \
    --num_ppo_epochs 4 \
    --kl_coef 0.05
```

### 关键参数

- `kl_coef`：KL惩罚系数（0.05-0.2）
- `num_ppo_epochs`：每批次的训练轮数（2-4）
- `cliprange`：PPO裁剪值（0.1-0.3）
- `vf_coef`：价值函数系数（0.1）

## GRPO（群体相对策略优化）

一种具有内存高效特性的在线强化学习算法。

### 基本用法

```python
from trl import GRPOTrainer, GRPOConfig
from datasets import load_dataset

# Define reward function
def reward_func(completions, **kwargs):
    return [len(set(c.split())) for c in completions]

config = GRPOConfig(
    output_dir="model-grpo",
    num_generations=4,  # Completions per prompt
    max_new_tokens=128
)

trainer = GRPOTrainer(
    model="Qwen/Qwen2-0.5B-Instruct",
    reward_funcs=reward_func,
    args=config,
    train_dataset=load_dataset("trl-lib/tldr", split="train")
)
trainer.train()
```

### 关键参数

- `num_generations`：2至8次补全生成
- `max_new_tokens`：64至256个新token
- 学习率：1e-5至1e-4

## 内存消耗对比

| 方法 | 7B模型内存占用 | 计算速度 | 适用场景 |
|------|--------------|----------|----------|
| PPO | 40GB | 中等 | 需要最高控制精度 |
| GRPO | 24GB | 快速 | **内存资源受限**的场景 |
| OnlineDPO | 28GB | 快速 | 不需要奖励模型的场景 |

## 参考资料

- PPO相关论文：https://arxiv.org/abs/1707.06347
- GRPO相关论文：https://arxiv.org/abs/2402.03300
- TRL文档：https://huggingface.co/docs/trl/
