---
sidebar_position: 1
title: "Tips & Best Practices"
description: "Practical advice to get the most out of Hermes Agent — prompt tips, CLI shortcuts, context files, memory, cost optimization, and security"
---

# 实用技巧与最佳实践

这是一份精选的实用技巧集，能帮助您更快更高效地使用 Hermes Agent。各部分针对不同方面——只需查看标题即可直接跳转到相关内容。

:::tip 不知道该选择哪个模型？
运行 `hermes setup --portal` 即可——同一订阅即可使用包括 Claude、GPT-5 和 Gemini 在内的 300 多个模型。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

---

## 获得最佳结果

### 明确说明需求

模糊的提示会带来模糊的结果。与其说“修复代码”，不如具体指出“修复 `api/handlers.py` 第 47 行的 TypeError 问题——`process_request()` 函数从 `parse_body()` 接收到的参数为 `None`”。提供的上下文越详细，所需的迭代次数就越少。

### 提前提供完整背景信息

在请求中提前附上相关细节：文件路径、错误信息、期望的行为表现。一条表述清晰的指令远胜于三轮反复确认。可直接粘贴错误堆栈信息——Agent 可以直接解析这些内容。

### 为重复性指令使用上下文文件

如果您经常需要重复说明相同的要求（如“请使用制表符而非空格”、“我们使用 pytest 工具”、“API 地址为 `/api/v2`”），可将这些内容写入 `AGENTS.md` 文件中。Agent 会在每次会话时自动读取该文件——设置完成后无需再费心重复说明。

### 允许 Agent 使用其内置工具

无需逐步骤手把手指导。与其说“打开 `tests/test_foo.py`，查看第42行，然后……”，不如直接要求“找到并修复失败的测试”。该智能体具备文件搜索、终端访问和代码执行功能——让它自行探索并迭代即可。

### 利用技能处理复杂工作流

在编写冗长的提示语来说明操作步骤之前，先确认是否已有对应的技能。输入 `/skills` 可查看可用技能，或直接调用特定技能，例如 `/axolotl` 或 `/github-pr-workflow`。

## CLI 高级用户技巧

### 多行输入

按 **Alt+Enter**、**Ctrl+J** 或 **Shift+Enter** 即可在不发送消息的情况下插入换行符。`Shift+Enter` 仅在终端将其视为独立按键时有效（默认情况下适用于 Kitty / foot / WezTerm / Ghostty；启用 Kitty 键盘协议后也适用于 iTerm2 / Alacritty / VS Code 终端）。前两种方式在所有终端中均适用。

### 粘贴内容识别

CLI 能自动识别多行粘贴的内容。直接粘贴代码块或错误堆栈即可——系统不会将每行视为独立消息发送，而是将整个粘贴内容缓存后作为一条消息发送。

### 中断与重定向

按一次 **Ctrl+C** 即可在智能体响应过程中中断操作，随后可输入新消息来重新引导它。若在2秒内再次按下 Ctrl+C，则会强制终止进程。当智能体开始偏离正确方向时，这一功能尤为实用。

### 使用 `-c` 恢复会话

上次会话中遗漏了什么内容？只需运行 `hermes -c` 即可从暂停处继续，所有对话历史都会完整恢复。您也可以通过标题来继续对话：`hermes -r "我的研究项目"`。

### 粘贴剪贴板中的图片

按下 **Ctrl+V** 即可将剪贴板中的图片直接粘贴到聊天界面中。该智能体具备图像分析功能，能够识别截图、图表、错误提示或用户界面原型——无需先将其保存为文件。

### 斜杠命令自动补全

输入 `/` 后按 **Tab** 键即可查看所有可用命令，其中包括内置命令（如 `/compress`、`/model`、`/title`）以及所有已安装的智能体技能。您无需记住任何命令，Tab 自动补全功能能帮您轻松完成操作。

:::提示
使用 `/verbose` 可在不同的工具输出显示模式间切换：**关闭 → 新内容 → 全部显示 → 详细显示**。“全部显示”模式非常适合查看智能体的处理过程；而“关闭”模式则最适合简单的问答场景。
:::

## 上下文文件

### AGENTS.md：您项目的大脑

在项目根目录下创建一个 `AGENTS.md` 文件，其中可记录架构决策、编码规范以及项目特定的操作指南。该文件会自动被注入到每个会话中，这样智能体就能始终了解您项目的规则。

```markdown
# Project Context
- This is a FastAPI backend with SQLAlchemy ORM
- Always use async/await for database operations
- Tests go in tests/ and use pytest-asyncio
- Never commit .env files
```

### SOUL.md：自定义人格设定

希望Hermes拥有稳定的默认语音？请编辑`~/.hermes/SOUL.md`文件（如果您使用了自定义的Hermes安装路径，则为`$/HERMES_HOME/SOUL.md`）。现在，Hermes会自动生成一个初始的SOUL配置文件，并将该全局文件作为整个实例的人格设定来源。

如需详细操作指南，请参阅[在Hermes中使用SOUL.md](/guides/use-soul-with-hermes)。

```markdown
# Soul
You are a senior backend engineer. Be terse and direct.
Skip explanations unless asked. Prefer one-liners over verbose solutions.
Always consider error handling and edge cases.
```

如需持久保留智能体的个性特征，请使用 `SOUL.md` 文件；若需针对特定项目编写操作说明，则可使用 `AGENTS.md`。

### .cursorrules 兼容性

您已拥有 `.cursorrules` 或 `.cursor/rules/*.mdc` 文件？Hermes 也能读取这些文件。无需重复定义编码规范——系统会自动从工作目录中加载它们。

### 检索机制

在会话启动时，Hermes 会首先加载当前工作目录中的顶层 `AGENTS.md` 文件。而子目录中的 `AGENTS.md` 文件则会在调用工具时（通过 `subdirectory_hints.py`）被动态检测并嵌入到工具结果中——它们不会提前加载到系统提示语中。

:::提示
请确保上下文文件简洁明了。由于这些内容会嵌入到每一条消息中，因此每个字符都会占用您的令牌额度。
:::

## 内存与技能

### 内存与技能：各司其职

**内存**用于存储事实性信息，如您的环境设置、偏好选项、项目路径以及智能体了解到的关于您的各种信息。而**技能**则用于存储流程化指令，包括多步骤工作流、特定工具的操作指南以及可重复使用的方案。对于“是什么”的问题，可使用内存；对于“如何做”的问题，则应使用技能。

### 何时创建技能

如果您发现某项任务需要5个以上步骤且会反复执行，可以让智能体为其创建一个技能。例如，您可以要求它“将你刚刚完成的操作保存为一个名为 `deploy-staging` 的技能”。下次只需输入 `/deploy-staging`，智能体就会自动加载完整的操作流程。

### 管理内存容量

内存容量是有意限制的（MEMORY.md 文件上限约为 2,200 个字符，USER.md 文件上限约为 1,375 个字符）。当内存被占满时，智能体会合并相关记录。您可以通过输入“清理你的内存”或“替换旧的 Python 3.9 相关说明——我们现在使用的是 3.12 版本”来协助处理。

### 让智能体记住内容

在高效的对话结束后，只需说“下次记得这些内容”，智能体就会保存其中的重点信息。您也可以给出更具体的指示，例如：“将‘我们的持续集成流程使用 GitHub Actions 及 `deploy.yml` 工作流’这一信息保存到内存中。”

:::warning
内存存储的是固定快照——在当前对话过程中所做的更改要等到下一次对话开始时才会显示在系统提示中。虽然智能体会立即将内容写入磁盘，但系统提示缓存并不会在对话进行中失效。
:::

## 性能与成本

### 避免破坏提示缓存

大多数大型语言模型服务提供商都会对对话开头部分（系统提示 + 对话历史）进行缓存。如果您保持系统提示的稳定性（使用相同的上下文文件和相同的内存配置），那么在同一个对话中的后续消息就能触发**缓存命中**，从而大幅降低成本。提示缓存的键由模型和账户唯一标识——因此，若显式切换模型、使用[自动提供商回退功能](../user-guide/features/fallback-providers.md)或进行[凭证池轮换](../user-guide/features/credential-pools.md)，都会迫使智能体在下次回应时重新读取整个对话内容，从而按全额输入费用计费。偶尔切换模型问题不大；但在长时间对话中频繁切换则会大幅增加成本。

### 在达到限制前使用 /compress 功能

在长时间的对话过程中，会不断积累令牌。当您发现响应速度变慢或内容被截断时，可以运行 `/compress` 命令。该命令会总结对话历史，在保留关键上下文的同时大幅减少令牌使用量。您可以使用 `/usage` 查看当前的令牌剩余情况。

### 通过任务分派实现并行处理

需要同时研究三个主题？可以让智能体使用 `delegate_task` 功能将任务拆分为多个并行子任务。每个子智能体会在独立的上下文中运行，最终只返回汇总结果——这能极大降低主对话的令牌消耗。

### 利用代码执行功能进行批量操作

无需逐一执行终端命令，您可以让智能体编写一个脚本一次性完成所有操作。例如，要求其“编写一个 Python 脚本将所有 `.jpeg` 文件重命名为 `.jpg` 并运行该脚本”，这种方式比逐个重命名文件更高效快捷。

### 选择合适的模型

您可以使用 `/model` 命令在对话过程中切换模型。对于需要复杂推理或架构决策的任务，建议使用前沿模型（如 Claude Sonnet/Opus、GPT-4o）；而对于格式化、重命名或生成模板等简单任务，则可选择速度更快的模型。请注意，每次模型切换都会重置提示词缓存（见上文），因此在长时间对话中，直接使用另一款模型开启新对话往往比频繁切换更为经济高效。

:::提示
定期运行 `/usage` 命令即可查看您的令牌使用情况。若需了解过去30天的整体使用模式，可运行 `/insights`。在开始任何对话之前——无论涉及系统提示、技能索引、内存还是工具结构——若想先知晓每条消息的*固定*成本，可使用 [`hermes prompt-size`](/reference/cli-commands#hermes-prompt-size) 命令（离线环境下也可使用）。
:::

## 消息传递技巧

### 设置主频道
在您常用的 Telegram 或 Discord 聊天频道中使用 `/sethome` 命令将其设为主频道。系统会将该频道作为发送定时任务结果及计划任务输出的内容载体。若未设置主频道，智能体将无处发送主动消息。

### 使用 /title 对会话进行分类
可通过 `/title auth-refactor` 或 `/title research-llm-quantization` 为会话命名。这样使用 `hermes sessions list` 命令即可轻松查找特定会话，也可通过 `hermes -r "auth-refactor"` 恢复该会话。未命名的会话则会越来越多，难以区分。

### 通过私信配对实现团队访问控制
无需手动收集用户 ID 制作白名单，只需启用私信配对功能即可。当团队成员向机器人发送私信时，他们会收到一个一次性配对码。您只需使用 `hermes pairing approve telegram XKGH5N7P` 即可批准，既简单又安全。

### 工具操作显示模式
使用 `/verbose` 命令可控制您看到的工具操作信息量。在消息平台中，通常越简洁越好——将显示模式设置为“new”即可仅查看新的工具调用记录。而在命令行界面中，选择“all”模式则能实时全面地了解智能体的所有操作。

:::提示
消息会话会一直保持有效，直到用户明确发出 `/new` 或 `/reset` 命令。上下文压缩功能可帮助处理长篇对话，无需手动设置空闲计时或每日重置。
:::

## 安全性

### 对于不可信代码，请使用 Docker

在处理不可信的代码库或运行未知程序时，建议将 Docker 或 Daytona 作为终端后端。在您的 `.env` 文件中设置 `TERMINAL_ENV=docker`。容器内的破坏性命令不会对主机系统造成损害。

```bash
# In your .env:
TERMINAL_ENV=docker
TERMINAL_DOCKER_IMAGE=hermes-sandbox:latest
```

### 规避 Windows 编码问题

在 Windows 系统中，某些默认编码（如 `cp125x`）无法表示所有的 Unicode 字符，这会在通过测试或编写脚本时导致 `UnicodeEncodeError` 错误。

- 建议以显式的 UTF-8 编码来打开文件：

```python
with open("results.txt", "w", encoding="utf-8") as f:
    f.write("✓ All good\n")
```

- 在 PowerShell 中，您还可以将当前会话的控制台输出及原生命令输出格式更改为 UTF-8。

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
```

这样能确保 PowerShell 及其子进程始终使用 UTF-8 编码，从而避免仅发生在 Windows 环境下的故障。

### 选择“始终允许”前请慎重考虑

当代理触发危险命令审批（如 `rm -rf`、`DROP TABLE` 等）时，系统会提供四种选项：**仅一次**、**当前会话**、**始终允许**、**拒绝**。在选择“始终允许”之前请务必三思——该选项会永久将该命令模式加入允许列表。建议先从“当前会话”选项开始使用，直到您熟悉其效果为止。

### 命令审批是您的安全保障

Hermes 会在执行任何命令之前，将其与精心整理的危险命令模式列表进行比对。这些危险模式包括递归删除、SQL 数据表删除、将 curl 输出传递给 shell 等操作。在生产环境中切勿禁用此功能——它存在是有充分理由的。

:::warning
在基于容器的后端环境（如 Docker、Singularity、Modal、Daytona）中运行时，由于容器本身即构成了安全边界，危险命令检查将会**被跳过**。请确保您的容器镜像已做好充分的安全配置。
:::

### 为消息机器人使用允许列表

切勿在具有终端访问权限的机器人上设置 `GATEWAY_ALLOW_ALL_USERS=true`。应始终使用平台特定的允许列表（如 `TELEGRAM_ALLOWED_USERS`、`DISCORD_ALLOWED_USERS`）或私信配对功能，来控制哪些用户可以与您的代理进行交互。

```bash
# Recommended: explicit allowlists per platform
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=123456789012345678

# Or use cross-platform allowlist
GATEWAY_ALLOWED_USERS=123456789,987654321
```

如果您有值得收录到此页面的建议？欢迎提交问题或 Pull Request——我们非常期待来自社区的贡献。
