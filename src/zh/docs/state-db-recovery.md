# 状态数据库与FTS恢复机制

`state.db`存储两类不同的数据：

- `sessions`和`messages`代表标准格式的对话记录；
- `messages_fts*`表及其同步触发器则为派生搜索索引。

这些派生索引可被暂时断开。但绝不能因此导致实时消息写入或搜索操作演变为无限制的全量对话记录重建过程。

## FTS损坏时的运行行为

当FTS的写入或搜索操作返回损坏错误时，`SessionDB`会执行以下操作：

1. 记录永久性的`fts_stale`标记；
2. 在同一事务中移除FTS同步触发器；
3. 跳过派生索引直接尝试标准格式的写入操作；以及
4. 通过`LIKE`回退机制，从标准格式的记录中响应搜索请求。

出现故障的实时操作不会执行`FTS5('rebuild')`命令。现有的恢复机制保持不变：后续打开的`SessionDB`可在跨进程访问锁及外部持有者保护机制下进行重建。如果该受保护的重建操作无法执行，FTS仍将处于断开状态，标准格式的写入功能依然可用，同时`hermes doctor`会提示明确的修复命令。

## 文件本身损坏时的运行行为

若实时写入操作返回纯粹的`SQLITE_CORRUPT`/`SQLITE_NOTADB`错误（意为“数据库磁盘图像格式错误”或“文件并非有效数据库”），且不存在FTS相关的故障痕迹，说明损坏发生在标准格式的B树结构、模式定义或自由列表中。此时`SessionDB`会将该受影响的模块隔离处理（触发`StateDbCorruptError`错误）。

1. 写入操作失败时会传递相应的错误信息，且不会进行任何重试；  
2. 后续对该句柄的写入操作会立即失败，而不会实际修改文件内容；  
3. 在调用 `close()` 后，该句柄永远不会重新建立连接；  
4. `close()` 操作会跳过显式的 WAL 检查点。  

停止写入操作是第一道防护措施。在实际使用中，曾有案例显示：在首次出现结构错误后，某个句柄仍持续写入约50分钟，最终在关闭时将15页数据以错误的页码写入（第1页被错误地标记为 `messages_fts_trigram_data` 类型），从而导致原本虽已损坏但仍可读取的文件彻底无法打开。跳过显式检查点是第二道防护措施；在 Python 3.12 及更高版本中，隔离机制还会禁用 SQLite 自带的“关闭时无需检查点”选项（`SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE`），这样 `-wal` 辅助进程就能在 `close()` 后依然存在，以便后续进行故障分析。而在 Python 3.11 中则不支持该选项，SQLite 可能在关闭时仍会执行一次检查点操作，因此在对任何服务进行重启之前，务必先将 `state.db`、`state.db-wal` 和 `state.db-shm` 这三个文件一起复制备份。  

网关和代理的刷新机制会将处于隔离状态的文件视为已被替换的文件：待处理的转录内容会被存放到 `sessions/<id>.jsonl` 文件以及网关的 `pending_messages/` 缓存目录中，而非重试队列中；同时，针对 FTS 的一次性重建操作也绝不会在受损文件上执行。隔离状态是针对单个进程而言的——只要进程仍在使用那个受损的句柄，它就会一直处于“污染”状态，直到该进程使用已修复或恢复好的文件重新启动为止。在网关仍在运行的情况下，请勿执行 `hermes doctor --fix` 命令。后续步骤：

```bash
hermes gateway stop
HERMES_HOME="$HOME/.hermes" hermes sessions recover --source "$HOME/.hermes/state.db" --inspect-only
# if recoverable:
HERMES_HOME="$HOME/.hermes" hermes sessions recover --source "$HOME/.hermes/state.db" --output "$HOME/recovered-state.db"
```

或者从 `state-snapshots/` 中恢复最新的快照。

## 显式修复

在修复配置文件数据库之前，先终止所有可能打开该数据库的进程。
在整个修复及验证过程中，均需保持这些进程处于停止状态。

```bash
hermes gateway stop
HERMES_HOME="$HOME/.hermes" hermes sessions repair --check-only
HERMES_HOME="$HOME/.hermes" hermes sessions repair
```

“sessions repair”功能默认会创建一个SQLite备份，并通过仓库所采用的受保护快照与升级机制来修复数据结构。请勿使用`cp`命令单独复制`state.db`、`state.db-wal`和`state.db-shm`这三个文件，因为它们实际上是一个完整的SQLite数据文件。

修复完成后，在重启网关之前，请先检查健康检测状态、过期标记、触发器设置以及标准行数是否正常。

```bash
HERMES_HOME="$HOME/.hermes" hermes sessions repair --check-only
sqlite3 "$HOME/.hermes/state.db" \
  "SELECT key, value FROM state_meta WHERE key = 'fts_stale';"
sqlite3 "$HOME/.hermes/state.db" \
  "SELECT type, name FROM sqlite_master WHERE name IN
   ('messages_fts_insert','messages_fts_update','messages_fts_delete')
   ORDER BY name;"
sqlite3 "$HOME/.hermes/state.db" \
  "SELECT 'sessions', COUNT(*) FROM sessions
   UNION ALL SELECT 'messages', COUNT(*) FROM messages;"
```

标记查询不应返回任何记录，必须触发预期的FTS机制，且标准记录的数量绝不能减少。如果修复失败，请同时保留实时数据库和已生成的备份文件；切勿为消除派生索引错误而删除标准记录。
