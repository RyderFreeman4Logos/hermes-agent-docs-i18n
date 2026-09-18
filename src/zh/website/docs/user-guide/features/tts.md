---
sidebar_position: 9
title: "Voice & TTS"
description: "Text-to-speech and voice message transcription across all platforms"
---

# 语音与文本转语音功能

Hermes Agent 支持在所有消息传递平台上实现文本转语音输出以及语音消息的转录功能。

:::提示 Nous 订阅用户
如果您拥有付费的 [Nous Portal](https://portal.nousresearch.com) 订阅资格，无需单独获取 OpenAI API 密钥，即可通过 **[Tool Gateway](tool-gateway.md)** 使用 OpenAI TTS 功能。新安装的用户可运行 `hermes setup --portal` 进行登录并一次性启用所有网关工具；已有安装的用户则可通过 `hermes model` 或 `hermes tools` 选择 **Nous Subscription** 仅获取文本转语音功能。
:::

## 文本转语音

支持通过十余种服务提供商将文本转换为语音：

| 服务提供商 | 音质 | 费用 | API 密钥 |
|----------|------|------|---------|
| **Edge TTS**（默认） | 良好 | 免费 | 无需密钥 |
| **ElevenLabs** | 优秀 | 付费 | `ELEVENLABS_API_KEY` |
| **OpenAI TTS** | 良好 | 付费 | `VOICE_TOOLS_OPENAI_KEY` |
| **MiniMax TTS** | 优秀 | 付费 | `MINIMAX_API_KEY` 或 `MINIMAX_CN_API_KEY` |
| **Mistral (Voxtral TTS)** | 优秀 | 付费 | `MISTRAL_API_KEY` |
| **Google Gemini TTS** | 优秀 | 免费套餐 | `GEMINI_API_KEY` |
| **xAI TTS** | 优秀 | 付费 | `XAI_API_KEY` |
| **DeepInfra TTS** | 良好 | 付费 | `DEEPINFRA_API_KEY` |
| **NeuTTS** | 良好 | 免费（本地运行） | 无需密钥 |
| **KittenTTS** | 良好 | 免费（本地运行） | 无需密钥 |
| **Piper** | 良好 | 免费（本地运行） | 无需密钥 |

### 平台交付方式

| 平台 | 传输方式 | 格式 |
|----------|----------|------|
| Telegram | 内嵌语音气泡 | Opus `.ogg` |
| Discord | 内嵌语音气泡（Opus/OGG），备用方式为文件附件 | Opus/MP3 |
| WhatsApp | 音频文件附件 | MP3 |
| CLI | 保存至 `~/.hermes/audio_cache/` 目录 | MP3 |

### 配置选项

```yaml
# In ~/.hermes/config.yaml
tts:
  provider: "edge"              # "edge" | "elevenlabs" | "openai" | "minimax" | "mistral" | "gemini" | "xai" | "deepinfra" | "neutts" | "kittentts" | "piper" — or "nous" for the managed Tool Gateway (written when you pick Nous Subscription in `hermes tools`)
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
    # language: "es"            # Sent as lang_code — only for OpenAI-compatible endpoints that support it (e.g. Kokoro)
  minimax:
    region: "global"           # "global" or "cn"; see selection rules below
    model: "speech-02-hd"     # speech-02-hd (default), speech-02-turbo
    voice_id: "English_expressive_narrator"  # See https://platform.minimax.io/faq/system-voice-id
    speed: 1                    # 0.5 - 2.0
    vol: 1                      # 0 - 10
    pitch: 0                    # -12 - 12
    # base_url: "https://tts.example/v1/t2a_v2"  # Optional endpoint override for the selected region
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
    language: "en"              # BCP-47 code (e.g. "en", "pt-BR") or "auto" for detection
    speed: 1.0                  # 0.7–1.5, playback speed (default: 1.0)
    auto_speech_tags: false     # insert expressive audio tags via LLM rewrite
    text_normalization: false   # normalize numbers/abbreviations/symbols to spoken form
    optimize_streaming_latency: 0  # 0–2, trades quality for lower latency (default: 0)
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

MiniMax TTS会同时确定对应的区域、端点以及认证密钥：

- 当`region: "global"`时，将使用`https://api.minimax.io/v1/t2a_v2`接口，并搭配`MINIMAX_API_KEY`。
- 当`region: "cn"`时，则使用`https://api.minimaxi.com/v1/t2a_v2`接口，并搭配`MINIMAX_CN_API_KEY`。
- 如果未指定`region`值，为保持向后兼容性，系统会优先使用`MINIMAX_API_KEY`。如果仅配置了`MINIMAX_CN_API_KEY`，Hermes则会自动选择“cn”区域。
- 明确指定的区域必须配备对应的认证密钥。Hermes绝不会借用其他区域的密钥。即使设置了`base_url`，也不会改变已选定的认证密钥；同时，指向其他区域官方端点的配置将被拒绝。

**速度控制**：默认情况下，全局设定的`tts.speed`值会适用于所有服务提供商。各提供商可通过自行设置`speed`参数来覆盖该全局值（例如`tts.openai.speed: 1.5`）。特定于提供商的速度设置会优先于全局值，默认值为`1.0`（正常速度）。

### Gemini角色提示词

Gemini TTS能够根据自然语言描述来调整语音风格。只需将`tts.gemini.persona_prompt_file`设置为包含语音角色描述的本地Markdown文件或文本文件即可。该文件可包含类似Gemini格式的各个部分，如`AUDIO PROFILE`、`SCENE`、`DIRECTOR'S NOTES`、`SAMPLE CONTEXT`以及`TRANSCRIPT`。

如果文件中包含 `{transcript}` 或 `{{ transcript }}` 这类占位符，Hermes会将其替换为实际的文本转语音内容。否则，Hermes会自动添加一个带有标签的`TRANSCRIPT`部分。这些角色提示词仅保存在本地，不会显示在聊天回复中。

```yaml
tts:
  provider: gemini
  gemini:
    voice: Algieba
    persona_prompt_file: ~/.hermes/tts/butler-voice.md
```

### 音频标签（Gemini、xAI）

Google 的 Gemini 3.1 Flash TTS 以及 xAI 的 Grok TTS 支持使用诸如 `[whispers]`、`[excitedly]`、`[very slow]`、`[laughs]` 等自由格式的方括号音频标签，以实现多样化的表达效果。若需让 Hermes 在文本转语音处理之前先进行隐式重写，可启用 `tts.gemini.audio_tags` 或 `tts.xai.auto_speech_tags`。该重写功能仅会在文本转语音脚本中插入这些内联标签，而用户可见的聊天回复内容则保持不变。

```yaml
tts:
  provider: gemini
  gemini:
    model: gemini-3.1-flash-tts-preview
    audio_tags: true
  xai: 
    auto_speech_tags: true
```

此次重写采用了 `auxiliary.tts_audio_tags` 功能，并默认使用您的主要聊天模型。如果您希望由成本更低或响应更快的模型来处理标签添加任务，可自行覆盖该辅助任务。

**语言（兼容 OpenAI 的端点）**：`tts.openai.language` 会作为 `lang_code` 请求参数传递给对应端点。该参数适用于支持 `lang_code` 的兼容 OpenAI 的文本转语音服务器——例如 [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI)，在此框架中设置 `language: "es"` 即可选择西班牙语发音器而非默认的英语发音器。若使用官方 OpenAI API，则无需设置该参数，因其不支持此参数；未设置时不会发送任何额外信息。

### 输入长度限制

各服务提供商均有明确的单次请求输入字符上限规定。Hermes 会在调用对应服务前，将较长的回复按顺序分割成考虑句子结构的片段，从而确保完整的标准化文本不被无声截断：

| 服务提供商 | 默认上限（字符数） |
|----------|---------------------|
| Edge TTS | 5000 |
| OpenAI | 4096 |
| xAI | 15000 |
| MiniMax | 10000 |
| Mistral | 4000 |
| Google Gemini | 32000 |
| ElevenLabs | 根据配置的 `model_id` 决定 |

| `model_id` | 字符上限 |
|------------|----------|
| `eleven_flash_v2_5` | 40000 |
| `eleven_flash_v2` | 30000 |
| `eleven_multilingual_v2`（默认值）、`eleven_multilingual_v1`、`eleven_english_sts_v2`、`eleven_english_sts_v1` | 10000 |
| `eleven_v3`、`eleven_ttv_v3` | 5000 |
| 未知模型 | 将回退至对应提供方的默认值（10000） |

您可以在 TTS 配置的“提供方”部分中使用 `max_text_length:` 选项来**为特定提供方覆盖此默认值**：

```yaml
tts:
  openai:
    max_text_length: 8192   # raise or lower the provider cap
```

系统仅接受正整数作为有效输入。零、负数、非数字值或布尔值将会沿用提供商的默认设置，因此即使配置出现错误，也不会意外绕过提供商设定的请求限制。

### Telegram语音气泡与ffmpeg

Telegram语音气泡要求使用Opus/OGG音频格式：

- **OpenAI、ElevenLabs和Mistral**可直接生成Opus格式音频——无需额外配置；
- **Edge TTS**（默认选项）输出MP3格式，需借助**ffmpeg**进行转换；
- **MiniMax TTS**同样输出MP3格式，亦需通过**ffmpeg**转换才能用于Telegram语音气泡；
- **Google Gemini TTS**输出原始PCM格式，会利用**ffmpeg**直接将其编码为Opus格式以适配Telegram语音气泡；
- **xAI TTS**输出MP3格式，同样需要**ffmpeg**转换才能用于Telegram语音气泡；
- **NeuTTS**输出WAV格式，也需要**ffmpeg**转换后才能用于Telegram语音气泡；
- **KittenTTS**输出WAV格式，同样需通过**ffmpeg**转换才能用于Telegram语音气泡；
- **Piper**输出WAV格式，也需要**ffmpeg**转换才能用于Telegram语音气泡。

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
如果您希望在不安装 ffmpeg 的情况下使用语音气泡功能，可切换至 OpenAI、ElevenLabs 或 Mistral 提供商。
:::

### xAI 自定义语音（语音克隆）

xAI 支持克隆您的声音并将其用于文本转语音功能。您可以在 [xAI 控制台](https://console.x.ai/team/default/voice/voice-library) 中创建自定义语音，随后在配置文件中设置对应的 `voice_id`：

```yaml
tts:
  provider: xai
  xai:
    voice_id: "nlbqfwie"   # your custom voice ID
```

如需了解关于录音、支持的格式及限制等详细信息，请参阅 [xAI 自定义语音文档](https://docs.x.ai/developers/model-capabilities/audio/custom-voices)。

### Piper（本地版，支持44种语言）

Piper 是由 Open Home Foundation（Home Assistant 的维护团队）开发的快速本地神经网络文本转语音引擎。它完全基于 CPU 运行，预置了 **44种语言**的语音模型，且无需 API 密钥。

**通过 `hermes tools` 安装**：依次选择“语音与文本转语音”→“Piper”，Hermes 会自动执行 `pip install piper-tts` 命令。也可手动安装：`pip install piper-tts`。

**切换至 Piper：**

```yaml
tts:
  provider: piper
  piper:
    voice: en_US-lessac-medium
```

对于首次调用且本地未缓存的语音，Hermes会运行`python -m piper.download_voices <name>`命令，将对应模型（大小约为20-90MB，具体取决于质量等级）下载到`~/.hermes/cache/piper-voices/`目录中。后续调用则会直接使用已缓存的模型。

**选择语音。**[完整的语音列表](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md)涵盖了英语、西班牙语、法语、德语、意大利语、荷兰语、葡萄牙语、俄语、波兰语、土耳其语、汉语、阿拉伯语、印地语等多种语言，每种语言都提供`x_low`/`low`/`medium`/`high`四种质量等级。您可以在[rhasspy.github.io/piper-samples](https://rhasspy.github.io/piper-samples/)处试听各类语音样本。

**使用预下载的语音。**将`tts.piper.voice`设置为以`.onnx`为扩展名的绝对路径即可：

```yaml
tts:
  piper:
    voice: /path/to/my-custom-voice.onnx
```

**高级参数**（如 `tts.piper.length_scale` / `noise_scale` / `noise_w_scale` / `volume` / `normalize_audio`、`use_cuda`）与 Piper 的 `SynthesisConfig` 一一对应。在较旧版本的 `piper-tts` 中，这些参数将被忽略。

### 通过语音开关实现预热与模型卸载（本地引擎）

本地引擎（Piper、KittenTTS）会以按需加载的方式启动模型，因此若不加以控制，在开启语音功能后产生的*第一个*语音回复前，系统会先耗费大量时间加载完整模型——在全新安装系统中，还需额外下载语音文件，这段时间内系统将处于静默状态。Hermes 会将语音输出开关视为需要使用文本转语音功能的信号：

- **桌面端** — “大声朗读回复”是一项独立的桌面端设置，与设置 → 语音选项中的网关 `voice.auto_tts` 设置无关。该设置只会同步一次，之后即使网关配置发生变化，也不会覆盖桌面端的设置。即便本地存储已满或不可用，此设置仍会在当前会话期间有效；至于在重启后保持设置状态，则取决于系统性能。开启“大声朗读回复”或开始“语音对话”时，系统会立即在后台预加载已配置的引擎。再次关闭这两项功能则会导致相应模型被卸载（Piper 语音模型的大小约为数十 MB，KittenTTS 则高达约 80 MB），从而避免内存被无谓占用。
- **命令行/终端界面** — 使用 `/voice tts` 命令（当设置了 `voice.auto_tts` 时也可使用 `/voice on`）可实现相同功能；而 `/voice off` 命令则用于卸载模型。
每个开关都会为引擎获取一个*租约*；只有当所有相关表面的租约都被释放后，模型才会被卸载。因此，在某个桌面窗口中关闭朗读功能，不会影响另一个窗口中正在进行的对话的语音输出。对于云服务提供商而言，并不存在需要保留的模型——该开关仅用于确保已按需懒加载的 SDK（如 edge-tts、ElevenLabs、Mistral）处于可用状态。预热操作为尽力而为：即便引擎无法加载，开关操作仍会成功，首次回复会像以往一样采用按需加载的方式。

桌面端会通过 `POST /api/audio/tts-lease` 请求发送参数 `{"lease": "<name>", "active": true|false}`；其他前端也可以使用相同的接口。

同一个租约同样适用于用户自定义的服务提供商，因此自托管的 TTS 服务器可以根据开关状态来预加载或卸载模型：[命令提供者](#custom-command-providers) 可以执行其可选的 `warm_command`/`release_command`，而 [Python 插件提供者](#python-plugin-providers) 则可通过 `warm()`/`release()` 方法来控制模型的加载与释放。

### 自定义命令提供者

如果某些你想要的 TTS 引擎未被原生支持（如 VoxCPM、MLX-Kokoro、XTTS CLI、语音克隆脚本，或是任何提供命令行接口的工具），你无需编写任何 Python 代码，即可将其作为**命令型提供者**接入系统。Hermes 会将输入文本写入一个临时的 UTF-8 文件，运行你指定的 Shell 命令，然后读取该命令生成的音频文件。

可以在 `tts.providers.<name>` 下声明一个或多个提供者，然后通过 `tts.provider: <name>` 在它们之间切换——操作方式与在 `edge` 和 `openai` 等内置提供者之间切换完全相同。

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

**支持的 `output_format` 值包括：** `mp3`（默认值）、`wav`、`ogg`、`flac`、`m4a`、`aac`、`amr`、`opus`。您的命令必须实际生成这些格式的文件（可通过 `ffmpeg` 等工具实现）；Hermes 仅会验证所指定的格式，并据此为输出文件命名。若遇到未知格式，系统将自动回退为 `mp3`。所选格式还会以 `{format}` 作为占位符显示在命令中。

**子进程环境设置：** TTS 和 STT 相关的命令执行时，子进程中会移除所有 Hermes 机密信息——包括网关机器人令牌、LLM 提供商 API 密钥以及内部中继凭证；而 `PATH`、`HOME`、区域设置等其他常规变量则会被保留。如果您的命令模板需要从环境中获取特定 API 密钥（例如通过 `curl` 执行的命令），请在提供商配置中的 `env_passthrough` 选项下列出相应的变量名称。

```yaml
tts:
  providers:
    mycloud:
      type: command
      command: 'curl -s -H "Authorization: Bearer $MYCLOUD_API_KEY" ... -o {output_path}'
      env_passthrough: [MYCLOUD_API_KEY]
```


#### 示例：豆瓣（Chinese seed-tts-2.0）

如需通过字节跳动的 [seed-tts-2.0](https://www.volcengine.com/docs/6561/1257544) 双向流 API 获取高质量的中文文本转语音服务，可安装 [`doubao-speech`](https://pypi.org/project/doubao-speech/) 这一 PyPI 包，并将其作为命令提供者进行集成：

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

认证信息来源于您的Shell环境变量（`VOLCENGINE_APP_ID` / `VOLCENGINE_ACCESS_TOKEN`）或`~/.doubao-speech/config.yaml`文件。您可以通过在命令后添加`--voice zh-female-warm`（或使用`doubao-speech list-voices`命令获取的其他语音别名）来选择所需语音。`doubao-speech`还集成了流式ASR功能——有关与Hermes的集成方式，请参阅[下方的STT部分](#example-doubao--volcengine-asr)。项目源码及完整文档地址：[github.com/Hypnus-Yuan/doubao-speech](https://github.com/Hypnus-Yuan/doubao-speech)。

#### 占位符

您的命令模板可引用这些占位符。Hermes会在渲染时替换这些占位符，并根据上下文对每个值进行Shell引号处理（原始形式/单引号/双引号），因此包含空格及其他对Shell敏感的字符的路径也能安全使用。

| 占位符          | 含义                                                |
|-----------------|------------------------------------------------------|
| `{input_path}`   | Hermes生成的临时UTF-8文本文件路径                    |
| `{text_path}`    | `{input_path}`的别名                                 |
| `{output_path}`  | 命令需要将音频写入的目标路径                        |
| `{format}`       | `mp3` / `wav` / `ogg` / `flac`                       |
| `{voice}`        | `tts.providers.<name>.voice`格式，未设置时为空         |
| `{model}`        | `tts.providers.<name>.model`格式                     |
| `{speed}`        | 经过处理的语速倍数（由特定服务提供或全局设定）       |

如需使用实际的大括号，可使用`{{`和`}}`。

#### 可选键

| 键值                | 默认值 | 含义                                                                                                    |
|--------------------|---------|------------------------------------------------------------------------------------------------------------|
| `timeout`          | `120`   | 空闲时间（秒）；当有标准输出或标准错误输出时，计时截止时间将重新计算。若进程长时间无活动，将会被终止（Unix系统使用`killpg`命令，Windows系统使用`taskkill /T`命令）。 |
| `output_format`    | `mp3`   | 可选值为`mp3`、`wav`、`ogg`或`flac`。若Hermes自动选择了文件路径，该格式会根据文件扩展名自动推断。      |
| `voice_compatible` | `false` | 当设置为`true`时，Hermes会通过ffmpeg将MP3/WAV格式的输出转换为Opus/OGG格式，以便Telegram能够正确显示语音气泡。      |
| `max_text_length`  | `5000`  | 每次执行命令时可输入的最大字符数；超过此长度的文本会被分割成多个有序的片段。                  |
| `voice` / `model`  | 空值   | 仅作为占位符传递给相关命令。                                                                           |
| `warm_command` / `release_command` | 未设置 | 当设备开启语音输出或所有设备的会话租约到期释放时，系统会运行的Shell命令——例如`curl -s localhost:5002/load?model={model}`用于预加载本地的文本转语音服务器，以及对应的`unload`命令。这类命令为尽力而为型且非阻塞式：会在后台运行，使用与`command`相同的`timeout`、`env_passthrough`以及 `{voice}`、`{model}`、`{speed}`占位符；其输出会被丢弃，仅在调试模式下记录失败信息。 |
#### 行为说明

- **内置提供者始终优先。** `tts.providers.openai` 这样的条目永远不会覆盖系统自带的 OpenAI 提供者，因此任何用户配置都无法悄无声息地替换内置提供者。
- **默认输出格式为文档。** 命令型提供者在所有平台上都会以普通音频附件的形式输出内容。若需为特定提供者启用语音气泡输出，可设置 `voice_compatible: true`。
- **命令执行失败会反馈给智能体。** 当命令返回非零退出码、输出为空或发生超时时，系统会通过命令的 stderr/stdout 返回错误信息，便于你在对话中调试相关提供者。
- **若已设置 `command:`，则默认类型为 `command`。** 明确指定 `type: command` 是良好的实践，但并非必需；只要 `command` 字段不为空，该条目即被视为命令型提供者。
- **`{input_path}` 和 `{text_path}` 可互换使用。** 根据你的命令表达习惯选择更合适的路径即可。

#### 安全性

命令型提供者会以用户的权限执行你所配置的任意 shell 命令。Hermes 会对占位符值进行转义处理，并强制执行预设的超时时间，但命令模板本身属于可信的本地输入——应像对待 PATH 中的 shell 脚本一样谨慎处理。

### Python 插件提供者

对于无法通过单个 Shell 命令实现的 TTS 引擎——例如没有 CLI 的 Python SDK、流式引擎、语音列表 API 以及需要 OAuth 刷新认证的引擎——可通过 `ctx.register_tts_provider()` 注册 Python 插件。该插件与[自定义命令提供者](#custom-command-providers)注册机制**共存**（而非替代）；请根据您的引擎类型选择合适的接口。

#### 如何选择

| 您的后端系统具备…… | 推荐使用 |
|---|---|
| 单个 CLI，可从文件/标准输入读取文本，并将音频写入文件/标准输出 | **命令提供者**（无需 Python） |
| 通过 Shell 管道串联的两个或三个 CLI | **命令提供者** |
| 仅有 Python SDK，没有 CLI | **插件** |
| 需要分块传输字节流（用于生成语音气泡的中间过程） | **插件**（需重写 `stream()` 方法） |
| 被 `hermes setup` 使用的语音列表 API | **插件**（需重写 `list_voices()` 方法） |
| 需要 OAuth 刷新机制（非静态令牌） | **插件** |

内置提供者始终是首选，且同名插件也会优先于自定义插件被使用——因此，您完全可以注册任意非内置名称的插件，而无需担心会覆盖现有的配置。

#### 最简插件示例

将以下内容放入 `~/.hermes/plugins/my-tts/` 目录中：

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

首先启用该插件（执行命令 `hermes plugins enable my-tts`），然后在 `config.yaml` 中将 `tts.provider` 指向它（设置为 `tts.provider: my-tts`），这样 `text_to_speech` 工具就会通过你所配置的插件来处理请求。

#### 可选钩子函数

你可以在自定义的提供者类中重写这些函数，以实现更深度的集成：

- `list_voices()` → 返回一个包含 `{id, display, language, gender, preview_url}` 字典的列表，这些信息会显示在 `hermes tools` 中。
- `list_models()` → 返回一个包含 `{id, display, languages, max_text_length}` 字典的列表。
- `get_setup_schema()` → 返回 `{name, badge, tag, env_vars: [{key, prompt, url}]}` 的结构，用于丰富 `hermes tools`/`hermes setup` 中的选择器界面。即使不实现此函数，插件仍可正常工作，但其选择器项的信息会非常有限。
- `stream(text, *, voice, model, format, **extra)` → 返回一个迭代器，用于逐帧生成音频字节以实现流式传输（默认行为是抛出 `NotImplementedError` 异常）。
- `voice_compatible` 属性 → 如果你的输出格式兼容 Opus 且网关应将其以语音气泡形式呈现，则将该属性设置为 `True`（默认值为 `False`，表示作为普通音频附件发送）。
- `warm()` / `release()` → 当某个终端设备开启语音输出功能，或所有终端设备的租约均到期释放时会被调用。此时若你的提供者被配置为 `tts.provider`，便可在此处预加载或卸载本地模型服务器。这两个函数的默认行为均为无操作；异常情况仅会在调试模式下记录，而不会导致语音功能的切换失败。

完整的抽象基类定义及文档字符串请参见 `agent/tts_provider.py` 文件。

## 语音消息转录（STT）

通过 Telegram、Discord、WhatsApp、Slack 或 Signal 发送的语音消息会自动被转录为文本，并插入到对话中。智能体将此转录内容视为普通文本来处理。

| 提供商 | 转录质量 | 成本 | API 密钥 |
|--------|----------|------|---------| 
| **Local Whisper**（默认） | 较好 | 免费 | 无需提供 |
| **Groq Whisper API** | 较好–优秀 | 免费套餐 | `GROQ_API_KEY` |
| **OpenAI Whisper API** | 较好–优秀 | 需付费 | `VOICE_TOOLS_OPENAI_KEY` 或 `OPENAI_API_KEY` |

:::info 无需额外配置
只要安装了 `faster-whisper`，即可直接使用本地转录功能。若该工具不可用，Hermes 还可以调用来自常见安装路径（如 `/opt/homebrew/bin`）的本地 `whisper` CLI，或通过 `HERMES_LOCAL_STT_COMMAND` 指定自定义命令。
:::

### 配置选项

```yaml
# In ~/.hermes/config.yaml
stt:
  provider: "local"           # "local" | "groq" | "openai" | "mistral" | "xai" | "elevenlabs" | "deepinfra"
  language: "en"              # Global language hint applied to every provider unless a per-provider language overrides it; set "" to restore auto-detect
  local:
    model: "base"             # tiny, base, small, medium, large-v3
    language: ""              # optional ISO-639-1 hint; blank = use HERMES_LOCAL_STT_LANGUAGE if set, else auto-detect
  groq:
    language: ""              # optional ISO-639-1 hint; blank = use HERMES_LOCAL_STT_LANGUAGE if set, else auto-detect
  openai:
    model: "whisper-1"        # whisper-1, gpt-4o-mini-transcribe, gpt-4o-transcribe, gpt-transcribe
  mistral:
    model: "voxtral-mini-latest"  # voxtral-mini-latest, voxtral-mini-2602
  xai:
    model: "grok-stt"         # xAI Grok STT
    language: ""              # optional ISO-639-1 hint; blank = use HERMES_LOCAL_STT_LANGUAGE if set, else "en"
```

### 提供商详情

**本地模式（faster-whisper）** — 通过 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 在本地运行 Whisper 模型。默认使用 CPU，如有 GPU 则会优先使用。各模型参数如下：

| 模型 | 大小 | 速度 | 质量 |
|------|------|------|-------|
| `tiny` | 约 75 MB | 最快 | 基础水平 |
| `base` | 约 150 MB | 快 | 较好（默认） |
| `small` | 约 500 MB | 中等 | 更优 |
| `medium` | 约 1.5 GB | 较慢 | 优秀 |
| `large-v3` | 约 3 GB | 最慢 | 最佳 |

**Groq API** — 需要提供 `GROQ_API_KEY`。若希望使用免费的托管语音转文字服务，此选项可作为良好的云端备选方案。通过设置 `stt.groq.language`（或全局环境变量 `HERMES_LOCAL_STT_LANGUAGE`），可绕过 Whisper 的自动语言检测功能，并降低已知语言音频的转录延迟。

**OpenAI API** — 首先会尝试使用 `VOICE_TOOLS_OPENAI_KEY`，若无效则回退至 `OPENAI_API_KEY`。支持 `whisper-1`、`gpt-4o-mini-transcribe`、`gpt-4o-transcribe` 以及 `gpt-transcribe` 这些模型。

**Mistral API（Voxtral Transcribe）** — 需要提供 `MISTRAL_API_KEY`。该功能基于 Mistral 的 [Voxtral Transcribe](https://docs.mistral.ai/capabilities/audio/speech_to_text/) 模型，支持 13 种语言、说话人分离以及单词级时间戳功能。可通过以下命令进行安装：`cd ~/.hermes/hermes-agent && uv pip install -e ".[mistral]"`。

**xAI Grok STT** — 需要提供 `XAI_API_KEY`。该服务以 multipart/form-data 格式向 `https://api.x.ai/v1/stt` 发送请求。如果您已经在使用 xAI 进行聊天或文本转语音功能，并希望用一个 API 密钥统一管理所有服务，那么这是一个不错的选择。其自动检测顺序位于 Groq 之后——如需强制使用该服务，可显式设置 `stt.provider: xai`。

**自定义本地 CLI 作为备用方案** —— 如果希望 Hermes 直接调用本地的文本转录命令，可设置 `HERMES_LOCAL_STT_COMMAND`。该命令模板支持 `{input_path}`、`{output_dir}`、`{language}` 和 `{model}` 这些占位符。Hermes 会将生成的模板分解为参数列表并直接执行，无需使用 Shell，因此 `|`、`>`、`&&` 和 `;` 等操作符会被视为普通参数传递。您的命令必须将转录结果以 `.txt` 格式写入 `{output_dir}` 指定的某个目录中。

#### 示例：Doubao / Volcengine ASR

如果您使用 [`doubao-speech`](https://pypi.org/project/doubao-speech/) 来实现 Doubao TTS（参见[上文](#example-doubao-chinese-seed-tts-20)），则同一个包可通过本地命令式的文本转录接口来完成语音转文字功能：

```bash
pip install doubao-speech
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_TOKEN="your-access-token"
export HERMES_LOCAL_STT_COMMAND='doubao-speech transcribe {input_path} --out {output_dir}/transcript.txt'
```

如果某个受信任的本地模板确实需要使用管道、重定向或其他 Shell 功能，应显式调用 Shell 程序。请将动态生成的路径保留在 Shell 程序之外，并以位置参数的形式传递给它。

```bash
export HERMES_LOCAL_STT_COMMAND='sh -c '\''whisper "$1" --output_format txt --output_dir "$2" | tee "$2/whisper.log"'\'' _ {input_path} {output_dir}'
```

在 Windows 系统上，建议使用显式的 `cmd /c` 或 PowerShell 包装脚本。通过显式包装脚本，shell 解释功能将成为配置后的 argv 的可选组成部分，而非每个本地语音转文字模板的固有特性。

```yaml
stt:
  provider: local_command
```

Hermes会将接收到的语音消息写入`{input_path}`，执行相应命令，然后读取在`{output_dir}`下生成的`.txt`文件。语言类型由Volcengine大模型端点自动识别。

### 回退机制

系统会严格遵循通过`config.yaml`（例如通过`hermes tools`）明确指定的`stt.provider`设置——如果该指定的服务提供商无法运行，转录将会抛出明确的错误信息（“已配置使用<provider>（通过hermes tools设置），但出现<failure>错误。请运行‘hermes tools’进行更改。”），而不会默默切换到其他引擎。需注意，配置文件中写明的`stt.provider: local`也视为明确的选择。

当**从未指定过任何服务提供商**时，Hermes会自动从可用选项中选择：
- 若本地版faster-whisper不可用，则先尝试使用本地的`whisper` CLI或`HERMES_LOCAL_STT_COMMAND`，然后再尝试云服务提供商；
- 若未设置Groq密钥，则跳过该选项，尝试下一个可用提供商；
- 若未设置OpenAI密钥，则跳过该选项，尝试下一个可用提供商；
- 若未设置Mistral密钥/SDK，则在自动检测阶段跳过该选项，直接尝试下一个可用提供商；
- 若所有选项均不可用，则语音消息将原样传递给用户，并附上相应提示。

### STT自定义命令提供商

如果您需要的文本转语音引擎未被原生支持（如百度语音识别、NVIDIA Parakeet、基于whisper.cpp构建的版本、开源的SenseVoice CLI，或是任何能提供命令行接口的工具），无需编写任何Python代码，即可将其作为**命令型提供者**进行集成。Hermes会执行您指定的命令行指令来处理音频文件，并将转换后的文本结果返回。

您可以在`stt.providers.<名称>`下定义一个或多个提供者，然后通过`stt.provider: <名称>`来切换使用不同的提供者——其结构与TTS[命令型提供者注册表](#custom-command-providers)相同，只是适配了“输入=音频 → 输出=文本”的处理流程。

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

该机制通过内置的 `local_command` 路径，对传统的 `HERMES_LOCAL_STT_COMMAND` 逃生通道进行了补充。与基于 shell 的命令提供程序注册表不同，传统模板会被拆分为 argv 参数并直接执行，无需经过 shell 的隐式解析。当您需要**多个**基于 shell 的语音转文字引擎、希望通过 `stt.provider` 自定义名称，或需要对每个提供程序单独设置 `language`/`model`/`timeout` 参数时，可使用 `stt.providers.<name>`。

#### 语音转文字占位符

您的命令模板可以引用这些占位符。Hermes 会在渲染时替换这些值，并根据上下文为每个值添加相应的引号（空引号/单引号/双引号），因此包含空格的路径也能正常使用。

| 占位符             | 含义                                                              |
|--------------------|-------------------------------------------------------------------|
| `{input_path}`      | 输入音频文件的绝对路径（原始位置，仅读）                             |
| `{output_path}`     | 命令应将转写结果写入的绝对路径                                     |
| `{output_dir}`     | `{output_path}` 的父目录（适用于类似“耳语”模式的工具）                 |
| `{format}`         | 预设的输出格式：`txt`/`json`/`srt`/`vtt`                             |
| `{language}`       | 预设的语言代码（默认为 `en`）                                      |
| `{model}`          | `stt.providers.<name>.model` 的形式，若未设置则为空字符串             |

如需在命令中嵌入 JSON 片段，可使用 `{{` 和 `}}` 来表示字面意义上的大括号。

#### 转录文本的读取方式

当您的命令成功执行后：

1. 如果 `{output_path}` 存在且非空 → Hermes 会以 UTF-8 文本格式读取该文件。
2. 否则，如果命令将输出写入标准输出 → Hermes 会使用标准输出内容。
3. 其他情况 → 将出现错误信息：“命令对应的 STT 提供程序未生成任何输出文件，也未产生标准输出”。

这一设计使得无论是用于写入文件的 CLI 工具（如 `whisper-cli`、`parakeet-asr`），还是将转录文本直接输出到标准输出的 curl 风格单行命令（如 `curl … | jq -r .text`），都能被 Hermes 正常使用。

对于 `format: json` / `srt` / `vtt` 这类格式，Hermes 会以 `transcript` 字段的形式返回原始文件内容。从 JSON 中提取 `.text` 内容超出了运行器的处理范围——您需要选择将格式设置为 `txt`，或是在后续流程中对 JSON 进行处理。

#### STT 命令提供程序的可选键值

| 键值             | 默认值   | 含义                                                                                              |
|-----------------|---------|------------------------------------------------------------------------------------------------------|
| `timeout`       | `300`   | 秒数；达到该时间后进程树将被终止（Unix系统使用`start_new_session`，Windows系统使用`taskkill /T`）。     |
| `format`        | `txt`   | 可选值为`txt`/`json`/`srt`/`vtt`，用于指定`{output_path}`的文件扩展名。                       |
| `language`      | `en`    | 该参数会传递给`{language}`。若未指定，则优先使用`stt.language`的值，否则使用`en`。             |
| `model`         | 空值     | 该参数会传递给`{model}`。调用`transcribe_audio()`函数时传入的`model=`参数可覆盖此设置。                |

#### STT命令提供器的行为说明

- **内置提供器始终优先生效**。即使声明了`stt.providers.openai: type: command`，也不会替代真正的OpenAI Whisper处理程序。在命令提供器解析机制启动之前，系统会直接使用内置提供器。
- **进程树完整终止**。当达到`timeout`设定的时间限制后，不仅shell封装层会被终止，整个进程树都会被强制关闭。因此，那些会创建模型加载子进程的长时间运行的ASR流程也能被可靠地终止。
- **自动处理引号**：位于单引号`'…'`内的占位符会进行单引号安全的转义处理；位于双引号`"…"`内的占位符则会进行`$$`、`` ` ``、`"`等转义处理；而位于引号之外的占位符则会被应用`shlex.quote`函数进行处理。无需预先对占位符值添加引号。

#### STT命令提供器的安全性说明

该 Shell 命令在与 Hermes 相同的用户权限下运行，并拥有对整个文件系统的访问权限——其信任模型与 `tts.providers.<name>: type: command` 以及 `HERMES_LOCAL_STT_COMMAND` 完全一致。请仅从您信任的来源声明命令提供程序。

### Python 插件提供程序（语音转文字）

对于那些非内置且无法通过 Shell 命令实现的语音转文字引擎（需要 Python SDK、基于 OAuth 的刷新式认证、分块流式处理等功能），可通过 `ctx.register_transcription_provider()` 注册 Python 插件。此类插件与 8 个内置提供程序（`local`、`local_command`、`groq`、`openai`、`mistral`、`xai`、`elevenlabs`、`deepinfra`）以及 `stt.providers.<name>: type: command` 注册表**共存**——内置提供程序会保留其原有的实现方式，在名称冲突时始终优先；而相同名称的命令提供程序则会在插件中占据优势（因为配置更偏向本地化，无需安装插件）。

#### 如何选择合适的方式（语音转文字）

| 后端支持的功能…                                                 | 使用方式                                                              |
|--------------------------------------------------------------|------------------------------------------------------------------|
| 一个可接收音频文件并输出文本的单一 Shell 命令                 | `stt.providers.<名称>: type: command`（无需 Python）                        |
| 仅需要传统的单命令解决方案                                 | `HERMES_LOCAL_STT_COMMAND` 环境变量（通过参数列表传递；无隐式 Shell）   |
| 无 CLI 的 Python SDK                                             | `register_transcription_provider()` 插件                              |
| OAuth 刷新认证、分块流式处理、语音列表元数据                   | `register_transcription_provider()` 插件                              |
| 内置功能已可满足需求（如 `local`、`groq`、`openai` 等）     | 设置 `stt.provider: <名称>`——内置功能可直接使用                     |

#### 解决方案优先级顺序

1. **`stt.provider` 是一个内置名称** → 表示内置调度方式，**始终具有优先权**。  
2. **当 `stt.provider` 与设置了 `command:` 参数的 `stt.providers.<name>` 匹配时** → 代表命令型提供程序运行方式（详见[STT自定义命令提供程序](#stt-custom-command-providers)），其优先级高于同名称的插件。  
3. **当 `stt.provider` 与插件注册的 `TranscriptionProvider` 对象匹配时** → 表示插件调度方式：  
   - 若插件的 `is_available()` 方法返回 `False`（如缺少凭证或SDK），则会抛出明确标识该插件的不可用错误信息——而非通用的“没有可用的STT提供程序”提示。  
   - 否则，将使用来自公共 `model=` 参数的 `model` 值（若未指定则回退至 `stt.<provider>.model`）以及来自 `stt.<provider>.language` 的语言参数，来调用插件的 `transcribe()` 方法。  
4. **若没有任何匹配项** → 会显示“没有可用的STT提供程序”错误。

#### 各提供程序的配置命名空间

插件会从 `config.yaml` 中的 `stt.<provider>` 部分读取针对特定提供程序的配置，其方式与内置提供程序读取 `stt.openai.model`/`stt.mistral.model` 的方式类似。

```yaml
stt:
  provider: my-stt
  my-stt:
    model: whisper-large-v3
    language: ja          # forwarded as language= to transcribe()
    # any other plugin-specific keys go here; read them via your
    # own config.yaml access in __init__/is_available/transcribe
```

调度器会传递该部分中的 `model` 和 `language` 参数；其余所有信息，插件均可自行读取。

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

首先启用该插件（执行命令 `hermes plugins enable my-stt`），然后在 `config.yaml` 中设置 `stt.provider: my-stt`，这样语音消息的转录功能就会通过您所配置的插件来处理。

#### 可选钩子函数

您可以在自定义的提供者类中重写这些函数，以实现更深度的集成：

- `list_models()` → 返回包含 `{id, display, languages, max_audio_seconds}` 字典的列表。
- `default_model()` → 当用户未指定模型时返回的字符串。
- `get_setup_schema()` → 返回 `{name, badge, tag, env_vars: [{key, prompt, url}]}` 的结构，用于填充 `hermes tools` / `hermes setup` 中的选项行（目前 STT 类别的选择器尚未正式推出——提供这些元数据是为了确保插件的向后兼容性）。

如需查看包含文档字符串的完整 ABC 接口定义，请参阅 `agent/transcription_provider.py` 文件。
