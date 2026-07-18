---
sidebar_position: 15
title: "Web Dashboard"
description: "Browser-based administration panel for managing configuration, API keys, MCP servers, messaging pairing, webhooks, the gateway, memory, credentials, sessions, logs, analytics, cron jobs, and skills"
---

# Web控制面板

Web控制面板是一种基于浏览器的用户界面，用于管理您的Hermes Agent安装。您无需编辑YAML文件或运行CLI命令，即可通过简洁的网页界面来配置设置、管理API密钥以及监控会话。

:::提示
托管模式下的身份验证采用Nous Portal OAuth机制；如果您希望控制面板能够与真正的后端系统交互，可使用`hermes setup --portal`命令同时连接模型网关和工具网关。详情请参阅[Nous Portal](/integrations/nous-portal)。
:::

## 快速入门

```bash
hermes dashboard
```

该命令会启动一个本地 Web 服务器，并在您的浏览器中打开 `http://127.0.0.1:9119`。控制面板完全在您的设备上运行，没有任何数据会离开本机。

### 参数选项

| 参数 | 默认值 | 描述 |
|------|---------|-------------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--insecure` | 关闭 | 允许绑定到非本机地址的主机（**非常危险**——会导致 API 密钥在网络中暴露；建议配合防火墙和强身份验证机制使用） |
| `--isolated` | 关闭 | 当从指定配置文件（如“工作节点控制面板”）启动时，为该配置文件单独运行服务器，而非指向主机的控制面板 |

```bash
# Custom port
hermes dashboard --port 8080

# Bind to all interfaces (use with caution on shared networks)
hermes dashboard --host 0.0.0.0

# Start without opening browser
hermes dashboard --no-open
```

## 管理多个配置文件

控制面板属于**机器级**管理界面：每台服务器会管理该机器上的所有[配置文件](../profiles.md)。当存在多个配置文件时，侧边栏中会出现一个配置文件切换器，用于决定管理页面读取和写入的数据所属的配置文件——配置、API密钥、技能、MCP、模型以及聊天标签页都会遵循这一设置。当选择的是控制面板自身以外的配置文件时，会有一条琥珀色横幅显示当前管理的配置文件名称，从而确保写入目标始终清晰明确。

配置文件的选择信息会体现在URL中（`?profile=<name>`），因此像`http://127.0.0.1:9119/skills?profile=worker`这样的深度链接在访问时就会自动预设好切换器选项，且刷新页面后设置也不会丢失。

从配置文件别名启动控制面板时，系统会直接跳转到该机器的控制面板，而不会启动额外的服务器。

```bash
worker dashboard
# → already running: opens the browser at ?profile=worker
# → not running:     starts the machine dashboard with "worker" preselected
```

如需取消该功能并运行针对特定配置文件专用的服务器，可传递 `--isolated` 参数（即采用统一前的运行方式——当您需要为不同配置文件提供具有独立认证机制的仪表板时，此方式十分有用）。

**Chat** 标签页也会随配置文件切换而改变：基于所选配置文件的 `HERMES_HOME` 路径，该标签页会启动对应的伪终端子进程，因此对话将使用该配置文件对应的模型、技能、内存及会话历史记录进行。更换配置文件则会启动全新的终端会话。

那些属于特定配置文件且不会被切换机制影响的组件包括：网关进程（可通过 `hermes -p <name> gateway …` 命令进行管理）、每个配置文件独立的会话数据库，以及定时任务调度器（Cron 页面已通过自身过滤功能实现了跨配置文件的汇总显示）。

## 先决条件

默认安装的 `hermes-agent` 并未包含 HTTP 库及伪终端辅助工具——这些都属于可选扩展组件。**Web 仪表板**需要 FastAPI 和 Uvicorn（属于 “web” 类扩展）。**Chat** 标签页还需要 `ptyprocess` 库来在伪终端后启动嵌入式 TUI 界面（在 POSIX 系统上属于 “pty” 类扩展）。可通过以下命令安装这两项组件：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[web,pty]"
```

`web` 这一附加组件会引入 FastAPI/Uvicorn；而 `pty` 组件则会引入 `ptyprocess`（用于 POSIX 环境）或 `pywinpty`（用于原生 Windows 环境——请注意，内置的 TUI 本身仍需依赖 WSL）。执行命令 `cd ~/.hermes/hermes-agent && uv pip install -e ".[all]"` 可同时安装这两种附加组件，若您还需要消息传递、语音功能等，这是最简便的方法。

如果在运行 `hermes dashboard` 时缺少相关依赖，系统会提示您需要安装哪些组件。如果前端尚未构建且系统中存在 `npm`，则首次启动时会自动进行构建。

“聊天”标签页在每次启动 `hermes dashboard` 时都会出现——内置的浏览器聊天面板（通过 PTY/WebSocket 运行 TUI）始终可用，无需任何额外参数。

## 页面

### 状态

首页会实时展示您的安装情况：

- **Agent 版本**及发布日期
- **网关状态**——运行中/已停止、PID 值、已连接的平台及其状态
- **活跃会话数**——过去 5 分钟内处于活跃状态的会话数量
- **最近会话**——最近 20 个会话的列表，显示所用模型、消息数量、Token 使用情况以及对话预览内容

状态页面每 5 秒自动刷新一次。

### 聊天

“聊天”标签页会将完整的 Hermes TUI（与执行 `hermes --tui` 时所看到的界面相同）直接嵌入浏览器中。在终端 TUI 中能实现的所有功能——斜杠命令、模型选择器、工具调用卡片、Markdown 流式显示、澄清/授权/批准提示、主题定制等——在这里都能正常使用，因为仪表板实际上是在运行真正的 TUI 可执行文件，并通过 [xterm.js](https://xtermjs.org/) 及其 WebGL 渲染器来呈现 ANSI 输出，从而实现完美对齐的单元格布局。

**工作原理如下：**

- `/api/pty` 会打开一个通过仪表板会话令牌进行身份验证的 WebSocket 连接
- 服务器会在 POSIX 伪终端背后启动 `hermes --tui`
- 按键输入会被发送到伪终端，而 ANSI 输出则会流回浏览器
- xterm.js 的 WebGL 渲染器会将每个单元格绘制到整数像素网格上；鼠标跟踪（SGR 1006 标准）、宽字符（Unicode 11）以及绘图符号都能得到原生支持
- 调整浏览器窗口大小时，会通过 `@xterm/addon-fit` 插件相应地调整 TUI 的大小

**恢复现有会话：** 在“会话”标签页中，点击任意会话旁边的播放图标（▶）。该操作会生成 `/chat?resume=<id>` 的链接，并以 `--resume` 参数启动 TUI，从而加载完整的对话历史记录。

**会话切换器（右侧栏）：** “聊天”标签页在终端旁有一个细长的右侧栏，其中包含类似 ChatGPT 风格的对话列表，让您无需离开页面即可切换不同对话。该栏将模型选择器置于顶部，会话列表紧随其下；终端则占据屏幕的大部分空间。列表显示当前活跃配置文件最近的会话信息——包括标题（若无法显示则显示对话预览）、上次活跃时间、消息数量，以及非 CLI 会话的来源渠道。点击任意一行即可在该位置恢复该会话（终端会重新加载该对话的历史记录），当前活跃的会话会被高亮显示。**新建聊天**则会启动一个全新的会话，同时刷新控件会重新加载会话列表。该右侧栏仅用于切换会话——删除、重命名、导出及批量清理操作仍需在“会话”标签页中进行。在屏幕较窄的情况下，该栏会折叠为滑出式面板。

**前置条件：**

- Node.js（与 `hermes --tui` 的要求相同；TUI 包会在首次启动时自动构建）
- `ptyprocess`——由 `pty` 附加组件自动安装（执行命令 `cd ~/.hermes/hermes-agent && uv pip install -e ".[web,pty]"`，或使用 `[all]` 即可同时安装两者）
- POSIX 内核（Linux、macOS 或 WSL2）。/chat 终端面板特别需要 POSIX 伪终端——原生 Windows 版 Python 没有对应的机制，因此在原生 Windows 环境下，虽然仪表板的其他功能（如会话、任务、指标、配置编辑器）仍可正常使用，但 /chat 标签页会显示提示，建议使用 WSL2 才能使用该功能。

关闭浏览器标签页后，服务器端的伪终端会被及时释放。重新打开浏览器则会启动一个全新的会话。

若想让 [Hermes Desktop](#connecting-hermes-desktop-to-a-remote-backend) 连接到另一台机器上运行的仪表板，而非其自带的本地后端，请参阅下文的远程后端相关内容。

### 将 Hermes Desktop 连接到远程后端

Hermes Desktop 通常会启动自己的本地后端，但也可以通过 **设置 → 网关 → 远程网关** 的方式连接到运行在远程机器（如虚拟机、家庭实验室设备等）上的仪表板。这也是出现“桌面端显示后端已准备就绪，但聊天功能无法使用”这类问题的常见原因，因为桌面端的就绪检查所验证的内容，远少于实际实时聊天连接所需的条件。

:::info 前置条件：远程主机上必须正在运行 `hermes dashboard`
桌面端所连接的“远程后端”实际上就是运行在远程机器上的 `hermes dashboard` 进程——也就是本文档所介绍的同一台服务器。在执行以下任何操作之前，该服务器都必须处于运行状态且可访问；桌面端仅会连接到该服务器，而不会替您启动它。建议通过 `systemd`/`tmux` 等工具保持该进程持续运行，这样即使用户退出登录或重启电脑，该进程也不会中断。而 **网关**（Telegram/Discord/Slack 等）则是另一个独立的长期运行的进程——如果您依赖消息通道功能，需要单独启动它；桌面端应用并不会连接到网关。
:::

桌面端的“远程后端已准备就绪”检测仅会访问 `GET /api/status` 这一公开接口——只要主机上运行有任何仪表板，该接口就会立即响应。而实时聊天连接则是通过另一个独立的 WebSocket 连接到 `/api/ws`（以及 `/api/pty`）接口，这个 Socket 连接还需通过另外两项检查才能建立，而这些检查是状态检测所不会涉及的：

1. **必须完成身份验证。** 当仪表板绑定到非回环地址时，会启用其身份验证机制。建议使用用户名和密码进行保护（可使用内置的 [用户名/密码提供器](#usernamepassword-provider-no-oauth-idp)）；桌面端会登录一次，然后通过一次性令牌为 WebSocket 连接复用该会话。如果未配置相应的提供器，非回环地址的仪表板在启动时就会直接失败。
2. **绑定主机必须允许客户端连接，并且 Host 头部信息必须匹配。** 回环绑定（`127.0.0.1`）仅接受回环地址的客户端，因此无论凭据如何，远程机器在 Socket 层就会被拒绝接入。建议将仪表板绑定到非回环地址（`--host 0.0.0.0`），这样对方 IP 校验机制才会允许远程客户端通过。在桌面端输入的远程 URL 必须能够通过仪表板绑定的同一主机访问——DNS 重定向校验要求 Host 头部信息必须一致。

#### 远程仪表板设置

请设置用户名和密码，然后让仪表板绑定到可访问的地址上运行。如果是通过 `systemd` 服务来运行仪表板：

```ini
[Service]
EnvironmentFile=%h/.hermes/.env
ExecStart=/path/to/venv/bin/python -m hermes_cli.main dashboard \
    --host 0.0.0.0 --port 9119 --no-open
```

其中 `~/.hermes/.env` 文件包含：

```bash
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
HERMES_DASHBOARD_BASIC_AUTH_SECRET=<32+ random bytes; openssl rand -base64 32>
```

接着在桌面端输入**远程地址**（例如 `http://VM_IP:9119`），并使用该用户名和密码进行**登录**。有关完整的配置选项，请参阅[用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp)部分。

:::提示 重新尝试使用桌面端之前请先确认网关已启动
在任何机器上，检查控制面板是否显示了用户名/密码提供程序：

```bash
curl -s http://VM_IP:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["basic"]
```

- 当 `auth_required: true` 且 providers 列表中包含 `"basic"` 时，桌面端的**登录**流程即可正常使用。  
- 当 `auth_required: false` 时，说明绑定地址为回环地址，或网关未启动。请绑定非回环地址。  
- 当 `auth_required: true` 但 providers 列表中不存在 `"basic"` 时，表示用户名/密码环境变量未被加载。请先修复该问题。  
:::

如果 `/api/status` 显示网关已通过 `"basic"` 提供商启动，且桌面端在登录后仍无法连接，则问题已超出基础配置范畴——请获取最新的 `desktop.log` 文件（路径：设置 → 网关 → 打开日志），以及同一重试时段内的控制台日志，查找 `/api/ws` 的关闭码（4403 表示聊天 WS 被请求守卫拒绝，例如主机/对端不匹配；4401 表示 WS 令牌未通过身份验证）。

### 配置

提供一个基于表单的编辑器用于编辑 `config.yaml` 文件。所有 150 多个配置字段都会从 `DEFAULT_CONFIG` 中自动检测出来，并按标签页分类展示：

![配置管理页面——左侧为筛选区域，右侧为自动检测到的字段](/img/dashboard/admin-config.png)

- **模型** — 默认模型、提供商、基础 URL 以及推理设置  
- **终端** — 后端类型（本地/ Docker/ SSH/ 模态）、超时时间以及 shell 偏好设置  
- **显示** — 主题皮肤、工具进度显示、继续处理提示以及旋转加载器设置  
- **智能体** — 最大迭代次数、网关超时时间以及服务等级  
- **委托** — 子智能体数量限制以及推理耗时设置  
- **内存** — 提供商选择以及上下文注入设置  
- **审批** — 危险命令的审批模式（智能/手动/关闭）  
- 其他更多内容——`config.yaml` 的每个部分都对应有相应的表单字段  

那些具有已知有效值的字段（如终端后端类型、主题皮肤、审批模式等）会以下拉菜单形式呈现；布尔值则显示为切换按钮；其余字段均为文本输入框。  

**操作按钮：**  
- **保存** — 立即将更改写入 `config.yaml` 文件  
- **重置为默认值** — 将所有字段恢复为默认值（需点击“保存”才会真正生效）  
- **导出** — 以 JSON 格式下载当前配置  
- **导入** — 上传 JSON 配置文件以替换现有设置  

:::提示  
配置更改将在下一次智能体会话或网关重启时生效。网页控制台编辑的正是与 `hermes config set` 命令以及网关读取的同一个 `config.yaml` 文件。  
:::

### API 密钥

用于管理存储 API 密钥和凭证的 `.env` 文件。这些密钥按类别分组：  

- **大语言模型提供商** — OpenRouter、Anthropic、OpenAI、DeepSeek 等  
- **工具 API 密钥** — Browserbase、Firecrawl、Tavily、ElevenLabs 等  
- **消息平台** — Telegram、Discord、Slack 机器人令牌等  
- **智能体设置** — 非敏感的环境变量，如 `API_SERVER_ENABLED`  

每项密钥都会显示：  
- 当前是否已设置（显示经过脱敏处理的值预览）  
- 该密钥的用途说明  
- 对应提供商的注册/密钥页面链接  
- 用于设置或更新值的输入框  
- 用于删除该密钥的按钮  

高级或极少使用的密钥默认会通过一个切换按钮隐藏起来。  

### 会话

可浏览并查看所有智能体会话。每行信息会显示会话名称、来源平台图标（CLI、Telegram、Discord、Slack、cron）、模型名称、消息数量、工具调用次数，以及该会话最后活跃的时间。正在运行的会话会用一个闪烁的徽章标示出来。  

- **搜索** — 使用 FTS5 对所有消息内容进行全文搜索。搜索结果会高亮显示相关片段，展开后页面会自动滚动到第一条匹配的消息。  
- **统计信息** — 统计栏会显示总会话数、当前处于活跃状态的会话数、已归档的会话数、总消息数，以及按来源分类的详细数据。  
- **展开查看** — 点击某次会话即可查看其完整的消息历史记录。消息会根据发送方角色（用户、助手、系统、工具）以不同颜色显示，并以带语法高亮的 Markdown 格式呈现。  
- **工具调用** — 包含工具调用的助手消息会以可折叠的块形式展示，其中包含函数名称及 JSON 参数。  
- **重命名** — 可在线修改或清除会话名称（使用铅笔图标）。  
- **导出** — 以 JSON 格式下载会话信息（包括元数据及完整消息历史）（使用下载图标）。  
- **清理旧会话** — “清理旧会话”按钮可用于删除超过 N 天未使用的已结束会话。  
- **删除** — 使用垃圾桶图标可移除某次会话及其所有消息历史记录。  

![会话管理页面——统计栏、清理功能，以及每行对应的重命名/导出/删除按钮](/img/dashboard/admin-sessions.png)

### 日志

可查看智能体、网关及错误日志文件，并支持过滤和实时滚动查看最新日志内容。  

- **文件类型** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换  
- **日志级别** — 按日志级别进行过滤：全部、调试、信息、警告或错误  
- **组件来源** — 按日志来源组件进行过滤：全部、网关、智能体、工具、CLI 或 cron  
- **显示行数** — 选择要显示的行数（50、100、200 或 500 行）  
- **自动刷新** — 开启/关闭实时滚动功能，系统会每 5 秒检查一次是否有新日志内容  
- **颜色编码** — 日志行会根据严重程度用不同颜色标注（错误为红色，警告为黄色，调试信息为浅色）  

### 分析统计

基于会话历史数据计算的使用量和成本分析结果。可选择时间范围（7 天、30 天或 90 天），查看以下内容：  

- **摘要卡片** — 总 token 数量（输入/输出）、缓存命中率、预估或实际总成本，以及每日平均会话数  
- **每日 token 使用情况图表** — 采用堆叠柱状图展示每日输入和输出 token 的使用情况，鼠标悬停时可查看详细分类及对应成本  
- **每日明细表** — 显示每天的日期、会话数、输入 token 数、输出 token 数、缓存命中率以及成本  
- **按模型分类的明细表** — 以表格形式展示所使用的每个模型、其对应的会话数、token 使用量及预估成本  

### 定时任务

可用于创建和管理定时运行的 cron 作业，从而按固定时间间隔执行智能体提示任务。  

- **创建** — 填写作业名称（可选）、提示内容、cron 表达式（例如 `0 9 * * *`），以及消息发送目标（本地、Telegram、Discord、Slack 或电子邮件）  
- **作业列表** — 每个作业都会显示其名称、提示内容预览、调度表达式、状态徽章（已启用/暂停/出错）、发送目标、上次运行时间以及下次运行时间  
- **暂停/继续** — 在已启用和已暂停状态之间切换作业  
- **编辑** — 打开预填好的模态框，用于修改作业的提示内容、调度时间、名称或发送目标  
- **立即触发** — 在非预定时间立即执行该作业  
- **删除** — 永久移除某个 cron 作业  

### 配置文件

可用于创建和管理[配置文件](../profiles.md)——这些独立的 Hermes 实例拥有各自的配置、技能和会话。  

- **配置文件卡片** — 每张卡片都会显示该配置文件的模型/提供商、技能数量、网关状态、描述以及相关徽章（活跃、默认、别名）  
- **创建** — 需要输入文件名称，可选择是否从默认配置克隆、是否复制所有内容、是否不包含任何预装技能，还需填写描述和模型信息；专门的配置文件创建页面（`/profiles/new`）会提供完整的配置流程（包括模型、MCP 服务及技能的设置）  
- **管理技能与工具** — 可跳转到针对该配置文件的技能管理页面（会自动切换侧边栏中的配置文件选择器）  
- **设为默认** — 可更改默认的固定配置，使得**后续的 CLI/网关运行**都使用该配置文件（功能与 `hermes profile use` 相同）。此操作不会改变控制台管理的默认配置——那是配置文件选择器的职责  
- **编辑模型/描述/SOUL** — 提供内联编辑器，可直接修改该配置文件的对应内容  
- **重命名/删除** — 仅适用于已命名的配置文件  

### 技能

可浏览、搜索及切换已安装的技能和工具集，同时还可以从技能中心安装新技能。这些技能均存储在 `~/.hermes/skills/` 目录下，并按类别分组展示。  

- **搜索** — 可通过名称、描述或类别来筛选已安装的技能和工具集  
- **类别筛选** — 点击类别标签可缩小列表范围（例如 MLOps、MCP、红队测试、AI 等）  
- **开关控制** — 通过切换按钮启用或禁用单个技能，更改会在下一次会话时生效  
- **工具集** — 另一个视图会展示内置的工具集（如文件操作、网页浏览等），并显示它们的启用/禁用状态、设置要求以及所含工具列表  
- **浏览技能中心** — 第三个视图可在所有来源中搜索技能中心的内容（功能与 `hermes skills search` 相同），可通过标识符直接安装任意找到的技能，并实时显示安装日志；同时还提供“更新全部”按钮，用于刷新已安装的技能。  

![技能管理页面——浏览技能中心视图：搜索、安装及更新功能](/img/dashboard/admin-skills-hub.png)

### MCP

无需使用 CLI 即可管理[MCP](/integrations/mcp)服务器。相关配置与 `hermes mcp` 命令所读取的 `config.yaml` 文件中的 `mcp_servers` 块内容一致。  

**您的 MCP 服务器：**  
- **添加** — 可注册 HTTP/SSE 服务器（提供 URL）或标准输入/输出服务器（提供命令及参数），对于标准输入/输出服务器，还可选择性地设置 `KEY=VALUE` 格式的环境变量  
- **启用/禁用** — 可在不删除服务器的情况下切换其启用状态。已禁用的服务器仍会保留在配置文件中，方便日后重新启用；更改会在下一次网关重启时生效  
- **测试** — 可连接到服务器，列出其提供的工具，然后断开连接——这样可以在智能体实际依赖该服务器之前验证连接是否正常  
- **删除** — 从配置文件中移除某个服务器  
- 在列表视图中，包含敏感信息的环境变量值会被进行脱敏处理  

**目录列表**：可浏览 Nous 审核通过的 MCP 服务器列表（即预装的 `optional-mcps/` 目录中的内容），并一键安装任意需要的服务器。那些需要 API 密钥的服务器会在界面中直接提示用户输入密钥，输入后的值会被保存到 `.env` 文件中。此目录与 `hermes mcp catalog` 命令及 `hermes mcp install` 命令使用的目录相同。  

![MCP 管理页面——显示您的服务器及其启用/禁用开关，以及安装目录列表](/img/dashboard/admin-mcp.png)

### Webhook

用于管理动态[Webhook 订阅](/user-guide/messaging/webhooks)功能。首先必须在消息设置中开启 Webhook 功能，否则页面会给出相应提示。  

- **创建** — 需要输入名称、描述、事件筛选条件、消息发送目标，可选择是否启用直接发送模式，还需输入智能体提示内容。创建完成后，页面会显示对应的路由 URL 以及一次性使用的 HMAC 密钥，方便用户复制  
- **启用/禁用** — 可切换订阅状态的开启或关闭。已禁用的路由虽然仍保留在订阅文件中，但网关会拒绝接收来自这些路由的请求（返回 403 错误）。网关会自动热加载配置文件，因此更改会在下一个事件到达时生效——无需重启网关  
- **列表** — 每个订阅项都会显示其 URL、支持的事件类型以及消息发送目标  
- **删除** — 可移除某个订阅项  

![Webhook 管理页面——显示各订阅项及其启用/禁用开关](/img/dashboard/admin-webhooks.png)

### 配对

无需使用 CLI 即可批准或撤销用户的消息发送权限——远程管理员可通过此功能将 Telegram/Discord 等平台的用户添加到已配对的网关中。该功能与 `hermes pairing` 完全兼容。  

- **待处理请求** — 每条记录都会显示平台名称、配对码、用户信息以及配对时长，旁边还有“批准”按钮  
- **已批准用户** — 每条记录会显示平台名称和用户信息，旁边有“撤销”按钮  
- **清除待处理请求** — 可一次性删除所有尚未处理的配对请求  

![配对管理页面](/img/dashboard/admin-pairing.png)

### 频道可通过浏览器将 Hermes 连接到任何消息平台——其功能与 `hermes setup gateway` 完全一致。该页面列出了所有受支持的通道（Telegram、Discord、Slack、Matrix、Mattermost、WhatsApp、Signal、BlueBubbles/iMessage、电子邮件、SMS/Twilio、钉钉、飞书/Lark、企业微信、微信、QQ Bot、元宝），并显示它们的实时连接状态。

- **配置**——打开针对特定平台的表单，其中仅包含该通道所需的字段（机器人令牌、应用令牌、服务器地址、允许列表等）。敏感信息会以密码输入框的形式呈现并经过脱敏处理；若留空某个字段，则保留其当前值。必填字段会被标记并经过验证。“设置指南”链接可指向对应平台的凭证文档。
- **启用/禁用**——切换通道的开启或关闭状态。凭证仍保存在磁盘中，仅活跃状态会发生变化。
- **测试**——检查该通道是否已正确配置、处于启用状态，以及是否能从网关获取实时连接信息。
- **重启网关**——凭证会被写入 `~/.hermes/.env` 文件，而启用状态则存储在 `config.yaml` 中；下次网关重启时会自动连接所有已启用的通道，您可直接在页面上触发重启操作。

![通道管理页面——显示各消息平台的状态、启用切换按钮以及针对每个平台的配置表单](/img/dashboard/admin-channels.png)

### 系统

用于管理整个系统运行的统一控制面板：

- **主机信息**——实时系统统计信息：操作系统/内核版本、架构类型、主机名、Python 与 Hermes 版本、CPU 核心数及使用率、内存使用情况、Hermes 安装目录的磁盘使用情况、系统运行时间以及负载平均值。（若安装了 `psutil`，则 CPU/内存/磁盘数据来自该工具；身份相关字段始终会显示。）Hermes 版本会显示**更新状态标签**（已更新/落后 N 个提交）以及**检查更新**按钮。当通过 git 或 pip 安装有可用更新时，“立即更新”按钮会先弹出确认对话框，告知您将拉取多少个提交，随后在后台执行 `hermes update` 命令。对于通过 Docker/Nix/Homebrew 安装的版本，控制面板无法直接进行就地更新，因此会显示相应的离线更新命令。
- **Nous Portal**——显示登录状态、当前使用的推理服务提供商，以及工具网关的路由表（说明哪些工具是通过 Portal 运行，哪些是在本地运行），同时提供管理订阅的链接。该页面为 `hermes portal` 的只读镜像。
- **技能管理器**——显示后台技能维护状态（运行中/暂停中、间隔时间、上次运行时间），并提供暂停/继续操作以及立即运行按钮。该功能与 `hermes curator` 相对应。
- **网关**——用于启动、停止和重启消息网关，同时显示实时状态（运行中/已停止、进程 ID、当前状态）。
- **内存管理**——可选择外部内存服务提供商（或仅使用内置内存），并重置内置的 `MEMORY.md` / `USER.md` 存储文件。
- **凭证池**——可添加或删除供代理轮询使用的 API 密钥（按服务提供商分类）。列表中的密钥会经过脱敏处理，原始密钥仅会传递给代理。
- **操作管理**——可运行 `doctor` 工具进行安全审计、创建备份、从备份文件恢复、更新技能、查看系统提示词的大小分布、生成支持信息转储文件，或迁移已废弃设置的配置。每个操作都会在后台启动相应任务，其实时日志会显示在页面上。
- **检查点**——查看 `/rollback` 阴影存储空间的大小，并可对其进行清理。
- **Shell 钩子**——列出已配置的钩子及其同意状态和可执行状态，可**创建**新的钩子（需指定事件、命令、匹配规则、超时时间，并需要用户同意），也可删除现有钩子。由于钩子可以运行任意命令，因此创建钩子的表单会显示安全警告，且钩子只有在获得用户同意后才会触发。

![系统管理页面——主机信息与 Nous Portal 状态](/img/dashboard/admin-system-top.png)

![系统管理页面——技能管理器、网关、内存管理及凭证池](/img/dashboard/admin-system-curator.png)

![系统管理页面——操作管理、检查点及 Shell 钩子](/img/dashboard/admin-system-ops.png)

创建 Shell 钩子时（请注意同意复选框和“可运行任意命令”的警告提示）：

![新建 Shell 钩子对话框](/img/dashboard/admin-hook-create.png)

:::warning 安全提示
Web 控制面板会读取和写入包含 API 密钥及敏感信息的 `.env` 文件。它默认绑定在 `127.0.0.1` 地址上，仅能从本地机器访问。如果将其绑定到 `0.0.0.0`，则网络中的任何用户都可能查看和修改您的凭证。此外，该控制面板本身没有独立的身份验证机制。
:::

## `/reload` 命令

该控制面板的更新还为交互式 CLI 添加了 `/reload` 命令。通过 Web 控制面板更改 API 密钥（或直接编辑 `.env` 文件）后，可在正在运行的 CLI 会话中使用 `/reload` 命令来应用这些更改，而无需重启系统：

```
You → /reload
  Reloaded .env (3 var(s) updated)
```

该功能会将`~/.hermes/.env`中的配置重新加载到正在运行的进程环境中。当您通过控制台添加了新的提供程序密钥并希望立即使用它时，此功能非常有用。

## REST API

Web控制台提供了前端所使用的REST API。您也可以直接调用这些接口以实现自动化操作：

:::tip 基于配置文件的接口
以下管理类接口——`/api/config`、`/api/env`、`/api/skills`、`/api/tools/toolsets`、`/api/mcp`以及`/api/model/{info,options,auxiliary,set}`——支持可选的`?profile=<name>`查询参数（在写入操作时则使用JSON正文中的`"profile"`字段），该参数可将读写操作限制在该配置文件的`HERMES_HOME`目录内。若未指定该参数，则使用控制台自身的配置文件；未知的配置文件名会返回`404`错误。`/api/pty` WebSocket接口也支持相同参数，用于在选定的配置文件下启动聊天功能。
:::

### GET /api/status

返回代理版本、网关状态、平台运行状况以及当前活跃会话数量。

### GET /api/sessions

返回最新的20个会话及其元数据（模型类型、令牌数量、时间戳、预览内容）。

### GET /api/config

以JSON格式返回当前的`config.yaml`配置内容。

### GET /api/config/defaults

返回默认的配置值。

### GET /api/config/schema

返回描述每个配置字段的架构信息——包括类型、描述、所属类别，以及适用时的可选值列表。前端会利用这些信息为每个字段渲染对应的输入控件。

### PUT /api/config

保存新的配置。请求体格式为`{"config": {...}}`。

### GET /api/env

返回所有已知的环境变量，包括它们的已设置/未设置状态、经过脱敏处理的值、描述以及所属类别。

### PUT /api/env

设置一个环境变量。请求体格式为`{"key": "VAR_NAME", "value": "secret"}`。

### DELETE /api/env

删除一个环境变量。请求体格式为`{"key": "VAR_NAME"}`。

### GET /api/sessions/\{session_id\}

返回单个会话的元数据。

### GET /api/sessions/\{session_id\}/messages

返回某个会话的全部消息历史记录，包括工具调用信息及时间戳。

### GET /api/sessions/search

对消息内容进行全文搜索。查询参数为`q`，返回匹配的会话ID及高亮显示的对应片段。

### DELETE /api/sessions/\{session_id\}

删除某个会话及其所有消息历史记录。

### GET /api/logs

返回日志行。查询参数包括：`file`（指定日志类型，如agent、errors、gateway）、`lines`（指定返回的日志行数）、`level`（日志级别）以及`component`（组件名称）。

### GET /api/analytics/usage

返回令牌使用情况、成本数据以及会话使用分析报告。查询参数为`days`（默认值为30），响应结果包含按日统计的数据以及各模型的汇总信息。

### GET /api/cron/jobs

返回所有已配置的定时任务，包括它们的状态、调度时间以及执行历史记录。

### POST /api/cron/jobs

创建一个新的定时任务。请求体格式为`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/\{job_id\}/pause

暂停某个定时任务。

### POST /api/cron/jobs/\{job_id\}/resume

恢复被暂停的定时任务。

### POST /api/cron/jobs/\{job_id\}/trigger

立即触发某个定时任务，使其在预定时间之外执行。

### DELETE /api/cron/jobs/\{job_id\}

删除某个定时任务。

### GET /api/skills

返回所有技能信息，包括名称、描述、所属类别以及是否已启用状态。

### PUT /api/skills/toggle

启用或禁用某个技能。请求体格式为`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有的工具集信息，包括标签、描述、工具列表以及是否处于活跃/已配置状态。

### 管理类接口

这些接口用于支持MCP、Channels、Webhooks、配对功能以及系统相关页面的运作。它们与`/api/`下的其他接口一样，都受到相同的认证机制保护。

| 方法与路径 | 功能说明 |
|---------------|---------|
| `GET /api/mcp/servers` | 列出已配置的MCP服务器（环境变量值已做脱敏处理） |
| `POST /api/mcp/servers` | 添加新的服务器。请求体格式为`{name, url?, command?, args?, env?, auth?}` |
| `POST /api/mcp/servers/{name}/test` | 连接服务器、列出可用工具、断开连接 |
| `PUT /api/mcp/servers/{name}/enabled` | 启用/禁用某个服务器 |
| `DELETE /api/mcp/servers/{name}` | 删除某个服务器 |
| `GET /api/mcp/catalog` | 浏览经过Nous认证的MCP插件目录 |
| `POST /api/mcp/catalog/install` | 安装某个插件条目（需要提供相应的环境变量） |
| `GET /api/messaging/platforms` | 列出所有消息通道，显示其状态以及各平台的配置字段 |
| `PUT /api/messaging/platforms/{id}` | 配置某个消息通道。请求体格式为`{enabled?, env?, clear_env?}`（环境变量信息会写入`.env`文件，启用状态则会被保存到`config.yaml`中） |
| `POST /api/messaging/platforms/{id}/test` | 检查某个消息通道是否已配置、处于启用状态且已建立连接 |
| `GET /api/pairing` | 列出待审核及已通过审核的消息发送用户 |
| `POST /api/pairing/approve` | 审核并批准某个代码。请求体格式为`{platform, code}` |
| `POST /api/pairing/revoke` | 撤销某个用户的授权。请求体格式为`{platform, user_id}` |
| `POST /api/pairing/clear-pending` | 删除所有待审核的代码 |
| `GET /api/webhooks` | 列出所有的订阅项以及各平台的启用状态 |
| `POST /api/webhooks` | 创建一个新的订阅项（会返回一次性使用的密钥） |
| `DELETE /api/webhooks/{name}` | 删除某个订阅项 |
| `GET /api/credentials/pool` | 列出所有已集中管理的轮换密钥（相关内容已做脱敏处理） |
| `POST /api/credentials/pool` | 添加新的密钥。请求体格式为`{provider, api_key, label?}` |
| `DELETE /api/credentials/pool/{provider}/{index}` | 删除某个密钥（索引从1开始计数） |
| `GET /api/memory` | 显示当前正在使用的提供程序、可用的提供程序列表以及内置存储空间的大小 |
| `PUT /api/memory/provider` | 选择要使用的提供程序（留空则表示仅使用内置提供程序） |
| `POST /api/memory/reset` | 重置内置存储空间。请求体格式为`{target: all\|memory\|user}` |
| `POST /api/gateway/start` · `/stop` · `/restart` | 控制网关的生命周期操作（在后台执行） |
| `POST /api/ops/doctor` · `/security-audit` · `/backup` · `/import` | 执行诊断与维护操作（在后台执行；可通过`/api/actions/{name}/status`查看操作日志） |
| `GET /api/ops/hooks` | 查看已配置的shell钩子以及允许列表的状态 |
| `GET /api/ops/checkpoints` · `POST .../prune` | 检查`/rollback`存储库的内容或删除其中的冗余数据 |
| `POST /api/ops/hooks` · `DELETE /api/ops/hooks` | 创建或删除shell钩子（操作需经过用户同意） |
| `GET /api/system/stats` | 获取主机运行状态统计信息——包括操作系统、CPU使用率、内存使用情况、磁盘使用状况以及系统运行时长 |
| `GET /api/hermes/update/check` | 查询是否有可用更新（包括尚未应用的提交记录及安装方式），但不会自动进行安装。对于那些落后于最新版本的git/pip安装版本，该接口还会返回一份包含变更内容的`commits`列表，列出每个提交的`sha`值、摘要、提交者以及提交时间。使用`?force=1`参数可强制忽略6小时的缓存限制 |
| `GET /api/curator` · `PUT .../paused` · `POST .../run` | 控制技能筛选器的状态，以及暂停/恢复和运行操作 |
| `GET /api/portal` | 用于Nous Portal的认证功能以及工具网关的路由设置（仅支持读取操作） |
| `POST /api/ops/prompt-size` · `/dump` · `/config-migrate` | 执行诊断相关操作（在后台执行） |
| `PUT /api/webhooks/{name}/enabled` | 启用/禁用某个Webhook路由 |
| `POST /api/skills/hub/install` · `/uninstall` · `/update` | 对技能中心进行相关操作（在后台执行） |
| `GET /api/skills/hub/search` | 在所有来源中搜索技能中心中的技能 |
| `GET /api/sessions/stats` | 获取会话存储库的统计信息 |
| `PATCH /api/sessions/{id}` | 重命名或归档某个会话 |
| `GET /api/sessions/{id}/export` | 将某个会话（包含元数据及所有消息内容）以JSON格式导出 |
| `POST /api/sessions/prune` | 删除那些已结束且超过N天的会话 |
| `PUT /api/cron/jobs/{id}` | 修改某个定时任务的提示语、调度时间、名称以及输出方式 |

## 认证（受控访问模式）

当控制台绑定到公共地址或非回环地址——即除`127.0.0.1`/`localhost`之外的任何地址——时，Hermes Agent会启用认证机制。每个请求都必须携带经过验证的会话Cookie，否则会被重定向至登录页面。系统预装了三种认证提供程序：

- **[用户名/密码认证](#usernamepassword-provider-no-oauth-idp)** —— 这是为自托管、本地部署或家庭实验室环境中的控制台添加认证的最简单方式，无需外部身份验证服务。**仅建议在可信网络或VPN保护的环境下使用，切勿用于面向公共互联网的部署。**
- **[OAuth（Nous Portal）认证](#default-provider-nous-research)** —— 适用于托管式部署以及所有可通过公共互联网访问的控制台，也是实现[远程Hermes Desktop连接](#connecting-hermes-desktop-to-a-remote-backend)的推荐方式。每次登录都会通过您的Nous账户进行验证，因此该认证提供程序非常适合用于面向公共互联网的场景。
- **[自托管OIDC认证](#self-hosted-oidc-provider)** —— 允许您通过标准的OpenID Connect方案自行搭建身份验证服务（如Keycloak、Auth0、Okta、Google，或通过OIDC桥接器连接的GitHub等）。无需使用Nous Portal，只要在前面部署符合规范的OIDC服务器，即可用于面向公共互联网的访问场景。

绑定到回环地址的运营商自有控制台则不受此影响——无需认证，也不会出现登录页面。

### 认证机制的启用条件

| 标志参数 | 认证机制状态 | 适用场景 |
|---------|-------------|----------|
| `hermes dashboard`（默认值——绑定到`127.0.0.1`） | 关闭 | 本地开发环境 |
| `hermes dashboard --host 0.0.0.0` | **开启** | 远程/生产环境——建议使用用户名/密码认证或OAuth进行保护 |

认证机制仅在以下两种情况下才会被启用：

1. 绑定地址既不是`127.0.0.1`、`::1`、`localhost`，也不是`0.0.0.0`；且
2. 未设置`--insecure`标志参数。

:::danger `--insecure`参数会完全禁用认证功能
使用`--insecure`参数可以跳过认证机制，直接提供无需认证的控制台访问权限，该控制台可读取/写入您的`.env`文件（其中包含API密钥和敏感信息），并且允许执行代理命令。**绝对不建议在远程连接场景中使用此参数。** 如果需要将控制台暴露给其他机器，应配置[用户名/密码认证](#usernamepassword-provider-no-oauth-idp)（或OAuth）方式，并且不要使用`--insecure`参数。该参数仅作为在完全可信、且受到防火墙保护的单一主机网络环境中的最后应急方案而存在。
:::

### 失败即关闭的机制

如果系统本应启用认证机制，但**没有**注册任何`DashboardAuthProvider`（既没有安装Nous插件，也没有自定义插件），则`hermes dashboard`会直接拒绝绑定，并显示明确的错误信息。系统不会采用“默认拒绝但允许一切”的 fallback策略——配置错误的受控访问控制台将根本无法启动。

当您以**交互式方式**（即在真实的终端环境中）运行`hermes dashboard --host 0.0.0.0`，且尚未配置任何认证提供程序时，Hermes不会仅仅报错，而是会主动提示您立即设置认证方式：您可以选择**用户名和密码认证**（系统会将`dashboard.basic_auth`信息写入`config.yaml`文件，随后几秒内即可开始使用），或者选择**OAuth认证**（系统会引导您前往`hermes dashboard register`页面进行设置）。对于非交互式的调用方式——如Docker/s6容器、持续集成流程、管道式执行等——则不会出现上述提示，直接会触发前述的失败即关闭错误，因此即使在没有认证的情况下，无人值守的部署也无法启动。

### 默认认证提供程序：Nous Research

系统自带的`plugins/dashboard_auth/nous`插件**始终处于已安装状态并会被自动加载**。一旦配置了客户端ID，该插件会自动注册一个名为`nous`的`DashboardAuthProvider`。

由于每次登录都会通过Nous Portal进行验证，并由您的Nous账户提供保护，**因此Nous认证提供程序是适合用于将控制台暴露给公共互联网的最佳选择。**

#### 注册控制台账号

要使用Nous认证提供程序，您需要一个OAuth客户端ID，其格式为`agent:{id}`。获取该客户端ID有两种方法：- **CLI — `hermes dashboard register`**：在仪表板所在的主机上运行该命令。它会自动识别您现有的 Nous 登录信息（若未登录，请先运行 `hermes setup`），将自托管的 OAuth 客户端注册到 Portal 中，并将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 值写入 `~/.hermes/.env` 文件中。可选参数包括：`--name`（用于设置易于识别的标签，若未指定则系统会自动生成）以及 `--redirect-uri`（面向公网的主机所使用的公共 HTTPS 回调地址）。

  ```bash
  hermes dashboard register
  # ✓ Registered dashboard "swift_falcon"
  # …writes HERMES_DASHBOARD_OAUTH_CLIENT_ID to ~/.hermes/.env
  ```

- **图形界面——本地控制面板页面。**在 Nous Portal 中打开 [`/local-dashboards`](https://portal.nousresearch.com/local-dashboards)，即可在浏览器端对自托管的控制面板进行注册、命名、管理及撤销操作。将生成的 `agent:{id}` 客户端 ID 复制到环境变量 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 或配置文件 `config.yaml` 中的 `dashboard.oauth.client_id` 字段。通过该界面，也可以撤销通过 CLI 注册的控制面板。

#### 配置

该插件会从两个来源读取配置，当环境变量被设置且非空时，将以该变量的值为准：

**`config.yaml`**——标准配置文件：

```yaml
dashboard:
  oauth:
    client_id: agent:01HXYZ…             # required to engage the gate
```

**环境变量** — 运维人员可覆盖的参数：

| 环境变量 | 覆盖项 | 格式 | 提供方 |
|---------|-----------|------|--------|
| `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | `dashboard.oauth.client_id` | `agent:{instance_id}` | `hermes dashboard register` |

根据 Hermes Agent 的惯例（`~/.hermes/.env` 仅用于存储 API 密钥/机密信息），对于本地开发、本地部署以及任何由您直接控制的场景，**推荐在 `config.yaml` 中设置这些值**。设置环境变量路径的存在是为了让托管平台能够注入特定于每次部署的 `client_id`，而无需任何人去修改镜像内的 `config.yaml` — 这也是该机制的主要用途。

空的环境变量值将被视为未设置，因此即使平台已配置了机密信息但未被填充，也不会意外覆盖 `config.yaml` 中的有效条目。

如果两个来源均未提供 `client_id`，插件会报告具体原因，而控制台的失败绑定错误则会明确指出需要修复的内容：

```
Refusing to bind dashboard to 0.0.0.0 — the OAuth auth gate engages on
non-loopback binds, but no auth providers are registered.

Bundled providers reported these issues:
  • nous: HERMES_DASHBOARD_OAUTH_CLIENT_ID is not set (and
    dashboard.oauth.client_id in config.yaml is empty). The Nous Portal
    provisions this env var (shape 'agent:{instance_id}') when it
    deploys a Hermes Agent instance — set it to your provisioned
    client id (either as an env var or under dashboard.oauth.client_id
    in config.yaml), or pass --insecure to skip the OAuth gate entirely.

Or pass --insecure to skip the auth gate (NOT recommended on untrusted
networks).
```

#### 实际案例：Nous Research

只需三步，即可从已登录的Hermes环境连接到由Nous管理的控制面板。

**1. 登录并注册控制面板。** 命令 `hermes dashboard register` 会利用您现有的Nous账号来配置OAuth客户端，并自动将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 的值写入 `~/.hermes/.env` 文件中：

```bash
hermes setup            # if you're not already logged into Nous Portal
hermes dashboard register
# ✓ Registered dashboard "swift_falcon"
# …writes HERMES_DASHBOARD_OAUTH_CLIENT_ID to ~/.hermes/.env
```

**2. 在可访问的地址上运行控制面板。** 若不使用 `--insecure` 参数且采用非回环绑定方式，系统将会启用 OAuth 认证机制，同时刚刚设置的 `client_id` 会自动激活 `nous` 提供商。

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

**3. 登录。** 打开 `http://<host>:9119/`，页面将自动跳转至 `/login`。点击 **Sign in with Nous Research** → 在门户网站上完成身份验证 → 最终返回已登录的仪表板。您还可以从任何设备上验证该接入通道是否正常。

```bash
curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["nous"]
```

调用 `GET /api/auth/me` 可返回已验证的会话信息（`provider: nous`）。对于面向互联网的服务器，需使用 `--redirect-uri https://hermes.example.com/auth/callback` 进行注册，并设置 `HERMES_DASHBOARD_PUBLIC_URL`，以便 OAuth 回调能指向您的公开网址（详见[公开网址覆盖](#public-url-override)部分）。

### 用户名/密码认证提供方（无需 OAuth 身份提供商）

如果您不想配置 OAuth 身份提供商——即采用“在控制面板中直接输入密码”的自托管部署方式，那么内置的 `plugins/dashboard_auth/basic` 插件会注册一个名为 `basic` 的 `DashboardAuthProvider`，该提供方通过**用户名和密码**进行认证，而非依赖 OAuth 重定向流程。

它与 OAuth 提供方使用相同的认证机制：服务在非回环地址上启动且不使用 `--insecure` 参数，登录页面会为该提供方显示凭证输入表单（而非“使用 X 登录”按钮），而登录后的所有功能——会话 Cookie、透明刷新、WS 令牌、登出操作以及审计日志——都与 OAuth 路径完全一致。这些会话是由提供方自行生成的基于 HMAC 签名的无状态令牌，因此**无需数据库，也不依赖外部身份提供商**。密码哈希则使用标准库中的 `scrypt` 函数（无第三方依赖）。

:::warning 仅可在受信任的网络中使用此功能——不可用于公共互联网
用户名/密码认证提供方适用于运行在**受信任网络**上或仅能通过**VPN**访问的自托管/本地/家庭实验室控制面板。由于它不依赖外部身份提供商、多因素认证或针对用户的独立账户来保护单一共享凭证，因此**不适合直接将控制面板暴露在公共互联网上**。对于面向互联网的控制面板，请改用[Nous Research 提供方](#default-provider-nous-research)（或您自己的[自托管 OIDC](#self-hosted-oidc-provider) / [自定义 OAuth](#custom-providers)提供方）。
:::

#### 配置

与 Nous 提供方类似，该提供方也会从 `config.yaml` 文件中读取配置（以标准格式为准），若环境变量被设置且非空，则以环境变量值为准。只有当同时配置了 `username` 以及 `password_hash`（推荐）或 `password` 时，该提供方才会启用——否则不会产生任何影响，因此 OAuth 用户以及使用回环地址或 `--insecure` 参数的运行方式都不会受到影响。

**`config.yaml`：**

```yaml
dashboard:
  basic_auth:
    username: admin
    # Preferred — no plaintext at rest. Compute with:
    #   python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"
    password_hash: "scrypt$16384$8$1$…$…"
    # ...or a plaintext password (hashed in-memory at load; less safe at rest):
    # password: "s3cret"
    secret: "<32+ random bytes, base64 or hex>"  # token-signing key
    session_ttl_seconds: 43200                    # optional; access-token lifetime (default 12h)
```

**环境变量覆盖规则：**

| 环境变量 | 被覆盖的配置项 | 备注 |
|---------|--------------|------|
| `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` | `dashboard.basic_auth.username` | 启用该功能所必需 |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` | `dashboard.basic_auth.password_hash` | 推荐使用（避免明文存储） |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | `dashboard.basic_auth.password` | 以明文形式存储；**其优先级高于配置中的 `password_hash`，便于通过环境变量更新密码** |
| `HERMES_DASHBOARD_BASIC_AUTH_SECRET` | `dashboard.basic_auth.secret` | 用于令牌签名的密钥 |
| `HERMES_DASHBOARD_BASIC_AUTH_TTL_SECONDS` | `dashboard.basic_auth.session_ttl_seconds` | 访问令牌的有效期 |

:::注意：为确保会话稳定性，请设置明确的 `secret` 值
当 `secret` 为空时，系统会为每个进程生成随机签名密钥。这对单进程环境而言尚可，但会导致**每次重启后所有会话失效**，且会话**无法跨多个工作进程延续**。如需实现重启后会话依旧有效或支持多工作进程部署，请设置明确的 `secret` 值。
:::

`/auth/password-login` 接口会对每个客户端 IP 实施速率限制（默认为每分钟 10 次尝试，超出后会返回 HTTP 429 错误），并且对于未知用户和密码错误的情况都会统一返回 `401 Invalid credentials` 错误信息，因此无法用于获取用户名列表。

#### 实际应用示例：用户名/密码认证
只需三步，即可在受信任的网络环境中搭建一个需要密码验证的仪表板。

**1. 在 `~/.hermes/.env` 文件中设置认证凭证。** 对密码进行哈希处理以避免明文存储，并设置稳定的签名密钥以确保会话在重启后依然有效：

```bash
# Compute a scrypt hash of your chosen password:
HASH=$(python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('choose-a-strong-password'))")

cat >> ~/.hermes/.env <<EOF
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH=$HASH
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env
```

**2. 在可访问的地址上运行控制面板。** 若以非回环地址进行绑定且未使用 `--insecure` 参数，则会启用网关功能，同时用户名与哈希值将用于激活 `basic` 提供商。

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

**3. 登录。** 打开 `http://<host>:9119/`，页面将自动跳转至 `/login` 页面——这是一个用于输入凭据的表单（而非“使用 X 登录”按钮）。输入 `admin` 及您的密码，即可进入已验证身份的控制面板。您也可以从任何设备上验证该网关功能。

```bash
curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["basic"]
```

执行 `GET /api/auth/me` 请求后会返回已验证的会话信息（`provider: basic`）。请将此操作置于 VPN 后面执行——请参阅上述警告；若使用公共主机，则应改用 [Nous Research](#default-provider-nous-research) 或 [自托管 OIDC](#self-hosted-oidc-provider) 提供商。

#### 自定义密码提供商

`basic` 仅是扩展点的一种实现方式。任何插件均可注册密码提供商：在您的 `DashboardAuthProvider` 子类中设置 `supports_password = True`，并实现 `complete_password_login(*, username, password) -> Session` 方法（验证失败时抛出 `InvalidCredentialsError` 异常，后端存储出现故障时抛出 `ProviderError` 异常）。对于纯密码型提供商，可将 OAuth 的 `start_login` / `complete_login` 方法保留为 `NotImplementedError` 占位实现。LDAP 绑定、凭证数据库或任何其他非重定向认证方案均采用此路径——框架会为您处理表单、路由、Cookie 以及会话刷新等功能。

### 自托管 OIDC 提供商

如果您自行运行身份提供商，内置的 `plugins/dashboard_auth/self_hosted` 插件会使用**标准 OpenID Connect** 协议对控制面板进行认证——无需为每个身份提供商编写专用代码，也不涉及 Nous Portal。该插件可与任何符合规范的 OIDC 服务器配合使用：

> **Authentik · Keycloak · Zitadel · Authelia · Auth0 · Okta · Google · …**

与 Nous 提供商类似，该插件会自动加载，并仅在配置完成后注册自身，因此对于回环测试或 `--insecure` 模式的控制面板而言无需执行任何操作。

#### 配置

需配置 **issuer**（发行机构）和 **client_id**（公共 PKCE 客户端，无需客户端密钥）。插件会从 `{issuer}/.well-known/openid-configuration` 获取身份提供商的 `authorization_endpoint`、`token_endpoint` 和 `jwks_uri`，因此您无需硬编码这些端点地址。

**`config.yaml`**——配置的核心文件：

```yaml
dashboard:
  oauth:
    provider: self-hosted
    self_hosted:
      issuer: https://auth.example.com/application/o/hermes/   # required
      client_id: hermes-dashboard                              # required
      scopes: "openid profile email"                           # optional (this is the default)
```

**环境变量**——操作员可覆盖这些变量（当设置非空值时，该值将优先于 `config.yaml` 中的配置；空值则视为未设置）：

| 环境变量 | 被覆盖的配置项 | 备注 |
|---------|--------------|------|
| `HERMES_DASHBOARD_OIDC_ISSUER` | `dashboard.oauth.self_hosted.issuer` | OIDC 发行方 URL——为必填项 |
| `HERMES_DASHBOARD_OIDC_CLIENT_ID` | `dashboard.oauth.self_hosted.client_id` | 公开客户端 ID——为必填项 |
| `HERMES_DASHBOARD_OIDC_SCOPES` | `dashboard.oauth.self_hosted.scopes` | 默认值为 `openid profile email` |

请在您的身份提供商（IDP）中注册一个支持授权码+PKCE（S256）授权模式的**公开**应用程序/客户端，并将控制面板的回调地址添加为允许的重定向 URI。回调地址为 `<dashboard public URL>/auth/callback`（有关控制面板如何在代理后获取其公开 URL 的信息，请参见[公开 URL 覆盖](#public-url-override)部分）。

#### 验证内容

提供商会根据检测到的 `jwks_uri` 来验证 OpenID Connect **ID 令牌**（RS256/ES256 格式），同时确保令牌中的 `iss` 和 `aud` 字段与您配置的 `issuer` 和 `client_id` 匹配。标准的 OIDC 声明会映射到控制面板的会话信息中：

| 会话字段 | 对应的声明 |
|---------|------------|
| `user_id` | `sub`（必填） |
| `email` | `email` |
| `display_name` | `name` → `preferred_username` → `nickname` → `email` |
| `org_id` | `org_id` / `organization`，若不存在则使用用户所属的 `groups` |

ID 令牌用于确认用户身份——访问令牌则被视为不可见数据（OIDC 规范并未要求其必须是 JWT 格式）。端点 URL 必须为 HTTPS 协议（本地开发环境中的环回地址 `http://` 是允许的），且发现文档中声明的 `issuer` 值必须与您的配置值一致（结尾斜杠的不同是可以接受的）。当 IDP 发放刷新令牌时，可通过标准的 `refresh_token` 授权模式实现静默重新认证；注销操作则会调用 IDP 中声明的 RFC 7009 标准的 `revocation_endpoint`。

> 目前暂不支持**机密客户端**（即那些拥有 `client_secret` 的客户端）——建议配置一个使用公开客户端 + PKCE 的方案，这对于面向浏览器的控制面板而言是常见的选择。

#### 实战示例：Keycloak

[Keycloak](https://www.keycloak.org/) 是最容易部署的自托管 OIDC 服务器之一，非常适合本地测试使用——它在开发模式下仅以单个容器形式运行（采用内存数据库），并提供了标准的 OIDC 发现功能。通过以下步骤，您只需几分钟即可实现从零到可正常使用的控制面板登录功能。

**1. 使用预配置的领域运行 Keycloak**。将此领域的导出文件保存为 `realm-hermes.json`——该文件定义了一个名为 `hermes` 的领域、一个**公开 PKCE 客户端**（名为 `hermes-dashboard`），以及一名测试用户。所有这些配置会在系统启动时自动导入，因此无需在管理界面进行任何操作。

```json
{
  "realm": "hermes",
  "enabled": true,
  "clients": [
    {
      "clientId": "hermes-dashboard",
      "name": "Hermes Agent Dashboard",
      "enabled": true,
      "publicClient": true,
      "standardFlowEnabled": true,
      "protocol": "openid-connect",
      "redirectUris": ["http://localhost:9119/auth/callback"],
      "webOrigins": ["http://localhost:9119"],
      "attributes": { "pkce.code.challenge.method": "S256" }
    }
  ],
  "users": [
    {
      "username": "testuser",
      "enabled": true,
      "emailVerified": true,
      "email": "testuser@example.com",
      "firstName": "Test",
      "lastName": "User",
      "credentials": [
        { "type": "password", "value": "testpassword", "temporary": false }
      ]
    }
  ]
}
```

启动它（Keycloak 26 及以上版本），并将该文件放入导入目录中：

```bash
docker run --rm -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  -v "$PWD/realm-hermes.json:/opt/keycloak/data/import/realm-hermes.json:ro" \
  quay.io/keycloak/keycloak:26.0 \
  start-dev --import-realm
```

一旦部署完成，该领域就会在 `http://localhost:8080/realms/hermes/.well-known/openid-configuration` 地址上公开标准的 OIDC 发现信息（颁发者地址为 `http://localhost:8080/realms/hermes`）。管理控制台则位于 `http://localhost:8080/`，登录账号为 `admin`/`admin`。

**2. 将控制面板指向该地址。** 由于这款自托管插件支持使用回环地址作为颁发者（非回环地址则必须使用 HTTPS），因此本地的 Keycloak 可以直接正常使用。

```bash
export HERMES_DASHBOARD_OIDC_ISSUER="http://localhost:8080/realms/hermes"
export HERMES_DASHBOARD_OIDC_CLIENT_ID="hermes-dashboard"
export HERMES_DASHBOARD_PUBLIC_URL="http://localhost:9119"
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

`HERMES_DASHBOARD_PUBLIC_URL` 用于指定仪表板的 OAuth 回调地址为 `http://localhost:9119/auth/callback`，即上述注册的重定向 URI。若在不使用 `--insecure` 参数的情况下将其绑定到 `0.0.0.0`（非回环地址），即可启用 OAuth 接口。

**3. 登录。** 打开 `http://localhost:9119/`，系统会自动跳转至 `/login` 页面。点击 **Sign in with Self-Hosted OIDC**，然后使用账号 `testuser` 和密码 `testpassword` 在 Keycloak 中完成认证，随后即可返回已登录的仪表板。侧边栏会显示“通过自托管服务以测试用户身份登录”，而调用 `GET /api/auth/me` 则可获取经过验证的会话信息（`provider: self-hosted`，`email: testuser@example.com`）。

> 如果您将仪表板绑定到其他主机或端口，或在该地址下访问，需在 Keycloak 管理控制台（Clients → hermes-dashboard → Settings）中将该地址的 `…/auth/callback` 添加到客户端的**有效重定向 URI**列表中。Authentik、Zitadel、Authelia 以及其他 OIDC 服务器也遵循相同的操作流程，仅发行方 URL 和客户端注册界面会有所不同。

### 公开 URL 覆盖

默认情况下，仪表板会根据请求中的信息自动重建 OAuth 回调地址，即 `X-Forwarded-Host`、`X-Forwarded-Proto` 与 `X-Forwarded-Prefix` 的组合值（当 uvicorn 配置了 `proxy_headers=True` 时即可实现，而 `start_server` 会在启用 OAuth 接口时自动设置该参数）。在正确设置了这三个请求头的反向代理后，此功能可无需额外配置即可正常工作。

对于那些无法可靠转发这些请求头的前端代理环境（如手动配置的 nginx、本地入口服务器，或仅部分启用代理链的自定义域名部署），需将 `dashboard.public_url`（或 `HERMES_DASHBOARD_PUBLIC_URL`）设置为访问该仪表板的**完整公开 URL**。

```yaml
dashboard:
  public_url: "https://dashboard.example.com/hermes"
```

当该参数被设置后，OAuth回调URL将直接变为 `<public_url>/auth/callback` —— 在该处理流程中会忽略 `X-Forwarded-Prefix`，因为操作员已明确指定了公共URL。这是有意为之：若再叠加前缀，对于那些公共URL本身已包含前缀的常见情况，就会导致前缀重复出现。

其优先级与其他控制面板设置相同——环境变量优先于 `config.yaml` 中的配置：

| 设置位置 | 覆盖路径 | 适用场景 |
|---------|---------------|-----------|
| `config.yaml` 中的 `dashboard.public_url` | `HERMES_DASHBOARD_PUBLIC_URL` | 本地开发/本地部署（标准方式） |
| 环境变量 `HERMES_DASHBOARD_PUBLIC_URL` | — | 托管平台密钥/CI环境 |
| 未设置 | — | 默认值——根据 `X-Forwarded-*` 请求头重建URL |

系统会拒绝缺少 `http://`/`https://` 协议、没有主机名，或包含引号/尖括号/空白字符/控制字符的无效值。对于格式错误的值，系统会自动转而通过请求头重建URL，从而确保登录流程能够正常运行，而不会将用户引导至恶意地址。

> **注意：** `public_url` 仅用于覆盖OAuth回调URL。`Secure` Cookie标志仍由 `request.url.scheme` 控制（在 `proxy_headers=True` 的情况下由 `X-Forwarded-Proto` 决定），因此在通过TLS加密的公开环境中使用 `http://` 协议的 `public_url` 时，生成的Cookie将不具备安全属性。这是操作员需要注意的问题——请确保在上游配置正确的TLS加密机制，并与 `public_url` 配合使用。

### OAuth流程

服务提供商需实现 [Nous Portal OAuth合约v1](https://github.com/NousResearch/nous-account-service/blob/main/docs/agent-dashboard-oauth-contract.md)——基于PKCE（S256）的授权码模式：

1. 用户在未携带会话Cookie的情况下访问 `/` 页面 → 网关会将其重定向至 `/login`。
2. 登录页面会显示“使用Nous Research继续登录”按钮 → 导向 `/auth/login?provider=nous`。
3. 服务器会将PKCE状态存储在临时Cookie中，然后将用户重定向至 `https://portal.nousresearch.com/oauth/authorize?…`。
4. 用户在Portal上进行身份验证，最终访问到 `/auth/callback?code=…&state=…`。
5. 服务器通过 `POST /api/oauth/token` 接口将授权码兑换为访问令牌，同时根据Portal提供的JWKS文件（`/.well-known/jwks.json`）验证JWT签名，随后设置 `hermes_session_at` Cookie。
6. 用户会被重定向回 `/` 页面（或通过 `next=` 查询参数返回原来的深度链接路径）。

访问令牌的有效期为15分钟。**合约v1中不支持刷新令牌**——当令牌过期时，单页应用中的请求封装机制会检测到401错误响应，进而全页跳转回 `/login` 以重新执行登录流程。

### 设置的Cookie

| 名称 | 生命周期 | 备注 |
|------|----------|-------|
| `hermes_session_at` | 与令牌有效期相同（15分钟） | 属性为HttpOnly、SameSite=Lax，仅在HTTPS环境下为Secure |
| `hermes_session_pkce` | 10分钟 | 属性为HttpOnly；在请求往返过程中存储PKCE验证器及服务提供商相关信息 |
| `hermes_session_rt` | v1版本中未使用 | 为未来兼容预留；当 `refresh_token` 为空时不会写入该Cookie |

这三个Cookie的路径均为 `/`，且 SameSite属性均为Lax。当通过HTTPS访问控制面板时，`Secure`标志会被设置（该判断基于请求URL的协议类型——在 `proxy_headers=True` 的情况下，会参考上游TLS加密节点提供的 `X-Forwarded-Proto`）。

### 登出

侧边栏插件会显示“当前以 <user_id…> 账户通过Nous登录”字样，并配有登出图标。点击该图标会发送 `/auth/logout` 请求，该请求会清除所有与控制面板相关的认证Cookie，然后将用户重定向回 `/login`。

### 审计日志

每次登录尝试、成功登录、登录失败以及会话验证失败的情况，都会以JSON格式记录到 `$HERMES_HOME/logs/dashboard-auth.log` 文件中。敏感字段（如 `access_token`、`refresh_token`、`code`、`code_verifier`、`state`、`Authorization` 请求头）在记录前会被脱敏处理。

### 自定义服务提供商

若需接入非Nous提供的OAuth服务提供商（如Google、GitHub或自定义OIDC方案），可创建一个插件，该插件需注册一个 `DashboardAuthProvider` 类型。

```python
# ~/.hermes/plugins/dashboard-auth-myidp/__init__.py
from hermes_cli.dashboard_auth import DashboardAuthProvider, Session, LoginStart

class MyIdPProvider(DashboardAuthProvider):
    name = "myidp"
    display_name = "My Identity Provider"

    def start_login(self, *, redirect_uri): ...
    def complete_login(self, *, code, state, code_verifier, redirect_uri): ...
    def verify_session(self, *, access_token): ...
    def refresh_session(self, *, refresh_token): ...
    def revoke_session(self, *, refresh_token): ...

def register(ctx):
    ctx.register_dashboard_auth_provider(MyIdPProvider())
```

登录页面会列出所有已注册的提供方；用户可以在 `/login` 页面选择多个提供方中的任意一个进行使用。

### 非交互式（承载令牌）认证

除了传统的交互式人工登录方式（会话 Cookie + 刷新机制）之外，`DashboardAuthProvider` ABC 还支持通过设置 `supports_token = True` 和 `verify_token(token=...)` 来实现**非交互式的服务间认证**功能。当某个提供方启用此功能后，系统会对传入的 `Authorization: Bearer <token>` 请求进行验证。验证成功后，该提供方指定的支持令牌认证的接口将会获得一个 `TokenPrincipal` 对象（存储在 `request.state.token_principal` 中），从而实现无需 Cookie、无需重定向且无需刷新的认证流程。

预置的第一个消费者就是 **drain** 提供方（位于 `plugins/dashboard_auth/drain`）：`nous-account-service` 会通过 `HERMES_DASHBOARD_DRAIN_SECRET` 为每个智能体生成专用密钥，该提供方则会使用恒定时间比较算法来验证传入的承载令牌，并将 `/api/gateway/drain` 接口标记为支持令牌认证。如果密钥强度不足或长度过短（小于 256 位），注册过程将会直接失败，相应接口也将保持禁用状态；而当该环境变量未被设置时，此功能则不会生效。相关的配置选项（如 `scope`、`min_secret_chars`）位于 `config.yaml` 文件的 `dashboard.drain_auth` 部分。

自定义提供方也可以通过相同的方式实现 `supports_token`/`verify_token` 功能，从而为其自身定义的支持机器认证的接口提供支持。

### 验证网关是否已启用

```bash
# Quick env-var path.
HERMES_DASHBOARD_OAUTH_CLIENT_ID=agent:test \
  hermes dashboard --host 0.0.0.0

# Or the equivalent via config.yaml (recommended for local dev / on-prem):
#
#   dashboard:
#     oauth:
#       client_id: agent:test
#
# then just:
hermes dashboard --host 0.0.0.0

# Hit /api/status to see the gate state:
curl -s http://127.0.0.1:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["nous"]
```

控制面板的 React StatusPage 在“Web server”选项下显示相同的字段。登录后，侧边栏中的 AuthWidget 会展示当前的登录身份。

## 将 Hermes Desktop 连接到远程后端

Hermes Desktop 可以驱动运行在另一台机器上的 Hermes 后端（如 VPS、家庭服务器，或通过 Tailscale 连接的 Mini）。在应用中，该功能位于 **Settings → Gateway → Remote gateway**，需要输入**远程 URL**以及登录方式。（关于桌面应用本身的安装、设置和聊天功能，请参阅 [Hermes Desktop](/user-guide/desktop) 页面。）

您可以使用内置的认证提供程序之一来保护远程控制面板，而桌面应用则会根据后端所声明的认证方式完成登录。对于位于您本地机器之外的后端——如 VPS、公共主机或任何面向互联网的服务器——推荐的认证提供程序是 **OAuth (Nous Portal)**（可通过 [`hermes dashboard register`](#registering-a-dashboard) 进行注册，然后使用“Sign in with Nous Research”进行登录）。当后端位于可信的局域网内或仅能通过 VPN 访问时，内置的 [用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp) 是最快捷的选择，但**不适用于直接暴露在公共互联网上**。将控制面板绑定到非回环地址后会启用其认证网关；登录成功后，桌面应用会自动复用该会话用于聊天 WebSocket，无需手动复制或粘贴令牌。

下面的示例采用了用户名/密码认证方式，因为它在可信网络环境中最容易配置；关于 OAuth 认证方式，请参阅 [默认提供程序：Nous Research](#default-provider-nous-research)。

### 在后端（远程机器上）

```bash
# 1. Set the dashboard login credentials in ~/.hermes/.env (secrets file, 0600).
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
# Recommended: a stable signing secret so sessions survive restarts.
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env

# 2. Run the dashboard bound to a reachable address. The non-loopback bind
#    engages the auth gate; the username/password provider handles login.
hermes dashboard --no-open --host 0.0.0.0 --port 9119
```

若不想以明文形式存储凭证？可使用带有 scrypt 哈希值的 `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` —— 详情请参阅 [用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp)。

若将控制面板作为 systemd 服务运行，当服务单元配置了 `EnvironmentFile=%h/.hermes/.env` 后，`~/.hermes/.env` 文件会自动被读取，因此启动时凭证便已存在于环境变量中。

:::warning
控制面板会读取和写入您的 `.env` 文件（其中包含 API 密钥及敏感信息），同时还能够执行代理命令。此处所示的 **用户名/密码** 设置仅适用于可信网络环境 —— 绝不可将受密码保护的控制面板直接暴露在公网上，应将其置于 VPN 后面。[Tailscale](https://tailscale.com/) 是一种理想的解决方案：通过 `--host <tailscale-ip>` 参数绑定到设备的 Tailscale IP 地址，并将 `http://<tailscale-ip>:9119` 设置为远程地址。只有同一 Tailscale 网络内的设备才能访问该控制面板。若需通过公网访问后端，则应使用 **OAuth (Nous Portal)** 提供程序。
:::

### 在 Hermes Desktop 中

**设置 → 网关 → 远程网关：**

- **远程地址** — `http://<backend-host>:9119`（如果在前端使用了反向代理，也可使用如 `/hermes` 这样的路径前缀）
- **登录** — 应用程序会自动识别用户名/密码类型的网关，并显示 **登录** 按钮；点击该按钮后输入第一步中设置的凭证
- **保存并重新连接** — 该操作会将桌面界面切换到远程后端

如果在后端设置了 `HERMES_DASHBOARD_BASIC_AUTH_SECRET`，则会自动刷新会话，并在重启后依然保持连接状态。

### 通过环境变量覆盖设置

无需通过应用程序内的设置，也可在启动 Hermes Desktop 之前通过环境变量指定后端地址。一旦设置了 `HERMES_DESKTOP_REMOTE_URL`，该值就会覆盖应用程序中保存的地址（此时网关设置面板会显示“环境变量覆盖”标识，并禁用编辑功能）；您仍需通过面板使用用户名和密码进行 **登录**。

| 环境变量 | 值 |
|---------|-------|
| `HERMES_DESKTOP_REMOTE_URL` | `http://<backend-host>:9119` |

### 故障排除

- **“远程网关信息不完整”** —— 说明您未输入远程地址。
- **登录失败，出现 401 错误或“凭证无效”提示** —— 用户名或密码与后端配置的 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` 不匹配。对于未知用户或错误密码的情况，后端会返回相同的通用错误信息，因此请务必检查这两项内容。可通过 `curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'` 命令验证网关状态 —— 结果应显示 `true`，且包含 `"basic"`。
- **没有“登录”按钮，而是要求输入会话令牌** —— 说明用户名/密码类型的提供程序未被启用（`/api/status` 的返回结果中不会列出 `"basic"`）。请确认已设置用户名及密码（或密码哈希值），并且控制面板进程已成功读取这些信息。
- **每次重启后都会自动登出** —— 请将 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 设置为一个固定值；否则每次启动时都会重新生成签名密钥。
- **连接被拒绝或超时** —— 可能是因为后端绑定到了默认的 `127.0.0.1`，而非可访问的地址；或者防火墙/VPN 阻断了对应端口。建议将绑定地址改为 `0.0.0.0` 或 Tailscale IP 地址，并在可信网络中开放该端口。

## CORS 设置

Web 服务器仅允许来自以下本地地址的跨域请求：

- `http://localhost:9119` / `http://127.0.0.1:9119`（生产环境）
- `http://localhost:3000` / `http://127.0.0.1:3000`
- `http://localhost:5173` / `http://127.0.0.1:5173`（Vite 开发服务器）

如果您在自定义端口上运行服务器，该端口对应的地址也会被自动添加到允许列表中。

## 开发相关

如果您计划为 Web 控制面板的前端功能做贡献：

```bash
# Terminal 1: start the backend API
hermes dashboard --no-open

# Terminal 2: start the Vite dev server with HMR
cd web/
npm install
npm run dev
```

位于 `http://localhost:5173` 的 Vite 开发服务器会将 `/api` 路由的请求转发至位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端应用基于 React 19、TypeScript、Tailwind CSS v4 以及 shadcn/ui 风格的组件构建。生产环境构建后的文件会输出到 `hermes_cli/web_dist/` 目录，由 FastAPI 服务器作为静态单页应用来提供服务。

## 更新时自动重建

当运行 `hermes update` 命令时，如果系统中安装了 `npm`，前端应用将会自动重新构建，从而确保控制面板与代码更新保持同步。若未安装 `npm`，则更新过程会跳过前端构建，`hermes dashboard` 会在首次启动时进行构建。

## 主题与插件

该控制面板预置了八种内置主题，同时还支持通过用户自定义主题、插件标签页以及后端 API 路由进行扩展——所有这些功能均可直接使用，无需克隆仓库。

您可以通过顶栏**实时切换主题**：点击语言切换器旁边的调色板图标即可。所选主题会保存在 `config.yaml` 文件的 `dashboard.theme` 字段中，并在页面加载时自动恢复。

同一选择器还支持**独立更改字体**：主题列表下方的“字体”选项可以覆盖当前主题的界面字体设置。此设置会在不同主题之间保持不变（存储于 `config.yaml` 的 `dashboard.font` 字段中）；若选择“主题默认值”，则可清除该设置并恢复为当前主题本身的字体。

内置主题如下：

| 主题 | 特点 |
|------|------|
| **Hermes Teal**（`default`） | 深青色搭配奶油色，使用系统字体，布局间距舒适 |
| **Hermes Teal (Large)**（`default-large`） | 与默认主题相同，但文字大小为 18px，布局间距更宽 |
| **Nous Blue**（`nous-blue`） | 采用 Nous 品牌的蓝色点缀，布局简洁宽敞 |
| **Midnight**（`midnight`） | 深蓝紫色色调，使用 Inter 与 JetBrains Mono 字体 |
| **Ember**（`ember`） | 温暖的深红色搭配青铜色，使用 Spectral 行书字体与 IBM Plex Mono 字体 |
| **Mono**（`mono`） | 灰度风格，使用 IBM Plex 字体，布局紧凑 |
| **Cyberpunk**（`cyberpunk`） | 黑底霓虹绿色，使用 Share Tech Mono 字体 |
| **Rosé**（`rose`） | 粉色搭配象牙白，使用 Fraunces 行书字体，布局宽敞 |

如需创建自定义主题、添加插件标签页、向壳层插槽注入功能，或暴露特定于插件的 REST 接口，请参阅 **[扩展控制面板](./extending-the-dashboard)** 完整指南。该指南涵盖了以下内容：

- 主题 YAML 结构——调色板、字体设置、布局、资源文件、componentStyles、颜色覆盖规则以及自定义 CSS
- 布局样式变体——`standard`、`cockpit`、`tiled`
- 插件清单、SDK、壳层插槽、页面级插槽（可在不覆盖原有组件的情况下将插件组件注入到内置页面中）、后端 FastAPI 路由
- 主题与插件结合使用的完整示例（Strike Freedom 控制台演示）
- 插件的发现、重新加载及故障排查方法 |
