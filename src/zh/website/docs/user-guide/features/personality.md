---
sidebar_position: 9
title: "Personality & SOUL.md"
description: "Customize Hermes Agent's personality with a global SOUL.md, built-in personalities, and custom persona definitions"
---

# 性格与 SOUL.md

Hermes Agent 的性格是完全可定制的。`SOUL.md` 即其**核心身份标识**——它是系统提示词中的首项内容，用于定义该智能体的特性。

- `SOUL.md`：一个存储在 `HERMES_HOME` 目录中的持久化角色配置文件，作为智能体的身份标识（系统提示词中的第1个字段）
- 内置或自定义的 `/personality` 预设值：会覆盖到会话级的系统提示词中

如果您希望改变 Hermes 的性格，或用完全不同的智能体角色取而代之，只需编辑 `SOUL.md` 即可。

## SOUL.md 的当前工作原理

目前，Hermes 会自动在以下位置生成默认的 `SOUL.md`：

```text
~/.hermes/SOUL.md
```

更准确地说，它会使用当前实例的 `HERMES_HOME` 设置；因此，如果您为 Hermes 指定了自定义的安装目录，它就会使用该目录。

```text
$HERMES_HOME/SOUL.md
```

### 重要行为规范

- **`SOUL.md` 是智能体的主要身份标识。** 它会占据系统提示词中的第1个位置，从而取代硬编码的默认身份。
- 若系统中尚不存在 `SOUL.md` 文件，Hermes 会自动生成一个初始版本。
- 现有的用户 `SOUL.md` 文件绝不会被覆盖。
- Hermes 仅从 `HERMES_HOME` 目录加载 `SOUL.md` 文件。
- Hermes 不会在当前工作目录中查找 `SOUL.md` 文件。
- 若 `SOUL.md` 存在但内容为空，或无法被加载，Hermes 会回退到内置的默认身份。
- 若 `SOUL.md` 包含内容，这些内容将在经过安全扫描和截断处理后原样注入。
- `SOUL.md` **不会**被复制到上下文文件部分——它仅作为身份标识出现一次。

正因如此，`SOUL.md` 才是真正的“用户级”或“实例级”身份标识，而不仅仅是一个附加层。

## 为何采用此设计

这样的设计能够确保智能体的性格表现具有可预测性。

如果 Hermes 从用户启动它的任意目录加载 `SOUL.md`，那么在不同项目中，智能体的性格表现就可能会发生意外变化。通过仅从 `HERMES_HOME` 加载文件，智能体的性格便归属于该 Hermes 实例本身。

此外，这种设计也有助于向用户清晰地说明操作方法：
- “只需编辑 `~/.hermes/SOUL.md` 即可更改 Hermes 的默认性格。”

## 如何编辑该文件

对于大多数用户而言：

```bash
~/.hermes/SOUL.md
```

如果您使用自定义主页：

```bash
$HERMES_HOME/SOUL.md
```

## SOUL.md 应该包含哪些内容？

请将其用于设定持久的语音风格与个性特征，例如：
- 语调
- 沟通方式
- 直接性的程度
- 默认的交互风格
- 需要避免的表述风格
- Hermes 应如何处理不确定性、分歧或模糊情况

而以下内容则不太适合放在其中：
- 单次项目的具体指令
- 文件路径
- 代码仓库的规范
- 临时性的工作流程细节

这类内容应归入 `AGENTS.md`，而非 `SOUL.md`。

## 优秀的 SOUL.md 内容标准

一份优秀的 SOUL 文件应当具备以下特点：
- 在不同场景下保持稳定
- 范围足够广泛，可适用于多种对话
- 具体性足够强，能够切实塑造语音风格
- 侧重于沟通与身份定位，而非针对特定任务的指令

### 示例

```markdown
# Personality

You are a pragmatic senior engineer with strong taste.
You optimize for truth, clarity, and usefulness over politeness theater.

## Style
- Be direct without being cold
- Prefer substance over filler
- Push back when something is a bad idea
- Admit uncertainty plainly
- Keep explanations compact unless depth is useful

## What to avoid
- Sycophancy
- Hype language
- Repeating the user's framing if it's wrong
- Overexplaining obvious things

## Technical posture
- Prefer simple systems over clever systems
- Care about operational reality, not idealized architecture
- Treat edge cases as part of the design, not cleanup
```

## Hermes会向提示词中注入什么内容

`SOUL.md`中的内容会直接被放入系统提示词的第一个槽位——即代理身份的位置，且不会添加任何封装语言。

这些内容会经过以下处理：
- 提示词注入检测
- 若内容过长则进行截断

如果该文件为空、仅包含空白字符或无法读取，Hermes会回退到内置的默认身份描述（“你是Hermes Agent，由Nous Research打造的智能AI助手……”）。在设置了`skip_context_files`时（例如在子代理/委托场景中），也会采用此回退机制。

## 安全扫描

在纳入系统之前，`SOUL.md`会像其他包含上下文的文件一样，被扫描是否存在提示词注入模式。

因此，你仍应将其内容聚焦于角色设定与语气表达，而非试图偷偷嵌入奇怪的元指令。

## SOUL.md与AGENTS.md的区别

这是最关键的区别点。

### SOUL.md
用于定义：
- 身份身份
- 语调风格
- 表达方式
- 默认沟通规则
- 人格层面的行为特征

### AGENTS.md
用于定义：
- 项目架构
- 编码规范
- 工具偏好
- 项目特定的工作流程
- 命令、端口、路径及部署说明

一个实用的原则是：
- 若某内容需始终跟随你，应放入`SOUL.md`
- 若某内容属于某个项目范畴，则应放入`AGENTS.md`

## SOUL.md与 `/personality`的区别

`SOUL.md`是你持久有效的默认人格设定。

而`/personality`则是会话级别的临时覆盖设置，用于修改或补充当前的系统提示词。

因此：
- `SOUL.md` = 基准语气
- `/personality` = 临时模式切换

示例：
- 保持一个务实的默认SOUL人格，然后在辅导对话时使用`/personality teacher`模式
- 保持简洁的SOUL人格，然后在头脑风暴时使用`/personality creative`模式

## 内置人格设定

Hermes预置了多种内置人格，你可以通过`/personality`命令进行切换。

| 名称 | 描述 |
|------|------|
| **helpful** | 友好型通用助手 |
| **concise** | 简洁直接的回复风格 |
| **technical** | 专业详尽的技术专家风范 |
| **creative** | 具有创新思维的独特风格 |
| **teacher** | 耐心指导并配有清晰示例的教育者 |
| **kawaii** | 可爱表情、闪亮元素与满腔热情 ★ |
| **catgirl** | 带有猫咪般神态的猫娘，会说“喵~” |
| **pirate** | 精通技术的海盗船长Hermes |
| **shakespeare** | 具有戏剧张力的吟游诗人风格 |
| **surfer** | 极其随和的兄弟风范 |
| **noir** | 硬汉侦探式的叙述风格 |
| **uwu** | 用超可爱的语气表达极致萌感 |
| **philosopher** | 对每个问题都进行深度思考 |
| **hype** | 充满无限能量与热情！！！ |

## 通过命令切换人格设定

### CLI方式

```text
/personality
/personality concise
/personality technical
```

### 消息平台

```text
/personality teacher
```

这些虽是便捷的叠加配置，但除非相关叠加设置对默认人格进行了实质性修改，否则全局的 `SOUL.md` 文件依然会为 Hermes 保留其默认的人格设定。

## 在配置文件中定义自定义人格

您还可以在 `~/.hermes/config.yaml` 文件的 `agent.personalities` 部分中，定义具有名称的自定义人格。

```yaml
agent:
  personalities:
    codereviewer: >
      You are a meticulous code reviewer. Identify bugs, security issues,
      performance concerns, and unclear design choices. Be precise and constructive.
```

接着使用以下命令切换至该代理：

```text
/personality codereviewer
```

## 推荐工作流程

一个稳健的默认配置包括：

1. 在 `~/.hermes/SOUL.md` 中维护一份精心设计的全局 `SOUL.md` 文件；
2. 将项目相关说明放在 `AGENTS.md` 中；
3. 仅在需要临时改变角色风格时使用 `/personality` 指令。

这样的配置能够为你带来：
- 稳定的对话风格；
- 适合特定项目的行为表现；
- 必要时的临时控制能力。

## 角色风格与完整提示词之间的交互机制

从宏观层面来看，提示词栈由以下部分组成：
1. **SOUL.md**（智能体身份定义——若该文件不存在，则使用内置的默认配置）；
2. 针对工具的使用行为指导；
3. 记忆信息/用户上下文；
4. 智能体技能相关指导；
5. 上下文文件（如 `AGENTS.md`、`.cursorrules`）；
6. 时间戳；
7. 针对不同平台的格式化提示；
8. 可选的系统级提示词叠加，例如 `/personality`。

`SOUL.md` 是整个系统的基石，所有其他配置都建立在其之上。

## 相关文档

- [上下文文件](/user-guide/features/context-files)
- [配置设置](/user-guide/configuration)
- [实用技巧与最佳实践](/guides/tips)
- [SOUL.md 使用指南](/guides/use-soul-with-hermes)

## 对话风格与 CLI 显示样式的分离机制

对话风格与 CLI 显示样式是相互独立的：

- `SOUL.md`、`agent.system_prompt` 以及 `/personality` 指令会影响 Hermes 的对话方式；
- `display.skin` 和 `/skin` 指令则决定 Hermes 在终端中的显示外观。

有关终端显示样式的更多信息，请参阅 [皮肤与主题](./skins.md)。
