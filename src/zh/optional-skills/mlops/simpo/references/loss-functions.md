# 损失函数

关于SimPO损失函数及其数学公式的完整指南。

## 概述

SimPO支持两种类型的损失函数：
- **Sigmoid**（默认值）——平滑且可微分的损失函数
- **Hinge**——基于边界的稀疏损失函数

这两种损失函数均无需参考模型（不需要参照模型）。

## SimPO损失函数公式

### 核心计算过程

**步骤1：对数概率比**：
```
pi_logratios = log P_θ(y_chosen|x) - log P_θ(y_rejected|x)
```

**步骤 2：应用目标利润率**：
```
logits = pi_logratios - γ/β
```
位置：
- γ/β = `gamma_beta_ratio`（目标边际值）

**步骤 3：计算损失值**（具体方式取决于损失类型）

### Sigmoid 损失（默认值）

**公式**：
```
L = -log σ(β * logits) * (1 - ε) - log σ(-β * logits) * ε
```

其中：
- β = `beta`（奖励缩放系数）
- σ = Sigmoid函数
- ε = `label_smoothing`（默认值为0.0）

**实现方式**：
```python
losses = (
    -F.logsigmoid(self.beta * logits) * (1 - self.label_smoothing)
    - F.logsigmoid(-self.beta * logits) * self.label_smoothing
)
```

**特性**：
- 平滑且连续的渐变效果
- 基于概率的解释机制
- 大多数任务中的标准选择
- 在较高的贝塔值下表现更佳

### Hinge 损失函数

**公式**：
```
L = max(0, 1 - β * logits)
```

**实现方式**：
```python
losses = torch.relu(1 - self.beta * logits)
```

**特性**：
- 非平滑型（在 logits = 1/β 处存在折点）
- 基于边际值（类似 SVM 方法）
- 可产生更稀疏的解
- 应用较为少见

## 与 DPO 的对比

### DPO 损失函数（需要参考模型）

**公式**：
```
L_DPO = -E[log σ(β * log(π_θ(y_w|x)/π_ref(y_w|x)) - β * log(π_θ(y_l|x)/π_ref(y_l|x)))]
```

**主要特性**：
- 需要参考模型 π_ref
- 按参考日志概率进行归一化处理
- 更为保守（结果更接近参考值）

### SimPO 损失函数（无需参考模型）

**公式**：
```
L_SimPO = -log σ(β * (log π_θ(y_w|x) - log π_θ(y_l|x) - γ/β))
```

**核心特性**：
- 无需参考模型
- 直接进行偏好优化
- 通过目标边际值 γ/β 控制偏好强度
- 效率更高（模型前向传播次数更少）

**可视化对比**：
```
DPO:    [Policy] - [Reference] → Loss
SimPO:  [Policy]               → Loss
```

## 平均对数概率奖励

### 计算方式

**每个标记的对数概率**：
```python
# Get log probs for each token
per_token_logps = log_softmax(logits).gather(dim=-1, index=labels)

# Create mask to ignore padding
loss_mask = (labels != label_pad_token_id)
```

**平均对数概率**（当 `average_log_prob=True` 时）：
```python
avg_logp = (per_token_logps * loss_mask).sum(-1) / loss_mask.sum(-1)
```

**对数概率总和**（当 `average_log_prob=False` 时）：
```python
sum_logp = (per_token_logps * loss_mask).sum(-1)
```

**为何选择平均值？**
- 根据序列长度进行标准化处理
- 避免对过短或过长的回复产生偏好
- 这是 SimPO 中的通用做法

### 奖励指标

**所选奖励方式**：
```python
chosen_rewards = beta * policy_chosen_logps.detach()
```

**被拒绝的奖励**：
```python
rejected_rewards = beta * policy_rejected_logps.detach()
```

**奖励边际**：
```python
reward_margin = chosen_rewards.mean() - rejected_rewards.mean()
```

## 标签平滑技术

### 带平滑项的公式

**Sigmoid损失函数**：
```
L = -log σ(β * logits) * (1 - ε) - log σ(-β * logits) * ε
```

**效果**：
- ε = 0.0：不进行平滑处理（默认值）
- ε = 0.1：10%的平滑处理（软标签）
- ε = 0.5：最大程度的平滑处理

**适用场景**：
- 带有噪声的偏好标签
- 不确定的偏好
- 防止过度自信

**配置参数**：
```yaml
label_smoothing: 0.1  # 10% smoothing
```

## SFT 正则化

### 组合损失函数

**包含 SFT 组件时**：
```
L_total = L_SimPO + λ * L_SFT
```

其中：
- L_SFT = 所选响应的交叉熵损失
- λ = `sft_weight`（取值范围为 0.0 至 1.0）

**实现方式**：
```python
if self.sft_weight > 0:
    sft_loss = -policy_chosen_logps
    total_loss = simpo_loss + self.sft_weight * sft_loss
```

**适用场景**：
- 保留模型原有能力
- 防止灾难性遗忘
- 对模型进行微调指导

**权衡因素**：
- 较高的 sft_weight 值：能更好保留模型能力，但对齐效果较差
- 较低的 sft_weight 值：对齐效果更佳，但可能导致模型遗忘原有能力

**配置参数**：
```yaml
sft_weight: 0.1  # 10% SFT regularization
```

## 损失函数类型选择

### Sigmoid 与 Hinge

| 维度 | Sigmoid | Hinge |
|------|---------|-------|
| 平滑性 | 平滑 | 不平滑 |
| 梯度 | 连续 | 在边界处不连续 |
| 稀疏性 | 解为密集形式 | 解为稀疏形式 |
| 可解释性 | 概率型 | 几何边界型 |
| 典型应用场景 | **通用场景** | 基于边界的任务 |
| 推荐方案 | **默认选择** | 实验性方案 |

**配置项**：
```yaml
# Sigmoid (default)
loss_type: sigmoid

# Hinge (alternative)
loss_type: hinge
```

## 数学特性

### 梯度分析

**Sigmoid 损失函数梯度**：
```
∂L/∂logits = -β * σ(-β * logits) * (1 - ε) + β * σ(β * logits) * ε
```

**Hinge 损失梯度**：
```
∂L/∂logits = -β   if logits < 1/β
             0     otherwise
```

**影响**：
- Sigmoid函数：始终会输出梯度信号
- Hinge函数：在满足阈值条件时无梯度输出

### 收敛行为

**Sigmoid函数**：
- 损失值逐渐趋近于零
- 即使存在较大损失差距也会持续优化
- 训练曲线更为平滑

**Hinge函数**：
- 在达到阈值条件时损失值为零
- 一旦满足阈值条件即停止优化
- 可能会出现训练停滞现象

## 完整损失示例

### 示例1：基础SimPO（Sigmoid函数）

**配置**：
```yaml
beta: 2.0
gamma_beta_ratio: 0.5
loss_type: sigmoid
label_smoothing: 0.0
sft_weight: 0.0
```

**损失计算**：
```python
# Step 1: Compute log probs
chosen_logps = avg_log_prob(policy(chosen))    # e.g., -1.2
rejected_logps = avg_log_prob(policy(rejected)) # e.g., -2.5

# Step 2: Log ratio and margin
pi_logratios = -1.2 - (-2.5) = 1.3
logits = 1.3 - 0.5 = 0.8

# Step 3: Sigmoid loss
loss = -log(sigmoid(2.0 * 0.8))
     = -log(sigmoid(1.6))
     = -log(0.832)
     = 0.184
```

### 示例 2：结合 SFT 的 SimPO

**配置**：
```yaml
beta: 2.5
gamma_beta_ratio: 0.5
loss_type: sigmoid
sft_weight: 0.1
```

**损失计算**：
```python
# SimPO loss (as above)
simpo_loss = 0.184

# SFT loss
sft_loss = -chosen_logps = -(-1.2) = 1.2

# Total loss
total_loss = simpo_loss + 0.1 * sft_loss
           = 0.184 + 0.12
           = 0.304
```

## 调试

### 检查奖励边际值

**边际值较低（< 0.5）**：
- 模型未能学习到用户偏好
- 增大 beta 参数或 gamma_beta_ratio 的值

**边际值较高（> 5.0）**：
- 可能存在过拟合现象
- 减小 beta 参数或学习率

**监控措施**：
```python
reward_margin = chosen_rewards.mean() - rejected_rewards.mean()
print(f"Reward margin: {reward_margin:.2f}")
```

### 检查日志概率

**典型数值范围**：
- 被选中值：-1.0 至 -2.0（数值越高越好）
- 被拒绝值：-2.0 至 -4.0（数值越低越差）

**异常警示信号**：
- 两者均为极负值（< -10）：模型未处于学习状态
- 两者均为正值（> 0）：存在数值不稳定问题

## 参考资料

- SimPO 论文：https://arxiv.org/abs/2405.14734
- DPO 论文：https://arxiv.org/abs/2305.18290
- 实现代码：https://github.com/princeton-nlp/SimPO
