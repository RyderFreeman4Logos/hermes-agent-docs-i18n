---
sidebar_position: 4
title: "Which File Does What?"
description: "SOUL.md vs USER.md vs MEMORY.md vs AGENTS.md — a one-page map of the agent's files, who writes each one, and when the agent actually sees them"
---

# 各文件的功能是什么？

“我告诉过我的智能体某些信息，但它却忘了。” “智能体的‘大脑’在哪个文件里？” “我修改了SOUL.md，为什么它还是不记得我的名字？” 这些问题其实都指向同一个核心：Hermes Agent由多个Markdown文件共同构成，每个文件都有不同的功能。本页面将所有文件的功能集中展示。如需深入了解其中某个文件，可点击链接查看[持久内存](/user-guide/features/memory)、[个性设置与SOUL.md](/user-guide/features/personality)以及[上下文文件](/user-guide/features/context-files)的相关内容。

## 总览表

| File | What it holds | Who writes it | When the agent sees it | Where it lives |
|------|---------------|---------------|------------------------|----------------|
| **SOUL.md** | The agent's primary identity — personality, tone, communication style, what to avoid stylistically | You. Hermes seeds a starter file automatically if one doesn't exist; existing files are never overwritten | Slot #1 of the system prompt, at session start | `~/.hermes/SOUL.md` (or `$HERMES_HOME/SOUL.md` with a custom home) — never the working directory |
| **USER.md** | User profile — your name, role, preferences, communication style, expectations | The agent, via the `memory` tool (you can gate saves with `write_approval`, or edit entries via `hermes journey edit`) | Injected into the system prompt as a frozen snapshot at session start | `~/.hermes/memories/` |
| **MEMORY.md** | Agent's personal notes — environment facts, project conventions, tool quirks, things learned | The agent, via the `memory` tool (same gating and editing options as USER.md) | Injected into the system prompt as a frozen snapshot at session start | `~/.hermes/memories/` |
| **AGENTS.md** | Project instructions, conventions, architecture — commands, ports, paths, repo-specific workflows | You (or whoever authors the project) | Loaded into the system prompt at startup from your working directory; nested copies are discovered progressively as the agent navigates subdirectories | Project working directory + subdirectories |
| **.hermes.md** / **HERMES.md** | Project instructions, like AGENTS.md but Hermes-specific and highest priority | You | Loaded into the system prompt at startup (first match wins over AGENTS.md) | Your project — discovery walks up to the git root |

:::info 每个会话仅一个项目上下文文件  
每个会话中仅加载**一种**项目上下文类型，按优先级顺序选取：`.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`。`SOUL.md` 作为智能体身份始终会被独立加载，不参与该优先级排序。如需包括 `CLAUDE.md` 和 `.cursorrules` 兼容性在内的完整列表，请参阅[上下文文件](/user-guide/features/context-files)文档。  

:::

一个实用的简写说明：  
- **SOUL.md** 定义了智能体的*身份*——如果它需要始终跟随你，内容应保存于此。  
- **USER.md** 描述的是*你*的身份——由智能体为你维护。  
- **MEMORY.md** 记录了智能体*所学到的内容*——同样由智能体自行管理。  
- **AGENTS.md**（或 `.hermes.md`）则包含*项目所需的信息*——如果内容属于某个项目，就应存放在此处。  

## “为什么它忘了我刚才说的话？”  
内存数据（MEMORY.md 和 USER.md）会以**静态快照**的形式被注入系统提示词中，该快照在会话开始时生成一次。若智能体在会话过程中保存了某些内容，更改会立即写入磁盘，但直到下一个会话开始才会显示在系统提示词中。这是有意为之：这样既能保持大语言模型的前缀缓存以提高性能，又能确保工具响应始终反映最新状态，因此不会丢失任何信息——只需启动新会话，更新后的内存数据就会同步呈现。更多详情请参阅[内存如何显示在系统提示词中](/user-guide/features/memory#how-memory-appears-in-the-system-prompt)。  

## 常见混淆点

### “我在 SOUL.md 中写了关于自己的信息，但 USER.md 却依然为空”

`SOUL.md` 与 `USER.md` 是两个相互独立的系统，不会互相传递数据。`SOUL.md` 是由**你**直接编辑的个性配置文件——它决定了对话的语气与身份特征，其内容会原封不动地作为提示词中的第1个参数被使用。而 `USER.md` 则属于持久化记忆的一部分，由**智能体**通过 `memory` 工具来编写。如果你希望在自己的 USER.md 中存储相关信息，只需告知智能体（例如“请记住我更喜欢简洁的回答”），它就会将这些信息保存下来。编辑 SOUL.md 无法填充记忆内容，而记忆中的条目也不会改变智能体的个性设定。建议将稳定的语气与个性指导功能交给 SOUL.md，将个人偏好和档案信息存放在记忆系统中。更多详情可参阅 [SOUL.md 中应包含哪些内容？](/user-guide/features/personality#what-should-go-in-soulmd) 以及 [两个目标机制详解](/user-guide/features/memory#two-targets-explained)。

### “我在对话过程中告诉了它我的名字，但它却表现得好像没听到一样”

如果智能体已将您的姓名存储在内存中，说明保存操作成功——您可以通过 `memory` 工具的响应或 `hermes journey list` 来查看。出现这种情况是因为系统提示词在会话过程中不会刷新，因此被“注入”的内存块仍显示着会话开始时的状态。智能体仍可在当前对话中使用您之前提供的信息（这些信息已包含在上下文中），而保存后的条目则会在后续会话的系统提示词中保留。对于在会话进行时对 `SOUL.md` 或 `AGENTS.md` 所做的修改也是如此：上下文是在会话开始时生成的，因此需要重新启动会话才能应用这些更改。

:::提示 快速决策指南
- 想改变智能体的**对话风格**？请编辑 `~/.hermes/SOUL.md` — [个性设置与 SOUL.md](/user-guide/features/personality)。
- 想让智能体**记住某个事实**？直接告诉它即可——它会自动存储到内存中。[持久内存功能](/user-guide/features/memory)。
- 想设定**项目规则**？在项目中创建 `AGENTS.md`（或 `.hermes.md`）文件 — [上下文文件](/user-guide/features/context-files)。
- 需要**临时**更改个性设置？使用 `/personality` 命令即可——这是会话级别的临时修改，无需编辑文件。
:::

## 相关文档

- [持久内存](/user-guide/features/memory) — MEMORY.md、USER.md文件，`memory`工具，容量限制以及`write_approval`功能  
- [个性设置与SOUL.md](/user-guide/features/personality) — SOUL.md的内容编写指南，`/personality`预设选项，以及提示词堆叠结构  
- [上下文文件](/user-guide/features/context-files) — AGENTS.md、`.hermes.md`文件，渐进式内容发现机制，以及安全扫描功能
