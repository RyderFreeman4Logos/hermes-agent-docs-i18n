---
title: "Faiss — Facebook's library for efficient similarity search and clustering of dense vectors"
sidebar_label: "Faiss"
description: "Facebook's library for efficient similarity search and clustering of dense vectors"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Faiss

Facebook 开发的用于高效处理密集向量相似性搜索与聚类的库。它能够支持数十亿级向量数据，具备 GPU 加速功能，并提供多种索引类型（Flat、IVF、HNSW）。该库适用于快速 k-NN 搜索、大规模向量检索，以及无需元数据信息的纯相似性搜索场景，是高性能应用的首选工具。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/mlops/faiss` 命令安装 |
| 路径 | `optional-skills/mlops/faiss` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `faiss-cpu`、`faiss-gpu`、`numpy` |
| 支持平台 | linux、macos |
| 标签 | `RAG`、`FAISS`、`相似性搜索`、`向量搜索`、`Facebook AI`、`GPU 加速`、`数十亿级数据`、`K-NN`、`HNSW`、`高性能`、`大规模处理` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，Agent 就会依据此内容执行操作。
:::

# FAISS —— 高效相似性搜索

Facebook AI 开发的可用于处理数十亿级向量相似性搜索的库。

## 何时使用 FAISS

**以下情况适合使用 FAISS：**
- 需要对大规模向量数据集（数百万至数十亿条）进行快速相似性搜索
- 需要 GPU 加速支持
- 仅需进行纯向量相似性比较（无需元数据过滤）
- 对高吞吐量与低延迟有严格要求
- 需要对嵌入向量进行离线/批量处理

**相关数据：**
- **在 GitHub 上拥有 31,700 多个星标**
- 由 Meta/Facebook AI Research 团队开发
- **可处理数十亿级向量数据**
- 基于 **C++** 开发，并提供 Python 接口

**如需其他替代方案，可选择：**
- **Chroma/Pinecone**：适用于需要元数据过滤的场景
- **Weaviate**：需要完整数据库功能时使用
- **Annoy**：功能更简单，但特性较少

## 快速入门

### 安装

```bash
# CPU only
pip install faiss-cpu

# GPU support
pip install faiss-gpu
```

### 基本用法

```python
import faiss
import numpy as np

# Create sample data (1000 vectors, 128 dimensions)
d = 128
nb = 1000
vectors = np.random.random((nb, d)).astype('float32')

# Create index
index = faiss.IndexFlatL2(d)  # L2 distance
index.add(vectors)             # Add vectors

# Search
k = 5  # Find 5 nearest neighbors
query = np.random.random((1, d)).astype('float32')
distances, indices = index.search(query, k)

print(f"Nearest neighbors: {indices}")
print(f"Distances: {distances}")
```

## 索引类型

### 1. 平面索引（精确匹配搜索）

```python
# L2 (Euclidean) distance
index = faiss.IndexFlatL2(d)

# Inner product (cosine similarity if normalized)
index = faiss.IndexFlatIP(d)

# Slowest, most accurate
```

### 2. IVF（倒序文件）——快速近似模式

```python
# Create quantizer
quantizer = faiss.IndexFlatL2(d)

# IVF index with 100 clusters
nlist = 100
index = faiss.IndexIVFFlat(quantizer, d, nlist)

# Train on data
index.train(vectors)

# Add vectors
index.add(vectors)

# Search (nprobe = clusters to search)
index.nprobe = 10
distances, indices = index.search(query, k)
```

### 3. HNSW（分层新维搜索）——最佳质量与速度平衡方案

```python
# HNSW index
M = 32  # Number of connections per layer
index = faiss.IndexHNSWFlat(d, M)

# No training needed
index.add(vectors)

# Search
distances, indices = index.search(query, k)
```

### 4. 产品量化——高效节省内存

```python
# PQ reduces memory by 16-32×
m = 8   # Number of subquantizers
nbits = 8
index = faiss.IndexPQ(d, m, nbits)

# Train and add
index.train(vectors)
index.add(vectors)
```

## 保存与加载

```python
# Save index
faiss.write_index(index, "large.index")

# Load index
index = faiss.read_index("large.index")

# Continue using
distances, indices = index.search(query, k)
```

## GPU加速功能

```python
# Single GPU
res = faiss.StandardGpuResources()
index_cpu = faiss.IndexFlatL2(d)
index_gpu = faiss.index_cpu_to_gpu(res, 0, index_cpu)  # GPU 0

# Multi-GPU
index_gpu = faiss.index_cpu_to_all_gpus(index_cpu)

# 10-100× faster than CPU
```

## 与LangChain的集成

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Create FAISS vector store
vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())

# Save
vectorstore.save_local("faiss_index")

# Load
vectorstore = FAISS.load_local(
    "faiss_index",
    OpenAIEmbeddings(),
    allow_dangerous_deserialization=True
)

# Search
results = vectorstore.similarity_search("query", k=5)
```

## 与 LlamaIndex 的集成

```python
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss

# Create FAISS index
d = 1536
faiss_index = faiss.IndexFlatL2(d)

vector_store = FaissVectorStore(faiss_index=faiss_index)
```

## 最佳实践

1. **选择合适的索引类型**——数据量小于1万时选用Flat索引，1万至100万条数据时选用IVF索引，追求高精度时可选用HNSW索引。
2. **对向量进行归一化处理**——使用IndexFlatIP时需配合已归一化的向量。
3. **大数据集优先使用GPU**——处理速度可提升10到100倍。
4. **保存训练好的索引**——模型训练成本较高。
5. **调整nprobe/ef_search参数**——在速度与精度之间取得平衡。
6. **监控内存使用情况**——处理大规模数据集时建议使用PQ索引。
7. **批量执行查询**——有助于更高效地利用GPU资源。

## 性能表现

| 索引类型 | 构建时间 | 查询速度 | 内存占用 | 准确率 |
|----------|----------|----------|----------|--------|
| Flat | 快 | 慢 | 高 | 100% |
| IVF | 中等 | 快 | 中等 | 95-99% |
| HNSW | 慢 | 最快 | 高 | 99% |
| PQ | 中等 | 快 | 低 | 90-95% |

## 相关资源

- **GitHub仓库**：https://github.com/facebookresearch/faiss ⭐ 31,700+星标
- **文档Wiki**：https://github.com/facebookresearch/faiss/wiki
- **许可证**：MIT协议
