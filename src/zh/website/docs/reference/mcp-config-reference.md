---
sidebar_position: 8
title: "MCP Config Reference"
description: "Reference for Hermes Agent MCP configuration keys, filtering semantics, and utility-tool policy"
---

# MCP 配置参考手册

本页面是主 MCP 文档的简明配套参考资料。

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

| 密钥 | 类型 | 适用场景 | 含义 |
|---|---|---|---|
| `command` | 字符串 | stdio | 需要启动的可执行程序 |
| `args` | 列表 | stdio | 子进程的参数 |
| `env` | 映射结构 | stdio | 传递给子进程的环境变量 |
| `url` | 字符串 | HTTP | 远程 MCP 接口地址 |
| `headers` | 映射结构 | HTTP | 发送至远程服务器请求的头部信息 |
| `ssl_verify` | 布尔值或字符串 | HTTP | TLS 验证设置。`true`（默认值）表示使用系统证书颁发机构；`false` 表示禁用验证（存在安全风险）；也可以是自定义 CA 签名包（PEM 格式）的路径 |
| `client_cert` | 字符串或列表 | HTTP | mTLS 客户端证书。字符串形式表示包含证书和密钥的 PEM 文件路径；列表 `[cert, key]` 表示证书和密钥为单独的文件；列表 `[cert, key, password]` 表示密钥已加密 |
| `client_key` | 字符串 | HTTP | 当 `client_cert` 为字符串且密钥存储在单独文件中时，该字段表示客户端私钥的路径 |
| `enabled` | 布尔值 | 两者均适用 | 设置为 `false` 时可完全跳过该服务器 |
| `timeout` | 数字 | 两者均适用 | 工具调用的超时时间 |
| `connect_timeout` | 数字 | 两者均适用 | 初始连接超时时间 |
| `supports_parallel_tool_calls` | 布尔值 | 两者均适用 | 是否允许该服务器上的工具并行运行 |
| `tools` | 映射结构 | 两者均适用 | 工具过滤规则及实用工具策略 |
| `auth` | 字符串 | HTTP | 认证方式。设置为 `oauth` 可启用基于 PKCE 的 OAuth 2.1 认证 |
| `sampling` | 映射结构 | 两者均适用 | 由服务器发起的 LLM 请求策略（详见 MCP 指南） |

## `tools` 策略键

| 键 | 类型 | 含义 |
|---|---|---|
| `include` | 字符串或列表 | 白名单机制，用于指定允许使用的服务器原生 MCP 工具 |
| `exclude` | 字符串或列表 | 黑名单机制，用于指定禁止使用的服务器原生 MCP 工具 |
| `resources` | 类布尔值 | 控制是否启用 `list_resources` 和 `read_resource` 功能 |
| `prompts` | 类布尔值 | 控制是否启用 `list_prompts` 和 `get_prompt` 功能 |

## 过滤规则逻辑

### `include` 设置

当设置了 `include` 参数后，仅会注册那些属于服务器原生的 MCP 工具。

```yaml
tools:
  include: [create_issue, list_issues]
```

### `exclude`

如果设置了 `exclude` 而未设置 `include`，则除了列出的工具名称之外，所有原生服务器 MCP 工具都会被注册。

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

## 工具类插件策略

Hermes 可以根据每个 MCP 服务器注册相应的工具封装插件：

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

### 基于能力识别的注册机制

即便设置了 `resources: true` 或 `prompts: true`，只要 MCP 会话并未实际提供相应的能力，Hermes 也不会注册那些工具功能。

因此出现以下情况属于正常现象：
- 您启用了提示功能
- 但并未看到任何提示相关的工具
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
- 不进行服务器发现
- 不注册任何工具
- 配置将保留以便日后重复使用

## 无结果时的处理方式

如果过滤操作移除了所有服务器原生工具，且也未注册任何实用工具，Hermes 将不会为该服务器创建空的 MCP 运行时工具集。

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
- 路径支持使用 `~` 进行扩展。若文件不存在，连接服务器时将会立即失败，并显示与服务器相关的错误信息。  
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
mcp_<server>_<tool>
```

示例：  
- `mcp_github_create_issue`  
- `mcp_filesystem_read_file`  
- `mcp_my_api_query_data`  

实用工具也遵循相同的命名前缀规则：  
- `mcp_<服务器名>_list_resources`  
- `mcp_<服务器名>_read_resource`  
- `mcp_<服务器名>_list_prompts`  
- `mcp_<服务器名>_get_prompt`  

### 名称规范化处理  

在注册之前，服务器名称和工具名称中的连字符（`-`）及点号（`.`）都会被替换为下划线。这样做可确保工具名称能够作为有效的标识符，用于调用大型语言模型相关接口。  

例如，一个名为 `my-api` 的服务器若提供了名为 `list-items.v2` 的工具，其名称将会被调整为：

```text
mcp_my_api_list_items_v2
```

在编写 `include` / `exclude` 过滤规则时，请牢记这一点：应使用 **原始的** MCP 工具名称（包含连字符/点号），而非经过清理后的版本。

## OAuth 2.1 身份验证

对于需要 OAuth 认证的 HTTP 服务器，需在服务器配置项中设置 `auth: oauth`：

```yaml
mcp_servers:
  protected_api:
    url: "https://mcp.example.com/mcp"
    auth: oauth
```

行为特性：  
- Hermes采用MCP SDK的OAuth 2.1 PKCE流程（包括元数据发现、动态客户端注册、令牌交换及刷新功能）；  
- 首次连接时，系统会打开一个浏览器窗口以进行授权；  
- 令牌会被保存在`~/.hermes/mcp-tokens/<服务器名>.json`文件中，并可在不同会话间重复使用；  
- 令牌刷新为自动处理，仅当刷新失败时才会要求重新授权；  
- 此功能仅适用于HTTP/StreamableHTTP传输方式（基于`url`的服务器）。
