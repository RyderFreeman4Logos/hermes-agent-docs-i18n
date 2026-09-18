# Photon iMessage 平台插件

该插件通过 [Photon][photon] 将 Hermes Agent 与 iMessage（以及其他 Spectrum 接口）相连。Photon 是一项托管服务，负责处理 iMessage 线路的分配、消息投递以及防滥用机制，因此用户无需自行搭建 Mac 中继服务器。

免费版本使用 Photon 的共享 iMessage 线路池，我们建议所有尚未购买专用号码的用户都采用此方案。

## 架构设计

与 Discord 和 Slack 类似，Photon 也采用**持久连接**机制——无需公开 URL、Webhook 或签名密钥。`spectrum-ts` SDK 会为双向通信维持一个长期有效的 **gRPC 流**。由于该 SDK 仅支持 TypeScript，Hermes 会在一个小型受监控的 Node sidecar 中运行它，并通过回环接口与之通信。

```
                         gRPC (spectrum-ts)
┌─────────────────────────┐ ◄───────────────► ┌──────────────────────┐
│  Photon Spectrum cloud  │   app.messages    │  Node sidecar        │
│  (iMessage line owner)  │   space.send()    │  (plugins/…/sidecar) │
└─────────────────────────┘                   └──────────┬───────────┘
                                       GET /inbound (NDJSON) │  ▲ POST /send
                                       inbound events        ▼  │ /send-richlink
                                                            │  │ /typing
                                              ┌──────────────────────┐
                                              │  PhotonAdapter        │
                                              │  (Python, in gateway) │
                                              └──────────────────────┘
```

- **入站流程**：Sidecar 会读取 SDK 的 `app.messages` gRPC 流，对每条消息进行标准化处理，然后通过回环地址的 `GET /inbound` 接口（以 NDJSON 格式）将其传输给适配器。适配器会根据 `messageId` 进行去重处理，随后向网关发送 `MessageEvent`。如果数据流中断，Sidecar 会自动重新连接；而与 Photon 的 gRPC 重新连接功能则由 Sidecar 负责。
- **出站流程**：`send`、`send_typing` 以及反应反馈功能均通过回环地址向 Sidecar 发送 POST 请求（对应接口为 `/send`、`/send-richlink`、`/send-attachment`、`/typing`、`/react`、`/unreact`），这些请求均会使用共享的 `X-Hermes-Sidecar-Token` 进行身份验证。

## 首次设置指南

```bash
# One-shot setup: device login (opens browser) + project + user + sidecar deps
hermes photon setup --phone +15551234567

# Start the gateway
hermes gateway start
```

`hermes photon setup` 会按以下顺序执行操作：

1. **设备登录**（遵循 RFC 8628 标准，使用 `client_id=photon-cli`）——打开 `https://app.photon.codes/` 进行授权，并保存相应的令牌。
2. 在 Photon 控制面板中**查找或创建** `Hermes Agent` 项目。
3. **配置项目密钥**——生成一个新的项目密钥（控制面板仅显示一次），并将其保存到 `~/.hermes/.env` 文件中，以便 sidecar 能够对 `spectrum-ts` 进行身份验证。由于 Spectrum 服务始终处于运行状态，因此无需单独的启用步骤。
4. 将您的电话号码**注册为 Spectrum 用户**（该操作具有幂等性——如果该号码已存在对应用户，则会跳过此步骤）。
5. **输出指定的 iMessage 线路号码**——即用于向代理发送短信的号码。
6. **安装 sidecar 所需依赖**（执行 `npm ci` 命令，会按原样安装锁定文件中的依赖版本，因此每次设置都会使用与该插件编写时完全一致的 `spectrum-ts` 版本）。

该工具没有独立的 `login` 命令；与其他所有 Hermes 频道一样，初始化流程都通过统一的设置界面完成。重新运行 `setup` 命令会复用现有的令牌/项目，因此可以安全地再次运行以完成未完成的设置。执行 `hermes photon status` 可以查看当前的配置情况。

## 凭证信息

运行时 SDK 的凭证存储在 `~/.hermes/.env` 文件中（该位置与其他所有频道保存令牌的地点相同），适配器会从环境变量中读取这些凭证。

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

> **关于 ID 的说明。** Photon 项目的控制台 ID 与 Spectrum 项目的 ID 是相同的值，以 `PHOTON_PROJECT_ID` 的形式呈现。`auth.json` 文件中的 `dashboard_project_id` 和 `spectrum_project_id` 两个键均存储该 ID。

## 配置参数

所有环境变量均在 `plugin.yaml` 中有详细说明。其中最重要的包括：

| Env var                   | Default                    | Meaning                              |
|---------------------------|----------------------------|--------------------------------------|
| `PHOTON_PROJECT_ID`       | from .env / auth.json      | Spectrum project id (SDK `projectId`)|
| `PHOTON_PROJECT_SECRET`   | from .env / auth.json      | Project secret                       |
| `PHOTON_SIDECAR_PORT`     | 8789                       | Loopback port for the sidecar        |
| `PHOTON_SIDECAR_AUTOSTART`| true                       | Spawn the sidecar on connect         |
| `PHOTON_DASHBOARD_HOST`   | https://app.photon.codes   | Dashboard API host                   |
| `PHOTON_SPECTRUM_HOST`    | https://spectrum.photon.codes | Spectrum API host                 |
| `PHOTON_HOME_CHANNEL`     | your number (set by setup) | Default space for cron delivery — a space id, or a bare E.164 number (resolved to a DM) |
| `PHOTON_ALLOWED_USERS`    | your number (set by setup) | Comma-separated E.164 allowlist      |
| `PHOTON_REQUIRE_MENTION`  | false                      | Gate group chats on a wake word      |
| `PHOTON_MAX_INLINE_ATTACHMENT_BYTES` | 20 MB           | Max inbound attachment size the sidecar reads & inlines |
| `PHOTON_TELEMETRY`        | false                      | Spectrum SDK telemetry — toggle with `hermes photon telemetry on\|off` (restart the gateway to apply) |
| `PHOTON_MARKDOWN`         | true                       | Send agent replies as markdown (iMessage renders natively). `false` strips formatting to plain text |
| `PHOTON_REACTIONS`        | false                      | Tapback 👀/👍/👎 as processing status; tapbacks on bot messages reach the agent as `reaction:added:<emoji>` |

## 附件与限制

- **会下载传入的附件及语音备忘录。** Sidecar组件会读取这些数据字节（通过`content.read()`方法），并将其以Base64格式嵌入到NDJSON事件中；适配器则将这些内容缓存到共享媒体缓存中，并设置`media_urls`/`media_types`字段，从而使智能体能够查看真实的图片或文件，或对语音备忘录进行转录——这一处理方式与BlueBubbles的iMessage通道保持一致。同时包含文本和附件的混合iMessage消息会被整合为分组数据包，从而确保用户输入的文本能与已缓存的媒体内容一同保留。对于大小超过`PHOTON_MAX_INLINE_ATTACHMENT_BYTES`（默认为20 MB）的媒体文件，或是读取过程中出现故障的文件，系统会回退为文本标记（如`[Photon attachment received: …]`或`[Photon voice received: …]`），这样智能体仍能知晓有内容已送达。如果Spectrum发送了`richlink`类型的内容对象，Hermes会保留其URL以及Spectrum预先提供的任何标题/摘要元数据；不过当前版本的Spectrum仍可能以普通文本形式发送常规链接。iMessage还可能在URL之后直接以`.pluginPayloadAttachment`图像格式发送富链接预览图；Hermes会将这些图像合并处理，从而使智能体仅收到一条链接消息，而无需再收到后续的“(附件)”提示。
- **支持发送外部附件。** 图片、语音笔记、视频及文档可通过 `space.send(attachment(...))` / `space.send(voice(...))`，经由侧车组件的 `/send-attachment` 接口进行发送；附文则会以独立的文本气泡形式显示在媒体内容之后。  
- **支持 Markdown 格式渲染。** 回复内容会通过 spectrum-ts 的 `markdown()` 构建器进行处理；iMessage 能够原生渲染加粗、斜体、列表、代码等格式，而其他 Spectrum 平台则仅以可读的纯文本形式显示。仅包含 URL 的回复则通过 spectrum-ts 的 `richlink()` 构建器发送，以便 iMessage 能够展示原生的链接预览卡片。若设置 `PHOTON_MARKDOWN=false`，则回复将恢复为纯文本格式，且无法使用富链接功能。  
- **在 `PHOTON_REACTIONS`（默认值为关闭）启用的前提下，支持反应功能。** 适配器会在处理过程中显示 👀 反应图标，处理完成后再替换为 👍/👎；而用户对机器人发送的消息作出的反应，则会以 `reaction:added:<emoji>` 的形式作为虚拟事件传递给智能体。侧车组件重启后，反应状态将尽力恢复——由于实时反应标识会丢失，因此旧的反应图标会在新的反应出现时自动替换。借助 spectrum-ts 的 `space.get` 功能，群组空间在重启后仍能保持连接状态。
- **支持已读回执功能。** 在将 iMessage 转发至 Hermes 后，sidecar 会立即标记该消息已被读取，因此发送方无需等待模型或工具的处理即可看到“已读”状态。而由 Hermes 发送的消息所对应的已读回执会被视为在线状态监测数据，不会触发任何代理处理流程。如需将消息状态始终保持在“已送达”，可设置 `PHOTON_READ_RECEIPTS=false`。
- **支持原生轮询功能。** Hermes 通过 sidecar 的 `/send-poll` 接口，利用 `spectrum-ts` 的 `poll(...)` 构建器来发送轮询内容。
- **支持消息特效功能。** 可通过 sidecar 的 `/send-effect` 接口，借助 `spectrum-ts` 的 iMessage `effect(...)` 构建器，为文本消息添加原生的 iMessage 气泡或屏幕特效。
- **定时任务/独立发送需要运行中的网关。** 网关之外的进程（如定时任务子进程、`hermes send` 命令）无法直接启动 sidecar；它们需通过路径 `<hermes-home>/runtime/photon-sidecar.json` 中的运行时记录来向正在运行的 sidecar 进行身份验证。该记录会在 sidecar 完成 `/healthz` 就绪检查后生成（时间为 `0600`），并在 sidecar 停止运行或启动失败时被删除。另外需注意，共享版或免费版的 Photon 号码无法与从未给其发送过消息的号码发起对话——这是 Photon 的政策限制，而非 Hermes 的功能局限。

## 升级 spectrum-ts

在 `sidecar/package.json` 中，`spectrum-ts` 被锁定为**精确版本**（而非使用 `^` 表示的版本范围），并通过 `npm ci` 进行安装。这是因为该 SDK 会频繁发布破坏性重大版本更新：v2 版移除了 `defineFusorPlatform` 功能；v3 版重构了空间构建机制；v5 版将其拆分为多个 `@spectrum-ts/*` 包，由 `spectrum-ts` 作为顶层包重新导出这些子包；而 v8 版则使 `richlink` 主要用于外部链接，导致许多原有内部链接现在会以普通 `text` 格式呈现。如果使用浮动版本范围或执行 `npm install spectrum-ts@latest` 的命令，那些具有破坏性的新版本就可能会在用户不知情的情况下破坏现有的项目配置。因此，升级操作是经过慎重考虑后才进行的。

1. 查阅当前锁定版本与目标版本之间的所有版本的[SDK发布说明](https://github.com/photon-hq/spectrum-ts/releases)。  
2. 在`sidecar/package.json`中更新对应的锁定版本，然后在`sidecar/`目录内运行`npm install`以重新生成`package-lock.json`。将这两个文件都提交到版本控制中。  
3. 根据新的类型定义迁移`sidecar/index.mjs`文件。`spectrum-ts`会重新导出`@spectrum-ts/core`（该框架包含Spectrum、内容构建器以及Space/Message相关功能）和`@spectrum-ts/imessage`（对应提供程序），因此权威的类型定义文件应为`sidecar/node_modules/@spectrum-ts/{core,imessage}/dist/*.d.ts`（官方文档可能会存在滞后）。  
4. 重新验证`sidecar/patch-spectrum-mixed-attachments.mjs`文件。该文件会重写`@spectrum-ts/imessage/dist/index.js`中编译好的iMessage入站映射逻辑，确保同时包含文本和附件的消息仍能保留其类型化的文本内容；这些映射的引用始终与特定构建版本的输出相关联。`npm install`会在`postinstall`阶段执行该文件，如果引用不再匹配将会抛出明显错误——此时需将引用更新为新的输出版本（`test_spectrum_patch.py`可用于测试该补丁）。  
5. 运行`pytest tests/plugins/platforms/photon/`命令。  
6. 进行端到端测试：使用`hermes photon status`检查状态，发送私信和群组消息并验证往返流程，以及在网关重启后立即测试智能体对群组的回复功能（该过程会涉及`space.get`功能的重新加载）。  

[photon]: https://photon.codes/
