---
title: "Llm Wiki — Karpathy's LLM Wiki: build/query interlinked markdown KB"
sidebar_label: "Llm Wiki"
description: "Karpathy's LLM Wiki: build/query interlinked markdown KB"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Llm Wiki

Karpathy 的 LLM Wiki：构建/查询相互关联的 Markdown 知识库。

## 技能元数据

| | |
|---|---|
| 来源 | 内置（默认已安装） |
| 路径 | `skills/research/llm-wiki` |
| 版本 | `2.1.0` |
| 创建者 | Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `wiki`、`knowledge-base`、`research`、`notes`、`markdown`、`rag-alternative` |
| 相关技能 | [`obsidian`](/docs/user-guide/skills/bundled/note-taking/note-taking-obsidian)、[`arxiv`](/docs/user-guide/skills/bundled/research/research-arxiv) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。当该技能处于激活状态时，智能体看到的指令即为内容。
:::

# Karpathy 的 LLM Wiki

以相互关联的 Markdown 文件形式构建并维护一个持久且不断扩充的知识库。
该功能基于 [Andrej Karpathy 的 LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)设计。

与传统 RAG（每次查询都需要从头重新检索知识）不同，该 Wiki 会一次性整合所有知识并保持其最新状态。其中的交叉引用早已设置完成，矛盾之处也会被标记出来，最终的综合结果能反映所有已收录的内容。

**分工协作：** 人类负责筛选资料并指导分析方向，而智能体则负责总结内容、建立交叉引用、整理文件并确保一致性。

## 何时使用此技能

在以下情况下可使用该技能：
- 用户要求创建、构建或启动一个 Wiki 或知识库
- 用户希望将新资料导入、添加到现有 Wiki 中或对其进行处理
- 用户提出问题，且配置路径下已存在相应的 Wiki
- 用户需要对其 Wiki 进行代码检查、审计或健康状况检测
- 用户在研究过程中提及自己的 Wiki、知识库或“笔记”

## Wiki 的存储位置

**位置：** 通过 `WIKI_PATH` 环境变量设置（例如在 `~/.hermes/.env` 文件中）。
若未设置该变量，则默认路径为 `~/wiki`。

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
```

该维基实际上只是一个存储 Markdown 文件的目录——您可以在 Obsidian、VS Code 或任何文本编辑器中打开它。无需数据库，也不需要任何特殊工具。

## 架构：三层结构

<!-- ascii-guard-ignore -->
```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams referenced by sources
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
└── queries/            # Layer 2: Filed query results worth keeping
```
**第一层——原始数据源：**不可更改。智能体仅会读取这些数据，而绝不会对其进行修改。
**第二层——维基内容：**由智能体管理的 Markdown 文件。这些文件由智能体创建、更新并建立相互引用关系。
**第三层——架构规范：**`SCHEMA.md` 文件用于定义结构、规范以及标签分类体系。

## 恢复现有的维基内容（非常重要——请在每次会话中执行此操作）

当用户已有现有维基内容时，**在采取任何操作之前务必先了解其结构**：

① **阅读 `SCHEMA.md`** — 了解相关领域、规范以及标签分类体系。
② **阅读 `index.md`** — 了解现有的页面及其概要。
③ **查看最近的 `log.md` 记录** — 阅读最近20-30条记录，以掌握近期活动动态。

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
# Orientation reads at session start
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<last 30 lines>
```

只有在完成定向设置之后，才应进行数据导入、查询或代码检查操作。这样做可以避免以下问题：
- 为已存在的实体创建重复页面
- 丢失对现有内容的交叉引用
- 违反架构规范
- 重复处理已记录过的工作

对于规模较大的维基（页面数超过100页），在创建新内容之前，还应先针对当前主题快速执行 `search_files` 操作。

## 初始化新维基

当用户请求创建或启动一个维基时，请按以下步骤操作：

1. 确定维基路径（可从 `$WIKI_PATH` 环境变量中获取，或询问用户；默认路径为 `~/wiki`）
2. 创建上述目录结构
3. 询问用户该维基涵盖的领域——请给出具体说明
4. 根据该领域编写定制化的 `SCHEMA.md` 文件（参见下方模板）
5. 编写包含分节标题的初始 `index.md` 文件
6. 编写包含创建记录的初始 `log.md` 文件
7. 确认维基已准备就绪，并推荐首批需要导入的资料来源

### SCHEMA.md 模板

需根据用户的领域进行相应调整。该架构能够约束智能体的行为，确保一致性：

```markdown
# Wiki Schema

## Domain
[What this wiki covers — e.g., "AI/ML research", "personal health", "startup intelligence"]

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- **Provenance markers:** On pages that synthesize 3+ sources, append `^[raw/articles/source-file.md]`
  at the end of paragraphs whose claims come from a specific source. This lets a reader trace each
  claim back without re-reading the whole raw file. Optional on single-source pages where the
  `sources:` frontmatter is enough.

## Frontmatter
  ```yaml
  ---
  title: Page Title
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: entity | concept | comparison | query | summary
  tags: [from taxonomy below]
  sources: [raw/articles/source-name.md]
  # Optional quality signals:
  confidence: high | medium | low        # how well-supported the claims are
  contested: true                        # set when the page has unresolved contradictions
  contradictions: [other-page-slug]      # pages this one conflicts with
  ---
  ```

`confidence`（置信度）和`contested`（争议性）字段虽为可选，但针对观点激烈或变化迅速的主题，建议使用这些字段。Lint工具会标记出`contested: true`且`confidence: low`的页面以便人工审核，从而防止站不住脚的论断悄然变成被广泛认可的维基事实。

### 原始内容/前置数据

原始来源也会包含一个简小的前置数据块，以便在重新导入时检测内容偏差：

```yaml
---
source_url: https://example.com/article   # original URL, if applicable
ingested: YYYY-MM-DD
sha256: &lt;hex digest of the raw content below the frontmatter>
---
```

`sha256:` 标记可用于在未来重新导入相同 URL 时，若内容未发生变化则跳过处理；一旦内容发生变动，则会标记出差异。该标记仅对内容主体（即 `---` 结尾之后的部分）进行计算，而不包括前端元数据本身。

## 标签分类体系
为该领域定义 10–20 个顶层标签。在使用新标签之前，请先将其添加至此列表中。

以人工智能/机器学习领域为例：
- 模型：model、architecture、benchmark、training
- 人物/机构：person、company、lab、open-source
- 技术方法：optimization、fine-tuning、inference、alignment、data
- 其他类别：comparison、timeline、controversy、prediction

规则：页面上的每个标签都必须出现在此分类体系中。如果需要新增标签，应先将其添加至此列表，然后再使用该标签。这样可以避免标签数量无序增长。

## 页面创建准则
- 当某个实体/概念在 2 个及以上来源中出现，或是一个来源的核心内容时，**创建新页面**
- 当某来源提及了已有页面已涵盖的内容时，**将该内容添加到现有页面中**
- 对于偶尔提及、细节无关的内容，或属于该领域之外的内容，**不要创建新页面**
- 当页面内容超过约 200 行时，**拆分页面**，通过交叉链接将不同子主题分开
- 当页面内容被完全替代时，**将其归档**，移至 `_archive/` 目录并从索引中删除

## 实体页面
每个重要实体对应一个页面。页面应包含以下内容：
- 概述/定义
- 关键事实与时间节点
- 与其他实体的关联关系（[[wikilinks]]）
- 参考来源

## 概念页面
每个概念或主题对应一个页面。页面应包含以下内容：
- 定义/解释
- 当前的认知状况
- 存在的疑问或争议点
- 相关概念（[[wikilinks]]）

## 对比页面
用于对不同事物进行并列分析。页面应包含：
- 对比的对象及对比原因
- 对比维度（建议以表格形式呈现）
- 对比结果或综合分析
- 参考来源

## 更新政策
当新信息与现有内容存在冲突时，应按以下步骤处理：
1. 检查日期——通常较新的来源信息会取代旧的信息
2. 如果确实存在矛盾，需同时记录两种观点，并注明对应的日期和来源
3. 在前端元数据中标记该矛盾：`contradictions: [页面名称]`
4. 在代码检查报告中标出该问题，以便用户审查
```

### index.md Template

The index is sectioned by type. Each entry is one line: wikilink + summary.

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total pages: N

## Entities
<!-- Alphabetical within section -->

## Concepts

## Comparisons

## Queries
```

**扩展规则：** 当任意一个分类下的条目数量超过50个时，应依据首字母或子域名将其拆分为多个子分类。而当整个索引的条目总数超过200个时，则需创建一个 `_meta/topic-map.md` 文件，按主题对页面进行归类，从而提升导航效率。

### log.md 模板

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, index.md, log.md
```

## 核心操作

### 1. 数据摄取

当用户提供来源内容（URL、文件或粘贴文本）时，需将其整合到维基中：

① **捕获原始来源内容：**
   - URL → 使用 `web_extract` 工具提取 Markdown 格式内容，并保存至 `raw/articles/` 目录
   - PDF → 同样使用 `web_extract`（该工具支持处理 PDF 文件），保存至 `raw/papers/` 目录
   - 粘贴的文本 → 保存到相应的 `raw/` 子目录中
   - 文件命名需具有描述性，例如：`raw/articles/karpathy-llm-wiki-2026.md`
   - **添加原始内容元数据**，包括 `source_url`、`ingested` 标识以及正文内容的 `sha256` 哈希值。当再次摄取相同 URL 的内容时，需重新计算该哈希值，并与已存储的值进行比对——若一致则跳过处理，若存在差异则标记为内容变化并更新记录。此操作在每次重新摄取时执行成本极低，却能有效检测到来源内容的隐性变动。

② **与用户讨论核心要点**——哪些内容值得关注，哪些对相关领域至关重要。（在自动化或定时任务场景下可跳过此步骤，直接进入后续流程。）

③ **检查已有内容**——搜索 `index.md` 文件，并使用 `search_files` 工具查找与提及实体或概念相关的现有页面。这正是不断完善的维基与大量重复内容之间的区别所在。

④ **编写或更新维基页面：**
   - **新实体/概念**：仅当其满足 `SCHEMA.md` 中规定的页面创建标准时才创建页面，即至少有2处来源提及，或为某个来源的核心内容
   - **现有页面**：补充新信息、更新事实内容，并更新 `updated` 时间戳。若新信息与现有内容存在矛盾，则需遵循相应的更新规则
   - **交叉引用**：每篇新建或更新的页面都必须通过 `[[wikilinks]]` 标签链接到至少2个其他页面，同时需确保现有页面也能反向链接回这些新页面
   - **标签使用**：仅可使用 `SCHEMA.md` 中定义的标签
   - **来源标注**：对于整合了3个以上来源内容的页面，需在所有引用特定来源信息的段落前添加 `^[raw/articles/source.md]` 标记
   - **置信度标注**：对于观点性较强、变化较快或仅基于单一来源的内容，应在元数据中将其置信度设置为 `medium` 或 `low`。除非某项主张能得到多个来源的充分支持，否则不应标记为 `high` 置信度

⑤ **更新导航结构：**
   - 将新页面按字母顺序添加到 `index.md` 的相应分类下
   - 更新索引页顶部的“总页面数”及“最后更新时间”
   - 在 `log.md` 文件中添加记录，格式为：`## [YYYY-MM-DD] ingest | Source Title`，并列出所有被创建或更新的文件

⑥ **向用户报告变更情况**——列出所有被创建或更新的文件。

单个来源内容通常会触发5到15个维基页面的更新，这是正常现象且符合预期，正是这种累积效应带来了知识的持续丰富。

### 2. 查询

当用户就维基涵盖的主题提出问题时：

① **读取 `index.md` 文件**，确定相关的页面。
② **对于页面数量超过100页的维基**，还需在所有 `.md` 文件中通过 `search_files` 工具搜索关键词——仅依赖索引可能遗漏相关内容。
③ **使用 `read_file` 工具读取相关页面的内容。**
④ **基于整合后的知识综合生成答案**，并注明所参考的维基页面，例如：“根据 [[page-a]] 和 [[page-b]] 的内容……”
⑤ **保存有价值的答案**——如果答案是对内容的深入对比、详细分析或创新性整合，可在 `queries/` 或 `comparisons/` 目录下创建专门页面；对于简单的查询结果，则无需保存，因为这类内容重新生成的成本较低。
⑥ **在 `log.md` 文件中记录此次查询内容以及是否已保存答案。**

### 3. 代码检查

当用户要求对维基进行代码检查、健康状态检测或审计时：

① **查找孤立页面**：即那些没有其他页面通过 `[[wikilinks]]` 标签链接进来的页面。
```python
# Use execute_code for this — programmatic scan across all wiki pages
import os, re
from collections import defaultdict
wiki = "<WIKI_PATH>"
# Scan all .md files in entities/, concepts/, comparisons/, queries/
# Extract all [[wikilinks]] — build inbound link map
# Pages with zero inbound links are orphans
```

② **失效的维基链接**：查找指向不存在页面的`[[links]]`链接。

③ **索引完整性**：每个维基页面都应出现在`index.md`中。需将文件系统内容与索引条目进行比对。

④ **前置数据验证**：每个维基页面必须包含所有必填字段（标题、创建时间、更新时间、类型、标签、来源）。标签必须属于既定的分类体系。

⑤ **过时内容**：那些`更新时间`比最新提及相同实体的来源内容早90天以上的页面。

⑥ **矛盾信息**：针对同一主题但存在相互冲突说法的页面。需找出那些虽共享相同标签/实体却陈述不同事实的页面，并将所有带有`contested: true`或`contradictions:`前置数据的页面列出，以便用户审核。

⑦ **质量信号识别**：列出`confidence: low`评分的页面，以及仅引用单一来源且未设置置信度字段的页面——这些页面需要进一步核实信息真实性，或将其置信度降级为`medium`。

⑧ **来源内容变动**：对于`raw/`目录中带有`sha256:`前置数据的每个文件，需重新计算其哈希值，并标记出不一致的情况。此类差异表明该原始文件可能已被修改（本不应发生，因为`raw/`目录中的文件是不可变的），或是从已变更地址获取的。这虽不属于严重错误，但仍值得上报。

⑨ **页面长度**：标记行数超过200行的页面——这些页面可能需要被拆分。

⑩ **标签审核**：列出所有正在使用的标签，并标记出那些不在`SCHEMA.md`分类体系中的标签。

⑪ **日志轮转**：当`log.md`中的记录数量超过500条时，需进行日志轮转。

⑫ **报告问题时**，需提供具体的文件路径及建议采取的措施，并按严重程度分类（失效链接 > 孤立页面 > 来源内容变动 > 存在矛盾的页面 > 过时内容 > 样式问题）。

⑬ **在`log.md`中记录**：格式为`## [YYYY-MM-DD] lint | 发现 N 个问题`

## 维基页面操作指南

### 搜索功能

```bash
# Find pages by content
search_files "transformer" path="$WIKI" file_glob="*.md"

# Find pages by filename
search_files "*.md" target="files" path="$WIKI"

# Find pages by tag
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# Recent activity
read_file "$WIKI/log.md" offset=<last 20 lines>
```

### 批量导入

在同时导入多个数据源时，应采用批量处理方式：
1. 首先读取所有数据源
2. 确定所有数据源中的所有实体和概念
3. 对这些实体和概念在现有页面中进行逐一查找（仅执行一次搜索，而非多次）
4. 一次性创建或更新相关页面（避免重复操作）
5. 最后统一更新 `index.md` 文件
6. 记录一次包含整个批量操作的日志条目

### 归档处理

当内容被完全替代或领域范围发生变化时：
1. 若不存在 `_archive/` 目录，则创建该目录
2. 将对应页面连同其原始路径一起移至 `_archive/` 目录中（例如：`_archive/entities/old-page.md`）
3. 从 `index.md` 中删除该页面的引用
4. 更新所有曾链接到该页面的页面——将维基链接替换为纯文本并加上 “(已归档)” 标注
5. 记录此次归档操作

### 与 Obsidian 的集成

该Wiki目录可直接作为Obsidian知识库使用：
- `[[wikilinks]]` 会显示为可点击的链接
- 图谱视图可用于可视化知识网络结构
- YAML前置数据可用于支持Dataview查询功能
- `raw/assets/` 文件夹用于存放通过 `![[image.png]]` 引用的图片

为获得最佳使用效果：
- 将Obsidian的附件存储路径设置为 `raw/assets/`
- 在Obsidian设置中开启“维基链接”功能（通常默认已开启）
- 安装Dataview插件，以便执行诸如 `TABLE tags FROM "entities" WHERE contains(tags, "company")` 这样的查询语句

如果同时使用Obsidian技能，需将 `OBSIDIAN_VAULT_PATH` 设置为与Wiki目录相同的路径。

### Obsidian无界面模式（服务器及无显示设备）

在无显示设备的机器上，应使用 `obsidian-headless` 而非桌面版应用。该工具可通过Obsidian Sync实现无图形界面的知识库同步——非常适合那些在服务器端写入内容、而通过另一台设备上的Obsidian桌面版读取内容的智能体场景。

**设置步骤：**
```bash
# Requires Node.js 22+
npm install -g obsidian-headless

# Login (requires Obsidian account with Sync subscription)
ob login --email <email> --password '<password>'

# Create a remote vault for the wiki
ob sync-create-remote --name "LLM Wiki"

# Connect the wiki directory to the vault
cd ~/wiki
ob sync-setup --vault "<vault-id>"

# Initial sync
ob sync

# Continuous sync (foreground — use systemd for background)
ob sync --continuous
```

**通过 systemd 实现持续后台同步：**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=/home/user/wiki
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# Enable linger so sync survives logout:
sudo loginctl enable-linger $USER
```

这样一来，当你在笔记本或手机上的 Obsidian 中浏览同一个知识库时，该智能体便可在服务器上的 `~/wiki` 目录中进行写入操作——更改内容会在几秒钟内显现出来。

## 常见误区

- **切勿修改 `raw/` 目录中的文件**——这些源数据是不可更改的，相关修正应通过维基页面来完成。
- **务必先了解结构**——在每次新会话开始执行任何操作前，都要先阅读 SCHEMA 文件、索引以及最近的日志。跳过此步骤会导致内容重复和交叉引用缺失。
- **必须及时更新 index.md 和 log.md**——忽视这一点会让维基系统功能退化，因为这两份文件是整个系统的导航核心。
- **不要为临时提及的内容创建页面**——需遵循 SCHEMA.md 中规定的页面创建标准。仅在脚注中出现一次的名称并不需要单独创建实体页面。
- **创建页面时必须添加交叉引用**——孤立的页面是无法被发现的，每个页面至少需要链接到另外两个页面。
- **必须使用前置信息**——它有助于实现搜索、过滤以及内容新鲜度检测。
- **标签必须来自预定义的分类体系**——随意使用的标签只会造成信息混乱。请先在 SCHEMA.md 中添加新标签，然后再加以使用。
- **保持页面易读性**——一个维基页面应在30秒内即可读完。建议将页面内容控制在200行以内，复杂分析内容可移至专门的深入探讨页面中。
- **大规模更新前请先询问**——如果某次数据导入会影响到10个以上的现有页面，请先与用户确认操作范围。
- **定期轮换日志文件**——当 log.md 的记录数超过500条时，将其重命名为 `log-YYYY.md` 并重新开始记录。智能体应在代码检查过程中检测日志大小。
- **明确处理矛盾内容**——切勿默默覆盖原有数据。应同时记录两种观点并标注日期，在前置信息中加以标记，以便用户审核。

## 相关工具

[llm-wiki-compiler](https://github.com/atomicmemory/llm-wiki-compiler) 是一个基于 Node.js 的命令行工具，它遵循与 Karpathy 系统相同的理念，可将各种源数据编译成概念维基。该工具兼容 Obsidian，因此那些希望使用定时或命令行驱动的编译流程的用户，可以将其指向与本智能体所维护的相同知识库。不过它的缺点是会完全掌控页面生成过程（取代了智能体对是否创建页面的判断），且更适合处理小型数据集。如果你需要智能体参与内容筛选，可使用此工具；而若想对整个源代码目录进行批量编译，则推荐使用 llmwiki。
