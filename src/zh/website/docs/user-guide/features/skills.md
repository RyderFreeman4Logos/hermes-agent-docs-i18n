---
sidebar_position: 2
title: "Skills System"
description: "On-demand knowledge documents — progressive disclosure, agent-managed skills, and the Skills Hub"
---

# 技能系统

技能是代理在需要时可以加载的按需知识文档。它们采用**渐进式展示**模式，以减少令牌使用量，并且兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。

所有技能都存储在 **`~/.hermes/skills/`** 目录中——这是主要的存储位置及权威数据源。在首次安装时，预置的技能会从仓库中复制到该目录。通过 Hub 安装的技能以及代理自行创建的技能也会存放在此处。代理可以修改或删除任何技能。

您还可以指定**外部技能目录**——即与本地目录一同扫描的其他文件夹。详情请参见下文的[外部技能目录](#external-skill-directories)。

另请参阅：

- [预置技能目录](/reference/skills-catalog)
- [官方可选技能目录](/reference/optional-skills-catalog)

## 从空白状态开始

默认情况下，每个配置文件都会包含预置的技能目录，而每次执行 `hermes update` 操作都会添加新预置的技能。如果您希望创建一个**不包含任何预置技能**、且在各次更新后仍保持空状态的配置文件，有以下两种方法：

**在安装时**（适用于默认的 `~/.hermes` 配置文件）：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --no-skills
```

**在创建配置文件时**（针对命名配置文件）：

```bash
hermes profile create research --no-skills
```

**在已安装的配置文件**（默认配置或自定义名称）上，可在运行时切换其状态：

```bash
hermes skills opt-out            # stop future seeding — nothing on disk is touched
hermes skills opt-out --remove   # also delete UNMODIFIED bundled skills (confirms first)
hermes skills opt-in --sync      # undo: remove the marker and re-seed now
```

以上三种方式都会在配置目录中写入一个`.no-bundled-skills`标记。只要该标记存在，安装程序、`hermes update`命令以及任何技能同步操作都会跳过对该配置文件中的内置技能的初始化过程。如需重新启用此功能，可删除该标记（或运行`hermes skills opt-in`命令）。

:::注意：默认安全设置
`hermes skills opt-out`仅会阻止*后续*的技能初始化——它绝不会删除磁盘上已存在的任何内容。可选的`--remove`参数仅会在内置技能未被修改（与Hermes安装版本完全一致）时才将其删除。您自行编辑过的技能、从Hub安装的技能以及您自己编写的技能将始终会被保留。
:::

## 使用技能

所有已安装的技能都会自动作为斜杠命令可用：

```bash
# In the CLI or any messaging platform:
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor
/plan design a rollout for migrating our auth provider

# Just the skill name loads it and lets the agent ask what you need:
/excalidraw
```

内置的 `plan` 技能就是一个很好的例子。运行命令 `/plan [request]` 后，系统会加载该技能的指令，指示 Hermes 在必要时检查上下文信息，生成一份 Markdown 格式的执行计划而非直接执行任务，并将结果保存在当前工作空间或后端工作目录下的 `.hermes/plans/` 文件夹中。

此外，您也可以通过自然对话的方式与这些技能进行交互：

```bash
hermes chat --toolsets skills -q "What skills do you have?"
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

## 从各种来源学习技能（`/learn`）

`/learn` 是一种高效的方法，无需手动编写 `SKILL.md` 文件，即可将您已掌握的知识或大量参考资料转化为可重复使用的技能。该功能具有高度灵活性：只要能描述清楚目标内容，智能体就能利用现有工具收集相关资料，进而按照[官方技能编写标准](#skillmd-format)生成技能文件（描述部分长度不超过60个字符，结构遵循标准顺序，使用Hermes工具框架，且不得创建自定义命令）。

```bash
# A local SDK or doc directory — read with read_file / search_files
/learn the REST client in ~/projects/acme-sdk, focus on auth + pagination

# An online doc page — fetched with web_extract
/learn https://docs.example.com/api/quickstart

# The workflow you just walked the agent through in this conversation
/learn how I just deployed the staging server

# Pasted notes / a described procedure
/learn filing an expense: open the portal, New > Expense, attach the receipt, submit
```

由于实时客服会负责数据获取，因此 `/learn` 功能在 CLI、消息网关、TUI 以及控制面板中均可正常使用——无论终端后端是本地的、Docker 环境的还是远程的，因为无需单独的数据接入引擎。在**控制面板**的“技能”页面上，有一个“学习技能”按钮，点击后会弹出一个面板，其中包含目录输入框、URL 输入框以及一个开放式文本框；该功能会构建一个 `/learn` 请求，并在聊天界面中执行它。

此过程不会留下任何模型工具的痕迹：`/learn` 会生成符合标准规范的提示语，然后将其作为普通对话轮次传递给客服。客服会使用 `skill_manage` 工具保存学习结果，因此如果启用了[内容审核机制](#gating-agent-skill-writes-skillswrite_approval)，该机制也会随之生效。

## 逐步展示功能

技能系统采用了高效节省令牌的加载方式：

```
Level 0: skills_list()           → [{name, description, category}, ...]   (~3k tokens)
Level 1: skill_view(name)        → Full content + metadata       (varies)
Level 2: skill_view(name, path)  → Specific reference file       (varies)
```

该智能体仅在实际需要时才会加载完整的技能内容。

## SKILL.md 格式规范

```markdown
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
platforms: [macos, linux]     # Optional — restrict to specific OS platforms
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    fallback_for_toolsets: [web]    # Optional — conditional activation (see below)
    requires_toolsets: [terminal]   # Optional — conditional activation (see below)
    config:                          # Optional — config.yaml settings
      - key: my.setting
        description: "What this controls"
        default: "value"
        prompt: "Prompt for setup"
---

# Skill Title

## When to Use
Trigger conditions for this skill.

## Procedure
1. Step one
2. Step two

## Pitfalls
- Known failure modes and fixes

## Verification
How to confirm it worked.
```

### 平台专用技能

通过 `platforms` 字段，技能可被限定为仅在特定操作系统上运行：

| 值 | 匹配的系统 |
|-------|----------|
| `macos` | macOS（Darwin） |
| `linux` | Linux |
| `windows` | Windows |

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders, FindMy)
platforms: [macos, linux]     # macOS and Linux
```

一旦设置，该技能将自动在系统提示、`skills_list()` 函数以及不兼容平台上的斜杠命令中隐藏。若未进行设置，则该技能会在所有平台上加载。

## 技能输出与媒体文件传输

当技能响应（或任何智能体响应）包含媒体文件的绝对路径时——例如 `/home/user/screenshots/diagram.png`——网关会自动识别该路径，将其从可见文本中剔除，并直接将文件以原生形式发送到用户的聊天界面中（如 Telegram 的图片、Discord 的附件等），而不会在消息中留下原始路径。

针对音频文件，`[[audio_as_voice]]` 指令可在支持该功能的平台（如 Telegram、WhatsApp）上将音频文件以原生语音消息气泡的形式呈现。

### 强制以文档形式传输：`[[as_document]]`

有时您可能希望获得与内联预览相反的效果：希望将文件作为可下载的附件发送，而非重新压缩后的图片气泡。典型的应用场景是高分辨率截图或图表——Telegram 的 `sendPhoto` 功能会将其重新压缩至约 200 KB 且分辨率为 1280 像素，从而导致内容难以辨识。而通过 `sendDocument` 发送的 1-2 MB PNG 文件则能完整保留原始数据。

如果响应内容（或其中的任何文本，通常为最后一行）包含指令 `[[as_document]]`，则从该响应中提取的所有媒体路径都会作为文档/文件附件发送，而非图片气泡形式：

```
Here is your rendered chart:

/home/user/.hermes/cache/chart-q4-2025.png

[[as_document]]
```

该指令会在内容传递之前被移除，因此用户永远无法看到它。其设计原则是每次响应都采用“全有或全无”的处理方式：仅输出一次`[[as_document]]`，同一响应中的每个图片路径都会作为独立文档被发送。这一机制与`[[audio_as_voice]]`的功能范围类似。

在以下情况下，可在技能中使用该指令：
- 当你需要以文件形式生成用户所需的截图或图表（以便在其他工具中编辑、归档或完整分享）；
- 默认的有损预览会掩盖细节（如小字体文字、高精度像素图以及对颜色敏感的渲染结果）。

那些没有独立文档路径的平台（例如短信服务）则会退而使用其现有的附件传输机制。

### 条件激活（备用技能）

技能可以根据当前会话中可用的工具自动显示或隐藏。这一功能对于**备用技能**尤为实用——这类免费或本地的替代方案仅应在高级工具不可用时才出现。

```yaml
metadata:
  hermes:
    fallback_for_toolsets: [web]      # Show ONLY when these toolsets are unavailable
    requires_toolsets: [terminal]     # Show ONLY when these toolsets are available
    fallback_for_tools: [web_search]  # Show ONLY when these specific tools are unavailable
    requires_tools: [terminal]        # Show ONLY when these specific tools are available
```

| 字段 | 行为 |
|-------|----------|
| `fallback_for_toolsets` | 当列出的工具集可用时，该技能将**隐藏**；若这些工具集缺失，则会显示。 |
| `fallback_for_tools` | 规则相同，但会检查单个工具而非工具集。 |
| `requires_toolsets` | 当列出的工具集不可用时，该技能将**隐藏**；若这些工具集存在，则会显示。 |
| `requires_tools` | 规则相同，但会检查单个工具。 |

**示例：** 内置的 `duckduckgo-search` 技能使用了 `fallback_for_toolsets: [web]`。当设置了 `FIRECRAWL_API_KEY` 且网络工具集可用时，智能体会使用 `web_search`，此时 DuckDuckGo 技能将保持隐藏状态。若未设置该 API 密钥，网络工具集不可用，DuckDuckGo 技能就会自动作为备用选项出现。

不包含任何条件字段的技能行为与以往完全一致——它们始终会被显示。

## 加载时的安全配置

技能可以声明所需的环境变量，而不会因此从搜索结果中消失：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

当遇到缺失值时，只有当相关技能已实际加载到本地 CLI 中时，Hermes 才会以安全的方式请求该值。您可以选择跳过设置步骤，继续使用该技能。消息交互界面绝不会在聊天中询问敏感信息——而是提示您在本地使用 `hermes setup` 命令或 `~/.hermes/.env` 文件来配置。

一旦完成设置，已声明的环境变量会**自动传递**给 `execute_code` 和 `terminal` 沙箱环境——这样技能中的脚本便可直接使用 `$TENOR_API_KEY`。对于非技能相关的环境变量，则可使用 `terminal.env_passthrough` 配置选项。详情请参阅[环境变量传递机制](/user-guide/security#environment-variable-passthrough)。

### 技能配置设置

技能还可以声明存储在 `config.yaml` 文件中的非敏感配置项（如路径、偏好设置）：

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
```

相关设置存储在 config.yaml 文件的 `skills.config` 子目录中。使用 `hermes config migrate` 命令可以查看未配置的设置，而 `hermes config show` 命令则可用于显示这些设置。当某个技能被加载时，其解析后的配置值会被注入到上下文中，从而使智能体能够自动获取到已配置的值。

如需了解更多详情，请参阅 [技能设置](/user-guide/configuration#skill-settings) 以及 [创建技能——配置设置](/developer-guide/creating-skills#config-settings-configyaml) 文档。

## 技能目录结构

```text
~/.hermes/skills/                  # Single source of truth
├── mlops/                         # Category directory
│   ├── axolotl/
│   │   ├── SKILL.md               # Main instructions (required)
│   │   ├── references/            # Additional docs
│   │   ├── templates/             # Output formats
│   │   ├── scripts/               # Helper scripts callable from the skill
│   │   └── assets/                # Supplementary files
│   └── vllm/
│       └── SKILL.md
├── devops/
│   └── deploy-k8s/                # Agent-created skill
│       ├── SKILL.md
│       └── references/
├── .hub/                          # Skills Hub state
│   ├── lock.json
│   ├── quarantine/
│   └── audit.log
└── .bundled_manifest              # Tracks seeded bundled skills
```

## 外部技能目录

如果您在Hermes之外维护技能——例如，某个被多个AI工具共享的`~/.agents/skills/`目录——您可以告知Hermes同时扫描这些目录。

只需在`~/.hermes/config.yaml`文件的`skills`部分添加`external_dirs`字段即可：

```yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills
```

路径支持使用 `~` 进行扩展，以及 `${VAR}` 进行环境变量替换。

### 工作原理

- **本地创建，原位更新**：由智能体新建的技能会存储在 `~/.hermes/skills/` 目录下。当智能体使用 `patch`、`edit`、`write_file`、`remove_file` 或 `delete` 等 `skill_manage` 操作时，现有技能会在其所在位置被修改，包括位于 `external_dirs` 下的技能。
- **外部目录并非写保护边界**：如果 Hermes 进程有权写入某个外部技能目录，那么由智能体管理的技能更新即可修改该目录中的文件。若要求共享的外部技能保持只读状态，则需通过文件系统权限设置或独立的配置文件/工具集来实现。
- **本地优先原则**：当本地目录和外部目录中存在同名技能时，以本地版本为准。
- **完全集成**：外部技能会显示在系统提示索引、`skills_list`、`skill_view` 中，也可通过 `/skill-name` 的路径命令调用——其使用方式与本地技能并无区别。
- **不存在的路径会被静默跳过**：如果配置的目录不存在，Hermes 会直接忽略它而不会报错。这对于那些并非所有机器上都存在的可选共享目录非常有用。

### 示例

```text
~/.hermes/skills/               # Local (primary, read-write)
├── devops/deploy-k8s/
│   └── SKILL.md
└── mlops/axolotl/
    └── SKILL.md

~/.agents/skills/               # External (shared, mutable if writable)
├── my-custom-workflow/
│   └── SKILL.md
└── team-conventions/
    └── SKILL.md
```

这四种技能都会显示在您的技能指数中。如果您在本地创建一个名为 `my-custom-workflow` 的新技能，它将会覆盖外部版本的该技能。

## 技能包

技能包是小型 YAML 文件，可将多个技能整合到同一个斜杠命令下。当您运行 `/<bundle-name>` 时，该包中列出的所有技能会同时加载——这对于那些总需要同一组技能共同完成的特定任务非常有用。

### 简单示例

```bash
# Create a bundle for backend feature work
hermes bundles create backend-dev \
  --skill github-code-review \
  --skill test-driven-development \
  --skill github-pr-workflow \
  -d "Backend feature work — review, test, PR workflow"
```

接着在 CLI 或任何网关平台上：

```
/backend-dev refactor the auth middleware
```

该智能体会在一条用户消息中接收已加载的这三个技能，而斜杠命令之后的所有文本则会被视为用户指令。 

### YAML架构

技能包存储在**`~/.hermes/skill-bundles/<slug>.yaml`**路径下，其格式如下：

```yaml
name: backend-dev
description: Backend feature work — review, test, PR workflow.
skills:
  - github-code-review
  - test-driven-development
  - github-pr-workflow
instruction: |
  Always start by writing failing tests, then implement.
  Open the PR through the standard workflow with co-author tags.
```

字段：
- `name`（可选——默认值为文件名基础部分）——该捆绑包的显示名称。该名称会被转换为连字符形式的短链接，以便在斜杠命令中使用（例如“Backend Dev”将变为 `/backend-dev`）。
- `description`（可选）——显示在 `/bundles` 页面以及“hermes bundles list”列表中的简短描述文字。
- `skills`（必填，且不能为空的列表）——技能名称或相对于技能目录的路径。请使用与传递给 `<skill-name>` 时相同的标识符。
- `instruction`（可选）——附加在已加载的技能内容之前的额外说明。可用于明确记载“我们通常如何将这些技能一起使用”。

### 捆绑包管理

```bash
# List all installed bundles
hermes bundles list

# Inspect one bundle
hermes bundles show backend-dev

# Create a bundle interactively (omit --skill flags to enter them one per line)
hermes bundles create research

# Overwrite an existing bundle
hermes bundles create backend-dev --skill ... --force

# Delete a bundle
hermes bundles delete backend-dev

# Re-scan ~/.hermes/skill-bundles/ and report changes
hermes bundles reload
```

在聊天会话中，使用 `/bundles` 命令即可查看所有已安装的插件包及其所含技能。

### 行为特性

- **当技能名称冲突时，插件包优先于单个技能生效**。如果你将某个插件包命名为 `research`，而系统中也存在名为 `research` 的技能，那么调用 `/research` 时会优先使用该插件包中的技能。这是有意为之——因为你通过命名选择了使用该插件包。
- **缺失的技能会被跳过，不会导致错误**。如果某个插件包列出了 `skill-foo` 这一技能，而你并未安装它，该插件包仍会加载其他可正常使用的技能，并向智能体显示一份清单，说明哪些技能被跳过了。
- **插件包可在所有场景下使用**——无论是交互式 CLI、文本用户界面、控制台聊天，还是各类通道平台（Telegram、Discord、Slack 等）——因为技能调度与单个技能命令的调度机制相同，都集中在同一位置处理。
- **插件包不会影响提示词缓存**。每次调用时，它们都会像 `/<skill-name>` 一样生成全新的用户消息，而不会修改系统提示词内容。

### 何时应使用插件包而非手动安装每个技能

以下情况适合使用插件包：
- 对于重复性任务，你总是需要搭配相同的几项技能（如 `/backend-dev`、`/release-prep`、`/incident-response`）。
- 相比于连续输入多个 `/skill` 命令，使用插件包能让你的思维模型更简洁，只需记住一个名称即可。
- 你希望为整个团队统一配置“任务模板”，只需将插件包的 YAML 文件放入共享的 dotfiles 仓库中，并通过符号链接将其置于 `~/.hermes/skill-bundles/` 目录下即可。

需要明确的是，插件包仅是一个 YAML 别名——它并不会自动为你安装技能。这些技能本身必须已经存在（位于 `~/.hermes/skills/` 目录或外部技能目录中）。否则，调用插件包时只会跳过那些缺失的技能。

## 智能体管理的技能（skill_manage 工具）

智能体可通过 `skill_manage` 工具自行创建、更新和删除技能。这相当于智能体的**程序化记忆**——当它找到一种复杂的处理流程后，会将该方法保存为技能，以便日后重复使用。

技能与记忆在自我提升循环中相互配合：记忆用于存储那些始终需要保持在上下文中的简洁且持久的事实，而技能则用于存储那些仅在相关时才需加载的复杂流程。后台审查功能可以在会话结束后建议或暂存技能更改，但下方的写入审批机制允许你在这些更改正式应用之前进行人工审核。

### 智能体何时会创建技能

- 成功完成一项复杂的任务（涉及5次及以上工具调用）后。
- 在遇到错误或陷入僵局后找到了可行的解决方案时。
- 用户指出了其处理方法的错误后。
- 发现某种复杂的处理流程后。

### 可用操作

| 操作 | 适用场景 | 关键参数 |
|------|---------|----------|
| `create` | 从零开始创建新技能 | `name`、`content`（完整的 SKILL.md 文件），可选 `category` |
| `patch` | 进行针对性修复（推荐方式） | `name`、`old_string`、`new_string` |
| `edit` | 对技能进行大规模结构重写 | `name`、`content`（替换后的完整 SKILL.md 文件） |
| `delete` | 完全删除某个技能 | `name` |
| `write_file` | 添加或更新辅助文件 | `name`、`file_path`、`file_content` |
| `remove_file` | 删除辅助文件 | `name`、`file_path` |

:::提示
对于技能更新，建议优先使用 `patch` 操作——因为它比 `edit` 更节省令牌，因为工具调用中仅会传输实际被修改的文本部分。
:::

### 审批智能体技能写入操作（`skills.write_approval`）

默认情况下，智能体可以自由创建技能——包括在每轮对话结束后进行的[后台自我提升审查](/user-guide/features/memory#controlling-memory-writes-write_approval)过程中创建。如果你希望先对每一次技能写入操作进行审批（比如那些无法准确判断自身学习成果的小型模型、安全要求较高的环境，或是希望有人监督自我提升流程的情况），可以启用写入审批机制：

```yaml
skills:
  write_approval: false     # false = write freely (default) | true = require approval
```

当设置 `write_approval: true` 时，所有的 `skill_manage` 写入操作（创建 / 编辑 /
补丁应用 / 删除 / 写入文件 / 删除文件）都会被**暂存**而非直接提交——由于 SKILL.md 文件体积过大，无法在线进行审查，因此无论该写入操作是来自前台对话还是后台审核流程，都会被暂存。这些暂存的写入内容会保存在 `~/.hermes/pending/skills/` 目录中，其审查流程与处理危险命令时所采用的熟悉的“批准/拒绝”机制相同。

```
/skills pending             # list staged skill writes + a one-line gist each
/skills diff <id>           # full unified diff (best viewed in CLI or dashboard)
/skills approve <id>        # apply it (or 'all')
/skills reject <id>         # drop it (or 'all')
/skills approval on         # turn the gate on (or 'off') and persist it
```

该审核功能既可在交互式 CLI 环境中使用，也适用于消息平台。
（由于聊天窗口的限制，差异对比输出会被截断——如需查看完整差异，请在 CLI 中或待处理的 JSON 文件中查看。）所有内存写入操作均受 `memory.write_approval` 机制的管控——详情请参阅[控制内存写入](/user-guide/features/memory#controlling-memory-writes-write_approval)。

> 单独的 `skills.guard_agent_created` 设置属于内容扫描器（基于危险模式规则），而非审批关卡——二者是相互独立的。更多信息请参见[针对智能体创建的技能写入的防护机制](/user-guide/configuration#guard-on-agent-created-skill-writes)。

## Skills Hub

您可以从此处浏览、搜索、安装并管理来自在线注册库、`skills.sh`、知名技能端点以及官方可选技能的各类智能体技能。

### 常用命令

```bash
hermes skills browse                              # Browse all hub skills (official first)
hermes skills browse --source official            # Browse only official optional skills
hermes skills search kubernetes                   # Search all sources
hermes skills search react --source skills-sh     # Search the skills.sh directory
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect openai/skills/k8s           # Preview before installing
hermes skills install openai/skills/k8s           # Install with security scan
hermes skills install official/security/1password
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install https://sharethis.chat/SKILL.md              # Direct URL (single-file SKILL.md)
hermes skills install https://example.com/SKILL.md --name my-skill # Override name when frontmatter has none
hermes skills list --source hub                   # List hub-installed skills
hermes skills check                               # Check installed hub skills for upstream updates
hermes skills update                              # Reinstall hub skills with upstream changes when needed
hermes skills audit                               # Re-scan all hub skills for security
hermes skills uninstall k8s                       # Remove a hub skill
hermes skills reset google-workspace              # Un-stick a bundled skill from "user-modified" (see below)
hermes skills reset google-workspace --restore    # Also restore the bundled version, deleting your local edits
hermes skills publish skills/my-skill --to github --repo owner/repo
hermes skills snapshot export setup.json          # Export skill config
hermes skills tap add myorg/skills-repo           # Add a custom GitHub source
```

### 支持的 hub 来源

| 来源 | 示例 | 备注 |
|------|---------|-------|
| `official` | `official/security/1password` | Hermes 自带的可选技能。 |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | 可通过命令 `hermes skills search <查询词> --source skills-sh` 进行搜索。当 skills.sh 的标识符与仓库文件夹名称不同时，Hermes 会自动解析该别名形式的技能。 |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | 直接从网站上的 `/.well-known/skills/index.json` 文件提供技能。可通过该网站或文档的 URL 进行搜索。 |
| `url` | `https://sharethis.chat/SKILL.md` | 指向单文件 `SKILL.md` 的直接 HTTP(S) URL。名称解析顺序为：前置信息 → URL 标识符 → 交互式提示 → `--name` 参数。 |
| `github` | `openai/skills/k8s` | 直接从 GitHub 仓库/路径安装技能或自定义插件。 |
| `clawhub`、`lobehub`、`browse-sh` | 各平台专用标识符 | 用于社区或市场平台的集成。 |

### 集成的 hub 与注册中心

Hermes 目前已与以下技能生态系统及发现源实现集成：

#### 1. 官方可选技能（`official`）

这类技能由 Hermes 仓库本身维护，安装时具有内置的信任度。

- 目录列表：[官方可选技能目录](../../reference/optional-skills-catalog)
- 仓库中的对应路径：`optional-skills/`
- 示例：

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

#### 2. skills.sh (`skills-sh`)

这是 Vercel 公开的技能目录。Hermes 可以直接搜索该目录，查看技能详情页面，解析别名形式的路径标识，并从对应的源代码仓库中安装相关技能。

- 目录地址：[skills.sh](https://skills.sh/)
- CLI/工具相关仓库：[vercel-labs/skills](https://github.com/vercel-labs/skills)
- Vercel 官方技能仓库：[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- 示例：

```bash
hermes skills search react --source skills-sh
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

#### 3. 知名技能端点（`well-known`）

这是一种基于 URL 的发现机制，用于查找发布有 `/.well-known/skills/index.json` 文件的站点。它并非单一的集中式平台，而是一种网络发现规范。

- 实时端点示例：[Mintlify 文档中的技能索引](https://mintlify.com/docs/.well-known/skills/index.json)
- 参考服务器实现：[vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- 示例：

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

#### 4. 直接从 GitHub 获取技能（`github`）

Hermes 支持直接从 GitHub 仓库及基于 GitHub 的资源源中安装技能。当您已知晓具体的仓库路径，或希望添加自定义的源仓库时，此功能非常实用。

无需任何设置即可使用的默认资源源：
- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [huggingface/skills](https://github.com/huggingface/skills)
- [NVIDIA/skills](https://github.com/NVIDIA/skills) — 经 NVIDIA 验证的技能（带有 `skill.oms.sig` 签名及 `skill-card.md` 管理文档）
- [garrytan/gstack](https://github.com/garrytan/gstack)

- 示例：

```bash
hermes skills install openai/skills/k8s
hermes skills tap add myorg/skills-repo
```

**分类分组（`skills.sh.json`）。** 任何 GitHub Tap 都可以在其仓库根目录中提供一个遵循[skills.sh 结构规范](https://skills.sh/schemas/skills.sh.schema.json)的 `skills.sh.json` 文件。系统会在索引构建时读取该文件中的 `groupings` 数据（每个分组包含一个 `title` 以及一系列技能名称），并将其作为显示在[Skills Hub](https://hermes-agent.nousresearch.com/docs) 页面上的分类标签，而非基于标签的推测结果。这一机制具有通用性：只要提供了该文件的 Tap 即可获得真正的分类功能，无需对 Hermes 端进行任何修改。

```json
{
  "$schema": "https://skills.sh/schemas/skills.sh.schema.json",
  "groupings": [
    { "title": "Inference AI", "skills": ["dynamo-recipe-runner", "dynamo-router-sla"] },
    { "title": "Decision Optimization", "skills": ["cuopt-developer", "cuopt-install"] }
  ]
}
```

#### 5. ClawHub (`clawhub`)

这是一个作为社区资源整合进来的第三方技能市场。

- 网站地址：[clawhub.ai](https://clawhub.ai/)
- Hermes资源标识符：`clawhub`

#### 6. Claude风格的市场化仓库 (`claude-marketplace`)

Hermes支持那些发布兼容Claude的插件/市场清单的市场化仓库。目前已整合的来源包括：
- [anthropics/skills](https://github.com/anthropics/skills)
- [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)

Hermes资源标识符：`claude-marketplace`

#### 7. LobeHub (`lobehub`)

Hermes能够搜索LobeHub公开目录中的智能体条目，并将其转换为可安装的Hermes技能。

- 网站地址：[LobeHub](https://lobehub.com/)
- 公开智能体索引：[chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- 相关仓库：[lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes资源标识符：`lobehub`

#### 8. browse.sh (`browse-sh`)

Hermes与[browse.sh](https://browse.sh)实现了集成。该平台是由Browserbase维护的目录，其中包含了200多个针对不同网站的浏览器自动化SKILL.md文件（涵盖Airbnb、Amazon、arXiv、12306.cn、Etsy、Xero等众多网站）。每个技能文件都会详细介绍如何实现对某个网站的端到端自动化操作，非常适合与Hermes的浏览器工具以及您已安装的各类浏览器自动化技能一起使用。

- 网站地址：[browse.sh](https://browse.sh/)
- 目录API接口：`https://browse.sh/api/skills`
- Hermes资源标识符：`browse-sh`
- 可信度等级：`社区级`

```bash
hermes skills search airbnb --source browse-sh
hermes skills inspect browse-sh/airbnb.com/search-listings-ddgioa
hermes skills install browse-sh/airbnb.com/search-listings-ddgioa
```

标识符的格式为 `browse-sh/<hostname>/<task-id>`，与 browse.sh 目录所展示的标识符一致。内容的解析是通过各技能的详细信息端点来完成的（`/api/skills/<slug>` → `skillMdUrl`），而非通过该目录对应的 GitHub `sourceUrl`。

#### 9. 直接 URL（`url`）

可直接从任何 HTTP(S) URL 下载单文件格式的 `SKILL.md` —— 当技能创建者在自己的网站上托管该技能时，此方式非常实用（无需在平台列表中注册，也无需输入 GitHub 路径）。Hermes 会获取该 URL，解析其中的 YAML 前置数据，并对其进行安全扫描，之后完成安装。

- Hermes 源标识：`url`
- 标识符：即该 URL 本身（无需添加前缀）
- 适用范围：仅限**单文件格式的 `SKILL.md`**。包含 `references/` 或 `scripts/` 文件的多文件格式技能需要使用清单文件，应通过上述其他来源之一进行发布。

```bash
hermes skills install https://sharethis.chat/SKILL.md
hermes skills install https://example.com/my-skill/SKILL.md --category productivity
```

名称解析的顺序如下：
1. SKILL.md YAML 前置字段中的 `name:` 字段（推荐方式——所有格式正确的技能文件均应包含该字段）。
2. URL 路径中的父目录名称（例如 `.../my-skill/SKILL.md` 对应 `my-skill`，`.../my-skill.md` 也对应 `my-skill`），前提是该名称为有效的标识符（符合正则表达式 `^[a-z][a-z0-9_-]*$

```bash
# Frontmatter has no name and the URL slug is unhelpful — supply one:
hermes skills install https://example.com/SKILL.md --name sharethis-chat

# Or inside a chat session:
/skills install https://example.com/SKILL.md --name sharethis-chat
```

信任级别始终为 `community` —— 会执行与其他来源相同的安全扫描。该 URL 会被用作安装标识符，因此当您需要刷新技能时，执行 `hermes skills update` 命令便会自动从同一 URL 获取最新信息。

### 安全扫描与 `--force` 参数

所有通过 hub 安装的技能都会经过**安全扫描器**的检测，该扫描器会排查数据泄露、命令注入、破坏性指令、供应链威胁以及其他潜在风险。

现在，`hermes skills inspect ...` 命令在可获取上游元数据的情况下也会将其显示出来：
- 代码仓库 URL
- skills.sh 详情页 URL
- 安装命令
- 每周安装次数
- 上游安全审计状态
- 知名的索引/端点 URL

如果您已审核过某个第三方技能，并希望忽略某个非危险性的策略限制，可使用 `--force` 参数。

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

重要行为说明：  
- 参数 `--force` 可用于覆盖针对“谨慎”或“警告”级别检测结果的策略限制。  
- 参数 `--force` **无法**覆盖“危险”级别的扫描判定结果。  
- 官方提供的可选技能（即 `official/...` 类型）被视为内置可信资源，因此不会显示第三方警告面板。  

### 信任等级  

| 等级 | 来源 | 策略规则 |
|------|------|----------|
| `builtin` | Hermes 内置功能 | 始终被信任 |
| `official` | 仓库中的 `optional-skills/` 目录 | 被视为内置可信资源，无第三方警告提示 |
| `trusted` | 如 `openai/skills`、`anthropics/skills`、`huggingface/skills`、`NVIDIA/skills` 等受信任的注册表或仓库 | 其策略限制比社区来源更为宽松 |
| `community` | 其余所有资源（如 `skills.sh`、知名接口、自定义 GitHub 仓库以及大多数技能市场） | 非危险级别的检测结果可通过 `--force` 参数覆盖；“危险”级别的判定结果仍会被阻止 |

### 更新生命周期  

当前，Hermes Hub 能够追踪足够的来源信息，以便重新检查已安装技能的上游版本：

```bash
hermes skills check          # Report which installed hub skills changed upstream
hermes skills update         # Reinstall only the skills with updates available
hermes skills update react   # Update one specific installed hub skill
```

该机制通过结合存储的源标识符与当前上游代码包的内容哈希值，来检测内容偏移情况。

:::提示 GitHub 请求速率限制
技能中心的功能依赖于 GitHub API，未授权用户的请求速率上限为每小时 60 次。如果在安装或搜索过程中遇到速率限制错误，可在 `.env` 文件中设置 `GITHUB_TOKEN`，将请求上限提升至每小时 5,000 次。出现此类错误时，错误信息中会提供相应的解决建议。
:::

### 发布自定义技能 Tap

如果您希望分享精心挑选的技能集——无论是供团队内部使用、组织内部共享，还是公开发布——都可以将其以 **Tap** 的形式发布：即一个 GitHub 仓库，其他 Hermes 用户可通过 `hermes skills tap add <owner/repo>` 命令将其添加。这种方式无需服务器、无需注册注册表，也无需发布流水线，只需一个包含 `SKILL.md` 文件的目录即可。

#### 仓库结构

Tap 可以是任何格式的 GitHub 仓库（公开或私有——私有仓库需要使用 `GITHUB_TOKEN`），其结构如下：

```
owner/repo
├── skills/                       # default path; configurable per-tap
│   ├── my-workflow/
│   │   ├── SKILL.md              # required
│   │   ├── references/           # optional supporting files
│   │   ├── templates/
│   │   └── scripts/
│   ├── another-skill/
│   │   └── SKILL.md
│   └── third-skill/
│       └── SKILL.md
└── README.md                     # optional but helpful
```

规则：
- 每个技能都会存储在 tap 根路径下的独立目录中（默认为 `skills/`）。
- 该目录名称即为该技能的安装标识符。
- 每个技能目录都必须包含一个符合标准 [SKILL.md 前置信息格式](#skillmd-format) 的 `SKILL.md` 文件（需包含 `name`、`description` 字段，还可可选地包含 `metadata.hermes.tags`、`version`、`author`、`platforms`、`metadata.hermes.config` 字段）。
- 在安装时，`references/`、`templates/`、`scripts/`、`assets/` 等子目录会与 `SKILL.md` 一同被下载。
- 目录名称以 `.` 或 `_` 开头的技能将被忽略。

Hermes 会通过列出 tap 路径下的所有子目录，并检查每个目录中是否存在 `SKILL.md` 文件，从而发现各类技能。

#### 最简 tap 示例

```
my-org/hermes-skills
└── skills/
    └── deploy-runbook/
        └── SKILL.md
```

`skills/deploy-runbook/SKILL.md`：

```markdown
---
name: deploy-runbook
description: Our deployment runbook — services, rollback, Slack channels
version: 1.0.0
author: My Org Platform Team
metadata:
  hermes:
    tags: [deployment, runbook, internal]
---

# Deploy Runbook

Step 1: ...
```

将其推送到 GitHub 后，任何 Hermes 用户均可订阅并安装该工具：

```bash
hermes skills tap add my-org/hermes-skills
hermes skills search deploy
hermes skills install my-org/hermes-skills/deploy-runbook
```

#### 非默认路径

如果您的技能文件并非位于 `skills/` 目录下（通常是在向现有项目添加 `skills/` 子目录时会出现这种情况），请编辑 `~/.hermes/.hub/taps.json` 文件中的对应配置项：

```json
{
  "taps": [
    {"repo": "my-org/platform-docs", "path": "internal/skills/"}
  ]
}
```

`hermes skills tap add` CLI命令会默认将新插件路径设置为`path: "skills/"`；如果需要其他路径，则可直接编辑该文件。`hermes skills tap list`命令可显示每个插件的实际路径。

#### 直接安装单个技能（无需添加插件）

用户也可以直接从任何公开的GitHub仓库中安装单个技能，而无需将该整个仓库作为插件添加进来：

```bash
hermes skills install owner/repo/skills/my-workflow
```

当您希望共享某项技能，而又无需让用户订阅您的整个技能库时，此功能非常实用。

#### Tap的信任等级

新的Tap默认被赋予“社区”级信任度。从这些Tap安装的技能会经过标准的安全扫描，且在首次安装时会显示第三方警告面板。如果您的组织或某个备受信赖的来源需要更高的信任度，可将对应的仓库添加到`tools/skills_hub.py`文件中的`TRUSTED_REPOS`列表中（这需要提交Hermes核心版本的PR）。

#### Tap管理

```bash
hermes skills tap list                                # show all configured taps
hermes skills tap add myorg/skills-repo               # add (default path: skills/)
hermes skills tap remove myorg/skills-repo            # remove
```

在正在运行的会话中：

```
/skills tap list
/skills tap add myorg/skills-repo
/skills tap remove myorg/skills-repo
```

Tap配置存储在`~/.hermes/.hub/taps.json`文件中（该文件会根据需求自动创建）。

## 打包技能更新（`hermes skills reset`）

Hermes在代码仓库的`skills/`目录中预置了一组打包好的技能。在安装时以及每次执行`hermes update`操作时，系统都会同步这些技能到`~/.hermes/skills/`目录，并在`~/.hermes/skills/.bundled_manifest`文件中记录映射关系，将每个技能名称与其同步时的内容哈希值（即**原始哈希值**）关联起来。

每次同步时，Hermes都会重新计算本地版本的内容哈希值，并将其与原始哈希值进行比对：

- **未发生变化** → 可以安全地获取上游的更新内容，再将新的打包版本复制进来，同时记录新的原始哈希值。
- **已发生变化** → 会被视为**用户修改过**的内容，此后将永久跳过该技能的同步，从而避免你的修改被覆盖。

这种保护机制虽然有效，但也存在一个弊端。如果你修改了某个打包技能，之后又想放弃这些修改，直接从`~/.hermes/hermes-agent/skills/`目录复制回原始版本，由于manifest文件中仍保留着上一次成功同步时的*旧*原始哈希值，而你新复制的内容对应的哈希值与该旧值不一致，因此同步系统会持续将其标记为用户修改过的内容。

此时就可以使用`hermes skills reset`命令来解决这个问题：

```bash
# Safe: clears the manifest entry for this skill. Your current copy is preserved,
# but the next sync re-baselines against it so future updates work normally.
hermes skills reset google-workspace

# Full restore: also deletes your local copy and re-copies the current bundled
# version. Use this when you want the pristine upstream skill back.
hermes skills reset google-workspace --restore

# Non-interactive (e.g. in scripts or TUI mode) — skip the --restore confirmation.
hermes skills reset google-workspace --restore --yes
```

该命令在聊天界面中与斜杠命令具有相同的功能：

```text
/skills reset google-workspace
/skills reset google-workspace --restore
```

:::注意：配置文件
每个配置文件都在其独立的 `HERMES_HOME` 目录下拥有自己的 `.bundled_manifest` 文件，因此 `hermes -p coder skills reset <name>` 命令仅会对该配置文件生效。
:::

### 斜杠命令（在聊天中使用）

所有命令在 `/skills` 接口下均可正常使用：

```text
/skills browse
/skills search react --source skills-sh
/skills search https://mintlify.com/docs --source well-known
/skills inspect skills-sh/vercel-labs/json-render/json-render-react
/skills install openai/skills/skill-creator --force
/skills check
/skills update
/skills reset google-workspace
/skills list
```

官方提供的可选技能仍会使用诸如 `official/security/1password` 以及 `official/migration/openclaw-migration` 这样的标识符。
