---
name: mcp-oauth-remote-gateway
description: Manual OAuth for remote MCP servers on headless gateways.
version: 1.0.0
author: Ben Barclay (benbarclay), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [MCP, OAuth, PKCE, Remote-Deployment]
    related_skills: [native-mcp, mcporter, fastmcp]
---

# 远程 Hermes 网关上的 MCP OAuth

## 概述

Hermes 内置的 MCP OAuth 客户端会在 Hermes 进程内部于 `127.0.0.1:<port>` 地址上启动一个一次性运行的 HTTP 监听器，并将该回环地址注册为 OAuth 的 `redirect_uri`。对于运行在用户本机上的本地 CLI 而言，这种方式能够完美工作。然而，当 Hermes 作为远程网关（容器、VPS、消息机器人等）运行时，该方法就会彻底失效——因为用户的浏览器会将 `127.0.0.1` 解析为用户的个人笔记本电脑地址，而非远程容器地址，从而导致授权码根本无法送达 Hermes。

本技能会手动处理整个 OAuth 流程，并将生成的令牌写入 Hermes 令牌存储所期望的特定文件中。这样一来，后续执行 `/reload-mcp` 命令时就能找到已缓存的令牌，从而完全跳过浏览器流程。

## 适用场景

仅在同时满足以下 **所有** 条件时才使用此技能：

1. 用户希望添加一个需要 OAuth 认证的远程 HTTP MCP 服务器（而非使用静态Bearer令牌）。
2. Hermes 正在作为**远程网关**运行（容器、VPS、Docker、托管服务等），而非运行在用户笔记本电脑上的本地 CLI。
3. 该服务器支持带有 PKCE 功能的 OAuth 2.1 标准以及 RFC 7591 规定的动态客户端注册功能（大多数现代 MCP 服务器都支持此功能，例如 Better Stack、Linear、Cloudflare、Datadog 等）。如果该服务器不支持 DCR 功能（GitHub 是典型的例外），则此技能不适用——此时应使用预先注册的 OAuth 应用或个人访问令牌。

**以下场景请勿使用此技能：**
- **本地 CLI Hermes**：只需在 `mcp_servers.<name>` 配置中设置 `auth: oauth`，然后执行 `/reload-mcp` 即可。内置的认证流程会自动打开浏览器，并在本地回环地址上捕获回调信息，能够完美工作。
- **接受静态Bearer令牌（API密钥）的服务器**：如果用户愿意，始终优先使用 `headers.Authorization: "Bearer <token>"` 的方式，因为这种方式更简单，且无需处理令牌刷新问题。
- **GitHub Copilot MCP**（`api.githubcopilot.com/mcp/`）：GitHub 不提供 DCR 功能，因此应使用个人访问令牌或预先注册的 OAuth 应用（参见注意事项 12）。

## 为什么内置 OAuth 流程在远程网关上会失败

Hermes 原生的 MCP OAuth 客户端（位于 `tools/mcp_oauth.py` 文件中）的工作流程如下：

1. 选择一个空闲的本地端口 `P`。
2. 向授权服务端注册一个动态 OAuth 客户端，同时指定 `redirect_uri = http://127.0.0.1:P/callback`。
3. 在 Hermes 进程内部于 `127.0.0.1:P` 地址上启动一个 HTTP 服务器。
4. 打印出授权 URL，然后在本地端点等待接收授权码。

当 Hermes 在远程环境中运行时，`redirect_uri` 中的 `127.0.0.1` 实际上是远程容器的回环地址，而非用户的本机地址。用户完成授权后，浏览器会尝试访问 `http://127.0.0.1:P/callback?code=...`，但由于该地址指向的是用户的个人笔记本电脑，因此无法建立连接。回调信息根本无法送达 Hermes 进程，整个流程会超时，执行 `/reload-mcp` 命令时只会返回“没有可用的 MCP 工具”这样的提示，且不会提供任何详细信息。

可识别的故障症状包括：在 hermes 用户名下出现 `[xdg-open] <defunct>` 类型的进程，`$

```bash
env | grep -iE "HERMES_DASHBOARD_PUBLIC_URL|RAILWAY_PUBLIC_DOMAIN|RAILWAY_STATIC_URL|RAILWAY_SERVICE_.*_URL|PUBLIC_URL|BASE_URL|DOMAIN" \
  | sed -E 's/(TOKEN|SECRET|KEY|PASSWORD)=.*/\1=***REDACTED***/I'
```

当 `HERMES_DASHBOARD_PUBLIC_URL` 被设置时，其值具有权威性。在 Railway 环境中，还需检查 `RAILWAY_PUBLIC_DOMAIN`/`RAILWAY_STATIC_URL`（即 `*.up.railway.app` 这类主机地址）以及 `RAILWAY_SERVICE_*_URL` 这些环境变量，因为它们有时会使用更友好的自定义域名。请将完整的 `https://` 地址提供给用户，并引导他们前往 Connectors/MCP 部分。务必先应用上述的 `sed` 删除操作——这些环境变量通常与 `*_TOKEN`/`*_SECRET` 变量处于相近位置。

**仪表板无法解决的问题（仍需在主机端/Shell 中处理）：**那些依赖 Shell 认证状态的 stdio 服务器（即那些凭据可能在重启后丢失的 CLI `login` 命令），以及任何从 `$HERMES_HOME/.env` 文件中读取凭据的程序。无论如何，这些都属于仪表板功能范围之外。

## 替代解决方案

手动完成 OAuth 授权流程，然后将生成的令牌写入 Hermes 的 `HermesTokenStorage` 本应写入的文件中。这样一来，当执行 `/reload-mcp` 操作时，Hermes 就能找到已缓存的令牌，从而完全跳过浏览器授权流程。

在网关主机的 `terminal` 工具中运行以下 Shell 命令，再通过 `execute_code` 或直接调用 `terminal python3` 来执行 Python 相关步骤（如 PKCE 生成、令牌交换及文件写入）。注意，文件写入操作必须与令牌交换操作放在同一个代码块中（参见注意事项 16）。

### 1. 确认当前为远程网关

```bash
env | grep -iE "HERMES|RAILWAY|CONTAINER"
echo "$DISPLAY $WAYLAND_DISPLAY $SSH_CLIENT"
```

无显示界面且带有远程指示灯的即为远程网关。`tools/mcp_oauth.py::_can_open_browser()`函数会使用相同的环境变量，因此如果Hermes自身的自动检测功能判定为“无头模式”，则内置流程将无法正常运行。

### 2. 查找HERMES_HOME及配置文件路径

```bash
HERMES_HOME=$(python3 -c 'from hermes_constants import get_hermes_home; print(get_hermes_home())')
echo "config: $HERMES_HOME/config.yaml"
echo "tokens: $HERMES_HOME/mcp-tokens/"
```

### 3. 从MCP服务器获取OAuth元数据

MCP服务器会通过RFC 9728标准（OAuth 2.0受保护资源元数据）来公开其OAuth配置信息。401响应中的`WWW-Authenticate`请求头会指示您应在何处查找这些信息：

```bash
curl -sI https://mcp.example.com | grep -i www-authenticate
# → Bearer realm="mcp", resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
```

**并非所有服务器都会返回 `WWW-Authenticate` 头信息。** 有些服务器会直接返回仅包含 `{"errors":["Unauthorized"]}` 的 401 响应，且不提供任何身份验证相关的提示。遇到这种情况时，应直接检测常见的路径：

```bash
for p in \
  /.well-known/oauth-protected-resource \
  /.well-known/oauth-authorization-server \
  /.well-known/openid-configuration ; do
  echo "=== $p ==="
  curl -s -A "python-httpx/0.27" "https://mcp.example.com$p" | head -c 400; echo
done
```

首先获取资源元数据以获得 `authorization_servers`，随后读取 AS 的 `/.well-known/oauth-authorization-server` 文件，从而获取 `authorization_endpoint`、`token_endpoint` 和 `registration_endpoint`。

需要注意：许多服务器位于 Cloudflare 后端，会导致使用纯 `urllib` 用户代理时出现 403 错误。因此，在此流程中的请求中务必设置 `User-Agent: python-httpx/0.27`（或类似值）。

### 4. 动态客户端注册（RFC 7591）

向 `registration_endpoint` 发送 POST 请求，内容如下：

```json
{
  "client_name": "Hermes Agent (manual OAuth)",
  "redirect_uris": ["http://127.0.0.1:8765/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none",
  "scope": "<scopes_from_resource_metadata>"
}
```

如果 AS 的 `scopes_supported` 为空，则完全省略 `scope` 参数——请参阅第 5 步中的注意事项。可使用端口 `8765`（或任意端口，因为不会有其他程序监听该端口）。将 `token_endpoint_auth_method` 设置为 `none` 可将该客户端标记为公共 PKCE 客户端，请保存返回的 `client_id`。

### 5. 使用 PKCE 构建授权 URL

需要生成以下内容：
- `code_verifier`：`secrets.token_urlsafe(64)[:128]`
- `code_challenge`：`base64url(sha256(code_verifier))`（无需添加填充字符）
- `state`：`secrets.token_urlsafe(24)`

查询参数包括：`response_type=code`、`client_id`、`redirect_uri`、`code_challenge`、`code_challenge_method=S256`、`state`，以及 `resource=<mcp_server_url>`（符合 RFC 8707 标准——许多服务器要求此参数以便将令牌与特定的 MCP 资源关联）。仅当 AS 元数据的 `scopes_supported` 是非空数组，且/或者资源元数据指定了特定作用域时，才需添加 `scope=<以空格分隔的作用域列表>` 参数。如果 `scopes_supported: []`，则应省略 `scope` 参数——服务器会自动授予其完整的默认作用域集。在 `scopes_supported` 为空的情况下随意构造作用域字符串，可能会导致某些 AS 返回 `invalid_scope` 错误。

请将 `code_verifier` 和 `state` 值保存到磁盘上（例如路径为 `/tmp/.mcp-oauth-work/<server>.json`，权限设置为 0600）。第 7 步需要使用这些值，且可能在多次对话轮次中都需要。

### 6. 将授权 URL 提供给用户

```
Open this URL in your browser:
<authorize_url>

After approving, your browser will try to load http://127.0.0.1:8765/callback
and fail to connect — THAT'S EXPECTED. Just copy the entire URL from the
address bar (it will contain ?code=...&state=...) and paste it back here.
```

### 7. 将代码转换为令牌

当用户粘贴回调 URL 后：

1. 从查询字符串中解析出 `code` 和 `state`。
2. **验证 `state` 是否与之前保存的值一致**（这是 CSRF 防护措施，切勿跳过）。
3. 向 `token_endpoint` 发送 `application/x-www-form-urlencoded` 格式的请求：
   - `grant_type=authorization_code`
   - `code=<来自回调的值>`
   - `redirect_uri=<与第4步相同的值>`
   - `client_id=<第4步中的值>`
   - `code_verifier=<之前保存的值>`
   - `resource=<mcp_server_url>`（如果授权服务在第5步中要求提供该参数，也需在此处包含）
4. 响应中将包含 `access_token`、`refresh_token`、`token_type`、`expires_in` 以及 `scope` 等字段。

### 8. 按 Hermes 的精确结构存储令牌

`tools/mcp_oauth.py::HermesTokenStorage` 要求在 `$HERMES_HOME/mcp-tokens/` 目录下创建两个文件（该目录权限需设置为 `0o700`，文件权限则需设置为 `0o600`）：

**`<server_name>.json`** — 用于存储 `OAuthToken` pydantic 模型的数据：
```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "refresh_token": "...",
  "scope": "read write"
}
```

**`<server_name>.client.json`** — 即 `OAuthClientInformationFull` 模型：
```json
{
  "client_id": "...",
  "redirect_uris": ["http://127.0.0.1:8765/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none",
  "scope": "read write",
  "client_name": "..."
}
```

请使用 `json.dumps(..., indent=2)` 的方式来编写每个文件。同时需通过 `re.sub(r'[^\w\-]', '_', server_name)[:128]` 对文件名进行清洗处理——该操作方式与 Hermes 令牌存储机制中的 `_safe_filename()` 函数一致。

### 9. 将服务器信息添加到 config.yaml 文件中

```yaml
mcp_servers:
  <name>:
    url: "https://mcp.example.com"
    auth: oauth
    timeout: 180
    connect_timeout: 60
```

### 10. 在要求用户重新加载之前先对令牌进行测试

手动发送一个MCP `initialize`请求，以确认令牌的端到端功能正常——这样就能在用户因再次出现“暂无可用的MCP工具”提示而感到困惑之前，及时发现作用域配置错误、`resource`值不正确以及CF拦截器等问题。

```python
body = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "hermes-debug", "version": "1.0"},
    },
}).encode()
# POST to the MCP URL with:
#   Authorization: Bearer <access_token>
#   Accept: application/json, text/event-stream
#   Content-Type: application/json
#   MCP-Protocol-Version: 2025-06-18
#   User-Agent: python-httpx/0.27
```

响应应为 HTTP 200 状态码，`Content-Type` 为 `text/event-stream`，并包含一个 JSON-RPC 格式的结果，其中含有 `serverInfo` 和 `capabilities` 字段。**请勿使用默认 UA 的 `urllib` 库**——尽管 Hermes（它使用 httpx 库）能够正常工作，但 Cloudflare 仍会阻止请求并返回 403 错误。`scripts/diagnose-oauth-mcp.py` 脚本可自动执行此测试。

### 11. 告诉用户运行 `/reload-mcp`

在重新加载后，Hermes 会检测到 `auth: oauth`，随即调用 `HermesTokenStorage.get_tokens()` 方法查找缓存中的令牌。若找到有效令牌，则跳过浏览器授权流程，直接注册 `mcp_<name>_*` 类的工具。在当前令牌的 `expires_in` 时间到期之前，系统会自动触发刷新。

## 常见问题与经验总结

1. **切勿认为“无头模式”就意味着无法使用 OAuth**。对于本地 CLI 环境，内置的授权流程完全可行；问题仅出现在远程部署场景中，即用户的浏览器与 Hermes 进程位于不同机器上。在断言 OAuth 不可用之前，请先检查实际运行环境。

2. **应查阅源代码而非仅依赖技能文档**。`tools/mcp_oauth.py` 文件以及 `website/docs/` 目录中的 MCP 配置参考是权威依据。在告诉用户某功能“不存在”之前，务必先在源代码树中搜索确认。

3. **Cloudflare 的 UA 过滤机制**。许多 MCP/OAuth 提供商会将基础设施置于 Cloudflare 后端，该平台会对包含 `python-urllib/*` 用户代理的请求在元数据接口上返回 403 错误，即便这些接口本身是公开可访问的。在此类请求中，需在每个请求中设置 `User-Agent: python-httpx/0.27`（或任何类似浏览器的字符串）。由于 Hermes 本身使用 httpx 库，因此在实际连接路径中不会遇到此问题。

4. **在授权请求和令牌请求中均需包含 `resource` 参数**。对于大多数现代 MCP 服务器而言，RFC 8707 规定的资源标识符并非可选——它们用于将生成的令牌与特定的 MCP 资源 URL 关联起来。虽然有时省略该参数也能正常工作，但生成的令牌日后在 MCP 服务器端可能会因作用域/受众错误而失效。

5. **路径末尾的斜杠至关重要**。部分服务器会将资源地址标记为带有斜杠的 `https://mcp.example.com/` 形式，而拒绝使用无斜杠版本生成的令牌。应直接复制来自 `.well-known/oauth-protected-resource` 响应中的 `resource` 值。

6. **`/reload-mcp` 在失败时不会输出任何提示信息**。如果重新加载后显示“没有可用的 MCP 工具”，且没有 `change_detail` 相关行，说明服务器配置存在但连接失败，且错误信息并未上报。此时需查看错误日志，通过手动发送 `initialize` POST 请求直接对令牌进行测试；若一切正常，则建议用户重启整个进程。

7. **断路器机制可承受 `/reload-mcp` 操作**。`tools/mcp_tool.py` 会在模块级别维护一个错误计数字典，并设置较低的触发阈值。一旦达到阈值（例如因令牌过期导致连续多次失败），工具处理程序会在调用服务器之前直接中断流程，因此单次成功的调用不会重置计数器。其表现为：重新加载后显示“已重新连接：X”，但在同一对话中后续请求仍会因“无法连接到服务器”而失败。恢复步骤为：首先尝试 `/reload-mcp`（成本低且不会影响聊天进程）——在当前版本中该操作可清除计数器；仅当重新加载后实时调用仍会中断时，才需升级为重启整个网关进程。切勿直接告知用户“必须重启”。

8. **已过期的 access_token 加上触发的断路器会导致死锁**。自动刷新逻辑是在 MCP 调用路径中运行的，而一旦断路器被触发，该路径就会被中断。仅手动刷新磁盘中的令牌并不足以解决问题——应结合完整重启操作，而非仅使用 `/reload-mcp`。

9. **手动刷新时出现 `invalid_grant` 错误意味着刷新令牌已失效——唯一解决方案是重新授权，切勿反复尝试**。当 access_token 过期时间较长时，服务器端也可能撤销或使刷新令牌失效。此时发送 `grant_type=refresh_token` 的 POST 请求会返回 HTTP 400 错误，内容类似 `{"error":"invalid_grant",...}`（具体表述可能为“未找到授权码”、“令牌已过期”或“刷新令牌无效”）。网关端无法对此进行恢复。应向用户提供两种选择：(a) 重新执行完整的 OAuth 授权流程（步骤 3–10）；(b) 如果提供商提供了静态个人 API 密钥，可切换使用该密钥——无需经历刷新/过期周期，更适合无人值守的远程网关。建议提前检测：在对 OAuth MCP 执行任何创建/更新操作之前，先比较 `expires_at` 时间与当前时间 `time.time()`；若令牌已过期，应立即尝试刷新，并直接显示 `invalid_grant` 错误，而非在操作中途失败。

10. **即使刷新成功，生成的令牌仍被拒绝，说明是服务器端会话已被撤销——唯有重新执行完整的授权码流程才能解决**。这与问题 9 不同。存储的令牌文件看似正常（`expires_at` 时间充足且包含刷新令牌），但实际发送 `initialize` POST 请求时却会因 `401 invalid_token` 错误返回 JSON-RPC 响应，内容类似 `{"error":{"code":-32002,"message":"Session expired. Please re-authenticate."}}`。虽然发送 `grant_type=refresh_token` 的 POST 请求可能**成功**（返回 HTTP 200 状态码及新的 access_token），但新生成的令牌仍会出现相同的 `-32002` 错误。这说明提供商在服务器端撤销了相关的 MCP *会话*；OAuth 刷新机制虽能重新生成凭证，却无法恢复已被撤销的会话。当 OAuth MCP 报告“未连接”时，可遵循以下决策规则：(1) 通过手动发送 `initialize` POST 请求对存储的 access_token 进行测试；(2) 若返回 `401 invalid_token` 错误，则尝试刷新并测试新生成的令牌；(3a) 新令牌可用 → 将其写入文件并重启以清除断路器；(3b) 新令牌仍出现 `-32002`/“会话已过期”错误 → 停止当前操作，这是会话被撤销的情况，应将完整的授权 URL 提供给用户以便重新授权。`scripts/diagnose-oauth-mcp.py` 脚本可自动执行步骤 1–2，并显示当前所处的处理分支。对于那些会话频繁被撤销的无人值守网关，建议使用静态个人 API 密钥。有关提供商定期撤销会话的实际案例，可参考 `references/stripe-mcp-oauth-revocation.md`。

11. **客户端信息文件并非可选**。Hermes 需要 `<server>.client.json` 文件才能知道用于刷新令牌的 `client_id`。若省略该文件，首次刷新就会失败，用户必须重新授权——编写这两个文件正是该技能的核心目的。

12. **切勿让用户手动输入需要打开的重定向 URL**。应使用 `urllib.parse.urlencode()` 函数以编程方式生成授权 URL。作用域中的空格以及 `state` 参数中的特殊字符都可能导致通过字符串拼接生成的 URL 出现问题。

13. **安全性考虑：临时存储文件中包含 `code_verifier`**。在成功完成令牌交换后，应立即删除 `/tmp/.mcp-oauth-work/<server>.json` 文件。一旦该身份验证凭证已被使用，便无需再保留它。

14. **应记录令牌端点实际返回的内容**。授权服务可能会授予比请求更窄或更宽的作用域。应将令牌交换响应中的 `scope` 值写入 `<server>.json` 文件，而非步骤 5 中用户所请求的作用域。当 `scopes_supported: []` 时，用户明确指定的作用域列表在双方均具有权威性：有些服务器会严格遵循用户列出的作用域（通过限制作用域来实现最小权限原则，或在用户需要全部功能时列出完整列表），而有些服务器在注册阶段不会反馈已授予的作用域——只有令牌交换响应才是权威依据。

15. **OAuth 令牌通常也可作为凭证，用于访问提供商的公共 REST API**。`<server>.json` 文件中的 access_token 通常并非“仅限 MCP 使用”——只要用户被授予了相应的资源作用域，使用 `Authorization: Bearer <token>` 格式访问提供商文档中规定的 REST API 即可成功。这是 OAuth 2.0 规范的要求，并非特定提供商的特例。当 MCP 服务器为只读模式而你需要执行写操作时，建议先确认 OAuth 令牌是否可直接用于访问提供商的 REST API，然后再考虑是否需要单独的 API 密钥。

16. **敏感信息遮蔽功能可能会在工具输出中隐藏令牌**。如果启用了敏感信息遮蔽功能，令牌及长字符串会在工具输出中显示为 `***`，因此你无法通过 `print(response)` 的方式在多轮对话中保持 access_token 的可见性。再加上授权码流程中 `code` 值为一次性使用，若打印令牌交换响应，不仅会丢失令牌，还会消耗 `code` 值，迫使用户必须使用新的授权 URL 重新开始流程。**务必在执行令牌交换的同一代码块中，直接将 access_token 写入最终存储文件**。如果出于调试目的必须打印内容，仅应输出 `len(access_token)`、`token_type`、`scope`、`expires_in` 等信息，切勿包含敏感内容。

17. **GitHub MCP（`api.githubcopilot.com/mcp/`）使用的是预先注册的机密 OAuth 应用，而非 DCR + PKCE-public 方式**。其客户端信息中包含真实的 `client_secret`，且 `token_endpoint_auth_method` 设置为 `client_secret_post`。向 `https://github.com/login/oauth/access_token` 发送令牌交换请求时，除 `client_id`、`code`、`code_verifier` 和 `redirect_uri`（PKCE 机制仍会在该机制基础上生效）之外，还必须将 `client_secret` 作为表单字段一同发送。OAuth 应用配置中的重定向 URI 是**固定不变**的——无法更改，因此手动调整监听端口的技巧并不适用；用户只需让浏览器尝试连接该端口失败，然后直接粘贴地址栏中的 URL 即可。

## 不建议的做法

- **不要将 `mcp-remote` 作为备用方案**。它通过 npx 启动一个子进程，而该子进程的 OAuth 回调服务器同样位于远程容器的本地主机上——问题依然存在。只有当 MCP 客户端完全不支持远程 HTTP 协议时（而 Hermes 本身已原生支持），`mcp-remote` 才能发挥作用。

- **如果用户明确要求使用 OAuth，切勿建议其“粘贴 API 令牌，我会帮您添加请求头”**。只有在解释了为何在远程部署环境中原生 OAuth 流程会失败之后，才可提供静态令牌的快捷方式。应尊重用户愿意为获得无需轮换且作用域受限的访问权限而付出额外努力的选择。

- **在未查阅源代码之前，切勿声称 Hermes 不支持某项功能**。在宣称具备某种功能之前，务必先在源代码树中搜索确认。

## 快速参考文件

- `scripts/diagnose-oauth-mcp.py` —— 该脚本可重复运行，默认为只读模式，用于诊断问题。输入服务器名称后，它会测试存储的 access_token，尝试刷新令牌，再测试新生成的令牌，并明确指出当前所处的恢复分支（`TOKEN_OK` 表示已通过断路器处理并重启，`REFRESH_FIXED` 表示已保存新令牌并重启，`SESSION_REVOKED` 表示需要完全重新授权，`REFRESH_DEAD` 表示同样需要完全重新授权或更换 API 密钥）。可通过传递 `--write` 参数来原子化地保存有效的刷新后令牌。该脚本绝不会输出任何敏感信息。**当 OAuth MCP 服务器报告“未连接”时，应首先运行此脚本**——它整合了问题 7/9/10 对应的决策流程。

- `references/stripe-mcp-oauth-revocation.md` —— 该文档提供了一个实际案例（Stripe），介绍了某提供商会定期撤销其 OAuth 会话的情况，以及相应的持久解决方案：即切换为静态的受限 API 密钥。

## 相关内容

- `native-mcp` —— 关于在 Hermes 中配置 MCP 的通用指南。权威的配置参考信息均存放于此处。

- `mcporter` —— 用于在 Hermes 配置之外进行临时 MCP 调用的外部 CLI 工具。
