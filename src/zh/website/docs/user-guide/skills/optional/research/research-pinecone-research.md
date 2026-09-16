---
title: "Pinecone Research — Agent RAG and long-term memory with Pinecone"
sidebar_label: "Pinecone Research"
description: "Agent RAG and long-term memory with Pinecone"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能的 SKILL.md 自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Pinecone Research

基于 Pinecone 的智能体 RAG 及长期记忆功能。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/research/pinecone-research` 安装 |
| 路径 | `optional-skills/research\pinecone-research` |
| 版本 | `1.0.0` |
| 创建者 | immuhammadfurqan |
| 许可证 | MIT |
| 依赖项 | `pinecone-client`, `langchain-pinecone` |
| 支持平台 | linux、macos、windows |
| 标签 | `RAG`、`Pinecone`、`Memory`、`Research`、`向量数据库`、`Agent`、`检索` |

## 参考：完整的 SKILL.md

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当技能处于激活状态时，智能体将看到这些内容作为指令。
:::

# Pinecone Research — 智能体 RAG 与长期记忆功能

将 Pinecone 用作智能体对话的检索增强生成（RAG）后端：持久化嵌入向量、从过往会话中检索相关上下文，并构建长期记忆。

## 何时使用此技能

**适用场景：**
- 使用 Pinecone 作为向量存储来构建智能体 RAG 流水线
- 需要在不同智能体会话之间保持长期记忆
- 将检索功能与智能体工具使用相结合
- 研究或开发语义搜索工作流

**如需其他功能，请使用 mlops/pinecone 技能：**
- 需要了解 Pinecone 的通用用法（索引管理、CRUD 操作、混合搜索功能）
- 在未集成 Agent 的环境下构建生产级基础设施

## 快速入门

### 设置

```bash
pip install pinecone-client langchain-pinecone langchain-openai
```

设置您的 API 密钥：
```bash
export PINECONE_API_KEY="your-api-key"
```

### 基础 RAG 流程

```python
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

# Initialize Pinecone
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

# Create or connect to index
index_name = "agent-memory"
if index_name not in [i.name for i in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

# Build vector store
vectorstore = PineconeVectorStore.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    index_name=index_name,
)

# Retrieve relevant context
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
results = retriever.invoke("What did the agent discuss yesterday?")
```

### 基于命名空间的会话内存

```python
# Store per-session memory
vectorstore = PineconeVectorStore(
    index=pc.Index(index_name),
    embedding=OpenAIEmbeddings(),
    namespace=f"session-{session_id}",
)

# Query across all sessions (no namespace filter)
all_memory = PineconeVectorStore(
    index=pc.Index(index_name),
    embedding=OpenAIEmbeddings(),
)
results = all_memory.similarity_search("relevant query", k=10)
```

## 最佳实践

1. **按会话或用户划分命名空间** —— 为多租户代理实现数据隔离  
2. **批量插入/更新** —— 每批处理100–200个向量以提高效率  
3. **元数据过滤** —— 用会话ID、时间戳和主题对向量进行标记  
4. **清理旧数据** —— 删除过时的命名空间以控制成本  
5. **采用无服务器架构** —— 支持自动扩展，并按使用量计费  

## 资源链接

- **Pinecone文档**：https://docs.pinecone.io  
- **LangChain集成指南**：https://python.langchain.com/docs/integrations/vectorstores/pinecone  
- **免费套餐**：1个索引，10万个向量（1536维）
