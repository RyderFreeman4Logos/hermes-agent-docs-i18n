# 奖励模型

针对强化学习人类反馈优化流程，介绍如何使用TRL方法训练奖励模型。

## 概述

奖励模型会根据人类的偏好对内容完成度进行评分。其应用场景包括：
- PPO训练（强化学习反馈）
- GRPO在线强化学习
- 内容完成度排序

## 基本训练流程

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from trl import RewardTrainer, RewardConfig
from datasets import load_dataset

# Load model (num_labels=1 for single reward score)
model = AutoModelForSequenceClassification.from_pretrained(
    "Qwen/Qwen2.5-0.5B-Instruct",
    num_labels=1
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")

# Load preference dataset (chosen/rejected pairs)
dataset = load_dataset("trl-lib/ultrafeedback_binarized", split="train")

# Configure
config = RewardConfig(
    output_dir="Qwen2.5-Reward",
    per_device_train_batch_size=2,
    num_train_epochs=1,
    learning_rate=1e-5
)

# Train
trainer = RewardTrainer(
    model=model,
    args=config,
    processing_class=tokenizer,
    train_dataset=dataset
)
trainer.train()
```

## 数据集格式

必填字段：
```json
{
  "prompt": "Question or instruction",
  "chosen": "Better response",
  "rejected": "Worse response"
}
```

## 布拉德利-特里损失函数

默认损失函数：
```
loss = -log(sigmoid(reward_chosen - reward_rejected))
```

学会区分“选中”与“拒绝”的结果评分。

## 奖励模型使用指南

### 推理阶段

```python
from transformers import pipeline

# Load trained reward model
reward_pipe = pipeline("text-classification", model="Qwen2.5-Reward")

# Score completions
texts = ["Good answer", "Bad answer"]
scores = reward_pipe(texts)
print(scores)  # Higher score = better
```

### 在 PPO 模式下

```python
from trl import PPOTrainer, PPOConfig

config = PPOConfig(
    reward_model_path="Qwen2.5-Reward"  # Use trained reward model
)

trainer = PPOTrainer(
    model=policy_model,
    config=config,
    # Reward model loaded automatically
)
```

## 超参数

| 模型规模 | 学习率 | 批量大小 | 训练轮数 |
|----------|--------|----------|----------|
| <10亿参数 | 2e-5 | 4-8 | 1-2 |
| 10亿–70亿参数 | 1e-5 | 2-4 | 1 |
| 70亿–130亿参数 | 5e-6 | 1-2 | 1 |

## 评估

检查奖励差异：
```python
# Chosen should score higher than rejected
chosen_rewards = model(**chosen_inputs).logits
rejected_rewards = model(**rejected_inputs).logits

accuracy = (chosen_rewards > rejected_rewards).float().mean()
print(f"Accuracy: {accuracy:.2%}")  # Target: >80%
```

## 参考资料

- InstructGPT 论文：https://arxiv.org/abs/2203.02155  
- TRL 文档：https://huggingface.co/docs/trl/reward_trainer
