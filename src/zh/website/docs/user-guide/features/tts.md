---
sidebar_position: 9
title: "Voice & TTS"
description: "Text-to-speech and voice message transcription across all platforms"
---

# 语音与文本转语音功能

Hermes Agent 支持在所有消息平台上实现文本转语音输出以及语音消息的转录功能。

:::提示 Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅资格，无需单独获取 OpenAI API 密钥，即可通过 **[Tool Gateway](tool-gateway.md)** 使用 OpenAI TTS 功能。新安装的用户可运行 `hermes setup --portal` 进行登录并一次性启用所有网关工具；已有安装的用户则可通过 `hermes model` 或 `hermes tools` 选择 **Nous Subscription** 仅获取 TTS 功能。
:::

## 文本转语音

支持通过十种不同的服务提供商将文本转换为语音：

| 服务提供商 | 音质 | 费用 | API 密钥 |
|----------|------|------|---------|
| **Edge TTS**（默认） | 良好 | 免费 | 无需密钥 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax TTS** | 优秀 | 付费 | `MINIMAX_API_KEY` |
| **Mistral (Voxtral TTS)** | 优秀 | 付费 | `MISTRAL_API_KEY` |
| **Google Gemini TTS** | 优秀 | 免费套餐 | `GEMINI_API_KEY` |
| **xAI TTS** | 优秀 | 付费 | `XAI_API_KEY` |
| **NeuTTS** | 良好 | 免费（本地运行） | 无需密钥 |
| **KittenTTS** | 良好 | 免费（本地运行） | 无需密钥 |
| **Piper** | 良好 | 免费（本地运行） | 无需密钥 |

### 平台传输方式

| 平台 | 传输方式 | 文件格式 |
|------|----------|----------|
| Telegram | 内嵌语音气泡播放 | Opus `.ogg` |
| Discord | 内嵌语音气泡（Opus/OGG），若无法播放则作为文件附件发送 | Opus/MP3 |
| WhatsApp | 音频文件附件 | MP3 |
| CLI 命令行 | 保存至 `~/.hermes/audio_cache/` 目录 | MP3 |

### 配置选项

```yaml
# In ~/.hermes/config.yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "neutts" | "kittentts" | "piper"
  speed: 1.0                    # Global speed multiplier (provider-specific settings override this)
  edge:
    voice: "en-US-AriaNeural"   # 322 voices, 74 languages
    speed: 1.0                  # Converted to rate percentage (+/-%)
  elevenlabs:
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    model_id: "eleven_multilingual_v2"
  openai:
    model: "gpt-4o-mini-tts"
    voice: "alloy"              # alloy, echo, fable, onyx, nova, shimmer
    base_url: "https://api.openai.com/v1"  # Override for OpenAI-compatible TTS endpoints
    speed: 1.0                  # 0.25 - 4.0
  minimax:
    model: "speech-02-hd"     # speech-02-hd (default), speech-02-turbo
    voice_id: "English_Graceful_Lady"  # See https://platform.minimax.io/faq/system-voice-id
    speed: 1                    # 0.5 - 2.0
    vol: 1                      # 0 - 10
    pitch: 0                    # -12 - 12
  mistral:
    model: "voxtral-mini-tts-2603"
    voice_id: "c69964a6-ab8b-4f8a-9465-ec0925096ec8"  # Paul - Neutral (default)
  gemini:
    model: "gemini-2.5-flash-preview-tts"  # or gemini-3.1-flash-tts-preview
    voice: "Kore"               # 30 prebuilt voices: Zephyr, Puck, Kore, Enceladus, Gacrux, etc.
    audio_tags: false           # Enable hidden Gemini 3.1 TTS audio-tag insertion
    persona_prompt_file: ""      # Optional Markdown/text file with Gemini voice direction
  xai:
    voice_id: "eve"             # or a custom voice ID — see docs below
    language: "en"              # ISO 639-1 code
    sample_rate: 24000          # 22050 / 24000 (default) / 44100 / 48000
    bit_rate: 128000            # MP3 bitrate; only applies when codec=mp3
    # base_url: "https://api.x.ai/v1"   # Override via XAI_BASE_URL env var
  neutts:
    ref_audio: ''
    ref_text: ''
    model: neuphonic/neutts-air-q4-gguf
    device: cpu
  kittentts:
    model: KittenML/kitten-tts-nano-0.8-int8   # 25MB int8; also: kitten-tts-micro-0.8 (41MB), kitten-tts-mini-0.8 (80MB)
    voice: Jasper                               # Jasper, Bella, Luna, Bruno, Rosie, Hugo, Kiki, Leo
    speed: 1.0                                  # 0.5 - 2.0
    clean_text: true                            # Expand numbers, currencies, units
  piper:
    voice: en_US-lessac-medium                  # voice name (auto-downloaded) OR absolute path to .onnx
    # voices_dir: ''                            # default: ~/.hermes/cache/piper-voices/
    # use_cuda: false                           # requires onnxruntime-gpu
    # length_scale: 1.0                         # 2.0 = twice as slow
    # noise_scale: 0.667
    # noise_w_scale: 0.8
    # volume: 1.0                               # 0.5 = half as loud
    # normalize_audio: true
```

**语速控制**：默认情况下，全局的 `tts.speed` 值会适用于所有服务提供商。各提供商可通过自身的 `speed` 设置来覆盖该值（例如 `tts.openai.speed: 1.5`）。特定于提供商的语速设置会优先于全局值，其默认值为 `1.0`（正常语速）。

### Gemini 人物设定提示词

Gemini TTS 能够理解基于自然语言描述的表演指导。您可以将 `tts.gemini.persona_prompt_file` 设置为包含语音角色描述的本地 Markdown 或文本文件。该文件可包含类似 Gemini 格式的各个部分，如 `AUDIO PROFILE`、`SCENE`、`DIRECTOR'S NOTES`、`SAMPLE CONTEXT` 以及 `TRANSCRIPT`。

如果文件中包含 `{transcript}` 或 `{{ transcript }}` 这类占位符，Hermes 会将其替换为实际的文本转语音内容。否则，Hermes 会自动添加一个带有标签的 `TRANSCRIPT` 部分。这些人物设定提示词仅保存在本地，不会显示在聊天回复中。

```yaml
tts:
  provider: gemini
  gemini:
    voice: Algieba
    persona_prompt_file: ~/.hermes/tts/butler-voice.md
```

### Gemini 音频标签功能

Gemini 3.1 Flash TTS 支持使用自由格式的方括号音频标签，例如 `[whispers]`、`[excitedly]`、`[very slow]`、`[laughs]` 以及各类用于表达情感的提示语。通过启用 `tts.gemini.audio_tags`，Hermes 可以在 Gemini TTS 处理之前进行隐式的重写操作。该重写过程仅会在 TTS 脚本中插入内联标签，而用户可见的聊天回复内容则保持不变。

```yaml
tts:
  provider: gemini
  gemini:
    model: gemini-3.1-flash-tts-preview
    audio_tags: true
```

此次重写采用了 `auxiliary.tts_audio_tags` 参数，并默认使用您的主要聊天模型。如果您希望由成本更低或速度更快的模型来处理标签添加功能，可自行覆盖该辅助任务。

### 输入长度限制

各服务提供商均有明确的单次请求输入字符数上限。Hermes 会在调用对应服务前对文本进行截断，因此不会出现因长度超限而导致的请求失败情况：

| 服务提供商 | 默认上限（字符数） |
|----------|---------------------|
| Edge TTS | 5000 |
| OpenAI | 4096 |
| xAI | 15000 |
| MiniMax | 10000 |
| Mistral | 4000 |
| Google Gemini | 32000 |
| ElevenLabs | 根据配置的 `model_id` 决定（见下表） |
| NeuTTS | 2000 |
| KittenTTS | 2000 |
| Piper | 5000 |

**ElevenLabs** 会依据所配置的 `model_id` 来确定输入长度上限：

| `model_id` | 上限（字符数） |
|------------|-------------|
| `eleven_flash_v2_5` | 40000 |
| `eleven_flash_v2` | 30000 |
| `eleven_multilingual_v2`（默认）、`eleven_multilingual_v1`、`eleven_english_sts_v2`、`eleven_english_sts_v1` | 10000 |
| `eleven_v3`、`eleven_ttv_v3` | 5000 |
| 未知模型 | 回退至该服务提供商的默认值（10000） |

您可以在 TTS 配置的服务提供商相关设置中，通过 `max_text_length:` 参数来**为特定服务提供商覆盖此限制**：

```yaml
tts:
  openai:
    max_text_length: 8192   # raise or lower the provider cap
```

系统仅接受正整数作为有效输入。零、负数、非数字值或布尔值将会采用提供商的默认设置，因此配置错误也不会意外导致截断功能被禁用。

### Telegram语音气泡与ffmpeg

Telegram语音气泡要求使用Opus/OGG音频格式：

- **OpenAI、ElevenLabs和Mistral**可直接生成Opus格式音频——无需额外配置
- **Edge TTS**（默认选项）输出MP3格式，需借助**ffmpeg**进行转换
- **MiniMax TTS**同样输出MP3格式，也需要通过**ffmpeg**转换才能用于Telegram语音气泡
- **Google Gemini TTS**输出原始PCM格式，会利用**ffmpeg**直接编码为Opus格式以适配Telegram语音气泡
- **xAI TTS**输出MP3格式，需借助**ffmpeg**转换后才能用于Telegram语音气泡
- **NeuTTS**输出WAV格式，同样需要通过**ffmpeg**转换才能用于Telegram语音气泡
- **KittenTTS**输出WAV格式，也需要通过**ffmpeg**转换才能用于Telegram语音气泡
- **Piper**输出WAV格式，同样需要借助**ffmpeg**转换才能用于Telegram语音气泡

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

若未安装 ffmpeg，Edge TTS、MiniMax TTS、NeuTTS、KittenTTS 以及 Piper audio 将以普通音频文件的形式发送（可播放，但会以矩形播放器显示而非语音气泡）。

:::提示
如果您希望在不安装 ffmpeg 的情况下使用语音气泡功能，请切换至 OpenAI、ElevenLabs 或 Mistral 提供商。
:::

### xAI 自定义语音（语音克隆）

xAI 支持克隆您的声音并将其用于文本转语音功能。您可以在 [xAI 控制台](https://console.x.ai/team/default/voice/voice-library) 中创建自定义语音，然后将在其中生成的 `voice_id` 设置到您的配置文件中：

```yaml
tts:
  provider: xai
  xai:
    voice_id: "nlbqfwie"   # your custom voice ID
```

如需了解有关录音、支持的格式及限制等详细信息，请参阅 [xAI 自定义语音文档](https://docs.x.ai/developers/model-capabilities/audio/custom-voices)。

### Piper（本地版，支持44种语言）

Piper 是由 Open Home Foundation（Home Assistant 的维护团队）开发的快速本地神经网络文本转语音引擎。它完全基于 CPU 运行，预置了**44种语言**的语音模型，且无需 API 密钥。

**通过 `hermes tools` 安装** → Voice & TTS → Piper — Hermes 会自动执行 `pip install piper-tts` 命令。也可手动安装：`pip install piper-tts`。

**切换至 Piper：**

```yaml
tts:
  provider: piper
  piper:
    voice: en_US-lessac-medium
```

对于首次调用且本地未缓存的语音，Hermes会执行`python -m piper.download_voices <name>`命令，将对应模型（大小约为20-90MB，具体取决于质量等级）下载到`~/.hermes/cache/piper-voices/`目录中。后续调用将直接使用已缓存的模型。

**选择语音。**[完整的语音列表](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md)涵盖了英语、西班牙语、法语、德语、意大利语、荷兰语、葡萄牙语、俄语、波兰语、土耳其语、中文、阿拉伯语、印地语等多种语言，每种语言都提供`x_low`/`low`/`medium`/`high`四种质量等级。您可以在[rhasspy.github.io/piper-samples](https://rhasspy.github.io/piper-samples/)处试听这些语音样本。

**使用预下载的语音。**只需将`tts.piper.voice`设置为以`.onnx`为扩展名的绝对路径即可：

```yaml
tts:
  piper:
    voice: /path/to/my-custom-voice.onnx
```

**高级参数**（`tts.piper.length_scale` / `noise_scale` / `noise_w_scale` / `volume` / `normalize_audio`, `use_cuda`）与 Piper 的 `SynthesisConfig` 一一对应。在较旧版本的 `piper-tts` 中，这些参数将被忽略。

### 自定义命令提供器

如果某些您需要的文本转语音引擎未被原生支持（如 VoxCPM、MLX-Kokoro、XTTS CLI、语音克隆脚本，或是任何其他提供命令行接口的工具），您无需编写任何 Python 代码，即可将其作为**命令型提供器**集成进来。Hermes 会将输入文本写入一个临时的 UTF-8 文件，执行您指定的 shell 命令，然后读取该命令生成的音频文件。

您可以在 `tts.providers.<name>` 下声明一个或多个提供器，并通过 `tts.provider: <name>` 来切换使用它们——操作方式与切换 `edge` 和 `openai` 等内置提供器相同。

```yaml
tts:
  provider: voxcpm                 # pick any name under tts.providers
  providers:
    voxcpm:
      type: command
      command: "voxcpm --ref ~/voice.wav --text-file {input_path} --out {output_path}"
      output_format: mp3
      timeout: 180
      voice_compatible: true       # try to deliver as a Telegram voice bubble

    mlx-kokoro:
      type: command
      command: "python -m mlx_kokoro --in {input_path} --out {output_path} --voice {voice}"
      voice: af_sky
      output_format: wav

    piper-custom:                  # native Piper also supports custom .onnx via tts.piper.voice
      type: command
      command: "piper -m /path/to/custom.onnx -f {output_path} < {input_path}"
      output_format: wav
```

#### 示例：豆瓣（Chinese seed-tts-2.0）

若要通过字节跳动的 [seed-tts-2.0](https://www.volcengine.com/docs/6561/1257544) 双向流 API 获取高质量的中文文本转语音效果，可安装 [`doubao-speech`](https://pypi.org/project/doubao-speech/) 这一 PyPI 包，并将其作为命令提供者进行集成：

```bash
pip install doubao-speech
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_TOKEN="your-access-token"
```

```yaml
tts:
  provider: doubao
  providers:
    doubao:
      type: command
      command: "doubao-speech say --text-file {input_path} --out {output_path}"
      output_format: mp3
      max_text_length: 1024
      timeout: 30
```

凭证可从您的shell环境（`VOLCENGINE_APP_ID` / `VOLCENGINE_ACCESS_TOKEN`）或`~/.doubao-speech/config.yaml`中获取。您可以通过在命令后添加`--voice zh-female-warm`（或使用`doubao-speech list-voices`命令查询的其他别名）来选择语音。`doubao-speech`还集成了流式ASR功能——有关Hermes的集成方式，请参阅[下方的STT部分](#example-doubao--volcengine-asr)。源代码及完整文档地址：[github.com/Hypnus-Yuan/doubao-speech](https://github.com/Hypnus-Yuan/doubao-speech)。

#### 占位符

您的命令模板可以引用这些占位符。Hermes会在渲染时替换这些占位符，并根据上下文对每个值进行shell引号处理（无论是裸引号、单引号还是双引号），因此包含空格及其他对shell敏感的字符的路径也能安全使用。

| 占位符          | 含义                                                     |
|------------------|----------------------------------------------------------|
| `{input_path}`   | Hermes生成的临时UTF-8文本文件的路径                        |
| `{text_path}`    | `{input_path}`的别名                                      |
| `{output_path}`  | 命令需要将音频写入的路径                                 |
| `{format}`       | `mp3` / `wav` / `ogg` / `flac`                              |
| `{voice}`        | `tts.providers.<name>.voice`；未设置时为空字符串           |
| `{model}`        | `tts.providers.<name>.model`                               |
| `{speed}`        | 已确定的速度倍率（由特定提供方或全局设置）               |

如需使用字面意义上的大括号，可使用`{{`和`}}`。

#### 可选参数

| 参数名            | 默认值 | 含义                                                                                                      |
|-------------------|--------|------------------------------------------------------------------------------------------------------------|
| `timeout`          | `120`   | 秒数；超时后进程树将被终止（Unix系统使用`killpg`，Windows系统使用`taskkill /T`）。               |
| `output_format`    | `mp3`   | `mp3` / `wav` / `ogg` / `flac`之一。若Hermes自动选择了输出路径，则会根据文件扩展名自动推断格式。      |
| `voice_compatible` | `false` | 当设置为`true`时，Hermes会通过ffmpeg将MP3/WAV格式的输出转换为Opus/OGG格式，以便Telegram正确显示语音气泡。 |
| `max_text_length`  | `5000`  | 在执行命令之前，输入文本会被截断到该长度。                                                                         |
| `voice` / `model`  | 空字符串 | 仅作为占位符值传递给命令，不会实际被使用。                                                                           |

#### 行为说明

- **内置提供方始终优先。** `tts.providers.openai`条目永远不会覆盖原生的OpenAI提供方，因此任何用户配置都无法悄无声息地替换内置提供方。
- **默认交付方式为文档格式。** 所有平台的命令提供方都会以普通音频附件的形式输出内容。如需让特定提供方以语音气泡形式输出，可设置`voice_compatible: true`。
- **命令执行失败会反馈给智能体。** 若命令返回非零退出码、输出为空或发生超时，系统会将错误信息连同命令的stderr/stdout一起返回，便于您在对话中调试相关提供方。
- 当设置了`command:`参数时，`type: command`为默认值。虽然显式写出`type: command`是良好习惯，但并非必需；只要`command`字符串非空，该条目即被视为命令提供方。
- `{input_path}` / `{text_path}`可以互换使用。请选择在您的命令中更易理解的格式。

#### 安全性

命令型提供方会以用户的权限执行您配置的任何shell命令。Hermes会对占位符值进行引号处理，并强制执行预设的超时时间，但命令模板本身属于可信的本地输入——请像对待PATH中的shell脚本一样谨慎处理。

### Python插件提供方

对于那些无法用单个shell命令实现的TTS引擎——例如没有CLI的Python SDK、流式引擎、语音列表API以及需要OAuth刷新认证的引擎——您可以通过`ctx.register_tts_provider()`注册Python插件。此类插件与[自定义命令提供方](#custom-command-providers)注册系统**共存**（而非替代），您可以根据引擎的特性选择合适的呈现方式。

#### 如何选择

| 您的后端具备……               | 推荐使用       |
|------------------------------|----------------|
| 一个可从文件/标准输入读取文本、并向文件/标准输出写入音频的CLI | **命令提供方**（无需Python） |
| 通过shell管道串联的两个或三个CLI | **命令提供方**     |
| 仅有Python SDK，没有CLI         | **插件**         |
| 需要分块传输的流式数据（用于生成中的语音气泡） | **插件**（需重写`stream()`函数） |
| 被`hermes setup`使用的语音列表API | **插件**（需重写`list_voices()`函数） |
| 需要OAuth刷新机制的认证方式（非静态令牌） | **插件**         |

内置提供方始终优先，而同名的命令提供方也会优先于同名插件——因此，您可以放心地为任何非内置名称注册插件，无需担心会覆盖现有的配置。

#### 最简插件示例

将以下内容放入`~/.hermes/plugins/my-tts/`目录中：

`plugin.yaml`：
```yaml
name: my-tts
version: 0.1.0
description: "My custom Python TTS backend"
```

`__init__.py`：
```python
from agent.tts_provider import TTSProvider


class MyTTSProvider(TTSProvider):
    @property
    def name(self) -> str:
        return "my-tts"  # what tts.provider matches against

    @property
    def display_name(self) -> str:
        return "My Custom TTS"

    def is_available(self) -> bool:
        # Return False when credentials/deps are missing — picker skips
        # this row but the dispatcher still routes here on explicit config.
        import os
        return bool(os.environ.get("MY_TTS_API_KEY"))

    def synthesize(self, text, output_path, *, voice=None, model=None,
                   speed=None, format="mp3", **extra) -> str:
        # Write audio bytes to output_path, return the path.
        # Raise on failure — the dispatcher converts exceptions to a
        # standard error envelope.
        import my_tts_sdk
        client = my_tts_sdk.Client()
        audio_bytes = client.synthesize(text=text, voice=voice or "default")
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return output_path


def register(ctx):
    ctx.register_tts_provider(MyTTSProvider())
```

首先启用该插件（执行 `hermes plugins enable my-tts`），然后在 `config.yaml` 中将 `tts.provider` 设置为该插件的名称（即 `tts.provider: my-tts`），这样 `text_to_speech` 工具就会通过您所启用的插件来处理请求。

#### 可选钩子函数

您可以在自定义的提供者类中重写这些函数，以实现更深度的集成：

- `list_voices()` → 返回一个包含 `{id, display, language, gender, preview_url}` 字典的列表，这些内容会显示在 `hermes tools` 中。
- `list_models()` → 返回一个包含 `{id, display, languages, max_text_length}` 字典的列表。
- `get_setup_schema()` → 返回 `{name, badge, tag, env_vars: [{key, prompt, url}]}` 的结构，用于丰富 `hermes tools` 和 `hermes setup` 中的选项选择行。即使不提供此函数，插件仍可正常工作，但其选项行的显示内容会较为简略。
- `stream(text, *, voice, model, format, **extra)` → 返回一个迭代器，用于逐块生成音频字节以实现流式传输（默认情况下会抛出 `NotImplementedError` 异常）。
- `voice_compatible` 属性 → 如果您的输出格式兼容 Opus 且希望网关以语音气泡的形式呈现，可将其设置为 `True`（默认值为 `False`，此时为普通音频附件）。

完整的 ABC 模板及文档字符串请参阅 `agent/tts_provider.py` 文件。

## 语音消息转录（STT）

通过 Telegram、Discord、WhatsApp、Slack 或 Signal 发送的语音消息会自动被转录成文本，并插入对话中。智能体会将这些转录后的文本视为普通文本处理。

| 提供者 | 转录质量 | 成本 | API 密钥 |
|--------|----------|------|---------|
| **Local Whisper**（默认） | 较好 | 免费 | 无需密钥 |
| **Groq Whisper API** | 较好–优秀 | 免费套餐 | `GROQ_API_KEY` |
| **OpenAI Whisper API** | 较好–优秀 | 需付费 | `VOICE_TOOLS_OPENAI_KEY` 或 `OPENAI_API_KEY` |

:::info 无需额外配置
只要安装了 `faster-whisper`，即可直接实现本地转录功能。如果该工具不可用，Hermes 还可以调用常见安装路径（如 `/opt/homebrew/bin`）下的本地 `whisper` CLI 工具，或者通过 `HERMES_LOCAL_STT_COMMAND` 指定自定义命令。
:::

### 配置选项

```yaml
# In ~/.hermes/config.yaml
stt:
  provider: "local"           # "local" | "groq" | "openai" | "mistral" | "xai"
  local:
    model: "base"             # tiny, base, small, medium, large-v3
  openai:
    model: "whisper-1"        # whisper-1, gpt-4o-mini-transcribe, gpt-4o-transcribe
  mistral:
    model: "voxtral-mini-latest"  # voxtral-mini-latest, voxtral-mini-2602
  xai:
    model: "grok-stt"         # xAI Grok STT
```

### 提供商详情

**本地模式（faster-whisper）** — 通过 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在本地运行 Whisper 模型。默认使用 CPU，若有 GPU 则会优先使用。各模型参数如下：

| 模型 | 大小 | 速度 | 质量 |
|------|------|------|---------|
| `tiny` | 约 75 MB | 最快 | 基础水平 |
| `base` | 约 150 MB | 快 | 较好（默认） |
| `small` | 约 500 MB | 中等 | 更佳 |
| `medium` | 约 1.5 GB | 较慢 | 极佳 |
| `large-v3` | 约 3 GB | 最慢 | 最优 |

**Groq API** — 需要提供 `GROQ_API_KEY`。若希望使用免费的托管语音转文字服务，这是不错的云端备选方案。

**OpenAI API** — 先尝试使用 `VOICE_TOOLS_OPENAI_KEY`，若无效则回退至 `OPENAI_API_KEY`。支持 `whisper-1`、`gpt-4o-mini-transcribe` 和 `gpt-4o-transcribe` 模型。

**Mistral API（Voxtral Transcribe）** — 需要提供 `MISTRAL_API_KEY`。使用 Mistral 的 [Voxtral Transcribe](https://docs.mistral.ai/capabilities/audio/speech_to_text/) 模型，支持 13 种语言、说话人分离以及单词级时间戳功能。可通过以下命令安装：`cd ~/.hermes/hermes-agent && uv pip install -e ".[mistral]"`。

**xAI Grok STT** — 需要提供 `XAI_API_KEY`。以 multipart/form-data 格式将数据发送至 `https://api.x.ai/v1/stt`。如果您已经在使用 xAI 进行聊天或文本转语音功能，并希望用一个 API 密钥统一管理所有服务，这是一个不错的选择。系统会按默认顺序在 Groq 之后尝试该方案——如需强制使用，可显式设置 `stt.provider: xai`。

**自定义本地 CLI 备选方案** — 若希望 Hermes 直接调用本地的转录命令，可设置 `HERMES_LOCAL_STT_COMMAND`。命令模板支持 `{input_path}`、 `{output_dir}`、 `{language}` 和 `{model}` 等占位符。您编写的命令必须将转录结果以 `.txt` 格式写入 `{output_dir}` 指定的目录中。

#### 示例：Doubao / Volcengine ASR

如果您使用 [`doubao-speech`](https://pypi.org/project/doubao-speech/) 来实现 Doubao 文本转语音功能（参见上文 [示例：Doubao 中文文本转语音](#example-doubao-chinese-seed-tts-20)），则同一个包也可通过本地命令接口实现语音转文字功能。

```bash
pip install doubao-speech
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_TOKEN="your-access-token"
export HERMES_LOCAL_STT_COMMAND='doubao-speech transcribe {input_path} --out {output_dir}/transcript.txt'
```

```yaml
stt:
  provider: local_command
```

Hermes会将接收到的语音消息写入`{input_path}`，执行相应命令，然后读取`{output_dir}`目录下生成的`.txt`文件。语言类型由Volcengine大模型端点自动识别。

### 回退机制

如果配置的提供服务不可用，Hermes会自动进行回退：
- **本地faster-whisper不可用** → 先尝试使用本地的`whisper` CLI或`HERMES_LOCAL_STT_COMMAND`，再尝试云服务提供商
- **未设置Groq密钥** → 先使用本地转录功能，再尝试OpenAI
- **未设置OpenAI密钥** → 先使用本地转录功能，再尝试Groq
- **未设置Mistral密钥/SDK** → 在自动检测阶段跳过该选项，直接使用下一个可用的提供服务
- **所有选项均不可用** → 语音消息将原样传递给用户，并附上说明

### STT自定义命令提供者

如果所需的语音转文字引擎未被原生支持（如Doubao ASR、NVIDIA Parakeet、基于whisper.cpp的版本、开源的SenseVoice CLI，或任何能调用Shell命令的工具），无需编写任何Python代码，即可将其作为**命令型提供者**接入系统。Hermes会针对音频文件执行您指定的Shell命令，并读取生成的转录文本。

可以在`stt.providers.<name>`下声明一个或多个提供者，通过`stt.provider: <name>`来切换使用——其结构与TTS[自定义命令提供者注册表](#custom-command-providers)相同，只是适配了“输入=音频 → 输出=转录文本”的处理流程。

```yaml
stt:
  provider: parakeet                # pick any name under stt.providers
  providers:
    parakeet:
      type: command
      command: "parakeet-asr --model nvidia/parakeet-tdt-0.6b-v2 --in {input_path} --out {output_path}"
      format: txt
      language: en
      timeout: 300

    whispercpp:
      type: command
      command: "whisper-cli -m ~/models/ggml-large-v3.bin -f {input_path} -otxt -of {output_dir}/transcript"
      format: txt

    sensevoice:
      type: command
      command: "sensevoice-cli {input_path} --json | tee {output_path}"
      format: json
```

该机制是对传统 `HERMES_LOCAL_STT_COMMAND` 逃生通道的补充——通过内置的 `local_command` 路径，该环境变量依然可以不受影响地继续使用。当您需要**多个**基于 Shell 的语音转文字引擎、希望通过 `stt.provider` 自定义引擎名称，或需要对每个提供程序单独设置 `language`/`model`/`timeout` 参数时，可使用 `stt.providers.<name>`。

#### 语音转文字占位符

您的命令模板可引用这些占位符。Hermes 会在渲染时替换它们，并根据上下文对每个值进行 Shell 引用处理（原始形式、单引号形式或双引号形式），因此包含空格的路径也能正常使用。

| 占位符           | 含义                                                                |
|------------------|----------------------------------------------------------------------|
| `{input_path}`    | 输入音频文件的绝对路径（原始位置，仅读）                             |
| `{output_path}`   | 命令应将转录结果写入的绝对路径                                     |
| `{output_dir}`    | `{output_path}` 的父目录（适用于类似 whisper 的工具）                 |
| `{format}`        | 预设的输出格式：`txt` / `json` / `srt` / `vtt`                       |
| `{language}`      | 预设的语言代码（默认为 `en`）                                      |
| `{model}`         | `stt.providers.<name>.model` 的形式；若未设置则为空                 |

如需在命令中嵌入 JSON 片段，可使用 `{{` 和 `}}` 来表示原始的大括号。

#### 转录结果的读取方式

当您的命令成功执行后：

1. 若 `{output_path}` 存在且非空 → Hermes 会以 UTF-8 文本格式读取该文件。
2. 否则，若命令将结果输出到标准输出 → Hermes 会使用该输出内容。
3. 否则 → 会出现错误：“命令对应的语音转文字提供程序未生成任何输出文件，也未产生标准输出”。

这让您既可以使用那些支持写入文件的 CLI 工具（如 `whisper-cli`、`parakeet-asr`），也可以使用将转录结果输出到标准输出的 curl 风格单行命令（如 `curl … | jq -r .text`）。

对于 `format: json` / `srt` / `vtt` 的格式，Hermes 会将原始文件内容作为 `transcript` 字段返回。从 JSON 中提取 `.text` 内容超出了运行器的处理范围——您可以选择将格式设置为 `txt`，或在上游对 JSON 进行后处理。

#### 语音转文字命令提供程序的可选参数

| 参数             | 默认值 | 含义                                                                                              |
|-----------------|--------|------------------------------------------------------------------------------------------------------|
| `timeout`       | `300`   | 秒数；超过该时间后进程树将被终止（Unix 系统使用 `start_new_session`，Windows 系统使用 `taskkill /T`）。 |
| `format`        | `txt`   | `txt` / `json` / `srt` / `vtt` 之一。同时决定了 `{output_path}` 的文件扩展名。                       |
| `language`      | `en`    | 该参数会传递给 `{language}`。默认值为 `stt.language`，若仍为默认值则使用 `en`。                     |
| `model`         | 空     | 该参数会传递给 `{model}`。若调用 `transcribe_audio()` 时指定了 `model=` 参数，则该值会被覆盖。                |

#### 语音转文字命令提供程序的行为说明

- **内置提供程序始终优先。** 即使您声明了 `stt.providers.openai: type: command`，也不会覆盖真正的 OpenAI Whisper 处理器。在命令提供程序解析器运行之前，系统会直接使用内置提供程序。
- **进程树清理机制。** 当达到 `timeout` 时间限制时，整个进程树都会被终止，而不仅仅是 Shell 包装层。那些会创建用于加载模型的子进程的长时间运行的 ASR 管道也能被可靠地终止。
- **自动进行 Shell 引用处理。** 位于单引号 `'…'` 内的占位符会进行单引号安全的转义处理；位于双引号 `"…"` 内的占位符会进行 `$`/`` ` ``/`"` 转义处理；位于引号外的占位符则会使用 `shlex.quote` 进行处理。无需预先对占位符值添加引号。

#### 语音转文字命令提供程序的安全性

Shell 命令会在与 Hermes 相同的用户权限下运行，并拥有完整的文件系统访问权限——其安全信任模型与 `tts.providers.<name>: type: command` 和 `HERMES_LOCAL_STT_COMMAND` 完全一致。请仅从您信任的来源注册命令提供程序。

### Python 插件提供程序（语音转文字）

对于那些非内置且无法用 Shell 命令实现的语音转文字引擎（需要 Python SDK、支持 OAuth 刷新认证、支持流式传输数据块等），可通过 `ctx.register_transcription_provider()` 注册 Python 插件。这类插件与 6 个内置提供程序（`local`、`local_command`、`groq`、`openai`、`mistral`、`xai`）以及 `stt.providers.<name>: type: command` 注册表**共存**——内置提供程序会保留其原生实现，且在名称冲突时始终优先；而相同名称的命令提供程序则会优先于插件（因为命令提供程序的配置更为本地化，无需安装插件）。

#### 如何选择合适的方式（语音转文字）

| 后端支持的功能                                                 | 推荐使用方式                                      |
|--------------------------------------------------------------|--------------------------------------------------|
| 一个可接收音频文件并直接输出文本的单个 Shell 命令           | `stt.providers.<name>: type: command`（无需 Python）       |
| 仅需使用传统的单命令逃生通道                                 | `HERMES_LOCAL_STT_COMMAND` 环境变量（为兼容旧版本保留） |
| 没有 CLI 接口的 Python SDK                                     | 使用 `register_transcription_provider()` 注册插件         |
| 需要 OAuth 刷新认证、流式传输数据块或语音列表元数据功能       | 使用 `register_transcription_provider()` 注册插件         |
| 已有内置提供程序可满足需求（如 `local`、`groq`、`openai` 等） | 设置 `stt.provider: <name>`——内置提供程序直接可用     |

#### 解析顺序

1. **`stt.provider` 是内置提供程序名称** → 直接使用内置提供程序。**始终优先。**
2. **`stt.provider` 的值与设置了 `command:` 参数的 `stt.providers.<name>` 匹配** → 使用命令提供程序运行器（详见[自定义语音转文字命令提供程序](#stt-custom-command-providers)）。此类提供程序会优先于同名插件。
3. **`stt.provider` 的值与插件注册的 `TranscriptionProvider` 对象匹配** → 使用插件运行器：
   - 若插件的 `is_available()` 方法返回 `False`（如缺少凭证或 SDK），则会产生一个错误信息，明确指出是该插件不可用——而非通用的“没有可用的语音转文字提供程序”提示。
   - 否则，会使用公共的 `model=` 参数指定的模型名称（若未指定则默认为 `stt.<provider>.model`）以及 `stt.<provider>.language` 指定的语言，调用插件的 `transcribe()` 方法。
4. **无匹配项** → 产生“没有可用的语音转文字提供程序”错误。

#### 各提供程序的配置命名空间

插件会从 `config.yaml` 文件中的 `stt.<provider>` 部分读取针对该提供程序的配置，其方式与内置提供程序读取 `stt.openai.model`/`stt.mistral.model` 的方式类似：

```yaml
stt:
  provider: my-stt
  my-stt:
    model: whisper-large-v3
    language: ja          # forwarded as language= to transcribe()
    # any other plugin-specific keys go here; read them via your
    # own config.yaml access in __init__/is_available/transcribe
```

调度器会从此部分传递 `model` 和 `language` 参数；其余所有信息，插件均可自行读取。

#### 最简插件

将其放入 `~/.hermes/plugins/my-stt/` 目录中：

`plugin.yaml`：
```yaml
name: my-stt
version: 0.1.0
description: "My custom Python STT backend"
```

`__init__.py`：
```python
from agent.transcription_provider import TranscriptionProvider


class MySTTProvider(TranscriptionProvider):
    @property
    def name(self) -> str:
        return "my-stt"  # what stt.provider matches against

    @property
    def display_name(self) -> str:
        return "My Custom STT"

    def is_available(self) -> bool:
        # Return False when credentials/deps are missing — picker skips
        # this row but the dispatcher still routes here on explicit config.
        import os
        return bool(os.environ.get("MY_STT_API_KEY"))

    def transcribe(self, file_path, *, model=None, language=None, **extra):
        # Return the standard transcribe envelope:
        #   {"success": bool, "transcript": str, "provider": str, "error": str}
        # Do NOT raise — convert exceptions to the error envelope so the
        # gateway/CLI caller sees a consistent shape on failure.
        try:
            import my_stt_sdk
            client = my_stt_sdk.Client()
            text = client.transcribe(open(file_path, "rb"))
            return {
                "success": True,
                "transcript": text,
                "provider": "my-stt",
            }
        except Exception as exc:
            return {
                "success": False,
                "transcript": "",
                "error": f"my-stt failed: {exc}",
                "provider": "my-stt",
            }


def register(ctx):
    ctx.register_transcription_provider(MySTTProvider())
```

首先通过命令 `hermes plugins enable my-stt` 启用该插件，然后在 `config.yaml` 中设置 `stt.provider: my-stt`，这样语音消息的转录功能就会通过您所配置的插件来处理。

#### 可选钩子函数

如需实现更深度的集成，可在您的提供者类中重写以下函数：

- `list_models()` → 返回包含 `{id, display, languages, max_audio_seconds}` 字典的列表。
- `default_model()` → 当用户未指定模型时返回的字符串。
- `get_setup_schema()` → 返回 `{name, badge, tag, env_vars: [{key, prompt, url}]}`，用于填充 `hermes tools` / `hermes setup` 中的选项行（目前 STT 类别的选择器尚未正式推出——提供这些元数据是为了确保插件的向后兼容性）。

如需查看包含文档字符串的完整 ABC 接口定义，请参阅 `agent/transcription_provider.py` 文件。
