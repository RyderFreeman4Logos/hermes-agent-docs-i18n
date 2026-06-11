# Photon Sidecar

这是一个小型节点辅助工具，用于连接Hermes Agent与Photon的Spectrum SDK（`spectrum-ts`）。由于Hermes是基于Python开发的，而Photon目前并未提供公开的HTTP消息发送接口，因此回复消息都需要通过此Sidecar来传递。

该Sidecar的功能包括：

- 运行 `Spectrum({ projectId, projectSecret, providers: [imessage.config()] })`；
- 为Python适配器提供一个仅支持环回连接的HTTP控制通道，用于发送消息发送请求和输入状态检测请求（通过 `X-Hermes-Sidecar-Token` 进行身份验证）；
- 接收传入的消息流，从而确保 `spectrum-ts` 能持续保持重连和心跳机制的正常运行（实际的消息传递则是通过Photon带签名的webhook发送到我们的Python aiohttp服务器）。

## 安装方式

```bash
cd plugins/platforms/photon/sidecar
npm install
```

Hermes 插件中的 `hermes photon setup` 命令会在此处自动执行 `npm install` 操作。

## 独立运行模式

用于调试：

```bash
PHOTON_PROJECT_ID=... PHOTON_PROJECT_SECRET=... \
PHOTON_SIDECAR_PORT=8789 PHOTON_SIDECAR_TOKEN=$(openssl rand -hex 16) \
node index.mjs
```

在正常使用情况下，Python适配器会负责监控该进程——启动它、在进程崩溃时重启、在系统关闭时终止它——而无需用户手动操作。

## 为何需要侧车组件？

Photon虽然提供了Webhook接收功能，但其官方文档明确指出：

> 应通过独立的`spectrum-ts` SDK实例调用`Space.send(...)`方法，并传入`space.id`以进行响应。目前暂未提供公开的HTTP发送接口。
> — https://photon.codes/docs/webhooks/events

一旦Photon推出HTTP发送接口，计划便是彻底废弃这个侧车组件，直接从Python层面发起请求。该插件的出站请求逻辑早已被封装在单个辅助函数（即`adapter.py`中的`_sidecar_send`）中，因此实现这一变更仅需修改一个文件即可。
