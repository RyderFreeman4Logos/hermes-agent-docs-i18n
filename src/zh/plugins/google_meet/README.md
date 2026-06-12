# google_meet 插件

该插件能够让 Hermes Agent 参与 Google Meet 通话、对其进行转录，可选地通过语音参与对话，并在通话结束后处理后续工作。

## 已发布版本

| 版本 | 功能 | 状态 |
|---|---|---|
| v1 | 仅支持转录：使用 Playwright 进入会议并抓取字幕生成转录文件 | ✓ 默认已内置 |
| v2 | 实时双向音频：通过 OpenAI Realtime 以及 BlackHole/PulseAudio null-sink 实现机器人在通话中的语音输出 | ✓ 需通过 `mode='realtime'` 参数启用 |
| v3 | 远程节点托管：在不同于网关的机器上运行机器人 | ✓ 需通过 `node='<名称>'` 参数启用 |

## 架构设计

```
┌─ gateway (Linux box, where hermes runs) ────────────────────────────┐
│                                                                      │
│   agent → meet_join(url, mode='realtime', node='my-mac')             │
│         │                                                            │
│         └─ NodeClient ─── ws ────┐                                   │
│                                  │                                   │
└──────────────────────────────────┼───────────────────────────────────┘
                                   │ wss (token auth)
                                   ▼
┌─ node host (user's Mac, signed-in Chrome lives here) ───────────────┐
│                                                                      │
│   NodeServer (from `hermes meet node run`)                           │
│     │                                                                │
│     ├─ start_bot → process_manager.start() → spawns meet_bot         │
│     │                                                                │
│     └─ meet_bot (Playwright)                                         │
│        ├─ Chromium → meet.google.com                                 │
│        ├─ caption scraper → transcript.txt                           │
│        └─ (realtime mode only) RealtimeSpeaker thread                │
│             ↓                                                        │
│           OpenAI Realtime WS → speaker.pcm                           │
│             ↓                                                        │
│           paplay → null-sink ← Chrome fake mic                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**在未使用 v3 版本时：** 右侧的所有功能均在网关机上运行。  
**在未使用 v2 版本时：** 会跳过“实时”处理路径，仅执行转录功能。

## 文件列表

| 路径 | 用途 |
|---|---|
| `plugin.yaml` | 配置清单 |
| `__init__.py` | `register(ctx)` —— 注册 5 个工具 + `on_session_end` 回调函数 + `hermes meet` 命令行工具 |
| `meet_bot.py` | Playwright 机器人子进程（独立运行，通过 `python -m plugins.google_meet.meet_bot` 启动） |
| `process_manager.py` | 本地机器人的生命周期管理 + `enqueue_say` 功能 |
| `tools.py` | 面向代理的工具接口 + 节点路由辅助函数 |
| `cli.py` | 提供 `hermes meet setup / auth / join / status / transcript / say / stop / node ...` 等命令 |
| `audio_bridge.py` | v2 版本：Linux 系统使用 PulseAudio 空虚声源，macOS 系统使用 BlackHole 探针 |
| `realtime/openai_client.py` | v2 版本：实现 `RealtimeSession` 与 `RealtimeSpeaker` 功能（文件队列 → OpenAI 实时 WebSocket → PCM） |
| `node/protocol.py` | v3 版本：消息封装结构及验证逻辑 |
| `node/registry.py` | v3 版本：配置文件位于 `$HERMES_HOME/workspace/meetings/nodes.json` |
| `node/server.py` | v3 版本：`NodeServer`（在主机上运行） |
| `node/client.py` | v3 版本：`NodeClient`（由网关上的工具处理程序及命令行工具使用） |
| `node/cli.py` | v3 版本：提供 `hermes meet node {run,list,approve,remove,status,ping}` 等命令 |
| `SKILL.md` | 代理使用指南 |

## 本地快速入门指南

```bash
hermes plugins enable google_meet
hermes meet install                                      # pip + Chromium
hermes meet setup                                        # preflight
hermes meet auth                                         # optional
hermes meet join https://meet.google.com/abc-defg-hij    # transcribe
```

## 实时模式

Linux（推荐，自动化程度最高）：
```bash
hermes meet install --realtime                     # installs pulseaudio-utils
echo 'OPENAI_API_KEY=sk-...' >> ~/.hermes/.env
hermes meet join https://meet.google.com/abc-defg-hij --mode realtime
# then from the agent or CLI:
hermes meet say "Good morning everyone, I'm the note-taker bot."
```

macOS系统：
```bash
hermes meet install --realtime     # runs: brew install blackhole-2ch ffmpeg
# then — manually! — open System Settings → Sound → Input → BlackHole 2ch
echo 'OPENAI_API_KEY=sk-...' >> ~/.hermes/.env
hermes meet join https://meet.google.com/abc-defg-hij --mode realtime
```

在 macOS 系统上，Hermes **不会**自动切换系统的音频输入源——必须由用户手动操作。这是有意为之：随意切换默认输入源可能会带来意想不到的副作用。

## 远程节点主机

在节点机器上（例如已登录 Chrome 的用户 Mac）：
```bash
pip install playwright websockets
python -m playwright install chromium
hermes plugins enable google_meet
hermes meet node run --display-name my-mac --host 0.0.0.0 --port 18789
# prints the bearer token on first run; copy it
```

在网关上：
```bash
hermes meet node approve my-mac ws://<mac-ip>:18789 <token>
hermes meet node ping my-mac
# now any meet_* tool call accepts node='my-mac' (or 'auto')
```

## 安全性

- URL 筛选规则：仅允许 `https://meet.google.com/abc-defg-hij`、`/new` 以及 `/lookup/<id>` 这类地址。
- 不会扫描日历、不会自动拨号，也不会自动发送同意通知。
- 节点服务器采用承载令牌进行身份验证；不内置密钥交换功能，也不支持 TLS 终止处理——建议在局域网内或受信任的反向代理后运行该服务器。
- 每对（网关，节点）组合仅能同时进行一场会议。若再次调用 `meet_join`，则会中断当前的会议。
- 除非当前会议是以 `mode='realtime'` 的方式启动的，否则 `meet_say` 功能将被拒绝使用。

## 不支持的功能

- **日历扫描**——有意未实现该功能，因此必须明确提供会议接入地址。
- **多租户节点共享**——每个节点一次仅能服务于一个网关。
- **Windows 系统**——尚未测试音频桥接功能，且在 Windows 上调用 `register()` 函数将无任何作用。
- **macOS 系统的系统音频输入切换**——此操作由用户自行负责，而非机器人。
