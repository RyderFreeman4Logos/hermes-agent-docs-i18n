---
sidebar_position: 10
title: "Migrate from OpenClaw"
description: "Complete guide to migrating your OpenClaw / Clawdbot setup to Hermes Agent — what gets migrated, how config maps, and what to check after."
---

# 从 OpenClaw 迁移

`hermes claw migrate` 命令可将您现有的 OpenClaw（或旧版的 Clawdbot/Moldbot）配置导入 Hermes。本指南将详细说明哪些内容会被迁移、配置键的对应关系，以及迁移完成后需要验证的事项。

:::note
如果您是从 **Claude Code** 或 **OpenAI Codex CLI** 过渡而来？请使用 [`hermes import-agent`](../user-guide/import-from-other-agents.md) 命令。
:::

:::tip
如果您的 OpenClaw 配置使用了多个提供商，可使用 `hermes setup --portal` 将其整合为单一的 OAuth 认证——只需一次登录即可使用 300 多种模型以及工具网关。详情请参阅 [Nous Portal](/integrations/nous-portal)。
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

在执行任何更改之前，该迁移工具总会先完整预览即将导入的内容。请仔细查看列表，确认无误后再继续操作。

默认从 `~/.openclaw/` 目录读取数据。系统会自动识别旧的 `~/.clawdbot/` 或 `~/.moltbot/` 目录，旧的配置文件名（如 `clawdbot.json`、`moltbot.json`）也是如此。

## 选项

| 选项 | 描述 |
|------|------|
| `--dry-run` | 仅预览——显示迁移内容后停止。 |
| `--preset <name>` | `full`（所有兼容设置）或 `user-data`（排除基础设施相关配置）。默认情况下，这两种预设都不会导入机密信息——需明确使用 `--migrate-secrets` 选项。 |
| `--overwrite` | 在出现冲突时覆盖现有的 Hermes 文件（默认：若计划存在冲突则拒绝应用）。 |
| `--migrate-secrets` | 包含 API 密钥。即使使用 `--preset full` 选项也必须此选项——没有任何预设会悄悄导入机密信息。 |
| `--no-backup` | 跳过对 `~/.hermes/` 的迁移前压缩包快照创建步骤（默认情况下，在应用更改前会在 `~/.hermes/backups/pre-migration-*.zip` 下生成一个恢复点存档，可通过 `hermes import` 命令恢复）。 |
| `--source <path>` | 自定义 OpenClaw 目录路径。 |
| `--workspace-target <path>` | 指定 `AGENTS.md` 文件的保存位置。 |
| `--skill-conflict <mode>` | `skip`（默认）、`overwrite` 或 `rename`。 |
| `--yes` | 跳过预览后的确认提示。 |

## 将被迁移的内容

### 人物设定、记忆内容及指令信息

| 类型 | OpenClaw 源文件路径 | Hermes 目标路径 | 备注 |
|------|----------------|-------------------|-------|
| 人物设定 | `workspace/SOUL.md` | `~/.hermes/SOUL.md` | 直接复制 |
| 工作空间说明 | `workspace/AGENTS.md` | 使用 `--workspace-target` 指定的 `AGENTS.md` 路径 | 需要使用 `--workspace-target` 参数 |
| 长期记忆 | `workspace/MEMORY.md` | `~/.hermes/memories/MEMORY.md` | 该文件会被解析为多个条目，与现有条目合并并去重，使用 `§` 作为分隔符 |
| 用户资料 | `workspace/USER.md` | `~/.hermes/memories/USER.md` | 合并逻辑与长期记忆相同 |
| 日志记忆文件 | `workspace/memory/*.md` | `~/.hermes/memories/MEMORY.md` | 所有的日志文件都会被合并到主记忆文件中 |

作为备用路径，还会检查 `workspace.default/` 和 `workspace-main/` 中的文件（在最新版本中，OpenClaw 将 `workspace/` 更名为 `workspace-main/`，而在多智能体环境中则使用 `workspace-{agentId}` 作为路径）。

### 技能（4个来源）

| 来源 | OpenClaw 文件位置 | Hermes 目标路径 |
|--------|------------------|-------------------|
| 工作空间技能 | `workspace/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 托管/共享技能 | `~/.openclaw/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 个人跨项目技能 | `~/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |
| 项目级共享技能 | `workspace/.agents/skills/` | `~/.hermes/skills/openclaw-imports/` |
技能冲突可通过 `--skill-conflict` 参数处理：`skip` 选项会保留现有的 Hermes 技能，`overwrite` 选项则会替换它，而 `rename` 选项则会创建一个带有 `-imported` 后缀的副本。

### 模型与提供者配置

| 配置项 | OpenClaw 配置路径 | Hermes 目标位置 | 备注 |
|------|---------------------|-------------------|-------|
| 默认模型 | `agents.defaults.model` | `config.yaml` → `model` | 可以是字符串形式，也可以是 `{primary, fallbacks}` 对象形式 |
| 自定义提供者 | `models.providers.*` | `config.yaml` → `custom_providers`（在下次执行 `hermes update` 配置迁移时，会自动转换为标准的 `providers:` 字典格式） | 该参数用于指定 `baseUrl`、`apiType`/`api` —— 支持简写形式（如“openai”、“anthropic”）以及带连字符的形式（如“openai-completions”、“anthropic-messages”、“google-generative-ai”） |
| 提供者 API 密钥 | `models.providers.*.apiKey` | `~/.hermes/.env` | 需要使用 `--migrate-secrets` 参数。详情请参见下文的[API 密钥解析](#api-key-resolution)部分。 |

### Agent 行为表现

| 项目 | OpenClaw 配置路径 | Hermes 配置路径 | 映射规则 |
|------|---------------------|-------------------|---------|
| 最大轮次数 | `agents.defaults.timeoutSeconds` | `agent.max_turns` | `timeoutSeconds / 10`，上限为 200 |
| 详细模式 | `agents.defaults.verboseDefault` | `agent.verbose` | “off” / “on” / “full” |
| 推理强度 | `agents.defaults.thinkingDefault` | `agent.reasoning_effort` | “always”/“high”/“xhigh” → “high”；“auto”/“medium”/“adaptive” → “medium”；“off”/“low”/“none”/“minimal” → “low” |
| 压缩功能 | `agents.defaults.compaction.mode` | `compression.enabled` | “off” → false，其他值均为 true |
| 压缩模型 | `agents.defaults.compaction.model` | `compression.summary_model` | 直接字符串复制 |
| 人类延迟 | `agents.defaults.humanDelay.mode` | `human_delay.mode` | “natural” / “custom” / “off” |
| 人类延迟时长 | `agents.defaults.humanDelay.minMs` / `.maxMs` | `human_delay.min_ms` / `.max_ms` | 直接复制 |
| 时区设置 | `agents.defaults.userTimezone` | `timezone` | 直接字符串复制 |
| 命令执行超时时间 | `tools.exec.timeoutSec` | `terminal.timeout` | 直接复制（字段名为 `timeoutSec`，而非 `timeout`） |
| Docker 沙箱环境 | `agents.defaults.sandbox.backend` | `terminal.backend` | “docker” → “docker” |
| Docker 镜像 | `agents.defaults.sandbox.docker.image` | `terminal.docker_image` | 直接复制 |

### 会话生命周期

空闲计时器和每日重置计时器不会被导入：Hermes 对话会一直保留，直到用户明确发出 `/new` 或 `/reset` 命令。而高级会话设置（如身份关联、线程绑定、维护选项、作用域及发送策略）则会被存档以供后续参考。

### MCP 服务器

| OpenClaw 字段 | Hermes 字段 | 备注 |
|----------------|-------------|-------|
| `mcp.servers.*.command` | `mcp_servers.*.command` | 标准输入输出传输方式 |
| `mcp.servers.*.args` | `mcp_servers.*.args` |  |
| `mcp.servers.*.env` | `mcp_servers.*.env` |  |
| `mcp.servers.*.cwd` | `mcp_servers.*.cwd` |  |
| `mcp.servers.*.url` | `mcp_servers.*.url` | HTTP/SSE 传输方式 |
| `mcp.servers.*.tools.include` | `mcp_servers.*.tools.include` | 工具筛选功能 |
| `mcp.servers.*.tools.exclude` | `mcp_servers.*.tools.exclude` |  |

### 文本转语音（TTS）

TTS 设置会从 **两个** OpenClaw 配置位置读取，其优先级如下：

1. `messages.tts.providers.{provider}.*`（标准配置位置）
2. 顶层配置的 `talk.providers.{provider}.*`（备用位置）
3. 旧版的扁平键格式 `messages.tts.{provider}.*`（最旧格式）

| 项目 | Hermes 目标路径 |
|------|-------------------|
| 提供商名称 | `config.yaml` → `tts.provider` |
| ElevenLabs 语音 ID | `config.yaml` → `tts.elevenlabs.voice_id` |
| ElevenLabs 模型 ID | `config.yaml` → `tts.elevenlabs.model_id` |
| OpenAI 模型 | `config.yaml` → `tts.openai.model` |
| OpenAI 语音 | `config.yaml` → `tts.openai.voice` |
| Edge TTS 语音 | `config.yaml` → `tts.edge.voice`（OpenClaw 将 “edge” 更名为 “microsoft”——两种名称均可被识别） |
| TTS 资源文件 | `~/.hermes/tts/`（通过复制文件方式提供） |

### 消息传递平台

| Platform | OpenClaw config path | Hermes `.env` variable | Notes |
|----------|---------------------|----------------------|-------|
| Telegram | `channels.telegram.botToken` or `.accounts.default.botToken` | `TELEGRAM_BOT_TOKEN` | Token can be string or [SecretRef](#secretref-handling). Both flat and accounts layout supported. |
| Telegram | `credentials/telegram-default-allowFrom.json` | `TELEGRAM_ALLOWED_USERS` | Comma-joined from `allowFrom[]` array |
| Discord | `channels.discord.token` or `.accounts.default.token` | `DISCORD_BOT_TOKEN` | |
| Discord | `channels.discord.allowFrom` or `.accounts.default.allowFrom` | `DISCORD_ALLOWED_USERS` | |
| Slack | `channels.slack.botToken` or `.accounts.default.botToken` | `SLACK_BOT_TOKEN` | |
| Slack | `channels.slack.appToken` or `.accounts.default.appToken` | `SLACK_APP_TOKEN` | |
| Slack | `channels.slack.allowFrom` or `.accounts.default.allowFrom` | `SLACK_ALLOWED_USERS` | |
| WhatsApp | `channels.whatsapp.allowFrom` or `.accounts.default.allowFrom` | `WHATSAPP_ALLOWED_USERS` | Auth via Baileys QR pairing — requires re-pairing after migration |
| Signal | `channels.signal.account` or `.accounts.default.account` | `SIGNAL_ACCOUNT` | |
| Signal | `channels.signal.httpUrl` or `.accounts.default.httpUrl` | `SIGNAL_HTTP_URL` | |
| Signal | `channels.signal.allowFrom` or `.accounts.default.allowFrom` | `SIGNAL_ALLOWED_USERS` | |
| Matrix | `channels.matrix.accessToken` or `.accounts.default.accessToken` | `MATRIX_ACCESS_TOKEN` | Uses `accessToken` (not `botToken`) |
| Mattermost | `channels.mattermost.botToken` or `.accounts.default.botToken` | `MATTERMOST_BOT_TOKEN` | |

### 其他配置项

| 配置项 | OpenClaw 路径 | Hermes 路径 | 备注 |
|------|-------------|-------------|-------|
| 审批模式 | `approvals.exec.mode` | `config.yaml` → `approvals.mode` | 取值范围：“auto”→“off”，“always”→“manual”，“smart”→“smart” |
| 命令白名单 | `exec-approvals.json` | `config.yaml` → `command_allowlist` | 各模式规则会进行合并与去重处理 |
| 浏览器 CDP 地址 | `browser.cdpUrl` | `config.yaml` → `browser.cdp_url` |  |
| 浏览器无头模式 | `browser.headless` | `config.yaml` → `browser.headless` |  |
| Brave 搜索密钥 | `tools.web.search.brave.apiKey` | `.env` → `BRAVE_API_KEY` | 需要使用 `--migrate-secrets` 参数 |
| 网关认证令牌 | `gateway.auth.token` | `.env` → `HERMES_GATEWAY_TOKEN` | 需要使用 `--migrate-secrets` 参数 |
| 工作目录 | `agents.defaults.workspace` | `config.yaml` → `terminal.cwd` | 为兼容旧版本，某些迁移任务仍可能输出 `MESSAGING_CWD` 作为备用值 |

### 归档配置（Hermes 中无直接对应项）

此类配置会被保存至 `~/.hermes/migration/openclaw/<时间戳>/archive/` 目录，以便人工查看：

| 类型 | 存档文件 | 在 Hermes 中的重建方式 |
|------|-----------|------------------------|
| `IDENTITY.md` | `archive/workspace/IDENTITY.md` | 合并到 `SOUL.md` 中 |
| `TOOLS.md` | `archive/workspace/TOOLS.md` | Hermes 已内置工具使用说明 |
| `HEARTBEAT.md` | `archive/workspace/HEARTBEAT.md` | 使用定时任务（cron job）处理周期性任务 |
| `BOOTSTRAP.md` | `archive/workspace/BOOTSTRAP.md` | 通过上下文文件或技能来实现 |
| 定时任务 | `archive/cron-config.json` | 使用 `hermes cron create` 命令重新创建 |
| 插件 | `archive/plugins-config.json` | 参见[插件指南](/user-guide/features/hooks) |
| Hook/Webhook | `archive/hooks-config.json` | 使用 `hermes webhook` 或网关 Hook |
| 内存后端 | `archive/memory-backend-config.json` | 通过 `hermes honcho` 进行配置 |
| 技能注册表 | `archive/skills-registry-config.json` | 使用 `hermes skills config` 命令 |
| 用户界面/身份配置 | `archive/ui-identity-config.json` | 使用 `/skin` 命令 |
| 日志记录 | `archive/logging-diagnostics-config.json` | 在 `config.yaml` 的日志配置部分进行设置 |
| 多智能体列表 | `archive/agents-list.json` | 通过 Hermes 配置文件来管理 |
| 渠道绑定 | `archive/bindings.json` | 需根据不同平台手动配置 |
| 复杂渠道 | `archive/channels-deep-config.json` | 需针对不同平台进行手动配置 |

## API 密钥解析

当启用 `--migrate-secrets` 参数时，API 密钥会按优先级从**四个来源**中收集：

1. **配置值** — `models.providers.*.apiKey` 以及 `openclaw.json` 中的 TTS 提供商密钥  
2. **环境文件** — `~/.openclaw/.env`（包含如 `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY` 等键值）  
3. **配置环境子对象** — `openclaw.json` → `"env"` 或 `"env"."vars"`（部分配置会将密钥存储于此，而非单独的 `.env` 文件中）  
4. **认证配置文件** — `~/.openclaw/agents/main/agent/auth-profiles.json`（用于存储每个智能体的凭证）  

配置值的优先级最高，后续的配置来源将填补剩余的空缺。  

### 支持的密钥类型  

`OPENROUTER_API_KEY`、`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`DEEPSEEK_API_KEY`、`GEMINI_API_KEY`、`ZAI_API_KEY`、`MINIMAX_API_KEY`、`ELEVENLABS_API_KEY`、`TELEGRAM_BOT_TOKEN`、`VOICE_TOOLS_OPENAI_KEY`  

不在此列表中的密钥将不会被复制。  

## SecretRef 处理方式  

OpenClaw 中用于存储令牌和 API 密钥的配置值可采用三种格式：

```json
// Plain string
"channels": { "telegram": { "botToken": "123456:ABC-DEF..." } }

// Environment template
"channels": { "telegram": { "botToken": "${TELEGRAM_BOT_TOKEN}" } }

// SecretRef object
"channels": { "telegram": { "botToken": { "source": "env", "id": "TELEGRAM_BOT_TOKEN" } } }
```

此次迁移可处理这三种格式的配置。对于源类型为 `env` 的环境模板和 SecretRef 对象，系统会从 `~/.openclaw/.env` 文件以及 `openclaw.json` 中的环境子对象中查找对应值。而源类型为 `file` 或 `exec` 的 SecretRef 对象则无法自动完成解析——系统会针对这类对象发出警告，相关值必须通过 `hermes config set` 命令手动添加到 Hermes 中。

## 迁移完成后

1. **查看迁移报告**——迁移完成后会生成该报告，其中列明了已迁移、跳过以及存在冲突的项的数量。

2. **检查归档文件**——位于 `~/.hermes/migration/openclaw/<timestamp>/archive/` 目录中的所有文件都需要人工处理。

3. **启动新会话**——已导入的技能和内存条目仅在新建的会话中生效，当前会话不受影响。

4. **验证 API 密钥**——运行 `hermes status` 命令以检查服务提供方的身份认证状态。

5. **测试消息功能**——如果已迁移平台令牌，需重启网关：`systemctl --user restart hermes-gateway`

6. **查看会话归档文件**——检查归档后的高级设置；出于设计考虑，空闲计时器和每日重置计时器不会被导入。

7. **重新配对 WhatsApp**——WhatsApp 使用二维码配对方式（Baileys 协议），而非令牌迁移机制。需运行 `hermes whatsapp` 命令进行配对。

8. **清理归档文件**——确认所有功能正常后，运行 `hermes claw cleanup` 命令将剩余的 OpenClaw 目录重命名为 `.pre-migration/`（以避免状态混淆）。

## 故障排除

### “未找到 OpenClaw 目录”

迁移过程会依次检查 `~/.openclaw/`、`~/.clawdbot/` 和 `~/.moltbot/` 这三个目录。如果您的安装路径不在这些位置，请使用 `--source /path/to/your/openclaw` 参数指定路径。

### “未找到提供者 API 密钥”

根据 OpenClaw 的版本不同，密钥可能存储在多个位置：`openclaw.json` 文件中 `models.providers.*.apiKey` 字段内、`~/.openclaw/.env` 文件中、`openclaw.json` 的 `"env"` 子对象中，或是 `agents/main/agent/auth-profiles.json` 文件中。迁移工具会逐一检查这四个位置。如果密钥使用了 `source: "file"` 或 `source: "exec"` 类型的 SecretRefs，系统将无法自动解析这些密钥——需要通过 `hermes config set` 命令手动添加。

### 迁移后技能未显示

导入的技能会存储在 `~/.hermes/skills/openclaw-imports/` 目录下。需要启动新会话才能让这些技能生效，或者运行 `/skills` 命令来确认它们已被加载。

### TTS 语音未同步迁移

OpenClaw 会将 TTS 相关设置存储在两个位置：`messages.tts.providers.*` 文件以及顶层的 `talk` 配置文件中。迁移过程会同时检查这两个位置。如果您的声音 ID 是通过 OpenClaw 用户界面设置的（且存储在其他路径），则可能需要手动设置：`hermes config set tts.elevenlabs.voice_id YOUR_VOICE_ID`。
