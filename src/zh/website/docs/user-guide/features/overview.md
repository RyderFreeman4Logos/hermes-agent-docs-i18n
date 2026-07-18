---
title: "Features Overview"
sidebar_label: "Overview"
sidebar_position: 1
---

# 功能概览

Hermes Agent 拥有丰富的功能，远不止基础聊天功能。从持久化内存与文件感知上下文，到浏览器自动化及语音对话，这些功能相互配合，让 Hermes 成为一款强大的自主助手。

:::提示 不知道从哪里开始？
只需一条命令 `hermes setup --portal` 即可同时配置模型提供器以及四种工具网关（网页搜索、图像生成、文本转语音、浏览器控制），详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 核心功能

- **[工具与工具集](tools.md)** — 工具是用于扩展助手功能的函数。它们被组织成逻辑化的工具集，可根据不同平台启用或禁用，涵盖网页搜索、终端执行、文件编辑、内存管理、任务委托等功能。
- **[技能系统](skills.md)** — 助手可在需要时加载按需知识文档。技能采用渐进式展示机制，以减少token消耗，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。
- **[持久化内存](memory.md)** — 一种有限且经过筛选的记忆系统，可在不同会话之间保持不变。Hermes 会通过 `MEMORY.md` 和 `USER.md` 文件记住您的偏好设置、项目信息、当前环境以及所学内容。
- **[上下文文件](context-files.md)** — Hermes 会自动发现并加载项目上下文文件（如 `.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`SOUL.md`、`.cursorrules`），这些文件决定了助手在您项目中的行为方式。
- **[上下文引用](context-references.md)** — 输入 `@` 后跟引用内容，即可将文件、文件夹、Git差异对比结果或URL直接嵌入消息中。Hermes 会自动在线展开引用并附加对应内容。
- **[检查点](../checkpoints-and-rollback.md)** — Hermes 会在对文件进行更改之前自动创建工作目录的快照，这样一旦出现问题，您就可以使用 `/rollback` 命令安全地恢复到之前的状态。

## 自动化功能

- **[定时任务（Cron）](cron.md)** — 可通过自然语言或Cron表达式安排任务自动执行。任务可绑定技能，将结果发送到任意平台，并支持暂停/继续及编辑操作。
- **[子助手委托](delegation.md)** — `delegate_task` 工具可创建具有独立上下文、受限工具集以及专属终端会话的子助手实例。默认情况下可同时运行3个并行工作的子助手（具体数量可配置）。
- **[代码执行](code-execution.md)** — `execute_code` 工具允许助手编写Python脚本，以编程方式调用Hermes工具，通过沙箱化的RPC执行方式将多步骤工作流程整合为单次大语言模型响应。
- **[事件钩子](hooks.md)** — 可在关键生命周期节点运行自定义代码。网关钩子用于处理日志记录、警报及Webhook请求；插件钩子则用于实现工具拦截、性能监控及规则限制。
- **[批量处理](batch-processing.md)** — 可让Hermes助手同时处理数百甚至数千条提示词，生成结构化的ShareGPT格式轨迹数据，用于训练数据生成或评估。

## 媒体与网页功能

- **[语音模式](voice-mode.md)** — 支持在CLI及消息平台中进行完整的语音交互。您可以使用麦克风与助手对话，听到其语音回复，还能在Discord语音频道中开展实时语音交流。
- **[浏览器自动化](browser.md)** — 支持多种后端的完整浏览器自动化功能：Browserbase云服务、Browser Use云服务、通过CDP连接的本地Chrome/Brave/Chromium/Edge浏览器，或是本地Chromium浏览器。可用来浏览网站、填写表单并提取信息。
- **[视觉功能与图像粘贴](vision.md)** — 支持多模态视觉处理。您可以将剪贴板中的图像粘贴到CLI中，然后让助手使用任何具备视觉功能的模型对其进行分析、描述或进行其他操作。
- **[图像生成](image-generation.md)** — 可使用FAL.ai根据文本提示词生成图像。目前支持11种模型（FLUX 2 Klein/Pro、GPT-Image 1.5/2、Nano Banana Pro、Ideogram V3、Recraft V4 Pro、Qwen、Z-Image Turbo、Krea V2 Medium/Large），可通过 `hermes tools` 命令选择所需模型。
- **[语音与文本转语音](tts.md)** — 支持在所有消息平台中进行文本转语音输出及语音消息转写，内置10种提供商选项：Edge TTS（免费）、ElevenLabs、OpenAI TTS、MiniMax、Mistral Voxtral、Google Gemini、xAI、NeuTTS、KittenTTS以及Piper；此外还支持针对任何本地文本转语音CLI的自定义命令提供商。

## 集成功能

- **[MCP集成](mcp.md)** — 可通过标准输入/输出或HTTP传输方式连接到任意MCP服务器。无需编写专属的Hermes工具，即可使用来自GitHub、数据库、文件系统及内部API的外部工具。该功能还支持按服务器筛选工具并设置采样策略。
- **[提供商路由](provider-routing.md)** — 可精细控制由哪些AI提供商处理您的请求。可通过排序、白名单、黑名单及优先级设置，根据成本、速度或质量需求进行优化。
- **[备用提供商](fallback-providers.md)** — 当主模型出现错误时，系统会自动切换到备用的LLM提供商，同时针对视觉处理和压缩等辅助任务也提供独立的备用方案。
- **[凭证池](credential-pools.md)** — 可将同一提供商的API调用分散到多个密钥上执行。在遇到速率限制或故障时，系统会自动切换密钥。
- **[提示词缓存](../configuration#prompt-caching)** — 在Anthropic原生平台、OpenRouter及Nous Portal上，Claude内置了跨会话的1小时前缀缓存功能。该功能始终处于启用状态，无需额外配置。
- **[内存提供器](memory-providers.md)** — 可接入外部内存后端（如Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover、Supermemory），以实现超越内置内存系统的跨会话用户建模与个性化功能。
- **[API服务器](api-server.md)** — 可将Hermes作为兼容OpenAI协议的HTTP接口对外提供。任何支持OpenAI格式的前端应用——如Open WebUI、LobeChat、LibreChat等——均可与之连接。
- **[IDE集成（ACP）](acp.md)** — 可在VS Code、Zed及JetBrains等支持ACP的编辑器中使用Hermes。聊天内容、工具操作记录、文件差异对比结果以及终端命令都可在编辑器内直接显示。
- **[批量处理](batch-processing.md)** — 可通过CLI让助手同时处理大量提示词或任务，生成结构化的输出结果并记录操作轨迹，非常适合用于评估或后续训练流程。

## 自定义设置

- **[个性设置与SOUL.md](personality.md)** — 可完全自定义助手的个性特征。`SOUL.md` 是主要的身份配置文件，位于系统提示词的最开头，您可以根据需要为每个会话选择内置或自定义的 `/personality` 预设值。
- **[皮肤与主题](skins.md)** — 可自定义CLI的视觉外观：横幅颜色、加载动画的图标和文字、响应框标签、品牌文字以及工具操作前缀等。
- **[插件](plugins.md)** — 无需修改核心代码即可添加自定义工具、钩子及集成功能。插件共有三种类型：通用插件（工具/钩子）、内存提供器（跨会话知识存储）以及上下文引擎（替代性上下文管理方式）。可通过统一的 `hermes plugins` 交互式界面进行管理。
