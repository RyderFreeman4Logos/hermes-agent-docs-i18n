---
sidebar_position: 8
title: "MCP Config Reference"
description: "Reference for Hermes Agent MCP configuration keys, filtering semantics, and utility-tool policy"
---

# MCP 配置参考

本页面是主 MCP 文档的简明参考手册。

如需概念性指导，请参阅：
- [MCP（模型上下文协议）](/user-guide/features/mcp)
- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)

## 根级配置结构

```yaml
mcp_servers:
  <server_name>:
    command: "..."      # stdio servers
    args: []
    env: {}

    # OR
    url: "..."          # HTTP servers
    headers: {}

    # Optional HTTP/SSE TLS settings:
    ssl_verify: true                # bool or path to a CA bundle (PEM)
    client_cert: "/path/to/cert.pem"  # mTLS client certificate (see below)
    # client_key: "/path/to/key.pem"  # optional, when key lives in a separate file

    enabled: true
    timeout: 120
    connect_timeout: 60
    supports_parallel_tool_calls: false
    tools:
      include: []
      exclude: []
      resources: true
      prompts: true
```

## 服务器密钥

| Key | Type | Applies to | Meaning |
|---|---|---|---|
| `command` | string | stdio | Executable to launch |
| `args` | list | stdio | Arguments for the subprocess |
| `env` | mapping | stdio | Environment passed to the subprocess |
| `url` | string | HTTP | Remote MCP endpoint |
| `headers` | mapping | HTTP | Headers for remote server requests |
| `ssl_verify` | bool or string | HTTP | TLS verification. `true` (default) uses system CAs, `false` disables verification (insecure), or a string path to a custom CA bundle (PEM) |
| `client_cert` | string or list | HTTP | mTLS client certificate. String = path to a PEM file containing cert + key. List `[cert, key]` = separate files. List `[cert, key, password]` = encrypted key |
| `client_key` | string | HTTP | Path to the client private key, when `client_cert` is a string and the key is in a separate file |
| `enabled` | bool | both | Skip the server entirely when false |
| `timeout` | number | both | Tool call timeout in seconds (default: `300`) |
| `connect_timeout` | number | both | Initial connection timeout in seconds (default: `60`) |
| `protocol` | string | both | Protocol-era negotiation: `auto` (default — legacy `initialize` handshake first, falling back to the 2026-07-28 `server/discover` stateless probe when the server rejects the handshake as modern-only), `stateless` (probe `server/discover` first; one legacy retry), or `legacy` (handshake only, no fallback) |
| `supports_parallel_tool_calls` | bool | both | Allow tools from this server to run concurrently |
| `skip_preflight` | bool | HTTP | Bypass the fail-fast content-type probe for valid Streamable HTTP endpoints whose HEAD/GET answers a non-MCP content type (default: `false`) |
| `transport` | string | HTTP | Set to `sse` to use the SSE transport instead of Streamable HTTP |
| `keepalive_interval` | number | both | Liveness ping cadence in seconds (default: `180`, floored at 5s). Set below the server's session TTL for servers that GC idle sessions quickly |
| `idle_timeout_seconds` | number | stdio | Optional stdio server recycle after idle time (`0` disables). May also live under a `lifecycle:` mapping |
| `max_lifetime_seconds` | number | stdio | Optional stdio server recycle after age (`0` disables). May also live under a `lifecycle:` mapping |
| `tools` | mapping | both | Filtering and utility-tool policy |
| `auth` | string | HTTP | Authentication method. Set to `oauth` to enable OAuth 2.1 with PKCE |
| `sampling` | mapping | both | Server-initiated LLM request policy (see MCP guide) |
| `elicitation` | mapping | both | Server-initiated user-input requests. `enabled` (default `true`) and `timeout` in seconds (default `300`). Form-mode requests route through the approval surface; URL-mode is declined (see MCP guide) |
| `trust` | string | both | Trust tier: `full` (default) or `untrusted`. On an `untrusted` server, every write-capable tool call (any tool without a `readOnlyHint: true` annotation) requires user approval through the standard approval surface before it runs. `readOnlyHint` is a server-supplied *hint* — a lying server can at most skip approval for tools it claims are read-only, never gain extra access — so mark any server you don't fully control as `untrusted`. Unrecognized values are treated as `untrusted` (fail-closed) |

## 环境变量引用

在服务器配置项中的任意位置（如 `env`、`headers`、`args`、`url` 等），均可使用 `${VAR}` 或 Cursor 风格的 SecretRef 格式 `${env:VAR}` 来引用环境变量——这两种方式最终都会指向同一个变量，因此从 Cursor/Claude 配置中复制的 MCP 代码片段无需修改即可直接使用。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "${env:GITHUB_TOKEN}"   # same as "${GITHUB_TOKEN}"
```

值会从当前激活配置文件的密钥范围中获取（若不存在则回退到进程环境），因此请将相关密钥放入 `~/.hermes/.env` 文件中。未被设置的变量将保持其原始占位符形式。

### 上下文变量

除了环境变量之外，Cursor 风格的上下文变量也会被插入使用（名称区分大小写）：

| 变量 | 对应值 |
|---|---|
| `${userHome}` | 当前用户的家目录 |
| `${workspaceFolder}` | 会话工作区根目录（若已知则为会话终端的当前工作目录，否则为进程的当前工作目录） |
| `${workspaceFolderBasename}` | `${workspaceFolder}` 的基名 |
| `${pathSeparator}` / `${/}` | 操作系统的路径分隔符（`os.sep`） |

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
    env:
      CACHE_DIR: "${userHome}${/}.cache${/}mcp"
```

任何其他 `${...}` 引用都会回退到上述的环境变量查找机制。

## `tools` 策略键

| 键 | 类型 | 含义 |
|---|---|---|
| `include` | 字符串或列表 | 授权服务器原生的 MCP 工具。条目可以是精确名称，也可以是类似 fnmatch 的通配符形式（如 `*_radar_*`、`get_zones_*`） |
| `exclude` | 字符串或列表 | 拒绝服务器原生的 MCP 工具。其精确名称/通配符规则与 `include` 相同 |
| `resources` | 类布尔值 | 开启/关闭 `list_resources` 和 `read_resource` 功能 |
| `prompts` | 类布尔值 | 开启/关闭 `list_prompts` 和 `get_prompt` 功能 |

## 过滤规则逻辑

### `include`

一旦设置了 `include`，则仅会注册那些服务器原生的 MCP 工具。

```yaml
tools:
  include: [create_issue, list_issues]
```

### `exclude`

如果设置了 `exclude` 而未设置 `include`，则除了列出的工具名称之外，所有服务器原生的 MCP 工具都会被注册。

```yaml
tools:
  exclude: [delete_customer]
```

### 优先级规则

当两者同时被设置时，`include` 的优先级更高。

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

结果：
- `create_issue` 功能仍然可用
- 由于 `include` 的优先级更高，`delete_issue` 被忽略

## 工具函数策略

Hermes 可以根据每个 MCP 服务器注册相应的工具函数封装：

资源操作：
- `list_resources`
- `read_resource`

提示词相关操作：
- `list_prompts`
- `get_prompt`

### 禁用资源操作

```yaml
tools:
  resources: false
```

### 禁用提示词功能

```yaml
tools:
  prompts: false
```

### 基于能力的注册机制

即便设置了 `resources: true` 或 `prompts: true`，只要 MCP 会话并未实际提供相应的能力，Hermes 也不会注册那些工具功能。

因此以下情况属于正常现象：
- 您启用了提示功能
- 但并未出现任何提示相关的工具
- 原因是服务器不支持该功能

## `enabled: false`

```yaml
mcp_servers:
  legacy:
    url: "https://mcp.legacy.internal"
    enabled: false
```

行为表现：
- 不尝试建立连接
- 不进行服务发现
- 不注册任何工具
- 配置信息将保留以便日后重复使用

## 无结果时的处理方式

如果过滤操作已移除所有服务器原生工具，且也未注册任何实用工具，Hermes 将不会为该服务器创建空的 MCP 运行时工具集。

## 配置示例

### 安全的 GitHub 允许列表

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
    tools:
      include: [list_issues, create_issue, update_issue, search_code]
      resources: false
      prompts: false
```

### Stripe 黑名单

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    headers:
      Authorization: "Bearer ***"
    tools:
      exclude: [delete_customer, refund_payment]
```

### 仅资源型文档服务器

```yaml
mcp_servers:
  docs:
    url: "https://mcp.docs.example.com"
    tools:
      include: []
      resources: true
      prompts: false
```

### TLS 客户端证书（mTLS）

对于需要客户端证书的 HTTP/SSE 服务器，请设置 `client_cert`（可选地也可设置 `client_key`）：

```yaml
mcp_servers:
  # Combined cert + key in a single PEM file
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: "~/secrets/mcp-client.pem"

  # Separate cert and key files
  partner_api:
    url: "https://mcp.partner.example.com/mcp"
    client_cert: "~/secrets/client.crt"
    client_key: "~/secrets/client.key"

  # Encrypted key with a passphrase (3-element list form)
  bank_api:
    url: "https://mcp.bank.example.com/mcp"
    client_cert: ["~/secrets/client.crt", "~/secrets/client.key", "my-passphrase"]

  # Custom CA bundle (private CA / self-signed server)
  lab_api:
    url: "https://mcp.lab.local/mcp"
    ssl_verify: "~/secrets/lab-ca.pem"
    client_cert: "~/secrets/lab-client.pem"
```

备注：  
- 路径支持使用 `~` 进行扩展。若文件不存在，连接服务器时会立即失败，并显示与服务器相关的错误信息。  
- `ssl_verify: false` 会完全禁用对服务器证书的验证。请勿在真实服务中使用此选项。  
- 该功能同时支持 Streamable HTTP 和 SSE 传输方式。  

## 重新加载配置  

修改 MCP 配置后，可通过以下命令重新加载服务器：

```text
/reload-mcp
```

## 工具命名规则

服务器原生的 MCP 工具将被命名为：

```text
mcp__<server>__<tool>
```

示例：  
- `mcp__github__create_issue`  
- `mcp__filesystem__read_file`  
- `mcp__my_api__query_data`  

实用工具也遵循相同的命名前缀规则：  
- `mcp__<服务器名>__list_resources`  
- `mcp__<服务器名>__read_resource`  
- `mcp__<服务器名>__list_prompts`  
- `mcp__<服务器名>__get_prompt`  

双下划线分隔符（`mcp__…__…`）与 Claude Code、Codex 以及 OpenCode 所采用的格式一致，即便相关组件中包含下划线，也能清晰区分服务器与工具的边界。  

### 名称规范化处理  

在注册之前，服务器名称和工具名称中的所有非字母、数字或下划线的字符（如连字符、点号、空格等）都会被替换为下划线。这样做可确保工具名称能够作为有效的标识符，用于调用大型语言模型接口。  

例如，一个名为 `my-api` 的服务器若提供了名为 `list-items.v2` 的工具，其名称将会被调整为：

```text
mcp__my_api__list_items_v2
```

在编写 `include` / `exclude` 过滤规则时，请牢记这一点：应使用 **原始的** MCP 工具名称（包含连字符/点号），而非经过处理的版本。

## OAuth 2.1 身份验证

对于需要 OAuth 认证的 HTTP 服务器，请在服务器配置项中设置 `auth: oauth`：

```yaml
mcp_servers:
  protected_api:
    url: "https://mcp.example.com/mcp"
    auth: oauth
```

行为特性：
- Hermes采用MCP SDK的OAuth 2.1 PKCE流程（包括元数据发现、客户端身份验证、令牌交换及刷新操作）
- 首次连接时，会打开一个浏览器窗口以进行授权
- 令牌会被保存在`~/.hermes/mcp-tokens/<server>.json`文件中，并可在不同会话间重复使用
- 令牌刷新为自动处理；仅当刷新失败时才会要求重新授权
- 该机制仅适用于HTTP/StreamableHTTP传输方式（基于`url`的服务器）

### 设备码登录（RFC 8628标准）

对于已声明`device_authorization_endpoint`的授权服务器，可在运行Hermes的机器终端上直接选择设备授权模式进行登录：

```bash
hermes mcp login protected_api --flow device
```

在任何设备上打开打印出的验证网址，然后输入页面上显示的用户代码。Hermes会定期轮询审批结果，同时会尊重`authorization_pending`和`slow_down`设置；一旦收到拒绝响应或代码过期，流程就会立即停止。该过程无需启动浏览器，也不需要配置回调监听器。`oauth.timeout`参数可限制等待审批的时间（默认为300秒），这一时间还会受到代码有效期的制约。

若要在服务器端设置`oauth.flow: device`，则`hermes mcp login`和`hermes mcp reauth`（包括`reauth --all`命令）将会使用设备授权方式。不过，使用`login --flow browser`指令登录时可以暂时忽略该设置；此时浏览器PKCE机制仍为默认选项。对于不支持的元数据，系统会给出明确的错误提示，而不会默许切换到其他授权流程。

在动态注册过程中，设备登录请求会通过设备本身或刷新令牌来获取授权；否则则会使用您预先配置的`oauth.client_id`、`oauth.client_secret`以及`oauth.token_endpoint_auth_method`。已注册的客户端必须支持设备授权功能，且不会使用浏览器CIMD文档。在设备授权请求中会包含`oauth.scope`参数，而`oauth.user_agent`参数同样适用于令牌轮询过程。生成的令牌、注册信息以及发行方元数据都会存储在当前活跃配置文件的MCP令牌存储区中，系统重启后仍会沿用原有的运行时刷新机制。失败的设备授权请求不会替换之前保存的凭证。

初始设备登录仅支持终端端使用：控制面板/浏览器回调以及后台重新连接均不会触发设备授权流程。必须针对与网关**相同的配置文件和主机**来执行登录命令。若设备授权已过期或被拒绝，且没有可用的刷新令牌，则需要再次进行明确登录。

### 客户端标识：CIMD与DCR

Hermes通过**客户端ID元数据文档**（Client ID Metadata Document，简称CIMD）向授权服务器标识自身，这一机制是MCP `2026-07-28`规范取代动态客户端注册所采用的方案。该文档的地址为`https://nousresearch.github.io/hermes-agent/docs/oauth/client-metadata.json`，该URL本身即为`client_id`——授权服务器会通过它获取Hermes的名称、标志以及允许的重定向URI。该文档不会随每次安装而注册新内容，也不针对特定用户生成。

最终是否采用该机制由授权服务器决定：只有当服务器在其元数据中声明`client_id_metadata_document_supported: true`时，SDK才会将文档地址作为`client_id`发送；否则仍会像以前一样通过DCR进行注册。虽然MCP规范已不再推荐使用DCR，但如今几乎所有已部署的授权服务器仍在使用它。

#### 回调端口

该文档规定了一组固定的回环重定向URI，且规范要求授权请求中的重定向URI必须与这些URI之一实现*完全字符串匹配*——因此CIMD流程无法使用Hermes通常选择的随机高端口。为此，Hermes将回调功能固定在了`27890`至`27894`之间的某个端口上。

由于在流程开始时重定向 URI 已被固定，而服务器的元数据则要等到流程中途才会送达，因此必须在了解服务器功能之前选定该端口。为此，Hermes 会为所有可能使用 CIMD 的流程锁定一个特定端口，而对于其余流程则采用随机端口：

- 对于 Hermes 之前已连接过且其缓存元数据中未标注支持 CIMD 的服务器，仍会保持其一贯使用的随机端口；
- 对于 Hermes 从未访问过的服务器，则会在首次登录时为其锁定一个端口，因为此时只能通过猜测来确定是否使用 CIMD；
- 任何可能导致回调地址发生变化的因素也会导致端口恢复为随机值：预先注册的 `oauth.client_id`、`oauth.client_secret`、自定义的 `oauth.client_name` 或 `oauth.token_endpoint_auth_method`、被覆盖的 `oauth.redirect_uri` 或 `oauth.redirect_port`、通过控制面板或桌面端发起的登录、磁盘上已存在的客户端注册记录，以及所有五个端口都被其他进程占用的情况。

一旦选定某个端口，它就会立即被绑定，并一直保持到浏览器发出重定向请求为止。因此，同一进程中同时进行的两次登录——比如使用另一个配置文件或连接另一台服务器——不会被分配到同一个监听端口上。

#### 当服务器拒绝该文档时

如果服务器在 *token* 端点获取了该文档但予以拒绝（返回 `invalid_client` 错误），Hermes 会记录下此次拒绝行为，并将其保存在 `~/.hermes/mcp-tokens/<server>.cimd-off` 文件中，之后对该服务器将始终使用 DCR 协议进行通信。

如果服务器完全无法获取或验证该文档，它会在发生任何重定向之前就在*授权*接口处终止操作。由于Hermes无法检测到相关信号，浏览器会显示“无效客户端”错误，且登录将在五分钟后超时。超时信息中会注明文档名称，并标注`cimd: false`。执行`hermes mcp login <server>`命令即可清除已记录的拒绝状态，从而使修正后的文档获得再次尝试的机会。

#### 可选的服务器级密钥

```yaml
mcp_servers:
  protected_api:
    url: "https://mcp.example.com/mcp"
    auth: oauth
    oauth:
      client_metadata_url: "https://example.com/my-cimd.json"  # self-hosted document
      cimd: false                                              # force DCR
      user_agent: "My-MCP-Client/1.0"                          # token-request User-Agent
```

`client_metadata_url` 必须是一个包含路径的 HTTPS 地址（不能仅包含域名，不能包含片段、用户信息以及 `.`/`..` 路径段），该地址在请求时需返回状态码 `200` 且 `Content-Type` 为 `application/json`，同时**严禁重定向**——授权服务器在获取该数据时不得跟随重定向链接。Hermes 仍会将回调地址固定在与 `27890`–`27894` 相同的范围内，因此自托管文档必须声明全部十个回环地址（每个端口对应 `http://127.0.0.1:<port>/callback` 和 `http://localhost:<port>/callback`），且其 `client_id` 必须为该地址本身。

`user_agent` 仅用于**令牌端点请求**（即授权码交换和刷新操作）时，替换 HTTP 库默认的 `User-Agent` 值——某些授权服务器和 WAF 会拒绝接受默认的 `python-httpx/...` 值。该参数不适用于 MCP 流量或 OAuth 发现流程，且其他令牌请求相关的头部字段也不支持配置。空值或 `null` 值将被忽略。

## 添加到 Hermes 链接

MCP 供应商和文档可以提供一个一键式的“添加到 Hermes”按钮，该按钮会打开已填好服务器配置的 Hermes 桌面应用，其工作原理类似于 Cursor 的 `cursor://anysphere.cursor-deeplink/mcp/install` 协议方案：

```text
hermes://mcp/install?name=NAME&config=BASE64
```

- `name` — 服务器名称。必须符合 `^[A-Za-z0-9._-]{1,64}$` 的格式要求。
- `config` — 以 **base64url编码的JSON格式** 表示的服务器配置对象（标准base64格式也可接受）。解码后的JSON对象必须包含一个 `url` 字段（仅支持 `http://`/`https://` 协议）或一个 `command` 字段，同时还可以包含上述文档中列出的任何服务器相关键值。超过32KB的载荷将被拒绝。

JavaScript示例：

```js
const config = { url: 'https://mcp.example.com/mcp' }
const link = `hermes://mcp/install?name=example&config=${btoa(JSON.stringify(config))
  .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')}`
```

点击该链接本身并不会自动安装任何内容：桌面应用会弹出一个确认对话框，显示服务器名称以及格式化后的完整配置信息（对于那些通过`command`命令运行本地进程的服务器，还会额外给出警示），用户必须明确进行确认操作。现有的服务器名称绝不会被覆盖——系统会要求用户选择重新命名或取消操作。
