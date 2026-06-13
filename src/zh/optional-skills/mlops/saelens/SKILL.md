---
name: sparse-autoencoder-training
description: Provides guidance for training and analyzing Sparse Autoencoders (SAEs) using SAELens to decompose neural network activations into interpretable features. Use when discovering interpretable features, analyzing superposition, or studying monosemantic representations in language models.
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [sae-lens>=6.0.0, transformer-lens>=2.0.0, torch>=2.0.0]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Sparse Autoencoders, SAE, Mechanistic Interpretability, Feature Discovery, Superposition]

---

# SAELens：用于实现机制可解释性的稀疏自编码器

SAELens 是用于训练和分析稀疏自编码器（SAEs）的核心库——这是一种将多语义神经网络激活值分解为稀疏且易于理解的特征的技术，其理念源自 Anthropic 在单语义性研究领域的开创性成果。

**GitHub 链接**：[jbloomAus/SAELens](https://github.com/jbloomAus/SAELens)（获得 1,100 多个星标）

## 问题所在：多语义性与叠加效应

神经网络中的单个神经元具有**多语义性**，即它们会在多种语义上截然不同的情境下被激活。这种现象的产生是因为模型利用**叠加效应**来表示超出其神经元数量之外的更多特征，从而导致可解释性变得十分困难。

**SAEs 通过以下方式解决这一问题**：它将密集的激活值分解为稀疏且具有单语义性的特征——对于任意给定的输入，通常只有少量特征会被激活，而且每个特征都对应一个可理解的概念。

## 何时使用 SAELens

**在以下情况下请使用 SAELens：**
- 在模型激活值中挖掘可解释的特征
- 了解模型学到了哪些概念
- 研究叠加效应与特征结构
- 基于特征进行模型引导或消融实验
- 分析与安全性相关的特征（如欺骗行为、偏见、有害内容）

**在以下情况下可考虑其他替代方案：**
- 需要进行基础激活值分析 → 直接使用 **TransformerLens**
- 希望开展因果干预实验 → 使用 **pyvene** 或 **TransformerLens**
- 需要对生产环境中的模型进行引导优化 → 考虑直接进行激活值工程优化

## 安装指南

```bash
pip install sae-lens
```

要求：Python 3.10+，transformer-lens>=2.0.0

## 核心概念

### SAEs的学习内容

SAEs通过稀疏瓶颈结构进行训练，从而重建模型激活值：

```
Input Activation → Encoder → Sparse Features → Decoder → Reconstructed Activation
    (d_model)       ↓        (d_sae >> d_model)    ↓         (d_model)
                 sparsity                      reconstruction
                 penalty                          loss
```

**损失函数**：`MSE(原始数据, 重建结果) + L1系数 × L1(特征值)`

### 关键验证（Anthropic研究）

在《迈向单义性》研究中，人类评估者发现**70%的SAE特征确实具有可解释性**。已发现的特征包括：
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
sae, cfg_dict, sparsity = SAE.from_pretrained(
    release="gpt2-small-res-jb",
    sae_id="blocks.8.hook_resid_pre",
    device="cuda"
)

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

| 发布版本 | 模型名称 | 层数 |
|---------|----------|------|
| `gpt2-small-res-jb` | GPT-2 Small | 多个残差流 |
| `gemma-2b-res` | Gemma 2B | 残差流 |
| HuggingFace 上的其他模型 | 搜索标签 `saelens` | 各种类型 |

### 检查清单
- [ ] 使用 TransformerLens 加载模型
- [ ] 为目标层加载对应的 SAE 模型
- [ ] 将激活值编码为稀疏特征
- [ ] 确定每个标记的顶级激活特征
- [ ] 验证重建质量

## 工作流程 2：训练自定义 SAE 模型

### 分步指南

```python
from sae_lens import SAE, LanguageModelSAERunnerConfig, SAETrainingRunner

# 1. Configure training
cfg = LanguageModelSAERunnerConfig(
    # Model
    model_name="gpt2-small",
    hook_name="blocks.8.hook_resid_pre",
    hook_layer=8,
    d_in=768,  # Model dimension

    # SAE architecture
    architecture="standard",  # or "gated", "topk"
    d_sae=768 * 8,  # Expansion factor of 8
    activation_fn="relu",

    # Training
    lr=4e-4,
    l1_coefficient=8e-5,  # Sparsity penalty
    l1_warm_up_steps=1000,
    train_batch_size_tokens=4096,
    training_tokens=100_000_000,

    # Data
    dataset_path="monology/pile-uncopyrighted",
    context_size=128,

    # Logging
    log_to_wandb=True,
    wandb_project="sae-training",

    # Checkpointing
    checkpoint_path="checkpoints",
    n_checkpoints=5,
)

# 2. Train
trainer = SAETrainingRunner(cfg)
sae = trainer.run()

# 3. Evaluate
print(f"L0 (avg active features): {trainer.metrics['l0']}")
print(f"CE Loss Recovered: {trainer.metrics['ce_loss_score']}")
```

### 关键超参数

| 参数 | 典型值 | 效果 |
|------|--------|------|
| `d_sae` | 4-16× d_model | 特征数量更多，模型容量更大 |
| `l1_coefficient` | 5e-5 至 1e-4 | 值越大，特征稀疏度越高，但精度越低 |
| `lr` | 1e-4 至 1e-3 | 标准优化器的学习率 |
| `l1_warm_up_steps` | 500-2000 | 防止特征过早失效 |

### 评估指标

| 指标 | 目标值 | 含义 |
|------|--------|------|
| **L0** | 50-200 | 每个标记的平均活跃特征数 |
| **CE Loss Score** | 80-95% | 重建结果与原始数据的交叉熵差异比例 |
| **失效特征比例** | <5% | 从未被激活的特征比例 |
| **解释方差** | >90% | 重建质量的高低 |

### 检查清单
- [ ] 选择目标层及挂接点
- [ ] 设置扩展因子（d_sae = 4-16× d_model）
- [ ] 根据期望的稀疏度调整 L1 系数
- [ ] 启用 L1 预热机制以防止特征失效
- [ ] 在训练过程中监控各项指标（使用 Weights & Biases 工具）
- [ ] 验证 L0 值及 CE 损失的恢复情况
- [ ] 检查失效特征的比例

## 工作流程 3：特征分析与调控

### 单个特征的分析

```python
from transformer_lens import HookedTransformer
from sae_lens import SAE
import torch

model = HookedTransformer.from_pretrained("gpt2-small", device="cuda")
sae, _, _ = SAE.from_pretrained(
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

### 问题：无效功能比例过高
```python
# WRONG: No warm-up, features die early
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=1e-4,
    l1_warm_up_steps=0,  # Bad!
)

# RIGHT: Warm-up L1 penalty
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=8e-5,
    l1_warm_up_steps=1000,  # Gradually increase
    use_ghost_grads=True,   # Revive dead features
)
```

### 问题：重建效果不佳（CE恢复率低）
```python
# Reduce sparsity penalty
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=5e-5,  # Lower = better reconstruction
    d_sae=768 * 16,       # More capacity
)
```

### 问题：功能无法被解析
```python
# Increase sparsity (higher L1)
cfg = LanguageModelSAERunnerConfig(
    l1_coefficient=1e-4,  # Higher = sparser, more interpretable
)
# Or use TopK architecture
cfg = LanguageModelSAERunnerConfig(
    architecture="topk",
    activation_fn_kwargs={"k": 50},  # Exactly 50 active features
)
```

### 问题：训练过程中出现内存错误
```python
cfg = LanguageModelSAERunnerConfig(
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

| 类名 | 功能说明 |
|------|---------|
| `SAE` | 稀疏自编码器模型 |
| `LanguageModelSAERunnerConfig` | 训练配置对象 |
| `SAETrainingRunner` | 训练循环管理器 |
| `ActivationsStore` | 激活值收集与批量处理模块 |
| `HookedSAETransformer` | TransformerLens与SAE的集成组件 |

## 参考文档

如需详细的API文档、教程及高级用法，请查看`references/`目录：

| 文件路径 | 内容说明 |
|----------|---------|
| [references/README.md](references/README.md) | 整体概览与快速入门指南 |
| [references/api.md](references/api.md) | SAE、TrainingSAE及相关配置的完整API参考文档 |
| [references/tutorials.md](references/tutorials.md) | 涵盖训练、分析及操作指导的分步教程 |

## 外部资源

### 教程
- [基础加载与分析](https://github.com/jbloomAus/SAELens/blob/main/tutorials/basic_loading_and_analysing.ipynb)
- [训练稀疏自编码器](https://github.com/jbloomAus/SAELens/blob/main/tutorials/training_a_sparse_autoencoder.ipynb)
- [ARENA SAE课程体系](https://www.lesswrong.com/posts/LnHowHgmrMbWtpkxx/intro-to-superposition-and-sparse-autoencoders-colab)

### 学术论文
- [迈向单义性](https://transformer-circuits.pub/2023/monosemantic-features) - Anthropic（2023年）
- [扩展单义性表现](https://transformer-circuits.pub/2024/scaling-monosemanticity/) - Anthropic（2024年）
- [稀疏自编码器可挖掘高度可解释的特征](https://arxiv.org/abs/2309.08600) - Cunningham等人（ICLR 2024）

### 官方文档
- [SAELens文档](https://jbloomaus.github.io/SAELens/)
- [Neuronpedia](https://neuronpedia.org) - 特征浏览器

## SAE架构类型

| 架构类型 | 描述 | 典型应用场景 |
|----------|---------|--------------|
| **标准型** | 使用ReLU激活函数结合L1正则化 | 通用场景 |
| **门控型** | 引入可学习的门控机制 | 实现更精准的稀疏度控制 |
| **TopK型** | 仅保留恰好K个活跃特征 | 确保恒定的稀疏度水平 |

```python
# TopK SAE (exactly 50 features active)
cfg = LanguageModelSAERunnerConfig(
    architecture="topk",
    activation_fn="topk",
    activation_fn_kwargs={"k": 50},
)
```
