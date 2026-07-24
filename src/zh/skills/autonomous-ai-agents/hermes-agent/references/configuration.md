# 配置、工具集与语音功能

可通过 `hermes config edit` 或 `hermes config set section.key value` 进行编辑。
完整参考文档：https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### 配置章节（最常用的键值）

| 章节 | 键选项 |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length`, `aliases` |
| `agent` | `max_turns` (90), `tool_use_enforcement`, `service_tier`, `verify_on_stop` |
| `terminal` | `backend` (local/docker/ssh/modal/daytona/singularity), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `interface` (cli/tui), `language`, `show_reasoning`, `show_cost`, `pet` |
| `approvals` | `mode` (smart/manual/off), `timeout`, `cron_mode` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral/elevenlabs/deepinfra) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts/gemini/piper/kittentts/deepinfra/xai) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider`, `write_approval` |
| `security` | `redact_secrets`, `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `max_concurrent_children`, `max_iterations` (50), `max_spawn_depth` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |
| `curator` | `enabled`, `consolidate` (false, 选择性合并辅助模型), `interval_hours`, `stale_after_days` |

使用 `hermes config check` 可检测旧配置中缺失的章节。

### 工具集

可通过交互式命令 `hermes tools` 或命令 `hermes tools enable/disable NAME` 来启用/禁用工具集。
完整列表参见 `toolsets.py` 文件中的 `TOOLSETS` 字典（`_HERMES_CORE_TOOLS` 是大多数平台默认使用的工具包）。

| 工具集 | 功能说明 |
|---------|----------|
| `web` / `search` | 网页搜索及信息提取功能，或仅提供搜索功能 |
| `browser` | 浏览器自动化操作（支持 Browserbase、Camofox 或本地 Chromium） |
| `terminal` | 命令行操作及进程管理 |
| `file` | 文件的读取、写入、搜索和修改 |
| `code_execution` | 存放式 Python 代码执行环境 |
| `coding` | 基于 LSP 的代码编辑辅助功能 |
| `computer_use` | 桌面 GUI 控制功能（通过 cua-driver 实现） |
| `vision` | 图像分析功能 |
| `image_gen` | 图像生成及图像编辑功能 |
| `video` / `video_gen` | 视频分析/生成功能 |
| `x_search` | X（Twitter）平台搜索功能（需使用 X OAuth 或 API 密钥） |
| `tts` | 文本转语音功能 |
| `skills` | 技能浏览与管理功能 |
| `memory` | 跨会话持久化内存功能 |
| `session_search` | 搜索历史对话内容 |
| `context_engine` | 可插拔的上下文引擎接口 |
| `project` | 基于名称的多文件夹工作区管理工具 |
| `delegation` | 向子智能体分配任务功能 |
| `cronjob` | 定时任务管理功能 |
| `clarify` | 向用户提问以获取更多信息 |
| `todo` | 会话内任务规划功能 |
| `kanban` | 多智能体工作队列管理工具（需由工作节点访问） |
| `debugging` | 额外的调试工具（默认关闭） |
| `safe` | 为受限会话设计的低风险工具集 |
| `spotify`, `homeassistant`, `discord`, `discord_admin`, `feishu_doc`, `feishu_drive`, `yuanbao` | 各类服务集成功能（需提供相应凭证才能使用） |

工具变更仅在启动新会话时 `/reset` 命令执行后生效，绝不会在对话进行中更改，以此确保提示词缓存的有效性。

## 语音功能

### STT（语音转文本）

来自消息平台的语音消息会自动被转录为文本。

```yaml
stt:
  enabled: true
  provider: local   # local (faster-whisper, free) | groq | openai | mistral | elevenlabs | deepinfra
  local:
    model: base     # tiny, base, small, medium, large-v3
```

自动检测优先级：本地 Faster-Whisper（通过 `pip install faster-whisper` 安装）→ Groq（需提供 `GROQ_API_KEY`，支持免费套餐）→ OpenAI（需提供 `VOICE_TOOLS_OPENAI_KEY`）→ Mistral Voxtral（需提供 `MISTRAL_API_KEY`）。

### 文本转语音功能 (TTS)

| 服务提供商 | 环境变量 | 是否免费 |
|----------|---------|-------|
| Edge TTS（默认） | 无 | 是 |
| ElevenLabs | `ELEVENLABS_API_KEY` | 支持免费套餐 |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | 需付费 |
| MiniMax | `MINIMAX_API_KEY` | 需付费 |
| Mistral | `MISTRAL_API_KEY` | 需付费 |
| Gemini | `GOOGLE_API_KEY` | 支持免费套餐 |
| NeuTTS / Piper / KittenTTS（本地运行） | 无 | 免费 |

语音指令：`/voice on`（语音对语音模式）、`/voice tts`（始终使用语音模式）、`/voice off`。
