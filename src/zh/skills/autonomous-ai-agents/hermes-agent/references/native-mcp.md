# 原生 MCP 客户端

Hermes Agent 内置了 MCP 客户端，该客户端会在启动时连接到 MCP 服务器，发现这些服务器提供的工具，并将其作为代理可直接调用的标准工具呈现。无需使用任何桥接 CLI——MCP 服务器提供的工具会与 `terminal`、`read_file` 等内置工具一同出现。

## 适用场景

在以下情况下可使用此功能：
- 连接到 MCP 服务器并在 Hermes Agent 内部使用其提供的工具
- 通过 MCP 添加外部功能（如文件系统访问、GitHub、数据库、API 等）
- 运行基于本地标准输入输出的 MCP 服务器（如 npx、uvx 或其他命令）
- 连接到远程的 HTTP/StreamableHTTP MCP 服务器
- 实现 MCP 工具在每次对话中自动被发现并可用

如果仅需在终端中临时调用 MCP 工具且无需进行任何配置，建议使用 `mcporter` 技能。

## 先决条件

- **mcp Python 包**——可选依赖项，可通过 `pip install mcp` 安装。若未安装，MCP 功能将默认被禁用。
- **Node.js**——基于 `npx` 的 MCP 服务器（大多数社区服务器）所需。
- **uv**——基于 `uvx` 的 MCP 服务器（Python 编写的服务器）所需。

请先安装 MCP SDK：

```bash
pip install mcp
# or, if using uv:
uv pip install mcp
```

## 快速入门

在 `~/.hermes/config.yaml` 文件的 `mcp_servers` 键下添加 MCP 服务器：

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

请重启 Hermes Agent。在启动后，它将执行以下操作：
1. 连接到服务器
2. 探索可用的工具
3. 使用前缀 `mcp_time_*` 对这些工具进行注册
4. 将它们注入到所有平台工具集中

之后您就可以像平常一样使用这些工具了——只需让代理帮忙获取当前时间即可。

## 配置参考

`mcp_servers` 下的每个条目都是一个服务器名称及其对应配置的映射。传输方式有两种：**stdio**（基于命令）和 **HTTP**（基于 URL）。

### Stdio 传输方式（命令 + 参数）

```yaml
mcp_servers:
  server_name:
    command: "npx"             # (required) executable to run
    args: ["-y", "pkg-name"]   # (optional) command arguments, default: []
    env:                       # (optional) environment variables for the subprocess
      SOME_API_KEY: "value"
    timeout: 120               # (optional) per-tool-call timeout in seconds, default: 120
    connect_timeout: 60        # (optional) initial connection timeout in seconds, default: 60
```

### HTTP传输协议（URL）

```yaml
mcp_servers:
  server_name:
    url: "https://my-server.example.com/mcp"   # (required) server URL
    headers:                                     # (optional) HTTP headers
      Authorization: "Bearer sk-..."
    timeout: 180               # (optional) per-tool-call timeout in seconds, default: 120
    connect_timeout: 60        # (optional) initial connection timeout in seconds, default: 60
```

### 所有配置选项

| 选项             | 类型   | 默认值 | 描述                                               |
|------------------|--------|---------|---------------------------------------------------|
| `command`         | 字符串 | --      | 需要运行的可执行文件（采用标准输入输出传输方式）     |
| `args`            | 列表   | `[]`    | 传递给该命令的参数                                 |
| `env`             | 字典   | `{}`    | 传递给子进程的额外环境变量                       |
| `url`             | 字符串 | --      | 服务器地址（采用HTTP传输方式，为必填项）           |
| `headers`         | 字典   | `{}`    | 每次请求时附带的HTTP头部信息                     |
| `timeout`         | 整数   | `120`   | 每次工具调用的超时时间（以秒为单位）               |
| `connect_timeout` | 整数   | `60`    | 初始连接及服务发现阶段的超时时间                   |

注意：服务器配置必须仅包含 `command`（标准输入输出方式）或 `url`（HTTP方式），不可同时存在。

## 工作原理

### 启动时的服务发现

当Hermes Agent启动时，会在工具初始化阶段调用 `discover_mcp_tools()` 函数：

1. 从 `~/.hermes/config.yaml` 文件中读取 `mcp_servers` 配置；
2. 对每个服务器，在独立的后台事件循环中建立连接；
3. 初始化MCP会话，并通过调用 `list_tools()` 函数来发现可用的工具；
4. 将每个工具注册到Hermes工具注册表中。

### 工具命名规则

MCP工具的注册遵循以下命名规范：

```
mcp_{server_name}_{tool_name}
```

为确保与 LLM API 兼容，名称中的连字符和点号会被替换为下划线。

示例：
- 服务器 `filesystem`，工具 `read_file` → `mcp_filesystem_read_file`
- 服务器 `github`，工具 `list-issues` → `mcp_github_list_issues`
- 服务器 `my-api`，工具 `fetch.data` → `mcp_my_api_fetch_data`

### 自动注入功能

在检测到相关工具后，MCP 工具会自动被注入到所有的 `hermes-*` 平台工具集中（包括 CLI、Discord、Telegram 等）。这意味着无需任何额外配置，即可在所有对话中使用这些 MCP 工具。

### 连接生命周期

- 每个服务器作为长期运行的 asyncio 任务，在后台守护线程中执行
- 连接会在代理进程的整个运行期间保持有效
- 若连接中断，系统会自动进行重连，并采用指数退避策略（最多尝试 5 次，每次等待时间最长为 60 秒）
- 当代理进程关闭时，所有连接都会被有序断开

### 可重试性

`discover_mcp_tools()` 函数具有可重试性——多次调用该函数仅会对尚未建立连接的服务器进行尝试。对于连接失败的服务器，系统会在后续调用中再次尝试。

## 传输类型

### 标准输入/输出传输

这是最常用的传输方式。Hermes 会以子进程的形式启动 MCP 服务器，并通过标准输入/输出进行通信。

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

该子进程会继承一个经过**过滤**后的环境变量（详情请参见下文的安全性说明），同时还会包含你在 `env` 中指定的所有变量。

### HTTP / StreamableHTTP 传输方式

适用于远程或共享的 MCP 服务器。此方式要求 `mcp` 包具备 HTTP 客户端支持功能（即 `mcp.client.streamable_http`）。

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer sk-..."
```

如果您所安装的 `mcp` 版本不支持 HTTP 功能，服务器将会因 `ImportError` 错误而崩溃，而其他服务器则可正常运行。

## 安全性

### 环境变量过滤

对于标准输入/输出类型的服务器，Hermes 不会将完整的 Shell 环境传递给 MCP 子进程。仅会继承一些安全的基线变量：

- `PATH`、`HOME`、`USER`、`LANG`、`LC_ALL`、`TERM`、`SHELL`、`TMPDIR`
- 所有的 `XDG_*` 变量

除非您通过 `env` 配置键明确添加，否则所有其他环境变量（如 API 密钥、令牌和机密信息）均会被排除在外。这样一来即可防止凭证意外泄露给不可信的 MCP 服务器。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      # Only this token is passed to the subprocess
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_..."
```

### 错误信息中的凭证信息脱敏

如果 MCP 工具调用失败，错误信息中任何类似凭证的格式内容都会在呈现给大语言模型之前被自动遮蔽。这包括：

- GitHub PATs（`ghp_...`）
- OpenAI 风格的密钥（`sk-...`）
- 承载令牌
- 通用的 `token=`、`key=`、`API_KEY=`、`password=`、`secret=` 格式

## 故障排除

### “未找到 MCP SDK——跳过 MCP 工具检测”

说明未安装 `mcp` Python 包。请先进行安装：

```bash
pip install mcp
```

### “未配置 MCP 服务器”

在 `~/.hermes/config.yaml` 文件中不存在 `mcp_servers` 键，或该键的值为空。请至少添加一个服务器。

### “无法连接到 MCP 服务器 ‘X’”

常见原因：
- **命令未找到**：`command` 可执行文件不在系统路径中。请确保已安装 `npx`、`uvx` 或相应的命令。
- **包未找到**：对于通过 npx 启动的服务器，对应的 npm 包可能不存在，或者需要在使用时添加 `-y` 参数以自动安装。
- **超时**：服务器启动耗时过长。请增大 `connect_timeout` 的值。
- **端口冲突**：对于 HTTP 服务器，可能无法访问该 URL。

### “MCP 服务器 ‘X’ 需要使用 HTTP 协议传输，但当前版本不支持 mcp.client.streamable_http”

您当前的 `mcp` 包版本不包含 HTTP 客户端功能。请升级该包版本：

```bash
pip install --upgrade mcp
```

### 工具未显示

- 确认服务器已列在 `mcp_servers` 下（而非 `mcp` 或 `servers`）。
- 检查 YAML 缩进是否正确。
- 查看 Hermes Agent 的启动日志中的连接相关信息。
- 工具名称前会带有 `mcp_{server}_{tool}` 前缀——请留意该格式。

### 连接持续中断

客户端会以指数退避策略最多重试 5 次（时间间隔分别为 1 秒、2 秒、4 秒、8 秒、16 秒，最长不超过 60 秒）。如果服务器根本无法访问，客户端将在 5 次尝试后放弃。请检查服务器进程及网络连接状况。

## 示例

### 时间服务器（uvx）

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

注册诸如 `mcp_time_get_current_time` 这样的工具。

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/documents"]
    timeout: 30
```

注册诸如 `mcp_filesystem_read_file`、`mcp_filesystem_write_file`、`mcp_filesystem_list_directory` 等工具。

### 已启用身份验证的 GitHub 服务器

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"
    timeout: 60
```

注册诸如 `mcp_github_list_issues`、`mcp_github_create_pull_request` 等工具。 

### 远程 HTTP 服务器

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.mycompany.com/v1/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
      X-Team-Id: "engineering"
    timeout: 180
    connect_timeout: 30
```

### 多服务器配置

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]

  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"

  company_api:
    url: "https://mcp.internal.company.com/mcp"
    headers:
      Authorization: "Bearer sk-xxxxxxxxxxxxxxxxxxxx"
    timeout: 300
```

所有服务器上的工具均已完成注册，可同时使用。为避免冲突，每台服务器上的工具前都会加上该服务器的名称作为前缀。

## 抽样机制（由服务器发起的LLM请求）

Hermes支持MCP的`sampling/createMessage`功能——MCP服务器可在工具执行过程中通过代理向LLM请求内容补全。这便实现了“代理参与循环”的工作流程（如数据分析、内容生成、决策制定等）。

抽样机制**默认处于开启状态**，具体配置可针对每台服务器单独设置：

```yaml
mcp_servers:
  my_server:
    command: "npx"
    args: ["-y", "my-mcp-server"]
    sampling:
      enabled: true           # default: true
      model: "gemini-3-flash" # model override (optional)
      max_tokens_cap: 4096    # max tokens per request
      timeout: 30             # LLM call timeout (seconds)
      max_rpm: 10             # max requests per minute
      allowed_models: []      # model whitelist (empty = all)
      max_tool_rounds: 5      # tool loop limit (0 = disable)
      log_level: "info"       # audit verbosity
```

在支持多轮工具增强型工作流的采样请求中，服务器还可以包含 `tools` 参数。`max_tool_rounds` 配置项可用于防止工具调用陷入无限循环。通过 `get_mcp_status()` 可以追踪每台服务器的审计指标，包括请求数、错误数、Token 使用量以及工具调用次数。

对于不可信的服务器，可通过设置 `sampling: { enabled: false }` 来禁用采样功能。

## 备注

- 从智能体的视角来看，MCP 工具是同步调用的，但实际上是在专用的后台事件循环中异步运行的。
- 工具的返回结果为 JSON 格式，内容为 `{"result": "..."}` 或 `{"error": "..."}`。
- 原生的 MCP 客户端与 `mcporter` 是相互独立的——两者可以同时使用。
- 服务器连接是持久化的，在同一智能体进程内的所有对话之间会共享这些连接。
- 要添加或删除服务器，需要重启智能体（目前不支持热重载功能）。
