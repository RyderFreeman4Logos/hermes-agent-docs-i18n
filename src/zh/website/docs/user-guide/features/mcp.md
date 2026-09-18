---
sidebar_position: 4
title: "MCP (Model Context Protocol)"
description: "Connect Hermes Agent to external tool servers via MCP — and control exactly which MCP tools Hermes loads"
---

# MCP（模型上下文协议）

MCP 允许 Hermes Agent 连接到外部工具服务器，从而使 Agent 能够使用位于 Hermes 之外的各种工具——例如 GitHub、数据库、文件系统、浏览器环境、内部 API 等。

如果您希望让 Hermes 使用其他地方已有的工具，MCP 通常是实现这一目标的最佳方式。

:::提示 来自 Claude Code？
您在 `~/.claude.json` 中配置的 `mcpServers` 字段对应于 Hermes 的 `config.yaml` 中的 `mcp_servers` —— 而命令 `hermes import-agent claude-code` 可以自动完成该字段的迁移（同时还会迁移技能和指令）。详情请参阅[从其他 Agent 导入](../import-from-other-agents.md)。
:::

## MCP 能为您带来什么

- 无需先编写原生 Hermes 工具，即可使用外部工具生态系统
- 在同一配置文件中同时支持本地标准输入输出服务器与远程 HTTP MCP 服务器
- 启动时自动发现并注册工具
- 当服务器支持时，为 MCP 资源和提示语提供实用封装
- 支持按服务器进行过滤，仅让 Hermes 使用您希望其看到的 MCP 工具

## 快速入门

1. 标准安装即已包含 MCP 支持，无需额外操作。

2. 在 `~/.hermes/config.yaml` 中添加一个 MCP 服务器：

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

Hermes 会自动发现 MCP 服务器中的各类工具，并能像使用其他工具一样将其调用。

## 工具目录：一键安装 Nous 审核通过的 MCP 服务

Hermes 内置了一个经过 Nous 团队审核并筛选过的 MCP 服务器目录。这些服务器默认处于禁用状态——请仅安装您真正需要的服务。

```bash
hermes mcp                # interactive picker (default)
hermes mcp catalog        # plain-text list, scriptable
hermes mcp install n8n    # install a catalog entry by name
```

该选择器会显示每一项的当前状态：将“COMPLETE”标记为“已完成”。切勿提前终止操作。

```
n8n          available              Manage and inspect n8n workflows from Hermes
linear       enabled                Linear issue/project management (remote OAuth)
github       installed (disabled)   GitHub repo + PR tools
```

在对应行按下 `Enter` 键即可进行安装（同时可输入所需的凭据），或执行启用、禁用、卸载操作。目录条目存储在 hermes-agent 仓库的 `optional-mcps/` 目录下——若该目录中存在相应条目，即表示已获得 Nous 的批准。此系统不存在社区提交机制，所有条目均需通过合并 Pull Request 方式添加。

目录条目可能需要以下凭据：

- **API 密钥** — Hermes 会在安装时提示输入，并将密钥值写入 `~/.hermes/.env` 文件中。非敏感值（如基础 URL）也会存入同一文件。
- **OAuth**（远程 MCP）——需在配置文件中以 `auth: oauth` 的格式进行指定；首次连接时，MCP 客户端会自动打开浏览器。
- **OAuth**（如 Google/GitHub 等第三方提供商）——若尚未完成认证，Hermes 会指引您使用命令 `hermes auth <provider>` 进行登录。

### 安装时的工具选择

配置完凭据后，Hermes 会探测 MCP 服务器，列出其提供的所有工具，并展示相应的选项清单：

```
Select tools for 'linear' (SPACE toggle, ENTER confirm)
  [x] find_issues       Find issues matching a query
  [x] get_issue         Get a single issue
  [x] create_issue      Create a new issue
  [ ] delete_workspace  Delete a Linear workspace
  ...
```

已预选中的条目来源于以下几处：

1. **您之前的选择**：如果您此前已安装过该条目（重新安装时会保留您之前的设置——清单中的默认值不会覆盖它们）；
2. **清单中的 `tools.default_enabled` 设置**：如果该条目指定了默认启用的工具（某些目录条目会预先筛选掉那些会修改配置或很少使用的工具）；
3. **全部条目**：若以上两种情况均不适用，则全部条目都会被选中。

对于那些自动生成的条目数量极多的项目（例如 `cloudflare`，拥有约 3,300 个 OpenAPI 接口工具），它们会指定 `tools.default_excluded` —— 一个包含具体名称和通配符模式的精选屏蔽列表。安装此类项目时将完全跳过检查流程，并直接写入 `tools.exclude`；所有未匹配的工具仍将保持启用状态，包括服务器后续添加的工具。如需重新启用某个工具组，可编辑 config.yaml 文件中的 `mcp_servers.<name>.tools.exclude`。

按回车键即可提交设置。最终只有被选中的工具才会被纳入 `mcp_servers.<name>.tools.include` 中。如果您选择了全部工具，则不会写入任何过滤规则（这样配置最为简洁，行为也与之前一致）。

**如果检测失败**（无法连接到服务器、OAuth 认证尚未完成、后台服务未运行），安装仍然会成功：此时会直接应用清单中的 `tools.default_enabled` 设置（如果已指定），或者不写入任何过滤规则（如果未指定）。待服务器可访问后，再次运行 `hermes mcp configure <name>` 即可进一步调整设置。

### 信任模型

安装某个目录条目时，会执行清单中指定的所有操作——包括 `git clone`、该条目中的 `bootstrap` 命令（如 `pip install`、`npm install` 等），以及最终启动 MCP 服务器本身的代码。由于清单需要经过 PR 审核才能被提交到 hermes-agent 仓库，因此 Nous 会在每个条目发布前进行审核——**但您在安装之前仍应仔细阅读清单**，尤其是 `source:` 字段中指定的仓库地址、`install.bootstrap:` 命令，以及任何 `transport.command:` 调用内容。

这些清单存储在 GitHub 的 [`optional-mcps/<name>/manifest.yaml`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps) 地址下。安装时，选择工具还会显示清单中的 `source:` URL，方便您快速验证上游仓库的真实性。Web 控制台的 MCP 页面也会展示每个目录条目的详细信息——传输方式、认证类型、端点 URL（HTTP）或命令及参数（标准输入/输出）、git 安装的源代码/引用地址及 bootstrap 命令，以及相关设置说明——其中 `source:` 字段会被呈现为可点击链接，让您在点击“安装”之前就能清楚地了解该条目将连接到何处或会执行哪些操作。

### 清单版本兼容性

清单会指定一个 `manifest_version` 版本。该目录系统具备向前兼容性：如果某个 PR 添加了 `manifest_version` 版本高于您当前使用的 Hermes 版本的条目，选择工具会针对该条目显示警告信息（`⚠ '<name>' requires a newer Hermes`），而不会将其悄悄隐藏。遇到这种情况时，请运行 `hermes update` 来安装最新版本的 Hermes。

### 运行时 `${ENV_VAR}` 变量替换

在条目的 `transport.command`、`transport.args`、`transport.url` 以及 `headers` 中，`${VAR}` 占位符会在连接服务器时根据环境变量进行替换（这些环境变量包括 `~/.hermes/.env` 文件中的所有内容）。当某个目录条目需要引用用户在其他地方配置的值时，这种方式非常有用——例如 `${HOME}/foo` 或 `${MY_PROVIDER_TOKEN}`。

类似光标风格的上下文变量也会被替换（区分大小写）：`${userHome}`（用户主目录）、`${workspaceFolder}`（会话工作区根目录）、`${workspaceFolderBasename}`，以及 `${pathSeparator}` / `${/}`（操作系统的路径分隔符）。详情请参阅 [MCP 配置参考](/docs/reference/mcp-config-reference)。

需要注意的是，这与目录清单中的 `${INSTALL_DIR}` 不同，后者会在安装时被替换为目录清单将条目的代码库克隆到的路径。

### 后续更新工具选择

```bash
hermes mcp configure linear
```

该功能会重新打开同一个检查表，且您当前选中的选项已预先勾选。当您希望启用更多工具，或服务器新增了您想使用的工具时，可使用此功能。

### 更新目录清单

MCP不会自动更新。如果清单版本发生变更，在Hermes升级后，请重新运行`hermes mcp install <name>`以刷新内容。

若要将某个MCP添加到目录中，请针对[`optional-mcps/`](https://github.com/NousResearch/hermes-agent/tree/main/optional-mcps)提交一个Pull Request。

### 建议元数据（`suggest:`）

清单中可声明一个可选的`suggest:`块，其中包含`keywords:`和/或`hosts:`列表。界面组件（目前为桌面应用的composer）会利用这些信息：当您的草稿中出现的完整单词与某关键词匹配，或粘贴的链接主机名以某主机后缀结尾时，便会提供“添加<服务器>”的一键按钮。该功能仅为建议性质——实际安装仍需通过相同的经过验证的目录/配置路径进行——而且大多数托管型远程服务（如Atlassian、Sentry、Notion、Stripe、Vercel、Supabase等）都会声明此元数据。

GitHub故意未被列入该目录：其托管型的MCP要求每个客户端自行配置OAuth应用（不支持通用动态客户端注册），而Hermes自带的`github/*`技能可驱动更强大的`gh` CLI集成方案。在桌面端，若尚未登录`gh`，GitHub相关提示则会推荐使用`github-auth`技能。

## 两种类型的MCP服务器

### Stdio服务器

Stdio服务器作为本地子进程运行，通过标准输入/输出进行通信。

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"
```

在以下情况下请使用标准输入输出服务器：
- 服务器已安装在本地；
- 您需要低延迟地访问本地资源；
- 您遵循的 MCP 服务器文档中明确了 `command`、`args` 和 `env` 的相关规范。

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
- 您的组织公开了内部 MCP 端点
- 您不希望 Hermes 为该集成启动本地子进程

### 经 OAuth 鉴权的 HTTP 服务器

大多数托管型 MCP 服务器（如 Cloudflare、Linear、Sentry、Atlassian、Asana、Figma、Stripe 等）要求使用 OAuth 2.1 而非静态令牌。只需设置 `auth: oauth`，Hermes 就会通过 MCP Python SDK 处理端点发现、客户端身份识别、PKCE、令牌交换、刷新以及升级认证等流程。

对于支持 [客户端 ID 元数据文档](../../reference/mcp-config-reference.md#client-identification-cimd-and-dcr)的服务器，Hermes 会使用该文档进行身份标识；而对于不支持的服务器，则会回退到动态客户端注册机制。这两种方式均为自动处理，无需额外配置。

:::tip Figma 远程 MCP
Figma 的托管端点（`https://mcp.figma.com/mcp`）仅允许通过**精确的 `client_name`**进行动态客户端注册——仅输入 `"Hermes Agent"` 会触发 403 错误，而 `"Claude Code"` 和 `"Codex"` 可以成功注册。Hermes 会自动为 `mcp.figma.com` 设置 `oauth.client_name: "Claude Code"`，因此无需特殊处理即可完成安装和登录。

```yaml
mcp_servers:
  figma:
    url: "https://mcp.figma.com/mcp"
    auth: oauth
```

或者：先执行 `hermes mcp install figma`，然后再运行 `hermes mcp login figma`。

```yaml
mcp_servers:
  linear:
    url: "https://mcp.linear.app/mcp"
    auth: oauth
```

首次连接时，Hermes 会输出一个授权 URL，并在可能的情况下自动打开您的浏览器，同时在本地回环端口等待 OAuth 回调。令牌会被缓存在 `~/.hermes/mcp-tokens/<server>.json` 文件中，权限设置为 0o600；之后每次运行都会自动重用这些令牌，直到刷新失败为止。

**远程/无界面主机场景。** 当 Hermes 在与浏览器不同的机器上运行时，回环回调无法到达您的笔记本电脑。此时可通过以下方式完成授权流程：

- **Hermes Desktop（自动模式）：** 当您通过 Desktop 应用的 MCP 设置界面针对远程后端进行 OAuth 登录时，Desktop 会在*您的*机器上托管回调监听器，并自动将授权信息转回网关——无需任何隧道、手动粘贴或代理设置。前提是 Desktop 应用和后端都必须为最新版本。
- **手动粘贴模式（无需额外设置）：** 在交互式终端中，Hermes 会在授权 URL 旁显示“或在此处粘贴重定向 URL…”的提示。您只需在浏览器中打开该 URL 进行授权，复制浏览器最终显示的完整 URL（由于重定向过程可能会出现连接错误，这是正常现象），然后将其粘贴到提示框中即可。仅包含 `?code=…&state=…` 的查询字符串也同样有效。
- **设备码登录（完全无需回调）：** 如果服务器的授权服务器提供了设备授权端点，可在运行 Hermes 的机器上执行命令 `hermes mcp login <server> --flow device`。该命令会输出一个验证网址和短代码；在任何设备上打开该网址并输入代码，Hermes 便会自动发起审批请求。此方式无需在主机上启动浏览器，也无需配置回调监听器。可在服务器上设置 `oauth.flow: device`，以便让 `login` 和 `reauth` 操作默认使用该登录流程。详情请参阅：[设备码登录](../../reference/mcp-config-reference.md#device-code-login-rfc-8628)。
- **SSH 端口转发：** 在另一个终端中执行命令 `ssh -N -L <port>:127.0.0.1:<port> user@host`，随后让重定向流程正常进行即可。
- **代理式回调（`redirect_uri`）：** 当某个公共 HTTPS 端点将请求转发到主机时（例如指向回调端口的 Tailscale Funnel 或反向代理），只需设置 `oauth.redirect_uri`，浏览器便会自动将用户重定向至 Hermes，无需任何隧道连接或手动粘贴操作。

```yaml
mcp_servers:
  myserver:
    url: "https://mcp.example.com/mcp"
    auth: oauth
    oauth:
      redirect_port: 8765                                # fixed port for the proxy to target
      redirect_uri: "https://oauth.example.ts.net/callback"
```

对于完全无界面的网关（即仅作为消息机器人，完全没有交互式终端），可选的 [`mcp-oauth-remote-gateway` 技能](../skills/optional/mcp/mcp-mcp-oauth-remote-gateway.md)会引导智能体手动完成整个流程，并在Hermes要求的相应位置填写令牌。

**需要注意的一个问题——WAF会拒绝以 `127.0.0.1` 作为重定向URI的请求。**部分服务提供商会在其授权服务器前部署WAF，这类WAF会对查询字符串中包含字面值 `127.0.0.1` 的任何授权请求返回403错误（Reclaim.ai的AWS API Gateway就是典型的例子——在任何请求到达OAuth应用之前都会返回 `{"message":"Forbidden"}`）。此时可设置 `oauth.redirect_host: localhost`，从而使用 `http://localhost:<port>/callback` 作为重定向地址；不过无论哪种方式，回调监听器仍然会绑定到 `127.0.0.1`。

如需完整的操作指南，包括无需DCR的服务器（如Slack）的使用方法、预注册的 `client_id`/`client_secret` 设置、作用域自定义，以及通过 `hermes mcp login <server>` 进行重新认证的步骤，请参阅 [通过SSH/远程主机进行OAuth授权](../../guides/oauth-over-ssh.md#mcp-servers)。

**常见陷阱——不支持自动注册的提供方（如 Google Drive、Atlassian）**。某些服务器会拒绝 `auth: oauth` 所依赖的动态客户端注册流程（RFC 7591）——Google 官方的 Drive 服务器（`https://drivemcp.googleapis.com/mcp/v1`）会返回 `400 Bad Request` 错误，从而导致无法创建 OAuth 客户端，也无法获取访问令牌。其表现较为隐蔽：这类服务器即便在无需认证的情况下也能响应 `tools/list` 请求，因此执行 `hermes mcp login` 时虽能列出相关工具，看似操作成功，但后续的任何实际工具调用都会超时。目前 `hermes mcp login` 已能检测到这种情况（它会检查磁盘上是否真的存在令牌），并提示用户自行创建 OAuth 客户端。您可以在对应提供方的控制台创建客户端，然后将其添加到配置中即可。

```yaml
mcp_servers:
  googledrive:
    url: "https://drivemcp.googleapis.com/mcp/v1"
    auth: oauth
    oauth:
      client_id: "<your-oauth-client-id>"
      client_secret: "<your-oauth-client-secret>"
```

接着运行 `hermes mcp login googledrive` —— 由于已预先注册了客户端，Hermes 会跳过注册步骤，直接执行常规的浏览器授权流程。

**常见隐患——配置自动重载竞争问题。** 当你在正在运行的 Hermes 会话中编辑 `~/.hermes/config.yaml` 文件时，CLI 会以30秒为超时时间自动重新加载 MCP 连接。对于需要交互式 OAuth 授权的流程来说，这个时间远远不够。建议先添加相关配置项，然后从新的终端窗口运行 `hermes mcp login <server>`，这样它就会等待整整5分钟，直到你完成授权。

## mTLS / 客户端证书

对于需要使用互惠 TLS（客户端证书认证）的远程 HTTP MCP 服务器，可以通过 `client_cert` / `client_key` 参数来支持。Hermes 会将解析后的证书传递给底层的 HTTP 客户端，用于执行 TLS 握手。

`client_cert` 支持以下三种格式：

- **单个合并后的 PEM 路径** —— 即一个文件同时包含证书和私钥：

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

- **一个 `[证书, 密钥, 密码]` 三元组**——当私钥被加密时，第三个元素即为该密钥的密码短语：

```yaml
mcp_servers:
  internal_api:
    url: "https://mcp.internal.example.com/mcp"
    client_cert: ["~/.certs/mcp-client.crt", "~/.certs/mcp-client.key", "${MCP_KEY_PASSWORD}"]
```

您还可以通过 `client_cert`（合并后的 PEM 格式）与独立的 `client_key` 来实现证书与密钥的完全分离。路径支持使用 `~` 进行扩展；若文件缺失，系统会抛出明确的、与服务器相关的错误，而不会导致难以理解的 TLS 握手失败。

## 每用户身份标识头

对于那些会根据调用者身份来控制行为的远程 HTTP/SSE MCP 服务器（如基于用户的速率限制、审计追踪、多租户路由等功能），您可以通过 `identity_header` 在每次请求中发送身份标识头：

```yaml
mcp_servers:
  team_api:
    url: "https://mcp.team.example.com/mcp"
    identity_header:
      name: "X-User-Id"
      value_from: "static"   # "static" (default) or "profile"
      value: "alice"         # required for static
```

- `value_from: static` 会直接使用 `config.yaml` 中指定的 `value` 值。  
- `value_from: profile` 会返回当前激活的 Hermes 配置文件名称，该名称在连接时仅解析一次——当同一台机器上的多个配置文件需要与同一服务器通信且需区分彼此时，此选项非常有用。  

若服务器的 `headers` 映射中存在同名（无论大小写如何）的显式条目，则该条目始终优先生效；`identity_header` 永远无法覆盖用户自定义的头部配置。对于无效的 `identity_header` 条目，系统会发出警告并予以忽略——它们绝不会阻止服务器建立连接。在基于标准输入输出的服务器上，该键会被忽略并伴随警告提示（因为标准输入输出传输方式不支持头部信息）。  

## 基本配置参考  

Hermes 会从 `~/.hermes/config.yaml` 文件的 `mcp_servers` 部分读取 MCP 配置。  

### 常见键值

| 键值 | 类型 | 含义 |
|---|---|---|
| `command` | 字符串 | stdio MCP 服务器的可执行文件 |
| `args` | 列表 | 传递给 stdio 服务器的参数 |
| `env` | 映射结构 | 传递给 stdio 服务器的环境变量 |
| `url` | 字符串 | HTTP MCP 接口地址 |
| `headers` | 映射结构 | 远程服务器的 HTTP 请求头 |
| `client_cert` | 字符串 \| 列表 | 用于 mTLS 的客户端证书——可以是完整的 PEM 格式路径，也可以是 `[证书, 密钥]` / `[证书, 密钥, 密码]` 的格式 |
| `client_key` | 字符串 | 当客户端证书与密钥分开存储时的私钥 PEM 格式路径 |
| `identity_header` | 映射结构 | 用于 HTTP/SSE 服务器的可选用户身份标识头——格式为 `{名称, 来源: 静态\|配置文件, 值}` |
| `timeout` | 数字 | 工具调用的超时时间 |
| `connect_timeout` | 数字 | 初始连接超时时间（同时也会限制 MCP 的 `initialize` 握手过程） |
| `idle_timeout_seconds` | 数字 | 若在指定秒数内没有工具调用，将回收该 stdio 服务器（值为 `0` 表示永不回收，为默认值）。下次有工具调用时，服务器会自动透明重启 |
| `max_lifetime_seconds` | 数字 | 当服务器总运行时间达到此数值时将回收——值为 `0` 表示永不回收，为默认值。下次使用时会自动透明重启 |
| `enabled` | 布尔值 | 若设置为 `false`，Hermes 将完全跳过该服务器 |
| `supports_parallel_tool_calls` | 布尔值 | 若设置为 `true`，该服务器上的工具可以同时运行 |
| `tools` | 映射结构 | 用于针对特定服务器筛选工具及定义相关策略 |

### 最简 stdio 示例

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
```

### 回收内存占用较高的 stdio 服务器

基于浏览器的 MCP 服务器（例如 `@playwright/mcp`）在首次调用工具后会持续保留完整的 Chromium 进程——这将占用数百 MB 的内存且永不释放。启用自动回收功能后，当达到空闲时间或生命周期限制时，该服务器将会被销毁；而在下次有工具被调用时，它会无缝重启（其所有工具会始终保持注册状态）：

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

对于知名的 MCP 服务器，`hermes mcp add` 命令支持 `--preset` 参数，该参数会自动填入传输相关的详细配置，从而省去用户自行查找对应命令及参数的麻烦。不过这些预设仅提供默认值——您在相同命令行中指定的其他任何配置（如环境变量、请求头、过滤规则等）依然会优先生效。

| 预设名称 | 连接的 MCP 服务器 |
|---|---|
| `codex` | Codex CLI 的 MCP 服务器（通过标准输入输出的 `codex mcp-server`）。要求 PATH 环境变量中已包含 `codex` CLI。 |

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

您可以选择任何本地名称（例如使用 `hermes mcp add my-codex --preset codex` 即可）；预设值仅用于提供 `command`/`args` 的默认值。

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

在实际使用中，通常无需手动调用带前缀的名称——Hermes 会在常规推理过程中自动识别工具并选择对应的函数。

### 工具结果清洗与 `_meta` 字段

在模型接收到 MCP 工具的结果之前，会对其进行两项处理：

- **移除不可见的 Unicode 标签字符。** 范围在 U+E0000–U+E007F 之间的字符在终端和聊天界面中不会显示，但模型却能完全识别——这类字符常被恶意或受控服务器用作注入提示信息的渠道。Hermes 会从工具结果、资源内容及工具描述中删除这些字符，而合法的表情符号标签序列（如国家旗帜 🏴󠁧󠁢󠁳󠁣󠁴󠁿）则会被保留。
- **保留供应商提供的 `_meta` 字段，但移除协议预留的键。** 当服务器为工具结果附加 `_meta` 映射（如 `com.example/handoff` 这样的供应商命名空间）时，Hermes 会将其与结果内容一同传递给模型。遵循 MCP 规范的键名规则，那些带有协议预留前缀的键——即以 `modelcontextprotocol` 或 `mcp` 为前缀后再跟有其他标签的键，例如 `modelcontextprotocol.io/...` 或 `tools.mcp.com/...`——会被剔除。如果最终没有内容需要传递给模型，则会完全省略 `_meta` 字段。

## MCP 实用工具

在支持的情况下，Hermes还会为MCP资源及提示词相关功能注册一些实用工具：

- `list_resources`
- `read_resource`
- `list_prompts`
- `get_prompt`

这些工具会以相同的前缀模式在每个服务器上被注册，例如：

- `mcp_github_list_resources`
- `mcp_github_get_prompt`

### 重要提示

这些实用工具现在具备能力感知功能：
- 仅当MCP会话真正支持资源操作时，Hermes才会注册资源相关工具；
- 仅当MCP会话真正支持提示词操作时，Hermes才会注册提示词相关工具。

因此，那些仅提供可调用工具而不存在资源或提示词的服务器，将不会获得这些额外的封装工具。

## 按服务器过滤

您可以控制每个MCP服务器向Hermes贡献哪些工具，从而实现对工具命名空间的精细化管理。

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

仅会注册那些 MCP 服务器工具。

`include`/`exclude` 中的条目也可以使用通配符模式（如 `*`、`?`、`[...]`，匹配时区分大小写）：例如 `include: ["*_dns_*"]` 会注册所有名称中包含 `_dns_` 的工具。不包含特殊字符的普通条目则执行精确匹配。对于那些按产品系列提供了数千个自动生成的端点工具的服务器，使用通配符是进行筛选的实用方法。

### 将服务器工具加入黑名单

```yaml
mcp_servers:
  stripe:
    url: "https://mcp.stripe.com"
    tools:
      exclude: [delete_customer]
```

除被排除的工具外，所有服务器工具均已完成注册。

### 全局模式

这两份列表既接受精确的名称，也支持 fnmatch 风格的全局模式——这对于像 Cloudflare 的 API MCP 这样拥有海量工具（约 3,300 个工具）的庞大系统而言尤为必要，因为若逐个端点排除特定产品类别，操作起来将极为繁琐。

```yaml
mcp_servers:
  cloudflare:
    url: "https://mcp.cloudflare.com/mcp?codemode=false"
    auth: oauth
    tools:
      exclude: ["*_radar_*", "*_accounts_dlp_*", "*_zones_web3_*"]
```

不包含通配符元字符（`*`、`?`、`[`）的条目将进行精确匹配——例如 `docs`，仅会排除名为 `docs` 的工具，而不会排除 `docs_search`。

### 优先级规则

当两者同时存在时：

```yaml
tools:
  include: [create_issue]
  exclude: [create_issue, delete_issue]
```

`include` 选项更具优势。

### 同样适用于过滤工具

您也可以单独禁用 Hermes 添加的工具封装层：

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

如果您的配置过滤掉了所有可调用的工具，并禁用了或省略了所有支持的实用功能，Hermes 也不会为该服务器创建一个空的运行时 MCP 工具集。这样一来，工具列表就能保持整洁。

## 运行时行为

### 发现时间

Hermes 在启动时会发现 MCP 服务器，并将其工具注册到常规工具注册表中。

### 动态工具发现

MCP 服务器可以在运行时通过发送 `notifications/tools/list_changed` 通知来告知 Hermes 其可用工具已发生变化。收到该通知后，Hermes 会自动重新获取该服务器的工具列表并更新注册表——无需手动执行 `/reload-mcp` 操作。

这对于那些功能会动态变化的 MCP 服务器非常有用（例如，在加载新的数据库架构时添加工具，或在某个服务离线时移除工具的服务器）。

此刷新过程具有锁保护机制，可防止同一服务器频繁发送通知导致重复刷新。对于提示项或资源的变化通知（`prompts/list_changed`、`resources/list_changed`），虽然已收到，但暂时不会触发相应操作。

### 重新加载

如果您需要更改 MCP 配置，请使用：

```text
/reload-mcp
```

此操作会从配置文件中重新加载MCP服务器，并更新可用的工具列表。它也是重新检测受可用性限制的工具（如Docker、`HASS_TOKEN`、OAuth等）的明确方式：否则会冻结当前会话中的工具集，因此只有在执行 `/reload-mcp`、`/new` 操作或进行上下文压缩时，才会识别出在会话期间新增的凭证或守护进程。关于服务器自身推送的运行时工具变更，请参阅上文中的[动态工具发现](#dynamic-tool-discovery)部分。

### 工具集

每台已配置的MCP服务器，在提供了至少一个已注册的工具后，也会生成一个运行时工具集：

```text
mcp-<server>
```

这使得在工具集层面理解 MCP 服务器变得更加容易。

## 安全模型

### 标准输入环境过滤

对于标准输入服务器，Hermes 不会原封不动地传递用户的完整 Shell 环境。只有明确配置的 `env` 变量以及安全的默认值会被传递过去，从而有效防止意外泄露敏感信息。

### 配置级暴露控制

这一新的过滤功能同时也具备安全管控作用：
- 禁用那些不希望模型看到的危险工具
- 为敏感服务器仅开放最基本的白名单
- 当不需要暴露某些功能时，可禁用资源/提示词包装器

## 典型应用场景

### 具有最小化问题管理功能的 GitHub 服务器

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
- 发现功能失效
- 您的过滤配置排除了这些工具
- 该服务器上不存在相应的功能能力
- 服务器被设置为 `enabled: false` 状态而处于禁用状态

如果您是刻意进行过滤，那么出现这种情况是正常的。

### 为何资源相关工具或提示工具未显示？

因为 Hermes 现在仅在同时满足以下两个条件时才会注册这些封装工具：
1. 您的配置允许使用它们
2. 服务器会话确实支持该功能能力

这是有意为之的设计，旨在确保工具列表的准确性。

## 并行调用工具

默认情况下，MCP 工具是依次运行的——一次一个。如果您的 MCP 服务器提供了可以安全并行运行的工具（例如只读查询、独立的 API 调用），您可以选择启用并行执行模式：

```yaml
mcp_servers:
  docs:
    command: "docs-server"
    supports_parallel_tool_calls: true
```

当 `supports_parallel_tool_calls` 的值为 `true` 时，Hermes 可以在单次工具调用批次中同时执行该服务器上的多个工具，其方式与处理内置只读工具（如 web_search、read_file 等）时相同。

:::caution
仅建议为那些工具可以安全地同时运行的 MCP 服务器启用并行调用功能。如果这些工具需要读取或写入共享状态、文件、数据库或外部资源，请在启用此设置之前仔细检查可能出现的读写竞争问题。
:::

## MCP 抽样支持

MCP 服务器可以通过 `sampling/createMessage` 协议向 Hermes 请求大语言模型推理服务。这样一来，MCP 服务器便可以委托 Hermes 代为生成文本——这对于那些需要大语言模型功能但自身没有模型访问权限的服务器而言非常有用。

对于所有支持该功能的 MCP 服务器，抽样功能**默认处于开启状态**。如需针对特定服务器进行配置，可在其设置中找到 `sampling` 键进行相关配置：

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

采样处理模块配备了滑动窗口速率限制器、单次请求超时机制以及工具循环深度限制，旨在防止使用情况失控。系统会针对每个服务器实例记录相关指标（请求数、错误次数、已使用的令牌数）。

如需为特定服务器禁用采样功能：

```yaml
mcp_servers:
  untrusted_server:
    url: "https://mcp.example.com"
    sampling:
      enabled: false
```

## MCP 提示功能支持

通过 `elicitation/create` 协议（需使用 mcp Python SDK ≥ 1.11.0），MCP 服务器可在工具调用过程中向用户请求结构化输入。Hermes 会通过现有的确认机制来处理**表单模式**的提示请求——即通过 CLI/TUI 中的交互式提示，或 Telegram、Slack 等网关平台上的确认按钮——从而确保无论会话在何处，请求都能送达您手中。而**URL 模式**的提示请求（即服务器将用户引导至外部 URL 的方式）则因不被支持而被拒绝。

默认情况下，每台服务器均开启此提示功能。您可在 `elicitation` 键下对其进行配置：

```yaml
mcp_servers:
  my_server:
    command: "my-mcp-server"
    elicitation:
      enabled: true    # default: true
      timeout: 300     # seconds to wait for your answer (default: 300)
```

默认的5分钟超时时间与网关的默认设置保持一致，这样在异步环境中使用的用户就有足够的时间作出响应，避免服务器过早放弃连接。处理程序会记录每台服务器的指标数据，包括请求数、已接收数、被拒绝数以及错误数。

## 将Hermes作为MCP服务器运行

除了能够**连接到**MCP服务器之外，Hermes本身也可以**充当**MCP服务器。这样一来，其他具备MCP功能的智能体（如Claude Code、Cursor、Codex或任何MCP客户端）就能利用Hermes的消息传递功能——查看对话列表、读取消息历史记录，以及在所有已连接的平台上发送消息。

### 何时使用此功能

- 您希望让Claude Code、Cursor或其他编程智能体通过Hermes来发送和读取Telegram/Discord/Slack中的消息
- 您需要一个能够同时连接Hermes所有消息平台的单一MCP服务器
- 您已经拥有一个已运行且连接了多个平台的Hermes网关

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

MCP 服务器提供了 10 种工具，既包括与 OpenClaw 的频道桥接功能相对应的工具，也包含专为 Hermes 设计的频道浏览器：

| 工具 | 描述 |
|------|------|
| `conversations_list` | 列出当前活跃的聊天对话。可按平台筛选或通过名称搜索。 |
| `conversation_get` | 根据会话密钥获取某次对话的详细信息。 |
| `messages_read` | 查看某次对话的最新消息记录。 |
| `attachments_fetch` | 从特定消息中提取非文本附件（如图片、媒体文件）。 |
| `events_poll` | 从指定位置开始轮询新的对话事件。 |
| `events_wait` | 进行长轮询/阻塞等待，直到下一事件出现（近乎实时）。 |
| `messages_send` | 通过特定平台发送消息（例如 `telegram:123456`、`discord:#general`）。 |
| `channels_list` | 列出所有平台上的可用聊天目标。 |
| `permissions_list_open` | 显示当前桥接会话中待处理的审批请求列表。 |
| `permissions_respond` | 授权或拒绝待处理的审批请求。 |

### 事件系统

MCP 服务器内置了实时事件桥接功能，可持续轮询 Hermes 的会话数据库以获取新消息。这使得 MCP 客户端能够近乎实时地掌握新出现的对话情况：

```
# Poll for new events (non-blocking)
events_poll(after_cursor=0)

# Wait for next event (blocks up to timeout)
events_wait(after_cursor=42, timeout_ms=30000)
```

事件类型：`message`、`approval_requested`、`approval_resolved`。

事件队列存储在内存中，会在桥接组件连接时开始运行。历史消息可通过 `messages_read` 获取。

### 选项

```bash
hermes mcp serve              # Normal mode
hermes mcp serve --verbose    # Debug logging on stderr
```

### 工作原理

MCP 服务器直接从 Hermes 的会话存储中读取对话数据——`~/.hermes/state.db` 是主要数据源，而 `sessions.json` 仅作为旧版兼容的备用文件存在。一个后台线程会持续轮询数据库以获取新消息，并维护一个内存中的事件队列。在发送消息时，它会使用与定时任务推送以及 `hermes send` CLI 相同的内部发送引擎（`tools/send_message_tool.py`）。

对于读取操作（如列出对话、查看历史记录、轮询事件），无需运行网关即可完成。而发送操作则必须运行网关，因为平台适配器需要保持活跃的连接。

### 当前限制

- 目前内置的 `hermes mcp serve` 只提供**基于标准输入输出**的 MCP 服务器功能。如果需要 HTTP 协议的 MCP 服务器，需单独运行适配器；或者更常见的做法是使用 Hermes 的 MCP **客户端**版本，该版本同时支持标准输入输出和 HTTP 协议（在 `mcp_servers.yaml`/`config.yaml` 中配置 `url` 和 `headers`；详情请参见上文的[HTTP 服务器](#http-servers)部分）。
- 通过针对文件修改时间进行优化的数据库轮询机制，事件轮询间隔约为 200 毫秒（当文件未被修改时无需处理）。
- 目前还不支持 `claude/channel` 推送通知协议。
- 只能发送纯文本内容（无法通过 `messages_send` 功能发送媒体文件或附件）。

## 相关文档

- [在 Hermes 中使用 MCP](/guides/use-mcp-with-hermes)
- [CLI 命令](/reference/cli-commands)
- [Slash 命令](/reference/slash-commands)
- [常见问题解答](/reference/faq)
