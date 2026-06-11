# Notion 块类型

通过 API 创建和读取所有常见 Notion 块类型的参考文档。

## 创建块

使用 `PATCH /v1/blocks/{page_id}/children` 接口，并传入 `children` 数组。每个块均遵循以下结构：

```json
{"object": "block", "type": "<type>", "<type>": { ... }}
```

### 段落

```json
{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello world"}}]}}
```

### 标题

```json
{"type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "Title"}}]}}
{"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Section"}}]}}
{"type": "heading_3", "heading_3": {"rich_text": [{"text": {"content": "Subsection"}}]}}
```

### 项目列表

```json
{"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Item"}}]}}
```

### 编号列表

```json
{"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"text": {"content": "Step 1"}}]}}
```

### 待办事项 / 复选框

```json
{"type": "to_do", "to_do": {"rich_text": [{"text": {"content": "Task"}}], "checked": false}}
```

### 引用/报价

```json
{"type": "quote", "quote": {"rich_text": [{"text": {"content": "Something wise"}}]}}
```

### 重要提示

```json
{"type": "callout", "callout": {"rich_text": [{"text": {"content": "Important note"}}], "icon": {"emoji": "💡"}}}
```

### 代码

```json
{"type": "code", "code": {"rich_text": [{"text": {"content": "print('hello')"}}], "language": "python"}}
```

### 切换开关

```json
{"type": "toggle", "toggle": {"rich_text": [{"text": {"content": "Click to expand"}}]}}
```

### 分隔线

```json
{"type": "divider", "divider": {}}
```

### 收藏

```json
{"type": "bookmark", "bookmark": {"url": "https://example.com"}}
```

### 图像（外部链接）

```json
{"type": "image", "image": {"type": "external", "external": {"url": "https://example.com/photo.png"}}}
```

## 读取块数据

通过 `GET /v1/blocks/{page_id}/children` 接口获取块数据时，每个块都包含一个 `type` 字段。可按如下方式提取可读文本：

| 类型 | 文本所在位置 | 其他字段 |
|------|--------------|----------|
| `paragraph` | `.paragraph.rich_text` | — |
| `heading_1/2/3` | `.heading_N.rich_text` | — |
| `bulleted_list_item` | `.bulleted_list_item.rich_text` | — |
| `numbered_list_item` | `.numbered_list_item.rich_text` | — |
| `to_do` | `.to_do.rich_text` | `.to_do.checked`（布尔值） |
| `toggle` | `.toggle.rich_text` | 包含子元素 |
| `code` | `.code.rich_text` | `.code.language` |
| `quote` | `.quote.rich_text` | — |
| `callout` | `.callout.rich_text` | `.callout.icon.emoji` |
| `divider` | — | — |
| `image` | `.image.caption` | `.image.file.url` 或 `.image.external.url` |
| `bookmark` | `.bookmark.caption` | `.bookmark.url` |
| `child_page` | — | `.child_page.title` |
| `child_database` | — | `.child_database.title` |

若某个块包含富文本数组，则其中包含带有 `.plain_text` 字段的对象——需将这些内容拼接起来，才能生成可读的输出。

---

*由 [@dogiladeveloper](https://github.com/dogiladeveloper) 提供*
