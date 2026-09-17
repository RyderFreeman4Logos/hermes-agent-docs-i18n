---
title: "Chroma — Embedding database for RAG and semantic search"
sidebar_label: "Chroma"
description: "Embedding database for RAG and semantic search"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Chroma

用于 RAG 及语义搜索的嵌入数据库。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/mlops/chroma` 安装 |
| 路径 | `optional-skills/mlops\chroma` |
| 版本 | `1.0.0` |
| 开发者 | Orchestra Research |
| 许可证 | MIT |
| 依赖项 | `chromadb`, `sentence-transformers` |
| 支持平台 | linux、macos、windows |
| 标签 | `RAG`、`Chroma`、`向量数据库`、`嵌入向量`、`语义搜索`、`开源`、`自托管`、`文档检索`、`元数据过滤` |

## 参考：完整的 SKILL.md 文件

:::info
以下是 Hermes 在触发该技能时加载的完整技能定义。当技能处于激活状态时，智能体看到的指令即为此内容。
:::

# Chroma —— 开源嵌入数据库

专为构建具备记忆功能的 LLM 应用而设计的原生 AI 数据库。

## 何时使用 Chroma

**以下情况建议使用 Chroma：**
- 构建 RAG（检索增强生成）应用
- 需要本地/自托管的向量数据库
- 寻求开源解决方案（Apache 2.0 许可）
- 在笔记本中进行原型开发
| 对文档进行语义搜索 |
| 同时存储嵌入向量和元数据 |

**相关数据：**
- **GitHub 星标数超过 24,300 个**
- **代码仓库分叉数超过 1,900 个**
- **当前版本为 v1.3.3**（稳定版，每周发布新版本）
- **采用 Apache 2.0 许可证**

**如需替代方案，可选择：**
- **Pinecone**：托管式云服务，具备自动扩展功能  
- **FAISS**：纯相似度搜索引擎，不支持元数据处理  
- **Weaviate**：专为生产环境设计的原生机器学习数据库  
- **Qdrant**：基于Rust语言开发的高性能搜索引擎  

## 快速入门

### 安装

```bash
# Python
pip install chromadb

# JavaScript/TypeScript
npm install chromadb @chroma-core/default-embed
```

### 基本用法（Python）

```python
import chromadb

# Create client
client = chromadb.Client()

# Create collection
collection = client.create_collection(name="my_collection")

# Add documents
collection.add(
    documents=["This is document 1", "This is document 2"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# Query
results = collection.query(
    query_texts=["document about topic"],
    n_results=2
)

print(results)
```

## 核心操作

### 1. 创建集合

```python
# Simple collection
collection = client.create_collection("my_docs")

# With custom embedding function
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="my_docs",
    embedding_function=openai_ef
)

# Get existing collection
collection = client.get_collection("my_docs")

# Delete collection
client.delete_collection("my_docs")
```

### 2. 添加文档

```python
# Add with auto-generated IDs
collection.add(
    documents=["Doc 1", "Doc 2", "Doc 3"],
    metadatas=[
        {"source": "web", "category": "tutorial"},
        {"source": "pdf", "page": 5},
        {"source": "api", "timestamp": "2025-01-01"}
    ],
    ids=["id1", "id2", "id3"]
)

# Add with custom embeddings
collection.add(
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    documents=["Doc 1", "Doc 2"],
    ids=["id1", "id2"]
)
```

### 3. 查询（相似度搜索）

```python
# Basic query
results = collection.query(
    query_texts=["machine learning tutorial"],
    n_results=5
)

# Query with filters
results = collection.query(
    query_texts=["Python programming"],
    n_results=3,
    where={"source": "web"}
)

# Query with metadata filters
results = collection.query(
    query_texts=["advanced topics"],
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$gte": 3}}
        ]
    }
)

# Access results
print(results["documents"])      # List of matching documents
print(results["metadatas"])      # Metadata for each doc
print(results["distances"])      # Similarity scores
print(results["ids"])            # Document IDs
```

### 4. 获取文档

```python
# Get by IDs
docs = collection.get(
    ids=["id1", "id2"]
)

# Get with filters
docs = collection.get(
    where={"category": "tutorial"},
    limit=10
)

# Get all documents
docs = collection.get()
```

### 5. 更新文档

```python
# Update document content
collection.update(
    ids=["id1"],
    documents=["Updated content"],
    metadatas=[{"source": "updated"}]
)
```

### 6. 删除文档

```python
# Delete by IDs
collection.delete(ids=["id1", "id2"])

# Delete with filter
collection.delete(
    where={"source": "outdated"}
)
```

## 持久化存储

```python
# Persist to disk
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.create_collection("my_docs")
collection.add(documents=["Doc 1"], ids=["id1"])

# Data persisted automatically
# Reload later with same path
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_docs")
```

## 嵌入功能

### 默认选项（Sentence Transformers）

```python
# Uses sentence-transformers by default
collection = client.create_collection("my_docs")
# Default model: all-MiniLM-L6-v2
```

### OpenAI

```python
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="openai_docs",
    embedding_function=openai_ef
)
```

### HuggingFace

```python
huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
    api_key="your-key",
    model_name="sentence-transformers/all-mpnet-base-v2"
)

collection = client.create_collection(
    name="hf_docs",
    embedding_function=huggingface_ef
)
```

### 自定义嵌入函数

```python
from chromadb import Documents, EmbeddingFunction, Embeddings

class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # Your embedding logic
        return embeddings

my_ef = MyEmbeddingFunction()
collection = client.create_collection(
    name="custom_docs",
    embedding_function=my_ef
)
```

## 元数据过滤

```python
# Exact match
results = collection.query(
    query_texts=["query"],
    where={"category": "tutorial"}
)

# Comparison operators
results = collection.query(
    query_texts=["query"],
    where={"page": {"$gt": 10}}  # $gt, $gte, $lt, $lte, $ne
)

# Logical operators
results = collection.query(
    query_texts=["query"],
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$lte": 3}}
        ]
    }  # Also: $or
)

# Contains
results = collection.query(
    query_texts=["query"],
    where={"tags": {"$in": ["python", "ml"]}}
)
```

## 与 LangChain 的集成

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(documents)

# Create Chroma vector store
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)

# Query
results = vectorstore.similarity_search("machine learning", k=3)

# As retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

## 与 LlamaIndex 的集成

```python
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
import chromadb

# Initialize Chroma
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("my_collection")

# Create vector store
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Create index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context
)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("What is machine learning?")
```

## 服务器模式

```python
# Run Chroma server
# Terminal: chroma run --path ./chroma_db --port 8000

# Connect to server
import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host="localhost",
    port=8000,
    settings=Settings(anonymized_telemetry=False)
)

# Use as normal
collection = client.get_or_create_collection("my_docs")
```

## 最佳实践

1. **使用持久化客户端**——避免重启后数据丢失  
2. **添加元数据**——便于筛选与追踪  
3. **批量操作**——一次性添加多个文档  
4. **选择合适的嵌入模型**——在速度与质量间取得平衡  
5. **运用过滤器**——缩小搜索范围  
6. **使用唯一标识符**——防止数据冲突  
7. **定期备份**——复制chroma_db目录  
8. **监控集合规模**——必要时进行扩展  
9. **测试嵌入功能**——确保输出质量  
10. **生产环境采用服务器模式**——更适用于多用户场景  

## 性能表现

| 操作 | 延迟时间 | 备注 |
|------|----------|------|
| 添加100个文档 | 约1-3秒 | 已启用嵌入功能 |
| 查询（前10条结果） | 约50-200毫秒 | 取决于集合规模 |
| 元数据筛选 | 约10-50毫秒 | 通过合理索引可显著提升速度 |

## 资源链接

- **GitHub仓库**：https://github.com/chroma-core/chroma ⭐ 24,300+星标  
- **文档中心**：https://docs.trychroma.com  
- **Discord社区**：https://discord.gg/MMeYNTmh3x  
- **当前版本**：1.3.3+  
- **许可证**：Apache 2.0
