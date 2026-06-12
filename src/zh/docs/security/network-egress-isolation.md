# Docker部署环境下的网络出口隔离

在Docker环境中运行Hermes时，默认的`network_mode: host`配置会赋予代理进程无限制的出网访问权限。本指南介绍了如何对网络流量进行隔离，使得代理核心仅能访问其所需的服务，同时阻止任意不必要的出站连接。

这一机制主要用于防御通过工具生成的shell命令，利用`curl`、`wget`或原始HTTP协议试图窃取数据的提示注入攻击。

## 威胁模型

Hermes的[SECURITY.md](../../SECURITY.md)第2节对信任模型进行了定义。终端后端是主要的执行边界。然而，在使用`network_mode: host`模式运行时，代理执行的任何命令都可能访问网络上的任意端点，包括外部端点。

网络出口隔离则增加了第二道防护层：即便容器内执行了恶意命令，它也无法访问那些未被明确列入允许列表的端点。

```
┌─────────────────────────────────────────────┐
│  Docker Network: internal (no internet)     │
│                                             │
│   ┌──────────────┐   ┌──────────────────┐   │
│   │ hermes-agent │   │ hermes-dashboard │   │
│   └──────┬───────┘   └────────┬─────────┘   │
│          │                    │              │
│          ▼                    │              │
│   ┌──────────────┐            │              │
│   │ hermes-gtw   │◄───────────┘              │
│   └──────┬───────┘                           │
│          │                                   │
└──────────┼───────────────────────────────────┘
           │
┌──────────┼───────────────────────────────────┐
│  Docker Network: egress (internet-capable)   │
│          │                                   │
│          ▼                                   │
│   ┌─────────────────┐                        │
│   │ egress-proxy     │──► allowlisted hosts  │
│   │ (squid / envoy)  │                       │
│   └─────────────────┘                        │
└──────────────────────────────────────────────┘
```

两个 Docker 网络：

- **`internal`** — 无默认路由，无法访问互联网。代理、控制面板及网关均运行在此网络中。
- **`egress`** — 可以访问互联网。仅有需要调用外部 API 的服务才会连接到此网络。

网关服务同时连接在这两个网络中，因此它能够接收来自 Telegram/Slack 等平台的入站消息，并将其转发至内部网络中的代理。

## Compose 配置

可通过 `docker-compose.override.yml` 文件来覆盖默认的 `docker-compose.yml` 配置：

```yaml
# docker-compose.override.yml
# Network egress isolation for production deployments.
#
# Usage:
#   HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d
#
# This overrides network_mode: host with isolated Docker networks.

networks:
  internal:
    driver: bridge
    internal: true          # no default route, no internet
  egress:
    driver: bridge

services:
  gateway:
    network_mode: ""        # clear the host-mode default
    networks:
      - internal
      - egress              # needs outbound for Telegram, LLM APIs
    ports:
      - "127.0.0.1:9119:9119"   # dashboard proxy, localhost only

  dashboard:
    network_mode: ""
    networks:
      - internal            # internal only, no egress needed
```

### 使用出口代理（推荐）

如需更严格的控制，建议让所有出站流量都通过具备明确允许列表的HTTP代理进行传输：

```yaml
# docker-compose.override.yml (with egress proxy)

networks:
  internal:
    driver: bridge
    internal: true
  egress:
    driver: bridge

services:
  gateway:
    network_mode: ""
    networks:
      - internal
      - egress
    environment:
      - HTTP_PROXY=http://egress-proxy:3128
      - HTTPS_PROXY=http://egress-proxy:3128
      - NO_PROXY=hermes,hermes-dashboard,localhost

  dashboard:
    network_mode: ""
    networks:
      - internal

  egress-proxy:
    image: ubuntu/squid:6.10-24.04_edge
    networks:
      - egress
    volumes:
      - ./config/squid-allowlist.conf:/etc/squid/conf.d/allowlist.conf:ro
    restart: unless-stopped
```

示例：`config/squid-allowlist.conf`：

```
# Only allow HTTPS CONNECT to these hosts
acl allowed_hosts dstdomain api.openai.com
acl allowed_hosts dstdomain api.anthropic.com
acl allowed_hosts dstdomain openrouter.ai
acl allowed_hosts dstdomain generativelanguage.googleapis.com
acl allowed_hosts dstdomain api.telegram.org
acl allowed_hosts dstdomain api.github.com
acl allowed_hosts dstdomain discord.com

http_access allow CONNECT allowed_hosts
http_access deny all
```

请根据所使用的大语言模型服务提供商及消息平台，调整允许列表以匹配相应配置。

## 验证设置是否正确

在搭建好整个系统后，请检查各组件之间是否实现了有效隔离：

```bash
# From the agent container: this should FAIL (no egress)
docker compose exec gateway \
  curl -sf --max-time 5 https://example.com && echo "FAIL: egress not blocked" || echo "OK: egress blocked"

# From the agent container: this should SUCCEED (internal network)
docker compose exec gateway \
  curl -sf --max-time 5 http://hermes-dashboard:9119/health && echo "OK: internal reachable" || echo "FAIL"

# If using egress proxy: this should SUCCEED (allowlisted)
docker compose exec gateway \
  curl -sf --max-time 5 --proxy http://egress-proxy:3128 https://api.openai.com/v1/models && echo "OK" || echo "FAIL"
```

## 局限性

- **DNS解析：** `internal`网络仍可解析外部DNS名称，除非您同时运行了会阻止外部查询的本地DNS解析器。对于大多数威胁模型而言，这种情况是可接受的，因为仅通过DNS解析无法窃取有价值的数据。

- **不能替代沙箱后端：** 本指南仅实现了对代理*容器*网络层面的隔离。如果您使用默认的本地终端后端，工具命令将在同一个容器内执行。如需更强的隔离效果，建议将网络分段与沙箱化的终端后端（如Docker、Modal、Daytona）结合使用。

- **平台适配器需要出站访问权限：** 网关服务需要具备出网能力才能访问消息平台API。如果您新增平台适配器，需将其API端点添加到代理的允许列表中。

## 相关文档

- [SECURITY.md](../../SECURITY.md) — Hermes信任模型与漏洞报告机制
- [终端后端](../../README.md) — 沙箱化执行环境
- [docker-compose.yml](../../docker-compose.yml) — 默认配置文件
