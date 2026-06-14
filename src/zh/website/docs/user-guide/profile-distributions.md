---
sidebar_position: 3
---

# 配置分发：共享完整代理

**配置分发**功能将一个完整的Hermes代理——包括其个性设定、技能、定时任务、MCP连接信息以及配置文件——打包为一个Git仓库。任何拥有该仓库访问权限的人都可以通过一条命令即可安装整个代理，对其进行更新，同时不会影响其原有的记忆、会话记录和API密钥。

如果某个[配置文件](./profiles.md)代表的是本地代理，那么配置分发则意味着将该代理变为可共享的形式。

## 这意味着什么

在配置分发功能出现之前，要共享一个Hermes代理，就需要将以下内容传递给他人：

1. `SOUL.md` 文件
2. 需要安装的技能列表
3. 已移除敏感信息的 `config.yaml` 文件
4. 已连接的MCP服务器说明
5. 所设置的定时任务
6. 需要设置的环境变量说明

……然后还要指望对方能正确地组装这些内容。每当版本升级或修复漏洞时，都不得不重复这一繁琐的过程。

而借助配置分发功能，所有这些内容都存储在同一个Git仓库中：

```
my-research-agent/
├── distribution.yaml    # manifest: name, version, env-var requirements
├── SOUL.md              # the agent's personality / system prompt
├── config.yaml          # model, temperature, reasoning, tool defaults
├── skills/              # bundled skills that come with the agent
├── cron/                # scheduled tasks the agent runs
└── mcp.json             # MCP servers the agent connects to
```

接收方运行：

```bash
hermes profile install github.com/you/my-research-agent --alias
```

……现在他们已经拥有了完整的智能体。他们只需填写自己的 API 密钥（从 `.env.EXAMPLE` 更改为 `.env`），就可以运行 `my-research-agent chat`，或通过 Telegram、Discord、Slack 或任何网关平台与之交互。当您推送新版本时，他们只需执行 `hermes profile update my-research-agent` 即可获取您的更新——他们的记忆和会话数据将保持不变。

## 为何选择 git？

我们曾考虑过使用压缩包、HTTP 归档文件或自定义格式，但都没有 git 更出色：

- **对创建者而言无需构建步骤**。只需将代码推送到 GitHub，使用者即可直接安装，无需经历“打包、上传、更新索引”这样的循环流程。
- **标签、分支和提交本身就是版本控制机制**。推送一个标签就能完成其他工具中“打包并上传版本”的功能。
- **更新仅需一次拉取操作**，而无需重新下载整个归档文件。
- **高度透明**。用户可以浏览代码仓库，查看不同版本间的差异，提交问题，甚至 fork 仓库进行自定义修改。
- **私有仓库也可免费使用**。无论是 SSH 密钥、`git credential` 工具，还是 GitHub CLI 中存储的凭据，终端已配置的任何认证方式都能无缝应用。
- **可重复性由提交 SHA 值保证**，这与 pip 和 npm 的记录方式一致。

唯一的缺点是：接收方需要安装 git。而到了 2026 年，所有运行 Hermes 的机器都已具备这一条件。

## 何时应该使用分发包？

适合使用的情况包括：

- **您希望与团队或社区共享某个专用智能体**——比如合规监控工具、代码审查助手、研究辅助智能体或客户支持机器人。
- **您需要将同一个智能体部署到多台机器上**，且不想每次都手动复制文件。
- **您正在对智能体进行迭代开发**，希望接收方能通过一条命令即可获取最新版本。
- **您正在将智能体作为产品进行开发**——设置了标准化默认参数、精选的技能库以及优化过的提示词，供他人作为起点使用。

不适合使用的情况包括：

- **您只是想在自己的机器上备份智能体配置**。此时应使用 [`hermes profile export` / `import`](../reference/profile-commands.md#hermes-profile-export) 命令——它们正是为此设计的。
- **您希望同时共享 API 密钥**。`auth.json` 和 `.env` 文件被刻意排除在分发包之外，每个安装者都需要自行提供凭据。
- **您希望共享记忆数据、会话记录或对话历史**。这些属于用户隐私数据，而非分发包的内容，因此永远不会被包含在内。

## 全生命周期：从创建者到安装者再到更新

以下是完整的端到端流程，您可以根据感兴趣的部分进行阅读。

---

## 面向创建者：发布分发包

### 第一步——从可用的配置文件开始

像处理其他配置文件一样构建并优化该智能体：

```bash
hermes profile create research-bot
research-bot setup                    # configure model, API keys
# Edit ~/.hermes/profiles/research-bot/SOUL.md
# Install skills, wire up MCP servers, schedule cron jobs, etc.
research-bot chat                     # dogfood until it feels right
```

### 第 2 步 — 添加 `distribution.yaml` 文件

创建 `~/.hermes/profiles/research-bot/distribution.yaml` 文件：

```yaml
name: research-bot
version: 1.0.0
description: "Autonomous research assistant with arXiv and web tools"
hermes_requires: ">=0.12.0"
author: "Your Name"
license: "MIT"

# Tell installers which env vars the agent needs. These are checked against
# the installer's shell and existing .env file so they don't get nagged
# about keys they already have configured.
env_requires:
  - name: OPENAI_API_KEY
    description: "OpenAI API key (for model access)"
    required: true
  - name: SERPAPI_KEY
    description: "SerpAPI key for web search"
    required: false
    default: ""
```

这就是完整的清单文件了。除 `name` 字段外，其余所有字段都设置了合理的默认值。

### 第 3 步 — 推送到 Git 仓库

```bash
cd ~/.hermes/profiles/research-bot
git init
git add .
git commit -m "v1.0.0"
git remote add origin git@github.com:you/research-bot.git
git tag v1.0.0
git push -u origin main --tags
```

该代码仓库现已升级为发布版本，任何拥有访问权限的用户均可进行安装。

:::note
Git 仓库中包含**配置目录中的所有内容，但已从发布版本中排除的文件除外**：`auth.json`、`.env`、`memories/`、`sessions/`、`state.db*`、`logs/`、`workspace/`、`*_cache/`、`local/`。这些文件仍会保留在您的机器上。如果您希望排除更多路径，还可以添加 `.gitignore` 文件。
:::

### 第 4 步 — 为版本化发布添加标签

每当智能体达到稳定状态时，便需提升版本号并为其添加标签：

```bash
# Edit distribution.yaml: version: 1.1.0
git add distribution.yaml SOUL.md skills/
git commit -m "v1.1.0: tighter research SOUL, add arxiv skill"
git tag v1.1.0
git push --tags
```

运行 `hermes profile update research-bot` 命令的接收端将会获取最新版本。

### 代码仓库的结构

一个完整的发布版：

```
research-bot/
├── distribution.yaml            # required
├── SOUL.md                      # strongly recommended
├── config.yaml                  # model, provider, tool defaults
├── mcp.json                     # MCP server connections
├── skills/
│   ├── arxiv-search/SKILL.md
│   ├── paper-summarization/SKILL.md
│   └── citation-lookup/SKILL.md
├── cron/
│   └── weekly-digest.json       # scheduled tasks
└── README.md                    # human-facing description (optional)
```

### 发行版自带内容与用户自定义内容

当安装程序升级到新版本时，部分文件会被替换（属于作者维护的域），而另一部分则保持不变（属于安装程序维护的域）。默认设置如下：

| 类别 | 路径 | 升级时处理方式 |
|---|---|---|
| **发行版自带内容** | `SOUL.md`、`config.yaml`、`mcp.json`、`skills/`、`cron/`、`distribution.yaml` | 从新克隆的版本中替换 |
| **配置覆盖项** | `config.yaml` | 默认情况下会保留原有设置——因为安装程序可能已对模型或服务提供商进行了定制。如需重置，可在升级时使用 `--force-config` 参数 |
| **用户自定义内容** | `memories/`、`sessions/`、`state.db*`、`auth.json`、`.env`、`logs/`、`workspace/`、`plans/`、`home/`、`*_cache/`、`local/` | 完全不会被修改 |

您可以在清单文件中自定义发行版自带内容的列表：

```yaml
distribution_owned:
  - SOUL.md
  - skills/research/            # only my research skills; other installed skills stay
  - cron/digest.json
```

如果未指定，则会采用上述默认设置——这正是大多数发行版所期望的。  

---

## 面向安装程序：使用发行版  

### 安装

```bash
hermes profile install github.com/you/research-bot --alias
```

执行流程如下：

1. 将仓库克隆到临时目录中。
2. 读取 `distribution.yaml` 文件，并展示配置清单（包括名称、版本、描述、作者以及必需的环境变量）。
3. 检查每个必需的环境变量在您的Shell环境及目标配置文件现有的 `.env` 中的设置情况，分别标记为“✓ 已设置”或“需设置”，让您清楚知晓哪些需要配置。
4. 提示您确认操作。如需跳过此步骤，可输入 `-y` / `--yes`。
5. 将发行版自带的文件复制到 `~/.hermes/profiles/research-bot/` 目录中（具体路径取决于配置清单中的 `name` 指定的位置）。
6. 生成带有注释标记的 `.env.EXAMPLE` 文件——请将其复制为 `.env` 并填写实际值。
7. 若使用 `--alias` 参数，会生成一个快捷命令封装，让您可以直接运行 `research-bot chat`。

### 源代码类型

任何 Git 地址均可使用：

```bash
# GitHub shorthand
hermes profile install github.com/you/research-bot

# Full HTTPS
hermes profile install https://github.com/you/research-bot.git

# SSH
hermes profile install git@github.com:you/research-bot.git

# Self-hosted, GitLab, Gitea, Forgejo — any Git host
hermes profile install https://git.example.com/team/research-bot.git

# Private repo using your configured git auth
hermes profile install git@github.com:your-org/internal-bot.git

# Local directory during development (no git push needed)
hermes profile install ~/my-profile-in-progress/
```

### 覆盖配置文件名称

有两名用户希望使用相同的发行版，但希望将其命名为不同的配置文件名称：

```bash
# Alice
hermes profile install github.com/acme/support-bot --name support-us --alias
# Bob (same distribution, different local name)
hermes profile install github.com/acme/support-bot --name support-eu --alias
```

### 填写环境变量

安装完成后，代理的配置文件中会包含一个 `.env.EXAMPLE` 文件：

```
# Environment variables required by this Hermes distribution.
# Copy to `.env` and fill in your own values before running.

# OpenAI API key (for model access)
# (required)
OPENAI_API_KEY=

# SerpAPI key for web search
# (optional)
# SERPAPI_KEY=
```

复制它：

```bash
cp ~/.hermes/profiles/research-bot/.env.EXAMPLE ~/.hermes/profiles/research-bot/.env
# Edit .env, paste your real keys
```

在安装过程中，那些已存在于您的shell环境中的必需密钥（例如在`~/.zshrc`文件中导出的`OPENAI_API_KEY`）会标记为“✓ 已设置”——您无需在`.env`文件中重复添加这些密钥。

### 查看已安装的内容

```bash
hermes profile info research-bot
```

显示内容：

```
Distribution: research-bot
Version:      1.0.0
Description:  Autonomous research assistant with arXiv and web tools
Author:       Your Name
Requires:     Hermes >=0.12.0
Source:       https://github.com/you/research-bot
Installed:    2026-05-08T17:04:32+00:00

Environment variables:
  OPENAI_API_KEY (required) — OpenAI API key (for model access)
  SERPAPI_KEY (optional) — SerpAPI key for web search
```

`hermes profile list`命令还会显示`Distribution`列，让您一目了然地看出哪些配置文件来自代码仓库，哪些是手动创建的。

```
 Profile          Model                        Gateway      Alias        Distribution
 ───────────────    ───────────────────────────    ───────────    ───────────    ────────────────────
 ◆default         claude-sonnet-4              stopped      —            —
  coder           gpt-5                        stopped      coder        —
  research-bot    claude-opus-4                stopped      research-bot research-bot@1.0.0
  telemetry       claude-sonnet-4              running      telemetry    telemetry@2.3.1
```

### 更新

```bash
hermes profile update research-bot
```

具体流程如下：

1. 从记录的源地址重新克隆仓库。
2. 替换由平台管理的文件（如 SOUL、技能文件、cron 配置及 mcp.json）。
3. **保留**您的 `config.yaml` 文件——您可能已对模型参数、温度值或其他设置进行了自定义调整。如需覆盖这些设置，请使用 `--force-config` 参数。
4. **绝不**修改用户数据：包括记忆内容、会话记录、认证信息、`.env` 配置文件、日志以及状态数据。

该过程无需重新下载整个压缩包，不会覆盖您对配置文件所做的本地修改，也不会删除您的对话历史记录。

### 删除操作

```bash
hermes profile delete research-bot
```

在要求您确认之前，删除提示会先显示相关分布信息。

```
Profile: research-bot
Path:    ~/.hermes/profiles/research-bot
Model:   claude-opus-4 (anthropic)
Skills:  12
Distribution: research-bot@1.0.0
Installed from: https://github.com/you/research-bot

This will permanently delete:
  • All config, API keys, memories, sessions, skills, cron jobs
  • Command alias (~/.local/bin/research-bot)

Type 'research-bot' to confirm:
```

这样，你就绝不会在不知该智能体来源且无法重新安装的情况下，误将其删除。

---

## 使用场景与模式

### 个人用途：在多台设备间同步同一个智能体

你在笔记本电脑上构建了一个研究助手智能体，现在希望在工作站上也能使用同一个智能体。

```bash
# Laptop
cd ~/.hermes/profiles/research-bot
git init && git add . && git commit -m "initial"
git remote add origin git@github.com:you/research-bot.git
git push -u origin main

# Workstation
hermes profile install github.com/you/research-bot --alias
# Fill in .env. Done.
```

在笔记本电脑上进行的任何代码迭代操作（如 `git commit && push`）都会通过 `hermes profile update research-bot` 命令同步到工作站。各设备的记忆是独立存储的——笔记本电脑仅保存自身的对话记录，工作站也仅保存自身的记录，两者之间不会产生冲突。

### 团队：部署经过审核的内部智能体

您的工程团队希望拥有一个具备特定 SOUL 配置、特定技能，并能自动为每份 Pull Request 执行处理任务的共享式代码审查智能体。

```bash
# Engineering lead
cd ~/.hermes/profiles/pr-reviewer
# ... build and tune ...
git init && git add . && git commit -m "v1.0 PR reviewer"
git tag v1.0.0
git push -u origin main --tags    # push to your company's internal Git host

# Each engineer
hermes profile install git@github.com:your-org/pr-reviewer.git --alias
# Fill in .env with their own API key (billed to them), .env.EXAMPLE points at what's required
pr-reviewer chat
```

当主版本 v1.1 发布后（带来了更强大的 SOUL 功能以及新的智能技能），工程师们只需运行 `hermes profile update pr-reviewer` 命令，短短几分钟内所有人就能使用到新版本。

### 社区版：发布公共智能体

如果您开发出了创新性的工具——比如“多市场交易助手”、“学术论文摘要生成器”或“Minecraft 服务器运维辅助工具”——并希望与他人分享，也可以这样做。

```bash
# You
cd ~/.hermes/profiles/polymarket-trader
# Write a solid README.md at the repo root — GitHub shows it on the repo page
git init && git add . && git commit -m "v1.0"
git tag v1.0.0
# Publish to a public GitHub repo
git remote add origin https://github.com/you/hermes-polymarket-trader.git
git push -u origin main --tags

# Anyone
hermes profile install github.com/you/hermes-polymarket-trader --alias
```

将安装命令发布到推特上。尝试使用它的人会向你反馈问题并提交 Pull Request。如果有人希望进行定制，他们就会创建分支——这正是大家早已熟悉的 Git 开发流程。

### 产品：推出功能完备的智能代理

你可能在 Hermes 的基础上进行了扩展——或许构建了一个合规监控工具、一套客户支持系统，或是某个特定领域的研究平台。现在你想将其作为产品进行推广。

```yaml
# distribution.yaml
name: telemetry-harness
version: 2.3.1
description: "Compliance telemetry harness — monitors and reviews regulated workflows"
hermes_requires: ">=0.13.0"
author: "Acme Compliance Inc."
license: "Commercial"

env_requires:
  - name: ACME_API_KEY
    description: "Your Acme Compliance license key (email support@acme.com)"
    required: true
  - name: OPENAI_API_KEY
    description: "OpenAI API key for model access"
    required: true
  - name: GRAPHITI_MCP_URL
    description: "URL for your Graphiti knowledge graph instance"
    required: false
    default: "http://127.0.0.1:8000/sse"
```

您的客户只需执行一条命令即可完成安装；安装预览会明确告知他们需要准备哪些密钥；一旦您为新版本添加标签，更新便会立即推送；而他们的合规数据（位于 `memories/` 和 `sessions/` 目录中）则永远不会离开他们的设备。

### 临时型：基于共享基础设施的一次性脚本

您是运维负责人。您需要一个临时代理，用于诊断生产环境中的故障——即一个预置了所需工具及MCP连接的标准化SOUL脚本——并在接下来的一周内运行在三名值班工程师的笔记本电脑上。

```bash
# You
# Build the profile, commit, push a private repo
git push -u origin main

# Each on-call
hermes profile install git@github.com:your-org/incident-2026-q2.git --alias

# Incident resolved — tear it down
hermes profile delete incident-2026-q2
```

其安装与删除的循环成本极低，甚至可以视为一次性操作。

```bash
# Your installed version
hermes profile info research-bot | grep Version

# Latest upstream (without installing)
git ls-remote --tags https://github.com/you/research-bot | tail -5
```

### 在更新过程中保留本地配置的定制设置

默认的更新机制已可实现这一功能：`config.yaml` 文件会得到保留。为更加稳妥，建议将您的本地修改内容保存在发行版不拥有的文件中：

```yaml
# ~/.hermes/profiles/research-bot/local/my-overrides.yaml
# (distribution never touches local/)
```

……并在需要时从 `config.yaml` 或您的 SOUL 中引用它。

### 强制进行完整重新安装

```bash
# Nuke and re-install from scratch (loses memories/sessions too)
hermes profile delete research-bot --yes
hermes profile install github.com/you/research-bot --alias

# Update to current main but reset config.yaml to the distribution's default
hermes profile update research-bot --force-config --yes
```

### 复制并自定义

标准的 Git 工作流程——各类发行版其实不过是仓库而已：

```bash
# Fork the repo on GitHub, then install your fork
hermes profile install github.com/yourname/forked-research-bot --alias

# Iterate locally in ~/.hermes/profiles/forked-research-bot/
# Edit SOUL.md, commit, push to your fork
# Upstream changes: pull them into your fork the usual way
```

### 在推送之前先测试分发版本

从作者的机器上操作：

```bash
# Install from a local directory (no git push needed)
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test --alias

# Tweak, delete, re-install until it's right
hermes profile delete research-bot-test --yes
hermes profile install ~/.hermes/profiles/research-bot --name research-bot-test
```

## 分发包中绝不会包含的内容

即便开发者意外将其放入分发包，安装程序也会强制排除这些路径。没有任何配置选项可以绕过这一限制——这一安全机制经过了回归测试，属于不可更改的规则：

- `auth.json` — OAuth令牌、平台凭证  
- `.env` — API密钥、敏感信息  
- `memories/` — 对话记忆数据  
- `sessions/` — 对话历史记录  
- `state.db`、`state.db-shm`、`state.db-wal` — 会话元数据  
- `logs/` — 智能体运行日志及错误日志  
- `workspace/` — 生成的临时工作文件  
- `plans/` — 草稿计划内容  
- `home/` — Docker后端中用户的主目录  
- `*_cache/` — 图像/音频/文档缓存文件  
- `local/` — 用户专属的定制化空间  

当你克隆某个分发包时，这些文件根本不存在；更新时它们也不会被添加。即便在五台机器上安装相同的分发包，每台机器也会拥有独立的数据集。

## 安全性与信任机制

默认情况下，配置文件分发包不会被签名。这意味着你需要信任：

- **Git托管平台**（GitHub/GitLab等），确保其提供的内容确实来自开发者；
- **开发者本身**，确保其没有植入恶意Soul文件、技能或定时任务。

分发包中的定时任务**不会自动触发**——安装程序会输出 `hermes -p <name> cron list` 命令，需由你手动启用。而Soul文件和技能在开始与对应配置文件对话时就会立即生效，因此若从陌生来源安装，建议先阅读相关文件。

简单类比：安装分发包就如同安装浏览器扩展或VS Code插件——操作简便但功能强大，关键在于信任来源。对于企业内部使用的分发包，可直接使用私有仓库及常规Git认证方式，无需额外配置。

未来版本可能会加入签名功能、包含已确认提交SHA值的锁定文件（`.distribution-lock.yaml`），以及可在更新前显示差异的 `--dry-run` 参数。不过这些功能目前尚未正式推出。

## 技术实现细节

如需了解实现细节、精确的CLI行为及所有参数信息，请参阅[配置文件命令参考文档](../reference/profile-commands.md#distribution-commands)。

简述如下：

- `install`、`update`、`info` 命令均隶属于 `hermes profile` 命令集，并非独立的命令结构；
- 配置文件采用YAML格式，仅要求包含 `name` 字段这一最小结构；
- 安装程序会使用你本地的 `git` 工具进行克隆，因此Shell已处理的任何认证方式（如SSH密钥、凭证管理工具）均可直接使用；
- 克隆完成后，`.git/` 目录会被移除——因为安装后的配置文件并非Git检出版本，从而避免“不小心将 `.env` 文件提交到分发包的Git历史记录中”的风险；
- 预留的配置文件名称（`hermes`、`test`、`tmp`、`root`、`sudo`）在安装时会被拒绝，以避免与常见系统命令冲突。

## 相关文档

- [配置文件：运行多个智能体](./profiles.md) —— 基本概念  
- [配置文件命令参考文档](../reference/profile-commands.md) —— 所有参数及选项说明  
- [`hermes profile export` / `import`](../reference/profile-commands.md#hermes-profile-export) —— 本地备份/恢复（非分发包相关）  
- [在Hermes中使用Soul](../guides/use-soul-with-hermes.md) —— 创建智能体个性  
- [个性与Soul](./features/personality.md) —— Soul在智能体中的功能作用  
- [技能目录](../reference/skills-catalog.md) —— 可打包的技能列表
