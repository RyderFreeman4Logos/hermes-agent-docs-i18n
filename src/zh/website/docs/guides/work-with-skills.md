---
sidebar_position: 12
title: "Working with Skills"
description: "Find, install, use, and create skills — on-demand knowledge that teaches Hermes new workflows"
---

# 使用技能

技能是一种按需提供的知识文档，用于指导Hermes如何处理各种特定任务——从生成ASCII艺术到管理GitHub拉取请求。本指南将为您详细介绍如何在日常工作中使用它们。

如需完整的技术参考资料，请参阅[技能系统](/user-guide/features/skills)。

---

## 查找技能

每个Hermes安装版本都自带一些预置的技能。快来查看有哪些技能可供使用：

```bash
# In any chat session:
/skills

# Or from the CLI:
hermes skills list
```

此处会显示一个包含名称与描述的内嵌列表：

```
ascii-art         Generate ASCII art using pyfiglet, cowsay, boxes...
arxiv             Search and retrieve academic papers from arXiv...
github-pr-workflow Full PR lifecycle — create branches, commit...
plan              Plan mode — inspect context, write a markdown...
excalidraw        Create hand-drawn style diagrams using Excalidraw...
```

### 搜索技能

```bash
# Search by keyword
/skills search docker
/skills search music
```

### 技能中心

官方提供的可选技能（那些体积较大或属于小众领域的技能默认处于未启用状态）均可通过该中心获取：

```bash
# Browse official optional skills
/skills browse

# Search the hub
/skills search blockchain
```

## 使用技能

所有已安装的技能都会自动成为斜杠命令。只需输入其名称即可：

```bash
# Load a skill and give it a task
/ascii-art Make a banner that says "HELLO WORLD"
/plan Design a REST API for a todo app
/github-pr-workflow Create a PR for the auth refactor

# Just the skill name (no task) loads it and lets you describe what you need
/excalidraw
```

您也可以通过自然对话来触发特定技能——只需告知Hermes使用某个特定技能，它就会通过`skill_view`工具加载该技能。

### 逐步展示机制

这些技能采用高效的令牌加载模式，智能体不会一次性加载所有内容：

1. **`skills_list()`** — 所有技能的精简列表（约3千个令牌），在会话开始时加载。
2. **`skill_view(name)`** — 某个特定技能的完整SKILL.md文件内容，当智能体判断需要该技能时才会加载。
3. **`skill_view(name, file_path)`** — 该技能中的某个具体参考文件，仅在实际需要时才加载。

这意味着，这些技能在真正被使用之前不会消耗任何令牌。

---

## 通过Hub进行安装

Hermes虽预装了官方提供的可选技能，但默认处于未激活状态。如需使用，需手动进行安装：

```bash
# Install an official optional skill
hermes skills install official/research/arxiv

# Install from the hub in a chat session
/skills install official/creative/songwriting-and-ai-music

# Install a single-file SKILL.md directly from any HTTP(S) URL
hermes skills install https://sharethis.chat/SKILL.md
/skills install https://example.com/SKILL.md --name my-skill
```

具体流程如下：
1. 技能目录会被复制到 `~/.hermes/skills/` 目录中；
2. 该技能会显示在您的 `skills_list` 输出结果中；
3. 此时即可通过斜杠命令来调用该技能。

:::提示
已安装的技能会在新会话中生效。若希望其在当前会话中也可用，可执行 `/reset` 重新启动会话，或添加 `--now` 参数立即清除提示词缓存（但这会导致下一轮需要消耗更多令牌）。
:::

### 验证安装情况

```bash
# Check it's there
hermes skills list | grep arxiv

# Or in chat
/skills search arxiv
```

## 插件提供的技能

插件可以使用命名空间格式（`plugin:skill`）来封装自身的技能，从而避免与内置技能发生名称冲突。

```bash
# Load a plugin skill by its qualified name
skill_view("superpowers:writing-plans")

# Built-in skill with the same base name is unaffected
skill_view("writing-plans")
```

插件技能**不会**被列在系统提示词中，也不会出现在 `skills_list` 中。这类技能是可选的——只有当您确定某个插件提供了相关技能时，才需要显式加载它。一旦加载成功，智能体就会看到一个横幅，列出该插件下的其他关联技能。

关于如何在自己的插件中集成技能，请参阅[构建 Hermes 插件 → 打包技能](/guides/build-a-hermes-plugin#bundle-skills)。

---

## 配置技能设置

某些技能会在其前置文本中声明所需的配置参数：

```yaml
metadata:
  hermes:
    config:
      - key: tenor.api_key
        description: "Tenor API key for GIF search"
        prompt: "Enter your Tenor API key"
        url: "https://developers.google.com/tenor/guides/quickstart"
```

当首次加载带有配置的技能时，Hermes会提示您输入相关数值。这些数值会被存储在`config.yaml`文件中的`skills.config.*`路径下。

可通过CLI来管理技能配置：

```bash
# Interactive config for a specific skill
hermes skills config gif-search

# View all skill config
hermes config show | grep '^skills\.config'
```

## 创建自定义技能

技能实际上只是包含 YAML 前置信息的 Markdown 文件。创建一个技能仅需不到五分钟的时间。

### 1. 创建目录

```bash
mkdir -p ~/.hermes/skills/my-category/my-skill
```

### 2. 编写 SKILL.md 文件

```markdown title="~/.hermes/skills/my-category/my-skill/SKILL.md"
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
metadata:
  hermes:
    tags: [my-tag, automation]
    category: my-category
---

# My Skill

## When to Use
Use this skill when the user asks about [specific topic] or needs to [specific task].

## Procedure
1. First, check if [prerequisite] is available
2. Run `command --with-flags`
3. Parse the output and present results

## Pitfalls
- Common failure: [description]. Fix: [solution]
- Watch out for [edge case]

## Verification
Run `check-command` to confirm the result is correct.
```

### 3. 添加参考文件（可选）

技能可以包含代理按需加载的辅助文件：

```
my-skill/
├── SKILL.md                    # Main skill document
├── references/
│   ├── api-docs.md             # API reference the agent can consult
│   └── examples.md             # Example inputs/outputs
├── templates/
│   └── config.yaml             # Template files the agent can use
└── scripts/
    └── setup.sh                # Scripts the agent can execute
```

请在您的 SKILL.md 文件中参考这些内容：

```markdown
For API details, load the reference: `skill_view("my-skill", "references/api-docs.md")`
```

### 4. 进行测试

启动一个新会话，然后尝试使用您的技能：

```bash
hermes chat -q "/my-skill help me with the thing"
```

该技能会自动启用，无需进行任何注册操作。只需将其放入 `~/.hermes/skills/` 目录中，即可立即使用。

:::info
该智能体还可以通过 `skill_manage` 功能自行创建和更新技能。在解决完复杂问题后，Hermes 可能会建议将相应的解决方案保存为技能，以便日后使用。
:::

---

## 各平台独立的技能管理

可控制哪些技能在哪些平台上可用：

```bash
hermes skills
```

这将打开一个交互式 TUI 界面，让你能够针对不同平台（CLI、Telegram、Discord 等）分别开启或关闭特定技能。当你需要让某些技能仅在特定场景下可用时，此功能非常实用——例如，避免在 Telegram 上启用开发相关技能。

---

## 技能与记忆

二者都会在会话之间保持持久性，但功能各异：

| | 技能 | 记忆 |
|---|---|---|
| **内容** | 过程性知识——即如何执行某项操作 | 事实性知识——即事物的基本情况 |
| **加载时机** | 仅在需要时按需加载 | 自动注入到每个会话中 |
| **规模** | 可能很大（数百行代码） | 应保持简洁（仅存储关键事实） |
| **资源消耗** | 加载前无需消耗令牌 | 消耗少量但固定的令牌成本 |
| **示例** | “如何将应用部署到 Kubernetes” | “用户偏好深色模式，所在时区为太平洋标准时间” |
| **创建者** | 你、智能体，或从 Hub 安装的技能 | 智能体根据对话内容自动生成 |

**经验法则：** 如果内容适合放在参考文档中，那就是技能；如果更适合写在便签上，那就是记忆。

---

## 实用建议

**让技能具备针对性。** 试图涵盖“所有 DevOps 内容”的技能往往会过于冗长且模糊不清。而像“将 Python 应用部署到 Fly.io”这类具体明确的技能，才真正具有实用价值。

**允许智能体创建技能。** 在完成复杂的多步骤任务后，Hermes 通常会提议将处理方法保存为技能。建议接受——这些由智能体生成的技能能够完整记录整个工作流程，包括过程中发现的各类问题。

**使用分类机制。** 将技能整理到子目录中（如 `~/.hermes/skills/devops/`、`~/.hermes/skills/research/` 等）。这样既能便于管理，也能帮助智能体更快找到相关技能。

**及时更新过时的技能。** 如果使用某项技能时遇到了它未涵盖的问题，可告知 Hermes 根据你的经验来更新该技能。未被维护的技能只会成为负担。

---

*如需了解完整的技能参考信息——包括前置字段、条件激活、外部目录等功能，请参阅 [技能系统](/user-guide/features/skills)。*
