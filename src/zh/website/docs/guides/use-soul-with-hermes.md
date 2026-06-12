---
sidebar_position: 7
title: "Use SOUL.md with Hermes"
description: "How to use SOUL.md to shape Hermes Agent's default voice, what belongs there, and how it differs from AGENTS.md and /personality"
---

# 在 Hermes 中使用 SOUL.md

`SOUL.md` 是您 Hermes 实例的**核心身份标识**。它是系统提示词中的首要内容——它决定了智能体的身份、表达方式以及应避免的行为。

如果您希望每次与 Hermes 对话时都能获得一致的助手体验，或者想要完全用自己定义的角色来替代 Hermes 的默认形象，那么就应该使用这个文件。

## SOUL.md 的用途

您可以使用 `SOUL.md` 来指定：
- 语气风格
- 人格特征
- 沟通方式
- Hermes 应该保持多直接或多亲切的态度
- Hermes 在表达上应避免的风格
- 面对不确定性、分歧和模糊情况时 Hermes 的应对方式

简而言之：
- `SOUL.md` 负责定义 Hermes 是谁以及它该如何表达。

## SOUL.md 不适用的场景

以下内容不应放在 `SOUL.md` 中：
- 项目特定的编码规范
- 文件路径
- 命令
- 服务端口
- 架构说明
- 项目工作流程指引

这些内容应记录在 `AGENTS.md` 中。

一个实用的原则是：
- 如果某项规则适用于所有场景，就将其放入 `SOUL.md`；
- 如果仅适用于某个特定项目，则放入 `AGENTS.md`。

## 文件存放位置

目前，Hermes 仅针对当前实例使用全局的 SOUL 文件：

```text
~/.hermes/SOUL.md
```

如果您使用自定义主目录来运行 Hermes，其路径将为：

```text
$HERMES_HOME/SOUL.md
```

## 首次运行时的行为

如果尚未存在，Hermes 会自动为您生成一个初始的 `SOUL.md` 文件。

这意味着大多数用户可以直接使用一个可立即阅读和编辑的实际文件来开始使用。

重要提示：
- 如果您已拥有 `SOUL.md` 文件，Hermes 不会覆盖它
- 如果该文件存在但内容为空，Hermes 也不会将其内容添加到提示词中

## Hermes 的使用方式

当 Hermes 启动会话时，它会从 `HERMES_HOME` 路径读取 `SOUL.md`，扫描其中的提示词注入模式，必要时对其进行截断，然后将其作为**智能体身份**——即系统提示词中的第1个槽位。这意味着 `SOUL.md` 会完全替代内置的默认身份文本。

如果 `SOUL.md` 文件缺失、为空或无法加载，Hermes 会回退到内置的默认身份。

该文件无需任何封装语言层，其内容本身才是关键——请按照您希望智能体思考和表达的方式来撰写内容。

## 首次编辑的建议

即使不进行其他操作，也请打开该文件并修改几行内容，使其更具个人特色。

例如：

```markdown
You are direct, calm, and technically precise.
Prefer substance over politeness theater.
Push back clearly when an idea is weak.
Keep answers compact unless deeper detail is useful.
```

仅此一点，就能显著改变对Hermes的使用体验。  

## 示例风格  

### 1. 务实的工程师

```markdown
You are a pragmatic senior engineer.
You care more about correctness and operational reality than sounding impressive.

## Style
- Be direct
- Be concise unless complexity requires depth
- Say when something is a bad idea
- Prefer practical tradeoffs over idealized abstractions

## Avoid
- Sycophancy
- Hype language
- Overexplaining obvious things
```

### 2. 研究合作伙伴

```markdown
You are a thoughtful research collaborator.
You are curious, honest about uncertainty, and excited by unusual ideas.

## Style
- Explore possibilities without pretending certainty
- Distinguish speculation from evidence
- Ask clarifying questions when the idea space is underspecified
- Prefer conceptual depth over shallow completeness
```

### 3. 教师/讲解员

```markdown
You are a patient technical teacher.
You care about understanding, not performance.

## Style
- Explain clearly
- Use examples when they help
- Do not assume prior knowledge unless the user signals it
- Build from intuition to details
```

### 4. 严格的审核者

```markdown
You are a rigorous reviewer.
You are fair, but you do not soften important criticism.

## Style
- Point out weak assumptions directly
- Prioritize correctness over harmony
- Be explicit about risks and tradeoffs
- Prefer blunt clarity to vague diplomacy
```

## 什么是优秀的 SOUL.md？

优秀的 `SOUL.md` 应具备以下特点：
- 稳定可靠
- 具有广泛适用性
- 能够体现独特风格
- 不包含过多的临时性指令

而薄弱的 `SOUL.md` 则表现为：
- 满是项目细节
- 内容相互矛盾
- 试图对每种响应格式进行过度约束
- 大量使用“提供帮助”和“表述清晰”这类空泛的表述

Hermes 本身就已经力求做到有帮助且表述清晰。`SOUL.md` 应该为其增添真正的个性与风格，而非重复那些显而易见的默认设置。

## 建议的结构

虽然并非必须使用标题，但它们能起到辅助作用。
以下是一种效果良好的简单结构：

```markdown
# Identity
Who Hermes is.

# Style
How Hermes should sound.

# Avoid
What Hermes should not do.

# Defaults
How Hermes should behave when ambiguity appears.
```

## SOUL.md 与 /personality 的区别

二者互为补充。

请使用 `SOUL.md` 设定持久的基础行为模式；
而使用 `/personality` 则用于临时切换模式。

示例：
- 您的默认 SOUL 行为风格是务实且直截了当的；
- 在某次会话中，您可以使用 `/personality teacher` 切换为教师风格；
- 之后无需修改基础语音文件，即可恢复原来的行为模式。

## SOUL.md 与 AGENTS.md 的区别

这是最常被犯的错误。

### 应放入 SOUL.md 的内容
- “表达要直截了当。”
- “避免使用夸张的措辞。”
- “除非需要深入解释，否则优先给出简短答案。”
- “当用户有误时予以纠正。”

### 应放入 AGENTS.md 的内容
- “请使用 pytest 而非 unittest。”
- “前端代码位于 `frontend/` 目录中。”
- “绝不可直接修改迁移文件。”
- “API 运行在 8000 端口上。”

## 如何编辑这些配置

```bash
nano ~/.hermes/SOUL.md
```

或

```bash
vim ~/.hermes/SOUL.md
```

接着重启 Hermes 或开启新的会话。

## 实用工作流程

1. 从预设的默认文件开始
2. 剔除那些不符合你期望语音风格的内容
3. 添加4–8行文字，明确界定语音风格与默认设置
4. 与Hermes进行一段时间的对话
5. 根据仍存在的问题进行调整

这种迭代式方法比试图一次性设计出完美的个性效果更好。

## 故障排除

### 我已编辑了SOUL.md，但Hermes的语音风格依旧不变

请检查：
- 是否编辑了 `~/.hermes/SOUL.md` 或 `$HERMES_HOME/SOUL.md`
- 而非项目目录中的某个 `SOUL.md` 文件
- 文件内容并非为空
- 编辑后是否已重启会话
- 是否有 `/personality` 覆盖层影响了最终结果

### Hermes忽略了我的SOUL.md中的部分内容

可能的原因：
- 优先级更高的指令覆盖了这些设置
- 文件中存在相互矛盾的指导内容
- 文件过长导致内容被截断
- 部分文本类似提示注入内容，可能被扫描器屏蔽或修改

### 我的SOUL.md变得过于针对特定项目

请将项目相关指令移至 `AGENTS.md` 中，让 `SOUL.md` 专注于个性与风格设定。

## 相关文档

- [个性设置与SOUL.md](/user-guide/features/personality)
- [上下文文件](/user-guide/features/context-files)
- [配置设置](/user-guide/configuration)
- [技巧与最佳实践](/guides/tips)
