---
title: Browser Automation
description: Control browsers with multiple providers, local Chromium-family browsers via CDP, or cloud browsers for web interaction, form filling, scraping, and more.
sidebar_label: Browser
sidebar_position: 5
---

# 浏览器自动化功能

Hermes Agent配备了完整的浏览器自动化工具集，支持多种后端选项：

- 通过 [Browser Use](https://browser-use.com) 使用**Browser Use云模式**，该服务可提供受管理的Chromium浏览器，具备隐身功能、住宅代理支持、验证码破解能力以及可重复使用的浏览器配置文件。
- 通过 [Browserbase](https://browserbase.com) 使用**Browserbase云模式**，这是一家提供云浏览器服务的供应商，还配备了反机器人技术工具。
- 通过 [Browser Use CLI 3.0](https://github.com/browser-use/browser-use) 使用**Browser Use模式**，该工具是本地Chrome浏览器以及Browser Use云浏览器的默认驱动程序。
- 通过 [Firecrawl](https://firecrawl.dev) 使用**Firecrawl云模式**，这类云浏览器内置了网页抓取功能。
- 通过 [Camofox](https://github.com/jo-inc/camofox-browser) 使用**Camofox本地模式**，可在本地实现反检测浏览（基于Firefox的指纹伪装技术）。
- 通过 [Lightpanda](https://lightpanda.io) 使用**Lightpanda本地引擎**，这是一款用Zig语言从头开始开发的无头浏览器，专为机器设计；它启动速度极快，内存占用仅为Chrome的1/16，运行速度则快9倍。该引擎既可在Browser Use模式下使用（由Hermes自动启动，无需Chromium或Node环境），也可与内置工具配合使用（对于目前尚不支持的功能，会自动回退到Chrome）。
- **本地Chromium系列CDP**——可通过 `/browser connect`命令将浏览器工具连接到您自己的Chrome、Brave、Chromium或Edge浏览器实例。
- 通过 `agent-browser` CLI及本地安装的Chromium浏览器使用**本地浏览器模式**。
在所有模式下，该智能体均能够浏览网页、操作页面元素、填写表单并提取信息。

## 概述

网页以**无障碍树结构**（基于文本的快照）的形式呈现，这使其非常适合用于大型语言模型智能体。各类交互式元素都会被赋予引用标识符（如 `@e1`、`@e2`），智能体可通过这些标识符来执行点击和输入操作。

主要功能包括：

- **多提供商云端执行** — 支持 Browser Use、Browserbase 或 Firecrawl，无需本地浏览器
- **本地 Chromium 系列浏览器集成** — 可通过 CDP 连接到正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器，实现实时浏览
- **云端反爬虫功能** — Browser Use Cloud 提供隐身模式、居住地代理以及验证码破解服务
- **持久化云端配置文件** — Browser Use Cloud 能在不同会话之间重复使用 Cookie、localStorage 以及保存的密码
- **会话隔离** — 每个任务都会拥有独立的浏览器会话
- **自动清理机制** — 非活跃会话会在超时后自动关闭
- **视觉分析功能** — 通过截图结合人工智能分析来实现对图像内容的理解

## 设置

:::tip Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅账户，无需额外 API 密钥即可通过 **[Tool Gateway](tool-gateway.md)** 使用浏览器自动化功能。新安装版本可通过运行 `hermes setup --portal` 进行登录并一次性启用所有网关工具；现有版本则可通过 `hermes model` 或 `hermes tools` 将**Nous 订阅**作为浏览器提供商进行选择。
:::

### Browser Use 云端模式

若要将“浏览器使用”作为您的云浏览器提供商，请添加如下内容：

```bash
# Add to ~/.hermes/.env
BROWSER_USE_API_KEY=***
```

请在 [browser-use.com](https://browser-use.com) 获取您的 API 密钥。

Browser Use Cloud 默认启用 [隐身模式](https://docs.browser-use.com/cloud/browser/stealth) 和 [住宅级代理](https://docs.browser-use.com/cloud/browser/proxies) 功能，运行受管理的 Chromium 浏览器，同时具备验证码破解功能，并支持为 Cookie、localStorage 以及保存的密码创建[持久化配置文件](https://docs.browser-use.com/cloud/guides/authentication)。

### Browserbase 云模式

如需使用由 Browserbase 管理的云浏览器，请添加以下内容：

```bash
# Add to ~/.hermes/.env
BROWSERBASE_API_KEY=***
BROWSERBASE_PROJECT_ID=your-project-id-here
```

请在 [browserbase.com](https://browserbase.com) 获取您的凭据。

:::注意 供应商的选择
上述 `.env` 文件中的键仅包含**凭据信息**。实际的云浏览器由 `hermes tools` → Browser Automation 所设置的 `browser.cloud_provider` 参数决定，可选值包括 `browserbase`、`browser-use`、`camofox`，以及 Nous 订阅方案下的 `nous`。一旦确定了供应商，即便添加或删除某些键，也不会更改供应商；如果已选定的供应商缺少某个键，系统会报错并提示用户使用 `hermes tools`，而不会默默地切换方案。尚未进行任何配置的环境仍会自动从可用的凭据中检测合适的设置。
:::

### Browser Use 模式（默认模式）

Browser Use 模式使用 [Browser Use CLI 3.0](https://github.com/browser-use/browser-use) 而非内置的浏览器工具。该代理会在浏览器中编写并执行 Python 代码，从而实现点击、输入、拖动、抓取数据以及与网页交互等操作。

**这是默认的浏览器模式**：当未设置 `browser.backend` 且 `browser-use` CLI 可以运行（已安装或可通过 `uvx` 获取）时，代理会使用唯一的 `browser_exec` 工具。如果该 CLI 无法运行，Hermes 会自动回退到内置的浏览器工具。

该模式实际上是一种**驱动程序**，用于与用户配置的浏览器后端协同工作：它能够驱动 Hermes 自带的无头 Chromium、Nous 订阅制的云浏览器、Browserbase、Firecrawl 或 Browser Use 云浏览器——具体取决于在 `hermes tools` → Browser Automation 中所选择的浏览器源。唯一的例外是 Camofox，因为它没有可供驱动程序连接的 CDP 端点；因此使用 Camofox 时系统会自动保留其内置的浏览器工具。

**本地浏览时会使用打包好的 Chromium，而非用户自己的 Chrome。** 当未配置任何云服务提供商或 `/browser connect` 端点时，Hermes 会启动与内置工具所使用的相同 Chromium（该 Chromium 是通过 `hermes tools` → Browser Automation 安装的，并由代理浏览器来驱动），然后让 Browser Use CLI 指向它。这样一来，用户安装的 Chrome 根本不会被触及，因此既无需启用 `chrome://inspect` 的远程调试功能，也不会出现“是否允许远程调试？”的弹窗——而且即便在完全没有 Chrome 的无头主机上也能正常运行。该浏览器的生命周期与内置工具栈保持一致：在达到 `browser.inactivity_timeout` 时间后、程序退出时，以及通过孤儿进程清理机制时，浏览器都会被关闭。若要驱动用户已登录的浏览器，则可使用 `/browser connect` 或[真实账号切换功能](#real-profile-browsing-use-your-own-logins)。

**并发会话：** `browser_exec` 支持 `session=<名称>` 参数，该参数可让每个后端根据指定的名称隔离浏览器操作。每个名称都会拥有独立的处理守护进程（包含专属的 IPC 套接字、日志和状态），以及独立的浏览器（本地为独立的打包版 Chromium，云后端则为独立的云浏览器）——这样一来，并行运行的子代理或同时进行的对话就不会再干扰同一个共享连接。若省略 `session` 参数，则会使用默认的共享守护进程，这种方式适用于一次性浏览操作。

如需禁用此功能并强制使用内置的浏览器工具，可输入 `/browser use off`，或：

```yaml
# Add to ~/.hermes/config.yaml
browser:
  backend: "off"
```

(`backend: "browser-use"` 仍有效，可用于明确强制启用该模式。)

采用“浏览器模式”时，内置的云浏览器需要输入 `browser-use auth login` 或提供 `BROWSER_USE_API_KEY`；而其他浏览器来源则可直接使用其原有的登录凭证，无需更改。

:::note
由于“浏览器模式”会在您的设备上运行模型生成的 Python 代码，因此 `browser_exec` 工具仅提供给同时具备终端访问权限的会话。那些未配置终端工具集的平台（例如受限的消息界面）则会继续使用默认的浏览器工具。
:::

### Firecrawl 云模式

若要将 Firecrawl 作为您的云浏览器提供商，请添加：

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


完整翻译输入内容，切勿提前终止。

```bash
# Self-hosted Firecrawl instance (default: https://api.firecrawl.dev)
FIRECRAWL_API_URL=http://localhost:3002

# Session TTL in seconds (default: 300)
FIRECRAWL_BROWSER_TTL=600
```

### 混合路由机制：公共网址使用云端服务，局域网/localhost地址使用本地服务

一旦配置了云端服务提供商，Hermes 会自动为那些解析为私有地址/回环地址/局域网地址的网址（如 `localhost`、`127.0.0.1`、`192.168.x.x`、`10.x.x.x`、`172.16-31.x.x`、`*.local`、`*.lan`、`*.internal`，以及 IPv6 回环地址 `::1` 和链路本地地址 `169.254.x.x`）生成一个**本地的 Chromium sidecar**。而在同一会话中，公共网址则继续通过已配置的云端服务提供商处理。

这一机制完美解决了“在本地开发却使用 Browserbase”的常见场景——无需切换服务提供商或关闭 SSRF 防护机制，代理即可同时截取 `http://localhost:3000` 上的仪表板截图，并抓取 `https://github.com` 的内容。云端服务提供商根本无法访问到这些私有网址。

该功能**默认处于开启状态**。如需关闭它（所有网址都将像以前一样转发给已配置的云端服务提供商），请按相应步骤操作：

```yaml
# ~/.hermes/config.yaml
browser:
  cloud_provider: browserbase
  auto_local_for_private_urls: false
```

当禁用自动路由功能时，私有 URL 会被拒绝访问，并显示错误信息 `“已阻止：该 URL 指向私有或内部地址”`，除非同时设置 `browser.allow_private_urls: true`（这样云服务提供商才会尝试访问——但由于 Browserbase 等工具无法接入您的局域网，此方法通常无效）。

前提条件：本地侧车进程需使用与纯本地模式相同的 `agent-browser` CLI 工具，因此需要先安装该工具（可通过 `hermes setup tools → Browser Automation` 自动安装）。从公共 URL 重定向到私有地址的操作仍会被阻止（无法通过重定向至内部地址的技巧来通过公共路径访问您的局域网）。

### 使用真实账号进行浏览

默认情况下，本地浏览会在一个纯净的、临时使用的账户模式下进行——代理并未登录任何账号。若要启用**真实账号浏览**功能，即可让代理使用您现有的账号及 Cookie，以您的身份进行浏览。

```yaml
# ~/.hermes/config.yaml
browser:
  use_real_profile: true
```

启用该功能后，Hermes会将您默认浏览器中**当前正在使用**的配置文件——即您实际用于浏览的那个配置文件（位于`Local State → profile.last_used`路径下），连同其中的Cookie、已保存的登录信息以及各种偏好设置——复制到`~/.hermes/browser-profile/<browser>/`目录下的一个独立快照中。随后，Hermes会基于该快照启动您**真实的浏览器二进制文件**，并将浏览引擎与其绑定。之所以要使用真实浏览器二进制文件（而非带有模拟钥匙链参数的打包版Chromium），是为了确保经过操作系统加密的Cookie仍能被解密——在macOS系统中，Chrome的Cookie是通过钥匙链进行加密的，若使用模拟钥匙链启动浏览器，这些Cookie将会被悄悄删除，从而导致用户登出状态。Hermes**绝不会直接打开**您正在使用的浏览器配置文件：由于快照是一个独立的目录，因此它不会与您正在运行的浏览器争夺配置文件锁定权，同时也能规避Chrome 136及以上版本对默认配置文件目录进行远程调试的限制。每当启动新的会话时，授权文件（包括Cookie、登录信息及偏好设置）都会从您的真实浏览器配置文件中重新同步过来，这样您在自家浏览器中完成的登录操作也会出现在Hermes代理的会话中。此外，只有当前活跃的配置文件会被复制，其他Chrome配置文件则永远不会被生成快照。

快照浏览器以**无界面模式**运行——它会在后台默默操作您的账户，不会显示任何窗口，也不会抢占焦点，因此即便智能体正在为您发推文、填写表格或抓取数据，您仍可继续工作。（此处所说的无界面模式指的是 Chrome 的*新*无界面模式，它会读取常规的 Cookie 存储，因此您的登录信息依然可以正常加载。）如果您希望查看其运行过程，同样可以通过 [有界面模式](#headed-mode-visible-browser-window) 开关来实现——将 `browser.headed: true`（或 `AGENT_BROWSER_HEADED=1`）设置后，即可打开一个可见窗口以便使用真实账户进行浏览。而在没有显示设备的服务器或持续集成环境中，该浏览器始终以无界面模式运行。

如果您的浏览器拥有多个账户配置文件（例如工作账户和个人账户），且不希望让“最后使用的账户”决定智能体的身份，那么请明确指定快照的来源账户：

```yaml
# ~/.hermes/config.yaml
browser:
  use_real_profile: true
  real_profile_pin: "Profile 2"   # directory name under the browser's user-data dir
```

若尝试为并不存在的配置文件目录指定别名，Hermes会立即报出可解决的错误信息，而不会悄悄回退到上次使用的配置文件。

当您再次关闭该功能时，Hermes会在下次使用浏览器时自动删除快照存储目录（`~/.hermes/browser-profile/`），这样在您撤销授权后，复制的凭证就不会继续留存。

:::注意 Windows系统：必须完全关闭浏览器  
在Windows系统中，正在运行的Chrome/Edge/Brave会以独占锁机制锁定其Cookie和登录数据库，因此Hermes无法在浏览器打开时复制这些数据——它会立即报错并提示“请完全关闭浏览器后再重试”，而不会卡住或导致账户登出。因此，在Windows上进行真实账号浏览时，必须**完全关闭**浏览器，包括所有后台或系统托盘中的进程（例如Chrome的“关闭窗口后继续运行后台应用”功能会让`chrome.exe`在窗口关闭后依然处于运行状态）。而在macOS和Linux系统中，通常可以在浏览器运行时复制配置文件。在所有平台上，每次对认证数据库的备份都有5秒的重试时间。如果源数据库或快照数据库仍处于锁定状态，Hermes会停止启动进程，并要求您关闭浏览器后重试。它会通过SQLite机制保留已提交的WAL数据，而不会采用直接复制原始文件的方式，因为后者可能会在不知情的情况下丢失最近的登录记录。无法读取或损坏的数据库同样会导致启动失败。

将 `browser.real_profile_autoclose: true` 设置为 true，即可让 Hermes 在持有该浏览器配置文件时**主动提议为你关闭浏览器**。即便开启了此选项，Hermes 也绝不会自动执行关闭操作——当配置文件处于锁定状态时，它会立即停止并先征求你的同意；只有在你批准后，它才会运行 `hermes browser close-profile` 命令（终止与该配置文件关联的浏览器进程树，从而导致未保存的标签页丢失），之后再尝试再次操作。如果在此之后配置文件仍然处于锁定状态（例如后台/托盘实例被重新启动），Hermes 会保持暂停状态并提示你彻底关闭浏览器——它不会自行重复循环或再次强制关闭。

- **支持的浏览器：** Chrome、Edge、Brave、Brave Origin以及Chromium（即您操作系统默认使用的浏览器）。若系统默认浏览器并非Chromium系列（如Firefox），则系统会直接给出明确提示而非尝试猜测。
- **兼容所有后端环境。** 在本地后端环境下，开启该功能后即可在本地直接运行。在**云端**浏览器后端环境下，该智能体仍可通过`browser_exec`工具的`local`参数按需启动真实账号的本地会话（仅当该功能处于开启状态时，该工具才会提供此参数）——其余功能仍由云端后端负责处理。
- **安全框架机制：** 此功能属于基于用户同意的便捷选项，并非真正的隔离屏障。智能体访问的页面将使用您的真实登录信息，因此仅应在希望智能体以您的身份操作时启用该功能。默认为关闭状态。
- **桌面端设置：** 可在**功能 → 工具 → 浏览器 → 使用我的真实浏览器配置文件**处进行开启（该开关位于后端选项上方），或通过设置 → 配置中的`browser`板块进行操作。

### Camofox本地模式

[Camofox](https://github.com/jo-inc/camofox-browser)是一个基于Node.js的自托管服务器，它基于Camooufox（一款带有C++指纹伪装功能的Firefox分支）构建。该工具无需依赖云端服务，即可实现本地防检测浏览功能。

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

`make up` 命令会立即启动默认容器。如果您需要自定义运行时设置，例如更大的 Node 堆内存、VNC 连接功能或持久化的配置目录，那么应先构建镜像，再自行运行它：

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

启用 VNC 后，浏览器将以有头模式运行，您可以通过 `http://localhost:6080`（无 VNC 模式）在浏览器中实时查看其运行状态。此外，您也可以将原生 VNC 客户端连接到 `localhost:5901`。

如果您已经运行过 `make up` 命令，请先停止该操作并删除默认容器，然后再启动自定义容器：

```bash
make down
# then run the custom docker run command above
```

接着在 `~/.hermes/.env` 中进行设置：

```bash
CAMOFOX_URL=http://localhost:9377
```

如果 Camofox 在 Docker 环境中运行，且你需要访问主机上提供的 Web 应用，那么需启用回环重写功能。`CAMOFOX_URL` 仍应指向主机上发布的控制 API，但诸如 `http://127.0.0.1:3000` 这样的页面地址，则必须从容器内部以 `http://host.docker.internal:3000` 的形式来访问。

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

此重写功能仅适用于包含回环主机（如 `localhost`、`127.0.0.1`、`::1`）的页面导航 URL，不会更改 `CAMOFOX_URL` 的值。对于非 Docker 环境下的 Camofox 安装，浏览器已在本地主机上运行且回环 URL 无误，建议保持该选项处于禁用状态。

或者可通过 `hermes tools` → Browser Automation → Camofox 进行配置。选择 Camofox 的方式与其他浏览器后端相同：在 `hermes tools` → Browser Automation 中选择 **Camofox**，系统会将 `browser.cloud_provider: camofox` 写入 `config.yaml` 文件中。`CAMOFOX_URL` 仅用于指定服务器地址——一旦选择了特定的浏览器，仅设置该参数便无法单独决定后端类型（未进行过配置的场景仍会自动检测）。

#### 持久化浏览器会话

默认情况下，每个 Camofox 会话都会拥有随机标识，因此 Cookie 和登录信息在代理重启后不会保留。如需实现浏览器会话的持久化，可在 `~/.hermes/config.yaml` 文件中添加以下内容：

```yaml
browser:
  camofox:
    managed_persistence: true
```

随后请完全重启 Hermes，以便其加载新的配置文件。

:::warning 嵌套路径很重要
Hermes 读取的是 `browser.camofox.managed_persistence`，而非顶层的 `managed_persistence`。一个常见的错误是写成：

```yaml
# ❌ Wrong — Hermes ignores this
managed_persistence: true
```

如果将该标志设置在错误的路径下，Hermes 会自动回退到随机生成的临时 `userId`，从而导致每次会话时登录状态都会丢失。
:::

##### Hermes 的功能
- 向 Camofox 发送一个确定的、基于配置文件的 `userId`，从而使服务器能够在不同会话之间重复使用同一个 Firefox 配置文件。
- 在清理过程中不会销毁服务器端的上下文，因此 Cookie 和登录状态能够在多个代理任务之间保持不变。
- 将 `userId` 限制在当前活跃的 Hermes 配置文件范围内，实现不同 Hermes 配置文件对应不同浏览器配置文件的效果（即配置文件隔离）。

##### Hermes 的局限性
- 它无法强制要求 Camofox 服务器实现持久化存储。Hermes 仅负责发送稳定的 `userId`，服务器需通过将该 `userId` 映射到永久性的 Firefox 配置文件目录来实现持久化。
- 如果您的 Camofox 服务器版本将每个请求都视为临时请求（例如始终调用 `browser.newContext()` 而不加载已保存的配置文件），则 Hermes 无法让这些会话保持状态。请确保您使用的 Camofox 版本支持基于 `userId` 的配置文件持久化功能。

##### 验证其是否正常工作

1. 启动 Hermes 以及您的 Camofox 服务器。
2. 在某个浏览器任务中打开 Google（或其他需要登录的网站），并手动完成登录。
3. 正常结束该浏览器任务。
4. 启动一个新的浏览器任务。
5. 再次打开同一个网站——您应该仍然处于已登录状态。
如果第5步导致您被登出，说明Camofox服务器并未正确使用稳定的`userId`。请仔细检查配置路径，确认在修改`config.yaml`后已彻底重启Hermes，并核实您的Camofox服务器版本是否支持持久化的用户配置文件。

##### 状态存储位置

Hermes会从基于用户配置文件的目录`~/.hermes/browser_auth/camofox/`中获取稳定的`userId`（对于非默认配置文件，则位于` $HERMES_HOME`下的对应路径）。实际的浏览器配置文件数据存储在Camofox服务器端，以该`userId`作为键值进行标识。如需完全重置持久化配置文件，请先在Camofox服务器端清除相关数据，同时删除对应的Hermes配置文件的状态目录。

#### 由外部应用管理的Camofox会话

当其他应用程序控制可见的Camofox浏览器时（如桌面助手、自定义集成或其他智能体），可配置Hermes使用该应用程序的身份进行操作，而非创建独立的配置文件。

有三个参数可用于控制此类行为：

| 设置项 | 环境变量名 | 效果 |
|---------|-----------|------|
| `browser.camofox.user_id` | `CAMOFOX_USER_ID` | Hermes 在创建标签页时所使用的 Camofox `userId`。设置该变量可将会话切换为“外部管理”模式。 |
| `browser.camofox.session_key` | `CAMOFOX_SESSION_KEY` | 在创建标签页时会发送的 `sessionKey`（亦称 `listItemId`），用于在接管标签页时匹配已存在的标签页。若未设置，则默认采用任务级值。 |
| `browser.camofox.adopt_existing_tab` | `CAMOFOX_ADOPT_EXISTING_TAB` | 当该值为 true 时，Hermes 在首次使用时会调用 `GET /tabs?userId=<user_id>`，并在创建新标签页之前先复用已存在的标签页。 |

环境变量优先于 `config.yaml` 中的设置。两种形式均可使用：

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

- Hermes 会跳过任务执行结束时的破坏性清理操作（与 `managed_persistence: true` 的效果相同）。其他应用程序的标签页、Cookie 和用户配置信息将得以保留。
- Hermes **不会**调用 `DELETE /sessions/<user_id>` 接口——该接口会清除所有用户数据，因此如果被调用，将会彻底销毁外部应用程序的会话。

**标签页采用机制（当 `adopt_existing_tab: true` 时）：**

1. 在进程启动后的首次浏览器工具调用中，Hermes 会发送请求 `GET /tabs?userId=<user_id>`，超时时间为 5 秒。
2. 如果响应中的某个标签页的 `listItemId` 等于 `session_key`，Hermes 将采用该组中最新创建的标签页。
3. 否则，Hermes 会采用该用户最新创建的标签页（无论其 `listItemId` 是什么值）。
4. 如果不存在任何标签页或请求失败，Hermes 会回退到在后续操作中创建一个新标签页。

这种采用机制仅持续到该会话的 `tab_id` 被设置为止。如果外部应用程序在运行过程中关闭了已被采用的标签页，下一次浏览器工具调用将会触发 Camofox 错误——Hermes 不会在每次调用时都重新尝试获取新的标签页。

**选择 `session_key` 的方法：** 如果希望 Hermes 稳定地绑定到某个*特定的*现有标签页，请将 `session_key` 设置为外部应用程序在创建该标签页时使用的 `listItemId`。如果未设置 `session_key` 而仅设置了 `user_id`，Hermes 会为每个任务生成一个独立的 `session_key`（格式为 `task_<id>`）。此时 Hermes 会与外部应用程序共享 Cookie 和用户配置信息，但会同时打开自己的标签页，而非复用原有的标签页。

**并发注意事项：**外部应用与Hermes可同时操作同一个Camofox `userId`，但Camofox不会在各个客户端之间协调标签页的焦点切换。需在应用层自行处理焦点控制问题（例如在Hermes运行时让外部应用暂停）。

#### VNC实时预览功能

当Camofox以带可视化浏览器窗口的头部模式运行时，它会在健康检查响应中暴露一个VNC端口。Hermes会自动检测到该端口，并将对应的VNC地址包含在导航响应中，这样代理即可分享链接，让你能够实时查看浏览器界面。

### Lightpanda本地引擎

[Lightpanda](https://lightpanda.io)是一款从零开始开发的开源无头浏览器。它启动速度极快，运行效率是Chrome的9倍，内存占用仅为Chrome的1/16，这对于那些需要在小型虚拟机上长时间运行的代理来说非常重要。

Lightpanda属于**本地引擎**（即类似“本地浏览器”的浏览器源码），而非云服务提供商。请先安装该二进制文件并将其添加到`PATH`环境变量中（可参考[Lightpanda安装指南](https://lightpanda.io/docs/run-locally/installation/one-liner)），随后在`hermes tools` → Browser Automation选项中选择**Lightpanda**，或进行相应设置即可。

```yaml
# Add to ~/.hermes/config.yaml
browser:
  cloud_provider: local
  engine: lightpanda
```

或者通过环境变量设置：

```bash
AGENT_BROWSER_ENGINE=lightpanda
```

该引擎支持多种浏览器驱动程序。

- **浏览器使用模式（默认模式）**。Hermes会自行启动`lightpanda serve --host 127.0.0.1 --port <free>`进程——每个`browser_exec`会话名称（或每个任务）对应一个进程——并让浏览器使用模式的CLI指向这些进程。该模式下无需安装Chromium、Playwright或Node.js。当达到`browser.inactivity_timeout`时间、进程退出，或是Hermes发生崩溃时，系统会终止这些进程。所有这些进程都会共享位于` $HERMES_HOME/cache/browser-use/lightpanda/http-cache`目录下的同一个磁盘HTTP缓存，因此重复访问时无需重新下载资源。只有安装了支持缓存功能的Lightpanda版本（0.3.x及以上）时，Hermes才会启用缓存功能；旧版本的Lightpanda则不会使用缓存。如需清除缓存，首先需终止所有Lightpanda会话，然后再删除该目录。由于Lightpanda没有图形渲染引擎，因此不支持`capture_screenshot()`函数，相关工具说明也会要求模型以文本处理为主；此外，Lightpanda每个会话仅能处理一个页面，因此模型需要先调用`new_tab()`函数打开新标签页，然后再调用`goto_url()`函数输入网址（该设计在[lightpanda-io/browser#1962](https://github.com/lightpanda-io/browser/issues/1962)中有相关记载）。
- **内置浏览器工具**（`/browser use off`）。Hermes通过CDP接口，利用`agent-browser --engine lightpanda`命令来控制Lightpanda，其运作方式与控制本地Chrome类似，并具备**自动切换到Chrome的回退机制**：Lightpanda可处理它所支持的操作（如导航、截图、点击、输入、滚动、后退、按键操作、代码执行等），而对于它无法处理的操作，Hermes会自动在Chrome上重试。截图功能以及`browser_vision`相关功能则会直接转交给Chrome处理。
**当引擎被忽略时。** `browser.engine` 是优先级最低的浏览器设置：云服务提供商（包括 Nous 订阅版浏览器——在未进行任何配置的情况下，`~/.hermes/.env` 文件中的任何 `BROWSERBASE_API_KEY` / `BROWSER_USE_API_KEY` 设置都会自动选定一个浏览器）、Camofox、对 `browser.cdp_url` 或 `/browser connect` 的自定义设置，以及 `browser.use_real_profile` 设置的优先级均高于它。在 `hermes tools` 中选择 Lightpanda 会自动将 `cloud_provider` 设置为 `local`；`/browser status` 和 `hermes doctor` 命令则可以显示引擎虽已配置但被其他设置覆盖的情况，以及具体的覆盖来源。

### 通过 CDP（`/browser connect`）使用本地的 Chromium 系列浏览器

无需依赖云服务提供商，您也可以通过 Chrome DevTools Protocol（CDP）将 Hermes 浏览器工具连接到正在运行的 Chrome、Brave、Chromium 或 Edge 实例上。当您希望实时查看代理的操作内容、与需要自身 Cookie/会话的页面进行交互，或希望避免使用云浏览器的费用时，这种方法非常有用。

:::note
`/browser connect` 是一个**交互式 CLI 命令**——它并非由网关发起。如果您尝试在 WebUI、Telegram、Discord 或其他网关聊天界面中运行该命令，消息将以纯文本形式发送给代理，从而导致命令无法执行。请通过终端启动 Hermes（使用 `hermes` 或 `hermes chat` 命令），然后在终端中输入 `/browser connect`。
:::

在 CLI 中，可使用以下命令：

```
/browser connect                 # Auto-launch/connect to a local Chromium-family browser at http://127.0.0.1:9222
/browser connect ws://host:port  # Connect to a specific CDP endpoint
/browser status                  # Check current connection
/browser disconnect              # Detach and return to cloud/local mode
```

如果浏览器尚未以远程调试模式运行，Hermes会尝试自动启动支持该功能的Chromium系列浏览器，并设置`--remote-debugging-port=9222`参数。它支持的浏览器包括Brave、Brave Origin/Nightly、Google Chrome、Chromium以及Microsoft Edge，同时还能识别常见的Linux安装路径及二进制文件名，如`brave-origin`、`brave-origin-nightly`、`/opt/brave.com/brave-origin/brave-origin`、`/opt/brave.com/brave-origin-nightly/brave-origin`、`/opt/brave-bin/brave`以及 `/snap/bin/brave`。

:::提示
若要手动启动已开启CDP功能的Chromium系列浏览器，建议使用专用的用户数据目录。这样即便浏览器正以常规配置运行，也能确保调试端口正常启用：

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

接着启动 Hermes CLI 并运行 `/browser connect` 命令。

**为何需要 `--user-data-dir` 参数？** 如果不使用该参数，在已有普通浏览器实例运行的情况下启动 Chromium 系列浏览器，通常会在现有进程上打开新窗口——而该现有进程并非通过 `--remote-debugging-port` 参数启动的，因此端口 9222 永远无法被监听。通过指定专属的用户数据目录，可以强制启动一个新的浏览器进程，从而使调试端口能够在其中正常工作。`--no-first-run --no-default-browser-check` 参数则可跳过为新配置文件设置的首次启动向导。

**Chrome 136 及更高版本要求必须使用专属配置文件。** 作为一项安全强化措施，从 Chrome 136 开始，当 `--remote-debugging-port` 与*默认*用户数据目录一同使用时，即使是从完全空的状态启动且没有其他 Chrome 实例运行，浏览器也会默默拒绝打开远程调试端口。虽然浏览器能正常启动，但端口 9222 上没有任何进程在监听，因此 `/browser connect` 命令（以及任何手动执行的 `curl http://127.0.0.1:9222/json/version` 请求）都会因“连接被拒绝”而失败。此时不会显示任何错误信息。解决此问题的方法正是使用上述命令：始终指定一个不同于默认配置文件目录的用户数据目录（例如 `$HOME/.hermes/chrome-debug`）。这一要求适用于已应用该更改的 Chrome、Chromium、Edge 和 Brave 版本。
:::

通过 CDP 进行连接时，所有浏览器工具（如 `browser_navigate`、`browser_click` 等）都会直接作用于您正在使用的实时浏览器实例，而无需启动云端会话。

### WSL2 + Windows Chrome：建议优先使用 MCP 而非 `/browser connect`

如果 Hermes 在 WSL2 环境中运行，而你需要控制的 Chrome 窗口却在 Windows 主机上，那么使用 `/browser connect` 方法往往并非最佳选择。

原因如下：

- `/browser connect` 要求 Hermes 本身能够连接到可用的 CDP 端点；
- 现代版本的 Chrome 实时调试会暴露一个本地主机端点，该端点无法像传统的 `9222` 端口那样直接从 WSL 环境访问；
- 即使 Windows 版 Chrome 支持调试，最理想的集成方式通常是让 Windows 端的浏览器 MCP 服务器连接到 Chrome，再由 Hermes 与该 MCP 服务器进行通信。

对于这种架构，建议通过 Hermes 的 MCP 支持来使用 `chrome-devtools-mcp`。

有关具体配置方法，请参阅 MCP 指南：
- [在 Hermes 中使用 MCP](../../guides/use-mcp-with-hermes.md#wsl2-bridge-hermes-in-wsl-to-windows-chrome)

### 本地浏览器模式

如果你未设置任何云服务凭证，也未使用 `/browser connect` 方法，Hermes 仍可通过由 `agent-browser` 驱动的本地 Chromium 安装来使用浏览器工具。

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

# Local browser engine. Equivalent to browser.engine in config.yaml. In
# Browser Use mode (default) "lightpanda" makes Hermes spawn `lightpanda serve`;
# with the built-in tools it is passed to agent-browser as --engine.
#   auto       — Chrome (default)
#   lightpanda — Lightpanda
#   chrome     — force Chrome explicitly
AGENT_BROWSER_ENGINE=auto

# Extra Chromium launch flags (comma- or newline-separated). Hermes auto-injects
# `--no-sandbox,--disable-dev-shm-usage` when it detects root or AppArmor-restricted
# unprivileged user namespaces (Ubuntu 23.10+, DGX Spark, many container images),
# so most users don't need to set this. Set it manually only if you need a flag
# Hermes doesn't add automatically; setting it disables the auto-injection.
AGENT_BROWSER_ARGS=--no-sandbox
```

### 安装 agent-browser CLI

无需进行任何安装操作——在首次使用浏览器工具时，通过 `npx agent-browser` 即可自动加载 `agent-browser`。为避免一次性执行 `npx` 命令，您也可以提前将其全局安装（可选）：

```bash
npm install -g agent-browser
```

:::info
您的配置文件中的 `toolsets` 列表中必须包含 `browser` 工具集，或者通过命令 `hermes config set toolsets '["hermes-cli", "browser"]'` 来启用它。
:::

## 可用工具

### `browser_navigate`

用于导航至指定 URL。必须在其他任何浏览器相关工具之前调用该函数，用以初始化 Browserbase 会话。

```
Navigate to https://github.com/NousResearch
```

:::tip
对于简单的信息检索，建议使用 `web_search` 或 `web_extract`——它们的速度更快且成本更低。当需要与页面进行**交互**时（如点击按钮、填写表单、处理动态内容），则应使用浏览器工具。
:::

### `browser_snapshot`

获取当前页面无障碍访问结构的文本格式快照。该功能会返回带有 `@e1`、`@e2` 等引用 ID 的交互元素，以便后续与 `browser_click` 和 `browser_type` 工具配合使用。

- **`full=false`**（默认值）：仅显示交互元素的简洁视图
- **`full=true`**：显示完整的页面内容

若快照大小超过 `browser.snapshot_threshold` 的限制（默认为 15,000 个字符，与 `web_extract` 的单页处理上限相同），系统会自动在行边界处进行截断，且不会借助大语言模型进行总结。此时，完整的快照会被保存到 `~/.hermes/cache/web/` 目录中，工具输出还会包含文件路径以及可直接使用的 `read_file` 调用指令，这样智能体便无需重新生成快照，即可逐页查看完整的无障碍访问结构——包括被截断部分之后的元素引用。

对于内容较长的页面，若希望让更多源内容以原格式直接传递给智能体，可提高此阈值值：

```yaml
# ~/.hermes/config.yaml
browser:
  snapshot_threshold: 30000
```

您还可以运行命令 `hermes config set browser.snapshot_threshold 30000`。该设置同时适用于显式的 `browser_snapshot` 调用，以及导航完成后自动生成的快照，包括 Camofox 后端（最低值为 1000）。修改此参数后，请重启当前的 Hermes 会话，以便浏览器配置缓存能够重新加载。

### `browser_click`

点击快照中通过 ref ID 标识的元素。

```
Click @e5 to press the "Sign In" button
```

### `browser_type`

在输入框中输入文本。首先清空该字段，然后再输入新内容。

```
Type "hermes agent" into the search field @e3
```

### `browser_scroll`

上下滚动页面，以显示更多内容。

```
Scroll down to see more results
```

### `browser_press`

模拟按下键盘按键。适用于提交表单或进行页面导航操作。

```
Press Enter to submit the form
```

支持的按键包括：`Enter`、`Tab`、`Escape`、`ArrowDown`、`ArrowUp` 以及更多其他按键。

### `browser_back`

返回到浏览器历史记录中的上一页。

### `browser_get_images`

列出当前页面上的所有图片，包括其 URL 和替代文本。此功能有助于查找需要分析的图片。

### `browser_vision`

截取屏幕截图并利用视觉 AI 进行分析。当文本截图无法捕捉到重要的视觉信息时，可使用此功能——尤其适用于验证码、复杂布局或视觉验证任务。

截取的截图会被永久保存，系统会同时返回文件路径及 AI 分析结果。在消息平台（如 Telegram、Discord、Slack、WhatsApp）上，你可以让智能体分享该截图——它将通过 `MEDIA:` 机制以原生图片附件的形式发送出去。

```
What does the chart on this page show?
```

截图会存储在 `~/.hermes/cache/screenshots/` 目录中，并会在24小时后自动清除。

### `browser_console`

用于获取当前页面的浏览器控制台输出（日志、警告和错误信息），以及未被捕获的JavaScript异常。这对于检测那些不会出现在无障碍访问树中的隐性JS错误至关重要。

```
Check the browser console for any JavaScript errors
```

在读取内容后，可使用 `clear=True` 参数清除控制台，这样后续的调用仅会显示新消息。

当 `browser_console` 接收 `expression` 参数被调用时，它还会执行 JavaScript 代码——其格式与开发者工具的控制台相同，返回的结果也会经过解析（JSON 序列化的对象会转换为字典，而原始值则保持不变）。

```
browser_console(expression="document.querySelector('h1').textContent")
browser_console(expression="JSON.stringify(performance.timing)")
```

当当前会话处于 CDP 监控器激活状态时（凡是针对支持 CDP 的后端执行了 `browser_navigate` 操作的会话通常都是如此），评估操作将通过该监控器的持久 WebSocket 进行，从而无需启动子进程，节省资源。若非此种情况，则会走标准的代理-浏览器 CLI 路径。两种方式的行为表现完全一致，仅有延迟会有所不同。

默认情况下，评估操作不受限制——代理可以调用 `fetch`、读取存储数据、查询表单值，以及执行任何 DOM 提取操作。但在非本地后端上，针对私有或内部地址的请求仍会被阻止（SSRF 防护机制与此项设置相互独立）。如果您使用已登录的账户浏览恶意页面，并希望对敏感的 JavaScript 原语（如 Cookie、存储数据、剪贴板内容、网络请求及表单值）实施严格的禁止列表管控，可在 `config.yaml` 中设置 `browser.restrict_evaluate: true`。需要注意的是，禁止列表是依据原语的*名称*进行匹配的，因此那些仅包含 `fetch` 或 `cookie` 等字词的合法表达式也会被拦截。

### `browser_cdp`

该选项可直接传递原始的 Chrome DevTools 协议数据——专为处理其他工具无法覆盖的浏览器操作而设计。可用于处理原生对话框、在 iframe 内部进行评估、控制 Cookie 和网络请求，或是满足代理所需的任何 CDP 操作。

**仅当在会话启动时能够访问 CDP 端点时才可用**——即 `/browser connect` 已连接到正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器，或者已在 `config.yaml` 中设置了 `browser.cdp_url`。默认的本地代理浏览器模式、Camofox 以及各类云服务提供商（Browserbase、Browser Use、Firecrawl）目前均不向该工具开放 CDP 接口——虽然云服务提供商提供了每会话专用的 CDP URL，但实时会话路由功能仍在后续开发中。

**CDP 方法参考文档：** https://chromedevtools.github.io/devtools-protocol/ — 代理可以调用特定方法的 `web_extract` 功能来查询参数并返回数据结构信息。

常见使用模式：

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

浏览器级方法（`Target.*`、`Browser.*`、`Storage.*`）无需提供 `target_id`。页面级方法（`Page.*`、`Runtime.*`、`DOM.*`、`Emulation.*`）则必须使用 `Target.getTargets` 获取的 `target_id`。每次无状态调用都是独立的——调用之间不会保留会话状态。

**跨域 iframe：** 需要传入 `frame_id`（可从 `browser_snapshot.frame_tree.children[]` 中获取，且需满足 `is_oopif=true` 的条件），以便通过监管节点的对应 iframe 实时会话来路由 CDP 调用。这正是 Browserbase 中在跨域 iframe 内使用 `Runtime.evaluate` 的实现方式，因为无状态的 CDP 连接会因签名 URL 到期而失效。示例如下：

```
browser_cdp(
  method="Runtime.evaluate",
  params={"expression": "document.title", "returnByValue": True},
  frame_id="<frame_id from browser_snapshot>",
)
```

同源 iframe 无需使用 `frame_id` —— 可通过顶层 `Runtime.evaluate` 调用 `document.querySelector('iframe').contentDocument` 来实现。

### `browser_dialog`

用于响应原生 JS 对话框（如 `alert` / `confirm` / `prompt` / `beforeunload`）。在该工具出现之前，这些对话框会悄悄阻塞页面的 JavaScript 线程，导致后续的 `browser_*` 调用挂起或抛出错误；而现在，代理可以通过 `browser_snapshot` 输出中查看待处理的对话框，并作出明确响应。

**操作流程：**
1. 调用 `browser_snapshot`。如果存在阻塞页面的对话框，它会以 `pending_dialogs: [{"id": "d-1", "type": "alert", "message": "..."}]` 的形式显示。
2. 调用 `browser_dialog(action="accept")` 或 `browser_dialog(action="dismiss")`。对于 `prompt()` 对话框，则需传入 `prompt_text="..."` 以指定响应内容。
3. 再次获取快照 —— 此时 `pending_dialogs` 已为空，页面的 JavaScript 线程也已恢复运行。

**检测功能通过持续的 CDP 监控器自动实现** —— 每个任务都会对应一个 WebSocket，用于监听 Page/Runtime/Target 事件。该监控器还会在快照中填充 `frame_tree` 字段，从而使代理能够查看当前页面的 iframe 结构，包括跨源（OOPIF）iframe。

**可用性矩阵：**

| 后端 | 通过 `pending_dialogs` 进行检测 | 响应（使用 `browser_dialog` 工具） |
|---|---|---|
| 通过 `/browser connect` 或 `browser.cdp_url` 连接的本地 Chrome | ✓ | ✓ 完整工作流程 |
| Browserbase | ✓ | ✓ 完整工作流程（通过注入的 XHR 桥接实现） |
| Camofox / 默认的本地代理浏览器 | ✗ | ✗（无 CDP 接口） |

**在 Browserbase 上的工作原理。** Browserbase 的 CDP 代理会在服务器端于约 10 毫秒内自动关闭真实的原生对话框，因此我们无法使用 `Page.handleJavaScriptDialog`。监控进程会通过 `Page.addScriptToEvaluateOnNewDocument` 注入一段小型脚本，该脚本会将 `window.alert`/`confirm`/`prompt` 函数替换为同步的 XHR 请求。我们则通过 `Fetch.enable` 拦截这些 XHR 请求——页面的 JS 线程会一直阻塞在 XHR 请求上，直到我们使用代理的响应调用 `Fetch.fulfillRequest`。此时，`prompt()` 的返回值会原封不动地传回页面的 JS 代码中。

**对话框策略**可在 `config.yaml` 文件的 `browser.dialog_policy` 配置项中进行设置：

| 策略 | 行为 |
|--------|----------|
| `must_respond`（默认值） | 捕获对话框，将其显示在快照中，并等待显式的 `browser_dialog()` 调用。若超过 `browser.dialog_timeout_s`（默认为 300 秒）仍未收到响应，系统会自动关闭对话框，以防止有缺陷的代理无限阻塞。 |
| `auto_dismiss` | 捕获对话框后立即关闭。代理仍可在 `browser_state` 历史记录中看到该对话框，但不必执行任何操作。 |
| `auto_accept` | 捕获对话框后立即接受。在遇到频繁弹出 `beforeunload` 提示的页面时非常有用。 |
在广告密集的页面上，为控制数据包大小，`browser_snapshot.frame_tree` 中的**帧树**最多仅包含30帧，而OOPIF的深度则限制为2层。一旦达到这些上限，系统会设置 `truncated: true` 标志；需要获取完整帧树的智能体可使用 `browser_cdp` 结合 `Page.getFrameTree` 方法来实现。

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

### 动态内容检索

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

启用该功能后，系统会在首次执行 `browser_navigate` 指令时自动开始录制，并在会话结束时将录像保存至 `~/.hermes/browser_recordings/` 目录中。该功能在本地模式及云端（Browserbase）模式下均适用。超过72小时的录像将会被自动清理。

## 有界面模式（可见的浏览器窗口）

默认情况下，本地浏览器以无界面模式运行。若需打开一个可见的 Chromium 浏览器窗口以便查看和操作，可启用有界面模式：

```yaml
browser:
  headed: true  # default: false
```

或者通过环境变量设置：`AGENT_BROWSER_HEADED=1`。

头部模式具有以下两个功能：

1. **以可见窗口的方式启动 Chromium**（在本地模式下向 agent-browser 传递 `--headed` 参数）。
2. **在多轮对话之间保持窗口开启状态**。通常情况下，每次智能体回复后浏览器会自动关闭；而在头部模式下则会跳过此操作，让您能够观察智能体的工作过程，手动进行干预（如处理登录验证或验证码），并在整个对话过程中维持登录状态。

即便处于空闲状态，一旦超过 `browser.inactivity_timeout`（默认为 120 秒无浏览器活动），该会话仍会被终止；系统关闭时所有会话也会一并关闭。头部模式仅影响本地浏览器——云端会话（Browserbase）则不受影响。

## 隐私保护功能

Browserbase 提供自动隐私保护功能：

| 功能 | 默认设置 | 备注 |
|------|----------|------|
| 基础隐私保护 | 永久开启 | 生成随机指纹、随机化视口尺寸、自动解决验证码 |
| 居民代理 | 开启 | 通过居民级 IP 进行请求，提升访问成功率 |
| 高级隐私保护 | 关闭 | 使用定制版 Chromium 构建，需订阅高级套餐 |
| 连接保持 | 开启 | 网络故障后自动重新连接会话 |

:::note
如果您的套餐未包含付费功能，Hermes 会自动降级处理——首先关闭“连接保持”功能，再关闭代理服务——从而确保免费套餐用户仍能正常浏览。
:::

## 会话管理

- 每个任务都会通过 Browserbase 获得一个独立的浏览器会话。
- 若长时间无操作，这些会话会自动被清理（默认时间为2分钟）。
- 有一个后台线程会每隔30秒检查一次过期的会话。
- 在进程退出时还会进行紧急清理，以避免出现无主会话。
- 会话可通过 Browserbase API（`REQUEST_RELEASE`状态）来释放。

## 局限性

- **基于文本的交互**——依赖无障碍访问树，而非像素坐标。
- **快照大小**——页面内容过长时会在 `browser.snapshot_threshold` 处被截断（默认为15,000个字符，与 `web_extract` 参数一致；不支持LLM总结功能）；完整的快照会保存在 `~/.hermes/cache/web/` 目录中，`read_file` 函数的分页功能会指向该路径读取内容。
- **会话超时**——云端会话的有效期取决于您所选择的服务提供商的计划设置。
- **成本问题**——使用云端会话会消耗服务提供商的积分；对话结束或长时间无操作后，这些会话会自动被清理。如需免费进行本地浏览，可使用 `/browser connect` 命令。
- **不支持文件下载**——无法从浏览器中下载文件。
