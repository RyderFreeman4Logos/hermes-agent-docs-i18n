# SAELens 教程

## 教程 1：加载与分析预训练的 SAE 模型

### 目标
加载一个预训练的 SAE 模型，并分析在特定输入下哪些特征会被激活。

### 分步指南

```python
from transformer_lens import HookedTransformer
from sae_lens import SAE
import torch

# 1. Load model and SAE
model = HookedTransformer.from_pretrained("gpt2-small", device="cuda")
sae, cfg_dict, sparsity = SAE.from_pretrained(
    release="gpt2-small-res-jb",
    sae_id="blocks.8.hook_resid_pre",
    device="cuda"
)

print(f"SAE input dim: {sae.cfg.d_in}")
print(f"SAE hidden dim: {sae.cfg.d_sae}")
print(f"Expansion factor: {sae.cfg.d_sae / sae.cfg.d_in:.1f}x")

# 2. Get model activations
prompt = "The capital of France is Paris"
tokens = model.to_tokens(prompt)
_, cache = model.run_with_cache(tokens)
activations = cache["resid_pre", 8]  # [1, seq_len, 768]

# 3. Encode to SAE features
features = sae.encode(activations)  # [1, seq_len, d_sae]

# 4. Analyze sparsity
active_per_token = (features > 0).sum(dim=-1)
print(f"Average active features per token: {active_per_token.float().mean():.1f}")

# 5. Find top features for each token
str_tokens = model.to_str_tokens(prompt)
for pos in range(len(str_tokens)):
    top_features = features[0, pos].topk(5)
    print(f"\nToken '{str_tokens[pos]}':")
    for feat_idx, feat_val in zip(top_features.indices, top_features.values):
        print(f"  Feature {feat_idx.item()}: {feat_val.item():.3f}")

# 6. Check reconstruction quality
reconstructed = sae.decode(features)
mse = ((activations - reconstructed) ** 2).mean()
print(f"\nReconstruction MSE: {mse.item():.6f}")
```

## 教程 2：训练自定义 SAE 模型

### 目标
在 GPT-2 的激活值上训练稀疏自编码器。

### 分步指南

```python
from sae_lens import LanguageModelSAERunnerConfig, SAETrainingRunner

# 1. Configure training
cfg = LanguageModelSAERunnerConfig(
    # Model
    model_name="gpt2-small",
    hook_name="blocks.6.hook_resid_pre",
    hook_layer=6,
    d_in=768,

    # SAE architecture
    architecture="standard",
    d_sae=768 * 8,  # 8x expansion
    activation_fn="relu",

    # Training
    lr=4e-4,
    l1_coefficient=8e-5,
    l1_warm_up_steps=1000,
    train_batch_size_tokens=4096,
    training_tokens=10_000_000,  # Small run for demo

    # Data
    dataset_path="monology/pile-uncopyrighted",
    streaming=True,
    context_size=128,

    # Dead feature prevention
    use_ghost_grads=True,
    dead_feature_window=5000,

    # Logging
    log_to_wandb=True,
    wandb_project="sae-training-demo",

    # Hardware
    device="cuda",
    dtype="float32",
)

# 2. Train
runner = SAETrainingRunner(cfg)
sae = runner.run()

# 3. Save
sae.save_model("./my_trained_sae")
```

### 超参数调优指南

| 出现的情况 | 建议尝试的操作 |
|---------------|----------------|
| L0值过高（>200） | 提高 `l1_coefficient` 的数值 |
| CE恢复率过低（<80%） | 降低 `l1_coefficient` 的数值，同时提高 `d_sae` 的数值 |
| 失效特征过多（>5%） | 启用 `use_ghost_grads` 参数，并增加 `l1_warm_up_steps` 的数值 |
| 训练过程不稳定 | 降低学习率 `lr`，同时增加 `lr_warm_up_steps` 的数值 |

---

## 教程3：特征归因与引导

### 目标
识别出哪些SAE特征影响了特定预测结果，并利用这些特征进行预测引导。

### 实施步骤

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

# 1. Feature attribution for a specific prediction
prompt = "The capital of France is"
tokens = model.to_tokens(prompt)
_, cache = model.run_with_cache(tokens)
activations = cache["resid_pre", 8]
features = sae.encode(activations)

# Target token
target_token = model.to_single_token(" Paris")

# Compute feature contributions to target logit
# contribution = feature_activation * decoder_weight * unembedding
W_dec = sae.W_dec  # [d_sae, d_model]
W_U = model.W_U    # [d_model, d_vocab]

# Feature direction projected to vocabulary
feature_to_logit = W_dec @ W_U  # [d_sae, d_vocab]

# Contribution of each feature to "Paris" at final position
feature_acts = features[0, -1]  # [d_sae]
contributions = feature_acts * feature_to_logit[:, target_token]

# Top contributing features
top_features = contributions.topk(10)
print("Top features contributing to 'Paris':")
for idx, val in zip(top_features.indices, top_features.values):
    print(f"  Feature {idx.item()}: {val.item():.3f}")

# 2. Feature steering
def steer_with_feature(feature_idx, strength=5.0):
    """Add a feature direction to the residual stream."""
    feature_direction = sae.W_dec[feature_idx]  # [d_model]

    def hook(activation, hook_obj):
        activation[:, -1, :] += strength * feature_direction
        return activation

    output = model.generate(
        tokens,
        max_new_tokens=10,
        fwd_hooks=[("blocks.8.hook_resid_pre", hook)]
    )
    return model.to_string(output[0])

# Try steering with top feature
top_feature_idx = top_features.indices[0].item()
print(f"\nSteering with feature {top_feature_idx}:")
print(steer_with_feature(top_feature_idx, strength=10.0))
```

## 教程 4：特征消融法

### 目标
通过移除特定特征来测试其因果重要性。

### 操作步骤

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

prompt = "The capital of France is"
tokens = model.to_tokens(prompt)

# Baseline prediction
baseline_logits = model(tokens)
target_token = model.to_single_token(" Paris")
baseline_prob = torch.softmax(baseline_logits[0, -1], dim=-1)[target_token].item()
print(f"Baseline P(Paris): {baseline_prob:.4f}")

# Get features to ablate
_, cache = model.run_with_cache(tokens)
activations = cache["resid_pre", 8]
features = sae.encode(activations)
top_features = features[0, -1].topk(10).indices

# Ablate top features one by one
for feat_idx in top_features:
    def ablation_hook(activation, hook, feat_idx=feat_idx):
        # Encode → zero feature → decode
        feats = sae.encode(activation)
        feats[:, :, feat_idx] = 0
        return sae.decode(feats)

    ablated_logits = model.run_with_hooks(
        tokens,
        fwd_hooks=[("blocks.8.hook_resid_pre", ablation_hook)]
    )
    ablated_prob = torch.softmax(ablated_logits[0, -1], dim=-1)[target_token].item()
    change = (ablated_prob - baseline_prob) / baseline_prob * 100
    print(f"Ablate feature {feat_idx.item()}: P(Paris)={ablated_prob:.4f} ({change:+.1f}%)")
```

## 教程 5：对比不同提示下的功能表现

### 目标
找出针对某一概念时始终会启用的功能。

### 分步指南

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

# Test prompts about the same concept
prompts = [
    "The Eiffel Tower is located in",
    "Paris is the capital of",
    "France's largest city is",
    "The Louvre museum is in",
]

# Collect feature activations
all_features = []
for prompt in prompts:
    tokens = model.to_tokens(prompt)
    _, cache = model.run_with_cache(tokens)
    activations = cache["resid_pre", 8]
    features = sae.encode(activations)
    # Take max activation across positions
    max_features = features[0].max(dim=0).values
    all_features.append(max_features)

all_features = torch.stack(all_features)  # [n_prompts, d_sae]

# Find features that activate consistently
mean_activation = all_features.mean(dim=0)
min_activation = all_features.min(dim=0).values

# Features active in ALL prompts
consistent_features = (min_activation > 0.5).nonzero().squeeze(-1)
print(f"Features active in all prompts: {len(consistent_features)}")

# Top consistent features
top_consistent = mean_activation[consistent_features].topk(min(10, len(consistent_features)))
print("\nTop consistent features (possibly 'France/Paris' related):")
for idx, val in zip(top_consistent.indices, top_consistent.values):
    feat_idx = consistent_features[idx].item()
    print(f"  Feature {feat_idx}: mean activation {val.item():.3f}")
```

## 外部资源

### 官方教程
- [基础加载与分析](https://github.com/jbloomAus/SAELens/blob/main/tutorials/basic_loading_and_analysing.ipynb)
- [训练稀疏自编码器](https://github.com/jbloomAus/SAELens/blob/main/tutorials/training_a_sparse_autoencoder.ipynb)
- [带特征值的Logits Lens方法](https://github.com/jbloomAus/SAELens/blob/main/tutorials/logits_lens_with_features.ipynb)

### ARENA课程体系
全面的稀疏自编码器课程：https://www.lesswrong.com/posts/LnHowHgmrMbWtpkxx/intro-to-superposition-and-sparse-autoencoders-colab

### 核心论文
- [迈向单义性](https://transformer-circuits.pub/2023/monosemantic-features) - Anthropic（2023年）
- [扩展单义性能力](https://transformer-circuits.pub/2024/scaling-monosemanticity/) - Anthropic（2024年）
- [稀疏自编码器可帮助发现可解释的特征](https://arxiv.org/abs/2309.08600) - ICLR 2024
