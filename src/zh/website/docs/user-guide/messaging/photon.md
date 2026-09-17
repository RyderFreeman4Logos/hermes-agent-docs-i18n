---
sidebar_position: 18
---

# Photon iMessage

通过 [Photon][photon] 将 Hermes 连接到 **iMessage**。Photon 是一项托管服务，负责处理苹果端的线路分配及防滥用机制，因此您无需自行搭建 Mac 中继服务器。

免费套餐使用 Photon 的共享 iMessage 线路池——不同接收方可能会看到不同的发送号码，但每段对话的稳定性都能得到保障。付费的商务套餐则为每位用户提供专属号码；该插件同时支持这两种模式，建议新手从免费套餐开始使用。

:::info 免费启动
Photon 的共享线路池是免费的。使用 Hermes 发送第一条 iMessage 无需订阅——只需提供一个可绑定到您账户的电话号码即可。
:::

## 架构设计

Photon 采用类似 Discord 或 Slack 的**持久连接**通道——**无需处理 webhook、公开 URL，也无需管理签名密钥**。

`spectrum-ts` SDK 会为双向通信维持一个长期运行的 **gRPC 流**。由于该 SDK 仅支持 TypeScript，Hermes 会在一个小型受监控的 **Node sidecar** 中运行它，并通过回环接口与之通信：

- **接收消息**——sidecar 读取 SDK 的 `app.messages` gRPC 流，通过回环接口的 `GET /inbound`（NDJSON 格式）将每条消息转发给 Python 适配器。该适配器会对消息进行去重处理，然后将其派发给对应智能体；如果连接中断，它会自动重新建立连接。
- **发送消息**——回复信息会以回环 POST 的形式发送到 sidecar，sidecar 再通过 SDK 调用 `space.send(...)` 方法发送消息。

Python 插件负责自动启动、监控并关闭该 sidecar。

## 先决条件

- 一个 Photon 账户——请在 [app.photon.codes][app] 进行注册  
- PATH 环境变量中已安装 **Node.js 18.17 或更高版本**（可通过 `node --version` 查看）  
- 一个可接收 iMessage 的电话号码（用于绑定账户）  

仅此而已——无需配置任何公共网址或隧道。  

## 首次设置  

运行统一网关向导，然后选择 **Photon iMessage** 即可：

```bash
hermes gateway setup
```

……或者直接运行 Photon 设置流程（向导会调用相同的操作步骤）：

```bash
# Device-code login + project + user + sidecar deps, all in one
hermes photon setup --phone +15551234567
```

设置步骤如下：

1. **设备登录**（`client_id=photon-cli`）——会打开
   `https://app.photon.codes/` 以进行授权，并存储承载令牌。
2. 在您的账户中**查找或创建** `Hermes Agent` 项目。
3. **启用 Spectrum 功能**，读取该项目的 Spectrum ID，并更换项目密钥。
4. 将您的电话号码**注册为 Spectrum 用户**——如果该号码已存在对应用户，则此步骤会被跳过，因此重复运行是安全的。
5. **打印分配给您的 iMessage 线路号码**——即用于发送消息联系代理的号码。
6. 在插件的 sidecar 目录中执行 `npm install`。在只读/不可修改的安装环境中（如托管的 Docker 镜像、Podman、Nix），sidecar 会自动回退到 `~/.hermes/photon/sidecar` 下的可写镜像；如需指定具体路径，可设置 `PHOTON_SIDECAR_DIR`。

运行时的凭证会被保存在 `~/.hermes/.env` 文件中（`PHOTON_PROJECT_ID` 为 Spectrum 项目 ID，`PHOTON_PROJECT_SECRET` 为项目密钥），其他所有通道的令牌也存储在此处。管理相关元数据（设备令牌、控制面板项目 ID）则保存在 `~/.hermes/auth.json` 文件的 `credential_pool.photon` / `credential_pool.photon_project` 子目录中。

## 用户授权

Photon 采用与其它 Hermes 通道相同的授权机制。您可以选择以下其中一种方式：

**直接消息配对（默认方式）。** 当有未知号码向您的 Photon 线路发送消息时，Hermes 会回复一个配对码。您只需通过相应操作批准该配对即可：

```bash
hermes pairing approve photon <CODE>
```

使用 `hermes pairing list` 命令即可查看待发送的验证码以及已通过验证的用户列表。

**在 `~/.hermes/.env` 文件中预授权特定号码**：

```bash
PHOTON_ALLOWED_USERS=+15551234567,+15559876543
```

**开放访问**（仅开发人员使用，位于 `~/.hermes/.env` 中）：

```bash
PHOTON_ALLOW_ALL_USERS=true
```

当设置了 `PHOTON_ALLOWED_USERS` 时，系统会默默忽略未知发件人的消息，而不会向其提供配对码（此白名单机制表明您有意限制访问权限）。

### 要求在群聊中@用户才能发送消息

默认情况下，Hermes 会对所有经过授权的私信和群消息作出响应。若希望群聊消息需经过用户确认才能发送，请启用@用户验证功能（私信则仍可正常发送）：

```yaml
gateway:
  platforms:
    photon:
      enabled: true
      require_mention: true
```

当设置 `require_mention: true` 时，群聊消息将会被忽略，除非它们符合特定的唤醒词模式。默认情况下，该模式匹配 “Hermes” 和 “@Hermes agent” 这两种形式。若需使用自定义的智能体名称，则需自行设定正则表达式模式。

```yaml
gateway:
  platforms:
    photon:
      require_mention: true
      mention_patterns:
        - '(?<![\w@])@?amos\b[,:\-]?'
```

这两个密钥同样支持环境变量（`PHOTON_REQUIRE_MENTION`、`PHOTON_MENTION_PATTERNS`）。其所采用的提及过滤机制与 BlueBubbles iMessage 频道所使用的完全相同。

## 启动网关

```bash
hermes gateway start
```

您将会看到类似如下的内容：

```
[photon] connected — sidecar on 127.0.0.1:8789, streaming inbound over gRPC
```

向您分配的号码发送 iMessage，Hermes 即会予以回复。

## 状态查询与故障排除

```bash
hermes photon status
```

它会打印已保存的凭证、Sidecar运行状态、您的注册号码，以及Hermes所使用的iMessage号码。当具备Photon令牌和控制面板项目时，`status`功能会直接从控制面板中补充缺失的号码信息，而无需再申请新的号码线路。

```
Photon iMessage status
──────────────────────
  device token        : ✓ stored
  dashboard project   : 3c90c3cc-0d44-4b50-...
  spectrum project id : sp-...
  project secret      : ✓ stored
  my number           : +15551234567
  assigned number     : +16282679185
  node binary         : /usr/bin/node
  sidecar deps        : ✓ installed
```

常见问题：

- **`sidecar deps : ✗ run hermes photon install-sidecar`** — 虽已安装 Node，但未安装 `spectrum-ts`。请运行建议的命令。
- **`device token : ✗ missing`** — 请运行 `hermes photon setup` 进行登录。
- **`No iMessage line assigned yet`** — 已启用 Spectrum 功能，但尚未配置任何号码；请重新运行 `hermes photon setup` 或查看 [控制面板][应用]。
- **Sidecar 无法启动** — 请确认 `node --version` 的版本为 18.17 及以上，并且 `hermes photon install-sidecar` 的执行过程没有出现错误。

## 当前的限制

- **传入的附件仅包含元数据。** 传入的事件会携带文件名和 MIME 类型；代理能够识别这些信息，但暂无法读取实际内容。SDK 通过 `content.read()` 方法提供附件字节，因此这属于 Sidecar 需要处理的后续问题。
- **支持传出的附件。** Hermes 可以通过 Sidecar 的 `/send-attachment` 接口，借助 spectrum-ts 的 `attachment()` / `voice()` 内容构建器来发送图片、语音备忘录、视频和文档。字幕会作为单独的 iMessage 气泡显示在媒体内容之后。
- **支持原生轮询功能。** Hermes 可以通过 Sidecar 的 `/send-poll` 接口，借助 spectrum-ts 的 `poll()` 构建器来发送轮询内容。
- **支持已读回执功能。** 在将 iMessage 转发至 Hermes 后，Sidecar 会标记该消息已被读取，这样发送方无需等待模型或工具的处理即可立即看到“已读”状态。而由 Hermes 发送的消息所产生的已读回执仅会被用作在线状态监控数据，不会触发任何代理处理流程。如需将消息状态始终保持在“已送达”状态，请设置 `PHOTON_READ_RECEIPTS=false`。

- **支持消息特效功能。** Hermes 可通过 Sidecar 的 `/send-effect` 接口，利用 spectrum-ts 提供的 iMessage `effect()` 构建工具，为文本消息添加原生 iMessage 气泡或屏幕特效。

- **Photon 的免费使用额度：** 每台服务器每天可发送 5,000 条消息，每条共享线路每天可发起 50 次新对话。如需提升额度，请发送邮件至 `help@photon.codes`。

- **定时任务及独立发送功能需要 Gateway 正在运行。** 远程发送工具（如定时任务、`hermes send` 命令以及控制面板）会复用 Gateway 启动的 Sidecar——它们从 `<hermes-home>/runtime/photon-sidecar.json` 文件中读取 Sidecar 的端口和令牌信息，该文件会在 Sidecar 通过健康检查后生成，且在其停止运行时会被删除。如果独立发送功能提示 Gateway 已关闭，请先启动（或重启）Gateway。
- **共享号码/免费套餐号码无法主动与新目标发起对话。** 这是Photon端的策略限制：只有当某个号码先向共享号码发送消息后，该共享号码才能向其回复。即便Hermes配置正确，尝试向完全陌生的接收者发送定时消息或独立消息也会被Photon拒绝——请让接收者先向该号码发送一条消息，或更换为专用号码。

## 环境变量

| 变量名                  | 默认值            | 备注                                      |
|---------------------------|--------------------|--------------------------------------------|
| `PHOTON_PROJECT_ID`       | 从 `.env` 文件读取  | Spectrum 项目标识（即 SDK 中的 `projectId`）；由设置程序自动配置 |
| `PHOTON_PROJECT_SECRET`   | 从 `.env` 文件读取  | 项目密钥；由设置程序自动配置               |
| `PHOTON_SIDECAR_PORT`     | `8789`             | 侧车控制模块及接收通道的环回端口         |
| `PHOTON_SIDECAR_AUTOSTART`| `true`             | 是否自动启动侧车控制模块                   |
| `PHOTON_NODE_BIN`         | `which node`       | 可用于覆盖 Node 运行程序的路径               |
| `PHOTON_HOME_CHANNEL`     | 未设置              | 用于定时任务及通知的默认频道编号           |
| `PHOTON_HOME_CHANNEL_NAME`| 未设置              | 该默认频道的显示名称                     |
| `PHOTON_ALLOWED_USERS`    | 未设置              | 以逗号分隔的 E.164 格式允许列表             |
| `PHOTON_ALLOW_ALL_USERS`  | `false`            | 仅限开发环境使用——允许接收所有发送方的消息   |
| `PHOTON_REQUIRE_MENTION`  | `false`            | 在群组中回复消息前是否需要指定唤醒词       |
| `PHOTON_MENTION_PATTERNS` | Hermes 唤醒词      | 用于群组消息识别的 JSON 列表、逗号分隔值或正则表达式模式 |
| `PHOTON_DASHBOARD_HOST`   | `app.photon.codes` | 可用于覆盖控制面板及设备登录页面的地址     |
| `PHOTON_SPECTRUM_HOST`    | `spectrum.photon.codes` | 可用于覆盖 Spectrum API 的服务器地址         |
[photon]：https://photon.codes/  
[app]：https://app.photon.codes/
