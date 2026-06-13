# Qdrant 故障排查指南

## 安装问题

### Docker 相关问题

**错误信息**：`无法连接到 Docker 守护进程`

**解决方案**：
```bash
# Start Docker daemon
sudo systemctl start docker

# Or use Docker Desktop on Mac/Windows
open -a Docker
```

**错误提示**：`端口 6333 已被占用`

**解决方案**：
```bash
# Find process using port
lsof -i :6333

# Kill process or use different port
docker run -p 6334:6333 qdrant/qdrant
```

### Python 客户端相关问题

**错误提示**：`ModuleNotFoundError: No module named 'qdrant_client'`

**解决方案**：
```bash
pip install qdrant-client

# With specific version
pip install qdrant-client>=1.12.0
```

**错误提示**：`grpc._channel._InactiveRpcError`

**解决方案**：
```bash
# Install with gRPC support
pip install 'qdrant-client[grpc]'

# Or disable gRPC
client = QdrantClient(host="localhost", port=6333, prefer_grpc=False)
```

## 连接问题

### 无法连接到服务器

**错误信息**：`ConnectionRefusedError: [Errno 111] Connection refused`

**解决方案**：

1. **检查服务器是否正在运行**：
```bash
docker ps | grep qdrant
curl http://localhost:6333/healthz
```

2. **验证端口绑定情况**：
```bash
# Check listening ports
netstat -tlnp | grep 6333

# Docker port mapping
docker port <container_id>
```

3. **使用正确的主机**：
```python
# Docker on Linux
client = QdrantClient(host="localhost", port=6333)

# Docker on Mac/Windows with networking issues
client = QdrantClient(host="127.0.0.1", port=6333)

# Inside Docker network
client = QdrantClient(host="qdrant", port=6333)
```

### 超时错误

**错误信息**：`TimeoutError: 连接超时`

**解决方案**：
```python
# Increase timeout
client = QdrantClient(
    host="localhost",
    port=6333,
    timeout=60  # seconds
)

# For large operations
client.upsert(
    collection_name="documents",
    points=large_batch,
    wait=False  # Don't wait for indexing
)
```

### SSL/TLS 错误

**错误代码**：`ssl.SSLCertVerificationError`

**解决方案**：
```python
# Qdrant Cloud
client = QdrantClient(
    url="https://cluster.cloud.qdrant.io",
    api_key="your-api-key"
)

# Self-signed certificate
client = QdrantClient(
    host="localhost",
    port=6333,
    https=True,
    verify=False  # Disable verification (not recommended for production)
)
```

## 收集问题

### 收集项已存在

**错误信息**：`ValueError: 收集项 ‘documents’ 已存在`

**解决方案**：
```python
# Check before creating
collections = client.get_collections().collections
names = [c.name for c in collections]

if "documents" not in names:
    client.create_collection(...)

# Or recreate
client.recreate_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
```

### 未找到集合

**错误信息**：`NotFoundException: 未找到名为 ‘docs’ 的集合`

**解决方案**：
```python
# List available collections
collections = client.get_collections()
print([c.name for c in collections.collections])

# Check exact name (case-sensitive)
try:
    info = client.get_collection("documents")
except Exception as e:
    print(f"Collection not found: {e}")
```

### 向量维度不匹配

**错误信息**：`ValueError: 向量维度不匹配。期望维度为384，实际获取的维度为768`

**解决方案**：
```python
# Check collection config
info = client.get_collection("documents")
print(f"Expected dimension: {info.config.params.vectors.size}")

# Recreate with correct dimension
client.recreate_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)  # Match your embeddings
)
```

## 搜索问题

### 没有搜索到结果

**问题**：执行搜索后未返回任何结果。

**解决方案**：

1. **确认数据存在**：
```python
info = client.get_collection("documents")
print(f"Points: {info.points_count}")

# Scroll to check data
points, _ = client.scroll(
    collection_name="documents",
    limit=10,
    with_payload=True
)
print(points)
```

2. **检查向量格式**：
```python
# Must be list of floats
query_vector = embedding.tolist()  # Convert numpy to list

# Check dimensions
print(f"Query dimension: {len(query_vector)}")
```

3. **验证过滤条件**：
```python
# Test without filter first
results = client.search(
    collection_name="documents",
    query_vector=query,
    limit=10
    # No filter
)

# Then add filter incrementally
```

### 搜索性能缓慢

**问题**：搜索耗时过长。

**解决方案**：

1. **创建有效负载索引**：
```python
# Index fields used in filters
client.create_payload_index(
    collection_name="documents",
    field_name="category",
    field_schema="keyword"
)
```

2. **启用量化功能**：
```python
client.update_collection(
    collection_name="documents",
    quantization_config=ScalarQuantization(
        scalar=ScalarQuantizationConfig(type=ScalarType.INT8)
    )
)
```

3. **调整 HNSW 参数**：
```python
# Faster search (less accurate)
client.update_collection(
    collection_name="documents",
    hnsw_config=HnswConfigDiff(ef_construct=64, m=8)
)

# Use ef search parameter
results = client.search(
    collection_name="documents",
    query_vector=query,
    search_params={"hnsw_ef": 64},  # Lower = faster
    limit=10
)
```

4. **使用 gRPC**：
```python
client = QdrantClient(
    host="localhost",
    port=6333,
    grpc_port=6334,
    prefer_grpc=True
)
```

### 结果不一致问题

**问题**：相同的查询会返回不同的结果。

**解决方案**：

1. **等待索引构建完成**：
```python
client.upsert(
    collection_name="documents",
    points=points,
    wait=True  # Wait for index update
)
```

2. **检查复制一致性**：
```python
# Strong consistency read
results = client.search(
    collection_name="documents",
    query_vector=query,
    consistency="all"  # Read from all replicas
)
```

## 插入或更新问题处理

### 批量插入或更新失败

**错误信息**：`PayloadError: Payload too large`

**解决方案**：
```python
# Split into smaller batches
def batch_upsert(client, collection, points, batch_size=100):
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=collection,
            points=batch,
            wait=True
        )

batch_upsert(client, "documents", large_points_list)
```

### 无效的点ID

**错误信息**：`ValueError: Invalid point ID`

**解决方案**：
```python
# Valid ID types: int or UUID string
from uuid import uuid4

# Integer ID
PointStruct(id=123, vector=vec, payload={})

# UUID string
PointStruct(id=str(uuid4()), vector=vec, payload={})

# NOT valid
PointStruct(id="custom-string-123", ...)  # Use UUID format
```

### 载荷验证错误

**错误信息**：`ValidationError: 无效的载荷`

**解决方案**：
```python
# Ensure JSON-serializable payload
import json

payload = {
    "title": "Document",
    "count": 42,
    "tags": ["a", "b"],
    "nested": {"key": "value"}
}

# Validate before upsert
json.dumps(payload)  # Should not raise

# Avoid non-serializable types
# NOT valid: datetime, numpy arrays, custom objects
payload = {
    "timestamp": datetime.now().isoformat(),  # Convert to string
    "vector": embedding.tolist()  # Convert numpy to list
}
```

## 内存问题

### 内存不足

**错误表现**：出现 `MemoryError` 错误或容器被终止

**解决方案**：

1. **启用磁盘存储**：
```python
client.create_collection(
    collection_name="large_collection",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    on_disk_payload=True,  # Store payloads on disk
    hnsw_config=HnswConfigDiff(on_disk=True)  # Store HNSW on disk
)
```

2. **使用量化功能**：
```python
# 4x memory reduction
client.update_collection(
    collection_name="large_collection",
    quantization_config=ScalarQuantization(
        scalar=ScalarQuantizationConfig(
            type=ScalarType.INT8,
            always_ram=False  # Keep on disk
        )
    )
)
```

3. **增加 Docker 内存**：
```bash
docker run -m 8g -p 6333:6333 qdrant/qdrant
```

4. **配置 Qdrant 存储**：
```yaml
# config.yaml
storage:
  performance:
    max_search_threads: 2
  optimizers:
    memmap_threshold_kb: 20000
```

### 索引构建期间内存占用过高

**解决方案**：
```python
# Increase indexing threshold for bulk loads
client.update_collection(
    collection_name="documents",
    optimizer_config={
        "indexing_threshold": 50000  # Delay indexing
    }
)

# Bulk insert
client.upsert(collection_name="documents", points=all_points, wait=False)

# Then optimize
client.update_collection(
    collection_name="documents",
    optimizer_config={
        "indexing_threshold": 10000  # Resume normal indexing
    }
)
```

## 集群问题

### 节点无法加入集群

**问题**：新节点无法加入集群。

**解决方案**：
```bash
# Check network connectivity
docker exec qdrant-node-2 ping qdrant-node-1

# Verify bootstrap URL
docker logs qdrant-node-2 | grep bootstrap

# Check Raft state
curl http://localhost:6333/cluster
```

### 分脑问题

**问题**：集群状态不一致。

**解决方案**：
```bash
# Force leader election
curl -X POST http://localhost:6333/cluster/recover

# Or restart minority nodes
docker restart qdrant-node-2 qdrant-node-3
```

### 复制延迟

**问题**：副本节点落后于主节点。

**解决方案**：
```python
# Check collection status
info = client.get_collection("documents")
print(f"Status: {info.status}")

# Use strong consistency for critical writes
client.upsert(
    collection_name="documents",
    points=points,
    ordering=WriteOrdering.STRONG
)
```

## 性能调优

### 基准测试配置

```python
import time
import numpy as np

def benchmark_search(client, collection, n_queries=100, dimension=384):
    # Generate random queries
    queries = [np.random.rand(dimension).tolist() for _ in range(n_queries)]

    # Warmup
    for q in queries[:10]:
        client.search(collection_name=collection, query_vector=q, limit=10)

    # Benchmark
    start = time.perf_counter()
    for q in queries:
        client.search(collection_name=collection, query_vector=q, limit=10)
    elapsed = time.perf_counter() - start

    print(f"QPS: {n_queries / elapsed:.2f}")
    print(f"Latency: {elapsed / n_queries * 1000:.2f}ms")

benchmark_search(client, "documents")
```

### 最佳 HNSW 参数配置

```python
# High recall (slower)
client.create_collection(
    collection_name="high_recall",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    hnsw_config=HnswConfigDiff(
        m=32,              # More connections
        ef_construct=200   # Higher build quality
    )
)

# High speed (lower recall)
client.create_collection(
    collection_name="high_speed",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    hnsw_config=HnswConfigDiff(
        m=8,               # Fewer connections
        ef_construct=64    # Lower build quality
    )
)

# Balanced
client.create_collection(
    collection_name="balanced",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    hnsw_config=HnswConfigDiff(
        m=16,              # Default
        ef_construct=100   # Default
    )
)
```

## 调试技巧

### 启用详细日志记录

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("qdrant_client").setLevel(logging.DEBUG)
```

### 查看服务器日志

```bash
# Docker logs
docker logs -f qdrant

# With timestamps
docker logs --timestamps qdrant

# Last 100 lines
docker logs --tail 100 qdrant
```

### 检查集合状态

```python
# Collection info
info = client.get_collection("documents")
print(f"Status: {info.status}")
print(f"Points: {info.points_count}")
print(f"Segments: {len(info.segments)}")
print(f"Config: {info.config}")

# Sample points
points, _ = client.scroll(
    collection_name="documents",
    limit=5,
    with_payload=True,
    with_vectors=True
)
for p in points:
    print(f"ID: {p.id}, Payload: {p.payload}")
```

### 测试连接

```python
def test_connection(host="localhost", port=6333):
    try:
        client = QdrantClient(host=host, port=port, timeout=5)
        collections = client.get_collections()
        print(f"Connected! Collections: {len(collections.collections)}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

test_connection()
```

## 获取帮助

1. **文档**：https://qdrant.tech/documentation/
2. **GitHub 问题报告**：https://github.com/qdrant/qdrant/issues
3. **Discord 社区**：https://discord.gg/qdrant
4. **Stack Overflow**：请添加 `qdrant` 标签

### 报告问题时请提供以下信息

- Qdrant 版本：`curl http://localhost:6333/`
- Python 客户端版本：`pip show qdrant-client`
- 完整的错误堆栈信息
- 最简可复现代码示例
- 集合配置信息
