---
title: "Notion — Notion API + ntn CLI: pages, databases, markdown, Workers"
sidebar_label: "Notion"
description: "Notion API + ntn CLI: pages, databases, markdown, Workers"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Notion

Notion API + ntn CLI：支持页面、数据库、Markdown 内容以及 Workers 功能。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/productivity\notion` |
| 版本 | `2.0.0` |
| 开发者 | 社区贡献 |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Notion`、`生产力工具`、`笔记`、`数据库`、`API`、`CLI`、`Workers` |

## 参考：完整 SKILL.md 内容

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# Notion

可通过两种方式与 Notion 进行交互。两种方式均使用相同的集成令牌——请根据实际可用情况选择。

◆ **`ntn` CLI** — Notion 官方命令行工具。语法更为简洁，支持单行文件上传，是 Workers 功能的必需项。截至 2026 年 5 月仅支持 macOS 和 Linux 系统（Windows 支持功能“即将推出”）。**安装时默认选用此方式。**
◆ **HTTP + curl** — 在所有系统上均可使用，包括 Windows。当未安装 `ntn` 时，**会自动回退至此方式。**

## 设置步骤

### 1. 获取集成令牌（两种使用方式均需）

1. 访问 https://notion.so/my-integrations 创建一个集成账户
2. 复制 API 密钥（以 `ntn_` 或 `secret_` 开头）
3. 将其存储在 `${HERMES_HOME:-~/.hermes}/.env` 文件中：
   ```
   NOTION_API_KEY=ntn_your_key_here
   ```
4. 在 Notion 中**将目标页面/数据库共享给该集成**：进入页面菜单，选择 `...` → `Connect to` → 选择对应的集成名称。若未执行此操作，即使页面实际存在，API 也会返回 404 错误。

### 2. 安装 `ntn`（macOS/Linux 系统的推荐安装路径）

```bash
# Recommended
curl -fsSL https://ntn.dev | bash

# Or via npm (needs Node 22+, npm 10+)
npm install --global ntn

ntn --version    # verify
```

**无需执行 `ntn login` 操作——可直接使用集成令牌。** 该方式支持无界面运行，无需浏览器即可使用。
```bash
export NOTION_API_TOKEN=$NOTION_API_KEY      # ntn reads NOTION_API_TOKEN
export NOTION_KEYRING=0                       # don't try to use the OS keychain
```

请将这些导出项添加到您的 shell 配置文件中（或 `${HERMES_HOME:-~/.hermes}/.env` 文件中），这样每个会话都能继承这些设置。

### 3. 运行时选择路径

```bash
if command -v ntn >/dev/null 2>&1; then
  # use ntn
else
  # fall back to curl
fi
```

Windows用户：在原生`ntn`版本发布之前，可直接跳过第2步——路径B同样可行。若您希望立即体验更便捷的CLI操作，可在WSL2环境中安装`ntn`。

## API基础

所有HTTP请求都必须包含`Notion-Version: 2025-09-03`这一字段。`ntn`会自动为您处理此项设置。在此版本中，用户所称的“数据库”在API中被称为**数据源**。

## 路径A — `ntn` CLI（推荐，适用于macOS/Linux）

### 原生API调用（即curl的简写形式）
```bash
ntn api v1/users                                  # GET
ntn api v1/pages parent[page_id]=abc123 \         # POST with inline body
  properties[title][0][text][content]="Notes"
ntn api v1/pages/abc123 -X PATCH archived:=true   # PATCH; := is non-string (bool/num/null)
```

语法说明：  
- `key=value` — 字符串类型字段  
- `key[nested]=value` — 嵌套对象字段  
- `key:=value` — 类型化赋值（布尔值、数字、null、数组）  

### 搜索功能
```bash
ntn api v1/search query="page title"
```

### 查看页面元数据
```bash
ntn api v1/pages/{page_id}
```

### 以 Markdown 格式读取页面（适配智能体使用）
```bash
ntn api v1/pages/{page_id}/markdown
```

### 按块读取页面内容
```bash
ntn api v1/blocks/{page_id}/children
```

### 从 Markdown 创建页面
```bash
ntn api v1/pages \
  parent[page_id]=xxx \
  properties[title][0][text][content]="Notes from meeting" \
  markdown="# Agenda

- Q3 roadmap
- Hiring"
```

### 使用 Markdown 修复页面内容
```bash
ntn api v1/pages/{page_id}/markdown -X PATCH \
  markdown="## Update

Shipped the prototype."
```

### 查询数据库（数据源）
```bash
ntn api v1/data_sources/{data_source_id}/query -X POST \
  filter[property]=Status filter[select][equals]=Active
```

对于包含排序、多个过滤条件或复合逻辑的复杂查询，可通过管道符传递 JSON 数据：
```bash
echo '{"filter": {"property": "Status", "select": {"equals": "Active"}}, "sorts": [{"property": "Date", "direction": "descending"}]}' | \
  ntn api v1/data_sources/{data_source_id}/query -X POST --json -
```

### 文件上传功能（一行命令即可完成——CLI领域的重大突破）
```bash
ntn files create < photo.png
ntn files create --external-url https://example.com/photo.png
ntn files list
```

与三步HTTP流程（创建上传 → PUT数据字节 → 获取引用）相比。

### 有用的环境变量
| 变量 | 效果 |
|---|---|
| `NOTION_API_TOKEN` | 认证令牌（优先于钥匙串）——请将其设置为您的集成令牌 |
| `NOTION_KEYRING=0` | 使用位于`~/.config/notion/auth.json`中的基于文件的凭证，而非操作系统钥匙串 |
| `NOTION_WORKSPACE_ID` | 跳过工作空间选择提示 |

## 方案B — HTTP + curl（跨平台，Windows默认方案）

所有请求均遵循以下模式：

```bash
curl -s -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

在 Windows 系统上，Windows 10 及更高版本自带的 `curl` 工具可直接使用。PowerShell 用户则可以选择使用 `Invoke-RestMethod` 命令。
```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'
```

### 读取页面元数据
```bash
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 以 Markdown 格式读取页面（更适用于智能体）

相比块级 JSON，这种格式更易于输入至模型中。

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 以块的形式读取页面内容（当需要结构化处理时）
```bash
curl -s "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### 从 Markdown 创建页面

`POST /v1/pages` 接受 `markdown` 类型的请求体参数。

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "properties": {"title": [{"text": {"content": "Notes from meeting"}}]},
    "markdown": "# Agenda\n\n- Q3 roadmap\n- Hiring\n\n## Decisions\n- Ship MVP Friday"
  }'
```

### 使用 Markdown 修复页面内容
```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}/markdown" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"markdown": "## Update\n\nShipped the prototype."}'
```

### 在数据库中创建页面（带类型属性）
```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}}
    }
  }'
```

### 查询数据库（数据源）
```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'
```

### 创建数据库
```bash
curl -s -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "title": [{"text": {"content": "My Database"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
      "Date": {"date": {}}
    }
  }'
```

### 更新页面属性
```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

### 向页面添加块内容
```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello from Hermes!"}}]}}
    ]
  }'
```

### 文件上传（三步流程）
```bash
# 1. Create upload
curl -s -X POST "https://api.notion.com/v1/file_uploads" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"filename": "photo.png", "content_type": "image/png"}'

# 2. PUT bytes to the upload_url returned above
curl -s -X PUT "{upload_url}" --data-binary @photo.png

# 3. Reference {file_upload_id} in a page/block payload
```

## 属性类型

数据库项常用的属性格式如下：

- **标题：** `{"title": [{"text": {"content": "..."}}]}`
- **富文本：** `{"rich_text": [{"text": {"content": "..."}}]}`
- **单选：** `{"select": {"name": "选项值"}}`
- **多选：** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **日期：** `{"date": {"start": "2026-01-15", "end": "2026-01-16"}}`
- **复选框：** `{"checkbox": true}`
- **数字：** `{"number": 42}`
- **URL：** `{"url": "https://..."}`
- **邮箱：** `{"email": "user@example.com"}`
- **关联关系：** `{"relation": [{"id": "page_id"}]}`

## API版本 2025-09-03 — 数据库与数据源的变更

- **数据库现已转变为数据源。** 请使用 `/data_sources/` 接口进行查询和检索操作。
- **每个数据库拥有两个标识符：** `database_id` 和 `data_source_id`。
  - 创建页面时使用 `database_id`：`parent: {"database_id": "..."}`
  - 执行查询时使用 `data_source_id`：`POST /v1/data_sources/{id}/query`
- 搜索结果中，数据库将以 `"object": "data_source"` 的形式返回，并包含 `data_source_id` 字段。

## Notion Workers（高级功能，需使用 `ntn`）

Workers 是由 Notion 为你托管的 TypeScript 程序。一个 Worker 可以实现以下任意组合的功能：
- **同步功能**——按预定时间间隔（默认为30分钟）从外部 API 拉取数据并导入 Notion 数据库。
- **工具功能**——作为可调用工具出现在 Notion 的自定义 Agent 中。
- **Webhook 功能**——接收来自外部服务（如 GitHub、Stripe 等）的 HTTP 事件，并在 Notion 中执行相应操作。

**计划/平台限制：**
- 所有套餐均支持 CLI 使用。**部署 Worker 则需选择 Business 或 Enterprise 套餐。**
- 截至 2026 年 5 月，`ntn` 仅适用于 macOS 和 Linux 系统；Windows 用户需使用 WSL2，或等待其获得原生支持。
- 2026 年 8 月 11 日前可免费使用；之后将按 Notion 积分进行计费。

### 最小化 Worker

```bash
ntn workers new my-worker      # scaffold
cd my-worker
# Edit src/index.ts
ntn workers deploy --name my-worker
```

`src/index.ts`：
```typescript
import { Worker } from "@notionhq/workers";

const worker = new Worker();
export default worker;

worker.tool("greet", {
  title: "Greet a User",
  description: "Returns a friendly greeting",
  inputSchema: { type: "object", properties: { name: { type: "string" } }, required: ["name"] },
  execute: async ({ name }) => `Hello, ${name}!`,
});
```

### Webhook 功能

```typescript
worker.webhook("onGithubPush", {
  title: "GitHub Push Handler",
  execute: async (events, { notion }) => {
    for (const event of events) {
      // event.body, event.rawBody (for signature verification), event.headers
      console.log("got delivery", event.deliveryId);
    }
  },
});
```

部署完成后，执行 `ntn workers webhooks list` 命令即可查看 Notion 生成的 URL。请将此 URL 视为机密信息——除非您启用了签名验证，否则任何拥有该 URL 的人都能发送事件。

### Worker 生命周期相关命令

```bash
ntn workers deploy
ntn workers list
ntn workers exec <capability-key> -d '{"name": "world"}'
ntn workers sync trigger <key>            # run a sync now
ntn workers sync pause <key>
ntn workers env set GITHUB_WEBHOOK_SECRET=...
ntn workers runs list                     # recent invocations
ntn workers runs logs <run-id>
ntn workers webhooks list
```

当需要构建 Worker 时，可使用 `ntn workers new` 命令生成项目模板，在 `src/index.ts` 文件中编写代码，通过 `ntn workers env set` 设置相关机密信息，最后进行部署。Notion 的完整 API 文档详见 https://developers.notion.com/workers。

## Notion 风格的 Markdown（用于 `/markdown` 接口）

在标准 CommonMark 的基础上增加了类似 XML 的标签，用于表示 Notion 特有的块结构。缩进请使用**制表符**。

**CommonMark 之外的块结构：**
```
<callout icon="🎯" color="blue_bg">
	Ship the MVP by **Friday**.
</callout>

<details color="gray">
<summary>Toggle title</summary>
	Children indented one tab
</details>

<columns>
	<column>Left side</column>
	<column>Right side</column>
</columns>

<table_of_contents color="gray"/>
```

**内联格式：**
- 提及用户：`<mention-user url="..."/>`、`<mention-page url="...">标题</mention-page>`、`<mention-date start="2026-05-15"/>`
- 下划线文本：`<span underline="true">文本</span>`
- 颜色文本：`<span color="blue">文本</span>`；若需首行应用颜色，则使用块级格式 `{color="blue"}` 
- 数学公式：内联格式为 `$x^2 $`，块级格式为 `$$ ... $$`
- 引用标注：`[^https://example.com]`

**可用颜色：** `gray brown orange yellow green blue purple pink red`，此外还提供用于背景色的 `*_bg` 变体。

层级为5级或6级的标题会自动折叠为H4级别。多个 `>` 符号行将被视为独立的引号块——如需多行引文，可在单个 `>` 内使用 `<br>` 标签换行。

## 选择合适方案

| 任务 | mac / Linux | Windows |
|---|---|---|
| 读取/写入页面、搜索、查询数据库 | `ntn api ...` | curl |
| 为智能体读取页面以便总结内容 | `ntn api v1/pages/{id}/markdown` | 使用 curl 调用 `/markdown` 接口 |
| 上传文件 | `ntn files create < 文件名>` | 需经过三步的HTTP流程 |
| 临时测试API功能 | `ntn api ...` | curl |
| 构建由Notion托管的同步工具、Webhook或智能体应用 | `ntn workers ...` | 使用WSL2环境结合 `ntn workers ...` |

## 备注

- 页面/数据库的 ID 均为 UUID 格式（可带连字符，也可不带，两种形式均可接受）。  
- 请求速率限制：平均约为每秒 3 次请求。CLI 工具也无法绕过此限制。  
- API 无法设置数据库**视图**的筛选条件——该功能仅限于用户界面操作。  
- 在创建数据源时，请使用 `"is_inline": true` 以便将其嵌入到页面中。  
- 使用 curl 时务必加上 `-s` 参数以隐藏进度条，从而获得更整洁的代理输出。  
- 读取数据时可通过 `jq` 处理 JSON 格式的内容：`... | jq '.results[0].properties'`。  
- Notion 现已内置 MCP 服务器（即“Notion MCP”），其在执行数据库操作时的令牌使用效率比旧版本高出约 91%。若希望在会话中实现实时访问 Notion 的功能，可通过 Hermes 的 MCP 支持进行连接；不过对于大多数一次性任务，上述路径就已足够使用。
