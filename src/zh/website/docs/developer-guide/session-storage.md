# 会话存储

Hermes Agent 使用 SQLite 数据库（`~/.hermes/state.db`）来在 CLI 会话与网关会话之间持久化存储会话元数据、完整消息历史记录以及模型配置。这种方式取代了之前采用的每会话单独生成 JSONL 文件的方案。

源文件：`hermes_state.py`

## 架构概览

```
~/.hermes/state.db (SQLite, WAL mode)
├── sessions              — Session metadata, token counts, billing
├── messages              — Full message history per session
├── messages_fts          — FTS5 virtual table (content + tool_name + tool_calls)
├── messages_fts_trigram  — FTS5 virtual table with trigram tokenizer (CJK / substring search)
├── state_meta            — Key/value metadata table
└── schema_version        — Single-row table tracking migration state
```

核心设计决策：
- 采用**WAL模式**支持多个并发读取者与单个写入者（适用于网关多平台环境）
- 使用**FTS5虚拟表**实现對所有会话消息的快速文本搜索
- 通过`parent_session_id`链构建**会话关联关系**（基于压缩触发进行数据拆分）
- 添加**消息来源标签**（如`cli`、`telegram`、`discord`等）以实现平台筛选
- 批量处理引擎与强化学习轨迹数据不存储于此（属于独立系统）

## SQLite数据库结构

### 会话表

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    user_id TEXT,
    model TEXT,
    model_config TEXT,
    system_prompt TEXT,
    parent_session_id TEXT,
    started_at REAL NOT NULL,
    ended_at REAL,
    end_reason TEXT,
    message_count INTEGER DEFAULT 0,
    tool_call_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_write_tokens INTEGER DEFAULT 0,
    reasoning_tokens INTEGER DEFAULT 0,
    billing_provider TEXT,
    billing_base_url TEXT,
    billing_mode TEXT,
    estimated_cost_usd REAL,
    actual_cost_usd REAL,
    cost_status TEXT,
    cost_source TEXT,
    pricing_version TEXT,
    title TEXT,
    api_call_count INTEGER DEFAULT 0,
    FOREIGN KEY (parent_session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_source ON sessions(source);
CREATE INDEX IF NOT EXISTS idx_sessions_parent ON sessions(parent_session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_title_unique
    ON sessions(title) WHERE title IS NOT NULL;
```

### 消息表

```sql
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    role TEXT NOT NULL,
    content TEXT,
    tool_call_id TEXT,
    tool_calls TEXT,
    tool_name TEXT,
    timestamp REAL NOT NULL,
    token_count INTEGER,
    finish_reason TEXT,
    reasoning TEXT,
    reasoning_content TEXT,
    reasoning_details TEXT,
    codex_reasoning_items TEXT,
    codex_message_items TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, timestamp);
```

备注：  
- `tool_calls` 以 JSON 字符串的形式存储（即工具调用对象的序列化列表）；  
- `reasoning_details`、`codex_reasoning_items` 以及 `codex_message_items` 均以 JSON 字符串形式存储；  
- 对于支持展示推理过程的提供者，`reasoning` 字段将存储其原始推理文本；  
- 时间戳为 Unix 时间戳浮点数（即 `time.time()` 的返回值）。  

### FTS5 全文搜索

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content,
    content=messages,
    content_rowid=id
);
```

FTS5 表通过三个触发器保持同步，这些触发器会在 `messages` 表执行插入、更新和删除操作时被触发：

```sql
CREATE TRIGGER IF NOT EXISTS messages_fts_insert AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_fts_delete AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content)
        VALUES('delete', old.id, old.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_fts_update AFTER UPDATE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content)
        VALUES('delete', old.id, old.content);
    INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;
```


## 架构版本与迁移说明

当前架构版本为：**21**

`schema_version` 表中仅存储一个整数。对于简单的列添加操作，系统会通过 `_reconcile_columns()` 函数以声明式方式处理（该函数会对比实际存在的列与 `SCHEMA_SQL` 中的定义，从而补充缺失的列）。而版本控制机制则专门用于那些无法通过声明式方式实现的数据迁移以及索引/FTS 相关的变更：

| 版本号 | 变更内容 |
|--------|----------|
| 1 | 初始架构（包含 sessions、messages、FTS5 功能） |
| 2 | 为 messages 表添加 `finish_reason` 列 |
| 3 | 为 sessions 表添加 `title` 列 |
| 4 | 在 `title` 列上创建唯一索引（允许为空值，非空值必须唯一） |
| 5 | 添加计费相关列：`cache_read_tokens`、`cache_write_tokens`、`reasoning_tokens`、`billing_provider`、`billing_base_url`、`billing_mode`、`estimated_cost_usd`、`actual_cost_usd`、`cost_status`、`cost_source`、`pricing_version` |
| 6 | 为 messages 表添加推理相关列：`reasoning`、`reasoning_details`、`codex_reasoning_items` |
| 7 | 为 messages 表添加 `reasoning_content` 列 |
| 8 | 为 sessions 表添加 `api_call_count` 列 |
| 9 | 为 messages 表添加 `codex_message_items` 列，用于复现 Codex Responses 类型的消息 ID/阶段信息 |
| 10 | 添加 `messages_fts_trigram` 虚拟表（用于处理中文字体的三字组分词及子串搜索功能），并回填现有数据行 |
| 11 | 重新为 `messages_fts` 和 `messages_fts_trigram` 创建索引，以覆盖 `tool_name` + `tool_calls` 组合信息；同时将索引模式从外部内容读取方式改为内联模式；删除旧的触发器，并为每条消息行回填数据 |
| 16 | 在 `model_config` 中为代理子智能体对应的行添加标记（字段为 `$._delegate_from`），这样当父智能体将其删除后，会话选择器仍能保持正常工作状态 |
| 18 | 整合网关元数据——从 `sessions.json` 文件中回填 `display_name`、`origin_json`、`expiry_finalized` 等字段 |
| 20 | 实现按模型划分的使用量统计功能——根据历史上的每会话使用总量，初始化 `session_model_usage` 表中的数据行 |

未列在上述版本中的变更，均是通过 `_reconcile_columns()` 函数以声明式方式实现的列添加操作（仅涉及版本号升级，不涉及数据迁移）。

此类声明式列添加操作会使用 `ALTER TABLE ADD COLUMN` 语句，并通过 try/except 机制来处理列已存在的情况（具备幂等性）。每次成功的迁移完成后，版本号都会随之上升。

## 写入冲突处理机制

多个 Hermes 进程（包括网关、CLI 会话以及工作树中的智能体）会共享同一个 `state.db` 文件。`SessionDB` 类通过以下方式来解决写入冲突问题：

- 使用较短的 SQLite 超时时间（1秒），而非默认的30秒；
- 在应用层实现带有随机抖动时间的重试机制（抖动范围为20-150毫秒，最多可重试15次）；
- 使用 `BEGIN IMMEDIATE` 事务，在事务开始阶段即可检测到锁定冲突；
- 每完成50次成功写入后进行一次 WAL 检查点操作（处于被动模式）。

这些措施旨在避免“车队效应”——即由于 SQLite 内部固定的退避机制，导致所有同时尝试写入的进程都在相同的间隔时间进行重试。

```
_WRITE_MAX_RETRIES = 15
_WRITE_RETRY_MIN_S = 0.020   # 20ms
_WRITE_RETRY_MAX_S = 0.150   # 150ms
_CHECKPOINT_EVERY_N_WRITES = 50
```


## 常见操作

### 初始化

```python
from hermes_state import SessionDB

db = SessionDB()                           # Default: ~/.hermes/state.db
db = SessionDB(db_path=Path("/tmp/test.db"))  # Custom path
```

### 创建与管理会话

```python
# Create a new session
db.create_session(
    session_id="sess_abc123",
    source="cli",
    model="anthropic/claude-sonnet-4.6",
    user_id="user_1",
    parent_session_id=None,  # or previous session ID for lineage
)

# End a session
db.end_session("sess_abc123", end_reason="user_exit")

# Reopen a session (clear ended_at/end_reason)
db.reopen_session("sess_abc123")
```

### 存储消息

```python
msg_id = db.append_message(
    session_id="sess_abc123",
    role="assistant",
    content="Here's the answer...",
    tool_calls=[{"id": "call_1", "function": {"name": "terminal", "arguments": "{}"}}],
    token_count=150,
    finish_reason="stop",
    reasoning="Let me think about this...",
)
```

### 获取消息

```python
# Raw messages with all metadata
messages = db.get_messages("sess_abc123")

# OpenAI conversation format (for API replay)
conversation = db.get_messages_as_conversation("sess_abc123")
# Returns: [{"role": "user", "content": "..."}, {"role": "assistant", ...}]
```

### 会话标题

```python
# Set a title (must be unique among non-NULL titles)
db.set_session_title("sess_abc123", "Fix Docker Build")

# Resolve by title (returns most recent in lineage)
session_id = db.resolve_session_by_title("Fix Docker Build")

# Auto-generate next title in lineage
next_title = db.get_next_title_in_lineage("Fix Docker Build")
# Returns: "Fix Docker Build #2"
```


## 全文搜索

`search_messages()` 方法支持 FTS5 查询语法，并能自动对用户输入的内容进行净化处理。

### 基本搜索

```python
results = db.search_messages("docker deployment")
```

### FTS5 查询语法

| 语法类型 | 示例 | 含义 |
|--------|---------|------|
| 关键词查询 | `docker deployment` | 两个词均需匹配（逻辑为 AND） |
| 引号短语查询 | `"exact phrase"` | 精确匹配整个短语 |
| 布尔 OR 查询 | `docker OR kubernetes` | 任意一个词即可匹配 |
| 布尔 NOT 查询 | `python NOT java` | 排除某个词 |
| 前缀查询 | `deploy*` | 匹配以该前缀开头的词 |

### 筛选搜索

```python
# Search only CLI sessions
results = db.search_messages("error", source_filter=["cli"])

# Exclude gateway sessions
results = db.search_messages("bug", exclude_sources=["telegram", "discord"])

# Search only user messages
results = db.search_messages("help", role_filter=["user"])
```

### 搜索结果格式

每条搜索结果包含以下内容：
- `id`、`session_id`、`role`、`timestamp`
- `snippet` — 由 FTS5 生成的片段，其中包含 `>>>match<<<` 标记
- `context` — 匹配内容前后各 1 条消息（内容长度限制为 200 字符）
- `source`、`model`、`session_started` — 取自父会话信息

 `_sanitize_fts5_query()` 方法用于处理各种边界情况：
- 删除未匹配的引号及特殊字符
- 将连字符连接的词组用引号括起来（如 `chat-send` → `"chat-send"`）
- 移除多余的布尔运算符（如 `hello AND` → `hello`）

## 会话关联关系

通过 `parent_session_id`，多个会话可以形成链式关联。这种情况通常发生在网关因上下文压缩而触发会话拆分时。

### 查询：查找会话关联关系

```sql
-- Find all ancestors of a session
WITH RECURSIVE lineage AS (
    SELECT * FROM sessions WHERE id = ?
    UNION ALL
    SELECT s.* FROM sessions s
    JOIN lineage l ON s.id = l.parent_session_id
)
SELECT id, title, started_at, parent_session_id FROM lineage;

-- Find all descendants of a session
WITH RECURSIVE descendants AS (
    SELECT * FROM sessions WHERE id = ?
    UNION ALL
    SELECT s.* FROM sessions s
    JOIN descendants d ON s.parent_session_id = d.id
)
SELECT id, title, started_at FROM descendants;
```

### 查询：包含预览功能的近期会话记录

```sql
SELECT s.*,
    COALESCE(
        (SELECT SUBSTR(m.content, 1, 63)
         FROM messages m
         WHERE m.session_id = s.id AND m.role = 'user' AND m.content IS NOT NULL
         ORDER BY m.timestamp, m.id LIMIT 1),
        ''
    ) AS preview,
    COALESCE(
        (SELECT MAX(m2.timestamp) FROM messages m2 WHERE m2.session_id = s.id),
        s.started_at
    ) AS last_active
FROM sessions s
ORDER BY s.started_at DESC
LIMIT 20;
```

### 查询：令牌使用统计信息

```sql
-- Total tokens by model
SELECT model,
       COUNT(*) as session_count,
       SUM(input_tokens) as total_input,
       SUM(output_tokens) as total_output,
       SUM(estimated_cost_usd) as total_cost
FROM sessions
WHERE model IS NOT NULL
GROUP BY model
ORDER BY total_cost DESC;

-- Sessions with highest token usage
SELECT id, title, model, input_tokens + output_tokens AS total_tokens,
       estimated_cost_usd
FROM sessions
ORDER BY total_tokens DESC
LIMIT 10;
```


## 导出与清理

```python
# Export a single session with messages
data = db.export_session("sess_abc123")

# Export all sessions (with messages) as list of dicts
all_data = db.export_all(source="cli")

# Delete old sessions (only ended sessions)
deleted_count = db.prune_sessions(older_than_days=90)
deleted_count = db.prune_sessions(older_than_days=30, source="telegram")

# Clear messages but keep the session record
db.clear_messages("sess_abc123")

# Delete session and all messages
db.delete_session("sess_abc123")
```


## 数据库位置

默认路径为：`~/.hermes/state.db`

该路径由 `hermes_constants.get_hermes_home()` 函数确定，其默认值为 `~/.hermes/`，也可根据 `HERMES_HOME` 环境变量的值来设定。

数据库文件、WAL 文件（`state.db-wal`）以及共享内存文件（`state.db-shm`）都会创建在同一个目录中。
