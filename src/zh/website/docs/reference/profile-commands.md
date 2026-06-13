---
sidebar_position: 7
---

# 配置文件命令参考

本页面介绍了与 [Hermes 配置文件](../user-guide/profiles.md) 相关的所有命令。关于常规的 CLI 命令，请参阅 [CLI 命令参考](./cli-commands.md)。

## `hermes profile`

```bash
hermes profile <subcommand>
```

用于管理配置文件的顶层命令。若直接运行 `hermes profile` 而不指定子命令，则会显示帮助信息。

| 子命令 | 描述 |
|----------|------|
| `list` | 列出所有配置文件。 |
| `use` | 设置当前（默认）激活的配置文件。 |
| `create` | 创建新的配置文件。 |
| `describe` | 读取或设置配置文件的描述信息（由看板调度器用于路由决策）。 |
| `delete` | 删除配置文件。 |
| `show` | 显示配置文件的详细信息。 |
| `alias` | 为配置文件重新生成Shell别名。 |
| `rename` | 重命名配置文件。 |
| `export` | 将配置文件导出为tar.gz压缩包。 |
| `import` | 从tar.gz压缩包中导入配置文件。 |
| `install` | 从Git地址或本地目录安装配置文件版本。详情请参阅[配置文件版本](../user-guide/profile-distributions.md)。 |
| `update` | 重新拉取由版本管理器管理的配置文件，并重新应用其相关组件。 |
| `info` | 显示配置文件的版本元数据（来源URL、提交信息、最后更新时间）。 |

## `hermes profile list`

```bash
hermes profile list
```

列出所有配置文件。当前处于激活状态的配置文件会标有 `*` 符号。

**示例：**

```bash
$ hermes profile list
  default
* work
  dev
  personal
```

无可用选项。

## `hermes profile use`

```bash
hermes profile use <name>
```

将 `<name>` 设置为当前激活的配置文件。此后所有未使用 `-p` 参数的 `hermes` 命令都将使用该配置文件。

| 参数 | 描述 |
|----------|-------------|
| `<name>` | 要激活的配置文件名称。若使用 `default`，则恢复为默认配置文件。 |

**示例：**

```bash
hermes profile use work
hermes profile use default
```

## `hermes profile create` 命令

```bash
hermes profile create <name> [options]
```

创建新配置文件。

| 参数/选项 | 描述 |
|----------|------|
| `<name>` | 新配置文件的名称。必须为有效的目录名（包含字母、数字、连字符和下划线）。 |
| `--clone` | 从当前配置文件复制 `config.yaml`、`.env` 和 `SOUL.md` 文件。 |
| `--clone-all` | 从当前配置文件复制所有内容（包括配置、记忆、技能、定时任务及插件），但不包括针对该配置文件的特定历史记录：会话记录、`state.db`、备份文件、状态快照及检查点。 |
| `--clone-from <profile>` | 而非从当前配置文件，从指定配置文件进行克隆。需与 `--clone` 或 `--clone-all` 一起使用。 |
| `--no-alias` | 跳过生成封装脚本的步骤。 |
| `--description "<text>"` | 用一两句话描述该配置文件的用途。Kanban 编排器会利用此描述根据角色而非仅凭配置文件名称来分配任务。可跳过此选项，稍后通过 `hermes profile describe` 添加描述。该描述会保存在 `<profile_dir>/profile.yaml` 中。 |
| `--no-skills` | 创建一个**空**配置文件，不启用任何预置技能。会在配置文件中添加 `.no-bundled-skills` 标记，以防止后续的 `hermes update` 操作重新加载预置技能集。同时该选项不允许与 `--clone` / `--clone-all` 一起使用（因为这些选项会强制复制技能）。适用于功能较为单一的编排器配置文件或不应继承完整技能库的沙箱配置文件。若需在已创建的配置文件（包括默认的 `~/.hermes`）上启用此功能，可使用 `hermes skills opt-out` / `hermes skills opt-in` 命令。 |

创建配置文件并不会将该配置文件所在的目录设置为终端命令的默认项目/工作目录。若希望某个配置文件针对特定项目运行，请在该配置文件的 `config.yaml` 中设置 `terminal.cwd`。

**示例：**

```bash
# Blank profile — needs full setup
hermes profile create mybot

# Clone config only from current profile
hermes profile create work --clone

# Clone everything from current profile
hermes profile create backup --clone-all

# Clone config from a specific profile
hermes profile create work2 --clone --clone-from work
```

## `hermes profile describe` 命令说明

```bash
hermes profile describe [<name>] [options]
```

读取或设置配置文件的描述信息。该描述会被看板协调器用于根据各配置文件的擅长任务类型来分配任务，而无需仅凭文件名进行猜测。描述信息会保存在 `<profile_dir>/profile.yaml` 中，因此可在系统重启后依然保留，并与网关共享。

若不使用任何参数，则会打印当前的描述内容（如果为空，则显示 `(no description set for '<name>')`）。

| 参数/选项 | 描述 |
|----------|------|
| `<name>` | 需要描述的配置文件名称。除非使用了 `--all --auto`，否则该参数为必填项。 |
| `--text "<text>"` | 将描述内容设置为这段精确的文本（由用户输入）。此操作会覆盖原有的描述信息。 |
| `--auto` | 基于配置文件已安装的技能、配置的模型以及文件名，通过辅助大型语言模型自动生成1-2句的描述。可在 `config.yaml` 的 `auxiliary.profile_describer` 中配置相关模型。自动生成的描述会标记为 `description_auto: true`，以便控制台将其标出以供审核。 |
| `--overwrite` | 当与 `--auto` 一起使用时，也会替换用户输入的描述内容（默认情况下，会跳过那些已明确设置描述信息的配置文件）。 |
| `--all` | 当与 `--auto` 一起使用时，会处理所有缺少描述信息的配置文件。 |

**示例：**

```bash
# Read the current description
hermes profile describe researcher

# Set it explicitly
hermes profile describe researcher --text "Reads source code and writes findings."

# Let the LLM generate one
hermes profile describe researcher --auto

# Fill in descriptions for every profile that doesn't have one
hermes profile describe --all --auto
```

## `hermes profile delete` 命令

```bash
hermes profile delete <name> [options]
```

删除某个配置文件，并同时移除其对应的shell别名。

| 参数/选项 | 描述 |
|----------|------|
| `<name>` | 需要删除的配置文件。 |
| `--yes`, `-y` | 跳过确认提示。 |

**示例：**

```bash
hermes profile delete mybot
hermes profile delete mybot --yes
```

:::warning
此操作会永久删除该配置文件的整个目录，其中包括所有的配置项、记忆数据、会话记录以及技能。当前处于激活状态的配置文件无法被删除。
:::

## `hermes profile show`

```bash
hermes profile show <name>
```

显示有关配置文件的详细信息，包括其主目录、已配置的模型、网关状态、技能数量以及配置文件的状态。

此处显示的是该配置文件在Hermes中的主目录，而非终端的工作目录。终端命令的起始路径为 `terminal.cwd`（若设置为 `cwd: "."`，则从本地后端的启动目录开始）。

| 参数 | 描述 |
|------|------|
| `<name>` | 需要检查的配置文件名称。 |

**示例：**

```bash
$ hermes profile show work
Profile: work
Path:    ~/.hermes/profiles/work
Model:   anthropic/claude-sonnet-4 (anthropic)
Gateway: stopped
Skills:  12
.env:    exists
SOUL.md: exists
Alias:   ~/.local/bin/work
```

## `hermes profile alias` 命令

```bash
hermes profile alias <name> [options]
```

会在 `~/.local/bin/<name>` 目录下重新生成Shell别名脚本。当别名被意外删除，或需要在更换Hermes安装位置后进行更新时，该功能非常有用。

| 参数/选项 | 描述 |
|----------|------|
| `<name>` | 需要为其创建/更新别名的配置文件。 |
| `--remove` | 不创建脚本，而是直接删除现有的包装脚本。 |
| `--name <alias>` | 自定义别名名称（默认为配置文件名称）。 |

**示例：**

```bash
hermes profile alias work
# Creates/updates ~/.local/bin/work

hermes profile alias work --name mywork
# Creates ~/.local/bin/mywork

hermes profile alias work --remove
# Removes the wrapper script
```

## `hermes profile rename` 命令

```bash
hermes profile rename <old-name> <new-name>
```

重命名配置文件，并同步更新目录路径及 Shell 别名。

| 参数 | 说明 |
|------|------|
| `<old-name>` | 当前配置文件名称。 |
| `<new-name>` | 新的配置文件名称。 |

**示例：**

```bash
hermes profile rename mybot assistant
# ~/.hermes/profiles/mybot → ~/.hermes/profiles/assistant
# ~/.local/bin/mybot → ~/.local/bin/assistant
```

## `hermes profile export` 命令

```bash
hermes profile export <name> [options]
```

将配置文件导出为压缩后的 tar.gz 形式。

| 参数 / 选项 | 描述 |
|-------------------|-------------|
| `<name>` | 需要导出的配置文件。 |
| `-o`, `--output <path>` | 输出文件路径（默认值：<name>.tar.gz）。 |

**示例：**

```bash
hermes profile export work
# Creates work.tar.gz in the current directory

hermes profile export work -o ./work-2026-03-29.tar.gz
```

## `hermes profile import` 命令

```bash
hermes profile import <archive> [options]
```

从 tar.gz 压缩包中导入配置文件。

| 参数/选项 | 描述 |
|----------|------|
| `<archive>` | 需要导入的 tar.gz 压缩包路径。 |
| `--name <name>` | 导入配置文件的名称（默认：根据压缩包名称自动推断）。 |

**示例：**

```bash
hermes profile import ./work-2026-03-29.tar.gz
# Infers profile name from the archive

hermes profile import ./work-2026-03-29.tar.gz --name work-restored
```

## 发布命令

:::tip
**初次使用发布功能？**请先阅读[Profile Distributions用户指南](../user-guide/profile-distributions.md)——该指南通过大量实例详细说明了其用途、适用场景及操作方法。如果您已经明确需求，可参考下方的CLI参考文档。
:::

发布功能可将配置文件转换为可共享、带版本控制的对象，并以**git仓库**的形式进行发布。接收方只需执行一条命令即可安装该配置文件，之后还可直接进行更新，而无需修改本地存储的数据、会话信息或认证凭证。

`auth.json`和`.env`文件永远不会被包含在发布内容中——它们始终保留在安装用户的机器上。

从首次安装到后续更新，接收方的用户数据（包括会话信息、认证状态以及其对`.env`文件所做的自定义修改）都会被完整保留。

:::info
对于在本地对配置文件进行**备份和恢复**操作，仍应使用`hermes profile export`/`import`命令。而发布功能（`install`/`update`/`info`）则是另一个概念：它通过git传输配置文件，以便他人能够安装使用。
:::

### `hermes profile install`

```bash
hermes profile install <source> [--name <name>] [--alias] [--force] [--yes]
```

从 Git URL 或本地目录安装配置文件分发包。

| 选项 | 描述 |
|------|-------------|
| `<source>` | Git URL（如 `github.com/user/repo`、`https://...`、`git@...`、`ssh://`、`git://`）或包含位于根目录下的 `distribution.yaml` 文件的本地目录。 |
| `--name NAME` | 覆盖清单中指定的配置文件名称。 |
| `--alias` | 同时创建一个 shell 包装命令（例如将 `telemetry` 替换为 `hermes -p telemetry`）。 |
| `--force` | 覆盖已存在的同名配置文件。用户数据仍会被保留。 |
| `-y`, `--yes` | 跳过清单预览确认提示。 |

安装程序会先显示清单、列出所需的环境变量，并在请求确认前对定时任务发出警告。这些所需的环境变量会保存在 `.env.EXAMPLE` 文件中，您只需将其复制为 `.env` 并填写相应内容即可。

**示例：**

```bash
# Install from a GitHub repo (shorthand)
hermes profile install github.com/kyle/telemetry-distribution --alias

# Install from a full HTTPS git URL
hermes profile install https://github.com/kyle/telemetry-distribution.git

# Install from SSH
hermes profile install git@github.com:kyle/telemetry-distribution.git

# Install from a local directory during development
hermes profile install ./telemetry/
```

### `hermes profile update` —— 更新 Hermes 配置文件

```bash
hermes profile update <name> [--force-config] [--yes]
```

从记录的源地址重新克隆该发行版并应用更新。发行版自带的文件（如 SOUL.md、skills/、cron/、mcp.json）将被覆盖；而用户数据（如记忆内容、会话信息、认证信息及 .env 文件）则完全不会被改动。

为保留您自定义的配置设置，系统会默认保留 `config.yaml` 文件。若需将其重置为发行版自带的默认配置，可使用 `--force-config` 参数。

### `hermes profile info`

```bash
hermes profile info <name>
```

该命令会输出配置文件的分布信息清单——包括名称、版本、所需的Hermes版本、创建者、环境变量要求、源URL/路径，以及该配置文件上次被“安装”或“更新”时的`Installed:`时间戳。这些信息有助于在安装共享配置文件之前了解其所需条件，同时也能帮助发现“该配置文件已安装6个月且尚未更新”的情况。

`hermes profile list`命令会在“Distribution”列中显示分布名称和版本；而`hermes profile show <name>` / `delete <name>`命令则会展示源URL，从而让你一目了然地分辨出哪些配置文件来自Git仓库，哪些是本地创建的。

### 私有分布

私有Git仓库可直接作为分布源，无需额外配置——安装过程会直接调用你系统中的常规`git`命令行工具，因此你的Shell已设置的任何认证方式（如SSH密钥、`git credential`辅助工具、GitHub CLI存储的HTTPS凭证）都会被自动应用。

```bash
# Uses your SSH key, the same as any other `git clone`
hermes profile install git@github.com:your-org/internal-assistant.git

# Uses your git credential helper
hermes profile install https://github.com/your-org/internal-assistant.git
```

如果在安装过程中，克隆命令会在终端中交互式地请求凭据，那么这些请求将会被直接传递。请先按照通常使用 `git clone` 克隆同一仓库的方式配置好认证信息，然后再进行安装。

### 发行版清单文件（`distribution.yaml`）

每个发行版的仓库根目录下都存在一个 `distribution.yaml` 文件：

```yaml
name: telemetry
version: 0.1.0
description: "Compliance monitoring harness"
hermes_requires: ">=0.12.0"
author: "Your Name"
license: "MIT"
env_requires:
  - name: OPENAI_API_KEY
    description: "OpenAI API key"
    required: true
  - name: GRAPHITI_MCP_URL
    description: "Memory graph URL"
    required: false
    default: "http://127.0.0.1:8000/sse"
distribution_owned:   # optional; defaults to SOUL.md, config.yaml,
                      #   mcp.json, skills/, cron/, distribution.yaml
  - SOUL.md
  - skills/compliance/
  - cron/
```

`hermes_requires` 支持使用 `>=`、`<=`、`==`、`!=`、`>`、`<` 或直接指定版本号（视为 `>=`）。如果当前 Hermes 版本不满足要求，安装将会报出明确的错误信息。

`distribution_owned` 为可选参数。若设置该参数，则仅在更新时替换指定的路径，配置文件中的其他内容仍保持用户所有。若未设置，则适用上述默认规则。

### 发布版本包

创建版本包的操作其实只需执行一次 git push 即可：

1. 在您的配置目录中创建 `distribution.yaml` 文件，至少需包含 `name` 和 `version` 两项内容。
2. 初始化一个 git 仓库（或使用现有仓库），然后将其推送到 GitHub、GitLab 或任何 Hermes 能够克隆的地址。
3. 告知接收者运行 `hermes profile install <您的仓库地址>` 即可。

建议使用 git 标签来管理不同版本的发布——克隆 `HEAD` 的接收者将获得最新版本，而您也可以随时在配置文件中提升 `version:` 的数值。

## `hermes -p` / `hermes --profile`

```bash
hermes -p <name> <command> [options]
hermes --profile <name> <command> [options]
```

这是一个全局标志，用于在无需更改默认设置的情况下，以特定配置文件运行任何 Hermes 命令。在该命令执行期间，它会覆盖当前激活的配置文件。

| 选项 | 描述 |
|------|------|
| `-p <name>`, `--profile <name>` | 用于该命令的配置文件名称。 |

**示例：**

```bash
hermes -p work chat -q "Check the server status"
hermes --profile dev gateway start
hermes -p personal skills list
hermes -p work config edit
```

## `hermes completion` 功能

```bash
hermes completion <shell>
```

生成Shell自动补全脚本，包括对配置文件名称及配置文件子命令的补全功能。

| 参数 | 描述 |
|--------|------|
| `<shell>` | 需要生成补全功能的Shell类型：`bash`、`zsh` 或 `fish`。 |

**示例：**

```bash
# Install completions
hermes completion bash >> ~/.bashrc
hermes completion zsh >> ~/.zshrc
hermes completion fish > ~/.config/fish/completions/hermes.fish

# Reload shell
source ~/.bashrc
```

安装完成后，制表补全功能将适用于以下场景：
- `hermes profile <TAB>` — 子命令（list、use、create 等）
- `hermes profile use <TAB>` — 配置文件名称
- `hermes -p <TAB>` — 配置文件名称

## 参考资料

- [配置文件用户指南](../user-guide/profiles.md)
- [CLI 命令参考手册](./cli-commands.md)
- [常见问题解答 — 配置文件部分](./faq.md#profiles)
