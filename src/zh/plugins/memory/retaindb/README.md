# RetainDB 内存提供程序

这款云内存 API 支持混合搜索功能（向量搜索 + BM25 + 重排算法），并提供 7 种不同类型的内存空间。

## 前提条件

- 需在 [retaindb.com](https://www.retaindb.com) 注册 RetainDB 账户（费用为每月 20 美元）
- 安装 `pip install requests` 工具

## 设置步骤

```bash
hermes memory setup    # select "retaindb"
```

或手动操作：
```bash
hermes config set memory.provider retaindb
echo "RETAINDB_API_KEY=your-key" >> ~/.hermes/.env
```

## 配置

所有配置均通过 `.env` 文件中的环境变量进行设置：

| 环境变量 | 默认值 | 描述 |
|---------|---------|-------------|
| `RETAINDB_API_KEY` | （必填） | API密钥 |
| `RETAINDB_BASE_URL` | `https://api.retaindb.com` | API接口地址 |
| `RETAINDB_PROJECT` | auto（基于用户配置文件） | 项目标识符 |

## 工具

| 工具 | 描述 |
|------|-------------|
| `retaindb_profile` | 用户的稳定配置文件 |
| `retaindb_search` | 语义搜索功能 |
| `retaindb_context` | 与任务相关的上下文信息 |
| `retaindb_remember` | 按类型和重要性存储事实信息 |
| `retaindb_forget` | 根据ID删除记忆内容 |
