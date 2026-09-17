---
title: "Features Overview"
sidebar_label: "Overview"
sidebar_position: 1
---

# 功能概览

Hermes Agent拥有丰富多样的功能，远不止基础聊天功能。从持久化记忆与文件感知的上下文管理，到浏览器自动化操作及语音对话，这些功能相互配合，让Hermes成为一款功能强大的自主助手。

:::提示 不知道从何开始？
只需一条命令`hermes setup --portal`，即可同时配置模型提供商以及四种工具网关（网页搜索、图像生成、文本转语音、浏览器控制）的功能。详情请参阅[Nous Portal](/integrations/nous-portal)。
:::

## 核心功能

- **[工具与工具集](tools.md)** — 工具是用于扩展智能体功能的函数。它们被整理为逻辑上的工具集，可根据不同平台进行启用或禁用，涵盖网页搜索、终端执行、文件编辑、内存管理、任务委托等功能。
- **[技能系统](skills.md)** — 智能体可在需要时加载的按需知识文档。这些技能采用渐进式展示机制，以减少令牌消耗，并兼容 [agentskills.io](https://agentskills.io/specification) 开放标准。
- **[持久内存](memory.md)** — 一种有限且经过筛选的内存，可在不同会话之间保持不变。Hermes 会通过 `MEMORY.md` 和 `USER.md` 记住您的偏好设置、项目信息、环境配置以及所学内容。
- **[上下文文件](context-files.md)** — Hermes 会自动发现并加载项目上下文文件（如 `.hermes.md`、`AGENTS.md`、`CLAUDE.md`、`SOUL.md`、`.cursorrules`），这些文件决定了智能体在您项目中的行为方式。
- **[上下文引用](context-references.md)** — 输入 `@` 后跟上引用标识，即可将文件、文件夹、Git 差异内容及网址直接插入消息中。Hermes 会在线展开该引用并自动附加对应内容。
- **[检查点](../checkpoints-and-rollback.md)** — 在对文件进行修改之前，Hermes 会自动创建工作目录的快照，如此一旦出现异常，您便可通过 `/rollback` 命令安全地恢复到之前的状态。

## 自动化

- **[定时任务（Cron）](cron.md)** — 支持使用自然语言或 Cron 表达式来安排任务自动执行。这些任务可绑定相应技能，将结果输出到任意平台，并且还支持暂停/恢复及编辑操作。
- **[子代理委托](delegation.md)** — `delegate_task` 工具能够创建具有独立上下文、受限工具集以及专属终端会话的子代理实例。默认情况下可同时运行 3 个子代理（该数值可配置），以实现并行处理。
- **[代码执行](code-execution.md)** — `execute_code` 工具允许代理编写 Python 脚本，以编程方式调用 Hermes 的各种工具；通过沙箱化的 RPC 执行机制，可将多步骤工作流整合为单次大语言模型响应。
- **[事件钩子](hooks.md)** — 可在关键生命周期节点运行自定义代码。网关钩子用于处理日志记录、警报通知以及 Webhook 请求；插件钩子则负责工具拦截、指标收集以及规则管控。
- **[批量处理](batch-processing.md)** — 能够让 Hermes 代理并行处理成百上千条提示词，从而生成结构化的 ShareGPT 格式轨迹数据，用于训练数据的创建或评估。

## 媒体与网页

- **[语音模式](voice-mode.md)** — 支持在命令行界面及各类消息平台中进行完整的语音交互。您可以通过麦克风与智能体对话，聆听其语音回复，并在 Discord 的语音频道中开展实时语音交流。  
- **[唤醒词](wake-word.md)** — 为命令行界面、文本用户界面及桌面应用提供免提式的“Hey Hermes”唤醒功能。当您说出预设的唤醒语时，设备上的热词监听器便会启动语音会话。  
- **[浏览器自动化](browser.md)** — 支持多种后端环境的完整浏览器自动化功能：Browserbase 云服务、Browser Use 云服务、通过 CDP 连接的本地 Chrome/Brave/Chromium/Edge 浏览器，或是本地 Chromium 浏览器。您可以利用这些功能浏览网页、填写表单并提取信息。  
- **[视觉识别与图片粘贴](vision.md)** — 提供多模态视觉处理能力。您可以将剪贴板中的图片粘贴到命令行界面中，然后让智能体使用任何具备视觉分析功能的模型对这些图片进行分析、描述或进行其他操作。  
- **[图像生成](image-generation.md)** — 可通过 FAL.ai 根据文本提示生成图像。目前支持十种模型（FLUX 2 Klein/Pro、GPT-Image 1.5/2、Nano Banana Pro、Ideogram V3、Recraft V4 Pro、Qwen、Z-Image Turbo、Krea V2 Medium/Large），您可通过 `hermes tools` 命令选择所需模型。  
- **[语音与文本转语音](tts.md)** — 支持在所有消息平台上进行文本转语音输出及语音消息转录，提供十种原生服务提供商选项：Edge TTS（免费）、ElevenLabs、OpenAI TTS、MiniMax、Mistral Voxtral、Google Gemini、xAI、NeuTTS、KittenTTS 以及 Piper；此外还支持为任何本地文本转语音命令行工具定制服务提供商。  

## 集成方案

- **[MCP集成](mcp.md)** — 通过标准输入/输出或HTTP协议连接任意MCP服务器。无需编写专属的Hermes工具，即可调用来自GitHub、数据库、文件系统以及内部API的外部工具。该功能还支持针对不同服务器的工具过滤与采样功能。
- **[提供者路由](provider-routing.md)** — 可精细控制由哪些AI提供者来处理您的请求。通过排序、白名单、黑名单及优先级设置，帮助您在成本、速度或质量之间实现最优平衡。
- **[备用提供者](fallback-providers.md)** — 当主模型出现故障时，可自动切换至备用的LLM提供者，同时针对图像处理和压缩等辅助任务也提供了独立的备用方案。
- **[凭证池](credential-pools.md)** — 允许对同一提供者的多次API调用使用不同的访问凭证。在遇到速率限制或请求失败时，系统会自动切换凭证。
- **[提示词缓存](../configuration#prompt-caching)** — 在Anthropic原生平台、OpenRouter及Nous Portal上，为Claude内置了跨会话的1小时提示词前缀缓存功能。该功能始终处于激活状态，无需额外配置。
- **[内存提供者](memory-providers.md)** — 支持接入外部内存后端（如Honcho、OpenViking、Mem0、Hindsight、Holographic、RetainDB、ByteRover、Supermemory），从而在内置内存系统之外实现更强大的跨会话用户建模与个性化功能。
- **[API服务器](api-server.md)** — 将Hermes作为兼容OpenAI协议的HTTP接口对外提供。任何支持OpenAI格式的前端应用——如Open WebUI、LobeChat、LibreChat等——均可与之连接。
- **[IDE集成（ACP）](acp.md)** — 在VS Code、Zed以及JetBrains等支持ACP的编辑器中使用Hermes。聊天内容、工具操作记录、文件差异对比以及终端命令都将在编辑器内直接显示。
- **[批量处理](batch-processing.md)** — 通过CLI并行处理多个提示词或任务，生成结构化输出并记录执行轨迹，便于进行性能评估或后续训练流程。

## 自定义设置

- **[个性与SOUL配置](personality.md)** — 可完全自定义智能体的性格特点。`SOUL.md`是核心身份配置文件，会作为系统提示词的第一部分；您还可以根据不同会话需求，选择内置或自定义的 `/personality` 预设值。
- **[皮肤与主题](skins.md)** — 自定义CLI的视觉呈现效果：包括横幅颜色、加载动画的图标与文字、响应框标签、品牌文本以及工具操作记录的前缀。
- **[插件](plugins.md)** — 无需修改核心代码即可添加自定义工具、钩子功能及集成方案。插件分为三类：通用插件（工具/钩子）、内存提供器（跨会话知识存储）以及上下文引擎（替代性上下文管理方式）。所有插件均通过统一的 `hermes plugins` 交互式界面进行管理。
