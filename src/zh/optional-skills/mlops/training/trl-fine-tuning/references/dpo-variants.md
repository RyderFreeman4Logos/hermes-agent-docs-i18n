# DPO 变体

关于 TRL 中直接偏好优化损失函数的完整指南。

## 概述

DPO 利用偏好数据（选择/拒绝对）来优化模型。TRL 支持针对不同场景的 10 多种损失函数变体。

## 损失函数类型

### 1. Sigmoid（标准 DPO）

**公式**：`-log(sigmoid(β * logits))`

**适用场景**：默认选择方式，通用偏好对齐

**配置参数**：
```python
DPOConfig(
    loss_type="sigmoid",
    beta=0.1,  # KL penalty
    per_device_train_batch_size=64,
    learning_rate=1e-6
)
```

### 2. IPO（身份策略优化）

**公式**：`(logits - 1/(2β))²`

**适用场景**：具备更坚实的理论基础，有助于降低过拟合现象

**配置参数**：
```python
DPOConfig(
    loss_type="ipo",
    beta=0.1,
    per_device_train_batch_size=90,
    learning_rate=1e-2
)
```

### 3. Hinge（SLiC）

**公式**：`ReLU(1 - β * logits)`

**适用场景**：基于边际的目标函数

**配置参数**：
```python
DPOConfig(
    loss_type="hinge",
    beta=0.1,
    per_device_train_batch_size=512,
    learning_rate=1e-4
)
```

### 4. 强健的差分隐私优化器

**公式**：采用带标签平滑处理的Sigmoid函数，以提高对噪声的抵抗能力

**适用场景**：偏好标签中存在噪声的情况

**配置参数**：
```python
DPOConfig(
    loss_type="robust",
    beta=0.01,
    label_smoothing=0.1,  # Noise probability
    per_device_train_batch_size=16,
    learning_rate=1e-3,
    max_prompt_length=128,
    max_length=512
)
```

### 5. BCO配对（二分类）

**计算公式**：训练二分类模型（选择=1，拒绝=0）

**适用场景**：存在成对偏好数据的情况

**配置参数**：
```python
DPOConfig(
    loss_type="bco_pair",
    beta=0.01,
    per_device_train_batch_size=128,
    learning_rate=5e-7,
    max_prompt_length=1536,
    max_completion_length=512
)
```

### 6. SPPO Hard

**计算公式**：成功推送→0.5，推送失败→-0.5

**适用场景**：纳什均衡状态、数据稀疏的情况

**配置选项**：
```python
DPOConfig(
    loss_type="sppo_hard",
    beta=0.1
)
```

### 7. DiscoPOP

**计算公式**：对数比率调制损耗法

**适用场景**：自动损耗检测

**配置参数**：
```python
DPOConfig(
    loss_type="discopop",
    beta=0.05,
    discopop_tau=0.05,
    per_device_train_batch_size=64,
    learning_rate=5e-7
)
```

### 8. APO Zero

**计算公式**：提高被选中的概率，降低被拒绝的概率

**适用场景**：模型生成的输出质量较差时

**配置参数**：
```python
DPOConfig(
    loss_type="apo_zero",
    beta=0.1,
    per_device_train_batch_size=64,
    learning_rate=2e-7,
    max_prompt_length=512,
    max_completion_length=512
)
```

### 9. APO 关闭模式

**计算公式**：同时降低两项数值，重点突出被拒绝的减少幅度

**适用场景**：模型输出优于获胜答案时

**配置参数**：
```python
DPOConfig(
    loss_type="apo_down",
    beta=0.1,
    # Same hyperparameters as apo_zero
)
```

### 10. AOT与AOT配对模型

**计算公式**：基于随机占优的分布对齐算法

**适用场景**：
- `aot_pair`：成对偏好数据
- `aot`：非成对数据

**配置参数**：
```python
DPOConfig(
    loss_type="aot_pair",  # or "aot"
    beta=0.1,
    label_smoothing=0.0
)
```

## 多损失训练

整合多种损失函数：

```python
DPOConfig(
    loss_type=["sigmoid", "ipo"],
    loss_weights=[0.7, 0.3],  # Weighted combination
    beta=0.1
)
```

## 关键参数

### Beta（β值）

用于控制与参考模型的偏差程度：
- **较高值**（0.5）：更为保守，更贴近参考模型
- **较低值**（0.01）：追求更强的对齐效果
- **默认值**：0.1

### 标签平滑处理

为提升DPO算法的稳定性：
- **0.0**：不进行平滑处理（默认值）
- **0.1-0.3**：具备中等程度的噪声抗扰性
- **0.5**：具有最高的噪声容忍度

### 最大长度限制

- `max_prompt_length`：128–1536
- `max_completion_length`：128–512
- `max_length`：整个序列的最大长度（1024–2048）

## 对比表格

| 损失函数 | 训练速度 | 稳定性 | 最佳适用场景 |
|----------|----------|--------|--------------|
| Sigmoid | 快 | 良好 | **通用场景** |
| IPO | 快 | 更优 | 解决过拟合问题 |
| Hinge | 快 | 良好 | 边界损失函数场景 |
| Robust | 快 | 最佳 | 存在噪声的数据 |
| BCO | 中等 | 良好 | 二分类任务 |
| DiscoPOP | 快 | 良好 | 新型架构模型 |
| APO | 快 | 良好 | 模型质量匹配场景 |

## 参考资料

- DPO相关论文：https://arxiv.org/abs/2305.18290
- IPO相关论文：https://arxiv.org/abs/2310.12036
- TRL文档：https://huggingface.co/docs/trl/dpo_trainer
