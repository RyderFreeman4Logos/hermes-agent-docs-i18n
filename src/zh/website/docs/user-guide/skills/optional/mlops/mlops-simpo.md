---
title: "Simpo Training — Simple Preference Optimization for LLM alignment"
sidebar_label: "Simpo Training"
description: "Simple Preference Optimization for LLM alignment"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Simpo 训练方法

一种用于大语言模型对齐的简单偏好优化技术。作为 DPO 的无参考模型替代方案，其性能更优（在 AlpacaEval 2.0 测试中提升 6.4 分）。无需参考模型，且比 DPO 更高效。当您希望获得比 DPO/PPO 更简单、更快速的训练流程时，可选用此方法进行偏好对齐。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/simpo` 安装 |
| 路径 | `optional-skills/mlops/simpo` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `torch`, `transformers`, `datasets`, `trl`, `accelerate` |
| 支持平台 | linux、macos、windows |
| 标签 | `训练后优化`, `SimPO`, `偏好优化`, `对齐`, `DPO 替代方案`, `无参考模型`, `大语言模型对齐`, `高效训练` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为此内容。
:::

# SimPO - 简单偏好优化方法

## 快速入门

SimPO 是一种无参考模型的偏好优化技术，无需参考模型即可超越 DPO 的性能表现。

**安装方式**：
```bash
# Create environment
conda create -n simpo python=3.10 && conda activate simpo

# Install PyTorch 2.2.2
# Visit: https://pytorch.org/get-started/locally/

# Install alignment-handbook
git clone https://github.com/huggingface/alignment-handbook.git
cd alignment-handbook
python -m pip install .

# Install Flash Attention 2
python -m pip install flash-attn --no-build-isolation
```

**训练**（Mistral 7B）：
```bash
ACCELERATE_LOG_LEVEL=info accelerate launch \
  --config_file accelerate_configs/deepspeed_zero3.yaml \
  scripts/run_simpo.py \
  training_configs/mistral-7b-base-simpo.yaml
```

## 常见工作流程

### 工作流程 1：基于基础模型（Mistral 7B）进行训练

**配置文件**（`mistral-7b-base-simpo.yaml`）：
```yaml
# Model
model_name_or_path: mistralai/Mistral-7B-v0.1
torch_dtype: bfloat16

# Dataset
dataset_mixer:
  HuggingFaceH4/ultrafeedback_binarized: 1.0
dataset_splits:
  - train_prefs
  - test_prefs

# SimPO hyperparameters
beta: 2.0                  # Reward scaling (2.0-10.0)
gamma_beta_ratio: 0.5       # Target margin (0-1)
loss_type: sigmoid          # sigmoid or hinge
sft_weight: 0.0             # Optional SFT regularization

# Training
learning_rate: 5e-7         # Critical: 3e-7 to 1e-6
num_train_epochs: 1
per_device_train_batch_size: 1
gradient_accumulation_steps: 8

# Output
output_dir: ./outputs/mistral-7b-simpo
```

**启动培训**：
```bash
accelerate launch --config_file accelerate_configs/deepspeed_zero3.yaml \
  scripts/run_simpo.py training_configs/mistral-7b-base-simpo.yaml
```

### 工作流 2：微调指令模型（Llama 3 8B）

**配置文件**（`llama3-8b-instruct-simpo.yaml`）：
```yaml
model_name_or_path: meta-llama/Meta-Llama-3-8B-Instruct

dataset_mixer:
  argilla/ultrafeedback-binarized-preferences-cleaned: 1.0

beta: 2.5
gamma_beta_ratio: 0.5
learning_rate: 5e-7
sft_weight: 0.1             # Add SFT loss to preserve capabilities

num_train_epochs: 1
per_device_train_batch_size: 2
gradient_accumulation_steps: 4
output_dir: ./outputs/llama3-8b-simpo
```

**启动**：
```bash
accelerate launch --config_file accelerate_configs/deepspeed_zero3.yaml \
  scripts/run_simpo.py training_configs/llama3-8b-instruct-simpo.yaml
```

### 工作流 3：需大量推理的任务（较低学习率）

**适用于数学/代码类任务**：
```yaml
model_name_or_path: deepseek-ai/deepseek-math-7b-base

dataset_mixer:
  argilla/distilabel-math-preference-dpo: 1.0

beta: 5.0                   # Higher for stronger signal
gamma_beta_ratio: 0.7       # Larger margin
learning_rate: 3e-7         # Lower LR for reasoning
sft_weight: 0.0

num_train_epochs: 1
per_device_train_batch_size: 1
gradient_accumulation_steps: 16
```

## 何时使用 SimPO 及其替代方案

**适合使用 SimPO 的情况**：
- 希望采用比 DPO 更简单的训练方式（无需参考模型）
- 拥有偏好数据（选择/拒绝对）
- 需要比 DPO 更优异的性能
- 计算资源有限
- 单节点训练即可满足需求

**算法选择指南**：
- **SimPO**：最简单，性能最佳，无需参考模型
- **DPO**：需要参考模型作为基准，策略更为保守
- **PPO**：控制能力最强，但需要奖励模型，设置较为复杂
- **GRPO**：内存效率高的强化学习算法，无需评估器

**应选择替代方案的情况**：
- **OpenRLHF**：支持多节点分布式训练，可采用 PPO/GRPO 算法
- **TRL**：需要在同一框架中整合多种方法
- **DPO**：作为成熟的基准用于性能对比

## 常见问题

**问题：损失发散**

降低学习率：
```yaml
learning_rate: 3e-7  # Reduce from 5e-7
```

降低测试版级别：
```yaml
beta: 1.0  # Reduce from 2.0
```

**问题：模型遗忘自身能力**

添加SFT正则化机制：
```yaml
sft_weight: 0.1  # Add SFT loss component
```

**问题：偏好设置区分度不足**

提高β值与边际值：
```yaml
beta: 5.0            # Increase from 2.0
gamma_beta_ratio: 0.8  # Increase from 0.5
```

**问题：训练过程中出现内存溢出**

减小批量大小：
```yaml
per_device_train_batch_size: 1
gradient_accumulation_steps: 16  # Maintain effective batch
```

启用梯度检查点功能：
```yaml
gradient_checkpointing: true
```

## 高级主题

**损失函数**：如需了解 Sigmoid 损失与 Hinge 损失的对比、数学表达式以及各自的适用场景，请参阅 [references/loss-functions.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/simpo/references/loss-functions.md)。

**超参数调优**：关于 beta、gamma 参数及学习率的选择指南，以及针对不同模型规模的推荐配置，可参考 [references/hyperparameters.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/simpo/references/hyperparameters.md)。

**数据集准备**：数据格式要求、数据质量筛选方法以及自定义数据集的创建方式，详见 [references/datasets.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops/simpo/references/datasets.md)。

## 硬件要求

- **GPU**：推荐使用 NVIDIA A100/H100
- **显存需求**：
  - 7B 模型：1 块 A100 40GB 显存（配合 DeepSpeed ZeRO-3 技术）
  - 8B 模型：2 块 A100 40GB 显存
  - 70B 模型：8 块 A100 80GB 显存
- **单节点部署**：使用 DeepSpeed ZeRO-3 即可满足需求
- **混合精度计算**：推荐采用 BF16 格式

**内存优化方案**：
- DeepSpeed ZeRO-3（默认配置）
- 梯度检查点技术
- Flash Attention 2

## 相关资源

- 论文链接：https://arxiv.org/abs/2405.14734（2024 年 NeurIPS 大会发表）
- GitHub 仓库：https://github.com/princeton-nlp/SimPO
- 模型地址：https://huggingface.co/princeton-nlp
- 对齐手册：https://github.com/huggingface/alignment-handbook
