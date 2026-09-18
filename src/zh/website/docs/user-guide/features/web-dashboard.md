---
sidebar_position: 15
title: "Hermes Web Dashboard"
description: "Browser-based administration panel for managing configuration, API keys, MCP servers, messaging pairing, webhooks, the gateway, memory, credentials, sessions, logs, analytics, cron jobs, and skills"
---

# Hermes Web 控制面板

Web 控制面板是一种基于浏览器的用户界面，用于管理您的 Hermes Agent 安装。您无需编辑 YAML 文件或运行 CLI 命令，即可在简洁的网页界面中配置设置、管理 API 密钥以及监控会话。

:::提示
托管模式下的身份验证采用 Nous Portal OAuth；如果您希望控制面板也能与真正的后端系统交互，可使用 `hermes setup --portal` 命令同时连接模型网关和工具网关。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 快速入门

```bash
hermes dashboard
```

该命令会启动一个本地 Web 服务器，并在您的浏览器中打开 `http://127.0.0.1:9119`。控制面板完全在您的设备上运行——没有任何数据会离开本机。

### 选项

| 标志 | 默认值 | 描述 |
|------|---------|-------------|
| `--port` | `9119` | Web 服务器运行的端口 |
| `--host` | `127.0.0.1` | 绑定地址 |
| `--no-open` | — | 不自动打开浏览器 |
| `--insecure` | 关闭 | **已废弃/无作用。** 旧版本中用于在非回环绑定地址时绕过身份验证，但现在已无法取消身份验证——公共绑定地址始终需要身份验证提供方（密码或 OAuth） |
| `--isolated` | 关闭 | 当从指定配置文件（如“工作节点控制面板”）启动时，运行专用的配置文件级服务器，而非路由至全局控制面板 |

```bash
# Custom port
hermes dashboard --port 8080

# Bind to all interfaces (use with caution on shared networks)
hermes dashboard --host 0.0.0.0

# Start without opening browser
hermes dashboard --no-open
```

## 管理多个配置文件

控制面板属于**机器级**管理界面：每台服务器负责管理该机器上的所有[配置文件](../profiles.md)。在存在多个配置文件时，侧边栏中会显示一个配置文件切换器，用于决定管理页面读取和写入的数据所对应的配置文件——配置、API密钥、技能、MCP、模型以及聊天标签页都会随之调整。当选择的是控制面板自身之外的配置文件时，系统会显示一条琥珀色横幅标明当前管理的配置文件，从而确保写入操作的目标始终清晰明确。

配置文件的选择信息会体现在URL中（`?profile=<名称>`），因此像`http://127.0.0.1:9119/skills?profile=worker`这样的深度链接在访问时就会自动选中对应的配置文件切换器，且刷新页面后设置不会丢失。

从配置文件别名启动控制面板时，系统会直接跳转至该机器的控制面板，而不会启动额外的服务器。

```bash
worker dashboard
# → already running: opens the browser at ?profile=worker
# → not running:     starts the machine dashboard with "worker" preselected
```

如需选择退出并运行仅限于该配置文件的专用服务器，可传递 `--isolated` 参数（即采用统一前的行为方式——当您需要为不同配置文件提供具有独立认证机制的仪表板时，此功能非常有用）。

**Chat** 标签页也会随配置文件切换而改变：基于所选配置文件的 `HERMES_HOME` 路径，受限聊天会生成对应的 PTY 子进程，因此对话将使用该配置文件对应的模型、技能、内存及会话历史记录进行。更换配置文件则会启动全新的终端会话。

那些仍保留在各配置文件中且不会被切换器整合的组件包括：网关进程（可通过 `hermes -p <name> gateway …` 命令进行管理）、每个配置文件独立的会话数据库，以及定时任务调度器（Cron 页面已通过自身过滤器实现了跨配置文件的汇总功能）。

## 先决条件

默认安装的 `hermes-agent` 并未包含 HTTP 库或 PTY 助手工具——这些属于可选附加组件。**Web 仪表板**需要 FastAPI 和 Uvicorn（属于 “web” 附加组件）。**Chat** 标签页还需要 `ptyprocess` 用于在伪终端后生成嵌入式 TUI（在 POSIX 系统上属于 “pty” 附加组件）。可通过以下命令安装这两项组件：

```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[web,pty]"
```

`web` 这一附加组件会引入 FastAPI/Uvicorn；而 `pty` 组件则会引入 `ptyprocess`（适用于 POSIX 环境）或 `pywinpty`（适用于原生 Windows 环境——请注意，内置的 TUI 本身仍需依赖 WSL）。执行命令 `cd ~/.hermes/hermes-agent && uv pip install -e ".[all]"` 可同时安装这两类附加组件，若您还需要消息功能、语音功能等，这是最简便的方案。

如果在运行 `hermes dashboard` 时缺少相关依赖，系统会提示您需要安装哪些组件。如果前端尚未构建且系统中存在 `npm`，则首次启动时会自动进行构建。

“聊天”标签页会在每次启动 `hermes dashboard` 时自动出现——内置的浏览器聊天面板（通过 PTY/WebSocket 运行 TUI）始终可用，无需额外设置任何参数。

## 页面

### 状态页面

首页会实时显示您的安装情况概览：

- **Agent 版本**及发布日期
- **网关状态**——运行中/已停止、进程 ID、已连接的平台及其状态
- **活跃会话数**——过去 5 分钟内处于活跃状态的会话数量
- **最近会话列表**——显示最近 20 次会话的记录，包括所使用的模型、消息数量、Token 使用情况以及对话预览内容

状态页面每 5 秒自动刷新一次。

#### 资源压力提示栏

当主机内存或磁盘空间不足时，状态监控结果会同步在仪表板顶部显示提示栏（无需额外发起请求）。

- **“您的 Agent 内存即将耗尽，可能会重启”** — 系统正常运行  
  根据网关每30秒检测的心跳数据，可用内存已降至*较高*水平（< 128 MiB 或 < 15%）或*严重*水平（< 64 MiB 或 < 5%）。
- **“您的 Agent 出现意外重启，很可能是由于内存不足”** — 生命周期记录显示在上次启动时因内存压力而发生了非正常退出（疑似内存溢出导致进程终止）。
- **磁盘警告** — 存放 `~/.hermes` 文件的磁盘空间几乎已满  
  （*较高*水平：剩余空间低于512 MB；*严重*水平：剩余空间低于256 MB）。

同一时间仅会显示最严重的活跃警告（磁盘严重 > 内存严重 > 内存溢出重启 > 磁盘较高 > 内存较高）。警告的关闭仅针对当前网关启动状态有效：关闭一个警告后，下一个活跃警告会显现；若网关重启或警告级别升级（从较高变为严重），该警告将重新出现；而过期的心跳数据则不会产生虚假警报。

### 聊天功能

**聊天**标签页可直接在浏览器中嵌入完整的Hermes TUI界面（与通过 `hermes --tui` 打开的界面相同）。终端TUI中的所有功能——斜杠命令、模型选择器、工具调用卡片、Markdown流式显示、澄清/授权/批准提示以及主题定制——在此处都能实现完全一致的功能，因为控制面板运行的是真实的TUI二进制文件，并通过 [xterm.js](https://xtermjs.org/) 及其WebGL渲染器来呈现ANSI输出，从而实现完美对齐的界面布局。

**工作原理：**

- `/api/pty` 会使用控制面板的会话令牌来建立 WebSocket 连接。  
- 服务器会在 POSIX 伪终端后启动 `hermes --tui` 进程。  
- 按键输入会被发送到该伪终端，而 ANSI 格式的输出则会返回至浏览器。  
- xterm.js 的 WebGL 渲染器会将每个字符单元绘制在整数像素网格上；鼠标跟踪（SGR 1006 标准）、宽字符（Unicode 11）以及绘图符号都能实现原生渲染。  
- 调整浏览器窗口大小时，会通过 `@xterm/addon-fit` 插件相应地调整 TUI 的显示尺寸。

**恢复现有会话：** 在 **Sessions** 标签页中，点击任意会话旁边的播放图标（▶）。这将跳转至 `/chat?resume=<id>` 地址，并以 `--resume` 参数启动 TUI，从而加载完整的对话历史记录。

**会话切换器（右侧栏）：**“聊天”标签页在终端旁边的细长右侧栏中展示了类似ChatGPT风格的对话列表，因此您无需离开当前页面即可切换不同对话。该栏将模型选择器置于顶部，会话列表紧接其下；而终端则占据屏幕的大部分区域。列表会显示当前配置文件下的最新会话信息——包括会话标题（如无法显示标题则会显示消息预览内容）、最近活跃时间、消息数量，以及非CLI会话的来源渠道。点击任意一行即可在该位置继续该对话（终端会重新加载并显示该对话的历史记录），当前活跃的会话会被高亮显示。“新建聊天”功能可启动一个全新会话，同时还有一个刷新控件可用于重新加载列表。此右侧栏仅用于切换操作，删除、重命名、导出以及批量清理等功能仍需在“会话”标签页中进行。在屏幕较窄的情况下，该栏会折叠为可滑出的面板。

**前置条件：**

- Node.js（要求与`hermes --tui`相同；TUI程序包会在首次启动时自动构建）
- `ptyprocess`——可通过`pty`扩展包安装（执行命令：`cd ~/.hermes/hermes-agent && uv pip install -e ".[web,pty]"`，或选择`[all]`即可同时安装两者）
- POSIX内核（Linux、macOS或WSL2）。/chat终端面板需要POSIX PTY支持——原生Windows版本的Python不具备此功能，因此在原生Windows系统上，虽然其他面板（如会话、任务、指标及配置编辑器）仍可正常使用，但/chat标签页会显示提示，建议使用WSL2来启用该功能。
关闭浏览器标签页后，服务器端的 PTY 会立即被正确释放。重新打开标签页则会创建一个新的会话。

若希望 [Hermes Desktop](#connecting-hermes-desktop-to-a-remote-backend) 连接到另一台机器上运行的控制面板，而非其自带的后台服务，请参阅下文的“远程后台”部分。

### 将 Hermes Desktop 连接到远程后台

Hermes Desktop 通常会启动自己的本地后台服务，但也可以通过 **设置 → 网关 → 远程网关** 选项连接到远程机器（如虚拟机、家庭实验室设备等）上运行的控制面板。这类问题往往是“桌面端显示后台已准备就绪，但聊天功能却无法使用”的常见原因，因为桌面端的就绪状态检查所要求的条件，比实际实时聊天连接所需的条件更为宽松。

:::info 先决条件：远程主机上必须正在运行 `hermes dashboard`  
Desktop 所连接的“远程后台”实际上就是运行在远程机器上的 `hermes dashboard` 进程——也就是本文档所描述的同一台服务器上的进程。在执行以下任何操作之前，该进程都必须处于运行状态且可访问；Desktop 仅会连接到该进程，而不会替您启动它。建议通过 `systemd`/`tmux` 等工具保持该进程持续运行，这样在用户登出或重启后它依然能正常工作。至于 **网关**（如 Telegram/Discord/Slack 等），则是一个独立的长期运行的进程——如果您依赖消息渠道功能，需单独启动该进程；桌面应用并非连接到网关本身。  
:::

桌面端的“远程后端已准备就绪”检测仅会调用公共接口 `GET /api/status`——只要主机上运行有任何仪表板，该接口就会立即返回响应。而实时聊天连接则是通过**独立的** WebSocket 连接到 `/api/ws`（以及 `/api/pty`）接口，这一连接还需经过状态检测从未涉及过的另外两项验证：

1. **必须完成身份认证。** 当仪表板绑定到非回环地址时，会启用其认证机制。可通过用户名和密码进行保护（即内置的[用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp)）；桌面端会登录一次，并通过一次性令牌为 WebSocket 连接复用该会话。若未配置相应的提供程序，非回环地址的仪表板**在启动时就会直接失败**。
2. **绑定主机必须允许客户端连接且与 Host 头部信息一致。** 回环绑定（如 `127.0.0.1`）仅接受回环地址的客户端，因此无论凭证如何，远程机器都会在套接字层被拒绝。建议将仪表板绑定到非回环地址（如 `--host 0.0.0.0`），这样对方 IP 的验证机制才能允许远程客户端接入。在桌面端输入的远程 URL 必须能够通过仪表板绑定的同一主机到达——DNS 重绑定验证要求 Host 头部信息必须匹配。

#### 远程仪表板设置

先设置用户名和密码，然后将仪表板绑定到可访问的地址并运行。对于 `systemd` 服务而言：

```ini
[Service]
EnvironmentFile=%h/.hermes/.env
ExecStart=/path/to/venv/bin/python -m hermes_cli.main dashboard \
    --host 0.0.0.0 --port 9119 --no-open
```

其中 `~/.hermes/.env` 文件中包含：

```bash
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
HERMES_DASHBOARD_BASIC_AUTH_SECRET=<32+ random bytes; openssl rand -base64 32>
```

接着在桌面端输入**远程地址**（例如 `http://VM_IP:9119`），并使用该用户名和密码进行**登录**。如需了解完整的配置选项，请参阅[用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp)部分。

:::提示 在重新尝试使用桌面端功能之前，请先确认网关已启动
在任何设备上，检查控制面板是否显示了用户名/密码提供程序：

```bash
curl -s http://VM_IP:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["basic"]
```

- 当 `auth_required: true` 且 providers 列表中包含 `"basic"` 时，桌面端的**登录**流程即可正常工作。  
- 当 `auth_required: false` 时，说明绑定地址为回环地址，或是网关未启动。请尝试绑定非回环地址。  
- 当 `auth_required: true` 但不存在 `"basic"` 提供商时，表示用户名/密码环境变量未被加载。请先修复该问题。  
:::

如果 `/api/status` 显示网关已通过 `"basic"` 提供商启动，但桌面端在登录后仍无法连接，说明问题已超出基础配置范畴。请获取最新的 `desktop.log` 文件（路径：设置 → 网关 → 打开日志），以及同一尝试时段内的控制台日志，查看 `/api/ws` 的返回码（4403 表示聊天 WS 被请求守卫拒绝，常见原因包括主机/对端不匹配；4401 表示 WS 令牌未通过身份验证）。

### 配置

`config.yaml` 支持基于表单的编辑方式。所有 150 多个配置字段都会从 `DEFAULT_CONFIG` 中自动识别，并按标签页分类展示：

![配置管理页面——左侧为分类筛选器，右侧为自动识别的字段](/img/dashboard/admin-config.png)


- **model** — 默认模型、提供方、基础 URL 以及推理设置  
- **terminal** — 后端类型（本地/ Docker/ SSH/ 模态）、超时时间以及 Shell 预设选项  
- **display** — 界面主题、工具进度显示、继续执行选项以及加载动画设置  
- **agent** — 最大迭代次数、网关超时时间以及服务等级  
- **delegation** — 子智能体数量限制以及推理耗力程度  
- **memory** — 提供方选择以及上下文注入设置  
- **approvals** — 危险命令的审批模式（智能/手动/关闭）  
- 其他选项 — `config.yaml` 的每个配置项都对应相应的表单字段  

那些具有固定有效值的字段（如终端后端类型、界面主题、审批模式等）会以下拉菜单形式呈现；布尔值则显示为切换开关；其余所有字段均为文本输入框。  

**操作按钮：**  
- **保存** — 立即将更改写入 `config.yaml` 文件  
- **恢复默认值** — 将所有字段重置为默认值（需点击“保存”才会生效）  
- **导出** — 以 JSON 格式下载当前配置  
- **导入** — 上传 JSON 配置文件以替换现有设置  

:::提示  
配置更改会在下一次智能体会话或网关重启时生效。网页控制面板编辑的正是 `hermes config set` 命令以及网关所读取的同一个 `config.yaml` 文件。  
:::  

### API 密钥  
用于管理存储 API 密钥和凭证的 `.env` 文件。这些密钥会按类别进行分组：

- **大语言模型提供商** — OpenRouter、Anthropic、OpenAI、DeepSeek 等。  
- **工具 API 密钥** — Browserbase、Firecrawl、Tavily、Keenable、ElevenLabs 等。  
- **消息平台** — Telegram、Discord、Slack 机器人令牌等。  
- **智能体设置** — 如 `API_SERVER_ENABLED` 这类非敏感的环境变量。  

每项配置均会显示：  
- 当前是否已设置（显示值的部分掩码内容）；  
- 其用途说明；  
- 对应提供商的注册/密钥获取页面链接；  
- 用于设置或更新值的输入框；  
- 用于删除该配置的按钮。  

高级或极少使用的配置项默认会通过开关隐藏起来。  

### 会话管理  

可浏览并查看所有智能体会话。每行信息会显示会话名称、来源平台图标（CLI、Telegram、Discord、Slack、cron）、模型名称、消息数量、工具调用次数，以及该会话最后活跃的时间。正在运行的会话会通过闪烁的标记来标识。

- **筛选** — “聊天记录”/“自动化任务”/“全部”选项卡可用于限定列表范围：*聊天记录*（默认选项）仅显示人工对话，隐藏自动化相关内容（如定时任务、工具、API及ACP会话）；*自动化任务*仅显示自动化相关内容；*全部*则显示所有内容。通过“精确来源”下拉菜单可进一步缩小范围，仅查看某个特定渠道的记录（例如仅Telegram）。搜索功能会自动适配当前所选的筛选条件。
- **搜索** — 基于FTS5技术对所有消息内容进行全文搜索。搜索结果会高亮显示相关片段，展开后页面会自动滚动至第一条匹配的消息。
- **统计信息** — 统计栏会显示总会话数、当前活跃的会话数、归档会话数、总消息数，以及按来源分类的详细数据。
- **展开** — 点击某条会话即可查看其完整的消息历史记录。消息会根据发送方角色（用户、助手、系统、工具）以不同颜色标注，并以支持语法高亮的Markdown格式呈现。
- **工具调用** — 包含工具调用的助手消息会以可折叠区块的形式展示，其中会注明函数名称及JSON参数。
- **重命名** — 可直接在对应行操作（通过铅笔图标）为会话设置或清除标题。
- **导出** — 可将某条会话的完整信息（包括元数据及全部消息历史）以JSON格式下载（通过下载图标操作）。
- **清理旧会话** — “清理旧会话”按钮可用于删除超过N天的已结束会话。
- **删除** — 通过垃圾桶图标可移除某条会话及其所有消息历史记录。

![会话管理页面——统计栏、清理功能以及每行对应的重命名/导出/删除操作](/img/dashboard/admin-sessions.png)

### 日志

支持通过筛选功能查看代理、网关及错误日志文件，同时还能实时查看日志尾部内容。

- **文件** — 在 `agent`、`errors` 和 `gateway` 日志文件之间切换  
- **级别** — 按日志级别筛选：ALL、DEBUG、INFO、WARNING 或 ERROR  
- **组件** — 按来源组件筛选：全部、gateway、agent、tools、cli 或 cron  
- **行数** — 选择要显示的行数（50、100、200 或 500）  
- **自动刷新** — 开启/关闭实时日志跟踪功能，每5秒查询一次新日志行  
- **颜色编码** — 根据严重程度对日志行进行颜色标注（错误为红色，警告为黄色，调试信息为浅色）  

### 分析功能

基于会话历史数据计算使用情况与成本分析。选择时间周期（7天、30天或90天），即可查看：  

- **概要卡片** — 总令牌数（输入/输出）、缓存命中率、预估或实际总成本，以及每日平均会话总数  
- **每日令牌使用图表** — 展示每日输入与输出令牌使用情况的堆叠柱状图，鼠标悬停可查看详细数据及成本  
- **每日明细表** — 列出每天的日期、会话数、输入令牌数、输出令牌数、缓存命中率及成本  
- **各模型使用情况明细** — 表格形式展示所使用的每个模型、对应会话数、令牌使用量及预估成本  

### Cron任务

创建并管理定时Cron作业，以便按固定时间间隔自动执行Agent指令。

- **创建** — 填写名称（可选）、提示词、定时表达式（例如 `0 9 * * *`）以及发送目标（本地、Telegram、Discord、Slack 或电子邮件）。  
- **任务列表** — 每个任务都会显示其名称、提示词预览、调度表达式、状态标签（已启用/暂停/出错）、发送目标、上次运行时间以及下次运行时间。  
- **暂停 / 继续** — 在已启用和暂停状态之间切换任务。  
- **编辑** — 打开预填好的模态框，用于修改任务的提示词、调度设置、名称或发送目标。  
- **立即触发** — 在非正常调度时间下立即执行任务。  
- **删除** — 永久移除该定时任务。  

### 配置文件  

创建并管理 [配置文件](../profiles.md) — 这些独立的 Hermes 实例拥有各自的配置、技能和会话。

- **配置文件卡片**——每张卡片会显示对应模型/提供方、技能数量、网关状态、描述以及徽章（激活、默认、别名）。
- **创建**——需填写名称，可选是否从默认配置克隆/克隆所有内容/不包含任何预装技能，同时还需填写描述和模型；专门的配置文件构建页面（`/profiles/new`）可提供完整的配置流程（模型、MCPs、技能）。
- **管理技能与工具**——跳转至该配置文件对应的技能页面（此时侧边栏会显示配置文件切换器）。
- **设为激活状态**——切换默认的激活状态，以便**后续的CLI/网关运行**使用该配置文件（功能与`hermes profile use`相同）。此操作不会改变控制面板所管理的配置——那是配置文件切换器的职责。
- **编辑模型/描述/SOUL**——提供内联编辑器，可直接修改该配置文件的相关内容。
- **重命名/删除**——仅适用于已命名的配置文件。

### 技能

可浏览、搜索并切换已安装的技能与工具集，同时还能从中心平台安装新技能。这些技能存储在`~/.hermes/skills/`目录中，并按类别进行分组。

- **搜索** — 按名称、描述或类别筛选已安装的技能与工具集  
- **类别筛选** — 点击类别标签以缩小列表范围（例如 MLOps、MCP、红队测试、AI）  
- **开关控制** — 通过开关启用或禁用单个技能。更改将在下次会话中生效。  
- **工具集** — 另一个视图可查看内置工具集（文件操作、网页浏览等），并显示其启用/禁用状态、设置要求以及所含工具列表  
- **浏览中心** — 第三个视图可在所有来源中搜索技能中心（功能与 `hermes skills search` 相同），可通过标识符安装任意结果，并提供“全部更新”按钮以刷新已安装的技能。

![技能管理页面 — 浏览中心视图：搜索、安装与更新](/img/dashboard/admin-skills-hub.png)

### MCP

无需使用 CLI 即可管理 [MCP](./mcp) 服务器。方法与在 `config.yaml` 中使用 `hermes mcp` 读取的 `mcp_servers` 配置项相同。

**您的 MCP 服务器：**

- **添加** — 注册 HTTP/SSE 服务器（URL）或标准输入输出服务器（命令及参数），对于标准输入输出服务器，还可可选地设置 `KEY=VALUE` 格式的环境变量。  
- **启用/禁用** — 在不删除服务器的情况下切换其开启或关闭状态。被禁用的服务器仍会保留在配置中，便于日后重新启用。此操作会在下一次网关重启时生效。  
- **测试** — 连接到服务器，列出其提供的工具，然后断开连接——在代理开始依赖该服务器之前对其进行连接验证。  
- **删除** — 从配置中移除某个服务器。  
在列表视图中，以密钥形式呈现的环境变量值会被匿名处理。

**目录**：浏览经过 Nous 审核的 MCP 服务器（即内置的 `optional-mcps/` 目录），并一键安装任意服务器。需要 API 密钥的条目会直接提示输入密钥，这些值将会被保存到 `.env` 文件中。该目录与 `hermes mcp catalog` / `hermes mcp install` 命令所使用的目录相同。

![MCP 管理页面 — 显示带有启用/禁用切换功能的服务器，以及安装目录](/img/dashboard/admin-mcp.png)

### Webhook

管理动态的 [Webhook 订阅](/user-guide/messaging/webhooks)。首先必须在消息设置中开启 Webhook 功能；若未开启，页面会给出提示。

- **创建** — 可设置名称、描述、事件过滤器、投递目标、可选的直接投递模式以及代理提示语。创建完成后，页面会显示路由URL及需复制的一次性HMAC密钥。  
- **启用/禁用** — 切换订阅状态的开启或关闭。被禁用的路由仍会保留在订阅文件中，但网关会拒绝接收其发送的事件（返回403错误）。网关会自动热加载该文件，因此更改会在下一个事件处理时生效，无需重启。  
- **列表** — 每个订阅项都会显示其URL、所处理的事件以及投递目标。  
- **删除** — 移除某个订阅项。  

![Webhooks管理页面——带有启用/禁用切换功能的订阅项](/img/dashboard/admin-webhooks.png)

### 配对

无需使用CLI即可批准或撤销用户的消息发送权限——远程管理员可通过此功能将Telegram/Discord等平台的用户接入已配对的网关。其功能与`hermes pairing`完全一致。  
- **待处理请求** — 每个请求项都会显示平台类型、代码、用户信息及生成时间，同时提供一个“批准”按钮。  
- **已批准用户** — 每个用户项都会显示平台类型及用户名，同时提供一个“撤销”按钮。  
- **清除待处理项** — 删除所有尚未处理的配对代码。  

![配对管理页面](/img/dashboard/admin-pairing.png)

### 频道

可通过浏览器将 Hermes 连接到任意消息平台——其功能与 `hermes setup gateway` 完全一致。该页面列出了所有受支持的渠道（Telegram、Discord、Slack、Matrix、Mattermost、WhatsApp、Signal、BlueBubbles/iMessage、电子邮件、SMS/Twilio、钉钉、飞书/Lark、企业微信、微信、QQ 聊天机器人、元宝），同时显示各渠道的实时连接状态。

- **配置**——打开针对特定平台的表单，其中仅包含该渠道所需的字段（机器人令牌、应用令牌、服务器地址、允许列表等）。敏感信息会以密码输入框的形式呈现并经过脱敏处理；若留空某个字段，则保留其当前值。必填字段会标出并进行验证。“设置指南”链接可引导用户查看对应平台的凭证文档。
- **启用/禁用**——切换渠道的开启或关闭状态。凭证仍保存在磁盘中，仅状态会发生变化。
- **测试**——检查该渠道是否已正确配置、处于开启状态，以及是否能从网关获取实时连接信息。
- **重启网关**——凭证会被写入 `~/.hermes/.env` 文件，而开启状态则存储在 `config.yaml` 文件中；网关在下一次启动时会自动连接所有已启用的渠道，用户可直接在此页面触发重启操作。

![渠道管理页面——显示各消息平台的连接状态、启用切换按钮以及针对不同平台的配置表单](/img/dashboard/admin-channels.png)

### 系统

用于管理整个系统安装操作的统一控制面板：

- **主机信息** — 实时系统状态：操作系统与内核版本、架构类型、主机名、Python及Hermes版本、CPU核心数与使用率、内存使用情况、Hermes安装目录的磁盘使用状况、系统运行时长以及负载平均值。（若安装了`psutil`，则CPU/内存/磁盘数据来自该工具；身份相关字段则会始终显示。）Hermes版本会显示**更新状态标签**（已更新/落后N次提交）以及**检查更新**按钮。对于通过Git方式安装的版本，当有可用更新时，**立即更新**按钮会先弹出确认对话框，说明将拉取多少次提交，随后在后台执行`hermes update`命令。而对于通过Docker或Nix方式安装的版本，控制面板无法直接进行就地更新，因此会显示相应的离线更新命令。）
- **Nous Portal** — 登录状态、当前正在使用的推理服务提供商，以及工具网关的路由表（显示哪些工具是通过Portal运行，哪些是在本地运行），同时还提供管理订阅的链接。该页面为`hermes portal`的只读镜像。
- **技能管理器** — 技能的后台维护状态（运行中/暂停中、间隔时间、上次运行时间），并提供暂停/继续操作以及立即运行按钮。该页面为`hermes curator`的镜像。
- **网关控制** — 可以启动、停止和重启消息传递网关，同时显示实时状态（运行中/已停止、进程ID、当前状态）。
- **内存设置** — 可选择外部内存提供方（或仅使用内置内存），并可重置内置的`MEMORY.md`/`USER.md`存储文件。
- **凭证池** — 可以添加或删除代理程序会按顺序调用的轮换API密钥（针对不同的服务提供商）。列表中的密钥值会被遮蔽处理，只有原始密钥值才会传递给代理程序。
- **操作** — 运行 `doctor` 工具进行安全审计、创建备份、从备份归档中恢复数据、更新技能配置、查看系统提示语的字符分布情况、生成支持信息转储文件，或为已废弃的设置迁移配置。这些操作都会启动相应的后台任务，其实时日志会实时显示在页面上。
- **检查点** — 查看 `/rollback` 阴影存储空间的大小并对其进行清理。
- **Shell钩子** — 列出已配置的钩子及其授权状态与可执行状态，**创建**钩子（包括事件、命令、匹配规则、超时时间等参数，并需用户同意授权），以及删除现有钩子。由于钩子可以执行任意命令，因此创建表单会显示安全警告，且只有在获得用户授权后钩子才会被触发。

![系统管理页面 — 主机统计信息与Nous Portal状态](/img/dashboard/admin-system-top.png)

![系统管理页面 — 技能管理器、网关、内存及凭证池信息](/img/dashboard/admin-system-curator.png)

![系统管理页面 — 操作、检查点及Shell钩子设置](/img/dashboard/admin-system-ops.png)

创建Shell钩子（请注意同意复选框以及“可执行任意命令”的安全警告）：

![新建Shell钩子对话框](/img/dashboard/admin-hook-create.png)

:::warning 安全提示  
Web 控制面板会读取和写入包含 API 密钥及敏感信息的 `.env` 文件。该控制面板默认绑定在 `127.0.0.1` 地址上，仅能从本地机器访问且无需登录。若将其绑定到非回环地址（包括 `0.0.0.0`），则系统会启用[身份验证机制](#authentication-gated-mode)：在配置好身份验证提供方（用户名/密码或 OAuth）之前，服务器将拒绝启动。  
:::

## `/reload` 命令  
该控制面板的更新还为交互式 CLI 添加了 `/reload` 命令。通过 Web 控制面板（或直接编辑 `.env` 文件）更改 API 密钥后，可在正在运行的 CLI 会话中使用 `/reload` 命令来应用这些更改，而无需重启服务器：

```
You → /reload
  Reloaded .env (3 var(s) updated)
```

该功能会将 `~/.hermes/.env` 的内容重新加载到正在运行的进程环境中。当您通过控制面板添加了新的提供程序密钥并希望立即使用它时，此功能非常有用。

## REST API

网页控制面板提供了一个供前端使用的 REST API。您也可以直接调用这些端点以实现自动化操作：

:::提示：基于配置文件的端点
管理端点系列——`/api/config`、`/api/env`、`/api/skills`、
`/api/tools/toolsets`、`/api/mcp` 以及 `/api/model/{info,options,auxiliary,set}`——
支持一个可选的 `?profile=<name>` 查询参数（在写入操作时则使用 JSON 正文中的 `"profile"`），该参数可将读写操作限制在对应配置文件的 `HERMES_HOME` 环境中。若未指定该参数，则表示使用控制面板自身的配置文件。未知的配置文件名称会返回 `404` 错误。`/api/pty` WebSocket 也支持相同的参数，以便在选定的配置文件下启动聊天功能。
:::

### GET /api/status

该接口会返回代理版本、网关状态、平台运行状况以及当前活跃会话的数量。

响应中还会包含两个提示性资源块（它们不会影响 `components`/`overall` 维度的健康状态判定）：

- **`memory`** — 该字段的数据来源于网关的30秒心跳信息以及生命周期记录表。包含的字段有：`pressure`（`ok` / `elevated` / `critical` / `unknown`）、`gateway_rss_mb`、`system_total_mb`、`system_available_mb`、`swap_used_mb`、`sampled_at`、`boot_id`、`last_boot_unclean`、`last_boot_suspected_oom`。当可用系统内存低于128 MiB（或15%）时，压力状态为`elevated`；低于64 MiB（或5%）时则为`critical`——恰好也是系统因内存不足而非正常退出并被判定为可能由OOM导致的时刻。对于超过150秒旧（或日期在未来）的心跳数据，虽然其数值仍会被保留，但压力状态会被设为`unknown`，这样已失效的网关的最后检测数据就无法冒充正常运行时的数据。

- **`disk`** — 该字段基于`~/.hermes`所在磁盘的实时`shutil.disk_usage()`检测结果。包含的字段有：`pressure`、`free_mb`、`total_mb`、`used_percent`、`sampled_at`。当可用空间低于512 MB（或使用率≥85%且剩余空间不足4 GB）时，压力状态为`elevated`；当可用空间低于256 MB（或使用率≥95%且剩余空间不足1 GB）时则为`critical`。

这两种数据采集方式都具有故障保护机制：一旦出现任何采样错误，相关数据块会被标记为`{"pressure": "unknown"}`，而不会导致状态查询接口返回失败。由于 `/api/status` 接口是公开接口，因此所显示的数值均为粗略值（以整MB和整百分比表示）。

### GET /api/sessions

返回最新的20个会话信息，同时包含会话元数据（模型类型、令牌数量、时间戳及预览内容）。

### GET /api/config

以JSON格式返回当前的`config.yaml`配置文件内容。

### GET /api/config/defaults

返回默认的配置值。

### GET /api/config/schema

该接口会返回描述所有配置字段的架构信息，包括类型、说明、分类以及适用时的可选值。前端系统会利用这些信息为每个字段渲染对应的输入控件。

### PUT /api/config

用于保存新的配置。请求体格式为：`{"config": {...}}`。

### GET /api/env

返回所有已知的环境变量，同时显示它们的已设置/未设置状态、掩码处理后的值、说明以及分类信息。

### PUT /api/env

用于设置环境变量。请求体格式为：`{"key": "VAR_NAME", "value": "secret"}`。

### DELETE /api/env

用于删除某个环境变量。请求体格式为：`{"key": "VAR_NAME"}`。

### GET /api/sessions/\{session_id\}

返回单个会话的元数据信息。

### GET /api/sessions/\{session_id\}/messages

返回有限页数的消息历史记录，其中包含工具调用信息和时间戳。默认情况下会按时间顺序返回最新的500条消息。如需进行精确分页，可使用`limit`（最大值为500）、`offset`以及`order=oldest|latest`参数。

### GET /api/sessions/search

对消息内容进行全文搜索。查询参数为`q`，返回匹配的会话ID及高亮显示的对应片段。

### DELETE /api/sessions/\{session_id\}

用于删除某个会话及其对应的消息历史记录。

### GET /api/logs

返回日志行数据。查询参数包括：`file`（agent/errors/gateway）、`lines`（记录数量）、`level`以及`component`。

### GET /api/analytics/usage

返回令牌使用情况、成本数据以及会话分析信息。查询参数为`days`（默认值为30）。响应结果包含按天统计的数据以及各模型的汇总信息。

### GET /api/cron/jobs

返回所有已配置的定时任务，包括其状态、调度时间以及运行历史记录。

### POST /api/cron/jobs

创建一个新的定时任务。请求体格式为：`{"prompt": "...", "schedule": "0 9 * * *", "name": "...", "deliver": "local"}`。

### POST /api/cron/jobs/\{job_id\}/pause

暂停某个定时任务。

### POST /api/cron/jobs/\{job_id\}/resume

恢复被暂停的定时任务。

### POST /api/cron/jobs/\{job_id\}/trigger

在非预定时间立即触发该定时任务。

### DELETE /api/cron/jobs/\{job_id\}

删除某个定时任务。

### GET /api/skills

返回所有技能信息，包括名称、描述、类别以及启用状态。

### PUT /api/skills/toggle

启用或禁用某个技能。请求体格式为：`{"name": "skill-name", "enabled": true}`。

### GET /api/tools/toolsets

返回所有工具集的信息，包括标签、描述、工具列表以及是否处于激活/已配置状态。

### 管理端点

这些端点为MCP、Channels、Webhooks、Pairing以及系统页面提供功能支持。与其余的 `/api/` 接口一样，它们均通过相同的身份验证机制进行访问控制。

| Method & path | Purpose |
|---------------|---------|
| `GET /api/mcp/servers` | List configured MCP servers (env values redacted) |
| `POST /api/mcp/servers` | Add a server. Body: `{name, url?, command?, args?, env?, auth?}` |
| `POST /api/mcp/servers/{name}/test` | Connect, list tools, disconnect |
| `PUT /api/mcp/servers/{name}/enabled` | Enable / disable a server |
| `DELETE /api/mcp/servers/{name}` | Remove a server |
| `GET /api/mcp/catalog` | Browse the Nous-approved MCP catalog |
| `POST /api/mcp/catalog/install` | Install a catalog entry (with required env) |
| `GET /api/messaging/platforms` | List every messaging channel with status + per-platform setup fields |
| `PUT /api/messaging/platforms/{id}` | Configure a channel. Body: `{enabled?, env?, clear_env?}` (env writes to `.env`, enabled to `config.yaml`) |
| `POST /api/messaging/platforms/{id}/test` | Report whether a channel is configured, enabled, and connected |
| `GET /api/pairing` | List pending + approved messaging users |
| `POST /api/pairing/approve` | Approve a code. Body: `{platform, code}` |
| `POST /api/pairing/revoke` | Revoke a user. Body: `{platform, user_id}` |
| `POST /api/pairing/clear-pending` | Drop all pending codes |
| `GET /api/webhooks` | List subscriptions + platform-enabled status |
| `POST /api/webhooks` | Create a subscription (returns one-time secret) |
| `DELETE /api/webhooks/{name}` | Remove a subscription |
| `GET /api/credentials/pool` | List pooled rotation keys (redacted) |
| `POST /api/credentials/pool` | Add a key. Body: `{provider, api_key, label?}` |
| `DELETE /api/credentials/pool/{provider}/{index}` | Remove a key (1-based index) |
| `GET /api/memory` | Active provider + available providers + built-in file sizes |
| `PUT /api/memory/provider` | Select a provider (empty = built-in only) |
| `POST /api/memory/reset` | Reset built-in memory. Body: `{target: all\|memory\|user}` |
| `POST /api/gateway/start` · `/stop` · `/restart` | Gateway lifecycle (backgrounded) |
| `POST /api/ops/doctor` · `/security-audit` · `/backup` · `/import` | Diagnostics & maintenance (backgrounded; tail via `/api/actions/{name}/status`) |
| `GET /api/ops/hooks` | Configured shell hooks + allowlist status |
| `GET /api/ops/checkpoints` · `POST .../prune` | Inspect / prune the `/rollback` store |
| `POST /api/ops/hooks` · `DELETE /api/ops/hooks` | Create / remove a shell hook (consent-gated) |
| `GET /api/system/stats` | Host stats — OS, CPU, memory, disk, uptime |
| `GET /api/hermes/update/check` | Report update availability (commits behind, install method) without applying. For git installs that are behind, also returns a `commits` list (`sha`, `summary`, `author`, `at`) of what's changed. `?force=1` busts the 6h cache |
| `GET /api/curator` · `PUT .../paused` · `POST .../run` | Skill-curator status + pause/resume + run |
| `GET /api/portal` | Nous Portal auth + Tool Gateway routing (read-only) |
| `POST /api/ops/prompt-size` · `/dump` · `/config-migrate` | Diagnostics (backgrounded) |
| `PUT /api/webhooks/{name}/enabled` | Enable / disable a webhook route |
| `POST /api/skills/hub/install` · `/uninstall` · `/update` | Skills hub actions (backgrounded) |
| `GET /api/skills/hub/search` | Search the skill hub across all sources |
| `GET /api/sessions/stats` | Session-store statistics |
| `PATCH /api/sessions/{id}` | Rename / archive a session |
| `GET /api/sessions/{id}/export` | Export a session (metadata + messages) as JSON |
| `POST /api/sessions/prune` | Delete ended sessions older than N days |
| `PUT /api/cron/jobs/{id}` | Edit a cron job's prompt / schedule / name / deliver |

## 认证（网关模式）

当控制面板绑定到公共地址或非回环地址——即除 `127.0.0.1` / `localhost` 之外的任何地址时，Hermes Agent 会启用认证网关。每个请求都必须携带经过验证的会话 Cookie，否则将被重定向至登录页面。系统预置了三种认证提供方：

- **[用户名/密码](#usernamepassword-provider-no-oauth-idp)** —— 这是为自托管/本地部署或家庭实验室环境中的控制面板添加认证的最简单方式，无需外部身份验证服务。**仅建议在可信网络或 VPN 后端使用，切勿用于面向公共互联网的场景。**
- **[OAuth（Nous Portal）](#default-provider-nous-research)** —— 适用于托管部署以及可通过公共互联网访问的任何控制面板，也是实现[远程 Hermes Desktop 连接](#connecting-hermes-desktop-to-a-remote-backend)的推荐方案。每次登录都会通过您的 Nous 账户进行验证，因此非常适合用于面向互联网的场景。
- **[自托管 OIDC](#self-hosted-oidc-provider)** —— 允许您通过标准的 OpenID Connect 协议自行搭建身份验证服务（如 Keycloak、Auth0、Okta、Google，或通过 OIDC 桥接实现的 GitHub 等）。无需使用 Nous Portal；在配有合规 OIDC 服务器作为前置节点的情况下，可安全地用于面向公共互联网的场景。

绑定到回环地址的运营商自有控制面板则不受影响——无需认证，也不会出现登录页面。

### 网关何时启用

| 标志 | 认证网关 | 使用场景 |
|-------|-----------|----------|
| `hermes dashboard`（默认值——绑定到 `127.0.0.1`） | 关闭 | 本地开发环境 |
| `hermes dashboard --host 0.0.0.0` | **开启** | 远程/生产环境——需通过用户名/密码认证提供器或 OAuth 进行保护 |

仅当绑定主机不是 `127.0.0.1`、`::1` 或 `localhost` 时，该认证网关才会启用。绑定到 `0.0.0.0`（或任何 RFC1918 标准的局域网地址）都会激活该网关。旧的 `--insecure` 标志**已无法关闭该网关**——出于向后兼容性考虑，该标志仍会被接受，但会触发警告并被忽略。

:::danger `--insecure` 标志实际上不起任何作用——它无法禁用认证功能
自 2026 年 6 月的安全强化措施实施后，`--insecure` 标志不再能绕过仪表板认证：非回环地址绑定始终需要使用认证提供器（即用户名/密码认证提供器或 OAuth）。如果希望获得无需认证的仪表板体验，应将其绑定到 `127.0.0.1`，并通过 SSH 隧道或 Tailscale 方式访问。
:::

### 失败即关闭机制

如果该认证网关本应启用，但**未注册任何 `DashboardAuthProvider`**（既没有 Nous 插件，也没有自定义插件），`hermes dashboard` 会拒绝绑定，并显示明确的错误信息。系统不会采用“默认拒绝但允许一切”的兜底策略——配置错误的带认证网关的仪表板将永远无法启动。

当您在**交互式终端**中运行 `hermes dashboard --host 0.0.0.0` 命令且尚未配置任何提供者时，Hermes 不仅会报错，还会主动提示您立即设置：您可以选择**用户名与密码**方式（系统会将 `dashboard.basic_auth` 内容写入 `config.yaml`，随后几秒内即可开始使用），或选择**OAuth** 方式（系统会引导您前往 `hermes dashboard register` 页面）。而对于非交互式的调用场景——如 Docker/s6、CI 环境或通过管道执行的命令——则不会显示上述提示，直接出现报错并终止运行，因此未经身份验证的无人值守部署同样无法启动。

### 默认提供者：Nous Research

预装的 `plugins/dashboard_auth/nous` 插件始终处于已安装状态并被自动加载。一旦配置了客户端 ID，该插件会自动注册一个名为 `nous` 的 `DashboardAuthProvider`。

由于所有登录操作都会通过 Nous Portal 进行验证，并受您的 Nous 账户保护，**因此 Nous 提供者是最适合将控制面板公开到互联网上的选择。**

#### 注册控制面板

要使用 Nous 提供者，您需要一个 OAuth 客户端 ID（格式为 `agent:{id}`）。获取该 ID 的方法有两种：

- **通过 CLI 命令 — `hermes dashboard register`**。在存放控制面板的服务器上运行此命令。它会自动识别您现有的 Nous 登录信息（若未登录，请先运行 `hermes setup`），在 Portal 中注册一个自托管的 OAuth 客户端，并将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 的值写入 `~/.hermes/.env` 文件中。可选参数包括：`--name`（用于设置易于识别的标签，如未指定则系统会自动生成）以及 `--redirect-uri`（面向互联网服务器的公共 HTTPS 回调地址）。

  ```bash
  hermes dashboard register
  # ✓ Registered dashboard "swift_falcon"
  # …writes HERMES_DASHBOARD_OAUTH_CLIENT_ID to ~/.hermes/.env
  ```

- **图形界面——本地控制面板页面。** 在 Nous Portal 中打开 [`/local-dashboards`](https://portal.nousresearch.com/local-dashboards)，即可在浏览器端对自托管控制面板进行注册、命名、管理及撤销操作。将生成的 `agent:{id}` 客户端 ID 复制到环境变量 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 或配置文件 `config.yaml` 中的 `dashboard.oauth.client_id` 字段。通过该界面也可撤销通过 CLI 注册的控制面板。

#### 配置方式

该插件会从两个配置源读取设置，若环境变量已设置且非空，则以环境变量中的值为准：

**`config.yaml`**——标准配置源：

```yaml
dashboard:
  oauth:
    client_id: agent:01HXYZ…             # required to engage the gate
```

**环境变量** — 操作员覆盖设置：

| 环境变量 | 覆盖项 | 格式 | 提供方 |
|---------|-----------|--------|----------|
| `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | `dashboard.oauth.client_id` | `agent:{instance_id}` | `hermes dashboard register` |

根据 Hermes Agent 的约定（`~/.hermes/.env` 仅用于存储 API 密钥/机密信息），对于本地开发、本地部署以及任何由您直接控制的场景，**推荐在 `config.yaml` 中设置这些值**。设置环境变量的方式是为了让托管平台能够注入针对每次部署的 `client_id`，而无需任何人去修改镜像内的 `config.yaml` —— 这也是其主要用途。

空的环境变量值将被视为未设置，因此即使平台已配置了密钥但未被填充，也不会意外覆盖 `config.yaml` 中的有效配置项。

如果两个来源均未提供 `client_id`，插件会报告具体原因，而控制台的错误信息则会明确指出需要修复的内容：

```
Refusing to bind dashboard to 0.0.0.0 — the auth gate engages on
non-loopback binds, but no auth providers are registered.

Bundled providers reported these issues:
  • nous: HERMES_DASHBOARD_OAUTH_CLIENT_ID is not set (and
    dashboard.oauth.client_id in config.yaml is empty). …

Configure an auth provider before exposing the dashboard:
  • Password: set dashboard.basic_auth.username + password_hash in config.yaml
  • OAuth: run `hermes dashboard register` (Nous Portal) or install a
    DashboardAuthProvider plugin.
There is no unauthenticated public-bind option — to keep it local, bind
127.0.0.1 and tunnel in (SSH / Tailscale).
```

#### 实际案例：Nous Research

只需三步，即可从已登录的Hermes环境连接到由Nous保护的仪表板。

**1. 登录并注册仪表板。** 命令 `hermes dashboard register` 会利用您现有的Nous账号来配置OAuth客户端，并自动将 `HERMES_DASHBOARD_OAUTH_CLIENT_ID` 写入 `~/.hermes/.env` 文件中：

```bash
hermes setup            # if you're not already logged into Nous Portal
hermes dashboard register
# ✓ Registered dashboard "swift_falcon"
# …writes HERMES_DASHBOARD_OAUTH_CLIENT_ID to ~/.hermes/.env
```

**2. 在可访问的地址上运行控制面板。** 使用非回环绑定方式即可启用 OAuth 接口，而刚刚设置的 `client_id` 会激活 `nous` 提供商服务：

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

**3. 登录。** 打开 `http://<host>:9119/`，页面将自动跳转至 `/login`。点击 **Sign in with Nous Research** → 在门户网站上完成身份验证 → 最终返回已登录的仪表板。您还可以从任何设备上验证该访问通道是否正常。

```bash
curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["nous"]
```

调用 `GET /api/auth/me` 可获取已验证的会话信息（`provider: nous`）。对于面向公网的服务器，需使用 `--redirect-uri https://hermes.example.com/auth/callback` 进行注册，并设置 `HERMES_DASHBOARD_PUBLIC_URL`，以便 OAuth 回调能够指向您的公网地址（详见[公网地址覆盖](#public-url-override)部分）。

### 用户名/密码认证提供方（无需 OAuth 身份提供商）

如果您不想配置 OAuth 身份提供商——即采用那种“在控制面板中直接输入密码即可”的自托管部署方式——内置的 `plugins/dashboard_auth/basic` 插件会注册一个名为 `basic` 的 `DashboardAuthProvider`，该提供方通过**用户名和密码**进行认证，而非依赖 OAuth 重定向机制。

它的运行逻辑与 OAuth 提供方相同：服务在非回环地址上启动，登录页面会显示该提供方的凭证输入表单（而非“使用 X 登录”按钮），而登录后的所有流程——会话 Cookie、透明刷新、WS 令牌、登出操作以及审计日志——都与 OAuth 路径完全一致。这些会话是由提供方自行生成的基于 HMAC 签名的无状态令牌，因此**无需数据库，也不依赖外部身份提供商**。密码加密则使用标准库中的 `scrypt` 函数（无需任何第三方依赖）。

:::warning 请仅在可信网络中使用此功能，切勿在公共互联网上使用。  
该用户名/密码提供程序专为运行在**可信网络**上的自托管/本地/家庭实验室控制面板设计，或仅能通过**VPN**访问。它仅用于保护单一共享凭证，不支持外部身份提供商、多因素认证或针对用户的独立账户，因此**不适合将控制面板直接暴露在公共互联网上**。对于面向互联网的控制面板，请改用[Nous Research提供程序](#default-provider-nous-research)（或您自己的[自托管OIDC](#self-hosted-oidc-provider) / [自定义OAuth](#custom-providers)提供程序）。

#### 配置  
与Nous提供程序类似，它也从`config.yaml`（标准配置文件）中读取设置，若环境变量被赋予非空值，则以环境变量为准。只有当同时配置了`username`以及`password_hash`（推荐）或`password`时，该功能才会启用——否则将不会执行任何操作，因此不会影响OAuth用户和回环操作员。

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
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | `dashboard.basic_auth.password` | 以明文形式存储；**其优先级高于配置中的 `password_hash`，便于通过环境变量进行密码轮换** |
| `HERMES_DASHBOARD_BASIC_AUTH_SECRET` | `dashboard.basic_auth.secret` | 用于令牌签名的密钥 |
| `HERMES_DASHBOARD_BASIC_AUTH_TTL_SECONDS` | `dashboard.basic_auth.session_ttl_seconds` | 访问令牌的有效时长 |

:::注意：为确保会话稳定性，请明确设置 `secret` 变量
当 `secret` 为空时，系统会为每个进程生成一个随机签名密钥。这对单个进程而言并无问题，但会导致**每次重启后所有会话失效**，且会话**无法跨多个工作进程延续**。如需实现重启后会话依然有效或支持多工作进程部署，请明确设置 `secret` 变量。
:::

`/auth/password-login` 接口会对每个客户端 IP 设置请求频率限制（默认为每分钟 10 次尝试，超出限制将返回 HTTP 429 错误），并且无论用户身份未知还是密码错误，都会统一返回 `401 Invalid credentials` 错误信息，因此无法用于获取用户名列表。

#### 实际应用示例：用户名/密码认证
只需三步，即可在受信任的网络环境中搭建一个需要密码验证的仪表板。

**1. 在 `~/.hermes/.env` 文件中设置凭据。** 对密码进行哈希处理，以避免明文以原始形式存储，并设置一个稳定的签名密钥，以确保会话在重启后依然有效：

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

**2. 在可访问的地址上运行控制面板。** 通过非回环绑定方式启动网关，再结合用户名与哈希值即可激活 `basic` 提供商：

```bash
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

**3. 登录。** 打开 `http://<host>:9119/`，页面将跳转至 `/login` 页面——这是一个用于输入凭据的表单（而非“使用 X 登录”按钮）。输入 `admin` 及您的密码，即可进入已验证身份的控制面板。您也可以从任何设备上验证该网关功能。

```bash
curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'
# true
# ["basic"]
```

调用 `GET /api/auth/me` 可返回已验证的会话信息（`provider: basic`）。请将此接口置于 VPN 后端使用——请注意上述警告；若使用公共主机，则应改用 [Nous Research](#default-provider-nous-research) 或 [自托管 OIDC](#self-hosted-oidc-provider) 提供商。

#### 自定义密码提供商

`basic` 仅是扩展点的一种实现方式。任何插件均可注册密码提供商：在您的 `DashboardAuthProvider` 子类中设置 `supports_password = True`，并实现 `complete_password_login(*, username, password) -> Session` 方法（验证失败时抛出 `InvalidCredentialsError` 异常，后端存储故障时抛出 `ProviderError` 异常）。对于纯密码型提供商，可将 OAuth 的 `start_login` / `complete_login` 方法保留为 `NotImplementedError` 占位实现。LDAP 绑定、凭证数据库或任何其他非重定向认证方案均适用此路径——框架会为您处理表单、路由、Cookie 以及会话刷新等操作。

### 自托管 OIDC 提供商

如果您自行运行身份验证提供商，内置的 `plugins/dashboard_auth/self_hosted` 插件即可通过**标准的 OpenID Connect** 协议对控制面板进行身份验证——无需为每个身份提供商编写专用代码，也不涉及 Nous Portal。该插件可与任何符合规范的 OIDC 服务器配合使用：

> **Authentik · Keycloak · Zitadel · Authelia · Auth0 · Okta · Google · …**

与 Nous 提供商类似，该插件会在配置完成后自动加载并仅注册一次，因此对于本地回环运行的控制面板而言无需额外操作。

#### 配置说明

需配置**发行方**和**client_id**（即公共 PKCE 客户端，无需客户端密钥）。该插件会从 `{issuer}/.well-known/openid-configuration` 中获取 IDP 的 `authorization_endpoint`、`token_endpoint` 以及 `jwks_uri`，因此您无需硬编码这些端点地址。

**`config.yaml`**——标准配置文件：

```yaml
dashboard:
  oauth:
    provider: self-hosted
    self_hosted:
      issuer: https://auth.example.com/application/o/hermes/   # required
      client_id: hermes-dashboard                              # required
      scopes: "openid profile email"                           # optional (this is the default)
```

**环境变量** — 操作员可覆盖这些值（当设置非空值时，该值将优先于 `config.yaml` 中的配置；空值则视为未设置）：

| 环境变量 | 被覆盖的值 | 备注 |
|---------|-----------|-------|
| `HERMES_DASHBOARD_OIDC_ISSUER` | `dashboard.oauth.self_hosted.issuer` | OIDC 发行方地址 — 必填 |
| `HERMES_DASHBOARD_OIDC_CLIENT_ID` | `dashboard.oauth.self_hosted.client_id` | 公开客户端 ID — 必填 |
| `HERMES_DASHBOARD_OIDC_SCOPES` | `dashboard.oauth.self_hosted.scopes` | 默认值为 `openid profile email` |

请在您的身份提供商中注册一个**公开**的应用程序/客户端，使用授权码 + PKCE（S256）授权模式，并将控制面板的回调地址添加为允许的重定向 URI。回调地址为 `<dashboard public URL>/auth/callback`（有关控制面板如何在代理后获取其公开 URL 的信息，请参阅[公开 URL 覆盖](#public-url-override)部分）。 

#### 验证内容

提供商会根据检测到的 `jwks_uri` 对 OpenID Connect **身份令牌**（RS256/ES256）进行验证，同时确保 `iss` 和 `aud` 字段与您配置的 `issuer` 和 `client_id` 匹配。标准的 OIDC 字段会映射到控制面板的会话信息中：

| 会话字段 | 对应的声明 |
|---------------|------------|
| `user_id` | `sub`（必填） |
| `email` | `email` |
| `display_name` | `name` → `preferred_username` → `nickname` → `email` |
| `org_id` | `org_id` / `organization`，若不存在则使用用户所属的 `groups` |
ID令牌用于确认身份，而访问令牌则被视为不可见数据（OIDC规范并未要求其必须是JWT格式）。端点URL必须使用HTTPS协议（在本地开发环境中，回环地址`http://`是可以接受的），且发现文档中声明的`issuer`值必须与您的配置值一致（允许末尾有斜杠的细微差异）。当身份提供商发行刷新令牌后，可通过标准的`refresh_token`授权机制实现静默式重新认证；而注销操作则会调用身份提供商所声明的RFC 7009标准中的`revocation_endpoint`。

> 目前暂不支持**机密客户端**（即那些拥有`client_secret`的客户端）——建议配置公开型+PKCE客户端，这是面向浏览器的控制台应用的常见选择。

#### 实际案例：Keycloak

[Keycloak](https://www.keycloak.org/)是最适合用于本地测试的自托管OIDC服务器之一——它在开发模式下以单个容器形式运行（采用内存数据库），并提供了标准的OIDC发现功能。通过本指南，您只需几分钟就能从零搭建出一个可正常使用的控制台登录系统。

**1. 使用预配置的领域运行Keycloak。** 将该领域的导出文件保存为`realm-hermes.json`——该文件定义了一个名为`hermes`的领域、一个**公开型PKCE客户端**（`hermes-dashboard`）以及一名测试用户，所有这些内容都会在系统启动时自动导入，因此无需在管理界面进行任何操作：

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

启动它（适用于 Keycloak 26 及更高版本），并将该文件放入导入目录中：

```bash
docker run --rm -p 8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  -v "$PWD/realm-hermes.json:/opt/keycloak/data/import/realm-hermes.json:ro" \
  quay.io/keycloak/keycloak:26.0 \
  start-dev --import-realm
```

一旦部署完成，该领域将会在 `http://localhost:8080/realms/hermes/.well-known/openid-configuration` 地址上公开标准的 OIDC 发现信息（颁发者地址为 `http://localhost:8080/realms/hermes`）。管理控制台则位于 `http://localhost:8080/`，登录账号为 `admin`，密码也为 `admin`。

**2. 将控制面板指向该地址。** 由于该自托管插件支持回环地址类型的颁发者（即 `http://` 开头的地址），因此无需额外配置；而对于非回环地址类型的颁发者，则必须使用 HTTPS，本地部署的 Keycloak 可以直接正常使用。

```bash
export HERMES_DASHBOARD_OIDC_ISSUER="http://localhost:8080/realms/hermes"
export HERMES_DASHBOARD_OIDC_CLIENT_ID="hermes-dashboard"
export HERMES_DASHBOARD_PUBLIC_URL="http://localhost:9119"
hermes dashboard --host 0.0.0.0 --port 9119 --no-open
```

`HERMES_DASHBOARD_PUBLIC_URL` 用于指定仪表板的 OAuth 回调地址为 `http://localhost:9119/auth/callback`，即前述 realm 所注册的重定向 URI。将其绑定到 `0.0.0.0`（非回环地址）即可启用 OAuth 门控功能。

**3. 登录。** 打开 `http://localhost:9119/`，系统会自动跳转至 `/login` 页面。点击 **Sign in with Self-Hosted OIDC**，然后使用账号 `testuser` 和密码 `testpassword` 在 Keycloak 中完成认证，之后便会返回已登录的仪表板页面。侧边栏会显示“通过自托管方式以测试用户身份登录”，而调用 `GET /api/auth/me` 则可以获取到经过验证的会话信息（`provider: self-hosted`，`email: testuser@example.com`）。

> 如果您将服务绑定到其他主机或端口，或是从该地址访问，需在 Keycloak 管理控制台（Clients → hermes-dashboard → Settings）中将该地址的 `…/auth/callback` 添加到客户端的**有效重定向 URI**列表中。Authentik、Zitadel、Authelia 以及其他 OIDC 服务器的处理方式类似，仅发行方 URL 和客户端注册界面有所不同。

### 公开 URL 覆盖

默认情况下，仪表板会根据请求中的信息自行生成 OAuth 回调地址，即 `X-Forwarded-Host`、`X-Forwarded-Proto` 与 `X-Forwarded-Prefix` 的组合（当 uvicorn 配置了 `proxy_headers=True` 时即可实现，而 `start_server` 会在启用门控功能时自动设置该参数）。只要反向代理正确设置了这三个头部信息，此机制即可在其后端直接正常工作。

对于那些无法可靠转发相关请求头的反向代理后的部署环境（如手动配置的 Nginx、本地入口服务器，以及仅部分经过代理链处理的自定义域名部署），请将 `dashboard.public_url`（或 `HERMES_DASHBOARD_PUBLIC_URL`）设置为可访问该控制面板的**完整公共网址**。

```yaml
dashboard:
  public_url: "https://dashboard.example.com/hermes"
  trusted_proxies:
    - "172.20.0.5"
```

一旦设置了该参数，OAuth 回调地址将直接变为 `<public_url>/auth/callback` 的形式——在该处理流程中会忽略 `X-Forwarded-Prefix` 参数，因为操作者已明确指定了公共 URL。这是有意为之：若再叠加前缀，对于那些公共 URL 中已包含前缀的常见情况，就会导致前缀出现重复。

`public_url` 中指定的主机名也会被直接视为有效的 HTTP `Host` 和 WebSocket `Origin` 值。这有助于那些在将请求转发到绑定在 `127.0.0.1` 上的控制面板时仍能保留浏览器可见主机名的反向代理服务器正常工作。该机制不支持通配符或后缀匹配，因此像 `dashboard.example.com.evil.test` 这样的攻击者主机仍会被 DNS 重定向防护机制拦截。

即便后端实际绑定的是回环地址，只要指定了非回环地址的 `public_url`，系统就会启用控制面板身份验证机制。请先配置密码或 OAuth 提供方；若未配置，Hermes 在启动时就会直接失败。这样做是为了防止本地的单页应用会话令牌通过代理服务器变成远程认证手段。在此模式下，Uvicorn 还会启用代理头部处理功能。回环代理服务器则会自动被信任。如果 TLS 终结节点是从其他容器或主机连接的，需将其确切的 IP 地址添加到 `dashboard.trusted_proxies` 中；若地址是动态变化的，则可为其专用代理网络定义一个特定的 CIDR 范围并添加进去。

```yaml
dashboard:
  public_url: "https://dashboard.example.com/hermes"
  trusted_proxies:
    - "172.20.0.0/24"
```

仅列出的对等节点才有权提供 `X-Forwarded-Proto` 和 `X-Forwarded-For` 头信息。Hermes 会始终保留对回环地址的信任机制，因此会拒绝包含 `*`、`0.0.0.0/0` 以及 `::/0` 的地址。若信任某个网络，则意味着该网络上的所有容器或机器均可提供转发元数据，因此建议使用具体的代理 IP 或专用的仅用于代理的网络。

```bash
# Backend remains reachable only on this machine.
hermes dashboard --host 127.0.0.1 --port 9119 --no-open
```

请将 TLS 反向代理指向 `http://127.0.0.1:9119`，并在 `dashboard.public_url` 中使用相同的外部地址。Tailscale Serve 就是这种部署方式的典型示例：它可以在 `https://<machine>.<tailnet>.ts.net` 这一主机名上终止仅支持 tailnet 协议的 HTTPS 流量，同时将请求代理到回环地址上的控制面板。应将该 HTTPS 地址直接设置为 `dashboard.public_url`。由于该地址仍被视为面向浏览器的非回环地址，因此需要配置控制面板的身份验证提供程序；不过这并不要求该服务能被公共互联网访问。

其优先级与其他控制面板设置相同——环境变量优先于 `config.yaml` 中的配置：

| 设置位置 | 覆盖路径 | 适用场景 |
|---------|---------------|----------|
| `config.yaml` 中的 `dashboard.public_url` | `HERMES_DASHBOARD_PUBLIC_URL` | 本地开发/本地部署（标准方式） |
| 环境变量 `HERMES_DASHBOARD_PUBLIC_URL` | — | 托管平台密钥/CI 环境 |
| 未设置 | — | 默认值——根据 `X-Forwarded-*` 请求头自动重建 |

系统会拒绝那些缺少 `http://`/`https://` 协议、没有主机名，或包含引号、尖括号、空白字符及控制字符的无效值。对于格式错误的值，系统会默认尝试通过请求头信息进行重建，从而确保登录流程正常运行，而不会将用户引导至危险的网址。

> **注意：** `public_url` 仅用于覆盖 OAuth 回调地址。`Secure` Cookie 标志仍由 `request.url.scheme` 控制，仅在连接方为回环地址或被列入 `trusted_proxies` 列表时才会使用 `X-Forwarded-Proto`。若代理地址并非回环地址，则需将 HTTPS `public_url` 与 TLS 终止机制结合使用，并设置受限的 trusted-proxy 条目。

### OAuth 流程

服务提供商需实现 [Nous Portal OAuth 合约 v1](https://github.com/NousResearch/nous-account-service/blob/main/docs/agent-dashboard-oauth-contract.md)——基于 PKCE（S256）的授权码模式：

1. 用户在未携带会话 Cookie 的状态下访问 `/`，网关会将其重定向至 `/login`。
2. 登录页面会显示“使用 Nous Research 继续登录”按钮，链接为 `/auth/login?provider=nous`。
3. 服务器将 PKCE 状态信息存储在短生命周期的 Cookie 中，然后将用户重定向至 `https://portal.nousresearch.com/oauth/authorize?…`。
4. 用户在 Portal 上完成身份验证后，会被引导至 `/auth/callback?code=…&state=…`。
5. 服务器通过 `POST /api/oauth/token` 接口将授权码换算为访问令牌，同时根据 Portal 的 JWKS 文件（`/.well-known/jwks.json`）验证 JWT 签名，最后设置 `hermes_session_at` Cookie。
6. 用户将被重定向回 `/`（或通过 `next=` 查询参数返回原来的深度链接路径）。

访问令牌的有效期为 15 分钟。**合约 v1 中不支持刷新令牌**——当令牌过期时，单页应用中的请求封装层会检测到 401 错误响应，进而全页跳转回 `/login` 以重新执行登录流程。

### 设置的 Cookie

| 名称 | 生命周期 | 备注 |
|------|----------|-------|
| `hermes_session_at` | 令牌有效期（15分钟） | 属性为HttpOnly，SameSite=Lax，仅在HTTPS环境下启用Secure属性 |
| `hermes_session_pkce` | 10分钟 | 属性为HttpOnly；在请求往返过程中用于存储PKCE验证器及提供方相关提示信息。在HTTPS环境下SameSite属性设置为None且需启用Secure属性——此类cookie必须能够穿越跨站IDP重定向链（因为Chromium会在跨站重定向链中的302响应中丢弃SameSite=Lax属性的cookie）；在本地回环HTTP请求中则设置为SameSite=Lax |
| `hermes_session_rt` | v1版本中未使用 | 为未来兼容性预留，当`refresh_token`为空时不会写入该cookie |

上述三个cookie的路径均为`Path=/`。所有会话cookie的SameSite属性均为Lax；而PKCE cookie在通过HTTPS设置时SameSite属性为None（详见表格）。当通过HTTPS访问控制面板时，系统会设置Secure属性——该判断依据是请求URL的协议类型；在`proxy_headers=True`配置下，也会尊重上游TLS终止节点传递的`X-Forwarded-Proto`头部信息。

### 登出

侧边栏组件会显示“当前以<user_id…>身份通过Nous登录”，并配有登出图标。点击该图标后会发送 `/auth/logout` 请求，该请求会清除所有与控制面板相关的认证cookie，并将用户重定向回 `/login` 页面。

### 审计日志

每次登录尝试、登录成功/失败以及会话验证失败的情况，都会以JSON格式记录到 `$HERMES_HOME/logs/dashboard-auth.log` 文件中。在记录之前，敏感字段（如`access_token`、`refresh_token`、`code`、`code_verifier`、`state`以及`Authorization`请求头）会被进行脱敏处理。

### 自定义提供方

若需接入非Nous OAuth的提供方（例如Google、GitHub或自定义OIDC服务），可创建一个插件并注册 `DashboardAuthProvider` 类：

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

### 非交互式（Bearer令牌）认证

除了基于人类用户的交互式登录方式（会话Cookie+刷新机制）之外，`DashboardAuthProvider` ABC 还支持通过设置 `supports_token = True` 和 `verify_token(token=...)` 来实现**非交互式的服务间通信**功能。当某个提供方启用此功能后，系统会对传入的 `Authorization: Bearer <token>` 令牌进行验证；验证成功后，该提供方指定的支持令牌认证的端点将会在请求中附加一个 `TokenPrincipal` 对象（位于 `request.state.token_principal` 中），从而实现无需Cookie、无需重定向且无需刷新的认证流程。

默认内置的第一个消费者就是 **drain** 提供方（位于 `plugins/dashboard_auth/drain`）：`nous-account-service` 会通过 `HERMES_DASHBOARD_DRAIN_SECRET` 为每个Agent生成专用密钥，该提供方会使用恒定时间比较算法来验证传入的Bearer令牌，并将 `/api/gateway/drain` 端点标记为支持令牌认证。如果密钥强度不足或长度过短（小于256位），注册过程将会直接失败，相关端点也将保持禁用状态；而当该环境变量未被设置时，此功能则不会生效。相关的配置选项（如 `scope`、`min_secret_chars`）位于 `config.yaml` 文件的 `dashboard.drain_auth` 部分。

自定义提供方也可以采用相同的方式实现 `supports_token`/`verify_token` 功能，以此开放自己支持机器端认证的端点。

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

控制面板中的 React StatusPage 在“Web server”选项下显示相同的字段。一旦完成登录，侧边栏中的 AuthWidget 会展示当前的登录身份。

## 将 Hermes Desktop 连接到远程后端

Hermes Desktop 可以驱动运行在另一台机器上的 Hermes 后端（如 VPS、家庭服务器，或通过 Tailscale 连接的 Mini）。在应用程序中，该功能位于 **Settings → Gateways → Remote gateway**，需要输入**远程 URL**以及登录方式。（关于桌面应用本身的安装、设置及聊天功能，请参阅 [Hermes Desktop](/user-guide/desktop) 页面。）

您可以使用随附的认证提供程序之一来保护远程控制面板，而桌面应用则会根据后端所指定的认证方式完成登录。对于位于您本地机器之外的后端——例如 VPS、公共主机或任何面向互联网的设备——推荐的认证提供程序是 **OAuth (Nous Portal)**（可通过 [`hermes dashboard register`](#registering-a-dashboard) 进行注册，然后使用“Sign in with Nous Research”进行登录）。当后端位于可信的局域网内或仅能通过 VPN 访问时，随附的 [用户名/密码认证提供程序](#usernamepassword-provider-no-oauth-idp) 是最快捷的选择，但**不适用于直接暴露在公共互联网上**。将控制面板绑定到非回环地址后，其认证网关便会启动；一旦完成登录，桌面应用会自动复用该会话用于聊天 WebSocket，无需手动复制或粘贴令牌。

下面的配置方案采用了用户名/密码认证方式，因为在可信网络环境中这种方式能最快完成部署；如需了解 OAuth 认证方式，请参阅[默认提供商：Nous Research](#default-provider-nous-research)。

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

不想以明文形式存储凭证？可使用 `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` 并配合 scrypt 哈希算法——更多详细信息请参阅[用户名/密码提供程序](#usernamepassword-provider-no-oauth-idp)。

若将控制面板作为 systemd 服务运行，当服务配置了 `EnvironmentFile=%h/.hermes/.env` 时，`~/.hermes/.env` 文件会自动被读取，因此启动时凭证便已存在于环境变量中。

:::warning
控制面板会读取和写入您的 `.env` 文件（其中包含 API 密钥及敏感信息），同时还能执行代理命令。此处介绍的**用户名/密码**设置仅适用于可信网络环境——切勿将受密码保护的控制面板直接暴露在公网上，应通过 VPN 进行隔离。[Tailscale](https://tailscale.com/) 是一种理想的解决方案：通过 `--host <tailscale-ip>` 参数绑定到设备的 Tailscale IP 地址，并将 `http://<tailscale-ip>:9119` 设置为远程地址，这样只有同属 Tailscale 网络的设备才能访问该控制面板。若需通过公网访问后端服务，则应改用**OAuth (Nous Portal)** 提供程序。
:::

### 在 Hermes Desktop 中

**设置 → 网关 → 远程网关：**

- **远程地址** — `http://<backend-host>:9119`（若在前面配置了反向代理，也可使用如 `/hermes` 这样的路径前缀）
- **登录** — 应用程序会自动识别用户名/密码类型的网关，并显示“登录”按钮；点击该按钮后输入第一步中设置的凭证即可
- **保存并重新连接** — 该操作会将桌面界面切换到远程后端上
如果在后端设置了 `HERMES_DASHBOARD_BASIC_AUTH_SECRET`，则会自动刷新会话，并在系统重启后依然保持有效。

### 环境变量覆盖

您无需通过应用内的设置进行配置，也可在启动桌面端之前，通过环境变量指定对应的后端地址。一旦设置了 `HERMES_DESKTOP_REMOTE_URL`，该值就会覆盖应用内保存的地址（此时“网关设置”面板会显示“环境变量覆盖”标识，且无法编辑）；您仍需在该面板中使用用户名和密码进行**登录**。

| 环境变量 | 值 |
|---------|-------|
| `HERMES_DESKTOP_REMOTE_URL` | `http://<backend-host>:9119` |

### 故障排除 |

- **“远程网关信息不完整”** —— 说明您尚未输入远程 URL。  
- **登录失败，返回 401 错误或“凭证无效”** —— 用户名或密码与后端的 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` 不匹配。对于未知用户或错误密码的情况，后端会返回相同的通用错误信息，因此请务必核对这两项内容。可通过命令 `curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'` 来确认网关状态，正常情况下该命令应输出 `true` 且包含 `"basic"`。  
- **没有“登录”按钮，而是要求输入会话令牌** —— 说明用户名/密码认证方式未被启用（执行 `/api/status` 后列表中不会出现 `"basic"`）。请确保已设置用户名及密码（或密码哈希值），并且控制台进程已加载这些信息。  
- **每次重启后都会自动登出** —— 请将 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 设置为一个固定值；否则系统会在每次启动时重新生成签名密钥。  
- **连接被拒绝/超时** —— 可能是因为后端绑定到了默认地址 `127.0.0.1`，而非可访问的地址；或是防火墙/VPN阻断了相应端口。建议将绑定地址改为 `0.0.0.0` 或 tailscale IP，并在可信网络中开放该端口。  

## CORS 支持

Web 服务器仅允许来自以下本地地址的 CORS 请求：

- `http://localhost:9119` / `http://127.0.0.1:9119`（生产环境）  
- `http://localhost:3000` / `http://127.0.0.1:3000`  
- `http://localhost:5173` / `http://127.0.0.1:5173`（Vite 开发服务器）  

如果您在自定义端口上运行服务器，该端口地址会自动被添加到允许列表中。  

## 开发相关说明

如果您正在为网页控制台前端功能做贡献：

```bash
# Terminal 1: start the backend API
hermes dashboard --no-open

# Terminal 2: start the Vite dev server with HMR
cd web/
npm install
npm run dev
```

位于 `http://localhost:5173` 的 Vite 开发服务器会将 `/api` 路由的请求转发至位于 `http://127.0.0.1:9119` 的 FastAPI 后端。

前端应用基于 React 19、TypeScript、Tailwind CSS v4 以及 shadcn/ui 风格的组件构建。生产环境构建后的代码会输出到 `hermes_cli/web_dist/` 目录，由 FastAPI 服务器作为静态单页应用来提供服务。

## 更新时自动重新构建

运行 `hermes update` 命令后，若系统中安装了 `npm`，前端应用将会自动重新构建，从而确保控制面板与代码更新保持同步。如果未安装 `npm`，则更新过程会跳过前端构建，`hermes dashboard` 会在首次启动时进行构建。

## 主题与插件

该控制面板预置了八种内置主题，同时支持通过用户自定义主题、插件标签页以及后端 API 路由进行扩展——所有这些功能均可直接使用，无需克隆仓库。

您可以通过顶部的标题栏**实时切换主题**：点击语言切换器旁边的调色板图标即可。所选主题会保存在 `config.yaml` 文件的 `dashboard.theme` 字段中，并在页面加载时自动恢复。

您还可以通过同一选择器**单独更改字体**：主题列表下方的“字体”选项可以覆盖当前主题的界面字体设置。此设置会在不同主题之间保持不变（存储于 `config.yaml` 的 `dashboard.font` 字段中）；若选择“主题默认值”，则可清除该设置并恢复为当前主题本身的字体。

内置主题：

| 主题 | 风格特点 |
|-------|-----------|
| **Hermes Teal**（`default`） | 深青色搭配奶油色，使用系统字体，布局间距舒适 |
| **Hermes Teal (Large)**（`default-large`） | 与默认主题相同，但文字大小为18px，布局间距更宽 |
| **Nous Blue**（`nous-blue`） | 采用Nous品牌蓝色作为点缀元素，布局显得更为宽敞 |
| **Midnight**（`midnight`） | 深蓝紫色色调，搭配Inter与JetBrains Mono字体 |
| **Ember**（`ember`） | 温暖的深红色与青铜色相结合，使用Spectral衬线字体与IBM Plex Mono字体 |
| **Mono**（`mono`） | 灰度风格，采用IBM Plex字体，布局紧凑 |
| **Cyberpunk**（`cyberpunk`） | 黑底霓虹绿配色，使用Share Tech Mono字体 |
| **Rosé**（`rose`） | 粉色与象牙白相配，采用Fraunces衬线字体，布局空间充裕 |

如需创建自定义主题，可通过添加插件标签页、注入到Shell插槽中，或暴露特定于插件的REST接口来实现。详细指南请参阅**[扩展控制面板](./extending-the-dashboard)**，该指南涵盖了以下内容：

- 主题YAML结构——包括配色方案、字体设置、布局设计、资源文件、componentStyles、colorOverrides以及customCSS配置
- 不同布局样式——`standard`、`cockpit`、`tiled`
- 插件清单、SDK、Shell插槽、页面级插槽（可在不覆盖原有内容的情况下将组件注入到内置页面中），以及后端FastAPI接口
- 一个完整的主题与插件结合使用示例（Strike Freedom控制台演示）
- 主题的发现、重新加载及故障排查方法 |
