---
sidebar_position: 2
title: "Environment Variables"
description: "Complete reference of all environment variables used by Hermes Agent"
---

# 环境变量参考

Hermes 会从进程环境读取环境变量，而对于用户管理的机密信息，则会从 `~/.hermes/.env` 文件中获取。请将 API 密钥、机器人令牌、OAuth 密钥以及其他凭证存储在 `.env` 文件中；如果存在配置键，建议优先使用 `config.yaml` 来设置非机密类的行为参数。以下部分变量仅为进程级覆盖项或内部桥接变量，即便此处有相关说明，也不应将其添加到 `.env` 文件中。

## 大语言模型提供方

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key (recommended for flexibility) |
| `OPENROUTER_BASE_URL` | Override the OpenRouter-compatible base URL |
| `FIREWORKS_API_KEY` | Fireworks AI API key ([app.fireworks.ai](https://app.fireworks.ai/settings/users/api-keys)). Configure endpoint overrides with `model.base_url` in `config.yaml`. |
| `HERMES_OPENROUTER_CACHE` | Enable OpenRouter response caching (`1`/`true`/`yes`/`on`). Overrides `openrouter.response_cache` in config.yaml. See [Response Caching](https://openrouter.ai/docs/guides/features/response-caching). |
| `HERMES_OPENROUTER_CACHE_TTL` | Cache TTL in seconds (1-86400). Overrides `openrouter.response_cache_ttl` in config.yaml. |
| `NOUS_BASE_URL` | Override Nous Portal base URL (rarely needed; development/testing only) |
| `NOUS_INFERENCE_BASE_URL` | Override Nous inference endpoint directly |
| `AI_GATEWAY_API_KEY` | Vercel AI Gateway API key ([ai-gateway.vercel.sh](https://ai-gateway.vercel.sh)) |
| `AI_GATEWAY_BASE_URL` | Override AI Gateway base URL (default: `https://ai-gateway.vercel.sh/v1`) |
| `OPENAI_API_KEY` | API key for custom OpenAI-compatible endpoints (used with `OPENAI_BASE_URL`) |
| `OPENAI_BASE_URL` | Base URL for custom endpoint (VLLM, SGLang, etc.) |
| `LM_API_KEY` | API key for LM Studio (`lmstudio` provider). Often a placeholder for local servers |
| `LM_BASE_URL` | LM Studio base URL (default: `http://localhost:1234/v1`) |
| `COPILOT_GITHUB_TOKEN` | GitHub token for Copilot API — first priority (OAuth `gho_*` or fine-grained PAT `github_pat_*`; classic PATs `ghp_*` are **not supported**) |
| `GH_TOKEN` | GitHub token — second priority for Copilot (also used by `gh` CLI) |
| `GITHUB_TOKEN` | GitHub token — third priority for Copilot |
| `HERMES_COPILOT_ACP_COMMAND` | Override Copilot ACP CLI binary path (default: `copilot`) |
| `COPILOT_CLI_PATH` | Alias for `HERMES_COPILOT_ACP_COMMAND` |
| `HERMES_COPILOT_ACP_ARGS` | Override Copilot ACP arguments (default: `--acp --stdio`) |
| `COPILOT_ACP_BASE_URL` | Override Copilot ACP base URL |
| `COPILOT_API_BASE_URL` | Override the Copilot API base URL (`copilot` provider) |
| `GLM_API_KEY` | z.ai / ZhipuAI GLM API key ([z.ai](https://z.ai)) |
| `ZAI_API_KEY` | Alias for `GLM_API_KEY` |
| `Z_AI_API_KEY` | Alias for `GLM_API_KEY` |
| `GLM_BASE_URL` | Override z.ai base URL (default: `https://api.z.ai/api/paas/v4`) |
| `KIMI_API_KEY` | Kimi / Moonshot AI API key ([moonshot.ai](https://platform.moonshot.ai)) |
| `KIMI_CODING_API_KEY` | Alias key for the `kimi-coding` provider (accepted alongside `KIMI_API_KEY`) |
| `KIMI_BASE_URL` | Override Kimi base URL (default: `https://api.moonshot.ai/v1`) |
| `KIMI_CN_API_KEY` | Kimi / Moonshot China API key ([moonshot.cn](https://platform.moonshot.cn)) |
| `ARCEEAI_API_KEY` | Arcee AI API key ([chat.arcee.ai](https://chat.arcee.ai/)) |
| `ARCEE_BASE_URL` | Override Arcee base URL (default: `https://api.arcee.ai/api/v1`) |
| `GMI_API_KEY` | GMI Cloud API key ([gmicloud.ai](https://www.gmicloud.ai/)) |
| `GMI_BASE_URL` | Override GMI Cloud base URL (default: `https://api.gmi-serving.com/v1`) |
| `ACTUAL_API_KEY` | Actual Computer inference key (`ac_...`, [actual.inc/user/keys](https://actual.inc/user/keys)). Not needed for the local daemon. |
| `ACTUAL_BASE_URL` | Override Actual Computer base URL (default: `https://api.actual.inc/v1`). Set to `http://127.0.0.1:8080` for the local offline daemon — loopback hosts need no API key. |
| `MINIMAX_API_KEY` | MiniMax API key — global endpoint ([minimax.io](https://www.minimax.io)). **Not used by `minimax-oauth`** (OAuth path uses browser login instead). |
| `MINIMAX_BASE_URL` | Override MiniMax base URL (default: `https://api.minimax.io/anthropic` — Hermes uses MiniMax's Anthropic Messages-compatible endpoint). **Not used by `minimax-oauth`**. |
| `MINIMAX_CN_API_KEY` | MiniMax API key — China endpoint ([minimaxi.com](https://www.minimaxi.com)). **Not used by `minimax-oauth`** (OAuth path uses browser login instead). |
| `MINIMAX_CN_BASE_URL` | Override MiniMax China base URL (default: `https://api.minimaxi.com/anthropic`). **Not used by `minimax-oauth`**. |
| `KILOCODE_API_KEY` | Kilo Code API key ([kilo.ai](https://kilo.ai)) |
| `KILOCODE_BASE_URL` | Override Kilo Code base URL (default: `https://api.kilo.ai/api/gateway`) |
| `XIAOMI_API_KEY` | Xiaomi MiMo API key ([platform.xiaomimimo.com](https://platform.xiaomimimo.com)) |
| `XIAOMI_BASE_URL` | Override Xiaomi MiMo base URL (default: `https://api.xiaomimimo.com/v1`) |
| `UPSTAGE_API_KEY` | Upstage API key for Solar models ([console.upstage.ai](https://console.upstage.ai/api-keys)) |
| `UPSTAGE_BASE_URL` | Override Upstage base URL (default: `https://api.upstage.ai/v1`) |
| `TOKENHUB_API_KEY` | Tencent TokenHub API key ([tokenhub.tencentmaas.com](https://tokenhub.tencentmaas.com)) |
| `TOKENHUB_BASE_URL` | Override Tencent TokenHub base URL (default: `https://tokenhub.tencentmaas.com/v1`) |
| `TOKENPLAN_API_KEY` | Tencent TokenPlan API key (LKEAP; Anthropic Messages endpoint) |
| `TOKENPLAN_BASE_URL` | Override Tencent TokenPlan base URL (default: `https://api.lkeap.cloud.tencent.com/plan/anthropic`) |
| `AZURE_FOUNDRY_API_KEY` | Microsoft Foundry / Azure OpenAI API key ([ai.azure.com](https://ai.azure.com/)). Not needed when `model.auth_mode: entra_id` |
| `AZURE_FOUNDRY_BASE_URL` | Microsoft Foundry endpoint URL (e.g. `https://<resource>.openai.azure.com/openai/v1` for OpenAI-style, or `https://<resource>.services.ai.azure.com/anthropic` for Anthropic-style) |
| `AZURE_ANTHROPIC_KEY` | Azure Anthropic API key for `provider: anthropic` + `base_url` pointing at a Microsoft Foundry Claude deployment (alternative to `ANTHROPIC_API_KEY` when both Anthropic and Azure Anthropic are configured) |
| `AZURE_TENANT_ID` | Entra ID tenant ID (service-principal flows; honored by `azure-identity` when `model.auth_mode: entra_id`) |
| `AZURE_CLIENT_ID` | Entra ID client ID (service principal, workload identity, or user-assigned managed identity) |
| `AZURE_CLIENT_SECRET` | Service principal secret used by `EnvironmentCredential` |
| `AZURE_CLIENT_CERTIFICATE_PATH` | Service principal certificate (alternative to `AZURE_CLIENT_SECRET`) |
| `AZURE_FEDERATED_TOKEN_FILE` | Federated token file path for AKS Workload Identity / OIDC flows |
| `AZURE_AUTHORITY_HOST` | Sovereign-cloud authority override (e.g. `https://login.microsoftonline.us` for Azure Government). See [Azure Foundry guide](/guides/azure-foundry#sovereign-clouds-government-china) |
| `IDENTITY_ENDPOINT` / `MSI_ENDPOINT` | Managed Identity endpoint for App Service, Functions, and Container Apps; VMs usually use IMDS instead and do not set these |
| `HF_TOKEN` | Hugging Face token for Inference Providers ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)) |
| `HF_BASE_URL` | Override Hugging Face base URL (default: `https://router.huggingface.co/v1`) |
| `GOOGLE_API_KEY` | Google AI Studio API key ([aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)) |
| `GEMINI_API_KEY` | Alias for `GOOGLE_API_KEY` |
| `GEMINI_BASE_URL` | Override Google AI Studio base URL |
| `VERTEX_CREDENTIALS_PATH` | Path to a Google Cloud service account JSON for Vertex AI (Gemini). Vertex uses OAuth2, not a static API key. Falls back to `GOOGLE_APPLICATION_CREDENTIALS`, then to ADC (`gcloud auth application-default login`). Set project/region under `vertex:` in `config.yaml` |
| `ANTHROPIC_API_KEY` | Anthropic Console API key ([console.anthropic.com](https://console.anthropic.com/)) |
| `ANTHROPIC_BASE_URL` | Override the Anthropic API base URL |
| `ANTHROPIC_TOKEN` | Manual or legacy Anthropic OAuth/setup-token override |
| `DASHSCOPE_API_KEY` | Qwen Cloud (Alibaba DashScope) API key for Qwen models ([modelstudio.console.alibabacloud.com](https://modelstudio.console.alibabacloud.com/)) |
| `DASHSCOPE_BASE_URL` | Custom DashScope base URL (default: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`; use `https://dashscope.aliyuncs.com/compatible-mode/v1` for mainland-China region) |
| `DASHSCOPE_CN_BASE_URL` | Override the `alibaba-cn` mainland-China DashScope base URL |
| `ALIBABA_CODING_PLAN_API_KEY` | Qwen Coding Plan API key (`alibaba-coding-plan`; also a fallback for `alibaba-coding-plan-cn`) |
| `ALIBABA_CODING_PLAN_CN_API_KEY` | Qwen Coding Plan API key for the mainland-China `alibaba-coding-plan-cn` provider (checked before the shared key, so only the CN row lights up) |
| `ALIBABA_CODING_PLAN_BASE_URL` | Override the Qwen Coding Plan base URL (international) |
| `ALIBABA_CODING_PLAN_CN_BASE_URL` | Override the Qwen Coding Plan base URL (mainland China) |
| `ALIBABA_TOKEN_PLAN_API_KEY` | Alibaba Model Studio Token Plan API key (`alibaba-token-plan`; also a fallback for `alibaba-token-plan-cn`) |
| `ALIBABA_TOKEN_PLAN_CN_API_KEY` | Token Plan API key for the mainland-China `alibaba-token-plan-cn` provider (checked before the shared key) |
| `ALIBABA_TOKEN_PLAN_BASE_URL` | Override the Token Plan base URL (international) |
| `ALIBABA_TOKEN_PLAN_CN_BASE_URL` | Override the Token Plan base URL (mainland China) |
| `DEEPSEEK_API_KEY` | DeepSeek API key for direct DeepSeek access ([platform.deepseek.com](https://platform.deepseek.com/api_keys)) |
| `DEEPSEEK_BASE_URL` | Custom DeepSeek API base URL |
| `DEEPINFRA_API_KEY` | DeepInfra API key ([deepinfra.com](https://deepinfra.com/dash/api_keys)) |
| `DEEPINFRA_BASE_URL` | DeepInfra base URL override |
| `NOVITA_API_KEY` | NovitaAI API key — AI-native cloud for Model API, Agent Sandbox, and GPU Cloud ([novita.ai/settings/key-management](https://novita.ai/settings/key-management)) |
| `NOVITA_BASE_URL` | Override NovitaAI base URL (default: `https://api.novita.ai/openai/v1`) |
| `RAMP_ROUTER_API_KEY` | Ramp Router API key ([app.router.com/keys](https://app.router.com/keys)); alias `ROUTER_API_KEY` also accepted |
| `RAMP_ROUTER_BASE_URL` | Override Ramp Router base URL (default: `https://api.router.com/v1`) |
| `NEBIUS_API_KEY` | Nebius Token Factory API key ([tokenfactory.nebius.com](https://tokenfactory.nebius.com/)); `NEBIUS_TOKEN_FACTORY_API_KEY` also accepted |
| `NEBIUS_BASE_URL` | Override Nebius Token Factory base URL (default: `https://api.tokenfactory.nebius.com/v1`) |
| `NVIDIA_API_KEY` | NVIDIA NIM API key — Nemotron and open models ([build.nvidia.com](https://build.nvidia.com)) |
| `NVIDIA_BASE_URL` | Override NVIDIA base URL (default: `https://integrate.api.nvidia.com/v1`; set to `http://localhost:8000/v1` for a local NIM endpoint) |
| `STEPFUN_API_KEY` | StepFun API key — Step-series models ([platform.stepfun.com](https://platform.stepfun.com)) |
| `STEPFUN_BASE_URL` | Override StepFun base URL (default: `https://api.stepfun.com/v1`) |
| `OLLAMA_API_KEY` | Ollama Cloud API key — managed Ollama catalog without local GPU ([ollama.com/settings/keys](https://ollama.com/settings/keys)) |
| `OLLAMA_BASE_URL` | Override Ollama Cloud base URL (default: `https://ollama.com/v1`) |
| `XAI_API_KEY` | xAI (Grok) API key for chat + TTS + web search ([console.x.ai](https://console.x.ai/)) |
| `XAI_BASE_URL` | Override xAI base URL (default: `https://api.x.ai/v1`) |
| `MISTRAL_API_KEY` | Mistral API key for Voxtral TTS and Voxtral STT ([console.mistral.ai](https://console.mistral.ai)) |
| `AWS_REGION` | AWS region for Bedrock inference (e.g. `us-east-1`, `eu-central-1`). Read by boto3. |
| `AWS_PROFILE` | AWS named profile for Bedrock authentication (reads `~/.aws/credentials`). Leave unset to use default boto3 credential chain. |
| `BEDROCK_BASE_URL` | Override Bedrock runtime base URL (default: `https://bedrock-runtime.us-east-1.amazonaws.com`; usually leave unset and use `AWS_REGION` instead) |
| `HERMES_QWEN_BASE_URL` | Qwen Portal base URL override (default: `https://portal.qwen.ai/v1`) |
| `OPENCODE_ZEN_API_KEY` | OpenCode Zen API key — pay-as-you-go access to curated models ([opencode.ai](https://opencode.ai/auth)) |
| `OPENCODE_ZEN_BASE_URL` | Override OpenCode Zen base URL |
| `OPENCODE_GO_API_KEY` | OpenCode Go API key — $10/month subscription for open models ([opencode.ai](https://opencode.ai/auth)) |
| `OPENCODE_GO_BASE_URL` | Override OpenCode Go base URL |
| `CLAUDE_CODE_OAUTH_TOKEN` | Explicit Claude Code token override if you export one manually |
| `HERMES_MODEL` | Override model name at process level (used by cron scheduler; prefer `config.yaml` for normal use) |
| `VOICE_TOOLS_OPENAI_KEY` | Preferred OpenAI key for OpenAI speech-to-text and text-to-speech providers |
| `HERMES_LOCAL_STT_COMMAND` | Optional local speech-to-text command template. Supports `{input_path}`, `{output_dir}`, `{language}`, and `{model}` placeholders |
| `HERMES_LOCAL_STT_LANGUAGE` | Default language hint for STT. Used by the `local` (faster-whisper) provider, `HERMES_LOCAL_STT_COMMAND`, the local `whisper` CLI fallback (default: `en`), Groq, and xAI when no per-provider `language` is set in `config.yaml` |
| `HERMES_HOME` | Override Hermes config directory (default: `~/.hermes`). Also scopes the gateway PID file and systemd service name, so multiple installations can run concurrently |
| `HERMES_GIT_BASH_PATH` | **Windows only.** Override `bash.exe` discovery for the terminal tool. Points at any bash — full Git-for-Windows install, WSL bash via symlink, MSYS2, Cygwin. The installer sets this automatically to the PortableGit it provisioned. See the [Windows (Native) Guide](../user-guide/windows-native.md#how-hermes-runs-shell-commands-on-windows) |
| `HERMES_DISABLE_WINDOWS_UTF8` | **Windows only.** Set to `1` to disable the UTF-8 stdio shim (`configure_windows_stdio()`) and fall back to the console's locale code page. Useful for bisecting encoding bugs; rarely the right setting in normal operation |
| `HERMES_KANBAN_HOME` | Override the shared Hermes root that anchors the kanban board (db + workspaces + worker logs). Falls back to `get_default_hermes_root()` (the parent of any active profile). Useful for tests and unusual deployments |
| `HERMES_KANBAN_BOARD` | Pin the active kanban board for this process. Takes precedence over `~/.hermes/kanban/current`; the dispatcher injects this into worker subprocess env so workers physically cannot see tasks on other boards. Defaults to `default`. Slug validation: lowercase alphanumerics + hyphens + underscores, 1-64 chars |
| `HERMES_KANBAN_DB` | Pin the kanban database file path directly (highest precedence; beats `HERMES_KANBAN_BOARD` and `HERMES_KANBAN_HOME`). The dispatcher injects this into worker subprocess env so profile workers converge on the dispatcher's board |
| `HERMES_KANBAN_WORKSPACES_ROOT` | Pin the kanban workspaces root directly (highest precedence for workspaces; beats `HERMES_KANBAN_HOME`). The dispatcher injects this into worker subprocess env |
| `HERMES_KANBAN_DISPATCH_IN_GATEWAY` | Runtime override for `kanban.dispatch_in_gateway`. Set to `0`, `false`, `no`, or `off` to keep the gateway from starting the embedded Kanban dispatcher; any other non-empty value enables it. Useful when a separate dispatcher process owns the board. |

## 提供商认证（OAuth）

对于原生 Anthropic 认证方式，若存在 Claude Code 自带的凭据文件，Hermes 会优先使用这些文件，因为它们可以自动刷新。**通过 OAuth 连接 Anthropic 需要订阅包含额外使用额度的 Claude Max 套餐**——Hermes 会以 Claude Code 的身份发起请求，仅消耗 Max 套餐中的额外/超额额度，而不占用基础额度，且不支持在 Claude Pro 上使用。若没有 Max 套餐及额外额度，则建议使用 API 密钥。虽然 `ANTHROPIC_TOKEN` 等环境变量仍可作为手动覆盖方式，但已不再推荐用于 Claude Max 的登录流程。

| 变量名 | 描述 |
|--------|------|
| `HERMES_PORTAL_BASE_URL` | 覆盖 Nous Portal 的 URL（用于开发/测试） |
| `NOUS_INFERENCE_BASE_URL` | 覆盖 Nous 推理 API 的 URL |
| `HERMES_NOUS_MIN_KEY_TTL_SECONDS` | 定期重新生成代理密钥前的最小有效期（默认值：1800 秒 = 30 分钟） |
| `HERMES_NOUS_TIMEOUT_SECONDS` | Nous 凭据/令牌获取流程的 HTTP 超时时间 |
| `HERMES_DUMP_REQUESTS` | 是否将 API 请求内容输出到日志文件中（`true`/`false`） |
| `HERMES_PREFILL_MESSAGES_FILE` | 包含在 API 调用时注入的临时预填消息的 JSON 文件路径 |
| `HERMES_TIMEZONE` | IANA 时区设置（例如 `America/New_York`） |

## 工具 API

| Variable | Description |
|----------|-------------|
| `PARALLEL_API_KEY` | AI-native web search ([parallel.ai](https://parallel.ai/)) |
| `FIRECRAWL_API_KEY` | Web scraping and cloud browser ([firecrawl.dev](https://firecrawl.dev/)) |
| `FIRECRAWL_API_URL` | Custom Firecrawl API endpoint for self-hosted instances (optional) |
| `TAVILY_API_KEY` | Optional Tavily API key for higher search/extract limits. After selecting Tavily as the web backend, keyless access works without it ([app.tavily.com](https://app.tavily.com/home), [keyless docs](https://docs.tavily.com/documentation/keyless)) |
| `TAVILY_BASE_URL` | Override the Tavily API endpoint. Useful for corporate proxies and self-hosted Tavily-compatible search backends. Same pattern as `GROQ_BASE_URL`. |
| `PERPLEXITY_API_KEY` | Perplexity Search API key for the `perplexity` web backend — ranked search results plus query-relevant page snippets for extract ([perplexity.ai/account/api](https://www.perplexity.ai/account/api)) |
| `PERPLEXITY_BASE_URL` | Override the Perplexity API endpoint (default `https://api.perplexity.ai`) for proxies (optional) |
| `SEARXNG_URL` | SearXNG instance URL for free self-hosted web search — no API key required ([searxng.github.io](https://searxng.github.io/searxng/)) |
| `EXA_API_KEY` | Exa API key for AI-native web search and contents ([exa.ai](https://exa.ai/)) |
| `BRAVE_SEARCH_API_KEY` | Brave Search API subscription token for web search (free tier available) ([brave.com/search/api](https://brave.com/search/api/)) |
| `BROWSERBASE_API_KEY` | Browser automation ([browserbase.com](https://browserbase.com/)) |
| `BROWSERBASE_PROJECT_ID` | Browserbase project ID |
| `BROWSER_USE_API_KEY` | Browser Use cloud browser API key ([browser-use.com](https://browser-use.com/)) |
| `FIRECRAWL_BROWSER_TTL` | Firecrawl browser session TTL in seconds (default: 300) |
| `BROWSER_CDP_URL` | Chrome DevTools Protocol URL for local browser (set via `/browser connect`, e.g. `ws://localhost:9222`) |
| `CAMOFOX_URL` | Camofox local anti-detection browser server address (default: `http://localhost:9377`). Address only — it does not select Camofox as the backend; pick Camofox in `hermes tools` (`browser.cloud_provider: camofox`) |
| `CAMOFOX_API_KEY` | Optional bearer token sent as Authorization header to a remote/authenticated Camofox server |
| `CAMOFOX_USER_ID` | Optional externally managed Camofox user ID for shared visible sessions |
| `CAMOFOX_SESSION_KEY` | Optional Camofox session key used when creating tabs for `CAMOFOX_USER_ID` |
| `CAMOFOX_ADOPT_EXISTING_TAB` | Set to `true` to reuse an existing Camofox tab before creating a new one |
| `BROWSER_INACTIVITY_TIMEOUT` | Browser session inactivity timeout in seconds |
| `AGENT_BROWSER_ARGS` | Extra Chromium launch flags (comma- or newline-separated). Hermes auto-injects `--no-sandbox,--disable-dev-shm-usage` when running as root or on AppArmor-restricted unprivileged user namespaces (Ubuntu 23.10+, DGX Spark, many container images); set this manually only to override or add other flags. |
| `AGENT_BROWSER_ENGINE` | Local browser engine: `auto` (default — Chromium-family via CDP), `lightpanda` (Browser Use mode spawns `lightpanda serve`; the built-in tools pass `--engine lightpanda` to agent-browser), or `chrome`. Same as `browser.engine` in config.yaml. |
| `FAL_KEY` | Image generation ([fal.ai](https://fal.ai/)) |
| `KREA_API_KEY` | Krea API key for Krea 2 image generation ([krea.ai](https://krea.ai/)) |
| `GROQ_API_KEY` | Groq Whisper STT API key ([groq.com](https://groq.com/)) |
| `ELEVENLABS_API_KEY` | ElevenLabs premium TTS voices ([elevenlabs.io](https://elevenlabs.io/)) |
| `PORCUPINE_ACCESS_KEY` | Picovoice Porcupine wake-word engine ([console.picovoice.ai](https://console.picovoice.ai/)) — only for `wake_word.provider: porcupine`; the default openWakeWord and sherpa engines need no key |
| `STT_GROQ_MODEL` | Override the Groq STT model (default: `whisper-large-v3-turbo`) |
| `GROQ_BASE_URL` | Override the Groq OpenAI-compatible STT endpoint |
| `STT_OPENAI_MODEL` | Override the OpenAI STT model (default: `whisper-1`) |
| `STT_OPENAI_BASE_URL` | Override the OpenAI-compatible STT endpoint |
| `GITHUB_TOKEN` | GitHub token for Skills Hub (higher API rate limits, skill publish) |
| `HONCHO_API_KEY` | Cross-session user modeling ([honcho.dev](https://honcho.dev/)) |
| `HONCHO_BASE_URL` | Base URL for self-hosted Honcho instances (default: Honcho cloud). No API key required for local instances |
| `HINDSIGHT_API_KEY` | Hindsight API key for graph-aware persistent memory ([hindsight.vectorize.io](https://hindsight.vectorize.io)) |
| `HINDSIGHT_API_URL` | Base URL for the Hindsight API (default: `https://api.hindsight.vectorize.io`) |
| `HINDSIGHT_TIMEOUT` | Timeout in seconds for Hindsight memory-provider API calls (default: `60`). Bump this if your Hindsight instance is slow to respond during `/sync` or `on_session_switch` and you're seeing timeouts in `errors.log`. |
| `MEM0_API_KEY` | Mem0 Platform API key for semantic persistent memory ([app.mem0.ai](https://app.mem0.ai)) |
| `MEM0_MODE` | Mem0 backend mode: `platform` (default) or `oss` — see [Memory Providers](/user-guide/features/memory-providers) |
| `MEM0_HOST` | Base URL of a self-hosted Mem0 server (switches the plugin off the Platform API) |
| `MEM0_USER_ID` | Override the user id Mem0 memories are stored under |
| `MEM0_AGENT_ID` | Override the agent id Mem0 memories are tagged with |
| `RETAINDB_API_KEY` | RetainDB API key for persistent memory ([retaindb.com](https://retaindb.com)) |
| `RETAINDB_BASE_URL` | Base URL for self-hosted RetainDB instances (default: `https://api.retaindb.com`) |
| `OPENVIKING_API_KEY` | OpenViking API key (leave blank for local dev mode) |
| `OPENVIKING_ENDPOINT` | OpenViking server URL (default: `http://127.0.0.1:1933`) |
| `BRV_API_KEY` | ByteRover API key (optional, for cloud sync — local-first by default) ([app.byterover.dev](https://app.byterover.dev)) |
| `SUPERMEMORY_API_KEY` | Semantic long-term memory with profile recall and session ingest ([supermemory.ai](https://supermemory.ai)) |
| `DAYTONA_API_KEY` | Daytona cloud sandboxes ([daytona.io](https://daytona.io/)) |
| `VERCEL_TOKEN` | Vercel Sandbox access token ([vercel.com](https://vercel.com/)) |
| `VERCEL_PROJECT_ID` | Vercel project ID (required with `VERCEL_TOKEN`) |
| `VERCEL_TEAM_ID` | Vercel team ID (required with `VERCEL_TOKEN`) |
| `VERCEL_OIDC_TOKEN` | Vercel short-lived OIDC token (development-only alternative) |

### 技能 API 密钥

特定内置或可选技能所使用的机密信息。仅在使用对应技能时才需要这些密钥。

| 变量名 | 所属技能 | 描述 |
|--------|----------|------|
| `NOTION_API_KEY` | `notion` | Notion 集成令牌。 |
| `LINEAR_API_KEY` | `linear` | Linear 个人 API 密钥。 |
| `AIRTABLE_API_KEY` | `airtable` | Airtable 个人访问令牌。 |
| `TENOR_API_KEY` | `gif-search` | 用于 GIF 搜索的 Tenor API 密钥。 |

### Langfuse 可观测性功能

内置插件 [`observability/langfuse`](/user-guide/features/built-in-plugins#observabilitylangfuse) 所需的环境变量。请在 `~/.hermes/.env` 文件中设置这些变量。此外，在这些设置生效之前，还需先启用该插件（执行命令 `hermes plugins enable observability/langfuse`，或在 `hermes plugins` 界面中勾选对应选项）。

| 变量 | 描述 |
|----------|-------------|
| `HERMES_LANGFUSE_PUBLIC_KEY` | Langfuse 项目的公钥（格式为 `pk-lf-...`），为必填项。 |
| `HERMES_LANGFUSE_SECRET_KEY` | Langfuse 项目的私钥（格式为 `sk-lf-...`），为必填项。 |
| `HERMES_LANGFUSE_BASE_URL` | Langfuse 服务器的 URL（默认值为 `https://cloud.langfuse.com`），用于自托管场景时需自行设置。 |
| `HERMES_LANGFUSE_ENV` | 接口请求中的环境标签（如 `production`、`staging` 等）。 |
| `HERMES_LANGFUSE_RELEASE` | 接口请求中的版本标签。 |
| `HERMES_LANGFUSE_SAMPLE_RATE` | SDK 的采样率，取值范围为 0.0–1.0（默认值为 `1.0`）。 |
| `HERMES_LANGFUSE_MAX_CHARS` | 序列化后的请求体中每个字段的最大字符数（默认值为 `12000`）。 |
| `HERMES_LANGFUSE_DEBUG` | 若设置为 `true`，则会在 `agent.log` 文件中输出更详细的插件日志。 |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL` | Langfuse SDK 的标准名称。当对应的 `HERMES_LANGFUSE_*` 变量未被设置时，系统会自动使用这些标准名称作为替代。 |

### Nous 工具网关

这些变量用于配置面向付费 Nous 用户或自托管网关部署的[工具网关](/user-guide/features/tool-gateway)。大多数用户无需手动设置这些参数——网关会通过 `hermes model` 或 `hermes tools` 自动完成配置。

| 变量 | 描述 |
|----------|-------------|
| `TOOL_GATEWAY_DOMAIN` | Tool Gateway 路由的基准域名（默认值：`nousresearch.com`） |
| `TOOL_GATEWAY_SCHEME` | 网关 URL 所使用的协议，可选 HTTP 或 HTTPS（默认值：`https`） |
| `TOOL_GATEWAY_USER_TOKEN` | Tool Gateway 的认证令牌（通常由 Nous 系统自动填充） |
| `FIRECRAWL_GATEWAY_URL` | 专门用于覆盖 Firecrawl 网关端点的 URL |

## 终端后端

| Variable | Description |
|----------|-------------|
| `TERMINAL_ENV` | Backend: `local`, `docker`, `ssh`, `singularity`, `modal`, `daytona`, `vercel_sandbox` |
| `HERMES_DOCKER_BINARY` | Override the container binary Hermes shells out to (e.g. `podman`, `/usr/local/bin/docker`). When unset, Hermes auto-discovers `docker` or `podman` on `PATH`. Needed when both are installed and you want the non-default, or when the binary lives outside `PATH`. |
| `TERMINAL_DOCKER_IMAGE` | Docker image (default: `nikolaik/python-nodejs:python3.11-nodejs20`) |
| `TERMINAL_DOCKER_FORWARD_ENV` | JSON array of env var names to explicitly forward into Docker terminal sessions. Note: skill-declared `required_environment_variables` are forwarded automatically — you only need this for vars not declared by any skill. |
| `TERMINAL_DOCKER_VOLUMES` | Additional Docker volume mounts (comma-separated `host:container` pairs) |
| `TERMINAL_DOCKER_ENV` | JSON object of extra env vars to set inside Docker terminal sessions (e.g. `{"FOO":"bar"}`) |
| `TERMINAL_DOCKER_EXTRA_ARGS` | JSON array of extra `docker run` arguments (e.g. `["--memory","4g"]`) |
| `TERMINAL_DOCKER_MOUNT_CWD_TO_WORKSPACE` | Advanced opt-in: mount the launch cwd into Docker `/workspace` (`true`/`false`, default: `false`) |
| `TERMINAL_SINGULARITY_IMAGE` | Singularity image or `.sif` path |
| `TERMINAL_MODAL_IMAGE` | Modal container image |
| `TERMINAL_DAYTONA_IMAGE` | Daytona sandbox image |
| `TERMINAL_VERCEL_RUNTIME` | Vercel Sandbox runtime (`node24`, `node22`, `python3.13`) |
| `TERMINAL_TIMEOUT` | Command timeout in seconds |
| `TERMINAL_LIFETIME_SECONDS` | Max lifetime for terminal sessions in seconds |
| `TERMINAL_CWD` | Deprecated direct override for gateway/cron terminal sessions. Prefer `terminal.cwd` in `config.yaml`; CLI still uses the launch directory. |
| `SUDO_PASSWORD` | Enable sudo without interactive prompt |

对于云沙箱后端，数据持久化是以文件系统为基础的。`TERMINAL_LIFETIME_SECONDS`用于控制Hermes何时清理空闲的终端会话，后续重新启动时可能会创建新的沙箱，而不会继续运行原有的进程。

## SSH后端

| 变量 | 描述 |
|------|------|
| `TERMINAL_SSH_HOST` | 远程服务器主机名 |
| `TERMINAL_SSH_USER` | SSH用户名 |
| `TERMINAL_SSH_PORT` | SSH端口（默认：22） |
| `TERMINAL_SSH_KEY` | 私钥路径 |
| `TERMINAL_SSH_PERSISTENT` | 覆盖SSH的持久化Shell设置（默认：遵循`TERMINAL_PERSISTENT_SHELL`的设置） |

## 容器资源（Docker、Singularity、Modal、Daytona）

| 变量 | 描述 |
|------|------|
| `TERMINAL_CONTAINER_CPU` | CPU核心数（默认：1） |
| `TERMINAL_CONTAINER_MEMORY` | 内存大小，单位为MB（默认：5120） |
| `TERMINAL_CONTAINER_DISK` | 磁盘空间大小，单位为MB（默认：51200） |
| `TERMINAL_CONTAINER_PERSISTENT` | 在不同会话之间保持容器文件系统不变（默认：`true`） |
| `TERMINAL_SANDBOX_DIR` | 用于存储工作区和覆盖文件的宿主机目录（默认：`~/.hermes/sandboxes/`） |

## 持久化Shell

| 变量 | 描述 |
|----------|-------------|
| `TERMINAL_PERSISTENT_SHELL` | 为非本地后端启用持久化 shell（默认值为 `true`）。也可通过 config.yaml 中的 `terminal.persistent_shell` 参数进行设置。 |
| `TERMINAL_LOCAL_PERSISTENT` | 为本地后端启用持久化 shell（默认值为 `false`）。 |
| `TERMINAL_SSH_PERSISTENT` | 覆盖 SSH 后端的持久化 shell 设置（默认值与 `TERMINAL_PERSISTENT_SHELL` 相同）。 |

## 出站代理（沙箱注入式）

这些环境变量不会在主机上设置——当 `proxy.enabled: true` 时，它们会由 [出站代理](../user-guide/egress/iron-proxy.md) 插件注入到 Docker 沙箱中。在本版本中，Docker 是唯一的有线后端。

| Variable | Description |
|----------|-------------|
| `HERMES_EGRESS_PROXY` | Set to `1` inside a sandbox when the egress proxy is active. Agent code can check this to know it's running behind a TLS-intercepting proxy. |
| Provider env vars (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, …) | Set to opaque proxy tokens, not real upstream secrets, so existing SDKs keep reading the standard env names. iron-proxy swaps those tokens for the real upstream secret at the network boundary. |
| `HERMES_PROXY_TOKEN_<ENV_NAME>` | Diagnostic alias for each minted provider mapping. E.g. `HERMES_PROXY_TOKEN_OPENROUTER_API_KEY=hermes-proxy-openrouter-…`. Same token value as the standard provider env var. |
| `HTTPS_PROXY` / `HTTP_PROXY` | `HTTPS_PROXY` points at `http://host.docker.internal:<tunnel_port>` for CONNECT/MITM. `HTTP_PROXY` points at `<tunnel_port + 1>` for plain-HTTP forwarding. |
| `NO_PROXY` | `127.0.0.1,localhost,::1` so loopback dev servers inside the sandbox bypass the proxy. |
| `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` / `CURL_CA_BUNDLE` / `NODE_EXTRA_CA_CERTS` | Path to the mounted Hermes egress CA cert inside the sandbox (`/etc/ssl/certs/hermes-egress-ca.crt`). Lets the language runtimes trust iron-proxy's MITM-minted leaf certs. |
| `NODE_OPTIONS` | Appended with `--use-openssl-ca` (your existing flags are preserved) so Node.js routes through the OpenSSL store the other CA-bundle vars control. Narrows the [Node.js asymmetric CA caveat](../user-guide/egress/iron-proxy.md#nodejs-asymmetric-ca-caveat). |
| `HERMES_IRON_PROXY_NONCE` | Set on the iron-proxy daemon process itself (NOT inside the sandbox). Used by `_pid_alive` to confirm a candidate PID still refers to *our* managed binary across PID recycling. |

当 `proxy.enabled: true` 且守护进程正在运行时，这些参数会由 Docker 终端后端自动设置。您无需自行配置；相关面向操作员的设置项位于 `~/.hermes/config.yaml` 文件的 `proxy:` 部分——详情请参阅[出站代理 → 配置](../user-guide/egress/iron-proxy.md#configuration)。

## 消息传递

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (from @BotFather) |
| `TELEGRAM_ALLOWED_USERS` | Comma-separated user IDs allowed to use the bot (applies to DMs, groups, and forums) |
| `TELEGRAM_ALLOW_ALL_USERS` | Allow any Telegram user to trigger the bot (dev only). |
| `TELEGRAM_GROUP_ALLOWED_USERS` | Comma-separated sender user IDs authorized in groups/forums only (does NOT grant DM access). Chat-ID-shaped values (starting with `-`) are still honored as chat IDs for backward compat with pre-#17686 configs, with a deprecation warning. |
| `TELEGRAM_GROUP_ALLOWED_CHATS` | Comma-separated group/forum chat IDs; any member is authorized |
| `TELEGRAM_HOME_CHANNEL` | Default Telegram chat/channel for cron delivery |
| `TELEGRAM_HOME_CHANNEL_NAME` | Display name for the Telegram home channel |
| `TELEGRAM_CRON_THREAD_ID` | Forum topic ID to receive cron deliveries; overrides `TELEGRAM_HOME_CHANNEL_THREAD_ID` for cron only. Use in topic mode so replies to cron messages open a new session instead of hitting the system lobby (#24409). |
| `TELEGRAM_WEBHOOK_URL` | Public HTTPS URL for webhook mode (enables webhook instead of polling) |
| `TELEGRAM_WEBHOOK_PORT` | Local listen port for webhook server (default: `8443`) |
| `TELEGRAM_WEBHOOK_SECRET` | Secret token Telegram echoes back in each update for verification. **Required whenever `TELEGRAM_WEBHOOK_URL` is set** — the gateway refuses to start without it (GHSA-3vpc-7q5r-276h). Generate with `openssl rand -hex 32`. |
| `TELEGRAM_REACTIONS` | Enable emoji reactions on messages during processing (default: `false`) |
| `TELEGRAM_REQUIRE_MENTION` | Require an explicit trigger before responding in Telegram groups. Equivalent to `telegram.require_mention` in `config.yaml`. |
| `TELEGRAM_MENTION_PATTERNS` | JSON array, newline-separated list, or comma-separated list of regex wake-word patterns accepted when Telegram group mention gating is enabled. Equivalent to `telegram.mention_patterns`. |
| `TELEGRAM_EXCLUSIVE_BOT_MENTIONS` | When enabled, explicit `@...bot` mentions in Telegram groups route only to the mentioned bot usernames before reply or wake-word fallbacks run. Default: `true`. Equivalent to `telegram.exclusive_bot_mentions`. |
| `TELEGRAM_BOTS_REQUIRE_MENTION` | When enabled, a message sent by another bot must explicitly `@thisbot` to trigger a response — a quote-reply alone is ignored, which stops two bots from replying to each other forever. Human replies are unaffected. Default: `false`. Equivalent to `telegram.bots_require_mention`. |
| `TELEGRAM_REPLY_TO_MODE` | Reply-reference behavior: `off`, `first` (default), or `all`. Matches the Discord pattern. |
| `TELEGRAM_IGNORED_THREADS` | Comma-separated Telegram forum topic/thread IDs where the bot never responds |
| `TELEGRAM_PROXY` | Proxy URL for Telegram connections — overrides `HTTPS_PROXY`. Supports `http://`, `https://`, `socks5://` |
| `DISCORD_BOT_TOKEN` | Discord bot token |
| `DISCORD_ALLOWED_USERS` | Comma-separated Discord user IDs allowed to use the bot |
| `DISCORD_ALLOW_ALL_USERS` | Allow any Discord user to trigger the bot (dev only). |
| `DISCORD_ALLOWED_ROLES` | Comma-separated Discord role IDs allowed to use the bot (OR with `DISCORD_ALLOWED_USERS`). Auto-enables the Members intent. Useful when moderation teams churn — role grants propagate automatically. |
| `DISCORD_ALLOWED_CHANNELS` | Comma-separated Discord channel IDs. When set, the bot only responds in these channels (plus DMs if allowed). Overrides `config.yaml` `discord.allowed_channels`. |
| `DISCORD_PROXY` | Proxy URL for Discord connections — overrides `HTTPS_PROXY`. Supports `http://`, `https://`, `socks5://` |
| `DISCORD_HOME_CHANNEL` | Default Discord channel for cron delivery |
| `DISCORD_HOME_CHANNEL_NAME` | Display name for the Discord home channel |
| `DISCORD_COMMAND_SYNC_POLICY` | Discord slash-command startup sync policy: `safe` (diff and reconcile), `bulk` (legacy `tree.sync()`), or `off` |
| `DISCORD_REQUIRE_MENTION` | Require an @mention before responding in server channels |
| `DISCORD_FREE_RESPONSE_CHANNELS` | Comma-separated channel IDs where mention is not required |
| `DISCORD_AUTO_THREAD` | Auto-thread long replies when supported |
| `DISCORD_ALLOW_ANY_ATTACHMENT` | When `true`, accept attachments of any file type (not just the built-in PDF/text/zip/office allowlist). Unknown types are cached and surfaced to the agent as a local path so it can inspect them via `terminal` / `read_file` / `ffprobe`. Default `false`. |
| `DISCORD_MAX_ATTACHMENT_BYTES` | Maximum bytes per attachment the gateway will cache. Default `33554432` (32 MiB). Set to `0` for no cap (attachments are held in memory while being written). |
| `DISCORD_REACTIONS` | Enable emoji reactions on messages during processing (default: `true`) |
| `DISCORD_IGNORED_CHANNELS` | Comma-separated channel IDs where the bot never responds |
| `DISCORD_NO_THREAD_CHANNELS` | Comma-separated channel IDs where bot responds without auto-threading |
| `DISCORD_REPLY_TO_MODE` | Reply-reference behavior: `off`, `first` (default), or `all` |
| `DISCORD_ALLOW_MENTION_EVERYONE` | Allow the bot to ping `@everyone`/`@here` (default: `false`). See [Mention Control](../user-guide/messaging/discord.md#mention-control). |
| `DISCORD_ALLOW_MENTION_ROLES` | Allow the bot to ping `@role` mentions (default: `false`). |
| `DISCORD_ALLOW_MENTION_USERS` | Allow the bot to ping individual `@user` mentions (default: `true`). |
| `DISCORD_ALLOW_MENTION_REPLIED_USER` | Ping the author when replying to their message (default: `true`). |
| `SLACK_BOT_TOKEN` | Slack bot token (`xoxb-...`) |
| `SLACK_APP_TOKEN` | Slack app-level token (`xapp-...`, required for Socket Mode) |
| `SLACK_ALLOWED_USERS` | Comma-separated Slack user IDs |
| `SLACK_ALLOW_ALL_USERS` | Allow any Slack user to trigger the bot (dev only). |
| `SLACK_ALLOW_BOTS` | Accept messages from other Slack bots: `none` (default), `mentions`, or `all`. The bot always ignores its own messages. |
| `SLACK_THREAD_REQUIRE_MENTION` | Require an explicit @mention for Slack thread replies while preserving top-level free-response channels |
| `SLACK_HOME_CHANNEL` | Default Slack channel for cron delivery |
| `SLACK_HOME_CHANNEL_NAME` | Display name for the Slack home channel |
| `GOOGLE_CHAT_PROJECT_ID` | GCP project hosting the Pub/Sub topic (falls back to `GOOGLE_CLOUD_PROJECT`) |
| `GOOGLE_CHAT_SUBSCRIPTION_NAME` | Full Pub/Sub subscription path, `projects/{proj}/subscriptions/{sub}` (legacy alias: `GOOGLE_CHAT_SUBSCRIPTION`) |
| `GOOGLE_CHAT_SERVICE_ACCOUNT_JSON` | Path to Service Account JSON, or the JSON inline (falls back to `GOOGLE_APPLICATION_CREDENTIALS`) |
| `GOOGLE_CHAT_ALLOWED_USERS` | Comma-separated user emails allowed to chat with the bot |
| `GOOGLE_CHAT_ALLOW_ALL_USERS` | Allow any Google Chat user to trigger the bot (dev only) |
| `GOOGLE_CHAT_HOME_CHANNEL` | Default space (e.g. `spaces/AAAA...`) for cron delivery |
| `GOOGLE_CHAT_HOME_CHANNEL_NAME` | Display name for the Google Chat home space |
| `GOOGLE_CHAT_MAX_MESSAGES` | Pub/Sub FlowControl max in-flight messages (default: `1`) |
| `GOOGLE_CHAT_MAX_BYTES` | Pub/Sub FlowControl max in-flight bytes (default: `16777216`, 16 MiB) |
| `GOOGLE_CHAT_BOOTSTRAP_SPACES` | Comma-separated extra space IDs to probe at startup when resolving the bot's own `users/{id}` |
| `GOOGLE_CHAT_DEBUG_RAW` | Set to any value to log redacted Pub/Sub envelopes at DEBUG level (debugging only) |
| `GOOGLE_CHAT_HTTP_EVENTS_URL` | Authenticated HTTP endpoint for Chat message events (alternative to Pub/Sub) |
| `GOOGLE_CHAT_HTTP_EVENTS_AUDIENCE` | Expected audience for Google-signed HTTP event bearer tokens (defaults to `GOOGLE_CHAT_HTTP_EVENTS_URL`) |
| `GOOGLE_CHAT_HTTP_EVENTS_SERVICE_ACCOUNT_EMAIL` | Expected Google service account email for HTTP event bearer tokens |
| `WHATSAPP_ENABLED` | Enable the WhatsApp bridge (`true`/`false`) |
| `WHATSAPP_MODE` | `bot` (separate number) or `self-chat` (message yourself) |
| `WHATSAPP_ALLOWED_USERS` | Comma-separated phone numbers (with country code, no `+`), or `*` to allow all senders |
| `WHATSAPP_ALLOW_ALL_USERS` | Allow all WhatsApp senders without an allowlist (`true`/`false`) |
| `WHATSAPP_HOME_CHANNEL` | Default chat ID for cron / notification delivery. |
| `WHATSAPP_HOME_CHANNEL_NAME` | Display name for the WhatsApp home channel. |
| `WHATSAPP_DEBUG` | Log raw message events in the bridge for troubleshooting (`true`/`false`) |
| `WHATSAPP_CLOUD_PHONE_NUMBER_ID` | Meta Phone Number ID from the WhatsApp Business Cloud API (15–17 digits; **not** the phone number itself) |
| `WHATSAPP_CLOUD_ACCESS_TOKEN` | Meta access token (starts with `EAA`); temporary tokens expire after 24h, System User tokens are permanent |
| `WHATSAPP_CLOUD_APP_SECRET` | 32-char hex app secret used to verify inbound webhook signatures |
| `WHATSAPP_CLOUD_VERIFY_TOKEN` | Shared secret for Meta's webhook verification handshake (auto-generated by the setup wizard) |
| `WHATSAPP_CLOUD_ALLOWED_USERS` | Comma-separated `wa_id`s (phone numbers with country code, no `+`) allowed to message the bot |
| `WHATSAPP_CLOUD_ALLOW_ALL_USERS` | Allow all WhatsApp Cloud senders without an allowlist (`true`/`false`) |
| `WHATSAPP_CLOUD_APP_ID` | Optional Meta App ID (for future analytics integration) |
| `WHATSAPP_CLOUD_WABA_ID` | Optional WhatsApp Business Account ID (for future analytics integration) |
| `WHATSAPP_CLOUD_WEBHOOK_HOST` | Interface the inbound webhook server binds to (default `0.0.0.0`) |
| `WHATSAPP_CLOUD_WEBHOOK_PORT` | Port the inbound webhook server binds to (default `8090`) |
| `WHATSAPP_CLOUD_WEBHOOK_PATH` | URL path Meta posts inbound messages to (default `/whatsapp/webhook`) |
| `WHATSAPP_CLOUD_API_VERSION` | Meta Graph API version to call (default `v20.0`) |
| `WHATSAPP_CLOUD_HOME_CHANNEL` | `wa_id` to use as the bot's home channel (for cron jobs etc.) |
| `WHATSAPP_CLOUD_DM_POLICY` | DM gating for the Cloud adapter (`open`/`allowlist`/`disabled`); falls back to `WHATSAPP_DM_POLICY` when unset |
| `WHATSAPP_CLOUD_ALLOW_FROM` | Comma-separated senders allowed when `dm_policy: allowlist` (bare `wa_id`s; Baileys-style JIDs are normalized) |
| `WHATSAPP_CLOUD_GROUP_POLICY` | Group gating for the Cloud adapter (`open`/`allowlist`/`disabled`); falls back to `WHATSAPP_GROUP_POLICY` when unset |
| `WHATSAPP_CLOUD_GROUP_ALLOW_FROM` | Comma-separated group chat IDs allowed when `group_policy: allowlist` |
| `SIGNAL_HTTP_URL` | signal-cli daemon HTTP endpoint (for example `http://127.0.0.1:8080`) |
| `SIGNAL_ACCOUNT` | Bot phone number in E.164 format |
| `SIGNAL_ALLOWED_USERS` | Comma-separated E.164 phone numbers or UUIDs |
| `SIGNAL_GROUP_ALLOWED_USERS` | Comma-separated group IDs, or `*` for all groups |
| `SIGNAL_HOME_CHANNEL_NAME` | Display name for the Signal home channel |
| `SIGNAL_IGNORE_STORIES` | Ignore Signal stories/status updates |
| `SIGNAL_ALLOW_ALL_USERS` | Allow all Signal users without an allowlist |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID (shared with telephony skill) |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token (shared with telephony skill; also used for webhook signature validation) |
| `TWILIO_PHONE_NUMBER` | Twilio phone number in E.164 format (shared with telephony skill) |
| `SMS_WEBHOOK_URL` | Public URL for Twilio signature validation — must match the webhook URL in Twilio Console (required) |
| `SMS_WEBHOOK_PORT` | Webhook listener port for inbound SMS (default: `8080`) |
| `SMS_WEBHOOK_HOST` | Webhook bind address (default: `127.0.0.1`) |
| `SMS_INSECURE_NO_SIGNATURE` | Set to `true` to disable Twilio signature validation (local dev only — not for production) |
| `SMS_ALLOWED_USERS` | Comma-separated E.164 phone numbers allowed to chat |
| `SMS_ALLOW_ALL_USERS` | Allow all SMS senders without an allowlist |
| `SMS_HOME_CHANNEL` | Phone number for cron job / notification delivery |
| `SMS_HOME_CHANNEL_NAME` | Display name for the SMS home channel |
| `EMAIL_ADDRESS` | Email address for the Email gateway adapter |
| `EMAIL_PASSWORD` | Password or app password for the email account |
| `EMAIL_IMAP_HOST` | IMAP hostname for the email adapter |
| `EMAIL_IMAP_PORT` | IMAP port |
| `EMAIL_SMTP_HOST` | SMTP hostname for the email adapter |
| `EMAIL_SMTP_PORT` | SMTP port |
| `EMAIL_ALLOWED_USERS` | Comma-separated email addresses allowed to message the bot |
| `EMAIL_HOME_ADDRESS` | Default recipient for proactive email delivery |
| `EMAIL_HOME_ADDRESS_NAME` | Display name for the email home target |
| `EMAIL_POLL_INTERVAL` | Email polling interval in seconds |
| `EMAIL_ALLOW_ALL_USERS` | Allow all inbound email senders |
| `DINGTALK_CLIENT_ID` | DingTalk bot AppKey from developer portal ([open.dingtalk.com](https://open.dingtalk.com)) |
| `DINGTALK_CLIENT_SECRET` | DingTalk bot AppSecret from developer portal |
| `DINGTALK_ALLOWED_USERS` | Comma-separated DingTalk user IDs allowed to message the bot |
| `DINGTALK_WEBHOOK_URL` | Static robot webhook URL for cross-platform / cron delivery. |
| `DINGTALK_HOME_CHANNEL` | Default conversation ID for cron / notification delivery. |
| `DINGTALK_HOME_CHANNEL_NAME` | Display name for the DingTalk home channel. |
| `FEISHU_APP_ID` | Feishu/Lark bot App ID from [open.feishu.cn](https://open.feishu.cn/) |
| `FEISHU_APP_SECRET` | Feishu/Lark bot App Secret |
| `FEISHU_DOMAIN` | `feishu` (China) or `lark` (international). Default: `feishu` |
| `FEISHU_CONNECTION_MODE` | `websocket` (recommended) or `webhook`. Default: `websocket` |
| `FEISHU_ENCRYPT_KEY` | Optional encryption key for webhook mode |
| `FEISHU_VERIFICATION_TOKEN` | Optional verification token for webhook mode |
| `FEISHU_ALLOWED_USERS` | Comma-separated Feishu user IDs allowed to message the bot |
| `FEISHU_ALLOW_BOTS` | `none` (default) / `mentions` / `all` — accept inbound messages from other bots. See [bot-to-bot messaging](../user-guide/messaging/feishu.md#bot-to-bot-messaging) |
| `FEISHU_REQUIRE_MENTION` | `true` (default) / `false` — whether group messages must @mention the bot. Override per-chat via `group_rules.<chat_id>.require_mention`. |
| `FEISHU_HOME_CHANNEL` | Feishu chat ID for cron delivery and notifications |
| `FEISHU_HOME_CHANNEL_NAME` | Display name for the Feishu home channel. |
| `FEISHU_ALLOW_ALL_USERS` | Allow any Feishu user to trigger the bot (dev only). |
| `WECOM_BOT_ID` | WeCom AI Bot ID from admin console |
| `WECOM_SECRET` | WeCom AI Bot secret |
| `WECOM_WEBSOCKET_URL` | Custom WebSocket URL (default: `wss://openws.work.weixin.qq.com`) |
| `WECOM_ALLOWED_USERS` | Comma-separated WeCom user IDs allowed to message the bot |
| `WECOM_HOME_CHANNEL` | WeCom chat ID for cron delivery and notifications |
| `WECOM_CALLBACK_CORP_ID` | WeCom enterprise Corp ID for callback self-built app |
| `WECOM_CALLBACK_CORP_SECRET` | Corp secret for the self-built app |
| `WECOM_CALLBACK_AGENT_ID` | Agent ID of the self-built app |
| `WECOM_CALLBACK_TOKEN` | Callback verification token |
| `WECOM_CALLBACK_ENCODING_AES_KEY` | AES key for callback encryption |
| `WECOM_CALLBACK_HOST` | Callback server bind address (default: `0.0.0.0`) |
| `WECOM_CALLBACK_PORT` | Callback server port (default: `8645`) |
| `WECOM_CALLBACK_ALLOWED_USERS` | Comma-separated user IDs for allowlist |
| `WECOM_CALLBACK_ALLOW_ALL_USERS` | Set `true` to allow all users without an allowlist |
| `WEIXIN_ACCOUNT_ID` | Weixin account ID obtained via QR login through iLink Bot API |
| `WEIXIN_TOKEN` | Weixin authentication token obtained via QR login through iLink Bot API |
| `WEIXIN_BASE_URL` | Override Weixin iLink Bot API base URL (default: `https://ilinkai.weixin.qq.com`) |
| `WEIXIN_CDN_BASE_URL` | Override Weixin CDN base URL for media (default: `https://novac2c.cdn.weixin.qq.com/c2c`) |
| `WEIXIN_DM_POLICY` | Direct message policy: `open`, `allowlist`, `pairing`, `disabled` (default: `open`) |
| `WEIXIN_GROUP_POLICY` | Group message policy: `open`, `allowlist`, `disabled` (default: `disabled`) |
| `WEIXIN_ALLOWED_USERS` | Comma-separated Weixin user IDs allowed to DM the bot |
| `WEIXIN_GROUP_ALLOWED_USERS` | Comma-separated Weixin **group chat IDs** (not member user IDs) allowed to interact with the bot. The variable name is legacy — it expects group IDs. Only takes effect when iLink actually delivers group events; QR-login iLink bot identities (`...@im.bot`) typically don't receive ordinary WeChat group messages. |
| `WEIXIN_HOME_CHANNEL` | Weixin chat ID for cron delivery and notifications |
| `WEIXIN_HOME_CHANNEL_NAME` | Display name for the Weixin home channel |
| `WEIXIN_ALLOW_ALL_USERS` | Allow all Weixin users without an allowlist (`true`/`false`) |
| `BLUEBUBBLES_SERVER_URL` | BlueBubbles server URL (e.g. `http://192.168.1.10:1234`) |
| `BLUEBUBBLES_PASSWORD` | BlueBubbles server password |
| `BLUEBUBBLES_WEBHOOK_HOST` | Webhook listener bind address (default: `127.0.0.1`) |
| `BLUEBUBBLES_WEBHOOK_PORT` | Webhook listener port (default: `8645`) |
| `BLUEBUBBLES_HOME_CHANNEL` | Phone/email for cron/notification delivery |
| `BLUEBUBBLES_ALLOWED_USERS` | Comma-separated authorized users |
| `BLUEBUBBLES_ALLOW_ALL_USERS` | Allow all users (`true`/`false`) |
| `QQ_APP_ID` | QQ Bot App ID from [q.qq.com](https://q.qq.com) |
| `QQ_CLIENT_SECRET` | QQ Bot App Secret from [q.qq.com](https://q.qq.com) |
| `QQ_STT_API_KEY` | API key for external STT fallback provider (optional, used when QQ built-in ASR returns no text) |
| `QQ_STT_BASE_URL` | Base URL for external STT provider (optional) |
| `QQ_STT_MODEL` | Model name for external STT provider (optional) |
| `QQ_ALLOWED_USERS` | Comma-separated QQ user openIDs allowed to message the bot |
| `QQ_GROUP_ALLOWED_USERS` | Comma-separated QQ group IDs for group @-message access |
| `QQ_ALLOW_ALL_USERS` | Allow all users (`true`/`false`, overrides `QQ_ALLOWED_USERS`) |
| `QQBOT_HOME_CHANNEL` | QQ user/group openID for cron delivery and notifications |
| `QQBOT_HOME_CHANNEL_NAME` | Display name for the QQ home channel |
| `QQ_PORTAL_HOST` | Override the QQ portal host (set to `sandbox.q.qq.com` to route through the sandbox gateway; default: `q.qq.com`). |
| `QQ_SANDBOX` | Enable QQ sandbox mode for development testing (`true`/`false`) |
| `MATTERMOST_URL` | Mattermost server URL (e.g. `https://mm.example.com`) |
| `MATTERMOST_TOKEN` | Bot token or personal access token for Mattermost |
| `MATTERMOST_ALLOWED_USERS` | Comma-separated Mattermost user IDs allowed to message the bot |
| `MATTERMOST_ALLOW_ALL_USERS` | Allow any Mattermost user to trigger the bot (dev only). |
| `MATTERMOST_ALLOWED_CHANNELS` | If set, the bot only responds in these channels (whitelist). |
| `MATTERMOST_HOME_CHANNEL` | Channel ID for proactive message delivery (cron, notifications) |
| `MATTERMOST_REQUIRE_MENTION` | Require `@mention` in channels (default: `true`). Set to `false` to respond to all messages. |
| `MATTERMOST_FREE_RESPONSE_CHANNELS` | Comma-separated channel IDs where bot responds without `@mention` |
| `MATTERMOST_REPLY_MODE` | Reply style: `thread` (threaded replies) or `off` (flat messages, default) |
| `MATRIX_HOMESERVER` | Matrix homeserver URL (e.g. `https://matrix.org`) |
| `MATRIX_ACCESS_TOKEN` | Matrix access token for bot authentication |
| `MATRIX_USER_ID` | Matrix user ID (e.g. `@hermes:matrix.org`) — required for password login, optional with access token |
| `MATRIX_PASSWORD` | Matrix password (alternative to access token) |
| `MATRIX_ALLOWED_USERS` | Comma-separated Matrix user IDs allowed to message the bot (e.g. `@alice:matrix.org`) |
| `MATRIX_ALLOW_ALL_USERS` | Allow any Matrix user to trigger the bot (dev only). |
| `MATRIX_HOME_CHANNEL` | Default room ID for cron / notification delivery. |
| `MATRIX_HOME_CHANNEL_NAME` | Display name for the Matrix home room. |
| `MATRIX_ALLOWED_ROOMS` | Comma-separated Matrix room IDs allowed to trigger bot responses |
| `MATRIX_HOME_ROOM` | Room ID for proactive message delivery (e.g. `!abc123:matrix.org`) |
| `MATRIX_ENCRYPTION` | Enable end-to-end encryption (`true`/`false`, default: `false`) |
| `MATRIX_E2EE_MODE` | Matrix E2EE behavior: `off`, `optional`, or `required`. Overrides `MATRIX_ENCRYPTION` when set. |
| `MATRIX_DEVICE_ID` | Stable Matrix device ID for E2EE persistence across restarts (e.g. `HERMES_BOT`). Without this, E2EE keys rotate every startup and historic-room decrypt breaks. |
| `MATRIX_REACTIONS` | Enable processing-lifecycle emoji reactions on inbound messages (default: `true`). Set to `false` to disable. |
| `MATRIX_REQUIRE_MENTION` | Require `@mention` in rooms (default: `true`). Set to `false` to respond to all messages. |
| `MATRIX_FREE_RESPONSE_ROOMS` | Comma-separated room IDs where bot responds without `@mention` |
| `MATRIX_IGNORE_USER_PATTERNS` | Comma-separated regular expressions for Matrix bridge/appservice ghost user IDs to ignore |
| `MATRIX_PROCESS_NOTICES` | Process inbound Matrix `m.notice` events (default: `false`) |
| `MATRIX_SESSION_SCOPE` | Matrix session scope for project rooms: `auto`, `room`, or `thread` (default: `auto`) |
| `MATRIX_TOOLS_ALLOW_REDACTION` | Allow Matrix message redaction tool execution (default: `false`) |
| `MATRIX_TOOLS_ALLOW_INVITES` | Allow Matrix invite tool execution (default: `false`) |
| `MATRIX_TOOLS_ALLOW_ROOM_CREATE` | Allow Matrix room creation tool execution (default: `false`) |
| `MATRIX_ALLOW_ROOM_MENTIONS` | Allow outbound `@room` mentions to notify all room members (default: `false`) |
| `MATRIX_AUTO_THREAD` | Auto-create threads for room messages (default: `true`) |
| `MATRIX_DM_AUTO_THREAD` | Auto-create threads for DM messages in Matrix (default: `false`) |
| `MATRIX_DM_MENTION_THREADS` | Create a thread when bot is `@mentioned` in a DM (default: `false`) |
| `MATRIX_APPROVAL_REQUIRE_SENDER` | Require approval/model-picker reactions to come from the original requester when known (default: `true`) |
| `MATRIX_APPROVAL_TIMEOUT_SECONDS` | Timeout for Matrix reaction approval/model-picker prompts (default: `300`) |
| `MATRIX_ALLOW_PUBLIC_ROOMS` | Allow Matrix room-creation tools to create public rooms (default: `false`) |
| `MATRIX_MAX_MEDIA_BYTES` | Maximum Matrix media upload/download size in bytes (default: `104857600`) |
| `MATRIX_RECOVERY_KEY` | Recovery key for cross-signing verification after device key rotation. Recommended for E2EE setups with cross-signing enabled. |
| `MATRIX_RECOVERY_KEY_OUTPUT_FILE` | Optional one-time path for a generated Matrix recovery key. Created with mode `0600` and never overwritten. |
| `HASS_TOKEN` | Home Assistant Long-Lived Access Token (enables HA platform + tools) |
| `HASS_URL` | Home Assistant URL (default: `http://homeassistant.local:8123`) |
| `WEBHOOK_ENABLED` | Enable the webhook platform adapter (`true`/`false`) |
| `WEBHOOK_PORT` | HTTP server port for receiving webhooks (default: `8644`) |
| `WEBHOOK_SECRET` | Global HMAC secret for webhook signature validation (used as fallback when routes don't specify their own) |
| `API_SERVER_ENABLED` | Enable the OpenAI-compatible API server (`true`/`false`). Runs alongside other platforms. |
| `API_SERVER_KEY` | Bearer token for API server authentication. Required whenever the API server is enabled. |
| `API_SERVER_CORS_ORIGINS` | Comma-separated browser origins allowed to call the API server directly (for example `http://localhost:3000,http://127.0.0.1:3000`). Default: disabled. |
| `API_SERVER_PORT` | Port for the API server (default: `8642`) |
| `API_SERVER_HOST` | Host/bind address for the API server (default: `127.0.0.1`). `API_SERVER_KEY` is still required on loopback; use a narrow `API_SERVER_CORS_ORIGINS` allowlist for browser access. |
| `API_SERVER_MODEL_NAME` | Model name advertised on `/v1/models`. Defaults to the profile name (or `hermes-agent` for the default profile). Useful for multi-user setups where frontends like Open WebUI need distinct model names per connection. |
| `GATEWAY_PROXY_URL` | URL of a remote Hermes API server to forward messages to ([proxy mode](/user-guide/messaging/matrix#proxy-mode-e2ee-on-macos)). When set, the gateway handles platform I/O only — all agent work is delegated to the remote server. Also configurable via `gateway.proxy_url` in `config.yaml`. |
| `GATEWAY_PROXY_KEY` | Bearer token for authenticating with the remote API server in proxy mode. Must match `API_SERVER_KEY` on the remote host. |
| `MESSAGING_CWD` | Deprecated compatibility fallback for gateway working directory. Prefer `terminal.cwd` in `config.yaml`. |
| `GATEWAY_ALLOWED_USERS` | Comma-separated user IDs allowed across all platforms |
| `GATEWAY_ALLOW_ALL_USERS` | Allow all users without allowlists (`true`/`false`, default: `false`) |

### Web控制台与Hermes Desktop

用于[Web控制台](/user-guide/features/web-dashboard)的认证，以及实现[Hermes Desktop与远程后端连接](/user-guide/features/web-dashboard#connecting-hermes-desktop-to-a-remote-backend)的认证。遵循仅使用密钥的惯例，凭证应存储在`~/.hermes/.env`文件中；而OAuth的`client_id`则建议设置在`config.yaml`的`dashboard.oauth`字段下（若两者同时设置，则以环境变量中的值为准）。

系统预置了三种控制台认证提供程序。对于远程Hermes Desktop连接或任何面向互联网的控制台，推荐的认证方式是**OAuth（Nous Portal）**——需设置`HERMES_DASHBOARD_OAUTH_CLIENT_ID`（可通过`hermes dashboard register`命令进行配置）。内置的**用户名/密码**认证提供程序（`HERMES_DASHBOARD_BASIC_AUTH_*`）适用于位于可信局域网内或VPN后的后端，是速度最快的选择，但不适合直接暴露在公共互联网上。若需使用自建的身份验证服务，可使用**自托管OIDC**认证提供程序（`HERMES_DASHBOARD_OIDC_*`）。无论采用哪种方式，只要通过非回环地址绑定（即使用`hermes dashboard --host 0.0.0.0`命令），系统就会启用认证机制。更多详情请参阅[Web控制台 → 认证](/user-guide/features/web-dashboard#authentication-gated-mode)。

| Variable | Description |
|----------|-------------|
| `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` | Username for the bundled username/password dashboard-auth provider (`plugins/dashboard_auth/basic`). Activates the provider when set together with a password. Overrides `dashboard.basic_auth.username`. |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | Plaintext password for the basic provider (hashed in-memory at load). Wins over a config `password_hash` so you can rotate via env. Overrides `dashboard.basic_auth.password`. |
| `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH` | scrypt password hash for the basic provider (preferred — no plaintext at rest). Compute with `python -c "from plugins.dashboard_auth.basic import hash_password; print(hash_password('PW'))"`. Overrides `dashboard.basic_auth.password_hash`. |
| `HERMES_DASHBOARD_BASIC_AUTH_SECRET` | HMAC key (32+ bytes, base64/hex/raw) signing the basic provider's stateless session tokens. Set explicitly so sessions survive restarts / span multiple workers; blank → random per-process (you'll be logged out on every restart). Overrides `dashboard.basic_auth.secret`. |
| `HERMES_DASHBOARD_BASIC_AUTH_TTL_SECONDS` | Access-token lifetime for the basic provider (default 12h). Overrides `dashboard.basic_auth.session_ttl_seconds`. |
| `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | OAuth client id (`agent:{instance_id}`) for the gated/public dashboard, activating the Nous (`plugins/dashboard_auth/nous`) provider. Overrides `dashboard.oauth.client_id`. Provision it with `hermes dashboard register`. |
| `HERMES_DASHBOARD_PUBLIC_URL` | Complete public URL the dashboard is reached at behind a reverse proxy. It controls OAuth callback construction, adds its exact hostname to the HTTP Host/WebSocket Origin guard, and requires the auth gate for non-loopback public hosts even when the backend binds to loopback. Overrides `dashboard.public_url`. |
| `HERMES_DASHBOARD_OIDC_ISSUER` | OIDC issuer URL for the bundled self-hosted OIDC provider (`plugins/dashboard_auth/self_hosted`). Required to activate it. Overrides `dashboard.oauth.self_hosted.issuer`. |
| `HERMES_DASHBOARD_OIDC_CLIENT_ID` | Public OIDC client id (authorization-code + PKCE) for the self-hosted OIDC provider. Required to activate it. Overrides `dashboard.oauth.self_hosted.client_id`. |
| `HERMES_DASHBOARD_OIDC_SCOPES` | Requested OIDC scopes for the self-hosted OIDC provider (default `openid profile email`). Overrides `dashboard.oauth.self_hosted.scopes`. |
| `HERMES_DESKTOP_REMOTE_URL` | (Desktop side) Base URL of the remote backend, e.g. `http://host:9119`. When set, overrides the in-app Gateway URL; you still sign in from the Gateway settings panel (OAuth redirect or username/password, whichever the backend advertises). |
| `HERMES_DESKTOP_HERMES` | Desktop backend command override. Used by packagers/Nix or troubleshooting to point Electron at a specific `hermes` executable after backend probing. |
| `HERMES_DESKTOP_HERMES_ROOT` | Desktop source-checkout override used by `hermes desktop --hermes-root`; checked before the packaged first-launch install or an existing `hermes` on `PATH`. |
| `HERMES_DESKTOP_IGNORE_EXISTING` | Set to `1` to make Desktop ignore an existing `hermes` on `PATH` during backend resolution. Equivalent to `hermes desktop --ignore-existing`. |
| `HERMES_DESKTOP_CWD` | Initial project directory for Desktop chat sessions. Set by `hermes desktop --cwd`. |
| `HERMES_DESKTOP_PYTHON` | Absolute path to a Python interpreter for the backend, checked before Electron auto-resolves one for the source checkout. Used by worktree dev helpers (see [TUI & Desktop from Worktrees](../developer-guide/worktree-ui-dev.md)) to reuse a shared venv. |
| `HERMES_DESKTOP_DEV_SERVER` | Vite dev-server URL the Electron shell loads instead of the packaged bundle (e.g. `http://127.0.0.1:5174`). Set automatically by `npm run dev`; only relevant when hacking on the app. |
| `HERMES_DESKTOP_CDP_PORT` | Overrides the Chrome DevTools Protocol port the renderer exposes on `127.0.0.1` for DOM/CSS inspection tooling (default `9222`). Dev-server runs (`npm run dev`, `hgui`) open it automatically; a packaged app never does, and no value here changes that. Set to `off` to disable it on a dev run. Anything that can reach the port can execute code in the renderer. |

### Microsoft Graph（Teams 会议）

用于后续 Teams 会议摘要处理流程的 Microsoft Graph REST 客户端的仅应用级凭据。有关 Azure 平台的操作指南以及所需的精确 API 权限，请参阅[注册 Microsoft Graph 应用](/guides/microsoft-graph-app-registration)。

| 变量 | 描述 |
|------|------|
| `MSGRAPH_TENANT_ID` | 用于 Graph 应用注册的 Azure AD 租户 ID（目录 GUID）。 |
| `MSGRAPH_CLIENT_ID` | Azure 应用注册的应用（客户端）ID。 |
| `MSGRAPH_CLIENT_SECRET` | 应用注册的客户端密钥值。请将其存储在 `~/.hermes/.env` 文件中，并设置权限为 `chmod 600`；需通过 Azure 平台定期更换该密钥。 |
| `MSGRAPH_SCOPE` | 用于客户端凭据令牌请求的 OAuth2 范围（默认值：`https://graph.microsoft.com/.default`）。 |
| `MSGRAPH_AUTHORITY_URL` | Microsoft 身份平台授权地址（默认值：`https://login.microsoftonline.com`）。仅在国家/主权云环境中需进行替换（例如 GCC High 地区的地址为 `https://login.microsoftonline.us`）。 |

### Microsoft Graph Webhook 监听器

用于接收 Graph 事件（Teams 会议、日历、聊天等）的入站变更通知监听器。有关设置及安全强化措施，请参阅[Microsoft Graph Webhook 监听器](/user-guide/messaging/msgraph-webhook)。

| 变量 | 描述 |
|----------|-------------|
| `MSGRAPH_WEBHOOK_ENABLED` | 启用 `msgraph_webhook` 网关平台（值为 `true`/`1`/`yes`）。 |
| `MSGRAPH_WEBHOOK_PORT` | 监听器绑定的端口（默认值为 `8646`）。 |
| `MSGRAPH_WEBHOOK_CLIENT_STATE` | 会在每条通知中重复出现的共享密钥，用于与 `hmac.compare_digest` 进行比对。可通过 `openssl rand -hex 32` 生成该值。 |
| `MSGRAPH_WEBHOOK_ACCEPTED_RESOURCES` | 以逗号分隔的 Graph 资源路径/模式允许列表（例如 `communications/onlineMeetings,chats/*/messages`）。末尾的 `*` 表示前缀匹配。若该字段为空，则允许所有资源。 |
| `MSGRAPH_WEBHOOK_ALLOWED_SOURCE_CIDRS` | 允许向监听器发送请求的 CIDR 范围，以逗号分隔（例如 `52.96.0.0/14,52.104.0.0/14`）。若该字段为空，则允许所有来源（为默认值）。在正式环境中，建议仅允许 Microsoft Graph 公布的出站访问范围。 |

### Teams 会议摘要推送功能

仅当启用了 [`teams_pipeline` 插件](/user-guide/messaging/msgraph-webhook) 时才会使用此功能。相关设置也可通过 `config.yaml` 文件中的 `platforms.teams.extra` 配置——当两者同时设置时，环境变量优先生效。更多详情请参阅 [Microsoft Teams → 会议摘要推送功能](/user-guide/messaging/teams#meeting-summary-delivery-teams-meeting-pipeline)。

| 变量 | 描述 |
|----------|-------------|
| `TEAMS_DELIVERY_MODE` | `graph` 或 `incoming_webhook`。 |
| `TEAMS_INCOMING_WEBHOOK_URL` | Teams 生成的 webhook URL；当 `TEAMS_DELIVERY_MODE=incoming_webhook` 时为必填项。 |
| `TEAMS_GRAPH_ACCESS_TOKEN` | 用于 Graph 模式传输的预获取委托访问令牌。通常无需使用——若未设置，该工具会自动回退至 `MSGRAPH_*` 应用凭据。 |
| `TEAMS_TEAM_ID` | 用于频道传输的目标团队 ID（`graph` 模式）。 |
| `TEAMS_CHANNEL_ID` | 目标频道 ID（需与 `TEAMS_TEAM_ID` 配合使用）。 |
| `TEAMS_CHAT_ID` | 目标一对一或群组聊天 ID（在 `graph` 模式中可作为团队+频道的替代选项）。 |

### LINE 消息传递 API

由内置的 LINE 平台插件（`plugins/platforms/line/`）所使用。有关完整设置指南，请参阅 [消息网关 → LINE](/user-guide/messaging/line)。

| Variable | Description |
|----------|-------------|
| `LINE_CHANNEL_ACCESS_TOKEN` | Long-lived channel access token from the LINE Developers Console (Messaging API tab). Required. |
| `LINE_CHANNEL_SECRET` | Channel secret (Basic settings tab); used for HMAC-SHA256 webhook signature verification. Required. |
| `LINE_HOST` | Webhook bind host (default: `0.0.0.0`). |
| `LINE_PORT` | Webhook bind port (default: `8646`). |
| `LINE_PUBLIC_URL` | Public HTTPS base URL (e.g. `https://my-tunnel.example.com`). Required for image / audio / video sends — LINE only accepts HTTPS-reachable URLs. |
| `LINE_ALLOWED_USERS` | Comma-separated user IDs allowed to DM the bot (`U`-prefixed). |
| `LINE_ALLOWED_GROUPS` | Comma-separated group IDs the bot will respond in (`C`-prefixed). |
| `LINE_ALLOWED_ROOMS` | Comma-separated room IDs the bot will respond in (`R`-prefixed). |
| `LINE_ALLOW_ALL_USERS` | Dev-only escape hatch — accepts any source. Default: `false`. |
| `LINE_HOME_CHANNEL` | Default delivery target for cron jobs with `deliver: line`. |
| `LINE_SLOW_RESPONSE_THRESHOLD` | Seconds before the slow-LLM Template Buttons postback fires (default: `45`). Set `0` to disable and always Push-fallback. |
| `LINE_PENDING_TEXT` | Bubble text shown alongside the postback button. |
| `LINE_BUTTON_LABEL` | Postback button label (default: `Get answer`). |
| `LINE_DELIVERED_TEXT` | Reply when an already-delivered postback is tapped again (default: `Already replied ✅`). |
| `LINE_INTERRUPTED_TEXT` | Reply when a `/stop`-orphaned postback button is tapped (default: `Run was interrupted before completion.`). |
| `LINE_EXPIRED_TEXT` | Reply when a postback button whose cached answer is gone (expired / lost with process state) is tapped (default: `That request has expired — send your message again.`). |

### ntfy（推送通知）

[ntfy](https://ntfy.sh/) 是一款轻量级的基于 HTTP 的推送通知服务。您可以通过 [ntfy 移动应用](https://ntfy.sh/docs/subscribe/phone/) 订阅某个主题，然后向该主题发送消息以与 Agent 进行交互。

| 参数 | 说明 |
|------|------|
| `NTFY_TOPIC` | 需要订阅的主题（用于接收消息）。为必填项。 |
| `NTFY_SERVER_URL` | 服务器地址（默认值为 `https://ntfy.sh`）。如需保障隐私，可指定自托管的 ntfy 服务器地址。 |
| `NTFY_TOKEN` | 可选的认证令牌。支持Bearer令牌（例如 `tk_xyz`），也支持基本认证格式的 `user:pass`。 |
| `NTFY_PUBLISH_TOPIC` | 用于发送回复的主题（默认值为 `NTFY_TOPIC`）。 |
| `NTFY_MARKDOWN` | 设置为 `true` 可在回复中添加 `X-Markdown: true` 标头。默认值为 `false`。 |
| `NTFY_ALLOWED_USERS` | 允许列表（视为用户 ID；在 ntfy 中则对应主题名称）。通常该值与 `NTFY_TOPIC` 相同。 |
| `NTFY_ALLOW_ALL_USERS` | 仅开发人员可使用——仅在受访问控制的私有主题中才安全。默认值为 `false`。 |
| `NTFY_HOME_CHANNEL` | 对于使用 `deliver: ntfy` 的定时任务，其默认消息发送目标。 |
| `NTFY_HOME_CHANNEL_NAME` | 主题通道的显示名称（默认值为主题名称）。 |

在将不受信任的主题用于部署之前，请先参阅 [ntfy 消息传递指南](/user-guide/messaging/ntfy)，尤其是 **身份模型** 部分。

### IRC

用于将 Hermes 连接到 IRC 服务器。无需任何外部依赖。详情请参阅 [IRC 消息传递指南](/user-guide/messaging/irc)。

| 变量 | 描述 |
|----------|-------------|
| `IRC_SERVER` | IRC 服务器主机名（例如 `irc.libera.chat`），为必填项。 |
| `IRC_CHANNEL` | 需要加入的频道（例如 `#hermes`）；多个频道请用逗号分隔，为必填项。 |
| `IRC_NICKNAME` | 机器人昵称（默认值为 `hermes-bot`），为必填项。 |
| `IRC_PORT` | 服务器端口（使用 TLS 时默认为 `6697`，不使用 TLS 时为 `6667`）。 |
| `IRC_USE_TLS` | 是否使用 TLS（取值 `true`/`false`；在端口 `6697` 上默认为 `true`）。 |
| `IRC_SERVER_PASSWORD` | 用于 `PASS` 命令的服务器密码（可选）。 |
| `IRC_NICKSERV_PASSWORD` | 连接时自动执行 IDENTIFY 操作所需的 NickServ 密码（可选）。 |
| `IRC_ALLOWED_USERS` | 允许与机器人交流的昵称列表，各昵称之间用逗号分隔。 |
| `IRC_ALLOW_ALL_USERS` | 允许频道中的任何用户与机器人交流（仅开发人员使用）。 |
| `IRC_HOME_CHANNEL` | 用于定时任务执行/通知发送的频道（默认值为 `IRC_CHANNEL`）。 |

### SimpleX

通过本地的 `simplex-chat` 守护进程，将 Hermes 连接到 [SimpleX Chat](https://simplex.chat/) 网络。详情请参阅 [SimpleX 消息传递指南](/user-guide/messaging/simplex)。

| 变量 | 描述 |
|----------|-------------|
| `SIMPLEX_WS_URL` | simplex-chat 守护进程的 WebSocket 地址（例如 `ws://127.0.0.1:5225`）。 |
| `SIMPLEX_ALLOWED_USERS` | 允许与机器人对话的 SimpleX 联系人 ID，以逗号分隔。 |
| `SIMPLEX_ALLOW_ALL_USERS` | 允许任何联系人都与机器人对话（仅适用于开发者——此选项会禁用白名单机制）。 |
| `SIMPLEX_AUTO_ACCEPT` | 自动接受来自其他联系人的加入请求（默认值为 `true`）。 |
| `SIMPLEX_GROUP_ALLOWED` | 机器人应加入的 SimpleX 群组 ID，以逗号分隔；若设置为 `*` 则允许加入任意群组。如未设置，则完全忽略群组消息（这是更安全的默认选项——否则处于群组中的机器人会处理所有成员的消息）。 |
| `SIMPLEX_HOME_CHANNEL` | 用于定时任务/通知发送的默认联系人/群组 ID。 |
| `SIMPLEX_HOME_CHANNEL_NAME` | 主通道的显示名称（默认值为该通道的 ID）。 |

### Photon

可通过 Node sidecar 将 Hermes 连接到 [Photon](https://photon.codes/) / Spectrum（iMessage 及其他 Spectrum 平台）。请参阅 [Photon 消息传递指南](/user-guide/messaging/photon)。

| Variable | Description |
|----------|-------------|
| `PHOTON_PROJECT_ID` | Spectrum project id (the project's `spectrumProjectId`; set by `hermes photon setup`). |
| `PHOTON_PROJECT_SECRET` | Project secret paired with the Spectrum project id (set by `hermes photon setup`). |
| `PHOTON_ALLOWED_USERS` | Comma-separated E.164 phone numbers allowed to talk to the bot. |
| `PHOTON_ALLOW_ALL_USERS` | Allow any sender to trigger the bot (dev only — disables allowlist). |
| `PHOTON_REQUIRE_MENTION` | Ignore group-chat messages unless they match a mention wake word (`true`/`false`, default `false`). |
| `PHOTON_MENTION_PATTERNS` | Mention wake-word regexes for group chats (JSON list or comma/newline-separated; defaults to Hermes wake words). |
| `PHOTON_HOME_CHANNEL` | Default Photon target for cron / notification delivery: Spectrum space id, DM GUID, or bare E.164 phone number. |
| `PHOTON_HOME_CHANNEL_NAME` | Human label for the home channel. |
| `PHOTON_MARKDOWN` | Send agent replies as markdown — iMessage renders it natively, other Spectrum platforms degrade to plain text (`true`/`false`, default `true`). |
| `PHOTON_REACTIONS` | Tapback 👀/👍/👎 on messages as processing status and route tapbacks on bot messages to the agent (`true`/`false`, default `false`). |
| `PHOTON_READ_RECEIPTS` | Mark inbound iMessages read after forwarding to Hermes (`true`/`false`, default `true`). |
| `PHOTON_TELEMETRY` | Enable Spectrum SDK telemetry in the sidecar (`true`/`false`, default `false`; toggle with `hermes photon telemetry on|off`). |
| `PHOTON_SIDECAR_PORT` | Loopback port for the Node sidecar control + inbound channel (default `8789`). |
| `PHOTON_SIDECAR_AUTOSTART` | Spawn the Node sidecar on connect (`true`/`false`, default `true`). |
| `PHOTON_NODE_BIN` | Path to the node binary (default: `shutil.which('node')`). |
| `PHOTON_DASHBOARD_HOST` | Photon Dashboard API host (default `https://app.photon.codes`). |
| `PHOTON_SPECTRUM_HOST` | Photon Spectrum API host (default `https://spectrum.photon.codes`). |

### Buzz（Nostr 社区）

| 变量 | 描述 |
|------|------|
| `BUZZ_RELAY_URL` | Buzz 社区中继的基址（例如：`https://mycommunity.communities.buzz.xyz`） |
| `BUZZ_PRIVATE_KEY` | 用于代理 Buzz 身份的 Nostr 私钥（nsec 或十六进制格式）——这是唯一的 Buzz 密钥 |
| `BUZZ_CREDENTIALS_FILE` | 包含 nsec 格式凭证的 JSON 文件（当未设置 `BUZZ_PRIVATE_KEY` 时作为备用） |
| `BUZZ_CHANNELS` | 需要关注的频道 UUID，以逗号分隔（默认：所有已加入的频道） |
| `BUZZ_HOME_CHANNEL` | 用于定时任务/通知发送的频道 UUID（默认为第一个被关注的频道） |
| `BUZZ_ALLOWED_USERS` | 允许与代理通信的 npubs 或十六进制公钥，以逗号分隔 |
| `BUZZ_ALLOW_ALL_USERS` | 是否允许任何社区成员与代理通信（`true`/`false`） |
| `BUZZ_TRANSPORT` | 数据接收方式：`auto`（默认，基于 WebSocket 并支持轮询作为备用）、`websocket` 或 `poll` |
| `BUZZ_POLL_INTERVAL` | 数据轮询检查的间隔时间（单位：秒，默认值为 `4`） |
| `BUZZ_AUTH_TAG` | 用于 NIP-42 WebSocket 认证的可选 NIP-OA 所有者认证标签 JSON 文件 |
| `BUZZ_CLI_PATH` | buzz CLI 可执行文件的路径（默认为 PATH 中的 `buzz`，其次为 `~/bin/buzz`） |

### Microsoft Teams（适配器）

此处指的是 Microsoft Teams 平台适配器（Bot Framework / Azure AD），与上文提到的 [Microsoft Graph（Teams 会议）](#microsoft-graph-teams-meetings) 集成不同。详情请参阅 [Teams 消息传递指南](/user-guide/messaging/teams)。

| 变量 | 描述 |
|------|------|
| `TEAMS_CLIENT_ID` | Azure AD 应用程序（Bot Framework）的客户端 ID。 |
| `TEAMS_CLIENT_SECRET` | Azure AD 应用程序的客户端密钥。 |
| `TEAMS_TENANT_ID` | 托管该机器人应用程序的 Azure AD 租户 ID。 |
| `TEAMS_HOST` | Webhook 绑定主机（默认值：未设置 → 双栈模式，支持 IPv4 和 IPv6 接口）。 |
| `TEAMS_PORT` | Webhook 监听端口（Bot Framework 默认值为 `3978`）。 |
| `TEAMS_ALLOWED_USERS` | 允许与机器人交互的 Teams 用户 ID 或 UPN，以逗号分隔。 |
| `TEAMS_ALLOW_ALL_USERS` | 允许任何 Teams 用户触发该机器人（仅开发人员使用）。 |
| `TEAMS_HOME_CHANNEL` | 用于定时任务执行或发送通知的默认聊天频道/频道 ID。 |
| `TEAMS_HOME_CHANNEL_NAME` | Teams 主页频道的显示名称。 |

### Raft

| 变量 | 描述 |
|------|------|
| `RAFT_PROFILE` | Raft 代理的配置文件标识符——设置该值后即可自动启用相应适配器。 |

### 高级消息发送调优

针对不同平台提供的高级参数，用于控制外出消息批量发送的频率。大多数用户无需调整这些参数；系统已预设默认值，可在确保流畅体验的同时遵守各平台的速率限制。

| Variable | Description |
|----------|-------------|
| `HERMES_TELEGRAM_TEXT_BATCH_DELAY_SECONDS` | Grace window before flushing a queued Telegram text chunk (default: `0.6`). |
| `HERMES_TELEGRAM_TEXT_BATCH_SPLIT_DELAY_SECONDS` | Delay between split chunks when a single Telegram message exceeds the length limit (default: `2.0`). |
| `HERMES_SIMPLEX_TEXT_BATCH_DELAY` | Quiet-period seconds (default: `0.8`) used to concatenate rapid-fire inbound text messages into a single MessageEvent — same pattern as Telegram's text batching. |
| `HERMES_TELEGRAM_MEDIA_BATCH_DELAY_SECONDS` | Grace window before flushing queued Telegram media (default: `0.6`). |
| `HERMES_TELEGRAM_FOLLOWUP_GRACE_SECONDS` | Delay before sending a follow-up after the agent finishes, to avoid racing the last stream chunk. |
| `HERMES_TELEGRAM_HTTP_CONNECT_TIMEOUT` / `_READ_TIMEOUT` / `_WRITE_TIMEOUT` / `_POOL_TIMEOUT` | Override the underlying `python-telegram-bot` HTTP timeouts (seconds). |
| `HERMES_TELEGRAM_INIT_TIMEOUT` | Per-attempt cap (seconds) on the Telegram `initialize()` connect chain during gateway startup, so an unreachable fallback-IP chain can't block startup indefinitely (default: `30`). |
| `HERMES_TELEGRAM_HTTP_POOL_SIZE` | Max concurrent HTTP connections to the Telegram API. |
| `HERMES_TELEGRAM_DISABLE_FALLBACK_IPS` | Disable the hard-coded Cloudflare fallback IPs used when DNS fails (`true`/`false`). |
| `HERMES_DISCORD_TEXT_BATCH_DELAY_SECONDS` | Grace window before flushing a queued Discord text chunk (default: `0.6`). |
| `HERMES_DISCORD_TEXT_BATCH_SPLIT_DELAY_SECONDS` | Delay between split chunks when a Discord message exceeds the length limit (default: `2.0`). |
| `HERMES_DISCORD_LIVENESS_INTERVAL_SECONDS` | Compatibility/manual override for `discord.websocket_liveness_interval_seconds`. Interval for sampling the active Discord Gateway WebSocket (default: `15`; set to `0` to disable). Prefer the `config.yaml` key. |
| `HERMES_DISCORD_LIVENESS_FAILURE_THRESHOLD` | Compatibility/manual override for `discord.websocket_liveness_failure_threshold`. Consecutive unhealthy WebSocket samples before forcing a reconnect (default: `2`). Prefer the `config.yaml` key. |
| `HERMES_MATRIX_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` | Matrix equivalents of the Telegram batch knobs. |
| `HERMES_FEISHU_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` / `_MAX_CHARS` / `_MAX_MESSAGES` | Feishu batcher tuning — delay, split delay, max chars per message, max messages per batch. |
| `HERMES_FEISHU_MEDIA_BATCH_DELAY_SECONDS` | Feishu media flush delay. |
| `HERMES_FEISHU_DEDUP_CACHE_SIZE` | Size of the Feishu webhook dedup cache (default: `1024`). |
| `HERMES_WECOM_TEXT_BATCH_DELAY_SECONDS` / `_SPLIT_DELAY_SECONDS` | WeCom batcher tuning. |
| `HERMES_VISION_DOWNLOAD_TIMEOUT` | Timeout in seconds for downloading an image before handing it to vision models (default: `30`). |
| `HERMES_VISION_MAX_CONCURRENCY` | Max concurrent image **encode/resize** bursts across the whole process (override for `auxiliary.vision.max_concurrency`; default: host CPU core count, no ceiling). Bounds only the CPU-bound encode step so a video-frame fan-out can't saturate every core and starve the event loop — the LLM calls stay fully concurrent. Values `< 1` are ignored. |
| `HERMES_RESTART_DRAIN_TIMEOUT` | Gateway: seconds to wait for active runs to drain on `/restart` before forcing the restart (default: `900`). |
| `HERMES_GATEWAY_PLATFORM_CONNECT_TIMEOUT` | Per-platform connect timeout during gateway startup and reconnect (seconds; `0`/negative waits indefinitely). Applies to the connect attempt *and* the Discord adapter's ready-wait, so accounts with many slash commands to sync don't get killed mid-startup. Bridged from `gateway.platform_connect_timeout` in `config.yaml` (default `30`); this env var is the manual override and wins if set explicitly. |
| `HERMES_GATEWAY_BUSY_INPUT_MODE` | Default gateway busy-input behavior: `queue`, `steer`, or `interrupt`. Can be overridden for the active profile with `/busy`. |
| `HERMES_GATEWAY_BUSY_ACK_ENABLED` | Whether the gateway sends an acknowledgment message (⚡/⏳/⏩) when a user sends input while the agent is busy (default: `true`). Set to `false` to suppress these messages entirely — the input is still queued/steered/interrupts as normal, only the chat reply is silenced. Bridged from `display.busy_ack_enabled` in `config.yaml`. |
| `HERMES_GATEWAY_NO_SUPERVISE` | Inside the s6-overlay Docker image, opt out of auto-supervision when running `hermes gateway run` and use pre-s6 foreground semantics (no auto-restart, gateway is the container's main process). Truthy values: `1`, `true`, `yes`. Equivalent to the `--no-supervise` CLI flag. No-op outside the s6 image. |
| `HERMES_GATEWAY_BOOTSTRAP_STATE` | Inside the s6-overlay Docker image, declare the gateway's **initial** supervised state on a fresh volume. On a blank volume there is no persisted `gateway_state.json`, so the boot reconciler registers the `gateway-default` slot but leaves it **down** (it only auto-starts when the last recorded state was `running`). Set this to `running` and the first-boot setup hook seeds `gateway_state.json` *before* the reconciler runs, so the gateway comes up on the very first boot. Only the literal value `running` is honoured. First-boot-only: an existing `gateway_state.json` is never overwritten, so a deliberately-stopped gateway stays stopped across restarts. No-op outside the s6 image. |
| `GATEWAY_RELAY_URL` | Experimental relay connector WebSocket base URL. When set, the gateway registers the generic `relay` adapter and dials the connector outbound. Mirrors `gateway.relay_url` in `config.yaml`. |
| `GATEWAY_RELAY_ID` | Relay gateway identifier assigned by `hermes gateway enroll` or managed self-provisioning. Mirrors `gateway.relay_id`. |
| `GATEWAY_RELAY_SECRET` | Per-gateway relay secret used to authenticate the WebSocket. If this is already configured, managed self-provisioning is skipped. Mirrors `gateway.relay_secret`. |
| `GATEWAY_RELAY_DELIVERY_KEY` | Connector-issued delivery key retained for relay/passthrough authentication compatibility. Current relay inbound messages arrive on the outbound WebSocket rather than a gateway-side HTTP receiver. |
| `GATEWAY_RELAY_ENROLL_TOKEN` | Enrollment token consumed by `hermes gateway enroll` when `--token` is not passed explicitly. |
| `GATEWAY_RELAY_PLATFORM` | Optional platform name advertised in the relay capability descriptor. |
| `GATEWAY_RELAY_BOT_ID` | Optional bot identifier advertised in the relay capability descriptor. |
| `GATEWAY_RELAY_ENDPOINT` | Optional gateway endpoint advertised for connector modes that need a callback/passthrough URL; not required for the default WS-only inbound relay path. Mirrors `gateway.relay_endpoint`. |
| `GATEWAY_RELAY_ROUTE_KEYS` | Comma-separated relay route keys advertised to the connector. Mirrors `gateway.relay_route_keys`. |
| `HERMES_FILE_MUTATION_VERIFIER` | Enable the per-turn file-mutation verifier footer (default: `true`). When enabled, Hermes appends an advisory listing any `write_file` / `patch` calls that failed during the turn and were not superseded by a successful write. Set to `0`, `false`, `no`, or `off` to suppress. Mirrors `display.file_mutation_verifier` in `config.yaml`; the env var wins when set. |
| `HERMES_CRON_TIMEOUT` | Inactivity timeout for cron job agent runs in seconds (default: `600`). The agent can run indefinitely while actively calling tools or receiving stream tokens — this only triggers when idle. Set to `0` for unlimited. |
| `HERMES_CRON_SCRIPT_TIMEOUT` | Timeout for pre-run scripts attached to cron jobs in seconds (default: `3600`). Bounds the script only — skill/agent jobs use the separate `HERMES_CRON_TIMEOUT` inactivity budget. Also configurable via `cron.script_timeout_seconds` in `config.yaml`. |
| `HERMES_CRON_MEDIA_SEND_TIMEOUT` | Timeout for each media attachment send during cron delivery via a live gateway adapter, in seconds (default: `300`). Raise it if large attachments (long TTS audio, big exports) time out during upload. Also configurable via `cron.media_send_timeout_seconds` in `config.yaml`. |
| `HERMES_CRON_MAX_PARALLEL` | Max cron jobs run in parallel per tick (default: `4`). |

## NeMo Relay

| 变量 | 描述 |
|----------|-------------|
| `HERMES_NEMO_RELAY_PLUGINS_TOML` | 指定 Hermes 核心在全局范围内加载的标准 NeMo Relay `plugins.toml` 文件的路径。若未设置该变量，Hermes 将不会初始化 Relay 中间件、动态插件或导出功能。已被移除的 `HERMES_NEMO_RELAY_ATOF_*` 和 `HERMES_NEMO_RELAY_ATIF_*` 变量将被忽略，应在其对应的配置文件中设置相关参数。详情请参阅 [NeMo Relay 可观测性配置](https://docs.nvidia.com/nemo/relay/configure-plugins/observability/about)。 |

## Agent 行为

| Variable | Description |
|----------|-------------|
| `HERMES_MAX_ITERATIONS` | Max tool-calling iterations per conversation (default: 500) |
| `HERMES_INFERENCE_MODEL` | Override model name at process level (takes priority over `config.yaml` for the session). Also settable via `-m`/`--model` flag. |
| `HERMES_YOLO_MODE` | Set to `1` to bypass dangerous-command approval prompts. Equivalent to `--yolo`. |
| `HERMES_ACCEPT_HOOKS` | Auto-approve any unseen shell hooks declared in `config.yaml` without a TTY prompt. Equivalent to `--accept-hooks` or `hooks_auto_accept: true`. |
| `HERMES_IGNORE_USER_CONFIG` | Skip `~/.hermes/config.yaml` and use built-in defaults (credentials in `.env` still load). Equivalent to `--ignore-user-config`. |
| `HERMES_IGNORE_RULES` | Skip auto-injection of `AGENTS.md`, `SOUL.md`, `.cursorrules`, memory, and preloaded skills. Equivalent to `--ignore-rules`. |
| `HERMES_SAFE_MODE` | Troubleshooting mode: disable ALL customizations — skips plugin discovery, MCP server loading, and shell-hook registration. Set automatically by `--safe-mode` (which also sets the two flags above). |
| `HERMES_TOOL_PROGRESS` | Unsupported since the config-v12 support floor — the variable is ignored. Use `display.tool_progress` in `config.yaml`. |
| `HERMES_TOOL_PROGRESS_MODE` | Deprecated compatibility variable for tool progress mode (still read by the gateway as a fallback). Prefer `display.tool_progress` in `config.yaml`. |
| `HERMES_HUMAN_DELAY_MODE` | Response pacing: `off`/`natural`/`custom` |
| `HERMES_HUMAN_DELAY_MIN_MS` | Custom delay range minimum (ms) |
| `HERMES_HUMAN_DELAY_MAX_MS` | Custom delay range maximum (ms) |
| `HERMES_QUIET` | Suppress non-essential output (`true`/`false`) |
| `CODEX_HOME` | When [Codex app-server runtime](../user-guide/features/codex-app-server-runtime) is enabled, override the directory Codex CLI reads its config + auth from (default: `~/.codex`). Hermes' migration writes the managed block to `<CODEX_HOME>/config.toml`. |
| `HERMES_KANBAN_TASK` | Set by the kanban dispatcher when spawning a worker (task UUID). Workers and the spawned `hermes-tools` MCP subprocess inherit it so kanban tools gate correctly. Don't set manually. |
| `HERMES_ACP_SKIP_CONFIGURED_MCP` | Set by an [ACP host](../user-guide/features/acp#host-integration) on the Hermes subprocess it spawns. `1` skips starting the globally configured `config.yaml` MCP servers before the ACP JSON-RPC loop, for hosts that pass the session's MCP servers through `session/new` themselves. Servers supplied by the ACP session are still registered; any other value keeps the default. Don't set manually. |
| `HERMES_API_TIMEOUT` | LLM API call timeout in seconds (default: `1800`) |
| `HERMES_API_CALL_STALE_TIMEOUT` | Non-streaming stale-call timeout in seconds (default: `90`). Auto-disabled for local providers when left unset, and may scale upward for very large contexts. Also configurable via `providers.<id>.stale_timeout_seconds` or `providers.<id>.models.<model>.stale_timeout_seconds` in `config.yaml`. |
| `HERMES_STREAM_READ_TIMEOUT` | Streaming socket read timeout in seconds (default: `120`). Auto-increased to `HERMES_API_TIMEOUT` for local providers. Increase if local LLMs time out during long code generation. |
| `HERMES_STREAM_STALE_TIMEOUT` | Stale stream detection timeout in seconds (default: `180`). Auto-disabled for local providers. Triggers connection kill if no chunks arrive within this window. |
| `HERMES_LOCAL_STREAM_STALE_TIMEOUT` | Stale stream ceiling for local providers (Ollama, oMLX, llama-cpp) in seconds (default: `900`). When the base stale timeout is at its default and a local endpoint is detected, this finite ceiling replaces the former infinite disable so a wedged local server eventually trips the detector instead of hanging forever. Also configurable via `agent.local_stream_stale_timeout` in `config.yaml`. |
| `HERMES_STREAM_RETRIES` | Number of mid-stream reconnect attempts on transient network errors (default: `3`). |
| `HERMES_STREAM_STALE_GIVEUP` | Cross-turn circuit breaker: after this many consecutive stale kills (streaming or non-streaming) with no completed response, abort each call immediately with an actionable error instead of re-waiting out the stale timeout (default: `5`, `0` disables). Resets on any completed response, `/model` switch, fallback activation, or turn-start primary restore. |
| `HERMES_AGENT_TIMEOUT` | Gateway inactivity timeout for a running agent in seconds (default: `1800`, 30 minutes). Resets on every tool call and streamed token. Set to `0` to disable. |
| `HERMES_GATEWAY_MAX_STARTS` | Respawn-storm circuit breaker: maximum gateway (re)starts allowed within the window before an exponential backoff is slept to break the storm (default: `5`, `0` disables). Also configurable via `gateway.respawn_storm.max_starts` in `config.yaml`. |
| `HERMES_GATEWAY_START_WINDOW_S` | Respawn-storm breaker window in seconds (default: `120`). Also configurable via `gateway.respawn_storm.window_seconds` in `config.yaml`. |
| `HERMES_AGENT_TIMEOUT_WARNING` | Gateway: send a warning message after this many seconds of inactivity (default: 75% of `HERMES_AGENT_TIMEOUT`). |
| `HERMES_AGENT_NOTIFY_INTERVAL` | Gateway: interval in seconds between progress notifications on long-running agent turns. |
| `HERMES_CHECKPOINT_TIMEOUT` | Timeout for filesystem checkpoint creation in seconds (default: `30`). |
| `HERMES_EXEC_ASK` | Enable execution approval prompts in gateway mode (`true`/`false`) |
| `HERMES_ENABLE_PROJECT_PLUGINS` | Enable auto-discovery of repo-local plugins from `./.hermes/plugins/` for both the agent loader and the dashboard web server. Accepts the standard truthy set: `1` / `true` / `yes` / `on` (case-insensitive). Everything else — including `0`, `false`, `no`, `off`, and the empty string — is treated as **disabled** (default). Note: as of GHSA-5qr3-c538-wm9j (#29156) the dashboard web server refuses to auto-import a project plugin's Python `api` file even when this var is enabled — project plugins may extend the UI via static JS/CSS but their backend routes are only loaded when moved under `~/.hermes/plugins/`. |
| `HERMES_PLUGINS_DEBUG` | `1`/`true` to surface verbose plugin-discovery logs on stderr — directories scanned, manifests parsed, skip reasons, and full tracebacks on parse or `register()` failure. Aimed at plugin authors. |
| `HERMES_BACKGROUND_NOTIFICATIONS` | Background process notification mode in gateway: `concise` (default), `all`, `result`, `error`, `off` |
| `HERMES_EPHEMERAL_SYSTEM_PROMPT` | Ephemeral system prompt injected at API-call time (never persisted to sessions) |
| `HERMES_PREFILL_MESSAGES_FILE` | Path to a JSON file of ephemeral prefill messages injected at API-call time. |
| `HERMES_ALLOW_PRIVATE_URLS` | `true`/`false` — allow tools to fetch localhost/private-network URLs. Off by default in gateway mode. |
| `HERMES_REDACT_SECRETS` | `true`/`false` — control secret redaction in tool output, logs, and chat responses (default: `true`). |
| `HERMES_WRITE_SAFE_ROOT` | Optional directory prefix that **hard-blocks** `write_file`/`patch` writes outside the listed roots (no approval prompt). Supports multiple directories separated by `os.pathsep` (`:` on Unix, `;` on Windows). See [HERMES_WRITE_SAFE_ROOT](#hermes_write_safe_root) below. |
| `HERMES_DISABLE_LAZY_INSTALLS` | Internal bridge var set automatically in the official Docker image to prevent runtime dependency installs into the immutable `/opt/hermes` tree. The user-facing equivalent is `security.allow_lazy_installs: false` in `config.yaml`; do not set this in `.env`. |
| `HERMES_DISABLE_FILE_STATE_GUARD` | Set to `1` to turn off the "file changed since you read it" guard on `patch`/`write_file`. |
| `HERMES_BUNDLED_SKILLS` | Comma-separated override for the list of bundled skills loaded at startup. |
| `HERMES_OPTIONAL_SKILLS` | Comma-separated list of optional-skill names to auto-install on first run. |
| `HERMES_DEBUG_INTERRUPT` | Set to `1` to log detailed interrupt/cancel tracing to `agent.log`. |
| `HERMES_DUMP_REQUESTS` | Dump API request payloads to log files (`true`/`false`) |
| `HERMES_DUMP_REQUEST_STDOUT` | Dump API request payloads to stdout instead of log files. |
| `HERMES_OAUTH_TRACE` | Set to `1` to log OAuth token exchange and refresh attempts. Includes redacted timing info. |
| `HERMES_AGENT_HELP_GUIDANCE` | Append additional guidance text to the system prompt for custom deployments. |
| `HERMES_AGENT_LOGO` | Override the ASCII banner logo at CLI startup. |
| `DELEGATION_MAX_CONCURRENT_CHILDREN` | Max parallel subagents per `delegate_task` batch (default: `3`, floor of 1, no ceiling). Also configurable via `delegation.max_concurrent_children` in `config.yaml` — the config value takes priority. |

### HERMES_WRITE_SAFE_ROOT {#hermes_write_safe_root}

当设置此变量后，`write_file` 和 `patch` 指令仅能作用于所列目录前缀内的路径。任何位于这些安全目录之外的路径都会**立即被拒绝**——此类写入操作无需经过危险命令审批流程，也不会出现允许用户强制执行的提示。

官方 Docker 镜像将 `HERMES_WRITE_SAFE_ROOT` 和 `HERMES_HOME` 同时设置为 `/opt/data`，以此确保智能体无法脱离已挂载的数据卷进行操作。

**除非您确实希望对写入操作进行沙箱限制，否则请勿将此变量添加到 `~/.hermes/.env` 文件中。** 一个常见的错误是将该变量指向项目目录，却期望智能体能够编辑 `~/.hermes/cron/jobs.json`、`~/.hermes/skills/` 或配置文件下的脚本——这些路径均位于沙箱之外，因此任何针对它们的 `write_file`/`patch` 操作都会因“超出 HERMES_WRITE_SAFE_ROOT 范围”而失败。

若需同时允许保存工作区数据与 Hermes 状态，请列出这两个目录前缀（顺序无关）：

```bash
export HERMES_WRITE_SAFE_ROOT=/path/to/project:/home/you/.hermes
```

若要恢复正常的写入功能，请将该变量重置或从 `.env` 文件中删除（但仍受凭据路径禁止列表的限制——详见[文件写入安全机制](../user-guide/security.md#file-write-safety)）。

## 接口参数

| 变量名 | 描述 |
|--------|------|
| `HERMES_TUI` | 当其值为 `1` 时，启动[TUI界面](../user-guide/tui.md)而非传统的命令行界面，效果等同于使用 `--tui` 参数。 |
| `HERMES_TUI_DIR` | 预置的 `ui-tui/` 目录路径（该目录必须包含 `dist/entry.js` 文件以及完整的 `node_modules` 文件）。发行版和 Nix 可通过此参数跳过首次启动时的 `npm install` 操作。 |
| `HERMES_TUI_RESUME` | 启动时根据编号恢复特定的 TUI 会话。设置该参数后，执行 `hermes --tui` 命令时会直接继承已存在的会话，而不会新建会话——这有助于在连接中断或终端崩溃后重新接入。 |
| `HERMES_TUI_THEME` | 强制指定 TUI 的颜色主题：`light`、`dark`，或是 6 位十六进制值表示的背景色（例如 `ffffff` 或 `1a1a2e`）。若未设置该参数，Hermes 会通过 `COLORFGBG` 及终端背景色查询自动检测主题；对于未设置 `COLORFGBG` 的终端（如 Ghostty、Warp、iTerm2 等），此参数可覆盖自动检测结果。 |
| `HERMES_INFERENCE_MODEL` | 不修改 `config.yaml` 文件即可强制指定 `hermes -z` / `hermes chat` 命令使用的模型。需与 `--provider` 参数配合使用。对于需要每次运行时都覆盖默认模型的脚本化工具（如任务扫描器、CI 环境、批量处理程序）而言，此参数非常实用。 |

## 会话设置 |

| 变量 | 描述 |
|------|------|
| `HERMES_SESSION_ID` | **会自动导出到Hermes启动的每一个工具子进程**中，包括`terminal`、`execute_code`、持久化shell、Docker/Singularity后端以及委托运行的子代理。该变量由代理自行设置为当前会话ID；从这些工具中调用的用户脚本可读取该值，从而将其输出、遥测数据或副作用与最初的Hermes会话关联起来。**不建议手动设置此变量**——从父shell覆盖该值仅能在代理未运行时生效，且一旦代理开始新的会话，该覆盖值就会被重置。 |
| `AI_AGENT` | **由CLI及网关入口点设置为`hermes-agent`**（前提是外部框架尚未设置该值），并会被导出到所有终端工具shell中——包括远程后端（如Docker、SSH、Modal、Daytona、Singularity、Vercel）。这是目前用于标识子进程所属代理的通用标准，各类通用工具（例如huggingface_hub的代理检测功能）都会读取该值以判断自身正在AI代理环境下运行。其值与公共代理框架注册表中的Hermes标识一致。请勿手动设置。 |
| `HERMES_AGENT` | **由CLI及网关入口点设置为`true`**，并会被导出到所有终端工具shell中，以便子进程能够明确识别自己正在Hermes内部运行。请勿手动设置。 |

## 上下文压缩（仅限config.yaml）

上下文压缩功能仅通过 `config.yaml` 文件进行配置，不存在相关的环境变量。阈值设置位于 `compression:` 块中，而摘要生成模型及提供方则归属于 `auxiliary.compression:` 下。

```yaml
compression:
  enabled: true
  threshold: 0.50
  target_ratio: 0.20         # fraction of threshold to preserve as recent tail
  protect_last_n: 20         # minimum recent messages to keep uncompressed
```

:::info 旧版本迁移
包含 `compression.summary_model`、`compression.summary_provider` 以及 `compression.summary_base_url` 的旧配置，在首次加载时会被自动迁移为 `auxiliary.compression.*` 格式。
:::

## 辅助任务覆盖参数

| 参数名 | 描述 |
|--------|------|
| `AUXILIARY_VISION_PROVIDER` | 用于覆盖视觉任务的提供方 |
| `AUXILIARY_VISION_MODEL` | 用于覆盖视觉任务的模型 |
| `AUXILIARY_VISION_BASE_URL` | 用于视觉任务的 OpenAI 兼容直接端点地址 |
| `AUXILIARY_VISION_API_KEY` | 与 `AUXILIARY_VISION_BASE_URL` 配对的 API 密钥 |

:::note
`AUXILIARY_WEB_EXTRACT_*` 系列参数已过时：`web_extract` 功能及浏览器快照不再依赖辅助大型语言模型。长页面和快照的内容会被固定长度截断，完整文本则会存储在磁盘上，以便通过 `read_file` 功能实现分页读取。
:::

对于特定任务对应的直接端点，Hermes 会使用该任务配置的 API 密钥或 `OPENAI_API_KEY`，而不会在这些自定义端点上重复使用 `OPENROUTER_API_KEY`。

## 备用提供方（仅适用于 config.yaml）

主要模型的备用链配置完全通过 `config.yaml` 完成——不存在相应的环境变量。只需在文件顶部添加一个包含 `provider` 和 `model` 键值的 `fallback_providers` 列表，即可在主模型出现故障时实现自动切换。那些提供方被设置为 `auto` 的辅助任务，在触发 Hermes 内置的辅助发现流程之前，也会先查询此备用链。

```yaml
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
```

为保持向后兼容性，系统仍会读取旧版那种仅基于单一提供者的 `fallback_model` 配置格式，但新配置应使用 `fallback_providers`。如需为特定任务配置辅助策略，请在 `config.yaml` 中使用 `auxiliary.<task>.fallback_chain` 选项；目前暂无对应的环境变量。

详情请参阅 [Fallback Providers](/user-guide/features/fallback-providers) 文档。

## 提供者路由配置（仅限 config.yaml）

这些配置需添加到 `~/.hermes/config.yaml` 文件的 `provider_routing` 部分中：

| 键值 | 描述 |
|-----|-------------|
| `sort` | 提供者排序规则：`"price"`（默认）、`"throughput"` 或 `"latency"` |
| `only` | 允许使用的提供者标识符列表（例如：`["anthropic", "google"]`） |
| `ignore` | 应跳过的提供者标识符列表 |
| `order` | 按指定顺序尝试的提供者标识符列表 |
| `require_parameters` | 仅使用能支持所有请求参数的提供者（`true`/`false`） |
| `data_collection` | 设置为 `"allow"`（默认）或 `"deny"`，用于排除会存储数据的提供者 |

:::tip
建议使用 `hermes config set` 命令来设置环境变量——该命令会自动将它们保存到相应的文件中（敏感信息保存为 `.env` 文件，其他配置则保存在 `config.yaml` 中）。
:::
