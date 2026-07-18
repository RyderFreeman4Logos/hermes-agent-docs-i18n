---
title: Browser Automation
description: Control browsers with multiple providers, local Chromium-family browsers via CDP, or cloud browsers for web interaction, form filling, scraping, and more.
sidebar_label: Browser
sidebar_position: 5
---

# 浏览器自动化

Hermes Agent配备了完整的浏览器自动化工具集，支持多种后端选项：

- 通过 [Browserbase](https://browserbase.com) 的**Browserbase云模式**，可获取托管式云浏览器及反爬虫功能；
- 作为另一种云浏览器提供商，可通过 [Browser Use](https://browser-use.com) 使用其**Browser Use云模式**；
- 通过 [Firecrawl](https://firecrawl.dev) 的**Firecrawl云模式**，获得内置抓取功能的云浏览器；
- 通过 [Camofox](https://github.com/jo-inc/camofox-browser) 的**Camofox本地模式**，实现基于Firefox的本地反检测浏览（指纹伪装）；
- **本地Chromium系列CDP模式**——可通过 `/browser connect` 将浏览器工具连接到您自己的Chrome、Brave、Chromium或Edge实例；
- 通过 `agent-browser` CLI及本地Chromium安装实现的**本地浏览器模式**。

在所有模式下，该代理均能够浏览网站、与页面元素交互、填写表单并提取信息。

## 概述

页面以**无障碍树结构**（基于文本的快照）的形式呈现，非常适合用于LLM代理。交互式元素会被赋予引用ID（如`@e1`、`@e2`），代理可利用这些ID进行点击和输入操作。

主要功能包括：

- **多提供商云端执行**——支持Browserbase、Browser Use或Firecrawl，无需本地浏览器；
- **本地Chromium系列集成**——可通过CDP连接到正在运行的Chrome、Brave、Chromium或Edge浏览器，实现直接浏览；
- **内置隐身功能**——随机生成指纹、自动解决验证码、使用住宅级代理（Browserbase提供）；
- **会话隔离**——每个任务都会拥有独立的浏览器会话；
- **自动清理**——超时后自动关闭闲置会话；
- **视觉分析**——通过截图结合AI分析实现图像理解。

## 设置

:::tip Nous订阅用户
如果您拥有付费的[Nous Portal](https://portal.nousresearch.com)订阅账号，无需额外API密钥即可通过**[工具网关](tool-gateway.md)**使用浏览器自动化功能。新安装版本可运行 `hermes setup --portal` 进行登录并一次性启用所有网关工具；现有版本则可通过 `hermes model` 或 `hermes tools` 将**Nous订阅**设置为浏览器提供商。
:::

### Browserbase云模式

如需使用Browserbase管理的云浏览器，请添加：

```bash
# Add to ~/.hermes/.env
BROWSERBASE_API_KEY=***
BROWSERBASE_PROJECT_ID=your-project-id-here
```

请在 [browserbase.com](https://browserbase.com) 获取您的凭据。

### 使用 Browser Use 云模式

若要将 Browser Use 作为您的云浏览器提供商，请添加以下内容：

```bash
# Add to ~/.hermes/.env
BROWSER_USE_API_KEY=***
```

请在 [browser-use.com](https://browser-use.com) 获取您的 API 密钥。Browser Use 通过其 REST API 提供云浏览器服务。如果同时设置了 Browserbase 和 Browser Use 的凭据，将以 Browserbase 的设置优先生效。

### Firecrawl 云模式

如需将 Firecrawl 作为您的云浏览器提供商，请添加以下配置：

```bash
# Add to ~/.hermes/.env
FIRECRAWL_API_KEY=fc-***
```

请在 [firecrawl.dev](https://firecrawl.dev) 获取您的 API 密钥。随后选择 Firecrawl 作为您的浏览器提供商：

```bash
hermes setup tools
# → Browser Automation → Firecrawl
```

可选设置：

```bash
# Self-hosted Firecrawl instance (default: https://api.firecrawl.dev)
FIRECRAWL_API_URL=http://localhost:3002

# Session TTL in seconds (default: 300)
FIRECRAWL_BROWSER_TTL=600
```

### 混合路由机制：公共网址走云端，局域网/localhost地址走本地

一旦配置了云服务提供商，Hermes 会自动为那些解析为私有地址/回环地址/局域网地址的网址（如 `localhost`、`127.0.0.1`、`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`、`*.local`、`*.lan`、`*.internal`，以及 IPv6 回环地址 `::1` 和链路本地地址 `169.254.x.x`）生成一个**本地的 Chromium sidecar**。而在同一会话中，公共网址则继续通过已配置的云服务提供商处理。

这一机制完美解决了“在本地开发却使用 Browserbase”的常见场景——无需切换服务提供商或关闭 SSRF 防护，代理即可同时截取 `http://localhost:3000` 上的仪表板截图，并抓取 `https://github.com` 的内容。云服务提供商根本无法获取到这些私有网址的信息。

该功能**默认处于开启状态**。如需关闭它（所有网址都将像以前一样发送到已配置的云服务提供商），可按相应步骤操作：

```yaml
# ~/.hermes/config.yaml
browser:
  cloud_provider: browserbase
  auto_local_for_private_urls: false
```

在禁用自动路由的情况下，私有 URL 会被拒绝访问，系统会返回错误信息 `“已阻止：该 URL 指向私有或内部地址”`，除非您同时设置 `browser.allow_private_urls: true`（这样云服务提供商才会尝试访问——但由于 Browserbase 等工具无法连接到您的局域网，此方法通常无效）。

前提条件：本地 sidecar 需要使用与纯本地模式相同的 `agent-browser` CLI 工具，因此您必须先安装它（可通过 `hermes setup tools → Browser Automation` 自动完成安装）。此外，从公共 URL 重定向到私有地址的操作仍然会被阻止（您无法通过重定向到内部地址的技巧来通过公共路径访问您的局域网）。

### Camofox 本地模式

[Camofox](https://github.com/jo-inc/camofox-browser) 是一个基于 Node.js 的自托管服务器，它基于 Camoufox（一款具备 C++ 指纹伪装功能的 Firefox 分支）构建。该工具可在无需依赖云服务的情况下实现本地防检测浏览功能。

```bash
# Clone the Camofox browser server first
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser

# Build and start with Docker using the default container settings
# (auto-detects arch: aarch64 on M1/M2, x86_64 on Intel)
make up

# Stop and remove the default container
make down

# Force a clean rebuild (for example, after upgrading VERSION/RELEASE)
make reset

# Just download binaries without building
make fetch

# Override arch or version explicitly
make up ARCH=x86_64
make up VERSION=135.0.1 RELEASE=beta.24
```

`make up` 命令会立即启动默认容器。如果您需要自定义运行时设置，例如更大的 Node 堆内存、VNC 连接功能或持久化的配置目录，那么应先构建镜像，再自行启动它：

```bash
# Build the image without starting the default container
make build

# Start with persistence, VNC live view, and a larger Node heap
mkdir -p ~/.camofox-docker
docker run -d \
  --name camofox-browser \
  --restart unless-stopped \
  -p 9377:9377 \
  -p 6080:6080 \
  -p 5901:5900 \
  -e CAMOFOX_PORT=9377 \
  -e ENABLE_VNC=1 \
  -e VNC_BIND=0.0.0.0 \
  -e VNC_RESOLUTION=1920x1080 \
  -e MAX_OLD_SPACE_SIZE=2048 \
  -v ~/.camofox-docker:/root/.camofox \
  camofox-browser:135.0.1-aarch64
```

启用 VNC 后，浏览器将以有界面模式运行，您可以通过 `http://localhost:6080`（未启用 VNC）在浏览器中实时查看其运行状态。此外，您也可以将原生 VNC 客户端连接到 `localhost:5901`。

如果您已经运行过 `make up` 命令，请先停止该操作并删除默认容器，然后再启动自定义容器：

```bash
make down
# then run the custom docker run command above
```

接着在 `~/.hermes/.env` 中进行设置：

```bash
CAMOFOX_URL=http://localhost:9377
```

如果 Camofox 在 Docker 环境中运行，且您希望它能访问主机上提供的 Web 应用，那么就需要启用回环重写功能。`CAMOFOX_URL` 仍应指向主机上发布的控制 API，但像 `http://127.0.0.1:3000` 这样的页面地址，则必须从容器内部以 `http://host.docker.internal:3000` 的形式来访问。

```yaml
# ~/.hermes/config.yaml
browser:
  camofox:
    rewrite_loopback_urls: true
    loopback_host_alias: host.docker.internal  # default; use a LAN IP if needed
```

对应的环境变量：

```bash
CAMOFOX_REWRITE_LOOPBACK_URLS=true
CAMOFOX_LOOPBACK_HOST_ALIAS=host.docker.internal
```

该重写功能仅适用于包含回环主机（如 `localhost`、`127.0.0.1`、`::1`）的页面导航 URL，不会更改 `CAMOFOX_URL` 的值。对于非 Docker 环境下的 Camofox 安装，浏览器已在本地主机上运行且回环 URL 已正确设置，建议保持该功能关闭状态。

或者可通过 `hermes tools` → Browser Automation → Camofox 进行配置。

一旦设置了 `CAMOFOX_URL`，所有浏览器工具将自动通过 Camofox 而非 Browserbase 或 agent-browser 来处理请求。

#### 持久化浏览器会话

默认情况下，每个 Camofox 会话都会被赋予一个随机标识——因此 Cookie 和登录信息在代理重启后不会保留。若需实现浏览器会话的持久化，可在 `~/.hermes/config.yaml` 文件中添加以下内容：

```yaml
browser:
  camofox:
    managed_persistence: true
```

随后请完全重启 Hermes，以便其加载新的配置。

:::warning 层级路径很重要
Hermes 读取的是 `browser.camofox.managed_persistence`，而非顶层的 `managed_persistence`。一个常见的错误就是这样编写：

```yaml
# ❌ Wrong — Hermes ignores this
managed_persistence: true
```

如果将该标志设置在错误的路径下，Hermes 会自动回退到随机生成的临时 `userId`，从而导致每次会话时登录状态都会丢失。
:::

##### Hermes 的功能
- 向 Camofox 发送一个确定的、基于浏览配置文件的 `userId`，从而使服务器能够在不同会话之间重复使用同一个 Firefox 配置文件。
- 在清理时会跳过服务器端的上下文销毁操作，因此 Cookie 和登录状态能够在各个 Agent 任务之间保持不变。
- 将 `userId` 限制在当前活跃的 Hermes 配置文件范围内，从而实现不同 Hermes 配置文件对应不同的浏览器配置文件（即配置文件隔离）。

##### Hermes 的局限性
- 它不会强制要求 Camofox 服务器实现持久化存储。Hermes 仅发送一个稳定的 `userId`；服务器必须通过将该 `userId` 映射到永久性的 Firefox 配置文件目录来实现持久化。
- 如果您的 Camofox 服务器版本将每个请求都视为临时请求（例如始终调用 `browser.newContext()` 而不加载已保存的配置文件），那么 Hermes 就无法让这些会话保持持久状态。请确保您使用的 Camofox 版本支持基于 `userId` 的配置文件持久化功能。

##### 验证功能是否正常

1. 启动 Hermes 以及您的 Camofox 服务器。
2. 在某个浏览器任务中打开 Google（或任何需要登录的网站），并手动完成登录。
3. 正常结束该浏览器任务。
4. 启动一个新的浏览器任务。
5. 再次打开同一个网站——您应该仍然处于登录状态。

如果第 5 步导致您被强制登出，说明 Camofox 服务器并未正确处理那个稳定的 `userId`。请仔细检查配置文件路径，确认在修改 `config.yaml` 后已彻底重启 Hermes，并核实您的 Camofox 服务器版本支持按用户保存的持久配置文件。

##### 状态存储位置

Hermes 从基于浏览配置文件的目录 `~/.hermes/browser_auth/camofox/`（对于非默认配置文件，则为 `$HERMES_HOME` 下的对应路径）中获取稳定的 `userId`。实际的浏览器配置文件数据则存储在 Camofox 服务器端，以该 `userId` 作为键进行标识。如需完全重置某个持久配置文件，请在 Camofox 服务器上清除该配置文件，并删除对应的 Hermes 配置文件的状态目录。

#### 由外部应用管理的 Camofox 会话

当有其他应用程序控制可见的 Camofox 浏览器（如桌面助手、自定义集成或其它 Agent）时，可以配置 Hermes 在该应用程序的标识下运行，而非创建独立的隔离配置文件。

有三个参数可用于控制此行为：

| 参数名 | 环境变量 | 效果 |
|--------|----------|------|
| `browser.camofox.user_id` | `CAMOFOX_USER_ID` | Hermes 在创建标签页时使用的 Camofox `userId`。设置该参数即可让会话进入“外部管理”模式。 |
| `browser.camofox.session_key` | `CAMOFOX_SESSION_KEY` | 在创建标签页时会发送的 `sessionKey`（亦称 `listItemId`），用于在后续操作中匹配已存在的标签页。若未设置，则默认为每个任务独立的值。 |
| `browser.camofox.adopt_existing_tab` | `CAMOFOX_ADOPT_EXISTING_TAB` | 当该参数设置为 true 时，Hermes 在首次使用时会调用 `GET /tabs?userId=<user_id>`，优先复用已存在的标签页而非新建。 |

环境变量的设置优先级高于 `config.yaml`。两种配置方式均可使用：

```yaml
browser:
  camofox:
    user_id: shared-camofox
    session_key: visible-tab
    adopt_existing_tab: true
```

```bash
CAMOFOX_USER_ID=shared-camofox
CAMOFOX_SESSION_KEY=visible-tab
CAMOFOX_ADOPT_EXISTING_TAB=true
```

**设置 `user_id` 后会发生哪些变化：**

- Hermes 会跳过任务结束时的破坏性清理操作（与 `managed_persistence: true` 的效果相同）。其他应用程序的标签页、Cookie 和用户配置信息将得以保留。
- Hermes **不会**调用 `DELETE /sessions/<user_id>` —— 该接口会清除所有用户数据，因此如果被触发，将会彻底删除外部应用程序的会话。

**标签页接管机制（当 `adopt_existing_tab: true` 时）：**

1. 在进程启动后的首次浏览器工具调用中，Hermes 会发送请求 `GET /tabs?userId=<user_id>`（超时时间为5秒）。
2. 如果响应中的某个标签页的 `listItemId` 等于 `session_key`，Hermes 将接管该组中最新创建的标签页。
3. 否则，Hermes 会接管该用户最新创建的标签页（无论其 `listItemId` 是什么）。
4. 如果不存在任何标签页或请求失败，Hermes 会回退到在下次操作时创建一个新标签页。

接管机制仅在为该会话分配好 `tab_id` 之前有效。如果外部应用程序在运行过程中关闭了被接管的标签页，下一次浏览器工具调用将会触发 Camofox 错误 —— Hermes 不会在每次调用时都重新尝试获取新的标签页。

**选择 `session_key` 的方法：** 如果您希望 Hermes 稳定地连接到某个*特定的*现有标签页，请将 `session_key` 设置为外部应用程序在创建该标签页时使用的 `listItemId`。如果您不设置 `session_key`，仅设置 `user_id`，Hermes 会为每个任务生成一个独立的 `session_key`（格式为 `task_<id>`）——此时 Hermes 会与外部应用程序共享 Cookie 和用户配置信息，但会同时打开自己的标签页，而非复用对方的标签页。

**并发注意事项：** 外部应用程序和 Hermes 可以同时使用同一个 Camofox `userId`，但 Camofox 不会在不同客户端之间协调各标签页的焦点切换。您需要在应用程序层进行协调（例如，在 Hermes 运行时让外部应用程序暂停）。

#### VNC 实时查看功能

当 Camofox 以有界面模式运行（即显示浏览器窗口）时，它会在健康检查响应中暴露一个 VNC 端口。Hermes 会自动检测到该端口，并在导航响应中包含对应的 VNC 地址，这样您就可以通过链接实时查看浏览器的操作情况。

### 通过 CDP（`/browser connect`）连接本地 Chromium 系列浏览器

您无需依赖云服务，也可以通过 Chrome DevTools Protocol（CDP）将 Hermes 浏览器工具连接到自己正在运行的 Chrome、Brave、Chromium 或 Edge 实例。当您需要实时查看代理的操作、与需要自身 Cookie/会话的页面进行交互，或希望避免使用云浏览器的费用时，此功能非常有用。

:::note
`/browser connect` 是一个**交互式 CLI 命令**——它并非由网关触发。如果您尝试在 WebUI、Telegram、Discord 或其他网关聊天界面中运行该命令，消息将以纯文本形式发送给代理，命令将无法执行。请在终端中启动 Hermes（使用 `hermes` 或 `hermes chat` 命令），然后在终端中输入 `/browser connect` 执行。
:::

在 CLI 中，可使用以下命令：

```
/browser connect                 # Auto-launch/connect to a local Chromium-family browser at http://127.0.0.1:9222
/browser connect ws://host:port  # Connect to a specific CDP endpoint
/browser status                  # Check current connection
/browser disconnect              # Detach and return to cloud/local mode
```

如果浏览器尚未以远程调试模式运行，Hermes会尝试自动启动支持该功能的Chromium系列浏览器，并设置`--remote-debugging-port=9222`参数。支持的浏览器包括Brave、Google Chrome、Chromium和Microsoft Edge，同时也涵盖了常见的Linux安装路径，如 `/opt/brave-bin/brave` 和 `/snap/bin/brave`。

:::提示
若希望手动启动已开启CDP功能的Chromium系列浏览器，请使用独立的用户数据目录，这样即便浏览器正在以常规配置运行，也能成功启用调试端口。

```bash
# Linux — Brave
brave-browser \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.hermes/chrome-debug \
  --no-first-run \
  --no-default-browser-check &

# Linux — Google Chrome
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=$HOME/.hermes/chrome-debug \
  --no-first-run \
  --no-default-browser-check &

# macOS — Brave
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check &

# macOS — Google Chrome
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.hermes/chrome-debug" \
  --no-first-run \
  --no-default-browser-check &
```

接着启动 Hermes CLI 并执行 `/browser connect` 命令。

**为何需要 `--user-data-dir` 参数？** 如果不使用该参数，在已有普通浏览器实例运行的情况下启动 Chromium 系列浏览器，通常会在现有进程上打开新窗口——而该现有进程并非通过 `--remote-debugging-port` 参数启动的，因此端口 9222 永远无法被占用。通过指定专用的用户数据目录，可以强制启动一个全新的浏览器进程，从而使调试端口能在其中正常监听。而 `--no-first-run --no-default-browser-check` 参数则可跳过针对新配置文件的初次启动向导。
:::

通过 CDP 连接时，所有浏览器工具（如 `browser_navigate`、`browser_click` 等）都会直接操作您正在使用的实时浏览器实例，而无需创建云端的调试会话。

### WSL2 + Windows Chrome：建议优先使用 MCP 而非 `/browser connect`

如果 Hermes 在 WSL2 环境中运行，但需要控制的 Chrome 浏览器窗口位于 Windows 主机上，那么 `/browser connect` 通常并非最佳解决方案。

原因如下：

- `/browser connect` 需要 Hermes 自身能够连接到可用的 CDP 端点；
- 现代版本的 Chrome 实时调试会话往往使用本地主机端点，而 WSL 环境无法像访问传统端口 9222 那样直接连接到这些端点；
- 即使 Windows 版 Chrome 支持调试，最干净的集成方式通常是让 Windows 端的浏览器 MCP 服务器与 Chrome 连接，再由 Hermes 与该 MCP 服务器进行通信。

对于这种架构，建议通过 Hermes 的 MCP 支持来使用 `chrome-devtools-mcp`。

有关具体配置方法，请参阅 MCP 指南：
- [在 Hermes 中使用 MCP](../../guides/use-mcp-with-hermes.md#wsl2-bridge-hermes-in-wsl-to-windows-chrome)

### 本地浏览器模式

如果您未设置任何云服务凭证，也未使用 `/browser connect` 命令，Hermes 仍可通过由 `agent-browser` 驱动的本地 Chromium 安装来使用各类浏览器工具。

### 可选环境变量

```bash
# Residential proxies for better CAPTCHA solving (default: "true")
BROWSERBASE_PROXIES=true

# Advanced stealth with custom Chromium — requires Scale Plan (default: "false")
BROWSERBASE_ADVANCED_STEALTH=false

# Session reconnection after disconnects — requires paid plan (default: "true")
BROWSERBASE_KEEP_ALIVE=true

# Custom session timeout in seconds (max 21600 = 6 hours) (default: project default)
# Examples: 600 (10min), 1800 (30min), 21600 (6h max)
BROWSERBASE_SESSION_TIMEOUT=1800

# Inactivity timeout before auto-cleanup in seconds (default: 120)
BROWSER_INACTIVITY_TIMEOUT=120

# Extra Chromium launch flags (comma- or newline-separated). Hermes auto-injects
# `--no-sandbox,--disable-dev-shm-usage` when it detects root or AppArmor-restricted
# unprivileged user namespaces (Ubuntu 23.10+, DGX Spark, many container images),
# so most users don't need to set this. Set it manually only if you need a flag
# Hermes doesn't add automatically; setting it disables the auto-injection.
AGENT_BROWSER_ARGS=--no-sandbox
```

### 安装 agent-browser CLI 工具

```bash
npm install -g agent-browser
# Or install locally in the repo:
npm install
```

:::info
您的配置文件中的 `toolsets` 列表中必须包含 `browser` 工具集，或者通过命令 `hermes config set toolsets '["hermes-cli", "browser"]'` 来启用它。
:::

## 可用工具

### `browser_navigate`

用于导航至指定 URL。必须在其他任何浏览器相关工具之前调用该函数，它负责初始化 Browserbase 会话。

```
Navigate to https://github.com/NousResearch
```

:::提示
对于简单的信息检索，建议优先使用 `web_search` 或 `web_extract`——它们的速度更快且成本更低。当需要与页面进行**交互**（如点击按钮、填写表单、处理动态内容）时，则应使用浏览器工具。
:::

### `browser_snapshot`

获取当前页面无障碍访问结构树的文本格式快照。该功能会返回带有 `@e1`、`@e2` 等引用 ID 的交互元素，以便后续与 `browser_click` 和 `browser_type` 功能配合使用。

- **`full=false`**（默认值）：仅显示交互元素的简洁视图
- **`full=true`**：显示完整的页面内容

长度超过 15,000 个字符的快照会自动被截断或由大型语言模型进行总结处理（其每页处理额度与 `web_extract` 相同）。此时，完整的快照会被保存到 `~/.hermes/cache/web/` 目录中，工具的输出还会包含该文件的路径以及可直接使用的 `read_file` 调用指令，这样智能体便无需重新生成快照，即可逐页查看完整的无障碍访问结构树——包括那些被截断之外的元素引用信息。

```
Click @e5 to press the "Sign In" button
```

### `browser_type`

在输入框中输入文本。首先清空该字段，然后再输入新内容。

```
Type "hermes agent" into the search field @e3
```

### `browser_scroll`

上下滚动页面，以查看更多内容。

```
Scroll down to see more results
```

### `browser_press`

模拟按下键盘按键。可用于提交表单或进行页面导航。

```
Press Enter to submit the form
```

支持的按键包括：`Enter`、`Tab`、`Escape`、`ArrowDown`、`ArrowUp` 以及更多功能键。

### `browser_back`

返回到浏览器历史记录中的上一页。

### `browser_get_images`

列出当前页面上的所有图片，同时显示其网址和替代文本。这对于查找需要分析的图片非常有用。

### `browser_vision`

截取屏幕截图并利用视觉 AI 进行分析。当文本截图无法捕捉到重要的视觉信息时，可使用此功能——尤其适用于验证码、复杂布局或视觉验证任务。

截图会被永久保存，系统会同时返回文件路径以及 AI 分析结果。在聊天平台（如 Telegram、Discord、Slack、WhatsApp）上，你可以让智能体分享该截图——它将通过 `MEDIA:` 机制以原生图片附件的形式发送出去。

```
What does the chart on this page show?
```

截图会存储在 `~/.hermes/cache/screenshots/` 目录中，并会在24小时后自动清除。

### `browser_console`

用于获取当前页面的浏览器控制台输出（日志、警告和错误信息），以及未被捕获的JavaScript异常。这对于检测那些不会出现在无障碍访问树中的隐匿式JavaScript错误至关重要。

```
Check the browser console for any JavaScript errors
```

在读取内容后，可使用 `clear=True` 参数清除控制台，这样后续的调用仅会显示新消息。

当 `browser_console` 接收 `expression` 参数时，还会执行 JavaScript 代码——其格式与开发者工具的控制台相同，返回结果将为解析后的形式（JSON 序列化的对象会转换为字典，而原始值则保持不变）。

```
browser_console(expression="document.querySelector('h1').textContent")
browser_console(expression="JSON.stringify(performance.timing)")
```

当当前会话处于 CDP 监控器激活状态时（凡是针对支持 CDP 的后端执行了 `browser_navigate` 操作的会话通常都如此），评估操作将通过该监控器的持久 WebSocket 进行，无需启动子进程，因此没有额外开销。否则，则会走标准的代理-浏览器 CLI 路径。两种方式的行为完全一致，仅延迟会有所不同。

默认情况下，评估操作不受限制——代理可以使用 `fetch`、读取存储数据、查询表单值，以及执行任何 DOM 提取操作。但在非本地后端上，针对私有/内部地址的请求仍会被阻断（SSRF 防护机制与此设置无关）。如果您使用已登录的账户浏览恶意页面，并希望对敏感的 JavaScript 原语（如 Cookie、存储数据、剪贴板内容、网络请求、表单值）实施严格的禁止列表管控，可在 `config.yaml` 中设置 `browser.restrict_evaluate: true`。需要注意的是，禁止列表匹配的是原语的*名称*，因此那些仅包含 `fetch` 或 `cookie` 等字词的合法表达式也会被阻断。

### `browser_cdp`

直接传递原始的 Chrome DevTools 协议数据——专为处理其他工具无法覆盖的浏览器操作而设计。可用于原生对话框处理、iframe 内部评估、Cookie/网络控制，或代理所需的任何 CDP 操作。

**仅在会话启动时能够访问 CDP 端点时才可用**——也就是说，必须已通过 `/browser connect` 连接到正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器，或者已在 `config.yaml` 中设置了 `browser.cdp_url`。目前的默认本地代理-浏览器模式、Camofox 以及各类云服务提供商（Browserbase、Browser Use、Firecrawl）均未向该工具开放 CDP 功能——虽然云服务提供商提供了每会话独立的 CDP URL，但实时会话路由功能仍在后续开发中。

**CDP 方法参考文档：** https://chromedevtools.github.io/devtools-protocol/ ——代理可以通过 `web_extract` 提取特定方法的页面内容，以此查询参数信息并了解其结构。

常见使用场景：

```
# List tabs (browser-level, no target_id)
browser_cdp(method="Target.getTargets")

# Handle a native JS dialog on a tab
browser_cdp(method="Page.handleJavaScriptDialog",
            params={"accept": true, "promptText": ""},
            target_id="<tabId>")

# Evaluate JS in a specific tab
browser_cdp(method="Runtime.evaluate",
            params={"expression": "document.title", "returnByValue": true},
            target_id="<tabId>")

# Get all cookies
browser_cdp(method="Network.getAllCookies")
```

浏览器级方法（`Target.*`、`Browser.*`、`Storage.*`）无需传入 `target_id`。页面级方法（`Page.*`、`Runtime.*`、`DOM.*`、`Emulation.*`）则必须使用 `Target.getTargets` 获取的 `target_id`。每次无状态调用都是独立的——调用之间不会保留会话状态。

**跨域 iframe：** 需要传入 `frame_id`（可从 `browser_snapshot.frame_tree.children[]` 中获取，且需满足 `is_oopif=true` 的条件），以便通过监管节点的对应 iframe 实时会话来路由 CDP 调用。这正是 Browserbase 中在跨域 iframe 内使用 `Runtime.evaluate` 的实现方式，因为无状态的 CDP 连接会因签名 URL 到期而失效。示例如下：

```
browser_cdp(
  method="Runtime.evaluate",
  params={"expression": "document.title", "returnByValue": True},
  frame_id="<frame_id from browser_snapshot>",
)
```

同源 iframe 不需要使用 `frame_id` —— 可以通过顶层 `Runtime.evaluate` 调用 `document.querySelector('iframe').contentDocument` 来获取内容。

### `browser_dialog`

用于处理原生 JS 对话框（如 `alert` / `confirm` / `prompt` / `beforeunload`）。在该工具出现之前，这些对话框会默默阻塞页面的 JavaScript 线程，后续的 `browser_*` 调用将会挂起或抛出错误；而现在，智能体可以通过 `browser_snapshot` 的输出查看待处理的对话框，并作出明确响应。

**工作流程：**
1. 调用 `browser_snapshot`。如果存在阻塞页面的对话框，它会以 `pending_dialogs: [{"id": "d-1", "type": "alert", "message": "..."}]` 的形式显示。
2. 调用 `browser_dialog(action="accept")` 或 `browser_dialog(action="dismiss")`。对于 `prompt()` 对话框，需传入 `prompt_text="..."` 以指定响应内容。
3. 再次获取快照 —— 此时 `pending_dialogs` 为空，页面的 JavaScript 线程已恢复运行。

**检测功能通过持续的 CDP 监控器自动实现** —— 每个任务都会通过一个 WebSocket 订阅 Page/Runtime/Target 事件。该监控器还会在快照中添加 `frame_tree` 字段，以便智能体查看当前页面的 iframe 结构，包括跨源（OOPIF）iframe。

**功能支持矩阵：**

| 后端环境 | 通过 `pending_dialogs` 进行检测 | 响应方式（`browser_dialog` 工具） |
|---|---|---|
| 通过 `/browser connect` 或 `browser.cdp_url` 连接的本地 Chrome | ✓ | 支持完整工作流程 |
| Browserbase | ✓ | 通过注入的 XHR 桥接支持完整工作流程 |
| Camofox / 默认本地智能体浏览器 | ✗ | ✗（无 CDP 接口） |

**在 Browserbase 上的实现原理。** Browserbase 的 CDP 代理会在服务器端于约 10 毫秒内自动关闭真实的原生对话框，因此我们无法使用 `Page.handleJavaScriptDialog`。监控器会通过 `Page.addScriptToEvaluateOnNewDocument` 注入一段小型脚本，用同步 XHR 替代 `window.alert`/`confirm`/`prompt` 的功能。我们会通过 `Fetch.enable` 拦截这些 XHR 请求 —— 在我们使用智能体的响应调用 `Fetch.fulfillRequest` 之前，页面的 JavaScript 线程会一直被阻塞在 XHR 请求上。而 `prompt()` 的返回值则会原封不动地传回页面的 JavaScript 中。

**对话框处理策略**可在 `config.yaml` 的 `browser.dialog_policy` 配置项中设置：

| 策略 | 行为 |
|--------|----------|
| `must_respond`（默认值） | 捕获对话框，将其显示在快照中，并等待明确的 `browser_dialog()` 调用。若超过 `browser.dialog_timeout_s`（默认 300 秒）仍未收到响应，系统会自动关闭对话框，防止有缺陷的智能体无限阻塞。 |
| `auto_dismiss` | 捕获对话框后立即关闭。智能体仍可在 `browser_state` 历史记录中看到该对话框，但无需采取任何操作。 |
| `auto_accept` | 捕获对话框后立即接受。适用于需要处理那些频繁弹出 `beforeunload` 提示的页面。 |

为控制内容量，`browser_snapshot.frame_tree` 中的 **框架树** 最多只显示 30 个框架，OOPIF 嵌套深度最多为 2 层，以此限制广告密集型页面的负载大小。当达到限制时，快照中会显示 `truncated: true` 标志；需要完整框架树的智能体可使用 `browser_cdp` 的 `Page.getFrameTree` 方法获取。

## 实际应用示例

### 填写网页表单

```
User: Sign up for an account on example.com with my email john@example.com

Agent workflow:
1. browser_navigate("https://example.com/signup")
2. browser_snapshot()  → sees form fields with refs
3. browser_type(ref="@e3", text="john@example.com")
4. browser_type(ref="@e5", text="SecurePass123")
5. browser_click(ref="@e8")  → clicks "Create Account"
6. browser_snapshot()  → confirms success
```

### 查询动态内容

```
User: What are the top trending repos on GitHub right now?

Agent workflow:
1. browser_navigate("https://github.com/trending")
2. browser_snapshot(full=true)  → reads trending repo list
3. Returns formatted results
```

## 会话录制

自动将浏览器会话录制为 WebM 视频文件：

```yaml
browser:
  record_sessions: true  # default: false
```

启用该功能后，系统会在首次执行 `browser_navigate` 指令时自动开始录制，并在会话结束时将录像保存至 `~/.hermes/browser_recordings/` 目录中。该功能在本地模式及 Browserbase 云模式下均适用。超过 72 小时的录像会自动被清理。

## 隐私保护功能

Browserbase 提供多种自动隐私保护功能：

| 功能 | 默认设置 | 备注 |
|------|----------|------|
| 基础隐私保护 | 永久开启 | 通过随机指纹、视口随机化以及自动解决验证码来增强隐私保护 |
| 居民级代理 | 开启 | 经由居民 IP 进行请求，提升访问成功率 |
| 高级隐私保护 | 关闭 | 需要使用定制版 Chromium 构建，且需订阅高级套餐 |
| 连接保持 | 开启 | 在网络出现故障时自动重新建立会话连接 |

:::note
如果您的套餐未包含付费功能，Hermes 会自动降级处理——首先关闭“连接保持”功能，再关闭代理服务——以确保免费套餐用户仍能正常浏览。
:::

## 会话管理

- 每个任务都会通过 Browserbase 创建独立的浏览器会话
- 会话在长时间无操作后会自动清理（默认时间为 2 分钟）
- 后台线程会每 30 秒检查一次过期的会话
- 在进程退出时还会进行紧急清理，防止出现孤立会话
- 会话可通过 Browserbase API（`REQUEST_RELEASE` 状态）进行释放

## 局限性

- **基于文本的交互**——依赖无障碍访问树而非像素坐标进行操作
- **快照大小限制**——页面内容过长时可能会被截断，或在达到 15,000 字符上限时由大语言模型进行总结（该限制与 `web_extract` 功能一致）；完整的快照会保存至 `~/.hermes/cache/web/` 目录，`read_file` 函数可通过该路径分页读取内容
- **会话超时**——云端会话的有效期取决于您所使用的服务提供商的套餐设置
- **成本问题**——云端会话会消耗服务提供商的积分；对话结束或长时间无操作后，这些会话会自动被清理。如需免费进行本地浏览，请使用 `/browser connect` 命令
- **不支持文件下载**——无法从浏览器中下载文件
