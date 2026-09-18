---
title: "Saelens — Train sparse autoencoders to interpret model features"
sidebar_label: "Saelens"
description: "Train sparse autoencoders to interpret model features"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Saelens

用于训练稀疏自编码器，从而解析模型特征。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/saelens` 安装 |
| 路径 | `optional-skills/mlops\saelens` |
| 版本 | `1.0.1` |
| 开发者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `sae-lens>=6.0.0`, `transformer-lens>=2.0.0`, `torch>=2.0.0` |
| 支持平台 | linux、macos、windows |
| 标签 | `稀疏自编码器`, `SAE`, `机制可解释性`, `特征发现`, `叠加效应` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，代理程序会将此内容视为操作指令。
:::

# SAELens：用于实现机制可解释性的稀疏自编码器

SAELens 是用于训练和分析稀疏自编码器（SAEs）的核心库——这是一种能够将多义神经网络激活值分解为稀疏且易于理解的特征的技术，其设计理念源自 Anthropic 在单义性研究领域的开创性成果。

**GitHub 地址**：[jbloomAus/SAELens](https://github.com/jbloomAus/SAELens)（拥有 1,100 多个星标）

## 问题所在：多义性与叠加效应

神经网络中的单个神经元具有**多义性**——它们会在多个语义上不同的场景下被激活。之所以会出现这种情况，是因为模型利用**叠加原理**来表示超出其神经元数量之外的更多特征，从而导致可解释性变得困难。

**SAE**通过将密集的激活值分解为稀疏的、单义性的特征来解决这一问题——对于任何给定的输入，通常只有少数特征会被激活，且每个特征都对应一个可解释的概念。

## 何时使用 SAELens

**在以下情况下可使用 SAELens：**
- 发现模型激活值中的可解释特征
- 了解模型学习了哪些概念
- 研究叠加原理与特征结构
- 基于特征进行调控或消融实验
- 分析与安全性相关的特征（如欺骗行为、偏见、有害内容）

**在以下情况下可考虑其他替代方案：**
- 需要进行基础激活值分析 → 直接使用 **TransformerLens**
- 希望开展因果干预实验 → 使用 **pyvene** 或 **TransformerLens**
- 需要对生产环境中的模型进行调控 → 考虑直接进行激活值工程

## 安装

```bash
pip install sae-lens
```

要求：Python 3.10+，transformer-lens>=2.0.0

## 核心概念

### SAEs的学习内容

SAEs通过稀疏瓶颈结构被训练来重建模型激活值：

```
Input Activation → Encoder → Sparse Features → Decoder → Reconstructed Activation
    (d_model)       ↓        (d_sae >> d_model)    ↓         (d_model)
                 sparsity                      reconstruction
                 penalty                          loss
```

**损失函数**：`MSE(原始数据, 重建结果) + L1系数 × L1(特征值)`

### 关键验证（Anthropic研究）

在《迈向单义性》研究中，人类评估者发现**70%的SAE特征具备真正的可解释性**。已发现的特征包括：
- DNA序列、法律文本、HTTP请求
- 希伯来语文本、营养成分说明、代码语法
- 情感倾向、命名实体、语法结构

## 工作流程1：加载与分析预训练的SAE模型

### 分步指南

```python
from transformer_lens import HookedTransformer
from sae_lens import SAE

# 1. Load model and pre-trained SAE
model = HookedTransformer.from_pretrained("gpt2-small", device="cuda")
# In sae-lens v6, SAE.from_pretrained() returns JUST the SAE (not a tuple).
sae = SAE.from_pretrained(
    release="gpt2-small-res-jb",
    sae_id="blocks.8.hook_resid_pre",
    device="cuda"
)
# If you also need the cfg dict and feature sparsity, use:
# sae, cfg_dict, sparsity = SAE.from_pretrained_with_cfg_and_sparsity(...)

# 2. Get model activations
tokens = model.to_tokens("The capital of France is Paris")
_, cache = model.run_with_cache(tokens)
activations = cache["resid_pre", 8]  # [batch, pos, d_model]

# 3. Encode to SAE features
sae_features = sae.encode(activations)  # [batch, pos, d_sae]
print(f"Active features: {(sae_features > 0).sum()}")

# 4. Find top features for each position
for pos in range(tokens.shape[1]):
    top_features = sae_features[0, pos].topk(5)
    token = model.to_str_tokens(tokens[0, pos:pos+1])[0]
    print(f"Token '{token}': features {top_features.indices.tolist()}")

# 5. Reconstruct activations
reconstructed = sae.decode(sae_features)
reconstruction_error = (activations - reconstructed).norm()
```

### 可用的预训练 SAE 模型

| 发布版本 | 模型 | 层数 |
|---------|-------|------|
| `gpt2-small-res-jb` | GPT-2 Small | 多个残差流 |
| `gemma-2b-res` | Gemma 2B | 残差流 |
| HuggingFace 上的多种模型 | 搜索标签 `saelens` | 各种类型 |

### 检查清单
- [ ] 使用 TransformerLens 加载模型
- [ ] 为目标层加载对应的 SAE 模型
- [ ] 将激活值编码为稀疏特征
- [ ] 确定每个标记的顶级激活特征
- [ ] 验证重建质量

## 工作流程 2：训练自定义 SAE 模型

### 分步指南

```python
from sae_lens import (
    LanguageModelSAETrainingRunner,
    LanguageModelSAERunnerConfig,
    StandardTrainingSAEConfig,
    LoggingConfig,
)

# 1. Configure training (v6 uses a NESTED config: SAE-specific options live in a
#    `sae=` sub-config, and logging options live in a `logger=` sub-config).
#    Note: `architecture`, `d_sae`, `l1_coefficient` etc. are now on the SAE sub-config,
#    and legacy flat options like `hook_layer`, `activation_fn`, `log_to_wandb` were removed.
cfg = LanguageModelSAERunnerConfig(
    # SAE architecture + sparsity (nested)
    sae=StandardTrainingSAEConfig(
        d_in=768,          # Model dimension
        d_sae=768 * 8,     # Expansion factor of 8
        l1_coefficient=8e-5,  # Sparsity penalty
        apply_b_dec_to_input=True,
        normalize_activations="expected_average_only_in",
    ),

    # Data-generating function (model + hook point)
    model_name="gpt2-small",
    hook_name="blocks.8.hook_resid_pre",  # layer is inferred from hook_name (no hook_layer)

    # Training
    lr=4e-4,
    l1_warm_up_steps=1000,
    train_batch_size_tokens=4096,
    training_tokens=100_000_000,

    # Data
    dataset_path="monology/pile-uncopyrighted",
    context_size=128,

    # Logging (nested)
    logger=LoggingConfig(
        log_to_wandb=True,
        wandb_project="sae-training",
    ),

    # Checkpointing
    checkpoint_path="checkpoints",
    n_checkpoints=5,
)

# 2. Train
trainer = LanguageModelSAETrainingRunner(cfg)  # SAETrainingRunner still works as an alias
sae = trainer.run()

# 3. Evaluate
print(f"L0 (avg active features): {trainer.metrics['l0']}")
print(f"CE Loss Recovered: {trainer.metrics['ce_loss_score']}")
```

> **v6版本迁移说明：** 对于其他类型的SAE，需更换相应的`sae=`子配置——即`GatedTrainingSAEConfig`、`TopKTrainingSAEConfig`（需直接设置参数`k`），或是`JumpReLUTrainingSAEConfig`（会使用`l0_coefficient`参数）。在v6版本中，那些旧式的固定参数选项（如`architecture`、`expansion_factor`、`hook_layer`、`activation_fn`/`activation_fn_kwargs`、`use_ghost_grads`、`ghost_grads`以及解码器相关的初始化参数）已被移除。

### 关键超参数

| 参数 | 典型值 | 影响 |
|------|--------|------|
| `d_sae` | 4-16× d_model | 参数值越大，模型特征越多，容量越高 |
| `l1_coefficient` | 5e-5至1e-4 | 值越大，特征稀疏度越高，但预测精度越低 |
| `lr` | 1e-4至1e-3 | 标准优化器的学习率 |
| `l1_warm_up_steps` | 500-2000 | 防止模型早期出现特征失效现象 |

### 评估指标

| 指标 | 目标值 | 含义 |
|------|--------|------|
| **L0** | 50-200 | 每个标记的平均活跃特征数 |
| **CE Loss Score** | 80-95% | 恢复后的交叉熵损失与原始值的比值 |
| **Dead Features** | <5% | 从未被激活的特征比例 |
| **Explained Variance** | >90% | 重建结果的精确度 |

### 检查清单
- [ ] 选择目标层及挂载点
- [ ] 设置扩展因子（d_sae = 4-16× d_model）
- [ ] 根据所需的特征稀疏度调整`l1_coefficient`值
- [ ] 启用L1预热机制，避免特征失效
- [ ] 在训练过程中监控各项指标（可使用W&B工具）
- [ ] 验证L0值及交叉熵损失的恢复情况
- [ ] 检查特征失效的比例

## 工作流程3：特征分析与调控

### 单个特征的分析

```python
from transformer_lens import HookedTransformer
from sae_lens import SAE
import torch

model = HookedTransformer.from_pretrained("gpt2-small", device="cuda")
sae = SAE.from_pretrained(  # v6 returns just the SAE
    release="gpt2-small-res-jb",
    sae_id="blocks.8.hook_resid_pre",
    device="cuda"
)

# Find what activates a specific feature
feature_idx = 1234
test_texts = [
    "The scientist conducted an experiment",
    "I love chocolate cake",
    "The code compiles successfully",
    "Paris is beautiful in spring",
]

for text in test_texts:
    tokens = model.to_tokens(text)
    _, cache = model.run_with_cache(tokens)
    features = sae.encode(cache["resid_pre", 8])
    activation = features[0, :, feature_idx].max().item()
    print(f"{activation:.3f}: {text}")
```

### 功能引导

```python
def steer_with_feature(model, sae, prompt, feature_idx, strength=5.0):
    """Add SAE feature direction to residual stream."""
    tokens = model.to_tokens(prompt)

    # Get feature direction from decoder
    feature_direction = sae.W_dec[feature_idx]  # [d_model]

    def steering_hook(activation, hook):
        # Add scaled feature direction at all positions
        activation += strength * feature_direction
        return activation

    # Generate with steering
    output = model.generate(
        tokens,
        max_new_tokens=50,
        fwd_hooks=[("blocks.8.hook_resid_pre", steering_hook)]
    )
    return model.to_string(output[0])
```

### 功能归因

```python
# Which features most affect a specific output?
tokens = model.to_tokens("The capital of France is")
_, cache = model.run_with_cache(tokens)

# Get features at final position
features = sae.encode(cache["resid_pre", 8])[0, -1]  # [d_sae]

# Get logit attribution per feature
# Feature contribution = feature_activation × decoder_weight × unembedding
W_dec = sae.W_dec  # [d_sae, d_model]
W_U = model.W_U    # [d_model, vocab]

# Contribution to "Paris" logit
paris_token = model.to_single_token(" Paris")
feature_contributions = features * (W_dec @ W_U[:, paris_token])

top_features = feature_contributions.topk(10)
print("Top features for 'Paris' prediction:")
for idx, val in zip(top_features.indices, top_features.values):
    print(f"  Feature {idx.item()}: {val.item():.3f}")
```

## 常见问题与解决方案

> 下方所有示例均采用 v6 层级化配置结构：与 SAE 相关的选项位于 `sae=` 子配置中（如 `StandardTrainingSAEConfig` / `TopKTrainingSAEConfig` 等），而训练相关参数则仍放在顶层的 `LanguageModelSAERunnerConfig` 中。

### 问题：无效特征比例过高
```python
from sae_lens import LanguageModelSAERunnerConfig, StandardTrainingSAEConfig

# WRONG: no warm-up, features die early
cfg = LanguageModelSAERunnerConfig(
    sae=StandardTrainingSAEConfig(d_in=768, d_sae=768*8, l1_coefficient=1e-4),
    l1_warm_up_steps=0,  # Bad!
)

# RIGHT: warm up the L1 penalty (v6 removed ghost grads; warm-up is the lever now)
cfg = LanguageModelSAERunnerConfig(
    sae=StandardTrainingSAEConfig(d_in=768, d_sae=768*8, l1_coefficient=8e-5),
    l1_warm_up_steps=1000,  # Gradually increase
)
```

### 问题：重建效果不佳（CE恢复率低）
```python
# Reduce sparsity penalty and/or add capacity (both on the SAE sub-config)
cfg = LanguageModelSAERunnerConfig(
    sae=StandardTrainingSAEConfig(
        d_in=768,
        d_sae=768 * 16,       # More capacity
        l1_coefficient=5e-5,  # Lower = better reconstruction
    ),
)
```

### 问题：功能无法被解析
```python
from sae_lens import LanguageModelSAERunnerConfig, StandardTrainingSAEConfig, TopKTrainingSAEConfig

# Increase sparsity (higher L1)
cfg = LanguageModelSAERunnerConfig(
    sae=StandardTrainingSAEConfig(d_in=768, d_sae=768*8, l1_coefficient=1e-4),
)
# Or use a TopK SAE (k is set directly in v6, not via activation_fn_kwargs)
cfg = LanguageModelSAERunnerConfig(
    sae=TopKTrainingSAEConfig(d_in=768, d_sae=768*8, k=50),  # Exactly 50 active features
)
```

### 问题：训练过程中出现内存错误
```python
cfg = LanguageModelSAERunnerConfig(
    sae=StandardTrainingSAEConfig(d_in=768, d_sae=768*8, l1_coefficient=8e-5),
    train_batch_size_tokens=2048,  # Reduce batch size
    store_batch_size_prompts=4,    # Fewer prompts in buffer
    n_batches_in_buffer=8,         # Smaller activation buffer
)
```

## 与 Neuronpedia 的集成

您可以在 [neuronpedia.org](https://neuronpedia.org) 上浏览预训练的 SAE 特征：

```python
# Features are indexed by SAE ID
# Example: gpt2-small layer 8 feature 1234
# → neuronpedia.org/gpt2-small/8-res-jb/1234
```

## 核心类参考

| 类名 | 用途 |
|------|------|
| `SAE` | 稀疏自编码器模型 |
| `LanguageModelSAERunnerConfig` | 最顶层训练配置（包含 `sae=` 和 `logger=` 参数） |
| `StandardTrainingSAEConfig` / `TopKTrainingSAEConfig` / `GatedTrainingSAEConfig` / `JumpReLUTrainingSAEConfig` | 针对不同 SAE 类型的子配置（v6 版本） |
| `LoggingConfig` | 日志记录/Weights & Biases 相关子配置（v6 版本） |
| `LanguageModelSAETrainingRunner` | 训练循环管理器（别名：`SAETrainingRunner`） |
| `ActivationsStore` | 激活值的收集与批处理 |
| `HookedSAETransformer` | TransformerLens 与 SAE 的集成模块 |

## 参考文档

如需详细的 API 文档、教程及高级用法，请查看 `references/` 文件夹：

| 文件路径 | 内容说明 |
|----------|----------|
| [references/README.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops\saelens/references/README.md) | 概述与快速入门指南 |
| [references/api.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops\saelens/references/api.md) | SAE、TrainingSAE 及各类配置的完整 API 参考手册 |
| [references/tutorials.md](https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/mlops\saelens/references/tutorials.md) | 包含训练、分析及控制流程的逐步教程 |

## 外部资源

### 教程资料
- [基础加载与分析](https://github.com/jbloomAus/SAELens/blob/main/tutorials/basic_loading_and_analysing.ipynb)  
- [训练稀疏自编码器](https://github.com/jbloomAus/SAELens/blob/main/tutorials/training_a_sparse_autoencoder.ipynb)  
- [ARENA SAE课程体系](https://www.lesswrong.com/posts/LnHowHgmrMbWtpkxx/intro-to-superposition-and-sparse-autoencoders-colab)  

### 学术论文  
- [迈向单义性](https://transformer-circuits.pub/2023/monosemantic-features) — Anthropic（2023年）  
- [扩展单义性能力](https://transformer-circuits.pub/2024/scaling-monosemanticity/) — Anthropic（2024年）  
- [稀疏自编码器可挖掘高度可解释的特征](https://arxiv.org/abs/2309.08600) — Cunningham等人（ICLR 2024）  

### 官方文档  
- [SAELens文档](https://jbloomaus.github.io/SAELens/)  
- [Neuronpedia](https://neuronpedia.org) — 特征浏览器  

## SAE架构  

| 架构类型 | 描述 | 应用场景 |  
|----------|------|----------|  
| **标准型** | ReLU激活函数 + L1正则化 | 通用场景 |  
| **门控型** | 学习型门控机制 | 更精准的稀疏性控制 |  
| **TopK型** | 恰好K个活跃特征 | 保持稳定的稀疏度 |

```python
from sae_lens import LanguageModelSAERunnerConfig, TopKTrainingSAEConfig

# TopK SAE (exactly 50 features active) — `k` is set on the SAE sub-config in v6
cfg = LanguageModelSAERunnerConfig(
    sae=TopKTrainingSAEConfig(d_in=768, d_sae=768*8, k=50),
)
```
