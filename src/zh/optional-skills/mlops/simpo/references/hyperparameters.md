# 超参数

关于SimPO超参数选择与调优的完整指南。

## 概述

SimPO中的关键超参数：
1. **学习率**——最为重要
2. **Beta（β）**——奖励缩放因子
3. **Gamma-Beta比率（γ/β）**——目标边际值
4. **SFT权重**——正则化强度

## 学习率

### 推荐范围

**按模型规模划分**：
| 模型规模 | 学习率 | 备注 |
|----------|--------|------|
| 1B-3B | 5e-7 至 1e-6 | 较高值更安全 |
| 7B-8B | 3e-7 至 5e-7 | **标准值** |
| 13B-30B | 1e-7 至 3e-7 | 为保证稳定性可选用较低值 |
| 70B+ | 5e-8 至 1e-7 | 非常保守的设置 |

**按任务类型划分**：
| 任务类型 | 学习率 | 原因 |
|----------|--------|------|
| 通用对话 | 5e-7 | 标准值 |
| 代码生成 | 3e-7 | **需要精确推理** |
| 数学推理 | 3e-7 | **需谨慎优化** |
| 创意写作 | 1e-6 | 可适当提高以获得更好效果 |

### 为何学习率如此重要

**过高**（7B模型超过1e-6）：
- 损失函数发散
- 灾难性遗忘
- 训练过程不稳定

**过低**（7B模型低于1e-7）：
- 收敛速度极慢
| 可能无法在规定时间内完成训练
| 学习不足

**最佳值**（7B模型为3e-7至5e-7）：
- 收敛稳定
| 最终性能优异
| 训练效率较高

### 配置示例

**Mistral 7B（通用任务）**：
```yaml
learning_rate: 5e-7
num_train_epochs: 1
warmup_ratio: 0.1
lr_scheduler_type: cosine
```

**Llama 3 8B（推理版）**：
```yaml
learning_rate: 3e-7
num_train_epochs: 1
warmup_ratio: 0.1
lr_scheduler_type: cosine
```

**Gemma 2 9B（创意版）**：
```yaml
learning_rate: 1e-6
num_train_epochs: 1
warmup_ratio: 0.1
lr_scheduler_type: linear
```

## Beta（β）

### 推荐值

**范围**：2.0 至 10.0（远高于 DPO 的 0.01-0.1）

**按偏好强度划分**：
| Beta | 偏好强度 | 使用场景 |
|------|-------------------|----------|
| 1.0-2.0 | 弱 | 微妙的偏好 |
| 2.0-5.0 | **标准** | 通用对齐 |
| 5.0-10.0 | 强 | 明确的偏好 |

**默认值**：2.0 至 2.5

### 为何 Beta 很重要

**Beta 值过低**（< 2.0）：
- 奖励信号较弱
- 偏好学习速度较慢
- 可能出现欠拟合现象

**Beta 值过高**（> 10.0）：
- 奖励信号过强
- 存在过拟合风险
- 可能忽略微弱的偏好

**最佳值**（2.0-5.0）：
- 奖励强度平衡
- 训练过程稳定
- 具备良好的泛化能力

### 与 Gamma 的协同作用

**Beta 与 Gamma 同时使用**：
```
Target margin in reward space = gamma
Target margin in logit space = gamma / beta
```

**示例**：
```yaml
beta: 2.0
gamma_beta_ratio: 0.5
# Effective gamma = 2.0 * 0.5 = 1.0
```

### 配置示例

**弱偏好设置**：
```yaml
beta: 2.0
gamma_beta_ratio: 0.3  # Small margin
```

**标准版**：
```yaml
beta: 2.5
gamma_beta_ratio: 0.5  # Default
```

**强优先级设置**：
```yaml
beta: 5.0
gamma_beta_ratio: 0.7  # Larger margin
```

## Γ/β 比值

### 推荐值

**范围**：0.0 至 1.0

**不同场景下的推荐值**：
| 比值 | 容差范围 | 适用场景 |
|-------|----------|----------|
| 0.0-0.3 | 较小 | 偏好数据较不明确 |
| 0.4-0.6 | **标准** | 通用场景 |
| 0.7-1.0 | 较大 | 偏好非常明确 |

**默认值**：0.5

### Γ 值的重要性

**低 Γ 值**（< 0.3）：
- 目标容忍度较小
- 对齐策略较为保守
- 行为更为谨慎

**高 Γ 值**（> 0.7）：
- 目标容忍度较大
| 对齐效果更强
| 策略更为激进

**最佳值**（0.4-0.6）：
- 容差适中
| 训练过程稳定
| 对齐效果良好

### 数学含义

**在损失函数中**：
```python
logits = pi_logratios - gamma_beta_ratio
loss = -log(sigmoid(beta * logits))
```

**解释**：
- gamma_beta_ratio 用于调整决策边界。
- 比值越高，所需的对数概率差就越大。
- 该参数决定了偏好差异需要达到多“明显”才算有效。

### 配置示例

**存在噪声的偏好**：
```yaml
gamma_beta_ratio: 0.3  # Smaller margin, more tolerant
```

**标准版**：
```yaml
gamma_beta_ratio: 0.5  # Default
```

**高质量偏好设置**：
```yaml
gamma_beta_ratio: 0.8  # Larger margin, stricter
```

## SFT 权重

### 推荐值

**范围**：0.0 至 1.0

**按模型类型划分**：
| 模型类型 | SFT 权重 | 原因 |
|----------|-----------|------|
| 基础模型 | 0.0 | 无先验能力 |
| **指令微调模型** | 0.05-0.1 | 保留指令遵循能力 |
| 聊天模型 | 0.1-0.2 | 保留对话能力 |

**默认值**：0.0（不进行 SFT 正则化处理）

### 为何 SFT 权重至关重要

**零 SFT**（0.0）：
- 仅进行偏好优化
- 可能会遗忘原有能力
- 为基础模型的标准设置

**低 SFT 值**（0.05-0.1）：
- 平衡的优化方式
- **推荐用于指令微调模型**
- 能适度保留原有能力

**高 SFT 值**（> 0.2）：
- 能强力保留原有能力
- 偏好对齐效果较弱
- 可能会降低对齐优化效果

### 权衡取舍

```
Total Loss = SimPO Loss + (sft_weight * SFT Loss)
```

**示例**：
```yaml
sft_weight: 0.1
# 90% preference optimization + 10% capability preservation
```

### 配置示例

**基础模型（未经过微调）**：
```yaml
model_name_or_path: mistralai/Mistral-7B-v0.1
sft_weight: 0.0
```

**指令模型（轻量级微调）**：
```yaml
model_name_or_path: meta-llama/Meta-Llama-3-8B-Instruct
sft_weight: 0.1
```

**聊天模型（经过适度监督微调）**：
```yaml
model_name_or_path: HuggingFaceH4/zephyr-7b-beta
sft_weight: 0.2
```

## 不同模型规模的推荐配置

### 7B模型（Mistral、Llama 3）

**标准配置**：
```yaml
learning_rate: 5e-7
beta: 2.0
gamma_beta_ratio: 0.5
sft_weight: 0.0  # 0.1 if instruct model
num_train_epochs: 1
per_device_train_batch_size: 2
gradient_accumulation_steps: 4
```

### 8B-13B 模型

**标准配置**：
```yaml
learning_rate: 3e-7
beta: 2.5
gamma_beta_ratio: 0.5
sft_weight: 0.1  # If instruct
num_train_epochs: 1
per_device_train_batch_size: 1
gradient_accumulation_steps: 8
```

### 70B模型

**标准配置**：
```yaml
learning_rate: 1e-7
beta: 2.0
gamma_beta_ratio: 0.5
sft_weight: 0.05
num_train_epochs: 1
per_device_train_batch_size: 1
gradient_accumulation_steps: 16
```

## 批量大小与梯度累积

### 实际批量大小

```
Effective Batch Size = per_device_batch_size * num_gpus * grad_accum_steps
```

**推荐的理想批量大小**：
- 7B：128–256
- 13B：64–128
- 70B：32–64

### 配置示例

**单张 GPU（A100 40GB）**：
```yaml
per_device_train_batch_size: 1
gradient_accumulation_steps: 128  # Effective batch = 128
```

**4块GPU（A100 40GB）**：
```yaml
per_device_train_batch_size: 2
gradient_accumulation_steps: 16  # Effective batch = 2*4*16 = 128
```

**8块GPU（A100 80GB）**：
```yaml
per_device_train_batch_size: 2
gradient_accumulation_steps: 8  # Effective batch = 2*8*8 = 128
```

## 损失函数类型

### Sigmoid 与 Hinge 对比

**Sigmoid**（默认值，推荐使用）：
```yaml
loss_type: sigmoid
label_smoothing: 0.0
```

**Hinge**（实验性功能）：
```yaml
loss_type: hinge
# No label smoothing for hinge
```

**何时使用 Hinge**：
- 基于边际值的任务
- SVM 类优化算法
- 实验性用途

**通常情况**：建议继续使用 Sigmoid 函数。

## 参数调优指南

### 第一步：从默认值开始

```yaml
learning_rate: 5e-7  # For 7B
beta: 2.0
gamma_beta_ratio: 0.5
sft_weight: 0.0  # 0.1 if instruct
loss_type: sigmoid
```

### 第 2 步：监控训练过程

**每 100 步检查一次**：
- 损失曲线（应呈平滑下降趋势）
- 奖励幅度（应持续上升）
- 被选中/被拒绝的日志概率值（应清晰区分）

### 第 3 步：必要时进行调整

**若损失值出现异常波动**：
```yaml
learning_rate: 3e-7  # Reduce from 5e-7
beta: 1.0           # Reduce from 2.0
```

**如果损失值过早趋于平稳**：
```yaml
learning_rate: 1e-6  # Increase from 5e-7
beta: 5.0           # Increase from 2.0
```

**若模型出现遗忘情况**：
```yaml
sft_weight: 0.2  # Increase from 0.0
```

## 完整示例配置

### Mistral 7B 基础版（标准配置）

```yaml
model_name_or_path: mistralai/Mistral-7B-v0.1
dataset_mixer:
  HuggingFaceH4/ultrafeedback_binarized: 1.0

learning_rate: 5e-7
beta: 2.0
gamma_beta_ratio: 0.5
loss_type: sigmoid
sft_weight: 0.0

num_train_epochs: 1
per_device_train_batch_size: 2
gradient_accumulation_steps: 4
warmup_ratio: 0.1
lr_scheduler_type: cosine

bf16: true
gradient_checkpointing: true
```

### Llama 3 8B Instruct（推理版）

```yaml
model_name_or_path: meta-llama/Meta-Llama-3-8B-Instruct
dataset_mixer:
  argilla/distilabel-math-preference-dpo: 1.0

learning_rate: 3e-7
beta: 5.0
gamma_beta_ratio: 0.7
loss_type: sigmoid
sft_weight: 0.1

num_train_epochs: 1
per_device_train_batch_size: 1
gradient_accumulation_steps: 16
warmup_ratio: 0.1
lr_scheduler_type: cosine
```

## 参考资料

- SimPO 论文：https://arxiv.org/abs/2405.14734
- 对齐手册：https://github.com/huggingface/alignment-handbook
