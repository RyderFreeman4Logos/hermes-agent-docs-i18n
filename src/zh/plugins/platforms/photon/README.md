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

`hermes photon setup` 会按以下步骤执行操作：

1. **设备登录**（遵循 RFC 8628 标准，使用 `client_id=photon-cli`）——打开 `https://app.photon.codes/` 进行授权，并保存访问令牌。
2. 在 Photon 控制面板中**查找或创建** `Hermes Agent` 项目。
3. **启用 Spectrum 功能**，读取该项目的 `spectrumProjectId`，更新项目密钥，并将两者均持久化存储。
4. 将您的电话号码**注册为 Spectrum 用户**（该操作具有幂等性——若该号码已存在对应用户，则直接跳过）。
5. **打印指定的 iMessage 线路号码**——即用于向代理发送消息的号码。
6. **安装侧车依赖项**（通过 `npm ci` 操作，会完全按照版本锁定文件中的内容进行安装，因此每次设置都会使用与该插件编写时完全一致的 `spectrum-ts` 版本）。

该工具没有独立的 `login` 命令；与其他所有 Hermes 通道一样，配置流程都通过统一的设置界面完成。重新运行 `setup` 命令会复用现有的令牌/项目，因此可安全地再次运行以完成未完成的配置。可通过运行 `hermes photon status` 查看当前已配置的内容。

## 凭证信息

运行时 SDK 的凭证存储在 `~/.hermes/.env` 文件中（该位置与其他所有通道的令牌存储位置相同），适配器会从环境变量中读取这些凭证。

```bash
PHOTON_PROJECT_ID=<spectrumProjectId>   # the SDK's projectId
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
        "dashboard_project_id": "<dashboard id>",
        "spectrum_project_id": "<spectrumProjectId>",
        "project_secret": "<projectSecret>",
        "name": "Hermes Agent"
      }
    ]
  }
}
```

> **关于标识符的说明。** 一个 Photon 项目包含两个标识符：用于管理 API 调用的控制台 `id`，以及 SDK 进行身份验证所使用的 `spectrumProjectId`。`PHOTON_PROJECT_ID` 即为 **Spectrum** 标识符。

## 配置参数

所有环境变量均在 `plugin.yaml` 中有详细说明。其中最重要的参数如下：

| 环境变量                     | 默认值                  | 含义                                   |
|------------------------------|-------------------------|----------------------------------------|
| `PHOTON_PROJECT_ID`         | 来自 .env / auth.json     | Spectrum 项目标识符（即 SDK 的 `projectId`）|
| `PHOTON_PROJECT_SECRET`      | 来自 .env / auth.json     | 项目密钥                               |
| `PHOTON_SIDECAR_PORT`        | 8789                     | Sidecar 的回环端口                     |
| `PHOTON_SIDECAR_AUTOSTART`   | true                    | 连接时自动启动 Sidecar                 |
| `PHOTON_DASHBOARD_HOST`       | https://app.photon.codes   | 控制台 API 所在主机地址                 |
| `PHOTON_SPECTRUM_HOST`       | https://spectrum.photon.codes | Spectrum API 所在主机地址               |
| `PHOTON_HOME_CHANNEL`        | 您的号码（由设置确定）  | 用于定时消息发送的默认空间——可以是空间 ID，也可以是纯 E.164 号码（会解析为私信号码） |
| `PHOTON_ALLOWED_USERS`      | 您的号码（由设置确定）  | 以逗号分隔的允许接收消息的 E.164 号码列表 |
| `PHOTON_REQUIRE_MENTION`    | false                   | 是否需要通过唤醒词才能进入群组聊天       |
| `PHOTON_MAX_INLINE_ATTACHMENT_BYTES` | 20 MB                 | Sidecar 能读取并内嵌的最大接收附件大小     |
| `PHOTON_TELEMETRY`          | false                   | Spectrum SDK 的遥测功能——可通过 `hermes photon telemetry on\|off` 开启/关闭（需重启网关才能生效） |
| `PHOTON_MARKDOWN`           | true                    | 以 Markdown 格式发送智能体回复（iMessage 可直接渲染）。设置为 `false` 时将去掉格式，仅显示纯文本 |
| `PHOTON_REACTIONS`          | false                   | 以👀/👍/👎等表情作为处理状态反馈；机器人发送的消息对应的反馈会以 `reaction:added:<emoji>` 的形式传递给智能体 |

## 附件与限制

- **接收的附件和语音备忘录会被下载。** Sidecar 会读取这些数据的字节内容（通过 `content.read()`），并将其以 Base64 格式内嵌到 NDJSON 事件中；适配器会将它们缓存到共享媒体缓存中，并设置 `media_urls`/`media_types`，这样智能体就能查看真实的图片或文件，或对语音备忘录进行转录——这与 BlueBubbles iMessage 频道的功能一致。对于大于 `PHOTON_MAX_INLINE_ATTACHMENT_BYTES`（默认为 20 MB）的媒体文件，或是读取失败的文件，系统会回退到文本标记形式（如 `[Photon attachment received: …]` 或 `[Photon voice received: …]`），这样智能体仍能知道有内容已送达。
- **支持发送附件。** 图片、语音备忘录、视频和文档可通过 `space.send(attachment(...))`/`space.send(voice(...))` 方法，经由 Sidecar 的 `/send-attachment` 接口发送；标题信息则会作为单独的文本气泡显示在媒体内容之后。
- **Markdown 格式可被渲染。** 智能体的回复会通过 spectrum-ts 的 `markdown()` 构建器处理；iMessage 能直接渲染加粗、斜体、列表和代码格式，而其他 Spectrum 平台则仅能显示可读的纯文本。若将 `PHOTON_MARKDOWN` 设置为 `false`，则回复将恢复为无格式的纯文本。
- 在 `PHOTON_REACTIONS`（默认为关闭）的支持下，系统也支持**反馈表情**：适配器在处理消息时会显示👀表情，处理完成后会替换为👍/👎表情；用户对机器人发送的消息发出的反馈表情，则会以 `reaction:added:<emoji>` 的形式传递给智能体。Sidecar 重启后，这些反馈表情的清除是尽力而为的——由于实时反馈标识会被丢失，因此旧的反馈表情会在新的反馈出现时被替换。借助 spectrum-ts v3 的 `space.get(id)` 函数，群组空间在重启后仍可保持连接。
- **消息特效和投票功能**——虽然 `spectrum-ts` 已支持，但目前尚未开放；将这些功能添加进去的合适位置就在 Sidecar 中。

## 升级 spectrum-ts

`spectrum-ts` 在 `sidecar/package.json` 中被锁定为**精确版本**（没有使用 `^` 范围），并通过 `npm ci` 命令安装，这是因为 SDK 会发布具有破坏性变更的 major 版本（v2 版移除了 `defineFusorPlatform` 函数；v3 版则重新设计了空间结构）。如果使用浮动版本范围或 `npm install spectrum-ts@latest` 的方式，可能会让带有破坏性变更的新版本在用户不知情的情况下破坏已有的配置。升级过程需谨慎操作：

1. 查阅当前锁定版本与目标版本之间的每一个版本的[SDK 发布说明](https://github.com/photon-hq/spectrum-ts/releases)，了解其中的变化。
2. 在 `sidecar/package.json` 中修改为对应的精确版本，然后在 `sidecar/` 目录下运行 `npm install` 命令以重新生成 `package-lock.json` 文件。将这两个文件都提交到版本控制中。
3. 根据新的类型定义修改 `sidecar/index.mjs` 文件（真实类型定义位于 `sidecar/node_modules/spectrum-ts/dist/*.d.ts` 文件中——官方文档的更新可能会滞后）。
4. 运行 `pytest tests/plugins/platforms/photon/` 命令进行测试。
5. 进行端到端验证：使用 `hermes photon status` 检查状态，发送私信和群组消息并测试往返流程，以及在网关重启后立即向群组发送智能体回复（以此测试 `space.get` 功能的恢复情况）。

[photon]: https://photon.codes/
