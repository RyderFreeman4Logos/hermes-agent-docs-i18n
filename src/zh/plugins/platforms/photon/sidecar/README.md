# Photon Sidecar

这是一个小型节点辅助工具，用于连接Hermes Agent与Photon的Spectrum SDK（`spectrum-ts`）。由于Hermes是基于Python开发的，而Photon目前并未提供公开的HTTP消息发送接口，因此回复消息需通过此Sidecar来传递。

该Sidecar的功能包括：

- 运行 `Spectrum({ projectId, projectSecret, providers: [imessage.config()] })`；
- 为Python适配器提供一个仅限环回的HTTP控制通道，用于发送消息发送/输入中状态请求（通过 `X-Hermes-Sidecar-Token` 进行身份验证）；
- 接收传入的消息流，从而确保 `spectrum-ts` 能持续维持重连和心跳机制正常运行，同时让Hermes能够通过适配器的环回 `GET /inbound` 流接收消息。

## 安装方式

```bash
cd plugins/platforms/photon/sidecar
npm install
```

Hermes 插件中的 `hermes photon setup` 命令会在此处自动执行 `npm install` 操作。

## 独立运行

用于调试：

```bash
PHOTON_PROJECT_ID=... PHOTON_PROJECT_SECRET=... \
PHOTON_SIDECAR_PORT=8789 PHOTON_SIDECAR_TOKEN=$(openssl rand -hex 16) \
node index.mjs
```

在正常使用情况下，Python适配器会负责监控该进程——启动它、在进程崩溃时重启、在系统关闭时终止它——而无需用户手动操作。

## 为何需要侧车组件？

Photon的Spectrum发送功能是通过TypeScript SDK中的`Space.send(...)` API来实现的。由于Hermes是基于Python编写的，因此响应消息需要通过这个侧车组件进行传输，直到Photon推出公开的HTTP发送端点为止。

一旦Photon提供了HTTP发送端点，计划便是完全废弃这个侧车组件，直接从Python代码中调用发送功能。该插件的出站通信路径目前已被封装在若干小型辅助函数中（如`adapter.py`中的`_sidecar_send`、`_sidecar_send_richlink`和 `_sidecar_send_attachment`），这样就能实现平滑过渡。
