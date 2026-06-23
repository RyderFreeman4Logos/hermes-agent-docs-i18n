# Mem0 内存提供器

通过 Mem0 Platform v3 API，实现基于语义搜索与混合多信号检索的服务器端大语言模型事实提取功能。

## 前提条件

- 安装 `pip install mem0ai` 工具
- 从 [app.mem0.ai](https://app.mem0.ai) 获取 Mem0 API 密钥

## 配置步骤

```bash
hermes memory setup    # select "mem0"
```

或手动操作：
```bash
hermes config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.hermes/.env
```

## 配置

行为设置存储在 `$HERMES_HOME/mem0.json` 文件中（可通过 `hermes memory setup` 命令进行设置）。仅密钥 `MEM0_API_KEY` 应存储在 `~/.hermes/.env` 文件中。

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `mode` | `platform` | `platform`（Mem0 Cloud）或 `oss`（自托管） |
| `user_id` | `hermes-user` | Mem0 平台上的用户标识符 |
| `agent_id` | `hermes` | Agent 的标识符 |
| `rerank` | `true` | 根据相关性对搜索结果进行重新排序（仅适用于平台模式） |

## OSS（自托管）模式

使用您自己的大语言模型、嵌入器及向量存储在本地运行 Mem0。

### 交互式设置

```bash
hermes memory setup
# Select "mem0" → "Open Source (self-hosted)"
# Follow prompts for LLM, embedder, and vector store
```

### 由智能体驱动的配置（标志参数）

```bash
hermes memory setup mem0 --mode oss \
  --oss-llm openai --oss-llm-key sk-... \
  --oss-vector qdrant
```

### 支持的提供方

| 组件 | 提供方 |
|-----------|-----------|
| 大语言模型 | openai、ollama |
| 嵌入模型服务 | openai、ollama |
| 向量存储 | qdrant（本地/服务器版）、pgvector |

### 参数参考

| 参数 | 描述 |
|------|-----------|
| `--mode` | `platform` 或 `oss` |
| `--oss-llm` | 大语言模型提供方（默认：openai） |
| `--oss-llm-key` | 大语言模型 API 密钥 |
| `--oss-embedder` | 嵌入模型服务提供方（默认：openai） |
| `--oss-vector` | 向量存储服务（默认：qdrant） |
| `--oss-vector-path` | Qdrant 本地路径 |
| `--user-id` | 用户标识符 |

## 模式切换

### 从平台模式切换到 OSS 模式

```bash
hermes memory setup mem0 --mode oss --oss-llm-key sk-...
```

或者直接编辑 `$HERMES_HOME/mem0.json` 文件：
```json
{
  "mode": "oss",
  "oss": {
    "llm": {"provider": "openai", "config": {"model": "gpt-5-mini"}},
    "embedder": {"provider": "openai", "config": {"model": "text-embedding-3-small"}},
    "vector_store": {"provider": "qdrant", "config": {"path": "~/.hermes/mem0_qdrant"}}
  }
}
```

### 从开源服务到平台化解决方案

```bash
hermes memory setup mem0 --mode platform --api-key sk-...
```

### 测试运行（无需实际写入的预览功能）

```bash
hermes memory setup mem0 --mode oss --oss-llm-key sk-... --dry-run
```

## 工具

| 工具 | 描述 |
|------|-------------|
| `mem0_list` | 列出所有已存储的记忆（分页显示） |
| `mem0_search` | 基于语义含义进行搜索 |
| `mem0_add` | 按原文形式存储事实（无需通过大语言模型提取） |
| `mem0_update` | 根据编号更新记忆的文本内容 |
| `mem0_delete` | 根据编号删除记忆 |

## 故障排除

### “Mem0暂时不可用”

连续5次失败后触发了断路器保护，2分钟后自动恢复。

- **平台模式**：请检查API密钥及网络连接状态。
- **OSS模式**：请确认您的向量存储服务（qdrant/pgvector）正在运行。

### OSS：Qdrant连接被拒绝

```bash
# If using local Qdrant, check the storage path is writable:
ls -la ~/.hermes/mem0_qdrant

# If using Qdrant server, check it's reachable:
curl http://localhost:6333/healthz
```

### OSS：PGVector 连接被拒绝

```bash
# Verify PostgreSQL is running and accepting connections:
pg_isready -h localhost -p 5432
```

### OSS：无法连接到 Ollama

```bash
# Check Ollama is running:
curl http://localhost:11434/api/tags
```

### 记忆内容未显示

- `mem0_add` 会原封不动地存储内容（不会进行提取）。如需通过大型语言模型进行提取，请使用 `sync_turn`。
- 搜索功能采用语义匹配机制——请尝试使用更宽泛的查询词。
- 请检查各会话之间 `user_id` 是否一致（路径：`$
