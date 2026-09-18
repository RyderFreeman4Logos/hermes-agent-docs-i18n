---
sidebar_position: 5
title: "Prompt Assembly"
description: "How Hermes builds the system prompt, preserves cache stability, and injects ephemeral layers"
---

# 提示词组装机制

Hermes 有意将以下内容分开处理：

- **缓存的系统提示词状态**
- **API调用时动态添加的临时内容**

这是该项目最重要的设计决策之一，因为它会影响到：

- token 使用效率
- 提示词缓存的效果
- 会话连贯性
- 内存处理的准确性

相关主要文件包括：

- `run_agent.py`
- `agent/prompt_builder.py`
- `tools/memory_tool.py`

## 缓存的系统提示词层级结构

缓存的系统提示词由三个有序的层级组成（详见 `agent/system_prompt.py`）：

1. **稳定层** —— 身份信息（`SOUL.md` 或默认值）、工具/模型使用指南、编程操作规范
2. **上下文层** —— 用户提供的 `system_message`、项目相关配置文件（`.hermes.md` / `AGENTS.md` / `CLAUDE.md` / `.cursorrules`），以及基于工作树的 Git 工作区快照、操作员指令和平台提示
3. **动态层** —— 技能索引、内置内存快照（`MEMORY.md`）、用户配置快照（`USER.md`）、外部内存提供模块、时间戳/会话信息/模型/提供方信息，以及运行时环境提示（主机名/用户目录/**当前工作目录**）

最终的系统提示词将按照 `稳定层` → `上下文层` → `动态层` 的顺序组合起来。这种层级结构对于确定各部分的优先级至关重要：
- 技能属于**稳定层**
- 内存/配置快照属于**动态层**
- 这两类内容均包含在缓存的系统提示词中（不会作为临时的、在对话过程中动态插入的内容）
在上下文层级中，共享的项目文件会出现在所有标识当前工作树的元素之前。当同一个项目在不同 Git 工作树中运行时，这些会话会共享一个覆盖整个上下文块的提示前缀，而不会止步于第一个依赖当前工作目录的行——这个前缀正是最长前缀提供程序缓存所复用的内容。没有工作区快照的会话则将其后续的引导信息保留在稳定层级中；而运行时环境块始终位于易变层级之末。

对于存储的提示而言：`_stored_prompt_matches_runtime()`（位于 `agent/conversation_loop.py` 中）会读取在已渲染的 `# Hermes runtime environment` 分界符之后的第一段主机信息，该分界符以绝对末尾的结束标记作为标识，以此区分这种格式与旧版直接引用标题的写法。运行时分界符位于所有项目、操作员、内存及插件相关文本之后，因此这些区块中的示例不会被误认为是运行时的当前工作目录。模型和提供程序的信息会在运行时分界符之前被读取，但嵌入器描述除外。`Platform:` 并非有意设计为身份识别字段：通过表面切换机制（桌面端 ↔ TUI 界面），系统会保留已存储的字节内容，并在每轮对话的用户消息通道中以一次性提示的形式输出当前界面的引导信息（详见 `agent/surface_switch.py`），从而确保缓存的前缀得以保留（#104414）。旧版提示仍保持其原有的“主机信息在前、上下文信息在后”的结构，因此那些在重新排序之前就已保存的提示依然有效。

当设置了 `skip_context_files` 参数时（例如在子代理委托场景中），SOUUL.md 文件将不会被加载，系统会转而使用硬编码的 `DEFAULT_AGENT_IDENTITY` 值。

### 具体示例：组合后的系统提示词

下图展示了在所有组件都存在时的最终系统提示词简化版本（注释标明了各部分的来源）：

```
# Layer 1: Agent Identity (from ~/.hermes/SOUL.md)
You are Hermes, an AI assistant created by Nous Research.
You are an expert software engineer and researcher.
You value correctness, clarity, and efficiency.
...

# Layer 2: Tool-aware behavior guidance
Task-learned procedures, pitfalls, and task-specific preferences belong
in skills. Memory is the narrow exception for facts that apply to EVERY
session regardless of task. Skill-writing instructions appear here only
when skill_manage is available; its absence does not widen memory's scope.
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

## 自定义平台提示

平台提示（位于第10层）是Hermes为Telegram、WhatsApp、Slack、CLI等平台提供的针对特定界面的引导信息——例如“您当前处于终端界面，请避免使用Markdown格式”。内置的默认提示存储在`PLATFORM_HINTS`（位于`agent/system_prompt.py`文件中）；而由插件提供的平台则通过平台注册表来设置各自的提示。

管理员可以通过`config.yaml`文件中的顶级`platform_hints`键，对某个特定平台的提示进行补充或替换，而无需影响其他任何平台。

```yaml
platform_hints:
  whatsapp:
    append: >
      When tabular output would be useful, invoke the table_formatting
      skill instead of emitting a Markdown table.
  slack:
    replace: "You are on Slack. Keep responses tight and avoid wide tables."
  telegram: "Prefer short messages; split long answers."   # shorthand = append
```

- `append` — 保留内置提示，并在其后添加额外文本。  
- `replace` — 完全替换内置提示。  
- 空字符串 — 即为 `append` 的简写形式。  
- 当同时使用 `append` 和 `replace` 时，`replace` 会优先生效。  
- 若配置项格式错误，系统会出于安全考虑忽略该错误并恢复为未修改的默认值，因此错误的配置值绝不会破坏提示语的生成，也不会在不同平台之间造成影响。  

此类覆盖配置会在系统提示语生成时被应用（即会话启动时，以及在提示语重新构建的压缩操作时）。它能为固定配置生成字节级稳定的提示语，因此会与内置提示语一同存放在 **stable** 类别中，不会干扰提示语缓存——它并非对已冻结的提示语在会话进行中的实时修改。  

## SOUL.md 如何出现在提示语中  

`SOUL.md` 位于 `~/.hermes/SOUL.md` 文件中，用于标识智能体的身份，即系统提示语的最开头部分。`prompt_builder.py` 中的加载逻辑如下：

```python
# From agent/prompt_builder.py (simplified)
def load_soul_md() -> Optional[str]:
    soul_path = get_hermes_home() / "SOUL.md"
    if not soul_path.exists():
        return None
    content = soul_path.read_text(encoding="utf-8").strip()
    content = _scan_context_content(content, "SOUL.md")  # Security scan
    content = _truncate_content(content, "SOUL.md")       # Cap scales with model context window (20k floor); config override wins
    return content
```

当 `load_soul_md()` 返回内容后，它会替换掉硬编码的 `DEFAULT_AGENT_IDENTITY`。随后会以 `skip_soul=True` 的参数调用 `build_context_files_prompt()` 函数，从而避免 SOUL.md 被重复使用（既不会作为身份信息出现，也不会作为上下文文件出现）。

如果不存在 `SOUL.md`，系统则会回退到以下方式：

```
You are Hermes Agent, built by Nous Research. Be direct: match the length
of your reply to the weight of the ask — a one-line question gets a
one-line answer, and finished work gets a short report of what changed,
what's verified, and what's left, never a replay of the process. No
filler ("Great question," "I'd be happy to"), no restating the request
back, no re-summarizing what you already said, no narrating tool calls
the user can see. Plain claims over adjectives; when unsure, say so
plainly. Agree because it's right, not because the user said it. Depth
is earned — give it when the user asks for detail, teaches, or the
stakes demand it, not by default.
```

## 上下文文件是如何注入的

`build_context_files_prompt()` 采用**优先级机制**——仅加载一种项目上下文类型（最先匹配到的类型将被采用）：

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
| 1 | `.hermes.md`、`HERMES.md` | 从当前工作目录到 git 根目录 | Hermes 原生项目配置文件 |
| 2 | `AGENTS.md` | 仅限当前工作目录 | 通用智能体指令文件 |
| 3 | `CLAUDE.md` | 仅限当前工作目录 | 兼容 Claude Code 使用 |
| 4 | `.cursorrules`、`.cursor/rules/*.mdc` | 仅限当前工作目录 | 兼容 Cursor 工具 |

所有上下文文件都会经过以下处理：
- **安全扫描**——检测提示注入模式，如隐藏字符、"忽略先前指令"以及凭证窃取企图
- **内容截断**——根据 `context_file_max_chars` 设置对文件内容进行限制，采用 70/20 的头部/尾部分割策略，并添加截断标记。该字符上限会随模型上下文窗口大小调整（最低 20,000 字符，最高 500,000 字符）；若在 `config.yaml` 中明确指定了 `context_file_max_chars`，则以该值为准
- **移除 YAML 前置信息**——会删除 `.hermes.md` 文件中的前置信息（该字段暂保留，未来可能用于配置覆盖）

## 仅在 API 调用时生效的层

以下内容有意不作为缓存系统提示的一部分被保存：
- `ephemeral_system_prompt`
- 预填充消息
- 由网关生成的会话上下文叠加信息
- 在当前轮次用户消息中插入的后续轮次的 Honcho/外部检索内容
`pre_llm_call` 插件提供的上下文也会被纳入此次 API 调用流程中：它会被附加到当前轮次的**用户消息**中，而不会被写入已缓存的系统提示中。当多个插件返回上下文时，Hermes 会将这些上下文块拼接在一起（详见[Hooks → `pre_llm_call`](../user-guide/features/hooks.md#pre_llm_call)）。

这种分离方式有助于保持用于缓存的部分内容稳定不变。

## 内存快照

本地内存和用户配置数据会被存储在系统提示的**易变层**中。会话过程中的写入操作虽然会更新磁盘状态，但除非触发重新构建流程（如开始新会话，或通过压缩等方式主动触发无效化/重新构建），否则不会修改已缓存的系统提示内容。

## 上下文文件

`agent/prompt_builder.py` 会通过**优先级机制**来扫描并处理项目中的上下文文件——只加载其中一种类型（最先匹配到的那个生效）：

1. `.hermes.md` / `HERMES.md`（从 Git 根目录开始查找）
2. `AGENTS.md`（在启动时以当前工作目录为起点；会话过程中会通过 `agent/subdirectory_hints.py` 逐步发现子目录中的此类文件）
3. `CLAUDE.md`（仅考虑当前工作目录）
4. `.cursorrules` / `.cursor/rules/*.mdc`（仅考虑当前工作目录）

用于身份信息的 `SOUL.md` 会通过 `load_soul_md()` 函数单独加载。一旦成功加载，`build_context_files_prompt(skip_soul=True)` 函数就会确保该文件不会重复出现。

在将上下文文件注入系统提示之前，过长的文件内容会被截断处理。

## 技能索引

当具备相应的技能工具时，技能系统会为系统提示生成一个简洁的技能索引。

## 支持的提示自定义方式

大多数用户应将 `agent/prompt_builder.py` 视为实现代码，而非配置界面。推荐的定制方式是修改 Hermes 已加载的提示词输入内容，而非直接编辑 Python 模板。

### 首先使用这些配置界面

- `~/.hermes/SOUL.md` — 用您自定义的智能体角色与行为规范替换内置的默认身份块。
- `~/.hermes/MEMORY.md` 和 `~/.hermes/USER.md` — 提供需要在新会话中保留的持久性跨会话事实及用户档案数据。
- 项目级配置文件，如 `.hermes.md`、`HERMES.md`、`AGENTS.md`、`CLAUDE.md` 或 `.cursorrules` — 注入特定于该仓库的工作规则。
- Skills 功能 — 在无需编辑核心提示词代码的情况下，封装可复用的工作流程与参考内容。
- 可选的系统提示词配置/API 覆盖 — 在不 fork Hermes 的前提下，添加针对特定部署环境的指令文本。
- 临时性覆盖配置，如 `HERMES_EPHEMERAL_SYSTEM_PROMPT` 或预填消息 — 添加仅适用于当前对话轮次的指导内容，避免其成为缓存提示词的前缀部分。

### 何时才需要编辑代码

只有当您有意维护某个 fork 版本或为上游版本贡献功能修改时，才应编辑 `agent/prompt_builder.py`。该文件负责为每个会话整合提示词处理逻辑、缓存边界以及内容注入顺序。直接在该文件中进行编辑属于全局产品层面的修改，而非针对单个用户的提示词定制。

简而言之：

- 若需使用不同的助手身份，请编辑 `SOUL.md` 文件。
- 若需自定义仓库规则，请修改项目上下文文件。
- 若需创建可复用的操作流程，请添加或修改技能模块。
- 若想更改 Hermes 为所有用户生成提示词的方式，可通过修改 Python 代码来实现，并将其视为代码贡献。

## 为何提示词生成机制采用此设计

该架构经过精心优化，旨在实现以下目标：

- 保留提供方端的提示词缓存功能；
- 避免不必要的历史记录修改；
- 保持内存语义的清晰性；
- 允许网关/ACP/CLI 添加上下文信息，而不会影响持久化的提示词状态。

## 相关文档

- [上下文压缩与提示词缓存](./context-compression-and-caching.md)
- [会话存储](./session-storage.md)
- [网关内部机制](./gateway-internals.md)
