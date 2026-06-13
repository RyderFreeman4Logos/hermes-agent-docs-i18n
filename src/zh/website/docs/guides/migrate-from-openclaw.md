---
sidebar_position: 10
title: "Migrate from OpenClaw"
description: "Complete guide to migrating your OpenClaw / Clawdbot setup to Hermes Agent — what gets migrated, how config maps, and what to check after."
---

# 从 OpenClaw 迁移

`hermes claw migrate` 命令可将您现有的 OpenClaw（或旧版的 Clawdbot/Moldbot）配置导入 Hermes。本指南将详细说明哪些内容会被迁移、配置键的对应关系，以及迁移完成后需要验证的事项。

:::提示
如果您的 OpenClaw 配置使用了多个服务提供商，使用 `hermes setup --portal` 即可将其整合为单一的 OAuth 认证方式——只需一次登录即可使用 300 多个模型以及工具网关。详情请参阅 [Nous Portal](/integrations/nous-portal)。
:::

## 快速入门

```bash
# Preview then migrate (always shows a preview first, then asks to confirm)
hermes claw migrate

# Preview only, no changes
hermes claw migrate --dry-run

# Full migration including API keys, skip confirmation
hermes claw migrate --preset full --migrate-secrets --yes
```

在执行任何更改之前，迁移工具总会先完整预览即将导入的内容。请仔细查看列表，确认无误后再继续。

默认从 `~/.openclaw/` 读取配置。系统会自动检测旧的 `~/.clawdbot/` 或 `~/.moltbot/` 目录，旧的配置文件名（如 `clawdbot.json`、`moltbot.json`）也是如此。

## 选项

| 选项 | 描述 |
|------|-------|
| `--dry-run` | 仅预览——显示迁移内容后停止。 |
| `--preset <name>` | `full`（所有兼容设置）或 `user-data`（排除基础设施相关配置）。默认情况下两种预设均不会导入密钥——需明确使用 `--migrate-secrets` 参数。 |
| `--overwrite` | 遇到冲突时覆盖现有的 Hermes 文件（默认：若计划存在冲突则拒绝应用）。 |
| `--migrate-secrets` | 包含 API 密钥。即使使用 `--preset full` 也必须此选项——没有任何预设会自动导入密钥。 |
| `--no-backup` | 跳过对 `~/.hermes/` 的迁移前压缩包快照的创建（默认情况下，在应用更改前会在 `~/.hermes/backups/pre-migration-*.zip` 下生成一个恢复点存档，可通过 `hermes import` 恢复）。 |
| `--source <path>` | 自定义 OpenClaw 目录路径。 |
| `--workspace-target <path>` | 指定 `AGENTS.md` 的保存位置。 |
| `--skill-conflict <mode>` | `skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过预览后的确认提示。 |

## 将被迁移的内容

### 人物设定、记忆与指令

| 内容 | OpenClaw 来源 | Hermes 目标路径 | 备注 |
|------|----------------|-------------------|------|
| 人物设定 | `workspace/SOUL.md` | `~/.hermes/SOUL.md` | 直接复制 |
| 工作区指令 | `workspace/AGENTS.md` | `--workspace-target` 指定的路径下的 `AGENTS.md` | 需要使用 `--workspace-target` 参数 |
| 长期记忆 | `workspace/MEMORY.md` | `~/.hermes/memories/MEMORY.md` | 会被解析为条目，与现有内容合并并去重，使用 `§` 作为分隔符。 |
| 用户档案 | `workspace/USER.md` | `~/.hermes/memories/USER.md` | 与长期记忆的合并逻辑相同。 |
| 日常记忆文件 | `workspace/memory/*.md` | `~/.hermes/memories/MEMORY.md` | 所有日常记忆文件都会合并到主记忆中。 |

作为备用路径，还会检查 `workspace.default/` 和 `workspace-main/` 中的文件（OpenClaw 在最新版本中将 `workspace/` 重命名为 `workspace-main/`，在多智能体环境中则使用 `workspace-{agentId}`）。

### 技能（4个来源）

| 来源 | OpenClaw 存放位置 | Hermes 目标路径 |
|------|------------------|-------------------|
| 工作区技能 | `workspace/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 托管/共享技能 | `~/.openclaw/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 个人跨项目技能 | `~/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 项目级共享技能 | `workspace/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |

技能冲突可通过 `--skill-conflict` 参数处理：`skip` 表示保留现有的 Hermes 技能，`overwrite` 表示替换它，`rename` 表示创建一个带 `-imported` 后缀的副本。

### 模型与提供者配置

| 内容 | OpenClaw 配置路径 | Hermes 目标路径 | 备注 |
|------|---------------------|-------------------|------|
| 默认模型 | `agents.defaults.model` | `config.yaml` → `model` | 可以是字符串，也可以是 `{primary, fallbacks}` 格式的对象 |
| 自定义提供者 | `models.providers.*` | `config.yaml` → `custom_providers` | 会映射 `baseUrl`、`apiType`/`api` —— 支持简写形式（如 "openai"、"anthropic"）和带连字符的形式（如 "openai-completions"、"anthropic-messages"、"google-generative-ai"） |
| 提供者 API 密钥 | `models.providers.*.apiKey` | `~/.hermes/.env` | 需要使用 `--migrate-secrets` 参数。详情见下文的 [API 密钥解析](#api-key-resolution)。 |

### 智能体行为设置

| 内容 | OpenClaw 配置路径 | Hermes 配置路径 | 映射关系 |
|------|---------------------|-------------------|----------|
| 最大轮次数 | `agents.defaults.timeoutSeconds` | `agent.max_turns` | 计算方式为 `timeoutSeconds / 10`，上限为 200 |
| 详细模式 | `agents.defaults.verboseDefault` | `agent.verbose` | 取值 "off"、"on"、"full" |
| 推理强度 | `agents.defaults.thinkingDefault` | `agent.reasoning_effort` | "always"/"high"/"xhigh" → "high"，"auto"/"medium"/"adaptive" → "medium"，"off"/"low"/"none"/"minimal" → "low" |
| 压缩功能 | `agents.defaults.compaction.mode` | `compression.enabled` | "off" → false，其他值均为 true |
| 压缩模型 | `agents.defaults.compaction.model` | `compression.summary_model` | 直接复制字符串 |
| 人工干预延迟 | `agents.defaults.humanDelay.mode` | `human_delay.mode` | 取值 "natural"、"custom"、"off" |
| 人工干预延迟时间 | `agents.defaults.humanDelay.minMs` / `.maxMs` | `human_delay.min_ms` / `.max_ms` | 直接复制 |
| 时区 | `agents.defaults.userTimezone` | `timezone` | 直接复制字符串 |
| 命令执行超时时间 | `tools.exec.timeoutSec` | `terminal.timeout` | 直接复制（字段名为 `timeoutSec`，而非 `timeout`） |
| Docker 沙箱 | `agents.defaults.sandbox.backend` | `terminal.backend` | "docker" → "docker" |
| Docker 镜像 | `agents.defaults.sandbox.docker.image` | `terminal.docker_image` | 直接复制 |

### 会话重置策略

| OpenClaw 配置路径 | Hermes 配置路径 | 备注 |
|-------------------|-------------------|------|
| `session.reset.mode` | `session_reset.mode` | 取值 "daily"、"idle" 或两者皆有 |
| `session.reset.atHour` | `session_reset.at_hour` | 每日重置的时间点（0–23 之间） |
| `session.reset.idleMinutes` | `session_reset.idle_minutes` | 无活动后的等待分钟数 |

注意：OpenClaw 还有 `session.resetTriggers` 参数（为一个简单的字符串数组，例如 `["daily", "idle"]`）。如果不存在结构化的 `session.reset` 配置，迁移工具会尝试从 `resetTriggers` 中推断设置。

### MCP 服务器

| OpenClaw 字段 | Hermes 字段 | 备注 |
|----------------|-------------|------|
| `mcp.servers.*.command` | `mcp_servers.*.command` | 使用标准输入输出传输方式 |
| `mcp.servers.*.args` | `mcp_servers.*.args` |  |
| `mcp.servers.*.env` | `mcp_servers.*.env` |  |
| `mcp.servers.*.cwd` | `mcp_servers.*.cwd` |  |
| `mcp.servers.*.url` | `mcp_servers.*.url` | 使用 HTTP/SSE 传输方式 |
| `mcp.servers.*.tools.include` | `mcp_servers.*.tools.include` | 工具过滤功能 |
| `mcp.servers.*.tools.exclude` | `mcp_servers.*.tools.exclude` |  |

### 文本转语音（TTS）

TTS 设置会从 **两个** OpenClaw 配置位置读取，优先级如下：

1. `messages.tts.providers.{provider}.*`（标准配置位置）
2. 顶层目录下的 `talk.providers.{provider}.*`（备用位置）
3. 旧格式的扁平键 `messages.tts.{provider}.*`（最旧格式）

| 内容 | Hermes 目标路径 |
|------|-------------------|
| 提供者名称 | `config.yaml` → `tts.provider` |
| ElevenLabs 语音 ID | `config.yaml` → `tts.elevenlabs.voice_id` |
| ElevenLabs 模型 ID | `config.yaml` → `tts.elevenlabs.model_id` |
| OpenAI 模型 | `config.yaml` → `tts.openai.model` |
| OpenAI 语音 | `config.yaml` → `tts.openai.voice` |
| Edge TTS 语音 | `config.yaml` → `tts.edge.voice`（OpenClaw 将 "edge" 改为 "microsoft"，但两者均可被识别） |
| TTS 资源文件 | `~/.hermes/tts/`（直接复制文件） |

### 消息平台配置

| 平台 | OpenClaw 配置路径 | Hermes `.env` 变量名 | 备注 |
|------|---------------------|----------------------|------|
| Telegram | `channels.telegram.botToken` 或 `.accounts.default.botToken` | `TELEGRAM_BOT_TOKEN` | Token 可以是字符串，也可以是 [SecretRef](#secretref-handling) 格式。同时支持扁平结构和基于账户的结构。 |
| Telegram | `credentials/telegram-default-allowFrom.json` | `TELEGRAM_ALLOWED_USERS` | 从 `allowFrom[]` 数组中提取并以逗号分隔的形式存储。 |
| Discord | `channels.discord.token` 或 `.accounts.default.token` | `DISCORD_BOT_TOKEN` |  |
| Discord | `channels.discord.allowFrom` 或 `.accounts.default.allowFrom` | `DISCORD_ALLOWED_USERS` |  |
| Slack | `channels.slack.botToken` 或 `.accounts.default.botToken` | `SLACK_BOT_TOKEN` |  |
| Slack | `channels.slack.appToken` 或 `.accounts.default.appToken` | `SLACK_APP_TOKEN` |  |
| Slack | `channels.slack.allowFrom` 或 `.accounts.default.allowFrom` | `SLACK_ALLOWED_USERS` |  |
| WhatsApp | `channels.whatsapp.allowFrom` 或 `.accounts.default.allowFrom` | `WHATSAPP_ALLOWED_USERS` | 通过 Baileys QR 配对进行身份验证——迁移后需要重新配对。 |
| Signal | `channels.signal.account` 或 `.accounts.default.account` | `SIGNAL_ACCOUNT` |  |
| Signal | `channels.signal.httpUrl` 或 `.accounts.default.httpUrl` | `SIGNAL_HTTP_URL` |  |
| Signal | `channels.signal.allowFrom` 或 `.accounts.default.allowFrom` | `SIGNAL_ALLOWED_USERS` |  |
| Matrix | `channels.matrix.accessToken` 或 `.accounts.default.accessToken` | `MATRIX_ACCESS_TOKEN` | 使用 `accessToken`（而非 `botToken`） |
| Mattermost | `channels.mattermost.botToken` 或 `.accounts.default.botToken` | `MATTERMOST_BOT_TOKEN` |  |

### 其他配置项

| 内容 | OpenClaw 路径 | Hermes 路径 | 备注 |
|------|----------------|--------------|------|
| 审批模式 | `approvals.exec.mode` | `config.yaml` → `approvals.mode` | "auto" → "off"，"always" → "manual"，"smart" → "smart" |
| 命令允许列表 | `exec-approvals.json` | `config.yaml` → `command_allowlist` | 模式规则会被合并并去重 |
| 浏览器 CDP 地址 | `browser.cdpUrl` | `config.yaml` → `browser.cdp_url` |  |
| 浏览器无头模式 | `browser.headless` | `config.yaml` → `browser.headless` |  |
| Brave 搜索密钥 | `tools.web.search.brave.apiKey` | `.env` 文件中的 `BRAVE_API_KEY` | 需要使用 `--migrate-secrets` 参数 |
| 网关认证令牌 | `gateway.auth.token` | `.env` 文件中的 `HERMES_GATEWAY_TOKEN` | 需要使用 `--migrate-secrets` 参数 |
| 工作目录 | `agents.defaults.workspace` | `config.yaml` → `terminal.cwd` | 旧版本迁移结果仍可能以 `MESSAGING_CWD` 作为兼容性备用字段存在。 |

### 归档内容（Hermes 中无直接对应项）

这些内容会被保存到 `~/.hermes/migration/openclaw/<timestamp>/archive/` 目录中，供人工查看：| 类型 | 存储文件 | 在 Hermes 中的重建方式 |
|------|-----------|------------------------|
| `IDENTITY.md` | `archive/workspace/IDENTITY.md` | 合并到 `SOUL.md` 中 |
| `TOOLS.md` | `archive/workspace/TOOLS.md` | Hermes 已内置工具使用说明 |
| `HEARTBEAT.md` | `archive/workspace/HEARTBEAT.md` | 使用定时任务（cron）处理周期性操作 |
| `BOOTSTRAP.md` | `archive/workspace/BOOTSTRAP.md` | 通过上下文文件或技能来实现 |
| 定时任务 | `archive/cron-config.json` | 使用 `hermes cron create` 命令重新创建 |
| 插件 | `archive/plugins-config.json` | 参见[插件指南](/user-guide/features/hooks) |
| Hook/Webhook | `archive/hooks-config.json` | 使用 `hermes webhook` 或网关 Hook |
| 内存后端 | `archive/memory-backend-config.json` | 通过 `hermes honcho` 进行配置 |
| 技能注册表 | `archive/skills-registry-config.json` | 使用 `hermes skills config` 命令 |
| UI/身份配置 | `archive/ui-identity-config.json` | 使用 `/skin` 命令 |
| 日志配置 | `archive/logging-diagnostics-config.json` | 在 `config.yaml` 的日志配置部分进行设置 |
| 多智能体列表 | `archive/agents-list.json` | 使用 Hermes 配置文件 |
| 渠道绑定 | `archive/bindings.json` | 需根据不同平台手动配置 |
| 复杂频道 | `archive/channels-deep-config.json` | 需根据平台手动配置 |

## API 密钥解析

当启用 `--migrate-secrets` 选项时，API 密钥会按优先级从**四个来源**中获取：

1. **配置值** — `models.providers.*.apiKey` 以及 `openclaw.json` 中的 TTS 提供商密钥
2. **环境文件** — `~/.openclaw/.env`（如 `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` 等密钥）
3. **配置中的环境子对象** — `openclaw.json` 中的 `"env"` 或 `"env"."vars"`（部分配置会将密钥存储在此处，而非单独的 `.env` 文件中）
4. **认证配置文件** — `~/.openclaw/agents/main/agent/auth-profiles.json`（各智能体的独立凭证）

配置值具有最高优先级，后续来源仅用于填补剩余的空缺。

### 支持的密钥类型

`OPENROUTER_API_KEY`、`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`DEEPSEEK_API_KEY`、`GEMINI_API_KEY`、`ZAI_API_KEY`、`MINIMAX_API_KEY`、`ELEVENLABS_API_KEY`、`TELEGRAM_BOT_TOKEN`、`VOICE_TOOLS_OPENAI_KEY`

不在此列表中的密钥将不会被复制。

## SecretRef 处理方式

OpenClaw 中用于存储令牌和 API 密钥的配置值有三种格式：

```json
// Plain string
"channels": { "telegram": { "botToken": "123456:ABC-DEF..." } }

// Environment template
"channels": { "telegram": { "botToken": "${TELEGRAM_BOT_TOKEN}" } }

// SecretRef object
"channels": { "telegram": { "botToken": { "source": "env", "id": "TELEGRAM_BOT_TOKEN" } } }
```

此次迁移可处理这三种格式的配置。对于源类型为 `env` 的环境模板及 SecretRef 对象，系统会从 `~/.openclaw/.env` 文件以及 `openclaw.json` 中的 `env` 子对象中查找对应值。而源类型为 `file` 或 `exec` 的 SecretRef 对象则无法自动解析——迁移过程会对此类对象发出警告，这些值需通过 `hermes config set` 手动添加到 Hermes 系统中。

## 迁移完成后

1. **查看迁移报告** —— 迁移完成后会生成该报告，其中会列出已迁移、跳过以及存在冲突的项目数量。

2. **检查归档文件** —— `~/.hermes/migration/openclaw/<timestamp>/archive/` 目录中的所有文件都需要人工处理。

3. **启动新会话** —— 导入的技能和记忆条目仅在新会话中生效，当前会话不会受到影响。

4. **验证 API 密钥** —— 运行 `hermes status` 命令以检查服务提供商的认证状态。

5. **测试消息功能** —— 如果您迁移了平台令牌，请重启网关：`systemctl --user restart hermes-gateway`

6. **检查会话策略** —— 运行 `hermes config show` 命令，确认 `session_reset` 的设置是否符合预期。

7. **重新配对 WhatsApp** —— WhatsApp 使用二维码配对方式（Baileys 协议），而非令牌迁移机制。请运行 `hermes whatsapp` 命令进行配对。

8. **清理归档文件** —— 在确认所有功能正常后，运行 `hermes claw cleanup` 命令将剩余的 OpenClaw 目录重命名为 `.pre-migration/`，以避免状态混淆。

## 故障排除

### “未找到 OpenClaw 目录”

迁移过程会依次检查 `~/.openclaw/`、`~/.clawdbot/` 和 `~/.moltbot/` 这三个目录。如果您的安装路径不在这些位置，可使用 `--source /path/to/your/openclaw` 参数指定路径。

### “未找到服务提供商 API 密钥”

根据 OpenClaw 的版本不同，密钥可能存储在多个位置：`openclaw.json` 文件中 `models.providers.*.apiKey` 字段内、`~/.openclaw/.env` 文件中、`openclaw.json` 的 `env` 子对象中，或是 `agents/main/agent/auth-profiles.json` 文件中。迁移过程会逐一检查这四个位置。如果密钥是通过源类型为 `file` 或 `exec` 的 SecretRef 对象存储的，它们无法自动解析——需通过 `hermes config set` 手动添加。

### 迁移后技能未显示

导入的技能会被保存在 `~/.hermes/skills/openclaw-imports/` 目录中。需启动新会话才能让这些技能生效，或者运行 `/skills` 命令查看它们是否已加载。

### TTS 语音未迁移

OpenClaw 将 TTS 设置存储在两个位置：`messages.tts.providers.*` 目录以及顶层的 `talk` 配置文件中。迁移过程会同时检查这两个位置。如果您的语音 ID 是通过 OpenClaw 用户界面设置的（且存储在其他路径），可能需要手动设置：`hermes config set tts.elevenlabs.voice_id YOUR_VOICE_ID`。
