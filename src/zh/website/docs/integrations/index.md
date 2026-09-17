---
title: "Integrations"
sidebar_label: "Overview"
sidebar_position: 0
---

# 集成功能

Hermes Agent 可连接外部系统，用于 AI 推理、工具服务器调用、IDE 工作流集成以及程序化访问等场景。这些集成扩展了 Hermes 的功能范围及运行场景。

:::提示 从这里开始
如果您只能设置一个集成，建议先配置 [Nous Portal](/integrations/nous-portal)——通过一次 OAuth 登录即可使用 300 多种模型，以及四种工具网关功能（网页搜索、图像生成、文本转语音和浏览器自动化）。
:::

## AI 提供商与路由机制

Hermes 开箱即支持多种 AI 推理提供商。您可以通过 `hermes model` 命令进行交互式配置，也可直接在 `config.yaml` 文件中设置。

- **[AI 提供商](/integrations/providers)** — 支持 OpenRouter、Anthropic、OpenAI、Google 以及所有兼容 OpenAI 的接口。Hermes 能自动识别各提供商的视觉处理、流式处理和工具调用等功能。
- **[提供商路由](/user-guide/features/provider-routing)** — 可精细控制由哪些底层提供商处理您的 OpenRouter 请求。您可以通过排序、白名单、黑名单以及明确的优先级设置，优化成本、速度或服务质量。
- **[备用提供商](/user-guide/features/fallback-providers)** — 当主模型出现故障时，系统会自动切换到备用的 LLM 提供商。该功能既包括主模型的备用方案，也包括针对视觉处理、数据压缩和网页提取等独立任务的备用方案。

## 工具服务器（MCP）

- **[MCP 服务器](/user-guide/features/mcp)** — 通过模型上下文协议将 Hermes 与外部工具服务器连接起来。无需编写原生 Hermes 工具，即可使用来自 GitHub、数据库、文件系统、浏览器环境、内部 API 等来源的工具。该功能支持标准输入输出与流式传输两种模式，具备按服务器筛选工具的能力，同时还支持基于能力的资源/提示词注册机制。

## 网页搜索后端

`web_search` 和 `web_extract` 工具支持八种后端提供商，可通过 `config.yaml` 或 `hermes tools` 进行配置：

| 后端提供商 | 环境变量 | 搜索功能 | 提取功能 | 爬取功能 |
|-----------|----------|----------|----------|----------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **SearXNG** | `SEARXNG_URL` | ✔ | — | — |
| **Brave**（免费版） | `BRAVE_SEARCH_API_KEY` | ✔ | — | — |
| **DuckDuckGo**（ddgs） | _（无）_ | ✔ | — | — |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **xAI** | `XAI_API_KEY` | ✔ | — | — |

快速设置示例：

```yaml
web:
  backend: firecrawl    # firecrawl | searxng | brave-free | ddgs | tavily | perplexity | keenable | exa | parallel | xai
```

如果未设置 `web.backend`，系统会自动从可用的 API 密钥中检测合适的后端。此外，通过 `FIRECRAWL_API_URL` 也可支持自托管的 Firecrawl。

## 浏览器自动化

Hermes 提供完整的浏览器自动化功能，支持多种后端选项，可用于浏览网站、填写表单以及提取信息：

- **Browser Use Cloud** — 提供托管式 Chromium 浏览器，具备隐身模式、住宅代理、验证码破解功能以及可重复使用的浏览器配置文件。
- **Browserbase** — 另一种云浏览器服务提供商，提供托管浏览器、反爬工具、验证码破解功能以及住宅代理。
- **本地 Chromium 系列 CDP** — 通过 `/browser connect` 命令连接正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器。
- **本地 Chromium** — 通过 `agent-browser` CLI 使用的无头本地浏览器。

有关设置与使用方法，请参阅 [浏览器自动化](/user-guide/features/browser) 文档。

## 语音与文本转语音服务提供商

支持在所有消息平台上进行文本转语音及语音转文本处理：

| 服务提供商 | 音质 | 费用 | API 密钥 |
|----------|------|------|---------|
| **Edge TTS**（默认） | 良好 | 免费 | 无需 API 密钥 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax** | 良好 | 付费 | `MINIMAX_API_KEY` |
| **xAI TTS** | 良好 | 付费 | `XAI_API_KEY` |
| **NeuTTS** | 良好 | 免费 | 无需 API 密钥 |
文本转语音功能支持八种服务提供商：本地版的 faster-whisper（免费，可在设备端运行）、本地命令封装工具、Groq、OpenAI Whisper API、Mistral、xAI、ElevenLabs Scribe 以及 DeepInfra。该功能可对 Telegram、Discord、WhatsApp 等各类消息平台中的语音消息进行转录。详情请参阅 [语音与文本转语音](/user-guide/features/tts) 以及 [语音模式](/user-guide/features/voice-mode) 文档。

## IDE 与编辑器集成

- **[IDE 集成（ACP）](/user-guide/features/acp)** — 可在 VS Code、Zed、JetBrains 等支持 ACP 的编辑器中使用 Hermes Agent。Hermes 会以 ACP 服务器的形式运行，从而在您的编辑器内展示聊天消息、工具操作记录、文件差异以及终端命令。

## 编程方式访问

- **[API 服务器](/user-guide/features/api-server)** — 可将 Hermes 暴露为兼容 OpenAI 格式的 HTTP 接口。任何支持 OpenAI 格式的前端应用——如 Open WebUI、LobeChat、LibreChat、NextChat、ChatBox——均可连接该接口，并将 Hermes 作为拥有完整工具集的后端来使用。

## 内存管理与个性化设置

- **[内置内存](/user-guide/features/memory)** — 通过 `MEMORY.md` 和 `USER.md` 文件实现持久化且经过整理的内存管理。该智能体会存储一定量的个人笔记和用户资料数据，这些数据可在不同会话之间保留。
- **[内存提供器](/user-guide/features/memory-providers)** — 支持接入外部内存后端以实现更深度的个性化功能。目前支持八种提供器：Honcho（辩证推理）、OpenViking（分层检索）、Mem0（云端提取）、Hindsight（知识图谱）、Holographic（本地 SQLite）、RetainDB（混合搜索）、ByteRover（基于 CLI 的方式）以及 Supermemory。

## 消息平台

Hermes 作为网关机器人运行在 27 种以上的消息平台上，所有平台的配置均通过同一个 `gateway` 子系统完成：

- **[Telegram](/user-guide/messaging/telegram)**、**[Discord](/user-guide/messaging/discord)**、**[Slack](/user-guide/messaging/slack)**、**[WhatsApp](/user-guide/messaging/whatsapp)**、**[Signal](/user-guide/messaging/signal)**、**[Matrix](/user-guide/messaging/matrix)**、**[Mattermost](/user-guide/messaging/mattermost)**、**[Email](/user-guide/messaging/email)**、**[SMS](/user-guide/messaging/sms)**、**[钉钉](/user-guide/messaging/dingtalk)**、**[飞书/Lark](/user-guide/messaging/feishu)**、**[企业微信](/user-guide/messaging/wecom)**、**[企业微信回调](/user-guide/messaging/wecom-callback)**、**[微信](/user-guide/messaging/weixin)**、**[BlueBubbles](/user-guide/messaging/bluebubbles)**、**[Buzz](/user-guide/messaging/buzz)**、**[QQ机器人](/user-guide/messaging/qqbot)**、**[元宝](/user-guide/messaging/yuanbao)**、**[Home Assistant](/user-guide/messaging/homeassistant)**、**[Microsoft Teams](/user-guide/messaging/teams)**、**[Microsoft Teams Meetings](/user-guide/messaging/teams-meetings)**、**[Microsoft Graph Webhook](/user-guide/messaging/msgraph-webhook)**、**[Google Chat](/user-guide/messaging/google_chat)**、**[LINE](/user-guide/messaging/line)**、**[ntfy](/user-guide/messaging/ntfy)**、**[SimpleX](/user-guide/messaging/simplex)**、**[Open WebUI](/user-guide/messaging/open-webui)**、**[Webhooks](/user-guide/messaging/webhooks)**

如需了解各平台的对比表格及设置指南，请参阅 [消息网关概述](/user-guide/messaging)。

### 快速连接链接

各大平台都设有标准的“创建机器人/应用”页面，其中一些平台还支持通过参数直接打开相应的表单。无需四处寻找控制台，可直接访问：

| 平台 | 直接链接 | 打开的页面 |
|------|----------|------------|
| **Telegram** | [t.me/BotFather](https://t.me/BotFather) | 与 BotFather 对话 —— 发送 `/newbot` 即可生成机器人令牌 |
| **Discord** | [discord.com/developers/applications?new_application=true](https://discord.com/developers/applications?new_application=true) | 开发者门户，已预加载“新建应用”对话框 |
| **Slack** | [api.slack.com/apps?new_app=1](https://api.slack.com/apps?new_app=1) | “创建新应用”对话框 —— 选择*从应用清单创建*，然后粘贴由 `hermes slack manifest --agent-view` 生成的清单文件 |
| **LINE** | [developers.line.biz/console](https://developers.line.biz/console/) | LINE 开发者控制台，用于创建消息传递 API 频道 |
| **飞书/企业微信** | [open.feishu.cn/app](https://open.feishu.cn/app) | 飞书开放平台控制台，用于创建自定义应用 |

每个平台的设置页面都会详细指导您在进入后需要完成的操作。

## 协作工作空间

- **[Buzz](/integrations/buzz)** — Block 基于 Nostr 构建的人机协作工作空间。提供三种集成方式：Buzz Desktop 会以托管式 ACP 运行时形式启动 Hermes；`buzz-acp` 中继桥在服务器端运行 Hermes 身份验证服务；而原生网关平台则能将 Buzz 频道与完整的 Hermes 内存管理、技能系统、审批流程及定时任务功能相连接。概述页面会对这三种方式进行对比说明。

## 家居自动化

- **[Home Assistant](/user-guide/messaging/homeassistant)** — 通过四种专用工具（`ha_list_entities`、`ha_get_state`、`ha_list_services`、`ha_call_service`）控制智能家居设备。当配置了 `HASS_TOKEN` 后，该 Home Assistant 工具集会自动启用。

## 插件

- **[插件系统](/user-guide/features/plugins)** — 无需修改核心代码，即可通过自定义工具、生命周期钩子及 CLI 命令来扩展 Hermes 功能。插件可从 `~/.hermes/plugins/`、项目内的 `.hermes/plugins/` 目录以及通过 pip 安装的插件入口点中获取。
- **[构建插件](/developer-guide/plugins)** — 提供逐步指南，帮助用户利用工具、钩子及 CLI 命令创建 Hermes 插件。

## 训练与评估

- **[批量处理](/user-guide/features/batch-processing)** — 可同时对数百条提示词处理 Agent，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或性能评估。
