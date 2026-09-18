---
sidebar_position: 8
title: "Context Files"
description: "Project context files — .hermes.md, AGENTS.md, CLAUDE.md, global SOUL.md, and .cursorrules — automatically injected into every conversation"
---

# 上下文文件

Hermes Agent 会自动发现并加载那些决定其行为方式的上下文文件。其中一些文件位于项目本地，可从当前工作目录中找到。而 `SOUL.md` 则属于整个 Hermes 实例的全局配置，仅从 `HERMES_HOME` 路径加载。

## 支持的上下文文件

| 文件名 | 用途 | 发现路径 |
|--------|------|----------|
| **.hermes.md** / **HERMES.md** | 项目相关指令（优先级最高） | 从 Git 根目录开始查找 |
| **AGENTS.override.md** | 对 AGENTS.md 的个人化、目录级覆盖配置（通常被标记为 gitignored） | 启动时从当前工作目录开始，逐步向下查找子目录 |
| **AGENTS.md** | 项目指令、规范及架构定义 | 启动时从当前工作目录开始，逐步向下查找子目录 |
| **CLAUDE.md** | Claude Code 的上下文文件（也会被自动检测） | 启动时从当前工作目录开始，逐步向下查找子目录 |
| **SOUL.md** | 为该 Hermes 实例定制全局性格与语气设置 | 仅从 `HERMES_HOME/SOUL.md` 路径加载 |
| **.cursorrules** | Cursor IDE 的编码规范文件 | 仅从当前工作目录加载 |
| **.cursor/rules/*.mdc** | Cursor IDE 的规则模块文件 | 仅从当前工作目录加载 |

:::info 优先级机制
每个会话中仅会加载**一种**项目上下文类型（按顺序匹配，第一个匹配到的生效）：`.hermes.md` → `AGENTS.override.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。而 **SOUL.md** 始终会作为智能体身份配置独立加载（对应槽位 #1）。

如果 `AGENTS.md` 旁边存在 `AGENTS.override.md`，则系统会加载该覆盖文件，而非已提交到仓库的版本。当您希望使用与仓库中版本不同的配置指令，而又不想修改已被跟踪的 `AGENTS.md` 时，可以保留一个个人使用的（通常会被标记为 gitignored 的）`AGENTS.override.md` 文件。
:::

## AGENTS.md

`AGENTS.md` 是项目的主要上下文文件。它用于向智能体说明项目的结构、需遵循的规范以及任何特殊要求。

### 目录链（git 根目录 → 工作目录）

当工作目录位于 git 仓库中时，Hermes 在会话启动时会加载一系列合并后的 `AGENTS.md` 文件：首先是 git 根目录下的 `AGENTS.md`，接着是中间各个目录中的 `AGENTS.md`，直至最终的工作目录版本。层级较深的文件会在提示信息中显示得更靠后，因此更具体的配置指令会优先生效。每个文件都会带有自身的来源标识（例如 `## ../../AGENTS.md`），而路径相同的重复文件则会被去重处理。

```
monorepo/                   (git root, cwd = packages/webapp/)
├── AGENTS.md              ← Loaded first (repo-wide conventions)
└── packages/
    ├── AGENTS.md          ← Loaded second
    └── webapp/
        └── AGENTS.md      ← Loaded last (most specific, takes precedence)
```

在 Git 仓库之外，系统仅会检查当前工作目录的内容——不会递归查询上级目录，因此放置在 `/tmp` 或 `$HOME` 目录中的 `AGENTS.md` 文件不会泄露到其他无关的会话中。

### 逐步发现子目录

在会话开始时，Hermes 会将工作目录中的 `AGENTS.md` 文件加载到系统提示符中。当代理在会话过程中通过 `read_file`、`terminal`、`search_files` 等功能进入子目录时，它会**逐步发现**这些目录中的上下文文件，并在它们变得相关时将其注入对话中。

```
my-project/
├── AGENTS.md              ← Loaded at startup (system prompt)
├── frontend/
│   └── AGENTS.md          ← Discovered when agent reads frontend/ files
├── backend/
│   └── AGENTS.md          ← Discovered when agent reads backend/ files
└── shared/
    └── AGENTS.md          ← Discovered when agent reads shared/ files
```

与在启动时加载所有内容相比，这种方法具有两大优势：
- **避免系统提示信息臃肿**——仅在需要时才会显示子目录相关提示
- **保留提示缓存**——系统提示在多轮对话中保持稳定

每个子目录在单个会话中最多会被检查一次。该机制还会向上遍历父目录，因此即便 `backend/src/` 目录本身没有上下文文件，读取 `backend/src/main.py` 时也能发现 `backend/AGENTS.md`。

:::info
子目录中的上下文文件会与启动时的上下文文件一样经过[安全扫描](#security-prompt-injection-protection)，恶意文件会被拦截。
:::

### AGENTS.md 示例

```markdown
# Project Context

This is a Next.js 14 web application with a Python FastAPI backend.

## Architecture
- Frontend: Next.js 14 with App Router in `/frontend`
- Backend: FastAPI in `/backend`, uses SQLAlchemy ORM
- Database: PostgreSQL 16
- Deployment: Docker Compose on a Hetzner VPS

## Conventions
- Use TypeScript strict mode for all frontend code
- Python code follows PEP 8, use type hints everywhere
- All API endpoints return JSON with `{data, error, meta}` shape
- Tests go in `__tests__/` directories (frontend) or `tests/` (backend)

## Important Notes
- Never modify migration files directly — use Alembic commands
- The `.env.local` file has real API keys, don't commit it
- Frontend port is 3000, backend is 8000, DB is 5432
```

## SOUL.md

`SOUL.md` 用于控制智能体的性格特征、语气以及交流风格。详细内容请参阅 [性格设置](/user-guide/features/personality) 页面。

**位置：**

- `~/.hermes/SOUL.md`
- 若您使用自定义的 Hermes 安装目录，则为 `$HERMES_HOME/SOUL.md`

重要说明：

- 如果尚未存在 `SOUL.md`，Hermes 会自动创建一个默认版本
- Hermes 仅从 `HERMES_HOME` 目录加载 `SOUL.md` 文件
- Hermes 不会扫描当前工作目录以查找 `SOUL.md`
- 若该文件为空，则不会将其中的任何内容添加到提示语中
- 若文件包含内容，系统会在扫描并截断后原样将其注入提示语中

## .cursorrules

Hermes 兼容 Cursor IDE 的 `.cursorrules` 文件以及 `.cursor/rules/*.mdc` 规则模块。如果这些文件位于项目根目录中，且未找到优先级更高的上下文文件（如 `.hermes.md`、`AGENTS.md` 或 `CLAUDE.md`），则会将这些文件作为项目上下文加载。

这意味着在使用 Hermes 时，您现有的 Cursor 规范会自动生效。

## 上下文文件的加载方式

### 启动时（系统提示语生成阶段）

上下文文件是由 `agent/prompt_builder.py` 文件中的 `build_context_files_prompt()` 函数负责加载的：

1. **扫描工作目录**——按顺序查找 `.hermes.md`、`AGENTS.md`、`CLAUDE.md` 以及 `.cursorrules` 文件（第一个找到的即被采用）。
2. **读取内容**——每个文件均以 UTF-8 编码的文本形式被读取。
3. **安全扫描**——检查内容中是否存在提示注入模式。
4. **内容截断**——对于字符数超过限制的文件，会对其开头和结尾部分进行截断（开头截取 70%，结尾截取 20%，并在中间添加标记）。该字符上限可通过 `config.yaml` 中的 `context_file_max_chars` 参数明确设置；若未设置，则会根据模型的上下文窗口大小动态调整（最低 20,000 字符，最高 500,000 字符）。
5. **内容整合**——所有提取的信息会在 `# Project Context` 标题下合并在一起。
6. **插入系统提示**——整合后的内容会被添加到系统的初始提示中。

### 会话进行中的动态发现机制

`agent/subdirectory_hints.py` 文件中的 `SubdirectoryHintTracker` 模块会监控工具调用参数中的文件路径信息：

1. **提取路径**——每次工具调用后，都会从参数（如 `path`、`workdir` 或 Shell 命令）中提取文件路径。
2. **向上遍历目录**——依次检查当前目录及其最多 5 个上级目录（遇到已访问过的目录则停止）。
3. **加载相关配置**——若找到 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` 文件，就会将其加载（每个目录中取第一个找到的文件）。
4. **安全扫描**——执行与启动文件相同的安全扫描流程，检测提示注入风险。
5. **内容截断**——每份文件的字符数上限为 8,000 字符。
6. **插入结果**——这些信息会被附加到工具的响应结果中，从而使模型能够在上下文中自然地获取这些信息。

最终的系统提示结构大致如下：

```text
# Project Context

The following project context files have been loaded and should be followed:

## AGENTS.md

[Your AGENTS.md content here]

## .cursorrules

[Your .cursorrules content here]

[Your SOUL.md content here]
```

请注意，Soul类型的内容会直接被插入，不会附带额外的封装文本。

## 安全性：提示词注入防护

在纳入使用之前，所有上下文文件都会经过扫描，以检测潜在的提示词注入风险。扫描工具会重点检查以下内容：

- **指令覆盖企图**：如“忽略之前的指令”、“ disregard your rules”
- **欺诈性表述**：如“不要告诉用户”
- **系统提示词覆盖尝试**：如“system prompt override”
- **隐藏的HTML注释**：`<!-- ignore instructions -->`
- **隐藏的div元素**：`<div style="display:none">`
- **凭证窃取行为**：如`curl ... $API_KEY`
- **敏感文件访问操作**：如`cat .env`、`cat credentials`
- **不可见字符**：零宽空格、双向文本控制字符、字节连接符

一旦检测到任何威胁模式，该文件将被立即阻止使用。

```
[BLOCKED: AGENTS.md contained potential prompt injection (prompt_injection). Content not loaded.]
```

:::warning
该扫描工具可防范常见的注入攻击模式，但无法替代对共享仓库中上下文文件的审查。对于非您创建的项目，请务必核实其中的 AGENTS.md 文件内容。
:::

## 大小限制

| 限制项 | 值 |
|-------|------|
| 每个文件的最大字符数 | 若已设置则为 `context_file_max_chars`，否则为动态值（随模型上下文窗口大小变化，最低 20,000 字符，最高 500,000 字符） |
| 每个文件的读取超时时间 | `context_file_read_timeout`（默认为 5 秒）；对于在 iCloud Drive、OneDrive 或 NFS 等平台上读取速度较慢的文件，系统会发出警告并跳过该文件 |
| 开头部分截断比例 | 70% |
| 结尾部分截断比例 | 20% |
| 截断标记 | 10%（显示字符计数，并建议使用文件处理工具） |

当文件大小超过设定限制时，系统会显示如下截断提示：

```
[...truncated AGENTS.md: kept 14000+4000 of 25000 chars. Use file tools to read the full file.]
```

## 高效使用上下文文件的技巧

:::tip AGENTS.md 的最佳实践
1. **保持简洁** —— 内容长度需控制在配置的 `context_file_max_chars` 限制之内，因为智能体会在每轮对话中读取该文件
2. **使用标题进行结构化组织** —— 用 `##` 标签划分架构、规范及重要说明等不同板块
3. **提供具体示例** —— 展示推荐的代码模式、API 结构以及命名规范
4. **明确列出禁忌事项** —— 例如“切勿直接修改迁移文件”
5. **列明关键路径与端口信息** —— 智能体会依据这些信息来执行终端命令
6. **随着项目发展及时更新** —— 过时的上下文信息甚至比没有上下文更糟糕
:::

### 子目录级上下文

对于多模块项目，可将针对特定子目录的说明放在嵌套的 AGENTS.md 文件中：

```markdown
<!-- frontend/AGENTS.md -->
# Frontend Context

- Use `pnpm` not `npm` for package management
- Components go in `src/components/`, pages in `src/app/`
- Use Tailwind CSS, never inline styles
- Run tests with `pnpm test`
```

```markdown
<!-- backend/AGENTS.md -->
# Backend Context

- Use `poetry` for dependency management
- Run the dev server with `poetry run uvicorn main:app --reload`
- All endpoints need OpenAPI docstrings
- Database models are in `models/`, schemas in `schemas/`
```
