# SAELens API 参考手册

## SAE 类

用于表示稀疏自编码器的核心类。

### 加载预训练的 SAE 模型

```python
from sae_lens import SAE

# From official releases
sae, cfg_dict, sparsity = SAE.from_pretrained(
    release="gpt2-small-res-jb",
    sae_id="blocks.8.hook_resid_pre",
    device="cuda"
)

# From HuggingFace
sae, cfg_dict, sparsity = SAE.from_pretrained(
    release="username/repo-name",
    sae_id="path/to/sae",
    device="cuda"
)

# From local disk
sae = SAE.load_from_disk("/path/to/sae", device="cuda")
```

### SAE属性

| 属性 | 形状 | 描述 |
|------|------|------|
| `W_enc` | [d_in, d_sae] | 编码器权重 |
| `W_dec` | [d_sae, d_in] | 解码器权重 |
| `b_enc` | [d_sae] | 编码器偏置项 |
| `b_dec` | [d_in] | 解码器偏置项 |
| `cfg` | SAEConfig | 配置对象 |

### 核心方法

#### encode()

```python
# Encode activations to sparse features
features = sae.encode(activations)
# Input: [batch, pos, d_in]
# Output: [batch, pos, d_sae]
```

#### 解码()

```python
# Reconstruct activations from features
reconstructed = sae.decode(features)
# Input: [batch, pos, d_sae]
# Output: [batch, pos, d_in]
```

#### forward() 函数

```python
# Full forward pass (encode + decode)
reconstructed = sae(activations)
# Returns reconstructed activations
```

#### 保存模型()

```python
sae.save_model("/path/to/save")
```

## SAEConfig

用于配置 SAE 架构及训练环境的类。

### 主要参数

| 参数 | 类型 | 描述 |
|------|------|------|
| `d_in` | int | 输入维度（模型的 d_model） |
| `d_sae` | int | SAE 隐藏层维度 |
| `architecture` | str | 架构类型，可选值为 "standard"、"gated"、"jumprelu"、"topk" |
| `activation_fn_str` | str | 激活函数名称 |
| `model_name` | str | 源模型名称 |
| `hook_name` | str | 模型中的钩子点位置 |
| `normalize_activations` | str | 激活值归一化方法 |
| `dtype` | str | 数据类型 |
| `device` | str | 运行设备 |

### 访问配置信息

```python
print(sae.cfg.d_in)      # 768 for GPT-2 small
print(sae.cfg.d_sae)     # e.g., 24576 (32x expansion)
print(sae.cfg.hook_name) # e.g., "blocks.8.hook_resid_pre"
```

## LanguageModelSAERunnerConfig

用于训练 SAE 模型的完整配置项。

### 配置示例

```python
from sae_lens import LanguageModelSAERunnerConfig

cfg = LanguageModelSAERunnerConfig(
    # Model and hook
    model_name="gpt2-small",
    hook_name="blocks.8.hook_resid_pre",
    hook_layer=8,
    d_in=768,

    # SAE architecture
    architecture="standard",  # "standard", "gated", "jumprelu", "topk"
    d_sae=768 * 8,           # Expansion factor
    activation_fn="relu",

    # Training hyperparameters
    lr=4e-4,
    l1_coefficient=8e-5,
    lp_norm=1.0,
    lr_scheduler_name="constant",
    lr_warm_up_steps=500,

    # Sparsity control
    l1_warm_up_steps=1000,
    use_ghost_grads=True,
    feature_sampling_window=1000,
    dead_feature_window=5000,
    dead_feature_threshold=1e-8,

    # Data
    dataset_path="monology/pile-uncopyrighted",
    streaming=True,
    context_size=128,

    # Batch sizes
    train_batch_size_tokens=4096,
    store_batch_size_prompts=16,
    n_batches_in_buffer=64,

    # Training duration
    training_tokens=100_000_000,

    # Logging
    log_to_wandb=True,
    wandb_project="sae-training",
    wandb_log_frequency=100,

    # Checkpointing
    checkpoint_path="checkpoints",
    n_checkpoints=5,

    # Hardware
    device="cuda",
    dtype="float32",
)
```

### 关键参数说明

#### 架构参数

| 参数 | 描述 |
|------|------|
| `architecture` | SAE类型：“standard”、“gated”、“jumprelu”、“topk” |
| `d_sae` | 隐藏层维度（也可使用`expansion_factor`） |
| `expansion_factor` | `d_sae`的替代参数：d_sae = d_in × expansion_factor |
| `activation_fn` | 激活函数，如“relu”、“topk”等 |
| `activation_fn_kwargs` | 激活函数参数的字典（例如，topk功能使用{"k": 50}） |

#### 稀疏性参数

| 参数 | 描述 |
|------|------|
| `l1_coefficient` | L1惩罚系数（数值越大，稀疏程度越高） |
| `l1_warm_up_steps` | L1惩罚逐渐增强的步数 |
| `use_ghost_grads` | 是否将梯度应用于“无效特征” |
| `dead_feature_threshold` | 判定特征为“无效”的激活值阈值 |
| `dead_feature_window` | 检测无效特征的步数窗口 |

#### 学习率参数

| 参数 | 描述 |
|------|------|
| `lr` | 基础学习率 |
| `lr_scheduler_name` | 学习率调度策略，如“constant”、“cosineannealing”等 |
| `lr_warm_up_steps` | 学习率预热步数 |
| `lr_decay_steps` | 学习率衰减的步数 |

---

## SAETrainingRunner

用于执行训练的主类。

### 基本训练流程

```python
from sae_lens import SAETrainingRunner, LanguageModelSAERunnerConfig

cfg = LanguageModelSAERunnerConfig(...)
runner = SAETrainingRunner(cfg)
sae = runner.run()
```

### 查看训练指标

```python
# During training, metrics logged to W&B include:
# - l0: Average active features
# - ce_loss_score: Cross-entropy recovery
# - mse_loss: Reconstruction loss
# - l1_loss: Sparsity loss
# - dead_features: Count of dead features
```

## ActivationsStore

用于管理激活信息的收集与批量处理。

### 基本用法

```python
from sae_lens import ActivationsStore

store = ActivationsStore.from_sae(
    model=model,
    sae=sae,
    store_batch_size_prompts=8,
    train_batch_size_tokens=4096,
    n_batches_in_buffer=32,
    device="cuda",
)

# Get batch of activations
activations = store.get_batch_tokens()
```

## HookedSAETransformer

将 SAE 模型与 TransformerLens 模型相集成。

### 基本用法

```python
from sae_lens import HookedSAETransformer

# Load model with SAE
model = HookedSAETransformer.from_pretrained("gpt2-small")
model.add_sae(sae)

# Run with SAE in the loop
output = model.run_with_saes(tokens, saes=[sae])

# Cache with SAE activations
output, cache = model.run_with_cache_with_saes(tokens, saes=[sae])
```

## SAE 架构

### 标准架构（ReLU + L1）

```python
cfg = LanguageModelSAERunnerConfig(
    architecture="standard",
    activation_fn="relu",
    l1_coefficient=8e-5,
)
```

### 受限访问

```python
cfg = LanguageModelSAERunnerConfig(
    architecture="gated",
)
```

### TopK

```python
cfg = LanguageModelSAERunnerConfig(
    architecture="topk",
    activation_fn="topk",
    activation_fn_kwargs={"k": 50},  # Exactly 50 active features
)
```

### JumpReLU（最先进技术）

```python
cfg = LanguageModelSAERunnerConfig(
    architecture="jumprelu",
)
```

## 实用功能

### 上传至 HuggingFace

```python
from sae_lens import upload_saes_to_huggingface

upload_saes_to_huggingface(
    saes=[sae],
    repo_id="username/my-saes",
    token="hf_token",
)
```

### Neuronpedia 集成

```python
# Features can be viewed on Neuronpedia
# URL format: neuronpedia.org/{model}/{layer}-{sae_type}/{feature_id}
# Example: neuronpedia.org/gpt2-small/8-res-jb/1234
```
