# SAELens 参考文档

该目录包含了关于 SAELens 的完整参考资料。

## 目录结构

- [api.md](api.md) - 针对 SAE、TrainingSAE 以及各类配置类的完整 API 参考手册
- [tutorials.md](tutorials.md) - 关于 SAE 训练与分析的逐步指导教程

## 快速链接

- **GitHub 代码库**：https://github.com/jbloomAus/SAELens
- **Neuronpedia**：https://neuronpedia.org（可浏览预训练好的 SAE 特征）
- **HuggingFace SAEs**：搜索标签 `saelens`

## 安装指南

```bash
pip install sae-lens
```

系统要求：Python 3.10 及以上版本，transformer-lens>=2.0.0 版本。

## 基本使用方法

```python
from transformer_lens import HookedTransformer
from sae_lens import SAE

# Load model and SAE
model = HookedTransformer.from_pretrained("gpt2-small", device="cuda")
sae, cfg_dict, sparsity = SAE.from_pretrained(
    release="gpt2-small-res-jb",
    sae_id="blocks.8.hook_resid_pre",
    device="cuda"
)

# Encode activations to sparse features
tokens = model.to_tokens("Hello world")
_, cache = model.run_with_cache(tokens)
activations = cache["resid_pre", 8]

features = sae.encode(activations)  # Sparse feature activations
reconstructed = sae.decode(features)  # Reconstructed activations
```

## 核心概念

### 稀疏自编码器
SAE能够将密集的神经网络激活值分解为稀疏且易于解释的特征：
- **编码器**：将输入维度 d_model 转换为稀疏维度 d_sae（通常具有 4-16 倍的维度扩展）；
- **ReLU/TopK**：用于实现特征稀疏性；
- **解码器**：用于重构原始激活值。

### 训练损失函数
`Loss = MSE(original, reconstructed) + L1_coefficient × L1(features)`

### 关键指标
- **L0值**：活跃特征的平均数量（目标范围：50-200）；
- **CE损失分数**：重构结果与原始模型之间的交叉熵损失（目标范围：80-95%）；
- **死特征**：从未被激活的特征（目标比例：<5%）。

## 可用的预训练 SAE 模型

| 发布版本 | 模型名称 | 描述 |
|---------|---------|------|
| `gpt2-small-res-jb` | GPT-2 Small | 基于残差流的 SAE 模型 |
| `gemma-2b-res` | Gemma 2B | 基于残差流的 SAE 模型 |
| 多种型号 | 在 HuggingFace 上搜索 | 社区训练的 SAE 模型 |
