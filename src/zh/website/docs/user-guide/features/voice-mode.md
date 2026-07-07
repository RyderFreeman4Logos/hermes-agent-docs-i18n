---
sidebar_position: 10
title: "Voice Mode"
description: "Real-time voice conversations with Hermes Agent — CLI, Telegram, Discord (DMs, text channels, and voice channels)"
---

# 语音模式

Hermes Agent 支持在命令行界面和消息平台之间实现完整的语音交互。您可以通过麦克风与智能体对话，听到其语音回复，并在 Discord 的语音频道中进行实时语音交流。

如需包含推荐配置及实际使用场景的详细设置指南，请参阅 [如何在使用 Hermes 时启用语音模式](/guides/use-voice-mode-with-hermes)。

## 先决条件

在使用语音功能之前，请确保满足以下条件：

1. **已安装 Hermes Agent** —— 可通过安装脚本完成（详见 [安装指南](/getting-started/installation)）
2. **已配置 LLM 服务提供商** —— 运行 `hermes model` 命令，或是在 `~/.hermes/.env` 文件中设置您选择的提供商凭据
3. **基础环境已正常运行** —— 先运行 `hermes` 命令确认智能体能响应文本指令，然后再启用语音功能

:::提示
首次运行 `hermes` 时，系统会自动创建 `~/.hermes/` 目录及默认的 `config.yaml` 文件。您只需手动创建 `~/.hermes/.env` 文件来存储 API 密钥即可。
:::

:::提示 Nous Portal 可同时满足两项需求
通过付费订阅 [Nous Portal](/user-guide/features/tool-gateway)，您不仅可以获得 LLM 服务（即第 2 步），还能通过工具网关使用 OpenAI TTS 功能——无需单独配置 OpenAI 密钥。在全新安装环境中，执行 `hermes setup --portal` 即可同时完成两项配置。
:::

## 功能概览

| 功能 | 支持平台 | 描述 |
|---------|----------|-------------|
| **交互式语音** | 命令行界面 | 按下 Ctrl+B 开始录音，智能体会自动检测静音并作出回应 |
| **自动语音回复** | Telegram、Discord | 智能体在提供文本回复的同时，还会发送语音音频 |
| **语音频道功能** | Discord | 机器人会加入语音频道，聆听用户发言，并以语音形式回复 |

## 所需条件

### Python 包

```bash
# CLI voice mode (microphone + audio playback)
cd ~/.hermes/hermes-agent && uv pip install -e ".[voice]"

# Discord + Telegram messaging (includes discord.py[voice] for VC support)
cd ~/.hermes/hermes-agent && uv pip install -e ".[messaging]"

# Premium TTS (ElevenLabs)
cd ~/.hermes/hermes-agent && uv pip install -e ".[tts-premium]"

# Local TTS (NeuTTS, optional)
python -m pip install -U neutts[all]

# Everything at once
cd ~/.hermes/hermes-agent && uv pip install -e ".[all]"
```

| 额外功能 | 所需包 | 适用场景 |
|-------|----------|---------|
| `voice` | `sounddevice`, `numpy` | CLI语音模式 |
| `messaging` | `discord.py[voice]`, `python-telegram-bot`, `aiohttp` | Discord及Telegram机器人 |
| `tts-premium` | `elevenlabs` | ElevenLabs文本转语音服务 |

可选的本地文本转语音服务：可通过`python -m pip install -U neutts[all]`单独安装`neutts`。首次使用时它会自动下载模型。

:::info
`discord.py[voice]`会自动安装**PyNaCl**（用于语音加密）以及**opus绑定库**，这是支持Discord语音频道所必需的。
:::

### 系统依赖项

```bash
# macOS
brew install portaudio ffmpeg opus
brew install espeak-ng   # for NeuTTS

# Ubuntu/Debian
sudo apt install portaudio19-dev ffmpeg libopus0
sudo apt install espeak-ng   # for NeuTTS
```

| 依赖项 | 用途 | 所需功能 |
|---------|------|----------|
| **PortAudio** | 麦克风输入与音频播放 | CLI语音模式 |
| **ffmpeg** | 音频格式转换（MP3 → Opus，PCM → WAV） | 所有平台 |
| **Opus** | Discord语音编码格式 | Discord语音频道 |
| **espeak-ng** | 音素合成后端 | 本地NeuTTS提供程序 |

### API密钥

请将其添加至`~/.hermes/.env`文件中：

```bash
# Speech-to-Text — local provider needs NO key at all
# pip install faster-whisper          # Free, runs locally, recommended
GROQ_API_KEY=your-key                 # Groq Whisper — fast, free tier (cloud)
VOICE_TOOLS_OPENAI_KEY=your-key       # OpenAI Whisper — paid (cloud)

# Text-to-Speech (optional — Edge TTS and NeuTTS work without any key)
ELEVENLABS_API_KEY=***           # ElevenLabs — premium quality
# VOICE_TOOLS_OPENAI_KEY above also enables OpenAI TTS
```

:::提示
如果已安装 `faster-whisper`，则语音模式在文本转语音功能上**无需任何 API 密钥**即可使用。模型文件（`base` 版本约 150 MB）会在首次使用时自动下载。
:::

---

## CLI 语音模式

**经典 CLI**（`hermes chat`）和 **TUI**（`hermes --tui`）均支持语音模式。两者的功能完全一致——命令格式相同、语音活动检测与静音识别机制相同、文本转语音为流式输出、幻觉过滤功能也相同。此外，TUI 还会将崩溃分析日志发送到 `~/.hermes/logs/`，这样在遇到某些特殊音频后端导致的即时通话故障时，就能通过完整的堆栈跟踪信息进行报告，而不会悄无声息地消失。

### 快速入门

启动 CLI 并开启语音模式：

```bash
hermes                # Start the interactive CLI
```

接着在 CLI 中使用以下命令：

```
/voice          Toggle voice mode on/off
/voice on       Enable voice mode
/voice off      Disable voice mode
/voice tts      Toggle TTS output
/voice status   Show current state
```

### 工作原理

1. 使用 `hermes` 启动 CLI，然后通过 `/voice on` 开启语音模式  
2. **按下 Ctrl+B** —— 会响起一声提示音（880Hz），录音随即开始  
3. **开始说话** —— 实时音频音量条会显示您的输入内容：`● [▁▂▃▅▇▇▅▂] ❯`  
4. **停止说话** —— 在3秒的静默后，录音会自动停止  
5. 会响起两声提示音（660Hz），表示录音已结束  
6. 音频通过 Whisper 进行转录后发送给智能体  
7. 如果启用了文本转语音功能，智能体的回复将会以语音形式输出  
8. 录音会**自动重新开始** —— 无需按下任何键即可再次开口说话  

此循环会持续进行，直到您在录音过程中按下 **Ctrl+B**（从而退出连续录音模式），或连续3次录音均未检测到语音输入。

:::提示
录音按键可通过 `~/.hermes/config.yaml` 文件中的 `voice.record_key` 参数进行配置（默认值为 `ctrl+b`）。
:::

### 静默检测

系统采用两阶段算法来判断您是否已完成说话：

1. **语音确认** —— 等待音频的均方根值超过阈值（200）且持续时间至少为0.3秒，可容忍音节间的短暂下降  
2. **结束检测** —— 在确认存在语音输入后，若随后出现3.0秒的持续静默，则触发停止录音  

如果15秒内完全未检测到任何语音，录音会自动停止。  
`silence_threshold` 和 `silence_duration` 这两个参数均可在 `config.yaml` 中进行配置。您还可以通过设置 `voice.beep_enabled: false` 来禁用录音开始/结束时的提示音。

### 流式文本转语音

当启用文本转语音功能时，智能体会在生成文本的同时**逐句**输出回复 —— 您无需等待完整的回复内容：

1. 将文本的增量部分缓存起来，直至形成完整的句子（最少20个字符）  
2. 移除其中的 Markdown 格式及 `<think>` 代码块  
3. 实时为每一句话生成并播放对应的音频

### 幻觉内容过滤

Whisper 有时会从静默或背景噪音中生成虚假文本（如“感谢观看”、“订阅”等）。智能体通过包含多种语言的26组已知幻觉短语，以及用于识别重复变体的正则表达式，来过滤这些错误内容。

---

## 网关语音回复（Telegram与Discord）

如果您尚未设置消息机器人，请参阅对应平台的指南：  
- [Telegram 设置指南](../messaging/telegram.md)  
- [Discord 设置指南](../messaging/discord.md)  

请启动网关以连接到您的消息平台：

```bash
hermes gateway        # Start the gateway (connects to configured platforms)
hermes gateway setup  # Interactive setup wizard for first-time configuration
```

### Discord：频道与私信

该机器人可在 Discord 上支持两种交互模式：

| 模式 | 交流方式 | 是否需要@提及 | 设置要求 |
|------|----------|--------------|---------|
| **私信（DM）** | 打开机器人的个人资料 → 点击“发送消息” | 不需要 | 立即可用 |
| **服务器频道** | 在机器人所在的文本频道中输入内容 | 需要（使用 `@botname`） | 须先将机器人邀请至该服务器 |

**私信（推荐用于个人使用）：** 直接与机器人开启私信对话并输入内容即可，无需@提及。语音回复及所有命令的功能与在频道中相同。

**服务器频道：** 机器人仅会在您@提及它时才会响应（例如 `@hermesbyt4 hello`）。请务必从提及弹窗中选择**机器人用户**，而非名称相同的角色。

:::提示
若想取消服务器频道中的@提及要求，可在 `~/.hermes/.env` 文件中添加相应配置：
```bash
DISCORD_REQUIRE_MENTION=false
```
或者将特定频道设置为自由回复模式（无需额外标注）：
```bash
DISCORD_FREE_RESPONSE_CHANNELS=123456789,987654321
```
:::

### 命令

这些命令在 Telegram 和 Discord（私信及文本频道）中均可使用：

```
/voice          Toggle voice mode on/off
/voice on       Voice replies only when you send a voice message
/voice tts      Voice replies for ALL messages
/voice off      Disable voice replies
/voice status   Show current setting
```

### 模式

| 模式 | 命令 | 行为表现 |
|------|---------|----------|
| `off` | `/voice off` | 仅文本模式（默认） |
| `voice_only` | `/voice on` | 仅在你发送语音消息时才会回复语音 |
| `all` | `/voice tts` | 对所有消息均以语音形式回复 |

语音模式设置会在网关重启后依然保持不变。

### 平台传输方式

| 平台 | 格式 | 备注 |
|------|---------|-------|
| **Telegram** | 语音气泡（Opus/OGG格式） | 在聊天界面内直接播放。如需转换，ffmpeg会自动将MP3转换为Opus格式 |
| **Discord** | 原生语音气泡（Opus/OGG格式） | 以类似用户发送的语音消息的方式在聊天界面内播放。若语音气泡API出现故障，则会回退为文件附件形式 |

---

## Discord语音频道

这是最沉浸式的语音功能：机器人可加入Discord语音频道，监听用户讲话内容，将其转录为文本，通过智能体进行处理，最终以语音形式在频道中回复。

### 设置步骤

#### 1. Discord机器人权限

如果你已经为文本通信配置好了Discord机器人（详见[Discord设置指南](../messaging/discord.md)），则需要为其添加语音相关权限。

请前往[Discord开发者门户](https://discord.com/developers/applications)，选择你的应用，进入**Installation** → **Default Install Settings** → **Guild Install**页面：

**在现有的文本通信权限基础上，添加以下权限：**

| 权限 | 用途 | 是否必需 |
|------|------|----------|
| **Connect** | 加入语音频道 | 是 |
| **Speak** | 在语音频道中播放TTS音频 | 是 |
| **Use Voice Activity** | 检测用户是否正在讲话 | 建议启用 |

**更新后的权限整数值：**

| 等级 | 整数值 | 包含的权限 |
|-------|--------|------------|
| 仅文本模式 | `309237763136` | 查看频道、发送消息、读取历史记录、嵌入内容、附件、主题帖、反应功能、创建公开主题帖 |
| 文本+语音模式 | `309240908864` | 上述所有权限 + Connect、Speak权限 |

使用更新后的权限URL**重新邀请机器人**即可：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=309240908864
```

请将 `YOUR_APP_ID` 替换为来自开发者门户中的您的应用 ID。

:::warning
若将机器人重新邀请至其已所在的服务器，只需更新其权限而无需将其移除。这样您不会丢失任何数据或配置。
:::

#### 2. 特权网关意图

在 [开发者门户](https://discord.com/developers/applications) → 您的应用 → **机器人** → **特权网关意图** 中，需启用以下三项：

| 意图 | 用途 |
|--------|---------|
| **在线状态意图** | 探测用户的在线/离线状态 |
| **服务器成员意图** | 将 `DISCORD_ALLOWED_USERS` 列表中的用户名转换为数字 ID（条件性） |
| **消息内容意图** | 读取频道中的文本消息内容 |

**消息内容意图**是必需的。只有当您的 `DISCORD_ALLOWED_USERS` 列表使用的是用户名时，才需要**服务器成员意图**——如果您使用的是数字用户 ID，则可以不启用该选项。语音频道的 SSRC → user_id 映射关系源自 Discord 语音 WebSocket 中的 SPEAKING 操作码，因此无需**服务器成员意图**。

#### 3. Opus 编解码器

运行网关的机器上必须安装 Opus 编解码器库：

```bash
# macOS (Homebrew)
brew install opus

# Ubuntu/Debian
sudo apt install libopus0
```

该机器人会自动从以下路径加载编解码器：
- **macOS：** `/opt/homebrew/lib/libopus.dylib`
- **Linux：** `libopus.so.0`

#### 4. 环境变量

```bash
# ~/.hermes/.env

# Discord bot (already configured for text)
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-user-id

# STT — local provider needs no key (pip install faster-whisper)
# GROQ_API_KEY=your-key            # Alternative: cloud-based, fast, free tier

# TTS — optional. Edge TTS and NeuTTS need no key.
# ELEVENLABS_API_KEY=***      # Premium quality
# VOICE_TOOLS_OPENAI_KEY=***  # OpenAI TTS / Whisper
```

### 启动网关

```bash
hermes gateway        # Start with existing configuration
```

该机器人应在几秒内出现在 Discord 中。

### 命令

在含有该机器人的 Discord 文本频道中使用以下命令：

```
/voice join      Bot joins your current voice channel
/voice channel   Alias for /voice join
/voice leave     Bot disconnects from voice channel
/voice status    Show voice mode and connected channel
```

:::info
在运行 `/voice join` 命令之前，您必须处于语音频道中。该机器人将会加入与您相同的语音频道。
:::

### 工作原理

当机器人加入语音频道后，它会执行以下操作：

1. **独立监听**每位用户的音频流
2. **检测静音状态**——在至少0.5秒的讲话结束后，若出现1.5秒的静音，便会触发处理流程
3. 通过 Whisper STT（本地服务、Groq或OpenAI）对音频进行转录
4. 经过完整的机器人处理流程（会话管理、工具调用及内存处理）
5. 最后通过文本转语音技术将回复内容在语音频道中播报出来

### 文本频道集成

当机器人处于语音频道时：

- 转录内容会显示在文本频道中：`[语音] @用户：您所说的内容`
- 机器人的回复既会以文本形式发送到该频道，也会通过语音在频道内播报
- 文本频道即为发出 `/voice join` 命令的频道

### 防止回声现象

在播放文本转语音回复时，机器人会自动暂停音频监听，从而避免其听到并重新处理自身的输出内容。

### 访问控制

仅 `DISCORD_ALLOWED_USERS` 中列出的用户才能通过语音进行交互。其他用户的音频将被静默忽略。

```bash
# ~/.hermes/.env
DISCORD_ALLOWED_USERS=284102345871466496
```

## 配置参考

### config.yaml

```yaml
# Voice recording (CLI)
voice:
  record_key: "ctrl+b"            # Key to start/stop recording
  max_recording_seconds: 120       # Maximum recording length
  auto_tts: false                  # Auto-enable TTS when voice mode starts
  beep_enabled: true               # Play record start/stop beeps
  silence_threshold: 200           # RMS level (0-32767) below which counts as silence
  silence_duration: 3.0            # Seconds of silence before auto-stop

# Speech-to-Text
stt:
  enabled: true                     # set to false to skip auto-transcription —
                                    # the gateway still caches the audio file and
                                    # passes its path to the agent as part of the
                                    # inbound message, useful for custom pipelines
                                    # (diarization, alignment, archival, etc.)
  provider: "local"                  # "local" (free) | "groq" | "openai" | "mistral" | "xai"
  local:
    model: "base"                    # tiny, base, small, medium, large-v3
  # model: "whisper-1"              # Legacy: used when provider is not set

# Text-to-Speech
tts:
  provider: "edge"                 # "edge" (free) | "elevenlabs" | "openai" | "neutts" | "minimax" | "mistral" | "gemini" | "xai" | "kittentts" | "piper"
  edge:
    voice: "en-US-AriaNeural"      # 322 voices, 74 languages
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"    # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"                 # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # optional: override for self-hosted or OpenAI-compatible endpoints
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
```

### 环境变量

```bash
# Speech-to-Text providers (local needs no key)
# pip install faster-whisper        # Free local STT — no API key needed
GROQ_API_KEY=...                    # Groq Whisper (fast, free tier)
VOICE_TOOLS_OPENAI_KEY=...         # OpenAI Whisper (paid)

# STT advanced overrides (optional)
STT_GROQ_MODEL=whisper-large-v3-turbo    # Override default Groq STT model
STT_OPENAI_MODEL=whisper-1               # Override default OpenAI STT model
GROQ_BASE_URL=https://api.groq.com/openai/v1     # Custom Groq endpoint
STT_OPENAI_BASE_URL=https://api.openai.com/v1    # Custom OpenAI STT endpoint

# Text-to-Speech providers (Edge TTS and NeuTTS need no key)
ELEVENLABS_API_KEY=***             # ElevenLabs (premium quality)
# VOICE_TOOLS_OPENAI_KEY above also enables OpenAI TTS

# Discord voice channel
DISCORD_BOT_TOKEN=...
DISCORD_ALLOWED_USERS=...
```

### STT 提供商对比

| 提供商 | 模型 | 速度 | 质量 | 成本 | API 密钥 |
|----------|-------|------|---------|------|---------|
| **本地** | `base` | 快（取决于 CPU/GPU） | 良好 | 免费 | 无 |
| **本地** | `small` | 中等 | 更优 | 免费 | 无 |
| **本地** | `large-v3` | 慢 | 最佳 | 免费 | 无 |
| **Groq** | `whisper-large-v3-turbo` | 非常快（约 0.5 秒） | 良好 | 免费套餐 | 有 |
| **Groq** | `whisper-large-v3` | 快（约 1 秒） | 更优 | 免费套餐 | 有 |
| **OpenAI** | `whisper-1` | 快（约 1 秒） | 良好 | 需付费 | 有 |
| **OpenAI** | `gpt-4o-transcribe` | 中等（约 2 秒） | 最佳 | 需付费 | 有 |
| **Mistral** | `voxtral-mini-latest` | 快 | 良好 | 需付费 | 有 |
| **xAI** | `grok-stt` | 快 | 良好 | 需付费 | 有 |

提供商优先级（自动回退顺序）：**本地** > **Groq** > **OpenAI**

### TTS 提供商对比

| 提供商 | 质量 | 成本 | 延迟 | 是否需要密钥 |
|----------|---------|------|-------|--------------|
| **Edge TTS** | 良好 | 免费 | 约 1 秒 | 否 |
| **ElevenLabs** | 极佳 | 需付费 | 约 2 秒 | 是 |
| **OpenAI TTS** | 良好 | 需付费 | 约 1.5 秒 | 是 |
| **NeuTTS** | 良好 | 免费 | 取决于 CPU/GPU | 否 |

NeuTTS 使用上述的 `tts.neutts` 配置块。

---

## 故障排除

### “未找到音频设备”（CLI 模式）

原因是未安装 PortAudio：

```bash
brew install portaudio    # macOS
sudo apt install portaudio19-dev  # Ubuntu
```

如果您在 Linux 桌面环境中通过 Docker 运行 Hermes，容器还需要访问主机的音频套接字。如需设置与 PulseAudio/PipeWire 兼容的音频桥接方案，请参阅 [Docker 音频桥接](/user-guide/docker#optional-linux-desktop-audio-bridge) 的相关说明。

### 机器人在 Discord 服务器频道中无响应

默认情况下，机器人在服务器频道中需要通过 @提及才能被唤醒。请确保您：

1. 输入 `@` 后选择**机器人用户**（带有 #discriminator 标识），而非名称相同的**角色**；
2. 或直接通过私信发送消息——无需进行提及操作；
3. 或在 `~/.hermes/.env` 文件中将 `DISCORD_REQUIRE_MENTION` 设置为 `false`。

### 机器人已加入视频通话，但无法听到我的声音

- 确认您的 Discord 用户 ID 已添加到 `DISCORD_ALLOWED_USERS` 列表中；
- 检查您在 Discord 中未被静音；
- 机器人需要先收到 Discord 发送的 SPEAKING 事件，才能处理您的音频——请在加入通话后几秒内开始说话。

### 机器人能听到我的声音，但无响应

- 确认文本转语音功能正常可用：可安装 `faster-whisper`（无需密钥），或设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`；
- 检查大语言模型是否已正确配置且可访问；
- 查看网关日志：`tail -f ~/.hermes/logs/gateway.log`。

### 机器人会在文本频道中回应，但在语音频道中不回应

- 可能是文本转语音服务出现故障——请检查 API 密钥及使用额度；
- 默认情况下会回退到免费的 Edge TTS 服务（无需密钥）；
- 查看日志以确认是否存在文本转语音相关的错误。

### Whisper 生成的文本内容错误

幻觉过滤机制通常能自动处理大多数异常情况。如果仍出现错误的转录结果：

- 尝试在更安静的环境中使用；
- 调整配置文件中的 `silence_threshold` 值（数值越高，过滤越不敏感）；
- 尝试使用其他文本转语音模型。
