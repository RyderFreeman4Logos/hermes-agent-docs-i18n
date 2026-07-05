---
sidebar_position: 1
title: "Tips & Best Practices"
description: "Practical advice to get the most out of Hermes Agent — prompt tips, CLI shortcuts, context files, memory, cost optimization, and security"
---

# 提示与最佳实践

这是一系列实用技巧汇总，能帮助您更快更高效地使用 Hermes Agent。各章节针对不同方面——只需查看标题即可直接跳转到相关内容。

:::tip 不知道该选择哪个模型？
运行 `hermes setup --portal` —— 一个订阅即可获取包括 Claude、GPT-5 和 Gemini 在内的 300 多个模型。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

---

## 获得最佳结果

### 明确说明需求

模糊的提示会带来模糊的结果。与其说“修复代码”，不如具体说明为“修复 `api/handlers.py` 第 47 行的 TypeError —— `process_request()` 函数从 `parse_body()` 接收到的值为 `None`”。提供的上下文越详细，所需的迭代次数就越少。

### 提前提供背景信息

在请求中提前附上相关细节：文件路径、错误信息、预期行为。一条表述清晰的指令远胜于三轮反复确认。可直接粘贴错误堆栈跟踪——Agent 能够解析这些内容。

### 使用上下文文件保存重复指令

如果您发现自己需要反复重复相同的指令（如“请使用制表符而非空格”、“我们使用 pytest 工具”、“API 地址为 `/api/v2`”），可将它们写入 `AGENTS.md` 文件中。Agent 会在每次会话时自动读取该文件——设置完成后无需再费心重复。

### 允许 Agent 使用其内置工具

不必事事亲力亲为。与其说“打开 `tests/test_foo.py`，查看第 42 行，然后……”，不如直接要求“查找并修复失败的测试”。Agent 具备文件搜索、终端访问和代码执行功能——让它自行探索和迭代即可。

### 复杂工作流程中使用技能

在编写冗长的提示来说明操作步骤之前，先确认是否已有对应的技能。输入 `/skills` 可查看可用技能，或直接调用特定技能，如 `/axolotl` 或 `/github-pr-workflow`。

## CLI 高级用户技巧

### 多行输入

按 **Alt+Enter**、**Ctrl+J** 或 **Shift+Enter** 即可在不发送指令的情况下插入换行符。`Shift+Enter` 仅在终端将其视为独立按键时有效（默认情况下适用于 Kitty / foot / WezTerm / Ghostty；启用 Kitty 键盘协议后也适用于 iTerm2 / Alacritty / VS Code 终端）。前两种方式在所有终端中均适用。

### 粘贴内容检测

CLI 能自动识别多行粘贴内容。直接粘贴代码块或错误堆栈跟踪即可——系统不会将每行视为独立消息发送。粘贴内容会被暂存并作为一条完整消息发送。

### 中断与重定向

按一次 **Ctrl+C** 即可在 Agent 响应过程中中断操作。之后您可以输入新指令来重新引导它。若在 2 秒内再次按下 Ctrl+C，则可强制退出。当 Agent 开始偏离正确方向时，这一功能尤为实用。

### 使用 `-c` 继续上一次会话

忘记上一次会话的内容？运行 `hermes -c` 即可从上次中断处继续，所有对话历史都会被恢复。您也可以通过任务标题来继续会话：`hermes -r "我的研究项目"`。

### 粘贴剪贴板中的图片

按 **Ctrl+V** 即可将剪贴板中的图片直接粘贴到聊天窗口中。Agent 能够利用视觉功能分析截图、图表、错误弹窗或界面原型——无需先保存为文件。

### 斜杠命令自动补全

输入 `/` 后按 **Tab** 即可查看所有可用命令，包括内置命令（如 `/compress`、 `/model`、 `/title》）以及已安装的所有技能。无需记忆任何命令——Tab 自动补全功能能帮您搞定一切。

:::tip
使用 `/verbose` 可在工具输出显示模式之间切换：**关闭 → 新信息 → 全部显示 → 详细显示**。“全部显示”模式适合查看 Agent 的操作过程；“关闭”模式则更适合简单的问答场景。
:::

## 上下文文件

### AGENTS.md：您项目的大脑

在项目根目录创建一个 `AGENTS.md` 文件，其中可记录架构决策、编码规范以及项目特定的操作指南。该文件会自动注入到每次会话中，因此 Agent 始终了解项目的规则要求。

```markdown
# Project Context
- This is a FastAPI backend with SQLAlchemy ORM
- Always use async/await for database operations
- Tests go in tests/ and use pytest-asyncio
- Never commit .env files
```

### SOUL.md：自定义个性设定

希望Hermes拥有稳定的默认语音？请编辑`~/.hermes/SOUL.md`文件（如果您使用了自定义的Hermes安装路径，则为`$

```markdown
# Soul
You are a senior backend engineer. Be terse and direct.
Skip explanations unless asked. Prefer one-liners over verbose solutions.
Always consider error handling and edge cases.
```

请使用 `SOUL.md` 文件来定义智能体的持久性格特征，而 `AGENTS.md` 则用于存放针对特定项目的操作指南。

### .cursorrules 兼容性

您已拥有 `.cursorrules` 或 `.cursor/rules/*.mdc` 文件吗？Hermes 也能读取这些文件。无需重复设置编码规范——系统会自动从当前工作目录加载它们。

### 智能体发现机制

在会话开始时，Hermes 会加载当前工作目录中的顶层 `AGENTS.md` 文件。对于子目录中的 `AGENTS.md` 文件，则会在调用工具时（通过 `subdirectory_hints.py`）动态检测并将其内容注入到工具结果中——它们不会被提前加载到系统提示语中。

:::tip
请确保上下文文件简洁明了。由于这些内容会嵌入到每一条消息中，因此每个字符都会占用您的令牌预算。
:::

## 内存与技能

### 内存与技能：各司其职

**内存**用于存储事实性信息，如您的环境设置、偏好选项、项目路径以及智能体了解到的关于您的信息。而**技能**则用于存储流程性内容，比如多步骤工作流、针对特定工具的指令以及可复用的操作方案。用内存记录“是什么”，用技能定义“怎么做”。

### 何时创建技能

如果您发现某项任务需要5个以上步骤且会重复执行，可以让智能体为其创建一个技能。例如，您可以要求它“将你刚才的操作保存为一个名为 `deploy-staging` 的技能”。下次只需输入 `/deploy-staging`，智能体就会自动加载完整的操作流程。

### 管理内存容量

内存容量是有限制的（`MEMORY.md` 最多为约2,200字符，`USER.md` 最多为约1,375字符）。当内存占满时，智能体会对条目进行整合。您可以通过要求它“清理内存”或“替换旧的Python 3.9相关说明——我们现在使用的是3.12版本”来协助管理。

### 让智能体主动记忆

在高效完成一次会话后，您可以说“请记住这些内容，以便下次使用”，智能体就会保存关键要点。您也可以具体说明，比如“请将‘我们的CI流程使用GitHub Actions及`deploy.yml`工作流’这条信息存入内存中”。

:::warning
内存中的内容是静态快照——在会话期间所做的更改要等到下一次会话开始时才会反映在系统提示语中。虽然智能体会立即将更改写入磁盘，但提示语缓存不会在会话进行中失效。
:::

## 性能与成本控制

### 避免破坏提示语缓存

大多数大型语言模型服务提供商都会对对话开头部分（系统提示语+历史记录）进行缓存。如果保持系统提示语不变（即上下文文件和内存内容不变），则会话中的后续消息就能实现**缓存命中**，从而大幅降低成本。缓存是按模型和账户来标识的——因此，如果显式切换模型、使用[自动提供商回退功能](../user-guide/features/fallback-providers.md)或[凭证池轮换功能](../user-guide/features/credential-pools.md)，都会迫使系统在下一轮响应时重新读取整个对话内容，从而按全额价格计费。偶尔切换没问题，但在长时间会话中频繁切换则会大幅增加成本。

### 在达到限制前使用 /compress 功能

长时间的会话会导致令牌积累。当您发现响应变慢或被截断时，可以运行 `/compress` 命令。该命令会总结对话历史，在保留关键上下文的同时大幅减少令牌数量。您可以使用 `/usage` 命令查看当前的令牌使用情况。

### 通过任务委派实现并行处理

需要同时研究三个主题吗？可以让智能体使用 `delegate_task` 功能分配多个并行子任务。每个子智能体会在独立的上下文中运行，最终只返回汇总结果——这能极大降低主对话的令牌消耗。

### 使用 execute_code 处理批量操作

无需逐个执行终端命令，您可以让智能体编写一个脚本一次性完成所有操作。要求它“写一个Python脚本将所有 `.jpeg` 文件重命名为 `.jpg`，然后运行该脚本”，这种方式比逐一重命名文件更高效、成本更低。

### 选择合适的模型

可以使用 `/model` 命令在会话中途切换模型。对于复杂的推理和架构设计任务，建议使用前沿模型（如Claude Sonnet/Opus、GPT-4o）；而对于格式化、重命名或生成样板代码等简单任务，则可选择速度更快的模型。请注意，每次模型切换都会重置提示语缓存（见上文），因此在长时间会话中，直接使用另一款模型开始新会话往往比频繁切换更为经济。

:::tip
建议定期运行 `/usage` 命令查看令牌消耗情况。如需了解过去30天的详细使用模式，可运行 `/insights` 命令。
:::

## 消息传递技巧

### 设置主频道

在您常用的Telegram或Discord聊天频道中使用 `/sethome` 命令将其设为主频道。Cron作业的结果和定时任务的输出都会发送到这里。如果没有设置主频道，智能体就无处发送主动消息。

### 使用 /title 对会话进行分类

可以通过 `/title auth-refactor` 或 `/title research-llm-quantization` 等命令为会话命名。带有名称的会话可以通过 `hermes sessions list` 命令轻松查找，也可以通过 `hermes -r "auth-refactor"` 命令继续处理。未命名的会话则会越积越多，难以区分。

### 通过私信配对实现团队访问控制

无需手动收集用户ID来建立白名单，只需启用私信配对功能即可。当团队成员向机器人发送私信时，他们会收到一个一次性配对码。您可以使用 `hermes pairing approve telegram XKGH5N7P` 命令进行批准——这种方式既简单又安全。

### 工具执行进度显示模式

可以使用 `/verbose` 命令控制您看到的工具执行信息量。在消息平台中，通常“少即是多”——将显示模式设置为“new”即可仅查看新的工具调用记录。在命令行界面中，将模式设置为“all”则可以实时查看智能体的所有操作。

:::tip
在消息平台上，会话会在空闲一段时间后（默认为24小时）或每天凌晨4点自动重置。如果需要更长的会话时间，可以在 `~/.hermes/config.yaml` 文件中根据不同平台进行相应设置。
:::

## 安全性

### 对于不可信代码，使用Docker容器

在处理不可信的代码库或运行未知代码时，建议使用Docker或Daytona作为终端后端。在您的 `.env` 文件中设置 `TERMINAL_BACKEND=docker`。这样，容器内的破坏性命令就无法损害您的主机系统。

```bash
# In your .env:
TERMINAL_BACKEND=docker
TERMINAL_DOCKER_IMAGE=hermes-sandbox:latest
```

### 规避 Windows 编码问题

在 Windows 系统中，某些默认编码（如 `cp125x`）无法表示所有的 Unicode 字符，这会在通过测试或脚本写入文件时引发 `UnicodeEncodeError` 错误。

- 建议以显式的 UTF-8 编码来打开文件：

```python
with open("results.txt", "w", encoding="utf-8") as f:
    f.write("✓ All good\n")
```

- 在 PowerShell 中，您还可以将当前会话的控制台输出及原生命令输出格式更改为 UTF-8。

```powershell
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
```

这能确保 PowerShell 及其子进程始终使用 UTF-8 编码，从而有效避免仅限于 Windows 环境下出现的故障。

### 选择“始终允许”前请谨慎考虑

当代理触发危险命令审批时（如 `rm -rf`、`DROP TABLE` 等），系统会提供四种选项：**单次允许**、**会话期间允许**、**始终允许**以及**拒绝**。在选择“始终允许”之前请务必深思熟虑——该选项会永久将该命令模式加入允许列表。建议先从“会话期间允许”开始使用，直到您对其效果十分熟悉为止。

### 命令审批是您的安全保障

Hermes 会在执行任何命令之前，将其与经过筛选的危险命令模式列表进行比对。这些危险模式包括递归删除、SQL 数据库删除、将 curl 命令通过管道传递给 shell 等等。在生产环境中切勿禁用此功能——它的存在自有其重要原因。

:::warning
在基于容器后端（如 Docker、Singularity、Modal、Daytona）的环境中运行时，由于容器本身即构成了安全边界，危险命令检查将会**被跳过**。请确保您的容器镜像已做好充分的安全加固。
:::

### 为消息机器人使用允许列表

切勿在具有终端访问权限的机器人上设置 `GATEWAY_ALLOW_ALL_USERS=true`。应始终使用特定于平台的允许列表（如 `TELEGRAM_ALLOWED_USERS`、`DISCORD_ALLOWED_USERS`）或私信配对功能，来控制哪些用户可以与您的代理进行交互。

```bash
# Recommended: explicit allowlists per platform
TELEGRAM_ALLOWED_USERS=123456789,987654321
DISCORD_ALLOWED_USERS=123456789012345678

# Or use cross-platform allowlist
GATEWAY_ALLOWED_USERS=123456789,987654321
```

如果您有值得收录到此页面的实用建议？欢迎提交问题或 Pull Request——我们诚邀社区成员的贡献。
