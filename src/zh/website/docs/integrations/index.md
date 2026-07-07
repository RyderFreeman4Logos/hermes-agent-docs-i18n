---
title: "Integrations"
sidebar_label: "Overview"
sidebar_position: 0
---

# 集成功能

Hermes Agent 可连接外部系统，用于实现 AI 推理、工具服务器调用、IDE 工作流集成以及程序化访问等功能。这些集成扩展了 Hermes 的功能范围及其可运行的场景。

:::提示 从这里开始
如果您只能设置一个集成，建议先配置 [Nous Portal](/integrations/nous-portal)——通过一次 OAuth 登录即可使用 300 多种模型，以及四种工具网关功能（网页搜索、图像生成、文本转语音和浏览器自动化）。
:::

## AI 提供商与路由机制

Hermes 开箱即支持多种 AI 推理提供商。您可以通过 `hermes model` 命令进行交互式配置，也可直接在 `config.yaml` 文件中设置。

- **[AI 提供商](/user-guide/features/provider-routing)** — 支持 OpenRouter、Anthropic、OpenAI、Google 以及所有兼容 OpenAI 的接口。Hermes 能自动识别各提供商的视觉处理、流式处理和工具调用等能力。
- **[提供商路由](/user-guide/features/provider-routing)** — 可精细控制由哪些底层提供商处理您的 OpenRouter 请求。您可以通过排序、白名单、黑名单以及明确的优先级设置，来优化成本、速度或服务质量。
- **[备用提供商](/user-guide/features/fallback-providers)** — 当主模型出现错误时，系统会自动切换到备用的 LLM 提供商。该功能包括主模型故障时的备用方案，以及针对视觉处理、数据压缩和网页提取等任务的独立备用方案。

## 工具服务器（MCP）

- **[MCP 服务器](/user-guide/features/mcp)** — 通过模型上下文协议将 Hermes 与外部工具服务器连接起来。无需编写自定义的 Hermes 工具，即可调用来自 GitHub、数据库、文件系统、浏览器环境、内部 API 等来源的工具。该功能支持标准输入输出和流式传输两种方式，同时具备按服务器筛选工具以及基于能力特征的资源/提示词注册功能。

## 网页搜索后端

`web_search` 和 `web_extract` 工具支持八种不同的后端提供商，可通过 `config.yaml` 或 `hermes tools` 命令进行配置：

| 后端提供商 | 环境变量 | 搜索功能 | 提取功能 | 爬取功能 |
|---------|---------|--------|---------|-------|
| **Firecrawl**（默认） | `FIRECRAWL_API_KEY` | ✔ | ✔ | ✔ |
| **SearXNG** | `SEARXNG_URL` | ✔ | — | — |
| **Brave**（免费版） | `BRAVE_SEARCH_API_KEY` | ✔ | — | — |
| **DuckDuckGo**（ddgs） | _无_ | ✔ | — | — |
| **Tavily** | `TAVILY_API_KEY` | ✔ | ✔ | ✔ |
| **Exa** | `EXA_API_KEY` | ✔ | ✔ | — |
| **Parallel** | `PARALLEL_API_KEY` | ✔ | ✔ | — |
| **xAI** | `XAI_API_KEY` | ✔ | — | — |

快速配置示例：

```yaml
web:
  backend: firecrawl    # firecrawl | searxng | brave-free | ddgs | tavily | exa | parallel | xai
```

如果未设置 `web.backend`，系统会自动从可用的 API 密钥中检测合适的后端。此外，通过 `FIRECRAWL_API_URL` 也可支持自托管的 Firecrawl。

## 浏览器自动化

Hermes 提供完整的浏览器自动化功能，支持多种后端选项，可用于浏览网站、填写表单以及提取信息：

- **Browserbase** — 提供带防爬虫工具、验证码破解功能及住宅级代理的托管云浏览器服务；
- **Browser Use** — 另一种云浏览器提供商；
- **本地 Chromium 系列 CDP** — 通过 `/browser connect` 功能连接到正在运行的 Chrome、Brave、Chromium 或 Edge 浏览器；
- **本地 Chromium** — 通过 `agent-browser` CLI 启动的无头本地浏览器。

有关设置与使用方法，请参阅 [浏览器自动化](/user-guide/features/browser) 文档。

## 语音与文本转语音服务提供商

支持在所有消息平台上实现文本转语音及语音转文本功能：

| 提供商 | 音质 | 费用 | API 密钥 |
|--------|------|------|---------|
| **Edge TTS**（默认） | 良好 | 免费 | 无需提供 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax** | 良好 | 付费 | `MINIMAX_API_KEY` |
| **xAI TTS** | 良好 | 付费 | `XAI_API_KEY` |
| **NeuTTS** | 良好 | 免费 | 无需提供 |

语音转文本功能支持六种提供商：本地 faster-whisper（免费，可在设备端运行）、本地命令封装工具、Groq、OpenAI Whisper API、Mistral 以及 xAI。语音消息转录功能适用于 Telegram、Discord、WhatsApp 等各类消息平台。详细信息请参阅 [语音与文本转语音](/user-guide/features/tts) 以及 [语音模式](/user-guide/features/voice-mode) 文档。

## IDE与编辑器集成

- **[IDE 集成（ACP）](/user-guide/features/acp)** — 可在 VS Code、Zed 以及 JetBrains 等支持 ACP 的编辑器中使用 Hermes Agent。Hermes 会作为 ACP 服务器运行，从而在编辑器内展示聊天消息、工具操作记录、文件差异对比及终端命令。

## 程序化访问

- **[API 服务器](/user-guide/features/api-server)** — 将 Hermes 暴露为兼容 OpenAI 格式的 HTTP 接口。任何支持 OpenAI 格式的前端应用——如 Open WebUI、LobeChat、LibreChat、NextChat、ChatBox——均可连接并使用 Hermes 及其完整的工具集作为后端。

## 内存管理与个性化设置

- **[内置内存功能](/user-guide/features/memory)** — 通过 `MEMORY.md` 和 `USER.md` 文件实现持久化且经过整理的内存存储。Agent 能够保存一定量的个人笔记和用户资料数据，这些数据可在不同会话之间保留。
- **[内存提供程序](/user-guide/features/memory-providers)** — 可插入外部内存后端以实现更深度的个性化功能。目前支持八种提供程序：Honcho（基于辩证推理）、OpenViking（分层检索）、Mem0（云端信息提取）、Hindsight（知识图谱）、Holographic（本地 SQLite 存储）、RetainDB（混合搜索）、ByteRover（基于 CLI 的方案）以及 Supermemory。

## 消息平台支持

Hermes 作为网关机器人可在 27 种以上的消息平台上运行，所有配置均通过统一的 `gateway` 子系统完成：

- **[Telegram](/user-guide/messaging/telegram)**、**[Discord](/user-guide/messaging/discord)**、**[Slack](/user-guide/messaging/slack)**、**[WhatsApp](/user-guide/messaging/whatsapp)**、**[Signal](/user-guide/messaging/signal)**、**[Matrix](/user-guide/messaging/matrix)**、**[Mattermost](/user-guide/messaging/mattermost)**、**[Email](/user-guide/messaging/email)**、**[SMS](/user-guide/messaging/sms)**、**[DingTalk](/user-guide/messaging/dingtalk)**、**[Feishu/Lark](/user-guide/messaging/feishu)**、**[WeCom](/user-guide/messaging/wecom)**、**[WeCom Callback](/user-guide/messaging/wecom-callback)**、**[Weixin](/user-guide/messaging/weixin)**、**[BlueBubbles](/user-guide/messaging/bluebubbles)**、**[QQ Bot](/user-guide/messaging/qqbot)**、**[Yuanbao](/user-guide/messaging/yuanbao)**、**[Home Assistant](/user-guide/messaging/homeassistant)**、**[Microsoft Teams](/user-guide/messaging/teams)**、**[Microsoft Teams Meetings](/user-guide/messaging/teams-meetings)**、**[Microsoft Graph Webhook](/user-guide/messaging/msgraph-webhook)**、**[Google Chat](/user-guide/messaging/google_chat)**、**[LINE](/user-guide/messaging/line)**、**[ntfy](/user-guide/messaging/ntfy)**、**[SimpleX](/user-guide/messaging/simplex)**、**[Open WebUI](/user-guide/messaging/open-webui)**、**[Webhooks](/user-guide/messaging/webhooks)**

平台对比表及配置指南请参阅 [消息网关概览](/user-guide/messaging) 文档。

## 家居自动化

- **[Home Assistant](/user-guide/messaging/homeassistant)** — 通过四个专用工具（`ha_list_entities`、`ha_get_state`、`ha_list_services`、`ha_call_service`）控制智能家居设备。当配置了 `HASS_TOKEN` 后，Home Assistant 相关工具集会自动启用。

## 插件系统

- **[插件系统](/user-guide/features/plugins)** — 无需修改核心代码，即可通过自定义工具、生命周期钩子及 CLI 命令来扩展 Hermes 功能。插件可从 `~/.hermes/plugins/`、项目本地目录下的 `.hermes/plugins/` 以及通过 pip 安装的插件入口点中找到。
- **[创建插件](/developer-guide/plugins)** — 提供分步指南，帮助您使用工具、钩子及 CLI 命令创建 Hermes 插件。

## 训练与评估

- **[批量处理功能](/user-guide/features/batch-processing)** — 可同时处理数百条提示词，生成结构化的 ShareGPT 格式轨迹数据，用于训练数据生成或性能评估。
