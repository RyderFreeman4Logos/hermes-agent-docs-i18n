---
title: "Pinecone — Managed vector database for production AI applications"
sidebar_label: "Pinecone"
description: "Managed vector database for production AI applications"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Pinecone

专为生产级 AI 应用设计的托管向量数据库。该服务采用全托管模式，具备自动扩展能力，支持混合搜索（密集向量与稀疏向量）、元数据过滤以及命名空间功能。其延迟极低（p95 值低于 100 毫秒），非常适合用于大规模的 RAG 应用、推荐系统或语义搜索场景，尤其适合无服务器及托管基础设施环境。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/mlops/pinecone` 命令安装 |
| 路径 | `optional-skills/mlops/pinecone` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可协议 | MIT |
| 依赖项 | `pinecone-client` |
| 支持平台 | linux、macos、windows |
| 标签 | `RAG`、`Pinecone`、`向量数据库`、`托管服务`、`无服务器`、`混合搜索`、`生产环境`、`自动扩展`、`低延迟`、`推荐系统` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。当技能处于激活状态时，智能体将依据此内容执行相应操作。
:::

# Pinecone —— 托管向量数据库

专为生产级 AI 应用打造的向量数据库。

## 何时选择 Pinecone

**适用场景：**
- 需要托管式的无服务器向量数据库
- 开发生产级 RAG 应用
- 需要自动扩展功能
- 对低延迟有严格要求（低于 100 毫秒）
- 不希望自行管理基础设施
- 需要支持混合搜索（密集向量与稀疏向量）

**核心优势：**
- 完全托管的 SaaS 模式
- 可支持数十亿级向量数据的自动扩展
- **p95 延迟低于 100 毫秒**
- 提供 99.9% 的正常运行时间服务等级协议

**可选替代方案：**
- **Chroma**：开源自托管版本
- **FAISS**：离线型纯相似度搜索工具
- **Weaviate**：功能更丰富的自托管解决方案

## 快速入门

### 安装方式

```bash
pip install pinecone-client
```

### 基本用法

```python
from pinecone import Pinecone, ServerlessSpec

# Initialize
pc = Pinecone(api_key="your-api-key")

# Create index
pc.create_index(
    name="my-index",
    dimension=1536,  # Must match embedding dimension
    metric="cosine",  # or "euclidean", "dotproduct"
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

# Connect to index
index = pc.Index("my-index")

# Upsert vectors
index.upsert(vectors=[
    {"id": "vec1", "values": [0.1, 0.2, ...], "metadata": {"category": "A"}},
    {"id": "vec2", "values": [0.3, 0.4, ...], "metadata": {"category": "B"}}
])

# Query
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    include_metadata=True
)

print(results["matches"])
```

## 核心操作

### 创建索引

```python
# Serverless (recommended)
pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",         # or "gcp", "azure"
        region="us-east-1"
    )
)

# Pod-based (for consistent performance)
from pinecone import PodSpec

pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=PodSpec(
        environment="us-east1-gcp",
        pod_type="p1.x1"
    )
)
```

### 向量插入/更新操作

```python
# Single upsert
index.upsert(vectors=[
    {
        "id": "doc1",
        "values": [0.1, 0.2, ...],  # 1536 dimensions
        "metadata": {
            "text": "Document content",
            "category": "tutorial",
            "timestamp": "2025-01-01"
        }
    }
])

# Batch upsert (recommended)
vectors = [
    {"id": f"vec{i}", "values": embedding, "metadata": metadata}
    for i, (embedding, metadata) in enumerate(zip(embeddings, metadatas))
]

index.upsert(vectors=vectors, batch_size=100)
```

### 查询向量

```python
# Basic query
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=10,
    include_metadata=True,
    include_values=False
)

# With metadata filtering
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    filter={"category": {"$eq": "tutorial"}}
)

# Namespace query
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    namespace="production"
)

# Access results
for match in results["matches"]:
    print(f"ID: {match['id']}")
    print(f"Score: {match['score']}")
    print(f"Metadata: {match['metadata']}")
```

### 元数据过滤

```python
# Exact match
filter = {"category": "tutorial"}

# Comparison
filter = {"price": {"$gte": 100}}  # $gt, $gte, $lt, $lte, $ne

# Logical operators
filter = {
    "$and": [
        {"category": "tutorial"},
        {"difficulty": {"$lte": 3}}
    ]
}  # Also: $or

# In operator
filter = {"tags": {"$in": ["python", "ml"]}}
```

## 命名空间

```python
# Partition data by namespace
index.upsert(
    vectors=[{"id": "vec1", "values": [...]}],
    namespace="user-123"
)

# Query specific namespace
results = index.query(
    vector=[...],
    namespace="user-123",
    top_k=5
)

# List namespaces
stats = index.describe_index_stats()
print(stats['namespaces'])
```

## 混合搜索（密集型 + 稀疏型）

```python
# Upsert with sparse vectors
index.upsert(vectors=[
    {
        "id": "doc1",
        "values": [0.1, 0.2, ...],  # Dense vector
        "sparse_values": {
            "indices": [10, 45, 123],  # Token IDs
            "values": [0.5, 0.3, 0.8]   # TF-IDF scores
        },
        "metadata": {"text": "..."}
    }
])

# Hybrid query
results = index.query(
    vector=[0.1, 0.2, ...],
    sparse_vector={
        "indices": [10, 45],
        "values": [0.5, 0.3]
    },
    top_k=5,
    alpha=0.5  # 0=sparse, 1=dense, 0.5=hybrid
)
```

## 与LangChain的集成

```python
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

# Create vector store
vectorstore = PineconeVectorStore.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    index_name="my-index"
)

# Query
results = vectorstore.similarity_search("query", k=5)

# With metadata filter
results = vectorstore.similarity_search(
    "query",
    k=5,
    filter={"category": "tutorial"}
)

# As retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
```

## 与 LlamaIndex 的集成

```python
from llama_index.vector_stores.pinecone import PineconeVectorStore

# Connect to Pinecone
pc = Pinecone(api_key="your-key")
pinecone_index = pc.Index("my-index")

# Create vector store
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# Use in LlamaIndex
from llama_index.core import StorageContext, VectorStoreIndex

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
```

## 索引管理

```python
# List indices
indexes = pc.list_indexes()

# Describe index
index_info = pc.describe_index("my-index")
print(index_info)

# Get index stats
stats = index.describe_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Namespaces: {stats['namespaces']}")

# Delete index
pc.delete_index("my-index")
```

## 删除向量

```python
# Delete by ID
index.delete(ids=["vec1", "vec2"])

# Delete by filter
index.delete(filter={"category": "old"})

# Delete all in namespace
index.delete(delete_all=True, namespace="test")

# Delete entire index
index.delete(delete_all=True)
```

## 最佳实践

1. **使用无服务器架构**——具备自动扩展能力，更具成本效益  
2. **批量插入/更新数据**——效率更高（每批处理100-200条记录）  
3. **添加元数据**——便于后续数据筛选  
4. **使用命名空间**——按用户或租户隔离数据  
5. **监控使用情况**——查看Pinecone控制台面板  
6. **优化筛选条件**——对频繁被筛选的字段建立索引  
7. **利用免费套餐进行测试**——可创建1个索引，存储10万条向量  
8. **采用混合搜索方式**——提升搜索质量  
9. **设置合适的维度参数**——与嵌入模型相匹配  
10. **定期备份数据**——导出重要数据  

## 性能表现

| 操作类型 | 延迟时间 | 备注 |
|---------|---------|------|
| 插入/更新数据 | 约50-100毫秒 | 每批处理一次 |
| 查询（p50分位数） | 约50毫秒 | 取决于索引规模 |
| 查询（p95分位数） | 约100毫秒 | 符合服务等级协议目标 |
| 元数据筛选 | 约+10-20毫秒 | 额外的处理开销 |

## 定价方案（2025年最新标准）

**无服务器架构**：
- 每百万次读取操作费用：0.096美元  
- 每百万次写入操作费用：0.06美元  
- 每GB存储空间每月费用：0.06美元  

**免费套餐**：
- 提供1个无服务器索引  
- 可存储10万条向量（每个向量1536个维度）  
- 非常适合原型开发  

## 相关资源

- **官方网站**：https://www.pinecone.io  
- **文档中心**：https://docs.pinecone.io  
- **控制台界面**：https://app.pinecone.io  
- **定价详情**：https://www.pinecone.io/pricing
