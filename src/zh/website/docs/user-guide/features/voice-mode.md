---
sidebar_position: 10
title: "Voice Mode"
description: "Real-time voice conversations with Hermes Agent — CLI, Telegram, Discord (DMs, text channels, and voice channels)"
---

# 语音模式

Hermes Agent 支持在命令行界面和消息平台之间实现完整的语音交互。您可以通过麦克风与智能体对话，听到其语音回复，并在 Discord 的语音频道中进行实时语音交流。

如需包含推荐配置及实际使用场景的详细设置指南，请参阅 [使用 Hermes 的语音模式](../../guides/use-voice-mode-with-hermes.md)。

关于免提会话启动方式——即通过说“hey hermes”（或任意指定短语）在命令行、文本用户界面或桌面应用中开启全新的语音会话，详情请参见 [唤醒词功能](/user-guide/features/wake-word)。

## 先决条件

在使用语音功能之前，请确保满足以下条件：

1. **已安装 Hermes Agent** —— 可通过安装脚本完成（详见 [安装指南](/getting-started/installation)）
2. **已配置 LLM 服务提供商** —— 运行 `hermes model` 命令，或是在 `~/.hermes/.env` 文件中设置您选择的提供商凭证
3. **基础环境已正常运行** —— 先运行 `hermes` 命令确认智能体能响应文本指令，然后再启用语音功能

:::提示
首次运行 `hermes` 时，系统会自动创建 `~/.hermes/` 目录及默认的 `config.yaml` 配置文件。您只需手动创建 `~/.hermes/.env` 文件来存储 API 密钥即可。
:::

:::提示 Nous Portal 可同时满足两项需求
通过付费订阅 [Nous Portal](/user-guide/features/tool-gateway)，即可同时获得 LLM 服务（对应步骤 2）以及通过工具网关提供的 OpenAI 文本转语音功能——无需单独配置 OpenAI 密钥。在全新安装时，执行 `hermes setup --portal` 即可一次性完成两项功能的连接。
:::

## 概述

| 功能特性 | 平台 | 描述 |
|---------|------|------|
| **交互式语音** | CLI | 按下 Ctrl+B 即可开始录音，智能体会自动检测静音并作出回应 |
| **自动语音回复** | Telegram、Discord | 智能体在发送文字回复的同时，还会附带语音音频 |
| **语音频道** | Discord | 机器人加入语音频道，聆听用户发言后以语音形式回复 |

## 需求条件

### Python 包 |

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

可选的本地文本转语音服务：可通过`python -m pip install -U neutts[all]`单独安装`neutts`。首次使用时它会自动下载对应模型。

:::info
`discord.py[voice]`会自动安装**PyNaCl**（用于语音加密）和**opus绑定库**，这是支持Discord语音频道所必需的。
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
|-----------|------|----------|
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

**经典 CLI**（`hermes chat`）和 **TUI**（`hermes --tui`）均支持语音模式。两者的功能完全一致——命令格式相同、语音活动检测机制相同、文本转语音为流式处理、幻觉过滤功能也相同。此外，TUI 还会将崩溃分析日志发送到 `~/.hermes/logs/`，这样在某些特殊音频后端出现即讲即听故障时，就能通过完整的堆栈跟踪信息进行报告，而不会悄无声息地消失。

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

1. 使用 `hermes` 启动 CLI，然后通过 `/voice on` 开启语音模式。
2. **按下 Ctrl+B** —— 会发出一声蜂鸣声（880Hz），录音随即开始。
3. **开始说话** —— 实时音频音量条会显示您的输入内容：`● [▁▂▃▅▇▇▅▂] ❯`。
4. **停止说话** —— 在3秒的静默后，录音会自动停止。
5. 会发出两声蜂鸣声（660Hz），表示录音已结束。
6. 音频内容会通过 Whisper 技术被转录并发送给智能体。
7. 如果启用了文本转语音功能，智能体的回复将会以语音形式输出。
8. 录音会**自动重新开始** —— 无需按下任何键即可再次开口说话。

此循环会持续进行，直到您在录音过程中按下 **Ctrl+B**（从而退出连续录音模式），或连续3次录音均未检测到语音输入。

:::提示
录音按键可通过 `~/.hermes/config.yaml` 文件中的 `voice.record_key` 参数进行自定义设置（默认值为 `ctrl+b`）。
:::

### 静默检测

系统采用两阶段算法来判断您是否已停止说话：

1. **语音确认** —— 等待音频的均方根值超过阈值（200）且持续时间至少为0.3秒，同时可容忍音节之间的短暂音量下降。
2. **结束检测** —— 在确认存在语音输入后，若随后出现3.0秒的持续静默，系统便会触发结束判定。

如果15秒内完全没有检测到语音，录音会自动停止。

`silence_threshold` 和 `silence_duration` 这两个参数均可在 `config.yaml` 中进行配置。您还可以通过设置 `voice.beep_enabled: false` 来关闭录音开始/结束时的蜂鸣声。

### 通过语音结束语音聊天

只需说出**“stop”**——仅此一个词——即可免提结束语音对话。该匹配规则设计得相当严格：整个输入内容（不区分大小写，忽略周围的标点符号）必须与预先配置的短语完全一致，因此像“别那样做，试试X吧”这样的表述仍会正常触发智能体响应。您可以通过`config.yaml`文件中的`voice.stop_phrases`参数来自定义短语列表（例如`["stop", "goodbye hermes"]`），若将其设置为`[]`则可禁用此功能。此外，当连续三轮未检测到语音输入时，语音对话也会自动结束。

在语音对话进行中直接输入简单的“stop”指令，在所有使用场景下（CLI、TUI、桌面端）均适用：该指令会直接结束语音对话，而不会被发送给智能体。而在非语音对话状态下，输入的“stop”则仅被视为普通消息。

### 流式文本转语音

启用文本转语音功能后，智能体会在逐句生成文本的同时同步输出回复——您无需等待完整的响应内容。该功能适用于**所有文本转语音服务提供商**：

1. 将文本增量逐步累积为完整的句子（最少20个字符）；
2. 移除其中的Markdown格式、表情符号以及`<think>`代码块；
3. 按照句子顺序实时播放音频——那些提供分块PCM接口的服务商（如ElevenLabs、OpenAI）可直接传输原始音频，从而实现最快速的语音输出；其他服务商（包括默认的Edge）则会在每句生成完成后再进行合成与播放。
相同的处理流程适用于经典 CLI、TUI 以及桌面应用。在桌面端的语音对话中，模型生成回复文本的同时，该文本会**实时**被发送到专为每个回复设计的语音 WebSocket 中，因此语音输出与文本生成是同步的——每个回复仅对应一个 WebSocket 连接和一个音频时钟，不存在按句间隔的连接延迟。

### 桌面远程模式：客户端直连语音（最短路径）

当 Hermes Desktop 连接到**远程网关**时，音频数据完全无需经过网关中转。在语音会话开始时，桌面应用会通过已认证的 REST 接口（`GET /api/audio/voice-config`）从网关获取当前活跃配置文件所对应的 STT/TTS 设置（包括服务提供商、模型、语言/音色以及认证凭证），随后直接调用相应的服务提供商：

- **听写/语音输入**：麦克风采集的音频会直接从桌面端传输到对应配置文件的 STT 服务提供商；只有转换后的*文本*才会作为提示信息发送给网关。
- **语音回复**：回复文本已通过聊天 WebSocket 实时流式传输至桌面端，随后桌面端会利用该配置文件对应的 TTS 服务提供商在本地合成语音并播放——整个过程中网关链路不会承载任何音频数据。

客户端无需进行任何配置：您所使用的配置文件即为所有服务提供商及密钥的权威来源，其效果就如同网关本身完成了所有处理工作一般。这些密钥仅存储在桌面端的会话内存中，绝不会被写入客户端硬盘。

那些仅能在网关主机上运行的提供程序（如本地 Whisper、`edge` TTS、命令型提供程序及插件），以及那些缺少相应端点的旧版后端，都会自动切换到中继路径（`/api/audio/transcribe` 和语音 WebSocket）进行运行。若希望强制所有提供程序都通过中继路径传输，可设置如下参数：

```yaml
voice:
  client_direct: false
```

**客户端直连支持**：可通过兼容 OpenAI 的接口、xAI Grok 语音转文字功能以及 ElevenLabs 语音转文字/文本生成服务，连接 OpenAI（包括由 Nous 管理的音频功能）、Groq、Mistral 和 DeepInfra。通过 OAuth 方式配置的 xAI 功能会始终在中继服务器上运行（OAuth 令牌的刷新操作在服务器端完成）。

### 中途插话

您可以在智能体响应的**任意阶段**中断对话——从您停止说话的那一刻起，麦克风就会保持开启状态，直到回复完全播放完毕（即全双工通信模式）：

- **在智能体思考时插话**：在连续语音模式下，当大型语言模型正在生成内容（尚未输出任何音频）时开口说话，即可中断当前的响应流程，您的话语将作为下一条消息发送，效果与在智能体正在输入时手动输入文字类似。
- **盖过其声音说话**：在智能体正在播放回复时开口说话，您的声音会立即中断播放，同时系统会接收您所说的话。语音检测器会根据对话开始时的“安静环境”来校准噪声阈值（而非以正在播放的音频为基准），因此背景音不会干扰检测，而正常的语音声量则能可靠地触发响应。
- **输入文字或按下录音键**：发送新消息或按下即时通话键，可立即停止所有设备上的音频播放。
- **说“停止”**：该停止指令在两个阶段均有效——在模型生成过程中可中断当前响应并结束语音聊天；在内容播放过程中则可切断语音流并终止对话。
**参数调优（config.yaml）**：将 `voice.barge_in` 设置为 `false` 即可禁用该功能；`voice.barge_in_threshold_multiplier`（默认值为 `3.0`）用于调整在安静环境基准值上的语音触发阈值；`voice.barge_in_grace_seconds`（默认值为 `0.5`）则可在内容开始播放后的一段时间内抑制误触发。若需实时调优，可将 `HERMES_VOICE_DEBUG=1` 设置为该值，以便将每块的 VAD 诊断信息（包括基准值、RMS 值以及触发判定结果）输出到标准错误流中。

智能体能够**感知**到自己被中断了：下一条消息会附带一条简短提示，告知模型其语音回复已被截断，这样模型就能做出自然反应（如表示“真没礼貌！”），或直接从中断处继续发言，而不会毫无察觉。

### 幻觉过滤机制

Whisper 有时会从静音或背景噪音中生成虚假文本（如“感谢观看”、“订阅”等）。智能体通过整合多语言中26种已知的幻觉短语，再加上用于识别重复变体的正则表达式模式，来过滤这些内容。

---

## 网关语音回复功能（Telegram与Discord）

如果您尚未设置消息机器人，请参阅对应平台的指南：
- [Telegram 设置指南](../messaging/telegram.md)
- [Discord 设置指南](../messaging/discord.md)

请启动网关以连接您的消息平台：

```bash
hermes gateway        # Start the gateway (connects to configured platforms)
hermes gateway setup  # Interactive setup wizard for first-time configuration
```

### Discord：频道与私信

该机器人可在 Discord 上支持两种交互模式：

| 模式 | 交流方式 | 是否需要@提及 | 设置要求 |
|------|----------|--------------|----------|
| **私信（DM）** | 打开机器人的个人资料 → 点击“发送消息” | 不需要 | 立即可用 |
| **服务器频道** | 在机器人所在的文本频道中输入内容 | 需要（使用 `@botname`） | 须先将机器人邀请至该服务器 |

**私信（推荐用于个人使用）：** 直接与机器人发起私信并输入内容即可，无需@提及。语音回复及所有命令的功能与在频道中相同。

**服务器频道：** 机器人仅会在你@提及它时才会响应（例如 `@hermesbyt4 hello`）。请务必从提及弹窗中选择**机器人用户**，而非名称相同的角色。

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

| 模式 | 命令 | 行为 |
|------|---------|------|
| `off` | `/voice off` | 仅文本模式（默认） |
| `voice_only` | `/voice on` | 仅在你发送语音消息时才会回复语音 |
| `all` | `/voice tts` | 对每条消息均以语音形式回复 |

语音模式设置会在网关重启后依然保持不变。

### 平台传输方式

| 平台 | 格式 | 备注 |
|------|---------|-------|
| **Telegram** | 语音气泡（Opus/OGG格式） | 在聊天界面中直接播放。如需转换，ffmpeg会自动将MP3转换为Opus格式 |
| **Discord** | 原生语音气泡（Opus/OGG格式） | 以类似用户发送的语音消息的方式在聊天界面中播放。若语音气泡API出现故障，则会回退为文件附件形式 |

---

## Discord语音频道

这是最沉浸式的语音功能：机器人可加入Discord语音频道，监听用户发言，将其语音转录后通过智能体处理，最终以语音形式在频道中回复。

### 设置步骤

#### 1. Discord机器人权限

如果你已经为文本消息功能配置了Discord机器人（详见[Discord设置指南](../messaging/discord.md)），则需要为其添加语音相关权限。

请前往[Discord开发者门户](https://discord.com/developers/applications)，选择你的应用，进入**Installation** → **Default Install Settings** → **Guild Install**页面：

**在现有的文本消息权限基础上，添加以下权限：**

| 权限 | 用途 | 是否必需 |
|------|------|----------|
| **Connect** | 进入语音频道 | 是 |
| **Speak** | 在语音频道中播放文本转语音音频 | 是 |
| **Use Voice Activity** | 检测用户是否正在说话 | 建议启用 |

**更新后的权限整数值：**

| 等级 | 整数值 | 包含的功能 |
|------|--------|------------|
| 仅文本 | `309237763136` | 查看频道、发送消息、读取历史记录、嵌入内容、上传附件、创建主题帖、发送反应、创建公开主题帖 |
| 文本+语音 | `309240908864` | 上述所有功能 + Connect、Speak权限 |

请使用包含更新后权限的链接**重新邀请该机器人**：

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=309240908864
```

请将 `YOUR_APP_ID` 替换为开发者门户中对应的应用程序 ID。

:::warning
若将机器人重新邀请至其已所在的服务器，只需更新其权限而无需将其移除。这样不会丢失任何数据或配置。
:::

#### 2. 特权网关意图

在 [开发者门户](https://discord.com/developers/applications) → 您的应用程序 → **机器人** → **特权网关意图** 中，需启用以下三项：

| 意图 | 用途 |
|--------|------|
| **在线状态意图** | 推测用户的在线/离线状态 |
| **服务器成员意图** | 将 `DISCORD_ALLOWED_USERS` 列表中的用户名转换为数字 ID（有条件） |
| **消息内容意图** | 读取频道中的文本消息内容 |

**消息内容意图**是必需的。只有当您的 `DISCORD_ALLOWED_USERS` 列表使用的是用户名时，才需要**服务器成员意图**——如果您使用的是数字用户 ID，则可以不启用该选项。语音频道的 SSRC 到 user_id 的映射关系来自 Discord 语音 WebSocket 中的 SPEAKING 操作码，因此无需**服务器成员意图**。

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

在包含该机器人的 Discord 文本频道中使用以下命令：

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
2. **检测静默状态**——在至少0.5秒的讲话结束后，若出现1.5秒的静默，便会触发处理流程
3. 通过 Whisper STT（本地服务、Groq或OpenAI）对音频进行转录
4. 经过完整的机器人处理流程（会话管理、工具调用及内存处理）
5. 最后通过文本转语音技术将回复内容在语音频道中播报出来

### 文本频道集成

当机器人处于语音频道时：

- 转录内容会显示在文本频道中：`[语音] @用户：您所说的内容`
- 机器人的回复既会以文本形式发送到该频道，也会通过语音在频道内播报
- 文本频道即为发出 `/voice join` 命令的频道

### 防止回声现象

在播放文本转语音回复时，机器人会自动暂停音频监听，从而避免听到并重新处理自己输出的音频内容。

### 访问控制

仅 `DISCORD_ALLOWED_USERS` 中列出的用户才能通过语音进行交互。其他用户的音频将被直接忽略。

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
  stop_phrases: ["stop"]           # Saying exactly one of these ends the voice chat; [] disables

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
    language: ""                     # optional ISO-639-1 hint; blank = use HERMES_LOCAL_STT_LANGUAGE if set, else auto-detect
  groq:
    language: ""                     # optional ISO-639-1 hint; blank = use HERMES_LOCAL_STT_LANGUAGE if set, else auto-detect
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
    # The `text_to_speech` tool accepts an optional per-call `instructions`
    # argument (tone, emotion, pacing, accent, whispering) that is forwarded
    # to `gpt-4o-mini-tts` and to OpenAI-compatible voice-design servers
    # (e.g. Qwen3-TTS-VoiceDesign via oMLX). See OpenAI's voice-design guide:
    # https://platform.openai.com/docs/guides/text-to-speech
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

### 文本转语音提供商对比

| 提供商 | 模型 | 速度 | 质量 | 成本 | API密钥 |
|--------|------|------|------|------|---------|
| **本地** | `base` | 快（取决于CPU/GPU性能） | 良好 | 免费 | 无 |
| **本地** | `small` | 中等 | 更佳 | 免费 | 无 |
| **本地** | `large-v3` | 慢 | 最优 | 免费 | 无 |
| **Groq** | `whisper-large-v3-turbo` | 非常快（约0.5秒） | 良好 | 免费套餐 | 有 |
| **Groq** | `whisper-large-v3` | 快（约1秒） | 更佳 | 免费套餐 | 有 |
| **OpenAI** | `whisper-1` | 快（约1秒） | 良好 | 需付费 | 有 |
| **OpenAI** | `gpt-4o-transcribe` | 中等（约2秒） | 最优 | 需付费 | 有 |
| **OpenAI** | `gpt-transcribe` | 快 | 最优 | 需付费（每分钟0.0045美元） | 有 |
| **Mistral** | `voxtral-mini-latest` | 快 | 良好 | 需付费 | 有 |
| **xAI** | `grok-stt` | 快 | 良好 | 需付费 | 有 |

提供商优先级（自动回退顺序）：**本地** > **Groq** > **OpenAI**

### 语音转文本提供商对比

| 提供商 | 质量 | 成本 | 延迟 | 是否需要密钥 |
|--------|------|------|------|--------------|
| **Edge TTS** | 良好 | 免费 | 约1秒 | 否 |
| **ElevenLabs** | 优秀 | 需付费 | 约2秒 | 是 |
| **OpenAI TTS** | 良好 | 需付费 | 约1.5秒 | 是 |
| **NeuTTS** | 良好 | 免费 | 取决于CPU/GPU性能 | 否 |

NeuTTS使用上述的`tts.neutts`配置项。

对于 `openai`，`text_to_speech` 工具支持一个可选的 `instructions` 参数，该参数可启用 `gpt-4o-mini-tts` 的语音设计功能（包括语调、情感、语速、口音以及低语效果）。同一个参数也可用于调用通过 `tts.openai.base_url` 指定的兼容 OpenAI 的语音设计服务器（例如通过 oMLX 提供的 Qwen3-TTS-VoiceDesign）。

---

## 故障排除

### “未找到音频设备”（CLI）

原因是未安装 PortAudio：

```bash
brew install portaudio    # macOS
sudo apt install portaudio19-dev  # Ubuntu
```

如果您在 Linux 桌面端通过 Docker 运行 Hermes，容器还需要能够访问宿主机的音频套接字。如需设置与 PulseAudio/PipeWire 兼容的音频连接方式，请参阅 [Docker 音频桥接](/user-guide/docker#optional-linux-desktop-audio-bridge) 的相关说明。

### 机器人在 Discord 服务器频道中无响应

默认情况下，机器人在服务器频道中需要通过 @提及才能被唤醒。请确保您：

1. 输入 `@` 并选择带有 **标识符** 的**机器人用户**，而非名称相同的**角色**
2. 或直接通过私信发送消息——无需提及机器人
3. 或在 `~/.hermes/.env` 文件中将 `DISCORD_REQUIRE_MENTION` 设置为 `false`

### 机器人已加入视频通话但听不到我的声音

- 确认您的 Discord 用户 ID 已添加到 `DISCORD_ALLOWED_USERS` 列表中
- 检查您在 Discord 中未被静音
- 机器人需要先收到 Discord 发送的 **SPEAKING** 事件，才能处理您的音频——请在加入通话后几秒内开始说话

### 机器人能听到我的声音但无响应

- 确认文本转语音功能正常：可安装 `faster-whisper`（无需密钥），或设置 `GROQ_API_KEY` / `VOICE_TOOLS_OPENAI_KEY`
- 检查大语言模型是否已正确配置且可访问
- 查看网关日志：`tail -f ~/.hermes/logs/gateway.log`

### 机器人在文本频道中有回应，但在语音频道中无回应

- 文本转语音服务可能出现故障——请检查 API 密钥及使用额度
- 默认情况下会回退到免费的 Edge TTS 服务（无需密钥）
- 查看日志以确认是否存在文本转语音相关的错误

### Whisper 返回乱码或错误文本

幻觉过滤机制通常能自动处理大多数异常情况。若仍出现错误转录结果：

- 选择更安静的环境进行使用  
- 调整配置文件中的 `silence_threshold` 参数（数值越高，灵敏度越低）  
- 尝试使用其他语音转文本模型
