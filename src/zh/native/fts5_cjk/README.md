# fts5_cjk — cjk_unicode61 FTS5 分词器

该分词器基于 unicode61 规则并结合了 CJK 字符二元组特性（遵循 Lucene CJKAnalyzer 的逻辑）。其功能在于解决在会话搜索中，长度为 1-2 个字符的韩文、中文或日文词汇被错误地转而进行全表 LIKE 查询的问题。

构建并安装到 `~/.hermes/lib/` 目录下：

    ./build.sh

若系统已存在 `sqlite3ext.h` 头文件，则直接使用；否则将使用 `vendor/` 目录中的预置版本——无需安装 libsqlite3-dev 工具包。

一旦该扩展模块被安装，下次打开 `SessionDB` 时就会自动创建 `messages_fts_cjk` 索引（外部内容及工具行将被排除，其存储规则与其他索引一致，均遵循 v23 的规范）。对于已包含数据的数据库，可运行以下命令进行补充索引：

    hermes sessions optimize-storage

无论何种情况，新消息都会被实时索引。如需禁用此功能，可在 `~/.hermes/config.yaml` 文件中将 `sessions.cjk_fts` 设置为 `false`。也可通过 `HERMES_FTS5_CJK_SO` 参数指定 .so 文件的路径。

该功能由 Soju06 提供（PR #65544）。
