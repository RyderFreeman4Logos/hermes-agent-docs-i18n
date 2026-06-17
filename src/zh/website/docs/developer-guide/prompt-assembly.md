---
sidebar_position: 5
title: "Prompt Assembly"
description: "How Hermes builds the system prompt, preserves cache stability, and injects ephemeral layers"
---

# 提示词组装

Hermes刻意将以下内容分开处理：

- **缓存的系统提示词状态**
- **API调用时临时添加的内容**

这是该项目最重要的设计决策之一，因为它会影响：

- token使用效率
- 提示词缓存效果
- 会话连贯性
- 内存数据准确性

相关主要文件包括：

- `run_agent.py`
- `agent/prompt_builder.py`
- `tools/memory_tool.py`

## 缓存的系统提示词层级

缓存的系统提示词由三个有序的层级组成（详见 `agent/system_prompt.py`）：

1. **稳定层** — 身份信息（`SOUL.md` 或默认值）、工具/模型使用指南、技能提示词、环境相关提示、平台相关提示
2. **上下文层** — 调用方提供的 `system_message` 以及项目上下文文件（`.hermes.md` / `AGENTS.md` / `CLAUDE.md` / `.cursorrules`）
3. **易变层** — 内置内存快照（`MEMORY.md`）、用户资料快照（`USER.md`）、外部内存提供模块、时间戳/会话信息/模型/提供方标识

最终的系统提示词将按照 `稳定层` → `上下文层` → `易变层` 的顺序组合起来。这种层级结构对于确定各部分的优先级至关重要：
- 技能属于**稳定层**
- 内存/资料快照属于**易变层**
- 这两类内容仍会保留在缓存的系统提示词中（不会作为临时的、在对话过程中动态插入的内容）

当设置了 `skip_context_files` 参数时（例如在子代理任务中），系统将不会加载 `SOUL.md`，而是直接使用硬编码的 `DEFAULT_AGENT_IDENTITY`。

### 具体示例：组装后的系统提示词

以下是在所有层级都存在时的最终系统提示词简化版本（注释标明了各部分的来源）：

```
# Layer 1: Agent Identity (from ~/.hermes/SOUL.md)
You are Hermes, an AI assistant created by Nous Research.
You are an expert software engineer and researcher.
You value correctness, clarity, and efficiency.
...

# Layer 2: Tool-aware behavior guidance
You have persistent memory across sessions. Save durable facts using
the memory tool: user preferences, environment details, tool quirks,
and stable conventions. Memory is injected into every turn, so keep
it compact and focused on facts that will still matter later.
...
When the user references something from a past conversation or you
suspect relevant cross-session context exists, use session_search
to recall it before asking them to repeat themselves.

# Tool-use enforcement (for GPT/Codex models only)
You MUST use your tools to take action — do not describe what you
would do or plan to do without actually doing it.
...

# Layer 3: Honcho static block (when active)
[Honcho personality/context data]

# Layer 4: Optional system message (from config or API)
[User-configured system message override]

# Layer 5: Frozen MEMORY snapshot
## Persistent Memory
- User prefers Python 3.12, uses pyproject.toml
- Default editor is nvim
- Working on project "atlas" in ~/code/atlas
- Timezone: US/Pacific

# Layer 6: Frozen USER profile snapshot
## User Profile
- Name: Alice
- GitHub: alice-dev

# Layer 7: Skills index
## Skills (mandatory)
Before replying, scan the skills below. If one clearly matches
your task, load it with skill_view(name) and follow its instructions.
...
<available_skills>
  software-development:
    - code-review: Structured code review workflow
    - test-driven-development: TDD methodology
  research:
    - arxiv: Search and summarize arXiv papers
</available_skills>

# Layer 8: Context files (from project directory)
# Project Context
The following project context files have been loaded and should be followed:

## AGENTS.md
This is the atlas project. Use pytest for testing. The main
entry point is src/atlas/main.py. Always run `make lint` before
committing.

# Layer 9: Timestamp + session
Current time: 2026-03-30T14:30:00-07:00
Session: abc123

# Layer 10: Platform hint
You are a CLI AI Agent. Try not to use markdown but simple text
renderable inside a terminal.
```

## SOUL.md 在提示词中的呈现方式

`SOUL.md` 位于 `~/.hermes/SOUL.md` 文件中，它代表了智能体的身份，即系统提示词中的第一个部分。`prompt_builder.py` 中的加载逻辑如下：

```python
# From agent/prompt_builder.py (simplified)
def load_soul_md() -> Optional[str]:
    soul_path = get_hermes_home() / "SOUL.md"
    if not soul_path.exists():
        return None
    content = soul_path.read_text(encoding="utf-8").strip()
    content = _scan_context_content(content, "SOUL.md")  # Security scan
    content = _truncate_content(content, "SOUL.md")       # Cap defaults to 20k chars, configurable
    return content
```

当 `load_soul_md()` 返回内容后，它会替换掉硬编码的 `DEFAULT_AGENT_IDENTITY`。随后会以 `skip_soul=True` 的参数调用 `build_context_files_prompt()` 函数，从而避免 SOUL.md 被重复使用（既不会作为身份信息出现，也不会作为上下文文件出现）。

如果不存在 `SOUL.md`，系统则会回退到以下方式：

```
You are Hermes Agent, an intelligent AI assistant created by Nous Research.
You are helpful, knowledgeable, and direct. You assist users with a wide
range of tasks including answering questions, writing and editing code,
analyzing information, creative work, and executing actions via your tools.
You communicate clearly, admit uncertainty when appropriate, and prioritize
being genuinely useful over being verbose unless otherwise directed below.
Be targeted and efficient in your exploration and investigations.
```

## 上下文文件如何被注入

`build_context_files_prompt()` 采用**优先级机制**——仅加载一种项目上下文类型（最先匹配的类型将生效）：

```python
# From agent/prompt_builder.py (simplified)
def build_context_files_prompt(cwd=None, skip_soul=False):
    cwd_path = Path(cwd).resolve()

    # Priority: first match wins — only ONE project context loaded
    project_context = (
        _load_hermes_md(cwd_path)       # 1. .hermes.md / HERMES.md (walks to git root)
        or _load_agents_md(cwd_path)    # 2. AGENTS.md (cwd only)
        or _load_claude_md(cwd_path)    # 3. CLAUDE.md (cwd only)
        or _load_cursorrules(cwd_path)  # 4. .cursorrules / .cursor/rules/*.mdc
    )

    sections = []
    if project_context:
        sections.append(project_context)

    # SOUL.md from HERMES_HOME (independent of project context)
    if not skip_soul:
        soul_content = load_soul_md()
        if soul_content:
            sections.append(soul_content)

    if not sections:
        return ""

    return (
        "# Project Context\n\n"
        "The following project context files have been loaded "
        "and should be followed:\n\n"
        + "\n".join(sections)
    )
```

### 上下文文件查找规则

| 优先级 | 文件名 | 搜索范围 | 备注 |
|--------|--------|----------|------|
| 1 | `.hermes.md`、`HERMES.md` | 从当前工作目录直至 git 根目录 | Hermes 原生项目配置文件 |
| 2 | `AGENTS.md` | 仅限当前工作目录 | 通用智能体指令文件 |
| 3 | `CLAUDE.md` | 仅限当前工作目录 | 兼容 Claude Code 使用 |
| 4 | `.cursorrules`、`.cursor/rules/*.mdc` | 仅限当前工作目录 | 兼容 Cursor 工具 |

所有上下文文件都会经过以下处理：
- **安全扫描** — 检测提示注入模式，如隐藏的 Unicode 字符、“忽略之前的指令”以及凭证窃取企图
- **截断处理** — 内容长度会被限制在 `context_file_max_chars` 字符以内（默认为 20,000 字符），采用 70/20 的头部/尾部保留比例，并添加截断标记
- **去除 YAML 前置信息** — 会移除 `.hermes.md` 中的前置信息（该字段预留用于未来的配置覆盖）

## 仅在 API 调用时存在的层

以下内容有意不作为缓存系统提示的一部分被保存：
- `ephemeral_system_prompt`
- 预填充消息
- 由网关生成的会话上下文叠加内容
- 在当前轮次中注入到用户消息中的后续轮次的 Honcho/外部检索结果

`pre_llm_call` 插件提供的上下文也属于这一类，它会被附加到当前轮次的**用户消息**中，而不会写入缓存的系统提示中。当多个插件返回上下文时，Hermes 会将这些上下文块拼接在一起（详见[Hooks → `pre_llm_call`](../user-guide/features/hooks.md#pre_llm_call)）。

这种分离方式有助于保持稳定的提示前缀，从而实现高效缓存。

## 内存快照

本地内存和用户配置数据会被存储在系统提示的**易变层**中。会话过程中的写入操作虽然会更新磁盘状态，但除非触发重新构建流程（如开始新会话，或通过压缩等方式显式触发无效化/重新构建），否则不会修改已缓存的系统提示。

## 上下文文件

`agent/prompt_builder.py` 会通过**优先级机制**来扫描并处理项目中的上下文文件——仅加载其中一种类型（优先匹配到的那个生效）：
1. `.hermes.md` / `HERMES.md`（会搜索至 git 根目录）
2. `AGENTS.md`（启动时从当前工作目录读取；在会话过程中会通过 `agent/subdirectory_hints.py` 逐步发现子目录中的文件）
3. `CLAUDE.md`（仅限当前工作目录）
4. `.cursorrules` / `.cursor/rules/*.mdc`（仅限当前工作目录）

用于身份配置的 `SOUL.md` 会通过 `load_soul_md()` 函数单独加载。一旦成功加载，`build_context_files_prompt(skip_soul=True)` 函数会确保该文件不会重复出现。

长度过长的文件在注入系统提示之前会被截断。

## 技能索引

当具备相关工具支持时，技能系统会为提示内容生成一个简洁的技能索引。

## 支持的提示自定义方式

大多数用户应将 `agent/prompt_builder.py` 视为实现代码，而非可直接配置的界面。推荐的定制方式是修改 Hermes 已经加载的提示输入内容，而非直接编辑 Python 模板文件。

### 首先尝试使用这些方式

- `~/.hermes/SOUL.md` — 用您自定义的智能体角色和行为规范替换内置的默认身份模块
- `~/.hermes/MEMORY.md` 和 `~/.hermes/USER.md` — 提供需要在新会话中继续使用的持久性事实信息和用户配置数据
- 项目级上下文文件，如 `.hermes.md`、`HERMES.md`、`AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` — 注入特定项目的工作规则
- 技能模块 — 无需编辑核心提示代码即可封装可复用的工作流程和参考信息
- 可选的系统提示配置/API 覆盖选项 — 可添加针对特定部署环境的指令文本，而无需 fork Hermes 源码
- 临时性叠加内容，如 `HERMES_EPHEMERAL_SYSTEM_PROMPT` 或预填充消息 — 添加仅适用于当前轮次的指导信息，这类内容不会成为缓存提示前缀的一部分

### 何时需要直接编辑代码

只有当您有意维护某个分支版本或向上游提交功能修改时，才需要编辑 `agent/prompt_builder.py`。该文件负责为每个会话构建提示结构、定义缓存边界以及确定内容注入顺序。直接在该文件中进行修改属于全局产品层面的改动，而非针对单个用户的提示定制。

简而言之：
- 若希望更改智能体身份，编辑 `SOUL.md`
- 若希望调整项目规则，编辑项目级上下文文件
- 若希望创建可复用的操作流程，添加或修改技能模块
- 若希望改变 Hermes 为所有用户生成提示的方式，则需要修改 Python 代码，并将其视为代码贡献

## 为何采用这种提示构建方式

这种架构设计旨在实现以下目标：
- 保留供应商侧提供的提示缓存功能
- 避免不必要的历史记录修改
- 保持内存操作逻辑的清晰性
- 允许网关/ACP/CLI 添加上下文信息，而不会污染已缓存的提示状态

## 相关文档

- [上下文压缩与提示缓存](./context-compression-and-caching.md)
- [会话存储](./session-storage.md)
- [网关内部机制](./gateway-internals.md)
