---
title: "Siyuan"
sidebar_label: "Siyuan"
description: "SiYuan Note API for searching, reading, creating, and managing blocks and documents in a self-hosted knowledge base via curl"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# SiYuan

SiYuan Note API 允许用户通过 curl 命令，在自托管的知识库中搜索、读取、创建及管理笔记块与文档。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 可使用 `hermes skills install official/productivity/siyuan` 安装 |
| 路径 | `optional-skills/productivity/siyuan` |
| 版本 | `1.0.0` |
| 开发者 | FEUAZUR |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `SiYuan`、`笔记`、`知识库`、`PKM`、`API` |
| 相关技能 | [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian)、[`notion`](/docs/user-guide/skills/bundled/productivity/productivity-notion) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# SiYuan Note API

可通过 curl 命令调用 [SiYuan](https://github.com/siyuan-note/siyuan) 核心 API，从而在自托管的知识库中对笔记块与文档进行搜索、读取、创建、更新及删除操作。无需额外工具——仅需 curl 命令及 API 令牌即可。

## 先决条件

1. 安装并运行 SiYuan（桌面版或 Docker 版）
2. 获取您的 API 令牌：**设置 > 关于 > API 令牌**
3. 将该令牌保存在 `~/.hermes/.env` 文件中：
   ```
   SIYUAN_TOKEN=your_token_here
   SIYUAN_URL=http://127.0.0.1:6806
   ```
如果未进行设置，`SIYUAN_URL` 的默认值为 `http://127.0.0.1:6806`。

## API 基础知识

所有 SiYuan API 调用均采用 **带有 JSON 数据体的 POST 请求**。每个请求都遵循以下格式：

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/..." \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"param": "value"}'
```

响应为结构如下的 JSON 格式数据：
```json
{"code": 0, "msg": "", "data": { ... }}
```
`code: 0` 表示操作成功。其他任何值均表示出现错误——请查看 `msg` 字段以获取详细信息。

**ID 格式：** SiYuan ID 的格式为 `20210808180117-6v0mkxr`（14位时间戳 + 7位字母数字组合）。

## 快速参考

| 操作 | 接口地址 |
|-----------|----------|
| 全文搜索 | `/api/search/fullTextSearchBlock` |
| SQL 查询 | `/api/query/sql` |
| 读取代码块 | `/api/block/getBlockKramdown` |
| 读取子节点 | `/api/block/getChildBlocks` |
| 获取路径 | `/api/filetree/getHPathByID` |
| 获取属性 | `/api/attr/getBlockAttrs` |
| 列出笔记本 | `/api/notebook/lsNotebooks` |
| 列出文档 | `/api/filetree/listDocsByPath` |
| 创建笔记本 | `/api/notebook/createNotebook` |
| 创建文档 | `/api/filetree/createDocWithMd` |
| 追加代码块 | `/api/block/appendBlock` |
| 更新代码块 | `/api/block/updateBlock` |
| 重命名文档 | `/api/filetree/renameDocByID` |
| 设置属性 | `/api/attr/setBlockAttrs` |
| 删除代码块 | `/api/block/deleteBlock` |
| 删除文档 | `/api/filetree/removeDocByID` |
| 导出为 Markdown 格式 | `/api/export/exportMdContent` |

## 常见操作

### 搜索（全文）

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/search/fullTextSearchBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "meeting notes", "page": 0}' | jq '.data.blocks[:5]'
```

### 搜索（SQL）

直接查询区块数据库。仅 SELECT 语句是安全的。

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/query/sql" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stmt": "SELECT id, content, type, box FROM blocks WHERE content LIKE '\''%keyword%'\'' AND type='\''p'\'' LIMIT 20"}' | jq '.data'
```

常用字段包括：`id`、`parent_id`、`root_id`、`box`（笔记本编号）、`path`、`content`、`type`、`subtype`、`created`、`updated`。

### 读取块内容

以 Kramdown（类似 Markdown 的格式）返回块内容。

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/getBlockKramdown" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data.kramdown'
```

### 阅读子块内容

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/getChildBlocks" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data'
```

### 获取人类可读的路径

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/getHPathByID" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data'
```

### 获取块属性

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/attr/getBlockAttrs" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "20210808180117-6v0mkxr"}' | jq '.data'
```

### 列出笔记本

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/notebook/lsNotebooks" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.data.notebooks[] | {id, name, closed}'
```

### 列出笔记本中的文档

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/listDocsByPath" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notebook": "NOTEBOOK_ID", "path": "/"}' | jq '.data.files[] | {id, name}'
```

### 创建文档

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/createDocWithMd" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notebook": "NOTEBOOK_ID",
    "path": "/Meeting Notes/2026-03-22",
    "markdown": "# Meeting Notes\n\n- Discussed project timeline\n- Assigned tasks"
  }' | jq '.data'
```

### 创建笔记本

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/notebook/createNotebook" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My New Notebook"}' | jq '.data.notebook.id'
```

### 向文档添加块内容

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/appendBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parentID": "DOCUMENT_OR_BLOCK_ID",
    "data": "New paragraph added at the end.",
    "dataType": "markdown"
  }' | jq '.data'
```

此外还提供以下接口：`/api/block/prependBlock`（参数相同，用于在块开头插入内容）以及 `/api/block/insertBlock`（使用 `previousID` 而非 `parentID`，用于在指定块之后插入内容）。

### 更新块内容

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/updateBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "BLOCK_ID",
    "data": "Updated content here.",
    "dataType": "markdown"
  }' | jq '.data'
```

### 重命名文档

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/filetree/renameDocByID" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "DOCUMENT_ID", "title": "New Title"}'
```

### 设置块属性

自定义属性必须以 `custom-` 作为前缀：

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/attr/setBlockAttrs" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "BLOCK_ID",
    "attrs": {
      "custom-status": "reviewed",
      "custom-priority": "high"
    }
  }'
```

### 删除块

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/block/deleteBlock" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "BLOCK_ID"}'
```

要删除整个文档：请使用 `/api/filetree/removeDocByID`，并传入参数 `{"id": "DOC_ID"}`。
要删除笔记本：请使用 `/api/notebook/removeNotebook`，并传入参数 `{"notebook": "NOTEBOOK_ID"}`。

### 将文档导出为 Markdown 格式

```bash
curl -s -X POST "${SIYUAN_URL:-http://127.0.0.1:6806}/api/export/exportMdContent" \
  -H "Authorization: Token $SIYUAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "DOCUMENT_ID"}' | jq -r '.data.content'
```

## 块类型

SQL 查询中常见的 `type` 值如下：

| 类型 | 描述 |
|------|-------------|
| `d` | 文档（根块） |
| `p` | 段落 |
| `h` | 标题 |
| `l` | 列表 |
| `i` | 列表项 |
| `c` | 代码块 |
| `m` | 数学公式块 |
| `t` | 表格 |
| `b` | 引用块 |
| `s` | 超级块 |
| `html` | HTML 块 |

## 常见问题

- **所有接口均为 POST 请求**——即便是只读操作也是如此。请勿使用 GET 请求。
- **SQL 安全性**：仅可使用 SELECT 查询。INSERT/UPDATE/DELETE/DROP 等操作存在风险，绝不可发送。
- **ID 格式验证**：ID 需符合 `YYYYMMDDHHmmss-xxxxxxx` 的格式，其他格式的 ID 均会被拒绝。
- **错误响应处理**：在处理 `data` 之前，务必先检查响应中的 `code` 是否不等于 0。
- **大型文档**：块内容及导出结果可能体积庞大。建议在 SQL 查询中使用 `LIMIT` 限制数据量，并通过 `jq` 工具提取所需内容。
- **笔记本 ID**：在操作特定笔记本时，需先通过 `lsNotebooks` 获取其 ID。

## 替代方案：MCP 服务器

如果您更倾向于使用原生集成而非 curl，可以安装 SiYuan MCP 服务器：

```yaml
# In ~/.hermes/config.yaml under mcp_servers:
mcp_servers:
  siyuan:
    command: npx
    args: ["-y", "@porkll/siyuan-mcp"]
    env:
      SIYUAN_TOKEN: "your_token"
      SIYUAN_URL: "http://127.0.0.1:6806"
```
