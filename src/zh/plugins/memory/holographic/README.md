# 全息记忆提供者

基于本地 SQLite 的事实存储引擎，具备 FTS5 搜索功能、信任度评分机制、实体解析能力，以及基于 HRR 的组合检索技术。

## 需求条件

无特殊要求——直接使用始终可用的 SQLite。如需进行 HRR 算术运算，可选配 NumPy 库。

## 设置方法

```bash
hermes memory setup    # select "holographic"
```

或手动操作：
```bash
hermes config set memory.provider holographic
```

## 配置

在 `config.yaml` 文件的 `plugins.hermes-memory-store` 下进行配置：

| 键值 | 默认值 | 描述 |
|-----|---------|-------------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite 数据库路径 |
| `auto_extract` | `false` | 会话结束时自动提取事实 |
| `default_trust` | `0.5` | 新事实的默认信任度得分 |
| `hrr_dim` | `1024` | HRR 向量的维度 |

## 工具

| 工具 | 描述 |
|------|-------------|
| `fact_store` | 提供 9 种操作：添加、搜索、查询关联、推理、矛盾检测、更新、删除、列表展示 |
| `fact_feedback` | 对事实的有用性进行评分（用于训练信任度得分） |
