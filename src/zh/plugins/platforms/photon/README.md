# Photon iMessage 平台插件

该插件通过 [Photon][photon] 将 Hermes Agent 与 iMessage（以及其他 Spectrum 接口）相连。Photon 是一项托管服务，负责处理 iMessage 线路的分配、消息投递以及防滥用机制，因此用户无需自行搭建 Mac 中继服务器。

免费版本使用 Photon 的共享 iMessage 线路池，我们建议所有尚未购买专用号码的用户都选择此方案。

## 架构

与 Discord 和 Slack 类似，Photon 也采用**持久连接**机制——无需公开 URL、Webhook 或签名密钥。`spectrum-ts` SDK 会为双向通信维持一个长期有效的 **gRPC 流**。由于该 SDK 仅支持 TypeScript，Hermes 会在一个小型受监控的 Node sidecar 中运行它，并通过回环接口与之通信。

```
                         gRPC (spectrum-ts)
┌─────────────────────────┐ ◄───────────────► ┌──────────────────────┐
│  Photon Spectrum cloud  │   app.messages    │  Node sidecar        │
│  (iMessage line owner)  │   space.send()    │  (plugins/…/sidecar) │
└─────────────────────────┘                   └──────────┬───────────┘
                                       GET /inbound (NDJSON) │  ▲ POST /send
                                       inbound events        ▼  │ /typing
                                              ┌──────────────────────┐
                                              │  PhotonAdapter        │
                                              │  (Python, in gateway) │
                                              └──────────────────────┘
```

- **入站流程**：Sidecar 会读取 SDK 的 `app.messages` gRPC 流，对每条消息进行标准化处理，然后通过回环地址的 `GET /inbound` 接口（采用 NDJSON 格式）将其传输给适配器。适配器会根据 `messageId` 对消息进行去重处理，随后向网关发送 `MessageEvent`。如果数据流中断，Sidecar 会自动重新连接；而与 Photon 的 gRPC 重新连接功能则由 Sidecar 负责。
- **出站流程**：`send`、`send_typing` 以及反应反馈功能均通过回环 POST 请求发送至 Sidecar（对应接口为 `/send`、`/send-attachment`、`/typing`、`/react`、`/unreact`），这些请求会使用共享的 `X-Hermes-Sidecar-Token` 进行身份验证。

## 首次设置指南

```bash
# One-shot setup: device login (opens browser) + project + user + sidecar deps
hermes photon setup --phone +15551234567

# Start the gateway
hermes gateway start
```

`hermes photon setup` 会按以下顺序执行操作：

1. **设备登录**（遵循 RFC 8628 标准，使用 `client_id=photon-cli`）—— 打开 `https://app.photon.codes/` 进行授权，并存储访问令牌。
2. 在 Photon 控制面板中**查找或创建** `Hermes Agent` 项目。
3. **配置项目密钥**—— 生成一个新的项目密钥（控制面板仅显示一次），并将其保存到 `~/.hermes/.env` 文件中，以便 sidecar 能够对 `spectrum-ts` 进行身份验证。由于 Spectrum 服务始终处于运行状态，因此无需单独的启用步骤。
4. 将您的电话号码**注册为 Spectrum 用户**（该操作具有幂等性——如果该号码已存在对应用户，则会跳过此步骤）。
5. **打印指定的 iMessage 线路号码**—— 即用于向代理发送消息的电话号码。
6. **安装 sidecar 所需依赖**（执行 `npm ci` 命令，会按原样安装锁定文件中的依赖版本，因此每次设置都会使用与该插件编写时完全一致的 `spectrum-ts` 版本）。

该工具没有独立的 `login` 命令；与其他所有 Hermes 频道一样，配置流程都通过统一的设置界面完成。重新运行 `setup` 命令会复用现有的令牌/项目，因此可以安全地再次运行以完成未完成的配置。执行 `hermes photon status` 可以查看当前的配置情况。

## 凭证信息

运行时 SDK 的凭证存储在 `~/.hermes/.env` 文件中（该位置也用于存储其他所有频道的令牌），适配器会从环境变量中读取这些凭证。

```bash
PHOTON_PROJECT_ID=<projectId>   # the SDK's projectId (same as the dashboard project id)
PHOTON_PROJECT_SECRET=<projectSecret>
```

管理元数据存储在 `~/.hermes/auth.json` 文件的 `credential_pool` 目录下：

```jsonc
{
  "credential_pool": {
    "photon": [
      { "access_token": "<device-bearer>", "issued_at": ... }
    ],
    "photon_project": [
      {
        "dashboard_project_id": "<project id>",
        "spectrum_project_id": "<project id>",
        "project_secret": "<projectSecret>",
        "name": "Hermes Agent"
      }
    ]
  }
}
```

> **关于 ID 的说明。** Photon 项目的控制台 ID 与 Spectrum 项目的 ID 是同一个值，以 `PHOTON_PROJECT_ID` 的形式暴露。`auth.json` 文件中的 `dashboard_project_id` 和 `spectrum_project_id` 两个键都存储该 ID。

## 配置参数

所有环境变量均在 `plugin.yaml` 中有详细说明。其中最重要的参数如下：

| 环境变量                   | 默认值                    | 含义                              |
|---------------------------|----------------------------|--------------------------------------|
| `PHOTON_PROJECT_ID`       | 来自 .env / auth.json      | Spectrum 项目 ID（SDK 中的 `projectId`）|
| `PHOTON_PROJECT_SECRET`   | 来自 .env / auth.json      | 项目密钥                           |
| `PHOTON_SIDECAR_PORT`     | 8789                       | Sidecar 的回环端口                 |
| `PHOTON_SIDECAR_AUTOSTART`| true                       | 连接时自动启动 Sidecar             |
| `PHOTON_DASHBOARD_HOST`   | https://app.photon.codes   | 控制台 API 主机地址                 |
| `PHOTON_SPECTRUM_HOST`    | https://spectrum.photon.codes | Spectrum API 主机地址               |
| `PHOTON_HOME_CHANNEL`     | 您的号码（由设置确定）   | 用于定时消息发送的默认空间——可以是空间 ID，也可以是纯 E.164 号码（会解析为私信号码） |
| `PHOTON_ALLOWED_USERS`    | 您的号码（由设置确定）   | 用逗号分隔的允许接收消息的 E.164 号码列表 |
| `PHOTON_REQUIRE_MENTION`  | false                      | 是否通过唤醒词来控制群聊                 |
| `PHOTON_MAX_INLINE_ATTACHMENT_BYTES` | 20 MB           | Sidecar 可读取并内嵌的最大接收附件大小 |
| `PHOTON_TELEMETRY`        | false                      | Spectrum SDK 的遥测功能——可通过 `hermes photon telemetry on\|off` 打开/关闭（需重启网关才能生效） |
| `PHOTON_MARKDOWN`         | true                       | 以 Markdown 格式发送智能体回复（iMessage 可直接渲染）。设置为 `false` 时则去掉格式，仅显示纯文本 |
| `PHOTON_REACTIONS`        | false                      | 以 👀/👍/👎 形式的反馈作为处理状态；机器人发送的消息所触发的反馈会以 `reaction:added:<emoji>` 的形式传递给智能体 |

## 附件与限制

- **接收的附件和语音笔记会被下载。** Sidecar 会读取这些数据的字节内容（通过 `content.read()`），并将其以 Base64 格式内嵌到 NDJSON 事件中；适配器会将它们缓存到共享媒体缓存中，并设置 `media_urls`/`media_types`，这样智能体就能看到真实的图片或文件，或对语音笔记进行转录——这与 BlueBubbles iMessage 频道的功能一致。同时包含文本和附件的混合 iMessage 消息会被整理为分组数据，从而在保留用户输入文本的同时保存缓存的媒体内容。如果附件大小超过 `PHOTON_MAX_INLINE_ATTACHMENT_BYTES` 的默认值 20 MB，或读取过程中出现错误，系统会回退到文本标记形式（如 `[Photon attachment received: …]` 或 `[Photon voice received: …]`），这样智能体仍能知道有新内容到达。
- **支持发送附件。** 图片、语音笔记、视频和文档可通过 `space.send(attachment(...))`/`space.send(voice(...))`，经由 Sidecar 的 `/send-attachment` 接口发送；附带的说明文字会作为单独的文本气泡出现在媒体内容之后。
- **Markdown 格式可被渲染。** 智能体的回复会通过 spectrum-ts 的 `markdown()` 构建器处理；iMessage 能直接渲染加粗、斜体、列表和代码格式，而其他 Spectrum 平台则仅能显示可读的纯文本。若将 `PHOTON_MARKDOWN` 设置为 `false`，则会恢复为无格式的纯文本。
- 在 `PHOTON_REACTIONS`（默认为关闭）的支持下，系统也支持反馈功能：适配器在处理消息时会发送 👀 反馈，处理完成后会替换为 👍/👎；用户对机器人发送的消息做出的反馈则会以 `reaction:added:<emoji>` 的形式传递给智能体。Sidecar 重启后，这些反馈的清除是尽力而为的——因为实时的反馈标识会丢失，所以旧的反馈会在新的反馈出现时被替代。通过 spectrum-ts v3 的 `space.get(id)` 功能，群组空间在重启后仍可保持连通性。
- **消息特效和投票功能**——虽然已被 `spectrum-ts` 支持，但目前尚未开放；这些功能未来可添加到 Sidecar 中。

## 升级 spectrum-ts

`spectrum-ts` 在 `sidecar/package.json` 中被锁定为**特定版本**（没有使用 `^` 范围），并通过 `npm ci` 安装，因为该 SDK 会发布具有破坏性变更的 major 版本（v2 版移除了 `defineFusorPlatform` 功能；v3 版则重新设计了空间结构）。如果使用浮动版本范围或 `npm install spectrum-ts@latest` 的方式，可能会在不知不觉中让新版本带来破坏性变更，影响现有设置。升级流程如下：

1. 查阅当前锁定版本与目标版本之间的每一个版本的 [SDK 发布说明](https://github.com/photon-hq/spectrum-ts/releases)。
2. 在 `sidecar/package.json` 中更新对应的锁定版本，然后在 `sidecar/` 目录下运行 `npm install` 以重新生成 `package-lock.json`。将这两项更改都提交到版本控制中。
3. 根据新的类型定义修改 `sidecar/index.mjs` 文件（真正的类型定义来自 `sidecar/node_modules/spectrum-ts/dist/*.d.ts` 文件——官方文档的更新可能会滞后）。
4. 运行 `pytest tests/plugins/platforms/photon/` 进行测试。
5. 进行端到端验证：查看 `hermes photon status` 的状态，发送私信和群聊消息并往返测试，以及在网关重启后立即向群组发送智能体回复（以此测试 `space.get` 功能的恢复情况）。

[photon]: https://photon.codes/
