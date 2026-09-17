---
sidebar_position: 9
title: "Personality & SOUL.md"
description: "Customize Hermes Agent's personality with a global SOUL.md, built-in personalities, and custom persona definitions"
---

# 性格与 SOUL.md

Hermes Agent 的性格完全可以自定义。`SOUL.md` 即其**核心身份标识**——它是系统提示词中的首要内容，决定了该智能体的特性。

- `SOUL.md`：一个存储在 `HERMES_HOME` 目录中的持久化角色配置文件，用于定义智能体的身份（系统提示词中的第1个字段）
- 内置或自定义的 `/personality` 预设值：会作为会话级别的系统提示词覆盖内容

如果您想改变 Hermes 的性格，或用完全不同的智能体角色取而代之，只需编辑 `SOUL.md` 即可。

## SOUL.md 的当前工作原理

目前，Hermes 会在以下位置自动生成默认的 `SOUL.md`：

```text
~/.hermes/SOUL.md
```

更准确地说，它会使用当前实例的 `HERMES_HOME` 设置；因此，如果您为 Hermes 指定了自定义的安装目录，它将会使用该目录。

```text
$HERMES_HOME/SOUL.md
```

### 重要行为规范

- **`SOUL.md` 是智能体的核心身份标识**。它位于系统提示语的第一个位置，会替代预设的固定身份标识。
- 若系统中尚不存在 `SOUL.md` 文件，Hermes 会自动生成一个初始版本。
- 现有的用户 `SOUL.md` 文件绝不会被覆盖。
- Hermes 仅从 `HERMES_HOME` 目录加载 `SOUL.md` 文件。
- Hermes 不会搜索当前工作目录中的 `SOUL.md` 文件。
- 若 `SOUL.md` 存在但内容为空，或无法被加载，Hermes 会回退到内置的默认身份标识。
- 若 `SOUL.md` 包含有效内容，这些内容会在经过安全扫描和长度截断处理后原样注入。
- `SOUL.md` **不会**被复制到上下文文件列表中——它仅作为身份标识出现一次。

正因如此，`SOUL.md` 才是真正的“用户专属”或“实例专属”身份标识，而不仅仅是一个附加层。

## 为何采用此设计

这样的设计能够确保智能体的性格表现具有可预测性。

如果 Hermes 从用户启动它的任意目录加载 `SOUL.md`，那么在不同项目中，智能体的性格表现就可能会发生意外变化。通过仅从 `HERMES_HOME` 加载文件，智能体的性格便归属于该 Hermes 实例本身。

此外，这样的设计也有助于向用户进行说明：
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

请使用它来设定持久的语音风格与人格特征，例如：
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
- 临时的工作流程细节

这些内容应放在 `AGENTS.md` 中，而非 `SOUL.md`。

## 优秀的 SOUL.md 内容标准

一份优秀的 SOUL 文件应当具备以下特点：
- 在不同场景下保持稳定
- 范围足够广泛，可适用于多种对话
- 具体性足够强，能切实塑造独特的语音风格
- 侧重于沟通方式和人格特征，而非针对特定任务的指令

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

## Hermes 向提示词中注入的内容

`SOUL.md` 中的内容会直接被放入系统提示词的第 1 个插槽——即智能体身份位置，不会添加任何封装语言。

这些内容会经过以下处理：
- 提示词注入检测
- 若内容过长则进行截断

如果该文件为空、仅包含空白字符或无法读取，Hermes 会回退到内置的默认身份描述（“你是由 Nous Research 开发的 Hermes Agent。请直截了当回应：回复长度应与问题重要性相匹配……”）。在设置了 `skip_context_files` 时（例如在子智能体/任务委派场景中），也会采用此回退机制。

## 安全扫描

在纳入系统提示词之前，`SOUL.md` 会像其他包含上下文的文件一样，接受提示词注入模式的扫描。

因此，你仍应将其内容聚焦于角色设定与语气表达，而非试图暗中插入奇怪的元指令。

## SOUL.md 与 AGENTS.md 的区别

这是两者之间最重要的差异。

### SOUL.md
用于定义：
- 智能体身份
- 语气风格
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
- 若某内容需始终跟随智能体，应放入 `SOUL.md`
- 若某内容属于某个特定项目，应放入 `AGENTS.md`

## SOUL.md 与 `/personality` 的区别

`SOUL.md` 是智能体的持久默认人格设定。

而 `/personality` 是会话级别的临时覆盖设置，用于修改或补充当前的系统提示词。

因此：
- `SOUL.md` = 基准语音风格  
- `/personality` = 临时模式切换  

示例：  
- 保持默认的务实型 SOUL 风格，然后在辅导对话时使用 `/personality teacher`；  
- 保持简洁型的 SOUL 风格，然后在头脑风暴时使用 `/personality creative`。  

## 内置人格模式  

Hermes 提供了多种内置人格模式，可通过 `/personality` 命令进行切换。  

| 名称 | 描述 |
|------|------|
| **helpful** | 友好型通用助手 |
| **concise** | 简洁直接的回复风格 |
| **technical** | 专业详尽的技术专家风范 |
| **creative** | 具有创新思维的突破性想法 |
| **teacher** | 耐心指导并配有清晰示例的教育者 |
| **kawaii** | 可爱的语气、闪烁效果及满满热情 ★ |
| **catgirl** | 具有猫咪般表情的猫娘，会说“喵~” |
| **pirate** | 精通技术的海盗船长 Hermes |
| **shakespeare** | 具有戏剧张力的诗体文风 |
| **surfer** | 极度放松的潮人风格 |
| **noir** | 硬汉侦探式的叙述风格 |
| **uwu** | 用超可爱的语气表达极致萌感 |
| **philosopher** | 对每个问题都会进行深入思考 |
| **hype** | 充满无限能量与热情！！！ |

## 通过命令切换人格模式  

### CLI

```text
/personality
/personality concise
/personality technical
```

### 消息平台

```text
/personality teacher
```

这些虽是便捷的叠加配置，但除非相关叠加配置对默认人格进行了实质性修改，否则全局的 `SOUL.md` 文件依然会为 Hermes 设定永久性的默认人格。

## 在配置文件中自定义人格

内置的人格在任何场景下（CLI、消息平台、TUI 以及桌面应用）均可用。你可以在 `~/.hermes/config.yaml` 文件的 `agent.personalities` 部分添加自己定制的人格，或通过复用现有名称来覆盖内置人格。

```yaml
agent:
  personalities:
    codereviewer: >
      You are a meticulous code reviewer. Identify bugs, security issues,
      performance concerns, and unclear design choices. Be precise and constructive.
```

接着使用以下命令切换到该代理：

```text
/personality codereviewer
```

您所选择的性格设定会以名称形式存储在 `display.personality` 中。这些性格设定绝不会影响 `agent.system_prompt` —— 该字段专用于您自行编写的手动系统提示语，且仅在未选择任何性格设定时才会生效。

## 恢复为默认设置

若要取消当前激活的性格设定并恢复基础行为（即您的 `SOUL.md` 中定义的个性，以及您设置的 `agent.system_prompt`，如有），可使用以下任意方法：

```text
/personality none
/personality default
/personality neutral
```

这三者都会清除当前选定的人格设置（`display.personality`），该更改将在您发送下一条消息时立即生效。若不带参数运行`/personality`命令，除了会列出所有可用预设选项外，还会将当前启用的人格标记为`none`。

:::注意：升级后的单次重置
旧版本的Hermes在不同平台间保存人格状态的方式并不一致，这可能导致之前已关闭的人格设置再次被启用。在升级后的首次运行时，所有已保存的人格选择都会被重置为`none`（系统会显示已清除的特定人格）。如果您仍希望使用该人格，可通过`/personality <name>`命令重新启用它。而手动设置的`agent.system_prompt`内容则永远不会被修改。
:::

## 推荐的工作流程

一个理想的默认配置包括：
1. 在`~/.hermes/SOUL.md`中保存一份经过深思熟虑的全局配置文件`SOUL.md`
2. 将项目相关说明放在`AGENTS.md`文件中
3. 仅在需要临时切换模式时才使用`/personality`命令

这样的配置能为您带来：
- 稳定的对话风格
- 属于特定项目的行为模式
- 必要时的临时控制能力

## 人格设置与完整提示词之间的交互机制

从宏观层面来看，提示词堆栈包含以下部分：
1. **SOUL.md**（智能体身份标识——若不存在则使用内置的默认值）
2. 针对不同工具的行为指导
3. 记忆信息/用户上下文
4. 技能相关指导
5. 上下文文件（如`AGENTS.md`、`.cursorrules`）
6. 时间戳
7. 针对不同平台的格式化提示
8. 可选的系统提示词叠加内容，例如`/personality`

`SOUL.md`是整个系统的基石——所有其他元素都建立在其基础之上。

## 相关文档

- [上下文文件](/user-guide/features/context-files)  
- [配置设置](/user-guide/configuration)  
- [实用技巧与最佳实践](/guides/tips)  
- [SOUL.md 使用指南](/guides/use-soul-with-hermes)  

## CLI 显示样式与对话风格的分离  

对话风格与 CLI 显示样式是相互独立的：  
- `SOUL.md`、`agent.system_prompt` 以及 `/personality` 用于设定 Hermes 的对话方式；  
- `display.skin` 和 `/skin` 则用于控制 Hermes 在终端中的外观。  

如需了解终端显示样式的设置方法，请参阅 [皮肤与主题](./skins.md)。
