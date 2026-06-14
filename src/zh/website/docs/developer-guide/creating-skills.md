---
sidebar_position: 3
title: "Creating Skills"
description: "How to create skills for Hermes Agent — SKILL.md format, guidelines, and publishing"
---

# 创建技能

技能是为 Hermes Agent 添加新功能的首选方式。相比工具，技能更易于创建，无需对 Agent 进行代码修改，同时还可以与社区共享。

## 应该创建技能还是工具？

在以下情况下，应创建**技能**：
- 该功能可通过指令、Shell 命令以及现有工具来实现；
- 它用于封装外部 CLI 或 API，以便 Agent 通过 `terminal` 或 `web_extract` 调用；
- 无需在 Agent 中内置自定义的 Python 集成或 API 密钥管理功能。
- 示例：arXiv 搜索、Git 工作流、Docker 管理、PDF 处理、通过 CLI 工具发送邮件。

在以下情况下，应创建**工具**：
- 需要与 API 密钥、认证流程或多组件配置进行端到端集成；
- 需要每次都精确执行的自定义处理逻辑；
- 需要处理二进制数据、流式数据或实时事件。
- 示例：浏览器自动化、文本转语音、视觉分析。

## 技能目录结构

已打包的技能存储在 `skills/` 目录中，并按类别分类。官方提供的可选技能则采用相同的结构，存放在 `optional-skills/` 目录下：

```text
skills/
├── research/
│   └── arxiv/
│       ├── SKILL.md              # Required: main instructions
│       └── scripts/              # Optional: helper scripts
│           └── search_arxiv.py
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── ...
```

## SKILL.md 格式规范

```markdown
---
name: my-skill
description: Brief description (shown in skill search results)
version: 1.0.0
author: Your Name
license: MIT
platforms: [macos, linux]          # Optional — restrict to specific OS platforms
                                   #   Valid: macos, linux, windows
                                   #   Omit to load on all platforms (default)
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]
    related_skills: [other-skill-name]
    requires_toolsets: [web]            # Optional — only show when these toolsets are active
    requires_tools: [web_search]        # Optional — only show when these tools are available
    fallback_for_toolsets: [browser]    # Optional — hide when these toolsets are active
    fallback_for_tools: [browser_navigate]  # Optional — hide when these tools exist
    config:                              # Optional — config.yaml settings the skill needs
      - key: my.setting
        description: "What this setting controls"
        default: "sensible-default"
        prompt: "Display prompt for setup"
    blueprint:                              # Optional — marks this skill a runnable automation
      schedule: "0 9 * * *"              #   cron expr / "every 2h" / ISO timestamp
      deliver: origin                    #   optional (default origin)
      prompt: "Task instruction for each run"  # optional
      no_agent: false                    # optional
required_environment_variables:          # Optional — env vars the skill needs
  - name: MY_API_KEY
    prompt: "Enter your API key"
    help: "Get one at https://example.com"
    required_for: "API access"
---

# Skill Title

Brief intro.

## When to Use
Trigger conditions — when should the agent load this skill?

## Quick Reference
Table of common commands or API calls.

## Procedure
Step-by-step instructions the agent follows.

## Pitfalls
Known failure modes and how to handle them.

## Verification
How the agent confirms it worked.
```

### 平台专用技能

可通过 `platforms` 字段将技能限制在特定的操作系统上使用：

```yaml
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders)
platforms: [macos, linux]     # macOS and Linux
platforms: [windows]          # Windows only
```

一旦该选项被设置，该技能将在不兼容的平台上自动从系统提示词、`skills_list()` 函数以及斜杠命令中隐藏。若未设置或为空，则该技能会在所有平台上加载（具备向后兼容性）。

### 条件式技能激活

技能可以声明对特定工具或工具集的依赖关系。这有助于控制该技能是否会在特定会话的系统提示词中显示。

```yaml
metadata:
  hermes:
    requires_toolsets: [web]           # Hide if the web toolset is NOT active
    requires_tools: [web_search]       # Hide if web_search tool is NOT available
    fallback_for_toolsets: [browser]   # Hide if the browser toolset IS active
    fallback_for_tools: [browser_navigate]  # Hide if browser_navigate IS available
```

| 字段 | 行为 |
|-------|----------|
| `requires_toolsets` | 若列出的任意工具集均不可用，则该技能将**隐藏**。 |
| `requires_tools` | 若列出的任意工具均不可用，则该技能将**隐藏**。 |
| `fallback_for_toolsets` | 若列出的任意工具集均可用，则该技能将**隐藏**。 |
| `fallback_for_tools` | 若列出的任意工具均可用，则该技能将**隐藏**。 |

**`fallback_for_*` 的使用场景：** 创建用于在主要工具不可用时提供替代方案的技能。例如，一个带有 `fallback_for_tools: [web_search]` 属性的 `duckduckgo-search` 技能，仅会在未配置需要 API 密钥的网页搜索工具时显示。

**`requires_*` 的使用场景：** 创建仅在特定工具存在时才有意义的技能。例如，一个带有 `requires_toolsets: [web]` 属性的网页抓取工作流技能，在网页工具被禁用时不会在提示信息中造成冗余内容。

### 环境变量要求

技能可以声明其所需的环境变量。当通过 `skill_view` 加载某个技能时，其所需的变量会自动被注册，以便传递到沙箱执行环境（终端、执行代码）中。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: "Tenor API key"               # Shown when prompting user
    help: "Get your key at https://tenor.com"  # Help text or URL
    required_for: "GIF search functionality"   # What needs this var
```

每个条目均支持以下配置：
- `name`（必填）——环境变量名称
- `prompt`（可选）——用于向用户询问该变量值的提示文本
- `help`（可选）——用于获取该变量值的帮助文本或相关网址
- `required_for`（可选）——说明哪些功能需要使用该变量

用户也可以在 `config.yaml` 中手动配置直传变量：

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_VAR
    - ANOTHER_VAR
```

如需了解仅适用于 macOS 的技能示例，请参阅 `skills/apple/` 目录。

## 加载时进行安全配置

当某个技能需要 API 密钥或令牌时，可使用 `required_environment_variables` 参数进行指定。即使未设置这些值，该技能也不会因此从发现列表中隐藏。相反，Hermes 会在该技能在本地 CLI 中被加载时，以安全的方式提示用户补充所需信息。

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: Tenor API key
    help: Get a key from https://developers.google.com/tenor
    required_for: full functionality
```

用户可以跳过设置步骤，直接继续加载技能。Hermes 永不会将原始密钥值暴露给模型。网关和消息传递会话会显示本地设置指南，而不会通过通信链路收集密钥信息。

:::提示：沙箱参数传递
当技能被加载后，所有已设置的 `required_environment_variables` 都会**自动传递**到 `execute_code` 和 `terminal` 沙箱中——包括 Docker 和 Modal 等远程后端。用户的技能脚本可以直接使用 `$TENOR_API_KEY`（或在 Python 中使用 `os.environ["TENOR_API_KEY"]`），无需用户进行任何额外配置。详情请参阅[环境变量传递](/user-guide/security#environment-variable-passthrough)。
:::

为保持向后兼容性，传统的 `prerequisites.env_vars` 仍被支持，可作为其别名使用。

### 配置设置（config.yaml）
技能可以声明非密钥类设置，这些设置会存储在 `config.yaml` 文件的 `skills.config` 命名空间下。与环境变量（即存储在 `.env` 文件中的密钥信息）不同，配置设置用于存储路径、偏好设置以及其他非敏感值。

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: Path to the plugin data directory
        default: "~/myplugin-data"
        prompt: Plugin data directory path
      - key: myplugin.domain
        description: Domain the plugin operates on
        default: ""
        prompt: Plugin domain (e.g., AI/ML research)
```

每个条目均支持以下字段：
- `key`（必填）——该设置的点路径（例如 `myplugin.path`）
- `description`（必填）——说明该设置控制的内容
- `default`（可选）——用户未进行配置时的默认值
- `prompt`（可选）——在执行 `hermes config migrate` 时显示的提示文本；若未指定则默认使用 `description` 的内容

**工作原理：**

1. **存储方式：** 这些值会被写入 `config.yaml` 文件中的 `skills.config.<key>` 路径下：
   ```yaml
   skills:
     config:
       myplugin:
         path: ~/my-data
   ```

2. **发现功能**：执行 `hermes config migrate` 命令后，系统会扫描所有已启用的智能体技能，找出未配置的设置，并向用户发出提示。这些设置也会显示在 `hermes config show` 的“智能体技能设置”选项中。

3. **运行时注入**：当某个智能体技能被加载时，其配置值会被解析并添加到该技能生成的响应消息中。
   ```
   [Skill config (from ~/.hermes/config.yaml):
     myplugin.path = /home/user/my-data
   ]
   ```
代理无需直接读取`config.yaml`文件，即可获取已配置的数值。

4. **手动设置**：用户也可以直接指定数值进行设置。
   ```bash
   hermes config set skills.config.myplugin.path ~/my-data
   ```

:::提示：如何选择合适选项
对于 API 密钥、令牌以及其他**机密信息**（存储在 `~/.hermes/.env` 文件中，且绝不会显示给模型），请使用 `required_environment_variables` 选项。而对于**路径、偏好设置以及非敏感配置**（存储在 `config.yaml` 文件中，可通过 `config show` 命令查看），则应使用 `config` 选项。
:::

### 凭证文件要求（OAuth 令牌等）

那些需要使用 OAuth 或基于文件的凭证的技能，可以指定需要挂载到远程沙箱中的文件。此功能适用于以**文件形式**存储的凭证（而非环境变量）——通常是指由设置脚本生成的 OAuth 令牌文件。

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
  - path: google_client_secret.json
    description: Google OAuth2 client credentials
```

每个条目都支持以下参数：
- `path`（必填）——相对于`~/.hermes/`的文件路径
- `description`（可选）——说明该文件的作用及创建方式

Hermes在加载时会检查这些文件是否存在。若文件缺失，则会触发`setup_needed`状态。对于已存在的文件，系统会自动：
- 以只读绑定挂载的方式将其**导入Docker容器**
- 在**Modal沙箱**中进行同步处理（在创建时以及每次执行命令前都会同步，从而确保会话进行中的OAuth功能正常工作）
- 直接在**本地后端**中使用，无需任何特殊处理

:::提示 如何选择使用方式
对于简单的API密钥和令牌（存储在`~/.hermes/.env`中的字符串），请使用`required_environment_variables`。而对于OAuth令牌文件、客户端密钥、服务账户JSON、证书，或任何以文件形式存在的凭证，则应使用`required_credential_files`。
:::

如需查看同时使用这两种方式的完整示例，请参阅`skills/productivity/google-workspace/SKILL.md`。

## 技能开发指南

### 不要依赖外部组件

优先使用Python标准库、curl以及Hermes现有的工具（如`web_extract`、`terminal`、`read_file`）。如果确实需要其他依赖项，应在技能文档中详细说明安装步骤。

### 逐步披露功能

先介绍最常用的工作流程，将边缘情况和高级用法放在最后。这样可以在处理常规任务时减少令牌的使用量。

### 包含辅助脚本

对于XML/JSON解析或复杂逻辑，可将相关辅助脚本放入`scripts/`目录中——不必期望大语言模型每次都自行编写解析代码。

### 以文档形式传递媒体内容（使用`[[as_document]]`指令）

如果您的技能生成了高分辨率截图、图表或其他因有损预览压缩会导致质量下降的图像，请在响应中的适当位置（通常为最后一行）添加`[[as_document]]`指令。网关会解析该指令，将所有提取出的媒体文件路径作为可下载的附件发送，而非以内嵌图片的形式呈现。更多详细信息请参阅[技能输出与媒体传递](../user-guide/features/skills.md#skill-output-and-media-delivery)。

#### 如何在SKILL.md中引用内置脚本

当技能被加载后，激活消息会以`[Skill directory: /abs/path]`的形式显示技能目录的绝对路径，同时还会在SKILL.md的正文中自动替换两个模板占位符：

| 占位符 | 替换为的内容 |
|---|---|
| `${HERMES_SKILL_DIR}` | 技能目录的绝对路径 |
| `${HERMES_SESSION_ID}` | 当前活跃会话的ID（如果没有会话，则保持原样） |

因此，SKILL.md可以通过这些占位符直接指示智能体运行内置脚本：

```markdown
To analyse the input, run:

    node ${HERMES_SKILL_DIR}/scripts/analyse.js <input>
```

智能体会看到已被替换的绝对路径，随后直接使用准备就绪的命令调用 `terminal` 工具——无需进行路径计算，也无需额外的 `skill_view` 往返调用。若需全局禁用此替换功能，可在 `config.yaml` 中将 `skills.template_vars` 设置为 `false`。

#### 内联 Shell 代码片段（可选）

智能体还能够在 SKILL.md 文件的正文中嵌入形如 `` !`cmd` `` 的内联 Shell 代码片段。启用该功能后，每个代码片段的输出内容会在智能体读取消息之前直接嵌入其中，从而使智能体能够注入动态上下文：

```markdown
Current date: !`date -u +%Y-%m-%d`
Git branch: !`git -C ${HERMES_SKILL_DIR} rev-parse --abbrev-ref HEAD`
```

该功能默认处于**关闭状态**——SKILL.md 文件中的任何代码片段都无需批准即可在主机上运行，因此请仅对您信任的技能来源启用此功能：

```yaml
# config.yaml
skills:
  inline_shell: true
  inline_shell_timeout: 10   # seconds per snippet
```

代码片段以技能目录作为工作目录运行，其输出长度上限为4000个字符。若出现故障（如超时或非零退出状态），系统会显示简短的`[inline-shell error: ...]`提示，而不会导致整个技能失效。

### 进行测试

运行该技能，并确认智能体能够正确遵循指令执行：

```bash
hermes chat --toolsets skills -q "Use the X skill to do Y"
```

## 技能应放置于何处？

所有 Hermes 安装版本都会自带已打包的技能（位于 `skills/` 目录中）。这类技能应当**对大多数用户都具有广泛实用性**，涵盖以下领域：
- 文档处理、网络调研、常见开发工作流程、系统管理
- 被大量不同用户频繁使用

如果您的技能虽为官方出品且实用，但并非所有人都需要（例如集成付费服务或依赖大型组件），则应将其放入 **`optional-skills/`** 目录——该目录中的技能会随代码仓库一同提供，可通过 `hermes skills browse` 命令查询（标记为“官方技能”），并且安装时会享有内置信任机制。

对于那些专业化、由社区贡献或面向小众群体的技能，将其上传至 **Skills Hub** 更为合适——通过将该技能注册到对应平台，再利用 `hermes skills install` 命令进行共享。

## 架构蓝图：兼具技能功能的自动化脚本

**架构蓝图**本质上仍属于普通技能，只不过会在其前置信息中额外指定执行时间表。只需添加 `metadata.hermes.blueprint` 块，该技能便能转化为可共享、可运行的自动化脚本：

```yaml
metadata:
  hermes:
    tags: [blueprint, email]
    blueprint:
      schedule: "0 8 * * *"     # presence of `blueprint:` marks it runnable
      deliver: telegram          # optional (default: origin)
      prompt: "Summarize my unread email and today's calendar."  # optional
      no_agent: false            # optional
```

由于蓝图本质上也是一种技能，因此它会原封不动地经过整个技能处理流程——包括搜索、检查、安装、安全扫描、来源追溯、数据抽取、集中索引处理，以及用于共享的 `hermes skills publish` 操作。用户无需学习任何新内容。

**安装蓝图**：当您安装包含 `blueprint:` 块的技能时，Hermes 会将其注册为“建议的定时任务”，而非直接安排执行。定时任务功能是**可选的**——安装过程绝不会默默创建重复运行的任务。您可以通过 `/suggestions` 查看相关建议并予以确认：

```bash
hermes skills install owner/morning-brief
# → Blueprint: 'morning-brief' is an automation (schedule 0 8 * * *).
#   Added to your suggestions — run /suggestions to schedule or dismiss it.

# then, in a session:
/suggestions             # lists pending suggestions, numbered
/suggestions accept 1    # creates the cron job
/suggestions dismiss 1   # never offer it again
```

蓝图是统一“推荐定时任务”界面的一种**数据来源**——该界面同样用于展示精心挑选的入门自动化方案，以及后续提供的使用模式与集成建议。详情请参阅下文的[推荐定时任务](#suggested-cron-jobs)。

**分享您自行构建的自动化方案**：通过定时任务加载的蓝图（如 `hermes cron create --skill <name> ...`）可以导出为 SKILL.md 文件，并像其他技能一样进行发布。这样一来，您亲自定制的自动化方案就能让他人只需一键即可安装使用。

蓝图机制并未引入新的对象类型、存储方式或传输机制——蓝图本身仍属于技能范畴，调度逻辑则由定时任务承担，而分享功能则沿用现有的发布/tap/index 流程。

## 推荐定时任务

Hermes 能够主动*推荐*各种自动化方案，让您只需轻触一下即可接受，无需手动组装定时任务。无论来自何处，所有推荐都会通过同一个界面——即 `/suggestions` 命令——呈现：

| 数据来源 | 触发条件 |
|--------|---------|
| `catalog` | 精心挑选的入门自动化方案（`/suggestions catalog`）——每日简报、重要邮件监控、每周回顾、工作日开始提醒等 |
| `blueprint` | 您安装了包含 `blueprint:` 块的技能 |
| `usage` | 后台分析发现存在需要定时任务处理的重复性需求 |
| `integration` | 您连接了某个账户（如 Gmail、GitHub 等），系统便会提供相关的自动化方案 |

```bash
/suggestions             # list pending
/suggestions accept N    # schedule suggestion N (creates the cron job)
/suggestions dismiss N   # dismiss it — latched, never re-offered
/suggestions catalog     # add the curated starter automations
```

接受建议时会调用 `cronjob` 工具所使用的相同函数 `cron.jobs.create_job`——并不存在第二种任务处理引擎。建议**绝不会**自动创建任务，接受操作始终需要明确确认。被拒绝的建议会通过唯一标识键被锁定，从而避免重复出现相同的提议。待处理列表设有上限，因此不会变成令人困扰的冗余信息堆。

**重要邮件监控器**这一功能项遵循“轮询→分类→展示”的工作流程：它使用简单的分类模型（位于 `config.yaml` 中的 `auxiliary.monitor`）对收件箱中的邮件进行评分，仅将紧急程度超过阈值的邮件呈现出来，其余邮件则保持沉默。

## 发布技能

### 发布至技能中心

```bash
hermes skills publish skills/my-skill --to github --repo owner/repo
```

### 导入到自定义仓库

将您的仓库添加为接入点：

```bash
hermes skills tap add owner/repo
```

用户随后便可以从此仓库中搜索并安装这些技能。

## 安全扫描

所有通过 Hub 安装的技能都会经过安全扫描器检测，重点排查以下风险：

- 数据窃取行为
- 提示注入企图
- 破坏性命令
- Shell 注入攻击

信任等级划分如下：
- `builtin` — 与 Hermes 一同提供（始终被信任）
- `official` — 来自仓库中的 `optional-skills/` 目录（默认被信任，无第三方警告）
- `trusted` — 来自 openai/skills、anthropic/skills、huggingface/skills
- `community` — 非危险性问题可通过 `--force` 参数忽略；危险性问题仍会被阻止使用

目前，Hermes 能够从多种外部发现机制中加载第三方技能：
- 直接的 GitHub 标识符（例如 `openai/skills/k8s`）
- `skills.sh` 标识符（例如 `skills-sh/vercel-labs/json-render/json-render-react`）
- 通过 `/.well-known/skills/index.json` 提供的知名接口

如果您希望自己的技能无需依赖 GitHub 特定的安装工具即可被发现，建议除了在仓库或市场平台上发布外，还通过知名的接口来提供这些技能。
