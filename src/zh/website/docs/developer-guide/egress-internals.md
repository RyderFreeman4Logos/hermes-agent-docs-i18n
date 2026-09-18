---
sidebar_position: 14
title: "Egress proxy internals"
description: "How the iron-proxy egress firewall integrates with Hermes — module layout, lifecycle, security invariants, and extension points"
---

# 出站代理内部架构

本页面从贡献者/插件开发者的角度，详解出站凭证注入防火墙（`hermes egress` / iron-proxy）的架构设计。最终用户的安装与使用指南请参阅 [出站代理](../user-guide/egress/iron-proxy.md)。

威胁模型与高层设计已在用户指南页面中概述；本页面则聚焦于其内部实现方式、与安全相关的代码所在位置，以及在对该系统进行修改时必须遵循的不变原则。 

## 模块结构

```text
agent/proxy_sources/iron_proxy.py     Core: binary install, CA gen, config build,
                                       subprocess lifecycle, mappings I/O, PID/nonce
                                       defense.  Pure-function surface where possible.

hermes_cli/proxy_cli.py               Wizard + slash command handlers.
                                       `hermes egress {install,setup,start,stop,
                                       status,disable,config}`.  Wires the
                                       core module into argparse.

hermes_cli/subcommands/egress.py:_dispatch_egress
                                       Top-level subparser dispatcher.
                                       dest='egress_command' (intentionally
                                       disjoint from the inbound OAuth
                                       `hermes proxy` subparser, which uses
                                       dest='proxy_command').

hermes_cli/config.py: proxy schema    The `proxy:` block in DEFAULT_CONFIG.
                                       Adding a knob means: add it here, add a
                                       wizard prompt or `setdefault` in
                                       proxy_cli.cmd_setup, and document it
                                       in the user-guide page.

tools/environments/docker.py
  _egress_proxy_args_for_docker()     Builds the volume_args / env_overrides /
                                       host_args triple that the Docker backend
                                       injects when `proxy.enabled: true`.

  DockerEnvironment.__init__          Docker-side merge logic: collision
                                       detection against critical egress vars,
                                       NODE_OPTIONS append-merge via the
                                       _HERMES_EGRESS_NODE_OPTIONS_APPEND
                                       sentinel, enforce_on_docker precedence.

tests/test_iron_proxy.py              Hermetic tests (~70).  Binary install
                                       path, config build, mappings I/O,
                                       subprocess lifecycle, docker arg builder,
                                       deny CIDR defaults, bind policy, CA
                                       TOCTOU, ensure_audit_log behaviour, etc.

tests/test_iron_proxy_cli.py          CLI handler unit tests (~20).  Argparse
                                       wiring, fail-loud paths, BWS refresh
                                       wire-up, dest='egress_command'
                                       regression guard.

tests/test_iron_proxy_e2e.py          Live E2E (gated on HERMES_RUN_E2E=1).
                                       Real iron-proxy binary, real curl,
                                       end-to-end token swap verified.
```

## 生命周期

```text
hermes egress install
  -> agent.proxy_sources.iron_proxy.install_iron_proxy(force=...)
       Downloads pinned tarball + checksums.txt from GitHub Releases.
       SHA-256 verification before extraction.
       tarfile.extract(..., filter="data") on Python 3.12+ (PEP 706);
         falls back to plain extract on older Python with member-name
         sanitisation via _pick_tar_member.
       Stage into ~/.hermes/bin/.iron-proxy_XXXX, chmod 755, os.replace
         to ~/.hermes/bin/iron-proxy (atomic).
       _VERSION_CACHE.pop(target) so a forced reinstall re-probes
         --version on next call.

hermes egress setup [--from-bitwarden | --no-bitwarden] [--rotate-tokens]
  -> proxy_cli.cmd_setup
       Step 1. find_iron_proxy(install_if_missing=False) -> install if absent.
       Step 2. ensure_ca_cert()
                 Run openssl genrsa + req via subprocess.
                 Write CA key via os.open(O_WRONLY|O_CREAT|O_TRUNC|O_NOFOLLOW, 0o600)
                   + os.replace.  Never exists on disk under default umask.
                 Write CA cert with 0o644 (public).
       Step 3. discover_provider_mappings() or pull names from BWS via
                 fetch_bitwarden_secrets() when --from-bitwarden.
                 merge_mappings(existing=load_mappings(), discovered,
                                rotate=args.rotate_tokens) preserves prior
                 tokens unless --rotate-tokens is passed.
                 discover_uncovered_providers() and surface warnings.
       Step 4. ensure_audit_log(audit_log_path)   # raises on OSError
               build_proxy_config(...) with defaults applied at the call site
                 (deny CIDRs default, bind policy from _default_http_listen).
               write_proxy_config(cfg)            # atomic via .tmp + os.replace, 0o600
               write_mappings(mappings)           # atomic, 0o600
       Step 5. proxy_cfg["enabled"] = True; credential_source preservation logic
               (do NOT silently downgrade bitwarden -> env on re-run);
               save_config(cfg).

hermes egress start
  -> proxy_cli.cmd_start
       Pre-checks (refuse-start path):
         - credential_source=bitwarden? -> pre-validate access_token_env + project_id
       -> iron_proxy.start_proxy(
            refresh_secrets_from_bitwarden=...,
            bitwarden_config=...,
          )
            existing=_read_pid(); if alive, idempotent return.
            _build_proxy_subprocess_env(...):  ALLOWLIST + mapped real_env_names,
              strip HTTPS_PROXY/etc. to avoid recursion, optional BWS refresh
              (raises on missing values unless allow_env_fallback=true).
            Plant nonce: _proxy_nonce = sha256(urandom(16)); env[NONCE_ENV] = ...
            Open log_path via O_NOFOLLOW + 0o600 + st_uid check.
            Popen with stdin=DEVNULL, stdout=log_fd, stderr=STDOUT,
              start_new_session=True (POSIX).
            Close parent's log_fd in finally.
            _write_pidfile_safely(pidfile, proc.pid)
              O_EXCL + O_NOFOLLOW + uid check + persisted nonce sidecar.
              FileExistsError -> discriminate live vs stale, retry once if stale.
            Install SIGINT/SIGTERM handlers (main-thread only).
            Poll loop (do-while shape):
              while True:
                if proc.poll() is not None: tail log + unlink pidfile + raise
                if _port_listening(probe_host, tunnel_port): break  # probe_host = configured bind host
                if time.time() >= deadline: break  (do-while: checked AFTER first probe)
                time.sleep(0.1)
            If not listening at exit: _kill_and_wait(proc) + unlink pidfile + raise.

hermes egress stop
  -> iron_proxy.stop_proxy
       _read_pid + _pid_alive guard.
       starttime_before = _pid_proc_starttime(pid)   # Linux only; None elsewhere
       os.kill(pid, SIGTERM)
       Wait up to 5s for graceful exit.
       After grace: re-check starttime + _pid_alive.
         If recycled (starttime drift OR _pid_alive False), DO NOT SIGKILL.
         Otherwise os.kill(pid, _KILL_SIGNAL).
       _cleanup_state_files: unlink pidfile + nonce sibling.
```

## 安全不变量

这些是至关重要的属性。一旦修改相关模块，就必须确保这些不变量依然保持不变。凡是涉及回归测试的项都会被明确标注出来。

### 文件系统权限

| 路径 | 权限模式 | 测试用例 |
|---|---|---|
| `~/.hermes/proxy/`（目录） | `0o700` | `test_proxy_state_dir_is_0o700` |
| `ca.key` | `0o600` | `test_ca_key_created_with_0o600` |
| `ca.crt` | `0o644` | （默认值；由 `ensure_ca_cert` 函数中的 `chmod` 指令设置） |
| `proxy.yaml` | `0o600` | （由 `write_proxy_config` 函数中的原子重命名操作后执行 `chmod`） |
| `mappings.json` | `0o600` | （由 `write_mappings` 函数中的原子重命名操作后执行 `chmod`） |
| `iron-proxy.pid` | `0o600` | （由 `_write_pidfile_safely` 函数中的 `os.open(..., 0o600)` 指令设置） |
| `iron-proxy.nonce` | `0o600` | （由 `_write_pidfile_safely` 函数中的 `os.open(..., 0o600)` 指令设置） |
| `audit.log` | `0o600` | `test_ensure_audit_log_creates_with_0o600` |
| `iron-proxy.log` | `0o600` | （由 `os.open(..., 0o600)` 指令结合 `fchmod` 函数设置） |

所有需要写入数据的路径均会使用 `os.open(O_WRONLY | O_CREAT | O_NOFOLLOW, 0o600)` 并配合 `os.fstat().st_uid` 进行权限检查。禁止使用 `shutil.copy2` 加 `os.chmod` 的方式，因为这种方式会导致默认遮罩值泄露。

### 最小化子进程环境变量

函数 `_build_proxy_subprocess_env` 绝对不能使用 `os.environ.copy()` 方法。允许设置的环境变量仅限于 `_PROXY_SUBPROCESS_ENV_ALLOWLIST` 中列出的那些（如 PATH、HOME、locale 等），以及 `load_mappings()` 函数所引用的环境变量名称。其余所有环境变量都应保留在主机上。

相关回归测试用例包括：`test_subprocess_env_strips_unrelated_secrets`、`test_subprocess_env_strips_proxy_recursion_vars`、`test_subprocess_env_keeps_infrastructure_vars`。

### 绑定策略

`_default_http_listen` 会返回一个仅包含一个元素的列表：在 Linux 系统上，该值为 Docker bridge 网关的 IP 地址（容器通过 `host.docker.internal:host-gateway` 访问代理，这一地址最终会解析为桥接网关——而容器内部无法访问回环地址）；在 macOS/Windows Docker Desktop 环境中，则为回环地址（VPNkit 会将 `host.docker.internal` 转发至主机）。若 Linux 系统未检测到 docker0 桥接设备，程序会发出警告并回退至使用回环地址。该值绝不能为 `0.0.0.0`，也不能是 `:PORT`（即 INADDR_ANY）格式。

`_detect_docker_bridge_ip` 会通过 `ipaddress.IPv4Address` 进行验证，凡是属于 `is_unspecified`、`is_loopback`、`is_multicast`、`is_reserved`、`is_link_local` 或 `is_global` 类型的地址都会被拒绝。此外，PATH 路径中存在的恶意 `ip` 接口模块也无法强行注入 `0.0.0.0` 地址。

**v0.39 版本的架构约束与监听器角色（已通过实际二进制文件验证）：** 该二进制文件中的 `config.Proxy` 结构体仅包含单个监听器字段，不存在复数形式的 `http_listens` 列表。`tunnel_listen` 用于处理 CONNECT 及中间人攻击类型的请求（即经过 `HTTPS_PROXY` 转发的流量）；而 `http_listen` 仅负责处理标准形式的纯 HTTP 请求转发（发送给它的 CONNECT 请求会被作为普通请求向上游转发，从而导致 400 错误）。因此，`build_proxy_config` 函数会将 `tunnel_listen` 绑定在 `tunnel_port` 端口，将 `http_listen` 绑定在 `tunnel_port + 1` 端口，两者均绑定在同一台主机上。Docker 后端会将 `HTTPS_PROXY` 设置为 `tunnel_port`，将 `HTTP_PROXY` 设置为 `tunnel_port + 1`。

存活检测机制（`start_proxy`轮询循环及`get_status`函数）会通过 `_read_http_listen_from_config()` 函数读取配置中指定的绑定主机地址，然后对该主机进行检测——如果使用硬编码的回环地址进行检测，那么那些绑定在桥接接口上的正常服务也会被误判为已失效。

回归测试包括：`test_default_bind_is_loopback_not_zero_zero`（确保不会使用INADDR_ANY地址，且生成的YAML文件中不包含`http_listens`项）、`test_default_bind_uses_docker_bridge_on_linux`、`test_default_bind_falls_back_to_loopback_without_bridge`、`test_default_bind_is_loopback_on_macos`，以及`test_detect_docker_bridge_ip_rejects_dangerous`（针对8种不同的攻击输入进行参数化测试）。

### 指标端口冲突问题

在iron-proxy v0.39版本中，`metrics.listen`默认值为`:9090`，这一端口与Hermes的默认`tunnel_port: 9090`相同。因此，`build_proxy_config`函数必须明确将`metrics.listen`设置为`127.0.0.1:0`，这样才能为指标收集功能分配一个临时的回环端口，从而确保无论操作员选择何种`tunnel_port`，该指标端口都不会与代理监听端口发生冲突。

回归测试为：`test_metrics_listener_pinned_to_loopback_ephemeral`。

### 默认拒绝CIDR范围

`_DEFAULT_UPSTREAM_DENY_CIDRS`涵盖了回环地址（IPv4和IPv6版本）、链路本地地址（包括地址为169.254.169.254的IMDS地址以及其IPv4映射的IPv6形式）、RFC1918规定的私有地址范围、IPv6的ULA地址范围、CGNAT地址范围，以及RFC2544标准规定的测试地址范围。当调用`build_proxy_config(..., upstream_deny_cidrs=None)`时，函数必须使用这些默认值；只有明确指定空列表时才表示放弃使用默认设置。

回归测试包括：`test_default_deny_cidrs_present_when_unspecified`和`test_default_deny_includes_ipv4_mapped_v6`。

### 审计日志的异常告警机制

若发生任何 `OSError`，`ensure_audit_log` 函数都会抛出 `RuntimeError`。在固定版本 v0.39 中，守护进程根本不会写入该文件（因为不存在 `log.audit_path` 字段），因此 `cmd_setup` 会将此类错误视为警告（在该版本升级之前，该文件并不承担实际功能），并将成功状态标记为“保留状态”。一旦版本升级到包含 `log.audit_path` 的版本，就需要重新评估：此时该文件将从第一字节起就被设置为 `0o600` 权限，并启用 `O_NOFOLLOW` 选项，从而确保隐私保护机制得以落实，相应测试也应再次失败。

**v0.39 的架构限制：** 在 iron-proxy v0.39 的 `config.Log` 结构中并不存在 `log.audit_path` 字段，因此 `build_proxy_config` 函数虽会接收 `audit_log` 参数，但不会将其写入生成的 YAML 文件中。在 v0.39 版本中，每次请求产生的记录会与守护进程级别的日志一同存储在 `iron-proxy.log` 文件中。尽管如此，`audit.log` 文件仍会被预先创建为 `0o600` 权限且带有 `O_NOFOLLOW` 选项，因此即便版本升级到支持独立日志流的版本，原有的隐私保护机制依然有效。

相关回归测试包括：`test_ensure_audit_log_raises_on_immutable_parent` 以及 `test_audit_log_kwarg_does_not_inject_audit_path_v039`。

### Bitwarden 模式下的明确错误提示

当同时满足以下条件时：`credential_source: bitwarden` 且 `proxy.allow_env_fallback: false`（默认值）：
- 缺少访问令牌环境变量 -> `cmd_start` 函数会拒绝启动。
- 缺少 `project_id` 参数 -> `cmd_start` 函数会拒绝启动。
- 对于一个或多个已配置的提供方，`bws secret list` 查询未返回任何结果 -> `_build_proxy_subprocess_env` 函数会抛出异常。

在 Bitwarden 模式下转而使用主机环境变量，反而会重新引入原本希望避免的日志过时问题。

回归问题：`test_cmd_start_refuses_when_bitwarden_token_missing`（CLI层）；`_build_proxy_subprocess_env`函数中的严格模式断言（守护进程层）。

### Docker环境变量冲突检测

当`enforce_on_docker: true`时，若任何用于控制出站的变量（如HTTPS_PROXY、SSL_CERT_FILE、NODE_EXTRA_CA_CERTS等）或任何已映射的`real_env_name`（如OPENROUTER_API_KEY等）被覆盖，容器启动前将引发`RuntimeError`错误。

回归问题：`test_docker_env_collision_with_proxy_raises_when_enforce`。

### PID回收防护机制

在确认`argv[0]`的文件名匹配有效之前，`_pid_alive`函数必须先查询进程内的 `_proxy_nonce`（同进程场景），或磁盘上的 `iron-proxy.nonce` 文件（跨CLI场景）。此外，在发送SIGKILL信号之前，`stop_proxy`函数必须重新检查 `/proc/<pid>/stat` 文件中的启动时间，若时间出现偏差则应抑制该信号。

回归问题：`test_stop_proxy_suppresses_sigkill_on_pid_recycle`、`test_pid_proc_starttime_parses_comm_with_parens`、`test_persisted_nonce_roundtrip`。

### 重新配置时的令牌保留

函数`merge_mappings(existing, discovered, rotate=False)`在处理存在重叠的提供商时，必须返回之前的令牌。重新运行`hermes egress setup`时，不得对正在运行的沙箱静默地返回401错误。只有明确使用`--rotate-tokens`选项时，才会进行令牌轮换。

回归问题：`test_merge_mappings_preserves_existing_tokens`、`test_merge_mappings_rotate_mints_fresh_tokens`。

### 凭证来源的保留

在未使用 `--no-bitwarden` 参数的情况下重新运行 `cmd_setup` 命令时，绝不允许将 `credential_source: bitwarden` 的配置降级为 `env`。若直接执行 `hermes egress setup`（不加任何参数），则会保留之前的所有配置设置。

该功能已通过 CLI 测试中的 `cmd_setup` 流程进行验证（当在先使用 `--from-bitwarden` 参数后再次执行单纯的 `setup` 命令时，就会触发对原有 Bitwarden 配置的保留机制）。

## 扩展点

### 添加新的承载令牌提供者

`iron_proxy.py` 文件中的 `_BEARER_PROVIDERS` 字典用于将环境变量名称映射为上游主机地址的元组。添加新的条目后，该提供者便能被 `discover_provider_mappings()` 函数识别；当对应的环境变量存在时，向导会自动为其生成令牌。

```python
_BEARER_PROVIDERS: Dict[str, Tuple[str, ...]] = {
    ...,
    "MY_PROVIDER_API_KEY": ("api.myprovider.com",),
}
```

同时请更新 `_DEFAULT_ALLOWED_HOSTS` 的值，以便代理默认允许上游请求通过。运行 `test_discover_provider_mappings_*` 命令即可进行验证。

### 添加新的头部令牌提供者（x-api-key系列）

如果该提供者使用静态的非授权类型头部信息进行身份验证（例如 Anthropic 的 `x-api-key`、Azure 的 `api-key` 或 Gemini 的 `x-goog-api-key`），请将其添加到 `_HEADER_AUTH_PROVIDERS` 中——iron-proxy 的 `secrets.replace.match_headers` 功能能够识别任意名称的头部信息，因此这类提供者可被视为一等效的替换提供者。

```python
_HEADER_AUTH_PROVIDERS: Dict[str, Dict[str, Tuple[str, ...]]] = {
    ...,
    "MY_PROVIDER_API_KEY": {
        "hosts": ("api.myprovider.com",),
        "match_headers": ("x-my-auth-header", "Authorization"),
        "aliases": (),
    },
}
```

请仅将 `aliases` 用于表示*相同*凭据的不同环境变量名称（例如用 `GOOGLE_API_KEY` 代表 `GEMINI_API_KEY`）——这些别名名称会被合并为单一映射，因为同一主机上的两条 `require: true` 规则会相互排斥对方的请求。同时还需更新 `_DEFAULT_ALLOWED_HOSTS`。

### 添加新的签名认证提供程序（未覆盖场景）

如果该提供程序使用 SigV4、SDK 生成的 OAuth 或请求签名机制，静态头部替换方式将无法满足需求。此时需将该环境变量添加到 `_NON_BEARER_PROVIDERS` 中，这样向导及 `hermes egress status` 命令就能对此发出警告：

```python
_NON_BEARER_PROVIDERS: Tuple[str, ...] = (
    ...,
    "MY_SIGNED_PROVIDER_ACCESS_KEY",
)
```

### 将 iron-proxy 集成到非 Docker 后端中

`_egress_proxy_args_for_docker` 是专为 Docker 设计的。那些需要类似集成方式的后端需自行实现相应的功能，具体要求包括：

1. 读取 `load_config().get("proxy", {})`；若 `enabled` 的值为 false，则返回空参数列表。
2. 调用 `iron_proxy.get_status()`；在 `configured`、`pid`、`listening` 或 `ca_cert_path` 出现异常时，体现相应的强制策略。
3. 调用 `iron_proxy.load_mappings()`；若映射列表为空且 `enforce_on_docker: true`，则拒绝挂载。
4. 设置七个环境变量（HTTPS_PROXY、NO_PROXY、REQUESTS_CA_BUNDLE、SSL_CERT_FILE、CURL_CA_BUNDLE、NODE_EXTRA_CA_CERTS、HERMES_EGRESS_PROXY），以及每个映射对应的 `HERMES_PROXY_TOKEN_<NAME>` 变量。
5. 将证书文件放置在运行时可信任的路径下（通常为 `/etc/ssl/certs/hermes-egress-ca.crt`），以便在沙箱环境中使用。
6. 对用户自定义的后端特定环境配置进行冲突检测。

Docker 版本的实现代码约 150 行；Modal、Daytona 和 SSH 等后端的实现代码量预计也与之相当。

### 订阅逐请求审计事件

在当前固定的 v0.39 版本中，iron-proxy 会将分行的 JSON 格式日志写入 `~/.hermes/proxy/iron-proxy.log` 文件中（该版本同时记录守护进程日志与每次请求的日志详情，具体可参见用户指南中的“iron-proxy v0.39 的日志记录功能”）。开发者可通过插件或外部监控工具对该文件进行实时跟踪，从而及时响应允许列表被拒绝、密钥被替换或上游服务出现错误等异常情况。一旦将固定版本升级到支持 `log.audit_path` 功能的版本，每次请求的日志流将会自动切换到 `audit.log` 文件中，而绑定在该路径上的监控工具也将无需人工操作即可开始正常工作。该日志格式的详细规范文档可见 [docs.iron.sh/audit](https://docs.iron.sh/audit)（链接）。

## 测试

```bash
# Hermetic suite (no network, no real binary)
scripts/run_tests.sh tests/test_iron_proxy.py tests/test_iron_proxy_cli.py

# Live E2E (real binary, real curl, real CONNECT tunnel)
HERMES_RUN_E2E=1 scripts/run_tests.sh tests/test_iron_proxy_e2e.py

# Live PTY smoke against `hermes egress`
HERMES_HOME=/tmp/hermes-egress-test python3 -m hermes_cli.main egress --help
HERMES_HOME=/tmp/hermes-egress-test python3 -m hermes_cli.main egress setup --help
```

该 CLI 工具基于 argparse 构建，因此使用 `--help` 命令是验证“新添加的参数是否已正确注册”的便捷方法。

## 相关内容

- 面向用户的设置与故障排除：[出口代理](https://hermes-agent.nousresearch.com/docs/user-guide/egress/iron-proxy)
- Docker 后端实现细节：[Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker)
- 与 Bitwarden Secrets Manager 的集成：[`hermes secrets bitwarden`](https://hermes-agent.nousresearch.com/docs/user-guide/secrets/bitwarden)
- CLI 命令参考：[`hermes egress`](https://hermes-agent.nousresearch.com/docs/reference/cli-commands#hermes-egress)
- 通过沙箱注入的环境变量：[出口代理（沙箱注入）](https://hermes-agent.nousresearch.com/docs/reference/environment-variables#egress-proxy-sandbox-injected)
