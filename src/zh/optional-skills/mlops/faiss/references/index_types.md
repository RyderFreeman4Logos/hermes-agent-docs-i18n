# FAISS 索引类型指南

关于如何选择及使用 FAISS 索引类型的完整指南。

## 索引选择指南

| 数据集规模 | 索引类型 | 是否需要训练 | 准确率 | 速度 |
|--------------|----------|--------------|--------|------|
| < 10K | Flat | 否 | 100% | 慢 |
| 10K-1M | IVF | 是 | 95-99% | 快 |
| 1M-10M | HNSW | 否 | 99% | 最快 |
| > 10M | IVF+PQ | 是 | 90-95% | 速度快，内存占用低 |

## Flat 索引（精确搜索）

### IndexFlatL2 - L2（欧几里得）距离

```python
import faiss
import numpy as np

d = 128  # Dimension
index = faiss.IndexFlatL2(d)

# Add vectors
vectors = np.random.random((1000, d)).astype('float32')
index.add(vectors)

# Search
k = 5
query = np.random.random((1, d)).astype('float32')
distances, indices = index.search(query, k)
```

**适用场景：**
- 数据集向量数量少于 10,000 个
- 需要 100% 的准确率
- 用作基准模型

### IndexFlatIP - 内积（余弦相似度）

请翻译完整的输入内容，切勿提前终止。

```python
# For cosine similarity, normalize vectors first
import faiss

d = 128
index = faiss.IndexFlatIP(d)

# Normalize vectors (required for cosine similarity)
faiss.normalize_L2(vectors)
index.add(vectors)

# Search
faiss.normalize_L2(query)
distances, indices = index.search(query, k)
```

**适用场景：**
- 需要计算余弦相似度
- 推荐系统
- 文本嵌入技术

## IVF索引（倒排文件）

### IndexIVFFlat - 基于聚类的搜索方式

```python
# Create quantizer
quantizer = faiss.IndexFlatL2(d)

# Create IVF index with 100 clusters
nlist = 100  # Number of clusters
index = faiss.IndexIVFFlat(quantizer, d, nlist)

# Train on data (required!)
index.train(vectors)

# Add vectors
index.add(vectors)

# Search (nprobe = clusters to search)
index.nprobe = 10  # Search 10 closest clusters
distances, indices = index.search(query, k)
```

**参数：**
- `nlist`：集群数量（建议范围为 √N 至 4√N）
- `nprobe`：需搜索的集群数（取值范围为 1-nlist，数值越大搜索精度越高）

**适用场景：**
- 数据集包含 1万至100万个向量
- 需要快速的近似搜索结果
- 可承受相应的训练时间成本

### 调整 nprobe 值的技巧

```python
# Test different nprobe values
for nprobe in [1, 5, 10, 20, 50]:
    index.nprobe = nprobe
    distances, indices = index.search(query, k)
    # Measure recall/speed trade-off
```

**使用指南：**
- `nprobe=1`：速度最快，召回率约为50%
- `nprobe=10`：平衡性较好，召回率约为95%
- `nprobe=nlist`：精确搜索（与Flat模式相同）

## HNSW索引（基于图结构）

### IndexHNSWFlat - 分层新维搜索

```python
# HNSW index
M = 32  # Number of connections per layer (16-64)
index = faiss.IndexHNSWFlat(d, M)

# Optional: Set ef_construction (build time parameter)
index.hnsw.efConstruction = 40  # Higher = better quality, slower build

# Add vectors (no training needed!)
index.add(vectors)

# Search
index.hnsw.efSearch = 16  # Search time parameter
distances, indices = index.search(query, k)
```

**参数：**
- `M`：每层的连接数（16-64，默认值为32）
- `efConstruction`：构建质量（40-200，数值越高效果越好）
- `efSearch`：搜索质量（16-512，数值越高结果越精确）

**适用场景：**
- 需要最高质量的近似搜索结果
- 能够承担更高的内存消耗（即更多的连接数）
- 数据集向量数量为100万至1000万

## PQ索引（产品量化）

### IndexPQ – 高内存效率型

```python
# PQ reduces memory by 16-32×
m = 8   # Number of subquantizers (divides d)
nbits = 8  # Bits per subquantizer

index = faiss.IndexPQ(d, m, nbits)

# Train (required!)
index.train(vectors)

# Add vectors
index.add(vectors)

# Search
distances, indices = index.search(query, k)
```

**参数：**
- `m`：子量化级数（d 必须能被 m 整除）
- `nbits`：每个码元的位数（8 或 16）

**内存节省效果：**
- 原始格式：d × 4 字节（float32格式）
- PQ格式：m 字节
- 压缩比：4d/m

**适用场景：**
- 内存资源有限的情况
- 数据集规模较大（超过1000万个向量）
- 可接受约90-95%的准确率

### IndexIVFPQ —— IVF与PQ相结合的格式

```python
# Best for very large datasets
nlist = 4096
m = 8
nbits = 8

quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, nbits)

# Train
index.train(vectors)
index.add(vectors)

# Search
index.nprobe = 32
distances, indices = index.search(query, k)
```

**适用场景：**
- 数据集向量数量超过 1000 万
- 需要快速搜索且内存占用较低
- 可接受 90%-95% 的准确率

## GPU 索引

### 单个 GPU

```python
import faiss

# Create CPU index
index_cpu = faiss.IndexFlatL2(d)

# Move to GPU
res = faiss.StandardGpuResources()  # GPU resources
index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)  # GPU 0

# Use normally
index_gpu.add(vectors)
distances, indices = index_gpu.search(query, k)
```

### 多 GPU 支持

```python
# Use all available GPUs
index_gpu = faiss.index_cpu_to_all_gpus(index_cpu)

# Or specific GPUs
gpus = [0, 1, 2, 3]  # Use GPUs 0-3
index_gpu = faiss.index_cpu_to_gpus_list(index_cpu, gpus)
```

**性能提升：**
- 单GPU：相比CPU速度提升10至50倍
- 多GPU：近乎线性扩展

## 索引工厂

```python
# Easy index creation with string descriptors
index = faiss.index_factory(d, "IVF100,Flat")
index = faiss.index_factory(d, "HNSW32")
index = faiss.index_factory(d, "IVF4096,PQ8")

# Train and use
index.train(vectors)
index.add(vectors)
```

**常用描述符：**
- `"Flat"`：精确搜索
- `"IVF100,Flat"`：包含100个分区的IVF索引
- `"HNSW32"`：M值为32的HNSW索引
- `"IVF4096,PQ8"`：结合PQ压缩技术的IVF索引

## 性能对比

### 搜索速度（100万个向量，k=10）

| 索引类型 | 构建时间 | 搜索时间 | 内存占用 | 召回率 |
|---------|----------|----------|----------|--------|
| Flat | 0秒 | 50毫秒 | 512 MB | 100% |
| IVF100 | 5秒 | 2毫秒 | 512 MB | 95% |
| HNSW32 | 60秒 | 1毫秒 | 1GB | 99% |
| IVF4096+PQ8 | 30秒 | 3毫秒 | 32 MB | 90% |

*测试环境：CPU（16核），向量维度为128*

## 最佳实践建议

1. **从Flat索引开始**——作为性能对比的基准
2. **中等规模数据集选用IVF索引**——性能与效率平衡较好
3. **在内存允许的情况下使用HNSW索引**——可获得最佳搜索质量
4. **大规模数据集可加入PQ压缩技术**——以节省内存
5. **当向量数量超过10万时使用GPU加速**——速度可提升10至50倍
6. **调整nprobe/efSearch参数**——在搜索速度与精度之间取得平衡
7. **使用具有代表性的数据集进行训练**——有助于获得更好的聚类效果
8. **保存训练好的索引文件**——避免重复训练

## 参考资源

- **Wiki文档**：https://github.com/facebookresearch/faiss/wiki
- **相关论文**：https://arxiv.org/abs/1702.08734
