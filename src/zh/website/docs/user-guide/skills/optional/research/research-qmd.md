---
title: "Qmd"
sidebar_label: "Qmd"
description: "Search personal knowledge bases, notes, docs, and meeting transcripts locally using qmd — a hybrid retrieval engine with BM25, vector search, and LLM reranking"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Qmd

Qmd 是一款融合了 BM25、向量搜索以及大语言模型重排技术的混合检索引擎，可帮助用户在本地搜索个人知识库、笔记、文档及会议记录。该工具同时支持命令行界面使用和 MCP 集成。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 通过 `hermes skills install official/research/qmd` 安装 |
| 路径 | `optional-skills/research/qmd` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent + Teknium |
| 许可协议 | MIT |
| 支持平台 | macos、linux |
| 标签 | `搜索`、`知识库`、`RAG`、`笔记`、`MCP`、`本地 AI` |
| 相关技能 | [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian)、[`native-mcp`](/docs/user-guide/skills/bundled/mcp/mcp-native-mcp)、[`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能启用后，智能体将依据这些内容执行操作。
:::

# QMD —— 查询标记文档工具

这是一款用于个人知识库的本地端搜索引擎。它能够对 Markdown 笔记、会议记录、文档以及各类文本文件进行索引，进而通过结合关键词匹配、语义理解以及大语言模型驱动的重排技术来实现混合搜索——所有操作均在本地完成，无需依赖云端服务。

该工具由 [Tobi Lütke](https://github.com/tobi/qmd) 开发，采用 MIT 许可协议。

## 适用场景

- 用户希望搜索自己的笔记、文档、知识库或会议记录
- 用户需要在大量 Markdown/文本文件中查找特定内容
- 用户需要语义搜索（例如“查找与 X 概念相关的笔记”），而不仅仅是关键词匹配
- 用户已搭建好 Qmd 文档集合并希望对其进行查询
- 用户希望搭建本地知识库或文档搜索系统
- 相关关键词：“搜索我的笔记”、“在文档中查找内容”、“知识库”、“QMD”

## 先决条件

### 需要 Node.js 22 及以上版本（必需）

```bash
# Check version
node --version  # must be >= 22

# macOS — install or upgrade via Homebrew
brew install node@22

# Linux — use NodeSource or nvm
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
# or with nvm:
nvm install 22 && nvm use 22
```

### 支持扩展的 SQLite（仅限 macOS）

macOS 系统自带的 SQLite 不支持加载扩展。建议通过 Homebrew 进行安装：

```bash
brew install sqlite
```

### 安装 qmd

```bash
npm install -g @tobilu/qmd
# or with Bun:
bun install -g @tobilu/qmd
```

首次运行时会自动下载3个本地的GGUF模型（总大小约2GB）：

| 模型名称 | 功能用途 | 大小 |
|---------|---------|------|
| embeddinggemma-300M-Q8_0 | 向量嵌入 | 约300MB |
| qwen3-reranker-0.6b-q8_0 | 结果重排 | 约640MB |
| qmd-query-expansion-1.7B | 查询扩展 | 约1.1GB |

### 验证安装情况

```bash
qmd --version
qmd status
```

## 快速参考

| 命令 | 功能说明 | 执行速度 |
|---------|-----------|---------|
| `qmd search "查询词"` | 基于BM25的关键词搜索（不使用模型） | 约0.2秒 |
| `qmd vsearch "查询词"` | 语义向量搜索（使用1个模型） | 约3秒 |
| `qmd query "查询词"` | 混合检索+重排机制（使用全部3个模型） | 热启动状态约2-3秒，冷启动状态约19秒 |
| `qmd get <docid>` | 获取完整文档内容 | 即时完成 |
| `qmd multi-get "glob"` | 获取多个文件 | 即时完成 |
| `qmd collection add <路径> --name <名称>` | 将目录添加为集合 | 即时完成 |
| `qmd context add <路径> "描述信息"` | 添加上下文元数据以提升检索效果 | 即时完成 |
| `qmd embed` | 生成/更新向量嵌入 | 时间不定 |
| `qmd status` | 显示索引状态及集合信息 | 即时完成 |
| `qmd mcp` | 启动MCP服务器（标准输入输出方式） | 持续运行 |
| `qmd mcp --http --daemon` | 启动MCP服务器（HTTP协议，使用热启动模型） | 持续运行 |

## 设置流程

### 1. 添加集合

将qmd指令指向存放文档的目录：

```bash
# Add a notes directory
qmd collection add ~/notes --name notes

# Add project docs
qmd collection add ~/projects/myproject/docs --name project-docs

# Add meeting transcripts
qmd collection add ~/meetings --name meetings

# List all collections
qmd collection list
```

### 2. 添加上下文描述

上下文元数据有助于搜索引擎理解每个集合中包含的内容。这能够显著提升检索质量：

```bash
qmd context add qmd://notes "Personal notes, ideas, and journal entries"
qmd context add qmd://project-docs "Technical documentation for the main project"
qmd context add qmd://meetings "Meeting transcripts and action items from team syncs"
```

### 3. 生成嵌入向量

```bash
qmd embed
```

该功能会处理所有集合中的所有文档，并生成向量嵌入。在添加新文档或新集合后，请重新运行此操作。

### 4. 验证

```bash
qmd status   # shows index health, collection stats, model info
```

## 搜索模式

### 快速关键词搜索（BM25）

适用场景：精确术语、代码标识符、名称及已知短语。
无需加载任何模型——可实现近乎即时的搜索结果。

```bash
qmd search "authentication middleware"
qmd search "handleError async"
```

### 语义向量搜索

适用场景：自然语言提问、概念化查询。
需加载嵌入模型（首次查询耗时约3秒）。

```bash
qmd vsearch "how does the rate limiter handle burst traffic"
qmd vsearch "ideas for improving onboarding flow"
```

### 带重排功能的混合搜索（最佳质量）

适用场景：对查询质量要求极高的重要查询。
该模式会同时运用三种模型——查询扩展、并行BM25+向量检索以及重排算法。

```bash
qmd query "what decisions were made about the database migration"
```

### 结构化多模式查询

在单个查询中整合多种搜索类型，从而提升查询精度：

```bash
# BM25 for exact term + vector for concept
qmd query $'lex: rate limiter\nvec: how does throttling work under load'

# With query expansion
qmd query $'expand: database migration plan\nlex: "schema change"'
```

### 查询语法（lex/BM25 模式）

| 语法 | 效果 | 示例 |
|------|------|---------|
| `term` | 前缀匹配 | `perf` 可匹配 “performance” |
| `"phrase"` | 完整短语匹配 | `"rate limiter"` |
| `-term` | 排除特定词项 | `performance -sports` |

### HyDE（假设性文档嵌入模型）

针对复杂主题，可直接描述期望的答案形式：

```bash
qmd query $'hyde: The migration plan involves three phases. First, we add the new columns without dropping the old ones. Then we backfill data. Finally we cut over and remove legacy columns.'
```

### 将范围限定在集合中

```bash
qmd search "query" --collection notes
qmd query "query" --collection project-docs
```

### 输出格式

```bash
qmd search "query" --json        # JSON output (best for parsing)
qmd search "query" --limit 5     # Limit results
qmd get "#abc123"                # Get by document ID
qmd get "path/to/file.md"       # Get by file path
qmd get "file.md:50" -l 100     # Get specific line range
qmd multi-get "journals/*.md" --json  # Batch retrieve by glob
```

## MCP 集成（推荐方式）

qmd 提供了一个 MCP 服务器，可通过内置的 MCP 客户端将搜索工具直接提供给 Hermes Agent。这是最理想的集成方案——一旦完成配置，Agent 就能自动使用 qmd 的工具，而无需加载相应的技能。

### 方案 A：Stdio 模式（简单版）

在 `~/.hermes/config.yaml` 中添加以下内容：

```yaml
mcp_servers:
  qmd:
    command: "qmd"
    args: ["mcp"]
    timeout: 30
    connect_timeout: 45
```

此操作用于注册以下工具：`mcp_qmd_search`、`mcp_qmd_vsearch`、`mcp_qmd_deep_search`、`mcp_qmd_get`以及`mcp_qmd_status`。

**权衡点：** 每次执行搜索请求时都会加载模型（冷启动时间约19秒），但在会话期间模型会保持激活状态。这种方式适用于偶尔使用的情况。

### 方案B：HTTP守护进程模式（速度更快，适合高频使用）

单独启动qmd守护进程——该进程可将模型保留在内存中以保持活跃状态：

```bash
# Start daemon (persists across agent restarts)
qmd mcp --http --daemon

# Runs on http://localhost:8181 by default
```

接着，配置 Hermes Agent 通过 HTTP 进行连接：

```yaml
mcp_servers:
  qmd:
    url: "http://localhost:8181/mcp"
    timeout: 30
```

**权衡点：** 运行时需占用约2GB内存，但每个查询的响应速度都很快（约2-3秒），非常适合频繁搜索的用户。

### 保持守护进程运行

#### macOS（launchd）

```bash
cat > ~/Library/LaunchAgents/com.qmd.daemon.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.qmd.daemon</string>
  <key>ProgramArguments</key>
  <array>
    <string>qmd</string>
    <string>mcp</string>
    <string>--http</string>
    <string>--daemon</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/qmd-daemon.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/qmd-daemon.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.qmd.daemon.plist
```

#### Linux（systemd用户服务）

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/qmd-daemon.service << 'EOF'
[Unit]
Description=QMD MCP Daemon
After=network.target

[Service]
ExecStart=qmd mcp --http --daemon
Restart=on-failure
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now qmd-daemon
systemctl --user status qmd-daemon
```

### MCP 工具参考

连接成功后，这些工具将以 `mcp_qmd_*` 的形式提供：

| MCP 工具 | 对应功能 | 描述 |
|----------|---------|-------------|
| `mcp_qmd_search` | `qmd search` | 基于 BM25 的关键词搜索 |
| `mcp_qmd_vsearch` | `qmd vsearch` | 语义向量搜索 |
| `mcp_qmd_deep_search` | `qmd query` | 混合搜索与重排序机制 |
| `mcp_qmd_get` | `qmd get` | 根据 ID 或路径获取文档 |
| `mcp_qmd_status` | `qmd status` | 检索索引的健康状况及统计信息 |

这些 MCP 工具支持使用结构化的 JSON 查询来实现多模式搜索：

```json
{
  "searches": [
    {"type": "lex", "query": "authentication middleware"},
    {"type": "vec", "query": "how user login is verified"}
  ],
  "collections": ["project-docs"],
  "limit": 10
}
```

## CLI 使用方式（不使用 MCP）

当未配置 MCP 时，可直接通过终端使用 qmd 命令：

```
terminal(command="qmd query 'what was decided about the API redesign' --json", timeout=30)
```

进行设置与管理操作时，请始终使用终端：

```
terminal(command="qmd collection add ~/Documents/notes --name notes")
terminal(command="qmd context add qmd://notes 'Personal research notes and ideas'")
terminal(command="qmd embed")
terminal(command="qmd status")
```

## 搜索流程的工作原理

了解其内部机制有助于选择合适的搜索模式：

1. **查询扩展** — 一个经过微调的17亿参数模型会生成2个替代查询。在结果融合阶段，原始查询的权重为其他查询的两倍。
2. **并行检索** — BM25（SQLite FTS5）与向量搜索会同时对所有查询变体进行检索。
3. **RRF融合** — 互斥排名融合算法（k=60）用于合并检索结果。排名奖励机制：第一名加0.05分，第二至第三名各加0.02分。
4. **LLM重排** — qwen3-reranker会对前30个候选结果进行评分（评分范围0.0-1.0）。
5. **位置感知混合** — 前3名的权重分配为：75%来自检索结果，25%来自重排结果；第4至10名的权重比为60/40；第11名及以后的权重比为40/60（针对长尾查询，更依赖重排结果）。

**智能分块**：文档会在自然断点处（标题、代码块、空行）被分割，每个分块长度约为900个令牌，且各分块之间有15%的重叠度。代码块绝不会在中间被拆分。

## 最佳实践

1. **始终添加上下文描述** — 使用`qmd context add`可显著提升检索精度。需明确说明每个集合包含的内容。
2. **添加文档后需重新嵌入向量** — 当向集合中添加新文件时，必须重新运行`qmd embed`命令。
3. **需快速查找时使用`qmd search`** — 对于需要快速检索关键词（如代码标识符、精确名称）的场景，BM25检索即刻完成且无需依赖模型。
4. **追求高质量结果时使用`qmd query`** — 当查询涉及概念性内容或用户需要最佳结果时，建议使用混合搜索模式。
5. **优先采用MCP集成方式** — 一旦配置完成，智能体即可直接使用原生工具，无需每次都加载该搜索技能。
6. **高频使用者可选择守护进程模式** — 如果用户经常检索知识库，建议采用HTTP守护进程设置。
7. **在结构化搜索中，第一个查询的权重为两倍** — 在结合词条检索与向量检索时，应将最重要或最确定的查询放在首位。

## 故障排除

### “首次运行时正在下载模型”
这是正常现象——qmd会在首次使用时自动下载约2GB的GGUF模型文件。此操作仅执行一次。

### 冷启动延迟（约19秒）
出现此情况是因为模型尚未加载到内存中。解决方法包括：
- 使用HTTP守护进程模式（`qmd mcp --http --daemon`）以保持模型处于活跃状态；
- 当无需使用模型时，可使用仅支持BM25检索的`qmd search`命令；
- MCP标准输入输出模式会在首次搜索时加载模型，并在整个会话期间保持模型活跃状态。

### macOS系统：“无法加载扩展”
请先安装Homebrew版本的SQLite：`brew install sqlite`，然后确保其路径在系统SQLite之前被系统识别。

### “未找到任何集合”
请运行`qmd collection add <路径> --name <名称>`命令添加目录，随后执行`qmd embed`为这些目录建立索引。

### 嵌入模型自定义（针对中文/多语言内容）
对于非英文内容，可设置`QMD_EMBED_MODEL`环境变量来指定对应的嵌入模型。
```bash
export QMD_EMBED_MODEL="your-multilingual-model"
```

## 数据存储

- **索引与向量数据：** `~/.cache/qmd/index.sqlite`
- **模型文件：** 首次运行时会自动下载到本地缓存中
- **无需依赖云端服务** —— 所有操作均在本地完成

## 参考资料

- [GitHub: tobi/qmd](https://github.com/tobi/qmd)
- [QMD 更新日志](https://github.com/tobi/qmd/blob/main/CHANGELOG.md)
