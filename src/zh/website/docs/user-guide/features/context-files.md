---
sidebar_position: 8
title: "Context Files"
description: "Project context files — .hermes.md, AGENTS.md, CLAUDE.md, global SOUL.md, and .cursorrules — automatically injected into every conversation"
---

# 上下文文件

Hermes Agent 会自动发现并加载那些决定其行为方式的上下文文件。其中一些文件属于项目级，会在工作目录中被检测到。而 `SOUL.md` 则是整个 Hermes 实例共用的，仅从 `HERMES_HOME` 路径下加载。

## 支持的上下文文件

| 文件名 | 用途 | 检测方式 |
|--------|------|----------|
| **.hermes.md** / **HERMES.md** | 项目相关说明（优先级最高） | 从 git 根目录开始查找 |
| **AGENTS.md** | 项目结构、规范及架构说明 | 启动时从当前工作目录开始，逐步向下查找子目录 |
| **CLAUDE.md** | Claude Code 的上下文文件（也会被检测到） | 启动时从当前工作目录开始，逐步向下查找子目录 |
| **SOUL.md** | 为该 Hermes 实例定制全局个性与语气设置 | 仅从 `HERMES_HOME/SOUL.md` 路径加载 |
| **.cursorrules** | Cursor IDE 编码规范文件 | 仅从当前工作目录加载 |
| **.cursor/rules/*.mdc** | Cursor IDE 规则模块文件 | 仅从当前工作目录加载 |

:::info 优先级规则
每个会话中仅会加载**一种**项目上下文类型（按顺序优先，第一个匹配的生效）：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。而 **SOUL.md** 始终会作为代理的身份设定（即第1个槽位）被独立加载。
:::

## AGENTS.md

`AGENTS.md` 是最主要的项目上下文文件。它用于向代理说明项目的结构、需要遵循的规范以及任何特殊要求。

### 逐步扫描子目录功能

在会话开始时，Hermes 会将工作目录中的 `AGENTS.md` 内容加载到系统提示语中。当代理在会话过程中通过 `read_file`、`terminal`、`search_files` 等功能进入子目录时，它会**逐步发现**这些目录中的上下文文件，并在它们变得相关时立即将其融入对话中。

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

与在启动时加载所有内容相比，这种方法具有以下两大优势：
- **避免系统提示信息臃肿**——仅在需要时才显示子目录相关提示
- **保持提示缓存稳定**——系统提示会在多轮对话中保持不变

每个子目录在单次会话中最多会被检查一次。该检测机制还会向上遍历父目录，因此即便 `backend/src/` 目录本身没有上下文文件，读取 `backend/src/main.py` 时也能发现 `backend/AGENTS.md`。

:::info
子目录中的上下文文件会与启动时的上下文文件一样经过相同的[安全扫描](#security-prompt-injection-protection)，恶意文件会被拦截。
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

`SOUL.md` 用于控制智能体的性格特征、语气以及沟通风格。详细信息请参阅 [性格设置](/user-guide/features/personality) 页面。

**位置：**

- `~/.hermes/SOUL.md`
- 若您使用自定义目录运行 Hermes，则为 `$HERMES_HOME/SOUL.md`

重要说明：

- 如果不存在 `SOUL.md`，Hermes 会自动生成一个默认版本
- Hermes 仅从 `HERMES_HOME` 目录加载 `SOUL.md`
- Hermes 不会搜索当前工作目录中的 `SOUL.md` 文件
- 若该文件为空，则不会将其中任何内容添加到提示语中
- 若文件包含内容，系统会在扫描并截断后原样将其插入提示语中

## .cursorrules

Hermes 兼容 Cursor IDE 的 `.cursorrules` 文件以及 `.cursor/rules/*.mdc` 规则模块。如果这些文件位于项目根目录中，且未找到优先级更高的上下文文件（如 `.hermes.md`、`AGENTS.md` 或 `CLAUDE.md`），则它们将被作为项目上下文加载。

这意味着在使用 Hermes 时，您现有的 Cursor 规范会自动生效。

## 上下文文件的加载方式

### 启动时（系统提示语）

上下文文件由 `agent/prompt_builder.py` 中的 `build_context_files_prompt()` 函数负责加载：

1. **扫描工作目录** — 按顺序查找 `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`（第一个匹配到的文件优先）
2. **读取内容** — 每个文件均以 UTF-8 编码格式读取
3. **安全扫描** — 检查内容中是否存在提示语注入风险
4. **截断处理** — 字符数超过 20,000 的文件会被截取开头和结尾部分（开头保留 70%，结尾保留 20%，中间会添加标记）
5. **整合内容** — 所有截取的内容会在 `# Project Context` 标题下合并
6. **插入提示语** — 整合后的内容会被添加到系统提示语中

### 会话进行中（逐步发现）

`agent/subdirectory_hints.py` 中的 `SubdirectoryHintTracker` 会监控工具调用参数中的文件路径：

1. **提取路径** — 每次工具调用后，都会从参数（如 `path`、`workdir` 或 Shell 命令）中提取文件路径
2. **向上遍历目录** — 依次检查当前目录及其最多 5 个上级目录（已访问过的目录不再重复检查）
3. **加载规则** — 若找到 `AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` 文件，即将其加载（每个目录中优先选择第一个匹配的文件）
4. **安全扫描** — 执行与启动时相同的提示语注入检测
5. **截断处理** — 每个文件的字符数上限为 8,000
6. **插入结果** — 这些内容会被附加到工具输出结果中，从而使模型能自然地在上下文中看到它们

最终的提示语结构大致如下：

```text
# Project Context

The following project context files have been loaded and should be followed:

## AGENTS.md

[Your AGENTS.md content here]

## .cursorrules

[Your .cursorrules content here]

[Your SOUL.md content here]
```

请注意，SOUL类型的内容会被直接插入，不会附带额外的封装文本。

## 安全性：提示注入防护

在将任何上下文文件纳入使用之前，系统都会对其进行潜在的提示注入检测。检测内容包括：

- **指令覆盖尝试**：如“忽略之前的指令”、“无视你的规则”
- **欺诈性表述**：如“不要告诉用户”
- **系统提示覆盖**：如“覆盖系统提示”
- **隐藏的HTML注释**：`<!-- ignore instructions -->`
- **隐藏的div元素**：`<div style="display:none">`
- **凭证窃取行为**：如`curl ... $API_KEY`
- **敏感文件访问尝试**：如`cat .env`、`cat credentials`
- **不可见字符**：零宽空格、双向文本控制字符、字节连接符

一旦检测到任何威胁模式，该文件就会被阻止使用。

```
[BLOCKED: AGENTS.md contained potential prompt injection (prompt_injection). Content not loaded.]
```

:::warning
该扫描工具可防范常见的注入攻击模式，但无法替代对共享仓库中上下文文件的仔细检查。对于非您创建的项目，请务必核实其中的 AGENTS.md 文件内容。
:::

## 大小限制

| 限制项 | 数值 |
|-------|------|
| 每个文件的最大字符数 | 20,000（约 7,000 个标记） |
| 开头部分截断比例 | 70% |
| 结尾部分截断比例 | 20% |
| 截断标记 | 10%（显示字符数并建议使用文件处理工具） |

当文件字符数超过 20,000 时，系统会显示如下截断提示：

```
[...truncated AGENTS.md: kept 14000+4000 of 25000 chars. Use file tools to read the full file.]
```

## 高效使用上下文文件的技巧

:::tip AGENTS.md 的最佳实践
1. **保持简洁**——字数务必控制在 20K 字以内，因为智能体会在每一轮对话中都读取该文件
2. **使用标题进行结构化组织**——用 `##` 标签划分架构、规范及重要说明等部分
3. **提供具体示例**——展示推荐的代码模式、API 结构以及命名规范
4. **明确说明禁忌事项**——例如“切勿直接修改迁移文件”
5. **列出关键路径与端口信息**——智能体会利用这些信息来执行终端命令
6. **随着项目发展及时更新**——过时的上下文比没有上下文更糟糕
:::

### 子目录级上下文

对于大型单体项目，可将针对特定子目录的说明放在嵌套的 AGENTS.md 文件中：

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
