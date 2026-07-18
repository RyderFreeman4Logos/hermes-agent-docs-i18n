---
sidebar_position: 4
title: "MCP (Model Context Protocol)"
description: "Connect Hermes Agent to external tool servers via MCP — and control exactly which MCP tools Hermes loads"
---

# MCP（模型上下文协议）

MCP使Hermes Agent能够连接到外部工具服务器，从而让Agent可以使用Hermes本身之外的工具——如GitHub、数据库、文件系统、浏览器环境、内部API等等。

如果您希望Hermes使用其他地方已有的工具，MCP通常是实现这一目标的最佳方式。

## MCP带来的优势

- 无需先编写专用的Hermes工具，即可接入外部工具生态系统
- 同一配置文件中可同时使用本地stdio服务器和远程HTTP MCP服务器
- 启动时自动发现并注册工具
- 在服务器支持的情况下，为MCP资源及提示语提供便捷的封装功能
- 支持按服务器进行过滤，仅暴露您希望Hermes使用的MCP工具

## 快速入门

1. 标准安装版本已内置MCP支持，无需额外操作。

2. 在`~/.hermes/config.yaml`文件中添加MCP服务器配置：

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

3. 启动 Hermes：

```bash
hermes chat
```

4. 要求 Hermes 使用基于 MCP 的功能。

例如：

```text
List the files in /home/user/projects and summarize the repo structure.
```

Hermes会自动发现MCP服务器中的各类工具，并像使用其他普通工具一样将其调用。

## 工具目录：一键安装Nous认证的MCP服务

Hermes内置了一个精心筛选的工具目录，其中收录的所有MCP服务器均经过Nous团队的审核与整合。这些服务默认处于禁用状态——请仅安装您真正需要的工具。

```bash
hermes mcp                # interactive picker (default)
hermes mcp catalog        # plain-text list, scriptable
hermes mcp install n8n    # install a catalog entry by name
```

选择器会显示每项内容及其当前状态：

```
n8n          available              Manage and inspect n8n workflows from Hermes
linear       enabled                Linear issue/project management (remote OAuth)
github       installed (disabled)   GitHub repo + PR tools
```

在对应行按下 `Enter` 键即可进行安装（同时会提示输入所需的凭据），或对已安装的工具进行启用、禁用或卸载操作。目录条目存储在 hermes-agent 仓库的 `optional-mcps/` 目录下——若该目录中存在相关条目，即表示已获得 Nous 的批准。该系统不设社区提交层级，所有条目均需通过合并 Pull Request 的方式添加。

目录条目可能需要以下凭据：

- **API 密钥**——安装时会由 Hermes 提示输入，并将密钥值写入 `~/.hermes/.env` 文件中。非敏感信息（如基础 URL）也会存储在同一文件里。
- **OAuth**（远程 MCP）——在配置文件中以 `auth: oauth` 的形式指定；首次连接时，MCP 客户端会自动打开浏览器。
- **OAuth**（如 Google/GitHub 等第三方提供商）——若尚未完成认证，Hermes 会提示您执行 `hermes auth <provider>` 命令进行登录。

### 安装时的工具选择

配置完凭据后，Hermes 会探测 MCP 服务器，列出其提供的所有工具，并显示相应的选项清单：

```
Select tools for 'linear' (SPACE toggle, ENTER confirm)
  [x] find_issues       Find issues matching a query
  [x] get_issue         Get a single issue
  [x] create_issue      Create a new issue
  [ ] delete_workspace  Delete a Linear workspace
  ...
```

已预选中的行来自以下来源：

1. **您之前的选择**：如果您之前已安装过该条目，系统会保留之前的选择——重新安装时不会覆盖原有设置，因为清单文件中的默认值不会取代它们；
2. **清单文件中的 `tools.default_enabled` 设置**：如果该条目指定了默认启用的工具，系统会依据此设置进行筛选（某些目录条目会预先排除那些会修改配置或很少使用的工具）；
3. **全部选项**：若上述两种情况均不适用，则所有工具都会被选中。

按下回车键即可提交选中的工具列表。最终只有被选中的工具才会被写入 `mcp_servers.<name>.tools.include` 文件中。如果您选择全部工具，则不会生成任何过滤规则（这样配置最为简洁，行为也与之前一致）。

**如果检测失败**（例如服务器无法访问、OAuth认证尚未完成，或后端服务未运行），安装仍会成功：系统会直接应用清单文件中指定的 `tools.default_enabled` 设置（若有该设置），否则则不生成任何过滤规则。待服务器可访问后，可再次运行 `hermes mcp configure <name>` 命令进行优化。

### 信任模型

安装目录条目时，系统会按照清单文件中的指定内容执行操作——包括执行 `git clone` 命令、条目中的 `bootstrap` 命令（如 `pip install`、`npm install` 等），最终还会运行 MCP 服务器自身的代码。由于清单文件在加入 hermes-agent 仓库之前需经过代码审查，因此 Nous 已在每个条目发布前对其进行了审核——**但您仍应在安装前仔细阅读清单文件**，尤其是 `source:` 字段中指定的仓库地址、`install.bootstrap:` 命令，以及任何 `transport.command:` 调用内容。

清单文件存储在 GitHub 的 [`optional-mcps/<name>/manifest.yaml`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps) 地址下。在安装过程中，选择工具的工具也会显示清单文件中的 `source:` URL，方便您快速验证上游仓库信息。Web 控制台的 MCP 页面会展示每个目录条目的详细信息——包括传输方式、认证类型、端点地址（HTTP 格式）或命令及参数（标准输入/输出格式）、Git 安装的源代码/引用地址及 bootstrap 命令，以及相关设置说明——其中 `source:` 字段会以可点击链接的形式呈现，让您在点击“安装”之前就能清楚了解该条目将连接到何处或运行什么程序。

### 清单文件版本兼容性

清单文件会指定一个 `manifest_version` 版本。该目录系统具备向前兼容性：如果某个提交添加的条目所使用的 `manifest_version` 版本高于您当前安装的 Hermes 版本，工具选择器会针对该条目显示警告信息（`⚠ '<name>' requires a newer Hermes`），而不会直接隐藏它。看到此类警告时，请运行 `hermes update` 命令来安装最新版本的 Hermes。

### 运行时 `${ENV_VAR}` 变量替换

在条目的 `transport.command`、`transport.args`、`transport.url` 和 `headers` 字段中，`${VAR}` 占位符会在服务器连接时根据环境变量进行替换（这些环境变量包括 `~/.hermes/.env` 文件中的所有内容）。当某个目录条目需要引用用户在其他地方配置的值时，这一功能非常有用——例如 `${HOME}/foo` 或 `${MY_PROVIDER_TOKEN}`。

需注意，这与目录清单文件中的 `${INSTALL_DIR}` 是不同的，后者会在安装时被替换为目录条目所对应的仓库克隆路径。

### 后续更新工具选择

```bash
hermes mcp configure linear
```

重新打开同一份检查表，且您当前选中的选项会自动被勾选。当您希望启用更多工具，或服务器新增了您想使用的工具时，可使用此功能。

### 更新目录清单

MCP 本身不会自动更新。如果清单版本发生了变化，在 Hermes 更新后，请重新运行 `hermes mcp install <name>` 以刷新内容。

若要将某个 MCP 添加到目录中，请针对 [`optional-mcps/`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps) 提交一个 Pull Request。

## 两种类型的 MCP 服务器

### Stdio 服务器

Stdio 服务器作为本地子进程运行，通过标准输入/输出进行通信。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
```

在以下情况下，请使用标准输入输出服务器：
- 服务器已安装在本地；
- 您需要低延迟地访问本地资源；
- 您遵循的 MCP 服务器文档中明确说明了 `command`、`args` 和 `env` 参数。

### HTTP 服务器

HTTP MCP 服务器是 Hermes 直接连接的远程端点。

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ***"
```

在以下情况下可使用 HTTP 服务器：
- MCP 服务器托管在其他位置
- 您的组织需公开内部 MCP 端点
- 您不希望 Hermes 为该集成启动本地子进程

### 经 OAuth 鉴权的 HTTP 服务器

大多数托管型 MCP 服务器（如 Linear、Sentry、Atlassian、Asana、Figma、Stripe 等）要求使用 OAuth 2.1 而非静态承载令牌。只需设置 `auth: oauth`，Hermes 就会通过 MCP Python SDK 自动处理端点发现、动态客户端注册、PKCE、令牌交换、刷新以及升级式认证等流程。

```yaml
mcp_servers:
  linear:
    url: "https://mcp.linear.app/mcp"
    auth: oauth
```

首次连接时，Hermes会输出授权URL，并在可能的情况下自动打开您的浏览器，同时在本地回环端口等待OAuth回调。令牌会被缓存于`~/.hermes/mcp-tokens/<server>.json`文件中，权限设置为0o600；后续运行时会自动重用这些令牌，直到刷新失败为止。

**远程/无界面主机环境。** 当Hermes在不同于浏览器的机器上运行时，回环回调无法连接到您的笔记本电脑。此时可通过以下两种方式完成授权流程：

- **直接粘贴（无需额外设置）：** 在交互式终端中，Hermes会在授权URL旁显示“或在此处粘贴重定向URL……”的提示。打开该URL进行授权，复制浏览器最终跳转到的完整地址（由于会出现连接错误，这是正常现象），然后将其粘贴到提示框中。仅包含`?code=…&state=…`参数的查询字符串也同样适用。
- **SSH端口转发：** 在另一个终端中执行命令`ssh -N -L <port>:127.0.0.1:<port> user@host`，之后即可让正常的重定向流程继续进行。
- **代理回调（`redirect_uri`）：** 如果有公共HTTPS端点负责将请求转发到目标主机（例如Tailscale Funnel或指向回调端口的反向代理），只需设置`oauth.redirect_uri`，浏览器便会自动将用户重定向至Hermes，无需任何隧道连接或手动粘贴操作。

```yaml
mcp_servers:
  myserver:
    url: "https://mcp.example.com/mcp"
    auth: oauth
    oauth:
      redirect_port: 8765                                # fixed port for the proxy to target
      redirect_uri: "https://oauth.example.ts.net/callback"
```

对于完全无界面的网关（即仅作为消息机器人，完全没有交互式终端），可选的 [`mcp-oauth-remote-gateway` 技能](../skills/optional/mcp/mcp-mcp-oauth-remote-gateway.md)会引导智能体手动完成相关流程，并在Hermes要求的位置填写令牌。

**注意事项——WAF会拒绝`127.0.0.1`格式的重定向URI。**部分服务提供商在其授权服务器前部署了WAF，这类WAF会拦截查询字符串中包含`127.0.0.1`的任何授权请求（Reclaim.ai的AWS API Gateway就是典型例子——所有尝试在到达OAuth应用之前都会返回`{"message":"Forbidden"}`）。此时可设置`oauth.redirect_host: localhost`，改用`http://localhost:<port>/callback`作为重定向地址；不过无论哪种方式，回调监听器仍然会绑定`127.0.0.1`地址。

如需完整的操作指南，包括无需DCR的服务器（如Slack）的使用方法、预注册的`client_id`/`client_secret`设置、作用域自定义，以及通过`hermes mcp login <server>`进行重新授权的操作，请参阅[通过SSH/远程主机实现OAuth](../../guides/oauth-over-ssh.md#mcp-servers)。

**注意事项——不支持自动注册的服务提供商（如Google Drive、Atlassian）。**某些服务器会拒绝`auth: oauth`机制所依赖的动态客户端注册流程（RFC 7591）——Google官方的Drive服务器（`https://drivemcp.googleapis.com/mcp/v1`）会返回`400 Bad Request`错误，因此既不会创建OAuth客户端，也无法获取令牌。其症状较为隐蔽：这些服务器即便在没有认证的情况下也会返回`tools/list`响应，因此`hermes mcp login`似乎能正常列出工具，但后续的任何实际工具调用都会超时。目前`hermes mcp login`已能检测到这种情况（它会检查是否有令牌真正被保存到磁盘），并提示用户自行创建OAuth客户端。您可以在对应服务提供商的控制台创建客户端，然后将其添加到配置中：

```yaml
mcp_servers:
  googledrive:
    url: "https://drivemcp.googleapis.com/mcp/v1"
    auth: oauth
    oauth:
      client_id: "<your-oauth-client-id>"
      client_secret: "<your-oauth-client-secret>"
```

接着运行 `hermes mcp login googledrive` —— 由于已预注册了客户端，Hermes 会跳过注册步骤，直接执行常规的浏览器授权流程。

**常见隐患——配置自动重载竞争问题。** 当你在正在运行的 Hermes 会话中编辑 `~/.hermes/config.yaml` 文件时，CLI 会以30秒的超时时间自动重新加载 MCP 连接。对于交互式的 OAuth 流程而言，这个时间远远不够。建议先添加相关配置项，然后从新的终端窗口运行 `hermes mcp login <server>`，这样它就会等待整整5分钟，直到你完成授权。

## mTLS / 客户端证书

对于需要互证 TLS（客户端证书认证）的远程 HTTP MCP 服务器，可通过 `client_cert` / `client_key` 参数来支持。Hermes 会将解析后的证书传递给底层的 HTTP 客户端，用于执行 TLS 握手。

`client_cert` 支持三种格式：

- **单个合并的 PEM 路径** —— 即一个文件同时包含证书和私钥：

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: "~/.certs/mcp-client.pem"
```

- **一个 `[cert, key]` 二元组**——证书与密钥分别存储于不同的文件中（相当于设置了 `client_cert` 和 `client_key`）：

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: ["~/.certs/mcp-client.crt", "~/.certs/mcp-client.key"]
```

- **一个 `[cert, key, password]` 三元组**——当私钥被加密时，第三个元素即为该密钥的密码短语：

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: ["~/.certs/mcp-client.crt", "~/.certs/mcp-client.key", "${MCP_KEY_PASSWORD}"]
```

您还可以通过使用 `client_cert`（合并后的 PEM 格式）与独立的 `client_key`，将证书和私钥完全分开存储。路径支持 `~` 扩展；若文件缺失，系统会抛出明确的、与服务器相关的错误，而不会出现难以理解的 TLS 握手失败现象。

## 基本配置参考

Hermes 会从 `~/.hermes/config.yaml` 文件中的 `mcp_servers` 部分读取 MCP 配置。

### 常用键值

| 键 | 类型 | 含义 |
|---|---|---|
| `command` | 字符串 | stdio MCP 服务器的可执行文件 |
| `args` | 列表 | 传给 stdio 服务器的参数 |
| `env` | 映射结构 | 传递给 stdio 服务器的环境变量 |
| `url` | 字符串 | HTTP MCP 接口地址 |
| `headers` | 映射结构 | 远程服务器的 HTTP 请求头 |
| `client_cert` | 字符串 \| 列表 | 用于 mTLS 的客户端证书——可以是合并后的 PEM 路径，也可以是 `[cert, key]`/`[cert, key, password]` 格式 |
| `client_key` | 字符串 | 客户端私钥的 PEM 路径（当与 `client_cert` 分开存储时使用） |
| `timeout` | 数字 | 工具调用的超时时间 |
| `connect_timeout` | 数字 | 初始连接超时时间（同时也会限制 MCP 的 `initialize` 握手过程） |
| `idle_timeout_seconds` | 数字 | 若在指定秒数内没有工具调用，便会回收该 stdio 服务器（值为 `0` 表示永不回收，为默认值）。下次有工具调用时，服务器会自动透明重启。 |
| `max_lifetime_seconds` | 数字 | 当服务器总运行时间达到此数值时，将会被回收（值为 `0` 表示永不回收，为默认值）。下次使用时会自动透明重启。 |
| `enabled` | 布尔值 | 若设置为 `false`，Hermes 将完全跳过该服务器 |
| `supports_parallel_tool_calls` | 布尔值 | 若设置为 `true`，该服务器上的工具可以并行执行 |
| `tools` | 映射结构 | 用于针对特定服务器过滤工具及定义相关策略 |

### 最简 stdio 示例

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

### 回收内存占用高的标准输入输出服务器

基于浏览器的 MCP 服务器（例如 `@playwright/mcp`）在首次调用工具后会一直保持完整的 Chromium 进程运行——这会占用数百 MB 的内存且永不释放。启用自动回收功能后，当达到空闲时间或生命周期限制时，该服务器会被终止，而在下次有工具被调用时又会无缝重启（其注册的工具在整个过程中始终有效）：

```yaml
mcp_servers:
  playwright:
    command: "npx"
    args: ["-y", "@playwright/mcp@latest", "--headless"]
    idle_timeout_seconds: 900     # recycle after 15 min without a tool call
    max_lifetime_seconds: 86400   # and at least once a day regardless
```

### 最简 HTTP 示例

```yaml
mcp_servers:
  company_api:
    url: "https://mcp.internal.example.com"
    headers:
      Authorization: "Bearer ***"
```

## 内置预设

对于常见的 MCP 服务器，`hermes mcp add` 命令支持 `--preset` 参数，该参数会自动填充传输相关配置，从而省去用户自行查找对应命令及参数的麻烦。不过这些预设仅提供默认值——您在相同命令行中指定的其他任何设置（如环境变量、请求头、过滤规则等）仍会优先生效。

| 预设名称 | 连接的 MCP 服务器 |
|---|---|
| `codex` | Codex CLI 的 MCP 服务器（通过标准输入输出运行的 `codex mcp-server`）。要求 PATH 环境变量中已包含 `codex` CLI。 |

```bash
# Add Codex CLI as an MCP server in one line
hermes mcp add codex --preset codex
```

这等价于执行了如下操作：

```yaml
mcp_servers:
  codex:
    command: "codex"
    args: ["mcp-server"]
```

您可以选择任何本地名称（例如 `hermes mcp add my-codex --preset codex` 即可）；预设值仅用于设置 `command`/`args` 的默认值。

## Hermes 如何注册 MCP 工具

Hermes 会在 MCP 工具前添加前缀，以避免其与内置名称发生冲突：

```text
mcp_<server_name>_<tool_name>
```

示例：

| 服务器 | MCP 工具 | 注册名称 |
|---|---|---|
| `filesystem` | `read_file` | `mcp_filesystem_read_file` |
| `github` | `create-issue` | `mcp_github_create_issue` |
| `my-api` | `query.data` | `mcp_my_api_query_data` |

在实际使用中，通常无需手动调用这些带前缀的名称——Hermes 会在正常推理过程中识别相应的工具并自动选择。

## MCP 工具类

在支持的情况下，Hermes 还会为 MCP 资源和提示词注册一些工具类功能：

- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

这些功能会按照相同的前缀模式针对每个服务器进行注册，例如：

- `mcp_github_list_resources`
- `mcp_github_get_prompt`

### 重要提示

这类工具类功能现在具备能力感知功能：
- 只有当 MCP 会话确实支持资源操作时，Hermes 才会注册相关的资源工具类；
- 只有当 MCP 会话确实支持提示词操作时，Hermes 才会注册相关的提示词工具类。

因此，那些仅提供可调用工具但不存在资源或提示词的服务器，将不会获得这些额外的封装功能。

## 按服务器过滤

您可以控制每个 MCP 服务器向 Hermes 提供哪些工具，从而实现对工具命名空间的精细化管理。

### 完全禁用某个服务器

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

如果设置为 `enabled: false`，Hermes 会完全跳过服务器，甚至不会尝试建立连接。

### 白名单服务器工具

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues]
```

仅已注册的 MCP 服务器工具会被启用。

### 黑名单服务器工具

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    tools:
      exclude: [delete_customer]
```

除被排除的工具外，所有服务器工具均已完成注册。

### 优先级规则

当两者同时存在时：

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

`include` 选项胜出。

### 还可单独禁用 Hermes 添加的实用工具封装：

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      prompts: false
      resources: false
```

这意味着：
- `tools.resources: false` 会禁用 `list_resources` 和 `read_resource` 功能；
- `tools.prompts: false` 会禁用 `list_prompts` 和 `get_prompt` 功能。

### 完整示例

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [create_issue, list_issues, search_code]
      prompts: false

  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer]
      resources: false

  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

## 若所有工具都被过滤掉会怎样？

如果您的配置过滤掉了所有可调用的工具，并禁用了或省略了所有支持的实用功能，Hermes不会为该服务器创建一个空的运行时MCP工具集。这样就能保持工具列表的整洁。

## 运行时行为

### 发现时间

Hermes在启动时会发现MCP服务器，并将其工具注册到常规工具注册表中。

### 动态工具发现

MCP服务器可以在运行时通过发送`notifications/tools/list_changed`通知来告知Hermes其可用工具已发生变化。收到该通知后，Hermes会自动重新获取服务器的工具列表并更新注册表——无需手动执行 `/reload-mcp` 操作。

这对于那些功能会动态变化的MCP服务器非常有用（例如，在加载新的数据库架构时添加工具，或在某个服务离线时移除工具的服务器）。

此刷新过程具有锁保护机制，可防止同一服务器频繁发送通知导致重复刷新。对于提示项或资源的变化通知（`prompts/list_changed`、`resources/list_changed`），虽然已收到但暂不会立即处理。

### 重新加载

如果您需要更改MCP配置，请使用：

```text
/reload-mcp
```

这将根据配置重新加载MCP服务器，并更新可用的工具列表。对于服务器自身推送的运行时工具变更，可参考上文中的[动态工具发现](#dynamic-tool-discovery)部分。

### 工具集

每当某个已配置的MCP服务器提供了至少一个已注册的工具时，它也会生成一个运行时工具集：

```text
mcp-<server>
```

这使得在工具集层面理解MCP服务器变得更加容易。

## 安全模型

### 标准输入环境过滤

对于标准输入服务器，Hermes不会原封不动地传递完整的Shell环境变量。仅会传递明确配置的`env`变量以及一组安全的默认值，从而有效防止意外泄露敏感信息。

### 配置级暴露控制

这一新的过滤功能同时也具备安全管控作用：
- 禁用那些不希望模型访问的危险工具
- 为敏感服务器仅开放最基本的白名单
- 在不需要暴露相关接口时，禁用资源/提示词封装功能

## 典型应用场景

### 具有最小化问题管理功能的GitHub服务器

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue]
      prompts: false
      resources: false
```

使用方式如下：

```text
Show me open issues labeled bug, then draft a new issue for the flaky MCP reconnection behavior.
```

### 已移除危险操作的 Stripe 服务器版本

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

使用方式如下：

```text
Look up the last 10 failed payments and summarize common failure reasons.
```

### 用于单个项目根目录的文件系统服务器

```yaml
mcp_servers:
  project_fs:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/my-project"]
```

使用方式如下：

```text
Inspect the project root and explain the directory layout.
```

## 故障排除

### MCP 服务器无法连接

请检查：

```bash
# Verify MCP deps are installed (already included in standard install)
cd ~/.hermes/hermes-agent && uv pip install -e ".[mcp]"

node --version
npx --version
```

接着请验证您的配置，然后重启 Hermes。

### 工具未显示

可能的原因包括：
- 服务器连接失败
- 发现功能异常
- 您的过滤配置排除了这些工具
- 该服务器上不存在相应的功能能力
- 服务器被设置为 `enabled: false` 状态而处于禁用状态

如果您是刻意进行过滤，那么这种情况属于正常现象。

### 为何资源相关工具或提示工具未出现？

因为 Hermes 现在仅会在同时满足以下两个条件时才注册这些封装工具：
1. 您的配置允许使用它们
2. 服务器会话确实支持相应的功能能力

这是有意为之的设计，旨在确保工具列表的准确性。

## 并行调用工具

默认情况下，MCP 工具是依次运行的——一次一个。如果您的 MCP 服务器提供了可以安全并行运行的工具（例如只读查询、独立的 API 调用），则您可以选择启用并行执行模式：

```yaml
mcp_servers:
  docs:
    command: "docs-server"
    supports_parallel_tool_calls: true
```

当 `supports_parallel_tool_calls` 的值为 `true` 时，Hermes 可以在单次工具调用批次中同时执行该服务器上的多个工具，其方式与处理内置只读工具（如 web_search、read_file 等）时相同。

:::caution
仅建议为那些工具可以安全地同时运行的 MCP 服务器启用并行调用功能。如果这些工具需要读取或写入共享状态、文件、数据库或外部资源，请在启用此设置之前仔细检查可能出现的读写竞态条件。
:::

## MCP 抽样支持

MCP 服务器可以通过 `sampling/createMessage` 协议向 Hermes 请求大语言模型推理服务。这样一来，MCP 服务器就可以让 Hermes 代为生成文本——这对于那些需要大语言模型功能但自身无法访问模型的服务器来说非常有用。

对于所有支持该功能的 MCP 服务器，抽样功能**默认处于开启状态**。您可以在每个服务器的配置中通过 `sampling` 键进行相应设置：

```yaml
mcp_servers:
  my_server:
    command: "my-mcp-server"
    sampling:
      enabled: true            # Enable sampling (default: true)
      model: "openai/gpt-4o"  # Override model for sampling requests (optional)
      max_tokens_cap: 4096     # Max tokens per sampling response (default: 4096)
      timeout: 30              # Timeout in seconds per request (default: 30)
      max_rpm: 10              # Rate limit: max requests per minute (default: 10)
      max_tool_rounds: 5       # Max tool-use rounds in sampling loops (default: 5)
      allowed_models: []       # Allowlist of model names the server may request (empty = any)
      log_level: "info"        # Audit log level: debug, info, or warning (default: info)
```

采样处理模块配备了滑动窗口速率限制器、单次请求超时机制以及工具循环深度限制，旨在防止资源使用失控。系统会针对每个服务器实例实时统计相关指标（请求数、错误次数、已使用的令牌数）。

如需为特定服务器关闭采样功能：

```yaml
mcp_servers:
  untrusted_server:
    url: "https://mcp.example.com"
    sampling:
      enabled: false
```

## 将 Hermes 作为 MCP 服务器运行

除了能够**连接**到 MCP 服务器之外，Hermes 本身也可以**充当** MCP 服务器。这样一来，其他具备 MCP 功能的智能体（如 Claude Code、Cursor、Codex 或任何 MCP 客户端）就能利用 Hermes 的消息功能——查看对话列表、读取消息历史记录，以及在你连接的所有平台上发送消息。

### 适用场景

- 你希望让 Claude Code、Cursor 或其他编程智能体通过 Hermes 发送和读取 Telegram/Discord/Slack 消息；
- 你需要一个能够同时连接 Hermes 所有消息平台的统一 MCP 服务器；
- 你已经拥有一个已运行且已连接了多个平台的 Hermes 网关。

### 快速入门

```bash
hermes mcp serve
```

这将启动一个标准输入输出型MCP服务器。进程的生命周期由MCP客户端（而非您）来管理。

### MCP客户端配置

请在您的MCP客户端配置中添加Hermes。例如，在Claude Code的`~/.claude/claude_desktop_config.json`文件中即可进行配置：

```json
{
  "mcpServers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

或者，如果您将 Hermes 安装在特定路径下：

```json
{
  "mcpServers": {
    "hermes": {
      "command": "/home/user/.hermes/hermes-agent/venv/bin/hermes",
      "args": ["mcp", "serve"]
    }
  }
}
```

### 可用工具

MCP 服务器提供了 10 种工具，既包括与 OpenClaw 的通道桥接功能相匹配的工具，也包含专为 Hermes 设计的通道浏览器：

| 工具 | 描述 |
|------|------|
| `conversations_list` | 列出正在进行的消息对话。可按平台筛选或通过名称搜索。 |
| `conversation_get` | 根据会话密钥获取某次对话的详细信息。 |
| `messages_read` | 查看某次对话的最新消息记录。 |
| `attachments_fetch` | 从特定消息中提取非文本附件（图片、媒体文件等）。 |
| `events_poll` | 从指定位置开始轮询新的对话事件。 |
| `events_wait` | 进行长轮询/阻塞，直到下一个事件出现（近乎实时）。 |
| `messages_send` | 通过特定平台发送消息（例如 `telegram:123456`、`discord:#general`）。 |
| `channels_list` | 列出所有平台上的可用消息发送目标。 |
| `permissions_list_open` | 显示当前桥接会话中待处理的审批请求列表。 |
| `permissions_respond` | 批准或拒绝待处理的审批请求。 |

### 事件系统

MCP 服务器内置实时事件桥接功能，可持续轮询 Hermes 的会话数据库以获取新消息。这使得 MCP 客户端能够近乎实时地掌握新对话的动态：

```
# Poll for new events (non-blocking)
events_poll(after_cursor=0)

# Wait for next event (blocks up to timeout)
events_wait(after_cursor=42, timeout_ms=30000)
```

事件类型：`message`、`approval_requested`、`approval_resolved`。

事件队列存储在内存中，会在桥接组件连接时开始工作。历史消息可通过 `messages_read` 获取。

### 选项

```bash
hermes mcp serve              # Normal mode
hermes mcp serve --verbose    # Debug logging on stderr
```

### 工作原理

MCP 服务器直接从 Hermes 的会话存储区（`~/.hermes/sessions/sessions.json` 及 SQLite 数据库）读取对话数据。一个后台线程会定期查询数据库中的新消息，并维护一个内存中的事件队列。在发送消息时，它使用与定时任务发送及 `hermes send` CLI 相同的内部发送引擎（`tools/send_message_tool.py`）。

对于读取操作（如列出对话、查看历史记录、轮询事件），无需运行网关；但执行发送操作时必须运行网关，因为平台适配器需要保持活跃的连接。

### 当前限制

- 目前内置的 `hermes mcp serve` 只提供**基于标准输入输出**的 MCP 服务器。如果需要 HTTP 版本的 MCP 服务器，需单独运行适配器；或者更常见的做法是使用 Hermes 的 MCP **客户端**，它同时支持标准输入输出和 HTTP 协议（在 `mcp_servers.yaml`/`config.yaml` 中配置 `url` 和 `headers`；详情请参见上文的[HTTP 服务器](#http-servers)部分）。
- 通过针对文件修改时间进行优化的数据库轮询机制，事件轮询间隔约为 200 毫秒（若文件未发生变化则跳过处理）。
- 目前尚不支持 `claude/channel` 推送通知协议。
- 仅支持文本发送（无法通过 `messages_send` 功能发送媒体文件或附件）。

## 相关文档

- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)
- [CLI 命令](/reference/cli-commands)
- [Slash 命令](/reference/slash-commands)
- [常见问题解答](/reference/faq)
