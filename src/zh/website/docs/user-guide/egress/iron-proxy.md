# 出站凭证注入代理（iron-proxy）

当 Hermes 在 Docker 终端沙箱中运行你的智能体时，该沙箱通常会存放真实的上游 API 密钥（如 `OPENROUTER_API_KEY`、`OPENAI_API_KEY` 等）。若智能体能够获取到沙箱内的命令执行权限，便可通过执行 `cat ~/.config/openrouter/auth.json` 或 `printenv | grep -i key` 等命令窃取这些密钥。

出站代理解决了这一问题：沙箱中仅存储不可见的**代理令牌**，而不会保存真实密钥。所有从沙箱发出的出站流量都会先经过主机上运行的本地 [iron-proxy](https://github.com/ironsh/iron-proxy) 守护进程（基于 Apache-2.0 协议和 Go 语言实现），该进程会终止 TLS 加密，并在将请求转发给上游服务之前用真实凭证替换代理令牌。即便沙箱被攻破，攻击者也只能获得仅在**已配置的受信任代理边界**内有效的令牌——该边界的构成包括证书颁发机构的私钥以及代理端点的完整性验证信息。如果流量被重定向到攻击者控制的代理基础设施（例如被盗用的证书私钥或被劫持的代理端点），那么这些令牌就不再具备保护作用。

在此版本中，出站代理仅与 Docker 后端集成。目前 Modal、Daytona、SSH 和 Singularity 还未接收代理环境变量或证书颁发机构相关配置。

## 它是什么

- 主机上运行一个受管理的 `iron-proxy` 子进程，该进程会被延迟安装到 `~/.hermes/bin/iron-proxy` 中；
- 本地证书颁发机构文件位于 `~/.hermes/proxy/ca.crt`，沙箱会信任该文件，从而使 iron-proxy 能够实现 TLS 中间人拦截并重写请求头；
- 配置文件 `proxy.yaml` 存放在 `~/.hermes/proxy/proxy.yaml` 中，其中列出了允许访问的上游主机地址以及密钥转换映射关系；
- 文件 `mappings.json` 用于记录各个代理令牌对应的具体环境变量。

沙箱会设置 `HTTPS_PROXY=http://host.docker.internal:9090`、`HTTP_PROXY=http://host.docker.internal:9091`，同时将 `OPENROUTER_API_KEY` 等标准提供程序环境变量替换为不可见的代理令牌。此外，还会导出类似 `HERMES_PROXY_TOKEN_<ENV_NAME>` 的别名以便于调试。现有的提供程序 SDK 会读取常规的环境变量名称，在 `Authorization` 头中发送代理令牌，而 iron-proxy 的 `secrets` 转换功能则会用来自主机端守护进程环境的真实值来替换这些令牌。

## 不属于什么

- 它**不是**用于入站连接的 `hermes proxy` 命令，后者实际上是一个 OAuth 集成型反向代理。两者命令不同（分别为 `hermes egress`），作用方向也不同；
- 它**不**位于你的本地终端与提供程序之间——仅存在于沙箱与提供程序之间；
- 它**不会**重写主机进程发起的进程内大语言模型调用所使用的凭据。这类调用仍会直接使用你的 `.env` 文件中的配置键值。其安全防护范围针对的是*沙箱*，而非主机。

## 快速开始

```bash
# 1. Install the iron-proxy binary (pinned version, SHA-256 verified)
hermes egress install

# 2. Run the wizard: generates CA, mints proxy tokens for every provider key
#    in your env, writes proxy.yaml.
hermes egress setup

# 3. Start the proxy daemon
hermes egress start

# 4. Check status
hermes egress status
```

`hermes egress setup` 会从您的环境中检测提供商密钥。如果这些密钥仅存储在 `~/.hermes/.env` 文件中（且未在 shell 中导出），该工具会自动读取该文件——您无需先执行 `export` 操作。

之后当您再次运行 `setup` 命令时（例如添加新的允许列表主机、更换令牌或切换凭证来源），由于配置存储在内存中，该工具会首先停止正在运行的守护进程，随后**主动提议为您重启它**，以便立即生效。在终端模式下，它会询问是否操作；如需始终自动重启，请传递 `--restart` 参数，若希望保持进程关闭状态，则使用 `--no-restart` 参数。其他情况下若要应用更改，只需执行 `hermes egress restart` 即可完成停止并重启的操作。

一旦启动，Docker 终端后端会自动：

- 将 `~/.hermes/proxy/ca.crt` 文件挂载到沙箱中的 `/etc/ssl/certs/hermes-egress-ca.crt` 路径下。  
- 设置 `HTTPS_PROXY`、`HTTP_PROXY`、`REQUESTS_CA_BUNDLE`、`SSL_CERT_FILE`、`CURL_CA_BUNDLE`、`NODE_EXTRA_CA_CERTS` 等环境变量，确保所有常见的 HTTP 运行时请求均通过代理传输，并信任相应的证书颁发机构。  
- 设置 `NODE_OPTIONS=--use-openssl-ca`（该值会追加到 `docker_env.NODE_OPTIONS` 中已存在的配置之后），使 Node.js 通过 OpenSSL 证书存储库来处理其他证书包相关变量所控制的证书验证——关于由此可能产生的缺陷，请参见下文的 [Node.js 非对称证书注意事项](#nodejs-asymmetric-ca-caveat)。  
- 添加 `--add-host=host.docker.internal:host-gateway` 参数，以便沙箱能够访问 Linux 环境下的主机端代理（Docker Desktop 在 macOS/Windows 系统上会自动处理此功能）。  
- 按照标准的提供程序环境变量名称（例如 `OPENROUTER_API_KEY`）导出代理令牌；同时，针对每一种生成的映射，还会提供一个名为 `HERMES_PROXY_TOKEN_<ENV_NAME>` 的诊断用别名。  

## 配置说明

完整的配置信息存储在 `~/.hermes/config.yaml` 文件的 `proxy:` 部分中。各参数的默认值已在文档中注明；所有配置均为可选项。

```yaml
proxy:
  # Master switch. When false the feature is a complete no-op — no
  # binaries downloaded, no docker mounts added, no subprocess started.
  enabled: false

  # Tunnel listener port. Sandboxes hit http://host.docker.internal:<port>.
  tunnel_port: 9090

  # Auto-download the pinned iron-proxy binary on first use.
  auto_install: true

  # Where iron-proxy looks up the real upstream secrets at egress time.
  #   env       — process env (default). Whatever is in your ~/.hermes/.env
  #               at proxy-start time is the source of truth.
  #   bitwarden — refetch from Bitwarden Secrets Manager on each proxy
  #               restart. Rotation in the BW web app propagates without
  #               touching .env. Requires `secrets.bitwarden.enabled: true`.
  credential_source: env

  # When true (default), the Docker backend refuses to start a sandbox if
  # the proxy is enabled but not running. Set to false to fall back to the
  # legacy "real credentials inside the sandbox" posture when the proxy
  # is unavailable.
  enforce_on_docker: true

  # When `credential_source: bitwarden` but the BWS access token /
  # project_id is missing OR the bws fetch returns no values for mapped
  # providers, the daemon raises by default (matches the spirit of "I
  # asked for rotation — don't silently use stale env values").  Set
  # to true to opt back into the legacy host-env fallback — useful for
  # migrations where you want to start switching to BW mode but haven't
  # wired every secret yet.
  allow_env_fallback: false

  # SSRF deny list applied to outbound traffic.  Omit / leave null to
  # use the safe default: loopback (v4 + v6), link-local (incl. cloud
  # metadata IPs at 169.254.169.254), RFC1918, IPv6 ULA, IPv4-mapped-v6,
  # CGNAT, and the RFC2544 benchmark range.  Set to an explicit `[]`
  # to opt out entirely (only sensible in hermetic tests).
  upstream_deny_cidrs: null

  # Extra allowed upstream hosts beyond the bundled defaults.
  # Wildcards (`*.foo.com`) are supported. The defaults cover OpenRouter,
  # OpenAI, Anthropic, Google, xAI, Mistral, Groq, Together, DeepSeek,
  # and Nous Research.
  extra_allowed_hosts: []
```

### 默认允许的上游主机列表

```
openrouter.ai           *.openrouter.ai
api.openai.com          api.anthropic.com
generativelanguage.googleapis.com
api.x.ai                api.mistral.ai
api.groq.com            api.together.xyz
api.deepseek.com        inference.nousresearch.com
```

如果您的智能体需要使用列表中未列出的上游服务——如自托管的推理端点、额外的云端大语言模型或MCP服务器——可将其添加到 `proxy.extra_allowed_hosts` 中。通配符会与完整的主机名进行匹配（例如 `*.example.com` 可匹配 `api.example.com` 和 `staging.example.com`，但无法匹配 `example.com` 本身）。

### 默认的SSRF禁止CIDR范围

无论是否有允许列表，这些范围都会被应用。iron-proxy会在网络边界层拒绝这些地址，因此即便通过允许列表中的主机名发起DNS重绑定攻击，也无法访问IMDS或您的内部网络：

| CIDR | 用途 |
|---|---|
| `127.0.0.0/8`, `::1/128` | 回环地址（IPv4和IPv6） |
| `169.254.0.0/16`, `fe80::/10` | 链路本地地址——**包括位于 `169.254.169.254` 的AWS/GCP/Azure IMDS节点** |
| `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | RFC1918标准网络范围 |
| `fc00::/7` | IPv6 ULA地址段 |
| `::ffff:0:0/96` | IPv4映射的IPv6地址——可防止双栈IMDS绕过机制 |
| `100.64.0.0/10` | RFC6598规定的CGNAT地址范围（被AWS VPC及K8s容器网络使用） |
| `198.18.0.0/15` | RFC2544标准中的测试用地址范围 |

如需覆盖默认设置，可自行定义列表并赋值给 `proxy.upstream_deny_cidrs`。若完全不需要此类限制（例如在需要进行回环地址测试的场景中），则可将该参数设置为空列表 `[]`。

### 绑定策略

代理服务绝不会绑定 `0.0.0.0` 地址。由于iron-proxy v0.39版本仅支持**每个守护进程单次绑定**，因此默认的绑定地址因平台而异：

- **Linux系统**：使用Docker桥接网关（默认地址为`172.17.0.1:<tunnel_port>`）。容器通过`host.docker.internal`访问代理，而`--add-host=host.docker.internal:host-gateway`指令会将该地址解析为正是这个桥接网关的IP地址——仅绑定到回环接口的地址在沙箱内部是无法被访问的。该桥接IP属于主机`docker0`接口上的地址，因此不会暴露在局域网中；不过默认桥接网络中的其他容器可以访问它，但请求仍需使用生成的代理令牌以及被列入白名单的上游服务器。如果未检测到Docker桥接（即未安装或未运行Docker），则系统会发出警告并回退到回环绑定模式。

- **macOS / Windows Docker Desktop系统**：采用回环绑定方式（地址为`127.0.0.1:<tunnel_port>`）。Docker Desktop自带的VPNkit功能会将`host.docker.internal`路由至主机，因此容器能够访问回环地址，这也是暴露风险最低的绑定方式。

如果某个局域网内的设备因代理令牌泄露而无法获取该代理，那么外部网络同样也无法访问该代理——因为两种绑定方式均不可从外部网络抵达。

此外，我们还将`metrics.listen: 127.0.0.1:0`固定为该地址，这样守护进程内置的指标服务就会使用一个临时的回环端口，而非默认的`:9090`端口——否则它会与`tunnel_port: 9090`争夺同一个套接字，导致守护进程因“地址已被占用”而无法启动。需注意，`:0`这个临时端口号每次启动时都是随机生成的，且不会在任何地方显示出来，因此通过此设置实际上相当于禁用了指标服务功能。

即便在 PATH 中存在某个恶意 `ip` shim，且该 shim 能够注入非私有 IPv4 地址作为桥接地址（如 `0.0.0.0`、公共地址、多播地址、链路本地地址等），回退到环回接口的机制依然有效——因为我们绝不会绑定任何无法通过 `ipaddress.IPv4Address` 结合 `is_*` 方法进行验证的地址。

## 支持的身份验证方案

`secrets` 转换功能会替换匹配位置中出现的所有代理令牌，其覆盖范围不仅限于 `Authorization: Bearer`：

| 提供商 | 环境变量 | 替换为 |
|---|---|---|
| OpenRouter、OpenAI、Groq、Together、DeepSeek、Mistral、xAI、Nous | `*_API_KEY` | `Authorization` 请求头 |
| Anthropic 原生服务 | `ANTHROPIC_API_KEY` | `x-api-key` + `Authorization` |
| Azure OpenAI | `AZURE_OPENAI_API_KEY` | `api-key` + `Authorization`（适用于 `*.openai.azure.com`、`*.cognitiveservices.azure.com`、`*.services.ai.azure.com` 等域名） |
| Google AI Studio（Gemini） | `GEMINI_API_KEY` / `GOOGLE_API_KEY` | `x-goog-api-key` 请求头或 `?key=` 查询参数 |

`GEMINI_API_KEY` 与 `GOOGLE_API_KEY` 被视为同一组凭证：系统会生成一个统一的代理令牌，并以这两个名称中的任意一个注入沙箱中，只要主机环境中含有其中任意一个名称，即可完成凭证识别。

## 不支持的提供商

那些需要请求签名或依赖 SDK 生成的 OAuth 机制的身份验证方案，无法通过静态请求头替换来实现替换——如果相关环境变量存在，沙箱中将持有该提供商的**真实凭证**，此时出站流量隔离保障功能将无法完全生效。

| 环境变量 | 提供商 | 原因 |
|---|---|---|
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | AWS Bedrock / SageMaker | 需要使用 SigV4 签名的请求 |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP Vertex AI | 通过服务账户文件生成 OAuth 凭证 |

这些环境变量通常存在于大多数开发人员的笔记本电脑上，用于其他工具（如 terraform、gcloud、aws CLI、ECR 推送等）。它们会在向导及 `hermes egress status` 命令中显示警告，但不会阻止代理启动。如果您在沙箱环境中不使用这些提供商，可通过 `unset` 这些变量来消除警告。

## 与 Bitwarden 的集成

如果您已经通过 [`hermes secrets bitwarden setup`](../secrets/bitwarden) 使用了 Bitwarden Secrets Manager，那么出口代理可以直接从该服务获取真实凭证，而无需依赖 `os.environ`：

```bash
hermes egress setup --from-bitwarden
```

该设置会将 `proxy.credential_source` 设定为 `bitwarden`，并自动从您的 Bitwarden 项目中获取对应的提供程序环境变量名称。

### 密钥轮换机制

当 `credential_source: bitwarden` 时，iron-proxy 守护进程会在**每次启动时**通过命令 `bws secret list <project_id>` 从 Bitwarden Web 应用中重新获取机密信息。因此，完整的轮换流程如下：

1. 在 Bitwarden 网页应用中轮换某个密钥。
2. 在主机上执行 `hermes egress stop && hermes egress start`。
3. 此之后启动的沙箱进程会自动将代理令牌替换为新值。

整个过程无需修改任何 `.env` 文件，也无需在主机上重启 Hermes。仅有代理守护进程会使用新值——您的主机进程及 `os.environ` 环境变量均保持不变。

### 启动时的严格校验

当 `credential_source: bitwarden` 时，`hermes egress start` 会在向导层进行预检，而 `_build_proxy_subprocess_env` 函数则会在守护进程层再次进行验证：

- 若 Bitwarden 的访问令牌环境变量未被设置，则拒绝启动，并提示用户请先设置该变量后重新运行；或者可选择使用 `hermes egress setup --no-bitwarden` 切换回环境变量模式。
- 若 `secrets.bitwarden.project_id` 的值为空，则拒绝启动，并提示用户执行 `hermes secrets bitwarden setup` 命令进行配置。
- 若通过 `bws secret list` 查询后，某个或多个已映射的提供程序没有返回任何密钥，则拒绝启动，并列出缺失的提供程序名称。

此类严格校验是刻意设计的。在 BW 模式下回退到主机环境变量，恰恰会重新引入原本希望通过 Bitwarden 路径避免的“数据过时”问题（用户选择 BW 模式正是为了获得可靠的密钥轮换保障，而自动回退则会破坏这一保障）。

配置标志 `proxy.allow_env_fallback: true` 会为迁移场景恢复到旧的“若无法访问 BWS，则自动回退至主机环境”的行为。当您需要逐个将密钥移入 BW，并希望守护进程使用当前可用的值启动时，可使用此选项。

### 更改凭证来源

| 来源 | 目标 | 命令 |
|---|---|---|
| 环境变量 | Bitwarden | `hermes egress setup --from-bitwarden` |
| Bitwarden | 环境变量 | `hermes egress setup --no-bitwarden` |

**若不使用上述任一标志重新运行 `hermes egress setup`，则保留现有的 `credential_source` 设置**——向导不会自动让您回退到环境变量模式。这一点很重要，因为一旦配置了 Bitwarden 模式，您便享受到了所承诺的密钥轮换保障；若要更改回环境变量模式，必须明确指定“我想要使用环境变量”。

## 斜杠命令

CLI 子命令结构：

```
hermes egress install                  # download the pinned iron-proxy binary
hermes egress install --force          # re-download even if a managed copy exists

hermes egress setup                    # interactive wizard
hermes egress setup --tunnel-port N    # override the tunnel listener port
hermes egress setup --from-bitwarden   # use BWS as credential source (fail-loud)
hermes egress setup --no-bitwarden     # explicitly switch back to env mode
hermes egress setup --rotate-tokens    # mint fresh tokens for every provider
                                       #   (default preserves existing)

hermes egress start                    # spawn the managed proxy daemon
hermes egress stop                     # SIGTERM (then SIGKILL after 5s grace)
hermes egress restart                  # stop (if running) then start — needed when
                                       #   upstream SECRETS change (rotation, new provider)
hermes egress reload                   # hot-reload the ruleset from proxy.yaml via the
                                       #   management API — no restart, no dropped
                                       #   connections (allowlist / mapping edits)

hermes egress status                   # binary + config + pid + listening state + mappings
hermes egress status --show-tokens     # print proxy tokens in full
                                       #   (default: redacted prefix + suffix only)

hermes egress disable                  # flip proxy.enabled = false
                                       #   (does not stop a running proxy)

hermes egress config                   # print the path to proxy.yaml for debugging
```

### 令牌轮换

默认情况下，`hermes egress setup` 会**保留**那些已拥有代理令牌的提供方的令牌。添加新提供方时，仅会为该新提供方生成新的令牌，现有令牌保持不变。这样一来，在重新运行向导时，运行中的沙箱就不会出现 401 错误。

`--rotate-tokens` 参数可轮换所有令牌：

```bash
hermes egress setup --rotate-tokens
```

当已存在令牌且标准输入为终端设备时，向导会提示用户进行确认。

```
⚠  --rotate-tokens will invalidate proxy tokens in every running
   Hermes sandbox.  They will start 401-ing against upstreams until restarted.
Type 'rotate' to confirm:
```

在非终端调用场景（如持续集成任务、脚本等）中，系统会跳过提示符，此时该标志将被视为用户的明确操作。在覆盖当前 `mappings.json` 文件之前，系统会先将其复制到一个带有时间戳的副本中，以便用户能够手动恢复原始文件。

```
backup: ~/.hermes/proxy/mappings.json.rotated-20260524T143012
```

当执行 `hermes egress setup` 命令并重新编写配置或令牌映射时，它会终止正在运行的守护进程，因为该守护进程会将旧的 YAML 内容保留在内存中。而在使用 `--rotate-tokens` 选项之后则不会如此：

```bash
hermes egress start
```

正在运行的容器中仍保留着旧的令牌，需要重新启动才能获取新的令牌。新的持久化 Docker 容器会带有“egress-posture”标签，因此 Hermes 不会再为新的会话重用之前用于出站连接或令牌轮换的容器。

## 状态目录结构

iron-proxy 所有维护的数据都存储在 `~/.hermes/proxy/` 目录下：

| 路径 | 权限 | 用途 |
|---|---|---|
| `~/.hermes/proxy/`（目录） | `0o700` | 仅所有者可访问及遍历 |
| `ca.crt` | `0o644` | 分发到沙箱环境中的公共 CA 证书 |
| `ca.key` | `0o600` | CA 签名密钥——绝不会离开主机 |
| `proxy.yaml` | `0o600` | iron-proxy 配置文件；每次执行 `setup` 命令时都会被重写 |
| `mappings.json` | `0o600` | 沙箱代理令牌与上游环境变量的映射关系 |
| `mappings.json.rotated-*` | `0o600` | 通过 `--rotate-tokens` 命令生成的备份文件 |
| `iron-proxy.pid` | `0o600` | 正在运行的守护进程的 PID |
| `iron-proxy.nonce` | `0o600` | 用于防止 PID 重复利用的每次启动生成的随机值 |
| `iron-proxy.log` | `0o600` | 守护进程的标准输出/标准错误日志——**在 v0.39 版本中包含每条请求的记录** |
| `audit.log` | `0o600` | 为未来版本中专门的每条请求审计流预留；提前创建以便在上游系统集成时仍能满足隐私保护要求 |

CA 私钥是最敏感的文件。它从创建之初就被设置为 `0o600` 权限，且第一字节未被设置 umask 值以防止 TOCTOU 攻击，同时还设置了 `O_NOFOLLOW` 属性，从而防止具有相同用户 ID 的攻击者通过植入的符号链接来重定向该文件。PID 文件、随机值文件、守护进程日志以及审计日志也均采用相同的保护措施。

### iron-proxy v0.39 版本的日志记录功能

在当前固定的二进制版本（**v0.39.0**）中，iron-proxy会将所有输出内容——包括守护进程层面的诊断信息以及每条请求的记录——写入**`~/.hermes/proxy/iron-proxy.log`**文件。由于v0.39版本的`config.Log`结构中并未设置独立的`audit_path`字段，因此我们无法将每条请求的记录定向写入该路径下的专用日志流。

尽管如此，我们仍会预先创建权限为`0o600`且带有`O_NOFOLLOW`属性的`~/.hermes/proxy/audit.log`文件，原因如下：

1. 这样做是为未来的版本升级预留路径：当固定版本升级到支持`log.audit_path`功能的版本后，每条请求的记录将自动写入该文件，而无需操作人员进行额外配置。**在此之前，该文件的容量始终为0字节——请勿将监控、告警或取证工具指向此文件。目前所有操作仍应使用`iron-proxy.log`。**
2. 从文件创建之初就设置`0o600`权限，可避免在v0.40及以上版本发布时出现因默认umask设置导致文件未被正确创建的问题。

在版本升级到来之前，对于以下两类用户而言，均应将`iron-proxy.log`视为权威日志来源：
- **守护进程层面事件**：启动提示、绑定错误、关闭原因、转换错误等，适用于运维操作与故障排查。
- **每条请求的记录**：连接到白名单内的上游服务、密钥交换触发、被列入黑名单等，适用于取证分析与合规审查。

这两类日志在系统重启后仍会持续追加内容。如果担心长期运行的主机磁盘占用问题，可使用logrotate工具对它们进行轮转处理。

## 工作原理

```
┌──────────────┐                ┌──────────────┐                ┌─────────────┐
│ Docker       │ CONNECT /     │ iron-proxy    │ HTTPS w/       │ OpenRouter  │
│ sandbox      ├──────────────▶│ (host:9090)   ├───────────────▶│ / OpenAI /  │
│              │ HTTP forward  │               │ real API key   │ Anthropic …  │
│ has:         │ w/ proxy tok  │ mints leaf    │                │             │
│ - proxy tok  │ in Auth hdr   │ cert from CA  │                │             │
│ - CA cert    │               │ matches token │                │             │
│ - HTTPS_PROXY│               │ swaps secret  │                │             │
└──────────────┘               └──────────────┘                └─────────────┘
                                       │
                                       │ daemon + per-request log (combined on v0.39)
                                       ▼
                              ~/.hermes/proxy/iron-proxy.log
                              (~/.hermes/proxy/audit.log reserved for v0.40+ split stream)
```

1. Sandbox会发起一个HTTPS请求，例如`POST https://openrouter.ai/v1/chat/completions`，并在请求头中添加`Authorization: Bearer hermes-proxy-openrouter-…`（此处为代理令牌，而非真正的API密钥）。
2. 由于设置了`HTTPS_PROXY`环境变量，该请求会以CONNECT隧道的形式被发送至iron-proxy。
3. iron-proxy会检查允许列表，确认`openrouter.ai`在允许范围内。
4. 接着，iron-proxy会使用我们的CA机构签发的证书为`openrouter.ai`生成临时叶子证书，终止TLS连接，并对请求内容进行检测。
5. “secrets”转换功能会匹配`Authorization`请求头中的代理令牌字符串，然后用来自iron-proxy自身环境的真实`OPENROUTER_API_KEY`值替换它。
6. 请求会被重新加密后转发至OpenRouter。
7. 在v0.39版本中，该请求会被记录到`~/.hermes/proxy/iron-proxy.log`文件中。从v0.40版本开始，由于已支持流式日志记录功能，每条请求的记录将会被保存到`~/.hermes/proxy/audit.log`中，而守护进程级的诊断信息则仍保留在`iron-proxy.log`中。更多详情请参阅[iron-proxy v0.39的日志记录功能](#logging-on-iron-proxy-v039)。

对于不在允许列表中的主机（例如`https://attacker.example.com/leak?key=...`），在有任何数据离开该主机之前，系统就会以HTTP 403错误拒绝请求。此类拒绝操作会被记录在`iron-proxy.log`中，其中会标注上游主机名称及请求来源的Sandbox信息。

### 将CA证书分发到Sandbox中

当Docker后端以`proxy.enabled: true`参数启动容器且守护进程处于监听状态时，它会在执行`docker run`命令时添加相应的参数。

| 参数 | 用途 |
|---|---|
| `-v ~/.hermes/proxy/ca.crt:/etc/ssl/certs/hermes-egress-ca.crt:ro` | 以只读方式挂载根证书机构文件 |
| `-e HTTPS_PROXY=http://host.docker.internal:9090` | 适用于 Python httpx / curl / Go 默认传输库 / Node fetch |
| `-e HTTP_PROXY=http://host.docker.internal:9091` | 适用于基于 curl + wget 的普通 HTTP 请求——普通 HTTP 转发监听端口为 `tunnel_port + 1` |
| `-e NO_PROXY=127.0.0.1,localhost,::1` | 沙箱内的回环开发服务器可绕过代理设置 |
| `-e REQUESTS_CA_BUNDLE=…ca.crt` | 适用于 Python `requests` 库 |
| `-e SSL_CERT_FILE=…ca.crt` | 适用于 Python `ssl` 模块/OpenSSL——**替换**系统默认证书存储 |
| `-e CURL_CA_BUNDLE=…ca.crt` | 适用于 curl 工具——**替换**系统默认证书存储 |
| `-e NODE_EXTRA_CA_CERTS=…ca.crt` | 适用于 Node.js——**添加**到系统默认证书存储中 |
| `-e NODE_OPTIONS="<your value> --use-openssl-ca"` | 适用于 Node.js——通过 OpenSSL 证书存储处理请求（参数会追加；原有的 `--max-old-space-size` 等选项依然有效） |
| `-e HERMES_EGRESS_PROXY=1` | 设置该参数后，代理服务器可读取相关值，从而知晓代理正在被使用 |
| `-e OPENROUTER_API_KEY=<proxy-token>` | 标准提供商环境变量会接收代理令牌，以确保现有 SDK 能继续正常工作 |
| `-e HERMES_PROXY_TOKEN_<NAME>=…` | 为每种映射提供的诊断别名；其值与标准提供商环境变量相同 |
| `--add-host=host.docker.internal:host-gateway` | 仅适用于 Linux 环境；Docker Desktop 会自动完成该映射 |

#### Node.js 非对称根证书机构的注意事项

`REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` / `CURL_CA_BUNDLE` 会**替换**沙箱内的系统 CA 存储。而 `NODE_EXTRA_CA_CERTS` 则用于**补充**该存储内容。原则上，沙箱中的 Node.js 进程可以通过直接创建原始的 `net.Socket` 并自行发起 TLS 握手来绕过代理——由于系统 CA 存储仍会信任真实的上游证书，因此这样的请求能够成功完成，而 Python 或 curl 则会在验证阶段失败。

`NODE_OPTIONS=--use-openssl-ca` 会被追加到 `docker_env.NODE_OPTIONS` 中已存在的配置之后。这样能强制 Node.js 使用由 `SSL_CERT_FILE` 控制的 OpenSSL 证书存储，从而减少两者之间的差异。不过，此方法无法覆盖那些在调用 `tls.connect()` 或 `https.request()` 时明确指定自身 `ca` 参数的代码，但能够解决大部分常见情况。

这是 v1 版本中已知的限制。如需上游团队解决该问题，请关注 [github.com/ironsh/iron-proxy/issues](https://github.com/ironsh/iron-proxy/issues)；在此期间，切勿在依赖出口隔离功能的沙箱中运行会创建原始套接字的不可信 Node 代码。

### docker_env 配置冲突

如果在 `docker_env:` 配置块中设置了用于控制代理的环境变量（虽不常见但有可能发生），当 `enforce_on_docker: true` 被设置时，Hermes 将拒绝启动该沙箱。这些变量包括：

- 出口控制相关变量：`HTTPS_PROXY`、`HTTP_PROXY`、`NO_PROXY`、`REQUESTS_CA_BUNDLE`、`SSL_CERT_FILE`、`CURL_CA_BUNDLE`、`NODE_EXTRA_CA_CERTS`
- 真实服务提供商相关的环境变量：`mappings.json` 中列出的所有变量（例如 `OPENROUTER_API_KEY`、`OPENAI_API_KEY`）

错误示例：

```
docker_env in config.yaml overrides egress-proxy variables
['HTTPS_PROXY', 'OPENROUTER_API_KEY']; enforce_on_docker is enabled.
Remove these keys from docker_env or disable enforce_on_docker to
opt out of egress isolation.
```

当设置 `enforce_on_docker: false` 时，相同情况会以警告形式出现，此时你的 `docker_env` 中的配置值将优先生效——这非常适合用于迁移或测试场景，但你也意味着主动放弃了隔离保障。

## PID与随机数防伪机制

守护进程的 PID 文件是通过 `O_EXCL`、`O_NOFOLLOW` 指令并配合所有权检查来创建的。当多次调用 `hermes egress start` 时，会出现以下两种结果之一：

- 若现有的 PID 文件指向正在运行的 iron-proxy，则第二次启动会被拒绝，同时会提示“已有进程正在运行”，并建议先执行 `hermes egress stop`；
- 若现有的 PID 文件已失效（即守护进程已崩溃），则第二次启动会解除对该文件的引用并尝试再次启动。

除此之外，每次调用 `start_proxy` 时都会在两个位置生成一个新的随机数：

- 守护进程的环境变量中设置 `HERMES_IRON_PROXY_NONCE=<nonce>`；
- 文件 `~/.hermes/proxy/iron-proxy.nonce` 中也存储该随机数，该文件的权限为 0o600，与 PID 文件同级。

当执行 `hermes egress stop`（或任何其他检测 `_pid_alive` 的操作）时，为了确认某个 PID 仍然对应着*本*守护进程——而非 iron-proxy 崩溃后被分配了相同 PID 的其他进程——系统会读取 `/proc/<pid>/environ` 文件来查找该随机数。正是由于有了磁盘上的副本，这一机制才能在多次调用 CLI 时依然有效（而内存中的 `_proxy_nonce` 是进程级变量，每次调用 `hermes` 命令时都会重置）。

如果随机数检查失败，代码将退而求其次，通过比对 `argv[0]` 的基名与 `iron-proxy` 的值来进行匹配。此外，`stop_proxy` 会在发送 SIGTERM 信号之前获取 `/proc/<pid>/stat` 文件中的启动时间，并在5秒的宽限期结束后再次进行验证——如果启动时间发生了变化，说明该进程在等待期间已被重新使用，系统会发出警告并抑制 SIGKILL 信号的发送。

## 安全模型

**可防范的风险：**

- Docker 沙箱中被注入的恶意代理程序读取 `printenv` 命令的输出或凭证文件，进而窃取真实密钥。
- 沙箱中的受控依赖组件试图向任意主机发送数据——默认的拒绝白名单机制会阻止未知目的地的连接。
- 代理程序尝试访问云元数据端点（如 `169.254.169.254`）——`iron-proxy` 通过 `upstream_deny_cidrs` 默认禁止此类访问，包括其 IPv4 映射的 IPv6 形式 `::ffff:169.254.169.254`。
- 通过白名单中的主机名将请求重定向到私有 IP 地址——拒绝列表会在连接时进行校验，而非在加入白名单时。
- 同一用户 ID 的本地进程试图读取 `iron-proxy` 守护进程的环境变量以窃取机密信息——只有映射中指定的环境变量名称会被传递，而非整个主机环境变量。
- 内网中的其他设备利用泄露的沙箱代理令牌消耗您的 API 配额——该代理始终绑定在 Linux 系统的 Docker 桥接网关或 Docker Desktop 的回环接口上，绝不会绑定到 `0.0.0.0`，因此外部网络无法访问它。

**无法防范的风险：**

- 宿主进程被攻破。即便代理进程本身遭到入侵，宿主机 `~/.hermes/.env` 文件中的真实密钥依然会泄露。这一机制属于多层防御策略，旨在防范沙箱被攻破的情况，而非宿主系统本身被入侵。
- **可信代理边界丧失**。令牌交换机制的前提是沙箱会信任已挂载的证书颁发机构证书（`/etc/ssl/certs/hermes-egress-ca.crt`），并且所有流量都会真正传输到*我们的*安全代理节点。如果该证书颁发机构的私钥被盗，或者沙箱的出站流量被重定向到攻击者控制的代理基础设施，中间人攻击者便可以提供有效的证书，此时代理令牌就不再能起到有效的防护作用（参见 [MITRE ATT&CK T1588.004](https://attack.mitre.org/techniques/T1588/004/) —— 通过获取TLS证书材料来实现中间人攻击）。因此必须妥善保护证书颁发机构私钥（其权限为 `0600`，仅限宿主机访问），以及代理端点。
- 使用原始套接字绕过 `HTTPS_PROXY` 设置的沙箱进程。代理无法拦截未经过其路由的流量。通过设置 `NODE_OPTIONS=--use-openssl-ca` 可以在一定程度上缓解Node.js环境下的这一问题（详见上文注意事项）。
- 被明确挂载到Docker容器中的凭证文件（如 `terminal.credential_files` 或通过技能注册的方式挂载的文件）。出站防护机制仅能保护提供商提供的环境变量，无法检查任意被挂载的文件。切勿将真实的提供商凭证挂载到受严格出站防护约束的沙箱环境中。
- 允许的数据外传。如果 `api.openai.com` 被列入白名单，智能体便可将外传数据嵌入发送至该主机的请求体中。守护进程日志虽会记录此类请求的发生，但无法阻止其发生。
- 未受限制的提供商（如 AWS Bedrock SigV4、GCP Vertex service-account OAuth）。相关环境变量仍保留在沙箱环境中；若启用这些功能，相应的凭证将完全绕过代理。详情请参阅[未受限制的提供商](#uncovered-providers)。
- iron-proxy 的内存密钥清除机制。该 Go 程序会在进程内存中存储真实的凭证信息；若发生核心转储，或同一用户身份的攻击者读取 `/proc/<pid>/mem` 文件，这些凭证便可能被泄露。此安全层不覆盖此类情况。

## 失败模式

- **未安装二进制文件且 `auto_install: true`** — 首次执行 `hermes egress setup` 或 `hermes egress start` 时会自动下载该文件，并通过 SHA-256 值与上游提供的 `checksums.txt` 文件进行校验。
- **未安装二进制文件且 `auto_install: false`** — 执行 `start` 命令时会失败，并显示提示需手动安装的明确信息。
- **`enabled: true` 但代理未运行** — 在默认设置 `enforce_on_docker: true` 的情况下，Docker 沙箱创建过程会因相关错误而拒绝启动。若将 `enforce_on_docker` 设置为 `false`，系统则会直接使用真实凭证进行外联操作，并记录警告信息。
- **端口冲突** — iron-proxy 会立即退出；`hermes egress start` 会输出最近的 20 行日志，随后以非零状态码失败。
- **上游主机被拒绝访问** — 沙箱会从代理处收到 HTTP 403 错误响应，响应体内会说明哪些主机未被允许访问。智能体检测到该错误后会将其上报。
- **请求使用云元数据 IP（169.254.169.254）**——无论白名单设置如何，都会被 `upstream_deny_cidrs` 拒绝。
- **`docker_env` 与用于控制代理的变量冲突（强制启用）**——创建沙箱时会因这些冲突变量的存在而被拒绝，并会显示冲突变量的名称。
- **`docker_forward_env` 尝试转发受保护的提供程序密钥（强制启用）**——创建沙箱会被拒绝；需从 `docker_forward_env` 中移除该密钥，或通过设置 `proxy.enforce_on_docker: false` 关闭此功能。
- **`docker_extra_args` 覆盖了代理环境/网络控制设置（强制启用）**——创建沙箱会被拒绝；用户指定的 `-e HTTPS_PROXY=...`、`--env-file` 或 `--network` 参数会在 Hermes 生成的参数之后执行，从而可能绕过出口限制。
- **`credential_source: bitwarden` 中缺少 BWS 访问令牌**——`hermes egress start` 命令会拒绝执行，并给出 `--no-bitwarden` 作为恢复提示。
- **iron-proxy 未在 5 秒内绑定**——相关进程将被终止，其 pid 文件也会被删除，错误信息会显示端口号及 `iron-proxy.log` 的尾部内容。
- **同时发起多个 `hermes egress start` 调用**——如果第一个进程的守护进程仍在运行，第二个调用会因“已有进程正在运行”而被拒绝；否则，第二个调用会删除旧的 pid 文件并继续执行。

## 故障排除

### “拒绝启动：未设置 BWS_ACCESS_TOKEN”

您已启用 `credential_source: bitwarden`，但 Shell 环境中不存在对应的访问令牌环境变量。可能的原因有：

```bash
export BWS_ACCESS_TOKEN=…   # one-shot
hermes egress start
```

或者将其移至 `~/.hermes/.env` 文件中。或者重新切换回环境变量模式：

```bash
hermes egress setup --no-bitwarden
```

### “iron-proxy 立即退出”

请查看 `~/.hermes/proxy/iron-proxy.log` 文件的最后20行。常见原因包括：

- 端口已被占用 → 更改 `proxy.tunnel_port` 值，或终止占用9090端口的进程
- `proxy.yaml` 配置无效 → 运行 `hermes egress setup` 重新生成配置文件
- CA证书/密钥权限设置错误 → 执行 `chmod 0o600 ~/.hermes/proxy/ca.key` 设置正确权限

### “iron-proxy 在5秒内未绑定到 \<bind-host\>:9090端口”

守护进程已启动，但未能绑定监听端口。这通常意味着程序在启动时出现卡顿或正在执行耗时操作。请检查 `~/.hermes/proxy/iron-proxy.log` 文件。异常进程会自动被终止，对应的PID文件也会被清理，此时可直接重新运行 `hermes egress start`。

### Linux环境下沙箱与代理连接超时

容器会将 `host.docker.internal` 解析为Docker桥接网关地址，而代理服务正绑定在该地址上，但由于主机防火墙（常见的是默认拒绝入站的 `ufw`）拦截了 `docker0` 接口上的容器到主机的流量，从而导致连接超时。可从容器内部进行验证：

```bash
docker run --rm --add-host host.docker.internal:host-gateway busybox \
  nc -zv -w 3 host.docker.internal 9090
```

如果执行 `hermes egress status` 命令时显示“正在监听”，但操作仍超时，那么请在防火墙中放行该桥接子网，例如对于 UFW 系统：

```bash
sudo ufw allow in on docker0 to any port 9090 proto tcp
sudo ufw allow in on docker0 to any port 9091 proto tcp
```

(9091 表示位于 `tunnel_port + 1` 端口的普通 HTTP 转发监听器。)

### 沙箱环境从代理服务器收到 `HTTP 403` 错误

沙箱内的代理尝试访问了未列入 `proxy.extra_allowed_hosts` 列表中的主机。403 错误响应中会说明是哪个主机。若希望允许该访问，可在配置文件中添加相应内容：

```yaml
proxy:
  extra_allowed_hosts:
    - api.example.com
    - "*.staging.example.com"
```

接着执行 `hermes egress setup`（用于重新生成 `proxy.yaml`），随后运行 `hermes egress stop && hermes egress start`。

### Sandbox环境中出现SSL验证错误

原因可能是CA证书未被加载到Sandbox环境中（这种情况较为罕见，因为当 `proxy.enabled: true` 时，Docker后端会自动处理此操作），或者您的镜像所使用的HTTP客户端正在从非标准的环境变量中读取配置。

```bash
# Inside the sandbox:
cat /etc/ssl/certs/hermes-egress-ca.crt | head -1
# Should print: -----BEGIN CERTIFICATE-----
env | grep -E "^(REQUESTS|CURL|SSL|NODE).*CA"
# Should list all four CA-bundle env vars pointing at /etc/ssl/certs/hermes-egress-ca.crt
```

如果证书不存在，请检查是否已设置 `proxy.enabled: true`，同时确认 `hermes egress status` 的显示值为 `Listening yes`。若环境变量缺失，可能是沙箱镜像中的启动脚本删除了这些变量——请检查您的 `docker_env` 配置。

### 沙箱从上游收到 `HTTP 401` 错误

常见原因有两点：

1. **重新配置时令牌被覆盖**。您执行了 `hermes egress setup --rotate-tokens` 命令（或通过其他方式轮换了令牌），但仍在运行的沙箱仍保留着旧令牌。此时需要重启这些沙箱。
2. **Bitwarden 刷新失败且未产生明显提示**。在新的错误提示机制下本不应出现此情况，但如果您设置了 `proxy.allow_env_fallback: true`，守护进程可能会带着过时的环境变量启动。请检查守护进程的环境变量（位于 `/proc/<iron-proxy-pid>/environ`）中是否包含应有的 `OPENROUTER_API_KEY` 等键值。

### 父进程终止后出现“地址已被使用”错误

在执行 `hermes egress start` 过程中，父级 Hermes 进程发生了崩溃（如监听检测时被强制中断、内存不足或系统异常）。新的修复逻辑会在 `Popen` 调用后立即写入进程标识文件，从而使这些“孤儿进程”能够被重新恢复：

```bash
hermes egress stop   # finds the orphan via the pidfile, kills it
hermes egress start
```

如果执行 `hermes egress stop` 后显示“iron-proxy 未运行”，但通过 `ps` 命令仍能看到该守护进程，这说明 PID 文件出现了不同步。可采取以下手动恢复方法：

```bash
pkill -TERM iron-proxy
rm -f ~/.hermes/proxy/iron-proxy.pid ~/.hermes/proxy/iron-proxy.nonce
hermes egress start
```

### 查看每次请求的行为日志

在固定版本的二进制文件（**v0.39**）中，守护进程级别的事件以及每次请求的记录都会被写入 `~/.hermes/proxy/iron-proxy.log` 文件中。该文件的格式为以换行符分隔的 JSON 格式。如需查找特定的上游服务，可使用 Grep 命令进行搜索：

```bash
grep '"upstream":"openrouter.ai"' ~/.hermes/proxy/iron-proxy.log | tail -20
```

或可实时观看：

```bash
tail -f ~/.hermes/proxy/iron-proxy.log | jq
```

当固定版本的版本号升级到 v0.40 及以上时（该版本新增了 `log.audit_path`），每次请求的记录将会被写入 `~/.hermes/proxy/audit.log`，而 `iron-proxy.log` 则仅用于存储守护进程层面的事件。在版本升级之前，`audit.log` 仍是一个空的占位文件（初始权限设置为 `0o600`，以便后续的守护进程继承严格的权限控制）——建议您立即将日志轮转或监控工具配置到 `iron-proxy.log` 上，待版本升级后再着手添加 `audit.log` 的相关功能。 

## v1 版本的局限性

- 仅支持 Docker 后端。Modal、Daytona 以及 SSH 连接功能将在后续的独立 PR 中实现。  
- 支持基于签名认证的提供商（如 AWS SigV4、GCP service-account OAuth）可完全绕过代理——详情请参阅[未支持的提供商](#uncovered-providers)。而基于请求头令牌的提供商（如 bearer、`x-api-key`、`api-key`、`x-goog-api-key`）则均被支持。  
- 上游版本不提供原生 Windows 可执行文件，需在 Linux / macOS / WSL 环境下运行。  
- 第一代产品使用的证书为有效期为 10 年的自签名证书。如需更换证书，需手动执行 `openssl genrsa ...` 命令（或等待后续版本中添加的 `hermes egress rotate-ca` 功能）。  
- 在修改配置或映射关系后重新运行设置命令会终止正在运行的守护进程；在令牌更换后，则需要重启守护进程（或仅修改规则集时使用 `hermes egress reload` 命令），并重新启动所有正在运行的沙箱环境。  
- iron-proxy 的内存中机密信息清除功能由上游控制。拥有 `/proc/<pid>/mem` 读取权限的同一用户身份攻击者能够从守护进程的内存中读取被交换出来的机密信息。  
- iron-proxy v0.39 版本仅支持**每个守护进程绑定一个地址**（在 Linux 环境下绑定到 Docker bridge 网关，在 Docker Desktop 环境下绑定到回环接口），并将守护进程日志与每条请求的日志合并为单一日志流。一旦上游版本新增 `proxy.http_listens`（复数形式）和 `log.audit_path` 参数，后续版本即可支持多地址绑定以及独立的审计日志流功能。  

## 参见

- 上游项目：[github.com/ironsh/iron-proxy](https://github.com/ironsh/iron-proxy)  
- 上游文档：[docs.iron.sh](https://docs.iron.sh/)  
- Bitwarden 集成功能：[`hermes secrets bitwarden`](../secrets/bitwarden)  
- Hermes Docker 终端后端：[Docker](../docker)  
- 开发者/贡献者参考资料：[Egress proxy 内部机制](../../developer-guide/egress-internals)
