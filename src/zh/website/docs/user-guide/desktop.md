---
sidebar_position: 3
title: "Desktop App"
description: "The native Hermes desktop app — a polished experience for chatting with Hermes, with streaming tool output, side-by-side previews, a file browser, voice, cron, profiles, skills, and settings. macOS, Windows, and Linux."
---

# 桌面应用

Hermes桌面应用是一款原生应用程序，它基于与CLI及网关中使用的**完全相同**的Agent构建——相同的配置、相同的API密钥、相同的会话、相同的技能以及相同的内存。它并非独立的产品，也不是轻量级的克隆版；而是采用了相同的Hermes Agent核心与设置，并通过精心设计的现代化用户界面来操控该Agent。如果您曾在终端中使用过`hermes`，那么您在那里配置的所有内容都会同步到桌面应用中，而在这里进行的任何操作也会实时反映在终端上。

该应用支持在**macOS、Windows和Linux**系统上运行。

:::提示 哪个界面对应哪种方式？
Hermes提供了多种前端界面，它们均与同一个Agent交互：

- **桌面应用**（即此页面）——一款专为聊天、配置和管理功能设计的原生应用程序。
- **CLI**（`hermes`）和**[TUI](./tui.md)**（`hermes --tui`）——终端界面。
- **[Web控制面板](./features/web-dashboard.md)**（`hermes dashboard`）——基于浏览器的管理面板；其可选的**聊天**标签页可通过伪终端嵌入TUI界面。

您可以根据当前需求选择合适的界面。由于所有界面共享状态，因此您可以在一个界面中开始会话，然后在另一个界面中继续该会话。
:::

## 安装

请按照[Hermes桌面应用的安装说明](../getting-started/installation.md)进行操作。

如果您已经安装了Hermes，只需直接运行即可。

```bash
hermes desktop
```

该模式将使用您当前的配置、密钥、会话及技能。

## 应用功能概览

桌面应用采用以聊天为主的界面设计，左侧为导航侧边栏。它支持同时管理多个智能体对话、配置消息传输服务、生成处理结果、浏览项目文件夹结构，以及同时处理多个项目。

### 聊天界面

这是应用的中心区域，您将享有以下功能：

- **实时流式响应**：在智能体工作过程中，可查看工具的实时操作状态及结构化的工具调用摘要。
- **统一的对话历史记录**：与所有Hermes界面一致——在此启动的会话可在CLI/TUI中继续，反之亦然。
- **拖放文件功能**：可将文件拖放到聊天区域的任意位置，作为下一条消息的附件。
- **右侧预览栏**：在继续聊天的同时，可并排查看网页、文件及工具输出结果。
- **提示词编辑器历史记录与队列管理**：在空白的提示词编辑器中按下上下箭头键，即可调出并重复使用之前的提示词；还可以在消息发送前对其进行编辑。

#### 状态栏

位于聊天界面底部的状态栏可实时显示会话状态，并无需打开设置菜单即可提供快速控制功能：

- **内联模型选择器**：可直接从状态栏切换当前会话所使用的模型。
- **会话级YOLO开关**：仅为当前会话开启或关闭YOLO模式（与TUI功能一致）。YOLO可绕过危险命令的确认提示，但请注意其风险——详情请参阅[安全设置 → YOLO模式](./security.md#yolo-mode)。

若要与另一台机器上的Hermes实例聊天而非使用内置的本地后端，请参阅下文的[连接远程后端](#connecting-to-a-remote-backend)；如需了解远程托管控制台连接的完整机制（包括认证网关、/api/ws聊天套接字以及WebSocket关闭码处理方式），请参阅[Web控制台 → 将Hermes桌面应用连接到远程后端](./features/web-dashboard.md#connecting-hermes-desktop-to-a-remote-backend)。

### 文件浏览器

无需离开应用即可浏览和预览工作目录，非常适合在智能体读取、写入或编辑文件时进行实时查看。可通过`hermes desktop --cwd <路径>`（或`HERMES_DESKTOP_CWD`环境变量）设置初始项目目录。

### 语音功能

支持与Hermes进行语音对话并听到回复，功能与其它平台上的[语音模式](./features/voice-mode.md)相同。在macOS系统中，系统会提示一次以获取麦克风访问权限。

### 设置与引导

无需编辑YAML文件，即可通过直观的界面管理服务提供者、模型、工具及凭证。首次运行时的引导流程可在几秒钟内让您发送第一条消息。设置面板涵盖服务提供者/密钥管理、模型选择、工具集配置、MCP服务器、网关设置以及会话管理功能。

- **服务提供者设置面板**：专门用于管理推理服务提供者，提供“账户/API密钥”式界面，便于登录并为每个提供者存储凭证。
- **菜单中显示所有提供者和模型**：GUI界面会展示完整的提供者列表以及`hermes model`所识别的所有模型，因此您可以从与CLI相同的目录中进行选择，而非仅查看经过筛选的子集。
- **xAI Grok OAuth支持**：Grok在启动器中被视为一级OAuth提供者，可通过浏览器流程进行登录，与其他OAuth提供者操作方式相同。
- **通过GUI安装工具后端**：可直接在应用内运行工具后端的安装步骤，无需切换到终端。
- **辅助模型警告功能**：如果您将主模型更改为新的服务提供者，而某些辅助任务（如标题生成、摘要提取等）仍绑定在另一个提供者上，应用会发出警告，防止您在不知情的情况下将工作分配到两个不同的提供者上。

首次运行引导流程已采用统一的覆盖式设计系统重新设计，您还可以选择**稍后选择服务提供者**，跳过提供者设置，直接进入应用使用。

### 管理面板

该应用还提供了更全面的Hermes管理功能，让您无需切换到终端即可操作：

- **技能管理**：浏览、安装及管理[技能](./features/skills.md)。
- **定时任务**：查看和管理[计划任务](../reference/cli-commands.md#hermes-cron)。
- **配置文件管理**：在多个[Hermes配置文件](./profiles.md)之间切换（每个配置文件拥有独立的配置、技能和会话）。
- **消息传输设置**：配置网关通道。
- **智能体管理**与**命令中心**：用于多智能体协作的管理界面。

### 键盘快捷键与导航

- **命令面板**：按下**Cmd+K**（Windows/Linux系统为Ctrl+K），即可通过键盘快速执行操作并导航应用。
- **可重新绑定的快捷键**：设置面板中的快捷键选项允许您将应用的键盘快捷键映射为自己的自定义按键。
- **自定义缩放快捷键**：支持以半步为单位调整界面缩放比例，从而更精细地控制文本大小。
- **界面语言切换器**：可在应用内直接切换界面语言，包括简体中文（zh-Hans）。

### 会话与配置文件

- **优化后的会话列表**：经过重新设计的会话列表具备归档功能，并采用了良好的会话管理机制，确保会话数量增多时仍能保持清晰易管。
- **按ID搜索会话**：可直接通过会话ID查找特定会话。
- **多配置文件并行会话**：可在多个[配置文件](./profiles.md)上同时运行会话，并可通过跨配置文件的`@session`链接引用其他配置文件中的会话。

## 更新功能

应用会在后台自动检查更新，一旦有新版本可用，即可一键更新。

[手动更新流程](https://hermes-agent.nousresearch.com/docs/getting-started/updating)同样适用于通过GUI进行的更新操作。

## 卸载功能

打开**设置 → 关于 → 危险区域**，然后选择要删除的内容范围：

- **仅卸载聊天GUI**：仅删除桌面应用及其数据；Hermes智能体、您的配置及聊天记录将保留。（相当于`hermes uninstall --gui`命令。）
- **卸载GUI和智能体，保留我的数据**：删除应用和智能体，但会保留配置、聊天记录及密码，以便日后重新安装。（相当于`hermes uninstall`命令。）
- **彻底卸载所有内容**：删除应用、智能体以及所有用户数据。（相当于`hermes uninstall --full`命令。）

应用会先关闭以完成卸载操作（清理工作会在应用退出后执行，用于移除正在运行的应用包及其虚拟环境）。如果未安装本地智能体（例如仅使用连接远程后端的“轻量级”GUI客户端），则智能体相关的卸载选项会自动隐藏。

您也可以通过终端执行相同操作——使用`hermes uninstall --gui`仅卸载GUI部分，或使用`hermes uninstall`/`hermes uninstall --full`同时卸载智能体。

:::note
从**源代码版本**（即`hermes desktop`的开发者构建版本）运行`hermes uninstall --gui`命令时，还会同时删除工作区中的`node_modules`目录以及`apps/desktop/{dist,release}`目录下的构建输出文件，因为这些都是GUI版本的构建产物。这些文件可通过`hermes desktop`（或`npm install`后再重新构建）恢复——但如果您正在对桌面应用进行开发，可能需要之后重新安装依赖项。
:::

## CLI参考：`hermes desktop`

如需通过CLI启动该应用，只需运行`hermes desktop`即可。默认情况下，它会先安装工作区的Node依赖项，构建当前操作系统版本的未打包Electron应用，然后再启动该打包后的应用。

| 标志                  | 描述                                                                 |
|-----------------------|----------------------------------------------------------------------|
| `--skip-build`         | 跳过npm安装/打包步骤，直接启动`apps/desktop/release`目录中已有的未打包应用 |
| `--force-build`        | 即使内容版本标识相同，也强制进行完整重建                                 |
| `--build-only`         | 仅构建桌面应用，不启动它（用于`hermes update`命令）                       |
| `--source`            | 直接使用`apps/desktop/dist`目录中的文件通过`electron .`启动应用，而非使用打包后的应用 |
| `--cwd PATH`           | 设置桌面聊天会话的初始项目目录（相当于设置`HERMES_DESKTOP_CWD`变量）     |
| `--hermes-root PATH`    | 覆盖应用所使用的Hermes源代码根目录（相当于设置`HERMES_DESKTOP_HERMES_ROOT`变量） |
| `--ignore-existing`   | 在解析后端时，强制让应用忽略`PATH`环境变量中已存在的任何`hermes` CLI命令 |
| `--fake-boot`          | 启用确定的启动延迟，用于验证启动界面功能                                 |

## 工作原理

打包后的应用仅包含Electron外壳程序。首次启动时，它会将Hermes Agent运行时组件安装到`HERMES_HOME`目录中（即`~/.hermes`，在Windows系统中为`%LOCALAPPDATA%\hermes`）——这一路径与CLI安装使用的路径相同，这也是两者可以互相替代的原因。React渲染器通过标准的网关API与`hermes dashboard`后端进行通信，并复用已有的智能体功能，而非重新实现。安装、后端解析以及自我更新等功能均运行在Electron主进程之中。

## 连接远程后端

默认情况下，该应用会启动并管理自己的**本地**后端。您也可以将其配置为连接到运行在另一台机器上的Hermes后端——可以是VPS、家庭服务器，或是通过Tailscale连接的Mini设备。

:::info 远程后端是一个正在运行的`hermes dashboard`进程
“远程后端”指的是运行在远程机器上的**`hermes dashboard`**服务器——桌面应用正是连接到该服务器的。除非该控制台实际处于运行状态且可访问，否则本节中的任何功能都无法正常工作。桌面应用不会自动启动该控制台；需要由您（或`systemd`服务）在远程主机上保持`hermes dashboard`持续运行，然后应用才会连接到它。如果您还使用消息通道（如Telegram、Discord等），则**网关**是一个需要单独启动的长期运行的进程——具体说明请参见设置步骤后的备注。
:::

连接过程分为两个部分：在后端端，您需要通过**认证提供者**来保护控制台；而在应用端，则需输入后端的URL并完成登录。将控制台绑定到非回环地址后，其认证网关会自动启用，而您所配置的认证提供者则决定桌面应用是否能够成功接入。

**请根据后端所在位置选择合适的认证提供者：**- **OAuth（Nous Portal）——适用于需要访问本地机器之外的任何服务的场景。**登录过程会通过您的Nous账户进行验证，因此非常适合用于VPS、公共主机或任何远程后端。请使用`hermes dashboard register`命令（或Portal的[`/local-dashboards`](https://portal.nousresearch.com/local-dashboards)页面）注册控制面板，以配置其OAuth客户端，随后即可通过应用中的“使用Nous Research登录”功能进行认证。如果您自行搭建了身份提供器，自托管的OIDC提供器也能实现相同的功能。
- **用户名/密码——仅适用于本地或受信任网络环境。**当后端位于同一受信任的局域网内，或只能通过VPN（如Tailscale）访问时，这是最简单的方案。该方法无需外部身份提供器，仅通过一个共享的凭证进行保护，**因此请勿将其用于面向公网的控制面板**——此类场景应优先使用OAuth。

本节其余部分介绍用户名/密码登录方式，是因为在受信任网络中快速搭建控制面板最为便捷；关于OAuth登录方式的详细内容，请参阅[Web Dashboard → 默认提供器：Nous Research](./features/web-dashboard.md#default-provider-nous-research)。

### 在后端（远程机器）上

设置用户名和密码，然后让控制面板绑定到一个可访问的地址并启动运行。这些凭证存储在`~/.hermes/.env`文件中（即密钥文件，权限设置为0600）：

```bash
# 1. Set the dashboard login credentials.
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=choose-a-strong-password
# Recommended: a stable signing secret so sessions survive restarts.
# Without it a random key is generated per boot and you'll be logged out
# on every restart.
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env

# 2. Run the dashboard bound to a reachable address. The non-loopback bind
#    engages the auth gate; the username/password provider handles login.
hermes dashboard --no-open --host 0.0.0.0 --port 9119
```

只要需要桌面应用能够保持连接，就请让 `hermes dashboard` 进程持续运行——一旦该进程停止，应用便无法再访问后端。建议通过 `systemd`、`tmux` 或您选择的进程管理工具来运行它，这样即便退出登录或重启系统，进程依然能正常存在。

另外，如果您依赖消息通道，还需确保远程主机上的**网关正在运行**——桌面应用实际上是与仪表板后端进行通信，而 Telegram/Discord/Slack 等消息平台的网关连接则是另一个独立的进程，需要您自行启动并持续维持其运行状态。关于网关的设置方法，请参阅 [消息功能](./messaging/index.md)。

不想将明文密码直接存储在系统中？可以改为使用 scrypt 哈希值作为密码，可通过以下命令生成哈希值：`python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"`。完整的配置项（包括 config.yaml 中的键、各类环境变量以及速率限制设置），可参见 [Web 仪表板 → 用户名/密码提供器](./features/web-dashboard.md#usernamepassword-provider-no-oauth-idp)。

如果选择以 systemd 服务的方式运行仪表板，请为该服务设置 `EnvironmentFile=%h/.hermes/.env`，这样在系统启动时，相关凭证就会自动加载到环境变量中。

:::warning
仪表板会读取和写入您的 `.env` 文件（其中包含 API 密钥及敏感信息），同时还能执行代理命令。上述的用户名/密码认证方式仅适用于可信网络环境——切勿将受密码保护的仪表板直接暴露在公网上，应将其置于 VPN 后面保护。[Tailscale](https://tailscale.com/) 是一个理想的解决方案：让仪表板绑定到设备的 Tailscale IP 地址（通过 `--host <tailscale-ip>` 参数设置），并将远程地址设为 `http://<tailscale-ip>:9119`，这样只有同一 Tailscale 网络内的设备才能访问它。若需通过公网连接后端，则应使用 **OAuth (Nous Portal)** 提供器。
:::

### 在应用内操作

**设置 → 网关 → 远程网关：**

1. **远程地址** — `http://<backend-host>:9119`（如果在前端设置了反向代理，可使用如 `/hermes` 这样的路径前缀）
2. **登录** — 应用会自动识别后端支持的认证方式，并相应显示按钮。对于用户名/密码类型的后端，会显示一个**登录**按钮，引导用户填写凭证（即步骤 1 中设置的用户名和密码）；而对于 OAuth 类型的后端，则会显示**使用 <提供器> 登录**的选项（例如“使用 Nous Research 登录”），从而通过对应提供器的浏览器界面完成登录。无论哪种方式，最终都会在应用端与后端建立已认证的会话。
3. **保存并重新连接** — 该操作会将桌面终端切换到远程后端。会话会自动刷新；如果设置了 `HERMES_DASHBOARD_BASIC_AUTH_SECRET`，即便系统重启，用户也会保持登录状态。

您也可以在启动应用之前，通过 `HERMES_DESKTOP_REMOTE_URL` 环境变量直接设置后端地址（该参数会覆盖应用内的设置）；不过仍需通过“网关”设置面板进行登录操作。

:::note 每个配置文件独立的远程主机
远程网关主机是按 [配置文件](./profiles.md) 单独配置的，因此每个配置文件都可以指向不同的远程后端（或继续使用本地后端）。切换配置文件时，应用连接的远程主机也会随之改变。
:::

### 故障排除

- **登录失败，出现 401 错误或“凭证无效”提示** — 说明用户名或密码与后端配置的 `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` / `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` 不匹配。后端对于未知用户和错误密码会返回相同的通用错误信息（不会暴露具体差异），因此请务必仔细核对这两项内容。可通过以下命令确认网关是否正在运行：`curl -s http://<host>:9119/api/status | jq '.auth_required, .auth_providers'`，正常情况下该命令应返回 `true`，且 `auth_providers` 列表中应包含 `"basic"`。
- **没有“登录”按钮，而是要求输入会话令牌** — 说明后端的用户名/密码认证功能未启用。执行 `/api/status` 命令后，`auth_providers` 列表中不会出现 `"basic"` 项。请确认 `~/.hermes/.env` 文件中已同时设置了用户名和密码（或密码哈希值），并且仪表板进程确实已加载了这些配置。
- **每次重启后都会自动登出** — 请为 `HERMES_DASHBOARD_BASIC_AUTH_SECRET` 设置一个固定值。如果不设置该变量，每次系统启动时都会重新生成令牌签名密钥，从而导致所有会话失效。
- **连接被拒绝或超时** — 可能是因为后端绑定在了默认的 `127.0.0.1` 地址上，或是防火墙/VPN 阻断了对应端口。建议将后端绑定到 `0.0.0.0` 或 Tailscale IP 地址，并在可信网络范围内开放该端口。

从 Web 仪表板的角度进行相同配置的方法，可参阅 [Web 仪表板 → 将 Hermes 桌面应用连接到远程后端](./features/web-dashboard.md#connecting-hermes-desktop-to-a-remote-backend)；相关环境变量则列在 [环境变量 → Web 仪表板与 Hermes 桌面应用](../reference/environment-variables.md#web-dashboard--hermes-desktop) 中。

## 故障排除

系统启动日志会保存在 `HERMES_HOME/logs/desktop.log` 文件中（其中包含后端输出信息及最近的 Python 错误堆栈）——如果应用报告启动失败，首先请查看该文件。您也可以通过命令行实时查看日志内容：

```bash
hermes logs gui -f
```

常见重置操作：

```bash
# Force a clean first-launch setup (macOS/Linux)
rm "$HOME/.hermes/hermes-agent/.hermes-bootstrap-complete"

# Rebuild a broken Python venv (macOS/Linux)
rm -rf "$HOME/.hermes/hermes-agent/venv"

# Reset a stuck macOS microphone prompt
tccutil reset Microphone com.nousresearch.hermes
```

### “构建桌面应用”步骤在下载 Electron 时卡住

在构建过程中，系统会从 `github.com/electron/electron/releases` 下载 Electron 运行时环境（约 114 MB）。如果安装程序在“构建桌面应用”阶段停滞不前，且控制台持续显示“retrying attempt=…”之类的信息，那就说明您的网络存在限制或被屏蔽了（可能是防火墙、代理设置或地区限制所致）。

安装程序会自动进行自我修复：在构建失败时，它首先会清除损坏的 Electron 压缩包缓存并重新尝试；如果仍然失败且您未设置 `ELECTRON_MIRROR`，它会通过 Electron 社区常用的镜像站 `npmmirror.com` 再次尝试下载。`@electron/get` 会通过对下载内容进行 SHASUM 校验来确保文件完整性，但这些校验值同样来自该镜像站——因此这种方式能检测到损坏或下载不完整的文件，却无法识别被篡改的镜像站。如果您不愿依赖第三方托管服务，可以自行指定 `ELECTRON_MIRROR` 值（见下文）；无论何时进行构建，系统都不会覆盖您已设置的值。

如需**选择自定义镜像站**（例如企业内部或可信的镜像站），请在手动安装或重新构建之前设置 `ELECTRON_MIRROR` —— 系统会尊重您的设置，不会对其进行覆盖。

```bash
ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/ \
  bash -c 'cd "$HOME/.hermes/hermes-agent/apps/desktop" && CSC_IDENTITY_AUTO_DISCOVERY=false npm run pack'
```

如需手动清除损坏的缓存 ZIP 文件：

```bash
rm -f "$HOME/Library/Caches/electron"/electron-*.zip   # macOS
rm -f "$HOME/.cache/electron"/electron-*.zip            # Linux
```

## 从源代码构建

如果您希望直接修改应用程序本身，只需从仓库根目录安装一次工作空间依赖项，然后从 `apps/desktop` 目录启动开发服务器即可：

```bash
npm install          # from repo root — links apps/desktop, web, apps/shared
cd apps/desktop
npm run dev          # Vite renderer + Electron, which boots the Python backend
```

可将该应用指向特定的结账页面，或通过独立的配置环境将其与真实环境隔离开来：

```bash
HERMES_DESKTOP_HERMES_ROOT=/path/to/clone npm run dev
HERMES_HOME=/tmp/throwaway npm run dev
npm run dev:fake-boot   # exercise the startup overlay with deterministic delays
```

构建安装程序：

```bash
npm run dist:mac     # DMG + zip
npm run dist:win     # NSIS + MSI
npm run dist:linux   # AppImage + deb + rpm
npm run pack         # unpacked app under release/ (no installer)
```

当环境中存在相应的凭证时（macOS 下为 `CSC_LINK` / `CSC_KEY_PASSWORD` / `APPLE_*`，Windows 下为 `WIN_CSC_*`），macOS/Windows 系统的签名与公证操作将会自动执行。

## 相关文档

- [CLI 指南](./cli.md) — 终端界面使用说明
- [TUI](./tui.md) — 桌面后端所采用的现代化终端用户界面
- [Web 控制面板](./features/web-dashboard.md) — 带有内置聊天功能的浏览器管理面板
- [配置文件](./configuration.md) — 桌面应用读写使用的配置信息
- [Windows（原生版）](./windows-native.md) — Windows 原生安装路径说明
