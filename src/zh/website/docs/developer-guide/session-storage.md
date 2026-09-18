# 会话存储

Hermes Agent 使用 SQLite 数据库（`~/.hermes/state.db`）来在 CLI 会话与网关会话之间持久保存会话元数据、完整消息历史记录以及模型配置，从而取代了之前那种为每个会话单独创建 JSONL 文件的方式。相关源文件包括：`hermes_state.py`（接口层）以及一系列 `hermes_state_*.py` 文件（分别负责处理架构定义、全文搜索、查询功能、数据压缩、跨平台适配、网关相关等功能）。

### 桌面端配置文件的隔离与压缩机制

无论单个 `hermes serve` 进程同时为多个配置文件提供服务，每个命名配置文件都会将其对应的内容存储在独立的 `$HERMES_HOME/state.db` 文件中。在会话进行中的 Agent 重建操作（如机器人聊天功能的刷新或通过 `tools.configure` 执行配置调整）必须保留该会话的数据库连接句柄，并在重建过程中绑定对应的配置文件路径。即将被替换的 Agent 退出时，不得关闭其继承来的数据库连接句柄。即便客户端仅提供 `session_id`，`tools.configure` 功能仍能从当前活跃会话的 `profile_home` 路径中读取配置信息。Agent 会在分配新的实例之前先准备好模型配置，随后再安装新 Agent 并同步移交相关控制权；如果准备阶段出现故障，则由原有的 Agent 负责完成后续的清理工作。那些无法被识别或对应目录已消失的显式配置文件，在尝试访问启动配置或历史记录之前就会失败。同样，过期的 `tools.configure` 会话 ID 也会导致“会话未找到”的错误，且不会对现有配置产生影响；即便省略会话 ID，该功能仍可正常用于修改全局设置。

就地压缩功能会将 `active=0` 的旧记录进行归档，同时将保留的上下文作为 `active=1` 的记录插入。因此，受保护的消息可以合法地同时出现在两代记录中，且内容和时间戳完全一致。请勿将这些归档记录误认为是重复项而删除。若发现重复的*实时*写入，请通过 `active=1` 进行诊断；在调查似乎出现回退的历史记录时，还需检查数据库配置及会话 ID。

## Codex 应用服务器输入所有权

在开始执行 Codex 任务之前，智能体会先保存用户输入的内容。随后，Codex 会将该输入作为开头的 `userMessage` 通知呈现出来。在运行时的拼接节点处，Hermes 仅会排除那些与序列化为 `turn/start` 的文本完全匹配的项，包括经过格式转换的富文本输入。之后发生的或不匹配的用户事件将保持完整，单独接收到的相同内容任务也同样如此。这一规则同样适用于合成输入/无密钥输入，且与平台消息 ID 无关。现有的历史重复记录不会被重写。当智能体声明其拥有数据持久化权限时，网关将跳过对应的转录记录写入操作。

## 网关异常路径输入所有权

网关异常可能发生在代理构建之前，也可能在其输入数据抵达 SQLite 之后。网关会在现有的 `display_metadata` 侧边数据结构中为已接收的输入添加所有者标记，然后通过代理常规的持久化路径进行处理。而提供者发送的消息则不会包含此类元数据。平台标记会根据平台、配置文件、作用域、聊天窗口及线程对传入的消息 ID 进行命名；为了解决引用/回复问题，原始的 `platform_message_id` 保持不变。即便文本内容和时间戳完全相同，无密钥模式下的消息也会获得新的标记。

异常处理机制仅会按照既定的重路由规则、标准实时压缩后的数据流以及压缩前的数据流顺序来查找该标记。处于活跃状态的行以及经过压缩的归档数据会被计入考量范围，而已撤销的行、被监控的输入数据以及无关的处理进程则不会被考虑。即使有其他进程正在处理同一会话，也无法抑制此次异常处理流程的启动。此外，无需建立完整的歷史记录基准或专门的归档消息体存储空间。若所有权读取失败，系统也不会允许进行推测性追加操作；而普通的歷史记录读取失败则仍会返回“历史记录不可用”的响应。

代理自身的常规持久化机制不会因此发生改变。这属于针对故障处理流程的仲裁机制，而非实现绝对一次性的数据传输、内容去重或架构迁移的功能。历史记录行不会被重新写入；未被标记的历史输入数据也无法为重新发送的事件确立所有权。

## 架构概览

```
~/.hermes/state.db (SQLite, WAL mode)
├── sessions              — Session metadata, token counts, billing
├── messages              — Full message history per session
├── session_model_usage   — Per-model/per-task usage attribution rows
├── messages_fts          — FTS5 virtual table (content + tool_name + tool_calls)
├── messages_fts_trigram  — FTS5 virtual table with trigram tokenizer (CJK / substring search)
├── messages_fts_cjk      — FTS5 virtual table with cjk_unicode61 tokenizer
├── state_meta            — Key/value metadata table
├── gateway_routing       — Gateway routing metadata
├── compression_locks     — Cross-process compression locking
├── async_delegations     — Async delegation bookkeeping
├── delivery_obligations  — Gateway outbox (owed replies); created lazily by gateway/delivery_ledger.py
└── schema_version        — Single-row table tracking migration state
```

`hermes sessions recover` 会将上述包含数据的表复制到恢复后的数据库中（FTS索引及`schema_version`会被重新生成）。如果源端存在延迟生成的`delivery_obligations`账本，该账本也会被一同复制——其行数会像`sessions`/`messages`一样进行验证。

主要设计决策：
- 采用**WAL模式**，支持多个并发读取器与一个写入器（适用于多平台网关）
- 使用**FTS5虚拟表**，实现对所有会话消息的快速文本搜索
- 通过`parent_session_id`链构建**会话关联关系**（基于压缩触发进行数据拆分）
- 添加**源端标签**（如`cli`、`telegram`、`discord`等），便于按平台筛选数据
- 批量处理任务及强化学习轨迹不会存储在此处（由独立系统负责）

## SQLite架构

### 会话表

此处仅展示简化版本——完整当前的列列表请参阅`hermes_state_common.py`中的`SCHEMA_SQL`文件（该内容由`hermes_state_schema.py`处理）（其中还包含网关路由相关元数据，如`session_key`、`chat_id`、`chat_type`、`thread_id`、`display_name`、`origin_json`、`expiry_finalized`，以及工作区相关字段`cwd`/`git_branch`/`git_repo_root`；此外还包括交接处理、压缩失败相关的字段，以及`profile_name`、`rewind_count`、`archived`和`pinned`等属性）：

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
    -- ... additional gateway/workspace/handoff/compression columns ...
    FOREIGN KEY (parent_session_id) REFERENCES sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_source ON sessions(source);
CREATE INDEX IF NOT EXISTS idx_sessions_parent ON sessions(parent_session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_title_unique
    ON sessions(title) WHERE title IS NOT NULL;
```

### 消息表

此处仅展示简化版本——完整的架构还包括 `effect_disposition`、`platform_message_id`、`observed`、`active`、`compacted`、`api_content`、`display_kind` 以及 `display_metadata` 等字段：

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
    -- ... additional display/compaction columns ...
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id, id);
```

备注：  
- `tool_calls` 以 JSON 字符串的形式存储（即工具调用对象的序列化列表）；  
- `reasoning_details`、`codex_reasoning_items` 以及 `codex_message_items` 均以 JSON 字符串形式存储。  
- 桌面端历史记录恢复功能在 REST 和 JSON-RPC 接口中都会保留助手相关的附加数据（包括通过 `session.resume`、`session.activate`、`session.history` 获取的数据），这些数据中可能包含推理过程及工具调用信息。REST 接口会返回 SQLite 格式的 JSON 字符串，而 RPC 接口则返回已解码的数据；桌面端可接受这两种格式的数据。在某些情况下，最终的回复内容可能仅存在于 `codex_message_items` 中，而 `content` 字段为空。不过标准内容仍具有优先级，分析或评论类内容不会被提升为回复文本。  
- 对于那些支持展示推理过程的提供方，`reasoning` 字段会存储其原始推理文本。  
- `api_content` 是一种保持字节级精确度的附加数据：当该字段的内容与 `content` 不同时，它保存的是此次消息发送给 API 的原始内容字符串（例如临时内存中的数据、插件注入的内容，或是持久化覆盖后的内容）。该字段旨在实现基于提示词缓存的稳定回放功能——数据会按发送时的原样存储，不过那些 sqlite3 无法绑定的单独替代数据会被对话循环从所有输出数据中剔除。若该字段值为 `NULL`，则表示 `content` 字段的内容已被原封不动地发送。  
- 时间戳为 Unix 时间戳浮点数（即 `time.time()` 的返回值）。  

### FTS5 全文搜索

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content,
    tool_name,
    tool_calls,
    content='messages',
    content_rowid='id'
);
```

FTS5 表通过三个触发器保持同步，这些触发器会在 `messages` 表执行 INSERT、UPDATE 和 DELETE 操作时被触发。当前的触发器会依据 `state_meta` 中的 `fts_rebuild_high_water` / `fts_rebuild_progress` 标记来控制执行（这样就可以在后台进行 FTS 重建，而不会导致重复索引），并且会覆盖所有三个被索引的列——具体的 SQL 语句请参见 `hermes_state_common.py` 文件中的 `SCHEMA_SQL` 部分。

## 架构版本与迁移

当前架构版本为：**23**

`schema_version` 表仅存储一个整数。简单的列添加功能由 `_reconcile_columns()` 函数以声明式方式处理（该函数会对比实际列与 `SCHEMA_SQL` 中的定义，然后补充任何缺失的列）。而基于版本控制的迁移机制则用于处理那些无法通过声明式方式实现的数据迁移以及索引/FTS 相关的变更。

| Version | Change |
|---------|--------|
| 1 | Initial schema (sessions, messages, FTS5) |
| 2 | Add `finish_reason` column to messages |
| 3 | Add `title` column to sessions |
| 4 | Add unique index on `title` (NULLs allowed, non-NULL must be unique) |
| 5 | Add billing columns: `cache_read_tokens`, `cache_write_tokens`, `reasoning_tokens`, `billing_provider`, `billing_base_url`, `billing_mode`, `estimated_cost_usd`, `actual_cost_usd`, `cost_status`, `cost_source`, `pricing_version` |
| 6 | Add reasoning columns to messages: `reasoning`, `reasoning_details`, `codex_reasoning_items` |
| 7 | Add `reasoning_content` column to messages |
| 8 | Add `api_call_count` column to sessions |
| 9 | Add `codex_message_items` column to messages for Codex Responses message id/phase replay |
| 10 | Add `messages_fts_trigram` virtual table (trigram tokenizer for CJK / substring search) and backfill existing rows |
| 11 | Re-index `messages_fts` and `messages_fts_trigram` to cover `tool_name` + `tool_calls` and switch from external-content to inline mode; drop old triggers and backfill every message row |
| 16 | Tag delegate subagent rows in `model_config` (`$._delegate_from`) so session pickers stay clean after parent deletes orphan them |
| 18 | Gateway metadata consolidation — backfill `display_name` / `origin_json` / `expiry_finalized` from `sessions.json` |
| 20 | Per-model usage attribution — seed `session_model_usage` rows from historical per-session aggregate totals |
| 22 | Task-dimension usage attribution — rebuild `session_model_usage` so the `task` column participates in the PRIMARY KEY |
| 23 | FTS storage redesign — external-content FTS tables replacing the v11 inline-mode copies (opt-in transition for existing DBs) |
| 29 | Cron sessions leave the trigram (substring/CJK) index; `messages_fts_trigram_src` view + triggers filter on `sessions.source`, one-time rebuild purges historical rows |
| 30 | Delegate-child (subagent) sessions leave the trigram index too — `source='subagent'` or the `$._delegate_from` marker (`FTS_TRIGRAM_SESSION_SQL`). Rows stay in `messages` and the standard `messages_fts` word index, so `session_search` still finds them; only the ~2.6× trigram shadow tables shrink. Same one-time rebuild as v29 |

上述版本中未列出的情况属于通过 `_reconcile_columns()` 实现的声明式列添加功能（仅会升级版本号，无需进行数据迁移）。

此类声明式列添加操作会使用 `ALTER TABLE ADD COLUMN` 语句，并通过 try/except 机制来处理列已存在的情况，从而确保操作的幂等性。每次成功完成数据迁移后，版本号都会随之上升。

## 写入冲突处理

多个 Hermes 进程（网关、CLI 会话以及工作树代理）会共享同一个 `state.db` 文件。`SessionDB` 类通过以下方式解决写入冲突问题：

- 使用较短的 SQLite 超时时间（1秒），而非默认的30秒；
- 在应用层实现带有随机抖动时间的重试机制（抖动范围为20-150毫秒，最多重试15次）；
- 使用 `BEGIN IMMEDIATE` 事务，在事务开始时就检测锁定冲突；
- 每完成50次成功写入后进行一次 WAL 检查点生成（处于被动模式）。

这些措施可避免“车队效应”——即由于 SQLite 内部的确定性退避机制，导致所有同时写入的进程都在相同的间隔时间进行重试。

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
| 关键词查询 | `docker deployment` | 两个词同时出现（等价于 AND 运算） |
| 引号短语查询 | `"exact phrase"` | 精确匹配整个短语 |
| 布尔 OR 查询 | `docker OR kubernetes` | 任一词出现即可 |
| 布尔 NOT 查询 | `python NOT java` | 排除指定词 |
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
- `context` — 匹配结果前后各 1 条消息（内容长度限制为 200 字符）
- `source`、`model`、`session_started` — 取自父会话信息

 `_sanitize_fts5_query()` 方法用于处理各种边界情况：
- 删除未匹配的引号及特殊字符
- 将连写的词汇用引号括起来（如 `chat-send` → `"chat-send"`）
- 移除多余的布尔运算符（如 `hello AND` → `hello`）

## 会话层级关系

通过 `parent_session_id`，多个会话可以形成链式结构。这种情况通常发生在网关因上下文压缩而触发会话分割时。

### 查询：查找会话层级关系

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

该路径由 `hermes_constants.get_hermes_home()` 函数确定，其默认值为 `~/.hermes/`，也可由 `HERMES_HOME` 环境变量的值决定。

数据库文件、WAL 文件（`state.db-wal`）以及共享内存文件（`state.db-shm`）都会创建在同一个目录中。
