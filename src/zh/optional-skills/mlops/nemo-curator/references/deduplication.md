# 重复内容去重指南

关于精确匹配、模糊匹配及语义匹配去重的完整指南。

## 精确匹配去重

移除内容完全相同的文档。

```python
from nemo_curator.modules import ExactDuplicates

# Exact deduplication
exact_dedup = ExactDuplicates(
    id_field="id",
    text_field="text",
    hash_method="md5"  # or "sha256"
)

deduped = exact_dedup(dataset)
```

**性能表现**：在 GPU 上的处理速度相比 CPU 快约 16 倍。

## 模糊去重功能

通过 MinHash 和 LSH 算法来删除内容几乎相同的文档。

```python
from nemo_curator.modules import FuzzyDuplicates

fuzzy_dedup = FuzzyDuplicates(
    id_field="id",
    text_field="text",
    num_hashes=260,        # MinHash permutations (more = accurate)
    num_buckets=20,        # LSH buckets (more = faster, less recall)
    hash_method="md5",
    jaccard_threshold=0.8  # Similarity threshold
)

deduped = fuzzy_dedup(dataset)
```

**参数**：
- `num_hashes`：128–512（默认值：260）
- `num_buckets`：10–50（默认值：20）
- `jaccard_threshold`：0.7–0.9（默认值：0.8）

**性能表现**：在8TB数据集上处理速度提升16倍（从120小时缩短至7.5小时）

## 语义去重

通过嵌入技术消除语义上相似的文档。

```python
from nemo_curator.modules import SemanticDuplicates

semantic_dedup = SemanticDuplicates(
    id_field="id",
    text_field="text",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    embedding_batch_size=256,
    threshold=0.85,  # Cosine similarity threshold
    device="cuda"
)

deduped = semantic_dedup(dataset)
```

**模型选项**：
- `all-MiniLM-L6-v2`：速度较快，维度为384
- `all-mpnet-base-v2`：质量更好，维度为768
- 支持自定义模型

## 对比分析

| 方法 | 速度 | 召回率 | 适用场景 |
|------|-------|--------|----------|
| 精确匹配 | 最快 | 100% | 仅用于完全相同的内容 |
| 模糊匹配 | 快 | 约95% | 近似重复内容（推荐） |
| 语义理解 | 较慢 | 约90% | 同义改写、内容重述 |

## 最佳实践建议

1. **先使用精确匹配进行去重**——先移除明显的重复内容
2. **针对大型数据集采用模糊匹配**——可在速度与质量之间取得最佳平衡
3. **对高价值数据使用语义理解方法**——虽成本较高但效果更彻底
4. **需启用GPU加速**——可实现10至16倍的速效提升
