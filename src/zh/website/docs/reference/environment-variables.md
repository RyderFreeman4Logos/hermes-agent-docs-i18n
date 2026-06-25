---
sidebar_position: 2
title: "Environment Variables"
description: "Complete reference of all environment variables used by Hermes Agent"
---

# 环境变量参考

Hermes 会从进程环境读取环境变量，而对于用户管理的机密信息，则从 `~/.hermes/.env` 文件中获取。请将 API 密钥、机器人令牌、OAuth 密钥以及其他凭证存储在 `.env` 文件中；如果存在配置键，建议优先使用 `config.yaml` 来设置非机密性的行为参数。以下部分变量仅为进程级覆盖项或内部桥接变量，即便此处有相关说明，也不应将其加入 `.env` 文件中。

## 大语言模型提供方| 变量名 | 描述 |
|--------|------|
| `OPENROUTER_API_KEY` | OpenRouter API密钥（为提升灵活性推荐使用） |
| `OPENROUTER_BASE_URL` | 覆盖与OpenRouter兼容的基URL |
| `HERMES_OPENROUTER_CACHE` | 启用OpenRouter响应缓存（值为`1`/`true`/`yes`/`on`）。会覆盖`config.yaml`中的`openrouter.response_cache`设置。详情请参阅[响应缓存](https://openrouter.ai/docs/guides/features/response-caching)。 |
| `HERMES_OPENROUTER_CACHE_TTL` | 缓存有效期，以秒为单位（范围：1-86400）。会覆盖`config.yaml`中的`openrouter.response_cache_ttl`设置。 |
| `NOUS_BASE_URL` | 覆盖Nous Portal的基URL（极少需要，仅用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 直接覆盖Nous推理接口的地址 |
| `OPENAI_API_KEY` | 用于自定义OpenAI兼容接口的API密钥（需与`OPENAI_BASE_URL`一起使用） |
| `OPENAI_BASE_URL` | 自定义接口的基URL（适用于VLLM、SGLang等框架） |
| `LM_API_KEY` | LM Studio（`lmstudio`提供者）的API密钥。通常用于本地服务器场景 |
| `LM_BASE_URL` | LM Studio的基URL（默认值：`http://localhost:1234/v1`） |
| `COPILOT_GITHUB_TOKEN` | Copilot API所需的GitHub令牌——优先级最高（支持OAuth类型的`gho_*`令牌或细粒度PAT类型的`github_pat_*`令牌；传统的PAT类型`ghp_*`不受支持） |
| `GH_TOKEN` | GitHub令牌——Copilot的第二优先级令牌（同时也被`gh` CLI使用） |
| `GITHUB_TOKEN` | GitHub令牌——Copilot的第三优先级令牌 |
| `HERMES_COPILOT_ACP_COMMAND` | 覆盖Copilot ACP CLI二进制文件的路径（默认值：`copilot`） |
| `COPILOT_CLI_PATH` | `HERMES_COPILOT_ACP_COMMAND`的别名 |
| `HERMES_COPILOT_ACP_ARGS` | 覆盖Copilot ACP的参数（默认值：`--acp --stdio`） |
| `COPILOT_ACP_BASE_URL` | 覆盖Copilot ACP的基URL |
| `COPILOT_API_BASE_URL` | 覆盖Copilot API的基URL（对应`copilot`提供者） |
| `GLM_API_KEY` | z.ai / ZhipuAI GLM API密钥（平台地址：[z.ai](https://z.ai)） |
| `ZAI_API_KEY` | `GLM_API_KEY`的别名 |
| `Z_AI_API_KEY` | `GLM_API_KEY`的别名 |
| `GLM_BASE_URL` | 覆盖z.ai的基URL（默认值：`https://api.z.ai/api/paas/v4`） |
| `KIMI_API_KEY` | Kimi / Moonshot AI API密钥（平台地址：[moonshot.ai](https://platform.moonshot.ai)） |
| `KIMI_CODING_API_KEY` | `kimi-coding`提供者对应的别名密钥，可与`KIMI_API_KEY`同时使用 |
| `KIMI_BASE_URL` | 覆盖Kimi的基URL（默认值：`https://api.moonshot.ai/v1`） |
| `KIMI_CN_API_KEY` | Kimi / Moonshot中国区API密钥（平台地址：[moonshot.cn](https://platform.moonshot.cn)） |
| `ARCEEAI_API_KEY` | Arcee AI API密钥（平台地址：[chat.arcee.ai](https://chat.arcee.ai/)） |
| `ARCEE_BASE_URL` | 覆盖Arcee的基URL（默认值：`https://api.arcee.ai/api/v1`） |
| `GMI_API_KEY` | GMI Cloud API密钥（平台地址：[gmicloud.ai](https://www.gmicloud.ai/)） |
| `GMI_BASE_URL` | 覆盖GMI Cloud的基URL（默认值：`https://api.gmi-serving.com/v1`） |
| `MINIMAX_API_KEY` | MiniMax API密钥——全球通用接口（平台地址：[minimax.io](https://www.minimax.io)）。**`minimax-oauth`模式不会使用该密钥**（该模式通过浏览器登录即可） |
| `MINIMAX_BASE_URL` | 覆盖Minimax的基URL（默认值：`https://api.minimax.io/anthropic`——Hermes使用的是Minimax兼容Anthropic Messages格式的接口）。**`minimax-oauth`模式也不会使用该值** |
| `MINIMAX_CN_API_KEY` | MiniMax API密钥——中国区接口（平台地址：[minimaxi.com](https://www.minimaxi.com)）。**`minimax-oauth`模式不会使用该密钥**（该模式通过浏览器登录即可） |
| `MINIMAX_CN_BASE_URL` | 覆盖Minimax中国区的基URL（默认值：`https://api.minimaxi.com/anthropic`）。**`minimax-oauth`模式不会使用该值** |
| `KILOCODE_API_KEY` | Kilo Code API密钥（平台地址：[kilo.ai](https://kilo.ai)） |
| `KILOCODE_BASE_URL` | 覆盖Kilo Code的基URL（默认值：`https://api.kilo.ai/api/gateway`） |
| `XIAOMI_API_KEY` | 小米MiMo API密钥（平台地址：[platform.xiaomimimo.com](https://platform.xiaomimimo.com)） |
| `XIAOMI_BASE_URL` | 覆盖小米MiMo的基URL（默认值：`https://api.xiaomimimo.com/v1`） |
| `TOKENHUB_API_KEY` | 腾讯TokenHub API密钥（平台地址：[tokenhub.tencentmaas.com](https://tokenhub.tencentmaas.com)） |
| `TOKENHUB_BASE_URL` | 覆盖腾讯TokenHub的基URL（默认值：`https://tokenhub.tencentmaas.com/v1`） |
| `AZURE_FOUNDRY_API_KEY` | Microsoft Foundry / Azure OpenAI API密钥（平台地址：[ai.azure.com](https://ai.azure.com/)）。当`model.auth_mode: entra_id`时无需此密钥 |
| `AZURE_FOUNDRY_BASE_URL` | Microsoft Foundry接口地址（例如，OpenAI风格接口为`https://<resource>.openai.azure.com/openai/v1`，Anthropic风格接口为`https://<resource>.services.ai.azure.com/anthropic`） |
| `AZURE_ANTHROPIC_KEY` | 用于`provider: anthropic`场景的Azure Anthropic API密钥，且其对应的`base_url`需指向Microsoft Foundry部署的Claude服务——当同时配置了Anthropic和Azure Anthropic时，该密钥可作为`ANTHROPIC_API_KEY`的替代方案 |
| `AZURE_TENANT_ID` | Entra ID租户ID（用于服务主体流程；当`model.auth_mode: entra_id`时，`azure-identity`会自动识别该值） |
| `AZURE_CLIENT_ID` | Entra ID客户端ID（可为服务主体、工作负载身份或用户分配的托管身份） |
| `AZURE_CLIENT_SECRET` | `EnvironmentCredential`所使用的服务主体密钥 |
| `AZURE_CLIENT_CERTIFICATE_PATH` | 服务主体证书文件路径（可作为`AZURE_CLIENT_SECRET`的替代方案） |
| `AZURE_FEDERATED_TOKEN_FILE` | AKS工作负载身份/OIDC流程所使用的联合令牌文件路径 |
| `AZURE_AUTHORITY_HOST` | 主权云授权服务器地址的覆盖值（例如，Azure政府版为`https://login.microsoftonline.us`）。详情请参阅[Azure Foundry指南](/guides/azure-foundry#sovereign-clouds-government-china) |
| `IDENTITY_ENDPOINT` / `MSI_ENDPOINT` | App Service、Functions及Container Apps所使用的托管身份接口地址；虚拟机通常使用IMDS机制，无需设置这些参数 |
| `HF_TOKEN` | 用于推理提供者的Hugging Face令牌（可在[Huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)处生成） |
| `HF_BASE_URL` | 覆盖Hugging Face的基URL（默认值：`https://router.huggingface.co/v1`） |
| `GOOGLE_API_KEY` | Google AI Studio API密钥（生成地址：[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)） |
| `GEMINI_API_KEY` | `GOOGLE_API_KEY`的别名 |
| `GEMINI_BASE_URL` | 覆盖Google AI Studio的基URL |
| `ANTHROPIC_API_KEY` | Anthropic控制台API密钥（平台地址：[console.anthropic.com](https://console.anthropic.com/)） |
| `ANTHROPIC_BASE_URL` | 覆盖Anthropic API的基URL |
| `ANTHROPIC_TOKEN` | 手动设置的或旧版的Anthropic OAuth/设置令牌覆盖值 |
| `DASHSCOPE_API_KEY` | 阿里云Qwen模型对应的Qwen Cloud（Alibaba DashScope）API密钥（管理地址：[modelstudio.console.alibabacloud.com](https://modelstudio.console.alibabacloud.com/)） |
| `DASHSCOPE_BASE_URL` | 自定义的DashScope基URL（默认值：`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`；中国内地地区请使用`https://dashscope.aliyuncs.com/compatible-mode/v1`） |
| `ALIBABA_CODING_PLAN_API_KEY` | Qwen编程计划API密钥（对应`alibaba-coding-plan`提供者） |
| `ALIBABA_CODING_PLAN_BASE_URL` | 覆盖Qwen编程计划的基URL |
| `DEEPSEEK_API_KEY` | 直接访问DeepSeek模型所需的API密钥（平台地址：[platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys)） |
| `DEEPSEEK_BASE_URL` | 自定义的DeepSeek API基URL |
| `NOVITA_API_KEY` | NovitaAI API密钥——专为模型API、Agent Sandbox及GPU云服务设计的原生AI云平台（密钥管理地址：[novita.ai/settings/key-management](https://novita.ai/settings/key-management)） |
| `NOVITA_BASE_URL` | 覆盖NovitaAI的基URL（默认值：`https://api.novita.ai/openai/v1`） |
| `NVIDIA_API_KEY` | NVIDIA NIM API密钥——用于Nemotron及开源模型的接口（生成地址：[build.nvidia.com](https://build.nvidia.com)） |
| `NVIDIA_BASE_URL` | 覆盖NVIDIA的基URL（默认值：`https://integrate.api.nvidia.com/v1`；如需使用本地NIM接口，可设置为`http://localhost:8000/v1`） |
| `STEPFUN_API_KEY` | StepFun API密钥——用于Step系列模型的接口（平台地址：[platform.stepfun.com](https://platform.stepfun.com)） |
| `STEPFUN_BASE_URL` | 覆盖StepFun的基URL（默认值：`https://api.stepfun.com/v1`） |
| `OLLAMA_API_KEY` | Ollama Cloud API密钥——无需本地GPU即可使用的托管Ollama模型库（密钥管理地址：[ollama.com/settings/keys](https://ollama.com/settings/keys)） |
| `OLLAMA_BASE_URL` | 覆盖Ollama Cloud的基URL（默认值：`https://ollama.com/v1`） |
| `XAI_API_KEY` | xAI（Grok）API密钥，支持聊天、文本转语音及网络搜索功能（控制台地址：[console.x.ai](https://console.x.ai/)） |
| `XAI_BASE_URL` | 覆盖xAI的基URL（默认值：`https://api.x.ai/v1`） |
| `MISTRAL_API_KEY` | Mistral API密钥，用于Voxtral文本转语音及语音转文本功能（控制台地址：[console.mistral.ai](https://console.mistral.ai)） |
| `AWS_REGION` | Bedrock推理服务的AWS区域（例如`us-east-1`、`eu-central-1`）。该值由boto3自动读取 |
| `AWS_PROFILE` | 用于Bedrock身份验证的AWS命名配置文件（会读取`~/.aws/credentials`中的设置）。如未指定该值，则使用boto3默认的凭据链 |
| `BEDROCK_BASE_URL` | 覆盖Bedrock运行时基URL（默认值：`https://bedrock-runtime.us-east-1.amazonaws.com`；通常无需设置，直接使用`AWS_REGION`即可） |
| `HERMES_QWEN_BASE_URL` | 覆盖Qwen Portal的基URL（默认值：`https://portal.qwen.ai/v1`） |
| `OPENCODE_ZEN_API_KEY` | OpenCode Zen API密钥——支持按需使用精选模型的按量付费服务（平台地址：[opencode.ai](https://opencode.ai/auth)） |
| `OPENCODE_ZEN_BASE_URL` | 覆盖OpenCode Zen的基URL |
| `OPENCODE_GO_API_KEY` | OpenCode Go API密钥——可按月支付10美元使用开源模型的服务（平台地址：[opencode.ai](https://opencode.ai/auth)） |
| `OPENCODE_GO_BASE_URL` | 覆盖OpenCode Go的基URL |
| `CLAUDE_CODE_OAUTH_TOKEN` | 若您手动导出了Claude Code令牌，可在此处显式指定该令牌值 |
| `HERMES_MODEL` | 在进程层面覆盖模型名称（主要用于cron调度器；常规使用建议通过`config.yaml`配置） |
| `VOICE_TOOLS_OPENAI_KEY` | 用于OpenAI语音转文本及文本转语音服务的推荐OpenAI API密钥 |
| `HERMES_LOCAL_STT_COMMAND` | 可选的本地语音转文本命令模板。支持使用 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 等占位符 |
| `HERMES_LOCAL_STT_LANGUAGE` | 传递给`HERMES_LOCAL_STT_COMMAND`的默认语言，或自动检测的本地`whisper` CLI默认语言（默认值：`en`） |
| `HERMES_HOME` | 覆盖Hermes配置目录的路径（默认值：`~/.hermes`）。该设置还会确定网关PID文件的位置及systemd服务名称，便于多实例同时运行 |
| `HERMES_GIT_BASH_PATH` | **仅适用于Windows系统**。用于指定终端工具所使用的`bash.exe`路径。可指向任何版本的bash——包括完整版的Git-for-Windows、通过符号链接连接的WSL bash、MSYS2或Cygwin。安装程序会自动将此路径设置为它所配置的PortableGit版本。详情请参阅[Windows（原生）指南](../user-guide/windows-native.md#how-hermes-runs-shell-commands-on-windows) |
| `HERMES_DISABLE_WINDOWS_UTF8` | **仅适用于Windows系统**。将其设置为`1`可禁用UTF-8标准输入输出模拟层（`configure_windows_stdio()`函数），转而使用控制台的本地代码页。该设置有助于排查编码相关问题；在正常运行时很少需要使用 |
| `HERMES_KANBAN_HOME` | 覆盖用于存储看板数据（数据库、工作空间及 worker日志）的共享Hermes根目录。如未指定该值，则会回退到`get_default_hermes_root()`函数确定的路径（即所有活跃配置文件的父目录）。该设置适用于测试或特殊部署场景 |
| `HERMES_KANBAN_BOARD` | 固定当前进程所使用的看板名称。该设置优先级高于`~/.hermes/kanban/current`；调度器会将此值注入worker子进程的环境变量中，从而确保worker无法查看其他看板上的任务。默认值为`default`。有效值格式：小写字母、数字、连字符及下划线组合，长度为1-64个字符 |
| `HERMES_KANBAN_DB` | 直接指定看板数据库文件的路径——优先级最高，可覆盖`HERMES_KANBAN_BOARD`和`HERMES_KANBAN_HOME`的设置。调度器会将此值注入worker子进程的环境变量中，确保所有profile worker都使用同一数据库 |
| `HERMES_KANBAN_WORKSPACES_ROOT` | 直接指定看板工作空间的根目录——针对工作空间而言优先级最高，可覆盖`HERMES_KANBAN_HOME`的设置。调度器会将此值注入worker子进程的环境变量中 |
| `HERMES_KANBAN_DISPATCH_IN_GATEWAY` | 对`kanban.dispatch_in_gateway`参数的运行时覆盖值。将其设置为`0`、`false`、`no`或`off`可阻止网关启动内置的Kanban调度器；任何非空字符串值都会启用该调度器。当有独立的调度器进程负责管理看板时，可使用此设置 |## 提供商认证（OAuth）

对于原生 Anthropic 认证方式，若存在 Claude Code 自带的凭据文件，Hermes 会优先使用这些文件，因为其凭据可以自动刷新。**通过 OAuth 连接 Anthropic 需要购买额外使用额度的 Claude Max 套餐**——Hermes 会以 Claude Code 的身份发起请求，仅能消耗 Max 套餐的额外/超额额度，无法使用基础 Max 配额，且不支持 Claude Pro。若没有 Max 套餐及额外额度，则应使用 API 密钥。虽然 `ANTHROPIC_TOKEN` 等环境变量仍可用于手动覆盖设置，但已不再是 Claude Max 登录的首选方式。

| 变量 | 描述 |
|------|------|
| `HERMES_PORTAL_BASE_URL` | 覆盖 Nous Portal URL（用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 覆盖 Nous 推理 API URL |
| `HERMES_NOUS_MIN_KEY_TTL_SECONDS` | 代理密钥在重新生成前的最小有效期（默认：1800 秒 = 30 分钟） |
| `HERMES_NOUS_TIMEOUT_SECONDS` | Nous 凭据/令牌流程的 HTTP 超时时间 |
| `HERMES_DUMP_REQUESTS` | 将 API 请求载荷输出到日志文件（`true`/`false`） |
| `HERMES_PREFILL_MESSAGES_FILE` | API 调用时注入的临时预填消息的 JSON 文件路径 |
| `HERMES_TIMEZONE` | IANA 时区覆盖值（例如 `America/New_York`） |

## 工具 API

| 变量 | 描述 |
|------|------|
| `PARALLEL_API_KEY` | 原生 AI 网页搜索服务（[parallel.ai](https://parallel.ai/)） |
| `FIRECRAWL_API_KEY` | 网页抓取与云浏览器服务（[firecrawl.dev](https://firecrawl.dev/)） |
| `FIRECRAWL_API_URL` | 自托管实例的自定义 Firecrawl API 接口地址（可选） |
| `TAVILY_API_KEY` | 用于原生 AI 网页搜索、内容提取与爬取的 Tavily API 密钥（[app.tavily.com](https://app.tavily.com/home)） |
| `SEARXNG_URL` | 免费自托管网页搜索的 SearXNG 实例地址——无需 API 密钥（[searxng.github.io](https://searxng.github.io/searxng/)） |
| `TAVILY_BASE_URL` | 覆盖 Tavily API 接口地址。适用于企业代理环境及自托管的 Tavily 兼容搜索后端，格式与 `GROQ_BASE_URL` 相同。 |
| `EXA_API_KEY` | 用于原生 AI 网页搜索与内容处理的 Exa API 密钥（[exa.ai](https://exa.ai/)） |
| `BROWSERBASE_API_KEY` | 浏览器自动化工具（[browserbase.com](https://browserbase.com/)） |
| `BROWSERBASE_PROJECT_ID` | Browserbase 项目编号 |
| `BROWSER_USE_API_KEY` | Browser Use 云浏览器 API 密钥（[browser-use.com](https://browser-use.com/)） |
| `FIRECRAWL_BROWSER_TTL` | Firecrawl 浏览器会话的有效期（秒为单位，默认：300 秒） |
| `BROWSER_CDP_URL` | 本地浏览器的 Chrome DevTools Protocol 地址（通过 `/browser connect` 设置，例如 `ws://localhost:9222`） |
| `CAMOFOX_URL` | Camofox 本地反检测浏览器地址（默认：`http://localhost:9377`） |
| `CAMOFOX_USER_ID` | 可选的外部管理的 Camofox 用户编号，用于共享可见会话 |
| `CAMOFOX_SESSION_KEY` | 为 `CAMOFOX_USER_ID` 创建标签页时使用的可选 Camofox 会话密钥 |
| `CAMOFOX_ADOPT_EXISTING_TAB` | 设置为 `true` 可在创建新标签页前复用现有的 Camofox 标签页 |
| `BROWSER_INACTIVITY_TIMEOUT` | 浏览器会话因无操作而自动关闭的超时时间（秒为单位） |
| `AGENT_BROWSER_ARGS` | 额外的 Chromium 启动参数（以逗号或换行分隔）。当在 root 权限下运行，或处于 AppArmor 限制的受限用户命名空间中（如 Ubuntu 23.10+、DGX Spark、许多容器镜像）时，Hermes 会自动注入 `--no-sandbox,--disable-dev-shm-usage` 参数；仅需手动设置此参数以覆盖或添加其他参数。 |
| `FAL_KEY` | 图像生成服务（[fal.ai](https://fal.ai/)） |
| `GROQ_API_KEY` | Groq Whisper 语音转文本 API 密钥（[groq.com](https://groq.com/)） |
| `ELEVENLABS_API_KEY` | ElevenLabs 高级文本转语音音色（[elevenlabs.io](https://elevenlabs.io/)） |
| `STT_GROQ_MODEL` | 覆盖 Groq 语音转文本模型（默认：`whisper-large-v3-turbo`） |
| `GROQ_BASE_URL` | 覆盖 Groq 兼容 OpenAI 的语音转文本接口地址 |
| `STT_OPENAI_MODEL` | 覆盖 OpenAI 语音转文本模型（默认：`whisper-1`） |
| `STT_OPENAI_BASE_URL` | 覆盖 OpenAI 兼容的语音转文本接口地址 |
| `GITHUB_TOKEN` | 用于 Skills Hub 的 GitHub 令牌（可提升 API 调用频率上限及支持技能发布功能） |
| `HONCHO_API_KEY` | 跨会话用户建模服务（[honcho.dev](https://honcho.dev/)） |
| `HONCHO_BASE_URL` | 自托管 Honcho 实例的基地址（默认为 Honcho 云服务）。本地实例无需 API 密钥。 |
| `HINDSIGHT_TIMEOUT` | Hindsight 记忆提供者 API 调用的超时时间（秒为单位，默认：`60` 秒）。若在执行 `/sync` 或 `on_session_switch` 操作时 Hindsight 实例响应缓慢，导致 `errors.log` 中出现超时错误，可提高此值。 |
| `SUPERMEMORY_API_KEY` | 支持基于语义的长期记忆功能，具备个人资料检索与会话数据导入能力（[supermemory.ai](https://supermemory.ai)） |
| `DAYTONA_API_KEY` | Daytona 云沙箱服务（[daytona.io](https://daytona.io/)） |

### Langfuse 可观测性功能

用于内置插件 [`observability/langfuse`](/user-guide/features/built-in-plugins#observabilitylangfuse) 的环境变量。需在 `~/.hermes/.env` 文件中设置这些变量。在它们生效之前，还需先启用该插件（执行 `hermes plugins enable observability/langfuse`，或通过 `hermes plugins` 界面勾选对应选项）。

| 变量 | 描述 |
|------|------|
| `HERMES_LANGFUSE_PUBLIC_KEY` | Langfuse 项目的公钥（格式为 `pk-lf-...`），为必填项。 |
| `HERMES_LANGFUSE_SECRET_KEY` | Langfuse 项目的私钥（格式为 `sk-lf-...`），为必填项。 |
| `HERMES_LANGFUSE_BASE_URL` | Langfuse 服务器地址（默认：`https://cloud.langfuse.com`），自托管环境可自行设置。 |
| `HERMES_LANGFUSE_ENV` | 请求追踪中的环境标签（如 `production`、`staging` 等）。 |
| `HERMES_LANGFUSE_RELEASE` | 请求追踪中的版本标签。 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | SDK 的采样率，范围为 0.0–1.0（默认：`1.0`）。 |
| `HERMES_LANGFUSE_MAX_CHARS` | 序列化后的请求载荷每字段的最大字符数（默认：`12000`）。 |
| `HERMES_LANGFUSE_DEBUG` | 设置为 `true` 可在 `agent.log` 文件中输出更详细的插件日志。 |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL` | 标准的 Langfuse SDK 参数名称。当未设置 `HERMES_LANGFUSE_*` 对应参数时，系统会自动使用这些标准名称作为备选。 |

### Nous 工具网关

这些变量用于配置付费 Nous 用户或自托管网关部署所使用的[工具网关](/user-guide/features/tool-gateway)。大多数用户无需设置这些参数——网关会通过 `hermes model` 或 `hermes tools` 自动配置。

| 变量 | 描述 |
|------|------|
| `TOOL_GATEWAY_DOMAIN` | 工具网关路由的基域名（默认：`nousresearch.com`）。 |
| `TOOL_GATEWAY_SCHEME` | 网关 URL 的协议类型，可选 HTTP 或 HTTPS（默认：`https`）。 |
| `TOOL_GATEWAY_USER_TOKEN` | 工具网关的认证令牌，通常会自动从 Nous 认证系统中获取。 |
| `FIRECRAWL_GATEWAY_URL` | 专门用于覆盖 Firecrawl 网关接口地址的参数。 |

## 终端后端

| 变量 | 描述 |
|------|------|
| `TERMINAL_ENV` | 后端类型：`local`、`docker`、`ssh`、`singularity`、`modal`、`daytona`。 |
| `HERMES_DOCKER_BINARY` | 覆盖 Hermes 调用的容器二进制文件路径（例如 `podman`、`/usr/local/bin/docker`）。若未设置，Hermes 会自动在 `PATH` 中查找 `docker` 或 `podman`。当两者均安装但希望使用非默认版本，或二进制文件不在 `PATH` 路径中时，需手动设置此参数。 |
| `TERMINAL_DOCKER_IMAGE` | Docker 镜像名称（默认：`nikolaik/python-nodejs:python3.11-nodejs20`）。 |
| `TERMINAL_DOCKER_FORWARD_ENV` | 需要显式转发到 Docker 终端会话中的环境变量名称的 JSON 数组。注意：技能中声明的 `required_environment_variables` 会自动被转发，此参数仅适用于未被任何技能声明的环境变量。 |
| `TERMINAL_DOCKER_VOLUMES` | 额外的 Docker 卷挂载配置（以逗号分隔的 `host:container` 对格式）。 |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | 高级可选功能：将启动目录挂载到 Docker 的 `/workspace` 目录中（`true`/`false`，默认：`false`）。 |
| `TERMINAL_SINGULARITY_IMAGE` | Singularity 镜像名称或 `.sif` 文件路径。 |
| `TERMINAL_MODAL_IMAGE` | Modal 容器镜像名称。 |
| `TERMINAL_DAYTONA_IMAGE` | Daytona 沙箱镜像名称。 |
| `TERMINAL_TIMEOUT` | 命令执行的超时时间（秒为单位）。 |
| `TERMINAL_LIFETIME_SECONDS` | 终端会话的最大运行时长（秒为单位）。 |
| `TERMINAL_CWD` | 已过时的直接覆盖参数，用于网关/定时任务终端会话。建议在 `config.yaml` 中使用 `terminal.cwd` 参数；CLI 仍会使用启动目录作为默认值。 |
| `SUDO_PASSWORD` | 允许无需交互式提示即可使用 sudo 权限。 |

对于云沙箱后端，数据持久化依赖于文件系统。`TERMINAL_LIFETIME_SECONDS` 参数用于控制 Hermes 在何时清理空闲的终端会话，后续重新启动时可能会创建新的沙箱环境，而非继续运行原有的进程。

## SSH 后端

| 变量 | 描述 |
|------|------|
| `TERMINAL_SSH_HOST` | 远程服务器的主机名。 |
| `TERMINAL_SSH_USER` | SSH 登录用户名。 |
| `TERMINAL_SSH_PORT` | SSH 端口（默认：22）。 |
| `TERMINAL_SSH_KEY` | 私钥文件的路径。 |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 的持久化 Shell 设置（默认值与 `TERMINAL_PERSISTENT_SHELL` 相同）。 |

## 容器资源（Docker、Singularity、Modal、Daytona）

| 变量 | 描述 |
|------|------|
| `TERMINAL_CONTAINER_CPU` | 容器可使用的 CPU 核心数（默认：1）。 |
| `TERMINAL_CONTAINER_MEMORY` | 容器可用内存大小（单位：MB，默认：5120 MB）。 |
| `TERMINAL_CONTAINER_DISK` | 容器可用磁盘空间（单位：MB，默认：51200 MB）。 |
| `TERMINAL_CONTAINER_PERSISTENT` | 是否在会话之间保持容器文件系统的持久性（默认：`true`）。 |
| `TERMINAL_SANDBOX_DIR` | 用于存储工作区及临时文件的宿主机目录路径（默认：`~/.hermes/sandboxes/`）。 |

## 持久化 Shell

| 变量 | 描述 |
|------|------|
| `TERMINAL_PERSISTENT_SHELL` | 为非本地后端启用持久化 Shell（默认：`true`）。也可通过 `config.yaml` 中的 `terminal.persistent_shell` 参数进行设置。 |
| `TERMINAL_LOCAL_PERSISTENT` | 为本地后端启用持久化 Shell（默认：`false`）。 |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 后端的持久化 Shell 设置（默认值与 `TERMINAL_PERSISTENT_SHELL` 相同）。 |

## 消息传递功能| 变量名 | 描述 |
|--------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram机器人令牌（从@BotFather获取） |
| `TELEGRAM_ALLOWED_USERS` | 允许使用该机器人的用户ID，以逗号分隔（适用于私信、群组及论坛） |
| `TELEGRAM_GROUP_ALLOWED_USERS` | 仅在群组/论坛中授权的发送者用户ID，以逗号分隔（**不授予私信访问权限**）。为兼容旧版配置（#17686之前），以“-”开头的聊天ID值仍会被视为有效聊天ID，但会发出弃用警告 |
| `TELEGRAM_GROUP_ALLOWED_CHATS` | 允许发送消息的群组/论坛聊天ID，以逗号分隔；该群组的任何成员均有权发送消息 |
| `TELEGRAM_HOME_CHANNEL` | 用于定时任务消息推送的默认Telegram聊天频道/频道名称 |
| `TELEGRAM_HOME_CHANNEL_NAME` | Telegram首页频道的显示名称 |
| `TELEGRAM_CRON_THREAD_ID` | 用于接收定时任务消息的论坛主题ID；仅针对定时任务，会覆盖`TELEGRAM_HOME_CHANNEL_THREAD_ID`设置。建议在主题模式下使用此参数，这样对定时消息的回复会打开新会话，而不会进入系统大厅（#24409） |
| `TELEGRAM_WEBHOOK_URL` | Webhook模式的公共HTTPS地址（可替代轮询方式发送消息） |
| `TELEGRAM_WEBHOOK_PORT` | Webhook服务器的本地监听端口（默认值为`8443`） |
| `TELEGRAM_WEBHOOK_SECRET` | Telegram在每次消息更新时返回的密钥，用于验证消息真实性。**一旦设置了`TELEGRAM_WEBHOOK_URL`，此参数为必填项**——否则网关将无法启动（GHSA-3vpc-7q5r-276h）。可通过`openssl rand -hex 32`命令生成该密钥 |
| `TELEGRAM_REACTIONS` | 在处理消息时启用表情符号反应功能（默认值为`false`） |
| `TELEGRAM_REQUIRE_MENTION` | 在Telegram群组中回复消息前，要求必须明确@提及机器人。相当于`config.yaml`中的`telegram.require_mention`设置 |
| `TELEGRAM_MENTION_PATTERNS` | 当启用Telegram群组@提及过滤功能时，允许的正则表达式触发词列表，格式可为JSON数组、换行分隔列表或逗号分隔列表。相当于`telegram.mention_patterns`设置 |
| `TELEGRAM_EXCLUSIVE_BOT_MENTIONS` | 启用后，在Telegram群组中，明确的`@...bot`提及会先被路由到对应的机器人用户名，之后才会执行回复或触发词处理逻辑。默认值为`true`。相当于`telegram.exclusive_bot_mentions`设置 |
| `TELEGRAM_REPLY_TO_MODE` | 回复时的引用方式：`off`、`first`（默认）或`all`，与Discord的规则一致 |
| `TELEGRAM_IGNORED_THREADS` | 机器人永远不会回复的Telegram论坛主题/线程ID，以逗号分隔 |
| `TELEGRAM_PROXY` | 用于连接Telegram的代理URL，可覆盖`HTTPS_PROXY`设置。支持`http://`、`https://`、`socks5://`格式 |
| `DISCORD_BOT_TOKEN` | Discord机器人令牌 |
| `DISCORD_ALLOWED_USERS` | 允许使用该机器人的Discord用户ID，以逗号分隔 |
| `DISCORD_ALLOWED_ROLES` | 允许使用该机器人的Discord角色ID，以逗号分隔（可与`DISCORD_ALLOWED_USERS`同时使用）。此设置会自动启用“成员”意图。当审核团队人员变动时非常有用，因为角色权限变更会自动生效 |
| `DISCORD_ALLOWED_CHANNELS` | 允许机器人发送消息的Discord频道ID，以逗号分隔。一旦设置，机器人将仅在这些频道（以及允许的私信）中回复消息，会覆盖`config.yaml`中的`discord.allowed_channels`设置 |
| `DISCORD_PROXY` | 用于连接Discord的代理URL，可覆盖`HTTPS_PROXY`设置。支持`http://`、`https://`、`socks5://`格式 |
| `DISCORD_HOME_CHANNEL` | 用于定时任务消息推送的默认Discord频道 |
| `DISCORD_HOME_CHANNEL_NAME` | Discord首页频道的显示名称 |
| `DISCORD_COMMAND_SYNC_POLICY` | Discord斜杠命令启动同步策略：`safe`（差异对比后再同步）、`bulk`（使用旧版的`tree.sync()`方式）或`off`（关闭同步） |
| `DISCORD_REQUIRE_MENTION` | 在服务器频道中回复消息前，要求必须进行@提及 |
| `DISCORD_FREE_RESPONSE_CHANNELS` | 不要求必须@提及即可发送回复的频道ID，以逗号分隔 |
| `DISCORD_AUTO_THREAD` | 当支持时，自动为长回复创建线程 |
| `DISCORD_ALLOW_ANY_ATTACHMENT` | 设置为`true`时，允许接收所有类型的附件（不仅限于默认支持的PDF、文本、ZIP、Office文档格式）。未知类型的附件会被缓存，并以本地路径的形式呈现给机器人，以便其通过`terminal`、`read_file`、`ffprobe`等功能进行查看。默认值为`false` |
| `DISCORD_MAX_ATTACHMENT_BYTES` | 网关缓存的单个附件的最大字节数。默认值为`33554432`（32兆字节）。设置为`0`则表示不设置上限（附件会在写入过程中保留在内存中） |
| `DISCORD_REACTIONS` | 在处理消息时启用表情符号反应功能（默认值为`true`） |
| `DISCORD_IGNORED_CHANNELS` | 机器人永远不会回复的Discord频道ID，以逗号分隔 |
| `DISCORD_NO_THREAD_CHANNELS` | 机器人发送回复时不会自动创建线程的频道ID，以逗号分隔 |
| `DISCORD_REPLY_TO_MODE` | 回复时的引用方式：`off`、`first`（默认）或`all`，与Discord规则一致 |
| `DISCORD_ALLOW_MENTION_EVERYONE` | 允许机器人向`@everyone`/`@here`发送消息（默认值为`false`）。详情请参阅[提及控制](../user-guide/messaging/discord.md#mention-control) |
| `DISCORD_ALLOW_MENTION_ROLES` | 允许机器人接收`@role`格式的提及（默认值为`false`） |
| `DISCORD_ALLOW_MENTION_USERS` | 允许机器人接收单个`@user`格式的提及（默认值为`true`） |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | 回复用户消息时，也向该用户发送回复（默认值为`true`） |
| `SLACK_BOT_TOKEN` | Slack机器人令牌（格式为`xoxb-...`） |
| `SLACK_APP_TOKEN` | Slack应用级令牌（格式为`xapp-...`，在Socket模式下为必填项） |
| `SLACK_ALLOWED_USERS` | 允许使用该机器人的Slack用户ID，以逗号分隔 |
| `SLACK_HOME_CHANNEL` | 用于定时任务消息推送的默认Slack频道 |
| `SLACK_HOME_CHANNEL_NAME` | Slack首页频道的显示名称 |
| `GOOGLE_CHAT_PROJECT_ID` | 托管Pub/Sub主题的GCP项目编号（如需备用，可使用`GOOGLE_CLOUD_PROJECT`） |
| `GOOGLE_CHAT_SUBSCRIPTION_NAME` | 完整的Pub/Sub订阅路径，格式为`projects/{proj}/subscriptions/{sub}`（旧版别名為`GOOGLE_CHAT_SUBSCRIPTION`） |
| `GOOGLE_CHAT_SERVICE_ACCOUNT_JSON` | 服务账户JSON文件的路径，或直接在此处填写JSON内容（如需备用，可使用`GOOGLE_APPLICATION_CREDENTIALS`） |
| `GOOGLE_CHAT_ALLOWED_USERS` | 允许与机器人聊天的用户邮箱地址，以逗号分隔 |
| `GOOGLE_CHAT_ALLOW_ALL_USERS` | 允许所有Google Chat用户触发机器人功能（仅开发人员可用） |
| `GOOGLE_CHAT_HOME_CHANNEL` | 用于定时任务消息推送的默认Google Chat空间编号（例如`spaces/AAAA...`） |
| `GOOGLE_CHAT_HOME_CHANNEL_NAME` | Google Chat首页空间的显示名称 |
| `GOOGLE_CHAT_MAX_MESSAGES` | Pub/Sub FlowControl机制允许的正在处理中的最大消息数（默认值为`1`） |
| `GOOGLE_CHAT_MAX_BYTES` | Pub/Sub FlowControl机制允许的正在处理中的最大字节数（默认值为`16777216`，即16兆字节） |
| `GOOGLE_CHAT_BOOTSTRAP_SPACES` | 启动时用于探测的额外空间编号，以便确定机器人自身的`users/{id}`信息 |### Web控制台与Hermes Desktop

用于[Web控制台](/user-guide/features/web-dashboard)的认证，以及实现[Hermes Desktop与远程后端连接](/user-guide/features/web-dashboard#connecting-hermes-desktop-to-a-remote-backend)。遵循“仅使用密钥”的原则，凭证应存储在`~/.hermes/.env`文件中；而OAuth的`client_id`则建议设置在`config.yaml`的`dashboard.oauth`字段下（若同时设置，环境变量优先生效）。

系统预置了三种控制台认证提供程序。对于远程Hermes Desktop连接或任何面向互联网的控制台，推荐的提供程序是**OAuth（Nous Portal）**——需设置`HERMES_DASHBOARD_OAUTH_CLIENT_ID`（可通过`hermes dashboard register`命令进行配置）。内置的**用户名/密码**提供程序（`HERMES_DASHBOARD_BASIC_AUTH_*`）适用于位于可信局域网或VPN后的后端，是最快的解决方案，但不适合直接暴露在公共互联网上。若要使用自建的身份验证服务，可使用**自托管OIDC**提供程序（`HERMES_DASHBOARD_OIDC_*`）。无论采用哪种方式，只要设置非回环绑定地址（如`hermes dashboard --host 0.0.0.0`），就会启用认证网关。详情请参阅[Web控制台 → 认证](/user-guide/features/web-dashboard#authentication-gated-mode)。

| 变量 | 描述 |
|------|------|
| `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` | 内置用户名/密码认证提供程序（`plugins/dashboard_auth/basic`）的用户名。当该变量与密码一同设置时，即可激活该提供程序，同时会覆盖`dashboard.basic_auth.username`的值。 |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | 该基础认证提供程序的明文密码（加载时会以哈希形式存储在内存中）。其优先级高于配置文件中的`password_hash`字段，因此可通过环境变量方便地更换密码，同时会覆盖`dashboard.basic_auth.password`的值。 |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` | 该基础认证提供程序的scrypt哈希密码（更推荐，因为不会以明文形式存储）。可通过命令`python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"`生成，同时会覆盖`dashboard.basic_auth.password_hash`的值。 |
| `HERMES_DASHBOARD_BASIC_AUTH_SECRET` | 用于为该基础认证提供程序的无状态会话令牌签名 的HMAC密钥（长度需大于32字节，支持base64、hex或原始格式）。明确设置此值可确保会话在重启后依然有效，或跨多个工作进程使用；若留空，则会为每个进程随机生成密钥（此时每次重启都会导致用户登出），同时会覆盖`dashboard.basic_auth.secret`的值。 |
| `HERMES_DASHBOARD_BASIC_AUTH_TTL_SECONDS` | 该基础认证提供程序的访问令牌有效期（默认为12小时），同时会覆盖`dashboard.basic_auth.session_ttl_seconds`的值。 |
| `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | 用于受保护/公共控制台的OAuth客户端ID（格式为`agent:{instance_id}`），可激活Nous提供程序（`plugins/dashboard_auth/nous`），同时会覆盖`dashboard.oauth.client_id`的值。需通过`hermes dashboard register`命令进行配置。 |
| `HERMES_DASHBOARD_PUBLIC_URL` | 控制台的完整公共URL地址，用于在反向代理后构建OAuth回调地址，同时会覆盖`dashboard.public_url`的值。 |
| `HERMES_DASHBOARD_OIDC_ISSUER` | 内置自托管OIDC提供程序（`plugins/dashboard_auth/self_hosted`）的OIDC发行方URL，激活该提供程序时必须设置此值，同时会覆盖`dashboard.oauth.self_hosted.issuer`的值。 |
| `HERMES_DASHBOARD_OIDC_CLIENT_ID` | 自托管OIDC提供程序的公共OIDC客户端ID（支持授权码模式和PKCE机制），激活该提供程序时必须设置此值，同时会覆盖`dashboard.oauth.self_hosted.client_id`的值。 |
| `HERMES_DASHBOARD_OIDC_SCOPES` | 自托管OIDC提供程序所请求的OIDC作用域（默认为`openid profile email`），同时会覆盖`dashboard.oauth.self_hosted.scopes`的值。 |
| `HERMES_DESKTOP_REMOTE_URL` | （桌面端）远程后端的基URL地址，例如`http://host:9119`。设置此值后会覆盖应用内的网关URL；用户仍需通过网关设置面板进行登录（可选择OAuth重定向或用户名/密码认证，具体取决于后端支持的认证方式）。 |
| `HERMES_DESKTOP_HERMES` | 桌面端后端命令的覆盖值，打包工具或Nix环境以及故障排查时使用，用于在探测到后端后指定给Electron进程的特定`hermes`可执行文件路径。 |
| `HERMES_DESKTOP_HERMES_ROOT` | 桌面端源代码检出路径的覆盖值，由`hermes desktop --hermes-root`命令使用，在首次启动时或系统`PATH`环境中已存在`hermes`可执行文件之前会优先检查此路径。 |
| `HERMES_DESKTOP_IGNORE_EXISTING` | 设置为`1`时，桌面端在确定后端地址时会忽略系统`PATH`环境中的现有`hermes`可执行文件，功能等同于`hermes desktop --ignore-existing`命令。 |
| `HERMES_DESKTOP_CWD` | 桌面端聊天会话的初始项目目录，可通过`hermes desktop --cwd`命令进行设置。 |

### Microsoft Graph（Teams会议）

用于即将推出的Teams会议摘要处理流程中Microsoft Graph REST客户端的仅应用专用凭证。有关Azure门户的操作指南及所需的精确API权限，请参阅[注册Microsoft Graph应用](/guides/microsoft-graph-app-registration)。

| 变量 | 描述 |
|------|------|
| `MSGRAPH_TENANT_ID` | Graph应用注册所对应的Azure AD租户ID（即目录GUID）。 |
| `MSGRAPH_CLIENT_ID` | Azure应用注册对应的应用程序（客户端）ID。 |
| `MSGRAPH_CLIENT_SECRET` | 该应用注册对应的客户端密钥，应存储在`~/.hermes/.env`文件中，并设置权限为`chmod 600`；需定期通过Azure门户更换此密钥。 |
| `MSGRAPH_SCOPE` | 用于客户端凭证令牌请求的OAuth2作用域（默认值为`https://graph.microsoft.com/.default`）。 |
| `MSGRAPH_AUTHORITY_URL` | Microsoft身份平台的服务地址（默认值为`https://login.microsoftonline.com`），仅在国家/主权云环境中需要修改此值（例如GCC High区域需使用`https://login.microsoftonline.us`）。 |

### Microsoft Graph Webhook监听器

用于接收Graph事件（如Teams会议、日历事件、聊天消息等）的入站变更通知。有关设置及安全强化措施，请参阅[Microsoft Graph Webhook监听器](/user-guide/messaging/msgraph-webhook)。

| 变量 | 描述 |
|------|------|
| `MSGRAPH_WEBHOOK_ENABLED` | 是否启用`msgraph_webhook`网关平台，取值为`true`、`1`或`yes`。 |
| `MSGRAPH_WEBHOOK_PORT` | 监听器绑定的端口，默认值为`8646`。 |
| `MSGRAPH_WEBHOOK_CLIENT_STATE` | Graph会在每条通知中回传的共享密钥，用于通过`hmac.compare_digest`函数进行验证，可通过命令`openssl rand -hex 32`生成该密钥。 |
| `MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES` | 以逗号分隔的Graph资源路径/模式允许列表（例如`communications/onlineMeetings,chats/*/messages`），末尾的`*`表示前缀匹配，若留空则表示允许所有资源。 |
| `MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS` | 以逗号分隔的CIDR范围列表，仅允许来自这些范围的请求发送到监听器（例如`52.96.0.0/14,52.104.0.0/14`），若留空则表示允许所有来源（为默认值）。在生产环境中应限制为Microsoft Graph官方公布的出站访问范围。 |

### Teams会议摘要发送

仅当启用了[`teams_pipeline`插件](/user-guide/messaging/msgraph-webhook)时才会使用该功能。相关设置也可通过`config.yaml`文件中的`platforms.teams.extra`字段进行配置——若同时设置了环境变量，则环境变量优先生效。详情请参阅[Microsoft Teams → 会议摘要发送](/user-guide/messaging/teams#meeting-summary-delivery-teams-meeting-pipeline)。

| 变量 | 描述 |
|------|------|
| `TEAMS_DELIVERY_MODE` | 发送模式，可选值为`graph`或`incoming_webhook`。 |
| `TEAMS_INCOMING_WEBHOOK_URL` | Teams生成的Webhook URL地址，当`TEAMS_DELIVERY_MODE`设置为`incoming_webhook`时必需。 |
| `TEAMS_GRAPH_ACCESS_TOKEN` | 用于Graph数据发送的预获取委托访问令牌，一般情况下并不需要使用；若未设置此值，系统会回退到使用`MSGRAPH_*`系列的应用专用凭证。 |
| `TEAMS_TEAM_ID` | 用于频道发送的目标团队ID（适用于`graph`模式）。 |
| `TEAMS_CHANNEL_ID` | 目标频道ID，需与`TEAMS_TEAM_ID`配对使用。 |
| `TEAMS_CHAT_ID` | 目标一对一或群组聊天的ID（在`graph`模式下可作为团队+频道的替代选项）。 |

### LINE消息API

由内置的LINE平台插件（`plugins/platforms/line/`）所使用。有关完整设置流程，请参阅[消息网关 → LINE](/user-guide/messaging/line)。

| 变量 | 描述 |
|------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | 来自LINE开发者控制台（消息API选项卡）的长期有效频道访问令牌，为必需项。 |
| `LINE_CHANNEL_SECRET` | 频道密钥，位于基本设置选项卡中，用于通过HMAC-SHA256算法对Webhook签名进行验证，为必需项。 |
| `LINE_HOST` | Webhook绑定的主机地址，默认值为`0.0.0.0`。 |
| `LINE_PORT` | Webhook绑定的端口，默认值为`8646`。 |
| `LINE_PUBLIC_URL` | 公共HTTPS基础URL地址（例如`https://my-tunnel.example.com`），用于发送图片、音频或视频文件——LINE仅接受可通过HTTPS访问的URL地址。 |
| `LINE_ALLOWED_USERS` | 以逗号分隔的允许向机器人发送私信的用户ID，用户ID前需加上`U`前缀。 |
| `LINE_ALLOWED_GROUPS` | 以逗号分隔的机器人将回复消息的群组ID，群组ID前需加上`C`前缀。 |
| `LINE_ALLOWED_ROOMS` | 以逗号分隔的机器人将回复消息的房间ID，房间ID前需加上`R`前缀。 |
| `LINE_ALLOW_ALL_USERS` | 仅开发人员可使用，表示允许来自任何来源的请求，默认值为`false`。 |
| `LINE_HOME_CHANNEL` | 当使用`deliver: line`指令通过定时任务发送消息时，默认的目标发送频道。 |
| `LINE_SLOW_RESPONSE_THRESHOLD` | 在触发慢响应LLM模板按钮的回调之前等待的秒数，默认值为`45`。将此值设置为`0`可禁用该功能，始终强制使用推送式回复。 |
| `LINE_PENDING_TEXT` | 显示在回调按钮旁边的提示文本。 |
| `LINE_BUTTON_LABEL` | 回调按钮的显示标签，默认值为`Get answer`。 |
| `LINE_DELIVERED_TEXT` | 当用户再次点击已发送过的回调消息时显示的回复文本，默认值为`Already replied ✅`。 |
| `LINE_INTERRUPTED_TEXT` | 当用户点击被标记为 `/stop` 的异常回调按钮时显示的回复文本，默认值为`Run was interrupted before completion.`。 |

### ntfy（推送通知）

[ntfy](https://ntfy.sh/)是一款轻量级的基于HTTP的推送通知服务。可通过[ntfy移动应用](https://ntfy.sh/docs/subscribe/phone/)订阅某个主题，向该主题发送消息即可与智能体进行交互。

| 变量 | 描述 |
|------|------|
| `NTFY_TOPIC` | 需要订阅的主题地址（用于接收新消息），为必需项。 |
| `NTFY_SERVER_URL` | 服务器URL地址，默认值为`https://ntfy.sh`，如需保障隐私，可指向自托管的ntfy服务。 |
| `NTFY_TOKEN` | 可选的认证令牌，可以是Bearer令牌（格式为`tk_xyz`），也可以是用于基本认证的`user:pass`格式凭证。 |
| `NTFY_PUBLISH_TOPIC` | 用于发送回复消息的主题地址，默认值为`NTFY_TOPIC`。 |
| `NTFY_MARKDOWN` | 设置为`true`时，回复消息会附带`X-Markdown: true`头部，允许使用Markdown格式，默认值为`false`。 |
| `NTFY_ALLOWED_USERS` | 允许发送消息的用户列表，这些值被视为用户ID；在ntfy系统中实际上对应的是主题名称，通常该值与`NTFY_TOPIC`相同。 |
| `NTFY_ALLOW_ALL_USERS` | 仅开发人员可使用，表示允许向所有用户发送消息，但仅能在访问受控的私有主题中使用，默认值为`false`。 |
| `NTFY_HOME_CHANNEL` | 当使用`deliver: ntfy`指令通过定时任务发送消息时，默认的目标发送频道。 |
| `NTFY_HOME_CHANNEL_NAME` | 该默认发送频道的显示名称，通常与主题名称相同。 |

在将不受信任的主题用于生产环境之前，请先仔细阅读[ntfy消息指南](/user-guide/messaging/ntfy)，尤其是**身份模型**相关章节。

### 高级消息配置调优用于控制出站消息批量处理功能的各平台高级配置项。大多数用户无需调整这些参数；系统默认设置已能确保在不过度降低性能的前提下遵守各平台的速率限制。

| 参数名 | 描述 |
|--------|------|
| `HERMES_TELEGRAM_TEXT_BATCH_DELAY_SECONDS` | 清除队列中的 Telegram 文本消息块之前的缓冲时间（默认值：`0.6` 秒）。 |
| `HERMES_TELEGRAM_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 当单条 Telegram 消息长度超出限制时，分割消息块之间的延迟时间（默认值：`2.0` 秒）。 |
| `HERMES_TELEGRAM_MEDIA_BATCH_DELAY_SECONDS` | 清除队列中的 Telegram 媒体文件之前的缓冲时间（默认值：`0.6` 秒）。 |
| `HERMES_TELEGRAM_FOLLOWUP_GRACE_SECONDS` | 在智能体处理完成后发送后续消息前的延迟时间，以避免与最后一条消息块的处理发生冲突。 |
| `HERMES_TELEGRAM_HTTP_CONNECT_TIMEOUT` / `_READ_TIMEOUT` / `_WRITE_TIMEOUT` / `_POOL_TIMEOUT` | 覆盖底层的 `python-telegram-bot` HTTP 相关超时时间（单位：秒）。 |
| `HERMES_TELEGRAM_HTTP_POOL_SIZE` | 连接到 Telegram API 的最大并发 HTTP 连接数。 |
| `HERMES_TELEGRAM_DISABLE_FALLBACK_IPS` | 禁用在 DNS 解析失败时使用的硬编码 Cloudflare 备用 IP 地址（取值：`true`/`false`）。 |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | 清除队列中的 Discord 文本消息块之前的缓冲时间（默认值：`0.6` 秒）。 |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | 当 Discord 消息长度超出限制时，分割消息块之间的延迟时间（默认值：`2.0` 秒）。 |
| `HERMES_MATRIX_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` | Matrix 平台的对应批量处理配置项。 |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` / `_MAX_CHARS` / `_MAX_MESSAGES` | Feishu 平台的批量处理参数——包括延迟时间、分割延迟、单条消息的最大字符数以及每批消息的最大数量。 |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | Feishu 平台的媒体文件清除延迟时间。 |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | Feishu webhook 冗余检测缓存的大小（默认值：`1024`）。 |
| `HERMES_WECOM_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` | WeCom 平台的批量处理配置项。 |
| `HERMES_VISION_DOWNLOAD_TIMEOUT` | 在将图像传递给视觉分析模型之前，下载该图像的超时时间（单位：秒，默认值：`30`）。 |
| `HERMES_RESTART_DRAIN_TIMEOUT` | 网关功能：在强制重启之前，等待正在运行的任务完成的时间长度（单位：秒，默认值：`900`）。 |
| `HERMES_GATEWAY_PLATFORM_CONNECT_TIMEOUT` | 网关启动时针对不同平台的连接超时时间（单位：秒）。 |
| `HERMES_GATEWAY_BUSY_INPUT_MODE` | 网关在处理任务繁忙时的默认输入处理方式：`queue`、`steer` 或 `interrupt`。可通过 `/busy` 命令针对特定聊天单独设置。 |
| `HERMES_GATEWAY_BUSY_ACK_ENABLED` | 当用户在智能体忙碌时发送输入信息，网关是否会发送确认消息（⚡/⏳/⏩）（默认值：`true`）。设置为 `false` 可完全隐藏这些消息——输入信息仍会按常规方式被排队、引导或中断处理，仅不会显示聊天回复的确认状态。该参数继承自 `config.yaml` 文件中的 `display.busy_ack_enabled` 设置。 |
| `HERMES_GATEWAY_NO_SUPERVISE` | 在 s6-overlay Docker 镜像中使用时，运行 `hermes gateway run` 命令时可选择关闭自动监控功能，从而使用 s6 之前的前台进程模式（无自动重启功能，网关成为容器的主进程）。有效值为：`1`、`true`、`yes`。该参数相当于 CLI 中的 `--no-supervise` 选项。在非 s6 镜像环境中此参数无效。 |
| `HERMES_GATEWAY_BOOTSTRAP_STATE` | 在 s6-overlay Docker 镜像中使用时，用于指定新卷上网关的**初始**监控状态。由于空白卷上不存在持久化的 `gateway_state.json` 文件，因此启动时协调器会创建 `gateway-default` 名称的配置项，但将其状态设置为**关闭**（仅当上次记录的状态为“运行中”时才会自动启动）。将此参数设置为 `running` 后，首次启动时的设置钩子会在协调器运行之前生成 `gateway_state.json` 文件，从而使网关在首次启动时就处于运行状态。仅接受字符串值 `running`。该功能仅在首次启动时生效：已存在的 `gateway_state.json` 文件不会被覆盖，因此手动停止的网关在重启后仍会保持停止状态。在非 s6 镜像环境中此参数无效。 |
| `GATEWAY_RELAY_URL` | 实验性的中继连接器 WebSocket 基础地址。设置该参数后，网关会注册通用的 `relay` 适配器，并向外连接该中继服务。该参数对应 `config.yaml` 文件中的 `gateway.relay_url`。 |
| `GATEWAY_RELAY_ID` | 由 `hermes gateway enroll` 命令分配或通过自主配置管理的中继网关标识符。该参数对应 `gateway.relay_id`。 |
| `GATEWAY_RELAY_SECRET` | 用于验证 WebSocket 连接的、针对每个网关的唯一密钥。如果已配置此密钥，则无需进行自主配置管理。该参数对应 `gateway.relay_secret`。 |
| `GATEWAY_RELAY_DELIVERY_KEY` | 由中继服务生成的交付密钥，用于确保兼容中继/直通模式下的身份验证机制。目前的中继服务入站消息是通过出站 WebSocket 而非网关端的 HTTP 接收器传递的。 |
| `GATEWAY_RELAY_ENROLL_TOKEN` | 当未明确指定 `--token` 参数时，`hermes gateway enroll` 命令会使用的注册令牌。 |
| `GATEWAY_RELAY_PLATFORM` | 中继功能描述中可选的平台名称。 |
| `GATEWAY_RELAY_BOT_ID` | 中继功能描述中可选的机器人标识符。 |
| `GATEWAY_RELAY_ENDPOINT` | 针对需要回调/直通 URL 的连接器模式而可选的网关端点地址；对于默认的仅支持 WebSocket 的入站中继路径而言并非必需。该参数对应 `gateway.relay_endpoint`。 |
| `GATEWAY_RELAY_ROUTE_KEYS` | 向连接器公布的、以逗号分隔的中继路由键值对。该参数对应 `gateway.relay_route_keys`。 |
| `HERMES_FILE_MUTATION_VERIFIER` | 是否启用每轮对话的文件修改验证功能（默认值：`true`）。启用该功能后，Hermes 会在对话记录中附加提示信息，列出本轮对话中所有失败且未被后续成功写入操作覆盖的 `write_file`/`patch` 操作。如需禁用此功能，可将其设置为 `0`、`false`、`no` 或 `off`。该参数对应 `config.yaml` 文件中的 `display.file_mutation_verifier`；如果环境变量已设置，则以环境变量值为准。 |
| `HERMES_CRON_TIMEOUT` | 定时任务智能体运行时的空闲超时时间（单位：秒，默认值：`600`）。只要智能体仍在主动调用工具或接收流式数据，就可以无限期运行——只有处于空闲状态时才会触发超时。设置为 `0` 表示无超时限制。 |
| `HERMES_CRON_SCRIPT_TIMEOUT` | 附加在定时任务前的预执行脚本的超时时间（单位：秒，默认值：`120`）。对于需要更长时间执行的脚本（例如为防止机器人检测而设置的随机延迟），可调整此参数。该参数也可通过 `config.yaml` 文件中的 `cron.script_timeout_seconds` 进行配置。 |
| `HERMES_CRON_MAX_PARALLEL` | 每个时间间隔内最多可同时运行的定时任务数量（默认值：`4`）。 |

## 智能体行为| 变量名 | 描述 |
|--------|------|
| `HERMES_MAX_ITERATIONS` | 每次对话中调用工具的最大迭代次数（默认值：90） |
| `HERMES_INFERENCE_MODEL` | 在进程层面强制指定模型名称（对该会话而言，其优先级高于 `config.yaml` 中的设置）。也可通过 `-m`/`--model` 参数进行设置。 |
| `HERMES_YOLO_MODE` | 设定为 `1` 可绕过危险命令的审批提示。相当于 `--yolo` 参数。 |
| `HERMES_ACCEPT_HOOKS` | 在无终端提示的情况下，自动批准 `config.yaml` 中声明的所有未见过的全局 shell 钩子。相当于 `--accept-hooks` 或 `hooks_auto_accept: true`。 |
| `HERMES_IGNORE_USER_CONFIG` | 跳过 `~/.hermes/config.yaml` 文件，使用内置默认设置（但 `.env` 文件中的凭据仍会被加载）。相当于 `--ignore-user-config`。 |
| `HERMES_IGNORE_RULES` | 跳过自动注入的 `AGENTS.md`、`SOUL.md`、`.cursorrules` 文件、内存内容以及预加载的技能。相当于 `--ignore-rules`。 |
| `HERMES_SAFE_MODE` | 故障排查模式：禁用所有自定义设置——跳过插件发现及 MCP 服务器加载流程。该模式会由 `--safe-mode` 参数自动启用（同时也会设置上述两个参数）。 |
| `HERMES_MD_NAMES` | 以逗号分隔的规则文件名列表，系统将自动注入这些文件（默认值：`AGENTS.md,CLAUDE.md,.cursorrules,SOUL.md`）。 |
| `HERMES_TOOL_PROGRESS` | 用于显示工具处理进度的过时兼容性变量。建议在 `config.yaml` 中使用 `display.tool_progress`。 |
| `HERMES_TOOL_PROGRESS_MODE` | 用于控制工具进度显示模式的过时兼容性变量。建议在 `config.yaml` 中使用 `display.tool_progress`。 |
| `HERMES_HUMAN_DELAY_MODE` | 响应节奏控制：`off`/`natural`/`custom` |
| `HERMES_HUMAN_DELAY_MIN_MS` | 自定义延迟范围的最小值（单位：毫秒） |
| `HERMES_HUMAN_DELAY_MAX_MS` | 自定义延迟范围的最大值（单位：毫秒） |
| `HERMES_QUIET` | 是否抑制非必要输出（`true`/`false`） |
| `CODEX_HOME` | 当启用 [Codex 应用服务器运行时环境](../user-guide/features/codex-app-server-runtime) 时，用于指定 Codex CLI 读取配置及认证信息的目录路径（默认值：`~/.codex`）。Hermes 的迁移功能会将相关配置写入 `<CODEX_HOME>/config.toml` 文件中。 |
| `HERMES_KANBAN_TASK` | 由看板调度器在启动工作进程时设置的任务 UUID。各个工作进程以及由此生成的 `hermes-tools` MCP 子进程都会继承该值，以便看板工具能够正确进行权限控制。请勿手动设置此值。 |
| `HERMES_API_TIMEOUT` | LLM API 调用的超时时间（单位：秒）（默认值：`1800`） |
| `HERMES_API_CALL_STALE_TIMEOUT` | 非流式调用中的旧请求超时时间（单位：秒）（默认值：`90`）。若未设置该值，本地提供商将自动禁用此功能；对于上下文规模极大的场景，该超时时间也可能会相应增加。同样可在 `config.yaml` 中通过 `providers.<id>.stale_timeout_seconds` 或 `providers.<id>.models.<model>.stale_timeout_seconds` 参数进行配置。 |
| `HERMES_STREAM_READ_TIMEOUT` | 流式套接字读取的超时时间（单位：秒）（默认值：`120`）。对于本地提供商，该值会自动调整为 `HERMES_API_TIMEOUT`。如果在长时间代码生成过程中出现本地 LLM 超时情况，可适当提高此值。 |
| `HERMES_STREAM_STALE_TIMEOUT` | 检测流式数据过时的超时时间（单位：秒）（默认值：`180`）。本地提供商将自动禁用此功能。若在该时间段内没有新的数据块到达，系统会主动断开连接。 |
| `HERMES_STREAM_RETRIES` | 遇到短暂网络故障时，在流式通信过程中尝试重新连接的次数（默认值：`3`）。 |
| `HERMES_AGENT_TIMEOUT` | 运行中的智能体处于非活跃状态时的超时时间（单位：秒）（默认值：`1800`，即 30 分钟）。每次调用工具或处理流式数据时，该计时器都会重置。将其设为 `0` 可禁用此功能。 |
| `HERMES_AGENT_TIMEOUT_WARNING` | 当智能体处于非活跃状态达到指定时间后，网关会发送警告信息（默认值为 `HERMES_AGENT_TIMEOUT` 的 75%）。 |
| `HERMES_AGENT_NOTIFY_INTERVAL` | 对于长时间运行的智能体轮次，网关在发送进度通知之间的间隔时间（单位：秒）。 |
| `HERMES_CHECKPOINT_TIMEOUT` | 创建文件系统检查点的超时时间（单位：秒）（默认值：`30`）。 |
| `HERMES_EXEC_ASK` | 在网关模式下是否启用执行操作前的审批提示（`true`/`false`）。 |
| `HERMES_ENABLE_PROJECT_PLUGINS` | 是否允许智能体加载器及控制台 Web 服务器自动发现位于 `./.hermes/plugins/` 目录中的项目级插件。该参数接受所有表示“真”的值：`1` / `true` / `yes` / `on`（不区分大小写）。其余所有值——包括 `0`、`false`、`no`、`off` 以及空字符串——均视为**禁用**状态（默认值）。注意：从 GHSA-5qr3-c538-wm9j (#29156) 版本开始，即使启用了此参数，控制台 Web 服务器仍不会自动导入项目插件的 Python `api` 文件——项目插件虽然可以通过静态 JS/CSS 扩展界面功能，但其后台路由仅当被放置在 `~/.hermes/plugins/` 目录下时才会被加载。 |
| `HERMES_PLUGINS_DEBUG` | 设定为 `1`/`true` 可在标准错误流中输出详细的插件发现过程日志——包括扫描的目录、解析的清单文件、跳过某些文件的理由，以及解析或 `register()` 操作失败时的完整堆栈跟踪信息。该功能主要面向插件开发者。 |
| `HERMES_BACKGROUND_NOTIFICATIONS` | 网关模式下的后台进程通知方式：`all`（默认）、`result`、`error`、`off`。 |
| `HERMES_EPHEMERAL_SYSTEM_PROMPT` | 在调用 API 时注入的临时系统提示语——此类提示语不会被保存到会话记录中。 |
| `HERMES_PREFILL_MESSAGES_FILE` | 包含临时预填提示语的 JSON 文件路径，这些提示语会在调用 API 时被注入。 |
| `HERMES_ALLOW_PRIVATE_URLS` | `true`/`false`——决定是否允许工具访问本地主机或私有网络中的 URL。在网关模式下默认为关闭状态。 |
| `HERMES_REDACT_SECRETS` | `true`/`false`——控制是否在工具输出、日志及聊天回复中隐藏敏感信息（默认值：`true`）。 |
| `HERMES_WRITE_SAFE_ROOT` | 可选目录前缀，用于限制 `write_file`/`patch` 操作的写入范围；位于该前缀之外的路径将需要额外审批才能写入。 |
| `HERMES_DISABLE_LAZY_INSTALLS` | 官方 Docker 镜像中自动设置的内部桥接变量，旨在防止在不可变的 `/opt/hermes` 目录树中安装运行时依赖项。在用户配置文件 `config.yaml` 中，对应的设置值为 `security.allow_lazy_installs: false`；请勿在 `.env` 文件中设置此参数。 |
| `HERMES_DISABLE_FILE_STATE_GUARD` | 设定为 `1` 可关闭 `patch`/`write_file` 操作中的“自上次读取后文件已被修改”检测功能。 |
| `HERMES_CORE_TOOLS` | 以逗号分隔的形式用于覆盖标准的核心工具列表（高级用法，很少需要）。 |
| `HERMES_BUNDLED_SKILLS` | 以逗号分隔的形式用于覆盖启动时自动加载的预装技能列表。 |
| `HERMES_OPTIONAL_SKILLS` | 以逗号分隔的列表形式，列出首次运行时应自动安装的可选技能名称。 |
| `HERMES_DEBUG_INTERRUPT` | 设定为 `1` 可将详细的中断/取消操作跟踪信息记录到 `agent.log` 文件中。 |
| `HERMES_DUMP_REQUESTS` | 是否将 API 请求的载荷内容输出到日志文件中（`true`/`false`）。 |
| `HERMES_DUMP_REQUEST_STDOUT` | 将 API 请求的载荷内容直接输出到标准输出流，而非日志文件。 |
| `HERMES_OAUTH_TRACE` | 设定为 `1` 可记录 OAuth 令牌的获取及刷新尝试过程，同时会包含经过脱敏处理的计时信息。 |
| `HERMES_OAUTH_FILE` | 用于指定存储 OAuth 凭据的文件路径（默认值：`~/.hermes/auth.json`）。 |
| `HERMES_AGENT_HELP_GUIDANCE` | 为自定义部署场景在系统提示语中追加额外的使用指南文本。 |
| `HERMES_AGENT_LOGO` | 用于在 CLI 启动时替换默认的 ASCII 标语徽标。 |
| `DELEGATION_MAX_CONCURRENT_CHILDREN` | 每批 `delegate_task` 请求允许的最大并行子智能体数量（默认值：`3`，下限为 1，无上限）。同样可在 `config.yaml` 中通过 `delegation.max_concurrent_children` 参数进行设置——配置文件中的值具有优先级。 |

## 界面相关设置

| 变量名 | 描述 |
|--------|------|
| `HERMES_TUI` | 当其值为 `1` 时，将启动 [TUI](../user-guide/tui.md) 界面，而非传统的命令行界面。相当于传递了 `--tui` 参数。 |
| `HERMES_TUI_DIR` | 预编译好的 `ui-tui/` 目录的路径（该目录必须包含 `dist/entry.js` 文件以及完整的 `node_modules` 依赖包）。发行版及 Nix 构建工具会使用此路径来跳过首次启动时的 `npm install` 操作。 |
| `HERMES_TUI_RESUME` | 启动时根据标识符恢复特定的 TUI 会话。一旦设置了该参数，执行 `hermes --tui` 命令时将不会新建会话，而是直接继续使用指定的会话——这在连接中断或终端崩溃后重新连接时非常有用。 |
| `HERMES_TUI_THEME` | 强制指定 TUI 的颜色主题：`light`、`dark`，或直接输入 6 位十六进制值表示背景色（例如 `ffffff` 或 `1a1a2e`）。若未设置该参数，Hermes 会通过查询 `COLORFGBG` 及终端背景色自动选择主题；而当终端未设置 `COLORFGBG` 参数时，此变量可覆盖自动检测结果。 |
| `HERMES_INFERENCE_MODEL` | 在不修改 `config.yaml` 的情况下，强制指定 `hermes -z` / `hermes chat` 命令所使用的模型。该参数需与 `--provider` 参数配合使用。对于需要每次运行时都指定不同默认模型的脚本化调用场景（如自动化扫描工具、CI 环境、批量处理脚本等），此功能非常实用。 |

## 会话设置

| 变量名 | 描述 |
|--------|------|
| `SESSION_IDLE_MINUTES` | 智能体处于非活跃状态达到指定分钟数后自动重置会话（默认值：1440 分钟，即 24 小时）。 |
| `SESSION_RESET_HOUR` | 每日会话重置的时间，采用 24 小时制表示（默认值：4，即凌晨 4 点）。 |
| `HERMES_SESSION_ID` | **会自动被嵌入到 Hermes 启动的每一个工具子进程**中——包括 `terminal`、`execute_code`、持久化终端会话、Docker/Singularity 后端环境以及派生的子智能体进程。智能体会将当前会话 ID 设置为此值；从工具中调用的用户脚本也可以读取该值，从而将其输出结果、监控数据或产生的副作用与对应的 Hermes 会话关联起来。**不建议手动设置此值**——从父终端覆盖设置的值仅在非智能体运行模式下有效，且一旦智能体开始新的会话，该覆盖值就会被立即替换。 |

## 上下文压缩（仅适用于 `config.yaml`）

上下文压缩功能完全通过 `config.yaml` 文件进行配置——不存在相应的环境变量。阈值相关设置位于 `compression:` 块中，而摘要生成模型及提供者则配置在 `auxiliary.compression:` 下。

```yaml
compression:
  enabled: true
  threshold: 0.50
  target_ratio: 0.20         # fraction of threshold to preserve as recent tail
  protect_last_n: 20         # minimum recent messages to keep uncompressed
```

:::info 旧配置迁移
包含 `compression.summary_model`、`compression.summary_provider` 以及 `compression.summary_base_url` 的旧版配置，在首次加载时会被自动迁移为 `auxiliary.compression.*` 格式。
:::

## 辅助任务覆盖参数

| 参数名 | 描述 |
|--------|------|
| `AUXILIARY_VISION_PROVIDER` | 用于视觉任务的提供商覆盖参数 |
| `AUXILIARY_VISION_MODEL` | 用于视觉任务的模型覆盖参数 |
| `AUXILIARY_VISION_BASE_URL` | 用于视觉任务的直接 OpenAI 兼容接口地址 |
| `AUXILIARY_VISION_API_KEY` | 与 `AUXILIARY_VISION_BASE_URL` 配对的 API 密钥 |
| `AUXILIARY_WEB_EXTRACT_PROVIDER` | 用于网页提取/摘要任务的提供商覆盖参数 |
| `AUXILIARY_WEB_EXTRACT_MODEL` | 用于网页提取/摘要任务的模型覆盖参数 |
| `AUXILIARY_WEB_EXTRACT_BASE_URL` | 用于网页提取/摘要任务的直接 OpenAI 兼容接口地址 |
| `AUXILIARY_WEB_EXTRACT_API_KEY` | 与 `AUXILIARY_WEB_EXTRACT_BASE_URL` 配对的 API 密钥 |

对于特定任务所需的直接接口，Hermes 会使用该任务配置的 API 密钥或 `OPENAI_API_KEY`，而不会重复使用 `OPENROUTER_API_KEY`。

## 备用提供商（仅适用于 config.yaml）

主模型的备用链配置完全通过 `config.yaml` 完成——不存在相应的环境变量。只需在文件顶部添加一个包含 `provider` 和 `model` 键的 `fallback_providers` 列表，即可在主模型出现故障时实现自动切换。那些提供商设置为 `auto` 的辅助任务，在触发 Hermes 内置的辅助任务发现机制之前，也会先查询此备用链。

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

为保持向后兼容性，系统仍会读取旧版的单提供者格式的 `fallback_model` 设置，但新配置应使用 `fallback_providers`。对于特定任务的辅助策略，请在 `config.yaml` 中使用 `auxiliary.<task>.fallback_chain` 选项；目前暂无对应的环境变量。

详情请参阅 [Fallback Providers](/user-guide/features/fallback-providers) 文档。

## 提供者路由设置（仅适用于 config.yaml）

这些设置需放在 `~/.hermes/config.yaml` 文件的 `provider_routing` 部分中：

| 键值 | 描述 |
|-----|-------------|
| `sort` | 提供者排序规则：`"price"`（默认）、`"throughput"` 或 `"latency"` |
| `only` | 允许使用的提供者标识列表（例如：`["anthropic", "google"]`） |
| `ignore` | 应跳过的提供者标识列表 |
| `order` | 按指定顺序尝试的提供者标识列表 |
| `require_parameters` | 仅使用能支持所有请求参数的提供者（`true`/`false`） |
| `data_collection` | 设置为 `"allow"`（默认）或 `"deny"`，用于排除会存储数据的提供者 |

:::tip
建议使用 `hermes config set` 命令来设置环境变量——该命令会自动将它们保存到相应的文件中（敏感信息存入 `.env` 文件，其他内容则存入 `config.yaml`）。
:::
