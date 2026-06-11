# Pinecone 部署指南

Pinecone 的生产环境部署模式。

## 无服务器架构与容器化架构对比

### 无服务器架构（推荐）

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="your-key")

# Create serverless index
pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",  # or "gcp", "azure"
        region="us-east-1"
    )
)
```

**优势：**  
- 自动扩展  
- 按使用量付费  
- 无需管理基础设施  
- 非固定负载场景下更具成本效益  

**适用场景：**  
- 流量波动较大  
- 需要优化成本  
- 不要求稳定的延迟性能  

### 基于 Pod 的架构

```python
from pinecone import PodSpec

pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=PodSpec(
        environment="us-east1-gcp",
        pod_type="p1.x1",  # or p1.x2, p1.x4, p1.x8
        pods=2,  # Number of pods
        replicas=2  # High availability
    )
)
```

**优势：**  
- 稳定的性能表现  
- 可预测的延迟  
- 更高的吞吐量  
- 专用的资源分配  

**适用场景：**  
- 生产环境任务  
- 需要稳定的 p95 延迟指标  
- 对高吞吐量有要求的应用  

## 混合搜索  

### 密集向量与稀疏向量

```python
# Upsert with both dense and sparse vectors
index.upsert(vectors=[
    {
        "id": "doc1",
        "values": [0.1, 0.2, ...],  # Dense (semantic)
        "sparse_values": {
            "indices": [10, 45, 123],  # Token IDs
            "values": [0.5, 0.3, 0.8]   # TF-IDF/BM25 scores
        },
        "metadata": {"text": "..."}
    }
])

# Hybrid query
results = index.query(
    vector=[0.1, 0.2, ...],  # Dense query
    sparse_vector={
        "indices": [10, 45],
        "values": [0.5, 0.3]
    },
    top_k=10,
    alpha=0.5  # 0=sparse only, 1=dense only, 0.5=balanced
)
```

**优势：**  
- 融合两者之长  
- 支持语义匹配与关键词匹配  
- 检索准确率优于单一匹配方式  

## 多租户专用命名空间

```python
# Separate data by user/tenant
index.upsert(
    vectors=[{"id": "doc1", "values": [...]}],
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

**应用场景：**
- 多租户 SaaS 平台
- 实现针对不同用户的数据隔离
- A/B 测试（生产环境/测试环境命名空间）

## 元数据过滤

### 精确匹配

```python
results = index.query(
    vector=[...],
    filter={"category": "tutorial"},
    top_k=5
)
```

### 范围查询

```python
results = index.query(
    vector=[...],
    filter={"price": {"$gte": 100, "$lte": 500}},
    top_k=5
)
```

### 复杂过滤器

```python
results = index.query(
    vector=[...],
    filter={
        "$and": [
            {"category": {"$in": ["tutorial", "guide"]}},
            {"difficulty": {"$lte": 3}},
            {"published": {"$gte": "2024-01-01"}}
        ]
    },
    top_k=5
)
```

## 最佳实践

1. **开发阶段使用无服务器架构**——更具成本效益  
2. **生产环境改用容器化部署**——确保性能稳定  
3. **启用命名空间功能**——实现多租户管理  
4. **合理添加元数据**——便于后续筛选操作  
5. **采用混合搜索方式**——提升查询质量  
6. **批量插入/更新数据**——每批处理100至200个向量  
7. **监控使用情况**——查看Pinecone控制面板  
8. **设置警报机制**——设定使用量或成本阈值  
9. **定期备份数据**——导出重要信息  
10. **测试筛选功能**——验证其性能表现  

## 资源链接

- **文档**：https://docs.pinecone.io  
- **控制台**：https://app.pinecone.io
