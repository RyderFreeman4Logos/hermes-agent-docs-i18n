---
sidebar_position: 2
title: "Skills System"
description: "On-demand knowledge documents — progressive disclosure, agent-managed skills, and the Skills Hub"
---

# 技能系统

技能是代理在需要时可以加载的按需知识文档。它们采用**渐进式展示**模式，以降低令牌使用量，并且兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。

所有技能都存储在 **`~/.hermes/skills/`** 目录中——这是主要的技能存放位置及权威数据源。在首次安装时，预装的技能会从代码仓库中被复制到此处；通过 Hub 安装的技能以及代理自行创建的技能也会存放在这里。代理可以修改或删除任何技能。

您还可以为 Hermes 指定**外部技能目录**——即除本地目录之外还会扫描的其他文件夹。详情请参见下文的[外部技能目录](#external-skill-directories)。

另请参阅：

- [预装技能目录](/reference/skills-catalog)
- [官方可选技能目录](/reference/optional-skills-catalog)

## 从空白状态开始

默认情况下，每个配置文件都会包含预装的技能目录，而每次执行 `hermes update` 操作都会添加新预装的技能。如果您希望创建一个**不包含任何预装技能**的配置文件，并且确保其在后续更新中仍保持为空，有以下两种方法：

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

以上三种方式都会在配置目录中写入一个`.no-bundled-skills`标记。只要该标记存在，安装程序、`hermes update`命令以及任何技能同步操作都会跳过对该配置文件的预装技能注入流程。如需重新启用此功能，可删除该标记（或运行`hermes skills opt-in`命令）。

:::注意：默认安全设置
`hermes skills opt-out`仅会阻止*后续*的技能注入——它绝不会删除磁盘上已存在的任何内容。可选的`--remove`参数仅在预装技能未被修改（与Hermes安装版本完全一致）时才会将其删除。您自行编辑过的技能、从Hub安装的技能以及您自行编写的技能将始终被保留。
:::

## 使用技能

所有已安装的技能都会自动作为斜杠命令可用：

```bash
# In the CLI or any messaging platform:
/gif-search funny cats
/axolotl help me fine-tune Llama 3 on my dataset
/github-pr-workflow create a PR for the auth refactor
/songsee analyze the frequency spread of this mix

# Just the skill name loads it and lets the agent ask what you need:
/excalidraw
```

### 在单个命令中叠加多个技能

您可以通过在消息开头串联斜杠命令，从而在一条消息中调用多个技能——前缀中的每个 `/skill` 标识符（最多5个）都会被加载，其余部分则构成您的指令内容。

```bash
/github-pr-workflow /test-driven-development fix issue #123 and open a PR
```

解析会在遇到第一个非已安装技能的标记时停止，因此那些以 `/` 开头的参数（如文件路径）绝不会被忽略。

```bash
/ocr-and-documents /tmp/scan.pdf extract the tables   # loads one skill; /tmp/scan.pdf is the argument
```

对于那些需要频繁使用的组合操作，建议使用[技能包](#skill-bundles)——只需一个简短的命令即可实现相同功能。

（规划模式的工作原理类似，但现在已内置为专用命令：`/plan [request]` 会指示 Hermes 在必要时检查上下文，生成 Markdown 格式的执行计划而非直接执行任务，并将结果保存在当前工作区或后端工作目录下的 `.hermes/plans/` 文件夹中。）

您也可以通过自然对话的方式与各种技能进行交互：

```bash
hermes chat --toolsets skills -q "What skills do you have?"
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

## 从各种资源中学习技能（`/learn`）

`/learn` 是一种高效的方式，无需手动编写 `SKILL.md` 文件，即可将您已掌握的知识或大量参考资料转化为可重复使用的技能。该功能具有高度灵活性：只要能描述清楚内容，它就能利用现有工具收集相关资料，进而按照[官方技能编写标准](#skillmd-format)生成技能文件（描述部分长度不超过60个字符，结构遵循标准顺序，使用Hermes工具框架，且不包含自定义命令）。

```bash
# A local SDK or doc directory — read with read_file / search_files
/learn the REST client in ~/projects/acme-sdk, focus on auth + pagination

# An online doc page — fetched with web_extract
/learn https://docs.example.com/api/quickstart

# The workflow you just walked the agent through in this conversation
/learn how I just deployed the staging server

# Pasted notes / a described procedure
/learn filing an expense: open the portal, New > Expense, attach the receipt, submit

# A whole book, paper stack, or large docs corpus — becomes a knowledge-base skill
/learn ~/books/designing-data-intensive-applications.pdf
```

### 大量来源资料可转化为知识库技能  

当输入资料为书籍、整叠论文、技术规范或庞大的文档文件夹时，智能体不会将其压缩进单个文件或简化为有损摘要。相反，它会构建一个**内容丰富的知识库技能**：一个精简的 `SKILL.md` 文件，其中包含该资料的核心思维模型与索引；同时，在 `references/` 目录下为每个章节或主题生成一个独立文件（若资料中包含相关术语，还会附带词汇表或速查表）。这些参考文件在未被查询时不会占用任何资源——智能体会通过 `skill_view` 函数按需加载它们，因此查询成本与答案的长度成正比，而非与原始资料规模挂钩。若针对同一主题添加新资料并再次执行 `/learn` 命令，系统会将新内容整合到现有技能中，而不会生成重复的技能。  

此处理过程会提炼出资料中的结构化内容——如框架、定义、决策规则、反模式等——但绝不会复制原文中的段落。由于智能体会自动处理资料获取工作，因此无论是在 CLI、消息网关、TUI、控制面板，还是任何终端后端（本地、Docker 或远程环境）中，执行 `/learn` 命令的方式都保持一致，因为系统中并不存在独立的资料导入引擎。在**控制面板**的“技能”页面上，有一个“学习技能”按钮，点击后会弹出一个面板，其中包含目录输入框、URL 输入框以及一个开放式文本框；系统会据此构建 `/learn` 请求，并在聊天界面中执行该请求。

不存在模型工具的额外开销：`/learn`功能会生成符合标准规范的提示语，并将其作为普通对话轮次传递给智能体。智能体会通过`skill_manage`工具保存处理结果，因此如果启用了[内容审核机制](#gating-agent-skill-writes-skillswrite_approval)，该机制也会随之生效。

## 逐步展示功能

各类技能均采用高效的令牌加载模式：

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

### 针对特定平台的技能

通过 `platforms` 字段，技能可以被限定在特定的操作系统上使用：

| 值 | 匹配的系统 |
|-------|----------|
| `macos` | macOS（Darwin） |
| `linux` | Linux |
| `windows` | Windows |

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders, FindMy)
platforms: [macos, linux]     # macOS and Linux
```

一旦设置该选项，该技能将自动在系统提示、`skills_list()` 函数以及不兼容平台上的斜杠命令中隐藏。若未设置，则该技能会在所有平台上显示。

## 技能输出与媒体文件传输

当技能响应（或任何智能体响应）包含媒体的绝对路径时——例如 `/home/user/screenshots/diagram.png`——网关会自动识别该路径，将其从可见文本中移除，并直接将文件以原生形式发送到用户的聊天界面中（如 Telegram 的图片、Discord 的附件等），而不会在消息中留下原始路径。

对于音频文件，`[[audio_as_voice]]` 指令可在支持该功能的平台（如 Telegram、WhatsApp）上将音频文件以原生语音消息气泡的形式呈现。

### 强制以文档形式传输：`[[as_document]]`

有时您可能需要与内联预览相反的效果：希望将文件作为可下载的附件发送，而非重新压缩后的图片气泡。典型的应用场景是高分辨率截图或图表——Telegram 的 `sendPhoto` 功能会将其重新压缩至约 200 KB 且分辨率为 1280 像素，从而影响可读性。而通过 `sendDocument` 发送的 1-2 MB PNG 文件则能完整保留原始数据。

如果响应内容（或其中的任何文本，通常是最后一行）包含指令 `[[as_document]]`，则从该响应中提取的所有媒体路径都将作为文档/文件附件发送，而非图片气泡形式。

```
Here is your rendered chart:

/home/user/.hermes/cache/chart-q4-2025.png

[[as_document]]
```

该指令会在内容传输前被移除，因此用户永远无法看到它。其设计原则是每次响应均为全有或全无：仅输出一次`[[as_document]]`，同一响应中的每个图片路径都会作为独立文档被发送。这一机制与`[[audio_as_voice]]`的作用范围类似。

在以下情况下，可在技能中使用该功能：
- 当你需要以文件形式生成用户所需的截图或图表（以便在其他工具中编辑、归档或完整分享）；
- 默认的有损预览会掩盖细节（如小字体文字、高精度像素图或对颜色敏感的渲染结果）。

对于没有独立文档路径的平台（例如短信），则会回退到其现有的附件传输机制。

### 条件激活（备用技能）

技能可以根据当前会话中可用的工具自动显示或隐藏。这对于**备用技能**尤为有用——这类免费或本地的替代方案仅应在高级工具不可用时出现。

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

**示例：** 内置的 `duckduckgo-search` 技能使用了 `fallback_for_toolsets: [web]` 这一设置。当设置了 `FIRECRAWL_API_KEY` 且网络工具集可用时，智能体会使用 `web_search` 功能，此时 DuckDuckGo 技能将保持隐藏状态。若该 API 密钥缺失，网络工具集不可用，DuckDuckGo 技能则会自动作为备用选项出现。

那些不包含任何条件字段的技能仍会像以往一样始终显示。  

## 加载时的安全配置

技能可以声明所需的环境变量，而不会因此从搜索结果中消失：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

当遇到缺失值时，只有当相关技能已实际加载到本地 CLI 中时，Hermes 才会以安全的方式请求该值。您可以跳过设置步骤，继续使用该技能。消息交互界面绝不会在聊天中询问敏感信息——而是提示您在本地使用 `hermes setup` 或 `~/.hermes/.env` 文件来配置。

一旦完成设置，已声明的环境变量将会**自动传递**给 `execute_code` 和 `terminal` 沙箱——技能中的脚本可以直接使用 `$TENOR_API_KEY`。对于非技能相关的环境变量，则可使用 `terminal.env_passthrough` 配置选项。详情请参阅[环境变量传递机制](/user-guide/security#environment-variable-passthrough)。

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

相关设置存储在 config.yaml 文件的 `skills.config` 部分。使用 `hermes config migrate` 命令可以查看未配置的设置，而 `hermes config show` 命令则可用于显示这些设置。当某个技能被加载时，其解析后的配置值会被注入到上下文中，从而使智能体能够自动获取到已配置的值。

如需了解更多详情，请参阅 [技能设置](/user-guide/configuration#skill-settings) 以及 [创建技能——配置设置](/developer-guide/creating-skills#config-settings-configyaml)。

## 技能目录结构

```text
~/.hermes/skills/                  # Single source of truth
├── mlops/                         # Category directory
│   ├── axolotl/
│   │   ├── SKILL.md               # Main instructions (required)
│   │   ├── references/            # Additional docs
│   │   ├── templates/             # Output formats
│   │   ├── scripts/               # Helper scripts callable from the skill
│   │   ├── examples/              # Referenced example outputs
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

通过第三方 URL 或 GitHub 安装的插件会包含 `SKILL.md` 文件，以及其在 `references/`、`templates/`、`scripts/`、`assets/` 和 `examples/` 目录下所引用的所有本地文件。未被引用的仓库文件则不会被复制。Hermes 会扫描整个隔离后的插件包，并将来源 URL、内容哈希值、扫描器版本、检测结果、时间戳以及内容为最新状态还是缓存状态等信息记录在 `skills/.hub/lock.json` 文件中。

### 建议性的 SkillEvaluator 扫描

除了内置的安全扫描器（用于执行上述安装策略外），Hermes 还可以运行 [NVIDIA SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator) 对每个已安装的插件进行一级检测，作为额外的审核手段。一级检测属于确定性扫描且无需密钥——它能够检测个人信息泄露（如泄露的电子邮件、个人路径、连接字符串）、Unicode 信息窃取行为、脚本错误、许可证合规性问题，还会通过 [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) 执行静态安全扫描。

需要注意的是，该扫描仅具有建议性质：在安装确认之前，系统会先显示包含文件名和行号的检测结果，随后安装仍会继续进行。那些看似真实凭证的内容（如私钥、云访问密钥、令牌、带凭据的连接字符串）会被标为红色，以便你在做出决定前仔细查看相关行。而属于个人信息类的检测结果仅用于提供参考——因为上游扫描器存在一些已知的误报情况（例如 `git@github.com` 这样的 SSH 语法、文档中的示例电子邮件），这类检测结果绝不会阻止任何安装操作。

若要启用该功能，请安装可选的扫描器二进制文件（第二个文件用于执行`security`检查；若没有它，该检查将仅显示“未运行”状态）：

```bash
uv tool install --python 3.13 \
  "skillevaluator @ git+https://github.com/NVIDIA/SkillEvaluator.git@v0.1.0"
uv tool install "git+https://github.com/NVIDIA/SkillSpector.git@v2.9.5"
```

如果路径中不存在该二进制文件，扫描将会被静默跳过。如需完全关闭此功能：

```yaml
skills:
  tier1_advisory: false
```

控制面板中的“Browse-hub扫描”按钮在返回结果时，会除了内置扫描器的判定之外，还提供相同的预警数据（即`tier1`字段）。

## 外部技能目录

如果您在Hermes之外维护了技能文件——例如多个AI工具共用的`~/.agents/skills/`目录——您可以指示Hermes对这些目录也进行扫描。

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

- **本地创建，原地更新**：由智能体新建的技能会被保存到 `~/.hermes/skills/` 目录中（若配置了其他路径，则保存至该路径——详见下文）。当智能体使用 `patch`、`edit`、`write_file`、`remove_file` 或 `delete` 等 `skill_manage` 操作时，现有技能会在其所在位置被修改，包括位于 `external_dirs` 下的技能。
- **外部目录并非写保护边界**：只要 Hermes 进程有权写入某个外部技能目录，智能体管理的技能更新即可修改该目录中的文件。若要求共享的外部技能始终保持只读状态，则需通过文件系统权限设置或独立的配置文件/工具集来实现。
- **本地优先原则**：如果本地目录和外部目录中存在同名的技能，将以本地版本为准。
- **完全集成**：外部技能会显示在系统提示词索引、`skills_list`、`skill_view` 中，也可通过 `/skill-name` 的路径形式调用——其使用方式与本地技能并无区别。
- **不存在的路径会被静默跳过**：若配置的目录不存在，Hermes 会直接忽略它而不会报错。这对于那些并非所有机器上都存在的可选共享目录非常有用。

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

这四种技能都会显示在你的技能指数中。如果你在本地创建一个名为 `my-custom-workflow` 的新技能，它将会覆盖原有的外部版本。

## 指定技能创建路径（`skills.create_dir`）

默认情况下，智能体会将新技能保存到用户本地的 `~/.hermes/skills/` 目录中。如果你希望智能体创建的技能存储在其他位置——比如共享的“大脑”目录、受 Git 监控的仓库，或是整个集群通用的技能存储空间——可以在 `skills` 配置项下设置 `create_dir` 参数：

```yaml
skills:
  create_dir: /opt/brain/skills
```

变更内容：

- **`skill_manage` 的创建操作将写入该目录。** 新技能（包括其所属的子目录）将在 `create_dir` 指定的路径下创建，而非本地技能目录。如果该目录尚不存在，会在首次写入时自动创建。
- **智能体的操作指令将遵循配置设置。** 所有指定技能创建路径的智能体指令——即 `skill_manage` 工具的描述及相关提示文本——都会动态使用配置中的目录路径，从而指示智能体在该位置创建技能。无需通过系统级提示进行覆盖或借助文件系统技巧。
- **该目录已实现完全集成。** 位于 `create_dir` 下的技能会与本地目录中的技能一同被扫描：它们会出现在技能索引、`skills_list`、`skill_view` 以及斜杠命令中，且可以像普通本地技能一样被修改或删除。
- **其他所有内容仍保持本地处理。** 现有的技能仍会在其原有的位置被修改；技能同步功能、Hub 以及 Curator 继续在用户个人目录下运行。

路径支持 `~` 扩展和 `${VAR}` 替换；相对路径会基于用户的 Hermes 主目录来解析。将 `create_dir` 设置为本地技能目录，与不设置该参数的效果相同。

## 项目级本地技能

仓库可以拥有自己的技能，这些技能仅对在该项目中启动的会话有效——这与其它智能体框架用于仓库级配置的机制类似。当在 git 检出目录中启动 Hermes 时，它会在以下位置查找技能：

```text
<project-root>/.hermes/skills/    # Hermes-native location
<project-root>/.agents/skills/    # cross-tool convention (shared with other agent CLIs)
```

项目根目录是指包含 `.git` 文件的最上层父目录（工作树和子模块也会被计入）。

### 信任项目

技能是智能体需要遵循的流程文档，因此 Hermes **不会**自动从任意克隆的代码库中加载这些技能。首次在包含项目技能的代码库中运行 Hermes 时，界面顶部会显示一条提示信息：

```text
◆ 3 project skill(s) found in /home/you/myproject but not loaded — run `hermes skills trust` to enable them.
```

只需信任该仓库一次（既可在其内部操作，也可通过传递路径来实现）：

```bash
hermes skills trust             # trust the current repo
hermes skills trust ~/myproject # or explicitly
hermes skills untrust           # revoke
```

受信任的目录存储在 `~/.hermes/config.yaml` 文件中的 `skills.trusted_project_dirs` 键下。如需完全关闭此功能（既不进行扫描也不显示提示），可设置 `skills.project_discovery: false`。

### 优先级

项目技能属于**优先级最高的类别**：`项目技能 → 本地技能（~/.hermes/skills/）→ 外部目录》。名为 `deploy` 的项目技能会覆盖该仓库内同名的配置文件或捆绑技能——这正是其设计目的：即仓库自带的技能在其所在环境中具有优先权，而不会影响你的全局配置。项目技能在智能体的技能索引中会被标记为 `[project]`，以便清晰显示其来源。

与外部目录类似，项目技能目录也被视为仓库所有：自主维护技能的机制不会对其进行修改，而新创建的智能体技能则会自动存放在 `~/.hermes/skills/` 目录下。

### 扫描时的隔离处理

信任关系是针对整个仓库层面的决策，但仓库中的技能内容会随着每次 `git pull` 操作而发生变化。为弥补这一缺陷，在项目技能被纳入索引之前，会使用与 Skills Hub 安装时相同的安全扫描工具对其进行检查。如果扫描结果判定为**危险**（如包含注入指令、窃取凭证的命令或隐藏文本技巧），该技能将被隔离：它不会出现在技能索引、`skills_list` 列表以及斜杠命令中，且会以错误提示拒绝按名称加载。扫描结果会以内容哈希值的形式缓存于 `~/.hermes/cache/project_skill_scans/` 目录下（绝不会存储在仓库内部），一旦技能内容发生变化，系统会自动重新进行扫描。

### 非交互式接口（cron、API、ACP）

Cron作业及其他非交互式接口会继承您设定的交互式信任策略——它们既不会主动提示用户，也不会自动建立信任关系。项目根目录由该接口的当前工作目录决定（对于Cron作业而言，即为`workdir`，其确定机制与终端工具相同）。如果Cron作业的`workdir`位于您之前已信任的仓库中，它将加载该仓库中的项目技能；而若位于未被信任或状态未定的仓库中，则不会加载任何技能。

## 技能包

技能包是小型YAML文件，可将多个技能整合在同一个斜杠命令下。当您运行`/<bundle-name>`时，该包中列出的所有技能会同时被加载——这对于那些始终需要同一组技能共同完成的特定任务来说非常有用。

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

该智能体会在一条用户消息中接收所有已加载的三种技能，而斜杠命令之后的任何文本则会被视为用户指令。 

### YAML 结构规范

技能包存储在 **`~/.hermes/skill-bundles/<slug>.yaml`** 文件中，其格式如下：

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
- `description`（可选）——显示在 `/bundles` 页面以及 “hermes bundles list” 列表中的简短说明文字。
- `skills`（必填，非空列表）——技能名称或相对于技能目录的路径。需使用与传递给 `<skill-name>` 时相同的标识符。
- `instruction`（可选）——附加到已加载技能内容之前的额外指导说明。可用于明确“我们通常如何将这些技能一起使用”。

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

在聊天会话中，输入 `/bundles` 即可查看所有已安装的插件包及其包含的技能。

### 行为特性

- **当技能名称冲突时，插件包优先于单个技能生效**。如果您将某个插件包命名为 `research`，而系统中又存在名为 `research` 的技能，那么输入 `/research` 时会调用该插件包。这是有意为之——您正是通过为插件包命名来选择使用它的。
- **缺失的技能会被跳过，而不会导致程序崩溃**。如果某个插件包列出了 `skill-foo` 这一技能，但您并未安装它，该插件包仍会加载其他可正常识别的技能，同时系统会给出提示说明哪些技能被跳过。
- **插件包可在所有场景下使用**——无论是交互式命令行界面、文本用户界面、控制台聊天，还是各类消息平台（Telegram、Discord、Slack 等）——因为任务调度与单个技能命令的调度机制都在同一位置集中处理。
- **插件包不会影响提示词缓存**。与使用 `/<skill-name>` 一样，插件包在调用时也会生成全新的用户消息，不会对系统提示词进行任何修改。

### 何时应使用插件包而非手动安装每个技能

以下情况适合使用插件包：
- 您总是为重复性任务搭配相同的技能（如 `/backend-dev`、`/release-prep`、`/incident-response`）。
- 相比于连续输入多个 `/skill` 命令，您希望用更简洁的方式记住这些技能。
- 您希望为整个团队统一配置“任务模板”，只需将插件包的 YAML 文件放入共享的 dotfiles 仓库中，并通过符号链接将其放到 `~/.hermes/skill-bundles/` 目录下即可。
Bundle仅是一个YAML别名——它并不会自动为你安装技能。这些技能本身必须已经存在（位于`~/.hermes/skills/`目录或外部技能目录中）。否则，调用bundle时会跳过那些缺失的技能。

## 由智能体管理的技能（skill_manage工具）

智能体可通过`skill_manage`工具创建、更新和删除自身的技能。这便是智能体的**程序化记忆**——当它找到一种复杂的处理流程时，会将该方法保存为技能以便日后重复使用。

技能与记忆在自我提升循环中协同工作：记忆用于存储那些始终需要保持在上下文中的简短且持久的事实，而技能则用于存储较长的流程，这些流程仅在相关时才会被加载。后台审核功能可以在会话结束后建议或准备技能的修改，但下方的写入审批机制可让你在这些更改正式应用前进行人工审核。

### 智能体何时创建技能

系统提示会让智能体使用`skill_manage`记录那些复杂的处理流程，以便日后重复使用。实际上，这包括以下情况：

- 当它找到值得重复使用的多步骤处理流程时
- 当它遇到错误或僵局并找到可行的解决路径时
- 当用户对其处理方式提出修正时

### 一个技能条目的结构是怎样的

技能是指按照您的要求，以最高效且最准确的方式执行某类任务的指导说明：包括具体的操作步骤、有效的命令与工具调用方式、期望得到的结果形式，以及可能造成时间浪费的陷阱。无论这些内容是由用户在前台对话中输入、后台审核过程生成，还是由内容整理者整合而成，它们所记录的都是**经验教训而非日志记录**：所谓陷阱，其实是一条可推广的规则，再加上一个说明其*成因*（即具体机制）的条款，且仅针对受影响的步骤进行一次性说明。事件描述、PR或问题编号、日期以及引用的聊天内容均不属于技能内容；这条规则即便脱离了相关背景故事依然有效。常驻规则保存在`SKILL.md`文件中；而`references/`目录则存放按主题分类的一组小型文件（如决策表、操作指南、各提供方的特殊要求等），这些文件会直接在该目录内进行扩展，而不会每次会话都新增一个文件。此外，技能也不需要在每次对话中重复已加载的内容（如仓库中的`AGENTS.md`文件及工具架构信息）。

`skill_manage`工具会对`create`命令以及`references/`目录中的内容运行提示性检查器，并将检测结果返回至工具的输出中。针对此类内容，特别设有两条规则：`incident-log-shape`（指内容中充斥着大量PR/问题编号的情况），以及`references-sprawl`（指参考文件数量超过60个的情况）。这些规则仅起到警示作用，绝不会阻止内容的写入。

### 操作

| 操作 | 用途 | 关键参数 |
|------|------|----------|
| `create` | 从零创建新技能 | `name`、`content`（完整的SKILL.md文件），可选`category` |
| `patch` | 进行针对性修复（推荐方式） | `name`、`old_string`、`new_string` |
| `edit` | 进行大规模结构重写 | `name`、`content`（替换为完整的SKILL.md文件） |
| `delete` | 完全删除某个技能 | `name` |
| `write_file` | 添加/更新辅助文件 | `name`、`file_path`、`file_content` |
| `remove_file` | 删除辅助文件 | `name`、`file_path` |

:::提示
对于技能更新，推荐使用`patch`操作——因为它比`edit`更节省令牌，因为工具调用中仅会包含更改过的文本。
:::

### 对技能写入进行审批控制（`skills.write_approval`）

默认情况下，智能体可以自由写入技能内容——包括在每轮对话结束后进行的[背景自我改进审核](/user-guide/features/memory#controlling-memory-writes-write_approval)所允许的内容。如果您希望先对每次技能写入进行审批（适用于那些无法准确判断所学内容的较小模型、安全要求较高的环境，或希望对自我改进流程进行监督的情况），可启用写入审批机制：

```yaml
skills:
  write_approval: false     # false = write freely (default) | true = require approval
```

当 `write_approval: true` 时，所有的 `skill_manage` 写入操作（创建 / 编辑 /
补丁应用 / 删除 / 写入文件 / 删除文件）都会被**暂存**而非直接提交——由于 SKILL.md 文件体积过大，无法在即时界面中进行审查，因此无论该写入操作是来自前台对话还是后台审核流程，都会被暂存。这些暂存的写入内容会保存在 `~/.hermes/pending/skills/` 目录中，其审查流程与处理危险命令时所采用的“批准/拒绝”机制完全一致。

```
/skills pending             # list staged skill writes + a one-line gist each
/skills diff <id>           # full unified diff (best viewed in CLI or dashboard)
/skills approve <id>        # apply it (or 'all')
/skills reject <id>         # drop it (or 'all')
/skills approval on         # turn the gate on (or 'off') and persist it
```

该审查功能既可在交互式 CLI 环境中使用，也可应用于消息平台。
（由于聊天窗口的限制，差异对比输出会被截断——如需查看完整差异，请在 CLI 中或待处理的 JSON 文件中查看。）内存写入操作同样受 `memory.write_approval` 机制的管控——详情请参阅[控制内存写入](/user-guide/features/memory#controlling-memory-writes-write_approval)。

> 单独的 `skills.guard_agent_created` 设置属于内容扫描器（基于危险模式启发式规则），而非审批关卡——二者是相互独立的。更多信息请参见[对智能体创建的技能写入进行防护](/user-guide/configuration#guard-on-agent-created-skill-writes)。

## Skills Hub

您可以浏览、搜索、安装以及管理来自在线注册库、`skills.sh`、知名技能端点以及官方可选技能的各类技能。

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
hermes skills install https://sharethis.chat/SKILL.md              # Direct URL (+ referenced support files)
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

### 支持的 Hub 来源

| 来源 | 示例 | 备注 |
|------|---------|-------|
| `official` | `official/security/1password` | Hermes 自带的可选技能。 |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | 可通过命令 `hermes skills search <查询词> --source skills-sh` 进行搜索。当 skills.sh 的标识符与仓库文件夹名称不同时，Hermes 会自动解析该别名形式的技能。 |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | 直接从网站上的 `/.well-known/skills/index.json` 文件提供技能。可通过网站地址或文档地址进行搜索。 |
| `url` | `https://sharethis.chat/SKILL.md` | 指向 `SKILL.md` 文件的直接 HTTP(S) 地址，以及明确指定的支持文件。名称解析顺序为：前置信息 → URL 标识符 → 交互式提示 → `--name` 参数。 |
| `github` | `openai/skills/k8s` | 直接从 GitHub 仓库/路径安装技能或自定义集成项。 |
| `clawhub`、`lobehub`、`browse-sh` | 各来源特定的标识符 | 用于社区或市场平台的集成。 |

### 集成的 Hub 与注册中心

Hermes 目前已与以下技能生态系统及发现源实现集成：

#### 1. 官方可选技能（`official`）

这类技能由 Hermes 仓库本身维护，安装时具有内置的信任度。

- 目录：[官方可选技能目录](../../reference/optional-skills-catalog)
- 仓库中的对应路径：`optional-skills/`
- 示例：

```bash
hermes skills browse --source official
hermes skills install official/security/1password
```

#### 2. skills.sh (`skills-sh`)

这是 Vercel 公开的技能目录。Hermes 可以直接搜索该目录，查看技能详情页面，解析别名形式的路径标识，并从底层的源代码仓库中安装相关技能。

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

这是一种基于 URL 的发现机制，用于查找发布 `/.well-known/skills/index.json` 文件的站点。它并非单一的集中式枢纽，而是一种网络发现规范。

- 实时端点示例：[Mintlify 文档中的技能索引](https://mintlify.com/docs/.well-known/skills/index.json)
- 参考服务器实现：[vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- 示例：

```bash
hermes skills search https://mintlify.com/docs --source well-known
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

#### 4. 直接从 GitHub 获取技能包（`github`）

Hermes 支持直接从 GitHub 仓库及基于 GitHub 的技能源获取技能包。当您已知晓具体的仓库路径，或希望添加自定义的来源仓库时，此功能非常实用。

无需任何设置即可浏览的默认技能源包括：
- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [huggingface/skills](https://github.com/huggingface/skills)
- [NVIDIA/skills](https://github.com/NVIDIA/skills) — 经 NVIDIA 验证的技能包（包含签名文件 `skill.oms.sig` 及管理文档 `skill-card.md`）
- [garrytan/gstack](https://github.com/garrytan/gstack)

- 示例：

```bash
hermes skills install openai/skills/k8s
hermes skills tap add myorg/skills-repo
```

**分类分组（`skills.sh.json`）**。某个 GitHub Tap 可以在其仓库根目录中提供一个遵循[skills.sh 架构规范](https://skills.sh/schemas/skills.sh.schema.json)的 `skills.sh.json` 文件。系统会在索引构建时读取该文件中的 `groupings` 配置（每个分组包含一个 `title` 以及一系列技能名称），并将其作为显示在[Skills Hub](https://hermes-agent.nousresearch.com/docs) 页面上的分类标签，而非基于标签的推测结果。这一机制具有通用性：只要提供了该文件的任何 Tap 都能获得准确的分类，无需对 Hermes 端进行任何修改。

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
- Hermes来源标识符：`clawhub`

#### 6. LobeHub (`lobehub`)

Hermes能够搜索LobeHub公开目录中的智能体条目，并将其转换为可直接安装的Hermes技能。

- 网站地址：[LobeHub](https://lobehub.com/)
- 公开智能体索引地址：[chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- 相关代码仓库：[lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes来源标识符：`lobehub`

#### 7. browse.sh (`browse-sh`)

Hermes与[browse.sh](https://browse.sh)相集成。该平台汇集了Browserbase提供的200多个针对不同网站定制的浏览器自动化SKILL.md文件，涵盖Airbnb、Amazon、arXiv、12306.cn、Etsy、Xero等诸多网站。每个技能文件都会详细说明如何对某个网站进行端到端的自动化操作，非常适合与Hermes的浏览器工具以及用户已安装的各类浏览器自动化技能一起使用。

- 网站地址：[browse.sh](https://browse.sh/)
- 目录API接口：`https://browse.sh/api/skills`
- Hermes来源标识符：`browse-sh`
- 可信度等级：`社区级`

```bash
hermes skills search airbnb --source browse-sh
hermes skills inspect browse-sh/airbnb.com/search-listings-ddgioa
hermes skills install browse-sh/airbnb.com/search-listings-ddgioa
```

标识符的格式为 `browse-sh/<hostname>/<task-id>`，与 browse.sh 目录所显示的短链接一致。内容的解析是通过各技能的详细信息端点来完成的（`/api/skills/<slug>` → `skillMdUrl`），而非通过该目录对应的 GitHub `sourceUrl`。

#### 8. 直接 URL（`url`）

可直接从任意 HTTP(S) URL 安装 `SKILL.md` —— 当技能创建者在自己的网站上托管该技能时，此方式非常实用（无需通过中心平台列表，也无需输入 GitHub 路径）。Hermes 还会自动获取 `references/`、`templates/`、`scripts/`、`assets/` 和 `examples/` 目录下被明确引用的文件，进而扫描并安装整个文件包。

- Hermes 源标识：`url`
- 标识符：即该 URL 本身（无需添加前缀）
- 范围：`SKILL.md` 以及允许列表中所指定的所有相关支持文件。Hermes 不会枚举或复制主机上的其他无关文件。

```bash
hermes skills install https://sharethis.chat/SKILL.md
hermes skills install https://example.com/my-skill/SKILL.md --category productivity
```

名称解析的顺序如下：
1. SKILL.md YAML 前置信息中的 `name:` 字段（推荐方式——所有格式正确的技能文件均应包含该字段）。
2. URL 路径中的父目录名称（例如 `.../my-skill/SKILL.md` 对应 `my-skill`，`.../my-skill.md` 也对应 `my-skill`），前提是该名称为有效的标识符（符合正则表达式 `^[a-z][a-z0-9_-]* $`）。
3. 具有 TTY 的终端上的交互式提示信息。
4. 在非交互式环境中（如 TUI 内的 `/skills install` 命令、网关平台及脚本中），会显示清晰的错误提示，指引用户使用 `--name` 参数进行手动指定。

```bash
# Frontmatter has no name and the URL slug is unhelpful — supply one:
hermes skills install https://example.com/SKILL.md --name sharethis-chat

# Or inside a chat session:
/skills install https://example.com/SKILL.md --name sharethis-chat
```

信任级别始终为 `community` —— 该技能会与其他所有来源的技能一样接受相同的安全扫描。URL 会被作为安装标识符保存，因此当您需要刷新技能时，执行 `hermes skills update` 命令便会自动从同一 URL 获取最新信息。

### 安全扫描与 `--force` 参数

所有通过 Hub 安装的技能都会经过**安全扫描器**的检测，该扫描器会排查数据外泄、命令注入、破坏性指令、供应链威胁以及其他潜在风险。

现在，`hermes skills inspect ...` 命令在可获取上游元数据的情况下也会将其显示出来，包括：
- 代码仓库 URL
- skills.sh 详情页 URL
- 安装命令
- 每周安装次数
- 上游安全审计状态
- 已知的索引/端点 URL

如果您已审查过某个第三方技能，并希望绕过某个非危险性的策略限制，可使用 `--force` 参数。

```bash
hermes skills install skills-sh/anthropics/skills/pdf --force
```

重要行为说明：  
- 参数 `--force` 可用于覆盖针对“谨慎”或“警告”级别检测结果的策略限制。  
- 但 `--force` **无法**覆盖“危险”级别的扫描判定结果。  
- 官方提供的可选技能（即 `official/...` 类别）被视为内置可信资源，因此不会显示第三方警告面板。  

### 信任等级  

| 等级 | 来源 | 策略规则 |
|------|------|----------|
| `builtin` | Hermes 内置功能 | 始终被信任 |
| `official` | 仓库中的 `optional-skills/` 目录 | 被视为内置可信资源，无第三方警告提示 |
| `trusted` | 如 `openai/skills`、`anthropics/skills`、`huggingface/skills`、`NVIDIA/skills` 等受信任的注册表或仓库 | 相较于社区来源，其策略限制更为宽松 |
| `community` | 其他所有资源（如 `skills.sh`、知名接口、自定义 GitHub 仓库以及大多数技能市场） | 非危险级别的检测结果可通过 `--force` 参数覆盖；而“危险”级别的判定结果仍会被阻止使用 |

### 更新生命周期  

当前，Hermes 的核心系统已能够追踪足够的来源信息，以便重新检查已安装技能的上游版本：

```bash
hermes skills check          # Report which installed hub skills changed upstream
hermes skills update         # Reinstall only the skills with updates available
hermes skills update react   # Update one specific installed hub skill
hermes skills update react --force   # Overwrite a skill you've edited locally
```

该机制通过结合存储的源标识符与当前上游插件包内容的哈希值来检测版本偏移。

对于缺失或非目录形式的安装（即“孤立安装”），以及路径无效或无法解析的情况（即“无效安装”），系统会跳过网络请求。缺失的目录条目可通过 `hermes skills uninstall <name>` 命令删除；而无效路径则需先检查并修复当前激活配置文件中的 `skills/.hub/lock.json`，之后才能重新尝试。系统不会自动删除任何条目。

已正常安装的插件将继续使用其源适配器原有的同步获取及传输超时设置。更新检测并没有严格的整体截止时间：即使某个已安装插件的来源地址无法访问或响应缓慢，也仍可能影响后续条目的检测进度。

对于您在本地进行过编辑的插件（即磁盘上的内容与安装时记录的哈希值不再匹配），`hermes skills update` 命令会**跳过**对这些插件的更新，从而避免您的修改被无声覆盖。如需强制使用上游版本，可传递 `--force` 参数。

:::提示 GitHub 请求频率限制
插件中心的相关操作会调用 GitHub API，未授权用户的请求频率限制为每小时 60 次。如果在安装或搜索过程中遇到频率限制错误，可在 `.env` 文件中设置 `GITHUB_TOKEN`，将请求上限提升至每小时 5,000 次。出现此类错误时，错误信息中会提供相应的解决建议。
:::

### 发布自定义插件入口

如果您希望分享一组精心挑选的技能——无论是供您的团队、组织内部使用，还是向公众公开——您可以将它们以 **tap** 的形式发布：其他 Hermes 用户可通过命令 `hermes skills tap add <owner/repo>` 将其添加到该 GitHub 仓库中。无需服务器、无需注册注册表，也无需版本发布流程，只需一个包含 `SKILL.md` 文件的目录即可。

#### 仓库结构

所谓 tap，其实就是任何格式的 GitHub 仓库（公开或私有——私有仓库需要使用 `GITHUB_TOKEN`），其结构如下：

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
- 每个技能目录都必须包含一份符合标准 [SKILL.md 前置信息格式](#skillmd-format) 的 `SKILL.md` 文件（需包含 `name`、`description` 字段，还可选择包含 `metadata.hermes.tags`、`version`、`author`、`platforms`、`metadata.hermes.config` 字段）。
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

将该代码推送到 GitHub 后，任何 Hermes 用户均可订阅并安装它：

```bash
hermes skills tap add my-org/hermes-skills
hermes skills search deploy
hermes skills install my-org/hermes-skills/deploy-runbook
```

#### 非默认路径

如果您的技能并非位于 `skills/` 目录下（通常是在向现有项目添加 `skills/` 子目录时会出现这种情况），请编辑 `~/.hermes/skills/.hub/taps.json` 文件中的对应配置项：

```json
{
  "taps": [
    {"repo": "my-org/platform-docs", "path": "internal/skills/"}
  ]
}
```

`hermes skills tap add` CLI命令会将新生成的tap默认配置在`path: "skills/"`路径下；如果需要使用其他路径，则可直接编辑该文件。`hermes skills tap list`命令可以显示每个tap的实际路径。

#### 直接安装单个技能（无需添加tap）

用户也可以直接从任何公开的GitHub仓库中安装单个技能，而无需将该整个仓库作为tap来添加：

```bash
hermes skills install owner/repo/skills/my-workflow
```

当您希望共享某项技能，而无需让用户订阅您的整个技能库时，此功能非常实用。

#### Tap的信任级别

新的Tap默认被赋予“社区”级信任度。从这些Tap中安装的技能会经过标准的安全扫描，首次安装时会显示第三方警告面板。如果您的组织或某个备受信任的来源需要更高的信任度，可将其仓库添加到`tools/skills_guard.py`文件中的`TRUSTED_REPOS`列表中（这需要提交Hermes核心版本的PR）。

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

这些插件会存储在 `~/.hermes/skills/.hub/taps.json` 文件中（该文件会根据需求自动创建）。

## 打包技能的更新（`hermes skills reset`）

Hermes 在代码仓库的 `skills/` 目录中预置了一组打包好的技能。在安装时以及每次执行 `hermes update` 操作时，系统都会将这些技能同步到 `~/.hermes/skills/` 目录，并在 `~/.hermes/skills/.bundled_manifest` 文件中记录映射关系，将每个技能名称与其同步时的内容哈希值（即**原始哈希值**）对应起来。

每次同步时，Hermes 会重新计算本地版本的内容哈希值，并将其与原始哈希值进行比对：

- **未发生变化** → 可以安全地获取上游的更新内容，将新版本的技能复制过来，并记录新的原始哈希值。
- **已发生变化** → 会被视为**用户修改过**的文件，此后将永久跳过同步处理，这样你的自定义修改就不会被覆盖。

技能内部生成的运行时缓存文件（如 `__pycache__/`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`，以及位于 `.py` 文件旁边的 `.pyc` 文件）并不计入哈希值计算范围内。因此，运行技能的辅助脚本不会导致该技能被标记为“用户修改过”，也不会使其在 `hermes skills list-modified` 或 `diff` 命令的输出中被隐藏。

虽然这种保护机制相当有效，但也存在一个潜在问题。如果你修改了某个打包好的技能，但后来又想放弃这些修改，直接从 `~/.hermes/hermes-agent/skills/` 复制回原始版本的内容，由于清单文件中仍然保存着上一次成功同步时的*旧*原始哈希值，而你新复制的内容对应的哈希值与该旧值不一致，因此同步系统会持续将其标记为“用户修改过”的状态。

`hermes skills reset` 是一条应急解决方案：

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

:::注：配置文件
每个配置文件都在其独立的 `HERMES_HOME` 目录下拥有自己的 `.bundled_manifest` 文件，因此 `hermes -p coder skills reset <name>` 命令仅会影响该配置文件。
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
