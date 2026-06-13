---
title: "Pinggy Tunnel — Zero-install localhost tunnels over SSH via Pinggy"
sidebar_label: "Pinggy Tunnel"
description: "Zero-install localhost tunnels over SSH via Pinggy"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Pinggy 隧道

通过 Pinggy 利用 SSH 创建无需安装的本地主机隧道。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 — 通过 `hermes skills install official/devops/pinggy-tunnel` 安装 |
| 路径 | `optional-skills/devops/pinggy-tunnel` |
| 版本 | `0.1.0` |
| 创建者 | Teknium (teknium1)、Hermes Agent |
| 许可证 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Pinggy`、`隧道`、`网络`、`SSH`、`Webhook`、`本地主机` |
| 相关技能 | `cloudflared-quick-tunnel`、[`webhook-subscriptions`](/docs/user-guide/skills/bundled/devops/devops-webhook-subscriptions) |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，Agent 就会依据此内容执行操作。
:::

# Pinggy 隧道技能

通过 Pinggy 的 SSH 反向隧道，将本地服务（开发服务器、Webhook 接收端、MCP 端点、演示程序）暴露到公共互联网上。无需安装任何守护进程——用户现有的 SSH 客户端只需连接到 `a.pinggy.io:443`，Pinggy 便会返回一个公共的 HTTP/HTTPS 地址。

免费套餐：可创建时长为 60 分钟的隧道，使用随机子域名，无需注册。专业套餐（每月 3 美元）需主动选择并获取令牌。

## 适用场景

- 用户希望“将本地服务暴露到网络”、“共享我的开发服务器”、“让该地址对公众可见”、“为某个端口创建隧道”、“为 Webhook 获取公共地址”
- 需要在执行本地任务时接收 Webhook 回调（如来自 Stripe、GitHub、Discord、AgentMail 的请求）
- 需要与远程方共享一次性的 HTTP 演示内容（如 MCP 服务器、Ollama/vLLM 端点、控制面板）
- 主机已安装 SSH，但没有 `cloudflared`/`ngrok` 程序，且安装这些程序又显得过于繁琐

如果主机已配置好 `cloudflared`，建议使用 `cloudflared-quick-tunnel` 技能——Cloudflare 的快速隧道不会在 60 分钟后失效。

## 先决条件

- PATH 环境变量中包含 `ssh` 命令（可通过 `ssh -V` 查验）。Linux、macos 及 Windows 10 及以上系统均已预装，无需额外安装。
- 在创建隧道之前，本地服务需已在 `127.0.0.1:<port>` 地址上监听。Pinggy 会返回相关地址，但在本地服务启动之前，这些地址将无法正常使用，会出现 502 错误。

可选配置：

- `PINGGY_TOKEN` 环境变量：用于启用专业套餐的付费功能（如固定子域名、自定义域名、同时创建多个隧道、取消 60 分钟时间限制）。免费套餐无需提供任何凭证。

## 快速参考

```bash
# Plain HTTP/HTTPS tunnel for port 8000 (free tier)
ssh -p 443 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
    -R0:localhost:8000 free@a.pinggy.io

# TCP tunnel (databases, raw SSH, etc.)
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:5432 tcp@a.pinggy.io

# TLS tunnel (Pinggy can't decrypt — bring your own certs at origin)
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:443 tls@a.pinggy.io

# Basic auth gate (b:user:pass)
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "b:admin:secret+free@a.pinggy.io"

# Bearer token gate (k:token)
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "k:mysecrettoken+free@a.pinggy.io"

# IP whitelist (w:CIDR)
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "w:203.0.113.0/24+free@a.pinggy.io"

# Enable CORS + force HTTPS redirect
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 \
    "co+x:https+free@a.pinggy.io"

# Pro tier (persistent URL, no 60-min cap)
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8000 "$PINGGY_TOKEN+a.pinggy.io"
```

## 步骤——启动隧道并获取 URL

模型应使用 `terminal` 工具。为确保在内容共享的整个过程中隧道都能保持畅通，需以后台进程的方式运行该工具，并从标准输出中解析出公共 URL。

### 1. 确认本地源端已正常启动

```bash
curl -sI http://127.0.0.1:8000/ | head -1
# expect HTTP/1.x 200 (or any non-connection-refused response)
```

如果当前还没有任何程序在监听，首先需要启动相应的服务（例如：`python3 -m http.server 8000 --bind 127.0.0.1`）。此时 Pinggy 会返回一个指向空地址的 URL——在目标服务启动之前，用户将一直看到 502 错误提示。

### 2. 以后台进程方式启动隧道

使用 `terminal(background=True)` 并将输出内容记录到日志文件中（Pinggy 会将相关 URL 输出到标准输出，同时保持连接处于开启状态）：

```bash
LOG=/tmp/pinggy-8000.log
nohup ssh -p 443 \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -R0:localhost:8000 free@a.pinggy.io \
    > "$LOG" 2>&1 &
echo $! > /tmp/pinggy-8000.pid
```

设置 `StrictHostKeyChecking=no` + `UserKnownHostsFile=/dev/null` 可跳过首次连接时的主机密钥验证提示。而 `ServerAliveInterval=30` 能防止因网络处于闲置状态而被 NAT 设备中断 SSH 会话。

### 3. 从日志中解析出 URL 地址

```bash
sleep 4
grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/pinggy-8000.log | head -1
```

预期输出如下：

```
You are not authenticated.
Your tunnel will expire in 60 minutes.
http://yqycl-98-162-69-48.a.free.pinggy.link
https://yqycl-98-162-69-48.a.free.pinggy.link
```

将 `https://...pinggy.link` 这一网址交给用户。 

### 4. 验证

```bash
curl -sI https://<the-url>/ | head -3
# expect 200/302/whatever the local origin actually returns
```

如果出现 `502 Bad Gateway` 错误，说明 SSH 连接已建立，但本地服务端并未处于监听状态——请先执行修复步骤 1。

### 5. 关闭流程

```bash
kill "$(cat /tmp/pinggy-8000.pid)"
# or, if the pid file got lost:
pkill -f 'ssh -p 443 .* free@a\.pinggy\.io'
```

如果您已通过 `terminal(background=True)` 获得 `session_id`，建议使用 `process(action='kill', session_id=...)`。

## 基于用户名关键字的访问控制

Pinggy 会将各种控制标志以 `+` 连接的方式添加到 SSH 用户名中。当用户名中包含 `+` 时，务必对整个 `user@host` 参数加上引号：

| 关键字 | 效果 |
|---------|------|
| `b:user:pass` | HTTP 基本认证验证 |
| `k:token` | 承载令牌头部验证（`Authorization: Bearer <token>`） |
| `w:CIDR` | IP 白名单（可指定单个 IP 或 CIDR 范围，可重复使用） |
| `co` | 添加 `Access-Control-Allow-Origin: *`（CORS 支持） |
| `x:https` | 强制使用 HTTPS —— 自动将 HTTP 重定向为 HTTPS |
| `a:Name:Value` | 添加请求头部 |
| `u:Name:Value` | 更新请求头部 |
| `r:Name` | 删除请求头部 |
| `qr` | 将 URL 的 QR 代码输出到标准输出（便于在移动设备上分享） |

这些关键字可自由组合使用，例如：`"b:admin:secret+co+x:https+free@a.pinggy.io"`。

## Web 调试器（可选）

Pinggy 可将进入的流量镜像到 `localhost:4300` 以便查看。您可以在 SSH 命令中添加本地转发配置：

```bash
ssh -p 443 -L4300:localhost:4300 -R0:localhost:8000 free@a.pinggy.io
```

接着在浏览器中打开 `http://localhost:4300`，即可查看实时的请求/响应对。

## 常见问题

- **免费套餐有60分钟的时长限制。** SSH会话在60分钟后终止，对应的URL也会失效。若需更长时间的连接，可使用 `PINGGY_TOKEN`（Pro版）或通过Shell循环实现自动重启（注意：免费套餐每次重启后URL都会变化）。
- **免费套餐的URL是随机生成的，且每次重启都会改变。** 不要将其加入书签，也不要复制到配置文件中，需每次从日志中重新解析。
- **每个源IP最多只能同时建立一条免费隧道。** 在同一台机器上启动第二条隧道通常会导致第一条隧道中断。Pro版则没有此限制。
- **用户名中的“+”号必须用引号括起来。** 虽然在bash中直接使用 `ssh ... b:admin:secret+free@a.pinggy.io` 可以正常工作，但在对“+”号有特殊处理的Shell环境或通过程序生成命令时则可能出错。务必用双引号将其包裹起来。
- **在没有访问控制标志的情况下，切勿传输任何敏感信息。** 普通的HTTP隧道任何人只要知道URL就能访问。对于非公开服务，请使用 `b:`、`k:` 或 `w:` 前缀。
- **`process(action='log')` 可能无法捕获SSH启动提示信息。** Pinggy会先输出URL，随后SSH会进入交互模式。应始终将输出重定向到日志文件，并直接用 `grep` 查询该文件——操作方式与 `cloudflared-quick-tunnel` 相同。
- **首次运行时会出现主机密钥确认提示。** 默认的OpenSSH配置会要求用户接受Pinggy的主机密钥。为实现无人值守运行，务必添加参数 `-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null`。
- **TCP和TLS隧道返回的是 `<subdomain>.a.pinggy.online:<port>` 格式的地址，而非HTTPS URL。** 需使用不同的正则表达式进行解析（包含 `tcp://` 和端口号）。不要默认所有Pinggy隧道都是HTTP协议。
- **Pro版要求将令牌作为用户名使用，而非作为标志参数。** 应使用格式 `"$PINGGY_TOKEN+a.pinggy.io"`（无需包含 `free@`）。使用令牌时还可以添加 `:persistent` 参数以获得稳定的子域名——详情请参阅 `pinggy.io/docs/`。

## 实现方案

这些方案将本地服务源与Pinggy隧道相结合。每个方案都是独立的——包括启动本地服务、建立隧道、解析URL，最后将结果返回给用户。

### 方案1 — 接收Webhook回调

当外部服务（如Stripe、GitHub、Discord、AgentMail等）需要在执行本地任务时向一个可公开访问的URL发送POST请求时，可使用此方案。

```bash
# 1. Tiny capturing server: every request gets appended to /tmp/webhook-hits.log
cat >/tmp/webhook-server.py <<'PY'
import http.server, json, datetime, pathlib
LOG = pathlib.Path("/tmp/webhook-hits.log")
class H(http.server.BaseHTTPRequestHandler):
    def _capture(self):
        n = int(self.headers.get("content-length") or 0)
        body = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        rec = {"t": datetime.datetime.utcnow().isoformat(), "path": self.path,
               "method": self.command, "headers": dict(self.headers), "body": body}
        with LOG.open("a") as f: f.write(json.dumps(rec) + "\n")
        self.send_response(200); self.send_header("content-type","application/json")
        self.end_headers(); self.wfile.write(b'{"ok":true}\n')
    def do_GET(self): self._capture()
    def do_POST(self): self._capture()
    def log_message(self,*a,**k): pass
http.server.HTTPServer(("127.0.0.1", 18080), H).serve_forever()
PY
nohup python3 /tmp/webhook-server.py >/tmp/webhook-server.log 2>&1 &
echo $! >/tmp/webhook-server.pid

# 2. Tunnel — bearer-token-gate so randos can't pollute the capture log
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:18080 "k:$(openssl rand -hex 12)+free@a.pinggy.io" \
    >/tmp/webhook-pinggy.log 2>&1 &
echo $! >/tmp/webhook-pinggy.pid
sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/webhook-pinggy.log | head -1)
echo "Webhook URL: $URL"

# 3. While the agent works, watch hits land
tail -f /tmp/webhook-hits.log
```

将 `$URL` 提供给需要调用您的服务。清理操作：执行 `kill $(cat /tmp/webhook-server.pid) $(cat /tmp/webhook-pinggy.pid)`。

### 方案 2 — 通过 HTTP/SSE 暴露 MCP 服务器

当远程 MCP 客户端（如另一台机器上的 Claude Desktop、同事的编辑器等）需要连接本地运行的 MCP 服务器时使用此方法。仅适用于支持 HTTP 协议传输的 MCP 服务器——采用标准输入输出模式的服务器无法通过该方式进行隧道传输。

```bash
# 1. Start the MCP server in HTTP mode (example: a FastMCP server on port 8765)
nohup python3 my_mcp_server.py --transport http --port 8765 \
    >/tmp/mcp-server.log 2>&1 &
echo $! >/tmp/mcp-server.pid

# 2. Tunnel with a bearer token — MCP traffic should not be open to the internet
TOKEN=$(openssl rand -hex 16)
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:8765 "k:$TOKEN+free@a.pinggy.io" \
    >/tmp/mcp-pinggy.log 2>&1 &
echo $! >/tmp/mcp-pinggy.pid
sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/mcp-pinggy.log | head -1)
echo "MCP URL: $URL"
echo "Bearer token: $TOKEN"
```

远程客户端会使用 `Authorization: Bearer $TOKEN` 的请求头连接到 `$URL`。Hermes 自带的原生 MCP 客户端配置如下：`{"transport": "http", "url": "<URL>", "headers": {"Authorization": "Bearer <TOKEN>"}}`。

### 方法 3 — 暴露本地 LLM 接口（Ollama / vLLM / llama.cpp）

将本地的模型共享给远程调用方（另一个智能体、手机或团队成员）。Ollama 通常在 `:11434` 端口上监听，而 vLLM 和 llama.cpp 一般则在 `:8000` 端口上运行。

```bash
# Pre-req: the model server is already running on 127.0.0.1:11434 (Ollama default)
TOKEN=$(openssl rand -hex 16)
nohup ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:11434 "k:$TOKEN+co+free@a.pinggy.io" \
    >/tmp/llm-pinggy.log 2>&1 &
echo $! >/tmp/llm-pinggy.pid
sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/llm-pinggy.log | head -1)
echo "Endpoint: $URL"
echo "Token:    $TOKEN"

# Verify
curl -s "$URL/api/tags" -H "Authorization: Bearer $TOKEN" | head
```

`co` 参数用于启用 CORS，以便浏览器端的调用者能够访问该接口。若仅为后端服务调用设计，则可省略 `co` 参数。对于兼容 OpenAI 的 vLLM/llama.cpp 接口，调用者需使用基础地址 `$URL/v1` 并附带 `Authorization: Bearer $TOKEN` 头部信息——但需要注意的是，Pinggy 会原封不动地传递请求体内容，因此模型服务器会直接收到 Pinggy 生成的令牌；本地服务器应被配置为忽略身份验证（因为它本来就只监听 `127.0.0.1` 地址），由 Pinggy 负责执行访问控制。

### 方案 4 — 使用一次性密码共享开发服务器

这是最快捷的“让同事临时测试我正在运行的应用”的方法。系统会生成一个随机密码，仅显示一次，一旦你按下 Ctrl-C，该密码即失效。

```bash
PASS=$(openssl rand -base64 12 | tr -d '+/=' | head -c 12)
echo "Dev server password: $PASS"
ssh -p 443 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 \
    -R0:localhost:3000 "b:dev:$PASS+co+x:https+free@a.pinggy.io"
# URL prints to the terminal. Share URL + password. Ctrl-C to tear down.
```

`b:dev:$PASS` 通过 HTTP Basic 认证机制来限制对特定 URL 的访问。`x:https` 则强制使用 TLS 加密传输。`co` 用于为单页应用前端添加 CORS 支持。

## 验证

```bash
# End-to-end: spin up a trivial origin, tunnel it, hit it, tear down
python3 -m http.server 18000 --bind 127.0.0.1 >/tmp/origin.log 2>&1 &
ORIGIN_PID=$!

nohup ssh -p 443 \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -R0:localhost:18000 free@a.pinggy.io >/tmp/pinggy-verify.log 2>&1 &
SSH_PID=$!

sleep 5
URL=$(grep -oE 'https://[a-z0-9-]+\.[a-z]+\.pinggy\.link' /tmp/pinggy-verify.log | head -1)
echo "URL: $URL"
curl -sI "$URL/" | head -1

kill "$SSH_PID" "$ORIGIN_PID"
```

预期结果：在 curl 命令的输出头部中应显示 `pinggy.link` 这一网址，以及 `HTTP/2 200` 的状态码。
