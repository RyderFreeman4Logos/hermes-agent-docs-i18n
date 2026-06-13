---
name: qdrant-vector-search
description: High-performance vector similarity search engine for RAG and semantic search. Use when building production RAG systems requiring fast nearest neighbor search, hybrid search with filtering, or scalable vector storage with Rust-powered performance.
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [qdrant-client>=1.12.0]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [RAG, Vector Search, Qdrant, Semantic Search, Embeddings, Similarity Search, HNSW, Production, Distributed]

---

# Qdrant - 向量相似度搜索引擎

一款基于 Rust 开发的高性能向量数据库，专为生产环境中的 RAG 与语义搜索而设计。

## 何时选择 Qdrant

**以下场景适合使用 Qdrant：**
- 构建对低延迟有要求的实际 RAG 系统
- 需要混合搜索方式（向量查询 + 元数据过滤）
- 需要通过分片/复制实现水平扩展
- 希望在本地部署以获得完全的数据控制权
- 每条记录需要存储多种向量格式（密集向量 + 稀疏向量）
- 构建实时推荐系统

**核心特性：**
- **基于 Rust 开发**：内存安全，性能卓越
- **强大的过滤功能**：可在搜索过程中根据任意字段进行过滤
- **多向量支持**：每个数据点可存储密集向量、稀疏向量及多种密集向量格式
- **量化技术**：提供标量量化、乘积量化及二进制量化，提升内存效率
- **分布式架构**：支持 Raft 共识机制、分片与复制功能
- **REST + gRPC 接口**：两种 API 功能完全对等

**如需其他替代方案，请考虑：**
- **Chroma**：部署更简单，适用于嵌入式场景
- **FAISS**：原始处理速度最快，适合研究及批量处理任务
- **Pinecone**：全托管服务，适合无需自行运维的用户
- **Weaviate**：优先推荐使用 GraphQL 接口，内置向量化工具

## 快速入门

### 安装

```bash
# Python client
pip install qdrant-client

# Docker (recommended for development)
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Docker with persistent storage
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### 基本用法

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Insert vectors with payload
client.upsert(
    collection_name="documents",
    points=[
        PointStruct(
            id=1,
            vector=[0.1, 0.2, ...],  # 384-dim vector
            payload={"title": "Doc 1", "category": "tech"}
        ),
        PointStruct(
            id=2,
            vector=[0.3, 0.4, ...],
            payload={"title": "Doc 2", "category": "science"}
        )
    ]
)

# Search with filtering
results = client.search(
    collection_name="documents",
    query_vector=[0.15, 0.25, ...],
    query_filter={
        "must": [{"key": "category", "match": {"value": "tech"}}]
    },
    limit=10
)

for point in results:
    print(f"ID: {point.id}, Score: {point.score}, Payload: {point.payload}")
```

## 核心概念

### 积分——基本数据单位

```python
from qdrant_client.models import PointStruct

# Point = ID + Vector(s) + Payload
point = PointStruct(
    id=123,                              # Integer or UUID string
    vector=[0.1, 0.2, 0.3, ...],        # Dense vector
    payload={                            # Arbitrary JSON metadata
        "title": "Document title",
        "category": "tech",
        "timestamp": 1699900000,
        "tags": ["python", "ml"]
    }
)

# Batch upsert (recommended)
client.upsert(
    collection_name="documents",
    points=[point1, point2, point3],
    wait=True  # Wait for indexing
)
```

### 集合——向量容器

```python
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff

# Create with HNSW configuration
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=384,                        # Vector dimensions
        distance=Distance.COSINE         # COSINE, EUCLID, DOT, MANHATTAN
    ),
    hnsw_config=HnswConfigDiff(
        m=16,                            # Connections per node (default 16)
        ef_construct=100,                # Build-time accuracy (default 100)
        full_scan_threshold=10000        # Switch to brute force below this
    ),
    on_disk_payload=True                 # Store payload on disk
)

# Collection info
info = client.get_collection("documents")
print(f"Points: {info.points_count}, Vectors: {info.vectors_count}")
```

### 距离度量标准

| 度量标准 | 使用场景 | 取值范围 |
|--------|----------|-------|
| `COSINE` | 文本嵌入、标准化向量 | 0 到 2 |
| `EUCLID` | 空间数据、图像特征 | 0 到 ∞ |
| `DOT` | 推荐系统、未标准化数据 | -∞ 到 ∞ |
| `MANHATTAN` | 稀疏特征、离散数据 | 0 到 ∞ |

## 搜索操作

### 基本搜索

```python
# Simple nearest neighbor search
results = client.search(
    collection_name="documents",
    query_vector=[0.1, 0.2, ...],
    limit=10,
    with_payload=True,
    with_vectors=False  # Don't return vectors (faster)
)
```

### 筛选搜索

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

# Complex filtering
results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(key="category", match=MatchValue(value="tech")),
            FieldCondition(key="timestamp", range=Range(gte=1699000000))
        ],
        must_not=[
            FieldCondition(key="status", match=MatchValue(value="archived"))
        ]
    ),
    limit=10
)

# Shorthand filter syntax
results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    query_filter={
        "must": [
            {"key": "category", "match": {"value": "tech"}},
            {"key": "price", "range": {"gte": 10, "lte": 100}}
        ]
    },
    limit=10
)
```

### 批量搜索

```python
from qdrant_client.models import SearchRequest

# Multiple queries in one request
results = client.search_batch(
    collection_name="documents",
    requests=[
        SearchRequest(vector=[0.1, ...], limit=5),
        SearchRequest(vector=[0.2, ...], limit=5, filter={"must": [...]}),
        SearchRequest(vector=[0.3, ...], limit=10)
    ]
)
```

## RAG集成

### 使用sentence-transformers实现

```python
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# Initialize
encoder = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="knowledge_base",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Index documents
documents = [
    {"id": 1, "text": "Python is a programming language", "source": "wiki"},
    {"id": 2, "text": "Machine learning uses algorithms", "source": "textbook"},
]

points = [
    PointStruct(
        id=doc["id"],
        vector=encoder.encode(doc["text"]).tolist(),
        payload={"text": doc["text"], "source": doc["source"]}
    )
    for doc in documents
]
client.upsert(collection_name="knowledge_base", points=points)

# RAG retrieval
def retrieve(query: str, top_k: int = 5) -> list[dict]:
    query_vector = encoder.encode(query).tolist()
    results = client.search(
        collection_name="knowledge_base",
        query_vector=query_vector,
        limit=top_k
    )
    return [{"text": r.payload["text"], "score": r.score} for r in results]

# Use in RAG pipeline
context = retrieve("What is Python?")
prompt = f"Context: {context}\n\nQuestion: What is Python?"
```

### 集成 LangChain 使用

```python
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Qdrant.from_documents(documents, embeddings, url="http://localhost:6333", collection_name="docs")
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

### 集成 LlamaIndex 使用

```python
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

vector_store = QdrantVectorStore(client=client, collection_name="llama_docs")
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
query_engine = index.as_query_engine()
```

## 多向量支持

### 命名向量（不同的嵌入模型）

```python
from qdrant_client.models import VectorParams, Distance

# Collection with multiple vector types
client.create_collection(
    collection_name="hybrid_search",
    vectors_config={
        "dense": VectorParams(size=384, distance=Distance.COSINE),
        "sparse": VectorParams(size=30000, distance=Distance.DOT)
    }
)

# Insert with named vectors
client.upsert(
    collection_name="hybrid_search",
    points=[
        PointStruct(
            id=1,
            vector={
                "dense": dense_embedding,
                "sparse": sparse_embedding
            },
            payload={"text": "document text"}
        )
    ]
)

# Search specific vector
results = client.search(
    collection_name="hybrid_search",
    query_vector=("dense", query_dense),  # Specify which vector
    limit=10
)
```

### 稀疏向量（BM25、SPLADE）

```python
from qdrant_client.models import SparseVectorParams, SparseIndexParams, SparseVector

# Collection with sparse vectors
client.create_collection(
    collection_name="sparse_search",
    vectors_config={},
    sparse_vectors_config={"text": SparseVectorParams(index=SparseIndexParams(on_disk=False))}
)

# Insert sparse vector
client.upsert(
    collection_name="sparse_search",
    points=[PointStruct(id=1, vector={"text": SparseVector(indices=[1, 5, 100], values=[0.5, 0.8, 0.2])}, payload={"text": "document"})]
)
```

## 量化（内存优化）

```python
from qdrant_client.models import ScalarQuantization, ScalarQuantizationConfig, ScalarType

# Scalar quantization (4x memory reduction)
client.create_collection(
    collection_name="quantized",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    quantization_config=ScalarQuantization(
        scalar=ScalarQuantizationConfig(
            type=ScalarType.INT8,
            quantile=0.99,        # Clip outliers
            always_ram=True      # Keep quantized in RAM
        )
    )
)

# Search with rescoring
results = client.search(
    collection_name="quantized",
    query_vector=query,
    search_params={"quantization": {"rescore": True}},  # Rescore top results
    limit=10
)
```

## 载荷索引功能

```python
from qdrant_client.models import PayloadSchemaType

# Create payload index for faster filtering
client.create_payload_index(
    collection_name="documents",
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD
)

client.create_payload_index(
    collection_name="documents",
    field_name="timestamp",
    field_schema=PayloadSchemaType.INTEGER
)

# Index types: KEYWORD, INTEGER, FLOAT, GEO, TEXT (full-text), BOOL
```

## 生产环境部署

### Qdrant Cloud

```python
from qdrant_client import QdrantClient

# Connect to Qdrant Cloud
client = QdrantClient(
    url="https://your-cluster.cloud.qdrant.io",
    api_key="your-api-key"
)
```

### 性能调优

```python
# Optimize for search speed (higher recall)
client.update_collection(
    collection_name="documents",
    hnsw_config=HnswConfigDiff(ef_construct=200, m=32)
)

# Optimize for indexing speed (bulk loads)
client.update_collection(
    collection_name="documents",
    optimizer_config={"indexing_threshold": 20000}
)
```

## 最佳实践

1. **批量操作**——使用批量插入/查询以提高效率  
2. **负载索引**——对过滤条件中用到的字段进行索引  
3. **量化处理**——对于包含超过100万个向量的大型集合，建议启用该功能  
4. **分片**——当集合中的向量数量超过1000万时，应采用分片机制  
5. **磁盘存储**——对于较大的负载数据，建议启用`on_disk_payload`选项  
6. **连接池**——重复使用客户端实例  

## 常见问题

**带过滤条件的查询速度缓慢：**
```python
# Create payload index for filtered fields
client.create_payload_index(
    collection_name="docs",
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD
)
```

**内存不足：**
```python
# Enable quantization and on-disk storage
client.create_collection(
    collection_name="large_collection",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    quantization_config=ScalarQuantization(...),
    on_disk_payload=True
)
```

**连接问题：**
```python
# Use timeout and retry
client = QdrantClient(
    host="localhost",
    port=6333,
    timeout=30,
    prefer_grpc=True  # gRPC for better performance
)
```

## 参考资料

- **[高级用法](references/advanced-usage.md)** - 分布式模式、混合搜索、推荐功能
- **[故障排除](references/troubleshooting.md)** - 常见问题、调试方法、性能优化

## 资源链接

- **GitHub仓库**：https://github.com/qdrant/qdrant（拥有22,000多个星标）
- **官方文档**：https://qdrant.tech/documentation/
- **Python客户端**：https://github.com/qdrant/qdrant-client
- **云服务平台**：https://cloud.qdrant.io
- **当前版本**：1.12.0及以上
- **许可证**：Apache 2.0
